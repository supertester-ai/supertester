# Test Report: [Module Name]

## Executive Summary
- **Generated:** YYYY-MM-DD
- **Requirement Doc:** [filename]
- **Total Test Cases:** N
- **Automation Rate:** X%
- **Review Status:** [summary]
- **Coverage Summary:** [one-sentence summary of behavior and evidence coverage]

## Requirement Coverage

| Req ID | Name | Test Cases | Automation | Coverage |
|--------|------|-----------|------------|----------|
| F-001 | [name] | TC-001, TC-002 | automatable | Full |
| IR-001 | [name] | TC-005 | partial | Partial |
| CMS-001 | [name] | TC-020 | manual | Full |

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
| Content Fidelity | [covered/partial/missing] | [source] | [notes] |
| Process Feedback | [covered/partial/missing] | [source] | [notes] |
| Interruption / Recovery | [covered/partial/missing] | [source] | [notes] |
| History / List Interaction | [covered/partial/missing] | [source] | [notes] |
| State / Data | [covered/partial/missing] | [source] | [notes] |
| Integration | [covered/partial/missing] | [source] | [notes] |
| Evidence Chain | [covered/partial/missing] | [source] | [notes] |
| Contract Content | [covered/partial/missing] | [source] | [notes] |
| Visual / Media Handling | [covered/partial/missing] | [source] | [notes] |

## High-Value Asset Preservation

| Asset Type | Description | Coverage | Handling |
|------------|-------------|----------|----------|
| [content / rules / process / interruption / history / contract / visual / PRD-external] | [asset] | [covered/partial/missing] | [automated/manual/partial/preserved] |

## Functional Test Cases Summary

### Module: [Module Name]

| TC ID | Name | Generator | Fidelity Modes | Priority |
|-------|------|-----------|----------------|----------|
| TC-001 | [name] | Equivalence | content_fidelity_mode | High |

**Total by module:** N test cases

## Automation Analysis

| Level | Count | Percentage |
|-------|-------|-----------|
| automatable | N | X% |
| partial | N | X% |
| manual | N | X% |

## Cross-Module Scenarios

| ID | Name | Type | Modules | Status |
|----|------|------|---------|--------|
| CMS-001 | [name] | interruption_recovery | [modules] | Covered |

## Automation Scripts

| Script File | Module | Test Cases | Count |
|-------------|--------|-----------|-------|
| auth.e2e.spec.ts | Authentication | TC-001, TC-002 | 2 |

## Retained Manual / Partial Verification

### Intentionally Retained Manual Coverage
- [asset or scenario kept manual, and why]

### Partially Automated Coverage
- [asset or scenario partially automated, and what still needs human verification]

### Still-Missing Coverage
- [asset or scenario not yet preserved in either automated or manual form]

## Gap Analysis

### Covered
- [capability, rule, or asset with explicit coverage]

### Preserved Manual
- [asset preserved via manual verification]

### Partial
- [dimension or asset with only partial coverage]

### Missing
- [dimension or asset not yet covered]

### Recommended Next Actions
1. [next action]
2. [next action]

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
- [additional observations or recommendations]
