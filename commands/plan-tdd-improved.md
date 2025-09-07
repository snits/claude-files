# Improved /plan-tdd Command

## Argument Processing

```bash
if [ -z "$1" ]; then
    echo "Error: /plan-tdd requires a specification file or description"
    echo "Usage: /plan-tdd <specification-file-or-description>"
    exit 1
fi

SPEC_INPUT="$1"
```

## File Archiving Setup

```bash
# Archive existing files with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_DIR="docs/00-project/archive_${TIMESTAMP}"

if [ -f "docs/00-project/plan.md" ] || [ -f "docs/00-project/tdd-prompts.md" ] || [ -f "docs/00-project/TODO.md" ]; then
    mkdir -p "$ARCHIVE_DIR"
    echo "Archiving existing project files to $ARCHIVE_DIR"
    [ -f "docs/00-project/plan.md" ] && cp "docs/00-project/plan.md" "$ARCHIVE_DIR/"
    [ -f "docs/00-project/tdd-prompts.md" ] && cp "docs/00-project/tdd-prompts.md" "$ARCHIVE_DIR/"
    [ -f "docs/00-project/TODO.md" ] && cp "docs/00-project/TODO.md" "$ARCHIVE_DIR/"
fi
```

## Agent Delegation

```bash
# Create context for meticulous-project-planner
echo "Creating comprehensive TDD implementation plan from specification: $SPEC_INPUT"

# Task meticulous-project-planner with zen planner tool
Task meticulous-project-planner with "Use zen planner tool to create detailed, step-by-step TDD implementation plan.

Specification: $SPEC_INPUT

Requirements:
- Break into small, iterative chunks that build on each other
- Each chunk should be test-driven with clear acceptance criteria  
- Include recursive breakdown - go multiple rounds to get right-sized steps
- Each code implementation step should be preceded by a step to develop tests for the code implementation
- Generate specific TDD prompts for each test and implementation step
- Include explicit checkpoint steps after each implementation step for: commit, code-reviewer gates, Jerry approval

Output files:
- docs/00-project/plan.md: High-level plan and chunk breakdown
- docs/00-project/tdd-prompts.md: Specific implementation prompts for each step
- docs/00-project/TODO.md: Project-level task tracking list

After plan creation, delegate to plan-validator for review and address any issues raised."

echo "Plan creation initiated. Files will be generated in docs/00-project/ after completion."
```
