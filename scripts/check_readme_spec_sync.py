#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

SPEC_HEADER = "# Chore Dispatcher System - Technical Specification"
README_SECTION = "## Technical Specification"


def extract_spec_text(readme_text: str) -> str:
    if README_SECTION not in readme_text:
        return ""
    section_start = readme_text.index(README_SECTION)
    spec_start = readme_text.index(SPEC_HEADER, section_start)
    return readme_text[spec_start:].strip()


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    readme_path = repo_root / "README.md"
    spec_path = repo_root / "chore_dispatcher_3.0_technical_spec.md"

    readme_text = readme_path.read_text(encoding="utf-8")
    spec_text = spec_path.read_text(encoding="utf-8").strip()

    embedded = extract_spec_text(readme_text)
    if not embedded:
        print("README.md is missing the Technical Specification section")
        return 1

    if embedded != spec_text:
        print("README.md technical spec is out of sync with chore_dispatcher_3.0_technical_spec.md")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
