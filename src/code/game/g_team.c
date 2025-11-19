/*
===========================================================================
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
===========================================================================
*/
//

#include "g_local.h"
#include <stdlib.h>

#define DOMINATION_DISTRESS_REPEAT_TIME	2000
#define DOMINATION_MAX_POINT_SPAWNS	25

typedef struct dominationPoint_s {
	gentity_t	*pointEnt;
	gentity_t	*trigger;
	team_t	ownerTeam;
	team_t	capturingTeam;
	float	progress;
	int	redOccupants;
	int	blueOccupants;
	int	lastOccupancyFrame;
	int	lastDistressTime;
	qboolean	distressNotified;
	qboolean	neutralizing;
	char	label[DOMINATION_LABEL_MAX];
	char	targetName[MAX_QPATH];
	gentity_t	*spawnTargets[DOMINATION_MAX_POINT_SPAWNS];
	int	spawnTargetCount;
} dominationPoint_t;


typedef struct teamgame_s {
	float			last_flag_capture;
	int				last_capture_team;
	flagStatus_t	redStatus;	// CTF
	flagStatus_t	blueStatus;	// CTF
	flagStatus_t	flagStatus;	// One Flag CTF
	int				redTakenTime;
	int				blueTakenTime;
	int				redObeliskAttackedTime;
	int				blueObeliskAttackedTime;
	dominationPoint_t		dominationPoints[DOMINATION_MAX_POINTS];
	int				dominationPointCount;
	int				dominationNextScoreTime;
} teamgame_t;

teamgame_t teamgame;

gentity_t	*neutralObelisk;

typedef struct teamBalanceInfo_s {
	int		redCount;
	int		blueCount;
	int		totalCount;
} teamBalanceInfo_t;

void Team_SetFlagStatus( int team, flagStatus_t status );
static void Team_InitDominationState( void );
static void Team_InitDomination( void );
static dominationPoint_t *Team_DominationPointForTrigger( const gentity_t *ent );
static dominationPoint_t *Team_DominationPointForPointEnt( const gentity_t *ent );
static dominationPoint_t *Team_DominationPointForTargetName( const char *targetname );
static void Team_DominationBuildSpawnList( dominationPoint_t *point );
static void Team_DominationPointThink( gentity_t *ent );
static void Team_DominationEventOrigin( const dominationPoint_t *point, vec3_t origin );
static void Team_DominationUpdatePointState( dominationPoint_t *point, int captureTime );
static int Team_DominationCaptureTime( void );
static int Team_DominationScoreInterval( void );
static float Team_DominationCaptureMultiplier( int playerCount );
static void Team_DominationAnnounceCapture( dominationPoint_t *point, team_t previousOwner );
static void Team_DominationAnnounceNeutralized( dominationPoint_t *point, team_t attacker );
static void Team_DominationSendDistress( dominationPoint_t *point );
static void G_ClearDroppedFlagState( gentity_t *flag );
static void G_ApplyDroppedFlagMetadata( gentity_t *drop, qboolean tackleDrop, qboolean suicideDrop, const gentity_t *attacker );

/*
=============
SP_team_dom_point

Registers Domination control point metadata and links spawn targets.
=============
*/
void SP_team_dom_point( gentity_t *ent ) {
	if ( g_gametype.integer != GT_DOMINATION ) {
		G_FreeEntity( ent );
		return;
	}

	if ( !ent->targetname || !ent->targetname[0] ) {
		G_Printf( "SP_team_dom_point: missing targetname\n" );
		G_FreeEntity( ent );
		return;
	}

	Team_RegisterDominationPoint( ent );
}

/*
=============
G_ADBonusesEnabled

Returns qtrue when Attack & Defend score bonuses should be processed.
=============
*/
static qboolean G_ADBonusesEnabled( void ) {
	if ( g_gametype.integer != GT_ATTACK_DEFEND ) {
		return qfalse;
	}

	if ( level.warmupTime ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
G_ADAnnounceBonus

Broadcasts the configured centerprint messaging for Attack & Defend bonuses.
=============
*/
static void G_ADAnnounceBonus( gentity_t *player, const char *label, int bonus ) {
	char		command[MAX_STRING_CHARS];

	if ( !player || !player->client || bonus <= 0 ) {
		return;
	}

	if ( !label || !label[0] ) {
		return;
	}

	Com_sprintf( command, sizeof( command ), "cp \"%s ^7(+%i)\"", label, bonus );
	G_TeamCommand( player->client->sess.sessionTeam, command );
}

/*
=============
G_ADAwardBonus

Applies Attack & Defend score bonuses and surfaces their HUD feedback.
=============
*/
void G_ADAwardBonus( gentity_t *player, const vec3_t origin, int bonus, const char *label ) {
	if ( !G_ADBonusesEnabled() || bonus <= 0 || !player || !player->client ) {
		return;
	}

	AddScore( player, origin, bonus );
	AddTeamScore( origin, player->client->sess.sessionTeam, bonus );
	G_ADAnnounceBonus( player, label, bonus );
}

/*
=============
Team_InitGame

Initializes team tracking, domination points, and shuffle callbacks.
=============
*/
void Team_InitGame( void ) {
	memset( &teamgame, 0, sizeof( teamgame ) );
	Team_InitDomination();

	switch ( g_gametype.integer ) {
	case GT_CTF:
		teamgame.redStatus = teamgame.blueStatus = -1; // Invalid to force update
		Team_SetFlagStatus( TEAM_RED, FLAG_ATBASE );
		Team_SetFlagStatus( TEAM_BLUE, FLAG_ATBASE );
		break;
	case GT_1FCTF:
		teamgame.flagStatus = -1; // Invalid to force update
		Team_SetFlagStatus( TEAM_FREE, FLAG_ATBASE );
		break;
	default:
		break;
	}

	G_AutoShuffleCountdown_SetGuard( Team_ShouldDeferAutoShuffleAnnouncements );
	G_AutoShuffleCountdown_SetCompleteCallback( Team_HandleAutoShuffleCountdownComplete );
	level.autoShuffleLastExecuteTime = 0;
	s_teamAutoShuffleArmed = qfalse;
}



/*
=============
Team_HasTeamGameActive

Returns qtrue when the active gametype tracks red/blue teams.
=============
*/
static qboolean Team_HasTeamGameActive( void ) {
	return ( g_gametype.integer >= GT_TEAM ) ? qtrue : qfalse;
}

/*
=============
Team_ShouldDeferAutoShuffleAnnouncements

Prevents countdown announcements during timeouts, intermissions, or live rounds.
=============
*/
static qboolean Team_ShouldDeferAutoShuffleAnnouncements( void ) {
	if ( level.timeoutActive ) {
		return qtrue;
	}
	if ( level.intermissionQueued || level.intermissiontime ) {
		return qtrue;
	}
	if ( level.roundState == ROUNDSTATE_ACTIVE ) {
		return qtrue;
	}
	return qfalse;
}

/*
=============
Team_BuildBalanceInfo

Caches the current team counts for balance and shuffle decisions.
=============
*/
static void Team_BuildBalanceInfo( teamBalanceInfo_t *info ) {
	if ( !info ) {
		return;
	}

	info->redCount = TeamCount( -1, TEAM_RED );
	info->blueCount = TeamCount( -1, TEAM_BLUE );
	info->totalCount = info->redCount + info->blueCount;
}

/*
=============
Team_GetRequiredPlayersPerTeam

Returns the configured minimum team size, clamped to zero or higher.
=============
*/
static int Team_GetRequiredPlayersPerTeam( void ) {
	int required = g_teamSizeMin.integer;

	if ( required < 0 ) {
		required = 0;
	}

	return required;
}

/*
=============
Team_GetAutoShuffleMinimumPlayers

Resolves the minimum number of total players required before auto-shuffle arms.
=============
*/
static int Team_GetAutoShuffleMinimumPlayers( void ) {
	int threshold = g_shuffleAutomaticMinPlayers.integer;

	if ( threshold <= 0 ) {
		threshold = g_shuffleMinPlayers.integer;
	}
	if ( threshold <= 0 ) {
		threshold = 4;
	}

	return threshold;
}

/*
=============
Team_ShouldAutoShuffle

Evaluates whether conditions warrant arming or executing an auto-shuffle.
=============
*/
static qboolean Team_ShouldAutoShuffle( const teamBalanceInfo_t *info ) {
	int delta;

	if ( !info ) {
		return qfalse;
	}
	if ( !Team_HasTeamGameActive() ) {
		return qfalse;
	}
	if ( g_shuffleAutomatic.integer <= 0 ) {
		return qfalse;
	}
	if ( level.warmupTime <= 0 ) {
		return qfalse;
	}
	if ( info->totalCount < Team_GetAutoShuffleMinimumPlayers() ) {
		return qfalse;
	}
	delta = abs( info->redCount - info->blueCount );
	if ( delta < 2 ) {
		return qfalse;
	}
	return qtrue;
}

/*
=============
Team_HandleAutoShuffleCountdownComplete

Invoked when the countdown reaches zero so the pending shuffle can execute.
=============
*/
static void Team_HandleAutoShuffleCountdownComplete( void ) {
	teamBalanceInfo_t info;

	Team_BuildBalanceInfo( &info );
	s_teamAutoShuffleArmed = qfalse;
	if ( !Team_ShouldAutoShuffle( &info ) ) {
		return;
	}
	Team_PerformAutomaticShuffle();
}

/*
=============
Team_IsAutoShuffleArmed

Returns qtrue when an automatic shuffle countdown has been armed.
=============
*/
qboolean Team_IsAutoShuffleArmed( void ) {
	return s_teamAutoShuffleArmed;
}

/*
=============
Team_PerformAutomaticShuffle

Randomizes players across teams and finalizes the auto-shuffle execution.
=============
*/
static void Team_PerformAutomaticShuffle( void ) {
	int players[MAX_CLIENTS];
	int playerCount;
	int i;
	int swaps;
	int targetRed;
	int assignedRed;
	int shuffled;

	if ( !Team_HasTeamGameActive() || level.warmupTime <= 0 ) {
		return;
	}

	playerCount = 0;
	for ( i = 0; i < level.maxclients; i++ ) {
		gclient_t *client = &level.clients[i];

		if ( client->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( client->sess.sessionTeam != TEAM_RED && client->sess.sessionTeam != TEAM_BLUE ) {
			continue;
		}

		players[playerCount++] = i;
	}

	if ( playerCount < 2 ) {
		return;
	}

	for ( i = playerCount - 1; i > 0; i-- ) {
		int temp;

		swaps = rand() % ( i + 1 );
		if ( swaps == i ) {
			continue;
		}

		temp = players[i];
		players[i] = players[swaps];
		players[swaps] = temp;
	}

	targetRed = ( playerCount + 1 ) / 2;
	assignedRed = 0;
	shuffled = 0;

	for ( i = 0; i < playerCount; i++ ) {
		int clientNum = players[i];
		gentity_t *ent = &g_entities[clientNum];
		const char *teamToken;

		if ( !ent->client ) {
			continue;
		}

		teamToken = ( assignedRed < targetRed ) ? "red" : "blue";
		if ( assignedRed < targetRed ) {
			assignedRed++;
		}

		if ( ( teamToken[0] == 'r' && ent->client->sess.sessionTeam == TEAM_RED ) ||
			( teamToken[0] == 'b' && ent->client->sess.sessionTeam == TEAM_BLUE ) ) {
			continue;
		}

		SetTeam( ent, (char *)teamToken );
		shuffled++;
	}

	level.autoShuffleLastExecuteTime = level.time;
	G_AutoShuffleCountdown_Cancel();
	s_teamAutoShuffleArmed = qfalse;

	if ( shuffled > 0 ) {
		G_LogPrintf( "match: auto-shuffle executed (%i players, %i moves)\n", playerCount, shuffled );
		trap_SendServerCommand( -1, "cp \"Teams automatically shuffled\n\"" );
	} else {
		G_LogPrintf( "match: auto-shuffle skipped (no moves)\n" );
	}

	G_UpdateMatchStateConfigString();
}

/*
=============
Team_UpdateAutoShuffleState

Monitors the team counts and schedules automatic shuffles when imbalance persists.
=============
*/
void Team_UpdateAutoShuffleState( void ) {
	teamBalanceInfo_t info;
	qboolean shouldShuffle;
	int delay;

	if ( !Team_HasTeamGameActive() ) {
		if ( s_teamAutoShuffleArmed || G_AutoShuffleCountdown_IsActive() ) {
			G_AutoShuffleCountdown_Cancel();
			s_teamAutoShuffleArmed = qfalse;
			G_UpdateMatchStateConfigString();
		}
		return;
	}

	Team_BuildBalanceInfo( &info );
	shouldShuffle = Team_ShouldAutoShuffle( &info );

	if ( !shouldShuffle ) {
		if ( s_teamAutoShuffleArmed || G_AutoShuffleCountdown_IsActive() ) {
			G_AutoShuffleCountdown_Cancel();
			if ( s_teamAutoShuffleArmed ) {
				trap_SendServerCommand( -1, "print \"Auto-shuffle cancelled.\\n\"" );
				G_LogPrintf( "match: auto-shuffle cancelled\n" );
			}
			s_teamAutoShuffleArmed = qfalse;
			G_UpdateMatchStateConfigString();
		}
		return;
	}

	if ( G_AutoShuffleCountdown_IsActive() ) {
		Team_ClampWarmupToShuffleCountdown();
		return;
	}

	if ( s_teamAutoShuffleArmed ) {
		return;
	}

	delay = g_shuffleTimedelay.integer;
	if ( delay < 0 ) {
		delay = 0;
	}

	if ( delay <= 0 ) {
		Team_PerformAutomaticShuffle();
		return;
	}

	G_AutoShuffleCountdown_Arm( delay * 1000 );
	s_teamAutoShuffleArmed = qtrue;
	Team_ClampWarmupToShuffleCountdown();
	G_LogPrintf( "match: auto-shuffle armed (%i seconds)\n", delay );
	trap_SendServerCommand( -1, va( "print \"Auto-shuffle will execute in %i seconds.\\n\"", delay ) );
	G_UpdateMatchStateConfigString();
}

/*
=============
Team_ClampWarmupToShuffleCountdown

Extends the warmup timer so the shuffle countdown can complete before live play.
=============
*/
void Team_ClampWarmupToShuffleCountdown( void ) {
	int secondsRemaining;
	int targetTime;

	if ( !Team_HasTeamGameActive() ) {
		return;
	}
	if ( !G_AutoShuffleCountdown_IsActive() ) {
		return;
	}
	if ( level.warmupTime <= 0 ) {
		return;
	}

	secondsRemaining = G_AutoShuffleCountdown_GetSecondsRemaining();
	if ( secondsRemaining <= 0 ) {
		return;
	}

	targetTime = level.time + secondsRemaining * 1000;
	if ( level.warmupTime < targetTime ) {
		level.warmupTime = targetTime;
		trap_SetConfigstring( CS_WARMUP, va( "%i", level.warmupTime ) );
	}
}

/*
=============
Team_HasMinimumPlayersForWarmup

Determines if the teams satisfy the configured warmup player requirements.
=============
*/
qboolean Team_HasMinimumPlayersForWarmup( void ) {
	teamBalanceInfo_t info;
	int required;

	if ( g_gametype.integer < GT_TEAM ) {
		return ( level.numPlayingClients >= 2 ) ? qtrue : qfalse;
	}

	Team_BuildBalanceInfo( &info );
	if ( info.redCount < 1 || info.blueCount < 1 ) {
		return qfalse;
	}

	required = Team_GetRequiredPlayersPerTeam();
	if ( required <= 1 ) {
		return qtrue;
	}

	if ( g_teamForcePresent.integer ) {
		return ( info.redCount >= required && info.blueCount >= required ) ? qtrue : qfalse;
	}
	if ( info.redCount < required && info.blueCount < required ) {
		return qfalse;
	}
	return qtrue;
}

/*
=============
Team_GetRespawnRatioForTeam

Returns a percentage describing how close the team is to satisfying g_teamSizeMin.
=============
*/
int Team_GetRespawnRatioForTeam( team_t team ) {
	int required;
	int count;

	if ( team != TEAM_RED && team != TEAM_BLUE ) {
		return 0;
	}
	if ( !Team_HasTeamGameActive() ) {
		return 100;
	}

	required = Team_GetRequiredPlayersPerTeam();
	if ( required <= 0 ) {
		required = 1;
	}

	count = TeamCount( -1, team );
	if ( count <= 0 ) {
		return 0;
	}

	return ( count * 100 ) / required;
}


/*
=============
Team_InitDominationState

Clears Domination point tracking between matches.
=============
*/
static void Team_InitDominationState( void ) {
	int		i;

	for ( i = 0; i < DOMINATION_MAX_POINTS; i++ ) {
		dominationPoint_t	*point = &teamgame.dominationPoints[i];

		memset( point, 0, sizeof( *point ) );
		point->ownerTeam = TEAM_FREE;
		point->capturingTeam = TEAM_FREE;
	}

	teamgame.dominationPointCount = 0;
	teamgame.dominationNextScoreTime = 0;
}

/*
=============
Team_InitDomination

Initializes Domination bookkeeping for the active match.
=============
*/
static void Team_InitDomination( void ) {
	Team_InitDominationState();

	if ( g_gametype.integer != GT_DOMINATION ) {
		return;
	}

	level.teamScores[TEAM_RED] = 0;
	level.teamScores[TEAM_BLUE] = 0;
}

/*
=============
Team_DominationPointForTrigger

Looks up the Domination point associated with the supplied trigger.
=============
*/
static dominationPoint_t *Team_DominationPointForTrigger( const gentity_t *ent ) {
	int		i;

	for ( i = 0; i < teamgame.dominationPointCount; i++ ) {
		if ( teamgame.dominationPoints[i].trigger == ent ) {
			return &teamgame.dominationPoints[i];
		}
	}

	return NULL;
}

/*
=============
Team_DominationPointForPointEnt

Looks up the Domination point that owns the provided info entity.
=============
*/
static dominationPoint_t *Team_DominationPointForPointEnt( const gentity_t *ent ) {
	int		i;

	for ( i = 0; i < teamgame.dominationPointCount; i++ ) {
		if ( teamgame.dominationPoints[i].pointEnt == ent ) {
			return &teamgame.dominationPoints[i];
		}
	}

	return NULL;
}

/*
=============
Team_DominationPointForTargetName

Finds a Domination point using its targetname.
=============
*/
static dominationPoint_t *Team_DominationPointForTargetName( const char *targetname ) {
	int		i;

	if ( !targetname || !targetname[0] ) {
		return NULL;
	}

	for ( i = 0; i < teamgame.dominationPointCount; i++ ) {
		if ( !Q_stricmp( teamgame.dominationPoints[i].targetName, targetname ) ) {
			return &teamgame.dominationPoints[i];
		}
	}

	return NULL;
}

/*
=============
Team_DominationBuildSpawnList

Collects info_player_deathmatch nodes tied to a Domination point.
=============
*/
static void Team_DominationBuildSpawnList( dominationPoint_t *point ) {
	gentity_t	*match;
	const char	*target;
	int		count;
	int		i;

	if ( !point || !point->pointEnt ) {
		return;
	}

	match = NULL;
	count = 0;
	target = point->pointEnt->target;
	point->pointEnt->target_ent = NULL;
	point->spawnTargetCount = 0;
	point->pointEnt->count = 0;

	if ( !target || !target[0] ) {
		return;
	}

	while ( ( match = G_Find( match, FOFS( targetname ), target ) ) != NULL ) {
		if ( Q_stricmp( match->classname, "info_player_deathmatch" ) ) {
			continue;
		}

		if ( count >= DOMINATION_MAX_POINT_SPAWNS ) {
			G_Printf( "WARNING: Domination point %s exceeded spawn budget (%d)\n",
				point->label, DOMINATION_MAX_POINT_SPAWNS );
			break;
		}

		point->spawnTargets[count++] = match;
	}

	point->spawnTargetCount = count;
	point->pointEnt->count = count;
	point->pointEnt->target_ent = NULL;

	for ( i = count - 1; i >= 0; i-- ) {
		match = point->spawnTargets[i];
		match->nextTrain = point->pointEnt->target_ent;
		point->pointEnt->target_ent = match;
	}
}

/*
=============
Team_DominationPointThink

Retries spawn linking for Domination metadata entities.
=============
*/
static void Team_DominationPointThink( gentity_t *ent ) {
	dominationPoint_t	*point;

	point = Team_DominationPointForPointEnt( ent );
	if ( !point ) {
		ent->think = NULL;
		ent->nextthink = 0;
		return;
	}

	Team_DominationBuildSpawnList( point );
	if ( point->spawnTargetCount > 0 || !ent->target || !ent->target[0] ) {
		ent->think = NULL;
		ent->nextthink = 0;
		return;
	}

	ent->nextthink = level.time + 100;
}

/*
=============
Team_DominationEventOrigin

Derives an origin for Domination temp entities.
=============
*/
static void Team_DominationEventOrigin( const dominationPoint_t *point, vec3_t origin ) {
	if ( point->trigger ) {
		VectorCopy( point->trigger->s.origin, origin );
		return;
	}

	if ( point->pointEnt ) {
		VectorCopy( point->pointEnt->s.origin, origin );
		return;
	}

	VectorClear( origin );
}


/*
=============
Team_DominationCaptureTime

Returns the Domination capture time in milliseconds.
=============
*/
static int Team_DominationCaptureTime( void ) {
	int		seconds = g_domCapTime.integer;

	if ( seconds < 1 ) {
		seconds = 1;
	}

	return seconds * 1000;
}

/*
=============
Team_DominationScoreInterval

Returns the Domination scoring cadence in milliseconds.
=============
*/
static int Team_DominationScoreInterval( void ) {
	int		seconds = g_domScoreRate.integer;

	if ( seconds < 1 ) {
		seconds = 1;
	}

	return seconds * 1000;
}

/*
=============
Team_DominationCaptureMultiplier

Calculates the capture speed adjustment granted by teammates.
=============
*/
static float Team_DominationCaptureMultiplier( int playerCount ) {
	float		scale;

	if ( playerCount <= 0 ) {
		return 0.0f;
	}

	if ( playerCount == 1 ) {
		return 1.0f;
	}

	scale = g_domTeammateCapScale.value;
	return 1.0f + ( playerCount - 1 ) * scale;
}

/*
=============
Team_RegisterDominationPoint

Registers a Domination control point metadata entity.
=============
*/
void Team_RegisterDominationPoint( gentity_t *pointEnt ) {
	dominationPoint_t	*point;
	char		defaultLabel[DOMINATION_LABEL_MAX];
	int		index;

	if ( teamgame.dominationPointCount >= DOMINATION_MAX_POINTS ) {
		G_Printf( "WARNING: too many Domination points (max %d)\n", DOMINATION_MAX_POINTS );
		G_FreeEntity( pointEnt );
		return;
	}

	index = teamgame.dominationPointCount;
	point = &teamgame.dominationPoints[index];
	memset( point, 0, sizeof( *point ) );
	point->pointEnt = pointEnt;
	point->ownerTeam = TEAM_FREE;
	point->capturingTeam = TEAM_FREE;
	point->trigger = NULL;

	if ( pointEnt->message && pointEnt->message[0] ) {
		Q_strncpyz( point->label, pointEnt->message, sizeof( point->label ) );
	} else {
		Com_sprintf( defaultLabel, sizeof( defaultLabel ), "%c", 'A' + index );
		Q_strncpyz( point->label, defaultLabel, sizeof( point->label ) );
	}

	if ( pointEnt->targetname ) {
		Q_strncpyz( point->targetName, pointEnt->targetname, sizeof( point->targetName ) );
	} else {
		point->targetName[0] = '\0';
	}

	Team_DominationBuildSpawnList( point );
	if ( point->spawnTargetCount <= 0 && pointEnt->target && pointEnt->target[0] ) {
		pointEnt->think = Team_DominationPointThink;
		pointEnt->nextthink = level.time + 100;
	}

	teamgame.dominationPointCount++;

	if ( teamgame.dominationNextScoreTime == 0 ) {
		teamgame.dominationNextScoreTime = level.time + Team_DominationScoreInterval();
	}
/*
=============
Team_RegisterDominationTrigger

Binds a Domination capture trigger to its metadata entity.
=============
*/
qboolean Team_RegisterDominationTrigger( gentity_t *trigger ) {
	dominationPoint_t	*point;

	if ( g_gametype.integer != GT_DOMINATION ) {
		G_FreeEntity( trigger );
		return qfalse;
	}

	if ( !trigger->target || !trigger->target[0] ) {
		G_Printf( "trigger_capturezone: missing target\n" );
		return qfalse;
	}

	point = Team_DominationPointForTargetName( trigger->target );
	if ( !point ) {
		return qfalse;
	}

	if ( point->trigger && point->trigger != trigger ) {
		G_Printf( "trigger_capturezone: duplicate target %s\n", trigger->target );
		return qfalse;
	}

	point->trigger = trigger;
	trigger->target_ent = point->pointEnt;
	return qtrue;
}

}

/*
=============
Team_DominationPointTouch

Counts players occupying a Domination point trigger.
=============
*/
void Team_DominationPointTouch( gentity_t *trigger, gentity_t *other, trace_t *trace ) {
	dominationPoint_t	*point;
	int		pointIndex;

	(void)trace;

	if ( g_gametype.integer != GT_DOMINATION ) {
		return;
	}

	if ( !other->client ) {
		return;
	}

	if ( other->client->sess.sessionTeam != TEAM_RED && other->client->sess.sessionTeam != TEAM_BLUE ) {
		return;
	}

	point = Team_DominationPointForTrigger( trigger );
	if ( !point ) {
		return;
	}

	pointIndex = point - teamgame.dominationPoints;
	if ( pointIndex < 0 || pointIndex >= DOMINATION_MAX_POINTS ) {
		return;
	}

	if ( other->client->dominationTouchFrame[pointIndex] == level.framenum ) {
		return;
	}

	other->client->dominationTouchFrame[pointIndex] = level.framenum;

	if ( point->lastOccupancyFrame != level.framenum ) {
		point->redOccupants = 0;
		point->blueOccupants = 0;
		point->lastOccupancyFrame = level.framenum;
	}

	if ( other->client->sess.sessionTeam == TEAM_RED ) {
		point->redOccupants++;
	} else {
		point->blueOccupants++;
	}
}

/*
=============
Team_DominationAnnounceCapture

Broadcasts that a Domination point has changed hands.
=============
*/
static void Team_DominationAnnounceCapture( dominationPoint_t *point, team_t previousOwner ) {
	gentity_t		*te;
	const char	*teamName;
	vec3_t	origin;

	if ( point->ownerTeam != TEAM_RED && point->ownerTeam != TEAM_BLUE ) {
		return;
	Team_DominationEventOrigin( point, origin );

	te = G_TempEntity( origin, EV_GLOBAL_TEAM_SOUND );
	te->r.svFlags |= SVF_BROADCAST;
	te->s.eventParm = ( point->ownerTeam == TEAM_RED ) ? GTS_RED_CAPTURE : GTS_BLUE_CAPTURE;

	teamName = TeamName( point->ownerTeam );
	trap_SendServerCommand( -1, va( "cp \"%s captured %s\"", teamName, point->label ) );

	if ( previousOwner != TEAM_FREE && previousOwner != point->ownerTeam ) {
		point->lastDistressTime = 0;
	}
}

/*
=============
Team_DominationAnnounceNeutralized

Informs players that a Domination point has been neutralized.
=============
*/
static void Team_DominationAnnounceNeutralized( dominationPoint_t *point, team_t attacker ) {
	gentity_t		*te;
	team_t		victim;
	vec3_t	origin;

	if ( attacker != TEAM_RED && attacker != TEAM_BLUE ) {
		return;
	}
	Team_DominationEventOrigin( point, origin );
	victim = ( attacker == TEAM_RED ) ? TEAM_BLUE : TEAM_RED;
	te = G_TempEntity( origin, EV_GLOBAL_TEAM_SOUND );
	te->r.svFlags |= SVF_BROADCAST;
	te->s.eventParm = ( victim == TEAM_RED ) ? GTS_RED_TAKEN : GTS_BLUE_TAKEN;
	trap_SendServerCommand( -1, va( "cp \"%s neutralized %s\"", TeamName( attacker ), point->label ) );
}

/*
=============
Team_DominationSendDistress

Warns defenders that their point is close to being captured.
=============
*/
static void Team_DominationSendDistress( dominationPoint_t *point ) {
	team_t		team = point->ownerTeam;

	if ( team != TEAM_RED && team != TEAM_BLUE ) {
		return;
	}

	if ( level.time - point->lastDistressTime < DOMINATION_DISTRESS_REPEAT_TIME ) {
		return;
	}

	point->lastDistressTime = level.time;
	point->distressNotified = qtrue;
	G_TeamCommand( team, va( "cp \"Protect domination point %s!\"", point->label ) );
}

/*
=============
Team_DominationUpdatePointState

Advances capture progress for a single Domination point.
=============
*/
static void Team_DominationUpdatePointState( dominationPoint_t *point, int captureTime ) {
	int		redOccupants = 0;
	int		blueOccupants = 0;
	team_t	advanceTeam = TEAM_FREE;
	int		playerCount = 0;
	float		delta;
	float		threshold;

	if ( point->lastOccupancyFrame == level.framenum ) {
		redOccupants = point->redOccupants;
		blueOccupants = point->blueOccupants;
	}

	if ( redOccupants > 0 || blueOccupants > 0 ) {
		if ( redOccupants > 0 && blueOccupants > 0 ) {
			if ( g_domEnableContention.integer ) {
				if ( redOccupants != blueOccupants ) {
					advanceTeam = ( redOccupants > blueOccupants ) ? TEAM_RED : TEAM_BLUE;
					playerCount = abs( redOccupants - blueOccupants );
				}
			}
		} else if ( redOccupants > 0 ) {
			advanceTeam = TEAM_RED;
			playerCount = redOccupants;
		} else {
			advanceTeam = TEAM_BLUE;
			playerCount = blueOccupants;
		}
	}

	if ( advanceTeam != TEAM_FREE && point->capturingTeam == TEAM_FREE && point->ownerTeam == advanceTeam && point->ownerTeam != TEAM_FREE ) {
		advanceTeam = TEAM_FREE;
	}

	if ( advanceTeam == TEAM_FREE || playerCount <= 0 ) {
		if ( point->capturingTeam == TEAM_FREE ) {
			point->progress = 0.0f;
			point->neutralizing = qfalse;
			point->distressNotified = qfalse;
		}
		point->redOccupants = 0;
		point->blueOccupants = 0;
		return;
	}

	delta = ( captureTime > 0 ) ? ( (float)level.msec / (float)captureTime ) * 100.0f : 0.0f;
	delta *= Team_DominationCaptureMultiplier( playerCount );
	if ( delta <= 0.0f ) {
		point->redOccupants = 0;
		point->blueOccupants = 0;
		return;
	}

	if ( point->capturingTeam == TEAM_FREE ) {
		point->capturingTeam = advanceTeam;
		point->progress = 0.0f;
		point->neutralizing = ( g_domNeutralFlag.integer && point->ownerTeam != TEAM_FREE && point->ownerTeam != advanceTeam );
		point->distressNotified = qfalse;
	}

	if ( point->capturingTeam != advanceTeam ) {
		point->progress -= delta;
		if ( point->progress <= 0.0f ) {
			point->progress = 0.0f;
			point->capturingTeam = advanceTeam;
			point->neutralizing = ( g_domNeutralFlag.integer && point->ownerTeam != TEAM_FREE && point->ownerTeam != advanceTeam );
			point->distressNotified = qfalse;
		}
		point->redOccupants = 0;
		point->blueOccupants = 0;
		return;
	}

	point->progress += delta;
	if ( point->progress >= 100.0f ) {
		point->progress = 100.0f;
		if ( point->neutralizing ) {

			point->ownerTeam = TEAM_FREE;
			point->neutralizing = qfalse;
			point->progress = 0.0f;
			Team_DominationAnnounceNeutralized( point, point->capturingTeam );
			point->distressNotified = qfalse;
			point->lastDistressTime = 0;
		} else {
			team_t	previousOwner = point->ownerTeam;

			point->ownerTeam = point->capturingTeam;
			point->capturingTeam = TEAM_FREE;
			point->progress = 0.0f;
			point->distressNotified = qfalse;
			if ( previousOwner != point->ownerTeam ) {
				Team_DominationAnnounceCapture( point, previousOwner );
			}
		}
	}

	threshold = Com_Clamp( 0.0f, 100.0f, g_domDistressThreshold.value );
	if ( point->ownerTeam != TEAM_FREE && point->capturingTeam != TEAM_FREE && point->capturingTeam != point->ownerTeam ) {
		if ( !point->distressNotified && point->progress >= threshold ) {
			Team_DominationSendDistress( point );
		}
	}

	point->redOccupants = 0;
	point->blueOccupants = 0;
}

/*
=============
Team_RunDomination

Executes Domination capture logic and handles scoring.
=============
*/
void Team_RunDomination( void ) {
	int		captureTime;
	int		scoreInterval;
	int		redOwned = 0;
	int		blueOwned = 0;
	int		i;
	vec3_t	origin = { 0.0f, 0.0f, 0.0f };

	if ( g_gametype.integer != GT_DOMINATION ) {
		teamgame.dominationNextScoreTime = 0;
		return;
	}

	if ( teamgame.dominationPointCount <= 0 ) {
		teamgame.dominationNextScoreTime = 0;
		return;
	}

	captureTime = Team_DominationCaptureTime();
	scoreInterval = Team_DominationScoreInterval();

	for ( i = 0; i < teamgame.dominationPointCount; i++ ) {
		dominationPoint_t	*point = &teamgame.dominationPoints[i];

		Team_DominationUpdatePointState( point, captureTime );
		if ( point->ownerTeam == TEAM_RED ) {
			redOwned++;
		} else if ( point->ownerTeam == TEAM_BLUE ) {
			blueOwned++;
		}
	}

	if ( teamgame.dominationNextScoreTime == 0 ) {
		teamgame.dominationNextScoreTime = level.time + scoreInterval;
	}

	if ( level.time < teamgame.dominationNextScoreTime ) {
		return;
	}

	if ( redOwned > 0 ) {
		AddTeamScore( origin, TEAM_RED, redOwned );
	}

	if ( blueOwned > 0 ) {
		AddTeamScore( origin, TEAM_BLUE, blueOwned );
	}

	teamgame.dominationNextScoreTime = level.time + scoreInterval;
}

int OtherTeam(int team) {
	if (team==TEAM_RED)
		return TEAM_BLUE;
	else if (team==TEAM_BLUE)
		return TEAM_RED;
	return team;
}

const char *TeamName(int team)  {
	if (team==TEAM_RED)
		return "RED";
	else if (team==TEAM_BLUE)
		return "BLUE";
	else if (team==TEAM_SPECTATOR)
		return "SPECTATOR";
	return "FREE";
}

const char *OtherTeamName(int team) {
	if (team==TEAM_RED)
		return "BLUE";
	else if (team==TEAM_BLUE)
		return "RED";
	else if (team==TEAM_SPECTATOR)
		return "SPECTATOR";
	return "FREE";
}

const char *TeamColorString(int team) {
	if (team==TEAM_RED)
		return S_COLOR_RED;
	else if (team==TEAM_BLUE)
		return S_COLOR_BLUE;
	else if (team==TEAM_SPECTATOR)
		return S_COLOR_YELLOW;
	return S_COLOR_WHITE;
}

// NULL for everyone
void QDECL PrintMsg( gentity_t *ent, const char *fmt, ... ) {
	char		msg[1024];
	va_list		argptr;
	char		*p;
	
	va_start (argptr,fmt);
	if (vsprintf (msg, fmt, argptr) > sizeof(msg)) {
		G_Error ( "PrintMsg overrun" );
	}
	va_end (argptr);

	// double quotes are bad
	while ((p = strchr(msg, '"')) != NULL)
		*p = '\'';

	trap_SendServerCommand ( ( (ent == NULL) ? -1 : ent-g_entities ), va("print \"%s\"", msg ));
}

/*
==============
AddTeamScore

 used for gametype > GT_TEAM
 for gametype GT_TEAM the level.teamScores is updated in AddScore in g_combat.c
==============
*/
void AddTeamScore(vec3_t origin, int team, int score) {
	gentity_t	*te;

	te = G_TempEntity(origin, EV_GLOBAL_TEAM_SOUND );
	te->r.svFlags |= SVF_BROADCAST;

	if ( team == TEAM_RED ) {
		if ( level.teamScores[ TEAM_RED ] + score == level.teamScores[ TEAM_BLUE ] ) {
			//teams are tied sound
			te->s.eventParm = GTS_TEAMS_ARE_TIED;
		}
		else if ( level.teamScores[ TEAM_RED ] <= level.teamScores[ TEAM_BLUE ] &&
					level.teamScores[ TEAM_RED ] + score > level.teamScores[ TEAM_BLUE ]) {
			// red took the lead sound
			te->s.eventParm = GTS_REDTEAM_TOOK_LEAD;
		}
		else {
			// red scored sound
			te->s.eventParm = GTS_REDTEAM_SCORED;
		}
	}
	else {
		if ( level.teamScores[ TEAM_BLUE ] + score == level.teamScores[ TEAM_RED ] ) {
			//teams are tied sound
			te->s.eventParm = GTS_TEAMS_ARE_TIED;
		}
		else if ( level.teamScores[ TEAM_BLUE ] <= level.teamScores[ TEAM_RED ] &&
					level.teamScores[ TEAM_BLUE ] + score > level.teamScores[ TEAM_RED ]) {
			// blue took the lead sound
			te->s.eventParm = GTS_BLUETEAM_TOOK_LEAD;
		}
		else {
			// blue scored sound
			te->s.eventParm = GTS_BLUETEAM_SCORED;
		}
	}
	level.teamScores[ team ] += score;
}

/*
==============
OnSameTeam
==============
*/
qboolean OnSameTeam( gentity_t *ent1, gentity_t *ent2 ) {
	if ( !ent1->client || !ent2->client ) {
		return qfalse;
	}

	if ( g_gametype.integer < GT_TEAM ) {
		return qfalse;
	}

	if ( ent1->client->sess.sessionTeam == ent2->client->sess.sessionTeam ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
G_FlagPowerupTeam

Resolves the owning team for a specific flag powerup constant.
=============
*/
static int G_FlagPowerupTeam( int flagPowerup ) {
	switch ( flagPowerup ) {
	case PW_REDFLAG:
		return TEAM_RED;
	case PW_BLUEFLAG:
		return TEAM_BLUE;
	case PW_NEUTRALFLAG:
		return TEAM_FREE;
	default:
		break;
	}

	return -1;
}

/*
=============
G_BuildFlagDropVelocity

Computes the outgoing velocity for a dropped flag based on the configured tuning values.
=============
*/
static void G_BuildFlagDropVelocity( gentity_t *carrier, vec3_t velocity ) {
	float forwardSpeed;
	float verticalSpeed;
	vec3_t forward;

	VectorClear( velocity );
	if ( !carrier || !carrier->client ) {
		return;
	}

	forwardSpeed = ( g_flagConfig.throwFlagForwardMult > 0 ) ? g_flagConfig.throwFlagForwardMult : 150.0f;
	verticalSpeed = ( g_flagConfig.throwFlagVelocity > 0 ) ? g_flagConfig.throwFlagVelocity : 200.0f;

	AngleVectors( carrier->client->ps.viewangles, forward, NULL, NULL );
	VectorScale( forward, forwardSpeed, velocity );
	velocity[2] += verticalSpeed + crandom() * 50.0f;
}

/*
=============
G_InitFlagDropPhysics

Applies the configured physics settings to a dropped flag entity.
=============
*/
static void G_InitFlagDropPhysics( gentity_t *carrier, gentity_t *drop ) {
	float bounce;

	if ( !drop ) {
		return;
	}

	if ( g_flagConfig.flagPhysics > 0 ) {
		drop->physicsObject = qtrue;
	}

	bounce = g_flagConfig.flagBounce;
	if ( bounce < 0.0f ) {
		bounce = 0.0f;
	} else if ( bounce > 1.0f ) {
		bounce = 1.0f;
	}

	if ( bounce > 0.0f ) {
		drop->s.eFlags |= EF_BOUNCE_HALF;
		drop->physicsBounce = bounce;
	} else {
		drop->s.eFlags &= ~EF_BOUNCE_HALF;
		drop->physicsBounce = 0.0f;
	}

	(void)carrier;
}

/*
=============
G_ClearDroppedFlagState

Resets the tackle metadata stored on a flag entity.
=============
*/
static void G_ClearDroppedFlagState( gentity_t *flag ) {
	if ( !flag ) {
		return;
	}

	flag->flagDroppedByEnemy = qfalse;
	flag->flagDroppedBySuicide = qfalse;
	flag->flagDroppedByClientNum = ENTITYNUM_NONE;
}

/*
=============
G_ApplyDroppedFlagMetadata

Records how a flag was dropped so the return logic can react accordingly.
=============
*/
static void G_ApplyDroppedFlagMetadata( gentity_t *drop, qboolean tackleDrop, qboolean suicideDrop, const gentity_t *attacker ) {
	if ( !drop ) {
		return;
	}

	G_ClearDroppedFlagState( drop );
	drop->flagDroppedByEnemy = tackleDrop;
	drop->flagDroppedBySuicide = suicideDrop;
	if ( attacker ) {
		drop->flagDroppedByClientNum = attacker->s.number;
	}
}

/*
=============
G_HandleFlagTackleBonus

Awards the tackle bonus and accompanying messaging when an attacker forces a drop.
=============
*/
static qboolean G_HandleFlagTackleBonus( gentity_t *carrier, gentity_t *attacker, int flagTeam ) {
	if ( !g_flagConfig.tackleFlag ) {
		return qfalse;
	}

	if ( !carrier || !carrier->client || !attacker || !attacker->client ) {
		return qfalse;
	}

	if ( attacker == carrier ) {
		return qfalse;
	}

	if ( OnSameTeam( carrier, attacker ) ) {
		return qfalse;
	}

	AddScore( attacker, carrier->r.currentOrigin, g_flagConfig.droppedFlagBonus );
	PrintMsg( NULL, "%s" S_COLOR_WHITE " tackled the %s flag carrier!\n",
		attacker->client->pers.netname, TeamName( flagTeam ) );
	return qtrue;
}

/*
=============
G_TossFlag

Drops or returns a carried flag depending on the provided context and configuration.
=============
*/
flagDropResult_t G_TossFlag( gentity_t *carrier, int flagPowerup, flagDropContext_t context, gentity_t *attacker, int meansOfDeath, gentity_t **dropped ) {
	int flagTeam;
	qboolean suicide;
	qboolean tackleDrop;
	gitem_t *item;
	gentity_t *drop;
	vec3_t velocity;
	flagDropResult_t result;

	if ( dropped ) {
		*dropped = NULL;
	}

	if ( !carrier || !carrier->client ) {
		return FLAG_DROP_RESULT_NONE;
	}

	flagTeam = G_FlagPowerupTeam( flagPowerup );
	if ( flagTeam == -1 ) {
		return FLAG_DROP_RESULT_NONE;
	}

	if ( !carrier->client->ps.powerups[ flagPowerup ] ) {
		return FLAG_DROP_RESULT_NONE;
	}

	carrier->client->ps.powerups[ flagPowerup ] = 0;
	suicide = ( context == FLAG_DROP_CONTEXT_DEATH && ( attacker == carrier || meansOfDeath == MOD_SUICIDE ) );
	tackleDrop = qfalse;
	result = FLAG_DROP_RESULT_NONE;

	if ( context == FLAG_DROP_CONTEXT_FORCED_RETURN || ( suicide && g_flagConfig.returnOnSuicide ) ) {
		Team_ReturnFlag( flagTeam );
		return FLAG_DROP_RESULT_RETURNED;
	}

	item = BG_FindItemForPowerup( flagPowerup );
	if ( !item ) {
		return FLAG_DROP_RESULT_NONE;
	}

	G_BuildFlagDropVelocity( carrier, velocity );
	drop = LaunchItem( item, carrier->s.pos.trBase, velocity );
	if ( drop ) {
		G_InitFlagDropPhysics( carrier, drop );
		if ( context == FLAG_DROP_CONTEXT_DEATH ) {
			tackleDrop = G_HandleFlagTackleBonus( carrier, attacker, flagTeam );
		}
		G_ApplyDroppedFlagMetadata( drop, tackleDrop, suicide, attacker );
		Team_CheckDroppedItem( drop );
		result = FLAG_DROP_RESULT_DROPPED;
		if ( dropped ) {
			*dropped = drop;
		}
	}

	return result;
}

static char ctfFlagStatusRemap[] = { '0', '1', '*', '*', '2' };
static char oneFlagStatusRemap[] = { '0', '1', '2', '3', '4' };

void Team_SetFlagStatus( int team, flagStatus_t status ) {
	qboolean modified = qfalse;

	switch( team ) {
	case TEAM_RED:	// CTF
		if( teamgame.redStatus != status ) {
			teamgame.redStatus = status;
			modified = qtrue;
		}
		break;

	case TEAM_BLUE:	// CTF
		if( teamgame.blueStatus != status ) {
			teamgame.blueStatus = status;
			modified = qtrue;
		}
		break;

	case TEAM_FREE:	// One Flag CTF
		if( teamgame.flagStatus != status ) {
			teamgame.flagStatus = status;
			modified = qtrue;
		}
		break;
	}

	if( modified ) {
		char st[4];

		if( g_gametype.integer == GT_CTF ) {
			st[0] = ctfFlagStatusRemap[teamgame.redStatus];
			st[1] = ctfFlagStatusRemap[teamgame.blueStatus];
			st[2] = 0;
		}
		else {		// GT_1FCTF
			st[0] = oneFlagStatusRemap[teamgame.flagStatus];
			st[1] = 0;
		}

		trap_SetConfigstring( CS_FLAGSTATUS, st );
	}
}

void Team_CheckDroppedItem( gentity_t *dropped ) {
	if( dropped->item->giTag == PW_REDFLAG ) {
		Team_SetFlagStatus( TEAM_RED, FLAG_DROPPED );
	}
	else if( dropped->item->giTag == PW_BLUEFLAG ) {
		Team_SetFlagStatus( TEAM_BLUE, FLAG_DROPPED );
	}
	else if( dropped->item->giTag == PW_NEUTRALFLAG ) {
		Team_SetFlagStatus( TEAM_FREE, FLAG_DROPPED );
	}
}

/*
================
Team_ForceGesture
================
*/
void Team_ForceGesture(int team) {
	int i;
	gentity_t *ent;

	for (i = 0; i < MAX_CLIENTS; i++) {
		ent = &g_entities[i];
		if (!ent->inuse)
			continue;
		if (!ent->client)
			continue;
		if (ent->client->sess.sessionTeam != team)
			continue;
		//
		ent->flags |= FL_FORCE_GESTURE;
	}
}

/*
================
Team_FragBonuses

Calculate the bonuses for flag defense, flag carrier defense, etc.
Note that bonuses are not cumulative.  You get one, they are in importance
order.
================
*/
void Team_FragBonuses(gentity_t *targ, gentity_t *inflictor, gentity_t *attacker)
{
	int i;
	gentity_t *ent;
	int flag_pw, enemy_flag_pw;
	int otherteam;
	int tokens;
	gentity_t *flag, *carrier = NULL;
	char *c;
	vec3_t v1, v2;
	int team;

	// no bonus for fragging yourself or team mates
	if (!targ->client || !attacker->client || targ == attacker || OnSameTeam(targ, attacker))
		return;

	team = targ->client->sess.sessionTeam;
	otherteam = OtherTeam(targ->client->sess.sessionTeam);
	if (otherteam < 0)
		return; // whoever died isn't on a team

	// same team, if the flag at base, check to he has the enemy flag
	if (team == TEAM_RED) {
		flag_pw = PW_REDFLAG;
		enemy_flag_pw = PW_BLUEFLAG;
	} else {
		flag_pw = PW_BLUEFLAG;
		enemy_flag_pw = PW_REDFLAG;
	}

	if (g_gametype.integer == GT_1FCTF) {
		enemy_flag_pw = PW_NEUTRALFLAG;
	} 

	// did the attacker frag the flag carrier?
	tokens = 0;
	if( g_gametype.integer == GT_HARVESTER ) {
		tokens = targ->client->ps.generic1;
	}
	if (targ->client->ps.powerups[enemy_flag_pw]) {
		attacker->client->pers.teamState.lastfraggedcarrier = level.time;
		AddScore(attacker, targ->r.currentOrigin, CTF_FRAG_CARRIER_BONUS);
		attacker->client->pers.teamState.fragcarrier++;
		PrintMsg(NULL, "%s" S_COLOR_WHITE " fragged %s's flag carrier!\n",
			attacker->client->pers.netname, TeamName(team));

		// the target had the flag, clear the hurt carrier
		// field on the other team
		for (i = 0; i < g_maxclients.integer; i++) {
			ent = g_entities + i;
			if (ent->inuse && ent->client->sess.sessionTeam == otherteam)
				ent->client->pers.teamState.lasthurtcarrier = 0;
		}
		return;
	}

	// did the attacker frag a head carrier? other->client->ps.generic1
	if (tokens) {
		attacker->client->pers.teamState.lastfraggedcarrier = level.time;
		AddScore(attacker, targ->r.currentOrigin, CTF_FRAG_CARRIER_BONUS * tokens * tokens);
		attacker->client->pers.teamState.fragcarrier++;
		PrintMsg(NULL, "%s" S_COLOR_WHITE " fragged %s's skull carrier!\n",
			attacker->client->pers.netname, TeamName(team));

		// the target had the flag, clear the hurt carrier
		// field on the other team
		for (i = 0; i < g_maxclients.integer; i++) {
			ent = g_entities + i;
			if (ent->inuse && ent->client->sess.sessionTeam == otherteam)
				ent->client->pers.teamState.lasthurtcarrier = 0;
		}
		return;
	}

	if (targ->client->pers.teamState.lasthurtcarrier &&
		level.time - targ->client->pers.teamState.lasthurtcarrier < CTF_CARRIER_DANGER_PROTECT_TIMEOUT &&
		!attacker->client->ps.powerups[flag_pw]) {
		// attacker is on the same team as the flag carrier and
		// fragged a guy who hurt our flag carrier
		AddScore(attacker, targ->r.currentOrigin, CTF_CARRIER_DANGER_PROTECT_BONUS);

		attacker->client->pers.teamState.carrierdefense++;
		targ->client->pers.teamState.lasthurtcarrier = 0;

		attacker->client->ps.persistant[PERS_DEFEND_COUNT]++;
		team = attacker->client->sess.sessionTeam;
		// add the sprite over the player's head
		attacker->client->ps.eFlags &= ~(EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP );
		attacker->client->ps.eFlags |= EF_AWARD_DEFEND;
		attacker->client->rewardTime = level.time + REWARD_SPRITE_TIME;

		return;
	}

	if (targ->client->pers.teamState.lasthurtcarrier &&
		level.time - targ->client->pers.teamState.lasthurtcarrier < CTF_CARRIER_DANGER_PROTECT_TIMEOUT) {
		// attacker is on the same team as the skull carrier and
		AddScore(attacker, targ->r.currentOrigin, CTF_CARRIER_DANGER_PROTECT_BONUS);

		attacker->client->pers.teamState.carrierdefense++;
		targ->client->pers.teamState.lasthurtcarrier = 0;

		attacker->client->ps.persistant[PERS_DEFEND_COUNT]++;
		team = attacker->client->sess.sessionTeam;
		// add the sprite over the player's head
		attacker->client->ps.eFlags &= ~(EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP );
		attacker->client->ps.eFlags |= EF_AWARD_DEFEND;
		attacker->client->rewardTime = level.time + REWARD_SPRITE_TIME;

		return;
	}

	// flag and flag carrier area defense bonuses

	// we have to find the flag and carrier entities

	if( g_gametype.integer == GT_OBELISK ) {
		// find the team obelisk
		switch (attacker->client->sess.sessionTeam) {
		case TEAM_RED:
			c = "team_redobelisk";
			break;
		case TEAM_BLUE:
			c = "team_blueobelisk";
			break;		
		default:
			return;
		}
		
	} else if (g_gametype.integer == GT_HARVESTER ) {
		// find the center obelisk
		c = "team_neutralobelisk";
	} else {
	// find the flag
	switch (attacker->client->sess.sessionTeam) {
	case TEAM_RED:
		c = "team_CTF_redflag";
		break;
	case TEAM_BLUE:
		c = "team_CTF_blueflag";
		break;		
	default:
		return;
	}
	// find attacker's team's flag carrier
	for (i = 0; i < g_maxclients.integer; i++) {
		carrier = g_entities + i;
		if (carrier->inuse && carrier->client->ps.powerups[flag_pw])
			break;
		carrier = NULL;
	}
	}
	flag = NULL;
	while ((flag = G_Find (flag, FOFS(classname), c)) != NULL) {
		if (!(flag->flags & FL_DROPPED_ITEM))
			break;
	}

	if (!flag)
		return; // can't find attacker's flag

	// ok we have the attackers flag and a pointer to the carrier

	// check to see if we are defending the base's flag
	VectorSubtract(targ->r.currentOrigin, flag->r.currentOrigin, v1);
	VectorSubtract(attacker->r.currentOrigin, flag->r.currentOrigin, v2);

	if ( ( ( VectorLength(v1) < CTF_TARGET_PROTECT_RADIUS &&
		trap_InPVS(flag->r.currentOrigin, targ->r.currentOrigin ) ) ||
		( VectorLength(v2) < CTF_TARGET_PROTECT_RADIUS &&
		trap_InPVS(flag->r.currentOrigin, attacker->r.currentOrigin ) ) ) &&
		attacker->client->sess.sessionTeam != targ->client->sess.sessionTeam) {

		// we defended the base flag
		AddScore(attacker, targ->r.currentOrigin, CTF_FLAG_DEFENSE_BONUS);
		attacker->client->pers.teamState.basedefense++;

		attacker->client->ps.persistant[PERS_DEFEND_COUNT]++;
		// add the sprite over the player's head
		attacker->client->ps.eFlags &= ~(EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP );
		attacker->client->ps.eFlags |= EF_AWARD_DEFEND;
		attacker->client->rewardTime = level.time + REWARD_SPRITE_TIME;

		return;
	}

	if (carrier && carrier != attacker) {
		VectorSubtract(targ->r.currentOrigin, carrier->r.currentOrigin, v1);
		VectorSubtract(attacker->r.currentOrigin, carrier->r.currentOrigin, v1);

		if ( ( ( VectorLength(v1) < CTF_ATTACKER_PROTECT_RADIUS &&
			trap_InPVS(carrier->r.currentOrigin, targ->r.currentOrigin ) ) ||
			( VectorLength(v2) < CTF_ATTACKER_PROTECT_RADIUS &&
				trap_InPVS(carrier->r.currentOrigin, attacker->r.currentOrigin ) ) ) &&
			attacker->client->sess.sessionTeam != targ->client->sess.sessionTeam) {
			AddScore(attacker, targ->r.currentOrigin, CTF_CARRIER_PROTECT_BONUS);
			attacker->client->pers.teamState.carrierdefense++;

			attacker->client->ps.persistant[PERS_DEFEND_COUNT]++;
			// add the sprite over the player's head
			attacker->client->ps.eFlags &= ~(EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP );
			attacker->client->ps.eFlags |= EF_AWARD_DEFEND;
			attacker->client->rewardTime = level.time + REWARD_SPRITE_TIME;

			return;
		}
	}
}

/*
================
Team_CheckHurtCarrier

Check to see if attacker hurt the flag carrier.  Needed when handing out bonuses for assistance to flag
carrier defense.
================
*/
void Team_CheckHurtCarrier(gentity_t *targ, gentity_t *attacker)
{
	int flag_pw;

	if (!targ->client || !attacker->client)
		return;

	if (targ->client->sess.sessionTeam == TEAM_RED)
		flag_pw = PW_BLUEFLAG;
	else
		flag_pw = PW_REDFLAG;

	// flags
	if (targ->client->ps.powerups[flag_pw] &&
		targ->client->sess.sessionTeam != attacker->client->sess.sessionTeam)
		attacker->client->pers.teamState.lasthurtcarrier = level.time;

	// skulls
	if (targ->client->ps.generic1 &&
		targ->client->sess.sessionTeam != attacker->client->sess.sessionTeam)
		attacker->client->pers.teamState.lasthurtcarrier = level.time;
}


gentity_t *Team_ResetFlag( int team ) {
	char *c;
	gentity_t *ent, *rent = NULL;

	switch (team) {
	case TEAM_RED:
		c = "team_CTF_redflag";
		break;
	case TEAM_BLUE:
		c = "team_CTF_blueflag";
		break;
	case TEAM_FREE:
		c = "team_CTF_neutralflag";
		break;
	default:
		return NULL;
	}

	ent = NULL;
	while ((ent = G_Find (ent, FOFS(classname), c)) != NULL) {
		if (ent->flags & FL_DROPPED_ITEM)
			G_FreeEntity(ent);
		else {
			rent = ent;
			RespawnItem(ent);
			G_ClearDroppedFlagState( ent );
		}
	}

	Team_SetFlagStatus( team, FLAG_ATBASE );

	return rent;
}

void Team_ResetFlags( void ) {
	if( g_gametype.integer == GT_CTF ) {
		Team_ResetFlag( TEAM_RED );
		Team_ResetFlag( TEAM_BLUE );
	}
	else if( g_gametype.integer == GT_1FCTF ) {
		Team_ResetFlag( TEAM_FREE );
	}
}

void Team_ReturnFlagSound( gentity_t *ent, int team ) {
	gentity_t	*te;

	if (ent == NULL) {
		G_Printf ("Warning:  NULL passed to Team_ReturnFlagSound\n");
		return;
	}

	te = G_TempEntity( ent->s.pos.trBase, EV_GLOBAL_TEAM_SOUND );
	if( team == TEAM_BLUE ) {
		te->s.eventParm = GTS_RED_RETURN;
	}
	else {
		te->s.eventParm = GTS_BLUE_RETURN;
	}
	te->r.svFlags |= SVF_BROADCAST;
}

void Team_TakeFlagSound( gentity_t *ent, int team ) {
	gentity_t	*te;

	if (ent == NULL) {
		G_Printf ("Warning:  NULL passed to Team_TakeFlagSound\n");
		return;
	}

	// only play sound when the flag was at the base
	// or not picked up the last 10 seconds
	switch(team) {
		case TEAM_RED:
			if( teamgame.blueStatus != FLAG_ATBASE ) {
				if (teamgame.blueTakenTime > level.time - 10000)
					return;
			}
			teamgame.blueTakenTime = level.time;
			break;

		case TEAM_BLUE:	// CTF
			if( teamgame.redStatus != FLAG_ATBASE ) {
				if (teamgame.redTakenTime > level.time - 10000)
					return;
			}
			teamgame.redTakenTime = level.time;
			break;
	}

	te = G_TempEntity( ent->s.pos.trBase, EV_GLOBAL_TEAM_SOUND );
	if( team == TEAM_BLUE ) {
		te->s.eventParm = GTS_RED_TAKEN;
	}
	else {
		te->s.eventParm = GTS_BLUE_TAKEN;
	}
	te->r.svFlags |= SVF_BROADCAST;
}

void Team_CaptureFlagSound( gentity_t *ent, int team ) {
	gentity_t	*te;

	if (ent == NULL) {
		G_Printf ("Warning:  NULL passed to Team_CaptureFlagSound\n");
		return;
	}

	te = G_TempEntity( ent->s.pos.trBase, EV_GLOBAL_TEAM_SOUND );
	if( team == TEAM_BLUE ) {
		te->s.eventParm = GTS_BLUE_CAPTURE;
	}
	else {
		te->s.eventParm = GTS_RED_CAPTURE;
	}
	te->r.svFlags |= SVF_BROADCAST;
}

void Team_ReturnFlag( int team ) {
	Team_ReturnFlagSound(Team_ResetFlag(team), team);
	if( team == TEAM_FREE ) {
		PrintMsg(NULL, "The flag has returned!\n" );
	}
	else {
		PrintMsg(NULL, "The %s flag has returned!\n", TeamName(team));
	}
}

void Team_FreeEntity( gentity_t *ent ) {
	if( ent->item->giTag == PW_REDFLAG ) {
		Team_ReturnFlag( TEAM_RED );
	}
	else if( ent->item->giTag == PW_BLUEFLAG ) {
		Team_ReturnFlag( TEAM_BLUE );
	}
	else if( ent->item->giTag == PW_NEUTRALFLAG ) {
		Team_ReturnFlag( TEAM_FREE );
	}
}

/*
==============
Team_DroppedFlagThink

Automatically set in Launch_Item if the item is one of the flags

Flags are unique in that if they are dropped, the base flag must be respawned when they time out
==============
*/
void Team_DroppedFlagThink(gentity_t *ent) {
	int		team = TEAM_FREE;

	if ( ent->timestamp > level.time ) {
		ent->nextthink = ent->timestamp;
		return;
	}

	if( ent->item->giTag == PW_REDFLAG ) {
		team = TEAM_RED;
	}
	else if( ent->item->giTag == PW_BLUEFLAG ) {
		team = TEAM_BLUE;
	}
	else if( ent->item->giTag == PW_NEUTRALFLAG ) {
		team = TEAM_FREE;
	}

	Team_ReturnFlagSound( Team_ResetFlag( team ), team );
	// Reset Flag will delete this entity
}


/*
==============
Team_DroppedFlagThink
==============
*/
int Team_TouchOurFlag( gentity_t *ent, gentity_t *other, int team ) {
	int			i;
	gentity_t		*player;
	gclient_t		*cl;
	int			enemy_flag;
	qboolean		teammateTouch;
	qboolean		tackleReturn;

	cl = ( other && other->client ) ? other->client : NULL;
	if ( !cl ) {
		Team_SetFlagStatus( team, FLAG_ATBASE );
		return 0;
	}

	if( g_gametype.integer == GT_1FCTF ) {
		enemy_flag = PW_NEUTRALFLAG;
	}
	else {
		if ( cl->sess.sessionTeam == TEAM_RED ) {
			enemy_flag = PW_BLUEFLAG;
		} else {
			enemy_flag = PW_REDFLAG;
		}
	}

	teammateTouch = ( cl->sess.sessionTeam == team );
	tackleReturn = ( ent && ent->flagDroppedByEnemy && other && other->client && !teammateTouch && ent->flagDroppedByClientNum == other->s.number );

	if ( ent->flags & FL_DROPPED_ITEM ) {
		if ( ent->flagDroppedBySuicide && g_flagConfig.returnOnSuicide ) {
			Team_SetFlagStatus( team, FLAG_ATBASE );
			G_ClearDroppedFlagState( ent );
			return 0;
		}

		if ( tackleReturn ) {
			PrintMsg( NULL, "%s" S_COLOR_WHITE " forced the %s flag to return!\n",
				cl->pers.netname, TeamName( team ) );
			G_ClearDroppedFlagState( ent );
			Team_ReturnFlagSound( Team_ResetFlag( team ), team );
			return 0;
		}

		if ( !teammateTouch ) {
			return 0;
		}

		// hey, its not home.  return it by teleporting it back
		PrintMsg( NULL, "%s" S_COLOR_WHITE " returned the %s flag!\n",
				cl->pers.netname, TeamName(team));
		AddScore(other, ent->r.currentOrigin, CTF_RECOVERY_BONUS);
		if ( ent->flagDroppedByEnemy && g_flagConfig.droppedFlagBonus > 0 ) {
			AddScore( other, ent->r.currentOrigin, g_flagConfig.droppedFlagBonus );
		}
		other->client->pers.teamState.flagrecovery++;
		other->client->pers.teamState.lastreturnedflag = level.time;
		G_ClearDroppedFlagState( ent );
		//ResetFlag will remove this entity!  We must return zero
		Team_ReturnFlagSound(Team_ResetFlag(team), team);
		return 0;
	}

	// the flag is at home base.  if the player has the enemy
	// flag, he's just won!
	if (!cl->ps.powerups[enemy_flag])
		return 0; // We don't have the flag
	if( g_gametype.integer == GT_1FCTF ) {
		PrintMsg( NULL, "%s" S_COLOR_WHITE " captured the flag!\n", cl->pers.netname );
	}
	else {
		PrintMsg( NULL, "%s" S_COLOR_WHITE " captured the %s flag!\n", cl->pers.netname, TeamName(OtherTeam(team)));
	}

	cl->ps.powerups[enemy_flag] = 0;

	teamgame.last_flag_capture = level.time;
	teamgame.last_capture_team = team;

	// Increase the team's score
	AddTeamScore(ent->s.pos.trBase, other->client->sess.sessionTeam, 1);
	Team_ForceGesture(other->client->sess.sessionTeam);

	other->client->pers.teamState.captures++;
	// add the sprite over the player's head
	other->client->ps.eFlags &= ~(EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP );
	other->client->ps.eFlags |= EF_AWARD_CAP;
	other->client->rewardTime = level.time + REWARD_SPRITE_TIME;
	other->client->ps.persistant[PERS_CAPTURES]++;

	// other gets another 10 frag bonus
	AddScore(other, ent->r.currentOrigin, CTF_CAPTURE_BONUS);
	G_ADAwardBonus( other, ent->r.currentOrigin, g_adCaptureScoreBonus.integer, S_COLOR_GREEN "Capture bonus" );

	Team_CaptureFlagSound( ent, team );

	// Ok, let's do the player loop, hand out the bonuses
	for (i = 0; i < g_maxclients.integer; i++) {
		player = &g_entities[i];
		if (!player->inuse)
			continue;

		if (player->client->sess.sessionTeam !=
			cl->sess.sessionTeam) {
			player->client->pers.teamState.lasthurtcarrier = -5;
		} else if (player->client->sess.sessionTeam ==
			cl->sess.sessionTeam) {
			if (player != other)
				AddScore(player, ent->r.currentOrigin, CTF_TEAM_BONUS);
			// award extra points for capture assists
			if (player->client->pers.teamState.lastreturnedflag +
				CTF_RETURN_FLAG_ASSIST_TIMEOUT > level.time) {
				AddScore (player, ent->r.currentOrigin, CTF_RETURN_FLAG_ASSIST_BONUS);
				other->client->pers.teamState.assists++;

				player->client->ps.persistant[PERS_ASSIST_COUNT]++;
				// add the sprite over the player's head
				player->client->ps.eFlags &= ~(EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP );
				player->client->ps.eFlags |= EF_AWARD_ASSIST;
				player->client->rewardTime = level.time + REWARD_SPRITE_TIME;

			} else if (player->client->pers.teamState.lastfraggedcarrier +
				CTF_FRAG_CARRIER_ASSIST_TIMEOUT > level.time) {
				AddScore(player, ent->r.currentOrigin, CTF_FRAG_CARRIER_ASSIST_BONUS);
				other->client->pers.teamState.assists++;
				player->client->ps.persistant[PERS_ASSIST_COUNT]++;
				// add the sprite over the player's head
				player->client->ps.eFlags &= ~(EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP );
				player->client->ps.eFlags |= EF_AWARD_ASSIST;
				player->client->rewardTime = level.time + REWARD_SPRITE_TIME;
			}
		}
	}
	Team_ResetFlags();

	CalculateRanks();

	return 0; // Do not respawn this automatically
}

int Team_TouchEnemyFlag( gentity_t *ent, gentity_t *other, int team ) {
	gclient_t *cl = other->client;

	if( g_gametype.integer == GT_1FCTF ) {
		PrintMsg (NULL, "%s" S_COLOR_WHITE " got the flag!\n", other->client->pers.netname );

		cl->ps.powerups[PW_NEUTRALFLAG] = INT_MAX; // flags never expire

		if( team == TEAM_RED ) {
			Team_SetFlagStatus( TEAM_FREE, FLAG_TAKEN_RED );
		}
		else {
			Team_SetFlagStatus( TEAM_FREE, FLAG_TAKEN_BLUE );
		}
	}
	else{
		PrintMsg (NULL, "%s" S_COLOR_WHITE " got the %s flag!\n",
			other->client->pers.netname, TeamName(team));

		if (team == TEAM_RED)
			cl->ps.powerups[PW_REDFLAG] = INT_MAX; // flags never expire
		else
			cl->ps.powerups[PW_BLUEFLAG] = INT_MAX; // flags never expire

		Team_SetFlagStatus( team, FLAG_TAKEN );
	}

	AddScore(other, ent->r.currentOrigin, CTF_FLAG_BONUS);
	G_ADAwardBonus( other, ent->r.currentOrigin, g_adTouchScoreBonus.integer, S_COLOR_CYAN "Touch bonus" );
	cl->pers.teamState.flagsince = level.time;
	Team_TakeFlagSound( ent, team );

	return -1; // Do not respawn this automatically, but do delete it if it was FL_DROPPED
}

int Pickup_Team( gentity_t *ent, gentity_t *other ) {
	int team;
	gclient_t *cl = other->client;

	if( g_gametype.integer == GT_OBELISK ) {
		// there are no team items that can be picked up in obelisk
		G_FreeEntity( ent );
		return 0;
	}

	if( g_gametype.integer == GT_HARVESTER ) {
		// the only team items that can be picked up in harvester are the cubes
		if( ent->spawnflags != cl->sess.sessionTeam ) {
			cl->ps.generic1 += 1;
		}
		G_FreeEntity( ent );
		return 0;
	}
	// figure out what team this flag is
	if( strcmp(ent->classname, "team_CTF_redflag") == 0 ) {
		team = TEAM_RED;
	}
	else if( strcmp(ent->classname, "team_CTF_blueflag") == 0 ) {
		team = TEAM_BLUE;
	}
	else if( strcmp(ent->classname, "team_CTF_neutralflag") == 0  ) {
		team = TEAM_FREE;
	}
	else {
		PrintMsg ( other, "Don't know what team the flag is on.\n");
		return 0;
	}
	if( g_gametype.integer == GT_1FCTF ) {
		if( team == TEAM_FREE ) {
			return Team_TouchEnemyFlag( ent, other, cl->sess.sessionTeam );
		}
		if( team != cl->sess.sessionTeam) {
			return Team_TouchOurFlag( ent, other, cl->sess.sessionTeam );
		}
		return 0;
	}
	// GT_CTF
	if( team == cl->sess.sessionTeam) {
		return Team_TouchOurFlag( ent, other, team );
	}
	return Team_TouchEnemyFlag( ent, other, team );
}

/*
===========
Team_GetLocation

Report a location for the player. Uses placed nearby target_location entities
============
*/
gentity_t *Team_GetLocation(gentity_t *ent)
{
	gentity_t		*eloc, *best;
	float			bestlen, len;
	vec3_t			origin;

	best = NULL;
	bestlen = 3*8192.0*8192.0;

	VectorCopy( ent->r.currentOrigin, origin );

	for (eloc = level.locationHead; eloc; eloc = eloc->nextTrain) {
		len = ( origin[0] - eloc->r.currentOrigin[0] ) * ( origin[0] - eloc->r.currentOrigin[0] )
			+ ( origin[1] - eloc->r.currentOrigin[1] ) * ( origin[1] - eloc->r.currentOrigin[1] )
			+ ( origin[2] - eloc->r.currentOrigin[2] ) * ( origin[2] - eloc->r.currentOrigin[2] );

		if ( len > bestlen ) {
			continue;
		}

		if ( !trap_InPVS( origin, eloc->r.currentOrigin ) ) {
			continue;
		}

		bestlen = len;
		best = eloc;
	}

	return best;
}


/*
===========
Team_GetLocation

Report a location for the player. Uses placed nearby target_location entities
============
*/
qboolean Team_GetLocationMsg(gentity_t *ent, char *loc, int loclen)
{
	gentity_t *best;

	best = Team_GetLocation( ent );
	
	if (!best)
		return qfalse;

	if (best->count) {
		if (best->count < 0)
			best->count = 0;
		if (best->count > 7)
			best->count = 7;
		Com_sprintf(loc, loclen, "%c%c%s" S_COLOR_WHITE, Q_COLOR_ESCAPE, best->count + '0', best->message );
	} else
		Com_sprintf(loc, loclen, "%s", best->message);

	return qtrue;
}


/*---------------------------------------------------------------------------*/

/*
================
SelectRandomDeathmatchSpawnPoint

go to a random point that doesn't telefrag
================
*/
#define	MAX_TEAM_SPAWN_POINTS	32
gentity_t *SelectRandomTeamSpawnPoint( int teamstate, team_t team ) {
	gentity_t	*spot;
	int			count;
	int			selection;
	gentity_t	*spots[MAX_TEAM_SPAWN_POINTS];
	char		*classname;

	if (teamstate == TEAM_BEGIN) {
		if (team == TEAM_RED)
			classname = "team_CTF_redplayer";
		else if (team == TEAM_BLUE)
			classname = "team_CTF_blueplayer";
		else
			return NULL;
	} else {
		if (team == TEAM_RED)
			classname = "team_CTF_redspawn";
		else if (team == TEAM_BLUE)
			classname = "team_CTF_bluespawn";
		else
			return NULL;
	}
	count = 0;

	spot = NULL;

	while ((spot = G_Find (spot, FOFS(classname), classname)) != NULL) {
		if ( SpotWouldTelefrag( spot ) ) {
			continue;
		}
		spots[ count ] = spot;
		if (++count == MAX_TEAM_SPAWN_POINTS)
			break;
	}

	if ( !count ) {	// no spots that won't telefrag
		return G_Find( NULL, FOFS(classname), classname);
	}

	selection = rand() % count;
	return spots[ selection ];
}


/*
===========
SelectCTFSpawnPoint

============
*/
gentity_t *SelectCTFSpawnPoint ( team_t team, int teamstate, vec3_t origin, vec3_t angles ) {
	gentity_t	*spot;

	spot = SelectRandomTeamSpawnPoint ( teamstate, team );

	if (!spot) {
		return SelectSpawnPoint( vec3_origin, origin, angles );
	}

	VectorCopy (spot->s.origin, origin);
	origin[2] += 9;
	VectorCopy (spot->s.angles, angles);

	return spot;
}

/*---------------------------------------------------------------------------*/

static int QDECL SortClients( const void *a, const void *b ) {
	return *(int *)a - *(int *)b;
}


/*
==================
TeamplayLocationsMessage

Format:
	clientNum location health armor weapon powerups

==================
*/
void TeamplayInfoMessage( gentity_t *ent ) {
	char		entry[1024];
	char		string[8192];
	int			stringlength;
	int			i, j;
	gentity_t	*player;
	int			cnt;
	int			h, a;
	int			clients[TEAM_MAXOVERLAY];

	if ( ! ent->client->pers.teamInfo )
		return;

	// figure out what client should be on the display
	// we are limited to 8, but we want to use the top eight players
	// but in client order (so they don't keep changing position on the overlay)
	for (i = 0, cnt = 0; i < g_maxclients.integer && cnt < TEAM_MAXOVERLAY; i++) {
		player = g_entities + level.sortedClients[i];
		if (player->inuse && player->client->sess.sessionTeam == 
			ent->client->sess.sessionTeam ) {
			clients[cnt++] = level.sortedClients[i];
		}
	}

	// We have the top eight players, sort them by clientNum
	qsort( clients, cnt, sizeof( clients[0] ), SortClients );

	// send the latest information on all clients
	string[0] = 0;
	stringlength = 0;

	for (i = 0, cnt = 0; i < g_maxclients.integer && cnt < TEAM_MAXOVERLAY; i++) {
		player = g_entities + i;
		if (player->inuse && player->client->sess.sessionTeam == 
			ent->client->sess.sessionTeam ) {

			h = player->client->ps.stats[STAT_HEALTH];
			a = player->client->ps.stats[STAT_ARMOR];
			if (h < 0) h = 0;
			if (a < 0) a = 0;

			Com_sprintf (entry, sizeof(entry),
				" %i %i %i %i %i %i", 
//				level.sortedClients[i], player->client->pers.teamState.location, h, a, 
				i, player->client->pers.teamState.location, h, a, 
				player->client->ps.weapon, player->s.powerups);
			j = strlen(entry);
			if (stringlength + j > sizeof(string))
				break;
			strcpy (string + stringlength, entry);
			stringlength += j;
			cnt++;
		}
	}

	trap_SendServerCommand( ent-g_entities, va("tinfo %i %s", cnt, string) );
}

void CheckTeamStatus(void) {
	int i;
	gentity_t *loc, *ent;

	if (level.time - level.lastTeamLocationTime > TEAM_LOCATION_UPDATE_TIME) {

		level.lastTeamLocationTime = level.time;

		for (i = 0; i < g_maxclients.integer; i++) {
			ent = g_entities + i;

			if ( ent->client->pers.connected != CON_CONNECTED ) {
				continue;
			}

			if (ent->inuse && (ent->client->sess.sessionTeam == TEAM_RED ||	ent->client->sess.sessionTeam == TEAM_BLUE)) {
				loc = Team_GetLocation( ent );
				if (loc)
					ent->client->pers.teamState.location = loc->health;
				else
					ent->client->pers.teamState.location = 0;
			}
		}

		for (i = 0; i < g_maxclients.integer; i++) {
			ent = g_entities + i;

			if ( ent->client->pers.connected != CON_CONNECTED ) {
				continue;
			}

			if (ent->inuse && (ent->client->sess.sessionTeam == TEAM_RED ||	ent->client->sess.sessionTeam == TEAM_BLUE)) {
				TeamplayInfoMessage( ent );
			}
		}
	}
}

/*-----------------------------------------------------------------*/

/*QUAKED team_CTF_redplayer (1 0 0) (-16 -16 -16) (16 16 32)
Only in CTF games.  Red players spawn here at game start.
*/
void SP_team_CTF_redplayer( gentity_t *ent ) {
}


/*QUAKED team_CTF_blueplayer (0 0 1) (-16 -16 -16) (16 16 32)
Only in CTF games.  Blue players spawn here at game start.
*/
void SP_team_CTF_blueplayer( gentity_t *ent ) {
}


/*QUAKED team_CTF_redspawn (1 0 0) (-16 -16 -24) (16 16 32)
potential spawning position for red team in CTF games.
Targets will be fired when someone spawns in on them.
*/
void SP_team_CTF_redspawn(gentity_t *ent) {
}

/*QUAKED team_CTF_bluespawn (0 0 1) (-16 -16 -24) (16 16 32)
potential spawning position for blue team in CTF games.
Targets will be fired when someone spawns in on them.
*/
void SP_team_CTF_bluespawn(gentity_t *ent) {
}


/*
================
Obelisks
================
*/

static void ObeliskRegen( gentity_t *self ) {
	self->nextthink = level.time + g_obeliskRegenPeriod.integer * 1000;
	if( self->health >= g_obeliskHealth.integer ) {
		return;
	}

	G_AddEvent( self, EV_POWERUP_REGEN, 0 );
	self->health += g_obeliskRegenAmount.integer;
	if ( self->health > g_obeliskHealth.integer ) {
		self->health = g_obeliskHealth.integer;
	}

	self->activator->s.modelindex2 = self->health * 0xff / g_obeliskHealth.integer;
	self->activator->s.frame = 0;
}


static void ObeliskRespawn( gentity_t *self ) {
	self->takedamage = qtrue;
	self->health = g_obeliskHealth.integer;

	self->think = ObeliskRegen;
	self->nextthink = level.time + g_obeliskRegenPeriod.integer * 1000;

	self->activator->s.frame = 0;
}


static void ObeliskDie( gentity_t *self, gentity_t *inflictor, gentity_t *attacker, int damage, int mod ) {
	int			otherTeam;

	otherTeam = OtherTeam( self->spawnflags );
	AddTeamScore(self->s.pos.trBase, otherTeam, 1);
	Team_ForceGesture(otherTeam);

	CalculateRanks();

	self->takedamage = qfalse;
	self->think = ObeliskRespawn;
	self->nextthink = level.time + g_obeliskRespawnDelay.integer * 1000;

	self->activator->s.modelindex2 = 0xff;
	self->activator->s.frame = 2;

	G_AddEvent( self->activator, EV_OBELISKEXPLODE, 0 );

	AddScore(attacker, self->r.currentOrigin, CTF_CAPTURE_BONUS);

	// add the sprite over the player's head
	attacker->client->ps.eFlags &= ~(EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP );
	attacker->client->ps.eFlags |= EF_AWARD_CAP;
	attacker->client->rewardTime = level.time + REWARD_SPRITE_TIME;
	attacker->client->ps.persistant[PERS_CAPTURES]++;

	teamgame.redObeliskAttackedTime = 0;
	teamgame.blueObeliskAttackedTime = 0;
}


static void ObeliskTouch( gentity_t *self, gentity_t *other, trace_t *trace ) {
	int			tokens;

	if ( !other->client ) {
		return;
	}

	if ( OtherTeam(other->client->sess.sessionTeam) != self->spawnflags ) {
		return;
	}

	tokens = other->client->ps.generic1;
	if( tokens <= 0 ) {
		return;
	}

	PrintMsg(NULL, "%s" S_COLOR_WHITE " brought in %i skull%s.\n",
					other->client->pers.netname, tokens, tokens ? "s" : "" );

	AddTeamScore(self->s.pos.trBase, other->client->sess.sessionTeam, tokens);
	Team_ForceGesture(other->client->sess.sessionTeam);

	AddScore(other, self->r.currentOrigin, CTF_CAPTURE_BONUS*tokens);

	// add the sprite over the player's head
	other->client->ps.eFlags &= ~(EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP );
	other->client->ps.eFlags |= EF_AWARD_CAP;
	other->client->rewardTime = level.time + REWARD_SPRITE_TIME;
	other->client->ps.persistant[PERS_CAPTURES] += tokens;
	
	other->client->ps.generic1 = 0;
	CalculateRanks();

	Team_CaptureFlagSound( self, self->spawnflags );
}

static void ObeliskPain( gentity_t *self, gentity_t *attacker, int damage ) {
	int actualDamage = damage / 10;
	if (actualDamage <= 0) {
		actualDamage = 1;
	}
	self->activator->s.modelindex2 = self->health * 0xff / g_obeliskHealth.integer;
	if (!self->activator->s.frame) {
		G_AddEvent(self, EV_OBELISKPAIN, 0);
	}
	self->activator->s.frame = 1;
	AddScore(attacker, self->r.currentOrigin, actualDamage);
}

gentity_t *SpawnObelisk( vec3_t origin, int team, int spawnflags) {
	trace_t		tr;
	vec3_t		dest;
	gentity_t	*ent;

	ent = G_Spawn();

	VectorCopy( origin, ent->s.origin );
	VectorCopy( origin, ent->s.pos.trBase );
	VectorCopy( origin, ent->r.currentOrigin );

	VectorSet( ent->r.mins, -15, -15, 0 );
	VectorSet( ent->r.maxs, 15, 15, 87 );

	ent->s.eType = ET_GENERAL;
	ent->flags = FL_NO_KNOCKBACK;

	if( g_gametype.integer == GT_OBELISK ) {
		ent->r.contents = CONTENTS_SOLID;
		ent->takedamage = qtrue;
		ent->health = g_obeliskHealth.integer;
		ent->die = ObeliskDie;
		ent->pain = ObeliskPain;
		ent->think = ObeliskRegen;
		ent->nextthink = level.time + g_obeliskRegenPeriod.integer * 1000;
	}
	if( g_gametype.integer == GT_HARVESTER ) {
		ent->r.contents = CONTENTS_TRIGGER;
		ent->touch = ObeliskTouch;
	}

	if ( spawnflags & 1 ) {
		// suspended
		G_SetOrigin( ent, ent->s.origin );
	} else {
		// mappers like to put them exactly on the floor, but being coplanar
		// will sometimes show up as starting in solid, so lif it up one pixel
		ent->s.origin[2] += 1;

		// drop to floor
		VectorSet( dest, ent->s.origin[0], ent->s.origin[1], ent->s.origin[2] - 4096 );
		trap_Trace( &tr, ent->s.origin, ent->r.mins, ent->r.maxs, dest, ent->s.number, MASK_SOLID );
		if ( tr.startsolid ) {
			ent->s.origin[2] -= 1;
			G_Printf( "SpawnObelisk: %s startsolid at %s\n", ent->classname, vtos(ent->s.origin) );

			ent->s.groundEntityNum = ENTITYNUM_NONE;
			G_SetOrigin( ent, ent->s.origin );
		}
		else {
			// allow to ride movers
			ent->s.groundEntityNum = tr.entityNum;
			G_SetOrigin( ent, tr.endpos );
		}
	}

	ent->spawnflags = team;

	trap_LinkEntity( ent );

	return ent;
}

/*QUAKED team_redobelisk (1 0 0) (-16 -16 0) (16 16 8)
*/
void SP_team_redobelisk( gentity_t *ent ) {
	gentity_t *obelisk;

	if ( g_gametype.integer <= GT_TEAM ) {
		G_FreeEntity(ent);
		return;
	}
	ent->s.eType = ET_TEAM;
	if ( g_gametype.integer == GT_OBELISK ) {
		obelisk = SpawnObelisk( ent->s.origin, TEAM_RED, ent->spawnflags );
		obelisk->activator = ent;
		// initial obelisk health value
		ent->s.modelindex2 = 0xff;
		ent->s.frame = 0;
	}
	if ( g_gametype.integer == GT_HARVESTER ) {
		obelisk = SpawnObelisk( ent->s.origin, TEAM_RED, ent->spawnflags );
		obelisk->activator = ent;
	}
	ent->s.modelindex = TEAM_RED;
	trap_LinkEntity(ent);
}

/*QUAKED team_blueobelisk (0 0 1) (-16 -16 0) (16 16 88)
*/
void SP_team_blueobelisk( gentity_t *ent ) {
	gentity_t *obelisk;

	if ( g_gametype.integer <= GT_TEAM ) {
		G_FreeEntity(ent);
		return;
	}
	ent->s.eType = ET_TEAM;
	if ( g_gametype.integer == GT_OBELISK ) {
		obelisk = SpawnObelisk( ent->s.origin, TEAM_BLUE, ent->spawnflags );
		obelisk->activator = ent;
		// initial obelisk health value
		ent->s.modelindex2 = 0xff;
		ent->s.frame = 0;
	}
	if ( g_gametype.integer == GT_HARVESTER ) {
		obelisk = SpawnObelisk( ent->s.origin, TEAM_BLUE, ent->spawnflags );
		obelisk->activator = ent;
	}
	ent->s.modelindex = TEAM_BLUE;
	trap_LinkEntity(ent);
}

/*QUAKED team_neutralobelisk (0 0 1) (-16 -16 0) (16 16 88)
*/
void SP_team_neutralobelisk( gentity_t *ent ) {
	if ( g_gametype.integer != GT_1FCTF && g_gametype.integer != GT_HARVESTER ) {
		G_FreeEntity(ent);
		return;
	}
	ent->s.eType = ET_TEAM;
	if ( g_gametype.integer == GT_HARVESTER) {
		neutralObelisk = SpawnObelisk( ent->s.origin, TEAM_FREE, ent->spawnflags);
		neutralObelisk->spawnflags = TEAM_FREE;
	}
	ent->s.modelindex = TEAM_FREE;
	trap_LinkEntity(ent);
}


/*
================
CheckObeliskAttack
================
*/
qboolean CheckObeliskAttack( gentity_t *obelisk, gentity_t *attacker ) {
	gentity_t	*te;

	// if this really is an obelisk
	if( obelisk->die != ObeliskDie ) {
		return qfalse;
	}

	// if the attacker is a client
	if( !attacker->client ) {
		return qfalse;
	}

	// if the obelisk is on the same team as the attacker then don't hurt it
	if( obelisk->spawnflags == attacker->client->sess.sessionTeam ) {
		return qtrue;
	}

	// obelisk may be hurt

	// if not played any sounds recently
	if ((obelisk->spawnflags == TEAM_RED &&
		teamgame.redObeliskAttackedTime < level.time - OVERLOAD_ATTACK_BASE_SOUND_TIME) ||
		(obelisk->spawnflags == TEAM_BLUE &&
		teamgame.blueObeliskAttackedTime < level.time - OVERLOAD_ATTACK_BASE_SOUND_TIME) ) {

		// tell which obelisk is under attack
		te = G_TempEntity( obelisk->s.pos.trBase, EV_GLOBAL_TEAM_SOUND );
		if( obelisk->spawnflags == TEAM_RED ) {
			te->s.eventParm = GTS_REDOBELISK_ATTACKED;
			teamgame.redObeliskAttackedTime = level.time;
		}
		else {
			te->s.eventParm = GTS_BLUEOBELISK_ATTACKED;
			teamgame.blueObeliskAttackedTime = level.time;
		}
		te->r.svFlags |= SVF_BROADCAST;
	}

	return qfalse;
}
