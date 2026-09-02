"""Two-layer atomic claim: O_EXCL lock file on this checkout, then kata's own claim, then a read-back.

The lock file stops same-machine racers before they reach the daemon and records the pid
for stale detection. kata's claim is the cross-session compare-and-swap (exit 5 on conflict).
The read-back closes the gap where a claim "succeeded" as a same-actor no-op on a stale owner.
"""
import json
import os
import socket
import time
from pathlib import Path

from .kata import KataClient
from .state import Paths, pid_alive


class ClaimError(RuntimeError):
    pass


def read_lock(paths: Paths, ref: str) -> dict | None:
    p = paths.lock(ref)
    try:
        return json.loads(p.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _write_lock(path: Path, actor: str):
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    with os.fdopen(fd, "w") as f:
        json.dump({"actor": actor, "pid": os.getpid(), "host": socket.gethostname(), "started": time.time()}, f)


def acquire(paths: Paths, ref: str, actor: str, kata: KataClient) -> bool:
    paths.locks.mkdir(parents=True, exist_ok=True)
    lock = paths.lock(ref)
    try:
        _write_lock(lock, actor)
    except FileExistsError:
        return False
    claimed = False
    try:
        if not kata.claim(ref, actor):
            lock.unlink(missing_ok=True)
            return False
        claimed = True
        # Guards against a claim that "succeeded" as a same-actor no-op on a stale
        # owner, or a daemon-side surprise. If the owner isn't us, there's nothing
        # of ours to undo.
        if kata.owner(ref) != actor:
            lock.unlink(missing_ok=True)
            return False
    except Exception:
        if claimed:
            # Best-effort rollback of the kata claim we just took. Call unassign
            # directly rather than through unassign_if_owner: that helper's own
            # owner() read-back is exactly what may be raising here, and we know
            # we're the owner since we just claimed as this actor one call ago.
            try:
                kata._run(["unassign", ref], actor=actor, check=False)
            except Exception:
                pass
        lock.unlink(missing_ok=True)
        raise
    return True


def release(paths: Paths, ref: str, actor: str, kata: KataClient):
    """Release the claim no matter what. Never raises: kata's own lookups can 404 (e.g. a
    deleted ref), so guarantee the lock file is gone even when the kata-side unassign raises."""
    try:
        kata.unassign_if_owner(ref, actor)
    except Exception:
        # unassign_if_owner's first act is owner() (a show read-back) -- that's exactly what
        # may be raising here, so the unassign itself never ran. Call unassign directly rather
        # than through the owner-guarded helper: we hold the claim under this exact actor, so
        # there's nothing to look up first.
        try:
            kata._run(["unassign", ref], actor=actor, check=False)
        except Exception:
            pass
    paths.lock(ref).unlink(missing_ok=True)


def stale_locks(paths: Paths) -> list[dict]:
    """Locks whose pid is dead on this host. A lock from another host is never judged stale here."""
    out = []
    if not paths.locks.exists():
        return out
    for p in sorted(paths.locks.glob("*.json")):
        d = read_lock(paths, p.stem)
        if d and d.get("host") == socket.gethostname() and not pid_alive(int(d.get("pid", 0))):
            out.append({"ref": p.stem, **d})
    return out
