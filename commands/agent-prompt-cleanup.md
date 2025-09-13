Iteratively improve the $1 agent prompt file by using the following process:

- Task clean-code-analyst with asessing ~/.claude/agent-reserves/$1.md
- Task $1, if available otherwise assess it yourself through the lense of $1, with assessing ~/.claude/agent-reserves/$1.md and the assessment from clean-code-analyst, and provide assessment of the prompt file.
- Task agent-prompt-engineer with taking these 2 assessments and updating ~/.claude/agent-reserves/$1.md

Do this until agents are satisfied with the $1 prompt file, or you have done 3 iterations.
