# Research Project Template

Author: **Nir Gutman**  |  created: May 2026

A GitHub repository template that integrates **code**, **publications**, and
**research** in one project, kept consistent through one set of AI-agent
instructions shared by GitHub Copilot (VS Code) and Claude Code, a literature
knowledge base with citation-auditing agents, a LaTeX change-marking system,
and a small set of portable skills.

## What's included

| Layer | What you get |
|---|---|
| **Agent instructions** | Root [`AGENTS.md`](AGENTS.md) plus sector files [`code/AGENTS.md`](code/AGENTS.md), [`research/AGENTS.md`](research/AGENTS.md), [`publications/AGENTS.md`](publications/AGENTS.md). [`CLAUDE.md`](CLAUDE.md) only imports `@AGENTS.md`. |
| **Guidance docs** | [`docs/agent-guidance/`](docs/agent-guidance/) — project layout, Git policy, LaTeX build environment. |
| **TODO queue** | [`docs/todo/`](docs/todo/README.md) — one dated file per topic, resolved items archived. |
| **Skills** | [`.agents/skills/`](.agents/skills/docs/registry.md) — brainstorming, writing-plans, math, latex-build, latex-paper-en, literature-review, research-gap-explorer, skill-maintenance. |
| **Literature agents** | [`.github/agents/`](.github/agents/) — `ingest-paper`, `find-papers`, `citation-audit` (+ `citation-reader`, `citation-checker`) with a test fixture. |
| **LaTeX marking module** | [`publications/modules/markings/`](publications/modules/markings/) — highlight `changes`/`missing`; the `approve-changes-markings` prompt strips them for submission. |
| **Example paper** | [`publications/paper---example/`](publications/paper---example/) — compilable starter manuscript. |
| **Code sector** | `code/src`, `code/scripts`, `code/tests` with a pytest gate and CI ([`.github/workflows/tests.yml`](.github/workflows/tests.yml)). |
| **VS Code config** | [`.vscode/settings.json`](.vscode/settings.json) — nested `AGENTS.md` loading, LaTeX Workshop recipe, terminal auto-approval. |

---

## Quick start

1. **Create your repository** — click **"Use this template"** → **"Create a new repository"**, then clone it.
2. **Create the Python environment** (Python 3.11+), from the repository root:

   ```powershell
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt -r code\requirements.txt
   ```

   (macOS/Linux: `.venv/bin/python -m pip install ...`.)
3. **Enable Claude Code skill discovery** (once per clone; skip if you only use Copilot):

   ```powershell
   .\.claude\setup-discovery.ps1
   ```

   It creates the git-ignored `.claude/skills` link to `.agents/skills`.
4. **Describe your study** — replace the TODO under **"What Is This Study About?"** in [`AGENTS.md`](AGENTS.md).
5. **Start your paper** — copy `publications/paper---example/` to `publications/paper---<slug>/` and edit it. Build it with the sequence in [`docs/agent-guidance/vscode-latex-environment.md`](docs/agent-guidance/vscode-latex-environment.md) (requires a TeX distribution such as [TeX Live](https://tug.org/texlive/) with `biber`).
6. **Check the code gate**:

   ```powershell
   Push-Location code; ..\.venv\Scripts\python.exe -m pytest; Pop-Location
   ```

No absolute paths need editing: every agent resolves the repository root with
`git rev-parse --show-toplevel`.

---

## Repository structure

See [`docs/agent-guidance/project-layout.md`](docs/agent-guidance/project-layout.md)
for the maintained map. In short:

```
AGENTS.md, CLAUDE.md          ← Root instructions (CLAUDE.md = @AGENTS.md)
requirements.txt              ← Dependencies of shared skill scripts
.agents/skills/               ← Project skills (+ docs/ registry and authorship)
.claude/setup-discovery.ps1   ← Creates the ignored .claude/skills link
.github/agents/               ← Literature and citation agents (+ tests/)
.github/prompts/              ← approve-changes-markings (+ scripts/)
.github/workflows/            ← CI: code-sector pytest
code/                         ← src/, scripts/, tests/, AGENTS.md, requirements.txt
research/                     ← derivations/, references/scientific_papers/, AGENTS.md
publications/                 ← modules/markings/, paper---example/, AGENTS.md
docs/                         ← agent-guidance/, todo/
artifacts/                    ← Generated data/figures (git-ignored)
_agents_outputs/              ← Agent results for human review
└── _agents_dump/             ← Interim agent files (git-ignored)
```

---

## The Mark API (for publications)

Agents editing LaTeX wrap their edits with the Mark API, so changes and
placeholders are highlighted in the compiled PDF — `changes` in yellow,
`missing` in red.

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

When you are ready to accept the edits, run the approval prompt from Copilot
Chat:

```
/approve-changes-markings
```

It strips all `changes` wrappers (keeping the content) and rebuilds the paper.

---

## Literature workflow

1. **Ingest a paper** — `@ingest-paper <PDF path or URL>` files it under
   `research/references/scientific_papers/<category>/<citation_key>/` with a
   `summary.md` and BibTeX.
2. **Find papers** — `@find-papers "your query"` ranks the knowledge base and
   writes the table to `_agents_outputs/find-papers/`.
3. **Audit citations** — `@citation-audit publications/paper---<slug>` checks
   every `\cite` against the cited paper itself and proposes marked fixes. The
   fixture in [`.github/agents/tests/citation-audit/`](.github/agents/tests/citation-audit/ANSWER_KEY.md)
   exercises the workflow.
4. **Cite in derivations** — link to `summary.md` files with relative markdown
   links (see [`research/AGENTS.md`](research/AGENTS.md)).

---

## Customizing for your project

- **Study description:** "What Is This Study About?" in `AGENTS.md`.
- **Paper categories:** the category hierarchy in `research/AGENTS.md` (starts empty).
- **Mark API roles/colors:** `\DefineMarkRole` calls in your paper's `config.tex`.
- **Skills:** follow [`.agents/skills/skill-maintenance/SKILL.md`](.agents/skills/skill-maintenance/SKILL.md) and update the [registry](.agents/skills/docs/registry.md). Edit skills only under `.agents/skills/`.
- **Instructions:** edit `AGENTS.md` or the sector `AGENTS.md` files directly. Never edit `CLAUDE.md` beyond its `@AGENTS.md` import.

## Git ownership

Agents do not stage, commit, or push unless you explicitly ask. See
[`docs/agent-guidance/git-policy.md`](docs/agent-guidance/git-policy.md).
