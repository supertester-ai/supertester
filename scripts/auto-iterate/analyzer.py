import json
from pathlib import Path
from jinja2 import Template
from claude_runner import claude_call


def _render(prompt_dir: str, name: str, **kwargs) -> str:
    text = Path(f"{prompt_dir}/{name}").read_text(encoding='utf-8')
    return Template(text).render(**kwargs)


def generate_patch(score: dict, skill_content: str,
                   iteration_history: list, abstraction_map: dict,
                   output_path: str, prompt_dir: str = None,
                   model: str = "sonnet", timeout: int = 300) -> dict:
    if prompt_dir is None:
        prompt_dir = str(Path(__file__).parent / "prompts")
    prompt = _render(
        prompt_dir, "analyze-and-patch.md",
        score_json=json.dumps(score, ensure_ascii=False, indent=2),
        skill_content=skill_content,
        iteration_history=json.dumps(iteration_history, ensure_ascii=False, indent=2),
        abstraction_map=json.dumps(abstraction_map, ensure_ascii=False, indent=2),
    )
    result = claude_call(prompt, output_path, parse_json=True,
                         model=model, timeout=timeout)
    if result is None:
        raise RuntimeError("Failed to parse patch JSON")
    return result


def review_patch(patch: dict, skill_content: str, output_path: str,
                 prompt_dir: str = None, model: str = "sonnet",
                 timeout: int = 300) -> dict:
    if prompt_dir is None:
        prompt_dir = str(Path(__file__).parent / "prompts")
    prompt = _render(
        prompt_dir, "review-patch.md",
        patch_json=json.dumps(patch, ensure_ascii=False, indent=2),
        skill_content=skill_content,
    )
    result = claude_call(prompt, output_path, parse_json=True,
                         model=model, timeout=timeout)
    if result is None:
        raise RuntimeError("Failed to parse review JSON")
    return result


def revise_patch(original_patch: dict, review_issues: list,
                 output_path: str, prompt_dir: str = None,
                 model: str = "sonnet", timeout: int = 300) -> dict:
    if prompt_dir is None:
        prompt_dir = str(Path(__file__).parent / "prompts")
    prompt = _render(
        prompt_dir, "revise-patch.md",
        original_patch=json.dumps(original_patch, ensure_ascii=False, indent=2),
        review_issues=json.dumps(review_issues, ensure_ascii=False, indent=2),
    )
    result = claude_call(prompt, output_path, parse_json=True,
                         model=model, timeout=timeout)
    if result is None:
        raise RuntimeError("Failed to parse revised patch JSON")
    return result


def run_analysis_cycle(score: dict, skill_content: str,
                       iteration_history: list, abstraction_map: dict,
                       iter_dir: str, max_revise_attempts: int = 2,
                       prompt_dir: str = None, models: dict = None,
                       timeout: int = 300) -> dict:
    """Complete analysis -> review -> revise cycle.

    Returns: {
        "verdict": "PASS" | "REVISE",
        "patch": final patch dict (passed review or last attempted)
        "skip_apply": True if review failed after max attempts
        "review_history": [...]
    }
    """
    if models is None:
        models = {"analyze": "sonnet", "review": "sonnet", "revise": "sonnet"}

    iter_path = Path(iter_dir)
    iter_path.mkdir(parents=True, exist_ok=True)

    patch = generate_patch(
        score, skill_content, iteration_history, abstraction_map,
        str(iter_path / "patch.json"),
        prompt_dir=prompt_dir, model=models["analyze"], timeout=timeout,
    )

    review_history = []
    for attempt in range(max_revise_attempts + 1):
        suffix = "" if attempt == 0 else f"-revise-{attempt}"
        review = review_patch(
            patch, skill_content,
            str(iter_path / f"review{suffix}.json"),
            prompt_dir=prompt_dir, model=models["review"], timeout=timeout,
        )
        review_history.append(review)
        if review["verdict"] == "PASS":
            return {
                "verdict": "PASS",
                "patch": patch,
                "review_history": review_history,
            }
        if attempt >= max_revise_attempts:
            break
        patch = revise_patch(
            patch, review.get("issues", []),
            str(iter_path / f"patch-revised-{attempt + 1}.json"),
            prompt_dir=prompt_dir, model=models["revise"], timeout=timeout,
        )

    return {
        "verdict": "REVISE",
        "patch": patch,
        "skip_apply": True,
        "review_history": review_history,
    }
