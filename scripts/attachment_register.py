#!/usr/bin/env python3
"""Register a downloaded course attachment in sources/attachments.csv.

Usage:
    python -I scripts/attachment_register.py attachments/w1/m3905-network-vm-start.pcap \
        --material-id 3905 --week 1 --original-name 1.Network_VM_Start.pcap \
        --source-url "https://..."
    python -I scripts/attachment_register.py <file anywhere> --dry-run
        Shows the kind, sha256, size and meta, and checks for a duplicate. Writes nothing.
        Use it on a fresh download in the scratchpad, before you name and move the file.

Always computes sha256 and size. Detects the kind from the extension and the first
bytes: pcap, archive, binary, dataset, vm-image, document, other (or use --kind).
Extra data goes to the `meta` column as JSON:
    pcap     format (pcap or pcapng), packets, duration in seconds
             (capinfos, then tshark, then a built-in parser)
    archive  entries, encrypted, unsafe_paths (zip and tar: the file LIST only)
The file is only read. It is never run, unpacked, mounted or changed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, find_tool  # noqa: E402

FIELDS = ["id", "material_id", "week", "kind", "original_name", "file", "sha256", "size",
          "meta", "source_url", "downloaded", "analyzed"]
KINDS = ["pcap", "archive", "binary", "dataset", "vm-image", "document", "other"]

EXT_KIND = {
    "pcap": {".pcap", ".pcapng", ".cap"},
    "archive": {".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".rar", ".zst"},
    "binary": {".exe", ".dll", ".sys", ".so", ".elf", ".bin", ".msi", ".apk", ".dylib", ".o", ".ko"},
    "dataset": {".csv", ".tsv", ".json", ".jsonl", ".log", ".evtx", ".db", ".sqlite", ".parquet"},
    "vm-image": {".ova", ".ovf", ".vmdk", ".vdi", ".qcow2", ".iso", ".img", ".vhd", ".vhdx"},
    "document": {".pdf", ".doc", ".docx", ".odt", ".txt", ".md", ".xls", ".xlsx", ".ppt", ".pptx"},
}
MAGIC_KIND = [
    (b"\xd4\xc3\xb2\xa1", "pcap"), (b"\xa1\xb2\xc3\xd4", "pcap"),
    (b"\x4d\x3c\xb2\xa1", "pcap"), (b"\xa1\xb2\x3c\x4d", "pcap"), (b"\x0a\x0d\x0d\x0a", "pcap"),
    (b"PK\x03\x04", "archive"), (b"7z\xbc\xaf\x27\x1c", "archive"), (b"Rar!", "archive"),
    (b"\x1f\x8b", "archive"), (b"BZh", "archive"), (b"\xfd7zXZ", "archive"),
    (b"MZ", "binary"), (b"\x7fELF", "binary"),
    (b"\xcf\xfa\xed\xfe", "binary"), (b"\xca\xfe\xba\xbe", "binary"),
    (b"%PDF", "document"),
]
MAX_ENTRIES = 200_000  # stop counting after this many names (protects from huge archives)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def detect_kind(path: Path) -> str:
    with path.open("rb") as f:
        head = f.read(8)
    for magic, kind in MAGIC_KIND:
        if head.startswith(magic):
            return kind
    ext = path.suffix.lower()
    for kind, exts in EXT_KIND.items():
        if ext in exts:
            return kind
    return "other"


# ---------- pcap ----------

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


def pcap_format(path: Path) -> str:
    with path.open("rb") as f:
        return "pcapng" if f.read(4) == b"\x0a\x0d\x0d\x0a" else "pcap"


def meta_pcap(path: Path) -> dict:
    meta: dict = {"format": pcap_format(path)}
    want = ".pcapng" if meta["format"] == "pcapng" else ".pcap"
    if path.suffix.lower() in (".pcap", ".pcapng") and path.suffix.lower() != want:
        print(f"Warning: the file is {meta['format']}, but the extension is {path.suffix}. "
              f"Use {want} in the local name.", file=sys.stderr)
    stats = stats_capinfos(path) or stats_tshark(path) or stats_builtin(path)
    if stats is None:
        print("Warning: could not read packets and duration. Fill them by hand.", file=sys.stderr)
        return meta
    meta.update({"packets": stats[0], "duration": round(stats[1], 2)})
    return meta


# ---------- archive: list names only, never extract ----------

def _unsafe(name: str) -> bool:
    n = name.replace("\\", "/")
    return n.startswith("/") or re.match(r"^[A-Za-z]:", n) is not None or ".." in n.split("/")


def meta_archive(path: Path) -> dict:
    names: list[str] = []
    meta: dict = {}
    try:
        if zipfile.is_zipfile(path):
            meta["format"] = "zip"
            with zipfile.ZipFile(path) as z:
                infos = z.infolist()
                names = [i.filename for i in infos[:MAX_ENTRIES]]
                meta["entries"] = len(infos)
                meta["encrypted"] = any(i.flag_bits & 0x1 for i in infos)
        elif tarfile.is_tarfile(path):
            meta["format"] = "tar"
            with tarfile.open(path) as t:
                for i, m in enumerate(t):
                    if i >= MAX_ENTRIES:
                        meta["truncated"] = True
                        break
                    names.append(m.name)
            meta["entries"] = len(names)
        else:
            meta["note"] = "listing not available (7z, rar and others): use a read-only 'list' command by hand"
            return meta
    except (OSError, zipfile.BadZipFile, tarfile.TarError, EOFError) as err:
        meta["note"] = f"could not list: {err}"
        return meta
    if any(_unsafe(n) for n in names):
        meta["unsafe_paths"] = True  # absolute paths or '..': never extract this archive blindly
    return meta


def build_meta(kind: str, path: Path) -> dict:
    if kind == "pcap":
        return meta_pcap(path)
    if kind == "archive":
        return meta_archive(path)
    return {}


def notes_for(meta: dict) -> None:
    if meta.get("unsafe_paths"):
        print("Warning: the archive has absolute or '..' paths. Do not extract it outside a lab VM.", file=sys.stderr)
    if meta.get("encrypted"):
        print("Note: the archive is password-protected. Take the password from the material text, never guess it.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", type=Path)
    ap.add_argument("--material-id")
    ap.add_argument("--week")
    ap.add_argument("--original-name", help="file name as in the course text")
    ap.add_argument("--source-url", default="")
    ap.add_argument("--kind", choices=KINDS, help="override the detected kind")
    ap.add_argument("--dry-run", action="store_true", help="show what would be registered; write nothing")
    args = ap.parse_args()

    path = args.file.resolve()
    if not path.is_file():
        sys.exit(f"File not found: {path}")

    digest = sha256_of(path)
    csv_path = ROOT / "sources" / "attachments.csv"
    with csv_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    duplicate = next((r for r in rows if r["sha256"] == digest), None)
    kind = args.kind or detect_kind(path)
    meta = build_meta(kind, path)
    meta_json = json.dumps(meta, ensure_ascii=False, separators=(",", ":"))

    if args.dry_run:
        print(f"file={path.name}  kind={kind}  size={path.stat().st_size}\nsha256={digest}\nmeta={meta_json}")
        if duplicate:
            print(f"Already registered: row {duplicate['id']} ({duplicate['file']})")
        notes_for(meta)
        print("Dry run: nothing written.")
        return

    missing = [f"--{n.replace('_', '-')}" for n in ("material_id", "week", "original_name") if not getattr(args, n)]
    if missing:
        sys.exit("Missing: " + ", ".join(missing))
    try:
        rel = path.relative_to(ROOT).as_posix()
    except ValueError:
        sys.exit("The file must be inside this repository (attachments/<week>/).")
    if not rel.startswith("attachments/"):
        sys.exit("Save the file in attachments/<week>/ first.")
    if "incoming" in rel.split("/"):
        sys.exit("Move the file out of incoming/ to attachments/<week>/ and give it its local name first.")
    if duplicate:
        sys.exit(f"Already registered: row {duplicate['id']} ({duplicate['file']})")

    next_id = max([int(r["id"]) for r in rows if r["id"].isdigit()] + [0]) + 1
    row = {"id": next_id, "material_id": args.material_id, "week": args.week, "kind": kind,
           "original_name": args.original_name, "file": rel, "sha256": digest,
           "size": path.stat().st_size, "meta": meta_json,
           "source_url": args.source_url, "downloaded": "yes", "analyzed": "no"}
    with csv_path.open("a", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n").writerow(row)
    print(f"Registered row {next_id}: {rel}  kind={kind}  meta={meta_json}")
    notes_for(meta)


if __name__ == "__main__":
    main()
