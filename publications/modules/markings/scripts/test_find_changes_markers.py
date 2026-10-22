#!/usr/bin/env python3
"""Regression tests for find_changes_markers.py."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from collections import Counter
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("find_changes_markers.py")
SPEC = importlib.util.spec_from_file_location("find_changes_markers", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
FINDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FINDER)


class FinderTests(unittest.TestCase):
    def test_scan_tex_reports_each_approvable_occurrence(self) -> None:
        source = r"""\Mark{changes}{added}
\Mark{changes}[heading]{Heading}
\Mark{changes}[math]{x+y}
\MarkEdit{edits}{old}{new}
\MarkEdit{edits}[text]{old text}{new text}
\MarkEdit{edits}[math]{x}{y}
\MarkEdit{edits}{deleted}{}
\Mark{changes}{outer \MarkEdit{edits}{old}{new}}
\Mark{changes}{one} and \Mark{changes}{two}
\Mark{missing}{keep me}
\MarkEdit{missing}{old}{new}
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_path = Path(temp_dir) / "fixture.tex"
            tex_path.write_text(source, encoding="utf-8")
            hits = FINDER.scan_tex(tex_path)

        counts = Counter(kind for _, kind, _ in hits)
        self.assertEqual(counts["Mark-inline"], 6)
        self.assertEqual(counts["MarkEdit-edits"], 5)
        self.assertEqual(sum(counts.values()), 11)

    def test_scan_bib_reports_only_changes_role_fields(self) -> None:
        source = """markroles = {changes},
markroles = {missing},
markroles = {edits, changes},
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            bib_path = Path(temp_dir) / "fixture.bib"
            bib_path.write_text(source, encoding="utf-8")
            hits = FINDER.scan_bib(bib_path)

        self.assertEqual(len(hits), 2)
        self.assertTrue(all(kind == "markroles-bib" for _, kind, _ in hits))


if __name__ == "__main__":
    unittest.main()
