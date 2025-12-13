"""Unit tests covering the client regression harness."""

from __future__ import annotations

from pathlib import Path

import json

import pytest

from tools.tests.client_regression import ClientPredictor, ClientRegressionHarness

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def sample_snapshots_path() -> Path:
    return Path(__file__).parent / "client_regression" / "sample_snapshots.json"


@pytest.fixture()
def regression_archive_dir() -> Path:
    return Path(__file__).parent / "client_regression"


@pytest.fixture()
def retail_netdump_path() -> Path:
    return REPO_ROOT / "tests" / "netdumps" / "retail_duel.snap.json"


@pytest.fixture()
def retail_baseline_path() -> Path:
    return Path(__file__).parent / "client_regression" / "retail_netdump_baseline.json"


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


def test_retail_netdump_frames_match_baseline(
    retail_netdump_path: Path, retail_baseline_path: Path
) -> None:
    harness = ClientRegressionHarness(ClientPredictor())
    snapshots, metadata = harness.load_netdump(retail_netdump_path)
    payloads = harness.replay_to_payloads(snapshots)

    baseline = json.loads(retail_baseline_path.read_text(encoding="utf-8"))
    expected = baseline["frames"]

    assert metadata.get("source") == baseline["metadata"]["source"]
    assert len(payloads) == len(expected)

    for payload, expected_frame in zip(payloads, expected):
        assert (payload["sequence"], payload["serverTime"]) == (
            expected_frame["sequence"],
            expected_frame["serverTime"],
        )
        assert payload["hash"] == expected_frame["hash"]
        assert payload["usercmdHash"] == expected_frame["usercmdHash"]


@pytest.mark.parametrize(
    ("archive_name", "expected_hashes"),
    [
        (
            "weapons_and_items_snapshots.json",
            [
                "50cc3bf0beb765c921b9cc3975cc611356ead31c522ffa9510963d3468ebf28d",
                "d50a4ede5b09d25864802265283488288b5227f8f5fa53e32eba76e3f8224ef3",
                "b0d4bc9d00594d0e65346d309f2cec2733a6d8d80c2801576f836f50378d3af1",
                "822dc1c14922b22b10010c58e9356d09fc37455599208f1509d5e02cff22db98",
            ],
        ),
        (
            "server_correction_snapshots.json",
            [
                "b8f8c3a4ee5da098cb9742ee0ea7d223031a028a501be204cbf04addfeeaa9ea",
                "88169c344538663fe617fff5f766e93a9861da1c17189a07d14a868205ee1e6d",
                "e79954ecd8b60788ba3f29caf923f9a305421434975c9649d031db1dbc931357",
                "eb79d52ca2a24dd508f66a0a538b68b13e2e5e42df845222c7e66cfc8151d9e5",
                "b03c5b2c6821be17da30c244636ddc65ed2f4d6b5df0004130a9d768ac7e314f",
            ],
        ),
        (
            "resource_drain_snapshots.json",
            [
                "36e4b60a34bf875d6b457ee4db3cd806be8b9efa5208314ba8d0d4d21cd0d630",
                "dfe4acd3d186ad813f469da5a267c538289a6faa5c0542766bafa69736004101",
                "503a6129457b9fae4ae216d262037a6e3b559bdbe5b714180164d26af4b59664",
                "f50331e421913018229f3c6bbf140f48347162d8a2bac38d24ef00b7d0e1e4eb",
                "abcf77c69e98c7792800435c09229ea664e912cde7376742e11ddcb4f614b94c",
            ],
        ),
    ],
)
def test_reference_archives_produce_expected_hashes(
    regression_archive_dir: Path, archive_name: str, expected_hashes: list[str]
) -> None:
    harness = ClientRegressionHarness(ClientPredictor())
    archive_path = regression_archive_dir / archive_name
    snapshots = harness.load_snapshots(archive_path)

    hashes = [frame.hud_hash for frame in harness.replay(snapshots)]

    assert hashes == expected_hashes
