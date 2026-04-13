import json
import re
from pathlib import Path
from collections import defaultdict


def normalize_module_name(module_path: str) -> str:
    """从 '00 公共规则/02 URL通用校验' 取最后一段，去掉前缀编号。

    例: '98 GEO SaaS/00 公共规则/02 URL通用校验' -> 'URL通用校验'
    """
    last = module_path.rstrip('/').split('/')[-1].strip()
    # 去掉前导编号 (如 "02 "、"01 ")
    return re.sub(r'^\d+\s+', '', last)


def split_reference(ref_path: str) -> dict[str, list]:
    """按 module_path 末尾模块名分组参考用例。

    Returns: {module_name: [case, ...]}
    """
    data = json.loads(Path(ref_path).read_text(encoding='utf-8'))
    cases = data["data"]["cases"]
    groups = defaultdict(list)
    for c in cases:
        name = normalize_module_name(c["module_path"])
        groups[name].append(c)
    return dict(groups)


def split_prd(prd_path: str) -> list[dict]:
    """按 Markdown `##` 二级标题拆分 PRD。

    Returns: [{"name": str, "content": str}, ...]
    """
    text = Path(prd_path).read_text(encoding='utf-8')
    lines = text.split('\n')

    modules = []
    current = None
    for line in lines:
        m = re.match(r'^##\s+(.+?)\s*$', line)
        if m and not line.startswith('###'):
            if current is not None:
                modules.append(current)
            current = {"name": m.group(1).strip(), "content": ""}
        elif current is not None:
            current["content"] += line + "\n"
    if current is not None:
        modules.append(current)
    return modules


def match_modules(prd_modules: list[dict], ref_groups: dict[str, list]) -> list[dict]:
    """将 PRD 模块与参考用例模块对齐。

    匹配策略: PRD 模块名在 ref 模块名中子串匹配 (双向)。
    未匹配的保留为单侧条目 (ref_cases 或 prd_content 为空)。

    Returns: [{"name": str, "prd_content": str|None, "ref_cases": list|None}]
    """
    matched = []
    used_ref = set()
    for pm in prd_modules:
        pname = pm["name"]
        match_ref = None
        for rname in ref_groups:
            if rname in pname or pname in rname:
                match_ref = rname
                break
        if match_ref:
            matched.append({
                "name": pname,
                "prd_content": pm["content"],
                "ref_cases": ref_groups[match_ref],
            })
            used_ref.add(match_ref)
        else:
            matched.append({
                "name": pname,
                "prd_content": pm["content"],
                "ref_cases": None,
            })
    # 未匹配的参考模块单独加入
    for rname, cases in ref_groups.items():
        if rname not in used_ref:
            matched.append({
                "name": rname,
                "prd_content": None,
                "ref_cases": cases,
            })
    return matched
