#!/bin/bash
# Auto-commit scratchpad changes at session start, then sync with origin.
#
# Captures work from previous sessions, pulls remote changes from other rigs,
# and pushes local commits upstream. All network operations are best-effort —
# failures log to ~/.claude/logs/scratchpad-autocommit.log but never block
# session start. Notable failures (rebase conflicts, push rejection) surface
# via systemMessage so the user sees them on session start.
#
# Task-in-progress suppression: if ~/.claude/scratchpad/.task-in-progress
# exists, skip the entire run (no commit, no pull, no push). Task workflows
# that make multiple commits across several sessions should create this
# marker before the first edit and remove it at task completion. Prevents
# the hook from interleaving generic "scratchpad: auto-commit <date>"
# commits with the workflow's descriptive task commits. See beads issue
# claudes-home-2p6.3 for motivation.

set -uo pipefail

SCRATCHPAD="$HOME/.claude/scratchpad"
LOG_DIR="$HOME/.claude/logs"
LOG_FILE="$LOG_DIR/scratchpad-autocommit.log"
TASK_MARKER="$SCRATCHPAD/.task-in-progress"

SYSTEM_MESSAGE=""

log() {
  printf '[%s] %s\n' "$(date -Iseconds)" "$*" >>"$LOG_FILE"
}

emit_and_exit() {
  if [ -n "$SYSTEM_MESSAGE" ]; then
    printf '{"systemMessage": "%s"}\n' "$SYSTEM_MESSAGE"
  fi
  exit 0
}

# Skip silently if scratchpad is not a git repo (e.g., pre-migration on a new rig)
[ -d "$SCRATCHPAD/.git" ] || exit 0

mkdir -p "$LOG_DIR"
cd "$SCRATCHPAD" || exit 0

# Suppress the whole run while a task workflow owns commit discipline.
# Covers: commit (avoids fragmenting the workflow's commits), pull (would
# rebase over uncommitted in-progress work), push (nothing new to push).
if [ -f "$TASK_MARKER" ]; then
  log "INFO: $TASK_MARKER present, suppressing auto-commit run"
  exit 0
fi

# Recover from a stuck rebase left over from a previous failed run
if [ -d ".git/rebase-merge" ] || [ -d ".git/rebase-apply" ]; then
  log "WARN: found in-progress rebase from a previous run, aborting"
  git rebase --abort >>"$LOG_FILE" 2>&1 || log "ERROR: git rebase --abort failed"
  SYSTEM_MESSAGE="scratchpad-autocommit recovered from a stuck rebase. See ~/.claude/logs/scratchpad-autocommit.log"
fi

# Stage and commit any local changes (clean working tree before network ops)
git add -A >>"$LOG_FILE" 2>&1 || log "WARN: git add -A returned non-zero"

if ! git diff --cached --quiet; then
  if ! git commit -s -m "scratchpad: auto-commit $(date +%Y-%m-%d)

Co-authored-by: Claude <noreply@anthropic.com>" >>"$LOG_FILE" 2>&1; then
    log "ERROR: git commit failed"
    SYSTEM_MESSAGE="scratchpad-autocommit: commit failed. See ~/.claude/logs/scratchpad-autocommit.log"
    emit_and_exit
  fi
fi

# Skip network ops if no upstream is configured
if ! git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
  log "INFO: no upstream tracking branch, skipping pull/push"
  emit_and_exit
fi

# Pull with rebase to incorporate remote changes from other rigs.
# Working tree is clean here, so --autostash is defensive only.
if ! git pull --rebase --autostash >>"$LOG_FILE" 2>&1; then
  log "ERROR: git pull --rebase failed"
  if [ -d ".git/rebase-merge" ] || [ -d ".git/rebase-apply" ]; then
    git rebase --abort >>"$LOG_FILE" 2>&1 || log "ERROR: rebase --abort also failed"
    SYSTEM_MESSAGE="scratchpad-autocommit: rebase conflict during pull, aborted. Manual sync needed. See ~/.claude/logs/scratchpad-autocommit.log"
  else
    SYSTEM_MESSAGE="scratchpad-autocommit: pull failed (network or auth?). See ~/.claude/logs/scratchpad-autocommit.log"
  fi
  emit_and_exit
fi

# Push local commits to origin
if ! git push >>"$LOG_FILE" 2>&1; then
  log "ERROR: git push failed"
  SYSTEM_MESSAGE="scratchpad-autocommit: push failed. See ~/.claude/logs/scratchpad-autocommit.log"
  emit_and_exit
fi

# Silent success
exit 0
