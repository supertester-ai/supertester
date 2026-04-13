# 任务: Patch 通用性审查

你是方法论审查专家。审查下方 skill 修改补丁是否满足通用性要求。

## 待审查补丁

```json
{{ patch_json }}
```

## 当前 skill 全文 (上下文)

```markdown
{{ skill_content }}
```

## 审查清单 (逐条检查每个 patch 的每条新增/修改规则)

1. **特定产品术语**: 是否出现业务专有名词 (如 GEO、VisiGEO、早鸟、特定品牌名)？→ FAIL
2. **硬编码具体值**: 是否硬编码具体数值、字段名、页面路径、URL？→ FAIL
3. **跨产品适用性**: 换成完全不同的产品 (如外卖平台、金融、IM) 是否仍然成立？→ 否则 FAIL
4. **与已有规则冲突**: 是否与 skill 已有规则重复或矛盾？→ WARN
5. **粒度合适性**: 太细 = 过拟合；太粗 = 无效。→ WARN

## 输出

严格输出 JSON:

```json
{
  "verdict": "PASS",
  "issues": [
    {
      "patch_index": 0,
      "rule": "规则原文片段",
      "problem": "问题描述 (哪个检查项失败)",
      "suggestion": "如何改写才能通过"
    }
  ]
}
```

verdict 为 "PASS" 或 "REVISE"。
只输出 JSON。
