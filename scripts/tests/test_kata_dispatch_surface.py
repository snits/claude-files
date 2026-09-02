import os
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))
from test_kata_dispatch_fakes import make_repo  # noqa: E402

from kata_dispatch import surface  # noqa: E402


def test_explicit_paths_that_exist(tmp_path):
    repo = make_repo(tmp_path)
    s = surface.predict(repo, "fix app", "The bug is in src/app.py and README.md; docs/nope.md does not exist")
    assert s == frozenset({"src/app.py", "README.md"})


def test_directory_expands_to_tracked_files(tmp_path):
    repo = make_repo(tmp_path)
    s = surface.predict(repo, "refactor src/", "everything under src/ moves")
    assert s == frozenset({"src/app.py", "src/util.py"})


def test_backticked_identifier_is_grepped(tmp_path):
    repo = make_repo(tmp_path)
    s = surface.predict(repo, "rename helper", "`helper` returns the wrong thing")
    assert s == frozenset({"src/util.py"})


def test_empty_evidence_is_wildcard(tmp_path):
    repo = make_repo(tmp_path)
    assert surface.predict(repo, "Decide the size gate", "two defensible options") == surface.WILDCARD


def test_too_many_files_is_wildcard(tmp_path):
    repo = make_repo(tmp_path)
    for i in range(45):
        (repo / "src" / f"m{i}.py").write_text("x = 1\n")
    subprocess.run(["git", "add", "src"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "many"], cwd=repo, check=True)
    assert surface.predict(repo, "touch src/", "all of src/") == surface.WILDCARD


def test_predict_never_reads_stdin(tmp_path):
    """rg with no path argument searches stdin. Run predict in a child whose stdin is a pipe
    nobody ever writes to or closes: with the bug, rg blocks forever and this times out. The
    body must be grep-bait (a backticked identifier, no path token) or _grep_files is never
    reached and the test would pass either way."""
    code = (
        f"import sys; sys.path.insert(0, {str(SCRIPTS_DIR)!r})\n"
        "from kata_dispatch import surface\n"
        f"print(sorted(surface.predict({str(tmp_path / 'proj')!r}, 'rename it', '`helper` returns the wrong thing')))\n"
    )
    make_repo(tmp_path)
    r, w = os.pipe()
    try:
        p = subprocess.run([sys.executable, "-c", code], stdin=r, capture_output=True, text=True, timeout=20)
    finally:
        os.close(r)
        os.close(w)
    assert p.returncode == 0, p.stderr
    assert "src/util.py" in p.stdout, p.stdout


def test_overlaps():
    a, b, c = frozenset({"x.py"}), frozenset({"x.py", "y.py"}), frozenset({"z.py"})
    assert surface.overlaps(a, b) and not surface.overlaps(a, c)
    assert surface.overlaps(surface.WILDCARD, c) and surface.overlaps(c, surface.WILDCARD)
    assert not surface.overlaps(frozenset(), c)
