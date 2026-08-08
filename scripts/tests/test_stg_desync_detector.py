import json
import subprocess
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent.parent / "stg_desync_detector.py"


def run_hook(command: str, cwd: Path):
    payload = json.dumps(
        {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(cwd)}
    )
    return subprocess.run(
        ["python3", str(HOOK)], input=payload, capture_output=True, text=True
    )


@pytest.fixture
def stg_repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(r)], check=True)
    subprocess.run(
        ["git", "-C", str(r), "commit", "--allow-empty", "-m", "init"], check=True
    )
    subprocess.run(["stg", "-C", str(r), "init"], check=True)
    return r


def desync(repo: Path):
    """Simulate what a script/alias that evaded the PreToolUse guard would do."""
    (repo / "f.txt").write_text("x")
    subprocess.run(["git", "-C", str(repo), "add", "f.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "stray"], check=True)


def test_in_sync_silent(stg_repo):
    res = run_hook("ls", stg_repo)
    assert res.returncode == 0
    assert res.stderr == ""


def test_desync_warns(stg_repo):
    desync(stg_repo)
    res = run_hook("./sneaky_script.sh", stg_repo)
    assert res.returncode == 2
    assert "stg repair" in res.stderr


def test_non_stg_repo_silent(tmp_path):
    r = tmp_path / "plain"
    r.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(r)], check=True)
    subprocess.run(
        ["git", "-C", str(r), "commit", "--allow-empty", "-m", "init"], check=True
    )
    assert run_hook("git commit --allow-empty -m x", r).returncode == 0


def test_outside_repo_silent(tmp_path):
    assert run_hook("ls", tmp_path).returncode == 0


def test_repair_resolves(stg_repo):
    desync(stg_repo)
    subprocess.run(["stg", "-C", str(stg_repo), "repair"], check=True)
    assert run_hook("ls", stg_repo).returncode == 0
