"""Parses damage timelines to verify VM/DLL parity."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tools.tests.match_sim import run_from_file

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SCENARIO = REPO_ROOT / "tools" / "tests" / "match_sim" / "damage_timeline.json"
EXPECTATION_PATH = REPO_ROOT / "tests" / "expectations" / "match_sim_damage_timeline.expect"
TARGETS = ("qvm", "dll")


def _load_expectations() -> dict[str, dict[str, list[str]]]:
    payload = json.loads(EXPECTATION_PATH.read_text(encoding="utf-8"))
    scenarios: dict[str, dict[str, list[str]]] = {}
    for scenario, targets in payload.items():
        scenarios[scenario] = {}
        for target, lines in targets.items():
            scenarios[scenario][target] = [str(line) for line in lines]
    return scenarios


def _collect_damage_summary(result) -> list[str]:
    lines: list[str] = []
    for frame in result.frames:
        for event in frame.events:
            action = str(event.get("action", "")).lower()
            if action not in {"damage", "heal"}:
                continue
            details = event.get("details", {})
            actor = event.get("bot", "<bot>")
            target = details.get("target", actor)
            amount = details.get("amount", 0.0)
            health = details.get("health", 0.0)
            lines.append(
                f"{event['time']:.3f} {actor} {action} {target} "
                f"amount={amount} health={health}"
            )
    return lines


def _assert_damage_parity(
    scenario: str,
    captured: list[str],
    expectations: dict[str, dict[str, list[str]]],
    tmp_path: Path,
) -> None:
    expected_targets = expectations.get(scenario)
    assert expected_targets, f"missing expectations for scenario '{scenario}'"
    qvm_expected = expected_targets.get("qvm")
    dll_expected = expected_targets.get("dll")
    assert qvm_expected is not None, f"missing qvm expectation for {scenario}"
    assert dll_expected is not None, f"missing dll expectation for {scenario}"
    assert qvm_expected == dll_expected, f"VM/DLL expectations diverge for {scenario}"

    for target, expected_lines in ("qvm", qvm_expected), ("dll", dll_expected):
        if captured != expected_lines:
            output_path = tmp_path / f"{scenario}-{target}.actual"
            output_path.write_text("\n".join(captured), encoding="utf-8")
            pytest.fail(
                f"{scenario} damage summary diverged for {target}. "
                f"Captured payload written to {output_path}"
            )


@pytest.fixture(scope="module")
def damage_expectations() -> dict[str, dict[str, list[str]]]:
    return _load_expectations()


def test_damage_timeline_parity(tmp_path: Path, damage_expectations) -> None:
    result = run_from_file(SCENARIO)
    summary = _collect_damage_summary(result)
    _assert_damage_parity("damage_timeline", summary, damage_expectations, tmp_path)
