#!/usr/bin/env bash
set -euo pipefail

# Resolve repository root
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILD_DIR="${BUILD_DIR:-${ROOT_DIR}/build/linux-i386-glibc}"
[[ "${BUILD_DIR}" = /* ]] || BUILD_DIR="${ROOT_DIR}/${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"
REFERENCE_SO="${ROOT_DIR}/assets/quakelive/baseq3/qagamei386.so"

# Prefer 32-bit toolchain defaults; callers may override CC/CXX/AS
CC32="${CC:-gcc} -m32 -std=gnu89"
CXX32="${CXX:-g++} -m32"
AS32="${AS:-gcc} -m32"

# Point pkg-config at the 32-bit .pc directory when present
export PKG_CONFIG_LIBDIR="${PKG_CONFIG_LIBDIR:-/usr/lib/i386-linux-gnu/pkgconfig}"

# Build only the server module to keep the loop tight
make -C "${ROOT_DIR}/src/code/unix" \
ARCH=i386 \
GLIBC=-glibc \
QL_ENABLE_OGG=0 \
B="${BUILD_DIR}" \
CC="${CC32}" \
CXX="${CXX32}" \
AS="${AS32}" \
makedirs "${BUILD_DIR}/baseq3/qagamei386.so"

# Capture export lists for parity validation
nm -D --defined-only "${BUILD_DIR}/baseq3/qagamei386.so" | awk '{print $3}' | sort -u > "${BUILD_DIR}/qagame.exports"
nm -D --defined-only "${REFERENCE_SO}" | awk '{print $3}' | sort -u > "${BUILD_DIR}/qagame-reference.exports"

if diff -u "${BUILD_DIR}/qagame-reference.exports" "${BUILD_DIR}/qagame.exports" > "${BUILD_DIR}/qagame.exports.diff"; then
echo "Symbol parity matches ${REFERENCE_SO}"
else
echo "Symbol list differs; see ${BUILD_DIR}/qagame.exports.diff"
fi
