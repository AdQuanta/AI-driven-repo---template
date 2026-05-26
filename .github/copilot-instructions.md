# Copilot Instructions

## Project Vision
This repository has three sectors:
- **research**: cross-media research truths, concepts, and planning notes.
- **code**: Python simulations, algorithms, demonstrations and experiments for the study.
- **publications**: authored deliverables produced from the research (like paper and presentations).

We combine these 3 sectors into a single project to allow for seamless integration of research insights, code development, and paper writing. Each sector has its own folder and specific instructions to guide work in that area, but they are all interconnected and should be developed with awareness of the others.

## What Is This Study About?

<!-- [TODO: Replace this section with a description of your specific research project.
     Include: the core problem, the main contribution, the key technical approach, and the goal.
     Example structure below — delete and replace with your own content.] -->

**[TODO: Project Name]** introduces **[TODO: brief description of the main technical contribution]**.
Instead of **[TODO: describe what is typically done]**, it **[TODO: describe what this work does differently]**.
The goal is **[TODO: describe the main research goal and expected impact]**.

## Sector Instruction Loading
Sector-specific guidance is now handled with folder-scoped instruction files:

- [code sector](instructions/code.instructions.md) for files in `code/**`
- [publications sector](instructions/publications.instructions.md) for files in `publications/**`
- [research sector](instructions/research.instructions.md) for files in `research/**`

### Fallback Rule
If a sector instruction file is missing, explicitly warn the user.


## output folders and dumps:
- Interim files used for agents processes should be placed in `_agents_outputs/_agents_dump/`, and should be cleaned up after use. This folder is ignored by git. **If this folder does not exist, create it before writing into it.**

- Final outputs meant for human consumption should be placed in `_agents_outputs/`.

- For code-sector script artifacts, use `artifacts/` (repo root) as the canonical generated-output root (with figures in `artifacts/figures/`).

## Paper Figure Source Of Truth
- Generated figures may be created under `artifacts/figures/`, but manuscript source files under `publications/paper/` must not reference `artifacts/` directly.
- If a figure is used by the paper, copy the final asset into `publications/paper/figures/` and reference it there (or place TikZ sources in `publications/paper/figures/tikz_art/`).
- Treat `publications/paper/figures/` as the Git-tracked source of truth for paper figures. Remove stale paper-local copies when a figure is no longer used.

## Answering Research Questions
When the user asks a conceptual, theoretical, or literature question about this study:
1. **Check `research/derivations/`** first — if the answer is likely a derived result, browse the relevant subfolder for worked derivations.
2. **Invoke the `find-papers` sub-agent** to search the literature knowledge base in `research/references/scientific_papers/`. Pass a concise query reflecting the user's question.
3. Synthesize the answer from both sources before responding.

### Ingesting Papers Found Online
If, while answering a research question, the agent identifies a relevant paper from an online source (e.g., arXiv, a publisher page, or a web search result) that is **not already in the knowledge base**:
- **Invoke the `ingest-paper` sub-agent** to add the paper before (or immediately after) citing it in the response.
- Pass the paper's URL, DOI, or file path as the argument to `ingest-paper`.
- The `ingest-paper` agent runs a deduplication check automatically — if the paper is already ingested, it will detect the match and stop without creating duplicates. It is safe to invoke it even when unsure.
- `ingest-paper` may need to create a **new sub-category folder** inside `research/references/scientific_papers/` if no existing category fits — this is expected and allowed.

### Saving New Derivations
If answering a research question requires working out a mathematical result or analytical derivation that does not already exist in `research/derivations/`, save it there following the structure and citation conventions in `research.instructions.md` ("Derivation Files — Structure and Citation Practice").

## Git operation ownership
- Do not ask me to commit, stage, or push Git changes. I will handle all Git operations myself unless I explicitly ask for them.

## Skill Authorship Metadata
Every skill in `.github/skills/` must declare authorship in its YAML frontmatter. The full convention is documented in [`.github/skills/docs/README.md`](skills/docs/README.md). Summary:

- **Installed from [skills.sh](https://www.skills.sh)** (listed in `skills-lock.json`): add `author: skills.sh` + `source: "https://www.skills.sh/{user}/{repo}/{name}"`.
- **Written locally**: add `author: <your-github-handle>`.

Maintain this when adding any new skill.

## Shared AI Instruction Layout
- `.github/copilot-instructions.md` is the single source of truth for global agent instructions.
- The repository root `CLAUDE.md` must contain exactly `@.github/copilot-instructions.md` so Claude Code loads the same global instructions.
- For each folder-scoped instruction file under `.github/instructions/`, create a `CLAUDE.md` file in the target folder that imports the matching instruction file.
- Do not duplicate global instructions in `CLAUDE.md`; edit `.github/copilot-instructions.md` instead.

## Skill Registry
When a user message matches a trigger, load and follow the linked `SKILL.md` before responding.

| Skill | SKILL.md | Triggers |
|---|---|---|
| brainstorming | `.github/skills/brainstorming/SKILL.md` | brainstorm, design a feature, explore requirements, compare approaches |
| find-skills | `.github/skills/find-skills/SKILL.md` | find a skill, is there a skill for, how do I do X, extend capabilities |
| latex-build | `.github/skills/latex-build/SKILL.md` | latexmk, LaTeX build, live preview, compile LaTeX |
| latex-paper-en | `.github/skills/latex-paper-en/SKILL.md` | proofread my paper, fix my LaTeX, bibliography errors, Algorithm 1, prepare for submission |
| literature-review | `.github/skills/literature-review/SKILL.md` | literature review, systematic review, meta-analysis, research synthesis, state of the art |
| math | `.github/skills/math/SKILL.md` | calculate, compute, solve, integrate, derivative, eigenvalue, matrix, simplify |
| networkx | `.github/skills/networkx/SKILL.md` | graph analysis, shortest path, centrality, clustering, community detection, network topology |
| pdf | `.github/skills/pdf/SKILL.md` | PDF, merge PDF, split PDF, OCR PDF, extract PDF text, watermark PDF |
| powershell-safe-commands | `.github/skills/powershell-safe-commands/SKILL.md` | PowerShell command, auto-approve, safe terminal command, approval prompt |
| pptx | `.github/skills/pptx/SKILL.md` | pptx, presentation, slides, slide deck, deck |
| research-gap-explorer | `.github/skills/research-gap-explorer/SKILL.md` | research gaps, brainstorm literature gaps, open research questions, idea matrix |
| scientific-visualization | `.github/skills/scientific-visualization/SKILL.md` | publication figure, matplotlib figure, seaborn plot, plotly chart, journal-ready plot |
| subagent-driven-development | `.github/skills/subagent-driven-development/SKILL.md` | execute implementation plan, independent tasks, subagent workflow |
| writing-plans | `.github/skills/writing-plans/SKILL.md` | implementation plan, write a plan, multi-step task, task breakdown |
| writing-skills | `.github/skills/writing-skills/SKILL.md` | create a skill, edit a skill, verify a skill, skill authoring |

## Knowledge Preservation
When a conversation surfaces a new convention, coding pattern, or hard-won lesson:

1. **Write it into the project** — the right place is the relevant sector instruction file (`code.instructions.md`, `publications.instructions.md`, `research.instructions.md`) or this file for cross-sector concerns. A lesson that only lives in an agent's personal memory file is invisible to the user and to other agents working in this repo.
2. **Personal memory (`/memories/`) is supplementary** — it can hold a pointer or summary, but the authoritative record must be in the repo.
3. **If a section doesn't exist yet, add it.** Don't skip preservation because there's no obvious heading to append to.

## Terminal command discipline (auto-approve friendliness)
VS Code Copilot auto-approves terminal commands that are **atomic and recognizable**. Complex multi-step scripts are not auto-approvable, even when individually safe. Follow these rules for every terminal command:

1. **One logical action per command.** Do not chain unrelated operations with `;`. A mkdir and a download are two commands, not one.
2. **No `$variable` indirection** for paths when avoidable. Prefer inlining the full path so the command is self-explanatory.
3. **No multi-line scripts or blocks** (no `foreach`, no `if/else`, no `@{}` hashtables) unless the entire block is a single logical step.
4. **Network fetches are one command = one file.** Use `python -c "import urllib.request; urllib.request.urlretrieve('<url>', r'<path>')"` for downloading files — NOT `curl.exe` or `Invoke-WebRequest`. Neither has an approval entry and will always prompt. Python urllib is pre-approved in `.vscode/settings.json`.
5. **Verification steps are separate commands.** Do not attach `Write-Host` result checks to the operation itself.
6. **`python urllib.request.urlretrieve` to trusted academic domains is pre-approved** via `.vscode/settings.json`. The following domains auto-approve without a prompt: `arxiv.org`, `doi.org`, `nature.com`, `link.springer.com`, `ieeexplore.ieee.org`, `dl.acm.org`, `link.aps.org`, `quantum-journal.org`, `semanticscholar.org`, `opg.optica.org`. Issue fetches to these domains directly. For any other domain, ask the user to add it to the allow list in `.vscode/settings.json` before fetching.
7. **NEVER use shell redirect operators** (`>`, `2>`, `2>&1`, `*>`). None have generic approval entries, so they will prompt unless an exact-match regex is added to `settings.json`. To run a Python script and capture output: just run `.venv\Scripts\python.exe code/scripts/figures/script.py` (no redirects) and then use the `get_terminal_output` tool to read what was printed. The terminal captures both stdout and stderr. This is the ONLY approved pattern for running scripts.
8. **Never use bare `python` for script execution.** Always use `.venv\Scripts\python.exe` (full venv path) or ensure the script path contains `code\scripts\` — both are pre-approved as substring patterns in `.vscode/settings.json`. Bare `python script.py` is NOT auto-approved.
9. **PDF file verification is pre-approved** via the pattern `python -c "import os; f=r'<path>'; print(os.path.getsize(f), open(f,'rb').read(5))"`. Use exactly this form to confirm a downloaded PDF is non-empty and starts with `%PDF-` (the first 5 bytes of any valid PDF).
