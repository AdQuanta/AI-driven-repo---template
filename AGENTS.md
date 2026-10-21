# Agent Instructions

## Project Vision
This repository has three connected sectors: `research/` for concepts,
derivations, and literature; `code/` for the project's code, simulations, and
experiments; and `publications/` for authored papers, figures, and
presentations. Work in the relevant sector while preserving consistency across
all three. For the directory map, see `docs/agent-guidance/project-layout.md`.
When a change adds, removes, moves, or renames a directory shown in this map,
update it in the same change.

## What Is This Project About?
Replace this paragraph with two or three sentences that state the project's
research question, its approach, and the outcome it aims for. Agents read this
statement on every turn, so keep it short and specific.

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

## Subagent Model Routing
Before invoking a subagent, read and follow
`docs/agent-guidance/subagent-model-routing.md`.

## VS Code And LaTeX Environment
Before compiling LaTeX or changing repository/user VS Code configuration for
LaTeX, read and follow `docs/agent-guidance/vscode-latex-environment.md`.

## Output Locations
- Put interim agent files in `_agents_outputs/_agents_dump/`; create it if
  missing and clean it up after use.
- Put final human-facing agent outputs in `_agents_outputs/`.
- `_agents_outputs/` is not maintained. Do not link to it from maintained
  files; promote content with lasting value to a maintained folder such as
  `docs/`, or leave temporary outputs unreferenced.
- Regenerable code-sector data and figures belong under `artifacts/`, which
  Git ignores; see the code-sector instructions.
- Results that are expensive or impossible to regenerate belong under
  `data/`, which Git tracks. Paid jobs, runs on external systems, and long
  simulations are examples. Never delete, overwrite, or regenerate them.
  Before writing, moving, or deleting generated data, read
  `docs/agent-guidance/data-preservation.md`.

## Answering Research Questions
For conceptual, theoretical, or literature questions, check relevant derivations
under `research/derivations/`, use the `find-papers` sub-agent for knowledge-base
literature, and synthesize both. If a needed paper is not in the knowledge base,
invoke `ingest-paper`. Save new derivations under `research/derivations/` using
the research-sector structure and citation rules.

## Git Safety
- Never use destructive Git commands that discard the user's working-tree
  state. Treat existing modifications as the user's unless the current task
  clearly created them.
- Never switch the branch of the user's active checkout.
- Agent-created worktrees may be managed by the agent for the task, but must not
  discard user-created changes or affect the user's active worktree.
- For details and optional worktree workflows, see
  `docs/agent-guidance/git-policy.md`.

## Skill Registry
When a user request matches a project skill, load and follow the relevant
`SKILL.md` before responding. The skill index lives in
`.agents/skills/docs/registry.md`. For skill authorship and registry
maintenance, use `.agents/skills/skill-maintenance/SKILL.md`.

## Custom Agents And Multi-Platform Discovery
Custom agents live only in `.claude/agents/`; never add a second agent folder
such as `.github/agents/`. Skills live only in `.agents/skills/`; never edit
or commit through the ignored `.claude/skills` link, which Claude Code users
create once per clone with `.claude/setup-discovery.ps1` (Windows) or
`.claude/setup-discovery.sh` (Linux/macOS).

Codex does not read `.claude/agents/`. When running under Codex and a task
matches an agent's `description`, run that agent as a subagent: read
`.claude/agents/<name>.agent.md`, call `spawn_agent` with a message that is the
complete file body copied verbatim (do not summarize or paraphrase it),
followed by the concrete task, and map its `tools` list to the equivalent Codex
capabilities. Platform matrix, rules, and checks:
`docs/agent-guidance/cross-platform-ai-support.md`.

## Knowledge Preservation
Record durable conventions, coding patterns, and hard-won lessons in the
project's canonical instructions or docs. Personal memory may hold a pointer or
summary, but the project record is authoritative.
