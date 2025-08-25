#!/bin/bash
# ABOUTME: Management script for Claude Code quality gate hooks
# Provides enable/disable, debugging, and project setup functionality

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETTINGS_FILE="/home/jsnitsel/.claude/settings.json"

usage() {
    cat << EOF
Usage: $0 <command> [options]

Commands:
  enable          Enable quality gate hooks
  disable         Disable quality gate hooks  
  debug           Enable debug logging for hooks
  nodebug         Disable debug logging
  test <file>     Test hook validation on a file
  setup <project> Set up quality commands for a project
  status          Show current hook status
  
Examples:
  $0 enable                                    # Enable hooks
  $0 debug                                     # Enable debug logging
  $0 test /path/to/file.ts                     # Test validation
  $0 setup /home/jsnitsel/proj/my-project      # Set up project commands
  $0 status                                    # Show status
EOF
}

# Check if hooks are enabled
hooks_enabled() {
    jq -e '.hooks.PreToolUse[]? | select(.matcher == "Edit|Write|MultiEdit")' "$SETTINGS_FILE" >/dev/null 2>&1
}

# Enable hooks
enable_hooks() {
    if hooks_enabled; then
        echo "✅ Quality gate hooks are already enabled"
        return 0
    fi
    
    echo "🔧 Enabling quality gate hooks..."
    
    # Create backup
    cp "$SETTINGS_FILE" "${SETTINGS_FILE}.backup"
    
    # Add hooks configuration if it doesn't exist
    if ! jq -e '.hooks' "$SETTINGS_FILE" >/dev/null 2>&1; then
        jq '. + {"hooks": {"PreToolUse": []}}' "$SETTINGS_FILE" > "${SETTINGS_FILE}.tmp" && mv "${SETTINGS_FILE}.tmp" "$SETTINGS_FILE"
    fi
    
    # Add the hook
    jq '.hooks.PreToolUse += [{
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [{
            "type": "command",
            "command": "/home/jsnitsel/.claude/hooks/validate-edit.sh"
        }]
    }]' "$SETTINGS_FILE" > "${SETTINGS_FILE}.tmp" && mv "${SETTINGS_FILE}.tmp" "$SETTINGS_FILE"
    
    echo "✅ Quality gate hooks enabled. Restart Claude Code for changes to take effect."
}

# Disable hooks
disable_hooks() {
    if ! hooks_enabled; then
        echo "ℹ️ Quality gate hooks are already disabled"
        return 0
    fi
    
    echo "🔧 Disabling quality gate hooks..."
    
    # Create backup
    cp "$SETTINGS_FILE" "${SETTINGS_FILE}.backup"
    
    # Remove the hook
    jq '.hooks.PreToolUse = (.hooks.PreToolUse // []) | map(select(.matcher != "Edit|Write|MultiEdit"))' "$SETTINGS_FILE" > "${SETTINGS_FILE}.tmp" && mv "${SETTINGS_FILE}.tmp" "$SETTINGS_FILE"
    
    echo "✅ Quality gate hooks disabled. Restart Claude Code for changes to take effect."
}

# Enable debug logging
enable_debug() {
    export CLAUDE_HOOK_DEBUG=1
    echo "🐛 Debug logging enabled. Check /tmp/claude-hook-debug.log for details."
    echo "   To make permanent, add CLAUDE_HOOK_DEBUG=1 to your shell profile."
}

# Disable debug logging
disable_debug() {
    unset CLAUDE_HOOK_DEBUG
    echo "🔇 Debug logging disabled."
    if [[ -f /tmp/claude-hook-debug.log ]]; then
        echo "   Cleaning up debug log..."
        rm -f /tmp/claude-hook-debug.log
    fi
}

# Test hook validation on a file
test_validation() {
    local file_path="$1"
    
    if [[ ! -f "$file_path" ]]; then
        echo "❌ File not found: $file_path"
        exit 1
    fi
    
    echo "🧪 Testing hook validation on: $file_path"
    
    # Create test JSON input
    local test_input
    test_input=$(jq -n --arg path "$file_path" --arg content "$(cat "$file_path")" '{
        "hook_event_name": "PreToolUse",
        "tool_name": "Edit",
        "tool_input": {
            "file_path": $path,
            "content": $content
        }
    }')
    
    # Set debug mode and run hook
    export CLAUDE_HOOK_DEBUG=1
    # Use provided project dir or infer from file path
    export CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(dirname "$file_path")}"
    
    echo "📁 Project directory: $CLAUDE_PROJECT_DIR"
    echo "🔍 Running validation..."
    
    if echo "$test_input" | "$SCRIPT_DIR/validate-edit.sh"; then
        echo "✅ Validation passed"
    else
        echo "❌ Validation failed"
    fi
    
    # Show debug log if it exists
    if [[ -f /tmp/claude-hook-debug.log ]]; then
        echo ""
        echo "📋 Debug output:"
        tail -20 /tmp/claude-hook-debug.log
    fi
}

# Set up quality commands for a project
setup_project() {
    local project_dir="$1"
    
    if [[ ! -d "$project_dir" ]]; then
        echo "❌ Project directory not found: $project_dir"
        exit 1
    fi
    
    local claude_dir="$project_dir/.claude"
    local commands_file="$claude_dir/quality-commands.json"
    
    # Create .claude directory if it doesn't exist
    if [[ ! -d "$claude_dir" ]]; then
        echo "📁 Creating .claude directory..."
        mkdir -p "$claude_dir"
    fi
    
    # Copy template if commands file doesn't exist
    if [[ ! -f "$commands_file" ]]; then
        echo "📋 Creating quality commands configuration..."
        cp "$SCRIPT_DIR/quality-commands-template.json" "$commands_file"
        echo "✅ Created: $commands_file"
        echo ""
        echo "📝 Next steps:"
        echo "   1. Edit $commands_file to match your project's commands"
        echo "   2. Test with: $0 test $project_dir/some-file.ts"
    else
        echo "ℹ️ Quality commands file already exists: $commands_file"
    fi
    
    # Detect project type and suggest commands
    echo ""
    echo "🔍 Detected project characteristics:"
    
    if [[ -f "$project_dir/package.json" ]]; then
        echo "   📦 Node.js project (package.json found)"
        echo "   💡 Suggested: npm run typecheck, npm run lint"
    fi
    
    if [[ -f "$project_dir/Cargo.toml" ]]; then
        echo "   🦀 Rust project (Cargo.toml found)"
        echo "   💡 Suggested: cargo check, cargo clippy"
    fi
    
    if [[ -f "$project_dir/tsconfig.json" ]]; then
        echo "   📘 TypeScript project (tsconfig.json found)"
        echo "   💡 Suggested: npx tsc --noEmit"
    fi
}

# Show current status
show_status() {
    echo "🔍 Claude Code Quality Gate Hooks Status"
    echo ""
    
    if hooks_enabled; then
        echo "✅ Hooks: ENABLED"
    else
        echo "❌ Hooks: DISABLED"
    fi
    
    if [[ "${CLAUDE_HOOK_DEBUG:-}" == "1" ]]; then
        echo "🐛 Debug logging: ENABLED"
    else
        echo "🔇 Debug logging: DISABLED"
    fi
    
    echo ""
    echo "📁 Hook files:"
    echo "   Script: $SCRIPT_DIR/validate-edit.sh"
    echo "   Utils:  $SCRIPT_DIR/hook-utils.sh"
    echo "   Config: $SETTINGS_FILE"
    
    if [[ -f /tmp/claude-hook-debug.log ]]; then
        echo "   Debug:  /tmp/claude-hook-debug.log ($(wc -l < /tmp/claude-hook-debug.log) lines)"
    fi
}

# Main command dispatch
case "${1:-}" in
    enable)
        enable_hooks
        ;;
    disable)
        disable_hooks
        ;;
    debug)
        enable_debug
        ;;
    nodebug)
        disable_debug
        ;;
    test)
        if [[ $# -lt 2 ]]; then
            echo "❌ Error: test command requires a file path"
            echo "Usage: $0 test <file_path>"
            exit 1
        fi
        test_validation "$2"
        ;;
    setup)
        if [[ $# -lt 2 ]]; then
            echo "❌ Error: setup command requires a project directory"
            echo "Usage: $0 setup <project_directory>"
            exit 1
        fi
        setup_project "$2"
        ;;
    status)
        show_status
        ;;
    -h|--help|help)
        usage
        ;;
    *)
        echo "❌ Error: Unknown command: ${1:-}"
        echo ""
        usage
        exit 1
        ;;
esac