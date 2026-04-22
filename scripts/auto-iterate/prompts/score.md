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
   - partial = 覆盖了功能但粒度不足

2. 按维度聚合:
   - 对同时有 A 和 B 基准的维度: `dimension_score = max(A_score, B_score)`
   - 对仅有 A 或 B 的维度: 使用该基准的得分

3. 计算总分: `sum(dimension_score × weight)`

4. 判定是否收敛:
   - `total_score >= {{ min_total_score }}` 且
   - 任一维度 `>= {{ min_dimension_score }}`

## 阶段特定规则

{% if phase == "phase1" %}
### Phase 1 — 需求解析评分规则

你评的是"需求是否被正确理解"，不是"测试用例是否完整"。

**module_completeness**:
- covered: 模块被识别且有 ≥1 个 F-xxx 映射
- partial: 模块被提及但无 F-xxx，或只识别了部分子功能
- missing: 模块完全未出现

**rule_extraction**:
- covered: 规则被识别，关键条件被提及（如"有锁定机制"+"由失败次数触发"）
- partial: 规则部分识别（如知道"有配额"但不知"按等级区分"）
- missing: 规则未被识别
- 注意: 不要求匹配具体数值，只要规则模式被识别即可

**asset_awareness**:
- covered: 该资产类别被标注到对应功能
- partial: 未显式标注但功能描述中隐含意识
- missing: 完全未提及该类别
- 注意: 只评类别级（如"有文案资产"），不评具体条目（如具体 toast 文案）

**input_constraint_identification**:
- covered: 输入字段被识别且 ≥2 个约束维度被提及
- partial: 字段被提及但约束描述模糊
- missing: 字段未被识别为输入约束点
- 注意: 不要求匹配具体值（如"max 100"），只要规格被识别（如"有长度限制"）

**clarification_quality**:
- covered: PRD 模糊点被识别为澄清项，问题方向正确
- partial: 相关领域有澄清但问题不够精准
- missing: 模糊点未被识别

**关键**: 不要因为产物没列出具体文案字符串、具体枚举值、具体状态码而扣分 —— 那些是 Phase 3 的职责。
{% endif %}

{% if phase == "phase2" %}
### Phase 2 — 关联分析评分规则

- covered 要求验证意图一致，不要求步骤文字相同
- AI 多出的部分不扣分
{% endif %}

{% if phase == "phase3" %}
### Phase 3 — 用例生成评分规则

- covered 要求验证意图一致，不要求步骤文字相同
- AI 多出的部分不扣分
- 对基准 B: 若需求特性不涉及该测试方法，该方法不计入评分
{% endif %}

## 通用规则

- `covered` 要求验证意图一致，不要求步骤文字相同
- AI 多出的部分不扣分 (只评是否覆盖了基准)
- 对基准 B: 若需求特性不涉及该测试方法，该方法不计入评分

## 输出

严格输出 JSON **对象**（顶层必须是 `{...}`，不是数组）。

结构硬约束:
- 顶层必须包含 `phase`, `module`, `iteration`, `dimensions`, `total_weighted_score`, `converged`, `weak_dimensions` 七个字段
- `dimensions` 是一个对象（key 是维度名），每个维度下的 `details` 才是数组
- **不要只输出 details 数组**——必须包裹在完整的外层结构中

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
