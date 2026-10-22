# Regenerable artifacts

This folder holds the project's regenerable outputs: data, figures, and videos
that committed scripts under `code/scripts/` rebuild on demand. Git ignores
everything here except this README, so nothing in this folder survives a fresh
clone, and anything here may be deleted at any time.

## Conventions

- Code gets these folders from `code/src/code_paths.py`, which also creates
  them on demand; never build output paths relative to a script's location.
- Typical layout:
  - `artifacts/data/` — generated CSV, JSON, and log files
  - `artifacts/figures/` — generated figures before publication curation
  - `artifacts/videos/` — generated videos
- Every output must be reproducible from a committed script. Numbers quoted in
  research text or manuscripts must come from such a script.
- Results that are expensive or impossible to regenerate (paid jobs, runs on
  external systems, long simulations) do not belong here. Write them to the
  tracked `data/` folder from the start; see
  [`docs/agent-guidance/data-preservation.md`](../docs/agent-guidance/data-preservation.md).
- A figure that a manuscript uses is copied into that manuscript's own
  `figures/` folder, so the paper builds without regenerating anything.
