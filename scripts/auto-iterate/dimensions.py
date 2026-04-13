"""各阶段评分维度定义"""

PHASE1_DIMENSIONS = {
    "module_feature_identification": {
        "weight": 0.20,
        "baseline": "A",
        "desc": "参考用例涉及的 module_path 在 parsed-requirements 中有对应 F-xxx",
    },
    "content_asset_extraction": {
        "weight": 0.15,
        "baseline": "A",
        "desc": "参考用例中出现的文案/提示语/模板在资产清单中被标记",
    },
    "enum_asset_completeness": {
        "weight": 0.15,
        "baseline": "A",
        "desc": "参考用例中的完整列表被完整保留而非截断",
    },
    "state_data_asset": {
        "weight": 0.10,
        "baseline": "A",
        "desc": "涉及 DB 断言/额度变化/状态流转被识别",
    },
    "evidence_type_tagging": {
        "weight": 0.10,
        "baseline": "A",
        "desc": "每个 F-xxx 标记了正确的证据类型",
    },
    "feature_tag_coverage": {
        "weight": 0.10,
        "baseline": "A",
        "desc": "6 类特性标签被正确标记",
    },
    "input_constraint_completeness": {
        "weight": 0.10,
        "baseline": "B",
        "desc": "每个输入字段识别了类型/范围/格式/必填约束",
    },
    "state_machine_identification": {
        "weight": 0.10,
        "baseline": "B",
        "desc": "涉及生命周期/流程的功能被标记为状态机类",
    },
}

PHASE2_DIMENSIONS = {
    "functional_dependency": {
        "weight": 0.15,
        "baseline": "A",
        "desc": "参考用例中隐含的跨模块依赖被识别",
    },
    "interruption_recovery": {
        "weight": 0.20,
        "baseline": "A+B",
        "desc": "刷新/切换/重试场景在关联分析中出现",
    },
    "history_list_interaction": {
        "weight": 0.15,
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
        "weight": 0.15,
        "baseline": "B",
        "desc": "模块 A 失败时对模块 B 的影响链被识别",
    },
    "concurrency_race": {
        "weight": 0.10,
        "baseline": "B",
        "desc": "共享资源的并发访问风险被识别",
    },
}

PHASE3_DIMENSIONS = {
    "step_coverage": {
        "weight": 0.20,
        "baseline": "A",
        "desc": "参考用例的每个 step 在 AI 用例中找到对应覆盖",
    },
    "content_fidelity": {
        "weight": 0.15,
        "baseline": "A",
        "desc": "需逐字段校验的地方写了具体内容",
    },
    "process_state": {
        "weight": 0.10,
        "baseline": "A+B",
        "desc": "loading/进度/中间状态被独立测试",
    },
    "interruption_recovery": {
        "weight": 0.10,
        "baseline": "A+B",
        "desc": "刷新/切换/退出等中断场景有对应用例",
    },
    "visual_asset_marking": {
        "weight": 0.05,
        "baseline": "A",
        "desc": "图片/Logo/样式类测试点标记为 manual/partial",
    },
    "contract_verification": {
        "weight": 0.10,
        "baseline": "A+B",
        "desc": "prompt/schema/模板作为合约逐项校验",
    },
    "equivalence_boundary": {
        "weight": 0.10,
        "baseline": "B",
        "desc": "输入类需求运用了等价类划分和边界值分析",
    },
    "exception_negative": {
        "weight": 0.10,
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
