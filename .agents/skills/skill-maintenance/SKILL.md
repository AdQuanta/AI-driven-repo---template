---
name: skill-maintenance
description: Use when adding, editing, renaming, removing, or reviewing project skills under .agents/skills, including authorship metadata or skill registry updates.
author: NGBigField
---

# Skill Maintenance

Use this for repo-specific skill upkeep.

## Required Checks

1. Read `.agents/skills/docs/README.md` before changing skills.
2. Keep `.agents/skills/docs/registry.md` updated when a skill is added,
   removed, renamed, or its trigger description materially changes.
3. Preserve authorship metadata in every `SKILL.md` frontmatter:
   - Skills sourced from an external repository: `author: <source-name>` and a
     matching `source:` URL pointing to the origin.
   - Local project skills: `author: <github-handle>` of the writer and no
     `source` field unless there is a real upstream source. Inherited skills
     keep their original `author`.
4. Edit skills only under `.agents/skills/`; do not create platform-specific
   copies under `.github/skills/`, `.claude/skills/`, or `.codex/`.
5. When a skill's bundled scripts import a third-party package, declare it in
   the root `requirements.txt` in the same change, commented with the script it
   backs.

## Completion Checklist

- `SKILL.md` frontmatter has `name`, `description`, and `author`.
- The description says when to use the skill, not the workflow it performs.
- `.agents/skills/docs/registry.md` reflects the final skill set.
- Imported skills still carry consistent authorship/source metadata in their
  frontmatter.
