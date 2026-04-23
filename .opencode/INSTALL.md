# Installing Supertester for OpenCode

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed

## Installation

Add supertester to the `plugin` array in your `opencode.json` (global or project-level):

```json
{
  "plugin": ["supertester@git+https://github.com/supertester-ai/supertester.git"]
}
```

Restart OpenCode. The plugin auto-installs and registers all skills.

Verify by asking: "Tell me about supertester"

## Usage

Use OpenCode's native `skill` tool:

```
use skill tool to list skills
use skill tool to load supertester/requirement-analysis
```

### Available Skills

| Skill | Purpose |
|-------|---------|
| using-supertester | Entry point + routing |
| requirement-analysis | Parse requirements + clarify ambiguities |
| requirement-association | Module dependency + cross-module scenarios |
| test-case-generation | Generate functional test cases |
| automation-analysis | Classify automation feasibility |
| automation-scripting | Generate Playwright E2E scripts |
| test-reporting | Generate test reports |

### Quick Start

```
You: analyze requirements/auth-prd.md and generate tests
```

Supertester will guide you through the 6-phase workflow automatically.

## Updating

Supertester updates automatically when you restart OpenCode.

To pin a specific version:

```json
{
  "plugin": ["supertester@git+https://github.com/supertester-ai/supertester.git#v0.1.0"]
}
```

## Tool Mapping

When skills reference Claude Code tools, OpenCode equivalents apply:

- `Skill` tool → OpenCode's native `skill` tool
- `Read`, `Write`, `Edit`, `Bash` → Native OpenCode tools
- `Agent` subagents → OpenCode's `@mention` system

## Troubleshooting

### Plugin not loading

1. Check logs: `opencode run --print-logs "hello" 2>&1 | grep -i supertester`
2. Verify the plugin line in your `opencode.json`
3. Make sure you're running a recent version of OpenCode

### Skills not found

1. Use `skill` tool to list what's discovered
2. Check that the plugin is loading (see above)
