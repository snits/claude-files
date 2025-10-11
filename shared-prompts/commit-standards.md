# Commit Standards

**For comprehensive git safety protocols, see**: skills/collaboration/git-safety

## Commit Message Format

```
feat(scope): brief description

Detailed explanation of change and why it was needed.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
Assisted-By: [agent-name] ([model-name: for example claude-sonnet-4])
```

## Quick Reference

- **ALWAYS use**: `git commit -s` (sign-off required)
- **Forbidden flags**: `--no-verify`, `--no-hooks`, `--no-pre-commit-hook`
- **Feature branches**: Never commit directly to main
- **Agent attribution**: Required for all agent contributions

## Before ANY Commit

- [ ] All tests pass
- [ ] Type checking clean
- [ ] Linting satisfied
- [ ] Code formatting applied

**See skills/collaboration/git-safety for detailed workflows and protocols.**
