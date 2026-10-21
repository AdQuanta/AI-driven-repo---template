# Publications Sector Guidance

> **STOP — READ THIS BEFORE MAKING ANY EDIT**
>
> Every addition or change to a `.tex` or `.bib` file MUST be wrapped with the Mark API:
> - Replacement of existing prose: `\MarkEdit{edits}[text]{old}{new}`
> - Replacement of inline math: `\MarkEdit{edits}[math]{old}{new}`
> - New inline text: `\Mark{changes}{...}`
> - Block text / whole paragraph: `\begin{MarkEnv}{changes}[text] ... \end{MarkEnv}`
> - Equations: `\begin{MarkEnv}{changes}[math] ... \end{MarkEnv}`
> - Figures: `\begin{MarkEnv}{changes}[figure] ... \end{MarkEnv}`
> - Headings: `\Mark{changes}[heading]{...}` inside the heading argument
> - New `.bib` entries: add `markroles = {changes},` as a field
>
> **No plain edits are acceptable. Unmarked changes are incomplete changes.**
> If the user explicitly approves an unmarked edit, make it plain and say so
> in the reply.
>
> After any `.tex`/`.bib` change, run the
> [full build](../docs/agent-guidance/vscode-latex-environment.md#agent-build-recipe)
> before reporting the task done (Gate 1).

## Manuscript Directories

Authored sources and generated artifacts stay apart. Each manuscript lives in
its own `publications/paper---<slug>/` directory with `main.tex`, `config.tex`,
`references.bib`, `sections/`, and `figures/`; build intermediates go to the
ignored `.latex_build/` folder described in the
[LaTeX environment guide](../docs/agent-guidance/vscode-latex-environment.md),
and regenerable figures and data come from `artifacts/`, never from the paper
folder. The shared Mark API lives in
[`modules/markings/`](modules/markings/README.md) and is loaded by relative path
from each paper's `config.tex`. The starter manuscript is
[`paper---example/`](paper---example/); copy it to start a new paper, and use
its sections as a working reference for every marker form below.
Optionally, group venue-specific copies as
`publications/submissions/<VENUE>/paper---<slug>/`.

## Core Best Practices

- Preserve scientific clarity, internal consistency, and LaTeX build stability.
- Mandatory: always compile the paper after making changes and check for errors.
- If there are compilation errors, the task is not complete.
- Keep notation, symbols, and terminology consistent across sections.
- Make minimal, targeted edits and avoid broad rewrites unless explicitly requested.
- Prefer concise, formal academic wording over conversational phrasing.
- For LaTeX manuscript editing, auditing, or compilation, load and follow
  `.agents/skills/latex-paper-en/SKILL.md`.
- For repository-specific build commands and VS Code configuration, read and
  follow `docs/agent-guidance/vscode-latex-environment.md`; it overrides generic
  compilation defaults in the skill.
- Standalone files also need all required packages declared explicitly in their own preamble — they cannot rely on `config.tex` or any shared include that `main.tex` loads.

## Show Replacements Like a Diff

Prefer `\MarkEdit` when revised text has an identifiable earlier version. Copy
the actual earlier source into `old`; keep the accepted wording in `new`.
Nested markers are forbidden: never put one Mark API wrapper inside another.
When revising content that is already marked, collapse the revision history
to one marker whose `old` argument is
the oldest version and whose `new` argument is the newest accepted version;
intermediate drafts need not be preserved. For display equations, do not nest
an inline `[math]` marker inside an existing math environment: mark the whole
equation with one `MarkEnv` instead.
Mark the smallest meaningful changed phrase and leave shared words outside the
command. If only a few words in a paragraph or caption changed, split the edit
at unchanged wording instead of wrapping the whole paragraph or caption. Use
`\Mark{changes}{...}` for text that was added without replacing earlier words.
Keep each old/new pair aligned so the popup describes the highlighted change.
Define the `edits` role with a green color in the paper preamble. The module's
default edit mode is `plain`, so select `\SetMarkEditMode{popup}` or
`\SetMarkEditMode{inline}` explicitly for a review PDF. In `inline` mode the old
text is red and struck through, and the new text is green highlighted. In
`popup` mode the new text has a green PDF highlight whose popup holds the old
text. In floats, including captions, a red note icon sits beside the green
highlighted new text because PDF text markup anchors are unreliable there.
The viewer controls the popup text color and interaction.
For a submission PDF, set the `edits` role to `[plain]` so only the new text
appears even if the review mode is `popup`.

Use `\Mark{changes}{...}` or `MarkEnv` for pure additions and supported block
content without an earlier counterpart; define `changes` as green for new work.
Do not invent old wording or attach an unrelated version to an edit note.
`\MarkEdit` supports prose with simple inline math and `\cite`, plus bare inline
math with `[math]`; compile and inspect the result. In a caption, provide a
plain optional short caption for the list of figures or tables. For headings, use the
existing `[heading]` form of `\Mark` until edit annotations are heading-safe.
Inspect the PDF note text too: PDF string conversion can omit math macros.
Add `\pdfstringdefDisableCommands` mappings in the paper preamble for symbols
used in old text, then rebuild and confirm the note reads correctly.

## Formatting New and Missing Content

To maintain clean highlights across text, equations, and figures, use the Mark API instead of plain text colors.

- Standard additions and replacements:
- Replaced text (inline): use `\MarkEdit{edits}{old}{new}`.
- Replaced inline math: use `\MarkEdit{edits}[math]{old}{new}`.
- New text (inline): use `\Mark{changes}{...}`.
- Section/subsection headings: use `\Mark{changes}[heading]{...}` directly inside the heading argument.
- Text (block): use `\begin{MarkEnv}{changes}[text] ... \end{MarkEnv}`.
- Equations: use `\begin{MarkEnv}{changes}[math] ... \end{MarkEnv}`.
- Figures: wrap graphics with `\begin{MarkEnv}{changes}[figure] ... \end{MarkEnv}`.
- **IMPORTANT**: `MarkEnv[figure]` wraps the content in a `tcolorbox`, which is NOT a float.
  Therefore, `\begin{figure}...\end{figure}` float environments CANNOT be placed inside `MarkEnv[figure]`.
  The correct pattern for a new figure float is: use a plain `\begin{figure}...\end{figure}` environment
  and mark only the caption text with `\Mark{changes}{...}`.
- **IMPORTANT**: `MarkEnv[text]` wraps content with `\hl{...}` (soul package), which cannot contain
  LaTeX environments like `equation`, `align`, `figure`, `tabular`, etc.
  Do NOT wrap large blocks containing environments in `MarkEnv[text]`.
  Instead, mark headings with `\Mark{changes}[heading]{...}` and leave body text without a block wrapper.
- **IMPORTANT**: `MarkEnv[math]` is only for bare equation content (no `\begin{equation}` inside).
  It wraps the content in a `tcolorbox` with `\begin{equation}...\end{equation}` added automatically.
- Missing or incomplete content:
- Text (inline): use `\Mark{missing}{...}`.
- Section/subsection headings: use `\Mark{missing}[heading]{...}` directly inside the heading argument.
- Text (block): use `\begin{MarkEnv}{missing}[text] ... \end{MarkEnv}`.
- Equations/Figures: use `MarkEnv` with role `missing` and kind `math` or `figure`.

### Heading Highlight Usage

- For heading arguments (`\section`, `\subsection`, `\subsubsection`), use the `heading` kind.


### Highlight Macro Usage (Text Blocks)

- Do not wrap every sentence fragment with separate `\Mark{changes}{...}` calls
    when the whole paragraph/caption segment is one continuous change.
- Prefer one `\Mark{changes}{...}` block for contiguous text, and split lines
    inside the same block using `%` line-continuation markers for readability.
- Only split into multiple highlight wrappers when the semantics differ
    (for example, mixing changed vs missing content, or separating distinct
    edit regions).
- Keep braces balanced so the full intended text remains inside the
    highlighting macro.

### Soul/`\hl` Hazards Inside `\Mark{...}` (avoid build breakage)

`\Mark{changes}{...}` (and `MarkEnv[text]`) wrap content in soul's `\hl`, which
re-scans every token and breaks on constructs it cannot reconstruct. Symptoms
are `TeX capacity exceeded ... input stack size` (often fatal, no PDF) or
`Package soul Error: Reconstruction failed` (non-fatal but the highlight renders
wrong — still counts as a build error under Gate 1). To stay safe:

- **Never put `\cref`/`\Cref`/`\ref`/`\cite` inside a `\Mark{...}`.** They expand
    to hyperref boxes that soul cannot scan. Keep the cross-reference *outside*
    the mark, e.g. `\Cref{fig:x} \Mark{changes}{shows ...}`.
- **Avoid the `\ ` control-space inside a mark** (e.g. `vs.\ `). Reword to a
    plain word (`versus`) — the escaped space triggers `Reconstruction failed`.
- **Wrap dense or relation-heavy inline math in `\mbox{...}`** (e.g.
    `\mbox{$N\in\{8,12,16\}$}`, `\mbox{$95\%$}`, `\mbox{$\lambda^\ast\approx0.3$}`).
    Long runs of adjacent `$...$` segments and `\%` inside math are the usual
    culprits.
- If a marked paragraph is long, **split it into several shorter
    `\Mark{changes}{...}` calls** to keep each `\hl` argument small.

## Marking New Citations

When adding new entries to `references.bib`, tag them so they are highlighted
in the bibliography alongside other marked changes.

- Add `markroles = {changes},` as a field in every newly added `.bib` entry.
- Do **not** add `markroles` to entries that already existed before the current
  task — only mark what is new or changed in this editing session.
- A `markroles` field holds exactly one role. Never list two roles in one
  entry.
- Example:
  ```bibtex
  @article{smith2024example,
    author    = {Smith, Alice},
    title     = {Example Paper},
    journal   = {J. Example Res.},
    year      = {2024},
    doi       = {10.0000/...},
    markroles = {changes},
  }
  ```
- After editing `.bib`, always run a full build (biber + pdflatex ×3) so that
  biber picks up the new field and the highlighting renders correctly.

## Approving Markings

When the user asks to approve or accept marked changes (for example "approve
all changes" or "accept the marked edits in this section"), delegate to the
[`approve-changes-markings`](../.claude/agents/approve-changes-markings.agent.md)
agent. It removes `\Mark{changes}` and `MarkEnv{changes}` wrappers, keeps only
the new argument of each `\MarkEdit{edits}`, strips `markroles = {changes}`
fields in the inferred scope, preserves every `missing` marker, and rebuilds
the paper. It leaves nested markers and multi-role `markroles` fields
unchanged and reports them as rule violations. Only approve markings when the
user explicitly asks.

## Figures and other assets

### Figures

Throughout this section, `<paper-dir>` stands for whichever manuscript directory
you are working in. The rules below apply to each manuscript independently.

- Figures that are used for a paper are kept separately in that paper's own `publications/<paper-dir>/figures/` directory. Even at the cost of duplicating some assets, we prefer to keep the paper figures separate from other project figures to avoid confusion and maintain a clear structure.
- The manuscript source under `publications/<paper-dir>/` must not reference `artifacts/` or other generated/ignored directories directly. Copy the final figure asset into `publications/<paper-dir>/figures/` first, then reference the paper-local copy.
- Thus, when a figure is needed for the paper, it should be copied to the `publications/<paper-dir>/figures/` directory and edited there if needed. Equally, if a figure file is no longer used in the paper, it should be removed from the `publications/<paper-dir>/figures/` directory to avoid clutter and confusion.

### TikZ Figure Organization

- Prefer storing long TikZ figure code in dedicated files rather than
    inline inside section text.
- Place those files in `publications/<paper-dir>/figures/tikz_art/`.
- Use descriptive file names that reflect the figure purpose
    (for example, `method_comparison_graphs.tikz.tex`).
- In section files, include TikZ art via `\input{...}` to keep source
    readable and easier to review.



## Writing and Formatting Best Practices

### NEVER write long lines of LaTeX code
- Break long lines of LaTeX code into multiple lines for better readability.
- Each line should be up to ~100 characters long when possible, and new sentences or logical units should start on a new line.

#### Text Example Style
```latex
Each estimate is itself an unbiased statistic of the samples~$x_1,\dots,x_n$ %
whose variance~$\sigma'^2$ can be read off by matching to
the form in~\eqref{eq:variance-decomposition}.
```

### Equation Formatting

When writing long LaTeX equations, format them as readable multiline blocks with consistent indentation.

- Indent nested expressions one level deeper than their parent expression.
- Keep operators and major structural elements on their own lines when this improves readability.
- Avoid compressing complex expressions into a single dense line.

#### Example Style
```latex
$$
    \mathcal{L}(\theta) =
    \sum_{i=1}^{N}
    \log\!\left(
        \frac{
            p_\theta\!\left(
                y_i \mid x_i
            \right)
        }{
            q\!\left(
                y_i
            \right)
        }
    )
$$
```



## Definition of Done

A publications-sector task is done only when all required gates below pass.

### Gate 1: LaTeX Build Integrity (Always Required)

- Compile the manuscript PDF after changes.
- If any LaTeX compilation error occurs, the task is not complete.

- Check that references compile correctly and are properly formatted. So no "[?]" placeholders references should remain. Also the citation table should appear.
- Verify that the generated PDF artifact is fresh in the current VS Code session.


### Gate 2: Figure Quality Review (Required When Figures Were Requested)

- Use AI as a visual judge on the generated PDF output.
- Render the page(s) holding the figure(s) to images (for example with
    `pdftoppm -png -r 150 -f <page> -l <page> main.pdf <out-prefix>` or
    PyMuPDF) and inspect the images.
- Confirm that figure quality is acceptable (readability, layout, labeling,
    and visual coherence with the manuscript).

### Gate 3: Text Quality and Story Alignment (Required When Manuscript Text Is Revised)

- Use AI as a writing and narrative judge for revised text.
- Verify flow, self-consistency, alignment with the paper's story, and writing style.

### Mandatory Retry Loop

- If any gate fails or appears questionable, report the issue back to the working
    agent (or calling agent), revise, and re-run the relevant gate checks.
- Do not return to the user (or calling agent) until all required gates pass.
