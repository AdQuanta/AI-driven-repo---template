# Math Cognitive Stack

A multi-layer system for machine-verified mathematical problem solving.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MATH COGNITIVE STACK                          │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1 │ SymPy        │ Symbolic computation (exact)          │
│  Layer 2 │ Z3           │ Constraint solving (SAT/SMT)          │
│  Layer 3 │ Scratchpad   │ Step-by-step verification             │
│  Layer 4 │ Lean 4       │ Formal proofs (optional, external)    │
└─────────────────────────────────────────────────────────────────┘
```

## When to Use Each Layer

| Problem Type | Layer | Why |
|--------------|-------|-----|
| Solve equation | SymPy | Exact symbolic solutions |
| Prove inequality | Z3 | SAT solver for constraints |
| Verify derivation | Scratchpad | Step verification |
| Formal theorem | Lean 4 (external) | Machine-checked proof |
| Category theory | Lean 4 (external) | Abstract structures |

## Quick Start

```bash
# Symbolic computation
python .agents/skills/math/scripts/cc_math/sympy_compute.py solve "x**2 - 4 = 0"

# Matrix operations
python .agents/skills/math/scripts/cc_math/sympy_compute.py eigenvalues "[[1,2],[3,4]]"
python .agents/skills/math/scripts/cc_math/sympy_compute.py eigenvectors "[[2,0],[0,3]]"

# Formal verification (only if a Lean 4 toolchain is installed; not shipped)
lake build  # Compiler-in-the-loop
```

Run every command from the repository root with the root `.venv` interpreter
(`.venv\Scripts\python.exe` on Windows, `.venv/bin/python` on Linux/macOS, or
`python` once the venv is activated). The packages are declared in the root
`requirements.txt`; `uv run python ...` also works where `uv` is installed but is
optional.

## Skill Hierarchy

```
.agents/skills/
├── math/                    # Domain skills by topic
│   ├── abstract-algebra/    # Groups, rings, fields
│   ├── category-theory/     # Functors, nat trans, limits
│   ├── complex-analysis/    # Analytic functions, residues
│   ├── functional-analysis/ # Banach spaces, operators
│   ├── linear-algebra/      # Matrices, eigenvalues, vectors
│   ├── mathematical-logic/  # Propositional, predicate logic
│   ├── measure-theory/      # Lebesgue, sigma-algebras
│   ├── real-analysis/       # Limits, continuity, convergence
│   ├── topology/            # Open sets, compactness
│   ├── ...
│   └── scripts/cc_math/     # SymPy, Z3, Pint, NumPy, SciPy, mpmath CLIs
```

## Domain Skills

Each domain skill contains a `SKILL.md` with when to use it, key patterns, and
the exact tool commands. Category folders carry a `README.md` that links their
sub-skills by relative path (`<name>/SKILL.md`).

See `TOOLS.md` for the full command reference and `WORKFLOW.md` for how to
extend the scripts.
