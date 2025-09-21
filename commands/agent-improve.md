Iteratively improve the $1 agent prompt file by using the following process:

- Task clean-code-analyst with asessing ~/.claude/agent-reserves/$1.md
- Task $1, if available otherwise assess it yourself through the lense of $1, with assessing ~/.claude/agent-reserves/$1.md and the assessment from clean-code-analyst, and provide assessment of the prompt file.
- Task agent-prompt-engineer with taking these 2 assessments and updating ~/.claude/agent-reserves/$1.md
- Do not include code samples as part of the prompt file.

Do this until agents are satisfied with the $1 prompt file, or you have done 3 iterations.

**PROMPT REQUIREMENT:** - If an agent prompt has explicit personalities mentioned of real-world people (examples: Steve Jobs, Sid Meier, Dani Bunten), or categories of people (example: code reviewer on linux kernel mailing list) those characteristics must be maintained in the improved prompt. It is an essential part of the prompt itself.

If the focus of a agent is narrowed down, suggest potential specialized agents that could be created to fill in gaps.
