# Test Report: [Module Name]

## Executive Summary
- **Generated:** YYYY-MM-DD
- **Requirement Doc:** [filename]
- **Total Test Cases:** N
- **Automation Rate:** X%
- **Review Status:** All phases reviewed
- **Coverage Summary:** [一句话总结行为覆盖与证据覆盖情况]

## Requirement Coverage

| Req ID | Name | Test Cases | Coverage |
|--------|------|-----------|----------|
| F-001 | [name] | TC-001, TC-002 | Full |
| F-002 | [name] | TC-010 | Full |
| IR-001 | [name] | TC-005 | Full |

### Coverage Statistics
- Total Requirements: N
- Fully Covered: N (X%)
- Partially Covered: N (X%)
- Not Covered: N (X%)

## Coverage Dimensions

| Dimension | Status | Evidence | Notes |
|-----------|--------|----------|-------|
| Behavior | [covered/partial/missing] | [source] | [notes] |
| Rules / Enumerations | [covered/partial/missing] | [source] | [notes] |
| Content | [covered/partial/missing] | [source] | [notes] |
| State / Data | [covered/partial/missing] | [source] | [notes] |
| Integration | [covered/partial/missing] | [source] | [notes] |
| Evidence Chain | [covered/partial/missing] | [source] | [notes] |

## Critical Test Assets

| Asset Type | Description | Coverage | Handling |
|------------|-------------|----------|----------|
| [Rules / Content / State / Contract / Integration] | [asset] | [covered/partial/missing] | [automated/manual/preserved] |

## Functional Test Cases Summary

### Module: [Module Name]

| TC ID | Name | Generator | Priority |
|-------|------|-----------|----------|
| TC-001 | [name] | Equivalence Class | High |
| TC-002 | [name] | Boundary Value | High |

**Total by module:** N test cases

## Automation Analysis

| Level | Count | Percentage |
|-------|-------|-----------|
| automatable | N | X% |
| partial | N | X% |
| manual | N | X% |

### Manual Retention Notes
- [为什么某些测试资产保留为人工或半自动]

## Cross-Module Scenarios

| ID | Name | Type | Modules | Status |
|----|------|------|---------|--------|
| CMS-001 | [name] | critical_path | [modules] | Covered |

## Automation Scripts

| Script File | Module | Test Cases | Count |
|-------------|--------|-----------|-------|
| auth.e2e.spec.ts | Authentication | TC-001, TC-002, TC-003 | 3 |

## Manual Test Cases

| TC ID | Name | Reason |
|-------|------|--------|
| TC-020 | [name] | [why manual] |

## Gap Analysis

### Covered
- [已明确覆盖的能力、规则或资产]

### Preserved Manual Coverage
- [虽未脚本化但已被人工用例明确保留的资产]

### Missing or Partial
- [当前仍缺失或仅部分覆盖的维度、规则、资产]

### Recommended Next Actions
1. [补强建议]
2. [补强建议]

## Traceability Matrix

| Requirement | Test Cases | Script | Automation | Status |
|-------------|-----------|--------|------------|--------|
| F-001 | TC-001, TC-002 | auth.e2e.spec.ts | automatable | covered |

## Review History

| Phase | Date | Reviewer | Result | Issues | Record |
|-------|------|----------|--------|--------|--------|
| Phase 2 | YYYY-MM-DD | test-reviewer | passed | 0 CRITICAL | review-association-*.md |
| Phase 3 | YYYY-MM-DD | test-reviewer | passed | 0 CRITICAL | review-testcases-*.md |
| Phase 5 | YYYY-MM-DD | test-reviewer | passed | 0 CRITICAL | review-scripts-*.md |

## Notes
- [Any additional observations or recommendations]
