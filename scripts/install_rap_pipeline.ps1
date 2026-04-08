param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$ClaudeHome = (Join-Path $HOME ".claude")
)

$ErrorActionPreference = "Stop"

function Ensure-Directory {
    param([string]$Path)
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Remove-IfExists {
    param([string]$Path)
    if (Test-Path $Path) {
        Remove-Item -Recurse -Force $Path
    }
}

$coreRoot = Join-Path $RepoRoot "skillpacks\\rap-pipeline-core"
$distRoot = Join-Path $RepoRoot "distribution\\rap-pipeline-local"

if (!(Test-Path $coreRoot)) {
    throw "Missing core skillpack at $coreRoot"
}

if (!(Test-Path $distRoot)) {
    throw "Missing distribution metadata at $distRoot"
}

$marketplaceRoot = Join-Path $ClaudeHome "plugins\\marketplaces\\rap-pipeline-local"
$pluginRoot = Join-Path $marketplaceRoot "plugins\\rap-pipeline"
$settingsPath = Join-Path $ClaudeHome "settings.json"
$timestamp = Get-Date -Format "yyyy-MM-ddTHHmmss"

Ensure-Directory $ClaudeHome
Ensure-Directory $marketplaceRoot
Ensure-Directory (Join-Path $marketplaceRoot ".claude-plugin")
Ensure-Directory (Join-Path $marketplaceRoot "plugins")
Ensure-Directory $pluginRoot
Ensure-Directory (Join-Path $pluginRoot ".claude-plugin")

Copy-Item -Force (Join-Path $distRoot ".claude-plugin\\marketplace.json") (Join-Path $marketplaceRoot ".claude-plugin\\marketplace.json")
Copy-Item -Force (Join-Path $distRoot "plugins\\rap-pipeline\\.claude-plugin\\plugin.json") (Join-Path $pluginRoot ".claude-plugin\\plugin.json")

foreach ($dirName in @("references", "skills", "templates")) {
    $target = Join-Path $pluginRoot $dirName
    Remove-IfExists $target
    Copy-Item -Recurse -Force (Join-Path $coreRoot $dirName) $target
}

$bootstrapSkillDir = Join-Path $pluginRoot "skills\\rap-pipeline"
Remove-IfExists $bootstrapSkillDir
Copy-Item -Recurse -Force (Join-Path $distRoot "plugins\\rap-pipeline\\skills\\rap-pipeline") $bootstrapSkillDir

if (Test-Path $settingsPath) {
    Copy-Item -Force $settingsPath "$settingsPath.backup-$timestamp"
    $settings = Get-Content -Raw $settingsPath | ConvertFrom-Json -AsHashtable
}
else {
    $settings = @{}
}

if ($null -eq $settings["extraKnownMarketplaces"]) {
    $settings["extraKnownMarketplaces"] = @{}
}

if ($null -eq $settings["enabledPlugins"]) {
    $settings["enabledPlugins"] = @{}
}

$settings["extraKnownMarketplaces"]["rap-pipeline-local"] = @{
    source = @{
        source = "directory"
        path = $marketplaceRoot
    }
    autoUpdate = $false
}

$settings["enabledPlugins"]["rap-pipeline@rap-pipeline-local"] = $true

$json = $settings | ConvertTo-Json -Depth 20
Set-Content -Path $settingsPath -Value $json -Encoding utf8

Write-Host "Installed rap-pipeline into: $marketplaceRoot"
Write-Host "Updated settings: $settingsPath"
Write-Host "Restart Claude Code if it is already running."
