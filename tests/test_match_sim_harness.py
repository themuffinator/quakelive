"""Test coverage for the deterministic match simulation harness."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.tests.match_sim.harness import MatchHarness, load_config, run_from_file

SCENARIO = REPO_ROOT / "tools" / "tests" / "match_sim" / "sample_scenario.json"
SCENARIO_DIR = REPO_ROOT / "tools" / "tests" / "match_sim"
ALL_SCENARIOS = [
    SCENARIO,
    SCENARIO_DIR / "overtime_scenario.json",
    SCENARIO_DIR / "complex_loadouts.json",
]


def test_run_from_file_is_deterministic(tmp_path) -> None:
    """Running the same scenario with the same seed yields identical timelines."""

    result_a = run_from_file(SCENARIO, seed=4242)
    result_b = run_from_file(SCENARIO, seed=4242)

    assert result_a.config.seed == 4242
    assert result_b.config.seed == 4242
    assert result_a.to_json(indent=None) == result_b.to_json(indent=None)


def test_seed_override_changes_randomised_outputs() -> None:
    """Using different seeds should influence randomised spawn and script values."""

    config_default = load_config(SCENARIO)
    default_result = MatchHarness(config_default).run()

    config_override = load_config(SCENARIO)
    override_result = MatchHarness(config_override, seed=9090).run()

    assert default_result.config.seed == 2024
    assert override_result.config.seed == 9090

    # Randomised command parameters should diverge when the seed is overridden.
    default_move_event = default_result.frames[2].events[0]
    override_move_event = override_result.frames[2].events[0]

    assert default_move_event["bot"] == "anarki"
    assert override_move_event["bot"] == "anarki"

    default_direction = default_move_event["details"]["velocity"]
    override_direction = override_move_event["details"]["velocity"]

    assert default_direction != override_direction
    assert default_result.to_json(indent=None) != override_result.to_json(indent=None)


@pytest.mark.parametrize("scenario_path", ALL_SCENARIOS, ids=[path.stem for path in ALL_SCENARIOS])
def test_all_scenarios_produce_frames(scenario_path: Path) -> None:
    """Ensure every shipped scenario runs without errors and emits timeline frames."""

    result = run_from_file(scenario_path, seed=1337)

    assert result.frames, "Scenario should produce at least one frame"
    assert result.config.map
    assert result.config.metadata is not None
