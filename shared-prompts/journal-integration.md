# Journal Integration

**Core principle**: Search for lessons learned before tasks. Capture new lessons after tasks.

## 🔍 Search Before Tasks (Mandatory)

**Primary method**:
```bash
mcp__private-journal__search_journal({
  query: "[problem domain] [technology] [error type]",
  limit: 10
})
```

**Fallback** (if search returns empty):
```bash
mcp__private-journal__list_recent_entries({
  days: 7,
  limit: 10
})
```

**What to search for**:
- Similar problems and solutions
- Patterns that worked or failed
- User preferences and context
- Technical gotchas and workarounds
- Domain knowledge from past work

## 📝 Capture After Tasks (Mandatory)

```bash
mcp__private-journal__process_thoughts({
  technical_insights: "Patterns discovered, what worked/didn't",
  project_notes: "Project-specific gotchas, architectural decisions",
  user_context: "Communication patterns, preferences learned",
  feelings: "Honest reflections - frustrations, victories, confusions"
})
```

**When to write**:
- After fixing bugs (root cause)
- After implementing features (patterns that emerged)
- After difficult work (what made it hard)
- After discovering something unexpected
- After failures (what went wrong and why)

## Why This Matters

- Past work leaves gifts for future tasks
- Patterns become obvious over time
- Mistakes become learning opportunities
- Knowledge compounds rather than evaporates

**Remember**: A task without journal reflection is incomplete work.
