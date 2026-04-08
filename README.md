# Supertester

AI 驱动的软件测试智能体插件 — 从需求文档到 Playwright E2E 脚本的全流程测试工作流。

**零代码依赖** | **文件持久化** | **全程可追溯** | **独立审查**

## 它做了什么

当你给 Supertester 一份需求文档时，它不会直接生成测试。它会：

1. **先理解需求** — 解析文档，发现模糊项，一个个问你直到搞清楚
2. **分析模块关联** — 挖掘隐含需求，生成跨模块测试场景
3. **智能生成用例** — 根据需求特征自动选择合适的测试方法（等价类、边界值、状态转换...），而非盲目全调用
4. **标记自动化等级** — 每个用例标记为 automatable / partial / manual
5. **生成 Playwright 脚本** — 只为已确认的可自动化用例生成代码
6. **独立审查** — test-reviewer agent 在关键节点审查质量，不是自己验证自己

整个过程的每一步都持久化为本地文件，支持中断恢复，每个测试用例可追溯到原始需求的文件和行号。

## 工作流程

```
<<<<<<< HEAD
TestingAgent/
├── SKILL.md              # ✅ opencode 技能入口文件
├── README.md            # 使用文档
├── LICENSE              # MIT 许可证
├── .gitignore
└── docs/
    └── design.md        # 设计规格说明书
```

**说明：** opencode 技能是一个基于 `SKILL.md` 的 prompt 模板系统，不需要 npm 包或 JavaScript 源码。
software-testing-agent/
├── SKILL.md                    # 主技能文件
├── README.md                   # 使用文档
├── LICENSE                     # MIT 许可证
├── src/
│   ├── router.js              # 意图路由
│   ├── requirements/
│   │   ├── parser.js         # 解析需求文档
│   │   ├── clarifier.js      # 需求澄清
│   │   ├── session.js        # 对话状态持久化
│   │   └── association.js    # 需求关联分析
│   │       ├── dependency.js  # 模块依赖分析
│   │       ├── implicit.js    # 隐含需求挖掘
│   │       └── crossModule.js # 跨模块场景生成
│   ├── functional/
│   │   ├── index.js         # FCG 编排器
│   │   ├── equivalence.js    # 等价类
│   │   ├── boundary.js       # 边界值
│   │   ├── exception.js      # 异常场景
│   │   ├── state.js         # 状态转换
│   │   ├── scenario.js       # 场景流
│   │   ├── decisionTable.js  # 决策表
│   │   ├── security.js       # 安全测试
│   │   ├── performance.js    # 性能测试
│   │   ├── deduplicator.js   # 去重
│   │   └── templates/        # 用例模板
│   ├── automation/
│   │   ├── analyzer.js      # 自动化可行性分析
│   │   ├── playwright.js     # Playwright 生成
│   │   └── markers.js        # 自动化等级标记
│   ├── formatter/
│   │   ├── terminal.js       # 终端输出
│   │   └── report.js         # 报告生成
│   └── config.js             # 配置加载
├── sessions/                  # 对话状态存储
├── testing-agent.config.js   # 默认配置
└── docs/
    ├── design.md             # 设计规格
    └── specs/                # 设计文档
=======
需求文档
    |
    v
[Phase 1] 需求解析与澄清 ──> .supertester/requirements/parsed-requirements.md
    |                          .supertester/requirements/clarifications.json
    v
[Phase 2] 需求关联分析 ──────> .supertester/requirements/module-dependencies.md
    |        |                  .supertester/requirements/implicit-requirements.md
    |        |                  .supertester/requirements/cross-module-scenarios.md
    |        v
    |    test-reviewer 审查
    |        |
    v        v
    用户确认
    |
    v
[Phase 3] 功能用例生成 ──────> .supertester/test-cases/functional-cases.md
    |        |                  .supertester/test-cases/deduplication-report.md
    |        v
    |    test-reviewer 审查
    |        |
    v        v
    用户确认
    |
    v
[Phase 4] 自动化可行性分析 ──> .supertester/test-cases/automation-analysis.md
    |
    v
[Phase 5] Playwright 脚本 ──> .supertester/scripts/*.spec.ts
    |        |                  .supertester/scripts/manual-cases.md
    |        v
    |    test-reviewer 审查
    |
    v
[Phase 6] 测试报告 ──────────> .supertester/reports/YYYY-MM-DD-<module>.md
>>>>>>> 7442b16 (refactor: redesign as Supertester - Superpowers-style skill plugin)
```

## 安装

<<<<<<< HEAD
### 安装

```bash
# 克隆仓库
git clone https://gitcode.com/orion-c/TestingAgent.git
cd TestingAgent
```

### 在 opencode 中配置

**步骤 1：在你的项目中创建技能目录**

```bash
# 在你的项目根目录
mkdir -p .claude/skills/testing-agent
```

**步骤 2：复制技能文件**

```bash
# 复制 SKILL.md
cp TestingAgent/SKILL.md .claude/skills/testing-agent/

# 复制设计文档（可选）
cp -r TestingAgent/docs .claude/skills/testing-agent/
```

**步骤 3：重启 opencode**

重启 opencode 后，技能会自动加载。

### 验证安装

在 opencode 中输入：

```
/test help
```

或直接使用：

```
帮我分析 requirements/auth-prd.md 中的测试需求
```

### 使用方式

在 opencode 中直接输入自然语言：

```
帮我分析 requirements/auth-prd.md 中的测试需求
```

或使用内置命令：

```
/test parse requirements/auth-prd.md
/test clarify
/test functional for "登录模块"
/test automate
/test query "checkout 模块需要哪些测试？"
```

## 📖 工作流程
=======
### Claude Code (Plugin Marketplace)

```bash
# 从 marketplace 安装（发布后可用）
/plugin install supertester
```

### 手动安装

```bash
# 克隆到本地
git clone <repo-url> supertester

# 复制到项目的 .claude/plugins/ 目录
cp -r supertester ~/.claude/plugins/supertester
```

### Cursor

```text
/add-plugin supertester
```

## 快速开始

### 完整流程：从需求到脚本
>>>>>>> 7442b16 (refactor: redesign as Supertester - Superpowers-style skill plugin)

```
你: 分析 requirements/auth-prd.md 并生成测试

Supertester:
  > 初始化 .supertester/ 工作目录...
  > 解析需求文档... 发现 4 个模块、12 个功能点
  > 检测到 3 个模糊项，开始澄清：
  >
  > 最大登录尝试次数是多少？
  > A) 3 次  B) 5 次  C) 无限制

你: B

Supertester:
  > 已记录。下一个问题...
  > (澄清完毕后)
  > 需求关联分析完成，发现 2 个隐含需求、3 个跨模块场景
  > test-reviewer 审查通过
  > 请确认关联分析结果？[Y/n]

你: Y

Supertester:
  > 生成功能测试用例... 45 个原始用例，去重后 28 个
  > test-reviewer 审查通过
  > 请确认功能用例？[Y/n]

你: Y

Supertester:
  > 自动化分析: 18 automatable / 7 partial / 3 manual
  > 生成 Playwright 脚本: 3 个 spec 文件
  > 报告已生成: .supertester/reports/2026-04-07-auth.md
```

### 中断恢复

如果会话中断（关闭终端、/clear、上下文满了），下次启动时：

```
Supertester:
  > 检测到未完成的测试任务
  > 当前进度: Phase 2（需求关联分析）in_progress
  > 继续？[Y/n]
```

所有进度保存在 `.supertester/` 目录，不丢失。

### 从中间阶段开始

如果已有功能用例，可以跳过前几个阶段：

```
你: 为已有的功能用例生成自动化脚本
  > 检测到 .supertester/test-cases/functional-cases.md
  > 跳转到 Phase 4: 自动化可行性分析...
```

## 测试方法覆盖

Supertester 不是对每个需求调用所有生成器，而是先分析需求特征，再选择合适的方法：

| 需求特征 | 自动选择的生成器 |
|---------|----------------|
| 有输入验证 | 等价类 + 边界值 |
| 有状态变化 | 状态转换 + 场景流 |
| 有复杂业务规则 | 决策表 + 等价类 |
| 安全敏感 | 安全测试（OWASP） |
| 性能关键 | 性能测试（负载/压力/峰值） |
| 多模块交互 | 跨模块场景（关键路径/错误传导/并发） |

全部 8 种生成器：等价类、边界值、异常场景、状态转换、场景流、决策表、安全测试、性能测试。

## 文件持久化

Supertester 将所有工作记忆写入磁盘文件，而非依赖上下文窗口：

```
项目目录/
└── .supertester/
    ├── test_plan.md              # 阶段追踪 + 决策记录 + 错误日志
    ├── findings.md               # 分析发现 + 知识库
    ├── progress.md               # 会话日志 + 操作时间线
    ├── requirements/             # Phase 1-2 输出
    │   ├── parsed-requirements.md
    │   ├── clarifications.json
    │   ├── module-dependencies.md
    │   ├── implicit-requirements.md
    │   └── cross-module-scenarios.md
    ├── test-cases/               # Phase 3-4 输出
    │   ├── functional-cases.md
    │   ├── automation-analysis.md
    │   └── deduplication-report.md
    ├── scripts/                  # Phase 5 输出
    │   ├── *.spec.ts
    │   └── manual-cases.md
    ├── reviews/                  # test-reviewer 审查记录
    │   └── review-<phase>-<timestamp>.md
    └── reports/                  # Phase 6 输出
        └── YYYY-MM-DD-<module>.md
```

### 为什么用文件而不是上下文

借鉴 [planning-with-files](https://github.com/nickarino/planning-with-files) 的核心原则：

- **上下文窗口是内存** — 有限、易失，一次 /clear 就没了
- **文件系统是磁盘** — 持久、无限，随时可恢复
- **Hooks 自动操控注意力** — 每次用户消息前自动读取 test_plan.md，防止目标漂移

## 需求追溯

每个产物都携带上游溯源 ID，形成完整追溯链：

```
需求文档行号 → 需求ID(F-001) → 用例ID(TC-001) → 脚本注释(// TC-001 | F-001)
```

生成的 Playwright 脚本示例：

```typescript
// TC-001 | F-001 | auth-prd.md:45-48
test('should login with valid email', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-testid="email-input"]', 'test@example.com');
  await page.fill('[data-testid="password-input"]', 'CorrectPassword123');
  await page.click('[data-testid="login-btn"]');
  await expect(page).toHaveURL('/dashboard');
});
```

## 质量保证

### 独立审查 Agent

test-reviewer 是独立的审查 agent，在 Phase 2/3/5 自动触发：

- **需求覆盖审查** — 每个需求是否都有对应用例
- **用例质量审查** — 前置条件是否可执行、步骤是否无歧义
- **脚本质量审查** — 代码是否可运行、选择器是否稳定

审查发现 CRITICAL/HIGH 问题 → 修复 → 重新审查（最多 3 轮，之后升级到用户）。

### 行为控制

每个 Skill 内置 Superpowers 风格的行为控制：

| 机制 | 说明 |
|------|------|
| **Iron Law** | 每个阶段的绝对禁令（如"不理解需求不准测试"） |
| **Hard Gate** | 阻塞进入下一阶段的硬门禁（如"用例未审查不准提交"） |
| **Red Flags** | Agent 自我说服的防御表（如"需求看起来清楚"→"做完检测才知道"） |
| **2-Action Rule** | 每 2 个操作后必须写入文件，防信息丢失 |
| **3-Strike Protocol** | 3 次失败后停止并升级到用户 |

## 插件架构

```
supertester/
├── .claude-plugin/          # 插件元数据
├── hooks/                   # 5 个 Hooks (注意力操控)
│   ├── session-start        # 注入 skill + 恢复上下文
│   ├── user-prompt-submit   # 每次消息注入当前阶段
│   ├── pre-tool-use         # Write/Edit 前重温目标
│   ├── post-tool-use        # Write/Edit 后提醒更新进度
│   └── stop                 # 验证所有阶段完成
├── skills/                  # 7 个 Skills (测试工作流)
│   ├── using-supertester/   # 入口 + 路由
│   ├── requirement-analysis/
│   ├── requirement-association/
│   ├── test-case-generation/
│   ├── automation-analysis/
│   ├── automation-scripting/
│   └── test-reporting/
├── agents/                  # 独立审查 Agent
│   └── test-reviewer.md
├── templates/               # 3 文件持久化模板
├── scripts/                 # 初始化 + 会话恢复
└── package.json             # 零依赖
```

## 设计文档

完整的架构设计、Skill 详细定义、数据结构和流程控制机制，见 [docs/design.md](docs/design.md)。

## 致谢

Supertester 的设计融合了以下项目的核心思想：

| 项目 | 借鉴 |
|------|------|
| [Superpowers](https://github.com/obra/superpowers) | Skill 行为塑造（Iron Law / Hard Gate / Red Flags） |
| [planning-with-files](https://github.com/nickarino/planning-with-files) | 3 文件持久化 + Hooks 注意力操控 + 会话恢复 |
| [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) | 架构参考（多 agent 编排模式） |

## License

MIT
