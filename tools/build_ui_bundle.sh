#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
MANIFEST="${REPO_ROOT}/tools/packaging/ui_bundle_manifest.json"
BUILD_ROOT="${REPO_ROOT}/build/ui_bundle"
STAGING="${BUILD_ROOT}/staging"
ARTIFACT_ROOT="${REPO_ROOT}/artifacts/ui_bundle"
LOG_DIR="${ARTIFACT_ROOT}/logs"
METRICS_DIR="${ARTIFACT_ROOT}/metrics"
FONT_BAKE_TOOL="${REPO_ROOT}/tools/packaging/bake_fonts.py"

mkdir -p "${STAGING}" "${LOG_DIR}" "${METRICS_DIR}"
rm -rf "${STAGING}" && mkdir -p "${STAGING}"

PACKAGE_NAME=$(python3 - <<PY
import json
import pathlib
with open(pathlib.Path("${MANIFEST}"), 'r', encoding='utf-8') as handle:
    print(json.load(handle)['package'])
PY
)

copy_log="${LOG_DIR}/manifest_copy.log"
python3 - <<PY
import json
import pathlib
import shutil
import sys

manifest = json.loads(pathlib.Path("${MANIFEST}").read_text())
staging = pathlib.Path("${STAGING}")
log_path = pathlib.Path("${copy_log}")
logs = []

for entry in manifest.get('files', []):
    source = pathlib.Path(entry['source'])
    destination = staging / entry['destination']
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    logs.append(f"Copied {source} -> {destination}")

log_path.write_text('\n'.join(logs) + '\n', encoding='utf-8')
PY

BAKE_LOG="${LOG_DIR}/font_bake.log"
METRICS_JSON="${METRICS_DIR}/font_metrics.json"
python3 "${FONT_BAKE_TOOL}" --manifest "${MANIFEST}" --output "${STAGING}" --log "${BAKE_LOG}" --metrics "${METRICS_JSON}"

PK3_PATH="${BUILD_ROOT}/${PACKAGE_NAME}"
rm -f "${PK3_PATH}"
(
  cd "${STAGING}" && zip -qr "${PK3_PATH}" .
)

mkdir -p "${ARTIFACT_ROOT}"
cp "${PK3_PATH}" "${ARTIFACT_ROOT}/${PACKAGE_NAME}"

cat <<MSG
UI bundle complete.
  package: ${PK3_PATH}
  manifest log: ${LOG_DIR}/manifest_copy.log
  font bake log: ${BAKE_LOG}
  font metrics: ${METRICS_JSON}
MSG
