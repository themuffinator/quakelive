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

static int s_lastTeamCountConfigstringUpdateTime;

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
G_ClanArenaWarmupRoundNumber

Returns the retail Clan Arena round number published before the active phase.
=============
*/
static int G_ClanArenaWarmupRoundNumber( void ) {
	int	round;

	round = level.teamScores[TEAM_RED] + level.teamScores[TEAM_BLUE] + 1;
	if ( round < 1 ) {
		round = 1;
	}

	return round;
}

/*
=============
G_BuildClanArenaMatchStateInfo

Builds the compact retail Clan Arena configstring 0x295 payload.
=============
*/
static qboolean G_BuildClanArenaMatchStateInfo( char *info ) {
	if ( !info || g_gametype.integer != GT_CLAN_ARENA ) {
		return qfalse;
	}

	info[0] = '\0';
	switch ( level.roundState ) {
	case ROUNDSTATE_INACTIVE:
		Q_strncpyz( info, "\\time\\-1\\round\\0", MAX_INFO_STRING );
		break;

	case ROUNDSTATE_WARMUP:
		G_SetMatchStateInt( info, MATCH_STATE_KEY_TIME, level.warmupTime );
		G_SetMatchStateInt( info, MATCH_STATE_KEY_ROUND, G_ClanArenaWarmupRoundNumber() );
		break;

	case ROUNDSTATE_ACTIVE:
	case ROUNDSTATE_COMPLETE:
		G_SetMatchStateInt( info, MATCH_STATE_KEY_ROUND, level.roundNumber );
		break;

	default:
		return qfalse;
	}

	return qtrue;
}

/*
=============
G_AttackDefendPublishedTurn

Returns the A/D turn that retail leaves visible while a completed turn resolves.
=============
*/
static int G_AttackDefendPublishedTurn( void ) {
	if ( level.adRoundState == AD_ROUNDSTATE_COMPLETE || level.adRoundState == AD_ROUNDSTATE_EXIT ) {
		return level.adTurnIndex ^ 1;
	}

	return level.adTurnIndex;
}

/*
=============
G_BuildAttackDefendMatchStateInfo

Builds the compact retail Attack and Defend configstring 0x295 payload.
=============
*/
static qboolean G_BuildAttackDefendMatchStateInfo( char *info ) {
	if ( !info || g_gametype.integer != GT_ATTACK_DEFEND ) {
		return qfalse;
	}

	info[0] = '\0';
	switch ( level.adRoundState ) {
	case AD_ROUNDSTATE_INACTIVE:
		Q_strncpyz( info, "\\time\\-1\\round\\0\\turn\\0\\state\\0", MAX_INFO_STRING );
		break;

	case AD_ROUNDSTATE_WARMUP:
		G_SetMatchStateInt( info, MATCH_STATE_KEY_TIME, level.roundTransitionTime );
		G_SetMatchStateInt( info, MATCH_STATE_KEY_ROUND, level.roundNumber );
		G_SetMatchStateInt( info, MATCH_STATE_KEY_TURN, level.adTurnIndex );
		G_SetMatchStateInt( info, MATCH_STATE_KEY_STATE, ROUNDSTATE_WARMUP );
		break;

	case AD_ROUNDSTATE_ACTIVE:
		G_SetMatchStateInt( info, MATCH_STATE_KEY_TURN, level.adTurnIndex );
		G_SetMatchStateInt( info, MATCH_STATE_KEY_STATE, ROUNDSTATE_ACTIVE );
		break;

	case AD_ROUNDSTATE_COMPLETE:
	case AD_ROUNDSTATE_EXIT:
		G_SetMatchStateInt( info, MATCH_STATE_KEY_TURN, G_AttackDefendPublishedTurn() );
		G_SetMatchStateInt( info, MATCH_STATE_KEY_STATE, ROUNDSTATE_ACTIVE );
		break;

	default:
		return qfalse;
	}

	return qtrue;
}

/*
=============
G_RedRoverPublishedRoundNumber

Returns the retail Red Rover round number cached for active rounds or derived
from team scores during pre-active controller states.
=============
*/
static int G_RedRoverPublishedRoundNumber( void ) {
	int	round;

	round = level.roundNumber;
	if ( round < 1 ) {
		round = level.teamScores[TEAM_RED] + level.teamScores[TEAM_BLUE] + 1;
	}
	if ( round < 1 ) {
		round = 1;
	}

	return round;
}

/*
=============
G_BuildRedRoverMatchStateInfo

Builds the compact retail Red Rover configstring 0x295 payload.
=============
*/
static qboolean G_BuildRedRoverMatchStateInfo( char *info ) {
	if ( !info || g_gametype.integer != GT_RED_ROVER ) {
		return qfalse;
	}

	info[0] = '\0';
	switch ( level.rrRoundState ) {
	case RR_ROUNDSTATE_INACTIVE:
		Q_strncpyz( info, "\\time\\-1\\round\\0", MAX_INFO_STRING );
		break;

	case RR_ROUNDSTATE_WARMUP:
	case RR_ROUNDSTATE_INFECTION_SEED:
		G_SetMatchStateInt( info, MATCH_STATE_KEY_TIME, level.roundTransitionTime );
		G_SetMatchStateInt( info, MATCH_STATE_KEY_ROUND, G_RedRoverPublishedRoundNumber() );
		break;

	case RR_ROUNDSTATE_ACTIVE:
	case RR_ROUNDSTATE_COMPLETE:
	case RR_ROUNDSTATE_EXIT:
		G_SetMatchStateInt( info, MATCH_STATE_KEY_ROUND, G_RedRoverPublishedRoundNumber() );
		break;

	default:
		return qfalse;
	}

	return qtrue;
}

/*
=============
G_BuildPublishedTimeoutCounts

Builds the retail timeout-count payload for match-state and auxiliary configstrings.
=============
*/
static void G_BuildPublishedTimeoutCounts( int *redOut, int *blueOut ) {
	int	red;
	int	blue;
	int	duel;

	if ( !redOut || !blueOut ) {
		return;
	}

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

	*redOut = red;
	*blueOut = blue;
}

/*
=============
G_UsesRoundControllerTeamCounts

Returns qtrue when retail publishes live PM_NORMAL team counts instead of raw rosters.
=============
*/
static qboolean G_UsesRoundControllerTeamCounts( void ) {
	switch ( g_gametype.integer ) {
	case GT_CLAN_ARENA:
	case GT_ATTACK_DEFEND:
	case GT_FREEZE:
	case GT_RED_ROVER:
		return ( level.roundState != ROUNDSTATE_INACTIVE ) ? qtrue : qfalse;
	default:
		return qfalse;
	}
}

/*
=============
G_BuildPublishedTeamCounts

Builds the retail-facing team-count payload for HUD and match-state publishers.
=============
*/
static void G_BuildPublishedTeamCounts( int counts[TEAM_NUM_TEAMS] ) {
	if ( !counts ) {
		return;
	}

	if ( g_gametype.integer < GT_TEAM ) {
		memset( counts, 0, sizeof( int ) * TEAM_NUM_TEAMS );
		return;
	}

	if ( G_UsesRoundControllerTeamCounts() ) {
		G_CountActivePlayersByTeam( counts );
		return;
	}

	G_CountConnectedClientsByTeam( counts );
}

/*
=============
G_UpdateTeamCountConfigstrings

Refreshes the auxiliary retail team-count configstrings on the observed 250 ms cadence.
=============
*/
void G_UpdateTeamCountConfigstrings( void ) {
	int counts[TEAM_NUM_TEAMS];

	if ( level.time > s_lastTeamCountConfigstringUpdateTime && level.time - s_lastTeamCountConfigstringUpdateTime <= 250 ) {
		return;
	}

	s_lastTeamCountConfigstringUpdateTime = level.time;
	G_BuildPublishedTeamCounts( counts );
	trap_SetConfigstring( CS_TEAM_COUNT_RED, va( "%i", counts[TEAM_RED] ) );
	trap_SetConfigstring( CS_TEAM_COUNT_BLUE, va( "%i", counts[TEAM_BLUE] ) );
}

/*
=============
G_UpdateTimeoutConfigStrings

Publishes the retail timeout auxiliary configstrings alongside CS_MATCH_STATE.
=============
*/
void G_UpdateTimeoutConfigStrings( void ) {
	int	red;
	int	blue;

	G_BuildPublishedTimeoutCounts( &red, &blue );

	trap_SetConfigstring( CS_TIMEOUT_COUNT_RED, va( "%i", red ) );
	trap_SetConfigstring( CS_TIMEOUT_COUNT_BLUE, va( "%i", blue ) );
	trap_SetConfigstring( CS_TIMEOUT_EXPIRE_TIME, va( "%i", level.timeoutExpireTime ) );

	if ( level.timeoutStartTime > 0 ) {
		trap_SetConfigstring( CS_TIMEOUT_START_TIME, va( "%i", level.timeoutStartTime ) );
	} else {
		trap_SetConfigstring( CS_TIMEOUT_START_TIME, "" );
	}
}

/*
=============
G_UpdateRoundStartConfigString

Publishes the hidden retail active-round timestamp used by CG_ROUNDTIMER.
=============
*/
static void G_UpdateRoundStartConfigString( void ) {
	if ( level.roundState == ROUNDSTATE_ACTIVE ) {
		trap_SetConfigstring( CS_ROUND_START_TIME, va( "%i", level.roundStartTime ) );
		return;
	}

	if ( g_gametype.integer == GT_CLAN_ARENA && level.roundState == ROUNDSTATE_COMPLETE ) {
		trap_SetConfigstring( CS_ROUND_START_TIME, va( "%i", -1 ) );
		return;
	}

	if ( g_gametype.integer == GT_ATTACK_DEFEND
		&& ( level.adRoundState == AD_ROUNDSTATE_COMPLETE || level.adRoundState == AD_ROUNDSTATE_EXIT ) ) {
		trap_SetConfigstring( CS_ROUND_START_TIME, va( "%i", -1 ) );
		return;
	}

	if ( g_gametype.integer == GT_RED_ROVER
		&& ( level.rrRoundState == RR_ROUNDSTATE_COMPLETE || level.rrRoundState == RR_ROUNDSTATE_EXIT ) ) {
		trap_SetConfigstring( CS_ROUND_START_TIME, va( "%i", -1 ) );
	}
}

/*
=============
G_UpdateSuddenDeathStatusConfigString

Publishes the dedicated retail sudden-death status latch alongside the
broader match-state payload.
=============
*/
static void G_UpdateSuddenDeathStatusConfigString( void ) {
	trap_SetConfigstring( CS_SUDDENDEATH_STATUS, level.suddenDeathActive ? "1" : "0" );
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
	int counts[TEAM_NUM_TEAMS];
	int red;
	int blue;
	int turn;

	info[0] = '\0';
	config = &g_matchFactoryConfig;

	G_BuildPublishedTimeoutCounts( &red, &blue );

	if ( g_gametype.integer == GT_ATTACK_DEFEND ) {
		turn = level.adTurnIndex;
	} else {
		turn = level.roundNumber & 1;
	}

	if ( !G_BuildClanArenaMatchStateInfo( info )
		&& !G_BuildAttackDefendMatchStateInfo( info )
		&& !G_BuildRedRoverMatchStateInfo( info ) ) {
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

		if ( g_gametype.integer >= GT_TEAM ) {
			G_BuildPublishedTeamCounts( counts );

			G_SetMatchStateInt( info, MATCH_STATE_KEY_TEAM_RED_COUNT, counts[TEAM_RED] );
			G_SetMatchStateInt( info, MATCH_STATE_KEY_TEAM_BLUE_COUNT, counts[TEAM_BLUE] );
			G_SetMatchStateInt( info, MATCH_STATE_KEY_RESPAWN_RED, Team_GetRespawnRatioForTeam( TEAM_RED ) );
			G_SetMatchStateInt( info, MATCH_STATE_KEY_RESPAWN_BLUE, Team_GetRespawnRatioForTeam( TEAM_BLUE ) );
			G_SetMatchStateInt( info, MATCH_STATE_KEY_SHUFFLE_ARMED, Team_IsAutoShuffleArmed() ? 1 : 0 );
			G_SetMatchStateInt( info, MATCH_STATE_KEY_SHUFFLE_REMAINING, G_AutoShuffleCountdown_GetSecondsRemaining() );
		}
	}

	G_UpdateRoundStartConfigString();
	G_UpdateSuddenDeathStatusConfigString();
	trap_SetConfigstring( CS_MATCH_STATE, info );
	G_UpdateTimeoutConfigStrings();
}
