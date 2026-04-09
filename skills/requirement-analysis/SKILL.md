---
name: requirement-analysis
description: Use when analyzing requirement documents - parses requirements, detects ambiguities, extracts high-value test assets, and conducts clarification dialogues before any test generation
---

# Skill 1: Requirement Analysis And Clarification

## Iron Law

> If the requirements are not understood, no test cases may be generated.
> Do not invoke `test-case-generation` until requirement analysis and clarification are complete.

<HARD-GATE>
Do not proceed to `requirement-association` while material ambiguities remain unresolved.
This applies even when the requirement document appears clear at first glance.
</HARD-GATE>

## Goal

Turn raw requirement documents into structured, test-ready requirements with:

- explicit functional behavior
- explicit evidence surfaces
- explicit high-value test assets
- explicit ambiguity records
- explicit markers for fidelity-sensitive requirements

The output of this phase must be rich enough that later phases do not need to "guess the missing details back".

## Workflow

```text
Requirement document
    |
    v
Parse Markdown -> extract modules / features / acceptance criteria / boundaries / dependencies / test assets
    |
    v
Tag each feature with fidelity-sensitive requirement markers
    |
    v
Detect ambiguity -> [Any unresolved ambiguity?]
    |                      |
    | no                   | yes
    v                      v
Write parsed-             Ask clarification questions one at a time
requirements.md           and save state to clarifications.json
    |                      |
    +----------+-----------+
               |
               v
Update test_plan.md / findings.md / progress.md
```

## Required Feature Tags

Every `F-xxx` must be evaluated for the following tags. These tags drive later generation strategy and review expectations.

| Tag | Meaning | Typical signals |
|-----|---------|-----------------|
| `content_fidelity` | The content itself must be checked precisely | copy, tooltip, email body, empty state, loading text, template content |
| `process_feedback` | Intermediate states matter, not only the final outcome | loading, progress, scanning, analyzing, processing |
| `interruption_recovery` | User interruption or context switching matters | refresh, switch language, navigate away, retry, logout during processing |
| `visual_asset` | Visual/media/brand assets require explicit handling | image, logo, banner, layout, icon, style |
| `contract_content` | Template/schema/prompt/path content is itself a contract | prompt, schema, JSON structure, output format, log path, export path |
| `business_outside_prd` | Important rules may live outside the PRD | feature flag, ops config, historical behavior, compatibility, legacy flow |

If a feature matches one of these tags, record it explicitly. Never rely on later phases to infer it again.

## Step 1: Parse The Requirement Document

Read the user-provided requirement document and extract:

- **Modules**: top-level product areas
- **Features (`F-xxx`)**: concrete behaviors within each module
- **Acceptance criteria**: expected outcomes and success rules
- **Boundary conditions**: limits, ranges, thresholds, counts, length rules
- **Dependencies**: modules, services, environments, third-party systems
- **Test assets**: anything too important to reduce to a generic "works correctly"
- **Source**: original file and line numbers

### Required Test Asset Categories

At minimum, extract these asset types when present:

1. **Content assets**
   - titles, button text, placeholders, notifications, modal copy, email content, loading text, empty states, help text
2. **Rule and enumeration assets**
   - matrices, allowlists, denylists, roles, statuses, error code lists, configuration options, exact supported values
3. **Integration assets**
   - callbacks, external systems, retries, sync points, async feedback, import/export contracts
4. **State and data assets**
   - field updates, quota changes, persistence, logs, records, derived state, history entries
5. **Constraint and contract assets**
   - schemas, prompt templates, output structures, file naming rules, path formats, permission rules
6. **Evidence surfaces**
   - UI, API, DB, Event, File, Message, Log, Metrics, External System

## Step 1.5: Build The Dual View For Every Feature

Every `F-xxx` must answer both questions:

- **Behavior view**: what does the user or system do?
- **Evidence view**: how do we prove it happened correctly?

If only the behavior view is captured, later phases will overfit to happy-path interactions and underfit to verification depth.

### Additional P0 Extraction Rules

For each feature, explicitly record:

- primary evidence surfaces
- irreplaceable assets that must not be abstracted away
- required feature tags from the tag table above

## Step 2: Detect Ambiguity

Use `@clarification-patterns.md` to detect ambiguous requirements.

Common semantic ambiguity signals:

- vague words such as "etc", "related", "reasonable", "appropriate"
- missing numeric thresholds
- missing error behavior
- multiple plausible interpretations
- hidden preconditions or postconditions

### Also Detect Test-Asset Ambiguity

You must also clarify ambiguity in test assets, not only feature semantics.

Clarify when any of the following is unclear:

- whether copy must match exactly or only semantically
- whether a list/matrix must be fully enumerated or only sampled
- whether intermediate progress states must be verified
- whether visual assets must be manually checked
- whether prompt/schema/template content is contractual
- whether history tables need sorting/pagination/scroll behavior validation
- whether there are PRD-external rules such as ops flags, legacy behavior, removed features, or compatibility constraints

### Strong Clarification Triggers

Treat the following phrases as default clarification triggers when the requirement does not fully specify expectations:

- "content as follows"
- "copy as follows"
- "template as follows"
- "prompt as follows"
- "schema as follows"
- "image as follows"
- "history list"
- "pagination"
- "sorting"
- "loading"
- "processing"
- "refresh"
- "switch language"
- "log path"
- "export path"
- "legacy"
- "feature flag"

## Step 3: Clarification Dialogue

Rules:

- ask one question at a time
- prefer multiple-choice when possible
- save `clarifications.json` after each answer
- support pause and resume

### Mandatory P0 Clarification Branch

Ask explicitly when not already answered by the source materials:

> Are there any important rules outside the PRD, such as ops toggles, historical compatibility behavior, removed-but-still-regression-worthy flows, or admin configuration that changes user behavior?

If yes, record them as test assets and tag the affected features with `business_outside_prd`.

## Step 4: Write Output Files

After analysis and clarification:

1. write `.supertester/requirements/parsed-requirements.md`
2. write `.supertester/requirements/clarifications.json` if clarifications exist
3. update `.supertester/test_plan.md` Phase 1 status to `complete`
4. update `.supertester/findings.md`
5. update `.supertester/progress.md`

## 2-Action Rule

- after analyzing 2 modules, update `parsed-requirements.md`
- after 2 clarification rounds, update `clarifications.json`

## Output Format

### parsed-requirements.md

```markdown
# Requirement Analysis

## Source Documents
- <filename> (analyzed at: YYYY-MM-DDTHH:MM:SSZ)

## Module List

### Module: [Module Name]

#### F-001: [Feature Name]
- **Description:** [feature description]
- **Acceptance Criteria:**
  - [criterion 1]
  - [criterion 2]
- **Boundary Conditions:** [boundary 1], [boundary 2]
- **Dependencies:** [dependency list]
- **Evidence Surfaces:** UI | API | DB | Event | File | Message | Log | Metrics | External System
- **Feature Tags:** content_fidelity | process_feedback | interruption_recovery | visual_asset | contract_content | business_outside_prd
- **High-Value Test Assets:**
  - **Content Assets:** [copy / text / templates that matter]
  - **Rule / Enum Assets:** [full list or matrix]
  - **Integration Assets:** [callbacks / systems / external dependencies]
  - **State / Data Assertions:** [objects / fields / persistence / history / logs]
  - **Constraint / Contract Assets:** [schema / prompt / path / output contract]
- **Source:** `<filename>` lines XX-YY

## Asset Inventory

### Content Inventory
- [asset] -> [feature] -> [exact vs semantic] -> [source]

### Rule / Matrix Inventory
- [asset] -> [full list or matrix] -> [feature] -> [source]

### Process Feedback Inventory
- [asset] -> [feature] -> [intermediate states to verify] -> [source]

### Interruption / Recovery Inventory
- [asset] -> [feature] -> [refresh / retry / context switch expectation] -> [source]

### Visual Asset Inventory
- [asset] -> [feature] -> [manual or partial verification expectation] -> [source]

### Contract Content Inventory
- [asset] -> [feature] -> [schema / prompt / path / template rule] -> [source]

### PRD-External Business Inventory
- [asset] -> [feature] -> [ops / legacy / config / compatibility note] -> [source]
```

### clarifications.json

```json
{
  "sessionId": "clarify-session-YYYYMMDD-NNN",
  "requirementDoc": "<filename>",
  "status": "completed|in_progress|paused",
  "createdAt": "ISO-8601",
  "updatedAt": "ISO-8601",
  "completedClarifications": [
    {
      "id": "CL-001",
      "relatedFeature": "F-001",
      "question": "Question text",
      "answer": "User answer",
      "answeredAt": "ISO-8601"
    }
  ],
  "pendingClarifications": [
    {
      "id": "CL-002",
      "relatedFeature": "F-001",
      "question": "Question text",
      "status": "pending",
      "options": ["Option A", "Option B", "Option C"]
    }
  ],
  "prdExternalAssets": [
    {
      "id": "EXT-001",
      "relatedFeature": "F-001",
      "type": "ops_toggle|legacy_behavior|admin_config|removed_flow|compatibility_rule",
      "description": "Description of the rule outside the PRD"
    }
  ],
  "pauseReason": ""
}
```

## Resume Behavior

| Trigger | Behavior |
|---------|----------|
| user says "continue clarification" | read the latest `clarifications.json` and resume pending items |
| user says "resume CL-002" | resume the specified clarification |
| new session starts | if `clarifications.json` exists and is not completed, prompt the user to continue |

## Red Flags

| If you think... | Reality is... |
|-----------------|---------------|
| "These details are too minor to capture" | Those details often become the highest-value missing tests. |
| "We can add the copy checks later" | Later phases usually abstract them away. |
| "Prompt/template text is implementation detail" | In AI systems, it is often business logic. |
| "Visual assets are not automatable, so ignore them" | They still must be preserved as manual or partial verification assets. |
| "PRD should be enough" | Real systems often depend on ops and historical behavior not stated in the PRD. |

## Completion Criteria

Phase 1 is complete only when:

- every `F-xxx` is structured
- material ambiguities are clarified
- high-value assets are extracted
- required feature tags are assigned
- primary evidence surfaces are recorded
- PRD-external business assets have been asked about or explicitly ruled out
