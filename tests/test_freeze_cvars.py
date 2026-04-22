"""Freeze Tag CVar regression coverage using the deterministic harness."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from tests._shared import REPO_ROOT

FREEZE_SCENARIO = REPO_ROOT / "tools" / "tests" / "match_sim" / "freeze_cvars.json"

from tools.tests.match_sim.harness import MatchHarness, load_config

def _load_freeze_harness(**cvar_overrides: int) -> MatchHarness:
    config = load_config(FREEZE_SCENARIO)
    freeze_meta = copy.deepcopy(config.metadata.get("freeze", {}))
    cvars = copy.deepcopy(freeze_meta.get("cvars", {}))
    cvars.update(cvar_overrides)
    freeze_meta["cvars"] = cvars
    freeze_meta["enabled"] = True
    config.metadata["freeze"] = freeze_meta
    return MatchHarness(config, seed=config.seed)

def _collect_events(result, action: str):
    for frame in result.frames:
        for event in frame.events:
            if event["action"] == action:
                yield event

def test_spawn_protection_blocks_damage_until_expiry() -> None:
    harness = _load_freeze_harness()
    result = harness.run()

    damage_events = list(_collect_events(result, "damage"))
    assert damage_events, "Scenario should emit damage commands"

    first, second = damage_events[:2]
    assert first["details"]["status"] == "blocked"
    assert first["details"]["reason"] == "spawn_protection"

    assert second["details"].get("target") == "ember"
    assert second["details"]["health"] == pytest.approx(85.0)

    spawn_events = list(_collect_events(result, "client_spawn"))
    assert spawn_events[0]["details"]["freeze_protection_expires"] == pytest.approx(3.0)

def test_auto_thaw_and_inventory_resets() -> None:
    harness = _load_freeze_harness()
    result = harness.run()

    thaw_events = [
        event for event in _collect_events(result, "freeze_thaw") if event["details"]["reason"] == "auto_thaw"
    ]
    assert thaw_events, "Auto-thaw event missing"
    assert thaw_events[0]["time"] == pytest.approx(7.5, rel=1e-3)

    round_win = [
        event
        for event in _collect_events(result, "freeze_thaw")
        if event["details"]["reason"] == "round_win"
    ]
    assert round_win
    assert round_win[0]["time"] == pytest.approx(9.3, rel=1e-3)

    reset_frame = next(frame for frame in result.frames if 9.0 <= frame.time < 9.2)
    ember_state = reset_frame.bots["ember"]
    assert ember_state["health"] == pytest.approx(125.0)
    assert ember_state["ammo"]["rocket"] == pytest.approx(10.0)
    assert ember_state["inventory"]["armor"] == 50
    assert "powerup_quad" not in ember_state["inventory"]

def test_thaw_assist_respects_through_surface_toggle() -> None:
    default_result = _load_freeze_harness().run()
    blocked = [
        event
        for event in _collect_events(default_result, "assist_thaw")
        if event["details"].get("status") == "blocked"
    ]
    assert blocked, "Blocked thaw attempts should be recorded"
    default_thaws = [
        event
        for event in _collect_events(default_result, "freeze_thaw")
        if event["details"]["reason"] == "assist"
    ]
    assert not default_thaws, "Through-surface disabled should prevent assist thaws"

    enabled_result = _load_freeze_harness(g_freezeThawThroughSurface=1).run()
    assist_thaws = [
        event
        for event in _collect_events(enabled_result, "freeze_thaw")
        if event["details"]["reason"] == "assist"
    ]
    assert assist_thaws, "Through-surface thaw should succeed when enabled"
    assert assist_thaws[0]["time"] == pytest.approx(5.5, rel=1e-3)

    enabled_auto = [
        event
        for event in _collect_events(enabled_result, "freeze_thaw")
        if event["details"]["reason"] == "auto_thaw"
    ]
    assert not enabled_auto, "Manual thaw should preempt auto-thaw"

def test_winning_team_credit_thaws_players_when_enabled() -> None:
    enabled = _load_freeze_harness().run()
    round_win_events = [
        event
        for event in _collect_events(enabled, "freeze_thaw")
        if event["details"]["reason"] == "round_win"
    ]
    assert round_win_events

    disabled = _load_freeze_harness(g_freezeThawWinningTeam=0).run()
    disabled_round_win = [
        event
        for event in _collect_events(disabled, "freeze_thaw")
        if event["details"]["reason"] == "round_win"
    ]
    assert not disabled_round_win

    late_auto = [
        event
        for event in _collect_events(disabled, "freeze_thaw")
        if event["details"]["reason"] == "auto_thaw" and event["time"] > 10.0
    ]
    assert late_auto, "Auto-thaw should eventually release the frozen winner"
    assert late_auto[0]["time"] == pytest.approx(13.2, rel=1e-3)
