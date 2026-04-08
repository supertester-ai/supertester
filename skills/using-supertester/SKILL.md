---
name: using-supertester
description: Use when starting any testing workflow conversation - initializes .supertester/ session, routes to appropriate skill based on user intent
---

# Supertester - AI 驱动的软件测试工作流

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

## 核心原则

1. **需求优先** — 不理解需求，不准生成任何测试
2. **文件即记忆** — 所有信息写入 `.supertester/` 文件，不依赖上下文窗口
3. **两阶段生成** — 先人工用例，确认后再自动化脚本
4. **独立审查** — test-reviewer agent 审查，不自证清白
5. **人工门禁** — 关键节点必须用户确认

## 初始化

检查 `.supertester/` 目录：

**不存在：**
1. 创建 `.supertester/` 及子目录 (requirements/, test-cases/, scripts/, reviews/, reports/)
2. 从 templates/ 复制 test_plan.md, findings.md, progress.md
3. 在 test_plan.md 的 Goal 中填写用户的测试目标
4. 更新 progress.md 的日期

**已存在：**
1. 读取 test_plan.md 确定当前阶段
2. 提示用户："检测到未完成的测试任务，当前在 Phase X。继续？"
3. 用户确认后从断点恢复

## 意图路由

| 用户意图 | 触发 Skill | 示例 |
|---------|-----------|------|
| 解析需求文档 | requirement-analysis | "分析 requirements/auth-prd.md" |
| 继续澄清 | requirement-analysis（恢复） | "继续澄清"、"恢复 CL-002" |
| 分析模块关联 | requirement-association | "分析模块依赖" |
| 生成功能用例 | test-case-generation | "生成登录模块的测试用例" |
| 分析自动化可行性 | automation-analysis | "分析哪些可以自动化" |
| 生成自动化脚本 | automation-scripting | "生成 Playwright 脚本" |
| 生成报告 | test-reporting | "生成测试报告" |
| 查询/问答 | 直接回答 | "checkout 模块需要哪些测试？" |

## Skill 索引

| # | Skill | 前置条件 | 输出 |
|---|-------|---------|------|
| 0 | using-supertester | — | 初始化 .supertester/ |
| 1 | requirement-analysis | 需求文档 | parsed-requirements.md, clarifications.json |
| 2 | requirement-association | Phase 1 complete | module-dependencies.md, implicit-requirements.md, cross-module-scenarios.md |
| 3 | test-case-generation | Phase 2 complete + 用户确认 | functional-cases.md, deduplication-report.md |
| 4 | automation-analysis | Phase 3 complete + 用户确认 | automation-analysis.md |
| 5 | automation-scripting | Phase 4 complete | *.spec.ts, manual-cases.md |
| 6 | test-reporting | Phase 5 complete | reports/YYYY-MM-DD-*.md |

## 文件持久化规则

### 3 核心文件

- **test_plan.md** — 阶段追踪 + 决策 + 错误记录。每次阶段变更、重大决策、错误发生时更新。
- **findings.md** — 分析发现 + 知识库。遵守 2-Action Rule。
- **progress.md** — 会话日志 + 时间线。每完成操作后更新。

### 2-Action Rule

> 每执行 2 个分析/搜索/浏览操作后，**必须**立即更新 findings.md。

### 3-Strike Error Protocol

```
ATTEMPT 1: 诊断 & 修复
ATTEMPT 2: 换方法
ATTEMPT 3: 更广泛地反思
3 次失败后: 升级到用户
```

## Red Flags

| 如果你在想... | 现实是... |
|--------------|------------|
| "不需要初始化 .supertester/" | 文件即记忆。没有文件就没有持久化。 |
| "跳过某个阶段" | 每个阶段都有 Hard Gate，不能跳过。 |
| "先做再说" | 先理解需求。Iron Law 不可违反。 |
| "上下文够用不需要写文件" | 上下文会丢失。文件不会。 |
| "用户催得急" | 返工成本远高于流程成本。 |

## 完整流程

```
需求文档 → [Skill 1] 解析+澄清 → [Skill 2] 关联分析 → 审查 → 用户确认
    → [Skill 3] 用例生成 → 审查 → 用户确认
    → [Skill 4] 自动化分析 → [Skill 5] 脚本生成 → 审查
    → [Skill 6] 报告生成
```
