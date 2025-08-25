# Claude Code Quality Gate Hooks

## Overview

This system implements file-level quality gate validation through Claude Code hooks, providing immediate feedback during code editing rather than waiting for commit-time validation.

## How It Works

**PreToolUse Hooks**: Before Claude Code executes `Edit`, `Write`, or `MultiEdit` tools, the validation script:

1. **Detects file type** based on extension (.ts, .js, .rs, .go, etc.)
2. **Discovers project commands** from `.claude/quality-commands.json` or inferred from project files
3. **Creates temporary file** with proposed content
4. **Runs quality gates** (typecheck, lint, format) on the temporary content
5. **Allows or blocks** the file operation based on validation results

**Benefits over Git pre-commit hooks:**
- ✅ **Immediate feedback** - catch issues before files are written
- ✅ **Prevents broken states** - never writes invalid code to disk  
- ✅ **Faster iteration** - no need to attempt commit to discover issues
- ✅ **Atomic validation** - each edit validated independently

## Installation & Setup

### 1. Enable Hooks (Already Done)

```bash
~/.claude/hooks/manage-hooks.sh enable
```

The hooks are configured in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "/home/jsnitsel/.claude/hooks/validate-edit.sh"
          }
        ]
      }
    ]
  }
}
```

### 2. Configure Project Quality Commands

For each project, create `.claude/quality-commands.json`:

```json
{
  "_comment": "Quality gate commands for this project",
  
  "typescript": [
    "npm run typecheck",
    "npm run lint"
  ],
  
  "rust": [
    "cargo check",
    "cargo clippy --all-targets -- -D warnings"
  ],
  
  "go": [
    "go vet ./...",
    "go fmt -l ."
  ],
  
  "_timeout_seconds": 30
}
```

### 3. Set Up New Projects

```bash
# Automatically set up a project
~/.claude/hooks/manage-hooks.sh setup /path/to/project

# Extract commands from existing agent PROJECT_SPECIFIC sections
~/.claude/hooks/extract-project-commands.sh /path/to/project
```

## Usage

### Management Commands

```bash
# Check status
~/.claude/hooks/manage-hooks.sh status

# Enable/disable hooks
~/.claude/hooks/manage-hooks.sh enable
~/.claude/hooks/manage-hooks.sh disable

# Enable debug logging
~/.claude/hooks/manage-hooks.sh debug

# Test validation on a file
~/.claude/hooks/manage-hooks.sh test /path/to/file.ts
```

### Debugging

Enable debug logging to see detailed hook execution:

```bash
export CLAUDE_HOOK_DEBUG=1
# Check debug output
tail -f /tmp/claude-hook-debug.log
```

## Project Configuration

### Quality Commands File Format

Location: `<project>/.claude/quality-commands.json`

```json
{
  "_comment": "Project-specific quality gate commands",
  
  "typescript": [
    "npx tsc --noEmit",
    "npx eslint --max-warnings 0"
  ],
  
  "javascript": [
    "npx eslint .",
    "npm test -- --passWithNoTests"
  ],
  
  "rust": [
    "cargo check --all-targets",
    "cargo clippy --all-targets --all-features -- -D warnings",
    "cargo fmt --check"
  ],
  
  "python": [
    "python -m py_compile",
    "flake8",
    "black --check"
  ],
  
  "go": [
    "go vet ./...",
    "go fmt -l .",
    "golangci-lint run"
  ],
  
  "_timeout_seconds": 30
}
```

### Command Discovery Priority

1. **Project config**: `.claude/quality-commands.json`
2. **Agent extraction**: Commands from `PROJECT_SPECIFIC_BEGIN/END` sections
3. **Inferred commands**: Based on project files (package.json, Cargo.toml, etc.)
4. **Fallback**: Language-specific defaults

### Supported File Types

- **TypeScript**: `.ts`, `.tsx` 
- **JavaScript**: `.js`, `.jsx`
- **Rust**: `.rs`
- **Go**: `.go`
- **Python**: `.py`
- **Java**: `.java`
- **C/C++**: `.c`, `.cpp`, `.h`, `.hpp`

## Integration with Workflow

### Sprint-to-Atomic-Task Integration

File-level validation enforces the atomic task discipline:

1. **Story breakdown** → atomic tasks in TodoWrite
2. **Task delegation** → specialized agents 
3. **Agent implementation** → immediate quality gate feedback
4. **Quality gates pass** → commit creation
5. **Code review** → series validation

### Agent Coordination

Quality gates integrate with agent workflow:

- **security-engineer**: Must validate security-related changes
- **test-specialist**: Tests must pass before commit
- **code-reviewer**: Final architectural review after atomic commits
- **performance-engineer**: Performance implications assessed

## Troubleshooting

### Common Issues

**Hook not running:**
```bash
# Check if hooks are enabled
~/.claude/hooks/manage-hooks.sh status

# Restart Claude Code after settings changes
```

**Commands not found:**
```bash
# Check project configuration
cat <project>/.claude/quality-commands.json

# Test command discovery
CLAUDE_PROJECT_DIR=/path/to/project ~/.claude/hooks/manage-hooks.sh test /path/to/file.ts
```

**Validation always fails:**
```bash
# Enable debug logging
export CLAUDE_HOOK_DEBUG=1

# Check what commands are running
tail -f /tmp/claude-hook-debug.log

# Verify commands work manually
cd /path/to/project && npm run typecheck
```

**Hook hangs or times out:**
```bash
# Adjust timeout in quality-commands.json
{
  "_timeout_seconds": 60
}

# Or set environment variable
export CLAUDE_HOOK_TIMEOUT=60
```

### Emergency Disable

If hooks are preventing editing:

```bash
# Disable hooks immediately
~/.claude/hooks/manage-hooks.sh disable

# Or remove from settings.json
jq 'del(.hooks.PreToolUse[] | select(.matcher == "Edit|Write|MultiEdit"))' ~/.claude/settings.json
```

### Debug Workflow

1. **Enable debug**: `export CLAUDE_HOOK_DEBUG=1`
2. **Test file**: `~/.claude/hooks/manage-hooks.sh test /path/to/file`
3. **Check logs**: `tail /tmp/claude-hook-debug.log`
4. **Verify commands**: Run quality gate commands manually
5. **Fix config**: Update `.claude/quality-commands.json`

## File Structure

```
~/.claude/hooks/
├── validate-edit.sh           # Main hook script
├── hook-utils.sh              # Helper functions
├── manage-hooks.sh            # Management commands
├── extract-project-commands.sh # Migration helper
├── quality-commands-template.json # Template config
└── README.md                  # This documentation
```

## Integration Examples

### New Project Setup

```bash
# 1. Set up project structure
mkdir my-project && cd my-project
npm init -y

# 2. Configure quality commands
~/.claude/hooks/manage-hooks.sh setup .

# 3. Edit quality-commands.json for your project
# 4. Test validation
~/.claude/hooks/manage-hooks.sh test src/index.ts
```

### Existing Project Migration

```bash
# 1. Extract from agent configurations
~/.claude/hooks/extract-project-commands.sh .

# 2. Review and customize generated config
vim .claude/quality-commands.json

# 3. Test with existing files
~/.claude/hooks/manage-hooks.sh test src/main.rs
```

This system transforms quality gates from post-implementation checks to proactive validation, ensuring code quality is maintained at the individual edit level rather than waiting for commit time.