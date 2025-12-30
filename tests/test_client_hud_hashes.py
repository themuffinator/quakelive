"""Ensure HUD hashes remain aligned between VM and DLL targets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTIFACT_ROOT = REPO_ROOT / "artifacts" / "tests" / "client_regression"


def _load_manifest(target: str) -> Dict[str, List[Mapping[str, object]]]:
    path = ARTIFACT_ROOT / target / "latest" / "hud_hashes.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(payload, list):
        return {"default": payload}
    if not isinstance(payload, dict):  # pragma: no cover - defensive guard
        raise TypeError("hud_hashes.json payload must be a dictionary or list")

    manifest: Dict[str, List[Mapping[str, object]]] = {}
    for scenario, entry in payload.items():
        frames: Iterable[Mapping[str, object]] = entry.get("frames", [])
        manifest[scenario] = [
            {
                "sequence": int(frame["sequence"]),
                "serverTime": int(frame["serverTime"]),
                "hash": str(frame["hash"]),
            }
            for frame in frames
        ]

    return manifest


def _assert_sequences_match(expected: List[Mapping[str, object]], actual: List[Mapping[str, object]], scenario: str) -> None:
    assert len(expected) == len(actual), f"Frame count mismatch for {scenario}"
    for index, (expected_frame, actual_frame) in enumerate(zip(expected, actual)):
        assert (expected_frame["sequence"], expected_frame["serverTime"]) == (
            actual_frame["sequence"],
            actual_frame["serverTime"],
        ), f"Timeline diverged for {scenario} at index {index}"
        assert expected_frame["hash"] == actual_frame["hash"], f"HUD hash mismatch for {scenario} at index {index}"


def test_client_hud_hashes_match_between_targets():
    """Validate that VM and DLL harness captures produce identical HUD hashes."""

    qvm_manifest = _load_manifest("qvm")
    dll_manifest = _load_manifest("dll")

    assert qvm_manifest, "Expected QVM HUD hash manifest to be populated"
    assert dll_manifest, "Expected DLL HUD hash manifest to be populated"

    assert set(qvm_manifest) == set(dll_manifest)

    for scenario in sorted(qvm_manifest):
        _assert_sequences_match(qvm_manifest[scenario], dll_manifest[scenario], scenario)
