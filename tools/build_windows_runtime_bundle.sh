#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
MANIFEST="${REPO_ROOT}/tools/packaging/windows_runtime_manifest.json"
STAGING="${REPO_ROOT}/build/windows_runtime"
LOG_DIR="${REPO_ROOT}/artifacts/windows_runtime"
LOG_PATH="${LOG_DIR}/manifest_copy.log"
STAGE_TOOL="${REPO_ROOT}/tools/packaging/stage_windows_runtime.py"

mkdir -p "${STAGING}" "${LOG_DIR}"

ARGS=(
  --manifest "${MANIFEST}"
  --output "${STAGING}"
  --log "${LOG_PATH}"
  --fetch-urls
)

if [[ "${INCLUDE_PROPRIETARY:-}" == "1" ]]; then
  ARGS+=(--include-proprietary)
fi

python3 "${STAGE_TOOL}" "${ARGS[@]}"

echo "Staged Windows runtime bundle at ${STAGING}"
echo "  manifest log: ${LOG_PATH}"
