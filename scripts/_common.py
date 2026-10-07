"""Shared helpers: tool lookup and hardware detection. Works on macOS, Windows, Linux."""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Places where Windows installers put tools that are often not in PATH.
_WIN_EXTRA = [
    Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Wireshark",
    Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Wireshark",
]


def system() -> str:
    """'Darwin', 'Windows' or 'Linux'."""
    return platform.system()


def find_tool(name: str) -> str | None:
    """Return the full path of a tool, or None."""
    found = shutil.which(name)
    if found:
        return found
    if system() == "Windows":
        for folder in _WIN_EXTRA:
            for ext in (".exe", ""):
                candidate = folder / (name + ext)
                if candidate.exists():
                    return str(candidate)
    return None


def find_obsidian() -> str | None:
    """Return the path of an installed Obsidian, or None. Only looks, never changes anything."""
    candidates: list[Path] = []
    if system() == "Darwin":
        candidates = [Path("/Applications/Obsidian.app"), Path.home() / "Applications" / "Obsidian.app"]
    elif system() == "Windows":
        local = Path(os.environ.get("LOCALAPPDATA", ""))
        for base in (local / "Programs" / "Obsidian",
                     Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Obsidian"):
            candidates.append(base / "Obsidian.exe")
    else:
        found = shutil.which("obsidian")
        return found
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def has_nvidia_gpu() -> bool:
    smi = find_tool("nvidia-smi")
    if not smi:
        return False
    try:
        out = subprocess.run([smi, "-L"], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return False
    return out.returncode == 0 and "GPU" in out.stdout


def is_apple_silicon() -> bool:
    return system() == "Darwin" and platform.machine() == "arm64"


def whisper_cpp_model_path(model: str = "large-v3") -> Path:
    return Path.home() / ".cache" / "whisper-cpp" / f"ggml-{model}.bin"


def pick_whisper() -> dict:
    """Choose the speech-to-text engine and the model by the hardware.

    Override with env vars WHISPER_BACKEND (whispercpp | faster-whisper)
    and WHISPER_MODEL (for example large-v3, medium, small).
    Returns: backend, model, device, compute_type, reason.
    """
    backend = os.environ.get("WHISPER_BACKEND", "").strip().lower()
    model = os.environ.get("WHISPER_MODEL", "").strip()

    if backend in ("whisper.cpp", "whisper-cpp"):
        backend = "whispercpp"

    if not backend:
        if system() == "Darwin" and find_tool("whisper-cli"):
            backend, device, compute, why = "whispercpp", "metal", "", "macOS: whisper.cpp uses Metal"
        elif has_nvidia_gpu():
            backend, device, compute, why = "faster-whisper", "cuda", "float16", "NVIDIA GPU found"
        else:
            backend, device, compute, why = "faster-whisper", "cpu", "int8", "no GPU: CPU with a smaller model"
        default_model = "large-v3" if device in ("metal", "cuda") else "medium"
    else:
        # Manual backend: still detect the device for faster-whisper.
        if backend == "faster-whisper" and has_nvidia_gpu():
            device, compute = "cuda", "float16"
        elif backend == "faster-whisper":
            device, compute = "cpu", "int8"
        else:
            device, compute = "metal" if system() == "Darwin" else "cpu", ""
        why = "backend set by WHISPER_BACKEND"
        default_model = "large-v3" if device in ("metal", "cuda") else "medium"

    return {
        "backend": backend,
        "model": model or default_model,
        "device": device,
        "compute_type": compute,
        "reason": why + ("; model set by WHISPER_MODEL" if model else ""),
    }


def python_cmd() -> str:
    return "python" if system() == "Windows" else Path(sys.executable).name
