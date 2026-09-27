#!/usr/bin/env python3
"""Keep ~/.agents copies of ~/.claude/commands current.

Codex (and other harnesses reading ~/.agents/skills) follow a symlinked skill
directory but skip a skill whose SKILL.md is itself a symlink, so a skill
sourced from a single command file cannot be linked and has to be a copy.
~/.claude/commands/<name>.md is the source; this refreshes
~/.agents/skills/<name>/SKILL.md whenever the two differ. ~/.agents/commands
mirrors the same files and is kept as copies for the same reason: a reader
that skips file symlinks would silently lose them.

Only existing copies are refreshed: a skill directory that is a symlink is
already single-source and is never written through, and nothing new is
created. Runs as a SessionStart hook; prints one line when it synced something
and nothing otherwise. Ruling: kata claudes-home 7wg6.
"""
import filecmp
import os
import sys
from pathlib import Path

COMMANDS = Path.home() / ".claude" / "commands"
AGENTS_SKILLS = Path.home() / ".agents" / "skills"
AGENTS_COMMANDS = Path.home() / ".agents" / "commands"


def refresh(source: Path, copy: Path) -> bool:
    """Make copy a regular file identical to source; return True if it changed."""
    if copy.is_file() and not copy.is_symlink() and filecmp.cmp(source, copy, shallow=False):
        return False
    tmp = copy.with_name(f".{copy.name}.sync")
    tmp.write_bytes(source.read_bytes())
    os.replace(tmp, copy)
    return True


def sync(commands: Path, skills: Path) -> list[str]:
    """Refresh stale SKILL.md copies; return the skill names that were rewritten."""
    if not skills.is_dir():
        return []
    synced = []
    for skill_dir in sorted(skills.iterdir()):
        if skill_dir.is_symlink() or not skill_dir.is_dir():
            continue
        source = commands / f"{skill_dir.name}.md"
        if source.is_file() and refresh(source, skill_dir / "SKILL.md"):
            synced.append(skill_dir.name)
    return synced


def sync_commands(commands: Path, mirror: Path) -> list[str]:
    """Refresh stale command copies; return the file names that were rewritten."""
    synced = []
    for copy in sorted(mirror.glob("*.md")):
        source = commands / copy.name
        if source.is_file() and refresh(source, copy):
            synced.append(copy.name)
    return synced


def main() -> int:
    try:
        skills = sync(COMMANDS, AGENTS_SKILLS)
        commands = sync_commands(COMMANDS, AGENTS_COMMANDS)
    except OSError as e:
        print(f"sync_agents_command_skills: {e}", file=sys.stderr)
        return 0
    if skills or commands:
        print(f"~/.agents re-synced from ~/.claude/commands: {', '.join(skills + commands)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
