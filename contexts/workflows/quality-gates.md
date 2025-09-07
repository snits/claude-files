# Quality Gates & Git Safety Protocols

## MANDATORY QUALITY GATES (Execute Before Any Commit)
**CRITICAL**: These commands MUST be run and pass before ANY commit operation.

### Required Execution Sequence:
1. **Type Checking**: `[project-specific-typecheck-command]`
   - MUST show "Success: no issues found" or equivalent
   - If errors found: Fix all type issues before proceeding

2. **Linting**: `[project-specific-lint-command]`
   - MUST show no errors or warnings
   - Auto-fix available: `[project-specific-lint-fix-command]`

3. **Testing**: `[project-specific-test-command]`
   - MUST show all tests passing
   - If failures: Fix failing tests before proceeding

4. **Formatting**: `[project-specific-format-command]`
   - Apply code formatting standards

**EVIDENCE REQUIREMENT**: Include command output in your response showing successful execution.

## Git Safety Protocols (NON-NEGOTIABLE)

**⚠️ ABSOLUTELY FORBIDDEN GIT FLAGS**: `--no-verify`, `--no-hooks`, `--no-pre-commit-hook`
**VIOLATION = IMMEDIATE FAILURE**

### MANDATORY PRE-COMMIT FAILURE PROTOCOL
**When pre-commit hooks fail, MUST follow this exact sequence:**

1. **READ COMPLETE ERROR OUTPUT ALOUD** (explain what you're seeing)
2. **IDENTIFY WHICH TOOL FAILED** (ruff, mypy, tests, etc.) and why  
3. **EXPLAIN THE FIX** you will apply and why it addresses root cause
4. **APPLY THE FIX** and re-run hooks
5. **🚨 NEVER COMMIT WITH FAILING HOOKS. NEVER USE --no-verify.**

**IF YOU CANNOT FIX HOOK FAILURES**: Ask user for help rather than bypass them

### Commit Requirements
- **USE `git commit -s` ALWAYS** (never MCP git tools)
- **Agent Attribution**: `Assisted-By: [agent-name] (claude-sonnet-4 / SHORT_HASH)`
- **Feature Branch Only**: NEVER commit directly to main
- **Atomic Discipline**: Single logical change per commit

### Agent Hash Mapping System
**MANDATORY agent attribution**: When ANY agent assists with work resulting in commit:
- **Agent Hash Mapping**: Use `~/devel/tools/get-agent-hash <agent-name>` to get hash for SHORT_HASH
- **If `get-agent-hash` fails**: Stop and ask user for help
- **No exceptions**: Agents MUST NOT be omitted from attribution

### Testing Standards Integration
**NO EXCEPTIONS POLICY**: ALL projects MUST have unit, integration, AND end-to-end tests
- **TDD workflow mandatory**: Write failing test → implement → commit → refactor
- **NEVER test mocked behavior**: Test real logic, not mock implementations
- **NEVER mock in end-to-end tests**: Always use real data and real APIs
- **Test output MUST be pristine**: Capture and test expected errors/logs

### Quality Assurance Triggers
- **test-specialist**: After new features, bug fixes, untested code discovery
- **qa-engineer**: Before feature completion, after integration issues
- **code-reviewer**: After each atomic commit  
- **security-engineer**: For user input or sensitive data handling