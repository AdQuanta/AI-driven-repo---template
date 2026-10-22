# Code Sector Guidance

This instruction is the canonical guidance for the code sector.

For code tasks, prioritize simulation correctness and reproducibility.

- Read existing modules before editing.
- Keep APIs stable unless explicitly asked to change them.
- Prefer small, testable changes and run relevant tests when possible.
- Put library logic in `code/src/`, figure scripts in `code/scripts/figures/`, and data-generation scripts in `code/scripts/data/`.
- For regenerable script results, use `artifacts/` (repo root, `code_paths.artifacts`) as the canonical root: figures in `artifacts/figures/`, videos in `artifacts/videos/`, and intermediate data in `artifacts/data/`. Git ignores it. Call `code_paths.paths.ensure_outputs_tree()` before writing there.
- For results that are expensive or impossible to regenerate (hardware runs, paid jobs, long simulations), use the Git-tracked `data/` (repo root, `code_paths.data`). Read `docs/agent-guidance/data-preservation.md` before writing, moving, or deleting generated data.
- Prefer centralized path inference via `code/src/code_paths.py` over per-script relative path finding. It finds the repo root from a `.git` directory (normal clone) or a `.git` file (linked worktree), and falls back to its own fixed location.
- Runtime bootstraps must prioritize the script's own checkout paths over existing shared-environment paths; a `.pth` file may otherwise import another worktree's source or send artifacts there.
- Long-running generation and validation should expose phase-level progress; use `pytest -s` for manual runs so its output capture does not hide progress bars.
- Shared cross-domain Python helpers belong in `code/src/utils/` (create it on first need); check and reuse these utilities before introducing new helpers in domain-specific modules.
- Declare every third-party package the code sector imports in `code/requirements.txt` (installed alone by CI) and in the root `requirements.txt` (installed into the shared `.venv`), in the same change that adds the import.
- Knowledge-base tooling (tag index, find-papers gatherer) is not code-sector code; it lives in `research/references/src/` with its own tests.


## Figure Text and Label Policy

- For formula-bearing figure labels (legend/title/axes), prefer LaTeX-formatted math labels when available instead of plain-text approximations such as `2d/(1+d^2)`.
- Keep one project-wide switch for LaTeX label rendering and one set of figure typography constants in a single module under `code/src/`; reuse them instead of hard-coding per-script values.
- Tune figure text sizes against the manuscript they will appear in, so figures match the paper's visual scale.


## Testing Guidelines

All existing tests must pass after changes.

- Test scope: write tests for `code/src/**` logic and internal APIs.
- Directory structure: place tests in `code/tests/` and create tests as needed during development.
- Test organization: one wrapper file per domain/module, named `code/tests/test_<module>.py` (for example, `test_code_paths.py`), so future domains can add one wrapper file.
- Imports: `code/pytest.ini` sets `pythonpath = src`, so tests import modules from `code/src/` directly (`import code_paths`). Do not add `sys.path` shims to tests.
- Test environment: install the root `requirements.txt` into the repository `.venv` (`.venv/Scripts/python.exe -m pip install -r requirements.txt` on Windows, `.venv/bin/python -m pip install -r requirements.txt` elsewhere).
- Canonical test command: use `python -m pytest` from the `code/` folder, with the root `.venv` interpreter (`..\.venv\Scripts\python.exe` on Windows, `../.venv/bin/python` elsewhere) rather than a bare `python` that may not be on `PATH`. From the repo root, `python -m pytest code` runs the same suite.
- Completion gate: before considering code work complete, run `Push-Location code; ..\.venv\Scripts\python.exe -m pytest; Pop-Location` (or `cd code && ../.venv/bin/python -m pytest`) and require a passing exit code.
