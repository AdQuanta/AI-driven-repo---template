# Project Skill Registry

This is the human-readable index of project skills. When adding, removing, or
renaming a skill, update this file and follow
[`skill-maintenance`](../skill-maintenance/SKILL.md).

| Skill | File | Use When |
|---|---|---|
| brainstorming | `.agents/skills/brainstorming/SKILL.md` | Brainstorming, designing a feature, exploring requirements, or comparing approaches. |
| latex-build | `.agents/skills/latex-build/SKILL.md` | LaTeX builds, `latexmk`, compilation, or live preview tasks. |
| latex-paper-en | `.agents/skills/latex-paper-en/SKILL.md` | English academic LaTeX paper editing, proofreading, bibliography fixes, submission checks, or algorithm block cleanup. |
| literature-review | `.agents/skills/literature-review/SKILL.md` | Systematic literature reviews, meta-analyses, or comprehensive research synthesis. |
| math | `.agents/skills/math/SKILL.md` | Computing, solving, simplifying, integrating, differentiating, eigenvalue work, or matrix math. |
| research-gap-explorer | `.agents/skills/research-gap-explorer/SKILL.md` | Exploring literature gaps, open research questions, or high-level research idea matrices. |
| skill-maintenance | `.agents/skills/skill-maintenance/SKILL.md` | Adding, editing, renaming, removing, or reviewing project skills and their metadata. |
| writing-plans | `.agents/skills/writing-plans/SKILL.md` | Writing implementation plans or task breakdowns for multi-step work. |

## Dependencies To Satisfy Before First Use

| Skill | Needs |
|---|---|
| latex-paper-en | `uv` on `PATH`; a TeX distribution with `pdflatex`/`xelatex`/`latexmk`/`bibtex`/`biber`/`chktex`; a harness that sets `$SKILL_DIR` (otherwise substitute `.agents/skills/latex-paper-en`). Repository build commands in `docs/agent-guidance/vscode-latex-environment.md` override its generic `latexmk` default. |
| latex-build | `latexmk` on `PATH` and a SyncTeX-capable PDF viewer. |
| literature-review | Python plus network access for its bundled `scripts/`. |
| research-gap-explorer | A live web-search tool in the harness. |
| brainstorming | Optional visual companion needs Node.js and a POSIX shell. |
| math | The Python packages in the root `requirements.txt`; smoke test: `.venv\Scripts\python.exe .agents\skills\math\scripts\cc_math\sympy_compute.py solve "x**2 - 4" --var x`. |

Any further skill requires a portability review (read it end to end, list every
tool, package, path, agent, and harness feature it assumes, confirm each exists,
and record the validation evidence) before it is added here.
