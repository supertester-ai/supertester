#!/usr/bin/env python3
"""
Self-containment validator for .supertester/test-cases/functional-cases.yaml.

Scans every test case's user-facing content fields for internal codes
(C-xxx, E-xxx, IR-xxx, CMS-xxx, CL-xxx, I-xxx, CTX-x, F-xxx, R-xxx,
UC-xxx, S-xxx, A-xxx, PR-xxx, P-xxx, SC-xxx) and flags EVERY occurrence.

Content fields must be completely self-contained and code-free: the actual
name / verbatim copy / state semantics / assumption must be written inline so
the case reads cleanly to a human, an automation author, or an external test
management system. Internal codes are allowed ONLY in the dedicated
traceability fields (feature / sub_refs / sources / source), where they act as
machine-readable cross-references and never reach the reader of the case body.

NOTE: This is stricter than earlier revisions, which tolerated codes as
parenthetical traceability suffixes inside content fields (e.g. 「文案」(C-001)).
Those suffixes clutter the case and scramble the reading, so they are now
violations too. Move every code to feature / sub_refs / sources / source.

Rule reference:
- skills/test-case-generation/SKILL.md '用例自包含原则'
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

# Fields that are pure traceability — codes are expected here and not scanned.
TRACEABILITY_ONLY_KEYS = {"feature", "sub_refs", "sources", "source"}

# User-facing content fields on case root that must be code-free.
ROOT_SCANNED_KEYS = {
    "title",
    "preconditions",
    "steps",
    "expected",
    "key_assets",
}

# Matrix row fields that must be code-free.
MATRIX_ROW_SCANNED_KEYS = {"action", "expected"}


def find_violations_in_text(text: str, field_path: str) -> list[dict]:
    """Find every internal code in a content field — all are violations."""
    if not text:
        return []
    violations: list[dict] = []
    for m in CODE_PATTERN.finditer(text):
        code = m.group(0)
        start, end = m.start(), m.end()
        snippet_start = max(0, start - 20)
        snippet_end = min(len(text), end + 20)
        snippet = text[snippet_start:snippet_end]
        violations.append(
            {
                "field": field_path,
                "code": code,
                "snippet": snippet,
                "rule": "code-in-content-field",
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
    """Flag empty titles. Codes in the title are caught by the content scan."""
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
    return []


RULE_MESSAGES = {
    "code-in-content-field": (
        "代号 {code} 出现在内容字段 {field}。内容字段必须完全自包含、零代号——"
        "把代号背后的实际名称 / 逐字文案 / 状态语义 / 假设描述直接写进字段，删除该代号；"
        "代号只允许出现在 feature / sub_refs / sources / source 四个纯溯源字段中。"
    ),
    "title-empty": "title 为空——必须用一句话描述本条用例要验证的业务行为。",
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
                "修复要求：内容字段（title / preconditions / steps / expected / "
                "key_assets / matrix rows / branches）必须零代号。把每个代号替代的"
                "实际名称 / 逐字文案 / 状态语义 / 假设描述内嵌进字段并删除代号；机器"
                "可追踪性由 feature / sub_refs / sources / source 四个纯溯源字段承载。"
                "修复后重跑本校验直到 0 处违规，再进入下一步。"
            )

    return 1 if all_issues else 0


if __name__ == "__main__":
    sys.exit(main())
