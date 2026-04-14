import json
from pathlib import Path
from jinja2 import Template
from claude_runner import claude_call


def _render(prompt_dir: str, name: str, **kwargs) -> str:
    text = Path(f"{prompt_dir}/{name}").read_text(encoding='utf-8')
    return Template(text).render(**kwargs)


def _load_manual_override(path: str) -> dict | None:
    """If a .manual sidecar JSON exists, use it instead of calling Claude.

    Allows resuming after a parse failure by manually fixing the JSON.
    E.g. if patch.json failed, write patch.json.manual with corrected JSON.
    """
    manual = Path(path + ".manual")
    if manual.exists():
        try:
            return json.loads(manual.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Manual override {manual} is invalid JSON: {e}")
    return None


def _diag(raw_path: str, kind: str) -> str:
    """Build actionable error message with raw response preview + recovery hint."""
    p = Path(raw_path)
    preview = ""
    if p.exists():
        text = p.read_text(encoding='utf-8')
        head = text[:400].replace('\n', ' | ')
        tail = text[-400:].replace('\n', ' | ') if len(text) > 400 else ""
        preview = f"\n  head: {head!r}\n  tail: {tail!r}\n  size: {len(text)} chars"
    return (
        f"Failed to parse {kind} JSON at {raw_path}.{preview}\n"
        f"  RECOVERY: inspect the file, fix JSON (likely unescaped quotes in string fields), "
        f"save as {raw_path}.manual, then rerun orchestrator.py — it will reuse the manual file."
    )


def generate_patch(score: dict, skill_content: str,
                   iteration_history: list, abstraction_map: dict,
                   output_path: str, prompt_dir: str = None,
                   model: str = "sonnet", timeout: int = 300) -> dict:
    override = _load_manual_override(output_path)
    if override is not None:
        print(f"[analyzer] Using manual override: {output_path}.manual", flush=True)
        return override

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
        raise RuntimeError(_diag(output_path, "patch"))
    return result


def review_patch(patch: dict, skill_content: str, output_path: str,
                 prompt_dir: str = None, model: str = "sonnet",
                 timeout: int = 300) -> dict:
    override = _load_manual_override(output_path)
    if override is not None:
        print(f"[analyzer] Using manual override: {output_path}.manual", flush=True)
        return override

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
        raise RuntimeError(_diag(output_path, "review"))
    return result


def revise_patch(original_patch: dict, review_issues: list,
                 output_path: str, prompt_dir: str = None,
                 model: str = "sonnet", timeout: int = 300) -> dict:
    override = _load_manual_override(output_path)
    if override is not None:
        print(f"[analyzer] Using manual override: {output_path}.manual", flush=True)
        return override

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
        raise RuntimeError(_diag(output_path, "revised patch"))
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
