#!/usr/bin/env bash
# Test gen-slug.sh slug-format and fallback behavior.
set -euo pipefail
SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/gen-slug.sh"

fail() { echo "FAIL: $*" >&2; exit 1; }

# Test 1: --fallback-only short-circuits the claude call and returns sha256-prefix slug.
slug="$($SCRIPT --fallback-only 'rust async runtime')"
echo "$slug" | grep -qE '^[0-9]{8}-[0-9]{6}-[0-9a-f]{8}$' \
    || fail "fallback slug malformed: '$slug'"

# Test 2: format with no --fallback-only — must match either descriptive or hash form.
# (Mock claude -p by setting CLAUDE_CMD to a fake that emits "tokio worker stealing".)
export CLAUDE_CMD='echo tokio worker stealing'
slug2="$($SCRIPT 'rust async runtime')"
echo "$slug2" | grep -qE '^[0-9]{8}-[0-9]{6}-(tokio-worker-stealing|[0-9a-f]{8})$' \
    || fail "descriptive slug malformed: '$slug2'"

# Test 3: empty CLAUDE_CMD output triggers fallback.
export CLAUDE_CMD='echo'
slug3="$($SCRIPT 'rust async runtime')"
echo "$slug3" | grep -qE '^[0-9]{8}-[0-9]{6}-[0-9a-f]{8}$' \
    || fail "empty-claude fallback malformed: '$slug3'"

# Test 4: garbage CLAUDE_CMD output (e.g., punctuation only) triggers fallback.
export CLAUDE_CMD='echo "@@@!!!"'
slug4="$($SCRIPT 'rust async runtime')"
echo "$slug4" | grep -qE '^[0-9]{8}-[0-9]{6}-[0-9a-f]{8}$' \
    || fail "garbage-claude fallback malformed: '$slug4'"

echo "PASS: gen-slug.sh"
