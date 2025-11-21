#!/usr/bin/env python3
"""Execute deterministic harness suites and materialise CI artefacts."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.tests.client_regression import ClientPredictor, ClientRegressionHarness
from tools.tests.match_sim.harness import run_from_file
from tools.tests.re_trace_harness import TraceHarnessResult, run_trace_harness

SCENARIO_ROOT = REPO_ROOT / "tools" / "tests" / "match_sim"
SCENARIOS: dict[str, Path] = {
    "duel": SCENARIO_ROOT / "sample_scenario.json",
    "overtime": SCENARIO_ROOT / "overtime_scenario.json",
    "loadouts": SCENARIO_ROOT / "complex_loadouts.json",
    "factory": SCENARIO_ROOT / "factory_cvars.json",
    "rotation": SCENARIO_ROOT / "rotation_vote.json",
    "bot_resources": SCENARIO_ROOT / "bot_resource_schedule.json",
    "freeze": SCENARIO_ROOT / "freeze_cvars.json",
    "ctf_flag_cvars": SCENARIO_ROOT / "ctf_flag_cvars.json",
    "clanarena_shuffle": SCENARIO_ROOT / "clanarena_shuffle.json",
    "duel_cvars": SCENARIO_ROOT / "duel_cvars.json",
    "damage_timeline": SCENARIO_ROOT / "damage_timeline.json",
}
DEFAULT_SCENARIO = SCENARIOS["duel"]
SNAPSHOT_ROOT = REPO_ROOT / "tools" / "tests" / "client_regression"
DEFAULT_SNAPSHOTS = SNAPSHOT_ROOT / "sample_snapshots.json"
SNAPSHOT_ARCHIVES: dict[str, Path] = {
    "hud_baseline": DEFAULT_SNAPSHOTS,
    "weapons_and_items": SNAPSHOT_ROOT / "weapons_and_items_snapshots.json",
    "resource_drain": SNAPSHOT_ROOT / "resource_drain_snapshots.json",
    "server_correction": SNAPSHOT_ROOT / "server_correction_snapshots.json",
}


@dataclass(slots=True)
class HarnessBundleResult:
    """Summary of a harness bundle invocation for a specific target."""

    target: str
    artifact_root: Path
    match_summaries: list[dict[str, object]]
    client_regression_entries: list[dict[str, object]]
    trace_result: TraceHarnessResult | None = None

    def match_timeline_path(self, slug: str) -> Path:
        return self.artifact_root / "match_sim" / self.target / slug / "timeline.json"

    def load_match_timeline(self, slug: str) -> dict[str, object]:
        timeline_path = self.match_timeline_path(slug)
        return json.loads(timeline_path.read_text(encoding="utf-8"))

    def log_path(self, harness_name: str) -> Path:
        return self.artifact_root / "logs" / self.target / f"{harness_name}.log"

    def read_log(self, harness_name: str) -> str:
        return self.log_path(harness_name).read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run_match_harness(target: str, artifact_root: Path, seed: int) -> list[dict[str, object]]:
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

    return summaries


def _run_client_harness(target: str, artifact_root: Path) -> list[dict[str, object]]:
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

    return log_entries


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


def run_harness_bundle(
    target: str,
    artifact_root: Path,
    *,
    seed: int = 2024,
    reverse_build_root: Path | None = None,
) -> HarnessBundleResult:
    """Execute the harness bundle for *target* and capture summary metadata."""

    artifact_root.mkdir(parents=True, exist_ok=True)
    if reverse_build_root is None:
        reverse_build_root = Path("build") / "re" / ("windows" if os.name == "nt" else "linux")

    _ensure_reverse_build(target, reverse_build_root)

    match_summaries = _run_match_harness(target, artifact_root, seed)
    client_entries = _run_client_harness(target, artifact_root)

    trace_result: TraceHarnessResult | None = None
    if target == "re":
        trace_artifact_root = artifact_root / "trace" / target
        expectation = REPO_ROOT / "tests" / "expectations" / "re" / "native-shim.log"
        trace_result = run_trace_harness(reverse_build_root, expectation, trace_artifact_root)

        summary_log = artifact_root / "logs" / target / "trace_harness.log"
        status = "matched" if trace_result.matches_expectation else "differs"
        _write_text(
            summary_log,
            (
                "Trace harness run completed successfully.\n"
                f"Observed log: {trace_result.log_path}\n"
                f"Diff output: {trace_result.diff_path}\n"
                f"Expectation status: {status}\n"
            ),
        )

    return HarnessBundleResult(
        target=target,
        artifact_root=artifact_root,
        match_summaries=match_summaries,
        client_regression_entries=client_entries,
        trace_result=trace_result,
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
    run_harness_bundle(
        args.target,
        artifact_root,
        seed=args.seed,
        reverse_build_root=args.reverse_build_root,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
