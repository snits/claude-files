#!/bin/bash

# Script to update Strategic Journal Policy sections in agent files

NEW_POLICY_FILE="/Users/jsnitsel/.claude/new-journal-policy.txt"

# Function to update a single agent file
update_agent() {
    local agent_file="$1"
    local temp_file="${agent_file}.tmp"
    
    echo "Updating: $agent_file"
    
    # Use awk to replace the Strategic Journal Policy section
    awk '
    BEGIN { in_journal_section = 0; replacement_done = 0 }
    
    # Start of Strategic Journal Policy section
    /^## Strategic Journal Policy/ {
        if (!replacement_done) {
            # Print the new policy
            while ((getline line < "'$NEW_POLICY_FILE'") > 0) {
                print line
            }
            close("'$NEW_POLICY_FILE'")
            replacement_done = 1
        }
        in_journal_section = 1
        next
    }
    
    # End of section (next ## header or empty line followed by ##)
    /^## / && in_journal_section && replacement_done {
        in_journal_section = 0
        print
        next
    }
    
    # Skip lines within the old journal section
    in_journal_section { next }
    
    # Print all other lines
    { print }
    ' "$agent_file" > "$temp_file"
    
    # Replace original with updated version
    mv "$temp_file" "$agent_file"
}

# Export function for use with xargs
export -f update_agent
export NEW_POLICY_FILE

# Update all agent files (excluding ones already updated)
echo "Updating agent journal policies..."

# Get list of agents that don't have "Query First" yet
find ~/.claude/agent-reserves/ ~/.claude/agents/ ~/devel/*/\.claude/agents/ -name "*.md" -type f 2>/dev/null | \
    xargs grep -L "Query First" | \
    while read agent_file; do
        update_agent "$agent_file"
    done

echo "Update complete!"