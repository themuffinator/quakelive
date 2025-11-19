"""Gametype lifecycle dispatch regression harness."""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
CODE_DIR = SRC_DIR / "code"
GAME_CODE_DIR = CODE_DIR / "game"

GAMETYPE_LIFECYCLE_SOURCE = (
    """
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#define QLR_INSTRUMENT_GAMETYPE_LIFECYCLE
#define GAME_INCLUDE
#include "code/game/g_local.h"

level_locals_t level;
vmCvar_t g_gametype;
vmCvar_t g_warmup;
static const char *s_duelSpawnGrantScript = "weapon_gauntlet weapon_machinegun ammo_bullets 100";
static gclient_t qlr_testClient;
static gentity_t qlr_testEntity;
static char qlr_vaBuffer[MAX_STRING_CHARS];

/*
=============
va

Provides a minimal vsnprintf-backed formatter for the harness.
=============
*/
char *va( char *format, ... ) {
@TAB@va_list args;

@TAB@if ( !format ) {
@TAB@@TAB@return qlr_vaBuffer;
@TAB@}

@TAB@va_start( args, format );
@TAB@vsnprintf( qlr_vaBuffer, sizeof( qlr_vaBuffer ), format, args );
@TAB@va_end( args );
@TAB@return qlr_vaBuffer;
}

/*
=============
trap_SetConfigstring

Stubs configstring writes for the lifecycle harness.
=============
*/
void trap_SetConfigstring( int num, const char *string ) {
@TAB@(void)num;
@TAB@(void)string;
}

/*
=============
G_UpdateReadyUpConfigstring

No-op placeholder for server broadcast updates.
=============
*/
void G_UpdateReadyUpConfigstring( void ) {}

/*
=============
G_RunGrantScript

Stubbed grant script executor used by the duel spawn hook.
=============
*/
void G_RunGrantScript( gentity_t *ent, const char *script ) {
@TAB@(void)ent;
@TAB@(void)script;
}

/*
=============
G_Frame_BeginRoundWarmup

Records round-based initialisation without mutating state.
=============
*/
void G_Frame_BeginRoundWarmup( void ) {}

/*
=============
G_RaceClientBegin

Silences race begin hooks during the duel lifecycle tests.
=============
*/
void G_RaceClientBegin( gentity_t *ent ) {
@TAB@(void)ent;
}

/*
=============
G_RaceClientSpawn

Silences race spawn hooks during the duel lifecycle tests.
=============
*/
void G_RaceClientSpawn( gentity_t *ent ) {
@TAB@(void)ent;
}

/*
=============
QLR_InitTestEntity

Initialises the shared entity used across lifecycle tests.
=============
*/
static void QLR_InitTestEntity( void ) {
@TAB@memset( &qlr_testClient, 0, sizeof( qlr_testClient ) );
@TAB@memset( &qlr_testEntity, 0, sizeof( qlr_testEntity ) );
@TAB@qlr_testEntity.client = &qlr_testClient;
}

#include "code/game/g_gametype_lifecycle.inc"

#define QLR_GAMETYPE_LIFECYCLE_STAGE_COUNT ( GAMETYPE_LIFECYCLE_CLIENT_SPAWN + 1 )
static int qlr_duelLifecycleCounts[QLR_GAMETYPE_LIFECYCLE_STAGE_COUNT];
static int qlr_defaultLifecycleCounts[QLR_GAMETYPE_LIFECYCLE_STAGE_COUNT];

/*
=============
QLR_RecordGametypeDuelStage

Tracks the number of times the duel handler processes each stage.
=============
*/
void QLR_RecordGametypeDuelStage( gametypeLifecycleStage_t stage ) {
@TAB@if ( stage < 0 || stage >= QLR_GAMETYPE_LIFECYCLE_STAGE_COUNT ) {
@TAB@@TAB@return;
@TAB@}

@TAB@qlr_duelLifecycleCounts[stage]++;
}

/*
=============
QLR_RecordGametypeDefaultStage

Tracks the number of times the default handler runs per stage.
=============
*/
void QLR_RecordGametypeDefaultStage( gametypeLifecycleStage_t stage ) {
@TAB@if ( stage < 0 || stage >= QLR_GAMETYPE_LIFECYCLE_STAGE_COUNT ) {
@TAB@@TAB@return;
@TAB@}

@TAB@qlr_defaultLifecycleCounts[stage]++;
}

/*
=============
QLR_ResetGametypeLifecycleHarness

Resets the lifecycle harness to a deterministic baseline.
=============
*/
void QLR_ResetGametypeLifecycleHarness( void ) {
@TAB@memset( &level, 0, sizeof( level ) );
@TAB@level.warmupTime = -1;
@TAB@memset( qlr_duelLifecycleCounts, 0, sizeof( qlr_duelLifecycleCounts ) );
@TAB@memset( qlr_defaultLifecycleCounts, 0, sizeof( qlr_defaultLifecycleCounts ) );
@TAB@g_gametype.integer = 0;
@TAB@g_warmup.integer = 0;
@TAB@QLR_InitTestEntity();
}

/*
=============
QLR_SetGametype

Overrides the active gametype for the harness.
=============
*/
void QLR_SetGametype( int gametype ) {
@TAB@g_gametype.integer = gametype;
}

/*
=============
QLR_SetWarmupSeconds

Configures the g_warmup cvar used by the duel countdown logic.
=============
*/
void QLR_SetWarmupSeconds( int seconds ) {
@TAB@g_warmup.integer = seconds;
}

/*
=============
QLR_SetWarmupTime

Sets the current warmup timestamp tracked on the level struct.
=============
*/
void QLR_SetWarmupTime( int warmupTime ) {
@TAB@level.warmupTime = warmupTime;
}

/*
=============
QLR_SetLevelTime

Controls the simulated server time consumed by duel warmup math.
=============
*/
void QLR_SetLevelTime( int timeMilliseconds ) {
@TAB@level.time = timeMilliseconds;
}

/*
=============
QLR_SetNumPlayingClients

Injects the number of active duel players for begin-stage coverage.
=============
*/
void QLR_SetNumPlayingClients( int count ) {
@TAB@level.numPlayingClients = count;
}

/*
=============
QLR_SetTestClientTeam

Assigns the shared entity's team context for spawn handling.
=============
*/
void QLR_SetTestClientTeam( int team ) {
@TAB@if ( qlr_testEntity.client ) {
@TAB@@TAB@qlr_testEntity.client->sess.sessionTeam = team;
@TAB@}
}

/*
=============
QLR_SetTestClientActive

Toggles whether the shared entity exposes a client pointer.
=============
*/
void QLR_SetTestClientActive( int active ) {
@TAB@qlr_testEntity.client = active ? &qlr_testClient : NULL;
}

/*
=============
QLR_RunGametypeInit

Executes the gametype init lifecycle stage.
=============
*/
void QLR_RunGametypeInit( void ) {
@TAB@G_GametypeInit();
}

/*
=============
QLR_RunGametypeClientBegin

Executes the ClientBegin lifecycle stage using the shared entity.
=============
*/
void QLR_RunGametypeClientBegin( void ) {
@TAB@G_GametypeClientBegin( &qlr_testEntity );
}

/*
=============
QLR_RunGametypeClientSpawn

Executes the ClientSpawn lifecycle stage using the shared entity.
=============
*/
void QLR_RunGametypeClientSpawn( void ) {
@TAB@G_GametypeClientSpawn( &qlr_testEntity );
}

/*
=============
QLR_GetDuelInitCount

Reports how often the duel handler processed the init stage.
=============
*/
int QLR_GetDuelInitCount( void ) {
@TAB@return qlr_duelLifecycleCounts[GAMETYPE_LIFECYCLE_INIT];
}

/*
=============
QLR_GetDuelClientBeginCount

Reports how often the duel handler processed the ClientBegin stage.
=============
*/
int QLR_GetDuelClientBeginCount( void ) {
@TAB@return qlr_duelLifecycleCounts[GAMETYPE_LIFECYCLE_CLIENT_BEGIN];
}

/*
=============
QLR_GetDuelClientSpawnCount

Reports how often the duel handler processed the ClientSpawn stage.
=============
*/
int QLR_GetDuelClientSpawnCount( void ) {
@TAB@return qlr_duelLifecycleCounts[GAMETYPE_LIFECYCLE_CLIENT_SPAWN];
}

/*
=============
QLR_GetDefaultInitCount

Reports how often the default handler processed the init stage.
=============
*/
int QLR_GetDefaultInitCount( void ) {
@TAB@return qlr_defaultLifecycleCounts[GAMETYPE_LIFECYCLE_INIT];
}

/*
=============
QLR_GetDefaultBeginCount

Reports how often the default handler processed the ClientBegin stage.
=============
*/
int QLR_GetDefaultBeginCount( void ) {
@TAB@return qlr_defaultLifecycleCounts[GAMETYPE_LIFECYCLE_CLIENT_BEGIN];
}

/*
=============
QLR_GetDefaultSpawnCount

Reports how often the default handler processed the ClientSpawn stage.
=============
*/
int QLR_GetDefaultSpawnCount( void ) {
@TAB@return qlr_defaultLifecycleCounts[GAMETYPE_LIFECYCLE_CLIENT_SPAWN];
}

/*
=============
QLR_GetGametypeTournamentValue

Exposes the GT_TOURNAMENT enumeration value to Python tests.
=============
*/
int QLR_GetGametypeTournamentValue( void ) {
@TAB@return GT_TOURNAMENT;
}

/*
=============
QLR_GetTeamFreeValue

Exposes the TEAM_FREE enumeration value to Python tests.
=============
*/
int QLR_GetTeamFreeValue( void ) {
@TAB@return TEAM_FREE;
}

/*
=============
QLR_GetTeamSpectatorValue

Exposes the TEAM_SPECTATOR enumeration value to Python tests.
=============
*/
int QLR_GetTeamSpectatorValue( void ) {
@TAB@return TEAM_SPECTATOR;
}
"""
).replace("@TAB@", "	")


def _build_gametype_lifecycle_library(tmp_path: Path) -> Path:
    src_path = tmp_path / "gametype_lifecycle_test.c"
    src_path.write_text(GAMETYPE_LIFECYCLE_SOURCE, encoding="utf-8")

    if os.name == "nt":
        raise RuntimeError("Gametype lifecycle harness requires a POSIX toolchain")
    elif sys.platform == "darwin":
        lib_path = tmp_path / "libgametype_lifecycle_test.dylib"
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
    else:
        lib_path = tmp_path / "libgametype_lifecycle_test.so"
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


def _load_gametype_lifecycle_library(lib_path: Path) -> ctypes.CDLL:
    library = ctypes.CDLL(str(lib_path))
    library.QLR_ResetGametypeLifecycleHarness.argtypes = []
    library.QLR_ResetGametypeLifecycleHarness.restype = None
    library.QLR_SetGametype.argtypes = [ctypes.c_int]
    library.QLR_SetGametype.restype = None
    library.QLR_SetWarmupSeconds.argtypes = [ctypes.c_int]
    library.QLR_SetWarmupSeconds.restype = None
    library.QLR_SetWarmupTime.argtypes = [ctypes.c_int]
    library.QLR_SetWarmupTime.restype = None
    library.QLR_SetLevelTime.argtypes = [ctypes.c_int]
    library.QLR_SetLevelTime.restype = None
    library.QLR_SetNumPlayingClients.argtypes = [ctypes.c_int]
    library.QLR_SetNumPlayingClients.restype = None
    library.QLR_SetTestClientTeam.argtypes = [ctypes.c_int]
    library.QLR_SetTestClientTeam.restype = None
    library.QLR_SetTestClientActive.argtypes = [ctypes.c_int]
    library.QLR_SetTestClientActive.restype = None
    library.QLR_RunGametypeInit.argtypes = []
    library.QLR_RunGametypeInit.restype = None
    library.QLR_RunGametypeClientBegin.argtypes = []
    library.QLR_RunGametypeClientBegin.restype = None
    library.QLR_RunGametypeClientSpawn.argtypes = []
    library.QLR_RunGametypeClientSpawn.restype = None
    library.QLR_GetDuelInitCount.argtypes = []
    library.QLR_GetDuelInitCount.restype = ctypes.c_int
    library.QLR_GetDuelClientBeginCount.argtypes = []
    library.QLR_GetDuelClientBeginCount.restype = ctypes.c_int
    library.QLR_GetDuelClientSpawnCount.argtypes = []
    library.QLR_GetDuelClientSpawnCount.restype = ctypes.c_int
    library.QLR_GetDefaultInitCount.argtypes = []
    library.QLR_GetDefaultInitCount.restype = ctypes.c_int
    library.QLR_GetDefaultBeginCount.argtypes = []
    library.QLR_GetDefaultBeginCount.restype = ctypes.c_int
    library.QLR_GetDefaultSpawnCount.argtypes = []
    library.QLR_GetDefaultSpawnCount.restype = ctypes.c_int
    library.QLR_GetGametypeTournamentValue.argtypes = []
    library.QLR_GetGametypeTournamentValue.restype = ctypes.c_int
    library.QLR_GetTeamFreeValue.argtypes = []
    library.QLR_GetTeamFreeValue.restype = ctypes.c_int
    library.QLR_GetTeamSpectatorValue.argtypes = []
    library.QLR_GetTeamSpectatorValue.restype = ctypes.c_int
    return library


@pytest.fixture(scope="module")
def gametype_lifecycle_library(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
    if os.name == "nt":
        pytest.skip("Gametype lifecycle harness requires a POSIX toolchain")
    tmp_path = tmp_path_factory.mktemp("gametype_lifecycle")
    lib_path = _build_gametype_lifecycle_library(tmp_path)
    return _load_gametype_lifecycle_library(lib_path)


def _configure_duel_state(library: ctypes.CDLL) -> None:
    library.QLR_ResetGametypeLifecycleHarness()
    library.QLR_SetGametype(library.QLR_GetGametypeTournamentValue())
    library.QLR_SetWarmupSeconds(5)
    library.QLR_SetWarmupTime(-1)
    library.QLR_SetLevelTime(1000)
    library.QLR_SetNumPlayingClients(2)
    library.QLR_SetTestClientActive(1)
    library.QLR_SetTestClientTeam(library.QLR_GetTeamFreeValue())


@pytest.mark.skipif(os.name == "nt", reason="Gametype lifecycle harness requires a POSIX toolchain")
def test_gametype_init_triggers_duel_branch(gametype_lifecycle_library: ctypes.CDLL) -> None:
    library = gametype_lifecycle_library
    _configure_duel_state(library)

    library.QLR_RunGametypeInit()

    assert library.QLR_GetDuelInitCount() == 1
    assert library.QLR_GetDefaultInitCount() == 1


@pytest.mark.skipif(os.name == "nt", reason="Gametype lifecycle harness requires a POSIX toolchain")
def test_client_begin_triggers_duel_branch(gametype_lifecycle_library: ctypes.CDLL) -> None:
    library = gametype_lifecycle_library
    _configure_duel_state(library)

    library.QLR_RunGametypeClientBegin()

    assert library.QLR_GetDuelClientBeginCount() == 1
    assert library.QLR_GetDefaultBeginCount() == 1


@pytest.mark.skipif(os.name == "nt", reason="Gametype lifecycle harness requires a POSIX toolchain")
def test_client_spawn_triggers_duel_branch(gametype_lifecycle_library: ctypes.CDLL) -> None:
    library = gametype_lifecycle_library
    _configure_duel_state(library)

    library.QLR_RunGametypeClientSpawn()

    assert library.QLR_GetDuelClientSpawnCount() == 1
    assert library.QLR_GetDefaultSpawnCount() == 1
