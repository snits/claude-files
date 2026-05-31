#!/usr/bin/env bash
# Capture a project's .scratchpad/ into the canonical store (additive, no --delete).
# Best-effort: always exits 0 so it never blocks session start/end. Logs failures.
set -uo pipefail

CENTRAL_PROJECTS="${SCRATCHPAD_CENTRAL_PROJECTS:-$HOME/.claude/scratchpad/projects}"
LOG_FILE="${SCRATCHPAD_SYNC_LOG:-$HOME/.claude/logs/scratchpad-sync.log}"

log() { mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null; printf '[%s] %s\n' "$(date -Iseconds)" "$*" >>"$LOG_FILE" 2>/dev/null; }

dir="${CLAUDE_PROJECT_DIR:-$PWD}"

# Resolve the MAIN checkout even when the session runs in a worktree.
common_git=$(git -C "$dir" rev-parse --path-format=absolute --git-common-dir 2>/dev/null) \
  || { log "skip: $dir not a git repo"; exit 0; }
main_root=$(dirname "$common_git")
slug=$(basename "$main_root")

src="$main_root/.scratchpad"
dest="$CENTRAL_PROJECTS/$slug"

[ -d "$src" ] || { log "skip: no $src"; exit 0; }
mkdir -p "$dest"
rsync -a "$src/" "$dest/" || { log "ERROR: rsync failed for $slug"; exit 0; }
log "synced $src -> $dest"
exit 0
