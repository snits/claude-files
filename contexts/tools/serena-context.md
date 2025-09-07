# Serena MCP Tools: Code Analysis & Discovery

## Core Code Discovery Tools

**`mcp__serena__get_symbols_overview`** - File Structure Understanding
- **When to Use**: First step exploring ANY new file or understanding code structure
- **Capabilities**: High-level overview of all symbols (classes, functions, methods), symbol hierarchy analysis
- **Benefits**: Quick structural understanding without reading full file content

**`mcp__serena__find_symbol`** - Precise Code Symbol Discovery
- **When to Use**: Finding specific classes, functions, methods, variables across codebase
- **Capabilities**: Powerful pattern matching (exact, substring, hierarchical), codebase or directory search, symbol body inclusion
- **Filters**: Symbol types (class=5, function=12, method=6, variable=13, etc.)

**`mcp__serena__search_for_pattern`** - Flexible Codebase Search
- **When to Use**: Complex pattern matching, regex searches, finding usage patterns
- **Capabilities**: Regular expression with context, file type filtering, glob inclusion/exclusion
- **Context**: Configurable lines before/after matches for comprehensive understanding

**`mcp__serena__find_referencing_symbols`** - Usage & Impact Analysis
- **When to Use**: Understanding symbol usage, impact analysis, refactoring planning
- **Capabilities**: Find all references to specific symbols, usage pattern analysis, dependency mapping

## Code Modification Tools

**`mcp__serena__replace_symbol_body`** - Precise Symbol Updates
- **Application**: Function/method implementation updates, class modifications with surgical precision
- **Benefits**: Maintains proper indentation, affects only target symbol without surrounding code changes

**`mcp__serena__insert_after_symbol` & `mcp__serena__insert_before_symbol`**
- **Application**: Strategic addition of methods, functions, imports relative to existing symbols
- **Benefits**: Contextual insertion, maintains code organization, proper indentation handling

## Strategic Code Analysis Workflows

**🔍 Codebase Exploration Workflow**:
1. `get_symbols_overview` - Understand file structure
2. `find_symbol` - Locate specific components  
3. `find_referencing_symbols` - Understand usage patterns
4. `search_for_pattern` - Find implementation patterns

**🏗️ Architecture Analysis Workflow**:
1. `find_symbol` with wildcards - Find domain components
2. `search_for_pattern` - Architectural patterns and connections
3. `find_referencing_symbols` - Map dependencies and relationships

**🔧 Refactoring Preparation Workflow**:
1. `find_symbol` - Locate refactoring target
2. `find_referencing_symbols` - Assess impact scope
3. `search_for_pattern` - Find related patterns needing updates

## Integration with Analysis Tools

**Combined with zen tools**:
- **zen thinkdeep + serena find_symbol**: Systematic code analysis with expert reasoning
- **zen debug + serena search_for_pattern**: Evidence-based debugging with code discovery
- **zen consensus + serena architecture analysis**: Multi-model architectural decisions

**Project Memory Integration**:
- **`mcp__serena__write_memory`**: Document architectural decisions, patterns discovered
- **`mcp__serena__read_memory`**: Access project knowledge for context continuity
- **Usage**: Persistent project knowledge across sessions with searchable context