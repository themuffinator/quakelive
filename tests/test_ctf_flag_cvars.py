"""Coverage for flag physics and return CVars within the match simulator."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests._shared import REPO_ROOT

SCENARIO = REPO_ROOT / "tools" / "tests" / "match_sim" / "ctf_flag_cvars.json"

from tools.tests.match_sim.harness import MatchHarness, load_config  # noqa: E402

def _run_scenario():
    config = load_config(SCENARIO)
    harness = MatchHarness(config, seed=config.seed)
    return harness.run()

@pytest.fixture(scope="module")
def ctf_result():
    return _run_scenario()

def _iter_events(result, *, action: str | None = None):
    for frame in result.frames:
        for event in frame.events:
            if action and event["action"] != action:
                continue
            yield event

def test_flag_drop_uses_ctf_cvars(ctf_result) -> None:
    drop_event = next(
        event
        for event in _iter_events(ctf_result, action="pickup")
        if event["details"].get("event") == "drop"
        and event["details"].get("flag") == "blue"
    )
    physics = drop_event["details"]["physics"]
    traj = drop_event["details"]["trajectory"]
    assert physics["enabled"] is True
    assert physics["bounce"] == pytest.approx(0.65)
    assert traj["forward_speed"] == pytest.approx(275.0)
    assert traj["vertical_speed"] == pytest.approx(240.0)
    expected_deadline = drop_event["time"] + 6.0
    assert drop_event["details"]["return_deadline"] == pytest.approx(expected_deadline, rel=1e-3)

def test_flag_timeout_and_suicide_returns(ctf_result) -> None:
    return_events = [
        event
        for event in _iter_events(ctf_result, action="flag_return")
        if event["details"].get("flag")
    ]
    neutral_return = next(evt for evt in return_events if evt["details"]["flag"] == "neutral")
    assert neutral_return["time"] == pytest.approx(12.2, rel=1e-3)
    assert neutral_return["details"]["status"] == "returned"
    assert not any(evt["details"]["flag"] == "blue" for evt in return_events)

    suicide_drop = next(
        event
        for event in _iter_events(ctf_result, action="pickup")
        if event["details"].get("flag") == "red" and event["details"].get("event") == "drop"
    )
    assert suicide_drop["details"]["status"] == "forced_return"
    assert suicide_drop["details"]["reason"] == "suicide"
