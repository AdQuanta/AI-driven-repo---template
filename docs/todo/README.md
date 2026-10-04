# Project TODOs

This directory is the repository's single canonical queue for open work across
research, code, publications, documentation, and AI infrastructure.

Before reading, creating, or updating a dated TODO file, read this README. There
is no master checklist: inspect the dated Markdown files in this directory when
TODO work is requested. Consult `resolved/` only when historical context is
needed.

## File structure

- Keep one topic per file.
- Name files `YYYY-MM-DD-<kebab-case-topic>.md`.
- State near the top whether the file records decisions, open investigations,
  implementation work, or a handoff.
- Keep task descriptions concise, actionable, and aligned with the project
  vision.
- Keep active TODOs directly in `docs/todo/`; Only terminal TODOs belong in
  `docs/todo/resolved/`.

## Working with TODOs

- Load the instructions for every sector whose files will be changed:
  [research](../../research/AGENTS.md),
  [code](../../code/AGENTS.md), or
  [publications](../../publications/AGENTS.md).
- Use repository-relative Markdown links so references remain navigable.
- Use proper LaTeX delimiters for math: `$...$` inline and `$$...$$` for display
  math.

## Closing a TODO

- Begin every `**Status:**` value with one of: `Open`, `In progress`,
  `Blocked`, `Done`, or `Superseded`. A short explanatory clause may follow.
- Move completed TODO files to `docs/todo/resolved/` as historical evidence.
  Set a terminal status (`Done` or `Superseded`), add a short note that links
  to the work, decision, or evidence that closed it, and update relative links
  to and from the moved file.
- A file with outstanding work remains non-terminal (`Open`, `In progress`, or
  `Blocked`); record resolved sections in place rather than using a partial
  terminal status.

## Research claims

For citable research claims, follow the research-sector citation workflow:
invoke `find-papers`, ingest missing sources when necessary, and link to each
paper's `research/references/scientific_papers/**/summary.md` using its exact
`short_cite` value. Do not substitute bare citation keys or external URLs for
knowledge-base links.

## Missing guidance

If this README is missing or a required sector instruction cannot be found,
warn the user instead of inventing conventions.