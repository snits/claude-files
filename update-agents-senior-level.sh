#!/bin/bash
# Batch update all agents to include senior-level language

echo "Starting batch update of agent seniority language..."

updated_count=0
total_count=0

for agent_file in ~/.claude/agent-reserves/*.md; do
  total_count=$((total_count + 1))
  agent_name=$(basename "$agent_file" .md)
  
  # Check if already updated
  if grep -q "^You are a senior-level" "$agent_file"; then
    echo "Already updated: $agent_name"
    continue
  fi
  
  # Check if it has the old pattern
  if grep -q "^You are [^a]" "$agent_file"; then
    echo "Updating: $agent_name"
    
    # Update the "You are" line to add senior-level and authority language
    sed -i.bak \
      -e 's/^You are the /You are a senior-level /' \
      -e 's/^You are working/You are a senior-level professional working/' \
      -e 's/^You are \([^a]\)/You are a senior-level \1/' \
      -e '/^You are a senior-level.*\. You understand/ s/\. You understand/ with deep expertise in your domain. You operate with the judgment and authority expected of a senior professional. You understand/' \
      "$agent_file"
    
    # Clean up backup file
    rm -f "${agent_file}.bak"
    updated_count=$((updated_count + 1))
  else
    echo "Skipping (no standard pattern): $agent_name"
  fi
done

echo "Batch update complete!"
echo "Total agents: $total_count"
echo "Updated agents: $updated_count"