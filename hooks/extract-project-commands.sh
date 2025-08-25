#!/bin/bash
# ABOUTME: Extract quality gate commands from PROJECT_SPECIFIC sections in agent files
# Helps migrate existing project configurations to the new hook system

set -euo pipefail

usage() {
    cat << EOF
Usage: $0 <project_directory> [output_file]

Extract quality gate commands from agent PROJECT_SPECIFIC sections and create
a quality-commands.json file for the hook validation system.

Arguments:
  project_directory  Path to project with .claude/agents directory
  output_file       Optional output file (default: project/.claude/quality-commands.json)

Examples:
  $0 /home/jsnitsel/proj/my-project
  $0 /home/jsnitsel/proj/my-project custom-commands.json
EOF
}

# Extract commands from a single agent file
extract_from_agent() {
    local agent_file="$1"
    local temp_output="$2"
    
    awk '
        /^<!-- PROJECT_SPECIFIC_BEGIN:/ { 
            in_section = 1
            next 
        }
        /^<!-- PROJECT_SPECIFIC_END:/ { 
            in_section = 0
            next 
        }
        in_section {
            # Look for command patterns
            if (/\[.*-typecheck.*\]/ || /typecheck.*command/) {
                # Extract command from brackets or description
                gsub(/.*\[/, "")
                gsub(/\].*/, "")
                if (length($0) > 0 && !seen["typecheck"]) {
                    print "typecheck: " $0
                    seen["typecheck"] = 1
                }
            }
            else if (/\[.*-lint.*\]/ || /lint.*command/) {
                gsub(/.*\[/, "")
                gsub(/\].*/, "")
                if (length($0) > 0 && !seen["lint"]) {
                    print "lint: " $0
                    seen["lint"] = 1
                }
            }
            else if (/\[.*-test.*\]/ || /test.*command/) {
                gsub(/.*\[/, "")
                gsub(/\].*/, "")
                if (length($0) > 0 && !seen["test"]) {
                    print "test: " $0
                    seen["test"] = 1
                }
            }
            else if (/\[.*-format.*\]/ || /format.*command/) {
                gsub(/.*\[/, "")
                gsub(/\].*/, "")
                if (length($0) > 0 && !seen["format"]) {
                    print "format: " $0
                    seen["format"] = 1
                }
            }
        }
    ' "$agent_file" >> "$temp_output"
}

# Detect project type from files
detect_project_type() {
    local project_dir="$1"
    
    if [[ -f "$project_dir/package.json" ]] && [[ -f "$project_dir/tsconfig.json" ]]; then
        echo "typescript"
    elif [[ -f "$project_dir/package.json" ]]; then
        echo "javascript"
    elif [[ -f "$project_dir/Cargo.toml" ]]; then
        echo "rust"
    elif [[ -f "$project_dir/go.mod" ]]; then
        echo "go"
    elif [[ -f "$project_dir/pyproject.toml" ]] || [[ -f "$project_dir/requirements.txt" ]]; then
        echo "python"
    elif [[ -f "$project_dir/pom.xml" ]] || [[ -f "$project_dir/build.gradle" ]]; then
        echo "java"
    else
        echo "unknown"
    fi
}

# Generate quality-commands.json
generate_commands_json() {
    local project_dir="$1"
    local commands_file="$2"
    local temp_commands="$3"
    
    local project_type
    project_type=$(detect_project_type "$project_dir")
    
    echo "🔍 Detected project type: $project_type"
    
    # Start building JSON
    cat > "$commands_file" << EOF
{
  "_comment": "Generated from PROJECT_SPECIFIC sections in agent files",
  "_project_type": "$project_type",
  
EOF

    # Add commands for detected project type
    echo "  \"$project_type\": [" >> "$commands_file"
    
    local first_command=true
    while IFS=': ' read -r cmd_type command; do
        if [[ -n "$command" ]]; then
            if [[ "$first_command" == "true" ]]; then
                first_command=false
            else
                echo "," >> "$commands_file"
            fi
            echo -n "    \"$command\"" >> "$commands_file"
        fi
    done < "$temp_commands"
    
    echo "" >> "$commands_file"
    echo "  ]," >> "$commands_file"
    
    # Add common fallbacks
    cat >> "$commands_file" << 'EOF'
  
  "_fallbacks": {
    "typescript": ["npx tsc --noEmit", "npx eslint ."],
    "javascript": ["npx eslint .", "npm test -- --passWithNoTests"],
    "rust": ["cargo check", "cargo clippy"],
    "python": ["python -m py_compile", "flake8"],
    "go": ["go vet", "go fmt -l ."]
  },
  
  "_timeout_seconds": 30
}
EOF
}

# Main function
main() {
    local project_dir="${1:-}"
    local output_file="${2:-}"
    
    if [[ -z "$project_dir" ]]; then
        echo "❌ Error: Project directory required"
        usage
        exit 1
    fi
    
    if [[ ! -d "$project_dir" ]]; then
        echo "❌ Error: Project directory not found: $project_dir"
        exit 1
    fi
    
    local agents_dir="$project_dir/.claude/agents"
    if [[ ! -d "$agents_dir" ]]; then
        echo "❌ Error: No .claude/agents directory found in: $project_dir"
        echo "   This project may not have agent configurations yet."
        exit 1
    fi
    
    # Set default output file
    if [[ -z "$output_file" ]]; then
        output_file="$project_dir/.claude/quality-commands.json"
    fi
    
    echo "🔍 Extracting commands from agent files in: $agents_dir"
    
    # Create temporary file for commands
    local temp_commands
    temp_commands=$(mktemp)
    
    # Extract commands from all agent files
    local found_agents=0
    find "$agents_dir" -name "*.md" -print0 | while IFS= read -r -d '' agent_file; do
        if grep -q "PROJECT_SPECIFIC_BEGIN" "$agent_file"; then
            echo "   📄 Processing: $(basename "$agent_file")"
            extract_from_agent "$agent_file" "$temp_commands"
            ((found_agents++))
        fi
    done
    
    if [[ ! -s "$temp_commands" ]]; then
        echo "⚠️  No quality gate commands found in PROJECT_SPECIFIC sections"
        echo "   You may need to set up commands manually."
        rm -f "$temp_commands"
        exit 1
    fi
    
    # Generate the JSON file
    echo "📝 Generating quality commands file: $output_file"
    generate_commands_json "$project_dir" "$output_file" "$temp_commands"
    
    # Cleanup
    rm -f "$temp_commands"
    
    echo "✅ Created: $output_file"
    echo ""
    echo "📋 Extracted commands:"
    jq -r ".[\"$(detect_project_type "$project_dir")\"][]?" "$output_file" 2>/dev/null | sed 's/^/   /'
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Review and edit: $output_file"
    echo "   2. Test with: ~/.claude/hooks/manage-hooks.sh test $project_dir/some-file"
    echo "   3. Enable hooks: ~/.claude/hooks/manage-hooks.sh enable"
}

# Handle help
if [[ "${1:-}" =~ ^(-h|--help|help)$ ]]; then
    usage
    exit 0
fi

main "$@"