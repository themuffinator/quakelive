"""Clan Arena warmup and shuffle regression tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests._shared import REPO_ROOT

SCENARIO = REPO_ROOT / "tools" / "tests" / "match_sim" / "clanarena_shuffle.json"

from tools.tests.match_sim.harness import MatchHarness, load_config  # noqa: E402

def _run_scenario():
    config = load_config(SCENARIO)
    harness = MatchHarness(config, seed=config.seed)
    return harness.run()

def _iter_events(result, action: str):
    for frame in result.frames:
        for event in frame.events:
            if event["action"] == action:
                yield event

@pytest.fixture(scope="module")
def ca_result():
    return _run_scenario()

def test_shuffle_countdown_and_execution(ca_result) -> None:
    events = list(_iter_events(ca_result, "tick_shuffle"))
    assert events, "tick_shuffle events missing"
    armed = events[0]
    assert armed["details"]["status"] == "armed"
    assert armed["details"]["delay"] == pytest.approx(4.0)
    assert armed["details"]["warmup_clamped"] is True
    executed = next(evt for evt in events if evt["details"]["status"] == "executed")
    assert executed["time"] == pytest.approx(4.2, rel=1e-3)
    countdown = next(evt for evt in events if evt["details"]["status"] == "countdown_active")
    assert countdown["details"]["deadline"] == pytest.approx(4.1, rel=1e-3)

def test_warmup_gate_force_present(ca_result) -> None:
    gates = list(_iter_events(ca_result, "check_warmup_gate"))
    assert [evt["details"]["status"] for evt in gates] == ["waiting", "ready"]
    assert gates[1]["details"]["required"] == 2

def test_shuffle_vote_flood_protection(ca_result) -> None:
    votes = list(_iter_events(ca_result, "shuffle_vote"))
    statuses = [evt["details"]["status"] for evt in votes]
    assert statuses[:3] == ["accepted", "accepted", "accepted"]
    assert votes[3]["details"]["status"] == "denied"
    assert votes[3]["details"]["penalty_remaining"] == pytest.approx(2.0, rel=1e-3)
    blocked = [evt for evt in votes[3:7] if evt["details"]["status"] == "denied"]
    assert len(blocked) >= 3
    assert votes[-1]["details"]["status"] == "accepted"
