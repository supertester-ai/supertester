"""主编排器: Phase 0 → Phase 1 迭代 → Phase 2 迭代 → Phase 3 按模块迭代 → 最终报告"""
import argparse
import json
import sys
from pathlib import Path

from config import Config
from state import load_or_init, State
from splitter import split_prd, split_reference, match_modules
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
        prompt_dir=config.prompt_dir, model=config.model,
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
        prompt_dir=config.prompt_dir, model=config.model,
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
        prompt_dir=config.prompt_dir, model=config.model,
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
        prompt_dir=config.prompt_dir, model=config.model,
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
               associations: str, only_module: str = None):
    log(f"Phase 3 start: {len(matched_modules)} modules")

    for module in matched_modules:
        name = module["name"]
        if only_module and name != only_module:
            continue
        if name in state.converged_modules:
            log(f"Module '{name}' already converged, skipping")
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
            prompt_dir=config.prompt_dir, model=config.model,
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
            prompt_dir=config.prompt_dir, model=config.model,
            timeout=config.timeout,
        )
        state.history[name] = result["history"]
        if result["converged"]:
            state.converged_modules.append(name)
        else:
            state.unconverged_modules.append({
                "module": name,
                "best_score": max((h.get("score", 0) for h in result["history"]), default=0),
                "gap_dimensions": result.get("weak_dimensions", []),
            })
        state.save()
        log(f"Module '{name}' end: converged={result['converged']}")


def main():
    parser = argparse.ArgumentParser(description="Supertester Skill 自动迭代优化")
    parser.add_argument("--phase", type=int, choices=[0, 1, 2, 3],
                        help="只跑指定阶段 (0=baseline提取)")
    parser.add_argument("--module", type=str,
                        help="只跑指定模块 (仅对 Phase 3 有效)")
    parser.add_argument("--status", action="store_true",
                        help="查看当前进度然后退出")
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
        return 0

    Path(config.output_dir).mkdir(parents=True, exist_ok=True)

    prd_modules = split_prd(config.prd_path)
    ref_groups = split_reference(config.reference_path)
    matched = match_modules(prd_modules, ref_groups)
    log(f"Split: {len(prd_modules)} PRD modules, {len(ref_groups)} ref groups, "
        f"{sum(1 for m in matched if m.get('ref_cases'))} matched")

    baselines_path = Path(config.output_dir) / "baselines"
    if not state.phase0_complete or not baselines_path.exists():
        baselines = run_phase0(
            matched, config.output_dir,
            config.prompt_dir, config.model, config.timeout,
        )
        state.phase0_complete = True
        state.save()
    else:
        baselines = {
            phase: json.loads((baselines_path / f"{phase}-baseline.json").read_text(encoding='utf-8'))
            for phase in ["phase1", "phase2", "phase3"]
        }
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
        run_phase3(config, state, baselines, matched,
                   parsed_requirements, associations, only_module=args.module)

    report_path = f"{config.output_dir}/final-report.md"
    generate_report(state, report_path)
    log(f"Report generated: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
