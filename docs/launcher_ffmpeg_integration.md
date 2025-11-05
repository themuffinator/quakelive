# Launcher FFmpeg Integration Audit & Refactor Plan

## 1. Current Usage Snapshot

The proprietary Quake Live launcher embeds Awesomium (Chromium 18) and relies on
its bundled FFmpeg glue to decode HTML5 media. Extracted strings from the
reference `awesomium.dll` expose the concrete decoder entry points and codecs in
use, including VP8/Vorbis demuxing and the H.264 bitstream converter.
【F:references/analysis/awesomium_ffmpeg_strings.txt†L2-L16】 These routines sit
outside the GPL engine today, so launcher videos render in Chromium surfaces
instead of inside Quake III renderer targets.

The GPL tree still exposes the legacy RoQ cinematic pipeline through
`CIN_PlayCinematic`, `CIN_RunCinematic`, and `CIN_DrawCinematic`. Those routines
manage 512×512 scratch images, drive the `videoMap` shader keyword, and stream
RoQ frames through `cl_cin.c` and the renderer bundles. 【F:src/code/client/cl_cin.c†L1481-L1566】【F:src/code/renderer/tr_shader.c†L697-L709】
Because launcher cinematics are isolated inside Awesomium, they never reach
these shared scratch textures and cannot be overlaid with the in-game UI or
post-processing effects.

## 2. Codec & Performance Requirements

* **Codec coverage.** Awesomium ships VP8/Vorbis WebM playback and hooks for
  H.264 bitstream conversion. 【F:references/analysis/awesomium_ffmpeg_strings.txt†L6-L16】 To preserve launcher parity we must
  preserve at least VP8 video with Vorbis audio and baseline H.264/AVC decode.
* **Surface size.** The cinematic bridge expects 256×256 or 512×512 textures and
  allocates 16 playback handles. 【F:src/code/client/cl_cin.c†L1481-L1597】 The new
  FFmpeg path should stream frames into these scratch slots, matching the
  `videoMap` shader handshake for live materials. 【F:src/code/renderer/tr_shader.c†L697-L709】
* **Throughput.** RoQ playback runs at ~30 fps with small buffers. The refactor
  must sustain 60 fps for VP8/H.264 at 720p without blocking the renderer thread;
  demuxing should occur on the existing background streaming worker introduced
  by `Sys_BeginStreamedFile`. 【F:src/code/client/cl_cin.c†L1500-L1559】

## 3. Redistributable FFmpeg Build

The repository ships `tools/ffmpeg/build-minimal.sh`, a decoder-only
configuration that remains redistributable under LGPL/GPL terms while covering
the required codecs. Invoke it from your CI system or local shell.

```bash
#!/usr/bin/env bash
# tools/ffmpeg/build-minimal.sh
set -euo pipefail
PREFIX="${1:-$PWD/out}"
COMMON_FLAGS=(
  --disable-programs
  --disable-doc
  --disable-debug
  --disable-network
  --disable-everything
  --enable-protocol=file
  --enable-demuxer=matroska
  --enable-parser=vp8
  --enable-parser=h264
  --enable-decoder=vp8
  --enable-decoder=h264
  --enable-decoder=aac
  --enable-decoder=vorbis
  --enable-decoder=opus
  --enable-decoder=pcm_s16le
  --enable-decoder=pcm_s16be
  --enable-decoder=pcm_u16le
  --enable-decoder=theora
  --enable-decoder=flac
  --enable-demuxer=ogg
  --enable-demuxer=mov
  --enable-demuxer=mp4
  --enable-demuxer=avi
  --enable-demuxer=wav
  --enable-demuxer=flac
  --enable-demuxer=matroska
  --enable-filter=scale
  --enable-gpl
)

case "${TARGET_OS:-$(uname -s)}" in
  MINGW*|MSYS*|CYGWIN*|Windows_NT)
    ./configure "${COMMON_FLAGS[@]}" --toolchain=msvc --prefix="$PREFIX"
    ;;
  Darwin)
    ./configure "${COMMON_FLAGS[@]}" --cc=clang --cxx=clang++ \
      --arch=x86_64 --enable-cross-compile --prefix="$PREFIX"
    ;;
  Linux)
    ./configure "${COMMON_FLAGS[@]}" --cc=gcc --cxx=g++ --prefix="$PREFIX"
    ;;
  *)
    echo "Unsupported host $TARGET_OS" >&2
    exit 1
    ;;
esac

make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
make install
```

Key properties:

* **Decoder-only footprint.** `--disable-everything` followed by targeted
  `--enable-decoder`/`--enable-demuxer` flags trims unused encoders so the
  runtime mirrors the legacy launcher.
* **Web codecs.** VP8, Vorbis, Opus, and Theora satisfy HTML5 playback while
  H.264 and AAC cover user-generated MP4 uploads.
* **Redistributable binaries.** The build depends solely on FFmpeg's built-in
  decoders, avoiding non-free libraries while remaining GPL-compatible.

## 4. Engine Playback Refactor

1. **New decoder shim.** Introduce `FFmpegCinematic` alongside the existing RoQ
   implementation. It should expose the same `CIN_*` entry points but stream
   frames via FFmpeg’s demuxer/decoder API. Each decoded frame lands in the
   existing scratch image array so render stages driven by `videoMap` continue to
   work. 【F:src/code/renderer/tr_shader.c†L697-L709】
2. **Shared streaming worker.** Reuse the streaming file API (`Sys_BeginStreamedFile`)
   so background demux keeps pace with 60 fps playback without stalling the main
   thread. The RoQ path already primes this worker. 【F:src/code/client/cl_cin.c†L1500-L1559】
3. **UI integration.** Expose a VM call that lets the Quake Live UI trigger
   cinematic playback directly. The HTML widgets can then be reimplemented with
   native menus that attach to shared renderer surfaces instead of Awesomium
   windows.
4. **Resource cleanup.** Mirror `CIN_StopCinematic` semantics so handles recycle
   cleanly and the renderer stops referencing freed textures. The FFmpeg shim
   should flush decoders before returning handles to the pool to avoid stale
   audio buffers.

## 5. Automated Playback Tests

Add `tools/tests/test_ffmpeg_samples.py` to exercise the rebuilt pipeline.
The test verifies the FFmpeg DLLs are present, runs `ffprobe` against a VP8/Vorbis
sample clip, and inspects the reported codecs. It skips gracefully when FFmpeg
binaries are unavailable but fails if the codecs are missing. 【F:tools/tests/test_ffmpeg_samples.py†L1-L78】
Ship the BSD-licensed `vp8_sample.webm` fixture from the libwebm test suite
alongside the test for deterministic results. 【F:tools/tests/media/vp8_sample.webm】

## 6. Packaging & Licensing Guidance

* **Windows.** Bundle the rebuilt `avcodec`, `avformat`, and `avutil` binaries
  next to the launcher EXE. Document the requirement to ship compatible VC runtimes
  (`MSVCR100.dll`/`MSVCP100.dll`) as the legacy client did. 【F:docs/quakelive_asset_audit.md†L31-L46】
* **Linux/macOS.** Distribute shared objects under `QuakeLive.app/Contents/Frameworks`
  or alongside the executable. Ensure `rpath` points to the packaged directory so
  the engine locates the FFmpeg libs without relying on the system install.
* **License notices.** Include FFmpeg’s `COPYING.LGPLv2.1`/`COPYING.GPLv2` files in
  the installer and update release notes to list libvpx, libvorbis, libopus, and
  libtheora acknowledgements.
* **Future work.** Streaming downloads and background audio/video require async
  buffering beyond the current `Sys_BeginStreamedFile` helper. Plan additional
  queueing for progressive WebM and consider integrating a media session manager
  before enabling background playback.

Following this plan retires the proprietary launcher stack, keeps the playback
pipeline redistributable, and prepares the GPL engine to own all media rendering
responsibilities.
