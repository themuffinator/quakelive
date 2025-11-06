"""Tests for the scripted match simulation harness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools.tests.match_sim import MatchHarness, run_from_file


def _write_scenario(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


@pytest.fixture()
def simple_scenario(tmp_path: Path) -> Path:
    scenario = {
        "map": "pro-q3dm13",
        "duration": 1.0,
        "tick_rate": 5,
        "seed": 999,
        "bots": [
            {
                "name": "visor",
                "team": "red",
                "spawn": {
                    "random_positions": [[0, 0, 48], [32, -16, 48]],
                },
                "initial_state": {
                    "health": 100,
                    "ammo": {"rail": 5},
                },
                "script": [
                    {"time": 0.0, "action": "look", "params": {"direction": [1, 0, 0]}},
                    {"time": 0.2, "action": "move", "params": {"direction": [1, 0, 0], "speed": 320}},
                    {"time": 0.4, "action": "shoot", "params": {"weapon": "rail"}},
                ],
            },
            {
                "name": "slash",
                "team": "blue",
                "spawn": {
                    "position": [-64, 16, 48],
                },
                "initial_state": {
                    "health": 125,
                    "inventory": {"armor": 50},
                },
                "script": [
                    {
                        "time": 0.4,
                        "action": "custom",
                        "params": {
                            "stack": {"random": {"mode": "randint", "low": 150, "high": 175}},
                        },
                    }
                ],
            },
        ],
    }
    scenario_path = tmp_path / "scenario.json"
    _write_scenario(scenario_path, scenario)
    return scenario_path


def test_run_from_file_produces_timeline(simple_scenario: Path) -> None:
    result = run_from_file(simple_scenario)

    assert result.config.map == "pro-q3dm13"
    # 1 second at 5 Hz -> 6 frames including tick 0
    assert len(result.frames) == 6
    assert result.frames[0].events[0]["action"] == "look"
    assert "visor" in result.frames[0].bots


@pytest.mark.parametrize("override_seed", [None, 73])
def test_seed_resolution(simple_scenario: Path, override_seed: int | None) -> None:
    result = run_from_file(simple_scenario, seed=override_seed)

    expected_seed = override_seed if override_seed is not None else 999
    assert result.config.seed == expected_seed

    harness = MatchHarness(result.config)
    assert harness.seed == expected_seed


def test_default_seed_used_when_not_specified(tmp_path: Path) -> None:
    scenario = {
        "map": "qzpractice", "duration": 0.2, "bots": [], "tick_rate": 10
    }
    scenario_path = tmp_path / "scenario.json"
    _write_scenario(scenario_path, scenario)

    harness = MatchHarness(run_from_file(scenario_path).config)
    assert harness.seed == 1337


def test_deterministic_runs_match(simple_scenario: Path) -> None:
    first = run_from_file(simple_scenario, seed=2024)
    second = run_from_file(simple_scenario, seed=2024)

    assert first.config.seed == second.config.seed == 2024
    assert [frame.bots for frame in first.frames] == [frame.bots for frame in second.frames]
    assert [frame.events for frame in first.frames] == [frame.events for frame in second.frames]
