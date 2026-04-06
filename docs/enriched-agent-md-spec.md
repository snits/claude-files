# Enriched Agent MD Specification

A single-file-as-system-prompt architecture for Claude Code agents with optional supporting directories for persistent state.

## Architecture

Every agent is defined by a single markdown file placed in `.claude/agents/`:

```
.claude/agents/
  agent-name.md           # System prompt (the agent's identity and behavior)
  agent-name/             # Optional supporting directory
    memory/
      README.md           # Format instructions and save criteria
      MEMORY.md           # Index of memory entries
      *.md                # Individual memory files
    references/           # Reference material the agent consults
    shared/               # Output directory (solo agents only)
```

The `.md` file is the agent. Everything in it becomes the agent's system prompt via native dispatch (`Agent(subagent_type="agent-name")`). The supporting directory is optional and lazily created.

## Dispatch

All agents use native dispatch. There is no two-tier system.

```
Agent(subagent_type="agent-name", prompt="[task description]")
```

The `description` field in frontmatter controls when the orchestrator selects this agent. Write it as a dispatch prompt with concrete trigger conditions and worked examples — it's load-bearing for agent selection.

## File References

File references (`@path/to/file`) in agent `.md` files are **not auto-expanded** into the system prompt. The agent sees the path as text and must actively Read the file. This is confirmed behavior as of 2026-04-04.

Design accordingly: inline everything that shapes behavior, reference paths only for content the agent reads on demand.

## Section Ordering

Section ordering is mandatory. It exploits attention effects and enables partial loading for design meetings.

```
frontmatter (name, description, color)

─── PRIMACY ZONE (identity + boundaries) ───
## Identity
## Voice
## Contract

─── OPERATIONAL CORE ───
## Reasoning Process
## Process / Expertise
## Team Relationships

─── SUPPLEMENTARY (may reference files) ───
## Memory
## References
## Project Context

─── RECENCY ZONE (active constraints) ───
## Anti-Patterns
## Off-Limits
```

**Identity and Voice must always be the first two body sections.** This enables loading the first ~30 lines for design-meeting reviewer assignment without loading the full agent.

## Inline/Reference Rule

**Anything that constrains agent behavior MUST be inline. Anything that informs agent work MAY be referenced by path.**

| Section | Placement | Rationale |
|---------|-----------|-----------|
| Identity | Must be inline | Core identity — system-prompt strength required |
| Voice | Must be inline | Behavioral shaping — system-prompt strength required |
| Contract | Must be inline | Scope boundaries — system-prompt strength required |
| Reasoning Process | Must be inline | Analytical structure — system-prompt strength required |
| Process / Expertise | Default inline | May reference external files if exceptionally long |
| Team Relationships | Default inline | May reference if team is very large |
| Memory | Reference by path | Supplementary, dynamic, grows over time |
| References | Reference by path | Supplementary, informational |
| Project Context | Inline | Project-specific, but small enough to inline |
| Anti-Patterns | Must be inline | Active constraints — recency-zone strength required |
| Off-Limits | Must be inline | Hard boundaries — recency-zone strength required |

## Quality Floor

The behavioral minimum for native dispatch: **Identity + Voice + Contract.**

- Without Voice, the agent has no distinct behavior — it defaults to generic Claude voice.
- Without Contract, the agent has no scope boundaries — scope bleed is the default.

Agents below this threshold work but get marginal benefit from native dispatch over general-purpose dispatch with a role prompt.

## Templates

Two templates at `~/.claude/templates/`:

- **`agent-quick-start.md`** (~25 lines): frontmatter + Identity + Contract + Process. For domain-focused utility agents. Includes graduation guidance.
- **`agent-full.md`** (~60 lines skeleton): Full section set for personality-driven agents. Includes zone comments and creation instructions.

The template choice is a complexity gradient, not a tier gate. Start with quick-start, graduate to full when the agent needs stronger persona.

## Supporting Directory

### When to Create

Don't create `agent-name/` until the agent actually needs it. Most agents start as a single `.md` file.

Create the supporting directory when:
- The agent needs persistent memory across sessions
- The agent has reference material to consult
- The agent produces output that others consume (solo agents)

### Bootstrap Pattern

When creating a memory directory:

```bash
mkdir -p .claude/agents/agent-name/memory
```

Add a `README.md` with format instructions and save criteria, and an empty `MEMORY.md` index. The system prompt line stays minimal:

```
You have persistent memory at `.claude/agents/agent-name/memory/`.
Check `MEMORY.md` at the start of each session.
```

Detailed format instructions belong in the directory's `README.md`, not in the system prompt. This minimizes boilerplate that dilutes persona-specific content.

### Input/Output Separation

The supporting directory mixes inputs (`memory/`, `references/`) with outputs (`shared/`). Agent instructions in the `.md` file must use explicit, separate path references for each — never a generic "your directory" pointer.

## Shared Output Directories

Two conventions based on context:

**Team agents** write to a team-level shared directory:
```
shared/agent-name/    # e.g., shared/upstream/
```
This preserves cross-agent output discovery. An agent or human looking for "what has the team produced" goes to one place.

**Solo agents** write to a per-agent directory:
```
agent-name/shared/    # Inside the supporting directory
```

The agent's `## Contract` section documents which convention applies.

## Staff Library and Forking

### Staff Directory

`~/desert-island/staff/agents/` is the canonical library for Desert Island Games agents. Project agents are forked from staff.

### Fork Workflow

1. Copy the `.md` file to the project's `.claude/agents/`
2. Start with an empty supporting directory (staff memories are staff context)
3. Add a `## Project Context` section for project-specific additions
4. Leave staff-originated sections unchanged when possible

Staff agents are seeds, not controlled templates. Once forked, they're independent.

### Propagation

Maintain a `staff/CHANGELOG.md` — when staff agents are updated, note what changed so project maintainers can decide whether to pull changes. No enforcement, no tooling, just visibility.

### Rename Convention (Substitution Test)

**When a forked agent's Identity section no longer describes the same archetype, rename the fork.**

Test: read the staff version's Identity opening paragraph. Read the fork's. If they describe fundamentally different specialists, rename. If they describe the same archetype in a different project context, keep the name.

Examples:
- Staff "tournament veteran who's seen every format failure mode" forked as "educational programming competition specialist" → **Rename** (different archetype)
- Staff competitive-play-designer forked to phoenix, identical archetype → **Keep name**
- Staff agent missing a section that was added later → **Keep name** (drift, not divergence)

The new name reflects what the agent IS, not its genealogy. `educational-competition-designer`, not `competitive-play-designer-v2`.

## Memory Hygiene

No formal rules. When significantly revising an agent's personality (new archetype, different domain, rewritten reasoning process), review its memory directory. Memories written under the old personality may conflict with the new one — they're formatted through the old persona's lens. Archive or delete memories that assume the old identity. Git history preserves everything.

If the rename convention is followed, this case is rare — renamed forks start with empty memory.

## Agent Lifecycle

### Creation
1. Choose a template (quick-start or full)
2. Fill in frontmatter and required sections
3. Place in `.claude/agents/` (global) or `project/.claude/agents/` (project-level)
4. Agent is available after next session start

### Modification
Edit the `.md` file directly. Changes take effect at next agent dispatch.

### Forking
Copy `.md` to target project. Add `## Project Context`. Start fresh supporting directory.

### Retirement
Move `.md` to `retired/agent-name.md`. Archive supporting directory to `retired/agent-name/`. Memory and shared output preserved for reference.

### Agent Discovery
Claude Code registers available agents at session start. New agent files created mid-session require a session restart to become dispatchable.

## Design Provenance

Architecture designed 2026-04-04 via design meeting with three reviewers (systems-architect, dev-experience, agent-behavior). Full meeting report at `~/.claude/scratchpad/meetings/agent-architecture-meeting/report.md`.

@ file expansion tested empirically 2026-04-04: neither plain path references nor `@path` references auto-expand into the agent's system prompt. Agents must actively Read referenced files.
