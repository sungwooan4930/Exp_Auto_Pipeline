# RAP Pipeline Install Guide

This repository includes install scripts so another user can install the global `rap-pipeline` plugin into their own Claude Code environment.

## What Gets Installed

The install scripts create a user-level local marketplace and enable one plugin:

- Marketplace: `rap-pipeline-local`
- Plugin: `rap-pipeline`

Installed target layout:

```text
~/.claude/plugins/marketplaces/rap-pipeline-local/
  .claude-plugin/marketplace.json
  plugins/rap-pipeline/
    .claude-plugin/plugin.json
    skills/
    references/
    templates/
```

The installer also updates `~/.claude/settings.json` so Claude Code knows about the marketplace and enables the plugin automatically.

## Prerequisites

- Claude Code installed
- This repository copied or cloned onto the target machine
- For macOS or Linux: `python3` available in `PATH`

## Windows Install

From the repository root, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_rap_pipeline.ps1
```

Optional custom Claude home:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_rap_pipeline.ps1 -ClaudeHome "C:\Users\<user>\.claude"
```

## macOS / Linux Install

From the repository root, run:

```bash
bash ./scripts/install_rap_pipeline.sh
```

Optional custom Claude home:

```bash
CLAUDE_HOME="$HOME/.claude" bash ./scripts/install_rap_pipeline.sh
```

## What The Scripts Change

They:

1. Copy the RAP plugin package into the user's local Claude marketplace directory.
2. Add this marketplace to `extraKnownMarketplaces` in `~/.claude/settings.json`.
3. Enable `rap-pipeline@rap-pipeline-local` in `enabledPlugins`.
4. Create a timestamped backup of the previous settings file if it already exists.

## After Install

Restart Claude Code if it was already open.

Inside a project repository that has local RAP files such as:

- `RAP_PROJECT_PROFILE.json`
- `run_logging.md`
- `search_cycle_input.json`

start the workflow with:

```text
rap-pipeline 시작
```

## Verify Install

You can verify by opening Claude Code and checking that `rap-pipeline` skills are available, or by running a fresh Claude CLI session and using:

```text
rap-pipeline 시작
```

If the plugin loaded correctly, Claude should enter the RAP bootstrap skill and ask which stage to start from.

## Uninstall

Delete:

- `~/.claude/plugins/marketplaces/rap-pipeline-local`

Then remove these settings entries from `~/.claude/settings.json`:

- `extraKnownMarketplaces.rap-pipeline-local`
- `enabledPlugins["rap-pipeline@rap-pipeline-local"]`

Restart Claude Code after removing them.
