---
description: "Use when working with planning notes, TODO resolution, and research concept docs in research/."
name: "Research Sector Guidance"
applyTo: "research/**"
---
# Research Sector Guidance

This instruction is the canonical guidance for the research sector.

## Folder Layout

```
research/
├── derivations/       # One subfolder per derivation topic (e.g., swap-fidelity-bounds/)
└── references/        # All ingested literature and background reading
    └── scientific_papers/  # Ingested papers; hierarchical topic categories
                            # (e.g., field_name/sub_category/citation_key/)
```

## Citation Organization

Each paper lives in its own dedicated subfolder named by citation key (e.g., `smith2024routing/`), inside the appropriate topic sub-category under `research/references/scientific_papers/`. Every paper folder must contain:
- A PDF of the paper, named using the **original published title** of the paper (e.g., `Probabilistic Quantum Teleportation.pdf`).
- A `summary.md` with YAML frontmatter, verbatim abstract, key takeaways, project relevance, and a BibTeX entry.

### Category Hierarchy

Papers are organized in a **two-level hierarchy**: `<top-level-field>/<sub-category>/<citation-key>/`.

<!-- [TODO: Replace the example hierarchy below with the categories that fit your research domain.
     Follow the scalability rules: keep flat until >12 papers in a category, then subdivide.
     Each sub-category must have at least 2 papers before it is created.] -->

**Example hierarchy** (replace with your own):

- **`your_field/`** — Papers on your main research area.
  - `sub_topic_a/` — Papers on aspect A of your field.
  - `sub_topic_b/` — Papers on aspect B of your field.
- **`foundational_theory/`** — Core theoretical background papers.
- **`experimental_platforms/`** — Hardware/platform-specific papers.

### Scalability Rules for Sub-categorization

These rules apply to **all** top-level fields, present and future:

1. **Threshold rule**: When a top-level category exceeds **~12 papers**, subdivide it into sub-categories by primary methodological or thematic focus.
2. **Minimum size**: Each sub-category must contain **at least 2 papers**. A single-paper sub-category should be merged into the closest related sub-category.
3. **Classify by primary contribution**: Place each paper in the sub-category matching its *main* contribution, not tangential mentions.
4. **Flat until necessary**: Categories with ≤12 papers remain flat (citation-key folders directly inside the top-level field). Do not pre-create empty sub-categories.
5. **Naming convention**: Sub-category folder names use `snake_case`, are descriptive, and avoid abbreviations (e.g., `routing_algorithms/` not `ra/`).
6. **Depth limit**: Maximum nesting is two levels (`field/sub-category/citation-key/`). If a sub-category itself grows beyond ~15 papers, split the *top-level field* into sibling fields rather than adding a third nesting level.

- Use [research/TODO.md](../../research/TODO.md) as the canonical checklist when TODO work is requested.
- For TODO-resolution execution workflow, follow [research/PRD_todo_resolution.md](../../research/PRD_todo_resolution.md) and strongly prefer using the `/todo-resolver` command to execute these tasks cleanly.
- Never mark TODO items as done unless the user explicitly asks to update checklist state.
- After completing related work, recommend which TODO items appear resolved and should be marked done by the user.
- Keep planning notes concise, actionable, and aligned with project vision.
- In human-facing Markdown notes under research/, write math with proper LaTeX delimiters: use inline `$...$` and display `$$...$$` blocks. Avoid plain-text pseudo-math forms like `x = y/sqrt(z)` without math delimiters.

## Derivation Files — Structure and Citation Practice

### Creating a New Derivation
When a mathematical result or analytical derivation is worked out that does not already exist in `research/derivations/`:
- Create a **dedicated subfolder** named after the topic using `kebab-case` (e.g., `research/derivations/swap-fidelity-bounds/`).
- Save the derivation as a Markdown file with a **meaningful, descriptive filename** (e.g., `fidelity-bound-under-werner-noise.md`).
- One subfolder per topic; multiple derivation files may live in the same subfolder if they share a topic.

### Citing Papers in Derivations
When writing or extending a derivation file under `research/derivations/`, cite relevant papers from the knowledge base using **relative Markdown links** to the paper's `summary.md` file. Do **not** use bare citation keys, DOIs, or plain-text references — always link so the citation is navigable.

**Link format** (relative path from the derivation file):

```markdown
[\[<short-cite>\]](../../references/scientific_papers/<field>/<sub-category>/<citation-key>/summary.md)
```

The inner `[...]` are literal characters in the rendered text, giving the familiar bracket-citation style. Use the exact `short_cite` value from the paper's `summary.md` YAML frontmatter as the link text.

**Example** — citing Smith et al. 2024 from a derivation two levels deep:

```markdown
The theoretical bound follows from the analysis of
[\[Smith et al., Nature 2024\]](../../references/scientific_papers/your_field/sub_topic_a/smith2024routing/summary.md).
```

**Rules:**
1. **Always link to `summary.md`**, not to the PDF, so the reader gets the structured summary and BibTeX entry.
2. **Use the `short_cite` field** from the paper's YAML frontmatter verbatim as the link text, wrapped in escaped brackets: `[\[<short-cite>\]](path)`.
3. **Invoke `find-papers`** before writing a derivation section to discover which knowledge-base papers are relevant — do not cite from memory alone.
4. **If a relevant paper is not yet in the knowledge base**, invoke `ingest-paper` to add it first, then link to its newly created `summary.md`.
