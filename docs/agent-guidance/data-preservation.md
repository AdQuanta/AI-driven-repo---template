# Data Preservation

This policy decides where generated data lives and whether Git tracks it.
Read it before writing, moving, or deleting generated data.

## Two kinds of generated data

| | Regenerable outputs | Tracked data |
| --- | --- | --- |
| Folder | `artifacts/` | `data/` |
| Tracked by Git | No | Yes |
| Losing it costs | One rerun of a committed script | Money, external access, or long compute that may not be repeatable |
| May be deleted | Any time | Never without the user's explicit instruction |

Do not confuse the two folders named "data". The root `data/` folder is
tracked and holds results that must be kept. `artifacts/data/` is ignored
and holds regenerable CSV, JSON, and log files.

## Which kind is it?

Data belongs in `data/` when regenerating it needs any of the following:

- **Money or metered quota.** Paid cloud jobs, metered API calls, or
  instrument time are examples.
- **An external system whose state cannot be restored.** A run on shared
  hardware, a live service, or a field measurement depends on that day's
  conditions, so it can never be repeated exactly.
- **Long compute.** More than about one hour of wall-clock time for the
  full run.
- **Many manual trials.** Results that took repeated tuning, retries, or
  human judgment to obtain.

Everything else is a regenerable output: a figure, a table, a quick sweep,
or anything a committed script rebuilds in minutes.

When unsure, keep the data in `data/` and ask the user. Wrongly keeping a
small file costs nothing. Wrongly losing an irreplaceable run cannot be
undone.

## Rules for tracked data

1. **Write it under `data/` from the start.** Do not write it to
   `artifacts/` and move it later. Code gets the folder from
   `code_paths.data`.
2. **Get it into Git promptly.** As soon as tracked data exists and is not
   committed, tell the user so in plain words, so it can be committed before
   anything else touches it.
3. **Never delete, overwrite, or regenerate it.** A new run gets a new run
   ID and a new directory. A pending record may be completed. A completed
   result is never rewritten.
4. **Never edit it by hand.** Record a correction in a note next to the
   data, and leave the data unchanged.
5. **Keep provenance next to the data.** Record what produced it, when, on
   which backend or machine, and what it cost. A run manifest that holds
   these fields is enough.
6. **Keep secrets out.** No tokens, API keys, instance identifiers, or
   account identifiers. Check before committing.
7. **Mind the size.** For a single file above about 10 MB, or a dataset
   above about 50 MB, stop and ask the user how to store it. Do not fall
   back to `artifacts/`.
8. **Make it findable.** List each dataset in `data/README.md`, and name it
   in a tracked report or TODO.

Git stores `data/` byte for byte. `.gitattributes` turns off line-ending
conversion for the folder.

## Rules for regenerable outputs

- Write them under `artifacts/`, which Git ignores except its `README.md`.
- A committed script must be able to rebuild them. Numbers quoted in
  research text must come from such a script; see `research/AGENTS.md`.
- Figures, tables, and reports derived from tracked data are regenerable
  outputs. They stay in `artifacts/` until a write-up or manuscript curates
  them into its own folder.

## Layout of `data/`

- `data/README.md` — index of the datasets and their provenance.
- `data/<source>/` — one folder per data source, for example
  `data/<instrument-or-service>/`.

When a change adds a dataset, add it to the index in the same change.
