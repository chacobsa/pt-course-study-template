#!/usr/bin/env python3
"""Find and fix speech-to-text errors in a transcript. Works the same on macOS and Windows.

Usage:
    python -I scripts/transcript_fix.py scan <transcript>
        Lists the lines with a known error from whisper-fixes.md and the runs of
        repeated lines (a Whisper loop). Changes nothing.

    python -I scripts/transcript_fix.py apply <transcript> <fixes.txt>
        Shows the diff. Changes nothing.
    python -I scripts/transcript_fix.py apply <transcript> <fixes.txt> --write --backup <raw copy>
        Copies the transcript to <raw copy> (it must not exist), then writes the fixes.

The fixes file has one replacement per line:  old phrase => new phrase
Empty lines and lines that start with # are skipped. Replacements run in file order.
A phrase matches only as whole words, with the exact case.
The script stops and writes nothing if a phrase is not found or the number of lines changes.
"""
from __future__ import annotations

import argparse
import difflib
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT  # noqa: E402

FIXES_TABLE = ROOT / "whisper-fixes.md"
MIN_REPEAT = 3  # report runs of this many identical lines or more


def phrase_re(phrase: str, ignore_case: bool = False) -> re.Pattern:
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", flags)


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


# ---------- scan ----------

def load_table() -> list[tuple[str, str]]:
    """Pairs (wrong variant, correct) from the table in whisper-fixes.md."""
    if not FIXES_TABLE.exists():
        sys.exit(f"Not found: {FIXES_TABLE}")
    pairs = []
    rows = [l for l in FIXES_TABLE.read_text(encoding="utf-8").splitlines() if l.startswith("|")]
    for row in rows[1:]:  # the first row is the header
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= set("-: "):
            continue  # separator row
        for variant in cells[0].split(","):
            variant = variant.strip()
            if variant:
                pairs.append((variant, cells[1]))
    return pairs


def repeated_runs(lines: list[str]) -> list[tuple[int, int, str]]:
    runs, start = [], 0
    for i in range(1, len(lines) + 1):
        if i == len(lines) or lines[i].strip() != lines[start].strip():
            if i - start >= MIN_REPEAT and lines[start].strip():
                runs.append((start + 1, i, lines[start].strip()))
            start = i
    return runs


def scan(path: Path) -> int:
    lines = read_lines(path)
    patterns = [(variant, correct, phrase_re(variant, ignore_case=True)) for variant, correct in load_table()]
    hits = 0
    for n, line in enumerate(lines, 1):
        for variant, correct, rx in patterns:
            if rx.search(line):
                hits += 1
                print(f"{n}: {variant} -> {correct} | {line.strip()[:120]}")
    runs = repeated_runs(lines)
    for first, last, text in runs:
        print(f"repeat: lines {first}-{last} are the same: {text[:80]}")
    print(f"lines: {len(lines)}; known errors: {hits}; repeated runs: {len(runs)}")
    print("Check each hit by meaning. Fix only clear errors (see AGENTS.md).")
    return 0


# ---------- apply ----------

def load_fixes(path: Path) -> list[tuple[str, str]]:
    fixes = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if " => " not in line:
            sys.exit(f"{path}:{n}: no ' => ' separator")
        old, new = (s.strip() for s in line.split(" => ", 1))
        if not old:
            sys.exit(f"{path}:{n}: empty old phrase")
        fixes.append((old, new))
    if not fixes:
        sys.exit(f"{path}: no replacements")
    return fixes


def apply(path: Path, fixes_path: Path, write: bool, backup: Path | None) -> int:
    lines = read_lines(path)
    new_lines = list(lines)
    problems = []
    for old, new in load_fixes(fixes_path):
        rx = phrase_re(old)
        count = 0
        for i, line in enumerate(new_lines):
            new_lines[i], k = rx.subn(lambda _m: new, line)
            count += k
        print(f"{count:4d} x  {old} => {new}")
        if count == 0:
            problems.append(f'not found: "{old}"')
    if len(new_lines) != len(lines) or "".join(new_lines).count("\n") != "".join(lines).count("\n"):
        problems.append("the number of lines changed")
    diff = difflib.unified_diff(lines, new_lines, fromfile=f"{path.name} (raw)", tofile=f"{path.name} (fixed)", n=0)
    sys.stdout.writelines(diff)
    changed = sum(1 for a, b in zip(lines, new_lines) if a != b)
    print(f"\nlines: {len(lines)}; changed lines: {changed}")
    if problems:
        for p in problems:
            print(p)
        print("Nothing written.")
        return 1
    if not write:
        print("Dry run: nothing written. Add --write --backup <file> to save.")
        return 0
    if backup is None:
        sys.exit("--write needs --backup <file> for the raw copy")
    if backup.exists():
        sys.exit(f"Backup already exists: {backup}")
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, backup)
    with path.open("w", encoding="utf-8", newline="\n") as f:  # LF also on Windows
        f.write("".join(new_lines))
    print(f"Written: {path}\nRaw copy: {backup}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan", help="list known errors and repeated lines")
    s.add_argument("transcript", type=Path)
    a = sub.add_parser("apply", help="replace whole phrases from a fixes file")
    a.add_argument("transcript", type=Path)
    a.add_argument("fixes", type=Path)
    a.add_argument("--write", action="store_true", help="save the result into the transcript")
    a.add_argument("--backup", type=Path, help="where to copy the raw transcript first (required with --write)")
    args = ap.parse_args()
    if not args.transcript.is_file():
        sys.exit(f"Not found: {args.transcript}")
    if args.cmd == "scan":
        return scan(args.transcript)
    return apply(args.transcript, args.fixes, args.write, args.backup)


if __name__ == "__main__":
    sys.exit(main())
