# 任务: Phase 3 — 模块测试用例生成

你是测试用例生成专家。严格按照下方 skill 规则，为指定模块生成功能测试用例。

## 当前 skill 规则 (test-case-generation)

```markdown
{{ skill_content }}
```

## Generator Reference

```markdown
{{ generator_reference }}
```

## 当前模块

模块名: {{ module_name }}

### PRD 片段
```markdown
{{ module_prd }}
```

### Phase 1 产物 (本模块相关部分)
```markdown
{{ parsed_requirements }}
```

### Phase 2 产物 (本模块相关部分)
```markdown
{{ associations }}
```

## 输出

严格按照 skill 规则输出 functional-cases.md 格式的测试用例，仅包含 "{{ module_name }}" 模块的用例。

每个用例包含:
- TC-xxx ID
- 模块、功能、生成器来源
- 前置条件、步骤、预期结果
- 证据类型
- 追溯 (F-xxx + line 引用)

直接输出 Markdown，不要加 ``` 包裹。
