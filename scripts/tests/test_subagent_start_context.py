import json
import subprocess
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "subagent_start_context.py"

SKILLS_SENTENCE = ("Skills: You have skills available via the Skill tool. Check the available-skills "
                   "section in your system context and invoke any relevant skills before proceeding. "
                   "For mathematical calculations or numerical claims, use the calculations-and-math skill.")


def run_hook(stdin="{}"):
    return subprocess.run(["python3", str(HOOK)], input=stdin, capture_output=True, text=True)


def block():
    r = run_hook(json.dumps({"hook_event_name": "SubagentStart", "agent_id": "x", "agent_type": "general-purpose"}))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["hookSpecificOutput"]["hookEventName"] == "SubagentStart"
    return out["hookSpecificOutput"]["additionalContext"]


def test_keeps_skills_sentence_verbatim():
    assert block().startswith(SKILLS_SENTENCE)


def test_carries_the_four_rules():
    text = block()
    assert "Report: put your full report inline in your final message" in text
    assert "one finding per message" in text
    assert "Worktree: if you were given a worktree, never merge it" in text
    assert "The orchestrator lands it." in text
    assert "Paths: .superpowers/ and .scratchpad/ are per-checkout" in text
    assert "Cite artifacts by absolute path." in text
    assert "Waiting: to wait for anything, use Monitor with an until-loop or run_in_background" in text
    assert "a foreground sleep N && ... is blocked" in text


def test_ignores_stdin_content():
    assert run_hook("not json at all").returncode == 0
    assert run_hook("").returncode == 0
    assert json.loads(run_hook("").stdout)["hookSpecificOutput"]["hookEventName"] == "SubagentStart"
