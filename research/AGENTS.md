# Research Sector Guidance

This instruction is the canonical guidance for the research sector.

## Folder Layout

```
research/
├── derivations/       # One subfolder per derivation topic (e.g., <topic-name>/)
└── references/        # All ingested literature and background reading
    └── scientific_papers/  # Ingested papers; topic categories grow with the base
                            # (e.g., <field>/<sub-category>/<citation-key>/)
```

Add `notes/` (modeling notes, framing decisions, open questions) and
`progress/` (dated experiment/progress write-ups) when the project first needs
them, and record them in `docs/agent-guidance/project-layout.md` in the same
change.

## Citation Organization

Each paper lives in its own dedicated subfolder named by citation key (e.g., `smith2024example/`), inside the appropriate topic category under `research/references/scientific_papers/`. Every paper folder must contain:
- A PDF of the paper, named using the **original published title** of the paper (e.g., `An Example Paper Title.pdf`).
- A `summary.md` with YAML frontmatter, verbatim abstract, key takeaways, project relevance, and a BibTeX entry.

### Category Hierarchy

Papers are organized in at most a **two-level hierarchy**: `<top-level-field>/<sub-category>/<citation-key>/`.

The taxonomy **starts empty**. Create no category folders until the first paper
is ingested, and let real ingests define the fields. Record the current
top-level fields here as they appear, one bullet each with a one-line scope, so
`ingest-paper` files new papers consistently:

- *(no categories yet)*

### Scalability Rules for Sub-categorization

These rules apply to **all** top-level fields, present and future:

1. **Threshold rule**: When a top-level category exceeds **~12 papers**, subdivide it into sub-categories by primary methodological or thematic focus.
2. **Minimum size**: Each sub-category must contain **at least 2 papers**. A single-paper sub-category should be merged into the closest related sub-category.
3. **Classify by primary contribution**: Place each paper in the sub-category matching its *main* contribution, not tangential mentions.
4. **Flat until necessary**: Categories with ≤12 papers remain flat (citation-key folders directly inside the top-level field). Do not pre-create empty sub-categories.
5. **Naming convention**: Sub-category folder names use `snake_case`, are descriptive, and avoid abbreviations (e.g., `routing_algorithms/` not `ra/`).
6. **Depth limit**: Maximum nesting is two levels (`field/sub-category/citation-key/`). If a sub-category itself grows beyond ~15 papers, split the *top-level field* into sibling fields rather than adding a third nesting level.
7. **Reorganize when needed**: Subdividing a field means moving already-ingested papers into the new sub-categories and repairing every relative link that pointed at them.

- Keep planning notes concise, actionable, and aligned with project vision.
- In human-facing Markdown notes under research/, write math with proper LaTeX delimiters: use inline `$...$` and display `$$...$$` blocks. Avoid plain-text pseudo-math forms like `x = y/sqrt(z)` without math delimiters.

## Citing Papers in Research Markdown

This rule applies to **every** human-facing Markdown file under `research/` — derivations, notes, progress write-ups, and planning documents alike. It does **not** apply to LaTeX sources under `publications/`, which use BibTeX keys via `\cite{}`.

Cite papers from the knowledge base using **relative Markdown links** to the paper's `summary.md` file. Do **not** use bare citation keys, DOIs, plain-text references, or bare external publisher/arXiv URLs — always link so the citation is navigable inside the repository.

**Link format** (relative path from the citing file):

```markdown
[\[<short-cite>\]](<relative-path>/references/scientific_papers/<field>/<sub-category>/<citation-key>/summary.md)
```

The inner `[...]` are literal characters in the rendered text, giving the familiar bracket-citation style. Use the exact `short_cite` value from the paper's `summary.md` YAML frontmatter as the link text.

**Example** — citing a paper from a file two levels deep (e.g. `research/derivations/<topic>/<file>.md`):

```markdown
The bound follows from the analysis of [\[Smith et al., J. Example Res. 2024\]](../../references/scientific_papers/<field>/smith2024example/summary.md).
```

From a file one level deep (e.g. `research/notes/<file>.md`), the prefix is `../` instead of `../../`.

**Rules:**
1. **Always link to `summary.md`**, not to the PDF, so the reader gets the structured summary and BibTeX entry.
2. **Use the `short_cite` field** from the paper's YAML frontmatter verbatim as the link text, wrapped in escaped brackets: `[\[<short-cite>\]](<path>)`.
3. **Invoke `find-papers`** before writing a section that makes citable claims — do not cite from memory alone.
4. **If a relevant paper is not yet in the knowledge base**, invoke `ingest-paper` to add it first, then link to its newly created `summary.md`.
5. **An external URL is never a substitute for a knowledge-base link.** If a source is worth citing, ingest it. A raw publisher/arXiv link may accompany a knowledge-base link only for material that will never be ingested (software documentation, standards, datasets).

## Derivation Files — Structure

### Creating a New Derivation
When a mathematical result or analytical derivation is worked out that does not already exist in `research/derivations/`:
- Create a **dedicated subfolder** named after the topic using `kebab-case` (e.g., `research/derivations/error-bound-analysis/`).
- Save the derivation as a Markdown file with a **meaningful, descriptive filename** (e.g., `bound-under-gaussian-noise.md`).
- One subfolder per topic; multiple derivation files may live in the same subfolder if they share a topic.
- Cite supporting literature per **Citing Papers in Research Markdown** above.
