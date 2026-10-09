#!/usr/bin/env python3
"""Check glossary.md and the glossary links in the notes.

Usage: python -I scripts/check_glossary.py

Checks:
- headings are in order: Latin first, then Cyrillic, case-insensitive;
- no duplicate headings;
- no slash, bracket, or colon in a heading (they break links);
- every [[glossary#...]] link in the Markdown files has an entry.
Text in fenced code blocks (``` ... ```) is skipped.
Exit code 1 if a problem is found.
"""
from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT  # noqa: E402

GLOSSARY = ROOT / "glossary.md"
SOURCES = ["README.md", "questions.md", "notes/**/*.md", "labs/**/*.md",
           "cheatsheets/**/*.md", "detections/**/*.md"]


def strip_fences(text: str) -> str:
    return re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)


def sort_key(heading: str) -> tuple:
    return (0 if heading[0].isascii() else 1, heading.lower())


def main() -> int:
    text = strip_fences(GLOSSARY.read_text(encoding="utf-8"))
    heads = re.findall(r"^## (.+)$", text, flags=re.M)
    problems = []
    for a, b in zip(heads, heads[1:]):
        if sort_key(a) > sort_key(b):
            problems.append(f'order: "{a}" is before "{b}"')
    for h, n in collections.Counter(heads).items():
        if n > 1:
            problems.append(f'duplicate heading: "{h}" ({n} times)')
    for h in heads:
        if re.search(r"[/:\[\]()]", h):
            problems.append(f'bad character in heading: "{h}"')
    known = set(heads)
    for pattern in SOURCES:
        for path in sorted(ROOT.glob(pattern)):
            body = strip_fences(path.read_text(encoding="utf-8"))
            for m in re.finditer(r"\[\[glossary#([^\]|]+)", body):
                if m.group(1) not in known:
                    rel = path.relative_to(ROOT).as_posix()
                    problems.append(f"{rel}: no entry for [[glossary#{m.group(1)}]]")
    print(f"headings: {len(heads)}")
    for p in problems:
        print(p)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
