# Agent Sync Analysis Status

## Context
Jerry and I were working on comparing project agents against agent-reserves to identify where PROJECT_SPECIFIC wrapper tags should be added before syncing.

## Completed Setup
✅ Mac Studio agent sync foundation complete:
- All 8 projects have agent directories with git repos
- All projects have .claude/ exclusions in .gitignore  
- All existing agent files committed to preserve them
- sync-project-agents script updated with environment variable validation

## Current Task
Need to analyze agent differences across these projects:
- ~/devel/ai-gatekeeper/.claude/agents/
- ~/devel/alexandria/.claude/agents/
- ~/devel/mnemosyne/.claude/agents/
- ~/devel/reposentry/.claude/agents/
- ~/devel/metis/.claude/agents/
- ~/desert-island/alpha-prime/.claude/agents/
- ~/desert-island/sim-prototype/.claude/agents/
- ~/devel/youtube-transcript-mcp/.claude/agents/

## Analysis Goals
1. Identify agents that exist in both project and agent-reserves
2. Compare content to find project-specific customizations
3. Recommend what needs PROJECT_SPECIFIC wrapper tags before sync
4. Categorize differences as: PROJECT_SPECIFIC candidates, outdated base content, or unclear

## Issue
Task tool was failing from claudes-home working directory. Jerry is restarting from ~/devel to continue the analysis.

## Agent Reserves Location
~/.claude/agent-reserves/ (91 base agents available)

## Next Steps
Resume analysis from ~/devel directory to compare project agents against base agents and recommend PROJECT_SPECIFIC tag placements.