# Supertester 安装指南

Supertester 是一个 AI 驱动的软件测试工作流插件，支持多种智能体工具。本文档详细说明如何在各平台安装和配置 Supertester。

## 平台概览

| 平台 | 安装方式 | 插件目录 | 技能目录 |
|------|---------|---------|---------|
| [OpenCode](#opencode-安装) | NPM 包插件 | `.opencode/plugins/` | `skills/` |
| [Claude Code](#claude-code-安装) | 插件市场 | `.claude-plugin/` | `skills/` |
| [Codex](#codex-安装) | Git 克隆 + Symlink | — | `~/.agents/skills/` |
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

- OpenAI Codex CLI 已安装
- Git

### 安装步骤

**1. 克隆仓库**

```bash
git clone https://github.com/supertester-ai/supertester.git ~/.codex/supertester
```

**2. 创建技能符号链接**

```bash
mkdir -p ~/.agents/skills
ln -s ~/.codex/supertester/skills ~/.agents/skills/supertester
```

**Windows (PowerShell)**
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\supertester" "$env:USERPROFILE\.codex\supertester\skills"
```

**3. 重启 Codex**

退出并重新启动 Codex CLI，技能会在启动时被扫描发现。

### 验证安装

```bash
ls -la ~/.agents/skills/supertester
```

应该看到指向 `~/.codex/supertester/skills` 的符号链接（或 Windows 上的链接）。

### 多代理功能（可选）

如果需要使用 `dispatching-parallel-agents` 等技能，在 Codex 配置中启用多代理功能：

```toml
[features]
multi_agent = true
```

### 更新

```bash
cd ~/.codex/supertester && git pull
```

技能通过符号链接即时更新。

### 卸载

```bash
rm ~/.agents/skills/supertester
# 可选：删除克隆的仓库
rm -rf ~/.codex/supertester
```

**Windows (PowerShell)**
```powershell
Remove-Item "$env:USERPROFILE\.agents\skills\supertester"
```

### 故障排除

**技能未显示**
1. 验证符号链接：`ls -la ~/.agents/skills/supertester`
2. 检查技能目录：`ls ~/.codex/supertester/skills`
3. 重启 Codex — 技能在启动时发现

**Windows 链接问题**

链接通常不需要特殊权限。如果创建失败，尝试以管理员身份运行 PowerShell。

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
