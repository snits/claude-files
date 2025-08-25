#!/bin/bash
# ABOUTME: Helper functions for Claude Code hooks validation system
# Provides file detection, command discovery, and validation execution

# Debug logging function
debug_log() {
    if [[ "${CLAUDE_HOOK_DEBUG:-}" == "1" ]]; then
        echo "DEBUG: $*" >> /tmp/claude-hook-debug.log
    fi
}

# Check if file should be validated based on extension and path
should_validate_file() {
    local file_path="$1"
    local filename=$(basename "$file_path")
    local extension="${filename##*.}"
    
    # Skip hidden files and specific directories
    if [[ "$filename" == .* ]] || [[ "$file_path" == *"/node_modules/"* ]] || [[ "$file_path" == *"/target/"* ]] || [[ "$file_path" == *"/.git/"* ]]; then
        return 1
    fi
    
    # Check for source code extensions
    case "$extension" in
        ts|tsx|js|jsx|py|rs|go|java|c|cpp|h|hpp)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Get file type for validation command selection
get_file_type() {
    local file_path="$1"
    local extension="${file_path##*.}"
    
    case "$extension" in
        ts|tsx)
            echo "typescript"
            ;;
        js|jsx)
            echo "javascript"
            ;;
        py)
            echo "python"
            ;;
        rs)
            echo "rust"
            ;;
        go)
            echo "go"
            ;;
        java)
            echo "java"
            ;;
        c|cpp|h|hpp)
            echo "cpp"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Create temporary file with proposed content
create_temp_file() {
    local original_path="$1"
    local content="$2"
    local temp_file
    
    # Create temp file with same extension
    local extension="${original_path##*.}"
    temp_file=$(mktemp --suffix=".$extension")
    
    # Write content to temp file
    echo "$content" > "$temp_file"
    
    echo "$temp_file"
}

# Clean up temporary file
cleanup_temp_file() {
    local temp_file="$1"
    if [[ -f "$temp_file" ]]; then
        rm -f "$temp_file"
    fi
}

# Discover project-specific quality gate commands
discover_project_commands() {
    local project_dir="$1"
    local file_type="$2"
    local commands_file="$project_dir/.claude/quality-commands.json"
    
    debug_log "Looking for commands in: $commands_file"
    
    # Check for project-specific commands file
    if [[ -f "$commands_file" ]]; then
        debug_log "Found quality commands file"
        # Handle both string and array formats
        jq -r "if (.$file_type | type) == \"array\" then .$file_type[] else .$file_type end // empty" "$commands_file" 2>/dev/null || echo ""
        return
    fi
    
    # Extract from agent files
    local agent_commands
    agent_commands=$(extract_agent_commands "$project_dir" "$file_type")
    if [[ -n "$agent_commands" ]]; then
        echo "$agent_commands"
        return
    fi
    
    # Fallback to inferred commands
    infer_project_commands "$project_dir" "$file_type"
}

# Extract commands from agent PROJECT_SPECIFIC sections
extract_agent_commands() {
    local project_dir="$1"
    local file_type="$2"
    local agents_dir="$project_dir/.claude/agents"
    
    if [[ ! -d "$agents_dir" ]]; then
        return
    fi
    
    # Look for type checking and linting commands in agent files
    find "$agents_dir" -name "*.md" -exec grep -l "PROJECT_SPECIFIC_BEGIN" {} \; 2>/dev/null | \
    while read -r agent_file; do
        awk '/^<!-- PROJECT_SPECIFIC_BEGIN:/ { in_section=1; next } 
             /^<!-- PROJECT_SPECIFIC_END:/ { in_section=0; next }
             in_section && /typecheck|lint/ { print }' "$agent_file" | \
        grep -E "(typecheck|lint)" | head -1
    done | head -1
}

# Infer commands from common project files
infer_project_commands() {
    local project_dir="$1"
    local file_type="$2"
    
    case "$file_type" in
        typescript|javascript)
            if [[ -f "$project_dir/package.json" ]]; then
                # Check for common npm script names
                if jq -e '.scripts.typecheck' "$project_dir/package.json" >/dev/null 2>&1; then
                    echo "npm run typecheck"
                elif jq -e '.scripts.lint' "$project_dir/package.json" >/dev/null 2>&1; then
                    echo "npm run lint"
                elif [[ -f "$project_dir/tsconfig.json" ]]; then
                    echo "npx tsc --noEmit"
                fi
            fi
            ;;
        rust)
            if [[ -f "$project_dir/Cargo.toml" ]]; then
                echo "cargo check"
            fi
            ;;
        python)
            if [[ -f "$project_dir/pyproject.toml" ]] || [[ -f "$project_dir/requirements.txt" ]]; then
                echo "python -m py_compile"
            fi
            ;;
        go)
            if [[ -f "$project_dir/go.mod" ]]; then
                echo "go vet"
            fi
            ;;
    esac
}

# Execute validation command with timeout
execute_validation_command() {
    local command="$1"
    local project_dir="$2"
    local timeout="${TIMEOUT_SECONDS:-30}"
    
    debug_log "Executing: $command (timeout: ${timeout}s)"
    
    # Change to project directory
    cd "$project_dir"
    
    # Execute with timeout
    if timeout "$timeout" bash -c "$command" >/dev/null 2>&1; then
        debug_log "Command succeeded: $command"
        return 0
    else
        local exit_code=$?
        debug_log "Command failed with exit code $exit_code: $command"
        return $exit_code
    fi
}

# Main validation function
validate_file_content() {
    local temp_file="$1"
    local original_path="$2"
    local project_dir="$3"
    
    local file_type
    file_type=$(get_file_type "$original_path")
    
    if [[ "$file_type" == "unknown" ]]; then
        debug_log "Unknown file type, skipping validation"
        return 0
    fi
    
    local commands
    commands=$(discover_project_commands "$project_dir" "$file_type")
    
    if [[ -z "$commands" ]]; then
        debug_log "No validation commands found for $file_type"
        return 0
    fi
    
    debug_log "Found validation commands: $commands"
    
    # Copy temp file to original location temporarily for validation
    local backup_file=""
    if [[ -f "$original_path" ]]; then
        backup_file=$(mktemp)
        cp "$original_path" "$backup_file"
    fi
    
    # Copy temp content to original location
    cp "$temp_file" "$original_path"
    
    # Execute validation commands
    local validation_result=0
    while IFS= read -r command; do
        if [[ -n "$command" ]]; then
            if ! execute_validation_command "$command" "$project_dir"; then
                validation_result=1
                break
            fi
        fi
    done <<< "$commands"
    
    # Restore original file
    if [[ -n "$backup_file" && -f "$backup_file" ]]; then
        mv "$backup_file" "$original_path"
    elif [[ ! -f "$backup_file" ]]; then
        rm -f "$original_path"
    fi
    
    return $validation_result
}