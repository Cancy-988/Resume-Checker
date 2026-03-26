# Resume-Checker

A Python-based **Resume Checker Bot** that analyses your resume and provides an overall score, grade, and actionable suggestions to help you land more interviews.

## Features

- 📄 Supports **PDF**, **DOCX**, and **TXT** resume files
- 🏷️  Detects key resume **sections** (Contact, Summary, Experience, Education, Skills, Projects, Certifications)
- 💪 Counts **action verbs** (e.g. *developed*, *led*, *optimized*)
- 📊 Identifies **quantified achievements** (e.g. *"increased revenue by 20%"*, *"managed a team of 5"*)
- 📧 Validates contact details (email, phone, LinkedIn)
- 🎯 Returns a **0–100 score** with letter grade (A–F)
- 🖨️  Human-readable report *or* machine-readable **JSON** output

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Cancy-988/Resume-Checker.git
cd Resume-Checker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Analyse your resume
python app.py path/to/your_resume.pdf
```

### Example output

```
============================================================
          📄  RESUME CHECKER BOT  REPORT
============================================================
  Overall Score : 88/100  (Grade: B)
  Word Count    : 520
  Action Verbs  : 9
  Quantified    : 5
────────────────────────────────────────────────────────────
  STRENGTHS
────────────────────────────────────────────────────────────
  ✅  Contact section detected.
  ✅  Summary section detected.
  ✅  Experience section detected.
  ✅  Education section detected.
  ✅  Skills section detected.
  ✅  Email address found.
  ✅  Phone number found.
  ✅  Strong use of action verbs (9 detected).
  ✅  Good use of quantified achievements (5 found).

  SUGGESTIONS FOR IMPROVEMENT
────────────────────────────────────────────────────────────
  ❌  Projects section not found – consider adding one.
  ⚠️   No LinkedIn URL detected – adding one can increase visibility.
============================================================
```

### JSON output

```bash
python app.py resume.txt --json
```

```json
{
  "score": 88,
  "grade": "B",
  "word_count": 520,
  "action_verb_count": 9,
  "quantification_count": 5,
  "has_email": true,
  "has_phone": true,
  "has_linkedin": false,
  ...
}
```

## Usage

```
usage: resume-checker [-h] [--json] resume

positional arguments:
  resume      Path to the resume file (.pdf, .docx, or .txt)

optional arguments:
  --json      Output results as JSON instead of a formatted report
  -h, --help  Show this help message and exit
```

## Python API

You can also use the checker directly in your own code:

```python
from resume_checker import check_resume, analyze_text, format_report

# From a file
result = check_resume("my_resume.pdf")
print(format_report(result))
print(f"Score: {result.score}/100  Grade: {result.grade}")

# From plain text
result = analyze_text("Jane Doe\njane@example.com\n...")
```

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Project Structure

```
Resume-Checker/
├── resume_checker.py   # Core analysis logic
├── app.py              # CLI entry point
├── requirements.txt    # Dependencies
└── tests/
    └── test_resume_checker.py
```
