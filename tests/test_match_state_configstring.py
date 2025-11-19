"""Regression tests for the match-state configstring payload."""

from __future__ import annotations

from pathlib import Path
import ctypes
import os
import subprocess
import sys
from typing import Dict

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
CODE_DIR = SRC_DIR / "code"
GAME_CODE_DIR = CODE_DIR / "game"

MATCH_STATE_SOURCE = (
    """
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define GAME_INCLUDE
#include "code/game/g_match_state.c"

level_locals_t level;
matchFactoryConfig_t g_matchFactoryConfig;
vmCvar_t g_gametype;

static char qlr_matchStateConfig[MAX_INFO_STRING];

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
@TAB@dest[destsize - 1] = 0;
}

/*
=============
Com_sprintf

Minimal vsnprintf wrapper for match-state tests.
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
@TAB@Com_sprintf( buffer, sizeof( buffer ), "%c%s%c%s", '\\\\', key, '\\\\', value );
@TAB@if ( strlen( buffer ) + strlen( info ) >= MAX_INFO_STRING ) {
@TAB@@TAB@return;
@TAB@}
@TAB@strcat( info, buffer );
}

/*
=============
Info_ValueForKey

Searches an info string for the value associated with the requested key.
=============
*/
char *Info_ValueForKey( const char *info, const char *key ) {
@TAB@static char valueBuffers[2][MAX_INFO_STRING];
@TAB@static int bufferIndex = 0;
@TAB@const char *keyStart;
@TAB@const char *valueStart;
@TAB@int keyLength;
@TAB@int valueLength;
@TAB@size_t lookupLength;
@TAB@char *out;

@TAB@bufferIndex ^= 1;
@TAB@out = valueBuffers[bufferIndex];
@TAB@out[0] = 0;

@TAB@if ( !info || !key || !*key ) {
@TAB@@TAB@return out;
@TAB@}

@TAB@lookupLength = strlen( key );
@TAB@while ( *info ) {
@TAB@@TAB@if ( *info == '\\\\' ) {
@TAB@@TAB@@TAB@info++;
@TAB@@TAB@}
@TAB@@TAB@keyStart = info;
@TAB@@TAB@while ( *info && *info != '\\\\' ) {
@TAB@@TAB@@TAB@info++;
@TAB@@TAB@}
@TAB@@TAB@keyLength = info - keyStart;
@TAB@@TAB@if ( *info == '\\\\' ) {
@TAB@@TAB@@TAB@info++;
@TAB@@TAB@}
@TAB@@TAB@valueStart = info;
@TAB@@TAB@while ( *info && *info != '\\\\' ) {
@TAB@@TAB@@TAB@info++;
@TAB@@TAB@}
@TAB@@TAB@if ( keyLength == (int)lookupLength && strncmp( keyStart, key, lookupLength ) == 0 ) {
@TAB@@TAB@@TAB@valueLength = info - valueStart;
@TAB@@TAB@@TAB@if ( valueLength >= MAX_INFO_STRING ) {
@TAB@@TAB@@TAB@@TAB@valueLength = MAX_INFO_STRING - 1;
@TAB@@TAB@@TAB@}
@TAB@@TAB@@TAB@memcpy( out, valueStart, (size_t)valueLength );
@TAB@@TAB@@TAB@out[valueLength] = 0;
@TAB@@TAB@@TAB@return out;
@TAB@@TAB@}
@TAB@}

@TAB@return out;
}

/*
=============
trap_SetConfigstring

Captures configstring updates from g_match_state.c.
=============
*/
void trap_SetConfigstring( int num, const char *string ) {
@TAB@const char *value = string ? string : "";
@TAB@if ( num != CS_MATCH_STATE ) {
@TAB@@TAB@return;
@TAB@}
@TAB@Q_strncpyz( qlr_matchStateConfig, value, sizeof( qlr_matchStateConfig ) );
}

/*
=============
trap_Cvar_Update

Stubbed cvar updater to satisfy shared headers.
=============
*/
void trap_Cvar_Update( vmCvar_t *cvar ) {
@TAB@(void)cvar;
}

/*
=============
QLR_ClearMatchStateConfig

Resets the captured configstring buffer.
=============
*/
static void QLR_ClearMatchStateConfig( void ) {
@TAB@memset( qlr_matchStateConfig, 0, sizeof( qlr_matchStateConfig ) );
}

/*
=============
QLR_ResetMatchState

Restores globals to default values between tests.
=============
*/
void QLR_ResetMatchState( void ) {
@TAB@memset( &level, 0, sizeof( level ) );
@TAB@memset( &g_matchFactoryConfig, 0, sizeof( g_matchFactoryConfig ) );
@TAB@g_gametype.integer = GT_TEAM;
@TAB@QLR_ClearMatchStateConfig();
}

/*
=============
QLR_SeedMatchStateValues

Initialises representative round, overtime, and timeout state.
=============
*/
static void QLR_SeedMatchStateValues( void ) {
@TAB@level.roundTransitionTime = 222222;
@TAB@level.roundNumber = 9;
@TAB@level.roundState = ROUNDSTATE_ACTIVE;
@TAB@level.overtimeActive = qtrue;
@TAB@level.overtimeStartTime = 111111;
@TAB@level.overtimeEndTime = 222333;
@TAB@level.overtimeCount = 3;
@TAB@level.timeoutActive = qtrue;
@TAB@level.timeoutTeam = TEAM_BLUE;
@TAB@level.timeoutExpireTime = 333444;
@TAB@level.timeoutOwner = 7;
@TAB@level.timeoutRemaining[TEAM_RED] = 60000;
@TAB@level.timeoutRemaining[TEAM_BLUE] = 45000;
@TAB@g_matchFactoryConfig.timeoutLengthSeconds = 75;
@TAB@g_matchFactoryConfig.timeoutCountPerTeam = 2;
@TAB@g_matchFactoryConfig.overtimeLengthSeconds = 120;
@TAB@g_matchFactoryConfig.suddenDeathRespawnsEnabled = qtrue;
@TAB@g_matchFactoryConfig.suddenDeathStartSeconds = 15;
@TAB@g_matchFactoryConfig.suddenDeathTickSeconds = 5;
@TAB@g_matchFactoryConfig.suddenDeathMaxSeconds = 60;
@TAB@g_matchFactoryConfig.suddenDeathIncrementSeconds = 3;
@TAB@g_matchFactoryConfig.suddenDeathPrintAnnouncements = qtrue;
@TAB@g_matchFactoryConfig.suddenDeathSpawnDelayActive = qtrue;
}

/*
=============
QLR_BuildMatchStateConfigstring

Populates level state and emits the configstring payload.
=============
*/
void QLR_BuildMatchStateConfigstring( void ) {
@TAB@QLR_SeedMatchStateValues();
@TAB@G_UpdateMatchStateConfigString();
}

/*
=============
QLR_GetMatchStateConfigstring

Exposes the captured configstring to the Python harness.
=============
*/
const char *QLR_GetMatchStateConfigstring( void ) {
@TAB@return qlr_matchStateConfig;
}

typedef struct qlrClientMatchState_s {
@TAB@int matchTimeoutLengthSeconds;
@TAB@int matchTimeoutCountPerTeam;
@TAB@int matchOvertimeLengthSeconds;
@TAB@qboolean matchSuddenDeathRespawnsEnabled;
@TAB@int matchSuddenDeathStartSeconds;
@TAB@int matchSuddenDeathTickSeconds;
@TAB@int matchSuddenDeathMaxSeconds;
@TAB@int matchSuddenDeathIncrementSeconds;
@TAB@qboolean matchSuddenDeathPrintAnnouncements;
@TAB@qboolean matchSuddenDeathSpawnDelayActive;
} qlrClientMatchState_t;

static qlrClientMatchState_t qlr_clientMatchState;

/*
=============
QLR_ResetClientMatchState

Clears the cached client-side match factory values between tests.
=============
*/
void QLR_ResetClientMatchState( void ) {
@TAB@memset( &qlr_clientMatchState, 0, sizeof( qlr_clientMatchState ) );
}

/*
=============
QLR_InfoIntForMatchKey

Lightweight info-string integer parser for the client harness.
=============
*/
static int QLR_InfoIntForMatchKey( const char *info, const char *key, int defaultValue ) {
@TAB@const char *value;

@TAB@if ( !info || !key ) {
@TAB@@TAB@return defaultValue;
@TAB@}

@TAB@value = Info_ValueForKey( info, key );
@TAB@if ( !value || !*value ) {
@TAB@@TAB@return defaultValue;
@TAB@}

@TAB@return atoi( value );
}

/*
=============
QLR_ParseMatchStateOnClient

Parses the captured configstring and populates the fake client state.
=============
*/
void QLR_ParseMatchStateOnClient( void ) {
@TAB@const char *info;

@TAB@info = QLR_GetMatchStateConfigstring();
@TAB@QLR_ResetClientMatchState();
@TAB@if ( !info || !*info ) {
@TAB@@TAB@return;
@TAB@}

@TAB@qlr_clientMatchState.matchTimeoutLengthSeconds = QLR_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_LENGTH, 0 );
@TAB@qlr_clientMatchState.matchTimeoutCountPerTeam = QLR_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_COUNT, 0 );
@TAB@qlr_clientMatchState.matchOvertimeLengthSeconds = QLR_InfoIntForMatchKey( info, MATCH_STATE_KEY_OVERTIME_LENGTH, 0 );
@TAB@qlr_clientMatchState.matchSuddenDeathRespawnsEnabled = QLR_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_RESPAWNS, 0 ) ? qtrue : qfalse;
@TAB@qlr_clientMatchState.matchSuddenDeathStartSeconds = QLR_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_START, 0 );
@TAB@qlr_clientMatchState.matchSuddenDeathTickSeconds = QLR_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_TICK, 0 );
@TAB@qlr_clientMatchState.matchSuddenDeathMaxSeconds = QLR_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_MAX, 0 );
@TAB@qlr_clientMatchState.matchSuddenDeathIncrementSeconds = QLR_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_INCREMENT, 0 );
@TAB@qlr_clientMatchState.matchSuddenDeathPrintAnnouncements = QLR_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_PRINT, 0 ) ? qtrue : qfalse;
@TAB@qlr_clientMatchState.matchSuddenDeathSpawnDelayActive = QLR_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_DELAY, 0 ) ? qtrue : qfalse;
}

/*
=============
QLR_GetClientTimeoutLengthSeconds

Exposes the parsed timeout length for assertions.
=============
*/
int QLR_GetClientTimeoutLengthSeconds( void ) {
@TAB@return qlr_clientMatchState.matchTimeoutLengthSeconds;
}

/*
=============
QLR_GetClientTimeoutCountPerTeam

Exposes the parsed timeout quota for assertions.
=============
*/
int QLR_GetClientTimeoutCountPerTeam( void ) {
@TAB@return qlr_clientMatchState.matchTimeoutCountPerTeam;
}

/*
=============
QLR_GetClientOvertimeLengthSeconds

Exposes the parsed overtime window for assertions.
=============
*/
int QLR_GetClientOvertimeLengthSeconds( void ) {
@TAB@return qlr_clientMatchState.matchOvertimeLengthSeconds;
}

/*
=============
QLR_GetClientSuddenDeathRespawnsEnabled

Indicates whether the client saw sudden-death respawns enabled.
=============
*/
int QLR_GetClientSuddenDeathRespawnsEnabled( void ) {
@TAB@return qlr_clientMatchState.matchSuddenDeathRespawnsEnabled ? 1 : 0;
}

/*
=============
QLR_GetClientSuddenDeathStartSeconds

Exposes the parsed sudden-death start time.
=============
*/
int QLR_GetClientSuddenDeathStartSeconds( void ) {
@TAB@return qlr_clientMatchState.matchSuddenDeathStartSeconds;
}

/*
=============
QLR_GetClientSuddenDeathTickSeconds

Exposes the parsed sudden-death tick interval.
=============
*/
int QLR_GetClientSuddenDeathTickSeconds( void ) {
@TAB@return qlr_clientMatchState.matchSuddenDeathTickSeconds;
}

/*
=============
QLR_GetClientSuddenDeathMaxSeconds

Exposes the parsed sudden-death max duration.
=============
*/
int QLR_GetClientSuddenDeathMaxSeconds( void ) {
@TAB@return qlr_clientMatchState.matchSuddenDeathMaxSeconds;
}

/*
=============
QLR_GetClientSuddenDeathIncrementSeconds

Exposes the parsed sudden-death increment.
=============
*/
int QLR_GetClientSuddenDeathIncrementSeconds( void ) {
@TAB@return qlr_clientMatchState.matchSuddenDeathIncrementSeconds;
}

/*
=============
QLR_GetClientSuddenDeathPrintAnnouncements

Indicates whether the client observed sudden-death announcements enabled.
=============
*/
int QLR_GetClientSuddenDeathPrintAnnouncements( void ) {
@TAB@return qlr_clientMatchState.matchSuddenDeathPrintAnnouncements ? 1 : 0;
}

/*
=============
QLR_GetClientSuddenDeathSpawnDelayActive

Indicates whether spawn delay is active for sudden-death.
=============
*/
int QLR_GetClientSuddenDeathSpawnDelayActive( void ) {
@TAB@return qlr_clientMatchState.matchSuddenDeathSpawnDelayActive ? 1 : 0;
}
"""
).replace("@TAB@", "\t")


def _parse_info_string(payload: str) -> Dict[str, str]:
    data = payload.strip("\\")
    if not data:
        return {}
    tokens = data.split("\\")
    return {tokens[i]: tokens[i + 1] for i in range(0, len(tokens) - 1, 2)}


def _build_match_state_library(tmp_path: Path) -> Path:
    src_path = tmp_path / "match_state_configstring_test.c"
    src_path.write_text(MATCH_STATE_SOURCE, encoding="utf-8")

    if sys.platform == "darwin":
        lib_path = tmp_path / "libmatch_state_configstring_test.dylib"
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
            "-I",
            str(SRC_DIR / "game"),
            "-o",
            str(lib_path),
            str(src_path),
        ]
    elif os.name == "nt":
        raise RuntimeError("Match-state harness requires a POSIX toolchain")
    else:
        lib_path = tmp_path / "libmatch_state_configstring_test.so"
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
            "-I",
            str(SRC_DIR / "game"),
            "-o",
            str(lib_path),
            str(src_path),
        ]

    subprocess.run(compile_cmd, check=True)
    return lib_path


def _load_match_state_library(lib_path: Path) -> ctypes.CDLL:
    library = ctypes.CDLL(str(lib_path))
    library.QLR_ResetMatchState.argtypes = []
    library.QLR_ResetMatchState.restype = None
    library.QLR_BuildMatchStateConfigstring.argtypes = []
    library.QLR_BuildMatchStateConfigstring.restype = None
    library.QLR_GetMatchStateConfigstring.argtypes = []
    library.QLR_GetMatchStateConfigstring.restype = ctypes.c_char_p
    library.QLR_ResetClientMatchState.argtypes = []
    library.QLR_ResetClientMatchState.restype = None
    library.QLR_ParseMatchStateOnClient.argtypes = []
    library.QLR_ParseMatchStateOnClient.restype = None
    library.QLR_GetClientTimeoutLengthSeconds.argtypes = []
    library.QLR_GetClientTimeoutLengthSeconds.restype = ctypes.c_int
    library.QLR_GetClientTimeoutCountPerTeam.argtypes = []
    library.QLR_GetClientTimeoutCountPerTeam.restype = ctypes.c_int
    library.QLR_GetClientOvertimeLengthSeconds.argtypes = []
    library.QLR_GetClientOvertimeLengthSeconds.restype = ctypes.c_int
    library.QLR_GetClientSuddenDeathRespawnsEnabled.argtypes = []
    library.QLR_GetClientSuddenDeathRespawnsEnabled.restype = ctypes.c_int
    library.QLR_GetClientSuddenDeathStartSeconds.argtypes = []
    library.QLR_GetClientSuddenDeathStartSeconds.restype = ctypes.c_int
    library.QLR_GetClientSuddenDeathTickSeconds.argtypes = []
    library.QLR_GetClientSuddenDeathTickSeconds.restype = ctypes.c_int
    library.QLR_GetClientSuddenDeathMaxSeconds.argtypes = []
    library.QLR_GetClientSuddenDeathMaxSeconds.restype = ctypes.c_int
    library.QLR_GetClientSuddenDeathIncrementSeconds.argtypes = []
    library.QLR_GetClientSuddenDeathIncrementSeconds.restype = ctypes.c_int
    library.QLR_GetClientSuddenDeathPrintAnnouncements.argtypes = []
    library.QLR_GetClientSuddenDeathPrintAnnouncements.restype = ctypes.c_int
    library.QLR_GetClientSuddenDeathSpawnDelayActive.argtypes = []
    library.QLR_GetClientSuddenDeathSpawnDelayActive.restype = ctypes.c_int
    return library


@pytest.fixture(scope="module")
def match_state_library(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
    if os.name == "nt":
        pytest.skip("Match-state harness requires a POSIX toolchain")
    tmp_path = tmp_path_factory.mktemp("match_state_configstring")
    lib_path = _build_match_state_library(tmp_path)
    return _load_match_state_library(lib_path)


@pytest.mark.skipif(os.name == "nt", reason="Match-state harness requires a POSIX toolchain")
def test_match_state_configstring_includes_expected_keys(match_state_library: ctypes.CDLL) -> None:
    library = match_state_library
    library.QLR_ResetMatchState()
    library.QLR_BuildMatchStateConfigstring()

    payload = library.QLR_GetMatchStateConfigstring()
    assert payload is not None

    info = payload.decode("utf-8")
    fields = _parse_info_string(info)
    expected = {
        "time": "222222",
        "round": "9",
        "turn": "1",
        "state": "2",
        "otActive": "1",
        "otStart": "111111",
        "otEnd": "222333",
        "otCount": "3",
        "otLength": "120",
        "toActive": "1",
        "toTeam": "2",
        "toExpire": "333444",
        "toOwner": "7",
        "toRed": "60000",
        "toBlue": "45000",
        "toLength": "75",
        "toCount": "2",
        "sdRespawns": "1",
        "sdStart": "15",
        "sdTick": "5",
        "sdMax": "60",
        "sdInc": "3",
        "sdPrint": "1",
        "sdDelay": "1",
    }

    for key, expected_value in expected.items():
        assert fields.get(key) == expected_value, f"Missing or incorrect value for {key}"


@pytest.mark.skipif(os.name == "nt", reason="Match-state harness requires a POSIX toolchain")
def test_client_parser_receives_factory_config(match_state_library: ctypes.CDLL) -> None:
    library = match_state_library
    library.QLR_ResetMatchState()
    library.QLR_ResetClientMatchState()
    library.QLR_BuildMatchStateConfigstring()
    library.QLR_ParseMatchStateOnClient()

    assert library.QLR_GetClientTimeoutLengthSeconds() == 75
    assert library.QLR_GetClientTimeoutCountPerTeam() == 2
    assert library.QLR_GetClientOvertimeLengthSeconds() == 120
    assert library.QLR_GetClientSuddenDeathRespawnsEnabled() == 1
    assert library.QLR_GetClientSuddenDeathStartSeconds() == 15
    assert library.QLR_GetClientSuddenDeathTickSeconds() == 5
    assert library.QLR_GetClientSuddenDeathMaxSeconds() == 60
    assert library.QLR_GetClientSuddenDeathIncrementSeconds() == 3
    assert library.QLR_GetClientSuddenDeathPrintAnnouncements() == 1
    assert library.QLR_GetClientSuddenDeathSpawnDelayActive() == 1
