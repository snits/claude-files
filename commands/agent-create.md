Task agent-prompt-engineer with creating a new agent prompt file in ~/.claude/agent-reserves/ using the optimized workflow that balances efficiency with quality.

**Arguments: $ARGUMENTS**

- Agent name: "database-optimization-specialist"
- With domain: "database-optimization-specialist --domain=performance"
- With color override: "database-specialist --color=blue"
- Skip defaults: "api-specialist --no-defaults" (forces interactive mode)

## Optimized Implementation Workflow

### TIER 1: Early Validation & Smart Defaults (30-60 seconds)

1. **Pre-Generation Validation:**
   - Extract agent name from $ARGUMENTS (first argument)
   - Ensure name follows kebab-case convention with auto-correction suggestions
   - **CRITICAL**: Check if agent already exists in ~/.claude/agent-reserves/ before proceeding
   - Add .md extension if not present

2. **Smart Defaults with Override Capability:**
   - **Agent name**: Extracted from input, validate kebab-case
   - **Display name**: Auto-generate from kebab-case ("database-specialist" → "Database Specialist")
   - **Domain expertise**: Extract from name patterns or use --domain flag
   - **Color category**: Auto-assign using domain keyword mapping (see below)
   - **Confirmation path**: "Creating 'Database Specialist' (blue category) - confirm? [Y/n]"

**Domain-to-Color Mapping System:**

- 🎮 **red**: Keywords: game, unity, unreal, gameplay, mechanics, balance
- 🏗️ **orange**: Keywords: architecture, system, infrastructure, platform, scalability
- 🔬 **cyan**: Keywords: scientific, mathematical, algorithm, research, analysis
- 💾 **blue**: Keywords: database, data, storage, query, analytics, warehouse
- ⚙️ **black**: Keywords: devops, engineering, build, deployment, automation, ci/cd
- 📋 **purple**: Keywords: process, management, workflow, optimization, efficiency
- 🔧 **yellow**: Keywords: language, compiler, parser, tool, cli, framework
- 📝 **green**: Keywords: documentation, content, writing, review, editing
- **Default**: gray (if no keywords match)

**Override Flags:**

- `--domain=<domain>`: Specify domain expertise directly
- `--color=<color>`: Override auto-selected color
- `--name="Display Name"`: Override auto-generated display name
- `--no-defaults`: Force interactive mode (skip all automation)

### TIER 2: Template Generation & Structure Validation (10-20 seconds)

3. **Generate agent content with validation:**
   - Use ~/claudes-home/templates/agent-prompt.md as base template
   - **Structure validation**: Verify template has required sections before generation
   - Replace template placeholders with collected/derived information:
     - `[agent-name]` → kebab-case name
     - `[Agent Name]` → display name (auto-generated or overridden)
     - `[role-based-color]` → selected color (auto-mapped or overridden)
     - `[agent role and expertise description]` → domain expertise
     - `[specific domain/capabilities]` → key capabilities
     - Fill in Core Expertise, Key Responsibilities, and other sections
     - Do not include code samples. The agent likely already knows them if you did.
   - **IMPORTANT**: Leave PROJECT-SPECIFIC-COMMANDS section with template placeholders
     - Keep `[project-specific-typecheck-command]` format in protected tags
     - Do NOT replace with actual commands (this happens during agent-deploy)

4. **Create agent file with format validation:**
   - Write to ~/.claude/agent-reserves/[agent-name].md
   - **Format consistency checks**: Validate standardized sections present:
     - Strategic Journal Policy (with Query First)
     - Persistent Output Requirement
     - Analysis Tools (including sequential-thinking guidance)
   - **File integrity check**: Verify file was written successfully and is readable

### TIER 3: Complexity-Based Quality Assessment (60-90 seconds)

**5. Intelligent iteration scaling based on agent complexity:**

**Complexity Assessment:**

- **Simple agents** (<5KB projected, single domain, standard patterns): **Skip iteration loop**
  - Example: "database-specialist", "api-reviewer", "test-helper"
  - Direct creation with final validation check

- **Standard agents** (5-15KB, focused domain, some customization): **Single improvement iteration**
  - Example: "performance-engineer", "security-analyst", "ui-specialist"
  - One round of parallel assessment and refinement

- **Complex agents** (>15KB, multiple domains, specialized workflows): **Full 3-iteration process**
  - Example: "game-engine-architect", "distributed-systems-expert", "ai-research-specialist"
  - Complete iterative improvement with deep validation

**Complexity Indicators:**

- Multiple domain keywords detected
- Specialized tool requirements mentioned
- Custom workflow patterns needed
- Integration with multiple other agents required
- Novel domain not covered by existing templates

**Parallel Quality Assessment Process:**

- Task clean-code-analyst with assessing ~/.claude/agent-reserves/[agent-name].md
- Assess yourself through the lens of [agent-name], with assessing ~/.claude/agent-reserves/[agent-name].md and the assessment from clean-code-analyst, and provide assessment of the prompt file
- Task agent-prompt-engineer with taking these 2 assessments and updating ~/.claude/agent-reserves/[agent-name].md
- **Iteration control**: Continue until quality gates pass or max iterations reached

**Override for Edge Cases:**

- `--complex`: Force full 3-iteration process regardless of size
- `--simple`: Skip iteration loop (use with caution)
- `--iterations=N`: Specify exact number of improvement rounds

6. **Confirm creation with integration hooks:**
   - Display success message with file path and agent classification
   - Show agent color, categorization, and complexity tier used
   - **Validation summary**: Report validation checks passed/failed
   - **Next steps guidance**: Suggest using `/agent-browse` to verify listing
   - **Integration note**: Remind about agent-deploy for project activation
   - **Quality metrics**: Report estimated agent effectiveness and completeness

## Example Usage Patterns

**Rapid Creation (uses smart defaults):**

```bash
/agent-create database-specialist
# → Creates "Database Specialist" with blue color, standard database capabilities

/agent-create api-security-expert
# → Creates "Api Security Expert" with black color (security + engineering keywords)
```

**Customized Creation:**

```bash
/agent-create blockchain-architect --domain="cryptocurrency and DeFi"
/agent-create data-processor --color=cyan --name="Data Processing Specialist"
/agent-create custom-agent --no-defaults  # Forces full interactive mode
```

**Complexity Control:**

```bash
/agent-create simple-helper --simple      # Skips iteration loop
/agent-create ai-researcher --complex     # Forces full 3-iteration process
/agent-create domain-expert --iterations=2 # Exactly 2 improvement rounds
```

## Smart Defaults Configuration

**Auto-Generated Sections:**

- Agent description (derived from domain and name)
- Display name (kebab-case → Title Case conversion)
- Color category (domain keyword → color mapping)
- Basic capabilities (domain-specific template snippets)

**Requires Customization:**

- Core Expertise (3-4 key areas specific to domain)
- Key Responsibilities (unique value proposition)
- Analysis Tools (domain-specific tools and workflows)
- Workflow Integration (coordination with other agents)
- Decision Authority (autonomous vs escalation boundaries)
- Success Metrics (measurable effectiveness criteria)
- Usage Guidelines (when and how to use effectively)

**Template Enhancement Areas:**

- Specialized workflow patterns
- Domain-specific quality gates
- Integration with external tools/systems
- Advanced decision-making frameworks

## Quality Gates & Validation

**Early Validation Checks (TIER 1):**

- [ ] Agent name follows kebab-case convention
- [ ] No existing agent with same name in ~/.claude/agent-reserves/
- [ ] Template file exists and is readable
- [ ] Domain keywords map to appropriate color category
- [ ] Required arguments provided or derivable from defaults

**Structure Validation (TIER 2):**

- [ ] Template placeholders properly replaced
- [ ] Required sections present (Core Expertise, Key Responsibilities, etc.)
- [ ] Strategic Journal Policy matches current template
- [ ] Persistent Output Requirement included
- [ ] PROJECT-SPECIFIC sections preserved with placeholders

**Quality Assessment (TIER 3):**

- [ ] Agent expertise clearly defined and scoped
- [ ] Decision authority boundaries appropriate for domain
- [ ] Usage guidelines clear and actionable
- [ ] Integration with other agents well-defined
- [ ] Success metrics measurable and relevant

**Performance Metrics:**

- **Target creation time**: 2-3 minutes (vs 4-6 minutes previously)
- **First-iteration success rate**: >90% (early validation prevents rework)
- **Error detection rate**: >95% in early validation phase
- **Quality consistency**: Standardized across all complexity tiers

## Error Handling & Recovery

**Common Error Scenarios:**

- **Agent name conflict**: Suggest alternative names or confirm overwrite
- **Invalid domain keywords**: Fall back to gray color with manual override option
- **Template missing/corrupted**: Clear error with resolution steps
- **File write permissions**: Detailed troubleshooting guidance

**Recovery Patterns:**

- **Validation failures**: Stop early with clear fix instructions
- **Template errors**: Provide template repair or regeneration options
- **Quality issues**: Offer re-run with different complexity tier
- **Integration problems**: Suggest manual review checkpoints

## Implementation Notes

**Sustainability Principles:**

- **Human judgment preserved**: Complex decisions still require human oversight
- **Quality standards maintained**: All existing quality gates preserved
- **Flexibility retained**: Override mechanisms for edge cases and custom requirements
- **Gradual adoption**: Can be implemented incrementally without breaking existing workflows

**Maintenance Requirements:**

- **Domain keyword mapping**: Update color mappings as new domains emerge
- **Template evolution**: Sync with template changes in ~/claudes-home/templates/
- **Quality metrics**: Monitor success rates and adjust complexity thresholds
- **User feedback integration**: Refine smart defaults based on usage patterns

**Future Enhancement Opportunities:**

- **Learning system**: Adapt defaults based on successful agent patterns
- **Integration APIs**: Connect with agent deployment and management systems
- **Batch creation**: Support for creating multiple related agents efficiently
- **Template variants**: Domain-specific template variations for common patterns
