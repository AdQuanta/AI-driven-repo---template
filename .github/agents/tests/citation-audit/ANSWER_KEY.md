# Citation-Audit Test — Answer Key

A controlled mock manuscript with **two planted errors**, **two stub-PDF papers**, a **multi-cite command**, a **table citation**, and a **nocite**, designed to exercise every hardened path in the citation-audit workflow.

## Mock paper

`mock-paper/` — two sections (`01_introduction.tex`, `02_related_work.tex`), seven citation instances plus one `\nocite`. The fixture's subject matter (quantum networking) is deliberately unrelated to any project built from this template; it is a test of the agent workflow, not of the project's science.

## Prerequisites in a fresh project

The fixture was authored against a knowledge base that already contained every cited paper. A project created from this template starts with an empty knowledge base, so:

- Each Reader will invoke `ingest-paper` for its cited paper before reading. That writes the seven cited papers under `research/references/scientific_papers/`. Run the test on a scratch branch or agent-created worktree and discard the ingested papers afterwards (or keep them if they are useful).
- The **stub-PDF tests (units 1 & 2) only apply if you plant stubs first**: before the run, ingest `wehner2018quantum` and `zukowski1993eventready`, then replace each PDF with a placeholder of a few bytes. Without planted stubs, units 1 & 2 should simply be `supported` from the full text.
- The audited directory name is `mock-paper` (no `paper---` prefix), so `<paper-slug>` is `mock-paper` and each inventory is named `fit__mock-paper.md`.

## How to run

Invoke `citation-audit` pointed at the mock paper directory:

```
@citation-audit .github/agents/tests/citation-audit/mock-paper
```

The agent should run to completion without manual nudges (hardening #2). Working files land in `_agents_outputs/_agents_dump/citation-audit/<date>/`.

---

## Expected enumeration

Phase 0 should find **7 work units** plus **1 nocite** (skipped):

| # | Unit ID | Key | File:Line | Claim attached to | Expected | Severity | Exercises |
|---|---------|-----|-----------|-------------------|----------|----------|-----------|
| 1 | `wehner2018quantum__01_introduction__L5` | wehner2018quantum | 01_introduction.tex:5 | Quantum networks unlock secure key exchange, sensing, modular computation | supported | none | Stub-PDF detection |
| 2 | `zukowski1993eventready__01_introduction__L9` | zukowski1993eventready | 01_introduction.tex:9 | Entanglement swapping = BSM projects two pairs onto a longer-range state | supported | none | Stub-PDF detection |
| 3 | `wootters1998entanglement__01_introduction__L12` | wootters1998entanglement | 01_introduction.tex:12 | Secret-key rate decays linearly in transmissivity; repeaterless ceiling | **wrong-paper** | **critical** | Planted error #1 |
| 4 | `pant2019routing__01_introduction__L16` | pant2019routing | 01_introduction.tex:16 | Multi-hop routing requires path-selection for swap outcomes | supported | none | Multi-cite splitting |
| 5 | `dahlberg2019linklayer__01_introduction__L16` | dahlberg2019linklayer | 01_introduction.tex:16 | Multi-hop routing requires link-layer coordination | supported | none | Multi-cite splitting |
| 6 | `bennett1993teleporting__01_introduction__L19` | bennett1993teleporting | 01_introduction.tex:19 | Swap ordering impacts end-to-end fidelity and success probability | **wrong-paper** | **critical** | Planted error #2 |
| 7 | `pirandola2019capacities__02_related_work__L10` | pirandola2019capacities | 02_related_work.tex:10 | Capacity bound for linear-chain architecture | supported | none | Table-citation context |
| — | _(nocite)_ | davis2025swapping | main.tex:7 | — | skipped | — | Nocite handling |

---

## Planted error #1 — unit 3

- **Cited paper:** `wootters1998entanglement` — _"Entanglement of Formation of an Arbitrary State of Two Qubits"_ — derives the concurrence formula for two-qubit entanglement. Says **nothing** about transmission rates, loss, transmissivity, or repeaterless bounds.
- **The claim** is the PLOB / rate-loss bound ($C = -\log_2(1-\eta)$, linear in transmissivity).
- **Correct paper:** `pirandola2017plob` — _"Fundamental Limits of Repeaterless Quantum Communications"_ — present in `references.bib`; ingested on demand if absent from the KB.
- **Expected Checker fix:** swap `\cite{wootters1998entanglement}` → `\cite{pirandola2017plob}`, applied as `\Mark{}`.

## Planted error #2 — unit 6

- **Cited paper:** `bennett1993teleporting` — _"Teleporting an Unknown Quantum State via Dual Classical and Einstein-Podolsky-Rosen Channels"_ — introduces quantum teleportation. Says **nothing** about swap ordering, scheduling, or its impact on network fidelity/success probability.
- **The claim** is about the impact of swap ordering on end-to-end performance.
- **Correct paper:** `chang2022swappingorder` — _"Order Matters: On the Impact of Swapping Order on an Entanglement Path in a Quantum Network"_ — present in `references.bib`; ingested on demand if absent from the KB.
- **Expected Checker fix:** swap `\cite{bennett1993teleporting}` → `\cite{chang2022swappingorder}`, applied as `\Mark{}`.

---

## Stub-PDF testing — units 1 & 2

- `wehner2018quantum` (~22 B) and `zukowski1993eventready` (~87 B) are placeholder stubs planted in the KB (see Prerequisites).
- The Reader must detect each as <100 KB and attempt `ingest-paper` re-fetch.
- The Reader may creatively find alternative full-text sources (e.g., Green-OA manuscripts, preprint mirrors). If it does, it should note the source in the inventory — this is a *better* outcome than summary-only fallback.
- If no full text is available (paywalled, no alternative), the Reader falls back to summary-only mode and adds a clearly visible caveat near the top of `## Verified Results`.
- **Expected:** each inventory either (a) documents the alternative source used, or (b) carries a visible caveat about summary-only evidence. The exact format is flexible — the Reader may use its own wording as long as the limitation is unmistakable.
- The report's "KB Defects Noted" section should flag both stubs for the user to supply real PDFs.

## Multi-cite testing — units 4 & 5

- `\cite{pant2019routing,dahlberg2019linklayer}` at line 16 is a single `\cite` command with two keys.
- Phase 0 must split it into **two separate units** sharing the same surrounding context paragraph.
- Both should be `supported`.

## Table-citation testing — unit 7

- `\cite{pirandola2019capacities}` sits inside a table cell (`02_related_work.tex:10`).
- The Conductor must extract construct-aware context: the **cell content** (`Linear chain & $-\log_2(1 - \eta^n)$`), the **column header** (`Reference`), the **row label** (`Linear chain`), and the **table caption** (`Capacity bounds for quantum network architectures.`).
- Should be `supported`.

## Nocite testing

- `\nocite{davis2025swapping}` in `main.tex:7` should be enumerated in the ledger but marked `skipped (no textual context)`.
- No Reader or Checker should be dispatched for it.

---

## Grading checklist

### Enumeration
- [ ] Ledger enumerates exactly 7 real units + 1 skipped nocite.
- [ ] Multi-cite at L16 produces 2 separate units (pant + dahlberg), not 1.

### Readers (7 dispatched)
- [ ] Each of the 7 cited papers gets one Reader; each writes `fit__mock-paper.md` with `## Verified Results` + sentinel.
- [ ] (If stubs planted) `wehner2018quantum` inventory carries `⚠ STUB-PDF` warning + `[SUMMARY-ONLY]` tags.
- [ ] (If stubs planted) `zukowski1993eventready` inventory carries `⚠ STUB-PDF` warning + `[SUMMARY-ONLY]` tags.
- [ ] `wootters1998entanglement` inventory explicitly records "does not establish" for rate/transmissivity/repeaterless claims.
- [ ] `bennett1993teleporting` inventory explicitly records "does not establish" for swap ordering/scheduling claims.

### Checkers (7 dispatched)
- [ ] Units 1, 2 → `supported` (note lower confidence from stub).
- [ ] Unit 3 → `wrong-paper`, severity `critical`, proposed swap to `pirandola2017plob`.
- [ ] Units 4, 5 → `supported`, grounded in named anchors.
- [ ] Unit 6 → `wrong-paper`, severity `critical`, proposed swap to `chang2022swappingorder`.
- [ ] Unit 7 → `supported`, grounding references the paper's capacity analysis. Context in the brief includes the table caption and column headers.

### Report & fixes
- [ ] `report.md` foregrounds units 3 and 6 as critical errors.
- [ ] All proposed `main.tex` edits are wrapped in `\Mark{}`.
- [ ] `pirandola2017plob` and `chang2022swappingorder` get **no** Reader/Checker — they surface only as Checker-proposed replacements. (They are in the bib but uncited.)
- [ ] `davis2025swapping` gets no Reader/Checker (nocite, skipped).

### Hardening-specific
- [ ] **Stub-PDF detection:** both stub inventories clearly flag the evidence limitation — either by documenting an alternative source or adding a visible summary-only caveat (hardening #1).
- [ ] **No parking:** Conductor ran to completion without stalling or requiring manual nudges (hardening #2).
- [ ] **Stall detection:** Conductor verified each sentinel immediately after sub-agent return; log shows foreground/blocking dispatch pattern (hardening #3).

---

## Scope guard

If the audit dispatches a Reader or Checker for `pirandola2017plob`, `chang2022swappingorder`, or `davis2025swapping`, that is a scope error — these keys are in the bib but not cited (or nocited), and should not receive workflow attention.
