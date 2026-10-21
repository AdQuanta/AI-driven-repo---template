"""Canonical project paths for the code sector.

This module centralizes absolute path inference for the repository layout, so
scripts and tests never build paths relative to their own location. All values
are ``pathlib.Path`` objects.

The repository root is the nearest ancestor holding ``.git`` as a directory (a
normal clone) or a file (a linked worktree). Without one, for example in a ZIP
download, the fixed location of this file decides. The search never climbs
above that fixed location into an outer repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


_this_file = Path(__file__).resolve()
# code_paths.py -> src -> code -> repository root
FALLBACK_ROOT = _this_file.parents[2]


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


@dataclass(frozen=True)
class ProjectPaths:
    """Snapshot of canonical project directories."""

    repo: Path
    code: Path
    src: Path
    utils: Path
    artifacts: Path
    figures: Path
    videos: Path
    dump: Path
    data: Path

    @classmethod
    def for_repo(cls, repo: Path) -> ProjectPaths:
        """Derive every canonical directory from a repository root."""

        code_dir = repo / "code"
        src_dir = code_dir / "src"
        artifacts_dir = repo / "artifacts"
        return cls(
            repo=repo,
            code=code_dir,
            src=src_dir,
            utils=src_dir / "utils",
            artifacts=artifacts_dir,
            figures=artifacts_dir / "figures",
            videos=artifacts_dir / "videos",
            dump=artifacts_dir / "data",
            # Results that are expensive or impossible to regenerate. Git
            # tracks this folder; see docs/agent-guidance/data-preservation.md.
            data=repo / "data",
        )

    @property
    def outputs(self) -> Path:
        """Alias of ``artifacts``, the root of regenerable outputs."""

        return self.artifacts

    def ensure_outputs_tree(self) -> None:
        """Create the standard artifacts tree if it does not already exist."""

        for directory in (self.artifacts, self.figures, self.videos, self.dump):
            directory.mkdir(parents=True, exist_ok=True)


paths = ProjectPaths.for_repo(find_repo_root(_this_file.parent, FALLBACK_ROOT))

repo = paths.repo
root = repo  # Alias of ``repo``.
code = paths.code
src = paths.src
utils = paths.utils
artifacts = paths.artifacts
outputs = paths.outputs  # Alias of ``artifacts``.
figures = paths.figures
videos = paths.videos
dump = paths.dump
data = paths.data


__all__ = [
    "FALLBACK_ROOT",
    "ProjectPaths",
    "artifacts",
    "code",
    "data",
    "dump",
    "figures",
    "find_repo_root",
    "outputs",
    "paths",
    "repo",
    "root",
    "src",
    "utils",
    "videos",
]
