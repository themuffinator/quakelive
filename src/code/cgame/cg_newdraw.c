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
#include "../../game/match_state_keys.h"
#include "../ui/ui_shared.h"

extern displayContextDef_t cgDC;

#define CG_ARENA_LOOKUP_TEXT_SIZE		( 128 * 1024 )
#define CG_ARENA_LOOKUP_FILE_LIST_SIZE		8192

typedef enum cgVoteSlotField_e {
	CG_VOTE_FIELD_GAMETYPE,
	CG_VOTE_FIELD_MAP,
	CG_VOTE_FIELD_NAME,
	CG_VOTE_FIELD_COUNT
	} cgVoteSlotField_t;

typedef struct cgStartingWeaponInfo_s {
	const char *token;
	weapon_t weapon;
} cgStartingWeaponInfo_t;

typedef struct cgServerSettingsWeaponIcon_s {
	unsigned int bit;
	weapon_t weapon;
} cgServerSettingsWeaponIcon_t;

//
// Forward declarations for HUD ownerdraw helpers used by Quake Live menus.
//
static const char *CG_ResolveWeaponName( int weapon );
static void CG_ParseActiveVoteCommand( char *command, size_t commandSize, char *argument, size_t argumentSize );
static void CG_DrawVoteShot(rectDef_t *rect, int slot);
static void CG_AlignTextX( float *x, const char *text, float scale, int align );
static float CG_AlignTextInRectX( const rectDef_t *rect, float scale, const char *text, int align );
static void CG_Text_Paint_LimitExt( float *maxX, float x, float y, float scale, vec4_t color, const char *text, float adjust, int limit, int fontIndex );
static void CG_Text_Paint_Limit( float *maxX, float x, float y, float scale, vec4_t color, const char *text, float adjust, int limit );
static qboolean CG_ShowPlayersRemaining( void );

void Menus_HandleOOBClick( menuDef_t *menu, int key, qboolean down );
int Menu_ItemsMatchingGroup( menuDef_t *menu, const char *name );
itemDef_t *Menu_GetMatchingItemByNumber( menuDef_t *menu, int index, const char *name );
itemDef_t *Menu_FindItemByName( menuDef_t *menu, const char *p );
itemDef_t *Menu_ClearFocus( menuDef_t *menu );
qboolean Rect_ContainsPoint( rectDef_t *rect, float x, float y );
void Item_ValidateTypeData( itemDef_t *item );
void Window_Paint( Window *w, float fadeAmount, float fadeClamp, float fadeCycle );
void Item_Paint( itemDef_t *item );
void Item_SetMouseOver( itemDef_t *item, qboolean focus );
void Item_RunScript( itemDef_t *item, const char *s );
qboolean Item_EnableShowViaCvar( itemDef_t *item, int flag );
qboolean Item_HandleKey( itemDef_t *item, int key, qboolean down );
int Item_ListBox_MaxScroll( itemDef_t *item );
int Item_ListBox_ThumbPosition( itemDef_t *item );
int Item_ListBox_ThumbDrawPosition( itemDef_t *item );
int Item_ListBox_OverLB( itemDef_t *item, float x, float y );
qboolean Item_ListBox_HandleKey( itemDef_t *item, int key, qboolean down, qboolean force );
void Item_ListBox_MouseEnter( itemDef_t *item, float x, float y );
qboolean Item_TextField_HandleKey( itemDef_t *item, int key );
qboolean Item_YesNo_HandleKey( itemDef_t *item, int key );
int Item_Multi_FindCvarByValue( itemDef_t *item );
const char *Item_Multi_Setting( itemDef_t *item );
qboolean Item_Multi_HandleKey( itemDef_t *item, int key );
const char *Item_PresetList_Setting( itemDef_t *item );
int Item_PresetList_FindCvarByValue( itemDef_t *item );
qboolean Item_PresetList_HandleKey( itemDef_t *item, int key );
void Controls_GetConfig( void );
void Controls_SetConfig( qboolean restart );
int BindingIDFromName( const char *name );
void BindingFromName( const char *cvar );
float Item_Slider_ThumbPosition( itemDef_t *item );
int Item_Slider_OverSlider( itemDef_t *item, float x, float y );
qboolean Item_Slider_HandleKey( itemDef_t *item, int key, qboolean down );
void Item_StartCapture( itemDef_t *item, int key );
qboolean Display_KeyBindPending( void );
void Item_TextColor( itemDef_t *item, vec4_t *newColor );
void Item_SetTextExtents( itemDef_t *item, int *width, int *height, const char *text );
void Item_Text_AutoWrapped_Paint( itemDef_t *item );
void Item_Text_Wrapped_Paint( itemDef_t *item );
void Item_Text_Paint( itemDef_t *item );
void Item_TextField_Paint( itemDef_t *item );
void Item_YesNo_Paint( itemDef_t *item );
void Item_Multi_Paint( itemDef_t *item );
void Item_PresetList_Paint( itemDef_t *item );
void Item_Slider_Paint( itemDef_t *item );
void Item_SliderColor_Paint( itemDef_t *item );
void Item_Bind_Paint( itemDef_t *item );
qboolean Item_Bind_HandleKey( itemDef_t *item, int key, qboolean down );
void Item_Model_Paint( itemDef_t *item );
void Item_ListBox_Paint( itemDef_t *item );
void Menu_FadeItemByName( menuDef_t *menu, const char *p, qboolean fadeOut );
void Menu_TransitionItemByName( menuDef_t *menu, const char *p, rectDef_t rectFrom, rectDef_t rectTo, int time, float amt );
void Menu_OrbitItemByName( menuDef_t *menu, const char *p, float x, float y, float cx, float cy, int time );
void Menus_Activate( menuDef_t *menu );
void Script_SetColor( itemDef_t *item, char **args );
void Script_SetBackground( itemDef_t *item, char **args );
void Script_SetTeamColor( itemDef_t *item, char **args );
void Script_SetItemColor( itemDef_t *item, char **args );
void Script_SetPlayerModel( itemDef_t *item, char **args );
void Script_SetPlayerHead( itemDef_t *item, char **args );
void Script_SetCvar( itemDef_t *item, char **args );
void Script_Exec( itemDef_t *item, char **args );
void Script_Play( itemDef_t *item, char **args );
void Script_playLooped( itemDef_t *item, char **args );
static void *CG_ClearBrowserFocus( void *overlay );

#define CG_RACE_CHECKPOINT_HALF_WIDTH 24.0f
#define CG_RACE_CHECKPOINT_HEIGHT 48.0f
#define CG_SPECTATOR_TRACK_TIMEOUT 5000

#define CG_STARTING_WEAPON_ICON_COUNT 14
#define CG_SCORE_FORFEIT -999

static const cgStartingWeaponInfo_t cgStartingWeaponIcons[CG_STARTING_WEAPON_ICON_COUNT] = {
	{ "g", WP_GAUNTLET },
	{ "mg", WP_MACHINEGUN },
	{ "sg", WP_SHOTGUN },
	{ "gl", WP_GRENADE_LAUNCHER },
	{ "rl", WP_ROCKET_LAUNCHER },
	{ "lg", WP_LIGHTNING },
	{ "rg", WP_RAILGUN },
	{ "pg", WP_PLASMAGUN },
	{ "bfg", WP_BFG },
	{ "gh", WP_GRAPPLING_HOOK },
	{ "ng", WP_NAILGUN },
	{ "pl", WP_PROX_LAUNCHER },
	{ "cg", WP_CHAINGUN },
	{ "hmg", WP_HEAVY_MACHINEGUN }
};

static const cgServerSettingsWeaponIcon_t cgServerSettingsWeaponIcons[] = {
	{ CUSTOM_SETTING_GAUNTLET, WP_GAUNTLET },
	{ CUSTOM_SETTING_MACHINEGUN, WP_MACHINEGUN },
	{ CUSTOM_SETTING_SHOTGUN, WP_SHOTGUN },
	{ CUSTOM_SETTING_GRENADE_LAUNCHER, WP_GRENADE_LAUNCHER },
	{ CUSTOM_SETTING_ROCKET_LAUNCHER, WP_ROCKET_LAUNCHER },
	{ CUSTOM_SETTING_LIGHTNING_GUN, WP_LIGHTNING },
	{ CUSTOM_SETTING_RAILGUN, WP_RAILGUN },
	{ CUSTOM_SETTING_PLASMAGUN, WP_PLASMAGUN },
	{ CUSTOM_SETTING_BFG, WP_BFG },
	{ CUSTOM_SETTING_GRAPPLING_HOOK, WP_GRAPPLING_HOOK },
	{ CUSTOM_SETTING_NAILGUN, WP_NAILGUN },
	{ CUSTOM_SETTING_PROX_LAUNCHER, WP_PROX_LAUNCHER },
	{ CUSTOM_SETTING_CHAINGUN, WP_CHAINGUN }
};

static qhandle_t cgGameTypeIconShaders[GT_MAX_GAME_TYPE];

static const char *cgMonthAbbrev[12] = {
	"Jan", "Feb", "Mar",
	"Apr", "May", "Jun",
	"Jul", "Aug", "Sep",
	"Oct", "Nov", "Dec"
};

/*
=============
CG_PluralSuffix

Returns the plural suffix used by retail endgame summary strings.
=============
*/
static const char *CG_PluralSuffix( int count ) {
	return ( count == 1 ) ? "" : "s";
}

/*
=============
CG_FormatMinutesSeconds

Formats a whole-second clock value into the retail `m:ss` ownerdraw string.
=============
*/
static const char *CG_FormatMinutesSeconds( int seconds ) {
	if ( seconds < 0 ) {
		seconds = 0;
	}

	return va( "%i:%i%i", seconds / 60, ( seconds % 60 ) / 10, seconds % 10 );
}

/*
=============
CG_GetRoundTimeLimitSeconds

Reads the retail roundtimelimit value directly from serverinfo.
=============
*/
static int CG_GetRoundTimeLimitSeconds( void ) {
	const char	*info;
	const char	*value;
	int		seconds;

	info = CG_ConfigString( CS_SERVERINFO );
	if ( !info || !*info ) {
		return 0;
	}

	value = Info_ValueForKey( info, SERVERINFO_KEY_ROUNDTIMELIMIT );
	if ( !value || !*value ) {
		return 0;
	}

	seconds = atoi( value );
	if ( seconds < 0 ) {
		return 0;
	}

	return seconds;
}

/*
=============
CG_FormatSignedWholeSeconds

Formats a signed millisecond delta into the retail coarse `[-]Ns` string.
=============
*/
static const char *CG_FormatSignedWholeSeconds( int milliseconds ) {
	unsigned int	absoluteMilliseconds;
	const char	*signPrefix;
	int		wholeSeconds;

	signPrefix = "";
	absoluteMilliseconds = (unsigned int)milliseconds;

	if ( milliseconds < 0 ) {
		signPrefix = "-";
		absoluteMilliseconds = (unsigned int)( -( milliseconds + 1 ) ) + 1u;
	}

	wholeSeconds = (int)( ( absoluteMilliseconds + 500u ) / 1000u );
	if ( wholeSeconds < 1 ) {
		wholeSeconds = 1;
	}

	return va( "%s%1.0fs", signPrefix, (double)wholeSeconds );
}

/*
=============
CG_FormatSignedMilliseconds

Formats a signed millisecond delta into the retail `[-]m:ss.mmm` string.
=============
*/
static const char *CG_FormatSignedMilliseconds( int milliseconds ) {
	unsigned int	absoluteMilliseconds;
	const char	*signPrefix;
	const char	*secondPrefix;
	int		minutes;
	float		seconds;

	signPrefix = "";
	absoluteMilliseconds = (unsigned int)milliseconds;
	if ( milliseconds < 0 ) {
		signPrefix = "-";
		absoluteMilliseconds = (unsigned int)( -( milliseconds + 1 ) ) + 1u;
	}

	minutes = absoluteMilliseconds / 60000u;
	seconds = ( absoluteMilliseconds % 60000u ) / 1000.0f;
	secondPrefix = ( seconds < 10.0f ) ? "0" : "";

	return va( "%s%d:%s%.03f", signPrefix, minutes, secondPrefix, seconds );
}

static void CG_DrawServerSettings(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle);
static void CG_DrawStartingWeapons(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle);
static void CG_DrawGameLimit( rectDef_t *rect, float scale, vec4_t color, int textStyle, int align );
static void CG_DrawGameTypeIcon(rectDef_t *rect);
static void CG_DrawGameTypeMap( rectDef_t *rect, float scale, vec4_t color, int textStyle, int align );
static void CG_DrawGameType( rectDef_t *rect, float scale, vec4_t color, int textStyle, int align );
static void CG_DrawMatchDetails( rectDef_t *rect, float scale, vec4_t color, int textStyle );
static void CG_DrawMatchEndCondition( rectDef_t *rect, float scale, vec4_t color, int textStyle );
static void CG_DrawMatchStatus( rectDef_t *rect, float scale, vec4_t color, int textStyle, int align );
static void CG_DrawRoundLabel( rectDef_t *rect, float scale, vec4_t color, int textStyle, int align );
static void CG_DrawLocalTime(rectDef_t *rect, float scale, vec4_t color, int textStyle, int align);
static void CG_DrawVoteGametype(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot);
static void CG_DrawVoteName(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot);
static void CG_DrawVoteMapSlot(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot);
static void CG_DrawVoteCount(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot, int align);
static void CG_DrawVoteTimer(rectDef_t *rect, float scale, vec4_t color, int textStyle, int align);
static void CG_DrawScoreboxFollowBackground(rectDef_t *rect, qhandle_t shader, vec4_t color);
static void CG_DrawScoreboxSpecBackground(rectDef_t *rect, qhandle_t shader, vec4_t color);
static void CG_DrawRoundBackground(rectDef_t *rect, qhandle_t shader, vec4_t color);
static void CG_DrawOvertimeBackground(rectDef_t *rect, qhandle_t shader, vec4_t color);
static void CG_TranslateHudRectForWidescreen(const rectDef_t *rect, rectDef_t *translated);
static void CG_UpdateSpectatorTargets( void );
static qboolean CG_LoadoutsEnabled( void );

extern int trap_RealTime( qtime_t *qtime );

#ifndef Vector4Set
#define Vector4Set(v,a,b,c,d) do { (v)[0]=(a); (v)[1]=(b); (v)[2]=(c); (v)[3]=(d); } while (0)
#endif

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
CG_RaceResetRunState

Clears the cached current-run Race HUD state while optionally preserving the
recorded best and last times.
=============
*/
void CG_RaceResetRunState( qboolean clearRecordedTimes ) {
	int i;

	memset( cgs.raceProgress, 0, sizeof( cgs.raceProgress ) );
	cgs.raceInfoActive = qfalse;
	cgs.raceInfoStartTime = 0;
	cgs.raceInfoCheckpointCount = 0;
	cgs.raceInfoCurrentCheckpointEntityNum = -1;
	cgs.raceInfoNextCheckpointEntityNum = -1;
	for ( i = 0; i < MAX_CLIENTS; ++i ) {
		cgs.raceProgress[i].currentCheckpoint = -1;
	}

	if ( clearRecordedTimes ) {
		memset( cgs.raceStatus, 0, sizeof( cgs.raceStatus ) );
		memset( cgs.raceLeaderSplits, 0, sizeof( cgs.raceLeaderSplits ) );
		cgs.raceInfoLastTime = -1;
		cgs.raceLeaderSplitCount = 0;
		cgs.raceStatusSequence = 0;
		cgs.raceLeaderClientNum = -1;
	}
}

/*
=============
CG_RaceResetState

Clears cached Race HUD state so configstrings can repopulate it.
=============
*/
void CG_RaceResetState( void ) {
	CG_RaceResetRunState( qtrue );

	if ( cgs.gametype == GT_RACE ) {
		trap_SendClientCommand( "raceinit" );
	}
}

/*
=============
CG_RaceBeepSoundForCvar

Maps cg_raceBeep's 1-8 selector onto the retail impact/bell cue bank.
=============
*/
static sfxHandle_t CG_RaceBeepSoundForCvar( void ) {
	switch ( cg_raceBeep.integer ) {
	case 2:
		return cgs.media.killBeepSound2;
	case 3:
		return cgs.media.killBeepSound3;
	case 4:
		return cgs.media.killBeepSound4;
	case 5:
		return cgs.media.killBeepSound5;
	case 6:
		return cgs.media.killBeepSound6;
	case 7:
		return cgs.media.killBeepSound7;
	case 8:
		return cgs.media.killBeepSound8;
	default:
		return cgs.media.killBeepSound1;
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

	switch ( cue ) {
	case CG_RACE_CUE_START:
	case CG_RACE_CUE_CHECKPOINT:
		if ( cg_raceBeep.integer <= 0 ) {
			return;
		}
		sfx = CG_RaceBeepSoundForCvar();
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
	if ( !cg.snap ) {
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

Emits the checkpoint centerprint; CG_RacePlayCue handles the audio cue.
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

	CG_CenterPrint( va( "Checkpoint\n%s", statusText ), SCREEN_HEIGHT * 0.30f, 0.3f );
}

/*
=============
CG_RaceApplyObservedFollowProgress

Uses the retail Race temp-entity and race_info payload instead of origin
prediction while tracking the active local or followed runner.
=============
*/
static qboolean CG_RaceApplyObservedFollowProgress( int clientNum, cgRaceClientProgress_t *progress ) {
	if ( !progress || !cg.snap ) {
		return qfalse;
	}

	if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {
		if ( clientNum != cg.spectatorFollowClient ) {
			return qfalse;
		}
	} else {
		if ( cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR || clientNum != cg.clientNum ) {
			return qfalse;
		}
	}

	progress->initialized = qtrue;
	progress->runActive = cgs.raceInfoActive;
	if ( cgs.raceInfoActive ) {
		progress->currentCheckpoint = cgs.raceInfoCheckpointCount;
		if ( progress->currentCheckpoint < 0 ) {
			progress->currentCheckpoint = 0;
		}
	} else if ( cgs.raceInfoLastTime >= 0 && cgs.racePointCount > 0 ) {
		progress->currentCheckpoint = cgs.racePointCount - 1;
	} else {
		progress->currentCheckpoint = -1;
	}

	return qtrue;
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

	if ( CG_RaceApplyObservedFollowProgress( clientNum, progress ) ) {
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
	int	index;
	int	currentElapsed;

	if ( !progress || !deltaOut ) {
		return qfalse;
	}

	currentElapsed = -1;
	if ( cgs.raceInfoActive && cgs.raceInfoStartTime > 0 ) {
		currentElapsed = cg.time - cgs.raceInfoStartTime;
	} else if ( status && status->currentElapsed >= 0 ) {
		currentElapsed = status->currentElapsed;
	}

	if ( !progress->runActive || currentElapsed < 0 ) {
		return qfalse;
	}
	index = progress->currentCheckpoint;
	if ( index <= 0 || index >= cgs.raceLeaderSplitCount ) {
		return qfalse;
	}
	*deltaOut = currentElapsed - cgs.raceLeaderSplits[index];
	return qtrue;
}

/*
=============
CG_RaceBuildRespawnPrompt

Builds the retail race respawn prompt when the local player is dead.
=============
*/
static qboolean CG_RaceBuildRespawnPrompt( char *buffer, size_t bufferSize ) {
	char	keyName[32];
	int		key;

	if ( !buffer || bufferSize <= 0 || !cg.snap ) {
		return qfalse;
	}

	if ( cg.snap->ps.pm_type == PM_INTERMISSION ) {
		return qfalse;
	}

	if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {
		return qfalse;
	}

	if ( cg.snap->ps.stats[STAT_HEALTH] > 0 ) {
		return qfalse;
	}

	key = trap_Key_GetKey( "kill" );
	if ( key == -1 ) {
		Q_strncpyz( buffer, "Bind 'kill' to respawn", bufferSize );
		return qtrue;
	}

	if ( cg.killRespawnHintSuppressed ) {
		return qfalse;
	}

	trap_Key_KeynumToStringBuf( key, keyName, sizeof( keyName ) );
	Q_strupr( keyName );
	Com_sprintf( buffer, bufferSize, "Press %s to respawn.", keyName );

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
	if ( CG_RaceBuildRespawnPrompt( buffer, bufferSize ) ) {
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
	int		currentElapsed;
	int		lastTime;

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

	currentElapsed = -1;
	if ( cgs.raceInfoActive && cgs.raceInfoStartTime > 0 ) {
		currentElapsed = cg.time - cgs.raceInfoStartTime;
	} else if ( status && status->currentElapsed >= 0 ) {
		currentElapsed = status->currentElapsed;
	}
	lastTime = ( cgs.raceInfoLastTime >= 0 ) ? cgs.raceInfoLastTime : -1;
	if ( lastTime < 0 && status && status->lastTime >= 0 ) {
		lastTime = status->lastTime;
	}

	if ( primary && primarySize > 0 ) {
		if ( currentElapsed >= 0 ) {
			int delta;
			char timeBuffer[32];
			CG_RaceFormatMilliseconds( currentElapsed, timeBuffer, sizeof( timeBuffer ) );
			Com_sprintf( primary, primarySize, "Cur %s", timeBuffer );
			if ( CG_RaceCheckpointDelta( status, progress, &delta ) ) {
				char deltaText[32];
				char extra[32];
				CG_RaceFormatDelta( delta, deltaText, sizeof( deltaText ) );
				Com_sprintf( extra, sizeof( extra ), "  d%s", deltaText );
				Q_strcat( primary, primarySize, extra );
			}
		} else if ( lastTime >= 0 ) {
			char timeBuffer[32];
			CG_RaceFormatMilliseconds( lastTime, timeBuffer, sizeof( timeBuffer ) );
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
CG_DrawRaceStatusAndTimes

Retail shared race ownerdraw leaf for both status and timing widgets.
=============
*/
static void CG_DrawRaceStatusAndTimes( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	const char	*text;
	char primary[64];
	char secondary[64];
	float	lineHeight;

	if ( ownerDraw == CG_RACE_STATUS ) {
		text = CG_GetRaceStatusText();
		if ( !text[0] ) {
			return;
		}

		CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, text, 0, 0, textStyle );
		return;
	}

	if ( ownerDraw != CG_RACE_TIMES ) {
		return;
	}

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

/*
=============
CG_GetScoreForClientNum

Returns the score entry for the requested client.
=============
*/
static const score_t *CG_GetScoreForClientNum( int clientNum ) {
	int i;

	if ( clientNum < 0 || clientNum >= cgs.maxclients || clientNum >= MAX_CLIENTS ) {
		return NULL;
	}

	for ( i = 0; i < cg.numScores; i++ ) {
		if ( cg.scores[i].client == clientNum ) {
			return &cg.scores[i];
		}
	}

	return NULL;
}

/*
=============
CG_BuildSpectatorClientOrder

Builds a sorted list of follow targets for the spectator HUD.
=============
*/
static void CG_BuildSpectatorClientOrder( void ) {
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

/*
=============
CG_UpdateSpectatorTargets

Refreshes the tracked spectator targets used by follow UI.
=============
*/
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

	if ( cg.snap->ps.persistant[PERS_TEAM] != TEAM_SPECTATOR &&
				!( cg.snap->ps.pm_flags & PMF_FOLLOW ) &&
				cg.snap->ps.pm_type != PM_SPECTATOR ) {
		cg.spectatorCameraLocked = qfalse;
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

/*
=============
CG_SpectatorClientInfo

Returns the client info for a tracked spectator slot.
=============
*/
static const clientInfo_t *CG_SpectatorClientInfo( int slot ) {
	int clientNum = -1;

	if ( slot == 0 ) {
		clientNum = cg.spectatorPrimaryClient;
	} else if ( slot == 1 ) {
		clientNum = cg.spectatorSecondaryClient;
	}

	if ( clientNum < 0 || clientNum >= cgs.maxclients || clientNum >= MAX_CLIENTS ) {
		return NULL;
	}

	if ( !cgs.clientinfo[clientNum].infoValid ) {
		return NULL;
	}

	return &cgs.clientinfo[clientNum];
}

/*
=============
CG_SpectatorClientScore

Returns the score entry for a tracked spectator slot.
=============
*/
static const score_t *CG_SpectatorClientScore( int slot ) {
	int clientNum = -1;

	if ( slot == 0 ) {
		clientNum = cg.spectatorPrimaryClient;
	} else if ( slot == 1 ) {
		clientNum = cg.spectatorSecondaryClient;
	}

	if ( clientNum < 0 || clientNum >= cgs.maxclients || clientNum >= MAX_CLIENTS ) {
		return NULL;
	}

	return CG_GetScoreForClientNum( clientNum );
}

/*
=============
CG_SpectatorSlotFollowed

Checks if the requested spectator slot is actively followed.
=============
*/
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
	int trackedTime = 0;

	if ( slot == 0 ) {
		clientNum = cg.spectatorPrimaryClient;
		trackedTime = cg.spectatorSlotTrackedTime[0];
	} else if ( slot == 1 ) {
		clientNum = cg.spectatorSecondaryClient;
		trackedTime = cg.spectatorSlotTrackedTime[1];
	}

	if ( clientNum < 0 ) {
		return qfalse;
	}

	if ( trackedTime > cg.time ) {
		return qtrue;
	}

	return ( clientNum == cg.spectatorTrackedClient );
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
	if ( cg.demoPlayback ) {
		return qfalse;
	}
	if ( !CG_IsSpectatorCamera() ) {
		return qfalse;
	}
	if ( cg_followPowerup.integer <= 0 ) {
		return qfalse;
	}

	return ( trackType == CG_SPECTATOR_TRACK_FLAG || trackType == CG_SPECTATOR_TRACK_POWERUP );
}

/*
=============
CG_TryAutoFollowPowerup

Mirrors the retail auto-follow command shape for powerup and flag-track events.
=============
*/
static void CG_TryAutoFollowPowerup( int clientNum, cgSpectatorTrackType_t trackType ) {
	const char	*suffix;

	if ( !CG_ShouldAutoFollowTrack( trackType ) ) {
		return;
	}
	if ( cg.spectatorCameraLocked ) {
		return;
	}

	suffix = "";
	if ( cg_followPowerup.integer == 2 && trackType == CG_SPECTATOR_TRACK_POWERUP ) {
		suffix = " pw";
	}

	trap_SendClientCommand( va( "follow %d%s", clientNum, suffix ) );
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
CG_SetSpectatorCameraLock

Enables or disables the spectator camera lock flag.
=============
*/
void CG_SetSpectatorCameraLock( qboolean locked ) {
	cg.spectatorCameraLocked = locked ? qtrue : qfalse;

	if ( locked ) {
		if ( cg.snap && ( cg.snap->ps.pm_flags & PMF_FOLLOW ) ) {
			CG_SetTrackPlayerCvarValue( cg.snap->ps.clientNum );
		} else if ( cg.spectatorFollowClient >= 0 ) {
			CG_SetTrackPlayerCvarValue( cg.spectatorFollowClient );
		} else {
			CG_SetTrackPlayerCvarValue( cg.spectatorTrackedClient );
		}
	} else if ( cg.spectatorTrackedClient < 0 ) {
		CG_SetTrackPlayerCvarValue( -1 );
	}
}

/*
=============
CG_SpectatorFollowRequest

Attempts to follow the provided client while respecting camera lock state.
=============
*/
qboolean CG_SpectatorFollowRequest( int clientNum ) {
	if ( clientNum < 0 || clientNum >= cgs.maxclients ) {
		return qfalse;
	}
	if ( cg.spectatorCameraLocked && cg.spectatorFollowClient >= 0 && cg.spectatorFollowClient != clientNum ) {
		return qfalse;
	}
	if ( !cgs.clientinfo[clientNum].infoValid || cgs.clientinfo[clientNum].team == TEAM_SPECTATOR ) {
		return qfalse;
	}

	cg.spectatorTrackedClient = clientNum;
	CG_SetTrackPlayerCvarValue( clientNum );

	trap_SendClientCommand( va( "follow %d", clientNum ) );
	return qtrue;
}

/*
=============
CG_StopSpectatorFollow

Releases the spectator camera from any follow target and clears locks.
=============
*/
void CG_StopSpectatorFollow( void ) {
	trap_SendClientCommand( "follow" );
	cg.spectatorTrackedClient = -1;
	CG_SetTrackPlayerCvarValue( -1 );
	CG_SetSpectatorCameraLock( qfalse );
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

	CG_TryAutoFollowPowerup( clientNum, trackType );
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


/*
=============
CG_ArmorTierForArmor

Returns the inferred armor tier used by source-side spectator summaries.
=============
*/
static int CG_ArmorTierForArmor( int armor ) {
	if ( armor >= 150 ) {
		return 2;
	}
	if ( armor >= 100 ) {
		return 1;
	}
	if ( armor > 0 ) {
		return 0;
	}
	return -1;
}

/*
=============
CG_GetArmorTierColorForTier

Returns the retail armor-tier tint for the replicated tier value.
=============
*/
static void CG_GetArmorTierColorForTier( int tier, vec4_t color ) {
	switch ( tier ) {
	case 2:
		Vector4Set( color, 1.0f, 0.0f, 0.0f, 1.0f );
		break;
	case 1:
		Vector4Set( color, 1.0f, 1.0f, 0.0f, 1.0f );
		break;
	case 0:
		Vector4Set( color, 0.0f, 1.0f, 0.0f, 1.0f );
		break;
	default:
		Vector4Set( color, 0.4f, 0.4f, 0.4f, 0.6f );
		break;
	}
}

/*
=============
CG_GetArmorTierColor

Returns the armor color tier for HUD bars.
=============
*/
static void CG_GetArmorTierColor( int armor, vec4_t color ) {
	CG_GetArmorTierColorForTier( CG_ArmorTierForArmor( armor ), color );
}

/*
=============
CG_BarValueFraction

Returns a normalized percentage for a clamped value.
=============
*/
static float CG_BarValueFraction( int value, int maximum ) {
	if ( maximum <= 0 ) {
		return 0.0f;
	}

	return Com_Clamp( 0.0f, (float)maximum, (float)value ) / (float)maximum;
}

/*
=============
CG_DrawBarFill

Renders a left-clipped portion of the supplied shader using the specified color and ratio.
=============
*/
static void CG_DrawBarFill( const rectDef_t *rect, qhandle_t shader, float fraction, const vec4_t color ) {
	float x;
	float y;
	float w;
	float h;

	if ( !rect ) {
		return;
	}

	if ( fraction <= 0.0f || rect->w <= 0.0f || rect->h <= 0.0f ) {
		return;
	}

	if ( fraction > 1.0f ) {
		fraction = 1.0f;
	}

	if ( shader ) {
		x = rect->x;
		y = rect->y;
		w = rect->w * fraction;
		h = rect->h;
		CG_AdjustFrom640( &x, &y, &w, &h );
		trap_R_SetColor( color );
		trap_R_DrawStretchPic( x, y, w, h, 0.0f, 0.0f, fraction, 1.0f, shader );
		trap_R_SetColor( NULL );
	} else {
		CG_FillRect( rect->x, rect->y, rect->w * fraction, rect->h, color );
	}
}

/*
=============
CG_DrawBarFillFromRight

Renders a right-clipped portion of the supplied shader using the specified color and ratio.
=============
*/
static void CG_DrawBarFillFromRight( const rectDef_t *rect, qhandle_t shader, float fraction, const vec4_t color ) {
	float x;
	float y;
	float w;
	float h;
	float s1;

	if ( !rect ) {
		return;
	}

	if ( fraction <= 0.0f || rect->w <= 0.0f || rect->h <= 0.0f ) {
		return;
	}

	if ( fraction > 1.0f ) {
		fraction = 1.0f;
	}

	w = rect->w * fraction;
	x = rect->x + rect->w - w;

	if ( shader ) {
		y = rect->y;
		h = rect->h;
		s1 = 1.0f - fraction;
		CG_AdjustFrom640( &x, &y, &w, &h );
		trap_R_SetColor( color );
		trap_R_DrawStretchPic( x, y, w, h, s1, 0.0f, 1.0f, 1.0f, shader );
		trap_R_SetColor( NULL );
	} else {
		CG_FillRect( x, rect->y, w, rect->h, color );
	}
}

/*
=============
CG_DrawBarFillFromBottom

Renders a bottom-clipped portion of the supplied shader using the specified color and ratio.
=============
*/
static void CG_DrawBarFillFromBottom( const rectDef_t *rect, qhandle_t shader, float fraction, const vec4_t color ) {
	float x;
	float y;
	float w;
	float h;
	float t1;

	if ( !rect ) {
		return;
	}

	if ( fraction <= 0.0f || rect->w <= 0.0f || rect->h <= 0.0f ) {
		return;
	}

	if ( fraction > 1.0f ) {
		fraction = 1.0f;
	}

	h = rect->h * fraction;
	y = rect->y + rect->h - h;

	if ( shader ) {
		x = rect->x;
		w = rect->w;
		t1 = 1.0f - fraction;
		CG_AdjustFrom640( &x, &y, &w, &h );
		trap_R_SetColor( color );
		trap_R_DrawStretchPic( x, y, w, h, 0.0f, t1, 1.0f, 1.0f, shader );
		trap_R_SetColor( NULL );
	} else {
		CG_FillRect( rect->x, y, rect->w, h, color );
	}
}

/*
=============
CG_PlayerMaxHealth

Returns the local player's retail max-health split for primary and excess bar segments.
=============
*/
static int CG_PlayerMaxHealth( void ) {
	int maxHealth;

	maxHealth = cg.snap->ps.stats[STAT_MAX_HEALTH];
	if ( maxHealth <= 0 ) {
		maxHealth = 100;
	}

	return maxHealth;
}

/*
=============
CG_DrawPlayerHealthBar100

Draws the retail primary player health bar ownerdraw.
=============
*/
static void CG_DrawPlayerHealthBar100( rectDef_t *rect, qhandle_t shader ) {
	vec4_t barColor;
	float ratio;
	int health;
	int maxHealth;

	if ( !cg.snap ) {
		return;
	}

	health = cg.snap->ps.stats[STAT_HEALTH];
	maxHealth = CG_PlayerMaxHealth();
	Vector4Copy( CG_TeamColor( cg.snap->ps.persistant[PERS_TEAM] ), barColor );
	barColor[3] = 1.0f;
	ratio = CG_BarValueFraction( health, maxHealth );

	if ( !shader ) {
		shader = cgs.media.healthBar100;
	}

	CG_DrawBarFill( rect, shader, ratio, barColor );
}

/*
=============
CG_DrawPlayerHealthBar200

Draws the retail excess player health bar ownerdraw.
=============
*/
static void CG_DrawPlayerHealthBar200( rectDef_t *rect, qhandle_t shader ) {
	vec4_t barColor;
	float ratio;
	int health;
	int maxHealth;
	int excessHealth;

	if ( !cg.snap ) {
		return;
	}

	health = cg.snap->ps.stats[STAT_HEALTH];
	maxHealth = CG_PlayerMaxHealth();
	excessHealth = health - maxHealth;
	if ( excessHealth <= 0 ) {
		return;
	}

	Vector4Copy( CG_TeamColor( cg.snap->ps.persistant[PERS_TEAM] ), barColor );
	barColor[3] = 1.0f;
	ratio = CG_BarValueFraction( excessHealth, maxHealth );

	if ( !shader ) {
		shader = cgs.media.healthBar200;
	}

	CG_DrawBarFillFromBottom( rect, shader, ratio, barColor );
}

/*
=============
CG_DrawPlayerArmorBar100

Draws the retail primary player armor bar ownerdraw.
=============
*/
static void CG_DrawPlayerArmorBar100( rectDef_t *rect, qhandle_t shader ) {
	vec4_t barColor;
	float ratio;
	int armor;

	if ( !cg.snap ) {
		return;
	}

	armor = cg.snap->ps.stats[STAT_ARMOR];
	Vector4Copy( CG_TeamColor( cg.snap->ps.persistant[PERS_TEAM] ), barColor );
	barColor[3] = 1.0f;
	ratio = CG_BarValueFraction( armor, 100 );

	if ( !shader ) {
		shader = cgs.media.armorBar100;
	}

	CG_DrawBarFillFromRight( rect, shader, ratio, barColor );
}

/*
=============
CG_DrawPlayerArmorBar200

Draws the retail excess player armor bar ownerdraw.
=============
*/
static void CG_DrawPlayerArmorBar200( rectDef_t *rect, qhandle_t shader ) {
	vec4_t barColor;
	float ratio;
	int armor;
	int excessArmor;

	if ( !cg.snap ) {
		return;
	}

	armor = cg.snap->ps.stats[STAT_ARMOR];
	excessArmor = armor - 100;
	if ( excessArmor <= 0 ) {
		return;
	}

	Vector4Copy( CG_TeamColor( cg.snap->ps.persistant[PERS_TEAM] ), barColor );
	barColor[3] = 1.0f;
	ratio = CG_BarValueFraction( excessArmor, 100 );

	if ( !shader ) {
		shader = cgs.media.armorBar200;
	}

	CG_DrawBarFillFromBottom( rect, shader, ratio, barColor );
}

/*
=============
CG_GetRoundPlayerCountTeam

Resolves the team whose cached round count should be displayed.
=============
*/
static team_t CG_GetRoundPlayerCountTeam( qboolean friendly ) {
	team_t	team;

	team = (team_t)cg.predictedPlayerState.persistant[PERS_TEAM];
	if ( !friendly ) {
		if ( team == TEAM_RED ) {
			team = TEAM_BLUE;
		} else if ( team == TEAM_BLUE ) {
			team = TEAM_RED;
		}
	}

	if ( team != TEAM_RED && team != TEAM_BLUE ) {
		return TEAM_FREE;
	}

	return team;
}

/*
=============
CG_DrawPlayerCount

Draws the text for either the friendly or enemy player count widgets.
=============
*/
static void CG_DrawPlayerCount( rectDef_t *rect, float scale, vec4_t color, int textStyle, qboolean friendly ) {
	char	buffer[8];
	team_t	team;
	int		count;
	int		width;

	if ( !rect ) {
		return;
	}

	team = CG_GetRoundPlayerCountTeam( friendly );
	count = ( team == TEAM_RED || team == TEAM_BLUE ) ? cgs.matchTeamCount[team] : 0;
	Com_sprintf( buffer, sizeof( buffer ), "%i", count );
	width = CG_Text_Width( buffer, scale, 0 );
	CG_Text_Paint( rect->x + ( rect->w - width ) * 0.5f, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );
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

	if ( !rect || !CG_ShouldDrawSpeedometer() ) {
		return;
	}

	speed = CG_SampleSpeedometer();
	Com_sprintf(buffer, sizeof(buffer), "%i", (int)(speed + 0.5f));
	width = CG_Text_Width(buffer, scale, 0);
	CG_Text_Paint(rect->x + (rect->w - width) * 0.5f, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}

/*
=============
CG_DrawSpeedometerOwnerDraw

Retail split ownerdraw leaf for the speedometer slot.
=============
*/
static void CG_DrawSpeedometerOwnerDraw(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	CG_DrawSpeedometer( rect, scale, color, textStyle );
}

/*
=============
CG_SpectatorFollowCycle

Cycles the next/previous spectator target while respecting camera lock state.
=============
*/
void CG_SpectatorFollowCycle( int dir ) {
	int i;
	int index = -1;
	int newClient = -1;
	int baseClient = -1;

	CG_UpdateSpectatorTargets();

	if ( cg.spectatorClientCount <= 0 ) {
		return;
	}

	if ( cg.spectatorCameraLocked ) {
		baseClient = cg.spectatorTrackedClient;
	} else if ( cg.spectatorFollowClient >= 0 ) {
		baseClient = cg.spectatorFollowClient;
	} else {
		baseClient = cg.spectatorTrackedClient;
	}

	if ( baseClient < 0 ) {
		baseClient = cg.spectatorPrimaryClient;
	}

	for ( i = 0; i < cg.spectatorClientCount; i++ ) {
		if ( cg.spectatorClientOrder[i] == baseClient ) {
			index = i;
			break;
		}
	}

	if ( index == -1 ) {
		index = 0;
	}

	index = ( index + dir + cg.spectatorClientCount ) % cg.spectatorClientCount;
	newClient = cg.spectatorClientOrder[index];

	if ( cg.spectatorCameraLocked ) {
		if ( newClient != cg.spectatorTrackedClient ) {
			cg.spectatorTrackedClient = newClient;
			CG_SetTrackPlayerCvarValue( newClient );
		}
		return;
	}

	CG_SpectatorFollowRequest( newClient );
}

/*
=============
CG_BuildSpectatorPlayerNameText

Builds the retail cached spectator scorebox name and applies the fixed
scorebox truncation threshold.
=============
*/
static qboolean CG_BuildSpectatorPlayerNameText( int slot, float scale, char *nameBuffer, size_t nameBufferSize ) {
	char	truncated[40];
	int	len;

	if ( !nameBuffer || nameBufferSize == 0 ) {
		return qfalse;
	}

	if ( slot == 0 ) {
		Q_strncpyz( nameBuffer, cgs.firstPlaceName, nameBufferSize );
	} else if ( slot == 1 ) {
		Q_strncpyz( nameBuffer, cgs.secondPlaceName, nameBufferSize );
	} else {
		nameBuffer[0] = '\0';
		return qfalse;
	}

	if ( cgs.gametype == GT_TOURNAMENT && !nameBuffer[0] ) {
		Q_strncpyz( nameBuffer, "-", nameBufferSize );
	}

	if ( CG_Text_Width( nameBuffer, scale, 0 ) <= 140 ) {
		return qtrue;
	}

	Q_strncpyz( truncated, nameBuffer, sizeof( truncated ) );
	len = strlen( truncated );
	while ( len > 0 ) {
		truncated[len - 1] = '\0';
		len--;
		if ( CG_Text_Width( truncated, scale, 0 ) < 132 ) {
			break;
		}
	}

	Com_sprintf( nameBuffer, nameBufferSize, "%s...", truncated );
	return qtrue;
}

/*
=============
CG_DrawSpectatorPlayerName

Renders the cached retail first/second-player spectator scorebox name.
=============
*/
static void CG_DrawSpectatorPlayerName( rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot, int align ) {
	char	nameBuffer[40];
	float	x;

	if ( !rect || !CG_BuildSpectatorPlayerNameText( slot, scale, nameBuffer, sizeof( nameBuffer ) ) ) {
		return;
	}

	x = rect->x;
	CG_AlignTextX( &x, nameBuffer, scale, align );
	CG_Text_Paint( x, rect->y, scale, color, nameBuffer, 0, 0, textStyle );
}

/*
=============
CG_DrawSpectatorPlayerScore

Draws the cached retail first/second-player spectator score value.
=============
*/
static void CG_DrawSpectatorPlayerScore( rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot, int align ) {
	char	buffer[16];
	float	x;
	int	score;

	if ( !rect ) {
		return;
	}

	score = ( slot == 0 ) ? cgs.scores1 : cgs.scores2;
	if ( score == SCORE_NOT_PRESENT || score == CG_SCORE_FORFEIT ) {
		Q_strncpyz( buffer, "-", sizeof( buffer ) );
	} else {
		Com_sprintf( buffer, sizeof( buffer ), "%d", score );
	}

	x = rect->x;
	CG_AlignTextX( &x, buffer, scale, align );
	CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawSpectatorHealthArmor

Draws the tracked spectator health and armor summary bar.
=============
*/
static void CG_DrawSpectatorHealthArmor( rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot ) {
	const clientInfo_t *ci = CG_SpectatorClientInfo( slot );
	vec4_t healthColor;
	vec4_t armorColor;
	vec4_t baseColor = { 0.0f, 0.0f, 0.0f, 0.45f };
	char buffer[32];
	float healthWidth;
	float armorWidth;
	int health;
	int armor;

	if ( !rect || !ci ) {
		return;
	}

	if ( !cg_specDuelHealthArmor.integer ) {
		return;
	}

	(void)color;

	health = ci->health;
	armor = ci->armor;
	if ( health < 0 ) {
		health = 0;
	}
	if ( armor < 0 ) {
		armor = 0;
	}

	CG_GetColorForHealth( health, armor, healthColor );
	CG_GetArmorTierColor( armor, armorColor );
	if ( !cg_specDuelHealthColor.integer ) {
		healthColor[0] = 1.0f;
		healthColor[1] = 1.0f;
		healthColor[2] = 1.0f;
		armorColor[0] = 1.0f;
		armorColor[1] = 1.0f;
		armorColor[2] = 1.0f;
	}

	healthColor[3] = 0.85f;
	armorColor[3] = 0.7f;

	healthWidth = rect->w * Com_Clamp( 0.0f, 1.0f, (float)health / 200.0f );
	armorWidth = rect->w * Com_Clamp( 0.0f, 1.0f, (float)armor / 200.0f );

	CG_FillRect( rect->x, rect->y, rect->w, rect->h, baseColor );
	CG_FillRect( rect->x, rect->y, healthWidth, rect->h * 0.65f, healthColor );
	CG_FillRect( rect->x, rect->y + rect->h * 0.65f, armorWidth, rect->h * 0.35f, armorColor );

	{
		vec4_t textColor = { 1.0f, 1.0f, 1.0f, 1.0f };
		Com_sprintf( buffer, sizeof( buffer ), "%d / %d", health, armor );
		CG_Text_Paint( rect->x + 2, rect->y + rect->h - 2, scale, textColor, buffer, 0, 0, textStyle );
	}
}

/*
=============
CG_GetProfileFallbackShader

Resolves the shader used when a client icon is unavailable.
=============
*/
static qhandle_t CG_GetProfileFallbackShader( void ) {
	static qhandle_t fallback;

	if ( !fallback ) {
		fallback = trap_R_RegisterShaderNoMip( "ui/assets/hud/armor.tga" );
		if ( !fallback ) {
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

	if ( !rect || !cg_drawProfileImages.integer ) {
		return;
	}

	ci = CG_SpectatorClientInfo( slot );
	if ( !ci ) {
		return;
	}

	shader = ci->modelIcon;
	if ( !shader ) {
		shader = CG_GetProfileFallbackShader();
	}

	if ( !shader ) {
		return;
	}

	Vector4Set( modulate, 1.0f, 1.0f, 1.0f, CG_SpectatorSlotFollowed( slot ) ? 1.0f : 0.6f );
	trap_R_SetColor( modulate );
	CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );
	trap_R_SetColor( NULL );
}

/*
=============
CG_GetPlacementFlagShader

Resolves the retail-style flag icon shader for a tracked placement slot.
=============
*/
static qhandle_t CG_GetPlacementFlagShader( int slot ) {
	const clientInfo_t *ci;

	ci = CG_SpectatorClientInfo( slot );
	if ( !ci ) {
		return 0;
	}

	return ci->countryFlagShader ? ci->countryFlagShader : CG_RegisterCountryFlag( ci->country );
}

/*
=============
CG_DrawPlacementFlagOwnerDraw

Draws the retail placement flag icon for the requested scorebox slot.
=============
*/
static void CG_DrawPlacementFlagOwnerDraw( rectDef_t *rect, int slot ) {
	qhandle_t shader;

	if ( !rect ) {
		return;
	}

	shader = CG_GetPlacementFlagShader( slot );
	if ( !shader ) {
		return;
	}

	CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );
}

/*
=============
CG_DrawPlacementAvatarOwnerDraw

Routes the retail placement avatar ownerdraw through the tracked-profile
image helper.
=============
*/
static void CG_DrawPlacementAvatarOwnerDraw( rectDef_t *rect, int slot ) {
	CG_DrawSpectatorProfileImage( rect, slot );
}

/*
=============
CG_GetSpectatorOwnerDrawSlot

Maps spectator owner-draw identifiers to the backing slot index.
=============
*/
static int CG_GetSpectatorOwnerDrawSlot( int ownerDraw ) {
	switch ( ownerDraw ) {
	case CG_1ST_PLYR_HEALTH_ARMOR:
	case CG_SPEC_FOLLOW_PRIMARY:
	case CG_SPEC_COMPARE_PRIMARY:
		return 0;
	case CG_2ND_PLYR_HEALTH_ARMOR:
	case CG_SPEC_FOLLOW_SECONDARY:
	case CG_SPEC_COMPARE_SECONDARY:
		return 1;
	default:
		return -1;
	}
}

/*
=============
CG_DrawSpectatorFollowIndicator

Renders a follow or tracking marker for the requested spectator slot.
=============
*/
static void CG_DrawSpectatorFollowIndicator( rectDef_t *rect, int ownerDraw, qhandle_t shader, vec4_t color ) {
	vec4_t modulate;
	const clientInfo_t *ci;
	float x;
	float y;
	float w;
	float h;
	int slot;

	slot = CG_GetSpectatorOwnerDrawSlot( ownerDraw );
	if ( slot < 0 ) {
		return;
	}

	ci = CG_SpectatorClientInfo( slot );
	if ( !ci ) {
		return;
	}

	if ( !shader ) {
		shader = cgs.media.scoreboxFollowShader;
	}

	if ( !shader ) {
		return;
	}

	Vector4Copy( color, modulate );
	if ( modulate[3] <= 0.0f ) {
		modulate[3] = 1.0f;
	}

	if ( CG_SpectatorSlotFollowed( slot ) ) {
		modulate[3] *= 1.0f;
	} else if ( CG_SpectatorSlotTracked( slot ) ) {
		modulate[3] *= 0.65f;
	} else {
		modulate[3] *= 0.25f;
	}

	x = rect->x;
	y = rect->y;
	w = rect->w;
	h = rect->h;
	CG_AdjustFrom640( &x, &y, &w, &h );

	trap_R_SetColor( modulate );
	trap_R_DrawStretchPic( x, y, w, h, 0.0f, 0.0f, 1.0f, 1.0f, shader );
	trap_R_SetColor( NULL );
}

/*
=============
CG_DrawSpectatorComparison

Draws the health and armor comparison bar for a spectator slot.
=============
*/
static void CG_DrawSpectatorComparison( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	const clientInfo_t *ci;
	const clientInfo_t *other;
	vec4_t healthColor;
	vec4_t armorColor;
	vec4_t textColor;
	vec4_t markerColor = { 1.0f, 1.0f, 1.0f, 0.35f };
	vec4_t baseColor = { 0.0f, 0.0f, 0.0f, 0.45f };
	float healthWidth;
	float armorWidth;
	float markerX;
	int otherSlot;
	int health;
	int armor;
	int slot;
	char buffer[32];

	if ( !rect ) {
		return;
	}

	slot = CG_GetSpectatorOwnerDrawSlot( ownerDraw );
	if ( slot < 0 ) {
		return;
	}

	ci = CG_SpectatorClientInfo( slot );
	if ( !ci ) {
		return;
	}

	if ( !cg_specDuelHealthArmor.integer ) {
		return;
	}

	otherSlot = ( slot == 0 ) ? 1 : 0;
	other = CG_SpectatorClientInfo( otherSlot );

	health = ci->health;
	armor = ci->armor;
	if ( health < 0 ) {
		health = 0;
	}
	if ( armor < 0 ) {
		armor = 0;
	}

	CG_GetColorForHealth( health, armor, healthColor );
	CG_GetArmorTierColor( armor, armorColor );
	if ( !cg_specDuelHealthColor.integer ) {
		healthColor[0] = 1.0f;
		healthColor[1] = 1.0f;
		healthColor[2] = 1.0f;
		armorColor[0] = 1.0f;
		armorColor[1] = 1.0f;
		armorColor[2] = 1.0f;
	}

	healthColor[3] = 0.85f;
	armorColor[3] = 0.7f;

	CG_FillRect( rect->x, rect->y, rect->w, rect->h, baseColor );

	healthWidth = rect->w * Com_Clamp( 0.0f, 1.0f, (float)health / 200.0f );
	armorWidth = rect->w * Com_Clamp( 0.0f, 1.0f, (float)armor / 200.0f );

	CG_FillRect( rect->x, rect->y, healthWidth, rect->h * 0.65f, healthColor );
	CG_FillRect( rect->x, rect->y + rect->h * 0.65f, armorWidth, rect->h * 0.35f, armorColor );

	if ( other ) {
		float comparison;
		float otherComparison;

		comparison = Com_Clamp( 0.0f, 1.0f, (float)( health + armor ) / 400.0f );
		otherComparison = Com_Clamp( 0.0f, 1.0f, (float)( other->health + other->armor ) / 400.0f );

		markerX = rect->x + rect->w * otherComparison - 1.0f;
		CG_FillRect( markerX, rect->y, 2.0f, rect->h, markerColor );

		if ( comparison > otherComparison && markerColor[3] < 0.6f ) {
			markerColor[3] = 0.6f;
		}
	}

	Vector4Copy( color, textColor );
	if ( textColor[3] <= 0.0f ) {
		textColor[3] = 1.0f;
	}

	Com_sprintf( buffer, sizeof( buffer ), "%d / %d", health, armor );
	CG_Text_Paint( rect->x + 2, rect->y + rect->h - 2, scale, textColor, buffer, 0, 0, textStyle );
}

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

	if ( cg.selectedScore < 0 || cg.selectedScore >= cg.numScores || cg.selectedScore >= MAX_CLIENTS ) {
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

	if ( score->client < 0 || score->client >= cgs.maxclients || score->client >= MAX_CLIENTS ) {
		return NULL;
	}

	return &cgs.clientinfo[score->client];
}

/*
=============
CG_GetTeamName

Resolves the configured display name for the supplied team, preferring configstrings before cvars.
=============
*/
const char *CG_GetTeamName( team_t team ) {
	const char	*teamName;

	switch ( team ) {
	case TEAM_RED:
		teamName = cgs.redTeamName;
		if ( teamName && teamName[0] ) {
			return teamName;
		}
		if ( cg_redTeamName.string[0] != '\0' ) {
			return cg_redTeamName.string;
		}
		return DEFAULT_REDTEAM_NAME;
	case TEAM_BLUE:
		teamName = cgs.blueTeamName;
		if ( teamName && teamName[0] ) {
			return teamName;
		}
		if ( cg_blueTeamName.string[0] != '\0' ) {
			return cg_blueTeamName.string;
		}
		return DEFAULT_BLUETEAM_NAME;
	default:
		return "Spectator";
	}
}

/*
=============
CG_GetTeamLabel

Provides a human readable label for the supplied team.
=============
*/
static const char *CG_GetTeamLabel( team_t team ) {
	return CG_GetTeamName( team );
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

Returns the number of valid clientinfo entries available for player counts.
=============
*/
static int CG_CountActivePlayers( void ) {
	int		count;
	int		i;

	count = 0;
	for ( i = 0; i < cgs.maxclients && i < MAX_CLIENTS; i++ ) {
		if ( cgs.clientinfo[i].infoValid ) {
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
	configName = serverInfo ? Info_ValueForKey( serverInfo, SERVERINFO_KEY_MAPNAME ) : NULL;
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
CG_FindArenaLongNameInData

Searches parsed arena info blocks for the long display name of the supplied map.
=============
*/
static qboolean CG_FindArenaLongNameInData( char *data, const char *mapName, char *buffer, size_t bufferSize ) {
	char	*cursor;
	char	*token;
	char	key[MAX_TOKEN_CHARS];
	char	info[MAX_INFO_STRING];

	if ( !data || !mapName || !*mapName || !buffer || bufferSize <= 0 ) {
		return qfalse;
	}

	cursor = data;
	while ( 1 ) {
		token = COM_Parse( &cursor );
		if ( !token[0] ) {
			break;
		}
		if ( strcmp( token, "{" ) ) {
			break;
		}

		info[0] = '\0';
		while ( 1 ) {
			token = COM_ParseExt( &cursor, qtrue );
			if ( !token[0] ) {
				break;
			}
			if ( !strcmp( token, "}" ) ) {
				break;
			}

			Q_strncpyz( key, token, sizeof( key ) );
			token = COM_ParseExt( &cursor, qfalse );
			Info_SetValueForKey( info, key, token[0] ? token : "<NULL>" );
		}

		if ( !Q_stricmp( Info_ValueForKey( info, ARENA_INFO_KEY_MAP ), mapName ) ) {
			const char	*longName;

			longName = Info_ValueForKey( info, ARENA_INFO_KEY_LONGNAME );
			if ( longName && *longName ) {
				Q_strncpyz( buffer, longName, bufferSize );
				return qtrue;
			}
		}
	}

	return qfalse;
}

/*
=============
CG_FindArenaLongNameInFile

Loads an arena metadata file and searches it for a retail long map name.
=============
*/
static qboolean CG_FindArenaLongNameInFile( const char *filename, const char *mapName, char *buffer, size_t bufferSize ) {
	static char	arenaText[CG_ARENA_LOOKUP_TEXT_SIZE];
	fileHandle_t	file;
	int		length;

	if ( !filename || !*filename ) {
		return qfalse;
	}

	file = 0;
	length = trap_FS_FOpenFile( filename, &file, FS_READ );
	if ( length <= 0 || !file ) {
		return qfalse;
	}
	if ( length >= (int)sizeof( arenaText ) ) {
		trap_FS_FCloseFile( file );
		return qfalse;
	}

	trap_FS_Read( arenaText, length, file );
	arenaText[length] = '\0';
	trap_FS_FCloseFile( file );

	return CG_FindArenaLongNameInData( arenaText, mapName, buffer, bufferSize );
}

/*
=============
CG_FindArenaLongName

Looks up a map's arena longname using the retail arena metadata search paths.
=============
*/
static qboolean CG_FindArenaLongName( const char *mapName, char *buffer, size_t bufferSize ) {
	char	fileList[CG_ARENA_LOOKUP_FILE_LIST_SIZE];
	char	*cursor;
	int	count;
	int	index;

	if ( !mapName || !*mapName || !buffer || bufferSize <= 0 ) {
		return qfalse;
	}

	if ( CG_FindArenaLongNameInFile( "scripts/arenas.txt", mapName, buffer, bufferSize ) ) {
		return qtrue;
	}

	fileList[0] = '\0';
	count = trap_QL_FS_GetFileList( "scripts", ".arena", fileList, sizeof( fileList ) );
	cursor = fileList;
	for ( index = 0; index < count; index++ ) {
		char	path[MAX_QPATH];
		int	length;

		length = strlen( cursor );
		if ( length <= 0 ) {
			cursor++;
			continue;
		}

		Com_sprintf( path, sizeof( path ), "scripts/%s", cursor );
		if ( CG_FindArenaLongNameInFile( path, mapName, buffer, bufferSize ) ) {
			return qtrue;
		}
		cursor += length + 1;
	}

	return qfalse;
}

/*
=============
CG_BuildMapDisplayName

Resolves the scoreboard map label to the arena longname when retail metadata is available.
=============
*/
static void CG_BuildMapDisplayName( char *buffer, size_t bufferSize ) {
	static char	cachedMap[MAX_QPATH];
	static char	cachedTitle[MAX_INFO_VALUE];
	char		mapName[MAX_QPATH];

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	buffer[0] = '\0';
	CG_BuildCleanMapName( mapName, sizeof( mapName ) );
	if ( !mapName[0] ) {
		return;
	}

	if ( cachedMap[0] && !Q_stricmp( cachedMap, mapName ) ) {
		Q_strncpyz( buffer, cachedTitle, bufferSize );
		return;
	}

	Q_strncpyz( cachedMap, mapName, sizeof( cachedMap ) );
	if ( !CG_FindArenaLongName( mapName, cachedTitle, sizeof( cachedTitle ) ) ) {
		Q_strncpyz( cachedTitle, mapName, sizeof( cachedTitle ) );
	}

	Q_strncpyz( buffer, cachedTitle, bufferSize );
}

/*
=============
CG_DrawMapName

Prints the current retail map display name.
=============
*/
static void CG_DrawMapName(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	char		nameBuffer[MAX_INFO_VALUE];

	CG_BuildMapDisplayName( nameBuffer, sizeof( nameBuffer ) );
	CG_Text_Paint(rect->x, rect->y, scale, color, nameBuffer, 0, 0, textStyle);
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

Returns the same arena longname label used by the standalone map-name ownerdraw.
=============
*/
static void CG_GetMapDisplayName( char *buffer, size_t bufferSize ) {
	CG_BuildMapDisplayName( buffer, bufferSize );
}

/*
=============
CG_GetConfiguredPlayerCountLimit

Returns the best available retail-style cap for the shared player-count ownerdraw.
=============
*/
static int CG_GetConfiguredPlayerCountLimit( void ) {
	int	playerLimit;

	playerLimit = cgs.maxclients;
	if ( cgs.gametype == GT_FFA || cgs.gametype == GT_TOURNAMENT || cgs.playerCountTeamSize <= 0 ) {
		return playerLimit;
	}

	if ( cgs.gametype >= GT_TEAM ) {
		playerLimit = cgs.playerCountTeamSize * 2;
		if ( playerLimit > cgs.maxclients ) {
			playerLimit = cgs.maxclients;
		}

		return playerLimit;
	}

	return cgs.playerCountTeamSize;
}

/*
=============
CG_DrawPlayerCounts

Renders the retail-style active-player summary for intro and scoreboard overlays.
=============
*/
static void CG_DrawPlayerCounts(rectDef_t *rect, float scale, vec4_t color, int textStyle, int align) {
	char	buffer[32];
	float	x;
	int		active;
	int		playerLimit;

	active = CG_CountActivePlayers();
	playerLimit = CG_GetConfiguredPlayerCountLimit();
	if ( playerLimit <= 0 ) {
		playerLimit = cgs.maxclients;
	}

	Com_sprintf( buffer, sizeof( buffer ), "%i/%i Players", active, playerLimit );
	x = rect->x;
	CG_AlignTextX( &x, buffer, scale, align );
	CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_GetStartingWeaponPreviewMask

Prefers the retail loadout-mask configstring and falls back to legacy
g_startingWeapons serverinfo when the configstring is absent.
=============
*/
static unsigned int CG_GetStartingWeaponPreviewMask( void ) {
	const char	*maskText;
	const char	*info;
	char		value[MAX_INFO_VALUE];
	unsigned int	serverMask;
	unsigned int	previewMask;
	weapon_t	weapon;

	maskText = CG_ConfigString( CS_LOADOUT_MASK );
	if ( maskText && maskText[0] ) {
		return (unsigned int)strtoul( maskText, NULL, 0 );
	}

	info = CG_ConfigString( CS_SERVERINFO );
	if ( !info || !*info ) {
		return 0u;
	}

	CG_GetServerInfoValue( info, "g_startingWeapons", value, sizeof( value ) );
	serverMask = value[0] ? (unsigned int)strtoul( value, NULL, 0 ) : 0u;
	previewMask = 0u;

	for ( weapon = WP_GAUNTLET; weapon < WP_NUM_WEAPONS; weapon++ ) {
		if ( serverMask & ( 1u << weapon ) ) {
			previewMask |= ( 1u << ( weapon - WP_GAUNTLET ) );
		}
	}

	return previewMask;
}

/*
=============
CG_GetStartingWeaponIconHandle

Resolves the retail starting-weapon preview icon from the cgame weapon slab.
=============
*/
static qhandle_t CG_GetStartingWeaponIconHandle( weapon_t weapon ) {
	if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return 0;
	}

	if ( !cg_weapons[weapon].registered ) {
		CG_RegisterWeapon( weapon );
	}

	return cg_weapons[weapon].weaponIcon;
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
		if ( !buffer[0] ) {
			CG_GetServerInfoValue( info, "sv_hostname", buffer, bufferSize );
		}
	}

	if ( !buffer[0] ) {
		Q_strncpyz( buffer, "Unknown location", bufferSize );
	}
}

/*
=============
CG_BuildIntroPanelDetailString

Builds the shared retail location/map detail string for intro panel ownerdraws.
=============
*/
static void CG_BuildIntroPanelDetailString( char *buffer, size_t bufferSize ) {
	char	mapName[MAX_INFO_VALUE];
	char	location[MAX_INFO_VALUE];

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	buffer[0] = '\0';
	CG_GetMapDisplayName( mapName, sizeof( mapName ) );
	if ( !mapName[0] ) {
		return;
	}

	CG_GetServerLocation( location, sizeof( location ) );
	if ( location[0] && Q_stricmp( location, "Unknown location" ) ) {
		Com_sprintf( buffer, bufferSize, "%s - %s", location, mapName );
		return;
	}

	Q_strncpyz( buffer, mapName, bufferSize );
}

/*
=============
CG_GameTypeShortString

Maps the active gametype to the retail intro-panel abbreviation table.
=============
*/
static const char *CG_GameTypeShortString( void ) {
	switch ( cgs.gametype ) {
	case GT_FFA:
		return "FFA";
	case GT_TOURNAMENT:
		return "DUEL";
	case GT_SINGLE_PLAYER:
		return "RACE";
	case GT_TEAM:
		return "TDM";
	case GT_CLAN_ARENA:
		return "CA";
	case GT_CTF:
		return "CTF";
	case GT_1FCTF:
		return "1F";
	case GT_OBELISK:
		return "OB";
	case GT_HARVESTER:
		return "HAR";
	case GT_FREEZE:
		return "FT";
	case GT_DOMINATION:
		return "DOM";
	case GT_ATTACK_DEFEND:
		return "AD";
	case GT_RED_ROVER:
		return "RR";
	default:
		return "Unknown Gametype";
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
CG_DrawServerSettings

Draws the retail custom-settings panel consumed by the intro/about overlays.
=============
*/
static void CG_DrawServerSettings(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle) {
	unsigned int	weaponMask;
	float		x;
	float		y;
	float		lineHeight;
	int		activeCount;
	char		buffer[64];
	int		i;

	if ( !rect ) {
		return;
	}

	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	lineHeight = (float)CG_Text_Height( "AIR CONTROL", scale, 0 );
	if ( lineHeight <= 0.0f ) {
		lineHeight = 10.0f;
	}
	lineHeight += 2.0f;
	activeCount = 0;
	weaponMask = (unsigned int)( cgs.customSettingsMask & CUSTOM_SETTING_WEAPON_MASK );

	if ( cgs.customSettingsMask & CUSTOM_SETTING_AIR_CONTROL ) {
		CG_Text_Paint( x, y, scale, color, "AIR CONTROL", 0, 0, textStyle );
		y += lineHeight;
		activeCount++;
	}
	if ( cgs.customSettingsMask & CUSTOM_SETTING_RAMP_JUMP ) {
		CG_Text_Paint( x, y, scale, color, "RAMP JUMPING", 0, 0, textStyle );
		y += lineHeight;
		activeCount++;
	}
	if ( cgs.serverSettingsArmorTiered ) {
		CG_Text_Paint( x, y, scale, color, "TIERED ARMOR", 0, 0, textStyle );
		y += lineHeight;
		activeCount++;
	}
	if ( cgs.customSettingsMask & CUSTOM_SETTING_WEAPON_SWITCHING ) {
		CG_Text_Paint( x, y, scale, color, "MODIFIED WEAPON SWITCH", 0, 0, textStyle );
		y += lineHeight;
		activeCount++;
	}
	if ( cgs.serverSettingsQuadFactor != 3 ) {
		Com_sprintf( buffer, sizeof( buffer ), "%ix QUAD", cgs.serverSettingsQuadFactor );
		CG_Text_Paint( x, y, scale, color, buffer, 0, 0, textStyle );
		y += lineHeight;
		activeCount++;
	}
	if ( cgs.customSettingsMask & CUSTOM_SETTING_PHYSICS ) {
		CG_Text_Paint( x, y, scale, color, "MODIFIED PHYSICS", 0, 0, textStyle );
		y += lineHeight;
		activeCount++;
	}
	if ( cgs.serverSettingsGravity != 800 ) {
		Com_sprintf( buffer, sizeof( buffer ), "GRAVITY %i", cgs.serverSettingsGravity );
		CG_Text_Paint( x, y, scale, color, buffer, 0, 0, textStyle );
		y += lineHeight;
		activeCount++;
	}
	if ( cgs.customSettingsMask & CUSTOM_SETTING_INSTAGIB ) {
		CG_Text_Paint( x, y, scale, color, "INSTAGIB", 0, 0, textStyle );
		y += lineHeight;
		activeCount++;
	}
	if ( cgs.customSettingsMask & CUSTOM_SETTING_QUAD_HOG ) {
		CG_Text_Paint( x, y, scale, color, "QUAD HOG", 0, 0, textStyle );
		y += lineHeight;
		activeCount++;
	}
	if ( cgs.customSettingsMask & CUSTOM_SETTING_REGEN_HEALTH ) {
		CG_Text_Paint( x, y, scale, color, "REGEN HEALTH", 0, 0, textStyle );
		y += lineHeight;
		activeCount++;
	}
	if ( ( cgs.customSettingsMask & CUSTOM_SETTING_DROP_HEALTH ) && !( cgs.customSettingsMask & CUSTOM_SETTING_INSTAGIB ) ) {
		CG_Text_Paint( x, y, scale, color, "DROP DAMAGED HEALTH", 0, 0, textStyle );
		y += lineHeight;
		activeCount++;
	}
	if ( cgs.customSettingsMask & CUSTOM_SETTING_VAMPIRIC_DAMAGE ) {
		CG_Text_Paint( x, y, scale, color, "VAMPIRIC DAMAGE", 0, 0, textStyle );
		y += lineHeight;
		activeCount++;
	}
	if ( cgs.customSettingsMask & CUSTOM_SETTING_ITEM_SPAWNING ) {
		CG_Text_Paint( x, y, scale, color, "MODIFIED ITEM SPAWNING", 0, 0, textStyle );
		y += lineHeight;
		activeCount++;
	}
	if ( cgs.customSettingsMask & CUSTOM_SETTING_HEADSHOTS ) {
		CG_Text_Paint( x, y, scale, color, "HEADSHOTS ENABLED", 0, 0, textStyle );
		y += lineHeight;
		activeCount++;
	}
	if ( cgs.customSettingsMask & CUSTOM_SETTING_RAIL_JUMPING ) {
		CG_Text_Paint( x, y, scale, color, "RAIL JUMPING", 0, 0, textStyle );
		y += lineHeight;
		activeCount++;
	}
	if ( weaponMask != 0u ) {
		CG_Text_Paint( x, y, scale, color, "MODIFIED WEAPONS", 0, 0, textStyle );
		if ( activeCount < 15 ) {
			float	iconSize;
			float	iconX;
			float	iconY;

			y += lineHeight;
			iconSize = lineHeight + 2.0f;
			iconX = x;
			iconY = y - iconSize + 2.0f;

			for ( i = 0; i < ARRAY_LEN( cgServerSettingsWeaponIcons ); i++ ) {
				float		badgeSize;
				qhandle_t	icon;
				weapon_t	weapon;

				if ( ( weaponMask & cgServerSettingsWeaponIcons[i].bit ) == 0u ) {
					continue;
				}

				weapon = cgServerSettingsWeaponIcons[i].weapon;
				icon = CG_GetStartingWeaponIconHandle( weapon );
				if ( !icon ) {
					continue;
				}

				CG_DrawPic( iconX, iconY, iconSize, iconSize, icon );
				badgeSize = iconSize * 0.5f;
				if ( cgs.media.modifiedIcon != 0 ) {
					CG_DrawPic( iconX + iconSize * 0.75f, iconY + iconSize * 0.5f, badgeSize, badgeSize, cgs.media.modifiedIcon );
				}
				iconX += iconSize + 2.0f;
			}
		}
	}
}

/*
=============
CG_DrawStartingWeapons

Draws the retail icon-strip loadout preview plus the queued primary weapon.
=============
*/
static void CG_DrawStartingWeapons(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle) {
	unsigned int	loadoutMask;
	int		primaryIndex;
	int		i;
	float		xOffset;
	float		plusX;
	float		plusY;
	float		plusWidth;
	qhandle_t	shader;

	(void)text_x;
	(void)text_y;

	if ( !rect || rect->w <= 0.0f || rect->h <= 0.0f ) {
		return;
	}

	loadoutMask = CG_GetStartingWeaponPreviewMask();
	xOffset = 0.0f;

	for ( i = 0; i < CG_STARTING_WEAPON_ICON_COUNT; i++ ) {
		if ( ( loadoutMask & ( 1u << i ) ) == 0 ) {
			continue;
		}

		shader = CG_GetStartingWeaponIconHandle( cgStartingWeaponIcons[i].weapon );
		if ( shader != 0 ) {
			trap_R_SetColor( colorWhite );
			CG_DrawPic( rect->x + xOffset, rect->y, rect->w, rect->h, shader );
			trap_R_SetColor( NULL );
		}

		xOffset += rect->w * 1.5f;
	}

	if ( !CG_LoadoutsEnabled() ) {
		return;
	}

	plusWidth = CG_Text_Width( "+", scale, 0 );
	plusX = rect->x + xOffset;
	if ( plusWidth < rect->w ) {
		plusX += ( rect->w - plusWidth ) * 0.5f;
	}
	plusY = rect->y + rect->h * 0.5f + CG_Text_Height( "+", scale, 0 ) * 0.5f;
	CG_Text_Paint( plusX, plusY, scale, color, "+", 0, 0, textStyle );

	primaryIndex = cg.weaponPrimary;
	if ( primaryIndex <= 0 || primaryIndex > CG_STARTING_WEAPON_ICON_COUNT ) {
		primaryIndex = CG_STARTING_WEAPON_ICON_COUNT;
	}

	shader = CG_GetStartingWeaponIconHandle( cgStartingWeaponIcons[primaryIndex - 1].weapon );
	if ( shader == 0 ) {
		return;
	}

	trap_R_SetColor( colorWhite );
	CG_DrawPic( rect->x + xOffset + rect->w, rect->y, rect->w, rect->h, shader );
	trap_R_SetColor( NULL );
}


/*
=============
CG_DrawGameLimit

Renders the retail-style single limit label for the current ruleset.
=============
*/
static void CG_DrawGameLimit( rectDef_t *rect, float scale, vec4_t color, int textStyle, int align ) {
	char	buffer[128];
	float	x;

	switch ( cgs.gametype ) {
	case GT_CTF:
	case GT_1FCTF:
	case GT_OBELISK:
	case GT_HARVESTER:
		Com_sprintf( buffer, sizeof( buffer ), "Cap Limit: %d", cgs.capturelimit );
		break;

	case GT_CLAN_ARENA:
	case GT_FREEZE:
	case GT_RED_ROVER:
		Com_sprintf( buffer, sizeof( buffer ), "Round Limit: %d", cgs.roundlimit );
		break;

	case GT_DOMINATION:
	case GT_ATTACK_DEFEND:
		Com_sprintf( buffer, sizeof( buffer ), "Score Limit: %d", cgs.scorelimit );
		break;

	default:
		Com_sprintf( buffer, sizeof( buffer ), "Frag Limit: %d", cgs.fraglimit );
		break;
	}

	x = rect->x;
	if ( align == ITEM_ALIGN_CENTER ) {
		x -= CG_Text_Width( buffer, scale, 0 ) * 0.5f;
	}
	CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_RegisterGameTypeIcons

Registers the retail HUD gametype icon set during graphics startup.
=============
*/
void CG_RegisterGameTypeIcons( void ) {
	memset( cgGameTypeIconShaders, 0, sizeof( cgGameTypeIconShaders ) );

	cgGameTypeIconShaders[GT_FFA] = trap_R_RegisterShaderNoMip( "ui/assets/hud/ffa.tga" );
	cgGameTypeIconShaders[GT_TOURNAMENT] = trap_R_RegisterShaderNoMip( "ui/assets/hud/duel.tga" );
	cgGameTypeIconShaders[GT_SINGLE_PLAYER] = trap_R_RegisterShaderNoMip( "ui/assets/hud/race.tga" );
	cgGameTypeIconShaders[GT_TEAM] = trap_R_RegisterShaderNoMip( "ui/assets/hud/tdm.tga" );
	cgGameTypeIconShaders[GT_CLAN_ARENA] = trap_R_RegisterShaderNoMip( "ui/assets/hud/ca.tga" );
	cgGameTypeIconShaders[GT_CTF] = trap_R_RegisterShaderNoMip( "ui/assets/hud/ctf.tga" );
	cgGameTypeIconShaders[GT_1FCTF] = trap_R_RegisterShaderNoMip( "ui/assets/hud/1f.tga" );
	cgGameTypeIconShaders[GT_OBELISK] = cgGameTypeIconShaders[GT_FFA];
	cgGameTypeIconShaders[GT_HARVESTER] = trap_R_RegisterShaderNoMip( "ui/assets/hud/har.tga" );
	cgGameTypeIconShaders[GT_FREEZE] = trap_R_RegisterShaderNoMip( "ui/assets/hud/ft.tga" );
	cgGameTypeIconShaders[GT_DOMINATION] = trap_R_RegisterShaderNoMip( "ui/assets/hud/dom.tga" );
	cgGameTypeIconShaders[GT_ATTACK_DEFEND] = trap_R_RegisterShaderNoMip( "ui/assets/hud/ad.tga" );
	cgGameTypeIconShaders[GT_RED_ROVER] = trap_R_RegisterShaderNoMip( "ui/assets/hud/rr.tga" );
}

/*
=============
CG_GameTypeIconShader

Returns the pre-registered shader handle for the supplied gametype icon.
=============
*/
static qhandle_t CG_GameTypeIconShader( gametype_t gametype ) {
	if ( gametype < 0 || gametype >= GT_MAX_GAME_TYPE ) {
		return 0;
	}

	return cgGameTypeIconShaders[gametype];
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

Outputs the retail "Gametype Fullname - Detail" intro-panel label.
=============
*/
static void CG_DrawGameTypeMap( rectDef_t *rect, float scale, vec4_t color, int textStyle, int align ) {
	char	detailBuffer[256];
	char	buffer[256];
	float	x;

	CG_BuildIntroPanelDetailString( detailBuffer, sizeof( detailBuffer ) );
	Com_sprintf( buffer, sizeof( buffer ), "%s - %s", CG_GameTypeString(), detailBuffer );

	x = rect->x;
	CG_AlignTextX( &x, buffer, scale, align );
	CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_BuildMatchStateLabel

Builds the compact retail match-state label for HUD text.
=============
*/
static void CG_BuildMatchStateLabel( char *buffer, size_t bufferSize ) {
	int timeoutStartTime;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	buffer[0] = '\0';
	timeoutStartTime = CG_GetMatchTimeoutStartTime();
	if ( cgs.matchTimeoutActive ) {
		if ( cgs.matchTimeoutTeam == TEAM_RED || cgs.matchTimeoutTeam == TEAM_BLUE ) {
			Com_sprintf( buffer, bufferSize, "Timeout %s", CG_GetTeamLabel( cgs.matchTimeoutTeam ) );
		} else {
			Q_strncpyz( buffer, "Timeout", bufferSize );
		}
		return;
	} else if ( timeoutStartTime > 0 ) {
		Q_strncpyz( buffer, "Timeout", bufferSize );
		return;
	}
	if ( cgs.matchOvertimeActive ) {
		Q_strncpyz( buffer, "Overtime", bufferSize );
		return;
	}
	if ( cg.snap && cg.snap->ps.pm_type == PM_INTERMISSION ) {
		Q_strncpyz( buffer, "Intermission", bufferSize );
		return;
	}
	if ( cgs.matchRoundState == ROUNDSTATE_WARMUP || cg.warmup > 0 ) {
		Q_strncpyz( buffer, "Warmup", bufferSize );
		return;
	}
	if ( cgs.matchRoundState == ROUNDSTATE_COMPLETE ) {
		Q_strncpyz( buffer, "Round complete", bufferSize );
		return;
	}
	if ( cgs.matchRoundNumber > 0 ) {
		Com_sprintf( buffer, bufferSize, "Round %i", cgs.matchRoundNumber );
		return;
	}

	Q_strncpyz( buffer, "In progress", bufferSize );
}

/*
=============
CG_GetMatchStateLabel

Summarizes the current match flow state for HUD text.
=============
*/
static const char *CG_GetMatchStateLabel( void ) {
	static char buffer[32];

	CG_BuildMatchStateLabel( buffer, sizeof( buffer ) );
	return buffer;
}

/*
=============
CG_GetMatchDetailsPhaseLabel

Returns the narrower retail phase label used by the intro-panel ownerdraw.
=============
*/
static const char *CG_GetMatchDetailsPhaseLabel( void ) {
	if ( cg.snap && cg.snap->ps.pm_type == PM_INTERMISSION ) {
		return "MATCH SUMMARY";
	}

	if ( cg.warmup != 0 ) {
		return "MATCH WARMUP";
	}

	return "MATCH IN PROGRESS";
}

/*
=============
CG_DrawMatchDetails

Renders the retail "Match phase - Gametype Shortname - Detail" text.
=============
*/
static void CG_DrawMatchDetails( rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
	char	detailBuffer[256];
	char	buffer[256];

	CG_BuildIntroPanelDetailString( detailBuffer, sizeof( detailBuffer ) );
	Com_sprintf( buffer, sizeof( buffer ), "%s - %s - %s",
		CG_GetMatchDetailsPhaseLabel(), CG_GameTypeShortString(), detailBuffer );

	CG_Text_Paint( rect->x, rect->y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawMatchEndCondition

Draws the retail end-condition sentence for the active ruleset.
=============
*/
static void CG_DrawMatchEndCondition( rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
	const char *reason;
	qboolean	timeLimitExpired;

	if ( cgs.gametype == GT_RACE ) {
		reason = "Fastest race time within the time limit";
	} else {
		timeLimitExpired = ( cgs.timelimit > 0
			&& cg.time - cgs.levelStartTime >= cgs.timelimit * 60000 ) ? qtrue : qfalse;
		if ( timeLimitExpired ) {
			if ( cgs.gametype == GT_CTF ) {
				reason = "Most flag captures within the time limit";
			} else if ( cgs.gametype == GT_CLAN_ARENA ) {
				reason = "Most rounds won within the time limit";
			} else {
				reason = "Highest score within the time limit";
			}
		} else if ( cgs.gametype == GT_CTF ) {
			if ( cgs.capturelimit == 0 || ( cgs.scores1 < cgs.capturelimit && cgs.scores2 < cgs.capturelimit ) ) {
				reason = "First to reach the mercy limit";
			} else {
				reason = "First to reach the capture limit";
			}
		} else if ( cgs.gametype == GT_CLAN_ARENA ) {
			reason = "First to reach the round limit";
		} else if ( cgs.gametype == GT_DOMINATION || cgs.gametype == GT_ATTACK_DEFEND ) {
			reason = "First to reach the score limit";
		} else {
			reason = "Highest score at the end of the game";
		}
	}

	CG_Text_Paint( rect->x, rect->y, scale, color, reason, 0, 0, textStyle );
}

/*
=============
CG_GetMatchPhaseText

Returns the retail uppercase match-phase banner used by compact scoreboard ownerdraws.
=============
*/
static const char *CG_GetMatchPhaseText( void ) {
	if ( cg.snap && cg.snap->ps.pm_type == PM_INTERMISSION ) {
		return "MATCH SUMMARY";
	}
	if ( cg.warmup != 0 ) {
		return "MATCH WARMUP";
	}

	return "MATCH IN PROGRESS";
}

/*
=============
CG_GetMatchStatusText

Builds the retail phase-plus-status text used by the match-status ownerdraw.
=============
*/
const char *CG_GetMatchStatusText( void ) {
	static char	buffer[256];
	const char	*phase;
	const char	*leaderName;
	int		redScore;
	int		blueScore;
	int		score;

	if ( cg.snap && cg.snap->ps.pm_type == PM_INTERMISSION ) {
		phase = "MATCH SUMMARY";
	} else if ( cg.warmup != 0 ) {
		phase = "MATCH WARMUP";
	} else {
		phase = "MATCH IN PROGRESS";
	}

	if ( cgs.scores1 == SCORE_NOT_PRESENT && cgs.scores2 == SCORE_NOT_PRESENT &&
		( cgs.gametype < GT_TEAM || cgs.gametype == GT_RED_ROVER ) ) {
		return phase;
	}

	if ( cgs.gametype == GT_RACE ) {
		if ( cgs.scores1 == 0x7fffffff || cgs.scores1 <= 0 ) {
			return phase;
		}

		Com_sprintf( buffer, sizeof( buffer ), "%s - %s^7 leads with a score of %s",
			phase, "", CG_FormatSignedMilliseconds( cgs.scores1 ) );
		return buffer;
	}

	if ( cgs.gametype >= GT_TEAM && cgs.gametype != GT_RED_ROVER ) {
		redScore = cg.teamScores[0];
		blueScore = cg.teamScores[1];

		if ( redScore == blueScore ) {
			Com_sprintf( buffer, sizeof( buffer ), "%s - Teams are tied at %i", phase, redScore );
		} else if ( redScore > blueScore ) {
			Com_sprintf( buffer, sizeof( buffer ), "%s - ^1Red^7 leads ^4Blue^7, %i to %i",
				phase, redScore, blueScore );
		} else {
			Com_sprintf( buffer, sizeof( buffer ), "%s - ^4Blue^7 leads ^1Red^7, %i to %i",
				phase, blueScore, redScore );
		}
		return buffer;
	}

	if ( cg.snap && cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR ) {
		if ( cgs.scores1 != SCORE_NOT_PRESENT ) {
			score = cgs.scores1;
			leaderName = cgs.firstPlaceName;
		} else {
			score = cgs.scores2;
			leaderName = cgs.secondPlaceName;
		}

		Com_sprintf( buffer, sizeof( buffer ), "%s - %s leads with %i", phase, leaderName, score );
		return buffer;
	}

	if ( !cg.snap ) {
		return phase;
	}

	Com_sprintf( buffer, sizeof( buffer ), "%s - %s place with %i",
		phase,
		CG_PlaceString( cg.snap->ps.persistant[PERS_RANK] + 1 ),
		cg.snap->ps.persistant[PERS_SCORE] );
	return buffer;
}

/*
=============
CG_DrawMatchStatus

Renders the pre-composed retail match-status ownerdraw text.
=============
*/
static void CG_DrawMatchStatus( rectDef_t *rect, float scale, vec4_t color, int textStyle, int align ) {
	const char	*statusText;
	float	x;

	statusText = CG_GetMatchStatusText();
	x = rect->x;
	CG_AlignTextX( &x, statusText, scale, align );
	CG_Text_Paint( x, rect->y, scale, color, statusText, 0, 0, textStyle );
}

/*
=============
CG_IsActiveScoreEntry

Reports whether the score row belongs to an active non-spectator client.
=============
*/
static qboolean CG_IsActiveScoreEntry( const score_t *score ) {
	const clientInfo_t	*ci;

	if ( !score ) {
		return qfalse;
	}

	if ( score->client < 0 || score->client >= cgs.maxclients ) {
		return qfalse;
	}

	ci = &cgs.clientinfo[score->client];
	if ( !ci->infoValid ) {
		return qfalse;
	}

	if ( ci->team == TEAM_SPECTATOR || score->team == TEAM_SPECTATOR ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
CG_GetActiveScoreByIndex

Returns the Nth active (non-spectator) scoreboard row.
=============
*/
static const score_t *CG_GetActiveScoreByIndex( int activeIndex ) {
	int	i;
	int	count;

	if ( activeIndex < 0 ) {
		return NULL;
	}

	count = 0;
	for ( i = 0; i < cg.numScores; i++ ) {
		if ( !CG_IsActiveScoreEntry( &cg.scores[i] ) ) {
			continue;
		}

		if ( count == activeIndex ) {
			return &cg.scores[i];
		}

		count++;
	}

	return NULL;
}

/*
=============
CG_GetEndGameScoreText

Builds the local player's summary text used by end-game score menus.
=============
*/
static const char *CG_GetEndGameScoreText( void ) {
	static char	buffer[128];
	int		score;
	int		rank;
	int		defends;
	int		assists;
	int		captures;

	buffer[0] = '\0';

	if ( !cg.snap ) {
		return "";
	}

	score = cg.snap->ps.persistant[PERS_SCORE];
	rank = cg.snap->ps.persistant[PERS_RANK] + 1;
	defends = cg.snap->ps.persistant[PERS_DEFEND_COUNT];
	assists = cg.snap->ps.persistant[PERS_ASSIST_COUNT];
	captures = cg.snap->ps.persistant[PERS_CAPTURES];

	if ( cgs.gametype == GT_SINGLE_PLAYER || cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR ) {
		return "";
	}

	if ( cgs.gametype == GT_RED_ROVER ) {
		if ( score == SCORE_NOT_PRESENT ) {
			return "";
		}
		if ( score == CG_SCORE_FORFEIT ) {
			return "You forfeited the match.";
		}

		Com_sprintf( buffer, sizeof( buffer ), "You finished with a score of %d.", score );
		return buffer;
	}

	if ( !CG_IsTeamWinnerGametype( cgs.gametype ) ) {
		if ( score == SCORE_NOT_PRESENT ) {
			return "";
		}
		if ( score == CG_SCORE_FORFEIT ) {
			return "You forfeited the match.";
		}

		Com_sprintf( buffer, sizeof( buffer ), "You finished %s with a score of %d",
			CG_PlaceString( rank ), score );
		return buffer;
	}

	if ( captures > 0 ) {
		if ( cgs.gametype == GT_HARVESTER ) {
			Com_sprintf( buffer, sizeof( buffer ), "You captured %d skull%s.",
				captures, CG_PluralSuffix( captures ) );
		} else {
			Com_sprintf( buffer, sizeof( buffer ), "You had %d flag capture%s.",
				captures, CG_PluralSuffix( captures ) );
		}
		return buffer;
	}

	if ( assists > 0 ) {
		Com_sprintf( buffer, sizeof( buffer ), "You had %d assist%s.",
			assists, CG_PluralSuffix( assists ) );
		return buffer;
	}

	if ( defends > 0 ) {
		Com_sprintf( buffer, sizeof( buffer ), "You had %d defend%s.",
			defends, CG_PluralSuffix( defends ) );
		return buffer;
	}

	if ( score == SCORE_NOT_PRESENT ) {
		return "";
	}
	if ( score == CG_SCORE_FORFEIT ) {
		return "You forfeited the match.";
	}

	Com_sprintf( buffer, sizeof( buffer ), "You finished with a score of %d.", score );
	return buffer;
}

/*
=============
CG_GetMatchWinnerText

Builds the winner line used by end-game score menus.
=============
*/
static const char *CG_GetMatchWinnerText( void ) {
	static char		buffer[128];
	const score_t		*winner;
	const score_t		*runnerUp;
	const clientInfo_t	*ci;
	team_t			winningTeam;
	qboolean		byForfeit;

	buffer[0] = '\0';
	byForfeit = qfalse;

	if ( CG_IsTeamWinnerGametype( cgs.gametype ) ) {
		if ( cg.teamScores[0] == cg.teamScores[1] ) {
			return "Match tied";
		}

		winningTeam = ( cg.teamScores[0] > cg.teamScores[1] ) ? TEAM_RED : TEAM_BLUE;
		if ( cg.snap && cg.snap->ps.pm_type == PM_INTERMISSION &&
			( cg.teamScores[0] == CG_SCORE_FORFEIT || cg.teamScores[1] == CG_SCORE_FORFEIT ) ) {
			Com_sprintf( buffer, sizeof( buffer ), "^%c%s^7 WINS by forfeit",
				( winningTeam == TEAM_RED ) ? '1' : '4',
				CG_GetTeamName( winningTeam ) );
		} else {
			Com_sprintf( buffer, sizeof( buffer ), "Winner: %s", CG_GetTeamName( winningTeam ) );
		}
		return buffer;
	}

	winner = CG_GetActiveScoreByIndex( 0 );
	runnerUp = CG_GetActiveScoreByIndex( 1 );
	if ( winner && runnerUp && winner->score == runnerUp->score ) {
		return "Match tied";
	}
	if ( !winner ) {
		return "Match complete";
	}
	if ( winner->score == CG_SCORE_FORFEIT ) {
		byForfeit = qtrue;
		winner = runnerUp;
	}
	if ( !winner ) {
		return "";
	}
	if ( winner->score == SCORE_NOT_PRESENT ) {
		return "";
	}

	ci = &cgs.clientinfo[winner->client];
	if ( cg.snap && cg.snap->ps.pm_type == PM_INTERMISSION ) {
		if ( byForfeit ) {
			Com_sprintf( buffer, sizeof( buffer ), "%s^7 WINS by forfeit",
				ci->name[0] ? ci->name : "Unknown player" );
		} else {
			Com_sprintf( buffer, sizeof( buffer ), "%s^7 WINS",
				ci->name[0] ? ci->name : "Unknown player" );
		}
		return buffer;
	}

	Com_sprintf( buffer, sizeof( buffer ), "Winner: %s", ci->name[0] ? ci->name : "Unknown player" );
	return buffer;
}

/*
=============
CG_DrawMatchWinner

Paints the winner line for end-game scoreboards.
=============
*/
static void CG_DrawMatchWinner( rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle ) {
	const char	*winnerText;
	float		x;
	float		y;

	if ( !rect ) {
		return;
	}

	winnerText = CG_GetMatchWinnerText();
	if ( !winnerText || !winnerText[0] ) {
		return;
	}

	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, winnerText, 0, 0, textStyle );
}

/*
=============
CG_DrawEndGameScore

Paints the local score/placement line for end-game scoreboards.
=============
*/
static void CG_DrawEndGameScore( rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, int textStyle ) {
	const char	*scoreText;
	float		x;
	float		y;

	if ( !rect ) {
		return;
	}

	scoreText = CG_GetEndGameScoreText();
	if ( !scoreText || !scoreText[0] ) {
		return;
	}

	CG_GetTextPosition( rect, text_x, text_y, &x, &y );
	CG_Text_Paint( x, y, scale, color, scoreText, 0, 0, textStyle );
}

/*
=============
CG_DrawRoundLabel

Displays the retail warmup/round label.
=============
*/
static void CG_DrawRoundLabel( rectDef_t *rect, float scale, vec4_t color, int textStyle, int align ) {
	char		label[32];
	float		x;

	if ( cgs.matchRoundNumber > 0 ) {
		Com_sprintf( label, sizeof( label ), "Round %d", cgs.matchRoundNumber );
	} else {
		Q_strncpyz( label, "Warmup", sizeof( label ) );
	}

	x = CG_AlignTextInRectX( rect, scale, label, align );
	CG_Text_Paint( x, rect->y + rect->h, scale, color, label, 0, 0, textStyle );
}

/*
=============
CG_DrawLocalTime

Paints the client's local date/time label using the retail HUD format.
=============
*/
static void CG_DrawLocalTime(rectDef_t *rect, float scale, vec4_t color, int textStyle, int align) {
	qtime_t		qt;
	const char	*monthLabel;
	char		buffer[64];
	float		x;

	trap_RealTime( &qt );
	if ( qt.tm_mon >= 0 && qt.tm_mon < (int)( sizeof( cgMonthAbbrev ) / sizeof( cgMonthAbbrev[0] ) ) ) {
		monthLabel = cgMonthAbbrev[qt.tm_mon];
	} else {
		monthLabel = cgMonthAbbrev[0];
	}

	Com_sprintf( buffer, sizeof( buffer ), "%02d:%02d (%s %02d, %d)",
		qt.tm_hour, qt.tm_min, monthLabel, qt.tm_mday, 1900 + qt.tm_year );

	x = rect->x;
	CG_AlignTextX( &x, buffer, scale, align );
	CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );
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
	char	previewToken[MAX_QPATH];
	cgVoteShotCache_t *cache;

	if ( slot < 1 || slot > 3 ) {
		return;
	}
	cache = &cg_voteShotCache[slot - 1];
	CG_GetVoteSlotString( slot, "Shot", previewToken, sizeof( previewToken ) );
	if ( !previewToken[0] ) {
		Q_strncpyz( previewToken, "default", sizeof( previewToken ) );
	}
	Com_sprintf( path, sizeof( path ), "levelshots/preview/%s", previewToken );
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
static void CG_DrawVoteGametype(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot) {
	char	buffer[MAX_CVAR_VALUE_STRING];

	CG_GetVoteSlotString( slot, "Gametype", buffer, sizeof( buffer ) );
	if ( !buffer[0] ) {
		return;
	}
	CG_Text_Paint( rect->x, rect->y - 8.0f, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawVoteName

Shows the prettified map name for the selected vote slot.
=============
*/
static void CG_DrawVoteName(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot) {
	char	buffer[MAX_CVAR_VALUE_STRING];

	CG_GetVoteSlotString( slot, "Name", buffer, sizeof( buffer ) );
	if ( !buffer[0] ) {
		CG_GetVoteSlotString( slot, "Map", buffer, sizeof( buffer ) );
		if ( !buffer[0] ) {
			return;
		}
	}
	CG_Text_Paint( rect->x, rect->y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawVoteMapSlot

Outputs the raw map name string for the vote slot widget.
=============
*/
static void CG_DrawVoteMapSlot(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot) {
	char	buffer[MAX_CVAR_VALUE_STRING];

	CG_GetVoteSlotString( slot, "Map", buffer, sizeof( buffer ) );
	if ( !buffer[0] ) {
		return;
	}
	CG_Text_Paint( rect->x, rect->y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawVoteCount

Paints the running vote count for the requested slot.
=============
*/
static void CG_DrawVoteCount(rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot, int align) {
	char	buffer[MAX_CVAR_VALUE_STRING];
	char	countText[MAX_CVAR_VALUE_STRING];
	float	x;

	CG_GetVoteSlotString( slot, "Count", countText, sizeof( countText ) );
	if ( !countText[0] ) {
		return;
	}
	Com_sprintf( buffer, sizeof( buffer ), "Votes: %s", countText );
	x = rect->x;
	CG_AlignTextX( &x, buffer, scale, align );
	CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawVoteTimer

Displays the time remaining until the current vote closes.
=============
*/
static void CG_DrawVoteTimer(rectDef_t *rect, float scale, vec4_t color, int textStyle, int align) {
	int		remaining;
	char	buffer[32];
	float	x;

	remaining = ( cgs.voteTime - cg.time + 20000 ) / 1000;
	if ( remaining < 1 ) {
		Q_strncpyz( buffer, "Voting has ended.", sizeof( buffer ) );
	} else if ( remaining == 1 ) {
		Com_sprintf( buffer, sizeof( buffer ), "Voting ends in %i second.", remaining );
	} else {
		Com_sprintf( buffer, sizeof( buffer ), "Voting ends in %i seconds.", remaining );
	}
	x = rect->x;
	CG_AlignTextX( &x, buffer, scale, align );
	CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawSelectedPlayerTeamColor

Fills the provided rectangle using the selected player's retail scoreboard color.
=============
*/
static void CG_DrawSelectedPlayerTeamColor(rectDef_t *rect, vec4_t color) {
	clientInfo_t	*ci;
	vec4_t			fill;

	if ( !rect ) {
		return;
	}

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
		if ( color ) {
			fill[0] = color[0];
			fill[1] = color[1];
			fill[2] = color[2];
			fill[3] = color[3];
		} else {
			Vector4Set( fill, 1.0f, 0.6f, 0.0f, 0.4f );
		}
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

	if ( !rect ) {
		return;
	}

	score = CG_GetSelectedScore();
	if ( !score ) {
		return;
	}

	Com_sprintf( buffer, sizeof( buffer ), "%i%%", score->accuracy );
	CG_Text_Paint(rect->x, rect->y, scale, color, buffer, 0, 0, textStyle);
}

static const weapon_t cgVerticalAccWeaponOrder[] = {
	WP_GAUNTLET,
	WP_MACHINEGUN,
	WP_SHOTGUN,
	WP_GRENADE_LAUNCHER,
	WP_ROCKET_LAUNCHER,
	WP_LIGHTNING,
	WP_RAILGUN,
	WP_PLASMAGUN,
	WP_BFG,
	WP_CHAINGUN,
	WP_NAILGUN,
	WP_PROX_LAUNCHER,
	WP_HEAVY_MACHINEGUN
};

/*
=============
CG_ShouldDrawAccVertical

Mirrors the retail accuracy-panel gate and refresh cadence.
=============
*/
static qboolean CG_ShouldDrawAccVertical( void ) {
	if ( !cg.accRequestActive || !cg.snap ) {
		return qfalse;
	}

	if ( cg.snap->ps.pm_type == PM_SPECTATOR &&
			!( cg.snap->ps.pm_flags & PMF_FOLLOW ) ) {
		return qfalse;
	}

	if ( cg.accRequestTime + 1000 < cg.time ) {
		cg.accRequestTime = cg.time;
		trap_SendClientCommand( "acc" );
	}

	return qtrue;
}

/*
=============
CG_ShouldDrawAccOverlay

Exports the accuracy-panel draw gate to legacy callers.
=============
*/
qboolean CG_ShouldDrawAccOverlay( void ) {
	return CG_ShouldDrawAccVertical();
}

/*
=============
CG_DrawWeaponVertical

Draws the retail vertical weapon-icon strip inside the `+acc` stats panel.
=============
*/
static void CG_DrawWeaponVertical( rectDef_t *rect, vec4_t color ) {
	int i;

	if ( !rect ) {
		return;
	}

	trap_R_SetColor( color );
	for ( i = 0; i < ARRAY_LEN( cgVerticalAccWeaponOrder ); i++ ) {
		qhandle_t icon;

		icon = CG_GetStartingWeaponIconHandle( cgVerticalAccWeaponOrder[i] );
		if ( !icon ) {
			continue;
		}

		CG_DrawPic( rect->x, rect->y + rect->h * i, rect->w, rect->w, icon );
	}
	trap_R_SetColor( NULL );
}

/*
=============
CG_DrawAccVertical

Draws the retail vertical per-weapon accuracy percentage strip paired with
`CG_WP_VERTICAL` inside the `+acc` stats panel.
=============
*/
static void CG_DrawAccVertical( rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
	char buffer[16];
	int i;

	if ( !rect ) {
		return;
	}

	for ( i = 0; i < ARRAY_LEN( cgVerticalAccWeaponOrder ); i++ ) {
		weapon_t weapon;

		weapon = cgVerticalAccWeaponOrder[i];
		Com_sprintf( buffer, sizeof( buffer ), "%i%%", cg.weaponAccuracies[weapon] );
		CG_Text_Paint( rect->x, rect->y + rect->h * ( i + 1 ), scale, color, buffer, 0, 0, textStyle );
	}
}

/*
=============
CG_DrawTeamPlayerCount

Renders the retail player-count summary string for the specified team.
=============
*/
static void CG_DrawTeamPlayerCount(rectDef_t *rect, float scale, vec4_t color, int textStyle, team_t team, int align) {
	char	buffer[64];
	int		count;
	int		teamLimit;
	float	x;

	count = CG_CountPlayersForTeam( team );
	teamLimit = cgs.playerCountTeamSize;

	switch ( cgs.gametype ) {
	case GT_TEAM:
	case GT_CLAN_ARENA:
	case GT_CTF:
	case GT_1FCTF:
	case GT_HARVESTER:
	case GT_DOMINATION:
	case GT_ATTACK_DEFEND:
		if ( teamLimit > 0 ) {
			Com_sprintf( buffer, sizeof( buffer ), "(%d/%d)", count, teamLimit );
		} else {
			Com_sprintf( buffer, sizeof( buffer ), "(%d)", count );
		}
		break;
	default:
		if ( teamLimit > 0 && teamLimit * 2 <= cgs.maxclients ) {
			Com_sprintf( buffer, sizeof( buffer ), "%d/%d Players", count, teamLimit );
		} else {
			Com_sprintf( buffer, sizeof( buffer ), "%d Player%s", count, ( count == 1 ) ? "" : "s" );
		}
		break;
	}

	x = CG_AlignTextInRectX( rect, scale, buffer, align );
	CG_Text_Paint( x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawTeamTimeoutCount

Displays the aligned timeout count for the given team if known.
=============
*/
static void CG_DrawTeamTimeoutCount( rectDef_t *rect, float scale, vec4_t color, int textStyle, team_t team, int align ) {
	char	buffer[64];
	int		remaining;
	float	x;

	if ( team <= TEAM_FREE || team >= TEAM_NUM_TEAMS ) {
		return;
	}

	remaining = cgs.matchTimeoutRemaining[team];
	Com_sprintf( buffer, sizeof( buffer ), "TO: %d", remaining );
	x = CG_AlignTextInRectX( rect, scale, buffer, align );
	CG_Text_Paint( x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );
}


/*
=============
CG_ClampTeamValue

Normalizes potentially invalid team numbers for HUD calculations.
=============
*/
static team_t CG_ClampTeamValue( int value ) {
	if ( value >= TEAM_RED && value <= TEAM_SPECTATOR ) {
		return (team_t)value;
	}

	return TEAM_FREE;
}

/*
=============
CG_GetRoundTeamCount

Returns the cached round-based team count.
=============
*/
static int CG_GetRoundTeamCount( team_t team ) {
	if ( team <= TEAM_FREE || team >= TEAM_NUM_TEAMS ) {
		return 0;
	}

	return cgs.matchTeamCount[team];
}

/*
=============
CG_DrawClanArenaPlayers

Displays the remaining player count for round-based team modes.
=============
*/
static void CG_DrawClanArenaPlayers(rectDef_t *rect, float scale, vec4_t color, int textStyle, team_t team) {
	char	buffer[64];
	int		count;

	count = CG_GetRoundTeamCount( team );
	Com_sprintf( buffer, sizeof( buffer ), "%d", count );
	CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle);
}

/*
=============
CG_CountDominationOwnedFlags

Counts Domination capture points owned by the specified team.
=============
*/
static int CG_CountDominationOwnedFlags( team_t team ) {
	if ( cgs.gametype != GT_DOMINATION && cgs.gametype != GT_ATTACK_DEFEND ) {
		return 0;
	}

	if ( team <= TEAM_FREE || team >= TEAM_NUM_TEAMS ) {
		return 0;
	}

	return cgs.dominationOwnedPointCount[team];
}

/*
=============
CG_DrawDominationOwnedFlags

Renders the number of Domination points controlled by a team.
=============
*/
static void CG_DrawDominationOwnedFlags(rectDef_t *rect, float scale, vec4_t color, int textStyle, team_t team) {
	char	buffer[64];
	int		owned;

	if ( team <= TEAM_FREE || team >= TEAM_NUM_TEAMS ) {
		return;
	}

	owned = CG_CountDominationOwnedFlags( team );
	Com_sprintf( buffer, sizeof( buffer ), "%d", owned );
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
	vec4_t	drawColor;

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
	Vector4Copy( color, drawColor );
	if ( average >= 80 ) {
		drawColor[0] = 1.0f;
		drawColor[1] = 0.2f;
		drawColor[2] = 0.2f;
	} else if ( average >= 40 ) {
		drawColor[0] = 1.0f;
		drawColor[1] = 0.85f;
		drawColor[2] = 0.2f;
	}

	Com_sprintf( buffer, sizeof( buffer ), "Avg ping %i", average );
	CG_Text_Paint(rect->x, rect->y + rect->h, scale, drawColor, buffer, 0, 0, textStyle);
}

/*
=============
CG_ResolveWeaponName

Maps a local weapon index to the fixed retail best-weapon ownerdraw label.
=============
*/
static const char *CG_ResolveWeaponName( int weapon ) {
	switch ( weapon ) {
	case WP_GAUNTLET:
		return "Gauntlet";
	case WP_MACHINEGUN:
		return "Machine Gun";
	case WP_SHOTGUN:
		return "Shotgun";
	case WP_GRENADE_LAUNCHER:
		return "Grenade";
	case WP_ROCKET_LAUNCHER:
		return "Rocket Launcher";
	case WP_LIGHTNING:
		return "Lightning Gun";
	case WP_RAILGUN:
		return "Rail Gun";
	case WP_PLASMAGUN:
		return "Plasma Gun";
	case WP_BFG:
		return "BFG";
	case WP_NAILGUN:
		return "Nail Gun";
	case WP_PROX_LAUNCHER:
		return "Proximity Mines";
	case WP_CHAINGUN:
		return "Chain Gun";
	case WP_HEAVY_MACHINEGUN:
		return "Heavy Machinegun";
	default:
		return NULL;
	}
}

/*
=============
CG_DrawSelectedPlayerBestWeapon

Prints the best known weapon for the highlighted scoreboard entry.
=============
*/
static void CG_DrawSelectedPlayerBestWeapon(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	const char			*weaponName;
	score_t				*score;
	int					weapon;

	if ( !rect ) {
		return;
	}

	score = CG_GetSelectedScore();
	if ( !rect || !score ) {
		return;
	}

	weapon = score->bestWeapon;
	weaponName = CG_ResolveWeaponName( weapon );
	if ( !weaponName ) {
		return;
	}

	CG_Text_Paint(rect->x, rect->y, scale, color, weaponName, 0, 0, textStyle);
}

/*
=============
CG_DrawProfileModel

Draws a client profile image with the shared retail active/inactive modulation.
=============
*/
static void CG_DrawProfileModel( rectDef_t *rect, int clientNum, qboolean active ) {
	const clientInfo_t	*ci;
	qhandle_t		shader;
	vec4_t			modulate;

	if ( clientNum < 0 || clientNum >= cgs.maxclients ) {
		return;
	}

	ci = &cgs.clientinfo[clientNum];
	if ( !ci->infoValid ) {
		return;
	}

	shader = ci->modelIcon;
	if ( !shader ) {
		shader = CG_GetProfileFallbackShader();
	}
	if ( !shader ) {
		return;
	}

	Vector4Set( modulate, 1.0f, 1.0f, 1.0f, active ? 1.0f : 0.8f );
	trap_R_SetColor( modulate );
	CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );
	trap_R_SetColor( NULL );
}

/*
=============
CG_ClientPreviewWeapon

Resolves the weapon used by the retail tracked-client preview scene.
=============
*/
static int CG_ClientPreviewWeapon( int clientNum ) {
	if ( clientNum == cg.clientNum && cg.snap && cg.snap->ps.clientNum == clientNum ) {
		if ( cg.snap->ps.weapon > WP_NONE && cg.snap->ps.weapon < WP_NUM_WEAPONS ) {
			return cg.snap->ps.weapon;
		}
	}

	if ( clientNum >= 0 && clientNum < MAX_CLIENTS ) {
		const centity_t	*cent;

		cent = &cg_entities[clientNum];
		if ( cent->currentState.weapon > WP_NONE && cent->currentState.weapon < WP_NUM_WEAPONS ) {
			return cent->currentState.weapon;
		}
	}

	return WP_NONE;
}

/*
=============
CG_ClientPreviewTorsoAnimation

Retail uses the alternate torso-attack pose for unarmed or gauntlet previews.
=============
*/
static int CG_ClientPreviewTorsoAnimation( int weapon ) {
	if ( weapon == WP_NONE || weapon == WP_GAUNTLET ) {
		return TORSO_ATTACK2;
	}

	return TORSO_ATTACK;
}

/*
=============
CG_ClientPreviewAnimationFrame

Returns the first frame for a preview animation, falling back to a safe idle
pose when the requested animation is unavailable.
=============
*/
static int CG_ClientPreviewAnimationFrame( const clientInfo_t *ci, int animationNumber, int fallbackAnimationNumber ) {
	if ( !ci ) {
		return 0;
	}

	if ( animationNumber < 0 || animationNumber >= MAX_TOTALANIMATIONS ||
		ci->animations[animationNumber].numFrames <= 0 ) {
		animationNumber = fallbackAnimationNumber;
		if ( animationNumber < 0 || animationNumber >= MAX_TOTALANIMATIONS ||
			ci->animations[animationNumber].numFrames <= 0 ) {
			return 0;
		}
	}

	return ci->animations[animationNumber].firstFrame;
}

/*
=============
CG_InitClientPreviewEntity

Initializes the shared render-entity state used by the client preview scene.
=============
*/
static void CG_InitClientPreviewEntity( refEntity_t *ent, const vec3_t origin, int renderfx ) {
	if ( !ent ) {
		return;
	}

	memset( ent, 0, sizeof( *ent ) );
	VectorCopy( origin, ent->origin );
	VectorCopy( origin, ent->oldorigin );
	VectorCopy( origin, ent->lightingOrigin );
	ent->renderfx = renderfx;
	ent->shaderRGBA[0] = 255;
	ent->shaderRGBA[1] = 255;
	ent->shaderRGBA[2] = 255;
	ent->shaderRGBA[3] = 255;
}

/*
=============
CG_DrawClientModelPreview

Builds the retail first-place or tracked-player preview scene with the full
tagged client model, attached weapon, and preview-only lighting.
=============
*/
static void CG_DrawClientModelPreview( rectDef_t *rect, int clientNum, int weaponNum, const vec3_t previewAngles, qboolean active ) {
	const clientInfo_t	*ci;
	const weaponInfo_t	*weapon;
	refdef_t		refdef;
	refEntity_t		legs;
	refEntity_t		torso;
	refEntity_t		head;
	refEntity_t		gun;
	refEntity_t		barrel;
	refEntity_t		ammo;
	vec3_t			origin;
	vec3_t			lightOrigin;
	float			heightScale;
	float			previewHeight;
	float			screenDistance;
	int			renderfx;
	int			torsoFrame;
	int			legsFrame;

	if ( !rect ) {
		return;
	}

	if ( clientNum < 0 || clientNum >= cgs.maxclients ) {
		return;
	}

	ci = &cgs.clientinfo[clientNum];
	if ( !ci->infoValid || !ci->legsModel || !ci->torsoModel || !ci->headModel ) {
		CG_DrawProfileModel( rect, clientNum, active );
		return;
	}

	if ( rect->w <= 0.0f || rect->h <= 0.0f ) {
		return;
	}

	heightScale = ( ci->headOffset[0] > 0.0f ) ? ci->headOffset[0] : 1.0f;
	previewHeight = 32.0f;
	if ( heightScale > 0.0f ) {
		previewHeight = 32.0f / ( heightScale * 0.85f );
	}

	memset( &refdef, 0, sizeof( refdef ) );
	refdef.rdflags = RDF_NOWORLDMODEL;
	AxisClear( refdef.viewaxis );
	refdef.x = (int)rect->x;
	refdef.y = (int)rect->y;
	refdef.width = (int)rect->w;
	refdef.height = (int)rect->h;
	if ( refdef.width <= 0 || refdef.height <= 0 ) {
		return;
	}

	refdef.fov_x = (float)refdef.width / 640.0f * 90.0f;
	screenDistance = refdef.width / tan( DEG2RAD( refdef.fov_x ) * 0.5f );
	refdef.fov_y = atan2( (float)refdef.height, screenDistance ) * ( 180.0f / (float)M_PI );
	refdef.time = cg.time;

	origin[0] = ( ( previewHeight + 24.0f ) * 1.1f ) / tan( DEG2RAD( refdef.fov_x ) * 0.5f );
	origin[1] = 0.0f;
	origin[2] = ( previewHeight - 24.0f ) * -0.5f;

	renderfx = RF_LIGHTING_ORIGIN | RF_NOSHADOW;
	legsFrame = CG_ClientPreviewAnimationFrame( ci, LEGS_IDLE, TORSO_STAND );
	torsoFrame = CG_ClientPreviewAnimationFrame( ci, CG_ClientPreviewTorsoAnimation( weaponNum ), TORSO_STAND );

	CG_InitClientPreviewEntity( &legs, origin, renderfx );
	legs.hModel = ci->legsModel;
	legs.customSkin = ci->legsSkin;
	AnglesToAxis( previewAngles, legs.axis );
	if ( heightScale != 1.0f ) {
		VectorScale( legs.axis[0], heightScale, legs.axis[0] );
		VectorScale( legs.axis[1], heightScale, legs.axis[1] );
		VectorScale( legs.axis[2], heightScale, legs.axis[2] );
		legs.nonNormalizedAxes = qtrue;
	}
	legs.frame = legsFrame;
	legs.oldframe = legsFrame;
	trap_R_ClearScene();
	trap_R_AddRefEntityToScene( &legs );

	CG_InitClientPreviewEntity( &torso, origin, renderfx );
	torso.hModel = ci->torsoModel;
	torso.customSkin = ci->torsoSkin;
	AxisClear( torso.axis );
	torso.frame = torsoFrame;
	torso.oldframe = torsoFrame;
	CG_PositionRotatedEntityOnTag( &torso, &legs, ci->legsModel, "tag_torso" );
	torso.nonNormalizedAxes = legs.nonNormalizedAxes;
	trap_R_AddRefEntityToScene( &torso );

	CG_InitClientPreviewEntity( &head, origin, renderfx );
	head.hModel = ci->headModel;
	head.customSkin = ci->headSkin;
	AxisClear( head.axis );
	CG_PositionRotatedEntityOnTag( &head, &torso, ci->torsoModel, "tag_head" );
	head.nonNormalizedAxes = torso.nonNormalizedAxes;
	trap_R_AddRefEntityToScene( &head );

	weapon = NULL;
	if ( weaponNum > WP_NONE && weaponNum < WP_NUM_WEAPONS ) {
		CG_RegisterWeapon( weaponNum );
		weapon = &cg_weapons[weaponNum];
	}

	if ( weapon && weapon->weaponModel ) {
		CG_InitClientPreviewEntity( &gun, origin, renderfx );
		gun.hModel = weapon->weaponModel;
		AxisClear( gun.axis );
		CG_PositionEntityOnTag( &gun, &torso, ci->torsoModel, "tag_weapon" );
		gun.nonNormalizedAxes = torso.nonNormalizedAxes;
		trap_R_AddRefEntityToScene( &gun );

		if ( weapon->barrelModel ) {
			vec3_t barrelAngles;

			CG_InitClientPreviewEntity( &barrel, origin, renderfx );
			barrel.hModel = weapon->barrelModel;
			VectorSet( barrelAngles, 0.0f, 0.0f, 0.0f );
			AnglesToAxis( barrelAngles, barrel.axis );
			CG_PositionRotatedEntityOnTag( &barrel, &gun, weapon->weaponModel, "tag_barrel" );
			barrel.nonNormalizedAxes = gun.nonNormalizedAxes;
			trap_R_AddRefEntityToScene( &barrel );
		}

		if ( weaponNum == WP_GRAPPLING_HOOK && weapon->ammoModel ) {
			CG_InitClientPreviewEntity( &ammo, origin, renderfx );
			ammo.hModel = weapon->ammoModel;
			AxisClear( ammo.axis );
			CG_PositionRotatedEntityOnTag( &ammo, &gun, weapon->weaponModel, "tag_ammo" );
			ammo.nonNormalizedAxes = gun.nonNormalizedAxes;
			trap_R_AddRefEntityToScene( &ammo );
		}
	}

	VectorCopy( origin, lightOrigin );
	lightOrigin[0] -= 100.0f;
	lightOrigin[1] += 100.0f;
	lightOrigin[2] += 100.0f;
	trap_R_AddLightToScene( lightOrigin, 500.0f, 1.0f, 1.0f, 1.0f );

	lightOrigin[0] -= 100.0f;
	lightOrigin[1] -= 100.0f;
	lightOrigin[2] -= 100.0f;
	trap_R_AddLightToScene( lightOrigin, 500.0f, 1.0f, 0.0f, 0.0f );

	trap_R_RenderScene( &refdef );
}

/*
=============
CG_DrawFirstPlaceModel

Draws the first-place player profile image for endgame scoreboards.
=============
*/
static void CG_DrawFirstPlaceModel( rectDef_t *rect, qboolean active ) {
	const score_t		*score;
	vec3_t			previewAngles;
	int			weaponNum;

	score = CG_GetActiveScoreByIndex( 0 );
	if ( !score || score->client < 0 || score->client >= cgs.maxclients ) {
		return;
	}

	weaponNum = score->bestWeapon;
	if ( weaponNum <= WP_NONE || weaponNum >= WP_NUM_WEAPONS ) {
		weaponNum = CG_ClientPreviewWeapon( score->client );
	}

	VectorSet( previewAngles, 5.0f, 160.0f, 0.0f );
	CG_DrawClientModelPreview( rect, score->client, weaponNum, previewAngles, active );
}

/*
=============
CG_DrawPlayerModel

Mirrors the retail player-model ownerdraw wrapper for the tracked/local client.
=============
*/
static void CG_DrawPlayerModel( rectDef_t *rect ) {
	int	clientNum;
	int	weaponNum;
	vec3_t	previewAngles;

	clientNum = cg.spectatorTrackedClient;
	if ( clientNum < 0 && cg.snap ) {
		clientNum = cg.snap->ps.clientNum;
	}

	weaponNum = CG_ClientPreviewWeapon( clientNum );
	VectorSet( previewAngles, 5.0f, 210.0f, 0.0f );
	CG_DrawClientModelPreview( rect, clientNum, weaponNum, previewAngles, qtrue );
}

/*
=============
CG_GetTeamPickupOwnerDrawMeta

Resolves team and stat-index metadata for team pickup/time-held ownerdraw IDs.
=============
*/
static qboolean CG_GetTeamPickupOwnerDrawMeta( int ownerDraw, team_t *team, int *statIndex ) {
	int		resolvedStatIndex;
	team_t	resolvedTeam;

	resolvedStatIndex = -1;
	resolvedTeam = TEAM_FREE;

	if ( ownerDraw >= CG_RED_TEAM_MAP_PICKUPS && ownerDraw <= CG_RED_TEAM_TIMEHELD_INVIS ) {
		resolvedTeam = TEAM_RED;
		resolvedStatIndex = ownerDraw - CG_RED_TEAM_MAP_PICKUPS;
	} else if ( ownerDraw >= CG_BLUE_TEAM_MAP_PICKUPS && ownerDraw <= CG_BLUE_TEAM_TIMEHELD_INVIS ) {
		resolvedTeam = TEAM_BLUE;
		resolvedStatIndex = ownerDraw - CG_BLUE_TEAM_MAP_PICKUPS;
	}

	if ( resolvedStatIndex < 0 || resolvedStatIndex >= CG_TEAMSTAT_COUNT ) {
		return qfalse;
	}

	if ( team ) {
		*team = resolvedTeam;
	}
	if ( statIndex ) {
		*statIndex = resolvedStatIndex;
	}

	return qtrue;
}

/*
=============
CG_IsTeamPickupOwnerDraw

Reports whether an ownerdraw is a red/blue team pickup or time-held metric.
=============
*/
static qboolean CG_IsTeamPickupOwnerDraw( int ownerDraw ) {
	return CG_GetTeamPickupOwnerDrawMeta( ownerDraw, NULL, NULL );
}

/*
=============
CG_IsTeamTimeHeldStatIndex

Reports whether a team scorestats field encodes a time-held duration.
=============
*/
static qboolean CG_IsTeamTimeHeldStatIndex( int statIndex ) {
	switch ( statIndex ) {
	case CG_TEAMSTAT_TIMEHELD_QUAD:
	case CG_TEAMSTAT_TIMEHELD_BS:
	case CG_TEAMSTAT_TIMEHELD_FLAG:
	case CG_TEAMSTAT_TIMEHELD_REGEN:
	case CG_TEAMSTAT_TIMEHELD_HASTE:
	case CG_TEAMSTAT_TIMEHELD_INVIS:
		return qtrue;
	default:
		return qfalse;
	}
}

/*
=============
CG_IsTeamTimeHeldOwnerDraw

Reports whether an ownerdraw is one of the retail team time-held slots.
=============
*/
static qboolean CG_IsTeamTimeHeldOwnerDraw( int ownerDraw ) {
	int	statIndex;

	if ( !CG_GetTeamPickupOwnerDrawMeta( ownerDraw, NULL, &statIndex ) ) {
		return qfalse;
	}

	return CG_IsTeamTimeHeldStatIndex( statIndex );
}

typedef enum {
	CG_TEAM_PICKUP_SUMMARY_ICON_RA = 0,
	CG_TEAM_PICKUP_SUMMARY_ICON_YA,
	CG_TEAM_PICKUP_SUMMARY_ICON_GA,
	CG_TEAM_PICKUP_SUMMARY_ICON_MH,
	CG_TEAM_PICKUP_SUMMARY_ICON_MEDKIT,
	CG_TEAM_PICKUP_SUMMARY_ICON_FLAG,
	CG_TEAM_PICKUP_SUMMARY_ICON_QUAD,
	CG_TEAM_PICKUP_SUMMARY_ICON_BS,
	CG_TEAM_PICKUP_SUMMARY_ICON_REGEN,
	CG_TEAM_PICKUP_SUMMARY_ICON_HASTE,
	CG_TEAM_PICKUP_SUMMARY_ICON_INVIS,
	CG_TEAM_PICKUP_SUMMARY_ICON_COUNT
} cgTeamPickupSummaryIcon_t;

typedef struct {
	int				statIndex;
	int				timeHeldStatIndex;
	cgTeamPickupSummaryIcon_t	icon;
	int				countTextOffsetX;
} cgTeamPickupSummaryEntry_t;

static const cgTeamPickupSummaryEntry_t cgTeamPickupSummaryEntries[] = {
	{ CG_TEAMSTAT_PICKUPS_RA, -1, CG_TEAM_PICKUP_SUMMARY_ICON_RA, 14 },
	{ CG_TEAMSTAT_PICKUPS_YA, -1, CG_TEAM_PICKUP_SUMMARY_ICON_YA, 11 },
	{ CG_TEAMSTAT_PICKUPS_GA, -1, CG_TEAM_PICKUP_SUMMARY_ICON_GA, 14 },
	{ CG_TEAMSTAT_PICKUPS_MH, -1, CG_TEAM_PICKUP_SUMMARY_ICON_MH, 14 },
	{ CG_TEAMSTAT_PICKUPS_MEDKIT, -1, CG_TEAM_PICKUP_SUMMARY_ICON_MEDKIT, 14 },
	{ CG_TEAMSTAT_PICKUPS_FLAG, CG_TEAMSTAT_TIMEHELD_FLAG, CG_TEAM_PICKUP_SUMMARY_ICON_FLAG, 14 },
	{ CG_TEAMSTAT_PICKUPS_QUAD, CG_TEAMSTAT_TIMEHELD_QUAD, CG_TEAM_PICKUP_SUMMARY_ICON_QUAD, 14 },
	{ CG_TEAMSTAT_PICKUPS_BS, CG_TEAMSTAT_TIMEHELD_BS, CG_TEAM_PICKUP_SUMMARY_ICON_BS, 14 },
	{ CG_TEAMSTAT_PICKUPS_REGEN, CG_TEAMSTAT_TIMEHELD_REGEN, CG_TEAM_PICKUP_SUMMARY_ICON_REGEN, 14 },
	{ CG_TEAMSTAT_PICKUPS_HASTE, CG_TEAMSTAT_TIMEHELD_HASTE, CG_TEAM_PICKUP_SUMMARY_ICON_HASTE, 14 },
	{ CG_TEAMSTAT_PICKUPS_INVIS, CG_TEAMSTAT_TIMEHELD_INVIS, CG_TEAM_PICKUP_SUMMARY_ICON_INVIS, 14 }
};

static qhandle_t cgTeamPickupSummaryIconHandles[CG_TEAM_PICKUP_SUMMARY_ICON_COUNT];
static qhandle_t cgTeamPickupSummaryBlueFlagHandle;
static qhandle_t cgTeamPickupSummaryNeutralFlagHandle;
static qhandle_t cgTeamPickupSummaryRedFlagHandle;

/*
=============
CG_IsTeamPickupSummaryOwnerDraw

Reports whether an ownerdraw is one of the retail aggregate team pickup rows.
=============
*/
static qboolean CG_IsTeamPickupSummaryOwnerDraw( int ownerDraw ) {
	return (qboolean)( ownerDraw == CG_RED_TEAM_MAP_PICKUPS || ownerDraw == CG_BLUE_TEAM_MAP_PICKUPS );
}

/*
=============
CG_GetTeamScoreStatValue

Reads a parsed retail team scorestat field for the requested team/stat pair.
=============
*/
static qboolean CG_GetTeamScoreStatValue( team_t team, int statIndex, int *value ) {
	int	teamIndex;
	int	resolvedValue;

	if ( !value ) {
		return qfalse;
	}
	if ( team != TEAM_RED && team != TEAM_BLUE ) {
		return qfalse;
	}
	if ( statIndex < 0 || statIndex >= CG_TEAMSTAT_COUNT ) {
		return qfalse;
	}
	if ( !cg.teamScoreStats.valid ) {
		return qfalse;
	}
	if ( cg.teamScoreStats.fieldCount <= 0 || statIndex >= cg.teamScoreStats.fieldCount ) {
		return qfalse;
	}

	teamIndex = ( team == TEAM_RED ) ? 0 : 1;
	resolvedValue = cg.teamScoreStats.values[teamIndex][statIndex];
	if ( resolvedValue < 0 ) {
		resolvedValue = 0;
	}

	*value = resolvedValue;
	return qtrue;
}

/*
=============
CG_GetTeamPickupSummaryIconHandle

Lazily resolves the retail scoreboard pickup-strip shader for the requested
team/icon slot.
=============
*/
static qhandle_t CG_GetTeamPickupSummaryIconHandle( team_t team, cgTeamPickupSummaryIcon_t icon ) {
	const char	*shaderName;
	qhandle_t	*handle;

	shaderName = NULL;
	handle = NULL;

	switch ( icon ) {
	case CG_TEAM_PICKUP_SUMMARY_ICON_RA:
		shaderName = "pickup_RA";
		handle = &cgTeamPickupSummaryIconHandles[icon];
		break;
	case CG_TEAM_PICKUP_SUMMARY_ICON_YA:
		shaderName = "pickup_YA";
		handle = &cgTeamPickupSummaryIconHandles[icon];
		break;
	case CG_TEAM_PICKUP_SUMMARY_ICON_GA:
		shaderName = "pickup_GA";
		handle = &cgTeamPickupSummaryIconHandles[icon];
		break;
	case CG_TEAM_PICKUP_SUMMARY_ICON_MH:
		shaderName = "pickup_MH";
		handle = &cgTeamPickupSummaryIconHandles[icon];
		break;
	case CG_TEAM_PICKUP_SUMMARY_ICON_MEDKIT:
		shaderName = "pickup_MK";
		handle = &cgTeamPickupSummaryIconHandles[icon];
		break;
	case CG_TEAM_PICKUP_SUMMARY_ICON_QUAD:
		shaderName = "pickup_QUAD";
		handle = &cgTeamPickupSummaryIconHandles[icon];
		break;
	case CG_TEAM_PICKUP_SUMMARY_ICON_BS:
		shaderName = "pickup_BS";
		handle = &cgTeamPickupSummaryIconHandles[icon];
		break;
	case CG_TEAM_PICKUP_SUMMARY_ICON_REGEN:
		shaderName = "pickup_REGEN";
		handle = &cgTeamPickupSummaryIconHandles[icon];
		break;
	case CG_TEAM_PICKUP_SUMMARY_ICON_HASTE:
		shaderName = "pickup_HASTE";
		handle = &cgTeamPickupSummaryIconHandles[icon];
		break;
	case CG_TEAM_PICKUP_SUMMARY_ICON_INVIS:
		shaderName = "pickup_INVIS";
		handle = &cgTeamPickupSummaryIconHandles[icon];
		break;
	case CG_TEAM_PICKUP_SUMMARY_ICON_FLAG:
		if ( cgs.gametype == GT_1FCTF ) {
			shaderName = "pickup_NTRLFLAG";
			handle = &cgTeamPickupSummaryNeutralFlagHandle;
		} else if ( team == TEAM_RED ) {
			shaderName = "pickup_BLUEFLAG";
			handle = &cgTeamPickupSummaryBlueFlagHandle;
		} else if ( team == TEAM_BLUE ) {
			shaderName = "pickup_REDFLAG";
			handle = &cgTeamPickupSummaryRedFlagHandle;
		}
		break;
	default:
		break;
	}

	if ( !handle || !shaderName ) {
		return 0;
	}
	if ( !*handle ) {
		*handle = trap_R_RegisterShaderNoMip( shaderName );
	}

	return *handle;
}

/*
=============
CG_DrawTeamPickupSummaryOwnerDraw

Reconstructs the retail aggregate pickup strip for `CG_RED_TEAM_MAP_PICKUPS`
and `CG_BLUE_TEAM_MAP_PICKUPS`.
=============
*/
static void CG_DrawTeamPickupSummaryOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	team_t	team;
	float	drawX;
	float	drawY;
	int	i;

	if ( !rect ) {
		return;
	}
	if ( ownerDraw == CG_RED_TEAM_MAP_PICKUPS ) {
		team = TEAM_RED;
	} else if ( ownerDraw == CG_BLUE_TEAM_MAP_PICKUPS ) {
		team = TEAM_BLUE;
	} else {
		return;
	}

	drawX = (float)(int)rect->x;
	drawY = (float)(int)rect->y;
	trap_R_SetColor( NULL );

	for ( i = 0; i < ARRAY_LEN( cgTeamPickupSummaryEntries ); i++ ) {
		const cgTeamPickupSummaryEntry_t	*entry;
		qhandle_t			iconHandle;
		int				pickupCount;

		entry = &cgTeamPickupSummaryEntries[i];
		if ( !CG_GetTeamScoreStatValue( team, entry->statIndex, &pickupCount ) || pickupCount <= 0 ) {
			continue;
		}

		iconHandle = CG_GetTeamPickupSummaryIconHandle( team, entry->icon );
		if ( !iconHandle ) {
			continue;
		}

		if ( entry->timeHeldStatIndex >= 0 ) {
			char	countText[16];
			char	timeText[16];
			int	timeHeld;

			timeHeld = 0;
			CG_GetTeamScoreStatValue( team, entry->timeHeldStatIndex, &timeHeld );

			CG_DrawPic( drawX, drawY - 7.0f, rect->w, rect->h, iconHandle );
			Com_sprintf( countText, sizeof( countText ), "%i", pickupCount );
			CG_Text_Paint( drawX + entry->countTextOffsetX, drawY + 8.0f, scale, color, countText, 0, 0, textStyle );
			if ( timeHeld > 0 ) {
				Q_strncpyz( timeText, CG_FormatMinutesSeconds( timeHeld ), sizeof( timeText ) );
			} else {
				Q_strncpyz( timeText, "-", sizeof( timeText ) );
			}
			CG_Text_Paint( drawX + 2.0f, drawY + 15.0f, scale, color, timeText, 0, 0, textStyle );
			drawX += 28.0f;
		} else {
			char	countText[16];

			CG_DrawPic( drawX, drawY, rect->w, rect->h, iconHandle );
			Com_sprintf( countText, sizeof( countText ), "%i", pickupCount );
			CG_Text_Paint( drawX + entry->countTextOffsetX, drawY + 15.0f, scale, color, countText, 0, 0, textStyle );
			drawX += 25.0f;
		}
	}
}

/*
=============
CG_BuildTeamPickupText

Builds team pickup-count ownerdraw text from parsed scorestats_team payloads.
=============
*/
static qboolean CG_BuildTeamPickupText( int ownerDraw, char *buffer, size_t bufferSize ) {
	team_t	team;
	int	statIndex;
	int	teamIndex;
	int	value;

	if ( !buffer || bufferSize <= 0 ) {
		return qfalse;
	}

	if ( !CG_GetTeamPickupOwnerDrawMeta( ownerDraw, &team, &statIndex ) ) {
		return qfalse;
	}
	if ( !cg.teamScoreStats.valid ) {
		return qfalse;
	}
	if ( cg.teamScoreStats.fieldCount <= 0 ) {
		return qfalse;
	}
	if ( statIndex < 0 || statIndex >= cg.teamScoreStats.fieldCount ) {
		return qfalse;
	}

	teamIndex = ( team == TEAM_RED ) ? 0 : 1;
	value = cg.teamScoreStats.values[teamIndex][statIndex];
	if ( value < 0 ) {
		value = 0;
	}
	if ( statIndex >= cg.teamScoreStats.fieldCount ) {
		return qfalse;
	}

	Com_sprintf( buffer, bufferSize, "%i", value );
	return qtrue;
}

/*
=============
CG_DrawTeamPickupOwnerDraw

Draws the current team pickup-count value for team scoreboard ownerdraws.
=============
*/
static void CG_DrawTeamPickupOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	char	buffer[32];

	if ( CG_IsTeamPickupSummaryOwnerDraw( ownerDraw ) ) {
		CG_DrawTeamPickupSummaryOwnerDraw( rect, scale, color, textStyle, ownerDraw );
		return;
	}

	if ( !CG_BuildTeamPickupText( ownerDraw, buffer, sizeof( buffer ) ) ) {
		return;
	}

	CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_BuildTeamTimeHeldText

Formats retail team time-held stats as `m:ss`.
=============
*/
static qboolean CG_BuildTeamTimeHeldText( int ownerDraw, char *buffer, size_t bufferSize ) {
	team_t	team;
	int	statIndex;
	int	value;

	if ( !buffer || bufferSize <= 0 ) {
		return qfalse;
	}

	if ( !CG_IsTeamTimeHeldOwnerDraw( ownerDraw ) ) {
		return qfalse;
	}

	if ( !CG_GetTeamPickupOwnerDrawMeta( ownerDraw, &team, &statIndex ) ) {
		return qfalse;
	}
	if ( !CG_GetTeamScoreStatValue( team, statIndex, &value ) ) {
		Q_strncpyz( buffer, "-", bufferSize );
		return qtrue;
	}

	Q_strncpyz( buffer, CG_FormatMinutesSeconds( value ), bufferSize );
	return qtrue;
}

/*
=============
CG_DrawTeamTimeHeldOwnerDraw

Draws the retail team time-held ownerdraw text for powerup pickups.
=============
*/
static void CG_DrawTeamTimeHeldOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	char	buffer[32];

	if ( !CG_BuildTeamTimeHeldText( ownerDraw, buffer, sizeof( buffer ) ) ) {
		return;
	}

	CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_GetPlacementScore

Returns the active scoreboard row for first/second place ownerdraws.
=============
*/
static const score_t *CG_GetPlacementScore( int slot ) {
	return CG_GetActiveScoreByIndex( slot );
}

/*
=============
CG_GetPlacementClientInfo

Resolves client info for a placement score row.
=============
*/
static const clientInfo_t *CG_GetPlacementClientInfo( const score_t *score ) {
	if ( !score ) {
		return NULL;
	}

	if ( score->client < 0 || score->client >= cgs.maxclients || score->client >= MAX_CLIENTS ) {
		return NULL;
	}

	return &cgs.clientinfo[score->client];
}

/*
=============
CG_ResolvePlacementMetricOwnerDraw

Maps first/second-place placement ownerdraw ids to a score slot and normalized
ownerdraw family.
=============
*/
static qboolean CG_ResolvePlacementMetricOwnerDraw( int ownerDraw, int *slot, int *normalized ) {
	int	resolvedSlot;
	int	resolvedOwnerDraw;

	resolvedSlot = -1;
	resolvedOwnerDraw = ownerDraw;

	if ( ownerDraw >= CG_1ST_PLYR_READY && ownerDraw <= CG_1ST_PLYR_TIER ) {
		resolvedSlot = 0;
	} else if ( ownerDraw >= CG_2ND_PLYR_READY && ownerDraw <= CG_2ND_PLYR_TIER ) {
		resolvedSlot = 1;
		resolvedOwnerDraw = ownerDraw - ( CG_2ND_PLYR - CG_1ST_PLYR );
	}

	if ( slot ) {
		*slot = resolvedSlot;
	}
	if ( normalized ) {
		*normalized = resolvedOwnerDraw;
	}

	return ( resolvedSlot >= 0 ) ? qtrue : qfalse;
}

/*
=============
CG_GetPlacementMetricWeapon

Returns the weapon referenced by a retail placement per-weapon ownerdraw.
=============
*/
static weapon_t CG_GetPlacementMetricWeapon( int ownerDraw ) {
	int normalized;

	normalized = ownerDraw;
	if ( ownerDraw >= CG_2ND_PLYR_FRAGS_G && ownerDraw <= CG_2ND_PLYR_ACC_HMG ) {
		normalized = ownerDraw - ( CG_2ND_PLYR - CG_1ST_PLYR );
	}

	switch ( normalized ) {
	case CG_1ST_PLYR_FRAGS_G:
	case CG_1ST_PLYR_DMG_G:
		return WP_GAUNTLET;
	case CG_1ST_PLYR_FRAGS_MG:
	case CG_1ST_PLYR_HITS_MG:
	case CG_1ST_PLYR_SHOTS_MG:
	case CG_1ST_PLYR_DMG_MG:
	case CG_1ST_PLYR_ACC_MG:
		return WP_MACHINEGUN;
	case CG_1ST_PLYR_FRAGS_SG:
	case CG_1ST_PLYR_HITS_SG:
	case CG_1ST_PLYR_SHOTS_SG:
	case CG_1ST_PLYR_DMG_SG:
	case CG_1ST_PLYR_ACC_SG:
		return WP_SHOTGUN;
	case CG_1ST_PLYR_FRAGS_GL:
	case CG_1ST_PLYR_HITS_GL:
	case CG_1ST_PLYR_SHOTS_GL:
	case CG_1ST_PLYR_DMG_GL:
	case CG_1ST_PLYR_ACC_GL:
		return WP_GRENADE_LAUNCHER;
	case CG_1ST_PLYR_FRAGS_RL:
	case CG_1ST_PLYR_HITS_RL:
	case CG_1ST_PLYR_SHOTS_RL:
	case CG_1ST_PLYR_DMG_RL:
	case CG_1ST_PLYR_ACC_RL:
		return WP_ROCKET_LAUNCHER;
	case CG_1ST_PLYR_FRAGS_LG:
	case CG_1ST_PLYR_HITS_LG:
	case CG_1ST_PLYR_SHOTS_LG:
	case CG_1ST_PLYR_DMG_LG:
	case CG_1ST_PLYR_ACC_LG:
		return WP_LIGHTNING;
	case CG_1ST_PLYR_FRAGS_RG:
	case CG_1ST_PLYR_HITS_RG:
	case CG_1ST_PLYR_SHOTS_RG:
	case CG_1ST_PLYR_DMG_RG:
	case CG_1ST_PLYR_ACC_RG:
		return WP_RAILGUN;
	case CG_1ST_PLYR_FRAGS_PG:
	case CG_1ST_PLYR_HITS_PG:
	case CG_1ST_PLYR_SHOTS_PG:
	case CG_1ST_PLYR_DMG_PG:
	case CG_1ST_PLYR_ACC_PG:
		return WP_PLASMAGUN;
	case CG_1ST_PLYR_FRAGS_BFG:
	case CG_1ST_PLYR_HITS_BFG:
	case CG_1ST_PLYR_SHOTS_BFG:
	case CG_1ST_PLYR_DMG_BFG:
	case CG_1ST_PLYR_ACC_BFG:
		return WP_BFG;
	case CG_1ST_PLYR_FRAGS_CG:
	case CG_1ST_PLYR_HITS_CG:
	case CG_1ST_PLYR_SHOTS_CG:
	case CG_1ST_PLYR_DMG_CG:
	case CG_1ST_PLYR_ACC_CG:
		return WP_CHAINGUN;
	case CG_1ST_PLYR_FRAGS_NG:
	case CG_1ST_PLYR_HITS_NG:
	case CG_1ST_PLYR_SHOTS_NG:
	case CG_1ST_PLYR_DMG_NG:
	case CG_1ST_PLYR_ACC_NG:
		return WP_NAILGUN;
	case CG_1ST_PLYR_FRAGS_PL:
	case CG_1ST_PLYR_HITS_PL:
	case CG_1ST_PLYR_SHOTS_PL:
	case CG_1ST_PLYR_DMG_PL:
	case CG_1ST_PLYR_ACC_PL:
		return WP_PROX_LAUNCHER;
	case CG_1ST_PLYR_FRAGS_HMG:
	case CG_1ST_PLYR_HITS_HMG:
	case CG_1ST_PLYR_SHOTS_HMG:
	case CG_1ST_PLYR_DMG_HMG:
	case CG_1ST_PLYR_ACC_HMG:
		return WP_HEAVY_MACHINEGUN;
	default:
		return WP_NONE;
	}
}

/*
=============
CG_GetPlacementScoreStats

Returns parsed per-weapon score stats for the supplied placement row.
=============
*/
static const cgScoreStats_t *CG_GetPlacementScoreStats( const score_t *score ) {
	if ( !score ) {
		return NULL;
	}

	if ( score->client < 0 || score->client >= cgs.maxclients || score->client >= MAX_CLIENTS ) {
		return NULL;
	}

	if ( !cg.scoreStats[score->client].valid ) {
		return NULL;
	}

	return &cg.scoreStats[score->client];
}

/*
=============
CG_BuildPlacementWeaponMetricText

Builds per-weapon first/second placement ownerdraw text from parsed scorestats payloads.
=============
*/
static qboolean CG_BuildPlacementWeaponMetricText( int ownerDraw, const score_t *score, char *buffer, size_t bufferSize ) {
	const cgScoreStats_t	*stats;
	weapon_t		weapon;
	int			normalized;

	if ( !score || !buffer || bufferSize <= 0 ) {
		return qfalse;
	}

	normalized = ownerDraw;
	if ( ownerDraw >= CG_2ND_PLYR_FRAGS_G && ownerDraw <= CG_2ND_PLYR_ACC_HMG ) {
		normalized = ownerDraw - ( CG_2ND_PLYR - CG_1ST_PLYR );
	}

	weapon = CG_GetPlacementMetricWeapon( ownerDraw );
	if ( weapon == WP_NONE ) {
		return qfalse;
	}

	stats = CG_GetPlacementScoreStats( score );
	if ( !stats ) {
		Q_strncpyz( buffer, "-", bufferSize );
		return qtrue;
	}

	if ( normalized >= CG_1ST_PLYR_FRAGS_G && normalized <= CG_1ST_PLYR_FRAGS_HMG ) {
		Com_sprintf( buffer, bufferSize, "%i", stats->weaponFrags[weapon] );
		return qtrue;
	}

	if ( normalized >= CG_1ST_PLYR_HITS_MG && normalized <= CG_1ST_PLYR_HITS_HMG ) {
		Com_sprintf( buffer, bufferSize, "%i", stats->weaponHits[weapon] );
		return qtrue;
	}

	if ( normalized >= CG_1ST_PLYR_SHOTS_MG && normalized <= CG_1ST_PLYR_SHOTS_HMG ) {
		Com_sprintf( buffer, bufferSize, "%i", stats->weaponShots[weapon] );
		return qtrue;
	}

	if ( normalized >= CG_1ST_PLYR_DMG_G && normalized <= CG_1ST_PLYR_DMG_HMG ) {
		Com_sprintf( buffer, bufferSize, "%i", stats->weaponDamage[weapon] );
		return qtrue;
	}

	if ( normalized >= CG_1ST_PLYR_ACC_MG && normalized <= CG_1ST_PLYR_ACC_HMG ) {
		Com_sprintf( buffer, bufferSize, "%i%%", stats->weaponAccuracy[weapon] );
		return qtrue;
	}

	return qfalse;
}

/*
=============
CG_BuildPlacementPickupMetricText

Builds placement pickup-count and average-interval ownerdraw text from scorestats.
=============
*/
static qboolean CG_BuildPlacementPickupMetricText( int ownerDraw, const score_t *score, char *buffer, size_t bufferSize ) {
	const cgScoreStats_t	*stats;
	int			index;
	int			normalized;

	if ( !score || !buffer || bufferSize <= 0 ) {
		return qfalse;
	}

	normalized = ownerDraw;
	CG_ResolvePlacementMetricOwnerDraw( ownerDraw, NULL, &normalized );

	if ( normalized < CG_1ST_PLYR_PICKUPS || normalized > CG_1ST_PLYR_AVG_PICKUP_TIME_MH ) {
		return qfalse;
	}

	stats = CG_GetPlacementScoreStats( score );
	if ( !stats ) {
		Q_strncpyz( buffer, "-", bufferSize );
		return qtrue;
	}

	if ( normalized == CG_1ST_PLYR_PICKUPS ) {
		int total;

		total = 0;
		for ( index = 0; index < CG_SCORESTAT_PICKUP_COUNT; index++ ) {
			total += stats->pickupCounts[index];
		}
		Com_sprintf( buffer, bufferSize, "%i", total );
		return qtrue;
	}

	if ( normalized >= CG_1ST_PLYR_PICKUPS_RA && normalized <= CG_1ST_PLYR_PICKUPS_MH ) {
		index = normalized - CG_1ST_PLYR_PICKUPS_RA;
		Com_sprintf( buffer, bufferSize, "%i", stats->pickupCounts[index] );
		return qtrue;
	}

	if ( normalized >= CG_1ST_PLYR_AVG_PICKUP_TIME_RA && normalized <= CG_1ST_PLYR_AVG_PICKUP_TIME_MH ) {
		index = normalized - CG_1ST_PLYR_AVG_PICKUP_TIME_RA;
		if ( stats->pickupCounts[index] <= 0 ) {
			buffer[0] = '\0';
		} else {
			Com_sprintf( buffer, bufferSize, "%3.2f", stats->pickupAvgSeconds[index] );
		}
		return qtrue;
	}

	return qfalse;
}

/*
=============
CG_GetPlacementFragCount

Returns the frag tally for placement ownerdraws. Retail team-family scoreboard
rows publish kills separately from the score column, while legacy layouts still
use score as the visible frag count.
=============
*/
static int CG_GetPlacementFragCount( const score_t *score ) {
	if ( !score ) {
		return 0;
	}

	switch ( cgs.gametype ) {
	case GT_TEAM:
	case GT_CTF:
	case GT_1FCTF:
	case GT_HARVESTER:
	case GT_DOMINATION:
	case GT_ATTACK_DEFEND:
	case GT_FREEZE:
		return score->kills;
	default:
		return score->score;
	}
}

/*
=============
cgSpectatorStatus_t

Retail status-image states for the first/second-player duel scorebox slots.
=============
*/
typedef enum {
	CG_SPECTATOR_STATUS_READY,
	CG_SPECTATOR_STATUS_NOTREADY,
	CG_SPECTATOR_STATUS_LEADS,
	CG_SPECTATOR_STATUS_TIED,
	CG_SPECTATOR_STATUS_TRAILS
} cgSpectatorStatus_t;

/*
=============
CG_ClientReadyForScoreboxStatus

Reports whether a client is marked ready in the snapshot bitmask consumed by
warmup and intermission scorebox status ownerdraws.
=============
*/
static qboolean CG_ClientReadyForScoreboxStatus( int clientNum ) {
	if ( !cg.snap ) {
		return qfalse;
	}

	if ( clientNum < 0 || clientNum >= 32 ) {
		return qfalse;
	}

	return ( cg.snap->ps.stats[STAT_CLIENTS_READY] & ( 1 << clientNum ) ) ? qtrue : qfalse;
}

/*
=============
CG_GetSpectatorStatusShader

Returns the retail first/second-player status backing image for the requested
scorebox state.
=============
*/
static qhandle_t CG_GetSpectatorStatusShader( int slot, cgSpectatorStatus_t status ) {
	if ( slot == 0 ) {
		switch ( status ) {
		case CG_SPECTATOR_STATUS_READY:
			return cgs.media.scoreFirstPlayerReadyShader;
		case CG_SPECTATOR_STATUS_LEADS:
			return cgs.media.scoreFirstPlayerLeadsShader;
		case CG_SPECTATOR_STATUS_TIED:
			return cgs.media.scoreFirstPlayerTiedShader;
		case CG_SPECTATOR_STATUS_TRAILS:
			return cgs.media.scoreFirstPlayerTrailsShader;
		case CG_SPECTATOR_STATUS_NOTREADY:
		default:
			return cgs.media.scoreFirstPlayerNotReadyShader;
		}
	}

	if ( slot == 1 ) {
		switch ( status ) {
		case CG_SPECTATOR_STATUS_READY:
			return cgs.media.scoreSecondPlayerReadyShader;
		case CG_SPECTATOR_STATUS_LEADS:
			return cgs.media.scoreSecondPlayerLeadsShader;
		case CG_SPECTATOR_STATUS_TIED:
			return cgs.media.scoreSecondPlayerTiedShader;
		case CG_SPECTATOR_STATUS_TRAILS:
			return cgs.media.scoreSecondPlayerTrailsShader;
		case CG_SPECTATOR_STATUS_NOTREADY:
		default:
			return cgs.media.scoreSecondPlayerNotReadyShader;
		}
	}

	return 0;
}

/*
=============
CG_BuildSpectatorStatusText

Builds the retail duel scorebox status text and backing image for the requested
slot.
=============
*/
static qboolean CG_BuildSpectatorStatusText( int slot, char *buffer, size_t bufferSize, qhandle_t *shader ) {
	const score_t	*score;
	cgSpectatorStatus_t	status;
	qboolean		liveDuel;

	if ( !buffer || bufferSize <= 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	status = CG_SPECTATOR_STATUS_NOTREADY;
	score = CG_SpectatorClientScore( slot );
	if ( !score ) {
		if ( cgs.gametype != GT_TOURNAMENT ) {
			return qfalse;
		}
		if ( shader ) {
			*shader = CG_GetSpectatorStatusShader( slot, status );
		}
		return qtrue;
	}

	liveDuel = ( cgs.gametype == GT_TOURNAMENT && cg.warmup == 0 && cg.snap &&
		cg.snap->ps.pm_type != PM_INTERMISSION ) ? qtrue : qfalse;
	if ( liveDuel ) {
		if ( cgs.scores1 == cgs.scores2 ) {
			Q_strncpyz( buffer, "TIED", bufferSize );
			status = CG_SPECTATOR_STATUS_TIED;
		} else if ( ( slot == 0 && cgs.scores1 > cgs.scores2 ) || ( slot == 1 && cgs.scores2 > cgs.scores1 ) ) {
			Q_strncpyz( buffer, "LEADS", bufferSize );
			status = CG_SPECTATOR_STATUS_LEADS;
		} else {
			Q_strncpyz( buffer, "TRAILS", bufferSize );
			status = CG_SPECTATOR_STATUS_TRAILS;
		}

		if ( shader ) {
			*shader = CG_GetSpectatorStatusShader( slot, status );
		}
		return qtrue;
	}

	if ( CG_ClientReadyForScoreboxStatus( score->client ) ) {
		Q_strncpyz( buffer, "READY", bufferSize );
		status = CG_SPECTATOR_STATUS_READY;
	} else {
		Q_strncpyz( buffer, "NOT READY", bufferSize );
		status = CG_SPECTATOR_STATUS_NOTREADY;
	}

	if ( shader ) {
		*shader = CG_GetSpectatorStatusShader( slot, status );
	}

	return qtrue;
}

/*
=============
CG_DrawSpectatorStatusLabel

Paints the retail duel scorebox status label for the requested tracked slot.
=============
*/
static void CG_DrawSpectatorStatusLabel( rectDef_t *rect, int slot ) {
	char	buffer[16];
	qhandle_t	shader;
	float	x;

	if ( !rect || !CG_BuildSpectatorStatusText( slot, buffer, sizeof( buffer ), &shader ) ) {
		return;
	}

	if ( shader ) {
		CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );
	}

	x = rect->x + ( rect->w - CG_Text_Width( buffer, 0.16f, 0 ) ) * 0.5f;
	CG_Text_Paint( x, rect->y + rect->h, 0.16f, colorWhite, buffer, 0, 0, 3 );
}

/*
=============
CG_DrawSpectatorPrimaryStatus

Draws the retail primary duel scorebox status label.
=============
*/
static void CG_DrawSpectatorPrimaryStatus( rectDef_t *rect ) {
	CG_DrawSpectatorStatusLabel( rect, 0 );
}

/*
=============
CG_DrawSpectatorSecondaryStatus

Draws the retail secondary duel scorebox status label.
=============
*/
static void CG_DrawSpectatorSecondaryStatus( rectDef_t *rect ) {
	CG_DrawSpectatorStatusLabel( rect, 1 );
}

/*
=============
CG_BuildPlacementMetricText

Builds a text payload for first/second place metric ownerdraws.
=============
*/
static qboolean CG_BuildPlacementMetricText( int ownerDraw, const score_t *score, const clientInfo_t *ci, char *buffer, size_t bufferSize ) {
	int normalized;

	if ( !score || !ci || !buffer || bufferSize <= 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	normalized = ownerDraw;
	CG_ResolvePlacementMetricOwnerDraw( ownerDraw, NULL, &normalized );

	switch ( normalized ) {
	case CG_1ST_PLYR_SCORE:
	case CG_1ST_PLYR_AVATAR:
	case CG_1ST_PLYR_HEALTH_ARMOR:
		return qfalse;
	case CG_1ST_PLYR_READY:
		return qfalse;
	case CG_1ST_PLYR_FRAGS:
		Com_sprintf( buffer, bufferSize, "%i", CG_GetPlacementFragCount( score ) );
		return qtrue;
	case CG_1ST_PLYR_DEATHS:
		Com_sprintf( buffer, bufferSize, "%i", score->deaths );
		return qtrue;
	case CG_1ST_PLYR_DMG:
		Com_sprintf( buffer, bufferSize, "%i", score->damage );
		return qtrue;
	case CG_1ST_PLYR_PING:
		Com_sprintf( buffer, bufferSize, "%i", score->ping );
		return qtrue;
	case CG_1ST_PLYR_WINS:
		Com_sprintf( buffer, bufferSize, "%i", ci->wins );
		return qtrue;
	case CG_1ST_PLYR_ACC:
		Com_sprintf( buffer, bufferSize, "%i%%", score->accuracy );
		return qtrue;
	case CG_1ST_PLYR_FLAG:
		return qfalse;
	case CG_1ST_PLYR_EXCELLENT:
		Com_sprintf( buffer, bufferSize, "%i", score->excellentCount );
		return qtrue;
	case CG_1ST_PLYR_IMPRESSIVE:
		Com_sprintf( buffer, bufferSize, "%i", score->impressiveCount );
		return qtrue;
	case CG_1ST_PLYR_HUMILIATION:
		Com_sprintf( buffer, bufferSize, "%i", score->guantletCount );
		return qtrue;
	default:
		break;
	}

	if ( CG_BuildPlacementWeaponMetricText( normalized, score, buffer, bufferSize ) ) {
		return qtrue;
	}

	if ( CG_BuildPlacementPickupMetricText( normalized, score, buffer, bufferSize ) ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
CG_DrawPlacementMetricTextOwnerDraw

Paints a retail placement metric ownerdraw through the shared scorebox text
builder.
=============
*/
static qboolean CG_DrawPlacementMetricTextOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	const score_t		*score;
	const clientInfo_t	*ci;
	char			buffer[64];
	int			normalized;
	int			slot;

	if ( !rect || !CG_ResolvePlacementMetricOwnerDraw( ownerDraw, &slot, &normalized ) ) {
		return qfalse;
	}

	score = CG_GetPlacementScore( slot );
	ci = CG_GetPlacementClientInfo( score );
	if ( !score || !ci ) {
		return qfalse;
	}

	if ( !CG_BuildPlacementMetricText( normalized, score, ci, buffer, sizeof( buffer ) ) ) {
		return qfalse;
	}

	CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );
	return qtrue;
}

/*
=============
CG_DrawPlacementFragsOwnerDraw

Draws the tracked frag count for a placement scorebox slot.
=============
*/
static qboolean CG_DrawPlacementFragsOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot ) {
	const score_t *score;
	char buffer[32];

	if ( !rect ) {
		return qfalse;
	}

	score = CG_GetPlacementScore( slot );
	if ( !score ) {
		return qfalse;
	}

	Com_sprintf( buffer, sizeof( buffer ), "%i", CG_GetPlacementFragCount( score ) );
	CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );
	return qtrue;
}

/*
=============
CG_DrawPlacementDeathsOwnerDraw

Draws the tracked death count for a placement scorebox slot.
=============
*/
static qboolean CG_DrawPlacementDeathsOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot ) {
	const score_t *score;
	char buffer[32];

	if ( !rect ) {
		return qfalse;
	}

	score = CG_GetPlacementScore( slot );
	if ( !score ) {
		return qfalse;
	}

	Com_sprintf( buffer, sizeof( buffer ), "%i", score->deaths );
	CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );
	return qtrue;
}

/*
=============
CG_DrawPlacementDamageOwnerDraw

Draws the tracked damage tally for a placement scorebox slot.
=============
*/
static qboolean CG_DrawPlacementDamageOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot ) {
	const score_t *score;
	char buffer[32];

	if ( !rect ) {
		return qfalse;
	}

	score = CG_GetPlacementScore( slot );
	if ( !score ) {
		return qfalse;
	}

	Com_sprintf( buffer, sizeof( buffer ), "%i", score->damage );
	CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );
	return qtrue;
}

/*
=============
CG_DrawPlacementWinsOwnerDraw

Draws the tracked wins tally for a placement scorebox slot.
=============
*/
static qboolean CG_DrawPlacementWinsOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int slot ) {
	const score_t *score;
	const clientInfo_t *ci;
	char buffer[32];

	if ( !rect ) {
		return qfalse;
	}

	score = CG_GetPlacementScore( slot );
	ci = CG_GetPlacementClientInfo( score );
	if ( !score || !ci ) {
		return qfalse;
	}

	Com_sprintf( buffer, sizeof( buffer ), "%i", ci->wins );
	CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );
	return qtrue;
}

/*
=============
CG_DrawPlacementPingOwnerDraw

Draws the retail first/second placement ping ownerdraw with the recovered ping
warning color thresholds.
=============
*/
static void CG_DrawPlacementPingOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	const score_t	*score;
	vec4_t		drawColor;
	int		slot;

	if ( !rect || !CG_ResolvePlacementMetricOwnerDraw( ownerDraw, &slot, NULL ) ) {
		return;
	}

	score = CG_GetPlacementScore( slot );
	if ( !score ) {
		return;
	}

	Vector4Copy( color, drawColor );
	if ( score->ping >= 80 ) {
		drawColor[0] = 1.0f;
		drawColor[1] = 0.2f;
		drawColor[2] = 0.2f;
	} else if ( score->ping >= 40 ) {
		drawColor[0] = 1.0f;
		drawColor[1] = 0.85f;
		drawColor[2] = 0.2f;
	}

	(void)CG_DrawPlacementMetricTextOwnerDraw( rect, scale, drawColor, textStyle, ownerDraw );
}

/*
=============
CG_DrawPlacementAccuracyOwnerDraw

Draws the retail first/second placement accuracy ownerdraw.
=============
*/
static void CG_DrawPlacementAccuracyOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	(void)CG_DrawPlacementMetricTextOwnerDraw( rect, scale, color, textStyle, ownerDraw );
}

/*
=============
CG_DrawPlacementWeaponFragsOwnerDraw

Draws the retail first/second placement per-weapon frag ownerdraws.
=============
*/
static void CG_DrawPlacementWeaponFragsOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	(void)CG_DrawPlacementMetricTextOwnerDraw( rect, scale, color, textStyle, ownerDraw );
}

/*
=============
CG_DrawPlacementWeaponHitsOwnerDraw

Draws the retail first/second placement per-weapon hit ownerdraws.
=============
*/
static void CG_DrawPlacementWeaponHitsOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	(void)CG_DrawPlacementMetricTextOwnerDraw( rect, scale, color, textStyle, ownerDraw );
}

/*
=============
CG_DrawPlacementWeaponShotsOwnerDraw

Draws the retail first/second placement per-weapon shot ownerdraws.
=============
*/
static void CG_DrawPlacementWeaponShotsOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	(void)CG_DrawPlacementMetricTextOwnerDraw( rect, scale, color, textStyle, ownerDraw );
}

/*
=============
CG_DrawPlacementWeaponDamageOwnerDraw

Draws the retail first/second placement per-weapon damage ownerdraws.
=============
*/
static void CG_DrawPlacementWeaponDamageOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	(void)CG_DrawPlacementMetricTextOwnerDraw( rect, scale, color, textStyle, ownerDraw );
}

/*
=============
CG_DrawPlacementWeaponAccuracyOwnerDraw

Draws the retail first/second placement per-weapon accuracy ownerdraws.
=============
*/
static void CG_DrawPlacementWeaponAccuracyOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	(void)CG_DrawPlacementMetricTextOwnerDraw( rect, scale, color, textStyle, ownerDraw );
}

/*
=============
CG_DrawPlacementPickupCountOwnerDraw

Draws the retail first/second placement pickup-count ownerdraw family.
=============
*/
static void CG_DrawPlacementPickupCountOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	(void)CG_DrawPlacementMetricTextOwnerDraw( rect, scale, color, textStyle, ownerDraw );
}

/*
=============
CG_DrawPlacementPickupAverageOwnerDraw

Draws the retail first/second placement pickup-average ownerdraw family.
=============
*/
static void CG_DrawPlacementPickupAverageOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	(void)CG_DrawPlacementMetricTextOwnerDraw( rect, scale, color, textStyle, ownerDraw );
}

/*
=============
CG_DrawPlacementAwardCountOwnerDraw

Draws the retail first/second placement medal-count ownerdraw family.
=============
*/
static void CG_DrawPlacementAwardCountOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	(void)CG_DrawPlacementMetricTextOwnerDraw( rect, scale, color, textStyle, ownerDraw );
}

/*
=============
CG_IsRetailPlacementMetricOwnerDraw

Reports whether the retail ownerdraw switch routes the placement metric to the
pre-switch placement helper.
=============
*/
static qboolean CG_IsRetailPlacementMetricOwnerDraw( int ownerDraw ) {
	switch ( ownerDraw ) {
	case CG_1ST_PLYR_READY:
	case CG_2ND_PLYR_READY:
	case CG_1ST_PLYR_FRAGS:
	case CG_2ND_PLYR_FRAGS:
	case CG_1ST_PLYR_DEATHS:
	case CG_2ND_PLYR_DEATHS:
	case CG_1ST_PLYR_DMG:
	case CG_2ND_PLYR_DMG:
	case CG_1ST_PLYR_PING:
	case CG_2ND_PLYR_PING:
	case CG_1ST_PLYR_WINS:
	case CG_2ND_PLYR_WINS:
	case CG_1ST_PLYR_ACC:
	case CG_2ND_PLYR_ACC:
	case CG_1ST_PLYR_FLAG:
	case CG_2ND_PLYR_FLAG:
		return qtrue;
	default:
		break;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_FRAGS_G && ownerDraw <= CG_1ST_PLYR_FRAGS_HMG ) ||
		( ownerDraw >= CG_2ND_PLYR_FRAGS_G && ownerDraw <= CG_2ND_PLYR_FRAGS_HMG ) ) {
		return qtrue;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_HITS_MG && ownerDraw <= CG_1ST_PLYR_HITS_HMG ) ||
		( ownerDraw >= CG_2ND_PLYR_HITS_MG && ownerDraw <= CG_2ND_PLYR_HITS_HMG ) ) {
		return qtrue;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_SHOTS_MG && ownerDraw <= CG_1ST_PLYR_SHOTS_HMG ) ||
		( ownerDraw >= CG_2ND_PLYR_SHOTS_MG && ownerDraw <= CG_2ND_PLYR_SHOTS_HMG ) ) {
		return qtrue;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_DMG_G && ownerDraw <= CG_1ST_PLYR_DMG_HMG ) ||
		( ownerDraw >= CG_2ND_PLYR_DMG_G && ownerDraw <= CG_2ND_PLYR_DMG_HMG ) ) {
		return qtrue;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_ACC_MG && ownerDraw <= CG_1ST_PLYR_ACC_HMG ) ||
		( ownerDraw >= CG_2ND_PLYR_ACC_MG && ownerDraw <= CG_2ND_PLYR_ACC_HMG ) ) {
		return qtrue;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_PICKUPS && ownerDraw <= CG_1ST_PLYR_PICKUPS_MH ) ||
		( ownerDraw >= CG_2ND_PLYR_PICKUPS && ownerDraw <= CG_2ND_PLYR_PICKUPS_MH ) ) {
		return qtrue;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_AVG_PICKUP_TIME_RA && ownerDraw <= CG_1ST_PLYR_AVG_PICKUP_TIME_MH ) ||
		( ownerDraw >= CG_2ND_PLYR_AVG_PICKUP_TIME_RA && ownerDraw <= CG_2ND_PLYR_AVG_PICKUP_TIME_MH ) ) {
		return qtrue;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_EXCELLENT && ownerDraw <= CG_1ST_PLYR_HUMILIATION ) ||
		( ownerDraw >= CG_2ND_PLYR_EXCELLENT && ownerDraw <= CG_2ND_PLYR_HUMILIATION ) ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
CG_DrawPlacementMetricOwnerDraw

Renders first/second place metric ownerdraws from available scoreboard fields.
=============
*/
static qboolean CG_DrawPlacementMetricOwnerDraw( rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw ) {
	int			normalized;
	int			slot;

	if ( !rect || !CG_IsRetailPlacementMetricOwnerDraw( ownerDraw ) ) {
		return qfalse;
	}

	if ( ownerDraw == CG_1ST_PLYR_READY ) {
		CG_DrawSpectatorPrimaryStatus( rect );
		return qtrue;
	}

	if ( ownerDraw == CG_2ND_PLYR_READY ) {
		CG_DrawSpectatorSecondaryStatus( rect );
		return qtrue;
	}

	if ( ownerDraw == CG_1ST_PLYR_PING || ownerDraw == CG_2ND_PLYR_PING ) {
		CG_DrawPlacementPingOwnerDraw( rect, scale, color, textStyle, ownerDraw );
		return qtrue;
	}

	if ( ownerDraw == CG_1ST_PLYR_ACC || ownerDraw == CG_2ND_PLYR_ACC ) {
		CG_DrawPlacementAccuracyOwnerDraw( rect, scale, color, textStyle, ownerDraw );
		return qtrue;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_FRAGS_G && ownerDraw <= CG_1ST_PLYR_FRAGS_HMG ) ||
		( ownerDraw >= CG_2ND_PLYR_FRAGS_G && ownerDraw <= CG_2ND_PLYR_FRAGS_HMG ) ) {
		CG_DrawPlacementWeaponFragsOwnerDraw( rect, scale, color, textStyle, ownerDraw );
		return qtrue;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_HITS_MG && ownerDraw <= CG_1ST_PLYR_HITS_HMG ) ||
		( ownerDraw >= CG_2ND_PLYR_HITS_MG && ownerDraw <= CG_2ND_PLYR_HITS_HMG ) ) {
		CG_DrawPlacementWeaponHitsOwnerDraw( rect, scale, color, textStyle, ownerDraw );
		return qtrue;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_SHOTS_MG && ownerDraw <= CG_1ST_PLYR_SHOTS_HMG ) ||
		( ownerDraw >= CG_2ND_PLYR_SHOTS_MG && ownerDraw <= CG_2ND_PLYR_SHOTS_HMG ) ) {
		CG_DrawPlacementWeaponShotsOwnerDraw( rect, scale, color, textStyle, ownerDraw );
		return qtrue;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_DMG_G && ownerDraw <= CG_1ST_PLYR_DMG_HMG ) ||
		( ownerDraw >= CG_2ND_PLYR_DMG_G && ownerDraw <= CG_2ND_PLYR_DMG_HMG ) ) {
		CG_DrawPlacementWeaponDamageOwnerDraw( rect, scale, color, textStyle, ownerDraw );
		return qtrue;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_ACC_MG && ownerDraw <= CG_1ST_PLYR_ACC_HMG ) ||
		( ownerDraw >= CG_2ND_PLYR_ACC_MG && ownerDraw <= CG_2ND_PLYR_ACC_HMG ) ) {
		CG_DrawPlacementWeaponAccuracyOwnerDraw( rect, scale, color, textStyle, ownerDraw );
		return qtrue;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_PICKUPS && ownerDraw <= CG_1ST_PLYR_PICKUPS_MH ) ||
		( ownerDraw >= CG_2ND_PLYR_PICKUPS && ownerDraw <= CG_2ND_PLYR_PICKUPS_MH ) ) {
		CG_DrawPlacementPickupCountOwnerDraw( rect, scale, color, textStyle, ownerDraw );
		return qtrue;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_AVG_PICKUP_TIME_RA && ownerDraw <= CG_1ST_PLYR_AVG_PICKUP_TIME_MH ) ||
		( ownerDraw >= CG_2ND_PLYR_AVG_PICKUP_TIME_RA && ownerDraw <= CG_2ND_PLYR_AVG_PICKUP_TIME_MH ) ) {
		CG_DrawPlacementPickupAverageOwnerDraw( rect, scale, color, textStyle, ownerDraw );
		return qtrue;
	}

	if ( ( ownerDraw >= CG_1ST_PLYR_EXCELLENT && ownerDraw <= CG_1ST_PLYR_HUMILIATION ) ||
		( ownerDraw >= CG_2ND_PLYR_EXCELLENT && ownerDraw <= CG_2ND_PLYR_HUMILIATION ) ) {
		CG_DrawPlacementAwardCountOwnerDraw( rect, scale, color, textStyle, ownerDraw );
		return qtrue;
	}

	if ( !CG_ResolvePlacementMetricOwnerDraw( ownerDraw, &slot, &normalized ) ) {
		return qfalse;
	}

	switch ( normalized ) {
	case CG_1ST_PLYR_FRAGS:
		return CG_DrawPlacementFragsOwnerDraw( rect, scale, color, textStyle, slot );
	case CG_1ST_PLYR_DEATHS:
		return CG_DrawPlacementDeathsOwnerDraw( rect, scale, color, textStyle, slot );
	case CG_1ST_PLYR_DMG:
		return CG_DrawPlacementDamageOwnerDraw( rect, scale, color, textStyle, slot );
	case CG_1ST_PLYR_WINS:
		return CG_DrawPlacementWinsOwnerDraw( rect, scale, color, textStyle, slot );
	case CG_1ST_PLYR_FLAG:
		CG_DrawPlacementFlagOwnerDraw( rect, slot );
		return qtrue;
	default:
		break;
	}

	return CG_DrawPlacementMetricTextOwnerDraw( rect, scale, color, textStyle, ownerDraw );
}

static qboolean CG_IsAwardOwnerDraw( int ownerDraw );

/*
=============
CG_AwardConfigStringIndex

Maps a retail award-player ownerdraw to its recovered winner configstring slot.
=============
*/
static int CG_AwardConfigStringIndex( int ownerDraw ) {
	switch ( ownerDraw ) {
	case CG_MOST_VALUABLE_OFFENSIVE_PLYR:
		return CS_AWARD_MOST_VALUABLE_OFFENSIVE;
	case CG_MOST_VALUABLE_DEFENSIVE_PLYR:
		return CS_AWARD_MOST_VALUABLE_DEFENSIVE;
	case CG_MOST_VALUABLE_PLYR:
		return CS_AWARD_MOST_VALUABLE;
	case CG_BEST_ITEMCONTROL_PLYR:
		return CS_AWARD_BEST_ITEMCONTROL;
	case CG_MOST_ACCURATE_PLYR:
		return CS_AWARD_MOST_ACCURATE;
	case CG_MOST_DAMAGEDEALT_PLYR:
		return CS_AWARD_MOST_DAMAGEDEALT;
	default:
		return -1;
	}
}

/*
=============
CG_GetAwardClientNum

Returns the current client winner for a retail endgame award slot.
=============
*/
static int CG_GetAwardClientNum( int ownerDraw ) {
	const char	*configString;
	int		configStringIndex;

	configStringIndex = CG_AwardConfigStringIndex( ownerDraw );
	if ( configStringIndex < 0 ) {
		return -1;
	}

	configString = CG_ConfigString( configStringIndex );
	if ( !configString || !configString[0] ) {
		return -1;
	}

	return atoi( configString );
}

/*
=============
CG_DrawAwardPlayer

Draws the award-winner profile image for the retail endgame summary widgets.
=============
*/
static qboolean CG_DrawAwardPlayer( rectDef_t *rect, int ownerDraw ) {
	int	clientNum;

	if ( !CG_IsAwardOwnerDraw( ownerDraw ) ) {
		return qfalse;
	}

	clientNum = CG_GetAwardClientNum( ownerDraw );
	if ( clientNum < 0 || clientNum >= cgs.maxclients ) {
		return qtrue;
	}

	CG_DrawProfileModel( rect, clientNum, qtrue );
	return qtrue;
}

/*
=============
CG_IsPlacementMetricOwnerDraw

Returns qtrue when the ownerdraw targets first/second place stats.
=============
*/
static qboolean CG_IsPlacementMetricOwnerDraw( int ownerDraw ) {
	return CG_IsRetailPlacementMetricOwnerDraw( ownerDraw );
}

/*
=============
CG_IsAwardOwnerDraw

Returns qtrue when the ownerdraw maps to an endgame award string.
=============
*/
static qboolean CG_IsAwardOwnerDraw( int ownerDraw ) {
	return CG_AwardConfigStringIndex( ownerDraw ) >= 0;
}

/*
=============
CG_IsCompetitiveScoreOwnerDraw

Reports whether an ownerdraw should refresh competitive scoreboard cache.
=============
*/
static qboolean CG_IsCompetitiveScoreOwnerDraw( int ownerDraw ) {
	if ( ownerDraw == CG_ROUNDTIMER || ownerDraw == CG_OVERTIME ||
		ownerDraw == CG_PLAYER_COUNTS ||
		ownerDraw == CG_1ST_PLACE_SCORE || ownerDraw == CG_2ND_PLACE_SCORE ||
		ownerDraw == CG_1ST_PLYR || ownerDraw == CG_1ST_PLYR_SCORE ||
		ownerDraw == CG_1ST_PLYR_HEALTH_ARMOR || ownerDraw == CG_1ST_PLYR_AVATAR ||
		ownerDraw == CG_2ND_PLYR || ownerDraw == CG_2ND_PLYR_SCORE ||
		ownerDraw == CG_2ND_PLYR_HEALTH_ARMOR || ownerDraw == CG_2ND_PLYR_AVATAR ||
		ownerDraw == CG_TEAM_PLYR_COUNT || ownerDraw == CG_ENEMY_PLYR_COUNT ||
		ownerDraw == CG_MATCH_WINNER || ownerDraw == CG_PLYR_END_GAME_SCORE ||
		ownerDraw == CG_1STPLACE_PLYR_MODEL ||
		ownerDraw == CG_FLAG_STATUS || ownerDraw == CG_RED_BASESTATUS || ownerDraw == CG_BLUE_BASESTATUS ) {
		return qtrue;
	}

	if ( CG_IsTeamPickupOwnerDraw( ownerDraw ) ) {
		return qtrue;
	}

	if ( CG_IsPlacementMetricOwnerDraw( ownerDraw ) ) {
		return qtrue;
	}

	return CG_IsAwardOwnerDraw( ownerDraw );
}

/*
=============
CG_DrawMatchState

Outputs the retail compact match-phase banner.
=============
*/
static void CG_DrawMatchState(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	CG_Text_Paint( rect->x, rect->y, scale, color, CG_GetMatchPhaseText(), 0, 0, textStyle );
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

Shows the retail spectator/pregame text family inside the owner-draw rect.
=============
*/
static void CG_DrawSpectatorMessages(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	char line1[64];
	char line2[96];
	char line3[64];
	char line4[64];
	vec4_t drawColor;
	float y;

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

		switch ( cgs.gametype ) {
		case GT_CLAN_ARENA:
		case GT_FREEZE:
		case GT_ATTACK_DEFEND:
		case GT_RED_ROVER:
			if ( cgs.matchRoundState == ROUNDSTATE_ACTIVE ) {
				Q_strncpyz( line1, "Round In Progress", sizeof( line1 ) );
				y = rect->y + CG_Text_Height( line1, scale, 0 );
				CG_Text_Paint( rect->x, y, scale, color, line1, 0, 0, textStyle );
			}
			break;
		}

		return;
	}

	if (!cg_drawSpecMessages.integer) {
		return;
	}

	Vector4Copy(color, drawColor);
	Q_strncpyz(line1, "SPECTATOR MODE", sizeof(line1));
	Q_strncpyz(line2, "Press mouse button 1 to cycle through players", sizeof(line2));
	line3[0] = '\0';
	line4[0] = '\0';
	if ( cgs.gametype == GT_TOURNAMENT ) {
		Q_strncpyz( line3, "waiting to play", sizeof( line3 ) );
	} else if ( cgs.gametype >= GT_TEAM ) {
		Q_strncpyz( line3, "press ESC and use the JOIN buttons", sizeof( line3 ) );
		Q_strncpyz( line4, "to enter the game", sizeof( line4 ) );
	}

	y = rect->y + CG_Text_Height(line1, scale, 0);
	CG_Text_Paint(rect->x, y, scale, drawColor, line1, 0, 0, textStyle);
	y += CG_Text_Height(line2, scale * 0.8f, 0) + 2.0f;
	CG_Text_Paint(rect->x, y, scale * 0.8f, drawColor, line2, 0, 0, textStyle);
	if ( line3[0] ) {
		y += CG_Text_Height(line3, scale * 0.8f, 0) + 2.0f;
		CG_Text_Paint(rect->x, y, scale * 0.8f, drawColor, line3, 0, 0, textStyle);
	}
	if ( line4[0] ) {
		y += CG_Text_Height(line4, scale * 0.8f, 0) + 2.0f;
		CG_Text_Paint(rect->x, y, scale * 0.8f, drawColor, line4, 0, 0, textStyle);
	}
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

	if ( !rect || cg_teamChatTime.integer <= 0 ) {
		return;
	}

	chatHeight = CG_GetChatHistoryLength();

	maxLines = cg.chatHistoryVisible ? chatHeight : 1;
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
		if (elapsed < 0) {
			elapsed = 0;
		}
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
	const clientInfo_t	*ci;
	vec4_t			color;
	vec4_t			modulate;
	float			x;
	float			y;
	float			w;
	float			h;
	int			slot;
	int			health;
	int			armor;

	if ( !rect || !cg.snap ) {
		return;
	}

	if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {
		slot = ( rect->x + rect->w * 0.5f < 320.0f ) ? 0 : 1;
		ci = CG_SpectatorClientInfo( slot );
	} else {
		slot = -1;
		ci = NULL;
	}

	if ( !ci ) {
		health = cg.snap->ps.stats[STAT_HEALTH];
		armor = cg.snap->ps.stats[STAT_ARMOR];
	} else {
		health = ci->health;
		armor = ci->armor;
	}

	CG_GetColorForHealth( health, armor, color );
	color[3] = 0.5f;

	if ( shader ) {
		Vector4Copy( color, modulate );
		x = rect->x;
		y = rect->y;
		w = rect->w;
		h = rect->h;
		CG_AdjustFrom640( &x, &y, &w, &h );
		trap_R_SetColor( modulate );
		trap_R_DrawStretchPic( x, y, w, h, 0.0f, 0.0f, 1.0f, 1.0f, shader );
		trap_R_SetColor( NULL );
		return;
	}

	CG_FillRect( rect->x, rect->y, rect->w, rect->h, color );
}

/*
=============
CG_DrawArmorTieredColorized

Draws the retail armor-tier color swatch from the replicated tier stat.
=============
*/
static void CG_DrawArmorTieredColorized( rectDef_t *rect ) {
	vec4_t color;

	if ( !rect || !cg.snap ) {
		return;
	}

	CG_GetArmorTierColorForTier( cg.snap->ps.stats[STAT_ARMOR_TIER], color );
	color[3] = 0.5f;
	CG_FillRect( rect->x, rect->y, rect->w, rect->h, color );
}

/*
=============
CG_DrawFollowPlayerNameEx

Renders the spectator follow label for the primary target slot, mirroring the
retail prefix split between `CG_FOLLOW_PLAYER_NAME` and `_EX`.
=============
*/
static void CG_DrawFollowPlayerNameEx(rectDef_t *rect, float scale, vec4_t color, int textStyle, int ownerDraw, int align) {
	const clientInfo_t *ci = CG_SpectatorClientInfo(0);
	vec4_t drawColor;
	char buffer[64];
	float x;

	if ( !rect || !ci ) {
		return;
	}

	Vector4Copy( color, drawColor );
	if ( cgs.gametype >= GT_TEAM ) {
		Vector4Copy( CG_TeamColor( ci->team ), drawColor );
		drawColor[3] = color[3];
	}

	if ( ownerDraw == CG_FOLLOW_PLAYER_NAME ) {
		Com_sprintf( buffer, sizeof( buffer ), "Following - %s", ci->name );
	} else {
		Q_strncpyz( buffer, ci->name, sizeof( buffer ) );
	}

	x = rect->x;
	CG_AlignTextX( &x, buffer, scale, align );

	CG_Text_Paint( x, rect->y, scale, drawColor, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawTeamColorized

Fills the supplied rect with the retail team color, tinting the provided shader
if available and preserving the menu item alpha.
=============
*/
static void CG_DrawTeamColorized( rectDef_t *rect, vec4_t itemColor, qhandle_t shader ) {
	vec4_t color;
	float x;
	float y;
	float w;
	float h;
	int team;
	
	if ( !rect ) {
		return;
	}

	team = TEAM_FREE;
	if ( cg.snap ) {
		team = cg.snap->ps.persistant[PERS_TEAM];
	}
	Vector4Copy( CG_TeamColor( team ), color );
	color[3] = itemColor[3];

	if ( shader ) {
		x = rect->x;
		y = rect->y;
		w = rect->w;
		h = rect->h;
		CG_AdjustFrom640( &x, &y, &w, &h );
		trap_R_SetColor( color );
		trap_R_DrawStretchPic( x, y, w, h, 0.0f, 0.0f, 1.0f, 1.0f, shader );
		trap_R_SetColor( NULL );
		return;
	}
	
	CG_FillRect( rect->x, rect->y, rect->w, rect->h, color );
}

/*
=============
CG_TranslateHudRectForWidescreen

Offsets a HUD rect to account for widescreen pillarboxing while using 640-based coordinates.
=============
*/
static void CG_TranslateHudRectForWidescreen(const rectDef_t *rect, rectDef_t *translated) {
	float pixelOffset;
	
	if (!rect || !translated) {
	return;
	}
	
	*translated = *rect;
	
	if (cgs.screenXScale <= 0.0f) {
	return;
	}
	
	if (cgs.glconfig.vidWidth * SCREEN_HEIGHT > cgs.glconfig.vidHeight * SCREEN_WIDTH) {
	float targetWidth;
	
	targetWidth = (float)cgs.glconfig.vidHeight * ((float)SCREEN_WIDTH / (float)SCREEN_HEIGHT);
	pixelOffset = 0.5f * ((float)cgs.glconfig.vidWidth - targetWidth);
	translated->x += pixelOffset / cgs.screenXScale;
	}
}

/*
=============
CG_DrawScoreboxFollowBackground

Tints the follow scorebox backing image for spectator HUDs.
=============
*/
static void CG_DrawScoreboxFollowBackground(rectDef_t *rect, qhandle_t shader, vec4_t color) {
	vec4_t modulate;
	float x;
	float y;
	float w;
	float h;
	rectDef_t widescreenRect;
	
	if (!shader) {
	shader = cgs.media.scoreboxFollowShader;
	}
	
	if (!shader) {
	return;
	}
	
	Vector4Copy(color, modulate);
	if (modulate[3] <= 0.0f) {
	modulate[3] = 1.0f;
	}
	
	CG_TranslateHudRectForWidescreen(rect, &widescreenRect);
	
	x = widescreenRect.x;
	y = widescreenRect.y;
	w = widescreenRect.w;
	h = widescreenRect.h;
	CG_AdjustFrom640(&x, &y, &w, &h);
	
	trap_R_SetColor(modulate);
	trap_R_DrawStretchPic(x, y, w, h, 0.0f, 0.0f, 1.0f, 1.0f, shader);
	trap_R_SetColor(NULL);
}

/*
=============
CG_DrawScoreboxSpecBackground

Tints the spectator scorebox backing image.
=============
*/
static void CG_DrawScoreboxSpecBackground(rectDef_t *rect, qhandle_t shader, vec4_t color) {
	vec4_t modulate;
	float x;
	float y;
	float w;
	float h;
	rectDef_t widescreenRect;
	
	if (!shader) {
	shader = cgs.media.scoreboxSpecShader;
	}
	
	if (!shader) {
	return;
	}
	
	Vector4Copy(color, modulate);
	if (modulate[3] <= 0.0f) {
	modulate[3] = 1.0f;
	}
	
	CG_TranslateHudRectForWidescreen(rect, &widescreenRect);
	
	x = widescreenRect.x;
	y = widescreenRect.y;
	w = widescreenRect.w;
	h = widescreenRect.h;
	CG_AdjustFrom640(&x, &y, &w, &h);
	
	trap_R_SetColor(modulate);
	trap_R_DrawStretchPic(x, y, w, h, 0.0f, 0.0f, 1.0f, 1.0f, shader);
	trap_R_SetColor(NULL);
}

/*
=============
CG_DrawRoundBackground

Draws a backing quad for the current match state label.
=============
*/
static void CG_DrawRoundBackground(rectDef_t *rect, qhandle_t shader, vec4_t color) {
	vec4_t modulate;
	float x;
	float y;
	float w;
	float h;
	const char *label;

	label = CG_GetMatchStateLabel();
	if (!label || !*label) {
		return;
	}

	Vector4Copy(color, modulate);
	if (modulate[3] <= 0.0f) {
		modulate[3] = 1.0f;
	}

	if (shader) {
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

	CG_FillRect(rect->x, rect->y, rect->w, rect->h, modulate);
}

/*
=============
CG_DrawOvertimeBackground

Paints the overtime banner background when active.
=============
*/
static void CG_DrawOvertimeBackground(rectDef_t *rect, qhandle_t shader, vec4_t color) {
	vec4_t modulate;
	float x;
	float y;
	float w;
	float h;

	if (!(cg.timelimitWarnings & 4) && !cgs.matchOvertimeActive) {
		return;
	}

	Vector4Copy(color, modulate);
	if (modulate[3] <= 0.0f) {
		modulate[3] = 1.0f;
	}

	if (shader) {
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

	CG_FillRect(rect->x, rect->y, rect->w, rect->h, modulate);
}

/*
=============
CG_BuildLevelTimerMilliseconds

Reconstructs the retail level-clock helper used by CG_LEVELTIMER.
=============
*/
static qboolean CG_BuildLevelTimerMilliseconds( int *millisecondsOut ) {
	int		currentTime;
	int		limitMilliseconds;
	int		milliseconds;
	int		timeoutStart;

	if ( millisecondsOut ) {
		*millisecondsOut = 0;
	}
	if ( !millisecondsOut ) {
		return qfalse;
	}

	timeoutStart = CG_GetMatchTimeoutStartTime();
	currentTime = timeoutStart;
	if ( currentTime == 0 ) {
		currentTime = cg.time;
	}

	if ( cg.warmup != 0 ) {
		if ( !CG_ShowPlayersRemaining() || cgs.matchRoundNumber <= 0 ) {
			return qfalse;
		}
	}

	limitMilliseconds = cgs.timelimit * 60000;
	if ( cgs.timelimit == 0 ) {
		milliseconds = currentTime - cgs.levelStartTime;
	} else {
		milliseconds = limitMilliseconds - currentTime + cgs.levelStartTime;
		if ( milliseconds < 0 ) {
			milliseconds = currentTime - limitMilliseconds - cgs.levelStartTime;
		} else if ( cg_levelTimerDirection.integer != 1 ) {
			milliseconds = currentTime - cgs.levelStartTime;
		}
	}

	*millisecondsOut = milliseconds;
	return qtrue;
}

/*
=============
CG_DrawLevelTimer

Renders the retail CG_LEVELTIMER ownerdraw clock.
=============
*/
static void CG_DrawLevelTimer(rectDef_t *rect, float scale, vec4_t color, int textStyle, int align) {
	int		milliseconds;
	int		seconds;
	float	x;
	char	buffer[32];

	milliseconds = 0;
	CG_BuildLevelTimerMilliseconds( &milliseconds );
	seconds = milliseconds / 1000;

	Q_strncpyz( buffer, CG_FormatMinutesSeconds( seconds ), sizeof( buffer ) );
	x = rect->x;
	CG_AlignTextX( &x, buffer, scale, align );
	CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawRoundTimer

Displays the round-clock ownerdraw during active round play.
=============
*/
static void CG_DrawRoundTimer(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	int		roundStartTime;
	int		roundTimeLimitSeconds;
	int		remainingMilliseconds;
	int		seconds;
	int		width;
	float	x;
	char	buffer[32];

	if ( cgs.matchRoundState != ROUNDSTATE_ACTIVE ) {
		return;
	}

	if ( cgs.matchTimeoutActive ) {
		return;
	}

	roundStartTime = CG_GetMatchRoundStartTime();
	roundTimeLimitSeconds = CG_GetRoundTimeLimitSeconds();
	if ( roundStartTime <= 0 || roundTimeLimitSeconds <= 0 ) {
		return;
	}

	remainingMilliseconds = roundTimeLimitSeconds * 1000 - cg.time + roundStartTime;
	if ( remainingMilliseconds <= 0 || remainingMilliseconds > 29999 ) {
		return;
	}

	seconds = ( remainingMilliseconds + 500 ) / 1000;
	Q_strncpyz( buffer, CG_FormatMinutesSeconds( seconds ), sizeof( buffer ) );
	width = CG_Text_Width( buffer, scale, 0 );
	x = rect->x + ( rect->w - width ) * 0.5f;
	CG_Text_Paint( x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawOvertime

Displays the overtime banner label when the match enters overtime.
=============
*/
static void CG_DrawOvertime(rectDef_t *rect, float scale, vec4_t color, int textStyle) {
	char	buffer[32];
	int		overtimeCount;

	if ( ( cg.timelimitWarnings & 4 ) || cgs.matchOvertimeActive ) {
		overtimeCount = CG_GetOvertimeCount();
		if ( overtimeCount > 1 ) {
			Com_sprintf( buffer, sizeof( buffer ), "Overtime x%i", overtimeCount );
		} else {
			Q_strncpyz( buffer, "Overtime", sizeof( buffer ) );
		}

		CG_Text_Paint(rect->x, rect->y, scale, color, buffer, 0, 0, textStyle);
	}
}

/*
=============
CG_DrawPlayerObituary

Draws the compact obituary-feed stack used by the retail `CG_PLAYER_OBIT` slot.
=============
*/
static void CG_DrawPlayerObituary( rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
	float	rowHeight;
	float	y;
	int		i;

	(void)color;

	if ( !rect ) {
		return;
	}

	if ( !cg_drawFragMessages.integer ) {
		return;
	}

	CG_PruneObituaryFeed();

	rowHeight = (float)CG_Text_Height( "A", scale, 0 );
	if ( rowHeight < 1.0f ) {
		rowHeight = ( rect->h > 0.0f ) ? rect->h : SMALLCHAR_HEIGHT;
	}

	y = rect->y;
	for ( i = 0; i < MAX_OBITUARIES; i++ ) {
		const cgObituary_t	*entry;
		vec4_t			targetColor;
		vec4_t			attackerColor;
		vec4_t			iconColor;
		float			alpha;
		float			x;
		float			iconSize;
		int			time;

		entry = &cg.obituaries[i];
		if ( !entry->active ) {
			break;
		}

		time = cg.time - entry->time;
		if ( time > OBITUARY_TIME - FADE_TIME ) {
			alpha = (float)( OBITUARY_TIME - time ) / FADE_TIME;
		} else {
			alpha = 1.0f;
		}

		if ( alpha <= 0.0f ) {
			continue;
		}

		x = rect->x;
		if ( entry->targetName[0] ) {
			CG_ObituaryColorForIndex( entry->targetColorIndex, alpha, targetColor );
			CG_Text_Paint( x, y, scale, targetColor, entry->targetName, 0, 0, textStyle );
			x += CG_Text_Width( entry->targetName, scale, 0 );
		}

		iconSize = rowHeight;
		if ( entry->icon ) {
			iconColor[0] = 1.0f;
			iconColor[1] = 1.0f;
			iconColor[2] = 1.0f;
			iconColor[3] = alpha;
			trap_R_SetColor( iconColor );
			CG_DrawPic( x, y - iconSize, iconSize, iconSize, entry->icon );
			trap_R_SetColor( NULL );
			x += iconSize + 2.0f;
		}

		if ( entry->hasAttacker && entry->attackerName[0] ) {
			CG_ObituaryColorForIndex( entry->attackerColorIndex, alpha, attackerColor );
			CG_Text_Paint( x, y, scale, attackerColor, entry->attackerName, 0, 0, textStyle );
		}

		y += rowHeight + 2.0f;
	}
}

void CG_InitTeamChat() {
	memset( teamChat1, 0, sizeof( teamChat1 ) );
	memset( teamChat2, 0, sizeof( teamChat2 ) );
	memset( systemChat, 0, sizeof( systemChat ) );
	memset( cgs.teamChatMsgs, 0, sizeof( cgs.teamChatMsgs ) );
	memset( cgs.teamChatMsgTimes, 0, sizeof( cgs.teamChatMsgTimes ) );
	cgs.teamChatPos = 0;
	cgs.teamLastChatPos = 0;
	cg.chatHistoryVisible = qfalse;
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
	if ( !cg.snap || ( cg.snap->ps.pm_flags & PMF_FOLLOW ) ||
			cg.snap->ps.pm_type == PM_SPECTATOR ||
			cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR ) {
		cgs.orderPending = qfalse;
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
			trap_SendConsoleCommand( va( "cmd vsay_team %s\n", p2 ) );
		} else {
			// for the player self
			if (sortedTeamPlayers[cg_currentSelectedPlayer.integer] == cg.snap->ps.clientNum && p1) {
				trap_SendConsoleCommand( va( "teamtask %i\n", cgs.currentOrder ) );
				//trap_SendConsoleCommand( va( "cmd say_team %s\n", p2 ) );
				trap_SendConsoleCommand( va( "cmd vsay_team %s\n", p1 ) );
			} else if (p2) {
				//trap_SendConsoleCommand( va( "cmd say_team %s, %s\n", ci->name, p ) );
				trap_SendConsoleCommand( va( "cmd vtell %d %s\n", sortedTeamPlayers[cg_currentSelectedPlayer.integer], p2 ) );
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


/*
=============
CG_DrawPlayerArmorIcon

Draws the local armor pickup icon as either a flat HUD icon or spinning model.
=============
*/
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

/*
=============
CG_DrawPlayerArmorValue

Draws the local armor count or caller-supplied armor value shader.
=============
*/
static void CG_DrawPlayerArmorValue( rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle, int align ) {
	char	num[16];
	float	x;
	float	y;
	int		value;
	centity_t	*cent;
	playerState_t	*ps;

	if ( !rect || !cg.snap ) {
		return;
	}

	cent = &cg_entities[cg.snap->ps.clientNum];
	ps = &cg.snap->ps;

	value = ps->stats[STAT_ARMOR];

	if ( shader ) {
		trap_R_SetColor( color );
		CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );
		trap_R_SetColor( NULL );
	} else {
		Com_sprintf( num, sizeof( num ), "%i", value );
		x = rect->x;
		y = rect->y + CG_Text_Height( num, scale, 0 );
		CG_AlignTextX( &x, num, scale, align );
		CG_Text_Paint( x, y, scale, color, num, 0, 0, textStyle );
	}
}
/*
=============
CG_DrawPlayerAmmoIcon

Draws the retail current-weapon ammo icon in 2D or rotating 3D form.
=============
*/
static void CG_DrawPlayerAmmoIcon( rectDef_t *rect, qboolean draw2D ) {
	centity_t	*cent;
	vec3_t		angles;
	vec3_t		origin;
	int		weapon;

	if ( !rect || !cg.snap ) {
		return;
	}

	cent = &cg_entities[cg.snap->ps.clientNum];

	if ( draw2D || (!cg_draw3dIcons.integer && cg_drawIcons.integer) ) { // bk001206 - parentheses
		qhandle_t	icon;

		weapon = cg.predictedPlayerState.weapon;
		if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
			return;
		}

		icon = cg_weapons[ weapon ].ammoIcon;
		if ( icon ) {
			CG_DrawPic( rect->x, rect->y, rect->w, rect->h, icon );
		}
	} else if (cg_draw3dIcons.integer) {
		weapon = cent->currentState.weapon;
		if ( weapon > WP_NONE && weapon < WP_NUM_WEAPONS && cg_weapons[ weapon ].ammoModel ) {
			VectorClear( angles );
			origin[0] = 70;
			origin[1] = 0;
			origin[2] = 0;
			angles[YAW] = 90 + 20 * sin( cg.time / 1000.0 );
			CG_Draw3DModel( rect->x, rect->y, rect->w, rect->h, cg_weapons[ weapon ].ammoModel, 0, origin, angles );
		}
	}
}

/*
=============
CG_DrawPlayerAmmoValue

Draws the local ammo count or the retail infinite-ammo fallback icon.
=============
*/
static void CG_DrawPlayerAmmoValue(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle, int align) {
	char	num[16];
	int	value;
	int	weapon;
	float	x;
	float	y;
	float	iconX;
	float	iconSize;
	centity_t	*cent;
	playerState_t	*ps;

	if ( !rect || !cg.snap ) {
		return;
	}

	cent = &cg_entities[cg.snap->ps.clientNum];
	ps = &cg.snap->ps;
	weapon = cent->currentState.weapon;

	if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return;
	}
	if ( weapon == WP_GAUNTLET || weapon == WP_GRAPPLING_HOOK ) {
		return;
	}

	value = ps->ammo[weapon];
	if ( value == -1 ) {
		if ( cgs.media.infiniteAmmoShader ) {
			iconSize = rect->w;
			iconX = rect->x;
			if ( align == ITEM_ALIGN_CENTER ) {
				iconX -= iconSize * 0.5f;
			} else if ( align == ITEM_ALIGN_RIGHT ) {
				iconX -= iconSize;
			}

			trap_R_SetColor( color );
			CG_DrawPic( iconX, rect->y, iconSize, iconSize, cgs.media.infiniteAmmoShader );
			trap_R_SetColor( NULL );
		}
		return;
	}

	if ( value > -1 ) {
		if ( shader ) {
			trap_R_SetColor( color );
			CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );
			trap_R_SetColor( NULL );
		} else {
			Com_sprintf( num, sizeof( num ), "%i", value );
			x = rect->x;
			y = rect->y + CG_Text_Height( num, scale, 0 );
			CG_AlignTextX( &x, num, scale, align );
			CG_Text_Paint( x, y, scale, color, num, 0, 0, textStyle );
		}
	}
}



/*
=============
CG_DrawPlayerHead

Draws the local player's animated HUD head.
=============
*/
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

/*
=============
CG_DrawPlayerScore

Draws the local player score at the retail ownerdraw origin.
=============
*/
static void CG_DrawPlayerScore( rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle ) {
	char	num[16];
	int	value;
	qboolean raceScore;

	if ( !rect || !cg.snap ) {
		return;
	}

	raceScore = qfalse;
	value = cg.snap->ps.persistant[PERS_SCORE];
	if ( cgs.gametype == GT_RACE ) {
		int clientNum = cg.snap->ps.clientNum;

		if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
			return;
		}

		value = cgs.clientinfo[clientNum].score;
		raceScore = qtrue;
	}

	if (shader) {
		trap_R_SetColor( color );
		CG_DrawPic(rect->x, rect->y, rect->w, rect->h, shader);
		trap_R_SetColor( NULL );
	} else {
		if ( value == SCORE_NOT_PRESENT ) {
			return;
		}
		if ( raceScore ) {
			if ( value == 0x7fffffff || value < 0 ) {
				Q_strncpyz( num, "-", sizeof( num ) );
			} else {
				Q_strncpyz( num, CG_FormatSignedWholeSeconds( value ), sizeof( num ) );
			}
		} else {
			Com_sprintf (num, sizeof(num), "%i", value);
		}
		CG_Text_Paint( rect->x, rect->y, scale, color, num, 0, 0, textStyle );
	}
}

/*
=============
CG_DrawPlayerItem

Draws the active holdable item and its retail progress overlay.
=============
*/
static void CG_DrawPlayerItem( rectDef_t *rect, float scale, qboolean draw2D ) {
	int		value;
	char	progressText[16];
	float	progressScale;
	float	progressWidth;
	int		progressPercent;
	vec3_t	origin, angles;

	value = cg.snap->ps.stats[STAT_HOLDABLE_ITEM];
	if ( value ) {
		CG_RegisterItemVisuals( value );

		if ( draw2D ) {
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

		if ( BG_HoldableForItemTag( bg_itemlist[ value ].giTag ) == HI_INVULNERABILITY &&
			cg.snap->ps.stats[STAT_PLAYER_ITEM_TIME] > 0 &&
			cg.snap->ps.stats[STAT_PLAYER_ITEM_TIME_MAX] > 0 ) {
			progressPercent = (int)( ( cg.snap->ps.stats[STAT_PLAYER_ITEM_TIME] * 100.0f ) / cg.snap->ps.stats[STAT_PLAYER_ITEM_TIME_MAX] + 0.5f );
			if ( progressPercent < 0 ) {
				progressPercent = 0;
			} else if ( progressPercent > 100 ) {
				progressPercent = 100;
			}

			Com_sprintf( progressText, sizeof( progressText ), "%d%%", progressPercent );
			progressScale = scale * 0.25f;
			progressWidth = CG_Text_Width( progressText, progressScale, 0 );
			CG_Text_Paint( rect->x + ( rect->w - progressWidth ) * 0.5f, rect->y + rect->h, progressScale,
				colorWhite, progressText, 0.0f, 0, ITEM_TEXTSTYLE_NORMAL );
		}
	}

}

typedef struct {
	int			bit;
	const char	*classname;
} cgKeyIconDef_t;

static const cgKeyIconDef_t cgKeyIconDefs[] = {
	{ KEY_FLAG_SILVER, "item_key_silver" },
	{ KEY_FLAG_GOLD, "item_key_gold" },
	{ KEY_FLAG_MASTER, "item_key_master" }
};

/*
=============
CG_DrawPlayerHasKey

Draws carried key icons from the retail replicated key-mask stat.
=============
*/
static void CG_DrawPlayerHasKey( rectDef_t *rect ) {
	int		mask;
	float	x;
	int		i;

	if ( !rect || !cg.snap ) {
		return;
	}

	mask = cg.snap->ps.stats[STAT_KEY_MASK];
	if ( mask <= 0 ) {
		return;
	}

	x = rect->x;
	for ( i = 0; i < sizeof( cgKeyIconDefs ) / sizeof( cgKeyIconDefs[0] ); i++ ) {
		const cgKeyIconDef_t	*def;
		gitem_t			*item;
		int			itemNum;
		qhandle_t		icon;

		def = &cgKeyIconDefs[i];
		if ( !( mask & def->bit ) ) {
			continue;
		}

		item = BG_FindItemByClassname( def->classname );
		if ( !item || !item->icon || !item->icon[0] ) {
			continue;
		}

		icon = 0;
		itemNum = (int)( item - bg_itemlist );
		if ( itemNum > 0 && itemNum < bg_numItems ) {
			CG_RegisterItemVisuals( itemNum );
			icon = cg_items[itemNum].icon;
		}
		if ( !icon ) {
			icon = trap_R_RegisterShader( item->icon );
		}
		if ( !icon ) {
			continue;
		}

		CG_DrawPic( x, rect->y, rect->w, rect->h, icon );
		x += rect->w * 0.5f;
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

/*
=============
CG_DrawPlayerHealth

Draws the local health count or caller-supplied health shader.
=============
*/
static void CG_DrawPlayerHealth(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle, int align ) {
	playerState_t	*ps;
	int	value;
	char	num[16];
	float	x;
	float	y;

	if ( !rect || !cg.snap ) {
		return;
	}

	ps = &cg.snap->ps;

	value = ps->stats[STAT_HEALTH];

	if (shader) {
		trap_R_SetColor( color );
		CG_DrawPic(rect->x, rect->y, rect->w, rect->h, shader);
		trap_R_SetColor( NULL );
	} else {
		Com_sprintf (num, sizeof(num), "%i", value);
		x = rect->x;
		y = rect->y + CG_Text_Height( num, scale, 0 );
		CG_AlignTextX( &x, num, scale, align );
		CG_Text_Paint( x, y, scale, color, num, 0, 0, textStyle );
	}
}


/*
=============
CG_AlignTextX

Mutates the supplied x anchor to account for center and right aligned text.
=============
*/
static void CG_AlignTextX( float *x, const char *text, float scale, int align ) {
	int textWidth;

	if ( !x ) {
		return;
	}

	textWidth = CG_Text_Width( text ? text : "", scale, 0 );
	if ( align == ITEM_ALIGN_CENTER ) {
		*x -= textWidth * 0.5f;
	} else if ( align == ITEM_ALIGN_RIGHT ) {
		*x -= textWidth;
	}
}

/*
=============
CG_AlignTextInRectX

Returns the x coordinate needed to paint the supplied text with the requested alignment.
=============
*/
static float CG_AlignTextInRectX( const rectDef_t *rect, float scale, const char *text, int align ) {
	if ( !rect ) {
		return 0.0f;
	}

	if ( align == ITEM_ALIGN_CENTER ) {
		return rect->x + ( rect->w - CG_Text_Width( text, scale, 0 ) ) * 0.5f;
	}
	if ( align == ITEM_ALIGN_RIGHT ) {
		return rect->x + rect->w - CG_Text_Width( text, scale, 0 );
	}

	return rect->x;
}

/*
=============
CG_BuildTeamScoreText

Builds the retail text payload for the shared red/blue score ownerdraw.
=============
*/
static qboolean CG_BuildTeamScoreText( team_t team, char *buffer, size_t bufferSize ) {
	int	score;

	if ( !buffer || bufferSize <= 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	score = ( team == TEAM_RED ) ? cgs.scores1 : cgs.scores2;
	if ( score == SCORE_NOT_PRESENT || score == CG_SCORE_FORFEIT ) {
		Q_strncpyz( buffer, "-", bufferSize );
		return qtrue;
	}

	Com_sprintf( buffer, bufferSize, "%i", score );
	return qtrue;
}

/*
=============
CG_DrawTeamScore

Renders the shared retail red/blue score ownerdraw with alignment and widescreen translation.
=============
*/
static void CG_DrawTeamScore( rectDef_t *rect, float scale, vec4_t color, int textStyle, team_t team, int align ) {
	char		buffer[16];
	rectDef_t	widescreenRect;
	float		x;

	if ( !rect || !CG_BuildTeamScoreText( team, buffer, sizeof( buffer ) ) ) {
		return;
	}

	CG_TranslateHudRectForWidescreen( rect, &widescreenRect );
	x = CG_AlignTextInRectX( &widescreenRect, scale, buffer, align );
	CG_Text_Paint( x, widescreenRect.y + widescreenRect.h, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawScoreValue

Restores the retail wrapper over the local and compact placement score ownerdraw
slots. Related retail team-score wiring stays in the ownerdraw dispatcher:
retail case CG_RED_SCORE: CG_DrawTeamScore( rect, scale, color, textStyle, TEAM_RED, ITEM_ALIGN_CENTER );
retail case CG_BLUE_SCORE: CG_DrawTeamScore( rect, scale, color, textStyle, TEAM_BLUE, ITEM_ALIGN_CENTER );
=============
*/
static void CG_DrawScoreValue( rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle, int ownerDraw ) {
	switch ( ownerDraw ) {
	case CG_PLAYER_SCORE:
		CG_DrawPlayerScore( rect, scale, color, shader, textStyle );
		return;
	case CG_1STPLACE:
		if ( cgs.scores1 != SCORE_NOT_PRESENT ) {
			CG_Text_Paint( rect->x, rect->y, scale, color, va( "%2i", cgs.scores1 ), 0, 0, textStyle );
		}
		return;
	case CG_2NDPLACE:
		if ( cgs.scores2 != SCORE_NOT_PRESENT ) {
			CG_Text_Paint( rect->x, rect->y, scale, color, va( "%2i", cgs.scores2 ), 0, 0, textStyle );
		}
		return;
	default:
		return;
	}
}

/*
=============
CG_DrawTeamName

Renders the shared retail red/blue team-name ownerdraw with fallback naming and alignment.
=============
*/
static void CG_DrawTeamName( rectDef_t *rect, float scale, vec4_t color, int textStyle, team_t team, int align ) {
	rectDef_t	widescreenRect;
	const char	*teamName;
	float		x;

	if ( !rect ) {
		return;
	}

	teamName = CG_GetTeamName( team );
	CG_TranslateHudRectForWidescreen( rect, &widescreenRect );
	x = CG_AlignTextInRectX( &widescreenRect, scale, teamName, align );
	CG_Text_Paint( x, widescreenRect.y + widescreenRect.h, scale, color, teamName, 0, 0, textStyle );
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

/*
=============
CG_GetTeamFlagStatusShader

Selects the retail icon used by the shared flag/base-status ownerdraw seam.
=============
*/
static qhandle_t CG_GetTeamFlagStatusShader( team_t team, qboolean baseStatus ) {
	int	status;

	if ( team != TEAM_RED && team != TEAM_BLUE ) {
		return 0;
	}

	if ( cgs.gametype == GT_HARVESTER && !baseStatus ) {
		return ( team == TEAM_RED ) ? cgs.media.redCubeIcon : cgs.media.blueCubeIcon;
	}

	if ( cgs.gametype == GT_1FCTF ) {
		if ( !baseStatus ) {
			return 0;
		}

		if ( team == TEAM_RED && cgs.flagStatus == FLAG_TAKEN_RED ) {
			return cgs.media.flagShader[1];
		}
		if ( team == TEAM_BLUE && cgs.flagStatus == FLAG_TAKEN_BLUE ) {
			return cgs.media.flagShader[2];
		}
		return cgs.media.flagShader[3];
	}

	if ( cgs.gametype != GT_CTF && cgs.gametype != GT_ATTACK_DEFEND && cgs.gametype != GT_OBELISK ) {
		return 0;
	}

	status = ( team == TEAM_RED ) ? cgs.redflag : cgs.blueflag;
	if ( status < FLAG_ATBASE || status > FLAG_DROPPED ) {
		return 0;
	}

	if ( baseStatus && status != FLAG_ATBASE ) {
		status = FLAG_TAKEN;
	}

	return ( team == TEAM_RED ) ? cgs.media.redFlagShader[status] : cgs.media.blueFlagShader[status];
}

/*
=============
CG_DrawTeamFlagOrBaseStatus

Retail shared ownerdraw leaf for red/blue flag and base-status icons.
=============
*/
static void CG_DrawTeamFlagOrBaseStatus( rectDef_t *rect, team_t team, qboolean baseStatus, qhandle_t shader ) {
	qhandle_t	handle;

	if ( shader && !baseStatus && cgs.gametype != GT_1FCTF ) {
		CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );
		return;
	}

	handle = CG_GetTeamFlagStatusShader( team, baseStatus );
	if ( !handle ) {
		return;
	}

	CG_DrawPic( rect->x, rect->y, rect->w, rect->h, handle );
}

static void CG_DrawBlueFlagStatus(rectDef_t *rect, qhandle_t shader) {
	CG_DrawTeamFlagOrBaseStatus( rect, TEAM_BLUE, qfalse, shader );
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
	CG_DrawTeamFlagOrBaseStatus( rect, TEAM_RED, qfalse, shader );
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

/*
=============
CG_HarvesterSkulls

Draws the retail Harvester carried-skull count and cube icon.
=============
*/
static void CG_HarvesterSkulls(rectDef_t *rect, float scale, vec4_t color, qboolean force2D, int textStyle ) {
	char num[16];
	vec3_t origin, angles;
	qhandle_t handle;
	int value;

	if ( !rect || !cg.snap ) {
		return;
	}

	if (cgs.gametype != GT_HARVESTER) {
		return;
	}

	value = cg.snap->ps.generic1 & 0x3f;

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

/*
=============
CG_GetOneFlagStatusShader

Returns the retail one-flag status icon used by the compact objective strip.
=============
*/
static qhandle_t CG_GetOneFlagStatusShader( void ) {
	int	shaderIndex;

	if ( cgs.flagStatus < FLAG_ATBASE || cgs.flagStatus > FLAG_DROPPED ) {
		return 0;
	}

	shaderIndex = 0;
	switch ( cgs.flagStatus ) {
	case FLAG_TAKEN_RED:
		shaderIndex = 1;
		break;
	case FLAG_TAKEN_BLUE:
		shaderIndex = 2;
		break;
	case FLAG_DROPPED:
		shaderIndex = 3;
		break;
	default:
		break;
	}

	return cgs.media.flagShader[shaderIndex];
}

/*
=============
CG_OneFlagStatus

Draws the retail 1FCTF ownerdraw icon.
=============
*/
static void CG_OneFlagStatus(rectDef_t *rect) {
	int		shaderIndex;

	if (cgs.gametype != GT_1FCTF) {
		return;
	}

	if ( cgs.flagStatus < FLAG_ATBASE || cgs.flagStatus > FLAG_DROPPED ) {
		return;
	}

	shaderIndex = 0;
	switch ( cgs.flagStatus ) {
	case FLAG_TAKEN_RED:
		shaderIndex = 1;
		break;
	case FLAG_TAKEN_BLUE:
		shaderIndex = 2;
		break;
	case FLAG_DROPPED:
		shaderIndex = 3;
		break;
	default:
		break;
	}

	CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cgs.media.flagShader[shaderIndex] );
}

/*
=============
CG_FlagStatusText

Converts a flag status enum to the compact status labels used by team overlays.
=============
*/
static const char *CG_FlagStatusText( int status ) {
	switch ( status ) {
	case FLAG_ATBASE:
		return "At Base";
	case FLAG_TAKEN:
		return "Taken";
	case FLAG_DROPPED:
		return "Dropped";
	default:
		return "-";
	}
}

/*
=============
CG_GetTeamBaseFlagState

Resolves the base-state flag enum for a specific team in CTF and 1FCTF.
=============
*/
static int CG_GetTeamBaseFlagState( team_t team ) {
	if ( team != TEAM_RED && team != TEAM_BLUE ) {
		return -1;
	}

	if ( cgs.gametype == GT_CTF ) {
		return ( team == TEAM_RED ) ? cgs.redflag : cgs.blueflag;
	}

	if ( cgs.gametype == GT_1FCTF ) {
		if ( cgs.flagStatus == FLAG_DROPPED ) {
			return FLAG_DROPPED;
		}
		if ( team == TEAM_RED && cgs.flagStatus == FLAG_TAKEN_RED ) {
			return FLAG_TAKEN;
		}
		if ( team == TEAM_BLUE && cgs.flagStatus == FLAG_TAKEN_BLUE ) {
			return FLAG_TAKEN;
		}
		return FLAG_ATBASE;
	}

	return -1;
}

/*
=============
CG_DrawObjectiveStatusTrack

Draws the thin background rail shared by the compact retail objective strips.
=============
*/
static void CG_DrawObjectiveStatusTrack( rectDef_t *rect, float left, float right ) {
	vec4_t	trackColor = { 0.0f, 0.0f, 0.0f, 0.35f };
	vec4_t	dividerColor = { 1.0f, 1.0f, 1.0f, 0.12f };
	float	trackY;
	float	centerX;

	if ( right <= left ) {
		return;
	}

	trackY = rect->y + rect->h * 0.5f - 1.0f;
	centerX = left + ( right - left ) * 0.5f - 1.0f;

	CG_FillRect( left, trackY, right - left, 2.0f, trackColor );
	CG_FillRect( centerX, rect->y + 2.0f, 2.0f, rect->h - 4.0f, dividerColor );
}

/*
=============
CG_DrawObjectiveStatusCtfFamilyStrip

Renders the recovered graphic strip used by the compact CTF-family spectator HUD.
=============
*/
static qboolean CG_DrawObjectiveStatusCtfFamilyStrip( rectDef_t *rect ) {
	qhandle_t	redBaseShader;
	qhandle_t	blueBaseShader;
	qhandle_t	redFlagShader;
	qhandle_t	blueFlagShader;
	float		iconSize;
	float		markerSize;
	float		leftIconX;
	float		rightIconX;
	float		trackLeft;
	float		trackRight;
	float		centerX;
	float		markerY;
	float		redMarkerX;
	float		blueMarkerX;

	if ( cgs.gametype != GT_CTF && cgs.gametype != GT_ATTACK_DEFEND && cgs.gametype != GT_OBELISK ) {
		return qfalse;
	}

	redBaseShader = CG_GetTeamFlagStatusShader( TEAM_RED, qtrue );
	blueBaseShader = CG_GetTeamFlagStatusShader( TEAM_BLUE, qtrue );
	redFlagShader = CG_GetTeamFlagStatusShader( TEAM_RED, qfalse );
	blueFlagShader = CG_GetTeamFlagStatusShader( TEAM_BLUE, qfalse );
	if ( !redBaseShader && !blueBaseShader && !redFlagShader && !blueFlagShader ) {
		return qfalse;
	}

	iconSize = rect->h;
	markerSize = rect->h * 0.75f;
	leftIconX = rect->x;
	rightIconX = rect->x + rect->w - iconSize;
	trackLeft = leftIconX + iconSize + 6.0f;
	trackRight = rightIconX - 6.0f;
	centerX = trackLeft + ( trackRight - trackLeft ) * 0.5f;
	markerY = rect->y + ( rect->h - markerSize ) * 0.5f;

	if ( redBaseShader ) {
		CG_DrawPic( leftIconX, rect->y, iconSize, iconSize, redBaseShader );
	}
	if ( blueBaseShader ) {
		CG_DrawPic( rightIconX, rect->y, iconSize, iconSize, blueBaseShader );
	}

	CG_DrawObjectiveStatusTrack( rect, trackLeft, trackRight );

	redMarkerX = centerX - markerSize * 0.5f;
	if ( cgs.redflag == FLAG_ATBASE ) {
		redMarkerX = trackLeft - markerSize * 0.5f;
	} else if ( cgs.redflag == FLAG_TAKEN ) {
		redMarkerX = trackRight - markerSize * 0.5f;
	} else if ( cgs.redflag == FLAG_DROPPED ) {
		redMarkerX = centerX - markerSize * 1.05f;
	}

	blueMarkerX = centerX - markerSize * 0.5f;
	if ( cgs.blueflag == FLAG_ATBASE ) {
		blueMarkerX = trackRight - markerSize * 0.5f;
	} else if ( cgs.blueflag == FLAG_TAKEN ) {
		blueMarkerX = trackLeft - markerSize * 0.5f;
	} else if ( cgs.blueflag == FLAG_DROPPED ) {
		blueMarkerX = centerX + markerSize * 0.05f;
	}

	if ( redFlagShader && cgs.redflag >= FLAG_ATBASE && cgs.redflag <= FLAG_DROPPED ) {
		CG_DrawPic( redMarkerX, markerY, markerSize, markerSize, redFlagShader );
	}
	if ( blueFlagShader && cgs.blueflag >= FLAG_ATBASE && cgs.blueflag <= FLAG_DROPPED ) {
		CG_DrawPic( blueMarkerX, markerY, markerSize, markerSize, blueFlagShader );
	}

	return qtrue;
}

/*
=============
CG_DrawObjectiveStatusOneFlagStrip

Renders the recovered compact neutral-flag icon strip for 1FCTF.
=============
*/
static qboolean CG_DrawObjectiveStatusOneFlagStrip( rectDef_t *rect ) {
	qhandle_t	redBaseShader;
	qhandle_t	blueBaseShader;
	qhandle_t	flagShader;
	float		iconSize;
	float		leftIconX;
	float		rightIconX;
	float		centerX;

	if ( cgs.gametype != GT_1FCTF ) {
		return qfalse;
	}

	flagShader = CG_GetOneFlagStatusShader();
	if ( !flagShader ) {
		return qfalse;
	}

	iconSize = rect->h;
	leftIconX = rect->x;
	rightIconX = rect->x + rect->w - iconSize;
	centerX = rect->x + ( rect->w - iconSize ) * 0.5f;
	redBaseShader = CG_GetTeamFlagStatusShader( TEAM_RED, qtrue );
	blueBaseShader = CG_GetTeamFlagStatusShader( TEAM_BLUE, qtrue );

	CG_DrawObjectiveStatusTrack( rect, leftIconX + iconSize + 6.0f, rightIconX - 6.0f );
	if ( redBaseShader ) {
		CG_DrawPic( leftIconX, rect->y, iconSize, iconSize, redBaseShader );
	}
	if ( blueBaseShader ) {
		CG_DrawPic( rightIconX, rect->y, iconSize, iconSize, blueBaseShader );
	}
	CG_DrawPic( centerX, rect->y, iconSize, iconSize, flagShader );
	return qtrue;
}

/*
=============
CG_DrawObjectiveStatusHarvesterStrip

Renders the compact Harvester strip from the already-registered cube icons.
=============
*/
static qboolean CG_DrawObjectiveStatusHarvesterStrip( rectDef_t *rect ) {
	float	iconSize;
	float	centerX;

	if ( cgs.gametype != GT_HARVESTER ) {
		return qfalse;
	}

	if ( !cgs.media.redCubeIcon && !cgs.media.blueCubeIcon ) {
		return qfalse;
	}

	iconSize = rect->h;
	centerX = rect->x + ( rect->w - iconSize ) * 0.5f;

	CG_DrawObjectiveStatusTrack( rect, rect->x + iconSize + 6.0f, rect->x + rect->w - iconSize - 6.0f );
	if ( cgs.media.redCubeIcon ) {
		CG_DrawPic( rect->x, rect->y, iconSize, iconSize, cgs.media.redCubeIcon );
	}
	if ( cgs.media.flagShader[0] ) {
		CG_DrawPic( centerX, rect->y, iconSize, iconSize, cgs.media.flagShader[0] );
	}
	if ( cgs.media.blueCubeIcon ) {
		CG_DrawPic( rect->x + rect->w - iconSize, rect->y, iconSize, iconSize, cgs.media.blueCubeIcon );
	}
	return qtrue;
}

/*
=============
CG_ObjectiveStatusDominationClampTeam

Normalizes the transmitted Domination team owner/capturer values.
=============
*/
static team_t CG_ObjectiveStatusDominationClampTeam( int value ) {
	if ( value >= TEAM_RED && value <= TEAM_SPECTATOR ) {
		return (team_t)value;
	}

	return TEAM_FREE;
}

/*
=============
CG_ObjectiveStatusDominationProgressIndex

Buckets the transmitted Domination capture progress for strip shader lookup.
=============
*/
static int CG_ObjectiveStatusDominationProgressIndex( float progress ) {
	float	clamped;
	int		index;

	clamped = Com_Clamp( 0.0f, 1.0f, progress );
	index = (int)( clamped * DOM_POINT_STATE_COUNT );
	if ( index >= DOM_POINT_STATE_COUNT ) {
		index = DOM_POINT_STATE_COUNT - 1;
	}

	return index;
}

/*
=============
CG_ObjectiveStatusDominationSelectShader

Picks the capture/defense strip shader for a Domination control point.
=============
*/
static qhandle_t CG_ObjectiveStatusDominationSelectShader( qboolean capture, qboolean distress, int index ) {
	if ( index < 0 || index >= DOM_POINT_STATE_COUNT ) {
		return 0;
	}

	if ( capture ) {
		return distress ? cgs.media.domCapDistressShaders[index] : cgs.media.domCapShaders[index];
	}

	return distress ? cgs.media.domDefDistressShaders[index] : cgs.media.domDefShaders[index];
}

/*
=============
CG_DrawObjectiveStatusDominationStrip

Renders the compact Domination control-point strip from the live ET_TEAM state.
=============
*/
static qboolean CG_DrawObjectiveStatusDominationStrip( rectDef_t *rect ) {
	centity_t	*points[DOMINATION_MAX_POINTS];
	team_t		viewerTeam;
	int		count;
	int		slot;
	int		i;
	float		iconSize;
	float		totalWidth;
	float		gap;
	float		x;

	if ( cgs.gametype != GT_DOMINATION ) {
		return qfalse;
	}

	memset( points, 0, sizeof( points ) );
	count = 0;
	for ( i = 0; i < MAX_GENTITIES; i++ ) {
		centity_t	*cent;
		int		pointIndex;

		cent = &cg_entities[i];
		if ( cent->currentState.eType != ET_TEAM ) {
			continue;
		}

		pointIndex = cent->currentState.clientNum - 1;
		if ( pointIndex < 0 || pointIndex >= DOMINATION_MAX_POINTS || points[pointIndex] ) {
			continue;
		}

		points[pointIndex] = cent;
		count++;
	}

	if ( count <= 0 ) {
		return qfalse;
	}

	viewerTeam = TEAM_FREE;
	if ( cg.snap ) {
		viewerTeam = (team_t)cg.snap->ps.persistant[PERS_TEAM];
	}

	iconSize = rect->h;
	gap = 4.0f;
	totalWidth = count * iconSize + ( count - 1 ) * gap;
	x = rect->x + ( rect->w - totalWidth ) * 0.5f;

	for ( slot = 0; slot < DOMINATION_MAX_POINTS; slot++ ) {
		centity_t	*cent;
		team_t		owner;
		team_t		capturing;
		qboolean	captureIcon;
		qboolean	distress;
		int		progressIndex;
		qhandle_t	shader;

		cent = points[slot];
		if ( !cent ) {
			continue;
		}

		owner = CG_ObjectiveStatusDominationClampTeam( cent->currentState.modelindex );
		capturing = CG_ObjectiveStatusDominationClampTeam( cent->currentState.modelindex2 );
		if ( capturing == TEAM_FREE ) {
			x += iconSize + gap;
			continue;
		}

		captureIcon = qtrue;
		if ( viewerTeam == owner && owner != TEAM_FREE ) {
			captureIcon = qfalse;
		} else if ( viewerTeam == TEAM_FREE || viewerTeam == TEAM_SPECTATOR || owner == TEAM_FREE ) {
			captureIcon = qtrue;
		}

		distress = qfalse;
		if ( cent->currentState.time2 > 0 ) {
			distress = ( cg.time - cent->currentState.time2 ) <= DOMINATION_DISTRESS_REPEAT_TIME;
		}

		progressIndex = CG_ObjectiveStatusDominationProgressIndex( (float)cent->currentState.frame / 255.0f );
		shader = CG_ObjectiveStatusDominationSelectShader( captureIcon, distress, progressIndex );
		if ( shader ) {
			CG_DrawPic( x, rect->y, iconSize, iconSize, shader );
		}

		x += iconSize + gap;
	}

	return qtrue;
}

/*
=============
CG_DrawObjectiveStatusStrip

Attempts the recovered retail graphic objective strip before the text fallback.
=============
*/
static qboolean CG_DrawObjectiveStatusStrip( rectDef_t *rect ) {
	if ( CG_DrawObjectiveStatusCtfFamilyStrip( rect ) ) {
		return qtrue;
	}

	if ( CG_DrawObjectiveStatusOneFlagStrip( rect ) ) {
		return qtrue;
	}

	if ( CG_DrawObjectiveStatusHarvesterStrip( rect ) ) {
		return qtrue;
	}

	return CG_DrawObjectiveStatusDominationStrip( rect );
}

/*
=============
CG_BuildObjectiveStatusLabel

Builds human-readable objective text for the broader CG_FLAG_STATUS slot.
=============
*/
static qboolean CG_BuildObjectiveStatusLabel( char *buffer, size_t bufferSize ) {
	int		redStatus;
	int		blueStatus;

	if ( !buffer || bufferSize <= 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';

	if ( cgs.gametype == GT_CTF ) {
		if ( cgs.redflag == FLAG_TAKEN && cgs.blueflag == FLAG_TAKEN ) {
			Q_strncpyz( buffer, "Both Flags Taken", bufferSize );
		} else if ( cgs.redflag == FLAG_TAKEN ) {
			Com_sprintf( buffer, bufferSize, "%s Flag Taken", CG_GetTeamName( TEAM_RED ) );
		} else if ( cgs.blueflag == FLAG_TAKEN ) {
			Com_sprintf( buffer, bufferSize, "%s Flag Taken", CG_GetTeamName( TEAM_BLUE ) );
		} else if ( cgs.redflag == FLAG_DROPPED ) {
			Com_sprintf( buffer, bufferSize, "%s Flag Dropped", CG_GetTeamName( TEAM_RED ) );
		} else if ( cgs.blueflag == FLAG_DROPPED ) {
			Com_sprintf( buffer, bufferSize, "%s Flag Dropped", CG_GetTeamName( TEAM_BLUE ) );
		} else {
			Q_strncpyz( buffer, "Flags At Base", bufferSize );
		}
		return qtrue;
	}

	if ( cgs.gametype == GT_1FCTF ) {
		switch ( cgs.flagStatus ) {
		case FLAG_TAKEN_RED:
			Com_sprintf( buffer, bufferSize, "%s Has Flag", CG_GetTeamName( TEAM_RED ) );
			break;
		case FLAG_TAKEN_BLUE:
			Com_sprintf( buffer, bufferSize, "%s Has Flag", CG_GetTeamName( TEAM_BLUE ) );
			break;
		case FLAG_DROPPED:
			Q_strncpyz( buffer, "Neutral Flag Dropped", bufferSize );
			break;
		default:
			Q_strncpyz( buffer, "Neutral Flag At Base", bufferSize );
			break;
		}
		return qtrue;
	}

	if ( cgs.gametype == GT_ATTACK_DEFEND ) {
		redStatus = cgs.redflag;
		blueStatus = cgs.blueflag;
		if ( redStatus < FLAG_ATBASE || redStatus > FLAG_DROPPED ||
			blueStatus < FLAG_ATBASE || blueStatus > FLAG_DROPPED ) {
			return qfalse;
		}

		Com_sprintf( buffer, bufferSize, "%s %s  %s %s",
			CG_GetTeamName( TEAM_RED ), CG_FlagStatusText( redStatus ),
			CG_GetTeamName( TEAM_BLUE ), CG_FlagStatusText( blueStatus ) );
		return qtrue;
	}

	return qfalse;
}

/*
=============
CG_DrawObjectiveStatus

Draws the broader retail objective-status ownerdraw text fallback.
=============
*/
static void CG_DrawObjectiveStatus( rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
	char buffer[64];

	if ( CG_DrawObjectiveStatusStrip( rect ) ) {
		return;
	}

	if ( !CG_BuildObjectiveStatusLabel( buffer, sizeof( buffer ) ) ) {
		return;
	}

	CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_DrawTeamBaseStatus

Draws a team-specific base status icon for CTF/1FCTF team overlays.
=============
*/
static void CG_DrawTeamBaseStatus( rectDef_t *rect, float scale, vec4_t color, int textStyle, team_t team ) {
	(void)scale;
	(void)color;
	(void)textStyle;

	if ( CG_GetTeamBaseFlagState( team ) < 0 ) {
		return;
	}

	CG_DrawTeamFlagOrBaseStatus( rect, team, qtrue, 0 );
}


/*
=============
CG_DrawCTFPowerUp

Draws the local persistent powerup item icon.
=============
*/
static void CG_DrawCTFPowerUp(rectDef_t *rect) {
	int		value;

	if ( !rect || !cg.snap ) {
		return;
	}

	value = cg.snap->ps.stats[STAT_PERSISTANT_POWERUP];
	if ( value <= 0 || value >= bg_numItems ) {
		return;
	}

	CG_RegisterItemVisuals( value );
	if ( cg_items[ value ].icon ) {
		CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cg_items[ value ].icon );
	}
}

/*
=============
CG_DrawTeamColor

Draws the retail team-color ownerdraw background.
=============
*/
static void CG_DrawTeamColor( rectDef_t *rect, vec4_t color ) {
	if ( !rect || !cg.snap ) {
		return;
	}

	CG_DrawTeamBackground( rect->x, rect->y, rect->w, rect->h, color[3], cg.snap->ps.persistant[PERS_TEAM] );
}

/*
=============
CG_DrawPowerupSpriteStack

Renders a stacked list of active powerups, mirroring the retail sprite stack.
=============
*/
static void CG_DrawPowerupSpriteStack( rectDef_t *rect, int align, float special, float scale, vec4_t color, const playerState_t *ps ) {
	char num[16];
	int			sorted[MAX_POWERUPS];
	int			sortedTime[MAX_POWERUPS];
	int			i, j;
	int			active;
	int			t;
	gitem_t	*item;
	float		f;
	rectDef_t r2;
	float *inc;
	float		baseStep;
	float		stackScale;
	float		iconWidth;
	float		iconHeight;
	float		iconOffset;
	float		textOffsetX;
	float		textScale;

	if ( !rect || !ps || ps->stats[STAT_HEALTH] <= 0 ) {
		return;
	}

	r2.x = rect->x;
	r2.y = rect->y;
	r2.w = rect->w;
	r2.h = rect->h;
	inc = (align == HUD_VERTICAL) ? &r2.y : &r2.x;
	baseStep = (align == HUD_VERTICAL) ? r2.h : r2.w;
	stackScale = 1.0f;

	active = 0;
	for ( i = 1; i < MAX_POWERUPS; i++ ) {
		if ( i == PW_NEUTRALFLAG || i == PW_NUM_POWERUPS ) {
			continue;
		}

		if ( !ps->powerups[i] || ps->powerups[i] == 0x7fffffff ) {
			continue;
		}

		t = ps->powerups[i] - cg.time;
		if ( t <= 0 || t >= 999000 ) {
			continue;
		}

		for ( j = active; j > 0 && t < sortedTime[j - 1]; j-- ) {
			sorted[j] = sorted[j - 1];
			sortedTime[j] = sortedTime[j - 1];
		}

		sorted[j] = i;
		sortedTime[j] = t;
		active++;
	}

	if (!active) {
		return;
	}

	if (baseStep > 0.0f) {
		float neededSpan;
		float availableSpan;

		neededSpan = (active * baseStep) + ((active - 1) * special);
		availableSpan = (align == HUD_VERTICAL) ? rect->h : rect->w;
		if (availableSpan > 0.0f && neededSpan > availableSpan) {
			stackScale = availableSpan / neededSpan;
		}
	}

	iconWidth = (r2.w * 0.75f) * stackScale;
	iconHeight = r2.h * stackScale;
	iconOffset = (baseStep + special) * stackScale;
	textOffsetX = iconWidth + 3.0f;
	textScale = scale * stackScale;

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

		CG_DrawPic(r2.x, r2.y, iconWidth, iconHeight, trap_R_RegisterShader(item->icon));
		Com_sprintf(num, sizeof(num), "%i", sortedTime[i] / 1000 + 1);
		CG_Text_Paint(r2.x + textOffsetX, r2.y + iconHeight, textScale, color, num, 0, 0, 0);
		*inc += iconOffset;
	}

	trap_R_SetColor(NULL);
}

/*
=============
CG_DrawAreaPowerUp

Draws the local area powerup stack when sprite self-display allows it.
=============
*/
static void CG_DrawAreaPowerUp( rectDef_t *rect, int align, float special, float scale, vec4_t color ) {
	if ( !rect || !cg.snap || !cg_drawSprites.integer ) {
		return;
	}

	if ( !CG_ShouldDrawSpriteSelf() && !( cg.snap->ps.pm_flags & PMF_FOLLOW ) && cg.snap->ps.clientNum == cg.clientNum ) {
		return;
	}

	CG_DrawPowerupSpriteStack( rect, align, special, scale, color, &cg.snap->ps );
}

/*
=============
CG_GetValue

Returns the retail ownerdraw score/stat callback values for menu-driven HUD
items.
=============
*/
float CG_GetValue(int ownerDraw) {
	centity_t	*cent;
	playerState_t	*ps;

	cent = &cg_entities[cg.snap->ps.clientNum];
	ps = &cg.snap->ps;

	switch (ownerDraw) {
	case CG_PLAYER_ARMOR_VALUE:
		return ps->stats[STAT_ARMOR];
	case CG_PLAYER_AMMO_VALUE:
		if ( cent->currentState.weapon ) {
			return ps->ammo[cent->currentState.weapon];
		}
		break;
	case CG_PLAYER_SCORE:
		return cg.snap->ps.persistant[PERS_SCORE];
	case CG_PLAYER_HEALTH:
		return ps->stats[STAT_HEALTH];
	case CG_RED_SCORE:
		return cgs.scores1;
	case CG_BLUE_SCORE:
		return cgs.scores2;
	default:
		break;
	}
	return -1;
}


/*
=============
CG_PlacementSlotContainsPredictedPlayer

Checks whether the active predicted player is represented by the requested
retail placement slot.
=============
*/
static qboolean CG_PlacementSlotContainsPredictedPlayer( int slot ) {
	const score_t	*score;

	if ( !cg.snap ) {
		return qfalse;
	}

	if ( cg.snap->ps.pm_type == PM_SPECTATOR ) {
		return qtrue;
	}

	score = CG_GetPlacementScore( slot );
	if ( !score ) {
		return qfalse;
	}

	return ( score->client == cg.snap->ps.clientNum ) ? qtrue : qfalse;
}

/*
=============
CG_PlacementSlotCanBeFollowed

Checks whether the requested placement slot points at a client other than the
active predicted player.
=============
*/
static qboolean CG_PlacementSlotCanBeFollowed( int slot ) {
	const score_t	*score;

	if ( !cg.snap ) {
		return qfalse;
	}

	score = CG_GetPlacementScore( slot );
	if ( !score ) {
		return qfalse;
	}

	return ( score->client != cg.snap->ps.clientNum ) ? qtrue : qfalse;
}

/*
=============
CG_PlacementWeaponFired

Mirrors the retail duel scoreboard weapon-row visibility cache checks for the
first two placement rows.
=============
*/
static qboolean CG_PlacementWeaponFired( weapon_t weapon ) {
	int	i;

	if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return qfalse;
	}

	for ( i = 0; i < cg.numScores && i < 2; i++ ) {
		const score_t		*score;
		const cgScoreStats_t	*stats;
		int			value;

		score = CG_GetPlacementScore( i );
		stats = CG_GetPlacementScoreStats( score );
		if ( !stats ) {
			continue;
		}

		if ( weapon == WP_GAUNTLET ) {
			value = stats->weaponShots[weapon];
		} else {
			value = stats->weaponDamage[weapon];
		}

		if ( value != 0 ) {
			return qtrue;
		}
	}

	return qfalse;
}

/*
=============
CG_LoadoutsEnabled

Determines whether the retail cg_loadout serverinfo mirror is enabled.
=============
*/
static qboolean CG_LoadoutsEnabled( void ) {
	return ( cg_loadout.integer != 0 ) ? qtrue : qfalse;
}

/*
=============
CG_OtherTeamHasFlag

Retail visibility predicate for the `CG_SHOW_OTHERTEAMHASFLAG` display flag.
=============
*/
qboolean CG_OtherTeamHasFlag( void ) {
	if (cgs.gametype == GT_CTF || cgs.gametype == GT_1FCTF || cgs.gametype == GT_ATTACK_DEFEND) {
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

/*
=============
CG_YourTeamHasFlag

Retail visibility predicate for the `CG_SHOW_YOURTEAMHASENEMYFLAG` display flag.
=============
*/
qboolean CG_YourTeamHasFlag( void ) {
	if (cgs.gametype == GT_CTF || cgs.gametype == GT_1FCTF || cgs.gametype == GT_ATTACK_DEFEND) {
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
CG_ShowBlueTeamHasRedFlag

HUD visibility helper for the blue-team carrier predicate.
=============
*/
static qboolean CG_ShowBlueTeamHasRedFlag( void ) {
	if ( cgs.gametype != GT_CTF && cgs.gametype != GT_1FCTF && cgs.gametype != GT_ATTACK_DEFEND ) {
		return qfalse;
	}

	if ( cgs.gametype == GT_1FCTF ) {
		return ( cgs.flagStatus == FLAG_TAKEN_BLUE ) ? qtrue : qfalse;
	}

	return ( cgs.redflag == FLAG_TAKEN || cgs.flagStatus == FLAG_TAKEN_RED ) ? qtrue : qfalse;
}

/*
=============
CG_ShowRedTeamHasBlueFlag

HUD visibility helper for the red-team carrier predicate.
=============
*/
static qboolean CG_ShowRedTeamHasBlueFlag( void ) {
	if ( cgs.gametype != GT_CTF && cgs.gametype != GT_1FCTF && cgs.gametype != GT_ATTACK_DEFEND ) {
		return qfalse;
	}

	if ( cgs.gametype == GT_1FCTF ) {
		return ( cgs.flagStatus == FLAG_TAKEN_RED ) ? qtrue : qfalse;
	}

	return ( cgs.blueflag == FLAG_TAKEN || cgs.flagStatus == FLAG_TAKEN_BLUE ) ? qtrue : qfalse;
}

/*
=============
CG_HudNotificationVisible

Mirrors the retail notification visibility gate: a live timeout must be armed,
and the icon blinks on the 0x200 time bit while the timeout is active.
=============
*/
static qboolean CG_HudNotificationVisible( int expireTime ) {
	if ( expireTime <= 0 || expireTime < cg.time ) {
		return qfalse;
	}

	return ( cg.time & 0x200 ) ? qtrue : qfalse;
}

/*
=============
CG_HasHudNoticeMessage

Reports whether the second retail notification icon should be visible.
=============
*/
static qboolean CG_HasHudNoticeMessage( void ) {
	return CG_HudNotificationVisible( cg.spectatorSlotTrackedTime[1] );
}

/*
=============
CG_HasHudPlayerMessage

Reports whether the first retail notification icon should be visible.
=============
*/
static qboolean CG_HasHudPlayerMessage( void ) {
	return CG_HudNotificationVisible( cg.spectatorSlotTrackedTime[0] );
}

/*
=============
CG_ShowPlayersRemaining

Returns qtrue for the round-based team modes that drive the players-remaining
HUD strips.
=============
*/
static qboolean CG_ShowPlayersRemaining( void ) {
	switch ( cgs.gametype ) {
	case GT_CLAN_ARENA:
	case GT_FREEZE:
	case GT_ATTACK_DEFEND:
	case GT_RED_ROVER:
		return qtrue;
	default:
		return qfalse;
	}
}

/*
=============
CG_GetLeadingHudTeam

Resolves which team owns the leading placement slot for team HUD layouts.
=============
*/
static team_t CG_GetLeadingHudTeam( void ) {
	if ( cgs.scores1 != SCORE_NOT_PRESENT && cgs.scores2 != SCORE_NOT_PRESENT && cgs.scores1 < cgs.scores2 ) {
		return TEAM_BLUE;
	}

	return TEAM_RED;
}

/*
=============
CG_ShowPlayerIsFirstPlace

Tracks whether the active local or followed player occupies the current top
placement slot on the non-team HUD.
=============
*/
static qboolean CG_ShowPlayerIsFirstPlace( void ) {
	clientInfo_t	*ci;
	int		clientNum;
	int		rank;

	if ( !cg.snap ) {
		return qfalse;
	}

	clientNum = cg.snap->ps.clientNum;
	if ( clientNum < 0 || clientNum >= cgs.maxclients ) {
		return qfalse;
	}

	if ( cgs.gametype >= GT_TEAM && cgs.gametype != GT_RED_ROVER ) {
		ci = &cgs.clientinfo[clientNum];
		if ( ci->team == TEAM_RED ) {
			return ( cgs.scores1 >= cgs.scores2 ) ? qtrue : qfalse;
		}
		if ( ci->team == TEAM_BLUE ) {
			return ( cgs.scores2 > cgs.scores1 ) ? qtrue : qfalse;
		}
		return qfalse;
	}

	rank = cg.snap->ps.persistant[PERS_RANK];
	if ( rank & RANK_TIED_FLAG ) {
		return qfalse;
	}

	return ( rank == 0 ) ? qtrue : qfalse;
}

/*
=============
CG_OwnerDrawPrimaryFlagVisible

Evaluates the primary retail ownerdraw visibility flag word.
=============
*/
static qboolean CG_OwnerDrawPrimaryFlagVisible( int flags ) {
	team_t	playerTeam;

	if ( flags & CG_SHOW_TEAMINFO ) {
		return ( cg_currentSelectedPlayer.integer == numSortedTeamPlayers ) ? qtrue : qfalse;
	}

	if ( flags & CG_SHOW_NOTEAMINFO ) {
		return ( cg_currentSelectedPlayer.integer != numSortedTeamPlayers ) ? qtrue : qfalse;
	}

	if ( flags & CG_SHOW_OTHERTEAMHASFLAG ) {
		return CG_OtherTeamHasFlag();
	}

	if ( flags & CG_SHOW_YOURTEAMHASENEMYFLAG ) {
		return CG_YourTeamHasFlag();
	}

	if ( flags & ( CG_SHOW_BLUE_TEAM_HAS_REDFLAG | CG_SHOW_RED_TEAM_HAS_BLUEFLAG ) ) {
		if ( ( flags & CG_SHOW_BLUE_TEAM_HAS_REDFLAG ) && CG_ShowBlueTeamHasRedFlag() ) {
			return qtrue;
		}
		if ( ( flags & CG_SHOW_RED_TEAM_HAS_BLUEFLAG ) && CG_ShowRedTeamHasBlueFlag() ) {
			return qtrue;
		}
	}

	if ( ( flags & CG_SHOW_PLAYERS_REMAINING ) && CG_ShowPlayersRemaining() ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_DUEL ) && cgs.gametype == GT_TOURNAMENT ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_CLAN_ARENA ) && cgs.gametype == GT_CLAN_ARENA ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_CTF ) && cgs.gametype == GT_CTF ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_ONEFLAG ) && cgs.gametype == GT_1FCTF ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_OBELISK ) && cgs.gametype == GT_OBELISK ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_HARVESTER ) && cgs.gametype == GT_HARVESTER ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_DOMINATION ) && cgs.gametype == GT_DOMINATION ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_ANYNONTEAMGAME ) && cgs.gametype < GT_TEAM ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_ANYTEAMGAME ) && cgs.gametype >= GT_TEAM ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_HEALTHCRITICAL ) && cg.snap->ps.stats[STAT_HEALTH] < 25 ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_IF_NOT_WARMUP ) && cg.warmup >= 0 ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_IF_PLAYER_HAS_FLAG ) &&
		( cg.snap->ps.powerups[PW_REDFLAG] || cg.snap->ps.powerups[PW_BLUEFLAG] ||
			cg.snap->ps.powerups[PW_NEUTRALFLAG] ) ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_IF_WARMUP ) && cg.warmup < 0 ) {
		return qtrue;
	}

	if ( flags & ( CG_SHOW_IF_BLUE_IS_FIRST_PLACE | CG_SHOW_IF_RED_IS_FIRST_PLACE ) ) {
		team_t leadingTeam = CG_GetLeadingHudTeam();

		if ( ( flags & CG_SHOW_IF_BLUE_IS_FIRST_PLACE ) && leadingTeam == TEAM_BLUE ) {
			return qtrue;
		}
		if ( ( flags & CG_SHOW_IF_RED_IS_FIRST_PLACE ) && leadingTeam == TEAM_RED ) {
			return qtrue;
		}
	}

	if ( ( flags & CG_SHOW_INTERMISSION ) && cg.snap->ps.pm_type == PM_INTERMISSION ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_NOTINTERMISSION ) && cg.snap->ps.pm_type != PM_INTERMISSION ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_IF_MSG_PRESENT ) && CG_HasHudPlayerMessage() ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_IF_NOTICE_PRESENT ) && CG_HasHudNoticeMessage() ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_IF_CHAT_VISIBLE ) && ( cg.chatHistoryVisible || cg.scoreBoardShowing ) ) {
		return qtrue;
	}

	if ( flags & ( CG_SHOW_IF_PLYR_IS_FIRST_PLACE | CG_SHOW_IF_PLYR_IS_NOT_FIRST_PLACE ) ) {
		qboolean isFirstPlace = CG_ShowPlayerIsFirstPlace();

		if ( ( flags & CG_SHOW_IF_PLYR_IS_FIRST_PLACE ) && isFirstPlace ) {
			return qtrue;
		}
		if ( ( flags & CG_SHOW_IF_PLYR_IS_NOT_FIRST_PLACE ) && !isFirstPlace ) {
			return qtrue;
		}
	}

	playerTeam = TEAM_FREE;
	if ( cg.snap ) {
		playerTeam = (team_t)cg.snap->ps.persistant[PERS_TEAM];
	}

	if ( ( flags & CG_SHOW_IF_PLYR_IS_ON_RED ) && playerTeam == TEAM_RED ) {
		return qtrue;
	}

	if ( ( flags & CG_SHOW_IF_PLYR_IS_ON_BLUE ) && playerTeam == TEAM_BLUE ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
CG_OwnerDrawSecondaryFlagVisible

Evaluates Quake Live's retail secondary ownerdraw visibility flag word.
=============
*/
static qboolean CG_OwnerDrawSecondaryFlagVisible( int flags2 ) {
	team_t	playerTeam;
	int	pmType;
	qboolean	loadoutsEnabled;

	if ( ( flags2 & CG_SHOW_IF_PLYR1 ) && CG_PlacementSlotContainsPredictedPlayer( 0 ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_PLYR2 ) && CG_PlacementSlotContainsPredictedPlayer( 1 ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_G_FIRED ) && CG_PlacementWeaponFired( WP_GAUNTLET ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_MG_FIRED ) && CG_PlacementWeaponFired( WP_MACHINEGUN ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_SG_FIRED ) && CG_PlacementWeaponFired( WP_SHOTGUN ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_GL_FIRED ) && CG_PlacementWeaponFired( WP_GRENADE_LAUNCHER ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_RL_FIRED ) && CG_PlacementWeaponFired( WP_ROCKET_LAUNCHER ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_LG_FIRED ) && CG_PlacementWeaponFired( WP_LIGHTNING ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_RG_FIRED ) && CG_PlacementWeaponFired( WP_RAILGUN ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_PG_FIRED ) && CG_PlacementWeaponFired( WP_PLASMAGUN ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_BFG_FIRED ) && CG_PlacementWeaponFired( WP_BFG ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_CG_FIRED ) && CG_PlacementWeaponFired( WP_CHAINGUN ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_NG_FIRED ) && CG_PlacementWeaponFired( WP_NAILGUN ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_PL_FIRED ) && CG_PlacementWeaponFired( WP_PROX_LAUNCHER ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_HMG_FIRED ) && CG_PlacementWeaponFired( WP_HEAVY_MACHINEGUN ) ) {
		return qtrue;
	}

	loadoutsEnabled = CG_LoadoutsEnabled();
	if ( ( flags2 & CG_SHOW_IF_LOADOUT_ENABLED ) && loadoutsEnabled ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_LOADOUT_DISABLED ) && !loadoutsEnabled ) {
		return qtrue;
	}

	playerTeam = TEAM_FREE;
	pmType = PM_NORMAL;
	if ( cg.snap ) {
		playerTeam = (team_t)cg.snap->ps.persistant[PERS_TEAM];
		pmType = cg.snap->ps.pm_type;
	}

	if ( ( flags2 & CG_SHOW_IF_PLYR_IS_ON_RED_OR_SPEC ) && ( playerTeam == TEAM_RED || pmType == PM_SPECTATOR ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_PLYR_IS_ON_BLUE_OR_SPEC ) && ( playerTeam == TEAM_BLUE || pmType == PM_SPECTATOR ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_PLYR_IS_ON_RED_NO_SPEC ) && playerTeam == TEAM_RED && pmType != PM_SPECTATOR ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_PLYR_IS_ON_BLUE_NO_SPEC ) && playerTeam == TEAM_BLUE && pmType != PM_SPECTATOR ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_1ST_PLYR_FOLLOWED ) && CG_PlacementSlotCanBeFollowed( 0 ) ) {
		return qtrue;
	}

	if ( ( flags2 & CG_SHOW_IF_2ND_PLYR_FOLLOWED ) && CG_PlacementSlotCanBeFollowed( 1 ) ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
CG_OwnerDrawVisible

Evaluates the ownerdraw visibility bitmasks for HUD and menu scripts.
=============
*/
qboolean CG_OwnerDrawVisible(int flags, int flags2) {
	if ( flags && CG_OwnerDrawPrimaryFlagVisible( flags ) ) {
		return qtrue;
	}

	if ( flags2 && CG_OwnerDrawSecondaryFlagVisible( flags2 ) ) {
		return qtrue;
	}

	return qfalse;
}


/*
=============
CG_DrawPlayerHasFlag

Draws the flag currently carried by the local predicted player state.
=============
*/
static void CG_DrawPlayerHasFlag(rectDef_t *rect, qboolean force2D) {
	int		flagTeam;
	float	inset;

	flagTeam = -1;
	inset = force2D ? 0.0f : 4.0f;

	if ( cg.predictedPlayerState.powerups[PW_REDFLAG] ) {
		flagTeam = TEAM_RED;
	} else if ( cg.predictedPlayerState.powerups[PW_BLUEFLAG] ) {
		flagTeam = TEAM_BLUE;
	} else if ( cg.predictedPlayerState.powerups[PW_NEUTRALFLAG] ) {
		flagTeam = TEAM_FREE;
	}

	if ( flagTeam < 0 ) {
		return;
	}

	CG_DrawFlagModel( rect->x + inset, rect->y + inset, rect->w - inset, rect->h - inset, flagTeam, force2D );

	if ( flagTeam == TEAM_FREE && cgs.gametype == GT_1FCTF ) {
		char	keyName[32];
		char	prompt[64];
		int		key;
		float	promptScale;
		float	promptX;
		vec4_t	promptColor = { 1.0f, 1.0f, 1.0f, 0.5f };

		key = trap_Key_GetKey( "dropflag" );
		if ( key == -1 ) {
			Q_strncpyz( keyName, "???", sizeof( keyName ) );
		} else {
			trap_Key_KeynumToStringBuf( key, keyName, sizeof( keyName ) );
			Q_strupr( keyName );
		}

		Com_sprintf( prompt, sizeof( prompt ), "Press %s to throw.", keyName );
		promptScale = 0.18f;
		promptX = rect->x + rect->w * 0.5f - ( CG_Text_Width( prompt, promptScale, 0 ) * 0.5f );
		CG_Text_Paint( promptX, rect->y + rect->h, promptScale, promptColor, prompt, 0, 0, 3 );
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

/*
=============
CG_GetKillerText

Builds the retail obituary text for the cached killer name.
=============
*/
const char *CG_GetKillerText( void ) {
	const char *s = "";
	if ( cg.killerName[0] ) {
		s = va( "Fragged by %s", cg.killerName );
	}
	return s;
}

/*
=============
CG_DrawKiller

Draws the centered retail obituary line.
=============
*/
static void CG_DrawKiller( rectDef_t *rect, float scale, vec4_t color, qhandle_t shader, int textStyle ) {
	const char	*text;
	float		x;

	(void)shader;

	if ( !rect || !cg.killerName[0] ) {
		return;
	}

	text = CG_GetKillerText();
	x = rect->x + rect->w * 0.5f - CG_Text_Width( text, scale, 0 ) * 0.5f;
	CG_Text_Paint( x, rect->y + rect->h, scale, color, text, 0, 0, textStyle );
}

/*
=============
CG_GetRaceCapFragLimitValue

Builds the Race remaining-checkpoint value used by the retail cap/frag limit ownerdraw.
=============
*/
static int CG_GetRaceCapFragLimitValue( void ) {
	cgRaceClientProgress_t	*progress;
	int						clientNum;
	int						remaining;

	if ( cgs.racePointCount <= 0 ) {
		return 0;
	}

	clientNum = CG_RaceResolveClientNum();
	progress = CG_RaceProgressForClient( clientNum );
	if ( !progress || !progress->initialized || progress->currentCheckpoint < 0 ) {
		return cgs.racePointCount;
	}

	remaining = cgs.racePointCount - ( progress->currentCheckpoint + 1 );
	if ( remaining < 0 ) {
		remaining = 0;
	}

	return remaining;
}

/*
=============
CG_DrawCapFragLimit

Renders the retail numeric limit bucket for the active gametype.
=============
*/
static void CG_DrawCapFragLimit( rectDef_t *rect, float scale, vec4_t color, int textStyle, int align ) {
	char	buffer[16];
	float	x;
	int		limit;

	switch ( cgs.gametype ) {
	case GT_RACE:
		limit = CG_GetRaceCapFragLimitValue();
		break;
	case GT_CTF:
	case GT_1FCTF:
	case GT_OBELISK:
	case GT_HARVESTER:
		limit = cgs.capturelimit;
		break;
	case GT_CLAN_ARENA:
	case GT_FREEZE:
	case GT_RED_ROVER:
		limit = cgs.roundlimit;
		break;
	case GT_DOMINATION:
	case GT_ATTACK_DEFEND:
		limit = cgs.scorelimit;
		break;
	default:
		limit = cgs.fraglimit;
		break;
	}

	Com_sprintf( buffer, sizeof( buffer ), "%2i", limit );
	x = rect->x;
	CG_AlignTextX( &x, buffer, scale, align );
	CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );
}

/*
=============
CG_GetRetailPlacementTeamName

Resolves the team label used by the retail wide first/second-place ownerdraws.
=============
*/
static const char *CG_GetRetailPlacementTeamName( team_t team ) {
	const char	*teamName;

	switch ( team ) {
	case TEAM_RED:
		teamName = cgs.redTeamName;
		if ( teamName && teamName[0] ) {
			return teamName;
		}
		return "Red Team";
	case TEAM_BLUE:
		teamName = cgs.blueTeamName;
		if ( teamName && teamName[0] ) {
			return teamName;
		}
		return "Blue Team";
	default:
		return "";
	}
}

/*
=============
CG_BuildPlacementScoreValue

Formats the live placement value for first/second-place score ownerdraws.
=============
*/
static qboolean CG_BuildPlacementScoreValue( int value, char *buffer, size_t bufferSize, qboolean leadingSpace, qboolean requirePositiveRaceTime ) {
	char		valueText[32];

	if ( !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	if ( value == SCORE_NOT_PRESENT ) {
		return qfalse;
	}

	if ( cgs.gametype == GT_RACE ) {
		if ( value == CG_SCORE_FORFEIT || value == 0x7fffffff || value < 0 || ( requirePositiveRaceTime && value == 0 ) ) {
			Q_strncpyz( buffer, leadingSpace ? " -" : "-", bufferSize );
		} else {
			CG_RaceFormatMilliseconds( value, valueText, sizeof( valueText ) );
			if ( leadingSpace ) {
				Com_sprintf( buffer, bufferSize, " %s", valueText );
			} else {
				Q_strncpyz( buffer, valueText, bufferSize );
			}
		}
		return qtrue;
	}

	Com_sprintf( buffer, bufferSize, leadingSpace ? " %d" : "%d", value );
	return qtrue;
}

/*
=============
CG_DrawPlacementScoreLine

Paints the retail split rank/name/value placement line with clipped middle text.
=============
*/
static void CG_DrawPlacementScoreLine( rectDef_t *rect, float scale, vec4_t color, int textStyle,
	const char *rankText, const char *nameText, const char *valueText ) {
	float		x;
	float		valueX;
	float		ellipsisX;
	float		ellipsisWidth;
	float		maxX;

	if ( !rect ) {
		return;
	}

	x = rect->x;
	if ( rankText && rankText[0] ) {
		CG_Text_PaintExt( x, rect->y, scale, color, rankText, 0.0f, 0, textStyle, FONT_DEFAULT );
		x += CG_Text_WidthExt( rankText, scale, 0, FONT_DEFAULT );
	}

	if ( !valueText || !valueText[0] ) {
		if ( nameText && nameText[0] ) {
			CG_Text_PaintExt( x, rect->y, scale, color, nameText, 0.0f, 0, textStyle, FONT_DEFAULT );
		}
		return;
	}

	valueX = rect->x + rect->w - CG_Text_WidthExt( valueText, scale, 0, FONT_DEFAULT );
	if ( nameText && nameText[0] && valueX > x ) {
		ellipsisWidth = CG_Text_WidthExt( "...", scale, 0, FONT_DEFAULT );
		if ( CG_Text_WidthExt( nameText, scale, 0, FONT_DEFAULT ) <= valueX - x ) {
			CG_Text_PaintExt( x, rect->y, scale, color, nameText, 0.0f, 0, textStyle, FONT_DEFAULT );
		} else if ( valueX - x > ellipsisWidth ) {
			ellipsisX = valueX - ellipsisWidth;
			maxX = ellipsisX;
			CG_Text_Paint_LimitExt( &maxX, x, rect->y, scale, color, nameText, 0.0f, 0, FONT_DEFAULT );
			CG_Text_PaintExt( ellipsisX, rect->y, scale, color, "...", 0.0f, 0, textStyle, FONT_DEFAULT );
		}
	}

	CG_Text_PaintExt( valueX, rect->y, scale, color, valueText, 0.0f, 0, textStyle, FONT_DEFAULT );
}

/*
=============
CG_Draw1stPlaceScore

Draws the wide retail first-place summary line used by spectator and HUD menus.
=============
*/
static void CG_Draw1stPlaceScore( rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
	char			nameBuffer[64];
	char			valueBuffer[32];
	team_t			leaderTeam;
	int			value;

	if ( CG_IsTeamWinnerGametype( cgs.gametype ) ) {
		if ( cgs.scores1 == SCORE_NOT_PRESENT ) {
			leaderTeam = TEAM_RED;
			valueBuffer[0] = '\0';
		} else {
			leaderTeam = ( cgs.scores1 < cgs.scores2 ) ? TEAM_BLUE : TEAM_RED;
			value = ( leaderTeam == TEAM_RED ) ? cgs.scores1 : cgs.scores2;
			if ( !CG_BuildPlacementScoreValue( value, valueBuffer, sizeof( valueBuffer ), qfalse, qfalse ) ) {
				return;
			}
		}

		Q_strncpyz( nameBuffer, CG_GetRetailPlacementTeamName( leaderTeam ), sizeof( nameBuffer ) );
		CG_DrawPlacementScoreLine( rect, scale, color, textStyle, "      ", nameBuffer, valueBuffer );
		return;
	}

	if ( cgs.scores1 == SCORE_NOT_PRESENT ) {
		if ( rect ) {
			CG_Text_Paint( rect->x, rect->y, scale, color, "1.", 0, 0, textStyle );
		}
		return;
	}

	if ( !CG_BuildPlacementScoreValue( cgs.scores1, valueBuffer, sizeof( valueBuffer ), qtrue, qfalse ) ) {
		return;
	}

	Q_strncpyz( nameBuffer, cgs.firstPlaceName, sizeof( nameBuffer ) );
	CG_DrawPlacementScoreLine( rect, scale, color, textStyle, "1. ", nameBuffer, valueBuffer );
}

/*
=============
CG_Draw2ndPlaceScore

Draws the wide retail trailing/local placement summary line used by spectator
and HUD menus.
=============
*/
static void CG_Draw2ndPlaceScore( rectDef_t *rect, float scale, vec4_t color, int textStyle ) {
	char			rankBuffer[8];
	char			nameBuffer[64];
	char			valueBuffer[32];
	const clientInfo_t	*ci;
	team_t			trailingTeam;
	int			clientNum;
	int			localRank;
	int			rank;
	int			value;

	if ( CG_IsTeamWinnerGametype( cgs.gametype ) ) {
		trailingTeam = ( cgs.scores1 < cgs.scores2 ) ? TEAM_RED : TEAM_BLUE;
		value = ( trailingTeam == TEAM_RED ) ? cgs.scores1 : cgs.scores2;
		if ( value == SCORE_NOT_PRESENT ) {
			valueBuffer[0] = '\0';
		} else if ( !CG_BuildPlacementScoreValue( value, valueBuffer, sizeof( valueBuffer ), qfalse, qfalse ) ) {
			return;
		}

		Q_strncpyz( nameBuffer, CG_GetRetailPlacementTeamName( trailingTeam ), sizeof( nameBuffer ) );
		CG_DrawPlacementScoreLine( rect, scale, color, textStyle, "      ", nameBuffer, valueBuffer );
		return;
	}

	if ( cg.snap && cg.snap->ps.pm_type != PM_SPECTATOR && !CG_ShowPlayerIsFirstPlace() ) {
		clientNum = cg.snap->ps.clientNum;
		if ( clientNum >= 0 && clientNum < cgs.maxclients && clientNum < MAX_CLIENTS ) {
			rank = cg.snap->ps.persistant[PERS_RANK];
			if ( rank & RANK_TIED_FLAG ) {
				rank &= ~RANK_TIED_FLAG;
			}

			localRank = rank + 1;
			value = ( cgs.gametype == GT_RACE ) ? cgs.clientinfo[clientNum].score : cg.snap->ps.persistant[PERS_SCORE];
			if ( !CG_BuildPlacementScoreValue( value, valueBuffer, sizeof( valueBuffer ), qtrue, qtrue ) ) {
				return;
			}

			ci = &cgs.clientinfo[clientNum];
			Q_strncpyz( nameBuffer, ( ci->name[0] ) ? ci->name : "Unknown", sizeof( nameBuffer ) );
			Com_sprintf( rankBuffer, sizeof( rankBuffer ), "%d. ", localRank );
			CG_DrawPlacementScoreLine( rect, scale, color, textStyle, rankBuffer, nameBuffer, valueBuffer );
			return;
		}
	}

	value = cgs.scores2;
	if ( !CG_BuildPlacementScoreValue( value, valueBuffer, sizeof( valueBuffer ), qtrue, qtrue ) ) {
		return;
	}

	localRank = ( cgs.scores1 != cgs.scores2 ) ? 2 : 1;
	Q_strncpyz( nameBuffer, cgs.secondPlaceName, sizeof( nameBuffer ) );

	Com_sprintf( rankBuffer, sizeof( rankBuffer ), "%d. ", localRank );
	CG_DrawPlacementScoreLine( rect, scale, color, textStyle, rankBuffer, nameBuffer, valueBuffer );
}

const char *CG_GetGameStatusText() {
	if ( !cg.snap ) {
		return "";
	}

	switch ( cgs.gametype ) {
	case GT_SINGLE_PLAYER:
		return "";

	case GT_FFA:
	case GT_TOURNAMENT:
	case GT_RED_ROVER:
		if ( cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR ) {
			return "";
		}
		return va( "%s place with %i",
			CG_PlaceString( cg.snap->ps.persistant[PERS_RANK] + 1 ),
			cg.snap->ps.persistant[PERS_SCORE] );

	default:
		if ( cg.teamScores[0] == cg.teamScores[1] ) {
			return va( "Teams are tied at %i", cg.teamScores[0] );
		}
		if ( cg.teamScores[0] > cg.teamScores[1] ) {
			return va( "^1Red^7 leads ^4Blue^7, %i to %i", cg.teamScores[0], cg.teamScores[1] );
		}
		return va( "^4Blue^7 leads ^1Red^7, %i to %i", cg.teamScores[1], cg.teamScores[0] );
	}
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
		return "Attack and Defend";
	case GT_RED_ROVER:
		return "Red Rover";
	default:
		return "Unknown Gametype";
	}
}
/*
=============
CG_DrawGameType

Draws the current gametype label through the retail center-only alignment path.
=============
*/
static void CG_DrawGameType( rectDef_t *rect, float scale, vec4_t color, int textStyle, int align ) {
	const char	*gameType;
	float		x;

	gameType = CG_GameTypeString();
	x = rect->x;
	if ( align == ITEM_ALIGN_CENTER ) {
		x -= CG_Text_Width( gameType, scale, 0 ) * 0.5f;
	}

	CG_Text_Paint( x, rect->y, scale, color, gameType, 0, 0, textStyle );
}

/*
=============
CG_Text_Paint_LimitExt

Renders text up to a character limit with an explicit host font bucket.
=============
*/
static void CG_Text_Paint_LimitExt( float *maxX, float x, float y, float scale, vec4_t color, const char* text, float adjust, int limit, int fontIndex ) {
	char limitedText[1024];
	const char *s;
	const char *limitEnd;
	const char *drawText;
	float screenX;
	float screenY;
	float screenMaxX;
	float outMaxX;
	float xScale;
	float yScale;
	float xBias;
	int fontHandle;
	int visibleCount;

	(void)adjust;

	if ( maxX == NULL ) {
		return;
	}

	if ( text == NULL || text[0] == '\0' ) {
		return;
	}

	if ( limit <= 0 ) {
		limitEnd = text + strlen( text );
	} else {
		visibleCount = 0;
		for ( s = text; *s; ) {
			if ( Q_IsColorString( s ) ) {
				s += 2;
				continue;
			}

			if ( visibleCount >= limit ) {
				break;
			}

			s++;
			visibleCount++;
		}
		limitEnd = s;
	}

	if ( *limitEnd == '\0' ) {
		drawText = text;
	} else {
		int copyLength;

		copyLength = (int)( limitEnd - text );
		if ( copyLength >= (int)sizeof( limitedText ) ) {
			copyLength = sizeof( limitedText ) - 1;
		}
		memcpy( limitedText, text, copyLength );
		limitedText[copyLength] = '\0';
		drawText = limitedText;
	}

	screenX = x;
	screenY = y;
	screenMaxX = *maxX;
	xScale = 1.0f;
	yScale = 1.0f;
	xBias = 0.0f;

	CG_AdjustFrom640( &screenX, &screenY, NULL, NULL );
	CG_AdjustFrom640( &screenMaxX, NULL, NULL, NULL );
	CG_AdjustFrom640( &xBias, NULL, &xScale, &yScale );

	fontHandle = CG_SelectTextFontHandle( scale, fontIndex );

	trap_R_SetColor( color );
	trap_QL_DrawScaledText(
		(int)screenX,
		(int)screenY,
		drawText,
		fontHandle,
		scale * QL_FONT_HOST_POINT_SIZE * yScale,
		(int)screenMaxX,
		&outMaxX,
		qfalse );
	trap_R_SetColor( NULL );

	if ( outMaxX > 0.0f && xScale > 0.0f ) {
		*maxX = ( outMaxX - xBias ) / xScale;
	} else {
		*maxX = 0.0f;
	}
}

/*
=============
CG_Text_Paint_Limit

Renders text up to a character limit while honoring inline color codes.
=============
*/
static void CG_Text_Paint_Limit(float *maxX, float x, float y, float scale, vec4_t color, const char* text, float adjust, int limit) {
	CG_Text_Paint_LimitExt( maxX, x, y, scale, color, text, adjust, limit, ITEM_FONT_INHERIT );
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

/*
=============
CG_DrawTeamSpectators

Draws the paged spectator list strip used by the retail spectator ownerdraw.
=============
*/
void CG_DrawTeamSpectators(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader) {
	int displayedCount;
	const char *entry;
	int i;
	int startIndex;
	float x;
	float y;

	(void)shader;

	if ( !rect || cg.spectatorEntryCount <= 0 ) {
		return;
	}

	if ( cg.spectatorOffset < 0 || cg.spectatorOffset >= cg.spectatorEntryCount ) {
		cg.spectatorOffset = 0;
	}

	startIndex = cg.spectatorOffset;
	displayedCount = 0;
	cg.spectatorPaintLen = 0;

	for ( i = startIndex; i < cg.spectatorEntryCount; i++ ) {
		int width;
		int pendingWidth;

		entry = cg.spectatorEntries[i];
		if ( !entry[0] ) {
			continue;
		}

		width = CG_Text_Width( entry, scale, 0 );
		pendingWidth = cg.spectatorPaintLen + width;
		if ( displayedCount > 0 ) {
			pendingWidth += 10;
		}

		if ( (float)pendingWidth > rect->w ) {
			break;
		}

		cg.spectatorPaintLen = pendingWidth;
		displayedCount++;
	}

	if ( displayedCount <= 0 ) {
		return;
	}

	x = rect->x;
	y = rect->y + rect->h - 3.0f;
	cg.spectatorPaintX = (int)x;

	for ( i = 0; i < displayedCount; i++ ) {
		int width;

		entry = cg.spectatorEntries[startIndex + i];
		if ( !entry[0] ) {
			continue;
		}

		CG_Text_Paint( x, y, scale, color, entry, 0, 0, 0 );
		width = CG_Text_Width( entry, scale, 0 );
		x += width + 10.0f;
	}

	cg.spectatorPaintX2 = (int)x;

	if ( cg.spectatorTime <= 0 ) {
		cg.spectatorTime = cg.time + 4000;
	} else if ( cg.time > cg.spectatorTime && cg.spectatorEntryCount > displayedCount ) {
		cg.spectatorTime = cg.time + 4000;
		cg.spectatorOffset = startIndex + displayedCount;
		if ( cg.spectatorOffset >= cg.spectatorEntryCount ) {
			cg.spectatorOffset = 0;
		}
	}
}

/*
=============
CG_DrawAdvert

Draws the retail advert slot and fires the inert native callback seam.
=============
*/
static void CG_DrawAdvert( rectDef_t *rect, vec4_t color, qhandle_t shader ) {
	if ( !rect || !shader ) {
		return;
	}

	trap_R_SetColor( color );
	CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );

#ifndef Q3_VM
	{
		int pixelArea;

		pixelArea = (int)( rect->w * rect->h );
		trap_QL_UpdateAdvert( shader, pixelArea );
	}
#endif

	trap_R_SetColor( NULL );
}

/*
=============
CG_DrawMedal

Draws the retail scoreboard medal ownerdraw leaf.
=============
*/
void CG_DrawMedal( int ownerDraw, rectDef_t *rect, float scale, vec4_t color, qhandle_t shader ) {
	score_t		*score;
	float		value;
	const char	*text;

	if ( !rect || cg.selectedScore < 0 || cg.selectedScore >= cg.numScores || cg.selectedScore >= MAX_CLIENTS ) {
		return;
	}

	score = &cg.scores[cg.selectedScore];
	value = 0;
	text = NULL;
	color[3] = 0.25;

	switch ( ownerDraw ) {
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

	if ( value > 0 ) {
		if ( ownerDraw != CG_PERFECT ) {
			if ( ownerDraw == CG_ACCURACY ) {
				text = va( "%i%%", (int)value );
				color[3] = 1.0;
			} else {
				text = va( "%i", (int)value );
				color[3] = 1.0;
			}
		} else {
			if ( value ) {
				color[3] = 1.0;
			}
			text = "Wow";
		}
	}

	trap_R_SetColor(color);
	CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );

	if ( text ) {
		color[3] = 1.0;
		value = CG_Text_Width( text, scale, 0 );
		CG_Text_Paint( rect->x + ( rect->w - value ) / 2, rect->y + rect->h + 10, scale, color, text, 0, 0, 0 );
	}
	trap_R_SetColor( NULL );

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
CG_OwnerDraw

Routes owner-draw IDs to their rendering helpers.
=============
*/
void CG_OwnerDraw(float x, float y, float w, float h, float text_x, float text_y, int ownerDraw, int ownerDrawFlags, int align, float special, float scale, vec4_t color, qhandle_t shader, int textStyle) {
	rectDef_t rect;

  if ( cg_drawStatus.integer == 0 ) {
		return;
	}

	//if (ownerDrawFlags != 0 && !CG_OwnerDrawVisible(ownerDrawFlags, 0)) {
	//	return;
	//}

rect.x = x;
rect.y = y;
	rect.w = w;
	rect.h = h;

	if ( CG_IsCompetitiveScoreOwnerDraw( ownerDraw ) ) {
		CG_TouchCompetitiveScores();
	}

	if ( CG_DrawPlacementMetricOwnerDraw( &rect, scale, color, textStyle, ownerDraw ) ) {
		return;
	}

	if ( CG_DrawAwardPlayer( &rect, ownerDraw ) ) {
		return;
	}

	switch (ownerDraw) {
	case CG_SERVER_SETTINGS:
		CG_DrawServerSettings(&rect, text_x, text_y, scale, color, textStyle);
		break;
	case CG_STARTING_WEAPONS:
		CG_DrawStartingWeapons(&rect, text_x, text_y, scale, color, textStyle);
		break;
	case CG_GAME_LIMIT:
		CG_DrawGameLimit( &rect, scale, color, textStyle, align );
		break;
	case CG_GAME_TYPE_ICON:
		CG_DrawGameTypeIcon(&rect);
		break;
	case CG_GAME_TYPE_MAP:
		CG_DrawGameTypeMap( &rect, scale, color, textStyle, align );
		break;
	case CG_GAME_TYPE:
		CG_DrawGameType( &rect, scale, color, textStyle, align );
		break;
	case CG_GAME_STATUS:
		CG_DrawGameStatus(&rect, scale, color, shader, textStyle);
		break;
	case CG_MATCH_DETAILS:
		CG_DrawMatchDetails( &rect, scale, color, textStyle );
		break;
	case CG_MATCH_END_CONDITION:
		CG_DrawMatchEndCondition( &rect, scale, color, textStyle );
		break;
	case CG_MATCH_STATUS:
		CG_DrawMatchStatus( &rect, scale, color, textStyle, align );
		break;
	case CG_CAPFRAGLIMIT:
		CG_DrawCapFragLimit( &rect, scale, color, textStyle, align );
		break;
	case CG_LEVELTIMER:
		CG_DrawLevelTimer(&rect, scale, color, textStyle, align);
		break;
	case CG_ROUND:
		if ( CG_ShowPlayersRemaining() ) {
			CG_DrawRoundLabel( &rect, scale, color, textStyle, align );
		}
			break;
	case CG_ROUND_BACKGROUND:
			/* Retail maps raw ownerdraw 0x162 to the common no-op return target. */
			return;
	case CG_ROUNDTIMER:
			CG_DrawRoundTimer(&rect, scale, color, textStyle);
			break;
	case CG_OVERTIME:
		if ( cg.warmup == 0 ) {
			CG_DrawOvertime(&rect, scale, color, textStyle);
		}
		break;
	case CG_OVERTIME_BACKGROUND:
			/* Retail maps raw ownerdraw 0x163 to the common no-op return target. */
			return;
	case CG_LOCALTIME:
		CG_DrawLocalTime(&rect, scale, color, textStyle, align);
		break;
	case CG_PLAYER_COUNTS:
		CG_DrawPlayerCounts(&rect, scale, color, textStyle, align);
		break;
	case CG_MAP_NAME:
		CG_DrawMapName(&rect, scale, color, textStyle);
		break;
	case CG_VOTEGAMETYPE1:
		CG_DrawVoteGametype(&rect, scale, color, textStyle, 1);
		break;
	case CG_VOTEGAMETYPE2:
		CG_DrawVoteGametype(&rect, scale, color, textStyle, 2);
		break;
	case CG_VOTEGAMETYPE3:
		CG_DrawVoteGametype(&rect, scale, color, textStyle, 3);
		break;
	case CG_VOTEMAP1:
		CG_DrawVoteMapSlot(&rect, scale, color, textStyle, 1);
		break;
	case CG_VOTEMAP2:
		CG_DrawVoteMapSlot(&rect, scale, color, textStyle, 2);
		break;
	case CG_VOTEMAP3:
		CG_DrawVoteMapSlot(&rect, scale, color, textStyle, 3);
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
		CG_DrawVoteName(&rect, scale, color, textStyle, 1);
		break;
	case CG_VOTENAME2:
		CG_DrawVoteName(&rect, scale, color, textStyle, 2);
		break;
	case CG_VOTENAME3:
		CG_DrawVoteName(&rect, scale, color, textStyle, 3);
		break;
	case CG_VOTECOUNT1:
		CG_DrawVoteCount(&rect, scale, color, textStyle, 1, align);
		break;
	case CG_VOTECOUNT2:
		CG_DrawVoteCount(&rect, scale, color, textStyle, 2, align);
		break;
	case CG_VOTECOUNT3:
		CG_DrawVoteCount(&rect, scale, color, textStyle, 3, align);
		break;
	case CG_VOTETIMER:
		CG_DrawVoteTimer(&rect, scale, color, textStyle, align);
		break;

	case CG_PLAYER_ARMOR_ICON:
		CG_DrawPlayerArmorIcon( &rect, ownerDrawFlags & CG_SHOW_2DONLY );
		break;
	case CG_PLAYER_ARMOR_ICON2D:
		CG_DrawPlayerArmorIcon( &rect, qtrue );
		break;
	case CG_PLAYER_ARMOR_VALUE:
		CG_DrawPlayerArmorValue( &rect, scale, color, shader, textStyle, align );
		break;
	case CG_PLAYER_ARMOR_BAR_100:
		CG_DrawPlayerArmorBar100( &rect, shader );
		break;
	case CG_PLAYER_ARMOR_BAR_200:
		CG_DrawPlayerArmorBar200( &rect, shader );
		break;
	case CG_PLAYER_AMMO_ICON:
		CG_DrawPlayerAmmoIcon( &rect, ownerDrawFlags & CG_SHOW_2DONLY );
		break;
	case CG_PLAYER_AMMO_ICON2D:
		CG_DrawPlayerAmmoIcon( &rect, qtrue );
		break;
	case CG_PLAYER_AMMO_VALUE:
		CG_DrawPlayerAmmoValue( &rect, scale, color, shader, textStyle, align );
		break;
	case CG_SELECTEDPLAYER_HEAD:
	case CG_SELECTEDPLAYER_NAME:
	case CG_SELECTEDPLAYER_LOCATION:
	case CG_SELECTEDPLAYER_STATUS:
	case CG_SELECTEDPLAYER_WEAPON:
	case CG_SELECTEDPLAYER_POWERUP:
	case CG_SELECTEDPLAYER_ARMOR:
	case CG_SELECTEDPLAYER_HEALTH:
	case CG_VOICE_HEAD:
	case CG_VOICE_NAME:
		/* Retail maps raw ownerdraws 0x158-0x161 to the common no-op return target. */
		return;
	case CG_PLAYER_HEAD:
		CG_DrawPlayerHead( &rect, ownerDrawFlags & CG_SHOW_2DONLY );
		break;
	case CG_PLAYERMODEL:
		CG_DrawPlayerModel( &rect );
		break;
	case CG_PLAYER_ITEM:
		CG_DrawPlayerItem( &rect, scale, ownerDrawFlags & CG_SHOW_2DONLY );
		break;
	case CG_PLAYER_SCORE:
		CG_DrawScoreValue( &rect, scale, color, shader, textStyle, ownerDraw );
		break;
	case CG_PLAYER_HEALTH:
		CG_DrawPlayerHealth( &rect, scale, color, shader, textStyle, align );
		break;
	case CG_PLAYER_HEALTH_BAR_100:
		CG_DrawPlayerHealthBar100( &rect, shader );
		break;
  case CG_PLAYER_HEALTH_BAR_200:
		CG_DrawPlayerHealthBar200( &rect, shader );
		break;
  case CG_RED_SCORE:
		CG_DrawTeamScore( &rect, scale, color, textStyle, TEAM_RED, align );
		break;
  case CG_BLUE_SCORE:
		CG_DrawTeamScore( &rect, scale, color, textStyle, TEAM_BLUE, align );
		break;
  case CG_RED_PLAYER_COUNT:
		CG_DrawTeamPlayerCount(&rect, scale, color, textStyle, TEAM_RED, align);
		break;
  case CG_BLUE_PLAYER_COUNT:
		CG_DrawTeamPlayerCount(&rect, scale, color, textStyle, TEAM_BLUE, align);
		break;
	case CG_RED_CLAN_PLYRS:
		if ( CG_ShowPlayersRemaining() ) {
			CG_DrawClanArenaPlayers(&rect, scale, color, textStyle, TEAM_RED);
		}
		break;
	case CG_BLUE_CLAN_PLYRS:
		if ( CG_ShowPlayersRemaining() ) {
			CG_DrawClanArenaPlayers(&rect, scale, color, textStyle, TEAM_BLUE);
		}
		break;
	case CG_RED_OWNED_FLAGS:
		if ( cgs.gametype == GT_DOMINATION || cgs.gametype == GT_ATTACK_DEFEND ) {
			CG_DrawDominationOwnedFlags(&rect, scale, color, textStyle, TEAM_RED);
		}
		break;
	case CG_BLUE_OWNED_FLAGS:
		if ( cgs.gametype == GT_DOMINATION || cgs.gametype == GT_ATTACK_DEFEND ) {
			CG_DrawDominationOwnedFlags(&rect, scale, color, textStyle, TEAM_BLUE);
		}
		break;
  case CG_RED_TIMEOUT_COUNT:
		if ( cgs.playerCountTeamSize > 0 ) {
			CG_DrawTeamTimeoutCount( &rect, scale, color, textStyle, TEAM_RED, align );
		}
		break;
  case CG_BLUE_TIMEOUT_COUNT:
		if ( cgs.playerCountTeamSize > 0 ) {
			CG_DrawTeamTimeoutCount( &rect, scale, color, textStyle, TEAM_BLUE, align );
		}
		break;
  case CG_RED_AVG_PING:
		CG_DrawTeamAveragePing(&rect, scale, color, textStyle, TEAM_RED);
		break;
  case CG_BLUE_AVG_PING:
		CG_DrawTeamAveragePing(&rect, scale, color, textStyle, TEAM_BLUE);
		break;
  case CG_RED_NAME:
		CG_DrawTeamName( &rect, scale, color, textStyle, TEAM_RED, align );
		break;
  case CG_BLUE_NAME:
		CG_DrawTeamName( &rect, scale, color, textStyle, TEAM_BLUE, align );
		break;
	case CG_BLUE_FLAGHEAD:
		/* Retail maps raw ownerdraw 0x167 to the common no-op return target. */
		return;
  case CG_BLUE_FLAGSTATUS:
    CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_BLUE, qfalse, shader );
    break;
	case CG_BLUE_FLAGNAME:
		/* Retail maps raw ownerdraw 0x168 to the common no-op return target. */
		return;
	case CG_RED_FLAGHEAD:
		/* Retail maps raw ownerdraw 0x169 to the common no-op return target. */
		return;
  case CG_RED_FLAGSTATUS:
    CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_RED, qfalse, shader );
    break;
	case CG_RED_FLAGNAME:
		/* Retail maps raw ownerdraw 0x16a to the common no-op return target. */
		return;
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
		/* Retail maps raw ownerdraw 0x16b to the common no-op return target. */
		return;
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
		/* Retail maps raw ownerdraw 0x16c to the common no-op return target. */
		return;
  case CG_PLAYER_HASFLAG:
    CG_DrawPlayerHasFlag(&rect, qfalse);
    break;
  case CG_PLAYER_HASFLAG2D:
    CG_DrawPlayerHasFlag(&rect, qtrue);
    break;
	case CG_AREA_SYSTEMCHAT:
	case CG_AREA_TEAMCHAT:
	case CG_AREA_CHAT:
		/* Retail maps raw ownerdraws 0x16d-0x16f to the common no-op return target. */
		return;
  case CG_AREA_NEW_CHAT:
                CG_DrawNewChatArea(&rect, scale, color, textStyle);
                break;
  case CG_KILLER:
		if ( cg.killerName[0] ) {
			CG_DrawKiller(&rect, scale, color, shader, textStyle);
		}
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
		if ( cg.spectatorEntryCount > 0 ) {
			CG_DrawTeamSpectators(&rect, scale, color, shader);
		}
		break;
	case UI_ADVERT:
		CG_DrawAdvert( &rect, color, shader );
		break;
  case CG_SELECTED_PLYR_TEAM_COLOR:
		CG_DrawSelectedPlayerTeamColor(&rect, color);
		break;
  case CG_SELECTED_PLYR_ACCURACY:
		CG_DrawSelectedPlayerAccuracy(&rect, scale, color, textStyle);
		break;
  case CG_WP_VERTICAL:
		CG_DrawWeaponVertical( &rect, color );
		break;
  case CG_ACC_VERTICAL:
		CG_DrawAccVertical( &rect, scale, color, textStyle );
		break;
  case CG_PLYR_BEST_WEAPON_NAME:
		CG_DrawSelectedPlayerBestWeapon(&rect, scale, color, textStyle);
		break;
  case CG_SPEC_MESSAGES:
		CG_DrawSpectatorMessages(&rect, scale, color, textStyle);
		break;
	case CG_TEAMINFO:
		/* Retail maps raw ownerdraw 0x166 to the common no-op return target. */
		return;
	case CG_1STPLACE:
		CG_DrawScoreValue( &rect, scale, color, shader, textStyle, ownerDraw );
		break;
  case CG_1STPLACE_PLYR_MODEL:
		CG_DrawFirstPlaceModel( &rect, qfalse );
		break;
	case CG_1STPLACE_PLYR_MODEL_ACTIVE:
		/* Retail maps raw ownerdraw 0x66 to the common no-op return target. */
		return;
	case CG_2NDPLACE:
		CG_DrawScoreValue( &rect, scale, color, shader, textStyle, ownerDraw );
		break;
  case CG_1ST_PLACE_SCORE:
    CG_Draw1stPlaceScore(&rect, scale, color, textStyle);
                break;
  case CG_2ND_PLACE_SCORE:
    CG_Draw2ndPlaceScore(&rect, scale, color, textStyle);
                break;
	case CG_PLAYER_OBIT:
		CG_DrawPlayerObituary(&rect, scale, color, textStyle);
		break;
	case CG_MATCH_STATE:
		CG_DrawMatchState(&rect, scale, color, textStyle);
		break;
	case CG_1ST_PLYR: {
		CG_DrawSpectatorPlayerName(&rect, scale, color, textStyle, 0, align);
		break;
	}
	case CG_1ST_PLYR_SCORE:
		CG_DrawSpectatorPlayerScore(&rect, scale, color, textStyle, 0, align);
		break;
	case CG_1ST_PLYR_TIME:
	case CG_1ST_PLYR_TIMEOUT_COUNT:
		/* Retail maps raw ownerdraws 0x6d and 0x73 to the common no-op return target. */
		return;
	case CG_1ST_PLYR_HEALTH_ARMOR:
		CG_DrawSpectatorComparison( &rect, scale, color, textStyle, ownerDraw );
		break;
	case CG_1ST_PLYR_AVATAR:
		CG_DrawPlacementAvatarOwnerDraw( &rect, 0 );
		break;
	case CG_2ND_PLYR: {
		CG_DrawSpectatorPlayerName(&rect, scale, color, textStyle, 1, align);
		break;
	}
	case CG_2ND_PLYR_SCORE:
		CG_DrawSpectatorPlayerScore(&rect, scale, color, textStyle, 1, align);
		break;
	case CG_2ND_PLYR_TIMEOUT_COUNT:
		/* Retail has no raw ownerdraw 0xcd helper route. */
		return;
	case CG_2ND_PLYR_PR:
	case CG_2ND_PLYR_TIER:
		/* Retail has no raw ownerdraw 0x119-0x11a helper route. */
		return;
	case CG_2ND_PLYR_HEALTH_ARMOR:
		CG_DrawSpectatorComparison( &rect, scale, color, textStyle, ownerDraw );
		break;
	case CG_2ND_PLYR_AVATAR:
		CG_DrawPlacementAvatarOwnerDraw( &rect, 1 );
		break;
		case CG_SCOREBOX_FOLLOW_BACKGROUND:
		case CG_SCOREBOX_SPEC_BACKGROUND:
				/* Retail maps raw ownerdraws 0x164-0x165 to the common no-op return target. */
				return;
		case CG_SPEC_FOLLOW_PRIMARY:
		case CG_SPEC_FOLLOW_SECONDARY:
		case CG_SPEC_COMPARE_PRIMARY:
		case CG_SPEC_COMPARE_SECONDARY:
				/* Retail maps raw ownerdraws 0x154-0x157 to the common no-op return target. */
				return;
	case CG_HEALTH_COLORIZED: {
		qhandle_t followShader = shader;

		if ( !followShader && cg.competitiveHudLoaded ) {
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

		if ( !teamShader && cg.competitiveHudLoaded ) {
			teamShader = cgs.media.scoreboxSpecShader;
		}
		CG_DrawTeamColorized( &rect, color, teamShader );
		break;
	}
	case CG_FOLLOW_PLAYER_NAME:
		CG_DrawFollowPlayerNameEx(&rect, scale, color, textStyle, ownerDraw, align);
		break;
	case CG_FOLLOW_PLAYER_NAME_EX:
		CG_DrawFollowPlayerNameEx(&rect, scale, color, textStyle, ownerDraw, align);
		break;
	case CG_RED_TEAM_MAP_PICKUPS:
	case CG_RED_TEAM_PICKUPS_RA:
	case CG_RED_TEAM_PICKUPS_YA:
	case CG_RED_TEAM_PICKUPS_GA:
	case CG_RED_TEAM_PICKUPS_MH:
	case CG_RED_TEAM_PICKUPS_QUAD:
	case CG_RED_TEAM_PICKUPS_BS:
	case CG_RED_TEAM_PICKUPS_FLAG:
	case CG_RED_TEAM_PICKUPS_MEDKIT:
	case CG_RED_TEAM_PICKUPS_REGEN:
	case CG_RED_TEAM_PICKUPS_HASTE:
	case CG_RED_TEAM_PICKUPS_INVIS:
	case CG_BLUE_TEAM_MAP_PICKUPS:
	case CG_BLUE_TEAM_PICKUPS_RA:
	case CG_BLUE_TEAM_PICKUPS_YA:
	case CG_BLUE_TEAM_PICKUPS_GA:
	case CG_BLUE_TEAM_PICKUPS_MH:
	case CG_BLUE_TEAM_PICKUPS_QUAD:
	case CG_BLUE_TEAM_PICKUPS_BS:
	case CG_BLUE_TEAM_PICKUPS_FLAG:
	case CG_BLUE_TEAM_PICKUPS_MEDKIT:
	case CG_BLUE_TEAM_PICKUPS_REGEN:
	case CG_BLUE_TEAM_PICKUPS_HASTE:
	case CG_BLUE_TEAM_PICKUPS_INVIS:
		CG_DrawTeamPickupOwnerDraw( &rect, scale, color, textStyle, ownerDraw );
		break;
	case CG_RED_TEAM_TIMEHELD_QUAD:
	case CG_RED_TEAM_TIMEHELD_BS:
	case CG_RED_TEAM_TIMEHELD_FLAG:
	case CG_RED_TEAM_TIMEHELD_REGEN:
	case CG_RED_TEAM_TIMEHELD_HASTE:
	case CG_RED_TEAM_TIMEHELD_INVIS:
	case CG_BLUE_TEAM_TIMEHELD_QUAD:
	case CG_BLUE_TEAM_TIMEHELD_BS:
	case CG_BLUE_TEAM_TIMEHELD_FLAG:
	case CG_BLUE_TEAM_TIMEHELD_REGEN:
	case CG_BLUE_TEAM_TIMEHELD_HASTE:
	case CG_BLUE_TEAM_TIMEHELD_INVIS:
		CG_DrawTeamTimeHeldOwnerDraw( &rect, scale, color, textStyle, ownerDraw );
		break;
	case CG_MATCH_WINNER:
		CG_DrawMatchWinner( &rect, text_x, text_y, scale, color, textStyle );
		break;
	case CG_PLYR_END_GAME_SCORE:
		CG_DrawEndGameScore( &rect, text_x, text_y, scale, color, textStyle );
		break;
	case CG_RACE_STATUS:
	case CG_RACE_TIMES:
		CG_DrawRaceStatusAndTimes( &rect, scale, color, textStyle, ownerDraw );
		break;
	case CG_FLAG_STATUS:
		CG_DrawObjectiveStatus( &rect, scale, color, textStyle );
		break;
	case CG_RED_BASESTATUS:
		CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_RED, qtrue, shader );
		break;
	case CG_BLUE_BASESTATUS:
		CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_BLUE, qtrue, shader );
		break;
	case CG_PLAYER_HASKEY:
		CG_DrawPlayerHasKey( &rect );
		break;
  case CG_SPEEDOMETER:
		CG_DrawSpeedometerOwnerDraw( &rect, scale, color, textStyle );
		break;
  case CG_TEAM_PLYR_COUNT:
		if ( CG_ShowPlayersRemaining() ) {
			CG_DrawPlayerCount(&rect, scale, color, textStyle, qtrue);
		}
		break;
	case CG_ENEMY_PLYR_COUNT:
		if ( CG_ShowPlayersRemaining() ) {
			CG_DrawPlayerCount(&rect, scale, color, textStyle, qfalse);
		}
		break;
  default:
    break;
  }
}


/*
=============
CG_ShouldCaptureSpectatorUi

Returns qtrue when spectator HUD input should be processed.
=============
*/
static qboolean CG_ShouldCaptureSpectatorUi( void ) {
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
CG_BrowserDisplayCursorType

Routes browser cursor-shape queries through the shared display runtime.
=============
*/
static int CG_BrowserDisplayCursorType( int x, int y ) {
	return Display_CursorType( x, y );
}

/*
=============
CG_BrowserHandleMouseMove

Routes retail browser mouse motion through one focused overlay root.
=============
*/
static void CG_BrowserHandleMouseMove( void *overlay, float x, float y ) {
	Menu_HandleMouseMove( (menuDef_t *)overlay, x, y );
}

/*
=============
CG_BrowserDisplayMouseMove

Routes browser mouse motion through the shared display runtime.
=============
*/
static qboolean CG_BrowserDisplayMouseMove( void *overlay, int x, int y ) {
	if ( overlay != NULL ) {
		CG_BrowserHandleMouseMove( overlay, (float)x, (float)y );
		return qtrue;
	}

	return Display_MouseMove( overlay, x, y );
}

/*
=============
CG_BrowserDisplayCaptureItem

Routes browser key dispatch through the retail display capture hit test before
falling back to the focused overlay root.
=============
*/
static void *CG_BrowserDisplayCaptureItem( int x, int y ) {
	return Display_CaptureItem( x, y );
}

/*
=============
CG_AllocBrowserWidgetState

Ensures the retail browser widget owns the shared type-data slab needed by the
draw and input helpers.
=============
*/
static void CG_AllocBrowserWidgetState( void *widget ) {
	if ( widget == NULL ) {
		return;
	}

	Item_ValidateTypeData( (itemDef_t *)widget );
}

/*
=============
CG_BrowserListMaxScroll

Routes retail browser list max-scroll queries through the shared list-box helper.
=============
*/
static int CG_BrowserListMaxScroll( void *widget ) {
	return Item_ListBox_MaxScroll( (itemDef_t *)widget );
}

/*
=============
CG_BrowserListThumbPosition

Routes retail browser list thumb-position queries through the shared list-box helper.
=============
*/
static int CG_BrowserListThumbPosition( void *widget ) {
	return Item_ListBox_ThumbPosition( (itemDef_t *)widget );
}

/*
=============
CG_BrowserListThumbDrawPosition

Routes retail browser list drag-position queries through the shared list-box helper.
=============
*/
static int CG_BrowserListThumbDrawPosition( void *widget ) {
	return Item_ListBox_ThumbDrawPosition( (itemDef_t *)widget );
}

/*
=============
CG_BrowserListOverLB

Routes retail browser list hit tests through the shared list-box helper.
=============
*/
static int CG_BrowserListOverLB( void *widget, float x, float y ) {
	return Item_ListBox_OverLB( (itemDef_t *)widget, x, y );
}

/*
=============
CG_BrowserTextFieldHandleKey

Routes retail browser edit-field key handling through the shared text-field helper.
=============
*/
static qboolean CG_BrowserTextFieldHandleKey( void *widget, int key ) {
	return Item_TextField_HandleKey( (itemDef_t *)widget, key );
}

/*
=============
CG_BrowserScriptFadeIn

Runs the retail browser `fadein` verb through the shared fade helper.
=============
*/
static void CG_BrowserScriptFadeIn( void *widget, char **args ) {
	const char	*name;
	itemDef_t	*item;

	item = (itemDef_t *)widget;
	if ( item == NULL ) {
		return;
	}

	if ( String_Parse( args, &name ) ) {
		Menu_FadeItemByName( (menuDef_t *)item->parent, name, qfalse );
	}
}

/*
=============
CG_BrowserScriptFadeOut

Runs the retail browser `fadeout` verb through the shared fade helper.
=============
*/
static void CG_BrowserScriptFadeOut( void *widget, char **args ) {
	const char	*name;
	itemDef_t	*item;

	item = (itemDef_t *)widget;
	if ( item == NULL ) {
		return;
	}

	if ( String_Parse( args, &name ) ) {
		Menu_FadeItemByName( (menuDef_t *)item->parent, name, qtrue );
	}
}

/*
=============
CG_BrowserScriptSetBackground

Runs the retail browser `setbackground` verb through the shared script helper.
=============
*/
static void CG_BrowserScriptSetBackground( void *widget, char **args ) {
	Script_SetBackground( (itemDef_t *)widget, args );
}

/*
=============
CG_BrowserScriptSetColor

Runs the retail browser `setcolor` verb through the shared script helper.
=============
*/
static void CG_BrowserScriptSetColor( void *widget, char **args ) {
	Script_SetColor( (itemDef_t *)widget, args );
}

/*
=============
CG_BrowserScriptSetTeamColor

Runs the retail browser `setteamcolor` verb through the shared script helper.
=============
*/
static void CG_BrowserScriptSetTeamColor( void *widget, char **args ) {
	Script_SetTeamColor( (itemDef_t *)widget, args );
}

/*
=============
CG_BrowserScriptSetItemColor

Runs the retail browser `setitemcolor` verb through the shared script helper.
=============
*/
static void CG_BrowserScriptSetItemColor( void *widget, char **args ) {
	Script_SetItemColor( (itemDef_t *)widget, args );
}

/*
=============
CG_TransitionBrowserItemsByName

Routes retail browser transition requests through the shared grouped-item helper.
=============
*/
static void CG_TransitionBrowserItemsByName( void *overlay, const char *name, rectDef_t rectFrom, rectDef_t rectTo, int time, float amount ) {
	Menu_TransitionItemByName( (menuDef_t *)overlay, name, rectFrom, rectTo, time, amount );
}

/*
=============
CG_BrowserScriptTransition

Runs the retail browser `transition` verb through the cgame-owned grouped-item wrapper.
=============
*/
static void CG_BrowserScriptTransition( void *widget, char **args ) {
	const char	*name;
	rectDef_t	rectFrom;
	rectDef_t	rectTo;
	int		time;
	float		amount;
	itemDef_t	*item;

	item = (itemDef_t *)widget;
	if ( item == NULL ) {
		return;
	}

	if ( String_Parse( args, &name ) &&
		Rect_Parse( args, &rectFrom ) &&
		Rect_Parse( args, &rectTo ) &&
		Int_Parse( args, &time ) &&
		Float_Parse( args, &amount ) ) {
		CG_TransitionBrowserItemsByName( item->parent, name, rectFrom, rectTo, time, amount );
	}
}

/*
=============
CG_OrbitBrowserItemsByName

Routes retail browser orbit requests through the shared grouped-item helper.
=============
*/
static void CG_OrbitBrowserItemsByName( void *overlay, const char *name, float x, float y, float cx, float cy, int time ) {
	Menu_OrbitItemByName( (menuDef_t *)overlay, name, x, y, cx, cy, time );
}

/*
=============
CG_BrowserScriptOrbit

Runs the retail browser `orbit` verb through the cgame-owned grouped-item wrapper.
=============
*/
static void CG_BrowserScriptOrbit( void *widget, char **args ) {
	const char	*name;
	float		x;
	float		y;
	float		cx;
	float		cy;
	int		time;
	itemDef_t	*item;

	item = (itemDef_t *)widget;
	if ( item == NULL ) {
		return;
	}

	if ( String_Parse( args, &name ) &&
		Float_Parse( args, &x ) &&
		Float_Parse( args, &y ) &&
		Float_Parse( args, &cx ) &&
		Float_Parse( args, &cy ) &&
		Int_Parse( args, &time ) ) {
		CG_OrbitBrowserItemsByName( item->parent, name, x, y, cx, cy, time );
	}
}

/*
=============
CG_BrowserScriptActivateAdvert

Runs the retail browser advert-activation verb through the cgame display context.
=============
*/
static void CG_BrowserScriptActivateAdvert( void *widget, char **args ) {
	const char	*cellIdToken;
	itemDef_t	*item;

	item = (itemDef_t *)widget;
	if ( !String_Parse( args, &cellIdToken ) ) {
		return;
	}

	if ( cgDC.activateAdvert ) {
		cgDC.activateAdvert( atoi( cellIdToken ) );
	}

	if ( item ) {
		item->window.flags &= ~WINDOW_HASFOCUS;
	}
}

/*
=============
CG_BrowserScriptSetPlayerModel

Runs the retail browser `setplayermodel` verb through the shared script helper.
=============
*/
static void CG_BrowserScriptSetPlayerModel( void *widget, char **args ) {
	Script_SetPlayerModel( (itemDef_t *)widget, args );
}

/*
=============
CG_BrowserScriptSetPlayerHead

Runs the retail browser `setplayerhead` verb through the shared script helper.
=============
*/
static void CG_BrowserScriptSetPlayerHead( void *widget, char **args ) {
	Script_SetPlayerHead( (itemDef_t *)widget, args );
}

/*
=============
CG_BrowserScriptSetCvar

Runs the retail browser `setcvar` verb through the shared script helper.
=============
*/
static void CG_BrowserScriptSetCvar( void *widget, char **args ) {
	Script_SetCvar( (itemDef_t *)widget, args );
}

/*
=============
CG_BrowserScriptExec

Runs the retail browser `exec` verb through the shared script helper.
=============
*/
static void CG_BrowserScriptExec( void *widget, char **args ) {
	Script_Exec( (itemDef_t *)widget, args );
}

/*
=============
CG_BrowserScriptPlay

Runs the retail browser `play` verb through the shared script helper.
=============
*/
static void CG_BrowserScriptPlay( void *widget, char **args ) {
	Script_Play( (itemDef_t *)widget, args );
}

/*
=============
CG_BrowserScriptPlayLooped

Runs the retail browser `playlooped` verb through the shared script helper.
=============
*/
static void CG_BrowserScriptPlayLooped( void *widget, char **args ) {
	Script_playLooped( (itemDef_t *)widget, args );
}

/*
=============
CG_BrowserMultiFindCvarByValue

Routes retail browser multi-choice cvar resolution through the shared helper.
=============
*/
static int CG_BrowserMultiFindCvarByValue( void *widget ) {
	return Item_Multi_FindCvarByValue( (itemDef_t *)widget );
}

/*
=============
CG_BrowserMultiSetting

Routes retail browser multi-choice label resolution through the shared helper.
=============
*/
static const char *CG_BrowserMultiSetting( void *widget ) {
	return Item_Multi_Setting( (itemDef_t *)widget );
}

/*
=============
CG_BrowserPresetListSetting

Routes retail browser preset-list label resolution through the shared helper.
=============
*/
static const char *CG_BrowserPresetListSetting( void *widget ) {
	return Item_PresetList_Setting( (itemDef_t *)widget );
}

/*
=============
CG_BrowserPresetListFindCvarByValue

Routes retail browser preset-list cvar resolution through the shared helper.
=============
*/
static int CG_BrowserPresetListFindCvarByValue( void *widget ) {
	return Item_PresetList_FindCvarByValue( (itemDef_t *)widget );
}

/*
=============
CG_DrawBrowserYesNoControl

Paints one retail browser yes-no control through the shared painter.
=============
*/
static void CG_DrawBrowserYesNoControl( void *widget ) {
	Item_YesNo_Paint( (itemDef_t *)widget );
}

/*
=============
CG_DrawBrowserMultiControl

Paints one retail browser multi-choice control through the shared painter.
=============
*/
static void CG_DrawBrowserMultiControl( void *widget ) {
	Item_Multi_Paint( (itemDef_t *)widget );
}

/*
=============
CG_DrawBrowserPresetList

Paints one retail browser preset-list control through the shared painter.
=============
*/
static void CG_DrawBrowserPresetList( void *widget ) {
	Item_PresetList_Paint( (itemDef_t *)widget );
}

/*
=============
CG_BrowserControlsGetConfig

Routes retail browser binding-cache refreshes through the shared controls helper.
=============
*/
static void CG_BrowserControlsGetConfig( void ) {
	Controls_GetConfig();
}

/*
=============
CG_BrowserControlsSetConfig

Routes retail browser binding writes through the shared controls helper.
=============
*/
static void CG_BrowserControlsSetConfig( qboolean restart ) {
	Controls_SetConfig( restart );
}

/*
=============
CG_BrowserBindingIDFromName

Routes retail browser command-binding lookup through the shared controls helper.
=============
*/
static int CG_BrowserBindingIDFromName( const char *name ) {
	return BindingIDFromName( name );
}

/*
=============
CG_BrowserBindingFromName

Routes retail browser binding-label resolution through the shared controls helper.
=============
*/
static void CG_BrowserBindingFromName( const char *name ) {
	BindingFromName( name );
}

/*
=============
CG_DrawBrowserBindControl

Paints one retail browser bind control through the shared painter.
=============
*/
static void CG_DrawBrowserBindControl( void *widget ) {
	Item_Bind_Paint( (itemDef_t *)widget );
}

/*
=============
CG_BrowserBindHandleKey

Routes retail browser bind-control key handling through the shared helper.
=============
*/
static qboolean CG_BrowserBindHandleKey( void *widget, int key, qboolean down ) {
	return Item_Bind_HandleKey( (itemDef_t *)widget, key, down );
}

/*
=============
CG_BrowserSliderThumbPosition

Routes retail browser slider-thumb positioning through the shared helper.
=============
*/
static float CG_BrowserSliderThumbPosition( void *widget ) {
	return Item_Slider_ThumbPosition( (itemDef_t *)widget );
}

/*
=============
CG_BrowserSetTextExtents

Routes retail browser text-extent updates through the shared helper.
=============
*/
static void CG_BrowserSetTextExtents( void *widget, int *width, int *height, const char *text ) {
	Item_SetTextExtents( (itemDef_t *)widget, width, height, text );
}

/*
=============
CG_DrawBrowserSliderControl

Paints one retail browser slider through the shared painter.
=============
*/
static void CG_DrawBrowserSliderControl( void *widget ) {
	Item_Slider_Paint( (itemDef_t *)widget );
}

/*
=============
CG_DrawBrowserSliderColorControl

Paints one retail browser color-slider through the shared painter.
=============
*/
static void CG_DrawBrowserSliderColorControl( void *widget ) {
	Item_SliderColor_Paint( (itemDef_t *)widget );
}

/*
=============
CG_BrowserTextColor

Routes retail browser text-color resolution through the shared helper.
=============
*/
static void CG_BrowserTextColor( void *widget, vec4_t *newColor ) {
	Item_TextColor( (itemDef_t *)widget, newColor );
}

/*
=============
CG_DrawBrowserAutoWrappedText

Paints one retail browser auto-wrapped text widget through the shared painter.
=============
*/
static void CG_DrawBrowserAutoWrappedText( void *widget ) {
	Item_Text_AutoWrapped_Paint( (itemDef_t *)widget );
}

/*
=============
CG_DrawBrowserWrappedText

Paints one retail browser wrapped text widget through the shared painter.
=============
*/
static void CG_DrawBrowserWrappedText( void *widget ) {
	Item_Text_Wrapped_Paint( (itemDef_t *)widget );
}

/*
=============
CG_DrawBrowserText

Paints one retail browser text widget through the cgame-owned wrapper chain.
=============
*/
static void CG_DrawBrowserText( void *widget ) {
	itemDef_t	*item;

	item = (itemDef_t *)widget;
	if ( item == NULL ) {
		return;
	}

	if ( item->window.flags & WINDOW_WRAPPED ) {
		CG_DrawBrowserWrappedText( item );
		return;
	}

	if ( item->window.flags & WINDOW_AUTOWRAPPED ) {
		CG_DrawBrowserAutoWrappedText( item );
		return;
	}

	Item_Text_Paint( item );
}

/*
=============
CG_DrawBrowserEditFieldControl

Paints one retail browser edit-field control through the shared painter.
=============
*/
static void CG_DrawBrowserEditFieldControl( void *widget ) {
	Item_TextField_Paint( (itemDef_t *)widget );
}

/*
=============
CG_DrawBrowserModelPreview

Paints one retail browser model preview through the shared painter.
=============
*/
static void CG_DrawBrowserModelPreview( void *widget ) {
	Item_Model_Paint( (itemDef_t *)widget );
}

/*
=============
CG_DrawBrowserListWidget

Paints one retail browser list widget through the shared painter.
=============
*/
static void CG_DrawBrowserListWidget( void *widget ) {
	Item_ListBox_Paint( (itemDef_t *)widget );
}

/*
=============
CG_DrawBrowserTextField

Paints one retail browser text field through the cgame-owned edit-field wrapper.
=============
*/
static void CG_DrawBrowserTextField( void *widget ) {
	CG_DrawBrowserEditFieldControl( widget );
}

/*
=============
CG_CloseBrowserWindowCinematic

Stops one active retail browser cinematic window.
=============
*/
static void CG_CloseBrowserWindowCinematic( Window *window ) {
	if ( window == NULL ) {
		return;
	}

	if ( window->style == WINDOW_STYLE_CINEMATIC && window->cinematic >= 0 && cgDC.stopCinematic ) {
		cgDC.stopCinematic( window->cinematic );
		window->cinematic = -1;
	}
}

/*
=============
CG_CloseBrowserMenuCinematics

Stops one retail browser overlay's active cinematics.
=============
*/
static void CG_CloseBrowserMenuCinematics( menuDef_t *menu ) {
	int	i;

	if ( menu == NULL ) {
		return;
	}

	CG_CloseBrowserWindowCinematic( &menu->window );
	for ( i = 0; i < menu->itemCount; i++ ) {
		CG_CloseBrowserWindowCinematic( &menu->items[i]->window );
		if ( menu->items[i]->type == ITEM_TYPE_OWNERDRAW && cgDC.stopCinematic ) {
			cgDC.stopCinematic( 0 - menu->items[i]->window.ownerDraw );
		}
	}
}

/*
=============
CG_CloseBrowserCinematics

Stops active retail browser cinematics through a cgame-owned display pass.
=============
*/
static void CG_CloseBrowserCinematics( void ) {
	int	i;

	for ( i = 0; i < menuCount; i++ ) {
		CG_CloseBrowserMenuCinematics( &Menus[i] );
	}
}

/*
=============
CG_ActivateBrowserOverlay

Activates one retail browser overlay through a cgame-owned wrapper.
=============
*/
void CG_ActivateBrowserOverlay( void *overlay ) {
	if ( overlay == NULL ) {
		return;
	}

	Menus_Activate( (menuDef_t *)overlay );
}

/*
=============
CG_BrowserMultiHandleKey

Routes retail browser multi-choice key handling through the shared helper.
=============
*/
static qboolean CG_BrowserMultiHandleKey( void *widget, int key ) {
	return Item_Multi_HandleKey( (itemDef_t *)widget, key );
}

/*
=============
CG_BrowserPresetListHandleKey

Routes retail browser preset-list key handling through the shared helper.
=============
*/
static qboolean CG_BrowserPresetListHandleKey( void *widget, int key ) {
	return Item_PresetList_HandleKey( (itemDef_t *)widget, key );
}

/*
=============
CG_BrowserListRepeatScroll

Routes retail browser list auto-scroll repeats through the shared list-box helper.
=============
*/
static void CG_BrowserListRepeatScroll( void *widget, int key ) {
	Item_ListBox_HandleKey( (itemDef_t *)widget, key, qtrue, qfalse );
}

/*
=============
CG_BrowserListDragThumb

Applies one retail browser list-thumb drag sample through the shared list geometry.
=============
*/
static void CG_BrowserListDragThumb( void *widget, float x, float y ) {
	int		pos;
	int		max;
	itemDef_t	*item;
	listBoxDef_t	*listPtr;
	rectDef_t	r;

	item = (itemDef_t *)widget;
	if ( item == NULL || item->typeData == NULL ) {
		return;
	}

	listPtr = (listBoxDef_t *)item->typeData;
	max = CG_BrowserListMaxScroll( item );
	if ( item->window.flags & WINDOW_HORIZONTAL ) {
		r.x = item->window.rect.x + SCROLLBAR_SIZE + 1;
		r.y = item->window.rect.y + item->window.rect.h - SCROLLBAR_SIZE - 1;
		r.h = SCROLLBAR_SIZE;
		r.w = item->window.rect.w - ( SCROLLBAR_SIZE * 2 ) - 2;
		pos = ( (int)x - r.x - SCROLLBAR_SIZE / 2 ) * max / ( r.w - SCROLLBAR_SIZE );
	} else {
		r.x = item->window.rect.x + item->window.rect.w - SCROLLBAR_SIZE - 1;
		r.y = item->window.rect.y + SCROLLBAR_SIZE + 1;
		r.h = item->window.rect.h - ( SCROLLBAR_SIZE * 2 ) - 2;
		r.w = SCROLLBAR_SIZE;
		pos = ( (int)y - r.y - SCROLLBAR_SIZE / 2 ) * max / ( r.h - SCROLLBAR_SIZE );
	}

	if ( pos < 0 ) {
		pos = 0;
	} else if ( pos > max ) {
		pos = max;
	}

	listPtr->startPos = pos;
}

/*
=============
CG_BrowserSliderApplyFromCursor

Applies one retail browser slider sample through the cgame-owned value wrapper.
=============
*/
static void CG_BrowserSliderApplyFromCursor( void *widget, float x ) {
	char		buffer[64];
	char		format[16];
	float		baseX;
	float		value;
	itemDef_t	*item;
	editFieldDef_t	*editPtr;

	item = (itemDef_t *)widget;
	if ( item == NULL || item->typeData == NULL || item->cvar == NULL || cgDC.setCVar == NULL ) {
		return;
	}

	editPtr = (editFieldDef_t *)item->typeData;
	if ( item->text ) {
		baseX = item->textRect.x + item->textRect.w + 8;
	} else {
		baseX = item->window.rect.x;
	}

	if ( x < baseX ) {
		x = baseX;
	} else if ( x > baseX + SLIDER_WIDTH ) {
		x = baseX + SLIDER_WIDTH;
	}

	value = ( x - baseX ) / SLIDER_WIDTH;
	value *= ( editPtr->maxVal - editPtr->minVal );
	value += editPtr->minVal;

	if ( item->integer ) {
		Com_sprintf( buffer, sizeof( buffer ), "%i", (int)ceil( value ) );
	} else if ( item->precision > 0 ) {
		Com_sprintf( format, sizeof( format ), "%%.%df", item->precision );
		Com_sprintf( buffer, sizeof( buffer ), format, value );
	} else {
		Com_sprintf( buffer, sizeof( buffer ), "%f", value );
	}

	cgDC.setCVar( item->cvar, buffer );
}

/*
=============
CG_BrowserStartCapture

Routes retail browser capture-start requests through the shared item-capture helper.
=============
*/
static void CG_BrowserStartCapture( void *widget, int key ) {
	Item_StartCapture( (itemDef_t *)widget, key );
}

/*
=============
CG_BrowserSliderHandleKey

Routes retail browser slider key handling through the shared helper.
=============
*/
static qboolean CG_BrowserSliderHandleKey( void *widget, int key, qboolean down ) {
	return Item_Slider_HandleKey( (itemDef_t *)widget, key, down );
}

/*
=============
CG_BrowserSliderOverControl

Routes retail browser slider hit tests through the shared helper.
=============
*/
static int CG_BrowserSliderOverControl( void *widget, float x, float y ) {
	return Item_Slider_OverSlider( (itemDef_t *)widget, x, y );
}

/*
=============
CG_BrowserWidgetHandleKey

Routes focused retail browser control keys through the shared per-widget handlers.
=============
*/
static qboolean CG_BrowserWidgetHandleKey( void *widget, int key, qboolean down ) {
	itemDef_t	*item;

	item = (itemDef_t *)widget;
	if ( item == NULL ) {
		return qfalse;
	}

	switch ( item->type ) {
	case ITEM_TYPE_LISTBOX:
		return Item_ListBox_HandleKey( item, key, down, qfalse );
	case ITEM_TYPE_YESNO:
		return Item_YesNo_HandleKey( item, key );
	case ITEM_TYPE_MULTI:
		return CG_BrowserMultiHandleKey( item, key );
	case ITEM_TYPE_BIND:
		return CG_BrowserBindHandleKey( item, key, down );
	case ITEM_TYPE_SLIDER:
	case ITEM_TYPE_SLIDER_COLOR:
		return CG_BrowserSliderHandleKey( item, key, down );
	case ITEM_TYPE_PRESETLIST:
		return CG_BrowserPresetListHandleKey( item, key );
	default:
		return qfalse;
	}
}

/*
=============
CG_DrawBrowserWidgetFrame

Paints one retail browser root or widget frame through the shared window
runtime.
=============
*/
static void CG_DrawBrowserWidgetFrame( Window *window, float fadeAmount, float fadeClamp, float fadeCycle ) {
	if ( window == NULL ) {
		return;
	}

	Window_Paint( window, fadeAmount, fadeClamp, fadeCycle );
}

/*
=============
CG_DrawBrowserWidget

Runs one retail browser widget through the cgame-owned draw dispatcher while
reusing the shared widget painters underneath.
=============
*/
static void CG_DrawBrowserWidget( void *widget ) {
	itemDef_t	*item;

	item = (itemDef_t *)widget;
	if ( item == NULL ) {
		return;
	}

	CG_AllocBrowserWidgetState( item );

	/*
	=============
	Retail browser overlays paint through the shared item dispatcher so every
	widget receives its window/background pass before any type-specific body
	paint. This keeps decorative scoreboard frames authored as default text items
	visible in cgame just like they are in the UI module.
	=============
	*/
	Item_Paint( item );
}

/*
=============
CG_ResolveBrowserMenuWidescreenMode

Mirrors the shared menu widescreen resolver for cgame-owned direct overlay
paints that bypass Menu_Paint.
=============
*/
static int CG_ResolveBrowserMenuWidescreenMode( const menuDef_t *menu ) {
	if ( menu == NULL ) {
		return WIDESCREEN_STRETCH;
	}

	if ( !menu->widescreenSet && !menu->fullScreen ) {
		return WIDESCREEN_CENTER;
	}

	return menu->widescreen;
}

/*
=============
CG_DrawBrowserFullscreenBackground

Draws cgame-owned fullscreen overlay backgrounds through the retail
backgroundSize source-aspect crop path.
=============
*/
static void CG_DrawBrowserFullscreenBackground( const menuDef_t *menu ) {
	float	sourceWidth;
	float	sourceHeight;
	float	screenWidth;
	float	screenHeight;
	float	s0;

	if ( menu == NULL ) {
		return;
	}

	sourceWidth = menu->backgroundRect.w;
	if ( sourceWidth > 0.0f ) {
		sourceHeight = menu->backgroundRect.h;
		screenWidth = (float)cgDC.glconfig.vidWidth;
		screenHeight = (float)cgDC.glconfig.vidHeight;
		s0 = ( ( sourceWidth - screenWidth * ( sourceHeight / screenHeight ) ) / sourceWidth ) * 0.5f;
		cgDC.drawStretchPic( 0.0f, 0.0f, screenWidth, screenHeight, s0, 0.0f, 1.0f - s0, 1.0f, menu->window.background );
		return;
	}

	cgDC.drawHandlePic( 0.0f, 0.0f, SCREEN_WIDTH, SCREEN_HEIGHT, menu->window.background );
}

/*
=============
CG_DrawBrowserOverlayTree

Paints one retail browser overlay root through the cgame-owned draw dispatcher.
=============
*/
void CG_DrawBrowserOverlayTree( void *overlay, qboolean forcePaint ) {
	int			i;
	menuDef_t		*menu;

	menu = (menuDef_t *)overlay;
	if ( menu == NULL ) {
		return;
	}

	if ( !( menu->window.flags & WINDOW_VISIBLE ) && !forcePaint ) {
		return;
	}

	if ( ( menu->window.ownerDrawFlags || menu->window.ownerDrawFlags2 ) && cgDC.ownerDrawVisible &&
		!cgDC.ownerDrawVisible( menu->window.ownerDrawFlags, menu->window.ownerDrawFlags2 ) ) {
		return;
	}

	if ( forcePaint ) {
		menu->window.flags |= WINDOW_FORCED;
	}

	CG_UpdateBrowserPresetLists( menu );

	if ( cgDC.setAdjustFrom640Mode ) {
		cgDC.setAdjustFrom640Mode( CG_ResolveBrowserMenuWidescreenMode( menu ) );
	}

	if ( menu->fullScreen ) {
		CG_DrawBrowserFullscreenBackground( menu );
	}

	CG_DrawBrowserWidgetFrame( &menu->window, menu->fadeAmount, menu->fadeClamp, menu->fadeCycle );

	for ( i = 0; i < menu->itemCount; i++ ) {
		CG_DrawBrowserWidget( menu->items[i] );
	}

	if ( cgDC.setAdjustFrom640Mode ) {
		cgDC.setAdjustFrom640Mode( WIDESCREEN_CENTER );
	}
}

/*
=============
CG_DrawBrowserOverlays

Runs the active retail browser overlay frame pump through a cgame-owned entry
point while preserving the shared capture-repeat runtime underneath.
=============
*/
void CG_DrawBrowserOverlays( void ) {
	Menu_PaintAll();
}

/*
=============
CG_BrowserRectContainsPoint

Routes the retail browser rect hit-test through the shared menu helper.
=============
*/
static qboolean CG_BrowserRectContainsPoint( const rectDef_t *rect, float x, float y ) {
	return Rect_ContainsPoint( (rectDef_t *)rect, x, y );
}

/*
=============
CG_BrowserItemsMatchingGroup

Counts retail browser widgets that match one name or group token.
=============
*/
static int CG_BrowserItemsMatchingGroup( void *overlay, const char *name ) {
	return Menu_ItemsMatchingGroup( (menuDef_t *)overlay, name );
}

/*
=============
CG_BrowserGetMatchingItemByNumber

Returns the Nth retail browser widget matching one name or group token.
=============
*/
static void *CG_BrowserGetMatchingItemByNumber( const char *name, void *overlay, int index ) {
	return Menu_GetMatchingItemByNumber( (menuDef_t *)overlay, index, name );
}

/*
=============
CG_FindBrowserWidgetByName

Finds one retail browser widget by name inside an overlay root.
=============
*/
static void *CG_FindBrowserWidgetByName( void *overlay, const char *name ) {
	return Menu_FindItemByName( (menuDef_t *)overlay, name );
}

/*
=============
CG_RunBrowserScript

Runs one retail browser widget script through the shared script-command table.
=============
*/
static void CG_RunBrowserScript( void *widget, const char *script ) {
	Item_RunScript( (itemDef_t *)widget, script );
}

/*
=============
CG_BrowserWidgetEnableShowViaCvar

Gates one retail browser widget through its enable/show cvar conditions.
=============
*/
static qboolean CG_BrowserWidgetEnableShowViaCvar( void *widget, int flag ) {
	return Item_EnableShowViaCvar( (itemDef_t *)widget, flag );
}

/*
=============
CG_ShowBrowserItemsByName

Shows or hides retail browser widgets by name or group and stops hidden
cinematics.
=============
*/
static void CG_ShowBrowserItemsByName( const char *name, void *overlay, qboolean show ) {
	int			count;
	int			i;
	menuDef_t		*menu;
	itemDef_t		*item;

	menu = (menuDef_t *)overlay;
	if ( menu == NULL || name == NULL || !name[0] ) {
		return;
	}

	count = CG_BrowserItemsMatchingGroup( menu, name );
	for ( i = 0; i < count; i++ ) {
		item = CG_BrowserGetMatchingItemByNumber( name, menu, i );
		if ( item == NULL ) {
			continue;
		}

		if ( show ) {
			item->window.flags |= WINDOW_VISIBLE;
			continue;
		}

		item->window.flags &= ~WINDOW_VISIBLE;
		if ( cgDC.stopCinematic && item->window.cinematic >= 0 ) {
			cgDC.stopCinematic( item->window.cinematic );
			item->window.cinematic = -1;
		}
	}
}

/*
=============
CG_BrowserScriptShow

Runs the retail browser `show` verb through the cgame-owned item visibility
wrapper.
=============
*/
static void CG_BrowserScriptShow( void *widget, char **args ) {
	const char	*name;
	itemDef_t	*item;

	item = (itemDef_t *)widget;
	if ( item && String_Parse( args, &name ) ) {
		CG_ShowBrowserItemsByName( name, item->parent, qtrue );
	}
}

/*
=============
CG_BrowserScriptHide

Runs the retail browser `hide` verb through the cgame-owned item visibility
wrapper.
=============
*/
static void CG_BrowserScriptHide( void *widget, char **args ) {
	const char	*name;
	itemDef_t	*item;

	item = (itemDef_t *)widget;
	if ( item && String_Parse( args, &name ) ) {
		CG_ShowBrowserItemsByName( name, item->parent, qfalse );
	}
}

/*
=============
CG_BrowserScriptOpen

Runs the retail browser `open` verb through the cgame-owned overlay open
wrapper.
=============
*/
static void CG_BrowserScriptOpen( void *widget, char **args ) {
	const char	*name;

	(void)widget;

	if ( String_Parse( args, &name ) ) {
		CG_OpenBrowserOverlayByName( name );
	}
}

/*
=============
CG_BrowserScriptConditionalOpen

Runs the retail browser `conditionalopen` verb through the cgame-owned overlay
open wrapper.
=============
*/
static void CG_BrowserScriptConditionalOpen( void *widget, char **args ) {
	const char	*cvar;
	const char	*name1;
	const char	*name2;
	float		value;

	(void)widget;

	if ( String_Parse( args, &cvar ) && String_Parse( args, &name1 ) && String_Parse( args, &name2 ) ) {
		value = trap_Cvar_VariableValue( cvar );
		if ( value == 0.0f ) {
			CG_OpenBrowserOverlayByName( name2 );
		} else {
			CG_OpenBrowserOverlayByName( name1 );
		}
	}
}

/*
=============
CG_BrowserScriptClose

Runs the retail browser `close` verb through the cgame-owned overlay close
wrapper.
=============
*/
static void CG_BrowserScriptClose( void *widget, char **args ) {
	const char	*name;

	(void)widget;

	if ( String_Parse( args, &name ) ) {
		CG_CloseBrowserOverlayByName( name );
	}
}

/*
=============
CG_BrowserScriptToggle

Runs the retail browser `toggle` verb by closing visible overlays and opening
hidden ones through the cgame-owned overlay wrappers.
=============
*/
static void CG_BrowserScriptToggle( void *widget, char **args ) {
	const char	*name;
	menuDef_t	*menu;

	(void)widget;

	if ( !String_Parse( args, &name ) ) {
		return;
	}

	menu = CG_FindBrowserOverlayByName( name );
	if ( menu == NULL ) {
		return;
	}

	if ( menu->window.flags & WINDOW_VISIBLE ) {
		CG_CloseBrowserOverlayByName( name );
		return;
	}

	CG_OpenBrowserOverlayByName( name );
}

/*
=============
CG_BrowserScriptSetFocus

Runs the retail browser `setfocus` verb through the cgame-owned widget lookup
and focus helpers.
=============
*/
static void CG_BrowserScriptSetFocus( void *widget, char **args ) {
	const char	*name;
	itemDef_t	*focusItem;
	itemDef_t	*item;

	item = (itemDef_t *)widget;
	if ( item == NULL || !String_Parse( args, &name ) ) {
		return;
	}

	focusItem = CG_FindBrowserWidgetByName( item->parent, name );
	if ( focusItem && !( focusItem->window.flags & WINDOW_DECORATION ) &&
		!( focusItem->window.flags & WINDOW_HASFOCUS ) ) {
		CG_ClearBrowserFocus( item->parent );
		focusItem->window.flags |= WINDOW_HASFOCUS;
		if ( focusItem->onFocus ) {
			CG_RunBrowserScript( focusItem, focusItem->onFocus );
		}
		if ( cgDC.Assets.itemFocusSound && cgDC.startLocalSound ) {
			cgDC.startLocalSound( cgDC.Assets.itemFocusSound, CHAN_LOCAL_SOUND );
		}
	}
}

/*
=============
CG_BrowserCorrectedTextRect

Returns the retail browser text bounds used for active-item hit tests.
=============
*/
static rectDef_t *CG_BrowserCorrectedTextRect( void *widget ) {
	itemDef_t		*item;
	static rectDef_t rect;

	item = widget;
	memset( &rect, 0, sizeof( rect ) );
	if ( item ) {
		rect = item->textRect;
		if ( rect.w ) {
			rect.y -= rect.h;
		}
	}

	return &rect;
}

/*
=============
CG_BrowserOverActiveItem

Mirrors the retail browser active-item hit test used before OOB clicks.
=============
*/
static qboolean CG_BrowserOverActiveItem( void *overlay, float x, float y ) {
	int			i;
	menuDef_t		*menu;
	itemDef_t		*item;

	menu = overlay;
	if ( !menu ) {
		return qfalse;
	}

	if ( !( menu->window.flags & ( WINDOW_VISIBLE | WINDOW_FORCED ) ) ) {
		return qfalse;
	}

	/* CG_BrowserRectContainsPoint( &menu->window.rect, x, y ) */
	if ( !Rect_ContainsPoint( &menu->window.rect, x, y ) ) {
		return qfalse;
	}

	for ( i = 0; i < menu->itemCount; i++ ) {
		item = menu->items[i];
		if ( !( item->window.flags & ( WINDOW_VISIBLE | WINDOW_FORCED ) ) ) {
			continue;
		}

		if ( item->window.flags & WINDOW_DECORATION ) {
			continue;
		}

		/* CG_BrowserRectContainsPoint( &item->window.rect, x, y ) */
		if ( !Rect_ContainsPoint( &item->window.rect, x, y ) ) {
			continue;
		}

		if ( item->type == ITEM_TYPE_TEXT && item->text ) {
			/* CG_BrowserRectContainsPoint( CG_BrowserCorrectedTextRect( item ), x, y ) */
			if ( Rect_ContainsPoint( CG_BrowserCorrectedTextRect( item ), x, y ) ) {
				return qtrue;
			}
			continue;
		}

		return qtrue;
	}

	return qfalse;
}

/*
=============
CG_GetFocusedBrowserOverlay

Returns the focused browser overlay used by the retail key path.
=============
*/
static void *CG_GetFocusedBrowserOverlay( void ) {
	return Menu_GetFocused();
}

/*
=============
CG_ClearBrowserFocus

Clears focus from the current retail browser overlay root.
=============
*/
static void *CG_ClearBrowserFocus( void *overlay ) {
	return Menu_ClearFocus( (menuDef_t *)overlay );
}

/*
=============
CG_BrowserHandleOOBClick

Routes the retail browser out-of-bounds click path through the shared overlay
activation helper.
=============
*/
static void CG_BrowserHandleOOBClick( void *overlay, int key, qboolean down ) {
	Menus_HandleOOBClick( (menuDef_t *)overlay, key, down );
}

/*
=============
CG_SetBrowserFocus

Assigns focus to one retail browser widget through the cgame-owned runtime
helper chain.
=============
*/
static qboolean CG_SetBrowserFocus( void *widget, float x, float y ) {
	int			i;
	itemDef_t		*item;
	itemDef_t		*oldFocus;
	sfxHandle_t		*sfx;
	qboolean		playSound;
	menuDef_t		*parent;

	item = (itemDef_t *)widget;
	sfx = &cgDC.Assets.itemFocusSound;
	playSound = qfalse;

	if ( item == NULL || item->window.flags & WINDOW_DECORATION || item->window.flags & WINDOW_HASFOCUS ||
		!( item->window.flags & WINDOW_VISIBLE ) ) {
		return qfalse;
	}

	parent = (menuDef_t *)item->parent;
	if ( !CG_BrowserWidgetEnableShowViaCvar( item, CVAR_ENABLE ) ) {
		return qfalse;
	}

	if ( !CG_BrowserWidgetEnableShowViaCvar( item, CVAR_SHOW ) ) {
		return qfalse;
	}

	oldFocus = CG_ClearBrowserFocus( item->parent );

	if ( item->type == ITEM_TYPE_TEXT ) {
		if ( CG_BrowserRectContainsPoint( CG_BrowserCorrectedTextRect( item ), x, y ) ) {
			item->window.flags |= WINDOW_HASFOCUS;
			if ( item->focusSound ) {
				sfx = &item->focusSound;
			}
			playSound = qtrue;
		} else if ( oldFocus ) {
			oldFocus->window.flags |= WINDOW_HASFOCUS;
			if ( oldFocus->onFocus ) {
				CG_RunBrowserScript( oldFocus, oldFocus->onFocus );
			}
		}
	} else {
		item->window.flags |= WINDOW_HASFOCUS;
		if ( item->onFocus ) {
			CG_RunBrowserScript( item, item->onFocus );
		}
		if ( item->focusSound ) {
			sfx = &item->focusSound;
		}
		playSound = qtrue;
	}

	if ( playSound && sfx && cgDC.startLocalSound ) {
		cgDC.startLocalSound( *sfx, CHAN_LOCAL_SOUND );
	}

	if ( parent ) {
		for ( i = 0; i < parent->itemCount; i++ ) {
			if ( parent->items[i] == item ) {
				parent->cursorItem = i;
				break;
			}
		}
	}

	return qtrue;
}

/*
=============
CG_SetBrowserMouseOver

Updates the retail browser widget hover bit through the shared menu runtime.
=============
*/
static void CG_SetBrowserMouseOver( void *widget, qboolean focus ) {
	Item_SetMouseOver( (itemDef_t *)widget, focus );
}

/*
=============
CG_BrowserMouseEnter

Routes one retail browser mouse-enter transition through the cgame-owned
runtime helper chain.
=============
*/
static void CG_BrowserMouseEnter( void *widget, float x, float y ) {
	itemDef_t	*item;

	item = (itemDef_t *)widget;
	if ( item == NULL ) {
		return;
	}

	if ( !CG_BrowserWidgetEnableShowViaCvar( item, CVAR_ENABLE ) ) {
		return;
	}

	if ( !CG_BrowserWidgetEnableShowViaCvar( item, CVAR_SHOW ) ) {
		return;
	}

	if ( CG_BrowserRectContainsPoint( CG_BrowserCorrectedTextRect( item ), x, y ) ) {
		if ( !( item->window.flags & WINDOW_MOUSEOVERTEXT ) ) {
			CG_RunBrowserScript( item, item->mouseEnterText );
			item->window.flags |= WINDOW_MOUSEOVERTEXT;
		}
		if ( !( item->window.flags & WINDOW_MOUSEOVER ) ) {
			CG_RunBrowserScript( item, item->mouseEnter );
			CG_SetBrowserMouseOver( item, qtrue );
		}
		return;
	}

	if ( item->window.flags & WINDOW_MOUSEOVERTEXT ) {
		CG_RunBrowserScript( item, item->mouseExitText );
		item->window.flags &= ~WINDOW_MOUSEOVERTEXT;
	}

	if ( !( item->window.flags & WINDOW_MOUSEOVER ) ) {
		CG_RunBrowserScript( item, item->mouseEnter );
		CG_SetBrowserMouseOver( item, qtrue );
	}

	if ( item->type == ITEM_TYPE_LISTBOX ) {
		Item_ListBox_MouseEnter( item, x, y );
	}
}

/*
=============
CG_BrowserMouseLeave

Routes one retail browser mouse-leave transition through the cgame-owned
runtime helper chain and clears the widget hover bit.
=============
*/
static void CG_BrowserMouseLeave( void *widget ) {
	itemDef_t	*item;

	item = (itemDef_t *)widget;
	if ( item == NULL ) {
		return;
	}

	if ( item->window.flags & WINDOW_MOUSEOVERTEXT ) {
		CG_RunBrowserScript( item, item->mouseExitText );
		item->window.flags &= ~WINDOW_MOUSEOVERTEXT;
	}

	CG_RunBrowserScript( item, item->mouseExit );
	item->window.flags &= ~( WINDOW_LB_RIGHTARROW | WINDOW_LB_LEFTARROW );
	CG_SetBrowserMouseOver( widget, qfalse );
}

/*
=============
CG_SetPrevBrowserCursorItem

Walks focus to the previous retail browser widget and refreshes hover state on
the newly focused control.
=============
*/
static void *CG_SetPrevBrowserCursorItem( void *overlay ) {
	qboolean	wrapped;
	int		oldCursor;
	menuDef_t	*menu;

	menu = (menuDef_t *)overlay;
	if ( menu == NULL ) {
		return NULL;
	}

	wrapped = qfalse;
	oldCursor = menu->cursorItem;
	if ( menu->cursorItem < 0 ) {
		menu->cursorItem = menu->itemCount - 1;
		wrapped = qtrue;
	}

	while ( menu->cursorItem > -1 ) {
		menu->cursorItem--;
		if ( menu->cursorItem < 0 && !wrapped ) {
			wrapped = qtrue;
			menu->cursorItem = menu->itemCount - 1;
		}

		if ( CG_SetBrowserFocus( menu->items[menu->cursorItem], (float)cgDC.cursorx, (float)cgDC.cursory ) ) {
			CG_BrowserHandleMouseMove( menu, menu->items[menu->cursorItem]->window.rect.x + 1, menu->items[menu->cursorItem]->window.rect.y + 1 );
			return menu->items[menu->cursorItem];
		}
	}

	menu->cursorItem = oldCursor;
	return NULL;
}

/*
=============
CG_SetNextBrowserCursorItem

Walks focus to the next retail browser widget and refreshes hover state on the
newly focused control.
=============
*/
static void *CG_SetNextBrowserCursorItem( void *overlay ) {
	qboolean	wrapped;
	int		oldCursor;
	menuDef_t	*menu;

	menu = (menuDef_t *)overlay;
	if ( menu == NULL ) {
		return NULL;
	}

	wrapped = qfalse;
	oldCursor = menu->cursorItem;
	if ( menu->cursorItem == -1 ) {
		menu->cursorItem = 0;
		wrapped = qtrue;
	}

	while ( menu->cursorItem < menu->itemCount ) {
		menu->cursorItem++;
		if ( menu->cursorItem >= menu->itemCount && !wrapped ) {
			wrapped = qtrue;
			menu->cursorItem = 0;
		}

		if ( CG_SetBrowserFocus( menu->items[menu->cursorItem], (float)cgDC.cursorx, (float)cgDC.cursory ) ) {
			CG_BrowserHandleMouseMove( menu, menu->items[menu->cursorItem]->window.rect.x + 1, menu->items[menu->cursorItem]->window.rect.y + 1 );
			return menu->items[menu->cursorItem];
		}
	}

	menu->cursorItem = oldCursor;
	return NULL;
}

/*
=============
CG_BrowserHandleKey

Routes retail browser key handling through the focused overlay.
=============
*/
static void CG_BrowserHandleKey( void *overlay, int key, qboolean down, unsigned int time ) {
	menuDef_t *menu;

	(void)time;

	menu = overlay;
	if ( !menu ) {
		return;
	}

	if ( down && !( menu->window.flags & WINDOW_POPUP ) &&
		!CG_BrowserOverActiveItem( menu, (float)cgDC.cursorx, (float)cgDC.cursory ) &&
		( key == K_MOUSE1 || key == K_MOUSE2 || key == K_MOUSE3 ) ) {
		/* Menus_HandleOOBClick( menu, key, down ); */
		CG_BrowserHandleOOBClick( menu, key, down );
		return;
	}

	if ( down && key == K_F11 ) {
		return;
	}

	if ( down && key == K_F12 ) {
		trap_SendConsoleCommand( "screenshotJPEG\n" );
		return;
	}

	Menu_HandleKey( menu, key, down );
}

/*
=============
CG_BrowserDisplayHandleKey

Routes browser key handling through the focused retail overlay.
=============
*/
static void CG_BrowserDisplayHandleKey( int key, qboolean down, int x, int y ) {
	void *overlay;

	cgDC.cursorx = x;
	cgDC.cursory = y;

	overlay = CG_BrowserDisplayCaptureItem( x, y );
	if ( !overlay ) {
		overlay = CG_GetFocusedBrowserOverlay();
	}
	if ( !overlay ) {
		return;
	}

	CG_BrowserHandleKey( overlay, key, down, 0 );
}

/*
=============
CG_RoundScreenCursorCoord
=============
*/
static int CG_RoundScreenCursorCoord( float value ) {
	return (int)( value + 0.5f );
}

/*
=============
CG_ConvertScreenCursorXToVirtual

Projects a host screen-space X coordinate into the cgame 640-space cursor.
=============
*/
static int CG_ConvertScreenCursorXToVirtual( int x ) {
	float	virtualX;

	if ( cgs.screenXBias > 0.0f && cgs.screenXScale > 0.0f ) {
		virtualX = ( (float)x - cgs.screenXBias ) / cgs.screenXScale;
		return CG_RoundScreenCursorCoord( virtualX );
	}

	if ( cgs.glconfig.vidWidth <= 0 ) {
		return 0;
	}

	virtualX = (float)x * ( (float)SCREEN_WIDTH / (float)cgs.glconfig.vidWidth );
	return CG_RoundScreenCursorCoord( virtualX );
}

/*
=============
CG_ConvertScreenCursorYToVirtual

Projects a host screen-space Y coordinate into the cgame 480-space cursor.
=============
*/
static int CG_ConvertScreenCursorYToVirtual( int y ) {
	float	virtualY;

	if ( cgs.glconfig.vidHeight <= 0 ) {
		return 0;
	}

	virtualY = (float)y * ( (float)SCREEN_HEIGHT / (float)cgs.glconfig.vidHeight );
	return CG_RoundScreenCursorCoord( virtualY );
}

/*
=============
CG_MouseEvent

Routes captured mouse coordinates through the HUD when spectator overlays are active.
=============
*/
void CG_MouseEvent( int x, int y ) {
	int n;
	qboolean allowSpectatorUi;

	if ( cg_ignoreMouseInput.integer ) {
		return;
	}

	allowSpectatorUi = CG_ShouldCaptureSpectatorUi();

	if ( ( cg.predictedPlayerState.pm_type == PM_NORMAL || ( cg.predictedPlayerState.pm_type == PM_SPECTATOR && !allowSpectatorUi ) ) &&
		cg.showScores == qfalse ) {
		trap_Key_SetCatcher( 0 );
		return;
	}

	cgs.cursorX = CG_ConvertScreenCursorXToVirtual( x );
	cgs.cursorY = CG_ConvertScreenCursorYToVirtual( y );

	if ( cgs.cursorX < 0 ) {
		cgs.cursorX = 0;
	} else if ( cgs.cursorX > SCREEN_WIDTH ) {
		cgs.cursorX = SCREEN_WIDTH;
	}

	if ( cgs.cursorY < 0 ) {
		cgs.cursorY = 0;
	} else if ( cgs.cursorY > SCREEN_HEIGHT ) {
		cgs.cursorY = SCREEN_HEIGHT;
	}

	cgDC.cursorx = cgs.cursorX;
	cgDC.cursory = cgs.cursorY;

	n = CG_BrowserDisplayCursorType( cgs.cursorX, cgs.cursorY );
	cgs.activeCursor = 0;
	if ( n == CURSOR_ARROW ) {
		cgs.activeCursor = cgs.media.selectCursor;
	} else if ( n == CURSOR_SIZER ) {
		cgs.activeCursor = cgs.media.sizeCursor;
	}

	CG_BrowserDisplayMouseMove( NULL, cgs.cursorX, cgs.cursorY );
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
=============
CG_CloseRetailCommandCaptureOverlay

Closes the active cgame-owned command overlay without resetting the broader
event-handling latch.
=============
*/
static void CG_CloseRetailCommandCaptureOverlay( void ) {
	int catcher;

	if ( cgs.eventHandling == CGAME_EVENT_TEAMMENU ||
			cgs.eventHandling == CGAME_EVENT_EDITHUD ) {
		CG_HideTeamMenu();
	}

	CG_CloseJoinGameMenu();

	catcher = trap_Key_GetCatcher();
	if ( catcher & KEYCATCH_CGAME ) {
		trap_Key_SetCatcher( catcher & ~KEYCATCH_CGAME );
	}
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
CG_RefreshDisplayContext
==================
*/
static void CG_RefreshDisplayContext( void ) {
	trap_GetGlconfig( &cgs.glconfig );
	cgs.screenXScale = cgs.glconfig.vidWidth / 640.0f;
	cgs.screenYScale = cgs.glconfig.vidHeight / 480.0f;
	if ( cgs.glconfig.vidWidth * SCREEN_HEIGHT > cgs.glconfig.vidHeight * SCREEN_WIDTH ) {
		cgs.screenXBias = 0.5f * ( (float)cgs.glconfig.vidWidth - ( (float)cgs.glconfig.vidHeight * ( (float)SCREEN_WIDTH / (float)SCREEN_HEIGHT ) ) );
	} else {
		cgs.screenXBias = 0.0f;
	}

	cgDC.glconfig = cgs.glconfig;
	cgDC.xscale = cgs.screenXScale;
	cgDC.yscale = cgs.screenYScale;
	cgDC.bias = cgs.screenXBias;

	Init_Display( &cgDC );
}

/*
==================
CG_EventHandling
==================
 type 0 - no event handling
      1 - team menu
      2 - scoreboard
      3 - hud editor
      4 - refresh display context
      5 - close command overlay

*/
void CG_EventHandling(int type) {
	if ( type == CGAME_EVENT_REFRESH_DISPLAY_CONTEXT ) {
		CG_RefreshDisplayContext();
		return;
	}
	if ( type == CGAME_EVENT_CLOSECOMMANDOVERLAY ) {
		CG_CloseRetailCommandCaptureOverlay();
		return;
	}

	cgs.eventHandling = type;
  if (type == CGAME_EVENT_NONE) {
    CG_HideTeamMenu();
	CG_CloseJoinGameMenu();
  } else if (type == CGAME_EVENT_TEAMMENU) {
    //CG_ShowTeamMenu();
  } else if (type == CGAME_EVENT_SCOREBOARD) {
  }

}

/*
=============
CG_HandleHudBindingCommand

Mirrors the retail HUD key path that intercepts specific bound commands.
=============
*/
static qboolean CG_HandleHudBindingCommand( const char *binding ) {
	if ( !binding || !binding[0] ) {
		return qfalse;
	}

	if ( Q_stricmpn( binding, "messagemode", sizeof( "messagemode" ) - 1 ) == 0 ||
		Q_stricmpn( binding, "screenshot", sizeof( "screenshot" ) - 1 ) == 0 ||
		Q_stricmpn( binding, "screenshotJPEG", sizeof( "screenshotJPEG" ) - 1 ) == 0 ) {
		trap_SendConsoleCommand( binding );
		return qtrue;
	}

	if ( Q_stricmpn( binding, "+voice", sizeof( "+voice" ) - 1 ) == 0 ) {
		trap_SendConsoleCommand( "+voice\n" );
		return qtrue;
	}

	if ( Q_stricmpn( binding, "+scores", sizeof( "+scores" ) - 1 ) == 0 ) {
		CG_ScoresDown_f();
		return qtrue;
	}

	return qfalse;
}

/*
=============
CG_KeyEvent

Mirrors the retail focused-overlay key dispatcher.
=============
*/
void CG_KeyEvent(int key, qboolean down) {
	char bindingBuf[0x20] = { 0 };

	if ( !down ) {
		return;
	}

	trap_Key_GetBindingBuf( key, bindingBuf, sizeof( bindingBuf ) );
	if ( CG_HandleHudBindingCommand( bindingBuf ) ) {
		return;
	}

	CG_BrowserDisplayHandleKey( key, down, cgs.cursorX, cgs.cursorY );
}

/*
=============
CG_RunMenuScript

Executes the retained retail cgame menu-script commands.
=============
*/
void CG_RunMenuScript( char **args ) {
	const char *name;
	qboolean fullscreen;

	if ( !args ) {
		return;
	}

	if ( !String_Parse( args, &name ) ) {
		return;
	}

	if ( !Q_stricmp( name, "setFullScreen" ) ) {
		trap_Cvar_Set( "r_fullScreen", "1" );
		trap_SendConsoleCommand( "vid_restart fast\n" );
		return;
	}

	if ( !Q_stricmp( name, "setWindowed" ) ) {
		trap_Cvar_Set( "r_fullScreen", "0" );
		trap_SendConsoleCommand( "vid_restart fast\n" );
		return;
	}

	if ( !Q_stricmp( name, "toggleFullscreen" ) ) {
		fullscreen = ( trap_Cvar_VariableValue( "r_fullScreen" ) != 0.0f ) ? qtrue : qfalse;
		trap_Cvar_Set( "r_fullScreen", fullscreen ? "0" : "1" );
		trap_SendConsoleCommand( "vid_restart fast\n" );
	}
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
