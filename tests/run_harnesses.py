#!/usr/bin/env python3
"""Execute deterministic harness suites and materialise CI artefacts."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.tests.client_regression import ClientPredictor, ClientRegressionHarness
from tools.tests.match_sim.harness import run_from_file
from tools.tests.re_trace_harness import run_trace_harness
DEFAULT_SCENARIO = REPO_ROOT / "tools" / "tests" / "match_sim" / "sample_scenario.json"
DEFAULT_SNAPSHOTS = REPO_ROOT / "tools" / "tests" / "client_regression" / "sample_snapshots.json"


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run_match_harness(target: str, artifact_root: Path, seed: int) -> None:
    timeline_path = artifact_root / "match_sim" / target / "timeline.json"
    result = run_from_file(DEFAULT_SCENARIO, seed=seed, output_path=timeline_path)

    summary = {
        "target": target,
        "scenario": str(DEFAULT_SCENARIO.relative_to(REPO_ROOT)),
        "seed": seed,
        "frame_count": len(result.frames),
        "duration_seconds": result.frames[-1].time if result.frames else 0.0,
        "bots": sorted(result.frames[0].bots.keys()) if result.frames else [],
    }
    summary_log = artifact_root / "logs" / target / "match_sim.log"
    _write_text(summary_log, "Match simulation harness completed successfully.\n" + json.dumps(summary, indent=2) + "\n")


def _run_client_harness(target: str, artifact_root: Path) -> None:
    harness = ClientRegressionHarness(ClientPredictor())
    snapshots = harness.load_snapshots(DEFAULT_SNAPSHOTS)
    frames = list(harness.replay(snapshots))

    hashes = [
        {
            "sequence": frame.sequence,
            "serverTime": frame.server_time,
            "hash": frame.hud_hash,
        }
        for frame in frames
    ]

    hashes_path = artifact_root / "client_regression" / target / "hud_hashes.json"
    _write_text(hashes_path, json.dumps(hashes, indent=2) + "\n")

    log_path = artifact_root / "logs" / target / "client_regression.log"
    _write_text(
        log_path,
        "Client regression harness generated HUD hashes.\n" + json.dumps(hashes, indent=2) + "\n",
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
