"""Runnable entrypoint: gather all paper summaries into a corpus file.

Writes ``_agents_outputs/_agents_dump/find-papers-corpus.md`` and prints a
one-line summary (corpus path + paper/warning counts) for the find-papers
agent to read. All logic lives in ``code/src/find_papers/gather.py``.
"""

import _path_setup  # noqa: F401  (adds code/src to sys.path)

import code_paths
from find_papers.gather import gather_summaries, render_corpus

PAPERS_ROOT = code_paths.repo / "research" / "references" / "scientific_papers"
CORPUS_PATH = (
    code_paths.repo / "_agents_outputs" / "_agents_dump" / "find-papers-corpus.md"
)


def main() -> None:
    result = gather_summaries(PAPERS_ROOT, code_paths.repo)
    corpus = render_corpus(result)

    CORPUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CORPUS_PATH.write_text(corpus, encoding="utf-8")

    rel = CORPUS_PATH.resolve().relative_to(code_paths.repo.resolve()).as_posix()
    print(
        f"find-papers corpus written to {rel} — "
        f"{len(result.records)} papers, {len(result.warnings)} warnings."
    )


if __name__ == "__main__":
    main()
