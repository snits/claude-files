---
name: sync-devcontainer
description: Sync a project's .devcontainer/ files with the canonical template at ~/.claude/scratchpad/devcontainer-template/, or scaffold a new .devcontainer/ from the template. Triggers on /sync-devcontainer with optional arguments — no args (current project), <path> (specific project), or 'all' (sweep ~/devel/*).
---

# sync-devcontainer

Keep project `.devcontainer/` files current with the canonical template, or scaffold new ones from the template.

## Usage

| Form | Behavior |
|---|---|
| `/sync-devcontainer` | Operate on the current working directory |
| `/sync-devcontainer <path>` | Operate on the specified project path (relative or absolute) |
| `/sync-devcontainer all` | Sweep every directory under `~/devel/*` that has a `.devcontainer/` subdirectory |

## Constants

- **Template source:** `~/.claude/scratchpad/devcontainer-template/`
- **Sweep root:** `~/devel/`
- **Files synced:** `devcontainer.json`, `local.env.example`
- **Files compared but not merged:** `Dockerfile` (footnote in summary if it differs)
- **Files ignored:** everything else in the template directory (e.g., `RECIPES.md`)

## Mode detection

For each target (cwd, an explicit path, or one entry during a sweep):

1. If the target's `.devcontainer/` directory does not exist, OR exists but is empty → **scaffold mode**.
2. Otherwise → **sync mode**.

For invocation argument `all`:

1. Enumerate `~/devel/*/` directories.
2. Filter to those with a non-empty `.devcontainer/` subdirectory. Skip the rest — sweep mode does NOT auto-scaffold projects that lack a `.devcontainer/`, because some `~/devel/` dirs (scratch space, forks, drafts) intentionally don't have one.
3. Run sync mode against each filtered target, in sequence (not parallel — conflict prompts must not interleave).
4. After all targets, print the aggregate summary.

## Sync mode: `devcontainer.json`

This is the heart of the skill. Walk the JSON structure of the template and project files in parallel, applying these rules at each node:

### Object nodes (e.g., `containerEnv`, `postCreateCommand`)

For each key in the template's object:
- **Key present in project, equal value** → no-op, skip silently.
- **Key absent in project** → ADD silently (this is an "addition"). Insert into the project's object preserving the project's existing key order; append at the end.
- **Key present in project, different value** → CONFLICT. Prompt the user (see "Conflict prompt" section below). Do not write yet.

For each key in the project's object that is NOT in the template's object:
- → PRESERVE silently. This is a project-specific entry. Never delete it.

### Array nodes (e.g., `mounts`, `runArgs`)

Treat each element as a unit. Compare elements between template and project:
- **Element string equal** in both → no-op, skip.
- **Element in template, not in project** → ADD silently (append to project's array, preserving project's existing element order).
- **Element in project, not in template** → PRESERVE silently.

**Special case for `mounts`:** entries are strings shaped like `source=...,target=...,type=bind,...`. Two strings that differ in any character compare as unequal under string equality, which would generate a spurious "remove + add" diff if e.g. `consistency=cached` were added or removed by the template. Mitigation:

For the `mounts` array specifically, additionally compare entries by their `target=` substring. If both arrays have an entry with the same `target=`:
- Treat them as the same logical mount (do not double-add).
- If the rest of the entry string differs, trigger a CONFLICT prompt for that mount (do not silently apply the template's version, since the project may have intentional mount options like `readonly`).

### Scalar nodes at root (e.g., `name`, `remoteUser`)

- **Equal** → no-op.
- **Different** → CONFLICT prompt.

### Implementation notes

- Read both JSON files via the Read tool.
- Compute the merged result in memory by walking the structures per the rules above.
- Use the Edit tool to insert additions one at a time, preserving the project file's overall formatting (indentation, trailing newlines). Do NOT rewrite the entire file via Write — that would lose formatting nuances and any trailing comments.
- For each addition applied, increment counters for the per-project summary (mounts, env vars, postCreateCommand entries, etc.).

## Conflict prompt

When the merge encounters a value mismatch (object key with different value, mount with same `target=` but different rest, or root scalar that differs), pause and present this prompt to the user, then wait for input:

```
CONFLICT in <project-name>/.devcontainer/devcontainer.json
Path: <dotted JSON path, e.g., containerEnv.OPENAI_CHAT_BASE_URL>
  template: <template's value, JSON-quoted>
  project:  <project's value, JSON-quoted>

Apply template / keep project / show context / skip? [t/k/c/s]
```

Response handling:
- `t` (apply template) — overwrite project's value with template's. Increment "conflicts resolved (took template)" counter.
- `k` (keep project) — leave project's value unchanged. Increment "conflicts resolved (kept project)" counter.
- `c` (show context) — print the surrounding 3-5 lines of raw JSON from both files (use `jq` or grep the context window) to help the user decide. Then re-prompt with `[t/k/s]` (no `c` again — single context display per conflict).
- `s` (skip) — do not modify this entry, but DO NOT count as resolved. Increment "conflicts skipped" counter. The drift remains; the user is opting to deal with it later.

After resolution, continue the merge from the next node. Do not abort the whole sync on a single conflict.

If the user aborts (Ctrl+C) mid-prompt, leave files in their current state. Per-file writes are atomic via the Edit tool, so any additions applied before the conflict remain. Report partial completion in the summary: "<project>: aborted at conflict on <path>; N additions applied before abort".

## Sync mode: `local.env.example`

`local.env.example` is documentation, not config. If the template's version differs from the project's (use `cmp` or compare file contents), overwrite the project's with the template's. No merge logic. Increment a "local.env.example overwritten" counter for the summary.

If the project does not have a `local.env.example` at all, copy the template's in.

If the files are identical, no-op.

## Sync mode: `Dockerfile`

The Dockerfile is **not merged** by this skill. Project Dockerfiles can have project-specific package additions (e.g., alexandria adds `postgresql-server pgvector` to the dnf install line) that semantic merge would handle poorly.

Instead, after handling devcontainer.json and local.env.example:

1. Compare the project's Dockerfile to the template's via `diff`. If they differ in any non-whitespace way, add a single-line footnote to the per-project summary:

   ```
   ! Dockerfile differs from template. Run:
       diff ~/.claude/scratchpad/devcontainer-template/Dockerfile <project>/.devcontainer/Dockerfile
   ```

2. If the project has no Dockerfile but the template does, copy the template's in (this is the only Dockerfile write the skill ever performs, and only happens during scaffold mode in practice — sync mode would only encounter this if the project had `.devcontainer/devcontainer.json` but no Dockerfile, which is unusual but valid).

## Per-project summary format

After processing one project, print a summary block:

```
<project-name>/.devcontainer/devcontainer.json:
  + N mount(s) added
  + N env var(s) added (key1, key2, ...)
  + N postCreateCommand(s) added (key1, key2, ...)
  ~ N conflict(s) resolved (took template: keyA, keyB; kept project: keyC)
  ! N conflict(s) skipped (keyD)
<project-name>/.devcontainer/local.env.example: overwritten   (only if changed)
<project-name>/.devcontainer/Dockerfile: differs from template (run `diff ...`)   (only if differs)
```

Skip lines whose count is zero. If everything was a no-op, print:

```
<project-name>: up to date
```

Use the project's directory basename (not full path) as `<project-name>` to keep the summary readable.
