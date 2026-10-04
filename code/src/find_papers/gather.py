"""Gather all paper ``summary.md`` files into a single corpus.

The ``find-papers`` agent previously fanned out into per-category and per-leaf
sub-agents that walked the directory tree by hand. That machinery is replaced
by this deterministic pass: it reads every ``summary.md`` under the knowledge
base, validates its structure, computes the relative link the agent needs for
its output table, and renders one corpus document the agent scores in a single
read.

All logic here is pure and side-effect free so it can be unit tested against a
temporary fixture tree. The thin runnable entrypoint lives in
``code/scripts/find_papers/gather_summaries.py``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# Section headings every well-formed summary.md must contain.
KEY_TAKEAWAYS_HEADING = "Key Takeaways"
RELEVANCE_HEADING = "Relevance to This Project"
ABSTRACT_HEADING = "Abstract"

# Tolerated spelling variants of the relevance heading. All denote the same
# section, so a trivial wording difference must not drop an otherwise valid
# paper. Add older variants here if summaries were written with another heading.
RELEVANCE_HEADING_VARIANTS = (
    RELEVANCE_HEADING,
    "Relevance to the Project",
)

# Where the find-papers agent writes its result file. Used only to compute the
# relative markdown link from that file back to each paper folder.
DEFAULT_OUTPUT_DIR_REL = "_agents_outputs/find-papers"

PAPER_DELIMITER = "=== PAPER:"


@dataclass(frozen=True)
class PaperRecord:
    """One scoreable paper extracted from a ``summary.md``."""

    citation_key: str
    folder_rel: str  # workspace-relative folder path, forward slashes
    link: str  # relative link from the output dir to the paper folder
    title: str
    short_cite: str
    abstract: str
    key_takeaways: str
    relevance: str


@dataclass
class GatherResult:
    """Outcome of a gather pass: the scoreable records plus any warnings."""

    records: list[PaperRecord] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ── parsing helpers ──────────────────────────────────────────────────────────
def parse_frontmatter(text: str) -> dict[str, str]:
    """Return the scalar ``key: value`` pairs from a leading YAML frontmatter
    block. Only simple single-line string fields are needed (``title``,
    ``short_cite``, ``citation_key``), so this avoids a YAML dependency and
    silently ignores list/multiline fields such as ``tags``.

    Returns an empty dict if the text has no frontmatter block.
    """
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        return {}
    end = normalized.find("\n---", 4)
    if end == -1:
        return {}
    block = normalized[4:end]

    fields: dict[str, str] = {}
    for line in block.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            continue
        key = key.strip()
        value = value.strip()
        # Skip list/flow values (e.g. ``tags: [a, b]``) and empty scalars.
        if not value or value.startswith("[") or value.startswith("{"):
            continue
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        fields[key] = value
    return fields


def extract_section(body: str, heading: str) -> str | None:
    """Return the text under a ``## <heading>`` section, excluding the heading
    line itself, trimmed. Capture stops at the next level-1/level-2 heading.

    Returns ``None`` if the heading is absent.
    """
    lines = body.replace("\r\n", "\n").split("\n")
    target = f"## {heading}".strip().lower()

    start = None
    for i, line in enumerate(lines):
        if line.strip().lower() == target:
            start = i + 1
            break
    if start is None:
        return None

    collected: list[str] = []
    for line in lines[start:]:
        stripped = line.lstrip()
        if stripped.startswith("## ") or (
            stripped.startswith("# ") and not stripped.startswith("## ")
        ):
            break
        collected.append(line)
    return "\n".join(collected).strip()


def extract_relevance(body: str) -> str | None:
    """Return the relevance-section text, tolerating known heading variants."""
    for variant in RELEVANCE_HEADING_VARIANTS:
        section = extract_section(body, variant)
        if section is not None:
            return section
    return None


def has_frontmatter(text: str) -> bool:
    return text.replace("\r\n", "\n").startswith("---\n")


# ── filesystem walk ──────────────────────────────────────────────────────────
def _to_rel(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _is_leaf_dir(directory: Path) -> bool:
    """A leaf directory has no child sub-directories — by convention a paper
    folder named by citation key."""
    return not any(child.is_dir() for child in directory.iterdir())


def gather_summaries(
    papers_root: Path,
    repo_root: Path,
    *,
    output_dir_rel: str = DEFAULT_OUTPUT_DIR_REL,
) -> GatherResult:
    """Walk ``papers_root`` and return every well-formed paper as a record,
    accumulating warnings for missing or malformed ``summary.md`` files.

    A directory with no sub-directories is treated as a paper folder and is
    expected to contain ``summary.md``; one that does not produces a warning.
    """
    result = GatherResult()
    papers_root = papers_root.resolve()
    repo_root = repo_root.resolve()
    output_dir_abs = (repo_root / output_dir_rel).resolve()

    # Deterministic order: sort leaf folders by their relative path.
    leaf_dirs = sorted(
        (d for d in papers_root.rglob("*") if d.is_dir() and _is_leaf_dir(d)),
        key=lambda d: d.resolve().as_posix(),
    )

    for folder in leaf_dirs:
        folder_rel = _to_rel(folder, repo_root)
        summary = folder / "summary.md"
        if not summary.is_file():
            result.warnings.append(f"WARNING: {folder_rel} — summary.md not found")
            continue

        text = summary.read_text(encoding="utf-8")
        missing = _first_missing_section(text)
        if missing is not None:
            result.warnings.append(
                f"WARNING: {folder_rel}/summary.md — missing section: {missing}"
            )
            continue

        fm = parse_frontmatter(text)
        link = os.path.relpath(folder.resolve(), output_dir_abs).replace(os.sep, "/")
        if not link.endswith("/"):
            link += "/"

        result.records.append(
            PaperRecord(
                citation_key=fm.get("citation_key", folder.name),
                folder_rel=folder_rel,
                link=link,
                title=fm.get("title", folder.name),
                short_cite=fm.get("short_cite", ""),
                abstract=extract_section(text, ABSTRACT_HEADING) or "",
                key_takeaways=extract_section(text, KEY_TAKEAWAYS_HEADING) or "",
                relevance=extract_relevance(text) or "",
            )
        )

    return result


def _first_missing_section(text: str) -> str | None:
    """Return the name of the first required section that is absent, or None."""
    if not has_frontmatter(text):
        return "YAML frontmatter"
    if extract_section(text, KEY_TAKEAWAYS_HEADING) is None:
        return f"## {KEY_TAKEAWAYS_HEADING}"
    if extract_relevance(text) is None:
        return f"## {RELEVANCE_HEADING}"
    return None


# ── corpus rendering ─────────────────────────────────────────────────────────
def render_corpus(result: GatherResult) -> str:
    """Render the gather result as a single delimited markdown document for the
    agent to read and score in one pass."""
    lines: list[str] = [
        "# find-papers corpus",
        "#",
        "# Generated by code/scripts/find_papers/gather_summaries.py — do not edit by hand.",
        f"# Papers: {len(result.records)}   Warnings: {len(result.warnings)}",
        "#",
        f"# Each paper block starts with a line '{PAPER_DELIMITER} <citation_key>'.",
        "# Use the 'link' field verbatim as the markdown link target in your output table;",
        "# the link display text is the citation_key.",
        "# Score primarily on the Relevance section; Key Takeaways and Abstract are secondary.",
        "",
    ]

    for rec in result.records:
        lines.append(f"{PAPER_DELIMITER} {rec.citation_key}")
        lines.append(f"folder: {rec.folder_rel}")
        lines.append(f"link: {rec.link}")
        lines.append(f"title: {rec.title}")
        lines.append(f"short_cite: {rec.short_cite}")
        lines.append("")
        if rec.abstract:
            lines.append("## Abstract")
            lines.append(rec.abstract)
            lines.append("")
        lines.append("## Key Takeaways")
        lines.append(rec.key_takeaways)
        lines.append("")
        lines.append(f"## {RELEVANCE_HEADING}")
        lines.append(rec.relevance)
        lines.append("")

    lines.append(f"=== WARNINGS ({len(result.warnings)}) ===")
    lines.extend(result.warnings)
    lines.append("")

    return "\n".join(lines)
