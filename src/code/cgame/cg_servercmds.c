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

typedef struct {
	const char	*legacyName;
	const char	*retailName;
} cgRetailMapAlias_t;

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
static const weapon_t cg_retailWeaponReloadOrder[] = {
	WP_GAUNTLET,
	WP_MACHINEGUN,
	WP_SHOTGUN,
	WP_GRENADE_LAUNCHER,
	WP_ROCKET_LAUNCHER,
	WP_LIGHTNING,
	WP_RAILGUN,
	WP_PLASMAGUN,
	WP_BFG,
	WP_GRAPPLING_HOOK,
	WP_NAILGUN,
	WP_PROX_LAUNCHER,
	WP_CHAINGUN,
	WP_HEAVY_MACHINEGUN
};
typedef struct {
	const char		*token;
	unsigned int	mask;
} cgDisableLoadoutToken_t;

#define CG_DISABLE_LOADOUT_G		( 1u << 0 )
#define CG_DISABLE_LOADOUT_MG		( 1u << 1 )
#define CG_DISABLE_LOADOUT_SG		( 1u << 2 )
#define CG_DISABLE_LOADOUT_GL		( 1u << 3 )
#define CG_DISABLE_LOADOUT_RL		( 1u << 4 )
#define CG_DISABLE_LOADOUT_LG		( 1u << 5 )
#define CG_DISABLE_LOADOUT_RG		( 1u << 6 )
#define CG_DISABLE_LOADOUT_PG		( 1u << 7 )
#define CG_DISABLE_LOADOUT_BFG		( 1u << 8 )
#define CG_DISABLE_LOADOUT_GH		( 1u << 9 )
#define CG_DISABLE_LOADOUT_NG		( 1u << 10 )
#define CG_DISABLE_LOADOUT_PL		( 1u << 11 )
#define CG_DISABLE_LOADOUT_CG		( 1u << 12 )
#define CG_DISABLE_LOADOUT_HMG		( 1u << 13 )

static const cgDisableLoadoutToken_t cg_retailDisableLoadoutTokens[] = {
	{ "g", CG_DISABLE_LOADOUT_G },
	{ "mg", CG_DISABLE_LOADOUT_MG },
	{ "sg", CG_DISABLE_LOADOUT_SG },
	{ "gl", CG_DISABLE_LOADOUT_GL },
	{ "rl", CG_DISABLE_LOADOUT_RL },
	{ "lg", CG_DISABLE_LOADOUT_LG },
	{ "rg", CG_DISABLE_LOADOUT_RG },
	{ "pg", CG_DISABLE_LOADOUT_PG },
	{ "bfg", CG_DISABLE_LOADOUT_BFG },
	{ "gh", CG_DISABLE_LOADOUT_GH },
	{ "ng", CG_DISABLE_LOADOUT_NG },
	{ "pl", CG_DISABLE_LOADOUT_PL },
	{ "cg", CG_DISABLE_LOADOUT_CG },
	{ "hmg", CG_DISABLE_LOADOUT_HMG },
	{ NULL, 0u }
};
static const weapon_t cg_retailAccuracyCommandOrder[] = {
	WP_NONE,
	WP_GAUNTLET,
	WP_MACHINEGUN,
	WP_SHOTGUN,
	WP_GRENADE_LAUNCHER,
	WP_ROCKET_LAUNCHER,
	WP_LIGHTNING,
	WP_RAILGUN,
	WP_PLASMAGUN,
	WP_BFG,
	WP_GRAPPLING_HOOK,
	WP_NAILGUN,
	WP_PROX_LAUNCHER,
	WP_CHAINGUN,
	WP_HEAVY_MACHINEGUN
};
static const cgRetailMapAlias_t cg_retailMapAliases[] = {
	{ "qzca1", "asylum" },
	{ "qzca2", "trinity" },
	{ "qzca3", "quarantine" },
	{ "qzctf1", "duelingkeeps" },
	{ "qzctf2", "troubledwaters" },
	{ "qzctf3", "stronghold" },
	{ "qzctf4", "spacectf" },
	{ "qzctf5", "falloutbunker" },
	{ "qzctf6", "beyondreality" },
	{ "qzctf7", "ironworks" },
	{ "qzctf8", "siberia" },
	{ "qzctf9", "bloodlust" },
	{ "qzctf10", "courtyard" },
	{ "qzdm1", "arenagate" },
	{ "qzdm2", "spillway" },
	{ "qzdm3", "hearth" },
	{ "qzdm4", "eviscerated" },
	{ "qzdm5", "forgotten" },
	{ "qzdm6", "campgrounds" },
	{ "qzdm7", "retribution" },
	{ "qzdm8", "brimstoneabbey" },
	{ "qzdm9", "heroskeep" },
	{ "qzdm10", "namelessplace" },
	{ "qzdm11", "chemicalreaction" },
	{ "qzdm12", "dredwerkz" },
	{ "qzdm13", "lostworld" },
	{ "qzdm14", "grimdungeons" },
	{ "qzdm15", "demonkeep" },
	{ "qzdm16", "cobaltstation" },
	{ "qzdm17", "longestyard" },
	{ "qzdm18", "spacechamber" },
	{ "qzdm19", "terminalheights" },
	{ "qzdm20", "hiddenfortress" },
	{ "qzteam1", "basesiege" },
	{ "qzteam2", "falloutbunker" },
	{ "qzteam3", "innersanctums" },
	{ "qzteam4", "scornforge" },
	{ "qzteam6", "vortexportal" },
	{ "qzteam7", "rebound" },
	{ "qztourney1", "powerstation" },
	{ "qztourney2", "provinggrounds" },
	{ "qztourney3", "hellsgate" },
	{ "qztourney4", "verticalvengeance" },
	{ "qztourney5", "hellsgateredux" },
	{ "qztourney6", "almostlost" },
	{ "qztourney7", "furiousheights" },
	{ "qztourney8", "sacellum" },
	{ "qztourney9", "houseofdecay" },
	{ "ztntourney1", "bloodrun" }
};
static int cg_matchTimeoutStartTime;
static int cg_matchRoundStartTime;
static void CG_AddToTeamChat( const char *str );

#define CG_RETAIL_TDM_TEAMSTAT_COUNT	14
#define CG_RETAIL_CTF_TEAMSTAT_COUNT	17
#define CG_RETAIL_TDM_SCORE_ROW_FIELDS	15
#define CG_RETAIL_CA_SCORE_ROW_FIELDS	16
#define CG_RETAIL_CTF_SCORE_ROW_FIELDS	17
#define CG_RETAIL_FREEZE_SCORE_ROW_FIELDS	17
#define CG_RETAIL_RR_SCORE_ROW_FIELDS	19
#define CG_RETAIL_DUEL_CORE_FIELDS		21
#define CG_RETAIL_DUEL_WEAPON_FIELDS		5
#define CG_RETAIL_DUEL_WEAPON_COUNT		( WP_NUM_WEAPONS - 1 )
#define CG_RETAIL_DUEL_SCORE_ROW_FIELDS	( CG_RETAIL_DUEL_CORE_FIELDS + ( CG_RETAIL_DUEL_WEAPON_FIELDS * CG_RETAIL_DUEL_WEAPON_COUNT ) )

static const cgTeamStatIndex_t cgRetailTdmTeamStatOrder[CG_RETAIL_TDM_TEAMSTAT_COUNT] = {
	CG_TEAMSTAT_MAP_PICKUPS,
	CG_TEAMSTAT_PICKUPS_RA,
	CG_TEAMSTAT_PICKUPS_YA,
	CG_TEAMSTAT_PICKUPS_GA,
	CG_TEAMSTAT_PICKUPS_MH,
	CG_TEAMSTAT_PICKUPS_QUAD,
	CG_TEAMSTAT_PICKUPS_BS,
	CG_TEAMSTAT_TIMEHELD_QUAD,
	CG_TEAMSTAT_TIMEHELD_BS,
	CG_TEAMSTAT_PICKUPS_FLAG,
	CG_TEAMSTAT_PICKUPS_MEDKIT,
	CG_TEAMSTAT_PICKUPS_REGEN,
	CG_TEAMSTAT_PICKUPS_HASTE,
	CG_TEAMSTAT_PICKUPS_INVIS
};

static const cgTeamStatIndex_t cgRetailCtfTeamStatOrder[CG_RETAIL_CTF_TEAMSTAT_COUNT] = {
	CG_TEAMSTAT_PICKUPS_RA,
	CG_TEAMSTAT_PICKUPS_YA,
	CG_TEAMSTAT_PICKUPS_GA,
	CG_TEAMSTAT_PICKUPS_MH,
	CG_TEAMSTAT_PICKUPS_QUAD,
	CG_TEAMSTAT_PICKUPS_BS,
	CG_TEAMSTAT_TIMEHELD_QUAD,
	CG_TEAMSTAT_TIMEHELD_BS,
	CG_TEAMSTAT_PICKUPS_FLAG,
	CG_TEAMSTAT_PICKUPS_MEDKIT,
	CG_TEAMSTAT_PICKUPS_REGEN,
	CG_TEAMSTAT_PICKUPS_HASTE,
	CG_TEAMSTAT_PICKUPS_INVIS,
	CG_TEAMSTAT_TIMEHELD_FLAG,
	CG_TEAMSTAT_TIMEHELD_REGEN,
	CG_TEAMSTAT_TIMEHELD_HASTE,
	CG_TEAMSTAT_TIMEHELD_INVIS
};

static const char *const cg_retailBlankGameInfoLines[6] = {
	" ",
	" ",
	" ",
	" ",
	" ",
	" "
};

static const char *const cg_retailTrainingGameInfoLines[6] = {
	"Welcome to QUAKE LIVE training",
	"A trainer named 'Crash' is waiting to give you a quick introduction",
	"to the game. Follow 'Crash' through a tour of the warm-up arena, then",
	"compete against her in a free-for-all deathmatch game.",
	"",
	"Click 'Start Training' to begin."
};

static const char *const cg_retailGameInfoLines[GT_MAX_GAME_TYPE][6] = {
	[GT_FFA] = {
		"This is a Free For All game",
		"Shoot Everyone!",
		"First player to reach the Frag Limit wins.",
		"If time runs out, the player with the highest score wins.",
		"If the time limit is hit and there is a tie, a Sudden Death round begins.",
		" "
	},
	[GT_TOURNAMENT] = {
		"This is a 1 vs 1 Duel game",
		"Defeat your opponent!",
		"If time runs out, the player with the highest score wins.",
		"If the time limit is hit and there is a tie, the match extends",
		"into overtime.",
		" "
	},
	[GT_SINGLE_PLAYER] = {
		"This is a Race game",
		"Race to the finish!",
		"Run through the course, hitting all checkpoints in order.",
		"Use all your movement skills to complete the course the fastest.",
		"The player with the shortest time at the end of the match wins.",
		" "
	},
	[GT_TEAM] = {
		"This is a Team Deathmatch game",
		"Shoot anyone on the other team!",
		"When time runs out, the team with the highest score wins.",
		"If the time limit is hit and there is a tie, a Sudden Death round begins.",
		" ",
		" "
	},
	[GT_CLAN_ARENA] = {
		"This is a Clan Arena game",
		"Shoot anyone on the other team!",
		"You spawn equipped with all weapons and full armor.",
		"Completely eliminate the opposing team to win the round.",
		"The first team to reach the round limit wins.",
		" "
	},
	[GT_CTF] = {
		"This is a Capture the Flag game",
		"Grab the other teams flag and bring it back to your own flag.",
		"First team to reach the Capture Limit wins.",
		"If time runs out, the team with most captures wins.",
		"If the time limit is hit and there is a tie, a Sudden Death round begins.",
		" "
	},
	[GT_1FCTF] = {
		"This is a One Flag game",
		"Grab the white flag in the center, and carry it to the enemy flag stand.",
		"First team to reach the Capture Limit wins.",
		"If time runs out, the team with most captures wins.",
		"If the time limit is hit and there is a tie, a Sudden Death round begins.",
		" "
	},
	[GT_OBELISK] = {
		"This is an Overload game",
		"Destroy the enemy obelisk.",
		"The obelisk will explode when enough damage is applied.",
		"When it explodes, your team scores a capture.",
		"First team to reach the Capture Limit wins.",
		" "
	},
	[GT_HARVESTER] = {
		"This is a Harvester game",
		"When a player is fragged, a skull spawns from the skull generator.",
		"Pick up enemy skulls.",
		"Carry the skulls to the enemy flag stand.",
		"First team to reach the Capture Limit wins.",
		" "
	},
	[GT_FREEZE] = {
		"This is a Freeze Tag game",
		"Shoot everyone on the other team!",
		"Fragging another player freezes them.",
		"Freeze all enemy team members to score a team point.",
		"Stand by frozen teammates for 3 seconds to thaw them.",
		" "
	},
	[GT_DOMINATION] = {
		"This is a Domination game",
		"Capture domination points to earn points for your team.",
		"Either team can capture any domination point.",
		"Capture multiple points to earn more points for your team.",
		"First team to reach the Score Limit wins.",
		" "
	},
	[GT_ATTACK_DEFEND] = {
		"This is an Attack and Defend game",
		"Alternate each round Attacking or Defending the flag.",
		"You spawn equipped with all weapons and full armor.",
		"Touch the enemy's flag to be awarded a bonus point.",
		"Eliminate the opposing team or capture their flag to win the round.",
		" "
	},
	[GT_RED_ROVER] = {
		"This is a Red Rover game",
		"You spawn equipped with all weapons and full armor.",
		"Frag enemies and they will respawn onto your team.",
		"Compete against your teammates for the most damage and frags.",
		"The player with the highest score at the end of the round limit wins.",
		" "
	}
};

static void CG_RemoveChatEscapeChar( char *text );
static void CG_ClearScoreStatsCache( void );
static void CG_ClearTeamScoreStatsCache( void );
static void CG_ClearClanArenaStatsCache( void );
static void CG_ClearTDMStatsCache( void );
static void CG_ClearCTFStatsCache( void );

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
		memcpy( settings, defaults, sizeof( pmove_settings_t ) );
	} else {
		memset( settings, 0, sizeof( pmove_settings_t ) );
	}
}

/*
=============
CG_SkipPmoveWhitespace

Advances the cursor past pmove payload whitespace characters.
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
CG_ParsePmoveJsonIntOrBool

Reads an integer token while accepting legacy JSON booleans as 0/1 aliases.
=============
*/
static qboolean CG_ParsePmoveJsonIntOrBool( const char **cursor, int *value ) {
	qboolean	boolValue;

	if ( !cursor || !*cursor || !value ) {
		return qfalse;
	}

	CG_SkipPmoveWhitespace( cursor );
	if ( !Q_strnicmp( *cursor, "true", 4 ) || !Q_strnicmp( *cursor, "false", 5 ) ) {
		if ( !CG_ParsePmoveJsonBool( cursor, &boolValue ) ) {
			return qfalse;
		}

		*value = boolValue ? 1 : 0;
		return qtrue;
	}

	return CG_ParsePmoveJsonInt( cursor, value );
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
CG_HasPmoveCompactToken

Returns qtrue when another compact pmove token remains.
=============
*/
static qboolean CG_HasPmoveCompactToken( const char **cursor ) {
	if ( !cursor || !*cursor ) {
		return qfalse;
	}

	CG_SkipPmoveWhitespace( cursor );
	return **cursor ? qtrue : qfalse;
}

/*
=============
CG_ParsePmoveCompactBool

Reads one retail compact boolean token.
=============
*/
static qboolean CG_ParsePmoveCompactBool( const char **cursor, qboolean *value ) {
	int parsed;

	if ( !value ) {
		return qfalse;
	}

	if ( !CG_ParsePmoveJsonInt( cursor, &parsed ) ) {
		return qfalse;
	}

	*value = parsed ? qtrue : qfalse;
	return qtrue;
}

/*
=============
CG_ClampPmoveNonNegative

Matches the retail compact parser's clamp for selected tuning floats.
=============
*/
static void CG_ClampPmoveNonNegative( float *value ) {
	if ( value && *value < 0.0f ) {
		*value = 0.0f;
	}
}

/*
=============
CG_ParsePmoveCompactSettingsPayload

Decodes the retail compact pmove configstring. Retail cgame consumes the first
33 tokens; the current reconstruction accepts a trailing extension for local
prediction fields that retail either replicated through playerState flags or
did not expose through this transport.
=============
*/
static qboolean CG_ParsePmoveCompactSettingsPayload( const char *payload, pmove_settings_t *settings ) {
	pmove_settings_t parsed;
	const char *cursor;
	int integerValue;

	if ( !settings ) {
		return qfalse;
	}

	CG_CopyDefaultPmoveSettings( &parsed );
	if ( !payload || !*payload ) {
		memcpy( settings, &parsed, sizeof( parsed ) );
		return qfalse;
	}

	cursor = payload;

#define PMOVE_COMPACT_FLOAT( name ) \
	if ( !CG_ParsePmoveJsonFloat( &cursor, &parsed.name ) ) { \
		CG_CopyDefaultPmoveSettings( settings ); \
		return qfalse; \
	}
#define PMOVE_COMPACT_INT( name ) \
	if ( !CG_ParsePmoveJsonInt( &cursor, &parsed.name ) ) { \
		CG_CopyDefaultPmoveSettings( settings ); \
		return qfalse; \
	}
#define PMOVE_COMPACT_BOOL( name ) \
	if ( !CG_ParsePmoveCompactBool( &cursor, &parsed.name ) ) { \
		CG_CopyDefaultPmoveSettings( settings ); \
		return qfalse; \
	}

	PMOVE_COMPACT_FLOAT( airAccel );
	PMOVE_COMPACT_FLOAT( airStepFriction );
	PMOVE_COMPACT_INT( airSteps );
	PMOVE_COMPACT_FLOAT( airStopAccel );
	PMOVE_COMPACT_BOOL( autoHop );
	PMOVE_COMPACT_BOOL( bunnyHop );
	PMOVE_COMPACT_INT( chainJump );
	if ( !CG_ParsePmoveJsonInt( &cursor, &integerValue ) ) {
		CG_CopyDefaultPmoveSettings( settings );
		return qfalse;
	}
	parsed.chainJumpVelocity = (float)integerValue;
	PMOVE_COMPACT_FLOAT( circleStrafeFriction );
	PMOVE_COMPACT_FLOAT( crouchSlideFriction );
	PMOVE_COMPACT_INT( crouchSlideTime );
	PMOVE_COMPACT_BOOL( crouchStepJump );
	PMOVE_COMPACT_FLOAT( jumpTimeDeltaMin );
	PMOVE_COMPACT_FLOAT( jumpVelocity );
	PMOVE_COMPACT_FLOAT( jumpVelocityMax );
	PMOVE_COMPACT_FLOAT( jumpVelocityScaleAdd );
	PMOVE_COMPACT_FLOAT( jumpVelocityTimeThreshold );
	PMOVE_COMPACT_FLOAT( jumpVelocityTimeThresholdOffset );
	PMOVE_COMPACT_BOOL( noPlayerClip );
	PMOVE_COMPACT_BOOL( rampJump );
	PMOVE_COMPACT_FLOAT( rampJumpScale );
	PMOVE_COMPACT_FLOAT( stepHeight );
	PMOVE_COMPACT_BOOL( stepJump );
	PMOVE_COMPACT_FLOAT( stepJumpVelocity );
	PMOVE_COMPACT_FLOAT( strafeAccel );
	PMOVE_COMPACT_FLOAT( velocityGh );
	PMOVE_COMPACT_FLOAT( walkAccel );
	PMOVE_COMPACT_FLOAT( walkFriction );
	PMOVE_COMPACT_FLOAT( waterSwimScale );
	PMOVE_COMPACT_FLOAT( waterWadeScale );
	PMOVE_COMPACT_INT( weaponDropTime );
	PMOVE_COMPACT_INT( weaponRaiseTime );
	PMOVE_COMPACT_FLOAT( wishSpeed );

	CG_ClampPmoveNonNegative( &parsed.jumpVelocityTimeThreshold );
	CG_ClampPmoveNonNegative( &parsed.jumpVelocityTimeThresholdOffset );
	CG_ClampPmoveNonNegative( &parsed.velocityGh );

	if ( CG_HasPmoveCompactToken( &cursor ) ) {
		PMOVE_COMPACT_FLOAT( airControl );
	}
	if ( CG_HasPmoveCompactToken( &cursor ) ) {
		PMOVE_COMPACT_BOOL( crouchSlide );
	}
	if ( CG_HasPmoveCompactToken( &cursor ) ) {
		PMOVE_COMPACT_BOOL( doubleJump );
	}
	if ( CG_HasPmoveCompactToken( &cursor ) ) {
		PMOVE_COMPACT_FLOAT( machinegunIronsightsScale );
	}
	if ( CG_HasPmoveCompactToken( &cursor ) ) {
		PMOVE_COMPACT_FLOAT( gauntletSpeedFactor );
	}
	if ( CG_HasPmoveCompactToken( &cursor ) ) {
		PMOVE_COMPACT_INT( midAirMinimumHeight );
	}
	if ( CG_HasPmoveCompactToken( &cursor ) ) {
		PMOVE_COMPACT_BOOL( nailgunBounceEnabled );
	}
	if ( CG_HasPmoveCompactToken( &cursor ) ) {
		PMOVE_COMPACT_INT( nailgunBouncePercentage );
	}
	if ( CG_HasPmoveCompactToken( &cursor ) ) {
		PMOVE_COMPACT_FLOAT( quadDamageMultiplier );
	}
	if ( CG_HasPmoveCompactToken( &cursor ) ) {
		PMOVE_COMPACT_BOOL( guidedRocketEnabled );
	}
	if ( CG_HasPmoveCompactToken( &cursor ) ) {
		PMOVE_COMPACT_INT( quadHogEnabled );
	}
	if ( CG_HasPmoveCompactToken( &cursor ) ) {
		PMOVE_COMPACT_INT( quadHogIdleSeconds );
	}
	if ( CG_HasPmoveCompactToken( &cursor ) ) {
		PMOVE_COMPACT_INT( quadHogTimeSeconds );
	}
	if ( CG_HasPmoveCompactToken( &cursor ) ) {
		PMOVE_COMPACT_INT( quadHogPingRateSeconds );
	}

#undef PMOVE_COMPACT_FLOAT
#undef PMOVE_COMPACT_INT
#undef PMOVE_COMPACT_BOOL

	memcpy( settings, &parsed, sizeof( parsed ) );
	return qtrue;
}

/*
=============
CG_ParsePmoveJsonSettingsPayload

Decodes the older reconstruction JSON pmove configstring payload into a
settings structure.
=============
*/
static qboolean CG_ParsePmoveJsonSettingsPayload( const char *payload, pmove_settings_t *settings ) {
	pmove_settings_t parsed;
	const char *cursor;
	char key[64];
	qboolean valid;

	if ( !settings ) {
		return qfalse;
	}

	CG_CopyDefaultPmoveSettings( &parsed );
	if ( !payload || !*payload ) {
		memcpy( settings, &parsed, sizeof( parsed ) );
		return qfalse;
	}

	cursor = payload;
	if ( !CG_ExpectPmoveChar( &cursor, '{' ) ) {
		memcpy( settings, &parsed, sizeof( parsed ) );
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
		} else if ( !Q_stricmp( key, "chainJump" ) ) {
			if ( !CG_ParsePmoveJsonIntOrBool( &cursor, &parsed.chainJump ) ) {
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
		PMOVE_FLOAT_FIELD( chainJumpVelocity )
		PMOVE_FLOAT_FIELD( circleStrafeFriction )
		PMOVE_BOOL_FIELD( crouchSlide )
		PMOVE_FLOAT_FIELD( crouchSlideFriction )
		PMOVE_INT_FIELD( crouchSlideTime )
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

	memcpy( settings, &parsed, sizeof( parsed ) );
	return valid;
}

/*
=============
CG_ParsePmoveSettingsPayload

Decodes the server broadcast pmove settings into a settings structure.
=============
*/
static qboolean CG_ParsePmoveSettingsPayload( const char *payload, pmove_settings_t *settings ) {
	const char *cursor;

	if ( !settings ) {
		return qfalse;
	}

	if ( !payload || !*payload ) {
		CG_CopyDefaultPmoveSettings( settings );
		return qfalse;
	}

	cursor = payload;
	CG_SkipPmoveWhitespace( &cursor );
	if ( *cursor == '{' ) {
		return CG_ParsePmoveJsonSettingsPayload( cursor, settings );
	}

	return CG_ParsePmoveCompactSettingsPayload( cursor, settings );
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
	memcpy( &cg_pmoveSettings, &parsed, sizeof( cg_pmoveSettings ) );
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
	cgs.racePointCount = 0;
	cgs.raceLeaderSplitCount = 0;
	memset( cgs.racePoints, 0, sizeof( cgs.racePoints ) );
	memset( cgs.raceLeaderSplits, 0, sizeof( cgs.raceLeaderSplits ) );
	CG_RaceResetState();
}

/*
=============
CG_ParseRaceInfo

Caches the retail six-field race follow payload from the race_info command.
=============
*/
static void CG_ParseRaceInfo( void ) {
	cgs.raceInfoActive = atoi( CG_Argv( 1 ) ) ? qtrue : qfalse;
	cgs.raceInfoStartTime = atoi( CG_Argv( 2 ) );
	cgs.raceInfoLastTime = atoi( CG_Argv( 3 ) );
	cgs.raceInfoCheckpointCount = atoi( CG_Argv( 4 ) );
	cgs.raceInfoCurrentCheckpointEntityNum = atoi( CG_Argv( 5 ) );
	cgs.raceInfoNextCheckpointEntityNum = atoi( CG_Argv( 6 ) );
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
CG_ParseRaceScores

=================
*/
static void CG_ParseRaceScores( void ) {
	int		i;

	cg.numScores = atoi( CG_Argv( 1 ) );
	if ( cg.numScores > MAX_CLIENTS ) {
		cg.numScores = MAX_CLIENTS;
	}

	cg.teamScores[0] = 0;
	cg.teamScores[1] = 0;

	memset( cg.scores, 0, sizeof( cg.scores ) );
	CG_ClearScoreStatsCache();
	CG_ClearTeamScoreStatsCache();
	CG_ClearClanArenaStatsCache();
	CG_ClearTDMStatsCache();
	CG_ClearCTFStatsCache();
	for ( i = 0 ; i < cg.numScores ; i++ ) {
		cg.scores[i].client = atoi( CG_Argv( i * 4 + 2 ) );
		cg.scores[i].score = atoi( CG_Argv( i * 4 + 3 ) );
		cg.scores[i].ping = 0;
		cg.scores[i].time = 0;
		cg.scores[i].scoreFlags = 0;
		cg.scores[i].powerUps = 0;
		cg.scores[i].accuracy = 0;
		cg.scores[i].impressiveCount = 0;
		cg.scores[i].excellentCount = 0;
		cg.scores[i].guantletCount = 0;
		cg.scores[i].defendCount = 0;
		cg.scores[i].assistCount = 0;
		cg.scores[i].perfect = 0;
		cg.scores[i].captures = 0;
		cg.scores[i].damage = 0;
		cg.scores[i].deaths = 0;

		if ( cg.scores[i].client < 0 || cg.scores[i].client >= MAX_CLIENTS ) {
			cg.scores[i].client = 0;
		}
		cgs.clientinfo[ cg.scores[i].client ].score = cg.scores[i].score;
		cgs.clientinfo[ cg.scores[i].client ].powerups = 0;

		cg.scores[i].team = cgs.clientinfo[cg.scores[i].client].team;
	}
	memset( cg.scoreStats, 0, sizeof( cg.scoreStats ) );
	memset( &cg.teamScoreStats, 0, sizeof( cg.teamScoreStats ) );
	CG_SetScoreSelection(NULL);
}

/*
=============
CG_ParseRetailAccuracyCommand

Retail routes both `acc` and `pstats` through the same compact 15-slot
per-weapon percentage slab.
=============
*/
static void CG_ParseRetailAccuracyCommand( void ) {
	int argc;
	int i;

	memset( cg.weaponAccuracies, 0, sizeof( cg.weaponAccuracies ) );

	argc = trap_Argc();
	for ( i = 0; i < ARRAY_LEN( cg_retailAccuracyCommandOrder ) && ( i + 1 ) < argc; i++ ) {
		weapon_t weapon;
		int value;

		weapon = cg_retailAccuracyCommandOrder[i];
		if ( weapon < 0 || weapon >= WP_NUM_WEAPONS ) {
			continue;
		}

		value = atoi( CG_Argv( i + 1 ) );
		if ( value < 0 ) {
			value = 0;
		} else if ( value > 100 ) {
			value = 100;
		}

		cg.weaponAccuracies[weapon] = value;
	}
}

/*
=============
CG_ParseAcc

Decodes the retail `acc` payload into the live per-weapon percentage cache used
by the vertical local accuracy overlay.
=============
*/
static void CG_ParseAcc( void ) {
	CG_ParseRetailAccuracyCommand();
}

#define CG_SCORESTAT_FRAG_WEAPON_COUNT		13
#define CG_SCORESTAT_ACCURACY_WEAPON_COUNT	12
#define CG_SCORESTAT_DMG_WEAPON_COUNT		13
#define CG_SCORESTAT_PLACEMENT_SLOTS		2
#define CG_SCORESTAT_FIELDS_PER_CLIENT		( 1 + CG_SCORESTAT_FRAG_WEAPON_COUNT + ( 2 * CG_SCORESTAT_ACCURACY_WEAPON_COUNT ) + CG_SCORESTAT_DMG_WEAPON_COUNT + ( 2 * CG_SCORESTAT_PICKUP_COUNT ) + 2 )
#define CG_CASTAT_WEAPON_COUNT				( WP_NUM_WEAPONS - 1 )

static const weapon_t cgScoreStatFragWeapons[CG_SCORESTAT_FRAG_WEAPON_COUNT] = {
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

static const weapon_t cgScoreStatAccuracyWeapons[CG_SCORESTAT_ACCURACY_WEAPON_COUNT] = {
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

static const weapon_t cgCAStatWeapons[CG_CASTAT_WEAPON_COUNT] = {
	WP_GAUNTLET,
	WP_MACHINEGUN,
	WP_SHOTGUN,
	WP_GRENADE_LAUNCHER,
	WP_ROCKET_LAUNCHER,
	WP_LIGHTNING,
	WP_RAILGUN,
	WP_PLASMAGUN,
	WP_BFG,
	WP_GRAPPLING_HOOK,
	WP_NAILGUN,
	WP_PROX_LAUNCHER,
	WP_CHAINGUN,
	WP_HEAVY_MACHINEGUN
};

/*
=================
CG_DebugAppendIntCsv

Builds a comma-separated integer list used by ownerdraw debug logging.
=================
*/
static void CG_DebugAppendIntCsv( char *buffer, int bufferSize, const int *values, int count ) {
	int	i;
	char	entry[24];

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !values || count <= 0 ) {
		return;
	}

	for ( i = 0; i < count; i++ ) {
		Com_sprintf( entry, sizeof( entry ), "%s%i", ( i > 0 ) ? "," : "", values[i] );
		Q_strcat( buffer, bufferSize, entry );
	}
}

/*
=================
CG_DebugAppendFloatCsv

Builds a comma-separated float list used by ownerdraw debug logging.
=================
*/
static void CG_DebugAppendFloatCsv( char *buffer, int bufferSize, const float *values, int count ) {
	int	i;
	char	entry[24];

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !values || count <= 0 ) {
		return;
	}

	for ( i = 0; i < count; i++ ) {
		Com_sprintf( entry, sizeof( entry ), "%s%3.2f", ( i > 0 ) ? "," : "", values[i] );
		Q_strcat( buffer, bufferSize, entry );
	}
}

/*
=================
CG_DebugDumpPlacementOwnerdrawScoreStats

Dumps parsed first/second placement ownerdraw inputs for validation harnesses.
=================
*/
static void CG_DebugDumpPlacementOwnerdrawScoreStats( void ) {
	int		placementIndex;

	if ( !cg_debugOwnerdrawStats.integer ) {
		return;
	}

	if ( cg.numScores <= 0 ) {
		CG_Printf( "ownerdraw_stats: placement rows unavailable (numScores=0)\n" );
		return;
	}

	for ( placementIndex = 0; placementIndex < cg.numScores && placementIndex < CG_SCORESTAT_PLACEMENT_SLOTS; placementIndex++ ) {
		const score_t		*score;
		int			clientNum;
		const cgScoreStats_t	*stats;
		int			fragValues[CG_SCORESTAT_FRAG_WEAPON_COUNT];
		int			hitValues[CG_SCORESTAT_ACCURACY_WEAPON_COUNT];
		int			shotValues[CG_SCORESTAT_ACCURACY_WEAPON_COUNT];
		int			damageValues[CG_SCORESTAT_DMG_WEAPON_COUNT];
		int			pickupValues[CG_SCORESTAT_PICKUP_COUNT];
		float			pickupAvgValues[CG_SCORESTAT_PICKUP_COUNT];
		char			fragCsv[256];
		char			hitCsv[256];
		char			shotCsv[256];
		char			damageCsv[256];
		char			pickupCsv[96];
		char			pickupAvgCsv[96];
		int			i;

		score = &cg.scores[placementIndex];
		clientNum = score->client;
		if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
			CG_Printf( "ownerdraw_stats: place=%i invalid client index=%i\n", placementIndex + 1, clientNum );
			continue;
		}

		stats = &cg.scoreStats[clientNum];
		if ( !stats->valid ) {
			CG_Printf( "ownerdraw_stats: place=%i client=%i valid=0\n", placementIndex + 1, clientNum );
			continue;
		}

		for ( i = 0; i < CG_SCORESTAT_FRAG_WEAPON_COUNT; i++ ) {
			int weapon = cgScoreStatFragWeapons[i];
			fragValues[i] = ( weapon > WP_NONE && weapon < WP_NUM_WEAPONS ) ? stats->weaponFrags[weapon] : 0;
		}
		for ( i = 0; i < CG_SCORESTAT_ACCURACY_WEAPON_COUNT; i++ ) {
			int weapon = cgScoreStatAccuracyWeapons[i];
			hitValues[i] = ( weapon > WP_NONE && weapon < WP_NUM_WEAPONS ) ? stats->weaponHits[weapon] : 0;
			shotValues[i] = ( weapon > WP_NONE && weapon < WP_NUM_WEAPONS ) ? stats->weaponShots[weapon] : 0;
		}
		for ( i = 0; i < CG_SCORESTAT_DMG_WEAPON_COUNT; i++ ) {
			int weapon = cgScoreStatFragWeapons[i];
			damageValues[i] = ( weapon > WP_NONE && weapon < WP_NUM_WEAPONS ) ? stats->weaponDamage[weapon] : 0;
		}
		for ( i = 0; i < CG_SCORESTAT_PICKUP_COUNT; i++ ) {
			pickupValues[i] = stats->pickupCounts[i];
			pickupAvgValues[i] = stats->pickupAvgSeconds[i];
		}

		CG_DebugAppendIntCsv( fragCsv, sizeof( fragCsv ), fragValues, CG_SCORESTAT_FRAG_WEAPON_COUNT );
		CG_DebugAppendIntCsv( hitCsv, sizeof( hitCsv ), hitValues, CG_SCORESTAT_ACCURACY_WEAPON_COUNT );
		CG_DebugAppendIntCsv( shotCsv, sizeof( shotCsv ), shotValues, CG_SCORESTAT_ACCURACY_WEAPON_COUNT );
		CG_DebugAppendIntCsv( damageCsv, sizeof( damageCsv ), damageValues, CG_SCORESTAT_DMG_WEAPON_COUNT );
		CG_DebugAppendIntCsv( pickupCsv, sizeof( pickupCsv ), pickupValues, CG_SCORESTAT_PICKUP_COUNT );
		CG_DebugAppendFloatCsv( pickupAvgCsv, sizeof( pickupAvgCsv ), pickupAvgValues, CG_SCORESTAT_PICKUP_COUNT );

		CG_Printf(
			"ownerdraw_stats: place=%i client=%i valid=%i frags=%s hits=%s shots=%s dmg=%s pickups=%s pickupAvg=%s pr=%i tier=%i\n",
			placementIndex + 1,
			clientNum,
			stats->valid ? 1 : 0,
			fragCsv,
			hitCsv,
			shotCsv,
			damageCsv,
			pickupCsv,
			pickupAvgCsv,
			stats->progressionPr,
			stats->progressionTier );
	}
}

/*
=================
CG_DebugDumpTeamOwnerdrawScoreStats

Dumps parsed red/blue team pickup and time-held ownerdraw inputs.
=================
*/
static void CG_DebugDumpTeamOwnerdrawScoreStats( int fieldCount ) {
	int		teamIndex;

	if ( !cg_debugOwnerdrawStats.integer ) {
		return;
	}

	if ( fieldCount <= 0 || fieldCount > CG_TEAMSTAT_COUNT ) {
		fieldCount = CG_TEAMSTAT_COUNT;
	}

	for ( teamIndex = 0; teamIndex < 2; teamIndex++ ) {
		int	values[CG_TEAMSTAT_COUNT];
		int	i;
		char	csv[512];

		for ( i = 0; i < fieldCount; i++ ) {
			values[i] = cg.teamScoreStats.values[teamIndex][i];
		}

		CG_DebugAppendIntCsv( csv, sizeof( csv ), values, fieldCount );
		CG_Printf(
			"ownerdraw_stats_team: team=%s fields=%i valid=%i values=%s\n",
			( teamIndex == 0 ) ? "red" : "blue",
			fieldCount,
			cg.teamScoreStats.valid ? 1 : 0,
			csv );
	}
}

/*
=================
CG_ClearScoreStatsCache

Clears cached per-weapon placement stats until a fresh scorestats command arrives.
=================
*/
static void CG_ClearScoreStatsCache( void ) {
	memset( cg.scoreStats, 0, sizeof( cg.scoreStats ) );
}

/*
=================
CG_ClearTeamScoreStatsCache

Clears cached team pickup/time-held scoreboard aggregates.
=================
*/
static void CG_ClearTeamScoreStatsCache( void ) {
	memset( &cg.teamScoreStats, 0, sizeof( cg.teamScoreStats ) );
}

/*
=================
CG_ClearClanArenaStatsCache

Clears cached retail castats rows until a fresh intermission update arrives.
=================
*/
static void CG_ClearClanArenaStatsCache( void ) {
	memset( cg.clanArenaStats, 0, sizeof( cg.clanArenaStats ) );
}

/*
=================
CG_ClearTDMStatsCache

Clears cached retail tdmstats rows until a fresh intermission update arrives.
=================
*/
static void CG_ClearTDMStatsCache( void ) {
	memset( cg.tdmStats, 0, sizeof( cg.tdmStats ) );
}

/*
=================
CG_ClearCTFStatsCache

Clears cached retail ctfstats rows until a fresh intermission update arrives.
=================
*/
static void CG_ClearCTFStatsCache( void ) {
	memset( cg.ctfStats, 0, sizeof( cg.ctfStats ) );
}

/*
=================
CG_ResetParsedScoreboardCaches

Clears the active scoreboard row caches before a new scoreboard payload is
parsed.
=================
*/
static void CG_ResetParsedScoreboardCaches( void ) {
	memset( cg.scores, 0, sizeof( cg.scores ) );
	CG_ClearScoreStatsCache();
	CG_ClearTeamScoreStatsCache();
	CG_ClearClanArenaStatsCache();
	CG_ClearTDMStatsCache();
	CG_ClearCTFStatsCache();
}

/*
=================
CG_FinalizeParsedScoreRow

Clamps a parsed scoreboard row, publishes its score into clientinfo, and
optionally updates the mirrored powerup bits when the transport provides them.
=================
*/
static void CG_FinalizeParsedScoreRow( score_t *score, int powerups ) {
	if ( !score ) {
		return;
	}

	if ( score->client < 0 || score->client >= MAX_CLIENTS ) {
		score->client = 0;
	}

	cgs.clientinfo[score->client].score = score->score;
	if ( powerups >= 0 ) {
		score->powerUps = powerups;
		cgs.clientinfo[score->client].powerups = powerups;
	}

	if ( score->team < TEAM_FREE || score->team >= TEAM_NUM_TEAMS ) {
		score->team = cgs.clientinfo[score->client].team;
	}
}

/*
=================
CG_ParseGenericScoreRows

Parses the current GPL-shaped 16-column scoreboard row layout from an arbitrary
argument offset and stride.
=================
*/
static void CG_ParseGenericScoreRows( int rowStartArg, int rowStride ) {
	int		i;
	int		argc;

	argc = trap_Argc();
	for ( i = 0 ; i < cg.numScores ; i++ ) {
		int		baseArg;
		int		powerups;

		baseArg = rowStartArg + i * rowStride;
		if ( argc <= ( baseArg + 15 ) ) {
			break;
		}

		cg.scores[i].client = atoi( CG_Argv( baseArg ) );
		cg.scores[i].score = atoi( CG_Argv( baseArg + 1 ) );
		cg.scores[i].ping = atoi( CG_Argv( baseArg + 2 ) );
		cg.scores[i].time = atoi( CG_Argv( baseArg + 3 ) );
		cg.scores[i].scoreFlags = atoi( CG_Argv( baseArg + 4 ) );
		powerups = atoi( CG_Argv( baseArg + 5 ) );
		cg.scores[i].accuracy = atoi( CG_Argv( baseArg + 6 ) );
		cg.scores[i].impressiveCount = atoi( CG_Argv( baseArg + 7 ) );
		cg.scores[i].excellentCount = atoi( CG_Argv( baseArg + 8 ) );
		cg.scores[i].guantletCount = atoi( CG_Argv( baseArg + 9 ) );
		cg.scores[i].defendCount = atoi( CG_Argv( baseArg + 10 ) );
		cg.scores[i].assistCount = atoi( CG_Argv( baseArg + 11 ) );
		cg.scores[i].perfect = atoi( CG_Argv( baseArg + 12 ) );
		cg.scores[i].captures = atoi( CG_Argv( baseArg + 13 ) );
		cg.scores[i].damage = atoi( CG_Argv( baseArg + 14 ) );
		cg.scores[i].deaths = atoi( CG_Argv( baseArg + 15 ) );
		cg.scores[i].kills = 0;
		cg.scores[i].bestWeapon = WP_NONE;
		cg.scores[i].activePlayer = qfalse;
		cg.scores[i].team = TEAM_FREE;

		CG_FinalizeParsedScoreRow( &cg.scores[i], powerups );
	}
}

/*
=================
CG_ParseRetailTdmScoreRows

Parses the retail GT_TEAM per-client scoreboard block.
=================
*/
static void CG_ParseRetailTdmScoreRows( int rowStartArg ) {
	int i;
	int argc;

	argc = trap_Argc();
	for ( i = 0; i < cg.numScores; i++ ) {
		int baseArg;

		baseArg = rowStartArg + i * CG_RETAIL_TDM_SCORE_ROW_FIELDS;
		if ( argc <= ( baseArg + ( CG_RETAIL_TDM_SCORE_ROW_FIELDS - 1 ) ) ) {
			break;
		}

		cg.scores[i].client = atoi( CG_Argv( baseArg ) );
		cg.scores[i].team = atoi( CG_Argv( baseArg + 1 ) );
		cg.scores[i].score = atoi( CG_Argv( baseArg + 2 ) );
		cg.scores[i].ping = atoi( CG_Argv( baseArg + 3 ) );
		cg.scores[i].time = atoi( CG_Argv( baseArg + 4 ) );
		cg.scores[i].kills = atoi( CG_Argv( baseArg + 5 ) );
		cg.scores[i].deaths = atoi( CG_Argv( baseArg + 6 ) );
		cg.scores[i].accuracy = atoi( CG_Argv( baseArg + 7 ) );
		cg.scores[i].bestWeapon = atoi( CG_Argv( baseArg + 8 ) );
		cg.scores[i].impressiveCount = atoi( CG_Argv( baseArg + 9 ) );
		cg.scores[i].excellentCount = atoi( CG_Argv( baseArg + 10 ) );
		cg.scores[i].guantletCount = atoi( CG_Argv( baseArg + 11 ) );
		cg.scores[i].teamDamageGiven = atoi( CG_Argv( baseArg + 12 ) );
		cg.scores[i].teamDamageReceived = atoi( CG_Argv( baseArg + 13 ) );
		cg.scores[i].damage = atoi( CG_Argv( baseArg + 14 ) );
		cg.scores[i].activePlayer = ( cg.scores[i].team != TEAM_SPECTATOR ) ? qtrue : qfalse;

		CG_FinalizeParsedScoreRow( &cg.scores[i], -1 );
	}
}

/*
=================
CG_ParseRetailCtfScoreRows

Parses the retail shared CTF-family per-client scoreboard block.
=================
*/
static void CG_ParseRetailCtfScoreRows( int rowStartArg ) {
	int i;
	int argc;

	argc = trap_Argc();
	for ( i = 0; i < cg.numScores; i++ ) {
		int baseArg;

		baseArg = rowStartArg + i * CG_RETAIL_CTF_SCORE_ROW_FIELDS;
		if ( argc <= ( baseArg + ( CG_RETAIL_CTF_SCORE_ROW_FIELDS - 1 ) ) ) {
			break;
		}

		cg.scores[i].client = atoi( CG_Argv( baseArg ) );
		cg.scores[i].team = atoi( CG_Argv( baseArg + 1 ) );
		cg.scores[i].score = atoi( CG_Argv( baseArg + 2 ) );
		cg.scores[i].ping = atoi( CG_Argv( baseArg + 3 ) );
		cg.scores[i].time = atoi( CG_Argv( baseArg + 4 ) );
		cg.scores[i].kills = atoi( CG_Argv( baseArg + 5 ) );
		cg.scores[i].deaths = atoi( CG_Argv( baseArg + 6 ) );
		cg.scores[i].accuracy = atoi( CG_Argv( baseArg + 7 ) );
		cg.scores[i].bestWeapon = atoi( CG_Argv( baseArg + 8 ) );
		cg.scores[i].impressiveCount = atoi( CG_Argv( baseArg + 9 ) );
		cg.scores[i].excellentCount = atoi( CG_Argv( baseArg + 10 ) );
		cg.scores[i].guantletCount = atoi( CG_Argv( baseArg + 11 ) );
		cg.scores[i].defendCount = atoi( CG_Argv( baseArg + 12 ) );
		cg.scores[i].assistCount = atoi( CG_Argv( baseArg + 13 ) );
		cg.scores[i].captures = atoi( CG_Argv( baseArg + 14 ) );
		cg.scores[i].perfect = atoi( CG_Argv( baseArg + 15 ) );
		cg.scores[i].activePlayer = atoi( CG_Argv( baseArg + 16 ) ) ? qtrue : qfalse;

		CG_FinalizeParsedScoreRow( &cg.scores[i], -1 );
	}
}

/*
=================
CG_ParseRetailFreezeScoreRows

Parses the retail Freeze per-client scoreboard block.
=================
*/
static void CG_ParseRetailFreezeScoreRows( int rowStartArg ) {
	int i;
	int argc;

	argc = trap_Argc();
	for ( i = 0; i < cg.numScores; i++ ) {
		int baseArg;

		baseArg = rowStartArg + i * CG_RETAIL_FREEZE_SCORE_ROW_FIELDS;
		if ( argc <= ( baseArg + ( CG_RETAIL_FREEZE_SCORE_ROW_FIELDS - 1 ) ) ) {
			break;
		}

		cg.scores[i].client = atoi( CG_Argv( baseArg ) );
		cg.scores[i].team = atoi( CG_Argv( baseArg + 1 ) );
		cg.scores[i].score = atoi( CG_Argv( baseArg + 2 ) );
		cg.scores[i].ping = atoi( CG_Argv( baseArg + 3 ) );
		cg.scores[i].time = atoi( CG_Argv( baseArg + 4 ) );
		cg.scores[i].kills = atoi( CG_Argv( baseArg + 5 ) );
		cg.scores[i].deaths = atoi( CG_Argv( baseArg + 6 ) );
		cg.scores[i].accuracy = atoi( CG_Argv( baseArg + 7 ) );
		cg.scores[i].bestWeapon = atoi( CG_Argv( baseArg + 8 ) );
		cg.scores[i].impressiveCount = atoi( CG_Argv( baseArg + 9 ) );
		cg.scores[i].excellentCount = atoi( CG_Argv( baseArg + 10 ) );
		cg.scores[i].guantletCount = atoi( CG_Argv( baseArg + 11 ) );
		cg.scores[i].assistCount = atoi( CG_Argv( baseArg + 12 ) );
		cg.scores[i].teamDamageGiven = atoi( CG_Argv( baseArg + 13 ) );
		cg.scores[i].teamDamageReceived = atoi( CG_Argv( baseArg + 14 ) );
		cg.scores[i].damage = atoi( CG_Argv( baseArg + 15 ) );
		cg.scores[i].activePlayer = atoi( CG_Argv( baseArg + 16 ) ) ? qtrue : qfalse;

		CG_FinalizeParsedScoreRow( &cg.scores[i], -1 );
	}
}

/*
=================
CG_ParseRetailTeamScoreHeader

Parses the retail red/blue team aggregate header block carried by team-family
scoreboard payloads into the shared ownerdraw cache.
=================
*/
static void CG_ParseRetailTeamScoreHeader( int headerStartArg, const cgTeamStatIndex_t *statOrder, int statCount ) {
	int	arg;
	int	teamIndex;
	int	fieldIndex;
	int	maxField;

	if ( !statOrder || statCount <= 0 ) {
		return;
	}

	CG_ClearTeamScoreStatsCache();
	arg = headerStartArg;
	maxField = 0;
	for ( teamIndex = 0; teamIndex < 2; teamIndex++ ) {
		for ( fieldIndex = 0; fieldIndex < statCount; fieldIndex++ ) {
			cg.teamScoreStats.values[teamIndex][statOrder[fieldIndex]] = atoi( CG_Argv( arg++ ) );
			if ( statOrder[fieldIndex] > maxField ) {
				maxField = statOrder[fieldIndex];
			}
		}
	}

	cg.teamScoreStats.fieldCount = maxField + 1;
	cg.teamScoreStats.valid = qtrue;
	CG_DebugDumpTeamOwnerdrawScoreStats( cg.teamScoreStats.fieldCount );
}

/*
=================
CG_ParseScoreStats

Parses compact placement stats (weapon + pickup data) published by server.
=================
*/
static void CG_ParseScoreStats( void ) {
	int argc;
	int count;
	int arg;
	int i;

	CG_ClearScoreStatsCache();

	argc = trap_Argc();
	if ( argc < 2 ) {
		return;
	}

	count = atoi( CG_Argv( 1 ) );
	if ( count < 0 ) {
		count = 0;
	}
	if ( count > MAX_CLIENTS ) {
		count = MAX_CLIENTS;
	}

	arg = 2;
	for ( i = 0; i < count; i++ ) {
		int clientNum;
		int j;

		if ( arg >= argc ) {
			break;
		}
		if ( ( argc - arg ) < CG_SCORESTAT_FIELDS_PER_CLIENT ) {
			if ( cg_debugOwnerdrawStats.integer ) {
				CG_Printf(
					"ownerdraw_stats: truncated scorestats payload at index=%i remaining=%i expected=%i\n",
					i,
					argc - arg,
					CG_SCORESTAT_FIELDS_PER_CLIENT );
			}
			break;
		}

		clientNum = atoi( CG_Argv( arg++ ) );

		for ( j = 0; j < CG_SCORESTAT_FRAG_WEAPON_COUNT && arg < argc; j++ ) {
			int value;
			weapon_t weapon;

			value = atoi( CG_Argv( arg++ ) );
			weapon = cgScoreStatFragWeapons[j];
			if ( clientNum >= 0 && clientNum < MAX_CLIENTS && weapon > WP_NONE && weapon < WP_NUM_WEAPONS ) {
				cg.scoreStats[clientNum].weaponFrags[weapon] = value;
			}
		}

		for ( j = 0; j < CG_SCORESTAT_ACCURACY_WEAPON_COUNT && arg < argc; j++ ) {
			int value;
			weapon_t weapon;

			value = atoi( CG_Argv( arg++ ) );
			weapon = cgScoreStatAccuracyWeapons[j];
			if ( clientNum >= 0 && clientNum < MAX_CLIENTS && weapon > WP_NONE && weapon < WP_NUM_WEAPONS ) {
				cg.scoreStats[clientNum].weaponHits[weapon] = value;
			}
		}

		for ( j = 0; j < CG_SCORESTAT_ACCURACY_WEAPON_COUNT && arg < argc; j++ ) {
			int value;
			weapon_t weapon;

			value = atoi( CG_Argv( arg++ ) );
			weapon = cgScoreStatAccuracyWeapons[j];
			if ( clientNum >= 0 && clientNum < MAX_CLIENTS && weapon > WP_NONE && weapon < WP_NUM_WEAPONS ) {
				cg.scoreStats[clientNum].weaponShots[weapon] = value;
			}
		}

		for ( j = 0; j < CG_SCORESTAT_DMG_WEAPON_COUNT && arg < argc; j++ ) {
			int value;
			weapon_t weapon;

			value = atoi( CG_Argv( arg++ ) );
			weapon = cgScoreStatFragWeapons[j];
			if ( clientNum >= 0 && clientNum < MAX_CLIENTS && weapon > WP_NONE && weapon < WP_NUM_WEAPONS ) {
				cg.scoreStats[clientNum].weaponDamage[weapon] = value;
			}
		}

		for ( j = 0; j < CG_SCORESTAT_PICKUP_COUNT && arg < argc; j++ ) {
			int value;

			value = atoi( CG_Argv( arg++ ) );
			if ( value < 0 ) {
				value = 0;
			}
			if ( clientNum >= 0 && clientNum < MAX_CLIENTS ) {
				cg.scoreStats[clientNum].pickupCounts[j] = value;
			}
		}

		for ( j = 0; j < CG_SCORESTAT_PICKUP_COUNT && arg < argc; j++ ) {
			float value;

			value = (float)atof( CG_Argv( arg++ ) );
			if ( value < 0.0f ) {
				value = 0.0f;
			}
			if ( clientNum >= 0 && clientNum < MAX_CLIENTS ) {
				cg.scoreStats[clientNum].pickupAvgSeconds[j] = value;
			}
		}

		if ( arg < argc ) {
			int value;

			value = atoi( CG_Argv( arg++ ) );
			if ( value < 0 ) {
				value = 0;
			}
			if ( clientNum >= 0 && clientNum < MAX_CLIENTS ) {
				cg.scoreStats[clientNum].progressionPr = value;
			}
		}

		if ( arg < argc ) {
			int value;

			value = atoi( CG_Argv( arg++ ) );
			if ( value < 0 ) {
				value = 0;
			}
			if ( clientNum >= 0 && clientNum < MAX_CLIENTS ) {
				cg.scoreStats[clientNum].progressionTier = value;
			}
		}

		if ( clientNum >= 0 && clientNum < MAX_CLIENTS ) {
			cg.scoreStats[clientNum].valid = qtrue;
		}
	}

	CG_DebugDumpPlacementOwnerdrawScoreStats();
}

/*
=================
CG_ParseTeamScoreStats

Parses compact team pickup/time-held aggregates published by the server.
=================
*/
static void CG_ParseTeamScoreStats( void ) {
	int	argc;
	int	fieldCount;
	int	arg;
	int	teamIndex;
	int	fieldIndex;

	CG_ClearTeamScoreStatsCache();

	argc = trap_Argc();
	if ( argc < 2 ) {
		return;
	}

	fieldCount = atoi( CG_Argv( 1 ) );
	if ( fieldCount < 0 ) {
		fieldCount = 0;
	}
	if ( fieldCount > CG_TEAMSTAT_COUNT ) {
		fieldCount = CG_TEAMSTAT_COUNT;
	}
	if ( fieldCount <= 0 ) {
		return;
	}

	if ( argc < ( 2 + fieldCount * 2 ) ) {
		return;
	}

	arg = 2;
	for ( teamIndex = 0; teamIndex < 2; teamIndex++ ) {
		for ( fieldIndex = 0; fieldIndex < fieldCount; fieldIndex++ ) {
			cg.teamScoreStats.values[teamIndex][fieldIndex] = atoi( CG_Argv( arg++ ) );
		}
	}

	cg.teamScoreStats.fieldCount = fieldCount;
	cg.teamScoreStats.valid = qtrue;
	CG_DebugDumpTeamOwnerdrawScoreStats( fieldCount );
}

/*
=================
CG_ParseClanArenaStats

Consumes the retail castats row transport keyed by scoreboard row index.
=================
*/
static void CG_ParseClanArenaStats( void ) {
	int			argc;
	int			rowIndex;
	int			arg;
	int			weaponIndex;
	cgClanArenaStats_t	*row;

	argc = trap_Argc();
	if ( argc < 4 ) {
		return;
	}

	rowIndex = atoi( CG_Argv( 1 ) );
	if ( rowIndex < 0 || rowIndex >= MAX_CLIENTS ) {
		return;
	}

	row = &cg.clanArenaStats[rowIndex];
	memset( row, 0, sizeof( *row ) );
	row->damageGiven = atoi( CG_Argv( 2 ) );
	row->damageReceived = atoi( CG_Argv( 3 ) );

	arg = 4;
	for ( weaponIndex = 0; weaponIndex < CG_CASTAT_WEAPON_COUNT && ( arg + 1 ) < argc; weaponIndex++ ) {
		weapon_t weapon;

		weapon = cgCAStatWeapons[weaponIndex];
		if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
			arg += 2;
			continue;
		}

		row->weaponFrags[weapon] = atoi( CG_Argv( arg++ ) );
		row->weaponAccuracy[weapon] = atoi( CG_Argv( arg++ ) );
	}

	row->valid = qtrue;
}

/*
=================
CG_ParseTDMStats

Consumes the retail tdmstats row transport keyed by scoreboard row index.
=================
*/
static void CG_ParseTDMStats( void ) {
	int		argc;
	int		rowIndex;
	int		arg;
	int		fieldIndex;
	cgTdmStats_t	*row;

	argc = trap_Argc();
	if ( argc < ( 2 + CG_TDMSTAT_FIELD_COUNT ) ) {
		return;
	}

	rowIndex = atoi( CG_Argv( 1 ) );
	if ( rowIndex < 0 || rowIndex >= MAX_CLIENTS ) {
		return;
	}

	row = &cg.tdmStats[rowIndex];
	memset( row, 0, sizeof( *row ) );

	arg = 2;
	for ( fieldIndex = 0; fieldIndex < CG_TDMSTAT_FIELD_COUNT && arg < argc; fieldIndex++ ) {
		row->values[fieldIndex] = atoi( CG_Argv( arg++ ) );
	}

	row->valid = qtrue;
}

/*
=================
CG_ParseCTFStats

Consumes the retail ctfstats row transport keyed by scoreboard row index.
=================
*/
static void CG_ParseCTFStats( void ) {
	int		argc;
	int		rowIndex;
	int		arg;
	int		fieldIndex;
	cgCtfStats_t	*row;

	argc = trap_Argc();
	if ( argc < ( 2 + CG_CTFSTAT_FIELD_COUNT ) ) {
		return;
	}

	rowIndex = atoi( CG_Argv( 1 ) );
	if ( rowIndex < 0 || rowIndex >= MAX_CLIENTS ) {
		return;
	}

	row = &cg.ctfStats[rowIndex];
	memset( row, 0, sizeof( *row ) );

	arg = 2;
	for ( fieldIndex = 0; fieldIndex < CG_CTFSTAT_FIELD_COUNT && arg < argc; fieldIndex++ ) {
		row->values[fieldIndex] = atoi( CG_Argv( arg++ ) );
	}

	row->valid = qtrue;
}

/*
=================
CG_ParseKeyMask

Parses a single key-mask update for one client.
=================
*/
static void CG_ParseKeyMask( void ) {
	int	clientNum;
	int	mask;

	if ( trap_Argc() < 3 ) {
		return;
	}

	clientNum = atoi( CG_Argv( 1 ) );
	mask = atoi( CG_Argv( 2 ) );

	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return;
	}

	if ( mask < 0 ) {
		mask = 0;
	}

	cg.clientKeyMask[clientNum] = mask;
}

/*
=================
CG_ParseKeyMasks

Parses a full key-mask table snapshot for connected clients.
=================
*/
static void CG_ParseKeyMasks( void ) {
	int argc;
	int count;
	int arg;
	int i;

	memset( cg.clientKeyMask, 0, sizeof( cg.clientKeyMask ) );

	argc = trap_Argc();
	if ( argc < 2 ) {
		return;
	}

	count = atoi( CG_Argv( 1 ) );
	if ( count < 0 ) {
		count = 0;
	}
	if ( count > MAX_CLIENTS ) {
		count = MAX_CLIENTS;
	}

	arg = 2;
	for ( i = 0; i < count; i++ ) {
		int clientNum;
		int mask;

		if ( arg + 1 >= argc ) {
			break;
		}

		clientNum = atoi( CG_Argv( arg++ ) );
		mask = atoi( CG_Argv( arg++ ) );

		if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
			continue;
		}
		if ( mask < 0 ) {
			mask = 0;
		}

		cg.clientKeyMask[clientNum] = mask;
	}
}

/*
=================
CG_ParseCompactScores

Consumes the retail compact smscores payload, which uses an 8-column client
stride instead of the full 16-column scoreboard layout.
=================
*/
static void CG_ParseCompactScores( void ) {
	int		i;
	int		powerups;

	cg.numScores = atoi( CG_Argv( 1 ) );
	if ( cg.numScores > MAX_CLIENTS ) {
		cg.numScores = MAX_CLIENTS;
	}

	cg.teamScores[0] = atoi( CG_Argv( 2 ) );
	cg.teamScores[1] = atoi( CG_Argv( 3 ) );

	CG_ResetParsedScoreboardCaches();
	for ( i = 0 ; i < cg.numScores ; i++ ) {
		cg.scores[i].client = atoi( CG_Argv( i * 8 + 4 ) );
		cg.scores[i].score = atoi( CG_Argv( i * 8 + 5 ) );
		cg.scores[i].ping = atoi( CG_Argv( i * 8 + 6 ) );
		cg.scores[i].time = atoi( CG_Argv( i * 8 + 7 ) );
		powerups = atoi( CG_Argv( i * 8 + 8 ) );
		cg.scores[i].scoreFlags = 0;
		cg.scores[i].activePlayer = atoi( CG_Argv( i * 8 + 9 ) ) ? qtrue : qfalse;
		cg.scores[i].damage = atoi( CG_Argv( i * 8 + 10 ) );
		cg.scores[i].deaths = atoi( CG_Argv( i * 8 + 11 ) );
		cg.scores[i].kills = 0;
		cg.scores[i].bestWeapon = WP_NONE;
		cg.scores[i].team = TEAM_FREE;

		CG_FinalizeParsedScoreRow( &cg.scores[i], powerups );
	}

	CG_SetScoreSelection( NULL );
}

/*
=================
CG_ParseRichScoreboardPayload

=================
*/
static void CG_ParseRichScoreboardPayload( void ) {
	cg.numScores = atoi( CG_Argv( 1 ) );
	if ( cg.numScores > MAX_CLIENTS ) {
		cg.numScores = MAX_CLIENTS;
	}

	cg.teamScores[0] = atoi( CG_Argv( 2 ) );
	cg.teamScores[1] = atoi( CG_Argv( 3 ) );

	CG_ResetParsedScoreboardCaches();
	CG_ParseGenericScoreRows( 4, 16 );
	CG_SetScoreSelection(NULL);
}

/*
=================
CG_ParseFFAScores

Consumes the retail dedicated `scores_ffa` scoreboard transport while
preserving the shared rich-score payload layout.
=================
*/
static void CG_ParseFFAScores( void ) {
	CG_ParseRichScoreboardPayload();
}

/*
=================
CG_ParseScores

Consumes the retail generic `scores` scoreboard transport, which shares the
same rich per-client payload layout as `scores_ffa`.
=================
*/
static void CG_ParseScores( void ) {
	CG_ParseRichScoreboardPayload();
}

/*
=================
CG_ParseDuelScores

Consumes the retail duel scoreboard transport, which omits the generic
red/blue team-score header and packs a fixed per-player stat row.
=================
*/
static void CG_ParseDuelScores( void ) {
	int		i;
	int		argc;

	argc = trap_Argc();
	if ( argc < 2 ) {
		return;
	}

	cg.numScores = atoi( CG_Argv( 1 ) );
	if ( cg.numScores < 0 ) {
		cg.numScores = 0;
	}
	if ( cg.numScores > 2 ) {
		cg.numScores = 2;
	}
	if ( cg.numScores > MAX_CLIENTS ) {
		cg.numScores = MAX_CLIENTS;
	}

	cg.teamScores[0] = 0;
	cg.teamScores[1] = 0;

	CG_ResetParsedScoreboardCaches();
	for ( i = 0; i < cg.numScores; i++ ) {
		int	baseArg;
		int	clientNum;
		int	weaponArg;
		int	weaponIndex;
		weapon_t	weapon;

		baseArg = 2 + i * CG_RETAIL_DUEL_SCORE_ROW_FIELDS;
		if ( argc <= ( baseArg + ( CG_RETAIL_DUEL_SCORE_ROW_FIELDS - 1 ) ) ) {
			break;
		}

		cg.scores[i].client = atoi( CG_Argv( baseArg ) );
		cg.scores[i].score = atoi( CG_Argv( baseArg + 1 ) );
		cg.scores[i].ping = atoi( CG_Argv( baseArg + 2 ) );
		cg.scores[i].time = atoi( CG_Argv( baseArg + 3 ) );
		cg.scores[i].kills = atoi( CG_Argv( baseArg + 4 ) );
		cg.scores[i].deaths = atoi( CG_Argv( baseArg + 5 ) );
		cg.scores[i].accuracy = atoi( CG_Argv( baseArg + 6 ) );
		cg.scores[i].bestWeapon = atoi( CG_Argv( baseArg + 7 ) );
		cg.scores[i].damage = atoi( CG_Argv( baseArg + 8 ) );
		cg.scores[i].impressiveCount = atoi( CG_Argv( baseArg + 9 ) );
		cg.scores[i].excellentCount = atoi( CG_Argv( baseArg + 10 ) );
		cg.scores[i].guantletCount = atoi( CG_Argv( baseArg + 11 ) );
		cg.scores[i].activePlayer = atoi( CG_Argv( baseArg + 12 ) ) ? qtrue : qfalse;
		cg.scores[i].scoreFlags = 0;
		cg.scores[i].powerUps = 0;
		cg.scores[i].defendCount = 0;
		cg.scores[i].assistCount = 0;
		cg.scores[i].captures = 0;
		cg.scores[i].perfect = qfalse;
		cg.scores[i].team = TEAM_FREE;
		cg.scores[i].teamDamageGiven = 0;
		cg.scores[i].teamDamageReceived = 0;

		clientNum = cg.scores[i].client;
		if ( clientNum >= 0 && clientNum < MAX_CLIENTS ) {
			cg.scoreStats[clientNum].pickupCounts[CG_SCORESTAT_PICKUP_RA] = atoi( CG_Argv( baseArg + 13 ) );
			cg.scoreStats[clientNum].pickupAvgSeconds[CG_SCORESTAT_PICKUP_RA] = (float)atof( CG_Argv( baseArg + 14 ) );
			cg.scoreStats[clientNum].pickupCounts[CG_SCORESTAT_PICKUP_YA] = atoi( CG_Argv( baseArg + 15 ) );
			cg.scoreStats[clientNum].pickupAvgSeconds[CG_SCORESTAT_PICKUP_YA] = (float)atof( CG_Argv( baseArg + 16 ) );
			cg.scoreStats[clientNum].pickupCounts[CG_SCORESTAT_PICKUP_GA] = atoi( CG_Argv( baseArg + 17 ) );
			cg.scoreStats[clientNum].pickupAvgSeconds[CG_SCORESTAT_PICKUP_GA] = (float)atof( CG_Argv( baseArg + 18 ) );
			cg.scoreStats[clientNum].pickupCounts[CG_SCORESTAT_PICKUP_MH] = atoi( CG_Argv( baseArg + 19 ) );
			cg.scoreStats[clientNum].pickupAvgSeconds[CG_SCORESTAT_PICKUP_MH] = (float)atof( CG_Argv( baseArg + 20 ) );

			weaponArg = baseArg + CG_RETAIL_DUEL_CORE_FIELDS;
			for ( weaponIndex = 0; weaponIndex < ARRAY_LEN( cg_retailWeaponReloadOrder ); weaponIndex++ ) {
				weapon = cg_retailWeaponReloadOrder[weaponIndex];
				cg.scoreStats[clientNum].weaponFrags[weapon] = atoi( CG_Argv( weaponArg ) );
				cg.scoreStats[clientNum].weaponDamage[weapon] = atoi( CG_Argv( weaponArg + 1 ) );
				cg.scoreStats[clientNum].weaponShots[weapon] = atoi( CG_Argv( weaponArg + 3 ) );
				cg.scoreStats[clientNum].weaponHits[weapon] = atoi( CG_Argv( weaponArg + 4 ) );
				weaponArg += CG_RETAIL_DUEL_WEAPON_FIELDS;
			}
			cg.scoreStats[clientNum].valid = qtrue;
		}

		CG_FinalizeParsedScoreRow( &cg.scores[i], -1 );
	}

	CG_SetScoreSelection( NULL );
}

/*
=================
CG_ParseTdmScores

Consumes the retail team-family scoreboard transport, which prefixes 28
red/blue aggregate fields ahead of the current per-client row block.
=================
*/
static void CG_ParseTdmScores( void ) {
	if ( trap_Argc() < 32 ) {
		return;
	}

	CG_ResetParsedScoreboardCaches();
	CG_ParseRetailTeamScoreHeader( 1, cgRetailTdmTeamStatOrder, CG_RETAIL_TDM_TEAMSTAT_COUNT );

	cg.numScores = atoi( CG_Argv( 29 ) );
	if ( cg.numScores > MAX_CLIENTS ) {
		cg.numScores = MAX_CLIENTS;
	}

	cg.teamScores[0] = atoi( CG_Argv( 30 ) );
	cg.teamScores[1] = atoi( CG_Argv( 31 ) );

	CG_ParseRetailTdmScoreRows( 32 );
	CG_SetScoreSelection( NULL );
}

/*
=================
CG_ParseCtfScores

Consumes the retail shared CTF-family scoreboard transport, which prefixes 34
red/blue aggregate fields ahead of the current per-client row block.
=================
*/
static void CG_ParseCtfScores( void ) {
	if ( trap_Argc() < 38 ) {
		return;
	}

	CG_ResetParsedScoreboardCaches();
	CG_ParseRetailTeamScoreHeader( 1, cgRetailCtfTeamStatOrder, CG_RETAIL_CTF_TEAMSTAT_COUNT );

	cg.numScores = atoi( CG_Argv( 35 ) );
	if ( cg.numScores > MAX_CLIENTS ) {
		cg.numScores = MAX_CLIENTS;
	}

	cg.teamScores[0] = atoi( CG_Argv( 36 ) );
	cg.teamScores[1] = atoi( CG_Argv( 37 ) );

	CG_ParseRetailCtfScoreRows( 38 );
	CG_SetScoreSelection( NULL );
}

/*
=================
CG_ParseFreezeScores

Consumes the retail Freeze scoreboard transport, which shares the 28-field
team header with TDM but carries its own 17-column per-client row block.
=================
*/
static void CG_ParseFreezeScores( void ) {
	if ( trap_Argc() < 32 ) {
		return;
	}

	CG_ResetParsedScoreboardCaches();
	CG_ParseRetailTeamScoreHeader( 1, cgRetailTdmTeamStatOrder, CG_RETAIL_TDM_TEAMSTAT_COUNT );

	cg.numScores = atoi( CG_Argv( 29 ) );
	if ( cg.numScores > MAX_CLIENTS ) {
		cg.numScores = MAX_CLIENTS;
	}

	cg.teamScores[0] = atoi( CG_Argv( 30 ) );
	cg.teamScores[1] = atoi( CG_Argv( 31 ) );

	CG_ParseRetailFreezeScoreRows( 32 );
	CG_SetScoreSelection( NULL );
}

/*
=================
CG_ParseClanArenaScores

Consumes the retail Clan Arena scoreboard transport, which uses its own
16-column row layout instead of the generic rich-score block.
=================
*/
static void CG_ParseClanArenaScores( void ) {
	int	i;
	int	argc;

	argc = trap_Argc();
	if ( argc < 4 ) {
		return;
	}

	cg.numScores = atoi( CG_Argv( 1 ) );
	if ( cg.numScores < 0 ) {
		cg.numScores = 0;
	}
	if ( cg.numScores > MAX_CLIENTS ) {
		cg.numScores = MAX_CLIENTS;
	}

	cg.teamScores[0] = atoi( CG_Argv( 2 ) );
	cg.teamScores[1] = atoi( CG_Argv( 3 ) );

	CG_ResetParsedScoreboardCaches();
	for ( i = 0; i < cg.numScores; i++ ) {
		int	baseArg;

		baseArg = 4 + i * CG_RETAIL_CA_SCORE_ROW_FIELDS;
		if ( argc <= ( baseArg + ( CG_RETAIL_CA_SCORE_ROW_FIELDS - 1 ) ) ) {
			break;
		}

		cg.scores[i].client = atoi( CG_Argv( baseArg ) );
		cg.scores[i].team = atoi( CG_Argv( baseArg + 1 ) );
		cg.scores[i].score = atoi( CG_Argv( baseArg + 2 ) );
		cg.scores[i].ping = atoi( CG_Argv( baseArg + 3 ) );
		cg.scores[i].time = atoi( CG_Argv( baseArg + 4 ) );
		cg.scores[i].kills = atoi( CG_Argv( baseArg + 5 ) );
		cg.scores[i].deaths = atoi( CG_Argv( baseArg + 6 ) );
		cg.scores[i].accuracy = atoi( CG_Argv( baseArg + 7 ) );
		cg.scores[i].bestWeapon = atoi( CG_Argv( baseArg + 8 ) );
		// Retail carries one additional CA-only integer here that is not surfaced
		// through the recovered source HUD paths yet.
		cg.scores[i].damage = atoi( CG_Argv( baseArg + 10 ) );
		cg.scores[i].impressiveCount = atoi( CG_Argv( baseArg + 11 ) );
		cg.scores[i].excellentCount = atoi( CG_Argv( baseArg + 12 ) );
		cg.scores[i].guantletCount = atoi( CG_Argv( baseArg + 13 ) );
		cg.scores[i].perfect = atoi( CG_Argv( baseArg + 14 ) ) ? qtrue : qfalse;
		cg.scores[i].activePlayer = atoi( CG_Argv( baseArg + 15 ) ) ? qtrue : qfalse;
		cg.scores[i].scoreFlags = 0;
		cg.scores[i].powerUps = 0;
		cg.scores[i].defendCount = 0;
		cg.scores[i].assistCount = 0;
		cg.scores[i].captures = 0;
		cg.scores[i].teamDamageGiven = 0;
		cg.scores[i].teamDamageReceived = 0;

		CG_FinalizeParsedScoreRow( &cg.scores[i], -1 );
	}

	CG_SetScoreSelection( NULL );
}

/*
=================
CG_ParseRedRoverScores

Consumes the retail Red Rover scoreboard transport, which extends the
non-team row with kills, medals, and teamplay award counters.
=================
*/
static void CG_ParseRedRoverScores( void ) {
	int	i;
	int	argc;

	argc = trap_Argc();
	if ( argc < 4 ) {
		return;
	}

	cg.numScores = atoi( CG_Argv( 1 ) );
	if ( cg.numScores < 0 ) {
		cg.numScores = 0;
	}
	if ( cg.numScores > MAX_CLIENTS ) {
		cg.numScores = MAX_CLIENTS;
	}

	cg.teamScores[0] = atoi( CG_Argv( 2 ) );
	cg.teamScores[1] = atoi( CG_Argv( 3 ) );

	CG_ResetParsedScoreboardCaches();
	for ( i = 0; i < cg.numScores; i++ ) {
		int	baseArg;

		baseArg = 4 + i * CG_RETAIL_RR_SCORE_ROW_FIELDS;
		if ( argc <= ( baseArg + ( CG_RETAIL_RR_SCORE_ROW_FIELDS - 1 ) ) ) {
			break;
		}

		cg.scores[i].client = atoi( CG_Argv( baseArg ) );
		cg.scores[i].score = atoi( CG_Argv( baseArg + 1 ) );
		cg.scores[i].ping = atoi( CG_Argv( baseArg + 3 ) );
		cg.scores[i].time = atoi( CG_Argv( baseArg + 4 ) );
		cg.scores[i].kills = atoi( CG_Argv( baseArg + 5 ) );
		cg.scores[i].deaths = atoi( CG_Argv( baseArg + 6 ) );
		cg.scores[i].accuracy = atoi( CG_Argv( baseArg + 7 ) );
		cg.scores[i].bestWeapon = atoi( CG_Argv( baseArg + 8 ) );
		// Retail RR rows also carry auxiliary non-scoreboard integers that the
		// current recovered HUD does not read yet.
		cg.scores[i].damage = atoi( CG_Argv( baseArg + 10 ) );
		cg.scores[i].impressiveCount = atoi( CG_Argv( baseArg + 11 ) );
		cg.scores[i].excellentCount = atoi( CG_Argv( baseArg + 12 ) );
		cg.scores[i].guantletCount = atoi( CG_Argv( baseArg + 13 ) );
		cg.scores[i].defendCount = atoi( CG_Argv( baseArg + 14 ) );
		cg.scores[i].assistCount = atoi( CG_Argv( baseArg + 15 ) );
		cg.scores[i].activePlayer = atoi( CG_Argv( baseArg + 16 ) ) ? qtrue : qfalse;
		cg.scores[i].captures = atoi( CG_Argv( baseArg + 17 ) );
		cg.scores[i].scoreFlags = 0;
		cg.scores[i].powerUps = 0;
		cg.scores[i].perfect = qfalse;
		cg.scores[i].team = TEAM_FREE;
		cg.scores[i].teamDamageGiven = 0;
		cg.scores[i].teamDamageReceived = 0;

		CG_FinalizeParsedScoreRow( &cg.scores[i], -1 );
	}

	CG_SetScoreSelection( NULL );
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
==================
CG_ParseDisableLoadoutConfigString

Mirrors the retail loadout-disable configstring onto the per-weapon ROM cvars.
==================
*/
static void CG_ParseDisableLoadoutConfigString( const char *configstring ) {
	const cgDisableLoadoutToken_t	*entry;
	unsigned long			flags;
	char				*end;
	char				cvarName[MAX_CVAR_VALUE_STRING];
	char				currentValue[MAX_CVAR_VALUE_STRING];
	const char			*resolvedValue;

	flags = 0ul;
	if ( configstring && configstring[0] ) {
		flags = strtoul( configstring, &end, 0 );
		if ( end == configstring ) {
			flags = 0ul;
		}
	}

	for ( entry = cg_retailDisableLoadoutTokens; entry->token; ++entry ) {
		resolvedValue = ( flags & entry->mask ) ? "1" : "0";
		Com_sprintf( cvarName, sizeof( cvarName ), "cg_disableLoadout_%s", entry->token );
		trap_Cvar_VariableStringBuffer( cvarName, currentValue, sizeof( currentValue ) );
		if ( Q_stricmp( currentValue, resolvedValue ) ) {
			trap_Cvar_Set( cvarName, resolvedValue );
		}
	}
}

/*
=================
CG_SetGameInfoCvars

Publishes the six retail `cg_gameInfo*` HUD/menu cvars from the current
serverinfo state.
=================
*/
static void CG_SetGameInfoCvars( void ) {
	const char		*info;
	const char		*trainingValue;
	const char *const	*gameInfo;

	info = CG_ConfigString( CS_SERVERINFO );
	gameInfo = cg_retailBlankGameInfoLines;

	trainingValue = Info_ValueForKey( info, "g_training" );
	if ( trainingValue[0] && atoi( trainingValue ) ) {
		gameInfo = cg_retailTrainingGameInfoLines;
	} else if ( cgs.gametype >= 0 && cgs.gametype < GT_MAX_GAME_TYPE ) {
		gameInfo = cg_retailGameInfoLines[cgs.gametype];
	}

	trap_Cvar_Set( "cg_gameInfo1", gameInfo[0] );
	trap_Cvar_Set( "cg_gameInfo2", gameInfo[1] );
	trap_Cvar_Set( "cg_gameInfo3", gameInfo[2] );
	trap_Cvar_Set( "cg_gameInfo4", gameInfo[3] );
	trap_Cvar_Set( "cg_gameInfo5", gameInfo[4] );
	trap_Cvar_Set( "cg_gameInfo6", gameInfo[5] );
}

/*
========================
CG_NormalizeMapFilename

Maps legacy Quake 3 arena tokens onto the retail Quake Live BSP basenames.
========================
*/
static const char *CG_NormalizeMapFilename( const char *mapname ) {
	int	i;

	if ( !mapname || !mapname[0] ) {
		return "";
	}

	for ( i = 0; i < ARRAY_LEN( cg_retailMapAliases ); i++ ) {
		if ( !Q_stricmp( mapname, cg_retailMapAliases[i].legacyName ) ) {
			return cg_retailMapAliases[i].retailName;
		}
	}

	return mapname;
}


/*
================
CG_ParseFactoryTitleServerinfo

Refreshes the cached factory title from the serverinfo-backed g_factoryTitle key.
================
*/
static void CG_ParseFactoryTitleServerinfo( const char *info ) {
	const char	*value;
	int		start;
	int		end;
	int		length;

	cgs.factoryTitle[0] = '\0';
	value = info ? Info_ValueForKey( info, "g_factoryTitle" ) : "";
	if ( !value ) {
		return;
	}

	start = 0;
	while ( value[start] && (unsigned char)value[start] <= ' ' ) {
		start++;
	}

	end = (int)strlen( value );
	while ( end > start && (unsigned char)value[end - 1] <= ' ' ) {
		end--;
	}

	length = end - start;
	if ( length <= 0 ) {
		return;
	}

	if ( length >= (int)sizeof( cgs.factoryTitle ) ) {
		length = (int)sizeof( cgs.factoryTitle ) - 1;
	}

	Com_sprintf( cgs.factoryTitle, sizeof( cgs.factoryTitle ), "%.*s", length, value + start );
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
	const char	*mapname;
	const char	*voteFlagsValue;
	qboolean	mapVotingDisabled;
	const char	*serverLoadout;
	const char	*voteFlagsString;
	int		voteFlags;

	info = CG_ConfigString( CS_SERVERINFO );
	gametypeValue = Info_ValueForKey( info, "g_gametype" );
	cgs.gametype = atoi( gametypeValue );
	trap_Cvar_Set( "cg_gametype", gametypeValue );
	trap_Cvar_Set("g_gametype", va("%i", cgs.gametype));
	cgs.dmflags = atoi( Info_ValueForKey( info, "dmflags" ) );
	cgs.teamflags = atoi( Info_ValueForKey( info, "teamflags" ) );
	cgs.fraglimit = atoi( Info_ValueForKey( info, "fraglimit" ) );
	cgs.capturelimit = atoi( Info_ValueForKey( info, "capturelimit" ) );
	cgs.scorelimit = atoi( Info_ValueForKey( info, "g_scorelimit" ) );
	cgs.timelimit = atoi( Info_ValueForKey( info, "timelimit" ) );
	cgs.roundlimit = atoi( Info_ValueForKey( info, "roundlimit" ) );
	CG_SetGameInfoCvars();
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

	{
		const char	*playerCountTeamSizeValue;

		/*
		 * The player-count ownerdraws consume the serverinfo-facing `teamsize`
		 * transport. qagame now mirrors the internal `g_teamSizeMin` state through
		 * that alias so live admin and vote changes stay visible to cgame.
		 */
		playerCountTeamSizeValue = Info_ValueForKey( info, "teamsize" );
		cgs.playerCountTeamSize = playerCountTeamSizeValue[0] ? atoi( playerCountTeamSizeValue ) : 0;
		if ( cgs.playerCountTeamSize < 0 ) {
			cgs.playerCountTeamSize = 0;
		}
	}
  
	serverLoadout = Info_ValueForKey( info, "loadout" );
	if ( !serverLoadout || !serverLoadout[0] ) {
		serverLoadout = Info_ValueForKey( info, "g_loadout" );
	}
	if ( !serverLoadout ) {
		serverLoadout = "";
	}
	Q_strncpyz( cgs.loadout, serverLoadout, sizeof( cgs.loadout ) );
	trap_Cvar_Set( "cg_loadout", cgs.loadout );
	CG_ParseFactoryTitleServerinfo( info );

	mapname = CG_NormalizeMapFilename( Info_ValueForKey( info, "mapname" ) );
	Com_sprintf( cgs.mapname, sizeof( cgs.mapname ), "maps/%s.bsp", mapname );
	CG_SetTeamNameCvar( "g_redteam", Info_ValueForKey( info, "g_redTeam" ), DEFAULT_REDTEAM_NAME, cgs.redTeam, sizeof( cgs.redTeam ) );
	CG_SetTeamNameCvar( "g_blueteam", Info_ValueForKey( info, "g_blueTeam" ), DEFAULT_BLUETEAM_NAME, cgs.blueTeam, sizeof( cgs.blueTeam ) );

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
CG_ParsePlayerCylindersConfigString

Restores the retail dedicated player-cylinder configstring parser and mirrors
the shared collision-shape gate through cg_playerCylinders.
=============
*/
static void CG_ParsePlayerCylindersConfigString( void ) {
	const char	*info;
	const char	*value;

	info = CG_ConfigString( CS_PLAYER_CYLINDERS );
	value = ( info && info[0] ) ? va( "%i", atoi( info ) ) : "0";

	cgs.playerCylindersEnabled = (qboolean)( atoi( value ) != 0 );
	trap_Cvar_Set( "cg_playerCylinders", value );
	trap_Cvar_Update( &cg_playerCylinders );
}

/*
=============
CG_ParseArmorTieredConfigString

Restores the retail armor-tiering parser boundary and mirrors the reconstructed
server-settings payload through cg_armorTiered for shared gameplay consumers.
=============
*/
static void CG_ParseArmorTieredConfigString( void ) {
	const char	*info;
	const char	*value;

	info = CG_ConfigString( CS_SERVER_SETTINGS_INFO_A );
	value = ( info && info[0] ) ? Info_ValueForKey( info, "armor_tiered" ) : "";
	if ( !value[0] ) {
		value = "0";
	}

	cgs.serverSettingsArmorTiered = (qboolean)( atoi( value ) != 0 );
	cg.armorTieredEnabled = cgs.serverSettingsArmorTiered;
	trap_Cvar_Set( "cg_armorTiered", value );
	trap_Cvar_Update( &cg_armorTiered );
}

/*
=============
CG_ResetPlayerAppearanceState

Restores the retail forced-player appearance cache to the current defaults.
=============
*/
static void CG_ResetPlayerAppearanceState( void ) {
	cgs.playermodelOverride[0] = '\0';
	cgs.playerheadmodelOverride[0] = '\0';
	cgs.allowCustomHeadmodels = qfalse;
	cgs.playerHeadScale = 1.0f;
	cgs.playerHeadScaleOffset = 1.0f;
	cgs.playerModelScale = 1.1f;
}

/*
==================
CG_ParsePlayerAppearanceConfigString

Decodes the retail player-appearance payload that carries enforced model and
head overrides plus the shared head/model scale controls.
==================
*/
static void CG_ParsePlayerAppearanceConfigString( void ) {
	const char	*info;
	const char	*value;
	char		oldModelOverride[MAX_QPATH];
	char		oldHeadOverride[MAX_QPATH];
	qboolean	oldAllowCustomHeadmodels;
	float		oldPlayerModelScale;

	Q_strncpyz( oldModelOverride, cgs.playermodelOverride, sizeof( oldModelOverride ) );
	Q_strncpyz( oldHeadOverride, cgs.playerheadmodelOverride, sizeof( oldHeadOverride ) );
	oldAllowCustomHeadmodels = cgs.allowCustomHeadmodels;
	oldPlayerModelScale = cgs.playerModelScale;

	CG_ResetPlayerAppearanceState();

	info = CG_ConfigString( CS_PLAYER_APPEARANCE );
	if ( info && info[0] ) {
		value = Info_ValueForKey( info, "g_playermodelOverride" );
		if ( value && value[0] ) {
			Q_strncpyz( cgs.playermodelOverride, value, sizeof( cgs.playermodelOverride ) );
		}

		value = Info_ValueForKey( info, "g_playerheadmodelOverride" );
		if ( value && value[0] ) {
			Q_strncpyz( cgs.playerheadmodelOverride, value, sizeof( cgs.playerheadmodelOverride ) );
		}

		value = Info_ValueForKey( info, "g_allowCustomHeadmodels" );
		if ( value && value[0] ) {
			cgs.allowCustomHeadmodels = (qboolean)( atoi( value ) != 0 );
		}

		value = Info_ValueForKey( info, "g_playerheadScale" );
		if ( value && value[0] ) {
			cgs.playerHeadScale = (float)atof( value );
		}

		value = Info_ValueForKey( info, "g_playerheadScaleOffset" );
		if ( value && value[0] ) {
			cgs.playerHeadScaleOffset = (float)atof( value );
		}

		value = Info_ValueForKey( info, "g_playerModelScale" );
		if ( value && value[0] ) {
			cgs.playerModelScale = (float)atof( value );
		}
	}

	if ( Q_stricmp( oldModelOverride, cgs.playermodelOverride ) ||
		Q_stricmp( oldHeadOverride, cgs.playerheadmodelOverride ) ||
		oldAllowCustomHeadmodels != cgs.allowCustomHeadmodels ) {
		CG_ApplyModelOverrides();
	} else if ( oldPlayerModelScale != cgs.playerModelScale ) {
		CG_RefreshClientHeadOffsets();
	}
}

/*
==================
CG_ParseWeaponReloadConfigString

Decodes the retail compact weapon-refire timing slab into the live pmove cache.
==================
*/
static void CG_ParseWeaponReloadConfigString( void ) {
	const char	*payload;
	char		*cursor;
	int		parsed[ARRAY_LEN( cg_retailWeaponReloadOrder )];
	int		i;

	payload = CG_ConfigString( CS_WEAPON_RELOAD_TIMES );
	if ( !payload || !payload[0] ) {
		return;
	}

	cursor = (char *)payload;
	for ( i = 0; i < ARRAY_LEN( parsed ); ++i ) {
		const char *token;

		token = COM_ParseExt( &cursor, qfalse );
		if ( !token || !token[0] ) {
			return;
		}

		parsed[i] = atoi( token );
	}

	for ( i = 0; i < ARRAY_LEN( parsed ); ++i ) {
		cg_pmoveSettings.weaponReloadTimes[cg_retailWeaponReloadOrder[i]] = parsed[i];
	}
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

	cg_matchRoundStartTime = 0;
	cgs.matchOvertimeActive = qfalse;
	cgs.matchOvertimeStartTime = 0;
	cgs.matchOvertimeEndTime = 0;
	cgs.matchOvertimeCount = 0;
	cgs.matchTimeoutActive = qfalse;
	cgs.matchTimeoutTeam = TEAM_FREE;
	cgs.matchTimeoutExpireTime = 0;
	cgs.matchTimeoutOwner = -1;
	cg_matchTimeoutStartTime = 0;
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
CG_ParseRoundStartTimeConfigString

Caches the hidden retail round-start timestamp mirrored through slot `0x296`.
=============
*/
static void CG_ParseRoundStartTimeConfigString( void ) {
	const char	*info;

	info = CG_ConfigString( CS_ROUND_START_TIME );
	if ( !info || !*info ) {
		cg_matchRoundStartTime = 0;
		return;
	}

	cg_matchRoundStartTime = atoi( info );
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
CG_ParseTimeoutConfigStrings

Refreshes the retail timeout auxiliaries published alongside CS_MATCH_STATE.
=============
*/
static void CG_ParseTimeoutConfigStrings( void ) {
	const char	*info;
	int		value;

	info = CG_ConfigString( CS_TIMEOUT_START_TIME );
	value = ( info && *info ) ? atoi( info ) : 0;
	if ( value < 0 ) {
		value = 0;
	}
	cg_matchTimeoutStartTime = value;

	info = CG_ConfigString( CS_TIMEOUT_EXPIRE_TIME );
	value = ( info && *info ) ? atoi( info ) : 0;
	if ( value < 0 ) {
		value = 0;
	}
	cgs.matchTimeoutExpireTime = value;

	info = CG_ConfigString( CS_TIMEOUT_COUNT_RED );
	if ( info && *info ) {
		value = atoi( info );
	} else {
		value = cgs.matchTimeoutCountPerTeam;
	}
	if ( value < 0 ) {
		value = 0;
	}
	cgs.matchTimeoutRemaining[TEAM_RED] = value;

	info = CG_ConfigString( CS_TIMEOUT_COUNT_BLUE );
	if ( info && *info ) {
		value = atoi( info );
	} else {
		value = cgs.matchTimeoutCountPerTeam;
	}
	if ( value < 0 ) {
		value = 0;
	}
	cgs.matchTimeoutRemaining[TEAM_BLUE] = value;
}

/*
=============
CG_ParseTeamCountConfigStrings

Refreshes the retail team-count auxiliaries mirrored for round HUD widgets.
=============
*/
static void CG_ParseTeamCountConfigStrings( void ) {
	const char	*info;
	int		value;

	info = CG_ConfigString( CS_TEAM_COUNT_RED );
	value = ( info && *info ) ? atoi( info ) : 0;
	if ( value < 0 ) {
		value = 0;
	}
	cgs.matchTeamCount[TEAM_RED] = value;

	info = CG_ConfigString( CS_TEAM_COUNT_BLUE );
	value = ( info && *info ) ? atoi( info ) : 0;
	if ( value < 0 ) {
		value = 0;
	}
	cgs.matchTeamCount[TEAM_BLUE] = value;
}

static void CG_ParseSuddenDeathStatus( void );

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
	qboolean wasOvertimeActive;
	int previousOvertimeCount;

	wasOvertimeActive = cgs.matchOvertimeActive;
	previousOvertimeCount = cgs.matchOvertimeCount;

	CG_ResetMatchStateFields();

	info = CG_ConfigString( CS_MATCH_STATE );
	if ( !info || !*info ) {
		CG_ParseTimeoutConfigStrings();
		CG_ParseTeamCountConfigStrings();
		return;
	}

	cgs.matchRoundTransitionTime = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TIME, 0 );
	cgs.matchRoundNumber = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_ROUND, 0 );
	cgs.matchRoundTurn = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_TURN, 0 );
	cgs.matchRoundState = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_STATE, 0 );
	cgs.matchOvertimeActive = CG_InfoIntForMatchKey( info, MATCH_STATE_KEY_OVERTIME_ACTIVE, 0 ) ? qtrue : qfalse;
	cgs.matchSuddenDeathActive = cgs.matchOvertimeActive;
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
	CG_ParseTimeoutConfigStrings();
	CG_ParseTeamCountConfigStrings();
	CG_ParseSuddenDeathStatus();

	if ( cgs.matchOvertimeActive ) {
		cg.timelimitWarnings |= 4;
		if ( ( !wasOvertimeActive || cgs.matchOvertimeCount > previousOvertimeCount ) && cgs.media.overtimeSound ) {
			trap_S_StartLocalSound( cgs.media.overtimeSound, CHAN_ANNOUNCER );
		}
	}
}

/*
=============
CG_ParseSuddenDeathStatus

Parses the dedicated sudden-death status latch published alongside the match
state payload and falls back to the match-state overtime flag when absent.
=============
*/
static void CG_ParseSuddenDeathStatus( void ) {
	const char	*info;
	int		value;

	info = CG_ConfigString( CS_SUDDENDEATH_STATUS );
	value = ( info && *info ) ? atoi( info ) : ( cgs.matchOvertimeActive ? 1 : 0 );

	cgs.matchSuddenDeathActive = value ? qtrue : qfalse;
}

/*
=============
 CG_ParseIntermissionExitStatus

Parses the retail intermission-exit latch published through configstring 0x2C3.
=============
*/
static void CG_ParseIntermissionExitStatus( void ) {
	const char	*info;
	int		value;

	info = CG_ConfigString( CS_INTERMISSION_EXIT_STATUS );
	value = ( info && *info ) ? atoi( info ) : 0;

	cgs.intermissionExitStatusLatched = value ? qtrue : qfalse;
}

/*
=============
CG_ParseReadyUpStatus

Parses the ready-up deadline published by the match controller.
=============
*/
static void CG_ParseReadyUpStatus( void ) {
	const char	*info;
	int		deadline;

	info = CG_ConfigString( CS_READYUP_STATUS );
	deadline = ( info && *info ) ? atoi( info ) : 0;
	if ( deadline < 0 ) {
		deadline = 0;
	}

	cgs.matchReadyUpDeadline = deadline;
}

/*
=============
CG_ParseWarmupReadyStatus

Parses the warmup readiness snapshot for HUD consumers.
=============
*/
static void CG_ParseWarmupReadyStatus( void ) {
	const char	*info;
	int		value;

	cgs.matchWarmupReadyPercent = 0;
	cgs.matchWarmupReadyCount = 0;
	cgs.matchWarmupReadyEligible = 0;

	info = CG_ConfigString( CS_WARMUP_READY );
	if ( !info || !*info ) {
		return;
	}

	value = atoi( Info_ValueForKey( info, "pct" ) );
	if ( value < 0 ) {
		value = 0;
	} else if ( value > 100 ) {
		value = 100;
	}
	cgs.matchWarmupReadyPercent = value;

	value = atoi( Info_ValueForKey( info, "ready" ) );
	if ( value < 0 ) {
		value = 0;
	}
	cgs.matchWarmupReadyCount = value;

	value = atoi( Info_ValueForKey( info, "eligible" ) );
	if ( value < 0 ) {
		value = 0;
	}
	cgs.matchWarmupReadyEligible = value;

	if ( cgs.matchWarmupReadyCount > cgs.matchWarmupReadyEligible ) {
		cgs.matchWarmupReadyCount = cgs.matchWarmupReadyEligible;
	}
}

/*
=============
CG_ParseSharedRaceDominationConfigStrings

Parses the retail shared Race/Domination auxiliary slots according to the active gametype.
=============
*/
static void CG_ParseSharedRaceDominationConfigStrings( void ) {
	const char	*info;
	int		value;

	cgs.dominationOwnedPointCount[TEAM_RED] = 0;
	cgs.dominationOwnedPointCount[TEAM_BLUE] = 0;

	if ( cgs.gametype == GT_RACE ) {
		CG_ParseRaceInfoString( CG_ConfigString( CS_RACE_INFO ) );
		CG_ParseRaceStatusString( CG_ConfigString( CS_RACE_STATUS ) );
		return;
	}

	CG_ParseRaceInit();
	if ( cgs.gametype != GT_DOMINATION && cgs.gametype != GT_ATTACK_DEFEND ) {
		return;
	}

	info = CG_ConfigString( CS_RACE_STATUS );
	value = ( info && *info ) ? atoi( info ) : 0;
	if ( value < 0 ) {
		value = 0;
	}
	cgs.dominationOwnedPointCount[TEAM_RED] = value;

	info = CG_ConfigString( CS_RACE_INFO );
	value = ( info && *info ) ? atoi( info ) : 0;
	if ( value < 0 ) {
		value = 0;
	}
	cgs.dominationOwnedPointCount[TEAM_BLUE] = value;
}

/*
=============
CG_GetMatchTimeoutStartTime

Returns the timeout start timestamp mirrored through CS_TIMEOUT_START_TIME.
=============
*/
int CG_GetMatchTimeoutStartTime( void ) {
	return cg_matchTimeoutStartTime;
}

/*
=============
CG_GetMatchRoundStartTime

Returns the hidden retail round-start timestamp mirrored through slot `0x296`.
=============
*/
int CG_GetMatchRoundStartTime( void ) {
	return cg_matchRoundStartTime;
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
		CG_CenterPrint( "Server enforced the compact scoreboard message.", SCREEN_HEIGHT * 0.30f, 0.25f );
	} else if ( !forceScoreboard && previousScoreboard ) {
		CG_CenterPrint( "Server restored your scoreboard message preference.", SCREEN_HEIGHT * 0.30f, 0.25f );
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
=============
CG_ParseFreezeTipConfigstrings

Caches the Freeze Tag tutorial tips from configstrings.
=============
*/
static void CG_ParseFreezeTipConfigstrings( void ) {
	const char	*tip;

	tip = CG_ConfigString( CS_FREEZE_TIP_OBJECTIVE );
	if ( tip && *tip ) {
		Q_strncpyz( cgs.freezeTipObjective, tip, sizeof( cgs.freezeTipObjective ) );
	} else {
		cgs.freezeTipObjective[0] = '\0';
	}

	tip = CG_ConfigString( CS_FREEZE_TIP_THAW );
	if ( tip && *tip ) {
		Q_strncpyz( cgs.freezeTipThaw, tip, sizeof( cgs.freezeTipThaw ) );
	} else {
		cgs.freezeTipThaw[0] = '\0';
	}

	tip = CG_ConfigString( CS_FREEZE_TIP_FREEZE );
	if ( tip && *tip ) {
		Q_strncpyz( cgs.freezeTipFreeze, tip, sizeof( cgs.freezeTipFreeze ) );
	} else {
		cgs.freezeTipFreeze[0] = '\0';
	}

	tip = CG_ConfigString( CS_FREEZE_TIP_SHOOT );
	if ( tip && *tip ) {
		Q_strncpyz( cgs.freezeTipShoot, tip, sizeof( cgs.freezeTipShoot ) );
	} else {
		cgs.freezeTipShoot[0] = '\0';
	}

	tip = CG_ConfigString( CS_FREEZE_TIP_SUMMARY );
	if ( tip && *tip ) {
		Q_strncpyz( cgs.freezeTipSummary, tip, sizeof( cgs.freezeTipSummary ) );
	} else {
		cgs.freezeTipSummary[0] = '\0';
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

Refreshes the cached factory flag metadata from the latest configstrings. The
matching title remains serverinfo-backed.
==================
*/
static void CG_ParseFactoryMetadata( void ) {
	const char *info;

	info = CG_ConfigString( CS_FACTORY_FLAGS );
	if ( info && *info ) {
		cgs.factoryFlags = (unsigned int)atoi( info );
	} else {
		cgs.factoryFlags = 0u;
	}

	cgs.factorySpawnHints[0] = '\0';
}

/*
==================
CG_ParseCustomSettingsConfigString

Decodes the retail custom-settings mask published by qagame.
==================
*/
static void CG_ParseCustomSettingsConfigString( void ) {
	const char		*info;
	char			*end;
	unsigned long long	value;

	info = CG_ConfigString( CS_CUSTOM_SETTINGS );
	if ( !info || !info[0] ) {
		cgs.customSettingsMask = 0ull;
		return;
	}

	value = strtoull( info, &end, 0 );
	if ( end == info ) {
		cgs.customSettingsMask = 0ull;
		return;
	}

	cgs.customSettingsMask = value;
}

/*
==================
CG_ParseServerSettingsInfoConfigStrings

Refreshes the retail server-settings scalar payloads used by the settings ownerdraw.
The adjacent armor-tiering toggle keeps its dedicated retail parser boundary.
==================
*/
static void CG_ParseServerSettingsInfoConfigStrings( void ) {
	const char	*info;
	const char	*value;

	info = CG_ConfigString( CS_SERVER_SETTINGS_INFO_B );
	value = ( info && info[0] ) ? Info_ValueForKey( info, "g_quadDamageFactor" ) : "";
	cgs.serverSettingsQuadFactor = value[0] ? atoi( value ) : 3;

	value = ( info && info[0] ) ? Info_ValueForKey( info, "g_gravity" ) : "";
	cgs.serverSettingsGravity = value[0] ? atoi( value ) : 800;
}

/*
==================
CG_ParseEnableBreathConfigString

Mirrors the retail CS_ENABLE_BREATH latch into the existing local cvar-backed
breath gate used by CG_BreathPuffs.
==================
*/
static void CG_ParseEnableBreathConfigString( const char *configstring ) {
	const char	*value;

	value = ( configstring && configstring[0] ) ? va( "%i", atoi( configstring ) ) : "0";
	trap_Cvar_Set( "g_enableBreath", value );
	trap_Cvar_Update( &cg_enableBreath );
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

/*
=================
CG_SetRotationVoteSlotCvar

Formats and updates one of the retail endgame-vote UI helper cvars.
=================
*/
static void CG_SetRotationVoteSlotCvar( int slot, const char *suffix, const char *value ) {
	char	key[MAX_CVAR_VALUE_STRING];

	if ( !suffix || !suffix[0] || slot < 0 || slot >= 3 ) {
		return;
	}

	Com_sprintf( key, sizeof( key ), "ui_vote%s%i", suffix, slot + 1 );
	trap_Cvar_Set( key, ( value && value[0] ) ? value : "" );
}

/*
=================
CG_ParseRotationVoteConfigStrings

Mirrors the retail intermission next-map preview payloads into the UI helper
cvars consumed by the `endgamevote.menu` ownerdraws.
=================
*/
static void CG_ParseRotationVoteConfigStrings( void ) {
	const char	*rotationTitles;
	const char	*rotationCounts;
	int			slot;

	rotationTitles = CG_ConfigString( CS_ROTATION_TITLES );
	rotationCounts = CG_ConfigString( CS_ROTATION_CONFIGS );

	for ( slot = 0; slot < 3; slot++ ) {
		char	infoKey[16];
		char	mapName[MAX_QPATH];
		char	voteName[MAX_CVAR_VALUE_STRING];
		char	voteGametype[MAX_CVAR_VALUE_STRING];
		char	voteCount[16];
		char	voteShot[MAX_QPATH];
		const char	*value;

		Com_sprintf( infoKey, sizeof( infoKey ), "map_%i", slot );
		value = Info_ValueForKey( rotationTitles, infoKey );
		Q_strncpyz( mapName, value ? value : "", sizeof( mapName ) );

		Com_sprintf( infoKey, sizeof( infoKey ), "title_%i", slot );
		value = Info_ValueForKey( rotationTitles, infoKey );
		Q_strncpyz( voteName, value ? value : "", sizeof( voteName ) );
		if ( !voteName[0] ) {
			Q_strncpyz( voteName, mapName, sizeof( voteName ) );
		}

		Com_sprintf( infoKey, sizeof( infoKey ), "gt_%i", slot );
		value = Info_ValueForKey( rotationTitles, infoKey );
		Q_strncpyz( voteGametype, value ? value : "", sizeof( voteGametype ) );

		Com_sprintf( infoKey, sizeof( infoKey ), "%i", slot );
		value = Info_ValueForKey( rotationCounts, infoKey );
		if ( value && value[0] ) {
			Q_strncpyz( voteCount, value, sizeof( voteCount ) );
		} else if ( mapName[0] ) {
			Q_strncpyz( voteCount, "0", sizeof( voteCount ) );
		} else {
			voteCount[0] = '\0';
		}

		if ( mapName[0] ) {
			Q_strncpyz( voteShot, mapName, sizeof( voteShot ) );
		} else {
			voteShot[0] = '\0';
		}

		CG_SetRotationVoteSlotCvar( slot, "Map", mapName );
		CG_SetRotationVoteSlotCvar( slot, "Name", voteName );
		CG_SetRotationVoteSlotCvar( slot, "Gametype", voteGametype );
		CG_SetRotationVoteSlotCvar( slot, "Count", voteCount );
		CG_SetRotationVoteSlotCvar( slot, "Shot", voteShot );
	}
}

void CG_SetConfigValues( void ) {
	const char *s;

	cgs.scores1 = atoi( CG_ConfigString( CS_SCORES1 ) );
	cgs.scores2 = atoi( CG_ConfigString( CS_SCORES2 ) );
	cgs.levelStartTime = atoi( CG_ConfigString( CS_LEVEL_START_TIME ) );
	cgs.voteTime = atoi( CG_ConfigString( CS_VOTE_TIME ) );
	cgs.voteYes = atoi( CG_ConfigString( CS_VOTE_YES ) );
	cgs.voteNo = atoi( CG_ConfigString( CS_VOTE_NO ) );
	Q_strncpyz( cgs.voteString, CG_ConfigString( CS_VOTE_STRING ), sizeof( cgs.voteString ) );
	trap_Cvar_Set( "ui_voteactive", cgs.voteTime ? "1" : "0" );
	trap_Cvar_Set( "ui_votestring", cgs.voteString );
	CG_ParseRotationVoteConfigStrings();
	CG_SetTeamNameFromConfigString( TEAM_RED, CG_ConfigString( CS_RED_TEAM_NAME ) );
	CG_SetTeamNameFromConfigString( TEAM_BLUE, CG_ConfigString( CS_BLUE_TEAM_NAME ) );
	CG_ParseDisableLoadoutConfigString( CG_ConfigString( CS_LOADOUT_FLAGS ) );
	CG_ParseEnableBreathConfigString( CG_ConfigString( CS_ENABLE_BREATH ) );
	if( cgs.gametype == GT_CTF || cgs.gametype == GT_ATTACK_DEFEND || cgs.gametype == GT_OBELISK ) {
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
	CG_ParseRoundStartTimeConfigString();
	CG_ParseTimeoutConfigStrings();
	CG_ParseTeamCountConfigStrings();
	CG_ParseSuddenDeathStatus();
	CG_ParseIntermissionExitStatus();
	CG_ParseReadyUpStatus();
	CG_ParseWarmupReadyStatus();
	CG_ParseForcedCosmetics();
	CG_ParseFreezeTipConfigstrings();
	CG_ParsePlayerCylindersConfigString();
	CG_ParseFactoryMetadata();
	CG_ParseCustomSettingsConfigString();
	CG_ParseArmorTieredConfigString();
	CG_ParseServerSettingsInfoConfigStrings();
	CG_ParsePlayerAppearanceConfigString();
	CG_ParsePmoveConfigString( CG_ConfigString( CS_PMOVE_SETTINGS ) );
	CG_ParseWeaponReloadConfigString();
	CG_ParseSharedRaceDominationConfigStrings();
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
	} else if ( num == CS_ROUND_START_TIME ) {
		CG_ParseRoundStartTimeConfigString();
	} else if ( num == CS_TEAM_COUNT_RED || num == CS_TEAM_COUNT_BLUE ) {
		CG_ParseTeamCountConfigStrings();
	} else if ( num == CS_TIMEOUT_START_TIME || num == CS_TIMEOUT_EXPIRE_TIME ||
		num == CS_TIMEOUT_COUNT_RED || num == CS_TIMEOUT_COUNT_BLUE ) {
		CG_ParseTimeoutConfigStrings();
	} else if ( num == CS_INTERMISSION_EXIT_STATUS || num == CS_SUDDENDEATH_STATUS ) {
		CG_ParseSuddenDeathStatus();
		CG_ParseIntermissionExitStatus();
	} else if ( num == CS_READYUP_STATUS ) {
		CG_ParseReadyUpStatus();
	} else if ( num == CS_WARMUP_READY ) {
		CG_ParseWarmupReadyStatus();
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
	} else if ( num == CS_LOADOUT_FLAGS ) {
		CG_ParseDisableLoadoutConfigString( str );
	} else if ( num == CS_ENABLE_BREATH ) {
		CG_ParseEnableBreathConfigString( str );
	} else if ( num == CS_PLAYER_CYLINDERS ) {
		CG_ParsePlayerCylindersConfigString();
	} else if ( num == CS_FACTORY_FLAGS ) {
		CG_ParseFactoryMetadata();
	} else if ( num == CS_CUSTOM_SETTINGS ) {
		CG_ParseCustomSettingsConfigString();
	} else if ( num == CS_SERVER_SETTINGS_INFO_A ) {
		CG_ParseArmorTieredConfigString();
	} else if ( num == CS_SERVER_SETTINGS_INFO_B ) {
		CG_ParseServerSettingsInfoConfigStrings();
	} else if ( num == CS_PLAYER_APPEARANCE ) {
		CG_ParsePlayerAppearanceConfigString();
	} else if ( num == CS_FORCED_COSMETICS ) {
		CG_ParseForcedCosmetics();
	} else if ( num >= CS_FREEZE_TIP_OBJECTIVE && num <= CS_FREEZE_TIP_SUMMARY ) {
		CG_ParseFreezeTipConfigstrings();
	} else if ( num == CS_RACE_INFO || num == CS_RACE_STATUS ) {
		CG_ParseSharedRaceDominationConfigStrings();
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
		trap_Cvar_Set( "ui_votestring", cgs.voteString );
		trap_S_StartLocalSound( cgs.media.voteNow, CHAN_ANNOUNCER );
	} else if ( num == CS_ROTATION_TITLES || num == CS_ROTATION_CONFIGS ) {
		CG_ParseRotationVoteConfigStrings();
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
		if ( num - CS_PLAYERS == cg.clientNum ) {
			CG_QueueClientInfoContextRefresh();
		}

		CG_NewClientInfo( num - CS_PLAYERS );
		CG_BuildSpectatorString();
	} else if ( num == CS_FLAGSTATUS ) {
	if( cgs.gametype == GT_CTF || cgs.gametype == GT_ATTACK_DEFEND || cgs.gametype == GT_OBELISK ) {
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
} else if ( num == CS_WEAPON_RELOAD_TIMES ) {
CG_ParseWeaponReloadConfigString();
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
	if ( cg_teamChatBeep.integer && cgs.media.talkSound ) {
		trap_S_StartLocalSound( cgs.media.talkSound, CHAN_LOCAL_SOUND );
	}

	CG_PushPrintString( str, TEAMCHAT_PRINT, 0 );
}

/*
=================
CG_ParseBufferedChat

Mirrors the retail bchat servercmd: beep, print the line, and push it
through the timed buffered-chat stack with a server-supplied hold time.
=================
*/
static void CG_ParseBufferedChat( void ) {
	char	text[MAX_SAY_TEXT];
	int		holdTime;

	if ( cgs.media.talkSound ) {
		trap_S_StartLocalSound( cgs.media.talkSound, CHAN_LOCAL_SOUND );
	}

	Q_strncpyz( text, CG_Argv( 1 ), sizeof( text ) );
	CG_RemoveChatEscapeChar( text );
	CG_Printf( "%s\n", text );

	holdTime = atoi( CG_Argv( 2 ) ) * 1000;
	CG_PushPrintString( text, SYSTEM_PRINT, holdTime );
}

/*
=================
CG_ParseClearChat

Resets the buffered chat ring in response to the retail clearChat servercmd.
=================
*/
static void CG_ParseClearChat( void ) {
	CG_InitTeamChat();
}

/*
=================
CG_ParseUiPriv

Compatibility alias for older local servercmd payloads that still spell the
retail privilege bridge as `ui_priv` instead of `priv`.
=================
*/
static void CG_ParseUiPriv( void ) {
	trap_Cvar_Set( "ui_priv", CG_Argv( 1 ) );
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
	CG_ClearQueuedWorldMarkers();
	CG_InitMarkPolys();
	CG_ClearParticles ();

	// make sure the "3 frags left" warnings play again
	cg.fraglimitWarnings = 0;

	cg.timelimitWarnings = 0;
	cg.itemPickup = 0;
	cg.itemPickupTime = 0;
	cg.itemPickupBlendTime = 0;
	cg.attackerTime = 0;

	cg.intermissionStarted = qfalse;
	cg.intermissionLetterboxChangeTime = 0;
	cg.intermissionLetterboxDuration = 0;
	cg.intermissionLetterboxStartHeight = 0.0f;
	cg.intermissionLetterboxTargetHeight = 0.0f;

	cgs.voteTime = 0;
	cgs.voteYes = 0;
	cgs.voteNo = 0;
	cgs.voteString[0] = '\0';
	trap_Cvar_Set( "ui_voteactive", "0" );
	trap_Cvar_Set( "ui_votestring", "" );
	cg.complaintClient = -1;
	cg.complaintEndTime = 0;
	memset( cg.adScoreHistory, 0, sizeof( cg.adScoreHistory ) );
	CG_ClearBufferedAnnouncements();

	cg.mapRestart = qtrue;

	CG_StartMusic();

	trap_S_ClearLoopingSounds(qtrue);

	// we really should clear more parts of cg here and stop sounds

	// play the "fight" sound if this is a restart without warmup
	if ( cg.warmup == 0 /* && cgs.gametype == GT_TOURNAMENT */) {
		trap_S_StartLocalSound( cgs.media.countFightSound, CHAN_ANNOUNCER );
		CG_CenterPrint( "FIGHT!", 120, 0.5f );
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
			Menus_OpenByName( "voiceMenu" );
			cg.voiceMenuTime = cg.time;
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

	CG_SetClientSpeakingState( clientNum, qtrue );

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
CG_HasActiveComplaintPrompt
=================
*/
static qboolean CG_HasActiveComplaintPrompt( void ) {
	return ( cg.complaintClient >= 0 && cg.complaintEndTime > cg.time ) ? qtrue : qfalse;
}

/*
=================
CG_IsServerChatClientMuted
=================
*/
static qboolean CG_IsServerChatClientMuted( int clientNum ) {
	const clientInfo_t	*ci;

	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return qfalse;
	}

	ci = &cgs.clientinfo[clientNum];
	cg.clientMuted[clientNum] = trap_QL_IsClientMuted( ci->identityLow, ci->identityHigh ) ? qtrue : qfalse;

	return cg.clientMuted[clientNum];
}

/*
=================
CG_ResolveServerChatText
=================
*/
static const char *CG_ResolveServerChatText( int *clientNum ) {
	int		parsedClientNum;

	if ( clientNum ) {
		*clientNum = -1;
	}

	if ( trap_Argc() < 3 ) {
		return NULL;
	}

	parsedClientNum = atoi( CG_Argv( 1 ) );
	if ( parsedClientNum < 0 || parsedClientNum >= MAX_CLIENTS ) {
		return NULL;
	}

	if ( clientNum ) {
		*clientNum = parsedClientNum;
	}

	return CG_Argv( 2 );
}

/*
=================
CG_ParseCenterPrint
=================
*/
static void CG_ParseCenterPrint( qboolean printToConsole ) {
	const char	*text;
	int		y;

	text = CG_Argv( 1 );
	y = ( cg.warmup == 0 ) ? 90 : 144;
	CG_CenterPrint( text, y, 0.4f );

	if ( printToConsole ) {
		CG_Printf( "%s", text );
	}
}

/*
=================
CG_ParsePrint
=================
*/
static void CG_ParsePrint( void ) {
	const char	*text;

	CG_PushPrintString( CG_Argv(1), SYSTEM_PRINT, 0 );
	text = CG_Argv( 1 );
	CG_Printf( "%s", text );

	if ( !Q_stricmpn( text, "vote failed", 11 ) || !Q_stricmpn( text, "team vote failed", 16 ) ) {
		trap_S_StartLocalSound( cgs.media.voteFailed, CHAN_ANNOUNCER );
	} else if ( !Q_stricmpn( text, "vote passed", 11 ) || !Q_stricmpn( text, "team vote passed", 16 ) ) {
		trap_S_StartLocalSound( cgs.media.votePassed, CHAN_ANNOUNCER );
	}
}

/*
=================
CG_ParseChat
=================
*/
static void CG_ParseChat( void ) {
	const char	*message;
	int		clientNum;
	char		text[MAX_SAY_TEXT];

	if ( cg_teamChatsOnly.integer ) {
		return;
	}

	message = CG_ResolveServerChatText( &clientNum );
	if ( !message ) {
		return;
	}

	if ( CG_IsServerChatClientMuted( clientNum ) ) {
		return;
	}

	if ( cg_chatbeep.integer && cgs.media.talkSound ) {
		trap_S_StartLocalSound( cgs.media.talkSound, CHAN_LOCAL_SOUND );
	}

	Q_strncpyz( text, message, sizeof( text ) );
	CG_RemoveChatEscapeChar( text );
	CG_PushPrintString( text, CHAT_PRINT, 0 );
	CG_Printf( "%s\n", text );
}

/*
=================
CG_ParseTeamChat
=================
*/
static void CG_ParseTeamChat( void ) {
	const char	*message;
	int		clientNum;
	char		text[MAX_SAY_TEXT];

	message = CG_ResolveServerChatText( &clientNum );
	if ( !message ) {
		return;
	}

	if ( CG_IsServerChatClientMuted( clientNum ) ) {
		return;
	}

	Q_strncpyz( text, message, sizeof( text ) );
	CG_RemoveChatEscapeChar( text );
	CG_AddToTeamChat( text );
	CG_Printf( "%s\n", text );
}

/*
=================
CG_ParseClearSounds
=================
*/
static void CG_ParseClearSounds( void ) {
	trap_S_ClearLoopingSounds( qtrue );
}

/*
=================
CG_ParsePriv
=================
*/
static void CG_ParsePriv( void ) {
	trap_Cvar_Set( "ui_priv", CG_Argv( 1 ) );
}

/*
=================
CG_ParsePStats
=================
*/
static void CG_ParsePStats( void ) {
	CG_ParseRetailAccuracyCommand();
}

/*
=================
CG_ParseComplaint
=================
*/
static void CG_ParseComplaint( void ) {
	int		value;

	if ( trap_Argc() < 2 ) {
		return;
	}

	if ( CG_HasActiveComplaintPrompt() ) {
		return;
	}

	value = atoi( CG_Argv( 1 ) );
	cg.complaintClient = value;
	cg.complaintEndTime = cg.time + ( ( value < 0 ) ? 10000 : 15000 );
}

/*
=================
CG_SetVoteUIActive
=================
*/
static void CG_SetVoteUIActive( qboolean active ) {
	trap_Cvar_Set( "ui_voteactive", active ? "1" : "0" );
}

/*
=================
CG_ParseADScoreHistory
=================
*/
static qboolean CG_ParseADScoreHistory( void ) {
	int		i;

	if ( trap_Argc() != ( CG_AD_SCORE_HISTORY_LENGTH + 3 ) ) {
		return qfalse;
	}

	for ( i = 0; i < CG_AD_SCORE_HISTORY_LENGTH; i++ ) {
		cg.adScoreHistory[i] = atoi( CG_Argv( i + 1 ) );
	}
	cg.teamScores[0] = atoi( CG_Argv( CG_AD_SCORE_HISTORY_LENGTH + 1 ) );
	cg.teamScores[1] = atoi( CG_Argv( CG_AD_SCORE_HISTORY_LENGTH + 2 ) );

	return qtrue;
}

/*
=================
CG_ParseADScores
=================
*/
static void CG_ParseADScores( void ) {
	if ( CG_ParseADScoreHistory() ) {
		return;
	}

	CG_ParseCtfScores();
}

/*
=================
CG_ParseScreenshot
=================
*/
static void CG_ParseScreenshot( void ) {
	if ( trap_Argc() > 1 ) {
		trap_SendConsoleCommand( va( "screenshotJPEG \"%s\"\n", CG_Argv( 1 ) ) );
	} else {
		trap_SendConsoleCommand( "screenshotJPEG\n" );
	}
}

/*
=================
CG_ParseRecord
=================
*/
static void CG_ParseRecord( void ) {
	if ( trap_Argc() > 1 ) {
		trap_SendConsoleCommand( va( "record \"%s\"\n", CG_Argv( 1 ) ) );
	} else {
		trap_SendConsoleCommand( "record\n" );
	}
}

/*
=================
CG_ParseStopRecord
=================
*/
static void CG_ParseStopRecord( void ) {
	trap_SendConsoleCommand( "stoprecord; wait\n" );
}

/*
=================
CG_ParsePlayMusic
=================
*/
static void CG_ParsePlayMusic( void ) {
	if ( trap_Argc() > 1 ) {
		trap_S_StartBackgroundTrack( CG_Argv(1), CG_Argv(2) );
	}
}

/*
=================
CG_ParseStopMusic
=================
*/
static void CG_ParseStopMusic( void ) {
	trap_S_StopBackgroundTrack();
}

/*
=================
CG_ParsePlaySound
=================
*/
static void CG_ParsePlaySound( void ) {
	if ( trap_Argc() > 1 ) {
		trap_S_StartLocalSound( trap_S_RegisterSound( CG_Argv( 1 ), qfalse ), CHAN_LOCAL_SOUND );
	}
}

/*
=================
CG_ServerCommandCompatibility
=================
*/
static qboolean CG_ServerCommandCompatibility( const char *cmd ) {
	if ( !strcmp( cmd, "itemcfg" ) ) {
		int	enabled;
		int	height;

		enabled = 0;
		height = ITEM_TIMER_DEFAULT_HEIGHT;
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
		return qtrue;
	}

	if ( !Q_stricmpn( cmd, "admin_race_point_", 17 ) ) {
		CG_ParseAdminRacePoint( cmd );
		return qtrue;
	}

	if ( !strcmp( cmd, "vchat" ) ) {
		CG_VoiceChat( SAY_ALL );
		return qtrue;
	}

	if ( !strcmp( cmd, "vtchat" ) ) {
		CG_VoiceChat( SAY_TEAM );
		return qtrue;
	}

	if ( !strcmp( cmd, "vtell" ) ) {
		CG_VoiceChat( SAY_TELL );
		return qtrue;
	}

	if ( !strcmp( cmd, "scorestats" ) ) {
		CG_ParseScoreStats();
		return qtrue;
	}

	if ( !strcmp( cmd, "scorestats_team" ) ) {
		CG_ParseTeamScoreStats();
		return qtrue;
	}

	if ( !strcmp( cmd, "keymask" ) ) {
		CG_ParseKeyMask();
		return qtrue;
	}

	if ( !strcmp( cmd, "keymasks" ) ) {
		CG_ParseKeyMasks();
		return qtrue;
	}

	if ( !Q_stricmp( cmd, "remapShader" ) ) {
		if ( trap_Argc() == 4 ) {
			trap_R_RemapShader( CG_Argv( 1 ), CG_Argv( 2 ), CG_Argv( 3 ) );
		}
		return qtrue;
	}

	if ( !strcmp( cmd, "ui_priv" ) ) {
		CG_ParseUiPriv();
		return qtrue;
	}

	if ( !strcmp( cmd, "loaddefered" ) ) {
		CG_LoadDeferredPlayers();
		return qtrue;
	}

	return qfalse;
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

	cmd = CG_Argv(0);

	if ( !cmd[0] ) {
		// server claimed the command
		return;
	}

	if ( !strcmp( cmd, "cs" ) ) {
		CG_ConfigStringModified();
		return;
	}

	if ( !strcmp( cmd, "screenshot" ) ) {
		CG_ParseScreenshot();
		return;
	}

	if ( !strcmp( cmd, "record" ) ) {
		CG_ParseRecord();
		return;
	}

	if ( !strcmp( cmd, "stoprecord" ) ) {
		CG_ParseStopRecord();
		return;
	}

	if ( !strcmp( cmd, "cp" ) ) {
		CG_ParseCenterPrint( qfalse );
		return;
	}

	if ( !strcmp( cmd, "pcp" ) ) {
		CG_ParseCenterPrint( qtrue );
		return;
	}

	/* Retail buffered writer leaves retained in the parse helpers:
	CG_PushPrintString( CG_Argv(1), SYSTEM_PRINT, 0 );
	CG_PushPrintString( text, CHAT_PRINT, 0 );
	CG_PushPrintString( text, TEAMCHAT_PRINT, 0 );
	*/
	if ( !strcmp( cmd, "print" ) ) {
		CG_ParsePrint();
		return;
	}

	if ( !strcmp( cmd, "chat" ) ) {
		CG_ParseChat();
		return;
	}

	if ( !strcmp( cmd, "bchat" ) ) {
		CG_ParseBufferedChat();
		return;
	}

	if ( !strcmp( cmd, "clearChat" ) ) {
		CG_ParseClearChat();
		return;
	}

	if ( !strcmp( cmd, "ui_priv" ) ) {
		CG_ParseUiPriv();
		return;
	}

	if ( !strcmp( cmd, "playSound" ) ) {
		CG_ParsePlaySound();
		return;
	}

	if ( !strcmp( cmd, "playMusic" ) ) {
		CG_ParsePlayMusic();
		return;
	}

	if ( !strcmp( cmd, "stopMusic" ) ) {
		CG_ParseStopMusic();
		return;
	}

	if ( !strcmp( cmd, "clearSounds" ) ) {
		CG_ParseClearSounds();
		return;
	}

	if ( !strcmp( cmd, "tchat" ) ) {
		CG_ParseTeamChat();
		return;
	}

	if ( !strcmp( cmd, "priv" ) ) {
		CG_ParsePriv();
		return;
	}

	if ( !strcmp( cmd, "scores_ffa" ) ) {
		CG_ParseFFAScores();
		return;
	}

	if ( !strcmp( cmd, "scores_duel" ) ) {
		CG_ParseDuelScores();
		return;
	}

	if ( !strcmp( cmd, "scores_race" ) ) {
		CG_ParseRaceScores();
		return;
	}

	if ( !strcmp( cmd, "scores_tdm" ) ) {
		CG_ParseTdmScores();
		return;
	}

	if ( !strcmp( cmd, "scores_ca" ) ) {
		CG_ParseClanArenaScores();
		return;
	}

	if ( !strcmp( cmd, "scores_ctf" ) ) {
		CG_ParseCtfScores();
		return;
	}

	if ( !strcmp( cmd, "scores_ft" ) ) {
		CG_ParseFreezeScores();
		return;
	}

	if ( !strcmp( cmd, "scores_ad" ) ) {
		CG_ParseADScores();
		return;
	}

	if ( !strcmp( cmd, "adscores" ) ) {
		CG_ParseADScores();
		return;
	}

	if ( !strcmp( cmd, "scores_rr" ) ) {
		CG_ParseRedRoverScores();
		return;
	}

	if ( !strcmp( cmd, "tdmstats" ) ) {
		CG_ParseTDMStats();
		return;
	}

	if ( !strcmp( cmd, "castats" ) ) {
		CG_ParseClanArenaStats();
		return;
	}

	if ( !strcmp( cmd, "ctfstats" ) ) {
		CG_ParseCTFStats();
		return;
	}

	if ( !strcmp( cmd, "smscores" ) ) {
		CG_ParseCompactScores();
		return;
	}

	if ( !strcmp( cmd, "scores" ) ) {
		CG_ParseScores();
		return;
	}

	if ( !strcmp( cmd, "acc" ) ) {
		CG_ParseAcc();
		return;
	}

	if ( !strcmp( cmd, "pstats" ) ) {
		CG_ParsePStats();
		return;
	}

	if ( !strcmp( cmd, "tinfo" ) ) {
		CG_ParseTeamInfo();
		return;
	}

	if ( !strcmp( cmd, "race_info" ) ) {
		CG_ParseRaceInfo();
		return;
	}

	if ( !strcmp( cmd, "race_init" ) ) {
		CG_ParseRaceInit();
		return;
	}

	if ( !strcmp( cmd, "complaint" ) ) {
		CG_ParseComplaint();
		return;
	}

	if ( !strcmp( cmd, "enable_vote_ui" ) ) {
		CG_SetVoteUIActive( qtrue );
		return;
	}

	if ( !strcmp( cmd, "disable_vote_ui" ) ) {
		CG_SetVoteUIActive( qfalse );
		return;
	}

	if ( !strcmp( cmd, "map_restart" ) ) {
		CG_MapRestart();
		return;
	}

	if ( !strcmp( cmd, "loaddeferred" ) ) {
		CG_LoadDeferredPlayers();
		return;
	}

	// clientLevelShot is sent before taking a special screenshot for
	// the menu system during development
	if ( !strcmp( cmd, "clientLevelShot" ) ) {
		if ( trap_Cvar_VariableValue( "sv_running" ) > 0.0f ) {
			cg.levelShot = qtrue;
		}
		return;
	}

	if ( CG_ServerCommandCompatibility( cmd ) ) {
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
