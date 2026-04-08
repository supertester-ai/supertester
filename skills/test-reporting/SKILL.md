---
name: test-reporting
description: Use when generating the final test report - aggregates all phase outputs into a comprehensive report with traceability matrix
---

# Skill 6: 测试报告生成

## Iron Law

> **测试报告不是数量汇总，而是覆盖说明。**
> 如果报告只统计测试用例和自动化率，却不能说明覆盖维度、关键测试资产保留情况和剩余缺口，这份报告就是不完整的。

## 前置条件

- Phase 5 (automation-scripting) Status: **complete**

## 流程

```
全部阶段输出
    |
    v
汇总统计
    |
    v
覆盖维度分析 + 关键资产保留分析 + gap 分析
    |
    v
生成追溯矩阵
    |
    v
生成报告 -> reports/YYYY-MM-DD-<module>.md
    |
    v
更新 test_plan.md Phase 6 -> complete
```

## 报告内容

报告模板见 @report-template.md

### 必须包含的章节

1. **执行摘要** — 日期、需求文档、总用例数、自动化率
2. **需求覆盖** — 每个 F-xxx / IR-xxx / CMS-xxx 对应多少用例、覆盖状态
3. **覆盖维度摘要** — 行为、规则、内容、状态/数据、集成、证据链等维度的覆盖情况
4. **关键测试资产保留情况** — 哪些规则、列表、内容、状态断言、契约被明确保留
5. **功能测试用例摘要** — 按模块分组的用例列表
6. **自动化分析** — automatable/partial/manual 统计，以及为什么保留人工测试
7. **跨模块场景** — CMS-xxx 场景列表
8. **自动化脚本** — spec 文件列表及用例映射
9. **人工测试用例** — manual 用例列表
10. **Gap 分析** — 已覆盖、保留、遗漏、建议补强项
11. **追溯矩阵** — 需求 -> 用例 -> 脚本 的完整映射
12. **审查记录摘要** — test-reviewer 各阶段审查结果

## 追溯矩阵格式

```markdown
## Traceability Matrix

| Requirement | Test Cases | Script | Automation | Status |
|-------------|-----------|--------|------------|--------|
| F-001: Login | TC-001, TC-002, TC-003 | auth.e2e.spec.ts | automatable | covered |
| F-002: Logout | TC-010 | auth.e2e.spec.ts | automatable | covered |
| IR-001: Redirect | TC-005 | auth.e2e.spec.ts | automatable | covered |
| CMS-001: Full flow | TC-030 | checkout.e2e.spec.ts | partial | covered |
```

## 覆盖维度格式

```markdown
## Coverage Dimensions

| Dimension | Status | Evidence | Notes |
|-----------|--------|----------|-------|
| Behavior | covered | functional-cases.md | 核心流程与异常路径已覆盖 |
| Rules / Enumerations | partial | functional-cases.md | 仍有部分完整列表待补 |
| Content | covered | functional-cases.md, manual-cases.md | 关键内容已保留人工验证 |
| State / Data | covered | functional-cases.md | 状态断言已纳入核心用例 |
| Integration | partial | automation-analysis.md | 外部系统异常矩阵仍待补 |
| Evidence Chain | covered | cross-module-scenarios.md | 多观测面验证场景已建立 |
```

## Gap 分析格式

```markdown
## Gap Analysis

### Covered
- [已经有明确覆盖的能力或维度]

### Preserved Manual Coverage
- [保留人工测试的资产/原因]

### Missing or Partial
- [当前仍缺失或仅部分覆盖的项]

### Recommended Next Actions
1. [建议补强项]
2. [建议补强项]
```

## 输出位置

`.supertester/reports/YYYY-MM-DD-<module>.md`

如果涉及多个模块，可以：
- 生成一个汇总报告: `YYYY-MM-DD-summary.md`
- 每个模块一个详细报告: `YYYY-MM-DD-<module>.md`

## 步骤

1. 读取所有阶段输出文件
2. 汇总统计数据
3. 汇总覆盖维度与关键测试资产保留情况
4. 明确哪些能力已自动化，哪些被有意保留为人工验证
5. 构建追溯矩阵（从 F-xxx 到 TC-xxx 到 *.spec.ts）
6. 生成 gap 分析：已覆盖 / 保留 / 缺失 / 建议补强
7. 按模板生成报告
8. 更新 test_plan.md Phase 6 -> complete
9. 更新 progress.md 完成日志

## 报告生成规则

- 不要把报告退化成“数量统计”或“文件清单”
- 报告必须解释“为什么某些测试仍保留人工执行”
- 如果关键测试资产没有进入自动化，也必须在报告里明确说明是否已经被人工用例保留
- 如果某个维度只覆盖了行为、没有覆盖证据，应标记为 partial，而不是直接写 covered
- 对缺口的描述要具体到维度或资产类型，而不是笼统写“待补充”
