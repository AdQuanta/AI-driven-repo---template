# citation-audit fixture: answer key

FICTIONAL TEST MATERIAL: every paper, author, and venue in this fixture is
invented. See `README.md` for how to run it.

In the paths below, `R` is the run copy
`_agents_outputs/_agents_dump/citation-audit-fixture`, `<date>` is the run
date (`YYYY-MM-DD`), and the run line is
`Audit run: <date> _agents_outputs/_agents_dump/citation-audit-fixture/mock-paper`
(the paper directory exactly as it was given to the conductor). The working
area is `R/output/_agents_dump/citation-audit/<date>/` and the report is
`R/output/citation-audit/<date>/report.md`. `KB` is
`R/knowledge-base/water_networks`.

## Before

Record `git status --porcelain` before the run. The run must not change it.

## Units

The section files are under `mock-paper/sections/`.

| # | Unit id | Key | `file:line` | Expected verdict | Expected severity | Exercises |
|---|---|---|---|---|---|---|
| 1 | `alder2021leakage__01_introduction__L6` | `alder2021leakage` | `01_introduction.tex:6` | `supported` | `none` or `minor` | plain prose cite |
| 2 | `birch2019pressure__01_introduction__L9` | `birch2019pressure` | `01_introduction.tex:9` | `supported` | `none` or `minor` | multi-cite split |
| 3 | `cedar2020smartmeters__01_introduction__L9` | `cedar2020smartmeters` | `01_introduction.tex:9` | `supported` | `none` or `minor` | multi-cite split |
| 4 | `dogwood2018chlorine__01_introduction__L12` | `dogwood2018chlorine` | `01_introduction.tex:12` | `wrong-paper` | `critical` | planted error; better-paper search proposes `elm2022coldbursts`, grounded in its `summary.md` |
| 5 | `fir2017valves__01_introduction__L15` | `fir2017valves` | `01_introduction.tex:15` | `supported`, lower confidence (`Summary-only (stub PDF): yes`) | `none` or `minor`, never `critical` | stub PDF |
| 6 | `hazel2019sensors__01_introduction__L18` | `hazel2019sensors` | `01_introduction.tex:18` | `supported` | `none` or `minor` | key drift to `hazel2020sensors` |
| 7 | `ivy2021tariffs__01_introduction__L20` | `ivy2021tariffs` | `01_introduction.tex:20` | `skipped (no inventory)` | n/a | missing paper |
| 8 | `alder2021leakage__02_related_work__L13` | `alder2021leakage` | `02_related_work.tex:13` | `supported` | `none` or `minor` | table citation; context includes the caption, the column header, and the row label |
| — | (nocite) | `gum2023review` | `main.tex:8` | `skipped (no textual context)` | n/a | `\nocite`; no reader or checker |

Two keys are deliberately never read:

- `elm2022coldbursts` is in the `.bib` and the knowledge base but is never
  cited. Only the unit-4 checker looks at it, through its `summary.md`.
- `gum2023review` is `\nocite` only and has no knowledge-base folder.

### Why each verdict holds

- **Units 2 and 3.** The sentence makes one claim per key: lowering
  night-time pressure cuts bursts (`birch2019pressure`, Section 3.1: burst
  frequency fell by 28%), and watching district inlet flows flags new leaks
  within a day (`cedar2020smartmeters`, Section 3.1: flagged within 24 hours
  in 9 of 10 trials). Under the multi-cite rule each key is judged on its own
  clause, so both are `supported`. The sentence claims no loss reduction for
  inlet monitoring, which `cedar2020smartmeters` argues but does not measure.
- **Unit 4.** `dogwood2018chlorine` measures chlorine decay in storage tanks
  (Results, Section 3). Its Limitations (Section 4) state that it does not
  examine pipe bursts, temperature effects on pipes, or cold weather. The
  claim, that burst rates in iron mains more than double below 2 °C soil
  temperature, is the Section 3.1 result of `elm2022coldbursts` (2.4 times
  higher), which is in the `.bib`.
- **Unit 5.** `fir2017valves`'s PDF is the 9-byte text `%PDF-stub`, so the
  reader works from `summary.md`. The summary states both halves of the claim:
  seized valves delay isolation for repair, and exercising every two years cut
  seized valves from 18% to 6%. The summary supports the claim, so the stub
  makes the unit lower confidence, not `unsupported`.
- **Unit 6.** The `.bib` entry `hazel2019sensors` has the title of the paper in
  the folder `hazel2020sensors`, so the reader resolves to that folder by
  title. The folder name differs from the cited key.
- **Unit 7.** No `summary.md` under the knowledge-base root has the title
  *Tiered Tariffs and Peak Demand*.

## Pass criteria

All must hold.

1. **Ledger.** `ledger.md` in the working area has exactly the 8 units above
   plus 1 `\nocite` row for `gum2023review`, marked
   `skipped (no textual context)`. The `file:line` values match the table.
   Flags: `fir2017valves` has `stub`; `hazel2019sensors` has `drift`, with
   resolved folder `KB/hazel2020sensors`; `ivy2021tariffs` has `missing`. No
   key has `no-bib-entry`. Every unit is `done` or `skipped`; none is
   `pending`, `failed`, `reader-failed`, or `checker-failed`.
2. **Planted error.** `units/dogwood2018chlorine__01_introduction__L12.md` has
   `verdict: wrong-paper` and `severity: critical`. Its `Better paper` line
   names `elm2022coldbursts` and quotes its `summary.md` (the 2.4-times,
   below-2 °C result), and its `Proposed edit` swaps the key to
   `elm2022coldbursts`. The swap is applied in
   `R/mock-paper/sections/01_introduction.tex` in the only accepted form:
   `\MarkEdit{edits}{\cite{dogwood2018chlorine}}{\cite{elm2022coldbursts}}`.
3. **Stub.** `KB/fir2017valves/fit.md` carries the `⚠ STUB-PDF` caveat at the
   top of `## Verified Results`, and its bullets are tagged `[SUMMARY-ONLY]`.
   `units/fir2017valves__01_introduction__L15.md` has `verdict: supported`,
   severity `none` or `minor` (never `critical`),
   `Summary-only (stub PDF): yes`, and `Used escape-hatch PDF read: no`.
4. **Key drift.** `KB/hazel2020sensors/fit.md` has a
   `### Targeted (hazel2019sensors)` block and a key-drift note naming
   `hazel2019sensors`. No `KB/hazel2019sensors/` folder exists.
5. **Missing paper.** The working area holds `missing/ivy2021tariffs.md`, with
   `Status: missing`, the run line,
   `Fetch policy: no-fetch (non-default knowledge-base root)`, and
   `<!-- AUDIT-READER-COMPLETE -->`. The unit is `skipped (no inventory)` and
   has no unit file. No `KB/ivy2021tariffs/` folder exists.
6. **Notes files.** `fit.md` exists in exactly six folders: `alder2021leakage`,
   `birch2019pressure`, `cedar2020smartmeters`, `dogwood2018chlorine`,
   `fir2017valves`, and `hazel2020sensors`. Each carries, inside
   `## Verified Results`, the run line and
   `Fetch policy: no-fetch (non-default knowledge-base root)`, ends that
   section with `<!-- AUDIT-READER-COMPLETE -->`, and has one `## Fit @` section
   per unit after it (two for `alder2021leakage`).
7. **Report.** `report.md` exists as a file at
   `<output root>/citation-audit/<date>/report.md`, that is
   `R/output/citation-audit/<date>/report.md`, with the required sections in
   order: critical errors, Knowledge-base defects, minor issues, and routine
   confirmations. Either the conductor wrote it, or the conductor returned it
   with a `REPORT-PATH:` line and the `<!-- REPORT-BEGIN -->` and
   `<!-- REPORT-END -->` markers and the runner saved it verbatim to that
   path. A report returned without `REPORT-PATH:` and the markers fails this
   criterion. The report states both roots. Its critical errors list unit 4.
   Its "Knowledge-base defects" section lists `fir2017valves` (stub),
   `hazel2019sensors` → `hazel2020sensors` (key drift), and `ivy2021tariffs`
   (missing), each with its key and folder. Its minor issues list unit 5 as
   summary-only. No key is reported as `no-bib-entry`.
8. **Never read.** `elm2022coldbursts` and `gum2023review` get no reader or
   checker: no `fit.md`, no `missing/` record, and no unit file for either key.
   `elm2022coldbursts` also gets no brief.
9. **Table context.** `briefs/alder2021leakage.md` gives unit 8 the caption
   (*Median leak-localization error by pipe material.*), the column header
   (`Reference`), and the row label (`Cast iron`), not just the cell.
10. **No fetching.** The copy's `knowledge-base/` has no new folder and no new
    PDF.
11. **Edited copy compiles.** `R/mock-paper/`, with the audit's Mark edits
    applied, builds without error using the full sequence from
    `docs/agent-guidance/vscode-latex-environment.md` (pdflatex, biber,
    pdflatex, pdflatex), with every intermediate in `.latex_build/`:

    ```bash
    cd _agents_outputs/_agents_dump/citation-audit-fixture/mock-paper && mkdir -p .latex_build \
      && pdflatex -synctex=1 -interaction=nonstopmode -file-line-error -halt-on-error --aux-directory=.latex_build main.tex \
      && biber --input-directory=.latex_build --output-directory=.latex_build main \
      && pdflatex -synctex=1 -interaction=nonstopmode -file-line-error -halt-on-error --aux-directory=.latex_build main.tex \
      && pdflatex -synctex=1 -interaction=nonstopmode -file-line-error -halt-on-error --aux-directory=.latex_build main.tex \
      && echo BUILD-OK
    ```

    `mock-paper/config.tex` loads the markings module by the relative path
    `../../../../publications/modules/markings/`, which resolves to the
    repository root from both `.agents/tests/citation-audit/mock-paper/` and
    the run copy. Build only in the run copy, never in this folder.
12. **No outside writes.** `git status --porcelain` matches the record made
    before the run.
13. **Supported units.** Units 1, 2, 3, 5, 6, and 8 (`alder2021leakage` ×2,
    `birch2019pressure`, `cedar2020smartmeters`, `fir2017valves`, and
    `hazel2019sensors`) have `verdict: supported` and severity `none` or
    `minor`, never `wrong-paper` or `unsupported`. A small wording fix proposed
    for one of them and applied as a `\Mark`/`\MarkEdit` edit is allowed.
    Unit 4 (`dogwood2018chlorine`) stays `wrong-paper`/`critical`, with the
    swap to `elm2022coldbursts` (criterion 2).

## Expected but not required

Only unit 4 needs an edit. A small wording fix on a supported unit is allowed
(criterion 13); any other proposed edit is worth investigating but does not
fail the run.
