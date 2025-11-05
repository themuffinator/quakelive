"""Unit tests covering the client regression harness."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.tests.client_regression import ClientPredictor, ClientRegressionHarness


@pytest.fixture()
def sample_snapshots_path() -> Path:
    return Path(__file__).parent / "client_regression" / "sample_snapshots.json"


def test_load_snapshots(sample_snapshots_path: Path) -> None:
    harness = ClientRegressionHarness(ClientPredictor())
    snapshots = harness.load_snapshots(sample_snapshots_path)

    assert [snap.sequence for snap in snapshots] == [1, 2, 3]
    assert snapshots[0].player_state["health"] == 125


def test_replay_produces_stable_hashes(sample_snapshots_path: Path) -> None:
    harness = ClientRegressionHarness(ClientPredictor())
    snapshots = harness.load_snapshots(sample_snapshots_path)

    frames = list(harness.replay(snapshots))
    hashes = [frame.hud_hash for frame in frames]

    assert hashes == [
        "db0c582635b0d000b8d8cc623979b0f556776ff168c4baf9717f6f2802632a11",
        "638c3a5679231de7caf143f388431effe769e912152bbd56f75a019ee5ab0e56",
        "fc456828d2c7d69712cee52bec1faa968bf274d60442ca33ef7f412badd2d1de",
    ]

    # Frames also expose the HUD payload in deterministic form.
    assert frames[-1].hud.to_dict()["weapon"] == "lightning_gun"


def test_replay_to_payloads_returns_json_ready_structures(sample_snapshots_path: Path) -> None:
    harness = ClientRegressionHarness(ClientPredictor())
    snapshots = harness.load_snapshots(sample_snapshots_path)

    payloads = harness.replay_to_payloads(snapshots)

    assert [payload["hash"] for payload in payloads] == [
        "db0c582635b0d000b8d8cc623979b0f556776ff168c4baf9717f6f2802632a11",
        "638c3a5679231de7caf143f388431effe769e912152bbd56f75a019ee5ab0e56",
        "fc456828d2c7d69712cee52bec1faa968bf274d60442ca33ef7f412badd2d1de",
    ]

    assert payloads[0]["hud"]["weapon"] == "rocket_launcher"
    assert payloads[-1]["sequence"] == 3
