Jerry is preparing for context compaction. Before any compaction can occur, you MUST systematically check and clean up the current session state:

**MANDATORY PRE-COMPACTION CHECKLIST:**

1. **Git Status Check**: Run `git status` to identify any uncommitted changes or untracked files
2. **Commit Pending Changes**: If there are modifications, stage and commit them with a clear message like "pre-compaction cleanup: [brief description]"
3. **TodoWrite Status**: Review current todo list and mark any completed tasks, document any in-progress work that needs to survive compaction
4. **Session State Summary**: Briefly summarize current working context, key decisions, and next steps
5. **File Modifications**: List any files that were created/modified in this session that need to be preserved
6. **Agent Context**: If any agents were used, note their outputs and any pending handoffs

**CRITICAL REMINDER**: Auto-compaction loses session memory of uncommitted file changes. This checklist prevents orphaned modifications.

Only after completing this checklist should Jerry proceed with compaction (/compact or /checkpoint).

Report your findings for each checklist item before declaring the session ready for compaction.