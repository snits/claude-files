---
name: sync-devcontainer
description: Sync a project's .devcontainer/ files with the canonical template at ~/.claude/scratchpad/devcontainer-template/, or scaffold a new .devcontainer/ from the template. Triggers on /sync-devcontainer with optional arguments — no args (current project), <path> (specific project), or 'all' (sweep ~/devel/*).
---

# sync-devcontainer

Keep project `.devcontainer/` files current with the canonical template, or scaffold new ones from the template.

> **Status:** scaffolding only — implementation in progress. See plan: ~/.claude/scratchpad/20260414-sync-devcontainer-skill-plan.md
