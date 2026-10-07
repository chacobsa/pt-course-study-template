#!/usr/bin/env python3
"""Check that the tools and the hardware are ready. Prints OK / MISSING and the fix.

Usage: python scripts/doctor.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, find_obsidian, find_tool, has_nvidia_gpu, pick_whisper, system, whisper_cpp_model_path  # noqa: E402

OS = system()
HINTS = {
    "ffmpeg": {"Darwin": "brew install ffmpeg", "Windows": "winget install Gyan.FFmpeg", "Linux": "sudo apt install ffmpeg"},
    "yt-dlp": {"Darwin": "brew install yt-dlp", "Windows": "winget install yt-dlp.yt-dlp", "Linux": "pipx install yt-dlp"},
    "tshark": {"Darwin": "brew install --cask wireshark", "Windows": "winget install WiresharkFoundation.Wireshark", "Linux": "sudo apt install tshark"},
    "capinfos": {"Darwin": "comes with Wireshark", "Windows": "comes with Wireshark", "Linux": "sudo apt install wireshark-common"},
    "git": {"Darwin": "xcode-select --install", "Windows": "winget install Git.Git", "Linux": "sudo apt install git"},
    "obsidian": {"Darwin": "brew install --cask obsidian", "Windows": "winget install Obsidian.Obsidian", "Linux": "see obsidian.md/download"},
    "whisper-cli": {"Darwin": "brew install whisper-cpp", "Windows": "", "Linux": ""},
}

problems = 0


def report(ok: bool, label: str, detail: str = "", fix: str = "", required: bool = True) -> None:
    global problems
    mark = "OK     " if ok else ("MISSING" if required else "optional")
    line = f"[{mark}] {label}"
    if detail:
        line += f": {detail}"
    print(line)
    if not ok and fix:
        print(f"           fix: {fix}")
    if not ok and required:
        problems += 1


def course_profile() -> str:
    """Read 'Тип курса' from course.md. Empty string if not set yet."""
    f = ROOT / "course.md"
    if not f.exists():
        return ""
    import re
    m = re.search(r"Тип курса:\s*`?(\w+)`?", f.read_text(encoding="utf-8"))
    value = m.group(1).lower() if m else ""
    return value if value in ("network", "general", "attachments") else ""


def _has_module(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except ImportError:  # parent package missing
        return False


def check_tool(name: str, required: bool = True) -> None:
    path = find_tool(name)
    report(bool(path), name, path or "", HINTS.get(name, {}).get(OS, ""), required)


def main() -> None:
    print(f"System: {OS}, Python {sys.version.split()[0]}\n")

    py_ok = sys.version_info >= (3, 9)
    report(py_ok, "Python >= 3.9", fix="Install Python 3.12 from python.org or winget install Python.Python.3.12")
    if OS == "Windows" and sys.version_info >= (3, 13):
        print("           note: faster-whisper wheels may be missing for this Python. Python 3.12 is the safe choice.")

    for tool in ("git", "ffmpeg", "yt-dlp"):
        check_tool(tool)
    profile = course_profile()
    if profile in ("network", ""):  # Wireshark tools matter only for network courses
        check_tool("tshark", required=False)  # or the Wireshark GUI
        check_tool("capinfos", required=False)  # attachment_register.py has a built-in fallback

    obs = find_obsidian()
    report(bool(obs), "Obsidian (to read the notes)", obs or "", HINTS["obsidian"].get(OS, ""), required=False)

    print("\nSpeech to text:")
    plan = pick_whisper()
    gpu = has_nvidia_gpu()
    print(f"           NVIDIA GPU: {'yes' if gpu else 'no'}")
    print(f"           plan: engine={plan['backend']} model={plan['model']} device={plan['device']} ({plan['reason']})")
    if plan["backend"] == "whispercpp":
        check_tool("whisper-cli")
        model = whisper_cpp_model_path(plan["model"])
        report(model.exists(), "whisper.cpp model", str(model),
               f"download ggml-{plan['model']}.bin from huggingface.co/ggerganov/whisper.cpp into that folder (about 3 GB)")
    else:
        have = importlib.util.find_spec("faster_whisper") is not None
        report(have, "faster-whisper (Python package)", fix="pip install -r scripts/requirements.txt")
        if plan["device"] == "cuda":
            libs = all(_has_module(m) for m in ("nvidia.cublas", "nvidia.cudnn"))
            report(libs, "CUDA 12 libraries for faster-whisper", fix="pip install -r scripts/requirements-cuda.txt",
                   required=False)

    print("\nManual step (cannot be checked by this script):")
    print("           Russian root certificates (Минцифры): https://www.gosuslugi.ru/landing/crt")
    print("           Install them by hand, see SETUP.md step 0. Without them the LMS does not open.")

    print("\nProject:")
    course = (ROOT / "course.md").read_text(encoding="utf-8") if (ROOT / "course.md").exists() else ""
    print(f"           course profile: {course_profile() or 'not set'}")
    report("TODO" not in course, "course.md filled", fix="run /init-course in Claude Code", required=False)

    print()
    if problems:
        print(f"{problems} required item(s) missing. Install them, then run this script again.")
        sys.exit(1)
    print("Everything required is ready.")


if __name__ == "__main__":
    main()
