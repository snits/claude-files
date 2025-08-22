#!/bin/bash
# Fix the agent attribution patterns more precisely

echo "Fixing agent attribution patterns..."

for agent_file in agent-reserves/*.md; do
  agent_name=$(basename "$agent_file" .md)
  
  # Skip already fully updated agents  
  if grep -q "agent-hashes.json" "$agent_file" && ! grep -q "git log --oneline -1 .claude/agents" "$agent_file"; then
    echo "Skipping fully updated: $agent_name"
    continue
  fi
  
  echo "Fixing: $agent_name"
  
  # Replace the git log line with hash lookup priority
  sed -i.bak \
    -e "s|- Get SHORT_HASH from your agent file: \`git log --oneline -1 \.claude/agents/${agent_name}\.md \| cut -d' ' -f1\`|- **Hash Lookup Priority**:\n  1. **First choice**: Check \`.claude/agent-hashes.json\` for your SHORT_HASH (stay in project directory)\n  2. **Fallback only**: If mapping file missing, use \`git log --oneline -1 .claude/agents/${agent_name}.md \| cut -d' ' -f1\`|g" \
    "$agent_file"
    
  rm -f "${agent_file}.bak"
done

echo "Attribution pattern fixes complete!"
