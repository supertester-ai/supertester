import json
from pathlib import Path
from jinja2 import Template
from claude_runner import claude_call


def extract_baselines_for_module(module: dict, output_path: str,
                                  prompt_dir: str = None,
                                  model: str = "sonnet",
                                  timeout: int = 300) -> dict:
    """对单个模块调用 Claude 提取三阶段基准"""
    if prompt_dir is None:
        prompt_dir = str(Path(__file__).parent / "prompts")

    template_text = Path(f"{prompt_dir}/extract-baseline.md").read_text(encoding='utf-8')
    tmpl = Template(template_text)

    prompt = tmpl.render(
        module_name=module["name"],
        reference_cases_json=json.dumps(module.get("ref_cases") or [], ensure_ascii=False, indent=2),
        prd_slice=module.get("prd_content") or "",
    )

    result = claude_call(prompt, output_path, parse_json=True, model=model, timeout=timeout)
    if result is None:
        raise RuntimeError(f"Failed to parse baseline JSON for module {module['name']}")
    return result


def merge_baselines(module_baselines: list[dict]) -> dict:
    """合并各模块基准为总基准，按 module_name 分组"""
    merged = {"phase1": {}, "phase2": {}, "phase3": {}}
    for b in module_baselines:
        name = b["module_name"]
        merged["phase1"][name] = b.get("phase1", {})
        merged["phase2"][name] = b.get("phase2", {})
        merged["phase3"][name] = b.get("phase3", {})
    return merged


def run_phase0(matched_modules: list[dict], output_dir: str,
               prompt_dir: str, model: str, timeout: int) -> dict:
    """Phase 0 主流程: 按模块提取基准 → 合并 → 写入 baselines/

    Raises:
        RuntimeError: 如果所有模块都提取失败（避免静默落盘空 baseline）
    """
    baselines_dir = Path(output_dir) / "baselines"
    baselines_dir.mkdir(parents=True, exist_ok=True)

    module_baselines = []
    failures = []
    candidates = [m for m in matched_modules if m.get("ref_cases")]
    print(f"[phase0] Extracting baselines for {len(candidates)} modules with reference cases", flush=True)

    for module in candidates:
        safe_name = module["name"].replace('/', '_').replace(' ', '_')
        out = baselines_dir / f"module-{safe_name}.json"
        try:
            print(f"[phase0] -> {module['name']}", flush=True)
            b = extract_baselines_for_module(
                module, str(out),
                prompt_dir=prompt_dir, model=model, timeout=timeout
            )
            module_baselines.append(b)
        except Exception as e:
            print(f"[phase0] WARN: {module['name']} baseline extraction failed: {e}", flush=True)
            failures.append((module['name'], str(e)))

    if not module_baselines:
        raise RuntimeError(
            f"Phase 0 failed: all {len(candidates)} module extractions failed. "
            f"First failure: {failures[0] if failures else 'unknown'}"
        )

    merged = merge_baselines(module_baselines)

    # 写分阶段文件
    for phase in ["phase1", "phase2", "phase3"]:
        path = baselines_dir / f"{phase}-baseline.json"
        path.write_text(
            json.dumps(merged[phase], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    print(f"[phase0] Done: {len(module_baselines)}/{len(candidates)} modules extracted "
          f"({len(failures)} failures)", flush=True)
    return merged
