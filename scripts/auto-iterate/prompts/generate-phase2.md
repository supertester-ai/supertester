# 任务: Phase 2 — 需求关联分析

你是测试设计专家。严格按照下方 skill 规则，基于 Phase 1 产物分析模块关联。

## 当前 skill 规则 (requirement-association)

```markdown
{{ skill_content }}
```

## Phase 1 产物 (parsed-requirements.md)

```markdown
{{ parsed_requirements }}
```

## 输出

严格遵循 skill 规则输出三部分内容，用 `---SECTION---` 分隔:

SECTION 1 — module-dependencies.md
SECTION 2 — implicit-requirements.md
SECTION 3 — cross-module-scenarios.md

要求:
- 识别 6 类依赖 (功能/状态/证据/共享资源/中断恢复/历史列表)
- 挖掘 9 类隐含需求
- 生成 9 类跨模块场景

直接输出内容，section 间用 `---SECTION---` 分隔。
