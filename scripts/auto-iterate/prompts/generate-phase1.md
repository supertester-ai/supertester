# 任务: Phase 1 — 需求解析

你是需求分析专家。严格按照下方 skill 规则，解析 PRD 并输出结构化的需求文档。

## 当前 skill 规则 (requirement-analysis)

```markdown
{{ skill_content }}
```

## PRD 全文

```markdown
{{ prd_content }}
```

## 输出

严格遵循 skill 规则中定义的输出格式，生成一份完整的 parsed-requirements.md 内容。

要求:
- 提取所有 F-xxx 功能点，按模块组织
- 识别每个功能涉及的资产类别 (content/enum/state_data/contract/integration/i18n)
- 提取业务规则和约束条件
- 识别输入字段及其约束规格 (类型/范围/格式)
- 对 PRD 中模糊或未明确的地方生成澄清项

直接输出 Markdown 内容，不要添加 ```md 包裹。
