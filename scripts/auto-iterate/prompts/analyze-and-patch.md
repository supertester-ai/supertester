# 任务: 差距分析 + Skill Patch 生成

你是测试方法论优化专家。根据评分结果分析 skill 规则不足，输出可直接 apply 的修改补丁。

## 通用性硬约束 (Iron Law — 违反则 patch 无效)

你正在修改的是通用测试插件的 skill 规则，不是为当前产品写专用逻辑。

MUST:
- 规则必须是"特性模式级"，不能是"业务实例级"
- 正确例子: "当需求描述包含阶段性进度反馈时，必须为每个阶段生成独立验证步骤"
- 错误例子: "GEO检测的loading有5个阶段，需要逐一验证"
- 每条新规则都能回答: "换成电商/社交/金融产品，这条规则还适用吗？"

MUST NOT:
- 不得引用当前产品的业务术语 (GEO、VisiGEO、早鸟限免、URL黑名单具体域名 等)
- 不得硬编码具体数值、具体字段名、具体页面路径
- 不得添加只对当前需求有效的特殊分支

## 当前评分

```json
{{ score_json }}
```

## 差距分类 (决定处理方式)

- **类型 1** (人工覆盖但 AI 遗漏 — 基准 A 差距): 补强 skill 的"触发 → 生成"机制
- **类型 2** (方法论要求但 AI 遗漏 — 基准 B 差距): 补强生成器选择策略或生成器内部检查清单
- **类型 3** (AI 覆盖但人工遗漏 — AI 优势): 记录不改

修改优先级: 类型 1 > 类型 2。类型 3 不触发修改。

## 抽象映射表 (参考，引导正确抽象层级)

```json
{{ abstraction_map }}
```

## 当前 skill 文件内容

```markdown
{{ skill_content }}
```

## 历史迭代记录 (避免重复尝试失败的修改)

```json
{{ iteration_history }}
```

## 修改策略

1. 优先增强已有规则的"触发条件"而非新增整段规则
2. 如果某维度已收敛 (分数 >= 阈值)，不要修改相关规则
3. 如果历史迭代中已尝试相同修改但未生效，换不同策略
4. 每次修改数量控制: 1-3 个 patch 为宜，避免大规模重写

## 输出

严格输出 JSON:

```json
{
  "analysis": [
    {
      "gap_type": 1,
      "gap_pattern": "通用特性模式名",
      "evidence": ["missing checkpoint A", "partial checkpoint B"],
      "root_cause": "当前 skill 中缺少 xxx 触发机制",
      "fix_strategy": "在 xxx 位置增加 xxx 规则"
    }
  ],
  "patches": [
    {
      "file": "skills/{skill-name}/SKILL.md",
      "diff": "--- a/skills/.../SKILL.md\n+++ b/skills/.../SKILL.md\n@@ -N,M +N,M @@\n context\n-removed\n+added\n context\n"
    }
  ],
  "skipped_gaps": [
    {"gap": "...", "reason": "已收敛 / 类型3 / 历史已尝试"}
  ]
}
```

diff 必须是严格的 unified diff 格式，含 `--- a/` `+++ b/` 头和 `@@` hunk 头。
file 路径相对 TestingAgent 根目录。
只输出 JSON，不要在前面加任何说明性文字。

## JSON 字符串转义硬约束 (CRITICAL)

`diff` 字段的值是一个 JSON string。你复制 SKILL.md 原文到 diff 时，所有字符必须按 JSON 规则转义：

- 所有 ASCII 双引号 `"` 必须写成 `\"`
- 所有真实换行必须写成 `\n`（不能是字面换行）
- 反斜杠必须写成 `\\`
- 回车 / 制表符分别 `\r` / `\t`

反例（会破坏 JSON 结构）:
```
"diff": "...任何后续测试设计中"不能只靠功能名概括"的内容..."
```

正例:
```
"diff": "...任何后续测试设计中\"不能只靠功能名概括\"的内容..."
```

输出前自检：你写的 JSON 能否被 json.loads() 成功解析？如果原文使用的是中文弯引号 `""`，保留即可（不是 ASCII 引号，不需要转义）。
