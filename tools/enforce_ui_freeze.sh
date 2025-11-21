#!/usr/bin/env bash
set -euo pipefail

BASE_BRANCH=${GITHUB_BASE_REF:-main}
REMOTE_NAME=${UI_FREEZE_REMOTE:-origin}

if git remote show "${REMOTE_NAME}" >/dev/null 2>&1; then
  BASE_REF="${REMOTE_NAME}/${BASE_BRANCH}"
else
  BASE_REF="${BASE_BRANCH}"
fi

echo "Ensuring base reference ${BASE_REF} is available..."
if ! git rev-parse --verify "${BASE_REF}" >/dev/null 2>&1; then
  if git remote show "${REMOTE_NAME}" >/dev/null 2>&1; then
    git fetch --no-tags --depth=1 "${REMOTE_NAME}" "${BASE_BRANCH}"
  fi
fi

if git rev-parse --verify "${BASE_REF}" >/dev/null 2>&1; then
  BASE_COMMIT=$(git merge-base HEAD "${BASE_REF}" || true)
else
  BASE_COMMIT=""
fi

if [[ -n "${BASE_COMMIT}" ]]; then
  CHANGED_UI_FILES=$(git diff --name-only "${BASE_COMMIT}" -- 'src/ui/**')
else
  echo "Base reference ${BASE_REF} is unavailable; falling back to working tree inspection." >&2
  CHANGED_UI_FILES=$(git status --porcelain -- 'src/ui/**' | cut -c4-)
fi

if [[ -n "${CHANGED_UI_FILES}" ]]; then
  echo "Changes to src/ui are blocked. Use code-level hooks or overlay packages instead." >&2
  echo "Detected modifications:" >&2
  echo "${CHANGED_UI_FILES}" >&2
  exit 1
fi

echo "No prohibited UI modifications detected."
