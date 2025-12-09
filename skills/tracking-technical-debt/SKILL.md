---
name: tracking-technical-debt
description: Track technical debt using UUID markers in code linked to beads for issue tracking
when_to_use: When you encounter or create technical debt that needs tracking rather than immediate fixing
version: 1.0.0
---

# Tracking Technical Debt

## Overview

Track technical debt by linking code comments to beads via UUIDs. No custom tooling needed - uses `uuid`, language-native comments, and beads for full lifecycle tracking.

## When to Track vs Fix

**Track as debt when:**
- Fix would derail current work
- Requires broader refactoring
- Needs design discussion
- Low priority but should not be forgotten
- Part of larger cleanup effort

**Just fix immediately when:**
- Takes less than 5 minutes
- Isolated change, no ripple effects
- Obvious fix, no design decisions
- Blocking current work anyway

**Never track as debt:**
- Security vulnerabilities (fix now or escalate)
- Broken tests (fix immediately)
- Build failures (fix immediately)

## The Workflow

### 1. Generate UUID

```bash
uuid -v 4
# Output: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### 2. Add Code Comment

Use language-appropriate comment syntax. Format:

```
DEBT[uuid-prefix]: CATEGORY - Brief description
```

**UUID prefix:** First 8 characters of UUID (enough to be unique, searchable)

**Categories:**
- `REFACTOR` - Code structure improvements
- `PERFORMANCE` - Optimization needed
- `CLEANUP` - Remove dead code, simplify
- `FIXME` - Known bug or issue
- `TODO` - Missing feature or incomplete
- `HACK` - Temporary workaround

**Examples by language:**

```typescript
// DEBT[a1b2c3d4]: REFACTOR - Extract validation logic to separate module
```

```python
# DEBT[a1b2c3d4]: PERFORMANCE - Replace O(n²) with hash lookup
```

```go
// DEBT[a1b2c3d4]: CLEANUP - Remove deprecated API calls after v2 migration
```

```rust
// DEBT[a1b2c3d4]: FIXME - Handle edge case when buffer is empty
```

```java
// DEBT[a1b2c3d4]: TODO - Add retry logic for transient failures
```

### 3. Create Bead

Use the `debt` label to identify debt items:

```bash
bd create --labels debt "REFACTOR: Extract validation logic to separate module"
```

Add category as additional label if useful:

```bash
bd create --labels debt,refactor "Extract validation logic to separate module"
bd create --labels debt,performance "Replace O(n²) with hash lookup"
```

### 4. Link UUID to Bead

Add the full UUID and file location as a comment:

```bash
bd comment <bead-id> "UUID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
Location: src/handlers/user.ts:142"
```

## Finding Debt

### By UUID (specific debt item)
```bash
rg "a1b2c3d4" .
```

### All debt markers
```bash
rg "DEBT\[" .
```

### By category
```bash
rg "DEBT\[.*\]: REFACTOR" .
rg "DEBT\[.*\]: PERFORMANCE" .
```

### In beads
```bash
bd list --label debt
bd show <bead-id>
```

## Analytics with bv

Once debt is tracked in beads, use bv for analytics:

```bash
# See what's blocking progress
bv --robot-insights

# Get execution plan for tackling debt
bv --robot-plan

# Priority recommendations
bv --robot-priority

# Filter to just debt items
bv --recipe debt  # if recipe exists, or filter manually
```

## Linking Debt to Features

When debt blocks feature work:

```bash
# Create feature
feature_id=$(bd create --type=feature "Add user dashboard" --json | jq -r '.id')

# Link existing debt as blocker
bd dep add "$feature_id" "$debt_bead_id"
```

Now `bv --robot-plan` will show debt must be resolved before feature.

## Closing Debt

When debt is resolved:

1. Remove the `DEBT[uuid]` comment from code
2. Close the bead: `bd close <bead-id> -r "Refactored in commit abc123"`

## Quick Reference

| Step | Command |
|------|---------|
| Generate UUID | `uuid -v 4` |
| Create bead | `bd create --labels debt "description"` |
| Add comment | `bd comment <id> "UUID: ... Location: ..."` |
| Find in code | `rg "DEBT\[" .` or `rg "<uuid-prefix>" .` |
| List all debt | `bd list --label debt` |
| Close debt | `bd close <id> -r "reason"` |

## Integration with Other Workflows

**During code review:** If reviewer spots debt, they can create the marker + bead.

**During implementation:** When you notice debt but can't fix now, track it and continue.

**Sprint planning:** Use `bv --robot-priority` to identify high-impact debt to address.

**Before major features:** Check `bv --robot-insights` for debt that might block progress.
