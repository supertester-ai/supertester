# 任务: 从人工参考用例反向提取验证基准

你是测试分析专家。给你一组人工编写的测试用例 (JSON)，请反向提取三层验证基准，用于后续评估 AI 生成用例的质量。

## 输入

### 模块名
{{ module_name }}

### 参考用例 (JSON)
```json
{{ reference_cases_json }}
```

### 对应 PRD 片段
```markdown
{{ prd_slice }}
```

## 任务

### 1. Phase 1 基准: 需求解析应识别的资产

从每个测试步骤中提取:

- **content_assets**: 步骤中出现的具体文案、提示语、模板、错误信息、email/export 内容
- **enum_assets**: 步骤中出现的完整列表/矩阵/映射 (如黑名单、密码规则)
- **state_data_assets**: 涉及 DB 字段、额度变化、状态流转、缓存、日志的内容
- **contract_assets**: prompt 模板、schema、文件路径、输出格式规则
- **feature_tags**: 应标记的特性标签 (从以下选择):
  - `content_fidelity`: 内容保真 (文案、模板)
  - `process_feedback`: 过程态反馈 (loading、进度)
  - `interruption_recovery`: 中断恢复 (刷新、切换)
  - `visual_asset`: 视觉资产 (图片、Logo、样式)
  - `contract_content`: 合约内容 (prompt、schema)
  - `business_outside_prd`: PRD 外业务 (运营策略)

### 2. Phase 2 基准: 关联分析应发现的场景

识别:

- **cross_module_deps**: 步骤中隐含的跨模块依赖 (如 A 模块产生的记录出现在 B 模块列表)
- **interruption_scenarios**: 刷新/切换语言/跳转返回/重登录/网络中断等测试
- **history_list_interactions**: 排序/分页/滚动/空状态测试
- **implicit_requirements**: 参考用例覆盖但 PRD 未明确写出的需求
- **prd_external_items**: 运营策略、灰度、历史兼容等 PRD 外业务

### 3. Phase 3 基准: 用例级必须覆盖的验证点

按 step 粒度列出:

- **checkpoints**: 每个独立验证点，含:
  - `id`: 基准 ID (BP-{module}-{n})
  - `description`: 验证目标 (一句话)
  - `from_step`: 来自参考用例的 step_id
  - `fidelity_required`: 是否需要内容保真 (true/false)
  - `is_process_state`: 是否过程态验证 (true/false)
  - `is_visual_asset`: 是否视觉资产 (true/false)
  - `is_contract`: 是否合约验证 (true/false)
  - `is_interruption`: 是否中断恢复 (true/false)

## 输出

严格输出 JSON，结构:

```json
{
  "module_name": "...",
  "phase1": {
    "content_assets": ["..."],
    "enum_assets": [{"name": "...", "items": ["..."]}],
    "state_data_assets": ["..."],
    "contract_assets": ["..."],
    "feature_tags": ["content_fidelity", "..."]
  },
  "phase2": {
    "cross_module_deps": ["..."],
    "interruption_scenarios": ["..."],
    "history_list_interactions": ["..."],
    "implicit_requirements": ["..."],
    "prd_external_items": ["..."]
  },
  "phase3": {
    "checkpoints": [
      {
        "id": "BP-URL-1",
        "description": "...",
        "from_step": "step_id",
        "fidelity_required": false,
        "is_process_state": false,
        "is_visual_asset": false,
        "is_contract": false,
        "is_interruption": false
      }
    ]
  }
}
```

只输出 JSON，不要额外说明。
