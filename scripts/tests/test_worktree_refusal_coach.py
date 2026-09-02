import json
import subprocess
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "worktree_refusal_coach.py"
WT = "/home/jsnitsel/dev/proj/.claude/worktrees/issue-abcd"
SHARED = "/home/jsnitsel/dev/proj"

# Verbatim Claude Code 2.1.259 refusal texts (captured 2026-09-02), with paths substituted.
TAIL = " Refusing to run it — a worktree-isolated session's git operations must target its own worktree."
V_COMPLEX = (f"This session is isolated in the worktree {WT}, but this command is too complex to verify "
             f"that it stays inside the worktree.{TAIL} Split it into plain, separate commands and run them from {WT}.")
V_C = (f"This session is isolated in the worktree {WT}, but this command redirects git to the shared checkout "
       f"via -C.{TAIL} Run the equivalent from {WT} without the redirect.")
V_CD = (f"This session is isolated in the worktree {WT}, but this command changes directory to the shared "
        f"checkout ({SHARED}) before running git.{TAIL} Run the equivalent from {WT} without the redirect.")
V_NAMES = (f"This agent is isolated in the worktree {WT}, but this command names git in a form too complex to "
           f"verify that it stays inside the worktree.{TAIL} Split it into plain, separate commands and run them from {WT}.")
V_EVAL = (f"This agent is isolated in the worktree {WT}, but this command runs a string through eval, which "
          f"can't be verified to stay inside the worktree.{TAIL}")
V_ENV = (f"This agent is isolated in the worktree {WT}, but this command runs python after PYTHONPATH is set "
         f"here to a value that configures what it loads or runs at startup inside a construct too complex to "
         f"verify, so what it runs cannot be shown not to be git.{TAIL}")
V_CWD = (f"This session is isolated in the worktree {WT}, but this command's working directory resolved to the "
         f"shared checkout ({SHARED}). Refusing to run it there — a worktree-isolated session's commands "
         f"must run inside its worktree.")


def run_hook(payload):
    data = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(["python3", str(HOOK)], input=data, capture_output=True, text=True)


def coach(command, error):
    r = run_hook({"hook_event_name": "PostToolUseFailure", "tool_name": "Bash",
                  "tool_input": {"command": command}, "error": error})
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip(), "expected coaching output"
    out = json.loads(r.stdout)
    assert out["hookSpecificOutput"]["hookEventName"] == "PostToolUseFailure"
    text = out["hookSpecificOutput"]["additionalContext"]
    assert text.endswith(f"Worktree: {WT}."), text
    return text


def test_cwd_trap_names_enterworktree():
    text = coach("grep -n VERDICT report.md", V_CWD)
    assert f"Call EnterWorktree {WT} again" in text


def test_git_dash_c_elsewhere():
    text = coach(f"git -C {SHARED} status --short", V_C)
    assert f"git -C {SHARED} targets the shared checkout" in text
    assert "Run git without -C" in text


def test_cd_elsewhere_before_git_by_error_text():
    text = coach(f"cd {SHARED}; git status --short", V_CD)
    assert "Do not cd out of the worktree before git" in text


def test_cd_elsewhere_before_git_by_command_shape():
    text = coach(f"cd {SHARED} && git log --oneline -1", V_COMPLEX)
    assert "Do not cd out of the worktree before git" in text


def test_git_substitution():
    text = coach('echo "tip: $(git rev-parse --short HEAD)"', V_NAMES)
    assert "$(git …) inside a string is refused" in text
    assert "own Bash call" in text


def test_backtick_git_substitution():
    text = coach("echo `git rev-parse HEAD`", V_NAMES)
    assert "$(git …) inside a string is refused" in text


def test_eval():
    text = coach('eval "git status --short"', V_EVAL)
    assert "eval is refused" in text


def test_env_prefix_substitution():
    text = coach("PYTHONPATH=$(pwd)/src python3 -m pytest -q 2>&1 | tail -3", V_ENV)
    assert "environment prefix is refused" in text


def test_fallback_lists_shapes():
    text = coach("n=$(grep -n x f | cut -d: -f1); sed -n \"${n}p\" f", V_COMPLEX)
    assert "Refused in an isolated worktree: git -C <other>" in text
    assert "Allowed: plain git" in text


def test_own_worktree_git_dash_c_is_not_called_elsewhere():
    # The guard allows this shape; if it ever reaches the hook it must fall through, not
    # accuse the model of targeting the shared checkout.
    text = coach(f"git -C {WT} status --short", V_COMPLEX)
    assert "targets the shared checkout" not in text


def test_own_worktree_cd_is_not_called_elsewhere():
    text = coach(f"cd {WT}; git status --short", V_COMPLEX)
    assert "Do not cd out of the worktree" not in text


def test_unrelated_bash_failure_is_silent():
    r = run_hook({"hook_event_name": "PostToolUseFailure", "tool_name": "Bash",
                  "tool_input": {"command": "ls /nope"}, "error": "ls: cannot access '/nope'"})
    assert r.returncode == 0 and r.stdout == ""


def test_malformed_stdin_is_silent():
    for payload in ("not json", "[]", json.dumps({"error": 5}), json.dumps({"error": V_C})):
        r = run_hook(payload)
        assert r.returncode == 0, payload
        assert r.stdout == "", payload
