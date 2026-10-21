# Research Project Template

A GitHub repository template for AI-assisted research projects. It integrates
**code**, **research**, and **publications** in one repository, kept consistent
through one set of agent instructions that Codex, Claude Code, and GitHub
Copilot all read from the same canonical files.

The template carries infrastructure only, with no research content: agent
instructions and custom agents, a literature knowledge-base workflow with
citation auditing, LaTeX manuscript conventions with a change-marking module,
portable skills, and portability rules. A new project adds its own subject,
code, papers, and data.

## What's included

| Layer | What you get |
| --- | --- |
| **Agent instructions** | Root [`AGENTS.md`](AGENTS.md) plus sector files [`code/AGENTS.md`](code/AGENTS.md), [`research/AGENTS.md`](research/AGENTS.md), and [`publications/AGENTS.md`](publications/AGENTS.md). [`CLAUDE.md`](CLAUDE.md) only imports `@AGENTS.md`. |
| **Guidance docs** | [`docs/agent-guidance/`](docs/agent-guidance/): project layout, cross-platform AI support, data preservation, subagent model routing, Git policy, the LaTeX build environment, and the reusable-project blueprint. |
| **TODO queue** | [`docs/todo/`](docs/todo/README.md): one dated file per topic, with resolved items archived. |
| **Skills** | [`.agents/skills/`](.agents/skills/docs/registry.md): brainstorming, writing-plans, subagent-driven-development, math, latex-build, latex-paper-en, literature-review, research-gap-explorer, and skill-maintenance. |
| **Custom agents** | [`.claude/agents/`](.claude/agents/): the literature workflow (`ingest-paper`, `find-papers`, `citation-audit`, `citation-reader`, `citation-checker`) plus `task-orchestrator`, `ai-judge`, and `approve-changes-markings`. Each has a fixture under [`.agents/tests/`](.agents/tests/). |
| **Knowledge base** | An empty `research/references/scientific_papers/`, the tag index under `research/references/indexes/tags/`, and the tooling in [`research/references/src/`](research/references/src/README.md). |
| **LaTeX** | The Mark API in [`publications/modules/markings/`](publications/modules/markings/) and a compilable [`publications/paper---example/`](publications/paper---example/). |
| **Code sector** | `code/src/code_paths.py` with its test, and empty `code/scripts/data/` and `code/scripts/figures/`. |
| **Durable roots** | Tracked [`data/`](data/README.md) for irreplaceable results; ignored [`artifacts/`](artifacts/README.md) for regenerable outputs; `_agents_outputs/` for agent reports. |
| **Editor and CI** | Machine-independent [`.vscode/`](.vscode/) LaTeX settings and tasks; [`.github/workflows/tests.yml`](.github/workflows/tests.yml) runs the tests, the discovery setup, and a TeX Live build of the example paper. |

## First clone

Create the repository from the template (**Use this template** > **Create a
new repository**) and clone it. Then run these steps once, from the repository
root. Python 3.11 or newer is assumed.

1. **Create the root virtual environment and install the shared
   dependencies.** One root `.venv` serves every sector and skill.

   Windows (PowerShell):

   ```powershell
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

   Linux or macOS:

   ```sh
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   ```

2. **Set up skill discovery for Claude Code.** This creates the ignored
   `.claude/skills` link to `.agents/skills/`. Codex and Copilot need no setup.

   Windows (PowerShell):

   ```powershell
   & .\.claude\setup-discovery.ps1
   ```

   If script execution is blocked, run
   `powershell -ExecutionPolicy Bypass -File .claude/setup-discovery.ps1`
   instead.

   Linux or macOS:

   ```sh
   sh .claude/setup-discovery.sh
   ```

   Under Git Bash on Windows, use the PowerShell script: Git Bash's `ln -s`
   copies the folder instead of linking it, so the shell script refuses to run
   there. A second run reports that the link is already configured. Keep
   editing skills in `.agents/skills/`; never add files under `.claude/skills`.
   Details and recovery steps are in
   [`docs/agent-guidance/cross-platform-ai-support.md`](docs/agent-guidance/cross-platform-ai-support.md).

3. **Describe the project.** Replace the placeholder under
   "What Is This Project About?" in [`AGENTS.md`](AGENTS.md).

No absolute paths need editing: agents and tools resolve the repository root
themselves.

## Layout

The maintained map is
[`docs/agent-guidance/project-layout.md`](docs/agent-guidance/project-layout.md).
In short:

```text
AGENTS.md, CLAUDE.md     root instructions (CLAUDE.md = @AGENTS.md)
README.md                this file
requirements.txt         root dependency manifest for .venv
.agents/skills/          project skills and their registry
.agents/tests/           agent fixtures, one folder per agent
.claude/agents/          custom agents, read by all three platforms
.claude/setup-discovery.ps1, .sh
                         create the ignored .claude/skills link
.github/workflows/       CI
.vscode/                 LaTeX settings, tasks, and build scripts
code/                    src/, scripts/, tests/, AGENTS.md
research/                derivations/, references/ (knowledge base + tooling), AGENTS.md
publications/            modules/markings/, paper---example/, AGENTS.md
docs/                    agent-guidance/, todo/
data/                    tracked, irreplaceable results
artifacts/               regenerable outputs (ignored except README.md)
_agents_outputs/         agent reports for humans (_agents_dump/ ignored)
```

## Verify the setup

Run these from the repository root with the root `.venv` active, or call its
interpreter by path (`.venv\Scripts\python.exe` on Windows,
`.venv/bin/python` on Linux or macOS).

- **Code tests**, run from `code/`:

  ```sh
  cd code
  python -m pytest
  cd ..
  ```

- **Knowledge-base tooling tests:**

  ```sh
  python -m pytest research/references/src
  ```

- **Marker-finder tests:**

  ```sh
  python -m pytest publications/modules/markings/scripts
  ```

- **Agent fixtures:** each folder under [`.agents/tests/`](.agents/tests/) has
  a `README.md` with the request to give the agent and the expected result:
  [`citation-audit`](.agents/tests/citation-audit/README.md),
  [`ai-judge`](.agents/tests/ai-judge/README.md),
  [`task-orchestrator`](.agents/tests/task-orchestrator/README.md), and
  [`approve-changes-markings`](.agents/tests/approve-changes-markings/README.md).

- **Example paper:** build `publications/paper---example/` with the recipe in
  [`docs/agent-guidance/vscode-latex-environment.md`](docs/agent-guidance/vscode-latex-environment.md):
  the `LaTeX: Full Build Sequence` task or `.vscode\latex-full-build.ps1` on
  Windows with MiKTeX, or the TeX Live sequence on Linux and macOS. A TeX
  distribution with `pdflatex` and `biber` is required. The build must finish
  with no undefined citations or references.

CI runs the same tests, the discovery setup, and the paper build on every push
to `main` and on pull requests.

## Adapting to a new project

Work through the **New-Project Adaptation Checklist** in
[`docs/agent-guidance/reusable-research-project-blueprint.md`](docs/agent-guidance/reusable-research-project-blueprint.md).
It covers the project statement, the layout map, the environment, the skills,
the literature workflow, the knowledge base, and CI, with a validation step for
each.

Personal working preferences, such as whether agents may commit or a preferred
coding style, are deliberately absent from the project instructions. Keep them
in your own user-level agent configuration.
