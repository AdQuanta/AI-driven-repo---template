[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

function Ensure-DiscoveryLink {
    param(
        [Parameter(Mandatory = $true)]
        [string]$LinkPath,

        [Parameter(Mandatory = $true)]
        [string]$TargetPath
    )

    $resolvedTarget = Resolve-Path -LiteralPath $TargetPath -ErrorAction Stop
    if (-not (Test-Path -LiteralPath $resolvedTarget.ProviderPath -PathType Container)) {
        throw "Canonical discovery target is not a directory: $TargetPath"
    }

    $existingItem = Get-Item -LiteralPath $LinkPath -Force -ErrorAction SilentlyContinue
    if ($null -ne $existingItem) {
        if (-not ($existingItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw "Refusing to replace non-link path: $LinkPath"
        }

        $existingTarget = [string]$existingItem.Target
        if ([string]::IsNullOrWhiteSpace($existingTarget)) {
            throw "Unable to determine the target of existing link: $LinkPath"
        }
        if (-not [IO.Path]::IsPathRooted($existingTarget)) {
            $existingTarget = Join-Path $existingItem.Parent.FullName $existingTarget
        }

        $resolvedExistingTarget = Resolve-Path -LiteralPath $existingTarget -ErrorAction SilentlyContinue
        if ($null -eq $resolvedExistingTarget) {
            throw "Existing discovery link is broken: $LinkPath"
        }
        if (-not [string]::Equals(
                $resolvedExistingTarget.ProviderPath.TrimEnd('\', '/'),
                $resolvedTarget.ProviderPath.TrimEnd('\', '/'),
                [StringComparison]::OrdinalIgnoreCase)) {
            throw "Existing discovery link points to the wrong target: $LinkPath"
        }

        Write-Host "Already configured: $LinkPath -> $TargetPath"
        return
    }

    $linkType = if ($env:OS -eq "Windows_NT") { "Junction" } else { "SymbolicLink" }
    New-Item -ItemType $linkType -Path $LinkPath -Target $resolvedTarget.ProviderPath | Out-Null
    Write-Host "Created ${linkType}: $LinkPath -> $TargetPath"
}

$repositoryRoot = Split-Path -Parent $PSScriptRoot
Ensure-DiscoveryLink `
    -LinkPath (Join-Path $PSScriptRoot "skills") `
    -TargetPath (Join-Path $repositoryRoot ".agents\skills")

# Never link .claude/agents to .github/agents: VS Code Copilot scans both
# folders, lists every agent twice, and then fails to resolve them.
$agentsLink = Get-Item -LiteralPath (Join-Path $PSScriptRoot "agents") -Force -ErrorAction SilentlyContinue
if ($null -ne $agentsLink -and ($agentsLink.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
    $agentsLink.Delete()
    Write-Host "Removed runtime link .claude\agents (it duplicates agents in VS Code Copilot)."
}

Write-Host "Claude Code skill discovery link is ready."