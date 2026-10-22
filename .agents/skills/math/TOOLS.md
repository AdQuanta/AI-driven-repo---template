# Math Tools Reference

Complete reference for all mathematical computation tools.

## SymPy Compute (`.agents/skills/math/scripts/cc_math/sympy_compute.py`)

### Equation Solving
```bash
python .agents/skills/math/scripts/cc_math/sympy_compute.py solve "x**2 - 4 = 0" --var x --domain real
# Returns: {"solutions": ["-2", "2"], "verified": true}
```

### Calculus
```bash
# Differentiation
python .agents/skills/math/scripts/cc_math/sympy_compute.py diff "x**3 + 2*x" --var x --order 1

# Integration
python .agents/skills/math/scripts/cc_math/sympy_compute.py integrate "x**2" --var x
python .agents/skills/math/scripts/cc_math/sympy_compute.py integrate "x**2" --var x --bounds "[0, 1]"

# Limits
python .agents/skills/math/scripts/cc_math/sympy_compute.py limit "sin(x)/x" --var x --to 0
```

### Linear Algebra
```bash
# Determinant
python .agents/skills/math/scripts/cc_math/sympy_compute.py det "[[1,2],[3,4]]"

# Eigenvalues
python .agents/skills/math/scripts/cc_math/sympy_compute.py eigenvalues "[[2,0],[0,3]]"

# Eigenvectors (with multiplicities)
python .agents/skills/math/scripts/cc_math/sympy_compute.py eigenvectors "[[1,2],[2,1]]"

# Matrix inverse
python .agents/skills/math/scripts/cc_math/sympy_compute.py inverse "[[1,2],[3,4]]"

# Transpose
python .agents/skills/math/scripts/cc_math/sympy_compute.py transpose "[[1,2,3],[4,5,6]]"

# Characteristic polynomial
python .agents/skills/math/scripts/cc_math/sympy_compute.py charpoly "[[1,2],[3,4]]" --var t
```

### Simplification
```bash
python .agents/skills/math/scripts/cc_math/sympy_compute.py simplify "sin(x)**2 + cos(x)**2"
# Returns: {"simplified": "1"}
```

## Z3 Solve (`.agents/skills/math/scripts/cc_math/z3_solve.py`)

### Satisfiability
```bash
python .agents/skills/math/scripts/cc_math/z3_solve.py sat "x > 0, x < 5, x != 3"
```

### Prove/Disprove
```bash
python .agents/skills/math/scripts/cc_math/z3_solve.py prove "x**2 >= 0"
```

## Lean 4 (Formal Verification, optional)

Only if the project installs a Lean 4 toolchain with Mathlib; neither ships
with this skill.

### Setup
```bash
lake new my_project math
cd my_project && lake build
```

### Compiler-in-the-Loop
Write proof → `lake build` → Compiler verifies

### Key Imports
```lean
import Mathlib.CategoryTheory.Functor.Basic
import Mathlib.CategoryTheory.NatTrans
import Mathlib.CategoryTheory.Limits.Shapes.Products
```

## Output Format

All tools return JSON:
```json
{
  "result": "...",
  "latex": "\\frac{d}{dx}...",
  "verified": true
}
```

Use `--json` flag for explicit JSON output.
