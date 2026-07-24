"""Tests for the retro transcript prefilter."""

from __future__ import annotations

import json
import time

import pytest

import mine_transcripts as mt


def write_session(directory, name, entries):
    """Write entries as a .jsonl transcript and return its path."""
    path = directory / name
    path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    return path


def human(text):
    return {"type": "user", "message": {"role": "user", "content": text}}


def assistant(text):
    return {
        "type": "assistant",
        "message": {"role": "assistant", "content": [{"type": "text", "text": text}]},
    }


def tool_result(text, is_error=False):
    return {
        "type": "user",
        "message": {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "abc",
                    "is_error": is_error,
                    "content": text,
                }
            ],
        },
    }


class TestHumanTurnExtraction:
    def test_extracts_typed_human_turns(self, tmp_path):
        path = write_session(
            tmp_path, "s.jsonl", [human("that's not what I asked for"), assistant("ok")]
        )
        facts = mt.scan_session(path)
        assert [t["text"] for t in facts.human_turns] == ["that's not what I asked for"]

    def test_records_line_number_that_resolves_in_the_raw_file(self, tmp_path):
        """Evidence pointers must be checkable against the transcript."""
        path = write_session(
            tmp_path,
            "s.jsonl",
            [assistant("first"), assistant("second"), human("the finding")],
        )
        facts = mt.scan_session(path)
        turn = facts.human_turns[0]
        assert turn["line"] == 3
        raw_line = path.read_text().splitlines()[turn["line"] - 1]
        assert turn["text"] in raw_line

    def test_ignores_tool_results_which_are_also_role_user(self, tmp_path):
        path = write_session(
            tmp_path, "s.jsonl", [tool_result("total 40\ndrwxr-xr-x boring output")]
        )
        facts = mt.scan_session(path)
        assert facts.human_turns == []

    def test_drops_harness_injected_turns(self, tmp_path):
        path = write_session(
            tmp_path,
            "s.jsonl",
            [
                human("<system-reminder>you have memory</system-reminder>"),
                human("<command-name>/wakey</command-name>"),
                human("real question"),
            ],
        )
        facts = mt.scan_session(path)
        assert [t["text"] for t in facts.human_turns] == ["real question"]

    def test_drops_meta_entries(self, tmp_path):
        path = write_session(
            tmp_path,
            "s.jsonl",
            [{**human("caveat text"), "isMeta": True}, human("real")],
        )
        facts = mt.scan_session(path)
        assert [t["text"] for t in facts.human_turns] == ["real"]

    def test_extracts_text_blocks_from_list_content(self, tmp_path):
        entry = {
            "type": "user",
            "message": {
                "role": "user",
                "content": [{"type": "text", "text": "typed with an image"}],
            },
        }
        path = write_session(tmp_path, "s.jsonl", [entry])
        facts = mt.scan_session(path)
        assert [t["text"] for t in facts.human_turns] == ["typed with an image"]


class TestSpeakerAttribution:
    def test_teammate_messages_are_marked_not_attributed_to_jerry(self, tmp_path):
        """Another agent's message arrives as a user turn but is not a correction from Jerry."""
        path = write_session(
            tmp_path,
            "s.jsonl",
            [
                human('Another Claude session sent a message: <teammate-message id="x">fix it'),
                human("actual Jerry turn"),
            ],
        )
        facts = mt.scan_session(path)
        assert facts.human_turns[0]["speaker"] == "teammate"
        assert facts.human_turns[1]["speaker"] == "user"

    def test_markdown_labels_teammate_turns(self, tmp_path, capsys):
        project = tmp_path / "-home-jsnitsel-devel-thing"
        project.mkdir()
        write_session(
            project, "s.jsonl", [human('<teammate-message id="x">review says revise')]
        )
        mt.main(["--projects-dir", str(tmp_path), "--days", "7"])
        assert "[TEAMMATE]" in capsys.readouterr().out


class TestToolErrors:
    def test_collects_failed_tool_results(self, tmp_path):
        path = write_session(
            tmp_path,
            "s.jsonl",
            [tool_result("ok result"), tool_result("ENOENT: no such file", is_error=True)],
        )
        facts = mt.scan_session(path)
        assert len(facts.tool_errors) == 1
        assert "ENOENT" in facts.tool_errors[0]["text"]
        assert facts.tool_errors[0]["line"] == 2

    def test_tool_errors_are_not_counted_as_human_turns(self, tmp_path):
        path = write_session(tmp_path, "s.jsonl", [tool_result("boom", is_error=True)])
        facts = mt.scan_session(path)
        assert facts.human_turns == []


class TestRobustness:
    def test_counts_unparseable_lines_instead_of_crashing(self, tmp_path):
        path = tmp_path / "s.jsonl"
        path.write_text(json.dumps(human("good")) + "\n{ truncated json\n")
        facts = mt.scan_session(path)
        assert facts.parse_failures == 1
        assert len(facts.human_turns) == 1

    def test_empty_transcript_yields_no_turns(self, tmp_path):
        path = tmp_path / "s.jsonl"
        path.write_text("")
        facts = mt.scan_session(path)
        assert facts.human_turns == []
        assert facts.is_interactive is False


class TestHeadlessClassification:
    def test_session_without_human_turns_is_headless(self, tmp_path):
        path = write_session(tmp_path, "s.jsonl", [assistant("automated run")])
        assert mt.scan_session(path).is_interactive is False

    def test_session_with_human_turns_is_interactive(self, tmp_path):
        path = write_session(tmp_path, "s.jsonl", [human("hi")])
        assert mt.scan_session(path).is_interactive is True


class TestWindowSelection:
    def test_selects_only_sessions_modified_in_window(self, tmp_path):
        project = tmp_path / "-home-jsnitsel-devel-thing"
        project.mkdir()
        recent = write_session(project, "recent.jsonl", [human("a")])
        stale = write_session(project, "stale.jsonl", [human("b")])
        old = time.time() - 30 * 86400
        import os

        os.utime(stale, (old, old))

        found = mt.sessions_in_window(time.time() - 7 * 86400, projects_dir=tmp_path)
        assert found == [recent]

    def test_excludes_subagent_transcripts(self, tmp_path):
        """Subagent transcripts contain no human turns, so no correction signal."""
        project = tmp_path / "-home-jsnitsel-devel-thing"
        sub = project / "session-id" / "subagents"
        sub.mkdir(parents=True)
        main = write_session(project, "main.jsonl", [human("a")])
        write_session(sub, "agent.jsonl", [human("b")])

        found = mt.sessions_in_window(time.time() - 7 * 86400, projects_dir=tmp_path)
        assert found == [main]

    def test_missing_projects_dir_returns_empty(self, tmp_path):
        assert mt.sessions_in_window(0, projects_dir=tmp_path / "nope") == []


class TestReporting:
    def test_json_output_lists_headless_sessions_explicitly(self, tmp_path, capsys):
        """A skipped source must be reported, never silently dropped."""
        project = tmp_path / "-home-jsnitsel-devel-thing"
        project.mkdir()
        write_session(project, "a.jsonl", [human("real")])
        write_session(project, "b.jsonl", [assistant("automated")])

        mt.main(["--projects-dir", str(tmp_path), "--days", "7", "--json"])
        payload = json.loads(capsys.readouterr().out)
        assert len(payload["sessions"]) == 1
        assert len(payload["headless_sessions"]) == 1

    def test_markdown_pointer_is_one_complete_copyable_token(self, tmp_path, capsys):
        """A bare 'L648:' invites citing the slice's own line number instead.

        Emitting the full path:line means the miner copies a whole token and has
        no second coordinate system to confuse it with.
        """
        project = tmp_path / "-home-jsnitsel-devel-thing"
        project.mkdir()
        path = write_session(project, "a.jsonl", [human("stop doing that")])

        mt.main(["--projects-dir", str(tmp_path), "--days", "7"])
        out = capsys.readouterr().out
        assert f"{path}:1" in out
        assert "stop doing that" in out

    def test_tool_error_pointer_is_also_a_complete_token(self, tmp_path, capsys):
        project = tmp_path / "-home-jsnitsel-devel-thing"
        project.mkdir()
        path = write_session(
            project, "a.jsonl", [human("hi"), tool_result("ENOENT", is_error=True)]
        )

        mt.main(["--projects-dir", str(tmp_path), "--days", "7"])
        out = capsys.readouterr().out
        assert f"{path}:2" in out

    def test_truncated_tool_error_list_is_announced(self, tmp_path, capsys):
        """Caps are reported, not silent."""
        project = tmp_path / "-home-jsnitsel-devel-thing"
        project.mkdir()
        entries = [human("hi")] + [tool_result(f"err {i}", is_error=True) for i in range(20)]
        write_session(project, "a.jsonl", entries)

        mt.main(["--projects-dir", str(tmp_path), "--days", "7"])
        out = capsys.readouterr().out
        assert "further tool errors not shown" in out

    def test_project_filter_scopes_output(self, tmp_path, capsys):
        """Project dir names all start with '-', which argparse would eat as a flag.

        The filter matches on substring so a bare name like 'alexandria' works.
        """
        for name in ("-home-jsnitsel-devel-alexandria", "-home-jsnitsel-devel-orbweaver"):
            project = tmp_path / name
            project.mkdir()
            write_session(project, "s.jsonl", [human(f"turn in {name}")])

        mt.main(["--projects-dir", str(tmp_path), "--days", "7", "--project", "alexandria"])
        out = capsys.readouterr().out
        assert "turn in -home-jsnitsel-devel-alexandria" in out
        assert "turn in -home-jsnitsel-devel-orbweaver" not in out

    def test_project_filter_accepts_full_dir_name_via_equals(self, tmp_path, capsys):
        project = tmp_path / "-home-jsnitsel-devel-alexandria"
        project.mkdir()
        write_session(project, "s.jsonl", [human("scoped turn")])

        mt.main(
            [
                "--projects-dir",
                str(tmp_path),
                "--days",
                "7",
                "--project=-home-jsnitsel-devel-alexandria",
            ]
        )
        assert "scoped turn" in capsys.readouterr().out
