# Shared AI Instructions: Claude Code + GitHub Copilot

## How it works

All agent instructions live in one place:

```
.github/copilot-instructions.md   ← single source of truth
CLAUDE.md                         ← one line: @.github/copilot-instructions.md
```

- **GitHub Copilot** reads `.github/copilot-instructions.md` natively.
- **Claude Code** reads `CLAUDE.md`, which imports the same file via the `@path` syntax.

To add or change instructions, edit only `.github/copilot-instructions.md`. `CLAUDE.md` never needs to change.

---

## Skills

Copilot and Claude handle skill discovery differently, which drives every structural decision here.

| | GitHub Copilot | Claude Code |
|---|---|---|
| **Discovery** | Auto-scans `.github/skills/` (platform convention) | None — must be listed explicitly |
| **Trigger** | Context-based, automatic | Only when a Skill Registry entry matches |

**Copilot** discovers skills by scanning `.github/skills/` — a GitHub platform convention, the same way `copilot-instructions.md` only works inside `.github/`. Skills placed anywhere else are invisible to Copilot; do not rename or move that folder.

**Claude Code** has no equivalent. It only knows about a skill if the skill appears in a file Claude has already read.

### The Skill Registry

The fix is a **Skill Registry** table inside `copilot-instructions.md`. This is not optional — it is the only mechanism that makes Claude skill-aware. Because `CLAUDE.md` `@`-imports `copilot-instructions.md` (see above), any table written there is automatically visible to Claude on every session. Copilot ignores the table and continues auto-discovering skills normally.

```markdown
## Skill Registry

When a user message matches a trigger, load and follow the linked SKILL.md before responding.

| Skill | SKILL.md | Triggers |
|---|---|---|
| Name | `.github/skills/name/SKILL.md` | trigger word, another trigger |
```

---

## Adding instructions or skills

### New global instruction
Edit `copilot-instructions.md`. Both tools see the change immediately.

### New scope-limited instruction
Applies only to a specific folder or file type.

1. Create `.github/instructions/<scope>.instructions.md` with this front-matter so Copilot knows when to load it:
   ```yaml
   ---
   applyTo: "path/to/scope/**"
   ---
   ```
   Copilot loads the file automatically whenever the active file matches the glob.

2. Create a `CLAUDE.md` inside the target subfolder with a single `@`-import pointing at the instructions file:
   ```
   @../../.github/instructions/<scope>.instructions.md
   ```
   Claude Code loads subfolder `CLAUDE.md` files automatically when working in that scope, so no changes to the global `copilot-instructions.md` are needed.

### New skill
Create `.github/skills/<name>/SKILL.md`. Copilot picks it up automatically; add a row to the Skill Registry in `copilot-instructions.md` for Claude.
