---
name: ingest-paper
description: Ingests, categorizes, and summarizes a new scientific paper PDF into
  the project knowledge base.
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
argument-hint: Provide the PDF path and optional target category.
---

# Ingest Paper Agent

This agent ingests a scientific paper PDF into the repository knowledge base using a strict, repeatable structure.

## Primary Goal

When the user asks to ingest, process, summarize, or read a new scientific paper PDF in the workspace, organize it under research/references/scientific_papers/ and produce a standardized summary.md.

Completion requires both artifacts in the destination folder: `summary.md` and a correctly named PDF.

## Invocation Modes

- **Default mode (metadata-first):** Follow the full workflow, including peer-reviewed version checks and web fetch fallback when needed.
- **User-provided-local-PDF mode:** If the user explicitly says to use already provided local files (for example, "do not fetch", "do not use arXiv", "papers are already in input folder"), then:
  - Skip web discovery and skip PDF fetching.
  - Use the provided local files as the source of truth for PDF placement.
  - Still perform deduplication, categorization, citation-key foldering, and summary generation/fixing.
  - If metadata fields are uncertain without web lookup, mark uncertainty in the final report.

## When To Use

- User asks to ingest a specific PDF.
- User asks to summarize a newly downloaded paper and file it in the literature folders.

## When Not To Use

- User asks for a general concept explanation without a specific paper file.
- User asks to summarize project code or paper drafts rather than an external PDF.

## Required Workflow

1. Extract title, authors, abstract, publication venue/year, and identifier metadata from the PDF.

2. **Deduplication check — run before creating anything.** Read the YAML frontmatter of every `summary.md` under `research/references/scientific_papers/` (all categories, all subfolders). A paper is considered already ingested if **any** of the following match the paper being ingested (case-insensitive):
   - `doi` field is identical and non-empty, or
   - `title` field is identical, or
   - `citation_key` matches the key you would assign.

   **If a match is found:** Do not create a new folder. Instead, switch to **assert-and-fix mode**:
   - Report which folder the match was found in.
   - Verify the existing folder has a correctly named PDF (original published title); fix the filename if wrong.
   - Verify `summary.md` contains all required sections (Abstract, Key Takeaways, Relevance, BibTeX); fill in any missing sections.
   - Verify the YAML frontmatter is complete; patch any missing or wrong fields.
   - Report a summary of what was checked and what (if anything) was corrected.
   - **Stop here** — do not proceed to steps 3–6.

   **If no match is found:** Continue to step 3.

3. Determine the best category folder under `research/references/scientific_papers/`. Follow the **Scalability Rules for Sub-categorization** in the research sector instructions: if a top-level field has sub-categories, place the paper in the correct sub-category (e.g., `<field>/<subfield>/`). If the field is still flat (≤12 papers), place the paper directly in the top-level field. If no category fits yet (a fresh project starts with none), create a new top-level field folder and add it to the taxonomy in `research/AGENTS.md`.
4. Create a dedicated paper folder named exactly with the citation key (for example: smith2025example).
5. **Peer-reviewed version check — run before acquiring any PDF.** Once you have identified the paper (title, DOI, arXiv ID), query arXiv, Semantic Scholar, or the publisher to determine whether a peer-reviewed journal or conference version exists:
   - If the input is an arXiv preprint and a published version exists: use the **published version** as the definitive reference. Update all metadata (title, journal_or_arxiv, DOI, date, BibTeX) to the journal version. The arXiv version may be cited in the BibTeX `eprint` field for provenance, but it must not be the primary record.
   - If the published version is **behind a paywall** and you cannot download it: stop PDF acquisition and notify the user with a clear message: *"The publisher version of [Title] (DOI: [doi]) is paywalled. Please provide the PDF so I can place it correctly."* Do not ingest the arXiv version as a substitute without explicit user approval.
   - If no peer-reviewed version exists, the arXiv preprint is acceptable. State this explicitly in the final report.

6. Ensure the paper PDF exists inside the citation-key subfolder. A PDF in the folder is mandatory regardless of how you obtained it. Use the following priority order to obtain it:
  1. **Copy** — if the user provided a file path, copy the PDF into the citation-key subfolder (do not move/delete the original unless the user explicitly requests it).
  2. **Fetch from the web** — if no path was given, or the copy fails, download the **peer-reviewed publisher PDF** via DOI resolver or publisher page first; fall back to arXiv only if no published version exists.
  3. **Ask the user** — if the publisher PDF is paywalled and cannot be fetched, halt and request it before continuing. Do not proceed with an arXiv substitute without the user's explicit approval.
  - Exception: if the PDF is already inside the correct citation-key subfolder with the correct filename, verify its presence and skip copy/fetch.
  - The PDF filename MUST be the original published title of the paper (e.g., `Probabilistic Quantum Teleportation.pdf`), not the citation key. Rename after copying/fetching if needed.
7. Create summary.md in the same folder using the exact template below. **Do not use the `Write` tool for this file — it will be refused.** Follow "How to write `summary.md` (required method)" under Execution Notes.
8. Generate and include a BibTeX entry in the summary.md file.
9. **Mandatory destination verification before completion.** For each processed paper, verify and report:
  - destination folder path
  - `summary.md` exists
  - PDF exists with final filename
  - PDF size in bytes (must be > 0)
  - source path used for the copy (if applicable)

  If any verification item fails, do not report success. Remediate first, then re-verify.
10. **Mandatory final report format.** End with a table containing one row per paper:
  - title
  - citation_key
  - category folder
  - source PDF path
  - destination PDF path
  - `summary.md` exists (true/false)
  - PDF exists (true/false)
  - PDF size bytes
  - status (`ingested`, `duplicate-fixed`, or `blocked`)

## summary.md Template (Exact Structure)

````markdown
---
title: "[Paper Name]"
authors: "[Author 1, Author 2, ...]"
date: "[Publication Date/Year]"
journal_or_arxiv: "[Journal Name or arXiv ID]"
doi: "[DOI Link]"
citation_key: "[e.g., smith2023measurement]"
short_cite: "[FirstAuthor et al., Venue Year]  (e.g., Smith et al., Nature 2023 — or Smith et al., arXiv 2023 if no journal version exists)"
tags: [topic_a, topic_b, topic_c]
---

# [Paper Name]

## Abstract
> [Paste the exact abstract text here verbatim]

## Key Takeaways
- **Core Contribution:** [1-2 sentences on what the paper solves]
- **Methodology:** [Briefly how they did it. Include key math expressions or algorithms if essential.]
- **Results:** [Main outcomes or performance metrics. Use relevant expressions if they define metrics.]

## Relevance to This Project
- **Connection:** [How this relates to the study described in the root `AGENTS.md` ("What Is This Study About?"). Include explicit math connections when relevant.]
- **Application:** [How to reuse methods, baselines, metrics, or citations in this project.]

## BibTeX
```bibtex
[Provide the generated BibTeX entry for this paper here.
 Rules:
 - `journal` must use the FULL journal name (e.g., "Physical Review Letters", "Nature").
 - Add `shortjournal` with the standard abbreviation (e.g., "PRL", "Nat. Phys.").
 - For @inproceedings entries, use `booktitle` (no journal/shortjournal fields).
 - For @misc/arXiv entries, omit journal/shortjournal.]
```
````

## Guardrails

- **Always run the deduplication check (step 2) before creating any folder or file.** A duplicate is detected by matching DOI, title, or derived citation key against existing YAML frontmatter.
- **Always run the peer-reviewed version check (step 5) before acquiring any PDF.** The published journal/conference version is always preferred over an arXiv preprint. Never store an arXiv PDF when a published version exists, unless the user explicitly approves it.
- **Paywalled PDFs must be requested from the user.** If the publisher PDF cannot be fetched openly, halt and ask — do not silently substitute the arXiv version.
- Do not place a PDF directly in a category folder; always use a dedicated citation-key subfolder.
- Each paper folder MUST contain a PDF — copy it, fetch it from the web, or ask the user; a folder without a PDF is incomplete and must be remediated before proceeding.
- Never claim completion based only on intended actions. Completion is allowed only after destination verification (existence and size checks) has been reported.
- Never move or delete a user-provided PDF from its original location unless the user explicitly requests it; always copy.
- If the user explicitly requests local-only ingestion, do not perform any web fetches or arXiv/publisher lookups for PDF acquisition.
- The PDF filename MUST be the original published title of the paper (e.g., `Probabilistic Quantum Teleportation.pdf`), not the citation key. Rename after placing in the folder if needed.
- The `short_cite` field MUST use the published venue (journal abbreviation or conference acronym), not arXiv, whenever a peer-reviewed version exists.
- **BibTeX `journal` field must always be the full journal name** (e.g., "Physical Review Letters", not "Phys. Rev. Lett." and not "PRL"). Add a separate `shortjournal` field for the standard abbreviation: use the
  venue's ISO 4 abbreviation, or its conventional short name when one is in
  common use. Examples:
  - Physical Review Letters → `shortjournal = {PRL}`
  - Nature Physics → `shortjournal = {Nat. Phys.}`
  - Nature Communications → `shortjournal = {Nat. Commun.}`
  - Science → `shortjournal = {Science}`
  - IEEE Transactions on Communications → `shortjournal = {IEEE Trans. Commun.}`
  - IEEE/ACM Transactions on Networking → `shortjournal = {IEEE/ACM Trans. Netw.}`
  - IEEE Access → `shortjournal = {IEEE Access}`
- For `@inproceedings` entries, use `booktitle` (no `journal` or `shortjournal` needed).
- The summary filename must be exactly summary.md.
- The abstract must be quoted verbatim in the blockquote section.
- Use YAML frontmatter exactly as shown; keep tags as a YAML array.
- Do not edit any `publications/<paper-dir>/references.bib` unless the user explicitly asks for that as an additional step.

## Execution Notes

- If citation metadata is incomplete, derive the best available fields from the PDF and clearly label uncertain fields.
- If category selection is ambiguous, pick the closest existing category and state the assumption in the final response.

### How to write `summary.md` (required method)

**Do not use the `Write`/`edit` tool for `summary.md`.** A harness heuristic blocks subagents from writing files whose names look like agent reports (`summary.md`, `report.md`, `findings.md`) to stop subagents dumping reports to disk instead of returning text. Here that is a false positive — `summary.md` is this agent's required knowledge-base artifact, not a report — but the block still fires, and improvised workarounds have produced files with inconsistent encodings (stray UTF-8 BOMs, mixed line endings) that differ from their sibling summaries.

Write the file with Python instead. This is the only sanctioned method:

1. Write the summary body to a scratchpad file named **`<citation_key>-body.md`**. The name must contain the citation key. Do not use a generic name such as `paper-body.md` or `summary_payload.txt` — the scratchpad is shared, concurrent ingest runs collide on generic names, and a collision silently copies another paper's summary into your destination.
2. Copy it into the destination with an explicit encoding, using the **`Bash` tool** (PowerShell strips the inner double quotes from this command) and the **absolute** path to the repository virtual environment (`<workspace-root>` is the output of `git rev-parse --show-toplevel`) — the working directory is not guaranteed between calls, so `.venv\Scripts\python.exe` alone will not resolve:

```
<workspace-root>/.venv/Scripts/python.exe -c "import pathlib,sys; src=pathlib.Path(sys.argv[1]); dst=pathlib.Path(sys.argv[2]); dst.parent.mkdir(parents=True, exist_ok=True); open(dst,'w',encoding='utf-8',newline='\r\n').write(src.read_text(encoding='utf-8-sig'))" <scratchpad>/<citation_key>-body.md <destination>/summary.md
```

`encoding='utf-8-sig'` on read strips any BOM the scratchpad file picked up; `encoding='utf-8'` with `newline='\r\n'` on write matches the existing summaries in the knowledge base. Use the `open(...)` form shown, not `Path.write_text(..., newline=...)`, which requires Python 3.10+.

3. Delete the scratchpad file, then verify the destination. **Read the written file back from disk** and confirm all of:
   - the file exists and its size is greater than zero;
   - its first byte is `-` (the YAML frontmatter delimiter, i.e. no BOM);
   - line endings are CRLF;
   - **its `citation_key` frontmatter field matches the paper you are ingesting** — a copy of the wrong body file passes every other check on this list, so this is the check that catches it;
   - all five required sections are present.

If step 2 fails, report the exact error and status `blocked`. Do not fall back to `Write`, and do not fall back to shell heredocs — heredoc quoting is unreliable for this content because summaries contain backticks, `$` math, and quotes.
