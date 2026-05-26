#!/usr/bin/env python3
"""Find all role=changes markers in a LaTeX paper project.

Outputs one line per marker in the format:
    FILE:LINE [KIND] SNIPPET

Kinds:
  Mark-inline   -- \\Mark{changes}{...}  or  \\Mark{changes}[kind]{...}
  MarkEnv-text  -- \\begin{MarkEnv}{changes}[text]
  MarkEnv-math  -- \\begin{MarkEnv}{changes}[math]   <- needs equation wrap on removal
  MarkEnv-fig   -- \\begin{MarkEnv}{changes}[figure]
  markroles-bib -- markroles = {changes, ...}  in a .bib entry

Usage:
    python .github/prompts/scripts/find_changes_markers.py [project_root]

    project_root defaults to  publications/paper
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

MARK_INLINE_RE = re.compile(r"\\Mark\{changes\}")
MARKENV_OPEN_RE = re.compile(
    r"\\begin\{MarkEnv\}\{changes\}(?:\[(?P<kind>[^\]]*)\])?",
    re.IGNORECASE,
)
MARKROLES_RE = re.compile(
    r"markroles\s*=\s*\{[^}]*\bchanges\b[^}]*\}",
    re.IGNORECASE,
)


def _snippet(line: str, maxlen: int = 72) -> str:
    s = line.strip()
    return s[:maxlen] + "…" if len(s) > maxlen else s


def scan_tex(path: Path) -> list[tuple[int, str, str]]:
    """Return list of (lineno, kind, snippet) for a .tex file."""
    results = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, start=1):
        if MARK_INLINE_RE.search(line):
            results.append((i, "Mark-inline", _snippet(line)))
        m = MARKENV_OPEN_RE.search(line)
        if m:
            kind_raw = (m.group("kind") or "text").strip().lower()
            kind_map = {"math": "MarkEnv-math", "figure": "MarkEnv-fig"}
            kind = kind_map.get(kind_raw, "MarkEnv-text")
            results.append((i, kind, _snippet(line)))
    return results


def scan_bib(path: Path) -> list[tuple[int, str, str]]:
    """Return list of (lineno, kind, snippet) for a .bib file."""
    results = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, start=1):
        if MARKROLES_RE.search(line):
            results.append((i, "markroles-bib", _snippet(line)))
    return results


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path("publications/paper")
    if not root.exists():
        print(f"ERROR: project root '{root}' does not exist.", file=sys.stderr)
        return 1

    total = 0
    for tex in sorted(root.rglob("*.tex")):
        hits = scan_tex(tex)
        for lineno, kind, snippet in hits:
            print(f"{tex}:{lineno} [{kind}] {snippet}")
            total += 1

    for bib in sorted(root.rglob("*.bib")):
        hits = scan_bib(bib)
        for lineno, kind, snippet in hits:
            print(f"{bib}:{lineno} [{kind}] {snippet}")
            total += 1

    print(f"\n{total} marker(s) found.", file=sys.stderr)
    return 0 if total == 0 else 2   # exit 2 = markers found, 0 = clean


if __name__ == "__main__":
    sys.exit(main(sys.argv))
