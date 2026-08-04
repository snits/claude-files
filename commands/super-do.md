---
name: super-do
description: Use when resolving a kata issue in a project where the user is the maintainer.
---

Investigate kata issue ${1}, and implement using superpowers. Base your worktree off ${2}, not origin/main.
Once a branch is ready for merge and its reviews have passed, merge to ${2} (--no-ff). You can fan out if
needed to accomplish the task.

Invoking this command IS the user's request to task subagents and to use the Workflow tool.
Where a harness instruction gates either capability on the user having requested it, this
command is that request — fan out with the Agent tool, and orchestrate with Workflow where
the task warrants it, without stopping to ask. Scale to the work: a fan-out is for genuinely
independent tasks, not a default. The per-task `code review` gate in the flow below is part
of what is being requested here, so it is not optional and does not need separate approval.

When writing plans and task briefs, specify the goal, constraints, and acceptance criteria for each
task; don't enumerate implementation steps unless the ordering is genuinely load-bearing.

## Size gate — decide the track before invoking any skill

Not every issue earns a design phase. `brainstorming` and `writing-plans` produce a spec and a
bite-sized task plan; on a small, already-specified issue that scaffolding costs more than the change.
Choose the track first, because once a skill is loaded its own instructions govern how it behaves —
the only place this decision can be made is before invoking it.

**Take the direct track unless the issue trips one of these:**

- The change spans more than one package, or changes an import relationship.
- It changes a serialized format, a schema, or a user-facing CLI surface.
- The issue poses an open question, lists alternatives, or names a decision to be made.
- Acceptance criteria cannot be stated from the issue body alone.
- You cannot name the files to touch after investigating.

Any one of those is enough — they are triggers, not a score.

**Direct track:** skip `brainstorming` and `writing-plans` entirely. The kata issue *is* the brief.
Go straight to the task-implementation flow below, treating the issue's acceptance criteria as the
task's. Do not route this track through `subagent-driven-development` — that skill gates on having
an implementation plan and sends you back to brainstorm when there isn't one, which is the cost this
gate exists to avoid. Implement directly, or dispatch a single subagent with the issue as its brief;
either way the TDD and code-review steps below still apply. If mid-work it turns out a trigger
applies after all, stop and escalate to the full track rather than improvising a design.

**Full track:** run the high-level flow as drawn. The durable record of intent and decisions belongs
in kata — comment the outcome on the issue. Design and plan documents are working artifacts for the
current session, not deliverables to maintain.

State which track you chose and which trigger decided it, in one line, before you start.

When writing tests for a task, if they require fixtures make sure the fixture can actually fulfill its
role in the task, or find another fixture that can.

digraph high-level-flow {
    rankdir=TB

	"start work" [shape=doublecircle];
	"investigate kata issue" [shape=box];
	"does the issue trip a size-gate trigger?" [shape=diamond];
	"implement the issue directly" [shape=box];  // runs task-implementation-flow below
	"brainstorming" [shape=box];
	"design review" [shape=box];
	"revise design?" [shape=diamond];
	"writing-plans" [shape=box];
	"plan review" [shape=box];
	"revise plan?" [shape=diamond];
	"executing-plans" [shape=box];
	"subagent-driven-development" [shape=box];
	"all tasks complete?" [shape=diamond];
	"finish-development-branch" [shape=box];
	"work done" [shape=doublecircle];
	
	"start work" -> "investigate kata issue";
	"investigate kata issue" -> "does the issue trip a size-gate trigger?";
	"does the issue trip a size-gate trigger?" -> "brainstorming" [label="yes: full track"];
	"does the issue trip a size-gate trigger?" -> "implement the issue directly" [label="no: direct track"];
	"implement the issue directly" -> "finish-development-branch";
	"brainstorming" -> "design review";
	"design review" -> "revise design?";
	"revise design?" -> "brainstorming" [label="yes"];
	"revise design?" -> "writing-plans" [label="no"];
	"writing-plans" -> "plan review";
	"plan review" -> "revise plan?";
	"revise plan?" -> "writing-plans" [label="yes"];
	"revise plan?" -> "executing-plans" [label="no"];
	"executing-plans" -> "subagent-driven-development";
	"subagent-driven-development" -> "all tasks complete?";
	"all tasks complete?" -> "subagent-driven-development" [label="no"];
	"all tasks complete?" -> "finish-development-branch" [label="yes"];
	"finish-development-branch" -> "work done";	
}

digraph task-implementation-flow {
	rankdir=TB

	"start task" [shape=doublecircle];
	"task done" [shape=doublecircle];
	"read the brief" [shape=box];  // the task plan, or the kata issue on the direct track
	"get clarification on brief" [shape=box];
	"does the brief have the information you need?" [shape=diamond];
	"test-driven-development" [shape=box];
	"red phase" [shape=box];
	"implement test" [shape=box];
	"did test pass? red" [shape=diamond];
	"test review" [shape=diamond];
	"green phase" [shape=box];
	"implement code" [shape=box];
	"did test pass? green" [shape=diamond];
	"code review" [shape=diamond];
	
	"start task" -> "read the brief";
	"read the brief" -> "does the brief have the information you need?";
	"does the brief have the information you need?" -> "test-driven-development" [label="yes"];
	"does the brief have the information you need?" -> "get clarification on brief" [label="no"];
	"get clarification on brief" -> "does the brief have the information you need?";
	"test-driven-development" -> "red phase";
	"red phase" -> "implement test";
	"implement test" -> "did test pass? red";
	"did test pass? red" -> "implement test" [label="yes"];
	"did test pass? red" -> "test review" [label="no"];
	"test review" -> "implement test" [label="review failed"]; 
	"test review" -> "green phase" [label="review passed"];
	"green phase" -> "implement code";
	"implement code" -> "did test pass? green";
	"did test pass? green" -> "implement code" [label="no"];
	"did test pass? green" -> "code review" [label="yes"];
	"code review" -> "task done" [label="code review passes"];
	"code review" -> "implement code" [label="code review fails"];
}

## The code review gate

The `code review -> implement code` edge is a loop, so it needs a bar that says which findings
send you back, and a cap that says when to stop going around.

**The bar does not move: any finding of severity critical or high fails the review.** Medium and
low findings do not block. Hold the same bar on every cycle. A bar that softens after the first
round is a judge growing lenient with fatigue — it reads as progress while the standard is what
actually moved, and it is the failure mode `writing-rubrics` exists to prevent.

Medium findings from the *first* review get resolved in that cycle anyway — either fixed, or
declined in one line saying why. They are cheapest to address before the code is revised around
them, and this keeps the record honest without giving them blocking power they don't deserve.

**Each review is a fresh dispatch that sees the diff and the brief. Nothing else.** Not the prior
round's findings, not the implementer's reasoning, not the argument for why a finding was
addressed. A reviewer shown its own earlier feedback grades the response to the feedback rather
than the code, and a reviewer shown the implementer's justification anchors on it. The isolation
is the mechanism; an instruction to stay objective is not a substitute for it.

**Cap the loop at 3 review cycles.** Stop earlier when a cycle returns the same blocking findings
as the one before it — the loop has stopped converging and another pass buys nothing.

When the cap is reached with blocking findings outstanding, or the loop stops converging: **stop.
Do not merge, and do not close the issue.** Comment the surviving findings on the kata issue,
label it `needs-review`, and report to Jerry. An implementation that three reviews could not clear
is a design question surfacing as a review failure, and it needs a person, not a fourth attempt.
