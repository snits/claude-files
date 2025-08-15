Initialize a new project with complete agent management infrastructure and standard project files.

**Arguments: $ARGUMENTS**
- Project name/type: "rust-api", "python-ml", "typescript-web", etc.
- Optional flags: "--no-agents", "--minimal"

**Project Setup Tasks:**

1. **Create project structure:**
   - Initialize main git repository if not exists
   - Create standard project directories
   - Set up basic project files (README.md, etc.)

2. **Configure .gitignore:**
   - Add `.claude/` to gitignore (keeps agent management separate)
   - Add language-specific ignores based on project type
   - Add common development ignores (logs, temp files, etc.)

3. **Set up agent management infrastructure:**
   - Create `.claude/agents/` directory 
   - Initialize separate git repo in `.claude/agents/`
   - Create initial README.md in agents repo explaining the workflow
   - Set up agent repo with proper remote (ask for GitHub repo URL)

4. **Project-specific setup based on type:**
   - **Rust projects**: Cargo.toml, src/main.rs, basic CI/CD
   - **Python projects**: pyproject.toml, requirements.txt, basic structure  
   - **TypeScript projects**: package.json, tsconfig.json, basic setup
   - **Web projects**: Add frontend-specific ignores and structure

5. **Create essential project files:**
   - README.md with project description and setup instructions
   - Basic CI/CD configuration files
   - Development scripts or Makefile
   - Documentation structure (docs/ directory)

6. **Agent workflow setup:**
   - Suggest initial agents based on project type
   - Provide `/agent-deploy` examples for the project type
   - Document the agent attribution workflow in project README

**Use bash commands for:**
- `git init` (both main project and .claude/agents)
- `git remote add origin URL` 
- Creating directory structures with `mkdir -p`
- Writing template files based on project type
- Setting up basic .gitignore patterns

**Handle edge cases:**
- Project already has git repo
- .claude directory already exists  
- Different project types requiring different setups
- User doesn't want agent management (--no-agents flag)

**End with:**
- Summary of what was created
- Next steps for development
- Suggested agents to deploy for this project type
- Commands to set up remote repositories