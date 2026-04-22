"""Tests covering bot resource loaders and spawn schedules."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import pytest

from tests._shared import REPO_ROOT

from tools.tests.match_sim import (
    BotConfig,
    CommandConfig,
    MatchConfig,
    MatchHarness,
    run_from_file,
)

def _collect_spawn_events(frames: Iterable) -> List[dict]:
    events: List[dict] = []
    for frame in frames:
        for event in frame.events:
            if event.get("action") == "client_spawn":
                events.append(event)
    return events

def _summarise_spawn_events(frames: Iterable) -> str:
    lines: List[str] = []
    for frame in frames:
        for event in frame.events:
            if event.get("action") != "client_spawn":
                continue
            details = event.get("details", {})
            alias = details.get("alias")
            issuer = details.get("issuer")
            reason = details.get("reason")
            warmup = details.get("warmup")
            lines.append(
                f"{event['time']:.3f} {event['bot']} alias={alias} warmup={warmup} issuer={issuer} reason={reason}"
            )
    return "\n".join(lines)

def test_bot_spawn_schedule_applies_delays() -> None:
    metadata = {
        "bot_resources": {
            "g_botsFile": [
                {"alias": "scripted_slash", "name": "slash", "team": "blue"},
                {"alias": "scripted_keel", "name": "keel", "team": "red"},
            ],
            "g_botSpawnList": [
                {"bot": "scripted_slash", "delay_ms": 0, "reason": "opening"},
                {"bot": "scripted_keel", "delay_ms": 1500, "reason": "followup"},
                {"bot": "scripted_slash", "delay_ms": 500, "reason": "return"},
            ],
        }
    }
    bots = (
        BotConfig(
            name="slash",
            team="blue",
            script=(CommandConfig(time=0.0, action="wait", params={}),),
        ),
        BotConfig(
            name="keel",
            team="red",
            script=(CommandConfig(time=0.0, action="wait", params={}),),
        ),
    )
    config = MatchConfig(
        map="qzpractice",
        duration=4.0,
        tick_rate=10,
        seed=1337,
        bots=bots,
        metadata=metadata,
    )
    harness = MatchHarness(config, seed=2024)
    result = harness.run()

    spawn_events = _collect_spawn_events(result.frames)
    assert [event["bot"] for event in spawn_events] == ["slash", "keel", "slash"]
    assert [event["time"] for event in spawn_events] == pytest.approx([0.0, 1.5, 2.0])

    # Ensure the resolved schedule is exposed with alias metadata.
    assert [entry["alias"] for entry in result.spawn_schedule] == [
        "scripted_slash",
        "scripted_keel",
        "scripted_slash",
    ]
    assert [entry["bot"] for entry in result.spawn_schedule] == ["slash", "keel", "slash"]
    assert result.bot_profiles["scripted_slash"]["name"] == "slash"

def test_access_permissions_enforced_for_commands() -> None:
    metadata = {
        "bot_resources": {
            "g_accessFile": {
                "commands": {
                    "addbot": {"allow": ["admin"]},
                    "request_spawn": {"allow": ["admin"]},
                },
                "spawns": {
                    "slash": {"allow": ["admin"]}
                },
            }
        }
    }
    slash_bot = BotConfig(
        name="slash",
        team="blue",
        script=(
            CommandConfig(
                time=0.0,
                action="request_spawn",
                params={"issuer": "player", "command": "addbot"},
            ),
            CommandConfig(
                time=1.0,
                action="request_spawn",
                params={"issuer": "admin", "command": "addbot"},
            ),
        ),
    )
    config = MatchConfig(
        map="qzpractice",
        duration=3.0,
        tick_rate=10,
        seed=2024,
        bots=(slash_bot,),
        metadata=metadata,
    )
    result = MatchHarness(config).run()

    request_events = [
        event
        for frame in result.frames
        for event in frame.events
        if event["action"] == "request_spawn"
    ]
    assert len(request_events) == 2
    assert request_events[0]["details"]["status"] == "rejected"
    assert request_events[1]["details"]["status"] == "queued"

    spawn_events = _collect_spawn_events(result.frames)
    assert len(spawn_events) == 1
    spawn_details = spawn_events[0]["details"]
    assert spawn_events[0]["time"] == pytest.approx(1.0)
    assert spawn_details["issuer"] == "admin"
    assert spawn_details["command"] == "addbot"

    assert result.access_permissions["commands"]["addbot"]["allow"] == ["admin"]
    assert result.spawn_schedule == []

def test_bot_resource_scenario_matches_expectation(tmp_path: Path) -> None:
    scenario_path = REPO_ROOT / "tools" / "tests" / "match_sim" / "bot_resource_schedule.json"
    result = run_from_file(scenario_path, seed=4242)
    summary = _summarise_spawn_events(result.frames)

    expectation_path = REPO_ROOT / "tests" / "expectations" / "match_sim_bot_resources.expect"
    expected = expectation_path.read_text(encoding="utf-8").strip()

    if summary.strip() != expected:
        output_path = tmp_path / "bot_resource_spawns.actual"
        output_path.write_text(summary, encoding="utf-8")
        pytest.fail(
            "Bot resource spawn timeline diverged from expectation. "
            f"Captured summary written to {output_path}"
        )
