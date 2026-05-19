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
#include "code/game/g_local.h"
#include "game/g_match_config.h"
#include "game/match_state_keys.h"

#define DEFAULT_TIMEOUT_LENGTH_SECONDS                  60
#define DEFAULT_TIMEOUT_COUNT_PER_TEAM                  0
#define DEFAULT_OVERTIME_LENGTH_SECONDS         120
#define DEFAULT_SUDDEN_DEATH_RESPAWN                    0
#define DEFAULT_SUDDEN_DEATH_START_SECONDS              3
#define DEFAULT_SUDDEN_DEATH_TICK_SECONDS               60
#define DEFAULT_SUDDEN_DEATH_MAX_SECONDS                10
#define DEFAULT_SUDDEN_DEATH_INCREMENT_SECONDS  1
#define DEFAULT_SUDDEN_DEATH_PRINT                      1
#define DEFAULT_FACTORY_RESPAWN_DELAY_MILLISECONDS              0
#define DEFAULT_FACTORY_WARMUP_DELAY_MILLISECONDS       0
#define DEFAULT_FACTORY_ALLOW_ITEM_DROPS                1
#define DEFAULT_FACTORY_ALLOW_ITEM_BOUNCE               1

level_locals_t level;
vmCvar_t g_gametype;

team_t TeamCount( int ignoreClientNum, int team ) {
	return 0;
}

int G_AutoShuffleCountdown_GetSecondsRemaining( void ) {
	return 0;
}

int Team_GetRespawnRatioForTeam( team_t team ) {
	return 0;
}

qboolean Team_IsAutoShuffleArmed( void ) {
	return 0;
}

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

static char qlr_matchStateConfig[MAX_INFO_STRING];
static int qlr_matchStateConfigUpdates;
static char qlr_suddenDeathStatusConfig[32];
static char qlr_roundStartConfig[32];
static char qlr_timeoutStartConfig[32];
static char qlr_timeoutExpireConfig[32];
static char qlr_timeoutCountRedConfig[32];
static char qlr_timeoutCountBlueConfig[32];
static char qlr_factoryFlagsConfig[32];
static char qlr_factorySpawnHintsConfig[MAX_INFO_STRING];

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
G_Printf

Routes server log messages to stdout for harness visibility.
=============
*/
void QDECL G_Printf( const char *fmt, ... ) {
@TAB@va_list args;

@TAB@if ( !fmt ) {
@TAB@@TAB@return;
@TAB@}

@TAB@va_start( args, fmt );
@TAB@vfprintf( stdout, fmt, args );
@TAB@va_end( args );
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
@TAB@switch ( num ) {
@TAB@case CS_MATCH_STATE:
@TAB@@TAB@qlr_matchStateConfigUpdates++;
@TAB@@TAB@Q_strncpyz( qlr_matchStateConfig, value, sizeof( qlr_matchStateConfig ) );
@TAB@@TAB@break;
@TAB@case CS_SUDDENDEATH_STATUS:
@TAB@@TAB@Q_strncpyz( qlr_suddenDeathStatusConfig, value, sizeof( qlr_suddenDeathStatusConfig ) );
@TAB@@TAB@break;
@TAB@case CS_ROUND_START_TIME:
@TAB@@TAB@Q_strncpyz( qlr_roundStartConfig, value, sizeof( qlr_roundStartConfig ) );
@TAB@@TAB@break;
@TAB@case CS_TIMEOUT_START_TIME:
@TAB@@TAB@Q_strncpyz( qlr_timeoutStartConfig, value, sizeof( qlr_timeoutStartConfig ) );
@TAB@@TAB@break;
@TAB@case CS_TIMEOUT_EXPIRE_TIME:
@TAB@@TAB@Q_strncpyz( qlr_timeoutExpireConfig, value, sizeof( qlr_timeoutExpireConfig ) );
@TAB@@TAB@break;
@TAB@case CS_TIMEOUT_COUNT_RED:
@TAB@@TAB@Q_strncpyz( qlr_timeoutCountRedConfig, value, sizeof( qlr_timeoutCountRedConfig ) );
@TAB@@TAB@break;
@TAB@case CS_TIMEOUT_COUNT_BLUE:
@TAB@@TAB@Q_strncpyz( qlr_timeoutCountBlueConfig, value, sizeof( qlr_timeoutCountBlueConfig ) );
@TAB@@TAB@break;
@TAB@case CS_FACTORY_FLAGS:
@TAB@@TAB@Q_strncpyz( qlr_factoryFlagsConfig, value, sizeof( qlr_factoryFlagsConfig ) );
@TAB@@TAB@break;
@TAB@case CS_SPAWN_HINTS:
@TAB@@TAB@Q_strncpyz( qlr_factorySpawnHintsConfig, value, sizeof( qlr_factorySpawnHintsConfig ) );
@TAB@@TAB@break;
@TAB@default:
@TAB@@TAB@break;
@TAB@}
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
@TAB@qlr_matchStateConfigUpdates = 0;
@TAB@memset( qlr_suddenDeathStatusConfig, 0, sizeof( qlr_suddenDeathStatusConfig ) );
@TAB@memset( qlr_roundStartConfig, 0, sizeof( qlr_roundStartConfig ) );
@TAB@memset( qlr_timeoutStartConfig, 0, sizeof( qlr_timeoutStartConfig ) );
@TAB@memset( qlr_timeoutExpireConfig, 0, sizeof( qlr_timeoutExpireConfig ) );
@TAB@memset( qlr_timeoutCountRedConfig, 0, sizeof( qlr_timeoutCountRedConfig ) );
@TAB@memset( qlr_timeoutCountBlueConfig, 0, sizeof( qlr_timeoutCountBlueConfig ) );
@TAB@memset( qlr_factoryFlagsConfig, 0, sizeof( qlr_factoryFlagsConfig ) );
@TAB@memset( qlr_factorySpawnHintsConfig, 0, sizeof( qlr_factorySpawnHintsConfig ) );
}

static void QLR_SetVmCvarInt( vmCvar_t *cvar, int value );
static void QLR_SetVmCvarString( vmCvar_t *cvar, const char *value );
void QLR_SetFactoryCvarsDefaults( void );
void QLR_SetFactoryCvarsCustom( void );

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
@TAB@QLR_SetFactoryCvarsDefaults();
}

/*
=============
QLR_SetVmCvarInt

Assigns the integer and string representations of a vmCvar_t.
=============
*/
static void QLR_SetVmCvarInt( vmCvar_t *cvar, int value ) {
@TAB@if ( !cvar ) {
@TAB@@TAB@return;
@TAB@}

@TAB@cvar->integer = value;
@TAB@cvar->value = (float)value;
@TAB@Com_sprintf( cvar->string, sizeof( cvar->string ), "%i", value );
}

/*
=============
QLR_SetVmCvarString

Copies the provided string into a vmCvar_t buffer.
=============
*/
static void QLR_SetVmCvarString( vmCvar_t *cvar, const char *value ) {
@TAB@if ( !cvar ) {
@TAB@@TAB@return;
@TAB@}

@TAB@if ( !value ) {
@TAB@@TAB@value = "";
@TAB@}

@TAB@Q_strncpyz( cvar->string, value, sizeof( cvar->string ) );
@TAB@cvar->integer = atoi( cvar->string );
@TAB@cvar->value = (float)cvar->integer;
}

/*
=============
QLR_SetFactoryCvarsDefaults

Seeds the factory cvars with stock values prior to loading configs.
=============
*/
void QLR_SetFactoryCvarsDefaults( void ) {
@TAB@QLR_SetVmCvarString( &g_factoryTitle, "" );
@TAB@QLR_SetVmCvarInt( &g_timeoutLen, DEFAULT_TIMEOUT_LENGTH_SECONDS );
@TAB@QLR_SetVmCvarInt( &g_timeoutCount, DEFAULT_TIMEOUT_COUNT_PER_TEAM );
@TAB@QLR_SetVmCvarInt( &g_overtime, DEFAULT_OVERTIME_LENGTH_SECONDS );
@TAB@QLR_SetVmCvarInt( &g_suddenDeathRespawn, DEFAULT_SUDDEN_DEATH_RESPAWN );
@TAB@QLR_SetVmCvarInt( &g_suddenDeathRespawnStart, DEFAULT_SUDDEN_DEATH_START_SECONDS );
@TAB@QLR_SetVmCvarInt( &g_suddenDeathRespawnTick, DEFAULT_SUDDEN_DEATH_TICK_SECONDS );
@TAB@QLR_SetVmCvarInt( &g_suddenDeathRespawnMax, DEFAULT_SUDDEN_DEATH_MAX_SECONDS );
@TAB@QLR_SetVmCvarInt( &g_suddenDeathRespawnIncrement, DEFAULT_SUDDEN_DEATH_INCREMENT_SECONDS );
@TAB@QLR_SetVmCvarInt( &g_suddenDeathRespawnPrint, DEFAULT_SUDDEN_DEATH_PRINT );
@TAB@QLR_SetVmCvarInt( &g_factoryRespawnDelay, DEFAULT_FACTORY_RESPAWN_DELAY_MILLISECONDS );
@TAB@QLR_SetVmCvarInt( &g_factoryWarmupSpawnDelay, DEFAULT_FACTORY_WARMUP_DELAY_MILLISECONDS );
@TAB@QLR_SetVmCvarInt( &g_factoryAllowItemDrops, DEFAULT_FACTORY_ALLOW_ITEM_DROPS );
@TAB@QLR_SetVmCvarInt( &g_factoryAllowItemBounce, DEFAULT_FACTORY_ALLOW_ITEM_BOUNCE );
}

/*
=============
QLR_SetFactoryCvarsCustom

Applies a custom factory profile for mid-match updates.
=============
*/
void QLR_SetFactoryCvarsCustom( void ) {
@TAB@QLR_SetVmCvarString( &g_factoryTitle, "" );
@TAB@QLR_SetVmCvarInt( &g_timeoutLen, 75 );
@TAB@QLR_SetVmCvarInt( &g_timeoutCount, 2 );
@TAB@QLR_SetVmCvarInt( &g_overtime, 210 );
@TAB@QLR_SetVmCvarInt( &g_suddenDeathRespawn, 1 );
@TAB@QLR_SetVmCvarInt( &g_suddenDeathRespawnStart, 20 );
@TAB@QLR_SetVmCvarInt( &g_suddenDeathRespawnTick, 15 );
@TAB@QLR_SetVmCvarInt( &g_suddenDeathRespawnMax, 90 );
@TAB@QLR_SetVmCvarInt( &g_suddenDeathRespawnIncrement, 4 );
@TAB@QLR_SetVmCvarInt( &g_suddenDeathRespawnPrint, 0 );
@TAB@QLR_SetVmCvarInt( &g_factoryRespawnDelay, 2000 );
@TAB@QLR_SetVmCvarInt( &g_factoryWarmupSpawnDelay, 500 );
@TAB@QLR_SetVmCvarInt( &g_factoryAllowItemDrops, 0 );
@TAB@QLR_SetVmCvarInt( &g_factoryAllowItemBounce, 0 );
}

/*
=============
QLR_InitMatchFactoryConfigHarness

Initialises the match factory cache using the harness cvars.
=============
*/
void QLR_InitMatchFactoryConfigHarness( void ) {
@TAB@G_InitMatchFactoryConfig();
}

/*
=============
QLR_UpdateMatchFactoryConfigHarness

Propagates cvar changes through G_UpdateMatchFactoryConfig.
=============
*/
void QLR_UpdateMatchFactoryConfigHarness( void ) {
@TAB@G_UpdateMatchFactoryConfig();
}

/*
=============
QLR_GetMatchStateConfigUpdateCount

Exposes how many times the match-state configstring changed.
=============
*/
int QLR_GetMatchStateConfigUpdateCount( void ) {
@TAB@return qlr_matchStateConfigUpdates;
}

/*
=============
QLR_SeedMatchStateValues

Initialises representative round, overtime, and timeout state.
=============
*/
static void QLR_SeedMatchStateValues( void ) {
@TAB@level.roundStartTime = 222000;
@TAB@level.roundTransitionTime = 222222;
@TAB@level.roundNumber = 9;
@TAB@level.roundState = ROUNDSTATE_ACTIVE;
@TAB@level.overtimeActive = qtrue;
@TAB@level.overtimeStartTime = 111111;
@TAB@level.overtimeEndTime = 222333;
@TAB@level.overtimeCount = 3;
@TAB@level.timeoutActive = qtrue;
@TAB@level.timeoutStartTime = 333000;
@TAB@level.timeoutTeam = TEAM_BLUE;
@TAB@level.timeoutExpireTime = 333444;
@TAB@level.timeoutOwner = 7;
@TAB@level.timeoutRemaining[TEAM_RED] = 2;
@TAB@level.timeoutRemaining[TEAM_BLUE] = 1;
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
QLR_BuildSuddenDeathStatusConfigstring

Publishes the mirrored sudden-death configstring for the requested active state.
=============
*/
void QLR_BuildSuddenDeathStatusConfigstring( int active ) {
@TAB@level.suddenDeathActive = active ? qtrue : qfalse;
@TAB@G_UpdateMatchStateConfigString();
}

/*
=============
QLR_GetSuddenDeathStatusConfigstring

Exposes the captured sudden-death configstring to the Python harness.
=============
*/
const char *QLR_GetSuddenDeathStatusConfigstring( void ) {
@TAB@return qlr_suddenDeathStatusConfig;
}

/*
=============
QLR_GetRoundStartConfigstring

Exposes the captured round-start configstring for assertions.
=============
*/
const char *QLR_GetRoundStartConfigstring( void ) {
@TAB@return qlr_roundStartConfig;
}

/*
=============
QLR_GetTimeoutStartConfigstring

Exposes the captured timeout-start configstring for assertions.
=============
*/
const char *QLR_GetTimeoutStartConfigstring( void ) {
@TAB@return qlr_timeoutStartConfig;
}

/*
=============
QLR_GetTimeoutExpireConfigstring

Exposes the captured timeout-expire configstring for assertions.
=============
*/
const char *QLR_GetTimeoutExpireConfigstring( void ) {
@TAB@return qlr_timeoutExpireConfig;
}

/*
=============
QLR_GetTimeoutCountRedConfigstring

Exposes the captured red timeout-count configstring for assertions.
=============
*/
const char *QLR_GetTimeoutCountRedConfigstring( void ) {
@TAB@return qlr_timeoutCountRedConfig;
}

/*
=============
QLR_GetTimeoutCountBlueConfigstring

Exposes the captured blue timeout-count configstring for assertions.
=============
*/
const char *QLR_GetTimeoutCountBlueConfigstring( void ) {
@TAB@return qlr_timeoutCountBlueConfig;
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
            str(CODE_DIR / "game" / "g_match_state.c"),
            str(SRC_DIR / "game" / "g_match_config.c"),
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
            str(CODE_DIR / "game" / "g_match_state.c"),
            str(SRC_DIR / "game" / "g_match_config.c"),
        ]

    subprocess.run(compile_cmd, check=True)
    return lib_path


def _load_match_state_library(lib_path: Path) -> ctypes.CDLL:
    library = ctypes.CDLL(str(lib_path))
    library.QLR_ResetMatchState.argtypes = []
    library.QLR_ResetMatchState.restype = None
    library.QLR_BuildMatchStateConfigstring.argtypes = []
    library.QLR_BuildMatchStateConfigstring.restype = None
    library.QLR_BuildSuddenDeathStatusConfigstring.argtypes = [ctypes.c_int]
    library.QLR_BuildSuddenDeathStatusConfigstring.restype = None
    library.QLR_GetMatchStateConfigstring.argtypes = []
    library.QLR_GetMatchStateConfigstring.restype = ctypes.c_char_p
    library.QLR_GetSuddenDeathStatusConfigstring.argtypes = []
    library.QLR_GetSuddenDeathStatusConfigstring.restype = ctypes.c_char_p
    library.QLR_GetRoundStartConfigstring.argtypes = []
    library.QLR_GetRoundStartConfigstring.restype = ctypes.c_char_p
    library.QLR_GetTimeoutStartConfigstring.argtypes = []
    library.QLR_GetTimeoutStartConfigstring.restype = ctypes.c_char_p
    library.QLR_GetTimeoutExpireConfigstring.argtypes = []
    library.QLR_GetTimeoutExpireConfigstring.restype = ctypes.c_char_p
    library.QLR_GetTimeoutCountRedConfigstring.argtypes = []
    library.QLR_GetTimeoutCountRedConfigstring.restype = ctypes.c_char_p
    library.QLR_GetTimeoutCountBlueConfigstring.argtypes = []
    library.QLR_GetTimeoutCountBlueConfigstring.restype = ctypes.c_char_p
    library.QLR_ResetClientMatchState.argtypes = []
    library.QLR_ResetClientMatchState.restype = None
    library.QLR_ParseMatchStateOnClient.argtypes = []
    library.QLR_ParseMatchStateOnClient.restype = None
    library.QLR_SetFactoryCvarsDefaults.argtypes = []
    library.QLR_SetFactoryCvarsDefaults.restype = None
    library.QLR_SetFactoryCvarsCustom.argtypes = []
    library.QLR_SetFactoryCvarsCustom.restype = None
    library.QLR_InitMatchFactoryConfigHarness.argtypes = []
    library.QLR_InitMatchFactoryConfigHarness.restype = None
    library.QLR_UpdateMatchFactoryConfigHarness.argtypes = []
    library.QLR_UpdateMatchFactoryConfigHarness.restype = None
    library.QLR_GetMatchStateConfigUpdateCount.argtypes = []
    library.QLR_GetMatchStateConfigUpdateCount.restype = ctypes.c_int
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
        "toRed": "2",
        "toBlue": "1",
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
def test_timeout_auxiliary_configstrings_publish_retail_values(match_state_library: ctypes.CDLL) -> None:
    library = match_state_library
    library.QLR_ResetMatchState()
    library.QLR_BuildMatchStateConfigstring()

    assert library.QLR_GetRoundStartConfigstring().decode("utf-8") == "222000"
    assert library.QLR_GetTimeoutStartConfigstring().decode("utf-8") == "333000"
    assert library.QLR_GetTimeoutExpireConfigstring().decode("utf-8") == "333444"
    assert library.QLR_GetTimeoutCountRedConfigstring().decode("utf-8") == "2"
    assert library.QLR_GetTimeoutCountBlueConfigstring().decode("utf-8") == "1"


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


@pytest.mark.skipif(os.name == "nt", reason="Match-state harness requires a POSIX toolchain")
def test_match_state_configstring_mirrors_sudden_death_flag(match_state_library: ctypes.CDLL) -> None:
    library = match_state_library
    library.QLR_ResetMatchState()

    library.QLR_BuildSuddenDeathStatusConfigstring(1)
    active = library.QLR_GetSuddenDeathStatusConfigstring()
    assert active is not None
    assert active.decode("utf-8") == "1"

    library.QLR_BuildSuddenDeathStatusConfigstring(0)
    inactive = library.QLR_GetSuddenDeathStatusConfigstring()
    assert inactive is not None
    assert inactive.decode("utf-8") == "0"


@pytest.mark.skipif(os.name == "nt", reason="Match-state harness requires a POSIX toolchain")
def test_match_factory_updates_refresh_match_state_configstring(match_state_library: ctypes.CDLL) -> None:
    library = match_state_library
    library.QLR_ResetMatchState()
    library.QLR_ResetClientMatchState()
    library.QLR_SetFactoryCvarsDefaults()
    library.QLR_InitMatchFactoryConfigHarness()

    assert library.QLR_GetMatchStateConfigUpdateCount() == 0

    library.QLR_UpdateMatchFactoryConfigHarness()
    assert library.QLR_GetMatchStateConfigUpdateCount() == 0

    library.QLR_SetFactoryCvarsCustom()
    library.QLR_UpdateMatchFactoryConfigHarness()
    assert library.QLR_GetMatchStateConfigUpdateCount() == 1

    library.QLR_ResetClientMatchState()
    library.QLR_ParseMatchStateOnClient()

    assert library.QLR_GetClientTimeoutLengthSeconds() == 75
    assert library.QLR_GetClientTimeoutCountPerTeam() == 2
    assert library.QLR_GetClientOvertimeLengthSeconds() == 210
    assert library.QLR_GetClientSuddenDeathRespawnsEnabled() == 1
    assert library.QLR_GetClientSuddenDeathStartSeconds() == 20
    assert library.QLR_GetClientSuddenDeathTickSeconds() == 15
    assert library.QLR_GetClientSuddenDeathMaxSeconds() == 90
    assert library.QLR_GetClientSuddenDeathIncrementSeconds() == 4
    assert library.QLR_GetClientSuddenDeathPrintAnnouncements() == 0
    assert library.QLR_GetClientSuddenDeathSpawnDelayActive() == 1


def test_cgame_match_flow_configstrings_are_wired() -> None:
    servercmds = (CODE_DIR / "cgame" / "cg_servercmds.c").read_text(encoding="utf-8")

    assert "CG_ParseSuddenDeathStatus();" in servercmds
    assert "CG_ParseReadyUpStatus();" in servercmds
    assert "CG_ParseWarmupReadyStatus();" in servercmds
    assert "num == CS_SUDDENDEATH_STATUS" in servercmds
    assert "num == CS_READYUP_STATUS" in servercmds
    assert "num == CS_WARMUP_READY" in servercmds


def test_client_hud_uses_runtime_sudden_death_and_retail_warmup_prompts() -> None:
    draw = (CODE_DIR / "cgame" / "cg_draw.c").read_text(encoding="utf-8")
    scoreboard = (CODE_DIR / "cgame" / "cg_scoreboard.c").read_text(encoding="utf-8")
    match_state = (CODE_DIR / "game" / "g_match_state.c").read_text(encoding="utf-8")

    assert "CG_BuildWarmupWaitingStatus" in draw
    assert '"The match requires %i player%s per team."' in draw
    assert '"Press %s to unready yourself"' in draw
    assert "cgs.matchReadyUpDeadline" in draw
    assert 'title = cgs.matchSuddenDeathActive ? "Sudden Death" : "Round Begins in";' in draw
    assert "cgHudScoreboard.suddenDeathActive = cgs.matchSuddenDeathActive;" in scoreboard
    assert 'trap_SetConfigstring( CS_SUDDENDEATH_STATUS, level.suddenDeathActive ? "1" : "0" );' in match_state
