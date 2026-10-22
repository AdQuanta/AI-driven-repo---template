# citation-audit fixture

A self-contained test of `citation-audit`, `citation-reader`, and
`citation-checker`: a mock manuscript, a small knowledge base of fictional
papers, and the LaTeX sources those papers were built from. Everything here is
**fictional test material**.

## Run

```bash
R=_agents_outputs/_agents_dump/citation-audit-fixture
rm -rf "$R" && mkdir -p "$R" && cp -r .agents/tests/citation-audit/mock-paper .agents/tests/citation-audit/knowledge-base "$R/"
```

The copy holds only `mock-paper/` and `knowledge-base/`. `ANSWER_KEY.md` and
`paper-sources/` stay out of it, because the agents under test must not be
able to read them.

Then dispatch `citation-audit` with these three repository-relative paths,
exactly as listed. The run line then contains the relative paper directory.

- paper directory: `_agents_outputs/_agents_dump/citation-audit-fixture/mock-paper`
- knowledge-base root: `_agents_outputs/_agents_dump/citation-audit-fixture/knowledge-base`
- output root: `_agents_outputs/_agents_dump/citation-audit-fixture/output`

Claude Code may refuse the conductor's write of `report.md`. If the
conductor's reply contains `REPORT-PATH:`, whoever runs the fixture, person
or agent, saves the text between `<!-- REPORT-BEGIN -->` and
`<!-- REPORT-END -->`, verbatim, to that path before checking the answer
key.

The non-default knowledge-base root makes the run isolated: nothing is fetched,
and every write stays inside the copy. Check the result against
`.agents/tests/citation-audit/ANSWER_KEY.md`, then delete the copy. Never run
the audit on this folder in place.

`mock-paper/config.tex` loads the markings module by a four-level relative
path, so the copy must stay at the depth shown above for the Mark edits the
audit applies to compile.

## Rebuilding a paper

The PDFs in `knowledge-base/` are built from `paper-sources/<key>.tex` with two
`pdflatex` passes. Each must keep at least 3,000 characters of text, or the
reader treats it as a stub. Build in a scratch folder so no auxiliary file
lands here:

```bash
B=_agents_outputs/_agents_dump/fixture-paper-build
rm -rf "$B" && mkdir -p "$B"
cp .agents/tests/citation-audit/paper-sources/<key>.tex "$B/"
(cd "$B" && pdflatex -interaction=nonstopmode -halt-on-error <key>.tex \
  && pdflatex -interaction=nonstopmode -halt-on-error <key>.tex)
pdftotext "$B/<key>.pdf" - | wc -m        # must be at least 3000
cp "$B/<key>.pdf" ".agents/tests/citation-audit/knowledge-base/water_networks/<key>/<Title>.pdf"
rm -rf "$B"
```

`fir2017valves` has no source: its "PDF" is the 9-byte text `%PDF-stub`, so
the reader treats it as a stub.
