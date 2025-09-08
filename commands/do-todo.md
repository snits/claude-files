1. Open `docs/00-project/TODO.md` () and select the first unchecked items to work on. If there are nested items in the todo list, traverse down the tree to the first unchecked leaf item. Parent items should only be marked as complete when all of their descendants are marked complete.
2. Using ToDoWrite create a list that includes the following steps:
    - A step to task the most domain-relevant agent with completing the item, using the corresponding prompt given in `docs/00-project/tdd-prompts.md` or in `docs/00-project/plan.md` if one didn't exist. If no prompt exists, create an appropriate prompt in the format used by the other prompts, and insert it into the document with the other prompts. Prioritize technical implementation and domain expert agents (such as rust-specialist, debug-specialist, performance-engineer) for code changes, architectural agents (such as systems-architect) for design decisions, security concerns to security-engineer, and testing to test-specialist. The agent should use the zen precommit tool prior completing their task if it involved code changes.
    - A step for committing the change. Use get-agent-hash to get the hash for any agents involved.
    - A step for tasking test-specialist to review any tests created for the item.
    - A step for tasking code-reviewer with doing quality gates for the change.
    - A step for getting approval from Jerry to move forward.
3. Create a new branch.
4. Carry out the steps in the ToDoWrite list.
5. Check off the item in `docs/00-project/TODO.md` when it is completed. Items with children, should only be marked complete when all items nested below them are marked complete.
