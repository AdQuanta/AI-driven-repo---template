"""Canonical project paths derived from this file location.

This module centralizes absolute path inference for the repository layout.
All values are ``pathlib.Path`` objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


_this_file = Path(__file__).resolve()
src = _this_file.parent
code = src.parent
repo = code.parent
root = repo  # Backward-compatible alias.
utils = src / "utils"

artifacts = repo / "artifacts"
outputs = artifacts  # Backward-compatible alias.
figures = artifacts / "figures"
videos = artifacts / "videos"
dump = artifacts / "data"


@dataclass(frozen=True)
class ProjectPaths:
    """Snapshot of canonical project directories."""

    repo: Path
    code: Path
    src: Path
    utils: Path
    artifacts: Path
    outputs: Path
    figures: Path
    videos: Path
    dump: Path

    def ensure_outputs_tree(self) -> None:
        """Create the standard artifacts tree if it does not already exist."""

        self.artifacts.mkdir(parents=True, exist_ok=True)
        self.figures.mkdir(parents=True, exist_ok=True)
        self.videos.mkdir(parents=True, exist_ok=True)
        self.dump.mkdir(parents=True, exist_ok=True)


paths = ProjectPaths(
    repo=repo,
    code=code,
    src=src,
    utils=utils,
    artifacts=artifacts,
    outputs=outputs,
    figures=figures,
    videos=videos,
    dump=dump,
)


__all__ = [
    "ProjectPaths",
    "artifacts",
    "code",
    "dump",
    "figures",
    "outputs",
    "paths",
    "repo",
    "root",
    "src",
    "utils",
    "videos",
]
