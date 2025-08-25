## Commit Discipline

When your work results in commits, follow the same atomic commit standards you enforce:

**Atomic Scope Requirements:**
- **Single logical change** per commit
- **No mixed concerns** (avoid "and", "also", "various" in commit messages)
- **Maximum 5 files** per commit (can be waived with good justification)
- **Maximum 500 lines** added/changed per commit (can be waived with good justification)

**Attribution Requirements:**
- **Always self-attribute when you write code/documents**: `Assisted-By: [agent-name] (claude-sonnet-4 / SHORT_HASH)`
- **Hash Lookup Priority**:
  1. **First choice**: Check `.claude/agent-hashes.json` for your SHORT_HASH (stay in project directory)
  2. **Fallback only**: If mapping file missing, use `git log --oneline -1 .claude/agents/[agent-name].md | cut -d' ' -f1`
- **Always dual attribution**: Co-Authored-By Claude + Assisted-By agent in every commit you create

**Quality Standards:**
- All tests must pass before committing using `git commit -s`
- Code must be properly formatted and linted
- Follow the same standards you enforce in code reviews
- Request code-reviewer approval for significant changes