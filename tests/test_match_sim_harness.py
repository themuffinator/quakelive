"""Test coverage for the deterministic match simulation harness."""

from __future__ import annotations

from pathlib import Path
import copy
import ctypes
import os
import subprocess
import sys
from collections.abc import Iterable, Mapping

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.tests.match_sim.harness import MatchHarness, load_config, run_from_file

SCENARIO = REPO_ROOT / "tools" / "tests" / "match_sim" / "sample_scenario.json"
SCENARIO_DIR = REPO_ROOT / "tools" / "tests" / "match_sim"
ROTATION_SCENARIO = SCENARIO_DIR / "rotation_vote.json"
FREEZE_SCENARIO = SCENARIO_DIR / "freeze_cvars.json"
ALL_SCENARIOS = [
    SCENARIO,
    SCENARIO_DIR / "overtime_scenario.json",
    SCENARIO_DIR / "complex_loadouts.json",
    SCENARIO_DIR / "factory_cvars.json",
    ROTATION_SCENARIO,
    FREEZE_SCENARIO,
]

SRC_DIR = REPO_ROOT / "src"
CODE_DIR = SRC_DIR / "code"
GAME_CODE_DIR = CODE_DIR / "game"

FACTORY_METADATA_SOURCE = (
    """
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#define GAME_INCLUDE
#include "game/g_match_config.c"

vmCvar_t g_timeoutLen;
vmCvar_t g_timeoutCount;
vmCvar_t g_overtime;
vmCvar_t g_suddenDeathRespawn;
vmCvar_t g_suddenDeathRespawnStart;
vmCvar_t g_suddenDeathRespawnTick;
vmCvar_t g_suddenDeathRespawnMax;
vmCvar_t g_suddenDeathRespawnIncrement;
vmCvar_t g_suddenDeathRespawnPrint;
vmCvar_t g_factoryRespawnDelay;
vmCvar_t g_factoryWarmupSpawnDelay;
vmCvar_t g_factoryAllowItemDrops;
vmCvar_t g_factoryAllowItemBounce;
vmCvar_t g_factoryTitle;

static char qlr_factoryTitleConfig[MAX_STRING_CHARS];
static char qlr_factoryFlagsConfig[32];
static char qlr_factorySpawnHints[MAX_INFO_STRING];

/*
=============
Q_strncpyz

Test harness friendly string copy helper.
=============
*/
void Q_strncpyz( char *dest, const char *src, int destsize ) {
@TAB@if ( !dest || destsize <= 0 ) {
@TAB@@TAB@return;
@TAB@}
@TAB@if ( !src ) {
@TAB@@TAB@src = "";
@TAB@}
@TAB@strncpy( dest, src, destsize - 1 );
@TAB@dest[destsize - 1] = '\0';
}

/*
=============
Com_sprintf

Minimal vsnprintf wrapper for metadata tests.
=============
*/
void QDECL Com_sprintf( char *dest, int size, const char *fmt, ... ) {
@TAB@va_list args;
@TAB@if ( !dest || size <= 0 || !fmt ) {
@TAB@@TAB@return;
@TAB@}
@TAB@va_start( args, fmt );
@TAB@vsnprintf( dest, size, fmt, args );
@TAB@va_end( args );
}

/*
=============
Info_SetValueForKey

Appends a key/value pair to an info string buffer.
=============
*/
void Info_SetValueForKey( char *info, const char *key, const char *value ) {
@TAB@char buffer[MAX_INFO_STRING];
@TAB@if ( !info || !key || !value ) {
@TAB@@TAB@return;
@TAB@}
@TAB@Com_sprintf( buffer, sizeof( buffer ), "\\%s\\%s", key, value );
@TAB@if ( strlen( buffer ) + strlen( info ) >= MAX_INFO_STRING ) {
@TAB@@TAB@return;
@TAB@}
@TAB@strcat( info, buffer );
}

/*
=============
G_Printf

Silences logging in the factory metadata harness.
=============
*/
void QDECL G_Printf( const char *fmt, ... ) {
@TAB@(void)fmt;
}

/*
=============
trap_SetConfigstring

Captures configstring updates for verification.
=============
*/
void trap_SetConfigstring( int num, const char *string ) {
@TAB@const char *value = string ? string : "";
@TAB@switch ( num ) {
@TAB@@TAB@case CS_FACTORY_TITLE:
@TAB@@TAB@@TAB@Q_strncpyz( qlr_factoryTitleConfig, value, sizeof( qlr_factoryTitleConfig ) );
@TAB@@TAB@@TAB@break;
@TAB@@TAB@case CS_FACTORY_FLAGS:
@TAB@@TAB@@TAB@Q_strncpyz( qlr_factoryFlagsConfig, value, sizeof( qlr_factoryFlagsConfig ) );
@TAB@@TAB@@TAB@break;
@TAB@@TAB@case CS_SPAWN_HINTS:
@TAB@@TAB@@TAB@Q_strncpyz( qlr_factorySpawnHints, value, sizeof( qlr_factorySpawnHints ) );
@TAB@@TAB@@TAB@break;
@TAB@@TAB@default:
@TAB@@TAB@@TAB@break;
@TAB@}
}

/*
=============
trap_Cvar_Update

Stubbed cvar update to satisfy g_match_config references.
=============
*/
void trap_Cvar_Update( vmCvar_t *cvar ) {
@TAB@(void)cvar;
}

/*
=============
QLR_ClearCapturedConfigstrings

Resets the captured configstring buffers between runs.
=============
*/
static void QLR_ClearCapturedConfigstrings( void ) {
@TAB@memset( qlr_factoryTitleConfig, 0, sizeof( qlr_factoryTitleConfig ) );
@TAB@memset( qlr_factoryFlagsConfig, 0, sizeof( qlr_factoryFlagsConfig ) );
@TAB@memset( qlr_factorySpawnHints, 0, sizeof( qlr_factorySpawnHints ) );
}

/*
=============
QLR_ResetFactoryConfig

Restores the cached factory config snapshot to default values.
=============
*/
void QLR_ResetFactoryConfig( void ) {
@TAB@memset( &g_matchFactoryConfig, 0, sizeof( g_matchFactoryConfig ) );
@TAB@g_matchFactoryConfig.timeoutLengthSeconds = DEFAULT_TIMEOUT_LENGTH_SECONDS;
@TAB@g_matchFactoryConfig.timeoutCountPerTeam = DEFAULT_TIMEOUT_COUNT_PER_TEAM;
@TAB@g_matchFactoryConfig.overtimeLengthSeconds = DEFAULT_OVERTIME_LENGTH_SECONDS;
@TAB@g_matchFactoryConfig.suddenDeathRespawnsEnabled = DEFAULT_SUDDEN_DEATH_RESPAWN ? qtrue : qfalse;
@TAB@g_matchFactoryConfig.suddenDeathStartSeconds = DEFAULT_SUDDEN_DEATH_START_SECONDS;
@TAB@g_matchFactoryConfig.suddenDeathTickSeconds = DEFAULT_SUDDEN_DEATH_TICK_SECONDS;
@TAB@g_matchFactoryConfig.suddenDeathMaxSeconds = DEFAULT_SUDDEN_DEATH_MAX_SECONDS;
@TAB@g_matchFactoryConfig.suddenDeathIncrementSeconds = DEFAULT_SUDDEN_DEATH_INCREMENT_SECONDS;
@TAB@g_matchFactoryConfig.suddenDeathPrintAnnouncements = DEFAULT_SUDDEN_DEATH_PRINT ? qtrue : qfalse;
@TAB@g_matchFactoryConfig.suddenDeathSpawnDelayActive = ( g_matchFactoryConfig.suddenDeathRespawnsEnabled && ( g_matchFactoryConfig.suddenDeathStartSeconds > 0 || g_matchFactoryConfig.suddenDeathIncrementSeconds > 0 ) ) ? qtrue : qfalse;
@TAB@g_matchFactoryConfig.factoryRespawnDelayMilliseconds = DEFAULT_FACTORY_RESPAWN_DELAY_MILLISECONDS;
@TAB@g_matchFactoryConfig.factoryWarmupSpawnDelayMilliseconds = DEFAULT_FACTORY_WARMUP_DELAY_MILLISECONDS;
@TAB@g_matchFactoryConfig.factoryAllowItemDrops = DEFAULT_FACTORY_ALLOW_ITEM_DROPS ? qtrue : qfalse;
@TAB@g_matchFactoryConfig.factoryAllowItemBounce = DEFAULT_FACTORY_ALLOW_ITEM_BOUNCE ? qtrue : qfalse;
@TAB@memset( &g_factoryTitle, 0, sizeof( g_factoryTitle ) );
@TAB@QLR_SetFactoryTitle( "" );
@TAB@QLR_ClearCapturedConfigstrings();
}

/*
=============
QLR_SetFactoryTitle

Overrides the g_factoryTitle CVar for testing.
=============
*/
void QLR_SetFactoryTitle( const char *value ) {
@TAB@const char *source = value ? value : "";
@TAB@Q_strncpyz( g_factoryTitle.string, source, sizeof( g_factoryTitle.string ) );
@TAB@g_factoryTitle.modificationCount++;
}

/*
=============
QLR_SetTimeoutLength

Tweaks the cached timeout length to trigger flag masks.
=============
*/
void QLR_SetTimeoutLength( int seconds ) {
@TAB@g_matchFactoryConfig.timeoutLengthSeconds = seconds;
}

/*
=============
QLR_GetFactoryTitleConfigstring

Exposes the most recent CS_FACTORY_TITLE payload.
=============
*/
const char *QLR_GetFactoryTitleConfigstring( void ) {
@TAB@return qlr_factoryTitleConfig;
}

/*
=============
QLR_GetFactoryFlagsConfigstring

Exposes the most recent CS_FACTORY_FLAGS payload.
=============
*/
const char *QLR_GetFactoryFlagsConfigstring( void ) {
@TAB@return qlr_factoryFlagsConfig;
}

/*
=============
QLR_BuildFactoryMetadata

Invokes the production code to emit fresh configstrings.
=============
*/
void QLR_BuildFactoryMetadata( void ) {
@TAB@G_MatchConfig_UpdateConfigstrings();
}
"""
    .replace("@TAB@", "\t")
)


def test_run_from_file_is_deterministic(tmp_path) -> None:
    """Running the same scenario with the same seed yields identical timelines."""

    result_a = run_from_file(SCENARIO, seed=4242)
    result_b = run_from_file(SCENARIO, seed=4242)

    assert result_a.config.seed == 4242
    assert result_b.config.seed == 4242
    assert result_a.to_json(indent=None) == result_b.to_json(indent=None)


def test_seed_override_changes_randomised_outputs() -> None:
    """Using different seeds should influence randomised spawn and script values."""

    config_default = load_config(SCENARIO)
    default_result = MatchHarness(config_default).run()

    config_override = load_config(SCENARIO)
    override_result = MatchHarness(config_override, seed=9090).run()

    assert default_result.config.seed == 2024
    assert override_result.config.seed == 9090

    # Randomised command parameters should diverge when the seed is overridden.
    default_move_event = default_result.frames[2].events[0]
    override_move_event = override_result.frames[2].events[0]

    assert default_move_event["bot"] == "anarki"
    assert override_move_event["bot"] == "anarki"

    default_direction = default_move_event["details"]["velocity"]
    override_direction = override_move_event["details"]["velocity"]

    assert default_direction != override_direction
    assert default_result.to_json(indent=None) != override_result.to_json(indent=None)


@pytest.mark.parametrize("scenario_path", ALL_SCENARIOS, ids=[path.stem for path in ALL_SCENARIOS])
def test_all_scenarios_produce_frames(scenario_path: Path) -> None:
    """Ensure every shipped scenario runs without errors and emits timeline frames."""

    result = run_from_file(scenario_path, seed=1337)

    assert result.frames, "Scenario should produce at least one frame"
    assert result.config.map
    assert result.config.metadata is not None


def test_rotation_vote_metadata_tracks_factory_title() -> None:
    """The rotation scenario captures factory vote details for documentation."""

    config = load_config(ROTATION_SCENARIO)
    metadata = config.metadata
    rotation_meta = metadata.get("rotation", {})
    factory_meta = metadata.get("factory", {})

    assert rotation_meta["factory_id"] == "power-tdm"
    assert rotation_meta["vote_command"] == "map purgatory power-tdm"
    assert rotation_meta["g_factoryTitle"] == factory_meta.get("title")

    result = MatchHarness(config, seed=config.seed).run()
    frame0 = result.frames[0]
    for bot_name in ("sarge", "slash"):
        bot_state = frame0.bots[bot_name]
        assert bot_state["ammo"]["rocket"] == pytest.approx(20.0)
        assert bot_state["ammo"]["lightning"] == pytest.approx(60.0)
        assert bot_state["inventory"]["armor"] == 75
        assert bot_state["inventory"]["gauntlet"] == 1

def _configure_factory_config(**overrides) -> MatchHarness:
    config = load_config(SCENARIO_DIR / "factory_cvars.json")
    factory_meta = copy.deepcopy(config.metadata.get("factory", {}))
    for key, value in overrides.items():
        if key == "items":
            items = copy.deepcopy(factory_meta.get("items", {}))
            items.update(value)
            factory_meta["items"] = items
        else:
            factory_meta[key] = value
    config.metadata["factory"] = factory_meta
    return MatchHarness(config, seed=config.seed)


@pytest.mark.parametrize(
    "active_loadout, expected_visor, expected_anarki",
    [
        (
            "practice",
            {"ammo": {"rocket": 15.0, "rail": 5.0}, "inventory": {"armor": 50, "mega": 1}},
            {"ammo": {"machinegun": 100.0, "lightning": 75.0}, "inventory": {"armor": 25, "gauntlet": 1}},
        ),
        (
            "tournament",
            {"ammo": {"rocket": 15.0, "rail": 5.0}, "inventory": {"armor": 50, "mega": 1}},
            {"ammo": {"rocket": 15.0, "rail": 5.0}, "inventory": {"armor": 50, "mega": 1}},
        ),
    ],
    ids=["practice-default", "tournament-default"],
)
def test_factory_loadout_toggle_updates_inventory(
    active_loadout: str, expected_visor: dict, expected_anarki: dict
) -> None:
    harness = _configure_factory_config(active_loadout=active_loadout)
    result = harness.run()

    first_frame = result.frames[0]
    visor_state = first_frame.bots["visor"]
    anarki_state = first_frame.bots["anarki"]

    assert visor_state["ammo"] == expected_visor["ammo"]
    assert visor_state["inventory"] == expected_visor["inventory"]

    assert anarki_state["ammo"] == expected_anarki["ammo"]
    assert anarki_state["inventory"] == expected_anarki["inventory"]


def test_factory_spawn_delays_emit_client_spawn_events() -> None:
    harness = _configure_factory_config()
    result = harness.run()

    spawn_events = [
        (event["bot"], event["details"]["warmup"], event["time"])
        for frame in result.frames
        for event in frame.events
        if event["action"] == "client_spawn"
    ]

    assert spawn_events == [
        ("visor", True, 0.5),
        ("anarki", True, 1.0),
        ("visor", False, 2.5),
        ("anarki", False, 2.7),
    ]


def _summarise_item_events(frames: Iterable[object]) -> str:
    lines: list[str] = []
    for frame in frames:
        events = getattr(frame, "events", None)
        if events is None:
            if isinstance(frame, Mapping):
                events = frame.get("events", [])
            else:
                raise TypeError("Frame does not expose event data")
        for event in events:
            action = event["action"]
            if action not in {"drop_item", "item_respawn", "item_return"}:
                continue
            bot = event["bot"]
            details = event["details"]
            item = details.get("item")
            if action == "drop_item":
                lines.append(
                    f"{event['time']:.3f} {bot} drop {item} status={details.get('status')} bounce={details.get('bounce')}"
                )
            elif action == "item_respawn":
                lines.append(f"{event['time']:.3f} {bot} respawn {item}")
            elif action == "item_return":
                lines.append(f"{event['time']:.3f} {bot} return {item}")
    return "\n".join(lines)


def _read_expectation(name: str) -> str:
    expectation_path = REPO_ROOT / "tests" / "expectations" / name
    return expectation_path.read_text(encoding="utf-8").strip()


def test_factory_item_flags_control_drop_behaviour(tmp_path: Path) -> None:
    baseline = _configure_factory_config()
    allow_bounce = _configure_factory_config(items={"allow_bounce": True})
    no_drops = _configure_factory_config(items={"allow_drops": False})

    results = [baseline.run(), allow_bounce.run(), no_drops.run()]
    summaries = [
        _summarise_item_events(result.frames)
        for result in results
    ]

    combined = "\n---\n".join(summaries)
    expected = _read_expectation("match_sim_factory_items.expect")
    if combined.strip() != expected.strip():
        output_path = tmp_path / "factory_items.actual"
        output_path.write_text(combined, encoding="utf-8")
        pytest.fail(
            "Item drop expectations diverged. "
            f"Captured summary written to {output_path}"
        )


def _read_factory_item_sections() -> list[str]:
    expectation = _read_expectation("match_sim_factory_items.expect")
    return [section.strip() for section in expectation.split("\n---\n")]


def test_cli_item_parity_matches_baseline_expectation(harness_parity_runs) -> None:
    sections = _read_factory_item_sections()
    baseline_expectation = sections[0]
    reference_payload: dict[str, object] | None = None

    for target in ("qvm", "dll"):
        run = harness_parity_runs.require(target)
        payload = run.load_match_timeline("factory")
        summary = _summarise_item_events(payload["frames"]).strip()
        assert summary == baseline_expectation

        if reference_payload is None:
            reference_payload = payload
        else:
            assert payload == reference_payload, f"{target} payload diverged from parity baseline"


def test_cli_item_parity_native_build_matches_vm(harness_parity_runs) -> None:
    native_run = harness_parity_runs.get("re")
    if native_run is None:
        pytest.skip(harness_parity_runs.missing_reason("re") or "Native build support unavailable")

    reference_payload = harness_parity_runs.require("qvm").load_match_timeline("factory")
    native_payload = native_run.load_match_timeline("factory")

    assert native_payload == reference_payload

    trace_log = native_run.read_log("trace_harness")
    assert "Trace harness run completed successfully." in trace_log


def _build_factory_metadata_library(tmp_path: Path) -> Path:
    src_path = tmp_path / "factory_metadata_test.c"
    src_path.write_text(FACTORY_METADATA_SOURCE, encoding="utf-8")

    if sys.platform == "darwin":
        lib_path = tmp_path / "libfactory_metadata_test.dylib"
        compile_cmd = [
            "cc",
            "-std=c99",
            "-dynamiclib",
            "-I",
            str(SRC_DIR),
            "-I",
            str(CODE_DIR),
            "-I",
            str(GAME_CODE_DIR),
            "-o",
            str(lib_path),
            str(src_path),
        ]
    elif os.name == "nt":
        raise RuntimeError("Factory metadata harness is unavailable on Windows toolchains")
    else:
        lib_path = tmp_path / "libfactory_metadata_test.so"
        compile_cmd = [
            "cc",
            "-std=c99",
            "-shared",
            "-fPIC",
            "-I",
            str(SRC_DIR),
            "-I",
            str(CODE_DIR),
            "-I",
            str(GAME_CODE_DIR),
            "-o",
            str(lib_path),
            str(src_path),
        ]

    subprocess.run(compile_cmd, check=True)
    return lib_path


def _load_factory_metadata_library(lib_path: Path) -> ctypes.CDLL:
    library = ctypes.CDLL(str(lib_path))
    library.QLR_ResetFactoryConfig.argtypes = []
    library.QLR_ResetFactoryConfig.restype = None
    library.QLR_SetFactoryTitle.argtypes = [ctypes.c_char_p]
    library.QLR_SetFactoryTitle.restype = None
    library.QLR_SetTimeoutLength.argtypes = [ctypes.c_int]
    library.QLR_SetTimeoutLength.restype = None
    library.QLR_BuildFactoryMetadata.argtypes = []
    library.QLR_BuildFactoryMetadata.restype = None
    library.QLR_GetFactoryTitleConfigstring.argtypes = []
    library.QLR_GetFactoryTitleConfigstring.restype = ctypes.c_char_p
    library.QLR_GetFactoryFlagsConfigstring.argtypes = []
    library.QLR_GetFactoryFlagsConfigstring.restype = ctypes.c_char_p
    return library


@pytest.fixture(scope="module")
def factory_metadata_library(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
    if os.name == "nt":
        pytest.skip("Factory metadata harness requires a POSIX toolchain")
    tmp_path = tmp_path_factory.mktemp("factory_metadata")
    lib_path = _build_factory_metadata_library(tmp_path)
    return _load_factory_metadata_library(lib_path)


@pytest.mark.skipif(os.name == "nt", reason="Factory metadata harness requires a POSIX toolchain")
def test_factory_title_configstring_matches_trimmed_preset(factory_metadata_library: ctypes.CDLL) -> None:
    library = factory_metadata_library
    library.QLR_ResetFactoryConfig()
    library.QLR_SetFactoryTitle(b"  Practice Preset  ")
    library.QLR_BuildFactoryMetadata()

    title = library.QLR_GetFactoryTitleConfigstring()
    flags = library.QLR_GetFactoryFlagsConfigstring()

    assert title is not None
    assert title.decode("utf-8") == "Practice Preset"
    assert flags is not None
    assert flags.decode("utf-8") == "0"

    library.QLR_SetTimeoutLength(90)
    library.QLR_BuildFactoryMetadata()

    updated_title = library.QLR_GetFactoryTitleConfigstring()
    updated_flags = library.QLR_GetFactoryFlagsConfigstring()

    assert updated_title is not None
    assert updated_title.decode("utf-8") == "Practice Preset"
    assert updated_flags is not None
    assert updated_flags.decode("utf-8") == "1"
