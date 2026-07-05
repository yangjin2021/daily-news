param(
    [string]$Query = "AI Agent",
    [int]$MaxItems = 12,
    [ValidateSet("brief", "standard", "deep")]
    [string]$Depth = "standard",
    [switch]$FromCache
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    python -m venv .venv
}

& $python -c "import feedparser, trafilatura, yaml" 2>$null
if ($LASTEXITCODE -ne 0) {
    & $python -m pip --isolated install -r requirements.txt
}

$argsList = @("scripts\report.py", "--query", $Query, "--max-items", $MaxItems, "--depth", $Depth, "--print")
if ($FromCache) {
    $argsList += "--from-cache"
}

& $python @argsList
