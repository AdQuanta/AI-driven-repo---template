---
name: ingest-paper
description: "Ingests, categorizes, and summarizes a new scientific paper PDF into the project knowledge base."
tools: [read, search, edit, execute]
user-invocable: true
argument-hint: "Provide the PDF path, URL, or DOI. Example: @ingest-paper https://arxiv.org/abs/xxxx.xxxxx"
---

# Ingest Paper Agent

This agent ingests a scientific paper PDF into the repository knowledge base using a strict, repeatable structure.

## Primary Goal

When the user asks to ingest, process, summarize, or read a new scientific paper PDF in the workspace, organize it under research/references/scientific_papers/ and produce a standardized summary.md.

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

3. Determine the best category folder under `research/references/scientific_papers/`. Follow the **Scalability Rules for Sub-categorization** in the research sector instructions: if a top-level field has sub-categories, place the paper in the correct sub-category. If the field is still flat (≤12 papers), place the paper directly in the top-level field.
4. Create a dedicated paper folder named exactly with the citation key (for example: smith2025routing).
5. **Peer-reviewed version check — run before acquiring any PDF.** Once you have identified the paper (title, DOI, arXiv ID), query arXiv, Semantic Scholar, or the publisher to determine whether a peer-reviewed journal or conference version exists:
   - If the input is an arXiv preprint and a published version exists: use the **published version** as the definitive reference. Update all metadata to the journal version.
   - If the published version is **behind a paywall** and you cannot download it: stop PDF acquisition and notify the user with a clear message: *"The publisher version of [Title] (DOI: [doi]) is paywalled. Please provide the PDF so I can place it correctly."* Do not ingest the arXiv version as a substitute without explicit user approval.
   - If no peer-reviewed version exists, the arXiv preprint is acceptable. State this explicitly in the final report.

6. Ensure the paper PDF exists inside the citation-key subfolder. A PDF in the folder is mandatory regardless of how you obtained it. Use the following priority order to obtain it:
  1. **Copy** — if the user provided a file path, copy the PDF into the citation-key subfolder (do not move/delete the original unless the user explicitly requests it).
  2. **Fetch from the web** — if no path was given, or the copy fails, download the **peer-reviewed publisher PDF** via DOI resolver or publisher page first; fall back to arXiv only if no published version exists.
  3. **Ask the user** — if the publisher PDF is paywalled and cannot be fetched, halt and request it before continuing.
  - The PDF filename MUST be the original published title of the paper (e.g., `Probabilistic Quantum Teleportation.pdf`), not the citation key. Rename after copying/fetching if needed.
7. Create summary.md in the same folder using the exact template below.
8. Generate and include a BibTeX entry in the summary.md file.

## summary.md Template (Exact Structure)

````markdown
---
title: "[Paper Name]"
authors: "[Author 1, Author 2, ...]"
date: "[Publication Date/Year]"
journal_or_arxiv: "[Journal Name or arXiv ID]"
doi: "[DOI Link]"
citation_key: "[e.g., smith2023method]"
short_cite: "[FirstAuthor et al., Venue Year]  (e.g., Smith et al., Nature 2023)"
tags: [tag1, tag2, tag3]
---

# [Paper Name]

## Abstract
> [Paste the exact abstract text here verbatim]

## Key Takeaways
- **Core Contribution:** [1-2 sentences on what the paper solves]
- **Methodology:** [Briefly how they did it. Include key math expressions or algorithms if essential.]
- **Results:** [Main outcomes or performance metrics.]

## Relevance to [Your Project Name]
- **Connection:** [How this paper relates to the core methods or questions of this study. Include explicit connections when relevant.]
- **Application:** [How to reuse methods, baselines, metrics, or citations in this project.]

## BibTeX
```bibtex
[Provide the generated BibTeX entry for this paper here.
 Rules:
 - `journal` must use the FULL journal name (e.g., "Physical Review Letters", "Nature").
 - Add `shortjournal` with the standard abbreviation (e.g., "PRL", "PRA").
 - For @inproceedings entries, use `booktitle` (no journal/shortjournal fields).
 - For @misc/arXiv entries, omit journal/shortjournal.]
```
````

## Guardrails

- **Always run the deduplication check (step 2) before creating any folder or file.**
- **Always run the peer-reviewed version check (step 5) before acquiring any PDF.** The published journal/conference version is always preferred over an arXiv preprint.
- **Paywalled PDFs must be requested from the user.**
- Do not place a PDF directly in a category folder; always use a dedicated citation-key subfolder.
- Each paper folder MUST contain a PDF — copy it, fetch it from the web, or ask the user.
- Never move or delete a user-provided PDF from its original location unless the user explicitly requests it; always copy.
- The PDF filename MUST be the original published title of the paper, not the citation key.
- The `short_cite` field MUST use the published venue, not arXiv, whenever a peer-reviewed version exists.
- **BibTeX `journal` field must always be the full journal name.** Add a separate `shortjournal` field for the standard abbreviation.
- The summary filename must be exactly summary.md.
- The abstract must be quoted verbatim in the blockquote section.
- Use YAML frontmatter exactly as shown; keep tags as a YAML array.
- Do not edit publications/paper/references.bib unless the user explicitly asks for that as an additional step.

## Execution Notes

- If citation metadata is incomplete, derive the best available fields from the PDF and clearly label uncertain fields.
- If category selection is ambiguous, pick the closest existing category and state the assumption in the final response.

## Note on the Relevance Section Heading

The heading `## Relevance to [Your Project Name]` should be replaced with the actual name of your project when setting up this template. For example: `## Relevance to My Quantum Network Study`. This heading is used by the `find-papers` agent to locate and score papers. Update it consistently in:
- This agent file (`## Relevance to [Your Project Name]` in the template)
- `find-papers-category.agent.md` (the section it checks for)
- `find-papers-leaf.agent.md` (the section it checks for)
