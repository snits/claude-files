#!/usr/bin/env bash
set -euo pipefail
SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/abandon.sh"

FAKE_HOME="$(mktemp -d)"
export HOME="$FAKE_HOME"
SLUG="20260502-143000-abandon-test"
RO="$HOME/research-out"
VAULT="$HOME/.claude/scratchpad/research-vault"

mkdir -p "$RO/$SLUG" "$RO/${SLUG}-retry1" "$RO/${SLUG}-retry2"
touch "$RO/$SLUG/x" "$RO/${SLUG}-retry1/x" "$RO/${SLUG}-retry2/x"
mkdir -p "$VAULT"  # vault should not be touched

"$SCRIPT" "$SLUG"

[ ! -d "$RO/$SLUG" ] || { echo "FAIL: original not removed"; exit 1; }
[ ! -d "$RO/${SLUG}-retry1" ] || { echo "FAIL: retry1 not removed"; exit 1; }
[ ! -d "$RO/${SLUG}-retry2" ] || { echo "FAIL: retry2 not removed"; exit 1; }
[ ! -d "$VAULT/$SLUG" ] || { echo "FAIL: vault entry was created (should not be)"; exit 1; }

echo "PASS: abandon.sh"
