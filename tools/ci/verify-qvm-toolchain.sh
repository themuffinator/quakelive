#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MISSING=()
REQUIRED_TOOLS=(perl make gcc)

for tool in "${REQUIRED_TOOLS[@]}"; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    MISSING+=("$tool")
  fi
done

if (( ${#MISSING[@]} > 0 )); then
  printf 'Missing required host tools: %s\n' "${MISSING[*]}" >&2
  exit 1
fi

echo "Detected toolchain components: ${REQUIRED_TOOLS[*]}"

pushd "$ROOT_DIR/src/q3asm" >/dev/null
make -n >/dev/null
popd >/dev/null

echo "q3asm makefile parsed successfully"

pushd "$ROOT_DIR/src/lcc" >/dev/null
make -n >/dev/null
popd >/dev/null

echo "lcc makefile parsed successfully"

VM_SCRIPTS=(
  "$ROOT_DIR/src/code/game/game.sh"
  "$ROOT_DIR/src/code/cgame/cgame.sh"
  "$ROOT_DIR/src/code/q3_ui/q3_ui.sh"
)

for script in "${VM_SCRIPTS[@]}"; do
  if [[ ! -f "$script" ]]; then
    printf 'Expected VM wrapper missing: %s\n' "$script" >&2
    exit 1
  fi
  echo "Verified wrapper: ${script#$ROOT_DIR/}"
done

echo "QVM toolchain prerequisites are present."
