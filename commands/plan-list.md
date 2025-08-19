List all planning documents and project plans with categorization and summary information.

**Displays plans organized by category with file information:**

**📋 PLANNING DOCUMENTS (from ~/clauses-home/plans/):**
- Show plan name, size, and brief description extracted from ABOUTME headers
- Categorize by plan type (MCP Integration, Infrastructure, Applications, etc.)
- Sort by category, then alphabetically within each category

**Implementation:**

1. **Scan plans directory:**
   ```bash
   ls ~/clauses-home/plans/*.md 2>/dev/null | sort
   ```

2. **Extract plan metadata for each file:**
   ```bash
   # Get file size
   du -h "$file" | cut -f1
   
   # Extract ABOUTME description (first two lines starting with "ABOUTME:")
   grep "^ABOUTME:" "$file" | head -2
   
   # Get file modification date for recency
   stat -f "%Sm" -t "%Y-%m-%d" "$file"
   ```

3. **Categorize plans by keywords in filename/content:**
   - 🤖 **MCP & Integration**: *mcp*, *integration*, *api*, *server*
   - 🏗️ **Infrastructure**: *architecture*, *system*, *framework*, *platform*
   - 🎮 **Applications**: *app*, *gui*, *game*, *interface*, *tool*
   - 📊 **Analysis & Quality**: *metrics*, *analysis*, *quality*, *assessment*
   - 🔧 **Development Tools**: *testing*, *automation*, *workflow*, *process*
   - 📚 **Documentation**: *docs*, *documentation*, *knowledge*, *library*
   - 🚀 **Deployment**: *deployment*, *production*, *ops*, *infra*
   - 📝 **General**: Everything else

4. **Extract brief descriptions:**
   - Use ABOUTME headers as primary source
   - Fall back to first meaningful heading or sentence
   - Format: "plan-name (size, date): Brief description"

**Sample output format:**
```
📋 PLANNING DOCUMENTS (~/claudes-home/plans/)

🤖 MCP & Integration (3 plans):
├── automated-code-metrics-mcp.md (8.2KB, 2025-08-19): Algorithmic code quality assessment server
├── context7-alexandria-integration.md (3.4KB, 2025-08-15): Real-time documentation integration 
└── zoo-dev-cad-mcp-integration.md (12.1KB, 2025-08-19): CAD design with ML-powered Zoo.dev APIs

🏗️ Infrastructure (2 plans):
├── linux-microkernel-project-plan.md (15.8KB, 2025-08-18): Kernel decomposition timeline
└── memory-distillation-architecture.md (6.2KB, 2025-08-14): Memory system design

🎮 Applications (3 plans):
├── alpha-prime-gui-testing-mcp-plan.md (4.1KB, 2025-08-16): GUI testing framework
├── desert-island-games-technical-blog.md (2.8KB, 2025-08-12): Technical blog content
└── screenshot-to-wireframe-converter.md (2.9KB, 2025-08-13): Design tool automation

📊 Analysis & Quality (1 plan):
└── kernel-fixes-benchmark-testing-framework.md (3.5KB, 2025-08-17): Performance testing

📝 General (3 plans):
├── ai-augmentation-benchmark-experiment.md (4.2KB, 2025-08-11): AI capability assessment
├── natural-language-automation-potential.md (3.1KB, 2025-08-10): Automation possibilities
└── text-to-speech-mcp-integration.md (1.9KB, 2025-08-09): Audio interface integration

Total: 12 plans, 58.1KB of planning documentation
Last updated: 2025-08-19

💡 Use 'project-librarian' agent to analyze plan relationships and connections
💡 Use '/plan-search KEYWORD' to find specific plans (if implemented)
```

**Command options:**
- `/plan-list` - Show all plans categorized (default)
- `/plan-list --recent` - Show only plans modified in last 7 days
- `/plan-list --category MCP` - Show only specific category
- `/plan-list --size` - Sort by file size instead of category
- `/plan-list --brief` - Compact format with just names and sizes

**Error handling:**
- If ~/clauses-home/plans/ doesn't exist: explain directory structure
- Handle permission issues gracefully
- Show clear totals and statistics for easy scanning
- Handle missing ABOUTME headers gracefully (use filename or first line)

**Categorization logic:**
```bash
categorize_plan() {
    local file="$1"
    local basename=$(basename "$file" .md)
    local content=$(head -10 "$file" | tr '[:upper:]' '[:lower:]')
    
    if echo "$basename $content" | grep -qE "(mcp|integration|api|server)"; then
        echo "🤖 MCP & Integration"
    elif echo "$basename $content" | grep -qE "(architecture|system|framework|platform|infrastructure)"; then
        echo "🏗️ Infrastructure"
    elif echo "$basename $content" | grep -qE "(app|gui|game|interface|tool|testing)"; then
        echo "🎮 Applications"
    elif echo "$basename $content" | grep -qE "(metrics|analysis|quality|assessment|benchmark)"; then
        echo "📊 Analysis & Quality"
    elif echo "$basename $content" | grep -qE "(workflow|process|automation|deployment)"; then
        echo "🔧 Development Tools"
    elif echo "$basename $content" | grep -qE "(docs|documentation|knowledge|library)"; then
        echo "📚 Documentation"
    else
        echo "📝 General"
    fi
}
```

**Future enhancements:**
- Integration with project-librarian for plan relationship analysis
- Search functionality across plan content
- Plan status tracking (draft, active, completed, archived)
- Cross-references between related plans
- Timeline view showing plan evolution over time