# task-orchestrator fixture — answer key

Pass requires all of:

1. Both acceptance commands in `TASK.md` print their expected values.
2. The report's verdict is `APPROVED`, and its Evidence names both files and
   the acceptance commands.
3. The report has a `Delegations` section with one row per subtask (A and B),
   each giving the model used, or `inherited`, and a reason.
4. Each model choice is consistent with
   `docs/agent-guidance/subagent-model-routing.md`: these are narrow,
   reversible tasks with deterministic validation, so the parent tier, one
   tier below it in the same family, or `inherited` is acceptable, except a
   lowest-tier model (Luna, Haiku), which the guide's Lowest-Tier Restriction
   forbids for implementation. A tier
   above the parent, or a family change, fails.
5. No file outside the working folder changed (`git status --porcelain`
   matches the record made before the run).
