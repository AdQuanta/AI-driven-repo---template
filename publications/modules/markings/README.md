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
\DefineMarkRole{changes}{CustomYellow}          % colored (default)
\DefineMarkRole{missing}{red}[plain]            % visible, no highlight
\DefineMarkRole{draft}{blue}[hidden]            % suppressed
```

## Main Commands

- `\DefineMarkRole{role}{color}[state]` registers a named role, its color, and an optional rendering state. `state` must be `colored` (default), `plain`, or `hidden`.
- `\SetMarkFallbackColor{color}` changes the color used when a role is missing or invalid.
- `\Mark{role}[kind]{content}` marks inline content.
- `\begin{MarkEnv}{role}[kind] ... \end{MarkEnv}` marks block content.
- `\MarkPlaceholderFigure{role}[layout]{description}{label}{caption}` inserts a placeholder figure with the chosen role styling.

Supported mark kinds are `text`, `math`, `figure`, and `heading`.

## Rendering States

Each role carries a rendering state that controls how its marks appear.

| State | Text visible | Color applied |
|---|---|---|
| `colored` | yes | yes (default) |
| `plain` | yes | no |
| `hidden` | no (suppressed) | no |

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

- `MarkEnv[math]` already supplies display-equation mode. Do not nest `equation` inside it.
- `MarkEnv[figure]` wraps content in a `tcolorbox`; it is not a floating `figure` environment.
- `\Mark{...}[heading]{...}` is the safe form for section and subsection titles.
- If you relocate this module, update both the `\input` path and the biblatex `datamodel` path together.
