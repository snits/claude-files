Show all running Claude instances and their current working contexts.

**Displays active Claude instances with:**

**🤖 CLAUDE INSTANCES:**
- Process ID and resource usage
- Working directory and project context
- Runtime duration
- Current activity status

**Implementation:**
1. **Find Claude processes:**
   ```bash
   ps aux | grep -E "claude$" | grep -v grep
   ```

2. **Get working directories:**
   ```bash
   for pid in $(ps aux | grep -E "claude$" | grep -v grep | awk '{print $2}'); do
     echo "PID $pid: $(lsof -p $pid 2>/dev/null | grep cwd | awk '{print $9}')"
   done
   ```

3. **Enhance with project context:**
   - Extract project name from working directory
   - Show git branch if in a git repo
   - Indicate current vs other instances

**Sample output format:**
```
🤖 CLAUDE INSTANCES (3 active):

├── 6577 [CURRENT] • claudes-home • main branch
│   ├── CPU: 18.7% • Memory: 546MB • Runtime: 11m
│   └── 🏠 Home/coordination workspace
│
├── 57786 • desert-island/clean-alpha • feature/combat-system  
│   ├── CPU: 0.0% • Memory: 75MB • Runtime: 1h 44m
│   └── 🎮 Game development (idle)
│
└── 52294 • devel/metis • main branch
    ├── CPU: 0.0% • Memory: 72MB • Runtime: 1h 26m  
    └── 📊 Mathematical modeling (idle)

💡 Use 'claude-post' for inter-instance coordination
💡 Kill idle instances with 'kill PID' if needed
```

**Error handling:**
- Handle permission issues for lsof gracefully
- Show clear status if no other instances found
- Indicate if working directory access is restricted