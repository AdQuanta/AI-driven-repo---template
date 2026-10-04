**Skill**: [LaTeX Build Automation](../SKILL.md)

## Troubleshooting

### Issue: latexmk Not Found

```bash
# Check installation
latexmk -v

# If not found, install a TeX distribution:
#   Windows: TeX Live (https://tug.org/texlive/) or MiKTeX
#   macOS:   MacTeX
#   Linux:   texlive-full (or your distro's TeX Live packages)
# Then make sure its bin directory is on PATH.
```

### Issue: PDF Not Auto-Reloading in the Viewer

**Check the viewer's auto-reload setting** (VS Code LaTeX Workshop reloads
automatically; SumatraPDF reloads on change; in Skim enable Preferences → Sync
→ "Check for file changes" and "Reload automatically").

**Verify SyncTeX enabled:**

```bash
latexmk -pdf -synctex=1 document.tex
# Should create document.synctex.gz
```

### Issue: Build Hangs on Error

```bash
# Use non-interactive mode
latexmk -pdf -interaction=nonstopmode document.tex

# Or in .latexmkrc:
$pdflatex = 'pdflatex -interaction=nonstopmode %O %S';
```

### Issue: Bibliography Not Updating

```bash
# Force rebuild of all dependencies
latexmk -gg -pdf document.tex

# Or clean and rebuild
latexmk -C && latexmk -pdf document.tex
```

### Issue: Compilation Errors Not Showing

```bash
# Use verbose mode
latexmk -pdf -verbose document.tex

# Check log file
less document.log
```

### Issue: Stale Auxiliary Files

```bash
# Clean all build artifacts
latexmk -C

# Rebuild from scratch
latexmk -pdf document.tex
```
