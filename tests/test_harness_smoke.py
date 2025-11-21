"""Smoke coverage for the deterministic harness artefacts."""

from __future__ import annotations

import pytest

from tests.run_harnesses import HarnessBundleResult, run_harness_bundle


@pytest.fixture(scope="module")
def vm_native_runs(tmp_path_factory: pytest.TempPathFactory) -> dict[str, HarnessBundleResult]:
    """Run the deterministic harness bundle for VM and native targets."""

    runs: dict[str, HarnessBundleResult] = {}
    for target in ("qvm", "dll"):
        artifact_root = tmp_path_factory.mktemp(f"harness_smoke_{target}")
        runs[target] = run_harness_bundle(target, artifact_root)

    return runs


def test_vm_and_native_timelines_match(vm_native_runs: dict[str, HarnessBundleResult]) -> None:
    """Ensure VM and native harness targets emit matching timelines."""

    slug = "duel"
    vm_run = vm_native_runs["qvm"]
    native_run = vm_native_runs["dll"]

    vm_timeline = vm_run.load_match_timeline(slug)
    native_timeline = native_run.load_match_timeline(slug)

    assert vm_run.match_timeline_path(slug).exists()
    assert native_run.match_timeline_path(slug).exists()
    assert vm_timeline == native_timeline

    match_log = native_run.read_log("match_sim")
    assert "Match simulation harness completed successfully." in match_log

    re_run = vm_native_runs.get("re")
    if re_run is not None:
        re_timeline = re_run.load_match_timeline(slug)
        assert re_timeline == vm_timeline
