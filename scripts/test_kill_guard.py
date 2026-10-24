"""Tests for the name-based process-kill guard."""
import io
import json

import pytest

from kill_guard import main, verdict

BLOCKED = [
    "pkill foo",
    "pkill -f kata",
    "sudo pkill -9 node",
    "FOO=1 pkill foo",
    "env nohup /usr/bin/pkill foo",
    "killall node",
    "killall -9 claude",
    "make && pkill -f server",
    "kill $(pgrep foo)",
    "kill -9 $(pgrep -f foo)",
    "kill `pgrep foo`",
    "kill $(pidof foo)",
    'kill "$(pgrep foo)"',
    "kill -9 $(pgrep -f x | head -1)",
    "pgrep foo | xargs kill",
    "pgrep -f foo | xargs -r kill -9",
    "pidof foo | xargs -n1 kill",
    "pgrep -f foo | grep -v bar | xargs kill",
    "bash -c 'pkill -f foo'",
    "sh -c 'killall foo'",
    "bash -c 'kill $(pgrep foo)'",
    "bash -c 'pgrep foo | xargs kill'",
    "for p in a b; do pkill $p; done",
    "sudo -u root pkill foo",
    "nice -n 5 pkill foo",
    "timeout 5 pkill foo",
    "timeout -s KILL 5 killall foo",
    "timeout -k 2 5 pkill foo",
    "exec pkill foo",
    "env -u HOME pkill foo",
    "sudo -E nice -n 5 pkill foo",
]

ALLOWED = [
    "kill 12345",
    "kill -9 12345 12346",
    "kill %1",
    "kill -0 12345",
    "kill $PID",
    'kill "$pid"',
    "kill $(cat x.pid)",
    "kill -- -12345",
    "pgrep -a foo",
    "ps aux | grep foo",
    "ps -o pid,ppid,cmd | grep foo",
    "echo pkill",
    "echo killall foo",
    "grep pkill file",
    "pgrep foo | wc -l",
    "pgrep foo; kill 123",
    "pgrep foo && xargs echo kill",
    "pgrep foo | xargs echo kill",
    'git commit -m "remove pkill call"',
    "cat <<'EOF'\npkill -f foo\nEOF",
    "cat > f <<EOF\nkill $(pgrep x)\nEOF",
    "",
    "command -v pkill",
    "command -v killall >/dev/null && echo yes",
    "command -V pkill",
    "sudo -l pkill",
    "env -u pkill ls",
    "nice -n 5 ls pkill",
    "timeout 5 sleep 1",
]


@pytest.mark.parametrize("cmd", BLOCKED)
def test_blocks(cmd):
    text = verdict(cmd, "/tmp")
    assert text is not None and text.startswith("BLOCKED:")


@pytest.mark.parametrize("cmd", ALLOWED)
def test_allows(cmd):
    assert verdict(cmd, "/tmp") is None


def test_message_content():
    text = verdict("pkill foo", "/tmp")
    assert "by name" in text
    assert "ps -o pid,ppid,cmd" in text
    assert "kill <literal-pid>" in text
    assert "2026-10-10" in text


def run_main(payload):
    err = io.StringIO()
    rc = main(io.StringIO(payload), err)
    return rc, err.getvalue()


def test_main_blocks_with_exit_2():
    rc, err = run_main(json.dumps({"tool_input": {"command": "pkill -f kata"}, "cwd": "/tmp"}))
    assert rc == 2 and err.startswith("BLOCKED:")


def test_main_allows_plain_kill():
    assert run_main(json.dumps({"tool_input": {"command": "kill 12345"}, "cwd": "/tmp"})) == (0, "")


def test_main_fails_open_when_verdict_raises(monkeypatch):
    import kill_guard

    def boom(command, cwd):
        raise RuntimeError("internal bug")

    monkeypatch.setattr(kill_guard, "verdict", boom)
    assert run_main(json.dumps({"tool_input": {"command": "pkill x"}, "cwd": "/tmp"})) == (0, "")


@pytest.mark.parametrize("payload", ["not json", "{}", '{"tool_input":{"command":5}}', "[]"])
def test_main_fails_open(payload):
    assert run_main(payload)[0] == 0
