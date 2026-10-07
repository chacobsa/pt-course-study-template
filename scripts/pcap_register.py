#!/usr/bin/env python3
"""Register a downloaded PCAP file in sources/pcaps.csv.

Usage:
    python scripts/pcap_register.py pcaps/w1/m3905-network-vm-start.pcap \
        --material-id 3905 --week 1 --original-name 1.Network_VM_Start.pcap \
        --source-url "https://..."

Computes sha256 and size, reads packet count and duration with capinfos
(Wireshark), then tshark, then a built-in read-only parser as a last resort.
The file is only read, never opened by any other program and never changed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, find_tool  # noqa: E402

FIELDS = ["id", "material_id", "week", "original_name", "file", "sha256", "size",
          "packets", "duration", "source_url", "downloaded", "analyzed"]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stats_capinfos(path: Path):
    tool = find_tool("capinfos")
    if not tool:
        return None
    out = subprocess.run([tool, "-M", "-c", "-u", str(path)], capture_output=True, text=True)
    pk = re.search(r"Number of packets:\s+(\d+)", out.stdout)
    du = re.search(r"Capture duration:\s+([\d.]+)", out.stdout)
    if out.returncode == 0 and pk:
        return int(pk.group(1)), float(du.group(1)) if du else 0.0
    return None


def stats_tshark(path: Path):
    tool = find_tool("tshark")
    if not tool:
        return None
    out = subprocess.run([tool, "-r", str(path), "-T", "fields", "-e", "frame.time_epoch"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return None
    times = [float(x) for x in out.stdout.split() if x]
    if not times:
        return 0, 0.0
    return len(times), max(times) - min(times)


def stats_builtin(path: Path):
    """Minimal read-only parser for classic pcap and pcapng (default time resolution)."""
    data = path.read_bytes()
    magic = data[:4]
    times: list[float] = []
    classic = {b"\xd4\xc3\xb2\xa1": ("<", 1e-6), b"\xa1\xb2\xc3\xd4": (">", 1e-6),
               b"\x4d\x3c\xb2\xa1": ("<", 1e-9), b"\xa1\xb2\x3c\x4d": (">", 1e-9)}
    if magic in classic:
        end, res = classic[magic]
        pos = 24
        while pos + 16 <= len(data):
            sec, frac, incl, _orig = struct.unpack_from(end + "IIII", data, pos)
            times.append(sec + frac * res)
            pos += 16 + incl
    elif magic == b"\x0a\x0d\x0d\x0a":
        end = "<" if data[8:12] == b"\x4d\x3c\x2b\x1a" else ">"
        pos = 0
        while pos + 12 <= len(data):
            btype, blen = struct.unpack_from(end + "II", data, pos)
            if blen < 12:
                break
            if btype == 6 and pos + 20 <= len(data):  # Enhanced Packet Block
                hi, lo = struct.unpack_from(end + "II", data, pos + 12)
                times.append(((hi << 32) | lo) * 1e-6)
            elif btype == 3:  # Simple Packet Block, no timestamp
                times.append(0.0)
            pos += blen
    else:
        return None
    if not times:
        return 0, 0.0
    return len(times), max(times) - min(times)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", type=Path)
    ap.add_argument("--material-id", required=True)
    ap.add_argument("--week", required=True)
    ap.add_argument("--original-name", required=True, help="file name as in the course text")
    ap.add_argument("--source-url", default="")
    args = ap.parse_args()

    path = args.file.resolve()
    if not path.exists():
        sys.exit(f"File not found: {path}")
    try:
        rel = path.relative_to(ROOT).as_posix()
    except ValueError:
        sys.exit("The file must be inside this repository (pcaps/<week>/).")

    digest = sha256_of(path)
    csv_path = ROOT / "sources" / "pcaps.csv"
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8", newline="")))
    for r in rows:
        if r["sha256"] == digest:
            sys.exit(f"Already registered: row {r['id']} ({r['file']})")

    stats = stats_capinfos(path) or stats_tshark(path) or stats_builtin(path)
    if stats is None:
        packets, duration = "", ""
        print("Warning: could not read packets and duration. Fill them by hand.", file=sys.stderr)
    else:
        packets, duration = stats[0], f"{stats[1]:.2f}"

    next_id = max([int(r["id"]) for r in rows if r["id"].isdigit()] + [0]) + 1
    row = {"id": next_id, "material_id": args.material_id, "week": args.week,
           "original_name": args.original_name, "file": rel, "sha256": digest,
           "size": path.stat().st_size, "packets": packets, "duration": duration,
           "source_url": args.source_url, "downloaded": "yes", "analyzed": "no"}
    with csv_path.open("a", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n").writerow(row)
    print(f"Registered row {next_id}: {rel}  packets={packets} duration={duration}s")


if __name__ == "__main__":
    main()
