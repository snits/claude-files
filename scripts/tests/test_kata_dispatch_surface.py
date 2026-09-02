import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
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


def test_overlaps():
    a, b, c = frozenset({"x.py"}), frozenset({"x.py", "y.py"}), frozenset({"z.py"})
    assert surface.overlaps(a, b) and not surface.overlaps(a, c)
    assert surface.overlaps(surface.WILDCARD, c) and surface.overlaps(c, surface.WILDCARD)
    assert not surface.overlaps(frozenset(), c)
