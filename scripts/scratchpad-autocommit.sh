#!/bin/bash
# Auto-commit scratchpad changes at session start.
# Captures work from previous sessions automatically.
set -euo pipefail

SCRATCHPAD="$HOME/.claude/scratchpad"

# Skip if not a git repo
if [ ! -d "$SCRATCHPAD/.git" ]; then
  exit 0
fi

cd "$SCRATCHPAD"

# Stage all changes
git add -A

# Only commit if there are staged changes
if ! git diff --cached --quiet; then
  git commit -s -m "scratchpad: auto-commit $(date +%Y-%m-%d)

Co-authored-by: Claude <noreply@anthropic.com>" || {
    echo "WARNING: scratchpad auto-commit failed" >&2
  }
fi
