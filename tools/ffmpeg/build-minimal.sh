#!/usr/bin/env bash
# Minimal FFmpeg build tailored for the Quake Live launcher refactor.
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

JOBS="$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
make -j"${JOBS}"
make install
