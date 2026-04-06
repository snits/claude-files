#!/bin/bash
# ABOUTME: Detects Claude Code version changes at session start.
# ABOUTME: Nudges the user to run /whats-new when a new version is found.

set -euo pipefail

VERSION_FILE="$HOME/.claude/last-evaluated-version"
# Get current version
current_version=$(claude --version 2>/dev/null | head -1 | sed 's/ (Claude Code)//')

if [ -z "$current_version" ]; then
  exit 0
fi

# Read last evaluated version
last_version=""
if [ -f "$VERSION_FILE" ]; then
  last_version=$(cat "$VERSION_FILE")
fi

# If versions match, nothing to do
if [ "$current_version" = "$last_version" ]; then
  exit 0
fi

# Version changed — update tracker and notify
echo "$current_version" > "$VERSION_FILE"

echo "Claude Code updated: ${last_version:-unknown} → ${current_version}. Run /whats-new to see what changed and how it affects your config."
