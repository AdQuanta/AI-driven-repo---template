"""find_papers — tooling for the project paper-search agent.

The :mod:`find_papers.gather` module collects every ``summary.md`` in the
scientific-paper knowledge base into a single corpus document that the
``find-papers`` agent reads and scores in one pass.
"""

from find_papers.gather import (
    GatherResult,
    PaperRecord,
    extract_section,
    gather_summaries,
    parse_frontmatter,
    render_corpus,
)

__all__ = [
    "GatherResult",
    "PaperRecord",
    "extract_section",
    "gather_summaries",
    "parse_frontmatter",
    "render_corpus",
]
