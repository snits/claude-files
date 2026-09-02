"""Where dispatcher state lives and the per-agent record it keeps there."""
import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import gitops

TARGET = "integration"


def branch_for(ref: str) -> str:
    return f"dispatch/{ref}"


class Paths:
    def __init__(self, repo: Path):
        self.repo = Path(repo).resolve()
        common = Path(gitops.rev_parse(self.repo, "--git-common-dir"))
        self.git_common = (common if common.is_absolute() else self.repo / common).resolve()
        base = self.git_common / "kata-dispatch"
        self.locks = base / "locks"
        self.agents = base / "agents"
        self.dispatch_root = self.repo.parent / f"{self.repo.name}-dispatch"
        self.integration_worktree = self.dispatch_root / "integration"

    def worktree(self, ref: str) -> Path:
        return self.dispatch_root / ref

    def lock(self, ref: str) -> Path:
        return self.locks / f"{ref}.json"

    def agent(self, ref: str) -> Path:
        return self.agents / f"{ref}.json"

    def run_dir(self, run_id: str) -> Path:
        return self.repo / ".scratchpad" / "tmp" / "dispatch" / run_id

    def ensure(self):
        for d in (self.locks, self.agents, self.dispatch_root):
            d.mkdir(parents=True, exist_ok=True)


@dataclass
class AgentRecord:
    ref: str
    actor: str
    run_id: str
    branch: str
    worktree: str
    log: str
    pid: int = 0
    started: float = field(default_factory=time.time)
    finished: float = 0.0
    state: str = "running"          # running | landing | done | escalated | blocked | orphaned
    outcome: str = ""               # free text set by landing
    session_id: str = ""
    cost_usd: float = 0.0
    merge_commit: str = ""

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(self), indent=1))
        os.replace(tmp, path)

    @classmethod
    def load(cls, path: Path) -> "AgentRecord":
        return cls(**json.loads(path.read_text()))

    @classmethod
    def load_all(cls, paths: Paths) -> list["AgentRecord"]:
        if not paths.agents.exists():
            return []
        return [cls.load(p) for p in sorted(paths.agents.glob("*.json"))]


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True
