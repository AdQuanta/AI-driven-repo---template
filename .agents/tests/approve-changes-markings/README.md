# approve-changes-markings fixture

A small LaTeX paper with every approvable marker kind, an empty replacement,
an approved and a `missing` `markroles` field, and a `\Mark{missing}` that
must survive.

## Run

1. Copy the mock paper to a run folder at the same depth (the paper loads the
   markings module by a four-level relative path):

   ```bash
   R=_agents_outputs/_agents_dump/approve-changes-markings
   rm -rf "$R" && mkdir -p "$R" && cp -r .agents/tests/approve-changes-markings/mock-paper "$R/"
   ```

2. Ask for approval in plain words, for example "approve all changes in
   `_agents_outputs/_agents_dump/approve-changes-markings/mock-paper`", so the
   parent delegates to `approve-changes-markings`. On a platform that cannot
   load the agent by name, dispatch a general-purpose subagent whose prompt is
   the verbatim body of `.claude/agents/approve-changes-markings.agent.md`
   followed by that request.

3. Check the result against `ANSWER_KEY.md`.

Never run the agent on `mock-paper/` in place.
