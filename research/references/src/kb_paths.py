"""Repository paths for the literature knowledge-base tools.

The tools in this folder find the repository root on their own, so they do
not depend on ``code/``. The root is the nearest ancestor holding ``.git`` as
a directory (a normal clone) or a file (a linked worktree). Without one, for
example in a ZIP download, the fixed location of this file decides. The
search never climbs above that fixed location into an outer repository.
"""

from __future__ import annotations

from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
# kb_paths.py -> src -> references -> research -> repository root
FALLBACK_ROOT = _THIS_FILE.parents[3]


def find_repo_root(start: Path, fallback: Path) -> Path:
    """Return the nearest ancestor of ``start`` (inclusive) containing ``.git``.

    ``.git`` may be a directory or a file. The walk stops at ``fallback``: if
    it reaches ``fallback`` without finding ``.git`` there, it returns
    ``fallback`` and never climbs into an outer repository. Return
    ``fallback`` also when no ancestor has ``.git``.
    """

    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
        if candidate == fallback:
            return fallback
    return fallback


def repo_root() -> Path:
    """Return the repository root of this checkout."""

    return find_repo_root(_THIS_FILE.parent, FALLBACK_ROOT)


def papers_root() -> Path:
    """Return the scientific-paper knowledge base folder."""

    return repo_root() / "research" / "references" / "scientific_papers"


def tag_index_dir() -> Path:
    """Return the generated tag-index folder."""

    return repo_root() / "research" / "references" / "indexes" / "tags"


def agents_dump_dir() -> Path:
    """Return the git-ignored folder for temporary agent files."""

    return repo_root() / "_agents_outputs" / "_agents_dump"
