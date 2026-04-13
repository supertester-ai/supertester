from pathlib import Path
from jinja2 import Template
from claude_runner import claude_call


def _render(prompt_dir: str, name: str, **kwargs) -> str:
    text = Path(f"{prompt_dir}/{name}").read_text(encoding='utf-8')
    return Template(text).render(**kwargs)


def make_phase1_generator(prd_content: str, skill_dir: str,
                          output_root: str, prompt_dir: str = None,
                          model: str = "sonnet", timeout: int = 300):
    """返回 (iter_num) -> ai_output"""
    if prompt_dir is None:
        prompt_dir = str(Path(__file__).parent / "prompts")

    def gen(iter_num: int) -> str:
        skill_content = Path(
            f"{skill_dir}/requirement-analysis/SKILL.md"
        ).read_text(encoding='utf-8')

        prompt = _render(
            prompt_dir, "generate-phase1.md",
            prd_content=prd_content, skill_content=skill_content,
        )
        output = Path(output_root) / f"iter-{iter_num}" / "parsed-requirements.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        return claude_call(prompt, str(output), model=model, timeout=timeout)

    return gen


def make_phase2_generator(parsed_requirements: str, skill_dir: str,
                          output_root: str, prompt_dir: str = None,
                          model: str = "sonnet", timeout: int = 300):
    if prompt_dir is None:
        prompt_dir = str(Path(__file__).parent / "prompts")

    def gen(iter_num: int) -> str:
        skill_content = Path(
            f"{skill_dir}/requirement-association/SKILL.md"
        ).read_text(encoding='utf-8')

        prompt = _render(
            prompt_dir, "generate-phase2.md",
            parsed_requirements=parsed_requirements,
            skill_content=skill_content,
        )
        output = Path(output_root) / f"iter-{iter_num}" / "associations.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        return claude_call(prompt, str(output), model=model, timeout=timeout)

    return gen


def make_phase3_generator(module_name: str, module_prd: str,
                          parsed_requirements: str, associations: str,
                          skill_dir: str, output_root: str,
                          prompt_dir: str = None, model: str = "sonnet",
                          timeout: int = 300):
    if prompt_dir is None:
        prompt_dir = str(Path(__file__).parent / "prompts")

    def gen(iter_num: int) -> str:
        skill_content = Path(
            f"{skill_dir}/test-case-generation/SKILL.md"
        ).read_text(encoding='utf-8')
        gen_ref_path = Path(f"{skill_dir}/test-case-generation/generator-reference.md")
        generator_reference = gen_ref_path.read_text(encoding='utf-8') if gen_ref_path.exists() else ""

        prompt = _render(
            prompt_dir, "generate-phase3.md",
            module_name=module_name, module_prd=module_prd,
            parsed_requirements=parsed_requirements,
            associations=associations,
            skill_content=skill_content,
            generator_reference=generator_reference,
        )
        safe_name = module_name.replace('/', '_').replace(' ', '_')
        output = Path(output_root) / f"iter-{iter_num}" / f"cases-{safe_name}.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        return claude_call(prompt, str(output), model=model, timeout=timeout)

    return gen
