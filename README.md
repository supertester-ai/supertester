# Software Testing Agent

AI 驱动的软件测试智能体插件 - 从需求文档自动生成功能测试用例和 Playwright E2E 自动化脚本。

## ✨ 核心特性

- **📋 需求优先** - 解析大型需求文档（Markdown），在生成测试前充分理解需求
- **💬 智能澄清** - 检测模糊需求，发起澄清对话，支持会话中断恢复
- **🔗 跨模块测试** - 分析模块依赖关系，挖掘隐含需求场景，生成跨模块关联测试
- **🧠 智能生成** - 根据需求特性自动选择合适的测试用例生成策略
- **🤖 Playwright E2E** - 生成高质量的 Playwright 自动化脚本
- **📊 自动化标记** - 每个用例标记自动化等级（automatable / partial / manual）
- **📝 用例追溯** - 每个测试用例可追溯到原始需求文件和行号

## 🎯 测试方法覆盖

| 生成器 | 测试方法 | 适用场景 |
|--------|----------|----------|
| 等价类生成器 | 等价划分 | 正向/反向输入用例 |
| 边界值生成器 | 边界分析 | 空值、最大/最小值、溢出 |
| 异常场景生成器 | 错误处理 | 网络异常、系统错误、安全异常 |
| 状态转换生成器 | 状态机测试 | 状态变迁、会话状态 |
| 场景流生成器 | 端到端流程 | 单模块内用户操作流程 |
| 决策表生成器 | 决策表测试 | 复杂业务规则、多条件组合 |
| 安全测试生成器 | 安全测试 | 注入、认证、数据保护 |
| 性能测试生成器 | 非功能测试 | 负载、压力、响应时间 |

## 📁 项目结构

```
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
```

## 🚀 快速开始

### 安装

**方式一：克隆仓库**

```bash
git clone https://gitcode.com/orion-c/TestingAgent.git
cd TestingAgent
```

**方式二：安装为 oh-my-opencode 插件**

```bash
# 在你的项目目录创建插件目录
mkdir -p .claude/skills/testing-agent

# 复制技能文件
cp /path/to/TestingAgent/SKILL.md .claude/skills/testing-agent/
cp -r /path/to/TestingAgent/src .claude/skills/testing-agent/
cp /path/to/TestingAgent/testing-agent.config.js ./
```

**方式三：使用 npm 包**

```bash
npm install @orion-c/testing-agent
```

### 初始化配置

在项目根目录创建 `testing-agent.config.js`：

```javascript
// testing-agent.config.js
module.exports = {
  conventions: {
    testDirectory: "__tests__",
    fileSuffix: ".test"
  },
  requirements: {
    docPatterns: ["**/requirements/**/*.md", "**/*spec*.md"]
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

### 使用方式

```bash
# 解析需求文档并开始澄清
/test parse requirements/auth-prd.md

# 继续澄清对话
/test clarify

# 生成功能测试用例
/test functional for "登录模块"

# 生成自动化脚本
/test automate

# 查询测试建议
/test query "checkout 模块需要哪些测试？"
```

### 配置文件

```javascript
// testing-agent.config.js
module.exports = {
  // 项目测试约定
  conventions: {
    testDirectory: "__tests__",
    fileSuffix: ".test"
  },
  
  // 需求文档模式
  requirements: {
    docPatterns: ["**/requirements/**/*.md", "**/*spec*.md"]
  },
  
  // 澄清行为
  clarification: {
    askBeforeGeneration: true,
    maxQuestionsPerRound: 3
  },
  
  // 两阶段工作流
  workflow: {
    requireConfirmation: true
  }
}
```

## 📖 工作流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   需求解析   │ -> │   需求澄清   │ -> │  需求关联   │
└─────────────┘    └─────────────┘    │   分析     │
                                       └──────┬──────┘
                                              │
                                              ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   用户确认   │ <- │  功能用例   │ <- │ 智能生成器  │
│             │    │   生成     │    │   选择     │
└─────────────┘    └─────────────┘    └─────────────┘
                      │
                      ▼
               ┌─────────────┐
               │  自动化可行性 │
               │    分析     │
               └──────┬──────┘
                      │
                      ▼
               ┌─────────────┐
               │ Playwright  │
               │  E2E 脚本   │
               └─────────────┘
```

## 🔧 技术栈

- **运行时**: Node.js
- **AI 模型**: Claude (通过 API)
- **测试框架**: Playwright
- **输出格式**: Markdown 报告

## 📚 设计文档

详细的设计规格说明书请参考 [docs/design.md](./docs/design.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](./LICENSE)

---

**Built with ❤️ for better software testing**
