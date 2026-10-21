# Project Layout Reference

This is the shared reference for repository structure. Keep root instructions
short and point here when agents need the full map.

## Maintenance

Agents must update this map whenever a repository hierarchy change affects a
directory shown here.

When adding, removing, moving, renaming, or materially changing a path or
workflow listed in `reusable-research-project-blueprint.md`, always inspect that
blueprint and update it when necessary. Also inspect it when introducing a new
structure or workflow that could become part of the standard for similar
AI-assisted research projects.

## Repository Structure

This repository directly owns and maintains all AI-agent infrastructure.
`AGENTS.md`, `.agents/skills/`, and `.claude/agents/` are edited directly, as
are the sector `AGENTS.md` files below. There is no generation, sync, or
projection step. Which platform reads which location is described in
`cross-platform-ai-support.md`.

- `AGENTS.md` — Root agent instructions; edited directly
- `CLAUDE.md` — `@AGENTS.md` import for Claude Code; edited directly
- `README.md` — Template purpose, first-clone setup, and verification
- `requirements.txt` — Root dependency manifest for the shared `.venv`
- `.agents/skills/` — Project skills; edited directly
  - `.agents/skills/docs/registry.md` — Skill index
- `.agents/tests/` — Fixtures for exercising custom agents (`citation-audit`,
  `ai-judge`, `task-orchestrator`, `approve-changes-markings`), each with its
  own `README.md`; kept outside the agent folder so no harness loads them as
  agents
- `.claude/agents/` — Custom agents; edited directly
- `.claude/skills` — Ignored link to `.agents/skills/` for Claude Code; never
  edit through it
- `.claude/setup-discovery.ps1` — Windows: creates the ignored `.claude/skills`
  junction
- `.claude/setup-discovery.sh` — Linux/macOS: creates the same link as a symlink
- `.github/workflows/` — CI: code tests, knowledge-base and marker-finder
  tests, discovery setup, and the example paper build
- `.vscode/` — Shared, machine-independent LaTeX settings, tasks, and the two
  build scripts the tasks call; see `vscode-latex-environment.md`
- `code/` — The project's code, simulations, and experiments
  - `code/AGENTS.md` — Code-sector instructions; edited directly
  - `code/src/` — Importable library modules, starting with `code_paths.py`
  - `code/scripts/` — Data-generation (`data/`) and figure (`figures/`)
    scripts
  - `code/tests/` — Pytest test suite, run from `code/`
- `research/` — Planning notes, derivations, and literature knowledge base
  - `research/AGENTS.md` — Research-sector instructions; edited directly
  - `research/derivations/` — Worked mathematical derivations by topic
  - `research/references/scientific_papers/` — Ingested scientific papers by
    category; starts empty
  - `research/references/src/` — Knowledge-base tools: the tag-index generator,
    the find-papers gatherer, their packages, and tests; see its
    [README](../../research/references/src/README.md)
  - `research/references/indexes/tags/` — Parallel literature navigation;
    [maintained operator README](../../research/references/indexes/tags/README.md)
    and [generated accepted-vocabulary snapshot](../../research/references/indexes/tags/index.md);
    not a separate registry or folder classification
- `publications/` — Authored deliverables
  - `publications/AGENTS.md` — Publications-sector instructions; edited
    directly
  - `publications/modules/markings/` — Shared Mark API (`markings.tex`,
    `markings.dbx`) and `scripts/`, the marker finder the
    `approve-changes-markings` agent runs
  - `publications/paper---example/` — Compilable example manuscript; copy it
    to `publications/paper---<slug>/` to start a paper
- `docs/` — Durable project documentation and workflows
  - `docs/agent-guidance/` — Detailed guidance cited by root instructions
  - `docs/todo/` — Canonical TODO queue, one dated file per topic
    - `docs/todo/resolved/` — Terminal TODOs, kept as historical evidence
- `data/` — Results that are expensive or impossible to regenerate; committed
  to Git and never deleted or overwritten. Its `README.md` indexes the
  datasets; see `data-preservation.md`
- `artifacts/` — Regenerable code-sector outputs, ignored by Git except its
  `README.md`; `code/src/code_paths.py` creates `artifacts/data/`,
  `artifacts/figures/`, and `artifacts/videos/` on demand
- `_agents_outputs/` — One-off agent reports for humans; not maintained, so
  maintained files must not link into it. Treat it as deletable: anything that
  must survive belongs in `docs/`.
  - `_agents_outputs/_agents_dump/` — Temporary agent files; git-ignored

Sectors may add subfolders when the project needs them, for example
`research/notes/` or `publications/presentations/`; add each one to this map
in the same change that creates it.
