#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILD_ROOT="${REPO_ROOT}/build/re/linux"
SRC_ROOT="${REPO_ROOT}/src-re/prototypes"

CC="${QLR_RE_CC:-${CC:-gcc}}"
CFLAGS_DEFAULT="-std=c99 -Wall -Wextra -O2 -fPIC"
LDFLAGS_DEFAULT="-shared"
CFLAGS="${QLR_RE_CFLAGS:-${CFLAGS:-$CFLAGS_DEFAULT}}"
LDFLAGS="${QLR_RE_LDFLAGS:-${LDFLAGS:-$LDFLAGS_DEFAULT}}"

mkdir -p "$BUILD_ROOT"

if ! command -v "$CC" >/dev/null 2>&1; then
  echo "Compiler '$CC' not found in PATH" >&2
  exit 1
fi

build_module() {
  local name="$1"
  shift
  local output="${BUILD_ROOT}/${name}.so"
  echo "[clean-room] Building ${name} -> ${output}"
  "$CC" \
    $CFLAGS \
    -I"${SRC_ROOT}/common" \
    "$@" \
    $LDFLAGS \
    -o "$output"
}

build_module qlr_client_frame \
  -I"${SRC_ROOT}/c_client" \
  "${SRC_ROOT}/c_client/cl_frame.c" \
  "${SRC_ROOT}/common/native_shim.c"

build_module qlr_game_frame \
  -I"${SRC_ROOT}/g_gameplay" \
  "${SRC_ROOT}/g_gameplay/g_frame.c" \
  "${SRC_ROOT}/common/native_shim.c"

echo "Clean-room shared objects stored under ${BUILD_ROOT}" 
