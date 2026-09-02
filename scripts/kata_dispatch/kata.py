"""Subprocess client for the kata CLI, run with cwd=repo so project resolution is the repo's."""
import json
import subprocess
from pathlib import Path


class KataError(RuntimeError):
    pass


class KataClient:
    def __init__(self, repo: Path):
        self.repo = Path(repo)

    def _run(self, args, check=True, actor=None) -> subprocess.CompletedProcess:
        cmd = ["kata", *args]
        if actor:
            cmd += ["--as", actor]
        p = subprocess.run(cmd, cwd=str(self.repo), capture_output=True, text=True, stdin=subprocess.DEVNULL)
        if check and p.returncode != 0:
            raise KataError(f"kata {' '.join(args)} failed ({p.returncode}): {p.stderr.strip() or p.stdout.strip()}")
        return p

    def _json(self, args) -> dict:
        return json.loads(self._run(args).stdout)

    def ready(self) -> list[dict]:
        return self._json(["ready", "--json"]).get("issues", [])

    def show(self, ref: str) -> dict:
        return self._json(["show", "--json", ref])

    def owner(self, ref: str) -> str | None:
        return self.show(ref)["issue"].get("owner")

    def labels(self, ref: str) -> set[str]:
        raw = self.show(ref).get("labels") or []
        return {l["label"] if isinstance(l, dict) else l for l in raw}

    def is_epic(self, ref: str) -> bool:
        """An issue with an open child is an epic: the loop cannot close it."""
        for link in self.show(ref).get("links") or []:
            if link.get("type") == "parent" and link["to"]["short_id"] == ref and link["from"].get("status") == "open":
                return True
        return False

    def claim(self, ref: str, actor: str) -> bool:
        """True when this actor now owns the issue. Exit 5 (already claimed by another) -> False."""
        p = self._run(["claim", ref], check=False, actor=actor)
        if p.returncode == 0:
            return True
        if p.returncode == 5:
            return False
        raise KataError(f"kata claim {ref}: exit {p.returncode}: {p.stderr.strip()}")

    def unassign_if_owner(self, ref: str, actor: str) -> bool:
        """kata unassign succeeds for any actor (verified 2026-09-01), so guard on the owner."""
        if self.owner(ref) != actor:
            return False
        self._run(["unassign", ref], actor=actor)
        return True

    def comment(self, ref: str, actor: str, body: str):
        self._run(["comment", ref, "--body", body], actor=actor)

    def label_add(self, ref: str, actor: str, label: str):
        self._run(["label", "add", ref, label], actor=actor)

    def healthy(self) -> bool:
        return self._run(["health"], check=False).returncode == 0
