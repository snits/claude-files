#!/bin/bash
# PreToolUse hook (matcher: Skill|EnterPlanMode). Injects the Project Kickoff
# Gate reminder when brainstorming or plan mode is invoked, so the gate is
# salient at the decision moment instead of buried in CLAUDE.md prose.
set -euo pipefail

input=$(cat)
tool_name=$(jq -r '.tool_name // empty' <<<"$input")

if [[ "$tool_name" == "Skill" ]]; then
  skill=$(jq -r '.tool_input.skill // empty' <<<"$input")
  case "$skill" in
    *brainstorming*) ;;
    *) exit 0 ;;
  esac
fi

jq -n '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    additionalContext: "Project Kickoff Gate (from ~/.claude/CLAUDE.md): if this is a NEW project or major feature kickoff, confirm these are stated before brainstorming or planning — (1) reference target (\"like X but Y\"; prior generations of our own projects and negative references count), (2) fidelity level (plausible/playable vs accurate/rigorous), (3) acceptance sketch (2-3 sentences of done), (4) SME-gap check (no nameable reference target -> run a research pass delivering candidate reference targets to choose between, not a survey), (5) risk spike check (name the technical unknown most likely to eat weeks). Deep-domain projects: the gate recurses — name the load-bearing subsystems and apply fidelity + SME-gap to each. Sequencing: unstructured discussion with Jerry until item 1 can be stated, THEN brainstorm. If any item is missing, ask Jerry for it — one at a time, in discussion, not as a form. If this is mid-project work or the gate is already satisfied in this conversation, proceed."
  }
}'
