# Example: Experiment Review

User request:
Review the experiments section for weak baselines, missing ablations, and unsupported claims, but do not rewrite the paper text.

Recommended module sequence:
1. `experiment`

Commands:
```bash
python -B .agents/skills/latex-paper-en/scripts/analyze_experiment.py main.tex --section experiments
```

Expected output:
- Reviewer-style `% EXPERIMENT ...` findings tied to concrete lines.
- Warnings about generic baselines, missing metrics, missing ablation/statistical evidence, or overclaiming.
