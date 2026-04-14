"""通用阶段/模块迭代循环"""
import json
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


def _reuse_ai_output(iter_dir: Path) -> str | None:
    """If ai-output.md exists and looks valid, reuse it (skip expensive gen)."""
    p = iter_dir / "ai-output.md"
    if not p.exists():
        return None
    text = p.read_text(encoding='utf-8')
    if not text.strip() or text.startswith("Error:"):
        return None
    print(f"[phase_loop] Reusing saved ai-output.md from {iter_dir.name}", flush=True)
    return text


def _reuse_score(iter_dir: Path) -> dict | None:
    """If score.json exists and parses, reuse it (skip expensive scoring)."""
    p = iter_dir / "score.json"
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        if data.get("total_weighted_score") is None and not data.get("dimensions"):
            return None
        print(f"[phase_loop] Reusing saved score.json from {iter_dir.name}", flush=True)
        return data
    except json.JSONDecodeError:
        return None


def iterate(phase: str, module_name: str,
            generator: Callable[[int], str],
            baseline_a: dict, convergence: dict,
            skill_dir: str, snapshot_root: str, iter_root: str,
            abstraction_map: dict, skill_files: list = None,
            max_revise_attempts: int = 2,
            prompt_dir: str = None, models: dict = None,
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
    if models is None:
        models = {"score": "sonnet", "analyze": "sonnet",
                  "review": "sonnet", "revise": "sonnet"}

    history = []
    last_score = None

    for iter_num in range(1, convergence["max_iterations"] + 1):
        iter_dir = Path(iter_root) / f"iter-{iter_num}"
        iter_dir.mkdir(parents=True, exist_ok=True)

        # ① 生成 (复用已保存的 ai-output.md 若存在)
        ai_output = _reuse_ai_output(iter_dir)
        if ai_output is None:
            ai_output = generator(iter_num)
            (iter_dir / "ai-output.md").write_text(ai_output, encoding='utf-8')

        # ② 打分 (复用已保存的 score.json 若存在)
        score = _reuse_score(iter_dir)
        if score is None:
            score = score_artifact(
                phase=phase, module_name=module_name, iteration=iter_num,
                ai_output=ai_output, baseline_a=baseline_a,
                output_path=str(iter_dir / "score.json"),
                convergence=convergence, prompt_dir=prompt_dir,
                model=models["score"], timeout=timeout,
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
            prompt_dir=prompt_dir, models=models, timeout=timeout,
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
