# Example: Translation And De-AI

User request:
Translate a Chinese technical paragraph into academic English, preserve `\cite{}` and math, then flag any AI-sounding phrases in the introduction.

Recommended module sequence:
1. `translation`
2. `deai`

Commands:
```bash
python -B .agents/skills/latex-paper-en/scripts/translate_academic.py input_zh.txt --domain deep-learning
python -B .agents/skills/latex-paper-en/scripts/deai_check.py main.tex --section introduction
```

Expected output:
- A translation report that keeps LaTeX fragments intact.
- `% DE-AI ...` findings that identify risky phrases without changing citations, labels, or equations.
