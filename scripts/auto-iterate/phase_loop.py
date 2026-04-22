"""通用阶段/模块迭代循环。"""

import json
from pathlib import Path
from typing import Callable

import patcher
from analyzer import run_analysis_cycle
from scorer import is_converged, normalize_score, score_artifact


def read_skill_content(skill_dir: str, files: list) -> str:
    """读取相关 skill 文件内容拼接，供分析/打补丁阶段参考。"""
    parts = []
    for f in files:
        path = Path(skill_dir).parent / f
        if path.exists():
            parts.append(f"=== {f} ===\n{path.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def _reuse_ai_output(iter_dir: Path) -> str | None:
    """If ai-output.md exists and looks valid, reuse it."""
    path = iter_dir / "ai-output.md"
    if not path.exists():
        return None
    text = path.read_text(encoding='utf-8')
    if not text.strip() or text.startswith("Error:"):
        return None
    print(f"[phase_loop] Reusing saved ai-output.md from {iter_dir.name}", flush=True)
    return text


def _reuse_score(iter_dir: Path) -> dict | None:
    """If score.json exists and looks valid, reuse it."""
    path = iter_dir / "score.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        print(
            f"[phase_loop] Saved score.json in {iter_dir.name} has invalid structure, ignoring",
            flush=True,
        )
        return None
    data = normalize_score(data)
    if "dimensions" not in data:
        print(
            f"[phase_loop] Saved score.json in {iter_dir.name} missing dimensions, ignoring",
            flush=True,
        )
        return None
    print(f"[phase_loop] Reusing saved score.json from {iter_dir.name}", flush=True)
    return data


def _progress_path(iter_dir: Path) -> Path:
    return iter_dir / "progress.json"


def _load_progress(iter_dir: Path) -> dict:
    path = _progress_path(iter_dir)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _save_progress(iter_dir: Path, **data) -> None:
    _progress_path(iter_dir).write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )


def _history_entry_from_score(iter_num: int, score: dict) -> dict:
    return {
        "iter": iter_num,
        "score": score.get("total_weighted_score", 0.0),
        "weak_dimensions": score.get("weak_dimensions", []),
    }


def iterate(
    phase: str,
    module_name: str,
    generator: Callable[[int], str],
    baseline_a: dict,
    convergence: dict,
    skill_dir: str,
    snapshot_root: str,
    iter_root: str,
    abstraction_map: dict,
    skill_files: list = None,
    max_revise_attempts: int = 2,
    prompt_dir: str = None,
    models: dict = None,
    timeout: int = 300,
) -> dict:
    """通用迭代循环。"""
    if skill_files is None:
        skill_files = []
    if models is None:
        models = {
            "score": "sonnet",
            "analyze": "sonnet",
            "review": "sonnet",
            "revise": "sonnet",
        }

    history = []
    last_score = None
    label = f"{phase}/{module_name}"

    for iter_num in range(1, convergence["max_iterations"] + 1):
        iter_dir = Path(iter_root) / f"iter-{iter_num}"
        iter_dir.mkdir(parents=True, exist_ok=True)
        print(f"[phase_loop] === {label} iter {iter_num}/{convergence['max_iterations']} ===", flush=True)

        progress = _load_progress(iter_dir)
        if progress.get("status") == "completed":
            score = progress.get("score") or _reuse_score(iter_dir) or {}
            if score:
                last_score = score
            entry = _history_entry_from_score(iter_num, score)
            for key in ("patch_skipped", "patches_applied", "patch_errors", "error"):
                if key in progress:
                    entry[key] = progress[key]
            history.append(entry)
            print(f"[phase_loop] [{label} iter {iter_num}] reusing completed progress", flush=True)
            if score and is_converged(score, convergence):
                total = score.get("total_weighted_score", 0.0)
                print(f"[phase_loop] [{label} iter {iter_num}] CONVERGED (total={total:.2f})", flush=True)
                return _build_result(True, iter_num, score, history)
            continue

        ai_output = _reuse_ai_output(iter_dir)
        if ai_output is None:
            print(f"[phase_loop] [{label} iter {iter_num}] step 1/4: generate", flush=True)
            _save_progress(iter_dir, status="in_progress", iter=iter_num, step="generate")
            try:
                ai_output = generator(iter_num)
            except Exception as e:
                print(f"[phase_loop] [{label} iter {iter_num}] generate FAILED: {e}", flush=True)
                _save_progress(
                    iter_dir,
                    status="failed",
                    iter=iter_num,
                    step="generate",
                    error=f"generate failed: {e}",
                )
                history.append({"iter": iter_num, "error": f"generate failed: {e}"})
                return _build_result(False, iter_num - 1, last_score, history)

            if not ai_output or not ai_output.strip():
                print(
                    f"[phase_loop] [{label} iter {iter_num}] generate returned EMPTY output, treating as failure",
                    flush=True,
                )
                _save_progress(
                    iter_dir,
                    status="failed",
                    iter=iter_num,
                    step="generate",
                    error="generate returned empty output",
                )
                history.append({"iter": iter_num, "error": "generate returned empty output"})
                continue

            (iter_dir / "ai-output.md").write_text(ai_output, encoding='utf-8')
            print(f"[phase_loop] [{label} iter {iter_num}] generate OK ({len(ai_output)} chars)", flush=True)

        score = _reuse_score(iter_dir)
        if score is None:
            print(f"[phase_loop] [{label} iter {iter_num}] step 2/4: score", flush=True)
            _save_progress(iter_dir, status="in_progress", iter=iter_num, step="score")
            try:
                score = score_artifact(
                    phase=phase,
                    module_name=module_name,
                    iteration=iter_num,
                    ai_output=ai_output,
                    baseline_a=baseline_a,
                    output_path=str(iter_dir / "score.json"),
                    convergence=convergence,
                    prompt_dir=prompt_dir,
                    model=models["score"],
                    timeout=timeout,
                )
            except Exception as e:
                print(f"[phase_loop] [{label} iter {iter_num}] score FAILED: {e}", flush=True)
                _save_progress(
                    iter_dir,
                    status="failed",
                    iter=iter_num,
                    step="score",
                    error=f"score failed: {e}",
                )
                history.append({"iter": iter_num, "error": f"score failed: {e}"})
                return _build_result(False, iter_num - 1, last_score, history)

        last_score = score
        total = score.get("total_weighted_score", 0.0)
        weak = score.get("weak_dimensions", [])
        print(f"[phase_loop] [{label} iter {iter_num}] score OK: total={total:.2f} weak={weak}", flush=True)

        entry = _history_entry_from_score(iter_num, score)
        history.append(entry)

        if is_converged(score, convergence):
            print(f"[phase_loop] [{label} iter {iter_num}] CONVERGED (total={total:.2f})", flush=True)
            _save_progress(iter_dir, status="completed", iter=iter_num, step="score", score=score)
            return _build_result(True, iter_num, score, history)

        print(f"[phase_loop] [{label} iter {iter_num}] step 3/4: analyze + patch + review", flush=True)
        _save_progress(iter_dir, status="in_progress", iter=iter_num, step="analyze", score=score)
        skill_content = read_skill_content(skill_dir, skill_files)
        try:
            analysis = run_analysis_cycle(
                score=score,
                skill_content=skill_content,
                iteration_history=history,
                abstraction_map=abstraction_map,
                iter_dir=str(iter_dir),
                max_revise_attempts=max_revise_attempts,
                prompt_dir=prompt_dir,
                models=models,
                timeout=timeout,
            )
        except Exception as e:
            print(f"[phase_loop] [{label} iter {iter_num}] analyze FAILED: {e}", flush=True)
            entry["error"] = f"analyze failed: {e}"
            _save_progress(
                iter_dir,
                status="failed",
                iter=iter_num,
                step="analyze",
                score=score,
                error=entry["error"],
            )
            continue

        if analysis.get("skip_apply"):
            print(f"[phase_loop] [{label} iter {iter_num}] patch review REVISE -> skip apply", flush=True)
            entry["patch_skipped"] = True
            _save_progress(
                iter_dir,
                status="completed",
                iter=iter_num,
                step="analyze",
                score=score,
                patch_skipped=True,
            )
            continue

        print(f"[phase_loop] [{label} iter {iter_num}] step 4/4: snapshot + apply patches", flush=True)
        _save_progress(iter_dir, status="in_progress", iter=iter_num, step="apply", score=score)
        snap_dir = Path(snapshot_root) / f"iter-{iter_num}"
        try:
            patcher.snapshot(skill_dir, str(snap_dir))
            testing_agent_root = str(Path(skill_dir).parent)
            patches = analysis["patch"].get("patches", [])
            errors = patcher.apply_patches(patches, testing_agent_root)
            entry["patches_applied"] = len(patches)
            if errors:
                entry["patch_errors"] = errors
                print(f"[phase_loop] [{label} iter {iter_num}] {len(errors)} patch errors", flush=True)
            else:
                print(f"[phase_loop] [{label} iter {iter_num}] applied {len(patches)} patches OK", flush=True)
            _save_progress(
                iter_dir,
                status="completed",
                iter=iter_num,
                step="apply",
                score=score,
                patches_applied=entry["patches_applied"],
                patch_errors=entry.get("patch_errors", []),
            )
        except Exception as e:
            print(f"[phase_loop] [{label} iter {iter_num}] apply FAILED: {e}", flush=True)
            entry["error"] = f"apply failed: {e}"
            _save_progress(
                iter_dir,
                status="failed",
                iter=iter_num,
                step="apply",
                score=score,
                error=entry["error"],
            )
            continue

    print(f"[phase_loop] [{label}] max iterations reached, NOT converged", flush=True)
    return _build_result(False, convergence["max_iterations"], last_score, history)


def _build_result(converged: bool, iterations: int, last_score: dict | None, history: list) -> dict:
    return {
        "converged": converged,
        "iterations": iterations,
        "final_score": last_score or {},
        "history": history,
        "weak_dimensions": last_score.get("weak_dimensions", []) if last_score else [],
    }
