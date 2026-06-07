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
3. **测试资产优先** — 测试不仅覆盖行为，还要保留关键规则、内容、状态断言、集成反馈和观测证据
4. **用例即终点** — 本流程产出经审查并用户确认的功能测试用例，不涉及自动化分析与脚本生成
5. **独立审查** — test-reviewer agent 审查，不自证清白
6. **人工门禁** — 关键节点必须用户确认

## 工作目标

Supertester（需求到用例版）的目标不是只生成“看起来完整”的功能用例，而是生成一套可追踪、可审查、且不丢关键测试资产的功能测试用例。流程从需求出发，终点为功能测试用例，不涉及自动化可行性分析、脚本生成与测试报告。

任何阶段都必须同时关注两件事：
- **行为覆盖**: 用户或系统的动作是否被测试到了
- **证据覆盖**: 我们是否保留了足够证据来证明它真的正确

如果只有行为覆盖，没有证据覆盖，后续最容易出现：
- 功能主流程看起来已覆盖，但关键规则、内容、列表或状态变化被漏掉
- 用例覆盖了流程，但不适合验收、排障或回归定位
- 去重后数量变少，但高价值测试资产也一起丢失

## 初始化

检查 `.supertester/` 目录：

**不存在：**
1. 创建 `.supertester/` 及子目录 (requirements/, test-cases/, reviews/, confirmations/)
2. 从 templates/ 复制 test_plan.md, findings.md, progress.md
3. 在 test_plan.md 的 Goal 中填写用户的测试目标
4. 检查 test_plan.md 的 Max Phase 字段：如果用户明确只需要到某个阶段（如 Phase 3），将 Max Phase 设为对应值；否则保持默认值
5. 更新 progress.md 的日期

**已存在：**
1. 读取 test_plan.md 确定当前阶段和 Max Phase
2. 如果当前阶段已达到 Max Phase，提示用户："检测到已完成的工作流（Max Phase = Phase X），所有阶段已完成。如需继续后续阶段，请更新 test_plan.md 中的 Max Phase。"
3. 如果未达到 Max Phase，提示用户："检测到未完成的测试任务，当前在 Phase X / Max Phase Y。继续？"
4. 用户确认后从断点恢复

## 意图路由

| 用户意图 | 触发 Skill | 示例 |
|---------|-----------|------|
| 解析需求文档 | requirement-analysis | "分析 requirements/auth-prd.md" |
| 继续澄清 | requirement-analysis（恢复） | "继续澄清"、"恢复 CL-002" |
| 分析模块关联 | requirement-association | "分析模块依赖" |
| 生成功能用例 | test-case-generation | "生成登录模块的测试用例" |
| 基于历史测试资产补充/修订/查缺补漏 | 先 requirement-analysis / requirement-association，再进入补充、修订和缺口补全 | "基于历史用例补充当前功能测试" |
| 查询/问答 | 直接回答 | "checkout 模块需要哪些测试？" |
| 请求自动化分析 / 脚本生成 / 测试报告 | 告知用户本版本不提供，流程终点为功能测试用例 | "生成 Playwright 脚本" |

如果用户提供了历史测试资产（历史用例、历史 case、测试清单、缺陷单、回归包），不要把它们只当参考材料。应优先把它们视为“业务历史逻辑与历史测试资产”，**在 Phase 1 就消化吸收**，用于补充、修订和查缺补漏，而不是把它们当成需要单独对比的一组产物：

**检测到历史测试资产时的处理流程：**
1. 在 Phase 1 解析需求的同时，解析历史测试资产，提取：
   - 完整 Prompt 文本（AI 产品的核心回归资产）
   - 第三方测试数据（支付测试卡号、OAuth 账号、短信测试号码等）
   - 具体库表名和字段名（DB 层断言依据）
   - 多条件决策矩阵（权益 x 授权 x 角色组合）
   - 多语言文案（中英文对照）
   - 运营策略场景（限免、优惠券、灰度等）
2. 将提取结果合并到 parsed-requirements.md 的测试资产汇总中（Prompt Inventory / Multi-Language Inventory 等）
3. Phase 3 生成或修订时，确保这些高价值资产不被遗漏，并在已有资产基础上做增补、删改和信息补全
4. 输出时围绕“当前需求下哪些历史逻辑应保留、哪些应调整、哪些缺口需要补齐”来组织结果，而不是做产物之间的比较

## Skill 索引

| # | Skill | 前置条件 | 输出 |
|---|-------|---------|------|
| 0 | using-supertester | — | 初始化 .supertester/ |
| 1 | requirement-analysis | 需求文档 | parsed-requirements.md, clarifications.json |
| 2 | requirement-association | Phase 1 complete | module-dependencies.md, implicit-requirements.md, cross-module-scenarios.md |
| 3 | test-case-generation | Phase 2 complete + 用户确认 | functional-cases.yaml, deduplication-report.md |

每个阶段的关注重点：
- **Phase 1**: 解析功能需求 + 抽取测试资产 + 明确证据类型 + 识别多语言/Prompt/测试数据资产 + 消化历史测试资产
- **Phase 2**: 分析功能依赖 + 状态依赖 + 证据依赖 + 共享资源风险
- **Phase 3**: 生成功能用例，同时保护关键测试资产不在简化或去重中丢失。这是本流程的终点产物

## 流程终止控制 (Max Phase)

`test_plan.md` 中的 **Max Phase** 字段控制工作流的终止阶段。达到该阶段后，`using-supertester` 将阻止进入后续 Phase 的请求，直到用户更新 Max Phase。本版本的最大 Phase 为 Phase 3（功能测试用例生成），不存在更后续的阶段。

### 工作流终止行为

| Max Phase | 终止点 | 被阻止的技能 |
|-----------|--------|-------------|
| Phase 1 | 需求解析完成后 | requirement-association, test-case-generation |
| Phase 2 | 关联分析完成后 | test-case-generation |
| Phase 3 (或不填) | 用例生成完成后 | 无（已是流程终点） |

### Max Phase 检查规则

1. **每次意图路由前检查**: 将用户意图映射到的目标 Phase 与 Max Phase 比较
2. **超出范围处理**: 如果目标 Phase > Max Phase，回复：
   ```
   当前 Max Phase = Phase X，该操作需要 Phase Y。
   如需继续，请先在 test_plan.md 中将 Max Phase 更新为 Phase Y。
   ```
3. **达到 Max Phase 后**: 对应 Phase 完成后的用户确认消息末尾追加：
   ```
   已到达 Max Phase (Phase X)。工作流在此终止。
   如需继续后续阶段，请更新 test_plan.md 中的 Max Phase 并重新启动会话。
   ```

## 文件持久化规则

### 3 核心文件

- **test_plan.md** — 阶段追踪 + 决策 + 错误记录。每次阶段变更、重大决策、错误发生时更新。
- **findings.md** — 分析发现 + 知识库。遵守 2-Action Rule。
- **progress.md** — 会话日志 + 时间线。每完成操作后更新。

### HTML 确认页

每个阶段进入“用户确认”前，必须生成可直接打开审查的 HTML 页面，而不是只让用户去隐藏目录里翻 Markdown。

生成命令（在目标项目根目录执行）：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/render-confirmation-html.py" --phase <1|2|3> --project-dir .
```

如果 `CLAUDE_PLUGIN_ROOT` 不可用，使用当前插件仓库中的脚本路径：

```bash
python3 /path/to/supertester/scripts/render-confirmation-html.py --phase <1|2|3> --project-dir .
```

输出路径固定为：

- Phase 1: `.supertester/confirmations/phase-1-confirmation.html`
- Phase 2: `.supertester/confirmations/phase-2-confirmation.html`
- Phase 3: `.supertester/confirmations/phase-3-confirmation.html`

确认页必须包含待确认产物、关键 checklist、缺失/blocked 项和 reviewer 摘要（如该阶段有 reviewer）。向用户请求确认时，必须同时给出 HTML 文件路径。用户明确确认后，才允许把对应 Phase 标为 complete。

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
| "超出 Max Phase 的用户请求可以直接执行" | Max Phase 是用户显式设定的终止边界，不得绕过。必须提示用户更新 Max Phase 后再继续。 |
| "历史测试用例只是参考" | 历史测试资产往往包含高价值规则、内容、状态断言和经验边界，忽略它们会让新生成结果失真 |
| "先把功能用例生成出来再查缺补漏" | 如果不在早期识别测试资产和证据类型，后期补洞成本更高 |

## 完整流程

```
需求文档 → [Skill 1] 解析+澄清 → [Skill 2] 关联分析 → 审查 → 用户确认
    → [Skill 3] 用例生成 → 审查 → 用户确认（流程终点：functional-cases.yaml）
```

## 基于历史测试资产的补充、修订与查缺补漏

当用户提供了历史测试资产时，默认按“基于历史资产补充、修订、查缺补漏”来处理。这里的历史资产代表业务历史逻辑和既有测试沉淀，不代表一组需要与新结果做横向比较的对象：

1. 先把历史测试资产纳入 Phase 1/2 的上下文，而不是只在最后报告阶段查看
2. 优先输出：
   - 需要保留的历史高价值资产
   - 需要新增的缺失覆盖
   - 需要删改的过时或失真内容
   - 需要补全的规则、数据、状态和证据链
3. 输出结论要服务于当前需求的测试设计，而不是服务于一份“旧 vs 新”的比较报告

不要把这类任务退化成“数量统计”或“谁更多”。重点是当前需求下的覆盖结构、修订质量和测试资产保真度。
