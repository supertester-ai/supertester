# Test Plan: [目标描述]

## Goal
[一句话描述最终测试目标]

## Coverage Goals
- **行为覆盖:** [核心流程 / 关键规则 / 异常处理 / 边界情况]
- **证据覆盖:** [UI / API / 状态数据 / 事件消息 / 文件 / 日志指标 / 外部系统]
- **关键测试资产保护:** [需要完整保留的规则、列表、内容、状态断言、契约]

## Current Phase
Phase 1

## Max Phase
<!-- 工作流终止阶段。本插件覆盖从需求到测试用例的 3 个 Phase，
     终点为 Phase 3（功能测试用例生成），不涉及自动化分析、脚本生成与测试报告。
     留空或不填表示执行全部 3 个 Phase。 -->
Phase 3

## Phases

### Phase 1: 需求解析与澄清
- [ ] 解析需求文档，提取模块/功能/验收标准/边界条件
- [ ] 抽取关键测试资产
- [ ] 标记主要证据类型
- [ ] 检测模糊项并发起澄清对话
- [ ] 生成 parsed-requirements.md
- [ ] 更新 findings.md
- **Completion Gate:** 功能项、关键测试资产、主要证据类型均已落盘
- **Status:** pending

### Phase 2: 需求关联分析
- [ ] 分析功能依赖
- [ ] 分析状态/数据依赖
- [ ] 分析证据依赖
- [ ] 分析共享资源风险
- [ ] 挖掘隐含需求
- [ ] 生成跨模块测试场景
- [ ] test-reviewer 审查
- [ ] 用户确认
- **Completion Gate:** 已覆盖功能链、状态链、证据链、共享资源风险
- **Status:** pending

### Phase 3: 功能测试用例生成
- [ ] 分析需求特征，选择合适的子生成器
- [ ] 根据证据维度选择验证方式
- [ ] 生成功能测试用例（输出 functional-cases.yaml，含 single / matrix / scenario_chain 三类）
- [ ] 字段矩阵聚合（同字段/同规则集 ≥3 条候选必须合并为 type: matrix）
- [ ] 去重
- [ ] 检查关键测试资产是否在生成或去重中丢失
- [ ] test-reviewer 审查（含矩阵聚合合理性 + verbatim 完整性）
- [ ] 用户确认
- **Completion Gate:** 行为覆盖与证据覆盖均可追踪，关键测试资产未丢失，无零散派生 single 群
- **Status:** pending

## Critical Test Assets
| Asset Type | Description | Source | Must Preserve |
|------------|-------------|--------|---------------|
|            |             |        | yes/no        |

## Evidence Map
| Feature | Evidence Types | Primary Source | Notes |
|---------|----------------|----------------|------|
|         |                |                |      |

## Decisions Made
| Decision | Rationale |
|----------|-----------|
|          |           |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |

## Notes
- 更新阶段状态: pending -> in_progress -> complete
- 每次重大决策前重新阅读此文件
- 记录所有错误，避免重复犯错
- 3 次失败后升级到用户
