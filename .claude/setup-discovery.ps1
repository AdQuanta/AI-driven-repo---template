# Creates the ignored .claude/skills link to the canonical .agents/skills
# (Windows: a junction, no elevation needed). Safe to run repeatedly.
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

function Fail([string]$Message) {
    Write-Host "setup-discovery: $Message"
    exit 1
}

function Resolve-LinkTarget($Item) {
    $target = [string]$Item.Target
    if ([string]::IsNullOrWhiteSpace($target)) { return $null }
    if (-not [IO.Path]::IsPathRooted($target)) {
        $target = Join-Path (Split-Path -Parent $Item.FullName) $target
    }
    $resolved = Resolve-Path -LiteralPath $target -ErrorAction SilentlyContinue
    if ($null -eq $resolved) { return $null }
    return $resolved.ProviderPath.TrimEnd('\', '/')
}

$claudeDir = $PSScriptRoot
$repositoryRoot = Split-Path -Parent $claudeDir
$agentsPath = Join-Path $claudeDir "agents"
$skillsTarget = Join-Path $repositoryRoot ".agents\skills"
$linkPath = Join-Path $claudeDir "skills"

# 1. Validate before creating anything.
$agentsItem = Get-Item -LiteralPath $agentsPath -Force -ErrorAction SilentlyContinue
if ($null -eq $agentsItem -or -not $agentsItem.PSIsContainer) {
    Fail "missing .claude\agents; restore the tracked directory from Git."
}
if ($agentsItem.Attributes -band [IO.FileAttributes]::ReparsePoint) {
    Fail ".claude\agents is a link; replace it with the tracked directory from Git."
}
if (-not (Test-Path -LiteralPath $skillsTarget -PathType Container)) {
    Fail ".agents\skills not found; run this from a complete clone."
}
$resolvedTarget = (Resolve-Path -LiteralPath $skillsTarget).ProviderPath.TrimEnd('\', '/')

# 2. Inspect an existing .claude\skills.
$existing = Get-Item -LiteralPath $linkPath -Force -ErrorAction SilentlyContinue
if ($null -ne $existing) {
    if (-not ($existing.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        Fail ".claude\skills exists and is not a link; move it aside and rerun (edit skills only in .agents\skills)."
    }
    if ((Resolve-LinkTarget $existing) -ne $resolvedTarget) {
        Fail ".claude\skills points elsewhere; remove that link and rerun."
    }
    Write-Host "setup-discovery: already configured: .claude\skills -> .agents\skills"
    exit 0
}

# 3. Create, then 4. confirm.
$linkType = if ($env:OS -eq "Windows_NT") { "Junction" } else { "SymbolicLink" }
New-Item -ItemType $linkType -Path $linkPath -Target $resolvedTarget | Out-Null
$created = Get-Item -LiteralPath $linkPath -Force -ErrorAction SilentlyContinue
if ($null -eq $created -or
    -not ($created.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
    (Resolve-LinkTarget $created) -ne $resolvedTarget) {
    Fail "creating the $linkType did not produce a working link at .claude\skills."
}

# 5. Report.
Write-Host "setup-discovery: created $linkType .claude\skills -> .agents\skills"
