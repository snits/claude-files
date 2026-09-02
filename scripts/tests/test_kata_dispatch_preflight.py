import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from test_kata_dispatch_fakes import make_repo  # noqa: E402

from kata_dispatch import preflight  # noqa: E402

PF = Path(__file__).resolve().parent.parent / "kata_dispatch" / "preflight.py"


def _wt(repo, tmp_path, ref="ab12"):
    wt = tmp_path / "proj-dispatch" / ref
    subprocess.run(["git", "worktree", "add", "-b", f"dispatch/{ref}", str(wt), "integration"], cwd=repo, check=True, capture_output=True)
    return wt


def test_main_checkout_is_refused(tmp_path):
    repo = make_repo(tmp_path)
    ok, why = preflight.check(repo)
    assert not ok and "main checkout" in why


def test_dispatch_worktree_is_allowed(tmp_path):
    repo = make_repo(tmp_path)
    wt = _wt(repo, tmp_path)
    assert preflight.check(wt) == (True, "ok")


def test_file_path_outside_worktree_is_refused(tmp_path):
    repo = make_repo(tmp_path)
    wt = _wt(repo, tmp_path)
    ok, why = preflight.check(wt, file_path=str(repo / "src" / "app.py"))
    assert not ok and "outside" in why
    ok, _ = preflight.check(wt, file_path=str(wt / "src" / "app.py"))
    assert ok


def test_wrong_branch_is_refused(tmp_path):
    repo = make_repo(tmp_path)
    wt = tmp_path / "other"
    subprocess.run(["git", "worktree", "add", "-b", "feature", str(wt), "integration"], cwd=repo, check=True, capture_output=True)
    ok, why = preflight.check(wt)
    assert not ok and "dispatch/" in why


def test_hook_mode_exit_codes(tmp_path):
    repo = make_repo(tmp_path)
    wt = _wt(repo, tmp_path)
    payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(repo / "README.md")}, "cwd": str(wt)})
    p = subprocess.run([sys.executable, str(PF), "--hook"], input=payload, capture_output=True, text=True, cwd=wt)
    assert p.returncode == 2 and "kata-dispatch preflight" in p.stderr
    payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(wt / "README.md")}, "cwd": str(wt)})
    p = subprocess.run([sys.executable, str(PF), "--hook"], input=payload, capture_output=True, text=True, cwd=wt)
    assert p.returncode == 0


def test_cli_mode(tmp_path):
    repo = make_repo(tmp_path)
    p = subprocess.run([sys.executable, str(PF)], capture_output=True, text=True, cwd=repo)
    assert p.returncode == 2


def test_shared_scratchpad_symlink_is_allowed(tmp_path):
    repo = make_repo(tmp_path)
    wt = _wt(repo, tmp_path)
    (repo / ".scratchpad").mkdir()
    (wt / ".scratchpad").symlink_to(repo / ".scratchpad", target_is_directory=True)
    ok, why = preflight.check(wt, file_path=str(wt / ".scratchpad" / "note.md"))
    assert (ok, why) == (True, "ok")


def test_symlink_escape_inside_worktree_is_refused(tmp_path):
    repo = make_repo(tmp_path)
    wt = _wt(repo, tmp_path)
    (wt / "evil").symlink_to(repo / "src", target_is_directory=True)
    ok, why = preflight.check(wt, file_path=str(wt / "evil" / "app.py"))
    assert not ok and "outside" in why


def test_relative_dotdot_escape_is_refused(tmp_path):
    repo = make_repo(tmp_path)
    wt = _wt(repo, tmp_path)
    ok, why = preflight.check(wt, file_path="../README.md")
    assert not ok and "outside" in why


def test_relative_dotdot_that_stays_inside_is_allowed(tmp_path):
    repo = make_repo(tmp_path)
    wt = _wt(repo, tmp_path)
    ok, why = preflight.check(wt, file_path=str(wt / "src" / ".." / "README.md"))
    assert (ok, why) == (True, "ok")


def test_hook_mode_malformed_payload_fails_closed(tmp_path):
    repo = make_repo(tmp_path)
    wt = _wt(repo, tmp_path)
    p = subprocess.run([sys.executable, str(PF), "--hook"], input="not json", capture_output=True, text=True, cwd=wt)
    assert p.returncode == 2 and "refusing" in p.stderr


def test_hook_mode_notebook_edit_uses_notebook_path(tmp_path):
    repo = make_repo(tmp_path)
    wt = _wt(repo, tmp_path)
    payload = json.dumps({"tool_name": "NotebookEdit", "tool_input": {"notebook_path": str(wt / "nb.ipynb")}, "cwd": str(wt)})
    p = subprocess.run([sys.executable, str(PF), "--hook"], input=payload, capture_output=True, text=True, cwd=wt)
    assert p.returncode == 0

    payload = json.dumps({"tool_name": "NotebookEdit", "tool_input": {"notebook_path": str(repo / "nb.ipynb")}, "cwd": str(wt)})
    p = subprocess.run([sys.executable, str(PF), "--hook"], input=payload, capture_output=True, text=True, cwd=wt)
    assert p.returncode == 2
