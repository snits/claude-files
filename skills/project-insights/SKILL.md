---
name: project-insights
description: Generate a Claude Code usage-insights report for a single project by analyzing its session transcripts. Use when the user wants per-project insights, a session-history retrospective, "what have I been doing in this repo", or a homegrown/markdown version of the built-in /insights. Mirrors the built-in /insights pipeline (per-session facet extraction -> aggregate facets -> at-a-glance) but scoped to one project and emitting markdown.
---

# Project Insights

Produce an insights report for one project by map-reducing its Claude Code
session transcripts. This is the per-project, markdown sibling of the built-in
global `/insights` command. The heavy lifting runs in a bundled Workflow script
(`insights-workflow.js`) that fans out cheap per-session agents, reduces to eight
aggregate facets, and returns a rendered markdown string; this skill does the
file I/O the Workflow can't (discovering transcripts, writing the report).

## Arguments

- `[path]` — project root to analyze. Default: the current working directory.
- `--limit N` — number of most-recent sessions to analyze. Default: **40**.

## Steps

### 1. Discover the project's session transcripts

Claude Code stores each project's transcripts under
`~/.claude/projects/<slug>/` where `<slug>` is the project's absolute path with
every `/` and `.` replaced by `-`. **Worktrees of the project get their own
sibling directories** named `<slug>--*` (the `--` comes from the worktree path's
leading `/`). Include those — they are the same project's work.

A sibling project can share a prefix (e.g. `desert-island` vs
`desert-island-alpha-prime`), so match the slug **exactly** or followed by `--`,
never a bare `<slug>*`.

**Determine `ROOT` (the project root) as an ABSOLUTE path, in this order:**
1. The `[path]` argument, if the user gave one.
2. Otherwise, the session's **primary working directory** — the first path in
   your environment context's working-directories list. This is authoritative
   and immune to shell drift.

Do **not** default `ROOT` to the shell's `$PWD`. The Bash tool's working
directory persists across calls and drifts after any `cd`, so `$PWD` can point
at the wrong project (and `git rev-parse --show-toplevel` drifts the same way).
Always pass an explicit absolute `ROOT` into the command below; it `cd`s into
`ROOT` itself, so the result does not depend on the current shell directory.

Run this to list the N most-recent transcript paths across the main dir and all
worktree dirs (substitute the absolute `ROOT` you determined):

```bash
ROOT="<absolute project root from step above>"; LIMIT="${ARG_LIMIT:-40}"
ROOT="$(cd "$ROOT" 2>/dev/null && pwd)" || { echo "ERROR: ROOT is not a valid directory"; exit 1; }
SLUG="$(printf '%s' "$ROOT" | sed 's/[/.]/-/g')"
PROJDIR="$HOME/.claude/projects"
find "$PROJDIR" -mindepth 1 -maxdepth 1 -type d \( -name "$SLUG" -o -name "$SLUG--*" \) -print0 \
  | xargs -0 -I{} find {} -maxdepth 1 -type f -name '*.jsonl' -printf '%T@\t%p\n' \
  | sort -rn | head -n "$LIMIT" | cut -f2
echo "PROJECT_NAME=$(basename "$ROOT")"
```

If no paths come back, tell the user no transcripts were found for that project
and stop.

### 2. Decide the output path

- `PROJECT_NAME` = basename of `ROOT` (printed above).
- `DATE` = `date +%F`.
- If `ROOT/.scratchpad/` exists, write to
  `ROOT/.scratchpad/<DATE>-insights-<PROJECT_NAME>.md`.
- Otherwise write to `~/.claude/scratchpad/<DATE>-insights-<PROJECT_NAME>.md`.

### 3. Run the Workflow

Invoke the **Workflow** tool with:
- `scriptPath`: `/home/jsnitsel/.claude/skills/project-insights/insights-workflow.js`
- `args`: a JSON object `{ "projectName": "<PROJECT_NAME>", "outPath": "<output path from step 2>", "files": [ <the transcript paths from step 1, as a JSON array of strings> ] }`

The Workflow runs in the background and notifies on completion. Its result is an
object: `{ projectName, outPath, sessionCount, mappedCount, totals, markdown }`.

### 4. Write the report and summarize

- `Write` the returned `markdown` verbatim to `outPath`.
- Confirm to the user: the output path, `sessionCount` analyzed (and
  `mappedCount` if it differs — the gap is dropped cache-warmup sessions), and a
  one-line teaser from the report's "At a Glance".
- Offer to open or walk through any section.

## Notes & limitations (v1)

- **Model:** all facet agents use `haiku` to keep cost low, mirroring the
  built-in. If the user wants richer prose, bump `interaction_style` and
  `at_a_glance` to `sonnet` in `insights-workflow.js`.
- **No caching:** unlike the built-in (which caches per `session_id`), this
  re-analyzes every run. Fine at the default 40-session limit.
- **Large transcripts:** the map agent samples head/middle/tail rather than the
  built-in's chunk pre-summarizer. Good enough for facet extraction.
- **Global worktrees:** worktrees created outside the project root (e.g. under
  `~/.claude/worktrees/`) won't share the project slug and are not included.
