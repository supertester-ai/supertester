---
name: requirement-analysis
description: Use when analyzing requirement documents - parses requirements, detects ambiguities, and conducts clarification dialogues before any test generation
---

# Skill 1: 需求解析与澄清

## Iron Law

> **不理解需求，就不准生成任何测试。**
> 如果你还没有完成需求解析和澄清，你不能调用 test-case-generation skill。

<HARD-GATE>
在所有模糊项澄清完毕之前，不准进入 requirement-association 阶段。
这适用于所有需求文档，无论看起来多清晰。
</HARD-GATE>

## 流程

```
需求文档
    |
    v
解析 Markdown -> 提取模块/功能/验收标准/边界条件
    |
    v
检测模糊项 -> [有模糊项?]
    |                |
    | 无             | 有
    v                v
写入 parsed-      发起澄清对话（一次一问，多选优先）
requirements.md       |
    |                v 每次交互后自动保存状态到 clarifications.json
    |                |
    |           [支持暂停/恢复]
    |                |
    |                v 所有项澄清完毕
    |                |
    +----------------+
    |
    v
更新 test_plan.md Phase 1 -> complete
更新 findings.md 需求发现
更新 progress.md 操作日志
```

## 步骤详解

### Step 1: 解析需求文档

读取用户指定的需求文档（Markdown 格式），提取：
- **模块**: 顶级功能模块
- **功能 (F-xxx)**: 每个模块下的具体功能
- **验收标准**: 每个功能的预期行为
- **边界条件**: 输入限制、数值范围
- **依赖**: 该功能依赖的其他模块/服务
- **来源**: 原始文档文件名 + 行号

### Step 2: 检测模糊项

使用 @clarification-patterns.md 中的模式检测模糊需求。常见模糊信号：
- 使用"等"、"之类"、"相关"等模糊词
- 缺少具体数值（"合理的时间"、"适当的长度"）
- 缺少错误处理描述
- 多种理解方式
- 隐含的前置/后置条件

### Step 3: 澄清对话

规则：
- **一次一问** — 不要一次抛出多个问题
- **多选优先** — 尽可能提供选项让用户选择
- **每次交互后保存** — 更新 clarifications.json
- **支持暂停** — 用户可以说"暂停"，下次说"继续澄清"时恢复

### Step 4: 写入产出文件

完成解析和澄清后：
1. 写入 `.supertester/requirements/parsed-requirements.md`
2. 写入 `.supertester/requirements/clarifications.json`（如有澄清）
3. 更新 `.supertester/test_plan.md` Phase 1 Status -> complete
4. 更新 `.supertester/findings.md` 需求发现
5. 更新 `.supertester/progress.md` 操作日志

## 2-Action Rule 落地

- 解析了 2 个模块 -> 立即写入 parsed-requirements.md
- 完成了 2 轮澄清 -> 立即更新 clarifications.json

## 输出格式

### parsed-requirements.md

```markdown
# 需求解析结果

## 来源文档
- <filename> (解析时间: YYYY-MM-DDTHH:MM:SSZ)

## 模块清单

### 模块: [模块名]

#### F-001: [功能名]
- **描述:** [功能描述]
- **验收标准:**
  - [标准1]
  - [标准2]
- **边界条件:** [边界1], [边界2]
- **依赖:** [依赖列表]
- **来源:** `<filename>` 行 XX-XX

## 统计
- 总模块: N
- 总功能: N
- 总验收标准: N
- 模糊项: N (已全部澄清)
```

### clarifications.json

```json
{
  "sessionId": "clarify-session-YYYYMMDD-NNN",
  "requirementDoc": "<filename>",
  "status": "completed|in_progress|paused",
  "createdAt": "ISO-8601",
  "updatedAt": "ISO-8601",
  "completedClarifications": [
    {
      "id": "CL-001",
      "relatedFeature": "F-001",
      "question": "问题描述",
      "answer": "用户回答",
      "answeredAt": "ISO-8601"
    }
  ],
  "pendingClarifications": [
    {
      "id": "CL-002",
      "relatedFeature": "F-001",
      "question": "问题描述",
      "status": "pending",
      "options": ["选项A", "选项B", "选项C"]
    }
  ],
  "pauseReason": ""
}
```

## 恢复机制

| 触发方式 | 行为 |
|---------|------|
| 用户说"继续澄清" | 读取最近的 clarifications.json，从 pendingClarifications 继续 |
| 用户说"恢复 CL-002" | 恢复指定澄清项 |
| 新会话启动 | SessionStart hook 检测到 clarifications.json 且 status != completed，提示用户 |

## Red Flags

| 如果你在想... | 现实是... |
|--------------|------------|
| "需求看起来很清楚" | 每个需求都有隐藏的模糊项，做完检测才知道 |
| "跳过澄清直接生成" | 违反 Iron Law，模糊需求生成的用例是浪费 |
| "用户催得急，先生成再说" | 返工成本远高于澄清成本 |
| "这个模糊项不影响测试" | 你不是产品经理，让用户决定 |
| "只有一两个模糊项，不需要走流程" | 一个模糊项可以衍生出多个错误用例 |

## 模糊项过多处理

如果检测到超过 10 个模糊项：
- 按模块分组
- 分批澄清，每批不超过 3 个问题
- 在 clarifications.json 中记录进度
