# Journal Implementation Guide

## Search Strategy
```bash
# Search for relevant context at task start
mcp__private-journal__search_journal({
  query: "[domain] [problem-type] [technology-stack]",
  limit: 10
})

# If search returns empty, use:
mcp__private-journal__list_recent_entries({
  days: 7,
  limit: 10
})
```

## Reflection Strategy
```bash
# Document learnings at task completion
mcp__private-journal__process_thoughts({
  technical_insights: "What patterns worked? What failed?",
  project_notes: "Project-specific discoveries and decisions",
  user_context: "User preferences and collaboration insights",
  feelings: "Honest reflections on challenges and victories"
})
```

## Search Targets
- **Prior solutions**: Has this problem been solved before?
- **Failed approaches**: What didn't work previously and why?
- **User preferences**: How does Jerry prefer this handled?
- **Technical gotchas**: Domain-specific pitfalls and patterns
- **Architectural decisions**: Previous design choices and rationale

## When to Write Journal Entries
- After fixing a bug (root cause analysis)
- After implementing a feature (patterns that emerged)
- After difficult conversations (communication insights)
- After discovering something unexpected (surprises and learnings)
- After failed attempts (what went wrong and why)

## Why This Matters
- Past work leaves gifts for future tasks
- Patterns become obvious over time
- Mistakes become learning opportunities
- Knowledge compounds rather than evaporates
- Agents learn from each other's experiences

## Troubleshooting
**If search returns empty results**:
1. Use `list_recent_entries` to see recent work
2. Try broader search terms
3. Still capture your learnings for future searches

**If process_thoughts fails**:
1. Simplify content (avoid complex characters)
2. Keep entries shorter if needed
3. Try again - persistence is important

Remember: **A task without journal reflection is incomplete work.**