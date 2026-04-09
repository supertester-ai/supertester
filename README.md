# Supertester

面向 AI coding agent 的测试工作流插件，从需求分析一路推进到测试用例、自动化可行性判断、Playwright 脚本和最终测试报告。

当前仓库的实现形态是“插件 + skills + hooks + 模板”，不是传统的 `src/` 应用。README 已按现状重写，适合作为仓库首页和接入说明。

## 它能做什么

Supertester 把测试工作拆成一条可追踪的 6 阶段流程：

1. 需求解析与澄清
2. 需求关联与跨模块场景分析
3. 功能测试用例生成
4. 自动化可行性分析
5. Playwright 脚本生成
6. 测试报告生成

核心特点：

- 基于 `skills/` 提供阶段化能力，而不是单次大提示词
- 基于 `.supertester/` 做文件级持久化，支持中断恢复
- 基于 `hooks/` 在关键时机注入上下文，减少流程跑偏
- 引入独立 `test-reviewer` 进行阶段审查
- 支持把测试资产沉淀为 Markdown 和 Playwright 代码

## 当前仓库结构

```text
TestingAgent/
├─ .claude-plugin/              # Claude Code 插件元数据
├─ .opencode/                   # OpenCode 插件适配与安装说明
├─ agents/                      # 审查 agent 定义
├─ docs/                        # 设计文档
├─ hooks/                       # SessionStart / Stop 等 hooks
├─ scripts/                     # 初始化与恢复脚本
├─ skills/                      # 7 个核心 skills
├─ templates/                   # .supertester/ 工作文件模板
├─ CLAUDE.md
├─ AGENTS.md
├─ package.json
└─ README.md
```

`skills/` 下当前包含：

- `using-supertester`
- `requirement-analysis`
- `requirement-association`
- `test-case-generation`
- `automation-analysis`
- `automation-scripting`
- `test-reporting`

## 工作流输出

插件运行后，会在目标项目里维护 `.supertester/` 目录，用来保存上下文和阶段产物。典型结构如下：

```text
.supertester/
├─ test_plan.md
├─ findings.md
├─ progress.md
├─ requirements/
│  ├─ parsed-requirements.md
│  ├─ clarifications.json
│  ├─ module-dependencies.md
│  ├─ implicit-requirements.md
│  └─ cross-module-scenarios.md
├─ test-cases/
│  ├─ functional-cases.md
│  ├─ automation-analysis.md
│  └─ deduplication-report.md
├─ scripts/
│  ├─ *.spec.ts
│  └─ manual-cases.md
├─ reviews/
└─ reports/
```

这套结构的目标不是只“生成一些测试内容”，而是把测试分析过程、决策依据、自动化边界和最终产物都保留下来。

## 插件组成

### Skills

`skills/` 是主能力层：

- `using-supertester`：入口 skill，负责初始化和路由
- `requirement-analysis`：解析需求、识别歧义、组织澄清
- `requirement-association`：分析依赖、隐含需求、跨模块场景
- `test-case-generation`：生成功能测试用例并去重
- `automation-analysis`：将用例分类为 `automatable` / `partial` / `manual`
- `automation-scripting`：为可自动化部分生成 Playwright 脚本
- `test-reporting`：汇总阶段结果，输出测试报告

### Hooks

`hooks/hooks.json` 当前定义了 5 个 hook：

- `SessionStart`
- `UserPromptSubmit`
- `PreToolUse`
- `PostToolUse`
- `Stop`

它们分别用于初始化会话、注入当前阶段上下文、在编辑前后提醒同步进度，以及在结束前检查流程是否完整。

### Templates

`templates/` 提供 3 个基础模板：

- `test_plan.md`
- `findings.md`
- `progress.md`

### Scripts

`scripts/` 当前包含：

- `init-session.sh`
- `init-session.ps1`
- `session-catchup.py`

用于初始化 `.supertester/` 和恢复中断的工作会话。

## 安装方式

### 1. 在 Claude Code 中作为本地插件使用

仓库已经包含 Claude 插件元数据：

- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`

如果你是本地调试这个插件，通常会把仓库作为插件源接入 Claude Code，并确保插件目录中的 `skills/` 与 `hooks/` 可被加载。

### 2. 在 OpenCode 中使用

仓库已经提供 OpenCode 适配层，入口位于 [`.opencode/plugins/supertester.js`](E:/workspace/aise/TestingAgent/.opencode/plugins/supertester.js)。

可按 [`.opencode/INSTALL.md`](E:/workspace/aise/TestingAgent/.opencode/INSTALL.md) 的说明，在 `opencode.json` 中添加：

```json
{
  "plugin": ["supertester@git+https://gitcode.com/orion-c/supertester.git"]
}
```

重启 OpenCode 后，插件会注册 `skills/` 并自动注入 `using-supertester` 的引导内容。

### 3. 作为仓库直接复用

如果你只是想复用这套 skill 资产，也可以直接使用本仓库中的：

- `skills/`
- `hooks/`
- `templates/`
- `agents/test-reviewer.md`

这种方式适合二次开发或迁移到其它 agent 平台。

## 快速开始

在接入插件后，可以直接给 agent 发自然语言任务，例如：

```text
分析 requirements/auth-prd.md，并生成测试方案
```

或者从中间阶段开始：

```text
基于现有功能用例，继续做自动化可行性分析
```

典型执行过程会是：

1. 初始化 `.supertester/`
2. 解析需求并输出结构化结果
3. 发现模糊项时发起澄清
4. 生成功能测试用例并经过审查
5. 分析哪些用例适合自动化
6. 生成 Playwright 脚本与最终报告

## 设计原则

- 先理解需求，再生成测试资产
- 把信息写入文件，而不是依赖短期上下文
- 功能用例和自动化脚本分阶段生成
- 由独立审查角色把关，而不是“自己写自己验”
- 保留 manual/partial 场景，不强行全部自动化

这些原则的详细说明可以参考 [docs/design.md](E:/workspace/aise/TestingAgent/docs/design.md)。

## 适用场景

适合：

- 需求文档驱动的测试设计
- 想把测试分析过程沉淀成文件资产的团队
- Web 应用的 Playwright E2E 测试规划与脚本生成
- 需要跨会话恢复上下文的长流程测试任务

暂不等同于：

- 一个完整的测试执行平台
- 一个带 `src/` 业务逻辑的传统 Node 应用
- 所有场景都自动跑完的全托管测试系统

## 开发说明

当前 `package.json` 只声明了最小的插件信息：

- 包名：`supertester`
- 版本：`0.1.0`
- 模块类型：`module`
- OpenCode 入口：`.opencode/plugins/supertester.js`

这也说明仓库重点在插件装配与 skill 编排，而不是运行时服务代码。

## License

MIT
