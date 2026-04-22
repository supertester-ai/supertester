import json
from pathlib import Path
from jinja2 import Template
from claude_runner import claude_call

# 单模块参考用例 JSON 的最大字符数，超出则截断
_MAX_CASES_CHARS = 40_000


def _truncate_cases(cases: list, max_chars: int = _MAX_CASES_CHARS) -> list:
    """对参考用例列表做渐进式截断，保证序列化后不超过 max_chars。"""
    full = json.dumps(cases, ensure_ascii=False)
    if len(full) <= max_chars:
        return cases
    # 逐条移除末尾用例直到符合限制
    truncated = list(cases)
    while truncated and len(json.dumps(truncated, ensure_ascii=False)) > max_chars:
        truncated.pop()
    return truncated


def extract_baselines_for_module(module: dict, output_path: str,
                                  prompt_dir: str = None,
                                  model: str = "sonnet",
                                  timeout: int = 300) -> dict:
    """对单个模块调用 Claude 提取三阶段基准"""
    if prompt_dir is None:
        prompt_dir = str(Path(__file__).parent / "prompts")

    template_text = Path(f"{prompt_dir}/extract-baseline.md").read_text(encoding='utf-8')
    tmpl = Template(template_text)

    raw_cases = module.get("ref_cases") or []
    cases = _truncate_cases(raw_cases)
    if len(cases) < len(raw_cases):
        print(f"[phase0]   truncated {len(raw_cases)} -> {len(cases)} cases "
              f"(>{_MAX_CASES_CHARS // 1000}K chars)", flush=True)

    prompt = tmpl.render(
        module_name=module["name"],
        reference_cases_json=json.dumps(cases, ensure_ascii=False, indent=2),
        prd_slice=module.get("prd_content") or "",
    )

    result = claude_call(prompt, output_path, parse_json=True, model=model, timeout=timeout)
    if result is None:
        raise RuntimeError(f"Failed to parse baseline JSON for module {module['name']}")
    # 确保 module_name 存在（Claude 有时会省略）
    if "module_name" not in result:
        result["module_name"] = module["name"]
    # 始终回写干净 JSON（claude_call 写的是原始响应，可能带 code fence）
    Path(output_path).write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8'
    )
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
               prompt_dir: str, model: str, timeout: int,
               max_retries: int = 2) -> dict:
    """Phase 0 主流程: 按模块提取基准 → 合并 → 写入 baselines/

    Args:
        max_retries: 单模块提取失败后的最大重试次数

    Raises:
        RuntimeError: 如果所有模块都提取失败（避免静默落盘空 baseline）
    """
    baselines_dir = Path(output_dir) / "baselines"
    baselines_dir.mkdir(parents=True, exist_ok=True)

    module_baselines = []
    failures = []
    reused = 0
    candidates = [m for m in matched_modules if m.get("ref_cases")]
    print(f"[phase0] Extracting baselines for {len(candidates)} modules with reference cases", flush=True)

    for module in candidates:
        safe_name = module["name"].replace('/', '_').replace(' ', '_')
        out = baselines_dir / f"module-{safe_name}.json"

        # 复用已成功落盘的模块基准，避免重复调用
        if out.exists():
            try:
                cached = json.loads(out.read_text(encoding='utf-8'))
                p1 = cached.get("phase1")
                is_new_format = (
                    isinstance(p1, dict)
                    and ("features" in p1 or "rules" in p1)
                )
                if is_new_format:
                    if not cached.get("module_name"):
                        cached["module_name"] = module["name"]
                        out.write_text(
                            json.dumps(cached, ensure_ascii=False, indent=2),
                            encoding='utf-8',
                        )
                    module_baselines.append(cached)
                    reused += 1
                    print(f"[phase0] -> {module['name']} (reused from disk)", flush=True)
                    continue
                elif p1 is not None:
                    print(f"[phase0] -> {module['name']} (old format, re-extracting)", flush=True)
            except (json.JSONDecodeError, KeyError):
                pass  # 文件损坏，重新提取

        # 提取（含重试）
        last_err = None
        for attempt in range(1, max_retries + 2):
            try:
                label = f" (retry {attempt - 1})" if attempt > 1 else ""
                print(f"[phase0] -> {module['name']}{label}", flush=True)
                b = extract_baselines_for_module(
                    module, str(out),
                    prompt_dir=prompt_dir, model=model, timeout=timeout
                )
                module_baselines.append(b)
                last_err = None
                break
            except Exception as e:
                last_err = e
                if attempt <= max_retries:
                    # 清理损坏的输出文件以防下次复用
                    if out.exists():
                        out.unlink()
                    print(f"[phase0]   attempt {attempt} failed: {e}", flush=True)

        if last_err is not None:
            print(f"[phase0] WARN: {module['name']} failed after {max_retries + 1} attempts: {last_err}", flush=True)
            failures.append((module['name'], str(last_err)))

    if not module_baselines:
        raise RuntimeError(
            f"Phase 0 failed: all {len(candidates)} module extractions failed. "
            f"First failure: {failures[0] if failures else 'unknown'}"
        )

    merged = merge_baselines(module_baselines)

    for phase in ["phase1", "phase2", "phase3"]:
        path = baselines_dir / f"{phase}-baseline.json"
        path.write_text(
            json.dumps(merged[phase], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    print(f"[phase0] Done: {len(module_baselines)}/{len(candidates)} modules "
          f"({reused} reused, {len(module_baselines) - reused} extracted, "
          f"{len(failures)} failures)", flush=True)
    return merged
