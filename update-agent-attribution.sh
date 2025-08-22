#!/bin/bash
# Update agent attribution sections with hash mapping knowledge

for agent_file in agent-reserves/*.md; do
  agent_name=$(basename "$agent_file" .md)
  echo "Updating $agent_name..."
  
  # Use sed to update the attribution section
  sed -i.bak \
    -e 's/Add proper self-attribution: `Assisted-By: \[agent-name\]/Always self-attribute when you write code\/documents**: `Assisted-By: '"$agent_name"'/g' \
    -e 's/Get SHORT_HASH from your agent file: `git log --oneline -1 \.claude\/agents\/\[agent-name\]\.md | cut -d'"'"' '"'"' -f1`/**Hash Lookup Priority**:\n  1. **First choice**: Check `.claude\/agent-hashes.json` for your SHORT_HASH (stay in project directory)\n  2. **Fallback only**: If mapping file missing, use `git log --oneline -1 .claude\/agents\/'"$agent_name"'.md | cut -d'"'"' '"'"' -f1`/g' \
    -e 's/If `\.claude\/agents\/` is a separate repository, get hash from that repo/**Always dual attribution**: Co-Authored-By Claude + Assisted-By agent in every commit you create/g' \
    "$agent_file"
done

echo "Attribution updates complete!"
