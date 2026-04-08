---
name: automation-scripting
description: Use when generating Playwright E2E test scripts from confirmed test cases - generates code for automatable cases, marks partial cases, documents manual cases
---

# Skill 5: 自动化脚本生成

## Iron Law

> **只为已确认且标记为 automatable/partial 的用例生成脚本。**

<HARD-GATE>
manual 用例不生成代码，只生成文档化的执行步骤到 manual-cases.md。
生成的脚本必须经过 test-reviewer 审查后才能输出给用户。
</HARD-GATE>

## 前置条件

- Phase 4 (automation-analysis) Status: **complete**
- `.supertester/test-cases/automation-analysis.md` 已生成

## 流程

```
functional-cases.md + automation-analysis.md
    |
    v
按模块分组
    |
    +---> automatable 用例 -> 完整 Playwright 代码
    |
    +---> partial 用例 -> 部分代码 + HUMAN VERIFICATION 标记
    |
    +---> manual 用例 -> manual-cases.md
    |
    v
test-reviewer 审查 -> reviews/review-scripts-*.md
    |
    v
更新 test_plan.md Phase 5 -> complete
```

## 生成规则

### automatable 用例
- 生成完整的 Playwright 测试代码
- 包含完整的 Arrange-Act-Assert
- 每个断言对应测试步骤的预期结果

### partial 用例
- 自动化部分生成完整代码
- 需人工验证的部分添加注释标记:
  ```typescript
  // HUMAN VERIFICATION NEEDED:
  // - [需要人工验证的内容描述]
  ```

### manual 用例
- 不生成任何代码
- 写入 `.supertester/scripts/manual-cases.md`
- 包含详细的人工执行步骤

## 代码规范

### 文件组织
- 每个测试文件对应一个模块: `<module-name>.e2e.spec.ts`
- 使用 Page Object 模式组织页面交互
- 文件头部注释包含模块信息和生成时间

### 溯源注释
每个 test 必须标记溯源:
```typescript
// TC-001 | F-001 | <source-file>:<line-range>
test('should ...', async ({ page }) => {
  // ...
});
```

### 代码结构
```typescript
// Arrange - 准备测试数据和页面状态
await page.goto('/path');

// Act - 执行操作
await page.fill('[data-testid="input"]', 'value');
await page.click('[data-testid="button"]');

// Assert - 验证结果
await expect(page).toHaveURL('/expected');
await expect(page.locator('[data-testid="msg"]')).toContainText('expected');
```

### 选择器策略
优先级从高到低:
1. `data-testid` 属性: `[data-testid="login-btn"]`
2. ARIA role: `getByRole('button', { name: 'Login' })`
3. Text content: `getByText('Submit')`
4. CSS selector: 最后选择，标记为不稳定

### Playwright 最佳实践
详细参考见 @playwright-patterns.md

## 输出示例

### automatable 用例

```typescript
// auth.e2e.spec.ts
// Module: User Authentication
// Generated: YYYY-MM-DD
// Source: functional-cases.md

import { test, expect } from '@playwright/test';

// TC-001 | F-001 | auth-prd.md:45-48
test('should login with valid email', async ({ page }) => {
  // Arrange
  await page.goto('/login');

  // Act
  await page.fill('[data-testid="email-input"]', 'test@example.com');
  await page.fill('[data-testid="password-input"]', 'CorrectPassword123');
  await page.click('[data-testid="login-btn"]');

  // Assert
  await expect(page).toHaveURL('/dashboard');
  await expect(page.locator('[data-testid="welcome-msg"]'))
    .toContainText('Welcome');
});
```

### partial 用例

```typescript
// TC-015 | F-001 | auth-prd.md:52
test('should display welcome elements after login', async ({ page }) => {
  // Arrange & Act (automated)
  await page.goto('/login');
  await page.fill('[data-testid="email-input"]', 'test@example.com');
  await page.fill('[data-testid="password-input"]', 'password123');
  await page.click('[data-testid="login-btn"]');
  await expect(page).toHaveURL('/dashboard');

  // HUMAN VERIFICATION NEEDED:
  // - Verify welcome message styling is correct
  // - Check dashboard layout renders without visual glitches
  // - Confirm notification bell icon appears in correct position
});
```

### manual-cases.md

```markdown
# Manual Test Cases

## TC-020: Email Notification Verification
**Module:** Notifications
**Function:** F-010
**Reason:** Requires actual email receipt and content verification

### Execution Steps
1. Trigger password reset for user test@example.com
2. Check email inbox for test@example.com
3. Verify email subject: "Password Reset Request"
4. Verify email body contains reset link
5. Click reset link, verify it opens correct page
6. Verify link expires after 24 hours

### Expected Results
- Email received within 5 minutes
- Subject and body match template
- Reset link functional and expires correctly
```

## test-reviewer 审查维度

- 代码无语法错误
- 遵循 Playwright 最佳实践
- 选择器策略稳定 (data-testid > CSS)
- Arrange-Act-Assert 结构清晰
- 溯源注释完整 (TC-xxx | F-xxx)
- partial 用例的 HUMAN VERIFICATION 标记准确

## Red Flags

| 如果你在想... | 现实是... |
|--------------|------------|
| "为 manual 用例也生成代码" | 违反 Hard Gate，manual 只写文档 |
| "选择器用 CSS class 就好" | CSS class 容易变，优先用 data-testid |
| "不需要溯源注释" | 溯源是追溯链的关键环节 |
| "跳过审查" | 脚本必须经 test-reviewer 审查 |
