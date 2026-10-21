# Math Skills Development Workflow

How to extend this skill.

## Philosophy: Cognitive Prosthetics

LLMs make arithmetic errors. These tools don't replace thinking—they augment it:
- **SymPy**: Exact symbolic computation (no floating point drift)
- **Z3**: Exhaustive constraint checking
- **Lean 4** (optional, external): the compiler is the proof checker

## Development Pattern

Write the failing test first, then the implementation:

```
1. Research     → Read the library's API docs
2. Plan         → Write a short plan (see the writing-plans skill)
3. Red          → Write failing tests FIRST
4. Green        → Implement to pass tests
5. Review       → Review the implementation
6. Document     → Update the skills and TOOLS.md that reference it
```

## Key Decisions

| Decision | Why | Alternative Rejected |
|----------|-----|---------------------|
| Lean 4 for category theory | Z3 can't do abstract algebra | Keep broken Z3 commands |
| SymPy over NumPy | Exact symbolic, not floating point | Numerical approximations |
| Compiler-in-the-loop | Lean compiler = proof verifier | Manual proof checking |

## Extending the System

### Add New SymPy Command

1. Write a failing test for the new command (in the project's test suite)
2. Implement the function in `.agents/skills/math/scripts/cc_math/sympy_compute.py`
3. Add the CLI subparser
4. Wire it into the `main()` dispatch
5. Update `TOOLS.md`, `SKILL.md`, and any topic skill that references it

### Add New Math Topic Skill

1. Create `<category>/<topic>/SKILL.md` with `name`, `description`, when to use,
   a decision tree, and exact tool commands
2. Link it from the category `README.md` as `<topic>/SKILL.md`
3. If the script needs a new third-party package, declare it in the root
   `requirements.txt`
