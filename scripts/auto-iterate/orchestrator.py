"""主编排器: Phase 0 → Phase 1 迭代 → Phase 2 迭代 → Phase 3 按模块迭代 → 最终报告"""
import argparse
import json
import sys
from pathlib import Path

from config import Config
from state import load_or_init, State
from splitter import discover_modules
from phase0 import run_phase0
from phase_loop import iterate
from generators import (
    make_phase1_generator, make_phase2_generator, make_phase3_generator,
)
from reporter import generate_report


def log(msg: str):
    print(f"[orchestrator] {msg}", flush=True)


def _safe(name: str) -> str:
    return name.replace('/', '_').replace(' ', '_')


def _upsert_unconverged_module(state: State, name: str, result: dict):
    entry = {
        "module": name,
        "best_score": max((h.get("score", 0) for h in result["history"]), default=0),
        "gap_dimensions": result.get("weak_dimensions", []),
    }
    state.unconverged_modules = [
        item for item in state.unconverged_modules
        if item.get("module") != name
    ]
    state.unconverged_modules.append(entry)


def run_phase1(config: Config, state: State, baselines: dict):
    """Phase 1 迭代: 需求解析"""
    if state.phase1_converged:
        log("Phase 1 already converged, skipping")
        return
    log("Phase 1 start")
    prd_content = Path(config.prd_path).read_text(encoding='utf-8')

    baseline_a = baselines["phase1"]

    gen = make_phase1_generator(
        prd_content=prd_content,
        skill_dir=config.skill_dir,
        output_root=f"{config.output_dir}/iterations/phase1",
        prompt_dir=config.prompt_dir, model=config.models["generate"],
        timeout=config.timeout,
    )
    result = iterate(
        phase="phase1", module_name="_global",
        generator=gen, baseline_a=baseline_a,
        convergence=config.convergence["phase1"],
        skill_dir=config.skill_dir,
        snapshot_root=f"{config.output_dir}/skill-snapshots/phase1",
        iter_root=f"{config.output_dir}/iterations/phase1",
        abstraction_map=config.abstraction_map,
        skill_files=["skills/requirement-analysis/SKILL.md",
                     "skills/requirement-analysis/clarification-patterns.md"],
        max_revise_attempts=config.max_patch_revise_attempts,
        prompt_dir=config.prompt_dir, models=config.models,
        timeout=config.timeout,
    )
    state.phase1_converged = result["converged"]
    state.phase1_iterations = result["iterations"]
    state.phase1_final_score = result["final_score"]
    state.history["phase1"] = result["history"]
    state.save()
    log(f"Phase 1 end: converged={result['converged']} iterations={result['iterations']}")


def redo_phase1_final(config: Config) -> str:
    """Phase 1 收敛后用最终版 skill 重新生成定稿产物"""
    prd_content = Path(config.prd_path).read_text(encoding='utf-8')
    gen = make_phase1_generator(
        prd_content=prd_content, skill_dir=config.skill_dir,
        output_root=f"{config.output_dir}/final-artifacts",
        prompt_dir=config.prompt_dir, model=config.model,
        timeout=config.timeout,
    )
    output = gen(iter_num=0)
    final_path = Path(config.output_dir) / "final-artifacts" / "parsed-requirements.md"
    final_path.parent.mkdir(parents=True, exist_ok=True)
    final_path.write_text(output, encoding='utf-8')
    return output


def run_phase2(config: Config, state: State, baselines: dict,
               parsed_requirements: str):
    if state.phase2_converged:
        log("Phase 2 already converged, skipping")
        return
    log("Phase 2 start")

    baseline_a = baselines["phase2"]
    gen = make_phase2_generator(
        parsed_requirements=parsed_requirements,
        skill_dir=config.skill_dir,
        output_root=f"{config.output_dir}/iterations/phase2",
        prompt_dir=config.prompt_dir, model=config.models["generate"],
        timeout=config.timeout,
    )
    result = iterate(
        phase="phase2", module_name="_global",
        generator=gen, baseline_a=baseline_a,
        convergence=config.convergence["phase2"],
        skill_dir=config.skill_dir,
        snapshot_root=f"{config.output_dir}/skill-snapshots/phase2",
        iter_root=f"{config.output_dir}/iterations/phase2",
        abstraction_map=config.abstraction_map,
        skill_files=["skills/requirement-association/SKILL.md"],
        max_revise_attempts=config.max_patch_revise_attempts,
        prompt_dir=config.prompt_dir, models=config.models,
        timeout=config.timeout,
    )
    state.phase2_converged = result["converged"]
    state.phase2_iterations = result["iterations"]
    state.phase2_final_score = result["final_score"]
    state.history["phase2"] = result["history"]
    state.save()
    log(f"Phase 2 end: converged={result['converged']} iterations={result['iterations']}")


def redo_phase2_final(config: Config, parsed_requirements: str) -> str:
    gen = make_phase2_generator(
        parsed_requirements=parsed_requirements,
        skill_dir=config.skill_dir,
        output_root=f"{config.output_dir}/final-artifacts",
        prompt_dir=config.prompt_dir, model=config.model,
        timeout=config.timeout,
    )
    output = gen(iter_num=0)
    final_path = Path(config.output_dir) / "final-artifacts" / "associations.md"
    final_path.parent.mkdir(parents=True, exist_ok=True)
    final_path.write_text(output, encoding='utf-8')
    return output


def run_phase3(config: Config, state: State, baselines: dict,
               matched_modules: list, parsed_requirements: str,
               associations: str, only_modules: list = None,
               force_modules: list = None):
    log(f"Phase 3 start: {len(matched_modules)} modules")
    if force_modules is None:
        force_modules = []

    # Clear state for force-rerun modules
    for fm in force_modules:
        state.converged_modules = [m for m in state.converged_modules if m != fm]
        state.completed_modules = [m for m in state.completed_modules if m != fm]
        state.unconverged_modules = [u for u in state.unconverged_modules if u.get("module") != fm]
    if force_modules:
        state.save()

    for module in matched_modules:
        name = module["name"]
        if only_modules and name not in only_modules:
            continue
        if name in state.converged_modules and name not in force_modules:
            log(f"Module '{name}' already converged, skipping")
            continue
        if name in state.completed_modules and name not in force_modules:
            log(f"Module '{name}' already evaluated (not converged), skipping (use --force-module to re-run)")
            continue
        if not module.get("ref_cases"):
            log(f"Module '{name}' has no reference cases, skipping")
            continue

        state.current_module = name
        state.save()
        log(f"Module '{name}' start")

        baseline_a = baselines["phase3"].get(name, {})
        gen = make_phase3_generator(
            module_name=name,
            module_prd=module.get("prd_content") or "",
            parsed_requirements=parsed_requirements,
            associations=associations,
            skill_dir=config.skill_dir,
            output_root=f"{config.output_dir}/iterations/phase3/{_safe(name)}",
            prompt_dir=config.prompt_dir, model=config.models["generate"],
            timeout=config.timeout,
        )
        result = iterate(
            phase="phase3", module_name=name,
            generator=gen, baseline_a=baseline_a,
            convergence=config.convergence["phase3"],
            skill_dir=config.skill_dir,
            snapshot_root=f"{config.output_dir}/skill-snapshots/phase3/{_safe(name)}",
            iter_root=f"{config.output_dir}/iterations/phase3/{_safe(name)}",
            abstraction_map=config.abstraction_map,
            skill_files=["skills/test-case-generation/SKILL.md",
                         "skills/test-case-generation/generator-reference.md"],
            max_revise_attempts=config.max_patch_revise_attempts,
            prompt_dir=config.prompt_dir, models=config.models,
            timeout=config.timeout,
        )
        state.history[name] = result["history"]
        if result["converged"]:
            state.unconverged_modules = [
                item for item in state.unconverged_modules
                if item.get("module") != name
            ]
            if name not in state.converged_modules:
                state.converged_modules.append(name)
        else:
            _upsert_unconverged_module(state, name, result)
        if name not in state.completed_modules:
            state.completed_modules.append(name)
        state.save()
        log(f"Module '{name}' end: converged={result['converged']}")


def main():
    parser = argparse.ArgumentParser(description="Supertester Skill 自动迭代优化")
    parser.add_argument("--phase", type=int, choices=[0, 1, 2, 3],
                        help="只跑指定阶段 (0=baseline提取)")
    parser.add_argument("--module", type=str, action="append",
                        help="只跑指定模块，可多次使用 (仅对 Phase 3 有效)")
    parser.add_argument("--force-module", type=str, action="append",
                        help="强制重跑指定模块（即使已评测过）")
    parser.add_argument("--list-modules", action="store_true",
                        help="列出所有模块及其状态然后退出")
    parser.add_argument("--status", action="store_true",
                        help="查看当前进度然后退出")
    parser.add_argument("--force-phase0", action="store_true",
                        help="忽略已有 baselines，强制重跑 Phase 0")
    parser.add_argument("--force-discover", action="store_true",
                        help="忽略已有 module-map 缓存，强制重新发现模块")
    args = parser.parse_args()

    config = Config()
    state_file = f"{config.output_dir}/iteration-state.json"
    state = load_or_init(state_file)

    if args.status:
        log(f"Phase 0 complete: {state.phase0_complete}")
        log(f"Phase 1 converged: {state.phase1_converged} ({state.phase1_iterations} iters)")
        log(f"Phase 2 converged: {state.phase2_converged} ({state.phase2_iterations} iters)")
        log(f"Converged modules ({len(state.converged_modules)}): {state.converged_modules}")
        log(f"Unconverged modules: {[u['module'] for u in state.unconverged_modules]}")
        evaluated_not_converged = [m for m in state.completed_modules
                                   if m not in state.converged_modules]
        log(f"Evaluated but not converged: {evaluated_not_converged}")
        return 0

    Path(config.output_dir).mkdir(parents=True, exist_ok=True)

    # AI-driven module discovery (cached unless --force-discover)
    matched = discover_modules(
        prd_path=config.prd_path,
        ref_path=config.reference_path,
        output_dir=config.output_dir,
        prompt_dir=config.prompt_dir,
        model=config.models.get("discover", config.model),
        timeout=config.timeout,
        force=args.force_discover,
    )
    log(f"Modules: {len(matched)} total, "
        f"{sum(1 for m in matched if m.get('ref_cases'))} with ref cases")

    if args.list_modules:
        for m in matched:
            name = m["name"]
            has_ref = bool(m.get("ref_cases"))
            if not has_ref:
                status = "no-ref"
            elif name in state.converged_modules:
                status = "converged"
            elif name in state.completed_modules:
                best = next((u["best_score"] for u in state.unconverged_modules
                             if u.get("module") == name), "?")
                status = f"evaluated (best={best})"
            else:
                status = "pending"
            log(f"  {name}: {status}")
        return 0

    baselines_path = Path(config.output_dir) / "baselines"

    def _load_baselines() -> dict | None:
        """加载磁盘上的 baseline，若内容空（all empty）返回 None"""
        if not baselines_path.exists():
            return None
        try:
            loaded = {
                phase: json.loads((baselines_path / f"{phase}-baseline.json").read_text(encoding='utf-8'))
                for phase in ["phase1", "phase2", "phase3"]
            }
        except (FileNotFoundError, json.JSONDecodeError) as e:
            log(f"Baseline files unreadable: {e}")
            return None
        # 全空检测：三个 phase 全是 {} → 视为无效 baseline
        if not any(loaded[p] for p in ["phase1", "phase2", "phase3"]):
            log("Existing baselines are empty — will rerun Phase 0")
            return None
        return loaded

    force = args.force_phase0 or (args.phase == 0)
    cached = None if force else _load_baselines()

    if cached is None:
        log("Running Phase 0 baseline extraction")
        baselines = run_phase0(
            matched, config.output_dir,
            config.prompt_dir, config.models["baseline"], config.timeout,
        )
        state.phase0_complete = True
        state.save()
    else:
        baselines = cached
        state.phase0_complete = True
        log("Phase 0 baselines loaded from disk")

    if args.phase == 0:
        return 0

    # Phase 1
    if args.phase is None or args.phase == 1:
        run_phase1(config, state, baselines)

    # 用最终 Phase 1 skill 重新生成定稿
    final_phase1_path = Path(config.output_dir) / "final-artifacts" / "parsed-requirements.md"
    if state.phase1_converged and not final_phase1_path.exists():
        log("Redo Phase 1 with final skill")
        redo_phase1_final(config)
    parsed_requirements = final_phase1_path.read_text(encoding='utf-8') if final_phase1_path.exists() else ""

    # Phase 2
    if args.phase is None or args.phase == 2:
        run_phase2(config, state, baselines, parsed_requirements)

    final_phase2_path = Path(config.output_dir) / "final-artifacts" / "associations.md"
    if state.phase2_converged and not final_phase2_path.exists():
        log("Redo Phase 2 with final skill")
        redo_phase2_final(config, parsed_requirements)
    associations = final_phase2_path.read_text(encoding='utf-8') if final_phase2_path.exists() else ""

    # Phase 3
    if args.phase is None or args.phase == 3:
        force_mods = args.force_module or []
        # --force-module implies --module selection
        only_mods = args.module or []
        if force_mods:
            only_mods = list(set(only_mods + force_mods))
        run_phase3(config, state, baselines, matched,
                   parsed_requirements, associations,
                   only_modules=only_mods or None,
                   force_modules=force_mods)

    report_path = f"{config.output_dir}/final-report.md"
    generate_report(state, report_path)
    log(f"Report generated: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
