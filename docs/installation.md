# Supertester 安装指南

Supertester 是一个 AI 驱动的软件测试工作流插件，支持多种智能体工具。本文档详细说明如何在各平台安装和配置 Supertester。

## 平台概览

| 平台 | 安装方式 | 插件目录 | 技能目录 |
|------|---------|---------|---------|
| [OpenCode](#opencode-安装) | NPM 包插件 | `.opencode/plugins/` | `skills/` |
| [Claude Code](#claude-code-安装) | 插件市场 | `.claude-plugin/` | `skills/` |
| [Codex](#codex-安装) | 完整插件安装 | `.codex-plugin/` + `hooks.json` + `agents/` + `skills/` | Codex Plugins |
| [OpenClaw](#openclaw-安装) | 复制技能目录 | — | `.openclaw/skills/` |
| [Continue](#continue-安装) | 复制技能目录 | — | `.continue/skills/` |

---

## OpenCode 安装

### 前置要求

- [OpenCode.ai](https://opencode.ai) 已安装

### 安装步骤

在 `opencode.json`（全局或项目级别）的 `plugin` 数组中添加 Supertester：

```json
{
  "plugin": ["supertester@git+https://github.com/supertester-ai/supertester.git"]
}
```

或者使用本地路径进行开发：

```json
{
  "plugin": ["supertester@local:/path/to/TestingAgent"]
}
```

### 重启验证

重启 OpenCode，插件会自动安装并注册所有技能。

验证安装：
```
You: Tell me about supertester
```

### 可用技能

| 技能 | 用途 |
|-----|------|
| `supertester/using-supertester` | 入口 + 路由 |
| `supertester/requirement-analysis` | 需求解析 + 澄清 |
| `supertester/requirement-association` | 模块依赖 + 跨模块场景 |
| `supertester/test-case-generation` | 生成功能测试用例 |
| `supertester/automation-analysis` | 自动化可行性分析 |
| `supertester/automation-scripting` | Playwright E2E 脚本生成 |
| `supertester/test-reporting` | 测试报告生成 |

### 工具映射

当技能引用 Claude Code 工具时，OpenCode 等效工具：

- `TodoWrite` → `todowrite`
- `Task` 工具 + 子代理 → OpenCode 的 `@mention` 系统
- `Skill` 工具 → OpenCode 原生 `skill` 工具
- `Read`, `Write`, `Edit`, `Bash` → OpenCode 原生工具

### 更新

Supertester 在重启 OpenCode 时自动更新。

锁定特定版本：
```json
{
  "plugin": ["supertester@git+https://github.com/supertester-ai/supertester.git#v0.1.0"]
}
```

### 故障排除

**插件未加载**
1. 检查日志：`opencode run --print-logs "hello" 2>&1 | grep -i supertester`
2. 验证 `opencode.json` 中的 plugin 配置
3. 确保运行的是最新版本的 OpenCode

**技能未找到**
1. 使用 `skill` 工具列出已发现的技能
2. 检查插件是否已加载（见上一条）
3. 确保技能目录包含有效的 `SKILL.md` 文件

---

## Claude Code 安装

### 前置要求

- Claude Code CLI 已安装

### 安装方式

Claude Code 通过插件市场安装，或直接从 git 仓库安装。

**方式一：插件市场（推荐）**

```bash
claude plugin install supertester
```

**方式二：从 git 仓库安装**

```bash
claude plugin add https://github.com/supertester-ai/supertester.git
```

### 验证安装

```bash
claude plugin list
```

确认 supertester 插件在列表中。

### 手动配置

如果需要手动配置，创建 `~/.claude/settings.json`：

```json
{
  "plugins": {
    "supertester": {
      "enabled": true,
      "skills": {
        "paths": ["/path/to/TestingAgent/skills"]
      }
    }
  }
}
```

### 技能加载

Supertester 的 `using-supertester` 技能会在会话启动时自动加载。

### 故障排除

**插件未显示**
```bash
claude plugin update
claude plugin list
```

**技能路径问题**
检查 `~/.claude/settings.json` 中的 `skills.paths` 配置是否包含 TestingAgent 的 skills 目录。

---

## Codex 安装

### 前置要求

- OpenAI Codex 已安装
- Git
- Codex 插件能力已启用
- Bash 可用

### 为什么不能只装 skills

Supertester 在 Codex 下要完整工作，不仅需要 `skills/`，还需要：

- `agents/test-reviewer.md`
- 根目录 `hooks.json`
- `.codex-plugin/plugin.json`

仅做 skills 软链会导致：

- `test-reviewer` 不可用
- SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / Stop 自动化行为失效

### 安装步骤

**方式一：从 Git 仓库安装完整插件**

在 Codex Plugins UI 中安装：

```text
https://github.com/supertester-ai/supertester.git
```

**方式二：从本地路径安装完整插件**

先克隆仓库：

```bash
git clone https://github.com/supertester-ai/supertester.git ~/plugins/supertester
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/supertester-ai/supertester.git "$env:USERPROFILE\plugins\supertester"
```

然后在 Codex Plugins UI 中安装本地插件目录 `~/plugins/supertester`。

### 验证安装

安装成功后，Codex 应同时加载：

- `skills/`
- `agents/test-reviewer.md`
- 根目录 `hooks.json`

验证点：

1. 会话开始时自动注入 Supertester 上下文
2. Phase 2/3/5 可调用 `test-reviewer`
3. Stop 时会检查 `.supertester/test_plan.md` 的阶段完成情况

### 更新

如果使用本地克隆安装：

```bash
cd ~/plugins/supertester && git pull
```

更新后在 Codex 中刷新或重新安装插件。

### 卸载

在 Codex Plugins UI 中移除该插件。若使用本地克隆，可随后删除本地目录。

### 故障排除

**插件只加载了 skills，没有完整流程**
1. 你可能用了旧的 skills-only 安装方式
2. 重新按完整插件模式安装
3. 确认插件根目录包含 `.codex-plugin/plugin.json`、`hooks.json`、`agents/`

**Hooks 没有触发**
1. 检查插件根目录是否存在 `hooks.json`
2. 检查 Bash 是否可用
3. 重启 Codex

**找不到 `test-reviewer`**

这通常表示 Codex 只加载了技能目录，没有加载插件的 `agents/` 目录。重新安装完整插件。

---

## OpenClaw 安装

### 前置要求

- [OpenClaw](https://openclaw.ai) 已安装

### 安装方式

OpenClaw 支持三种技能位置（按优先级排序）：
1. **工作区技能**（最高优先级）：`<workspace>/.openclaw/skills/`
2. **本地/托管技能**：`~/.openclaw/skills/`
3. **捆绑技能**（最低优先级）：随安装附带的技能

### 方式一：工作区安装（推荐）

将技能复制到项目的工作区技能目录：

```bash
# 克隆仓库
git clone https://github.com/supertester-ai/supertester.git

# 复制 OpenClaw 技能到工作区
cp -r supertester/.openclaw/skills/supertester your-project/.openclaw/skills/

# 清理
rm -rf supertester
```

### 方式二：全局安装

安装到本地 OpenClaw 技能目录：

```bash
# 克隆仓库
git clone https://github.com/supertester-ai/supertester.git

# 复制到全局技能目录
mkdir -p ~/.openclaw/skills
cp -r supertester/.openclaw/skills/supertester ~/.openclaw/skills/

# 清理
rm -rf supertester
```

### 验证安装

```bash
# 检查 OpenClaw 状态和已加载的技能
openclaw status
```

### 配置（可选）

在 `~/.openclaw/openclaw.json` 中配置技能：

```json5
{
  skills: {
    entries: {
      "supertester": {
        enabled: true
      }
    }
  }
}
```

### 工作原理

OpenClaw 在会话启动时会快照符合条件的技能：
- 工作区技能优先于捆绑技能
- 技能在工作区中修改后需要重启会话

### 辅助脚本

初始化会话文件：
```bash
# macOS/Linux
bash .openclaw/skills/supertester/scripts/init-session.sh

# Windows
powershell -ExecutionPolicy Bypass -File .openclaw/skills/supertester/scripts/init-session.ps1
```

验证阶段完成：
```bash
bash .openclaw/skills/supertester/scripts/check-complete.sh
```

### 故障排除

**技能未加载**
1. 检查技能目录：`ls .openclaw/skills/`
2. 验证 SKILL.md 文件存在
3. 重启 OpenClaw 会话

---

## Continue 安装

### 前置要求

- [Continue](https://continue.dev) VS Code 或 JetBrains 扩展已安装

### 安装方式

Continue 支持项目级别（`<repo>/.continue/...`）和全局（`~/.continue/...`）位置。

### 方式一：项目级别安装（推荐）

在项目根目录：

```bash
git clone https://github.com/supertester-ai/supertester.git
cp -r supertester/.continue .continue
```

重启 Continue（重新加载 IDE）以加载新文件。

### 方式二：全局安装

复制技能和提示到全局 Continue 目录：

```bash
git clone https://github.com/supertester-ai/supertester.git
mkdir -p ~/.continue/skills ~/.continue/prompts
cp -r supertester/.continue/skills/supertester ~/.continue/skills/
cp supertester/.continue/prompts/supertester.prompt ~/.continue/prompts/
```

重启 Continue。

### 验证安装

在 Continue 聊天中运行：
```
/supertester
```

或询问：
```
You: What skills are available?
```

### 使用方法

1. 在 Continue 聊天中，运行：`/supertester`
2. 提示将引导您完成工作流程

### 辅助脚本（可选）

从项目根目录：

```bash
# 创建 task_plan.md / findings.md / progress.md（如果缺失）
bash .continue/skills/supertester/scripts/init-session.sh

# 验证所有阶段标记为完成
bash .continue/skills/supertester/scripts/check-complete.sh
```

### 注意事项

- Continue 不运行 Claude Code hooks（PreToolUse/PostToolUse/Stop）
- 工作流程是手动的：需要在决策前重新阅读 `task_plan.md`，在每个阶段后更新
- 三个规划文件是工具无关的，可以在 Claude Code、Cursor、Gemini CLI 和 Continue 之间通用

---

## 技能列表

所有平台可用的技能：

| 技能名称 | 触发条件 | 用途 |
|---------|---------|------|
| `using-supertester` | 会话启动自动加载 | 入口 skill，初始化工作流 |
| `requirement-analysis` | 分析需求文档 | 解析需求 + 澄清模糊项 |
| `requirement-association` | 分析模块依赖 | 模块依赖 + 跨模块场景 |
| `test-case-generation` | 生成测试用例 | 功能测试用例生成 |
| `automation-analysis` | 分析自动化可行性 | 分类为 automatable/partial/manual |
| `automation-scripting` | 生成自动化脚本 | Playwright E2E 脚本生成 |
| `test-reporting` | 生成报告 | 聚合所有阶段输出 |

---

## 工作流程

完整测试工作流：

```
需求文档
    │
    ▼
[Phase 1] requirement-analysis
    │  解析需求 → 澄清模糊项
    ▼
[Phase 2] requirement-association
    │  模块依赖 + 隐含需求 + 跨模块场景
    │  → test-reviewer 审查 → 用户确认
    ▼
[Phase 3] test-case-generation
    │  生成功能用例 → test-reviewer 审查 → 用户确认
    ▼
[Phase 4] automation-analysis
    │  分析自动化可行性 → 用户确认
    ▼
[Phase 5] automation-scripting
    │  生成 Playwright 脚本 → test-reviewer 审查
    ▼
[Phase 6] test-reporting
       生成最终测试报告
```

---

## 文件结构

Supertester 在项目目录下创建 `.supertester/` 目录：

```
.supertester/
├── test_plan.md              # 阶段追踪 + 决策 + 错误
├── findings.md              # 研究发现 + 知识库
├── progress.md              # 会话日志 + 时间戳
├── requirements/            # Phase 1-2 输出
│   ├── parsed-requirements.md
│   ├── clarifications.json
│   ├── module-dependencies.md
│   ├── implicit-requirements.md
│   └── cross-module-scenarios.md
├── test-cases/              # Phase 3-4 输出
│   ├── functional-cases.md
│   ├── automation-analysis.md
│   └── deduplication-report.md
├── scripts/                 # Phase 5 输出
│   ├── *.spec.ts
│   └── manual-cases.md
├── reviews/                 # 审查记录
│   └── review-*.md
└── reports/                # Phase 6 输出
    └── *.md
```

---

## 获取帮助

- 报告问题：https://github.com/supertester-ai/supertester/issues
- 主文档：https://github.com/supertester-ai/supertester
- OpenCode 文档：https://opencode.ai/docs/
- Claude Code 文档：https://docs.anthropic.com/
- Codex 文档：https://docs.codex.io/
- OpenClaw 文档：https://docs.openclaw.ai/
- Continue 文档：https://continue.dev/docs
