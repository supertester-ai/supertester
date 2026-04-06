# 软件测试智能体插件 - 设计规格说明书

## 概述

**插件名称：** `software-testing-agent`  
**类型：** 独立技能插件  
**核心功能：** AI 驱动的软件测试助手，覆盖完整测试生命周期：需求解析、功能测试用例生成、自动化脚本生成和测试分析。  
**目标用户：** 使用 Playwright 进行 Web E2E 测试的 JavaScript/TypeScript 开发者。

---

## 核心设计原则

### 原则一：需求优先

> **在生成任何测试之前，必须先理解需求。**

大型需求文档（markdown 文件、PRD、规范说明）在任何测试生成之前必须被解析和分析。模糊或不清晰的需求会触发澄清对话。

### 原则二：两阶段测试生成

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────────────┐
│  功能测试用例    │ ──▶ │      确认环节         │ ──▶ │     自动化脚本           │
│  (人工可读)      │     │    (用户确认)         │     │  (自动化 + 人工标记)     │
└─────────────────┘     └──────────────────────┘     └─────────────────────────┘
```

**阶段一：功能测试用例（人工用例）**
- 从需求生成人工可读的测试用例
- 不涉及自动化，仅包含测试步骤和预期结果
- 重点关注完整性：测试什么，而非如何自动化

**阶段二：自动化脚本**
- 仅在功能测试用例确认后开始
- 生成 Playwright E2E 测试代码
- **为每个测试用例标记：**
  - 🤖 `automatable` - 可完全自动化
  - ⚠️ `partial` - 部分可自动化，需人工介入
  - 👤 `manual` - 需人工执行

### 原则三：人工介入

```
需求 → 解析 → [发现模糊?] → 澄清 ─┐
                                  │
         ┌────────────────────────┘
         ▼
功能用例 ──▶ 用户审核 ──▶ 确认
                           │
                           ▼
                  自动化脚本 ──▶ 带标记的输出
```

---

## 架构设计

### 整体架构

```
用户输入
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                      意图路由器                              │
│           (解析用户意图：需求分析/功能用例/自动化脚本)          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      需求解析器                              │
│            (解析需求文档，提取模块、功能点、边界条件)          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      需求澄清器                              │
│              (检测模糊需求，发起澄清对话)                      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    需求关联分析器                             │
│            (模块依赖分析 → 隐含需求挖掘 → 跨模块场景生成)       │
└────────────────────────────┬────────────────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         │                                           │
         ▼                                           ▼
┌─────────────────────┐               ┌─────────────────────┐
│   功能用例生成器     │               │    需求清晰则继续     │
│   (单模块用例)       │               │                     │
└──────────┬──────────┘               └──────────┬──────────┘
           │                                     │
            ▼                                     │
┌─────────────────────┐                         │
│     用户确认环节      │ ◀────────────────────────┘
└──────────┬──────────┘
           │ (确认后)
           ▼
┌─────────────────────────────────────────────────────────────┐
│                      自动化可行性分析器                       │
│               (分析每个用例，标记自动化可行性)                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    自动化脚本生成器                           │
│                (生成框架代码，标记自动化等级)                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                       输出格式化器                           │
│                    (终端摘要 + 报告文件)                      │
└─────────────────────────────────────────────────────────────┘
```

**需求关联分析器**是架构流程中的必要环节，位于需求澄清之后、功能用例生成之前：
- 解析模块间的依赖关系
- 挖掘需求中隐含的场景
- 生成跨模块的关联测试场景

### 组件详情

#### 1. 意图路由器

**用途：** 解析用户输入，确定测试任务类型。

**支持的意图：**
- `parse` - 解析需求文档，提取可测试项
- `clarify` - 处理模糊需求
- `functional` - 生成功能测试用例
- `automate` - 根据已确认用例生成自动化脚本
- `analyze` - 分析现有测试覆盖率和缺口
- `query` - 回答关于测试的问题

**实现方式：**
- 用户输入关键词模式匹配
- 返回：`{ intent: string, confidence: number, parameters: object }`

#### 2. 需求解析器

**用途：** 解析大型需求文档（markdown），提取可测试项。

**能力：**
- 解析包含多个模块/章节的 markdown 文件
- 提取功能、用户故事、验收标准
- 识别文档中提到的模块、函数、类
- 从文本中提取边界条件、错误场景
- 构建结构化需求树

**输出：**
```javascript
{
  modules: [
    {
      name: "用户认证",
      file: "auth.md",
      features: [
        {
          id: "F-001",
          name: "邮箱登录",
          description: "...",
          acceptanceCriteria: ["有效邮箱重定向到仪表板", "无效显示错误"],
          boundaryConditions: ["空邮箱", "格式无效", "密码错误"],
          dependencies: ["用户服务", "令牌服务"]
        }
      ]
    }
  ],
  ambiguousItems: [
    { module: "用户认证", feature: "F-001", unclear: "最大登录尝试次数是多少？" }
  ]
}
```

#### 3. 需求澄清器

**用途：** 检测模糊需求并发起澄清对话。

**核心特性：对话状态持久化与恢复**

由于澄清过程可能因需要与项目团队沟通而中断，设计必须支持对话状态的持久化和恢复。

**对话状态管理：**
```javascript
{
  sessionId: "clarify-session-20260406-001",
  requirementDoc: "requirements/auth-prd.md",
  status: "in_progress" | "paused" | "completed",
  createdAt: "2024-04-06T10:00:00Z",
  updatedAt: "2024-04-06T14:30:00Z",
  
  // 已完成的澄清
  completedClarifications: [
    {
      id: "CL-001",
      question: "最大登录尝试次数是多少？",
      answer: "5次",
      answeredAt: "2024-04-06T11:00:00Z",
      answeredBy: "user"
    }
  ],
  
  // 待澄清的项
  pendingClarifications: [
    {
      id: "CL-002",
      question: "密码过期策略是什么？",
      status: "pending",
      options: ["90天", "180天", "永不过期"]
    }
  ],
  
  // 当前暂停的原因
  pauseReason: "需要与后端团队确认密码过期策略",
  resumedFrom: null  // 如果是从中断恢复，记录恢复点
}
```

**对话生命周期：**

```
┌─────────┐    开始澄清    ┌─────────────┐
│  初始   │ ───────────▶ │  进行中     │
└─────────┘               │ (in_progress)│
                          └──────┬──────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
        ┌──────────┐      ┌──────────┐      ┌──────────┐
        │ 已完成   │      │  已暂停   │      │  已中断   │
        │(completed)│      │ (paused) │      │(aborted) │
        └──────────┘      └────┬─────┘      └──────────┘
                               │
                               │ 恢复对话
                               ▼
                        ┌─────────────┐
                        │ 从暂停点继续 │
                        └─────────────┘
```

**行为：**
- 检测到模糊项时暂停
- 采用一对一提问方式
- 尽可能提供多选选项
- 记录澄清内容供后续参考
- **每次交互后自动保存状态**
- **支持通过会话ID恢复中断的对话**

**对话恢复机制：**

| 恢复触发方式 | 说明 |
|-------------|------|
| 用户说"继续澄清" | 自动查找最近的暂停会话并恢复 |
| 用户说"恢复 CL-002" | 恢复指定的澄清项 |
| 用户提供答案 | 自动关联到对应的暂停项并继续 |

**澄清类型：**
- 缺失的边界条件
- 不清晰的验收标准
- 未定义的错误处理
- 模糊的数据约束

#### 4. 需求关联分析器

**用途：** 分析需求模块间的关联关系，挖掘隐含需求场景，生成跨模块测试用例。

**核心能力：**

##### 4.1 模块依赖分析

**目的：** 构建模块间的依赖关系图，理解模块如何协同工作。

**分析方法：**
- 显式依赖：需求文档中明确提到的模块调用关系
- 隐式依赖：通过数据流/事件流推断的模块关联
- 共享资源依赖：多个模块依赖同一数据/服务

**输出：**
```javascript
{
  moduleGraph: {
    nodes: [
      { id: "用户认证", type: "core", dependencies: ["邮件服务", "令牌服务"] },
      { id: "商品目录", type: "core", dependencies: ["库存服务", "搜索服务"] },
      { id: "购物车", type: "core", dependencies: ["用户认证", "商品目录", "库存服务"] },
      { id: "支付", type: "core", dependencies: ["购物车", "订单服务", "第三方支付"] }
    ],
    edges: [
      { from: "用户认证", to: "购物车", type: "session" },
      { from: "商品目录", to: "购物车", type: "data_flow" },
      { from: "购物车", to: "支付", type: "workflow" }
    ]
  },
  criticalPaths: [
    ["用户认证", "商品目录", "购物车", "支付", "订单"],
    ["用户认证", "购物车", "支付", "通知"]
  ]
}
```

##### 4.2 隐含需求挖掘

**目的：** 从需求文本中推断未明确说明但必须存在的场景。

**挖掘策略：**
| 隐含类型 | 识别模式 | 示例 |
|----------|----------|------|
| 前置条件隐含 | "后" → 隐含"前" | "登录后显示仪表板" → 隐含未登录时的重定向需求 |
| 后置结果隐含 | "为了X" → 隐含X失败的处理 | "为了完成订单" → 隐含库存不足/支付失败的场景 |
| 数据一致性隐含 | A模块修改数据 → B模块应同步 | "用户修改邮箱" → 隐含订单中邮箱展示的同步需求 |
| 边界情况隐含 | 正常流程 → 边界情况 | "允许添加购物车" → 隐含库存上限、超重、有效期等边界 |
| 异常传导隐含 | 模块A异常 → 模块B如何响应 | "支付服务不可用" → 隐含订单状态、用户通知的处理 |

**输出：**
```javascript
{
  implicitRequirements: [
    {
      id: "IR-001",
      impliedBy: {
        module: "登录",
        statement: "登录后显示用户仪表板"
      },
      inferredRequirement: {
        name: "未登录访问保护",
        description: "未登录用户访问 /dashboard 应重定向到登录页",
        type: "security",
        severity: "high"
      }
    },
    {
      id: "IR-002",
      impliedBy: {
        module: "订单",
        statement: "为保证订单完成"
      },
      inferredRequirement: {
        name: "支付失败处理",
        description: "支付失败时订单应保持待支付状态，允许重试",
        type: "error_handling",
        severity: "critical"
      }
    }
  ]
}
```

##### 4.3 跨模块场景生成

**目的：** 基于模块依赖分析，生成串联多个相关模块的测试场景。

**生成策略：**
1. 从关键路径（critical paths）生成主流程场景
2. 从模块边界（module boundaries）生成集成测试场景
3. 从异常传导路径生成错误恢复场景

**场景类型：**

| 场景类型 | 描述 | 示例 |
|----------|------|------|
| 关键路径场景 | 覆盖核心业务流程的端到端场景 | 注册→登录→浏览→下单→支付→确认 |
| 模块边界场景 | 测试模块间的接口和数据一致性 | 购物车数量变化→订单详情同步 |
| 错误传导场景 | 一个模块的错误如何影响下游模块 | 支付超时→订单状态→通知用户 |
| 并发场景 | 多模块间的状态一致性 | 用户同时打开多个页面购物车同步 |
| 数据同步场景 | 模块间的数据一致性问题 | 修改收货地址→历史订单显示旧地址？ |

**输出：**
```javascript
{
  crossModuleScenarios: [
    {
      id: "CMS-001",
      name: "完整购买流程（关键路径）",
      scenarioType: "critical_path",
      modules: ["用户认证", "商品目录", "购物车", "支付", "订单", "通知"],
      steps: [
        { step: 1, module: "用户认证", action: "用户登录系统", expected: "获取有效会话" },
        { step: 2, module: "商品目录", action: "浏览并搜索商品", expected: "返回商品列表" },
        { step: 3, module: "商品目录", action: "查看商品详情", expected: "显示库存、价格" },
        { step: 4, module: "购物车", action: "添加商品到购物车", expected: "购物车计数+1" },
        { step: 5, module: "购物车", action: "修改商品数量", expected: "实时更新总价" },
        { step: 6, module: "支付", action: "发起支付流程", expected: "跳转支付网关" },
        { step: 7, module: "支付", action: "支付成功回调", expected: "创建订单" },
        { step: 8, module: "订单", action: "订单状态变更", expected: "状态变为已支付" },
        { step: 9, module: "通知", action: "发送订单确认", expected: "邮件/短信通知" }
      ],
      entryCondition: "用户已注册，有有效商品",
      exitCondition: "订单完成，用户收到确认通知"
    },
    {
      id: "CMS-002",
      name: "支付失败-订单恢复（错误传导）",
      scenarioType: "error_propagation",
      modules: ["支付", "订单", "通知", "购物车"],
      steps: [
        { step: 1, module: "购物车", action: "用户添加商品并发起结算", expected: "创建待支付订单" },
        { step: 2, module: "支付", action: "用户选择支付方式", expected: "显示支付页面" },
        { step: 3, module: "支付", action: "支付超时或失败", expected: "返回支付失败" },
        { step: 4, module: "订单", action: "订单保持待支付状态", expected: "订单不自动取消" },
        { step: 5, module: "购物车", action: "商品仍保留在购物车", expected: "用户可继续支付" },
        { step: 6, module: "通知", action: "发送支付失败通知", expected: "提醒用户重试" }
      ],
      entryCondition: "用户发起支付",
      exitCondition: "用户可重新支付或放弃"
    },
    {
      id: "CMS-003",
      name: "多设备购物车同步（并发场景）",
      scenarioType: "concurrency",
      modules: ["用户认证", "购物车"],
      steps: [
        { step: 1, module: "设备A", action: "用户登录并添加商品A到购物车", expected: "购物车显示1件商品" },
        { step: 2, module: "设备B", action: "同一用户在其他设备登录", expected: "获取相同会话" },
        { step: 3, module: "设备B", action: "设备B添加商品B到购物车", expected: "设备A购物车应同步显示2件" },
        { step: 4, module: "设备A", action: "设备A删除商品A", expected: "设备B购物车应同步显示只剩商品B" }
      ],
      entryCondition: "用户登录状态，多设备",
      exitCondition: "所有设备购物车状态一致"
    }
  ]
}
```

#### 5. 功能用例生成器（智能编排）

**用途：** 分析每个需求点的特性，智能选择合适的子生成器，而非对所有需求调用所有生成器。

**核心流程：**
```
确认后的需求
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                   需求特性分析器                            │
│         (分析需求类型 → 决定调用哪些生成器)                   │
└────────────────────────────┬────────────────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         │         按需调用合适的生成器            │
         ▼                    ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  仅 API/函数    │ │  有状态机特征   │ │  复杂业务规则   │
│  → 等价类+边界值 │ │  → 状态转换    │ │  → 决策表       │
│                 │ │    + 场景流    │ │    + 等价类     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                    │                    │
         └────────────────────┴────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │     去重引擎    │
                    └─────────────────┘
```

**需求特性分析器：**

根据需求特征自动判断需要哪些生成器：

```javascript
{
  requirementAnalysis: {
    requirement: {
      id: "F-001",
      name: "用户登录",
      type: "api" | "workflow" | "stateful" | "business_rule" | "security"
    },
    
    // 需求特征判断
    characteristics: {
      hasInputValidation: true,      // 需要等价类、边界值
      hasStateTransitions: true,     // 需要状态转换
      hasBusinessRules: false,        // 不需要决策表
      hasSecurityConcerns: true,      // 需要安全测试
      isCrossModule: false,          // 跨模块由关联分析器处理
      hasPerformanceRequirements: false
    },
    
    // 决定调用的生成器
    selectedGenerators: [
      "equivalence",      // 必须：输入验证
      "boundary",         // 必须：边界值
      "exception",        // 必须：错误处理
      "state",            // 必须：有状态转换
      "security"          // 必须：有安全需求
    ],
    
    // 不调用的生成器及原因
    skippedGenerators: [
      { generator: "decisionTable", reason: "无复杂业务规则" },
      { generator: "performance", reason: "无性能需求描述" },
      { generator: "scenario", reason: "单模块API，非工作流" }
    ]
  }
}
```

**需求类型 → 生成器映射：**

| 需求类型 | 必需生成器 | 可选生成器 |
|----------|-----------|-----------|
| **API/函数** | 等价类、边界值 | 异常场景 |
| **工作流/业务流程** | 场景流、异常场景 | 等价类、边界值 |
| **状态机模块** | 状态转换、场景流 | 边界值、异常场景 |
| **复杂业务规则** | 决策表、等价类 | 边界值、安全测试 |
| **安全敏感模块** | 安全测试、等价类 | 异常场景、边界值 |
| **性能关键模块** | 性能测试、场景流 | 边界值 |

**示例判断逻辑：**

```javascript
function selectGenerators(requirement) {
  const selected = new Set();
  
  // 基础生成器：几乎所有需求都需要
  selected.add('equivalence');  // 等价划分
  selected.add('boundary');     // 边界值
  
  // 根据需求类型判断
  if (requirement.type === 'api' || requirement.type === 'function') {
    // API/函数：主要关注输入输出
    selected.add('exception');  // 异常场景
  }
  
  if (requirement.type === 'workflow' || requirement.type === 'stateful') {
    // 工作流/状态机：需要状态转换
    selected.add('state');
    selected.add('scenario');
  }
  
  if (requirement.hasComplexConditionals) {
    // 复杂条件：需要决策表
    selected.add('decisionTable');
  }
  
  if (requirement.type === 'security' || requirement.securityRelated) {
    // 安全相关：必须安全测试
    selected.add('security');
  }
  
  if (requirement.performanceCritical) {
    // 性能关键：添加性能测试
    selected.add('performance');
  }
  
  return Array.from(selected);
}
```

**子生成器清单：**

| 生成器 | 适用场景 | 判断条件 |
|--------|----------|----------|
| 等价类生成器 | 输入验证、参数校验 | `hasInputValidation: true` |
| 边界值生成器 | 数值边界、长度限制 | `hasBoundaryConditions: true` |
| 异常场景生成器 | 错误处理、异常流程 | `hasErrorHandling: true` |
| 状态转换生成器 | 状态机、有限状态模块 | `hasStateTransitions: true` |
| 场景流生成器 | 工作流、业务流程 | `type === 'workflow'` |
| 决策表生成器 | 复杂业务规则、多条件 | `hasComplexConditionals: true` |
| 安全测试生成器 | 安全敏感模块 | `type === 'security'` |
| 性能测试生成器 | 性能关键模块 | `performanceCritical: true` |
| 去重引擎 | 去除所有重复用例 | 始终调用 |
| 场景流生成器 | 端到端场景测试 | 跨模块业务流程 |
| 决策表生成器 | 复杂业务规则测试 | 条件组合、决策逻辑 |
| 安全测试生成器 | 安全测试用例 | 注入、认证、数据保护 |
| 性能测试生成器 | 非功能测试用例 | 负载、压力、响应时间 |
| 去重引擎 | 去除重复用例 | 合并冗余测试用例 |

---

##### 4.1 等价类生成器

**用途：** 基于等价划分生成测试用例（正向/反向）。

**等价类：**
- 有效输入（应该通过）
- 无效输入（应该以特定错误失败）
- 边界值（边界情况）

**输出：**
```javascript
{
  type: "equivalence",
  category: "positive" | "negative",
  partition: "valid_email" | "invalid_format" | "empty" | "not_registered",
  description: "有效邮箱格式应成功登录",
  input: { email: "test@example.com", password: "ValidPass123" },
  expectedResult: "登录成功，重定向到仪表板"
}
```

---

##### 4.2 边界值生成器

**用途：** 生成边界条件的测试用例。

**边界类型：**
- 数值边界（0、最大值、最小值、-1、溢出）
- 字符串边界（空、最大长度、Unicode）
- 集合边界（空数组、单个元素、大型数据集）

**输出：**
```javascript
{
  type: "boundary",
  boundaryType: "length_max" | "value_min" | "empty" | "null" | "overflow",
  description: "255个字符的邮箱（最大允许长度）",
  input: { email: "a".repeat(250) + "@test.com", password: "ValidPass123" },
  expectedResult: "根据规范接受或拒绝"
}
```

---

##### 4.3 异常场景生成器

**用途：** 生成错误条件和异常处理的测试用例。

**异常类型：**
- 网络错误（超时、断连）
- 系统错误（崩溃、OOM）
- 数据错误（损坏、无效状态）
- 安全错误（未授权、禁止访问）

**输出：**
```javascript
{
  type: "exception",
  exceptionType: "network_timeout" | "invalid_state" | "unauthorized_access",
  description: "登录时网络超时",
  preconditions: ["用户输入凭证", "网络变得不可用"],
  steps: ["输入邮箱", "输入密码", "点击登录", "网络超时发生"],
  expectedResult: "显示重试选项，不崩溃"
}
```

---

##### 4.4 状态转换生成器

**用途：** 生成基于状态的测试用例。

**状态类型：**
- 状态转换（logged_out → logging_in → logged_in）
- 工作流序列（cart → checkout → payment → confirmation）
- 会话状态（过期、更新、终止）

**输出：**
```javascript
{
  type: "state_transition",
  fromState: "已登出",
  event: "提交有效凭证",
  toState: "已登录",
  description: "使用有效凭证从已登出状态转换到已登录状态",
  steps: ["验证初始状态为已登出", "提交有效凭证", "验证状态现在为已登录"]
}
```

---

##### 4.5 场景流生成器

**用途：** 生成覆盖单个模块内的端到端用户场景测试用例。

**注意：** 跨模块的复杂场景由**需求关联分析器**（4.4节）负责生成。

**适用场景（单模块内）：**
- 模块内用户旅程测试
- 模块内状态流转
- 模块内错误处理

**场景类型：**
- 主流程（Happy Path）
- 备选流程（Alternative Path）
- 错误恢复流程（Error Recovery）

**输出：**
```javascript
{
  type: "scenario",
  scenarioName: "登录流程（单模块）",
  scenarioType: "happy_path" | "alternative" | "error_recovery",
  module: "用户认证",
  steps: [
    { step: 1, action: "输入有效邮箱", expected: "邮箱格式验证通过" },
    { step: 2, action: "输入正确密码", expected: "密码验证通过" },
    { step: 3, action: "点击登录按钮", expected: "跳转到仪表板" }
  ],
  entryCondition: "用户打开登录页面",
  exitCondition: "用户成功登录或显示错误"
}
```

**与需求关联分析器的区别：**

| 场景类型 | 生成器 | 范围 |
|----------|--------|------|
| 单模块内场景 | 场景流生成器 | 单个模块内的操作流程 |
| 跨模块场景 | 需求关联分析器 | 多模块间的数据流/工作流 |

---

##### 4.6 决策表生成器

**用途：** 从具有多个输入条件的复杂业务规则生成测试用例。

**适用场景：**
- 定价规则（基于会员资格 + 数量 + 季节的折扣）
- 验证规则（基于类型 + 必填 + 条件的字段验证）
- 资格规则（基于多个条件的审批）

**决策表结构：**
```javascript
{
  conditionColumns: ["是否高级会员", "订单 > $100", "季节折扣"],
  actionColumns: ["应用10%折扣", "应用20%折扣", "无折扣"],
  rules: [
    { conditions: [true, true, false], actions: ["应用10%折扣"] },
    { conditions: [true, false, true], actions: ["应用20%折扣"] },
    // ... 所有组合
  ]
}
```

**输出：**
```javascript
{
  type: "decision_table",
  ruleName: "折扣资格",
  conditions: [
    { name: "是否高级会员", type: "boolean", values: [true, false] },
    { name: "订单金额", type: "numeric", values: ["<$50", "$50-$100", ">$100"] },
    { name: "是否有优惠券", type: "boolean", values: [true, false] }
  ],
  rules: [
    { id: "DT-001", conditions: [true, ">$100", true], expected: "25%折扣" },
    { id: "DT-002", conditions: [true, "$50-$100", false], expected: "15%折扣" }
  ],
  testCases: [
    { ruleId: "DT-001", input: {...}, expected: "25%折扣" }
  ]
}
```

---

##### 4.7 安全测试生成器

**用途：** 生成以安全为重点的测试用例。

**安全测试类别：**
- 输入验证（SQL注入、XSS、命令注入）
- 认证与授权（绕过、权限提升）
- 数据保护（加密、PII处理）
- 会话管理（会话固定、劫持、超时）
- API安全（限流、CORS、CSRF）

**输出：**
```javascript
{
  type: "security",
  category: "injection" | "auth" | "data_protection" | "session" | "api",
  testName: "登录表单中的SQL注入",
  attackVector: "' OR '1'='1",
  description: "尝试通过邮箱字段进行SQL注入",
  expectedBehavior: "输入被清理，无数据库暴露，显示错误",
  severity: "critical" | "high" | "medium" | "low",
  owaspCategory: "A03:2021 - Injection"
}
```

---

##### 4.8 性能测试生成器

**用途：** 生成非功能性性能测试用例。

**性能测试类型：**
- 响应时间测试（负载下的API响应）
- 负载测试（并发用户限制）
- 压力测试（断点识别）
- 持久性测试（内存泄漏、随时间退化）
- 峰值测试（流量突增）

**输出：**
```javascript
{
  type: "performance",
  testType: "load" | "stress" | "endurance" | "spike",
  testName: "负载下的登录API响应时间",
  scenario: "100个并发用户尝试登录",
  metrics: {
    responseTime: { target: "<500ms", threshold: "<1000ms" },
    throughput: { target: ">100 req/sec" },
    errorRate: { target: "<1%" }
  },
  preconditions: ["服务器已部署", "测试数据已填充"],
  testPhases: [
    { phase: "ramp_up", duration: "2min", users: "0 → 100" },
    { phase: "sustained", duration: "10min", users: "100" },
    { phase: "ramp_down", duration: "1min", users: "100 → 0" }
  ],
  successCriteria: "95%的请求在500ms内完成"
}
```

---

##### 4.9 去重引擎

**用途：** 从所有子生成器中去除重复的测试用例。

**去重策略：**
```javascript
{
  strategies: [
    "exact_duplicate",        // 相同输入、相同预期
    "subset_duplicate",      // 一个用例覆盖另一个
    "redundant_boundary",    // 边界值与等价类冗余
    "overlapping_state"      // 状态转换已被覆盖
  ],
  mergeRules: {
    boundary_plus_equivalence: "keep_boundary",
    exception_covering_normal: "keep_exception"
  }
}
```

**去重输出：**
```javascript
{
  originalCount: 45,
  afterDeduplication: 28,
  removed: [
    { id: "TC-003", reason: "subset_duplicate", absorbedBy: "TC-001" }
  ],
  finalCases: [
    // 去重、合并后的唯一测试用例
  ]
}
```

**最终输出格式：**
```markdown
## 测试用例：TC-001
**功能：** 邮箱登录
**模块：** 用户认证
**生成器：** 等价类（正向）

### 前置条件
- 用户已注册邮箱 test@example.com
- 用户知道正确密码

### 测试步骤
1. 导航到 /login
2. 在邮箱字段输入 "test@example.com"
3. 在密码字段输入 "CorrectPassword123"
4. 点击"登录"按钮

### 预期结果
- 用户重定向到 /dashboard
- 显示"欢迎回来！"消息

### 测试类型
- 正向：用有效凭证登录

### 需求来源
| 来源文件 | 行号 | 原始需求文本 |
|----------|------|-------------|
| `requirements/auth-prd.md` | 45-48 | "用户应能使用邮箱和密码登录系统，登录成功后跳转到仪表板" |
| `requirements/auth-prd.md` | 52 | "邮箱格式需符合标准 email 格式规范" |

### 生成来源
- 等价划分（有效邮箱格式）← 来源：行 45-48
- 边界值（标准长度）← 来源：行 52
```

---

#### 5. 自动化可行性分析器

**用途：** 分析每个功能测试用例的自动化可行性。

**自动化等级：**
```javascript
{
  level: "automatable" | "partial" | "manual",
  reasoning: "为什么是这个等级？",
  automatableParts: ["步骤1", "步骤2"],
  needsHumanParts: ["步骤3 - 视觉验证"],
  automationHints: ["使用模拟API", "设置测试数据库"]
}
```

**判断标准：**
| 等级 | 标准 |
|------|------|
| 🤖 `automatable` | 所有步骤可自动化，无需视觉/人工验证 |
| ⚠️ `partial` | 核心步骤可自动化，但需人工设置或最终验证 |
| 👤 `manual` | 需人工观察、物理设备或复杂设置 |

---

#### 6. 自动化脚本生成器

**用途：** 生成特定框架的测试代码。

**支持的框架：**
| 测试类型 | 框架 | 说明 |
|----------|------|------|
| Web E2E 测试 | Playwright | 浏览器自动化、页面交互 |

**生成流程：**
1. 获取已确认的功能测试用例
2. 根据用例类型和自动化等级生成 Playwright 代码：
   - 场景流测试用例 → Playwright E2E 代码
   - 跨模块测试用例 → Playwright E2E 代码
3. 对于 `partial` 等级的用例：
   - 生成自动化代码部分
   - 标记需要人工验证的部分
4. 对于 `manual` 用例，在文档中说明执行步骤

**输出：**
```javascript
{
  unitTestFile: "auth.test.ts",
  e2eTestFile: "auth.e2e.spec.ts",
  cases: [
    {
      id: "TC-001",
      name: "should login with valid email",
      testType: "unit",
      status: "automatable",
      code: `
        test('should login with valid email', async () => {
          // Setup
          const mockLogin = jest.fn().mockResolvedValue({ success: true });

          // Execute
          const result = await login('test@example.com', 'password');

          // Verify
          expect(result.success).toBe(true);
        });
      `,
      humanNotes: null
    },
    {
      id: "TC-010",
      name: "complete purchase flow",
      testType: "e2e",
      status: "automatable",
      code: `
        test('complete purchase flow', async ({ page }) => {
          // Navigate to catalog
          await page.goto('/catalog');
          await page.click('[data-testid="product-1"]');

          // Add to cart
          await page.click('[data-testid="add-to-cart"]');
          await expect(page.locator('[data-testid="cart-count"]')).toHaveText('1');

          // Proceed to checkout
          await page.click('[data-testid="checkout-btn"]');
          await page.fill('[data-testid="payment-card"]', '4242424242424242');

          // Complete purchase
          await page.click('[data-testid="pay-btn"]');
          await expect(page.locator('[data-testid="order-confirmation"]')).toBeVisible();
        });
      `,
      humanNotes: null
    },
    {
      id: "TC-015",
      name: "verify welcome message visibility",
      testType: "e2e",
      status: "partial",
      code: `
        test('verify welcome message after login', async ({ page }) => {
          // Automated part
          await page.goto('/login');
          await page.fill('[name="email"]', 'test@example.com');
          await page.fill('[name="password"]', 'password123');
          await page.click('[data-testid="login-btn"]');
          await expect(page).toHaveURL('/dashboard');

          // HUMAN VERIFICATION NEEDED:
          // - Verify "Welcome back, User!" message is visible
          // - Check dashboard layout renders correctly
          // - Confirm notification bell icon shows
        });
      `,
      humanNotes: "需要人工验证页面视觉元素是否正确显示"
    }
  ]
}
```

---

#### 7. 输出格式化器

**用途：** 以适当格式呈现结果。

**混合输出模式：**
- **终端：** 摘要表格、关键指标、确认提示
- **报告文件：** 详细 Markdown 报告，包含：
  - 执行摘要
  - 需求概览
  - 功能测试用例（全部）
  - 自动化脚本（按自动化等级标记）
  - 人工测试用例（分离）

**报告位置：** `reports/testing-agent/YYYY-MM-DD-<task-type>.md`

---

## 用户交互模式

### 模式一：需求优先测试

```
用户: /test generate for requirements/auth-prd.md
  → 意图: parse
  → 输出: 解析后的需求，包含模块分解
  → 如有需要则澄清（模糊项）
  → 展示功能测试用例供审核
  → 等待确认
  → 生成带自动化标记的自动化脚本
```

### 模式二：直接功能用例生成

```
用户: /test functional for "login with email"
  → 意图: functional
  → 直接生成功能测试用例
  → 展示供用户审核
```

### 模式三：需求问答

```
用户: checkout 模块需要哪些测试？
  → 意图: query
  → 输出: 建议的测试用例列表

用户: 澄清注册功能的密码要求
  → 意图: clarify
  → 输出: 提出具体的澄清问题
```

---

## 功能需求

### FR-1: 需求解析

| ID | 需求 | 优先级 |
|----|------|--------|
| FR-1.1 | 解析包含多个模块的大型 markdown 文件 | 必须 |
| FR-1.2 | 提取功能、验收标准、边界条件 | 必须 |
| FR-1.3 | 构建结构化需求树 | 必须 |
| FR-1.4 | 识别不清晰/模糊的项 | 必须 |
| FR-1.5 | 支持多种需求格式 | 应该 |

### FR-2: 需求澄清

| ID | 需求 | 优先级 |
|----|------|--------|
| FR-2.1 | 检测模糊需求 | 必须 |
| FR-2.2 | 生成有针对性的澄清问题 | 必须 |
| FR-2.3 | 尽可能支持多选答案 | 应该 |
| FR-2.4 | 记录澄清内容 | 必须 |

### FR-3: 功能测试用例生成

| ID | 需求 | 优先级 |
|----|------|--------|
| FR-3.1 | 生成人工可读的测试用例 | 必须 |
| FR-3.2 | 包含前置条件、步骤、预期结果 | 必须 |
| FR-3.3 | 使用专门的子生成器处理不同用例类型 | 必须 |
| FR-3.4 | 支持等价划分（正向/反向） | 必须 |
| FR-3.5 | 支持边界值分析 | 必须 |
| FR-3.6 | 支持异常/错误场景生成 | 必须 |
| FR-3.7 | 支持状态转换测试 | 必须 |
| FR-3.8 | 支持场景流（单模块内端到端流程） | 必须 |
| FR-3.9 | 支持决策表（复杂业务规则） | 必须 |
| FR-3.10 | 支持安全测试生成 | 必须 |
| FR-3.11 | 支持性能测试生成 | 应该 |
| FR-3.12 | 对生成的测试用例去重（单模块内） | 必须 |
| FR-3.13 | 映射到源代码模块/函数 | 应该 |
| FR-3.14 | 按模块/功能分组 | 必须 |

### FR-3.5: 需求关联分析（跨模块）

| ID | 需求 | 优先级 |
|----|------|--------|
| FR-3.5.1 | 分析模块间的依赖关系，构建依赖图 | 必须 |
| FR-3.5.2 | 从需求文本中挖掘隐含需求场景 | 必须 |
| FR-3.5.3 | 生成跨模块的关键路径场景 | 必须 |
| FR-3.5.4 | 生成跨模块的错误传导场景 | 必须 |
| FR-3.5.5 | 生成跨模块的数据同步场景 | 应该 |
| FR-3.5.6 | 生成跨模块的并发一致性场景 | 应该 |
| FR-3.5.7 | 跨模块测试用例去重 | 必须 |

### FR-4: 自动化可行性分析

| ID | 需求 | 优先级 |
|----|------|--------|
| FR-4.1 | 分析每个测试用例的自动化潜力 | 必须 |
| FR-4.2 | 分类为 automatable/partial/manual | 必须 |
| FR-4.3 | 解释分类原因 | 必须 |
| FR-4.4 | 为部分可自动化的用例建议自动化方法 | 应该 |

### FR-5: 自动化脚本生成

| ID | 需求 | 优先级 |
|----|------|--------|
| FR-5.1 | 生成 Playwright 代码（Web E2E） | 必须 |
| FR-5.2 | 遵循项目约定的模式和规范 | 必须 |
| FR-5.3 | 应用适当的 page object 模式 | 必须 |
| FR-5.4 | 在输出中标记自动化等级 | 必须 |
| FR-5.5 | 分离仅人工测试用例 | 必须 |

### FR-6: 报告生成

| ID | 需求 | 优先级 |
|----|------|--------|
| FR-6.1 | 生成 Markdown 报告文件 | 必须 |
| FR-6.2 | 包含所有功能测试用例 | 必须 |
| FR-6.3 | 包含生成的自动化脚本 | 必须 |
| FR-6.4 | 清晰标记自动化等级 | 必须 |
| FR-6.5 | 创建摘要部分 | 必须 |

---

## 非功能需求

| ID | 需求 | 说明 |
|----|------|------|
| NFR-1 | 处理长达 10,000 行的需求文档 | 全面解析大型文档 |
| NFR-2 | 支持 monorepo 项目结构 | 多个 `package.json` 位置 |
| NFR-3 | 通过 `testing-agent.config.js` 可配置 | 覆盖默认值 |
| NFR-4 | 任何生成前必须先澄清 | 永不跳过澄清 |
| NFR-5 | 自动化前必须用户确认 | 两阶段是强制性的 |
| NFR-6 | 对话状态必须持久化 | 支持会话中断和恢复 |
| NFR-7 | 会话恢复后从断点继续 | 不丢失任何已澄清的内容 |

---

## 配置 Schema

```javascript
// testing-agent.config.js
module.exports = {
  // 项目特定的测试约定
  conventions: {
    testDirectory: "__tests__",  // 或 "tests"，或按包
    fileSuffix: ".test",          // 或 ".spec"
    mockDirectory: "__mocks__"
  },

  // 源文件位置
  sources: {
    include: ["src/**/*.ts", "lib/**/*.ts"],
    exclude: ["**/*.d.ts", "**/node_modules/**"]
  },

  // 需求解析
  requirements: {
    // 识别可测试项的模式
    featureKeywords: ["should", "must", "shall", "when", "if"],
    boundaryKeywords: ["empty", "null", "undefined", "max", "min", "first", "last"],
    // 需求文档的文件模式
    docPatterns: ["**/requirements/**/*.md", "**/*spec*.md", "**/*prd*.md"]
  },

  // 澄清行为
  clarification: {
    askBeforeGeneration: true,    // 始终澄清模糊项
    maxQuestionsPerRound: 3       // 不要让用户应接不暇
  },

  // 两阶段工作流
  workflow: {
    // 功能用例必须在自动化前确认
    requireConfirmation: true,
    // 小改动可自动生成，大改动需确认
    autonomyThresholds: {
      newTestCases: 5,            // < 5 个用例 = 自动生成
      newFiles: 1                  // 新文件 = 需确认
    }
  },

  // 报告输出
  reports: {
    directory: "reports/testing-agent",
    format: "markdown"
  }
}
```

---

## 文件结构

```
software-testing-agent/
├── SKILL.md                    # 主技能文件
├── README.md                   # 使用文档
├── src/
│   ├── router.js              # 意图路由逻辑
│   ├── requirements/
│   │   ├── parser.js          # 解析需求文档
│   │   ├── extractor.js       # 提取可测试项
│   │   ├── clarifier.js       # 处理模糊需求
│   │   ├── session.js         # 对话状态持久化与恢复
│   │   └── association.js     # 需求关联分析器
│   │       ├── dependency.js  # 模块依赖分析
│   │       ├── implicit.js    # 隐含需求挖掘
│   │       └── crossModule.js # 跨模块场景生成
│   ├── functional/
│   │   ├── index.js           # FCG 编排器
│   │   ├── equivalence.js     # 等价类生成器
│   │   ├── boundary.js        # 边界值生成器
│   │   ├── exception.js       # 异常场景生成器
│   │   ├── state.js           # 状态转换生成器
│   │   ├── scenario.js        # 场景流生成器
│   │   ├── decisionTable.js   # 决策表生成器
│   │   ├── security.js        # 安全测试生成器
│   │   ├── performance.js     # 性能测试生成器
│   │   ├── deduplicator.js   # 去重引擎
│   │   └── templates/         # 用例模板
│   ├── automation/
│   │   ├── analyzer.js        # 分析自动化可行性
│   │   ├── playwright.js     # Playwright E2E 代码生成
│   │   └── markers.js        # 标记自动化等级
│   ├── formatter/
│   │   ├── terminal.js        # 终端输出
│   │   └── report.js          # 报告生成
│   └── config.js              # 配置加载器
├── sessions/                   # 对话状态存储目录
│   └── clarify-session-*.json  # 澄清会话状态文件
└── testing-agent.config.js     # 默认配置
```

---

## 内部 API 设计

### `router.parseIntent(input)`

**输入：** 用户消息字符串

**输出：**
```javascript
{
  intent: "parse" | "clarify" | "functional" | "automate" | "analyze" | "query",
  confidence: 0.0-1.0,
  parameters: {
    target?: string,        // 文件路径或模块名
    scope?: string,         // "file" | "module" | "project"
    options?: object
  }
}
```

### `requirements.parse(docPath)`

**输入：** 需求文档路径

**输出：**
```javascript
{
  modules: [{ name, features: [...] }],
  ambiguousItems: [{ module, feature, unclear }],
  statistics: { totalFeatures, totalAC, ambiguityScore }
}
```

### `requirements.clarify(ambiguousItems)`

**输入：** 模糊项列表

**输出：**
```javascript
{
  clarifications: [
    {
      question: "最大登录尝试次数是多少？",
      options: ["3次", "5次", "无限次"],
      selected: null  // 用户填写
    }
  ]
}
```

### `functional.generate(confirmedRequirements)`

**输入：** 已澄清的需求

**输出：**
```javascript
{
  testCases: [
    {
      id: "TC-001",
      module: "认证",
      feature: "登录",
      generatorType: "equivalence",        // 创建此用例的生成器
      subCategory: "positive",               // 等价类子类型
      preconditions: [...],
      steps: [...],
      expectedResult: "...",
      tags: ["critical", "p0"],
      sourceRequirement: "F-001",           // 映射到源需求 ID
      
      // 需求来源追溯
      requirementSource: {
        file: "requirements/auth-prd.md",
        lines: [45, 46, 47, 48],          // 原始需求文本所在行号
        rawText: "用户应能使用邮箱和密码登录系统，登录成功后跳转到仪表板",
        generator: "equivalence"            // 由哪个生成器基于此来源生成
      }
    }
  ],
  // 去重报告
  deduplication: {
    originalCount: 50,
    finalCount: 32,
    removed: [
      { id: "TC-010", reason: "subset_duplicate", absorbedBy: "TC-003" }
    ]
  },
  requiresConfirmation: true
}
```

### `automation.analyze(functionalCases)`

**输入：** 功能测试用例

**输出：**
```javascript
{
  analysis: [
    {
      caseId: "TC-001",
      level: "automatable",
      reasoning: "所有步骤可通过API调用",
      automatableParts: ["步骤1-4"],
      needsHumanParts: null
    }
  ]
}
```

### `automation.generate(cases, analysis)`

**输入：** 功能用例 + 自动化分析

**输出：**
```javascript
{
  e2eTests: [
    {
      caseId: "TC-010",
      framework: "playwright",
      code: "test('...', async ({ page }) => { ... })",
      status: "automatable",
      humanNotes: null
    }
  ],
  manualCases: [
    {
      caseId: "TC-005",
      status: "manual",
      instructions: "...",
      humanNotes: "需要物理设备交互"
    }
  ]
}
```

---

## 错误处理

| 错误场景 | 处理方式 |
|----------|----------|
| 需求文档未找到 | 提示用户提供正确路径 |
| 未找到可测试项 | 报告并建议改进文档格式 |
| 模糊项过多（>10） | 按模块分组，分批澄清 |
| 未检测到测试框架 | 提示用户指定或通过 package.json 自动检测 |
| AI 生成失败 | 回退到基于模板的生成 |
| 配置无效 | 使用默认值，警告用户 |

---

## Phase 1 范围外

- Playwright 底层脚本细节 - 只生成用例级 E2E 脚本，不涉及底层 API 调用细节
- 测试执行编排 - 不执行测试，只生成用例
- CI/CD 集成 - 不做 CI/CD 集成
- 快照测试 - 不生成快照测试
- Mock 文件生成 - 不自动生成 mock 文件（由开发者手动维护）
- 代码覆盖率分析（独立功能）- 覆盖率分析是独立功能

---

## 未来增强

- FR-7: 测试执行与失败分析
- FR-8: 性能分析（慢测试检测）
- FR-9: 变异测试集成
- FR-10: 属性测试（模糊测试）
- FR-11: 现有代码覆盖率缺口分析

---

## 附录：参考技能

本设计遵循以下技能建立的模式：

- `brainstorming` - 澄清优先方法、用户确认环节
- `systematic-debugging` - 结构化分析方法
- `test-driven-development` - 测试用例质量标准
