"""Shared pytest fixtures for deterministic harness runs."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from typing import Dict

import pytest

from tests.run_harnesses import HarnessBundleResult, REPO_ROOT, run_harness_bundle


@dataclass(slots=True)
class HarnessTargetMatrix:
    """Container for harness bundle outputs across build targets."""

    runs: Dict[str, HarnessBundleResult]
    missing_targets: Dict[str, str]

    def has(self, target: str) -> bool:
        return target in self.runs

    def get(self, target: str) -> HarnessBundleResult | None:
        return self.runs.get(target)

    def missing_reason(self, target: str) -> str | None:
        return self.missing_targets.get(target)

    def require(self, target: str) -> HarnessBundleResult:
        if target not in self.runs:
            reason = self.missing_reason(target) or f"{target} target is unavailable"
            pytest.skip(reason)
        return self.runs[target]


def _detect_native_support() -> tuple[bool, str | None]:
    build_script = REPO_ROOT / "tools" / "ci" / "build-cleanroom.sh"
    if os.name == "nt":
        return False, "Native reverse builds require a POSIX shell"
    if not build_script.exists():
        return False, f"Missing clean-room build helper: {build_script}"
    if shutil.which("bash") is None:
        return False, "bash is not available in PATH"
    compiler = os.environ.get("QLR_RE_CC") or os.environ.get("CC") or "gcc"
    if shutil.which(compiler) is None:
        return False, f"Required compiler '{compiler}' is not available"
    prototype_root = REPO_ROOT / "src-re" / "prototypes"
    if not prototype_root.exists():
        return False, f"Reverse-engineering prototypes missing: {prototype_root}"
    return True, None


def _collect_harness_runs(tmp_path_factory: pytest.TempPathFactory) -> HarnessTargetMatrix:
    runs: Dict[str, HarnessBundleResult] = {}
    missing: Dict[str, str] = {}

    for target in ("qvm", "dll"):
        artifact_root = tmp_path_factory.mktemp(f"harness_{target}")
        runs[target] = run_harness_bundle(target, artifact_root)

    supported, reason = _detect_native_support()
    if supported:
        artifact_root = tmp_path_factory.mktemp("harness_re")
        runs["re"] = run_harness_bundle("re", artifact_root)
    else:
        missing["re"] = reason or "Native reverse build tooling unavailable"

    return HarnessTargetMatrix(runs=runs, missing_targets=missing)


@pytest.fixture(scope="session")
def harness_parity_runs(
    tmp_path_factory: pytest.TempPathFactory,
) -> HarnessTargetMatrix:
    """Execute the harness bundle once per supported target for parity tests."""

    return _collect_harness_runs(tmp_path_factory)
