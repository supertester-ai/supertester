# 任务: 根据审查意见修订 Patch

你要根据审查意见修订 patch，保留修改意图但消除通用性问题。

## 原始 patch

```json
{{ original_patch }}
```

## 审查意见

```json
{{ review_issues }}
```

## 要求

- 保留 analysis (差距识别不变)
- 按审查建议重写 patches 中的 diff
- 消除业务术语/硬编码值/过拟合规则
- 保持改进意图 (仍然解决原本的差距)

## 输出

与原始 patch 相同的 JSON 结构 (含 analysis + patches + skipped_gaps)。

只输出 JSON。
