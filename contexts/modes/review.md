# REVIEW MODE Detailed Requirements

## Modal Entry Protocol
**ENTRY CRITERIA**:
- [ ] **Implementation Complete**: All planned changes implemented per approved plan
- [ ] **MODE DECLARATION**: "ENTERING REVIEW MODE: [validation scope and criteria]"

## Mandatory Quality Gates (BEFORE ANY COMMIT)

**🚨 DEVELOPMENT QUALITY GATES** - ALL must pass:
- [ ] **All tests pass**: `[run project test command]` - NO EXCEPTIONS
- [ ] **Type checking clean**: `[run project typecheck command]` - Must show zero errors
- [ ] **Linting satisfied**: `[run project lint command]` - Must pass without warnings
- [ ] **Code formatting applied**: `[run project format command]` - Consistent style enforced

**EVIDENCE REQUIREMENT**: Include command output in your response showing successful execution.

## MCP Validation Tools

**Comprehensive Quality Analysis**:
- **`mcp__zen__codereview`**: Systematic quality, security, performance, architecture analysis with expert validation
- **`mcp__zen__precommit`**: Git change impact assessment and completeness verification
- **`mcp__metis__verify_mathematical_solution`**: Mathematical correctness validation (if applicable)

**Usage Strategy**:
- Use `mcp__zen__codereview` for all significant implementations
- Use `mcp__zen__precommit` for multi-file or complex changes
- Always enable expert validation (`use_assistant_model: true`) for critical changes

## Git Safety Protocols (NON-NEGOTIABLE)

**⚠️ ABSOLUTELY FORBIDDEN GIT FLAGS**: `--no-verify`, `--no-hooks`, `--no-pre-commit-hook`

**MANDATORY PRE-COMMIT FAILURE PROTOCOL** (When hooks fail):
1. **READ COMPLETE ERROR OUTPUT ALOUD** (explain what you're seeing)
2. **IDENTIFY WHICH TOOL FAILED** (ruff, mypy, tests, etc.) and why
3. **EXPLAIN THE FIX** you will apply and why it addresses root cause
4. **APPLY THE FIX** and re-run hooks
5. **🚨 NEVER COMMIT WITH FAILING HOOKS. NEVER USE --no-verify.**

**IF YOU CANNOT FIX HOOK FAILURES**: Ask user for help rather than bypass them

## Commit Protocol

**CHECKPOINT C: COMMIT READY** (MANDATORY before any commit):
- [ ] All quality gates passed and documented
- [ ] Atomic scope verified (single logical change)
- [ ] Commit message drafted with clear scope boundaries
- [ ] Security-engineer approval obtained (if security-relevant changes)
- [ ] TodoWrite task marked complete

**COMMIT REQUIREMENTS**:
- **USE `git commit -s` ALWAYS** (never MCP git tools)
- **Agent Attribution**: `Assisted-By: [agent-name] (claude-sonnet-4 / SHORT_HASH)`
- **Feature Branch Only**: NEVER commit directly to main
- **Atomic Discipline**: Single logical change per commit

## Validation Strategy

**Testing Validation**:
- Verify all tests pass on first run
- Check test coverage for new functionality
- Validate test scenarios cover edge cases appropriately

**Code Quality Validation**:
- Ensure adherence to project conventions and patterns
- Verify proper error handling and edge case management
- Check for security vulnerabilities or performance issues

## Failure Handling & Recovery

**Quality Gate Failures**:
- Fix issues and re-run gates (never bypass)
- Document root cause and resolution approach
- Re-run complete validation cycle after fixes

**Scope Creep Detection**:
- If atomic scope violated → Return to ANALYSIS MODE for scope redefinition
- If additional issues discovered → Create new user story rather than expanding current scope

## Exit Criteria & Post-Commit Protocol

**REVIEW MODE EXIT REQUIREMENTS**:
- [ ] All verification steps pass successfully
- [ ] Atomic commit created with proper attribution
- [ ] Clean working directory (all changes committed)

**POST-COMMIT PROTOCOL**:
- [ ] Request code-reviewer review of complete commit series  
- [ ] Repository in clean state for next development cycle
- [ ] Complete feature validation if this was final commit in series