"""Validation harness checks for ownerdraw stats debug log payloads."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
G_CMDS = REPO_ROOT / "src" / "code" / "game" / "g_cmds.c"
OWNERDRAW_EXPECTATION_PATH = REPO_ROOT / "tests" / "expectations" / "ownerdraw_runtime_baseline.json"

PLACEMENT_LOG_RE = re.compile(
    r"^ownerdraw_stats: "
    r"place=(?P<place>\d+) "
    r"client=(?P<client>-?\d+) "
    r"valid=(?P<valid>\d+) "
    r"frags=(?P<frags>-?\d+(?:,-?\d+)*) "
    r"hits=(?P<hits>-?\d+(?:,-?\d+)*) "
    r"shots=(?P<shots>-?\d+(?:,-?\d+)*) "
    r"dmg=(?P<dmg>-?\d+(?:,-?\d+)*) "
    r"pickups=(?P<pickups>-?\d+(?:,-?\d+)*) "
    r"pickupAvg=(?P<pickup_avg>-?\d+(?:\.\d+)?(?:,-?\d+(?:\.\d+)?)*) "
    r"pr=(?P<pr>-?\d+) "
    r"tier=(?P<tier>-?\d+)$"
)

TEAM_LOG_RE = re.compile(
    r"^ownerdraw_stats_team: "
    r"team=(?P<team>red|blue) "
    r"fields=(?P<fields>\d+) "
    r"valid=(?P<valid>\d+) "
    r"values=(?P<values>-?\d+(?:,-?\d+)*)$"
)


def _parse_csv(payload: str) -> list[int]:
    return [int(token) for token in payload.split(",") if token]


def _parse_float_csv(payload: str) -> list[float]:
    return [float(token) for token in payload.split(",") if token]


def _normalize_placement_match(match: re.Match[str]) -> dict[str, object]:
    return {
        "place": int(match.group("place")),
        "client": int(match.group("client")),
        "valid": int(match.group("valid")),
        "frags": _parse_csv(match.group("frags")),
        "hits": _parse_csv(match.group("hits")),
        "shots": _parse_csv(match.group("shots")),
        "dmg": _parse_csv(match.group("dmg")),
        "pickups": _parse_csv(match.group("pickups")),
        "pickupAvg": _parse_float_csv(match.group("pickup_avg")),
        "pr": int(match.group("pr")),
        "tier": int(match.group("tier")),
    }


def _normalize_team_match(match: re.Match[str]) -> dict[str, object]:
    return {
        "team": match.group("team"),
        "fields": int(match.group("fields")),
        "valid": int(match.group("valid")),
        "values": _parse_csv(match.group("values")),
    }


def _runtime_ownerdraw_fixture_path() -> Path:
    return Path(os.environ.get("QLR_OWNERDRAW_FIXTURE_PATH", str(OWNERDRAW_EXPECTATION_PATH)))


def _serialize_runtime_ownerdraw_fixture(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(payload, indent=2, sort_keys=True)}\n", encoding="utf-8")


def _build_runtime_ownerdraw_fixture(
    latest_by_place: dict[int, re.Match[str]],
    latest_by_team: dict[str, re.Match[str]],
) -> dict[str, object]:
    return {
        "placement": {
            "1": _normalize_placement_match(latest_by_place[1]),
            "2": _normalize_placement_match(latest_by_place[2]),
        },
        "team": {
            "red": _normalize_team_match(latest_by_team["red"]),
            "blue": _normalize_team_match(latest_by_team["blue"]),
        },
    }


def _collect_log_matches(log_text: str) -> tuple[list[re.Match[str]], list[re.Match[str]]]:
    placement_matches: list[re.Match[str]] = []
    team_matches: list[re.Match[str]] = []

    for raw_line in log_text.splitlines():
        line = raw_line.strip()
        placement_match = PLACEMENT_LOG_RE.match(line)
        if placement_match is not None:
            placement_matches.append(placement_match)
            continue

        team_match = TEAM_LOG_RE.match(line)
        if team_match is not None:
            team_matches.append(team_match)

    return placement_matches, team_matches


def test_ownerdraw_log_regex_parses_payloads() -> None:
    placement_line = (
        "ownerdraw_stats: place=1 client=3 valid=1 "
        "frags=1,2,3,4,5,6,7,8,9,10,11,12,13 "
        "hits=1,2,3,4,5,6,7,8,9,10,11,12 "
        "shots=2,4,6,8,10,12,14,16,18,20,22,24 "
        "dmg=10,20,30,40,50,60,70,80,90,100,110,120,130 "
        "pickups=2,4,6,8 pickupAvg=5.00,10.50,15.25,20.00 pr=2400 tier=6"
    )
    team_line = (
        "ownerdraw_stats_team: team=red fields=18 valid=1 "
        "values=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18"
    )

    placement_match = PLACEMENT_LOG_RE.match(placement_line)
    assert placement_match is not None

    frags = _parse_csv(placement_match.group("frags"))
    hits = _parse_csv(placement_match.group("hits"))
    shots = _parse_csv(placement_match.group("shots"))
    damage = _parse_csv(placement_match.group("dmg"))
    pickups = _parse_csv(placement_match.group("pickups"))
    pickup_avg = _parse_float_csv(placement_match.group("pickup_avg"))

    assert len(frags) == 13
    assert len(hits) == 12
    assert len(shots) == 12
    assert len(damage) == 13
    assert len(pickups) == 4
    assert len(pickup_avg) == 4
    assert pickup_avg == [5.0, 10.5, 15.25, 20.0]
    assert int(placement_match.group("pr")) == 2400
    assert int(placement_match.group("tier")) == 6

    team_match = TEAM_LOG_RE.match(team_line)
    assert team_match is not None
    field_count = int(team_match.group("fields"))
    values = _parse_csv(team_match.group("values"))
    assert len(values) == field_count
    assert team_match.group("team") == "red"
    assert int(team_match.group("valid")) == 1


def test_ownerdraw_debug_cvar_and_markers_are_registered() -> None:
    servercmds = CG_SERVERCMDS.read_text(encoding="utf-8")
    main = CG_MAIN.read_text(encoding="utf-8")

    assert "cg_debugOwnerdrawStats" in main
    assert '"cg_debugOwnerdrawStats"' in main
    assert "ownerdraw_stats: place=" in servercmds
    assert "ownerdraw_stats_team: team=" in servercmds


def test_ownerdraw_dumps_run_after_scorestats_updates() -> None:
    source = CG_SERVERCMDS.read_text(encoding="utf-8")

    assert "CG_SCORESTAT_FIELDS_PER_CLIENT" in source
    score_valid = source.index("cg.scoreStats[clientNum].valid = qtrue;")
    score_dump = source.index("CG_DebugDumpPlacementOwnerdrawScoreStats();")
    team_valid = source.index("cg.teamScoreStats.valid = qtrue;")
    team_dump = source.index("CG_DebugDumpTeamOwnerdrawScoreStats( fieldCount );")
    score_guard = source.index("( argc - arg ) < CG_SCORESTAT_FIELDS_PER_CLIENT")
    score_parse = source.index("clientNum = atoi( CG_Argv( arg++ ) );")

    assert score_valid < score_dump
    assert team_valid < team_dump
    assert score_guard < score_parse


def test_duel_scorestats_use_retail_weapon_entry_order() -> None:
    source = CG_SERVERCMDS.read_text(encoding="utf-8")

    order_start = source.index("static const weapon_t cg_retailWeaponReloadOrder[]")
    order_end = source.index("typedef struct {", order_start)
    order_block = source[order_start:order_end]
    duel_start = source.index("static void CG_ParseDuelScores")
    duel_end = source.index("CG_SetScoreSelection( NULL );", duel_start)
    duel_block = source[duel_start:duel_end]

    for expected in (
        "WP_GAUNTLET",
        "WP_MACHINEGUN",
        "WP_SHOTGUN",
        "WP_GRAPPLING_HOOK",
        "WP_NAILGUN",
        "WP_PROX_LAUNCHER",
        "WP_CHAINGUN",
        "WP_HEAVY_MACHINEGUN",
    ):
        assert expected in order_block

    assert order_block.index("WP_SHOTGUN") < order_block.index("WP_HEAVY_MACHINEGUN")
    assert order_block.index("WP_GRAPPLING_HOOK") < order_block.index("WP_NAILGUN")
    assert "for ( weaponIndex = 0; weaponIndex < ARRAY_LEN( cg_retailWeaponReloadOrder ); weaponIndex++ )" in duel_block
    assert "weapon = cg_retailWeaponReloadOrder[weaponIndex];" in duel_block
    assert "for ( weapon = WP_GAUNTLET; weapon < WP_NUM_WEAPONS; ++weapon )" not in duel_block


def test_team_scorestats_cache_tracks_field_count() -> None:
    servercmds = CG_SERVERCMDS.read_text(encoding="utf-8")
    local = CG_LOCAL.read_text(encoding="utf-8")

    assert "fieldCount;" in local

    parse_start = servercmds.index("static void CG_ParseTeamScoreStats")
    parse_end = servercmds.index("static void CG_ParseKeyMask")
    parse_block = servercmds[parse_start:parse_end]

    assert "cg.teamScoreStats.fieldCount = fieldCount;" in parse_block
    assert parse_block.index("cg.teamScoreStats.fieldCount = fieldCount;") < parse_block.index(
        "cg.teamScoreStats.valid = qtrue;"
    )


def test_progression_scorestats_use_session_skill_sources() -> None:
    source = G_CMDS.read_text(encoding="utf-8")

    pr_start = source.index("static int G_GetPlacementProgressionPr")
    tier_start = source.index("static int G_GetPlacementProgressionTier")
    send_start = source.index("static void G_SendScoreStatsMessage")

    pr_block = source[pr_start:tier_start]
    tier_block = source[tier_start:send_start]

    assert "progressionPr = cl->sess.skill1;" in pr_block
    assert "skill3" not in pr_block

    assert "progressionTier = cl->sess.skill2;" in tier_block
    assert "skill3" not in tier_block
    assert "itemProgressionTier" not in tier_block
    assert "progressionFlags" not in tier_block


def test_runtime_qconsole_ownerdraw_log_capture(tmp_path: Path) -> None:
    if os.environ.get("QLR_VALIDATE_OWNERDRAW_LOGS", "0") != "1":
        pytest.skip("Set QLR_VALIDATE_OWNERDRAW_LOGS=1 to validate runtime ownerdraw logs.")

    log_path = Path(
        os.environ.get(
            "QLR_QCONSOLE_LOG",
            str(REPO_ROOT / "build" / "win32" / "Debug" / "bin" / "baseq3" / "qconsole.log"),
        )
    )
    if not log_path.exists():
        pytest.skip(f"Missing qconsole log: {log_path}")

    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    placement_matches, team_matches = _collect_log_matches(log_text)
    assert placement_matches, "No ownerdraw_stats placement lines were found in qconsole.log"
    assert team_matches, "No ownerdraw_stats_team lines were found in qconsole.log"

    latest_by_place: dict[int, re.Match[str]] = {}
    latest_by_team: dict[str, re.Match[str]] = {}
    for match in placement_matches:
        latest_by_place[int(match.group("place"))] = match
    for match in team_matches:
        latest_by_team[match.group("team")] = match

    assert 1 in latest_by_place, "Missing place=1 ownerdraw_stats log line"
    assert 2 in latest_by_place, "Missing place=2 ownerdraw_stats log line"
    assert "red" in latest_by_team, "Missing red ownerdraw_stats_team log line"
    assert "blue" in latest_by_team, "Missing blue ownerdraw_stats_team log line"

    for place in (1, 2):
        match = latest_by_place[place]
        assert len(_parse_csv(match.group("frags"))) == 13
        assert len(_parse_csv(match.group("hits"))) == 12
        assert len(_parse_csv(match.group("shots"))) == 12
        assert len(_parse_csv(match.group("dmg"))) == 13
        assert len(_parse_csv(match.group("pickups"))) == 4
        assert len(_parse_csv(match.group("pickup_avg"))) == 4

    for team in ("red", "blue"):
        match = latest_by_team[team]
        fields = int(match.group("fields"))
        values = _parse_csv(match.group("values"))
        assert fields > 0
        assert len(values) == fields

    fixture_payload = _build_runtime_ownerdraw_fixture(latest_by_place, latest_by_team)
    fixture_path = _runtime_ownerdraw_fixture_path()
    if os.environ.get("QLR_WRITE_OWNERDRAW_FIXTURE", "0") == "1":
        _serialize_runtime_ownerdraw_fixture(fixture_path, fixture_payload)
        pytest.skip(f"Wrote ownerdraw runtime fixture to {fixture_path}")

    if not fixture_path.exists():
        pytest.fail(
            "Missing ownerdraw runtime fixture. "
            f"Capture one with QLR_VALIDATE_OWNERDRAW_LOGS=1 QLR_WRITE_OWNERDRAW_FIXTURE=1 "
            f"(path: {fixture_path})"
        )

    expected_payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if fixture_payload != expected_payload:
        actual_path = tmp_path / "ownerdraw_runtime_baseline.actual.json"
        _serialize_runtime_ownerdraw_fixture(actual_path, fixture_payload)
        pytest.fail(
            "Runtime ownerdraw payload diverged from baseline fixture. "
            f"Captured payload written to {actual_path}"
        )
