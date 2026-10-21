# VS Code and LaTeX Environment

This is the canonical guide for compiling LaTeX and configuring the VS Code/LaTeX workflow in this repository. It applies to agents and humans. The executable configuration remains in `.vscode/`; when this guide and the executable files disagree, inspect the executable files and update this guide in the same change.

## Mandatory Agent Gate

Before compiling any LaTeX project, editing LaTeX build configuration, or applying VS Code user/global settings for this workflow, read this file and inspect the current `.vscode/settings.json`, `.vscode/tasks.json`, `.vscode/find-latex-root.ps1`, and `.vscode/latex-full-build.ps1`.

Agents must follow these rules:

1. Use the configured tasks or, as an agent, the [Agent Build Recipe](#agent-build-recipe). Do not run bare `latexmk -pdf`, because it puts intermediate files in the source directory.
2. Keep every project's intermediate files in its own `.latex_build/` directory.
3. Do not start a second LaTeX build while another build is active.
4. After changing publication LaTeX, complete the required preflight and full build. Compilation errors leave the task incomplete.
5. When changing VS Code user settings or user keybindings, merge the documented entries into the existing JSON; never replace the whole user file.

## Source of Truth

| Purpose | Maintained location |
| --- | --- |
| This policy, setup, and troubleshooting guide | `docs/agent-guidance/vscode-latex-environment.md` |
| LaTeX Workshop recipes and workspace appearance | `.vscode/settings.json` |
| Workspace task chain | `.vscode/tasks.json` |
| Active-file root discovery | `.vscode/find-latex-root.ps1` |
| Build commands shared by tasks and agents | `.vscode/latex-full-build.ps1` |
| Publication editing and marking rules | `publications/AGENTS.md` |
| English manuscript workflow and diagnostics | `.agents/skills/latex-paper-en/SKILL.md` |

The repository ships no `.vscode/keybindings.json`: VS Code reads keybindings only from user-level configuration. The suggested user-level bindings are listed under [Applying User/Global VS Code Configuration](#applying-userglobal-vs-code-configuration).

Do not create project-local compilation guides. Put generally reusable changes here and put executable changes in `.vscode/`. A truly project-specific validation command may be recorded in this guide under the relevant project heading in [Publication Validation](#publication-validation).

### Agent Routing and Precedence

For English LaTeX manuscript editing, auditing, or compilation, load and follow
`.agents/skills/latex-paper-en/SKILL.md`. Do not load that skill for a pure VS
Code configuration, root-discovery, or unrelated asset task unless the request
also involves manuscript work.

Apply overlapping guidance in this order:

1. Publication instructions control repository-local manuscript requirements,
    including the Mark API and completion gates.
2. This guide controls repository-specific build commands, task selection,
    `.latex_build/` placement, preflight, and VS Code behavior.
3. The `latex-paper-en` skill controls manuscript analysis and editing workflow.
4. Generic defaults inside skill modules apply only when they do not conflict
    with the preceding sources.

In particular, do not use the skill's generic bare `latexmk` default in this
repository. Use `LaTeX: Full Build Sequence` or reproduce the commands defined
in this guide.

## Prerequisites

Install a TeX distribution that provides `pdflatex`, `bibtex`, and `biber` on `PATH`. On Windows, MiKTeX is suitable; on Linux and macOS, TeX Live is. The VS Code tasks and the agent build script run under Windows PowerShell. Install these VS Code extensions as needed:

- LaTeX Workshop (`James-Yu.latex-workshop`): compilation, PDF viewing, and SyncTeX.
- Settings Cycler (`hoovercj.vscode-settings-cycler`): required only for the PDF-only inversion shortcut.
- vscode-icons (`vscode-icons-team.vscode-icons`): optional Explorer folder icons.

LaTeX Workshop `10.13.1` is a known-good version. Version `10.14.1` was observed to break double-click backward SyncTeX; if that behavior recurs, test a current version first and fall back to `10.13.1` if necessary.

## Repository Build Model

### Project Roots

Every independent root `.tex` file must begin with a magic comment naming itself:

```latex
% !TEX root = main.tex
```

Use the actual filename for standalone documents. This prevents LaTeX Workshop from selecting another project's `main.tex` in this multi-project workspace. Standalone files must also declare all packages they require instead of relying on another paper's shared preamble.

The workspace task helper starts at the active file's directory and walks upward toward the workspace root until it finds `main.tex`. The task runs from that directory. Consequently, the shared task chain supports any nested project whose root is named `main.tex`; a differently named root can still use LaTeX Workshop's active-document recipe but requires an explicitly scoped task if it needs the shared task workflow.

### Output Placement

- Final PDF: next to the root `.tex` file.
- SyncTeX output: next to the root `.tex` file.
- All auxiliary output: the project-local `.latex_build/` directory.

The repository `.gitignore` contains:

```gitignore
.latex_build/
publications/**/main.pdf
*.synctex.gz
*.synctex(busy)
```

After a build, no `.aux`, `.bbl`, `.bcf`, `.blg`, `.log`, `.fls`, or `.fdb_latexmk` files should appear beside the source files.

### Commands and Full Sequence

The full sequence is:

```text
pdflatex -> bibliography tool -> pdflatex -> pdflatex
```

#### Windows and MiKTeX

The configured tools use these arguments:

```text
pdflatex -synctex=1 -interaction=nonstopmode -file-line-error --aux-directory=.latex_build <root.tex>
biber --input-directory=.latex_build --output-directory=.latex_build <root-without-extension>
bibtex .latex_build/<root-without-extension>
```

Workspace tasks and the agent build script additionally use `-halt-on-error` for focused build failure reporting. `--aux-directory` is a MiKTeX option: the PDF is written next to the root file and everything else goes to `.latex_build/`.

#### TeX Live (Linux, macOS, and CI)

TeX Live's `pdflatex` has no `--aux-directory`; use `-output-directory` instead. It does not create that folder, so create it first. Run from the manuscript folder, because manuscripts load `../modules/markings/…` by relative path:

```text
mkdir -p .latex_build
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=.latex_build main.tex
biber --input-directory=.latex_build --output-directory=.latex_build main
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=.latex_build main.tex
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=.latex_build main.tex
mv .latex_build/main.pdf .
```

The last step moves the PDF next to `main.tex`, matching the MiKTeX layout. For a BibTeX project, replace the `biber` line with `bibtex .latex_build/main`.

### VS Code Tasks

In VS Code, run the default task `LaTeX: Full Build Sequence`. Its ordered component tasks are:

1. `LaTeX: First pdfLaTeX Pass`
2. `LaTeX: Run Bibliography`
3. `LaTeX: Second pdfLaTeX Pass`
4. `LaTeX: Third pdfLaTeX Pass`

Each task calls `.vscode/find-latex-root.ps1` to locate the project root and then `.vscode/latex-full-build.ps1` for one step. The bibliography task reads the first-pass `.aux`: `\bibdata` selects BibTeX; otherwise a `.bcf` selects Biber. The aggregate `LaTeX: Full Build Sequence` supports both bibliography systems while keeping intermediates under `.latex_build/`.

LaTeX Workshop also defines these manually selectable recipes in `.vscode/settings.json`:

- `pdfLaTeX (quick)`: one `pdflatex` pass.
- `pdfLaTeX -> Biber -> pdfLaTeX x2 (full)`: the same complete sequence using active-document placeholders.
- `pdfLaTeX -> BibTeX -> pdfLaTeX x2 (full)`: the corresponding BibTeX sequence.

LaTeX Workshop automatic builds are disabled because a save-triggered quick recipe would race the explicit full task and could corrupt shared auxiliary files. The optional user-level `Ctrl+S` and `Ctrl+Shift+B` bindings documented below each save and launch the named full sequence. Always verify that no build is already active before starting another.

### Agent Build Recipe

Agents cannot start VS Code tasks. On Windows, run the script that the
`LaTeX: Full Build Sequence` task uses, from the repository root:

```powershell
.vscode\latex-full-build.ps1 -ProjectDir <path-to-folder-with-main.tex> -Quiet
```

`-ProjectDir` may be relative to the repository root or absolute. `-Quiet` hides tool output but keeps status lines and the
closing summary: page count, undefined references or citations, and overfull
boxes. The script exits nonzero on any LaTeX or bibliography error, and exits
`2` without building if a LaTeX process is already running. On Linux or macOS,
run the [TeX Live sequence](#tex-live-linux-macos-and-ci) from the manuscript
folder and check `.latex_build/main.log` for undefined references.

- Before building, tell the user not to save in VS Code until the build
  finishes, because `Ctrl+S` starts a second build when the optional binding
  is installed.
- After building, report the summary. Undefined references leave the task
  incomplete.
- If the project records a page limit, check the page count against it.

### Cleaning

Use `LaTeX: Clean Intermediates` to remove stale `.latex_build/main.aux`, `.bbl`, `.bcf`, and `.blg` files. LaTeX Workshop is configured to understand build subfolders but never clean automatically.

## Publication Validation

For every changed publication project:

1. Run any project-specific preflight.
2. Run the full `pdflatex -> bibliography tool -> pdflatex -> pdflatex` sequence.
3. Confirm there are no LaTeX errors.
4. Confirm the bibliography and cross-references resolve.
5. Confirm intermediate files remain under the project's `.latex_build/` directory.
6. Confirm only expected final outputs appear beside the root source.

### Example Paper

The project root is `publications/paper---example/`, its root file is `main.tex`, it uses biblatex with Biber, and its cache is `.latex_build/` inside that directory. It has no preflight. Build it on Windows with:

```powershell
.vscode\latex-full-build.ps1 -ProjectDir publications\paper---example -Quiet
```

On Linux or macOS, run the TeX Live sequence above from `publications/paper---example/`. CI builds it the same way.

When the project adds its own manuscripts, record any manuscript-specific preflight, alternative build (for example a plain submission PDF), or page limit here under a heading for that manuscript.

## Troubleshooting

### Missing or Stale Bibliography

A new paper or stale cache needs the full sequence, not a single `pdflatex` pass. Typical symptoms are:

- Exit code 1 even though a PDF was written.
- `File ended while scanning use of \abx@aux@segm`.
- `Runaway argument?` near `\begin{document}`.
- `Package biblatex Warning: Please (re)run Biber`.

Remove the stale cache entries with `LaTeX: Clean Intermediates`, then run `LaTeX: Full Build Sequence`.

### Concurrent Build Corruption

Two builds can write `main.aux` simultaneously and truncate it, producing the same symptoms as a missing `.bbl`. Wait until the active full sequence completes before saving again or launching another task. Then clean the stale intermediates and rebuild.

### Unresolved References or Figures

- For unresolved citations, run the full sequence.
- For unresolved cross-references, run another `pdflatex` pass after the full sequence.
- For broken figures, resolve paths relative to the root `.tex` file's directory.
- If no task runs, confirm the active file is below a directory containing `main.tex` and that directory is below the workspace root.

## Current Workspace Experience

The committed workspace opens PDFs in a VS Code tab and configures double-click backward SyncTeX. Explorer folder associations display `code/` as `src`, `research/` as `library`, and `publications/` as `docs` when vscode-icons is installed. vscode-icons does not pick up `vsicons.associations.folders` from a fresh clone automatically: if these folders show plain icons, run `vscode-icons: Apply Icons Customization` from the Command Palette and reload the window.

Without any user-level configuration, double-clicking in the PDF runs backward SyncTeX and `LaTeX: Full Build Sequence` runs from **Terminal > Run Build Task**. The keyboard shortcuts below require the optional user-level keybindings.

## Applying User/Global VS Code Configuration

User settings and global keybindings live outside the repository and are not applied by cloning it. Open them through the Command Palette using `Preferences: Open User Settings (JSON)` and `Preferences: Open Keyboard Shortcuts (JSON)`. Merge the entries below with existing content and preserve unrelated settings and bindings.

### User Settings

These settings make PDF inversion independent of the VS Code theme:

```json
{
    "latex-workshop.view.pdf.viewer": "tab",
    "latex-workshop.view.pdf.internal.synctex.keybinding": "double-click",
    "latex-workshop.view.pdf.invertMode.enabled": "compat",
    "latex-workshop.view.pdf.invert": 0.9,
    "latex-workshop.view.pdf.invertMode.brightness": 0.99,
    "latex-workshop.view.pdf.invertMode.grayscale": 0,
    "latex-workshop.view.pdf.invertMode.sepia": 0.01
}
```

In `compat` mode, inversion is active only when `latex-workshop.view.pdf.invert` is greater than zero. Changing inversion settings requires refreshing the PDF viewer.

### Global Keybindings

Add these objects inside the existing user `keybindings.json` array:

```json
{
    "key": "ctrl+s",
    "command": "runCommands",
    "when": "editorLangId == latex",
    "args": {
        "commands": [
            "workbench.action.files.save",
            {
                "command": "workbench.action.tasks.runTask",
                "args": "LaTeX: Full Build Sequence"
            }
        ]
    }
},
{
    "key": "ctrl+shift+b",
    "command": "runCommands",
    "when": "editorLangId == latex",
    "args": {
        "commands": [
            "workbench.action.files.save",
            {
                "command": "workbench.action.tasks.runTask",
                "args": "LaTeX: Full Build Sequence"
            }
        ]
    }
},
{
    "key": "ctrl+shift+m",
    "command": "runCommands",
    "args": {
        "commands": [
            {
                "command": "settings.cycle",
                "args": {
                    "id": "pdfInvert",
                    "overrideWorkspaceSettings": true,
                    "values": [
                        { "latex-workshop.view.pdf.invert": 0.9 },
                        { "latex-workshop.view.pdf.invert": 0 }
                    ]
                }
            },
            "latex-workshop.refresh-viewer"
        ]
    }
},
{
    "key": "f9",
    "command": "latex-workshop.synctex",
    "when": "editorTextFocus && editorLangId == latex"
}
```

The resulting shortcuts are:

| Shortcut | Action |
| --- | --- |
| `Ctrl+S` in LaTeX | Save and run the repository's full build task. |
| `Ctrl+Shift+B` in LaTeX | Save and run the repository's full build task. |
| `Ctrl+Shift+M` | Toggle PDF-only dark/light inversion and refresh the viewer. |
| `F9` | Forward SyncTeX from source to PDF. |
| Double-click in the PDF | Backward SyncTeX from PDF to source (workspace setting; no binding needed). |

The global `Ctrl+S` and `Ctrl+Shift+B` bindings assume the open workspace provides a task named `LaTeX: Full Build Sequence`. Remove or scope those bindings differently when working in LaTeX workspaces that do not define this task.

## Maintaining This Integration

When changing the workflow:

1. Edit the executable `.vscode/` configuration first.
2. Update this guide in the same change.
3. If agent behavior changes, edit the root or sector `AGENTS.md` files directly. Do not create generated copies.
4. After editing an `AGENTS.md`, re-read it and confirm no generated or
   projected copy was created elsewhere.
5. Search for removed task names, paths, and superseded guides before completion.
