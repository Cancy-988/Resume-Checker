"""
Tests for the Resume Checker Bot.

All tests operate on plain text so no external dependencies (pdfplumber /
python-docx) are required to run the suite.
"""

import dataclasses
import json
import os
import tempfile
from pathlib import Path

import pytest

from resume_checker import (
    ACTION_VERBS,
    CheckResult,
    SectionResult,
    _compute_score,
    _count_action_verbs,
    _count_quantifications,
    _detect_sections,
    _has_contact,
    _score_to_grade,
    _word_count,
    analyze_text,
    check_resume,
    extract_text_from_txt,
    format_report,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

MINIMAL_RESUME = """
Jane Doe
jane@example.com
+1 555-123-4567
linkedin.com/in/janedoe

Summary
Experienced software engineer with 5 years building scalable web applications.

Experience
Software Engineer – Acme Corp (2020–present)
- Developed and shipped 10 new features that increased user retention by 25%
- Led a team of 5 engineers to deliver the project on time
- Reduced infrastructure costs by 30% through optimization

Education
B.Sc. Computer Science, State University (2018)

Skills
Python, JavaScript, SQL, Docker, Kubernetes, AWS

Projects
Resume Checker – Built an open-source tool that analysed 200+ resumes

Certifications
AWS Certified Solutions Architect
"""

POOR_RESUME = """
John Smith

I am looking for a job. I can do things well.
"""


# ---------------------------------------------------------------------------
# Unit tests – helpers
# ---------------------------------------------------------------------------

class TestWordCount:
    def test_empty_string(self):
        assert _word_count("") == 0

    def test_single_word(self):
        assert _word_count("hello") == 1

    def test_multiple_words(self):
        assert _word_count("hello world foo") == 3

    def test_minimal_resume(self):
        assert _word_count(MINIMAL_RESUME) > 50


class TestScoreToGrade:
    def test_a_grade(self):
        assert _score_to_grade(95) == "A"
        assert _score_to_grade(90) == "A"

    def test_b_grade(self):
        assert _score_to_grade(85) == "B"
        assert _score_to_grade(80) == "B"

    def test_c_grade(self):
        assert _score_to_grade(75) == "C"
        assert _score_to_grade(70) == "C"

    def test_d_grade(self):
        assert _score_to_grade(65) == "D"
        assert _score_to_grade(60) == "D"

    def test_f_grade(self):
        assert _score_to_grade(59) == "F"
        assert _score_to_grade(0) == "F"


class TestDetectSections:
    def test_all_sections_present(self):
        results = _detect_sections(MINIMAL_RESUME)
        for section in ("contact", "summary", "experience", "education", "skills"):
            assert results[section].found, f"Expected section '{section}' to be found"

    def test_missing_sections(self):
        results = _detect_sections(POOR_RESUME)
        assert not results["experience"].found
        assert not results["education"].found
        assert not results["skills"].found

    def test_feedback_message_found(self):
        results = _detect_sections(MINIMAL_RESUME)
        assert "✅" in results["experience"].feedback

    def test_feedback_message_missing(self):
        results = _detect_sections(POOR_RESUME)
        assert "❌" in results["experience"].feedback


class TestActionVerbs:
    def test_known_verbs(self):
        text = "I developed and launched a new product. I also led a team."
        count = _count_action_verbs(text)
        assert count >= 2

    def test_no_verbs(self):
        text = "Hello world this is a test with no resume verbs"
        count = _count_action_verbs(text)
        assert count == 0

    def test_minimal_resume_has_verbs(self):
        count = _count_action_verbs(MINIMAL_RESUME)
        assert count >= 3


class TestQuantification:
    def test_percentage(self):
        text = "Increased sales by 25%"
        assert _count_quantifications(text) >= 1

    def test_users(self):
        text = "Platform reached 1 million users in 6 months"
        assert _count_quantifications(text) >= 1

    def test_no_numbers(self):
        text = "I did some things and achieved goals"
        assert _count_quantifications(text) == 0

    def test_minimal_resume(self):
        assert _count_quantifications(MINIMAL_RESUME) >= 2


class TestHasContact:
    def test_email_detected(self):
        has_email, _, _ = _has_contact("Contact me at foo@bar.com")
        assert has_email

    def test_no_email(self):
        has_email, _, _ = _has_contact("No contact info here")
        assert not has_email

    def test_phone_detected(self):
        _, has_phone, _ = _has_contact("+1 555-123-4567")
        assert has_phone

    def test_linkedin_detected(self):
        _, _, has_linkedin = _has_contact("linkedin.com/in/janedoe")
        assert has_linkedin

    def test_all_present(self):
        has_email, has_phone, has_linkedin = _has_contact(MINIMAL_RESUME)
        assert has_email
        assert has_phone
        assert has_linkedin


class TestComputeScore:
    def test_all_sections_found(self):
        sections = {sec: SectionResult(found=True, feedback="") for sec in ["contact", "summary", "experience", "education", "skills", "projects", "certifications"]}
        score = _compute_score(sections, action_verb_count=10, quant_count=5)
        assert score == 100

    def test_no_sections_found(self):
        sections = {sec: SectionResult(found=False, feedback="") for sec in ["contact", "summary", "experience", "education", "skills", "projects", "certifications"]}
        score = _compute_score(sections, action_verb_count=0, quant_count=0)
        assert score == 0

    def test_partial_score(self):
        sections = {sec: SectionResult(found=False, feedback="") for sec in ["contact", "summary", "experience", "education", "skills", "projects", "certifications"]}
        sections["experience"] = SectionResult(found=True, feedback="")
        sections["education"] = SectionResult(found=True, feedback="")
        score = _compute_score(sections, action_verb_count=0, quant_count=0)
        assert 0 < score < 100


# ---------------------------------------------------------------------------
# Integration tests – analyze_text
# ---------------------------------------------------------------------------

class TestAnalyzeText:
    def test_minimal_resume_score(self):
        result = analyze_text(MINIMAL_RESUME)
        assert isinstance(result, CheckResult)
        assert result.score > 60, "A well-formed resume should score > 60"
        assert result.grade in ("A", "B", "C", "D", "F")

    def test_poor_resume_score(self):
        result = analyze_text(POOR_RESUME)
        assert result.score < 50, "A poor resume should score < 50"

    def test_strengths_populated(self):
        result = analyze_text(MINIMAL_RESUME)
        assert len(result.strengths) > 0

    def test_suggestions_for_poor_resume(self):
        result = analyze_text(POOR_RESUME)
        assert len(result.suggestions) > 0

    def test_contact_fields(self):
        result = analyze_text(MINIMAL_RESUME)
        assert result.has_email
        assert result.has_phone
        assert result.has_linkedin

    def test_word_count_populated(self):
        result = analyze_text(MINIMAL_RESUME)
        assert result.word_count > 0

    def test_action_verb_count(self):
        result = analyze_text(MINIMAL_RESUME)
        assert result.action_verb_count > 0

    def test_quantification_count(self):
        result = analyze_text(MINIMAL_RESUME)
        assert result.quantification_count > 0


# ---------------------------------------------------------------------------
# Integration tests – check_resume (file I/O)
# ---------------------------------------------------------------------------

class TestCheckResume:
    def test_txt_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(MINIMAL_RESUME)
            tmp_path = fh.name
        try:
            result = check_resume(tmp_path)
            assert result.score > 0
        finally:
            os.unlink(tmp_path)

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            check_resume("/nonexistent/path/to/resume.txt")

    def test_unsupported_format_raises(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".xyz", delete=False
        ) as fh:
            fh.write("test content")
            tmp_path = fh.name
        try:
            with pytest.raises(ValueError, match="Unsupported file format"):
                check_resume(tmp_path)
        finally:
            os.unlink(tmp_path)


class TestExtractTextFromTxt:
    def test_reads_file_content(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as fh:
            fh.write("Hello, World!")
            tmp_path = fh.name
        try:
            text = extract_text_from_txt(tmp_path)
            assert text == "Hello, World!"
        finally:
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

class TestFormatReport:
    def test_contains_score(self):
        result = analyze_text(MINIMAL_RESUME)
        report = format_report(result)
        assert str(result.score) in report

    def test_contains_grade(self):
        result = analyze_text(MINIMAL_RESUME)
        report = format_report(result)
        assert result.grade in report

    def test_contains_word_count(self):
        result = analyze_text(MINIMAL_RESUME)
        report = format_report(result)
        assert str(result.word_count) in report

    def test_poor_resume_report_has_suggestions(self):
        result = analyze_text(POOR_RESUME)
        report = format_report(result)
        assert "SUGGESTIONS" in report

    def test_report_is_string(self):
        result = analyze_text(MINIMAL_RESUME)
        assert isinstance(format_report(result), str)


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

class TestCLI:
    def _run(self, *argv):
        """Run main() and return (exit_code, stdout_capture)."""
        import io
        import sys
        from app import main

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            code = main(list(argv))
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        return code, output

    def test_basic_run(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(MINIMAL_RESUME)
            tmp_path = fh.name
        try:
            code, output = self._run(tmp_path)
            assert code == 0
            assert "RESUME CHECKER BOT" in output
        finally:
            os.unlink(tmp_path)

    def test_json_output(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(MINIMAL_RESUME)
            tmp_path = fh.name
        try:
            code, output = self._run(tmp_path, "--json")
            assert code == 0
            data = json.loads(output)
            assert "score" in data
            assert "grade" in data
        finally:
            os.unlink(tmp_path)

    def test_missing_file_exit_code(self):
        import sys

        old_stderr = sys.stderr
        import io

        sys.stderr = io.StringIO()
        try:
            from app import main
            code = main(["/no/such/file.txt"])
        finally:
            sys.stderr = old_stderr
        assert code == 1

    def test_unsupported_format_exit_code(self):
        import io
        import sys

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".xyz", delete=False
        ) as fh:
            fh.write("test")
            tmp_path = fh.name
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        try:
            from app import main
            code = main([tmp_path])
        finally:
            sys.stderr = old_stderr
            os.unlink(tmp_path)
        assert code == 1
