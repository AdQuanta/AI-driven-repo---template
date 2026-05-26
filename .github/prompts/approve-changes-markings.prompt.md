---
name: approve-changes-markings
description: "Approve marked LaTeX changes by inferred span (selection, file, citations, or global), remove only role=changes wrappers/fields, keep role=missing, and rebuild."
---

# Accept Changes Markings

Use this prompt when the user wants to accept highlighted edits.
The agent must infer approval span from context and execute directly, without confirmation loops.

## Input

Expected input from the user message and editor context:
- `project_root`: path to the LaTeX project root (for example `publications/paper`)
- Optional `main_tex`: root TeX file (default `main.tex`)
- Optional `scope_glob`: files to process (default `**/*.tex` and `**/*.bib` under `project_root`)
- Optional cited range/selection from active editor context
- Optional file mention in user text

Approval understanding (semantic, not literal):
- Treat natural requests like "approve all", "accept all changes", "approve everything", "approve in this file", "approve this part", and "approve citations" as explicit authorization.
- Do not require an exact sentence.

If absolutely necessary input is missing (for example no detectable project root), infer from workspace structure before asking.

## Goal

Remove highlighting wrappers for role `changes` everywhere in scope while preserving content.
Do not remove or alter role `missing` markers.

## Hard Rules

- Clean only role `changes`.
- Do not touch role `missing`.
- Keep textual content, math content, and figure content exactly as authored.
- Preserve surrounding LaTeX structure and formatting as much as possible.
- Execute cleanup directly once scope is inferred; do not ask for additional confirmation.
- Perform cleanup in one batch and then run a full LaTeX build.

## Scope Inference (Priority Order)

Infer span from user intent and editor context in this exact order:

1. **Selection/Area scope**:
- If user refers to "this area", "this section", "this part", or selection is available, apply only to that cited span in the active file.

2. **File scope**:
- If user refers to "this file" or provides a file path, apply to that file only.
- If no file is named but an active file exists in editor context, use the active file.

3. **Citation scope**:
- If user says "approve citations" (or equivalent), clean `changes` markings related to citations in the inferred span.
- Also open relevant `.bib` file(s) and clean matching `markroles` entries for cited keys in that span.

4. **Global scope**:
- If user intent is all-inclusive ("approve all", "everything", "all changes"), apply across all in-scope `*.tex` and `*.bib` files under `project_root`.

Fallback:
- If intent is ambiguous, default to active-file scope and proceed.

## Marking Patterns To Clean

The project uses the marking API in `modules/markings.tex`.

### TeX wrappers

1. Inline mark macro:
- `\\Mark{changes}{...}` -> `...`
- `\\Mark{changes}[text]{...}` -> `...`
- `\\Mark{changes}[heading]{...}` -> `...`
- `\\Mark{changes}[math]{...}` -> `...`

2. Block environment — **kind-dependent replacement**:
- `\\begin{MarkEnv}{changes}[text] ... \\end{MarkEnv}` → inner content only
- `\\begin{MarkEnv}{changes}[math] ... \\end{MarkEnv}` → **`\\begin{equation}\n...\n\\end{equation}`**
  (the `[math]` wrapper IS the math mode; stripping without wrapping breaks the build)
- `\\begin{MarkEnv}{changes}[figure] ... \\end{MarkEnv}` → inner content only

3. Nested wrappers:
- Remove recursively until no `changes` wrapper remains.

### Bibliography markers

In `.bib` files, remove `changes` from:
- `markroles = {changes}` (remove full field)
- `markroles = {changes, ...}` or `{..., changes}` (remove only token `changes`, keep others)
- If the resulting list is empty, remove the entire `markroles` field.

For citation-scope approval:
- Parse cited keys in target TeX scope from standard citation commands (`\\cite`, `\\parencite`, `\\textcite`, etc.).
- Locate those keys in bibliography file(s) used by the project.
- Clean `changes` token in `markroles` for those entries only.

## Procedure

1. Infer scope using the priority rules above.
2. Discover candidate files for that scope.
3. Apply cleanup edits for role `changes` only in inferred scope.
4. For citation-scope or global-scope approvals, clean applicable `.bib` `markroles` as specified.
5. Run search checks and confirm:
- no remaining `\\Mark{changes}`
- no remaining `\\begin{MarkEnv}{changes}`
- no remaining in-scope `markroles` entries containing `changes` that should have been approved
6. Run full LaTeX build for the target project.
7. Report the result.

## Implementation Guidance

### Step 1 — Locate every marker with the finder script

Run the [finder script](./scripts/find_changes_markers.py) to get a precise, line-numbered inventory:

```powershell
.venv\Scripts\python.exe .github/prompts/scripts/find_changes_markers.py publications/paper
```

Output format per match:
```
PATH:LINE [KIND] SNIPPET
```

Kinds and what each removal requires:
| Kind | Removal action |
|---|---|
| `Mark-inline` | Strip `\Mark{changes}[opt]{...}` → inner `...` |
| `MarkEnv-text` | Strip `\begin{MarkEnv}{changes}[text]...\end{MarkEnv}` → inner content |
| `MarkEnv-math` | Replace `\begin{MarkEnv}{changes}[math]...\end{MarkEnv}` → `\begin{equation}...\end{equation}` (**math mode must be preserved**) |
| `MarkEnv-fig` | Strip `\begin{MarkEnv}{changes}[figure]...\end{MarkEnv}` → inner content |
| `markroles-bib` | Remove `markroles = {changes},` field line from `.bib` entry |

### Step 2 — Edit files directly with agent tools

For each hit from the finder, use `read_file` to read the exact surrounding
lines, then use `replace_string_in_file` to make the precise substitution.

Do **not** write a bulk-transform script. The agent's built-in file-editing
tools are more reliable and produce easier-to-review diffs.

Key rules for making edits:
- Include 3-5 lines of unchanged context in `oldString` so the match is unique.
- For `MarkEnv-math`, replace the whole `\begin{MarkEnv}...\end{MarkEnv}` block
  with `\begin{equation}...\end{equation}` keeping the body untouched.
- For `Mark-inline` spanning multiple lines, capture the full brace-balanced
  group by reading ahead with `read_file`.

### Step 3 — Validate

After all edits, re-run the finder script and confirm exit 0 (zero markers):

```powershell
.venv\Scripts\python.exe .github/prompts/scripts/find_changes_markers.py publications/paper
```

Then run the project full build task to confirm no LaTeX errors were introduced.

## Output Contract

Return:
- inferred scope and why (selection/file/citations/global)
- list of edited files
- count of removed `changes` wrappers/fields
- build result (pass/fail)
- any ambiguous cases requiring manual review
