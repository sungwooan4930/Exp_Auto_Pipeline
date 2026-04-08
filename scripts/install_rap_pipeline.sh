#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${1:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
CLAUDE_HOME="${CLAUDE_HOME:-${HOME}/.claude}"

CORE_ROOT="${REPO_ROOT}/skillpacks/rap-pipeline-core"
DIST_ROOT="${REPO_ROOT}/distribution/rap-pipeline-local"
MARKETPLACE_ROOT="${CLAUDE_HOME}/plugins/marketplaces/rap-pipeline-local"
PLUGIN_ROOT="${MARKETPLACE_ROOT}/plugins/rap-pipeline"
SETTINGS_PATH="${CLAUDE_HOME}/settings.json"

if [[ ! -d "${CORE_ROOT}" ]]; then
  echo "Missing core skillpack at ${CORE_ROOT}" >&2
  exit 1
fi

if [[ ! -d "${DIST_ROOT}" ]]; then
  echo "Missing distribution metadata at ${DIST_ROOT}" >&2
  exit 1
fi

mkdir -p "${MARKETPLACE_ROOT}/.claude-plugin"
mkdir -p "${MARKETPLACE_ROOT}/plugins"
mkdir -p "${PLUGIN_ROOT}/.claude-plugin"

cp "${DIST_ROOT}/.claude-plugin/marketplace.json" "${MARKETPLACE_ROOT}/.claude-plugin/marketplace.json"
cp "${DIST_ROOT}/plugins/rap-pipeline/.claude-plugin/plugin.json" "${PLUGIN_ROOT}/.claude-plugin/plugin.json"

rm -rf "${PLUGIN_ROOT}/references" "${PLUGIN_ROOT}/skills" "${PLUGIN_ROOT}/templates"
cp -R "${CORE_ROOT}/references" "${PLUGIN_ROOT}/references"
cp -R "${CORE_ROOT}/skills" "${PLUGIN_ROOT}/skills"
cp -R "${CORE_ROOT}/templates" "${PLUGIN_ROOT}/templates"

rm -rf "${PLUGIN_ROOT}/skills/rap-pipeline"
mkdir -p "${PLUGIN_ROOT}/skills"
cp -R "${DIST_ROOT}/plugins/rap-pipeline/skills/rap-pipeline" "${PLUGIN_ROOT}/skills/rap-pipeline"

mkdir -p "${CLAUDE_HOME}"
if [[ -f "${SETTINGS_PATH}" ]]; then
  cp "${SETTINGS_PATH}" "${SETTINGS_PATH}.backup-$(date +%Y-%m-%dT%H%M%S)"
fi

python3 - <<'PY' "${SETTINGS_PATH}" "${MARKETPLACE_ROOT}"
import json
import pathlib
import sys

settings_path = pathlib.Path(sys.argv[1])
marketplace_root = sys.argv[2]

if settings_path.exists():
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
else:
    settings = {}

settings.setdefault("extraKnownMarketplaces", {})
settings.setdefault("enabledPlugins", {})

settings["extraKnownMarketplaces"]["rap-pipeline-local"] = {
    "source": {
        "source": "directory",
        "path": marketplace_root,
    },
    "autoUpdate": False,
}

settings["enabledPlugins"]["rap-pipeline@rap-pipeline-local"] = True

settings_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY

echo "Installed rap-pipeline into: ${MARKETPLACE_ROOT}"
echo "Updated settings: ${SETTINGS_PATH}"
echo "Restart Claude Code if it is already running."
