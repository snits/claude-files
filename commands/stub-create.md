Create a tracked function stub with UUID for systematic implementation tracking.

**Arguments: $ARGUMENTS**
- Function description: "connectDatabase with retry logic"
- Optional flags: "--assign AGENT_NAME", "--priority high|medium|low", "--file PATH", "--returns TYPE"

**Stub Creation Process:**

1. **Generate UUID using same logic as todo-create:**
   ```bash
   # Cross-platform UUID generation  
   if command -v uuid >/dev/null 2>&1; then
       full_uuid=$(uuid -v4)
   elif command -v uuidgen >/dev/null 2>&1; then  
       full_uuid=$(uuidgen)
   else
       echo "❌ No UUID generator found"
       exit 1
   fi
   
   short_uuid=$(echo $full_uuid | cut -c1-8)
   ```

2. **Add to project documentation:**
   ```markdown
   ## Outstanding Stubs
   
   ### High Priority
   - `STUB-e5f6g7h8`: connectDatabase with retry logic
     - **Full UUID**: e5f6g7h8-1234-5678-9abc-def012345678
     - **Created**: 2025-08-15
     - **Assigned**: database-specialist
     - **File**: src/database.rs:45
     - **Returns**: Connection
     - **Status**: Open
   ```

3. **Generate stub code format based on context:**
   
   **Rust:**
   ```rust
   // STUB-e5f6g7h8: connectDatabase with retry logic
   fn connect_database() -> Connection {
       todo!("STUB-e5f6g7h8: Implement connection retry logic with exponential backoff")
   }
   ```
   
   **TypeScript:**
   ```typescript
   // STUB-e5f6g7h8: connectDatabase with retry logic  
   function connectDatabase(): Connection {
       throw new Error("STUB-e5f6g7h8: Implement connection retry logic");
   }
   ```
   
   **Python:**
   ```python
   # STUB-e5f6g7h8: connectDatabase with retry logic
   def connect_database() -> Connection:
       raise NotImplementedError("STUB-e5f6g7h8: Implement connection retry logic")
   ```

4. **Smart language detection:**
   - Check file extension or project type
   - Use appropriate stub/todo syntax for the language
   - Include proper error handling that references the UUID

5. **Integration with agent system:**
   - Suggest appropriate agent based on function description
   - Link to agent deployment if specialist not yet in project
   - Track which stubs are assigned to which agents

**Usage examples:**
```bash
/stub-create "Authentication middleware with JWT validation"
/stub-create "Database migration runner" --assign database-specialist --returns "MigrationResult"
/stub-create "API rate limiter" --file src/middleware.ts --assign security-engineer --priority high
```

**Quality Gate Features:**
- Prevent releases with unimplemented stubs
- Track stub-to-implementation conversion rates
- Enable stub aging reports (how long stubs remain unimplemented)
- Support stub dependency tracking

**Output format:**
- Generated stub code in appropriate language syntax
- Documentation entry added to outstanding-work.md
- Suggested agent assignment if not specified
- Current project stub summary and health metrics