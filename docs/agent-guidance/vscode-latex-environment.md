# VS Code and LaTeX Environment

This is the canonical guide for compiling LaTeX and configuring the VS Code/LaTeX
workflow in this repository. It applies to agents and humans. The executable
configuration lives in `.vscode/settings.json`; when this guide and that file
disagree, inspect the file and update this guide in the same change.

## Mandatory Agent Gate

Before compiling any LaTeX project, editing LaTeX build configuration, or
applying VS Code user/global settings for this workflow, read this file and
inspect the current `.vscode/settings.json`.

Agents must follow these rules:

1. Reproduce the exact commands in **Commands and Full Sequence** below. Do not
   run bare `latexmk -pdf`, because it puts intermediate files in the source
   directory.
2. Keep every project's intermediate files in its own `.latex_build/` directory.
3. Do not start a second LaTeX build while another build is active.
4. After changing publication LaTeX, run the full build. Compilation errors
   leave the task incomplete.
5. Do not modify VS Code user settings or user keybindings unless the user
   explicitly requests it. Merge entries into the existing JSON; never replace
   the whole user file.

## Source of Truth

| Purpose | Maintained location |
| --- | --- |
| This policy, setup, and troubleshooting guide | `docs/agent-guidance/vscode-latex-environment.md` |
| LaTeX Workshop recipes and workspace appearance | `.vscode/settings.json` |
| Publication editing and marking rules | `publications/AGENTS.md` |
| English manuscript workflow and diagnostics | `.agents/skills/latex-paper-en/SKILL.md` |

Do not create project-local compilation guides. Put generally reusable changes
here and executable changes in `.vscode/settings.json`. A truly
project-specific validation command (for example a marking preflight script)
may be recorded in this guide under a heading for that manuscript.

Machine-local helpers such as `.vscode/tasks.json`, `.vscode/keybindings.json`,
or root-discovery scripts are intentionally **not** part of this template. A
developer may add them locally; if they become a shared standard, commit them
and document them here in the same change.

### Agent Routing and Precedence

For English LaTeX manuscript editing, auditing, or compilation, load and follow
`.agents/skills/latex-paper-en/SKILL.md`. Do not load that skill for a pure VS
Code configuration task unless the request also involves manuscript work.

Apply overlapping guidance in this order:

1. Publication instructions control repository-local manuscript requirements,
   including the Mark API and completion gates.
2. This guide controls repository-specific build commands, `.latex_build/`
   placement, and VS Code behavior.
3. The `latex-paper-en` skill controls manuscript analysis and editing workflow.
4. Generic defaults inside skill modules (such as a bare `latexmk` call) apply
   only when they do not conflict with the preceding sources.

## Prerequisites

Install a TeX distribution that provides `pdflatex` and `biber` on `PATH`
(MiKTeX on Windows, TeX Live on Linux/macOS). Install these VS Code extensions
as needed:

- LaTeX Workshop (`James-Yu.latex-workshop`): compilation, PDF viewing, and
  SyncTeX.
- vscode-icons (`vscode-icons-team.vscode-icons`): optional Explorer folder
  icons.

## Repository Build Model

### Project Roots

Every independent root `.tex` file must begin with a magic comment naming
itself:

```latex
% !TEX root = main.tex
```

Use the actual filename for standalone documents. This prevents LaTeX Workshop
from selecting another project's `main.tex` in this multi-project workspace.
Standalone files must also declare all packages they require instead of relying
on another paper's shared preamble.

### Output Placement

- Final PDF: next to the root `.tex` file.
- SyncTeX output: next to the root `.tex` file.
- All auxiliary output: the project-local `.latex_build/` directory.

The repository `.gitignore` contains:

```gitignore
**/.latex_build/
publications/**/main.pdf
*.synctex.gz
*.synctex(busy)
```

After a build, no `.aux`, `.bbl`, `.bcf`, `.blg`, `.log`, `.fls`, or
`.fdb_latexmk` files should appear beside the source files.

### Commands and Full Sequence

Run every command **from the manuscript directory** (the directory holding
`main.tex`, e.g. `publications/paper---example/`):

```powershell
pdflatex -synctex=1 -interaction=nonstopmode -file-line-error --aux-directory=.latex_build main.tex
biber --input-directory=.latex_build --output-directory=.latex_build main
pdflatex -synctex=1 -interaction=nonstopmode -file-line-error --aux-directory=.latex_build main.tex
pdflatex -synctex=1 -interaction=nonstopmode -file-line-error --aux-directory=.latex_build main.tex
```

That is the full bibliography-aware sequence
`pdflatex -> biber -> pdflatex -> pdflatex`. Agents may add `-halt-on-error`
to the `pdflatex` calls for focused failure reporting.

`--aux-directory` is a MiKTeX option. On TeX Live, replace it with
`-output-directory=.latex_build` and move the PDF and SyncTeX file back next to
`main.tex` after the last pass (or set `TEXMFOUTPUT`); keep the `biber` flags
unchanged.

LaTeX Workshop defines the same tools as two manually selectable recipes:

- `pdfLaTeX (quick)`: one `pdflatex` pass.
- `pdfLaTeX -> Biber -> pdfLaTeX x2 (full)`: the complete sequence; this is the
  default recipe used by **LaTeX Workshop: Build LaTeX project**.

LaTeX Workshop automatic builds are disabled (`autoBuild.run: never`) because a
save-triggered build would race an explicit full build started by an agent or
by hand and could corrupt shared auxiliary files. Always verify that no build is
already active before starting another.

### Cleaning

Delete stale `.latex_build/main.aux`, `.bbl`, `.bcf`, and `.blg` files to force
a clean rebuild. LaTeX Workshop is configured to understand build subfolders
but never to clean automatically.

## Publication Validation

For every changed publication project:

1. Run any project-specific preflight recorded below.
2. Run the full `pdflatex -> biber -> pdflatex -> pdflatex` sequence.
3. Confirm there are no LaTeX errors.
4. Confirm the bibliography and cross-references resolve (no `[?]` or `??`).
5. Confirm intermediate files remain under the project's `.latex_build/`
   directory.
6. Confirm only expected final outputs appear beside the root source.

### Project-Specific Preflights

None yet. Record a heading per manuscript here when one gains a preflight
command.

## Troubleshooting

### Missing or Stale Bibliography

A new paper or stale cache needs the full sequence, not a single `pdflatex`
pass. Typical symptoms are:

- Exit code 1 even though a PDF was written.
- `File ended while scanning use of \abx@aux@segm`.
- `Runaway argument?` near `\begin{document}`.
- `Package biblatex Warning: Please (re)run Biber`.

Delete the stale cache entries (see **Cleaning**), then run the full sequence.

### Concurrent Build Corruption

Two builds can write `main.aux` simultaneously and truncate it, producing the
same symptoms as a missing `.bbl`. Wait until the active build completes before
launching another. Then clean the stale intermediates and rebuild.

### Unresolved References or Figures

- For unresolved citations, run the full sequence.
- For unresolved cross-references, run another `pdflatex` pass after the full
  sequence.
- For broken figures, resolve paths relative to the root `.tex` file's
  directory.

## Workspace Experience

The committed workspace opens PDFs in a VS Code tab and configures double-click
backward SyncTeX. Explorer folder associations display `code/`, `research/`,
and `publications/` with distinct icons when vscode-icons is installed.
