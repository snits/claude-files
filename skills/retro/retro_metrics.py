#!/usr/bin/env python3
"""Per-retro pattern metrics: hits and eligible sessions per deterministic pattern.

Spec: ~/claudes-home/docs/superpowers/specs/2026-09-07-retro-pattern-metrics-design.md
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import mine_transcripts as mt

REGISTRY_PATH = Path(__file__).parent / "patterns.toml"
ELIGIBILITY = ("isolated", "ran_bash", "any")
KATA_WORKSPACE = Path.home() / "claudes-home"


@dataclass(frozen=True)
class Remedy:
    ref: str
    landed: dt.date | None = None


@dataclass
class Pattern:
    name: str
    detector: re.Pattern
    eligible: str
    remedies: list[Remedy] = field(default_factory=list)


def _parse_date(value) -> dt.date | None:
    if value is None:
        return None
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value))


def load_registry(path: Path = REGISTRY_PATH) -> list[Pattern]:
    """Parse patterns.toml, rejecting anything the counter could not act on."""
    data = tomllib.loads(path.read_text())
    patterns: list[Pattern] = []
    seen: set[str] = set()
    for raw in data.get("pattern", []):
        name = raw["name"]
        if name in seen:
            raise ValueError(f"duplicate pattern name: {name}")
        seen.add(name)
        eligible = raw["eligible"]
        if eligible not in ELIGIBILITY:
            raise ValueError(f"{name}: eligible must be one of {ELIGIBILITY}, got {eligible!r}")
        remedies = []
        for entry in raw.get("remedies", []):
            if "ref" not in entry:
                raise ValueError(f"{name}: every remedy needs a ref")
            remedies.append(Remedy(ref=entry["ref"], landed=_parse_date(entry.get("landed"))))
        patterns.append(
            Pattern(name=name, detector=re.compile(raw["detector"]), eligible=eligible, remedies=remedies)
        )
    return patterns


def registry_hash(path: Path = REGISTRY_PATH) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


WORKTREE_CWD = re.compile(r"/\.?worktrees/")


@dataclass
class SessionMetrics:
    """What one session (top-level transcript plus its subagents) contributes to a row."""

    path: Path
    version: str = "unknown"
    interactive: bool = False
    isolated: bool = False
    ran_bash: bool = False
    errors: list[str] = field(default_factory=list)

    def eligible_for(self, test: str) -> bool:
        return {"isolated": self.isolated, "ran_bash": self.ran_bash, "any": True}[test]


def subagent_files(path: Path) -> list[Path]:
    """In-process subagent transcripts belonging to this session, sorted."""
    return sorted((path.parent / path.stem / "subagents").glob("*.jsonl"))


def _scan_lines(path: Path, facts: SessionMetrics, *, top_level: bool) -> None:
    with path.open("r", errors="replace") as handle:
        for raw in handle:
            raw = raw.strip()
            if not raw:
                continue
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if not isinstance(entry, dict):
                continue

            if top_level and facts.version == "unknown" and entry.get("version"):
                facts.version = str(entry["version"])
            cwd = entry.get("cwd")
            if isinstance(cwd, str) and WORKTREE_CWD.search(cwd):
                facts.isolated = True

            kind = entry.get("type")
            message = entry.get("message", {}) if isinstance(entry.get("message"), dict) else {}
            content = message.get("content")

            if kind == "attachment":
                snapshot = entry.get("attachment", {}).get("snapshot", {})
                if isinstance(snapshot, dict) and snapshot.get("isWorktree") is True:
                    facts.isolated = True
            elif kind == "assistant" and isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict) or block.get("type") != "tool_use":
                        continue
                    name = block.get("name")
                    if name == "Bash":
                        facts.ran_bash = True
                    elif name == "EnterWorktree":
                        facts.isolated = True
                    elif name == "Agent" and block.get("input", {}).get("isolation") == "worktree":
                        facts.isolated = True
            elif kind == "user" and not entry.get("isMeta"):
                error = mt._tool_error_of(content)
                if error is not None:
                    facts.errors.append(error)
                    continue
                if top_level:
                    text = mt._text_of(content).strip()
                    if text and not any(marker in text for marker in mt.HARNESS_MARKERS):
                        facts.interactive = True


def scan_metrics_session(path: Path) -> SessionMetrics:
    facts = SessionMetrics(path=path)
    _scan_lines(path, facts, top_level=True)
    for sub in subagent_files(path):
        _scan_lines(sub, facts, top_level=False)
    return facts


def landed_date(ref: str, *, workspace: Path = KATA_WORKSPACE, run=subprocess.run) -> dt.date | None:
    """Close date of a kata issue, or None if it is open or the ref does not resolve."""
    result = run(
        ["kata", "show", ref, "--json", "--workspace", str(workspace)],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        issue = json.loads(result.stdout)["issue"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return None
    if not isinstance(issue, dict):
        return None
    closed_at = issue.get("closed_at") if issue.get("status") == "closed" else None
    if not isinstance(closed_at, str) or not closed_at:
        return None
    try:
        return dt.datetime.fromisoformat(closed_at.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _remedy_record(remedy: Remedy, landed: Callable[[str], dt.date | None]) -> dict:
    from_kata = landed(remedy.ref)
    if from_kata is not None:
        return {"ref": remedy.ref, "landed": from_kata.isoformat(), "source": "kata"}
    if remedy.landed is not None:
        return {"ref": remedy.ref, "landed": remedy.landed.isoformat(), "source": "registry"}
    return {"ref": remedy.ref, "landed": None, "source": "none"}


def build_row(
    sessions: list[SessionMetrics],
    patterns: list[Pattern],
    *,
    window_start: str,
    window_end: str,
    computed_at: str,
    registry_sha256: str,
    landed: Callable[[str], dt.date | None],
) -> dict:
    """One metrics row. Only interactive sessions count; hits count only in eligible ones."""
    interactive = [s for s in sessions if s.interactive]
    out: dict = {}
    for pattern in patterns:
        versions: dict[str, dict[str, int]] = {}
        for session in interactive:
            if not session.eligible_for(pattern.eligible):
                continue
            bucket = versions.setdefault(session.version, {"hits": 0, "eligible": 0})
            bucket["eligible"] += 1
            bucket["hits"] += sum(1 for text in session.errors if pattern.detector.search(text))
        out[pattern.name] = {
            "versions": versions,
            "remedies": [_remedy_record(r, landed) for r in pattern.remedies],
        }
    return {
        "window_start": window_start,
        "window_end": window_end,
        "computed_at": computed_at,
        "registry_sha256": registry_sha256,
        "stale_registry": False,
        "sessions_interactive": len(interactive),
        "patterns": out,
    }
