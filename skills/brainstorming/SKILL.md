---
name: brainstorming
description: Use when creating or developing anything, before writing code or implementation plans - consults domain experts to validate premise and evaluate approaches, then refines ideas into fully-formed designs through structured questioning and incremental validation
---

# Brainstorming Ideas Into Designs

## Overview

Transform rough ideas into fully-formed designs through structured questioning and alternative exploration.

**Core principle:** Ask questions to understand, explore alternatives, present design incrementally for validation.

**Announce at start:** "I'm using the brainstorming skill to refine your idea into a design."

## Quick Reference

| Phase | Key Activities | Tool Usage | Output |
|-------|---------------|------------|--------|
| **1. Understanding** | Ask questions (one at a time) | AskUserQuestion for choices | Purpose, constraints, criteria |
| **1.5. Domain Experts & Premise** | Identify specialists, validate premise | Task tool for specialist consultation | Validated premise OR simpler alternative |
| **2. Exploration** | Propose 2-3 approaches | AskUserQuestion for approach selection | Architecture options with trade-offs |
| **3. Design Presentation** | Present in 200-300 word sections | Open-ended questions | Complete design with validation |
| **4. Design Documentation** | Write design document | writing-clearly-and-concisely skill | Design doc in docs/plans/ |
| **5. Worktree Setup** | Set up isolated workspace | using-git-worktrees skill | Ready development environment |
| **6. Planning Handoff** | Create implementation plan | writing-plans skill | Detailed task breakdown |

## The Process

Copy this checklist to track progress:

```
Brainstorming Progress:
- [ ] Phase 1: Understanding (purpose, constraints, criteria gathered)
- [ ] Phase 1.5: Domain Experts & Premise (specialists identified and consulted, premise validated OR simpler alternative found)
- [ ] Phase 2: Exploration (2-3 approaches proposed and evaluated)
- [ ] Phase 3: Design Presentation (design validated in sections)
- [ ] Phase 4: Design Documentation (design written to docs/plans/)
- [ ] Phase 5: Worktree Setup (if implementing)
- [ ] Phase 6: Planning Handoff (if implementing)
```

### Phase 1: Understanding
- Check current project state in working directory
  - **Optional:** Consult discovery agents (see `consultants:consulting-agents`) to find relevant existing code, patterns, or components
  - Helpful when idea builds on or interacts with existing functionality
- Ask ONE question at a time to refine the idea
- **Use AskUserQuestion tool** when you have multiple choice options
- Gather: Purpose, constraints, success criteria

**Example using AskUserQuestion:**
```
Question: "Where should the authentication data be stored?"
Options:
  - "Session storage" (clears on tab close, more secure)
  - "Local storage" (persists across sessions, more convenient)
  - "Cookies" (works with SSR, compatible with older approach)
```

### Phase 1.5: Domain Expert Identification & Premise Validation

**When Phase 1.5 is REQUIRED:**

Use Phase 1.5 for **significant features** - skip only for trivial changes.

**Significant features include:**
- New services, databases, or external integrations
- Architecture changes (new patterns, storage layers, async processing)
- Security-sensitive functionality (auth, payments, PII handling)
- Performance-critical paths (high-traffic APIs, real-time processing)
- Multi-domain complexity (touches 3+ technical domains)

**Red flags that trigger Phase 1.5:**
- "We should add..." without evidence of need
- "Users might want..." without metrics or user research
- Solutions looking for problems
- Complexity increases without validated benefit

#### Phase 1.5a: Identify Domain Expertise Needed

After Phase 1 understanding, analyze what technical domains the idea touches.

**Example analysis:**
```
"This involves database schema changes, async background processing, and semantic search"
"Domains: database design, data pipelines, performance optimization"
"Needed specialists: database-optimization-specialist, data-pipeline-architect, performance-engineer"
```

**Present to Jerry:**
```
"Based on the idea, I think we need these specialists:
- [specialist-name]: [why needed for this idea]
- [specialist-name]: [why needed for this idea]

Should I wait while you create these agents, or do they already exist in the project?"
```

**Wait for Jerry to:**
- Create new specialists (using his templates)
- Point to existing specialists in project or other projects
- Confirm you can proceed

#### Phase 1.5b: Premise Validation (REQUIRED)

**Use Task tool to consult specialists** identified in 1.5a.

**Specialist mission:** Question the premise, not design implementation.

**Questions specialists MUST address:**
1. **Evidence of need:** What metrics/data show this problem exists?
2. **Current state:** What's actually failing with current approach?
3. **Simpler alternatives:** Can we solve this without the proposed complexity?
4. **Complexity costs:** What's the operational/maintenance burden?
5. **Success criteria:** How will we know this actually helped?

**Example consultation:**
```
Task: consultants:architecture-specialist

"Please evaluate whether we should build [feature description].

Question the premise:
- What evidence do we have this is needed?
- What simpler alternatives exist?
- What are the complexity costs?
- How will we measure success?

Your goal is to challenge the idea, not design it."
```

**Incorporate specialist feedback:**
- If specialists identify fatal flaws → Return to Phase 1 or abandon idea
- If specialists suggest simpler alternatives → Explore those instead
- If premise validated → Document evidence/metrics in design, proceed to Phase 2

**TodoWrite enforcement:**

Add these todos when entering Phase 1.5:
1. "Identify domain expertise needed for [idea]"
2. "Consult [specialist-name] for premise validation"
3. "Incorporate specialist premise feedback"

**Output:** Either validated premise with evidence, or return to Phase 1 with specialists' simpler alternatives.

### Phase 2: Exploration

**Step 1: Draft approaches**
- Propose 2-3 different approaches
- For each: Core architecture, trade-offs, complexity assessment

**Step 2: Specialist evaluation (if needed)**

**When specialist evaluation is needed:**
- Approaches have significant architectural trade-offs (event-driven vs synchronous, storage patterns, concurrency models)
- Performance, security, or scalability implications differ between options
- Multiple valid technical solutions with different complexity/benefit profiles

**When you can skip specialist evaluation:**
- Approach is straightforward with no architectural decisions
- Specialists already addressed approach in Phase 1.5b premise validation
- Work is cleanup, deletion, or obvious implementation

**If skipping:** Briefly explain why (e.g., "Specialists already validated this in Phase 1.5b" or "No architectural trade-offs to evaluate").

**If needed:**
- **Use Task tool** to consult specialists from Phase 1.5a
- Ask specialists to evaluate technical soundness of each approach
- Questions: Performance characteristics, scalability, failure modes, operational complexity

**Example consultation:**
```
Task: consultants:database-optimization-specialist

"Please evaluate these 3 database approaches for [feature]:

Approach A: [description]
Approach B: [description]
Approach C: [description]

For each, assess:
- Query performance characteristics
- Schema migration complexity
- Scalability concerns
- Data consistency trade-offs"
```

**Step 3: Present evaluated approaches to Jerry**
- Incorporate specialist feedback into trade-off descriptions
- **Use AskUserQuestion tool** to present approaches as structured choices
- Ask which approach resonates

**Example using AskUserQuestion:**
```
Question: "Which architectural approach should we use?"
Options:
  - "Event-driven with message queue" (scalable, complex setup, eventual consistency - architect notes: introduces retry complexity)
  - "Direct API calls with retry logic" (simple, synchronous, easier to debug - architect notes: may hit rate limits)
  - "Hybrid with background jobs" (balanced, moderate complexity - architect notes: best fault isolation)
```

### Phase 3: Design Presentation
- Present in 200-300 word sections
- Cover: Architecture, components, data flow, error handling, testing
- Ask after each section: "Does this look right so far?" (open-ended)
- Use open-ended questions here to allow freeform feedback

### Phase 4: Design Documentation
After design is validated, write it to a permanent document:
- **File location:** `docs/plans/YYYY-MM-DD-<topic>-design.md` (use actual date and descriptive topic)
- **RECOMMENDED SUB-SKILL:** Use elements-of-style:writing-clearly-and-concisely (if available) for documentation quality
- **Content:** Capture the design as discussed and validated in Phase 3, organized into the sections that emerged from the conversation
- Commit the design document to git before proceeding

### Phase 5: Worktree Setup (for implementation)
When design is approved and implementation will follow:
- Announce: "I'm using the using-git-worktrees skill to set up an isolated workspace."
- **REQUIRED SUB-SKILL:** Use superpowers:using-git-worktrees
- Follow that skill's process for directory selection, safety verification, and setup
- Return here when worktree ready

### Phase 6: Planning Handoff
Ask: "Ready to create the implementation plan?"

When your human partner confirms (any affirmative response):
- Announce: "I'm using the writing-plans skill to create the implementation plan."
- **REQUIRED SUB-SKILL:** Use writing-plans
- Create detailed plan in the worktree

## Question Patterns

### When to Use AskUserQuestion Tool

**Use AskUserQuestion for:**
- Phase 1: Clarifying questions with 2-4 clear options
- Phase 2: Architectural approach selection (2-3 alternatives)
- Any decision with distinct, mutually exclusive choices
- When options have clear trade-offs to explain

**Benefits:**
- Structured presentation of options with descriptions
- Clear trade-off visibility for partner
- Forces explicit choice (prevents vague "maybe both" responses)

### When to Use Open-Ended Questions

**Use open-ended questions for:**
- Phase 3: Design validation ("Does this look right so far?")
- When you need detailed feedback or explanation
- When partner should describe their own requirements
- When structured options would limit creative input

**Example decision flow:**
- "What authentication method?" → Use AskUserQuestion (2-4 options)
- "Does this design handle your use case?" → Open-ended (validation)

## When to Revisit Earlier Phases

```dot
digraph revisit_phases {
    rankdir=LR;
    "New constraint revealed?" [shape=diamond];
    "Partner questions approach?" [shape=diamond];
    "Requirements unclear?" [shape=diamond];
    "Return to Phase 1" [shape=box, style=filled, fillcolor="#ffcccc"];
    "Return to Phase 2" [shape=box, style=filled, fillcolor="#ffffcc"];
    "Continue forward" [shape=box, style=filled, fillcolor="#ccffcc"];

    "New constraint revealed?" -> "Return to Phase 1" [label="yes"];
    "New constraint revealed?" -> "Partner questions approach?" [label="no"];
    "Partner questions approach?" -> "Return to Phase 2" [label="yes"];
    "Partner questions approach?" -> "Requirements unclear?" [label="no"];
    "Requirements unclear?" -> "Return to Phase 1" [label="yes"];
    "Requirements unclear?" -> "Continue forward" [label="no"];
}
```

**You can and should go backward when:**
- Partner reveals new constraint during Phase 2 or 3 → Return to Phase 1
- Validation shows fundamental gap in requirements → Return to Phase 1
- Partner questions approach during Phase 3 → Return to Phase 2
- Something doesn't make sense → Go back and clarify

**Don't force forward linearly** when going backward would give better results.

## Key Principles

| Principle | Application |
|-----------|-------------|
| **One question at a time** | Phase 1: Single question per message, use AskUserQuestion for choices |
| **Structured choices** | Use AskUserQuestion tool for 2-4 options with trade-offs |
| **YAGNI ruthlessly** | Remove unnecessary features from all designs |
| **Explore alternatives** | Always propose 2-3 approaches before settling |
| **Incremental validation** | Present design in sections, validate each |
| **Flexible progression** | Go backward when needed - flexibility > rigidity |
| **Announce usage** | State skill usage at start of session |
