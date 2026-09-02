#!/usr/bin/env python3
"""SubagentStart hook: the skills reminder plus the four brief-side rules retros traced to
subagent failures (report delivery, own-worktree merges, per-checkout paths, sleep-polling).

Ignores stdin. Prints one hookSpecificOutput JSON object. Never exits non-zero.
"""
import json
import sys

SKILLS = ("Skills: You have skills available via the Skill tool. Check the available-skills section "
          "in your system context and invoke any relevant skills before proceeding. For mathematical "
          "calculations or numerical claims, use the calculations-and-math skill.")

RULES = (
    "Report: put your full report inline in your final message. If it exceeds a screenful, send it "
    "one finding per message. A report written only to a file did not arrive.",
    "Worktree: if you were given a worktree, never merge it, rebase the target onto it, or remove it. "
    "The orchestrator lands it.",
    "Paths: .superpowers/ and .scratchpad/ are per-checkout. Cite artifacts by absolute path.",
    "Waiting: to wait for anything, use Monitor with an until-loop or run_in_background; "
    "a foreground sleep N && ... is blocked.",
)


def main() -> int:
    try:
        sys.stdin.read()
    except Exception:
        pass
    text = SKILLS + "\n" + "\n".join(RULES)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SubagentStart",
                                             "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
