Create a tracked TODO item with UUID for systematic technical debt management.

**Arguments: $ARGUMENTS**
- Description: "Optimize database connection pooling"
- Optional flags: "--assign AGENT_NAME", "--priority high|medium|low", "--file PATH"

**TODO Creation Process:**

1. **Generate UUID:**
   ```bash
   # Cross-platform UUID generation
   if command -v uuid >/dev/null 2>&1; then
       full_uuid=$(uuid -v4)
   elif command -v uuidgen >/dev/null 2>&1; then  
       full_uuid=$(uuidgen)
   else
       echo "❌ No UUID generator found (install uuid package or use macOS uuidgen)"
       exit 1
   fi
   
   # Create 8-character short UUID for code comments
   short_uuid=$(echo $full_uuid | cut -c1-8)
   ```

2. **Create project TODO tracking file if needed:**
   - Check if `docs/outstanding-work.md` exists
   - Create with proper header structure if missing
   - Use consistent format for tracking

3. **Add to project documentation:**
   ```markdown
   ## Outstanding TODOs
   
   ### High Priority
   - `TODO-a1b2c3d4`: Optimize database connection pooling
     - **Full UUID**: a1b2c3d4-e5f6-7890-abcd-ef1234567890
     - **Created**: 2025-08-15
     - **Assigned**: database-specialist
     - **File**: src/database.rs:45
     - **Status**: Open
   ```

4. **Generate code comment format:**
   ```
   // TODO-a1b2c3d4: Optimize database connection pooling
   ```

5. **Provide insertion guidance:**
   - Show the comment format to insert at appropriate location
   - If --file specified, show specific line number suggestions
   - Remind about assignment if agent specified

6. **Update project metrics:**
   - Count total outstanding TODOs
   - Show priority distribution
   - Warn if TODO count exceeds project threshold (if configured)

**Usage examples:**
```bash
/todo-create "Fix memory leak in data processor"
/todo-create "Add input validation" --assign security-engineer --priority high
/todo-create "Optimize query performance" --file src/database.rs --assign database-specialist
```

**Quality Gate Integration:**
- Track total TODO count for project health metrics
- Provide UUID for later completion verification
- Enable TODO assignment to appropriate agents
- Support TODO aging and priority management

**Output format:**
- Generated UUID and comment format
- Documentation entry added
- Assignment confirmation (if specified)
- Current project TODO summary