# Example: Figures And Title

User request:
Before I submit to ACM, check whether my figures are publication-ready and whether the title is too generic.

Recommended module sequence:
1. `figures`
2. `title`

Commands:
```bash
python -B .agents/skills/latex-paper-en/scripts/check_figures.py main.tex
python -B .agents/skills/latex-paper-en/scripts/optimize_title.py main.tex --check
```

Expected output:
- Figure warnings about missing files, DPI, or caption/extension issues.
- Title score with concrete title-improvement suggestions.
