#!/usr/bin/env python3
"""Validate that the launcher FFmpeg toolchain meets playback requirements."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LIBDIR = REPO_ROOT / "references" / "original-assets" / "quakelive"
REQUIRED_LIBS = ["avcodec-53.dll", "avformat-53.dll", "avutil-51.dll"]
SAMPLE_CLIP = Path(__file__).resolve().parent / "media" / "vp8_sample.webm"


def check_libraries(libdir: Path) -> list[str]:
    missing: list[str] = []
    for name in REQUIRED_LIBS:
        if not (libdir / name).exists():
            missing.append(name)
    return missing


def run_ffprobe(ffprobe: str, sample: Path) -> dict:
    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_streams",
        "-of",
        "json",
        str(sample),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe failed")
    return json.loads(result.stdout)


def main() -> int:
    libdir = Path(os.environ.get("FFMPEG_LAUNCHER_LIBDIR", DEFAULT_LIBDIR))
    missing = check_libraries(libdir)
    if missing:
        print(
            f"Missing FFmpeg runtime libraries in {libdir}: {', '.join(missing)}",
            file=sys.stderr,
        )
        return 1

    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        print("SKIP: ffprobe binary not available in PATH", file=sys.stderr)
        return 0

    if not SAMPLE_CLIP.exists():
        print(f"Sample clip missing: {SAMPLE_CLIP}", file=sys.stderr)
        return 1

    metadata = run_ffprobe(ffprobe, SAMPLE_CLIP)
    codecs = {stream.get("codec_type"): stream.get("codec_name") for stream in metadata.get("streams", [])}

    missing_streams = [key for key in ("video", "audio") if key not in codecs]
    if missing_streams:
        print(
            f"Sample clip lacks expected streams: {', '.join(missing_streams)}",
            file=sys.stderr,
        )
        return 1

    failures: list[str] = []
    if codecs.get("video") != "vp8":
        failures.append(f"Expected VP8 video stream, got {codecs.get('video')!r}")
    if codecs.get("audio") not in {"vorbis", "opus"}:
        failures.append(f"Expected Vorbis/Opus audio stream, got {codecs.get('audio')!r}")

    if failures:
        print("; ".join(failures), file=sys.stderr)
        return 1

    print("FFmpeg sample playback requirements satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
