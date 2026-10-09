#!/usr/bin/env python3
"""Check that every [[wikilink]] points to an existing note.

Usage: python -I scripts/check_links.py

- Links to the glossary ([[glossary#...]]) are checked by check_glossary.py.
- Text in `code` and in fenced code blocks is skipped.
- Hidden folders (.obsidian, .claude) and templates/ are skipped.
- A link like [[IDS]] to a note that does not exist is reported.
  Terms must link to the glossary: [[glossary#IDS|IDS]].
Exit code 1 if a problem is found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT  # noqa: E402

SKIP_DIRS = {"templates"}


def note_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*.md"):
        parts = path.relative_to(ROOT).parts
        if any(p.startswith(".") for p in parts) or parts[0] in SKIP_DIRS:
            continue
        files.append(path)
    return sorted(files)


def main() -> int:
    files = note_files()
    names = {p.stem for p in files}
    problems = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)
        text = re.sub(r"`[^`\n]*`", "", text)
        for m in re.finditer(r"\[\[([^\]#|]*)", text):
            name = m.group(1).strip()
            if name and name not in names:
                problems.append(f"{path.relative_to(ROOT).as_posix()}: [[{name}]] has no note")
    for p in problems:
        print(p)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
