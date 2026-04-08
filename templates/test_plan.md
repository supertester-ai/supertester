# Test Plan: [目标描述]

## Goal
[一句话描述最终测试目标]

## Current Phase
Phase 1

## Phases

### Phase 1: 需求解析与澄清
- [ ] 解析需求文档，提取模块/功能/验收标准/边界条件
- [ ] 检测模糊项并发起澄清对话
- [ ] 生成 parsed-requirements.md
- [ ] 更新 findings.md
- **Status:** pending

### Phase 2: 需求关联分析
- [ ] 分析模块间依赖关系
- [ ] 挖掘隐含需求
- [ ] 生成跨模块测试场景
- [ ] test-reviewer 审查
- [ ] 用户确认
- **Status:** pending

### Phase 3: 功能测试用例生成
- [ ] 分析需求特征，选择合适的子生成器
- [ ] 生成功能测试用例
- [ ] 去重
- [ ] test-reviewer 审查
- [ ] 用户确认
- **Status:** pending

### Phase 4: 自动化可行性分析
- [ ] 分析每个测试用例的自动化潜力
- [ ] 标记为 automatable / partial / manual
- [ ] 生成 automation-analysis.md
- **Status:** pending

### Phase 5: 自动化脚本生成
- [ ] 为 automatable 用例生成完整 Playwright 代码
- [ ] 为 partial 用例生成部分代码 + HUMAN VERIFICATION 标记
- [ ] 为 manual 用例生成 manual-cases.md
- [ ] test-reviewer 审查
- **Status:** pending

### Phase 6: 测试报告
- [ ] 生成需求覆盖矩阵
- [ ] 生成自动化统计
- [ ] 生成完整追溯链报告
- **Status:** pending

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
