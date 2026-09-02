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
    try:
        if not kata.claim(ref, actor):
            lock.unlink(missing_ok=True)
            return False
        if kata.owner(ref) != actor:
            kata.unassign_if_owner(ref, actor)
            lock.unlink(missing_ok=True)
            return False
    except Exception:
        lock.unlink(missing_ok=True)
        raise
    return True


def release(paths: Paths, ref: str, actor: str, kata: KataClient):
    kata.unassign_if_owner(ref, actor)
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
