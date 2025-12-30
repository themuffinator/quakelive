"""Deterministic coverage for reload/refire and ammo pickup timing baselines."""

from __future__ import annotations

from typing import Mapping

import pytest

from tests.conftest import HarnessTargetMatrix


def _collect_mismatches(
    entries: Mapping[str, Mapping[str, object]],
    *,
    reference_key: str,
) -> list[str]:
    mismatches: list[str] = []
    for weapon, entry in entries.items():
        if entry.get(reference_key) is None:
            continue
        if not entry.get("matches", False):
            mismatches.append(weapon)
    return mismatches


def _assert_reload_and_refire_parity(weapon_timings: Mapping[str, object]) -> None:
    reload_entries = weapon_timings.get("reload_times")
    assert isinstance(reload_entries, Mapping), "Missing reload/refire timing entries"
    mismatches = _collect_mismatches(reload_entries, reference_key="reference_ms")
    assert not mismatches, f"Reload/refire timings mismatched: {', '.join(sorted(mismatches))}"


def _assert_ammo_pickup_parity(weapon_timings: Mapping[str, object]) -> None:
    ammo_entries = weapon_timings.get("ammo_pickups")
    assert isinstance(ammo_entries, Mapping), "Missing ammo pickup timing entries"
    mismatches = _collect_mismatches(ammo_entries, reference_key="reference_pickup")
    assert not mismatches, f"Ammo pickup timings mismatched: {', '.join(sorted(mismatches))}"


@pytest.mark.parametrize("target", ("qvm", "dll", "re"))
def test_weapon_timing_harness_matches_reference(
    target: str, harness_parity_runs: HarnessTargetMatrix
) -> None:
    """Ensure reload/refire and ammo pickup timings stay aligned with HLIL tables."""

    run = harness_parity_runs.get(target)
    if not run:
        reason = harness_parity_runs.missing_reason(target) or f"{target} target is unavailable"
        pytest.skip(reason)

    weapon_timings = run.weapon_timings
    assert isinstance(weapon_timings, Mapping), "Missing weapon timing harness payload"

    _assert_reload_and_refire_parity(weapon_timings)
    _assert_ammo_pickup_parity(weapon_timings)
