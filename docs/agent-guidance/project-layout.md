# Project Layout Reference

This is the shared reference for repository structure. Keep root instructions
short and point here when agents need the full map.

## Maintenance

Agents must update this map whenever a repository hierarchy change affects a
directory shown here, in the same change. Drop entries for directories that no
longer exist; add entries only for directories that actually exist.

## Repository Structure

This repository directly owns and maintains all AI-agent infrastructure.
`AGENTS.md`, `.agents/skills/`, `.github/agents/`, and `.github/prompts/` are
edited directly, as are the sector `AGENTS.md` files below. There is no
generation, sync, or projection step.

- `AGENTS.md` — Root agent instructions; edited directly
- `CLAUDE.md` — `@AGENTS.md` import for Claude Code; edited directly
- `requirements.txt` — Root dependency manifest for shared skills and agents
- `.agents/skills/` — Project skills; edited directly
  - `.agents/skills/docs/` — Skill authorship convention and skill registry
- `.claude/` — Claude Code adapter; `setup-discovery.ps1` creates the ignored
  `.claude/skills` link to `.agents/skills/`
- `.github/agents/` — Copilot custom agents; edited directly
  - `.github/agents/tests/citation-audit/` — Fixture for the citation agents
- `.github/prompts/` — Copilot prompt files and their helper scripts
- `.github/workflows/` — CI workflows (`tests.yml` runs the code-sector pytest
  gate)
- `.vscode/settings.json` — Workspace settings: nested `AGENTS.md` loading,
  LaTeX Workshop recipe, terminal auto-approval rules
- `code/` — Python simulations, algorithms, and experiments
  - `code/AGENTS.md` — Code-sector instructions; edited directly
  - `code/requirements.txt` — Code-sector dependency manifest
  - `code/src/` — Importable library modules (`code_paths.py`, `find_papers/`)
  - `code/scripts/` — Data-generation, figure, and tooling scripts
  - `code/tests/` — Pytest test suite
- `research/` — Derivations and literature knowledge base
  - `research/AGENTS.md` — Research-sector instructions; edited directly
  - `research/derivations/` — Worked mathematical derivations by topic
  - `research/references/scientific_papers/` — Ingested scientific papers by
    category (starts empty)
- `publications/` — Authored deliverables
  - `publications/AGENTS.md` — Publications-sector instructions; edited
    directly
  - `publications/modules/markings/` — Shared Mark API LaTeX module
  - `publications/paper---example/` — Starter LaTeX manuscript; copy it to
    `publications/paper---<slug>/` for each new paper
- `docs/` — Durable project documentation and workflows
  - `docs/agent-guidance/` — Detailed guidance cited by root instructions
  - `docs/todo/` — Canonical TODO queue, one dated file per topic
    - `docs/todo/resolved/` — Archived resolved TODO files
- `artifacts/` — Generated code-sector outputs; git-ignored and created on
  first use (`data/`, `figures/`)
- `_agents_outputs/` — Final agent-produced outputs for humans
  - `_agents_outputs/_agents_dump/` — Temporary agent files; git-ignored and
    created on first use
