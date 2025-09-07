# Improved /do-todo Command

## TODO.md Validation and Selection
```bash
# Check if TODO.md exists
if [ ! -f "docs/00-project/TODO.md" ]; then
    echo "Error: docs/00-project/TODO.md not found. Run /plan-tdd first."
    exit 1
fi

# Find first unchecked item in TODO.md
NEXT_TASK=$(grep -n "^- \[ \]" "docs/00-project/TODO.md" | head -n1)

if [ -z "$NEXT_TASK" ]; then
    echo "No unchecked tasks found in TODO.md. All tasks may be complete!"
    exit 0
fi

# Extract line number and task description
TASK_LINE_NUM=$(echo "$NEXT_TASK" | cut -d: -f1)
TASK_DESC=$(echo "$NEXT_TASK" | cut -d: -f2- | sed 's/^- \[ \] //')

echo "Selected task: $TASK_DESC"
```

## TodoWrite Integration and Branch Setup
```bash
# Add task to current session TodoWrite
TodoWrite add "$TASK_DESC"
TodoWrite set_status "$TASK_DESC" "in_progress"

# Create feature branch for this task
BRANCH_NAME=$(echo "$TASK_DESC" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-' | cut -c1-50)
git checkout -b "feature/$BRANCH_NAME"

echo "Created branch: feature/$BRANCH_NAME"
echo "Task added to TodoWrite and marked in_progress"
```

## Agent Delegation with Context
```bash
# Determine appropriate agent and provide context
echo "Delegating task to appropriate agent..."

# Create comprehensive task context
TASK_CONTEXT="Task from project TODO.md: $TASK_DESC

Context:
- This is task line $TASK_LINE_NUM from docs/00-project/TODO.md
- Working branch: feature/$BRANCH_NAME
- Check docs/00-project/plan.md and docs/00-project/tdd-prompts.md for detailed guidance
- Follow TDD workflow: write failing test, implement minimal code, refactor
- Complete Checkpoints A, B, C before committing
- Request code-reviewer approval after commit

Deliverables:
- Implemented functionality with passing tests
- Atomic commit with clear message
- All quality gates passed (tests, lint, typecheck, format)"

# Task appropriate agent (agent selection handled by Task tool based on context)
Task auto-select "$TASK_CONTEXT"
```

## Completion and State Update
```bash
# After agent completion, update TODO.md
echo "Updating TODO.md to mark task as complete..."

# Mark task as complete in TODO.md
sed -i "${TASK_LINE_NUM}s/^- \[ \]/- [x]/" "docs/00-project/TODO.md"

# Mark complete in TodoWrite
TodoWrite set_status "$TASK_DESC" "completed"

echo "Task completed and marked in both TODO.md and TodoWrite"
echo "Ready for next task execution"
```