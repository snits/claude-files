#!/usr/bin/env python3
"""Keep ~/.agents/skills copies of ~/.claude/commands current.

Codex (and other harnesses reading ~/.agents/skills) follow a symlinked skill
directory but skip a skill whose SKILL.md is itself a symlink, so a skill
sourced from a single command file cannot be linked and has to be a copy.
~/.claude/commands/<name>.md is the source; this refreshes
~/.agents/skills/<name>/SKILL.md whenever the two differ.

Only existing copies are refreshed: a skill directory that is a symlink is
already single-source and is never written through, and no new skill
directories are created. Runs as a SessionStart hook; prints one line when it
synced something and nothing otherwise. Ruling: kata claudes-home 7wg6.
"""
import filecmp
import os
import sys
from pathlib import Path

COMMANDS = Path.home() / ".claude" / "commands"
AGENTS_SKILLS = Path.home() / ".agents" / "skills"


def sync(commands: Path, skills: Path) -> list[str]:
    """Refresh stale copies; return the names that were rewritten."""
    if not skills.is_dir():
        return []
    synced = []
    for skill_dir in sorted(skills.iterdir()):
        if skill_dir.is_symlink() or not skill_dir.is_dir():
            continue
        source = commands / f"{skill_dir.name}.md"
        copy = skill_dir / "SKILL.md"
        if not source.is_file():
            continue
        if copy.is_file() and not copy.is_symlink() and filecmp.cmp(source, copy, shallow=False):
            continue
        tmp = skill_dir / ".SKILL.md.sync"
        tmp.write_bytes(source.read_bytes())
        os.replace(tmp, copy)
        synced.append(skill_dir.name)
    return synced


def main() -> int:
    try:
        synced = sync(COMMANDS, AGENTS_SKILLS)
    except OSError as e:
        print(f"sync_agents_command_skills: {e}", file=sys.stderr)
        return 0
    if synced:
        print(f"~/.agents/skills re-synced from ~/.claude/commands: {', '.join(synced)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
