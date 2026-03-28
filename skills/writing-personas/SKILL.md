---
name: writing-personas
description: Use when creating, editing, or tuning agent persona/role prompts — especially when personas show overconfidence, attention narrowing, skipped tool use, or domain tunnel vision
---

# Writing Personas

## Overview

**Writing personas IS Test-Driven Development applied to role prompts.**

Persona prompts shape agent behavior across many dimensions simultaneously. The goal is preserving personality and domain voice while eliminating bias and blindness. You calibrate by testing for known failure modes, modifying the prompt, and verifying the personality survived the fix.

**REQUIRED BACKGROUND:** You MUST understand superpowers:writing-skills and superpowers:test-driven-development. This skill adapts their TDD methodology to persona prompt authoring.

## When to Use

- Creating a new agent persona/role prompt
- An existing persona shows overconfidence, narrowed attention, or skipped tool use
- Tuning a persona that works well on some tasks but fails on others
- Evaluating whether a persona adds value over a general-purpose agent with a role line in the task prompt

**When NOT to use:**
- Writing task prompts (no persistent identity needed)
- Skill documentation (use superpowers:writing-skills)
- One-shot agent dispatches where persona isn't reused

## The Two-Axis Problem

Unlike skills (which add constraints), personas must be evaluated on **two axes simultaneously**:

1. **Calibration axis** — failure modes should disappear after changes
2. **Preservation axis** — personality and domain voice should survive changes

A persona that passes all calibration tests but loses its distinctive voice is just a general-purpose agent with extra steps. A persona with great voice that can't use tools is a liability. Both axes must pass.

## Known Failure Modes

Documented from experimental testing (Fall 2025):

| Failure Mode | Symptom | Root Cause |
|-------------|---------|------------|
| **Overconfidence** | Doesn't use tools when it should | Persona identity implies expertise, model skips verification |
| **Attention narrowing** | Misses things outside domain | Prompt focuses attention, model ignores peripheral signals |
| **Domain tunnel vision** | Claims everything relates to their specialty | Identity-protective reasoning — persona defends relevance |
| **Skipped tool use** | "I know this" instead of looking it up | Overconfidence variant — expertise identity discourages searching |
| **Peer steamrolling** | Dominates team discussions, dismisses other perspectives | Strong persona voice overrides collaborative behavior |
| **First-mover anchoring** | Whoever writes first controls the group output | Confident persona voice sets frame others defer to |

## Calibration Test Types

### For Any Persona

**Tool use test:** Ask a domain question where the answer has changed recently or requires verification. Does the persona look it up or just "know" it?

**Cross-domain test:** Give a task requiring expertise outside their domain. Do they acknowledge limits or bull through?

**Bias test:** Present two approaches where the weaker one aligns with the persona's identity. Do they pick it anyway?

**Collaboration test:** Give a task where another specialist would clearly be better. Do they defer or claim it?

### For Team Personas

**Peer dynamics test:** Put 3-4 personas in a team meeting. Observe: Who steamrolls? Who defers? Who refuses to acknowledge others' expertise?

**First-mover test:** Run the same team task twice with different agents creating the initial shared document. Does the final output change based on who wrote first?

## Persona Prompt Structure

A well-calibrated persona prompt has three layers:

```
1. IDENTITY — Who they are, how they think, their voice
   (This is what you're preserving)

2. DOMAIN — What they know, their expertise, their approach
   (This is what adds value over general-purpose)

3. CALIBRATION GUARDS — Explicit counters to known failure modes
   (This is what you're adding/tuning)
```

### Calibration Guards

Add these only when calibration testing reveals the specific failure. Don't preemptively guard against everything — that's how you kill the personality.

**Anti-overconfidence (add when tool-use test fails):**
```
When uncertain or when information may have changed, use available
tools to verify rather than relying on domain knowledge alone.
```

**Anti-tunnel-vision (add when cross-domain test fails):**
```
Not every problem is a [domain] problem. When a task falls outside
your expertise, say so and recommend who would be better suited.
```

**Anti-steamrolling (add when peer dynamics test fails):**
```
In team settings, listen before asserting. Your domain expertise
is one perspective, not the only perspective.
```

Keep guards minimal and specific. Each one dilutes the persona voice slightly, so only add what calibration testing proves is needed.

## RED-GREEN-REFACTOR for Personas

### RED: Calibration Baseline

Run calibration tests with the persona as-is. Document:
- Which tests fail and how
- Exact rationalizations the persona uses
- Whether the personality/voice is present and distinctive

If no calibration tests fail, the persona may not need modification. If the personality isn't distinctive, consider whether a persona is warranted at all.

### GREEN: Targeted Modification

For each documented failure:
1. Add the minimal calibration guard that addresses it
2. Rerun the specific failing calibration test
3. Verify it passes

Then immediately run a preservation test:
- Give a task the persona previously handled well with good voice
- Verify the personality and domain expertise are still present

### REFACTOR: Iterate

- New failure mode appeared? Add targeted guard, re-test both axes
- Personality degraded? Guard was too broad — narrow it or rephrase
- General-purpose agent matches performance? The persona may not be adding value — consider retiring it

## The Value Test

After calibration, run the persona and a general-purpose agent (with a one-line role in the task prompt) on the same task. Compare:

- Does the persona produce meaningfully different output?
- Is the persona's output better for its intended use case?
- Does the persona's voice add value (engagement, clarity, perspective)?

If general-purpose matches or beats the persona, the persona prompt is overhead. A one-line role in the task prompt may be sufficient.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Adding all guards preemptively | Only add guards that address documented failures |
| Testing personality and calibration separately | Always test both axes after every change |
| Over-guarding until persona is bland | Keep guards minimal and specific |
| Assuming persona adds value without testing | Run the value test against general-purpose |
| Testing only on tasks that suit the persona | Include cross-domain and collaboration scenarios |

## The Iron Law

```
NO PERSONA CHANGE WITHOUT A FAILING CALIBRATION TEST FIRST
```

If you can't demonstrate the failure mode, you don't know what you're fixing. And if you can't verify the personality survived, you may have killed what made the persona useful.
