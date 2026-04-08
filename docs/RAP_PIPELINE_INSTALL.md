# RAP Pipeline Install Guide

This repository includes install scripts so another user can install the global `rap-pipeline` plugin into their own Claude Code environment.

## Claude Code Runbook

If Claude Code is explicitly asked to read this file and help with installation, it should do the following in order:

1. Detect whether the machine is Windows or macOS/Linux.
2. Confirm that this repository is present locally.
3. If the repository is already cloned, update it with `git pull origin main`.
4. If the local checkout uses `master` instead of `main`, update it with `git pull origin master`.
5. Run the correct install script for the current OS.
6. Verify that `~/.claude/settings.json` now contains:
   - `extraKnownMarketplaces.rap-pipeline-local`
   - `enabledPlugins["rap-pipeline@rap-pipeline-local"] = true`
7. Tell the user to restart Claude Code if it was already running.
8. Explain how to use the plugin after install.

After installation, Claude Code should explain this quick start:

- Open a project repository that contains local RAP files such as `RAP_PROJECT_PROFILE.json`, `run_logging.md`, and `search_cycle_input.json`.
- Start with `rap-pipeline 시작`.
- The plugin should ask which stage to start from.
- It should not start literature search automatically from project topic alone.

Claude Code should not automatically start the RAP workflow unless the user explicitly asks for that next step.

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
- Git installed
- For macOS or Linux: `python3` available in `PATH`

## Get The Repository

If the target machine does not already have this repository, clone it first:

```bash
git clone https://github.com/sungwooan4930/Exp_Auto_Pipeline.git
cd Exp_Auto_Pipeline
```

If the repository already exists locally, update it before installing:

```bash
git pull origin main
```

If the local checkout uses `master` instead of `main`, use:

```bash
git pull origin master
```

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

Expected behavior:

1. Claude loads the RAP bootstrap skill.
2. Claude asks which stage to start from.
3. The user chooses one of:
   - `연구 서치 시작`
   - `gap 가설 단계 시작`
   - `실험 설계 시작`
   - `시뮬레이션 시작`
   - `상태 업데이트`
4. Only after `연구 서치 시작` is chosen should the plugin read `search_cycle_input.json`.

## Usage After Install

Typical first use:

```text
rap-pipeline 시작
```

Direct stage entry:

```text
rap-pipeline 연구 서치 시작
rap-pipeline gap 가설 단계 시작
rap-pipeline 실험 설계 시작
rap-pipeline 시뮬레이션 시작
rap-pipeline 상태 업데이트
```

Recommended user flow:

1. Prepare or review `RAP_PROJECT_PROFILE.json`.
2. Prepare the stage input JSON such as `search_cycle_input.json`.
3. Run `rap-pipeline 시작`.
4. Choose the desired stage.
5. Review generated JSON outputs and `run_logging.md`.

## Update To A New Version

When a newer version of this repository is pushed, update the local checkout first:

```bash
git pull origin main
```

If the local checkout uses `master`, use:

```bash
git pull origin master
```

Then run the install script again so the newest plugin files are copied into `~/.claude`.

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_rap_pipeline.ps1
```

macOS / Linux:

```bash
bash ./scripts/install_rap_pipeline.sh
```

Restart Claude Code after reinstalling the updated plugin files.

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
