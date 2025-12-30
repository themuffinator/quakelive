"""Diff deterministic harness outputs to spot behaviour drifts."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Mapping, MutableMapping, Sequence


@dataclass
class RunSummary:
    """Captured metrics for a single harness run."""

    target: str
    match: Dict[str, object]
    client: Dict[str, object]

    def to_json(self) -> str:
        return json.dumps({"target": self.target, "match": self.match, "client": self.client}, indent=2, sort_keys=True)


@dataclass
class DiffSummary:
    """Human-consumable diff between two :class:`RunSummary` instances."""

    baseline: str
    candidate: str
    severity: str
    scoreboard: Sequence[str]
    events: Sequence[str]
    frames: Sequence[str]
    final_state: Sequence[str]

    def to_json(self) -> str:
        payload = {
            "baseline": self.baseline,
            "candidate": self.candidate,
            "severity": self.severity,
            "scoreboard": list(self.scoreboard),
            "events": list(self.events),
            "frames": list(self.frames),
            "final_state": list(self.final_state),
        }
        return json.dumps(payload, indent=2, sort_keys=True)

    def format_report(self) -> str:
        sections = [
            f"Behaviour Diff Report: {self.baseline} → {self.candidate}",
            f"Severity: {self.severity.upper()}",
            "",
        ]
        sections.extend(_format_section("Scoreboard", self.scoreboard))
        sections.extend(_format_section("Events", self.events))
        sections.extend(_format_section("Frame Hashes", self.frames))
        sections.extend(_format_section("Final State", self.final_state))
        return "\n".join(sections).rstrip() + "\n"


def _format_section(title: str, lines: Sequence[str]) -> Iterable[str]:
    yield f"{title}:"
    if lines:
        yield from (f"  - {line}" for line in lines)
    else:
        yield "  (no discrepancies)"
    yield ""


def _load_json(path: Path) -> Mapping[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_match_timeline(root: Path, target: str) -> Path:
    latest_root = root / "match_sim" / target / "latest"
    index_path = latest_root / "index.json"
    if index_path.exists():
        entries = _load_json(index_path)
        if isinstance(entries, Sequence):
            duel_entry = next(
                (entry for entry in entries if isinstance(entry, Mapping) and entry.get("slug") == "duel"),
                None,
            )
            pick = duel_entry or (entries[0] if entries else None)
            if isinstance(pick, Mapping):
                slug = pick.get("slug")
                if isinstance(slug, str):
                    candidate = latest_root / slug / "timeline.json"
                    if candidate.exists():
                        return candidate
    if latest_root.exists():
        candidates = sorted(latest_root.glob("*/timeline.json"))
        if candidates:
            return candidates[0]
    legacy = root / "match_sim" / target / "timeline.json"
    if legacy.exists():
        return legacy
    raise FileNotFoundError(f"Missing match simulation timeline under {latest_root}")


def _resolve_client_hashes(root: Path, target: str) -> Path:
    latest = root / "client_regression" / target / "latest" / "hud_hashes.json"
    if latest.exists():
        return latest
    legacy = root / "client_regression" / target / "hud_hashes.json"
    if legacy.exists():
        return legacy
    raise FileNotFoundError(f"Missing client HUD hashes under {latest.parent}")


def _summarise_match(frames: Sequence[Mapping[str, object]]) -> Dict[str, object]:
    event_counts: Counter[str] = Counter()
    score_totals: MutableMapping[str, float] = defaultdict(float)
    damage_totals: MutableMapping[str, float] = defaultdict(float)
    heal_totals: MutableMapping[str, float] = defaultdict(float)
    kill_totals: Counter[str] = Counter()

    for frame in frames:
        for event in frame.get("events", []):
            action = str(event.get("action", "unknown"))
            event_counts[action] += 1
            actor = str(event.get("bot") or event.get("team") or "unknown")
            details = event.get("details")
            if isinstance(details, Mapping):
                if "score" in details:
                    score_totals[actor] += float(details["score"])
                if "points" in details:
                    score_totals[actor] += float(details["points"])
                if "amount" in details:
                    amount = float(details["amount"])
                    if action == "damage":
                        damage_totals[actor] += amount
                    elif action == "heal":
                        heal_totals[actor] += amount
                if details.get("result") in {"frag", "kill"} or action in {"frag", "kill"}:
                    kill_totals[actor] += 1

    final_state: Dict[str, Dict[str, float]] = {}
    if frames:
        for name, payload in frames[-1].get("bots", {}).items():
            inventory = payload.get("inventory", {})
            armor = None
            if isinstance(inventory, Mapping):
                armor = inventory.get("armor")
            final_state[str(name)] = {
                "health": float(payload.get("health", 0.0)),
                "armor": float(armor) if armor is not None else None,
            }

    return {
        "frame_count": len(frames),
        "duration": float(frames[-1].get("time", 0.0) if frames else 0.0),
        "events": {
            "total": sum(event_counts.values()),
            "by_action": dict(sorted(event_counts.items())),
        },
        "scoreboard": dict(sorted(score_totals.items())),
        "damage": dict(sorted(damage_totals.items())),
        "healing": dict(sorted(heal_totals.items())),
        "frags": dict(sorted(kill_totals.items())),
        "final_state": final_state,
    }


def _summarise_client(frames: Sequence[Mapping[str, object]]) -> Dict[str, object]:
    hashes = {int(frame["sequence"]): str(frame["hash"]) for frame in frames}
    return {
        "frame_count": len(frames),
        "hashes": {str(seq): hash_value for seq, hash_value in sorted(hashes.items())},
    }


def summarise_run(root: Path, target: str) -> RunSummary:
    match_path = _resolve_match_timeline(root, target)
    client_path = _resolve_client_hashes(root, target)

    timeline = _load_json(match_path)
    match_summary = _summarise_match(timeline.get("frames", []))

    hashes_payload = _load_json(client_path)
    if isinstance(hashes_payload, Mapping):
        frames = hashes_payload.get("frames")
        if isinstance(frames, Sequence):
            client_summary = _summarise_client(frames)  # type: ignore[arg-type]
        else:
            raise ValueError("Client regression payload missing 'frames' list")
    elif isinstance(hashes_payload, Sequence):
        client_summary = _summarise_client(hashes_payload)  # type: ignore[arg-type]
    else:
        raise TypeError("Unsupported structure for HUD hashes payload")

    return RunSummary(target=target, match=match_summary, client=client_summary)


def _diff_dict(baseline: Mapping[str, float], candidate: Mapping[str, float]) -> list[str]:
    lines: list[str] = []
    keys = sorted(set(baseline) | set(candidate))
    for key in keys:
        base_value = baseline.get(key)
        cand_value = candidate.get(key)
        if base_value == cand_value:
            continue
        lines.append(f"{key}: {base_value} → {cand_value}")
    return lines


def _diff_event_counts(baseline: Mapping[str, object], candidate: Mapping[str, object]) -> list[str]:
    base_events = baseline.get("by_action", {}) if isinstance(baseline, Mapping) else {}
    cand_events = candidate.get("by_action", {}) if isinstance(candidate, Mapping) else {}
    return _diff_dict({str(k): float(v) for k, v in base_events.items()}, {str(k): float(v) for k, v in cand_events.items()})


def _diff_final_state(baseline: Mapping[str, object], candidate: Mapping[str, object]) -> list[str]:
    lines: list[str] = []
    keys = sorted(set(baseline) | set(candidate))
    for key in keys:
        base_payload = baseline.get(key, {}) if isinstance(baseline, Mapping) else {}
        cand_payload = candidate.get(key, {}) if isinstance(candidate, Mapping) else {}
        for attr in {"health", "armor"}:
            base_value = base_payload.get(attr) if isinstance(base_payload, Mapping) else None
            cand_value = cand_payload.get(attr) if isinstance(cand_payload, Mapping) else None
            if base_value == cand_value:
                continue
            lines.append(f"{key}.{attr}: {base_value} → {cand_value}")
    return lines


def _diff_hashes(baseline: Mapping[str, object], candidate: Mapping[str, object]) -> list[str]:
    base_hashes = baseline.get("hashes", {}) if isinstance(baseline, Mapping) else {}
    cand_hashes = candidate.get("hashes", {}) if isinstance(candidate, Mapping) else {}
    lines: list[str] = []
    keys = sorted(set(base_hashes) | set(cand_hashes), key=lambda value: int(value))
    for key in keys:
        base_value = base_hashes.get(key)
        cand_value = cand_hashes.get(key)
        if base_value == cand_value:
            continue
        if base_value is None:
            lines.append(f"Sequence {key} missing from baseline (candidate={cand_value})")
        elif cand_value is None:
            lines.append(f"Sequence {key} missing from candidate (baseline={base_value})")
        else:
            lines.append(f"Sequence {key}: {base_value} → {cand_value}")
    return lines


def diff_runs(baseline: RunSummary, candidate: RunSummary) -> DiffSummary:
    scoreboard = _diff_dict(
        baseline.match.get("scoreboard", {}),
        candidate.match.get("scoreboard", {}),
    )
    events = _diff_event_counts(baseline.match.get("events", {}), candidate.match.get("events", {}))
    final_state = _diff_final_state(
        baseline.match.get("final_state", {}),
        candidate.match.get("final_state", {}),
    )
    frames = _diff_hashes(baseline.client, candidate.client)

    severity = _resolve_severity(scoreboard=scoreboard, frames=frames, events=events, final_state=final_state)

    return DiffSummary(
        baseline=baseline.target,
        candidate=candidate.target,
        severity=severity,
        scoreboard=scoreboard,
        events=events,
        frames=frames,
        final_state=final_state,
    )


def _resolve_severity(
    *, scoreboard: Sequence[str], frames: Sequence[str], events: Sequence[str], final_state: Sequence[str]
) -> str:
    level = 0
    if scoreboard or frames:
        level = max(level, 3)
    if events:
        level = max(level, 2)
    if final_state and level < 3:
        level = max(level, 2)
    return {0: "none", 1: "low", 2: "medium", 3: "high"}[level]


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diff deterministic harness outputs.")
    parser.add_argument("--baseline-root", type=Path, required=True, help="Root directory for baseline artefacts")
    parser.add_argument("--baseline-target", required=True, help="Baseline target identifier (e.g. qvm)")
    parser.add_argument("--candidate-root", type=Path, help="Root directory for candidate artefacts (defaults to baseline root)")
    parser.add_argument("--candidate-target", required=True, help="Candidate target identifier (e.g. dll)")
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Destination directory for summaries and diff reports.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    candidate_root = args.candidate_root or args.baseline_root

    baseline = summarise_run(args.baseline_root, args.baseline_target)
    candidate = summarise_run(candidate_root, args.candidate_target)
    diff = diff_runs(baseline, candidate)

    args.output.mkdir(parents=True, exist_ok=True)

    _write_text(args.output / f"summary_{baseline.target}.json", baseline.to_json() + "\n")
    _write_text(args.output / f"summary_{candidate.target}.json", candidate.to_json() + "\n")
    _write_text(args.output / "diff.json", diff.to_json() + "\n")
    report = diff.format_report()
    _write_text(args.output / "diff_report.txt", report)

    print(report, end="")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
