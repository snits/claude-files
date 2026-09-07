#!/usr/bin/env python3
"""Per-retro pattern metrics: hits and eligible sessions per deterministic pattern.

Spec: ~/claudes-home/docs/superpowers/specs/2026-09-07-retro-pattern-metrics-design.md
"""

from __future__ import annotations

import datetime as dt
import hashlib
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent / "patterns.toml"
ELIGIBILITY = ("isolated", "ran_bash", "any")


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
