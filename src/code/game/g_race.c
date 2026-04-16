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

static void G_RaceCachePointMetadata( gentity_t *ent );
static void G_RaceUpdateInfoConfigString( void );
static void G_RaceRegisterPoint( gentity_t *ent );
static int G_RaceCheckpointCount( const gclient_t *client );

/*
=============
G_RacePointEntityNum

Returns the entity number for a race checkpoint or -1 when absent.
=============
*/
static int G_RacePointEntityNum( const gentity_t *point ) {
	if ( !point || !point->inuse ) {
		return -1;
	}

	return point->s.number;
}

/*
=============
G_RaceResolveInfoClient

Resolves the player whose retail race_info payload should be sent to a client.
=============
*/
static gclient_t *G_RaceResolveInfoClient( int clientNum ) {
	gentity_t	*ent;
	int		targetClientNum;

	if ( clientNum < 0 || clientNum >= level.maxclients ) {
		return NULL;
	}

	ent = &g_entities[clientNum];
	if ( !ent->inuse || !ent->client ) {
		return NULL;
	}

	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR &&
		ent->client->sess.spectatorState == SPECTATOR_FOLLOW ) {
		targetClientNum = ent->client->sess.spectatorClient;
		if ( targetClientNum >= 0 && targetClientNum < level.maxclients &&
			level.clients[targetClientNum].pers.connected == CON_CONNECTED &&
			level.clients[targetClientNum].sess.sessionTeam != TEAM_SPECTATOR ) {
			return &level.clients[targetClientNum];
		}
		return NULL;
	}

	return ent->client;
}

/*
=============
G_RaceBuildInfoCommand

Builds the retail six-field race_info payload for one tracked race client.
=============
*/
static void G_RaceBuildInfoCommand( const gclient_t *client, char *buffer, size_t bufferSize ) {
	int	active;
	int	startTime;
	int	lastFinishTime;
	int	checkpointCount;
	int	currentCheckpointEntityNum;
	int	nextCheckpointEntityNum;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	active = 0;
	startTime = 0;
	lastFinishTime = -1;
	checkpointCount = 0;
	currentCheckpointEntityNum = -1;
	nextCheckpointEntityNum = -1;
	if ( client ) {
		active = client->raceState.active ? 1 : 0;
		startTime = client->raceState.startTime;
		lastFinishTime = client->raceState.lastFinishTime;
		if ( client->raceState.active ) {
			checkpointCount = G_RaceCheckpointCount( client );
			currentCheckpointEntityNum = G_RacePointEntityNum( client->raceState.currentPoint );
			nextCheckpointEntityNum = G_RacePointEntityNum( client->raceState.nextPoint );
		}
	}

	Com_sprintf( buffer, bufferSize, "race_info %i %i %i %i %i %i",
		active, startTime, lastFinishTime, checkpointCount,
		currentCheckpointEntityNum, nextCheckpointEntityNum );
}

/*
=============
G_RaceBroadcastPrint

Broadcasts a race admin print message to every connected client.
=============
*/
static void G_RaceBroadcastPrint( const char *message ) {
	if ( !message || !*message ) {
		return;
	}

	trap_SendServerCommand( -1, va( "print \"%s\"", message ) );
}

/*
=============
FinishSpawningRacePoint

Drops a race checkpoint to the floor through the deferred retail spawn path.
=============
*/
static void FinishSpawningRacePoint( gentity_t *ent ) {
	trace_t	tr;
	vec3_t	dest;
	vec3_t	snapped;

	if ( !ent ) {
		return;
	}

	if ( ent->spawnflags & 1 ) {
		G_SetOrigin( ent, ent->s.origin );
	} else {
		VectorSet( dest, ent->s.origin[0], ent->s.origin[1], ent->s.origin[2] - 4096.0f );
		trap_Trace( &tr, ent->s.origin, ent->r.mins, ent->r.maxs, dest, ent->s.number, MASK_SOLID );
		if ( tr.startsolid ) {
			G_Printf( "FinishSpawningItem: race_point startsolid at %s\n", vtos( ent->s.origin ) );
			G_FreeEntity( ent );
			return;
		}

		ent->s.groundEntityNum = tr.entityNum;
		G_SetOrigin( ent, tr.endpos );
	}

	VectorCopy( ent->s.origin, snapped );
	snapped[0] = (float)( (int)snapped[0] );
	snapped[1] = (float)( (int)snapped[1] );
	snapped[2] = (float)( (int)( snapped[2] + 1.0f ) );
	G_SetOrigin( ent, snapped );

	trap_LinkEntity( ent );
	if ( ent->racePointIndex < 0 ) {
		G_RaceRegisterPoint( ent );
	} else {
		G_RaceCachePointMetadata( ent );
		G_RaceUpdateInfoConfigString();
	}
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

	trap_SendServerCommand( clientNum, "race_init" );
	for ( i = 0; i < count; i++ ) {
		if ( level.racePointInfo[i].inUse ) {
			G_RaceSendPointMetadataCommand( clientNum, i );
		}
	}
}

/*
=============
G_RaceSendInfoCommand

Flushes the retail race_info payload to one client, while preserving the
broadcast configstring helper for admin/server probes.
=============
*/
void G_RaceSendInfoCommand( int clientNum ) {
	char		buffer[MAX_STRING_CHARS];
	gclient_t	*client;

	if ( clientNum < 0 ) {
		G_RaceUpdateInfoConfigString();
		trap_SendServerCommand( clientNum, g_raceInfo );
		return;
	}

	client = G_RaceResolveInfoClient( clientNum );
	G_RaceBuildInfoCommand( client, buffer, sizeof( buffer ) );
	trap_SendServerCommand( clientNum, buffer );
}

/*
=============
G_RaceFormatMilliseconds

Formats a millisecond duration into a mm:ss.mmm string.
=============
*/
static void G_RaceFormatMilliseconds( int milliseconds, char *buffer, size_t bufferSize ) {
	unsigned int	absoluteMilliseconds;
	const char		*signPrefix;
	const char		*secondPrefix;
	int minutes;
	float seconds;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	signPrefix = "";
	absoluteMilliseconds = (unsigned int)milliseconds;
	if ( milliseconds < 0 ) {
		signPrefix = "-";
		absoluteMilliseconds = (unsigned int)( -( milliseconds + 1 ) ) + 1u;
	}

	minutes = absoluteMilliseconds / 60000u;
	seconds = ( absoluteMilliseconds % 60000u ) / 1000.0f;
	secondPrefix = ( seconds < 10.0f ) ? "0" : "";
	Com_sprintf( buffer, bufferSize, "%s%d:%s%.03f", signPrefix, minutes, secondPrefix, seconds );
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
	client->raceState.currentPoint = NULL;
	client->raceState.nextPoint = NULL;
	memset( client->raceState.currentSplits, 0, sizeof( client->raceState.currentSplits ) );
}

/*
=============
Cmd_RaceInit_f

Clears the invoking client's in-progress race state without rebuilding level metadata.
=============
*/
void Cmd_RaceInit_f( gentity_t *ent ) {
	if ( g_gametype.integer != GT_RACE || !ent || !ent->client ) {
		return;
	}

	G_RaceClearClientRunState( ent->client );
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
G_RaceCheckpointCount

Returns the number of cleared checkpoints for the current run.
=============
*/
static int G_RaceCheckpointCount( const gclient_t *client ) {
	int	checkpointCount;

	if ( !client ) {
		return 0;
	}

	checkpointCount = client->raceState.nextCheckpoint - 1;
	if ( checkpointCount < 0 ) {
		checkpointCount = 0;
	}

	return checkpointCount;
}

/*
=============
G_RacePickPointTarget

Resolves the next point in a race-point target chain.
=============
*/
static gentity_t *G_RacePickPointTarget( const gentity_t *point ) {
	if ( !point || !point->target || !point->target[0] ) {
		return NULL;
	}

	return G_PickTarget( point->target );
}

/*
=============
G_RacePointIsStart

Treats the first registered point as a valid start while preserving the retail
targetname-free start-point behavior for authored maps.
=============
*/
static qboolean G_RacePointIsStart( const gentity_t *point ) {
	if ( !point ) {
		return qfalse;
	}

	if ( point->racePointIndex == 0 ) {
		return qtrue;
	}

	return ( qboolean )( !point->targetname || !point->targetname[0] );
}

/*
=============
G_RaceEmitClientEvent

Spawns a retail-style single-client temp entity for Race events.
=============
*/
static gentity_t *G_RaceEmitClientEvent( gentity_t *player, int event ) {
	gentity_t	*tent;

	if ( !player || !player->client ) {
		return NULL;
	}

	tent = G_TempEntity( player->client->ps.origin, event );
	tent->r.svFlags |= SVF_SINGLECLIENT;
	tent->r.singleClient = player->s.number;
	G_SetRetailEventRecipient( tent, player->s.number );
	return tent;
}

/*
=============
G_RaceEmitStartEvent

Publishes the retail EV_RACE_START payload for the local runner.
=============
*/
static void G_RaceEmitStartEvent( gentity_t *player ) {
	gentity_t	*tent;
	gclient_t	*client;

	if ( !player || !player->client ) {
		return;
	}

	client = player->client;
	tent = G_RaceEmitClientEvent( player, EV_RACE_START );
	if ( !tent ) {
		return;
	}

	tent->s.groundEntityNum = G_RaceCheckpointCount( client );
	tent->s.constantLight = G_RacePointEntityNum( client->raceState.currentPoint );
	tent->s.legsAnim = G_RacePointEntityNum( client->raceState.nextPoint );
	G_SetRetailEventIntPayload( &tent->s, client->raceState.startTime );
}

/*
=============
G_RaceEmitCheckpointEvent

Publishes the retail EV_RACE_CHECKPOINT payload for the local runner.
=============
*/
static void G_RaceEmitCheckpointEvent( gentity_t *player, int splitDelta, qboolean hasBestSplit ) {
	gentity_t	*tent;
	gclient_t	*client;

	if ( !player || !player->client ) {
		return;
	}

	client = player->client;
	tent = G_RaceEmitClientEvent( player, EV_RACE_CHECKPOINT );
	if ( !tent ) {
		return;
	}

	tent->s.groundEntityNum = G_RaceCheckpointCount( client );
	tent->s.constantLight = G_RacePointEntityNum( client->raceState.currentPoint );
	tent->s.legsAnim = G_RacePointEntityNum( client->raceState.nextPoint );
	G_SetRetailEventIntPayload( &tent->s, splitDelta );
	G_SetRetailEventData( &tent->s, hasBestSplit ? 1 : 0 );
}

/*
=============
G_RaceEmitFinishEvent

Publishes the retail EV_RACE_FINISH payload for the local runner.
=============
*/
static void G_RaceEmitFinishEvent( gentity_t *player, int elapsed ) {
	gentity_t	*tent;

	tent = G_RaceEmitClientEvent( player, EV_RACE_FINISH );
	if ( !tent ) {
		return;
	}

	G_SetRetailEventIntPayload( &tent->s, elapsed );
	G_SetRetailEventData( &tent->s, 1 );
}

/*
=============
G_RaceEmitNewHighScoreEvent

Publishes the retail EV_NEW_HIGH_SCORE cue for a new course record.
=============
*/
static void G_RaceEmitNewHighScoreEvent( gentity_t *player ) {
	(void)G_RaceEmitClientEvent( player, EV_NEW_HIGH_SCORE );
}

/*
=============
G_RaceStartRun

Begins a new race attempt for the provided player.
=============
*/
static void G_RaceStartRun( gentity_t *point, gentity_t *player ) {
	gclient_t	*client;
	gentity_t	*currentPoint;

	if ( !point || !player || !player->client ) {
		return;
	}

	client = player->client;
	if ( client->raceState.active && level.time - client->raceState.startTime <= 999 ) {
		return;
	}

	currentPoint = G_RacePickPointTarget( point );
	if ( !currentPoint ) {
		return;
	}

	G_RaceClearClientRunState( client );
	client->raceState.active = qtrue;
	client->raceState.startTime = level.time;
	client->raceState.nextCheckpoint = 1;
	client->raceState.currentPoint = currentPoint;
	client->raceState.nextPoint = G_RacePickPointTarget( currentPoint );
	client->raceState.currentSplits[0] = 0;
	G_RaceEmitStartEvent( player );
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
	gclient_t	*client;
	gclient_t	*leader;
	qboolean	personalBest;
	qboolean	newHighScore;

	if ( !player || !player->client ) {
		return;
	}

	client = player->client;
	if ( !point || client->raceState.currentPoint != point ) {
		return;
	}

	if ( client->raceState.nextCheckpoint >= 0 && client->raceState.nextCheckpoint < MAX_RACE_POINTS ) {
		client->raceState.currentSplits[client->raceState.nextCheckpoint] = elapsed;
	}

	client->raceState.lastFinishTime = elapsed;
	leader = G_RaceFindLeader();
	personalBest = ( client->raceState.bestTime == RACE_INVALID_TIME || elapsed < client->raceState.bestTime );
	newHighScore = ( leader == NULL || elapsed < leader->raceState.bestTime ) ? qtrue : qfalse;

	if ( personalBest ) {
		client->raceState.bestTime = elapsed;
		memcpy( client->raceState.bestSplits, client->raceState.currentSplits, sizeof( client->raceState.bestSplits ) );
	}

	if ( newHighScore ) {
		G_RaceEmitNewHighScoreEvent( player );
	}
	G_RaceEmitFinishEvent( player, elapsed );
	G_RaceAnnounceFinish( player, elapsed, personalBest );
	G_RankSendPlayerRaceComplete( player, elapsed );
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
	gclient_t	*client;
	int		bestSplit;
	int		elapsed;
	int		splitDelta;
	qboolean	hasBestSplit;

	if ( !point || !player || !player->client ) {
		return;
	}

	client = player->client;
	if ( !client->raceState.active || client->raceState.currentPoint != point ) {
		return;
	}

	elapsed = level.time - client->raceState.startTime;
	if ( !point->target || !point->target[0] ) {
		G_RaceFinishRun( point, player, elapsed );
		return;
	}

	hasBestSplit = qfalse;
	splitDelta = 0;
	bestSplit = 0;
	if ( client->raceState.nextCheckpoint >= 0 && client->raceState.nextCheckpoint < MAX_RACE_POINTS ) {
		bestSplit = client->raceState.bestSplits[client->raceState.nextCheckpoint];
		client->raceState.currentSplits[client->raceState.nextCheckpoint] = elapsed;
		if ( bestSplit != 0 ) {
			hasBestSplit = qtrue;
			splitDelta = elapsed - bestSplit;
		}
	}

	client->raceState.nextCheckpoint++;
	client->raceState.currentPoint = G_RacePickPointTarget( point );
	client->raceState.nextPoint = G_RacePickPointTarget( client->raceState.currentPoint );
	G_RaceEmitCheckpointEvent( player, splitDelta, hasBestSplit );
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

	if ( G_RacePointIsStart( point ) ) {
		G_RaceStartRun( point, player );
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
	VectorSet( ent->r.mins, -40.0f, -40.0f, -15.0f );
	VectorSet( ent->r.maxs, 40.0f, 40.0f, 128.0f );
	ent->r.contents = CONTENTS_TRIGGER;
	ent->r.svFlags |= SVF_NOCLIENT;
	ent->touch = G_RacePointTouch;
	ent->racePointIndex = -1;
	ent->think = FinishSpawningRacePoint;
	ent->nextthink = level.time + 1;
	trap_LinkEntity( ent );
}

/*
=============
G_RaceAdminClearPoints

Removes all race points from the current level.
=============
*/
static void G_RaceAdminClearPoints( gentity_t *ent ) {
	gentity_t	*point;
	int		i;

	(void)ent;
	point = NULL;
	while ( ( point = G_Find( point, FOFS( classname ), "race_point" ) ) != NULL ) {
		G_FreeEntity( point );
	}

	for ( i = 0; i < level.maxclients; ++i ) {
		if ( level.clients[i].pers.connected != CON_CONNECTED ) {
			continue;
		}
		G_RaceClearClientRunState( &level.clients[i] );
	}

	memset( level.racePoints, 0, sizeof( level.racePoints ) );
	memset( level.racePointInfo, 0, sizeof( level.racePointInfo ) );
	level.racePointCount = 0;
	level.raceLastSpawnedPoint = NULL;
	G_RaceUpdateInfoConfigString();
	G_RaceBroadcastInitCommand( -1 );
	G_RaceBroadcastPrint( "clearing race points\n" );
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

	(void)ent;
	point = NULL;
	while ( ( point = G_Find( point, FOFS( classname ), "race_point" ) ) != NULL ) {
		Com_sprintf( buffer, sizeof( buffer ), "%f %f %f\n",
			point->s.origin[0], point->s.origin[1], point->s.origin[2] );
		G_RaceBroadcastPrint( buffer );
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
	vec3_t	origin;
	char targetName[16];

	if ( level.racePointCount >= MAX_RACE_POINTS ) {
		G_RaceBroadcastPrint( "too many race points\n" );
		return;
	}

	point = G_Spawn();
	if ( !point ) {
		trap_SendServerCommand( ent - g_entities, "print \"failed to allocate race point\n\"" );
		return;
	}

	VectorSet( origin, ent->s.origin[0], ent->s.origin[1], ent->s.origin[2] - 8.0f );
	G_SetOrigin( point, origin );
	point->classname = "race_point";
	point->spawnflags = 0;
	Com_sprintf( targetName, sizeof( targetName ), "arp%i", level.racePointCount );
	point->targetname = G_NewString( targetName );
	point->racePointAdminSpawned = qtrue;

	if ( level.raceLastSpawnedPoint ) {
		level.raceLastSpawnedPoint->target = G_NewString( targetName );
		G_RaceCachePointMetadata( level.raceLastSpawnedPoint );
	}

	SP_race_point( point );
	if ( !point->inuse ) {
		return;
	}

	G_RaceRegisterPoint( point );
	G_RaceBroadcastPrint( "spawning a race point\n" );
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
		trap_SendServerCommand( ent - g_entities, "print \"" GAMEPRINT_RACEPOINT_RACE_ONLY "\"" );
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
G_RaceResetClientAndSpawn

Resets a race client, republishes the retail race-init state, and reruns ClientSpawn.
=============
*/
void G_RaceResetClientAndSpawn( gentity_t *ent ) {
	int	racePointCount;

	if ( g_gametype.integer != GT_RACE || !ent || !ent->client ) {
		return;
	}

	G_RaceResetClient( ent->client );

	racePointCount = level.racePointCount;
	if ( racePointCount < 0 ) {
		racePointCount = 0;
	}
	if ( racePointCount > MAX_RACE_POINTS ) {
		racePointCount = MAX_RACE_POINTS;
	}

	trap_SetConfigstring( CS_RACE_RECORDS, va( "%i", racePointCount ) );
	G_RaceBroadcastInitCommand( ent->s.number );
	G_RaceUpdateConfigstrings();
	ClientSpawn( ent );
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
G_BuildRaceScoreboardMessage

Builds and sends the retail `scores_race` payload for one client.
=============
*/
void G_BuildRaceScoreboardMessage( gentity_t *ent ) {
	if ( g_gametype.integer != GT_RACE || !ent || !ent->client ) {
		return;
	}

	G_RaceBuildScoreString();
	trap_SendServerCommand( ent - g_entities, g_raceScores );
}

/*
=============
G_RaceSendScoreboard

Responds to the "score" command while in Race gametype.
=============
*/
void G_RaceSendScoreboard( gentity_t *ent ) {
	G_BuildRaceScoreboardMessage( ent );
}
