---
name: work-bead
description: Use when resolving a bead in a project where the user is the maintainer.
---

Investigate bead ${1}, and implement using superpowers. For any commits made, review the results
of the automated roborev reviews, and deal with any relevant findings. Once complete, and reviews
have passed merge to local main (--no-ff), and the push to origin.

digraph high-level-flow {
    rankdir=TB

	"start work" [shape=doublecircle];
	"investigate bead" [shape=box];
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
	
	"start work" -> "investigate bead";
	"investigate bead" -> "brainstorming";
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
	"read task plan" [shape=box];
	"get clarification on plan" [shape=box];
	"does the plan have the information you need?" [shape=diamond];
	"test-driven-development" [shape=box];
	"red phase" [shape=box];
	"implement test" [shape=box];
	"did test pass? red" [shape=diamond];
	"test review" [shape=diamond];
	"green phase" [shape=box];
	"implement code" [shape=box];
	"did test pass? green" [shape=diamond];
	"code review" [shape=diamond];
	"roborev review" [shape=diamond];
	
	"start task" -> "read task plan";
	"read task plan" -> "does the plan have the information you need?";
	"does the plan have the information you need?" -> "test-driven-development" [label="yes"];
	"does the plan have the information you need?" -> "get clarification on plan" [label="no"];
	"get clarification on plan" -> "does the plan have the information you need?";
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
	"code review" -> "roborev review" [label="code review passes"];
	"code review" -> "implement code" [label="code review fails"];
	"roborev review" -> "task done" [label="roborev review passes"];
	"roborev review" -> "implement code" [label="roborev review fails"];
}
