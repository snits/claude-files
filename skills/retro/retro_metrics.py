#!/usr/bin/env python3
"""Per-retro pattern metrics: hits and eligible sessions per deterministic pattern.

Spec: ~/claudes-home/docs/superpowers/specs/2026-09-07-retro-pattern-metrics-design.md
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import mine_transcripts as mt

REGISTRY_PATH = Path(__file__).parent / "patterns.toml"
METRICS_PATH = Path.home() / ".claude" / "retro" / "metrics.jsonl"
ELIGIBILITY = ("isolated", "ran_bash", "any")
KATA_WORKSPACE = Path.home() / "claudes-home"
UTC = dt.timezone.utc


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


def _iso(moment: dt.datetime) -> str:
    return moment.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse_iso(text: str) -> dt.datetime:
    return dt.datetime.fromisoformat(text.replace("Z", "+00:00"))


def read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


def _sessions_between(start: dt.datetime, end: dt.datetime, projects_dir: Path) -> list[SessionMetrics]:
    out = []
    for path in mt.sessions_in_window(start.timestamp(), projects_dir):
        if path.stat().st_mtime > end.timestamp():
            continue
        out.append(scan_metrics_session(path))
    return out


def compute_row(*, window_start: dt.datetime, window_end: dt.datetime, projects_dir: Path,
                registry_path: Path, landed, computed_at: dt.datetime | None = None) -> dict:
    sessions = _sessions_between(window_start, window_end, projects_dir)
    return build_row(
        sessions, load_registry(registry_path),
        window_start=_iso(window_start), window_end=_iso(window_end),
        computed_at=_iso(computed_at or dt.datetime.now(UTC)),
        registry_sha256=registry_hash(registry_path), landed=landed,
    )


def append_row(*, metrics_path: Path, projects_dir: Path, registry_path: Path,
               since: dt.datetime | None, now: dt.datetime, landed) -> dict:
    rows = read_rows(metrics_path)
    if since is None:
        if not rows:
            raise ValueError("no previous row to tile from; pass --since for the first row")
        since = _parse_iso(rows[-1]["window_end"])
    row = compute_row(window_start=since, window_end=now, projects_dir=projects_dir,
                      registry_path=registry_path, landed=landed, computed_at=now)
    write_rows(metrics_path, rows + [row])
    return row


def rebuild_rows(*, metrics_path: Path, projects_dir: Path, registry_path: Path, landed) -> list[dict]:
    """Recompute every row under the current registry; keep and flag rows with no transcripts left."""
    rebuilt = []
    for old in read_rows(metrics_path):
        start, end = _parse_iso(old["window_start"]), _parse_iso(old["window_end"])
        if not _sessions_between(start, end, projects_dir):
            kept = dict(old)
            kept["stale_registry"] = kept["registry_sha256"] != registry_hash(registry_path)
            rebuilt.append(kept)
            continue
        rebuilt.append(compute_row(window_start=start, window_end=end, projects_dir=projects_dir,
                                   registry_path=registry_path, landed=landed))
    write_rows(metrics_path, rebuilt)
    return rebuilt


def _rate(hits: int, eligible: int) -> str:
    return f"{hits / eligible:.2f}" if eligible else "-"


def render_trend(rows: list[dict]) -> str:
    if not rows:
        return "(no metrics rows yet)\n"
    names: list[str] = []
    for name in rows[-1]["patterns"]:
        names.append(name)
    for row in rows:
        for name in row["patterns"]:
            if name not in names:
                names.append(name)
    out: list[str] = []
    for name in names:
        out.append(f"## {name}")
        out.append(f" {'window_end':<12} {'hits':>5}  {'eligible':>8}  {'rate':<6}")
        marked: set[str] = set()
        any_stale = False
        for row in rows:
            pat = row["patterns"].get(name)
            if pat is None:
                continue
            end = row["window_end"][:10]
            versions = pat["versions"]
            hits = sum(v["hits"] for v in versions.values())
            eligible = sum(v["eligible"] for v in versions.values())
            markers = []
            for remedy in pat.get("remedies", []):
                landed = remedy.get("landed")
                if landed and end > landed and remedy["ref"] not in marked:
                    marked.add(remedy["ref"])
                    markers.append(f"◄ {remedy['ref']} landed {landed}")
            prefix = "!" if row.get("stale_registry") else " "
            any_stale = any_stale or prefix == "!"
            line = f"{prefix}{end:<12} {hits:>5}  {eligible:>8}  {_rate(hits, eligible):<6}"
            if markers:
                line += " " + ", ".join(markers)
            out.append(line.rstrip())
            if len(versions) > 1:
                for version in sorted(versions):
                    v = versions[version]
                    out.append(f"   {version:<10} {v['hits']:>5}  {v['eligible']:>8}  {_rate(v['hits'], v['eligible']):<6}".rstrip())
        if any_stale:
            out.append("! = computed under an older registry; run --rebuild")
        out.append("")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--append", action="store_true", help="compute one row for the window and append it (default)")
    mode.add_argument("--rebuild", action="store_true", help="recompute every row under the current registry")
    mode.add_argument("--trend", action="store_true", help="print trend tables for the recap")
    parser.add_argument("--since", help="ISO date for the first row's window start (append only)")
    parser.add_argument("--metrics-path", type=Path, default=METRICS_PATH)
    parser.add_argument("--projects-dir", type=Path, default=mt.PROJECTS_DIR)
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    parser.add_argument("--no-kata", action="store_true", help="tests only: skip kata lookups for landed dates")
    args = parser.parse_args(argv)

    landed = (lambda ref: None) if args.no_kata else landed_date
    try:
        if args.trend:
            sys.stdout.write(render_trend(read_rows(args.metrics_path)))
        elif args.rebuild:
            rows = rebuild_rows(metrics_path=args.metrics_path, projects_dir=args.projects_dir,
                                registry_path=args.registry, landed=landed)
            print(f"rebuilt {len(rows)} rows")
        else:
            since = _parse_iso(args.since) if args.since else None
            if since is not None and since.tzinfo is None:
                since = since.replace(tzinfo=UTC)
            row = append_row(metrics_path=args.metrics_path, projects_dir=args.projects_dir,
                             registry_path=args.registry, since=since, now=dt.datetime.now(UTC), landed=landed)
            print(f"appended row {row['window_start']} → {row['window_end']}: {row['sessions_interactive']} interactive sessions")
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
