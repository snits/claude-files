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
