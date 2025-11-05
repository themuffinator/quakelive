"""Tests for the trace capture and replay harness."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping

import pytest

from tools.trace import (
    TraceLaunchResult,
    TraceLauncher,
    TraceLauncherConfig,
    TraceReplayer,
    TraceVMDriver,
)


@pytest.fixture()
def trace_fixture(tmp_path_factory: pytest.TempPathFactory) -> TraceLaunchResult:
    output_dir = tmp_path_factory.mktemp("trace")
    producer = Path(__file__).parent / "match_sim" / "mock_trace_producer.py"
    config = TraceLauncherConfig(
        command=[sys.executable, str(producer)],
        output_dir=output_dir,
        match_duration=0.2,
    )
    launcher = TraceLauncher(config)
    return launcher.launch()


def test_launcher_captures_expected_streams(trace_fixture: TraceLaunchResult) -> None:
    result = trace_fixture

    assert result.manifest_path.exists()
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))

    assert manifest["counts"]["SYS"] == 2
    assert manifest["counts"]["RNG"] == 1
    assert manifest["counts"]["ENT"] == 2
    assert manifest["metadata"]["map"] == "qztourney7"

    syscalls = (result.output_dir / "syscalls.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(syscalls) == 2
    assert "trap_Print" in syscalls[0]


def test_replay_confirms_determinism(trace_fixture: TraceLaunchResult) -> None:
    class RecordingDriver(TraceVMDriver):
        def __init__(self) -> None:
            self.syscalls: list[Mapping[str, Any]] = []
            self.rng: list[Mapping[str, Any]] = []
            self.entities: list[Mapping[str, Any]] = []

        def apply_syscall(self, event: Mapping[str, Any]) -> None:
            self.syscalls.append(event)

        def apply_rng_seed(self, event: Mapping[str, Any]) -> None:
            self.rng.append(event)

        def apply_entity_state(self, event: Mapping[str, Any]) -> None:
            self.entities.append(event)

    driver = RecordingDriver()
    replayer = TraceReplayer(trace_fixture.output_dir, driver)
    replay_result = replayer.replay()

    assert replay_result.digests == json.loads(
        trace_fixture.manifest_path.read_text(encoding="utf-8")
    )["digests"]

    assert len(driver.syscalls) == 2
    assert driver.syscalls[0]["name"] == "trap_Print"
    assert len(driver.rng) == 1
    assert driver.rng[0]["seed"] == 123456
    assert len(driver.entities) == 2
    assert driver.entities[-1]["entities"][0]["health"] == 100
