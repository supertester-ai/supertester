---
name: test-reporting
description: Use when generating the final test report - aggregates all phase outputs into a comprehensive report with traceability, coverage-dimension analysis, retained manual assets, and clear gap statements
---

# Skill 6: Test Reporting

## Iron Law

> A test report is not a count summary; it is a coverage explanation.
> If the report cannot explain what is covered, what is intentionally retained for manual verification, and what remains partial or missing, the report is incomplete.

## Preconditions

- Phase 5 status is `complete`

## Goal

Produce a report that makes the test outcome decision-ready by showing:

- requirement coverage
- coverage dimensions
- preserved high-value assets
- automation boundaries
- retained manual or partial verification areas
- remaining gaps and next actions

## Workflow

```text
All phase outputs
    |
    v
Aggregate counts and mappings
    |
    v
Analyze coverage dimensions + preserved assets + manual retention + gaps
    |
    v
Build traceability matrix
    |
    v
Write report -> reports/YYYY-MM-DD-<module>.md
    |
    v
Update test_plan.md Phase 6 -> complete
```

## Required Report Sections

The report must include:

1. **Executive Summary**
2. **Requirement Coverage**
3. **Coverage Dimensions**
4. **High-Value Asset Preservation**
5. **Functional Test Case Summary**
6. **Automation Analysis**
7. **Cross-Module Scenarios**
8. **Automation Scripts**
9. **Retained Manual / Partial Verification**
10. **Gap Analysis**
11. **Traceability Matrix**
12. **Review History**

## New P1 Reporting Rule: Retained Manual Assets Are First-Class Output

Do not treat manual or partial coverage as a leftover list.

Whenever the workflow preserves assets as manual or partial, the report must explicitly explain:

- which asset was retained
- why it was not fully automated
- whether it is still covered manually
- whether the limitation is intentional or still a gap

This rule is generic and applies across products. It is not limited to visual assets.

## Report Content Rules

### 1. Requirement Coverage

For each `F-xxx`, `IR-xxx`, and `CMS-xxx`, report:

- linked test cases
- automation level
- coverage status

### 2. Coverage Dimensions

At minimum, evaluate:

- behavior
- rules / enumerations
- content fidelity
- process feedback
- interruption / recovery
- history / list interaction
- state / data
- integration
- evidence chain
- contract content
- visual / media handling

If a dimension has only behavior coverage but weak evidence coverage, mark it `partial`, not `covered`.

### 3. High-Value Asset Preservation

Summarize how the workflow preserved:

- copy and content assets
- rules, matrices, lists, enums
- process-state assets
- interruption/recovery behaviors
- history/list behaviors
- prompt/schema/path/template contracts
- visual/media assets
- PRD-external business assets

### 4. Retained Manual / Partial Verification

This section must separate:

- **intentionally retained manual coverage**
- **partially automated coverage**
- **still-missing coverage**

Do not merge these into one bucket.

### 5. Gap Analysis

Classify gaps into:

- `covered`
- `preserved_manual`
- `partial`
- `missing`

Use concrete asset or dimension names. Never write vague "needs more coverage".

## Output Template Reference

See `@report-template.md`.

## Output Location

Write to:

- `.supertester/reports/YYYY-MM-DD-<module>.md`

If multiple modules are involved, you may generate:

- one summary report: `YYYY-MM-DD-summary.md`
- one detailed report per module

## Steps

1. read all phase output files
2. aggregate counts and mappings
3. analyze coverage dimensions
4. analyze preserved assets and retained manual/partial assets
5. construct the traceability matrix
6. write gap analysis using concrete asset/dimension terms
7. generate the report from the template
8. update Phase 6 to `complete`
9. update `progress.md`

## Reporting Rules

- do not reduce the report to counts or file listings
- explain why some coverage is intentionally manual or partial
- if an asset is not automated but is preserved manually, say so explicitly
- if an asset is neither automated nor manually preserved, mark it as missing
- if a dimension covers only final behavior but not the relevant process, contract, or evidence depth, mark it as partial
- write in reusable, domain-agnostic language; the structure must work across future products
