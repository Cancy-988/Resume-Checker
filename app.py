#!/usr/bin/env python3
"""
Resume Checker Bot – CLI entry point.

Usage:
    python app.py resume.pdf
    python app.py resume.docx
    python app.py resume.txt
"""

import argparse
import sys

from resume_checker import check_resume, format_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resume-checker",
        description="Analyze a resume file and receive actionable feedback.",
    )
    parser.add_argument(
        "resume",
        help="Path to the resume file (.pdf, .docx, or .txt)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of a formatted report",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = check_resume(args.resume)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ImportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        import json
        import dataclasses

        print(json.dumps(dataclasses.asdict(result), indent=2))
    else:
        print(format_report(result))

    return 0


if __name__ == "__main__":
    sys.exit(main())
