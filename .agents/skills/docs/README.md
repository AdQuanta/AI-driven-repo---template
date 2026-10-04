# Skills Authorship Convention

`.agents/skills/` is the directly maintained skill location for this
repository. Every skill lives here as its own owned source of truth; there is
no separate generated or vendored copy to keep in sync. Edit the owning skill
in place.

Every skill in this folder must declare authorship in its YAML frontmatter so future contributors can trace where a skill came from and who maintains it.

## Fields

| Field | Required | Description |
|-------|----------|--------------|
| `author` | ✅ Always | Who wrote or sourced the skill |
| `source` | When sourced externally | Direct URL to the skill's origin |

## Authorship Rules

### Skills sourced from an external repository (e.g. via [skills.sh](https://www.skills.sh))

Set both fields:

```yaml
author: skills.sh
source: "https://www.skills.sh/{github-user}/{github-repo}/{skill-name}"
```

Provenance is tracked entirely through this frontmatter — there is no separate
lock file. When an imported skill is updated from upstream, edit it in place
under `.agents/skills/` and keep the `source:` URL accurate.

### Skills written for this project

Skills **not** sourced externally are local, custom skills. Set only the
GitHub handle of the person who wrote them:

```yaml
author: <github-handle>
```

Skills inherited from the template keep their original `author` value
(for example `author: NGBigField`) as provenance.

## Example Frontmatter

**Custom skill:**
```yaml
---
name: my-skill
description: Does something useful for this project.
author: <github-handle>
---
```

**Imported from an external source:**
```yaml
---
name: networkx
description: Comprehensive toolkit for network graphs.
author: skills.sh
source: "https://www.skills.sh/davila7/claude-code-templates/networkx"
---
```

## Skill Maintenance Skill

Before adding, editing, renaming, removing, or reviewing project skills, follow
[`skill-maintenance`](../skill-maintenance/SKILL.md). It is the repo-specific
entry point for authorship metadata, registry updates, and skill-ownership
rules.

## Checklist When Adding a New Skill

1. **Sourced from an external repository?**
   → Add `author: <source-name>` + `source:` with the origin URL.

2. **Written by hand or copied/adapted locally?**
   → Add `author: <github-handle>`. No `source` field needed.

3. Update [`registry.md`](registry.md) so the human-readable skill index stays current.
   Edit the owning skill in place under `.agents/skills/`; do not create
   platform-specific copies elsewhere in the repository.
