1. Open `docs/00-project/TODO.md` () and select the first unchecked items to work on. If there are nested items in the todo list, traverse down the tree to the first unchecked leaf item. Parent items should only be marked as complete when all of their descendants are marked complete.
2. Using ToDoWrite create a list that includes the following steps:
    - A step to determine the most domain-relevant agent for completing the item. Read the corresponding prompt given in `docs/00-project/tdd-prompts.md` or in `docs/00-project/plan.md` if one didn't exist. If no prompt exists, create an appropriate prompt in the format used by the other prompts, and insert it into the document with the other prompts. Prioritize technical implementation and domain expert agents (such as rust-specialist, debug-specialist, performance-engineer) for code changes, architectural agents (such as systems-architect) for design decisions, security concerns to security-engineer, and testing to test-specialist. The agent should use the zen precommit tool prior completing their task if it involved code changes.
    - An initial step to task the agent with determining if the prompt, which you will include, is sufficient for the task with the following additions:
      - Ask the agent to walk through their thought process step-by-step in their response.
      - Ask the agent to request any information it feels it needs to do the job properly in their response.
    - A step to iteratively refine the prompt by repeatedly asking the agent to evaluate prompt sufficiency and request needed information, modifying the prompt based on agent feedback and search-specialist discoveries, and continuing until the agent confirms the prompt is sufficient for the task (maximum 3 iterations to prevent infinite loops).
    - A step to update the finalized prompt in `docs/00-project/tdd-prompts.md` as needed.
    - A step to task the agent with completing the actual todo item using the prompt from the previous steps.
    - A step for committing the change. Use get-agent-hash to get the hash for any agents involved. Any type checking, linting, formatting, and testing quality gates should happen here.
    - A step for tasking test-specialist to review any tests created for the item.
    - A step for tasking code-reviewer with doing quality gates for the change using the zen codereview tool.
    - A step for getting approval from Jerry to move forward.
3. Carry out the steps in the ToDoWrite list.
4. Check off the item in `docs/00-project/TODO.md` when it is completed. Items with children, should only be marked complete when all items nested below them are marked complete.
