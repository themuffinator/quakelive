#!/usr/bin/env python3
"""Execute deterministic harness suites and materialise CI artefacts."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.tests.client_regression import ClientPredictor, ClientRegressionHarness
from tools.tests.match_sim.harness import run_from_file
from tools.tests.re_trace_harness import run_trace_harness
SCENARIO_ROOT = REPO_ROOT / "tools" / "tests" / "match_sim"
SCENARIOS: dict[str, Path] = {
    "duel": SCENARIO_ROOT / "sample_scenario.json",
    "overtime": SCENARIO_ROOT / "overtime_scenario.json",
    "loadouts": SCENARIO_ROOT / "complex_loadouts.json",
    "factory": SCENARIO_ROOT / "factory_cvars.json",
}
DEFAULT_SCENARIO = SCENARIOS["duel"]
DEFAULT_SNAPSHOTS = REPO_ROOT / "tools" / "tests" / "client_regression" / "sample_snapshots.json"


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run_match_harness(target: str, artifact_root: Path, seed: int) -> None:
    summaries: list[dict[str, object]] = []
    for slug, scenario_path in SCENARIOS.items():
        timeline_path = artifact_root / "match_sim" / target / slug / "timeline.json"
        result = run_from_file(scenario_path, seed=seed, output_path=timeline_path)

        summaries.append(
            {
                "target": target,
                "slug": slug,
                "scenario": str(scenario_path.relative_to(REPO_ROOT)),
                "seed": seed,
                "frame_count": len(result.frames),
                "duration_seconds": result.frames[-1].time if result.frames else 0.0,
                "bots": sorted(result.frames[0].bots.keys()) if result.frames else [],
            }
        )

    index_path = artifact_root / "match_sim" / target / "index.json"
    _write_text(index_path, json.dumps(summaries, indent=2) + "\n")

    summary_log = artifact_root / "logs" / target / "match_sim.log"
    _write_text(
        summary_log,
        "Match simulation harness completed successfully.\n"
        + json.dumps(summaries, indent=2)
        + "\n",
    )


def _run_client_harness(target: str, artifact_root: Path) -> None:
    harness = ClientRegressionHarness(ClientPredictor())

    manifest: dict[str, dict[str, object]] = {}
    log_entries: list[dict[str, object]] = []

    for scenario, archive in SNAPSHOT_ARCHIVES.items():
        archive_payload = json.loads(archive.read_text(encoding="utf-8"))
        metadata = archive_payload.get("metadata", {})
        snapshots = harness.load_snapshots(archive)
        frames = list(harness.replay(snapshots))

        payloads = [harness.frame_to_payload(frame) for frame in frames]
        manifest[scenario] = {
            "metadata": metadata,
            "frames": payloads,
        }

        log_entries.append(
            {
                "scenario": scenario,
                "archive": str(archive.relative_to(REPO_ROOT)),
                "metadata": metadata,
                "frameCount": len(payloads),
                "hashes": [frame["hash"] for frame in payloads],
            }
        )

    hashes_path = artifact_root / "client_regression" / target / "hud_hashes.json"
    _write_text(hashes_path, json.dumps(manifest, indent=2) + "\n")

    log_path = artifact_root / "logs" / target / "client_regression.log"
    log_text = (
        "Client regression harness generated HUD hashes for captured scenarios.\n"
        + json.dumps(log_entries, indent=2)
        + "\n"
    )
    _write_text(log_path, log_text)


def _ensure_reverse_build(target: str, reverse_build_root: Path) -> None:
    """Run the clean-room build helper so trace harnesses have binaries."""

    if target != "re":
        return

    build_script = REPO_ROOT / "tools" / "ci" / "build-cleanroom.sh"
    if not build_script.exists():
        raise FileNotFoundError(f"Missing clean-room build helper: {build_script}")

    # Execute the helper from the repository root so relative paths align with CI.
    subprocess.run([str(build_script)], check=True, cwd=str(REPO_ROOT))

    if reverse_build_root.name.lower() == "windows":
        extension = ".dll"
    else:
        extension = ".so"

    expected_outputs = ["qlr_client_frame", "qlr_game_frame"]
    missing = [
        name
        for name in expected_outputs
        if not (reverse_build_root / f"{name}{extension}").exists()
    ]
    if missing:
        formatted = ", ".join(missing)
        raise FileNotFoundError(
            "Clean-room build did not produce expected artefacts: " f"{formatted}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic harness suites and emit artefacts.")
    parser.add_argument(
        "--target",
        choices=("qvm", "dll", "re"),
        required=True,
        help="Build target driving the harness run",
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=Path("artifacts") / "tests",
        help="Destination root for artefacts (defaults to artifacts/tests).",
    )
    parser.add_argument("--seed", type=int, default=2024, help="Seed override for deterministic simulations")
    parser.add_argument(
        "--reverse-build-root",
        type=Path,
        default=Path("build") / "re" / ("windows" if os.name == "nt" else "linux"),
        help="Location of clean-room binaries for the trace harness.",
    )
    args = parser.parse_args(argv)

    artifact_root = args.artifact_root
    artifact_root.mkdir(parents=True, exist_ok=True)

    _ensure_reverse_build(args.target, args.reverse_build_root)

    _run_match_harness(args.target, artifact_root, args.seed)
    _run_client_harness(args.target, artifact_root)

    if args.target == "re":
        trace_artifact_root = artifact_root / "trace" / args.target
        expectation = REPO_ROOT / "tests" / "expectations" / "re" / "native-shim.log"
        result = run_trace_harness(args.reverse_build_root, expectation, trace_artifact_root)

        summary_log = artifact_root / "logs" / args.target / "trace_harness.log"
        status = "matched" if result.matches_expectation else "differs"
        _write_text(
            summary_log,
            (
                "Trace harness run completed successfully.\n"
                f"Observed log: {result.log_path}\n"
                f"Diff output: {result.diff_path}\n"
                f"Expectation status: {status}\n"
            ),
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
