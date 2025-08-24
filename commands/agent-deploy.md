Deploy agents from ~/.claude/agent-reserves/ to current project using COW reflinks.

**Arguments: $ARGUMENTS**
- Single agent: "rust-specialist" 
- Multiple agents: "rust-specialist game-engine-architect"
- Preview mode: "database-specialist --preview"

**Implementation steps:**
1. **Validate environment:**
   - Check if `.claude/agents/` directory exists in current project
   - If not, inform user to run from project root or create directory

2. **Parse arguments:**
   - Split $ARGUMENTS into individual agent names and flags
   - Handle --preview flag separately
   - Add .md extension if not present

3. **For each agent:**
   - Check if agent exists in ~/.claude/agent-reserves/
   - Check if already deployed in project
   - If preview mode: show what would happen
   - If deploy mode: 
     - Copy agent using `cp --reflink=auto` to create COW reflink
     - **CRITICAL**: Update PROJECT-SPECIFIC-COMMANDS section with project commands
       - Detect project type (pyproject.toml → Python, Cargo.toml → Rust, package.json → Node)
       - Replace template placeholders with actual commands:
         - Python: `uv run mypy src/`, `uv run ruff check`, `uv run pytest`, `uv run ruff format`
         - Rust: `cargo check`, `cargo clippy`, `cargo test`, `cargo fmt`
         - Node: `npm run typecheck`, `npm run lint`, `npm run test`, `npm run format`

4. **Use these bash commands:**
   ```bash
   cp --reflink=auto ~/.claude/agent-reserves/AGENT.md .claude/agents/AGENT.md
   # Fallback: cp ~/.claude/agent-reserves/AGENT.md .claude/agents/AGENT.md
   ```

5. **Provide feedback:**
   - ✅ Successfully deployed count
   - ⚠️ Already exists warnings  
   - ❌ Not found errors
   - 💡 Reminder about COW reflink behavior

**Error handling:**
- No arguments: Show usage and suggest /agent-browse
- Not in project: Explain directory requirement
- Agent not found: Suggest /agent-browse to discover agents
- Already exists: Explain removal and redeployment