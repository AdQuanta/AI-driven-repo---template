"""Tests for the pure literature-tag index model and rendering logic."""

from __future__ import annotations

from dataclasses import replace
from difflib import SequenceMatcher
from pathlib import Path

import pytest


import literature_tags.tag_index as tag_index_module
from literature_tags import (
    GenerationPlan,
    GENERATED_MARKER,
    PaperTagRecord,
    TagIndexError,
    TagIndexPaths,
    apply_generation_plan,
    discover_summaries,
    normalize_tag,
    parse_accepted_index,
    parse_summary,
    plan_generation,
    render_expected_outputs,
    render_index,
    render_tag_page,
    suggest_similar_tags,
    validate_records,
    validate_tag,
)


def _summary_text(
    *,
    citation_key: str = '"example2026"',
    short_cite: str = '"Example et al., Venue 2026"',
    tags: str = "[experimental_network, sensor_networks]",
    newline: str = "\n",
) -> str:
    return newline.join(
        (
            "---",
            f"citation_key: {citation_key}",
            f"short_cite: {short_cite}",
            f"tags: {tags}",
            "---",
            "",
            "# Example",
            "",
        )
    )


def _write_summary(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def _record(
    tmp_path: Path,
    *,
    citation_key: str = "example2026",
    short_cite: str = "Example et al., Venue 2026",
    tags: tuple[str, ...] = ("experimental_network",),
    summary_rel: str = (
        "research/references/scientific_papers/ecology/"
        "example/example2026/summary.md"
    ),
) -> PaperTagRecord:
    return PaperTagRecord(
        summary_path=tmp_path / summary_rel,
        summary_rel=summary_rel,
        citation_key=citation_key,
        short_cite=short_cite,
        tags=tags,
    )


def _fixture_paths(tmp_path: Path) -> TagIndexPaths:
    paths = TagIndexPaths(
        repo_root=tmp_path,
        papers_root=tmp_path / "research/references/scientific_papers",
        index_dir=tmp_path / "research/references/indexes/tags",
    )
    paths.index_dir.parent.mkdir(parents=True, exist_ok=True)
    return paths


def _write_fixture_summary(
    paths: TagIndexPaths,
    *,
    tags: str = "[wetlands]",
    folder: str = "example",
    citation_key: str = "example2026",
) -> Path:
    summary = paths.papers_root / folder / "summary.md"
    _write_summary(
        summary,
        _summary_text(
            citation_key=citation_key,
            short_cite=f'"{citation_key}, 2026"',
            tags=tags,
        ),
    )
    return summary


def _write_accepted_index(
    paths: TagIndexPaths,
    counts: dict[str, int],
) -> None:
    paths.index_dir.mkdir(parents=True, exist_ok=True)
    (paths.index_dir / "index.md").write_text(
        render_index(counts),
        encoding="utf-8",
        newline="",
    )


def _bootstrap_fixture(paths: TagIndexPaths) -> GenerationPlan:
    plan = plan_generation(paths, accept_new_tags=True)
    assert plan.exit_code == 0
    apply_generation_plan(plan, paths)
    return plan


def _tree_snapshot(root: Path) -> dict[str, bytes | None]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): None if path.is_dir() else path.read_bytes()
        for path in sorted(root.rglob("*"))
    }


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_parse_summary_accepts_lf_and_crlf(tmp_path: Path, newline: str) -> None:
    summary = tmp_path / "papers" / "example" / "summary.md"
    _write_summary(summary, _summary_text(newline=newline))

    record = parse_summary(summary, tmp_path)

    assert record == PaperTagRecord(
        summary_path=summary,
        summary_rel="papers/example/summary.md",
        citation_key="example2026",
        short_cite="Example et al., Venue 2026",
        tags=("experimental_network", "sensor_networks"),
    )


def test_parse_summary_accepts_quoted_and_unquoted_tags(tmp_path: Path) -> None:
    summary = tmp_path / "summary.md"
    _write_summary(
        summary,
        _summary_text(tags="['experimental_network', \"wetlands\", water_networks]"),
    )

    assert parse_summary(summary, tmp_path).tags == (
        "experimental_network",
        "wetlands",
        "water_networks",
    )


def test_parse_summary_does_not_treat_nested_fields_as_top_level(
    tmp_path: Path,
) -> None:
    summary = tmp_path / "summary.md"
    _write_summary(
        summary,
        "---\nmetadata:\n  citation_key: nested2026\n"
        "  short_cite: Nested et al., 2026\n  tags: [wetlands]\n---\n",
    )

    with pytest.raises(TagIndexError) as exc_info:
        parse_summary(summary, tmp_path)

    assert exc_info.value.code == "missing_field"
    assert "citation_key" in str(exc_info.value)


@pytest.mark.parametrize(
    ("text", "code"),
    [
        ("# no frontmatter\n", "missing_frontmatter"),
        ("---\ncitation_key: example2026\n", "unterminated_frontmatter"),
        (
            "---\ncitation_key: example\nshort_cite: Cite\n---\n",
            "missing_field",
        ),
        (
            "---\ncitation_key: one\ncitation_key: two\n"
            "short_cite: Cite\ntags: [wetlands]\n---\n",
            "duplicate_field",
        ),
        (
            "---\ncitation_key: \nshort_cite: Cite\ntags: [wetlands]\n---\n",
            "empty_field",
        ),
        (
            "---\ncitation_key: '   '\nshort_cite: Cite\ntags: [wetlands]\n---\n",
            "empty_field",
        ),
        (
            "---\ncitation_key: example\nshort_cite: Cite\n"
            "tags: wetlands, soil_moisture\n---\n",
            "malformed_field",
        ),
        (
            "---\ncitation_key: example\nshort_cite: Cite\ntags: []\n---\n",
            "empty_field",
        ),
        (
            "---\ncitation_key: example\nshort_cite: Cite\n"
            "tags: ['wetlands]\n---\n",
            "malformed_field",
        ),
    ],
)
def test_parse_summary_rejects_missing_malformed_or_duplicate_required_fields(
    tmp_path: Path,
    text: str,
    code: str,
) -> None:
    summary = tmp_path / "summary.md"
    _write_summary(summary, text)

    with pytest.raises(TagIndexError) as exc_info:
        parse_summary(summary, tmp_path)

    assert exc_info.value.code == code
    assert exc_info.value.summary_path == summary


@pytest.mark.parametrize(
    ("tag", "candidate"),
    [
        ("Experimental-Work", "experimental_work"),
        ("resource allocation", "resource_allocation"),
        ("LOD__limit!", "lod_limit!"),
        ("é", "é"),
        (" __ÄBC-İ Σ\tA___ ", "Äbc_İ_Σ_a"),
    ],
)
def test_noncanonical_tag_is_rejected_with_normalized_candidate(
    tag: str,
    candidate: str,
) -> None:
    issue = validate_tag(tag)

    assert issue is not None
    assert issue.code == "invalid_tag"
    assert issue.tag == tag
    assert issue.normalized_candidate == candidate
    assert normalize_tag(tag) == candidate


def test_validate_tag_accepts_canonical_lowercase_snake_case() -> None:
    assert validate_tag("wetlands") is None
    assert validate_tag("two_sensors_2") is None


def test_validate_records_rejects_duplicate_tags_and_citation_keys(
    tmp_path: Path,
) -> None:
    alpha = _record(
        tmp_path,
        citation_key="shared2026",
        tags=("wetlands", "wetlands", "Bad-Tag"),
        summary_rel="papers/a/summary.md",
    )
    beta = _record(
        tmp_path,
        citation_key="shared2026",
        tags=("water_networks",),
        summary_rel="papers/b/summary.md",
    )

    issues = validate_records((beta, alpha))

    assert [(issue.code, issue.summary_rel, issue.tag) for issue in issues] == [
        ("invalid_tag", "papers/a/summary.md", "Bad-Tag"),
        ("duplicate_tag", "papers/a/summary.md", "wetlands"),
        ("duplicate_citation_key", "papers/a/summary.md", "shared2026"),
        ("duplicate_citation_key", "papers/b/summary.md", "shared2026"),
    ]


def test_discover_summaries_is_recursive_and_deterministic(tmp_path: Path) -> None:
    papers = tmp_path / "research" / "references" / "scientific_papers"
    _write_summary(
        papers / "z_category" / "zeta" / "summary.md",
        _summary_text(citation_key="zeta2026", short_cite="Zeta, 2026"),
    )
    _write_summary(
        papers / "a_category" / "alpha" / "summary.md",
        _summary_text(citation_key="alpha2026", short_cite="Alpha, 2026"),
    )

    records = discover_summaries(papers, tmp_path)

    assert tuple(record.citation_key for record in records) == (
        "alpha2026",
        "zeta2026",
    )
    assert all("\\" not in record.summary_rel for record in records)


def test_discover_summaries_rejects_duplicate_citation_keys(tmp_path: Path) -> None:
    papers = tmp_path / "papers"
    _write_summary(papers / "a" / "summary.md", _summary_text())
    _write_summary(papers / "b" / "summary.md", _summary_text())

    with pytest.raises(TagIndexError) as exc_info:
        discover_summaries(papers, tmp_path)

    assert exc_info.value.code == "duplicate_citation_key"


def test_parse_accepted_index_reads_strictly_increasing_unique_rows() -> None:
    text = (
        GENERATED_MARKER
        + "\r\n# Scientific-paper tags\r\n\r\n"
        + "| Tag | Papers |\r\n|---|---:|\r\n"
        + "| [`experimental_network`](by_tag/experimental_network.md) | 3 |\r\n"
        + "| [`wetlands`](by_tag/wetlands.md) | 0 |\r\n"
    )

    assert parse_accepted_index(text) == ("experimental_network", "wetlands")


@pytest.mark.parametrize(
    "row",
    [
        "| [`wetlands`](by_tag/other.md) | 1 |",
        "| [wetlands](by_tag/wetlands.md) | 1 |",
        "| [`wetlands`](by_tag/wetlands.md) | -1 |",
        "| [`Bad-Tag`](by_tag/Bad-Tag.md) | 1 |",
        "| [`wetlands`](by_tag/wetlands.md) | one |",
        "| [`wetlands`](wetlands.md) | 1 |",
    ],
)
def test_parse_accepted_index_rejects_malformed_rows(row: str) -> None:
    text = (
        GENERATED_MARKER
        + "\n# Scientific-paper tags\n\n"
        + "| Tag | Papers |\n|---|---:|\n"
        + row
        + "\n"
    )

    with pytest.raises(TagIndexError, match="accepted index"):
        parse_accepted_index(text)


@pytest.mark.parametrize(
    "rows",
    [
        ("wetlands", "experimental_network"),
        ("wetlands", "wetlands"),
    ],
)
def test_parse_accepted_index_rejects_unsorted_or_duplicate_tags(
    rows: tuple[str, str],
) -> None:
    rendered_rows = "".join(f"| [`{tag}`](by_tag/{tag}.md) | 1 |\n" for tag in rows)
    text = (
        GENERATED_MARKER
        + "\n# Scientific-paper tags\n\n"
        + "| Tag | Papers |\n|---|---:|\n"
        + rendered_rows
    )

    with pytest.raises(TagIndexError):
        parse_accepted_index(text)


@pytest.mark.parametrize(
    "suffix",
    [
        "\n",
        "unexpected trailing text\n",
    ],
)
def test_parse_accepted_index_ignores_trailing_content(suffix: str) -> None:
    text = render_index({"wetlands": 1}) + suffix

    assert parse_accepted_index(text) == ("wetlands",)


def test_parse_accepted_index_accepts_missing_final_newline() -> None:
    text = render_index({"wetlands": 1}).removesuffix("\n")

    assert parse_accepted_index(text) == ("wetlands",)


def test_similarity_normalizes_then_applies_threshold_and_order() -> None:
    accepted = ("abe", "abc", "wetlands", "experimental_network")
    suggestions = suggest_similar_tags("  ABD! ", accepted)

    expected = sorted(
        (
            (tag, SequenceMatcher(None, "abd!", tag).ratio())
            for tag in accepted
            if SequenceMatcher(None, "abd!", tag).ratio() >= 0.45
        ),
        key=lambda item: (-item[1], item[0]),
    )[:3]
    assert [(item.tag, item.ratio) for item in suggestions] == expected
    assert [item.tag for item in suggestions[:2]] == ["abc", "abe"]


def test_render_index_uses_exact_schema_and_sorted_tags() -> None:
    rendered = render_index({"wetlands": 1, "experimental_network": 3})

    assert rendered == (
        GENERATED_MARKER
        + "\n# Scientific-paper tags\n\n"
        + "| Tag | Papers |\n|---|---:|\n"
        + "| [`experimental_network`](by_tag/experimental_network.md) | 3 |\n"
        + "| [`wetlands`](by_tag/wetlands.md) | 1 |\n"
    )


def test_render_tag_page_links_to_summary_and_sorts_papers(tmp_path: Path) -> None:
    later = _record(
        tmp_path,
        citation_key="zeta2026",
        short_cite="Zeta et al., 2026",
        summary_rel="research/references/scientific_papers/z/zeta/summary.md",
    )
    earlier = _record(
        tmp_path,
        citation_key="alpha2026",
        short_cite="Alpha et al., 2026",
        summary_rel="research/references/scientific_papers/a/alpha/summary.md",
    )

    page = render_tag_page("experimental_network", (later, earlier))

    assert page == (
        GENERATED_MARKER
        + "\n# Papers tagged `experimental_network`\n\n"
        + "**Paper count:** 2\n\n"
        + "- [\\[Alpha et al., 2026\\]](../../../scientific_papers/a/alpha/summary.md)"
        + " — `alpha2026`\n"
        + "- [\\[Zeta et al., 2026\\]](../../../scientific_papers/z/zeta/summary.md)"
        + " — `zeta2026`\n"
    )


def test_render_tag_page_escapes_citation_punctuation(tmp_path: Path) -> None:
    record = _record(
        tmp_path,
        citation_key="alpha]path\\`trial",
        short_cite="Alpha [lab] \\ path `trial` *draft*, 2026",
    )

    page = render_tag_page("experimental_network", (record,))

    assert (
        "- [\\[Alpha \\[lab\\] \\\\ path \\`trial\\` \\*draft\\*, 2026\\]]"
        "(../../../scientific_papers/ecology/example/example2026/summary.md)"
        " — ``alpha]path\\`trial``\n"
    ) in page


def test_renderers_reject_conflicting_duplicate_summary_records_deterministically(
    tmp_path: Path,
) -> None:
    original = _record(tmp_path, citation_key="alpha", short_cite="Alpha")
    conflicting = _record(tmp_path, citation_key="beta", short_cite="Beta")

    expected_messages: list[str] = []
    for records in ((original, conflicting), (conflicting, original)):
        with pytest.raises(TagIndexError) as outputs_error:
            render_expected_outputs(records)
        with pytest.raises(TagIndexError) as page_error:
            render_tag_page("experimental_network", records)
        assert outputs_error.value.code == "conflicting_summary_record"
        assert page_error.value.code == "conflicting_summary_record"
        assert str(outputs_error.value) == str(page_error.value)
        expected_messages.append(str(outputs_error.value))

    assert expected_messages[0] == expected_messages[1]


def test_renderers_permit_identical_duplicate_summary_records(tmp_path: Path) -> None:
    record = _record(tmp_path)

    outputs = render_expected_outputs((record, record))
    page = render_tag_page("experimental_network", (record, record))

    assert "| [`experimental_network`](by_tag/experimental_network.md) | 1 |" in outputs[
        "index.md"
    ]
    assert page.count("example2026/summary.md") == 1
    assert "**Paper count:** 1" in page


def test_render_expected_outputs_has_deterministic_counts_and_keys(
    tmp_path: Path,
) -> None:
    alpha = _record(
        tmp_path,
        citation_key="alpha",
        short_cite="Alpha",
        tags=("wetlands", "experimental_network"),
        summary_rel="papers/alpha/summary.md",
    )
    beta = _record(
        tmp_path,
        citation_key="beta",
        short_cite="Beta",
        tags=("wetlands",),
        summary_rel="papers/beta/summary.md",
    )

    outputs = render_expected_outputs((beta, alpha))

    assert tuple(outputs) == (
        "index.md",
        "by_tag/experimental_network.md",
        "by_tag/wetlands.md",
    )
    assert "| [`experimental_network`](by_tag/experimental_network.md) | 1 |" in outputs[
        "index.md"
    ]
    assert "| [`wetlands`](by_tag/wetlands.md) | 2 |" in outputs["index.md"]
    wetlands_page = outputs["by_tag/wetlands.md"]
    assert wetlands_page.index("Alpha") < wetlands_page.index("Beta")


@pytest.mark.parametrize("check", [False, True])
def test_missing_index_requires_explicit_bootstrap(
    tmp_path: Path,
    check: bool,
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)

    plan = plan_generation(paths, check=check)

    assert plan.exit_code == 1
    assert [issue.code for issue in plan.issues] == ["bootstrap_required"]
    assert tuple(plan.expected) == ("index.md", "by_tag/wetlands.md")


def test_accept_new_tags_may_bootstrap_missing_index(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)

    plan = plan_generation(paths, accept_new_tags=True)

    assert plan.exit_code == 0
    assert plan.issues == ()
    assert plan.suggestions == {"wetlands": ()}
    assert set(path.name for path in plan.stale_paths) == {"index.md", "wetlands.md"}


def test_unseen_valid_tag_reports_every_using_summary_and_suggestions(
    tmp_path: Path,
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(
        paths,
        tags="[experimental_work]",
        folder="a",
        citation_key="alpha2026",
    )
    _write_fixture_summary(
        paths,
        tags="[experimental_work]",
        folder="z",
        citation_key="zeta2026",
    )
    _write_accepted_index(paths, {"experimental_network": 2})

    plan = plan_generation(paths)

    assert plan.exit_code == 1
    assert [
        (issue.code, issue.tag, issue.summary_rel) for issue in plan.issues
    ] == [
        (
            "unseen_tag",
            "experimental_work",
            "research/references/scientific_papers/a/summary.md",
        ),
        (
            "unseen_tag",
            "experimental_work",
            "research/references/scientific_papers/z/summary.md",
        ),
    ]
    assert plan.suggestions["experimental_work"][0].tag == "experimental_network"
    assert len(plan.suggestions["experimental_work"]) <= 3


def test_invalid_tag_reports_normalized_candidate_and_suggestions(
    tmp_path: Path,
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths, tags="[Experimental-Work]")
    _write_accepted_index(paths, {"experimental_network": 1})

    plan = plan_generation(paths)

    assert plan.exit_code == 1
    invalid = next(issue for issue in plan.issues if issue.code == "invalid_tag")
    assert invalid.normalized_candidate == "experimental_work"
    assert plan.suggestions["Experimental-Work"][0].tag == "experimental_network"


def test_accept_new_tags_allows_valid_unseen_tags(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths, tags="[experimental_work]")
    _write_accepted_index(paths, {"experimental_network": 0})

    plan = plan_generation(paths, accept_new_tags=True)

    assert plan.exit_code == 0
    assert plan.issues == ()
    assert "by_tag/experimental_work.md" in plan.expected
    assert "by_tag/experimental_network.md" not in plan.expected


def test_removed_accepted_tag_becomes_marked_obsolete_without_accept_flag(
    tmp_path: Path,
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    _write_accepted_index(paths, {"old_tag": 1, "wetlands": 1})
    obsolete = paths.index_dir / "old_tag.md"
    obsolete.write_text(
        f"{GENERATED_MARKER}\nold\n",
        encoding="utf-8",
        newline="",
    )

    plan = plan_generation(paths)

    assert plan.exit_code == 0
    assert "old_tag.md" not in plan.expected
    assert plan.obsolete_marked_paths == (obsolete,)


def test_check_returns_two_for_otherwise_valid_stale_output(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    _write_accepted_index(paths, {"wetlands": 0})

    plan = plan_generation(paths, check=True)

    assert plan.exit_code == 2
    assert set(path.name for path in plan.stale_paths) == {"index.md", "wetlands.md"}
    assert not any(issue.code != "stale_output" for issue in plan.issues)


def test_check_treats_crlf_and_lf_as_same_logical_text(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    _bootstrap_fixture(paths)
    for path in paths.index_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))

    plan = plan_generation(paths, check=True)

    assert plan.exit_code == 0
    assert plan.stale_paths == ()


def test_bom_in_managed_output_is_rejected(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    _bootstrap_fixture(paths)
    managed = paths.index_dir / "by_tag" / "wetlands.md"
    managed.write_bytes(b"\xef\xbb\xbf" + managed.read_bytes())

    plan = plan_generation(paths, check=True)

    assert plan.exit_code == 3
    assert any(issue.code == "output_bom" for issue in plan.issues)


@pytest.mark.parametrize(
    "filename",
    ["wetlands.md", "obsolete.md", "by_tag/wetlands.md", "by_tag/obsolete.md"],
)
def test_unmarked_expected_or_obsolete_page_is_unsafe(
    tmp_path: Path,
    filename: str,
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    _write_accepted_index(paths, {"wetlands": 1})
    protected = paths.index_dir / filename
    protected.parent.mkdir(exist_ok=True)
    protected.write_text("hand maintained\n", encoding="utf-8", newline="")

    plan = plan_generation(paths, accept_new_tags=True)

    assert plan.exit_code == 3
    assert any(issue.code == "unmarked_managed_file" for issue in plan.issues)
    assert protected.read_text(encoding="utf-8") == "hand maintained\n"


def test_unrelated_unsafe_output_does_not_suppress_unseen_diagnostics(
    tmp_path: Path,
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths, tags="[experimental_work]")
    _write_accepted_index(paths, {"experimental_network": 0})
    (paths.index_dir / "unrelated.md").write_text(
        "hand maintained\n",
        encoding="utf-8",
        newline="",
    )

    plan = plan_generation(paths)

    assert plan.exit_code == 3
    assert [issue.code for issue in plan.issues] == [
        "unmarked_managed_file",
        "unseen_tag",
    ]
    assert plan.suggestions["experimental_work"][0].tag == "experimental_network"


def test_writer_removes_only_marked_obsolete_pages(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    _write_accepted_index(paths, {"old_tag": 1, "wetlands": 1})
    obsolete = paths.index_dir / "by_tag" / "old_tag.md"
    obsolete.parent.mkdir()
    obsolete.write_text(
        f"{GENERATED_MARKER}\nobsolete\n",
        encoding="utf-8",
        newline="",
    )

    plan = plan_generation(paths)
    apply_generation_plan(plan, paths)

    assert not obsolete.exists()
    assert (paths.index_dir / "by_tag" / "wetlands.md").is_file()


def test_writer_migrates_legacy_top_level_pages_into_by_tag(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    _write_accepted_index(paths, {"wetlands": 1})
    legacy = paths.index_dir / "wetlands.md"
    legacy.write_text(f"{GENERATED_MARKER}\nlegacy\n", encoding="utf-8", newline="")

    plan = plan_generation(paths)
    assert plan.obsolete_marked_paths == (legacy,)
    apply_generation_plan(plan, paths)

    assert not legacy.exists()
    assert (paths.index_dir / "by_tag" / "wetlands.md").is_file()
    assert plan_generation(paths, check=True).exit_code == 0


@pytest.mark.parametrize("filename", ["README.md", "index.md", "Bad-Tag.md"])
def test_noncanonical_file_in_by_tag_is_unsafe(tmp_path: Path, filename: str) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    _bootstrap_fixture(paths)
    stray = paths.index_dir / "by_tag" / filename
    stray.write_text(f"{GENERATED_MARKER}\nstray\n", encoding="utf-8", newline="")

    plan = plan_generation(paths, check=True)

    assert plan.exit_code == 3
    assert any(
        issue.code == "noncanonical_managed_filename" for issue in plan.issues
    )
    assert stray.is_file()


def test_readme_is_never_managed_or_removed(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    readme = paths.index_dir / "README.md"
    readme.parent.mkdir(parents=True)
    original = f"{GENERATED_MARKER}\nmaintained anyway\n"
    readme.write_text(original, encoding="utf-8", newline="")

    plan = plan_generation(paths, accept_new_tags=True)
    apply_generation_plan(plan, paths)

    assert readme.read_text(encoding="utf-8") == original
    assert readme not in plan.obsolete_marked_paths


def test_planner_rejects_index_directory_outside_repository(tmp_path: Path) -> None:
    paths = TagIndexPaths(
        repo_root=tmp_path / "repo",
        papers_root=tmp_path / "repo/papers",
        index_dir=tmp_path / "outside/tags",
    )
    _write_fixture_summary(paths)

    plan = plan_generation(paths, accept_new_tags=True)

    assert plan.exit_code == 3
    assert any(issue.code == "index_outside_repository" for issue in plan.issues)


def test_planner_rejects_missing_repository_root(tmp_path: Path) -> None:
    missing_repo = tmp_path / "missing-repository"
    paths = TagIndexPaths(
        repo_root=missing_repo,
        papers_root=missing_repo / "papers",
        index_dir=missing_repo / "indexes/tags",
    )

    plan = plan_generation(paths, accept_new_tags=True)

    assert plan.exit_code == 3
    assert {issue.code for issue in plan.issues} == {
        "repo_root_invalid", "index_parent_missing"
    }
    assert plan.obsolete_marked_paths == ()


def test_missing_papers_root_blocks_without_planning_or_mutation(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    paths = TagIndexPaths(
        repo_root=repo,
        papers_root=repo / "missing-papers",
        index_dir=repo / "indexes/tags",
    )
    _write_accepted_index(paths, {"old_tag": 1})
    old_page = paths.index_dir / "old_tag.md"
    old_page.write_text(
        f"{GENERATED_MARKER}\nold\n",
        encoding="utf-8",
        newline="",
    )
    before = _tree_snapshot(paths.index_dir)

    plan = plan_generation(paths, accept_new_tags=True)

    assert plan.exit_code == 1
    assert any(issue.code == "papers_root_invalid" for issue in plan.issues)
    assert plan.obsolete_marked_paths == ()
    with pytest.raises(TagIndexError, match="refusing to apply"):
        apply_generation_plan(plan, paths)
    assert _tree_snapshot(paths.index_dir) == before


def test_planner_rejects_papers_root_outside_repository(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    paths = TagIndexPaths(
        repo_root=repo,
        papers_root=tmp_path / "outside-papers",
        index_dir=repo / "indexes/tags",
    )
    _write_fixture_summary(paths)

    plan = plan_generation(paths, accept_new_tags=True)

    assert plan.exit_code == 3
    assert any(issue.code == "papers_root_unsafe" for issue in plan.issues)
    assert plan.obsolete_marked_paths == ()


def test_planner_rejects_symlinked_papers_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    papers = repo / "papers"
    papers.mkdir(parents=True)
    paths = TagIndexPaths(
        repo_root=repo,
        papers_root=papers,
        index_dir=repo / "indexes/tags",
    )
    real_is_symlink = Path.is_symlink

    def report_papers_root_as_symlink(path: Path) -> bool:
        return path == papers or real_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", report_papers_root_as_symlink)

    plan = plan_generation(paths, accept_new_tags=True)

    assert plan.exit_code == 3
    assert any(issue.code == "papers_root_unsafe" for issue in plan.issues)
    assert plan.obsolete_marked_paths == ()


def test_writer_rejects_escaping_expected_path_before_writing(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    outside = paths.index_dir.parent / "outside.md"
    plan = GenerationPlan(
        expected={"../outside.md": "unsafe\n"},
        stale_paths=(outside,),
        obsolete_marked_paths=(),
        issues=(),
        suggestions={},
        exit_code=0,
    )

    with pytest.raises(TagIndexError, match="managed path"):
        apply_generation_plan(plan, paths)

    assert not outside.exists()
    assert not paths.index_dir.exists()


def test_writer_rejects_index_as_obsolete_before_mutation(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    _write_accepted_index(paths, {"wetlands": 0})
    index = paths.index_dir / "index.md"
    before = index.read_bytes()
    plan = GenerationPlan(
        expected={},
        stale_paths=(),
        obsolete_marked_paths=(index,),
        issues=(),
        suggestions={},
        exit_code=0,
    )

    with pytest.raises(TagIndexError, match="obsolete managed path"):
        apply_generation_plan(plan, paths)

    assert index.read_bytes() == before


def test_writer_rejects_duplicate_obsolete_paths_before_mutation(
    tmp_path: Path,
) -> None:
    paths = _fixture_paths(tmp_path)
    paths.index_dir.mkdir()
    obsolete = paths.index_dir / "old_tag.md"
    before = f"{GENERATED_MARKER}\nold\n".encode("utf-8")
    obsolete.write_bytes(before)
    plan = GenerationPlan(
        expected={},
        stale_paths=(),
        obsolete_marked_paths=(obsolete, obsolete),
        issues=(),
        suggestions={},
        exit_code=0,
    )

    with pytest.raises(TagIndexError, match="duplicate obsolete"):
        apply_generation_plan(plan, paths)

    assert obsolete.read_bytes() == before


def test_writer_rejects_noncanonical_obsolete_filename_before_mutation(
    tmp_path: Path,
) -> None:
    paths = _fixture_paths(tmp_path)
    paths.index_dir.mkdir()
    noncanonical = paths.index_dir / "Bad-Tag.md"
    before = f"{GENERATED_MARKER}\nold\n".encode("utf-8")
    noncanonical.write_bytes(before)
    plan = GenerationPlan(
        expected={},
        stale_paths=(),
        obsolete_marked_paths=(noncanonical,),
        issues=(),
        suggestions={},
        exit_code=0,
    )

    with pytest.raises(TagIndexError, match="obsolete managed path"):
        apply_generation_plan(plan, paths)

    assert noncanonical.read_bytes() == before


def test_noncanonical_managed_filename_is_unsafe_and_not_obsolete(
    tmp_path: Path,
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    _write_accepted_index(paths, {"wetlands": 1})
    noncanonical = paths.index_dir / "Bad-Tag.md"
    before = f"{GENERATED_MARKER}\nold\n".encode("utf-8")
    noncanonical.write_bytes(before)

    plan = plan_generation(paths)

    assert plan.exit_code == 3
    assert any(
        issue.code == "noncanonical_managed_filename" for issue in plan.issues
    )
    assert noncanonical not in plan.obsolete_marked_paths
    assert noncanonical.read_bytes() == before


def test_writer_is_idempotent_and_emits_lf_utf8_without_bom(
    tmp_path: Path,
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    _bootstrap_fixture(paths)
    before = {path.name: path.read_bytes() for path in paths.index_dir.glob("*.md")}

    plan = plan_generation(paths)
    apply_generation_plan(plan, paths)
    after = {path.name: path.read_bytes() for path in paths.index_dir.glob("*.md")}

    assert plan.exit_code == 0
    assert plan.stale_paths == ()
    assert before == after
    assert all(not content.startswith(b"\xef\xbb\xbf") for content in after.values())
    assert all(b"\r" not in content for content in after.values())


def test_writer_rejects_marked_output_drift_before_mutation(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    _write_accepted_index(paths, {"wetlands": 0})
    plan = plan_generation(paths)
    assert plan.exit_code == 0

    (paths.index_dir / "index.md").write_text(
        render_index({"wetlands": 2}),
        encoding="utf-8",
        newline="",
    )
    before_apply = _tree_snapshot(paths.index_dir)

    with pytest.raises(TagIndexError) as exc_info:
        apply_generation_plan(plan, paths)

    assert exc_info.value.code == "output_state_changed"
    assert _tree_snapshot(paths.index_dir) == before_apply


def test_writer_rejects_source_drift_before_mutation(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    summary = _write_fixture_summary(paths)
    _write_accepted_index(paths, {"wetlands": 0})
    plan = plan_generation(paths)
    assert plan.exit_code == 0
    before_outputs = _tree_snapshot(paths.index_dir)

    summary.write_bytes(summary.read_bytes() + b"changed after planning\n")

    with pytest.raises(TagIndexError) as exc_info:
        apply_generation_plan(plan, paths)

    assert exc_info.value.code == "source_state_changed"
    assert _tree_snapshot(paths.index_dir) == before_outputs


def test_writer_rolls_back_exact_tree_when_second_replace_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths, tags="[wetlands, water_networks]")
    _write_accepted_index(paths, {"wetlands": 0, "water_networks": 0})
    plan = plan_generation(paths)
    assert plan.exit_code == 0
    before = _tree_snapshot(paths.index_dir)
    real_replace = tag_index_module._atomic_replace
    replace_calls = 0

    def fail_second_replace(source: Path, target: Path) -> None:
        nonlocal replace_calls
        replace_calls += 1
        if replace_calls == 2:
            raise OSError("injected second replace failure")
        real_replace(source, target)

    monkeypatch.setattr(tag_index_module, "_atomic_replace", fail_second_replace)

    with pytest.raises(TagIndexError, match="transaction failed"):
        apply_generation_plan(plan, paths)

    assert _tree_snapshot(paths.index_dir) == before


def test_writer_rolls_back_exact_tree_when_delete_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    _write_accepted_index(paths, {"old_tag": 1, "wetlands": 0})
    obsolete = paths.index_dir / "old_tag.md"
    obsolete.write_text(
        f"{GENERATED_MARKER}\nold\n",
        encoding="utf-8",
        newline="",
    )
    plan = plan_generation(paths)
    assert plan.exit_code == 0
    before = _tree_snapshot(paths.index_dir)

    def fail_delete(path: Path) -> None:
        raise OSError(f"injected delete failure: {path.name}")

    monkeypatch.setattr(tag_index_module, "_unlink_managed", fail_delete)

    with pytest.raises(TagIndexError, match="transaction failed"):
        apply_generation_plan(plan, paths)

    assert _tree_snapshot(paths.index_dir) == before


def test_conflicting_generation_modes_are_usage_failure(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)

    plan = plan_generation(paths, check=True, accept_new_tags=True)

    assert plan.exit_code == 1
    assert [issue.code for issue in plan.issues] == ["usage_error"]


@pytest.mark.parametrize(
    ("raw", "decoded"),
    [
        ("'O''Brien, 2026'", "O'Brien, 2026"),
        (r'"A\"B\\C\nD\tE\x21\u03A9\U0001F600"', 'A"B\\C\nD\tE!Ω😀'),
        (r'"\0\a\b\v\f\r\e\ \/\N\_\L\P"', "\0\a\b\v\f\r\x1b /\x85\xa0\u2028\u2029"),
    ],
)
def test_quoted_yaml_scalars_are_decoded(
    tmp_path: Path, raw: str, decoded: str
) -> None:
    # YAML decoding is generic; display metadata has stricter single-line rules.
    value, end = tag_index_module._parse_scalar_token(
        raw, "short_cite", tmp_path / "summary.md"
    )
    assert value == decoded
    assert end == len(raw)
    assert tag_index_module._parse_inline_tags(
        f"[{raw}]", tmp_path / "summary.md"
    ) == (decoded,)


@pytest.mark.parametrize("field", ["citation_key", "short_cite", "tags"])
@pytest.mark.parametrize(
    "raw",
    [
        "0x2A", "-0xFF", "+0xA_B", "0b101010", "-0b1_010", "+0b10",
        "0o52", "-0o52", "+0o52", "052", "-052", "+0_52",
        "42", "-42", "+42", "1_000", "1_000.25", ".5", "-.5", "42.",
        "1e3", "-1.2E+3", "1_000.0e-2", "1:20", "-1:20:30", "1:20.5",
        ".inf", "-.Inf", "+.INF", ".NaN", ".nan", ".NAN",
        "yes", "NO", "On", "off", "y", "N", "TRUE", "False", "Null", "~",
        "2026-10-13", "2026-10-13T12:34:56Z",
        "2026-1-3 1:02:03.5 -05:00",
    ],
)
def test_plain_yaml_non_string_types_require_quotes(
    tmp_path: Path, field: str, raw: str
) -> None:
    summary = tmp_path / "summary.md"
    values = {"citation_key": '"key"', "short_cite": '"Cite"', "tags": "[wetlands]"}
    values[field] = f"[{raw}]" if field == "tags" else raw
    _write_summary(summary, _summary_text(**values))

    with pytest.raises(TagIndexError) as error:
        parse_summary(summary, tmp_path)
    assert error.value.code == "malformed_field"
    assert error.value.summary_path == summary

    for quote in ("'", '"'):
        quoted = f"{quote}{raw}{quote}"
        values[field] = f"[{quoted}]" if field == "tags" else quoted
        _write_summary(summary, _summary_text(**values))
        record = parse_summary(summary, tmp_path)
        assert getattr(record, field) == ((raw,) if field == "tags" else raw)


@pytest.mark.parametrize(
    "raw",
    ["0xGG", "0b102", "0o89", "1:60", "1_000_papers", "42nd", "infinity",
     "nan", ".infinitude", "2026-10-13-paper", "yes_paper", "none"],
)
def test_plain_yaml_type_lookalikes_remain_strings(tmp_path: Path, raw: str) -> None:
    summary = tmp_path / "summary.md"
    _write_summary(summary, _summary_text(citation_key=raw, short_cite=raw, tags=f"[{raw}]"))

    record = parse_summary(summary, tmp_path)
    assert (record.citation_key, record.short_cite, record.tags) == (raw, raw, (raw,))


@pytest.mark.parametrize("field", ["citation_key", "short_cite", "tags"])
@pytest.mark.parametrize(
    "raw",
    ["- bad", "? bad", ": bad", "a:\tb", "a:", "a\t# comment", "a\0b",
     "\x0bCite", "Cite\x1f"],
)
def test_blocker_invalid_plain_yaml_scalars_are_rejected(
    tmp_path: Path, field: str, raw: str
) -> None:
    summary = tmp_path / "summary.md"
    values = {"citation_key": '"key"', "short_cite": '"Cite"', "tags": "[wetlands]"}
    values[field] = f"[{raw}]" if field == "tags" else raw
    _write_summary(summary, _summary_text(**values))

    with pytest.raises(TagIndexError) as error:
        parse_summary(summary, tmp_path)

    assert error.value.code == "malformed_field"
    assert error.value.summary_path == summary


@pytest.mark.parametrize("quote", ["", "'", '"'])
@pytest.mark.parametrize("control", ["\0", "\x01", "\x0b", "\x1f", "\x7f", "\x9f"])
def test_blocker_literal_yaml_control_characters_are_rejected(
    tmp_path: Path, quote: str, control: str
) -> None:
    summary = tmp_path / "summary.md"
    _write_summary(
        summary, _summary_text(short_cite=f"{quote}A{control}B{quote}")
    )

    with pytest.raises(TagIndexError) as error:
        parse_summary(summary, tmp_path)

    assert error.value.code == "malformed_field"


@pytest.mark.parametrize("raw", ["'- bad'", '"? bad"', '"a:\tb"'])
def test_quoted_yaml_indicators_remain_valid(tmp_path: Path, raw: str) -> None:
    value, end = tag_index_module._parse_scalar_token(
        raw, "short_cite", tmp_path / "summary.md"
    )
    assert value == raw[1:-1]
    assert end == len(raw)


@pytest.mark.parametrize("raw", ["-bad", "?bad", ":bad", "a:b", "a#b"])
def test_valid_plain_yaml_indicators_are_not_over_rejected(
    tmp_path: Path, raw: str
) -> None:
    summary = tmp_path / "summary.md"
    _write_summary(summary, _summary_text(short_cite=raw))
    assert parse_summary(summary, tmp_path).short_cite == raw


@pytest.mark.parametrize("field", ["citation_key", "short_cite"])
@pytest.mark.parametrize(
    "escape", [r"\r", r"\n", r"\t", r"\0", r"\e", r"\x7f", r"\N", r"\L", r"\P"]
)
@pytest.mark.parametrize("mode", ["default", "check", "accept"])
def test_blocker_decoded_metadata_controls_fail_before_writing(
    tmp_path: Path, field: str, escape: str, mode: str
) -> None:
    paths = _fixture_paths(tmp_path)
    summary = _write_fixture_summary(paths)
    _bootstrap_fixture(paths)
    values = {"citation_key": '"key"', "short_cite": '"Cite"', "tags": "[wetlands]"}
    values[field] = f'"A{escape}B"'
    _write_summary(summary, _summary_text(**values))
    before = _tree_snapshot(tmp_path)

    plan = plan_generation(
        paths, check=mode == "check", accept_new_tags=mode == "accept"
    )

    assert plan.exit_code == 1
    assert [issue.code for issue in plan.issues] == ["invalid_citation_metadata"]
    assert field in plan.issues[0].message
    assert plan.expected == {}
    with pytest.raises(TagIndexError, match="refusing to apply"):
        apply_generation_plan(plan, paths)
    assert _tree_snapshot(tmp_path) == before


@pytest.mark.parametrize("field", ["citation_key", "short_cite"])
def test_blocker_direct_records_cannot_render_metadata_controls(
    tmp_path: Path, field: str
) -> None:
    record = _record(tmp_path)
    if field == "citation_key":
        record = replace(record, citation_key="A\rB")
    else:
        record = replace(record, short_cite="A\rB")

    assert [issue.code for issue in validate_records((record,))] == [
        "invalid_citation_metadata"
    ]
    with pytest.raises(TagIndexError) as error:
        render_tag_page("experimental_network", (record,))
    assert error.value.code == "invalid_citation_metadata"


@pytest.mark.parametrize(
    "suffix", ["\n```markdown\n| example |\n```\n", "```\n| example |\n```\n",
               "Notes.\n| example |\n", "\n| example |\n",
               "```markdown\n| Tag | Papers |\n|---|---:|\n| example |\n```\n",
               "\n~~~markdown\n# Scientific-paper tags\n| Tag | Papers |\n"
               "|---|---:|\n| example |\n~~~\n",
               "\nNotes.\n| Tag | Papers |\n"]
)
def test_blocker_pipe_examples_after_table_end_are_only_stale(
    tmp_path: Path, suffix: str
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    _bootstrap_fixture(paths)
    index = paths.index_dir / "index.md"
    text = render_index({"wetlands": 1}) + suffix
    index.write_bytes(text.encode("utf-8"))
    before = _tree_snapshot(tmp_path)

    assert parse_accepted_index(text) == ("wetlands",)
    plan = plan_generation(paths, check=True)
    assert plan.exit_code == 2
    assert plan.issues == ()
    assert plan.stale_paths == (index,)
    assert _tree_snapshot(tmp_path) == before


@pytest.mark.parametrize("position", ["before_heading", "before_table", "after_table"])
@pytest.mark.parametrize(
    ("opening", "closing"),
    [("```markdown", "```"), ("  ~~~markdown", "  ~~~~"), ("````markdown", "`````")],
)
def test_accepted_schema_ignores_fenced_heading_and_table_examples(
    position: str, opening: str, closing: str
) -> None:
    example = (
        opening + "\n# Scientific-paper tags\n| Tag | Papers |\n|---|---:|\n"
        "| example |\n```not-a-closing-fence\n" + closing + "\n"
    )
    text = render_index({"wetlands": 1})
    if position == "before_heading":
        text = text.replace(GENERATED_MARKER + "\n", GENERATED_MARKER + "\n" + example)
    elif position == "before_table":
        text = text.replace("| Tag | Papers |", example + "| Tag | Papers |")
    else:
        text += example

    assert parse_accepted_index(text) == ("wetlands",)


@pytest.mark.parametrize(
    "text",
    [
        GENERATED_MARKER + "\n```markdown\n" + render_index({"wetlands": 1}) + "```\n",
        GENERATED_MARKER + "\n# Scientific-paper tags\n```markdown\n"
        "| Tag | Papers |\n|---|---:|\n```\n",
        render_index({"wetlands": 1}) + "\n| Tag | Papers |\n|---|---:|\n",
        render_index({"wetlands": 1}) + "\n# Example\n| Tag | Papers |\n|---|---:|\n",
        render_index({"wetlands": 1}) + "\n# Scientific-paper tags\n",
        GENERATED_MARKER + "\n# Scientific-paper tags\n# Unrelated section\n"
        "| Tag | Papers |\n|---|---:|\n",
        GENERATED_MARKER + "\n# Scientific-paper tags\n| Tag | Papers |\n|---|---|\n",
    ],
)
def test_accepted_schema_requires_one_actual_table_in_its_heading(text: str) -> None:
    with pytest.raises(TagIndexError) as error:
        parse_accepted_index(text)
    assert error.value.code == "malformed_index"


@pytest.mark.parametrize("row", ["| example |", "  | example |", "| [`wetlands`](bad.md) | 1 |"])
def test_contiguous_invalid_rows_still_fail_before_table_end(
    tmp_path: Path, row: str
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    _bootstrap_fixture(paths)
    index = paths.index_dir / "index.md"
    index.write_bytes((render_index({"wetlands": 1}) + row + "\n\nEnd.\n").encode("utf-8"))

    plan = plan_generation(paths, check=True)
    assert plan.exit_code == 1
    assert [issue.code for issue in plan.issues] == ["malformed_index"]


def test_printable_quoted_metadata_is_preserved_and_immediately_current(
    tmp_path: Path,
) -> None:
    paths = _fixture_paths(tmp_path)
    summary = _write_fixture_summary(paths)
    _write_summary(
        summary,
        _summary_text(short_cite=r'"O\u0027Brien [lab] \\ path \u03A9\_\U0001F600"', tags="[wetlands]"),
    )
    source_before = summary.read_bytes()

    record = parse_summary(summary, paths.repo_root)
    assert record.short_cite == "O'Brien [lab] \\ path Ω\xa0😀"
    _bootstrap_fixture(paths)
    assert plan_generation(paths, check=True).exit_code == 0
    assert summary.read_bytes() == source_before
    assert all(b"\r" not in path.read_bytes() for path in paths.index_dir.rglob("*.md"))
    assert "O'Brien \\[lab\\] \\\\ path Ω\xa0😀" in (paths.index_dir / "by_tag" / "wetlands.md").read_text(encoding="utf-8")


def test_writer_rejects_bare_cr_in_expected_text_without_silent_rewrite(
    tmp_path: Path,
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    plan = plan_generation(paths, accept_new_tags=True)
    expected = dict(plan.expected)
    expected["by_tag/wetlands.md"] += "A\rB\n"
    plan = replace(plan, expected=expected)
    before = _tree_snapshot(tmp_path)

    with pytest.raises(TagIndexError) as error:
        apply_generation_plan(plan, paths)

    assert error.value.code == "invalid_generated_output"
    assert error.value.exit_code == 1
    assert _tree_snapshot(tmp_path) == before


@pytest.mark.parametrize("field", ["citation_key", "short_cite", "tags"])
@pytest.mark.parametrize(
    "raw",
    [
        '"a"b"', "'a'b'", '"a" trailing', r'"bad\q"',
        r'"bad\x0G"', r'"bad\uD800"', r'"bad\U00110000"',
        "{key: value}", "[nested]", "|", ">", "&anchor wetlands", "*alias", "!!str wetlands",
        "null", "~", "true", "false", "123", "a: b",
    ],
)
def test_unsupported_or_malformed_yaml_scalars_fail(
    tmp_path: Path, field: str, raw: str
) -> None:
    summary = tmp_path / "summary.md"
    values = {"citation_key": '"key"', "short_cite": '"Cite"', "tags": "[wetlands]"}
    values[field] = f"[{raw}]" if field == "tags" else raw
    _write_summary(summary, _summary_text(**values))
    with pytest.raises(TagIndexError) as error:
        parse_summary(summary, tmp_path)
    assert error.value.code == "malformed_field"


def test_single_quoted_backslash_and_quoted_commas_are_literal(tmp_path: Path) -> None:
    summary = tmp_path / "summary.md"
    _write_summary(
        summary, _summary_text(tags=r"""['a\b', 'c,d', 'O''Brien', "wetlands"]""")
    )
    assert parse_summary(summary, tmp_path).tags == (r"a\b", "c,d", "O'Brien", "wetlands")


def test_required_scalar_continuations_are_rejected(tmp_path: Path) -> None:
    summary = tmp_path / "summary.md"
    _write_summary(summary, _summary_text(short_cite="Cite\n  continued"))
    with pytest.raises(TagIndexError) as error:
        parse_summary(summary, tmp_path)
    assert error.value.code == "malformed_field"


@pytest.mark.parametrize("decoration", ["trailing", "surrounding", "no_newline"])
def test_index_formatting_drift_is_stale_not_schema_error(
    tmp_path: Path, decoration: str
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    _bootstrap_fixture(paths)
    index = paths.index_dir / "index.md"
    text = index.read_text(encoding="utf-8")
    if decoration == "trailing":
        text += "\nNotes outside the table.\n"
    elif decoration == "surrounding":
        text = text.replace(
            GENERATED_MARKER + "\n", GENERATED_MARKER + "\nIntro.\n\n"
        ) + "End.\n"
    else:
        text = text.rstrip("\n")
    index.write_bytes(text.encode("utf-8"))
    before = _tree_snapshot(paths.index_dir)
    assert parse_accepted_index(text) == ("wetlands",)
    plan = plan_generation(paths, check=True)
    assert plan.exit_code == 2
    assert plan.issues == ()
    assert plan.stale_paths == (index,)
    assert _tree_snapshot(paths.index_dir) == before


@pytest.mark.parametrize("tag", ["index", "readme", "README", "ReadMe"])
def test_reserved_tag_output_collisions_are_unsafe(tmp_path: Path, tag: str) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths, tags=f"[{tag}]")
    before = _tree_snapshot(tmp_path)
    plan = plan_generation(paths, accept_new_tags=True)
    assert plan.exit_code == 3
    assert any(issue.code == "reserved_output_collision" for issue in plan.issues)
    assert _tree_snapshot(tmp_path) == before


@pytest.mark.parametrize("source_problem", ["papers", "repo"])
def test_invalid_source_root_does_not_hide_output_safety(
    tmp_path: Path, source_problem: str
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_accepted_index(paths, {"wetlands": 1})
    (paths.index_dir / "wetlands.md").write_bytes(b"maintained\n")
    if source_problem == "repo":
        paths = TagIndexPaths(tmp_path / "missing", paths.papers_root, paths.index_dir)
    plan = plan_generation(paths, accept_new_tags=True)
    assert plan.exit_code == 3
    codes = {issue.code for issue in plan.issues}
    expected_source = (
        "papers_root_invalid" if source_problem == "papers" else "repo_root_invalid"
    )
    expected_safety = (
        "unmarked_managed_file" if source_problem == "papers" else "index_outside_repository"
    )
    assert {expected_source, expected_safety} <= codes
    assert plan.obsolete_marked_paths == ()


def test_writer_rejects_symlink_expected_target_before_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    plan = plan_generation(paths, accept_new_tags=True)
    real_is_symlink = Path.is_symlink
    monkeypatch.setattr(
        Path, "is_symlink", lambda path: path.name == "wetlands.md" or real_is_symlink(path)
    )
    with pytest.raises(TagIndexError) as error:
        apply_generation_plan(plan, paths)
    assert error.value.code == "managed_symlink"
    assert not paths.index_dir.exists()


@pytest.mark.parametrize(
    ("code", "status"),
    [("protected_readme", 3), ("managed_path_escape", 3),
     ("reserved_output_collision", 3), ("managed_symlink", 3),
     ("duplicate_managed_path", 3), ("apply_failed", 1),
     ("output_state_changed", 1), ("source_state_changed", 1)],
)
def test_generation_error_exit_status(code: str, status: int) -> None:
    assert TagIndexError(code, "failure").exit_code == status


@pytest.mark.parametrize("filename", ["WETLANDS.MD", "INDEX.MD", "readme.MD"])
def test_case_variant_markdown_outputs_are_unsafe(tmp_path: Path, filename: str) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    paths.index_dir.mkdir()
    protected = paths.index_dir / filename
    protected.write_bytes(b"maintained\n")
    before = _tree_snapshot(paths.index_dir)
    plan = plan_generation(paths, accept_new_tags=True)
    assert plan.exit_code == 3
    assert _tree_snapshot(paths.index_dir) == before


def test_writer_safety_wins_when_sources_also_drift(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    summary = _write_fixture_summary(paths)
    plan = plan_generation(paths, accept_new_tags=True)
    paths.index_dir.mkdir()
    (paths.index_dir / "wetlands.md").write_bytes(b"maintained\n")
    summary.unlink()
    before = _tree_snapshot(paths.index_dir)
    with pytest.raises(TagIndexError) as error:
        apply_generation_plan(plan, paths)
    assert error.value.exit_code == 3
    assert _tree_snapshot(paths.index_dir) == before


def test_writer_permission_failure_rolls_back_without_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    plan = plan_generation(paths, accept_new_tags=True)
    before = _tree_snapshot(tmp_path)

    def deny_replace(source: Path, target: Path) -> None:
        raise PermissionError("injected locked output")

    monkeypatch.setattr(tag_index_module, "_atomic_replace", deny_replace)
    with pytest.raises(TagIndexError, match="locked output") as error:
        apply_generation_plan(plan, paths)
    assert isinstance(error.value.__cause__, PermissionError)
    assert error.value.exit_code == 1
    assert _tree_snapshot(tmp_path) == before


def test_writer_preserves_unsafe_snapshot_failure_classification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths)
    plan = plan_generation(paths, accept_new_tags=True)
    before = _tree_snapshot(tmp_path)

    def fail_snapshot(index_dir: Path) -> dict[str, str]:
        raise TagIndexError("output_bom", f"unsafe snapshot at {index_dir}")

    monkeypatch.setattr(tag_index_module, "_snapshot_managed_outputs", fail_snapshot)
    with pytest.raises(TagIndexError) as error:
        apply_generation_plan(plan, paths)
    assert error.value.exit_code == 3
    assert _tree_snapshot(tmp_path) == before


def test_render_sort_uses_key_as_tie_breaker(tmp_path: Path) -> None:
    beta = _record(
        tmp_path, citation_key="beta", short_cite="Same", summary_rel="papers/b/summary.md"
    )
    alpha = _record(
        tmp_path, citation_key="alpha", short_cite="Same", summary_rel="papers/a/summary.md"
    )
    page = render_tag_page("experimental_network", (beta, alpha))
    assert page.index(" — `alpha`") < page.index(" — `beta`")


def test_decoded_tag_duplicates_fail_generation_without_writes(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    _write_fixture_summary(paths, tags=r'[wetlands, "\u0077etlands"]')
    before = _tree_snapshot(tmp_path)
    plan = plan_generation(paths, accept_new_tags=True)
    assert plan.exit_code == 1
    assert any(issue.code == "duplicate_tag" for issue in plan.issues)
    assert _tree_snapshot(tmp_path) == before


