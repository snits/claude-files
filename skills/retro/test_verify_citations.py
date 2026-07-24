"""Tests for the retro citation verifier."""

from __future__ import annotations

import json

import verify_citations as vc


def write_transcript(tmp_path, entries):
    path = tmp_path / "session.jsonl"
    path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    return path


def human(text):
    return {"type": "user", "message": {"role": "user", "content": text}}


class TestPointerExtraction:
    def test_finds_pointer_and_backtick_quote_on_same_bullet(self):
        report = "- `/a/b/session.jsonl:42`: `the quoted text`\n"
        found = vc.extract_citations(report)
        assert found == [("/a/b/session.jsonl", 42, "the quoted text")]

    def test_finds_pointer_with_double_quoted_text(self):
        report = '- /a/b/session.jsonl:7 — "stop doing that"\n'
        found = vc.extract_citations(report)
        assert found == [("/a/b/session.jsonl", 7, "stop doing that")]

    def test_pointer_without_quote_yields_none_quote(self):
        report = "- see /a/b/session.jsonl:9 for context\n"
        assert vc.extract_citations(report) == [("/a/b/session.jsonl", 9, None)]

    def test_ignores_prose_without_pointers(self):
        assert vc.extract_citations("just some prose about a jsonl file\n") == []

    def test_finds_multiple_pointers_across_lines(self):
        report = "- `/a/s.jsonl:1`: `x`\n- `/a/s.jsonl:2`: `y`\n"
        assert len(vc.extract_citations(report)) == 2


class TestAbbreviatedPointers:
    def test_ellipsis_shortened_pointer_is_flagged_as_abbreviated(self):
        """`.../session.jsonl:21` is not independently resolvable by a reader."""
        report = "- `.../8702d408.jsonl:21`: `some quoted text`\n"
        (path, line, quote) = vc.extract_citations(report)[0]
        assert vc.verify_one(path, line, quote, abbreviated=True).status == (
            "ABBREVIATED-POINTER"
        )

    def test_extraction_marks_abbreviation(self):
        report = "- `.../8702d408.jsonl:21`: `text here`\n"
        assert vc.is_abbreviated(report, report.index("/8702d408"))

    def test_full_path_is_not_marked_abbreviated(self):
        report = "- `/home/x/8702d408.jsonl:21`: `text here`\n"
        assert not vc.is_abbreviated(report, report.index("/home"))


class TestAnnotationTags:
    def test_prefilter_tags_are_stripped_before_matching(self, tmp_path):
        """`[TOOL ERROR]` is the prefilter's annotation, not transcript text.

        A miner copies the whole slice entry, tag included; matching the tag
        against the raw transcript would fail every such citation.
        """
        path = write_transcript(tmp_path, [human("Exit code 2 deposition_spike failed")])
        result = vc.verify_one(str(path), 1, "[TOOL ERROR] Exit code 2 deposition_spike")
        assert result.status == "OK"

    def test_teammate_tag_is_stripped(self, tmp_path):
        path = write_transcript(tmp_path, [human("Another Claude session sent a message")])
        result = vc.verify_one(str(path), 1, "[TEAMMATE] Another Claude session sent")
        assert result.status == "OK"

    def test_quote_that_is_only_a_tag_is_unverifiable(self, tmp_path):
        path = write_transcript(tmp_path, [human("some text")])
        assert vc.verify_one(str(path), 1, "[TEAMMATE]").status == "UNVERIFIABLE"


class TestVerification:
    def test_quote_present_at_cited_line_passes(self, tmp_path):
        path = write_transcript(tmp_path, [human("first"), human("the real quote here")])
        result = vc.verify_one(str(path), 2, "the real quote")
        assert result.status == "OK"

    def test_quote_absent_at_cited_line_is_mismatch(self, tmp_path):
        path = write_transcript(tmp_path, [human("first"), human("something else")])
        result = vc.verify_one(str(path), 2, "the real quote")
        assert result.status == "TEXT-MISMATCH"

    def test_quote_found_at_a_different_line_reports_where(self, tmp_path):
        """The common failure: right quote, wrong line number."""
        path = write_transcript(tmp_path, [human("the real quote here"), human("other")])
        result = vc.verify_one(str(path), 2, "the real quote")
        assert result.status == "TEXT-MISMATCH"
        assert result.found_at == 1

    def test_line_beyond_end_of_file_is_no_such_line(self, tmp_path):
        path = write_transcript(tmp_path, [human("only one")])
        assert vc.verify_one(str(path), 99, "anything").status == "NO-SUCH-LINE"

    def test_missing_file_is_no_such_file(self, tmp_path):
        assert vc.verify_one(str(tmp_path / "gone.jsonl"), 1, "x").status == "NO-SUCH-FILE"

    def test_pointer_without_quote_is_unverifiable_not_ok(self, tmp_path):
        path = write_transcript(tmp_path, [human("text")])
        assert vc.verify_one(str(path), 1, None).status == "UNVERIFIABLE"

    def test_whitespace_differences_do_not_cause_false_mismatch(self, tmp_path):
        path = write_transcript(tmp_path, [human("wrapped   text\nacross lines")])
        assert vc.verify_one(str(path), 1, "wrapped text across lines").status == "OK"

    def test_matches_text_inside_tool_result_blocks(self, tmp_path):
        entry = {
            "type": "user",
            "message": {
                "role": "user",
                "content": [
                    {"type": "tool_result", "is_error": True, "content": "ENOENT boom"}
                ],
            },
        }
        path = write_transcript(tmp_path, [entry])
        assert vc.verify_one(str(path), 1, "ENOENT boom").status == "OK"


class TestReporting:
    def test_exit_code_nonzero_when_a_citation_fails(self, tmp_path, capsys):
        path = write_transcript(tmp_path, [human("real")])
        report = tmp_path / "r.md"
        report.write_text(f"- `{path}:1`: `nowhere near this`\n")
        assert vc.main([str(report)]) == 1
        assert "TEXT-MISMATCH" in capsys.readouterr().out

    def test_exit_code_zero_when_all_pass(self, tmp_path, capsys):
        path = write_transcript(tmp_path, [human("real quote")])
        report = tmp_path / "r.md"
        report.write_text(f"- `{path}:1`: `real quote`\n")
        assert vc.main([str(report)]) == 0

    def test_summary_counts_each_status(self, tmp_path, capsys):
        path = write_transcript(tmp_path, [human("real quote")])
        report = tmp_path / "r.md"
        report.write_text(
            f"- `{path}:1`: `real quote`\n"
            f"- `{path}:99`: `line does not exist`\n"
            f"- `{path}:1` pointer with no quote\n"
        )
        vc.main([str(report)])
        out = capsys.readouterr().out
        assert "1 OK" in out
        assert "1 NO-SUCH-LINE" in out
        assert "1 UNVERIFIABLE" in out

    def test_reports_when_no_citations_found_at_all(self, tmp_path, capsys):
        report = tmp_path / "r.md"
        report.write_text("A retro with no citations whatsoever.\n")
        assert vc.main([str(report)]) == 1
        assert "no citations" in capsys.readouterr().out.lower()
