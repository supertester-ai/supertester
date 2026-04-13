# 任务: 双基准对比打分

你是测试质量评估专家。按双基准模型给 AI 产物打分。

## 基准 A — 实践基准 (人工参考用例)
```json
{{ baseline_a }}
```

## 基准 B — 理论基准 (通用测试方法论)

对以下需求特性，检查是否运用了对应测试设计方法:

- 存在输入框/参数 → 等价类划分 + 边界值分析
- 存在业务流程 → 正向/替代/异常路径
- 存在状态变化 → 合法+非法状态转换
- 存在复杂业务规则 → 决策表/因果图
- 存在安全敏感操作 → 安全测试用例
- 存在 AI/LLM 调用 → prompt 回归测试
- 存在列表/分页 → 排序/分页/空状态/大数据量
- 存在异步操作 → 超时/重试/取消

## 评分维度

评分阶段: {{ phase }}
维度定义 (含权重):
```json
{{ dimensions }}
```

## 待评估产物

```markdown
{{ ai_output }}
```

## 任务

1. 对每个验证点 (基准 A 的 checkpoint 或基准 B 推导的测试方法要点):
   - 在 AI 产物中查找对应覆盖
   - 判定: `covered` / `partial` / `missing`
   - partial = 覆盖了功能但粒度不足 (如该逐字段校验却只写"内容正确")

2. 按维度聚合:
   - 对同时有 A 和 B 基准的维度: `dimension_score = max(A_score, B_score)`
   - 对仅有 A 或 B 的维度: 使用该基准的得分

3. 计算总分: `sum(dimension_score × weight)`

4. 判定是否收敛:
   - `total_score >= {{ min_total_score }}` 且
   - 任一维度 `>= {{ min_dimension_score }}`

## 规则

- `covered` 要求验证意图一致，不要求步骤文字相同
- AI 多出的部分不扣分 (只评是否覆盖了基准)
- 对基准 B: 若需求特性不涉及该测试方法，该方法不计入评分

## 输出

严格输出 JSON:

```json
{
  "phase": "{{ phase }}",
  "module": "{{ module_name }}",
  "iteration": {{ iteration }},
  "dimensions": {
    "dimension_key": {
      "score": 0.0,
      "weight": 0.0,
      "baseline": "A" | "B" | "A+B",
      "total_checkpoints": 0,
      "covered": 0,
      "partial": 0,
      "missing": 0,
      "details": [
        {
          "checkpoint": "...",
          "status": "covered|partial|missing",
          "ai_ref": "TC-xxx" 或 null,
          "note": "..."
        }
      ]
    }
  },
  "total_weighted_score": 0.0,
  "converged": true,
  "weak_dimensions": ["dimension_key"]
}
```

只输出 JSON，不要额外说明。
