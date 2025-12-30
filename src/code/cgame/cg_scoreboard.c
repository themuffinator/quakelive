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
// cg_scoreboard -- draw the scoreboard on top of the game screen
#include "cg_local.h"
#include "../game/generated/ql_gametype_strings.h"


#define	SCOREBOARD_X		(0)

#define SB_HEADER			86
#define SB_TOP				(SB_HEADER+32)

// Where the status bar starts, so we don't overwrite it
#define SB_STATUSBAR		420

#define SB_NORMAL_HEIGHT	40
#define SB_INTER_HEIGHT		16 // interleaved height

#define SB_MAXCLIENTS_NORMAL  ((SB_STATUSBAR - SB_TOP) / SB_NORMAL_HEIGHT)
#define SB_MAXCLIENTS_INTER   ((SB_STATUSBAR - SB_TOP) / SB_INTER_HEIGHT - 1)

// Used when interleaved



#define SB_LEFT_BOTICON_X	(SCOREBOARD_X+0)
#define SB_LEFT_HEAD_X		(SCOREBOARD_X+32)
#define SB_RIGHT_BOTICON_X	(SCOREBOARD_X+64)
#define SB_RIGHT_HEAD_X		(SCOREBOARD_X+96)
// Normal
#define SB_BOTICON_X		(SCOREBOARD_X+32)
#define SB_HEAD_X			(SCOREBOARD_X+64)

#define SB_SCORELINE_X		112

#define SB_RATING_WIDTH	    (6 * BIGCHAR_WIDTH) // width 6
#define SB_SCORE_X			(SB_SCORELINE_X + BIGCHAR_WIDTH) // width 6
#define SB_RATING_X			(SB_SCORELINE_X + 6 * BIGCHAR_WIDTH) // width 6
#define SB_PING_X			(SB_SCORELINE_X + 12 * BIGCHAR_WIDTH + 8) // width 5
#define SB_TIME_X			(SB_SCORELINE_X + 17 * BIGCHAR_WIDTH + 8) // width 5
#define SB_NAME_X			(SB_SCORELINE_X + 22 * BIGCHAR_WIDTH) // width 15

typedef enum {
	CG_HUD_SCOREBOARD_VARIANT_FFA,
	CG_HUD_SCOREBOARD_VARIANT_TEAM,
	CG_HUD_SCOREBOARD_VARIANT_ROUND,
	CG_HUD_SCOREBOARD_VARIANT_DOMINATION,
	CG_HUD_SCOREBOARD_VARIANT_ATTACK_DEFEND
} cgHudScoreboardVariant_t;

// The new and improved score board
//
// In cases where the number of clients is high, the score board heads are interleaved
// here's the layout

//
//	0   32   80  112  144   240  320  400   <-- pixel position
//  bot head bot head score ping time name
//  
//  wins/losses are drawn on bot icon now

static qboolean localClient; // true if local client has been displayed

static cgHudScoreboard_t cgHudScoreboard;

static void CG_UpdateHudScoreboardSummary( void );
static void CG_UpdateHudScoreboardBanners( void );

/*
=============
CG_ScoreboardWideScaleFactor

Returns the widescreen scale factor for 640-based coordinates.
=============
*/
static float CG_ScoreboardWideScaleFactor( void ) {
	float		scale;

	if ( cgs.glconfig.vidWidth <= 0 || cg.refdef.width <= 0 ) {
		return 1.0f;
	}

	scale = (float)cg.refdef.width / (float)SCREEN_WIDTH;
	return scale;
}

/*
=============
CG_ScoreboardWideScale

Returns the widescreen-scaled coordinate for a 640-based x position.
=============
*/
static float CG_ScoreboardWideScale( float baseX ) {
	return baseX * CG_ScoreboardWideScaleFactor();
}

/*
=============
CG_ScoreboardVariant

Determines which HUD scoreboard variant should be exposed for the gametype.
=============
*/
static cgHudScoreboardVariant_t CG_ScoreboardVariant( void ) {
	switch ( cgs.gametype ) {
	case GT_CA:
	case GT_FREEZE:
		return CG_HUD_SCOREBOARD_VARIANT_ROUND;
	case GT_DOMINATION:
		return CG_HUD_SCOREBOARD_VARIANT_DOMINATION;
	case GT_ATTACK_DEFEND:
		return CG_HUD_SCOREBOARD_VARIANT_ATTACK_DEFEND;
	default:
		break;
	}

	if ( cgs.gametype >= GT_TEAM ) {
		return CG_HUD_SCOREBOARD_VARIANT_TEAM;
	}

	return CG_HUD_SCOREBOARD_VARIANT_FFA;
}

/*
=============
CG_ResetHudScoreboard

Clears and seeds the HUD scoreboard cache for menu-driven scoreboxes.
=============
*/
static void CG_ResetHudScoreboard( qboolean timersActive ) {
	float			scale;

	memset( &cgHudScoreboard, 0, sizeof( cgHudScoreboard ) );

	scale = CG_ScoreboardWideScaleFactor();

	cgHudScoreboard.scale = scale;
	cgHudScoreboard.widescreen = ( cgs.glconfig.vidWidth > SCREEN_WIDTH );
	cgHudScoreboard.scoreboardX = CG_ScoreboardWideScale( SCOREBOARD_X );
	cgHudScoreboard.scoreboardWidth = CG_ScoreboardWideScale( SCREEN_WIDTH );
	cgHudScoreboard.scoreX = CG_ScoreboardWideScale( SB_SCORE_X + (SB_RATING_WIDTH / 2) );
	cgHudScoreboard.scoreWidth = SB_RATING_WIDTH * scale;
	cgHudScoreboard.pingX = CG_ScoreboardWideScale( SB_PING_X );
	cgHudScoreboard.pingWidth = 5 * BIGCHAR_WIDTH * scale;
	cgHudScoreboard.timeX = CG_ScoreboardWideScale( SB_TIME_X );
	cgHudScoreboard.timeWidth = timersActive ? ( 5 * BIGCHAR_WIDTH * scale ) : 0;
	cgHudScoreboard.nameX = CG_ScoreboardWideScale( SB_NAME_X );
	cgHudScoreboard.nameWidth = 15 * BIGCHAR_WIDTH * scale;
	cgHudScoreboard.gametype = cgs.gametype;
	cgHudScoreboard.variant = CG_ScoreboardVariant();

	cgHudScoreboard.overtimeConfigured = (qboolean)( cgs.matchOvertimeCount > 0 );
	cgHudScoreboard.overtimeActive = cgs.matchOvertimeActive;
	cgHudScoreboard.overtimeCount = cgs.matchOvertimeCount;
	cgHudScoreboard.suddenDeathConfigured =
			( cgs.matchSuddenDeathStartSeconds > 0 && cgs.matchSuddenDeathTickSeconds > 0 );
	cgHudScoreboard.suddenDeathActive = cgs.matchSuddenDeathSpawnDelayActive;
	cgHudScoreboard.suddenDeathRespawns = cgs.matchSuddenDeathRespawnsEnabled;
	cgHudScoreboard.suddenDeathDelayActive = cgs.matchSuddenDeathSpawnDelayActive;
	cgHudScoreboard.suddenDeathStart = cgs.matchSuddenDeathStartSeconds;
	cgHudScoreboard.suddenDeathTick = cgs.matchSuddenDeathTickSeconds;
	cgHudScoreboard.suddenDeathMax = cgs.matchSuddenDeathMaxSeconds;
	cgHudScoreboard.suddenDeathIncrement = cgs.matchSuddenDeathIncrementSeconds;

	CG_UpdateHudScoreboardSummary();
	CG_UpdateHudScoreboardBanners();
}


/*
=============
CG_UpdateHudScoreboardSummary

Builds gametype-aware summary metadata for HUD menu scoreboxes.
=============
*/
static void CG_UpdateHudScoreboardSummary( void ) {
	const char		*summary;

	cgHudScoreboard.gametype = cgs.gametype;
	cgHudScoreboard.teamGame = (qboolean)( cgs.gametype >= GT_TEAM );
	cgHudScoreboard.redScore = 0;
	cgHudScoreboard.blueScore = 0;
	cgHudScoreboard.leadingTeam = TEAM_FREE;
	cgHudScoreboard.scoresTied = qfalse;
	summary = "Scoreboard";

	if ( cgHudScoreboard.teamGame ) {
		cgHudScoreboard.redScore = cg.teamScores[0];
		cgHudScoreboard.blueScore = cg.teamScores[1];
		if ( cgHudScoreboard.redScore == cgHudScoreboard.blueScore ) {
			cgHudScoreboard.scoresTied = qtrue;
			summary = va( "Teams are tied at %i", cgHudScoreboard.redScore );
		} else if ( cgHudScoreboard.redScore > cgHudScoreboard.blueScore ) {
			cgHudScoreboard.leadingTeam = TEAM_RED;
			summary = va( "Red leads %i to %i", cgHudScoreboard.redScore, cgHudScoreboard.blueScore );
		} else {
			cgHudScoreboard.leadingTeam = TEAM_BLUE;
			summary = va( "Blue leads %i to %i", cgHudScoreboard.blueScore, cgHudScoreboard.redScore );
		}
	} else if ( cg.snap && cg.snap->ps.persistant[PERS_TEAM] != TEAM_SPECTATOR ) {
		summary = va( "%s place with %i",
			CG_PlaceString( cg.snap->ps.persistant[PERS_RANK] + 1 ),
			cg.snap->ps.persistant[PERS_SCORE] );
	}

	Q_strncpyz( cgHudScoreboard.summary, summary, sizeof( cgHudScoreboard.summary ) );
}

/*
=============
CG_UpdateHudScoreboardBanners

Refreshes overtime and sudden-death banner state for menu consumers.
=============
*/
static void CG_UpdateHudScoreboardBanners( void ) {
	const char			*respawnSuffix;
	const char			*delaySuffix;

	cgHudScoreboard.overtimeVisible = (qboolean)( cgHudScoreboard.overtimeConfigured || cgHudScoreboard.overtimeActive );
	cgHudScoreboard.suddenDeathVisible = (qboolean)( cgHudScoreboard.suddenDeathConfigured || cgHudScoreboard.suddenDeathActive );

	cgHudScoreboard.overtimeLabel[0] = '\0';
	cgHudScoreboard.suddenDeathLabel[0] = '\0';

	if ( cgHudScoreboard.overtimeVisible ) {
		if ( cgHudScoreboard.overtimeCount > 0 ) {
			Com_sprintf( cgHudScoreboard.overtimeLabel, sizeof( cgHudScoreboard.overtimeLabel ),
				"Overtime x%i", cgHudScoreboard.overtimeCount );
		} else {
			Q_strncpyz( cgHudScoreboard.overtimeLabel, "Overtime", sizeof( cgHudScoreboard.overtimeLabel ) );
		}
	}

	if ( cgHudScoreboard.suddenDeathVisible ) {
		respawnSuffix = cgHudScoreboard.suddenDeathRespawns ? " +respawn" : "";
		delaySuffix = cgHudScoreboard.suddenDeathDelayActive ? " +delay" : "";
		Com_sprintf( cgHudScoreboard.suddenDeathLabel, sizeof( cgHudScoreboard.suddenDeathLabel ),
			"Sudden Death%s%s", respawnSuffix, delaySuffix );
	}
}

/*
=============
CG_HudScoreboardContainsClient

Checks if the cached HUD scoreboard already contains the supplied client.
=============
*/
static qboolean CG_HudScoreboardContainsClient( int clientNum ) {
	int		i;

	for ( i = 0; i < cgHudScoreboard.count; i++ ) {
		if ( cgHudScoreboard.entries[i].clientNum == clientNum ) {
			return qtrue;
		}
	}

	return qfalse;
}

/*
=============
CG_AppendHudScoreboardEntry

Caches a scoreboard row for the menu-driven HUD overlays.
=============
*/
static void CG_AppendHudScoreboardEntry( const score_t *score, const clientInfo_t *ci ) {
	cgHudScoreboardEntry_t	*entry;

	if ( !score || !ci || cgHudScoreboard.count >= MAX_CLIENTS ) {
		return;
	}

	if ( CG_HudScoreboardContainsClient( score->client ) ) {
		return;
	}

	entry = &cgHudScoreboard.entries[cgHudScoreboard.count++];
	entry->clientNum = score->client;
	entry->score = score->score;
	entry->ping = score->ping;
	entry->time = CG_ScoreboardTimeSeconds( score );
	entry->team = ci->team;
	entry->spectator = ( ci->team == TEAM_SPECTATOR );
	entry->localPlayer = ( cg.snap && score->client == cg.snap->ps.clientNum );

	if ( ci->team >= TEAM_FREE && ci->team < TEAM_NUM_TEAMS ) {
		cgHudScoreboard.teamCounts[ci->team]++;
	}
}

/*
=============
CG_BuildHudScoreboard

Seeds the Quake Live HUD scoreboard cache without invoking the legacy renderer.
=============
*/
void CG_BuildHudScoreboard( void ) {
	int			i;
	qboolean			timersActive;

	timersActive = (qboolean)( cgs.itemTimersEnabled || cgs.forceHudHints );

	CG_ResetHudScoreboard( timersActive );

	for ( i = 0; i < cg.numScores; i++ ) {
		score_t			*score;
		clientInfo_t	*ci;

		score = &cg.scores[i];
		if ( score->client < 0 || score->client >= cgs.maxclients ) {
			continue;
		}

		ci = &cgs.clientinfo[score->client];
		if ( !ci->infoValid ) {
			continue;
		}

		CG_AppendHudScoreboardEntry( score, ci );
	}
}


/*
=============
CG_TouchCompetitiveScores

Requests updated score data to populate Quake Live HUD ownerdraws.
=============
*/
void CG_TouchCompetitiveScores( void ) {
	if ( !cg.competitiveHudLoaded ) {
		return;
	}

	if ( cg.scoresRequestTime + 2000 < cg.time ) {
		cg.scoresRequestTime = cg.time;
		trap_SendClientCommand( "score" );
	}
}

/*
=============
CG_DamagePlumPresetDescription

Provides a human-readable label for the cached damage-plum preset.
=============
*/
static const char *CG_DamagePlumPresetDescription( void ) {
	switch ( cg.damagePlumPreset ) {
	case DAMAGE_PLUM_PRESET_ALL_WEAPONS:
		return "All weapons";
	case DAMAGE_PLUM_PRESET_AOE_WEAPONS:
		return "AoE weapons";
	case DAMAGE_PLUM_PRESET_CUSTOM:
		return "Custom list";
	default:
		return "Off";
	}
}

/*
=============
CG_DamagePlumStyleDescription

Returns the label for the selected damage-plum color style.
=============
*/
static const char *CG_DamagePlumStyleDescription( void ) {
	switch ( CG_GetDamagePlumColorStyle() ) {
	case DAMAGE_PLUM_COLOR_STYLE_DAMAGE:
		return "Damage colors";
	case DAMAGE_PLUM_COLOR_STYLE_WEAPON:
		return "Weapon colors";
	default:
		return "1-color fade";
	}
}


/*
=============
CG_DrawForcedScoreboardTip

Draws the forced compact-scoreboard banner when the server enforces it.
=============
*/
static int CG_DrawForcedScoreboardTip( float fade, int lineOffset ) {
	vec4_t	color;
	const char	*message;
	int	width;
	int	x;
	int	y;

	if ( !cgs.forceSmallScoreboardMessage || fade <= 0.0f ) {
		return lineOffset;
	}
	message = "Compact scoreboard message forced by server";
	width = CG_DrawStrlen( message ) * SMALLCHAR_WIDTH;
	x = ( SCREEN_WIDTH - width ) / 2;
	y = SB_TOP - ( lineOffset * SMALLCHAR_HEIGHT ) - 4;

	color[0] = 1.0f;
	color[1] = 1.0f;
	color[2] = 1.0f;
	color[3] = fade;

	CG_DrawSmallStringColor( x, y, message, color );

	return lineOffset + 1;
}

/*
=============
CG_DrawForcedGametypeHint

Displays the gametype training hint when the server forces HUD widgets.
=============
*/
static int CG_DrawForcedGametypeHint( float fade, int lineOffset ) {
	const char		*hint;
	vec4_t	color;
	int	width;
	int	x;
	int	y;

	if ( !cgs.forceHudHints || fade <= 0.0f ) {
		return lineOffset;
	}

	if ( cgs.gametype < 0 || cgs.gametype >= GT_MAX_GAME_TYPE ) {
		return lineOffset;
	}

	hint = QL_GametypeHudHint( cgs.gametype );
	if ( !hint || !*hint ) {
		return lineOffset;
	}

	color[0] = 1.0f;
	color[1] = 1.0f;
	color[2] = 1.0f;
	color[3] = fade;

	width = CG_DrawStrlen( hint ) * SMALLCHAR_WIDTH;
	y = SB_TOP - ( lineOffset * SMALLCHAR_HEIGHT ) - 4;
	x = ( SCREEN_WIDTH - width ) / 2;

	CG_DrawSmallStringColor( x, y, hint, color );

	return lineOffset + 1;
}

/*
=============
CG_DrawFreezeTagTips

Draws the Freeze Tag tutorial tips when forced HUD hints are active.
=============
*/
static int CG_DrawFreezeTagTips( float fade, int lineOffset ) {
	const char	*tip;
	vec4_t	color;
	int	width;
	int	x;
	int	y;
	int	i;
	const char *tips[] = {
		cgs.freezeTipObjective,
		cgs.freezeTipThaw,
		cgs.freezeTipFreeze,
		cgs.freezeTipShoot,
		cgs.freezeTipSummary
	};

	if ( !cgs.forceHudHints || fade <= 0.0f ) {
		return lineOffset;
	}

	if ( cgs.gametype != GT_FREEZE ) {
		return lineOffset;
	}

	color[0] = 1.0f;
	color[1] = 1.0f;
	color[2] = 1.0f;
	color[3] = fade;

	for ( i = 0; i < (int)( sizeof( tips ) / sizeof( tips[0] ) ); i++ ) {
		tip = tips[i];
		if ( !tip || !*tip ) {
			continue;
		}

		width = CG_DrawStrlen( tip ) * SMALLCHAR_WIDTH;
		x = ( SCREEN_WIDTH - width ) / 2;
		y = SB_TOP - ( lineOffset * SMALLCHAR_HEIGHT ) - 4;
		CG_DrawSmallStringColor( x, y, tip, color );
		lineOffset++;
	}

	return lineOffset;
}


/*
=================
CG_DrawFactoryMetadata

Renders the active match factory metadata sourced from configstrings.
=================
*/
static void CG_DrawFactoryMetadata( float fade ) {
	vec4_t	color;
	char	hints[MAX_STRING_CHARS];
	char	line[MAX_STRING_CHARS];
	int	x;
	int	y;
	int	timeoutCount;
	int	timeoutLength;
	int	overtimeLength;
	qboolean	sdEnabled;
	int	sdStart;
	int	sdTick;
	int	sdMax;
	int	sdInc;
	qboolean	sdPrint;
	qboolean	sdDelay;

	if ( fade <= 0.0f ) {
		return;
	}

	if ( !cgs.factoryTitle[0] && !cgs.factorySpawnHints[0] && cgs.factoryFlags == 0u ) {
		return;
	}

	color[0] = 1.0f;
	color[1] = 1.0f;
	color[2] = 1.0f;
	color[3] = fade;

	x = 8;
	y = 72;

	if ( cgs.factoryTitle[0] ) {
		CG_DrawSmallStringColor( x, y, cgs.factoryTitle, color );
		y += SMALLCHAR_HEIGHT;
	} else if ( cgs.factoryFlags == 0u ) {
		CG_DrawSmallStringColor( x, y, "Standard factory", color );
		y += SMALLCHAR_HEIGHT;
	}

	if ( cgs.factoryFlags != 0u ) {
		CG_DrawSmallStringColor( x, y, "Custom factory settings active", color );
		y += SMALLCHAR_HEIGHT;
	}

	if ( CG_DamagePlumsEnabled() ) {
		const char		*presetDesc;
		const char		*styleDesc;

		presetDesc = CG_DamagePlumPresetDescription();
		styleDesc = CG_DamagePlumStyleDescription();
		Com_sprintf( line, sizeof( line ), "Damage numbers: %s (%s)", presetDesc, styleDesc );
		CG_DrawSmallStringColor( x, y, line, color );
		y += SMALLCHAR_HEIGHT;
	} else {
		CG_DrawSmallStringColor( x, y, "Damage numbers: Off", color );
		y += SMALLCHAR_HEIGHT;
	}

	if ( !cgs.factorySpawnHints[0] ) {
		return;
	}

	Q_strncpyz( hints, cgs.factorySpawnHints, sizeof( hints ) );
	timeoutCount = atoi( Info_ValueForKey( hints, "toCount" ) );
	timeoutLength = atoi( Info_ValueForKey( hints, "toLength" ) );
	overtimeLength = atoi( Info_ValueForKey( hints, "otLength" ) );
	sdEnabled = atoi( Info_ValueForKey( hints, "sd" ) ) ? qtrue : qfalse;
	sdStart = atoi( Info_ValueForKey( hints, "sdStart" ) );
	sdTick = atoi( Info_ValueForKey( hints, "sdTick" ) );
	sdMax = atoi( Info_ValueForKey( hints, "sdMax" ) );
	sdInc = atoi( Info_ValueForKey( hints, "sdInc" ) );
	sdPrint = atoi( Info_ValueForKey( hints, "sdPrint" ) ) ? qtrue : qfalse;
	sdDelay = atoi( Info_ValueForKey( hints, "sdDelay" ) ) ? qtrue : qfalse;

	if ( timeoutCount > 0 && timeoutLength > 0 ) {
		Com_sprintf( line, sizeof( line ), "Timeouts: %ix%is", timeoutCount, timeoutLength );
	} else {
		Q_strncpyz( line, "Timeouts: disabled", sizeof( line ) );
	}
	if ( overtimeLength > 0 ) {
		char extra[64];
		Com_sprintf( extra, sizeof( extra ), "  Overtime: %is", overtimeLength );
		Q_strcat( line, sizeof( line ), extra );
	} else {
		Q_strcat( line, sizeof( line ), "  Overtime: disabled" );
	}
	CG_DrawSmallStringColor( x, y, line, color );
	y += SMALLCHAR_HEIGHT;

	if ( sdEnabled ) {
		Com_sprintf( line, sizeof( line ), "Sudden death: on (start %is tick %is max %is +%is%s%s)",
			sdStart,
			sdTick,
			sdMax,
			sdInc,
			sdDelay ? " delay" : "",
			sdPrint ? "" : " silent" );
	} else {
		Q_strncpyz( line, "Sudden death: off", sizeof( line ) );
	}
	CG_DrawSmallStringColor( x, y, line, color );
}


/*
=============
CG_FormatScoreboardTime

Formats a time value into the mm:ss string used on the scoreboard.
=============
*/
static void CG_FormatScoreboardTime( int timeSeconds, char *buffer, int bufferSize ) {
	int		minutes;
	int		seconds;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	if ( timeSeconds < 0 ) {
		timeSeconds = 0;
	}

	minutes = timeSeconds / 60;
	seconds = timeSeconds % 60;

	Com_sprintf( buffer, bufferSize, "%i:%02i", minutes, seconds );
}

/*
=============
CG_ClientRaceTimeSeconds

Returns the race timer in seconds for the supplied client when available.
=============
*/
static int CG_ClientRaceTimeSeconds( int clientNum ) {
	const cgRaceClientStatus_t	*status;
	int							elapsed;

	if ( cgs.gametype != GT_SINGLE_PLAYER ) {
		return -1;
	}

	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return -1;
	}

	status = &cgs.raceStatus[clientNum];
	if ( !status->initialized ) {
		return -1;
	}

	if ( status->currentElapsed >= 0 ) {
		elapsed = status->currentElapsed;
	} else if ( status->lastTime >= 0 ) {
		elapsed = status->lastTime;
	} else if ( status->bestTime >= 0 ) {
		elapsed = status->bestTime;
	} else {
		return -1;
	}

	if ( elapsed < 0 ) {
		elapsed = 0;
	}

	return ( elapsed + 500 ) / 1000;
}

/*
=============
CG_ScoreboardTimeSeconds

Determines which timer value to display for the provided scoreboard entry.
=============
*/
static int CG_ScoreboardTimeSeconds( const score_t *score ) {
	int		raceTime;
	int		timeValue;

	if ( !score ) {
		return 0;
	}

	raceTime = CG_ClientRaceTimeSeconds( score->client );
	if ( raceTime >= 0 ) {
		return raceTime;
	}

	timeValue = score->time;
	if ( timeValue <= 0 ) {
		timeValue = CG_GetScoreboardTimerSeconds();
	}

	return timeValue;
}

/*
=================
CG_DrawClientScore

Draws a single client row in the scoreboard.
=================
*/
static void CG_DrawClientScore( int y, score_t *score, float *color, float fade, qboolean largeFormat, qboolean timersActive ) {
	char	string[1024];
	vec3_t	headAngles;
	clientInfo_t	*ci;
	int iconx, headx;
	int timeValue;
	char	timeString[16];

	if ( score->client < 0 || score->client >= cgs.maxclients ) {
		Com_Printf( "Bad score->client: %i\n", score->client );
		return;
	}
	
	ci = &cgs.clientinfo[score->client];

	iconx = SB_BOTICON_X + (SB_RATING_WIDTH / 2);
	headx = SB_HEAD_X + (SB_RATING_WIDTH / 2);

	// draw the handicap or bot skill marker (unless player has flag)
	if ( ci->powerups & ( 1 << PW_NEUTRALFLAG ) ) {
		if( largeFormat ) {
			CG_DrawFlagModel( iconx, y - ( 32 - BIGCHAR_HEIGHT ) / 2, 32, 32, TEAM_FREE, qfalse );
		}
		else {
			CG_DrawFlagModel( iconx, y, 16, 16, TEAM_FREE, qfalse );
		}
	} else if ( ci->powerups & ( 1 << PW_REDFLAG ) ) {
		if( largeFormat ) {
			CG_DrawFlagModel( iconx, y - ( 32 - BIGCHAR_HEIGHT ) / 2, 32, 32, TEAM_RED, qfalse );
		}
		else {
			CG_DrawFlagModel( iconx, y, 16, 16, TEAM_RED, qfalse );
		}
	} else if ( ci->powerups & ( 1 << PW_BLUEFLAG ) ) {
		if( largeFormat ) {
			CG_DrawFlagModel( iconx, y - ( 32 - BIGCHAR_HEIGHT ) / 2, 32, 32, TEAM_BLUE, qfalse );
		}
		else {
			CG_DrawFlagModel( iconx, y, 16, 16, TEAM_BLUE, qfalse );
		}
	} else {
		if ( ci->botSkill > 0 && ci->botSkill <= 5 ) {
			if ( cg_drawIcons.integer ) {
				if( largeFormat ) {
					CG_DrawPic( iconx, y - ( 32 - BIGCHAR_HEIGHT ) / 2, 32, 32, cgs.media.botSkillShaders[ ci->botSkill - 1 ] );
				}
				else {
					CG_DrawPic( iconx, y, 16, 16, cgs.media.botSkillShaders[ ci->botSkill - 1 ] );
				}
			}
		} else if ( ci->handicap < 100 ) {
			Com_sprintf( string, sizeof( string ), "%i", ci->handicap );
			if ( cgs.gametype == GT_TOURNAMENT )
				CG_DrawSmallStringColor( iconx, y - SMALLCHAR_HEIGHT/2, string, color );
			else
				CG_DrawSmallStringColor( iconx, y, string, color );
		}

		// draw the wins / losses
		if ( cgs.gametype == GT_TOURNAMENT ) {
			Com_sprintf( string, sizeof( string ), "%i/%i", ci->wins, ci->losses );
			if( ci->handicap < 100 && !ci->botSkill ) {
				CG_DrawSmallStringColor( iconx, y + SMALLCHAR_HEIGHT/2, string, color );
			}
			else {
				CG_DrawSmallStringColor( iconx, y, string, color );
			}
		}
	}

	// draw the face
	VectorClear( headAngles );
	headAngles[YAW] = 180;
	if( largeFormat ) {
		CG_DrawHead( headx, y - ( ICON_SIZE - BIGCHAR_HEIGHT ) / 2, ICON_SIZE, ICON_SIZE, 
			score->client, headAngles );
	}
	else {
		CG_DrawHead( headx, y, 16, 16, score->client, headAngles );
	}

	// draw the team task
	if ( ci->teamTask != TEAMTASK_NONE ) {
		if ( ci->teamTask == TEAMTASK_OFFENSE ) {
			CG_DrawPic( headx + 48, y, 16, 16, cgs.media.assaultShader );
		}
		else if ( ci->teamTask == TEAMTASK_DEFENSE ) {
			CG_DrawPic( headx + 48, y, 16, 16, cgs.media.defendShader );
		}
	}
	// draw the score line
	timeValue = CG_ScoreboardTimeSeconds( score );
	if ( timersActive ) {
		CG_FormatScoreboardTime( timeValue, timeString, sizeof( timeString ) );
	} else {
		timeString[0] = '\0';
	}

	if ( score->ping == -1 ) {
		if ( timersActive ) {
			Com_sprintf( string, sizeof( string ),
				" connecting    %s", ci->name );
		} else {
			Com_sprintf( string, sizeof( string ),
				" connecting %s", ci->name );
		}
	} else if ( timersActive ) {
		if ( ci->team == TEAM_SPECTATOR ) {
			Com_sprintf( string, sizeof( string ),
				" SPECT %3i %7s %s", score->ping, timeString, ci->name );
		} else {
			Com_sprintf( string, sizeof( string ),
				"%5i %4i %7s %s", score->score, score->ping, timeString, ci->name );
		}
	} else {
		if ( ci->team == TEAM_SPECTATOR ) {
			Com_sprintf( string, sizeof( string ),
				" SPECT %3i %s", score->ping, ci->name );
		} else {
			Com_sprintf( string, sizeof( string ),
				"%5i %4i %s", score->score, score->ping, ci->name );
		}
	}

	// highlight your position
	if ( score->client == cg.snap->ps.clientNum ) {
		float	hcolor[4];
		int		rank;

		localClient = qtrue;

		if ( cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR 
			|| cgs.gametype >= GT_TEAM ) {
			rank = -1;
		} else {
			rank = cg.snap->ps.persistant[PERS_RANK] & ~RANK_TIED_FLAG;
		}
		if ( rank == 0 ) {
			hcolor[0] = 0;
			hcolor[1] = 0;
			hcolor[2] = 0.7f;
		} else if ( rank == 1 ) {
			hcolor[0] = 0.7f;
			hcolor[1] = 0;
			hcolor[2] = 0;
		} else if ( rank == 2 ) {
			hcolor[0] = 0.7f;
			hcolor[1] = 0.7f;
			hcolor[2] = 0;
		} else {
			hcolor[0] = 0.7f;
			hcolor[1] = 0.7f;
			hcolor[2] = 0.7f;
		}

		hcolor[3] = fade * 0.7;
		CG_FillRect( SB_SCORELINE_X + BIGCHAR_WIDTH + (SB_RATING_WIDTH / 2), y, 
			640 - SB_SCORELINE_X - BIGCHAR_WIDTH, BIGCHAR_HEIGHT+1, hcolor );
	}

	CG_DrawBigString( SB_SCORELINE_X + (SB_RATING_WIDTH / 2), y, string, fade );

	// add the "ready" marker for intermission exiting
	if ( cg.snap->ps.stats[ STAT_CLIENTS_READY ] & ( 1 << score->client ) ) {
		CG_DrawBigStringColor( iconx, y, "READY", color );
	}
}

/*
=============
CG_TeamScoreboard

Renders the scoreboard rows for a specific team or grouping.
=============
*/
static int CG_TeamScoreboard( int y, team_t team, float fade, int maxClients, int lineHeight, qboolean timersActive ) {
	int		i;
	score_t	*score;
	float	color[4];
	int		count;
	clientInfo_t	*ci;

	color[0] = color[1] = color[2] = 1.0;
	color[3] = fade;

	count = 0;
	for ( i = 0 ; i < cg.numScores && count < maxClients ; i++ ) {
		score = &cg.scores[i];
		ci = &cgs.clientinfo[ score->client ];

		if ( team != ci->team ) {
			continue;
		}

		CG_DrawClientScore( y + lineHeight * count, score, color, fade, lineHeight >= SB_NORMAL_HEIGHT, timersActive );

		count++;
	}

	return count;
}

/*
=================
CG_DrawScoreboard

Draw the normal in-game scoreboard
=================
*/
qboolean CG_DrawOldScoreboard( void ) {
	int		x, y, w, i, n1, n2;
	float	fade;
	float	*fadeColor;
	char	*s;
	int maxClients;
	int lineHeight;
	int topBorderSize, bottomBorderSize;
	int			nameHeaderX;
	qboolean		timersActive;
	int			lineOffset;

	// don't draw amuthing if the menu or console is up
	if ( cg_paused.integer ) {
		cg.deferredPlayerLoading = 0;
		return qfalse;
	}

	if ( cg.competitiveHudLoaded ) {
		return qfalse;
	}

	if ( cgs.gametype == GT_SINGLE_PLAYER && cg.predictedPlayerState.pm_type == PM_INTERMISSION ) {
		cg.deferredPlayerLoading = 0;
		return qfalse;
	}

	// don't draw scoreboard during death while warmup up
	if ( cg.warmup && !cg.showScores ) {
		return qfalse;
	}

	if ( cg.showScores || cg.predictedPlayerState.pm_type == PM_DEAD ||
		 cg.predictedPlayerState.pm_type == PM_INTERMISSION ) {
		fade = 1.0;
		fadeColor = colorWhite;
	} else {
		fadeColor = CG_FadeColor( cg.scoreFadeTime, FADE_TIME );
		
		if ( !fadeColor ) {
			// next time scoreboard comes up, don't print killer
			cg.deferredPlayerLoading = 0;
			cg.killerName[0] = 0;
			return qfalse;
		}
		fade = *fadeColor;
	}


	// fragged by ... line
	if ( cg.killerName[0] ) {
		s = va("Fragged by %s", cg.killerName );
		w = CG_DrawStrlen( s ) * BIGCHAR_WIDTH;
		x = ( SCREEN_WIDTH - w ) / 2;
		y = 40;
		CG_DrawBigString( x, y, s, fade );
	}

	// current rank
	if ( cgs.gametype < GT_TEAM) {
		if (cg.snap->ps.persistant[PERS_TEAM] != TEAM_SPECTATOR ) {
			s = va("%s place with %i",
				CG_PlaceString( cg.snap->ps.persistant[PERS_RANK] + 1 ),
				cg.snap->ps.persistant[PERS_SCORE] );
			w = CG_DrawStrlen( s ) * BIGCHAR_WIDTH;
			x = ( SCREEN_WIDTH - w ) / 2;
			y = 60;
			CG_DrawBigString( x, y, s, fade );
		}
	} else {
		if ( cg.teamScores[0] == cg.teamScores[1] ) {
			s = va("Teams are tied at %i", cg.teamScores[0] );
		} else if ( cg.teamScores[0] >= cg.teamScores[1] ) {
			s = va("Red leads %i to %i",cg.teamScores[0], cg.teamScores[1] );
		} else {
			s = va("Blue leads %i to %i",cg.teamScores[1], cg.teamScores[0] );
		}

		w = CG_DrawStrlen( s ) * BIGCHAR_WIDTH;
		x = ( SCREEN_WIDTH - w ) / 2;
		y = 60;
		CG_DrawBigString( x, y, s, fade );
	}
	CG_DrawFactoryMetadata( fade );

	// scoreboard
	y = SB_HEADER;

	timersActive = ( cgs.itemTimersEnabled || cgs.forceHudHints );

	CG_DrawPic( SB_SCORE_X + (SB_RATING_WIDTH / 2), y, 64, 32, cgs.media.scoreboardScore );
	CG_DrawPic( SB_PING_X - (SB_RATING_WIDTH / 2), y, 64, 32, cgs.media.scoreboardPing );
	if ( timersActive ) {
		CG_DrawPic( SB_TIME_X - (SB_RATING_WIDTH / 2), y, 64, 32, cgs.media.scoreboardTime );
	}
	nameHeaderX = SB_SCORELINE_X + (SB_RATING_WIDTH / 2) + ( timersActive ? 16 : 11 ) * BIGCHAR_WIDTH;
	CG_DrawPic( nameHeaderX, y, 64, 32, cgs.media.scoreboardName );

	lineOffset = 1;
	lineOffset = CG_DrawForcedScoreboardTip( fade, lineOffset );
	lineOffset = CG_DrawForcedGametypeHint( fade, lineOffset );
	lineOffset = CG_DrawFreezeTagTips( fade, lineOffset );

	y = SB_TOP;

	// If there are more than the configured number of slots, use the interleaved scores
	{
		int		configuredHeight;
		int		interHeight;
		int		availableHeight;
		int		normalMaxClients;
		int		interMaxClients;

		configuredHeight = cgs.itemTimerHeight;
		if ( configuredHeight <= 0 ) {
			configuredHeight = SB_NORMAL_HEIGHT;
		} else if ( configuredHeight > ITEM_TIMER_MAX_HEIGHT ) {
			configuredHeight = ITEM_TIMER_MAX_HEIGHT;
		}
		if ( configuredHeight < SB_INTER_HEIGHT ) {
			configuredHeight = SB_INTER_HEIGHT;
		}

		interHeight = configuredHeight / 2;
		if ( interHeight < SB_INTER_HEIGHT ) {
			interHeight = SB_INTER_HEIGHT;
		}

		availableHeight = SB_STATUSBAR - SB_TOP;
		normalMaxClients = availableHeight / configuredHeight;
		if ( normalMaxClients <= 0 ) {
			normalMaxClients = 1;
		}

		interMaxClients = availableHeight / interHeight - 1;
		if ( interMaxClients <= 0 ) {
			interMaxClients = 1;
		}

		if ( cg.numScores > normalMaxClients ) {
			maxClients = interMaxClients;
			lineHeight = interHeight;
			topBorderSize = 8;
			bottomBorderSize = 16;
		} else {
			maxClients = normalMaxClients;
			lineHeight = configuredHeight;
			topBorderSize = 16;
			bottomBorderSize = 16;
		}
	}


	localClient = qfalse;

	if ( cgs.gametype >= GT_TEAM ) {
		//
		// teamplay scoreboard
		//
		y += lineHeight/2;

		if ( cg.teamScores[0] >= cg.teamScores[1] ) {
			n1 = CG_TeamScoreboard( y, TEAM_RED, fade, maxClients, lineHeight, timersActive );
			CG_DrawTeamBackground( 0, y - topBorderSize, 640, n1 * lineHeight + bottomBorderSize, 0.33f, TEAM_RED );
			y += (n1 * lineHeight) + BIGCHAR_HEIGHT;
			maxClients -= n1;
			n2 = CG_TeamScoreboard( y, TEAM_BLUE, fade, maxClients, lineHeight, timersActive );
			CG_DrawTeamBackground( 0, y - topBorderSize, 640, n2 * lineHeight + bottomBorderSize, 0.33f, TEAM_BLUE );
			y += (n2 * lineHeight) + BIGCHAR_HEIGHT;
			maxClients -= n2;
		} else {
			n1 = CG_TeamScoreboard( y, TEAM_BLUE, fade, maxClients, lineHeight, timersActive );
			CG_DrawTeamBackground( 0, y - topBorderSize, 640, n1 * lineHeight + bottomBorderSize, 0.33f, TEAM_BLUE );
			y += (n1 * lineHeight) + BIGCHAR_HEIGHT;
			maxClients -= n1;
			n2 = CG_TeamScoreboard( y, TEAM_RED, fade, maxClients, lineHeight, timersActive );
			CG_DrawTeamBackground( 0, y - topBorderSize, 640, n2 * lineHeight + bottomBorderSize, 0.33f, TEAM_RED );
			y += (n2 * lineHeight) + BIGCHAR_HEIGHT;
			maxClients -= n2;
		}
		n1 = CG_TeamScoreboard( y, TEAM_SPECTATOR, fade, maxClients, lineHeight, timersActive );
		y += (n1 * lineHeight) + BIGCHAR_HEIGHT;

	} else {
		//
		// free for all scoreboard
		//
		n1 = CG_TeamScoreboard( y, TEAM_FREE, fade, maxClients, lineHeight, timersActive );
		y += (n1 * lineHeight) + BIGCHAR_HEIGHT;
		n2 = CG_TeamScoreboard( y, TEAM_SPECTATOR, fade, maxClients - n1, lineHeight, timersActive );
		y += (n2 * lineHeight) + BIGCHAR_HEIGHT;
	}

	if (!localClient) {
		// draw local client at the bottom
		for ( i = 0 ; i < cg.numScores ; i++ ) {
			if ( cg.scores[i].client == cg.snap->ps.clientNum ) {
				CG_DrawClientScore( y, &cg.scores[i], fadeColor, fade, lineHeight >= SB_NORMAL_HEIGHT, timersActive );
				break;
			}
		}
	}

	// load any models that have been deferred
	if ( ++cg.deferredPlayerLoading > 10 ) {
		CG_LoadDeferredPlayers();
	}

	return qtrue;
}

//================================================================================

/*
================
CG_CenterGiantLine
================
*/
static void CG_CenterGiantLine( float y, const char *string ) {
	float		x;
	vec4_t		color;

	color[0] = 1;
	color[1] = 1;
	color[2] = 1;
	color[3] = 1;

	x = 0.5 * ( 640 - GIANT_WIDTH * CG_DrawStrlen( string ) );

	CG_DrawStringExt( x, y, string, color, qtrue, qtrue, GIANT_WIDTH, GIANT_HEIGHT, 0 );
}

/*
=================
CG_DrawTourneyScoreboard

Draw the oversize scoreboard for tournements
=================
*/
void CG_DrawOldTourneyScoreboard( void ) {
	const char		*s;
	vec4_t			color;
	int				min, tens, ones;
	clientInfo_t	*ci;
	int				y;
	int				i;

	// request more scores regularly
	if ( cg.scoresRequestTime + 2000 < cg.time ) {
		cg.scoresRequestTime = cg.time;
		trap_SendClientCommand( "score" );
	}

	color[0] = 1;
	color[1] = 1;
	color[2] = 1;
	color[3] = 1;

	// draw the dialog background
	color[0] = color[1] = color[2] = 0;
	color[3] = 1;
	CG_FillRect( 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, color );

	// print the mesage of the day
	s = CG_ConfigString( CS_MOTD );
	if ( !s[0] ) {
		s = "Scoreboard";
	}

	// print optional title
	CG_CenterGiantLine( 8, s );

	// print server time
	ones = cg.time / 1000;
	min = ones / 60;
	ones %= 60;
	tens = ones / 10;
	ones %= 10;
	s = va("%i:%i%i", min, tens, ones );

	CG_CenterGiantLine( 64, s );


	// print the two scores

	y = 160;
	if ( cgs.gametype >= GT_TEAM ) {
		//
		// teamplay scoreboard
		//
		CG_DrawStringExt( 8, y, "Red Team", color, qtrue, qtrue, GIANT_WIDTH, GIANT_HEIGHT, 0 );
		s = va("%i", cg.teamScores[0] );
		CG_DrawStringExt( 632 - GIANT_WIDTH * strlen(s), y, s, color, qtrue, qtrue, GIANT_WIDTH, GIANT_HEIGHT, 0 );
		
		y += 64;

		CG_DrawStringExt( 8, y, "Blue Team", color, qtrue, qtrue, GIANT_WIDTH, GIANT_HEIGHT, 0 );
		s = va("%i", cg.teamScores[1] );
		CG_DrawStringExt( 632 - GIANT_WIDTH * strlen(s), y, s, color, qtrue, qtrue, GIANT_WIDTH, GIANT_HEIGHT, 0 );
	} else {
		//
		// free for all scoreboard
		//
		for ( i = 0 ; i < MAX_CLIENTS ; i++ ) {
			ci = &cgs.clientinfo[i];
			if ( !ci->infoValid ) {
				continue;
			}
			if ( ci->team != TEAM_FREE ) {
				continue;
			}

			CG_DrawStringExt( 8, y, ci->name, color, qtrue, qtrue, GIANT_WIDTH, GIANT_HEIGHT, 0 );
			s = va("%i", ci->score );
			CG_DrawStringExt( 632 - GIANT_WIDTH * strlen(s), y, s, color, qtrue, qtrue, GIANT_WIDTH, GIANT_HEIGHT, 0 );
			y += 64;
		}
	}


}

/*
=============
CG_GetHudScoreboard

Returns the cached HUD scoreboard data for menu rendering.
=============
*/
const cgHudScoreboard_t *CG_GetHudScoreboard( void ) {
	return &cgHudScoreboard;
}

/*
=============
CG_GetHudScoreboardEntry

Returns a cached HUD scoreboard entry for listbox owner-draws.
=============
*/
const cgHudScoreboardEntry_t *CG_GetHudScoreboardEntry( int index, team_t team ) {
	int		i;
	int		filteredIndex;

	if ( index < 0 ) {
		return NULL;
	}

	if ( team >= TEAM_FREE && team < TEAM_NUM_TEAMS ) {
		filteredIndex = 0;
		for ( i = 0; i < cgHudScoreboard.count; i++ ) {
			if ( cgHudScoreboard.entries[i].team != team ) {
				continue;
			}

			if ( filteredIndex == index ) {
				return &cgHudScoreboard.entries[i];
			}

			filteredIndex++;
		}

		return NULL;
	}

	if ( index >= cgHudScoreboard.count ) {
		return NULL;
	}

	return &cgHudScoreboard.entries[index];
}

/*
=============
CG_GetHudScoreboardTeamCount

Returns the number of cached HUD scoreboard rows for a specific team.
=============
*/
int CG_GetHudScoreboardTeamCount( team_t team ) {
	if ( team >= TEAM_FREE && team < TEAM_NUM_TEAMS ) {
		return cgHudScoreboard.teamCounts[team];
	}

	return cgHudScoreboard.count;
}
