# Research Project Template

Author: **Nir Gutman**  |  created: May 2026

A GitHub repository template that integrates **code**, **publications**, and **research** in one project — synchronized through shared AI agent instructions, a literature knowledge base, a LaTeX change-marking system, and a set of reusable skills.

## What's included

| Layer | What you get |
|---|---|
| **Agent instructions** | `.github/copilot-instructions.md` — global rules for Claude Code & GitHub Copilot; sector-scoped instructions for `code/`, `publications/`, `research/` |
| **Literature agents** | `find-papers` (semantic search over your knowledge base) and `ingest-paper` (adds papers with summaries and BibTeX) |
| **LaTeX marking module** | `publications/modules/markings/` — highlight changes/missing content; `approve-changes-markings` prompt to strip them for submission |
| **Example paper** | `publications/paper/` — compilable template with Mark API examples, config, and a placeholder section |
| **Skills** | Locally authored skills in `.github/skills/`; external skills tracked in `skills-lock.json` |
| **Prompts & agents** | AI Judge, Task Orchestrator, TodoList Resolver, and more |
| **VS Code config** | LaTeX Workshop recipes, Python path setup, terminal auto-approval rules |

---

## Quick start

### 1. Use this as a GitHub template

Click **"Use this template"** → **"Create a new repository"**.

### 2. Update workspace paths

**Critical:** several agent files contain placeholder paths that must be updated before the agents work correctly.

Open `.github/agents/find-papers.agent.md` and replace every occurrence of:
```
<WORKSPACE_ROOT>
```
with the absolute path to your repository root (e.g., `C:\Users\you\repos\my-project` or `/home/you/repos/my-project`).

### 3. Update the project description

Edit `.github/copilot-instructions.md`:
- Replace the `[TODO]` block in **"What Is This Study About?"** with your project's description.
- Update the **Skill Registry** table if you add or remove skills.

### 4. Install external skills

```bash
npx skills install
```

This reads `skills-lock.json` and downloads all external skills from [skills.sh](https://www.skills.sh) into `.github/skills/`.

### 5. Set up LaTeX

Install a TeX distribution (e.g., [MiKTeX](https://miktex.org/) or [TeX Live](https://tug.org/texlive/)) and open `publications/paper/main.tex` in VS Code with the [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop) extension.

---

## Repository structure

```
.github/
├── copilot-instructions.md   ← Global agent instructions (edit this, not CLAUDE.md)
├── instructions/             ← Sector-scoped instructions (code, publications, research)
├── agents/                   ← find-papers, ingest-paper, ai-judge, task-orchestrator, ...
├── prompts/                  ← approve-changes-markings, todolist-resolver
├── skills/                   ← Locally authored skills (+ external via skills-lock.json)
└── docs/                     ← How the shared-AI-instruction system works

code/
├── src/                      ← Core Python modules
├── tests/                    ← Automated tests (run: python -m pytest from code/)
└── scripts/                  ← Exploration scripts and figure generators

publications/
├── modules/markings/         ← Reusable LaTeX marking module
└── paper/                    ← Main manuscript (config.tex, main.tex, sections/, figures/)

research/
├── derivations/              ← Worked mathematical derivations
└── references/scientific_papers/   ← Ingested literature (find-papers / ingest-paper)

artifacts/                    ← Generated outputs (figures, data) — gitignored
_agents_outputs/              ← Agent results for human review
└── _agents_dump/             ← Interim agent files (gitignored, cleaned up after use)
```

---

## The Mark API (for publications)

AI agents working on LaTeX are guided to wrap their edits with the Mark API, so that changes and placeholders appear visually highlighted in the compiled PDF — `changes` in yellow, `missing` in red.

```latex
% Inline text change
\Mark{changes}{This sentence was revised.}

% Block paragraph change
\begin{MarkEnv}{changes}[text]
This whole paragraph is new.
\end{MarkEnv}

% New equation
\begin{MarkEnv}{changes}[math]
E = mc^2
\end{MarkEnv}

% Missing content placeholder
\Mark{missing}{TODO: describe the experimental setup here.}
```

When you're happy with the edits and ready to clean up the markings, run the approval prompt from GitHub Copilot Chat:

```
/approve-changes-markings
```

This strips all `changes` wrappers (leaving the content) so the PDF is clean for submission.

---

## Literature workflow

> The examples below use GitHub Copilot Chat's `@agent` invocation syntax.

1. **Find papers** — invoke the `find-papers` agent with a query:
   ```
   @find-papers "your research topic"
   ```
2. **Ingest a paper** — invoke `ingest-paper` with a PDF path or URL:
   ```
   @ingest-paper https://arxiv.org/abs/xxxx.xxxxx
   ```
3. **Cite in derivations** — use relative markdown links to `summary.md` files in `research/references/`.

---

## Customizing for your project

- **Change the study description:** edit the "What Is This Study About?" section in `.github/copilot-instructions.md`.
- **Change the paper categories:** edit the category hierarchy in `.github/instructions/research.instructions.md`.
- **Change Mark API roles/colors:** edit `publications/paper/config.tex` (`\DefineMarkRole` calls).
- **Add a new skill:** create `.github/skills/<name>/SKILL.md` and add a row to the Skill Registry table in `copilot-instructions.md`.
- **Add global instructions:** edit `.github/copilot-instructions.md` directly (never edit `CLAUDE.md`).
- **Add sector-scoped instructions:** edit the matching `.github/instructions/*.instructions.md` file.
