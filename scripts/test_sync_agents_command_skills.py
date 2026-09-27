"""Tests for mirroring ~/.claude/commands into ~/.agents/skills copies.

Run against real temporary directory trees — no mocks.
"""
from sync_agents_command_skills import sync


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
