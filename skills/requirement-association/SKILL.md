---
name: requirement-association
description: Use when analyzing module dependencies and cross-module scenarios - discovers implicit requirements, generates cross-module test scenarios, requires user confirmation before proceeding
---

# Skill 2: 需求关联分析

## Iron Law

> **不分析关联，就不准生成用例。**
> 单模块测试无法覆盖模块间的交互问题。必须先完成关联分析。

<HARD-GATE>
在用户确认关联分析结果之前，不准进入 test-case-generation 阶段。
</HARD-GATE>

## 前置条件

- Phase 1 (requirement-analysis) Status: **complete**
- `.supertester/requirements/parsed-requirements.md` 已生成

## 流程

```
parsed-requirements.md
    |
    v
模块依赖分析 -> module-dependencies.md
    |  (显式依赖 + 隐式依赖 + 共享资源依赖)
    |
    v
隐含需求挖掘 -> implicit-requirements.md
    |  (前置条件隐含 + 后置结果隐含 + 数据一致性隐含
    |   + 边界情况隐含 + 异常传导隐含)
    |
    v
跨模块场景生成 -> cross-module-scenarios.md
    |  (关键路径 + 模块边界 + 错误传导 + 并发 + 数据同步)
    |
    v
-> test-reviewer agent 审查 -> reviews/review-association-*.md
    |
    v
-> 用户确认
    |
    v
更新 test_plan.md Phase 2 -> complete
```

## 步骤详解

### Step 1: 模块依赖分析

读取 parsed-requirements.md，分析：

1. **显式依赖** — 需求文档中明确提到的模块间依赖
2. **隐式依赖** — 通过数据流推断的依赖（A 的输出是 B 的输入）
3. **共享资源依赖** — 共享数据库表、缓存、配置的模块

输出到 `.supertester/requirements/module-dependencies.md`:

```markdown
# 模块依赖分析

## 依赖图

| 模块 | 类型 | 依赖 | 依赖类型 |
|------|------|------|---------|
| [模块名] | core/support | [依赖模块列表] | direct/workflow/shared_resource |

## 关键路径
1. [模块A] -> [模块B] -> [模块C] -> [模块D]
2. ...

## 共享资源
| 资源 | 共享模块 | 冲突风险 |
|------|---------|---------|
| [资源名] | [模块列表] | high/medium/low |
```

### Step 2: 隐含需求挖掘

从需求文本中挖掘未明确写出但逻辑上必须存在的需求：

1. **前置条件隐含** — "登录后显示仪表板" -> 未登录访问 /dashboard 应重定向
2. **后置结果隐含** — "下单成功" -> 库存应减少、订单状态应更新
3. **数据一致性隐含** — 修改用户名 -> 所有显示用户名的地方都应更新
4. **边界情况隐含** — "支持多个地址" -> 最大地址数？删除最后一个地址？
5. **异常传导隐含** — 支付服务超时 -> 订单应如何处理？

输出到 `.supertester/requirements/implicit-requirements.md`:

```markdown
# 隐含需求

| ID | 推断来源 | 隐含需求 | 类型 | 严重性 |
|----|---------|---------|------|--------|
| IR-001 | F-001: "登录后显示仪表板" | 未登录访问 /dashboard 应重定向到登录页 | security | high |
| IR-002 | F-005: "下单成功" | 支付失败时订单保持待支付状态 | error_handling | critical |
```

### Step 3: 跨模块场景生成

基于依赖图和隐含需求，生成跨模块测试场景：

场景类型：
- **critical_path** — 核心业务流程的端到端路径
- **module_boundary** — 两个模块交互的边界测试
- **error_propagation** — 一个模块错误如何影响下游模块
- **concurrent** — 多模块并发操作的冲突场景
- **data_sync** — 数据在多模块间的一致性验证

输出到 `.supertester/requirements/cross-module-scenarios.md`:

```markdown
# 跨模块测试场景

## CMS-001: [场景名称]

**场景类型:** critical_path | module_boundary | error_propagation | concurrent | data_sync
**涉及模块:** [模块列表]
**入口条件:** [前置条件]
**退出条件:** [成功标准]

| 步骤 | 模块 | 操作 | 预期结果 |
|------|------|------|---------|
| 1 | [模块] | [操作] | [结果] |

**溯源:** F-001, F-003, IR-001
```

### Step 4: test-reviewer 审查

生成完上述三个文件后，调用 test-reviewer agent 审查：
- 隐含需求是否合理
- 跨模块场景是否完整
- 是否遗漏关键依赖路径

审查结果保存到 `.supertester/reviews/review-association-<timestamp>.md`

### Step 5: 用户确认

向用户展示：
1. 模块依赖概要
2. 发现的隐含需求列表
3. 跨模块测试场景列表
4. 审查结果摘要

等待用户确认后，更新 test_plan.md Phase 2 -> complete。

## 2-Action Rule 落地

- 分析了 2 个模块的依赖 -> 立即写入 module-dependencies.md
- 挖掘了 2 个隐含需求 -> 立即写入 implicit-requirements.md
- 生成了 2 个跨模块场景 -> 立即写入 cross-module-scenarios.md

## Red Flags

| 如果你在想... | 现实是... |
|--------------|------------|
| "单模块够了" | 80% 的生产 bug 发生在模块交互边界 |
| "不需要跨模块测试" | 用户流程天然跨模块，不测就是盲区 |
| "关联分析太慢了" | 发现隐含需求比事后修 bug 便宜 100 倍 |
| "隐含需求太多了" | 按严重性排序，critical 必须覆盖 |
| "跳过审查直接给用户" | test-reviewer 必须先审查 |
