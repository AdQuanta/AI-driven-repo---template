# find-latex-root.ps1
# Walks up from $FileDirname toward $WorkspaceFolder looking for main.tex.
# Outputs the directory path that contains main.tex, or exits with code 1 if not found.

param(
    [Parameter(Mandatory)][string]$FileDirname,
    [Parameter(Mandatory)][string]$WorkspaceFolder
)

$dir = $FileDirname
while ($dir -ne $WorkspaceFolder -and -not (Test-Path "$dir\main.tex")) {
    $dir = Split-Path $dir -Parent
}

if (-not (Test-Path "$dir\main.tex")) {
    Write-Host "No main.tex found between '$FileDirname' and '$WorkspaceFolder' - nothing to build."
    exit 1
}

Write-Output $dir
