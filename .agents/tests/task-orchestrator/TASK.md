# Orchestrator fixture task

Working folder: `_agents_outputs/_agents_dump/task-orchestrator-fixture/`
(it is git-ignored and already holds this file).

- **Subtask A:** create `alpha.txt` whose entire content is the single line
  `ALPHA_DONE`.
- **Subtask B:** create `beta.json` containing exactly the JSON object
  `{"status": "ok", "items": 3}`.

The subtasks are independent. Delegate each to its own subagent.

## Acceptance

Run from the repository root:

```text
python -c "import pathlib; print(pathlib.Path('_agents_outputs/_agents_dump/task-orchestrator-fixture/alpha.txt').read_text().strip())"
python -c "import json, pathlib; print(json.loads(pathlib.Path('_agents_outputs/_agents_dump/task-orchestrator-fixture/beta.json').read_text()))"
```

They must print `ALPHA_DONE` and `{'status': 'ok', 'items': 3}`.
