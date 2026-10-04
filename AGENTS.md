# Agent Instructions

## Project Vision
This repository has three connected sectors: `research/` for concepts,
derivations, and literature; `code/` for Python simulations and experiments;
and `publications/` for authored papers, figures, and presentations. Work in
the relevant sector while preserving consistency across all three. For the
directory map, see `docs/agent-guidance/project-layout.md`. When a change adds,
removes, moves, or renames a directory shown in this map, update it in the same
change.

## What Is This Study About?
TODO: Replace this paragraph with a two- or three-sentence statement of the
research question, the system studied, and the key quantity or trade-off the
project investigates. Agents read it on every turn, so keep it short and precise.

## Sector Instruction Loading
Before editing sector files, read and follow the nearest applicable instructions:

- `code/**`: `code/AGENTS.md`
- `publications/**`: `publications/AGENTS.md`
- `research/**`: `research/AGENTS.md`

### Fallback Rule
If a sector instruction file is missing, explicitly warn the user.

## Project TODOs
Project TODOs live in `docs/todo/`. Before reading, creating, or updating a
TODO, read `docs/todo/README.md`.

## VS Code And LaTeX Environment
Before compiling LaTeX or changing repository/user VS Code configuration for
LaTeX, read and follow `docs/agent-guidance/vscode-latex-environment.md`.


## Output Locations
- Put interim agent files in `_agents_outputs/_agents_dump/`; create it if
  missing and clean it up after use.
- Put final human-facing agent outputs in `_agents_outputs/`.
- Code-sector generated data and figures belong under `artifacts/`; see the
  code-sector instructions.

## Answering Research Questions
For conceptual, theoretical, or literature questions, check relevant derivations
under `research/derivations/`, use the `find-papers` sub-agent for knowledge-base
literature, and synthesize both. If a needed paper is not in the knowledge base,
invoke `ingest-paper`. Save new derivations under `research/derivations/` using
the research-sector structure and citation rules.

## Git Operation Ownership
- Do not stage, commit, or push unless the user explicitly asks.
- Never use destructive Git commands that discard the user's active working-tree
  state.
- Agent-created worktrees may be managed by the agent for the task, but must not
  discard user-created changes or affect the user's active worktree.
- For optional worktree workflows, see `docs/agent-guidance/git-policy.md`.

## Skill Registry
When a user request matches a project skill, load and follow the relevant
`SKILL.md` before responding. The skill index lives in
`.agents/skills/docs/registry.md`. For skill authorship and registry
maintenance, use `.agents/skills/skill-maintenance/SKILL.md`.

## Claude Code Discovery
The canonical skill and agent sources remain `.agents/skills/` and
`.github/agents/`. After a fresh clone, run `.claude/setup-discovery.ps1` once
to create Claude Code's ignored `.claude/skills` runtime link. Do not edit or
commit content through `.claude/skills/`, and never link `.claude/agents` to
`.github/agents`: VS Code Copilot scans both and breaks on the duplicates.
Claude Code discovery of the `.github/agents/` definitions is not configured;
verify direct agent loading and subagent dispatch separately before relying on
it in Claude Code.

## Knowledge Preservation
Record durable conventions, coding patterns, and hard-won lessons in the
project's canonical instructions or docs. Personal memory may hold a pointer or
summary, but the project record is authoritative.
