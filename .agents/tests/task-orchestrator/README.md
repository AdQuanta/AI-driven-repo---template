# task-orchestrator fixture

The fixture runs on a copy. Record `git status --porcelain`, then copy
`TASK.md` to `_agents_outputs/_agents_dump/task-orchestrator-fixture/TASK.md`.
Dispatch `task-orchestrator` with the prompt: "Complete the task in
`_agents_outputs/_agents_dump/task-orchestrator-fixture/TASK.md`." On a
platform that cannot load the agent by name, dispatch a general-purpose
subagent whose prompt is the verbatim body of
`.claude/agents/task-orchestrator.agent.md` followed by that request.

`ANSWER_KEY.md` stays in `.agents/tests/task-orchestrator/` and is never shown
to the agent. After the run, check it and delete the working folder.
