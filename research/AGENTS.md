# Research Sector Guidance

This instruction is the canonical guidance for the research sector.

## Folder Layout

```
research/
├── derivations/       # One subfolder per derivation topic (e.g., <topic-name>/)
└── references/        # All ingested literature and background reading
    ├── indexes/tags/  # Parallel tag navigation; maintained README, generated index.md
    │   └── by_tag/    # Generated per-tag pages, one <tag>.md per accepted tag
    ├── scientific_papers/  # Ingested papers; topic categories grow with the base
    │                       # (e.g., <field>/<sub-category>/<citation-key>/)
    └── src/           # Knowledge-base tooling: tag-index generator, find-papers gatherer
```

Add `notes/` (modeling notes, framing decisions, open questions) and
`progress/` (dated experiment/progress write-ups) when the project first needs
them, and record them in `docs/agent-guidance/project-layout.md` in the same
change.

## Literature Tags and Parallel Navigation

Paper summary inline `tags` arrays are authoritative assignments. Use canonical
ASCII lowercase `snake_case` (`^[a-z0-9]+(?:_[a-z0-9]+)*$`), with no duplicates
within a summary. Before assigning tags, read the accepted
[tag index](references/indexes/tags/index.md) and reuse accurate existing tags.
Explain genuinely new concepts; review every unseen tag and similar-tag
suggestion before explicit acceptance with `--accept-new-tags`. The generated
index is the accepted-vocabulary snapshot, not a separately maintained registry.

After creating or repairing a summary, run normal generation from the repository
root with the project Python environment:
`python research/references/src/generate_literature_tag_index.py`, then
`python research/references/src/generate_literature_tag_index.py --check`.
If normal generation reports unseen tags, correct accidental variants or accept
only justified new concepts using `--accept-new-tags`, then rerun `--check`.
See the maintained [operator README](references/indexes/tags/README.md) for
bootstrap, validation, and safety rules. Never hand-edit generated pages.

Tags provide overlapping, parallel navigation only. They never replace the
primary-contribution folder classification or require moving/duplicating papers.
Required `citation_key` and `short_cite` values must be nonempty, printable,
control-free single-line strings; quoted escapes cannot introduce C0/C1 controls
or Unicode line/paragraph separators.

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

For illustration only (these folders do not exist), a grown taxonomy could
look like this:

- **`statistical_methods/`** — Estimation, inference, and uncertainty quantification.
  - `sampling_methods/` — Monte Carlo, importance sampling, and bootstrap techniques.
  - `bayesian_inference/` — Priors, posterior computation, and model comparison.
- **`optimization/`** — Problem formulations and solvers (still flat, ≤12 papers).

### Scalability Rules for Sub-categorization

These rules apply to **all** top-level fields, present and future:

1. **Threshold rule**: When a top-level category exceeds **~12 papers**, subdivide it into sub-categories by primary methodological or thematic focus.
2. **Minimum size**: Each sub-category must contain **at least 2 papers**. A single-paper sub-category should be merged into the closest related sub-category.
3. **Classify by primary contribution**: Place each paper in the sub-category matching its *main* contribution, not tangential mentions.
4. **Flat until necessary**: Categories with ≤12 papers remain flat (citation-key folders directly inside the top-level field). Do not pre-create empty sub-categories.
5. **Naming convention**: Sub-category folder names use `snake_case`, are descriptive, and avoid abbreviations (e.g., `sampling_methods/` not `sm/`).
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

## Reproducible Numbers

Every number quoted in research Markdown must be traceable. It is either
taken from a cited paper, or produced by code committed in this repository:
tested logic under `code/src/`, run by a script under `code/scripts/`.

- Name the script next to the numbers it produced, or once in the note.
- Do not quote the result of an ad-hoc command, a notebook cell, or an
  interactive session. Commit the code first, then quote its output.
- Numbers that rest on hardware or other costly runs must point to data
  kept under `data/`; see
  `docs/agent-guidance/data-preservation.md`.

Research computation stays in `code/`; knowledge-base tooling is not research
computation. The tag-index generator and the find-papers gatherer live in
[`references/src/`](references/src/README.md) with their own tests, and
nothing there imports from `code/`.
