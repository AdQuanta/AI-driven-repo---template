# approve-changes-markings fixture — answer key

## Before

The finder reports 10 markers in `mock-paper/`: `Mark-inline` ×3,
`MarkEdit-edits` ×3, `MarkEnv-text`, `MarkEnv-math`, `MarkEnv-fig`, and
`markroles-bib` ×1.

## Pass criteria

All must hold for the run copy `R/mock-paper`:

1. The finder reports `0 marker(s) found.` and exits `0`.
2. These print nothing:

   ```bash
   git diff --no-index --ignore-all-space --ignore-blank-lines .agents/tests/approve-changes-markings/expected/sections/body.tex "$R/mock-paper/sections/body.tex"
   git diff --no-index --ignore-all-space --ignore-blank-lines .agents/tests/approve-changes-markings/expected/references.bib "$R/mock-paper/references.bib"
   ```

3. `\Mark{missing}{TODO: keep this missing marker.}` and
   `markroles = {missing}` are still present.
4. The agent reports a successful full build. Its report gives the scope as
   global and separate counts: 3 `changes` additions (one of them a heading),
   3 `edits` replacements, 3 `MarkEnv` environments, and 1 bibliography
   field. Its "Rule violations" line says none.

## What each case tests

| Source | Expected | Rule |
| --- | --- | --- |
| heading `Mark{changes}[heading]{Body}` | `Body` | heading kind |
| `MarkEdit{edits}{slow}{fast}` | `fast` | keep the new argument |
| `Mark{changes}[math]{x^2}` | `$x^2$` | math kind restores math mode |
| `MarkEdit{edits}{inner old}{inner new}` mid-sentence | `Outer text with inner new inside.` | surrounding text untouched |
| `MarkEdit{edits}{ and loses a clause}{}` | nothing | empty new argument deletes |
| `MarkEnv{changes}[math]` | `equation` environment | math block keeps display mode |
| `MarkEnv{changes}[figure]` inside `figure` | inner content only | figure kind |
| `markroles = {changes}` | field removed | approved citation |
| `markroles = {missing}` | unchanged | never touch `missing` |
| `Mark{missing}{…}` | unchanged | never touch `missing` |

The mock paper holds no nested markers and no multi-role `markroles` field:
both are forbidden by `publications/AGENTS.md`.
