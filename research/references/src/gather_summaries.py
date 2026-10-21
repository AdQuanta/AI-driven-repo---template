"""Runnable entrypoint: gather all paper summaries into a corpus file.

Writes ``_agents_outputs/_agents_dump/find-papers-corpus.md`` and prints a
one-line summary (corpus path + paper/warning counts) for the find-papers
agent to read. All logic lives in ``find_papers/gather.py`` beside this file.
"""

import kb_paths
from find_papers.gather import gather_summaries, render_corpus

CORPUS_FILENAME = "find-papers-corpus.md"


def main() -> None:
    repo = kb_paths.repo_root()
    corpus_path = kb_paths.agents_dump_dir() / CORPUS_FILENAME
    result = gather_summaries(kb_paths.papers_root(), repo)
    corpus = render_corpus(result)

    corpus_path.parent.mkdir(parents=True, exist_ok=True)
    corpus_path.write_text(corpus, encoding="utf-8")

    rel = corpus_path.resolve().relative_to(repo.resolve()).as_posix()
    print(
        f"find-papers corpus written to {rel} — "
        f"{len(result.records)} papers, {len(result.warnings)} warnings."
    )


if __name__ == "__main__":
    main()
