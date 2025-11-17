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

#include "g_local.h"

static char g_raceScores[MAX_STRING_CHARS];
static char g_raceInfo[MAX_STRING_CHARS];

static void G_RaceUpdateInfoConfigString( void );

/*
=============
G_RacePrintMessage

Sends a print message to a specific client or the server console when ent is NULL.
=============
*/
static void G_RacePrintMessage( gentity_t *ent, const char *message ) {
	if ( !message || !*message ) {
		return;
	}

	if ( ent && ent->client ) {
		trap_SendServerCommand( ent - g_entities, va( "print \"%s\"", message ) );
		return;
	}

	G_Printf( "%s", message );
}

/*
=============
G_RaceDropPointToFloor

Drops a checkpoint to the ground and reports startsolid errors.
=============
*/
static qboolean G_RaceDropPointToFloor( gentity_t *ent ) {
	trace_t	tr;
	vec3_t	dest;

	if ( !ent ) {
		return qfalse;
	}

	if ( ent->spawnflags & 1 ) {
		G_SetOrigin( ent, ent->s.origin );
		return qtrue;
	}

	VectorSet( dest, ent->s.origin[0], ent->s.origin[1], ent->s.origin[2] - 4096 );
	trap_Trace( &tr, ent->s.origin, ent->r.mins, ent->r.maxs, dest, ent->s.number, MASK_SOLID );
	if ( tr.startsolid ) {
		G_Printf( "SP_race_point: startsolid at %s\n", vtos( ent->s.origin ) );
		G_FreeEntity( ent );
		return qfalse;
	}

	ent->s.groundEntityNum = tr.entityNum;
	G_SetOrigin( ent, tr.endpos );
	return qtrue;
}

/*
=============
G_RaceCachePointMetadata

Persists origin and target metadata for a checkpoint.
=============
*/
static void G_RaceCachePointMetadata( gentity_t *ent ) {
	racePointInfo_t	*info;

	if ( !ent || ent->racePointIndex < 0 || ent->racePointIndex >= MAX_RACE_POINTS ) {
		return;
	}

	info = &level.racePointInfo[ent->racePointIndex];
	memset( info, 0, sizeof( *info ) );
	info->inUse = qtrue;
	info->adminSpawned = ent->racePointAdminSpawned;
	VectorCopy( ent->s.origin, info->origin );
	if ( ent->target ) {
		Q_strncpyz( info->target, ent->target, sizeof( info->target ) );
	}
	if ( ent->targetname ) {
		Q_strncpyz( info->targetname, ent->targetname, sizeof( info->targetname ) );
	}
}

/*
=============
G_RaceSendPointMetadataCommand

Broadcasts the admin_race_point_%i payload for a specific checkpoint index.
=============
*/
qboolean G_RaceSendPointMetadataCommand( int clientNum, int index ) {
	racePointInfo_t	*info;
	const char	*target;
	const char	*targetname;

	if ( index < 0 || index >= MAX_RACE_POINTS ) {
		return qfalse;
	}

	info = &level.racePointInfo[index];
	if ( !info->inUse ) {
		return qfalse;
	}

	target = ( info->target[0] ) ? info->target : "-";
	targetname = ( info->targetname[0] ) ? info->targetname : "-";
	trap_SendServerCommand( clientNum, va( "admin_race_point_%i %.2f %.2f %.2f %s %s",
		index, info->origin[0], info->origin[1], info->origin[2], target, targetname ) );
	return qtrue;
}

/*
=============
G_RaceBroadcastInitCommand

Sends race_init followed by metadata for each checkpoint.
=============
*/
void G_RaceBroadcastInitCommand( int clientNum ) {
	int	count;
	int	i;

	count = level.racePointCount;
	if ( count < 0 ) {
		count = 0;
	}
	if ( count > MAX_RACE_POINTS ) {
		count = MAX_RACE_POINTS;
	}

	trap_SendServerCommand( clientNum, va( "race_init %i", level.racePointCount ) );
	for ( i = 0; i < count; i++ ) {
		if ( level.racePointInfo[i].inUse ) {
			G_RaceSendPointMetadataCommand( clientNum, i );
		}
	}
}

/*
=============
G_RaceSendInfoCommand

Flushes the race_info payload to a specific client.
=============
*/
void G_RaceSendInfoCommand( int clientNum ) {
	G_RaceUpdateInfoConfigString();
	trap_SendServerCommand( clientNum, g_raceInfo );
}

/*
=============
G_RaceFormatMilliseconds

Formats a millisecond duration into a mm:ss.mmm string.
=============
*/
static void G_RaceFormatMilliseconds( int milliseconds, char *buffer, size_t bufferSize ) {
	int minutes;
	int seconds;
	int ms;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	if ( milliseconds < 0 ) {
		Q_strncpyz( buffer, "0:00.000", bufferSize );
		return;
	}

	minutes = milliseconds / 60000;
	seconds = ( milliseconds % 60000 ) / 1000;
	ms = milliseconds % 1000;
	Com_sprintf( buffer, bufferSize, "%d:%02d.%03d", minutes, seconds, ms );
}

/*
=============
G_RaceClearClientRunState

Stops any in-progress run for the provided client.
=============
*/
static void G_RaceClearClientRunState( gclient_t *client ) {
	if ( !client ) {
		return;
	}

	client->raceState.active = qfalse;
	client->raceState.startTime = 0;
	client->raceState.nextCheckpoint = 0;
	memset( client->raceState.currentSplits, 0, sizeof( client->raceState.currentSplits ) );
}

/*
=============
G_RaceResetClient

Initializes a client's race bookkeeping and clears any run state.
=============
*/
static void G_RaceResetClient( gclient_t *client ) {
	if ( !client ) {
		return;
	}

	if ( !client->raceState.initialized ) {
		client->raceState.initialized = qtrue;
		client->raceState.bestTime = RACE_INVALID_TIME;
		client->raceState.lastFinishTime = -1;
		memset( client->raceState.bestSplits, 0, sizeof( client->raceState.bestSplits ) );
	}

	G_RaceClearClientRunState( client );
}

/*
=============
G_RaceCompareClients

qsort comparator used for building the race scoreboard.
=============
*/
static int G_RaceCompareClients( const void *a, const void *b ) {
	const int left = *(const int *)a;
	const int right = *(const int *)b;
	const gclient_t *leftClient = &level.clients[left];
	const gclient_t *rightClient = &level.clients[right];
	int leftTime;
	int rightTime;

	leftTime = leftClient->raceState.bestTime;
	rightTime = rightClient->raceState.bestTime;

	if ( leftTime == RACE_INVALID_TIME && rightTime == RACE_INVALID_TIME ) {
		return left - right;
	}

	if ( leftTime == RACE_INVALID_TIME ) {
		return 1;
	}

	if ( rightTime == RACE_INVALID_TIME ) {
		return -1;
	}

	if ( leftTime != rightTime ) {
		return leftTime - rightTime;
	}

	return left - right;
}

/*
=============
G_RaceBuildScoreString

Regenerates the race scoreboard command and updates the configstring.
=============
*/
static void G_RaceBuildScoreString( void ) {
	char buffer[MAX_STRING_CHARS];
	char entry[64];
	int indices[MAX_CLIENTS];
	int count;
	int i;

	buffer[0] = '\0';
	count = 0;

	for ( i = 0; i < level.maxclients; ++i ) {
		if ( level.clients[i].pers.connected != CON_CONNECTED ) {
			continue;
		}
		indices[count++] = i;
	}

	if ( count > 1 ) {
		qsort( indices, count, sizeof( indices[0] ), G_RaceCompareClients );
	}

	for ( i = 0; i < count; ++i ) {
		gclient_t *client;
		int bestTime;
		int lastTime;
		int currentElapsed;

		client = &level.clients[indices[i]];
		bestTime = ( client->raceState.bestTime == RACE_INVALID_TIME ) ? -1 : client->raceState.bestTime;
		lastTime = client->raceState.lastFinishTime;
		currentElapsed = client->raceState.active ? ( level.time - client->raceState.startTime ) : -1;
		Com_sprintf( entry, sizeof( entry ), " %i %i %i %i", indices[i], bestTime, lastTime, currentElapsed );
		if ( strlen( buffer ) + strlen( entry ) >= sizeof( buffer ) ) {
			break;
		}
		Q_strcat( buffer, sizeof( buffer ), entry );
	}

	Com_sprintf( g_raceScores, sizeof( g_raceScores ), "scores_race %i%s", count, buffer );
	trap_SetConfigstring( CS_RACE_SCORES, g_raceScores );
}

/*
=============
G_RaceFindLeader

Returns the client pointer for the player with the best recorded time.
=============
*/
static gclient_t *G_RaceFindLeader( void ) {
	gclient_t *leader;
	int i;

	leader = NULL;
	for ( i = 0; i < level.maxclients; ++i ) {
		gclient_t *client = &level.clients[i];

		if ( client->pers.connected != CON_CONNECTED ) {
			continue;
		}

		if ( client->raceState.bestTime == RACE_INVALID_TIME ) {
			continue;
		}

		if ( !leader || client->raceState.bestTime < leader->raceState.bestTime ) {
			leader = client;
		}
	}

	return leader;
}

/*
=============
G_RaceUpdateInfoConfigString

Updates the race_info configstring so clients know checkpoint counts and best splits.
=============
*/
static void G_RaceUpdateInfoConfigString( void ) {
	char buffer[MAX_STRING_CHARS];
	char entry[32];
	gclient_t *leader;
	int i;

	buffer[0] = '\0';
	leader = G_RaceFindLeader();

	if ( leader && leader->raceState.bestTime != RACE_INVALID_TIME ) {
		for ( i = 0; i < level.racePointCount && i < MAX_RACE_POINTS; ++i ) {
			int split = leader->raceState.bestSplits[i];

			Com_sprintf( entry, sizeof( entry ), " %i", split );
			if ( strlen( buffer ) + strlen( entry ) >= sizeof( buffer ) ) {
				break;
			}
			Q_strcat( buffer, sizeof( buffer ), entry );
		}
	}

	Com_sprintf( g_raceInfo, sizeof( g_raceInfo ), "race_info %i%s", level.racePointCount, buffer );
	trap_SetConfigstring( CS_RACE_INFO, g_raceInfo );
}

/*
=============
G_RaceUpdateConfigstrings

Refreshes both race configstrings.
=============
*/
static void G_RaceUpdateConfigstrings( void ) {
	G_RaceBuildScoreString();
	G_RaceUpdateInfoConfigString();
}

/*
=============
G_RaceStartRun

Begins a new race attempt for the provided player.
=============
*/
static void G_RaceStartRun( gentity_t *player ) {
	gclient_t *client;

	if ( !player || !player->client ) {
		return;
	}

	client = player->client;
	G_RaceClearClientRunState( client );
	client->raceState.active = qtrue;
	client->raceState.startTime = level.time;
	client->raceState.nextCheckpoint = 1;
	client->raceState.lastFinishTime = -1;
	client->raceState.currentSplits[0] = 0;
}

/*
=============
G_RaceAnnounceFinish

Prints the completion message for a race attempt.
=============
*/
static void G_RaceAnnounceFinish( gentity_t *player, int elapsed, qboolean personalBest ) {
	char timeBuffer[32];
	char message[MAX_STRING_CHARS];
	const char *format;

	if ( !player || !player->client ) {
		return;
	}

	G_RaceFormatMilliseconds( elapsed, timeBuffer, sizeof( timeBuffer ) );
	format = personalBest ? "^1Personal best! ^7%s^7 finished the race in %s\n" : "%s finished the race in %s\n";
	Com_sprintf( message, sizeof( message ), format, player->client->pers.netname, timeBuffer );
	trap_SendServerCommand( -1, va( "print \"%s\"", message ) );
}

/*
=============
G_RaceFinishRun

Handles the bookkeeping associated with completing the final checkpoint.
=============
*/
static void G_RaceFinishRun( gentity_t *point, gentity_t *player, int elapsed ) {
	gclient_t *client;
	qboolean personalBest;

	(void)point;

	if ( !player || !player->client ) {
		return;
	}

	client = player->client;
	client->raceState.active = qfalse;
	client->raceState.nextCheckpoint = 0;
	client->raceState.lastFinishTime = elapsed;
	personalBest = ( client->raceState.bestTime == RACE_INVALID_TIME || elapsed < client->raceState.bestTime );

	if ( personalBest ) {
		client->raceState.bestTime = elapsed;
		memcpy( client->raceState.bestSplits, client->raceState.currentSplits, sizeof( client->raceState.bestSplits ) );
	}

	G_RaceAnnounceFinish( player, elapsed, personalBest );
	G_RaceClearClientRunState( client );
	G_RaceUpdateConfigstrings();
}

/*
=============
G_RaceAdvanceCheckpoint

Processes a touch event for checkpoints after the start line.
=============
*/
static void G_RaceAdvanceCheckpoint( gentity_t *point, gentity_t *player ) {
	gclient_t *client;
	int elapsed;

	if ( !point || !player || !player->client ) {
		return;
	}

	client = player->client;
	if ( !client->raceState.active ) {
		return;
	}

	if ( point->racePointIndex != client->raceState.nextCheckpoint ) {
		return;
	}

	elapsed = level.time - client->raceState.startTime;
	client->raceState.currentSplits[point->racePointIndex] = elapsed;
	client->raceState.nextCheckpoint++;

	if ( point->racePointIndex == level.racePointCount - 1 ) {
		G_RaceFinishRun( point, player, elapsed );
	}
}

/*
=============
G_RaceHandlePointTouch

Entry point invoked when a race checkpoint is touched by an entity.
=============
*/
void G_RaceHandlePointTouch( gentity_t *point, gentity_t *player ) {
	if ( g_gametype.integer != GT_RACE || !point || !player || !player->client ) {
		return;
	}

	if ( level.racePointCount <= 0 ) {
		return;
	}

	if ( point->racePointIndex <= 0 ) {
		G_RaceStartRun( player );
		return;
	}

	G_RaceAdvanceCheckpoint( point, player );
}

/*
=============
G_RaceRegisterPoint

Adds a race_point entity to the level tracking lists.
=============
*/
static void G_RaceRegisterPoint( gentity_t *ent ) {
	if ( level.racePointCount >= MAX_RACE_POINTS ) {
		G_Printf( "race: too many checkpoints (max %i)\n", MAX_RACE_POINTS );
		G_FreeEntity( ent );
		return;
	}

	level.racePoints[level.racePointCount] = ent;
	ent->racePointIndex = level.racePointCount;
	ent->racePointAdminSpawned = qfalse;
	level.racePointCount++;
	level.raceLastSpawnedPoint = ent;
	G_RaceCachePointMetadata( ent );
	G_RaceUpdateInfoConfigString();
}

/*
=============
G_RacePointTouch

Touch handler for race checkpoint triggers.
=============
*/
static void G_RacePointTouch( gentity_t *self, gentity_t *other, trace_t *trace ) {
	(void)trace;
	G_RaceHandlePointTouch( self, other );
}

/*
=============
SP_race_point

Spawns a race checkpoint trigger.
=============
*/
void SP_race_point( gentity_t *ent ) {
	if ( g_gametype.integer != GT_RACE ) {
		G_FreeEntity( ent );
		return;
	}

	ent->classname = "race_point";
	VectorSet( ent->r.mins, -24.0f, -24.0f, 0.0f );
	VectorSet( ent->r.maxs, 24.0f, 24.0f, 48.0f );
	ent->r.contents = CONTENTS_TRIGGER;
	ent->clipmask = CONTENTS_PLAYERCLIP | CONTENTS_BODY;
	ent->r.svFlags |= SVF_NOCLIENT;
	ent->touch = G_RacePointTouch;
	ent->racePointIndex = -1;
	if ( !G_RaceDropPointToFloor( ent ) ) {
		return;
	}
	trap_LinkEntity( ent );
	G_RaceRegisterPoint( ent );
}

/*
=============
G_RaceAdminClearPoints

Removes all race points from the current level.
=============
*/
static void G_RaceAdminClearPoints( gentity_t *ent ) {
	gentity_t *point;
	int cleared;

	cleared = 0;
	point = NULL;
	while ( ( point = G_Find( point, FOFS( classname ), "race_point" ) ) != NULL ) {
		G_FreeEntity( point );
		cleared++;
	}

	if ( cleared > 0 ) {
		memset( level.racePoints, 0, sizeof( level.racePoints ) );
		memset( level.racePointInfo, 0, sizeof( level.racePointInfo ) );
		level.racePointCount = 0;
		level.raceLastSpawnedPoint = NULL;
	}

	G_RaceUpdateInfoConfigString();
	G_RaceBroadcastInitCommand( -1 );
	G_RacePrintMessage( ent, "clearing race points\n" );
}

/*
=============
G_RaceAdminDumpPoints

Prints the positions of every registered race point for debugging.
=============
*/
static void G_RaceAdminDumpPoints( gentity_t *ent ) {
	gentity_t *point;
	char buffer[128];

	point = NULL;
	while ( ( point = G_Find( point, FOFS( classname ), "race_point" ) ) != NULL ) {
		const char *target = ( point->target && *point->target ) ? point->target : "-";
		const char *targetName = ( point->targetname && *point->targetname ) ? point->targetname : "-";
		Com_sprintf( buffer, sizeof( buffer ), "%i: %.2f %.2f %.2f target=%s targetname=%s\n",
			point->racePointIndex, point->s.origin[0], point->s.origin[1], point->s.origin[2], target, targetName );
		G_RacePrintMessage( ent, buffer );
	}
}

/*
=============
G_RaceAdminSpawnPoint

Spawns a new checkpoint at the admin's current location.
=============
*/
static void G_RaceAdminSpawnPoint( gentity_t *ent ) {
	gentity_t *point;
	char targetName[32];

	if ( level.racePointCount >= MAX_RACE_POINTS ) {
		trap_SendServerCommand( ent - g_entities, va( "print \"too many race points (max %i)\n\"", MAX_RACE_POINTS ) );
		return;
	}

	point = G_Spawn();
	if ( !point ) {
		trap_SendServerCommand( ent - g_entities, "print \"failed to allocate race point\n\"" );
		return;
	}

	VectorCopy( ent->s.origin, point->s.origin );
	VectorCopy( point->s.origin, point->r.currentOrigin );
	point->classname = "race_point";
	SP_race_point( point );
	if ( !point->inuse ) {
		return;
	}

	Com_sprintf( targetName, sizeof( targetName ), "admin_race_point_%i", point->racePointIndex );
	point->targetname = G_NewString( targetName );
	point->racePointAdminSpawned = qtrue;
	G_RaceCachePointMetadata( point );
	trap_SendServerCommand( -1, "print \"spawning a race point\n\"" );
	trap_SendServerCommand( -1, va( "admin_race_point_%i %.2f %.2f %.2f %s %s",
		point->racePointIndex, point->s.origin[0], point->s.origin[1], point->s.origin[2],
		( point->target && *point->target ) ? point->target : "-",
		point->targetname ? point->targetname : "-" ) );
	G_RaceBroadcastInitCommand( -1 );
}

/*
=============
G_RaceAdminCommand

Handles the racepoint admin command for spawning, clearing, or dumping checkpoints.
=============
*/
void G_RaceAdminCommand( gentity_t *ent ) {
	char arg[MAX_STRING_CHARS];

	if ( !ent || !ent->client ) {
		return;
	}

	if ( g_gametype.integer != GT_RACE ) {
		trap_SendServerCommand( ent - g_entities, "print \"RacePoint is only permitted in Race.\n\"" );
		return;
	}

	if ( !g_cheats.integer ) {
		trap_SendServerCommand( ent - g_entities, "print \"Cheats are not enabled on this server.\n\"" );
		return;
	}

	if ( ent->health <= 0 ) {
		trap_SendServerCommand( ent - g_entities, "print \"You must be alive to use this command.\n\"" );
		return;
	}

	if ( trap_Argc() > 1 ) {
		trap_Argv( 1, arg, sizeof( arg ) );
		if ( !Q_stricmp( arg, "clear" ) ) {
			G_RaceAdminClearPoints( ent );
			return;
		}

		if ( !Q_stricmp( arg, "dump" ) ) {
			G_RaceAdminDumpPoints( ent );
			return;
		}
	}

	G_RaceAdminSpawnPoint( ent );
}

/*
=============
G_RaceServerClearPoints

Clears all checkpoints when invoked from the dedicated console.
=============
*/
void G_RaceServerClearPoints( void ) {
	G_RaceAdminClearPoints( NULL );
}

/*
=============
G_RaceServerDumpPoints

Dumps checkpoint metadata to the server console.
=============
*/
void G_RaceServerDumpPoints( void ) {
	G_RaceAdminDumpPoints( NULL );
}

/*
=============
G_RaceInitLevel

Clears the per-level race state and configstrings.
=============
*/
void G_RaceInitLevel( void ) {
	memset( level.racePoints, 0, sizeof( level.racePoints ) );
	level.racePointCount = 0;
	level.raceLastSpawnedPoint = NULL;
	memset( level.racePointInfo, 0, sizeof( level.racePointInfo ) );
	Q_strncpyz( g_raceScores, "scores_race 0", sizeof( g_raceScores ) );
	Q_strncpyz( g_raceInfo, "race_info 0", sizeof( g_raceInfo ) );
	trap_SetConfigstring( CS_RACE_SCORES, g_raceScores );
	trap_SetConfigstring( CS_RACE_INFO, g_raceInfo );
}

/*
=============
G_RaceClientBegin

Initializes race state when a client finishes connecting.
=============
*/
void G_RaceClientBegin( gentity_t *ent ) {
	if ( g_gametype.integer != GT_RACE || !ent || !ent->client ) {
		return;
	}

	G_RaceResetClient( ent->client );
	G_RaceBroadcastInitCommand( ent->s.number );
	G_RaceUpdateConfigstrings();
}

/*
=============
G_RaceClientSpawn

Stops any active run when the client respawns.
=============
*/
void G_RaceClientSpawn( gentity_t *ent ) {
	if ( g_gametype.integer != GT_RACE || !ent || !ent->client ) {
		return;
	}

	G_RaceClearClientRunState( ent->client );
	G_RaceUpdateConfigstrings();
}

/*
=============
G_RaceSendScoreboard

Responds to the "score" command while in Race gametype.
=============
*/
void G_RaceSendScoreboard( gentity_t *ent ) {
	if ( g_gametype.integer != GT_RACE || !ent || !ent->client ) {
		return;
	}

	G_RaceBuildScoreString();
	trap_SendServerCommand( ent - g_entities, g_raceScores );
}
