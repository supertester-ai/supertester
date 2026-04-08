---
name: automation-analysis
description: Use when analyzing test case automation feasibility - classifies each test case as automatable, partial, or manual based on Playwright capabilities
---

# Skill 4: 自动化可行性分析

## Iron Law

> **未经用户确认的用例不准分析自动化可行性。**

## 前置条件

- Phase 3 (test-case-generation) Status: **complete**
- 用户已确认功能测试用例

## 流程

```
functional-cases.md (已确认)
    |
    v
逐个分析每个 TC-xxx
    |
    v
标记: automatable / partial / manual
    |
    v
生成 automation-analysis.md
    |
    v
更新 test_plan.md Phase 4 -> complete
```

## 自动化等级判断标准

| 等级 | 标准 | Playwright 可行性 | 示例 |
|------|------|------------------|------|
| `automatable` | 所有步骤可通过 Playwright API 完成，无需视觉/人工验证 | 完全可行 | 表单提交、页面跳转、API 调用、DOM 断言 |
| `partial` | 核心步骤可自动化，但某些验证需人工 | 部分可行 | UI 视觉验证、布局检查、复杂交互反馈 |
| `manual` | 无法通过 Playwright 完成，需人工观察或物理设备 | 不可行 | 邮件内容、短信验证、物理设备、主观体验 |

## 判断指南

### automatable 信号
- 页面导航和 URL 验证
- 表单填写和提交
- DOM 元素存在/内容验证
- HTTP 状态码检查
- Cookie/LocalStorage 验证
- 文件下载（验证触发）
- 数据库状态（通过 API）

### partial 信号
- 需要视觉验证（样式、布局、动画）
- 需要验证 PDF/图片内容
- 需要验证第三方嵌入内容
- 需要验证音频/视频播放
- 拖拽交互的精确位置验证

### manual 信号
- 接收实际邮件/短信
- 物理设备交互（扫码、NFC）
- 主观用户体验评估
- 跨浏览器视觉一致性
- 无障碍辅助工具交互
- 需要第三方系统的人工操作

## 输出格式 (automation-analysis.md)

```markdown
# 自动化可行性分析

## 统计
- 总用例: N
- automatable: X (Y%)
- partial: X (Y%)
- manual: X (Y%)

## 详细分析

| 用例ID | 名称 | 等级 | 理由 | 可自动化部分 | 需人工部分 |
|--------|------|------|------|-------------|-----------|
| TC-001 | [名称] | automatable | [理由] | 步骤 1-4 | -- |
| TC-015 | [名称] | partial | [理由] | 步骤 1-3 | 步骤 4: [描述] |
| TC-020 | [名称] | manual | [理由] | -- | 全部 |

## automatable 用例清单
[ID 列表，供 automation-scripting 使用]

## partial 用例清单
[ID 列表 + 可自动化步骤范围]

## manual 用例清单
[ID 列表，将输出到 manual-cases.md]
```

## 2-Action Rule 落地

- 分析了 2 个用例 -> 立即追加到 automation-analysis.md

## Red Flags

| 如果你在想... | 现实是... |
|--------------|------------|
| "全部标记为 automatable" | 不诚实的标记会导致脚本生成后无法运行 |
| "跳过分析直接生成脚本" | 没有分析就无法正确处理 partial 和 manual |
| "partial 太麻烦，算 manual" | partial 的自动化部分仍有价值 |
