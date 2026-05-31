#!/usr/bin/env bash
# Tests for sync-scratchpad.sh — self-contained, no external deps.
set -uo pipefail
export GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=test@example.com
export GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=test@example.com

SCRIPT="$(cd "$(dirname "$0")/.." && pwd)/sync-scratchpad.sh"
PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf 'ok   - %s\n' "$1"; }
nok() { FAIL=$((FAIL+1)); printf 'FAIL - %s\n' "$1"; }
check(){ if [ "$2" = "$3" ]; then ok "$1"; else nok "$1 (want [$3] got [$2])"; fi; }

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
CENTRAL="$TMP/central/projects"; mkdir -p "$CENTRAL"

run_sync() { # $1 = project dir the "session" runs in
  SCRATCHPAD_CENTRAL_PROJECTS="$CENTRAL" \
  SCRATCHPAD_SYNC_LOG="$TMP/sync.log" \
  CLAUDE_PROJECT_DIR="$1" \
    bash "$SCRIPT"
}

# Case 1: non-git dir → no-op, exit 0, no dest created
mkdir -p "$TMP/plain"; run_sync "$TMP/plain"; check "non-git dir exits 0" "$?" "0"
[ ! -e "$CENTRAL/plain" ] && ok "non-git: no dest created" || nok "non-git: no dest created"

# Case 2: basic sync, slug = repo basename
proj="$TMP/myproj"; mkdir -p "$proj/.scratchpad"
git -C "$proj" init -q -b main; git -C "$proj" commit -q --allow-empty -m init
echo "hello" > "$proj/.scratchpad/note.md"
run_sync "$proj"
[ -f "$CENTRAL/myproj/note.md" ] && ok "basic sync copies file" || nok "basic sync copies file"
check "synced content" "$(cat "$CENTRAL/myproj/note.md" 2>/dev/null)" "hello"

# Case 3: worktree session → slug resolves to MAIN checkout basename
wt="$TMP/wt1"; git -C "$proj" worktree add -q "$wt" -b wtbranch
echo "fromwt" > "$proj/.scratchpad/wt.md"
run_sync "$wt"
[ -f "$CENTRAL/myproj/wt.md" ] && ok "worktree syncs to main slug (myproj)" || nok "worktree syncs to main slug (myproj)"
[ ! -d "$CENTRAL/wt1" ] && ok "worktree name not used as slug" || nok "worktree name not used as slug"

# Case 4: missing .scratchpad → no-op, no dest created
proj2="$TMP/noscratch"; mkdir -p "$proj2"; git -C "$proj2" init -q -b main
run_sync "$proj2"; check "missing .scratchpad exits 0" "$?" "0"
[ ! -d "$CENTRAL/noscratch" ] && ok "missing .scratchpad: no dest created" || nok "missing .scratchpad: no dest created"

# Case 5: additive — file removed from source is retained in central
rm "$proj/.scratchpad/note.md"; run_sync "$proj"
[ -f "$CENTRAL/myproj/note.md" ] && ok "additive: deleted source file retained" || nok "additive: deleted source file retained"

echo ""; echo "PASS=$PASS FAIL=$FAIL"; [ "$FAIL" -eq 0 ]
