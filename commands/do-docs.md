# Tiered Documentation Pipeline Architecture

I would like you to documentation using the process below for the following task: $ARGUMENTS

## Task sizing

- Given the above, first decide if the task should be broken up into multiple tasks. Task the codebase-analyzer agent to give you
  an idea of what you are working with codebase wise if needed.
   
## ToDoWrite setup

- Create a ToDoWrite task list consisting of steps for each task, and then sub-tasks for each task where the following will occur:

### **Tier 1**

1. Agent Selection: Determine agent best suited to task:
	- Technical Documentation: tech-docs-writer agent
	- Scientific Documentation: scientific-documentation-specialist agent
	- Publication Formatting: publication-formatter agent
	- general-purpose: general-purpose agent
	- for polishing work: copy-editor agent

	If an agent doesn't appear to be available ask Jerry to deploy the agent.

2. Generate a prompt for context research for the task. Iteratively refine the research prompt  with the codebase-analyzer agent (max 3 times)
   until the codebase-analyzer agent is satisfied with the prompt. The prompt must include a work product requirement of generating a
   markdown report of the research results.

3. Task the codebase-analyzer agent with the prompt from step 2.

## **Tier 2**

4. Using the report output from 3, generate a prompt for the chosen  agent to implement the documentation. Iteratively refine
   the prompt with the documentation agent (max 3 times) until the documentation agent is satisfied with the prompt. The work product
   should be markdown files, or files of an appropriate format for the given task.

5. Task the documentation agent with the prompt from 4.

## **Tier 3**

6. Present the results to Jerry, and get approval of work.

