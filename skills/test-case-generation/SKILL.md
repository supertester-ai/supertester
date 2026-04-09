---
name: test-case-generation
description: Use when generating functional test cases from analyzed requirements - intelligently selects sub-generators, applies fidelity strategies, deduplicates carefully, requires test-reviewer audit and user confirmation
---

# Skill 3: Functional Test Case Generation

## Iron Law

> Select generators based on requirement traits. Do not blindly invoke all generators.
> Test design is not only about behavior coverage; it must preserve high-value test assets and verification depth.

<HARD-GATE>
Do not proceed to `automation-analysis` before the user confirms the functional test cases.
Do not submit functional cases to the user before `test-reviewer` has reviewed them.
</HARD-GATE>

## Preconditions

- Phase 2 status is `complete`
- the user has confirmed the association analysis results

## Core Workflow

```text
Confirmed requirements + association results + extracted test assets
        |
        v
Requirement trait analysis
        +
Fidelity strategy selection
        |
        v
Sub-generator selection
        |
        v
Test case generation
        |
        v
Deduplication with asset-protection rules
        |
        v
test-reviewer audit
        |
        v
User confirmation
```

## Generation Strategy

Always reason on two axes:

- **Behavior axis**: input validation, workflows, state transitions, rule combinations, security, performance
- **Evidence axis**: UI, content, API, DB, event, file, log, metrics, external systems

### New P0 Layer: Fidelity Strategy

Before picking sub-generators, assign one or more fidelity modes to each `F-xxx`.

| Fidelity Mode | When to use | Expected outcome |
|---------------|-------------|------------------|
| `enumeration_mode` | full lists, matrices, denylists, status sets | preserve full coverage instead of sampled examples |
| `content_fidelity_mode` | exact copy, prompt content, templates, tooltips, email text | generate field-by-field or item-by-item verification |
| `process_mode` | loading, progress, processing, scanning, staged feedback | generate intermediate-state verification cases |
| `interruption_mode` | refresh, language switch, navigation away, retry, logout during processing | generate interruption and recovery cases |
| `visual_fallback_mode` | image, logo, layout, style, media validation | generate manual or partial cases instead of silently dropping coverage |
| `history_interaction_mode` | history tables, record lists, feeds, result lists | generate sorting / pagination / scrolling / empty-state coverage |
| `contract_content_mode` | prompt, schema, output template, path format, export contract | generate structure and contract validation cases |

Sub-generators tell you *what kind of logic to test*.
Fidelity modes tell you *how detailed and how preserving the generated tests must be*.

## Requirement Type -> Generator Mapping

| Requirement Type | Required Generators | Optional Generators |
|------------------|---------------------|---------------------|
| API / parameter validation | equivalence, boundary | exception |
| workflow / business flow | scenario, exception | equivalence, boundary |
| state machine | state transition, scenario | boundary, exception |
| complex business rules | decision table, equivalence | boundary, security |
| security-sensitive module | security, equivalence | exception, boundary |
| performance-sensitive module | performance, scenario | boundary |

## Evidence Axis Requirements

| Evidence Surface | Generation Requirement |
|------------------|------------------------|
| UI / content | specify exact text or element expectations, not "shows correctly" |
| API | specify request/response/status/field contract |
| DB / state | specify object/field/state changes and persistence behavior |
| Event / message | specify trigger, emission, consumption, retry, or failure behavior |
| File | specify file content, format, naming, or export/import outcome |
| Log / metrics | specify expected log, metric, audit trail, or path |
| External system | specify external preconditions, feedback, failure, and verification path |

If multiple evidence surfaces matter, the test set must reflect multiple observation paths.

## Fidelity Strategy Triggers

The following are not optional hints. Treat them as direct mode triggers.

### Trigger `content_fidelity_mode`

- copy as follows
- content as follows
- tooltip
- email template
- empty state
- loading text
- button text
- prompt text
- modal copy

### Trigger `process_mode`

- loading
- progress
- processing
- scanning
- analyzing
- generating
- staged status

### Trigger `interruption_mode`

- refresh
- retry
- navigate away
- switch language
- switch tab
- logout during processing
- recover after failure

### Trigger `visual_fallback_mode`

- image
- logo
- banner
- visual
- layout
- style
- media

### Trigger `history_interaction_mode`

- history
- records
- list
- pagination
- sorting
- infinite scroll
- table

### Trigger `contract_content_mode`

- prompt
- schema
- output format
- path format
- export path
- log path
- template fields

## Step 1: Analyze Requirement Traits

For each `F-xxx`:

1. analyze behavior traits
2. analyze evidence surfaces
3. identify high-value assets that must not be abstracted away
4. assign fidelity modes
5. choose sub-generators
6. record the rationale in `findings.md`

### Required Trait Checks

For each feature, explicitly ask:

- Does this feature require exact content verification?
- Does it have important intermediate states?
- Does it need interruption/recovery coverage?
- Does it include visual/media assets that need manual or partial handling?
- Does it include history/list behavior?
- Does it include contract content such as prompt/schema/path/template rules?

## Step 2: Generate Test Cases

Each generated case must include:

- test case ID (`TC-xxx`)
- module and feature
- generator source
- fidelity mode(s)
- preconditions
- test steps
- expected results
- primary evidence surfaces
- requirement traceability (file + line)

### Asset Preservation Rules

If a feature includes high-value assets:

- **Content assets**: generate explicit content checks, not vague content assertions
- **Rule / enum assets**: preserve full lists or matrix logic where the full set is the requirement
- **State / data assets**: include state changes, side effects, persistence, history, or audit expectations
- **Integration assets**: include success, failure, timeout, retry, downgrade, or callback expectations
- **Contract content assets**: generate structure-level validation and field-level validation where needed
- **Visual assets**: if direct automation is not appropriate, generate a `manual` or `partial` case instead of omitting it

### P0 Case Patterns To Force When Triggered

If the feature has `process_mode`, generate at least one case for:

- intermediate status visibility
- transition order between major stages

If the feature has `interruption_mode`, generate at least one case for:

- interrupted-in-progress recovery or reset behavior

If the feature has `history_interaction_mode`, generate cases for the applicable list mechanics:

- sorting
- pagination
- scrolling / lazy loading
- empty state

If the feature has `contract_content_mode`, generate at least one case for:

- structure correctness
- required fields or sections

If the feature has `content_fidelity_mode`, prefer itemized checks over generalized "copy is correct".

## Step 3: Deduplicate Carefully

Deduplication categories:

- `exact_duplicate`
- `subset_duplicate`
- `redundant_boundary`
- `overlapping_state`

### Asset Protection Rules

Do not deduplicate away a case merely because its main flow looks similar when it preserves a distinct high-value asset, such as:

- exact copy or template verification
- intermediate process-state verification
- interruption/recovery verification
- history interaction verification
- distinct evidence surfaces
- contract structure validation
- manual/partial visual verification

If in doubt, keep the case and explain why in `deduplication-report.md`.

## Step 4: test-reviewer Audit

Call `test-reviewer` to review:

- requirement coverage
- fidelity-mode correctness
- asset preservation quality
- generator selection quality
- deduplication quality
- whether process/interruption/history/visual/contract gaps remain

CRITICAL or HIGH issues must be fixed before user review.

## Step 5: User Confirmation

Present:

- original vs deduplicated counts
- cases grouped by module
- review summary

After confirmation, update Phase 3 to `complete`.

## Output Format (`functional-cases.md`)

```markdown
# Functional Test Cases

## Generation Summary
- Raw case count: N
- Deduplicated count: M
- See deduplication details: deduplication-report.md

## TC-001: [Case Name]
- **Module:** [Module Name]
- **Feature:** F-001 [Feature Name]
- **Generator:** [Generator Name]
- **Fidelity Modes:** enumeration_mode | content_fidelity_mode | process_mode | interruption_mode | visual_fallback_mode | history_interaction_mode | contract_content_mode
- **Evidence Surfaces:** UI | API | DB | Event | File | Message | Log | Metrics | External System

### Preconditions
- [condition 1]
- [condition 2]

### Test Steps
1. [step 1]
2. [step 2]

### Expected Results
- [result 1]
- [result 2]

### Requirement Traceability
| Source File | Lines | Original Text |
|-------------|-------|---------------|
| `<filename>` | XX-YY | "Original text" |

### Preserved Assets
- [exact copy / matrix / state assertion / prompt template / visual fallback note]
```

## 2-Action Rule

- after generating cases for 2 features, append to `functional-cases.md`
- after 2 rounds of deduplication analysis, update `deduplication-report.md`

## Red Flags

| If you think... | Reality is... |
|-----------------|---------------|
| "The generator choice is enough" | Without fidelity strategy, high-value details still disappear. |
| "We can sample a few values from the list" | If the list itself is the requirement, sampling is a coverage bug. |
| "Intermediate states are implied by the final state" | Process feedback is a separate verification target. |
| "Visual checks are not automatable, so skip them" | They must be preserved as manual or partial coverage. |
| "Prompt/template validation is overkill" | In AI systems, prompt/template content often is the contract. |
| "History lists are just UI polish" | Sorting/pagination/scroll behavior is often core product behavior. |

## Completion Criteria

Phase 3 is complete only when:

- every `F-xxx` has behavior coverage
- high-value assets are preserved
- fidelity modes have been applied where needed
- process/interruption/history/contract/visual gaps are not silently dropped
- multi-surface evidence needs are reflected in the case set
- reviewer confirms no obvious coverage-dimension gaps remain
