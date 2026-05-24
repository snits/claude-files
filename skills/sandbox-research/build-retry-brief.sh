#!/usr/bin/env bash
# build-retry-brief.sh — append validator feedback to original brief for retry.
#
# Usage:
#   build-retry-brief.sh <original-brief.md> <final-verdict.json>
#
# Writes the retry brief to stdout.
set -euo pipefail

[ -n "${1:-}" ] && [ -n "${2:-}" ] || { echo "usage: build-retry-brief.sh <original-brief.md> <final-verdict.json>" >&2; exit 2; }

ORIGINAL="$1"
VERDICT="$2"

[ -r "$ORIGINAL" ] || { echo "build-retry-brief.sh: cannot read $ORIGINAL" >&2; exit 2; }
[ -r "$VERDICT" ]  || { echo "build-retry-brief.sh: cannot read $VERDICT" >&2; exit 2; }

cat "$ORIGINAL"
echo
echo "---"
echo
echo "## Prior attempt was blocked by validator"
# Path is interpolated into the python literal below; safe because callers pass
# slug-derived paths (sanitized to [a-z0-9-], no quotes/metacharacters).
python3 -c "
import json, sys
v = json.load(open('$VERDICT'))
for r in v.get('reasons', []):
    print(f'- {r}')
"
echo
echo "Address these in this attempt."
