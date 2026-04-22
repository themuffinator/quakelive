"""Deterministic pickup coverage validating VM/DLL parity."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Sequence

import pytest

from tests._shared import REPO_ROOT

from tools.tests.match_sim import BotConfig, CommandConfig, MatchConfig, MatchHarness

EXPECTATION_PATH = REPO_ROOT / "tests" / "expectations" / "match_sim_item_pickups.expect"
TARGETS: Sequence[str] = ("qvm", "dll")

def _load_expectations() -> dict[str, dict[str, list[str]]]:
    payload = json.loads(EXPECTATION_PATH.read_text(encoding="utf-8"))
    scenarios: dict[str, dict[str, list[str]]] = {}
    for scenario, targets in payload.items():
        scenarios[scenario] = {}
        for target, lines in targets.items():
            scenarios[scenario][target] = [str(line) for line in lines]
    return scenarios

@pytest.fixture(scope="module")
def pickup_expectations() -> dict[str, dict[str, list[str]]]:
    return _load_expectations()

def _collect_pickup_summary(result) -> list[str]:
    lines: list[str] = []
    for frame in result.frames:
        for event in frame.events:
            if event["action"].lower() != "pickup":
                continue
            details = event.get("details", {})
            pickup_type = details.get("type")
            time_stamp = f"{event['time']:.3f}"
            bot = event.get("bot", "<bot>")
            if pickup_type == "ammo":
                lines.append(
                    f"{time_stamp} {bot} ammo {details.get('weapon')} "
                    f"requested={details.get('requested')} granted={details.get('granted')} "
                    f"denied={details.get('denied')} total={details.get('total')} max={details.get('max')} "
                    f"saturated={details.get('saturated')}"
                )
            elif pickup_type == "armor":
                lines.append(
                    f"{time_stamp} {bot} armor requested={details.get('requested')} "
                    f"granted={details.get('granted')} denied={details.get('denied')} total={details.get('total')} "
                    f"effective_max={details.get('effective_max')} handicap={details.get('handicap_applied')} "
                    f"saturated={details.get('saturated')}"
                )
            elif pickup_type == "flag":
                status = details.get("status")
                flag_name = details.get("flag")
                mode = details.get("mode")
                extra = []
                if "carrier" in details:
                    extra.append(f"carrier={details['carrier']}")
                if "score_delta" in details:
                    extra.append(f"score={details['score_delta']}")
                if "previous" in details:
                    extra.append(f"previous={details['previous']}")
                lines.append(
                    f"{time_stamp} {bot} flag {flag_name} mode={mode} event={details.get('event')} "
                    f"status={status} {' '.join(extra).strip()}".rstrip()
                )
    return lines

def _assert_pickup_parity(
    scenario: str,
    captured: Iterable[str],
    expectations: dict[str, dict[str, list[str]]],
    tmp_path: Path,
) -> None:
    recorded = [line.strip() for line in captured]
    expected_targets = expectations.get(scenario)
    assert expected_targets, f"missing expectations for scenario '{scenario}'"
    qvm_expected = expected_targets.get("qvm")
    dll_expected = expected_targets.get("dll")
    assert qvm_expected is not None, f"missing qvm expectation for {scenario}"
    assert dll_expected is not None, f"missing dll expectation for {scenario}"
    assert qvm_expected == dll_expected, f"VM/DLL expectations diverge for {scenario}"

    for target, expected_lines in ("qvm", qvm_expected), ("dll", dll_expected):
        if recorded != expected_lines:
            output_path = tmp_path / f"{scenario}-{target}.actual"
            output_path.write_text("\n".join(recorded), encoding="utf-8")
            pytest.fail(
                f"{scenario} pickup summary diverged for {target}. "
                f"Captured payload written to {output_path}"
            )

def _run_harness(config: MatchConfig) -> list[str]:
    harness = MatchHarness(config, seed=config.seed)
    return _collect_pickup_summary(harness.run())

def _max_ammo_config() -> MatchConfig:
    script = [
        CommandConfig(
            time=0.25,
            action="pickup",
            params={"type": "ammo", "weapon": "rocket", "amount": 4, "max": 20},
        ),
        CommandConfig(
            time=0.5,
            action="pickup",
            params={"type": "ammo", "weapon": "rocket", "amount": 5, "max": 20},
        ),
        CommandConfig(time=0.75, action="shoot", params={"weapon": "rocket", "cost": 7}),
        CommandConfig(
            time=1.0,
            action="pickup",
            params={"type": "ammo", "weapon": "rocket", "amount": 6, "max": 20},
        ),
        CommandConfig(
            time=1.25,
            action="pickup",
            params={"type": "ammo", "weapon": "rocket", "amount": 2, "max": 20},
        ),
    ]
    config = MatchConfig(
        map="qztourney7",
        duration=2.0,
        tick_rate=10,
        seed=2024,
        bots=[
            BotConfig(
                name="visor",
                team="red",
                initial_state={"ammo": {"rocket": 18}},
                script=script,
            )
        ],
    )
    return config

def _spawn_armor_config() -> MatchConfig:
    bot = BotConfig(
        name="anarki",
        team="blue",
        initial_state={"inventory": {"armor": 0}, "custom": {"handicap": 0.75}},
        script=[
            CommandConfig(
                time=0.25,
                action="pickup",
                params={"type": "armor", "amount": 50, "max": 100},
            ),
            CommandConfig(
                time=0.75,
                action="pickup",
                params={"type": "armor", "amount": 50, "max": 100},
            ),
            CommandConfig(time=1.0, action="custom", params={"handicap": 1.0}),
            CommandConfig(
                time=1.1,
                action="set_state",
                params={"inventory": {"armor": 20}},
            ),
            CommandConfig(
                time=1.2,
                action="pickup",
                params={"type": "armor", "amount": 50, "max": 100},
            ),
            CommandConfig(
                time=1.4,
                action="pickup",
                params={"type": "armor", "amount": 50, "max": 100},
            ),
        ],
    )
    return MatchConfig(map="pro-q3dm6", duration=2.0, tick_rate=10, seed=4040, bots=[bot])

def _flag_modes_config() -> MatchConfig:
    ranger_script = [
        CommandConfig(
            time=0.1,
            action="pickup",
            params={"type": "flag", "flag": "blue", "event": "pickup", "mode": "ctf"},
        ),
        CommandConfig(
            time=0.3,
            action="pickup",
            params={"type": "flag", "flag": "blue", "event": "capture", "mode": "ctf", "score": 1},
        ),
        CommandConfig(
            time=0.8,
            action="pickup",
            params={"type": "flag", "flag": "neutral", "event": "pickup", "mode": "1fctf"},
        ),
        CommandConfig(
            time=0.9,
            action="pickup",
            params={"type": "flag", "flag": "neutral", "event": "drop", "mode": "1fctf"},
        ),
    ]
    slash_script = [
        CommandConfig(
            time=0.4,
            action="pickup",
            params={"type": "flag", "flag": "red", "event": "pickup", "mode": "ctf"},
        ),
        CommandConfig(
            time=0.6,
            action="pickup",
            params={"type": "flag", "flag": "red", "event": "capture", "mode": "ctf", "score": 1},
        ),
        CommandConfig(
            time=1.0,
            action="pickup",
            params={"type": "flag", "flag": "neutral", "event": "return", "mode": "1fctf"},
        ),
        CommandConfig(
            time=1.2,
            action="pickup",
            params={"type": "flag", "flag": "neutral", "event": "pickup", "mode": "1fctf"},
        ),
        CommandConfig(
            time=1.4,
            action="pickup",
            params={"type": "flag", "flag": "neutral", "event": "capture", "mode": "1fctf", "score": 1},
        ),
    ]
    return MatchConfig(
        map="qzteam1",
        duration=2.0,
        tick_rate=10,
        seed=4242,
        bots=[
            BotConfig(name="ranger", team="red", script=ranger_script),
            BotConfig(name="slash", team="blue", script=slash_script),
        ],
    )

def test_max_ammo_pickup_parity(tmp_path: Path, pickup_expectations: dict[str, dict[str, list[str]]]) -> None:
    summary = _run_harness(_max_ammo_config())
    _assert_pickup_parity("max_ammo", summary, pickup_expectations, tmp_path)

def test_spawn_armor_handicap(tmp_path: Path, pickup_expectations: dict[str, dict[str, list[str]]]) -> None:
    summary = _run_harness(_spawn_armor_config())
    _assert_pickup_parity("spawn_armor", summary, pickup_expectations, tmp_path)

def test_flag_modes_cover_ctf_and_oneflag(
    tmp_path: Path, pickup_expectations: dict[str, dict[str, list[str]]]
) -> None:
    summary = _run_harness(_flag_modes_config())
    _assert_pickup_parity("flag_modes", summary, pickup_expectations, tmp_path)
