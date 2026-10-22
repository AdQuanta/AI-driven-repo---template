---
name: approve-changes-markings
description: Approves marked LaTeX edits. Use when the user asks to approve or accept changes, marked edits, or citations. Removes changes/edits wrappers in the inferred scope, keeps only accepted content, preserves role=missing, and rebuilds the paper.
tools:
- read
- search
- edit
- execute
- Read
- Grep
- Glob
- Edit
- Write
- Bash
- PowerShell
user-invocable: true
---

# Accept Changes Markings

The parent agent delegates to you when the user asks to accept highlighted edits, for example "approve all changes", "accept the marked edits", or "approve citations". The parent passes the user's words plus any editor selection or active file; use them as the scope evidence below.
The agent must infer approval span from context and execute directly, without confirmation loops.

## Input

Expected input from the delegation message (the user's request plus editor context):
- `project_root`: path to the LaTeX project root (for example `publications/paper---example`)
- Optional `main_tex`: root TeX file (default `main.tex`)
- Optional `scope_glob`: files to process (default `**/*.tex` and `**/*.bib` under `project_root`)
- Optional cited range/selection from active editor context
- Optional file mention in user text

Approval understanding (semantic, not literal):
- Treat natural requests like "approve all", "accept all changes", "approve everything", "approve in this file", "approve this part", and "approve citations" as explicit authorization.
- Do not require an exact sentence.

If absolutely necessary input is missing (for example no detectable project root), infer from workspace structure before asking.

## Goal

Remove addition wrappers for role `changes` and replacement wrappers for role
`edits` everywhere in scope. Preserve addition content and keep only the new
argument of each replacement.
Do not remove or alter role `missing` markers.

## Hard Rules

- Clean only `\Mark{changes}`, `MarkEnv{changes}`, `\MarkEdit{edits}`, and
  applicable bibliography `changes` tokens.
- Do not touch role `missing`.
- For `\MarkEdit{edits}`, discard the old argument and preserve only the new
  argument. An empty new argument deletes the replaced content.
- Keep accepted textual content, math content, and figure content exactly as authored.
- Preserve surrounding LaTeX structure and formatting as much as possible.
- Nested markers (one Mark API wrapper inside another) and `markroles` fields
  with more than one role are forbidden by `publications/AGENTS.md`. Do not
  approve either: leave it unchanged and list it under "Rule violations" in
  the report.
- Execute cleanup directly once scope is inferred; do not ask for additional confirmation.
- Perform cleanup in one batch and then run a full LaTeX build.

## Scope Inference (Priority Order)

Infer span from user intent and editor context in this exact order:

1. **Selection/Area scope**:
- If user refers to "this area", "this section", "this part", or selection is available, apply only to that cited span in the active file.

2. **File scope**:
- If user refers to "this file" or provides a file path, apply to that file only.
- If no file is named but an active file exists in editor context, use the active file.
- If the user identifies a project as "rooted at", "starting from", or equivalent
  and names its root `main.tex`, treat that path as the project root and use global scope.

3. **Citation scope**:
- If user says "approve citations" (or equivalent), clean `changes` markings related to citations in the inferred span.
- Also open relevant `.bib` file(s) and clean matching `markroles` entries for cited keys in that span.

4. **Global scope**:
- If user intent is all-inclusive ("approve all", "everything", "all changes"), apply across all in-scope `*.tex` and `*.bib` files under `project_root`.

Fallback:
- If intent is ambiguous, default to active-file scope and proceed.

## Marking Patterns To Clean

The project uses the marking API in `publications/modules/markings/markings.tex`.

### TeX wrappers

1. Inline mark macro:
- `\\Mark{changes}{...}` -> `...`
- `\\Mark{changes}[text]{...}` -> `...`
- `\\Mark{changes}[heading]{...}` -> `...`
- `\\Mark{changes}[math]{...}` -> `$...$`
  (the `[math]` wrapper supplies math mode; an empty payload becomes nothing)

2. Inline replacement macro:
- `\\MarkEdit{edits}{old}{new}` -> `new`
- `\\MarkEdit{edits}[text]{old}{new}` -> `new`
- `\\MarkEdit{edits}[math]{old}{new}` -> `$new$`
  (the `[math]` wrapper supplies math mode; an empty `new` argument becomes nothing)
- Example: `\\MarkEdit{edits}{old wording}{new wording}` -> `new wording`
- Delete the entire command wrapper and old argument; do not leave braces from
  either one around the accepted content.

3. Block environment — **kind-dependent replacement** (see `publications/modules/markings/markings.tex` for the disabled fallback):
- `\\begin{MarkEnv}{changes}[text] ... \\end{MarkEnv}` → inner content only
- `\\begin{MarkEnv}{changes}[math] ... \\end{MarkEnv}` → **`\\begin{equation}\n...\n\\end{equation}`**
  (the `[math]` wrapper IS the math mode; stripping without wrapping breaks the build)
- `\\begin{MarkEnv}{changes}[figure] ... \\end{MarkEnv}` → inner content only

4. Nested wrappers are forbidden. Leave a nested marker unchanged and report it
   under "Rule violations".

### Bibliography markers

A `markroles` field holds exactly one role. In `.bib` files:
- `markroles = {changes}`: remove the whole field.
- `markroles = {missing}`: leave it unchanged.
- A field listing two or more roles is forbidden: leave it unchanged and report
  it under "Rule violations".

For citation-scope approval:
- Parse cited keys in target TeX scope from standard citation commands (`\\cite`, `\\parencite`, `\\textcite`, etc.).
- Locate those keys in bibliography file(s) used by the project.
- Remove `markroles = {changes}` from those entries only.
- Do not modify other entry metadata.

## Procedure

1. Infer scope using the priority rules above.
2. Discover candidate files for that scope.
3. Apply cleanup edits for approvable `changes` and `edits` roles in inferred scope.
4. For citation-scope or global-scope approvals, clean applicable `.bib` `markroles` as specified.
5. Run search checks and confirm:
- no remaining `\\Mark{changes}`
- no remaining `\\MarkEdit{edits}`
- no remaining `\\begin{MarkEnv}{changes}`
- no remaining in-scope `markroles` entries containing `changes` that should have been approved
- except the rule violations you left unchanged: each remaining hit must be
  listed under "Rule violations"
6. Run full LaTeX build for the target project.
7. Report the result.

## Implementation Guidance

### Step 1 — Locate every marker with the finder script

Run the [finder script](../../publications/modules/markings/scripts/find_changes_markers.py) to get a precise, line-numbered inventory:

```text
python publications/modules/markings/scripts/find_changes_markers.py <path/to/paper>
```

Use the project virtual environment's interpreter when one exists
(`.venv\Scripts\python.exe` on Windows, `.venv/bin/python` elsewhere). The
finder exits `0` when no markers remain and `2` when it finds markers.

Output format per match:
```
PATH:LINE [KIND] SNIPPET
```

Kinds and what each removal requires:
| Kind | Removal action |
|---|---|
| `Mark-inline` | Strip `\Mark{changes}[opt]{...}`; keep the inner content and restore `$...$` for `[math]` |
| `MarkEdit-edits` | Strip `\MarkEdit{edits}[opt]{old}{new}`; discard `old`, keep `new`, and restore `$new$` for nonempty `[math]` |
| `MarkEnv-text` | Strip `\begin{MarkEnv}{changes}[text]...\end{MarkEnv}` → inner content |
| `MarkEnv-math` | Replace `\begin{MarkEnv}{changes}[math]...\end{MarkEnv}` → `\begin{equation}...\end{equation}` (**math mode must be preserved**) |
| `MarkEnv-fig` | Strip `\begin{MarkEnv}{changes}[figure]...\end{MarkEnv}` → inner content |
| `markroles-bib` | Remove the `markroles = {changes},` field line from the `.bib` entry; a field with two or more roles is a rule violation |

### Step 2 — Edit files directly with agent tools

For each hit from the finder, read the exact surrounding lines, then make a
targeted exact-string edit (several edits in one file are fine).

Do **not** write a bulk-transform script. The agent's built-in file-editing
tools are more reliable and produce easier-to-review diffs.

Key rules for making edits:
- Include 3-5 lines of unchanged context in the text you replace so the match is unique.
- For `MarkEnv-math`, replace the whole `\begin{MarkEnv}...\end{MarkEnv}` block
  with `\begin{equation}...\end{equation}` keeping the body untouched.
- For `Mark-inline` spanning multiple lines, capture the full brace-balanced
  group by reading ahead.
- For `MarkEdit-edits`, capture both complete brace-balanced arguments. Keep only
  the second argument, including when it is empty.
- If a wrapper's content holds another Mark API wrapper, the markers are nested:
  leave both unchanged and report them under "Rule violations".

### Step 3 — Validate with the finder and search

Prefer `rg` for supplemental searches when it is available; otherwise use the
environment's text-search tool.

After all edits, re-run the finder script. It must exit 0 (zero markers), or
exit 2 with every remaining hit listed under "Rule violations" (the finder
still reports the nested markers and multi-role fields you left unchanged):

```text
python publications/modules/markings/scripts/find_changes_markers.py <path/to/paper>
```

Then run the project's full LaTeX build, following
`docs/agent-guidance/vscode-latex-environment.md`, to confirm no LaTeX errors were introduced.

## Output Contract

Return:
- inferred scope and why (selection/file/citations/global)
- list of edited files
- separate counts of accepted `changes` additions, `edits` replacements,
  `MarkEnv` environments, and bibliography fields
- build result (pass/fail)
- "Rule violations": every nested marker and multi-role `markroles` field left
  unchanged, with its file and line (write "none" if there are none)
- any ambiguous cases requiring manual review

If ambiguous macro structure is encountered, apply the safest local edit and continue; include the snippet in the final report.
