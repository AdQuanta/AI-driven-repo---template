# Module: Format Check

**Trigger**: format, chktex, lint, 格式检查

## Commands

```bash
python -B .agents/skills/latex-paper-en/scripts/check_format.py main.tex
python -B .agents/skills/latex-paper-en/scripts/check_format.py main.tex --strict
```

## Details
Raw script output: PASS / WARN / FAIL with categorized issues.
Skill-layer response: summarize the actionable findings as LaTeX-friendly review comments.
Ensure the document compiles before checking formats iteratively.

