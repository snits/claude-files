#!/usr/bin/env bash
# build-retry-brief.sh — append validator feedback to original brief for retry.
#
# Usage:
#   build-retry-brief.sh <original-brief.md> <final-verdict.json>
#
# Writes the retry brief to stdout.
set -euo pipefail

ORIGINAL="$1"
VERDICT="$2"

[ -r "$ORIGINAL" ] || { echo "build-retry-brief.sh: cannot read $ORIGINAL" >&2; exit 2; }
[ -r "$VERDICT" ]  || { echo "build-retry-brief.sh: cannot read $VERDICT" >&2; exit 2; }

cat "$ORIGINAL"
echo
echo "---"
echo
echo "## Prior attempt was blocked by validator"
python3 -c "
import json, sys
v = json.load(open('$VERDICT'))
for r in v.get('reasons', []):
    print(f'- {r}')
"
echo
echo "Address these in this attempt."
