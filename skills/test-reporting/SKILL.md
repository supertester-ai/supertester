---
name: test-reporting
description: Use when generating the final test report - aggregates all phase outputs into a comprehensive report with traceability matrix
---

# Skill 6: 测试报告生成

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
2. **需求覆盖** — 每个 F-xxx 对应多少用例、覆盖状态
3. **功能测试用例摘要** — 按模块分组的用例列表
4. **自动化分析** — automatable/partial/manual 统计
5. **跨模块场景** — CMS-xxx 场景列表
6. **自动化脚本** — spec 文件列表及用例映射
7. **人工测试用例** — manual 用例列表
8. **追溯矩阵** — 需求 -> 用例 -> 脚本 的完整映射
9. **审查记录摘要** — test-reviewer 各阶段审查结果

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

## 输出位置

`.supertester/reports/YYYY-MM-DD-<module>.md`

如果涉及多个模块，可以：
- 生成一个汇总报告: `YYYY-MM-DD-summary.md`
- 每个模块一个详细报告: `YYYY-MM-DD-<module>.md`

## 步骤

1. 读取所有阶段输出文件
2. 汇总统计数据
3. 构建追溯矩阵（从 F-xxx 到 TC-xxx 到 *.spec.ts）
4. 按模板生成报告
5. 更新 test_plan.md Phase 6 -> complete
6. 更新 progress.md 完成日志
