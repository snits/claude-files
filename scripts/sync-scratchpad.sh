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
# Allowlist intake (ruling: Jerry, 2026-08-29, kata claudes-home#6w27). The central
# store's contract is agent work products: markdown, diffs/patches, small scripts.
#
# ORDERING IS LOAD-BEARING AND IS THE REVERSE OF .gitignore's. rsync is
# FIRST-match-wins; .gitignore is LAST-match-wins. So the junk-tree excludes must
# come BEFORE --include='*/', or the include re-admits descent into them and a
# venv's thousands of *.py match the *.py rule. Do not "tidy" this into the same
# order as the .gitignore.
#
# -m (--prune-empty-dirs) is required: --include='*/' otherwise mirrors the entire
# directory skeleton of every project into the store.
# --exclude='.git/' stops nested checkouts arriving as embedded repos -- that is how
# projects/alexandria/qxq2-matrix and projects/rhkmaint-tools/revumatic became
# tracked gitlinks.
# --exclude='tmp/' is the funnel from kata claudes-home#ehph: .scratchpad/tmp/ is the
# designated bulk/ephemeral zone and never syncs.
# --max-size caps even allowed types; a 274 MiB .json proved text-extension != small.
# -F honours a per-directory .rsync-filter file, giving any subtree a local opt-out
# (`- *` inside one excludes that whole directory). Needed because the type
# allowlist cannot tell a vendored upstream CHECKOUT from agent work product --
# revumatic's ~75 *.py matched the allowlist perfectly. Structural funnel: see
# kata claudes-home#ehph.
rsync -a -m -F --max-size=10m \
  --exclude='.git/' \
  --exclude='.venv/' --exclude='venv/' --exclude='node_modules/' \
  --exclude='__pycache__/' --exclude='target/' --exclude='.tox/' \
  --exclude='.mypy_cache/' --exclude='.pytest_cache/' \
  --exclude='tmp/' \
  --include='*/' \
  --include='*.md' --include='*.diff' --include='*.patch' \
  --include='*.py' --include='*.sh' \
  --exclude='*' \
  "$src/" "$dest/" || { log "ERROR: rsync failed for $slug"; exit 0; }
log "synced $src -> $dest"
exit 0
