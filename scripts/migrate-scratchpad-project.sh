#!/usr/bin/env bash
# Migrate ONE project from .claude/scratchpad symlink to a real root .scratchpad/.
# Idempotent and safe to re-run. Usage: migrate-scratchpad-project.sh /abs/path/to/project
set -euo pipefail
proj="$1"
link="$proj/.claude/scratchpad"

[ -L "$link" ] || { echo "SKIP $proj: no .claude/scratchpad symlink (already migrated or n/a)"; exit 0; }
central=$(readlink -f "$link") || { echo "ERROR $proj: cannot resolve symlink $link"; exit 1; }
[ -d "$central" ] || { echo "ERROR $proj: symlink target $central missing"; exit 1; }

mkdir -p "$proj/.scratchpad"
rsync -a "$central/" "$proj/.scratchpad/"                       # seed working copy from canonical store

# Idempotent, newline-safe .gitignore append (avoids gluing onto a no-trailing-newline last line)
gi="$proj/.gitignore"
if ! grep -qxF '/.scratchpad/' "$gi" 2>/dev/null; then
  [ -s "$gi" ] && [ -n "$(tail -c1 "$gi")" ] && printf '\n' >>"$gi"
  printf '/.scratchpad/\n' >>"$gi"
fi

rm "$link"                                                      # remove old symlink last
echo "OK   $proj  (slug=$(basename "$central"))"
