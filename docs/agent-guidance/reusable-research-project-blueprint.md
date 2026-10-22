# Reusable Research-Project Blueprint

This document is the portability standard that this template implements. Read
it when you **start a new project from the template**, or when you **bring the
standard into an existing repository**. It lists the assets that make up the
standard, what each one depends on, how to prove that your copy works, and what
must stay out of the repository.

## How To Read The Tables

Every asset table in this document uses exactly these columns:

| Path | Adoption | Dependencies | Validation | Notes |
| --- | --- | --- | --- | --- |
| *(path relative to the template root)* | `copy-and-adapt`, `optional`, or `do-not-copy` | what must already exist for the asset to work | a concrete command or check that proves the copy works | what to change, and what breaks if you do not |

Adoption values mean:

- `copy-and-adapt`: part of the starter standard. It ships in the template.
  Adapt its project-specific parts before first use. To bring the standard into
  an existing repository, copy it from the template to the same path.
- `optional`: useful, but only after an explicit portability review (see
  `Optional Capability Packs`).
- `do-not-copy`: must not be imported into a project from anywhere else, such
  as another project or an earlier repository. It is absent from the template
  and must stay absent.

Keep every asset at the **same relative path** it has in the template unless a
row says otherwise. Paths are load-bearing: agents, instructions, and scripts
refer to each other by relative path, so moving one asset silently breaks the
others.

Values marked *Observed* were recorded by running the check in the template
itself (Windows, root `.venv` on Python 3.12) when this document was last
revised. Re-run a check after any change to the asset it covers. Commands are
written for Windows PowerShell with `.venv\Scripts\python.exe`. On Linux or
macOS, use `.venv/bin/python` and the equivalent shell commands.

## Shared Validation Snippets

Rows below refer to these checks **by name**. Each is a literal Windows
PowerShell 5.1 command; run it from the repository root. They are defined here
rather than inside table cells because their regular expressions and pipelines
contain `|`, which would break the Markdown tables.

**A check that has never reported a hit is unproven.** A scan that reports
clean may be clean, or it may be unable to match anything. Before trusting a
clean result, run the same command once with a term you know is present, and
confirm that it reports a hit.

**path check**: does the asset exist where the files that use it expect it?

```powershell
Test-Path <path>
```

Must return `True`. *Observed:* `True` for every path this document names as
shipped in the template. The one expected exception is `.claude/skills`, which
is created by a setup script after cloning (see `Core Instructions and
Guidance`).

**project-name scan**: does an imported file still carry the nouns of the
project it came from?

```powershell
Select-String -Path <path> -Pattern '<old-project-name>|\b<OLD-ACRONYM>\b|<old-domain-term>'
```

Fill in the names of whatever project you import from: its name, its acronym,
and its most distinctive domain terms. Two rules:

- `Select-String` is **case-insensitive by default**, so list each term once.
  `Example-Project|example-project` is redundant.
- Keep terms specific. A bare `alpha` also matches "alphabet", "alphanumeric",
  and "alpha release". Wrap short acronyms in `\b...\b` so they do not match
  inside ordinary words. A check that reports false alarms is a check people
  learn to ignore.

Must return nothing in the adopting project. To prove the command form works,
run it once with a term known to be present. *Observed:*
`Select-String -Path AGENTS.md -Pattern 'spawn_agent'` returns 1 hit.

**recursive content scan**: the same idea over a directory tree.

```powershell
Get-ChildItem <dir> -Recurse -Filter <glob> | Select-String -Pattern '<terms>'
```

This form avoids two traps, each of which produces a check that **cannot
fail**:

- `Select-String` has **no `-Recurse` parameter**. `(Get-Command
  Select-String).Parameters.Keys -contains 'Recurse'` returns `False`, and
  passing it is a hard error, not a silent no-op.
- `Select-String` takes **.NET regex**, not grep BRE. Alternation is `a|b`.
  Writing `a\|b` matches the literal three-character string `a|b` and therefore
  matches nothing.

A non-recursive `-Path <dir>\*.md` glob fails silently one level down.
*Observed:* `Get-ChildItem .agents\skills\*.md` matches **0** files, while
`Get-ChildItem .agents\skills -Recurse -Filter *.md` matches more than a
hundred.

**link scan**: does every relative Markdown link in a file resolve?

```powershell
$d = Split-Path -Parent (Resolve-Path <path>)
Select-String -Path <path> -Pattern '\]\(([^)]+)\)' -AllMatches |
  ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value } |
  Where-Object { $_ -notmatch '^(https?:|mailto:|#)' -and $_ -notmatch '[<>*?|]' } |
  ForEach-Object { $t = ($_ -split '#')[0]
                   if ($t -and -not (Test-Path (Join-Path $d $t))) { "BROKEN: $t" } }
```

Must print nothing. The `[<>*?|]` filter skips documentation placeholders such
as `<citation-key>`, which are not real links. *Observed:* clean on every
Markdown file in the template.

**tracked-residue scan**: has a cache or build intermediate reached Git?

```powershell
git ls-files --cached --others --exclude-standard |
  Select-String -Pattern '(__pycache__/|\.pyc$|\.pytest_cache/|node_modules/|\.aux$|\.bbl$|\.latex_build/)'
```

Must print nothing. It lists only files that Git tracks or would track, so
ignored local runs (for example fixture copies under
`_agents_outputs/_agents_dump/`) do not count. *Observed:* nothing.

---

## Core Repository Structure

The template has three research sectors (`code/`, `research/`,
`publications/`) and shared operational directories. Everything else in this
blueprint assumes they exist at these paths.

| Path | Adoption | Dependencies | Validation | Notes |
| --- | --- | --- | --- | --- |
| `code/` | `copy-and-adapt` | The root `.venv`; `code/pytest.ini` (`testpaths = tests`, `pythonpath = src`); `code/requirements.txt` | **path check** on `code\src\code_paths.py` and `code\tests\test_code_paths.py`; then `Push-Location code; ..\.venv\Scripts\python.exe -m pytest -q; Pop-Location` exits `0`. *Observed:* `True`, `True`, then `6 passed`, exit `0` | Ships `code/src/code_paths.py` with its test and empty `code/scripts/data/` and `code/scripts/figures/`. Add the project's own code beside them. Keep at least one test: with an empty `code/tests/`, pytest exits `5` ("no tests collected") and the CI code job fails. |
| `research/` | `copy-and-adapt` | Nothing beyond the directory itself | **path check** on `research\derivations` and `research\references\scientific_papers`. *Observed:* `True`, `True` | Ships an empty `derivations/`, an empty knowledge base, the tag index, and the knowledge-base tooling. Add `notes/` and `progress/` when first needed, and record them in `docs/agent-guidance/project-layout.md` in the same change, as `research/AGENTS.md` requires. |
| `research/derivations/` | `copy-and-adapt` | The citation rule in `research/AGENTS.md`; relative links into `research/references/scientific_papers/**/summary.md` | `Get-ChildItem research\derivations -Recurse -Filter *.md` returns nothing until the project writes its first derivation; afterwards, the **link scan** on each derivation prints nothing. *Observed:* 0 files | One `kebab-case` subfolder per topic, each holding one or more descriptively named Markdown files. Math in Markdown uses `$...$` and `$$...$$`. Never import another project's derivations (see `Files and Content That Must Not Be Copied`). |
| `research/references/scientific_papers/` | `copy-and-adapt` | The literature agents (see `Mandatory Literature Knowledge-Base Workflow`); one `summary.md` per citation-key folder | **path check** → `True`; then `Get-ChildItem research\references\scientific_papers -Recurse -Include *.pdf,summary.md` returns nothing in a fresh project. *Observed:* `True`, 0 files | Ships empty (a `.gitkeep` only). Keep the **structure and rules**; let the project's own ingests fill it. See `Paper Taxonomy Rules` below. |
| `publications/` | `copy-and-adapt` | A TeX distribution with `pdflatex` and `biber`; the build recipe in `docs/agent-guidance/vscode-latex-environment.md` | **path check** on `publications\modules\markings\markings.tex` and `publications\paper---example\main.tex`. *Observed:* `True`, `True`. Then build the example manuscript (see `Publication Baseline`) | Ships the markings module and the example manuscript. Each manuscript gets its own `publications/paper---<slug>/`; venue copies may be grouped under `publications/submissions/<VENUE>/paper---<slug>/`. Decide the marking policy and venue conventions in `publications/AGENTS.md` before first use. |
| `docs/agent-guidance/` | `copy-and-adapt` | Root and sector `AGENTS.md` files that cite these documents by relative path | **path check** on `docs\agent-guidance\project-layout.md`; then the **link scan** on every file in the directory. *Observed:* `True`, and the link scan is clean | Ships `project-layout.md`, `cross-platform-ai-support.md`, `data-preservation.md`, `git-policy.md`, `subagent-model-routing.md`, `vscode-latex-environment.md`, and this blueprint. Keep them current as the project's paths change. |
| `docs/todo/` | `copy-and-adapt` | `docs/todo/README.md`; `docs/todo/resolved/`; relative links to the sector instruction files | **path check** on `docs\todo\README.md` and `docs\todo\resolved`; then `Get-ChildItem docs\todo -Filter *.md` lists only `README.md` in a fresh project. *Observed:* `True`, `True`, and only `README.md` | Keep the queue conventions: one topic per file named `YYYY-MM-DD-<kebab-case-topic>.md`, the fixed `**Status:**` values, and terminal files moved to `resolved/`. Never import another project's task files. |
| `artifacts/` | `copy-and-adapt` | Generation scripts under `code/scripts/`; the `.gitignore` rules `/artifacts/*` and `!/artifacts/README.md` | **path check** on `artifacts\README.md`; `git check-ignore -v artifacts/x` prints the ignoring rule; `git check-ignore -q artifacts/README.md` exits `1` (the README is not ignored). *Observed:* `True`, `.gitignore:104:/artifacts/*`, exit `1` | Regenerable data, figures, and videos; `code_paths` creates `artifacts/data/`, `artifacts/figures/`, and `artifacts/videos/` on demand. Keep the `/artifacts/*` form: Git cannot re-include a file under a directory rule such as `/artifacts/`, so that form would also ignore the README. |
| `data/` | `copy-and-adapt` | `docs/agent-guidance/data-preservation.md`; the `/data/** -text` and `/data/README.md text` rules in `.gitattributes`; `code_paths.data` | **path check** on `data\README.md`; `git check-ignore -v data` prints nothing; `git check-attr text data/x.json` prints `text: unset`. *Observed:* `True`, nothing, `data/x.json: text: unset` | Results that are expensive or impossible to regenerate. Git tracks the folder byte for byte. Ships with only its README, whose dataset index starts empty. |
| `_agents_outputs/` | `copy-and-adapt` | The root `AGENTS.md` output-location rule; the ignore rule `_agents_outputs/_agents_dump/` | `git ls-files _agents_outputs` lists only `_agents_outputs/.gitkeep`; `git check-ignore -v _agents_outputs/_agents_dump` prints the ignoring rule. *Observed:* `.gitkeep` only; `.gitignore:108:_agents_outputs/_agents_dump/` | Human-facing agent reports, with `_agents_dump/` for temporary evidence and fixture runs. The folder is not maintained: maintained files must not link into it; promote durable content to `docs/` instead. |

### Paper Taxonomy Rules

The knowledge-base *taxonomy rules* are part of the standard; another
project's *categories* are not.

- The paper taxonomy **starts empty**. Create no category folders until the
  first paper is ingested, then record each new top-level field in the
  "Category Hierarchy" list of `research/AGENTS.md`.
- Keep the taxonomy **flat while it is small**: citation-key folders sit
  directly inside a top-level field until that field grows past roughly a dozen
  papers.
- **Classify by primary contribution**, not by tangential mentions: a paper goes
  where its main result belongs.
- **Avoid one-paper categories.** A category that would hold a single paper is
  merged into the closest related one.
- **Subdivide only as diversity grows.** Do not pre-create empty sub-categories
  in anticipation.
- **Limit nesting** to `field/sub-category/citation-key/`. If a sub-category
  itself outgrows its bounds, split the top-level field into sibling fields
  rather than adding a third level.
- **Reorganize earlier papers when needed.** Subdividing a field means moving
  the already-ingested papers into the new sub-categories and repairing every
  relative link that pointed at them.
- **Do not import another project's categories.** A taxonomy built for a
  different subject fits none of the incoming papers, and the ingest agent will
  silently mis-file papers to satisfy it.

### Reusable Literature Tag Index

This workflow ships with the literature agents. It adds overlapping tag
navigation without replacing primary-contribution folder classification. The
inline `tags` arrays in each summary are authoritative; tags use ASCII lowercase
`snake_case`, and accurate accepted tags are reused before new concepts are
proposed.

| Path | Adoption | Dependencies | Validation | Notes |
| --- | --- | --- | --- | --- |
| [research/references/src/](../../research/references/src/) | `copy-and-adapt` | Python standard library; pytest; its own `pytest.ini` (`pythonpath = .`) | `.venv\Scripts\python.exe -m pytest research/references/src -q` exits `0`. *Observed:* `468 passed`, exit `0` | Knowledge-base tooling lives beside the knowledge base, not in `code/`, and imports nothing from `code/`. It holds `kb_paths.py` (repository root from a `.git` directory or file, with a fixed-location fallback), the `literature_tags/` and `find_papers/` packages, both entrypoints, `README.md`, and `tests/`. The summary heading `## Relevance to the project` is fixed. `find_papers/gather.py` (`RELEVANCE_HEADING`), `tests/test_find_papers_gather.py`, the summary template in `ingest-paper`, and the scoring rules in `find-papers` all name it; if it is ever renamed, change all four in the same change. |
| [research/references/src/generate_literature_tag_index.py](../../research/references/src/generate_literature_tag_index.py) | `copy-and-adapt` | The package beside it and `kb_paths.py` | `.venv\Scripts\python.exe research/references/src/generate_literature_tag_index.py --check` exits `0`. *Observed:* exit `0` on the shipped empty index | Thin entrypoint. It sits beside its package, so it needs no `sys.path` setup. The CI `kb-and-markings-tests` job runs the same `--check`. |
| [research/references/src/gather_summaries.py](../../research/references/src/gather_summaries.py) | `copy-and-adapt` | `find_papers/` and `kb_paths.py` | `.venv\Scripts\python.exe research/references/src/gather_summaries.py` prints the corpus path and paper count, and exits `0`. *Observed:* `0 papers, 0 warnings`, exit `0` | Writes the `find-papers` corpus to `_agents_outputs/_agents_dump/find-papers-corpus.md`. |
| [research/references/indexes/tags/README.md](../../research/references/indexes/tags/README.md) | `copy-and-adapt` | Matching source and index paths and generator commands | **link scan** → nothing; then `--check` exits `0` | Maintained operator guidance: modes, exit codes, bootstrap, and generated-file safety. Not generated. |
| [research/references/indexes/tags/index.md](../../research/references/indexes/tags/index.md) as shipped (header-only, no `by_tag/` pages) | `copy-and-adapt` | The generator; the project's own summaries | `--check` exits `0`. *Observed:* exit `0` | The empty bootstrap: the generated marker, the heading, and an empty table. It holds no vocabulary. Regenerate it; never edit it by hand. |
| Another project's generated `index.md` and `by_tag/` pages | `do-not-copy` | — | `Get-ChildItem research\references\indexes\tags\by_tag -ErrorAction SilentlyContinue` returns nothing until the project's own first accepted tags. *Observed:* nothing (no `by_tag/` folder) | Never import another project's accepted vocabulary or tag pages. Regenerate from the project's own literature. |

From the repository root, using the project's Python environment:

```powershell
.venv\Scripts\python.exe -m pytest research/references/src -q
.venv\Scripts\python.exe research/references/src/generate_literature_tag_index.py
.venv\Scripts\python.exe research/references/src/generate_literature_tag_index.py --accept-new-tags
.venv\Scripts\python.exe research/references/src/generate_literature_tag_index.py --check
```

The template already ships the empty bootstrap index, so a project started from
it needs no bootstrap step. When bringing the standard into a repository that
has no `index.md`, create `research/references/indexes/tags/` first and run
`--accept-new-tags` once to bootstrap; default and check modes exit `1` with
`bootstrap_required` until then.

After the first ingests, run normal generation. Inspect every unseen tag and
every similar-tag suggestion, correct variants, and explicitly accept only
justified new concepts: `--accept-new-tags` accepts **all** unseen valid tags.
Always finish with `--check`. The ingest report includes canonical tags,
whether the index was refreshed and checked, and links to the relevant tag
pages.

The generated `index.md` is the accepted snapshot, **not a separately
maintained registry**; never edit it or the tag pages by hand. Required
`citation_key` and `short_cite` values are nonempty, printable, control-free
single-line strings, including after decoding quoted YAML escapes. The accepted
table ends at the first non-pipe line; fenced examples outside the interface
are ignored by vocabulary parsing, while formatting drift is stale output.
Check compares decoded logical text with CRLF normalized to LF, not raw bytes.
See the [operator README](../../research/references/indexes/tags/README.md) for
the schema, exit codes, and marked-file safety. Re-run these gates after every
change to the tooling; the observed results above do not prove that a changed
copy works.

---

## Core Instructions and Guidance

These are the always-loaded instruction files. They have the highest leverage
of any asset, and they are where project-specific rules accumulate.

**Validation for every row in this table** is the same three-part check, run
from the repository root against each file:

1. the **path check**: the file exists where the files that use it expect it;
2. the **project-name scan**: no nouns from a project you imported from
   survive in it;
3. the **link scan**: every relative Markdown link in it resolves.

All three are defined in `Shared Validation Snippets` above. The path check
must return `True`; the other two must return nothing. Also confirm that every
backticked repository path a file names exists: these files cite most
documents as backticked paths rather than links, and the link scan does not see
those. Do not substitute a directory-existence check for these checks: an
instruction file that points at a missing guidance document degrades every
later agent turn without ever failing loudly.

*Observed for every row below:* the path check returns `True`, and the link
scan is clean. Every backticked repository path in the root and sector
`AGENTS.md` files and in `docs/todo/README.md` exists, except `.claude/skills`,
which is created after cloning.

| Path | Adoption | Dependencies | Validation | Notes |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | `copy-and-adapt` | `docs/agent-guidance/project-layout.md`, `docs/agent-guidance/cross-platform-ai-support.md`, `docs/agent-guidance/data-preservation.md`, `docs/agent-guidance/git-policy.md`, `docs/agent-guidance/subagent-model-routing.md`, `docs/agent-guidance/vscode-latex-environment.md`, `docs/todo/README.md`, the sector `AGENTS.md` files, `.agents/skills/docs/registry.md`, and `.agents/skills/skill-maintenance/SKILL.md`, all cited by relative path | The three checks. **Plus** `Select-String AGENTS.md -Pattern 'spawn_agent'` returns exactly 1 hit if Codex is a supported harness, and `Select-String AGENTS.md -Pattern 'Replace this paragraph'` returns nothing once the project statement is written. *Observed:* `spawn_agent` 1 hit; the placeholder 1 hit, by design, until a project replaces it | Root always-on instructions. Replace the placeholder under "What Is This Project About?" with two or three sentences on the research question, approach, and intended outcome. Keep "Sector Instruction Loading", "Output Locations", "Git Safety", and "Custom Agents And Multi-Platform Discovery". Dropping the last section silently removes Codex agent support (see `docs/agent-guidance/cross-platform-ai-support.md`). |
| `code/AGENTS.md` | `copy-and-adapt` | `code/src/code_paths.py`, `code/tests/`, `code/pytest.ini`, `code/requirements.txt`, the root `requirements.txt`, and the root `.venv` | The three checks | Keep the `artifacts/`, `data/`, and `code_paths` conventions; the rule to declare each import in both `code/requirements.txt` and the root `requirements.txt`; the test layout (`code/tests/test_<module>.py`, no `sys.path` shims because `pytest.ini` sets `pythonpath = src`); the canonical command `python -m pytest` run from inside `code/`; and the completion gate. Add the project's own domain rules. Personal coding-style rules stay out (see `Files and Content That Must Not Be Copied`). |
| `research/AGENTS.md` | `copy-and-adapt` | `research/references/scientific_papers/`, `research/references/src/`, the tag index, the `find-papers` and `ingest-paper` agents | The three checks | Keep the citation-by-relative-link rule, the taxonomy and sub-categorization rules, the tag workflow, and the reproducible-numbers rule. Record top-level fields in its "Category Hierarchy" list as they appear; it ships with *(no categories yet)* and an illustration-only example that names folders which do not exist. |
| `publications/AGENTS.md` | `copy-and-adapt` | The markings module; `publications/paper---example/`; the build recipe in `docs/agent-guidance/vscode-latex-environment.md`; the `approve-changes-markings` agent | The three checks | Keep the separation between authored sources and generated artifacts and the Definition of Done gates. Its marking policy requires every `.tex`/`.bib` change to be wrapped with the Mark API, forbids nested markers, and allows exactly one role per `markroles` field; review that policy and the venue conventions before first use. |
| `docs/agent-guidance/project-layout.md` | `copy-and-adapt` | Must match the directories that actually exist | The three checks. **Plus** a fourth, specific to this file: every path the map names exists. *Observed:* all 36 named paths exist except `.claude/skills`, which the setup script creates | This is the map the root instructions point at. Update it in the same change that adds, removes, moves, or renames a directory it shows. Paths created on demand (`.claude/skills`, `_agents_outputs/_agents_dump/`, the `artifacts/` subfolders, and the optional examples `research/notes/` and `publications/presentations/`) are the only accepted gaps. |
| `docs/todo/README.md` | `copy-and-adapt` | `docs/todo/` and the sector instruction files it links to | The three checks | Keep the naming scheme, the one-topic-per-file rule, the status values, and the closing procedure. TODO checkbox and closure ownership rules are personal preferences and stay out. |
| `CLAUDE.md` | `optional` | A harness that reads `CLAUDE.md` and supports `@`-file inclusion | The three checks. **Plus** `Get-Content CLAUDE.md` prints exactly `@AGENTS.md` and nothing else. *Observed:* `@AGENTS.md` | Ships in the template. Keep it if the project uses Claude Code; otherwise delete it together with both `.claude/setup-discovery.*` scripts, the `/.claude/skills` ignore rule, and the CI `discovery-setup` job. The whole file is the one-line shim `@AGENTS.md`, so `AGENTS.md` stays the single source of truth. A shim that grew a second line is no longer a shim. It makes one file visible to a second harness; it is **not** a promise of feature parity between Claude Code, Copilot, and Codex (see `docs/agent-guidance/cross-platform-ai-support.md`). |
| `.claude/setup-discovery.ps1` and `.claude/setup-discovery.sh` | `copy-and-adapt` | Canonical `.agents/skills/`; a real `.claude/agents/` directory; the ignore rule `/.claude/skills` **without** a trailing slash (Git records a Linux/macOS symlink as a file, and a trailing-slash rule matches directories only); PowerShell 5.1+ for the `.ps1`, POSIX `sh` for the `.sh`; the `.gitattributes` rule `*.sh text eol=lf`, so the `.sh` keeps LF in Windows clones | Windows: run `& .\.claude\setup-discovery.ps1` twice; the first run creates the junction and the second reports it already configured. Linux/macOS: run `sh .claude/setup-discovery.sh` twice with the same result, then `test -L .claude/skills`. Both: `git check-ignore -v .claude/skills` prints the rule and `git status --porcelain` stays empty. The `.sh` refuses to run under Git Bash, MSYS, or Cygwin, where `ln -s` silently copies the folder. *Observed:* `.gitignore:113:/.claude/skills`; `git check-attr eol .claude/setup-discovery.sh` prints `eol: lf`. The scripts were not run here; CI's `discovery-setup` job runs the `.sh` | Both scripts share one contract: check `.claude/agents/` and `.agents/skills/` first; leave a correct link alone; refuse, and never delete, a wrong link or a real directory, giving a recovery hint; confirm the new link resolves; print one line. Rules and rationale: `docs/agent-guidance/cross-platform-ai-support.md`. |
| `docs/agent-guidance/cross-platform-ai-support.md` | `copy-and-adapt` | `.claude/agents/`; both `.claude/setup-discovery.*` scripts and `CLAUDE.md` if Claude Code is supported | The three checks. **Plus** run its `Verification` table on each platform the project uses | Cited by `AGENTS.md` and `README.md`. Delete the matrix columns, rules, and checks for platforms the project does not use. It records that the template ships no `.claude/settings.json`: permission allowlists are per-user and belong in user-level configuration or the ignored `.claude/settings.local.json`. Record the outcome of its per-platform checks, for example in a TODO under `docs/todo/`. |

---

## Mandatory Skills

`.agents/skills/` is the directly maintained skill location: one owned copy per
skill, edited in place, with no generated or vendored duplicates. The template
ships the eight starter skills below plus `skill-maintenance` and the registry.
When you bring a skill in from elsewhere, copy the whole skill directory (not
just `SKILL.md`), preserve its `author`/`source` frontmatter, and register it in
`.agents/skills/docs/registry.md`. If Claude Code is a supported harness, run
the setup script for your OS (`.claude/setup-discovery.ps1` on Windows,
`.claude/setup-discovery.sh` on Linux/macOS) so these canonical skills resolve
under their bare names without a copied `.claude/skills/` tree.

Skill scripts run from the repository root with the root `.venv` interpreter.
`uv` is optional for every shipped skill. *Observed:* `uv` is not installed on
the machine that recorded these values, and none of the checks below needed it.

| Path | Adoption | Dependencies | Validation | Notes |
| --- | --- | --- | --- | --- |
| `.agents/skills/latex-paper-en/` | `copy-and-adapt` | The root `.venv` (its scripts use only the standard library); a TeX distribution providing `latexmk`, `pdflatex`/`xelatex`, `bibtex`/`biber`, and `chktex` on `PATH`; the bundled `scripts/`, `references/`, `examples/`, `evals/`, and `agents/openai.yaml` | **path check** on `.agents\skills\latex-paper-en\SKILL.md` → `True`; then, in a scratch copy of a manuscript under `_agents_outputs/_agents_dump/`, `.venv\Scripts\python.exe -B .agents/skills/latex-paper-en/scripts/compile.py <main.tex>` exits `0` and emits a PDF. The compile leg was not run here | Every module command is `python -B .agents/skills/latex-paper-en/scripts/<script>.py` with repository-relative paths, so no `$SKILL_DIR` variable is needed. Review the harness-specific `allowed-tools` list: its `Bash(python *)`-style patterns are parsed by only some harnesses. For papers under `publications/`, the build recipe in `docs/agent-guidance/vscode-latex-environment.md` overrides the skill's generic compile defaults, as `publications/AGENTS.md` states. |
| `.agents/skills/latex-build/` | `copy-and-adapt` | `latexmk` on `PATH`; a PDF viewer that supports SyncTeX reload | **path check** on `.agents\skills\latex-build\SKILL.md` → `True`; `Get-Command latexmk` resolves (`command -v latexmk` on Linux/macOS). *Observed:* `True`; `latexmk` resolves. Then, in a scratch folder under `_agents_outputs/_agents_dump/`, `latexmk -pdf <stub>.tex` exits `0`, and `latexmk -pvc -pdf <stub>.tex` rebuilds on edit and reloads in the viewer. The stub legs need a GUI and were not run here | Gives Windows, Linux, and macOS commands and viewers. Bare `latexmk` puts intermediates beside the sources, which the repository's LaTeX guide forbids for manuscripts; the skill itself says the guide takes precedence for papers in this repository. Use its generic workflow only for standalone documents or scratch builds. |
| `.agents/skills/literature-review/` | `copy-and-adapt` | The root `.venv` with `requests` (declared in section 1 of the root `requirements.txt`) for `scripts/verify_citations.py`; pandoc and a LaTeX engine for `scripts/generate_pdf.py`; the harness's web-search and web-fetch tools | **path check** on `.agents\skills\literature-review\SKILL.md` → `True`; then each of `search_databases.py`, `verify_citations.py`, and `generate_pdf.py` under `.agents\skills\literature-review\scripts\` exits `0` with `--help`. *Observed:* `True`; all three exit `0`. Then generate one review end to end into the project's chosen output folder | Visual elements are optional (Mermaid, TikZ, or matplotlib); no figure-generation skill is required. Domain clients such as `gget`, `bioservices`, and `datacommons-client` are optional and are not declared. Its database list leans biomedical; point it at the project's fields. Save reviews where the project keeps research notes, never inside the skill folder. |
| `.agents/skills/research-gap-explorer/` | `copy-and-adapt` | A live web-search tool (and web-fetch tool) in the target harness | **path check** on `.agents\skills\research-gap-explorer\SKILL.md` → `True` (*Observed:* `True`); then ask the skill for research vectors on a known topic and require that every entry in its "Raw Materials" list resolves when opened. This leg needs live network access and was not run here; treat an unrun check as an unverified adoption | The skill requires "the harness's web-search tool" and tells the agent to say so and stop if none is available, rather than fall back to training data. Confirm the target harness exposes such a tool. |
| `.agents/skills/brainstorming/` | `copy-and-adapt` | `scripts/server.js`, `scripts/helper.js`, `scripts/frame-template.html`, `scripts/start-server.sh`, and `scripts/stop-server.sh` (Node.js and a POSIX shell) for the visual companion; a general-purpose subagent dispatched with `spec-document-reviewer-prompt.md`; the `writing-plans` skill | **path check** on `.agents\skills\brainstorming\SKILL.md` → `True` (*Observed:* `True`); then dispatch the spec-review step once and require the general-purpose reviewer, using `spec-document-reviewer-prompt.md`, to return a review; run `scripts/start-server.sh` only if the visual companion is used. Neither behavioural leg was run here; both need a live harness, and the companion also needs Node and a POSIX shell | Writes specs to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`; the matching plan goes to `docs/superpowers/plans/`. `docs/superpowers/` does not ship; add it to the layout map when it is first created. **Keep the spec root and the plan root in the same tree**: if you move one, move the other. Do not make the root conditional on an output root declared in `AGENTS.md`; that once sent specs to an unmaintained directory while plans stayed in `docs/`. The skill carries no commit policy in either direction; each user's own agent configuration decides. The visual companion's `.sh` launchers do not run unmodified on Windows. |
| `.agents/skills/writing-plans/` | `copy-and-adapt` | An optional general-purpose reviewer dispatched with `plan-document-reviewer-prompt.md`; `subagent-driven-development` as the execution skill; the "Agent-Created Worktrees" section of `docs/agent-guidance/git-policy.md` | **path check** on `.agents\skills\writing-plans\SKILL.md` → `True` (*Observed:* `True`); then produce one plan and require that the sub-skill named in its mandatory header resolves. The plan-production leg needs a spec and was not run here | Saves plans to `docs/superpowers/plans/`, next to the matching spec; if you change the plan root, change the spec root in `brainstorming` to match. It works in the current worktree unless the user asked for a separate one. Its header and execution handoff name `subagent-driven-development`, which ships; it offers no other execution option. Commit checkpoints read "commit if the project's Git policy allows; otherwise record the diff base for review". |
| `.agents/skills/subagent-driven-development/` | `copy-and-adapt` | `writing-plans`, whose plans it executes; `docs/agent-guidance/subagent-model-routing.md`; the "Agent-Created Worktrees" section of `docs/agent-guidance/git-policy.md`; its own `implementer-prompt.md`, `spec-reviewer-prompt.md`, and `code-quality-reviewer-prompt.md` | **path check** on `.agents\skills\subagent-driven-development\SKILL.md` → `True`; then the **recursive content scan** over `.agents\skills` with glob `*.md`, once per term over `superpowers:`, `executing-plans`, `using-git-worktrees`, `requesting-code-review`, `finishing-a-development-branch`, `test-driven-development`, `code-reviewer` → **0 hits**. *Observed:* `True`, and 0 hits for every term | Ships because `writing-plans` hands off to it. It references no skill that does not ship: worktrees point at `git-policy.md`, code review dispatches a general-purpose subagent with the skill's own reviewer prompt, the finish step runs the full verification and follows the project's Git policy, and test-first is an inline rule. |
| `.agents/skills/math/` | `copy-and-adapt` | The root `.venv` with the section 1 packages of the root `requirements.txt` used by `scripts/cc_math/*.py` (`sympy`, `mpmath`, `numpy`, `scipy`, `z3-solver`, `pint`, `shapely`, `matplotlib`); optional topic and proof sub-skills referenced from the routers | **path check** on `.agents\skills\math\scripts\cc_math\sympy_compute.py` → `True`; then `.venv\Scripts\python.exe .agents\skills\math\scripts\cc_math\sympy_compute.py solve "x**2 - 4" --var x` prints solutions `-2` and `2` and exits `0`. *Observed:* `True`, then `"solutions": ["-2", "2"]`, `"verified": true`, exit `0` | Commands are plain `python` with paths from the repository root; if you relocate the directory you must rewrite all of them, and the smoke test above is the cheapest way to catch it. A missing package makes a script print `{"error": "No module named ..."}` and exit `1`, so install the manifest before first use. Sub-skills are linked by relative paths; `grep -rnoE "\.agents/skills/[a-z0-9-]+" .agents/skills` must name only folders that exist. *Observed:* every name it prints is a shipped folder. |
| `.agents/skills/skill-maintenance/` and `.agents/skills/docs/registry.md` | `copy-and-adapt` | Every shipped skill folder | **path check** on both; then the skill names in the registry table match `Get-ChildItem .agents\skills -Directory` minus `docs`. *Observed:* `True`, `True`; 9 registry rows, 9 skill folders | The registry is the human-readable index that `AGENTS.md` points at. Update it in the same change that adds, removes, or renames a skill, following `skill-maintenance`. |

---

## Mandatory Literature Knowledge-Base Workflow

These five agents are **one workflow**, not five independent assets. They share
a knowledge-base layout, a `short_cite` convention, a citation-key folder
scheme, and a report output root. Adopt and adapt them together.

For cross-harness definitions, keep both Copilot's aliases and Claude Code's
case-sensitive tool names in each `tools` list, with the same semantic
allowlist; `docs/agent-guidance/cross-platform-ai-support.md` describes the
failure when Claude's names are missing and how Codex treats the list.

| Path | Adoption | Dependencies | Validation | Notes |
| --- | --- | --- | --- | --- |
| `.claude/agents/ingest-paper.agent.md` | `copy-and-adapt` | `research/references/scientific_papers/`; a PDF-reading capability; the taxonomy rules in `research/AGENTS.md`; the tag-index generator | **path check** → `True` (*Observed:* `True`); then ingest one throwaway PDF and require a `<field>/<citation-key>/` folder holding the PDF and a `summary.md` with complete YAML frontmatter and a `## Relevance to the project` section, followed by a passing tag-index `--check`. The ingest leg needs subagent dispatch and a PDF, and was not run here | Canonical entry point for the knowledge base. Its deduplication step reads every existing `summary.md`, so the frontmatter schema must match the summary template it emits. It creates the first top-level field itself when the knowledge base is empty. |
| `.claude/agents/find-papers.agent.md` | `copy-and-adapt` | A populated `research/references/scientific_papers/`; `research/references/src/gather_summaries.py`; `_agents_outputs/find-papers/` as its write target | **path check** → `True` (*Observed:* `True`); then run a query against a knowledge base holding at least two papers and require a ranked Markdown table under `_agents_outputs/find-papers/` whose relative links all resolve (re-use the **link scan** on the produced table). The query leg needs subagent dispatch and was not run here | Search side of the workflow. It scores every paper, primarily on its `## Relevance to the project` section, so it is only useful after `ingest-paper` has run; on an empty base it returns an empty table, which is correct but easy to misread as a failure. Change its output root if the project moves `_agents_outputs/`. |
| `.claude/agents/citation-audit.agent.md` | `copy-and-adapt` | `citation-reader` and `citation-checker` (adapt all three together); subagent dispatch; a LaTeX manuscript under `publications/`; a writable output root | **path check** on all three citation agents → `True`, `True`, `True`; then `Select-String -Path .claude\agents\citation-*.agent.md -Pattern 'C:\\Users'` returns nothing (*Observed:* nothing); then run the `.agents/tests/citation-audit/` fixture and check `ANSWER_KEY.md` | **Conductor.** Review the three citation agents' paths and interfaces together: they exchange per-unit verdict files and a claim inventory through agreed paths, so adapting one in isolation breaks the other two. Inputs: the paper directory (required), a knowledge-base root (default `research/references/scientific_papers`), and an output root (default `_agents_outputs`). A non-default knowledge-base root makes the run isolated: no fetching (no `ingest-paper`, no web search), and no writes outside the two roots and the paper directory. Each reader resolves its paper's folder by `.bib` title or DOI, writes `fit.md` there (or a missing record), and ends its reply with `RESOLVED: <folder>`, `RESOLVED-SHARED: <folder>` (a second key for the same paper adds its block to the shared notes), or `MISSING: <key>`. Notes carry a run line, `Audit run: <date> <paper directory>`, so notes from an earlier audit are re-read rather than reused. A stub is judged by content (a PDF that will not open or yields under 1,000 characters of text); its units are judged from `summary.md` and never become critical on that ground alone. A better-paper swap must name a key already in the `.bib`. The report has a "Knowledge-base defects" section listing every stub, missing paper, and key drift. Claude Code refuses report-file writes from subagents, so when its write of `report.md` is refused the Conductor returns the report between `REPORT-BEGIN`/`REPORT-END` markers with a `REPORT-PATH:` line, and the caller saves it. |
| `.claude/agents/citation-reader.agent.md` | `copy-and-adapt` | `ingest-paper`, only outside isolated runs (it ingests a missing paper, or re-fetches a stub, before reading); the knowledge-base root; the brief and run line `citation-audit` passes it | **path check** → `True` (*Observed:* `True`); then, in the fixture run above, require one anchored claim inventory per cited paper at exactly the path `citation-checker` reads. The fixture leg needs subagent dispatch and was not run here | Adapt together with `citation-audit` and `citation-checker`. Its output contract is consumed by `citation-checker`, so any path change must be made in both files in the same edit. It writes `fit.md` in the folder it resolves, or a missing record in the working area. The notes carry the run line, so notes from an earlier audit are overwritten. A stub's inventory comes from `summary.md` under a `⚠ STUB-PDF` caveat. When a second key resolves to a folder already read in this run, the reader adds only its own `### Targeted (<key>)` block to the shared `fit.md`. |
| `.claude/agents/citation-checker.agent.md` | `copy-and-adapt` | `citation-reader`'s `fit.md` in the resolved folder; the knowledge-base root; the manuscript's `.bib` | **path check** → `True` (*Observed:* `True`); then, in the fixture run above, require exactly one verdict file per `(citation_key, location)` unit, each with an optional proposed fix, in the directory `citation-audit` reconciles. The fixture leg needs subagent dispatch and was not run here | Adapt together with `citation-audit` and `citation-reader`. One verdict file per work unit is what lets the conductor guarantee full coverage; changing the file naming without telling the conductor produces silent under-coverage. With stub notes (`⚠ STUB-PDF`) it skips the escape-hatch PDF read, tags its grounding `[SUMMARY-ONLY]`, and never marks a unit `critical` on the stub alone. It looks for a better paper only under the knowledge-base root and in the `.bib`, and proposes a swap only to a key already in the `.bib`. |
| `.agents/tests/citation-audit/` | `copy-and-adapt` | The three citation agents; the markings module (the mock paper loads it by a four-level relative path, so run copies sit at the depth its `README.md` gives) | **path check** on `.agents\tests\citation-audit\ANSWER_KEY.md` → `True` (*Observed:* `True`); then the audit run over a copy of `mock-paper/` reproduces the answer key. The audit leg needs subagent dispatch and was not run here | Self-contained: a mock manuscript, a small knowledge base of fictional papers (`knowledge-base/`), and their LaTeX sources (`paper-sources/`). It needs no papers from the project's own knowledge base, so it runs in a fresh repository. Covers plain and multi-cite citations, a planted wrong citation with a better-paper swap, a table citation, a stub, key drift, a missing paper, and a `\nocite`. Run it on a copy; see its `README.md`. |

### Required Agents Beyond the Literature Workflow

Each agent below ships with a fixture under `.agents/tests/`. Run fixtures on a
copy under `_agents_outputs/_agents_dump/`, never in place.

| Path | Adoption | Dependencies | Validation | Notes |
| --- | --- | --- | --- | --- |
| `.claude/agents/ai-judge.agent.md` | `copy-and-adapt` | A caller that supplies the original request, the work product, and validation output | **path check** → `True`; then the `.agents/tests/ai-judge/` fixture: the incomplete case returns `FAIL` naming the missing hyphen-collapsing rule, and the complete case returns `PASS` | Contains no project terms. The fixture pins its behaviour, so a changed copy is verified by the two cases rather than by trust. |
| `.agents/tests/ai-judge/` | `copy-and-adapt` | `ai-judge`; Python and pytest for the cases' own tests | **path check** on `.agents\tests\ai-judge\ANSWER_KEY.md` → `True`; then the two dispatches in its `README.md`. *Observed:* `True`; the cases' own tests pass (`case-complete`: `5 passed`; `case-incomplete`: `4 passed`) | Each case holds `REQUEST.md`, `work/`, and `VALIDATION.txt`. The incomplete case's tests pass; its gap is a missing requirement, which is what the judge must catch. |
| `.claude/agents/task-orchestrator.agent.md` and `docs/agent-guidance/subagent-model-routing.md` | `copy-and-adapt` | Subagent dispatch; the routing guide's ladders and its inherit-the-parent fallback | **path check** on both → `True`, `True`; then the `.agents/tests/task-orchestrator/` fixture: both acceptance commands print their expected values, and the report lists each subtask with evidence and one `Delegations` row per subtask | The orchestrator follows the routing guide and records each delegation's model. The ladders are preferences; where a platform cannot select or rank models, the subagent inherits the parent model. Re-check ladder names against the target harness. |
| `.agents/tests/task-orchestrator/` | `copy-and-adapt` | `task-orchestrator` | **path check** on `.agents\tests\task-orchestrator\ANSWER_KEY.md` → `True`; then the dispatch in its `README.md` | Two independent file-writing subtasks with deterministic acceptance commands, written under the git-ignored `_agents_outputs/_agents_dump/`. |
| `.claude/agents/approve-changes-markings.agent.md` | `copy-and-adapt` | `publications/modules/markings/` and its `scripts/find_changes_markers.py`; the build recipe in `docs/agent-guidance/vscode-latex-environment.md` | **path check** → `True`; then the `.agents/tests/approve-changes-markings/` fixture: the finder reports 0 markers afterwards, the cleaned files match `expected/` ignoring whitespace, the `missing` markers survive, and the copy builds | An agent, so all three platforms can delegate to it. Users ask in plain words ("approve all changes"); the parent passes the selection or active file as scope. It leaves nested markers and multi-role `markroles` fields unchanged and reports them as rule violations. |
| `.agents/tests/approve-changes-markings/` | `copy-and-adapt` | The agent above; the markings module (the mock paper loads it by a four-level relative path, so run copies sit at the same depth) | **path check** on `.agents\tests\approve-changes-markings\ANSWER_KEY.md` → `True`; then the run in its `README.md`. *Observed:* `True`; before any run, `find_changes_markers.py` on `mock-paper/` reports `10 marker(s) found.`, as the answer key expects | Covers every finder kind, an empty replacement, an approved and a `missing` `markroles` field, and a `\Mark{missing}` that must survive. It holds no nested markers or multi-role `markroles` fields, which `publications/AGENTS.md` forbids. |

---

## Publication Baseline

| Path | Adoption | Dependencies | Validation | Notes |
| --- | --- | --- | --- | --- |
| `publications/modules/markings/` | `copy-and-adapt` | `xcolor`, `soul`, `environ`, `etoolbox`, `xparse`, `tcolorbox`, `pdfcomment`; biblatex with biber for citation highlighting through `markings.dbx` | **path check** on `publications\modules\markings\markings.tex` → `True`; then `.venv\Scripts\python.exe -m pytest publications/modules/markings/scripts -q` exits `0`; then build a manuscript that loads it. *Observed:* `True`, then `2 passed`, exit `0` | Keep unchanged. `scripts/find_changes_markers.py` is the finder the `approve-changes-markings` agent runs, with its test beside it. Relocating the module means updating the `\input` path and the biblatex `datamodel` path in every manuscript's `config.tex` together. |
| `publications/paper---example/` | `copy-and-adapt` | The markings module; the build recipe in `docs/agent-guidance/vscode-latex-environment.md`; on Linux or CI, the TeX Live packages in the CI `paper-build` job | A clean build with the recipe exits `0`, the log has no undefined citations or references, and no intermediates appear beside the sources. On Windows with MiKTeX: `.vscode\latex-full-build.ps1 -ProjectDir publications\paper---example -Quiet`. On Linux or macOS: the TeX Live sequence from inside the paper folder. The build was not run here; CI's `paper-build` job runs it | Short, generic, and compilable. Its `config.tex` defines the roles `changes`, `edits`, and `missing`. It demonstrates `\Mark{changes}{…}`, `\Mark{changes}[heading]{…}`, `\MarkEdit{edits}{old}{new}`, `\MarkEdit{edits}[math]{old}{new}`, `\Mark{missing}{…}`, `MarkEnv` text and math, `\MarkPlaceholderFigure`, and one cited `.bib` entry with `markroles = {changes}`. Copy it to `publications/paper---<slug>/` to start a paper. If you rename or remove it, update the CI `paper-build` job in the same change. |

---

## Environment, Testing, and CI Templates

| Path | Adoption | Dependencies | Validation | Notes |
| --- | --- | --- | --- | --- |
| `.venv` (root virtual environment) | `copy-and-adapt` | A pinned Python version (the template assumes 3.11 or newer; CI uses 3.11); `.venv` listed in `.gitignore`; the root `requirements.txt` | `.venv\Scripts\python.exe -c "import sys; print(sys.version)"` prints the intended version; `git check-ignore -v .venv` prints the ignoring rule. *Observed:* the template ships no `.venv`; `.gitignore:58:.venv` | Adopt the **convention** (one root `.venv` that every sector and skill uses), never a directory. Create it from the manifest; never copy one between machines or repositories. |
| `requirements.txt` (root dependency manifest) | `copy-and-adapt` | pip and a virtual environment; nothing else. It is deliberately pip/venv-native rather than conda, so the same file works unchanged on Windows, macOS, and Linux | `.venv\Scripts\python.exe -m pip install --dry-run -r requirements.txt` exits `0` with every requirement resolved; then run each skill's smallest command and confirm none returns `{"error": "No module named ..."}`. *Observed:* the dry run exits `0` | **The manifest is what makes a skill's shipped scripts real rather than decorative**: an undeclared package makes its script fail with `No module named ...` and exit `1`. Section 1, **Shared project structure**, declares what the shipped skills import: `sympy`, `mpmath`, `numpy`, `scipy`, `z3-solver`, `pint`, `shapely`, `matplotlib`, and `requests`, plus a commented optional `plotly`. Section 2 is a placeholder (`pytest`) for the project's own packages; replace and extend it. Entries are lower bounds, each commented with the script it backs. A stack with an install constraint the root `.venv` should not inherit (a heavy optional SDK, a conda environment, a different Python version) keeps its own manifest, listed in the root file's header. |
| Code-sector tests (`code/pytest.ini`, `code/requirements.txt`, `code/tests/`) | `copy-and-adapt` | The root `.venv`; `code/src/` on the import path through `pythonpath = src` | `Push-Location code; ..\.venv\Scripts\python.exe -m pytest -q; Pop-Location` exits `0`. *Observed:* `6 passed`, exit `0` | The canonical gate runs **from inside `code/`**: `pytest.ini` there sets the test paths and `pythonpath = src`. Call the venv interpreter by path rather than a bare `python`; on a clean machine the venv is not on `PATH`. `code/requirements.txt` is what CI installs for this suite alone, so every package the code sector imports goes in both it and the root manifest. The knowledge-base tools and the marker finder have their own suites, run from the repository root: `python -m pytest research/references/src -q` (*Observed:* `468 passed`) and `python -m pytest publications/modules/markings/scripts -q` (*Observed:* `2 passed`). An app added under a sector later keeps its own suite and command; do not fold it into the `code/` run unless it lives under `code/`. |
| LaTeX build documentation (`docs/agent-guidance/vscode-latex-environment.md`) | `copy-and-adapt` | The chosen TeX distribution, editor extension, and viewer; the four `.vscode/` files it describes | **path check** → `True` (*Observed:* `True`); then follow the document on a clean machine and confirm the example manuscript compiles end to end. The end-to-end leg needs a clean machine and was not run here | Keep a written, followable build procedure: agents should never guess LaTeX invocations. The canonical recipe is `pdflatex → biber → pdflatex → pdflatex` with intermediates in `.latex_build/`. It gives both the MiKTeX recipe (`--aux-directory`) and the TeX Live recipe (`mkdir -p .latex_build`, `-output-directory=.latex_build`, then move the PDF next to `main.tex`). User-level settings and keybindings are documented as entries to merge, never shipped. |
| `.vscode/settings.json`, `.vscode/tasks.json`, `.vscode/find-latex-root.ps1`, `.vscode/latex-full-build.ps1` | `copy-and-adapt` | LaTeX Workshop and the other extensions the settings configure; Windows PowerShell for the tasks and scripts | **path check** on all four → `True`; then `Select-String -Path .vscode\*.json -Pattern 'C:\\\\Users\\\\'` returns nothing (the quadrupled backslashes are explained in the machine-local configuration row below); then open the repository in the editor and confirm no setting references a missing path or extension. *Observed:* `True` ×4; nothing | `settings.json` holds the Copilot chat settings, Python `extraPaths` for `code/src` and `research/references/src`, folder icons, and the LaTeX Workshop recipes. It ships with no terminal auto-approve list: command allowlists are a per-user choice. Ship `tasks.json` together with both scripts it calls; neither holds machine paths. `keybindings.json` is user-level and never ships. |
| `.github/workflows/tests.yml` (GitHub Actions) | `copy-and-adapt` | GitHub Actions enabled; `ubuntu-latest` runners; Python 3.11; the TeX Live apt packages below | `Get-ChildItem .github\workflows\*.yml` lists only workflows you intend; then push a branch and confirm the run triggers and exits `0`. *Observed:* `tests.yml` only. The trigger leg is only observable on the project's own remote | Triggers on push to `main` and on pull requests. Four jobs: `code-tests` installs `code/requirements.txt` and runs `python -m pytest -q` from inside `code/`; `kb-and-markings-tests` runs pytest on `research/references/src` and `publications/modules/markings/scripts` and the tag-index `--check`; `discovery-setup` runs `sh .claude/setup-discovery.sh` twice and asserts that the link is a symlink, resolves, is ignored, and leaves `git status --porcelain` empty; `paper-build` installs `texlive-latex-recommended texlive-fonts-recommended texlive-latex-extra texlive-plain-generic texlive-pictures texlive-bibtex-extra texlive-science biber`, runs the TeX Live recipe in `publications/paper---example/`, fails on undefined citations or references, and uploads the PDF. `texlive-plain-generic` is named explicitly because it provides `soul` and `tracklang` (for `pdfcomment`), and `texlive-latex-extra` only recommends it. **Check every command and trigger against the project**: branch names, `working-directory`, and the paper path are repository-specific, and a workflow that points at paths that do not exist will silently never test them. |

### Keeping the manifest honest

When any code in the repository (a skill, an agent, a sector app, or the
project's own code) gains a dependency on a third-party package, declare it in
the matching section of the root `requirements.txt` in the same change that
introduces the dependency, with a comment naming the script it backs. Code
under `code/` also goes in `code/requirements.txt`. Do not rely on the package
happening to be present in a developer's environment: an undeclared import is
invisible until someone clones the repository, and it surfaces as a bare
`No module named ...` that gives no hint about what to install or which asset
needed it. Only a stack with its own install constraint gets a separate
manifest. The cheapest check that the manifest is still complete is to run each
affected skill's smallest command, and the sector test suites, in a fresh
environment built from the manifest alone.

### Durable-data review criteria

The layout map may describe a **planned** data root without creating an empty
dataset or an invented index row; distinguish such entries from existing
directories when applying the layout directory check. Index only datasets that
actually exist. Keep paid or otherwise irreplaceable raw records under `data/`
from the start; local proposals and derived data and figures use the ignored
`artifacts/` root.

For workflows that spend money or quota, exclusive file writes, hashes, and
advisory locks do not by themselves prove power-loss durability. Flushing a
file is not the same as flushing its directory entry, and some platforms,
including Windows through Python's standard library, offer no directory flush.
Paid execution needs a separately reviewed durability strategy, or an
environment with the required directory-flush guarantees; tests against a local
temporary store do not establish that guarantee. Preserve reservations for
submissions whose outcome is unknown, and reconcile the remote job identity
before any retry. These are review criteria, not approval to spend a budget.

**Project-specific workflows are not starter defaults.** A workflow that
publishes one project's app, or guards a generated-file mechanism that a
directly owned repository does not have, belongs to that project. Write such
workflows for the project that needs them; never import them as a starting
point.

---

## Optional Capability Packs

Anything **not** listed as part of the starter standard above requires an
explicit portability review before adoption. A portability review means: read
the asset end to end; list every tool, package, path, agent, and harness
feature it assumes; confirm each one exists in the project; and record the
validation evidence that proves the adapted copy works. Assets that fail the
review are either fixed before adoption or left out: an unreviewed skill that
references a missing tool degrades every agent turn that loads it, without ever
failing loudly.

| Path | Adoption | Dependencies | Validation | Notes |
| --- | --- | --- | --- | --- |
| Additional skills (`.agents/skills/<name>/` beyond the starter set) | `optional` | Per skill. Enumerate what ships with `Get-ChildItem .agents\skills -Directory`. *Observed:* 10 directories, the nine registered skills plus `docs/`, all in the starter set | Per skill, in this order: **path check** on `.agents\skills\<name>\SKILL.md` → `True`; then enumerate its assumed tooling by running `Select-String -Path .agents\skills\<name>\SKILL.md -Pattern '<term>'` once per term over `uv run`, `npx`, `node `, `$SKILL_DIR`, `allowed-tools`, `scripts/` (run every term, not just the first; a single term can match nothing while others match many lines); confirm every hit resolves in the target harness; then run the skill's own smallest command end to end and require exit `0`. Record that output with the adoption | Typical candidates are figure generation, visualization, notebook or domain toolkits, document-format helpers, and skill-authoring skills. Each needs its own dependency audit, a registry row, and declared packages before it earns a place. |
| Sector apps (for example `research/apps/<app>/` or `code/apps/<app>/`) | `optional` | Per app; typically a CLI or harness it drives and one agent contract it calls | The app's own test suite, run with its own command from the app root, exits `0`; then one end-to-end use reaches the agent it calls | A reviewable app is project-owned, has a test suite that mirrors its `src/` module by module, resolves the repository root itself (for example with `git rev-parse --show-toplevel`, overridable by an environment variable) instead of hard-coding it, and names exactly one agent contract. It stays optional when it binds to one specific CLI or agent path. |
| `.github/prompts/*.prompt.md` | `optional` | GitHub Copilot | **path check** on the prompt; **link scan** on it → nothing; then one run on a representative input | The template ships no `.github/prompts/`. Prompts there are Copilot-only: Codex and Claude Code do not read them. Prefer an agent under `.claude/agents/`, which all three platforms can use. `.github/agents/` is never a valid agent location. |

---

## Files and Content That Must Not Be Copied

Every check in this table is an **absence** check: it asserts that the listed
content is *not* present. Each check must pass in the template and in any
project that adopts the standard. Because a passing absence check looks the
same as a broken one, prove each command form once with a term or path you know
is present, as `Shared Validation Snippets` describes. *Observed* values were
recorded in the template.

| Path | Adoption | Dependencies | Validation | Notes |
| --- | --- | --- | --- | --- |
| `research/references/scientific_papers/**/*.pdf` and `**/summary.md` from another project | `do-not-copy` | — | `Get-ChildItem research\references\scientific_papers -Recurse -Include *.pdf,summary.md` returns nothing before the project's own first ingest. *Observed:* nothing | Another project's papers and summaries are its literature record. Copying them pre-loads irrelevant sources and corrupts the ingest agent's deduplication check. Ingest what the project actually cites. The fictional papers under `.agents/tests/citation-audit/knowledge-base/` are fixture material, not a knowledge base. |
| `research/derivations/**`, `research/notes/**`, `research/progress/**` from another project | `do-not-copy` | — | `Get-ChildItem research\derivations -Recurse -Filter *.md` returns nothing before the project writes its own; `Test-Path research\notes` and `Test-Path research\progress` return `False` until the project creates them. *Observed:* nothing; `False`, `False` | Derivations, notes, and progress logs belong to the project that wrote them. Keep the directories and conventions; write the content. |
| `artifacts/**` | `do-not-copy` | — | `Get-ChildItem artifacts -Recurse -Force` lists only `README.md` in a fresh clone; `git check-ignore -v artifacts/x` prints the ignoring rule. *Observed:* only `README.md`; `.gitignore:104:/artifacts/*` | Generated data, figures, and videos are reproducible outputs of one project's code and mean nothing in another. |
| `data/**` (except `README.md`) | `do-not-copy` | — | `Get-ChildItem data -Recurse -File` returns only `README.md` before the project's first dataset. *Observed:* only `README.md` | Another project's paid or long-running results. Start the dataset index empty. |
| `_agents_outputs/**` (including `_agents_dump/`) | `do-not-copy` | — | `git ls-files _agents_outputs` lists only `_agents_outputs/.gitkeep`; `git check-ignore -v _agents_outputs/_agents_dump` prints the ignoring rule. *Observed:* `.gitkeep` only; `.gitignore:108:_agents_outputs/_agents_dump/` | Past agent reports and temporary evidence. A local `_agents_dump/` may hold fixture runs; it is ignored and never committed. |
| `code/src/**`, `code/scripts/**`, `code/apps/**` from another project | `do-not-copy` | — | `Get-ChildItem code\src,code\scripts -Recurse -File` lists only the project's own files (in the template: `code_paths.py` and the two `.gitkeep` files); then the **project-name scan** over each imported file returns nothing. *Observed:* `code\src\code_paths.py`, `code\scripts\data\.gitkeep`, `code\scripts\figures\.gitkeep` | Domain code belongs to its project. The `code/` *structure*, `code_paths.py`, and the conventions are the starter standard; another project's implementation is not. |
| `publications/paper---*/` (other than the example), `publications/submissions/**`, `publications/presentations/**`, `publications/animations/**` from another project | `do-not-copy` | — | `Get-ChildItem publications -Directory` lists only `modules`, `paper---example`, and the project's own manuscripts. *Observed:* `modules`, `paper---example` | Another project's manuscripts, venue packages, decks, and animation sources, including their marking history and venue templates. The `publications/submissions/<VENUE>/` *convention* (venue rules in a `SUBMISSION-GUIDELINES.md` beside a standalone `paper---*/` project that bundles its own class files) is worth adopting; another project's content is not. |
| `secrets/`, credentials, API keys, tokens | `do-not-copy` | — | `Test-Path secrets` returns `False`, `git check-ignore -v secrets/x` prints the ignoring rule, and a secret scan finds nothing. *Observed:* `False`; `.gitignore` ignores `secrets/` | Never copy credentials between repositories. Provision new ones and keep them out of version control. |
| Environment files (`.venv/`, `.env`, lockfiles bound to one machine) | `do-not-copy` | — | `Test-Path .venv` returns `False` in a fresh clone; `git check-ignore -v .venv` and `git check-ignore -v .env` print their rules. *Observed:* `False`; `.gitignore:58:.venv`; `.gitignore:57:.env` | Adopt the *convention* of a root `.venv` (see `Environment, Testing, and CI Templates`); recreate the environment from the manifest. |
| Machine-local configuration (`.claude/settings.local.json`, `.vscode/keybindings.json`, absolute user paths in any config) | `do-not-copy` | — | `Test-Path .claude\settings.local.json` and `Test-Path .vscode\keybindings.json` return `False`, and `Select-String -Path .vscode\*.json,.claude\*.json -Pattern 'C:\\\\Users\\\\'` returns nothing. The quadrupled backslashes are deliberate: JSON escapes the path separator, so the regex must match `C:\\Users\\` **as written on disk**. A single-escaped pattern `'C:\\Users\\'` cannot match a JSON-escaped path and would be a check that cannot fail. Prove the form with `'C:\\Users\\x' \| Select-String -Pattern 'C:\\\\Users\\\\'`, which returns 1 hit. *Observed:* `False`, `False`, nothing; the proof returns 1 hit and the single-escaped pattern 0 | One developer's machine setup. Absolute user paths break on any other machine and are the most common silent failure when a config is copied wholesale. `.claude/settings.local.json` is ignored by `.gitignore`. |
| Caches and build residue (`__pycache__/`, `*.pyc`, `.pytest_cache/`, LaTeX `.aux`/`.bbl`/`.latex_build/`, `node_modules/`) | `do-not-copy` | — | The **tracked-residue scan** prints nothing. *Observed:* nothing | Regenerated on first run; copying them only imports stale state. Local runs may leave such files in ignored folders; the scan checks only what Git would track. |
| Generated or vendored platform copies (`.codex/`, `.github/agents/`, `.github/skills/`, `.github/instructions/`, `.github/copilot-instructions.md`, copied content under `.claude/skills/`, generated sector `CLAUDE.md` files, generated-instruction layers, AI-tool submodules) | `do-not-copy` | — | `Test-Path .github\skills`, `Test-Path .github\agents`, `Test-Path .github\instructions`, `Test-Path .github\copilot-instructions.md`, `Test-Path .codex`, and `Test-Path .gitmodules` return `False`; `Get-ChildItem -Recurse -Force -Filter CLAUDE.md` finds only the root shim. If `.claude\skills` exists, `Get-Item -Force` must report a link targeting `.agents\skills`, and `git check-ignore -v` must print its ignore rule; a real directory is a failure. `(Get-Item .claude\agents -Force).LinkType` is empty: `.claude\agents` is a real tracked directory, never a link. *Observed:* all `False`; only the root `CLAUDE.md`; `.claude\skills` absent (setup not run); `.claude\agents` LinkType empty | Generated mirrors and vendored copies duplicate content and drift from their owner. Own skills and agents directly under `.agents/skills/` and `.claude/agents/`. The ignored skills link created by the `.claude/setup-discovery.*` scripts is the narrow exception: it contains no independent files and exists only to adapt the canonical path to Claude Code's fixed discovery location. |
| Personal working preferences in instructions and skills: Git stage/commit/push ownership, TODO checkbox and closure ownership, the VS Code user-settings permission rule, and Python coding-style opinions (module calling conventions, a dual-callable `argparse` pattern, Enum and type-hint preferences, a ban on script-level tests, mandatory tests) | `do-not-copy` | — | Run `Select-String -Path AGENTS.md,code\AGENTS.md,docs\todo\README.md,docs\agent-guidance\git-policy.md,docs\agent-guidance\vscode-latex-environment.md -Pattern '<term>'` and the **recursive content scan** over `.agents\skills` with glob `*.md`, once per term over `stage,? (or )?commit`, `owns staging`, `Do not mark checklist`, `Only the user may declare`, `user settings or user keybindings unless`, `sys\.argv`, `_parse_args`, `Script-level tests`, `Mandatory tests`; every run returns nothing. *Observed:* 0 hits for every term, across the five files and every shipped skill folder | These are one developer's habits, not project mechanism. Each user keeps them in their own user-level configuration for whichever AI platform they use (Copilot, Claude Code, Codex). Keep the safety rules: never run destructive Git commands on the user's working tree, never switch the user's active branch, treat existing modifications as user-owned, and merge rather than replace any VS Code user-settings change. |

---

## New-Project Adaptation Checklist

Work through this in order for a project started from this template. To bring
the standard into an existing repository instead, first copy each
`copy-and-adapt` asset from the template to the same relative path, then follow
the same steps. Do not skip the validation column: an unadapted copy fails
quietly.

1. **Replace the placeholders.** Write the project statement under "What Is
   This Project About?" in `AGENTS.md`; `Select-String AGENTS.md -Pattern
   'Replace this paragraph'` must then return nothing. Replace the section 2
   placeholder in `requirements.txt` with the project's own packages, and
   mirror the code sector's imports in `code/requirements.txt`. Copy
   `publications/paper---example/` to `publications/paper---<slug>/` for the
   first manuscript, or adapt it in place; either way, keep the CI
   `paper-build` job pointed at a manuscript that exists. Confirm that each
   `git check-ignore` in `Core Repository Structure` prints its rule.
2. **Review the instruction layer.** Read `AGENTS.md`, the three sector
   `AGENTS.md` files, `docs/agent-guidance/project-layout.md`, and
   `docs/todo/README.md`. Add the project's own sector rules, and keep personal
   working preferences out (see the last row of `Files and Content That Must
   Not Be Copied`). Run the three checks (path check, project-name scan, link
   scan) on each file you changed or imported.
3. **Set up the platforms.** Follow
   `docs/agent-guidance/cross-platform-ai-support.md` and cut it down to the
   platforms the project uses. For Claude Code, run the setup script for your
   OS once (`.claude/setup-discovery.ps1` on Windows,
   `.claude/setup-discovery.sh` on Linux/macOS). Without Claude Code, delete
   `CLAUDE.md`, both setup scripts, the `/.claude/skills` ignore rule, and the
   CI `discovery-setup` job together. Keep the Codex paragraph of the
   `AGENTS.md` section only if Codex is used. Run the guide's checks on each
   platform; do not assume feature parity.
4. **Keep the layout map true.** Update
   `docs/agent-guidance/project-layout.md` in the same change that adds,
   removes, moves, or renames a directory, and delete entries for directories
   the project does not keep.
5. **Stand up the environment.** Create the root `.venv` on a pinned Python
   version and install `requirements.txt`. Keep its section 1, the packages the
   shipped skills need (`sympy`, `mpmath`, `numpy`, `scipy`, `z3-solver`,
   `pint`, `shapely`, `matplotlib`, `requests`). Then run each skill's smallest
   command and confirm none returns `No module named ...`. Thereafter keep the
   manifests current in the same change that adds any new dependency.
6. **Verify the skills.** The template ships eight starter skills plus
   `skill-maintenance`, all registered in `.agents/skills/docs/registry.md`.
   Work through each `Mandatory Skills` row's `Notes` column and resolve the
   named assumptions **before** first use. Run each row's validation, at
   minimum the math smoke test, which must print roots `-2` and `2` and exit
   `0`. Register any skill you add or remove.
7. **Run the agent fixtures.** Run the `.agents/tests/citation-audit/` fixture
   and compare the result with its `ANSWER_KEY.md`; review the three citation
   agents' paths and interfaces together if you change any of them. Run the
   `ai-judge`, `task-orchestrator`, and `approve-changes-markings` fixtures the
   same way, each on a copy under `_agents_outputs/_agents_dump/`.
8. **Start the knowledge base empty.** Keep
   `research/references/scientific_papers/` free of category folders until the
   first ingest, follow the `Paper Taxonomy Rules`, and let real ingests define
   the taxonomy. Record each new top-level field in `research/AGENTS.md`.
9. **Wire testing and CI.** Add the project's own code tests under
   `code/tests/`, give any sector app its own suite and command, and check
   `.github/workflows/tests.yml` against the repository's branches, paths, and
   runner OS. Push a branch and confirm that each job triggers and passes.
10. **Review optional packs.** For anything outside the starter standard, run
    the portability review described in `Optional Capability Packs` and record
    the evidence before adopting it.
11. **Record the evidence.** Keep the validation output for every adopted or
    changed asset with the change that made it, so a later reader can tell an
    adapted copy from a broken one.

---

## Maintenance and Maturity Rules

1. **Direct ownership.** Every instruction, skill, and agent in the repository
   is a directly maintained file edited in place. No generated mirrors, no
   vendored submodules, no per-platform duplicates of the same content. One
   file, one owner.
2. **Same relative path by default.** Keep an asset at the path it has in the
   template unless there is a stated reason to move it. Assets reference each
   other by relative path; relocating one without updating the files that use
   it is the most common way an adopted workflow breaks.
3. **Dependency and path review before adoption.** Before an asset is used for
   real, enumerate the tools, packages, harness features, agents, and paths it
   assumes, and confirm each exists. An asset whose dependencies cannot be
   satisfied is adapted or dropped, never adopted "for now".
4. **Validation evidence.** Every adoption carries the output of its validation
   check. A row in this blueprint without a runnable check is an incomplete row;
   an adoption without recorded evidence is an unverified adoption.
5. **Blueprint inspection on change.** Whenever a listed asset changes, or
   whenever a new reusable pattern is introduced anywhere in the repository,
   inspect this blueprint in the same change and update the affected rows,
   dependencies, validation commands, observed values, and exclusions. A
   blueprint that lags the repository is worse than none, because it is
   trusted.
6. **Personal preferences stay personal.** Before a rule enters a reusable
   asset, decide whether it is project mechanism or one developer's working
   habit (Git workflow, approval rituals, coding style). Habits belong in that
   developer's user-level agent configuration; only mechanism and safety rules
   travel with the project.
