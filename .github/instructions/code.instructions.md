---
description: "Use when implementing or modifying Python code, simulations, algorithms, architecture, or tests in code/."
name: "Code Sector Guidance"
applyTo: "code/**"
---
# Code Sector Guidance

This instruction is the canonical guidance for the code sector.

For code tasks, prioritize Python simulation correctness and reproducibility.

- Read existing modules before editing.
- Keep APIs stable unless explicitly asked to change them.
- Prefer small, testable changes and run relevant tests when possible.
- For generated script results, use `artifacts/` (repo root) as the canonical root (figures in `artifacts/figures/`).
- Prefer centralized path inference via `code/src/code_paths.py` over per-script relative path finding.
- Shared cross-domain Python helpers live in `code/src/utils`; check and reuse these utilities before introducing new helpers in domain-specific modules.
- For scripts in `code/scripts/**`, prefer pure Python entrypoints that run directly in file-run/debug sessions; avoid adding CLI/`argparse` layers unless the user explicitly asks for CLI support.


## Figure Text and Label Policy

- For formula-bearing figure labels (legend/title/axes), prefer LaTeX-formatted math labels when available instead of plain-text approximations.
- Respect the global switch in `code/src/Globals.py` (`GlobalFlags.LaTeX_RENDERING`) for label style selection.
- Reuse global typography constants from `VisualConfig` for figure text sizes instead of hard-coded per-script values.
- Use `VisualConfig.PLOT_FONT_SIZE_PAPER_MATCH` as the project default "paper-visual-match" baseline when tuning figure text for manuscript inclusion.


## Code writing style:


### Python Module Calling Conventions
- **Never use `subprocess.run([sys.executable, "script.py"])` to call a Python script** that has an importable `main()`. Import and call it directly.
- **Never mutate `sys.argv`** to pass arguments to another module's `main()`. Refactor that `main()` to accept explicit keyword arguments with defaults instead.
- **Separate argparse from logic**: keep `argparse` in a `_parse_args()` helper called only from `if __name__ == "__main__"`, so `main()` is callable programmatically with keyword args.
- **`sys.path` manipulation and module-level imports belong at module level** (before any `def`), not lazily inside function bodies.
- When refactoring away a `subprocess` call to a direct import, remove the `import subprocess` line. When keeping subprocess usage, ensure it is imported.

**Canonical dual-callable pattern** — every module that can be run as a script should be callable both from the terminal and from Python code without any argument plumbing:

```python
# ── module-level imports (never inside def) ─────────────────────────────────
import argparse

# ── pure logic ───────────────────────────────────────────────────────────────
def main(*, n_steps: int = 100, alpha: float = 0.5) -> None:
    """Run the simulation. All parameters are keyword-only with defaults."""
    ...  # actual logic here

# ── CLI shim (only reached via `python script.py`) ───────────────────────────
def _parse_args() -> dict:
    p = argparse.ArgumentParser()
    p.add_argument("--n-steps", type=int, default=100)
    p.add_argument("--alpha", type=float, default=0.5)
    ns = p.parse_args()
    return {"n_steps": ns.n_steps, "alpha": ns.alpha}

if __name__ == "__main__":
    main(**_parse_args())
```

Callers (other scripts, tests, notebooks) just do:
```python
from code.scripts.figures.my_script import main
main(n_steps=200, alpha=0.3)   # no CLI, no subprocess, no sys.argv mutation
```

> **Exception for `code/scripts/**`:** pure exploration scripts that are never imported do not need `_parse_args()`. Keep `if __name__ == "__main__": main()` and put defaults directly in `main()`'s signature.

### Prefer Enums and Literals
Prefer expressive control-state types (`Enum` or `Literal`) over ambiguous `bool` flags when code flow depends on named states.

### Split Long Functions into Smaller Ones
When independent parts of a logic block can be extracted, split them into small, named sub-functions instead of keeping one long function.

### Type-hinting:
Use type hints for all functions, including return types. This improves readability and linting and helps catch bugs.

- Avoid using `Any` as a type hint. Instead, use more specific types or create custom types if necessary.
- If many outputs are needed from a function, consider using a `TypedDict` or a `dataclass` to return a structured object instead of an ambiguous unnamed tuple\dict.


## Testing Guidelines

Changes to the codebase must be accompanied by appropriate tests to ensure correctness and prevent regressions. All prior tests must pass after changes are made, and new tests should be added to cover new functionality or edge cases introduced by the changes.

- Test scope: write tests for `code/src/**` logic and internal APIs (math, physics, algorithms, OOP behavior).
- Test organization: use `code/tests/` with one wrapper file per domain/module (for example, `test_risk_tradeoff.py`).
- Script-level tests are not allowed. Period. Do not add tests for `code/scripts/**`.

### Test Selection Checklist (use before writing tests)
- Test it if it is core logic: equations, physics/math invariants, algorithmic decisions, reusable OOP behavior, or regression-prone domain logic in `code/src/**`.
- Do not test `code/scripts/**` glue: CLI argument plumbing, wrapper entrypoints, path bootstrapping, or artifact printouts.
- If logic in a script is important, move it to `code/src/**` and test the extracted module logic there.


- Mandatory tests: all simulations must be verified with automated tests, including small or simple features.
- Directory structure: place tests in `code/tests/` and create tests as needed during development.
- Canonical test command: use `python -m pytest` from the `code/` folder.
- Wrapper pattern: keep domain wrappers in `code/tests/test_*.py` so future domains can add one wrapper file.
- Completion gate: before considering code work complete, run `Push-Location code; python -m pytest; Pop-Location` and require a passing exit code.
