"""Tests for the find-papers summary-gathering logic (code/src/find_papers)."""

from __future__ import annotations

from pathlib import Path
import sys

# Ensure code/src is importable when running pytest from code/.
CODE_SRC = Path(__file__).resolve().parents[1] / "src"
if str(CODE_SRC) not in sys.path:
    sys.path.insert(0, str(CODE_SRC))

from find_papers.gather import (  # noqa: E402
    PAPER_DELIMITER,
    RELEVANCE_HEADING,
    extract_section,
    gather_summaries,
    parse_frontmatter,
    render_corpus,
)


WELL_FORMED = """\
---
title: "A Fine Paper"
short_cite: "Doe, PRL 2020"
citation_key: "doe2020fine"
tags: [a, b, c]
---

# A Fine Paper

## Abstract
> The abstract text.

## Key Takeaways
- Did a thing.

## Relevance to This Project
- Provides the key insight our method builds on.

## BibTeX
```bibtex
@article{doe2020fine}
```
"""


def _make_paper(folder: Path, text: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "summary.md").write_text(text, encoding="utf-8")


def _make_tree(tmp_path: Path) -> tuple[Path, Path]:
    """Build a minimal knowledge-base tree; return (repo_root, papers_root)."""
    repo = tmp_path / "repo"
    papers = repo / "research" / "references" / "scientific_papers"
    papers.mkdir(parents=True)
    return repo, papers


# ── frontmatter & section parsing ────────────────────────────────────────────
def test_parse_frontmatter_reads_scalars_and_skips_lists() -> None:
    fm = parse_frontmatter(WELL_FORMED)
    assert fm["title"] == "A Fine Paper"
    assert fm["short_cite"] == "Doe, PRL 2020"
    assert fm["citation_key"] == "doe2020fine"
    assert "tags" not in fm  # list values are skipped


def test_parse_frontmatter_without_block_returns_empty() -> None:
    assert parse_frontmatter("# No frontmatter here") == {}


def test_extract_section_captures_until_next_heading() -> None:
    takeaways = extract_section(WELL_FORMED, "Key Takeaways")
    assert takeaways == "- Did a thing."
    assert extract_section(WELL_FORMED, "Nonexistent") is None


# ── gather pass ──────────────────────────────────────────────────────────────
def test_gather_collects_well_formed_paper(tmp_path: Path) -> None:
    repo, papers = _make_tree(tmp_path)
    _make_paper(papers / "field_a" / "subfield_b" / "doe2020fine", WELL_FORMED)

    result = gather_summaries(papers, repo)

    assert len(result.records) == 1
    assert result.warnings == []
    rec = result.records[0]
    assert rec.citation_key == "doe2020fine"
    assert rec.folder_rel == (
        "research/references/scientific_papers/field_a/subfield_b/doe2020fine"
    )
    # Link is relative to _agents_outputs/find-papers/ and ends with a slash.
    assert rec.link.startswith("../../research/references/scientific_papers/")
    assert rec.link.endswith("doe2020fine/")
    assert rec.title == "A Fine Paper"
    assert "key insight" in rec.relevance


def test_gather_on_empty_knowledge_base_returns_nothing(tmp_path: Path) -> None:
    repo, papers = _make_tree(tmp_path)

    result = gather_summaries(papers, repo)

    assert result.records == []
    assert result.warnings == []


def test_gather_warns_on_missing_summary(tmp_path: Path) -> None:
    repo, papers = _make_tree(tmp_path)
    # Leaf folder with no summary.md.
    (papers / "field_a" / "empty_paper").mkdir(parents=True)

    result = gather_summaries(papers, repo)

    assert result.records == []
    assert any("summary.md not found" in w for w in result.warnings)


def test_gather_tolerates_relevance_heading_variant(tmp_path: Path) -> None:
    repo, papers = _make_tree(tmp_path)
    variant = WELL_FORMED.replace(
        f"## {RELEVANCE_HEADING}",
        "## Relevance to the Project",
    )
    _make_paper(papers / "field_a" / "doe2020fine", variant)

    result = gather_summaries(papers, repo)

    assert result.warnings == []
    assert len(result.records) == 1
    assert "key insight" in result.records[0].relevance


def test_gather_warns_on_missing_section(tmp_path: Path) -> None:
    repo, papers = _make_tree(tmp_path)
    no_relevance = WELL_FORMED.replace(
        f"## {RELEVANCE_HEADING}\n- Provides the key insight our method builds on.\n",
        "",
    )
    _make_paper(papers / "field_a" / "broken", no_relevance)

    result = gather_summaries(papers, repo)

    assert result.records == []
    assert any("missing section" in w for w in result.warnings)


def test_gather_is_deterministically_ordered(tmp_path: Path) -> None:
    repo, papers = _make_tree(tmp_path)
    _make_paper(papers / "b_cat" / "zeta2020", WELL_FORMED)
    _make_paper(papers / "a_cat" / "alpha2020", WELL_FORMED)

    keys = [r.folder_rel for r in gather_summaries(papers, repo).records]
    assert keys == sorted(keys)


# ── corpus rendering ─────────────────────────────────────────────────────────
def test_render_corpus_has_delimiters_and_warning_block(tmp_path: Path) -> None:
    repo, papers = _make_tree(tmp_path)
    _make_paper(papers / "field_a" / "doe2020fine", WELL_FORMED)
    (papers / "field_a" / "empty_paper").mkdir(parents=True)

    corpus = render_corpus(gather_summaries(papers, repo))

    assert f"{PAPER_DELIMITER} doe2020fine" in corpus
    assert f"## {RELEVANCE_HEADING}" in corpus
    assert "=== WARNINGS (1) ===" in corpus
    assert "summary.md not found" in corpus
