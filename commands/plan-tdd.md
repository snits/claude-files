Iteratively generate a step-by-step blueprint for building this project using the zen planner tool to draft a detailed, step-by-step plan. Then, once you have a solid plan, break it down into small, iterative chunks that build on each other. Look at these chunks and then go another round to break it into small steps. Review the results and make sure that the steps are small enough to be implemented safely with strong testing, but big enough to move the project forward, and ideally will fit within the context window of the agent. Iterate until you feel that the  actionable tasks are right sized for this project. Ideally a step small enough to be accomplished with the context window size an agent has. Capture the plan into a markdown file in docs/00-project/plan.md. Also create a docs/00-project/TODO.md to maintain state of on overall ToDoWrite list of the actionable tasks for the plan. The list should contain actionable tasks and sub-tasks in a nested structure. Example of what I mean by nested:

**Phase 1**

- [ ] Task 1
  - [ ] Sub-task 1.1
  - [ ] Sub-task 1.2
    - [ ] Sub-task 1.2.1
- [ ] Task 2

Then task plan-validator with looking over for any issues. Address any issues that are raised.

From here you should have the foundation to provide a series of prompts for a code-generation LLM that will implement each step in a test-driven manner. Prioritize best practices, incremental progress, and early testing, ensuring no big jumps in complexity at any stage. Make sure that each prompt builds on the previous prompts, and ends with wiring things together. There should be no hanging or orphaned code that isn't integrated into a previous step. Capture the prompts in a directory docs/00-project/tdd-prompts/ in individual markdown files for each prompt, with the file appropriately named so that you can easily find it.

Each prompt should be tagged as text using code tags. The goal is to output prompts, but context, etc is important as well.

The spec, or initial plan is in the file called:
