from pathlib import Path
import json
from splitter import split_reference, split_prd, normalize_module_name, match_modules


def test_normalize_module_name_strips_numbering():
    assert normalize_module_name("02 URL通用校验") == "URL通用校验"
    assert normalize_module_name("00 公共规则/02 URL通用校验") == "URL通用校验"


def test_split_reference_groups_by_module(tmp_path):
    ref = {
        "data": {
            "cases": [
                {"case_id": "1", "module_path": "A/B/URL通用校验", "case_name": "x", "steps": []},
                {"case_id": "2", "module_path": "A/B/URL通用校验", "case_name": "y", "steps": []},
                {"case_id": "3", "module_path": "A/C/系统异常", "case_name": "z", "steps": []},
            ]
        }
    }
    ref_file = tmp_path / "ref.json"
    ref_file.write_text(json.dumps(ref), encoding='utf-8')

    groups = split_reference(str(ref_file))
    assert "URL通用校验" in groups
    assert len(groups["URL通用校验"]) == 2
    assert "系统异常" in groups
    assert len(groups["系统异常"]) == 1


def test_split_prd_by_headings(tmp_path):
    content = """# 标题
## 模块 A
A 内容
### 子节
子节内容
## 模块 B
B 内容
"""
    prd = tmp_path / "prd.md"
    prd.write_text(content, encoding='utf-8')

    modules = split_prd(str(prd))
    names = [m["name"] for m in modules]
    assert "模块 A" in names
    assert "模块 B" in names
    # 子节应在模块 A 片段内
    mod_a = next(m for m in modules if m["name"] == "模块 A")
    assert "子节内容" in mod_a["content"]


def test_match_modules_bidirectional_substring():
    prd = [{"name": "URL通用校验", "content": "prd text"}]
    ref = {"URL通用校验": [{"case_id": "1"}]}
    result = match_modules(prd, ref)
    assert len(result) == 1
    assert result[0]["prd_content"] == "prd text"
    assert result[0]["ref_cases"] == [{"case_id": "1"}]


def test_match_modules_unmatched_both_sides():
    prd = [{"name": "仅PRD模块", "content": "p"}]
    ref = {"仅参考模块": [{"case_id": "1"}]}
    result = match_modules(prd, ref)
    names = [r["name"] for r in result]
    assert "仅PRD模块" in names
    assert "仅参考模块" in names
