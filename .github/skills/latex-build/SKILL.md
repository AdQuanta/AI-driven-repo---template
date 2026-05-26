---
name: latex-build
description: LaTeX builds with latexmk and live preview. TRIGGERS - latexmk, LaTeX build, live preview, compilation.
allowed-tools: Read, Edit, Bash
author: NGBigField
---

# LaTeX Build Automation

## When to Use This Skill

Use this skill when:

- Compiling LaTeX documents
- Setting up live preview with auto-rebuild
- Managing multi-file projects
- Troubleshooting build failures
- Cleaning build artifacts
- Automating compilation workflows

## Why latexmk?

Industry standard build tool:

- Auto-detects dependencies (bibliography, index, etc.)
- Runs correct number of times (handles cross-references)
- Live preview mode watches for file changes
- Works with Skim for SyncTeX auto-reload
- Bundled with MacTeX (no separate install needed)

---

## Basic Usage

### One-Time Build

```bash
latexmk -pdf document.tex
# Result: document.pdf created
```

### Live Preview (Watch Mode)

```bash
latexmk -pvc -pdf document.tex
# Compiles, then watches for file changes and auto-recompiles
```

**Stop watching:** Press `Ctrl+C`

---

## Quick Reference Card

```bash
# Build once
latexmk -pdf document.tex

# Live preview (watch mode)
latexmk -pvc -pdf document.tex

# Build with SyncTeX
latexmk -pdf -synctex=1 document.tex

# Clean artifacts
latexmk -c              # Keep PDF
latexmk -C              # Remove PDF too

# Force rebuild
latexmk -gg -pdf document.tex

# Non-interactive (for CI)
latexmk -pdf -interaction=nonstopmode document.tex
```

---

## VS Code + LaTeX Workshop (this project)

This project uses **LaTeX Workshop** (not latexmk directly). The VS Code settings in `.vscode/settings.json` configure:
- `pdfLaTeX (quick)` recipe: one pdflatex pass for fast previews
- `pdfLaTeX -> Biber -> pdfLaTeX x2 (full)` recipe: full build with bibliography
- Aux files go into `.latex_build/` to keep the source folder clean

Use the LaTeX Workshop panel in VS Code to select which recipe to run.

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| latexmk not found | Not in PATH | Add TeX distribution bin to PATH |
| Undefined control sequence | Missing package | Check `\usepackage` statements |
| References show ?? | Need multiple runs | latexmk handles this automatically |
| Live preview not updating | Viewer auto-reload disabled | Enable in viewer preferences |
| Build hangs | Input prompt in nonstop mode | Use `-interaction=nonstopmode` flag |
| PDF not updating | Build error | Check .log file for specific error |
| SyncTeX not working | Missing -synctex=1 flag | Add `-synctex=1` to build command |
