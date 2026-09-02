"""Pure selection: the next dispatchable issue whose surface is disjoint from every running one.

Narrow surfaces are considered before WILDCARD ones, original order preserved within each
group. A WILDCARD overlaps everything, so it is only ever pickable with no agent running --
taking it while slots are free would idle the whole pool behind one issue that could have
waited. Deferring it costs the WILDCARD queue time and nothing else.
"""
from dataclasses import dataclass

from .surface import WILDCARD, overlaps

SKIP_LABELS = ("needsinfo", "needs-decision", "deferred", "needs-review")


@dataclass(frozen=True)
class Candidate:
    ref: str
    title: str
    priority: int | None
    owner: str | None
    labels: frozenset
    surface: frozenset
    is_epic: bool


def candidates_from_ready(ready_issues, surface_fn, epic_fn) -> list[Candidate]:
    out = []
    for i in ready_issues:
        raw = i.get("labels") or []
        labels = frozenset(l["label"] if isinstance(l, dict) else l for l in raw)
        out.append(Candidate(ref=i["short_id"], title=i.get("title", ""), priority=i.get("priority"),
                             owner=i.get("owner"), labels=labels,
                             surface=surface_fn(i.get("title", ""), i.get("body", "")),
                             is_epic=epic_fn(i["short_id"])))
    return out


def pick(candidates, running_surfaces, exclude):
    skipped = []
    # One stable sort, not two passes: two passes would re-append every narrow candidate's
    # skip reason whenever the first pass found no pick.
    for c in sorted(candidates, key=lambda c: c.surface == WILDCARD):
        if c.ref in exclude:
            skipped.append((c.ref, "excluded")); continue
        if c.owner:
            skipped.append((c.ref, "owned")); continue
        hit = next((l for l in SKIP_LABELS if l in c.labels), None)
        if hit:
            skipped.append((c.ref, f"label:{hit}")); continue
        if c.is_epic:
            skipped.append((c.ref, "epic")); continue
        if any(overlaps(c.surface, r) for r in running_surfaces):
            skipped.append((c.ref, "overlap")); continue
        return c, skipped
    return None, skipped
