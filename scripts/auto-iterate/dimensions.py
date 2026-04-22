"""各阶段评分维度定义"""

# Phase 1: 需求解析 — 只评"需求是否被正确理解"，不评测试设计
PHASE1_DIMENSIONS = {
    "module_completeness": {
        "weight": 0.30,
        "baseline": "A",
        "desc": "PRD 中的所有模块/功能是否被识别并分配 F-xxx",
    },
    "rule_extraction": {
        "weight": 0.25,
        "baseline": "A",
        "desc": "业务规则、约束条件、前置/后置条件是否被提取（规则模式级，不要求具体数值）",
    },
    "asset_awareness": {
        "weight": 0.20,
        "baseline": "A",
        "desc": "资产类别是否被正确识别（知道'有文案/枚举/状态数据'，不要求列出具体内容）",
    },
    "input_constraint_identification": {
        "weight": 0.10,
        "baseline": "B",
        "desc": "输入字段是否识别了类型/范围/格式等约束（规格级，不要求具体值）",
    },
    "clarification_quality": {
        "weight": 0.15,
        "baseline": "A+B",
        "desc": "澄清项是否有效：覆盖了 PRD 模糊地带，问题方向正确",
    },
}

# Phase 2: 关联分析 — 增加从 Phase 1 移入的 feature_tag_coverage 和 state_machine_identification
PHASE2_DIMENSIONS = {
    "functional_dependency": {
        "weight": 0.15,
        "baseline": "A",
        "desc": "参考用例中隐含的跨模块依赖被识别",
    },
    "interruption_recovery": {
        "weight": 0.15,
        "baseline": "A+B",
        "desc": "刷新/切换/重试场景在关联分析中出现",
    },
    "history_list_interaction": {
        "weight": 0.10,
        "baseline": "A+B",
        "desc": "排序/分页/空状态被识别为关联场景",
    },
    "implicit_requirements": {
        "weight": 0.15,
        "baseline": "A",
        "desc": "PRD 未明确写出但参考用例覆盖的需求被发现",
    },
    "prd_external_business": {
        "weight": 0.10,
        "baseline": "A",
        "desc": "运营逻辑被标记为待澄清项",
    },
    "error_propagation": {
        "weight": 0.10,
        "baseline": "B",
        "desc": "模块 A 失败时对模块 B 的影响链被识别",
    },
    "concurrency_race": {
        "weight": 0.05,
        "baseline": "B",
        "desc": "共享资源的并发访问风险被识别",
    },
    "feature_tag_coverage": {
        "weight": 0.10,
        "baseline": "A",
        "desc": "6 类特性标签被正确分配到各功能，用于指导测试策略路由",
    },
    "state_machine_identification": {
        "weight": 0.10,
        "baseline": "B",
        "desc": "涉及生命周期/流程的功能被识别为需要状态转换测试",
    },
}

# Phase 3: 用例生成 — 增加从 Phase 1 移入的 evidence_type_tagging、content/enum 细粒度
PHASE3_DIMENSIONS = {
    "step_coverage": {
        "weight": 0.15,
        "baseline": "A",
        "desc": "参考用例的每个 step 在 AI 用例中找到对应覆盖",
    },
    "content_fidelity": {
        "weight": 0.12,
        "baseline": "A",
        "desc": "需逐字段校验的地方写了具体文案内容（字符串级匹配）",
    },
    "enum_completeness": {
        "weight": 0.08,
        "baseline": "A",
        "desc": "枚举列表在测试数据中被完整覆盖而非截断",
    },
    "evidence_type_tagging": {
        "weight": 0.08,
        "baseline": "A",
        "desc": "每个测试用例标记了正确的证据验证方式",
    },
    "process_state": {
        "weight": 0.08,
        "baseline": "A+B",
        "desc": "loading/进度/中间状态被独立测试",
    },
    "interruption_recovery": {
        "weight": 0.08,
        "baseline": "A+B",
        "desc": "刷新/切换/退出等中断场景有对应用例",
    },
    "visual_asset_marking": {
        "weight": 0.05,
        "baseline": "A",
        "desc": "图片/Logo/样式类测试点标记为 manual/partial",
    },
    "contract_verification": {
        "weight": 0.08,
        "baseline": "A+B",
        "desc": "prompt/schema/模板作为合约逐项校验",
    },
    "equivalence_boundary": {
        "weight": 0.10,
        "baseline": "B",
        "desc": "输入类需求运用了等价类划分和边界值分析",
    },
    "exception_negative": {
        "weight": 0.08,
        "baseline": "B",
        "desc": "覆盖了错误处理/异常路径/权限越界",
    },
    "state_transition": {
        "weight": 0.05,
        "baseline": "B",
        "desc": "涉及状态机的模块覆盖了合法+非法转换",
    },
    "method_fit": {
        "weight": 0.05,
        "baseline": "B",
        "desc": "为需求特性选择了正确的生成器/设计方法",
    },
}

DIMENSIONS_BY_PHASE = {
    "phase1": PHASE1_DIMENSIONS,
    "phase2": PHASE2_DIMENSIONS,
    "phase3": PHASE3_DIMENSIONS,
}
