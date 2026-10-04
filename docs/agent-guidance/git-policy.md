# Git Policy Reference

This document holds the detailed Git workflow policy. Root instructions keep
only the safety contract.

## Ownership Boundary

- The user owns staging, committing, and pushing unless they explicitly ask an
  agent to do one of those operations.
- The user's active working tree may contain irreplaceable uncommitted work.
  Treat any existing modification as user-owned unless there is clear evidence
  it was created by the current agent task.
- Do not switch the user's active worktree to another branch.

## Destructive Commands

Never use Git commands that discard or rewrite working-tree state in the user's
active worktree, including:

- `git checkout -- <path>`
- `git restore`
- `git reset --hard`
- `git clean`
- `git stash`

If an agent needs to undo its own edit, use the editing tool to make a targeted
manual reversal. Do not use a blanket Git restore/reset operation.

## Agent-Created Worktrees

Git worktrees are allowed when they protect the user's active worktree. An agent
may create a separate worktree for a feature branch and work exclusively inside
that directory.

Within an agent-created worktree, the agent may manage the task branch as needed
when the user has asked for that workflow. This can include branching,
committing, pushing, and merging the completed feature branch back into the
user's current branch.

The same data-loss rule still applies: do not discard user-created changes, even
inside a worktree. If the worktree has changes whose ownership is unclear, stop
and ask before destructive cleanup.