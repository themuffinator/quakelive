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
static void CG_DrawForcedScoreboardTip( float fade ) {
	vec4_t	color;
	const char	*message;
	int	width;
	int	x;
	int	y;

	if ( !cgs.forceSmallScoreboardMessage || fade <= 0.0f ) {
		return;
	}
	message = "Compact scoreboard message forced by server";
	width = CG_DrawStrlen( message ) * SMALLCHAR_WIDTH;
	x = ( SCREEN_WIDTH - width ) / 2;
	y = SB_TOP - SMALLCHAR_HEIGHT - 4;

	color[0] = 1.0f;
	color[1] = 1.0f;
	color[2] = 1.0f;
	color[3] = fade;

	CG_DrawSmallStringColor( x, y, message, color );
}

/*
=============
CG_DrawForcedGametypeHint

Displays the gametype training hint when the server forces HUD widgets.
=============
*/
static void CG_DrawForcedGametypeHint( float fade ) {
	const char		*hint;
	vec4_t	color;
	int	width;
	int	x;
	int	y;
	int	lineOffset;

	if ( !cgs.forceHudHints || fade <= 0.0f ) {
		return;
	}

	if ( cgs.gametype < 0 || cgs.gametype >= GT_MAX_GAME_TYPE ) {
		return;
	}

	hint = QL_GametypeHudHint( cgs.gametype );
	if ( !hint || !*hint ) {
		return;
	}

	color[0] = 1.0f;
	color[1] = 1.0f;
	color[2] = 1.0f;
	color[3] = fade;

	width = CG_DrawStrlen( hint ) * SMALLCHAR_WIDTH;
	lineOffset = cgs.forceSmallScoreboardMessage ? 2 : 1;
	y = SB_TOP - ( lineOffset * SMALLCHAR_HEIGHT ) - 4;
	x = ( SCREEN_WIDTH - width ) / 2;

	CG_DrawSmallStringColor( x, y, hint, color );
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
				" SPECT %3i %4i %s", score->ping, score->time, ci->name );
		} else {
			Com_sprintf( string, sizeof( string ),
				"%5i %4i %4i %s", score->score, score->ping, score->time, ci->name );
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

	// don't draw amuthing if the menu or console is up
	if ( cg_paused.integer ) {
		cg.deferredPlayerLoading = 0;
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

	CG_DrawForcedScoreboardTip( fade );
	CG_DrawForcedGametypeHint( fade );

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

