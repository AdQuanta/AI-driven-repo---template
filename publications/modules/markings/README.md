# Marking Module

This folder contains a reusable LaTeX marking module.
It gives you a compact API for highlighting changed text,
flagging missing material, boxing display equations,
framing figure content, and coloring bibliography entries
through biblatex metadata.

## Folder Contents

- `markings.tex` implements the public macros and environments.
- `markings.dbx` declares the `markroles` biblatex field used for citation highlighting.
- `README.md` explains how to install and use the module.

## What The Module Does

- Defines named marking roles such as `changes` or `missing`.
- Maps each role to a color.
- Supports inline text marks, heading-safe marks, block math marks, and figure marks.
- Provides a placeholder-figure helper.
- Highlights bibliography entries and in-text citations when a `.bib` entry carries a matching `markroles` field.

## Installation

1. Load the required packages in your document preamble.

```latex
\usepackage[dvipsnames]{xcolor}
\usepackage{soul}
\usepackage{environ}
\usepackage{etoolbox}
\usepackage{xparse}
\usepackage[most]{tcolorbox}
\usepackage{xpatch}
\usepackage{pdfcomment}
```

2. Input the module file.

```latex
\input{path/to/markings.tex}
```

3. If you use biblatex highlighting, point the `datamodel` option at the companion `.dbx` file without the extension.

```latex
\usepackage[
  backend=biber,
  datamodel=path/to/markings
]{biblatex}
```

4. Define at least one role. The third argument sets the rendering state and is optional (default: `colored`).

```latex
\DefineMarkRole{changes}{green}                 % colored (default)
\DefineMarkRole{missing}{red}[plain]            % visible, no highlight
\DefineMarkRole{draft}{blue}[hidden]            % suppressed
```

## Main Commands

- `\DefineMarkRole{role}{color}[state]` registers a named role, its color, and an optional rendering state. `state` must be `colored` (default), `plain`, or `hidden`.
- `\SetMarkFallbackColor{color}` changes the color used when a role is missing or invalid.
- `\Mark{role}[kind]{content}` marks inline content.
- `\SetMarkEditMode{plain|popup|inline}` chooses how replacements appear. The default is `plain`.
- `\MarkEdit{role}[kind]{old}{new}` marks a replacement. `kind` defaults to `text`; `math` accepts bare inline math expressions.
- `\begin{MarkEnv}{role}[kind] ... \end{MarkEnv}` marks block content.
- `\MarkPlaceholderFigure{role}[layout]{description}{label}{caption}` inserts a placeholder figure with the chosen role styling.

Supported mark kinds are `text`, `math`, `figure`, and `heading`.
`\MarkEdit` supports `text` and `math`.

### Replacement modes

Define an edit role to choose the replacement highlight color. `edits` is an
ordinary role name, not a reserved word:

```latex
\DefineMarkRole{edits}{green}
\SetMarkEditMode{popup} % set explicitly for an annotated review PDF
\MarkEdit{edits}{old prose with $x^2$ and \cite{demo}}{new prose with $x^3$ and \cite{demo}}
\MarkEdit{edits}[math]{x^2}{x^3}
```

| Mode | Output |
|---|---|
| `plain` (default) | New text only, with no highlight or annotation. |
| `popup` | Green PDF highlight on new text with the old text in its popup; inside floats, a red note icon sits beside green highlighted new text. |
| `inline` | Red struck-through old text followed by green highlighted new text. |

The role's `plain` or `hidden` state also shows only the new text, regardless of
the edit mode. This lets a submission build override an annotated review build.
Popup notes use PDF annotations, whose appearance and interaction vary by viewer.
The viewer chooses the popup text color. PDF text markup anchors do not resolve
reliably inside floats, so edits in captions use a red note icon instead.
Replacement popups start with `Earlier version:` on a separate line; a deletion
without replacement starts with `Removed text:`. The PDF viewer controls the
popup font and size.
The note stores a readable PDF-text rendering of the old argument; math is
flattened and citations may appear as bibliography keys. For math macros omitted
from a note, add `\pdfstringdefDisableCommands` mappings in the document preamble
and inspect the rebuilt PDF. The new argument is
typeset normally in all modes. Keep `\MarkEdit` within a single paragraph.
For a caption, supply a plain optional short caption so the edit command is
not written to the list of figures or tables. Do not use it in headings.

## Rendering States

Each role carries a rendering state that controls how its marks appear.

| State | Text visible | Color applied |
|---|---|---|
| `colored` | yes | yes (default) |
| `plain` | yes | no |
| `hidden` | no (suppressed) | no |

Set the state as the optional third argument of `\DefineMarkRole`:

```latex
\DefineMarkRole{changes}{green}              % colored — highlight shown
\DefineMarkRole{notes}{gray}[plain]          % text shown without highlight
\DefineMarkRole{todo}{red}[hidden]           % content entirely suppressed
```

**Exception — headings:** when a role is `hidden` and used in a heading mark, the text is still rendered (but without color). Suppressing a heading would break TOC entries and cross-references. A package warning is emitted to alert you.

**Exception — citations:** bibliography citation colors are controlled by role state, but citations are never fully suppressed regardless of state.

## Examples

Inline text:

```latex
\Mark{changes}{This sentence was revised.}
```

Heading text:

```latex
\section{\Mark{changes}[heading]{Updated Heading}}
```

Displayed equation:

```latex
\begin{MarkEnv}{changes}[math]
E = mc^2
\end{MarkEnv}
```

Placeholder figure:

```latex
\MarkPlaceholderFigure{missing}{Add architecture diagram here.}{fig:arch}{Architecture overview.}
```

Bib entry metadata:

```bibtex
@article{example2026,
  author    = {Example, Ada},
  title     = {A Marked Reference},
  journal   = {Journal of Examples},
  year      = {2026},
  markroles = {changes},
}
```

## Important Behavior Notes

- Never nest one marker inside another. Nesting is forbidden, and a marker
  inside a highlighted marker does not compile.
- A `.bib` entry's `markroles` field holds exactly one role.
- `MarkEnv[math]` already supplies display-equation mode. Do not nest `equation` inside it.
- `MarkEnv[figure]` wraps content in a `tcolorbox`; it is not a floating `figure` environment.
- `\Mark{...}[heading]{...}` is the safe form for section and subsection titles.
- If you relocate this module, update both the `\input` path and the biblatex `datamodel` path together.

## Marker finder

`scripts/find_changes_markers.py <project_root>` lists every approvable
`changes`/`edits` marker under a manuscript, one `PATH:LINE [KIND] SNIPPET`
line each. It exits `0` when none remain and `2` when markers are found. The
`approve-changes-markings` agent runs it before and after cleanup. Test:
`python -m pytest publications/modules/markings/scripts -q`.
