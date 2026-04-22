# Supertester for Continue

AI-driven software testing workflow plugin for [Continue](https://continue.dev) (VS Code / JetBrains).

---

## What This Integration Adds

- Project-level skill: `.continue/skills/supertester/`
- Project-level slash command prompt: `.continue/prompts/supertester.prompt`
- Full 6-phase testing workflow from requirements to Playwright E2E scripts

Continue supports both **project-level** (`<repo>/.continue/...`) and **global** (`~/.continue/...`) locations.

---

## Installation (Project-level, recommended)

In your project root:

```bash
git clone https://github.com/your-org/supertester.git
cp -r supertester/.continue .continue
```

Restart Continue (or reload the IDE) so it picks up the new files.

---

## Installation (Global)

Copy the skill and prompt into your global Continue directory:

```bash
git clone https://github.com/your-org/supertester.git
mkdir -p ~/.continue/skills ~/.continue/prompts
cp -r supertester/.continue/skills/supertester ~/.continue/skills/
cp supertester/.continue/prompts/supertester.prompt ~/.continue/prompts/
```

Restart Continue (or reload the IDE) so it picks up the new files.

---

## Usage

1. In Continue chat, run:
   - `/supertester`
2. The prompt will guide you through the 6-phase testing workflow

### Quick Start

```
You: /supertester analyze requirements/auth-prd.md and generate tests
```

---

## Available Skills

| Skill | Purpose |
|-------|---------|
| using-supertester | Entry point + workflow routing |
| requirement-analysis | Parse requirements + clarify ambiguities |
| requirement-association | Module dependencies + cross-module scenarios |
| test-case-generation | Generate functional test cases |
| automation-analysis | Classify automation feasibility |
| automation-scripting | Generate Playwright E2E scripts |
| test-reporting | Generate test reports |

---

## Helper Scripts (Optional)

From your project root:

```bash
# Create .supertester/ session files (if missing)
bash .continue/skills/supertester/scripts/init-session.sh

# Verify all phases marked complete
bash .continue/skills/supertester/scripts/check-complete.sh
```

---

## Notes & Limitations

- Continue does not run Claude Code hooks (PreToolUse/PostToolUse/Stop). The workflow is manual: re-read `.supertester/task_plan.md` before decisions and update it after each phase.
- The workflow state files in `.supertester/` are tool-agnostic and can be used across Claude Code, Cursor, Gemini CLI, and Continue.
- All testing workflow state is persisted to `.supertester/` directory in your project root.

---

## Getting Help

- Report issues: https://github.com/your-org/supertester/issues
- Main documentation: https://github.com/your-org/supertester
