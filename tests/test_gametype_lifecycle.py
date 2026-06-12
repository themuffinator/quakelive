"""Gametype lifecycle dispatch regression harness."""

from __future__ import annotations

import ctypes
import os
from pathlib import Path

import pytest

from tests.compiler_support import compile_c_binary, find_c_compiler, shared_library_name

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
CODE_DIR = SRC_DIR / "code"
GAME_CODE_DIR = CODE_DIR / "game"

GAMETYPE_LIFECYCLE_SOURCE = (
	"""
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#ifdef WIN32
#define QLR_EXPORT __declspec(dllexport)
#else
#define QLR_EXPORT
#endif

#define QLR_INSTRUMENT_GAMETYPE_LIFECYCLE
#define GAME_INCLUDE
#include "code/game/g_local.h"

level_locals_t level;
vmCvar_t g_gametype;
vmCvar_t g_warmup;
vmCvar_t g_suddenDeathRespawn;
vmCvar_t g_suddenDeathRespawnStart;
vmCvar_t g_suddenDeathRespawnTick;
vmCvar_t g_suddenDeathRespawnMax;
vmCvar_t g_suddenDeathRespawnIncrement;
vmCvar_t g_suddenDeathRespawnPrint;
static const char *s_duelSpawnGrantScript = "weapon_gauntlet weapon_machinegun ammo_bullets 100";
static gclient_t qlr_testClient;
static gentity_t qlr_testEntity;
static char qlr_vaBuffer[MAX_STRING_CHARS];
static char qlr_lastWarmupConfigstring[MAX_STRING_CHARS];
static char qlr_lastGrantScript[MAX_STRING_CHARS];
static int qlr_warmupConfigstringWriteCount;
static int qlr_readyUpConfigstringCount;
static int qlr_roundWarmupCount;
static int qlr_raceClientBeginCount;
static int qlr_raceClientSpawnCount;
static int qlr_grantScriptCount;

/*
=============
Q_strncpyz

Minimal bounded string copy helper for the lifecycle harness.
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
@TAB@dest[destsize - 1] = '\\0';
}

/*
=============
va

Provides a minimal vsnprintf-backed formatter for the harness.
=============
*/
char *va( const char *format, ... ) {
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

Captures warmup configstring writes for lifecycle assertions.
=============
*/
void trap_SetConfigstring( int num, const char *string ) {
@TAB@const char *value;

@TAB@value = string ? string : "";
@TAB@if ( num != CS_WARMUP ) {
@TAB@@TAB@return;
@TAB@}

@TAB@Q_strncpyz( qlr_lastWarmupConfigstring, value, sizeof( qlr_lastWarmupConfigstring ) );
@TAB@qlr_warmupConfigstringWriteCount++;
}

/*
=============
G_UpdateReadyUpConfigstring

Tracks retail ready-up configstring refreshes.
=============
*/
void G_UpdateReadyUpConfigstring( void ) {
@TAB@qlr_readyUpConfigstringCount++;
}

/*
=============
G_SetWarmupTime

Mirrors the shared qagame warmup latch helper for lifecycle-only tests.
=============
*/
void G_SetWarmupTime( int warmupTime ) {
@TAB@level.warmupTime = warmupTime;
@TAB@trap_SetConfigstring( CS_WARMUP, va( "%i", level.warmupTime ) );
@TAB@G_UpdateReadyUpConfigstring();
}

/*
=============
G_RunGrantScript

Captures the duel spawn grant script applied during ClientSpawn.
=============
*/
void G_RunGrantScript( gentity_t *ent, const char *script ) {
@TAB@(void)ent;
@TAB@Q_strncpyz( qlr_lastGrantScript, script, sizeof( qlr_lastGrantScript ) );
@TAB@qlr_grantScriptCount++;
}

/*
=============
G_Frame_BeginRoundWarmup

Records round-based initialisation without mutating state.
=============
*/
void G_Frame_BeginRoundWarmup( void ) {
@TAB@qlr_roundWarmupCount++;
}

/*
=============
G_RaceClientBegin

Tracks race begin dispatch through the lifecycle seam.
=============
*/
void G_RaceClientBegin( gentity_t *ent ) {
@TAB@(void)ent;
@TAB@qlr_raceClientBeginCount++;
}

/*
=============
G_RaceClientSpawn

Tracks race spawn dispatch through the lifecycle seam.
=============
*/
void G_RaceClientSpawn( gentity_t *ent ) {
@TAB@(void)ent;
@TAB@qlr_raceClientSpawnCount++;
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
@TAB@qlr_testEntity.s.number = 0;
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
QLR_EXPORT void QLR_ResetGametypeLifecycleHarness( void ) {
@TAB@memset( &level, 0, sizeof( level ) );
@TAB@level.warmupTime = -1;
@TAB@memset( qlr_duelLifecycleCounts, 0, sizeof( qlr_duelLifecycleCounts ) );
@TAB@memset( qlr_defaultLifecycleCounts, 0, sizeof( qlr_defaultLifecycleCounts ) );
@TAB@memset( qlr_lastWarmupConfigstring, 0, sizeof( qlr_lastWarmupConfigstring ) );
@TAB@memset( qlr_lastGrantScript, 0, sizeof( qlr_lastGrantScript ) );
@TAB@qlr_warmupConfigstringWriteCount = 0;
@TAB@qlr_readyUpConfigstringCount = 0;
@TAB@qlr_roundWarmupCount = 0;
@TAB@qlr_raceClientBeginCount = 0;
@TAB@qlr_raceClientSpawnCount = 0;
@TAB@qlr_grantScriptCount = 0;
@TAB@g_gametype.integer = 0;
@TAB@g_warmup.integer = 0;
@TAB@g_suddenDeathRespawn.integer = 0;
@TAB@g_suddenDeathRespawnStart.integer = 0;
@TAB@g_suddenDeathRespawnTick.integer = 0;
@TAB@g_suddenDeathRespawnMax.integer = 0;
@TAB@g_suddenDeathRespawnIncrement.integer = 0;
@TAB@g_suddenDeathRespawnPrint.integer = 0;
@TAB@QLR_InitTestEntity();
}

/*
=============
QLR_SetGametype

Overrides the active gametype for the harness.
=============
*/
QLR_EXPORT void QLR_SetGametype( int gametype ) {
@TAB@g_gametype.integer = gametype;
}

/*
=============
QLR_SetWarmupSeconds

Configures the g_warmup cvar used by the duel countdown logic.
=============
*/
QLR_EXPORT void QLR_SetWarmupSeconds( int seconds ) {
@TAB@g_warmup.integer = seconds;
}

/*
=============
QLR_SetWarmupTime

Sets the current warmup timestamp tracked on the level struct.
=============
*/
QLR_EXPORT void QLR_SetWarmupTime( int warmupTime ) {
@TAB@level.warmupTime = warmupTime;
}

/*
=============
QLR_SetLevelTime

Controls the simulated server time consumed by duel warmup math.
=============
*/
QLR_EXPORT void QLR_SetLevelTime( int timeMilliseconds ) {
@TAB@level.time = timeMilliseconds;
}

/*
=============
QLR_SetNumPlayingClients

Injects the number of active duel players for begin-stage coverage.
=============
*/
QLR_EXPORT void QLR_SetNumPlayingClients( int count ) {
@TAB@level.numPlayingClients = count;
}

/*
=============
QLR_SetTestClientTeam

Assigns the shared entity's team context for spawn handling.
=============
*/
QLR_EXPORT void QLR_SetTestClientTeam( int team ) {
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
QLR_EXPORT void QLR_SetTestClientActive( int active ) {
@TAB@qlr_testEntity.client = active ? &qlr_testClient : NULL;
}

/*
=============
QLR_RunGametypeInit

Executes the gametype init lifecycle stage.
=============
*/
QLR_EXPORT void QLR_RunGametypeInit( void ) {
@TAB@G_GametypeInit();
}

/*
=============
QLR_RunGametypeClientBegin

Executes the ClientBegin lifecycle stage using the shared entity.
=============
*/
QLR_EXPORT void QLR_RunGametypeClientBegin( void ) {
@TAB@G_GametypeClientBegin( &qlr_testEntity );
}

/*
=============
QLR_RunGametypeClientSpawn

Executes the ClientSpawn lifecycle stage using the shared entity.
=============
*/
QLR_EXPORT void QLR_RunGametypeClientSpawn( void ) {
@TAB@G_GametypeClientSpawn( &qlr_testEntity );
}

/*
=============
QLR_GetDuelInitCount

Reports how often the duel handler processed the init stage.
=============
*/
QLR_EXPORT int QLR_GetDuelInitCount( void ) {
@TAB@return qlr_duelLifecycleCounts[GAMETYPE_LIFECYCLE_INIT];
}

/*
=============
QLR_GetDuelClientBeginCount

Reports how often the duel handler processed the ClientBegin stage.
=============
*/
QLR_EXPORT int QLR_GetDuelClientBeginCount( void ) {
@TAB@return qlr_duelLifecycleCounts[GAMETYPE_LIFECYCLE_CLIENT_BEGIN];
}

/*
=============
QLR_GetDuelClientSpawnCount

Reports how often the duel handler processed the ClientSpawn stage.
=============
*/
QLR_EXPORT int QLR_GetDuelClientSpawnCount( void ) {
@TAB@return qlr_duelLifecycleCounts[GAMETYPE_LIFECYCLE_CLIENT_SPAWN];
}

/*
=============
QLR_GetDefaultInitCount

Reports how often the default handler processed the init stage.
=============
*/
QLR_EXPORT int QLR_GetDefaultInitCount( void ) {
@TAB@return qlr_defaultLifecycleCounts[GAMETYPE_LIFECYCLE_INIT];
}

/*
=============
QLR_GetDefaultBeginCount

Reports how often the default handler processed the ClientBegin stage.
=============
*/
QLR_EXPORT int QLR_GetDefaultBeginCount( void ) {
@TAB@return qlr_defaultLifecycleCounts[GAMETYPE_LIFECYCLE_CLIENT_BEGIN];
}

/*
=============
QLR_GetDefaultSpawnCount

Reports how often the default handler processed the ClientSpawn stage.
=============
*/
QLR_EXPORT int QLR_GetDefaultSpawnCount( void ) {
@TAB@return qlr_defaultLifecycleCounts[GAMETYPE_LIFECYCLE_CLIENT_SPAWN];
}

/*
=============
QLR_GetWarmupTime

Exposes the tracked level warmup timestamp for lifecycle assertions.
=============
*/
QLR_EXPORT int QLR_GetWarmupTime( void ) {
@TAB@return level.warmupTime;
}

/*
=============
QLR_GetWarmupConfigstringWriteCount

Reports how often CS_WARMUP was refreshed by the lifecycle helpers.
=============
*/
QLR_EXPORT int QLR_GetWarmupConfigstringWriteCount( void ) {
@TAB@return qlr_warmupConfigstringWriteCount;
}

/*
=============
QLR_GetLastWarmupConfigstring

Returns the most recent CS_WARMUP payload captured by the harness.
=============
*/
QLR_EXPORT const char *QLR_GetLastWarmupConfigstring( void ) {
@TAB@return qlr_lastWarmupConfigstring;
}

/*
=============
QLR_GetReadyUpConfigstringCount

Reports ready-up configstring refresh calls.
=============
*/
QLR_EXPORT int QLR_GetReadyUpConfigstringCount( void ) {
@TAB@return qlr_readyUpConfigstringCount;
}

/*
=============
QLR_GetRoundWarmupCount

Reports round-warmup initialisation dispatches.
=============
*/
QLR_EXPORT int QLR_GetRoundWarmupCount( void ) {
@TAB@return qlr_roundWarmupCount;
}

/*
=============
QLR_GetRaceClientBeginCount

Reports race-specific ClientBegin dispatches.
=============
*/
QLR_EXPORT int QLR_GetRaceClientBeginCount( void ) {
@TAB@return qlr_raceClientBeginCount;
}

/*
=============
QLR_GetRaceClientSpawnCount

Reports race-specific ClientSpawn dispatches.
=============
*/
QLR_EXPORT int QLR_GetRaceClientSpawnCount( void ) {
@TAB@return qlr_raceClientSpawnCount;
}

/*
=============
QLR_GetGrantScriptCount

Reports how often the duel spawn loadout script ran.
=============
*/
QLR_EXPORT int QLR_GetGrantScriptCount( void ) {
@TAB@return qlr_grantScriptCount;
}

/*
=============
QLR_GetLastGrantScript

Returns the most recent duel spawn grant script captured by the harness.
=============
*/
QLR_EXPORT const char *QLR_GetLastGrantScript( void ) {
@TAB@return qlr_lastGrantScript;
}

/*
=============
QLR_GetGametypeTournamentValue

Exposes the GT_TOURNAMENT enumeration value to Python tests.
=============
*/
QLR_EXPORT int QLR_GetGametypeTournamentValue( void ) {
@TAB@return GT_TOURNAMENT;
}

/*
=============
QLR_GetGametypeRaceValue

Exposes the GT_RACE enumeration value to Python tests.
=============
*/
QLR_EXPORT int QLR_GetGametypeRaceValue( void ) {
@TAB@return GT_RACE;
}

/*
=============
QLR_GetGametypeClanArenaValue

Exposes the GT_CLAN_ARENA enumeration value to Python tests.
=============
*/
QLR_EXPORT int QLR_GetGametypeClanArenaValue( void ) {
@TAB@return GT_CLAN_ARENA;
}

/*
=============
QLR_GetGametypeRedRoverValue

Exposes the GT_RED_ROVER enumeration value to Python tests.
=============
*/
QLR_EXPORT int QLR_GetGametypeRedRoverValue( void ) {
@TAB@return GT_RED_ROVER;
}

/*
=============
QLR_GetTeamFreeValue

Exposes the TEAM_FREE enumeration value to Python tests.
=============
*/
QLR_EXPORT int QLR_GetTeamFreeValue( void ) {
@TAB@return TEAM_FREE;
}

/*
=============
QLR_GetTeamSpectatorValue

Exposes the TEAM_SPECTATOR enumeration value to Python tests.
=============
*/
QLR_EXPORT int QLR_GetTeamSpectatorValue( void ) {
@TAB@return TEAM_SPECTATOR;
}
"""
).replace("@TAB@", "\t")


def _build_gametype_lifecycle_library(tmp_path: Path) -> Path:
	src_path = tmp_path / "gametype_lifecycle_test.c"
	src_path.write_text(GAMETYPE_LIFECYCLE_SOURCE, encoding="utf-8")

	compiler = find_c_compiler()
	if compiler is None:
		pytest.skip("No supported C compiler is available for gametype lifecycle probes.")

	lib_path = tmp_path / shared_library_name("gametype_lifecycle_test")
	extra_cflags = (
		["-Wall", "-Werror", "-Wno-return-type"]
		if not compiler.is_msvc and os.name == "nt"
		else (["-Wall", "-Werror"] if not compiler.is_msvc else ["/W3", "/WX"])
	)

	compile_c_binary(
		compiler,
		[src_path],
		lib_path,
		include_dirs=[
			SRC_DIR,
			CODE_DIR,
			GAME_CODE_DIR,
		],
		extra_cflags=extra_cflags,
		shared=True,
		workdir=REPO_ROOT,
	)
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
	library.QLR_GetWarmupTime.argtypes = []
	library.QLR_GetWarmupTime.restype = ctypes.c_int
	library.QLR_GetWarmupConfigstringWriteCount.argtypes = []
	library.QLR_GetWarmupConfigstringWriteCount.restype = ctypes.c_int
	library.QLR_GetLastWarmupConfigstring.argtypes = []
	library.QLR_GetLastWarmupConfigstring.restype = ctypes.c_char_p
	library.QLR_GetReadyUpConfigstringCount.argtypes = []
	library.QLR_GetReadyUpConfigstringCount.restype = ctypes.c_int
	library.QLR_GetRoundWarmupCount.argtypes = []
	library.QLR_GetRoundWarmupCount.restype = ctypes.c_int
	library.QLR_GetRaceClientBeginCount.argtypes = []
	library.QLR_GetRaceClientBeginCount.restype = ctypes.c_int
	library.QLR_GetRaceClientSpawnCount.argtypes = []
	library.QLR_GetRaceClientSpawnCount.restype = ctypes.c_int
	library.QLR_GetGrantScriptCount.argtypes = []
	library.QLR_GetGrantScriptCount.restype = ctypes.c_int
	library.QLR_GetLastGrantScript.argtypes = []
	library.QLR_GetLastGrantScript.restype = ctypes.c_char_p
	library.QLR_GetGametypeTournamentValue.argtypes = []
	library.QLR_GetGametypeTournamentValue.restype = ctypes.c_int
	library.QLR_GetGametypeRaceValue.argtypes = []
	library.QLR_GetGametypeRaceValue.restype = ctypes.c_int
	library.QLR_GetGametypeClanArenaValue.argtypes = []
	library.QLR_GetGametypeClanArenaValue.restype = ctypes.c_int
	library.QLR_GetGametypeRedRoverValue.argtypes = []
	library.QLR_GetGametypeRedRoverValue.restype = ctypes.c_int
	library.QLR_GetTeamFreeValue.argtypes = []
	library.QLR_GetTeamFreeValue.restype = ctypes.c_int
	library.QLR_GetTeamSpectatorValue.argtypes = []
	library.QLR_GetTeamSpectatorValue.restype = ctypes.c_int
	return library


@pytest.fixture(scope="module")
def gametype_lifecycle_library(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
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


def _configure_race_state(library: ctypes.CDLL) -> None:
	library.QLR_ResetGametypeLifecycleHarness()
	library.QLR_SetGametype(library.QLR_GetGametypeRaceValue())
	library.QLR_SetTestClientActive(1)
	library.QLR_SetTestClientTeam(library.QLR_GetTeamFreeValue())


def test_gametype_init_resets_duel_warmup_and_refreshes_configstrings(
	gametype_lifecycle_library: ctypes.CDLL,
) -> None:
	library = gametype_lifecycle_library
	_configure_duel_state(library)
	library.QLR_SetWarmupTime(7777)

	library.QLR_RunGametypeInit()

	assert library.QLR_GetDuelInitCount() == 1
	assert library.QLR_GetDefaultInitCount() == 1
	assert library.QLR_GetWarmupTime() == -1
	assert library.QLR_GetWarmupConfigstringWriteCount() == 1
	assert library.QLR_GetLastWarmupConfigstring() == b"-1"
	assert library.QLR_GetReadyUpConfigstringCount() == 1


def test_duel_client_begin_starts_countdown_when_both_players_are_present(
	gametype_lifecycle_library: ctypes.CDLL,
) -> None:
	library = gametype_lifecycle_library
	_configure_duel_state(library)

	library.QLR_RunGametypeClientBegin()

	assert library.QLR_GetDuelClientBeginCount() == 1
	assert library.QLR_GetDefaultBeginCount() == 1
	assert library.QLR_GetWarmupTime() == 5000
	assert library.QLR_GetWarmupConfigstringWriteCount() == 1
	assert library.QLR_GetLastWarmupConfigstring() == b"5000"
	assert library.QLR_GetReadyUpConfigstringCount() == 1


def test_duel_client_begin_clears_countdown_when_players_drop_below_two(
	gametype_lifecycle_library: ctypes.CDLL,
) -> None:
	library = gametype_lifecycle_library
	_configure_duel_state(library)
	library.QLR_SetNumPlayingClients(1)
	library.QLR_SetWarmupTime(9000)

	library.QLR_RunGametypeClientBegin()

	assert library.QLR_GetDuelClientBeginCount() == 1
	assert library.QLR_GetDefaultBeginCount() == 1
	assert library.QLR_GetWarmupTime() == -1
	assert library.QLR_GetWarmupConfigstringWriteCount() == 1
	assert library.QLR_GetLastWarmupConfigstring() == b"-1"
	assert library.QLR_GetReadyUpConfigstringCount() == 1


def test_duel_client_spawn_applies_the_retail_grant_script_to_active_players(
	gametype_lifecycle_library: ctypes.CDLL,
) -> None:
	library = gametype_lifecycle_library
	_configure_duel_state(library)

	library.QLR_RunGametypeClientSpawn()

	assert library.QLR_GetDuelClientSpawnCount() == 1
	assert library.QLR_GetDefaultSpawnCount() == 1
	assert library.QLR_GetGrantScriptCount() == 1
	assert library.QLR_GetLastGrantScript() == b"weapon_gauntlet weapon_machinegun ammo_bullets 100"


def test_duel_client_spawn_skips_spectator_loadout_grants(
	gametype_lifecycle_library: ctypes.CDLL,
) -> None:
	library = gametype_lifecycle_library
	_configure_duel_state(library)
	library.QLR_SetTestClientTeam(library.QLR_GetTeamSpectatorValue())

	library.QLR_RunGametypeClientSpawn()

	assert library.QLR_GetDuelClientSpawnCount() == 1
	assert library.QLR_GetDefaultSpawnCount() == 1
	assert library.QLR_GetGrantScriptCount() == 0
	assert library.QLR_GetLastGrantScript() == b""


def test_race_lifecycle_routes_begin_and_spawn_hooks_without_round_warmup(
	gametype_lifecycle_library: ctypes.CDLL,
) -> None:
	library = gametype_lifecycle_library
	_configure_race_state(library)

	library.QLR_RunGametypeInit()
	library.QLR_RunGametypeClientBegin()
	library.QLR_RunGametypeClientSpawn()

	assert library.QLR_GetDefaultInitCount() == 1
	assert library.QLR_GetDefaultBeginCount() == 1
	assert library.QLR_GetDefaultSpawnCount() == 1
	assert library.QLR_GetRaceClientBeginCount() == 1
	assert library.QLR_GetRaceClientSpawnCount() == 1
	assert library.QLR_GetRoundWarmupCount() == 0
	assert library.QLR_GetWarmupConfigstringWriteCount() == 0


@pytest.mark.parametrize("gametype_getter", ["QLR_GetGametypeClanArenaValue", "QLR_GetGametypeRedRoverValue"])
def test_round_based_lifecycle_only_primes_round_warmup_during_init(
	gametype_lifecycle_library: ctypes.CDLL,
	gametype_getter: str,
) -> None:
	library = gametype_lifecycle_library
	library.QLR_ResetGametypeLifecycleHarness()
	library.QLR_SetGametype(getattr(library, gametype_getter)())

	library.QLR_RunGametypeInit()
	library.QLR_RunGametypeClientBegin()
	library.QLR_RunGametypeClientSpawn()

	assert library.QLR_GetRoundWarmupCount() == 1
	assert library.QLR_GetDefaultInitCount() == 0
	assert library.QLR_GetDefaultBeginCount() == 0
	assert library.QLR_GetDefaultSpawnCount() == 0
	assert library.QLR_GetRaceClientBeginCount() == 0
	assert library.QLR_GetRaceClientSpawnCount() == 0
