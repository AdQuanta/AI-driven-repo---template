#!/bin/sh
# Creates the ignored .claude/skills symlink to the canonical .agents/skills
# (Linux/macOS). Safe to run repeatedly. On Windows use setup-discovery.ps1.
set -eu

fail() {
    echo "setup-discovery: $1" >&2
    exit 1
}

case "$(uname -s)" in
    MINGW* | MSYS* | CYGWIN*)
        fail "Windows shell detected; run .claude/setup-discovery.ps1 instead (ln -s here copies the folder instead of linking it)."
        ;;
esac

claude_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(dirname -- "$claude_dir")
agents_dir="$claude_dir/agents"
skills_target="$repo_root/.agents/skills"
link="$claude_dir/skills"

# 1. Validate before creating anything.
if [ ! -d "$agents_dir" ] || [ -L "$agents_dir" ]; then
    fail "missing or linked .claude/agents; restore the tracked directory from Git."
fi
[ -d "$skills_target" ] || fail ".agents/skills not found; run this from a complete clone."
target_real=$(cd -- "$skills_target" && pwd -P)

# 2. Inspect an existing .claude/skills.
if [ -L "$link" ]; then
    link_real=$(cd -- "$link" 2>/dev/null && pwd -P) || link_real=""
    [ "$link_real" = "$target_real" ] || fail ".claude/skills points elsewhere; remove that link and rerun."
    echo "setup-discovery: already configured: .claude/skills -> ../.agents/skills"
    exit 0
fi
if [ -e "$link" ]; then
    fail ".claude/skills exists and is not a link; move it aside and rerun (edit skills only in .agents/skills)."
fi

# 3. Create, then 4. confirm.
ln -s ../.agents/skills "$link"
link_real=$(cd -- "$link" 2>/dev/null && pwd -P) || link_real=""
if [ ! -L "$link" ] || [ "$link_real" != "$target_real" ]; then
    fail "creating the symlink did not produce a working link at .claude/skills."
fi

# 5. Report.
echo "setup-discovery: created .claude/skills -> ../.agents/skills"
