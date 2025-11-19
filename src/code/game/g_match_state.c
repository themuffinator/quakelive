/*
============================================================================
Copyright (C) 1999-2005 Id Software, Inc.

This file is part of Quake III Arena source code.

Quake III Arena source code is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

Quake III Arena source code is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
============================================================================
*/

#include "g_local.h"
#include "g_match_config.h"
#include "../game/match_state_keys.h"

/*
=============
G_SetMatchStateInt

Formats an integer payload and appends it to the match state info string.
=============
*/
static void G_SetMatchStateInt( char *info, const char *key, int value ) {
char buffer[32];

if ( !info || !key ) {
return;
}

Com_sprintf( buffer, sizeof( buffer ), "%i", value );
Info_SetValueForKey( info, key, buffer );
}

/*
=============
G_SetMatchFactoryConfigFields

Appends the cached match factory configuration values to the match-state payload.
=============
*/
static void G_SetMatchFactoryConfigFields( char *info, const matchFactoryConfig_t *config ) {
if ( !info || !config ) {
return;
}

G_SetMatchStateInt( info, MATCH_STATE_KEY_TIMEOUT_LENGTH, config->timeoutLengthSeconds );
G_SetMatchStateInt( info, MATCH_STATE_KEY_TIMEOUT_COUNT, config->timeoutCountPerTeam );
G_SetMatchStateInt( info, MATCH_STATE_KEY_OVERTIME_LENGTH, config->overtimeLengthSeconds );
G_SetMatchStateInt( info, MATCH_STATE_KEY_SUDDEN_RESPAWNS, config->suddenDeathRespawnsEnabled ? 1 : 0 );
G_SetMatchStateInt( info, MATCH_STATE_KEY_SUDDEN_START, config->suddenDeathStartSeconds );
G_SetMatchStateInt( info, MATCH_STATE_KEY_SUDDEN_TICK, config->suddenDeathTickSeconds );
G_SetMatchStateInt( info, MATCH_STATE_KEY_SUDDEN_MAX, config->suddenDeathMaxSeconds );
G_SetMatchStateInt( info, MATCH_STATE_KEY_SUDDEN_INCREMENT, config->suddenDeathIncrementSeconds );
G_SetMatchStateInt( info, MATCH_STATE_KEY_SUDDEN_PRINT, config->suddenDeathPrintAnnouncements ? 1 : 0 );
G_SetMatchStateInt( info, MATCH_STATE_KEY_SUDDEN_DELAY, config->suddenDeathSpawnDelayActive ? 1 : 0 );
}

/*
=============
G_UpdateMatchStateConfigString

Builds the configstring payload describing round timers, overtime, and timeout state.
=============
*/
void G_UpdateMatchStateConfigString( void ) {
	char info[MAX_INFO_STRING];
	const matchFactoryConfig_t *config;
	int red;
	int blue;
	int duel;
	int turn;

	info[0] = '\0';
	config = &g_matchFactoryConfig;

	red = level.timeoutRemaining[TEAM_RED];
	blue = level.timeoutRemaining[TEAM_BLUE];
	if ( g_gametype.integer < GT_TEAM ) {
		duel = level.timeoutRemaining[TEAM_FREE];
		if ( duel < 0 ) {
			duel = 0;
		}
		red = duel;
		blue = duel;
	}

	if ( red < 0 ) {
		red = 0;
	}
	if ( blue < 0 ) {
		blue = 0;
	}

	turn = level.roundNumber & 1;

	G_SetMatchStateInt( info, MATCH_STATE_KEY_TIME, level.roundTransitionTime );
	G_SetMatchStateInt( info, MATCH_STATE_KEY_ROUND, level.roundNumber );
	G_SetMatchStateInt( info, MATCH_STATE_KEY_TURN, turn );
	G_SetMatchStateInt( info, MATCH_STATE_KEY_STATE, level.roundState );
	G_SetMatchStateInt( info, MATCH_STATE_KEY_OVERTIME_ACTIVE, level.overtimeActive ? 1 : 0 );
	G_SetMatchStateInt( info, MATCH_STATE_KEY_OVERTIME_START, level.overtimeStartTime );
	G_SetMatchStateInt( info, MATCH_STATE_KEY_OVERTIME_END, level.overtimeEndTime );
	G_SetMatchStateInt( info, MATCH_STATE_KEY_OVERTIME_COUNT, level.overtimeCount );
G_SetMatchStateInt( info, MATCH_STATE_KEY_TIMEOUT_ACTIVE, level.timeoutActive ? 1 : 0 );
G_SetMatchStateInt( info, MATCH_STATE_KEY_TIMEOUT_TEAM, level.timeoutTeam );
G_SetMatchStateInt( info, MATCH_STATE_KEY_TIMEOUT_EXPIRE, level.timeoutExpireTime );
G_SetMatchStateInt( info, MATCH_STATE_KEY_TIMEOUT_OWNER, level.timeoutOwner );
G_SetMatchStateInt( info, MATCH_STATE_KEY_TIMEOUT_RED, red );
G_SetMatchStateInt( info, MATCH_STATE_KEY_TIMEOUT_BLUE, blue );
G_SetMatchFactoryConfigFields( info, config );

trap_SetConfigstring( CS_MATCH_STATE, info );
}
