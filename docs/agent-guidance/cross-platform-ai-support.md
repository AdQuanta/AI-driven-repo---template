# Cross-Platform AI Support

This repository supports VS Code Copilot, Claude Code, and Codex from one owned
copy of every instruction, skill, and agent. There is no generation, sync, or
projection step: each asset has exactly one canonical location, and each
platform reaches it either natively or through one narrow adapter.

## What Each Platform Reads

| Asset | Canonical location | Copilot | Claude Code | Codex |
| --- | --- | --- | --- | --- |
| Root instructions | `AGENTS.md` | native | via `CLAUDE.md` (`@AGENTS.md`) | native |
| Skills | `.agents/skills/` | native | via the ignored `.claude/skills` link | native |
| Custom agents | `.claude/agents/*.agent.md` | native | native | via the `AGENTS.md` spawn instruction |

The repository ships no `.claude/settings.json`. Permission allowlists are a
per-user choice; keep them in user-level or `.claude/settings.local.json`
configuration, which Git ignores.

The root `AGENTS.md` "Sector Instruction Loading" rule tells every platform to
read the sector `AGENTS.md` files before editing in `code/`, `research/`, or
`publications/`.

## One-Time Setup

- **Claude Code:** after a fresh clone, run the setup script for your OS once
  from the repository root: `& .\.claude\setup-discovery.ps1` on Windows or
  `sh .claude/setup-discovery.sh` on Linux/macOS. Both create the ignored
  `.claude/skills` link to `.agents/skills/` (a junction on Windows, needing no
  elevation; a relative symbolic link elsewhere) and never copy content. Both:
  - check `.claude/agents/` and `.agents/skills/` before creating anything;
  - leave a correct link alone and report it;
  - refuse, and never delete, a link with another target or a real directory
    at that path, printing a recovery hint;
  - confirm the new link resolves, and print one line.

  The `.sh` refuses to run under Git Bash, MSYS, or Cygwin, where `ln -s`
  silently copies the folder. `.gitattributes` keeps `*.sh` files LF in every
  checkout, so the script runs unchanged on Linux and macOS.
- **Copilot and Codex:** no setup.

## Rules

1. **One agent folder.** Custom agents live only in `.claude/agents/`, a real
   tracked directory. Never add `.github/agents/` or a link between the two:
   Copilot scans both, lists each agent twice, and fails to resolve the
   duplicates (observed for `find-papers` and `ai-judge`).
2. **Never edit through the link.** Edit skills in `.agents/skills/`. Never
   edit or commit content through `.claude/skills`.
3. **Ignore the link without a trailing slash.** The rule is
   `/.claude/skills`. Git records a Linux/macOS symlink as a file, and a
   `/.claude/skills/` rule matches directories only, so the link would show up
   as untracked and could be committed.
4. **No generated copies.** Do not add `.codex/`, `.github/skills/`,
   `.github/instructions/`, a copied `.claude/skills/` tree, or generated
   sector `CLAUDE.md` files. Copies drift from their owner.
5. **Tool names for both harnesses.** Each agent's `tools` list carries both
   Copilot's lowercase aliases (`read`, `search`, …) and Claude Code's
   case-sensitive names (`Read`, `Grep`, `Glob`, `Bash`, `PowerShell`, `Edit`,
   `Write`, `Agent`, `TodoWrite`). With lowercase aliases alone, Claude Code
   resolves zero tools and refuses to launch the subagent.
6. **Agent test fixtures stay outside the agent folder.** Put them under
   `.agents/tests/` so no platform loads them as agents.

## How Codex Runs Project Agents

Codex custom agents are standalone TOML files under `.codex/agents/`, a
different schema, so Codex cannot read `.claude/agents/*.agent.md`. Instead of
generating a projection, the root `AGENTS.md` tells Codex to call `spawn_agent`
with the agent file body **copied verbatim**, followed by the task.

- **Keep that `AGENTS.md` sentence unchanged.** With looser wording ("spawn a
  subagent whose instructions are the body of that file"), Codex paraphrased a
  9.9 KB agent body into about 0.6 KB. The current wording forwarded the full
  body.
- **Under Codex, the `tools` list is guidance, not enforcement.** Codex ignores
  agent frontmatter and is only told to map the list to equivalent
  capabilities.
- **If you reword the sentence, retest it.** Ask Codex in natural language to
  run an agent, then check the spawn payload size in
  `~/.codex/sessions/*/rollout-*.jsonl`. Codex's `--json` stream does not show
  `spawn_agent` calls.

## Verification

Run from the repository root.

| Check | Expected |
| --- | --- |
| `Test-Path .github\agents; Test-Path .codex` | `False`, `False` |
| `(Get-Item .claude\agents -Force).LinkType` | empty (a real directory) |
| `(Get-Item .claude\skills -Force).Target` | the absolute path of `.agents\skills` |
| `git check-ignore -v .claude/skills` | prints the `.gitignore` rule |
| Linux/macOS: `test -L .claude/skills && ls .claude/skills/brainstorming/SKILL.md` | the path prints |
| `git status --porcelain .claude` after running a setup script | empty |
| `Select-String AGENTS.md -Pattern 'spawn_agent'` | exactly 1 hit |
| `npx --yes @anthropic-ai/claude-code plugin validate .claude/agents` | "Validation passed" |
| Copilot agent picker and `/` skill list (manual) | each project agent and skill appears once |

The platforms are not interchangeable. Check bare skill invocation, direct
agent loading, real parent-to-subagent dispatch, and tool permissions
separately on each platform you rely on. Record the outcome of those checks,
for example in a TODO under `docs/todo/`, so later changes can be compared
against it.
