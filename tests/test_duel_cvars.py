"""Validate duel-specific CVars and configstring signals."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests._shared import REPO_ROOT

SCENARIO = REPO_ROOT / "tools" / "tests" / "match_sim" / "duel_cvars.json"

from tools.tests.match_sim.harness import run_from_file  # noqa: E402

@pytest.fixture(scope="module")
def duel_timeline():
    return run_from_file(SCENARIO)

def _extract_events(result, action: str):
    for frame in result.frames:
        for event in frame.events:
            if event["action"] == action:
                yield event

def test_duel_loadout_grant_matches_retail_baseline(duel_timeline):
    grants = list(_extract_events(duel_timeline, "duel_loadout"))
    assert grants, "Loadout grant event missing from duel scenario"
    details = grants[0]["details"]
    assert details["script"] == "weapon_gauntlet weapon_machinegun ammo_bullets 100"

def test_duel_ready_up_flow_exposes_warmup_and_counts(duel_timeline):
    ready_events = list(_extract_events(duel_timeline, "duel_ready_up"))
    assert ready_events, "Ready-up state should be captured"
    ready = ready_events[0]["details"]
    assert ready["warmup_time"] == -1
    assert ready["min_players"] == 2
    assert ready["countdown_seconds"] == 20
    assert ready["ready_configstring"] == "ready:0"

def test_duel_sudden_death_cvars_match_baseline(duel_timeline):
    sudden_death = list(_extract_events(duel_timeline, "duel_sudden_death"))
    assert sudden_death, "Sudden-death settings should be emitted"
    payload = sudden_death[0]["details"]
    assert payload["respawn"] == 0
    assert payload["start_seconds"] == 3
    assert payload["tick_seconds"] == 60
    assert payload["max_seconds"] == 10
    assert payload["increment_seconds"] == 1
    assert payload["print_announcements"] == 1
