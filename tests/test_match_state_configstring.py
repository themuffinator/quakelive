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

typedef struct qlr_cgs_s {
        qboolean        matchOvertimeActive;
        int             matchOvertimeStartTime;
        int             matchOvertimeEndTime;
        int             matchOvertimeCount;
        qboolean        matchTimeoutActive;
        int             matchTimeoutTeam;
        int             matchTimeoutExpireTime;
        int             matchTimeoutOwner;
        int             matchTimeoutRemaining[TEAM_NUM_TEAMS];
        int             matchTimeoutLengthSeconds;
        int             matchTimeoutCountPerTeam;
        int             matchOvertimeLengthSeconds;
        qboolean        matchSuddenDeathRespawnsEnabled;
        int             matchSuddenDeathStartSeconds;
        int             matchSuddenDeathTickSeconds;
        int             matchSuddenDeathMaxSeconds;
        int             matchSuddenDeathIncrementSeconds;
        qboolean        matchSuddenDeathPrintAnnouncements;
        qboolean        matchSuddenDeathSpawnDelayActive;
        int             matchRoundTransitionTime;
        int             matchRoundNumber;
        int             matchRoundTurn;
        int             matchRoundState;
} cgs_t;

extern cgs_t cgs;
const char *CG_ConfigString( int index );

#include "code/cgame/cg_match_state_parse_impl.h"

level_locals_t level;
matchFactoryConfig_t g_matchFactoryConfig;
vmCvar_t g_gametype;
cgs_t cgs;

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
@TAB@dest[destsize - 1] = '\\0';
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

Retrieves the value for a key from an info string payload.
=============
*/
#define INFO_SEPARATOR_CHAR 92
char *Info_ValueForKey( const char *info, const char *key ) {
@TAB@static char valuePool[2][MAX_INFO_STRING];
@TAB@static int poolIndex = 0;
@TAB@const char *cursor;
@TAB@const char *keyStart;
@TAB@const char *valueStart;
@TAB@size_t keyLength;
@TAB@size_t tokenLength;
@TAB@size_t valueLength;

@TAB@if ( !info || !key || !*key ) {
@TAB@@TAB@return "";
@TAB@}

@TAB@keyLength = strlen( key );
@TAB@cursor = info;
@TAB@while ( (unsigned char)*cursor == INFO_SEPARATOR_CHAR ) {
@TAB@@TAB@cursor++;
@TAB@@TAB@keyStart = cursor;
@TAB@@TAB@while ( *cursor && (unsigned char)*cursor != INFO_SEPARATOR_CHAR ) {
@TAB@@TAB@@TAB@cursor++;
@TAB@@TAB@}
@TAB@@TAB@tokenLength = (size_t)( cursor - keyStart );
@TAB@@TAB@if ( tokenLength == keyLength && !strncmp( keyStart, key, keyLength ) ) {
@TAB@@TAB@@TAB@if ( (unsigned char)*cursor == INFO_SEPARATOR_CHAR ) {
@TAB@@TAB@@TAB@@TAB@cursor++;
@TAB@@TAB@@TAB@}
@TAB@@TAB@@TAB@valueStart = cursor;
@TAB@@TAB@@TAB@while ( *cursor && (unsigned char)*cursor != INFO_SEPARATOR_CHAR ) {
@TAB@@TAB@@TAB@@TAB@cursor++;
@TAB@@TAB@@TAB@}
@TAB@@TAB@@TAB@valueLength = cursor - valueStart;
@TAB@@TAB@@TAB@if ( valueLength >= sizeof( valuePool[0] ) ) {
@TAB@@TAB@@TAB@@TAB@valueLength = sizeof( valuePool[0] ) - 1u;
@TAB@@TAB@@TAB@}
@TAB@@TAB@@TAB@poolIndex ^= 1;
@TAB@@TAB@@TAB@memcpy( valuePool[poolIndex], valueStart, valueLength );
@TAB@@TAB@@TAB@valuePool[poolIndex][valueLength] = '\\0';
@TAB@@TAB@@TAB@return valuePool[poolIndex];
@TAB@@TAB@}
@TAB@@TAB@if ( (unsigned char)*cursor == INFO_SEPARATOR_CHAR ) {
@TAB@@TAB@@TAB@cursor++;
@TAB@@TAB@@TAB@while ( *cursor && (unsigned char)*cursor != INFO_SEPARATOR_CHAR ) {
@TAB@@TAB@@TAB@@TAB@cursor++;
@TAB@@TAB@@TAB@}
@TAB@@TAB@}
@TAB@}

@TAB@return "";
}
#undef INFO_SEPARATOR_CHAR

/*
=============
CG_ConfigString

Returns the cached configstring for the requested index.
=============
*/
const char *CG_ConfigString( int index ) {
@TAB@if ( index == CS_MATCH_STATE ) {
@TAB@@TAB@return qlr_matchStateConfig;
@TAB@}

@TAB@return "";
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
@TAB@memset( &cgs, 0, sizeof( cgs ) );
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

/*
=============
QLR_ParseClientMatchState

Invokes the cgame parser to refresh cached match-state fields.
=============
*/
void QLR_ParseClientMatchState( void ) {
@TAB@CG_ParseMatchState();
}

/*
=============
QLR_GetClientTimeoutLength

Exposes the parsed timeout length in seconds for verification.
=============
*/
int QLR_GetClientTimeoutLength( void ) {
@TAB@return cgs.matchTimeoutLengthSeconds;
}

/*
=============
QLR_GetClientTimeoutCount

Exposes the parsed per-team timeout count for verification.
=============
*/
int QLR_GetClientTimeoutCount( void ) {
@TAB@return cgs.matchTimeoutCountPerTeam;
}

/*
=============
QLR_GetClientOvertimeLength

Returns the parsed overtime window duration.
=============
*/
int QLR_GetClientOvertimeLength( void ) {
@TAB@return cgs.matchOvertimeLengthSeconds;
}

/*
=============
QLR_GetClientSuddenDeathRespawns

Indicates whether sudden-death respawns are enabled.
=============
*/
int QLR_GetClientSuddenDeathRespawns( void ) {
@TAB@return cgs.matchSuddenDeathRespawnsEnabled ? 1 : 0;
}

/*
=============
QLR_GetClientSuddenDeathStart

Returns the parsed sudden-death start offset.
=============
*/
int QLR_GetClientSuddenDeathStart( void ) {
@TAB@return cgs.matchSuddenDeathStartSeconds;
}

/*
=============
QLR_GetClientSuddenDeathTick

Returns the parsed sudden-death tick interval.
=============
*/
int QLR_GetClientSuddenDeathTick( void ) {
@TAB@return cgs.matchSuddenDeathTickSeconds;
}

/*
=============
QLR_GetClientSuddenDeathMax

Returns the parsed sudden-death maximum duration.
=============
*/
int QLR_GetClientSuddenDeathMax( void ) {
@TAB@return cgs.matchSuddenDeathMaxSeconds;
}

/*
=============
QLR_GetClientSuddenDeathIncrement

Returns the parsed sudden-death increment duration.
=============
*/
int QLR_GetClientSuddenDeathIncrement( void ) {
@TAB@return cgs.matchSuddenDeathIncrementSeconds;
}

/*
=============
QLR_GetClientSuddenDeathPrint

Indicates whether sudden-death announcements are enabled.
=============
*/
int QLR_GetClientSuddenDeathPrint( void ) {
@TAB@return cgs.matchSuddenDeathPrintAnnouncements ? 1 : 0;
}

/*
=============
QLR_GetClientSuddenDeathDelay

Indicates whether sudden-death spawn delay is active.
=============
*/
int QLR_GetClientSuddenDeathDelay( void ) {
@TAB@return cgs.matchSuddenDeathSpawnDelayActive ? 1 : 0;
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
            "-I",
            str(CODE_DIR / "cgame"),
            "-I",
            str(CODE_DIR / "renderer"),
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
            "-I",
            str(CODE_DIR / "cgame"),
            "-I",
            str(CODE_DIR / "renderer"),
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
    library.QLR_ParseClientMatchState.argtypes = []
    library.QLR_ParseClientMatchState.restype = None
    library.QLR_GetClientTimeoutLength.argtypes = []
    library.QLR_GetClientTimeoutLength.restype = ctypes.c_int
    library.QLR_GetClientTimeoutCount.argtypes = []
    library.QLR_GetClientTimeoutCount.restype = ctypes.c_int
    library.QLR_GetClientOvertimeLength.argtypes = []
    library.QLR_GetClientOvertimeLength.restype = ctypes.c_int
    library.QLR_GetClientSuddenDeathRespawns.argtypes = []
    library.QLR_GetClientSuddenDeathRespawns.restype = ctypes.c_int
    library.QLR_GetClientSuddenDeathStart.argtypes = []
    library.QLR_GetClientSuddenDeathStart.restype = ctypes.c_int
    library.QLR_GetClientSuddenDeathTick.argtypes = []
    library.QLR_GetClientSuddenDeathTick.restype = ctypes.c_int
    library.QLR_GetClientSuddenDeathMax.argtypes = []
    library.QLR_GetClientSuddenDeathMax.restype = ctypes.c_int
    library.QLR_GetClientSuddenDeathIncrement.argtypes = []
    library.QLR_GetClientSuddenDeathIncrement.restype = ctypes.c_int
    library.QLR_GetClientSuddenDeathPrint.argtypes = []
    library.QLR_GetClientSuddenDeathPrint.restype = ctypes.c_int
    library.QLR_GetClientSuddenDeathDelay.argtypes = []
    library.QLR_GetClientSuddenDeathDelay.restype = ctypes.c_int
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

    library.QLR_ParseClientMatchState()
    assert library.QLR_GetClientTimeoutLength() == 75
    assert library.QLR_GetClientTimeoutCount() == 2
    assert library.QLR_GetClientOvertimeLength() == 120
    assert library.QLR_GetClientSuddenDeathRespawns() == 1
    assert library.QLR_GetClientSuddenDeathStart() == 15
    assert library.QLR_GetClientSuddenDeathTick() == 5
    assert library.QLR_GetClientSuddenDeathMax() == 60
    assert library.QLR_GetClientSuddenDeathIncrement() == 3
    assert library.QLR_GetClientSuddenDeathPrint() == 1
    assert library.QLR_GetClientSuddenDeathDelay() == 1
