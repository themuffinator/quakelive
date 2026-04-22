from __future__ import annotations

from pathlib import Path

import pytest

from tests._shared import REPO_ROOT

SCENARIO = REPO_ROOT / "tools" / "tests" / "match_sim" / "cvar_toggles.json"
EXPECTATION = REPO_ROOT / "tests" / "expectations" / "match_sim_cvar_toggles.expect"

from tools.tests.match_sim.harness import run_from_file  # noqa: E402

def _summarise_cvar_events(frames):
    lines = []
    for frame in frames:
        events = getattr(frame, "events", None)
        if events is None and hasattr(frame, "get"):
            events = frame.get("events", [])
        if events is None:
            events = []
        for event in events:
            if event.get("action") != "cvar_toggle":
                continue
            details = event.get("details", {})
            name = details.get("name")
            value = details.get("value")
            lines.append(f"{event.get('time', 0.0):.3f} {name}={value}")
    return "\n".join(lines)

def test_cvar_toggle_timeline_matches_expectation(tmp_path: Path) -> None:
    timeline = run_from_file(SCENARIO)
    summary = _summarise_cvar_events(timeline.frames)
    expected = EXPECTATION.read_text(encoding="utf-8").strip()
    if summary.strip() != expected:
        output_path = tmp_path / "cvar_toggles.actual"
        output_path.write_text(summary, encoding="utf-8")
        pytest.fail(
            "CVar toggle timeline diverged from expectation. "
            f"Captured summary written to {output_path}"
        )

