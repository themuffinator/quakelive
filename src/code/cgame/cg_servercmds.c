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
// cg_servercmds.c -- reliably sequenced text commands sent by the server
// these are processed at snapshot transition time, so there will definately
// be a valid snapshot this frame

#include "cg_local.h"
#include "../../ui/menudef.h" // bk001205 - for Q3_ui as well
#include <stdlib.h>

#include "../../game/match_state_keys.h"

// Mirrors the VF_* vote flag bits exposed via g_voteFlags on the server.
#define CG_VOTEFLAG_NO_MAP	0x0001
#define CG_VOTEFLAG_NO_NEXTMAP	0x0004
#define CG_VOTEFLAG_NO_ENDVOTE	0x0800
#ifndef VF_NO_GAMETYPE
#define VF_NO_GAMETYPE	0x0008
#endif

typedef struct {
	const char *order;
	int taskNum;
} orderTask_t;

static const orderTask_t validOrders[] = {
	{ VOICECHAT_GETFLAG,						TEAMTASK_OFFENSE },
	{ VOICECHAT_OFFENSE,						TEAMTASK_OFFENSE },
	{ VOICECHAT_DEFEND,							TEAMTASK_DEFENSE },
	{ VOICECHAT_DEFENDFLAG,					TEAMTASK_DEFENSE },
	{ VOICECHAT_PATROL,							TEAMTASK_PATROL },
	{ VOICECHAT_CAMP,								TEAMTASK_CAMP },
	{ VOICECHAT_FOLLOWME,						TEAMTASK_FOLLOW },
	{ VOICECHAT_RETURNFLAG,					TEAMTASK_RETRIEVE },
	{ VOICECHAT_FOLLOWFLAGCARRIER,	TEAMTASK_ESCORT }
};

static const int numValidOrders = sizeof(validOrders) / sizeof(orderTask_t);

/*
=============
CG_CopyDefaultPmoveSettings

Copies the compiled pmove defaults into the destination buffer.
=============
*/
static void CG_CopyDefaultPmoveSettings( pmove_settings_t *settings ) {
	const pmove_settings_t *defaults;

	if ( !settings ) {
		return;
	}

	defaults = PM_GetDefaultSettings();
	if ( defaults ) {
		Com_Memcpy( settings, defaults, sizeof( pmove_settings_t ) );
	} else {
		Com_Memset( settings, 0, sizeof( pmove_settings_t ) );
	}

/*
=============
CG_SkipPmoveWhitespace

Advances the cursor past JSON whitespace characters.
=============
*/
static void CG_SkipPmoveWhitespace( const char **cursor ) {
	const char *c;

	if ( !cursor || !*cursor ) {
		return;
	}

	c = *cursor;
	while ( *c == ' ' || *c == '\t' || *c == '\n' || *c == '\r' ) {
		++c;
	}
	*cursor = c;
}

/*
=============
CG_ExpectPmoveChar

Validates that the next non-whitespace character matches the expected token.
=============
*/
static qboolean CG_ExpectPmoveChar( const char **cursor, char expected ) {
	if ( !cursor || !*cursor ) {
		return qfalse;
	}

	CG_SkipPmoveWhitespace( cursor );
	if ( !*cursor || **cursor != expected ) {
		return qfalse;
	}

	(*cursor)++;
	return qtrue;
}

/*
=============
CG_ParsePmoveJsonString

Parses a JSON string token, optionally copying it into the supplied buffer.
=============
*/
static qboolean CG_ParsePmoveJsonString( const char **cursor, char *buffer, size_t bufferSize ) {
	size_t length;

	if ( !cursor || !*cursor ) {
		return qfalse;
	}

	CG_SkipPmoveWhitespace( cursor );
	if ( **cursor != '"' ) {
		return qfalse;
	}

	(*cursor)++;
	length = 0u;
	while ( **cursor && **cursor != '"' ) {
		if ( buffer && bufferSize > 0u ) {
			if ( length + 1u >= bufferSize ) {
				return qfalse;
			}
			buffer[length++] = **cursor;
		}
		(*cursor)++;
	}

	if ( **cursor != '"' ) {
		return qfalse;
	}

	if ( buffer && bufferSize > 0u ) {
		buffer[length] = '\0';
	}

	(*cursor)++;
	return qtrue;
}

/*
=============
CG_ParsePmoveJsonBool

Reads a boolean token from the payload.
=============
*/
static qboolean CG_ParsePmoveJsonBool( const char **cursor, qboolean *value ) {
	if ( !cursor || !*cursor || !value ) {
		return qfalse;
	}

	CG_SkipPmoveWhitespace( cursor );
	if ( !Q_strnicmp( *cursor, "true", 4 ) ) {
		*value = qtrue;
		*cursor += 4;
		return qtrue;
	}

	if ( !Q_strnicmp( *cursor, "false", 5 ) ) {
		*value = qfalse;
		*cursor += 5;
		return qtrue;
	}

	return qfalse;
}

/*
=============
CG_ParsePmoveJsonFloat

Reads a floating point token from the payload.
=============
*/
static qboolean CG_ParsePmoveJsonFloat( const char **cursor, float *value ) {
	double parsed;
	char *endPtr;

	if ( !cursor || !*cursor || !value ) {
		return qfalse;
	}

	CG_SkipPmoveWhitespace( cursor );
	parsed = strtod( *cursor, &endPtr );
	if ( endPtr == *cursor ) {
		return qfalse;
	}

	*value = (float)parsed;
	*cursor = endPtr;
	return qtrue;
}

/*
=============
CG_ParsePmoveJsonInt

Reads an integer token from the payload.
=============
*/
static qboolean CG_ParsePmoveJsonInt( const char **cursor, int *value ) {
	long parsed;
	char *endPtr;

	if ( !cursor || !*cursor || !value ) {
		return qfalse;
	}

	CG_SkipPmoveWhitespace( cursor );
	parsed = strtol( *cursor, &endPtr, 10 );
	if ( endPtr == *cursor ) {
		return qfalse;
	}

	*value = (int)parsed;
	*cursor = endPtr;
	return qtrue;
}

/*
=============
CG_SkipPmoveJsonValue

Skips a JSON value so unknown tokens don't poison the decoder.
=============
*/
static qboolean CG_SkipPmoveJsonValue( const char **cursor ) {
	int depth;

	if ( !cursor || !*cursor ) {
		return qfalse;
	}

	CG_SkipPmoveWhitespace( cursor );
	if ( !*cursor ) {
		return qfalse;
	}

	if ( **cursor == '{' ) {
		depth = 1;
		(*cursor)++;
		while ( depth > 0 && **cursor ) {
			if ( **cursor == '{' ) {
				++depth;
				(*cursor)++;
			} else if ( **cursor == '}' ) {
				--depth;
				(*cursor)++;
			} else if ( **cursor == '"' ) {
				if ( !CG_ParsePmoveJsonString( cursor, NULL, 0 ) ) {
					return qfalse;
				}
			} else {
				(*cursor)++;
			}
		}
		return depth == 0;
	}

	if ( **cursor == '[' ) {
		depth = 1;
		(*cursor)++;
		while ( depth > 0 && **cursor ) {
			if ( **cursor == '[' ) {
				++depth;
				(*cursor)++;
			} else if ( **cursor == ']' ) {
				--depth;
				(*cursor)++;
			} else if ( **cursor == '"' ) {
				if ( !CG_ParsePmoveJsonString( cursor, NULL, 0 ) ) {
					return qfalse;
				}
			} else {
				(*cursor)++;
			}
		}
		return depth == 0;
	}

	if ( **cursor == '"' ) {
		return CG_ParsePmoveJsonString( cursor, NULL, 0 );
	}

	while ( **cursor && **cursor != ',' && **cursor != '}' && **cursor != ']' ) {
		(*cursor)++;
	}
	return qtrue;
}

/*
=============
CG_ParsePmoveWeaponReloadTimes

Decodes the weapon reload times array from the payload.
=============
*/
static qboolean CG_ParsePmoveWeaponReloadTimes( const char **cursor, int *reloadTimes ) {
	int weapon;

	if ( !cursor || !*cursor || !reloadTimes ) {
		return qfalse;
	}

	if ( !CG_ExpectPmoveChar( cursor, '[' ) ) {
		return qfalse;
	}

	weapon = 0;
	while ( qtrue ) {
		CG_SkipPmoveWhitespace( cursor );
		if ( !*cursor ) {
			return qfalse;
		}

		if ( **cursor == ']' ) {
			(*cursor)++;
			break;
		}

		if ( weapon >= WP_NUM_WEAPONS ) {
			return qfalse;
		}

		if ( !CG_ParsePmoveJsonInt( cursor, &reloadTimes[weapon] ) ) {
			return qfalse;
		}
		++weapon;

		CG_SkipPmoveWhitespace( cursor );
		if ( **cursor == ',' ) {
			(*cursor)++;
			continue;
		} else if ( **cursor == ']' ) {
			(*cursor)++;
			break;
		} else {
			return qfalse;
		}
	}

	return ( weapon == WP_NUM_WEAPONS );
}

/*
=============
CG_ParsePmoveSettingsPayload

Decodes the pmove configstring payload into a settings structure.
=============
*/
static qboolean CG_ParsePmoveSettingsPayload( const char *payload, pmove_settings_t *settings ) {
	pmove_settings_t parsed;
	const char *cursor;
	char key[64];
	qboolean valid;

	if ( !settings ) {
		return qfalse;
	}

	CG_CopyDefaultPmoveSettings( &parsed );
	if ( !payload || !*payload ) {
		Com_Memcpy( settings, &parsed, sizeof( parsed ) );
		return qfalse;
	}

	cursor = payload;
	if ( !CG_ExpectPmoveChar( &cursor, '{' ) ) {
		Com_Memcpy( settings, &parsed, sizeof( parsed ) );
		return qfalse;
	}

	valid = qtrue;
	while ( valid ) {
		CG_SkipPmoveWhitespace( &cursor );
		if ( !*cursor ) {
			valid = qfalse;
			break;
		}

		if ( *cursor == '}' ) {
			++cursor;
			break;
		}

		if ( !CG_ParsePmoveJsonString( &cursor, key, sizeof( key ) ) ) {
			valid = qfalse;
			break;
		}

		if ( !CG_ExpectPmoveChar( &cursor, ':' ) ) {
			valid = qfalse;
			break;
		}

		if ( !Q_stricmp( key, "weaponReloadOverrides" ) ) {
			if ( !CG_ParsePmoveWeaponReloadTimes( &cursor, parsed.weaponReloadOverrides ) ) {
				valid = qfalse;
			}
		} else if ( !Q_stricmp( key, "weaponReloadTimes" ) ) {
			if ( !CG_ParsePmoveWeaponReloadTimes( &cursor, parsed.weaponReloadTimes ) ) {
				valid = qfalse;
			}
		}

	#define PMOVE_BOOL_FIELD( name ) \
		else if ( !Q_stricmp( key, #name ) ) { \
			if ( !CG_ParsePmoveJsonBool( &cursor, &parsed.name ) ) { \
				valid = qfalse; \
			} \
		}
	#define PMOVE_INT_FIELD( name ) \
		else if ( !Q_stricmp( key, #name ) ) { \
			if ( !CG_ParsePmoveJsonInt( &cursor, &parsed.name ) ) { \
				valid = qfalse; \
			} \
		}
	#define PMOVE_FLOAT_FIELD( name ) \
		else if ( !Q_stricmp( key, #name ) ) { \
			if ( !CG_ParsePmoveJsonFloat( &cursor, &parsed.name ) ) { \
				valid = qfalse; \
			} \
		}

		PMOVE_FLOAT_FIELD( airAccel )
		PMOVE_FLOAT_FIELD( airControl )
		PMOVE_FLOAT_FIELD( airStepFriction )
		PMOVE_INT_FIELD( airSteps )
		PMOVE_FLOAT_FIELD( airStopAccel )
		PMOVE_BOOL_FIELD( autoHop )
		PMOVE_BOOL_FIELD( bunnyHop )
		PMOVE_BOOL_FIELD( chainJump )
		PMOVE_FLOAT_FIELD( chainJumpVelocity )
		PMOVE_FLOAT_FIELD( circleStrafeFriction )
		PMOVE_BOOL_FIELD( crouchSlide )
		PMOVE_FLOAT_FIELD( crouchSlideFriction )
		PMOVE_INT_FIELD( crouchSlideTime )
		PMOVE_FLOAT_FIELD( flightThrust )
		PMOVE_BOOL_FIELD( crouchStepJump )
		PMOVE_BOOL_FIELD( doubleJump )
		PMOVE_FLOAT_FIELD( jumpTimeDeltaMin )
		PMOVE_FLOAT_FIELD( jumpVelocity )
		PMOVE_FLOAT_FIELD( jumpVelocityMax )
		PMOVE_FLOAT_FIELD( jumpVelocityScaleAdd )
		PMOVE_FLOAT_FIELD( jumpVelocityTimeThreshold )
		PMOVE_FLOAT_FIELD( jumpVelocityTimeThresholdOffset )
		PMOVE_BOOL_FIELD( noPlayerClip )
		PMOVE_BOOL_FIELD( rampJump )
		PMOVE_FLOAT_FIELD( rampJumpScale )
		PMOVE_FLOAT_FIELD( stepHeight )
		PMOVE_BOOL_FIELD( stepJump )
		PMOVE_FLOAT_FIELD( stepJumpVelocity )
		PMOVE_FLOAT_FIELD( strafeAccel )
		PMOVE_FLOAT_FIELD( velocityGh )
		PMOVE_FLOAT_FIELD( walkAccel )
		PMOVE_FLOAT_FIELD( walkFriction )
		PMOVE_FLOAT_FIELD( waterSwimScale )
		PMOVE_FLOAT_FIELD( waterWadeScale )
		PMOVE_INT_FIELD( weaponDropTime )
		PMOVE_INT_FIELD( weaponRaiseTime )
		PMOVE_FLOAT_FIELD( wishSpeed )
		PMOVE_FLOAT_FIELD( machinegunIronsightsScale )
		PMOVE_FLOAT_FIELD( gauntletSpeedFactor )
		PMOVE_INT_FIELD( midAirMinimumHeight )
		PMOVE_BOOL_FIELD( nailgunBounceEnabled )
		PMOVE_INT_FIELD( nailgunBouncePercentage )
		PMOVE_FLOAT_FIELD( quadDamageMultiplier )
		PMOVE_BOOL_FIELD( guidedRocketEnabled )
		PMOVE_INT_FIELD( quadHogEnabled )
		PMOVE_INT_FIELD( quadHogIdleSeconds )
		PMOVE_INT_FIELD( quadHogTimeSeconds )
		PMOVE_INT_FIELD( quadHogPingRateSeconds )

#undef PMOVE_BOOL_FIELD
#undef PMOVE_INT_FIELD
#undef PMOVE_FLOAT_FIELD

		else {
			if ( !CG_SkipPmoveJsonValue( &cursor ) ) {
				valid = qfalse;
			}
		}

		if ( !valid ) {
			break;
		}

		CG_SkipPmoveWhitespace( &cursor );
		if ( *cursor == ',' ) {
			++cursor;
			continue;
		} else if ( *cursor == '}' ) {
			++cursor;
			break;
		} else {
			valid = qfalse;
			break;
		}
	}

	if ( !valid ) {
		CG_CopyDefaultPmoveSettings( &parsed );
	}

	Com_Memcpy( settings, &parsed, sizeof( parsed ) );
	return valid;
}

/*
=============
CG_ParsePmoveConfigString

Decodes the server broadcast pmove settings into the active client cache.
=============
*/
void CG_ParsePmoveConfigString( const char *payload ) {
	pmove_settings_t parsed;

	CG_ParsePmoveSettingsPayload( payload, &parsed );
	Com_Memcpy( &cg_pmoveSettings, &parsed, sizeof( cg_pmoveSettings ) );
}

static int CG_ValidOrder(const char *p) {
	int i;
	for (i = 0; i < numValidOrders; i++) {
		if (Q_stricmp(p, validOrders[i].order) == 0) {
			return validOrders[i].taskNum;
		}
	}
	return -1;
}
/*
=============
CG_ParseRaceInit

Resets the cached race metadata when a race_init command arrives.
=============
*/
static void CG_ParseRaceInit( void ) {
	int count = 0;

	if ( trap_Argc() > 1 ) {
		count = atoi( CG_Argv( 1 ) );
	}

	if ( count < 0 ) {
		count = 0;
	}
	if ( count > MAX_RACE_POINTS ) {
		count = MAX_RACE_POINTS;
	}

	cgs.racePointCount = count;
	cgs.raceLeaderSplitCount = 0;
	memset( cgs.racePoints, 0, sizeof( cgs.racePoints ) );
	memset( cgs.raceLeaderSplits, 0, sizeof( cgs.raceLeaderSplits ) );
	CG_RaceResetState();
}

/*
=============
CG_ParseRaceInfoCommand

Stores the latest leader split data from the race_info command.
=============
*/
static void CG_ParseRaceInfoCommand( void ) {
	int count = 0;
	int argc;
	int i;

	argc = trap_Argc();
	if ( argc > 1 ) {
		count = atoi( CG_Argv( 1 ) );
	}
	if ( count < 0 ) {
		count = 0;
	}
	if ( count > MAX_RACE_POINTS ) {
		count = MAX_RACE_POINTS;
	}

	cgs.racePointCount = count;
	cgs.raceLeaderSplitCount = 0;
	memset( cgs.raceLeaderSplits, 0, sizeof( cgs.raceLeaderSplits ) );
	for ( i = 0; i < count && ( i + 2 ) < argc; i++ ) {
		cgs.raceLeaderSplits[i] = atoi( CG_Argv( i + 2 ) );
		cgs.raceLeaderSplitCount++;
	}
}

/*
=============
CG_ParseAdminRacePoint

Updates local checkpoint metadata for admin_race_point_%i commands.
=============
*/
static void CG_ParseAdminRacePoint( const char *cmd ) {
	int index;
	cgRacePointInfo_t *info;

	if ( !cmd ) {
		return;
	}

	index = atoi( cmd + 17 );
	if ( index < 0 || index >= MAX_RACE_POINTS ) {
		return;
	}

	info = &cgs.racePoints[index];
	memset( info, 0, sizeof( *info ) );
	info->active = qtrue;
	if ( trap_Argc() > 1 ) {
		info->origin[0] = atof( CG_Argv( 1 ) );
	}
	if ( trap_Argc() > 2 ) {
		info->origin[1] = atof( CG_Argv( 2 ) );
	}
	if ( trap_Argc() > 3 ) {
		info->origin[2] = atof( CG_Argv( 3 ) );
	}
	if ( trap_Argc() > 4 ) {
		const char *target = CG_Argv( 4 );
		if ( target && Q_stricmp( target, "-" ) ) {
			Q_strncpyz( info->target, target, sizeof( info->target ) );
		}
	}
	if ( trap_Argc() > 5 ) {
		const char *targetName = CG_Argv( 5 );
		if ( targetName && Q_stricmp( targetName, "-" ) ) {
			Q_strncpyz( info->targetname, targetName, sizeof( info->targetname ) );
		}
	}

	if ( index >= cgs.racePointCount ) {
		cgs.racePointCount = index + 1;
	}
}

/*
=================
CG_ParseScores

=================
*/
static void CG_ParseScores( void ) {
	int		i, powerups;

	cg.numScores = atoi( CG_Argv( 1 ) );
	if ( cg.numScores > MAX_CLIENTS ) {
		cg.numScores = MAX_CLIENTS;
	}

	cg.teamScores[0] = atoi( CG_Argv( 2 ) );
	cg.teamScores[1] = atoi( CG_Argv( 3 ) );

	memset( cg.scores, 0, sizeof( cg.scores ) );
	for ( i = 0 ; i < cg.numScores ; i++ ) {
		//
		cg.scores[i].client = atoi( CG_Argv( i * 14 + 4 ) );
		cg.scores[i].score = atoi( CG_Argv( i * 14 + 5 ) );
		cg.scores[i].ping = atoi( CG_Argv( i * 14 + 6 ) );
		cg.scores[i].time = atoi( CG_Argv( i * 14 + 7 ) );
		cg.scores[i].scoreFlags = atoi( CG_Argv( i * 14 + 8 ) );
		powerups = atoi( CG_Argv( i * 14 + 9 ) );
		cg.scores[i].accuracy = atoi(CG_Argv(i * 14 + 10));
		cg.scores[i].impressiveCount = atoi(CG_Argv(i * 14 + 11));
		cg.scores[i].excellentCount = atoi(CG_Argv(i * 14 + 12));
		cg.scores[i].guantletCount = atoi(CG_Argv(i * 14 + 13));
		cg.scores[i].defendCount = atoi(CG_Argv(i * 14 + 14));
		cg.scores[i].assistCount = atoi(CG_Argv(i * 14 + 15));
		cg.scores[i].perfect = atoi(CG_Argv(i * 14 + 16));
		cg.scores[i].captures = atoi(CG_Argv(i * 14 + 17));

		if ( cg.scores[i].client < 0 || cg.scores[i].client >= MAX_CLIENTS ) {
			cg.scores[i].client = 0;
		}
		cgs.clientinfo[ cg.scores[i].client ].score = cg.scores[i].score;
		cgs.clientinfo[ cg.scores[i].client ].powerups = powerups;

		cg.scores[i].team = cgs.clientinfo[cg.scores[i].client].team;
	}
	CG_SetScoreSelection(NULL);

}

/*
=================
CG_ParseTeamInfo

=================
*/
static void CG_ParseTeamInfo( void ) {
	int		i;
	int		client;

	numSortedTeamPlayers = atoi( CG_Argv( 1 ) );

	for ( i = 0 ; i < numSortedTeamPlayers ; i++ ) {
		client = atoi( CG_Argv( i * 6 + 2 ) );

		sortedTeamPlayers[i] = client;

		cgs.clientinfo[ client ].location = atoi( CG_Argv( i * 6 + 3 ) );
		cgs.clientinfo[ client ].health = atoi( CG_Argv( i * 6 + 4 ) );
		cgs.clientinfo[ client ].armor = atoi( CG_Argv( i * 6 + 5 ) );
		cgs.clientinfo[ client ].curWeapon = atoi( CG_Argv( i * 6 + 6 ) );
		cgs.clientinfo[ client ].powerups = atoi( CG_Argv( i * 6 + 7 ) );
	}
}


/*
=============
CG_SetTeamNameCvar

Synchronizes cached team labels and archived client cvars with incoming
serverinfo updates while allowing manual edits between updates.
=============
*/
static void CG_SetTeamNameCvar( const char *cvarName, const char *serverValue, const char *defaultValue, char *cachedValue, int cachedValueSize ) {
	const char	*resolvedValue;
	char		currentValue[MAX_CVAR_VALUE_STRING];

	if ( serverValue && serverValue[0] ) {
		resolvedValue = serverValue;
	} else if ( defaultValue ) {
		resolvedValue = defaultValue;
	} else {
		resolvedValue = "";
	}

	if ( cachedValue && cachedValueSize > 0 ) {
		Q_strncpyz( cachedValue, resolvedValue, cachedValueSize );
	}

	trap_Cvar_VariableStringBuffer( cvarName, currentValue, sizeof( currentValue ) );
	if ( Q_stricmp( currentValue, resolvedValue ) ) {
		trap_Cvar_Set( cvarName, resolvedValue );
	}
}


/*
================
CG_ParseServerinfo

This is called explicitly when the gamestate is first received,
and whenever the server updates any serverinfo flagged cvars
================
*/
void CG_ParseServerinfo( void ) {
	const char	*info;
	const char	*gametypeValue;
	char	*mapname;
	char	oldModelOverride[MAX_QPATH];
	char	oldHeadOverride[MAX_QPATH];
	const char	*modelOverride;
	const char	*headOverride;
	const char	*voteFlagsValue;
	qboolean	mapVotingDisabled;
	const char	*serverLoadout;
	const char	*voteFlagsString;
	int		voteFlags;

	info = CG_ConfigString( CS_SERVERINFO );
	Q_strncpyz( oldModelOverride, cgs.playermodelOverride, sizeof( oldModelOverride ) );
	Q_strncpyz( oldHeadOverride, cgs.playerheadmodelOverride, sizeof( oldHeadOverride ) );
	gametypeValue = Info_ValueForKey( info, "g_gametype" );
	cgs.gametype = atoi( gametypeValue );
	trap_Cvar_Set( "cg_gametype", gametypeValue );
	trap_Cvar_Set("g_gametype", va("%i", cgs.gametype));
	cgs.dmflags = atoi( Info_ValueForKey( info, "dmflags" ) );
	cgs.teamflags = atoi( Info_ValueForKey( info, "teamflags" ) );
	cgs.fraglimit = atoi( Info_ValueForKey( info, "fraglimit" ) );
	cgs.capturelimit = atoi( Info_ValueForKey( info, "capturelimit" ) );
	cgs.timelimit = atoi( Info_ValueForKey( info, "timelimit" ) );
	voteFlagsValue = Info_ValueForKey( info, "g_voteFlags" );
	cgs.voteFlags = atoi( voteFlagsValue );
	mapVotingDisabled = ( cgs.voteFlags & ( CG_VOTEFLAG_NO_MAP | CG_VOTEFLAG_NO_NEXTMAP ) ) ? qtrue : qfalse;
	trap_Cvar_Set( "ui_mapVotingDisabled", mapVotingDisabled ? "1" : "0" );

	/*
	 * g_voteFlags bits used by map and end-match voting:
	 *	0x0001 (CG_VOTEFLAG_NO_MAP)		- blocks manual callvote map commands.
	 *	0x0004 (CG_VOTEFLAG_NO_NEXTMAP)	- blocks manual callvote nextmap commands.
	 *	0x0800 (CG_VOTEFLAG_NO_ENDVOTE)	- disables the automatic end-match vote menu.
	 *
	 * During overtime Quake Live also suppresses end-match voting regardless of
	 * the configured flags, so mirror that behavior for the UI toggle here.
	 */
	{
		qboolean		overtimeActive;
		qboolean		endMapVotingDisabled;

		overtimeActive = cgs.matchOvertimeActive ? qtrue : qfalse;
		endMapVotingDisabled = ( ( cgs.voteFlags & CG_VOTEFLAG_NO_ENDVOTE ) != 0 ) || overtimeActive;
		trap_Cvar_Set( "ui_endMapVotingDisabled", endMapVotingDisabled ? "1" : "0" );
	}
	cgs.maxclients = atoi( Info_ValueForKey( info, "sv_maxclients" ) );
  
	serverLoadout = Info_ValueForKey( info, "loadout" );
	if ( !serverLoadout || !serverLoadout[0] ) {
		serverLoadout = Info_ValueForKey( info, "g_loadout" );
	}
	if ( !serverLoadout ) {
		serverLoadout = "";
	}
	Q_strncpyz( cgs.loadout, serverLoadout, sizeof( cgs.loadout ) );
	trap_Cvar_Set( "cg_loadout", cgs.loadout );
  
	{
		const char	*armorTieredValue;

		armorTieredValue = Info_ValueForKey( info, "g_armorTiered" );
		if ( !armorTieredValue[0] ) {
			armorTieredValue = "0";
		}

		cg.armorTieredEnabled = (qboolean)( atoi( armorTieredValue ) != 0 );
		trap_Cvar_Set( "cg_armorTiered", armorTieredValue );
	}
  
	mapname = Info_ValueForKey( info, "mapname" );
	Com_sprintf( cgs.mapname, sizeof( cgs.mapname ), "maps/%s.bsp", mapname );
CG_SetTeamNameCvar( "g_redteam", Info_ValueForKey( info, "g_redTeam" ), DEFAULT_REDTEAM_NAME, cgs.redTeam, sizeof( cgs.redTeam ) );
CG_SetTeamNameCvar( "g_blueteam", Info_ValueForKey( info, "g_blueTeam" ), DEFAULT_BLUETEAM_NAME, cgs.blueTeam, sizeof( cgs.blueTeam ) );
	modelOverride = Info_ValueForKey( info, "g_playermodelOverride" );
	headOverride = Info_ValueForKey( info, "g_playerheadmodelOverride" );
	Q_strncpyz( cgs.playermodelOverride, modelOverride, sizeof( cgs.playermodelOverride ) );
	Q_strncpyz( cgs.playerheadmodelOverride, headOverride, sizeof( cgs.playerheadmodelOverride ) );
	if ( Q_stricmp( oldModelOverride, cgs.playermodelOverride ) || Q_stricmp( oldHeadOverride, cgs.playerheadmodelOverride ) ) {
		CG_ApplyModelOverrides();
	}

	voteFlagsString = Info_ValueForKey( info, "g_voteFlags" );
	voteFlags = atoi( voteFlagsString );
	if ( voteFlags & VF_NO_GAMETYPE ) {
		trap_Cvar_Set( "ui_gameTypeVotingDisabled", "1" );
	} else {
		trap_Cvar_Set( "ui_gameTypeVotingDisabled", "0" );
	}
}

/*
==================
CG_ParseWarmup
==================
*/
static void CG_ParseWarmup( void ) {
	const char	*info;
	int			warmup;

	info = CG_ConfigString( CS_WARMUP );

	warmup = atoi( info );
	cg.warmupCount = -1;

	if ( warmup == 0 && cg.warmup ) {

	} else if ( warmup > 0 && cg.warmup <= 0 ) {
		if ( cgs.gametype >= GT_CTF ) {
			trap_S_StartLocalSound( cgs.media.countPrepareTeamSound, CHAN_ANNOUNCER );
		} else
		{
			trap_S_StartLocalSound( cgs.media.countPrepareSound, CHAN_ANNOUNCER );
		}
	}

	cg.warmup = warmup;
	trap_Cvar_Set( "ui_warmup", va( "%i", cg.warmup ) );
}

/*
=============
CG_InfoIntForMatchKey

Extracts an integer value from the supplied match-state info string.
=============
*/
static int CG_InfoIntForMatchKey( const char *info, const char *key, int defaultValue ) {
	const char *value;

	if ( !info || !key ) {
		return defaultValue;
	}

	value = Info_ValueForKey( info, key );
	if ( !value || !*value ) {
		return defaultValue;
	}

	return atoi( value );
}

/*
=============
CG_ResetMatchStateFields

Clears cached match-state variables before parsing.
=============
*/
static void CG_ResetMatchStateFields( void ) {
	int i;

	cgs.matchOvertimeActive = qfalse;
	cgs.matchOvertimeStartTime = 0;
	cgs.matchOvertimeEndTime = 0;
	cgs.matchOvertimeCount = 0;
	cgs.matchTimeoutActive = qfalse;
	cgs.matchTimeoutTeam = TEAM_FREE;
	cgs.matchTimeoutExpireTime = 0;
	cgs.matchTimeoutOwner = -1;
	for ( i = 0; i < TEAM_NUM_TEAMS; i++ ) {
		cgs.matchTimeoutRemaining[i] = 0;
		cgs.matchTeamCount[i] = 0;
		cgs.matchTeamRespawnRatio[i] = 0;
	}
	cgs.matchTimeoutLengthSeconds = 0;
	cgs.matchTimeoutCountPerTeam = 0;
	cgs.matchOvertimeLengthSeconds = 0;
	cgs.matchSuddenDeathRespawnsEnabled = qfalse;
	cgs.matchSuddenDeathStartSeconds = 0;
	cgs.matchSuddenDeathTickSeconds = 0;
	cgs.matchSuddenDeathMaxSeconds = 0;
	cgs.matchSuddenDeathIncrementSeconds = 0;
	cgs.matchSuddenDeathPrintAnnouncements = qfalse;
	cgs.matchSuddenDeathSpawnDelayActive = qfalse;
	cgs.matchRoundTransitionTime = 0;
	cgs.matchRoundNumber = 0;
	cgs.matchRoundTurn = 0;
	cgs.matchRoundState = 0;
	cgs.matchAutoShuffleArmed = qfalse;
	cgs.matchAutoShuffleSecondsRemaining = 0;
}



/*
=============
CG_ParseMatchFactoryConfig

Extracts the server-provided match factory configuration fields from the payload.
=============
*/
static void CG_ParseMatchFactoryConfig( const char *info ) {
	if ( !info || !*info ) {
		return;
	}

	cgs.matchOvertimeLengthSeconds = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_OVERTIME_LENGTH, 0 );
	cgs.matchTimeoutLengthSeconds = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_LENGTH, 0 );
	cgs.matchTimeoutCountPerTeam = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_COUNT, 0 );
	cgs.matchSuddenDeathRespawnsEnabled = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_RESPAWNS, 0 ) ? qtrue : qfalse;
	cgs.matchSuddenDeathStartSeconds = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_START, 0 );
	cgs.matchSuddenDeathTickSeconds = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_TICK, 0 );
	cgs.matchSuddenDeathMaxSeconds = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_MAX, 0 );
	cgs.matchSuddenDeathIncrementSeconds = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_INCREMENT, 0 );
	cgs.matchSuddenDeathPrintAnnouncements = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_PRINT, 0 ) ? qtrue : qfalse;
	cgs.matchSuddenDeathSpawnDelayActive = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SUDDEN_DELAY, 0 ) ? qtrue : qfalse;
}

/*
=============
CG_ParseMatchState

Parses the match state configstring and updates client state.
=============
*/
static void CG_ParseMatchState( void ) {
	const char *info;
	int timeoutRemaining;
	int value;

	CG_ResetMatchStateFields();

	info = CG_ConfigString( CS_MATCH_STATE );
	if ( !info || !*info ) {
		return;
	}

	cgs.matchRoundTransitionTime = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIME, 0 );
	cgs.matchRoundNumber = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_ROUND, 0 );
	cgs.matchRoundTurn = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TURN, 0 );
	cgs.matchRoundState = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_STATE, 0 );
	cgs.matchOvertimeActive = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_OVERTIME_ACTIVE, 0 ) ? qtrue : qfalse;
	cgs.matchOvertimeStartTime = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_OVERTIME_START, 0 );
	cgs.matchOvertimeEndTime = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_OVERTIME_END, 0 );
	cgs.matchOvertimeCount = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_OVERTIME_COUNT, 0 );
	cgs.matchTimeoutActive = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_ACTIVE, 0 ) ? qtrue : qfalse;
	cgs.matchTimeoutTeam = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_TEAM, TEAM_FREE );
	cgs.matchTimeoutExpireTime = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_EXPIRE, 0 );
	cgs.matchTimeoutOwner = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_OWNER, -1 );
	timeoutRemaining = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_RED, 0 );
	if ( timeoutRemaining < 0 ) {
		timeoutRemaining = 0;
	}
	cgs.matchTimeoutRemaining[TEAM_RED] = timeoutRemaining;
	timeoutRemaining = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIMEOUT_BLUE, 0 );
	if ( timeoutRemaining < 0 ) {
		timeoutRemaining = 0;
	}
	cgs.matchTimeoutRemaining[TEAM_BLUE] = timeoutRemaining;

	cgs.matchTeamCount[TEAM_RED] = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TEAM_RED_COUNT, 0 );
	cgs.matchTeamCount[TEAM_BLUE] = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TEAM_BLUE_COUNT, 0 );

	value = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_RESPAWN_RED, 0 );
	if ( value < 0 ) {
		value = 0;
	}
	cgs.matchTeamRespawnRatio[TEAM_RED] = value;
	value = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_RESPAWN_BLUE, 0 );
	if ( value < 0 ) {
		value = 0;
	}
	cgs.matchTeamRespawnRatio[TEAM_BLUE] = value;

	cgs.matchAutoShuffleArmed = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SHUFFLE_ARMED, 0 ) ? qtrue : qfalse;
	cgs.matchAutoShuffleSecondsRemaining = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_SHUFFLE_REMAINING, 0 );
	if ( cgs.matchAutoShuffleSecondsRemaining < 0 ) {
		cgs.matchAutoShuffleSecondsRemaining = 0;
	}

	CG_ParseMatchFactoryConfig( info );
}

/*
=============
CG_RequestForcedAtmosphere

Caches the forced atmosphere token and notifies the player when it changes.
=============
*/
static void CG_RequestForcedAtmosphere( const char *effect ) {
	if ( !effect ) {
		effect = "";
	}

	if ( !effect[0] ) {
		if ( cgs.forcedAtmosphere[0] ) {
			cgs.forcedAtmosphere[0] = '\0';
			CG_Printf( "Server cleared forced atmosphere overrides.\n" );
		}
		return;
	}

	if ( !Q_stricmp( effect, cgs.forcedAtmosphere ) ) {
		return;
	}

	Q_strncpyz( cgs.forcedAtmosphere, effect, sizeof( cgs.forcedAtmosphere ) );
	CG_Printf( "Server forced atmosphere: %s\n", cgs.forcedAtmosphere );
}

/*
=============
CG_ParseForcedCosmetics

Parses the forced cosmetics configstring and updates local client state.
=============
*/
static void CG_ParseForcedCosmetics( void ) {
	const char		*info;
	const char		*value;
	qboolean	forceScoreboard;
	qboolean	forceHud;
	qboolean	forceDamage;
	qboolean	previousScoreboard;
	qboolean	previousHud;
	qboolean	previousDamage;

	previousScoreboard = cgs.forceSmallScoreboardMessage;
	previousHud = cgs.forceHudHints;
	previousDamage = cgs.forceDmgThroughSurface;
	forceScoreboard = qfalse;
	forceHud = qfalse;
	forceDamage = qfalse;

	info = CG_ConfigString( CS_FORCED_COSMETICS );
	if ( info && *info ) {
		value = Info_ValueForKey( info, "sb" );
		if ( value && *value ) {
			forceScoreboard = atoi( value ) ? qtrue : qfalse;
		}

		value = Info_ValueForKey( info, "hud" );
		if ( value && *value ) {
			forceHud = atoi( value ) ? qtrue : qfalse;
		}

		value = Info_ValueForKey( info, "dmg" );
		if ( value && *value ) {
			forceDamage = atoi( value ) ? qtrue : qfalse;
		}

		value = Info_ValueForKey( info, "atm" );
		if ( value ) {
			CG_RequestForcedAtmosphere( value );
		}
	} else {
		CG_RequestForcedAtmosphere( "" );
	}

	cgs.forceSmallScoreboardMessage = forceScoreboard;
	cgs.forceHudHints = forceHud;
	cgs.forceDmgThroughSurface = forceDamage;

	if ( forceScoreboard && !previousScoreboard ) {
		CG_CenterPrint( "Server enforced the compact scoreboard message.", SCREEN_HEIGHT * 0.30f, SMALLCHAR_WIDTH );
	} else if ( !forceScoreboard && previousScoreboard ) {
		CG_CenterPrint( "Server restored your scoreboard message preference.", SCREEN_HEIGHT * 0.30f, SMALLCHAR_WIDTH );
	}

	if ( forceHud && !previousHud ) {
		CG_Printf( "Server forced HUD training widgets.\n" );
	} else if ( !forceHud && previousHud ) {
		CG_Printf( "Server cleared forced HUD training widgets.\n" );
	}

	if ( forceDamage && !previousDamage ) {
		CG_Printf( "Server forced damage through surfaces.\n" );
	} else if ( !forceDamage && previousDamage ) {
		CG_Printf( "Server restored default surface damage rules.\n" );
	}
}

/*
================
CG_SetConfigValues

Called on load to set the initial values from configure strings
================
*/

/*
==================
CG_ParseFactoryMetadata

Refreshes the cached factory metadata strings from the latest configstrings.
==================
*/
static void CG_ParseFactoryMetadata( void ) {
	const char *info;

	info = CG_ConfigString( CS_FACTORY_TITLE );
	if ( info && *info ) {
		Q_strncpyz( cgs.factoryTitle, info, sizeof( cgs.factoryTitle ) );
	} else {
		cgs.factoryTitle[0] = '\0';
	}

	info = CG_ConfigString( CS_FACTORY_FLAGS );
	if ( info && *info ) {
		cgs.factoryFlags = (unsigned int)atoi( info );
	} else {
		cgs.factoryFlags = 0u;
	}

	info = CG_ConfigString( CS_SPAWN_HINTS );
	if ( info && *info ) {
		Q_strncpyz( cgs.factorySpawnHints, info, sizeof( cgs.factorySpawnHints ) );
	} else {
		cgs.factorySpawnHints[0] = '\0';
}
}

/*
=============
CG_SetTeamNameFromConfigString

Caches the latest team name advertised in a configstring, clearing stale values when empty.
=============
*/
static void CG_SetTeamNameFromConfigString( team_t team, const char *configstring ) {
	char	*target;
	int		targetSize;

	target = NULL;
	targetSize = 0;

	switch ( team ) {
	case TEAM_RED:
		target = cgs.redTeamName;
		targetSize = (int)sizeof( cgs.redTeamName );
		break;
	case TEAM_BLUE:
		target = cgs.blueTeamName;
		targetSize = (int)sizeof( cgs.blueTeamName );
		break;
	default:
		return;
	}

	if ( configstring && configstring[0] ) {
		Q_strncpyz( target, configstring, targetSize );
	} else {
		target[0] = '\0';
	}
}

void CG_SetConfigValues( void ) {
	const char *s;

	cgs.scores1 = atoi( CG_ConfigString( CS_SCORES1 ) );
	cgs.scores2 = atoi( CG_ConfigString( CS_SCORES2 ) );
	cgs.levelStartTime = atoi( CG_ConfigString( CS_LEVEL_START_TIME ) );
	CG_SetTeamNameFromConfigString( TEAM_RED, CG_ConfigString( CS_RED_TEAM_NAME ) );
	CG_SetTeamNameFromConfigString( TEAM_BLUE, CG_ConfigString( CS_BLUE_TEAM_NAME ) );
	if( cgs.gametype == GT_CTF ) {
		s = CG_ConfigString( CS_FLAGSTATUS );
		cgs.redflag = s[0] - '0';
		cgs.blueflag = s[1] - '0';
	}
	else if( cgs.gametype == GT_1FCTF ) {
		s = CG_ConfigString( CS_FLAGSTATUS );
		cgs.flagStatus = s[0] - '0';
	}
	cg.warmup = atoi( CG_ConfigString( CS_WARMUP ) );
	CG_ParseMatchState();
	CG_ParseForcedCosmetics();
	CG_ParseFactoryMetadata();
	CG_ParsePmoveConfigString( CG_ConfigString( CS_PMOVE_SETTINGS ) );
	CG_ParseRaceInfoString( CG_ConfigString( CS_RACE_INFO ) );
	CG_ParseRaceStatusString( CG_ConfigString( CS_RACE_STATUS ) );
}
/*
=====================
CG_ShaderStateChanged
=====================
*/
void CG_ShaderStateChanged(void) {
	char originalShader[MAX_QPATH];
	char newShader[MAX_QPATH];
	char timeOffset[16];
	const char *o;
	char *n,*t;

	o = CG_ConfigString( CS_SHADERSTATE );
	while (o && *o) {
		n = strstr(o, "=");
		if (n && *n) {
			strncpy(originalShader, o, n-o);
			originalShader[n-o] = 0;
			n++;
			t = strstr(n, ":");
			if (t && *t) {
				strncpy(newShader, n, t-n);
				newShader[t-n] = 0;
			} else {
				break;
			}
			t++;
			o = strstr(t, "@");
			if (o) {
				strncpy(timeOffset, t, o-t);
				timeOffset[o-t] = 0;
				o++;
				trap_R_RemapShader( originalShader, newShader, timeOffset );
			}
		} else {
			break;
		}
	}
}

/*
================
CG_ConfigStringModified

================
*/
static void CG_ConfigStringModified( void ) {
	const char	*str;
	int		num;

	num = atoi( CG_Argv( 1 ) );

	// get the gamestate from the client system, which will have the
	// new configstring already integrated
	trap_GetGameState( &cgs.gameState );

	// look up the individual string that was modified
	str = CG_ConfigString( num );

	// do something with it if necessary
	if ( num == CS_MUSIC ) {
		CG_StartMusic();
	} else if ( num == CS_SERVERINFO ) {
		CG_ParseServerinfo();
	} else if ( num == CS_WARMUP ) {
		CG_ParseWarmup();
	} else if ( num == CS_MATCH_STATE ) {
		CG_ParseMatchState();
	} else if ( num == CS_SCORES1 ) {
		cgs.scores1 = atoi( str );
	} else if ( num == CS_SCORES2 ) {
		cgs.scores2 = atoi( str );
	} else if ( num == CS_RED_TEAM_NAME ) {
		CG_SetTeamNameFromConfigString( TEAM_RED, str );
	} else if ( num == CS_BLUE_TEAM_NAME ) {
		CG_SetTeamNameFromConfigString( TEAM_BLUE, str );
	} else if ( num == CS_LEVEL_START_TIME ) {
		cgs.levelStartTime = atoi( str );
	} else if ( num == CS_FACTORY_TITLE || num == CS_FACTORY_FLAGS || num == CS_SPAWN_HINTS ) {
		CG_ParseFactoryMetadata();
	} else if ( num == CS_FORCED_COSMETICS ) {
		CG_ParseForcedCosmetics();
	} else if ( num == CS_RACE_INFO ) {
		CG_ParseRaceInfoString( str );
	} else if ( num == CS_RACE_STATUS ) {
		CG_ParseRaceStatusString( str );
	} else if ( num == CS_VOTE_TIME ) {
		cgs.voteTime = atoi( str );
		trap_Cvar_Set( "ui_voteactive", cgs.voteTime ? "1" : "0" );
		cgs.voteModified = qtrue;
	} else if ( num == CS_VOTE_YES ) {
		cgs.voteYes = atoi( str );
		cgs.voteModified = qtrue;
	} else if ( num == CS_VOTE_NO ) {
		cgs.voteNo = atoi( str );
		cgs.voteModified = qtrue;
	} else if ( num == CS_VOTE_STRING ) {
		Q_strncpyz( cgs.voteString, str, sizeof( cgs.voteString ) );
		trap_S_StartLocalSound( cgs.media.voteNow, CHAN_ANNOUNCER );
	} else if ( num >= CS_TEAMVOTE_TIME && num <= CS_TEAMVOTE_TIME + 1) {
		cgs.teamVoteTime[num-CS_TEAMVOTE_TIME] = atoi( str );
		cgs.teamVoteModified[num-CS_TEAMVOTE_TIME] = qtrue;
	} else if ( num >= CS_TEAMVOTE_YES && num <= CS_TEAMVOTE_YES + 1) {
		cgs.teamVoteYes[num-CS_TEAMVOTE_YES] = atoi( str );
		cgs.teamVoteModified[num-CS_TEAMVOTE_YES] = qtrue;
	} else if ( num >= CS_TEAMVOTE_NO && num <= CS_TEAMVOTE_NO + 1) {
		cgs.teamVoteNo[num-CS_TEAMVOTE_NO] = atoi( str );
		cgs.teamVoteModified[num-CS_TEAMVOTE_NO] = qtrue;
	} else if ( num >= CS_TEAMVOTE_STRING && num <= CS_TEAMVOTE_STRING + 1) {
		Q_strncpyz( cgs.teamVoteString[num-CS_TEAMVOTE_STRING], str, sizeof( cgs.teamVoteString ) );
		trap_S_StartLocalSound( cgs.media.voteNow, CHAN_ANNOUNCER );
	} else if ( num == CS_INTERMISSION ) {
		cg.intermissionStarted = atoi( str );
	} else if ( num >= CS_MODELS && num < CS_MODELS+MAX_MODELS ) {
		cgs.gameModels[ num-CS_MODELS ] = trap_R_RegisterModel( str );
	} else if ( num >= CS_SOUNDS && num < CS_SOUNDS+MAX_MODELS ) {
		if ( str[0] != '*' ) {	// player specific sounds don't register here
			cgs.gameSounds[ num-CS_SOUNDS] = trap_S_RegisterSound( str, qfalse );
		}
} else if ( num >= CS_PLAYERS && num < CS_PLAYERS+MAX_CLIENTS ) {
CG_NewClientInfo( num - CS_PLAYERS );
CG_BuildSpectatorString();
} else if ( num == CS_FLAGSTATUS ) {
if( cgs.gametype == GT_CTF ) {
// format is rb where its red/blue, 0 is at base, 1 is taken, 2 is dropped
cgs.redflag = str[0] - '0';
cgs.blueflag = str[1] - '0';
}
else if( cgs.gametype == GT_1FCTF ) {
cgs.flagStatus = str[0] - '0';
}
}
else if ( num == CS_SHADERSTATE ) {
CG_ShaderStateChanged();
} else if ( num == CS_PMOVE_SETTINGS ) {
CG_ParsePmoveConfigString( str );
}

}


/*
=======================
CG_AddToTeamChat

=======================
*/
static void CG_AddToTeamChat( const char *str ) {
	int len;
	char *p, *ls;
	int lastcolor;
	int chatHeight;

	chatHeight = CG_GetChatHistoryLength();

	if ( chatHeight <= 0 || cg_teamChatTime.integer <= 0 ) {
		// team chat disabled, dump into normal chat
		cgs.teamChatPos = cgs.teamLastChatPos = 0;
		return;
	}

	if ( cg_teamChatBeep.integer && cgs.media.talkSound ) {
		trap_S_StartLocalSound( cgs.media.talkSound, CHAN_LOCAL_SOUND );
	}

	len = 0;

	p = cgs.teamChatMsgs[cgs.teamChatPos % chatHeight];
	*p = 0;

	lastcolor = '7';

	ls = NULL;
	while (*str) {
		if (len > TEAMCHAT_WIDTH - 1) {
			if (ls) {
				str -= (p - ls);
				str++;
				p -= (p - ls);
			}
			*p = 0;

			cgs.teamChatMsgTimes[cgs.teamChatPos % chatHeight] = cg.time;

			cgs.teamChatPos++;
			p = cgs.teamChatMsgs[cgs.teamChatPos % chatHeight];
			*p = 0;
			*p++ = Q_COLOR_ESCAPE;
			*p++ = lastcolor;
			len = 0;
			ls = NULL;
		}

		if ( Q_IsColorString( str ) ) {
			*p++ = *str++;
			lastcolor = *str;
			*p++ = *str++;
			continue;
		}
		if (*str == ' ') {
			ls = p;
		}
		*p++ = *str++;
		len++;
	}
	*p = 0;

	cgs.teamChatMsgTimes[cgs.teamChatPos % chatHeight] = cg.time;
	cgs.teamChatPos++;

	if (cgs.teamChatPos - cgs.teamLastChatPos > chatHeight)
		cgs.teamLastChatPos = cgs.teamChatPos - chatHeight;
	}

/*
===============
CG_MapRestart

The server has issued a map_restart, so the next snapshot
is completely new and should not be interpolated to.

A tournement restart will clear everything, but doesn't
require a reload of all the media
===============
*/
static void CG_MapRestart( void ) {
	if ( cg_showmiss.integer ) {
		CG_Printf( "CG_MapRestart\n" );
	}

	CG_InitLocalEntities();
	CG_InitMarkPolys();
	CG_ClearParticles ();

	// make sure the "3 frags left" warnings play again
	cg.fraglimitWarnings = 0;

	cg.timelimitWarnings = 0;

	cg.intermissionStarted = qfalse;

	cgs.voteTime = 0;
	trap_Cvar_Set( "ui_voteactive", "0" );

	cg.mapRestart = qtrue;

	CG_StartMusic();

	trap_S_ClearLoopingSounds(qtrue);

	// we really should clear more parts of cg here and stop sounds

	// play the "fight" sound if this is a restart without warmup
	if ( cg.warmup == 0 /* && cgs.gametype == GT_TOURNAMENT */) {
		trap_S_StartLocalSound( cgs.media.countFightSound, CHAN_ANNOUNCER );
		CG_CenterPrint( "FIGHT!", 120, GIANTCHAR_WIDTH*2 );
	}
	if (cg_singlePlayerActive.integer) {
		trap_Cvar_Set("ui_matchStartTime", va("%i", cg.time));
		if (cg_recordSPDemo.integer && cg_recordSPDemoName.string && *cg_recordSPDemoName.string) {
			trap_SendConsoleCommand(va("set g_synchronousclients 1 ; record %s \n", cg_recordSPDemoName.string));
		}
	}
	trap_Cvar_Set("cg_thirdPerson", "0");
}

#define MAX_VOICEFILESIZE	16384
#define MAX_VOICEFILES		8
#define MAX_VOICECHATS		64
#define MAX_VOICESOUNDS		64
#define MAX_CHATSIZE		64
#define MAX_HEADMODELS		64

typedef struct voiceChat_s
{
	char id[64];
	int numSounds;
	sfxHandle_t sounds[MAX_VOICESOUNDS];
	char chats[MAX_VOICESOUNDS][MAX_CHATSIZE];
} voiceChat_t;

typedef struct voiceChatList_s
{
	char name[64];
	int gender;
	int numVoiceChats;
	voiceChat_t voiceChats[MAX_VOICECHATS];
} voiceChatList_t;

typedef struct headModelVoiceChat_s
{
	char headmodel[64];
	int voiceChatNum;
} headModelVoiceChat_t;

voiceChatList_t voiceChatLists[MAX_VOICEFILES];
headModelVoiceChat_t headModelVoiceChat[MAX_HEADMODELS];

/*
=================
CG_ParseVoiceChats
=================
*/
int CG_ParseVoiceChats( const char *filename, voiceChatList_t *voiceChatList, int maxVoiceChats ) {
	int	len, i;
	fileHandle_t f;
	char buf[MAX_VOICEFILESIZE];
	char **p, *ptr;
	char *token;
	voiceChat_t *voiceChats;
	qboolean compress;
	sfxHandle_t sound;

	compress = qtrue;
	if (cg_buildScript.integer) {
		compress = qfalse;
	}

	len = trap_FS_FOpenFile( filename, &f, FS_READ );
	if ( !f ) {
		trap_Print( va( S_COLOR_RED "voice chat file not found: %s\n", filename ) );
		return qfalse;
	}
	if ( len >= MAX_VOICEFILESIZE ) {
		trap_Print( va( S_COLOR_RED "voice chat file too large: %s is %i, max allowed is %i", filename, len, MAX_VOICEFILESIZE ) );
		trap_FS_FCloseFile( f );
		return qfalse;
	}

	trap_FS_Read( buf, len, f );
	buf[len] = 0;
	trap_FS_FCloseFile( f );

	ptr = buf;
	p = &ptr;

	Com_sprintf(voiceChatList->name, sizeof(voiceChatList->name), "%s", filename);
	voiceChats = voiceChatList->voiceChats;
	for ( i = 0; i < maxVoiceChats; i++ ) {
		voiceChats[i].id[0] = 0;
	}
	token = COM_ParseExt(p, qtrue);
	if (!token || token[0] == 0) {
		return qtrue;
	}
	if (!Q_stricmp(token, "female")) {
		voiceChatList->gender = GENDER_FEMALE;
	}
	else if (!Q_stricmp(token, "male")) {
		voiceChatList->gender = GENDER_MALE;
	}
	else if (!Q_stricmp(token, "neuter")) {
		voiceChatList->gender = GENDER_NEUTER;
	}
	else {
		trap_Print( va( S_COLOR_RED "expected gender not found in voice chat file: %s\n", filename ) );
		return qfalse;
	}

	voiceChatList->numVoiceChats = 0;
	while ( 1 ) {
		token = COM_ParseExt(p, qtrue);
		if (!token || token[0] == 0) {
			return qtrue;
		}
		Com_sprintf(voiceChats[voiceChatList->numVoiceChats].id, sizeof( voiceChats[voiceChatList->numVoiceChats].id ), "%s", token);
		token = COM_ParseExt(p, qtrue);
		if (Q_stricmp(token, "{")) {
			trap_Print( va( S_COLOR_RED "expected { found %s in voice chat file: %s\n", token, filename ) );
			return qfalse;
		}
		voiceChats[voiceChatList->numVoiceChats].numSounds = 0;
		while(1) {
			token = COM_ParseExt(p, qtrue);
			if (!token || token[0] == 0) {
				return qtrue;
			}
			if (!Q_stricmp(token, "}"))
				break;
			sound = trap_S_RegisterSound( token, compress );
			voiceChats[voiceChatList->numVoiceChats].sounds[voiceChats[voiceChatList->numVoiceChats].numSounds] = sound;
			token = COM_ParseExt(p, qtrue);
			if (!token || token[0] == 0) {
				return qtrue;
			}
			Com_sprintf(voiceChats[voiceChatList->numVoiceChats].chats[
							voiceChats[voiceChatList->numVoiceChats].numSounds], MAX_CHATSIZE, "%s", token);
			if (sound)
				voiceChats[voiceChatList->numVoiceChats].numSounds++;
			if (voiceChats[voiceChatList->numVoiceChats].numSounds >= MAX_VOICESOUNDS)
				break;
		}
		voiceChatList->numVoiceChats++;
		if (voiceChatList->numVoiceChats >= maxVoiceChats)
			return qtrue;
	}
	return qtrue;
}

/*
=================
CG_LoadVoiceChats
=================
*/
void CG_LoadVoiceChats( void ) {
	int size;

	size = trap_MemoryRemaining();
	CG_ParseVoiceChats( "scripts/female1.voice", &voiceChatLists[0], MAX_VOICECHATS );
	CG_ParseVoiceChats( "scripts/female2.voice", &voiceChatLists[1], MAX_VOICECHATS );
	CG_ParseVoiceChats( "scripts/female3.voice", &voiceChatLists[2], MAX_VOICECHATS );
	CG_ParseVoiceChats( "scripts/male1.voice", &voiceChatLists[3], MAX_VOICECHATS );
	CG_ParseVoiceChats( "scripts/male2.voice", &voiceChatLists[4], MAX_VOICECHATS );
	CG_ParseVoiceChats( "scripts/male3.voice", &voiceChatLists[5], MAX_VOICECHATS );
	CG_ParseVoiceChats( "scripts/male4.voice", &voiceChatLists[6], MAX_VOICECHATS );
	CG_ParseVoiceChats( "scripts/male5.voice", &voiceChatLists[7], MAX_VOICECHATS );
	CG_Printf("voice chat memory size = %d\n", size - trap_MemoryRemaining());
}

/*
=================
CG_HeadModelVoiceChats
=================
*/
int CG_HeadModelVoiceChats( char *filename ) {
	int	len, i;
	fileHandle_t f;
	char buf[MAX_VOICEFILESIZE];
	char **p, *ptr;
	char *token;

	len = trap_FS_FOpenFile( filename, &f, FS_READ );
	if ( !f ) {
		//trap_Print( va( "voice chat file not found: %s\n", filename ) );
		return -1;
	}
	if ( len >= MAX_VOICEFILESIZE ) {
		trap_Print( va( S_COLOR_RED "voice chat file too large: %s is %i, max allowed is %i", filename, len, MAX_VOICEFILESIZE ) );
		trap_FS_FCloseFile( f );
		return -1;
	}

	trap_FS_Read( buf, len, f );
	buf[len] = 0;
	trap_FS_FCloseFile( f );

	ptr = buf;
	p = &ptr;

	token = COM_ParseExt(p, qtrue);
	if (!token || token[0] == 0) {
		return -1;
	}

	for ( i = 0; i < MAX_VOICEFILES; i++ ) {
		if ( !Q_stricmp(token, voiceChatLists[i].name) ) {
			return i;
		}
	}

	//FIXME: maybe try to load the .voice file which name is stored in token?

	return -1;
}


/*
=================
CG_GetVoiceChat
=================
*/
int CG_GetVoiceChat( voiceChatList_t *voiceChatList, const char *id, sfxHandle_t *snd, char **chat) {
	int i, rnd;

	for ( i = 0; i < voiceChatList->numVoiceChats; i++ ) {
		if ( !Q_stricmp( id, voiceChatList->voiceChats[i].id ) ) {
			rnd = random() * voiceChatList->voiceChats[i].numSounds;
			*snd = voiceChatList->voiceChats[i].sounds[rnd];
			*chat = voiceChatList->voiceChats[i].chats[rnd];
			return qtrue;
		}
	}
	return qfalse;
}

/*
=================
CG_VoiceChatListForClient
=================
*/
voiceChatList_t *CG_VoiceChatListForClient( int clientNum ) {
	clientInfo_t *ci;
	int voiceChatNum, i, j, k, gender;
	char filename[MAX_QPATH], headModelName[MAX_QPATH];

	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		clientNum = 0;
	}
	ci = &cgs.clientinfo[ clientNum ];

	for ( k = 0; k < 2; k++ ) {
		if ( k == 0 ) {
			if (ci->headModelName[0] == '*') {
				Com_sprintf( headModelName, sizeof(headModelName), "%s/%s", ci->headModelName+1, ci->headSkinName );
			}
			else {
				Com_sprintf( headModelName, sizeof(headModelName), "%s/%s", ci->headModelName, ci->headSkinName );
			}
		}
		else {
			if (ci->headModelName[0] == '*') {
				Com_sprintf( headModelName, sizeof(headModelName), "%s", ci->headModelName+1 );
			}
			else {
				Com_sprintf( headModelName, sizeof(headModelName), "%s", ci->headModelName );
			}
		}
		// find the voice file for the head model the client uses
		for ( i = 0; i < MAX_HEADMODELS; i++ ) {
			if (!Q_stricmp(headModelVoiceChat[i].headmodel, headModelName)) {
				break;
			}
		}
		if (i < MAX_HEADMODELS) {
			return &voiceChatLists[headModelVoiceChat[i].voiceChatNum];
		}
		// find a <headmodelname>.vc file
		for ( i = 0; i < MAX_HEADMODELS; i++ ) {
			if (!strlen(headModelVoiceChat[i].headmodel)) {
				Com_sprintf(filename, sizeof(filename), "scripts/%s.vc", headModelName);
				voiceChatNum = CG_HeadModelVoiceChats(filename);
				if (voiceChatNum == -1)
					break;
				Com_sprintf(headModelVoiceChat[i].headmodel, sizeof ( headModelVoiceChat[i].headmodel ),
							"%s", headModelName);
				headModelVoiceChat[i].voiceChatNum = voiceChatNum;
				return &voiceChatLists[headModelVoiceChat[i].voiceChatNum];
			}
		}
	}
	gender = ci->gender;
	for (k = 0; k < 2; k++) {
		// just pick the first with the right gender
		for ( i = 0; i < MAX_VOICEFILES; i++ ) {
			if (strlen(voiceChatLists[i].name)) {
				if (voiceChatLists[i].gender == gender) {
					// store this head model with voice chat for future reference
					for ( j = 0; j < MAX_HEADMODELS; j++ ) {
						if (!strlen(headModelVoiceChat[j].headmodel)) {
							Com_sprintf(headModelVoiceChat[j].headmodel, sizeof ( headModelVoiceChat[j].headmodel ),
									"%s", headModelName);
							headModelVoiceChat[j].voiceChatNum = i;
							break;
						}
					}
					return &voiceChatLists[i];
				}
			}
		}
		// fall back to male gender because we don't have neuter in the mission pack
		if (gender == GENDER_MALE)
			break;
		gender = GENDER_MALE;
	}
	// store this head model with voice chat for future reference
	for ( j = 0; j < MAX_HEADMODELS; j++ ) {
		if (!strlen(headModelVoiceChat[j].headmodel)) {
			Com_sprintf(headModelVoiceChat[j].headmodel, sizeof ( headModelVoiceChat[j].headmodel ),
					"%s", headModelName);
			headModelVoiceChat[j].voiceChatNum = 0;
			break;
		}
	}
	// just return the first voice chat list
	return &voiceChatLists[0];
}

#define MAX_VOICECHATBUFFER		32

typedef struct bufferedVoiceChat_s
{
	int clientNum;
	sfxHandle_t snd;
	int voiceOnly;
	char cmd[MAX_SAY_TEXT];
	char message[MAX_SAY_TEXT];
} bufferedVoiceChat_t;

bufferedVoiceChat_t voiceChatBuffer[MAX_VOICECHATBUFFER];

/*
=================
CG_PlayVoiceChat
=================
*/
void CG_PlayVoiceChat( bufferedVoiceChat_t *vchat ) {
	// if we are going into the intermission, don't start any voices
	if ( cg.intermissionStarted ) {
		return;
	}

	if ( cg_playVoiceChats.integer ) {
		trap_S_StartLocalSound( vchat->snd, CHAN_VOICE);
		if (vchat->clientNum != cg.snap->ps.clientNum) {
			int orderTask = CG_ValidOrder(vchat->cmd);
			if (orderTask > 0) {
				cgs.acceptOrderTime = cg.time + 5000;
				Q_strncpyz(cgs.acceptVoice, vchat->cmd, sizeof(cgs.acceptVoice));
				cgs.acceptTask = orderTask;
				cgs.acceptLeader = vchat->clientNum;
			}
			// see if this was an order
			CG_ShowResponseHead();
		}
	}
	if ( !vchat->voiceOnly && cg_showVoiceText.integer ) {
		CG_AddToTeamChat( vchat->message );
		CG_Printf( "%s\n", vchat->message );
	}
	voiceChatBuffer[cg.voiceChatBufferOut].snd = 0;
}

/*
=====================
CG_PlayBufferedVoieChats
=====================
*/
void CG_PlayBufferedVoiceChats( void ) {
	if ( cg.voiceChatTime < cg.time ) {
		if (cg.voiceChatBufferOut != cg.voiceChatBufferIn && voiceChatBuffer[cg.voiceChatBufferOut].snd) {
			//
			CG_PlayVoiceChat(&voiceChatBuffer[cg.voiceChatBufferOut]);
			//
			cg.voiceChatBufferOut = (cg.voiceChatBufferOut + 1) % MAX_VOICECHATBUFFER;
			cg.voiceChatTime = cg.time + 1000;
		}
	}
}

/*
=====================
CG_AddBufferedVoiceChat
=====================
*/
void CG_AddBufferedVoiceChat( bufferedVoiceChat_t *vchat ) {
	// if we are going into the intermission, don't start any voices
	if ( cg.intermissionStarted ) {
		return;
	}

	memcpy(&voiceChatBuffer[cg.voiceChatBufferIn], vchat, sizeof(bufferedVoiceChat_t));
	cg.voiceChatBufferIn = (cg.voiceChatBufferIn + 1) % MAX_VOICECHATBUFFER;
	if (cg.voiceChatBufferIn == cg.voiceChatBufferOut) {
		CG_PlayVoiceChat( &voiceChatBuffer[cg.voiceChatBufferOut] );
		cg.voiceChatBufferOut++;
	}
}

/*
=================
CG_VoiceChatLocal
=================
*/
void CG_VoiceChatLocal( int mode, qboolean voiceOnly, int clientNum, int color, const char *cmd ) {
	char *chat;
	voiceChatList_t *voiceChatList;
	clientInfo_t *ci;
	sfxHandle_t snd;
	bufferedVoiceChat_t vchat;

	// if we are going into the intermission, don't start any voices
	if ( cg.intermissionStarted ) {
		return;
	}

	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		clientNum = 0;
	}
	ci = &cgs.clientinfo[ clientNum ];

	cgs.currentVoiceClient = clientNum;

	voiceChatList = CG_VoiceChatListForClient( clientNum );

	if ( CG_GetVoiceChat( voiceChatList, cmd, &snd, &chat ) ) {
		//
		if ( mode == SAY_TEAM || !cg_teamChatsOnly.integer ) {
			vchat.clientNum = clientNum;
			vchat.snd = snd;
			vchat.voiceOnly = voiceOnly;
			Q_strncpyz(vchat.cmd, cmd, sizeof(vchat.cmd));
			if ( mode == SAY_TELL ) {
				Com_sprintf(vchat.message, sizeof(vchat.message), "[%s]: %c%c%s", ci->name, Q_COLOR_ESCAPE, color, chat);
			}
			else if ( mode == SAY_TEAM ) {
				Com_sprintf(vchat.message, sizeof(vchat.message), "(%s): %c%c%s", ci->name, Q_COLOR_ESCAPE, color, chat);
			}
			else {
				Com_sprintf(vchat.message, sizeof(vchat.message), "%s: %c%c%s", ci->name, Q_COLOR_ESCAPE, color, chat);
			}
			CG_AddBufferedVoiceChat(&vchat);
		}
	}
}

/*
=================
CG_VoiceChat
=================
*/
void CG_VoiceChat( int mode ) {
	const char *cmd;
	int clientNum, color;
	qboolean voiceOnly;

	voiceOnly = atoi(CG_Argv(1));
	clientNum = atoi(CG_Argv(2));
	color = atoi(CG_Argv(3));
	cmd = CG_Argv(4);

	if (cg_noTaunt.integer != 0) {
		if (!strcmp(cmd, VOICECHAT_KILLINSULT)  || !strcmp(cmd, VOICECHAT_TAUNT) || \
			!strcmp(cmd, VOICECHAT_DEATHINSULT) || !strcmp(cmd, VOICECHAT_KILLGAUNTLET) || \
			!strcmp(cmd, VOICECHAT_PRAISE)) {
			return;
		}
	}

	CG_VoiceChatLocal( mode, voiceOnly, clientNum, color, cmd );
}

/*
=================
CG_RemoveChatEscapeChar
=================
*/
static void CG_RemoveChatEscapeChar( char *text ) {
	int i, l;

	l = 0;
	for ( i = 0; text[i]; i++ ) {
		if (text[i] == '\x19')
			continue;
		text[l++] = text[i];
	}
	text[l] = '\0';
}

/*
=================
CG_ServerCommand

The string has been tokenized and can be retrieved with
Cmd_Argc() / Cmd_Argv()
=================
*/
static void CG_ServerCommand( void ) {
	const char	*cmd;
	char		text[MAX_SAY_TEXT];

	cmd = CG_Argv(0);

	if ( !cmd[0] ) {
		// server claimed the command
		return;
	}

	if ( !strcmp( cmd, "cp" ) ) {
		CG_CenterPrint( CG_Argv(1), SCREEN_HEIGHT * 0.30, BIGCHAR_WIDTH );
		return;
	}

	if ( !strcmp( cmd, "cs" ) ) {
		CG_ConfigStringModified();
		return;
	}

	if ( !strcmp( cmd, "itemcfg" ) ) {
		int	enabled = 0;
		int	height = ITEM_TIMER_DEFAULT_HEIGHT;
		if ( trap_Argc() > 1 ) {
			enabled = atoi( CG_Argv( 1 ) );
		}
		if ( trap_Argc() > 2 ) {
			height = atoi( CG_Argv( 2 ) );
		}
		cgs.itemTimersEnabled = enabled ? qtrue : qfalse;
		if ( height <= 0 ) {
			height = ITEM_TIMER_DEFAULT_HEIGHT;
		} else if ( height > ITEM_TIMER_MAX_HEIGHT ) {
			height = ITEM_TIMER_MAX_HEIGHT;
		}
		cgs.itemTimerHeight = height;
		return;
	}

	if ( !strcmp( cmd, "race_init" ) ) {
		CG_ParseRaceInit();
		return;
	}

	if ( !strcmp( cmd, "race_info" ) ) {
		CG_ParseRaceInfoCommand();
		return;
	}

	if ( !Q_stricmpn( cmd, "admin_race_point_", 17 ) ) {
		CG_ParseAdminRacePoint( cmd );
		return;
	}

	if ( !strcmp( cmd, "print" ) ) {
		CG_Printf( "%s", CG_Argv(1) );
		cmd = CG_Argv(1);			// yes, this is obviously a hack, but so is the way we hear about
									// votes passing or failing
		if ( !Q_stricmpn( cmd, "vote failed", 11 ) || !Q_stricmpn( cmd, "team vote failed", 16 )) {
			trap_S_StartLocalSound( cgs.media.voteFailed, CHAN_ANNOUNCER );
		} else if ( !Q_stricmpn( cmd, "vote passed", 11 ) || !Q_stricmpn( cmd, "team vote passed", 16 ) ) {
			trap_S_StartLocalSound( cgs.media.votePassed, CHAN_ANNOUNCER );
		}
		return;
	}

	if ( !strcmp( cmd, "chat" ) ) {
		if ( !cg_teamChatsOnly.integer ) {
			Q_strncpyz( text, CG_Argv(1), MAX_SAY_TEXT );
			CG_RemoveChatEscapeChar( text );
			CG_Printf( "%s\n", text );
		}
		return;
	}

	if ( !strcmp( cmd, "tchat" ) ) {
		Q_strncpyz( text, CG_Argv(1), MAX_SAY_TEXT );
		CG_RemoveChatEscapeChar( text );
		CG_AddToTeamChat( text );
		CG_Printf( "%s\n", text );
		return;
	}
	if ( !strcmp( cmd, "vchat" ) ) {
		CG_VoiceChat( SAY_ALL );
		return;
	}

	if ( !strcmp( cmd, "vtchat" ) ) {
		CG_VoiceChat( SAY_TEAM );
		return;
	}

	if ( !strcmp( cmd, "vtell" ) ) {
		CG_VoiceChat( SAY_TELL );
		return;
	}

	if ( !strcmp( cmd, "scores" ) ) {
		CG_ParseScores();
		return;
	}

	if ( !strcmp( cmd, "tinfo" ) ) {
		CG_ParseTeamInfo();
		return;
	}

	if ( !strcmp( cmd, "map_restart" ) ) {
		CG_MapRestart();
		return;
	}

  if ( Q_stricmp (cmd, "remapShader") == 0 ) {
		if (trap_Argc() == 4) {
			trap_R_RemapShader(CG_Argv(1), CG_Argv(2), CG_Argv(3));
		}
	}

	// loaddeferred can be both a servercmd and a consolecmd
	if ( !strcmp( cmd, "loaddefered" ) ) {	// FIXME: spelled wrong, but not changing for demo
		CG_LoadDeferredPlayers();
		return;
	}

	// clientLevelShot is sent before taking a special screenshot for
	// the menu system during development
	if ( !strcmp( cmd, "clientLevelShot" ) ) {
		cg.levelShot = qtrue;
		return;
	}

	CG_Printf( "Unknown client game command: %s\n", cmd );
}


/*
====================
CG_ExecuteNewServerCommands

Execute all of the server commands that were received along
with this this snapshot.
====================
*/
void CG_ExecuteNewServerCommands( int latestSequence ) {
	while ( cgs.serverCommandSequence < latestSequence ) {
		if ( trap_GetServerCommand( ++cgs.serverCommandSequence ) ) {
			CG_ServerCommand();
		}
	}
}
