"""评分模块: 对 AI 产物进行双基准打分"""

import json
from pathlib import Path
from jinja2 import Template
from claude_runner import claude_call
from dimensions import DIMENSIONS_BY_PHASE


def is_converged(score: dict, convergence_cfg: dict) -> bool:
    """检查评分是否满足收敛条件

    Args:
        score: 评分结果字典，包含 total_weighted_score 和 dimensions
        convergence_cfg: 收敛配置，包含 min_total_score 和 min_dimension_score

    Returns:
        True 如果满足收敛条件，False 否则
    """
    total = score.get("total_weighted_score", 0.0)
    if total < convergence_cfg["min_total_score"]:
        return False

    floor = convergence_cfg["min_dimension_score"]
    for dim in score.get("dimensions", {}).values():
        if dim.get("score", 0.0) < floor:
            return False

    return True


def score_artifact(
    phase: str,
    module_name: str,
    iteration: int,
    ai_output: str,
    baseline_a: dict,
    output_path: str,
    convergence: dict,
    prompt_dir: str = None,
    model: str = "sonnet",
    timeout: int = 300,
) -> dict:
    """对 AI 产物评分

    Args:
        phase: 评分阶段 (phase1/phase2/phase3)
        module_name: 模块名称
        iteration: 迭代次数
        ai_output: AI 产物内容
        baseline_a: 基准 A (人工参考用例)
        output_path: 输出路径
        convergence: 收敛配置
        prompt_dir: 提示词目录
        model: Claude 模型
        timeout: 超时时间

    Returns:
        评分结果字典

    Raises:
        RuntimeError: 如果 JSON 解析失败
    """
    if prompt_dir is None:
        prompt_dir = str(Path(__file__).parent / "prompts")

    # 加载提示词模板
    template = Template(
        Path(f"{prompt_dir}/score.md").read_text(encoding="utf-8")
    )

    # 获取该阶段的维度定义
    dimensions = DIMENSIONS_BY_PHASE[phase]

    # 渲染提示词
    prompt = template.render(
        phase=phase,
        module_name=module_name,
        iteration=iteration,
        ai_output=ai_output,
        baseline_a=json.dumps(baseline_a, ensure_ascii=False, indent=2),
        dimensions=json.dumps(dimensions, ensure_ascii=False, indent=2),
        min_total_score=convergence["min_total_score"],
        min_dimension_score=convergence["min_dimension_score"],
    )

    # 调用 Claude 进行评分
    result = claude_call(
        prompt,
        output_path,
        parse_json=True,
        model=model,
        timeout=timeout,
    )

    if result is None:
        raise RuntimeError(
            f"Failed to parse score JSON for {phase}/{module_name}"
        )

    return result
