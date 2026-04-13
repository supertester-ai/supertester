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
- 提取所有 F-xxx 功能点
- 完整标注 8 类测试资产 (内容/规则/集成/状态数据/约束/证据/多语言/Prompt)
- 为每个功能点标注证据类型
- 标注特性标签 (content_fidelity / process_feedback / interruption_recovery / visual_asset / contract_content / business_outside_prd)

直接输出 Markdown 内容，不要添加 ```md 包裹。
