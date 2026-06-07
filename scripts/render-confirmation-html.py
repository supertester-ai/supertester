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
import webbrowser
from pathlib import Path
from typing import Iterable


PHASE_CONFIG = {
    "1": {
        "title": "阶段一 确认页 · 需求解析",
        "phase": "阶段一：需求解析",
        "output": "phase-1-confirmation.html",
        "checklist": [
            "功能模块、功能点、验收标准、边界条件已经结构化落盘。",
            "关键测试资产、证据类型、规则/枚举/内容资产已经展开，不以示例替代完整需求。",
            "所有关键模糊项已澄清；如仍有 pending/blocked 项，已在页面中明确暴露。",
            "用户确认后才允许进入 阶段二 需求关联分析。",
        ],
        "files": [
            ("解析后的需求", "requirements/parsed-requirements.md"),
            ("澄清记录", "requirements/clarifications.json"),
            ("分析发现", "findings.md"),
            ("测试计划", "test_plan.md"),
        ],
    },
    "2": {
        "title": "阶段二 确认页 · 需求关联分析",
        "phase": "阶段二：需求关联分析",
        "output": "phase-2-confirmation.html",
        "checklist": [
            "功能依赖、状态依赖、证据依赖和共享资源风险已经覆盖。",
            "隐含需求、PRD 外运营边界和 blocked/pending 项已明确列出。",
            "跨模块场景不仅包含正常主流程，也包含中断恢复、历史列表、错误传播和证据链。",
            "test-reviewer 审查摘要已纳入页面；用户确认后才允许进入 阶段三。",
        ],
        "files": [
            ("模块依赖", "requirements/module-dependencies.md"),
            ("隐含需求", "requirements/implicit-requirements.md"),
            ("跨模块场景", "requirements/cross-module-scenarios.md"),
            ("最新关联分析审查", "reviews/review-association-*.md"),
            ("分析发现", "findings.md"),
        ],
    },
    "3": {
        "title": "阶段三 确认页 · 功能测试用例",
        "phase": "阶段三：功能测试用例",
        "output": "phase-3-confirmation.html",
        "checklist": [
            "覆盖矩阵 已展示完整、部分、缺失和 blocked 覆盖状态。",
            "功能测试用例 已通过自包含校验和 reviewer 审查。",
            "用例统计、类型分布、P0/P1/P2 优先级分布和关键缺口已暴露。",
            "用户确认后，阶段三 才算完成；本工作流到功能测试用例为止。",
        ],
        "files": [
            ("覆盖矩阵", "test-cases/coverage-matrix.md"),
            ("功能测试用例", "test-cases/functional-cases.yaml"),
            ("去重报告", "test-cases/deduplication-report.md"),
            ("测试面规划", "test-cases/test-surface-plan.md"),
            ("设计产物", "test-cases/design-artifacts.md"),
            ("最新测试用例审查", "reviews/review-test-cases-*.md"),
            ("分析发现", "findings.md"),
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


_LEVEL_ORDER = {"P0": 0, "P1": 1, "P2": 2}


def multiline_html(value: object) -> str:
    """转义并把换行渲染为 <br>，用于 action/result 等可能多行的字段。"""
    text = "" if value is None else str(value)
    return html.escape(text).replace("\n", "<br>")


def level_badge(level: object) -> str:
    lv = str(level or "P1").strip().upper() or "P1"
    cls = {"P0": "p0", "P1": "p1", "P2": "p2"}.get(lv, "p1")
    return f'<span class="badge lvl-{cls}">{html.escape(lv)}</span>'


def step_flags(step: dict) -> str:
    flags = []
    if step.get("verbatim"):
        flags.append('<span class="badge flag-verbatim">逐字</span>')
    status = step.get("status")
    if status:
        flags.append(f'<span class="badge flag-status">{html.escape(str(status).upper())}</span>')
    return "".join(flags)


def leaf_step_row(step: dict) -> str:
    if not isinstance(step, dict):
        return f'<tr><td colspan="5">{multiline_html(step)}</td></tr>'
    source = step.get("source", "") or ""
    return (
        "<tr>"
        f"<td>{multiline_html(step.get('action'))}</td>"
        f"<td>{multiline_html(step.get('result'))}</td>"
        f"<td>{level_badge(step.get('level'))}</td>"
        f"<td>{html.escape(str(source))}</td>"
        f"<td>{step_flags(step)}</td>"
        "</tr>"
    )


_STEP_TABLE_HEAD = (
    '<table class="step-table"><thead><tr>'
    "<th>操作</th><th>预期结果</th><th>优先级</th><th>来源</th><th>标记</th>"
    "</tr></thead><tbody>"
)


def render_case_steps(steps: object) -> str:
    """按是否为'组'聚合渲染步骤：group 步骤折叠其 children，散落的叶子步骤合并为一张表。"""
    out: list[str] = []
    leaf_buffer: list[str] = []

    def flush() -> None:
        if leaf_buffer:
            out.append(
                '<div class="step-loose"><div class="group-title">独立步骤</div>'
                + _STEP_TABLE_HEAD
                + "".join(leaf_buffer)
                + "</tbody></table></div>"
            )
            leaf_buffer.clear()

    for step in steps or []:
        if isinstance(step, dict) and step.get("group"):
            flush()
            children = step.get("children") or []
            rows = "".join(leaf_step_row(child) for child in children)
            out.append(
                '<div class="step-group">'
                f'<div class="group-title">组 · {multiline_html(step.get("action"))}'
                f' <span class="muted">（{len(children)} 步）</span></div>'
                + _STEP_TABLE_HEAD
                + rows
                + "</tbody></table></div>"
            )
        else:
            leaf_buffer.append(leaf_step_row(step))
    flush()
    return "\n".join(out)


def case_max_level(case: dict) -> str:
    levels: list[str] = []
    for step in case.get("steps") or []:
        if isinstance(step, dict) and step.get("group"):
            for child in step.get("children") or []:
                if isinstance(child, dict):
                    levels.append(str(child.get("level", "P1")).upper())
        elif isinstance(step, dict):
            levels.append(str(step.get("level", "P1")).upper())
    if not levels:
        return "P1"
    return sorted(levels, key=lambda lv: _LEVEL_ORDER.get(lv, 1))[0]


def render_case_card(case: dict) -> str:
    cid = html.escape(str(case.get("id", "")))
    name = html.escape(str(case.get("case_name", "")))
    ctype = str(case.get("type", "")).strip()

    badges = []
    type_label = {"matrix": "矩阵", "single": "单条"}.get(ctype, ctype)
    if type_label:
        badges.append(f'<span class="badge type">{html.escape(type_label)}</span>')
    badges.append(level_badge(case_max_level(case)))
    for ev in case.get("evidence_types") or []:
        badges.append(f'<span class="badge ev">{html.escape(str(ev))}</span>')

    meta_rows: list[str] = []

    def meta_row(key: str, value_html: str) -> None:
        if value_html:
            meta_rows.append(f"<div><dt>{html.escape(key)}</dt><dd>{value_html}</dd></div>")

    meta_row("功能点", html.escape(str(case.get("feature", "") or "")))
    sub_refs = case.get("sub_refs") or []
    if sub_refs:
        meta_row("关联", html.escape(", ".join(str(s) for s in sub_refs)))
    meta_row("验证方式", html.escape(str(case.get("verification_method", "") or "")))
    precondition = case.get("precondition")
    if precondition:
        meta_row("前置条件", multiline_html(precondition))
    key_assets = case.get("key_assets") or []
    if key_assets:
        items = "".join(f"<li>{multiline_html(asset)}</li>" for asset in key_assets)
        meta_row("关键资产", f'<ul class="ka">{items}</ul>')

    meta_html = f'<dl class="case-meta">{"".join(meta_rows)}</dl>' if meta_rows else ""
    steps_html = render_case_steps(case.get("steps"))

    return (
        '<details class="case-card">'
        f'<summary><span class="cid">{cid}</span>'
        f'<span class="cname">{name}</span>'
        f'<span class="badge-row">{"".join(badges)}</span></summary>'
        f'<div class="case-body">{meta_html}{steps_html}</div>'
        "</details>"
    )


def render_functional_cases(text: str) -> str | None:
    """把 functional-cases.yaml 渲染为按模块聚合的折叠卡片；无法解析时返回 None 由调用方降级。"""
    try:
        import yaml  # type: ignore
    except Exception:
        return None
    try:
        data = yaml.safe_load(text)
    except Exception:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        return None

    cases = [c for c in data["cases"] if isinstance(c, dict)]
    meta = data.get("meta") or {}

    parts: list[str] = []
    if isinstance(meta, dict) and meta:
        bits: list[str] = []
        if meta.get("total_cases") is not None:
            bits.append(f"用例 {meta['total_cases']}")
        if meta.get("total_steps") is not None:
            bits.append(f"步骤 {meta['total_steps']}")
        level_dist = meta.get("level_distribution") or {}
        for key in ("P0", "P1", "P2"):
            if key in level_dist:
                bits.append(f"{key} {level_dist[key]}")
        if bits:
            chips = "".join(f'<span class="sum-chip">{html.escape(b)}</span>' for b in bits)
            parts.append(f'<div class="cases-summary">{chips}</div>')

    # 按 module 聚合，保留首次出现顺序
    order: list[str] = []
    grouped: dict[str, list[dict]] = {}
    for case in cases:
        module = str(case.get("module") or "未分组")
        if module not in grouped:
            grouped[module] = []
            order.append(module)
        grouped[module].append(case)

    for module in order:
        module_cases = grouped[module]
        inner = "".join(render_case_card(c) for c in module_cases)
        parts.append(
            '<details class="module-card" open>'
            f'<summary>{html.escape(module)}'
            f'<span class="muted"> · {len(module_cases)} 条用例</span></summary>'
            f'<div class="module-body">{inner}</div>'
            "</details>"
        )
    return "\n".join(parts)


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
        if path.name == "functional-cases.yaml":
            structured = render_functional_cases(text)
            if structured is not None:
                return structured
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
                "<span>缺失或尚未生成</span></div>"
            )
            continue
        meta = file_meta(path, project_dir)
        cards.append(
            '<div class="source-card ready">'
            f"<strong>{html.escape(label)}</strong>"
            f"<span>{html.escape(meta['path'])}</span>"
            f"<span>修改时间：{html.escape(meta['mtime'])}</span>"
            f"<span>{html.escape(meta['size'])}</span>"
            "</div>"
        )
    return "\n".join(cards)


def render_body(config: dict, files: list[tuple[str, Path | None]], project_dir: Path) -> tuple[str, str]:
    sections: list[tuple[str, str]] = []
    checklist = "\n".join(f"<li>{html.escape(item)}</li>" for item in config["checklist"])
    sections.append(
        (
            "审查门禁",
            '<section class="panel"><h2>审查门禁</h2>'
            '<p><span class="status">待人工确认</span></p>'
            f'<ul class="checklist">{checklist}</ul></section>',
        )
    )
    sections.append(
        (
            "源文件清单",
            '<section class="panel"><h2>源文件清单</h2><div class="source-grid">'
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
            "确认",
            '<section class="panel"><h2>确认</h2>'
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
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="生成后不自动用本地浏览器打开确认页（默认会自动打开）",
    )
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

    if not args.no_open:
        open_in_browser(out_path)
    return 0


def open_in_browser(out_path: Path) -> None:
    """尽量用本地默认浏览器打开确认页，失败时只打印提示，不影响主流程。"""
    url = out_path.resolve().as_uri()
    try:
        opened = webbrowser.open(url)
    except Exception:
        opened = False
    if opened:
        print(f"已尝试在本地浏览器打开确认页：{url}")
        return
    # webbrowser 在部分平台/无头环境返回 False，回退到平台命令。
    import shutil
    import subprocess

    candidates = []
    if os.name == "nt":
        candidates.append(["cmd", "/c", "start", "", str(out_path)])
    candidates.append(["open", str(out_path)])      # macOS
    candidates.append(["xdg-open", str(out_path)])  # Linux
    candidates.append(["wslview", str(out_path)])   # WSL
    for cmd in candidates:
        if shutil.which(cmd[0]) is None:
            continue
        try:
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"已尝试在本地浏览器打开确认页：{url}")
            return
        except Exception:
            continue
    print(f"未能自动打开浏览器，请手动打开确认页：{out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
