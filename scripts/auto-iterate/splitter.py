from __future__ import annotations

import json
import re
import hashlib
from pathlib import Path
from collections import defaultdict


def normalize_module_name(module_path: str) -> str:
    """从 '00 公共规则/02 URL通用校验' 取最后一段，去掉前缀编号。

    例: '98 GEO SaaS/00 公共规则/02 URL通用校验' -> 'URL通用校验'

    NOTE: 此函数保留用于向后兼容和测试。新代码应使用 discover_modules()。
    """
    last = module_path.rstrip('/').split('/')[-1].strip()
    # 去掉前导编号 (如 "02 "、"01 ")
    return re.sub(r'^\d+\s+', '', last)


def split_reference(ref_path: str) -> dict[str, list]:
    """按 module_path 末尾模块名分组参考用例。

    NOTE: 此函数保留用于向后兼容。新代码应使用 discover_modules()。

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

    NOTE: 此函数保留用于向后兼容。新代码应使用 discover_modules()。

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

    NOTE: 此函数保留用于向后兼容。新代码应使用 discover_modules()。

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


# ---------------------------------------------------------------------------
# AI-based module discovery
# ---------------------------------------------------------------------------

def _extract_prd_outline(prd_path: str) -> str:
    """提取 PRD 的标题大纲 (##/###/#### 层级)，保留缩进层次。"""
    text = Path(prd_path).read_text(encoding='utf-8')
    lines = []
    for line in text.split('\n'):
        m = re.match(r'^(#{2,4})\s+(.+?)\s*$', line)
        if m:
            depth = len(m.group(1)) - 2  # ## -> 0, ### -> 1, #### -> 2
            lines.append('  ' * depth + m.group(2))
    return '\n'.join(lines)


def _extract_ref_paths(ref_path: str) -> list[str]:
    """提取参考用例 JSON 中所有去重的 module_path。"""
    data = json.loads(Path(ref_path).read_text(encoding='utf-8'))
    cases = data["data"]["cases"]
    paths = sorted(set(c["module_path"] for c in cases))
    return paths


def _compute_input_hash(prd_path: str, ref_path: str) -> str:
    """基于 PRD 和 Ref 文件内容计算哈希，用于缓存失效判断。"""
    h = hashlib.sha256()
    h.update(Path(prd_path).read_bytes())
    h.update(Path(ref_path).read_bytes())
    return h.hexdigest()[:16]


def _load_module_map_cache(cache_path: str, expected_hash: str) -> list[dict] | None:
    """加载缓存的 module-map.json，校验 input_hash。"""
    p = Path(cache_path)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        if data.get("input_hash") != expected_hash:
            return None
        return data["modules"]
    except (json.JSONDecodeError, KeyError):
        return None


def _build_matched_from_module_map(
    module_map: list[dict],
    prd_path: str,
    ref_path: str,
) -> list[dict]:
    """将 AI 生成的 module_map 转换为 orchestrator 需要的 matched 格式。

    Returns: [{"name": str, "prd_content": str|None, "ref_cases": list|None}]
    """
    # 构建 PRD section -> content 的索引
    prd_sections = _index_prd_sections(prd_path)

    # 构建 ref_path -> cases 的索引
    ref_index = _index_ref_cases(ref_path)

    matched = []
    for mod in module_map:
        # 拼接 PRD 内容
        prd_content_parts = []
        for section_key in mod.get("prd_sections", []):
            content = prd_sections.get(section_key)
            if content:
                prd_content_parts.append(content)
        prd_content = '\n'.join(prd_content_parts) if prd_content_parts else None

        # 收集参考用例
        ref_cases = []
        for rp in mod.get("ref_paths", []):
            ref_cases.extend(ref_index.get(rp, []))

        matched.append({
            "name": mod["name"],
            "prd_content": prd_content,
            "ref_cases": ref_cases if ref_cases else None,
        })

    return matched


def _index_prd_sections(prd_path: str) -> dict[str, str]:
    """构建 "H2 > H3 > H4" 路径 -> 对应内容 的索引。

    同时也索引每个标题自身 (不含子标题路径)，便于灵活匹配。
    """
    text = Path(prd_path).read_text(encoding='utf-8')
    lines = text.split('\n')

    index = {}
    # 追踪当前各级标题
    headers = {2: None, 3: None, 4: None}
    current_path = None
    current_content_lines = []

    def _flush():
        if current_path and current_content_lines:
            content = '\n'.join(current_content_lines)
            index[current_path] = content
            # 也用最后一级标题名单独索引
            last_part = current_path.split(' > ')[-1]
            if last_part not in index:
                index[last_part] = content

    for line in lines:
        m = re.match(r'^(#{2,4})\s+(.+?)\s*$', line)
        if m:
            _flush()
            level = len(m.group(1))
            title = m.group(2).strip()
            headers[level] = title
            # 清除更深层级
            for deeper in range(level + 1, 5):
                headers[deeper] = None
            # 构建路径
            parts = [headers[lv] for lv in range(2, level + 1) if headers[lv]]
            current_path = ' > '.join(parts)
            current_content_lines = []
        else:
            current_content_lines.append(line)

    _flush()
    return index


def _index_ref_cases(ref_path: str) -> dict[str, list]:
    """构建 module_path -> [case, ...] 的索引。"""
    data = json.loads(Path(ref_path).read_text(encoding='utf-8'))
    cases = data["data"]["cases"]
    index = defaultdict(list)
    for c in cases:
        index[c["module_path"]].append(c)
    return dict(index)


def discover_modules(
    prd_path: str,
    ref_path: str,
    output_dir: str,
    prompt_dir: str,
    model: str = "sonnet",
    timeout: int = 300,
    force: bool = False,
) -> list[dict]:
    """AI 驱动的模块发现: 分析 PRD 大纲 + 参考用例路径，输出对齐后的模块列表。

    1. 提取 PRD 标题大纲和 ref module_paths
    2. 检查缓存 (module-map.json)，输入未变则复用
    3. 调用 Claude 生成 module_map
    4. 转换为 orchestrator 需要的 matched 格式

    Returns: [{"name": str, "prd_content": str|None, "ref_cases": list|None}]
    """
    from jinja2 import Template
    from claude_runner import claude_call

    cache_path = f"{output_dir}/module-map.json"
    input_hash = _compute_input_hash(prd_path, ref_path)

    # 检查缓存
    if not force:
        cached = _load_module_map_cache(cache_path, input_hash)
        if cached is not None:
            print(f"[splitter] Module map loaded from cache ({len(cached)} modules)", flush=True)
            return _build_matched_from_module_map(cached, prd_path, ref_path)

    # 准备 prompt 输入
    prd_outline = _extract_prd_outline(prd_path)
    ref_paths = _extract_ref_paths(ref_path)

    template_text = Path(f"{prompt_dir}/discover-modules.md").read_text(encoding='utf-8')
    tmpl = Template(template_text)
    prompt = tmpl.render(
        prd_outline=prd_outline,
        ref_paths='\n'.join(ref_paths),
    )

    # 调用 Claude
    raw_output = f"{output_dir}/module-map-raw.md"
    result = claude_call(prompt, raw_output, parse_json=True, model=model, timeout=timeout)
    if result is None:
        raise RuntimeError("Failed to parse module-map JSON from Claude output")

    module_map = result.get("modules", [])
    if not module_map:
        raise RuntimeError("Claude returned empty module list")

    # 写入缓存 (带 input_hash)
    cache_data = {"input_hash": input_hash, "modules": module_map}
    Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
    Path(cache_path).write_text(
        json.dumps(cache_data, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    print(f"[splitter] Module map generated: {len(module_map)} modules", flush=True)

    return _build_matched_from_module_map(module_map, prd_path, ref_path)
