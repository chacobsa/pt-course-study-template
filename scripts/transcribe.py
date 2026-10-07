#!/usr/bin/env python3
"""Make a Russian transcript from a course video.

Usage:
    python scripts/transcribe.py media/w1/m3989-why-analyze-traffic.mp4 [--dry-run]

Writes transcripts/<week>/<name>.ru.txt (plain text, one segment per line).
The temporary 16 kHz audio is deleted at the end.

Engine and model are chosen by the hardware (see _common.pick_whisper):
    macOS            -> whisper.cpp (whisper-cli), large-v3, Metal
    NVIDIA GPU       -> faster-whisper, large-v3, CUDA, float16
    no GPU           -> faster-whisper, medium, CPU, int8
Override: WHISPER_BACKEND=whispercpp|faster-whisper, WHISPER_MODEL=large-v3|medium|small
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, find_tool, pick_whisper, whisper_cpp_model_path  # noqa: E402


def extract_audio(video: Path, wav: Path) -> None:
    ffmpeg = find_tool("ffmpeg")
    if not ffmpeg:
        sys.exit("ffmpeg not found. See SETUP.md, then run scripts/doctor.py")
    subprocess.run(
        [ffmpeg, "-y", "-loglevel", "error", "-i", str(video), "-vn", "-ac", "1",
         "-ar", "16000", "-c:a", "pcm_s16le", str(wav)],
        check=True,
    )


def run_whispercpp(wav: Path, out_base: Path, model: str) -> Path:
    cli = find_tool("whisper-cli")
    model_path = whisper_cpp_model_path(model)
    if not cli:
        sys.exit("whisper-cli not found. Install whisper.cpp (brew install whisper-cpp).")
    if not model_path.exists():
        sys.exit(f"Model file not found: {model_path}")
    # -mc 0 stops context carry-over (prevents repeat loops); -sns drops non-speech tokens
    subprocess.run(
        [cli, "-m", str(model_path), "-l", "ru", "-mc", "0", "-sns",
         "-f", str(wav), "-otxt", "-of", str(out_base)],
        check=True, stdout=subprocess.DEVNULL,
    )
    return out_base.with_name(out_base.name + ".txt")


def add_cuda_dll_dirs() -> None:
    """On Windows, pip-installed CUDA DLLs (nvidia-cublas-cu12, nvidia-cudnn-cu12) are not in the DLL path."""
    if sys.platform != "win32":
        return
    import os
    import site
    for base in site.getsitepackages() + [site.getusersitepackages()]:
        for pkg in ("cublas", "cudnn"):
            d = Path(base) / "nvidia" / pkg / "bin"
            if d.is_dir():
                os.add_dll_directory(str(d))
                os.environ["PATH"] = str(d) + os.pathsep + os.environ.get("PATH", "")


def run_faster_whisper(wav: Path, out_txt: Path, model: str, device: str, compute: str) -> Path:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("faster-whisper is not installed. Run: pip install -r scripts/requirements.txt")
    if device == "cuda":
        add_cuda_dll_dirs()
    wm = WhisperModel(model, device=device, compute_type=compute)
    # condition_on_previous_text=False prevents repeat loops (same idea as -mc 0 in whisper.cpp)
    segments, _info = wm.transcribe(
        str(wav), language="ru", condition_on_previous_text=False, vad_filter=True
    )
    with out_txt.open("w", encoding="utf-8", newline="\n") as f:
        for seg in segments:
            text = seg.text.strip()
            if text:
                f.write(text + "\n")
    return out_txt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("--dry-run", action="store_true", help="show the choice and exit")
    args = ap.parse_args()

    video = args.video.resolve()
    if not video.exists():
        sys.exit(f"Video not found: {video}")
    week = video.parent.name
    name = video.stem
    out_dir = ROOT / "transcripts" / week
    out_txt = out_dir / f"{name}.ru.txt"

    plan = pick_whisper()
    print(f"engine={plan['backend']} model={plan['model']} device={plan['device']} "
          f"({plan['reason']})")
    print(f"output={out_txt}")
    if args.dry_run:
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="transcribe-") as tmp:  # temporary audio, never kept
        wav = Path(tmp) / f"{name}.16k.wav"
        extract_audio(video, wav)
        if plan["backend"] == "whispercpp":
            result = run_whispercpp(wav, out_dir / f"{name}.ru", plan["model"])
        else:
            try:
                result = run_faster_whisper(wav, out_txt, plan["model"], plan["device"], plan["compute_type"])
            except Exception as err:  # CUDA libraries missing is the common case on Windows
                if plan["device"] != "cuda":
                    raise
                print(f"GPU run failed ({err}). Falling back to CPU, model medium.", file=sys.stderr)
                result = run_faster_whisper(wav, out_txt, "medium", "cpu", "int8")
    print(result)


if __name__ == "__main__":
    main()
