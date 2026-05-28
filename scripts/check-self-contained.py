#!/usr/bin/env python3
"""
Self-containment validator for .supertester/test-cases/functional-cases.yaml.

Scans every test case's user-facing fields for internal codes
(C-xxx, E-xxx, IR-xxx, CMS-xxx, CL-xxx, I-xxx, CTX-x, F-xxx, R-xxx,
UC-xxx, S-xxx, A-xxx, PR-xxx, P-xxx, SC-xxx) and flags occurrences where
the code itself carries the semantic instead of acting as a parenthetical
traceability annotation after literal content.

Rule reference:
- skills/test-case-generation/SKILL.md '内部代号自包含自检（强制）'
- agents/test-reviewer.md Section 3.A 'Internal-code references (self-containment)'

Exit codes:
  0  No violations
  1  Violations present (also writes report)
  2  File missing, YAML parse error, or PyYAML not installed
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    sys.stderr.write(
        "[check-self-contained] PyYAML missing. Install with: "
        "pip install pyyaml\n"
    )
    sys.exit(2)


# Internal-code regex. re.ASCII ensures \b works at CJK/ASCII boundaries.
CODE_PATTERN = re.compile(
    r"\b(?:C|E|IR|CMS|CL|I|CTX|F|R|UC|S|A|PR|P|SC)-\w+\b",
    re.ASCII,
)

# Single-pair parens matcher (no nested parens supported on purpose —
# we iterate until stable).
PARENS_PATTERN = re.compile(r"[(（]([^()（）]*)[)）]")

# Characters that, when immediately to the left of a code (optionally
# followed by whitespace), mark the code as a parenthetical traceability
# annotation after literal content (e.g. 「文案」(C-001)).
ANNOTATION_LEFT_CHARS = "」』\\)）\\]】\"\\'"
ANNOTATION_LEFT_RE = re.compile(
    rf"[{ANNOTATION_LEFT_CHARS}]\s*$"
)

# Fields that are pure traceability — codes are expected here and not
# scanned.
TRACEABILITY_ONLY_KEYS = {"feature", "sub_refs", "sources", "source"}

# User-facing fields on case root that must be self-contained.
ROOT_SCANNED_KEYS = {
    "title",
    "preconditions",
    "steps",
    "expected",
    "key_assets",
}

# Matrix row fields that must be self-contained.
MATRIX_ROW_SCANNED_KEYS = {"action", "expected"}

# Light qualifier words that, together with codes and separators, render
# a paren block a pure traceability annotation that can be stripped.
LIGHT_QUALIFIERS = (
    "推测",
    "待PRD澄清",
    "待澄清",
    "BLOCKED",
    "blocked",
    "待定",
    "待补充",
    "TBD",
    "todo",
    "TODO",
    "对应",
    "依据",
    "参见",
    "见",
)

SEPARATOR_RE = re.compile(r"[\s/,，、;；:：]+")


def is_traceability_only_parens(content: str) -> bool:
    """Return True if parens content is just codes + separators + light qualifiers."""
    if not CODE_PATTERN.search(content):
        return False
    stripped = CODE_PATTERN.sub("", content)
    stripped = SEPARATOR_RE.sub("", stripped)
    for word in LIGHT_QUALIFIERS:
        stripped = stripped.replace(word, "")
    return stripped == ""


def strip_traceability_parens(text: str) -> str:
    """Iteratively remove parens that are pure traceability annotations."""

    def replace(match: re.Match) -> str:
        if is_traceability_only_parens(match.group(1)):
            return ""
        return match.group(0)

    prev: str | None = None
    while prev != text:
        prev = text
        text = PARENS_PATTERN.sub(replace, text)
    return text


OPEN_PARENS = "(（"
CLOSE_PARENS = ")）"


def enclosing_parens(text: str, code_start: int, code_end: int) -> tuple[int, int] | None:
    """Return (open_idx, close_idx) of the nearest balanced parens enclosing a code, or None."""
    depth = 0
    open_idx = -1
    for i in range(code_start - 1, -1, -1):
        ch = text[i]
        if ch in CLOSE_PARENS:
            depth += 1
        elif ch in OPEN_PARENS:
            if depth == 0:
                open_idx = i
                break
            depth -= 1
    if open_idx < 0:
        return None
    depth = 0
    close_idx = -1
    for i in range(code_end, len(text)):
        ch = text[i]
        if ch in OPEN_PARENS:
            depth += 1
        elif ch in CLOSE_PARENS:
            if depth == 0:
                close_idx = i
                break
            depth -= 1
    if close_idx < 0:
        return None
    return (open_idx, close_idx)


def code_is_paren_tail_annotation(
    text: str, code_start: int, code_end: int
) -> bool:
    """OK pattern: (实际内容…，CODE[/CODE…]) — code(s) at the tail of a paren block."""
    span = enclosing_parens(text, code_start, code_end)
    if span is None:
        return False
    open_idx, close_idx = span
    content_after = text[code_end:close_idx]
    # Allow trailing codes + separators + light qualifiers only.
    after_remainder = CODE_PATTERN.sub("", content_after)
    after_remainder = SEPARATOR_RE.sub("", after_remainder)
    for word in LIGHT_QUALIFIERS:
        after_remainder = after_remainder.replace(word, "")
    if after_remainder != "":
        return False
    content_before = text[open_idx + 1 : code_start]
    chinese_before = re.findall(r"[一-鿿]", content_before)
    return len(chinese_before) >= 2


def find_violations_in_text(text: str, field_path: str) -> list[dict]:
    """Find every internal code that is NOT a parenthetical traceability annotation."""
    if not text:
        return []
    violations: list[dict] = []
    cleaned = strip_traceability_parens(text)
    for m in CODE_PATTERN.finditer(cleaned):
        start, end = m.start(), m.end()
        left_window = cleaned[max(0, start - 6) : start]
        if ANNOTATION_LEFT_RE.search(left_window):
            # Code follows a closing quote/bracket — annotation suffix after literal.
            continue
        if code_is_paren_tail_annotation(cleaned, start, end):
            # Code sits at the tail of a parens block whose body is literal content.
            continue
        code = m.group(0)
        snippet_start = max(0, start - 16)
        snippet_end = min(len(cleaned), end + 16)
        snippet = cleaned[snippet_start:snippet_end]
        violations.append(
            {
                "field": field_path,
                "code": code,
                "snippet": snippet,
                "rule": "code-carries-meaning",
            }
        )
    return violations


def emit_strings(path: str, value, skip_keys: set[str]):
    """Recursively yield (field_path, string_value) for scanned fields."""
    if value is None:
        return
    if isinstance(value, str):
        yield (path, value)
        return
    if isinstance(value, list):
        for i, item in enumerate(value):
            sub_path = f"{path}[{i}]"
            if isinstance(item, str):
                yield (sub_path, item)
            elif isinstance(item, dict):
                for k, v in item.items():
                    if k in skip_keys:
                        continue
                    yield from emit_strings(f"{sub_path}.{k}", v, skip_keys)
            elif isinstance(item, list):
                yield from emit_strings(sub_path, item, skip_keys)
        return
    if isinstance(value, dict):
        for k, v in value.items():
            if k in skip_keys:
                continue
            yield from emit_strings(f"{path}.{k}", v, skip_keys)
        return


def collect_case_fields(case: dict):
    """Yield (field_path, text) for every scanned text in a case."""
    for key in ROOT_SCANNED_KEYS:
        if key in case:
            yield from emit_strings(key, case[key], TRACEABILITY_ONLY_KEYS)

    if case.get("type") == "matrix":
        for gi, group in enumerate(case.get("groups", []) or []):
            if not isinstance(group, dict):
                continue
            name = group.get("name")
            if isinstance(name, str):
                yield (f"groups[{gi}].name", name)
            for ri, row in enumerate(group.get("rows", []) or []):
                if not isinstance(row, dict):
                    continue
                for rk, rv in row.items():
                    if rk in TRACEABILITY_ONLY_KEYS:
                        continue
                    if rk not in MATRIX_ROW_SCANNED_KEYS:
                        continue
                    yield from emit_strings(
                        f"groups[{gi}].rows[{ri}].{rk}",
                        rv,
                        TRACEABILITY_ONLY_KEYS,
                    )

    if case.get("type") == "scenario_chain":
        for bi, branch in enumerate(case.get("branches", []) or []):
            if not isinstance(branch, dict):
                continue
            for bk, bv in branch.items():
                if bk in TRACEABILITY_ONLY_KEYS:
                    continue
                yield from emit_strings(
                    f"branches[{bi}].{bk}", bv, TRACEABILITY_ONLY_KEYS
                )


def title_body_issues(case: dict) -> list[dict]:
    """Flag titles where the body before the trailing code-paren cannot stand alone."""
    title = case.get("title")
    if not isinstance(title, str) or not title.strip():
        return [
            {
                "field": "title",
                "code": "",
                "snippet": str(title) if title else "",
                "rule": "title-empty",
            }
        ]
    # Strip trailing code-only parens to get body.
    m = re.search(r"[（(][^()（）]*[)）]\s*$", title)
    if not m:
        return []
    trailing_content = title[m.start() + 1 : m.end() - 1]
    body = title[: m.start()].strip()
    # If trailing is pure traceability (codes + separators + light qualifiers),
    # then the title body must be substantive on its own.
    if not is_traceability_only_parens(trailing_content):
        # Trailing parens contains substantive non-code text — fine for now;
        # field-level scan will catch any meaning-carrying codes inside.
        return []
    cn_chars = re.findall(r"[一-鿿]", body)
    if len(cn_chars) < 6:
        return [
            {
                "field": "title",
                "code": "",
                "snippet": title,
                "rule": "title-body-too-short",
            }
        ]
    return []


RULE_MESSAGES = {
    "code-carries-meaning": (
        "代号 {code} 出现在 {field}，但前面没有字面内容承载。"
        "代号只能作为括号溯源注释附在实际内容之后，例如 「实际内容」({code})；"
        "不能用代号替代字段中的名称、文案、状态或假设描述。"
    ),
    "title-empty": "title 为空——必须用一句话描述本条用例要验证的业务行为。",
    "title-body-too-short": (
        "title 主体过短或仅由代号占据。删掉括号尾巴后剩余文字 < 6 个汉字，"
        "无法独立表达验证目标；请在主体补充动宾结构（验证什么 / 何种条件 / 预期）。"
    ),
}


def validate_case(case: dict) -> list[dict]:
    case_id = case.get("id", "<unknown>")
    issues: list[dict] = []
    for field_path, text in collect_case_fields(case):
        if not isinstance(text, str):
            continue
        for v in find_violations_in_text(text, field_path):
            v["case_id"] = case_id
            v["message"] = RULE_MESSAGES[v["rule"]].format(
                code=v["code"], field=field_path
            )
            issues.append(v)
    for v in title_body_issues(case):
        v["case_id"] = case_id
        v["message"] = RULE_MESSAGES[v["rule"]]
        issues.append(v)
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate self-containment of functional-cases.yaml"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".supertester/test-cases/functional-cases.yaml",
        help=(
            "Path to functional-cases.yaml "
            "(default: .supertester/test-cases/functional-cases.yaml)"
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of human-readable text",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit reported violations (0 = no limit)",
    )
    args = parser.parse_args()

    p = Path(args.path)
    if not p.exists():
        sys.stderr.write(f"[check-self-contained] file not found: {p}\n")
        return 2

    try:
        with p.open("r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)
    except yaml.YAMLError as e:
        sys.stderr.write(f"[check-self-contained] YAML parse error: {e}\n")
        return 2

    cases = (doc or {}).get("cases", []) or []
    if not isinstance(cases, list):
        sys.stderr.write(
            "[check-self-contained] 'cases' must be a list at the YAML root\n"
        )
        return 2

    all_issues: list[dict] = []
    for c in cases:
        if not isinstance(c, dict):
            continue
        all_issues.extend(validate_case(c))

    truncated = False
    reported = all_issues
    if args.limit and len(all_issues) > args.limit:
        reported = all_issues[: args.limit]
        truncated = True

    result = {
        "file": str(p),
        "total_cases": len(cases),
        "violation_count": len(all_issues),
        "reported_count": len(reported),
        "truncated": truncated,
        "violations": reported,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if not all_issues:
            print(
                f"[check-self-contained] PASS  {len(cases)} 条用例，0 处自包含违规"
            )
        else:
            print(
                f"[check-self-contained] FAIL  {len(cases)} 条用例，"
                f"{len(all_issues)} 处自包含违规"
                + (f"（仅展示前 {len(reported)} 条）" if truncated else "")
            )
            for v in reported:
                print(f"- [{v['rule']}] {v['case_id']} / {v['field']}")
                if v["code"]:
                    print(f"    code: {v['code']}")
                print(f"    snippet: …{v['snippet']}…")
                print(f"    {v['message']}")
                print()
            print(
                "修复要求：在出现代号的字段中，把代号替代的实际名称/文案/状态/假设的语义"
                "内嵌进去，代号降级为括号注释（仅 feature / sub_refs / sources 三个"
                "纯溯源字段允许直接放代号）。修复后重跑本校验直到 0 处违规，再进入下一步。"
            )

    return 1 if all_issues else 0


if __name__ == "__main__":
    sys.exit(main())
