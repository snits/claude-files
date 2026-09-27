"""Tests for mirroring ~/.claude/commands into ~/.agents/skills copies.

Run against real temporary directory trees — no mocks.
"""
from sync_agents_command_skills import sync, sync_commands


def make_tree(tmp_path):
    commands = tmp_path / "claude" / "commands"
    skills = tmp_path / "agents" / "skills"
    commands.mkdir(parents=True)
    skills.mkdir(parents=True)
    return commands, skills


def test_stale_copy_is_replaced_with_the_command(tmp_path):
    commands, skills = make_tree(tmp_path)
    (commands / "verify-branch.md").write_text("new gate\n")
    (skills / "verify-branch").mkdir()
    (skills / "verify-branch" / "SKILL.md").write_text("old gate\n")

    assert sync(commands, skills) == ["verify-branch"]
    assert (skills / "verify-branch" / "SKILL.md").read_text() == "new gate\n"


def test_identical_copy_is_left_alone(tmp_path):
    commands, skills = make_tree(tmp_path)
    (commands / "groom.md").write_text("same\n")
    (skills / "groom").mkdir()
    (skills / "groom" / "SKILL.md").write_text("same\n")

    assert sync(commands, skills) == []


def test_skill_without_a_command_source_is_untouched(tmp_path):
    commands, skills = make_tree(tmp_path)
    (skills / "retro").mkdir()
    (skills / "retro" / "SKILL.md").write_text("retro\n")

    assert sync(commands, skills) == []
    assert (skills / "retro" / "SKILL.md").read_text() == "retro\n"


def test_symlinked_skill_directory_is_never_written_through(tmp_path):
    # A dir-linked skill is already single-source; writing into it would
    # overwrite the file it points at in ~/.claude/skills.
    commands, skills = make_tree(tmp_path)
    target = tmp_path / "claude" / "skills" / "dream"
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text("the real skill\n")
    (skills / "dream").symlink_to(target)
    (commands / "dream.md").write_text("a command of the same name\n")

    assert sync(commands, skills) == []
    assert (target / "SKILL.md").read_text() == "the real skill\n"


def test_command_with_no_existing_skill_dir_is_not_created(tmp_path):
    commands, skills = make_tree(tmp_path)
    (commands / "smartcompact.md").write_text("x\n")

    assert sync(commands, skills) == []
    assert not (skills / "smartcompact").exists()


def test_missing_skills_root_syncs_nothing(tmp_path):
    commands, _ = make_tree(tmp_path)
    (commands / "verify-branch.md").write_text("x\n")

    assert sync(commands, tmp_path / "absent") == []


def test_linked_skill_file_is_replaced_by_a_copy(tmp_path):
    # Codex skips a SKILL.md that is a symlink, so a link must become a file.
    commands, skills = make_tree(tmp_path)
    (commands / "work-issue.md").write_text("loop\n")
    (skills / "work-issue").mkdir()
    (skills / "work-issue" / "SKILL.md").symlink_to(commands / "work-issue.md")

    assert sync(commands, skills) == ["work-issue"]
    copy = skills / "work-issue" / "SKILL.md"
    assert not copy.is_symlink()
    assert copy.read_text() == "loop\n"


def make_command_tree(tmp_path):
    commands = tmp_path / "claude" / "commands"
    mirror = tmp_path / "agents" / "commands"
    commands.mkdir(parents=True)
    mirror.mkdir(parents=True)
    return commands, mirror


def test_stale_command_copy_is_refreshed(tmp_path):
    commands, mirror = make_command_tree(tmp_path)
    (commands / "super-do.md").write_text("new\n")
    (mirror / "super-do.md").write_text("old\n")

    assert sync_commands(commands, mirror) == ["super-do.md"]
    assert (mirror / "super-do.md").read_text() == "new\n"


def test_linked_command_becomes_a_regular_file(tmp_path):
    commands, mirror = make_command_tree(tmp_path)
    (commands / "groom.md").write_text("groom\n")
    (mirror / "groom.md").symlink_to(commands / "groom.md")

    assert sync_commands(commands, mirror) == ["groom.md"]
    assert not (mirror / "groom.md").is_symlink()
    assert (mirror / "groom.md").read_text() == "groom\n"


def test_identical_command_copy_is_left_alone(tmp_path):
    commands, mirror = make_command_tree(tmp_path)
    (commands / "dead-code.md").write_text("same\n")
    (mirror / "dead-code.md").write_text("same\n")

    assert sync_commands(commands, mirror) == []


def test_command_copy_without_a_source_is_untouched(tmp_path):
    commands, mirror = make_command_tree(tmp_path)
    (mirror / "orphan.md").write_text("keep\n")

    assert sync_commands(commands, mirror) == []
    assert (mirror / "orphan.md").read_text() == "keep\n"


def test_missing_command_mirror_syncs_nothing(tmp_path):
    commands, _ = make_command_tree(tmp_path)
    (commands / "groom.md").write_text("x\n")

    assert sync_commands(commands, tmp_path / "absent") == []
