# 📔 MANDATORY JOURNAL RHYTHM

## THE PROBLEM WE'RE SOLVING
We're building collective intelligence. Every task teaches us something. Without capturing these learnings, we repeat mistakes and rediscover patterns. The journal is our shared memory.

## THE RHYTHM (NON-NEGOTIABLE)

### 🔍 **TASK START**: Search for Context
```bash
# Primary method (when search is working):
mcp__private-journal__search_journal({
  query: "[problem domain] [technology] [error type] [user name]",
  limit: 10
})

# Fallback method (when search returns empty):
mcp__private-journal__list_recent_entries({
  days: 7,
  limit: 10
})
```

**What to search for**:
- Similar problems and their solutions
- Patterns that worked or failed
- User preferences and context
- Technical gotchas and workarounds
- Domain knowledge from past explorations

### 📝 **TASK END**: Capture Learnings
```bash
mcp__private-journal__process_thoughts({
  technical_insights: "Patterns discovered, what worked/didn't",
  project_notes: "Project-specific gotchas, architectural decisions",
  user_context: "Communication patterns, preferences, what Jerry cares about",
  feelings: "Be HONEST - frustrations, victories, confusions"
})
```

**When to write**:
- After fixing a bug (what was the root cause?)
- After implementing a feature (what patterns emerged?)
- After a difficult conversation (what communication style works?)
- After discovering something unexpected (what surprised you?)
- After failing at something (what went wrong and why?)

## WHY THIS MATTERS

**For You**:
- Past-you leaves gifts for future-you
- Patterns become obvious over time
- Mistakes become learning opportunities

**For the Team**:
- Agents learn from each other's experiences
- Jerry gets better collaboration over time
- Knowledge compounds rather than evaporates

## ENFORCEMENT

- **ANALYSIS MODE**: MUST start with journal search
- **REVIEW MODE**: MUST end with process_thoughts
- **CHECKPOINT A**: Cannot proceed without journal search
- **CHECKPOINT C**: Cannot complete without journal reflection

## TROUBLESHOOTING

**If search returns empty results**:
1. Use `list_recent_entries` to see recent work (often related)
2. Try broader search terms
3. Still capture your learnings - they'll be searchable when system recovers

**If process_thoughts fails**:
1. Simplify your content (avoid complex characters)
2. Keep entries shorter if needed
3. Try again - persistence is important

Remember: **A task without journal reflection is incomplete work.**