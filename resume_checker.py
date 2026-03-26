"""
Resume Checker Bot
Analyzes resumes and provides actionable feedback to help improve them.
Supports PDF, DOCX, and plain-text (.txt) resume files.
"""

from __future__ import annotations

import os
import re
import string
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Optional heavy-weight imports – handled gracefully so tests that do not
# need them still work without installing the packages.
# ---------------------------------------------------------------------------

try:
    import pdfplumber  # type: ignore
    _PDF_AVAILABLE = True
except ImportError:  # pragma: no cover
    _PDF_AVAILABLE = False

try:
    from docx import Document as _DocxDocument  # type: ignore
    _DOCX_AVAILABLE = True
except ImportError:  # pragma: no cover
    _DOCX_AVAILABLE = False


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Common section headings found in resumes (case-insensitive)
SECTION_KEYWORDS: dict[str, list[str]] = {
    "contact": [
        "contact", "phone", "email", "address", "linkedin", "github",
        "portfolio", "website",
    ],
    "summary": [
        "summary", "objective", "profile", "about me", "overview",
        "professional summary", "career objective",
    ],
    "experience": [
        "experience", "work experience", "employment", "work history",
        "professional experience", "career history", "internship",
    ],
    "education": [
        "education", "academic", "qualification", "degree", "university",
        "college", "school",
    ],
    "skills": [
        "skills", "technical skills", "competencies", "technologies",
        "tools", "languages", "expertise", "proficiencies",
    ],
    "projects": [
        "projects", "personal projects", "side projects", "portfolio",
        "open source",
    ],
    "certifications": [
        "certifications", "certificates", "licenses", "accreditations",
        "achievements", "awards", "honors",
    ],
}

# Strong action verbs that indicate concrete contributions
ACTION_VERBS: list[str] = [
    "achieved", "built", "coordinated", "created", "decreased", "delivered",
    "designed", "developed", "directed", "drove", "engineered", "established",
    "exceeded", "executed", "expanded", "generated", "grew", "implemented",
    "improved", "increased", "initiated", "launched", "led", "managed",
    "mentored", "modernized", "optimized", "oversaw", "planned", "produced",
    "reduced", "refactored", "resolved", "scaled", "shipped", "spearheaded",
    "streamlined", "transformed", "trained",
]

# Patterns that suggest quantified achievements (numbers / percentages)
QUANTIFICATION_PATTERN = re.compile(
    r"\b\d+[\d,]*\s*(?:%|percent|x|times|hours?|days?|weeks?|months?|years?|"
    r"users?|customers?|employees?|teams?|projects?|"
    r"k|m|b|million|billion|thousand)(?!\w)",
    re.IGNORECASE,
)

# Simple email / phone / LinkedIn patterns for contact detection
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(
    r"(\+?\d[\d\s\-().]{7,}\d)"
)
LINKEDIN_PATTERN = re.compile(r"linkedin\.com/in/[\w\-]+", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SectionResult:
    found: bool
    feedback: str


@dataclass
class CheckResult:
    """Full analysis result for a single resume."""

    score: int  # 0-100
    grade: str  # A / B / C / D / F
    sections: dict[str, SectionResult] = field(default_factory=dict)
    suggestions: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    word_count: int = 0
    action_verb_count: int = 0
    quantification_count: int = 0
    has_email: bool = False
    has_phone: bool = False
    has_linkedin: bool = False


# ---------------------------------------------------------------------------
# Text extraction helpers
# ---------------------------------------------------------------------------

def extract_text_from_pdf(path: str | Path) -> str:
    """Extract plain text from a PDF file using pdfplumber."""
    if not _PDF_AVAILABLE:
        raise ImportError(
            "pdfplumber is required to parse PDF files. "
            "Install it with: pip install pdfplumber"
        )
    pages: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n".join(pages)


def extract_text_from_docx(path: str | Path) -> str:
    """Extract plain text from a DOCX file using python-docx."""
    if not _DOCX_AVAILABLE:
        raise ImportError(
            "python-docx is required to parse DOCX files. "
            "Install it with: pip install python-docx"
        )
    doc = _DocxDocument(path)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text_from_txt(path: str | Path) -> str:
    """Read a plain-text file."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def extract_text(path: str | Path) -> str:
    """Detect file type and return extracted text."""
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    if suffix in (".docx", ".doc"):
        return extract_text_from_docx(path)
    if suffix in (".txt", ".text", ""):
        return extract_text_from_txt(path)
    raise ValueError(f"Unsupported file format: '{suffix}'. Use PDF, DOCX, or TXT.")


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def _lower_text(text: str) -> str:
    return text.lower()


def _detect_sections(text: str) -> dict[str, SectionResult]:
    lower = _lower_text(text)
    results: dict[str, SectionResult] = {}
    for section, keywords in SECTION_KEYWORDS.items():
        found = any(kw in lower for kw in keywords)
        if found:
            feedback = f"✅  {section.capitalize()} section detected."
        else:
            feedback = f"❌  {section.capitalize()} section not found – consider adding one."
        results[section] = SectionResult(found=found, feedback=feedback)
    return results


def _count_action_verbs(text: str) -> int:
    lower = _lower_text(text)
    words = set(re.findall(r"\b[a-z]+\b", lower))
    return sum(1 for verb in ACTION_VERBS if verb in words)


def _count_quantifications(text: str) -> int:
    return len(QUANTIFICATION_PATTERN.findall(text))


def _has_contact(text: str) -> tuple[bool, bool, bool]:
    has_email = bool(EMAIL_PATTERN.search(text))
    has_phone = bool(PHONE_PATTERN.search(text))
    has_linkedin = bool(LINKEDIN_PATTERN.search(text))
    return has_email, has_phone, has_linkedin


def _word_count(text: str) -> int:
    return len(text.split())


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

_SECTION_WEIGHTS: dict[str, int] = {
    "contact": 15,
    "summary": 10,
    "experience": 20,
    "education": 15,
    "skills": 15,
    "projects": 10,
    "certifications": 5,
}
_SECTION_TOTAL = sum(_SECTION_WEIGHTS.values())  # 90 points from sections

_ACTION_VERB_BONUS_MAX = 5   # up to 5 points
_QUANT_BONUS_MAX = 5         # up to 5 points


def _compute_score(
    sections: dict[str, SectionResult],
    action_verb_count: int,
    quant_count: int,
) -> int:
    section_score = sum(
        _SECTION_WEIGHTS[sec]
        for sec, result in sections.items()
        if result.found
    )
    # Scale section score to 90%
    section_points = int(section_score / _SECTION_TOTAL * 90)

    # Action verb bonus (0-5)
    verb_bonus = min(action_verb_count, 10) / 10 * _ACTION_VERB_BONUS_MAX

    # Quantification bonus (0-5)
    quant_bonus = min(quant_count, 5) / 5 * _QUANT_BONUS_MAX

    return min(100, section_points + int(verb_bonus) + int(quant_bonus))


# ---------------------------------------------------------------------------
# Main analyser
# ---------------------------------------------------------------------------

def analyze_text(text: str) -> CheckResult:
    """
    Analyze raw resume text and return a :class:`CheckResult`.

    This is the core function. You can call it directly if you already have
    the plain text of a resume (useful in tests or pipelines).
    """
    sections = _detect_sections(text)
    action_verb_count = _count_action_verbs(text)
    quant_count = _count_quantifications(text)
    has_email, has_phone, has_linkedin = _has_contact(text)
    wc = _word_count(text)
    score = _compute_score(sections, action_verb_count, quant_count)
    grade = _score_to_grade(score)

    strengths: list[str] = []
    suggestions: list[str] = []

    # Section feedback
    for sec_result in sections.values():
        if sec_result.found:
            strengths.append(sec_result.feedback)
        else:
            suggestions.append(sec_result.feedback)

    # Contact details
    if has_email:
        strengths.append("✅  Email address found.")
    else:
        suggestions.append("❌  No email address detected – add one to your contact section.")

    if has_phone:
        strengths.append("✅  Phone number found.")
    else:
        suggestions.append("❌  No phone number detected – consider adding one.")

    if has_linkedin:
        strengths.append("✅  LinkedIn profile URL found.")
    else:
        suggestions.append("⚠️   No LinkedIn URL detected – adding one can increase visibility.")

    # Action verbs
    if action_verb_count >= 8:
        strengths.append(
            f"✅  Strong use of action verbs ({action_verb_count} detected)."
        )
    elif action_verb_count >= 4:
        suggestions.append(
            f"⚠️   Only {action_verb_count} action verb(s) detected. "
            "Try to start bullet points with strong verbs (e.g. 'built', 'led', 'optimized')."
        )
    else:
        suggestions.append(
            f"❌  Very few action verbs detected ({action_verb_count}). "
            "Rewrite experience bullets to start with strong action verbs."
        )

    # Quantified achievements
    if quant_count >= 3:
        strengths.append(
            f"✅  Good use of quantified achievements ({quant_count} found)."
        )
    elif quant_count == 1 or quant_count == 2:
        suggestions.append(
            f"⚠️   Only {quant_count} quantified achievement(s) found. "
            "Add numbers/percentages to demonstrate impact (e.g. 'reduced load time by 40%')."
        )
    else:
        suggestions.append(
            "❌  No quantified achievements found. "
            "Use metrics to show impact (e.g. 'increased revenue by 20%', 'managed a team of 5')."
        )

    # Word count / length
    if wc < 200:
        suggestions.append(
            f"❌  Resume appears too short ({wc} words). "
            "Aim for at least 400–600 words for a one-page resume."
        )
    elif wc > 1000:
        suggestions.append(
            f"⚠️   Resume may be too long ({wc} words). "
            "Keep a one-page resume under ~700 words; two pages under ~1,400."
        )
    else:
        strengths.append(f"✅  Resume length looks good ({wc} words).")

    return CheckResult(
        score=score,
        grade=grade,
        sections=sections,
        suggestions=suggestions,
        strengths=strengths,
        word_count=wc,
        action_verb_count=action_verb_count,
        quantification_count=quant_count,
        has_email=has_email,
        has_phone=has_phone,
        has_linkedin=has_linkedin,
    )


def check_resume(path: str | Path) -> CheckResult:
    """
    Load a resume file and return analysis results.

    :param path: Path to a ``.pdf``, ``.docx``, or ``.txt`` resume file.
    :returns: A :class:`CheckResult` containing score, grade, and suggestions.
    :raises FileNotFoundError: If the file does not exist.
    :raises ValueError: If the file format is not supported.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {path}")
    text = extract_text(path)
    return analyze_text(text)


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

def format_report(result: CheckResult) -> str:
    """Return a human-readable report string for a :class:`CheckResult`."""
    sep = "─" * 60
    lines: list[str] = [
        "",
        "=" * 60,
        "          📄  RESUME CHECKER BOT  REPORT",
        "=" * 60,
        f"  Overall Score : {result.score}/100  (Grade: {result.grade})",
        f"  Word Count    : {result.word_count}",
        f"  Action Verbs  : {result.action_verb_count}",
        f"  Quantified    : {result.quantification_count}",
        sep,
    ]

    if result.strengths:
        lines.append("  STRENGTHS")
        lines.append(sep)
        for s in result.strengths:
            lines.append(f"  {s}")
        lines.append("")

    if result.suggestions:
        lines.append("  SUGGESTIONS FOR IMPROVEMENT")
        lines.append(sep)
        for s in result.suggestions:
            lines.append(f"  {s}")
        lines.append("")

    lines.append("=" * 60)
    lines.append("")
    return "\n".join(lines)
