# ai-judge fixture

Two cases with the same request. `case-incomplete` silently skips rule 4, and
its tests still pass. `case-complete` meets every rule.

## Run

For each case, copy it to a run folder, then dispatch `ai-judge`:

```bash
mkdir -p _agents_outputs/_agents_dump/ai-judge
cp -r .agents/tests/ai-judge/<case> _agents_outputs/_agents_dump/ai-judge/
```

Dispatch prompt:

> Judge the work in `_agents_outputs/_agents_dump/ai-judge/<case>/`. The
> original request is `REQUEST.md`, the work product is `work/`, and the
> validation output is `VALIDATION.txt`.

Check each verdict against `ANSWER_KEY.md`.
