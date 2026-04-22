# 任务: 从人工参考用例反向提取验证基准

你是测试分析专家。给你一组人工编写的测试用例 (JSON)，请反向提取三层验证基准，用于后续评估 AI 生成产物的质量。

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

### 1. Phase 1 基准: 需求解析应正确理解的内容

Phase 1 评的是"需求是否被正确理解"，不是"测试用例是否完整"。
请在**规则模式级别**概括，不要列出具体值或具体字符串。

#### 1a. 功能识别 (features)

列出测试用例覆盖的所有功能点，概括为功能名:
- 功能名应可从 PRD 中找到对应描述
- 子功能应归属到父功能下
- 不要写具体测试步骤

#### 1b. 业务规则 (rules)

从测试步骤中提取隐含的业务规则，**概括为规则模式**:
- GOOD: "存在基于失败次数的账号锁定机制"
- BAD:  "3分钟内5次错误触发5分钟锁定"
- GOOD: "不同会员等级有差异化的功能配额"
- BAD:  "免费5次/月，付费100次/月"
- GOOD: "异步任务存在权益预扣和异常返还规则"
- BAD:  "PENDING预扣1次，FAILED返还"

关键: 具体数值、字段名、状态码属于测试数据，不是规则模式。

#### 1c. 资产类别 (asset_categories)

标注该模块涉及的资产类别（只填类别名，不列具体条目）:
- `content`: 有需要验证的界面文案/提示语/邮件模板
- `enum`: 有需要完整覆盖的枚举列表/状态映射
- `state_data`: 有需要断言的数据库/缓存/会话状态
- `contract`: 有需要逐项验证的 prompt/schema/格式规范
- `integration`: 有外部系统交互（支付/邮件/第三方API）
- `i18n`: 有多语言/多地区差异

#### 1d. PRD 模糊点 (ambiguities)

找出测试用例中有明确处理但 PRD 中模糊或未写的地方:
- 描述模糊的**领域**（不写具体值）
- 期望的澄清方向

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
    "features": [
      { "name": "功能名", "sub_features": ["子功能1", "子功能2"] }
    ],
    "rules": [
      { "pattern": "规则模式概括（不含具体数值）", "scope": "适用的功能范围" }
    ],
    "asset_categories": ["content", "enum", "state_data"],
    "ambiguities": [
      { "area": "模糊领域描述", "direction": "期望的澄清方向" }
    ]
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
