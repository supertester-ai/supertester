---
name: testing-agent
description: "AI-powered software testing assistant - generates functional test cases and Playwright E2E scripts from requirement documents. Use when user wants to create tests, analyze requirements, or generate automation scripts."
---

# Software Testing Agent

AI 驱动的软件测试智能体插件。

## 使用场景

当用户说以下内容时使用此技能：

- "帮我测试..."
- "生成测试用例"
- "分析需求文档"
- "创建 E2E 测试"
- "需要测试这个功能"
- "生成 Playwright 脚本"
- "如何测试这个模块"

## 核心命令

### 1. 解析需求文档

```
/test parse requirements/auth-prd.md
```

解析 Markdown 需求文档，提取模块、功能点、边界条件。

### 2. 需求澄清

```
/test clarify
/test clarify for "登录模块"
```

检测模糊需求，发起澄清对话。支持会话中断恢复。

### 3. 生成功能测试用例

```
/test functional for "登录模块"
/test functional for requirements/auth-prd.md
```

生成人工可读的功能测试用例（不去重）。

### 4. 生成自动化脚本

```
/test automate
/test automate for TC-001, TC-002
```

根据已确认的用例生成 Playwright E2E 脚本。

### 5. 查询测试建议

```
/test query "checkout 模块需要哪些测试？"
/test query "登录模块的测试覆盖是否完整？"
```

回答关于测试的问题。

## 工作流程

```
需求文档
    │
    ▼
┌─────────────┐
│  需求解析    │ → 提取模块、功能、边界条件
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  需求澄清    │ → 模糊项澄清（支持中断恢复）
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  需求关联    │ → 模块依赖、隐含需求、跨模块场景
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 功能用例生成  │ → 智能选择生成器（等价类/边界值/异常等）
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  用户确认    │ → 审核确认用例
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 自动化分析   │ → 标记 automatable/partial/manual
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Playwright  │ → 生成 E2E 脚本
└─────────────┘
```

## 测试用例生成器

| 生成器 | 用途 |
|--------|------|
| 等价类生成器 | 正向/反向输入用例 |
| 边界值生成器 | 空值、最大/最小值、溢出 |
| 异常场景生成器 | 网络异常、系统错误 |
| 状态转换生成器 | 状态变迁 |
| 场景流生成器 | 单模块端到端流程 |
| 决策表生成器 | 复杂业务规则 |
| 安全测试生成器 | 注入、认证 |
| 性能测试生成器 | 负载、压力 |

## 自动化等级

| 等级 | 说明 |
|------|------|
| 🤖 `automatable` | 可完全自动化 |
| ⚠️ `partial` | 部分可自动化，需人工验证 |
| 👤 `manual` | 需人工执行 |

## 示例对话

### 示例 1：解析需求文档

```
用户: /test parse requirements/auth-prd.md

助手: ✅ 需求解析完成

模块: 用户认证
├─ F-001: 邮箱登录
├─ F-002: 密码重置
└─ F-003: 第三方登录

发现 3 个模糊项需要澄清：
1. F-001: 最大登录尝试次数？
2. F-002: 密码重置链接有效期？
3. F-003: 支持哪些第三方平台？
```

### 示例 2：生成测试用例

```
用户: /test functional for "登录模块"

助手: ✅ 生成了 12 个功能测试用例

├─ 等价类 (5个)
│  ├─ TC-001: 有效邮箱+正确密码 → 登录成功
│  ├─ TC-002: 无效邮箱格式 → 显示格式错误
│  └─ ...
├─ 边界值 (3个)
│  ├─ TC-006: 空邮箱 → 提示必填
│  └─ ...
├─ 异常场景 (2个)
│  └─ TC-008: 网络超时 → 显示重试
└─ 安全测试 (2个)
   └─ TC-010: SQL注入尝试 → 被拦截

⚠️ 3 个用例标记为 partial，需人工验证
```

### 示例 3：生成自动化脚本

```
用户: /test automate

助手: ✅ 生成了 Playwright E2E 脚本

├─ auth.e2e.spec.ts (9个测试)
│  ├─ TC-001 🤖 automatable
│  ├─ TC-002 🤖 automatable
│  └─ TC-008 ⚠️ partial
│     // 需要人工验证错误消息样式
└─ manual-cases.md (3个)
   └─ TC-010 👤 manual
      // 需要在真机上测试指纹识别
```

## 配置文件

项目根目录创建 `testing-agent.config.js`：

```javascript
module.exports = {
  conventions: {
    testDirectory: "__tests__",
    fileSuffix: ".test"
  },
  requirements: {
    docPatterns: ["**/requirements/**/*.md"]
  },
  clarification: {
    askBeforeGeneration: true,
    maxQuestionsPerRound: 3
  },
  workflow: {
    requireConfirmation: true
  }
}
```

## 注意事项

1. **需求优先** - 先理解需求，再生成测试
2. **澄清不跳过** - 模糊需求必须澄清后才能继续
3. **用户确认** - 用例确认后才生成自动化脚本
4. **用例追溯** - 每个用例记录原始需求来源

## 错误处理

| 错误 | 处理方式 |
|------|----------|
| 需求文档不存在 | 提示用户检查路径 |
| 解析失败 | 报告错误，建议检查文档格式 |
| 对话中断 | 自动保存状态，支持恢复 |
