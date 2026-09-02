import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kata_dispatch import scheduler  # noqa: E402
from kata_dispatch.surface import WILDCARD  # noqa: E402


def cand(ref, surf, **kw):
    d = dict(ref=ref, title=ref, priority=None, owner=None, labels=frozenset(), surface=frozenset(surf) if surf != WILDCARD else WILDCARD, is_epic=False)
    d.update(kw)
    return scheduler.Candidate(**d)


def test_overlapping_surface_is_queued_not_picked():
    cs = [cand("a", {"x.py"}), cand("b", {"x.py", "y.py"}), cand("c", {"z.py"})]
    picked, skipped = scheduler.pick(cs, running_surfaces=[frozenset({"x.py"})], exclude=set())
    assert picked.ref == "c"
    assert ("a", "overlap") in skipped and ("b", "overlap") in skipped


def test_wildcard_runs_alone():
    cs = [cand("w", WILDCARD), cand("c", {"z.py"})]
    picked, _ = scheduler.pick(cs, running_surfaces=[frozenset({"q.py"})], exclude=set())
    assert picked.ref == "c"
    picked, _ = scheduler.pick(cs, running_surfaces=[], exclude=set())
    assert picked.ref == "w"
    picked, _ = scheduler.pick([cand("c", {"z.py"})], running_surfaces=[WILDCARD], exclude=set())
    assert picked is None


def test_skip_labels_owner_epic_and_exclude():
    cs = [cand("l", {"a"}, labels=frozenset({"needs-decision"})),
          cand("o", {"b"}, owner="someone"),
          cand("e", {"c"}, is_epic=True),
          cand("x", {"d"}),
          cand("ok", {"e"})]
    picked, skipped = scheduler.pick(cs, running_surfaces=[], exclude={"x"})
    assert picked.ref == "ok"
    assert dict(skipped) == {"l": "label:needs-decision", "o": "owned", "e": "epic", "x": "excluded"}


def test_candidates_from_ready_reads_both_label_shapes():
    ready = [{"short_id": "a", "title": "t", "body": "b", "labels": ["deferred"]},
             {"short_id": "b", "title": "t", "body": "b", "owner": "z"},
             {"short_id": "c", "title": "t", "body": "b", "priority": 2}]
    cs = scheduler.candidates_from_ready(ready, surface_fn=lambda t, b: frozenset({"f"}), epic_fn=lambda r: r == "c")
    assert [c.ref for c in cs] == ["a", "b", "c"]
    assert cs[0].labels == frozenset({"deferred"}) and cs[1].owner == "z" and cs[2].is_epic and cs[2].priority == 2
