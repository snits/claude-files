Deep search through agent capabilities and expertise areas in ~/.claude/agent-reserves/

**Search Terms: $ARGUMENTS**

**Task:**
1. Search through all agent files for mentions of the search terms
2. Score results by relevance:
   - Filename matches (higher weight)
   - Content frequency (number of mentions)
   - Context relevance

3. **Use these bash commands:**
   - `grep -ci "TERM" ~/.claude/agent-reserves/*.md` for content counting
   - `basename file .md` to get clean agent names  
   - Search both filenames and file contents

4. **Present results ranked by relevance:**
   - Show agent name, relevance score, and match context
   - Include brief explanation of why each agent matches
   - Format as: "🎯 AGENT_NAME (score: X) [context]"

5. **Always end with:**
   - "💡 Use '/agent-deploy AGENT_NAME' to add to current project"
   - "💡 Use '/agent-browse' to explore by category"

**Handle edge cases:**
- No arguments: show usage and examples
- No matches: suggest broader search terms
- Multiple term matches: combine scores intelligently