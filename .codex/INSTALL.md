# Installing Supertester for Codex

Enable Supertester skills in Codex via native skill discovery. Just clone and symlink.

## Prerequisites

- Git

## Installation

1. **Clone the Supertester repository:**
   ```bash
git clone https://github.com/supertester-ai/supertester.git ~/.codex/supertester
   ```

2. **Create the skills symlink:**
   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/supertester/skills ~/.agents/skills/supertester
   ```

   **Windows (PowerShell):**
   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
   cmd /c mklink /J "$env:USERPROFILE\.agents\skills\supertester" "$env:USERPROFILE\.codex\supertester\skills"
   ```

3. **Restart Codex** (quit and relaunch the CLI) to discover the skills.

## Verify

```bash
ls -la ~/.agents/skills/supertester
```

You should see a symlink (or junction on Windows) pointing to your Supertester skills directory.

## Updating

```bash
cd ~/.codex/supertester && git pull
```

Skills update instantly through the symlink.

## Uninstalling

```bash
rm ~/.agents/skills/supertester
```

Optionally delete the clone: `rm -rf ~/.codex/supertester`.

**Windows (PowerShell):**
```powershell
Remove-Item "$env:USERPROFILE\.agents\skills\supertester"
```

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

## Troubleshooting

### Skills not showing up

1. Verify the symlink: `ls -la ~/.agents/skills/supertester`
2. Check skills exist: `ls ~/.codex/supertester/skills`
3. Restart Codex — skills are discovered at startup

### Windows junction issues

Junctions normally work without special permissions. If creation fails, try running PowerShell as administrator.

## Getting Help

- Report issues: https://github.com/supertester-ai/supertester/issues
- Main documentation: https://github.com/supertester-ai/supertester
