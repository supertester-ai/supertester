from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent  # scripts/auto-iterate/
TESTING_AGENT_ROOT = PROJECT_ROOT.parent.parent  # TestingAgent/


@dataclass
class Config:
    # 输入路径
    prd_path: str = "E:/workspace/aise/geo-sass-re/requirements/VisiGEO-PRD.md"
    reference_path: str = "E:/workspace/aise/data/GEO_LV_2026.01_cases0326.json"
    skill_dir: str = str(TESTING_AGENT_ROOT / "skills")
    agent_dir: str = str(TESTING_AGENT_ROOT / "agents")
    output_dir: str = str(PROJECT_ROOT / "output")
    prompt_dir: str = str(PROJECT_ROOT / "prompts")

    # Claude CLI
    model: str = "sonnet"
    timeout: int = 1800  # 30 min — Phase 1/3 生成大型产物需要多轮推理
    max_patch_revise_attempts: int = 2

    # 收敛标准
    convergence: dict = field(default_factory=lambda: {
        "phase1": {"min_total_score": 0.80, "min_dimension_score": 0.60, "max_iterations": 4},
        "phase2": {"min_total_score": 0.75, "min_dimension_score": 0.55, "max_iterations": 4},
        "phase3": {"min_total_score": 0.85, "min_dimension_score": 0.65, "max_iterations": 5},
    })

    # 抽象映射表
    abstraction_map: dict = field(default_factory=lambda: {
        "loading阶段文案未逐项验证": "process_feedback — 阶段性进度反馈需逐阶段验证",
        "运营模式未覆盖": "business_outside_prd — PRD外运营策略需主动澄清",
        "Logo/图片未测": "visual_asset — 视觉资产需标记为 manual/partial",
        "prompt模板未逐字段校验": "contract_content — 内容模板需作为合约逐项验证",
        "处理中刷新未测": "interruption_recovery — 处理中状态需测试中断恢复",
        "列表排序未测": "history_interaction — 列表需覆盖排序/分页/滚动/空状态",
    })
