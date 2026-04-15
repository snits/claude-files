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
