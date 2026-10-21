"""Tests for repository-root discovery in kb_paths."""

from __future__ import annotations

from pathlib import Path

import kb_paths


def _src_dir(root: Path) -> Path:
    start = root / "research" / "references" / "src"
    start.mkdir(parents=True)
    return start


def test_finds_git_directory(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    start = _src_dir(tmp_path)
    assert kb_paths.find_repo_root(start, tmp_path / "unused") == tmp_path


def test_finds_git_file_of_linked_worktree(tmp_path: Path) -> None:
    (tmp_path / ".git").write_text(
        "gitdir: /elsewhere/.git/worktrees/example\n", encoding="utf-8"
    )
    start = _src_dir(tmp_path)
    assert kb_paths.find_repo_root(start, tmp_path / "unused") == tmp_path


def test_falls_back_without_git(tmp_path: Path) -> None:
    start = _src_dir(tmp_path)
    fallback = tmp_path / "fallback"
    assert kb_paths.find_repo_root(start, fallback) == fallback


def test_stops_at_fallback_inside_outer_repository(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    fallback = tmp_path / "repo"
    start = _src_dir(fallback)
    assert kb_paths.find_repo_root(start, fallback) == fallback


def test_fallback_root_is_repository_root() -> None:
    marker = kb_paths.FALLBACK_ROOT / "research" / "references" / "src" / "kb_paths.py"
    assert marker.is_file()


def test_paths_derive_from_repo_root() -> None:
    root = kb_paths.repo_root()
    refs = root / "research" / "references"
    assert kb_paths.papers_root() == refs / "scientific_papers"
    assert kb_paths.tag_index_dir() == refs / "indexes" / "tags"
    assert kb_paths.agents_dump_dir() == root / "_agents_outputs" / "_agents_dump"
