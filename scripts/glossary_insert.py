#!/usr/bin/env python3
"""Insert new glossary entries. Old lines stay as they are.

Usage:
    python -I scripts/glossary_insert.py <blocks.md> <glossary.md> <out.md>

The blocks file has groups like this:

    @@BEFORE ARP
    ## Anycast gateway
    - **Что это:** ...

    @@END
    ## Шлюз по умолчанию
    - **Что это:** ...

@@BEFORE <heading> inserts the group before the line "## <heading>". The heading
must exist exactly once outside fenced code blocks (the sample entry is skipped). @@END appends the group at the end of the file (use it for
the first entry and for entries after the last heading in the alphabet).
Each group must start with a "## " heading.

The script writes a new file and checks that no old line was changed or removed.
Read the result, run scripts/check_glossary.py on it, then replace glossary.md.
"""
from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path


def heading_positions(text: str, anchor: str) -> list[int]:
    """Start positions of the line "## <anchor>" outside fenced code blocks."""
    fences = [m.span() for m in re.finditer(r"^```.*?^```", text, flags=re.S | re.M)]
    found = []
    for m in re.finditer(r"^## " + re.escape(anchor) + r"[ \t]*$", text, flags=re.M):
        if not any(a <= m.start() < b for a, b in fences):
            found.append(m.start())
    return found


def main(blocks_path: str, src: str, out: str) -> None:
    old_text = Path(src).read_text(encoding="utf-8")
    text = old_text
    raw = Path(blocks_path).read_text(encoding="utf-8")
    parts = re.split(r"^@@(BEFORE .+|END)[ \t]*\n", raw, flags=re.M)
    if parts[0].strip():
        sys.exit("text before the first @@BEFORE or @@END marker")
    added = 0
    for marker, block in zip(parts[1::2], parts[2::2]):
        block = block.strip("\n") + "\n"
        if not block.startswith("## "):
            sys.exit(f'group after "@@{marker}" does not start with a "## " heading')
        if marker == "END":
            text = text.rstrip("\n") + "\n\n" + block
        else:
            anchor = marker[len("BEFORE "):].strip()
            found = heading_positions(text, anchor)
            if len(found) != 1:
                sys.exit(f'heading "{anchor}" found {len(found)} times, need exactly 1')
            i = found[0]
            text = text[:i] + block + "\n" + text[i:]
        added += len(re.findall(r"^## ", block, flags=re.M))
    removed = [l for l in difflib.ndiff(old_text.splitlines(), text.splitlines()) if l.startswith("- ")]
    if removed:
        sys.exit("old lines changed or removed:\n" + "\n".join(removed[:20]))
    with open(out, "w", encoding="utf-8", newline="\n") as f:  # LF also on Windows
        f.write(text)
    print(f"entries added: {added}; old lines changed: 0; written to {out}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
