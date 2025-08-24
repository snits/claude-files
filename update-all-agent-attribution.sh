#!/bin/bash
# Batch update all agent attribution sections with hash mapping knowledge

echo "Starting batch update of agent attribution sections..."

for agent_file in agent-reserves/*.md; do
  agent_name=$(basename "$agent_file" .md)
  
  # Skip agents we already updated manually
  if [[ "$agent_name" =~ ^(git-scm-master|systems-architect|rust-specialist|integration-specialist|performance-engineer)$ ]]; then
    echo "Skipping already updated: $agent_name"
    continue
  fi
  
  echo "Updating: $agent_name"
  
  # Update the attribution requirements section
  sed -i.bak \
    -e "s/Get SHORT_HASH from your agent file: \`git log --oneline -1 \.claude\/agents\/\[agent-name\]\.md | cut -d' ' -f1\`/**Hash Lookup Priority**:\n  1. **First choice**: Check \`.claude\/agent-hashes.json\` for your SHORT_HASH (stay in project directory)\n  2. **Fallback only**: If mapping file missing, use \`git log --oneline -1 .claude\/agents\/${agent_name}.md | cut -d' ' -f1\`/g" \
    -e "s/If \`\.claude\/agents\/\` is a separate repository, get hash from that repo/**Always dual attribution**: Co-Authored-By Claude + Assisted-By agent in every commit you create/g" \
    "$agent_file"
    
  # Clean up backup file
  rm -f "${agent_file}.bak"
done

echo "Batch update complete!"
