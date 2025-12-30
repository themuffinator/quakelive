#!/usr/bin/env python3
"""Execute deterministic harness suites and materialise CI artefacts."""
from __future__ import annotations

import argparse
import json
import os
import re
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
    "rating_metadata": SCENARIO_ROOT / "rating_metadata.json",
    "ruleset_pql": SCENARIO_ROOT / "ruleset_pql.json",
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
    "round_overtime": SNAPSHOT_ROOT / "round_overtime_snapshots.json",
}
NETDUMP_ROOT = REPO_ROOT / "tests" / "netdumps"
NETDUMP_BASELINE = SNAPSHOT_ROOT / "retail_netdump_baseline.json"
HUD_ASPECT_RATIOS: tuple[str, ...] = ("4x3", "16x9", "21x9")
COMPETITIVE_HUD_CONFIG: dict[str, object] = {
    "cg_useCompetitiveHud": True,
    "hudFiles": ["ui/hud.txt", "ui/hud3.menu"],
    "description": "Competitive HUD assets enabled for captures",
}
WEAPON_ENUM_ALIASES: dict[str, str] = {
    "BFG": "WP_BFG",
    "Chaingun": "WP_CHAINGUN",
    "Gauntlet": "WP_GAUNTLET",
    "Grappling Hook": "WP_GRAPPLING_HOOK",
    "Grenade Launcher": "WP_GRENADE_LAUNCHER",
    "Heavy Machinegun": "WP_HEAVY_MACHINEGUN",
    "Lightning Gun": "WP_LIGHTNING",
    "Machinegun": "WP_MACHINEGUN",
    "Nailgun": "WP_NAILGUN",
    "Plasmagun": "WP_PLASMAGUN",
    "Proximity Launcher": "WP_PROX_LAUNCHER",
    "Railgun": "WP_RAILGUN",
    "Rocket Launcher": "WP_ROCKET_LAUNCHER",
    "Shotgun": "WP_SHOTGUN",
}
REFERENCE_BG_PMOVE = REPO_ROOT / "references" / "hlil" / "quakelive" / "qagamex86.dll_split" / "bg_pmove.md"
BG_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"
BG_MISC_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_misc.c"


@dataclass(slots=True)
class HarnessBundleResult:
    """Summary of a harness bundle invocation for a specific target."""

    target: str
    artifact_root: Path
    match_summaries: list[dict[str, object]]
    client_regression_entries: list[dict[str, object]]
    retail_netdump_entries: list[dict[str, object]]
    hud_captures: list[dict[str, object]]
    weapon_timings: dict[str, object]
    trace_result: TraceHarnessResult | None = None

    def _suite_root(self, suite: str) -> Path:
        return self.artifact_root / suite / self.target / "latest"

    def match_timeline_path(self, slug: str) -> Path:
        return self._suite_root("match_sim") / slug / "timeline.json"

    def load_match_timeline(self, slug: str) -> dict[str, object]:
        timeline_path = self.match_timeline_path(slug)
        return json.loads(timeline_path.read_text(encoding="utf-8"))

    def log_path(self, harness_name: str) -> Path:
        return self._suite_root("logs") / f"{harness_name}.log"

    def read_log(self, harness_name: str) -> str:
        return self.log_path(harness_name).read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, object]) -> None:
    _write_text(path, json.dumps(payload, indent=2) + "\n")


def _suite_root(artifact_root: Path, suite: str, target: str) -> Path:
    return artifact_root / suite / target / "latest"


def _current_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def _weapon_to_enum_name(weapon: str) -> str:
    """Convert a human-friendly weapon label to its enum constant name."""

    return WEAPON_ENUM_ALIASES.get(weapon, f"WP_{weapon.upper().replace(' ', '_')}")


def _parse_reference_tables(reference_path: Path) -> tuple[dict[str, int], dict[str, dict[str, int]]]:
    """Extract reload/refire and ammo pickup values from the HLIL reference tables."""

    reloads: dict[str, int] = {}
    ammo: dict[str, dict[str, int]] = {}
    section: str | None = None

    for line in reference_path.read_text(encoding="utf-8").splitlines():
        striped = line.strip()
        if striped.startswith("## Weapon Reload Times"):
            section = "reload"
            continue
        if striped.startswith("## Ammo Pickup"):
            section = "ammo"
            continue
        if not striped.startswith("|") or striped.startswith("| ---"):
            continue

        cells = [part.strip() for part in striped.strip("|").split("|")]

        weapon = cells[0]
        if section == "reload":
            if len(cells) < 2:
                continue
            try:
                reloads[weapon] = int(cells[1])
            except ValueError:
                continue
        elif section == "ammo":
            if len(cells) < 3:
                continue
            try:
                pickup = int(cells[1])
                max_stack = int(cells[2])
            except ValueError:
                continue
            ammo[weapon] = {"pickup": pickup, "max_stack": max_stack}

    return reloads, ammo


def _parse_reload_defaults(pmove_path: Path) -> dict[str, int]:
    """Read the designated reload defaults from `bg_pmove.c`."""

    reloads: dict[str, int] = {}
    within_table = False
    pattern = re.compile(r"\[(WP_[A-Z0-9_]+)\]\s*=\s*(\d+)")

    for line in pmove_path.read_text(encoding="utf-8").splitlines():
        if "weaponReloadTimes" in line:
            within_table = True

        if within_table:
            if "}" in line:
                within_table = False
                continue
            match = pattern.search(line)
            if match:
                weapon, value = match.groups()
                reloads[weapon] = int(value)

    return reloads


def _parse_ammo_pickups(misc_path: Path) -> dict[str, dict[str, int]]:
    """Read pickup and max stack defaults from `bg_misc.c`."""

    ammo: dict[str, dict[str, int]] = {}
    within_table = False
    pattern = re.compile(r"\{\s*(WP_[A-Z0-9_]+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)")

    for line in misc_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("const bgWeaponStats_t bg_weaponStats"):
            within_table = True
            continue
        if within_table and line.strip().startswith("};"):
            within_table = False
            continue
        if within_table:
            match = pattern.search(line)
            if match:
                weapon, pickup, max_stack = match.groups()
                ammo[weapon] = {"pickup": int(pickup), "max_stack": int(max_stack)}

    return ammo


def _load_netdump_baseline(path: Path) -> dict[tuple[int, int], dict[str, object]]:
    """Load hashed baselines keyed by (sequence, serverTime)."""

    if not path.exists():
        return {}

    payload = json.loads(path.read_text(encoding="utf-8"))
    frames = payload.get("frames", [])
    baseline: dict[tuple[int, int], dict[str, object]] = {}

    for frame in frames:
        seq = int(frame["sequence"])
        server_time = int(frame["serverTime"])
        baseline[(seq, server_time)] = {
            "hash": str(frame.get("hash", "")),
            "usercmdHash": str(frame.get("usercmdHash", "")),
        }

    return baseline


def _run_weapon_timing_harness(target: str, artifact_root: Path, commit_hash: str) -> dict[str, object]:
    """Emit deterministic weapon timing baselines for CI parity checks."""

    reference_reload, reference_ammo = _parse_reference_tables(REFERENCE_BG_PMOVE)
    repo_reload = _parse_reload_defaults(BG_PMOVE_PATH)
    repo_ammo = _parse_ammo_pickups(BG_MISC_PATH)

    weapon_names = sorted({*reference_reload.keys(), *reference_ammo.keys()})
    reload_entries: dict[str, dict[str, object]] = {}
    ammo_entries: dict[str, dict[str, object]] = {}

    for weapon in weapon_names:
        ref_reload = reference_reload.get(weapon)
        repo_key = _weapon_to_enum_name(weapon)
        observed_reload = repo_reload.get(repo_key)
        reload_entries[weapon] = {
            "reference_ms": ref_reload,
            "repo_ms": observed_reload,
            "matches": ref_reload == observed_reload,
        }

        ref_ammo = reference_ammo.get(weapon, {})
        observed_ammo = repo_ammo.get(repo_key, {})
        ammo_entries[weapon] = {
            "reference_pickup": ref_ammo.get("pickup"),
            "repo_pickup": observed_ammo.get("pickup"),
            "reference_max_stack": ref_ammo.get("max_stack"),
            "repo_max_stack": observed_ammo.get("max_stack"),
            "matches": (ref_ammo.get("pickup") == observed_ammo.get("pickup"))
            and (ref_ammo.get("max_stack") == observed_ammo.get("max_stack")),
        }

    payload = {
        "target": target,
        "commit": commit_hash,
        "reference": str(REFERENCE_BG_PMOVE.relative_to(REPO_ROOT)),
        "reload_times": reload_entries,
        "ammo_pickups": ammo_entries,
        "sources": {
            "bg_pmove": str(BG_PMOVE_PATH.relative_to(REPO_ROOT)),
            "bg_misc": str(BG_MISC_PATH.relative_to(REPO_ROOT)),
        },
    }

    output_path = _suite_root(artifact_root, "weapon_timings", target) / "baseline.json"
    _write_json(output_path, payload)

    mismatches = [
        weapon
        for weapon, entry in reload_entries.items()
        if entry.get("reference_ms") is not None and not entry.get("matches")
    ]
    ammo_mismatches = [
        weapon
        for weapon, entry in ammo_entries.items()
        if entry.get("reference_pickup") is not None and not entry.get("matches")
    ]
    log_lines = [
        "Weapon timing harness completed successfully.",
        f"Baseline path: {output_path}",
    ]
    if mismatches:
        log_lines.append(f"Reload mismatches: {', '.join(sorted(mismatches))}")
    if ammo_mismatches:
        log_lines.append(f"Ammo mismatches: {', '.join(sorted(ammo_mismatches))}")

    log_path = _suite_root(artifact_root, "logs", target) / "weapon_timings.log"
    _write_text(log_path, "\n".join(log_lines) + "\n")

    return payload


def _run_match_harness(target: str, artifact_root: Path, seed: int) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for slug, scenario_path in SCENARIOS.items():
        timeline_path = _suite_root(artifact_root, "match_sim", target) / slug / "timeline.json"
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
                "metadata": result.config.metadata,
                "ruleset": result.config.metadata.get("ruleset"),
            }
        )

    index_path = _suite_root(artifact_root, "match_sim", target) / "index.json"
    _write_text(index_path, json.dumps(summaries, indent=2) + "\n")

    summary_log = _suite_root(artifact_root, "logs", target) / "match_sim.log"
    _write_text(
        summary_log,
        "Match simulation harness completed successfully.\n"
        + json.dumps(summaries, indent=2)
        + "\n",
    )

    return summaries


def _run_client_harness(
    target: str, artifact_root: Path, harness: ClientRegressionHarness | None = None
) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    harness = harness or ClientRegressionHarness(ClientPredictor())

    manifest: dict[str, dict[str, object]] = {}
    log_entries: list[dict[str, object]] = []
    capture_payloads: dict[str, dict[str, object]] = {}

    for scenario in sorted(SNAPSHOT_ARCHIVES.keys()):
        archive = SNAPSHOT_ARCHIVES[scenario]
        archive_payload = json.loads(archive.read_text(encoding="utf-8"))
        metadata = archive_payload.get("metadata", {})
        snapshots = harness.load_snapshots(archive)
        frames = list(harness.replay(snapshots))

        payloads = [harness.frame_to_payload(frame) for frame in frames]
        manifest[scenario] = {
            "metadata": metadata,
            "frames": payloads,
        }

        capture_payloads[scenario] = {
            "frames": payloads,
            "metadata": metadata,
            "archive": str(archive.relative_to(REPO_ROOT)),
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

    hashes_path = _suite_root(artifact_root, "client_regression", target) / "hud_hashes.json"
    _write_json(hashes_path, manifest)

    log_path = _suite_root(artifact_root, "logs", target) / "client_regression.log"
    log_text = (
        "Client regression harness generated HUD hashes for captured scenarios.\n"
        + json.dumps(log_entries, indent=2)
        + "\n"
    )
    _write_text(log_path, log_text)

    return log_entries, capture_payloads


def _run_retail_netdump_harness(
    target: str, artifact_root: Path, harness: ClientRegressionHarness
) -> list[dict[str, object]]:
    """Replay captured retail netdumps and emit hash comparisons."""

    if not NETDUMP_ROOT.exists():
        return []

    baseline_map = _load_netdump_baseline(NETDUMP_BASELINE)
    entries: list[dict[str, object]] = []
    log_entries: list[dict[str, object]] = []

    for netdump in sorted(NETDUMP_ROOT.glob("*.json")):
        snapshots, metadata = harness.load_netdump(netdump)
        frames = list(harness.replay(snapshots))
        payloads = [harness.frame_to_payload(frame) for frame in frames]

        frame_entries: list[dict[str, object]] = []
        for payload in payloads:
            key = (payload["sequence"], payload["serverTime"])
            expected = baseline_map.get(key, {})
            frame_entries.append(
                {
                    "sequence": payload["sequence"],
                    "serverTime": payload["serverTime"],
                    "hash": payload.get("hash"),
                    "usercmdHash": payload.get("usercmdHash"),
                    "matchesBaseline": (
                        expected.get("hash") == payload.get("hash")
                        and expected.get("usercmdHash") == payload.get("usercmdHash")
                    ),
                }
            )

        entries.append(
            {
                "netdump": str(netdump.relative_to(REPO_ROOT)),
                "metadata": metadata,
                "frames": frame_entries,
            }
        )

        log_entries.append(
            {
                "netdump": str(netdump.relative_to(REPO_ROOT)),
                "frameCount": len(frame_entries),
                "metadata": metadata,
                "hashes": [frame.get("hash") for frame in frame_entries],
                "usercmdHashes": [frame.get("usercmdHash") for frame in frame_entries],
                "baselineMatches": all(frame.get("matchesBaseline") for frame in frame_entries),
            }
        )

    output_path = _suite_root(artifact_root, "client_regression", target) / "retail_netdump_hashes.json"
    _write_json(output_path, {"entries": entries, "baseline": str(NETDUMP_BASELINE.relative_to(REPO_ROOT))})

    log_path = _suite_root(artifact_root, "logs", target) / "retail_netdump.log"
    _write_text(
        log_path,
        "Retail netdump harness captured HUD and usercmd hashes.\n"
        + json.dumps(log_entries, indent=2)
        + "\n",
    )

    return log_entries


def _run_hud_capture_harness(
    target: str,
    artifact_root: Path,
    capture_payloads: dict[str, dict[str, object]],
    commit_hash: str,
) -> list[dict[str, object]]:
    hud_root = _suite_root(artifact_root, "hud-captures", target)
    hud_root.mkdir(parents=True, exist_ok=True)

    manifest_entries: list[dict[str, object]] = []

    for aspect in HUD_ASPECT_RATIOS:
        aspect_root = hud_root / aspect
        aspect_root.mkdir(parents=True, exist_ok=True)

        for scenario, payload in sorted(capture_payloads.items()):
            frames = payload.get("frames", [])
            metadata = payload.get("metadata", {})
            archive = payload.get("archive")

            capture_payload = {
                "metadata": {
                    "aspect": aspect,
                    "hudConfig": COMPETITIVE_HUD_CONFIG,
                    "commit": commit_hash,
                    "scenario": scenario,
                    "archive": archive,
                    "frames": len(frames),
                    "snapshotMetadata": metadata,
                },
                "frames": frames,
            }

            capture_path = aspect_root / f"{scenario}.json"
            _write_json(capture_path, capture_payload)

            manifest_entries.append(
                {
                    "target": target,
                    "aspect": aspect,
                    "scenario": scenario,
                    "frames": len(frames),
                    "hashes": [frame.get("hash") for frame in frames],
                    "path": str(capture_path.relative_to(artifact_root)),
                    "hudConfig": COMPETITIVE_HUD_CONFIG,
                    "commit": commit_hash,
                }
            )

    manifest = {
        "commit": commit_hash,
        "hudConfig": COMPETITIVE_HUD_CONFIG,
        "captures": manifest_entries,
    }

    manifest_path = hud_root / "manifest.json"
    _write_json(manifest_path, manifest)

    log_path = _suite_root(artifact_root, "logs", target) / "hud_captures.log"
    _write_text(
        log_path,
        "HUD capture harness produced competitive HUD baselines.\n"
        + json.dumps(manifest_entries, indent=2)
        + "\n",
    )

    return manifest_entries


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

    commit_hash = _current_commit()
    harness = ClientRegressionHarness(ClientPredictor())
    weapon_timings = _run_weapon_timing_harness(target, artifact_root, commit_hash)
    match_summaries = _run_match_harness(target, artifact_root, seed)
    client_entries, capture_payloads = _run_client_harness(target, artifact_root, harness)
    netdump_entries = _run_retail_netdump_harness(target, artifact_root, harness)
    hud_captures = _run_hud_capture_harness(target, artifact_root, capture_payloads, commit_hash)

    trace_result: TraceHarnessResult | None = None
    if target == "re":
        trace_artifact_root = _suite_root(artifact_root, "trace", target)
        expectation = REPO_ROOT / "tests" / "expectations" / "re" / "native-shim.log"
        trace_result = run_trace_harness(reverse_build_root, expectation, trace_artifact_root)

        summary_log = _suite_root(artifact_root, "logs", target) / "trace_harness.log"
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
        retail_netdump_entries=netdump_entries,
        hud_captures=hud_captures,
        weapon_timings=weapon_timings,
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
