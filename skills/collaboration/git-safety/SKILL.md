---
name: Git Safety Protocols
description: Non-negotiable git commit safety protocols - forbidden flags, pre-commit handling, quality gates
when_to_use: Before ANY commit. When pre-commit hooks fail. When tempted to use --no-verify. When under time pressure. When user waiting. When tired or rushing. When "just formatting" or "trivial change". When production issue needs quick deploy.
version: 1.0.0
languages: all
---

# Git Safety Protocols

## Overview

**Core principle:** Quality gates protect you when you're most vulnerable - tired, rushing, under pressure.

**Claude Code baseline:** Built-in Bash tool already prohibits destructive git operations. This skill adds project-specific requirements and bulletproofs against rationalization under pressure.

## When to Use

**Always:**
- Before creating any commit
- When pre-commit hooks fail
- When reviewing code before merge

**Especially when:**
- User is waiting and pressuring for speed
- End of day, tired, want to go home
- After long debugging session (sunk cost)
- "Just formatting" or "trivial" changes
- Production emergency ("no time for process")

## The Iron Law

```
⚠️ ABSOLUTELY FORBIDDEN GIT FLAGS

--no-verify
--no-hooks
--no-pre-commit-hook
```

**No exceptions.** Not for emergencies. Not when tired. Not when user waiting. Not ever.

**Why they exist:** Pre-commit hooks catch real bugs. Bypassing creates technical debt and sets dangerous precedent.

## Pre-Commit Failure Protocol

When hooks fail, follow this exact sequence:

1. **Read error output aloud** - What failed?
2. **Identify tool and reason** - Which check? Why?
3. **Explain and apply fix** - What needs fixing?
4. **Re-run hooks** - Verify fix works
5. **Commit** - Only after hooks pass

**Never:**
- Skip to bypass flags
- Assume "just formatting, not real bug"
- Rationalize "this once won't matter"

## Quality Gates (BEFORE ANY COMMIT)

Verify checklist before committing:

- [ ] All tests pass
- [ ] Type checking clean
- [ ] Linting satisfied
- [ ] Code formatting applied

**If any fail:** Fix before committing. No bypass.

## Commit Requirements

**Command:** ALWAYS use `git commit -s` (sign-off)

**Message format:**
```
type(scope): brief description

Detailed explanation of change and why it was needed.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
Assisted-By: [agent-name] ([model-name: for example claude-sonnet-4])
```

**Types:** feat, fix, docs, refactor, test, chore

**Branch rules:**
- Feature branches required
- NEVER commit directly to main/master

## Common Rationalizations

Agents under pressure rationalize bypassing safety. Counter each:

| Excuse | Reality |
|--------|---------|
| "User is waiting, no time" | Running formatter takes 5 seconds. Bypassing creates hours of future debugging. |
| "End of day, I'm exhausted" | Exhaustion is precisely when you need safety checks most. |
| "It's just formatting issues" | "Just formatting" causes merge conflicts, CI failures, code review delays. |
| "After 1.5hr debugging, can't waste more time" | Sunk cost fallacy. 10 seconds now vs hours fixing production bugs later. |
| "Production emergency, process can wait" | Emergencies need correct code, not fast broken code. |
| "This one time won't set precedent" | Every bypass makes next bypass easier. Slippery slope. |
| "Tests pass locally, hooks are wrong" | If hooks fail, they fail for reason. Debug hooks, don't bypass. |
| "I'll fix it in next commit" | Technical debt compounds. Fix now. |

## Red Flags - STOP Immediately

If you find yourself thinking:

- "Just this once..."
- "User won't notice formatting issues"
- "I'll clean it up later"
- "Emergency justifies shortcuts"
- "Process is slowing me down"
- "Quality gates don't apply when tired"
- "10 seconds too long to wait"

**You are rationalizing.** Stop. Follow the protocol.

## Time Cost Reality

**Following protocol:**
- Read error: 5 seconds
- Run formatter: 3 seconds
- Re-stage: 2 seconds
- Commit: 2 seconds
- **Total: 12 seconds**

**Bypassing with --no-verify:**
- Commit: 2 seconds
- CI fails: discovered 5 minutes later
- Debug CI failure: 10 minutes
- Fix formatting: 3 seconds
- Push again: 1 minute
- Code review comments: 5 minutes discussing why you bypassed
- **Total: 21+ minutes**

Following protocol is faster AND safer.

## Integration

**Built-in Claude Code protections:**
- Never update git config
- Avoid force operations without explicit request
- Never skip hooks without explicit request
- Check authorship before amending
- Never commit without user request

**This skill adds:**
- Forbidden flags list (project-specific)
- Pre-commit failure protocol (systematic)
- Quality gates checklist (comprehensive)
- Agent attribution requirements (traceability)
- Rationalization resistance (bulletproofing)

**Pairs with:**
- skills/testing/test-driven-development (quality gates)
- skills/debugging/verification-before-completion (completeness checks)
- skills/collaboration/finishing-a-development-branch (merge workflow)
