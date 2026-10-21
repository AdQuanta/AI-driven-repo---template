"""Pure parsing, validation, and rendering for the literature tag index."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field
from difflib import SequenceMatcher
import hashlib
import os
from pathlib import Path
import posixpath
import re
import shutil
import tempfile


GENERATED_MARKER = "<!-- GENERATED: literature-tag-index; DO NOT EDIT -->"
CANONICAL_TAG_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")

_INDEX_HEADING = "# Scientific-paper tags"
_TABLE_HEADER = "| Tag | Papers |"
_TABLE_SEPARATOR = "|---|---:|"
TAG_PAGES_DIRNAME = "by_tag"
_INDEX_FILENAME = "index.md"
_INDEX_ROW_PATTERN = re.compile(
    r"^\| \[`(?P<tag>[a-z0-9]+(?:_[a-z0-9]+)*)`\]"
    rf"\({TAG_PAGES_DIRNAME}/(?P=tag)\.md\) \| (?P<count>[0-9]+) \|$"
)
_MARKDOWN_FENCE_PATTERN = re.compile(r" {0,3}(`{3,}|~{3,})(.*)")
_YAML_NUMBER_PATTERN = re.compile(
    r"""
    (?:
        [-+]?(?:
            0b[01_]+ | 0o[0-7_]+ | 0x[0-9a-fA-F_]+
            | (?:[0-9][0-9_]*(?:\.[0-9_]*)? | \.[0-9_]+)
              (?:[eE][-+]?[0-9]+)?
            | [0-9][0-9_]*(?::[0-5]?[0-9])+(?:\.[0-9_]*)?
            | \.(?:inf|Inf|INF)
        )
        | \.(?:nan|NaN|NAN)
    )
    """,
    re.VERBOSE,
)
_YAML_TIMESTAMP_PATTERN = re.compile(
    r"""
    (?:
        [0-9]{4}-[0-9]{2}-[0-9]{2}
        | [0-9]{4}-[0-9]{1,2}-[0-9]{1,2}[Tt\x20\t]+[0-9]{1,2}
          :[0-9]{2}:[0-9]{2}(?:\.[0-9]*)?
          (?:[\x20\t]*(?:Z|[-+][0-9]{1,2}(?::[0-9]{2})?))?
    )
    """,
    re.VERBOSE,
)
_YAML_NON_STRING_KEYWORDS = {
    "null", "~", "true", "false", "y", "n", "yes", "no", "on", "off",
}
_REQUIRED_FIELDS = ("citation_key", "short_cite", "tags")
_TAG_INDEX_DIR_REL = "research/references/indexes/tags"
_ASCII_LOWER_TRANSLATION = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"
)
_UTF8_BOM = b"\xef\xbb\xbf"
_UNSAFE_ISSUE_CODES = {
    "index_directory_invalid",
    "index_outside_repository",
    "index_parent_missing",
    "managed_path_escape",
    "managed_path_not_file",
    "managed_symlink",
    "noncanonical_managed_filename",
    "output_bom",
    "output_not_utf8",
    "output_read_error",
    "papers_root_unsafe",
    "protected_readme",
    "reserved_output_collision",
    "duplicate_managed_path",
    "unmarked_managed_file",
}
_ACCEPTED_INDEX_ISSUE_CODES = {"bootstrap_required", "malformed_index"}
_USAGE_ISSUE_CODES = {"usage_error"}
_UNSEEN_ISSUE_CODES = {"unseen_tag"}


@dataclass(frozen=True)
class PaperTagRecord:
    """Required tag metadata from one canonical paper summary."""

    summary_path: Path
    summary_rel: str
    citation_key: str
    short_cite: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class ValidationIssue:
    """One deterministic source-validation problem."""

    code: str
    message: str
    tag: str = ""
    summary_rel: str = ""
    normalized_candidate: str = ""


@dataclass(frozen=True)
class TagSuggestion:
    """An accepted tag and its mechanical string-similarity score."""

    tag: str
    ratio: float


@dataclass(frozen=True)
class TagIndexPaths:
    """Explicit repository locations used by generation planning."""

    repo_root: Path
    papers_root: Path
    index_dir: Path


@dataclass(frozen=True)
class GenerationPlan:
    """Complete read-only result of planning one generation operation."""

    expected: Mapping[str, str]
    stale_paths: tuple[Path, ...]
    obsolete_marked_paths: tuple[Path, ...]
    issues: tuple[ValidationIssue, ...]
    suggestions: Mapping[str, tuple[TagSuggestion, ...]]
    exit_code: int
    source_snapshot: Mapping[str, str] = field(default_factory=dict)
    output_snapshot: Mapping[str, str] = field(default_factory=dict)


class TagIndexError(ValueError):
    """Raised when source metadata or a persisted tag index cannot be parsed."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        summary_path: Path | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.summary_path = summary_path

    @property
    def exit_code(self) -> int:
        """Classify expected API failures consistently at entrypoint boundaries."""

        return 3 if self.code in _UNSAFE_ISSUE_CODES else 1


def _parse_required_scalar(field: str, raw_value: str, summary_path: Path) -> str:
    if not raw_value:
        raise TagIndexError(
            "empty_field",
            f"required frontmatter field is empty: {field}",
            summary_path=summary_path,
        )
    value, end = _parse_scalar_token(raw_value, field, summary_path)
    if raw_value[end:].strip():
        raise _malformed_scalar(field, summary_path)
    if not value.strip():
        raise TagIndexError(
            "empty_field",
            f"required frontmatter field is empty: {field}",
            summary_path=summary_path,
        )
    _validate_citation_metadata(field, value, summary_path)
    return value


def _validate_citation_metadata(field: str, value: str, summary_path: Path) -> None:
    """Require exact, single-line display text; never normalize decoded controls.

    YAML escapes are decoded generically, but citation labels and keys cannot
    contain C0/C1 controls or Unicode line/paragraph separators in Markdown.
    """

    if any(
        ord(character) < 0x20
        or 0x7F <= ord(character) <= 0x9F
        or character in "\u2028\u2029"
        for character in value
    ):
        raise TagIndexError(
            "invalid_citation_metadata",
            f"{field} must be single-line text without control characters "
            "or line separators; decoded YAML escapes are not silently rewritten",
            summary_path=summary_path,
        )


def _has_invalid_yaml_characters(text: str) -> bool:
    """Reject literal non-printable YAML input, not decoded quoted escapes."""

    return any(
        (ord(character) < 0x20 and character != "\t")
        or 0x7F <= ord(character) <= 0x84
        or 0x86 <= ord(character) <= 0x9F
        or 0xD800 <= ord(character) <= 0xDFFF
        or character in "\ufffe\uffff"
        for character in text
    )


def _malformed_scalar(field: str, summary_path: Path) -> TagIndexError:
    return TagIndexError(
        "malformed_field",
        f"required frontmatter field contains an unsupported or malformed scalar: {field}",
        summary_path=summary_path,
    )


def _is_non_string_plain_scalar(value: str) -> bool:
    """Require quotes for YAML 1.1/1.2 non-string scalar families.

    No loader-dependent coercion: reject decimal/base-prefixed numbers,
    legacy underscore/sexagesimal numbers, infinities/NaN, nulls, booleans
    (including legacy spellings), and timestamps. Whole-token matching keeps
    ordinary text such as ``42nd`` and ``0xGG`` valid; quoted tokens bypass
    this check entirely. Leading-zero integers remain rejected as before.
    """

    return (
        value.lower() in _YAML_NON_STRING_KEYWORDS
        or _YAML_NUMBER_PATTERN.fullmatch(value) is not None
        or _YAML_TIMESTAMP_PATTERN.fullmatch(value) is not None
    )


def _parse_scalar_token(
    text: str, field: str, summary_path: Path, *, flow: bool = False
) -> tuple[str, int]:
    """Decode the supported single-line YAML string subset, without coercion."""

    if not text or _has_invalid_yaml_characters(text):
        raise _malformed_scalar(field, summary_path)
    quote = text[0]
    if quote not in "'\"":
        end = text.find(",") if flow else len(text)
        if end < 0:
            end = len(text)
        value = text[:end].strip()
        # Collections, block scalars, aliases, anchors, typed values and
        # comments are outside this intentionally small string-only subset.
        if (
            not value
            or value[0] in "[]{}|>!&*#%@`"
            or re.match(r"^[-?:](?:[ \t]|$)", value)
            or value[-1] in "'\""
            or re.search(r":(?:[ \t]|$)|[ \t]#", value)
            or (flow and any(character in value for character in "[]{}'\""))
            or _is_non_string_plain_scalar(value)
        ):
            raise _malformed_scalar(field, summary_path)
        return value, end

    escapes = {
        "0": "\0", "a": "\a", "b": "\b", "t": "\t", "n": "\n",
        "v": "\v", "f": "\f", "r": "\r", "e": "\x1b", " ": " ",
        '"': '"', "/": "/", "\\": "\\", "N": "\x85", "_": "\xa0",
        "L": "\u2028", "P": "\u2029", "\t": "\t",
    }
    characters: list[str] = []
    position = 1
    while position < len(text):
        character = text[position]
        position += 1
        if character == quote:
            if quote == "'" and position < len(text) and text[position] == "'":
                characters.append("'")
                position += 1
                continue
            return "".join(characters), position
        if quote == '"' and character == "\\":
            if position >= len(text):
                raise _malformed_scalar(field, summary_path)
            escape = text[position]
            position += 1
            if escape in escapes:
                characters.append(escapes[escape])
            elif escape in {"x", "u", "U"}:
                width = {"x": 2, "u": 4, "U": 8}[escape]
                digits = text[position:position + width]
                if len(digits) != width or not re.fullmatch(r"[0-9a-fA-F]+", digits):
                    raise _malformed_scalar(field, summary_path)
                codepoint = int(digits, 16)
                if codepoint > 0x10FFFF or 0xD800 <= codepoint <= 0xDFFF:
                    raise _malformed_scalar(field, summary_path)
                characters.append(chr(codepoint))
                position += width
            else:
                raise _malformed_scalar(field, summary_path)
        else:
            characters.append(character)
    raise _malformed_scalar(field, summary_path)


def _parse_inline_tags(raw_value: str, summary_path: Path) -> tuple[str, ...]:
    if not raw_value:
        raise TagIndexError(
            "empty_field",
            "required frontmatter field is empty: tags",
            summary_path=summary_path,
        )
    if not raw_value.startswith("[") or not raw_value.endswith("]"):
        raise TagIndexError(
            "malformed_field",
            "tags must be an inline array",
            summary_path=summary_path,
        )

    content = raw_value[1:-1].strip()
    if not content:
        raise TagIndexError(
            "empty_field",
            "required frontmatter field is empty: tags",
            summary_path=summary_path,
        )

    tags: list[str] = []
    remaining = content
    while remaining:
        tag, end = _parse_scalar_token(remaining, "tags", summary_path, flow=True)
        if not tag.strip():
            raise _malformed_scalar("tags", summary_path)
        tags.append(tag)
        remaining = remaining[end:].lstrip()
        if not remaining:
            break
        if remaining[0] != ",":
            raise _malformed_scalar("tags", summary_path)
        remaining = remaining[1:].lstrip()
        if not remaining:
            raise _malformed_scalar("tags", summary_path)
    return tuple(tags)


def _deduplicate_records(
    records: tuple[PaperTagRecord, ...],
) -> tuple[PaperTagRecord, ...]:
    records_by_summary: dict[str, list[PaperTagRecord]] = defaultdict(list)
    for record in records:
        records_by_summary[record.summary_rel].append(record)

    deduplicated: list[PaperTagRecord] = []
    for summary_rel in sorted(records_by_summary):
        matching = records_by_summary[summary_rel]
        first = matching[0]
        if any(record != first for record in matching[1:]):
            raise TagIndexError(
                "conflicting_summary_record",
                f"conflicting records share summary path: {summary_rel}",
            )
        deduplicated.append(first)
    return tuple(deduplicated)


def _escape_markdown_link_label(value: str) -> str:
    return "".join(
        f"\\{character}" if character in "\\[]`*_" else character
        for character in value
    )


def _render_code_span(value: str) -> str:
    backtick_runs = (len(run) for run in re.findall(r"`+", value))
    delimiter = "`" * (max(backtick_runs, default=0) + 1)
    content = f" {value} " if value.startswith("`") or value.endswith("`") else value
    return f"{delimiter}{content}{delimiter}"


def normalize_tag(tag: str) -> str:
    """Return the mechanical lowercase ``snake_case`` candidate for ``tag``."""

    normalized = tag.translate(_ASCII_LOWER_TRANSLATION)
    normalized = re.sub(r"[-\s]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.strip("_")


def parse_summary(summary_path: Path, repo_root: Path) -> PaperTagRecord:
    """Parse required metadata from one summary without changing source text."""

    text = summary_path.read_bytes().decode("utf-8")
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0] != "---":
        raise TagIndexError(
            "missing_frontmatter",
            f"summary does not start with YAML frontmatter: {summary_path}",
            summary_path=summary_path,
        )

    try:
        closing_index = lines.index("---", 1)
    except ValueError as exc:
        raise TagIndexError(
            "unterminated_frontmatter",
            f"summary has no closing frontmatter delimiter: {summary_path}",
            summary_path=summary_path,
        ) from exc

    raw_fields: dict[str, str] = {}
    previous_required = ""
    for line in lines[1:closing_index]:
        if line[:1].isspace():
            if previous_required and line.strip() and not line.lstrip().startswith("#"):
                raise _malformed_scalar(previous_required, summary_path)
            continue
        key, separator, raw_value = line.partition(":")
        key = key.strip()
        if not separator or key not in _REQUIRED_FIELDS:
            if line.strip() and not line.startswith("#"):
                previous_required = ""
            continue
        if key in raw_fields:
            raise TagIndexError(
                "duplicate_field",
                f"required frontmatter field appears more than once: {key}",
                summary_path=summary_path,
            )
        if _has_invalid_yaml_characters(raw_value):
            raise _malformed_scalar(key, summary_path)
        raw_fields[key] = raw_value.strip()
        previous_required = key

    for field in _REQUIRED_FIELDS:
        if field not in raw_fields:
            raise TagIndexError(
                "missing_field",
                f"required frontmatter field is missing: {field}",
                summary_path=summary_path,
            )

    citation_key = _parse_required_scalar(
        "citation_key", raw_fields["citation_key"], summary_path
    )
    short_cite = _parse_required_scalar(
        "short_cite", raw_fields["short_cite"], summary_path
    )
    tags = _parse_inline_tags(raw_fields["tags"], summary_path)

    try:
        summary_rel = summary_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise TagIndexError(
            "summary_outside_repository",
            f"summary is outside the repository root: {summary_path}",
            summary_path=summary_path,
        ) from exc

    return PaperTagRecord(
        summary_path=summary_path,
        summary_rel=summary_rel,
        citation_key=citation_key,
        short_cite=short_cite,
        tags=tags,
    )


def discover_summaries(
    papers_root: Path,
    repo_root: Path,
) -> tuple[PaperTagRecord, ...]:
    """Recursively parse summaries in stable repository-relative path order."""

    summary_paths = sorted(
        papers_root.rglob("summary.md"),
        key=lambda path: path.relative_to(papers_root).as_posix(),
    )
    records = tuple(parse_summary(path, repo_root) for path in summary_paths)

    paths_by_citation_key: dict[str, list[str]] = defaultdict(list)
    for record in records:
        paths_by_citation_key[record.citation_key].append(record.summary_rel)
    duplicates = {
        key: tuple(paths)
        for key, paths in paths_by_citation_key.items()
        if len(paths) > 1
    }
    if duplicates:
        citation_key = min(duplicates)
        paths = ", ".join(sorted(duplicates[citation_key]))
        raise TagIndexError(
            "duplicate_citation_key",
            f"duplicate citation key {citation_key!r} in: {paths}",
        )

    return records


def validate_tag(tag: str) -> ValidationIssue | None:
    """Return an issue when ``tag`` is not canonical lowercase snake_case."""

    if CANONICAL_TAG_PATTERN.fullmatch(tag):
        return None
    candidate = normalize_tag(tag)
    return ValidationIssue(
        code="invalid_tag",
        message=f"tag is not canonical lowercase snake_case: {tag!r}",
        tag=tag,
        normalized_candidate=candidate,
    )


def validate_records(
    records: tuple[PaperTagRecord, ...],
) -> tuple[ValidationIssue, ...]:
    """Validate display metadata, tags, and local/global uniqueness."""

    issues: list[ValidationIssue] = []
    sorted_records = sorted(
        records,
        key=lambda record: (record.summary_rel, record.citation_key),
    )

    for record in sorted_records:
        for field in ("citation_key", "short_cite"):
            try:
                _validate_citation_metadata(
                    field, getattr(record, field), record.summary_path
                )
            except TagIndexError as exc:
                issues.append(
                    ValidationIssue(
                        code=exc.code,
                        message=str(exc),
                        summary_rel=record.summary_rel,
                    )
                )
        for tag in record.tags:
            issue = validate_tag(tag)
            if issue is not None:
                issues.append(
                    ValidationIssue(
                        code=issue.code,
                        message=issue.message,
                        tag=issue.tag,
                        summary_rel=record.summary_rel,
                        normalized_candidate=issue.normalized_candidate,
                    )
                )
        tag_counts = Counter(record.tags)
        for tag in sorted(tag for tag, count in tag_counts.items() if count > 1):
            issues.append(
                ValidationIssue(
                    code="duplicate_tag",
                    message=f"tag appears more than once in summary: {tag!r}",
                    tag=tag,
                    summary_rel=record.summary_rel,
                )
            )

    records_by_key: dict[str, list[PaperTagRecord]] = defaultdict(list)
    for record in sorted_records:
        records_by_key[record.citation_key].append(record)
    for citation_key in sorted(records_by_key):
        matching_records = records_by_key[citation_key]
        if len(matching_records) < 2:
            continue
        for record in matching_records:
            issues.append(
                ValidationIssue(
                    code="duplicate_citation_key",
                    message=f"citation key is used by multiple summaries: {citation_key!r}",
                    tag=citation_key,
                    summary_rel=record.summary_rel,
                )
            )

    issue_priority = {
        "invalid_tag": 0,
        "duplicate_tag": 1,
        "duplicate_citation_key": 2,
    }
    return tuple(
        sorted(
            issues,
            key=lambda issue: (
                issue.summary_rel,
                issue_priority.get(issue.code, 99),
                issue.tag,
                issue.message,
            ),
        )
    )


def _unfenced_markdown_lines(lines: list[str]) -> list[str]:
    """Mask fence blocks without moving line positions used by table parsing."""

    visible: list[str] = []
    fence = ""
    for line in lines:
        match = _MARKDOWN_FENCE_PATTERN.fullmatch(line)
        if fence:
            visible.append("")
            if (
                match is not None
                and match[1][0] == fence[0]
                and len(match[1]) >= len(fence)
                and not match[2].strip()
            ):
                fence = ""
        elif match is not None and not (
            match[1][0] == "`" and "`" in match[2]
        ):
            fence = match[1]
            visible.append("")
        else:
            visible.append(line)
    return visible


def parse_accepted_index(text: str) -> tuple[str, ...]:
    """Parse the contiguous pipe rows immediately following the separator.

    The first non-pipe line (including a blank or fence) ends the table.
    Only unfenced heading/table blocks define the schema; exactly one actual
    canonical table must occur in the accepted heading's section. Other text
    is formatting drift, not accepted-vocabulary schema data.
    """

    normalized = text.replace("\r\n", "\n")
    lines = normalized.split("\n")
    visible = _unfenced_markdown_lines(lines)
    headings = [number for number, line in enumerate(visible) if line == _INDEX_HEADING]
    headers = [
        number for number, line in enumerate(visible[:-1])
        if line == _TABLE_HEADER and visible[number + 1] == _TABLE_SEPARATOR
    ]
    if (
        not lines or lines[0] != GENERATED_MARKER
        or len(headings) != 1 or len(headers) != 1
        or headers[0] <= headings[0]
        or any(
            re.match(r"^ {0,3}#{1,6}(?:[ \t]|$)", line)
            for line in visible[headings[0] + 1:headers[0]]
        )
    ):
        raise TagIndexError(
            "malformed_index",
            "accepted index does not match the generated heading and table schema",
        )

    tags: list[str] = []
    for row in lines[headers[0] + 2:]:
        if not row.lstrip().startswith("|"):
            break
        match = _INDEX_ROW_PATTERN.fullmatch(row)
        if match is None:
            raise TagIndexError(
                "malformed_index",
                f"accepted index contains an invalid table row: {row!r}",
            )
        tag = match.group("tag")
        if tags and tag <= tags[-1]:
            raise TagIndexError(
                "malformed_index",
                "accepted index tags are not unique and strictly increasing",
            )
        tags.append(tag)

    return tuple(tags)


def suggest_similar_tags(
    candidate: str,
    accepted: tuple[str, ...],
) -> tuple[TagSuggestion, ...]:
    """Return up to three accepted tags similar to a normalized candidate."""

    normalized_candidate = normalize_tag(candidate)
    suggestions = (
        TagSuggestion(
            tag=accepted_tag,
            ratio=SequenceMatcher(None, normalized_candidate, accepted_tag).ratio(),
        )
        for accepted_tag in set(accepted)
    )
    eligible = (suggestion for suggestion in suggestions if suggestion.ratio >= 0.45)
    return tuple(
        sorted(eligible, key=lambda item: (-item.ratio, item.tag))[:3]
    )


def render_index(counts: Mapping[str, int]) -> str:
    """Render the generated accepted-tag index in canonical tag order."""

    rows: list[str] = []
    for tag in sorted(counts):
        issue = validate_tag(tag)
        if issue is not None:
            raise TagIndexError("invalid_tag", issue.message)
        count = counts[tag]
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise TagIndexError(
                "invalid_count",
                f"paper count for {tag!r} is not a nonnegative integer: {count!r}",
            )
        rows.append(f"| [`{tag}`]({TAG_PAGES_DIRNAME}/{tag}.md) | {count} |")

    lines = [
        GENERATED_MARKER,
        _INDEX_HEADING,
        "",
        _TABLE_HEADER,
        _TABLE_SEPARATOR,
        *rows,
    ]
    return "\n".join(lines) + "\n"


def render_tag_page(tag: str, records: tuple[PaperTagRecord, ...]) -> str:
    """Render one tag page, filtering and sorting matching papers."""

    issue = validate_tag(tag)
    if issue is not None:
        raise TagIndexError("invalid_tag", issue.message)

    matching: list[PaperTagRecord] = []
    for record in _deduplicate_records(records):
        if tag in record.tags:
            matching.append(record)
    matching.sort(
        key=lambda record: (record.short_cite, record.citation_key),
    )

    lines = [
        GENERATED_MARKER,
        f"# Papers tagged `{tag}`",
        "",
        f"**Paper count:** {len(matching)}",
        "",
    ]
    for record in matching:
        _validate_citation_metadata("short_cite", record.short_cite, record.summary_path)
        _validate_citation_metadata("citation_key", record.citation_key, record.summary_path)
        link = posixpath.relpath(
            record.summary_rel,
            f"{_TAG_INDEX_DIR_REL}/{TAG_PAGES_DIRNAME}",
        )
        short_cite = _escape_markdown_link_label(record.short_cite)
        citation_key = _render_code_span(record.citation_key)
        lines.append(
            f"- [\\[{short_cite}\\]]({link}) — {citation_key}"
        )
    return "\n".join(lines) + "\n"


def render_expected_outputs(
    records: tuple[PaperTagRecord, ...],
) -> dict[str, str]:
    """Return every expected generated file keyed by tag-index-relative POSIX path."""

    deduplicated = _deduplicate_records(records)
    tags = sorted({tag for record in deduplicated for tag in record.tags})
    for tag in tags:
        if tag.casefold() in {"index", "readme"}:
            raise TagIndexError(
                "reserved_output_collision",
                f"tag collides with a reserved output filename: {tag!r}",
            )
    counts = {
        tag: sum(tag in record.tags for record in deduplicated)
        for tag in tags
    }

    outputs = {_INDEX_FILENAME: render_index(counts)}
    outputs.update(
        (f"{TAG_PAGES_DIRNAME}/{tag}.md", render_tag_page(tag, deduplicated))
        for tag in tags
    )
    return outputs


def _repository_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def _validate_source_roots(paths: TagIndexPaths) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    if not paths.repo_root.exists() or not paths.repo_root.is_dir():
        issues.append(
            ValidationIssue(
                code="repo_root_invalid",
                message="repository root must exist and be a directory",
                summary_rel=paths.repo_root.as_posix(),
            )
        )
        return tuple(issues)

    if not paths.papers_root.exists() or not paths.papers_root.is_dir():
        issues.append(
            ValidationIssue(
                code="papers_root_invalid",
                message="papers root must exist and be a directory",
                summary_rel=_repository_relative(paths.papers_root, paths.repo_root),
            )
        )
        return tuple(issues)

    repo_root = paths.repo_root.resolve()
    papers_root = paths.papers_root.resolve()
    try:
        papers_root.relative_to(repo_root)
    except ValueError:
        issues.append(
            ValidationIssue(
                code="papers_root_unsafe",
                message="papers root resolves outside the repository",
                summary_rel=papers_root.as_posix(),
            )
        )
    if paths.papers_root.is_symlink():
        issues.append(
            ValidationIssue(
                code="papers_root_unsafe",
                message="papers root may not be a symbolic link",
                summary_rel=paths.papers_root.as_posix(),
            )
        )
    return tuple(issues)


def _digest_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _snapshot_sources(paths: TagIndexPaths) -> dict[str, str]:
    summary_paths = sorted(
        paths.papers_root.rglob("summary.md"),
        key=lambda path: _repository_relative(path, paths.repo_root),
    )
    return {
        _repository_relative(path, paths.repo_root): _digest_bytes(path.read_bytes())
        for path in summary_paths
    }


def _collect_records(
    paths: TagIndexPaths,
) -> tuple[tuple[PaperTagRecord, ...], tuple[ValidationIssue, ...]]:
    records: list[PaperTagRecord] = []
    issues: list[ValidationIssue] = []
    try:
        summary_paths = sorted(
            paths.papers_root.rglob("summary.md"),
            key=lambda path: _repository_relative(path, paths.repo_root),
        )
    except OSError as exc:
        return (), (
            ValidationIssue(
                code="source_discovery_error",
                message=f"cannot discover paper summaries: {exc}",
                summary_rel=_repository_relative(paths.papers_root, paths.repo_root),
            ),
        )

    for summary_path in summary_paths:
        summary_rel = _repository_relative(summary_path, paths.repo_root)
        try:
            records.append(parse_summary(summary_path, paths.repo_root))
        except TagIndexError as exc:
            issues.append(
                ValidationIssue(
                    code=exc.code,
                    message=str(exc),
                    summary_rel=summary_rel,
                )
            )
        except UnicodeDecodeError as exc:
            issues.append(
                ValidationIssue(
                    code="source_not_utf8",
                    message=f"summary is not valid UTF-8: {exc}",
                    summary_rel=summary_rel,
                )
            )
        except OSError as exc:
            issues.append(
                ValidationIssue(
                    code="source_read_error",
                    message=f"cannot read summary: {exc}",
                    summary_rel=summary_rel,
                )
            )

    record_tuple = tuple(records)
    issues.extend(validate_records(record_tuple))
    return record_tuple, tuple(issues)


def _issue_class(issue: ValidationIssue) -> int:
    if issue.code in _USAGE_ISSUE_CODES:
        return 0
    if issue.code in _UNSAFE_ISSUE_CODES:
        return 1
    if issue.code in _ACCEPTED_INDEX_ISSUE_CODES:
        return 3
    if issue.code in _UNSEEN_ISSUE_CODES:
        return 4
    return 2


def _sort_issues(issues: list[ValidationIssue]) -> tuple[ValidationIssue, ...]:
    return tuple(
        sorted(
            issues,
            key=lambda issue: (
                _issue_class(issue),
                issue.tag,
                issue.summary_rel,
                issue.code,
                issue.message,
            ),
        )
    )


def _logical_text(text: str) -> str:
    return text.replace("\r\n", "\n")


def _decode_managed_file(
    path: Path,
) -> tuple[str | None, ValidationIssue | None]:
    try:
        content = path.read_bytes()
    except OSError as exc:
        return None, ValidationIssue(
            code="output_read_error",
            message=f"cannot read managed output: {exc}",
            summary_rel=path.as_posix(),
        )
    if content.startswith(_UTF8_BOM):
        return None, ValidationIssue(
            code="output_bom",
            message="managed output must be UTF-8 without a byte-order mark",
            summary_rel=path.as_posix(),
        )
    try:
        return content.decode("utf-8"), None
    except UnicodeDecodeError as exc:
        return None, ValidationIssue(
            code="output_not_utf8",
            message=f"managed output is not valid UTF-8: {exc}",
            summary_rel=path.as_posix(),
        )


def _has_generated_marker(text: str) -> bool:
    return bool(text.splitlines()) and text.splitlines()[0] == GENERATED_MARKER


def _inspect_managed_outputs(
    paths: TagIndexPaths,
    expected_names: set[str],
) -> tuple[tuple[ValidationIssue, ...], tuple[Path, ...], Path | None]:
    issues: list[ValidationIssue] = []
    obsolete: list[Path] = []
    repo_root = paths.repo_root.resolve()
    index_dir = paths.index_dir.resolve(strict=False)

    try:
        index_dir.relative_to(repo_root)
    except ValueError:
        issues.append(
            ValidationIssue(
                code="index_outside_repository",
                message="tag-index directory resolves outside the repository",
                summary_rel=index_dir.as_posix(),
            )
        )
        return tuple(issues), (), None

    if not index_dir.exists():
        if not index_dir.parent.is_dir():
            issues.append(
                ValidationIssue(
                    code="index_parent_missing",
                    message="tag-index parent must exist before generation",
                    summary_rel=index_dir.parent.as_posix(),
                )
            )
        return tuple(issues), (), index_dir
    if not index_dir.is_dir():
        issues.append(
            ValidationIssue(
                code="index_directory_invalid",
                message="tag-index path is not a directory",
                summary_rel=index_dir.as_posix(),
            )
        )
        return tuple(issues), (), None

    try:
        entries = sorted(index_dir.iterdir(), key=lambda path: path.name)
    except OSError as exc:
        issues.append(
            ValidationIssue(
                code="output_read_error",
                message=f"cannot inspect tag-index directory: {exc}",
                summary_rel=index_dir.as_posix(),
            )
        )
        return tuple(issues), (), index_dir

    _inspect_managed_entries(
        paths, entries, index_dir, "", expected_names, issues, obsolete
    )

    pages_dir = index_dir / TAG_PAGES_DIRNAME
    if pages_dir.is_symlink():
        issues.append(
            ValidationIssue(
                code="managed_symlink",
                message="the tag-pages directory may not be a symbolic link",
                summary_rel=_repository_relative(pages_dir, paths.repo_root),
            )
        )
    elif pages_dir.exists():
        if not pages_dir.is_dir():
            issues.append(
                ValidationIssue(
                    code="index_directory_invalid",
                    message="tag-pages path is not a directory",
                    summary_rel=_repository_relative(pages_dir, paths.repo_root),
                )
            )
        else:
            try:
                page_entries = sorted(pages_dir.iterdir(), key=lambda path: path.name)
            except OSError as exc:
                issues.append(
                    ValidationIssue(
                        code="output_read_error",
                        message=f"cannot inspect tag-pages directory: {exc}",
                        summary_rel=_repository_relative(pages_dir, paths.repo_root),
                    )
                )
            else:
                _inspect_managed_entries(
                    paths,
                    page_entries,
                    pages_dir,
                    f"{TAG_PAGES_DIRNAME}/",
                    expected_names,
                    issues,
                    obsolete,
                )

    return tuple(issues), tuple(obsolete), index_dir


def _inspect_managed_entries(
    paths: TagIndexPaths,
    entries: list[Path],
    directory: Path,
    key_prefix: str,
    expected_names: set[str],
    issues: list[ValidationIssue],
    obsolete: list[Path],
) -> None:
    """Check one managed directory; a top-level ``<tag>.md`` is a legacy page."""

    is_pages_dir = bool(key_prefix)
    for entry in entries:
        if entry.suffix.casefold() != ".md" or (
            not is_pages_dir and entry.name == "README.md"
        ):
            continue
        display_path = _repository_relative(entry, paths.repo_root)
        if not is_pages_dir and entry.name.casefold() == "readme.md":
            issues.append(
                ValidationIssue(
                    code="protected_readme",
                    message="README.md is maintained and never managed",
                    summary_rel=display_path,
                )
            )
            continue
        is_index = not is_pages_dir and entry.name == _INDEX_FILENAME
        if not is_index and (
            entry.suffix != ".md"
            or validate_tag(entry.stem) is not None
            or entry.stem in {"index", "readme"}
        ):
            issues.append(
                ValidationIssue(
                    code="noncanonical_managed_filename",
                    message=(
                        "managed tag-page filename must be canonical "
                        "<tag>.md"
                    ),
                    tag=entry.stem,
                    summary_rel=display_path,
                )
            )
            continue
        if entry.is_symlink():
            issues.append(
                ValidationIssue(
                    code="managed_symlink",
                    message="managed Markdown paths may not be symbolic links",
                    summary_rel=display_path,
                )
            )
            continue
        try:
            if entry.resolve().parent != directory:
                raise ValueError
        except (OSError, ValueError):
            issues.append(
                ValidationIssue(
                    code="managed_path_escape",
                    message="managed output resolves outside the tag-index directory",
                    summary_rel=display_path,
                )
            )
            continue
        if not entry.is_file():
            issues.append(
                ValidationIssue(
                    code="managed_path_not_file",
                    message="managed Markdown path is not a regular file",
                    summary_rel=display_path,
                )
            )
            continue
        text, issue = _decode_managed_file(entry)
        if issue is not None:
            issues.append(
                ValidationIssue(
                    code=issue.code,
                    message=issue.message,
                    summary_rel=display_path,
                )
            )
            continue
        assert text is not None
        if not _has_generated_marker(text):
            issues.append(
                ValidationIssue(
                    code="unmarked_managed_file",
                    message="refusing to overwrite or remove unmarked Markdown",
                    summary_rel=display_path,
                )
            )
        elif f"{key_prefix}{entry.name}" not in expected_names:
            obsolete.append(entry)


def _managed_markdown_entries(index_dir: Path) -> list[tuple[str, Path]]:
    """Return ``(key, path)`` for every managed-candidate Markdown file."""

    candidates: list[tuple[str, Path]] = []
    for entry in sorted(index_dir.iterdir(), key=lambda path: path.name):
        if entry.suffix.casefold() != ".md" or entry.name == "README.md":
            continue
        candidates.append((entry.name, entry))
    pages_dir = index_dir / TAG_PAGES_DIRNAME
    if pages_dir.is_dir() and not pages_dir.is_symlink():
        for entry in sorted(pages_dir.iterdir(), key=lambda path: path.name):
            if entry.suffix.casefold() != ".md":
                continue
            candidates.append((f"{TAG_PAGES_DIRNAME}/{entry.name}", entry))
    return candidates


def _snapshot_managed_outputs(index_dir: Path) -> dict[str, str]:
    if not index_dir.is_dir():
        return {}
    snapshot: dict[str, str] = {}
    for key, entry in _managed_markdown_entries(index_dir):
        text, issue = _decode_managed_file(entry)
        if issue is not None or text is None:
            raise TagIndexError(
                issue.code if issue is not None else "output_read_error",
                issue.message if issue is not None else "cannot read managed output",
            )
        logical_bytes = _logical_text(text).encode("utf-8")
        snapshot[key] = _digest_bytes(logical_bytes)
    return snapshot


def _current_stale_paths(
    expected: Mapping[str, str],
    index_dir: Path,
) -> tuple[Path, ...]:
    stale_paths: list[Path] = []
    for filename, expected_text in sorted(expected.items()):
        current_path = index_dir / filename
        if not current_path.exists():
            stale_paths.append(current_path)
            continue
        if current_path.is_symlink() or not current_path.is_file():
            continue
        current_text, decode_issue = _decode_managed_file(current_path)
        if decode_issue is not None:
            continue
        assert current_text is not None
        if _logical_text(current_text) != _logical_text(expected_text):
            stale_paths.append(current_path)
    return tuple(stale_paths)


def _read_accepted_tags(
    paths: TagIndexPaths,
    *,
    accept_new_tags: bool,
) -> tuple[tuple[str, ...], list[ValidationIssue], bool]:
    index_path = paths.index_dir.resolve(strict=False) / "index.md"
    if not index_path.exists():
        if accept_new_tags:
            return (), [], True
        return (), [
            ValidationIssue(
                code="bootstrap_required",
                message=(
                    "index.md is missing; use --accept-new-tags to bootstrap "
                    "the accepted vocabulary"
                ),
                summary_rel=_repository_relative(index_path, paths.repo_root),
            )
        ], False
    if index_path.is_symlink() or not index_path.is_file():
        return (), [], False

    text, unsafe_issue = _decode_managed_file(index_path)
    if unsafe_issue is not None:
        return (), [], False
    assert text is not None
    try:
        return parse_accepted_index(text), [], True
    except TagIndexError as exc:
        return (), [
            ValidationIssue(
                code=exc.code,
                message=str(exc),
                summary_rel=_repository_relative(index_path, paths.repo_root),
            )
        ], False


def plan_generation(
    paths: TagIndexPaths,
    *,
    check: bool = False,
    accept_new_tags: bool = False,
) -> GenerationPlan:
    """Validate sources and outputs, returning all work without writing."""

    if check and accept_new_tags:
        issue = ValidationIssue(
            code="usage_error",
            message="--check and --accept-new-tags are mutually exclusive",
        )
        return GenerationPlan({}, (), (), (issue,), {}, 1)

    root_issues = _validate_source_roots(paths)
    if root_issues:
        safety_issues, _, _ = _inspect_managed_outputs(paths, set())
        sorted_root_issues = _sort_issues([*root_issues, *safety_issues])
        exit_code = (
            3
            if any(_issue_class(issue) == 1 for issue in sorted_root_issues)
            else 1
        )
        return GenerationPlan(
            expected={},
            stale_paths=(),
            obsolete_marked_paths=(),
            issues=sorted_root_issues,
            suggestions={},
            exit_code=exit_code,
        )

    try:
        source_snapshot_before = _snapshot_sources(paths)
    except OSError as exc:
        source_snapshot_before = {}
        source_snapshot_issue = ValidationIssue(
            code="source_read_error",
            message=f"cannot snapshot paper summaries: {exc}",
        )
    else:
        source_snapshot_issue = None

    records, source_issues = _collect_records(paths)
    issues = list(source_issues)
    collision_issues = [
        ValidationIssue(
            code="reserved_output_collision",
            message=f"tag collides with a reserved output filename: {tag!r}",
            tag=tag,
            summary_rel=record.summary_rel,
        )
        for record in records
        for tag in sorted(set(record.tags))
        if tag.casefold() in {"index", "readme"}
    ]
    issues.extend(collision_issues)
    if source_snapshot_issue is not None:
        issues.append(source_snapshot_issue)
    try:
        source_snapshot = _snapshot_sources(paths)
    except OSError as exc:
        source_snapshot = {}
        issues.append(
            ValidationIssue(
                code="source_read_error",
                message=f"cannot snapshot paper summaries: {exc}",
            )
        )
    if source_snapshot_before != source_snapshot:
        issues.append(
            ValidationIssue(
                code="source_state_changed",
                message="paper summaries changed during generation planning",
            )
        )
    source_is_valid = not source_issues and not collision_issues
    source_is_valid = source_is_valid and not any(
        issue.code in {"source_read_error", "source_state_changed"}
        for issue in issues
    )
    expected = render_expected_outputs(records) if source_is_valid else {}

    safety_issues, obsolete_paths, resolved_index_dir = _inspect_managed_outputs(
        paths,
        set(expected),
    )
    issues.extend(safety_issues)

    if resolved_index_dir is not None:
        accepted, accepted_issues, accepted_available = _read_accepted_tags(
            paths,
            accept_new_tags=accept_new_tags,
        )
    else:
        accepted, accepted_issues, accepted_available = (), [], False
    issues.extend(accepted_issues)

    suggestions: dict[str, tuple[TagSuggestion, ...]] = {}
    invalid_tags = sorted(
        {issue.tag for issue in source_issues if issue.code == "invalid_tag"}
    )
    for tag in invalid_tags:
        suggestions[tag] = suggest_similar_tags(normalize_tag(tag), accepted)

    observed_valid_tags = sorted(
        {
            tag
            for record in records
            for tag in record.tags
            if validate_tag(tag) is None
        }
    )
    unseen_tags = (
        [tag for tag in observed_valid_tags if tag not in accepted]
        if accepted_available
        else []
    )
    for tag in unseen_tags:
        suggestions[tag] = suggest_similar_tags(tag, accepted)
        if accept_new_tags:
            continue
        using_records = sorted(
            (record for record in records if tag in record.tags),
            key=lambda record: record.summary_rel,
        )
        issues.extend(
            ValidationIssue(
                code="unseen_tag",
                message=f"tag is not in the accepted vocabulary: {tag!r}",
                tag=tag,
                summary_rel=record.summary_rel,
            )
            for record in using_records
        )

    stale_paths: tuple[Path, ...] = ()
    if expected and resolved_index_dir is not None:
        stale_paths = _current_stale_paths(expected, resolved_index_dir)

    output_snapshot: dict[str, str] = {}
    if resolved_index_dir is not None and not safety_issues:
        try:
            output_snapshot = _snapshot_managed_outputs(resolved_index_dir)
        except TagIndexError as exc:
            issues.append(
                ValidationIssue(
                    code=exc.code,
                    message=str(exc),
                )
            )

    sorted_issues = _sort_issues(issues)
    issue_classes = {_issue_class(issue) for issue in sorted_issues}
    if 1 in issue_classes:
        exit_code = 3
    elif issue_classes:
        exit_code = 1
    elif check and (stale_paths or obsolete_paths):
        exit_code = 2
    else:
        exit_code = 0

    return GenerationPlan(
        expected=expected,
        stale_paths=stale_paths,
        obsolete_marked_paths=(
            tuple(sorted(obsolete_paths, key=lambda path: path.as_posix()))
            if source_is_valid else ()
        ),
        issues=sorted_issues,
        suggestions={tag: suggestions[tag] for tag in sorted(suggestions)},
        exit_code=exit_code,
        source_snapshot=source_snapshot,
        output_snapshot=output_snapshot,
    )


def _validated_managed_target(filename: str, index_dir: Path) -> Path:
    if filename.casefold() == "readme.md":
        raise TagIndexError("protected_readme", "README.md is never managed")
    page_prefix = f"{TAG_PAGES_DIRNAME}/"
    if filename == _INDEX_FILENAME:
        parent_dir = index_dir
    elif (
        filename.startswith(page_prefix)
        and filename.endswith(".md")
        and validate_tag(filename[len(page_prefix):-3]) is None
        and filename[len(page_prefix):-3] not in {"index", "readme"}
    ):
        parent_dir = index_dir / TAG_PAGES_DIRNAME
    else:
        raise TagIndexError(
            "managed_path_escape",
            f"invalid managed path: {filename!r}",
        )
    if parent_dir.is_symlink():
        raise TagIndexError(
            "managed_symlink",
            "the tag-pages directory may not be a symbolic link",
        )
    lexical_target = index_dir / filename
    if lexical_target.is_symlink():
        raise TagIndexError("managed_symlink", "managed output may not be a symbolic link")
    target = lexical_target.resolve(strict=False)
    if target.parent != parent_dir:
        raise TagIndexError(
            "managed_path_escape",
            f"managed path escapes tag-index directory: {filename!r}",
        )
    return target


def _atomic_replace(source: Path, target: Path) -> None:
    os.replace(source, target)


def _unlink_managed(path: Path) -> None:
    path.unlink()


def apply_generation_plan(plan: GenerationPlan, paths: TagIndexPaths) -> None:
    """Apply a successful plan after repeating all path and marker checks."""

    if plan.exit_code != 0 or plan.issues:
        raise TagIndexError(
            "unsuccessful_plan",
            "refusing to apply a generation plan with validation or safety issues",
        )

    repo_root = paths.repo_root.resolve()
    index_dir = paths.index_dir.resolve(strict=False)
    try:
        index_dir.relative_to(repo_root)
    except ValueError as exc:
        raise TagIndexError(
            "index_outside_repository",
            "tag-index directory resolves outside the repository",
        ) from exc
    if not index_dir.exists() and not index_dir.parent.is_dir():
        raise TagIndexError(
            "index_parent_missing",
            "tag-index parent must exist before generation",
        )
    if index_dir.exists() and not index_dir.is_dir():
        raise TagIndexError(
            "index_directory_invalid",
            "tag-index path is not a directory",
        )

    expected_targets = {
        filename: _validated_managed_target(filename, index_dir)
        for filename in plan.expected
    }
    for filename, expected_text in plan.expected.items():
        normalized_text = _logical_text(expected_text)
        if "\r" in normalized_text:
            raise TagIndexError(
                "invalid_generated_output",
                f"expected managed output contains a bare carriage return: {filename}",
            )
        if expected_text.startswith("\ufeff") or not _has_generated_marker(
            normalized_text
        ):
            raise TagIndexError(
                "unmarked_managed_file",
                f"expected managed output lacks the generated marker: {filename}",
            )
    stale_paths = tuple(path.resolve(strict=False) for path in plan.stale_paths)
    if len(set(stale_paths)) != len(stale_paths):
        raise TagIndexError(
            "duplicate_managed_path",
            "duplicate stale managed paths are not allowed",
        )
    expected_stale = {
        target for target in expected_targets.values() if target in stale_paths
    }
    if set(stale_paths) != expected_stale:
        raise TagIndexError(
            "managed_path_escape",
            "stale paths do not match direct expected managed paths",
        )

    obsolete_paths = tuple(
        path.resolve(strict=False) for path in plan.obsolete_marked_paths
    )
    if len(set(obsolete_paths)) != len(obsolete_paths):
        raise TagIndexError(
            "duplicate_managed_path",
            "duplicate obsolete managed paths are not allowed",
        )
    pages_dir = index_dir / TAG_PAGES_DIRNAME
    expected_target_paths = set(expected_targets.values())
    for obsolete in obsolete_paths:
        if (
            obsolete.parent not in {index_dir, pages_dir}
            or obsolete.suffix != ".md"
            or obsolete.name.casefold() in {"index.md", "readme.md"}
            or validate_tag(obsolete.stem) is not None
            or obsolete in expected_target_paths
        ):
            raise TagIndexError(
                "managed_path_escape",
                f"invalid obsolete managed path: {obsolete}",
            )

    current_issues, current_obsolete, _ = _inspect_managed_outputs(
        paths,
        set(plan.expected),
    )
    if current_issues:
        raise TagIndexError(
            current_issues[0].code,
            current_issues[0].message,
        )

    source_root_issues = _validate_source_roots(paths)
    if source_root_issues:
        raise TagIndexError(
            "source_state_changed",
            "source roots changed after generation planning",
        )
    try:
        current_source_snapshot = _snapshot_sources(paths)
    except OSError as exc:
        raise TagIndexError(
            "source_state_changed",
            f"cannot verify source snapshot: {exc}",
        ) from exc
    if current_source_snapshot != dict(plan.source_snapshot):
        raise TagIndexError(
            "source_state_changed",
            "paper summaries changed after generation planning",
        )

    if {path.resolve() for path in current_obsolete} != set(obsolete_paths):
        raise TagIndexError(
            "output_state_changed",
            "managed output state changed after planning",
        )
    try:
        current_output_snapshot = _snapshot_managed_outputs(index_dir)
    except TagIndexError as exc:
        raise TagIndexError(
            exc.code,
            f"cannot verify managed-output snapshot: {exc}",
        ) from exc
    if current_output_snapshot != dict(plan.output_snapshot):
        raise TagIndexError(
            "output_state_changed",
            "managed output changed after generation planning",
        )
    current_stale = {
        path.resolve(strict=False)
        for path in _current_stale_paths(plan.expected, index_dir)
    }
    if current_stale != set(stale_paths):
        raise TagIndexError(
            "output_state_changed",
            "managed output staleness changed after generation planning",
        )

    if not stale_paths and not obsolete_paths:
        return

    index_dir_existed = index_dir.exists()
    pages_dir_existed = pages_dir.exists()
    transaction_dir: Path | None = None
    backups: dict[Path, Path] = {}
    created_targets: list[Path] = []
    try:
        if not index_dir_existed:
            index_dir.mkdir()
        transaction_dir = Path(
            tempfile.mkdtemp(prefix=".literature-tag-index-", dir=index_dir)
        )
        stage_dir = transaction_dir / "stage"
        backup_dir = transaction_dir / "backup"
        stage_dir.mkdir()
        (stage_dir / TAG_PAGES_DIRNAME).mkdir()
        backup_dir.mkdir()

        staged_outputs: dict[str, Path] = {}
        for filename in sorted(plan.expected):
            staged_path = stage_dir / filename
            output = _logical_text(plan.expected[filename]).encode("utf-8")
            staged_path.write_bytes(output)
            staged_outputs[filename] = staged_path

        backup_targets = sorted(
            {
                target
                for target in expected_stale
                if target.exists()
            }
            | set(obsolete_paths),
            key=lambda path: path.as_posix(),
        )
        for number, target in enumerate(backup_targets):
            backup = backup_dir / f"{number:06d}.bak"
            shutil.copy2(target, backup)
            backups[target] = backup

        if not pages_dir_existed and any(
            target.parent == pages_dir for target in expected_stale
        ):
            pages_dir.mkdir()

        for filename in sorted(plan.expected):
            target = expected_targets[filename]
            if target not in expected_stale:
                continue
            if not target.exists():
                created_targets.append(target)
            _atomic_replace(staged_outputs[filename], target)

        for obsolete in sorted(obsolete_paths, key=lambda path: path.as_posix()):
            _unlink_managed(obsolete)
    except Exception as exc:
        rollback_errors: list[str] = []
        for target in reversed(created_targets):
            try:
                if target.exists():
                    os.unlink(target)
            except OSError as rollback_exc:
                rollback_errors.append(str(rollback_exc))
        for target, backup in sorted(
            backups.items(),
            key=lambda item: item[0].as_posix(),
        ):
            try:
                if backup.exists():
                    _atomic_replace(backup, target)
            except OSError as rollback_exc:
                rollback_errors.append(str(rollback_exc))
        if not pages_dir_existed and pages_dir.exists():
            try:
                pages_dir.rmdir()
            except OSError as rollback_exc:
                rollback_errors.append(str(rollback_exc))
        detail = f"generation transaction failed: {exc}"
        if rollback_errors:
            detail += "; rollback errors: " + "; ".join(rollback_errors)
        raise TagIndexError("apply_failed", detail) from exc
    finally:
        if transaction_dir is not None:
            shutil.rmtree(transaction_dir, ignore_errors=True)
        if not index_dir_existed and index_dir.exists():
            try:
                index_dir.rmdir()
            except OSError:
                pass
