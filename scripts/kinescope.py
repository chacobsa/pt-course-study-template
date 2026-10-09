#!/usr/bin/env python3
"""List or download the formats of a Kinescope video. Works on macOS and Windows.

yt-dlp has no Kinescope extractor. Its generic extractor breaks the signed URL
(&amp; instead of &) and gets error 403. This script reads the player page with
the LMS referer, takes the master.m3u8 URL, repairs it, and runs yt-dlp with it.

Usage:
    python -I scripts/kinescope.py <video id or embed URL>
        Prints the title and the length, then the formats with sizes (yt-dlp -F).
        Downloads nothing.
    python -I scripts/kinescope.py <video id> --download -f <video format>+<audio format> -o <file.mp4>
        Downloads the video and the audio and merges them into mp4 without re-encoding.

The signed URL works only for a short time. Never save it in the repository.
The script never prints the value of the `sign` parameter.
"""
from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_tool  # noqa: E402

LMS_REFERER = "https://lms.edu.ptsecurity.com/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def redact(text: str) -> str:
    return re.sub(r"(sign=)[^&\s\"'\\]+", r"\1REDACTED", text)


def video_id(arg: str) -> str:
    vid = arg.rstrip("/").rsplit("/", 1)[-1].split("?", 1)[0]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", vid):
        sys.exit(f"Not a Kinescope video id: {arg}")
    return vid


def fetch_player(vid: str) -> str:
    req = urllib.request.Request(f"https://kinescope.io/embed/{vid}",
                                 headers={"Referer": LMS_REFERER, "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError) as err:
        sys.exit(f"Could not read the player page: {err}")


def find_playlist(page: str) -> str:
    m = re.search(r"https?:[^\"'\s<>]+?master\.m3u8[^\"'\s<>]*", page)
    if not m:
        sys.exit("No master.m3u8 URL on the player page. Kinescope may have changed the page.")
    url = m.group(0).replace("\\u0026", "&").replace("\\/", "/")
    return html.unescape(url)


def find_info(page: str) -> tuple[str, str]:
    t = re.search(r"<title>([^<]*)</title>", page)
    title = html.unescape(t.group(1)).strip() if t else "?"
    d = re.search(r'"duration"\s*:\s*([\d.]+)', page)
    if not d:
        return title, "?"
    s = int(float(d.group(1)))
    return title, f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


def run_ytdlp(args: list[str]) -> int:
    tool = find_tool("yt-dlp")
    if not tool:
        sys.exit("yt-dlp not found. See SETUP.md, then run scripts/doctor.py")
    proc = subprocess.Popen([tool, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace")
    assert proc.stdout is not None
    for line in proc.stdout:
        print(redact(line), end="", flush=True)
    return proc.wait()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", help="Kinescope video id (data-videolazy-id) or embed URL")
    ap.add_argument("--download", action="store_true", help="download instead of listing the formats")
    ap.add_argument("-f", "--format", help="yt-dlp format, for example <video id>+<audio id>")
    ap.add_argument("-o", "--output", type=Path, help="output file (.mp4)")
    args = ap.parse_args()

    vid = video_id(args.video)
    page = fetch_player(vid)
    playlist = find_playlist(page)
    title, length = find_info(page)
    print(f"title: {title}\nlength: {length}")

    referer = ["--referer", f"https://kinescope.io/embed/{vid}"]
    if not args.download:
        return run_ytdlp([*referer, "-F", playlist])
    if not args.format or not args.output:
        sys.exit("--download needs -f <format> and -o <file>")
    if args.output.exists():
        sys.exit(f"Already exists: {args.output}")
    return run_ytdlp([*referer, "--newline", "-f", args.format, "--merge-output-format", "mp4",
                      "-o", str(args.output), playlist])


if __name__ == "__main__":
    sys.exit(main())
