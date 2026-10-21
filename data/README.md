# Tracked data

This folder is the project's tracked root for durable data: results that are
expensive or impossible to regenerate, such as paid jobs, runs on external
systems, or long simulations. Git tracks everything here, byte for byte. Do not
delete, overwrite, regenerate, or hand-edit anything in this folder. The rules
are in the
[data preservation policy](../docs/agent-guidance/data-preservation.md).

Regenerable outputs do not belong here; they go to the ignored `artifacts/`
folder.

## Adding a dataset

1. Write the dataset under `data/<source>/<run-id>/` from the start, with a
   manifest that records what produced it, when, on which backend or machine,
   and what it cost.
2. Add a row for it to the index below in the same change.
3. Tell the user that it is not yet committed.

## Datasets

No datasets yet.

| Dataset | Source | Produced by | Cost or wall time | Reported in |
| --- | --- | --- | --- | --- |
