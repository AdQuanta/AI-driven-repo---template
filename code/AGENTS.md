# Code Sector Guidance

This instruction is the canonical guidance for the code sector.

For code tasks, prioritize Python simulation correctness and reproducibility.

- Read existing modules before editing.
- Keep APIs stable unless explicitly asked to change them.
- Prefer small, testable changes and run relevant tests when possible.
- For generated script results, use `artifacts/` (repo root) as the canonical root (figures in `artifacts/figures/`, data in `artifacts/data/`).
- Prefer centralized path inference via `code/src/code_paths.py` over per-script relative path finding.
- Shared cross-domain Python helpers belong in `code/src/utils/` (create it on first need); check and reuse these utilities before introducing new helpers in domain-specific modules.
- Sector-specific Python dependencies are declared in `code/requirements.txt`; the root `requirements.txt` is reserved for packages used by shared skills and agents.


## Figure Text and Label Policy

- For formula-bearing figure labels (legend/title/axes), prefer LaTeX-formatted math labels when available instead of plain-text approximations such as `2d/(1+d^2)`.
- Keep one project-wide switch for LaTeX label rendering and one set of figure typography constants in a single module under `code/src/`; reuse them instead of hard-coding per-script values.
- Tune figure text sizes against the manuscript they will appear in, so figures match the paper's visual scale.


## Testing Guidelines

All existing tests must pass after changes.

- Test scope: write tests for `code/src/**` logic and internal APIs.
- Test organization: use `code/tests/` with one wrapper file per domain/module (for example, `test_find_papers_gather.py`).
- Directory structure: place tests in `code/tests/` and create tests as needed during development.
- Canonical test command: use `python -m pytest` from the `code/` folder, with the root `.venv` interpreter (`..\.venv\Scripts\python.exe` on Windows, `../.venv/bin/python` elsewhere) rather than a bare `python` that may not be on `PATH`.
- Wrapper pattern: keep domain wrappers in `code/tests/test_*.py` so future domains can add one wrapper file.
- Completion gate: before considering code work complete, run `Push-Location code; ..\.venv\Scripts\python.exe -m pytest; Pop-Location` and require a passing exit code.
