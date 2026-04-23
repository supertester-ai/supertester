# Supertester for OpenClaw

AI-driven software testing workflow plugin for [OpenClaw](https://openclaw.ai).

---

## What This Integration Adds

- Workspace skill: `.openclaw/skills/supertester/`
- Full testing workflow: 6-phase lifecycle from requirements to Playwright scripts
- Cross-platform support (macOS, Linux, Windows)

OpenClaw supports three skill locations (in precedence order):
1. **Workspace skills** (highest priority): `<workspace>/.openclaw/skills/`
2. **Managed/local skills**: `~/.openclaw/skills/`
3. **Bundled skills** (lowest priority): shipped with install

---

## Installation (Workspace, recommended)

Copy the skill to your project:

```bash
# Clone the repo
git clone https://github.com/supertester-ai/supertester.git

# Copy the OpenClaw skill to your workspace
cp -r supertester/skills/supertester your-project/.openclaw/skills/

# Clean up
rm -rf supertester
```

---

## Installation (Global)

Install to your local OpenClaw skills directory:

```bash
# Clone the repo
git clone https://github.com/supertester-ai/supertester.git

# Copy to global OpenClaw skills
mkdir -p ~/.openclaw/skills
cp -r supertester/skills/supertester ~/.openclaw/skills/

# Clean up
rm -rf supertester
```

---

## Verify Installation

```bash
# Check OpenClaw status and loaded skills
openclaw status
```

---

## Usage

1. Start an OpenClaw session in your project directory
2. Supertester will guide you through the 6-phase testing workflow:
   - Phase 1: Requirement Analysis
   - Phase 2: Requirement Association
   - Phase 3: Test Case Generation
   - Phase 4: Automation Analysis
   - Phase 5: Automation Scripting
   - Phase 6: Test Reporting

### Quick Start

```
You: analyze requirements/auth-prd.md and generate tests
```

Supertester will initialize the workflow and guide you through each phase.

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

## Configuration (Optional)

Configure the skill in `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "supertester": {
        enabled: true
      }
    }
  }
}
```

---

## Notes

- OpenClaw snapshots eligible skills when a session starts
- Workspace skills take precedence over bundled skills
- The skill works on all platforms: macOS, Linux, and Windows
- All workflow state is persisted to `.supertester/` directory

---

## Getting Help

- Report issues: https://github.com/supertester-ai/supertester/issues
- Main documentation: https://github.com/supertester-ai/supertester
