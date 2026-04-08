# Supertester - AI 驱动的软件测试工作流插件

## 插件概述

Supertester 是一个 Superpowers 风格的纯 Markdown 技能插件，覆盖完整测试生命周期：
需求解析 -> 需求关联分析 -> 功能测试用例生成 -> 自动化可行性分析 -> Playwright 脚本生成 -> 测试报告。

## 核心原则

1. **需求优先** — 不理解需求，不准生成任何测试
2. **文件即记忆** — 所有重要信息写入 `.supertester/` 目录下的文件，不依赖上下文窗口
3. **两阶段测试生成** — 先生成人工可读用例，确认后再生成自动化脚本
4. **独立审查** — test-reviewer agent 独立审查，不自证清白
5. **人工介入门禁** — 关键节点必须用户确认后才能继续

## Skill 索引

| Skill | 用途 | 触发示例 |
|-------|------|---------|
| using-supertester | 入口路由 + 初始化 | 会话启动时自动注入 |
| requirement-analysis | 需求解析与澄清 | "分析 requirements/xxx.md" |
| requirement-association | 需求关联分析 | "分析模块依赖" |
| test-case-generation | 功能测试用例生成 | "生成测试用例" |
| automation-analysis | 自动化可行性分析 | "分析哪些可以自动化" |
| automation-scripting | Playwright 脚本生成 | "生成 Playwright 脚本" |
| test-reporting | 测试报告生成 | "生成测试报告" |

## 文件持久化

工作目录: `.supertester/`

核心文件:
- `test_plan.md` — 阶段追踪 + 决策记录 + 错误日志
- `findings.md` — 分析发现 + 知识库
- `progress.md` — 会话日志 + 操作时间线

## 行为控制

- **Iron Law**: 每个 Skill 的绝对禁令
- **Hard Gate**: 阻塞进入下一阶段的硬门禁
- **Red Flags**: Agent 自我说服的防御表
- **2-Action Rule**: 每 2 个操作后必须更新文件
- **3-Strike Protocol**: 3 次失败后升级到用户

## Agent

- `test-reviewer` — 独立审查 agent，在 Phase 2/3/5 审查产出物质量
