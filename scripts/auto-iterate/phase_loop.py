"""通用阶段/模块迭代循环"""
from pathlib import Path
from typing import Callable
import patcher
from scorer import score_artifact, is_converged
from analyzer import run_analysis_cycle


def read_skill_content(skill_dir: str, files: list) -> str:
    """读取相关 skill 文件内容拼接 (供 patch 生成参考)"""
    parts = []
    for f in files:
        path = Path(skill_dir).parent / f  # file paths are relative to TestingAgent root
        if path.exists():
            parts.append(f"=== {f} ===\n{path.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def iterate(phase: str, module_name: str,
            generator: Callable[[int], str],
            baseline_a: dict, convergence: dict,
            skill_dir: str, snapshot_root: str, iter_root: str,
            abstraction_map: dict, skill_files: list = None,
            max_revise_attempts: int = 2,
            prompt_dir: str = None, model: str = "sonnet",
            timeout: int = 300) -> dict:
    """通用迭代循环。

    Args:
        generator: (iter_num) -> ai_output 字符串。封装了不同阶段的生成逻辑。
        skill_files: 相关 skill 文件相对路径列表 (供 analyze 读取全文)

    Returns:
        {
            "converged": bool,
            "iterations": int,
            "final_score": dict,
            "history": [...],
            "weak_dimensions": [...],  # 仅未收敛时
        }
    """
    if skill_files is None:
        skill_files = []

    history = []
    last_score = None

    for iter_num in range(1, convergence["max_iterations"] + 1):
        iter_dir = Path(iter_root) / f"iter-{iter_num}"
        iter_dir.mkdir(parents=True, exist_ok=True)

        # ① 生成
        ai_output = generator(iter_num)
        (iter_dir / "ai-output.md").write_text(ai_output, encoding='utf-8')

        # ② 打分
        score = score_artifact(
            phase=phase, module_name=module_name, iteration=iter_num,
            ai_output=ai_output, baseline_a=baseline_a,
            output_path=str(iter_dir / "score.json"),
            convergence=convergence, prompt_dir=prompt_dir,
            model=model, timeout=timeout,
        )
        last_score = score
        history.append({
            "iter": iter_num,
            "score": score.get("total_weighted_score", 0.0),
            "weak_dimensions": score.get("weak_dimensions", []),
        })

        # ③ 收敛检查
        if is_converged(score, convergence):
            return {
                "converged": True,
                "iterations": iter_num,
                "final_score": score,
                "history": history,
            }

        # ④ 分析 + patch 生成 + 审查
        skill_content = read_skill_content(skill_dir, skill_files)
        analysis = run_analysis_cycle(
            score=score, skill_content=skill_content,
            iteration_history=history, abstraction_map=abstraction_map,
            iter_dir=str(iter_dir), max_revise_attempts=max_revise_attempts,
            prompt_dir=prompt_dir, model=model, timeout=timeout,
        )

        if analysis.get("skip_apply"):
            history[-1]["patch_skipped"] = True
            continue  # 审查未通过，跳过本轮 patch

        # ⑤ 快照 + 应用
        snap_dir = Path(snapshot_root) / f"iter-{iter_num}"
        patcher.snapshot(skill_dir, str(snap_dir))

        testing_agent_root = str(Path(skill_dir).parent)
        errors = patcher.apply_patches(
            analysis["patch"].get("patches", []),
            testing_agent_root,
        )
        history[-1]["patches_applied"] = len(analysis["patch"].get("patches", []))
        if errors:
            history[-1]["patch_errors"] = errors

    # 未收敛
    return {
        "converged": False,
        "iterations": convergence["max_iterations"],
        "final_score": last_score,
        "history": history,
        "weak_dimensions": last_score.get("weak_dimensions", []) if last_score else [],
    }
