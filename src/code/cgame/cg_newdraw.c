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


#include "cg_local.h"
#include "../ui/ui_shared.h"

extern displayContextDef_t cgDC;

typedef enum cgVoteSlotField_e {
	CG_VOTE_FIELD_GAMETYPE,
	CG_VOTE_FIELD_MAP,
	CG_VOTE_FIELD_NAME,
	CG_VOTE_FIELD_COUNT
	} cgVoteSlotField_t;

//
// Forward declarations for HUD ownerdraw helpers used by Quake Live menus.
//
static void CG_DrawServerSettings(rectDef_t *rect, float scale, vec4_t color, int textStyle);
static void CG_DrawStartingWeapons(rectDef_t *rect, float scale, vec4_t color, int textStyle);
static void CG_DrawGameLimit(rectDef_t *rect, float scale, vec4_t color, int textStyle);
static void CG_DrawGameTypeMap(rectDef_t *rect, float scale, vec4_t color, int textStyle);
static void CG_DrawMatchDetails(rectDef_t *rect, float scale, vec4_t color, int textStyle);
static void CG_DrawMatchStatus(rectDef_t *rect, float scale, vec4_t color, int textStyle);
static void CG_DrawMatchEndCondition(rectDef_t *rect, float scale, vec4_t color, int textStyle);
static void CG_ParseActiveVoteCommand( char *command, size_t commandSize, char *argument, size_t argumentSize );
static void CG_DrawVoteShot(rectDef_t *rect, int slot);
static void CG_DrawVoteMapSlot(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot, cgVoteSlotField_t field);
static void CG_DrawVoteGametype(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot);
static void CG_DrawVoteMap(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot);
static void CG_DrawVoteName(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot);
static void CG_DrawVoteCount(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot);
static void CG_DrawVoteTimer(rectDef_t *rect, float scale, vec4_t color, int textStyle);

#define CG_RACE_CHECKPOINT_HALF_WIDTH 24.0f
#define CG_RACE_CHECKPOINT_HEIGHT 48.0f
#define CG_SPECTATOR_TRACK_TIMEOUT 5000

enum {
ROUNDSTATE_INACTIVE,
ROUNDSTATE_WARMUP,
ROUNDSTATE_ACTIVE,
ROUNDSTATE_COMPLETE
};

static void CG_DrawServerSettings(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle);
static void CG_DrawStartingWeapons(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle);
static void CG_DrawGameLimit(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle);
static void CG_DrawGameTypeIcon(rectDef_t *rect);
static void CG_DrawGameTypeMap(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle);
static void CG_DrawMatchDetails(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle);
static void CG_DrawMatchEndCondition(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle);
static void CG_DrawMatchStatus(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle);
static void CG_DrawRoundLabel(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle);
static void CG_DrawLocalTime(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle);
static void CG_DrawVoteGametype(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle, int slot);
static void CG_DrawVoteName(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle, int slot);
static void CG_DrawVoteMapSlot(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle, int slot);
static void CG_DrawVoteShot(rectDef_t *rect, int slot);
static void CG_DrawVoteCount(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle, int slot);
static void CG_DrawVoteTimer(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle);

/*
=============
CG_RaceFormatMilliseconds

Formats a millisecond duration into a mm:ss.mmm string.
=============
*/
static void CG_RaceFormatMilliseconds( int milliseconds, char *buffer, size_t bufferSize ) {
	int	minutes;
	int	seconds;
	int	ms;

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
	Com_sprintf( buffer, bufferSize, "%i:%02i.%03i", minutes, seconds, ms );
}

/*
=============
CG_RaceResetState

Clears cached race HUD state so configstrings can repopulate it.
=============
*/
void CG_RaceResetState( void ) {
	int i;

	memset( cgs.raceProgress, 0, sizeof( cgs.raceProgress ) );
	memset( cgs.raceStatus, 0, sizeof( cgs.raceStatus ) );
	cgs.raceStatusSequence = 0;
	cgs.raceLeaderClientNum = -1;
	for ( i = 0; i < MAX_CLIENTS; ++i ) {
		cgs.raceProgress[i].currentCheckpoint = -1;
	}
}

/*
=============
CG_RacePlayCue

Plays a race HUD cue when enabled.
=============
*/
void CG_RacePlayCue( cgRaceCue_t cue ) {
	sfxHandle_t sfx = 0;

	if ( !cg_raceBeep.integer ) {
		return;
	}

	switch ( cue ) {
	case CG_RACE_CUE_START:
		sfx = cgs.media.raceStartBeep;
		break;
	case CG_RACE_CUE_CHECKPOINT:
		sfx = cgs.media.raceCheckpointBeep;
		break;
	case CG_RACE_CUE_FINISH:
		sfx = cgs.media.raceFinishBeep;
		break;
	default:
		return;
	}

	if ( sfx ) {
		trap_S_StartLocalSound( sfx, CHAN_LOCAL_SOUND );
	}
}

/*
=============
CG_ParseRaceInfoString

Parses the race_info configstring and caches the split metadata.
=============
*/
void CG_ParseRaceInfoString( const char *infoString ) {
	char buffer[MAX_STRING_CHARS];
	char *text;
	const char *token;
	int i;
	int count;

	cgs.raceLeaderSplitCount = 0;
	if ( !infoString || !*infoString ) {
		return;
	}

	Q_strncpyz( buffer, infoString, sizeof( buffer ) );
	text = buffer;
	token = COM_ParseExt( &text, qfalse );
	if ( Q_stricmp( token, "race_info" ) ) {
		return;
	}

	token = COM_ParseExt( &text, qfalse );
	count = token ? atoi( token ) : 0;
	if ( count < 0 ) {
		count = 0;
	}
	if ( count > MAX_RACE_POINTS ) {
		count = MAX_RACE_POINTS;
	}

	cgs.racePointCount = count;
	memset( cgs.raceLeaderSplits, 0, sizeof( cgs.raceLeaderSplits ) );
	for ( i = 0; i < count; ++i ) {
		token = COM_ParseExt( &text, qfalse );
		if ( !token || !*token ) {
			break;
		}
		cgs.raceLeaderSplits[i] = atoi( token );
		cgs.raceLeaderSplitCount++;
	}
	for ( i = 0; i < MAX_CLIENTS; ++i ) {
		cgs.raceProgress[i].currentCheckpoint = -1;
		cgs.raceProgress[i].runActive = qfalse;
		cgs.raceProgress[i].initialized = qfalse;
	}
}

/*
=============
CG_ParseRaceStatusString

Parses the scores_race configstring and caches per-client timing data.
=============
*/
void CG_ParseRaceStatusString( const char *statusString ) {
	char buffer[MAX_STRING_CHARS];
	char *text;
	const char *token;
	int count;
	int sequence;
	int i;

	if ( !statusString || !*statusString ) {
		memset( cgs.raceStatus, 0, sizeof( cgs.raceStatus ) );
		cgs.raceStatusSequence = 0;
		cgs.raceLeaderClientNum = -1;
		return;
	}

	Q_strncpyz( buffer, statusString, sizeof( buffer ) );
	text = buffer;
	token = COM_ParseExt( &text, qfalse );
	if ( Q_stricmp( token, "scores_race" ) ) {
		return;
	}

	token = COM_ParseExt( &text, qfalse );
	count = token ? atoi( token ) : 0;
	if ( count < 0 ) {
		count = 0;
	}
	if ( count > MAX_CLIENTS ) {
		count = MAX_CLIENTS;
	}

	sequence = ++cgs.raceStatusSequence;
	cgs.raceLeaderClientNum = -1;
	for ( i = 0; i < count; ++i ) {
		int values[4];
		int j;

		for ( j = 0; j < 4; ++j ) {
			token = COM_ParseExt( &text, qfalse );
			if ( !token || !*token ) {
				break;
			}
			values[j] = atoi( token );
		}
		if ( j < 4 ) {
			break;
		}

		if ( values[0] < 0 || values[0] >= MAX_CLIENTS ) {
			continue;
		}

		cgRaceClientStatus_t *status = &cgs.raceStatus[values[0]];
		int previousLast = status->lastTime;

		if ( !status->initialized ) {
			status->lapCount = 0;
		}

		status->initialized = qtrue;
		status->bestTime = values[1];
		status->lastTime = values[2];
		status->currentElapsed = values[3];
		status->lastUpdateSequence = sequence;

		if ( status->lastTime >= 0 && status->lastTime != previousLast ) {
			if ( status->lapCount < RACE_INVALID_TIME ) {
				status->lapCount++;
			}
		} else if ( status->lastTime < 0 && status->bestTime < 0 ) {
			status->lapCount = 0;
		}

		if ( status->bestTime >= 0 ) {
			if ( cgs.raceLeaderClientNum < 0 ||
				status->bestTime < cgs.raceStatus[cgs.raceLeaderClientNum].bestTime ) {
				cgs.raceLeaderClientNum = values[0];
			}
		}
	}

	for ( i = 0; i < MAX_CLIENTS; ++i ) {
		cgRaceClientStatus_t *status = &cgs.raceStatus[i];
		if ( status->initialized && status->lastUpdateSequence != sequence ) {
			memset( status, 0, sizeof( *status ) );
		}
	}
}

/*
=============
CG_RacePointContainsIndex

Tests if the provided origin lies within the checkpoint bounds.
=============
*/
static qboolean CG_RacePointContainsIndex( int index, const vec3_t origin ) {
	const cgRacePointInfo_t *point;
	float minX;
	float maxX;
	float minY;
	float maxY;
	float minZ;
	float maxZ;

	if ( index < 0 || index >= cgs.racePointCount ) {
		return qfalse;
	}

	point = &cgs.racePoints[index];
	if ( !point->active ) {
		return qfalse;
	}

	minX = point->origin[0] - CG_RACE_CHECKPOINT_HALF_WIDTH;
	maxX = point->origin[0] + CG_RACE_CHECKPOINT_HALF_WIDTH;
	minY = point->origin[1] - CG_RACE_CHECKPOINT_HALF_WIDTH;
	maxY = point->origin[1] + CG_RACE_CHECKPOINT_HALF_WIDTH;
	minZ = point->origin[2];
	maxZ = point->origin[2] + CG_RACE_CHECKPOINT_HEIGHT;

	if ( origin[0] < minX || origin[0] > maxX ) {
		return qfalse;
	}
	if ( origin[1] < minY || origin[1] > maxY ) {
		return qfalse;
	}
	if ( origin[2] < minZ || origin[2] > maxZ ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
CG_RaceProgressForClient

Returns the cached checkpoint progress entry for a client.
=============
*/
static cgRaceClientProgress_t *CG_RaceProgressForClient( int clientNum ) {
	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return NULL;
	}
	return &cgs.raceProgress[clientNum];
}

/*
=============
CG_RaceStatusForClient

Returns the cached race status entry for a client if available.
=============
*/
static const cgRaceClientStatus_t *CG_RaceStatusForClient( int clientNum ) {
	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return NULL;
	}
	if ( !cgs.raceStatus[clientNum].initialized ) {
		return NULL;
	}
	return &cgs.raceStatus[clientNum];
}


/*
=============
CG_RaceShouldPlayCheckpointFeedback

Determines if checkpoint notifications should be emitted for a client.
=============
*/
static qboolean CG_RaceShouldPlayCheckpointFeedback( int clientNum ) {
	if ( cg_raceBeep.integer == 0 || !cg.snap ) {
		return qfalse;
	}
	if ( cg.snap->ps.pm_type == PM_INTERMISSION ) {
		return qfalse;
	}
	if ( clientNum < 0 ) {
		return qfalse;
	}
	if ( !( cg.snap->ps.pm_flags & PMF_FOLLOW ) && clientNum == cg.clientNum ) {
		return qtrue;
	}
	if ( ( cg.snap->ps.pm_flags & PMF_FOLLOW ) && clientNum == cg.spectatorFollowClient ) {
		return qtrue;
	}
	return qfalse;
}


/*
=============
CG_RacePlayCheckpointFeedback

Emits the checkpoint centerprint and audio cue when enabled.
=============
*/
static void CG_RacePlayCheckpointFeedback( const cgRaceClientProgress_t *progress ) {
	char		statusText[64];
	int		 total;
	int		 cleared;
	int		 remaining;

	if ( !progress ) {
		return;
	}

	total = ( cgs.racePointCount > 0 ) ? ( cgs.racePointCount - 1 ) : 0;
	cleared = progress->currentCheckpoint;
	if ( total <= 0 || cleared <= 0 ) {
		return;
	}

	remaining = total - cleared;
	if ( remaining < 0 ) {
		remaining = 0;
	}
	if ( remaining > 0 ) {
		Com_sprintf( statusText, sizeof( statusText ), "%i remaining", remaining );
	} else {
		Q_strncpyz( statusText, "Finish", sizeof( statusText ) );
	}

	CG_CenterPrint( va( "Checkpoint\n%s", statusText ), SCREEN_HEIGHT * 0.30f, BIGCHAR_WIDTH );
	trap_S_StartLocalSound( cgs.media.selectSound, CHAN_LOCAL_SOUND );
}

/*
=============
CG_RaceUpdateClientProgress

Updates the predicted checkpoint state for a specific client.
=============
*/
static void CG_RaceUpdateClientProgress( int clientNum, const vec3_t origin, const cgRaceClientStatus_t *status ) {
	cgRaceClientProgress_t *progress;

	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return;
	}

	progress = &cgs.raceProgress[clientNum];
	if ( !progress->initialized ) {
		progress->currentCheckpoint = -1;
		progress->initialized = qtrue;
	}

	if ( cgs.racePointCount <= 0 ) {
		progress->runActive = qfalse;
		progress->currentCheckpoint = -1;
		return;
	}

	if ( !status || status->currentElapsed < 0 ) {
		progress->runActive = qfalse;
		if ( status && status->lastTime >= 0 ) {
			progress->currentCheckpoint = cgs.racePointCount - 1;
		} else {
			progress->currentCheckpoint = -1;
		}
		return;
	}

	if ( !progress->runActive ) {
		if ( CG_RacePointContainsIndex( 0, origin ) ) {
			progress->runActive = qtrue;
			progress->currentCheckpoint = 0;
			progress->lastTouchTime = cg.time;
			CG_RacePlayCue( CG_RACE_CUE_START );
		}
		return;
	}

	if ( progress->currentCheckpoint < 0 ) {
		progress->currentCheckpoint = 0;
	}

	if ( progress->currentCheckpoint >= cgs.racePointCount - 1 ) {
		progress->runActive = qfalse;
		return;
	}

	if ( CG_RacePointContainsIndex( progress->currentCheckpoint + 1, origin ) ) {
		progress->currentCheckpoint++;
		progress->lastTouchTime = cg.time;
		if ( CG_RaceShouldPlayCheckpointFeedback( clientNum ) ) {
			CG_RacePlayCheckpointFeedback( progress );
		}
		if ( progress->currentCheckpoint >= cgs.racePointCount - 1 ) {
			progress->runActive = qfalse;
			CG_RacePlayCue( CG_RACE_CUE_FINISH );
		} else {
			CG_RacePlayCue( CG_RACE_CUE_CHECKPOINT );
		}
	}
}

/*
=============
CG_RaceResolveClientNum

Determines which client the race owner draws should track.
=============
*/
static int CG_RaceResolveClientNum( void ) {
	if ( !cg.snap ) {
		return -1;
	}
	if ( cgs.gametype != GT_RACE ) {
		return -1;
	}
	if ( cg.snap->ps.pm_type == PM_INTERMISSION ) {
		return -1;
	}
	if ( ( cg.snap->ps.pm_flags & PMF_FOLLOW ) && cg.spectatorFollowClient >= 0 ) {
		return cg.spectatorFollowClient;
	}
	if ( cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR ) {
		return -1;
	}
	return cg.clientNum;
}

/*
=============
CG_RaceGetClientOrigin

Copies the best available origin for a client into the output vector.
=============
*/
static qboolean CG_RaceGetClientOrigin( int clientNum, vec3_t origin ) {
	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return qfalse;
	}
	if ( clientNum == cg.clientNum && !( cg.snap->ps.pm_flags & PMF_FOLLOW ) ) {
		VectorCopy( cg.predictedPlayerState.origin, origin );
		return qtrue;
	}
	VectorCopy( cg_entities[clientNum].lerpOrigin, origin );
	return qtrue;
}

/*
=============
CG_RacePrepareHudState

Resolves the client and predicted checkpoint state for race HUD rendering.
=============
*/
static qboolean CG_RacePrepareHudState( const cgRaceClientStatus_t **statusOut, cgRaceClientProgress_t **progressOut ) {
	const cgRaceClientStatus_t *status;
	cgRaceClientProgress_t *progress;
	vec3_t origin;
	int clientNum;

	if ( !cg.snap || cgs.gametype != GT_RACE ) {
		return qfalse;
	}
	if ( cg.snap->ps.pm_type == PM_INTERMISSION ) {
		return qfalse;
	}

	CG_UpdateSpectatorTargets();
	clientNum = CG_RaceResolveClientNum();
	if ( clientNum < 0 ) {
		return qfalse;
	}

	status = CG_RaceStatusForClient( clientNum );
	progress = CG_RaceProgressForClient( clientNum );
	if ( progress && CG_RaceGetClientOrigin( clientNum, origin ) ) {
		CG_RaceUpdateClientProgress( clientNum, origin, status );
	}

	if ( statusOut ) {
		*statusOut = status;
	}
	if ( progressOut ) {
		*progressOut = progress;
	}

	return qtrue;
}

/*
=============
CG_RaceCurrentLapNumber

Returns the lap number the HUD should display for a client.
=============
*/
static int CG_RaceCurrentLapNumber( const cgRaceClientStatus_t *status ) {
	int lap = 1;

	if ( status && status->initialized ) {
		lap = status->lapCount + 1;
		if ( lap <= 0 ) {
			lap = 1;
		}
	}

	return lap;
}

/*
=============
CG_RaceLeaderBestTime

Fetches the best recorded leader time if available.
=============
*/
static int CG_RaceLeaderBestTime( void ) {
	int splits = cgs.raceLeaderSplitCount;

	if ( splits > 0 ) {
		return cgs.raceLeaderSplits[splits - 1];
	}
	if ( cgs.raceLeaderClientNum >= 0 && cgs.raceLeaderClientNum < MAX_CLIENTS ) {
		const cgRaceClientStatus_t *status = &cgs.raceStatus[cgs.raceLeaderClientNum];
		if ( status->initialized && status->bestTime >= 0 ) {
			return status->bestTime;
		}
	}
	return -1;
}

/*
=============
CG_RaceFormatDelta

Formats a millisecond delta into a signed seconds string.
=============
*/
static void CG_RaceFormatDelta( int delta, char *buffer, size_t bufferSize ) {
	float seconds;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}
	seconds = (float)delta / 1000.0f;
	Com_sprintf( buffer, bufferSize, "%+.3f", seconds );
}

/*
=============
CG_RaceCheckpointDelta

Computes the delta between the current split and the leader split.
=============
*/
static qboolean CG_RaceCheckpointDelta( const cgRaceClientStatus_t *status, const cgRaceClientProgress_t *progress, int *deltaOut ) {
	int index;

	if ( !status || !progress || !deltaOut ) {
		return qfalse;
	}
	if ( !progress->runActive || status->currentElapsed < 0 ) {
		return qfalse;
	}
	index = progress->currentCheckpoint;
	if ( index <= 0 || index >= cgs.raceLeaderSplitCount ) {
		return qfalse;
	}
	*deltaOut = status->currentElapsed - cgs.raceLeaderSplits[index];
	return qtrue;
}

/*
=============
CG_RaceBuildStatusString

Builds the race status ownerdraw text for the active client.
=============
*/
static qboolean CG_RaceBuildStatusString( char *buffer, size_t bufferSize ) {
	const cgRaceClientStatus_t *status;
	cgRaceClientProgress_t *progress;
	int lap;
	int cleared;
	int total;

	if ( !buffer || bufferSize <= 0 ) {
		return qfalse;
	}
	buffer[0] = '\0';

	if ( !CG_RacePrepareHudState( &status, &progress ) ) {
		return qfalse;
	}

	if ( cg.warmup ) {
		Q_strncpyz( buffer, "Warmup", bufferSize );
		return qtrue;
	}

	lap = CG_RaceCurrentLapNumber( status );
	total = ( cgs.racePointCount > 0 ) ? ( cgs.racePointCount - 1 ) : 0;
	cleared = 0;
	if ( progress && progress->currentCheckpoint > 0 ) {
		cleared = progress->currentCheckpoint;
		if ( cleared > total ) {
			cleared = total;
		}
	}

	if ( total <= 0 || !progress ) {
		Com_sprintf( buffer, bufferSize, "Lap %i", lap );
	} else if ( cg_drawCheckpointRemaining.integer && progress &&
	( progress->runActive || cleared > 0 ) ) {
		int remaining = total - cleared;
		if ( remaining < 0 ) {
			remaining = 0;
		}
		Com_sprintf( buffer, bufferSize, "Lap %i  %i CPs left", lap, remaining );
	} else {
		Com_sprintf( buffer, bufferSize, "Lap %i  CP %i/%i", lap, cleared, total );
	}

	return qtrue;
}

/*
=============
CG_RaceBuildTimesStrings

Builds the race timing ownerdraw text for the active client.
=============
*/
static qboolean CG_RaceBuildTimesStrings( char *primary, size_t primarySize, char *secondary, size_t secondarySize ) {
	const cgRaceClientStatus_t *status;
	cgRaceClientProgress_t *progress;

	if ( primary && primarySize > 0 ) {
		primary[0] = '\0';
	}
	if ( secondary && secondarySize > 0 ) {
		secondary[0] = '\0';
	}

	if ( !CG_RacePrepareHudState( &status, &progress ) ) {
		return qfalse;
	}

	if ( cg.warmup ) {
		if ( primary && primarySize > 0 ) {
			Q_strncpyz( primary, "Warmup", primarySize );
		}
		return qtrue;
	}

	if ( primary && primarySize > 0 ) {
		if ( status && status->currentElapsed >= 0 ) {
			int delta;
			char timeBuffer[32];
			CG_RaceFormatMilliseconds( status->currentElapsed, timeBuffer, sizeof( timeBuffer ) );
			Com_sprintf( primary, primarySize, "Cur %s", timeBuffer );
			if ( CG_RaceCheckpointDelta( status, progress, &delta ) ) {
				char deltaText[32];
				char extra[32];
				CG_RaceFormatDelta( delta, deltaText, sizeof( deltaText ) );
				Com_sprintf( extra, sizeof( extra ), "  d%s", deltaText );
				Q_strcat( primary, primarySize, extra );
			}
		} else if ( status && status->lastTime >= 0 ) {
			char timeBuffer[32];
			CG_RaceFormatMilliseconds( status->lastTime, timeBuffer, sizeof( timeBuffer ) );
			Com_sprintf( primary, primarySize, "Last %s", timeBuffer );
		} else {
			Q_strncpyz( primary, "Ready", primarySize );
		}
	}

	if ( secondary && secondarySize > 0 ) {
		int leaderBest = CG_RaceLeaderBestTime();
		if ( status && status->bestTime >= 0 ) {
			char timeBuffer[32];
			CG_RaceFormatMilliseconds( status->bestTime, timeBuffer, sizeof( timeBuffer ) );
			if ( leaderBest >= 0 ) {
				int delta = status->bestTime - leaderBest;
				char deltaText[32];
				CG_RaceFormatDelta( delta, deltaText, sizeof( deltaText ) );
				Com_sprintf( secondary, secondarySize, "Best %s (%s)", timeBuffer, deltaText );
			} else {
				Com_sprintf( secondary, secondarySize, "Best %s", timeBuffer );
			}
		} else if ( leaderBest >= 0 ) {
			char timeBuffer[32];
			CG_RaceFormatMilliseconds( leaderBest, timeBuffer, sizeof( timeBuffer ) );
			Com_sprintf( secondary, secondarySize, "Leader %s", timeBuffer );
		}
	}

	return qtrue;
}

/*
=============
CG_GetRaceStatusText

Returns the race status ownerdraw text for UI layout calculations.
=============
*/
const char *CG_GetRaceStatusText( void ) {
	static char buffer[64];

	if ( CG_RaceBuildStatusString( buffer, sizeof( buffer ) ) ) {
		return buffer;
	}
	buffer[0] = '\0';
	return buffer;
}

/*
=============
CG_GetRaceTimesPrimaryText

Returns the primary race timing line for UI layout calculations.
=============
*/
const char *CG_GetRaceTimesPrimaryText( void ) {
	static char buffer[64];

	if ( CG_RaceBuildTimesStrings( buffer, sizeof( buffer ), NULL, 0 ) ) {
		return buffer;
	}
	buffer[0] = '\0';
	return buffer;
}

/*
=============
CG_GetRaceTimesSecondaryText

Returns the secondary race timing line for UI layout calculations.
=============
*/
const char *CG_GetRaceTimesSecondaryText( void ) {
	static char buffer[64];

	if ( CG_RaceBuildTimesStrings( NULL, 0, buffer, sizeof( buffer ) ) ) {
		return buffer;
	}
	buffer[0] = '\0';
	return buffer;
}

/*
=============
CG_DrawRaceStatus

Renders the race status ownerdraw (lap and checkpoint info).
=============
*/
static void CG_DrawRaceStatus( rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
	const char *text = CG_GetRaceStatusText();

	if ( !text[0] ) {
		return;
	}

	CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, text, 0, 0, textStyle );
}

/*
=============
CG_DrawRaceTimes

Renders the race timing ownerdraw (current/last and best comparisons).
=============
*/
static void CG_DrawRaceTimes( rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
	char primary[64];
	char secondary[64];
	float lineHeight;

	if ( !CG_RaceBuildTimesStrings( primary, sizeof( primary ), secondary, sizeof( secondary ) ) ) {
		return;
	}

	lineHeight = ( rect->h > 0.0f ) ? rect->h : ( scale * 12.0f );
	CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, primary, 0, 0, textStyle );
	if ( secondary[0] ) {
		CG_Text_Paint( rect->x, rect->y + rect->h + lineHeight, scale, color, secondary, 0, 0, textStyle );
	}
}


// set in CG_ParseTeamInfo

//static int sortedTeamPlayers[TEAM_MAXOVERLAY];
//static int numSortedTeamPlayers;
int drawTeamOverlayModificationCount = -1;

//static char systemChat[256];
//static char teamChat1[256];
//static char teamChat2[256];

/*
=============
CG_IsSelfOnTeamOverlay

Indicates if the local player should appear on the overlay.
=============
*/
qboolean CG_IsSelfOnTeamOverlay( void ) {
	return ( qboolean )( cg_selfOnTeamOverlay.integer != 0 );
}

/*
=============
CG_TeamOverlayXValue

Returns the configured overlay X coordinate.
=============
*/
float CG_TeamOverlayXValue( void ) {
	return cg_drawTeamOverlayX.value;
}

/*
=============
CG_TeamOverlayYValue

Returns the configured overlay Y coordinate.
=============
*/
float CG_TeamOverlayYValue( void ) {
	return cg_drawTeamOverlayY.value;
}

/*
=============
CG_TeamOverlaySizeValue

Returns the overlay size scalar.
=============
*/
float CG_TeamOverlaySizeValue( void ) {
	return cg_drawTeamOverlaySize.value;
}

/*
=============
CG_TeamOverlayOpacityValue

Returns the overlay opacity scalar.
=============
*/
float CG_TeamOverlayOpacityValue( void ) {
	return cg_drawTeamOverlayOpacity.value;
}

static const score_t *CG_GetScoreForClientNum(int clientNum) {
int i;

if (clientNum < 0 || clientNum >= cgs.maxclients) {
return NULL;
}

for (i = 0; i < cg.numScores; i++) {
if (cg.scores[i].client == clientNum) {
return &cg.scores[i];
}
}

return NULL;
}

static void CG_BuildSpectatorClientOrder(void) {
	int i;

	cg.spectatorClientCount = 0;

	for ( i = 0; i < cg.numScores && cg.spectatorClientCount < MAX_CLIENTS; i++ ) {
		int clientNum = cg.scores[i].client;
		clientInfo_t *ci;

		if ( clientNum < 0 || clientNum >= cgs.maxclients ) {
			continue;
		}

		ci = &cgs.clientinfo[clientNum];
		if ( !ci->infoValid || ci->team == TEAM_SPECTATOR ) {
			continue;
		}

		cg.spectatorClientOrder[cg.spectatorClientCount++] = clientNum;
	}

	if ( cg.spectatorClientCount > 0 ) {
		return;
	}

	for ( i = 0; i < cgs.maxclients && cg.spectatorClientCount < MAX_CLIENTS; i++ ) {
		clientInfo_t *ci = &cgs.clientinfo[i];
		if ( !ci->infoValid || ci->team == TEAM_SPECTATOR ) {
			continue;
		}
		cg.spectatorClientOrder[cg.spectatorClientCount++] = i;
	}
}

static void CG_UpdateSpectatorTargets( void ) {
	int i;
	int primary = -1;
	int secondary = -1;

	if ( !cg.snap ) {
		cg.spectatorPrimaryClient = -1;
		cg.spectatorSecondaryClient = -1;
		cg.spectatorClientCount = 0;
		return;
	}

	CG_BuildSpectatorClientOrder();

	if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {
		cg.spectatorFollowClient = cg.snap->ps.clientNum;
	} else {
		cg.spectatorFollowClient = -1;
	}

	if ( cg.spectatorFollowClient >= 0 && cg.spectatorFollowClient < cgs.maxclients ) {
		const clientInfo_t *ci = &cgs.clientinfo[cg.spectatorFollowClient];

		if ( ci->infoValid && ci->team != TEAM_SPECTATOR ) {
			primary = cg.spectatorFollowClient;
		}
	}

	for ( i = 0; primary == -1 && i < cg.spectatorClientCount; i++ ) {
		primary = cg.spectatorClientOrder[i];
	}

	for ( i = 0; i < cg.spectatorClientCount; i++ ) {
		int clientNum = cg.spectatorClientOrder[i];

		if ( clientNum == primary ) {
			continue;
		}

		secondary = clientNum;
		break;
	}

	cg.spectatorPrimaryClient = primary;
	cg.spectatorSecondaryClient = secondary;
	cg.spectatorTargetUpdateTime = cg.time;
}

static const clientInfo_t *CG_SpectatorClientInfo( int slot ) {
	int clientNum = -1;

	if ( slot == 0 ) {
		clientNum = cg.spectatorPrimaryClient;
	} else if ( slot == 1 ) {
		clientNum = cg.spectatorSecondaryClient;
	}

	if ( clientNum < 0 || clientNum >= cgs.maxclients ) {
		return NULL;
	}

	if ( !cgs.clientinfo[clientNum].infoValid ) {
		return NULL;
	}

	return &cgs.clientinfo[clientNum];
}

static const score_t *CG_SpectatorClientScore( int slot ) {
	const clientInfo_t *ci = CG_SpectatorClientInfo( slot );

	if ( !ci ) {
		return NULL;
	}

	return CG_GetScoreForClientNum( ci->clientNum );
}

static qboolean CG_SpectatorSlotFollowed( int slot ) {
	int clientNum = ( slot == 0 ) ? cg.spectatorPrimaryClient : cg.spectatorSecondaryClient;

	return ( clientNum >= 0 && clientNum == cg.spectatorFollowClient );
}

/*
=============
CG_SpectatorSlotTracked

Returns qtrue when the requested spectator slot matches the tracked client.
=============
*/
static qboolean CG_SpectatorSlotTracked( int slot ) {
	int clientNum = -1;

	if ( slot == 0 ) {
		clientNum = cg.spectatorPrimaryClient;
	} else if ( slot == 1 ) {
		clientNum = cg.spectatorSecondaryClient;
	}

	return ( clientNum >= 0 && clientNum == cg.spectatorTrackedClient );
}

/*
=============
CG_IsSpectatorCamera

Returns qtrue when the local client is spectating or following a player.
=============
*/
qboolean CG_IsSpectatorCamera( void ) {
	if ( !cg.snap ) {
		return qfalse;
	}
	if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {
		return qtrue;
	}
	if ( cg.snap->ps.pm_type == PM_SPECTATOR ) {
		return qtrue;
	}
	return ( cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR );
}


/*
=============
CG_ShouldAutoFollowTrack

Determines whether automatic follow commands should be issued for a track event.
=============
*/
static qboolean CG_ShouldAutoFollowTrack( cgSpectatorTrackType_t trackType ) {
	int followMode;

	if ( cg.demoPlayback ) {
		return qfalse;
	}
	if ( !CG_IsSpectatorCamera() ) {
		return qfalse;
	}

	followMode = cg_followPowerup.integer;
	if ( followMode <= 0 ) {
		return qfalse;
	}
	if ( followMode > 1 && trackType != CG_SPECTATOR_TRACK_FLAG ) {
		return qfalse;
	}
	return qtrue;
}

/*
=============
CG_SetTrackPlayerCvarValue

Updates the cg_trackPlayer cvar to the supplied client number.
=============
*/
static void CG_SetTrackPlayerCvarValue( int clientNum ) {
	if ( clientNum < 0 ) {
		if ( cg_trackPlayer.integer != -1 ) {
			trap_Cvar_Set( "cg_trackPlayer", "-1" );
			cg_trackPlayer.integer = -1;
			cg_trackPlayer.value = -1.0f;
		}
		return;
	}

	if ( cg_trackPlayer.integer == clientNum ) {
		return;
	}

	trap_Cvar_Set( "cg_trackPlayer", va( "%d", clientNum ) );
	cg_trackPlayer.integer = clientNum;
	cg_trackPlayer.value = (float)clientNum;
}

/*
=============
CG_SpectatorTrackEvent

Records a potential follow target generated by a powerup or flag event.
=============
*/
void CG_SpectatorTrackEvent( int clientNum, cgSpectatorTrackType_t trackType ) {
	if ( trackType <= CG_SPECTATOR_TRACK_NONE ) {
		return;
	}
	if ( clientNum < 0 || clientNum >= cgs.maxclients ) {
		return;
	}
	if ( !cgs.clientinfo[clientNum].infoValid ) {
		return;
	}

	if ( cg.trackedPlayerClientNum >= 0 &&
		cg.trackedPlayerPriority > trackType &&
		cg.trackedPlayerExpireTime > cg.time ) {
		return;
	}

	cg.trackedPlayerClientNum = clientNum;
	cg.trackedPlayerPriority = trackType;
	cg.trackedPlayerExpireTime = cg.time + CG_SPECTATOR_TRACK_TIMEOUT;

	if ( CG_ShouldAutoFollowTrack( trackType ) ) {
		trap_SendClientCommand( va( "follow %d", clientNum ) );
	}
}

/*
=============
CG_UpdateSpectatorTracking

Maintains the tracked client state and exposes it through cg_trackPlayer.
=============
*/
void CG_UpdateSpectatorTracking( void ) {
	qboolean autoActive = qfalse;
	int target = -1;

	if ( cg.trackedPlayerClientNum >= 0 && cg.trackedPlayerExpireTime > cg.time ) {
		if ( cg.trackedPlayerClientNum < cgs.maxclients &&
			cgs.clientinfo[cg.trackedPlayerClientNum].infoValid ) {
			target = cg.trackedPlayerClientNum;
			autoActive = qtrue;
		} else {
			cg.trackedPlayerClientNum = -1;
			cg.trackedPlayerPriority = CG_SPECTATOR_TRACK_NONE;
			cg.trackedPlayerExpireTime = 0;
		}
	}

	if ( autoActive ) {
		CG_SetTrackPlayerCvarValue( target );
	} else {
		target = cg_trackPlayer.integer;
		if ( target < 0 || target >= cgs.maxclients ||
			!cgs.clientinfo[target].infoValid ) {
			target = -1;
		}
		CG_SetTrackPlayerCvarValue( target );
	}

	cg.spectatorTrackedClient = target;
}


static void CG_GetArmorTierColor(int armor, vec4_t color) {
if (armor >= 150) {
color[0] = 0.9f; color[1] = 0.15f; color[2] = 0.15f; color[3] = 1.0f;
} else if (armor >= 100) {
color[0] = 0.95f; color[1] = 0.75f; color[2] = 0.2f; color[3] = 1.0f;
} else if (armor > 0) {
color[0] = 0.2f; color[1] = 0.8f; color[2] = 0.2f; color[3] = 1.0f;
} else {
color[0] = color[1] = color[2] = 0.4f; color[3] = 0.6f;
}
}

/*
=============
CG_NormalizedTo100

Returns a normalized percentage for values capped at 100.
=============
*/
static float CG_NormalizedTo100(int value) {
return Com_Clamp(0.0f, 100.0f, (float)value) * (1.0f / 100.0f);
}

/*
=============
CG_NormalizedTo200

Returns a normalized percentage for values capped at 200.
=============
*/
static float CG_NormalizedTo200(int value) {
return Com_Clamp(0.0f, 200.0f, (float)value) * (1.0f / 200.0f);
}

/*
=============
CG_DrawBarFill

Renders a clipped portion of the supplied shader using the specified color and ratio.
=============
*/
static void CG_DrawBarFill(const rectDef_t *rect, qhandle_t shader, float fraction, const vec4_t color) {
float x;
float y;
float w;
float h;

if (!rect) {
return;
}

if (fraction <= 0.0f || rect->w <= 0.0f || rect->h <= 0.0f) {
return;
}

if (fraction > 1.0f) {
fraction = 1.0f;
}

if (shader) {
x = rect->x;
y = rect->y;
w = rect->w * fraction;
h = rect->h;
CG_AdjustFrom640(&x, &y, &w, &h);
trap_R_SetColor(color);
trap_R_DrawStretchPic(x, y, w, h, 0.0f, 0.0f, fraction, 1.0f, shader);
trap_R_SetColor(NULL);
} else {
CG_FillRect(rect->x, rect->y, rect->w * fraction, rect->h, color);
}
}

/*
=============
CG_DrawPlayerHealthBar

Draws the player health fill bar for either the 0-100 or 0-200 range.
=============
*/
static void CG_DrawPlayerHealthBar(rectDef_t *rect, qhandle_t shader, qboolean use200Range) {
vec4_t barColor;
float ratio;
int health;
int armor;

if (!cg.snap) {
return;
}

health = cg.snap->ps.stats[STAT_HEALTH];
armor = cg.snap->ps.stats[STAT_ARMOR];
CG_GetColorForHealth(health, armor, barColor);
barColor[3] = 1.0f;
ratio = (use200Range) ? CG_NormalizedTo200(health) : CG_NormalizedTo100(health);

if (!shader) {
shader = (use200Range) ? cgs.media.healthBar200 : cgs.media.healthBar100;
}

CG_DrawBarFill(rect, shader, ratio, barColor);
}

/*
=============
CG_DrawPlayerArmorBar

Draws the player armor fill bar for either the 0-100 or 0-200 range.
=============
*/
static void CG_DrawPlayerArmorBar(rectDef_t *rect, qhandle_t shader, qboolean use200Range) {
vec4_t barColor;
float ratio;
int armor;

if (!cg.snap) {
return;
}

armor = cg.snap->ps.stats[STAT_ARMOR];
CG_GetArmorTierColor(armor, barColor);
barColor[3] = 1.0f;
ratio = (use200Range) ? CG_NormalizedTo200(armor) : CG_NormalizedTo100(armor);

if (!shader) {
shader = (use200Range) ? cgs.media.armorBar200 : cgs.media.armorBar100;
}

CG_DrawBarFill(rect, shader, ratio, barColor);
}

/*
=============
CG_CountLivingPlayers

Determines how many teammates and enemies are alive based on clientinfo health data.
=============
*/
static void CG_CountLivingPlayers(int *friendCount, int *enemyCount) {
team_t myTeam;
int i;

if (!friendCount || !enemyCount) {
return;
}

*friendCount = 0;
*enemyCount = 0;

if (!cg.snap) {
return;
}

myTeam = cg.snap->ps.persistant[PERS_TEAM];
if (myTeam == TEAM_SPECTATOR && (cg.snap->ps.pm_flags & PMF_FOLLOW)) {
int followClient = cg.snap->ps.clientNum;
if (followClient >= 0 && followClient < cgs.maxclients && cgs.clientinfo[followClient].infoValid) {
myTeam = cgs.clientinfo[followClient].team;
}
}

for (i = 0; i < cgs.maxclients; i++) {
const clientInfo_t *ci = &cgs.clientinfo[i];
team_t team;
qboolean alive;

if (!ci->infoValid) {
continue;
}

team = ci->team;
if (team != TEAM_RED && team != TEAM_BLUE) {
continue;
}

if (i == cg.snap->ps.clientNum) {
alive = (cg.snap->ps.stats[STAT_HEALTH] > 0);
} else {
alive = (ci->health > 0);
}

if (!alive) {
continue;
}

if (team == myTeam) {
(*friendCount)++;
} else {
(*enemyCount)++;
}
}
}

/*
=============
CG_DrawPlayerCount

Draws the text for either the friendly or enemy player count widgets.
=============
*/
static void CG_DrawPlayerCount(rectDef_t *rect, float scale, vec4_t color, int textStyle, qboolean friendly) {
char buffer[8];
int friendCount;
int enemyCount;
int width;

CG_CountLivingPlayers(&friendCount, &enemyCount);
Com_sprintf(buffer, sizeof(buffer), "%i", friendly ? friendCount : enemyCount);
width = CG_Text_Width(buffer, scale, 0);
		CG_Text_Paint(rect->x + (rect->w - width) * 0.5f, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}

/*
=============
CG_SampleSpeedometer

Samples and caches the player's horizontal speed for the current frame.
=============
*/
static float CG_SampleSpeedometer(void) {
vec3_t horizontalVelocity;

if (!cg.snap) {
cg.speedometerSample = 0.0f;
cg.speedometerSampleTime = cg.time;
return 0.0f;
}

if (cg.speedometerSampleTime == cg.time) {
return cg.speedometerSample;
}

VectorCopy(cg.snap->ps.velocity, horizontalVelocity);
horizontalVelocity[2] = 0.0f;
cg.speedometerSample = VectorLength(horizontalVelocity);
cg.speedometerSampleTime = cg.time;
return cg.speedometerSample;
}

/*
=============
CG_DrawSpeedometer

Renders the HUD speedometer text when the corresponding cvar is enabled.
=============
*/
static void CG_DrawSpeedometer(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
char buffer[32];
float speed;
int width;

if (!CG_ShouldDrawSpeedometer()) {
return;
}

speed = CG_SampleSpeedometer();
Com_sprintf(buffer, sizeof(buffer), "%i", (int)(speed + 0.5f));
width = CG_Text_Width(buffer, scale, 0);
CG_Text_Paint(rect->x + (rect->w - width) * 0.5f, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}

void CG_SpectatorFollowCycle(int dir) {
int i;
int index = -1;
int newClient;

CG_UpdateSpectatorTargets();

if (cg.spectatorClientCount <= 0) {
return;
}

for (i = 0; i < cg.spectatorClientCount; i++) {
if (cg.spectatorClientOrder[i] == cg.spectatorFollowClient) {
index = i;
break;
}
}

if (index == -1) {
index = 0;
}

index = (index + dir + cg.spectatorClientCount) % cg.spectatorClientCount;
newClient = cg.spectatorClientOrder[index];

trap_SendClientCommand(va("follow %d", newClient));
}

/*
=============
CG_DrawSpectatorPlayerName

Renders the tracked spectator player name with an optional backing shader.
=============
*/
static void CG_DrawSpectatorPlayerName(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot, qhandle_t shader) {
	const clientInfo_t *ci = CG_SpectatorClientInfo( slot );
	vec4_t drawColor;
	vec4_t modulate;
	float x;
	float y;
	float w;
	float h;

	if ( !ci ) {
		return;
	}

	if ( shader ) {
		Vector4Set( modulate, 1.0f, 1.0f, 1.0f, 1.0f );
		x = rect->x;
		y = rect->y;
		w = rect->w;
		h = rect->h;
		CG_AdjustFrom640( &x, &y, &w, &h );
		trap_R_SetColor( modulate );
		trap_R_DrawStretchPic( x, y, w, h, 0.0f, 0.0f, 1.0f, 1.0f, shader );
		trap_R_SetColor( NULL );
	}

	Vector4Copy( color, drawColor );
	if ( CG_SpectatorSlotFollowed( slot ) || CG_SpectatorSlotTracked( slot ) ) {
		drawColor[3] = 1.0f;
	}

	CG_Text_Paint( rect->x, rect->y, scale, drawColor, ci->name, 0, 0, textStyle );
}

static void CG_DrawSpectatorPlayerScore(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot) {
const score_t *score = CG_SpectatorClientScore(slot);
char buffer[32];

if (!score) {
return;
}

Com_sprintf(buffer, sizeof(buffer), "%d", score->score);
CG_Text_Paint(rect->x, rect->y, scale, color, buffer, 0, 0, textStyle);
}

static void CG_DrawSpectatorHealthArmor(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot) {
const clientInfo_t *ci = CG_SpectatorClientInfo(slot);
vec4_t healthColor;
vec4_t armorColor;
vec4_t baseColor = { 0.0f, 0.0f, 0.0f, 0.45f };
char buffer[32];
float healthWidth, armorWidth;
int health;
int armor;

if (!ci) {
return;
}

(void)color;

health = ci->health;
armor = ci->armor;
if (health < 0) {
health = 0;
}
if (armor < 0) {
armor = 0;
}

CG_GetColorForHealth(health, armor, healthColor);
CG_GetArmorTierColor(armor, armorColor);

healthColor[3] = 0.85f;
armorColor[3] = 0.7f;

healthWidth = rect->w * Com_Clamp(0.0f, 1.0f, (float)health / 200.0f);
armorWidth = rect->w * Com_Clamp(0.0f, 1.0f, (float)armor / 200.0f);

CG_FillRect(rect->x, rect->y, rect->w, rect->h, baseColor);
CG_FillRect(rect->x, rect->y, healthWidth, rect->h * 0.65f, healthColor);
CG_FillRect(rect->x, rect->y + rect->h * 0.65f, armorWidth, rect->h * 0.35f, armorColor);

{
vec4_t textColor = { 1.0f, 1.0f, 1.0f, 1.0f };
Com_sprintf(buffer, sizeof(buffer), "%d / %d", health, armor);
CG_Text_Paint(rect->x + 2, rect->y + rect->h - 2, scale, textColor, buffer, 0, 0, textStyle);
}
}

/*
=============
CG_GetProfileFallbackShader

Resolves the shader used when a client icon is unavailable.
=============
*/
static qhandle_t CG_GetProfileFallbackShader(void) {
	static qhandle_t fallback;

	if (!fallback) {
		fallback = trap_R_RegisterShaderNoMip("ui/assets/hud/armor.tga");
		if (!fallback) {
			fallback = cgs.media.deferShader;
		}
	}

	return fallback;
}

/*
=============
CG_DrawSpectatorProfileImage

Draws the tracked player's avatar or fallback profile image.
=============
*/
static void CG_DrawSpectatorProfileImage(rectDef_t *rect, int slot) {
	const clientInfo_t *ci;
	qhandle_t shader;
	vec4_t modulate;

	if (!cg_drawProfileImages.integer) {
		return;
	}

	ci = CG_SpectatorClientInfo(slot);
	if (!ci) {
		return;
	}

	shader = ci->modelIcon;
	if (!shader) {
		shader = CG_GetProfileFallbackShader();
	}

	if (!shader) {
		return;
	}

	Vector4Set(modulate, 1.0f, 1.0f, 1.0f, CG_SpectatorSlotFollowed(slot) ? 1.0f : 0.6f);
	trap_R_SetColor(modulate);
	CG_DrawPic(rect->x, rect->y, rect->w, rect->h, shader);

/*
=============
CG_GetSelectedScore

Returns the currently selected scoreboard entry, if available.
=============
*/
score_t *CG_GetSelectedScore( void ) {
	if ( cg.numScores <= 0 ) {
		return NULL;
	}

	if ( cg.selectedScore < 0 || cg.selectedScore >= cg.numScores ) {
		return NULL;
	}

	return &cg.scores[cg.selectedScore];
}

/*
=============
CG_GetSelectedClientInfo

Resolves the client information for the currently selected scoreboard entry.
=============
*/
static clientInfo_t *CG_GetSelectedClientInfo( void ) {
	score_t		*score;

	score = CG_GetSelectedScore();
	if ( !score ) {
		return NULL;
	}

	if ( score->client < 0 || score->client >= cgs.maxclients ) {
		return NULL;
	}

	return &cgs.clientinfo[score->client];
}

/*
=============
CG_GetTeamLabel

Provides a human readable label for the supplied team.
=============
*/
static const char *CG_GetTeamLabel( team_t team ) {
	switch ( team ) {
	case TEAM_RED:
		return ( cg_redTeamName.string[0] != '\0' ) ? cg_redTeamName.string : DEFAULT_REDTEAM_NAME;
	case TEAM_BLUE:
		return ( cg_blueTeamName.string[0] != '\0' ) ? cg_blueTeamName.string : DEFAULT_BLUETEAM_NAME;
	default:
		return "Spectator";
	}
}

/*
=============
CG_CountPlayersForTeam

Counts the number of scoreboard entries assigned to a specific team.
=============
*/
static int CG_CountPlayersForTeam( team_t team ) {
	int		count;
	int		i;

	count = 0;
	for ( i = 0; i < cg.numScores; i++ ) {
		if ( cg.scores[i].team == team ) {
			count++;
		}
	}

	return count;
}

/*
=============
CG_CountActivePlayers

Returns the number of scoreboard entries that are not spectators.
=============
*/
static int CG_CountActivePlayers( void ) {
	int		count;
	int		i;

	count = 0;
	for ( i = 0; i < cg.numScores; i++ ) {
		if ( cg.scores[i].team != TEAM_SPECTATOR ) {
			count++;
		}
	}

	return count;
}

/*
=============
CG_CleanMapName

Normalizes a map path to just the BSP name without extensions.
=============
*/
static void CG_CleanMapName( const char *input, char *output, size_t outputSize ) {
	char					*ext;

	if ( !output || outputSize <= 0 ) {
		return;
	}

	output[0] = '\0';
	if ( !input || !*input ) {
		return;
	}

	Q_strncpyz( output, input, outputSize );
	if ( !Q_stricmpn( output, "maps/", 5 ) ) {
		memmove( output, output + 5, strlen( output + 5 ) + 1 );
	}

	ext = strrchr( output, '.' );
	if ( ext ) {
		*ext = '\0';
	}
}

/*
=============
CG_BuildCleanMapName

Resolves the current map name in a player-friendly format.
=============
*/
static void CG_BuildCleanMapName( char *buffer, size_t bufferSize ) {
	const char	*serverInfo;
	const char	*configName;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	buffer[0] = '\0';
	serverInfo = CG_ConfigString( CS_SERVERINFO );
	configName = serverInfo ? Info_ValueForKey( serverInfo, "mapname" ) : NULL;
	if ( configName && *configName ) {
		CG_CleanMapName( configName, buffer, bufferSize );
		return;
	}

	if ( cgs.mapname[0] != '\0' ) {
		CG_CleanMapName( cgs.mapname, buffer, bufferSize );
		return;
	}

	Q_strncpyz( buffer, "Unknown", bufferSize );
}

/*
=============
CG_DrawMapName

Prints the current map name stripped of file path information.
=============
*/
static void CG_DrawMapName(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	char		nameBuffer[MAX_QPATH];

	CG_BuildCleanMapName( nameBuffer, sizeof( nameBuffer ) );
	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, nameBuffer, 0, 0, textStyle);
}

/*
=============
CG_GetServerLocationString

Extracts the server-provided location or hostname for HUD displays.
=============
*/
static void CG_GetServerLocationString( char *buffer, size_t bufferSize ) {
	const char	*info;
	const char	*location;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	buffer[0] = '\0';
	info = CG_ConfigString( CS_SERVERINFO );
	if ( info && *info ) {
		location = Info_ValueForKey( info, "location" );
		if ( location && *location ) {
			Q_strncpyz( buffer, location, bufferSize );
			return;
		}

		location = Info_ValueForKey( info, "sv_location" );
		if ( location && *location ) {
			Q_strncpyz( buffer, location, bufferSize );
			return;
		}

		location = Info_ValueForKey( info, "sv_hostname" );
		if ( location && *location ) {
			Q_strncpyz( buffer, location, bufferSize );
			return;
		}
	}

	Q_strncpyz( buffer, "Unknown server", bufferSize );
}

/*
=============
CG_DrawPlayerCounts

Renders the number of active players versus the server capacity.
=============
*/
static void CG_DrawPlayerCounts(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	char	buffer[32];
	int		active;

	active = CG_CountActivePlayers();
	Com_sprintf( buffer, sizeof( buffer ), "%i/%i players", active, cgs.maxclients );
	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}


/*
=============
CG_GetServerInfoValue

Looks up a key in the CS_SERVERINFO string and copies it into the caller's buffer.
=============
*/
static void CG_GetServerInfoValue( const char *info, const char *key, char *buffer, size_t bufferSize ) {
	const char *value;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !info || !*info || !key ) {
		return;
	}

	value = Info_ValueForKey( info, key );
	if ( value && *value ) {
		Q_strncpyz( buffer, value, bufferSize );
	}
}

/*
=============
CG_GetMapDisplayName

Builds a human-readable map name stripped of directory prefixes and extensions.
=============
*/
static void CG_GetMapDisplayName( char *buffer, size_t bufferSize ) {
	const char *info;
	const char *configName;
	char		name[MAX_QPATH];
	char		*ext;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	info = CG_ConfigString( CS_SERVERINFO );
	configName = NULL;
	if ( info && *info ) {
		configName = Info_ValueForKey( info, "mapname" );
	}

	if ( configName && *configName ) {
		Q_strncpyz( name, configName, sizeof( name ) );
	} else if ( cgs.mapname[0] != '\0' ) {
		Q_strncpyz( name, cgs.mapname, sizeof( name ) );
	} else {
		Q_strncpyz( name, "Unknown", sizeof( name ) );
	}

	if ( !Q_stricmpn( name, "maps/", 5 ) ) {
		memmove( name, name + 5, strlen( name + 5 ) + 1 );
	}

	ext = strrchr( name, '.' );
	if ( ext ) {
		*ext = '\0';
	}

	Q_strncpyz( buffer, name, bufferSize );
}

/*
=============
CG_GetServerLocation

Returns the best-effort server location string from the serverinfo block.
=============
*/
static void CG_GetServerLocation( char *buffer, size_t bufferSize ) {
	const char *info;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	info = CG_ConfigString( CS_SERVERINFO );
	buffer[0] = '\0';
	if ( info && *info ) {
		CG_GetServerInfoValue( info, "location", buffer, bufferSize );
		if ( !buffer[0] ) {
			CG_GetServerInfoValue( info, "sv_location", buffer, bufferSize );
		}
		if ( !buffer[0] ) {
			CG_GetServerInfoValue( info, "server_location", buffer, bufferSize );
		}
	}

	if ( !buffer[0] ) {
		Q_strncpyz( buffer, "Unknown location", bufferSize );
	}
}

/*
=============
CG_GameTypeShortString

Maps the active gametype to its short label (FFA, TDM, etc.).
=============
*/
static const char *CG_GameTypeShortString( void ) {
	switch ( cgs.gametype ) {
	case GT_FFA:
		return "FFA";
	case GT_TOURNAMENT:
		return "Duel";
	case GT_SINGLE_PLAYER:
		return "Race";
	case GT_TEAM:
		return "TDM";
	case GT_CLAN_ARENA:
		return "CA";
	case GT_CTF:
		return "CTF";
	case GT_1FCTF:
		return "1FCTF";
	case GT_OBELISK:
		return "Overload";
	case GT_HARVESTER:
		return "Harvester";
	case GT_FREEZE:
		return "Freeze";
	case GT_DOMINATION:
		return "Domination";
	case GT_ATTACK_DEFEND:
		return "Attack & Defend";
	case GT_RED_ROVER:
		return "Red Rover";
	default:
		return "";
	}
}

/*
=============
CG_GetTextPosition

Applies text_x/text_y offsets to the provided rectangle and returns the draw origin.
=============
*/
static void CG_GetTextPosition( const rectDef_t *rect, float text_x, float text_y, float *outX, float *outY ) {
	float x;
	float y;

	x = rect->x + text_x;
	y = rect->y + rect->h + text_y;

	if ( outX ) {
		*outX = x;
	}
	if ( outY ) {
		*outY = y;
	}
}

/*
=============
CG_AppendServerSetting

Appends a fragment to the composite server settings line.
=============
*/
static void CG_AppendServerSetting( char *buffer, size_t bufferSize, const char *text ) {
	if ( !buffer || bufferSize <= 0 || !text || !*text ) {
		return;
	}

	if ( buffer[0] ) {
		Q_strcat( buffer, bufferSize, "  |  " );
	}
	Q_strcat( buffer, bufferSize, text );
}

/*
=============
CG_DrawServerSettings

Summarizes factory metadata and server toggles for the intro/about overlays.
=============
*/
static void CG_DrawServerSettings(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle) {
	char	buffer[256];
	char	value[MAX_INFO_VALUE];
	const char *info;
	float	x;
	float	y;
	qboolean loadoutsEnabled;
	qboolean itemTimersEnabled;
	qboolean trainingEnabled;

	info = CG_ConfigString( CS_SERVERINFO );
	buffer[0] = '\0';
	loadoutsEnabled = CG_LoadoutsEnabled();
	itemTimersEnabled = qfalse;
	trainingEnabled = qfalse;

	if ( info && *info ) {
		CG_GetServerInfoValue( info, "g_itemTimers", value, sizeof( value ) );
		if ( value[0] && atoi( value ) ) {
			itemTimersEnabled = qtrue;
		}
		CG_GetServerInfoValue( info, "g_training", value, sizeof( value ) );
		if ( value[0] && atoi( value ) ) {
			trainingEnabled = qtrue;
		}
	}

	if ( cgs.factoryTitle[0] ) {
		CG_AppendServerSetting( buffer, sizeof( buffer ), cgs.factoryTitle );
	} else {
		CG_AppendServerSetting( buffer, sizeof( buffer ), "Standard factory" );
	}
	CG_AppendServerSetting( buffer, sizeof( buffer ), loadoutsEnabled ? "Loadouts on" : "Loadouts off" );
	CG_AppendServerSetting( buffer, sizeof( buffer ), itemTimersEnabled ? "Item timers on" : "Item timers off" );
	if ( trainingEnabled ) {
		CG_AppendServerSetting( buffer, sizeof( buffer ), "Training mode" );
	}

	if ( !buffer[0] ) {
		return;
	}

	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawStartingWeapons

Lists the spawn loadout when the server advertises g_startingWeapons.
=============
*/
static void CG_DrawStartingWeapons(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle) {
	const char *info;
	char		value[MAX_INFO_VALUE];
	int		mask;
	int		weapon;
	char		buffer[256];
	float	x;
	float	y;
	qboolean listed;

	info = CG_ConfigString( CS_SERVERINFO );
	if ( !info || !*info ) {
		return;
	}

	CG_GetServerInfoValue( info, "g_startingWeapons", value, sizeof( value ) );
	mask = value[0] ? (int)strtol( value, NULL, 0 ) : 0;
	buffer[0] = '\0';
	listed = qfalse;

	for ( weapon = WP_GAUNTLET; weapon < WP_NUM_WEAPONS; weapon++ ) {
		int bit;
		const char *weaponName;

		bit = 1 << ( weapon - 1 );
		if ( ( mask & bit ) == 0 ) {
			continue;
		}

		weaponName = CG_ResolveWeaponName( weapon );
		if ( !weaponName ) {
			continue;
		}

		if ( listed ) {
			Q_strcat( buffer, sizeof( buffer ), ", " );
		}
		Q_strcat( buffer, sizeof( buffer ), weaponName );
		listed = qtrue;
	}

	if ( !listed ) {
		if ( CG_LoadoutsEnabled() ) {
			Q_strncpyz( buffer, "Factory loadouts active", sizeof( buffer ) );
		} else {
			Q_strncpyz( buffer, "Default loadout", sizeof( buffer ) );
		}
	}

	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, buffer, 0, 0, textStyle );
}


/*
=============
CG_DrawGameLimit

Describes the active timelimit and score limits for the match.
=============
*/
static void CG_DrawGameLimit(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle) {
	char	buffer[128];
	const char *info;
	int		limitValue;
	char		value[MAX_INFO_VALUE];
	float	x;
	float	y;

	buffer[0] = '\0';
	info = CG_ConfigString( CS_SERVERINFO );

	if ( cgs.timelimit > 0 ) {
		char segment[32];
		Com_sprintf( segment, sizeof( segment ), "Time %i", cgs.timelimit );
		CG_AppendServerSetting( buffer, sizeof( buffer ), segment );
	}

	limitValue = 0;
	if ( cgs.gametype >= GT_CTF && cgs.gametype != GT_ATTACK_DEFEND ) {
		limitValue = cgs.capturelimit;
		if ( limitValue > 0 ) {
			char segment[32];
			Com_sprintf( segment, sizeof( segment ), "Captures %i", limitValue );
			CG_AppendServerSetting( buffer, sizeof( buffer ), segment );
		}
	} else if ( cgs.gametype == GT_ATTACK_DEFEND ) {
		if ( info && *info ) {
			CG_GetServerInfoValue( info, "g_scorelimit", value, sizeof( value ) );
			limitValue = value[0] ? atoi( value ) : 0;
		}
		if ( limitValue > 0 ) {
			char segment[32];
			Com_sprintf( segment, sizeof( segment ), "Score %i", limitValue );
			CG_AppendServerSetting( buffer, sizeof( buffer ), segment );
		}
	} else if ( cgs.fraglimit > 0 ) {
		char segment[32];
		Com_sprintf( segment, sizeof( segment ), "Frags %i", cgs.fraglimit );
		CG_AppendServerSetting( buffer, sizeof( buffer ), segment );
	}

	if ( info && *info ) {
		CG_GetServerInfoValue( info, "mercylimit", value, sizeof( value ) );
		limitValue = value[0] ? atoi( value ) : 0;
		if ( limitValue > 0 ) {
			char segment[32];
			Com_sprintf( segment, sizeof( segment ), "Mercy %i", limitValue );
			CG_AppendServerSetting( buffer, sizeof( buffer ), segment );
		}
	}

	if ( !buffer[0] ) {
		return;
	}

	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_GameTypeIconShader

Returns the shader handle for the supplied gametype icon, registering it on demand.
=============
*/
static qhandle_t CG_GameTypeIconShader( gametype_t gametype ) {
	static const char *paths[GT_MAX_GAME_TYPE] = {
		[GT_FFA] = "ui/assets/hud/ffa.png",
		[GT_TOURNAMENT] = "ui/assets/hud/duel.png",
		[GT_SINGLE_PLAYER] = "ui/assets/hud/race.png",
		[GT_TEAM] = "ui/assets/hud/tdm.png",
		[GT_CLAN_ARENA] = "ui/assets/hud/ca.png",
		[GT_CTF] = "ui/assets/hud/ctf.png",
		[GT_1FCTF] = "ui/assets/hud/flag.png",
		[GT_OBELISK] = "ui/assets/hud/dom.png",
		[GT_HARVESTER] = "ui/assets/hud/har.png",
		[GT_FREEZE] = "ui/assets/hud/ft.png",
		[GT_DOMINATION] = "ui/assets/hud/dom.png",
		[GT_ATTACK_DEFEND] = "ui/assets/hud/ad.png",
		[GT_RED_ROVER] = "ui/assets/hud/rr.png"
	};
	static qhandle_t shaders[GT_MAX_GAME_TYPE];

	if ( gametype < 0 || gametype >= GT_MAX_GAME_TYPE ) {
		return 0;
	}

	if ( !shaders[gametype] && paths[gametype] ) {
		shaders[gametype] = trap_R_RegisterShaderNoMip( paths[gametype] );
	}

	return shaders[gametype];
}

/*
=============
CG_DrawGameTypeIcon

Paints the current gametype icon using the HUD asset bundle.
=============
*/
static void CG_DrawGameTypeIcon(rectDef_t *rect) {
	qhandle_t shader;

	shader = CG_GameTypeIconShader( cgs.gametype );
	if ( !shader ) {
		return;
	}

	CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );
}

/*
=============
CG_DrawGameTypeMap

Outputs "Gametype Fullname - Server Location - Map" for intro panels.
=============
*/
static void CG_DrawGameTypeMap(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle) {
	char	location[64];
	char	mapName[MAX_QPATH];
	char	buffer[256];
	float	x;
	float	y;

	CG_GetServerLocation( location, sizeof( location ) );
	CG_GetMapDisplayName( mapName, sizeof( mapName ) );
	Com_sprintf( buffer, sizeof( buffer ), "%s - %s - %s", CG_GameTypeString(), location, mapName );

	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_GetMatchStateLabel

Summarizes the current match flow state for HUD text.
=============
*/
static const char *CG_GetMatchStateLabel( void ) {
	static char buffer[32];

	if ( cgs.matchTimeoutActive ) {
		return "Timeout";
	}
	if ( cgs.matchOvertimeActive ) {
		return "Overtime";
	}
	if ( cg.snap && cg.snap->ps.pm_type == PM_INTERMISSION ) {
		return "Intermission";
	}
	if ( cgs.matchRoundState == ROUNDSTATE_WARMUP || cg.warmup > 0 ) {
		return "Warmup";
	}
	if ( cgs.matchRoundState == ROUNDSTATE_COMPLETE ) {
		return "Round complete";
	}
	if ( cgs.matchRoundNumber > 0 ) {
		Com_sprintf( buffer, sizeof( buffer ), "Round %i", cgs.matchRoundNumber );
		return buffer;
	}
	return "In progress";
}

/*
=============
CG_DrawMatchDetails

Renders "Game state - Gametype Shortname - Server Location - Map" text.
=============
*/
static void CG_DrawMatchDetails(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle) {
	char	location[64];
	char	mapName[MAX_QPATH];
	char	buffer[256];
	float	x;
	float	y;

	CG_GetServerLocation( location, sizeof( location ) );
	CG_GetMapDisplayName( mapName, sizeof( mapName ) );
	Com_sprintf( buffer, sizeof( buffer ), "%s - %s - %s - %s", CG_GetMatchStateLabel(), CG_GameTypeShortString(), location, mapName );

	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, buffer, 0, 0, textStyle );
}

static qboolean CG_TimeLimitHit( void ) {
	if ( cgs.timelimit <= 0 || cgs.levelStartTime <= 0 ) {
		return qfalse;
	}
	return ( cg.time - cgs.levelStartTime ) >= cgs.timelimit * 60000;
}

static qboolean CG_FragLimitHit( void ) {
	if ( cgs.fraglimit <= 0 ) {
		return qfalse;
	}
	if ( cgs.scores1 != SCORE_NOT_PRESENT && cgs.scores1 >= cgs.fraglimit ) {
		return qtrue;
	}
	return qfalse;
}

static qboolean CG_CaptureLimitHit( void ) {
	if ( cgs.capturelimit <= 0 ) {
		return qfalse;
	}
	if ( cgs.scores1 != SCORE_NOT_PRESENT && cgs.scores1 >= cgs.capturelimit ) {
		return qtrue;
	}
	if ( cgs.scores2 != SCORE_NOT_PRESENT && cgs.scores2 >= cgs.capturelimit ) {
		return qtrue;
	}
	return qfalse;
}

static qboolean CG_ScoreLimitHit( void ) {
	const char *info;
	char		value[MAX_INFO_VALUE];
	int		limit;

	info = CG_ConfigString( CS_SERVERINFO );
	if ( !info || !*info ) {
		return qfalse;
	}
	CG_GetServerInfoValue( info, "g_scorelimit", value, sizeof( value ) );
	limit = value[0] ? atoi( value ) : 0;
	if ( limit <= 0 ) {
		return qfalse;
	}
	if ( cgs.scores1 != SCORE_NOT_PRESENT && cgs.scores1 >= limit ) {
		return qtrue;
	}
	if ( cgs.scores2 != SCORE_NOT_PRESENT && cgs.scores2 >= limit ) {
		return qtrue;
	}
	return qfalse;
}

static qboolean CG_MercyLimitHit( void ) {
	const char *info;
	char		value[MAX_INFO_VALUE];
	int		limit;
	int		delta;

	info = CG_ConfigString( CS_SERVERINFO );
	if ( !info || !*info ) {
		return qfalse;
	}
	CG_GetServerInfoValue( info, "mercylimit", value, sizeof( value ) );
	limit = value[0] ? atoi( value ) : 0;
	if ( limit <= 0 ) {
		return qfalse;
	}
	if ( cgs.scores1 == SCORE_NOT_PRESENT || cgs.scores2 == SCORE_NOT_PRESENT ) {
		return qfalse;
	}
	delta = abs( cgs.scores1 - cgs.scores2 );
	return ( delta >= limit );
}

/*
=============
CG_DrawMatchEndCondition

Summarizes why the previous match ended (time, frag limit, mercy, etc.).
=============
*/
static void CG_DrawMatchEndCondition(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle) {
	const char *reason;
	float x;
	float y;

	reason = "Match complete";
	if ( CG_TimeLimitHit() ) {
		reason = "Time limit hit";
	} else if ( CG_CaptureLimitHit() ) {
		reason = "Capture limit hit";
	} else if ( CG_ScoreLimitHit() ) {
		reason = "Score limit hit";
	} else if ( CG_FragLimitHit() ) {
		reason = "Frag limit hit";
	} else if ( CG_MercyLimitHit() ) {
		reason = "Mercy rule";
	} else if ( cgs.matchOvertimeActive ) {
		reason = "Sudden death";
	}

	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, reason, 0, 0, textStyle );
}

/*
=============
CG_DrawMatchStatus

Renders "Game State - Scores message" using the existing HUD helpers.
=============
*/
static void CG_DrawMatchStatus(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle) {
	char	buffer[256];
	float	x;
	float	y;

	if ( !cg.snap ) {
		return;
	}

	Com_sprintf( buffer, sizeof( buffer ), "%s - %s", CG_GetMatchStateLabel(), CG_GetGameStatusText() );
	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawRoundLabel

Displays the current round or match state string.
=============
*/
static void CG_DrawRoundLabel(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle) {
	const char	*label;
	float		x;
	float		y;

	label = CG_GetMatchStateLabel();
	if ( !label || !*label ) {
		return;
	}

	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, label, 0, 0, textStyle );
}

/*
=============
CG_DrawLocalTime

Paints the client's current local time in hours and minutes.
=============
*/
static void CG_DrawLocalTime(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle) {
	qtime_t	qt;
	char	buffer[32];
	float	x;
	float	y;

	trap_RealTime( &qt );
	Com_sprintf( buffer, sizeof( buffer ), "%02i:%02i", qt.tm_hour, qt.tm_min );

	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_BuildVoteSlotCvarName

Formats the ui_vote cvar name for the requested slot and suffix.
=============
*/
static void CG_BuildVoteSlotCvarName( int slot, const char *suffix, char *buffer, size_t bufferSize ) {
	if ( !buffer || bufferSize <= 0 || !suffix ) {
		return;
	}

	Com_sprintf( buffer, bufferSize, "ui_vote%s%i", suffix, slot );
}

/*
=============
CG_GetVoteSlotString

Reads the text payload for a vote slot helper cvar into buffer.
=============
*/
static void CG_GetVoteSlotString( int slot, const char *suffix, char *buffer, size_t bufferSize ) {
	char name[MAX_QPATH];

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}
	buffer[0] = '\0';
	if ( slot < 1 || slot > 3 ) {
		return;
	}
	CG_BuildVoteSlotCvarName( slot, suffix, name, sizeof( name ) );
	trap_Cvar_VariableStringBuffer( name, buffer, bufferSize );
}

typedef struct {
	char		path[MAX_QPATH];
	qhandle_t	handle;
} cgVoteShotCache_t;

static cgVoteShotCache_t cg_voteShotCache[3];

/*
=============
CG_DrawVoteShot

Displays the screenshot preview tied to a given vote option slot.
=============
*/
static void CG_DrawVoteShot(rectDef_t *rect, int slot) {
	char	path[MAX_QPATH];
	cgVoteShotCache_t *cache;

	if ( slot < 1 || slot > 3 ) {
		return;
	}
	cache = &cg_voteShotCache[slot - 1];
	CG_GetVoteSlotString( slot, "Shot", path, sizeof( path ) );
	if ( !path[0] ) {
		return;
	}
	if ( Q_stricmp( cache->path, path ) ) {
		cache->handle = trap_R_RegisterShaderNoMip( path );
		Q_strncpyz( cache->path, path, sizeof( cache->path ) );
	}
	if ( !cache->handle ) {
		return;
	}
	CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cache->handle );
}

/*
=============
CG_DrawVoteGametype

Renders the gametype label text for the specified vote slot.
=============
*/
static void CG_DrawVoteGametype(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle, int slot) {
	char	buffer[MAX_CVAR_VALUE_STRING];
	float	x;
	float	y;

	CG_GetVoteSlotString( slot, "Gametype", buffer, sizeof( buffer ) );
	if ( !buffer[0] ) {
		return;
	}
	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawVoteName

Shows the prettified map name for the selected vote slot.
=============
*/
static void CG_DrawVoteName(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle, int slot) {
	char	buffer[MAX_CVAR_VALUE_STRING];
	float	x;
	float	y;

	CG_GetVoteSlotString( slot, "Name", buffer, sizeof( buffer ) );
	if ( !buffer[0] ) {
		CG_GetVoteSlotString( slot, "Map", buffer, sizeof( buffer ) );
		if ( !buffer[0] ) {
			return;
		}
	}
	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawVoteMapSlot

Outputs the raw map name string for the vote slot widget.
=============
*/
static void CG_DrawVoteMapSlot(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle, int slot) {
	char	buffer[MAX_CVAR_VALUE_STRING];
	float	x;
	float	y;

	CG_GetVoteSlotString( slot, "Map", buffer, sizeof( buffer ) );
	if ( !buffer[0] ) {
		return;
	}
	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawVoteCount

Paints the running vote count for the requested slot.
=============
*/
static void CG_DrawVoteCount(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle, int slot) {
	char	buffer[MAX_CVAR_VALUE_STRING];
	float	x;
	float	y;

	CG_GetVoteSlotString( slot, "Count", buffer, sizeof( buffer ) );
	if ( !buffer[0] ) {
		return;
	}
	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawVoteTimer

Displays the time remaining until the current vote closes.
=============
*/
static void CG_DrawVoteTimer(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle) {
	int		remaining;
	char	buffer[32];
	float	x;
	float	y;

	if ( !cgs.voteTime ) {
		return;
	}
	remaining = ( VOTE_TIME - ( cg.time - cgs.voteTime ) + 999 ) / 1000;
	if ( remaining < 0 ) {
		remaining = 0;
	}
	Com_sprintf( buffer, sizeof( buffer ), "Vote %is", remaining );
	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawSelectedPlayerTeamColor

Fills the provided rectangle using the selected player's team color.
=============
*/
static void CG_DrawSelectedPlayerTeamColor(rectDef_t *rect) {
	clientInfo_t	*ci;
	vec4_t			fill;

	ci = CG_GetSelectedClientInfo();
	if ( !ci ) {
		return;
	}

	switch ( ci->team ) {
	case TEAM_RED:
		Vector4Set( fill, 1.0f, 0.0f, 0.0f, 0.45f );
		break;
	case TEAM_BLUE:
		Vector4Set( fill, 0.2f, 0.35f, 1.0f, 0.45f );
		break;
	default:
		Vector4Set( fill, 1.0f, 1.0f, 1.0f, 0.25f );
		break;
	}

	CG_FillRect(rect->x, rect->y, rect->w, rect->h, fill);
}

/*
=============
CG_DrawSelectedPlayerAccuracy

Displays the accuracy statistic for the selected scoreboard entry.
=============
*/
static void CG_DrawSelectedPlayerAccuracy(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	score_t		*score;
	char		buffer[16];

	score = CG_GetSelectedScore();
	if ( !score ) {
		return;
	}

	Com_sprintf( buffer, sizeof( buffer ), "%i%%", score->accuracy );
	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}

/*
=============
CG_DrawTeamPlayerCount

Renders the player count string for the specified team.
=============
*/
static void CG_DrawTeamPlayerCount(rectDef_t *rect, float scale, vec4_t color, int textStyle, team_t team) {
	char	buffer[64];
	int		count;

	count = CG_CountPlayersForTeam( team );
	Com_sprintf( buffer, sizeof( buffer ), "%s (%i)", CG_GetTeamLabel( team ), count );
	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}

/*
=============
CG_DrawTeamTimeoutCount

Displays the remaining timeout count for the given team if known.
=============
*/
static void CG_DrawTeamTimeoutCount(rectDef_t *rect, float scale, vec4_t color, int textStyle, team_t team) {
	char	buffer[64];
	int		remaining;

	if ( team <= TEAM_FREE || team >= TEAM_NUM_TEAMS ) {
		return;
	}

	remaining = cgs.matchTimeoutRemaining[team];
	Com_sprintf( buffer, sizeof( buffer ), "Timeouts %i", remaining );
	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}

/*
=============
CG_DrawTeamAveragePing

Shows the average ping for the members of the supplied team.
=============
*/
static void CG_DrawTeamAveragePing(rectDef_t *rect, float scale, vec4_t color, int textStyle, team_t team) {
	int		sum;
	int		count;
	int		average;
	int		i;
	char	buffer[48];

	sum = 0;
	count = 0;
	for ( i = 0; i < cg.numScores; i++ ) {
		if ( cg.scores[i].team != team ) {
			continue;
		}
		if ( cg.scores[i].ping < 0 ) {
			continue;
		}
		sum += cg.scores[i].ping;
		count++;
	}

	if ( count <= 0 ) {
		return;
	}

	average = sum / count;
	Com_sprintf( buffer, sizeof( buffer ), "Avg ping %i", average );
	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}

/*
=============
CG_ResolveWeaponName

Translates a weapon index into a localized pickup name.
=============
*/
static const char *CG_ResolveWeaponName( int weapon ) {
	const gitem_t	*item;

	if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return NULL;
	}

	item = BG_FindItemForWeapon( (weapon_t)weapon );
	if ( !item || !item->pickup_name || !item->pickup_name[0] ) {
		return NULL;
	}

	return item->pickup_name;
}

/*
=============
CG_DrawSelectedPlayerBestWeapon

Prints the best known weapon for the highlighted scoreboard entry.
=============
*/
static void CG_DrawSelectedPlayerBestWeapon(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	const clientInfo_t	*ci;
	const centity_t		*cent;
	const char			*weaponName;
	int				clientNum;

	ci = CG_GetSelectedClientInfo();
	if ( !ci ) {
		return;
	}

	clientNum = ci->clientNum;
	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return;
	}

	cent = &cg_entities[clientNum];
	weaponName = CG_ResolveWeaponName( cent->currentState.weapon );
	if ( !weaponName ) {
		weaponName = "Unknown";
	}

	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, weaponName, 0, 0, textStyle);
}

/*
=============
CG_BuildMatchStateLabel

Generates the textual description of the active match phase.
=============
*/
static void CG_BuildMatchStateLabel( char *buffer, size_t bufferSize, qboolean includeDefault ) {
	int		remaining;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( cgs.matchTimeoutActive && cgs.matchTimeoutTeam > TEAM_FREE && cgs.matchTimeoutTeam < TEAM_NUM_TEAMS ) {
		remaining = ( cgs.matchTimeoutExpireTime - cg.time + 999 ) / 1000;
		if ( remaining < 0 ) {
			remaining = 0;
		}
		Com_sprintf( buffer, bufferSize, "Timeout %s (%is)", CG_GetTeamLabel( cgs.matchTimeoutTeam ), remaining );
		return;
	}

	if ( cgs.matchOvertimeActive ) {
		Com_sprintf( buffer, bufferSize, "Overtime %i", cgs.matchOvertimeCount );
		return;
	}

	if ( cg.intermissionStarted ) {
		Q_strncpyz( buffer, "Intermission", bufferSize );
		return;
	}

	if ( cg.warmup ) {
		Q_strncpyz( buffer, "Warmup", bufferSize );
		return;
	}

	if ( includeDefault ) {
		Q_strncpyz( buffer, "Match", bufferSize );
	}
}

/*
=============
CG_DrawMatchState

Outputs a textual summary of timeout or overtime state.
=============
*/
static void CG_DrawMatchState(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	char		buffer[64];

	CG_BuildMatchStateLabel( buffer, sizeof( buffer ), qfalse );
	if ( buffer[0] ) {
		CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
		return;
	}

	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, CG_GetGameStatusText(), 0, 0, textStyle);
}

/*
=============
CG_DrawPregameCoach

Draws the configstring-driven pregame tutorial text when applicable.
=============
*/
static qboolean CG_DrawPregameCoach(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	const char *headline;
	const char *body;
	vec4_t bgColor = { 0.0f, 0.0f, 0.0f, 0.45f };
	vec4_t bodyColor;
	float y;

	if (!cg_drawPregameMessages.integer || !cg.snap) {
		return qfalse;
	}

	if (cg.warmup <= 0 && !cgs.matchTimeoutActive && !(cg.snap->ps.pm_flags & PMF_FOLLOW)) {
		return qfalse;
	}

	headline = CG_ConfigString(CS_TUTORIAL_NAME);
	body = CG_ConfigString(CS_TUTORIAL_TEXT);
	if ((!headline || !headline[0]) && (!body || !body[0])) {
		return qfalse;
	}

	CG_FillRect(rect->x, rect->y, rect->w, rect->h, bgColor);
	Vector4Copy(color, bodyColor);
	bodyColor[3] = color[3] * 0.9f;

	y = rect->y + scale;
	if (headline && headline[0]) {
		CG_Text_Paint(rect->x, y, scale, color, headline, 0, 0, textStyle);
		y += CG_Text_Height(headline, scale, 0) + 2.0f;
	}

	if (body && body[0]) {
		CG_Text_Paint(rect->x, y, scale * 0.8f, bodyColor, body, 0, 0, textStyle);
	}

	return qtrue;
}

/*
=============
CG_DrawSpectatorMessages

Shows spectator follow hints or pregame coach text inside the owner-draw rect.
=============
*/
static void CG_DrawSpectatorMessages(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	char line1[64];
	char line2[96];
	vec4_t drawColor;
	float y;
	const clientInfo_t *ci;

	if (!cg.snap) {
		return;
	}

	if (cg.snap->ps.persistant[PERS_TEAM] != TEAM_SPECTATOR) {
		if (CG_DrawPregameCoach(rect, scale, color, textStyle)) {
			return;
		}
		if (!cg_drawSpecMessages.integer) {
			return;
		}
	}

	if (!cg_drawSpecMessages.integer || cg.snap->ps.persistant[PERS_TEAM] != TEAM_SPECTATOR) {
		return;
	}

	Vector4Copy(color, drawColor);

	if (cg.snap->ps.pm_flags & PMF_FOLLOW) {
		ci = CG_SpectatorClientInfo(0);
		if (ci) {
			Com_sprintf(line1, sizeof(line1), "FOLLOWING %s", ci->name);
		} else {
			Q_strncpyz(line1, "FOLLOWING", sizeof(line1));
		}
		Q_strncpyz(line2, "Press FIRE to cycle, JUMP for free camera", sizeof(line2));
	} else {
		Q_strncpyz(line1, "FREE SPECTATE", sizeof(line1));
		Q_strncpyz(line2, "Press FIRE to follow a player", sizeof(line2));
	}

	y = rect->y + CG_Text_Height(line1, scale, 0);
	CG_Text_Paint(rect->x, y, scale, drawColor, line1, 0, 0, textStyle);
	y += CG_Text_Height(line2, scale * 0.8f, 0) + 2.0f;
	CG_Text_Paint(rect->x, y, scale * 0.8f, drawColor, line2, 0, 0, textStyle);
}

/*
=============
CG_DrawNewChatArea

Displays the timed chat stack that the Quake Live menus reference.
=============
*/
static void CG_DrawNewChatArea(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	int chatHeight;
	int maxLines;
	float lineHeight;
	float y;
	int i;

	if (cg_teamChatTime.integer <= 0) {
		return;
	}

	chatHeight = CG_GetChatHistoryLength();

	maxLines = chatHeight;
	lineHeight = CG_Text_Height("A", scale, 0);
	y = rect->y + rect->h - lineHeight;

	for (i = 0; i < maxLines; i++) {
		int pos = cgs.teamChatPos - 1 - i;
		int index;
		int elapsed;
		vec4_t lineColor;

		if (pos < 0 || pos < cgs.teamChatPos - maxLines) {
			break;
		}

		index = pos % chatHeight;
		if (index < 0) {
			index += chatHeight;
		}

		elapsed = cg.time - cgs.teamChatMsgTimes[index];
		if (elapsed >= cg_teamChatTime.integer || !cgs.teamChatMsgs[index][0]) {
			continue;
		}

		Vector4Copy(color, lineColor);
		lineColor[3] *= 1.0f - (float)elapsed / (float)cg_teamChatTime.integer;
		CG_Text_Paint(rect->x, y, scale, lineColor, cgs.teamChatMsgs[index], 0, 0, textStyle);

		y -= lineHeight;
		if (y < rect->y) {
			break;
		}
	}
}

/*
=============
CG_DrawHealthColorized

Fills the supplied rectangle using the player's health color, optionally tinting a shader.
=============
*/
static void CG_DrawHealthColorized(rectDef_t *rect, qhandle_t shader) {
const clientInfo_t *ci;
vec4_t color;
vec4_t modulate;
float x;
float y;
float w;
float h;
int slot;
int health;
int armor;

if (cg.snap && (cg.snap->ps.pm_flags & PMF_FOLLOW)) {
slot = (rect->x + rect->w * 0.5f < 320.0f) ? 0 : 1;
ci = CG_SpectatorClientInfo(slot);
} else {
slot = -1;
ci = NULL;
}

if (!ci) {
health = cg.snap->ps.stats[STAT_HEALTH];
armor = cg.snap->ps.stats[STAT_ARMOR];
} else {
health = ci->health;
armor = ci->armor;
}

CG_GetColorForHealth(health, armor, color);
color[3] = 0.5f;

if (shader) {
Vector4Copy(color, modulate);
x = rect->x;
y = rect->y;
w = rect->w;
h = rect->h;
CG_AdjustFrom640(&x, &y, &w, &h);
trap_R_SetColor(modulate);
trap_R_DrawStretchPic(x, y, w, h, 0.0f, 0.0f, 1.0f, 1.0f, shader);
trap_R_SetColor(NULL);
return;
}

CG_FillRect(rect->x, rect->y, rect->w, rect->h, color);
}

static void CG_DrawArmorTieredColorized(rectDef_t *rect) {
vec4_t color;
CG_GetArmorTierColor(cg.snap->ps.stats[STAT_ARMOR], color);
color[3] = 0.5f;
CG_FillRect(rect->x, rect->y, rect->w, rect->h, color);
}

static void CG_DrawFollowPlayerNameEx(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
const clientInfo_t *ci = CG_SpectatorClientInfo(0);
char buffer[64];

if (!ci) {
return;
}

Com_sprintf(buffer, sizeof(buffer), "Following %s", ci->name);
CG_Text_Paint(rect->x, rect->y, scale, color, buffer, 0, 0, textStyle);
}

/*
=============
CG_DrawTeamColorized

Fills the supplied rect with the team color, tinting the provided shader if available.
=============
*/
static void CG_DrawTeamColorized(rectDef_t *rect, qhandle_t shader) {
vec4_t color;
float x;
float y;
float w;
float h;

CG_GetTeamColor(&color);
if (shader) {
x = rect->x;
y = rect->y;
w = rect->w;
h = rect->h;
CG_AdjustFrom640(&x, &y, &w, &h);
trap_R_SetColor(color);
trap_R_DrawStretchPic(x, y, w, h, 0.0f, 0.0f, 1.0f, 1.0f, shader);
trap_R_SetColor(NULL);
return;
}

CG_FillRect(rect->x, rect->y, rect->w, rect->h, color);
}

static void CG_DrawLevelTimer(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
int msec;
int seconds;
char buffer[32];

msec = cg.time - cgs.levelStartTime;
if (msec < 0) {
msec = 0;
}

seconds = msec / 1000;
Com_sprintf(buffer, sizeof(buffer), "%02i:%02i", seconds / 60, seconds % 60);
CG_Text_Paint(rect->x, rect->y, scale, color, buffer, 0, 0, textStyle);
}

static void CG_DrawRoundTimer(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
CG_DrawLevelTimer(rect, scale, color, textStyle);
}

static void CG_DrawOvertime(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
if (cg.timelimitWarnings & 4) {
CG_Text_Paint(rect->x, rect->y, scale, color, "OVERTIME", 0, 0, textStyle);
}
}

static void CG_DrawPlayerObituary(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
const char *text = CG_GetKillerText();
if (!text || !*text) {
return;
}
CG_Text_Paint(rect->x, rect->y, scale, color, text, 0, 0, textStyle);
}

void CG_InitTeamChat() {
  memset(teamChat1, 0, sizeof(teamChat1));
  memset(teamChat2, 0, sizeof(teamChat2));
  memset(systemChat, 0, sizeof(systemChat));
}

void CG_SetPrintString(int type, const char *p) {
  if (type == SYSTEM_PRINT) {
    strcpy(systemChat, p);
  } else {
    strcpy(teamChat2, teamChat1);
    strcpy(teamChat1, p);
  }
}

void CG_CheckOrderPending() {
	if (cgs.gametype < GT_CTF) {
		return;
	}
	if (cgs.orderPending) {
		//clientInfo_t *ci = cgs.clientinfo + sortedTeamPlayers[cg_currentSelectedPlayer.integer];
		const char *p1, *p2, *b;
		p1 = p2 = b = NULL;
		switch (cgs.currentOrder) {
			case TEAMTASK_OFFENSE:
				p1 = VOICECHAT_ONOFFENSE;
				p2 = VOICECHAT_OFFENSE;
				b = "+button7; wait; -button7";
			break;
			case TEAMTASK_DEFENSE:
				p1 = VOICECHAT_ONDEFENSE;
				p2 = VOICECHAT_DEFEND;
				b = "+button8; wait; -button8";
			break;					
			case TEAMTASK_PATROL:
				p1 = VOICECHAT_ONPATROL;
				p2 = VOICECHAT_PATROL;
				b = "+button9; wait; -button9";
			break;
			case TEAMTASK_FOLLOW: 
				p1 = VOICECHAT_ONFOLLOW;
				p2 = VOICECHAT_FOLLOWME;
				b = "+button10; wait; -button10";
			break;
			case TEAMTASK_CAMP:
				p1 = VOICECHAT_ONCAMPING;
				p2 = VOICECHAT_CAMP;
			break;
			case TEAMTASK_RETRIEVE:
				p1 = VOICECHAT_ONGETFLAG;
				p2 = VOICECHAT_RETURNFLAG;
			break;
			case TEAMTASK_ESCORT:
				p1 = VOICECHAT_ONFOLLOWCARRIER;
				p2 = VOICECHAT_FOLLOWFLAGCARRIER;
			break;
		}

		if (cg_currentSelectedPlayer.integer == numSortedTeamPlayers) {
			// to everyone
			trap_SendConsoleCommand(va("cmd vsay_team %s\n", p2));
		} else {
			// for the player self
			if (sortedTeamPlayers[cg_currentSelectedPlayer.integer] == cg.snap->ps.clientNum && p1) {
				trap_SendConsoleCommand(va("teamtask %i\n", cgs.currentOrder));
				//trap_SendConsoleCommand(va("cmd say_team %s\n", p2));
				trap_SendConsoleCommand(va("cmd vsay_team %s\n", p1));
			} else if (p2) {
				//trap_SendConsoleCommand(va("cmd say_team %s, %s\n", ci->name,p));
				trap_SendConsoleCommand(va("cmd vtell %d %s\n", sortedTeamPlayers[cg_currentSelectedPlayer.integer], p2));
			}
		}
		if (b) {
			trap_SendConsoleCommand(b);
		}
		cgs.orderPending = qfalse;
	}
}

static void CG_SetSelectedPlayerName() {
  if (cg_currentSelectedPlayer.integer >= 0 && cg_currentSelectedPlayer.integer < numSortedTeamPlayers) {
		clientInfo_t *ci = cgs.clientinfo + sortedTeamPlayers[cg_currentSelectedPlayer.integer];
	  if (ci) {
			trap_Cvar_Set("cg_selectedPlayerName", ci->name);
			trap_Cvar_Set("cg_selectedPlayer", va("%d", sortedTeamPlayers[cg_currentSelectedPlayer.integer]));
			cgs.currentOrder = ci->teamTask;
	  }
	} else {
		trap_Cvar_Set("cg_selectedPlayerName", "Everyone");
	}
}
int CG_GetSelectedPlayer() {
	if (cg_currentSelectedPlayer.integer < 0 || cg_currentSelectedPlayer.integer >= numSortedTeamPlayers) {
		cg_currentSelectedPlayer.integer = 0;
	}
	return cg_currentSelectedPlayer.integer;
}

void CG_SelectNextPlayer() {
	CG_CheckOrderPending();
	if (cg_currentSelectedPlayer.integer >= 0 && cg_currentSelectedPlayer.integer < numSortedTeamPlayers) {
		cg_currentSelectedPlayer.integer++;
	} else {
		cg_currentSelectedPlayer.integer = 0;
	}
	CG_SetSelectedPlayerName();
}

void CG_SelectPrevPlayer() {
	CG_CheckOrderPending();
	if (cg_currentSelectedPlayer.integer > 0 && cg_currentSelectedPlayer.integer < numSortedTeamPlayers) {
		cg_currentSelectedPlayer.integer--;
	} else {
		cg_currentSelectedPlayer.integer = numSortedTeamPlayers;
	}
	CG_SetSelectedPlayerName();
}


static void CG_DrawPlayerArmorIcon( rectDef_t *rect, qboolean draw2D ) {
	centity_t	*cent;
	playerState_t	*ps;
	vec3_t		angles;
	vec3_t		origin;

  if ( cg_drawStatus.integer == 0 ) {
		return;
	}

	cent = &cg_entities[cg.snap->ps.clientNum];
	ps = &cg.snap->ps;

	if ( draw2D || ( !cg_draw3dIcons.integer && cg_drawIcons.integer) ) { // bk001206 - parentheses
		CG_DrawPic( rect->x, rect->y + rect->h/2 + 1, rect->w, rect->h, cgs.media.armorIcon );
  } else if (cg_draw3dIcons.integer) {
	  VectorClear( angles );
    origin[0] = 90;
  	origin[1] = 0;
  	origin[2] = -10;
  	angles[YAW] = ( cg.time & 2047 ) * 360 / 2048.0;
  
    CG_Draw3DModel( rect->x, rect->y, rect->w, rect->h, cgs.media.armorModel, 0, origin, angles );
  }

}

static void CG_DrawPlayerArmorValue(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle) {
	char	num[16];
  int value;
	centity_t	*cent;
	playerState_t	*ps;

  cent = &cg_entities[cg.snap->ps.clientNum];
	ps = &cg.snap->ps;

	value = ps->stats[STAT_ARMOR];
  

	if (shader) {
    trap_R_SetColor( color );
		CG_DrawPic(rect->x, rect->y, rect->w, rect->h, shader);
	  trap_R_SetColor( NULL );
	} else {
		Com_sprintf (num, sizeof(num), "%i", value);
		value = CG_Text_Width(num, scale, 0);
	  CG_Text_Paint(rect->x + (rect->w - value) / 2, rect->y + rect->h, scale, color, num, 0, 0, textStyle);
	}
}


static void CG_DrawPlayerAmmoIcon( rectDef_t *rect, qboolean draw2D ) {
	centity_t	*cent;
	playerState_t	*ps;
	vec3_t		angles;
	vec3_t		origin;

	cent = &cg_entities[cg.snap->ps.clientNum];
	ps = &cg.snap->ps;

	if ( draw2D || (!cg_draw3dIcons.integer && cg_drawIcons.integer) ) { // bk001206 - parentheses
	  qhandle_t	icon;
    icon = cg_weapons[ cg.predictedPlayerState.weapon ].ammoIcon;
		if ( icon ) {
		  CG_DrawPic( rect->x, rect->y, rect->w, rect->h, icon );
		}
  } else if (cg_draw3dIcons.integer) {
  	if ( cent->currentState.weapon && cg_weapons[ cent->currentState.weapon ].ammoModel ) {
	    VectorClear( angles );
	  	origin[0] = 70;
  		origin[1] = 0;
  		origin[2] = 0;
  		angles[YAW] = 90 + 20 * sin( cg.time / 1000.0 );
  		CG_Draw3DModel( rect->x, rect->y, rect->w, rect->h, cg_weapons[ cent->currentState.weapon ].ammoModel, 0, origin, angles );
  	}
  }
}

static void CG_DrawPlayerAmmoValue(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle) {
	char	num[16];
	int value;
	centity_t	*cent;
	playerState_t	*ps;

	cent = &cg_entities[cg.snap->ps.clientNum];
	ps = &cg.snap->ps;

	if ( cent->currentState.weapon ) {
		value = ps->ammo[cent->currentState.weapon];
		if ( value > -1 ) {
			if (shader) {
		    trap_R_SetColor( color );
				CG_DrawPic(rect->x, rect->y, rect->w, rect->h, shader);
			  trap_R_SetColor( NULL );
			} else {
				Com_sprintf (num, sizeof(num), "%i", value);
				value = CG_Text_Width(num, scale, 0);
				CG_Text_Paint(rect->x + (rect->w - value) / 2, rect->y + rect->h, scale, color, num, 0, 0, textStyle);
			}
		}
	}

}



static void CG_DrawPlayerHead(rectDef_t *rect, qboolean draw2D) {
	vec3_t		angles;
	float		size, stretch;
	float		frac;
	float		x = rect->x;

	VectorClear( angles );

	if ( cg.damageTime && cg.time - cg.damageTime < DAMAGE_TIME ) {
		frac = (float)(cg.time - cg.damageTime ) / DAMAGE_TIME;
		size = rect->w * 1.25 * ( 1.5 - frac * 0.5 );

		stretch = size - rect->w * 1.25;
		// kick in the direction of damage
		x -= stretch * 0.5 + cg.damageX * stretch * 0.5;

		cg.headStartYaw = 180 + cg.damageX * 45;

		cg.headEndYaw = 180 + 20 * cos( crandom()*M_PI );
		cg.headEndPitch = 5 * cos( crandom()*M_PI );

		cg.headStartTime = cg.time;
		cg.headEndTime = cg.time + 100 + random() * 2000;
	} else {
		if ( cg.time >= cg.headEndTime ) {
			// select a new head angle
			cg.headStartYaw = cg.headEndYaw;
			cg.headStartPitch = cg.headEndPitch;
			cg.headStartTime = cg.headEndTime;
			cg.headEndTime = cg.time + 100 + random() * 2000;

			cg.headEndYaw = 180 + 20 * cos( crandom()*M_PI );
			cg.headEndPitch = 5 * cos( crandom()*M_PI );
		}

		size = rect->w * 1.25;
	}

	// if the server was frozen for a while we may have a bad head start time
	if ( cg.headStartTime > cg.time ) {
		cg.headStartTime = cg.time;
	}

	frac = ( cg.time - cg.headStartTime ) / (float)( cg.headEndTime - cg.headStartTime );
	frac = frac * frac * ( 3 - 2 * frac );
	angles[YAW] = cg.headStartYaw + ( cg.headEndYaw - cg.headStartYaw ) * frac;
	angles[PITCH] = cg.headStartPitch + ( cg.headEndPitch - cg.headStartPitch ) * frac;

	CG_DrawHead( x, rect->y, rect->w, rect->h, cg.snap->ps.clientNum, angles );
}

static void CG_DrawSelectedPlayerHealth( rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle ) {
	clientInfo_t *ci;
	int value;
	char num[16];

  ci = cgs.clientinfo + sortedTeamPlayers[CG_GetSelectedPlayer()];
  if (ci) {
		if (shader) {
			trap_R_SetColor( color );
			CG_DrawPic(rect->x, rect->y, rect->w, rect->h, shader);
			trap_R_SetColor( NULL );
		} else {
			Com_sprintf (num, sizeof(num), "%i", ci->health);
		  value = CG_Text_Width(num, scale, 0);
		  CG_Text_Paint(rect->x + (rect->w - value) / 2, rect->y + rect->h, scale, color, num, 0, 0, textStyle);
		}
	}
}

static void CG_DrawSelectedPlayerArmor( rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle ) {
	clientInfo_t *ci;
	int value;
	char num[16];
  ci = cgs.clientinfo + sortedTeamPlayers[CG_GetSelectedPlayer()];
  if (ci) {
    if (ci->armor > 0) {
			if (shader) {
				trap_R_SetColor( color );
				CG_DrawPic(rect->x, rect->y, rect->w, rect->h, shader);
				trap_R_SetColor( NULL );
			} else {
				Com_sprintf (num, sizeof(num), "%i", ci->armor);
				value = CG_Text_Width(num, scale, 0);
				CG_Text_Paint(rect->x + (rect->w - value) / 2, rect->y + rect->h, scale, color, num, 0, 0, textStyle);
			}
		}
 	}
}

qhandle_t CG_StatusHandle(int task) {
	qhandle_t h = cgs.media.assaultShader;
	switch (task) {
		case TEAMTASK_OFFENSE :
			h = cgs.media.assaultShader;
			break;
		case TEAMTASK_DEFENSE :
			h = cgs.media.defendShader;
			break;
		case TEAMTASK_PATROL :
			h = cgs.media.patrolShader;
			break;
		case TEAMTASK_FOLLOW :
			h = cgs.media.followShader;
			break;
		case TEAMTASK_CAMP :
			h = cgs.media.campShader;
			break;
		case TEAMTASK_RETRIEVE :
			h = cgs.media.retrieveShader; 
			break;
		case TEAMTASK_ESCORT :
			h = cgs.media.escortShader; 
			break;
		default : 
			h = cgs.media.assaultShader;
			break;
	}
	return h;
}

static void CG_DrawSelectedPlayerStatus( rectDef_t *rect ) {
	clientInfo_t *ci = cgs.clientinfo + sortedTeamPlayers[CG_GetSelectedPlayer()];
	if (ci) {
		qhandle_t h;
		if (cgs.orderPending) {
			// blink the icon
			if ( cg.time > cgs.orderTime - 2500 && (cg.time >> 9 ) & 1 ) {
				return;
			}
			h = CG_StatusHandle(cgs.currentOrder);
		}	else {
			h = CG_StatusHandle(ci->teamTask);
		}
		CG_DrawPic( rect->x, rect->y, rect->w, rect->h, h );
	}
}


static void CG_DrawPlayerStatus( rectDef_t *rect ) {
	clientInfo_t *ci = &cgs.clientinfo[cg.snap->ps.clientNum];
	if (ci) {
		qhandle_t h = CG_StatusHandle(ci->teamTask);
		CG_DrawPic( rect->x, rect->y, rect->w, rect->h, h);
	}
}


/*
=============
CG_DrawSelectedPlayerName

Draws the selected player's name or the active voice client's name.
=============
*/
static void CG_DrawSelectedPlayerName( rectDef_t *rect, float scale, vec4_t color, qboolean voice, int textStyle) {
	clientInfo_t *ci;

	if ( voice && !CG_ShouldDisplayVoiceIndicator() ) {
		return;
	}

	ci = cgs.clientinfo + ( ( voice ) ? cgs.currentVoiceClient : sortedTeamPlayers[CG_GetSelectedPlayer()] );
	if ( ci ) {
		CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, ci->name, 0, 0, textStyle);
	}
}

static void CG_DrawSelectedPlayerLocation( rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
	clientInfo_t *ci;
  ci = cgs.clientinfo + sortedTeamPlayers[CG_GetSelectedPlayer()];
  if (ci) {
		const char *p = CG_ConfigString(CS_LOCATIONS + ci->location);
		if (!p || !*p) {
			p = "unknown";
		}
    CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, p, 0, 0, textStyle);
  }
}

static void CG_DrawPlayerLocation( rectDef_t *rect, float scale, vec4_t color, int textStyle  ) {
	clientInfo_t *ci = &cgs.clientinfo[cg.snap->ps.clientNum];
  if (ci) {
		const char *p = CG_ConfigString(CS_LOCATIONS + ci->location);
		if (!p || !*p) {
			p = "unknown";
		}
    CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, p, 0, 0, textStyle);
  }
}



static void CG_DrawSelectedPlayerWeapon( rectDef_t *rect ) {
	clientInfo_t *ci;

  ci = cgs.clientinfo + sortedTeamPlayers[CG_GetSelectedPlayer()];
  if (ci) {
	  if ( cg_weapons[ci->curWeapon].weaponIcon ) {
	    CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cg_weapons[ci->curWeapon].weaponIcon );
		} else {
  	  CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cgs.media.deferShader);
    }
  }
}

static void CG_DrawPlayerScore( rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle ) {
  char num[16];
  int value = cg.snap->ps.persistant[PERS_SCORE];

	if (shader) {
		trap_R_SetColor( color );
		CG_DrawPic(rect->x, rect->y, rect->w, rect->h, shader);
		trap_R_SetColor( NULL );
	} else {
		Com_sprintf (num, sizeof(num), "%i", value);
		value = CG_Text_Width(num, scale, 0);
	  CG_Text_Paint(rect->x + (rect->w - value) / 2, rect->y + rect->h, scale, color, num, 0, 0, textStyle);
	}
}

static void CG_DrawPlayerItem( rectDef_t *rect, float scale, qboolean draw2D) {
	int		value;
  vec3_t origin, angles;

	value = cg.snap->ps.stats[STAT_HOLDABLE_ITEM];
	if ( value ) {
		CG_RegisterItemVisuals( value );

		if (qtrue) {
		  CG_RegisterItemVisuals( value );
		  CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cg_items[ value ].icon );
		} else {
 			VectorClear( angles );
			origin[0] = 90;
  		origin[1] = 0;
   		origin[2] = -10;
  		angles[YAW] = ( cg.time & 2047 ) * 360 / 2048.0;
			CG_Draw3DModel(rect->x, rect->y, rect->w, rect->h, cg_items[ value ].models[0], 0, origin, angles );
		}
	}

}


static void CG_DrawSelectedPlayerPowerup( rectDef_t *rect, qboolean draw2D ) {
	clientInfo_t *ci;
  int j;
  float x, y;

  ci = cgs.clientinfo + sortedTeamPlayers[CG_GetSelectedPlayer()];
  if (ci) {
    x = rect->x;
    y = rect->y;

		for (j = 0; j < PW_NUM_POWERUPS; j++) {
			if (ci->powerups & (1 << j)) {
				gitem_t	*item;
				item = BG_FindItemForPowerup( j );
				if (item) {
				  CG_DrawPic( x, y, rect->w, rect->h, trap_R_RegisterShader( item->icon ) );
					x += 3;
					y += 3;
          return;
				}
			}
		}

  }
}


/*
=============
CG_DrawSelectedPlayerHead

Draws the head model for the selected player or active voice client.
=============
*/
static void CG_DrawSelectedPlayerHead( rectDef_t *rect, qboolean draw2D, qboolean voice ) {
	clipHandle_t	cm;
	clientInfo_t	*ci;
	float			len;
	vec3_t			origin;
	vec3_t			mins, maxs, angles;

	if ( voice && !CG_ShouldDisplayVoiceIndicator() ) {
		return;
	}

	ci = cgs.clientinfo + ( ( voice ) ? cgs.currentVoiceClient : sortedTeamPlayers[CG_GetSelectedPlayer()] );

	if (ci) {
		if ( cg_draw3dIcons.integer ) {
			cm = ci->headModel;
			if ( !cm ) {
				return;
			}

			// offset the origin y and z to center the head
			trap_R_ModelBounds( cm, mins, maxs );

			origin[2] = -0.5 * ( mins[2] + maxs[2] );
			origin[1] = 0.5 * ( mins[1] + maxs[1] );

			// calculate distance so the head nearly fills the box
			// assume heads are taller than wide
			len = 0.7 * ( maxs[2] - mins[2] );
			origin[0] = len / 0.268;	// len / tan( fov/2 )

			// allow per-model tweaking
			VectorAdd( origin, ci->headOffset, origin );

			angles[PITCH] = 0;
			angles[YAW] = 180;
			angles[ROLL] = 0;

			CG_Draw3DModel( rect->x, rect->y, rect->w, rect->h, ci->headModel, ci->headSkin, origin, angles );
		} else if ( cg_drawIcons.integer ) {
			CG_DrawPic( rect->x, rect->y, rect->w, rect->h, ci->modelIcon );
		}

		// if they are deferred, draw a cross out
		if ( ci->deferred ) {
			CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cgs.media.deferShader );
		}
	}
}

static void CG_DrawPlayerHealth(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle ) {
	playerState_t	*ps;
  int value;
	char	num[16];

	ps = &cg.snap->ps;

	value = ps->stats[STAT_HEALTH];

	if (shader) {
		trap_R_SetColor( color );
		CG_DrawPic(rect->x, rect->y, rect->w, rect->h, shader);
		trap_R_SetColor( NULL );
	} else {
		Com_sprintf (num, sizeof(num), "%i", value);
	  value = CG_Text_Width(num, scale, 0);
	  CG_Text_Paint(rect->x + (rect->w - value) / 2, rect->y + rect->h, scale, color, num, 0, 0, textStyle);
	}
}


static void CG_DrawRedScore(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle ) {
	int value;
	char num[16];
	if ( cgs.scores1 == SCORE_NOT_PRESENT ) {
		Com_sprintf (num, sizeof(num), "-");
	}
	else {
		Com_sprintf (num, sizeof(num), "%i", cgs.scores1);
	}
	value = CG_Text_Width(num, scale, 0);
	CG_Text_Paint(rect->x + rect->w - value, rect->y + rect->h, scale, color, num, 0, 0, textStyle);
}

static void CG_DrawBlueScore(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle ) {
	int value;
	char num[16];

	if ( cgs.scores2 == SCORE_NOT_PRESENT ) {
		Com_sprintf (num, sizeof(num), "-");
	}
	else {
		Com_sprintf (num, sizeof(num), "%i", cgs.scores2);
	}
	value = CG_Text_Width(num, scale, 0);
	CG_Text_Paint(rect->x + rect->w - value, rect->y + rect->h, scale, color, num, 0, 0, textStyle);
}

// FIXME: team name support
static void CG_DrawRedName(rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
  CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, cg_redTeamName.string , 0, 0, textStyle);
}

static void CG_DrawBlueName(rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
  CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, cg_blueTeamName.string, 0, 0, textStyle);
}

static void CG_DrawBlueFlagName(rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
  int i;
  for ( i = 0 ; i < cgs.maxclients ; i++ ) {
	  if ( cgs.clientinfo[i].infoValid && cgs.clientinfo[i].team == TEAM_RED  && cgs.clientinfo[i].powerups & ( 1<< PW_BLUEFLAG )) {
      CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, cgs.clientinfo[i].name, 0, 0, textStyle);
      return;
    }
  }
}

static void CG_DrawBlueFlagStatus(rectDef_t *rect, qhandle_t shader) {
	if (cgs.gametype != GT_CTF && cgs.gametype != GT_1FCTF) {
		if (cgs.gametype == GT_HARVESTER) {
		  vec4_t color = {0, 0, 1, 1};
		  trap_R_SetColor(color);
	    CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cgs.media.blueCubeIcon );
		  trap_R_SetColor(NULL);
		}
		return;
	}
  if (shader) {
		CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );
  } else {
	  gitem_t *item = BG_FindItemForPowerup( PW_BLUEFLAG );
    if (item) {
		  vec4_t color = {0, 0, 1, 1};
		  trap_R_SetColor(color);
	    if( cgs.blueflag >= 0 && cgs.blueflag <= 2 ) {
		    CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cgs.media.flagShaders[cgs.blueflag] );
			} else {
		    CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cgs.media.flagShaders[0] );
			}
		  trap_R_SetColor(NULL);
	  }
  }
}

static void CG_DrawBlueFlagHead(rectDef_t *rect) {
  int i;
  for ( i = 0 ; i < cgs.maxclients ; i++ ) {
	  if ( cgs.clientinfo[i].infoValid && cgs.clientinfo[i].team == TEAM_RED  && cgs.clientinfo[i].powerups & ( 1<< PW_BLUEFLAG )) {
      vec3_t angles;
      VectorClear( angles );
 		  angles[YAW] = 180 + 20 * sin( cg.time / 650.0 );;
      CG_DrawHead( rect->x, rect->y, rect->w, rect->h, 0,angles );
      return;
    }
  }
}

static void CG_DrawRedFlagName(rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
  int i;
  for ( i = 0 ; i < cgs.maxclients ; i++ ) {
	  if ( cgs.clientinfo[i].infoValid && cgs.clientinfo[i].team == TEAM_BLUE  && cgs.clientinfo[i].powerups & ( 1<< PW_REDFLAG )) {
      CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, cgs.clientinfo[i].name, 0, 0, textStyle);
      return;
    }
  }
}

static void CG_DrawRedFlagStatus(rectDef_t *rect, qhandle_t shader) {
	if (cgs.gametype != GT_CTF && cgs.gametype != GT_1FCTF) {
		if (cgs.gametype == GT_HARVESTER) {
		  vec4_t color = {1, 0, 0, 1};
		  trap_R_SetColor(color);
	    CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cgs.media.redCubeIcon );
		  trap_R_SetColor(NULL);
		}
		return;
	}
  if (shader) {
		CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );
  } else {
	  gitem_t *item = BG_FindItemForPowerup( PW_REDFLAG );
    if (item) {
		  vec4_t color = {1, 0, 0, 1};
		  trap_R_SetColor(color);
	    if( cgs.redflag >= 0 && cgs.redflag <= 2) {
		    CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cgs.media.flagShaders[cgs.redflag] );
			} else {
		    CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cgs.media.flagShaders[0] );
			}
		  trap_R_SetColor(NULL);
	  }
  }
}

static void CG_DrawRedFlagHead(rectDef_t *rect) {
  int i;
  for ( i = 0 ; i < cgs.maxclients ; i++ ) {
	  if ( cgs.clientinfo[i].infoValid && cgs.clientinfo[i].team == TEAM_BLUE  && cgs.clientinfo[i].powerups & ( 1<< PW_REDFLAG )) {
      vec3_t angles;
      VectorClear( angles );
 		  angles[YAW] = 180 + 20 * sin( cg.time / 650.0 );;
      CG_DrawHead( rect->x, rect->y, rect->w, rect->h, 0,angles );
      return;
    }
  }
}

static void CG_HarvesterSkulls(rectDef_t *rect, float scale, vec4_t color, qboolean force2D, int textStyle ) {
	char num[16];
	vec3_t origin, angles;
	qhandle_t handle;
	int value = cg.snap->ps.generic1;

	if (cgs.gametype != GT_HARVESTER) {
		return;
	}

	if( value > 99 ) {
		value = 99;
	}

	Com_sprintf (num, sizeof(num), "%i", value);
	value = CG_Text_Width(num, scale, 0);
	CG_Text_Paint(rect->x + (rect->w - value), rect->y + rect->h, scale, color, num, 0, 0, textStyle);

	if (cg_drawIcons.integer) {
		if (!force2D && cg_draw3dIcons.integer) {
			VectorClear(angles);
			origin[0] = 90;
			origin[1] = 0;
			origin[2] = -10;
			angles[YAW] = ( cg.time & 2047 ) * 360 / 2048.0;
			if( cg.snap->ps.persistant[PERS_TEAM] == TEAM_BLUE ) {
				handle = cgs.media.redCubeModel;
			} else {
				handle = cgs.media.blueCubeModel;
			}
			CG_Draw3DModel( rect->x, rect->y, 35, 35, handle, 0, origin, angles );
		} else {
			if( cg.snap->ps.persistant[PERS_TEAM] == TEAM_BLUE ) {
				handle = cgs.media.redCubeIcon;
			} else {
				handle = cgs.media.blueCubeIcon;
			}
			CG_DrawPic( rect->x + 3, rect->y + 16, 20, 20, handle );
		}
	}
}

static void CG_OneFlagStatus(rectDef_t *rect) {
	if (cgs.gametype != GT_1FCTF) {
		return;
	} else {
		gitem_t *item = BG_FindItemForPowerup( PW_NEUTRALFLAG );
		if (item) {
			if( cgs.flagStatus >= 0 && cgs.flagStatus <= 4 ) {
				vec4_t color = {1, 1, 1, 1};
				int index = 0;
				if (cgs.flagStatus == FLAG_TAKEN_RED) {
					color[1] = color[2] = 0;
					index = 1;
				} else if (cgs.flagStatus == FLAG_TAKEN_BLUE) {
					color[0] = color[1] = 0;
					index = 1;
				} else if (cgs.flagStatus == FLAG_DROPPED) {
					index = 2;
				}
			  trap_R_SetColor(color);
				CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cgs.media.flagShaders[index] );
			}
		}
	}
}


static void CG_DrawCTFPowerUp(rectDef_t *rect) {
	int		value;

	if (cgs.gametype < GT_CTF) {
		return;
	}
	value = cg.snap->ps.stats[STAT_PERSISTANT_POWERUP];
	if ( value ) {
		CG_RegisterItemVisuals( value );
		CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cg_items[ value ].icon );
	}
}



static void CG_DrawTeamColor(rectDef_t *rect, vec4_t color) {
	CG_DrawTeamBackground(rect->x, rect->y, rect->w, rect->h, color[3], cg.snap->ps.persistant[PERS_TEAM]);
}

/*
=============
CG_DrawPowerupSpriteStack

Renders a stacked list of active powerups, mirroring the retail sprite stack.
=============
*/
static void CG_DrawPowerupSpriteStack(rectDef_t *rect, int align, float special, float scale, vec4_t color, const playerState_t *ps) {
	char num[16];
	int			sorted[MAX_POWERUPS];
	int			sortedTime[MAX_POWERUPS];
	int			i, j, k;
	int			active;
	int			t;
	gitem_t	*item;
	float		f;
	rectDef_t r2;
	float *inc;

	if (!ps || ps->stats[STAT_HEALTH] <= 0) {
		return;
	}

	r2.x = rect->x;
	r2.y = rect->y;
	r2.w = rect->w;
	r2.h = rect->h;
	inc = (align == HUD_VERTICAL) ? &r2.y : &r2.x;

	active = 0;
	for (i = 0; i < MAX_POWERUPS; i++) {
		if (!ps->powerups[i]) {
			continue;
		}

		t = ps->powerups[i] - cg.time;
		if (t <= 0 || t >= 999000) {
			continue;
		}

		for (j = 0; j < active; j++) {
			if (sortedTime[j] >= t) {
				for (k = active - 1; k >= j; k--) {
					sorted[k + 1] = sorted[k];
					sortedTime[k + 1] = sortedTime[k];
				}
				break;
			}
		}

		sorted[j] = i;
		sortedTime[j] = t;
		active++;
	}

	for (i = 0; i < active; i++) {
		item = BG_FindItemForPowerup(sorted[i]);
		if (!item) {
			continue;
		}

		t = ps->powerups[sorted[i]];
		if (t - cg.time >= POWERUP_BLINKS * POWERUP_BLINK_TIME) {
			trap_R_SetColor(NULL);
		} else {
			vec4_t modulate;

			f = (float)(t - cg.time) / POWERUP_BLINK_TIME;
			f -= (int)f;
			modulate[0] = modulate[1] = modulate[2] = modulate[3] = f;
			trap_R_SetColor(modulate);
		}

		CG_DrawPic(r2.x, r2.y, r2.w * 0.75f, r2.h, trap_R_RegisterShader(item->icon));
		Com_sprintf(num, sizeof(num), "%i", sortedTime[i] / 1000);
		CG_Text_Paint(r2.x + (r2.w * 0.75f) + 3, r2.y + r2.h, scale, color, num, 0, 0, 0);
		*inc += r2.w + special;
	}

	trap_R_SetColor(NULL);
}

static void CG_DrawAreaPowerUp(rectDef_t *rect, int align, float special, float scale, vec4_t color) {
	if (!cg_drawSprites.integer) {
		return;
	}

	if (!CG_ShouldDrawSpriteSelf() && cg.snap && !(cg.snap->ps.pm_flags & PMF_FOLLOW) && cg.snap->ps.clientNum == cg.clientNum) {
		return;
	}

	CG_DrawPowerupSpriteStack(rect, align, special, scale, color, &cg.snap->ps);
}


float CG_GetValue(int ownerDraw) {
	centity_t	*cent;
 	clientInfo_t *ci;
	playerState_t	*ps;

  cent = &cg_entities[cg.snap->ps.clientNum];
	ps = &cg.snap->ps;

  switch (ownerDraw) {
  case CG_SELECTEDPLAYER_ARMOR:
    ci = cgs.clientinfo + sortedTeamPlayers[CG_GetSelectedPlayer()];
    return ci->armor;
    break;
  case CG_SELECTEDPLAYER_HEALTH:
    ci = cgs.clientinfo + sortedTeamPlayers[CG_GetSelectedPlayer()];
    return ci->health;
    break;
  case CG_PLAYER_ARMOR_VALUE:
		return ps->stats[STAT_ARMOR];
    break;
  case CG_PLAYER_AMMO_VALUE:
		if ( cent->currentState.weapon ) {
		  return ps->ammo[cent->currentState.weapon];
		}
    break;
  case CG_PLAYER_SCORE:
	  return cg.snap->ps.persistant[PERS_SCORE];
    break;
  case CG_PLAYER_HEALTH:
		return ps->stats[STAT_HEALTH];
    break;
  case CG_RED_SCORE:
		return cgs.scores1;
    break;
  case CG_BLUE_SCORE:
		return cgs.scores2;
    break;
  default:
    break;
  }
	return -1;
}


/*
=============
CG_SpectatorPlayerSlotActive

Returns qtrue when the requested spectator slot has a valid client.
=============
*/
static qboolean CG_SpectatorPlayerSlotActive( int slot ) {
	return ( CG_SpectatorClientInfo( slot ) != NULL );
}

/*
=============
CG_LocalPlayerHasWeapon

Checks if the predicted player currently owns the supplied weapon.
=============
*/
static qboolean CG_LocalPlayerHasWeapon( weapon_t weapon ) {
	if ( !cg.snap ) {
		return qfalse;
	}

	if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return qfalse;
	}

	return ( ( cg.snap->ps.stats[STAT_WEAPONS] & ( 1 << weapon ) ) != 0 );
}

/*
=============
CG_LoadoutsEnabled

Determines whether the active server advertises g_loadout as enabled.
=============
*/
static qboolean CG_LoadoutsEnabled( void ) {
	const char *info;
	const char *value;

	info = CG_ConfigString( CS_SERVERINFO );
	if ( !info || !*info ) {
		return qfalse;
	}

	value = Info_ValueForKey( info, "g_loadout" );
	if ( !value || !*value ) {
		return qfalse;
	}

	return ( atoi( value ) != 0 );
}

qboolean CG_OtherTeamHasFlag() {
	if (cgs.gametype == GT_CTF || cgs.gametype == GT_1FCTF) {
		int team = cg.snap->ps.persistant[PERS_TEAM];
		if (cgs.gametype == GT_1FCTF) {
			if (team == TEAM_RED && cgs.flagStatus == FLAG_TAKEN_BLUE) {
				return qtrue;
			} else if (team == TEAM_BLUE && cgs.flagStatus == FLAG_TAKEN_RED) {
				return qtrue;
			} else {
				return qfalse;
			}
		} else {
			if (team == TEAM_RED && cgs.redflag == FLAG_TAKEN) {
				return qtrue;
			} else if (team == TEAM_BLUE && cgs.blueflag == FLAG_TAKEN) {
				return qtrue;
			} else {
				return qfalse;
			}
		}
	}
	return qfalse;
}

qboolean CG_YourTeamHasFlag() {
	if (cgs.gametype == GT_CTF || cgs.gametype == GT_1FCTF) {
		int team = cg.snap->ps.persistant[PERS_TEAM];
		if (cgs.gametype == GT_1FCTF) {
			if (team == TEAM_RED && cgs.flagStatus == FLAG_TAKEN_RED) {
				return qtrue;
			} else if (team == TEAM_BLUE && cgs.flagStatus == FLAG_TAKEN_BLUE) {
				return qtrue;
			} else {
				return qfalse;
			}
		} else {
			if (team == TEAM_RED && cgs.blueflag == FLAG_TAKEN) {
				return qtrue;
			} else if (team == TEAM_BLUE && cgs.redflag == FLAG_TAKEN) {
				return qtrue;
			} else {
				return qfalse;
			}
		}
	}
	return qfalse;
}

/*
=============
CG_OwnerDrawVisible

Evaluates the ownerdraw visibility bitmasks for HUD and menu scripts.
=============
*/
qboolean CG_OwnerDrawVisible(int flags) {

	if (flags & CG_SHOW_TEAMINFO) {
		return (cg_currentSelectedPlayer.integer == numSortedTeamPlayers);
	}

	if (flags & CG_SHOW_NOTEAMINFO) {
		return !(cg_currentSelectedPlayer.integer == numSortedTeamPlayers);
	}

	if (flags & CG_SHOW_OTHERTEAMHASFLAG) {
		return CG_OtherTeamHasFlag();
	}

	if (flags & CG_SHOW_YOURTEAMHASENEMYFLAG) {
		return CG_YourTeamHasFlag();
	}

	if (flags & (CG_SHOW_BLUE_TEAM_HAS_REDFLAG | CG_SHOW_RED_TEAM_HAS_BLUEFLAG)) {
		if (flags & CG_SHOW_BLUE_TEAM_HAS_REDFLAG && (cgs.redflag == FLAG_TAKEN || cgs.flagStatus == FLAG_TAKEN_RED)) {
			return qtrue;
		} else if (flags & CG_SHOW_RED_TEAM_HAS_BLUEFLAG && (cgs.blueflag == FLAG_TAKEN || cgs.flagStatus == FLAG_TAKEN_BLUE)) {
			return qtrue;
		}
		return qfalse;
	}

	if (flags & CG_SHOW_ANYTEAMGAME) {
		if( cgs.gametype >= GT_TEAM) {
			return qtrue;
		}
	}

	if (flags & CG_SHOW_ANYNONTEAMGAME) {
		if( cgs.gametype < GT_TEAM) {
			return qtrue;
		}
	}

	if (flags & CG_SHOW_HARVESTER) {
		if( cgs.gametype == GT_HARVESTER ) {
			return qtrue;
    } else {
      return qfalse;
    }
	}

	if (flags & CG_SHOW_ONEFLAG) {
		if( cgs.gametype == GT_1FCTF ) {
			return qtrue;
    } else {
      return qfalse;
    }
	}

	if (flags & CG_SHOW_CTF) {
		if( cgs.gametype == GT_CTF ) {
			return qtrue;
		}
	}

	if (flags & CG_SHOW_OBELISK) {
		if( cgs.gametype == GT_OBELISK ) {
			return qtrue;
    } else {
      return qfalse;
    }
	}

	if (flags & CG_SHOW_HEALTHCRITICAL) {
		if (cg.snap->ps.stats[STAT_HEALTH] < 25) {
			return qtrue;
		}
	}

	if (flags & CG_SHOW_IF_PLAYER_HAS_FLAG) {
		if (cg.snap->ps.powerups[PW_REDFLAG] || cg.snap->ps.powerups[PW_BLUEFLAG] || cg.snap->ps.powerups[PW_NEUTRALFLAG]) {
			return qtrue;
		}
	}

	if (flags & CG_SHOW_IF_PLYR1) {
		return CG_SpectatorPlayerSlotActive( 0 );
	}

	if (flags & CG_SHOW_IF_PLYR2) {
		return CG_SpectatorPlayerSlotActive( 1 );
	}

	if (flags & CG_SHOW_IF_G_FIRED) {
		return CG_LocalPlayerHasWeapon( WP_GAUNTLET );
	}

	if (flags & CG_SHOW_IF_MG_FIRED) {
		return CG_LocalPlayerHasWeapon( WP_MACHINEGUN );
	}

	if (flags & CG_SHOW_IF_SG_FIRED) {
		return CG_LocalPlayerHasWeapon( WP_SHOTGUN );
	}

	if (flags & CG_SHOW_IF_GL_FIRED) {
		return CG_LocalPlayerHasWeapon( WP_GRENADE_LAUNCHER );
	}

	if (flags & CG_SHOW_IF_RL_FIRED) {
		return CG_LocalPlayerHasWeapon( WP_ROCKET_LAUNCHER );
	}

	if (flags & CG_SHOW_IF_LG_FIRED) {
		return CG_LocalPlayerHasWeapon( WP_LIGHTNING );
	}

	if (flags & CG_SHOW_IF_RG_FIRED) {
		return CG_LocalPlayerHasWeapon( WP_RAILGUN );
	}

	if (flags & CG_SHOW_IF_PG_FIRED) {
		return CG_LocalPlayerHasWeapon( WP_PLASMAGUN );
	}

	if (flags & CG_SHOW_IF_BFG_FIRED) {
		return CG_LocalPlayerHasWeapon( WP_BFG );
	}

	if (flags & CG_SHOW_IF_CG_FIRED) {
		return CG_LocalPlayerHasWeapon( WP_CHAINGUN );
	}

	if (flags & CG_SHOW_IF_NG_FIRED) {
		return CG_LocalPlayerHasWeapon( WP_NAILGUN );
	}

	if (flags & CG_SHOW_IF_PL_FIRED) {
		return CG_LocalPlayerHasWeapon( WP_PROX_LAUNCHER );
	}

	if (flags & CG_SHOW_IF_HMG_FIRED) {
		return CG_LocalPlayerHasWeapon( WP_HEAVY_MACHINEGUN );
	}

	if (flags & (CG_SHOW_IF_LOADOUT_ENABLED | CG_SHOW_IF_LOADOUT_DISABLED)) {
		qboolean loadoutsEnabled = CG_LoadoutsEnabled();

		if (flags & CG_SHOW_IF_LOADOUT_ENABLED) {
			return loadoutsEnabled;
		}

		return (loadoutsEnabled == qfalse);
	}

	if (flags & (CG_SHOW_IF_PLYR_IS_ON_RED_OR_SPEC | CG_SHOW_IF_PLYR_IS_ON_BLUE_OR_SPEC |
		CG_SHOW_IF_PLYR_IS_ON_RED_NO_SPEC | CG_SHOW_IF_PLYR_IS_ON_BLUE_NO_SPEC)) {
		team_t playerTeam = TEAM_FREE;
		qboolean spectator = qfalse;

		if (cg.snap) {
			playerTeam = (team_t)cg.snap->ps.persistant[PERS_TEAM];
			spectator = (playerTeam == TEAM_SPECTATOR) || (cg.snap->ps.pm_type == PM_SPECTATOR) ||
				(cg.snap->ps.pm_flags & PMF_FOLLOW);
		}

		if (flags & CG_SHOW_IF_PLYR_IS_ON_RED_OR_SPEC) {
			return (playerTeam == TEAM_RED) || spectator;
		}

		if (flags & CG_SHOW_IF_PLYR_IS_ON_BLUE_OR_SPEC) {
			return (playerTeam == TEAM_BLUE) || spectator;
		}

		if (flags & CG_SHOW_IF_PLYR_IS_ON_RED_NO_SPEC) {
			return (playerTeam == TEAM_RED) && !spectator;
		}

		return (playerTeam == TEAM_BLUE) && !spectator;
	}

	if ( flags & CG_SHOW_IF_1ST_PLYR_FOLLOWED ) {
		return CG_SpectatorSlotFollowed( 0 );
	}

	if ( flags & CG_SHOW_IF_2ND_PLYR_FOLLOWED ) {
		return CG_SpectatorSlotFollowed( 1 );
	}

	if ( flags & CG_SHOW_IF_1ST_PLYR_TRACKED ) {
		return CG_SpectatorSlotTracked( 0 );
	}

	if ( flags & CG_SHOW_IF_2ND_PLYR_TRACKED ) {
		return CG_SpectatorSlotTracked( 1 );
	}
	return qfalse;
}



static void CG_DrawPlayerHasFlag(rectDef_t *rect, qboolean force2D) {
	int adj = (force2D) ? 0 : 2;
	if( cg.predictedPlayerState.powerups[PW_REDFLAG] ) {
  	CG_DrawFlagModel( rect->x + adj, rect->y + adj, rect->w - adj, rect->h - adj, TEAM_RED, force2D);
	} else if( cg.predictedPlayerState.powerups[PW_BLUEFLAG] ) {
  	CG_DrawFlagModel( rect->x + adj, rect->y + adj, rect->w - adj, rect->h - adj, TEAM_BLUE, force2D);
	} else if( cg.predictedPlayerState.powerups[PW_NEUTRALFLAG] ) {
  	CG_DrawFlagModel( rect->x + adj, rect->y + adj, rect->w - adj, rect->h - adj, TEAM_FREE, force2D);
	}
}

static void CG_DrawAreaSystemChat(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader) {
  CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, systemChat, 0, 0, 0);
}

static void CG_DrawAreaTeamChat(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader) {
  CG_Text_Paint(rect->x, rect->y + rect->h, scale, color,teamChat1, 0, 0, 0);
}

static void CG_DrawAreaChat(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader) {
  CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, teamChat2, 0, 0, 0);
}

const char *CG_GetKillerText() {
	const char *s = "";
	if ( cg.killerName[0] ) {
		s = va("Fragged by %s", cg.killerName );
	}
	return s;
}


static void CG_DrawKiller(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle ) {
	// fragged by ... line
	if ( cg.killerName[0] ) {
		int x = rect->x + rect->w / 2;
	  CG_Text_Paint(x - CG_Text_Width(CG_GetKillerText(), scale, 0) / 2, rect->y + rect->h, scale, color, CG_GetKillerText(), 0, 0, textStyle);
	}
	
}


static void CG_DrawCapFragLimit(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle) {
	int limit = (cgs.gametype >= GT_CTF) ? cgs.capturelimit : cgs.fraglimit;
	CG_Text_Paint(rect->x, rect->y, scale, color, va("%2i", limit),0, 0, textStyle); 
}

static void CG_Draw1stPlace(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle) {
	if (cgs.scores1 != SCORE_NOT_PRESENT) {
		CG_Text_Paint(rect->x, rect->y, scale, color, va("%2i", cgs.scores1),0, 0, textStyle); 
	}
}

static void CG_Draw2ndPlace(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle) {
	if (cgs.scores2 != SCORE_NOT_PRESENT) {
		CG_Text_Paint(rect->x, rect->y, scale, color, va("%2i", cgs.scores2),0, 0, textStyle); 
	}
}

const char *CG_GetGameStatusText() {
	const char *s = "";
	if ( cgs.gametype < GT_TEAM) {
		if (cg.snap->ps.persistant[PERS_TEAM] != TEAM_SPECTATOR ) {
			s = va("%s place with %i",CG_PlaceString( cg.snap->ps.persistant[PERS_RANK] + 1 ),cg.snap->ps.persistant[PERS_SCORE] );
		}
	} else {
		if ( cg.teamScores[0] == cg.teamScores[1] ) {
			s = va("Teams are tied at %i", cg.teamScores[0] );
		} else if ( cg.teamScores[0] >= cg.teamScores[1] ) {
			s = va("Red leads Blue, %i to %i", cg.teamScores[0], cg.teamScores[1] );
		} else {
			s = va("Blue leads Red, %i to %i", cg.teamScores[1], cg.teamScores[0] );
		}
	}
	return s;
}
	
static void CG_DrawGameStatus(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle ) {
	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, CG_GetGameStatusText(), 0, 0, textStyle);
}

const char *CG_GameTypeString() {
	switch ( cgs.gametype ) {
	case GT_FFA:
		return "Free For All";
	case GT_TOURNAMENT:
		return "Duel";
	case GT_SINGLE_PLAYER:
		return "Race";
	case GT_TEAM:
		return "Team Deathmatch";
	case GT_CLAN_ARENA:
		return "Clan Arena";
	case GT_CTF:
		return "Capture the Flag";
	case GT_1FCTF:
		return "One Flag CTF";
	case GT_OBELISK:
		return "Overload";
	case GT_HARVESTER:
		return "Harvester";
	case GT_FREEZE:
		return "Freeze Tag";
	case GT_DOMINATION:
		return "Domination";
	case GT_ATTACK_DEFEND:
		return "Attack & Defend";
	case GT_RED_ROVER:
		return "Red Rover";
	default:
		return "";
	}
}
static void CG_DrawGameType(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle ) {
	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, CG_GameTypeString(), 0, 0, textStyle);
}

/*
=============
CG_GameTypeShortString

Provides a compact gametype label for scoreboard widgets.
=============
*/
static const char *CG_GameTypeShortString( void ) {
	switch ( cgs.gametype ) {
	case GT_FFA:
		return "FFA";
	case GT_TOURNAMENT:
		return "Duel";
	case GT_SINGLE_PLAYER:
		return "Race";
	case GT_TEAM:
		return "TDM";
	case GT_CLAN_ARENA:
		return "CA";
	case GT_CTF:
		return "CTF";
	case GT_1FCTF:
		return "1FCTF";
	case GT_OBELISK:
		return "Overload";
	case GT_HARVESTER:
		return "Harvester";
	case GT_FREEZE:
		return "Freeze";
	case GT_DOMINATION:
		return "Domination";
	case GT_ATTACK_DEFEND:
		return "A&D";
	case GT_RED_ROVER:
		return "Red Rover";
	default:
		return "Match";
	}
}

/*
=============
CG_DrawServerSettings

Summarizes factory metadata and server toggles for the intro/about overlays.
=============
*/
static void CG_DrawServerSettings(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	char		buffer[256];
	char		value[MAX_INFO_VALUE];
	const char	*info;
	qboolean	loadoutsEnabled;
	qboolean	itemTimersEnabled;
	qboolean	trainingEnabled;

	info = CG_ConfigString( CS_SERVERINFO );
	buffer[0] = '\0';
	loadoutsEnabled = CG_LoadoutsEnabled();
	itemTimersEnabled = qfalse;
	trainingEnabled = qfalse;

	if ( info && *info ) {
		CG_GetServerInfoValue( info, "g_itemTimers", value, sizeof( value ) );
		if ( value[0] && atoi( value ) ) {
			itemTimersEnabled = qtrue;
		}
		CG_GetServerInfoValue( info, "g_training", value, sizeof( value ) );
		if ( value[0] && atoi( value ) ) {
			trainingEnabled = qtrue;
		}
	}

	if ( cgs.factoryTitle[0] ) {
		CG_AppendServerSetting( buffer, sizeof( buffer ), cgs.factoryTitle );
	} else {
		CG_AppendServerSetting( buffer, sizeof( buffer ), "Standard factory" );
	}
	CG_AppendServerSetting( buffer, sizeof( buffer ), loadoutsEnabled ? "Loadouts on" : "Loadouts off" );
	CG_AppendServerSetting( buffer, sizeof( buffer ), itemTimersEnabled ? "Item timers on" : "Item timers off" );
	if ( trainingEnabled ) {
		CG_AppendServerSetting( buffer, sizeof( buffer ), "Training mode" );
	}

	if ( !buffer[0] ) {
		return;
	}

	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}

/*
=============
CG_DrawStartingWeapons

Lists the spawn loadout when the server advertises g_startingWeapons.
=============
*/
static void CG_DrawStartingWeapons(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	const char	*info;
	char		value[MAX_INFO_VALUE];
	int		mask;
	int		weapon;
	char		buffer[256];
	qboolean	listed;

	info = CG_ConfigString( CS_SERVERINFO );
	if ( !info || !*info ) {
		return;
	}

	CG_GetServerInfoValue( info, "g_startingWeapons", value, sizeof( value ) );
	mask = value[0] ? (int)strtol( value, NULL, 0 ) : 0;
	buffer[0] = '\0';
	listed = qfalse;

	for ( weapon = WP_GAUNTLET; weapon < WP_NUM_WEAPONS; weapon++ ) {
		int			bit;
		const char	*weaponName;

		bit = 1 << ( weapon - 1 );
		if ( ( mask & bit ) == 0 ) {
			continue;
		}

		weaponName = CG_ResolveWeaponName( weapon );
		if ( !weaponName ) {
			continue;
		}

		if ( listed ) {
			Q_strcat( buffer, sizeof( buffer ), ", " );
		}
		Q_strcat( buffer, sizeof( buffer ), weaponName );
		listed = qtrue;
	}

	if ( !listed ) {
		if ( CG_LoadoutsEnabled() ) {
			Q_strncpyz( buffer, "Factory loadouts active", sizeof( buffer ) );
		} else {
			Q_strncpyz( buffer, "Default loadout", sizeof( buffer ) );
		}
	}

	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);

/*
=============
CG_DrawGameLimit

Describes the active timelimit and score limits for the match.
=============
*/
static void CG_DrawGameLimit(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	char		buffer[128];
	const char	*info;
	int		limitValue;
	char		value[MAX_INFO_VALUE];

	buffer[0] = '\0';
	info = CG_ConfigString( CS_SERVERINFO );

	if ( cgs.timelimit > 0 ) {
		char segment[32];
		Com_sprintf( segment, sizeof( segment ), "Time %i", cgs.timelimit );
		CG_AppendServerSetting( buffer, sizeof( buffer ), segment );
	}

	limitValue = 0;
	if ( cgs.gametype >= GT_CTF && cgs.gametype != GT_ATTACK_DEFEND ) {
		limitValue = cgs.capturelimit;
		if ( limitValue > 0 ) {
			char segment[32];
			Com_sprintf( segment, sizeof( segment ), "Captures %i", limitValue );
			CG_AppendServerSetting( buffer, sizeof( buffer ), segment );
		}
	} else if ( cgs.gametype == GT_ATTACK_DEFEND ) {
		if ( info && *info ) {
			CG_GetServerInfoValue( info, "g_scorelimit", value, sizeof( value ) );
			limitValue = value[0] ? atoi( value ) : 0;
		}
		if ( limitValue > 0 ) {
			char segment[32];
			Com_sprintf( segment, sizeof( segment ), "Score %i", limitValue );
			CG_AppendServerSetting( buffer, sizeof( buffer ), segment );
		}
	} else if ( cgs.fraglimit > 0 ) {
		char segment[32];
		Com_sprintf( segment, sizeof( segment ), "Frags %i", cgs.fraglimit );
		CG_AppendServerSetting( buffer, sizeof( buffer ), segment );
	}

	if ( info && *info ) {
		CG_GetServerInfoValue( info, "mercylimit", value, sizeof( value ) );
		limitValue = value[0] ? atoi( value ) : 0;
		if ( limitValue > 0 ) {
			char segment[32];
			Com_sprintf( segment, sizeof( segment ), "Mercy %i", limitValue );
			CG_AppendServerSetting( buffer, sizeof( buffer ), segment );
		}
	}

	if ( !buffer[0] ) {
		return;
	}

	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}

/*
=============
CG_DrawGameTypeMap

Outputs "Gametype Fullname - Server Location - Map" for intro panels.
=============
*/
static void CG_DrawGameTypeMap(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	char		location[64];
	char		mapName[MAX_QPATH];
	char		buffer[256];

	CG_GetServerLocation( location, sizeof( location ) );
	CG_GetMapDisplayName( mapName, sizeof( mapName ) );
	Com_sprintf( buffer, sizeof( buffer ), "%s - %s - %s", CG_GameTypeString(), location, mapName );
	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}

/*
=============
CG_DrawMatchDetails

Renders "Game state - Gametype Shortname - Server Location - Map" text.
=============
*/
static void CG_DrawMatchDetails(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	char		location[64];
	char		mapName[MAX_QPATH];
	char		buffer[256];
	const char	*state;

	state = CG_GetMatchStateLabel();
	CG_GetServerLocation( location, sizeof( location ) );
	CG_GetMapDisplayName( mapName, sizeof( mapName ) );
	Com_sprintf( buffer, sizeof( buffer ), "%s - %s - %s - %s", state, CG_GameTypeShortString(), location, mapName );
	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}

/*
=============
CG_DrawMatchStatus

Renders "Game State - Scores message" using the existing HUD helpers.
=============
*/
static void CG_DrawMatchStatus(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	const char	*state;
	const char	*status;
	char		buffer[256];

	if ( !cg.snap ) {
		return;
	}

	state = CG_GetMatchStateLabel();
	status = CG_GetGameStatusText();
	if ( !state ) {
		state = "";
	}
	if ( !status ) {
		status = "";
	}
	Com_sprintf( buffer, sizeof( buffer ), "%s - %s", state, status );
	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}

/*
=============
CG_DrawMatchEndCondition

Describes why the intermission was triggered (limit or time).
=============
*/
static void CG_DrawMatchEndCondition(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	char		buffer[64];
	qboolean	drawn;

	buffer[0] = '\0';
	drawn = qfalse;
	if ( cg.intermissionStarted ) {
		if ( cgs.timelimit > 0 ) {
			int elapsedMinutes = ( cg.time - cgs.levelStartTime ) / 60000;
			if ( elapsedMinutes >= cgs.timelimit ) {
				Q_strncpyz( buffer, "Timelimit hit", sizeof( buffer ) );
				drawn = qtrue;
			}
		}

		if ( !drawn && cgs.gametype >= GT_CTF && cgs.capturelimit > 0 ) {
			if ( cg.teamScores[TEAM_RED] >= cgs.capturelimit || cg.teamScores[TEAM_BLUE] >= cgs.capturelimit ) {
				Q_strncpyz( buffer, "Capture limit reached", sizeof( buffer ) );
				drawn = qtrue;
			}
		}

		if ( !drawn && cgs.fraglimit > 0 && cgs.scores1 >= cgs.fraglimit ) {
			Q_strncpyz( buffer, "Frag limit reached", sizeof( buffer ) );
			drawn = qtrue;
		}
	}

	if ( !drawn ) {
		Q_strncpyz( buffer, cg.intermissionStarted ? "Match complete" : "Match in progress", sizeof( buffer ) );
	}

	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}

static void CG_Text_Paint_Limit(float *maxX, float x, float y, float scale, vec4_t color, const char* text, float adjust, int limit) {
  int len, count;
	vec4_t newColor;
	glyphInfo_t *glyph;
  if (text) {
// TTimo: FIXME
//    const unsigned char *s = text; // bk001206 - unsigned
    const char *s = text;
		float max = *maxX;
		float useScale;
		fontInfo_t *font = &cgDC.Assets.textFont;
		if (scale <= cg_smallFont.value) {
			font = &cgDC.Assets.smallFont;
		} else if (scale > cg_bigFont.value) {
			font = &cgDC.Assets.bigFont;
		}
		useScale = scale * font->glyphScale;
		trap_R_SetColor( color );
    len = strlen(text);					 
		if (limit > 0 && len > limit) {
			len = limit;
		}
		count = 0;
		while (s && *s && count < len) {
			glyph = &font->glyphs[(int)*s]; // TTimo: FIXME: getting nasty warnings without the cast, hopefully this doesn't break the VM build
			if ( Q_IsColorString( s ) ) {
				memcpy( newColor, g_color_table[ColorIndex(*(s+1))], sizeof( newColor ) );
				newColor[3] = color[3];
				trap_R_SetColor( newColor );
				s += 2;
				continue;
			} else {
	      float yadj = useScale * glyph->top;
				if (CG_Text_Width(s, useScale, 1) + x > max) {
					*maxX = 0;
					break;
				}
		    CG_Text_PaintChar(x, y - yadj, 
			                    glyph->imageWidth,
				                  glyph->imageHeight,
					                useScale, 
						              glyph->s,
							            glyph->t,
								          glyph->s2,
									        glyph->t2,
										      glyph->glyph);
	      x += (glyph->xSkip * useScale) + adjust;
				*maxX = x;
				count++;
				s++;
	    }
		}
	  trap_R_SetColor( NULL );
  }

}



#define PIC_WIDTH 12

void CG_DrawNewTeamInfo(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, qhandle_t shader) {
	int xx;
	float y;
	int i, j, len, count;
	const char *p;
	vec4_t		hcolor;
	float pwidth, lwidth, maxx, leftOver;
	clientInfo_t *ci;
	gitem_t	*item;
	qhandle_t h;

	// max player name width
	pwidth = 0;
	count = (numSortedTeamPlayers > 8) ? 8 : numSortedTeamPlayers;
	for (i = 0; i < count; i++) {
		ci = cgs.clientinfo + sortedTeamPlayers[i];
		if ( ci->infoValid && ci->team == cg.snap->ps.persistant[PERS_TEAM]) {
			len = CG_Text_Width( ci->name, scale, 0);
			if (len > pwidth)
				pwidth = len;
		}
	}

	// max location name width
	lwidth = 0;
	for (i = 1; i < MAX_LOCATIONS; i++) {
		p = CG_ConfigString(CS_LOCATIONS + i);
		if (p && *p) {
			len = CG_Text_Width(p, scale, 0);
			if (len > lwidth)
				lwidth = len;
		}
	}

	y = rect->y;

	for (i = 0; i < count; i++) {
		ci = cgs.clientinfo + sortedTeamPlayers[i];
		if ( ci->infoValid && ci->team == cg.snap->ps.persistant[PERS_TEAM]) {

			xx = rect->x + 1;
			for (j = 0; j <= PW_NUM_POWERUPS; j++) {
				if (ci->powerups & (1 << j)) {

					item = BG_FindItemForPowerup( j );

					if (item) {
						CG_DrawPic( xx, y, PIC_WIDTH, PIC_WIDTH, trap_R_RegisterShader( item->icon ) );
						xx += PIC_WIDTH;
					}
				}
			}

			// FIXME: max of 3 powerups shown properly
			xx = rect->x + (PIC_WIDTH * 3) + 2;

			CG_GetColorForHealth( ci->health, ci->armor, hcolor );
			trap_R_SetColor(hcolor);
			CG_DrawPic( xx, y + 1, PIC_WIDTH - 2, PIC_WIDTH - 2, cgs.media.heartShader );

			//Com_sprintf (st, sizeof(st), "%3i %3i", ci->health,	ci->armor);
			//CG_Text_Paint(xx, y + text_y, scale, hcolor, st, 0, 0); 

			// draw weapon icon
			xx += PIC_WIDTH + 1;

// weapon used is not that useful, use the space for task
#if 0
			if ( cg_weapons[ci->curWeapon].weaponIcon ) {
				CG_DrawPic( xx, y, PIC_WIDTH, PIC_WIDTH, cg_weapons[ci->curWeapon].weaponIcon );
			} else {
				CG_DrawPic( xx, y, PIC_WIDTH, PIC_WIDTH, cgs.media.deferShader );
			}
#endif

			trap_R_SetColor(NULL);
			if (cgs.orderPending) {
				// blink the icon
				if ( cg.time > cgs.orderTime - 2500 && (cg.time >> 9 ) & 1 ) {
					h = 0;
				} else {
					h = CG_StatusHandle(cgs.currentOrder);
				}
			}	else {
				h = CG_StatusHandle(ci->teamTask);
			}

			if (h) {
				CG_DrawPic( xx, y, PIC_WIDTH, PIC_WIDTH, h);
			}

			xx += PIC_WIDTH + 1;

			leftOver = rect->w - xx;
			maxx = xx + leftOver / 3;



			CG_Text_Paint_Limit(&maxx, xx, y + text_y, scale, color, ci->name, 0, 0); 

			p = CG_ConfigString(CS_LOCATIONS + ci->location);
			if (!p || !*p) {
				p = "unknown";
			}

			xx += leftOver / 3 + 2;
			maxx = rect->w - 4;

			CG_Text_Paint_Limit(&maxx, xx, y + text_y, scale, color, p, 0, 0); 
			y += text_y + 2;
			if ( y + text_y + 2 > rect->y + rect->h ) {
				break;
			}

		}
	}
}


void CG_DrawTeamSpectators(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader) {
const clientInfo_t *primary;
const clientInfo_t *secondary;
float y;
char buffer[128];

CG_UpdateSpectatorTargets();

primary = CG_SpectatorClientInfo(0);
secondary = CG_SpectatorClientInfo(1);

if (!primary && !secondary) {
return;
}

y = rect->y;

if (primary) {
Com_sprintf(buffer, sizeof(buffer), "Primary: %s", primary->name);
CG_Text_Paint(rect->x, y, scale, color, buffer, 0, 0, 0);
y += scale * 14.0f;
}

if (secondary) {
Com_sprintf(buffer, sizeof(buffer), "Secondary: %s", secondary->name);
CG_Text_Paint(rect->x, y, scale, color, buffer, 0, 0, 0);
}
}



void CG_DrawMedal(int ownerDraw, rectDef_t *rect, float scale, vec4_t color, qhandle_t shader) {
	score_t *score = &cg.scores[cg.selectedScore];
	float value = 0;
	char *text = NULL;
	color[3] = 0.25;

	switch (ownerDraw) {
		case CG_ACCURACY:
			value = score->accuracy;
			break;
		case CG_ASSISTS:
			value = score->assistCount;
			break;
		case CG_DEFEND:
			value = score->defendCount;
			break;
		case CG_EXCELLENT:
			value = score->excellentCount;
			break;
		case CG_IMPRESSIVE:
			value = score->impressiveCount;
			break;
		case CG_PERFECT:
			value = score->perfect;
			break;
		case CG_GAUNTLET:
			value = score->guantletCount;
			break;
		case CG_CAPTURES:
			value = score->captures;
			break;
	}

	if (value > 0) {
		if (ownerDraw != CG_PERFECT) {
			if (ownerDraw == CG_ACCURACY) {
				text = va("%i%%", (int)value);
				if (value > 50) {
					color[3] = 1.0;
				}
			} else {
				text = va("%i", (int)value);
				color[3] = 1.0;
			}
		} else {
			if (value) {
				color[3] = 1.0;
			}
			text = "Wow";
		}
	}

	trap_R_SetColor(color);
	CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );

	if (text) {
		color[3] = 1.0;
		value = CG_Text_Width(text, scale, 0);
		CG_Text_Paint(rect->x + (rect->w - value) / 2, rect->y + rect->h + 10 , scale, color, text, 0, 0, 0);
	}
	trap_R_SetColor(NULL);

}

	
/*
=============
CG_ParseActiveVoteCommand

Breaks the active vote string into the command and first argument.
=============
*/
static void CG_ParseActiveVoteCommand( char *command, size_t commandSize, char *argument, size_t argumentSize ) {
	char		buffer[MAX_STRING_CHARS];
	char		*cursor;
	const char	*token;

	if ( command && commandSize > 0 ) {
		command[0] = '\0';
	}
	if ( argument && argumentSize > 0 ) {
		argument[0] = '\0';
	}

	if ( !cgs.voteString[0] ) {
		return;
	}

	Q_strncpyz( buffer, cgs.voteString, sizeof( buffer ) );
	cursor = buffer;
	token = COM_ParseExt( &cursor, qfalse );
	if ( token && *token && command && commandSize > 0 ) {
		Q_strncpyz( command, token, commandSize );
	}

	token = COM_ParseExt( &cursor, qfalse );
	if ( token && *token && argument && argumentSize > 0 ) {
		Q_strncpyz( argument, token, argumentSize );
	}
}

/*
=============
CG_DrawVoteShot

Renders a preview levelshot for the active vote option.
=============
*/
static void CG_DrawVoteShot(rectDef_t *rect, int slot) {
	char		command[MAX_TOKEN_CHARS];
	char		argument[MAX_TOKEN_CHARS];
	char		mapName[MAX_QPATH];
	char		shotPath[MAX_QPATH];
	qhandle_t	shader;

	if ( slot > 0 || !cgs.voteTime ) {
		return;
	}

	CG_ParseActiveVoteCommand( command, sizeof( command ), argument, sizeof( argument ) );
	if ( argument[0] ) {
		CG_CleanMapName( argument, mapName, sizeof( mapName ) );
	} else {
		CG_BuildCleanMapName( mapName, sizeof( mapName ) );
	}

	Com_sprintf( shotPath, sizeof( shotPath ), "levelshots/%s.tga", mapName );
	shader = trap_R_RegisterShaderNoMip( shotPath );
	if ( !shader ) {
		shader = trap_R_RegisterShaderNoMip( "levelshots/preview/default" );
	}
	if ( !shader ) {
		return;
	}

	trap_R_SetColor( NULL );
	CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );
}

/*
=============
CG_DrawVoteMapSlot

Paints textual vote metadata for the supplied slot field.
=============
*/
static void CG_DrawVoteMapSlot(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot, cgVoteSlotField_t field) {
	char		command[MAX_TOKEN_CHARS];
	char		argument[MAX_TOKEN_CHARS];
	char		mapName[MAX_QPATH];
	char		buffer[256];
	const char	*text;

	if ( slot > 0 || !cgs.voteTime || !cgs.voteString[0] ) {
		return;
	}

	CG_ParseActiveVoteCommand( command, sizeof( command ), argument, sizeof( argument ) );
	buffer[0] = '\0';
	text = buffer;

	switch ( field ) {
	case CG_VOTE_FIELD_GAMETYPE:
		if ( command[0] ) {
			if ( !Q_stricmp( command, "map" ) || !Q_stricmp( command, "nextmap" ) ) {
				text = CG_GameTypeString();
			} else {
				Q_strncpyz( buffer, command, sizeof( buffer ) );
				text = buffer;
			}
		} else {
			text = "Vote";
		}
		break;
	case CG_VOTE_FIELD_MAP:
	case CG_VOTE_FIELD_NAME:
		if ( argument[0] ) {
			CG_CleanMapName( argument, mapName, sizeof( mapName ) );
			text = mapName;
		} else {
			CG_BuildCleanMapName( mapName, sizeof( mapName ) );
			text = mapName;
		}
		break;
	case CG_VOTE_FIELD_COUNT:
		Com_sprintf( buffer, sizeof( buffer ), "Yes %i / No %i", cgs.voteYes, cgs.voteNo );
		text = buffer;
		break;
	}

	if ( text && *text ) {
		CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, text, 0, 0, textStyle);
	}
}

/*
=============
CG_DrawVoteGametype
=============
*/
static void CG_DrawVoteGametype(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot) {
	CG_DrawVoteMapSlot(rect, scale, color, textStyle, slot, CG_VOTE_FIELD_GAMETYPE);
}

/*
=============
CG_DrawVoteMap
=============
*/
static void CG_DrawVoteMap(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot) {
	CG_DrawVoteMapSlot(rect, scale, color, textStyle, slot, CG_VOTE_FIELD_MAP);
}

/*
=============
CG_DrawVoteName
=============
*/
static void CG_DrawVoteName(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot) {
	CG_DrawVoteMapSlot(rect, scale, color, textStyle, slot, CG_VOTE_FIELD_NAME);
}

/*
=============
CG_DrawVoteCount
=============
*/
static void CG_DrawVoteCount(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot) {
	CG_DrawVoteMapSlot(rect, scale, color, textStyle, slot, CG_VOTE_FIELD_COUNT);
}

/*
=============
CG_DrawVoteTimer

Displays the remaining seconds for the active vote.
=============
*/
static void CG_DrawVoteTimer(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	int		remaining;
	char		buffer[32];

	if ( !cgs.voteTime ) {
		return;
	}

	remaining = ( VOTE_TIME - ( cg.time - cgs.voteTime ) ) / 1000;
	if ( remaining < 0 ) {
		remaining = 0;
	}
	Com_sprintf( buffer, sizeof( buffer ), "Vote %is", remaining );
	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}


/*
=============
CG_OwnerDraw

Routes owner-draw IDs to their rendering helpers.
=============
*/
void CG_OwnerDraw(float x, float y, float w, float h, float text_x, float text_y, int ownerDraw, int ownerDrawFlags, int align, float special, float scale, vec4_t color, qhandle_t shader, int textStyle) {
	rectDef_t rect;

  if ( cg_drawStatus.integer == 0 ) {
		return;
	}

	//if (ownerDrawFlags != 0 && !CG_OwnerDrawVisible(ownerDrawFlags)) {
	//	return;
	//}

  rect.x = x;
  rect.y = y;
  rect.w = w;
  rect.h = h;

	switch (ownerDraw) {
	case CG_SERVER_SETTINGS:
		CG_DrawServerSettings(&rect, text_x, text_y, scale, color, textStyle);
		break;
	case CG_STARTING_WEAPONS:
		CG_DrawStartingWeapons(&rect, text_x, text_y, scale, color, textStyle);
		break;
	case CG_GAME_LIMIT:
		CG_DrawGameLimit(&rect, text_x, text_y, scale, color, textStyle);
		break;
	case CG_GAME_TYPE_ICON:
		CG_DrawGameTypeIcon(&rect);
		break;
	case CG_GAME_TYPE_MAP:
		CG_DrawGameTypeMap(&rect, text_x, text_y, scale, color, textStyle);
		break;
	case CG_GAME_TYPE:
		CG_DrawGameType(&rect, scale, color, shader, textStyle);
		break;
	case CG_GAME_STATUS:
		CG_DrawGameStatus(&rect, scale, color, shader, textStyle);
		break;
	case CG_MATCH_DETAILS:
		CG_DrawMatchDetails(&rect, text_x, text_y, scale, color, textStyle);
		break;
	case CG_MATCH_END_CONDITION:
		CG_DrawMatchEndCondition(&rect, text_x, text_y, scale, color, textStyle);
		break;
	case CG_MATCH_STATUS:
		CG_DrawMatchStatus(&rect, text_x, text_y, scale, color, textStyle);
		break;
	case CG_CAPFRAGLIMIT:
		CG_DrawCapFragLimit(&rect, scale, color, shader, textStyle);
		break;
	case CG_LEVELTIMER:
		CG_DrawLevelTimer(&rect, scale, color, textStyle);
		break;
	case CG_ROUND:
		CG_DrawRoundLabel(&rect, text_x, text_y, scale, color, textStyle);
		break;
	case CG_ROUNDTIMER:
		CG_DrawRoundTimer(&rect, scale, color, textStyle);
		break;
	case CG_OVERTIME:
		CG_DrawOvertime(&rect, scale, color, textStyle);
		break;
	case CG_LOCALTIME:
		CG_DrawLocalTime(&rect, text_x, text_y, scale, color, textStyle);
		break;
	case CG_PLAYER_COUNTS:
		CG_DrawPlayerCounts(&rect, scale, color, textStyle);
		break;
	case CG_MAP_NAME:
		CG_DrawMapName(&rect, scale, color, textStyle);
		break;
	case CG_VOTEGAMETYPE1:
		CG_DrawVoteGametype(&rect, text_x, text_y, scale, color, textStyle, 1);
		break;
	case CG_VOTEGAMETYPE2:
		CG_DrawVoteGametype(&rect, text_x, text_y, scale, color, textStyle, 2);
		break;
	case CG_VOTEGAMETYPE3:
		CG_DrawVoteGametype(&rect, text_x, text_y, scale, color, textStyle, 3);
		break;
	case CG_VOTEMAP1:
		CG_DrawVoteMapSlot(&rect, text_x, text_y, scale, color, textStyle, 1);
		break;
	case CG_VOTEMAP2:
		CG_DrawVoteMapSlot(&rect, text_x, text_y, scale, color, textStyle, 2);
		break;
	case CG_VOTEMAP3:
		CG_DrawVoteMapSlot(&rect, text_x, text_y, scale, color, textStyle, 3);
		break;
	case CG_VOTESHOT1:
		CG_DrawVoteShot(&rect, 1);
		break;
	case CG_VOTESHOT2:
		CG_DrawVoteShot(&rect, 2);
		break;
	case CG_VOTESHOT3:
		CG_DrawVoteShot(&rect, 3);
		break;
	case CG_VOTENAME1:
		CG_DrawVoteName(&rect, text_x, text_y, scale, color, textStyle, 1);
		break;
	case CG_VOTENAME2:
		CG_DrawVoteName(&rect, text_x, text_y, scale, color, textStyle, 2);
		break;
	case CG_VOTENAME3:
		CG_DrawVoteName(&rect, text_x, text_y, scale, color, textStyle, 3);
		break;
	case CG_VOTECOUNT1:
		CG_DrawVoteCount(&rect, text_x, text_y, scale, color, textStyle, 1);
		break;
	case CG_VOTECOUNT2:
		CG_DrawVoteCount(&rect, text_x, text_y, scale, color, textStyle, 2);
		break;
	case CG_VOTECOUNT3:
		CG_DrawVoteCount(&rect, text_x, text_y, scale, color, textStyle, 3);
		break;
	case CG_VOTETIMER:
		CG_DrawVoteTimer(&rect, text_x, text_y, scale, color, textStyle);
		break;

  case CG_PLAYER_ARMOR_ICON:
    CG_DrawPlayerArmorIcon(&rect, ownerDrawFlags & CG_SHOW_2DONLY);
    break;
  case CG_PLAYER_ARMOR_ICON2D:
    CG_DrawPlayerArmorIcon(&rect, qtrue);
    break;
  case CG_PLAYER_ARMOR_VALUE:
    CG_DrawPlayerArmorValue(&rect, scale, color, shader, textStyle);
    break;
  case CG_PLAYER_ARMOR_BAR_100:
CG_DrawPlayerArmorBar(&rect, shader, qfalse);
break;
  case CG_PLAYER_ARMOR_BAR_200:
CG_DrawPlayerArmorBar(&rect, shader, qtrue);
break;
  case CG_PLAYER_AMMO_ICON:
    CG_DrawPlayerAmmoIcon(&rect, ownerDrawFlags & CG_SHOW_2DONLY);
    break;
  case CG_PLAYER_AMMO_ICON2D:
    CG_DrawPlayerAmmoIcon(&rect, qtrue);
    break;
  case CG_PLAYER_AMMO_VALUE:
    CG_DrawPlayerAmmoValue(&rect, scale, color, shader, textStyle);
    break;
  case CG_SELECTEDPLAYER_HEAD:
    CG_DrawSelectedPlayerHead(&rect, ownerDrawFlags & CG_SHOW_2DONLY, qfalse);
    break;
  case CG_VOICE_HEAD:
    CG_DrawSelectedPlayerHead(&rect, ownerDrawFlags & CG_SHOW_2DONLY, qtrue);
    break;
  case CG_VOICE_NAME:
    CG_DrawSelectedPlayerName(&rect, scale, color, qtrue, textStyle);
    break;
  case CG_SELECTEDPLAYER_STATUS:
    CG_DrawSelectedPlayerStatus(&rect);
    break;
  case CG_SELECTEDPLAYER_ARMOR:
    CG_DrawSelectedPlayerArmor(&rect, scale, color, shader, textStyle);
    break;
  case CG_SELECTEDPLAYER_HEALTH:
    CG_DrawSelectedPlayerHealth(&rect, scale, color, shader, textStyle);
    break;
  case CG_SELECTEDPLAYER_NAME:
    CG_DrawSelectedPlayerName(&rect, scale, color, qfalse, textStyle);
    break;
  case CG_SELECTEDPLAYER_LOCATION:
    CG_DrawSelectedPlayerLocation(&rect, scale, color, textStyle);
    break;
  case CG_SELECTEDPLAYER_WEAPON:
    CG_DrawSelectedPlayerWeapon(&rect);
    break;
  case CG_SELECTEDPLAYER_POWERUP:
    CG_DrawSelectedPlayerPowerup(&rect, ownerDrawFlags & CG_SHOW_2DONLY);
    break;
  case CG_PLAYER_HEAD:
    CG_DrawPlayerHead(&rect, ownerDrawFlags & CG_SHOW_2DONLY);
    break;
  case CG_PLAYER_ITEM:
    CG_DrawPlayerItem(&rect, scale, ownerDrawFlags & CG_SHOW_2DONLY);
    break;
  case CG_PLAYER_SCORE:
    CG_DrawPlayerScore(&rect, scale, color, shader, textStyle);
    break;
  case CG_PLAYER_HEALTH:
    CG_DrawPlayerHealth(&rect, scale, color, shader, textStyle);
    break;
  case CG_PLAYER_HEALTH_BAR_100:
CG_DrawPlayerHealthBar(&rect, shader, qfalse);
break;
  case CG_PLAYER_HEALTH_BAR_200:
CG_DrawPlayerHealthBar(&rect, shader, qtrue);
break;
  case CG_RED_SCORE:
    CG_DrawRedScore(&rect, scale, color, shader, textStyle);
                break;
  case CG_BLUE_SCORE:
    CG_DrawBlueScore(&rect, scale, color, shader, textStyle);
                break;
  case CG_RED_PLAYER_COUNT:
		CG_DrawTeamPlayerCount(&rect, scale, color, textStyle, TEAM_RED);
		break;
  case CG_BLUE_PLAYER_COUNT:
		CG_DrawTeamPlayerCount(&rect, scale, color, textStyle, TEAM_BLUE);
		break;
  case CG_RED_TIMEOUT_COUNT:
		CG_DrawTeamTimeoutCount(&rect, scale, color, textStyle, TEAM_RED);
		break;
  case CG_BLUE_TIMEOUT_COUNT:
		CG_DrawTeamTimeoutCount(&rect, scale, color, textStyle, TEAM_BLUE);
		break;
  case CG_RED_AVG_PING:
		CG_DrawTeamAveragePing(&rect, scale, color, textStyle, TEAM_RED);
		break;
  case CG_BLUE_AVG_PING:
		CG_DrawTeamAveragePing(&rect, scale, color, textStyle, TEAM_BLUE);
		break;
  case CG_RED_NAME:
    CG_DrawRedName(&rect, scale, color, textStyle);
    break;
  case CG_BLUE_NAME:
    CG_DrawBlueName(&rect, scale, color, textStyle);
    break;
  case CG_BLUE_FLAGHEAD:
    CG_DrawBlueFlagHead(&rect);
    break;
  case CG_BLUE_FLAGSTATUS:
    CG_DrawBlueFlagStatus(&rect, shader);
    break;
  case CG_BLUE_FLAGNAME:
    CG_DrawBlueFlagName(&rect, scale, color, textStyle);
    break;
  case CG_RED_FLAGHEAD:
    CG_DrawRedFlagHead(&rect);
    break;
  case CG_RED_FLAGSTATUS:
    CG_DrawRedFlagStatus(&rect, shader);
    break;
  case CG_RED_FLAGNAME:
    CG_DrawRedFlagName(&rect, scale, color, textStyle);
    break;
  case CG_HARVESTER_SKULLS:
    CG_HarvesterSkulls(&rect, scale, color, qfalse, textStyle);
    break;
  case CG_HARVESTER_SKULLS2D:
    CG_HarvesterSkulls(&rect, scale, color, qtrue, textStyle);
    break;
  case CG_ONEFLAG_STATUS:
    CG_OneFlagStatus(&rect);
    break;
  case CG_PLAYER_LOCATION:
    CG_DrawPlayerLocation(&rect, scale, color, textStyle);
    break;
  case CG_TEAM_COLOR:
    CG_DrawTeamColor(&rect, color);
    break;
  case CG_CTF_POWERUP:
    CG_DrawCTFPowerUp(&rect);
    break;
  case CG_AREA_POWERUP:
		CG_DrawAreaPowerUp(&rect, align, special, scale, color);
    break;
  case CG_PLAYER_STATUS:
    CG_DrawPlayerStatus(&rect);
    break;
  case CG_PLAYER_HASFLAG:
    CG_DrawPlayerHasFlag(&rect, qfalse);
    break;
  case CG_PLAYER_HASFLAG2D:
    CG_DrawPlayerHasFlag(&rect, qtrue);
    break;
  case CG_AREA_SYSTEMCHAT:
    CG_DrawAreaSystemChat(&rect, scale, color, shader);
    break;
  case CG_AREA_TEAMCHAT:
    CG_DrawAreaTeamChat(&rect, scale, color, shader);
    break;
  case CG_AREA_CHAT:
    CG_DrawAreaChat(&rect, scale, color, shader);
    break;
  case CG_AREA_NEW_CHAT:
                CG_DrawNewChatArea(&rect, scale, color, textStyle);
                break;
  case CG_KILLER:
    CG_DrawKiller(&rect, scale, color, shader, textStyle);
    break;
	case CG_ACCURACY:
	case CG_ASSISTS:
	case CG_DEFEND:
	case CG_EXCELLENT:
	case CG_IMPRESSIVE:
	case CG_PERFECT:
	case CG_GAUNTLET:
	case CG_CAPTURES:
		CG_DrawMedal(ownerDraw, &rect, scale, color, shader);
		break;
  case CG_SPECTATORS:
                CG_DrawTeamSpectators(&rect, scale, color, shader);
                break;
  case CG_SELECTED_PLYR_TEAM_COLOR:
		CG_DrawSelectedPlayerTeamColor(&rect);
		break;
  case CG_SELECTED_PLYR_ACCURACY:
		CG_DrawSelectedPlayerAccuracy(&rect, scale, color, textStyle);
		break;
  case CG_PLYR_BEST_WEAPON_NAME:
		CG_DrawSelectedPlayerBestWeapon(&rect, scale, color, textStyle);
		break;
  case CG_SPEC_MESSAGES:
		CG_DrawSpectatorMessages(&rect, scale, color, textStyle);
		break;
  case CG_TEAMINFO:
                if (cg_currentSelectedPlayer.integer == numSortedTeamPlayers) {
                        CG_DrawNewTeamInfo(&rect, text_x, text_y, scale, color, shader);
                }
                break;
  case CG_1STPLACE:
    CG_Draw1stPlace(&rect, scale, color, shader, textStyle);
                break;
  case CG_2NDPLACE:
    CG_Draw2ndPlace(&rect, scale, color, shader, textStyle);
                break;
  case CG_1ST_PLACE_SCORE:
    CG_Draw1stPlace(&rect, scale, color, shader, textStyle);
                break;
  case CG_2ND_PLACE_SCORE:
    CG_Draw2ndPlace(&rect, scale, color, shader, textStyle);
                break;
  case CG_PLAYER_OBIT:
    CG_DrawPlayerObituary(&rect, scale, color, textStyle);
                break;
  case CG_MATCH_STATE:
		CG_DrawMatchState(&rect, scale, color, textStyle);
		break;
  case CG_1ST_PLYR: {
qhandle_t nameShader = shader;
if (!nameShader && cg.competitiveHudLoaded) {
nameShader = cgs.media.inkFadeLeftShader;
}
    CG_DrawSpectatorPlayerName(&rect, scale, color, textStyle, 0, nameShader);
                break;
}
  case CG_1ST_PLYR_SCORE:
    CG_DrawSpectatorPlayerScore(&rect, scale, color, textStyle, 0);
                break;
  case CG_1ST_PLYR_HEALTH_ARMOR:
    CG_DrawSpectatorHealthArmor(&rect, scale, color, textStyle, 0);
                break;
  case CG_1ST_PLYR_AVATAR:
		CG_DrawSpectatorProfileImage(&rect, 0);
			break;
  case CG_2ND_PLYR: {
qhandle_t nameShader = shader;
if (!nameShader && cg.competitiveHudLoaded) {
nameShader = cgs.media.inkFadeRightShader;
}
    CG_DrawSpectatorPlayerName(&rect, scale, color, textStyle, 1, nameShader);
                break;
}
  case CG_2ND_PLYR_SCORE:
    CG_DrawSpectatorPlayerScore(&rect, scale, color, textStyle, 1);
                break;
  case CG_2ND_PLYR_HEALTH_ARMOR:
    CG_DrawSpectatorHealthArmor(&rect, scale, color, textStyle, 1);
                break;
  case CG_2ND_PLYR_AVATAR:
		CG_DrawSpectatorProfileImage(&rect, 1);
			break;
  case CG_HEALTH_COLORIZED: {
qhandle_t followShader = shader;
if (!followShader && cg.competitiveHudLoaded) {
followShader = cgs.media.scoreboxFollowShader;
}
    CG_DrawHealthColorized(&rect, followShader);
                break;
}
  case CG_ARMORTIERED_COLORIZED:
    CG_DrawArmorTieredColorized(&rect);
                break;
  case CG_TEAM_COLORIZED: {
qhandle_t teamShader = shader;
if (!teamShader && cg.competitiveHudLoaded) {
teamShader = cgs.media.scoreboxSpecShader;
}
    CG_DrawTeamColorized(&rect, teamShader);
                break;
}
	case CG_FOLLOW_PLAYER_NAME_EX:
	CG_DrawFollowPlayerNameEx(&rect, scale, color, textStyle);
	break;
	case CG_MATCH_WINNER:
	CG_DrawGameStatus(&rect, scale, color, shader, textStyle);
	break;
	case CG_RACE_STATUS:
	CG_DrawRaceStatus(&rect, scale, color, textStyle);
	break;
	case CG_RACE_TIMES:
	CG_DrawRaceTimes(&rect, scale, color, textStyle);
	break;
	case CG_FLAG_STATUS:
	case CG_RED_BASESTATUS:
	case CG_BLUE_BASESTATUS:
	case CG_PLAYER_HASKEY:
	break;
  case CG_SPEEDOMETER:
CG_DrawSpeedometer(&rect, scale, color, textStyle);
break;
  case CG_TEAM_PLYR_COUNT:
CG_DrawPlayerCount(&rect, scale, color, textStyle, qtrue);
break;
  case CG_ENEMY_PLYR_COUNT:
CG_DrawPlayerCount(&rect, scale, color, textStyle, qfalse);
break;
  case CG_FOLLOW_PLAYER_NAME_EX:
    CG_DrawFollowPlayerNameEx(&rect, scale, color, textStyle);
                break;
  case CG_MATCH_WINNER:
    CG_DrawGameStatus(&rect, scale, color, shader, textStyle);
                break;
  case CG_RACE_STATUS:
  case CG_RACE_TIMES:
  case CG_FLAG_STATUS:
  case CG_RED_BASESTATUS:
  case CG_BLUE_BASESTATUS:
  case CG_PLAYER_HASKEY:
                break;
  default:
    break;
  }
}

void CG_MouseEvent( int x, int y ) {
	int n;
	qboolean allowSpectatorUi = ( cg.snap && ( cg.snap->ps.pm_flags & PMF_FOLLOW ) );

	if ( cg_ignoreMouseInput.integer ) {
		return;
	}

	if ( ( cg.predictedPlayerState.pm_type == PM_NORMAL || ( cg.predictedPlayerState.pm_type == PM_SPECTATOR && !allowSpectatorUi ) ) &&
		 cg.showScores == qfalse ) {
		trap_Key_SetCatcher( 0 );
		return;
	}

	cgs.cursorX += x;
	if ( cgs.cursorX < 0 ) {
		cgs.cursorX = 0;
	} else if ( cgs.cursorX > 640 ) {
		cgs.cursorX = 640;
	}

	cgs.cursorY += y;
	if ( cgs.cursorY < 0 ) {
		cgs.cursorY = 0;
	} else if ( cgs.cursorY > 480 ) {
		cgs.cursorY = 480;
	}

	n = Display_CursorType( cgs.cursorX, cgs.cursorY );
	cgs.activeCursor = 0;
	if ( n == CURSOR_ARROW ) {
		cgs.activeCursor = cgs.media.selectCursor;
	} else if ( n == CURSOR_SIZER ) {
		cgs.activeCursor = cgs.media.sizeCursor;
	}

	if ( cgs.capturedItem ) {
		Display_MouseMove( cgs.capturedItem, x, y );
	} else {
		Display_MouseMove( NULL, cgs.cursorX, cgs.cursorY );
	}
}

}

/*
==================
CG_HideTeamMenus
==================

*/
void CG_HideTeamMenu() {
  Menus_CloseByName("teamMenu");
  Menus_CloseByName("getMenu");
}

/*
==================
CG_ShowTeamMenus
==================

*/
void CG_ShowTeamMenu() {
  Menus_OpenByName("teamMenu");
}




/*
==================
CG_EventHandling
==================
 type 0 - no event handling
      1 - team menu
      2 - hud editor

*/
void CG_EventHandling(int type) {
	cgs.eventHandling = type;
  if (type == CGAME_EVENT_NONE) {
    CG_HideTeamMenu();
  } else if (type == CGAME_EVENT_TEAMMENU) {
    //CG_ShowTeamMenu();
  } else if (type == CGAME_EVENT_SCOREBOARD) {
  }

}



void CG_KeyEvent(int key, qboolean down) {
qboolean allowSpectatorUi = (cg.snap && (cg.snap->ps.pm_flags & PMF_FOLLOW));

if (!down) {
return;
}

if ( cg.predictedPlayerState.pm_type == PM_NORMAL || (cg.predictedPlayerState.pm_type == PM_SPECTATOR && !allowSpectatorUi && cg.showScores == qfalse)) {
CG_EventHandling(CGAME_EVENT_NONE);
    trap_Key_SetCatcher(0);
return;
}

  //if (key == trap_Key_GetKey("teamMenu") || !Display_CaptureItem(cgs.cursorX, cgs.cursorY)) {
    // if we see this then we should always be visible
  //  CG_EventHandling(CGAME_EVENT_NONE);
  //  trap_Key_SetCatcher(0);
  //}



  Display_HandleKey(key, down, cgs.cursorX, cgs.cursorY);

	if (cgs.capturedItem) {
		cgs.capturedItem = NULL;
	}	else {
		if (key == K_MOUSE2 && down) {
			cgs.capturedItem = Display_CaptureItem(cgs.cursorX, cgs.cursorY);
		}
	}
}

int CG_ClientNumFromName(const char *p) {
  int i;
  for (i = 0; i < cgs.maxclients; i++) {
    if (cgs.clientinfo[i].infoValid && Q_stricmp(cgs.clientinfo[i].name, p) == 0) {
      return i;
    }
  }
  return -1;
}

void CG_ShowResponseHead() {
  Menus_OpenByName("voiceMenu");
	trap_Cvar_Set("cl_conXOffset", "72");
	cg.voiceTime = cg.time;
}

/*
=============
CG_MenuScript_OpenScoreboard

Requests fresh scoreboard data and forces the HUD overlay to appear.
=============
*/
static void CG_MenuScript_OpenScoreboard( void ) {
	CG_BuildSpectatorString();
	if ( cg.scoresRequestTime + 2000 < cg.time ) {
		cg.scoresRequestTime = cg.time;
		trap_SendClientCommand( "score" );
		if ( !cg.showScores ) {
			cg.showScores = qtrue;
			cg.numScores = 0;
		}
	} else {
		cg.showScores = qtrue;
	}
	CG_EventHandling( CGAME_EVENT_SCOREBOARD );
}

/*
=============
CG_MenuScript_CloseScoreboard

Hides the Quake Live scoreboard overlay.
=============
*/
static void CG_MenuScript_CloseScoreboard( void ) {
	if ( cg.showScores ) {
		cg.showScores = qfalse;
		cg.scoreFadeTime = cg.time;
	}
	if ( cgs.eventHandling == CGAME_EVENT_SCOREBOARD ) {
		CG_EventHandling( CGAME_EVENT_NONE );
	}
}

/*
=============
CG_MenuScript_WebCommand

Dispatches browser-related console commands on behalf of HUD scripts.
=============
*/
static void CG_MenuScript_WebCommand( const char *command, const char *argument ) {
	char buffer[MAX_STRING_CHARS];

	if ( !command || !*command ) {
		return;
	}

	if ( argument && *argument ) {
		Com_sprintf( buffer, sizeof( buffer ), "%s %s\n", command, argument );
	} else {
		Com_sprintf( buffer, sizeof( buffer ), "%s\n", command );
	}

	trap_SendConsoleCommand( buffer );
}

/*
=============
CG_MenuScript_FollowClient

Follows the specified client if they are valid.
=============
*/
static void CG_MenuScript_FollowClient( int clientNum ) {
	if ( clientNum < 0 || clientNum >= cgs.maxclients ) {
		return;
	}
	if ( !cgs.clientinfo[clientNum].infoValid ) {
		return;
	}

	trap_SendClientCommand( va( "follow %d", clientNum ) );
}

/*
=============
CG_MenuScript_FollowSlot

Follows the player occupying a spectator slot (0 = primary, 1 = secondary).
=============
*/
static void CG_MenuScript_FollowSlot( int slot ) {
	int clientNum;

	CG_UpdateSpectatorTargets();
	if ( slot < 0 || slot >= cg.spectatorClientCount ) {
		return;
	}

	clientNum = cg.spectatorClientOrder[slot];
	if ( clientNum < 0 || clientNum >= cgs.maxclients ) {
		return;
	}

	CG_MenuScript_FollowClient( clientNum );
}

/*
=============
CG_MenuScript_StopFollowing

Releases the spectator camera from any follow target.
=============
*/
static void CG_MenuScript_StopFollowing( void ) {
	trap_SendClientCommand( "follow" );
}

/*
=============
CG_MenuScript_ToggleHudEditor

Toggles the HUD editor event catcher used by Quake Live.
=============
*/
static void CG_MenuScript_ToggleHudEditor( void ) {
	int catcher;
	qboolean enable;

	enable = ( cgs.eventHandling != CGAME_EVENT_EDITHUD );
	catcher = trap_Key_GetCatcher();
	if ( enable ) {
		CG_EventHandling( CGAME_EVENT_EDITHUD );
		trap_Key_SetCatcher( catcher | KEYCATCH_CGAME );
	} else {
		CG_EventHandling( CGAME_EVENT_NONE );
		trap_Key_SetCatcher( catcher & ~KEYCATCH_CGAME );
	}
}

/*
=============
CG_MenuScript_ParseOptionalToken

Reads the next token if one exists without permanently advancing on failure.
=============
*/
static qboolean CG_MenuScript_ParseOptionalToken( char **args, const char **out ) {
	char *backup;

	if ( !args || !out ) {
		return qfalse;
	}

	backup = *args;
	if ( String_Parse( args, out ) ) {
		return qtrue;
	}

	*out = NULL;
	*args = backup;
	return qfalse;
}

/*
=============
CG_MenuScript_FollowName

Follows the player whose name was provided by a menu script.
=============
*/
static void CG_MenuScript_FollowName( const char *playerName ) {
	int clientNum;

	if ( !playerName || !*playerName ) {
		return;
	}

	clientNum = CG_ClientNumFromName( playerName );
	if ( clientNum >= 0 ) {
		CG_MenuScript_FollowClient( clientNum );
	}
}

void CG_RunMenuScript(char **args) {
	const char *name;
	const char *argument;

	if ( !args ) {
		return;
	}

	if ( !String_Parse( args, &name ) ) {
		return;
	}

	if ( !Q_stricmp( name, "openScoreboard" ) ) {
		CG_MenuScript_OpenScoreboard();
		return;
	}

	if ( !Q_stricmp( name, "closeScoreboard" ) ) {
		CG_MenuScript_CloseScoreboard();
		return;
	}

	if ( !Q_stricmp( name, "spectatorFollowNext" ) ) {
		CG_SpectatorFollowCycle( 1 );
		return;
	}

	if ( !Q_stricmp( name, "spectatorFollowPrev" ) ) {
		CG_SpectatorFollowCycle( -1 );
		return;
	}

	if ( !Q_stricmp( name, "spectatorFollowPrimary" ) ) {
		CG_MenuScript_FollowSlot( 0 );
		return;
	}

	if ( !Q_stricmp( name, "spectatorFollowSecondary" ) ) {
		CG_MenuScript_FollowSlot( 1 );
		return;
	}

	if ( !Q_stricmp( name, "spectatorFollowSlot" ) ) {
		if ( String_Parse( args, &argument ) ) {
			CG_MenuScript_FollowSlot( atoi( argument ) );
		}
		return;
	}

	if ( !Q_stricmp( name, "spectatorFollowClient" ) ) {
		if ( String_Parse( args, &argument ) ) {
			CG_MenuScript_FollowClient( atoi( argument ) );
		}
		return;
	}

	if ( !Q_stricmp( name, "spectatorFollowName" ) || !Q_stricmp( name, "spectatorFollowPlayer" ) ) {
		if ( String_Parse( args, &argument ) ) {
			CG_MenuScript_FollowName( argument );
		}
		return;
	}

	if ( !Q_stricmp( name, "spectatorFollowStop" ) ) {
		CG_MenuScript_StopFollowing();
		return;
	}

	if ( !Q_stricmp( name, "hud_editToggle" ) ) {
		CG_MenuScript_ToggleHudEditor();
		return;
	}

	if ( !Q_stricmp( name, "web_showBrowserHash" ) ) {
		argument = NULL;
		CG_MenuScript_ParseOptionalToken( args, &argument );
		CG_MenuScript_WebCommand( "web_showBrowser", argument );
		return;
	}

	if ( !Q_strnicmp( name, "web_", 4 ) ) {
		argument = NULL;
		CG_MenuScript_ParseOptionalToken( args, &argument );
		CG_MenuScript_WebCommand( name, argument );
		return;
	}

	Com_Printf( "Unknown cgame menu script '%s'\n", name );
}


void CG_GetTeamColor(vec4_t *color) {
  if (cg.snap->ps.persistant[PERS_TEAM] == TEAM_RED) {
    (*color)[0] = 1.0f;
    (*color)[3] = 0.25f;
    (*color)[1] = (*color)[2] = 0.0f;
  } else if (cg.snap->ps.persistant[PERS_TEAM] == TEAM_BLUE) {
    (*color)[0] = (*color)[1] = 0.0f;
    (*color)[2] = 1.0f;
    (*color)[3] = 0.25f;
  } else {
    (*color)[0] = (*color)[2] = 0.0f;
    (*color)[1] = 0.17f;
    (*color)[3] = 0.25f;
	}
}

