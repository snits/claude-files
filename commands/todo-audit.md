Audit and validate all tracked TODOs and stubs for quality gate compliance.

**Arguments: $ARGUMENTS**
- Optional scope: "todos", "stubs", or "all" (default: all)
- Optional flags: "--strict", "--report", "--max-count N"

**Audit Process:**

1. **Scan codebase for TODO/STUB comments:**
   ```bash
   # Find all TODO/STUB comments with UUIDs
   grep -r "TODO-[a-f0-9]\{8\}" . --include="*.rs" --include="*.ts" --include="*.py" --include="*.js"
   grep -r "STUB-[a-f0-9]\{8\}" . --include="*.rs" --include="*.ts" --include="*.py" --include="*.js"
   ```

2. **Validate documentation sync:**
   - Check that all code TODOs exist in docs/outstanding-work.md
   - Check that all doc entries have corresponding code comments
   - Identify orphaned entries (docs without code or code without docs)

3. **Quality Gate Checks:**
   
   **TODO Count Validation:**
   - Count total outstanding TODOs
   - Compare against project threshold (configurable per project)
   - Fail if exceeds limit (default: warn at 10, fail at 25)
   
   **Stub Implementation Validation:**
   - Check for unimplemented stubs that block functionality
   - Validate that stub functions aren't called in production code paths
   - Ensure critical path stubs are prioritized
   
   **Aging Analysis:**
   - Calculate how long TODOs/stubs have been outstanding
   - Flag items older than threshold (default: 30 days)
   - Escalate critical items that remain unaddressed

4. **Generate reports:**
   
   **Summary Report:**
   ```
   📊 TODO/STUB AUDIT REPORT
   
   ✅ TODOs: 8 tracked, 2 high priority
   ⚠️  Stubs: 12 tracked, 3 blocking critical paths
   ❌ Orphaned: 2 code TODOs missing from docs
   
   🚨 QUALITY GATE: FAIL
   - Stub count (12) exceeds threshold (10)
   - 3 stubs on critical paths unassigned
   - 1 TODO older than 30 days
   ```
   
   **Detailed Report:**
   ```
   ## High Priority Issues
   - STUB-a1b2c3d4: Authentication middleware (BLOCKING: user login)
   - TODO-e5f6g7h8: Fix memory leak (AGE: 45 days)
   
   ## Assignment Needed
   - STUB-i9j0k1l2: Database optimizer (suggested: database-specialist)
   
   ## Documentation Sync Issues  
   - TODO-m3n4o5p6: Found in code but missing from docs
   ```

5. **Integration with CI/CD:**
   - Exit code 0: All checks pass
   - Exit code 1: Warnings (TODOs approaching limits)
   - Exit code 2: Failures (limits exceeded, blocking stubs)
   - Generate machine-readable output for CI systems

6. **Remediation suggestions:**
   - Suggest appropriate agents for unassigned items
   - Provide `/agent-deploy` commands for missing specialists
   - Offer `/todo-complete` workflows for ready items

**Usage examples:**
```bash
/todo-audit                    # Full audit with quality gates
/todo-audit stubs --strict     # Only audit stubs with strict thresholds  
/todo-audit --report          # Generate detailed report
/todo-audit --max-count 5     # Fail if more than 5 outstanding items
```

**Configuration (per project):**
Projects can configure thresholds in `.claude/todo-config.json`:
```json
{
  "todo_warn_threshold": 10,
  "todo_fail_threshold": 25,
  "stub_warn_threshold": 5,
  "stub_fail_threshold": 10,
  "aging_threshold_days": 30,
  "critical_stubs": ["auth", "security", "data"]
}
```

**Quality Gate Integration:**
- Pre-commit hooks can run lightweight audit
- CI/CD pipelines can enforce thresholds
- Release gates can block deployments with critical stubs
- Agent assignment can be enforced for high-priority items