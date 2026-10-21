# latex-full-build.ps1
# Builds the LaTeX project whose root main.tex is in $ProjectDir, keeping all
# intermediates in $ProjectDir\.latex_build. The VS Code LaTeX tasks and agents
# both call this script; see docs/agent-guidance/vscode-latex-environment.md.
#
#   -Step All           pdflatex -> bibliography -> pdflatex -> pdflatex, then summary (default)
#   -Step Pass          one pdflatex pass
#   -Step Bibliography  bibtex if main.aux has \bibdata, else biber if main.bcf exists
#   -Step FinalPass     one pdflatex pass, then summary
#   -Quiet              hide tool output; status lines and the summary still print

param(
    [Parameter(Mandatory)][string]$ProjectDir,
    [ValidateSet('All', 'Pass', 'Bibliography', 'FinalPass')][string]$Step = 'All',
    [switch]$Quiet
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path (Join-Path $ProjectDir 'main.tex'))) {
    Write-Host "No main.tex in '$ProjectDir' - nothing to build."
    exit 1
}

# Two builds writing the same main.aux corrupt it, so refuse to start while one runs.
$busy = Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -match '^(miktex-)?(pdflatex|pdftex|bibtex|biber)$' }
if ($busy) {
    Write-Host "A LaTeX build is already running ($(($busy.ProcessName | Sort-Object -Unique) -join ', ')). Wait for it to finish."
    exit 2
}

function Invoke-Tool([string]$Label, [string]$Exe, [string[]]$ToolArgs) {
    Write-Host "== $Label"
    if ($Quiet) { & $Exe @ToolArgs | Out-Null } else { & $Exe @ToolArgs }
    if ($LASTEXITCODE -ne 0) {
        Write-Host "$Label failed (exit $LASTEXITCODE); see .latex_build\main.log or .blg."
        exit $LASTEXITCODE
    }
}

function Invoke-Pass([string]$Label) {
    Invoke-Tool $Label 'pdflatex' @('-synctex=1', '-interaction=nonstopmode', '-halt-on-error',
        '-file-line-error', '--aux-directory=.latex_build', 'main.tex')
}

function Invoke-Bibliography {
    if ((Test-Path '.latex_build/main.aux') -and
        (Select-String -LiteralPath '.latex_build/main.aux' -SimpleMatch -Pattern '\bibdata{' -Quiet)) {
        Invoke-Tool 'bibtex' 'bibtex' @('.latex_build/main')
    } elseif (Test-Path '.latex_build/main.bcf') {
        Invoke-Tool 'biber' 'biber' @('--input-directory=.latex_build', '--output-directory=.latex_build', 'main')
    } else {
        Write-Host '== No bibliography pass required.'
    }
}

function Write-Summary {
    $log = Get-Content -LiteralPath '.latex_build/main.log'
    $pages = $log | Select-String -Pattern 'Output written on main\.pdf \((\d+) pages?' | Select-Object -Last 1
    $undefined = @($log | Select-String -Pattern 'undefined' | Where-Object { $_.Line -match 'Warning' })
    $overfull = @($log | Select-String -Pattern '^Overfull')
    Write-Host '== Summary'
    if ($pages) { Write-Host "Pages: $($pages.Matches[0].Groups[1].Value)" } else { Write-Host 'Pages: no PDF written' }
    Write-Host "Undefined references/citations: $($undefined.Count)"
    $undefined | Select-Object -First 10 | ForEach-Object { Write-Host "  $($_.Line)" }
    Write-Host "Overfull boxes: $($overfull.Count)"
    $overfull | Select-Object -First 10 | ForEach-Object { Write-Host "  $($_.Line)" }
}

# Push/Pop keeps the caller's working directory unchanged, even on exit.
Push-Location -LiteralPath $ProjectDir
try {
    if (-not (Test-Path '.latex_build')) { New-Item -ItemType Directory -Path '.latex_build' | Out-Null }
    switch ($Step) {
        'Pass'         { Invoke-Pass 'pdflatex' }
        'Bibliography' { Invoke-Bibliography }
        'FinalPass'    { Invoke-Pass 'pdflatex'; Write-Summary }
        'All' {
            Invoke-Pass 'pdflatex (1/3)'
            Invoke-Bibliography
            Invoke-Pass 'pdflatex (2/3)'
            Invoke-Pass 'pdflatex (3/3)'
            Write-Summary
        }
    }
} finally {
    Pop-Location
}
exit 0
