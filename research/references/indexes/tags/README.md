# Scientific-paper tag index

## Source assignments and accepted vocabulary

The inline `tags` arrays in paper [summaries](../../scientific_papers/) are
authoritative for paper-to-tag assignments. The generated [index](index.md)
is the accepted-vocabulary snapshot and the entry point: it lists accepted tags
and paper counts, and links to one generated page per tag under `by_tag/`.
Only this README and the index sit at the top level, so the index cannot be
mistaken for a tag page. It is not an independently maintained registry.
Edit source summary metadata, then regenerate; never edit generated Markdown.
This README is maintained by hand and is not a generated file.

## Canonical tags and metadata

Use ASCII lowercase `snake_case`, matching `^[a-z0-9]+(?:_[a-z0-9]+)*$`.
Reuse an accepted tag whenever its meaning fits. Tags must be unique within
each summary's inline array. The generator validates tags; it does not rewrite
source summaries, normalize assignments, or automatically merge suggestions.

When the generator rejects a noncanonical tag, it reports a normalized
candidate: ASCII letters lowercased, hyphens and whitespace replaced with
underscores, and repeated or edge underscores collapsed and trimmed. For
example, `Sensor-Networks` becomes `sensor_networks`. Edit the summary to use
the candidate, or an accepted tag that already means the same thing.

Before accepting a new tag, check the similar-tag suggestions. Prefer one
spelling per concept, for example `sensor_networks` rather than both
`sensor_network` and `sensor_networks`. Keep a narrower tag, such as
`wireless_sensor_networks`, only when it names a distinct concept that more
than one paper shares.

Required `citation_key` and `short_cite` metadata must be nonempty, printable,
control-free single-line strings: no decoded C0/C1 controls (including tabs) or
Unicode line/paragraph separators.
Quoted YAML escapes do not bypass this rule. Labels are preserved rather than
silently flattened or rewritten. Keep `tags` as a nonempty inline string array.

## Generator commands

Run from the repository root using the project's Python environment:

```text
python research/references/src/generate_literature_tag_index.py
python research/references/src/generate_literature_tag_index.py --check
python research/references/src/generate_literature_tag_index.py --accept-new-tags
```

- **Default:** validate sources and regenerate only when all observed tags are
  already accepted. Use after changing assignments or citation metadata.
- **Check:** validate and compare expected filenames and decoded logical text,
  normalizing CRLF to LF, without writing. It is not a raw-byte comparison;
  equivalent CRLF/LF output passes. Other formatting drift is stale output.
  Use as the freshness gate; stale generated output fails the check.
- **Accept new tags:** explicitly accept all unseen valid tags and regenerate.
  First run default or check mode to inspect every unseen tag and its similar-tag
  suggestions. Review the complete set before accepting; suggestions never merge
  tags automatically. Check and accept modes are mutually exclusive.

If the generated index is absent, default and check modes exit `1` with
`bootstrap_required`; bootstrap explicitly with `--accept-new-tags`. Ensure this
directory and its parent exist before generating; the planner rejects a missing
parent. After bootstrap or acceptance, run `--check`. Repeating default
generation should be byte-identical.

On an empty knowledge base, bootstrap writes an `index.md` with the marker, the
heading, and an empty table, and no `by_tag/` pages; `--check` then exits `0`.
A new project starts from that empty index. After the first ingests add tagged
summaries, review their tags in default mode, then accept them.

The accepted-vocabulary interface is the exact `# Scientific-paper tags`
heading and its one canonical `| Tag | Papers |` table. Table rows end at the
first non-pipe line. Fenced examples outside that interface are ignored by
vocabulary parsing; malformed contiguous table rows still fail validation.
Surrounding prose or formatting changes can parse as valid vocabulary but still
fail `--check` as stale generated output. Do not edit the snapshot to accept tags.

When a tag disappears from every source summary, regeneration removes its
marked page and its index row. A later reintroduction is an unseen tag requiring
review and explicit acceptance again. Do not remove a tag by editing the index.

## Generated-file safety and failures

Every generated file begins with this exact first line:

```text
<!-- GENERATED: literature-tag-index; DO NOT EDIT -->
```

Generated files use deterministic UTF-8 without BOM and LF line endings. The
generator replaces or removes only marked files in its managed locations
(`index.md` here and `by_tag/<tag>.md`); it never writes or removes this README
or source summaries. `by_tag/` holds only canonical `<tag>.md` pages; any other
Markdown there is an unsafe-state failure. A marked `<tag>.md` at the top level
belongs to an older flat layout and is removed as obsolete. Unmarked collisions,
unsafe paths or symlinks, malformed accepted indexes, invalid metadata, and
source/output changes since planning must be resolved, not bypassed. Do not
manually add the marker to unrelated content to force an overwrite.

| Exit code | Meaning |
|---|---|
| `0` | Generation succeeded, or check found valid current output. |
| `1` | Source/frontmatter, accepted-index/bootstrap, unseen-tag, usage, or generation failure. |
| `2` | Check found otherwise valid but stale generated output. |
| `3` | Unsafe output state, such as an unmarked managed-path collision. |

Diagnostics identify the issue and, where applicable, the tag and repository-
relative summary path. Unsafe-state failures take precedence over other failures;
staleness alone yields code `2`. Fix the reported source or safety issue and rerun
the appropriate mode. Do not hand-edit generated pages to make checks pass.