# Knowledge-base tools

Tools that maintain the literature knowledge base in `research/references/`.
They live beside the knowledge base, not in `code/`, which holds the project's
research code. Nothing here imports from `code/`.

| Entrypoint | What it does | Used by |
| --- | --- | --- |
| `generate_literature_tag_index.py` | Validates summary tags and regenerates [`../indexes/tags/`](../indexes/tags/) | `ingest-paper` agent |
| `gather_summaries.py` | Collects every `summary.md` into one corpus at `_agents_outputs/_agents_dump/find-papers-corpus.md` | `find-papers` agent |

Run them from the repository root with the project's Python environment:

```text
python research/references/src/generate_literature_tag_index.py
python research/references/src/generate_literature_tag_index.py --check
python research/references/src/generate_literature_tag_index.py --accept-new-tags
python research/references/src/gather_summaries.py
```

Modes, exit codes, and safety rules for the tag index are in the
[operator README](../indexes/tags/README.md).

## Layout

- `kb_paths.py` — finds the repository root (a `.git` directory, or a `.git`
  file in a linked worktree; otherwise the fixed location of this folder) and
  the knowledge-base paths.
- `literature_tags/` — tag parsing, validation, rendering, and safe writing.
- `find_papers/` — summary gathering and corpus rendering.
- `tests/` — the test suite.

## Tests

```text
python -m pytest research/references/src -q
```

`pytest.ini` puts this folder on the import path, so tests need no `sys.path`
edits.
