"""Tests for the canonical project paths in ``code_paths``."""

from __future__ import annotations

from pathlib import Path

import code_paths
from code_paths import ProjectPaths, find_repo_root


def test_repo_root_resolves_to_this_repository() -> None:
    repo = code_paths.paths.repo

    assert (repo / "AGENTS.md").is_file()
    assert (repo / "code").is_dir()
    assert code_paths.paths.src == Path(code_paths.__file__).resolve().parent


def test_find_repo_root_accepts_git_directory(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    start = repo / "code" / "src"
    start.mkdir(parents=True)
    (repo / ".git").mkdir()

    assert find_repo_root(start, fallback=repo) == repo


def test_find_repo_root_accepts_git_file(tmp_path: Path) -> None:
    repo = tmp_path / "worktree"
    start = repo / "code" / "src"
    start.mkdir(parents=True)
    (repo / ".git").write_text("gitdir: ../main/.git/worktrees/worktree\n")

    assert find_repo_root(start, fallback=repo) == repo


def test_find_repo_root_falls_back_without_git(tmp_path: Path) -> None:
    repo = tmp_path / "download"
    start = repo / "code" / "src"
    start.mkdir(parents=True)

    assert find_repo_root(start, fallback=repo) == repo


def test_find_repo_root_never_climbs_into_outer_repository(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    repo = tmp_path / "nested"
    start = repo / "code" / "src"
    start.mkdir(parents=True)

    assert find_repo_root(start, fallback=repo) == repo


def test_ensure_outputs_tree_creates_artifact_directories(tmp_path: Path) -> None:
    project = ProjectPaths.for_repo(tmp_path)

    project.ensure_outputs_tree()
    project.ensure_outputs_tree()  # Idempotent.

    assert project.outputs == project.artifacts == tmp_path / "artifacts"
    for directory in (project.artifacts, project.figures, project.videos, project.dump):
        assert directory.is_dir()
        assert directory.is_relative_to(tmp_path)
    assert not project.data.exists()
