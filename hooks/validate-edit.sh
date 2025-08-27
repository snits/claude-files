#!/bin/bash
# ABOUTME: Universal Claude Code hook for file-level quality gate validation
# Reads project-specific commands and validates file edits before they're written

set -euo pipefail

# Enable debug mode if CLAUDE_HOOK_DEBUG is set
if [[ "${CLAUDE_HOOK_DEBUG:-}" == "1" ]]; then
    set -x
    exec 2>> /tmp/claude-hook-debug.log
    echo "=== Hook execution started: $(date) ===" >> /tmp/claude-hook-debug.log
fi

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_CONFIG_DIR="$SCRIPT_DIR"
TIMEOUT_SECONDS="${CLAUDE_HOOK_TIMEOUT:-30}"

# Source helper functions
source "$HOOK_CONFIG_DIR/hook-utils.sh"

# Main validation function
main() {
    local hook_input
    local tool_name
    local file_path
    local file_content
    local project_dir
    
    # Read JSON input from stdin
    hook_input=$(cat)
    
    # Parse hook input
    tool_name=$(echo "$hook_input" | jq -r '.tool_name')
    file_path=$(echo "$hook_input" | jq -r '.tool_input.file_path // empty')
    file_content=$(echo "$hook_input" | jq -r '.tool_input.content // .tool_input.new_string // empty')
    project_dir="${CLAUDE_PROJECT_DIR:-$(pwd)}"
    
    # Debug logging
    debug_log "Hook triggered for tool: $tool_name"
    debug_log "File path: $file_path"
    debug_log "Project directory: $project_dir"
    
    # Skip if no file path (some tools don't edit files)
    if [[ -z "$file_path" || "$file_path" == "null" ]]; then
        debug_log "No file path found, allowing operation"
        exit 0
    fi
    
    # Skip if file doesn't need validation
    if ! should_validate_file "$file_path"; then
        debug_log "File doesn't need validation: $file_path"
        exit 0
    fi
    
    # Create temporary file with the proposed content
    local temp_file
    temp_file=$(create_temp_file "$file_path" "$file_content")
    
    # Run validation
    if validate_file_content "$temp_file" "$file_path" "$project_dir"; then
        debug_log "Validation passed for: $file_path"
        cleanup_temp_file "$temp_file"
        exit 0
    else
        debug_log "Validation failed for: $file_path"
        echo "File validation failed for: $file_path" >&2
        echo "Quality gate checks (lint, typecheck, tests) must pass before editing." >&2
        cleanup_temp_file "$temp_file"
        exit 2  # Block the operation
    fi
}

# Error handling
trap 'handle_error $? $LINENO' ERR

handle_error() {
    local exit_code=$1
    local line_number=$2
    
    debug_log "Error occurred at line $line_number with exit code $exit_code"
    
    # Always allow operation on script errors to avoid breaking editing
    echo "Hook validation error (line $line_number). Allowing operation to proceed." >&2
    exit 0
}

# Run main function
main "$@"