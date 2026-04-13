from pathlib import Path
from state import State


def _fmt_score(s: dict) -> str:
    if not s:
        return "N/A"
    return f"{s.get('total_weighted_score', 0.0):.2f}"


def generate_report(state: State, output_path: str):
    """生成最终报告"""
    lines = []
    lines.append("# Supertester Skill 自动迭代优化报告\n")
    lines.append(f"开始时间: {state.started_at}\n")

    # 执行摘要
    lines.append("## 执行摘要\n")
    phase3_total = len(state.converged_modules) + len(state.unconverged_modules)
    lines.append(f"- Phase 1: {'已收敛' if state.phase1_converged else '未收敛'}, "
                 f"{state.phase1_iterations} 轮, 最终分 {_fmt_score(state.phase1_final_score)}")
    lines.append(f"- Phase 2: {'已收敛' if state.phase2_converged else '未收敛'}, "
                 f"{state.phase2_iterations} 轮, 最终分 {_fmt_score(state.phase2_final_score)}")
    lines.append(f"- Phase 3: {phase3_total} 个模块, "
                 f"{len(state.converged_modules)} 个收敛, "
                 f"{len(state.unconverged_modules)} 个需人工介入\n")

    # Phase 1 轨迹
    if "phase1" in state.history:
        lines.append("## Phase 1 迭代轨迹\n")
        lines.append("| 轮次 | 总分 | 短板维度 |")
        lines.append("|------|------|----------|")
        for h in state.history["phase1"]:
            weak = ", ".join(h.get("weak_dimensions", [])) or "—"
            lines.append(f"| {h['iter']} | {h.get('score', 0):.2f} | {weak} |")
        lines.append("")

    # Phase 2 轨迹
    if "phase2" in state.history:
        lines.append("## Phase 2 迭代轨迹\n")
        lines.append("| 轮次 | 总分 | 短板维度 |")
        lines.append("|------|------|----------|")
        for h in state.history["phase2"]:
            weak = ", ".join(h.get("weak_dimensions", [])) or "—"
            lines.append(f"| {h['iter']} | {h.get('score', 0):.2f} | {weak} |")
        lines.append("")

    # Phase 3 各模块轨迹
    lines.append("## Phase 3 各模块迭代轨迹\n")
    for module_name in state.converged_modules:
        if module_name in state.history:
            lines.append(f"### 模块: {module_name} (已收敛)\n")
            lines.append("| 轮次 | 总分 | 短板维度 |")
            lines.append("|------|------|----------|")
            for h in state.history[module_name]:
                weak = ", ".join(h.get("weak_dimensions", [])) or "—"
                lines.append(f"| {h['iter']} | {h.get('score', 0):.2f} | {weak} |")
            lines.append("")

    # 未收敛项
    if state.unconverged_modules:
        lines.append("## 未收敛项 (需人工介入)\n")
        lines.append("| 阶段/模块 | 最高分 | 短板维度 |")
        lines.append("|-----------|--------|----------|")
        for u in state.unconverged_modules:
            dims = ", ".join(u.get("gap_dimensions", [])) or "—"
            lines.append(f"| {u['module']} | {u.get('best_score', 0):.2f} | {dims} |")
        lines.append("")

    Path(output_path).write_text("\n".join(lines), encoding='utf-8')
