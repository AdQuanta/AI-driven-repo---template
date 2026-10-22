"""Generate or check the repository's scientific-paper tag index."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys
from typing import NoReturn, TypedDict

import kb_paths
from literature_tags import (
    GenerationPlan,
    TagIndexError,
    TagIndexPaths,
    apply_generation_plan,
    plan_generation,
)


class _UsageParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        self.print_usage()
        self.exit(1, f"{self.prog}: error: {message}\n")


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _print_diagnostics(plan: GenerationPlan, paths: TagIndexPaths) -> None:
    for issue in plan.issues:
        fields = [issue.code]
        if issue.tag:
            fields.append(f"tag={issue.tag}")
        if issue.summary_rel:
            fields.append(f"path={issue.summary_rel}")
        if issue.normalized_candidate:
            fields.append(f"normalized={issue.normalized_candidate}")
        suggestions = plan.suggestions.get(issue.tag, ())
        if suggestions:
            fields.append(
                "suggestions=" + ",".join(item.tag for item in suggestions)
            )
        fields.append(issue.message)
        print(": ".join(fields))

    stale_diagnostics = [
        f"stale_output: path={_display_path(path, paths.repo_root)}"
        for path in plan.stale_paths
    ]
    stale_diagnostics.extend(
        f"stale_output: obsolete={_display_path(path, paths.repo_root)}"
        for path in plan.obsolete_marked_paths
    )
    for diagnostic in sorted(stale_diagnostics):
        print(diagnostic)


def main(
    *,
    check: bool = False,
    accept_new_tags: bool = False,
    paths: TagIndexPaths | None = None,
) -> int:
    """Plan and optionally apply generation using explicit, testable paths."""

    selected_paths = paths or TagIndexPaths(
        repo_root=kb_paths.repo_root(),
        papers_root=kb_paths.papers_root(),
        index_dir=kb_paths.tag_index_dir(),
    )
    try:
        plan = plan_generation(
            selected_paths,
            check=check,
            accept_new_tags=accept_new_tags,
        )
        if plan.exit_code != 0:
            _print_diagnostics(plan, selected_paths)
            return plan.exit_code
        if not check:
            apply_generation_plan(plan, selected_paths)
    except TagIndexError as exc:
        print(f"{exc.code}: {exc}", file=sys.stderr)
        return exc.exit_code
    except (OSError, UnicodeError) as exc:
        print(f"generation_failed: {exc}", file=sys.stderr)
        return 1
    return 0


class _CLIArgs(TypedDict):
    check: bool
    accept_new_tags: bool


def _parse_args(argv: Sequence[str] | None = None) -> _CLIArgs:
    parser = _UsageParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--accept-new-tags", action="store_true")
    namespace = parser.parse_args(argv)
    return {
        "check": namespace.check,
        "accept_new_tags": namespace.accept_new_tags,
    }


if __name__ == "__main__":
    raise SystemExit(main(**_parse_args()))
