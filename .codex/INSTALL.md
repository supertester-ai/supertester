# Installing Supertester for Codex

Install Supertester as a full Codex plugin. The old `skills`-only symlink mode is not sufficient because it does not load the bundled `test-reviewer` agent or the hook-based workflow guards.

## What the Codex plugin loads

When installed as a full plugin, Codex loads:

- `skills/` for the Supertester workflow skills
- `agents/test-reviewer.md` for independent review
- root `hooks.json` for SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, and Stop checks

## Prerequisites

- Git
- Codex with plugin support enabled
- Bash available in PATH

## Installation

### Preferred: install as a Codex plugin

Use the Codex Plugins UI and install this repository as a plugin. The Codex manifest is:

```text
.codex-plugin/plugin.json
```

If your Codex build supports installing from a Git repository, use:

```text
https://github.com/supertester-ai/supertester.git
```

If your Codex build supports installing from a local path, first clone the repository:

```bash
git clone https://github.com/supertester-ai/supertester.git ~/plugins/supertester
```

Then install the local plugin directory through the Codex Plugins UI.

**Windows (PowerShell)**

```powershell
git clone https://github.com/supertester-ai/supertester.git "$env:USERPROFILE\plugins\supertester"
```

### Legacy fallback: skills-only mode

The old skills-only install can still expose the Markdown skills, but it is **not** a complete Supertester installation in Codex because it does not provide native plugin hooks or the bundled reviewer agent.

## Verify

After installation, confirm the following behavior in Codex:

1. On session start, Supertester context is injected automatically.
2. `using-supertester` is available without manual skill symlink setup.
3. Phase 2/3/5 flows can call the bundled `test-reviewer`.
4. Stop checks warn when `.supertester/test_plan.md` still has incomplete phases.

## Updating

If installed from a local clone:

```bash
cd ~/plugins/supertester && git pull
```

Then refresh or reinstall the plugin in Codex.

## Uninstalling

Remove the plugin from the Codex Plugins UI. If you used a local clone, optionally delete it afterward.

## Troubleshooting

### The plugin loads skills but not the full workflow

You likely installed Supertester as skills only. Reinstall it as a full Codex plugin so `agents/` and `hooks.json` are loaded as well.

### Hooks do not run

1. Confirm the plugin root includes `hooks.json`
2. Confirm Bash is available in PATH
3. Restart Codex after plugin installation or update

### `test-reviewer` cannot be found

This indicates Codex loaded the skills without the plugin's `agents/` directory. Reinstall as a full plugin.

## Getting Help

- Report issues: https://github.com/supertester-ai/supertester/issues
- Main documentation: https://github.com/supertester-ai/supertester
