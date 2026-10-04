# Publications Sector Guidance

> **STOP — READ THIS BEFORE MAKING ANY EDIT**
>
> Every addition or change to a `.tex` or `.bib` file MUST be wrapped with the Mark API:
> - Inline text: `\Mark{changes}{...}`
> - Block text / whole paragraph: `\begin{MarkEnv}{changes}[text] ... \end{MarkEnv}`
> - Equations: `\begin{MarkEnv}{changes}[math] ... \end{MarkEnv}`
> - Figures: `\begin{MarkEnv}{changes}[figure] ... \end{MarkEnv}`
> - Headings: `\Mark{changes}[heading]{...}` inside the heading argument
> - New `.bib` entries: add `markroles = {changes},` as a field
>
> **No plain edits are acceptable. Unmarked changes are incomplete changes.**

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


## Formatting New and Missing Content

To maintain clean highlights across text, equations, and figures, use the Mark API instead of plain text colors.

- Standard additions or changes:
- Text (inline): use `\Mark{changes}{...}`.
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
- Example:
  ```bibtex
  @article{smith2024example,
    author    = {Smith, Alice},
    title     = {Example Paper},
    journal   = {Phys. Rev. Lett.},
    year      = {2024},
    doi       = {10.1103/...},
    markroles = {changes},
  }
  ```
- After editing `.bib`, always run a full build (biber + pdflatex ×3) so that
  biber picks up the new field and the highlighting renders correctly.

## Removing Markings Before Submission

Run the `approve-changes-markings` prompt
(`.github/prompts/approve-changes-markings.prompt.md`) to strip approved
`\Mark{changes}` wrappers and `markroles = {changes}` fields from a paper.
Only do this when the user explicitly asks.

## Figures and other assets

### Manuscript Directories

Each manuscript lives in its own `publications/paper---<slug>/` directory with
`main.tex`, `config.tex`, `references.bib`, `sections/`, and `figures/`. The
shared Mark API lives in `publications/modules/markings/` and is loaded by
relative path from each paper's `config.tex`. The starter manuscript is
[`paper---example/`](paper---example/); copy it to start a new paper.

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
