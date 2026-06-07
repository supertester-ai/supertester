#!/usr/bin/env python3
"""Render Supertester human confirmation pages.

Usage:
  python3 scripts/render-confirmation-html.py --phase 2 --project-dir /path/to/project

The script intentionally uses only the Python standard library so it can run in
projects without extra dependencies.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import html
import json
import os
import re
from pathlib import Path
from typing import Iterable


PHASE_CONFIG = {
    "1": {
        "title": "Phase 1 Confirmation - Requirement Analysis",
        "phase": "Phase 1: Requirement Analysis",
        "output": "phase-1-confirmation.html",
        "checklist": [
            "功能模块、功能点、验收标准、边界条件已经结构化落盘。",
            "关键测试资产、证据类型、规则/枚举/内容资产已经展开，不以示例替代完整需求。",
            "所有关键模糊项已澄清；如仍有 pending/blocked 项，已在页面中明确暴露。",
            "用户确认后才允许进入 Phase 2 requirement-association。",
        ],
        "files": [
            ("Parsed Requirements", "requirements/parsed-requirements.md"),
            ("Clarifications", "requirements/clarifications.json"),
            ("Findings", "findings.md"),
            ("Test Plan", "test_plan.md"),
        ],
    },
    "2": {
        "title": "Phase 2 Confirmation - Requirement Association",
        "phase": "Phase 2: Requirement Association",
        "output": "phase-2-confirmation.html",
        "checklist": [
            "功能依赖、状态依赖、证据依赖和共享资源风险已经覆盖。",
            "隐含需求、PRD 外运营边界和 blocked/pending 项已明确列出。",
            "跨模块场景不仅包含 happy path，也包含中断恢复、历史列表、错误传播和证据链。",
            "test-reviewer 审查摘要已纳入页面；用户确认后才允许进入 Phase 3。",
        ],
        "files": [
            ("Module Dependencies", "requirements/module-dependencies.md"),
            ("Implicit Requirements", "requirements/implicit-requirements.md"),
            ("Cross-Module Scenarios", "requirements/cross-module-scenarios.md"),
            ("Latest Association Review", "reviews/review-association-*.md"),
            ("Findings", "findings.md"),
        ],
    },
    "3": {
        "title": "Phase 3 Confirmation - Functional Test Cases",
        "phase": "Phase 3: Functional Test Cases",
        "output": "phase-3-confirmation.html",
        "checklist": [
            "coverage-matrix.md 已展示完整、部分、缺失和 blocked 覆盖状态。",
            "functional-cases.yaml 已通过自包含校验和 reviewer 审查。",
            "用例统计、类型分布、P0/P1/P2 优先级分布和关键缺口已暴露。",
            "用户确认后，Phase 3 才算完成；本工作流到功能测试用例为止。",
        ],
        "files": [
            ("Coverage Matrix", "test-cases/coverage-matrix.md"),
            ("Functional Cases", "test-cases/functional-cases.yaml"),
            ("Deduplication Report", "test-cases/deduplication-report.md"),
            ("Test Surface Plan", "test-cases/test-surface-plan.md"),
            ("Design Artifacts", "test-cases/design-artifacts.md"),
            ("Latest Test Case Review", "reviews/review-test-cases-*.md"),
            ("Findings", "findings.md"),
        ],
    },
}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def latest_match(supertester_dir: Path, pattern: str) -> Path | None:
    matches = [Path(p) for p in glob.glob(str(supertester_dir / pattern))]
    if not matches:
        return None
    return max(matches, key=lambda item: item.stat().st_mtime)


def resolve_file(supertester_dir: Path, rel_path: str) -> Path | None:
    if "*" in rel_path:
        return latest_match(supertester_dir, rel_path)
    path = supertester_dir / rel_path
    return path if path.exists() else None


def file_meta(path: Path, project_dir: Path) -> dict[str, str]:
    stat = path.stat()
    try:
        rel = path.relative_to(project_dir)
    except ValueError:
        rel = path
    return {
        "path": str(rel),
        "mtime": dt.datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
        "size": f"{stat.st_size:,} bytes",
    }


def slugify(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", text.strip()).strip("-")
    return value or "section"


def inline_md(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def render_table(lines: list[str]) -> str:
    rows = []
    for line in lines:
        cells = [inline_md(cell.strip()) for cell in line.strip().strip("|").split("|")]
        rows.append(cells)
    if len(rows) < 2:
        return "<pre><code>" + html.escape("\n".join(lines)) + "</code></pre>"

    header = rows[0]
    body_rows = rows[2:] if re.match(r"^\s*\|?\s*:?-{3,}", lines[1]) else rows[1:]
    out = ["<table><thead><tr>"]
    out.extend(f"<th>{cell}</th>" for cell in header)
    out.append("</tr></thead><tbody>")
    for row in body_rows:
        out.append("<tr>")
        out.extend(f"<td>{cell}</td>" for cell in row)
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def markdown_to_html(markdown: str) -> str:
    output: list[str] = []
    lines = markdown.splitlines()
    i = 0
    in_list = False
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            if in_list:
                output.append("</ul>")
                in_list = False
            i += 1
            continue
        if line.lstrip().startswith("|"):
            if in_list:
                output.append("</ul>")
                in_list = False
            table_lines = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            output.append(render_table(table_lines))
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            if in_list:
                output.append("</ul>")
                in_list = False
            level = min(len(heading.group(1)) + 1, 4)
            output.append(f"<h{level}>{inline_md(heading.group(2))}</h{level}>")
            i += 1
            continue
        bullet = re.match(r"^\s*[-*]\s+(.+)$", line)
        if bullet:
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{inline_md(bullet.group(1))}</li>")
            i += 1
            continue
        if in_list:
            output.append("</ul>")
            in_list = False
        output.append(f"<p>{inline_md(line)}</p>")
        i += 1
    if in_list:
        output.append("</ul>")
    return "\n".join(output)


def render_document(path: Path) -> str:
    suffix = path.suffix.lower()
    text = read_text(path)
    if suffix == ".json":
        try:
            text = json.dumps(json.loads(text), ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            pass
        return f"<pre><code>{html.escape(text)}</code></pre>"
    if suffix in {".yaml", ".yml"}:
        return f"<pre><code>{html.escape(text)}</code></pre>"
    if suffix == ".md":
        return markdown_to_html(text)
    return f"<pre><code>{html.escape(text)}</code></pre>"


def render_source_cards(files: Iterable[tuple[str, Path | None]], project_dir: Path) -> str:
    cards = []
    for label, path in files:
        if path is None:
            cards.append(
                f'<div class="source-card missing"><strong>{html.escape(label)}</strong>'
                "<span>Missing or not generated yet</span></div>"
            )
            continue
        meta = file_meta(path, project_dir)
        cards.append(
            '<div class="source-card ready">'
            f"<strong>{html.escape(label)}</strong>"
            f"<span>{html.escape(meta['path'])}</span>"
            f"<span>Modified: {html.escape(meta['mtime'])}</span>"
            f"<span>{html.escape(meta['size'])}</span>"
            "</div>"
        )
    return "\n".join(cards)


def render_body(config: dict, files: list[tuple[str, Path | None]], project_dir: Path) -> tuple[str, str]:
    sections: list[tuple[str, str]] = []
    checklist = "\n".join(f"<li>{html.escape(item)}</li>" for item in config["checklist"])
    sections.append(
        (
            "Review Gate",
            '<section class="panel"><h2>Review Gate</h2>'
            '<p><span class="status">Needs human confirmation</span></p>'
            f'<ul class="checklist">{checklist}</ul></section>',
        )
    )
    sections.append(
        (
            "Source Files",
            '<section class="panel"><h2>Source Files</h2><div class="source-grid">'
            + render_source_cards(files, project_dir)
            + "</div></section>",
        )
    )
    for label, path in files:
        if path is None:
            continue
        sections.append(
            (
                label,
                f'<section class="panel doc"><h2>{html.escape(label)}</h2>'
                + render_document(path)
                + "</section>",
            )
        )
    sections.append(
        (
            "Confirmation",
            '<section class="panel"><h2>Confirmation</h2>'
            "<p>请审查本页面内容。确认通过后，在对话中明确回复确认该阶段，Supertester 才能更新 test_plan.md 并进入下一步。</p>"
            '<p class="footer-note">此 HTML 是确认视图；Markdown/YAML/JSON 源文件仍是可追踪来源。</p>'
            "</section>",
        )
    )
    nav = "\n".join(
        f'<a href="#{slugify(title)}">{html.escape(title)}</a>' for title, _ in sections
    )
    body = "\n".join(
        content.replace("<section ", f'<section id="{slugify(title)}" ', 1)
        for title, content in sections
    )
    return nav, body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=sorted(PHASE_CONFIG))
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--template", default=None)
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    supertester_dir = project_dir / ".supertester"
    if not supertester_dir.exists():
        raise SystemExit(f"Missing .supertester directory: {supertester_dir}")

    script_dir = Path(__file__).resolve().parent
    plugin_root = script_dir.parent
    template_path = Path(args.template).resolve() if args.template else plugin_root / "templates" / "confirmation.html"
    template = read_text(template_path)

    config = PHASE_CONFIG[args.phase]
    files = [
        (label, resolve_file(supertester_dir, rel_path))
        for label, rel_path in config["files"]
    ]
    nav, body = render_body(config, files, project_dir)

    output = (
        template.replace("{{TITLE}}", html.escape(config["title"]))
        .replace("{{PHASE}}", html.escape(config["phase"]))
        .replace("{{GENERATED_AT}}", html.escape(now_iso()))
        .replace("{{PROJECT_DIR}}", html.escape(str(project_dir)))
        .replace("{{NAV}}", nav)
        .replace("{{BODY}}", body)
    )

    out_dir = supertester_dir / "confirmations"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / config["output"]
    out_path.write_text(output, encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
