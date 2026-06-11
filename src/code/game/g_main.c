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
#include "g_config.h"
#include "g_match_config.h"
#include "g_legacy_cvars.h"
#include "../game/match_state_keys.h"
#include "generated/ql_gametype_strings.h"
#include <limits.h>
#include <stdint.h>
#include "../../../src-re/include/ql_types.h"
#include <time.h>
#include <stdlib.h>

#ifndef ARRAY_LEN
#define ARRAY_LEN( x ) ( sizeof( x ) / sizeof( (x)[0] ) )
#endif

#define MAX_ADMIN_ACCESS_FILE_BYTES	8192
#define GAME_STATE_BUFFER_LENGTH		16
#define RANK_EVENT_PAYLOAD_MAX		16384
#define AUTO_RECORD_BASENAME_MAX	256
#define AUTO_RECORD_TOKEN_MAX		40
#define VF_NO_ENDVOTE			0x0800
#define GAME_CVAR_FLAG_RETAIL_10000	0x00010000
#define GAME_CVAR_FLAG_RETAIL_20000	0x00020000
#define GAME_CVAR_FLAG_RETAIL_40000	0x00040000
#define DEFAULT_FLAG_DROPPED_TIMEOUT_MS	30000
#define DEFAULT_REDTEAM_NAME		"Stroggs"
#define DEFAULT_BLUETEAM_NAME		"Pagans"
#define RANK_POWERUPS_FIRST_RETAIL	PW_INVIS
#define RANK_POWERUPS_LAST_RETAIL	MAX_POWERUPS

#define AUTO_RECORD_STATE_RECORDING	( 1 << 0 )
#define AUTO_RECORD_STATE_SCREENSHOT	( 1 << 1 )

level_locals_t	level;
weaponConfig_t	g_weaponConfig;
flagConfig_t	g_flagConfig;


typedef struct {
	vmCvar_t	*vmCvar;
	char		*cvarName;
	char		*defaultString;
	int			cvarFlags;
	int			modificationCount;  // for tracking changes
	qboolean	trackChange;	    // track this variable, and announce if changed
	qboolean	teamShader;	    // track and if changed, update shader state
	const char	*helpString; // optional help text advertised alongside the cvar
	qboolean	customSetting; // counts toward g_customSettings when true
} cvarTable_t;

gentity_t		g_entities[MAX_GENTITIES];
gclient_t		g_clients[MAX_CLIENTS];

static qlr_game_frame_context_t *g_qlr_frame_ctx = NULL;
static int	s_itemTimersModCount = 0;
static int	s_itemHeightModCount = 0;
static int	s_lastItemTimerEnabled = -1;
static int	s_lastItemTimerHeight = -1;
static int	s_forceSmallScoreboardMessageModCount = -1;
static int	s_forceSendConfigstringModCount = -1;
static int	s_forceAtmosphericEffectsModCount = -1;
static int	s_forceDmgThroughSurfaceModCount = -1;
static int	s_armorTieredModCount = -1;
static int	s_disableLoadoutModCount = 0;
static int	s_loadoutModCount = 0;
static int	s_startingWeaponsModCount = 0;
static int	s_factoryModCount = 0;
static int	s_inactivityModCount = 0;
static int	s_roundWarmupDelayModCount = 0;
static int	s_teamSizeMinModCount = 0;
static char	s_worldspawnAtmosphere[MAX_QPATH];
static char	s_lastForcedCosmeticsPayload[MAX_INFO_STRING];
static char	s_playerCylindersPayload[32];
static char	s_serverSettingsInfoPayloadA[MAX_INFO_STRING];
static char	s_serverSettingsInfoPayloadB[MAX_INFO_STRING];
static char	s_weaponReloadPayload[MAX_INFO_STRING];
static char	s_playerAppearancePayload[MAX_INFO_STRING];
static char	s_gameStateBuffer[GAME_STATE_BUFFER_LENGTH];
static char	s_dominationCaptureTimePayload[32];
static char	s_rrInfectedSurvivorPingRatePayload[32];
static char	s_customSettingsPayload[MAX_INFO_STRING];
static qboolean s_customSettingsDirty = qtrue;
static uint64_t s_lastCustomSettingsMask = 0;
static int	s_autoRecordState = 0;
static char	s_autoRecordBasename[AUTO_RECORD_BASENAME_MAX];
static int	s_adminAccessEntryCount = 0;
static adminAccessEntry_t	s_adminAccessList[MAX_ADMIN_ACCESS_ENTRIES];
static const char *s_duelSpawnGrantScript = "weapon_gauntlet weapon_machinegun ammo_bullets 100";
static vmCvar_t	g_teamSizeLegacy;
static legacyCvarAlias_t	s_legacyCvarAliases[] = {
	{ &g_teamSizeMin, "g_teamSizeMin", &g_teamSizeLegacy, "teamsize", "0", CVAR_SERVERINFO | CVAR_NORESTART, -1, -1 }
};

static qlr_game_frame_context_t *G_GetFrameContext( void );
static void G_RunFrameTimeoutAdvance( int msec );
static void G_DispatchScheduledThinks( qlr_game_frame_context_t *ctx, int msec );
static void G_StepEntities( qlr_game_frame_context_t *ctx );
static void G_DispatchEvents( qlr_game_frame_context_t *ctx );
static void G_FinishClientFrames( qlr_game_frame_context_t *ctx );
static void G_RunFrameRoundModeCountHooks( void );
static void G_CheckLevelTimers( qlr_game_frame_context_t *ctx, int previousWarmupTime, int previousIntermissionQueued );
static void G_RunFrameGametypeHooks( void );
static void G_UpdateTrainingState( void );
static void G_UpdateGametypeTutorialText( void );
static void G_InitPublishedCvarState( void );
static void G_InitLevelCvarMirrors( void );
static void G_SyncAdminConfig( void );
static void G_ResetAdminAccessList( void );
static void G_UpdateGameStateForLevel( void );
static void G_SyncAllClientArmorTiers( void );
static void G_SyncPlayerCylinderClientFlags( void );
static qboolean G_ParseAdminAccessTier( const char *token, int *tierOut );
static const char *G_AdminAccessTierToken( int tier );
static const char *G_AdminAccessTierLabel( int tier );
static void G_LoadAdminAccessFile( void );
static void G_WriteAdminAccessFile( void );
static void G_PrintAccessListLine( gentity_t *ent, const char *line );
static void G_UpdatePlayerCylindersConfigstring( qboolean forceBroadcast );
static void G_UpdateServerSettingsInfoConfigstrings( qboolean forceBroadcast );
static void G_UpdateWeaponReloadConfigstring( qboolean forceBroadcast );
static void G_UpdatePlayerAppearanceConfigstring( qboolean forceBroadcast );
static void G_UpdateModeSpecificConfigstrings( qboolean forceBroadcast );
static uint64_t G_ComputeCustomSettingsMask( void );
static void G_UpdateCustomSettingsConfigstring( qboolean forceBroadcast );
static void G_UpdateCustomSettingsMaskForCvar( const cvarTable_t *cv );
static void G_PublishWarmupReadyConfigstring( int readyCount, int eligibleCount, int readyMask );
static void G_CountAndSortConnectedClients( int *numNonSpectatorClients, int *numConnectedClients, int *follow1, int *follow2, int *numPlayingClients, int *sortedClients );
void G_SuddenDeathThink( void );

/*
=============
G_SelectForcedAtmosphere

Selects the highest priority forced atmosphere token to publish to clients.
=============
*/
static const char *G_SelectForcedAtmosphere( void ) {
	if ( g_forceAtmosphericEffects.string[0] ) {
		return g_forceAtmosphericEffects.string;
	}

	if ( s_worldspawnAtmosphere[0] ) {
		return s_worldspawnAtmosphere;
	}

	return "";
}

/*
=============
G_ReadServerTeamName

Reads the retail serverinfo team-name cvars without registering the removed
lowercase qagame aliases.
=============
*/
static void G_ReadServerTeamName( team_t team, char *buffer, int bufferSize ) {
	const char	*cvarName;
	const char	*fallback;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	if ( team == TEAM_BLUE ) {
		cvarName = SERVERINFO_KEY_BLUE_TEAM;
		fallback = DEFAULT_BLUETEAM_NAME;
	} else {
		cvarName = SERVERINFO_KEY_RED_TEAM;
		fallback = DEFAULT_REDTEAM_NAME;
	}

	trap_Cvar_VariableStringBuffer( cvarName, buffer, bufferSize );
	if ( !buffer[0] ) {
		Q_strncpyz( buffer, fallback, bufferSize );
	}
}

/*
=============
G_UpdateForcedCosmeticsConfigstring

Rebuilds the forced cosmetics payload and broadcasts it to all clients when requested.
=============
*/
void G_UpdateForcedCosmeticsConfigstring( qboolean forceBroadcast ) {
	char		info[MAX_INFO_STRING];
	const char	*atmosphere;
	qboolean	shouldBroadcast;

	info[0] = '\0';

	Info_SetValueForKey( info, FORCED_COSMETICS_KEY_SMALL_SCOREBOARD, g_forceSmallScoreboardMessage.integer ? "1" : "0" );
	Info_SetValueForKey( info, FORCED_COSMETICS_KEY_HUD, g_forceSendConfigstring.integer ? "1" : "0" );
	Info_SetValueForKey( info, FORCED_COSMETICS_KEY_DAMAGE, g_forceDmgThroughSurface.integer ? "1" : "0" );

	atmosphere = G_SelectForcedAtmosphere();
	if ( atmosphere && atmosphere[0] ) {
		Info_SetValueForKey( info, FORCED_COSMETICS_KEY_ATMOSPHERE, atmosphere );
	}

	shouldBroadcast = forceBroadcast;
	if ( !shouldBroadcast && Q_stricmp( info, s_lastForcedCosmeticsPayload ) ) {
		shouldBroadcast = qtrue;
	}

	if ( !shouldBroadcast ) {
		return;
	}

	trap_SetConfigstring( CS_FORCED_COSMETICS, info );
	Q_strncpyz( s_lastForcedCosmeticsPayload, info, sizeof( s_lastForcedCosmeticsPayload ) );
}

/*
=============
G_SetWorldspawnAtmosphere

Caches the worldspawn-provided atmosphere token and refreshes the broadcast payload.
=============
*/
void G_SetWorldspawnAtmosphere( const char *atmosphere ) {
	if ( atmosphere && atmosphere[0] ) {
		Q_strncpyz( s_worldspawnAtmosphere, atmosphere, sizeof( s_worldspawnAtmosphere ) );
	} else {
		s_worldspawnAtmosphere[0] = '\0';
	}

	G_UpdateForcedCosmeticsConfigstring( qtrue );
}

/*
=============
G_SetGameState

Writes the provided state token to the g_gameState CVar when it changes.
=============
*/
void G_SetGameState( const char *state ) {
	const char	*value;

	value = ( state && state[0] ) ? state : GAME_STATE_PRE_GAME;

	if ( !Q_stricmp( s_gameStateBuffer, value ) ) {
		return;
	}

	trap_Cvar_Set( "g_gameState", value );
	Q_strncpyz( s_gameStateBuffer, value, sizeof( s_gameStateBuffer ) );
}

/*
=============
G_ShortGametypeName

Returns the compact retail gametype label used by the auto-record basename
builder.
=============
*/
static const char *G_ShortGametypeName( int gametype ) {
	switch ( gametype ) {
	case GT_FFA:
		return "FFA";
	case GT_TOURNAMENT:
		return "DUEL";
	case GT_RACE:
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
		break;
	}

	return "ERR";
}

/*
=============
G_SanitizeFilenameToken

Matches the retail auto-record sanitizer so match media basenames only keep the
safe filename subset and collapse empty results to `invalid`.
=============
*/
static char *G_SanitizeFilenameToken( char *dst, const char *src ) {
	char		*out;
	int		count;
	unsigned char	ch;

	if ( !dst ) {
		return NULL;
	}

	out = dst;
	count = 0;
	ch = ( src && src[0] ) ? (unsigned char)src[0] : 0;

	while ( ch && count < ( AUTO_RECORD_TOKEN_MAX - 1 ) ) {
		if ( ch == '^' ) {
			if ( src[1] ) {
				src++;
			}
			src++;
			ch = (unsigned char)*src;
			continue;
		}

		if ( ch > 0x20 && ch < 0x7f ) {
			switch ( ch ) {
			case '#':
			case '$':
			case '%':
			case '&':
			case '(':
			case ')':
			case '+':
			case ',':
			case '-':
			case ';':
			case '=':
			case '@':
			case '[':
			case ']':
			case '_':
			case '`':
			case '{':
				*out++ = (char)ch;
				count++;
				break;
			default:
				if ( ( ch >= '0' && ch <= '9' )
					|| ( ch >= 'A' && ch <= 'Z' )
					|| ( ch >= 'a' && ch <= 'z' ) ) {
					*out++ = (char)ch;
					count++;
				}
				break;
			}
		}

		src++;
		ch = (unsigned char)*src;
	}

	*out = '\0';

	if ( out == dst ) {
		strncpy( dst, "invalid", AUTO_RECORD_TOKEN_MAX - 1 );
		dst[AUTO_RECORD_TOKEN_MAX - 1] = '\0';
	}

	return dst;
}

/*
=============
G_BuildAutoRecordBasename

Reconstructs the retail record/screenshot basename family used by the
ClientConnect late-join path and the match media controller.
=============
*/
static char *G_BuildAutoRecordBasename( gentity_t *ent ) {
	char		tokenA[AUTO_RECORD_TOKEN_MAX];
	char		tokenB[AUTO_RECORD_TOKEN_MAX];
	char		mapToken[AUTO_RECORD_TOKEN_MAX];
	char		mapName[MAX_QPATH];
	qtime_t		now;
	int		clientNum;

	s_autoRecordBasename[0] = '\0';

	if ( !ent || !ent->client ) {
		return s_autoRecordBasename;
	}

	clientNum = ent - g_entities;

	if ( g_gametype.integer == GT_TOURNAMENT ) {
		int		duelLow;
		int		duelHigh;
		const char	*lowName;
		const char	*highName;

		duelLow = ( level.numConnectedClients > 0 ) ? level.sortedClients[0] : -1;
		duelHigh = ( level.numConnectedClients > 1 ) ? level.sortedClients[1] : -1;

		lowName = ( duelLow >= 0 && duelLow < level.maxclients )
			? level.clients[duelLow].pers.netname
			: ent->client->pers.netname;
		highName = ( duelHigh >= 0 && duelHigh < level.maxclients )
			? level.clients[duelHigh].pers.netname
			: lowName;

		G_SanitizeFilenameToken( tokenA, lowName );
		G_SanitizeFilenameToken( tokenB, highName );

		if ( clientNum == duelLow ) {
			Com_sprintf( s_autoRecordBasename, sizeof( s_autoRecordBasename ), "%s(POV)-vs-%s", tokenA, tokenB );
		} else if ( clientNum == duelHigh ) {
			Com_sprintf( s_autoRecordBasename, sizeof( s_autoRecordBasename ), "%s(POV)-vs-%s", tokenB, tokenA );
		} else {
			Com_sprintf( s_autoRecordBasename, sizeof( s_autoRecordBasename ), "%s-vs-%s", tokenA, tokenB );
		}
	} else {
		char	teamName[MAX_CVAR_VALUE_STRING];

		teamName[0] = '\0';
		if ( ent->client->sess.sessionTeam == TEAM_RED ) {
			G_ReadServerTeamName( TEAM_RED, teamName, sizeof( teamName ) );
		} else if ( ent->client->sess.sessionTeam == TEAM_BLUE ) {
			G_ReadServerTeamName( TEAM_BLUE, teamName, sizeof( teamName ) );
		}

		if ( teamName[0] ) {
			G_SanitizeFilenameToken( tokenA, teamName );
			Q_strcat( s_autoRecordBasename, sizeof( s_autoRecordBasename ), tokenA );
			Q_strcat( s_autoRecordBasename, sizeof( s_autoRecordBasename ), "-" );
		}

		Q_strcat( s_autoRecordBasename, sizeof( s_autoRecordBasename ), G_ShortGametypeName( g_gametype.integer ) );

		if ( ent->client->sess.sessionTeam != TEAM_SPECTATOR ) {
			G_SanitizeFilenameToken( tokenA, ent->client->pers.netname );
			Q_strcat( s_autoRecordBasename, sizeof( s_autoRecordBasename ), va( "-%s", tokenA ) );
		}
	}

	trap_Cvar_VariableStringBuffer( "mapname", mapName, sizeof( mapName ) );
	G_SanitizeFilenameToken( mapToken, mapName );
	Q_strcat( s_autoRecordBasename, sizeof( s_autoRecordBasename ), va( "-%s", mapToken ) );

	trap_RealTime( &now );
	Q_strcat( s_autoRecordBasename, sizeof( s_autoRecordBasename ),
		va( "-%d_%02d_%02d-%02d_%02d_%02d",
			now.tm_year + 1900,
			now.tm_mon + 1,
			now.tm_mday,
			now.tm_hour,
			now.tm_min,
			now.tm_sec ) );

	return s_autoRecordBasename;
}

/*
=============
G_StopAutoRecord

Stops the retail-style per-client match demo recording lane for every connected
client that opted into the shared `cg_autoAction` record bit.
=============
*/
static void G_StopAutoRecord( void ) {
	int		i;

	if ( !( s_autoRecordState & AUTO_RECORD_STATE_RECORDING ) ) {
		return;
	}

	s_autoRecordState &= ~AUTO_RECORD_STATE_RECORDING;

	for ( i = 0; i < level.maxclients; i++ ) {
		gentity_t	*ent;
		gclient_t	*client;

		ent = &g_entities[i];
		client = ent->client;
		if ( !client || client->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( !( client->pers.recordingPreferences & CLIENT_RECORDING_DEMO_RECORD ) ) {
			continue;
		}

		trap_SendServerCommand( i, "stoprecord" );
	}
}

/*
=============
G_StartAutoRecordForClient

Starts the retail late-join auto-record lane for one client when the current
match is already recording.
=============
*/
void G_StartAutoRecordForClient( gentity_t *ent ) {
	int	clientNum;

	if ( !ent || !ent->client ) {
		return;
	}

	if ( !( s_autoRecordState & AUTO_RECORD_STATE_RECORDING ) ) {
		return;
	}

	if ( !( ent->client->pers.recordingPreferences & CLIENT_RECORDING_DEMO_RECORD ) ) {
		return;
	}

	clientNum = ent - g_entities;
	trap_SendServerCommand( clientNum, va( "record \"%s\"\n", G_BuildAutoRecordBasename( ent ) ) );
}

/*
=============
G_CheckAutoRecord

Tracks the retail match auto-record controller state across warmup, live play,
and intermission.
=============
*/
static void G_CheckAutoRecord( void ) {
	int	i;

	if ( level.warmupTime == -1 ) {
		G_StopAutoRecord();
		s_autoRecordState = 0;
		return;
	}

	if ( level.warmupTime != 0 ) {
		return;
	}

	if ( level.intermissiontime ) {
		if ( level.time - level.intermissiontime <= 4000 ) {
			return;
		}
		if ( s_autoRecordState & AUTO_RECORD_STATE_SCREENSHOT ) {
			return;
		}

		G_StopAutoRecord();
		s_autoRecordState |= AUTO_RECORD_STATE_SCREENSHOT;

		for ( i = 0; i < level.maxclients; i++ ) {
			gentity_t	*ent;
			gclient_t	*client;

			ent = &g_entities[i];
			client = ent->client;
			if ( !client || client->pers.connected != CON_CONNECTED ) {
				continue;
			}
			if ( !( client->pers.recordingPreferences & CLIENT_RECORDING_SCREENSHOT ) ) {
				continue;
			}

			trap_SendServerCommand( i, va( "screenshot \"%s\"\n", G_BuildAutoRecordBasename( ent ) ) );
		}

		return;
	}

	if ( s_autoRecordState & AUTO_RECORD_STATE_RECORDING ) {
		return;
	}

	s_autoRecordState |= AUTO_RECORD_STATE_RECORDING;

	for ( i = 0; i < level.maxclients; i++ ) {
		gentity_t	*ent;
		gclient_t	*client;

		ent = &g_entities[i];
		client = ent->client;
		if ( !client || client->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( !( client->pers.recordingPreferences & CLIENT_RECORDING_DEMO_RECORD ) ) {
			continue;
		}

		trap_SendServerCommand( i, va( "record \"%s\"\n", G_BuildAutoRecordBasename( ent ) ) );
	}
}

/*
=============
G_SyncAllClientArmorTiers

Refreshes the replicated armor tier state after the server toggle changes.
=============
*/
static void G_SyncAllClientArmorTiers( void ) {
	int		i;
	qboolean	armorTiered;

	armorTiered = g_armorTiered.integer ? qtrue : qfalse;
	for ( i = 0; i < level.maxclients; i++ ) {
		BG_UpdateArmorTierFromCurrentArmor( &level.clients[i].ps, armorTiered );
	}
}


void QLR_Game_BindFrameContext( qlr_game_frame_context_t *ctx ) {
	g_qlr_frame_ctx = ctx;

	if ( g_qlr_frame_ctx ) {
		g_qlr_frame_ctx->level = ( qlr_level_locals_t * )&level;
		g_qlr_frame_ctx->entities = ( qlr_gentity_t * )g_entities;
		g_qlr_frame_ctx->entity_count = level.num_entities;
	}
}

void QLR_Game_UnbindFrameContext( void ) {
	g_qlr_frame_ctx = NULL;
}

vmCvar_t	g_gametype;
vmCvar_t	g_dmflags;
vmCvar_t	g_fraglimit;
vmCvar_t	g_timelimit;
vmCvar_t	mercylimit;
vmCvar_t	g_mercytime;
vmCvar_t	g_capturelimit;
vmCvar_t	g_scorelimit;
vmCvar_t	g_domCapTime;
vmCvar_t	g_domTeammateCapScale;
vmCvar_t	g_domDistressThreshold;
vmCvar_t	g_domEnableContention;
vmCvar_t	g_domNeutralFlag;
vmCvar_t	g_domScoreRate;
vmCvar_t	g_friendlyFire;
vmCvar_t	g_friendlyFireDampen;
vmCvar_t	g_password;
vmCvar_t	g_needpass;
vmCvar_t	g_gameState;
vmCvar_t	g_customSettings;
vmCvar_t	g_allTalk;
vmCvar_t	g_maxclients;
vmCvar_t	g_dedicated;
vmCvar_t	g_speed;
vmCvar_t	g_gravity;
vmCvar_t	g_cheats;
vmCvar_t	g_knockback;
vmCvar_t	g_inactivity;
vmCvar_t	g_inactivityWarning;
vmCvar_t	g_debugMove;
vmCvar_t	g_debugDamage;
vmCvar_t	g_debugAlloc;
vmCvar_t	g_debugFlags;
vmCvar_t	g_debugInactivity;
vmCvar_t	g_debugThawTime;
vmCvar_t	g_debugVampiricDamage;
vmCvar_t	g_weaponRespawn;
vmCvar_t	g_motd;
vmCvar_t	g_warmup;
vmCvar_t	g_doWarmup;
vmCvar_t	g_dropCmds;
vmCvar_t	g_warmupDelay;
vmCvar_t	g_warmupReadyDelay;
vmCvar_t	g_warmupReadyDelayAction;
vmCvar_t	g_restarted;
static vmCvar_t	g_svWarmupReadyPercentage;
vmCvar_t	g_log;
vmCvar_t	g_logSync;
vmCvar_t	g_podiumDist;
vmCvar_t	g_podiumDrop;
vmCvar_t	g_allowSpecVote;
vmCvar_t	g_allowVote;
vmCvar_t	g_allowVoteMidGame;
vmCvar_t	g_allowForfeit;
vmCvar_t	g_allowKill;
vmCvar_t	g_allowCustomHeadmodels;
vmCvar_t	g_complaintLimit;
vmCvar_t	g_complaintDamageThreshold;
vmCvar_t	g_voteFlags;
vmCvar_t	g_voteDelay;
vmCvar_t	g_voteLimit;
vmCvar_t	g_teamAutoJoin;
vmCvar_t	g_teamForceBalance;
vmCvar_t	g_banIPs;
vmCvar_t	g_filterBan;
vmCvar_t	g_instaGib;
vmCvar_t	g_itemTimers;
vmCvar_t	g_itemHeight;
vmCvar_t	g_specItemTimers;
vmCvar_t	g_forceSmallScoreboardMessage;
vmCvar_t	g_forceSendConfigstring;
vmCvar_t	g_forceAtmosphericEffects;
vmCvar_t	g_forceDmgThroughSurface;
vmCvar_t	g_dmgThroughSurfaceAngularThreshold;
vmCvar_t	g_dmgThroughSurfaceDampening;
vmCvar_t	g_dmgThroughSurfaceDistance;
vmCvar_t	g_grantItemOnSpawn;
vmCvar_t	g_disableLoadout;
vmCvar_t	g_maxDeferredSpawns;
vmCvar_t	g_teamSpawnAsSpec;
vmCvar_t	g_teamSpecFreeCam;
vmCvar_t	g_teamSpecSayEnable;
vmCvar_t	g_teamSizeMin;
vmCvar_t	g_teamForcePresent;
vmCvar_t	g_enemyTeamRespawnRatio;
vmCvar_t	g_switchTeamDelay;
vmCvar_t	g_shuffleTimedelay;
vmCvar_t	g_shuffleMinPlayers;
vmCvar_t	g_shuffleAutomatic;
vmCvar_t	g_shuffleAutomaticMinPlayers;
vmCvar_t	g_playerCylinders;
vmCvar_t	g_playerheadScale;
vmCvar_t	g_playerheadScaleOffset;
vmCvar_t	g_playerModelScale;
vmCvar_t	g_autoAction;
vmCvar_t	g_floodprot_maxcount;
vmCvar_t	g_floodprot_decay;
vmCvar_t	g_droppedPowerupsDecay;
vmCvar_t	g_dropPowerups;
vmCvar_t	g_dropSkulls;
vmCvar_t	g_kickBadUserinfo;
vmCvar_t	g_playermodelOverride;
vmCvar_t	g_playerheadmodelOverride;
vmCvar_t	g_training;
vmCvar_t	g_skipTrainingEnable;
static vmCvar_t	bot_autoReady;
static vmCvar_t	bot_breakPoint;
static vmCvar_t	bot_debugVar;
static vmCvar_t	bot_dynamicSkill;
static vmCvar_t	bot_followDist;
static vmCvar_t	bot_followMe;
static vmCvar_t	bot_gauntlet;
static vmCvar_t	bot_gauntletOnly;
static vmCvar_t	bot_hud;
static vmCvar_t	bot_instaGibAimSkill;
static vmCvar_t	bot_itemDelayTime;
static vmCvar_t	bot_teamkill;
vmCvar_t	bot_showAreaNumber;
vmCvar_t	bot_showAreas;
vmCvar_t	bot_showAvoidSpots;
static vmCvar_t	bot_showPath;
static vmCvar_t	bot_showTourPoints;
static vmCvar_t	bot_startingSkill;
static vmCvar_t	bot_training;
vmCvar_t	g_lagHaxHistory;
vmCvar_t	g_lagHaxMs;
vmCvar_t	g_botsFile;
vmCvar_t	g_botSpawnList;
vmCvar_t	g_accessFile;
vmCvar_t	g_factoryTitle;
vmCvar_t	g_factory;
vmCvar_t	g_dropInactive;
vmCvar_t	pmove_fixed;
vmCvar_t	pmove_msec;
vmCvar_t	g_overtime;
vmCvar_t	g_timeoutLen;
vmCvar_t	g_timeoutCount;
vmCvar_t        g_vampiricDamage;
vmCvar_t	g_suddenDeathRespawn;
vmCvar_t	g_suddenDeathRespawnStart;
vmCvar_t	g_suddenDeathRespawnTick;
vmCvar_t	g_suddenDeathRespawnMax;
vmCvar_t	g_suddenDeathRespawnIncrement;
vmCvar_t	g_suddenDeathRespawnPrint;
vmCvar_t	g_damage_cg;
vmCvar_t	g_damage_g;
vmCvar_t	g_damage_gh;
vmCvar_t	g_damage_mg;
vmCvar_t	g_damage_hmg;
vmCvar_t	g_damage_ng;
vmCvar_t	g_damage_sg;
vmCvar_t	g_damage_sg_outer;
vmCvar_t	g_damage_gl;
vmCvar_t	g_splashDamage_gl;
vmCvar_t	g_splashRadius_gl;
vmCvar_t	g_damage_rl;
vmCvar_t	g_splashDamage_rl;
vmCvar_t	g_splashRadius_rl;
vmCvar_t	g_damage_pg;
vmCvar_t	g_damage_pl;
vmCvar_t	g_splashDamage_pl;
vmCvar_t	g_splashRadius_pl;
vmCvar_t	g_splashDamage_pg;
vmCvar_t	g_splashRadius_pg;
vmCvar_t	g_damage_lg;
vmCvar_t	g_damage_rg;
vmCvar_t	g_damage_bfg;
vmCvar_t	g_splashDamage_bfg;
vmCvar_t	g_splashRadius_bfg;
vmCvar_t	g_damage_sg_falloff;
vmCvar_t	g_damage_lg_falloff;
vmCvar_t	g_range_sg_falloff;
vmCvar_t	g_range_lg_falloff;
vmCvar_t	g_accelFactor_rl;
vmCvar_t	g_accelRate_rl;
vmCvar_t	g_accelFactor_pg;
vmCvar_t	g_accelRate_pg;
vmCvar_t	g_accelFactor_bfg;
vmCvar_t	g_accelRate_bfg;
vmCvar_t	g_damagePlums;
vmCvar_t	g_powerupRespawn;
vmCvar_t	g_flightThrust;
vmCvar_t	g_flightRefuelRate;
vmCvar_t	g_maxFlightFuel;
vmCvar_t	g_battleSuitDampen;
vmCvar_t	g_kamiAttenuate;
vmCvar_t	g_kamiMinRatio;
vmCvar_t	g_latchedHookOffset;
vmCvar_t	g_bestStartingWeapons;
vmCvar_t	g_dropDamagedHealth;
vmCvar_t	g_velocity_gl;
vmCvar_t	g_velocity_rl;
vmCvar_t	g_velocity_pg;
vmCvar_t	g_velocity_bfg;
vmCvar_t	g_velocity_gh;
vmCvar_t	g_lightningDischarge;
vmCvar_t	g_railJump;
vmCvar_t	g_gauntletSpeedFactor;
vmCvar_t	g_headShotDamage_rg;
vmCvar_t	g_ironsights_mg;
vmCvar_t	g_midAirMinHeight;
vmCvar_t	g_nailbounce;
vmCvar_t	g_nailbouncepercentage;
vmCvar_t	g_nailcount;
vmCvar_t	g_nailspeed;
vmCvar_t	g_nailspread;
vmCvar_t	g_guidedRocket;
vmCvar_t	g_rocketsplashOffset;
vmCvar_t	g_splashdamageOffset;
vmCvar_t	g_quadDamageFactor;
vmCvar_t	g_quadHog;
vmCvar_t	g_quadHogIdle;
vmCvar_t	g_quadHogTime;
vmCvar_t	g_quadHogPingRate;
vmCvar_t	g_adTouchScoreBonus;
vmCvar_t	g_adElimScoreBonus;
vmCvar_t	g_adCaptureScoreBonus;
vmCvar_t	g_roundWarmupDelay;
vmCvar_t	g_roundDrawLivingCount;
vmCvar_t	g_roundDrawHealthCount;
vmCvar_t	g_freezeThawWinningTeam;
vmCvar_t	g_freezeThawThroughSurface;
vmCvar_t	g_freezeThawTime;
vmCvar_t	g_freezeThawTick;
vmCvar_t	g_freezeThawRadius;
vmCvar_t	g_freezeRoundDelay;
vmCvar_t	g_freezeResetWeaponsOnRound;
vmCvar_t	g_freezeResetHealthOnRound;
vmCvar_t	g_freezeResetArmorOnRound;
vmCvar_t	g_freezeRemovePowerupsOnRound;
vmCvar_t	g_freezeProtectedSpawnTime;
vmCvar_t	g_freezeEnvironmentalRespawnDelay;
vmCvar_t	g_freezeAutoThawTime;
static matchFactoryConfig_t matchFlow_lastConfig;
vmCvar_t	g_obeliskHealth;
vmCvar_t	g_obeliskRegenPeriod;
vmCvar_t	g_obeliskRegenAmount;
vmCvar_t	g_obeliskRespawnDelay;
vmCvar_t	g_cubeTimeout;
vmCvar_t	g_singlePlayer;
vmCvar_t	g_enableDebugTrace;
vmCvar_t	g_enableDust;
vmCvar_t	g_proxMineTimeout;
vmCvar_t	g_rrRoundScoreBonus;
vmCvar_t	g_rrDeathScorePenalty;
vmCvar_t	g_rrInfectedZombieFragBonus;
vmCvar_t	g_rrInfectedZombieHealthBonus;
vmCvar_t	g_rrInfectedZombieSpeed;
vmCvar_t	g_rrInfectedSurvivorScoreMethod;
vmCvar_t	g_rrInfectedSurvivorScoreBonus;
vmCvar_t	g_rrInfectedSurvivorScoreRate;
vmCvar_t	g_rrInfectedSurvivorMinSpeed;
vmCvar_t	g_rrInfectedSurvivorPingRate;
vmCvar_t	g_rrInfectedSpreadWarningTime;
vmCvar_t	g_rrInfectedSpreadTime;
vmCvar_t	g_rrInfected;
vmCvar_t	g_rrDamageScoreBonus;
vmCvar_t	g_rrAllowNegativeScores;
vmCvar_t	g_lastManStandingWarning;
vmCvar_t	g_lastManStandingMessage;
vmCvar_t	roundlimit;
vmCvar_t	roundtimelimit;
vmCvar_t	practiceflags;
vmCvar_t	g_flagBounce;
vmCvar_t	g_flagPhysics;
vmCvar_t	g_throwFlagVelocity;
vmCvar_t	g_throwFlagForwardMult;
vmCvar_t	g_tackleFlag;
vmCvar_t	g_returnFlagOnSuicide;
vmCvar_t	g_droppedFlagBonus;
vmCvar_t	g_neutralFlagPingTime;
vmCvar_t	g_spawnArmor;
vmCvar_t	g_spawnArmorDmgScale;
vmCvar_t	g_spawnMinDistance;
vmCvar_t	g_spawnRandomRatio;
vmCvar_t	g_spawnDelay_key;
vmCvar_t	g_spawnDelay_powerup;
vmCvar_t	g_spawnDelayRandom_key;
vmCvar_t	g_spawnDelayRandom_powerup;

// bk001129 - made static to avoid aliasing
static cvarTable_t		gameCvarTable[] = {
	// don't override the cheat state set by the system
	{ &g_cheats, "sv_cheats", "", 0, 0, qfalse },

	// noset vars
	{ NULL, "gamename", GAMEVERSION , CVAR_SERVERINFO | CVAR_ROM, 0, qfalse  },
	{ NULL, "g_levelStartTime", "0", CVAR_SERVERINFO | CVAR_ROM, 0, qfalse },
	{ NULL, "gamedate", __DATE__ , CVAR_ROM, 0, qfalse  },
	{ &g_restarted, "g_restarted", "0", CVAR_ROM, 0, qfalse  },
	{ NULL, "sv_mapname", "", CVAR_SERVERINFO | CVAR_ROM, 0, qfalse  },
	{ &g_gameState, "g_gameState", GAME_STATE_PRE_GAME, CVAR_SERVERINFO | CVAR_ROM, 0, qfalse, qfalse, "Publishes the current match phase (PRE_GAME, COUNT_DOWN, IN_PROGRESS)." },

	// latched vars
	{ &g_gametype, "g_gametype", "0", CVAR_SERVERINFO | CVAR_LATCH | CVAR_ROM, 0, qfalse  },
	{ &g_customSettings, "g_customSettings", "0", CVAR_SERVERINFO, 0, qfalse, qfalse, "Digest of flagged gameplay overrides published to CS_SERVERINFO.", qfalse },

	{ &g_maxclients, "sv_maxclients", "8", CVAR_SERVERINFO | CVAR_LATCH | CVAR_ARCHIVE, 0, qfalse  },

	// change anytime vars
	{ &g_dmflags, "dmflags", "0", CVAR_SERVERINFO | CVAR_ARCHIVE, 0, qtrue  },
	{ &g_fraglimit, "fraglimit", "20", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue },
{ &g_timelimit, "timelimit", "0", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue },
	{ &mercylimit, "mercylimit", "0", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue, qfalse, "Score differential that triggers the mercy rule once the grace window expires; 0 disables mercy checks." },
	{ &g_mercytime, "g_mercytime", "0", CVAR_NORESTART | CVAR_GAMERULE, 0, qfalse, qfalse, "Minutes after match start before the server evaluates mercylimit." },
	{ &g_capturelimit, "capturelimit", "8", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue },
	{ &g_scorelimit, "scorelimit", "150", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART | CVAR_GAMERULE, 0, qtrue, qfalse, "Team score threshold that ends Attack & Defend matches when positive." },
	{ &g_domCapTime, "g_domCapTime", "5", CVAR_GAMERULE, 0, qfalse, qfalse, "Seconds required to capture a Domination point with a single attacker." },
	{ &g_domTeammateCapScale, "g_domTeammateCapScale", "0.5", CVAR_GAMERULE, 0, qfalse, qfalse, "Additional capture speed gained per extra teammate assisting." },
	{ &g_domDistressThreshold, "g_domDistressThreshold", "75", CVAR_GAMERULE, 0, qfalse, qfalse, "Percent progress when defenders receive a distress warning." },
	{ &g_domEnableContention, "g_domEnableContention", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Allow Domination progress to continue when both teams contest a point." },
	{ &g_domNeutralFlag, "g_domNeutralFlag", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Require Domination points to be neutralized before capture completes when non-zero." },
	{ &g_domScoreRate, "g_domScoreRate", "5", CVAR_GAMERULE, 0, qfalse, qfalse, "Seconds between Domination score ticks per owned point." },
	{ &roundlimit, "roundlimit", "10", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue, qfalse, "Maximum number of rounds to play before the match ends." },
	{ &roundtimelimit, "roundtimelimit", "180", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue, qfalse, "Seconds allowed per active round before it times out." },
	{ &g_roundWarmupDelay, "g_roundWarmupDelay", "10000", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse, qfalse, "Milliseconds of warmup that separate freeze-style rounds." },
	{ &g_roundDrawLivingCount, "g_roundDrawLivingCount", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Print remaining living player counts when freeze rounds end." },
	{ &g_roundDrawHealthCount, "g_roundDrawHealthCount", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Print aggregate team health when freeze rounds finish." },
	{ &g_freezeThawWinningTeam, "g_freezeThawWinningTeam", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Award thaw credit to the winning team before the next round when non-zero." },
	{ &g_freezeThawThroughSurface, "g_freezeThawThroughSurface", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Allow thaw traces to pass through solid world geometry when enabled." },
	{ &g_freezeThawTime, "g_freezeThawTime", "2000", CVAR_GAMERULE, 0, qfalse, qfalse, "Milliseconds teammates must remain nearby before a frozen player thaws." },
	{ &g_freezeThawTick, "g_freezeThawTick", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Non-zero enables thaw-progress tick events while an ally stays in range." },
	{ &g_freezeThawRadius, "g_freezeThawRadius", "96", CVAR_GAMERULE, 0, qfalse, qfalse, "Radius in units required for thaw assistance to register." },
	{ &g_freezeRoundDelay, "g_freezeRoundDelay", "4000", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse, qfalse, "Delay in milliseconds between a freeze round ending and the next warmup." },
	{ &g_freezeResetWeaponsOnRound, "g_freezeResetWeaponsOnRound", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Respawn players with the factory loadout each time a freeze round restarts." },
	{ &g_freezeResetHealthOnRound, "g_freezeResetHealthOnRound", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Restore players to full health whenever a freeze round resets or they thaw." },
	{ &g_freezeResetArmorOnRound, "g_freezeResetArmorOnRound", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Restore armor to the factory amount on round reset or thaw." },
	{ &g_freezeRemovePowerupsOnRound, "g_freezeRemovePowerupsOnRound", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Strip carried powerups whenever a freeze round begins anew." },
	{ &g_freezeProtectedSpawnTime, "g_freezeProtectedSpawnTime", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Milliseconds of post-thaw spawn protection applied to players." },
	{ &g_freezeEnvironmentalRespawnDelay, "g_freezeEnvironmentalRespawnDelay", "5000", CVAR_GAMERULE, 0, qfalse, qfalse, "Milliseconds frozen players wait before auto-respawning when killed by the environment." },
	{ &g_freezeAutoThawTime, "g_freezeAutoThawTime", "120000", CVAR_GAMERULE, 0, qfalse, qfalse, "Milliseconds after which frozen players automatically thaw even without help." },
	{ &g_rrRoundScoreBonus, "g_rrRoundScoreBonus", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail Red Rover round-completion score bonus mirrored from qagamex86." },
	{ &g_rrDeathScorePenalty, "g_rrDeathScorePenalty", "-1", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail Red Rover death score delta applied through the round death handler." },
	{ &g_rrInfectedZombieFragBonus, "g_rrInfectedZombieFragBonus", "2", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail Red Rover infected frag bonus applied when a zombie kills a survivor." },
	{ &g_rrInfectedZombieHealthBonus, "g_rrInfectedZombieHealthBonus", "50", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail Red Rover cvar mirrored from qagamex86 for infected spawn health." },
	{ &g_rrInfectedZombieSpeed, "g_rrInfectedZombieSpeed", "1.15", CVAR_GAMERULE, 0, qfalse, qfalse, "Speed multiplier applied to infected players." },
	{ &g_rrInfectedSurvivorScoreMethod, "g_rrInfectedSurvivorScoreMethod", "2", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail Red Rover survivor-bonus mode selector mirrored from qagamex86." },
	{ &g_rrInfectedSurvivorScoreBonus, "g_rrInfectedSurvivorScoreBonus", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail Red Rover survivor-bonus amount mirrored from qagamex86." },
	{ &g_rrInfectedSurvivorScoreRate, "g_rrInfectedSurvivorScoreRate", "30", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail Red Rover survivor-bonus interval mirrored from qagamex86." },
	{ &g_rrInfectedSurvivorMinSpeed, "g_rrInfectedSurvivorMinSpeed", "500.0f", CVAR_GAMERULE, 0, qfalse, qfalse, "Minimum planar speed survivors must maintain before receiving penalty pings." },
	{ &g_rrInfectedSurvivorPingRate, "g_rrInfectedSurvivorPingRate", "2000", CVAR_GAMERULE, 0, qfalse, qfalse, "Milliseconds between survivor warning pings when moving too slowly." },
	{ &g_rrInfectedSpreadWarningTime, "g_rrInfectedSpreadWarningTime", "10", CVAR_GAMERULE, 0, qfalse, qfalse, "Seconds before forced infection that survivors begin receiving warning cues." },
	{ &g_rrInfectedSpreadTime, "g_rrInfectedSpreadTime", "40", CVAR_GAMERULE, 0, qfalse, qfalse, "Seconds a survivor can avoid infection before the virus automatically spreads." },
	{ &g_rrInfected, "g_rrInfected", "0", CVAR_LATCH | GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Enable the infection ruleset inside Red Rover." },
	{ &g_rrDamageScoreBonus, "g_rrDamageScoreBonus", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Multiplier applied to survivor damage when using damage-based scoring." },
	{ &g_rrAllowNegativeScores, "g_rrAllowNegativeScores", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Allow Red Rover scoring adjustments to drive a player's score below zero." },
	{ &g_lastManStandingWarning, "g_lastManStandingWarning", "1", 0, 0, qfalse, qfalse, "Enable the retail last-man-standing centerprint in team round modes." },
	{ &g_lastManStandingMessage, "g_lastManStandingMessage", "You are the last standing", 0, 0, qfalse, qfalse, "Centerprint sent to the lone remaining teammate when last-man-standing warnings are enabled." },
	{ &practiceflags, "practiceflags", "0", CVAR_ARCHIVE, 0, qfalse, qfalse, "Bitmask consumed by practice factories to enable Quake Live's training assists (RJ, SJ, etc.)." },

	{ &g_friendlyFire, "g_friendlyFire", "0", CVAR_GAMERULE, 0, qtrue  },
	{ &g_friendlyFireDampen, "g_friendlyFireDampen", "1.00", CVAR_GAMERULE, 0, qfalse, qfalse, "Damage scale applied to same-team hits when friendly fire remains enabled." },

	{ &g_teamAutoJoin, "g_teamAutoJoin", "0", CVAR_ARCHIVE, 0, qfalse, qfalse },
	{ &g_teamForceBalance, "g_teamForceBalance", "1", CVAR_ARCHIVE | CVAR_SERVERINFO  },
	{ &g_teamSpawnAsSpec, "g_teamSpawnAsSpec", "0", 0, 0, qfalse, qfalse, "Block live-team joins until administrators clear the lock; spectator and free joins remain allowed." },
	{ &g_teamSpecFreeCam, "g_teamSpecFreeCam", "0", 0, 0, qfalse, qfalse, "Allow spectators to use free-flying cameras when non-zero; otherwise they stay in follow or scoreboard views." },
	{ &g_teamSpecSayEnable, "g_teamSpecSayEnable", "1", 0, 0, qfalse, qfalse, "Permit spectators to chat while observing when enabled." },

	{ &g_teamSizeMin, "g_teamSizeMin", "1", CVAR_SERVERINFO, 0, qfalse, qfalse, "Minimum players per team required before warmup countdowns start in team modes." },
	{ &g_teamForcePresent, "g_teamForcePresent", "1", 0, 0, qfalse, qfalse, "Force both teams to satisfy g_teamSizeMin before starting live play." },
	{ &g_enemyTeamRespawnRatio, "g_enemyTeamRespawnRatio", "1.5", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail enemy-team respawn ratio cvar retained for qagame table parity." },
	{ &g_switchTeamDelay, "g_switchTeamDelay", "3", CVAR_GAMERULE, 0, qfalse, qfalse, "Seconds before a client may issue another team switch command." },
	{ &g_shuffleTimedelay, "g_shuffle_timedelay", "5000", 0, 0, qfalse, qfalse, "Milliseconds to delay before an automatic shuffle executes once armed." },
	{ &g_shuffleMinPlayers, "g_shuffle_minplayers", "3", 0, 0, qfalse, qfalse, "Minimum total players required before shuffle logic is considered." },
	{ &g_shuffleAutomatic, "g_shuffle_automatic", "0", 0, 0, qfalse, qfalse, "Enable Quake Live style automatic team shuffles during warmup." },
	{ &g_shuffleAutomaticMinPlayers, "g_shuffle_automatic_minplayers", "6", 0, 0, qfalse, qfalse, "Player threshold that must be met before auto-shuffle countdowns can arm." },

	{ &g_log, "g_log", "", CVAR_ARCHIVE, 0, qfalse  },
	{ &g_logSync, "g_logSync", "0", CVAR_ARCHIVE, 0, qfalse  },
	{ &g_accessFile, "g_accessFile", "access.txt", 0, 0, qfalse, qfalse, "Relative path to the access permission file evaluated for admin commands." },

	{ &g_password, "g_password", "", CVAR_USERINFO, 0, qfalse  },

	{ &g_banIPs, "g_banIPs", "", CVAR_ARCHIVE, 0, qfalse  },
	{ &g_filterBan, "g_filterBan", "1", CVAR_ARCHIVE, 0, qfalse  },
	{ &g_instaGib, "g_instaGib", "0", CVAR_SERVERINFO | GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse },
	{ &g_itemTimers, "g_itemTimers", "1", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse, qfalse, "Force server-controlled item timers to display for all clients when non-zero." },
	{ &g_itemHeight, "g_itemHeight", "35", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse, qfalse, "Vertical offset in units applied to enforced item timer indicators." },
	{ &g_forceSmallScoreboardMessage, "g_forceSmallScoreboardMessage", "0", 0, 0, qfalse, qfalse, "Prefer the compact scoreboard centerprint even with small player counts." },
	{ &g_forceSendConfigstring, "g_forceSendConfigstring", "0", 0, 0, qfalse, qfalse, "Resend all configstrings to clients on map load when enabled to debug sync issues." },
	{ &g_forceAtmosphericEffects, "g_forceAtmosphericEffects", "", CVAR_GAMERULE, 0, qfalse, qfalse, "Enable atmospheric map effects such as snow or rain regardless of client preference." },
	{ &g_forceDmgThroughSurface, "g_forceDmgThroughSurface", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Allow splash damage to pass through non-solid surfaces for testing when set." },
	{ &g_dmgThroughSurfaceAngularThreshold, "g_dmgThroughSurfaceAngularThreshold", "0.5f", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail angle threshold used when choosing damage-through-surface impact events." },
	{ &g_dmgThroughSurfaceDampening, "g_dmgThroughSurfaceDampening", "0.5f", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail radius scale for splash damage through surfaces." },
	{ &g_dmgThroughSurfaceDistance, "g_dmgThroughSurfaceDistance", "-33.1f", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail probe distance for damage-through-surface impact validation." },
	{ &g_specItemTimers, "g_specItemTimers", "1", 0, 0, qfalse },
	{ &g_grantItemOnSpawn, "g_grantItemOnSpawn", "", CVAR_GAMERULE, 0, qfalse, qfalse, "Whitespace or comma separated list of `give` tokens handed to every spawn, mirroring Quake Live's server-only spawn grants." },
	{ &g_disableLoadout, "g_disableLoadout", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Additional loadout restrictions expressed as a whitespace or comma separated list of weapon tokens (g, mg, sg, gl, rl, lg, rg, pg, bfg, gh, ng, pl, cg, hmg) or a numeric bitmask." },
	{ &g_playermodelOverride, "g_playermodelOverride", "", GAME_CVAR_FLAG_RETAIL_10000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Optional model path used to override every player's model selection server-wide." },
	{ &g_playerheadmodelOverride, "g_playerheadmodelOverride", "", GAME_CVAR_FLAG_RETAIL_10000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Optional head model override applied to all players for consistent visuals." },
	{ &g_allowCustomHeadmodels, "g_allowCustomHeadmodels", "0", GAME_CVAR_FLAG_RETAIL_10000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Allow clients to request independent headmodel strings; disabling forces heads to track the enforced player model." },
	{ &g_playerCylinders, "g_playerCylinders", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Toggles the Quake Live player-cylinder collision volumes so forced cosmetics line up with the server's hitboxes." },
	{ &g_playerheadScale, "g_playerheadScale", "1.0", GAME_CVAR_FLAG_RETAIL_10000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Primary multiplier applied to forced head models for visibility parity." },
	{ &g_playerheadScaleOffset, "g_playerheadScaleOffset", "1.0", GAME_CVAR_FLAG_RETAIL_10000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Secondary head-model scalar layered on top of g_playerheadScale so admins can fine-tune the enforced size." },
	{ &g_playerModelScale, "g_playerModelScale", "1.1", GAME_CVAR_FLAG_RETAIL_10000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Applies a global scale multiplier to server-enforced player models." },
	{ &g_autoAction, "g_autoAction", "0", 0, 0, qfalse, qfalse, "Comma or semicolon separated list of event:command pairs executed automatically (match_start, match_end, player_connect, player_disconnect)." },
	{ &g_skipTrainingEnable, "g_skipTrainingEnable", "0", CVAR_SYSTEMINFO | CVAR_ROM, 0, qfalse, qfalse, "Retail read-only training skip latch reset by the training command path." },
	{ &bot_autoReady, "bot_autoReady", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail bot auto-ready toggle retained for qagame cvar-table parity." },
	{ &bot_breakPoint, "bot_breakPoint", "0", 0, 0, qfalse, qfalse, "Retail bot AI debug breakpoint latch retained for cvar-table parity." },
	{ &bot_debugVar, "bot_debugVar", "0", 0, 0, qfalse, qfalse, "Retail bot AI debug selector retained for cvar-table parity." },
	{ &bot_dynamicSkill, "bot_dynamicSkill", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Enable retail bot training dynamic skill updates when non-zero." },
	{ &bot_followDist, "bot_followDist", "250", CVAR_GAMERULE, 0, qfalse, qfalse, "Distance the retail training bot keeps from the local player." },
	{ &bot_followMe, "bot_followMe", "", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail training follow-state cvar mirrored by the bot state update path." },
	{ &bot_gauntlet, "bot_gauntlet", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail training gauntlet toggle reset by the training skip path." },
	{ &bot_gauntletOnly, "bot_gauntletOnly", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail bot gauntlet-only toggle retained for qagame cvar-table parity." },
	{ &bot_hud, "bot_hud", "-1", CVAR_CHEAT, 0, qfalse, qfalse, "Retail bot HUD debug selector retained as a cheat-protected cvar." },
	{ &bot_instaGibAimSkill, "bot_instaGibAimSkill", "0.4", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail instagib bot aim-skill scalar retained for qagame cvar-table parity." },
	{ &bot_itemDelayTime, "bot_itemDelayTime", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Seconds before the retail training bot re-enables item pickup prediction." },
	{ &bot_teamkill, "bot_teamkill", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail qagame bot teamkill cvar retained alongside the server botlib precreation." },
	{ &bot_showAreaNumber, "bot_showAreaNumber", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail debug area-number cvar mirrored by BotTestAAS." },
	{ &bot_showAreas, "bot_showAreas", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail debug-area draw toggle mirrored by BotTestAAS." },
	{ &bot_showAvoidSpots, "bot_showAvoidSpots", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail avoid-spot draw toggle mirrored by BotTestAAS." },
	{ &bot_showPath, "bot_showPath", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail botlib path debug cvar also mirrored into the botlib libvar table." },
	{ &bot_showTourPoints, "bot_showTourPoints", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail training tour-point debug toggle retained for cvar-table parity." },
	{ &bot_startingSkill, "bot_startingSkill", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Starting bot skill cvar updated by the retail training skill path." },
	{ &bot_training, "bot_training", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail bot training phase cvar mirrored by the training state machine." },
	{ &g_floodprot_maxcount, "g_floodprot_maxcount", "10", 0, 0, qfalse, qfalse, "Maximum chat or command bursts allowed before retail flood protection drops clients on overflow; 0 disables the limiter." },
	{ &g_floodprot_decay, "g_floodprot_decay", "1000", 0, 0, qfalse, qfalse, "Milliseconds required before a flood point decays back off the counter; maxcount is the limiter on/off switch." },
	{ &g_startingHealth, "g_startingHealth", "100", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse, qfalse, "Health awarded to players when they spawn." },
	{ &g_startingArmor, "g_startingArmor", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Armor awarded to players when they spawn." },
	{ &g_armorTiered, "armor_tiered", "0", GAME_CVAR_FLAG_RETAIL_20000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Enable retail Quake Live tiered armor behaviour for pickups, regen, and the dedicated HUD settings transport." },
	{ &g_startingWeapons, "g_startingWeapons", "3", CVAR_GAMERULE, 0, qfalse, qfalse, "Bitmask of weapons awarded to players when they spawn." },
	{ &g_flightThrust, "g_flightThrust", "1200", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail Flight thrust cvar retained for table parity; shared pmove does not consume it." },
	{ &g_flightRefuelRate, "g_flightRefuelRate", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail Flight refuel-rate cvar retained for table parity; pickups use powerup quantity directly." },
	{ &g_maxFlightFuel, "g_maxFlightFuel", "16000", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail Flight fuel cap cvar retained for table parity; pickups use powerup quantity directly." },
	{ &g_kamiAttenuate, "g_kamiAttenuate", "2048", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail Kamikaze attenuation distance used for radial damage falloff." },
	{ &g_kamiMinRatio, "g_kamiMinRatio", "0.1", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail minimum Kamikaze damage ratio after attenuation." },
	{ &g_battleSuitDampen, "g_battleSuitDampen", "0.25", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail damage multiplier applied to non-falling damage while Battlesuit is active." },
	{ &g_latchedHookOffset, "g_latchedHookOffset", "-2.0f", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail server hook-offset cvar retained for qagame table parity." },
	{ &g_bestStartingWeapons, "g_bestStartingWeapons", "gh bfg rl lg rg hmg cg sg pg mg ng gl g pl", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail best-starting-weapon preference list retained for factory and cvar parity." },
	{ &g_dropDamagedHealth, "g_dropDamagedHealth", "0", CVAR_TEMP | GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "When enabled, health items dropped by players preserve their damaged counts instead of always healing for their base amount." },
	{ &g_droppedPowerupsDecay, "g_droppedPowerupsDecay", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail Quake Live dropped-powerup decay cvar retained for factory and cvar parity." },
	{ &g_dropPowerups, "g_dropPowerups", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail Quake Live death-drop powerup cvar retained for factory and cvar parity." },
	{ &g_dropSkulls, "g_dropSkulls", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail Quake Live Harvester skull-drop cvar retained for factory and cvar parity." },
	{ &g_kickBadUserinfo, "g_kickBadUserinfo", "1", 0, 0, qfalse, qfalse, "Drop clients submitting malformed userinfo when non-zero; 0 only warns and repairs the data." },
	{ &g_botsFile, "g_botsFile", "", CVAR_INIT | CVAR_ROM, 0, qfalse, qfalse, "Override bot definition list with a custom script when specified." },
	{ &g_botSpawnList, "g_botSpawnList", "", 0, 0, qfalse, qfalse, "Space-separated bot names automatically spawned on map start when set." },
	{ &g_adTouchScoreBonus, "g_adTouchScoreBonus", "1", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse, qfalse, "Attack & Defend touch bonus added to the scoring totals whenever an attacker grabs the flag." },
	{ &g_adElimScoreBonus, "g_adElimScoreBonus", "2", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse, qfalse, "Attack & Defend elimination bonus granted to teams and players for each enemy frag." },
	{ &g_adCaptureScoreBonus, "g_adCaptureScoreBonus", "3", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse, qfalse, "Attack & Defend capture bonus layered on top of the base team point whenever the flag is secured." },
	{ &g_flagBounce, "g_flagBounce", "0.25", CVAR_GAMERULE, 0, qfalse, qfalse, "Bounce scale applied to dropped flags when retail flag physics are enabled." },
	{ &g_flagPhysics, "g_flagPhysics", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Selects optional flag physics modes; zero preserves the classic handling." },
	{ &g_throwFlagVelocity, "g_throwFlagVelocity", "0", 0, 0, qfalse, qfalse, "Forward launch velocity applied when retail flag physics are enabled." },
	{ &g_throwFlagForwardMult, "g_throwFlagForwardMult", "2.5", 0, 0, qfalse, qfalse, "Multiplier applied to carrier velocity when tossing flags with retail physics." },
	{ &g_tackleFlag, "g_tackleFlag", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Enable experimental tackle mechanics that jostle flags from carriers when non-zero." },
	{ &g_returnFlagOnSuicide, "g_returnFlagOnSuicide", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Return a carried flag immediately when its owner suicides when enabled." },
	{ &g_droppedFlagBonus, "g_droppedFlagBonus", "1", CVAR_TEMP, 0, qfalse, qfalse, "Bonus granted to players that force or recover an enemy-dropped flag." },
	{ &g_neutralFlagPingTime, "g_neutralFlagPingRate", "2400", CVAR_GAMERULE, 0, qfalse, qfalse, "Milliseconds between neutral flag ping notifications while it sits on the ground; set to 0 to disable." },
	{ &g_spawnArmor, "g_spawnArmor", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail spawn-armor timer stored in the player powerup timer array." },
	{ &g_spawnArmorDmgScale, "g_spawnArmorDmgScale", "0.5", CVAR_GAMERULE, 0, qfalse, qfalse, "Damage multiplier applied while the retail spawn armor timer is active." },
	{ &g_spawnMinDistance, "g_spawnMinDistance", "64", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail spawn-selection minimum-distance cvar retained for qagame table parity." },
	{ &g_spawnRandomRatio, "g_spawnRandomRatio", "0.5", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail spawn-selection random-ratio cvar retained for qagame table parity." },
	{ &g_spawnDelay_key, "g_spawnDelay_key", "30", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Base seconds before map key items spawn in." },
	{ &g_spawnDelay_powerup, "g_spawnDelay_powerup", "45", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Base seconds before map powerups spawn in." },
	{ &g_spawnDelayRandom_key, "g_spawnDelayRandom_key", "15", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Random seconds added to map key item initial spawn delay." },
	{ &g_spawnDelayRandom_powerup, "g_spawnDelayRandom_powerup", "15", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Random seconds added to map powerup initial spawn delay." },

	{ &g_needpass, "g_needpass", "0", CVAR_SERVERINFO | CVAR_ROM, 0, qfalse },

	{ &g_allTalk, "g_allTalk", "0", 0, 0, qfalse, qfalse, "Allow players, spectators, and opposing teams to share chat when enabled." },

	{ &g_dedicated, "dedicated", "0", 0, 0, qfalse  },

	{ &g_speed, "g_speed", "320", CVAR_GAMERULE, 0, qtrue  },
	{ &g_gravity, "g_gravity", "800", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qtrue  },
	{ &g_knockback, "g_knockback", "1000", CVAR_GAMERULE, 0, qtrue  },
	{ &g_max_knockback, "g_max_knockback", "120", CVAR_GAMERULE, 0, qfalse, qfalse, "Upper clamp applied to positive computed knockback force." },
	{ &g_weaponRespawn, "g_weaponRespawn", "5", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qtrue  },
	{ &g_inactivity, "g_inactivity", "0", 0, 0, qtrue },
	{ &g_inactivityWarning, "g_inactivityWarning", "10", 0, 0, qtrue, qfalse, "Seconds before an inactivity timeout that the warning centerprint is sent." },
	{ &g_dropInactive, "g_dropInactive", "1", 0, 0, qfalse, qfalse, "Automatically remove clients marked inactive when enabled." },
	{ &g_debugMove, "g_debugMove", "0", 0, 0, qfalse },
	{ &g_debugDamage, "g_debugDamage", "0", 0, 0, qfalse },
	{ &g_debugAlloc, "g_debugAlloc", "0", 0, 0, qfalse },
	{ &g_debugFlags, "g_debugFlags", "0", 0, 0, qfalse, qfalse, "Retail debug flag bitmask retained for qagame cvar-table parity." },
	{ &g_debugInactivity, "g_debugInactivity", "0", 0, 0, qfalse, qfalse, "Retail inactivity debug toggle retained for qagame cvar-table parity." },
	{ &g_debugThawTime, "g_debugThawTime", "0", 0, 0, qfalse, qfalse, "Retail thaw-time debug toggle retained for qagame cvar-table parity." },
	{ &g_debugVampiricDamage, "g_debugVampiricDamage", "0", 0, 0, qfalse, qfalse, "Retail vampiric-damage debug toggle retained for qagame cvar-table parity." },
	{ &g_motd, "g_motd", "", 0, 0, qfalse },

	{ &g_podiumDist, "g_podiumDist", "80", CVAR_GAMERULE, 0, qfalse },
	{ &g_podiumDrop, "g_podiumDrop", "70", CVAR_GAMERULE, 0, qfalse },

	{ &g_allowSpecVote, "g_allowSpecVote", "0", 0, 0, qfalse },
	{ &g_allowVote, "g_allowVote", "1", CVAR_ARCHIVE, 0, qfalse },
	{ &g_allowVoteMidGame, "g_allowVoteMidGame", "0", 0, 0, qfalse },
	{ &g_allowForfeit, "g_allowForfeit", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Enables the forfeit console command when non-zero so duel and CA leagues can permit early surrenders." },
	{ &g_allowKill, "g_allowKill", "1000", CVAR_GAMERULE, 0, qfalse, qfalse, "Minimum milliseconds between kill commands; 0 restores instant suicides." },
	{ &g_complaintLimit, "g_complaintLimit", "5", CVAR_ARCHIVE, 0, qfalse, qfalse, "Maximum complaints before a player is automatically kicked; 0 disables kicking." },
	{ &g_complaintDamageThreshold, "g_complaintDamageThreshold", "400", CVAR_ARCHIVE, 0, qfalse, qfalse, "Minimum damage from a teammate required to present the complaint prompt." },
	{ &g_voteFlags, "g_voteFlags", "0", CVAR_ARCHIVE | CVAR_SERVERINFO, 0, qfalse },
	{ &g_voteDelay, "g_voteDelay", "0", 0, 0, qfalse },
	{ &g_voteLimit, "g_voteLimit", "0", 0, 0, qfalse },
	{ &g_warmup, "g_warmup", "10", CVAR_ARCHIVE, 0, qtrue  },
	{ &g_doWarmup, "g_doWarmup", "1", CVAR_ARCHIVE, 0, qtrue  },
	{ &g_dropCmds, "g_dropCmds", "7", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail command-drop bitmask updated alongside round attack lockout state." },
	{ &g_warmupDelay, "g_warmupDelay", "15", 0, 0, qfalse, qfalse, "Seconds after level start before retail warmup countdown checks may proceed." },
	{ &g_warmupReadyDelay, "g_warmupReadyDelay", "0", 0, 0, qfalse, qfalse, "Seconds to wait in duel after exactly one player readies before applying g_warmupReadyDelayAction; 0 disables the retail delay controller." },
	{ &g_warmupReadyDelayAction, "g_warmupReadyDelayAction", "1", 0, 0, qfalse, qfalse, "Retail duel ready-delay action: 1 moves the unready duelist to spectate-only, 2 forces both duelists ready." },
	{ &g_svWarmupReadyPercentage, "sv_warmupReadyPercentage", "0.51", CVAR_ARCHIVE | CVAR_LATCH, 0, qfalse, qfalse, "Fraction of warmup-eligible clients required to ready before the retail countdown starts." },
	{ &g_training, "g_training", "0", CVAR_SYSTEMINFO | CVAR_GAMERULE, 0, qfalse, qfalse, "Marks training sessions and disables competitive match flow when set." },
	{ &g_lagHaxHistory, "g_lagHaxHistory", "4", CVAR_LATCH, 0, qfalse, qfalse, "Hidden Quake Live rewind history depth used by the retail lag compensation seam." },
	{ &g_lagHaxMs, "g_lagHaxMs", "80", CVAR_LATCH, 0, qfalse, qfalse, "Hidden Quake Live rewind window in milliseconds for the retail lag compensation seam." },
	{ &g_enableDebugTrace, "g_enableDebugTrace", "0", 0, 0, qfalse, qfalse, "Retail debug trace toggle retained for qagame cvar-table parity." },
	{ &g_overtime, "g_overtime", "120", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse, qfalse, "Overtime period length in seconds once regulation ends tied; 0 keeps sudden death active until the tie is broken." },
	{ &g_suddenDeathRespawn, "g_suddenDeathRespawn", "0", CVAR_GAMERULE, 0, qfalse, qfalse, "Allow ammo to continue respawning during sudden death when set to 1." },
	{ &g_timeoutLen, "g_timeoutLen", "60", CVAR_GAMERULE, 0, qfalse, qfalse, "Timeout duration in seconds for each team pause." },
	{ &g_timeoutCount, "g_timeoutCount", "0", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse, qfalse, "Number of timeouts each team may call per match." },
	{ &g_factoryTitle, "g_factoryTitle", "", CVAR_SERVERINFO | CVAR_ROM, 0, qfalse, qfalse, "Short factory title pushed via serverinfo for display on connected clients." },
	{ &g_factory, "g_factory", "", CVAR_SERVERINFO | CVAR_ROM, 0, qfalse, qfalse, "Identifier of the active factory loaded from scripts/factories*, defaulting to the current gametype's retail factory when unset or invalid." },
	{ &g_maxDeferredSpawns, "g_maxDeferredSpawns", "4", 0, 0, qfalse, qfalse, "Maximum simultaneous delayed spawns the queue may hold before new respawns execute immediately." },
	{ &g_vampiricDamage, "g_vampiricDamage", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Fraction of dealt health damage returned to the attacker as healing." },
	{ &g_suddenDeathRespawnStart, "g_suddenDeathRespawnStart", "3", CVAR_GAMERULE, 0, qfalse, qfalse, "Initial sudden-death respawn delay in seconds when respawns are enabled." },
	{ &g_suddenDeathRespawnTick, "g_suddenDeathRespawnTick", "60", CVAR_GAMERULE, 0, qfalse, qfalse, "Interval in seconds after which sudden-death respawn delays are increased." },
	{ &g_suddenDeathRespawnMax, "g_suddenDeathRespawnMax", "10", CVAR_GAMERULE, 0, qfalse, qfalse, "Maximum sudden-death respawn delay in seconds." },
	{ &g_suddenDeathRespawnIncrement, "g_suddenDeathRespawnIncrement", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Seconds added to the sudden-death respawn delay at each tick." },
	{ &g_suddenDeathRespawnPrint, "g_suddenDeathRespawnPrint", "1", CVAR_GAMERULE, 0, qfalse, qfalse, "Print announcements when sudden-death respawn delays change." },
	{ &g_damage_cg, "g_damage_cg", "8", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "Chaingun bullet damage per hit; 8 mirrors the Quake Live HLIL defaults." },
	{ &g_damage_g, "g_damage_g", "50", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_damage_gh, "g_damage_gh", "10", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "Grappling Hook projectile impact damage; 10 matches the retail DLL export." },
	{ &g_damage_mg, "g_damage_mg", "5", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_damage_ng, "g_damage_ng", "12", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "Nailgun projectile damage per bolt; 12 reproduces the HLIL tables." },
	{ &g_damage_hmg, "g_damage_hmg", "8", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_damage_sg, "g_damage_sg", "5", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_damage_sg_outer, "g_damage_sg_outer", "5", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "Shotgun outer-ring pellet damage when Quake Live's dual spread is active." },
	{ &g_damage_gl, "g_damage_gl", "100", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_splashDamage_gl, "g_splashdamage_gl", "100", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_splashRadius_gl, "g_splashradius_gl", "150", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_damage_rl, "g_damage_rl", "100", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_splashDamage_rl, "g_splashdamage_rl", "84", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_splashRadius_rl, "g_splashradius_rl", "120", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_damage_pg, "g_damage_pg", "20", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_damage_pl, "g_damage_pl", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "Direct-hit damage applied by the proximity mine launcher before the mine arms." },
	{ &g_splashDamage_pl, "g_splashdamage_pl", "100", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "Splash damage applied when a proximity mine detonates." },
	{ &g_splashRadius_pl, "g_splashradius_pl", "150", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "Splash radius applied when a proximity mine detonates." },
	{ &g_splashDamage_pg, "g_splashdamage_pg", "15", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_splashRadius_pg, "g_splashradius_pg", "20", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_damage_lg, "g_damage_lg", "6", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_damage_rg, "g_damage_rg", "80", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_damage_bfg, "g_damage_bfg", "100", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_splashDamage_bfg, "g_splashdamage_bfg", "100", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_splashRadius_bfg, "g_splashradius_bfg", "80", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },
	{ &g_damage_sg_falloff, "g_damage_sg_falloff", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Shotgun pellet damage subtracted for each g_range_sg_falloff interval beyond the first; 0 preserves constant damage." },
	{ &g_range_sg_falloff, "g_range_sg_falloff", "768", CVAR_GAMERULE, 0, qfalse, qfalse, "Distance in units before shotgun damage begins to fall off." },
	{ &g_damage_lg_falloff, "g_damage_lg_falloff", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Damage subtracted from lightning gun hits for each retail falloff interval beyond g_range_lg_falloff; 0 keeps constant damage." },
	{ &g_range_lg_falloff, "g_range_lg_falloff", "768", CVAR_GAMERULE, 0, qfalse, qfalse, "Distance in units before retail lightning falloff starts, with each additional interval removing another g_damage_lg_falloff step." },
	{ &g_accelFactor_rl, "g_accelFactor_rl", "1", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Scale applied to rocket acceleration tests when factories enable projectile acceleration; 1 keeps stock speeds." },
	{ &g_accelRate_rl, "g_accelRate_rl", "16", CVAR_GAMERULE, 0, qfalse, qfalse, "Milliseconds between rocket acceleration steps when g_accelFactor_rl is active." },
	{ &g_accelFactor_pg, "g_accelFactor_pg", "1", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Scale applied to plasmagun bolt acceleration when Quake Live factories request faster bolts; 1 keeps stock speeds." },
	{ &g_accelRate_pg, "g_accelRate_pg", "16", CVAR_GAMERULE, 0, qfalse, qfalse, "Milliseconds between plasmagun acceleration steps while the associated factor is non-zero." },
	{ &g_accelFactor_bfg, "g_accelFactor_bfg", "1", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Scale applied to BFG projectile acceleration; 1 leaves classic trajectories untouched." },
	{ &g_accelRate_bfg, "g_accelRate_bfg", "16", CVAR_GAMERULE, 0, qfalse, qfalse, "Milliseconds between BFG acceleration updates whenever acceleration is enabled." },
	{ &g_velocity_gl, "g_velocity_gl", "700", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "Grenade Launcher projectile speed in ups; mirrors the compiled 700 default and feeds both server and client prediction." },
	{ &g_velocity_rl, "g_velocity_rl", "1000", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "Rocket Launcher projectile speed in ups, defaulting to the retail 1000 ups behaviour." },
	{ &g_velocity_pg, "g_velocity_pg", "2000", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "Plasmagun bolt speed in ups; aligns with the legacy 2000 ups firing velocity." },
	{ &g_velocity_bfg, "g_velocity_bfg", "1800", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "BFG projectile speed in ups pulled from the retail DLL defaults." },
	{ &g_velocity_gh, "g_velocity_gh", "1800", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "Grappling Hook projectile speed in ups; 1800 preserves the retail projectile behaviour." },
	{ &g_lightningDischarge, "g_lightningDischarge", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "When enabled, lightning gun shots discharge and damage the shooter when fired in hazardous volumes." },
	{ &g_railJump, "g_railJump", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "Strength of the retail rail jump push applied when a rail shot hits solid geometry within 120 units." },
	{ &g_gauntletSpeedFactor, "g_gauntletSpeedFactor", "1.0", CVAR_GAMERULE, 0, qfalse, qfalse, "Gauntlet swing speed multiplier requested by Quake Live factories; 1.0 retains stock timing." },
	{ &g_headShotDamage_rg, "g_headShotDamage_rg", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "Extra railgun damage applied to headshots whenever headshot mutators run; 0 keeps the classic behaviour." },
	{ &g_ironsights_mg, "g_ironsights_mg", "1.0", CVAR_TEMP | GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Machinegun ironsight spread/recoil scale pulled from the HLIL weapon tables." },
	{ &g_midAirMinHeight, "g_midAirMinHeight", "96", CVAR_GAMERULE, 0, qfalse, qfalse, "Minimum height in units that a target must reach before mid-air medals and splash bonuses register." },
	{ &g_nailbounce, "g_nailbounce", "1", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Maximum number of ricochets allowed for each bouncing Nailgun bolt." },
	{ &g_nailbouncepercentage, "g_nailbouncepercentage", "65", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Chance (0-100) for a Nailgun bolt to receive the ricochet flag." },
	{ &g_nailcount, "g_nailcount", "10", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Number of Nailgun bolts fired per shot." },
	{ &g_nailspeed, "g_nailspeed", "1000", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Randomized Nailgun bolt velocity span in ups." },
	{ &g_nailspread, "g_nailspread", "400", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse, "Spread applied to Nailgun bolt direction sampling." },
	{ &g_powerupRespawn, "g_powerupRespawn", "120", CVAR_GAMERULE, 0, qfalse, qfalse, "Seconds before powerups respawn after being collected; 0 uses each entity's scripted timing." },
	{ &g_guidedRocket, "g_guidedRocket", "0", CVAR_GAMERULE, 0, qtrue, qfalse, "Enable Quake Live style guided rockets when non-zero." },
	{ &g_rocketsplashOffset, "g_rocketsplashOffset", "-10.0", CVAR_GAMERULE, 0, qtrue, qfalse, "Offset in ups applied along the impact normal before evaluating rocket splash damage." },
	{ &g_splashdamageOffset, "g_splashdamageOffset", "0.05", CVAR_GAMERULE, 0, qfalse, qfalse, "Retail generic splash-damage offset cvar retained for qagame table parity." },
	{ &g_damagePlums, "g_damagePlums", "2", CVAR_GAMERULE, 0, qfalse, qfalse, "Toggle per-player damage plums emitted by the server when scoring events occur." },
	{ &g_quadDamageFactor, "g_quadDamageFactor", "3", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse, qfalse, "Damage multiplier applied while Quad Damage is active; 3 mirrors the Quake Live DLL." },
	{ &g_quadHog, "g_quadHog", "0", CVAR_LATCH | GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse, "Toggle Quad Hog survival mode that forces the carrier to fight the arena when enabled." },
	{ &g_quadHogIdle, "g_quadHogIdle", "20", CVAR_GAMERULE, 0, qtrue, qfalse, "Seconds of inactivity allowed for the Quad Hog carrier before the powerup is revoked." },
	{ &g_quadHogTime, "g_quadHogTime", "60", CVAR_GAMERULE, 0, qtrue, qfalse, "Maximum time in seconds a player may hold Quad during Quad Hog events before it auto-expires." },
	{ &g_quadHogPingRate, "g_quadHogPingRate", "1500", CVAR_GAMERULE, 0, qtrue, qfalse, "Milliseconds between Quad Hog reminder pings while the timer is active." },
	{ &g_obeliskHealth, "g_obeliskHealth", "2500", CVAR_GAMERULE, 0, qfalse },
	{ &g_obeliskRegenPeriod, "g_obeliskRegenPeriod", "1", CVAR_GAMERULE, 0, qfalse },
	{ &g_obeliskRegenAmount, "g_obeliskRegenAmount", "15", CVAR_GAMERULE, 0, qfalse },
	{ &g_obeliskRespawnDelay, "g_obeliskRespawnDelay", "10", CVAR_GAMERULE, 0, qfalse },

	{ &g_cubeTimeout, "g_cubeTimeout", "30", CVAR_GAMERULE, 0, qfalse },
	{ &g_singlePlayer, "ui_singlePlayerActive", "", 0, 0, qfalse, qfalse  },

	{ &g_enableDust, "g_enableDust", "0", 0, 0, qtrue, qfalse },
	{ &g_proxMineTimeout, "g_proxMineTimeout", "20", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse },
	{ &pmove_fixed, "pmove_fixed", "0", CVAR_SYSTEMINFO, 0, qfalse},
	{ &pmove_msec, "pmove_msec", "8", CVAR_SYSTEMINFO, 0, qfalse}

};

// bk001129 - made static to avoid aliasing
static int gameCvarTableSize = sizeof( gameCvarTable ) / sizeof( gameCvarTable[0] );

/*
=============
G_RefreshAllCvars

Synchronises every registered vmCvar_t with the engine so scripted factory updates can be applied immediately.
=============
*/
void G_RefreshAllCvars( void ) {
	int				 i;
	cvarTable_t	*cv;

	for ( i = 0, cv = gameCvarTable; i < gameCvarTableSize; i++, cv++ ) {
		if ( cv->vmCvar ) {
			trap_Cvar_Update( cv->vmCvar );
		}
	}
}

static void G_ReportMissingCvar( const char *cvarName ) {
        if ( !cvarName || !cvarName[0] ) {
                return;
        }

        G_Printf( "WARNING: gameplay config cvar %s is unavailable; using fallback value\n", cvarName );
}

static int G_ReadWeaponCvar( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
	if ( !cvar ) {
		G_ReportMissingCvar( cvarName );
		return fallback;
	}

	if ( cvar->integer <= 0 ) {
		return fallback;
	}

	return cvar->integer;
}

static int G_ReadWeaponCvarRaw( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
	if ( !cvar ) {
		G_ReportMissingCvar( cvarName );
		return fallback;
	}

	return cvar->integer;
}

static int G_ReadWeaponCvarAtLeast( const vmCvar_t *cvar, int fallback, const char *cvarName, int minValue ) {
	int		value;

	value = G_ReadWeaponCvar( cvar, fallback, cvarName );
	if ( value < minValue ) {
		return minValue;
	}

	return value;
}

static qboolean G_ReadWeaponBoolCvar( const vmCvar_t *cvar, qboolean fallback, const char *cvarName ) {
	if ( !cvar ) {
		G_ReportMissingCvar( cvarName );
		return fallback;
	}

	return ( cvar->integer != 0 ) ? qtrue : qfalse;
}

/*
=============
G_ReadWeaponCvarNonNegative

Clamps gameplay CVars that allow zero to non-negative integers while respecting fallbacks when invalid data is supplied.
=============
*/
static int G_ReadWeaponCvarNonNegative( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
	int		value;

	value = G_ReadWeaponCvarRaw( cvar, fallback, cvarName );
	if ( value < 0 ) {
		return fallback;
	}

	return value;
}

/*
=============
G_ReadWeaponFloatCvarRaw

Returns floating-point gameplay CVar values or the supplied fallback when the variable is missing.
=============
*/
static float G_ReadWeaponFloatCvarRaw( const vmCvar_t *cvar, float fallback, const char *cvarName ) {
	if ( !cvar ) {
		G_ReportMissingCvar( cvarName );
		return fallback;
	}

	return cvar->value;
}

/*
=============
G_ReadWeaponFloatCvarNonNegative

Ensures floating-point gameplay CVars stay non-negative and fall back when invalid values are entered.
=============
*/
static float G_ReadWeaponFloatCvarNonNegative( const vmCvar_t *cvar, float fallback, const char *cvarName ) {
	float		value;

	value = G_ReadWeaponFloatCvarRaw( cvar, fallback, cvarName );
	if ( value < 0.0f ) {
		return fallback;
	}

	return value;
}

/*
=============
G_InitWeaponConfig

Refreshes the cached weapon config block from gameplay CVars.
=============
*/
void G_InitWeaponConfig( void ) {
	g_weaponConfig.gauntletDamage = G_ReadWeaponCvar( &g_damage_g, 50, "g_damage_g" );
	g_weaponConfig.machinegunDamage = G_ReadWeaponCvar( &g_damage_mg, 5, "g_damage_mg" );
	g_weaponConfig.heavyMachinegunDamage = G_ReadWeaponCvar( &g_damage_hmg, 8, "g_damage_hmg" );
	g_weaponConfig.chaingunDamage = G_ReadWeaponCvar( &g_damage_cg, 8, "g_damage_cg" );
	g_weaponConfig.shotgunDamage = G_ReadWeaponCvar( &g_damage_sg, 5, "g_damage_sg" );
	g_weaponConfig.shotgunOuterDamage = G_ReadWeaponCvar( &g_damage_sg_outer, 5, "g_damage_sg_outer" );
	g_weaponConfig.shotgunFalloffDamage = G_ReadWeaponCvarNonNegative( &g_damage_sg_falloff, 0, "g_damage_sg_falloff" );
	g_weaponConfig.shotgunFalloffRange = G_ReadWeaponCvarNonNegative( &g_range_sg_falloff, 768, "g_range_sg_falloff" );
	g_weaponConfig.grenadeDamage = G_ReadWeaponCvar( &g_damage_gl, 100, "g_damage_gl" );
	g_weaponConfig.grenadeSplashDamage = G_ReadWeaponCvar( &g_splashDamage_gl, 100, "g_splashdamage_gl" );
	g_weaponConfig.grenadeSplashRadius = G_ReadWeaponCvar( &g_splashRadius_gl, 150, "g_splashradius_gl" );
	g_weaponConfig.grenadeSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_gl, 700, "g_velocity_gl", 1 );
	g_weaponConfig.rocketDamage = G_ReadWeaponCvar( &g_damage_rl, 100, "g_damage_rl" );
	g_weaponConfig.rocketSplashDamage = G_ReadWeaponCvar( &g_splashDamage_rl, 84, "g_splashdamage_rl" );
	g_weaponConfig.rocketSplashRadius = G_ReadWeaponCvar( &g_splashRadius_rl, 120, "g_splashradius_rl" );
	g_weaponConfig.rocketSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_rl, 1000, "g_velocity_rl", 1 );
	g_weaponConfig.rocketAccelerationFactor = G_ReadWeaponFloatCvarNonNegative( &g_accelFactor_rl, 1.0f, "g_accelFactor_rl" );
	g_weaponConfig.rocketAccelerationRate = G_ReadWeaponCvarNonNegative( &g_accelRate_rl, 16, "g_accelRate_rl" );
	g_weaponConfig.rocketSplashOffset = G_ReadWeaponCvarRaw( &g_rocketsplashOffset, -10, "g_rocketsplashOffset" );
	g_weaponConfig.plasmaDamage = G_ReadWeaponCvar( &g_damage_pg, 20, "g_damage_pg" );
	g_weaponConfig.plasmaSplashDamage = G_ReadWeaponCvar( &g_splashDamage_pg, 15, "g_splashdamage_pg" );
	g_weaponConfig.plasmaSplashRadius = G_ReadWeaponCvar( &g_splashRadius_pg, 20, "g_splashradius_pg" );
	g_weaponConfig.plasmaSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_pg, 2000, "g_velocity_pg", 1 );
	g_weaponConfig.plasmaAccelerationFactor = G_ReadWeaponFloatCvarNonNegative( &g_accelFactor_pg, 1.0f, "g_accelFactor_pg" );
	g_weaponConfig.plasmaAccelerationRate = G_ReadWeaponCvarNonNegative( &g_accelRate_pg, 16, "g_accelRate_pg" );
	g_weaponConfig.lightningDamage = G_ReadWeaponCvar( &g_damage_lg, 6, "g_damage_lg" );
	g_weaponConfig.lightningFalloffDamage = G_ReadWeaponCvarNonNegative( &g_damage_lg_falloff, 0, "g_damage_lg_falloff" );
	g_weaponConfig.lightningFalloffRange = G_ReadWeaponCvarNonNegative( &g_range_lg_falloff, 768, "g_range_lg_falloff" );
	g_weaponConfig.railJumpStrength = G_ReadWeaponCvarNonNegative( &g_railJump, 0, "g_railJump" );
	g_weaponConfig.railgunDamage = G_ReadWeaponCvar( &g_damage_rg, 80, "g_damage_rg" );
	g_weaponConfig.bfgDamage = G_ReadWeaponCvar( &g_damage_bfg, 100, "g_damage_bfg" );
	g_weaponConfig.bfgSplashDamage = G_ReadWeaponCvar( &g_splashDamage_bfg, 100, "g_splashdamage_bfg" );
	g_weaponConfig.bfgSplashRadius = G_ReadWeaponCvar( &g_splashRadius_bfg, 80, "g_splashradius_bfg" );
	g_weaponConfig.bfgSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_bfg, 1800, "g_velocity_bfg", 1 );
	g_weaponConfig.bfgAccelerationFactor = G_ReadWeaponFloatCvarNonNegative( &g_accelFactor_bfg, 1.0f, "g_accelFactor_bfg" );
	g_weaponConfig.bfgAccelerationRate = G_ReadWeaponCvarNonNegative( &g_accelRate_bfg, 16, "g_accelRate_bfg" );
	g_weaponConfig.grappleDamage = G_ReadWeaponCvar( &g_damage_gh, 10, "g_damage_gh" );
	g_weaponConfig.grappleSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_gh, 1800, "g_velocity_gh", 1 );
	g_weaponConfig.gauntletSpeedFactor = G_ReadWeaponFloatCvarNonNegative( &g_gauntletSpeedFactor, 1.0f, "g_gauntletSpeedFactor" );
	g_weaponConfig.lightningDischargeFlags = G_ReadWeaponCvarNonNegative( &g_lightningDischarge, 0, "g_lightningDischarge" );
	g_weaponConfig.railgunHeadshotDamage = G_ReadWeaponCvarNonNegative( &g_headShotDamage_rg, 0, "g_headShotDamage_rg" );
	g_weaponConfig.machinegunIronsightsScale = G_ReadWeaponFloatCvarNonNegative( &g_ironsights_mg, 1.0f, "g_ironsights_mg" );
	g_weaponConfig.midAirMinimumHeight = G_ReadWeaponCvarNonNegative( &g_midAirMinHeight, 96, "g_midAirMinHeight" );
	g_weaponConfig.nailgunCount = G_ReadWeaponCvarNonNegative( &g_nailcount, 10, "g_nailcount" );
	g_weaponConfig.nailgunDamage = G_ReadWeaponCvar( &g_damage_ng, 12, "g_damage_ng" );
	g_weaponConfig.nailgunSpeed = G_ReadWeaponCvarAtLeast( &g_nailspeed, 1000, "g_nailspeed", 1 );
	g_weaponConfig.nailgunSpread = G_ReadWeaponCvarNonNegative( &g_nailspread, 400, "g_nailspread" );
	g_weaponConfig.nailgunBounceCount = G_ReadWeaponCvarNonNegative( &g_nailbounce, 1, "g_nailbounce" );
	g_weaponConfig.nailgunBounceEnabled = ( g_weaponConfig.nailgunBounceCount > 0 ) ? qtrue : qfalse;
	g_weaponConfig.nailgunBouncePercentage = G_ReadWeaponCvarNonNegative( &g_nailbouncepercentage, 65, "g_nailbouncepercentage" );
	if ( g_weaponConfig.nailgunBouncePercentage > 100 ) {
		g_weaponConfig.nailgunBouncePercentage = 100;
	}
	g_weaponConfig.proximityLauncherDamage = G_ReadWeaponCvarNonNegative( &g_damage_pl, 0, "g_damage_pl" );
	g_weaponConfig.proximityLauncherSplashDamage = G_ReadWeaponCvar( &g_splashDamage_pl, 100, "g_splashdamage_pl" );
	g_weaponConfig.proximityLauncherSplashRadius = G_ReadWeaponCvar( &g_splashRadius_pl, 150, "g_splashradius_pl" );
	g_weaponConfig.quadDamageMultiplier = G_ReadWeaponFloatCvarNonNegative( &g_quadDamageFactor, 3.0f, "g_quadDamageFactor" );
	g_weaponConfig.guidedRocketEnabled = G_ReadWeaponBoolCvar( &g_guidedRocket, qfalse, "g_guidedRocket" );
	g_weaponConfig.quadHogEnabled = G_ReadWeaponBoolCvar( &g_quadHog, qfalse, "g_quadHog" );
	g_weaponConfig.quadHogIdleSeconds = G_ReadWeaponCvarRaw( &g_quadHogIdle, 20, "g_quadHogIdle" );
	if ( g_weaponConfig.quadHogIdleSeconds < 0 ) {
		g_weaponConfig.quadHogIdleSeconds = 0;
	}
	g_weaponConfig.quadHogTimeSeconds = G_ReadWeaponCvarRaw( &g_quadHogTime, 60, "g_quadHogTime" );
	if ( g_weaponConfig.quadHogTimeSeconds < 0 ) {
		g_weaponConfig.quadHogTimeSeconds = 0;
	}
	g_weaponConfig.quadHogPingRateMilliseconds = G_ReadWeaponCvarRaw( &g_quadHogPingRate, 1500, "g_quadHogPingRate" );
	if ( g_weaponConfig.quadHogPingRateMilliseconds < 0 ) {
		g_weaponConfig.quadHogPingRateMilliseconds = 0;
	}
}

void G_UpdateWeaponConfig( void ) {
	G_InitWeaponConfig();
}

/*
=============
G_InitFlagConfig

Initializes the cached flag configuration cvars so other systems can read them without repeated VM lookups.
=============
*/
void G_InitFlagConfig( void ) {
	G_UpdateFlagConfig();
}

/*
=============
G_UpdateFlagConfig

Refreshes the cached flag physics and toss settings from the latest cvar values.
=============
*/
void G_UpdateFlagConfig( void ) {
	float	bounce;

	bounce = g_flagBounce.value;
	if ( bounce < 0.0f ) {
		bounce = 0.0f;
	} else if ( bounce > 1.0f ) {
		bounce = 1.0f;
	}
	g_flagConfig.flagBounce = bounce;

	g_flagConfig.flagPhysics = ( g_flagPhysics.integer < 0 ) ? 0 : g_flagPhysics.integer;
	g_flagConfig.throwFlagVelocity = ( g_throwFlagVelocity.integer < 0 ) ? 0 : g_throwFlagVelocity.integer;
	g_flagConfig.throwFlagForwardMult = ( g_throwFlagForwardMult.value < 0.0f ) ? 0.0f : g_throwFlagForwardMult.value;
	g_flagConfig.tackleFlag = ( g_tackleFlag.integer != 0 ) ? qtrue : qfalse;
	g_flagConfig.returnOnSuicide = ( g_returnFlagOnSuicide.integer != 0 ) ? qtrue : qfalse;
	g_flagConfig.droppedFlagBonus = ( g_droppedFlagBonus.integer < 0 ) ? 0 : g_droppedFlagBonus.integer;
	g_flagConfig.dropTimeoutMs = DEFAULT_FLAG_DROPPED_TIMEOUT_MS;
	g_flagConfig.neutralFlagPingTimeMs = ( g_neutralFlagPingTime.integer < 0 ) ? 0 : g_neutralFlagPingTime.integer;
}

/*
=============
G_UpdateItemTimerConfig

Synchronises the item timer configuration cvars with all clients.
=============
*/
static void G_UpdateItemTimerConfig( qboolean forceBroadcast ) {
	int	enabled;
	int	height;

	enabled = g_itemTimers.integer ? 1 : 0;
	height = g_itemHeight.integer;
	if ( height <= 0 ) {
		height = ITEM_TIMER_DEFAULT_HEIGHT;
	} else if ( height > ITEM_TIMER_MAX_HEIGHT ) {
		height = ITEM_TIMER_MAX_HEIGHT;
	}

	if ( !forceBroadcast && enabled == s_lastItemTimerEnabled && height == s_lastItemTimerHeight ) {
		return;
	}

	s_lastItemTimerEnabled = enabled;
	s_lastItemTimerHeight = height;

	G_BroadcastItemTimerState( enabled, height );
}

static void LevelCheckTimers( void );
static void G_CheckTimeoutExpired( void );
void G_UpdateMatchStateConfigString( void );
int G_BuildExitRuleLimitMsec( int minutes, int bonusMsec );
static qboolean G_StartOrExtendOvertime( void );
static void G_StopOvertime( void );
static void G_TrackSuddenDeathAnnouncements( void );
static qboolean G_ClearConnectedReadyStates( qboolean updateUserinfo );
static void G_ResetDuelWarmupState( qboolean clearReadyFlags );
void G_InitGame( int levelTime, int randomSeed, int restart );
void G_RunFrame( int levelTime );
void G_ShutdownGame( int restart );
void G_RegisterCvars(void);
void CheckExitRules( void );

/*
================
G_NativeInit
================
*/
static void G_NativeInit( int levelTime, int randomSeed, qboolean restart ) {
	G_InitGame( levelTime, randomSeed, restart );
}

/*
================
G_NativeShutdown
================
*/
static void G_NativeShutdown( qboolean restart ) {
	G_ShutdownGame( restart );
}

/*
================
G_NativeClientConnect
================
*/
static const char *G_NativeClientConnect( int clientNum, qboolean firstTime, qboolean isBot ) {
	return ClientConnect( clientNum, firstTime, isBot );
}


/*
================
vmMain

This is the only way control passes into the module.
This must be the very first function compiled into the .q3vm file
================
*/
int vmMain( int command, int arg0, int arg1, int arg2, int arg3, int arg4, int arg5, int arg6, int arg7, int arg8, int arg9, int arg10, int arg11  ) {
	switch ( command ) {
	case GAME_INIT:
		G_NativeInit( arg0, arg1, arg2 ? qtrue : qfalse );
		return 0;
	case GAME_SHUTDOWN:
		G_NativeShutdown( arg0 ? qtrue : qfalse );
		return 0;
	case GAME_CLIENT_CONNECT:
		return (int)(intptr_t)G_NativeClientConnect( arg0, arg1 ? qtrue : qfalse, arg2 ? qtrue : qfalse );
	case GAME_CLIENT_THINK:
		ClientThink( arg0 );
		return 0;
	case GAME_CLIENT_USERINFO_CHANGED:
		ClientUserinfoChanged( arg0 );
		return 0;
	case GAME_CLIENT_DISCONNECT:
		ClientDisconnect( arg0 );
		return 0;
	case GAME_CLIENT_BEGIN:
		ClientBegin( arg0 );
		return 0;
	case GAME_CLIENT_COMMAND:
		ClientCommand( arg0 );
		return 0;
	case GAME_RUN_FRAME:
		G_RunFrame( arg0 );
		return 0;
	case GAME_CONSOLE_COMMAND:
		return ConsoleCommand();
	case BOTAI_START_FRAME:
		return BotAIStartFrame( arg0 );
	case GAME_CAN_CLIENT_SEE_CLIENT:
		return G_CanClientSeeClient( arg0, arg1 );
	case GAME_FREEZE_CAN_SEE_THAW_PROGRESS_EVENT:
		return G_FreezeCanSeeThawProgressEvent( arg0, arg1 );
	case GAME_IS_OBJECTIVE_ENTITY:
		return G_IsObjectiveEntity( arg0 );
	case GAME_SHOULD_SUPPRESS_VOICE_TO_CLIENT:
		return G_ShouldSuppressVoiceToClient( arg0, arg1 );
	case GAME_IS_CLIENT_ADMIN:
		return G_IsClientAdmin( arg0 );
	case GAME_ARE_ENEMY_CLIENTS:
		return G_AreEnemyClients( arg0, arg1 );
	case GAME_GET_CLIENT_SCORE:
		return G_GetClientScore( arg0 );
	}

	return -1;
}

#ifdef _MSC_VER
#pragma warning(push)
#pragma warning(disable:4090)
#endif
static void *g_nativeExports[GAME_NATIVE_EXPORT_COUNT] = {
	[GAME_NATIVE_EXPORT_SHUTDOWN] = G_NativeShutdown,
	[GAME_NATIVE_EXPORT_RUN_FRAME] = G_RunFrame,
	[GAME_NATIVE_EXPORT_REGISTER_CVARS] = G_RegisterCvars,
	[GAME_NATIVE_EXPORT_INIT] = G_NativeInit,
	[GAME_NATIVE_EXPORT_CONSOLE_COMMAND] = ConsoleCommand,
	[GAME_NATIVE_EXPORT_CLIENT_USERINFO_CHANGED] = ClientUserinfoChanged,
	[GAME_NATIVE_EXPORT_CLIENT_THINK] = ClientThink,
	[GAME_NATIVE_EXPORT_CLIENT_DISCONNECT] = ClientDisconnect,
	[GAME_NATIVE_EXPORT_CLIENT_CONNECT] = G_NativeClientConnect,
	[GAME_NATIVE_EXPORT_CLIENT_COMMAND] = ClientCommand,
	[GAME_NATIVE_EXPORT_CLIENT_BEGIN] = ClientBegin,
	[GAME_NATIVE_EXPORT_BOTAI_START_FRAME] = BotAIStartFrame,
	[GAME_NATIVE_EXPORT_CAN_CLIENT_SEE_CLIENT] = G_CanClientSeeClient,
	[GAME_NATIVE_EXPORT_FREEZE_CAN_SEE_THAW_PROGRESS_EVENT] = G_FreezeCanSeeThawProgressEvent,
	[GAME_NATIVE_EXPORT_IS_OBJECTIVE_ENTITY] = G_IsObjectiveEntity,
	[GAME_NATIVE_EXPORT_SHOULD_SUPPRESS_VOICE_TO_CLIENT] = G_ShouldSuppressVoiceToClient,
	[GAME_NATIVE_EXPORT_IS_CLIENT_ADMIN] = G_IsClientAdmin,
	[GAME_NATIVE_EXPORT_ARE_ENEMY_CLIENTS] = G_AreEnemyClients,
	[GAME_NATIVE_EXPORT_GET_CLIENT_SCORE] = G_GetClientScore
};
#ifdef _MSC_VER
#pragma warning(pop)
#endif

/*
================
G_GetNativeExportTable
================
*/
void **G_GetNativeExportTable( void ) {
	return g_nativeExports;
}


void QDECL G_Printf( const char *fmt, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, fmt);
	vsprintf (text, fmt, argptr);
	va_end (argptr);

	trap_Printf( text );
}

void QDECL G_Error( const char *fmt, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, fmt);
	vsprintf (text, fmt, argptr);
	va_end (argptr);

	trap_Error( text );
}

/*
================
G_FindTeams

Chain together all entities with a matching team field.
Entity teams are used for item groups and multi-entity mover groups.

All but the first will have the FL_TEAMSLAVE flag set and teammaster field set
All but the last will have the teamchain field set to the next one
================
*/
void G_FindTeams( void ) {
	gentity_t	*e, *e2;
	int		i, j;
	int		c, c2;

	c = 0;
	c2 = 0;
	for ( i=1, e=g_entities+i ; i < level.num_entities ; i++,e++ ){
		if (!e->inuse)
			continue;
		if (!e->team)
			continue;
		if (e->flags & FL_TEAMSLAVE)
			continue;
		e->teammaster = e;
		c++;
		c2++;
		for (j=i+1, e2=e+1 ; j < level.num_entities ; j++,e2++)
		{
			if (!e2->inuse)
				continue;
			if (!e2->team)
				continue;
			if (e2->flags & FL_TEAMSLAVE)
				continue;
			if (!strcmp(e->team, e2->team))
			{
				c2++;
				e2->teamchain = e->teamchain;
				e->teamchain = e2;
				e2->teammaster = e;
				e2->flags |= FL_TEAMSLAVE;

				// make sure that targets only point at the master
				if ( e2->targetname ) {
					e->targetname = e2->targetname;
					e2->targetname = NULL;
				}
			}
		}
	}

	G_Printf ("%i teams with %i entities\n", c, c2);
}

void G_RemapTeamShaders() {
	char string[1024];
	char redTeam[MAX_CVAR_VALUE_STRING];
	char blueTeam[MAX_CVAR_VALUE_STRING];
	float f = level.time * 0.001;

	G_ReadServerTeamName( TEAM_RED, redTeam, sizeof( redTeam ) );
	G_ReadServerTeamName( TEAM_BLUE, blueTeam, sizeof( blueTeam ) );

	Com_sprintf( string, sizeof(string), "team_icon/%s_red", redTeam );
	AddRemap("textures/ctf2/redteam01", string, f); 
	AddRemap("textures/ctf2/redteam02", string, f); 
	Com_sprintf( string, sizeof(string), "team_icon/%s_blue", blueTeam );
	AddRemap("textures/ctf2/blueteam01", string, f); 
	AddRemap("textures/ctf2/blueteam02", string, f); 
	trap_SetConfigstring(CS_SHADERSTATE, BuildShaderStateConfig());
}

/*
=============
G_UpdateCustomSettingsMaskForCvar

Marks the published custom-settings digest dirty when a tracked gameplay cvar
entry participates in the retail custom-settings mask.
=============
*/
static void G_UpdateCustomSettingsMaskForCvar( const cvarTable_t *cv ) {
	if ( !cv || !cv->customSetting ) {
		return;
	}

	s_customSettingsDirty = qtrue;
}

/*
=============
G_ResetClientInactivityWarnings

Clears the per-client inactivity-warning latch after the inactivity timer cvar changes.
=============
*/
static void G_ResetClientInactivityWarnings( void ) {
	int	i;

	if ( !level.clients ) {
		return;
	}

	for ( i = 0; i < level.maxclients; i++ ) {
		if ( level.clients[i].pers.connected == CON_CONNECTED ) {
			level.clients[i].inactivityWarning = qfalse;
		}
	}
}

/*
=================
G_RegisterCvars
=================
*/
void G_RegisterCvars( void ) {
	int		i;
	cvarTable_t	*cv;

	for ( i = 0, cv = gameCvarTable ; i < gameCvarTableSize ; i++, cv++ ) {
		trap_Cvar_Register( cv->vmCvar, cv->cvarName,
			cv->defaultString, cv->cvarFlags );
		if ( cv->vmCvar ) {
			cv->modificationCount = cv->vmCvar->modificationCount;
		}

		G_UpdateCustomSettingsMaskForCvar( cv );
	}

	LegacyCvar_RegisterAliases( s_legacyCvarAliases, ARRAY_LEN( s_legacyCvarAliases ) );
	s_customSettingsDirty = qtrue;

	G_Config_RegisterCvars();
	G_Config_UpdateCvars();
	LegacyCvar_UpdateAliases( s_legacyCvarAliases, ARRAY_LEN( s_legacyCvarAliases ) );
	G_RegisterPmoveCvars();

	// check some things
	if ( g_gametype.integer < 0 || g_gametype.integer >= GT_MAX_GAME_TYPE ) {
		G_Printf( "g_gametype %i is out of range, defaulting to 0\n", g_gametype.integer );
		trap_Cvar_Set( "g_gametype", "0" );
	}

	trap_Cvar_Register( NULL, "g_version", QL_GAME_VERSION, CVAR_ROM );

	s_factoryModCount = g_factory.modificationCount;
	s_inactivityModCount = g_inactivity.modificationCount;
	s_itemTimersModCount = g_itemTimers.modificationCount;
	s_itemHeightModCount = g_itemHeight.modificationCount;
	s_forceSmallScoreboardMessageModCount = g_forceSmallScoreboardMessage.modificationCount;
	s_forceSendConfigstringModCount = g_forceSendConfigstring.modificationCount;
	s_forceAtmosphericEffectsModCount = g_forceAtmosphericEffects.modificationCount;
	s_forceDmgThroughSurfaceModCount = g_forceDmgThroughSurface.modificationCount;
	s_armorTieredModCount = g_armorTiered.modificationCount;
	s_disableLoadoutModCount = g_disableLoadout.modificationCount;
	s_loadoutModCount = g_loadout.modificationCount;
	s_startingWeaponsModCount = g_startingWeapons.modificationCount;
	s_roundWarmupDelayModCount = g_roundWarmupDelay.modificationCount;
	s_teamSizeMinModCount = g_teamSizeMin.modificationCount;
	s_worldspawnAtmosphere[0] = '\0';
	s_lastForcedCosmeticsPayload[0] = '\0';
	G_InitWeaponConfig();
	G_InitWeaponReloadConfig();
	G_InitKnockbackConfig();
	G_InitStartingAmmoConfig();
	G_InitAmmoPackConfig();
	G_InitFlagConfig();
	G_InitFactoryCvarConfig();
	G_InitMatchFactoryConfig();
}

/*
=============
G_InitPublishedCvarState

Publishes the retail init-time configstring slab after the effective cvar set
has been finalized for the new level.
=============
*/
static void G_InitPublishedCvarState( void ) {
	G_PmoveSetConfigstringsReady( qtrue );
	G_RefreshPmoveSettings();
	G_UpdatePlayerCylindersConfigstring( qtrue );
	G_MatchConfig_UpdateConfigstrings();
	G_UpdateModeSpecificConfigstrings( qtrue );
	G_UpdateCustomSettingsConfigstring( qtrue );
	level.disableLoadoutMapMask = 0;
	G_UpdateDisableLoadoutConfigstrings();
	G_UpdateServerSettingsInfoConfigstrings( qtrue );
	G_UpdateItemTimerConfig( qtrue );
	G_UpdateForcedCosmeticsConfigstring( qtrue );
	G_UpdateGametypeTutorialText();
	G_UpdateWeaponReloadConfigstring( qtrue );
	G_UpdatePlayerAppearanceConfigstring( qtrue );
}

/*
=============
G_InitLevelCvarMirrors

Reapplies the source-side level mirrors that are stored outside retail's
zeroed level blob so the post-memset state matches the active cvar snapshot.
=============
*/
static void G_InitLevelCvarMirrors( void ) {
	level.warmupModificationCount = g_warmup.modificationCount;
	G_SyncAdminConfig();
	G_SyncMatchFactoryConfigToLevel();
	level.quadHogEnabled = ( g_weaponConfig.quadHogEnabled != 0 );
	level.quadHogOwner = ENTITYNUM_NONE;
	level.quadHogExpireTime = 0;
	level.quadHogLastActiveTime = 0;
	level.quadHogNextPingTime = 0;
}

void G_UpdateCvars( void ) {
        int                     i;
        cvarTable_t     *cv;
        qboolean remapped = qfalse;
	qboolean loadoutConfigstringsDirty = qfalse;

        for ( i = 0, cv = gameCvarTable ; i < gameCvarTableSize ; i++, cv++ ) {
                if ( cv->vmCvar ) {
                        trap_Cvar_Update( cv->vmCvar );

                        if ( cv->modificationCount != cv->vmCvar->modificationCount ) {
                                cv->modificationCount = cv->vmCvar->modificationCount;

                                if ( cv->trackChange ) {
                                        trap_SendServerCommand( -1, va("print \"Server: %s changed to %s\n\"",
                                                cv->cvarName, cv->vmCvar->string ) );
                                }

				G_UpdateCustomSettingsMaskForCvar( cv );

                                if (cv->teamShader) {
                                        remapped = qtrue;
                                }
                        }
                }
        }

	if (remapped) {
		G_RemapTeamShaders();
	}

	if ( g_teamSizeMin.modificationCount != s_teamSizeMinModCount ) {
		s_teamSizeMinModCount = g_teamSizeMin.modificationCount;
		G_UpdateMatchStateConfigString();
	}

	if ( g_roundWarmupDelay.modificationCount != s_roundWarmupDelayModCount ) {
		s_roundWarmupDelayModCount = g_roundWarmupDelay.modificationCount;
		G_RoundHandleWarmupDelayCvarUpdate();
	}

	if ( g_armorTiered.modificationCount != s_armorTieredModCount ) {
		s_armorTieredModCount = g_armorTiered.modificationCount;
		G_SyncAllClientArmorTiers();
	}

	if ( g_inactivity.modificationCount != s_inactivityModCount ) {
		s_inactivityModCount = g_inactivity.modificationCount;
		G_ResetClientInactivityWarnings();
	}

	if ( g_factory.modificationCount != s_factoryModCount ) {
		s_factoryModCount = g_factory.modificationCount;
		Factory_ApplyCurrentSelection( qfalse );
	}

	G_Config_UpdateCvars();

	G_UpdateWeaponConfig();
	G_UpdateWeaponReloadConfig();
	G_UpdateKnockbackConfig();
	G_UpdateStartingAmmoConfig();
	G_UpdateAmmoPackConfig();
	G_UpdateFlagConfig();
	G_UpdateFactoryCvarConfig();
        G_UpdateMatchFactoryConfig();
	G_SyncMatchFactoryConfigToLevel();
	if ( g_loadout.modificationCount != s_loadoutModCount ) {
		s_loadoutModCount = g_loadout.modificationCount;
		loadoutConfigstringsDirty = qtrue;
	}
	if ( g_startingWeapons.modificationCount != s_startingWeaponsModCount ) {
		s_startingWeaponsModCount = g_startingWeapons.modificationCount;
		loadoutConfigstringsDirty = qtrue;
	}
	if ( g_itemTimers.modificationCount != s_itemTimersModCount || g_itemHeight.modificationCount != s_itemHeightModCount ) {
		s_itemTimersModCount = g_itemTimers.modificationCount;
		s_itemHeightModCount = g_itemHeight.modificationCount;
		G_UpdateItemTimerConfig( qfalse );
	}
	if ( g_forceSmallScoreboardMessage.modificationCount != s_forceSmallScoreboardMessageModCount ||
		 g_forceSendConfigstring.modificationCount != s_forceSendConfigstringModCount ||
		 g_forceAtmosphericEffects.modificationCount != s_forceAtmosphericEffectsModCount ||
		 g_forceDmgThroughSurface.modificationCount != s_forceDmgThroughSurfaceModCount ) {
		s_forceSmallScoreboardMessageModCount = g_forceSmallScoreboardMessage.modificationCount;
		s_forceSendConfigstringModCount = g_forceSendConfigstring.modificationCount;
		s_forceAtmosphericEffectsModCount = g_forceAtmosphericEffects.modificationCount;
		s_forceDmgThroughSurfaceModCount = g_forceDmgThroughSurface.modificationCount;
		G_UpdateForcedCosmeticsConfigstring( qtrue );
	}
	if ( g_disableLoadout.modificationCount != s_disableLoadoutModCount ) {
		s_disableLoadoutModCount = g_disableLoadout.modificationCount;
		loadoutConfigstringsDirty = qtrue;
	}
	if ( loadoutConfigstringsDirty ) {
		G_UpdateDisableLoadoutConfigstrings();
	}
	level.quadHogEnabled = ( g_weaponConfig.quadHogEnabled != 0 );

	G_SyncAdminConfig();
	G_UpdateTrainingState();
	G_UpdateGametypeTutorialText();
	G_RefreshPmoveSettings();
	G_UpdatePlayerCylindersConfigstring( qfalse );
	G_UpdateServerSettingsInfoConfigstrings( qfalse );
	G_UpdateWeaponReloadConfigstring( qfalse );
	G_UpdatePlayerAppearanceConfigstring( qfalse );
	G_UpdateModeSpecificConfigstrings( qfalse );
	G_UpdateCustomSettingsConfigstring( qfalse );
}

/*
=============
G_CustomSettingsDirty

Returns whether any tracked gameplay CVars have changed since the last
custom-settings digest was published.
=============
*/
qboolean G_CustomSettingsDirty( void ) {
	return s_customSettingsDirty;
}

/*
=============
G_ClearCustomSettingsDirtyFlag

Marks the custom-settings digest as up-to-date so later updates can wait
for additional gameplay overrides before rebuilding the string.
=============
*/
void G_ClearCustomSettingsDirtyFlag( void ) {
	s_customSettingsDirty = qfalse;
}

/*
=============
G_SyncPlayerCylinderFlag

Keeps the retail player-cylinder collision bit aligned with the published
player-cylinder gameplay toggle for one active client entity.
=============
*/
void G_SyncPlayerCylinderFlag( gentity_t *ent ) {
	if ( !ent || !ent->client ) {
		return;
	}

	if ( g_playerCylinders.integer != 0
		&& ent->client->pers.connected == CON_CONNECTED
		&& ent->client->sess.sessionTeam != TEAM_SPECTATOR ) {
		ent->r.svFlags |= SVF_CAPSULE;
	} else {
		ent->r.svFlags &= ~SVF_CAPSULE;
	}
}

/*
=============
G_SyncPlayerCylinderClientFlags

Refreshes the capsule collision flag for every spawned client after the
retail player-cylinder cvar changes.
=============
*/
static void G_SyncPlayerCylinderClientFlags( void ) {
	int	i;

	for ( i = 0; i < level.maxclients; i++ ) {
		gentity_t	*ent;

		ent = &g_entities[i];
		if ( !ent->client || ent->client->pers.connected != CON_CONNECTED ) {
			continue;
		}

		G_SyncPlayerCylinderFlag( ent );
	}
}

/*
=============
G_UpdatePlayerCylindersConfigstring

Publishes the retail dedicated numeric player-cylinder toggle configstring.
=============
*/
static void G_UpdatePlayerCylindersConfigstring( qboolean forceBroadcast ) {
	char	payload[32];

	Com_sprintf( payload, sizeof( payload ), "%i", g_playerCylinders.integer );
	if ( !forceBroadcast && !Q_stricmp( payload, s_playerCylindersPayload ) ) {
		return;
	}

	G_SyncPlayerCylinderClientFlags();
	trap_SetConfigstring( CS_PLAYER_CYLINDERS, payload );
	Q_strncpyz( s_playerCylindersPayload, payload, sizeof( s_playerCylindersPayload ) );
}

/*
=============
G_UpdateServerSettingsInfoConfigstrings

Publishes the retail server-settings info-string slab consumed by the UI ownerdraw.
=============
*/
static void G_UpdateServerSettingsInfoConfigstrings( qboolean forceBroadcast ) {
	char	payloadA[MAX_INFO_STRING];
	char	payloadB[MAX_INFO_STRING];

	payloadA[0] = '\0';
	payloadB[0] = '\0';

	Info_SetValueForKey( payloadA, SERVER_SETTINGS_KEY_ARMOR_TIERED, va( "%i", g_armorTiered.integer ) );
	Info_SetValueForKey( payloadB, SERVER_SETTINGS_KEY_QUAD_DAMAGE_FACTOR, va( "%i", g_quadDamageFactor.integer ) );
	Info_SetValueForKey( payloadB, SERVER_SETTINGS_KEY_GRAVITY, va( "%i", g_gravity.integer ) );

	if ( forceBroadcast || Q_stricmp( payloadA, s_serverSettingsInfoPayloadA ) != 0 ) {
		trap_SetConfigstring( CS_SERVER_SETTINGS_INFO_A, payloadA );
		Q_strncpyz( s_serverSettingsInfoPayloadA, payloadA, sizeof( s_serverSettingsInfoPayloadA ) );
	}

	if ( forceBroadcast || Q_stricmp( payloadB, s_serverSettingsInfoPayloadB ) != 0 ) {
		trap_SetConfigstring( CS_SERVER_SETTINGS_INFO_B, payloadB );
		Q_strncpyz( s_serverSettingsInfoPayloadB, payloadB, sizeof( s_serverSettingsInfoPayloadB ) );
	}
}

/*
=============
G_UpdatePlayerAppearanceConfigstring

Publishes the retail player-appearance info string consumed by cgame's
forced-player visual parser.
=============
*/
static void G_UpdatePlayerAppearanceConfigstring( qboolean forceBroadcast ) {
	char	payload[MAX_INFO_STRING];

	payload[0] = '\0';

	Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERMODEL_OVERRIDE, g_playermodelOverride.string );
	Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERHEADMODEL_OVERRIDE, g_playerheadmodelOverride.string );
	Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_ALLOW_CUSTOM_HEADMODELS, va( "%i", g_allowCustomHeadmodels.integer ) );
	Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERHEAD_SCALE, va( "%g", g_playerheadScale.value ) );
	Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERHEAD_SCALE_OFFSET, va( "%g", g_playerheadScaleOffset.value ) );
	Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERMODEL_SCALE, va( "%g", g_playerModelScale.value ) );

	if ( forceBroadcast || Q_stricmp( payload, s_playerAppearancePayload ) != 0 ) {
		trap_SetConfigstring( CS_PLAYER_APPEARANCE, payload );
		Q_strncpyz( s_playerAppearancePayload, payload, sizeof( s_playerAppearancePayload ) );
	}
}

/*
=============
G_UpdateWeaponReloadConfigstring

Publishes the retail compact weapon-refire configstring consumed by cgame's
dedicated reload parser.
=============
*/
static void G_UpdateWeaponReloadConfigstring( qboolean forceBroadcast ) {
	char	payload[MAX_INFO_STRING];

	Com_sprintf(
		payload,
		sizeof( payload ),
		"%i %i %i %i %i %i %i %i %i %i %i %i %i %i",
		g_pmoveSettings.weaponReloadTimes[WP_GAUNTLET],
		g_pmoveSettings.weaponReloadTimes[WP_MACHINEGUN],
		g_pmoveSettings.weaponReloadTimes[WP_SHOTGUN],
		g_pmoveSettings.weaponReloadTimes[WP_GRENADE_LAUNCHER],
		g_pmoveSettings.weaponReloadTimes[WP_ROCKET_LAUNCHER],
		g_pmoveSettings.weaponReloadTimes[WP_LIGHTNING],
		g_pmoveSettings.weaponReloadTimes[WP_RAILGUN],
		g_pmoveSettings.weaponReloadTimes[WP_PLASMAGUN],
		g_pmoveSettings.weaponReloadTimes[WP_BFG],
		g_pmoveSettings.weaponReloadTimes[WP_GRAPPLING_HOOK],
		g_pmoveSettings.weaponReloadTimes[WP_NAILGUN],
		g_pmoveSettings.weaponReloadTimes[WP_PROX_LAUNCHER],
		g_pmoveSettings.weaponReloadTimes[WP_CHAINGUN],
		g_pmoveSettings.weaponReloadTimes[WP_HEAVY_MACHINEGUN]
	);

	if ( forceBroadcast || Q_stricmp( payload, s_weaponReloadPayload ) != 0 ) {
		trap_SetConfigstring( CS_WEAPON_RELOAD_TIMES, payload );
		Q_strncpyz( s_weaponReloadPayload, payload, sizeof( s_weaponReloadPayload ) );
	}
}

/*
=============
G_UpdateDominationCaptureTimeConfigstring

Publishes the retail Domination capture-time configstring sourced from g_domCapTime.
=============
*/
static void G_UpdateDominationCaptureTimeConfigstring( qboolean forceBroadcast ) {
	char	payload[32];

	Com_sprintf( payload, sizeof( payload ), "%f", g_domCapTime.value );
	if ( !forceBroadcast && !Q_stricmp( payload, s_dominationCaptureTimePayload ) ) {
		return;
	}

	trap_SetConfigstring( CS_DOMINATION_CAPTURE_TIME, payload );
	Q_strncpyz( s_dominationCaptureTimePayload, payload, sizeof( s_dominationCaptureTimePayload ) );
}

/*
=============
G_UpdateRRInfectedSurvivorPingRateConfigstring

Publishes the retail Red Rover survivor-ping cadence configstring.
=============
*/
static void G_UpdateRRInfectedSurvivorPingRateConfigstring( qboolean forceBroadcast ) {
	char	payload[32];

	Com_sprintf( payload, sizeof( payload ), "%f", g_rrInfectedSurvivorPingRate.value );
	if ( !forceBroadcast && !Q_stricmp( payload, s_rrInfectedSurvivorPingRatePayload ) ) {
		return;
	}

	trap_SetConfigstring( CS_RR_INFECTED_SURVIVOR_PING_RATE, payload );
	Q_strncpyz( s_rrInfectedSurvivorPingRatePayload, payload, sizeof( s_rrInfectedSurvivorPingRatePayload ) );
}

/*
=============
G_UpdateModeSpecificConfigstrings

Refreshes the retail mode-specific numeric configstrings owned by qagame.
=============
*/
static void G_UpdateModeSpecificConfigstrings( qboolean forceBroadcast ) {
	G_UpdateDominationCaptureTimeConfigstring( forceBroadcast );
	G_UpdateRRInfectedSurvivorPingRateConfigstring( forceBroadcast );
}

/*
=============
G_ComputeCustomSettingsMask

Aggregates the retail custom-settings mask from the current effective gameplay
configuration instead of the older source-only customSetting flag walk.
=============
*/
static uint64_t G_ComputeCustomSettingsMask( void ) {
	uint64_t	mask;

	mask = G_ComputeConfigCustomSettingsMask();

	if ( G_PmoveHasAirControlCustomSetting() ) {
		mask |= CUSTOM_SETTING_AIR_CONTROL;
	}
	if ( G_PmoveHasRampJumpCustomSetting() ) {
		mask |= CUSTOM_SETTING_RAMP_JUMP;
	}
	if ( g_speed.integer != 320 || G_PmoveHasPhysicsCustomSetting() ) {
		mask |= CUSTOM_SETTING_PHYSICS;
	}
	if ( G_PmoveHasWeaponSwitchingCustomSetting() ) {
		mask |= CUSTOM_SETTING_WEAPON_SWITCHING;
	}
	if ( g_instaGib.integer != 0 ) {
		mask |= CUSTOM_SETTING_INSTAGIB;
	}
	if ( g_quadHog.integer != 0 ) {
		mask |= CUSTOM_SETTING_QUAD_HOG;
	}
	if ( g_dropDamagedHealth.integer != 0 ) {
		mask |= CUSTOM_SETTING_DROP_HEALTH;
	}
	if ( g_vampiricDamage.value != 0.0f ) {
		mask |= CUSTOM_SETTING_VAMPIRIC_DAMAGE;
	}
	if ( g_headShotDamage_rg.integer != 0 ) {
		mask |= CUSTOM_SETTING_HEADSHOTS;
	}
	if ( g_railJump.integer != 0 ) {
		mask |= CUSTOM_SETTING_RAIL_JUMPING;
	}
	if ( G_PmoveHasNoPlayerClipCustomSetting() ) {
		mask |= CUSTOM_SETTING_NO_PLAYER_CLIP;
	}
	if ( g_rrInfected.integer != 0 ) {
		mask |= CUSTOM_SETTING_INFECTED;
	}
	if ( g_lightningDischarge.integer != 0 ) {
		mask |= CUSTOM_SETTING_LIGHTNING_DISCHARGE;
	}

	return mask;
}

/*
=============
G_UpdateCustomSettingsConfigstring

Serialises the custom-settings mask, mirrors it into g_customSettings, and
publishes the value to CS_CUSTOM_SETTINGS when the payload changes.
=============
*/
static void G_UpdateCustomSettingsConfigstring( qboolean forceBroadcast ) {
	uint64_t	mask;
	char		payload[MAX_INFO_STRING];

	mask = G_ComputeCustomSettingsMask();
	Com_sprintf( payload, sizeof( payload ), "%llu", (unsigned long long)mask );

	if ( !forceBroadcast && mask == s_lastCustomSettingsMask &&
		!Q_stricmp( payload, s_customSettingsPayload ) ) {
		G_ClearCustomSettingsDirtyFlag();
		return;
	}

	trap_Cvar_Set( "g_customSettings", payload );
	trap_SetConfigstring( CS_CUSTOM_SETTINGS, payload );
	Q_strncpyz( s_customSettingsPayload, payload, sizeof( s_customSettingsPayload ) );
	s_lastCustomSettingsMask = mask;
	G_ClearCustomSettingsDirtyFlag();
}


/*
=============
G_UpdateTrainingState

Synchronises the latched g_training cvar with the level training flag.
=============
*/
static void G_UpdateTrainingState( void ) {
	trap_Cvar_Update( &g_training );
	level.trainingMapActive = ( g_training.integer != 0 ) ? qtrue : qfalse;
}

/*
=============
G_SyncAdminConfig

Copies the admin-facing cosmetic CVars into the level cache so other
systems can read consistent values without touching the VM handles.
=============
*/
static void G_SyncAdminConfig( void ) {
	level.adminConfig.allowCustomHeadmodels = ( g_allowCustomHeadmodels.integer != 0 ) ? qtrue : qfalse;
	level.adminConfig.playerCylinders = ( g_playerCylinders.integer != 0 ) ? qtrue : qfalse;
	level.adminConfig.practiceFlags = practiceflags.integer;
	level.adminConfig.playerModelScale = g_playerModelScale.value;
	level.adminConfig.playerHeadScale = g_playerheadScale.value;
	level.adminConfig.playerHeadScaleOffset = g_playerheadScaleOffset.value;
}

/*
=============
G_ResetAdminAccessList

Clears any cached SteamID privilege pairs for the new level.
=============
*/
static void G_ResetAdminAccessList( void ) {
	s_adminAccessEntryCount = 0;
	memset( s_adminAccessList, 0, sizeof( s_adminAccessList ) );
}

/*
=============
G_AdminAccessTierToken

Returns the retail symbolic token for a persisted admin access tier.
=============
*/
static const char *G_AdminAccessTierToken( int tier ) {
	switch ( tier ) {
	case -1:
		return "ban";
	case PRIV_MOD:
		return "mod";
	case PRIV_ADMIN:
		return "admin";
	default:
		return NULL;
	}
}

/*
=============
G_AdminAccessTierLabel

Returns the fixed-width retail access-list label for a cached tier.
=============
*/
static const char *G_AdminAccessTierLabel( int tier ) {
	switch ( tier ) {
	case -1:
		return "BAN   ";
	case PRIV_MOD:
		return "MOD   ";
	case PRIV_ADMIN:
		return "ADMIN ";
	default:
		return "      ";
	}
}

/*
=============
G_ParseAdminAccessTier

Validates the privilege tier token pulled from the access file.
=============
*/
static qboolean G_ParseAdminAccessTier( const char *token, int *tierOut ) {
	if ( !token || !token[0] || !tierOut ) {
		return qfalse;
	}

	if ( !Q_stricmp( token, "ban" ) ) {
		*tierOut = -1;
		return qtrue;
	}
	if ( !Q_stricmp( token, "mod" ) ) {
		*tierOut = PRIV_MOD;
		return qtrue;
	}
	if ( !Q_stricmp( token, "admin" ) ) {
		*tierOut = PRIV_ADMIN;
		return qtrue;
	}

	return qfalse;
}

/*
=============
G_SetAdminAccessForSteamID

Adds or updates a cached privilege entry for a SteamID.
=============
*/
void G_SetAdminAccessForSteamID( const char *steamId, int tier, qboolean temporary ) {
	int		i;

	if ( !steamId || !steamId[0] ) {
		return;
	}

	for ( i = 0; i < s_adminAccessEntryCount; i++ ) {
		if ( !Q_stricmp( s_adminAccessList[i].steamId, steamId ) ) {
			s_adminAccessList[i].privilegeTier = tier;
			s_adminAccessList[i].temporary = temporary;
			return;
		}
	}

	if ( s_adminAccessEntryCount >= MAX_ADMIN_ACCESS_ENTRIES ) {
		G_Printf( "WARNING: access list full, skipping SteamID %s\n", steamId );
		return;
	}

	Q_strncpyz( s_adminAccessList[s_adminAccessEntryCount].steamId, steamId,
		sizeof( s_adminAccessList[s_adminAccessEntryCount].steamId ) );
	s_adminAccessList[s_adminAccessEntryCount].privilegeTier = tier;
	s_adminAccessList[s_adminAccessEntryCount].temporary = temporary;
	s_adminAccessEntryCount++;
}

/*
=============
G_RemoveAdminAccessForSteamID

Erases a cached SteamID privilege entry if present.
=============
*/
void G_RemoveAdminAccessForSteamID( const char *steamId ) {
	int	i;

	if ( !steamId || !steamId[0] ) {
		return;
	}

	for ( i = 0; i < s_adminAccessEntryCount; i++ ) {
		if ( !Q_stricmp( s_adminAccessList[i].steamId, steamId ) ) {
			if ( i + 1 < s_adminAccessEntryCount ) {
				memmove( &s_adminAccessList[i], &s_adminAccessList[i + 1],
					(size_t)( s_adminAccessEntryCount - i - 1 ) * sizeof( s_adminAccessList[0] ) );
			}
			s_adminAccessEntryCount--;
			memset( &s_adminAccessList[s_adminAccessEntryCount], 0,
				sizeof( s_adminAccessList[s_adminAccessEntryCount] ) );
			return;
		}
	}
}

/*
=============
G_PrintAccessListLine

Prints one access-list line to a client or to the dedicated server console.
=============
*/
static void G_PrintAccessListLine( gentity_t *ent, const char *line ) {
	if ( ent && ent->client ) {
		trap_SendServerCommand( ent - g_entities, va( "print \"%s\"", line ) );
		return;
	}

	G_Printf( "%s", line );
}

/*
=============
G_PrintAccessListPage

Prints one retail-style page of the cached SteamID privilege list.
=============
*/
void G_PrintAccessListPage( gentity_t *ent, unsigned int page ) {
	enum { ACCESS_LIST_PAGE_SIZE = 20 };
	unsigned int	totalPages;
	unsigned int	start;
	unsigned int	end;
	unsigned int	i;
	char		line[MAX_STRING_CHARS];

	if ( s_adminAccessEntryCount <= 0 ) {
		totalPages = 1;
	} else {
		totalPages = (unsigned int)( ( s_adminAccessEntryCount + ACCESS_LIST_PAGE_SIZE - 1 ) / ACCESS_LIST_PAGE_SIZE );
	}

	if ( page >= totalPages ) {
		page = totalPages - 1;
	}

	Com_sprintf( line, sizeof( line ), "Access List: Page %i of %i\n", page + 1, totalPages );
	G_PrintAccessListLine( ent, line );
	G_PrintAccessListLine( ent, "=============================\n" );

	start = page * ACCESS_LIST_PAGE_SIZE;
	end = start + ACCESS_LIST_PAGE_SIZE;
	if ( end > (unsigned int)s_adminAccessEntryCount ) {
		end = (unsigned int)s_adminAccessEntryCount;
	}

	for ( i = start; i < end; i++ ) {
		const adminAccessEntry_t	*entry;
		unsigned long long		steamIdValue;

		entry = &s_adminAccessList[i];
		steamIdValue = 0;
		sscanf( entry->steamId, "%llu", &steamIdValue );
		Com_sprintf( line, sizeof( line ), "%llu %s %s\n",
			steamIdValue,
			G_AdminAccessTierLabel( entry->privilegeTier ),
			entry->temporary ? "TEMP" : "PERM" );
		G_PrintAccessListLine( ent, line );
	}
}

/*
=============
G_LoadAdminAccessFile

Loads g_accessFile and caches its SteamID to privilege tier mappings.
=============
*/
static void G_LoadAdminAccessFile( void ) {
	fileHandle_t	handle;
	int			length;
	char		buffer[MAX_ADMIN_ACCESS_FILE_BYTES + 1];
	char		*cursor;
	qboolean	truncated;

	G_ResetAdminAccessList();
	G_Printf( "initializing access list...\n" );

	if ( !g_accessFile.string[0] ) {
		G_Printf( "file not found: %s\n", g_accessFile.string );
		return;
	}

	length = trap_FS_FOpenFile( g_accessFile.string, &handle, FS_READ );
	if ( length <= 0 || !handle ) {
		if ( handle ) {
			trap_FS_FCloseFile( handle );
		}
		G_Printf( "file not found: %s\n", g_accessFile.string );
		return;
	}

	if ( length > MAX_ADMIN_ACCESS_FILE_BYTES ) {
		length = MAX_ADMIN_ACCESS_FILE_BYTES;
		truncated = qtrue;
	} else {
		truncated = qfalse;
	}

	trap_FS_Read( buffer, length, handle );
	buffer[length] = '\0';
	trap_FS_FCloseFile( handle );

	if ( truncated ) {
		G_Printf( "WARNING: %s exceeds %i bytes; truncating access list.\n", g_accessFile.string, MAX_ADMIN_ACCESS_FILE_BYTES );
	}

	cursor = buffer;
	while ( qtrue ) {
		char				*line;
		char				*carriageReturn;
		unsigned long long	steamIdValue;
		char				steamToken[ 32 ];
		char				tierToken[ 16 ];
		int					tier;

		line = strtok( cursor, "\n" );
		cursor = NULL;
		if ( !line ) {
			break;
		}

		if ( line[0] == '#' ) {
			continue;
		}

		carriageReturn = strchr( line, '\r' );
		if ( carriageReturn ) {
			*carriageReturn = '\0';
		}

		if ( sscanf( line, "%llu|%15s", &steamIdValue, tierToken ) != 2 || !G_ParseAdminAccessTier( tierToken, &tier ) ) {
			G_Printf( "^1invalid admin access format, skipping: %s\n", line );
			continue;
		}

		Com_sprintf( steamToken, sizeof( steamToken ), "%llu", steamIdValue );
		G_SetAdminAccessForSteamID( steamToken, tier, qfalse );
	}

	G_Printf( "loaded %i steam ids into the access list\n", s_adminAccessEntryCount );
}

/*
=============
G_WriteAdminAccessFile

Persists the retail symbolic admin access list back to g_accessFile.
=============
*/
static void G_WriteAdminAccessFile( void ) {
	static const char accessHeader[] =
		"# Be sure to run /reload_access if editing this file while server is running.\r\n"
		"# The server will overwrite your changes on map exit and shutdown\r\n"
		"# 1 entry per line, format: steamid|(mod|admin|ban)\r\n"
		"# ex: 76561198072786081|ban\r\n";
	fileHandle_t	handle;
	int		length;
	int		i;

	if ( !g_accessFile.string[0] ) {
		G_Printf( "file not found: %s\n", g_accessFile.string );
		return;
	}

	length = trap_FS_FOpenFile( g_accessFile.string, &handle, FS_WRITE );
	if ( length < 0 || !handle ) {
		if ( handle ) {
			trap_FS_FCloseFile( handle );
		}
		G_Printf( "file not found: %s\n", g_accessFile.string );
		return;
	}

	trap_FS_Write( accessHeader, (int)strlen( accessHeader ), handle );

	for ( i = 0; i < s_adminAccessEntryCount; i++ ) {
		const adminAccessEntry_t	*entry;
		const char			*tierToken;
		char				line[64];

		entry = &s_adminAccessList[i];
		if ( entry->temporary ) {
			continue;
		}

		tierToken = G_AdminAccessTierToken( entry->privilegeTier );
		if ( !tierToken ) {
			continue;
		}

		Com_sprintf( line, sizeof( line ), "%s|%s\r\n", entry->steamId, tierToken );
		trap_FS_Write( line, (int)strlen( line ), handle );
	}

	trap_FS_FCloseFile( handle );
}

/*
=============
G_AdminAccessForSteamID

Returns the cached privilege tier for the supplied SteamID if present.
=============
*/
int G_AdminAccessForSteamID( const char *steamId ) {
	int	i;

	if ( !steamId || !steamId[0] ) {
		return 0;
	}

	for ( i = 0; i < s_adminAccessEntryCount; i++ ) {
		if ( !Q_stricmp( s_adminAccessList[i].steamId, steamId ) ) {
			return s_adminAccessList[i].privilegeTier;
		}
	}

	return 0;
}

/*
=============
G_AdminAccessForConnectedClient

Rebuilds the cached privilege tier for a live client after access-list changes.
=============
*/
static int G_AdminAccessForConnectedClient( int clientNum ) {
	gclient_t			*client;
	char				userinfo[MAX_INFO_STRING];
	const char			*ip;
	unsigned long long	steamIdValue;
	char				steamIdString[32];

	if ( clientNum < 0 || clientNum >= level.maxclients ) {
		return PRIV_NONE;
	}

	client = &level.clients[clientNum];
	if ( client->pers.connected == CON_DISCONNECTED ) {
		return PRIV_NONE;
	}

	if ( client->pers.localClient ) {
		return PRIV_ROOT;
	}

	trap_GetUserinfo( clientNum, userinfo, sizeof( userinfo ) );
	ip = Info_ValueForKey( userinfo, "ip" );
	if ( ip[0] && !Q_stricmp( ip, "localhost" ) ) {
		return PRIV_ROOT;
	}

	if ( client->pers.steamIdValid ) {
		steamIdValue = ( (unsigned long long)client->pers.steamIdHigh << 32 ) | client->pers.steamIdLow;
		Com_sprintf( steamIdString, sizeof( steamIdString ), "%llu", steamIdValue );
		return G_AdminAccessForSteamID( steamIdString );
	}

	return G_AdminAccessForSteamID( Info_ValueForKey( userinfo, "steamid" ) );
}

/*
=============
G_ReloadAdminAccess

Reloads the access file and refreshes cached privilege tiers for connected clients.
=============
*/
void G_ReloadAdminAccess( void ) {
	int	clientNum;

	G_LoadAdminAccessFile();

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gclient_t	*client;

		client = &level.clients[clientNum];
		if ( client->pers.connected == CON_DISCONNECTED ) {
			continue;
		}

		client->sess.privilege = G_AdminAccessForConnectedClient( clientNum );
	}
}


#include "g_gametype_lifecycle.inc"


/*
============
G_CountSpawnPoints

Caches the retail spawn-point counts gathered during level init.
============
*/
static void G_CountSpawnPoints( void ) {
	int			entNum;
	gentity_t	*spot;

	level.deathmatchSpawnPointCount = 0;
	level.redSpawnPointCount = 0;
	level.blueSpawnPointCount = 0;

	for ( entNum = 0; entNum < level.num_entities; entNum++ ) {
		gentity_t	*ent;

		ent = &g_entities[entNum];
		if ( !ent->inuse || !ent->classname ) {
			continue;
		}

		if ( Q_stricmp( ent->classname, "info_player_deathmatch" ) ) {
			continue;
		}

		if ( level.deathmatchSpawnPointCount < 25 ) {
			level.deathmatchSpawnPointCount++;
		}
	}

	spot = NULL;
	while ( ( spot = G_Find( spot, FOFS( classname ), "team_CTF_redspawn" ) ) != NULL ) {
		if ( level.redSpawnPointCount < 25 ) {
			level.redSpawnPointCount++;
		}
	}

	spot = NULL;
	while ( ( spot = G_Find( spot, FOFS( classname ), "team_CTF_bluespawn" ) ) != NULL ) {
		if ( level.blueSpawnPointCount < 25 ) {
			level.blueSpawnPointCount++;
		}
	}
}

/*
============
G_InitGame

============
*/
void G_InitGame( int levelTime, int randomSeed, int restart ) {
	int					i;
	char				session[MAX_STRING_CHARS];
	int					sessionGametype;

	G_Printf ("------- Game Initialization -------\n");
	G_Printf ("gamename: %s\n", GAMEVERSION);
	G_Printf ("gamedate: %s\n", __DATE__);

	srand( randomSeed );
	G_PmoveClearConfigstring();

	G_RegisterCvars();
	trap_Cvar_Update( &mercylimit );
	trap_Cvar_Update( &g_mercytime );

	trap_Cvar_Set( "g_training", "0" );
	G_UpdateTrainingState();

	G_FactoryRegistry_Init();
	Factory_ApplyCurrentSelection( qtrue );
	G_InitPublishedCvarState();
	G_LoadAdminAccessFile();
	G_InitMemory();

	// set some level globals
	memset( &level, 0, sizeof( level ) );
	G_InitLevelCvarMirrors();
	if ( g_gametype.integer == GT_RACE ) {
		G_RaceInitLevel();
	}
	G_InitSpawnQueue();
	G_FreezeSyncCvars();
	level.time = levelTime;
	level.previousTime = levelTime;
	level.startTime = levelTime;
	level.pendingVoteClientNum = -1;
	{
		time_t levelStart = time( NULL );
		char startTimeBuffer[32];

		Com_sprintf( startTimeBuffer, sizeof( startTimeBuffer ), "%u", (unsigned int)levelStart );
		trap_Cvar_Set( "g_levelStartTime", startTimeBuffer );
	}
	if ( restart ) {
		trap_GetConfigstring( CS_MATCH_GUID, level.rankMatchGuid, sizeof( level.rankMatchGuid ) );
	} else {
		level.rankMatchGuid[0] = '\0';
	}
	if ( !level.rankMatchGuid[0] ) {
		trap_GenerateMatchGuid( level.rankMatchGuid, sizeof( level.rankMatchGuid ) );
	}
	if ( !level.rankMatchGuid[0] ) {
		Com_sprintf( level.rankMatchGuid, sizeof( level.rankMatchGuid ), "%08X%08X",
			(unsigned int)level.startTime, (unsigned int)( randomSeed ^ rand() ) );
	}
	level.rankMatchStartedSent = qfalse;
	level.rankMatchReportSent = qfalse;
	level.rankExitMessage[0] = '\0';
	level.rankLastScorer = -1;
	level.rankLastTeamScorer = -1;
	level.roundState = ROUNDSTATE_INACTIVE;
	level.roundTransitionTime = ROUND_TRANSITION_NONE;
	level.roundPendingExit = qfalse;
	level.rrRoundState = RR_ROUNDSTATE_INACTIVE;
	level.rrPendingRoundState = RR_ROUNDSTATE_INACTIVE;
	level.rrStateChangeTime = levelTime;
	level.rrSelectedInfectedClientNum = -1;
	level.rrCarryoverInfectedClientNum = -1;
	level.rrLastInfectionTime = -1;
	level.rrNextSurvivalBonusTime = 0;
	level.rrPendingMatchExit = qfalse;
	level.adRoundState = AD_ROUNDSTATE_INACTIVE;
	level.adPendingRoundState = AD_ROUNDSTATE_INACTIVE;
	level.adStateChangeTime = levelTime;
	level.adTurnIndex = 0;
	level.adRoundWinner = TEAM_FREE;
	level.adRoundWinnerAlreadyScored = qfalse;
	G_SetGameState( GAME_STATE_PRE_GAME );
	s_autoRecordState = 0;
	s_autoRecordBasename[0] = '\0';

	level.timeoutOwner = -1;
	level.timeoutTeam = TEAM_FREE;
	level.timeoutActive = qfalse;
	level.timeoutStartTime = 0;
	level.timeoutExpireTime = 0;
	level.intermissionExitStatusLatched = qfalse;
	level.overtimeAccumulatedMsec = 0;
	level.overtimeActive = qfalse;
	level.overtimeStartTime = 0;
	level.overtimeEndTime = 0;
	level.overtimeCount = 0;
	level.suddenDeathActive = qfalse;
	level.suddenDeathLastDelay = -1;
	level.suddenDeathNoRespawnLogged = qfalse;
	level.matchForfeited = qfalse;
        {
                int team;
                for ( team = TEAM_FREE; team < TEAM_NUM_TEAMS; team++ ) {
                        level.timeoutRemaining[team] = g_matchFactoryConfig.timeoutCountPerTeam;
                }
        }
        matchFlow_lastConfig = g_matchFactoryConfig;

	level.snd_fry = G_SoundIndex("sound/player/fry.wav");	// FIXME standing in lava / slime
	G_SoundIndex( "sound/player/gurp1.wav" );
	G_SoundIndex( "sound/player/gurp2.wav" );

	if ( g_gametype.integer != GT_SINGLE_PLAYER && g_log.string[0] ) {
		if ( g_logSync.integer ) {
			trap_FS_FOpenFile( g_log.string, &level.logFile, FS_APPEND_SYNC );
		} else {
			trap_FS_FOpenFile( g_log.string, &level.logFile, FS_APPEND );
		}
		if ( !level.logFile ) {
			G_Printf( "WARNING: Couldn't open logfile: %s\n", g_log.string );
		} else {
			char	serverinfo[MAX_INFO_STRING];

			trap_GetServerinfo( serverinfo, sizeof( serverinfo ) );

			G_LogPrintf("------------------------------------------------------------\n" );
			G_LogPrintf("InitGame: %s\n", serverinfo );
		}
	} else {
		G_Printf( "Not logging to disk.\n" );
	}

	trap_Cvar_VariableStringBuffer( "session", session, sizeof( session ) );
	sessionGametype = atoi( session );
	if ( g_gametype.integer != sessionGametype ) {
		level.newSession = qtrue;
		G_Printf( "Gametype changed, clearing session data.\n" );
	}

	// initialize all entities for this game
	memset( g_entities, 0, MAX_GENTITIES * sizeof(g_entities[0]) );
	level.gentities = g_entities;

	// initialize all clients for this game
	level.maxclients = g_maxclients.integer;
	memset( g_clients, 0, MAX_CLIENTS * sizeof(g_clients[0]) );
	level.clients = g_clients;

	// set client fields on player ents
	for ( i=0 ; i<level.maxclients ; i++ ) {
		g_entities[i].client = level.clients + i;
		G_InitClientVoteThrottle( level.clients + i );
	}

	// always leave room for the max number of clients,
	// even if they aren't all used, so numbers inside that
	// range are NEVER anything but clients
	level.num_entities = MAX_CLIENTS;

	{
		char	matchGuidInfo[GAME_MATCH_GUID_BUFFER_SIZE];

		if ( restart ) {
			trap_GetConfigstring( CS_MATCH_GUID, matchGuidInfo, sizeof( matchGuidInfo ) );
		} else {
			matchGuidInfo[0] = '\0';
		}
		if ( !matchGuidInfo[0] ) {
			Q_strncpyz( matchGuidInfo, level.rankMatchGuid, sizeof( matchGuidInfo ) );
		}
		Q_strncpyz( level.rankMatchGuid, matchGuidInfo, sizeof( level.rankMatchGuid ) );
		trap_SetConfigstring( CS_MATCH_GUID, matchGuidInfo );
	}

	// let the server system know where the entites are
	trap_LocateGameData( level.gentities, level.num_entities, sizeof( gentity_t ), 
		&level.clients[0].ps, sizeof( level.clients[0] ) );

	// reserve some spots for dead player bodies
	InitBodyQue();

	ClearRegisteredItems();
	G_InitItemSpawnDelays();

	// parse the key/value pairs and spawn gentities
	G_SpawnEntitiesFromString();
	FindIntermissionPoint();
	G_CountSpawnPoints();
	G_InitLagHaxHistory();
	G_UpdateTrainingState();
	if ( level.trainingMapActive ) {
		int team;
		for ( team = TEAM_FREE; team < TEAM_NUM_TEAMS; team++ ) {
			level.timeoutRemaining[team] = 0;
		}
		level.timeoutActive = qfalse;
		level.timeoutOwner = -1;
		level.timeoutTeam = TEAM_FREE;
		level.timeoutExpireTime = 0;
		level.timeoutStartTime = 0;
	}

	// general initialization
	G_FindTeams();

	// make sure we have flags for CTF, etc
	if( g_gametype.integer >= GT_TEAM ) {
		G_CheckTeamItems();
	}

	G_GametypeInit();

	SaveRegisteredItems();

	G_Printf ("-----------------------------------\n");
	G_UpdateTimeoutConfigStrings();

	if( g_gametype.integer == GT_SINGLE_PLAYER || trap_Cvar_VariableIntegerValue( "com_build" ) ) {
		G_ModelIndex( SP_PODIUM_MODEL );
	}

	if ( trap_Cvar_VariableIntegerValue( "bot_enable" ) ) {
		BotAISetup( restart );
		BotAILoadMap( restart );
		G_InitBots( restart );
	}

	G_SpawnQuadHogQuad();
	G_SpawnItemPowerups();

	G_RemapTeamShaders();

	LevelCheckTimers();
	G_UpdateMatchStateConfigString();
	G_UpdateTeamCountConfigstrings();
	G_MatchConfig_UpdateConfigstrings();
	G_UpdateTournamentQueuePositions();
}



/*
=================
G_ShutdownGame
=================
*/
void G_ShutdownGame( int restart ) {
	char	exitReason[MAX_STRING_CHARS];

	G_Printf ("==== ShutdownGame ====\n");
	G_PmoveClearConfigstring();
	G_PmoveSetConfigstringsReady( qfalse );

	trap_Cvar_VariableStringBuffer( "com_errorMessage", exitReason, sizeof( exitReason ) );
	if ( !exitReason[0] ) {
		Q_strncpyz( exitReason, "Shutdown", sizeof( exitReason ) );
	}

	if ( level.time ) {
		LogExit( exitReason );
		G_WriteSessionData();
		G_WriteAdminAccessFile();
	}

	if ( level.logFile ) {
		G_LogPrintf("ShutdownGame:\n" );
		G_LogPrintf("------------------------------------------------------------\n" );
		trap_FS_FCloseFile( level.logFile );
		level.logFile = 0;
	}

	if ( trap_Cvar_VariableIntegerValue( "bot_enable" ) ) {
		BotAIShutdown( restart );
	}
}



//===================================================================

#ifndef GAME_HARD_LINKED
// this is only here so the functions in q_shared.c and bg_*.c can link

void QDECL Com_Error ( int errorLevel, const char *error, ... ) {
	va_list		argptr;
	char		text[1024];

	(void)errorLevel;

	va_start (argptr, error);
	vsprintf (text, error, argptr);
	va_end (argptr);

	G_Error( "%s", text);
}

void QDECL Com_Printf( const char *msg, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, msg);
	vsprintf (text, msg, argptr);
	va_end (argptr);

	G_Printf ("%s", text);
}

#endif

/*
========================================================================

PLAYER COUNTING / SCORE SORTING

========================================================================
*/

/*
=============
G_IsTournamentQueueEligibleClient

Returns qtrue for spectators who are actually eligible to occupy a duel
queue slot.
=============
*/
static qboolean G_IsTournamentQueueEligibleClient( const gclient_t *client ) {
	if ( !client ) {
		return qfalse;
	}
	if ( client->pers.connected != CON_CONNECTED ) {
		return qfalse;
	}
	if ( client->sess.sessionTeam != TEAM_SPECTATOR ) {
		return qfalse;
	}
	if ( client->sess.spectateOnly ) {
		return qfalse;
	}
	if ( client->sess.spectatorState == SPECTATOR_SCOREBOARD ||
		client->sess.spectatorClient < 0 ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
G_FindNextTournamentPlayer

Returns the oldest eligible waiting spectator for duel queue promotion.
=============
*/
gentity_t *G_FindNextTournamentPlayer( void ) {
	gentity_t	*nextInLine;
	int		i;

	nextInLine = NULL;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		gclient_t	*client;

		client = &level.clients[i];
		if ( !G_IsTournamentQueueEligibleClient( client ) ) {
			continue;
		}

		if ( !nextInLine || client->sess.spectatorTime < nextInLine->client->sess.spectatorTime ) {
			nextInLine = &g_entities[i];
		}
	}

	return nextInLine;
}

/*
=============
G_CompareTournamentQueueTimes

=============
*/
static int QDECL G_CompareTournamentQueueTimes( const void *a, const void *b ) {
	const gclient_t	*clientA;
	const gclient_t	*clientB;

	clientA = &level.clients[*(const int *)a];
	clientB = &level.clients[*(const int *)b];

	if ( clientA->sess.spectatorTime > clientB->sess.spectatorTime ) {
		return 1;
	}
	if ( clientA->sess.spectatorTime < clientB->sess.spectatorTime ) {
		return -1;
	}

	return 0;
}

/*
=============
G_UpdateTournamentQueuePositions

=============
*/
void G_UpdateTournamentQueuePositions( void ) {
	int	queuedClients[MAX_CLIENTS];
	int	queuedCount;
	int	i;

	if ( g_gametype.integer != GT_TOURNAMENT ) {
		return;
	}

	queuedCount = 0;
	for ( i = 0; i < level.numConnectedClients; i++ ) {
		int		clientNum;
		gclient_t	*client;

		clientNum = level.sortedClients[i];
		client = &level.clients[clientNum];
		if ( !G_IsTournamentQueueEligibleClient( client ) ) {
			if ( client->sess.spectatorQueuePosition != 0 ) {
				client->sess.spectatorQueuePosition = 0;
				client->sess.spectatorQueuePositionDirty = qtrue;
			}
			continue;
		}

		queuedClients[queuedCount] = clientNum;
		queuedCount++;
	}

	qsort( queuedClients, queuedCount, sizeof( queuedClients[0] ), G_CompareTournamentQueueTimes );

	for ( i = 0; i < queuedCount; i++ ) {
		gclient_t	*client;
		int		queuePosition;

		client = &level.clients[queuedClients[i]];
		queuePosition = i + 1;

		if ( client->sess.spectatorQueuePosition != queuePosition ) {
			client->sess.spectatorQueuePosition = queuePosition;
			client->sess.spectatorQueuePositionDirty = qtrue;
		}
	}
}

/*
=============
G_SyncTournamentQueueTeamTasks

=============
*/
void G_SyncTournamentQueueTeamTasks( void ) {
	char		userinfo[MAX_INFO_STRING];
	int		dirtyClients[MAX_CLIENTS];
	int		dirtyCount;
	int		i;

	if ( g_gametype.integer != GT_TOURNAMENT ) {
		return;
	}

	dirtyCount = 0;
	for ( i = 0; i < level.numConnectedClients; i++ ) {
		int		clientNum;
		gclient_t	*client;

		clientNum = level.sortedClients[i];
		client = &level.clients[clientNum];
		if ( client->sess.spectatorQueuePositionDirty ) {
			client->sess.spectatorQueuePositionDirty = qfalse;
			dirtyClients[dirtyCount] = clientNum;
			dirtyCount++;
		}
	}

	if ( dirtyCount <= 0 ) {
		return;
	}

	for ( i = 0; i < dirtyCount; i++ ) {
		int		clientNum;
		gclient_t	*client;

		clientNum = dirtyClients[i];
		client = &level.clients[clientNum];

		trap_GetUserinfo( clientNum, userinfo, sizeof( userinfo ) );
		Info_SetValueForKey( userinfo, "teamtask", va( "%d", client->sess.spectatorQueuePosition ) );
		trap_SetUserinfo( clientNum, userinfo );
		ClientUserinfoChanged( clientNum );
	}
}

/*
=============
AddTournamentPlayer

If there are less than two tournament players, put a
spectator in the game and restart
=============
*/
void AddTournamentPlayer( void ) {
	gentity_t	*nextInLine;

	if ( g_gametype.integer != GT_TOURNAMENT ) {
		return;
	}

	if ( level.numPlayingClients >= 2 ) {
		return;
	}

	// retail never promotes duel spectators during intermission or a timeout
	if ( level.intermissiontime || level.intermissionQueued || level.timeoutActive ) {
		return;
	}

	nextInLine = G_FindNextTournamentPlayer();
	if ( !nextInLine ) {
		return;
	}

	G_ResetDuelWarmupState( qfalse );

	// set them to free-for-all team
	SetTeam( nextInLine, "f" );
	G_ClearConnectedReadyStates( qtrue );
}

/*
=======================
RemoveTournamentLoser

Make the loser a spectator at the back of the line
=======================
*/
void RemoveTournamentLoser( void ) {
	int			clientNum;

	if ( level.numPlayingClients != 2 ) {
		return;
	}

	clientNum = level.sortedClients[1];

	if ( level.clients[ clientNum ].pers.connected != CON_CONNECTED ) {
		return;
	}

	// make them a spectator
	SetTeam( &g_entities[ clientNum ], "s" );
}

/*
=======================
RemoveTournamentWinner
=======================
*/
void RemoveTournamentWinner( void ) {
	int			clientNum;

	if ( level.numPlayingClients != 2 ) {
		return;
	}

	clientNum = level.sortedClients[0];

	if ( level.clients[ clientNum ].pers.connected != CON_CONNECTED ) {
		return;
	}

	// make them a spectator
	SetTeam( &g_entities[ clientNum ], "s" );
}

/*
=======================
AdjustTournamentScores
=======================
*/
void AdjustTournamentScores( void ) {
	int			clientNum;

	clientNum = level.sortedClients[0];
	if ( level.clients[ clientNum ].pers.connected == CON_CONNECTED ) {
		level.clients[ clientNum ].sess.wins++;
		ClientUserinfoChanged( clientNum );
	}

	clientNum = level.sortedClients[1];
	if ( level.clients[ clientNum ].pers.connected == CON_CONNECTED ) {
		level.clients[ clientNum ].sess.losses++;
		ClientUserinfoChanged( clientNum );
	}

}

/*
=============
G_SetAwardConfigstring

Publishes one of the recovered retail award winner client-number slots.
=============
*/
static void G_SetAwardConfigstring( int configstringIndex, int clientNum ) {
	if ( clientNum < 0 || clientNum >= level.maxclients ) {
		trap_SetConfigstring( configstringIndex, "" );
		return;
	}

	if ( level.clients[clientNum].pers.connected != CON_CONNECTED ) {
		trap_SetConfigstring( configstringIndex, "" );
		return;
	}

	trap_SetConfigstring( configstringIndex, va( "%i", clientNum ) );
}

/*
=============
G_UpdateAwardConfigstrings

Refreshes the retail postgame-award winner configstrings recovered from qagame.
=============
*/
static void G_UpdateAwardConfigstrings( void ) {
	int		clientNum;
	int		eligibleCount;
	int		bestItemControlClient;
	int		bestItemControlMetric;
	int		bestItemControlScore;
	int		bestAccuracyClient;
	int		bestAccuracyMetric;
	int		bestAccuracyShots;
	int		bestMostValuableClient;
	int		bestMostValuableMetric;
	int		bestOffensiveClient;
	int		bestOffensiveMetric;
	int		bestOffensiveScore;
	int		bestDefensiveClient;
	int		bestDefensiveMetric;
	int		bestDefensiveScore;
	int		bestDamageClient;
	int		bestDamageMetric;
	int		bestDamageScore;

	eligibleCount = 0;
	bestItemControlClient = -1;
	bestItemControlMetric = -1;
	bestItemControlScore = -1;
	bestAccuracyClient = -1;
	bestAccuracyMetric = -1;
	bestAccuracyShots = -1;
	bestMostValuableClient = -1;
	bestMostValuableMetric = -1;
	bestOffensiveClient = -1;
	bestOffensiveMetric = -1;
	bestOffensiveScore = -1;
	bestDefensiveClient = -1;
	bestDefensiveMetric = -1;
	bestDefensiveScore = -1;
	bestDamageClient = -1;
	bestDamageMetric = -1;
	bestDamageScore = -1;

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gclient_t	*cl;
		int		score;
		int		captures;
		int		defends;
		int		assists;
		int		itemControlMetric;
		int		accuracyMetric;
		int		accuracyShots;
		int		offensiveMetric;
		int		defensiveMetric;
		int		damageMetric;

		cl = &level.clients[clientNum];
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( cl->sess.sessionTeam == TEAM_SPECTATOR ) {
			continue;
		}

		eligibleCount++;
		score = cl->ps.persistant[PERS_SCORE];
		captures = cl->ps.persistant[PERS_CAPTURES];
		defends = cl->ps.persistant[PERS_DEFEND_COUNT];
		assists = cl->ps.persistant[PERS_ASSIST_COUNT];
		itemControlMetric = captures * 4 + defends * 2 + assists;
		damageMetric = cl->pers.damageGiven;
		if ( cl->accuracy_shots > 0 && cl->accuracy_hits > 0 ) {
			accuracyMetric = cl->accuracy_hits * 100 / cl->accuracy_shots;
			accuracyShots = cl->accuracy_shots;
		} else {
			accuracyMetric = 0;
			accuracyShots = 0;
		}
		offensiveMetric = captures * 100 + assists * 10 + score;
		defensiveMetric = defends * 100 + score;

		if ( itemControlMetric > bestItemControlMetric
			|| ( itemControlMetric == bestItemControlMetric && score > bestItemControlScore ) ) {
			bestItemControlMetric = itemControlMetric;
			bestItemControlScore = score;
			bestItemControlClient = clientNum;
		}

		if ( accuracyMetric > bestAccuracyMetric
			|| ( accuracyMetric == bestAccuracyMetric && accuracyShots > bestAccuracyShots ) ) {
			bestAccuracyMetric = accuracyMetric;
			bestAccuracyShots = accuracyShots;
			bestAccuracyClient = clientNum;
		}

		if ( score > bestMostValuableMetric ) {
			bestMostValuableMetric = score;
			bestMostValuableClient = clientNum;
		}

		if ( offensiveMetric > bestOffensiveMetric
			|| ( offensiveMetric == bestOffensiveMetric && score > bestOffensiveScore ) ) {
			bestOffensiveMetric = offensiveMetric;
			bestOffensiveScore = score;
			bestOffensiveClient = clientNum;
		}

		if ( defensiveMetric > bestDefensiveMetric
			|| ( defensiveMetric == bestDefensiveMetric && score > bestDefensiveScore ) ) {
			bestDefensiveMetric = defensiveMetric;
			bestDefensiveScore = score;
			bestDefensiveClient = clientNum;
		}

		if ( damageMetric > bestDamageMetric
			|| ( damageMetric == bestDamageMetric && score > bestDamageScore ) ) {
			bestDamageMetric = damageMetric;
			bestDamageScore = score;
			bestDamageClient = clientNum;
		}
	}

	if ( eligibleCount <= 0 ) {
		G_SetAwardConfigstring( CS_AWARD_BEST_ITEMCONTROL, -1 );
		G_SetAwardConfigstring( CS_AWARD_MOST_ACCURATE, -1 );
		G_SetAwardConfigstring( CS_AWARD_MOST_VALUABLE, -1 );
		G_SetAwardConfigstring( CS_AWARD_MOST_VALUABLE_OFFENSIVE, -1 );
		G_SetAwardConfigstring( CS_AWARD_MOST_VALUABLE_DEFENSIVE, -1 );
		G_SetAwardConfigstring( CS_AWARD_MOST_DAMAGEDEALT, -1 );
		return;
	}

	G_SetAwardConfigstring( CS_AWARD_BEST_ITEMCONTROL, bestItemControlClient );
	G_SetAwardConfigstring( CS_AWARD_MOST_ACCURATE, bestAccuracyClient );

	switch ( g_gametype.integer ) {
	case GT_RACE:
	case GT_CLAN_ARENA:
	case GT_DOMINATION:
	case GT_ATTACK_DEFEND:
	case GT_RED_ROVER:
		G_SetAwardConfigstring( CS_AWARD_MOST_VALUABLE, -1 );
		break;
	default:
		G_SetAwardConfigstring( CS_AWARD_MOST_VALUABLE, bestMostValuableClient );
		break;
	}

	switch ( g_gametype.integer ) {
	case GT_CTF:
	case GT_1FCTF:
	case GT_OBELISK:
	case GT_HARVESTER:
	case GT_DOMINATION:
	case GT_ATTACK_DEFEND:
		G_SetAwardConfigstring( CS_AWARD_MOST_VALUABLE_OFFENSIVE, bestOffensiveClient );
		G_SetAwardConfigstring( CS_AWARD_MOST_VALUABLE_DEFENSIVE, bestDefensiveClient );
		G_SetAwardConfigstring( CS_AWARD_MOST_DAMAGEDEALT, bestDamageClient );
		break;
	default:
		G_SetAwardConfigstring( CS_AWARD_MOST_VALUABLE_OFFENSIVE, -1 );
		G_SetAwardConfigstring( CS_AWARD_MOST_VALUABLE_DEFENSIVE, -1 );
		G_SetAwardConfigstring( CS_AWARD_MOST_DAMAGEDEALT, -1 );
		break;
	}
}

/*
=============
SortRanks

=============
*/
int QDECL SortRanks( const void *a, const void *b ) {
	gclient_t	*ca, *cb;

	ca = &level.clients[*(int *)a];
	cb = &level.clients[*(int *)b];

	// sort special clients last
	if ( ca->sess.spectatorState == SPECTATOR_SCOREBOARD || ca->sess.spectatorClient < 0 ) {
		return 1;
	}
	if ( cb->sess.spectatorState == SPECTATOR_SCOREBOARD || cb->sess.spectatorClient < 0  ) {
		return -1;
	}

	// then connecting clients
	if ( ca->pers.connected == CON_CONNECTING ) {
		return 1;
	}
	if ( cb->pers.connected == CON_CONNECTING ) {
		return -1;
	}


	// then spectators
	if ( ca->sess.sessionTeam == TEAM_SPECTATOR && cb->sess.sessionTeam == TEAM_SPECTATOR ) {
		if ( ca->sess.spectatorTime < cb->sess.spectatorTime ) {
			return -1;
		}
		if ( ca->sess.spectatorTime > cb->sess.spectatorTime ) {
			return 1;
		}
		return 0;
	}
	if ( ca->sess.sessionTeam == TEAM_SPECTATOR ) {
		return 1;
	}
	if ( cb->sess.sessionTeam == TEAM_SPECTATOR ) {
		return -1;
	}

	if ( g_gametype.integer == GT_RACE ) {
		if ( ca->ps.persistant[PERS_SCORE]
			< cb->ps.persistant[PERS_SCORE] ) {
			return -1;
		}
		if ( ca->ps.persistant[PERS_SCORE]
			> cb->ps.persistant[PERS_SCORE] ) {
			return 1;
		}
		return 0;
	}

	// then sort by score
	if ( ca->ps.persistant[PERS_SCORE]
		> cb->ps.persistant[PERS_SCORE] ) {
		return -1;
	}
	if ( ca->ps.persistant[PERS_SCORE]
		< cb->ps.persistant[PERS_SCORE] ) {
		return 1;
	}
	return 0;
}

/*
============
G_CountAndSortConnectedClients

Rebuilds the retail connected-client count block used by CalculateRanks.
============
*/
static void G_CountAndSortConnectedClients( int *numNonSpectatorClients, int *numConnectedClients, int *follow1, int *follow2, int *numPlayingClients, int *sortedClients ) {
	int		i;

	*follow1 = -1;
	*follow2 = -1;
	*numConnectedClients = 0;
	*numNonSpectatorClients = 0;
	*numPlayingClients = 0;
	level.numVotingClients = 0;		// don't count bots
	for ( i = 0; i < TEAM_NUM_TEAMS; i++ ) {
		level.numteamVotingClients[i] = 0;
	}

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if ( level.clients[i].pers.connected == CON_DISCONNECTED ) {
			continue;
		}

		sortedClients[*numConnectedClients] = i;
		( *numConnectedClients )++;

		if ( level.clients[i].sess.sessionTeam == TEAM_SPECTATOR ) {
			continue;
		}

		( *numNonSpectatorClients )++;

		// decide if this should be auto-followed
		if ( level.clients[i].pers.connected != CON_CONNECTED ) {
			continue;
		}

		( *numPlayingClients )++;
		if ( !( g_entities[i].r.svFlags & SVF_BOT ) ) {
			level.numVotingClients++;
			if ( level.clients[i].sess.sessionTeam == TEAM_RED ) {
				level.numteamVotingClients[0]++;
			} else if ( level.clients[i].sess.sessionTeam == TEAM_BLUE ) {
				level.numteamVotingClients[1]++;
			}
		}

		if ( *follow1 == -1 ) {
			*follow1 = i;
		} else if ( *follow2 == -1 ) {
			*follow2 = i;
		}
	}

	qsort( sortedClients, *numConnectedClients, sizeof( sortedClients[0] ), SortRanks );
}

/*
============
CalculateRanks

Recalculates the score ranks of all players
This will be called on every client connect, begin, disconnect, death,
and team change.
============
*/
void CalculateRanks( void ) {
	int		i;
	int		rank;
	int		score;
	int		newScore;
	gclient_t	*cl;

	G_CountAndSortConnectedClients( &level.numNonSpectatorClients, &level.numConnectedClients,
		&level.follow1, &level.follow2, &level.numPlayingClients, level.sortedClients );

	// set the rank value for all clients that are connected and not spectators
	if ( g_gametype.integer >= GT_TEAM ) {
		// in team games, rank is just the order of the teams, 0=red, 1=blue, 2=tied
		for ( i = 0;  i < level.numConnectedClients; i++ ) {
			cl = &level.clients[ level.sortedClients[i] ];
			if ( level.teamScores[TEAM_RED] == level.teamScores[TEAM_BLUE] ) {
				cl->ps.persistant[PERS_RANK] = 2;
			} else if ( level.teamScores[TEAM_RED] > level.teamScores[TEAM_BLUE] ) {
				cl->ps.persistant[PERS_RANK] = 0;
			} else {
				cl->ps.persistant[PERS_RANK] = 1;
			}
		}
	} else {	
		rank = -1;
		score = 0;
		for ( i = 0;  i < level.numPlayingClients; i++ ) {
			cl = &level.clients[ level.sortedClients[i] ];
			newScore = cl->ps.persistant[PERS_SCORE];
			if ( i == 0 || newScore != score ) {
				rank = i;
				// assume we aren't tied until the next client is checked
				level.clients[ level.sortedClients[i] ].ps.persistant[PERS_RANK] = rank;
			} else {
				// we are tied with the previous client
				level.clients[ level.sortedClients[i-1] ].ps.persistant[PERS_RANK] = rank | RANK_TIED_FLAG;
				level.clients[ level.sortedClients[i] ].ps.persistant[PERS_RANK] = rank | RANK_TIED_FLAG;
			}
			score = newScore;
			if ( g_gametype.integer == GT_SINGLE_PLAYER && level.numPlayingClients == 1 ) {
				level.clients[ level.sortedClients[i] ].ps.persistant[PERS_RANK] = rank | RANK_TIED_FLAG;
			}
		}
	}

	// set the CS_SCORES1/2 configstrings, which will be visible to everyone
	if ( g_gametype.integer >= GT_TEAM ) {
		trap_SetConfigstring( CS_SCORES1, va("%i", level.teamScores[TEAM_RED] ) );
		trap_SetConfigstring( CS_SCORES2, va("%i", level.teamScores[TEAM_BLUE] ) );
		trap_SetConfigstring( CS_FIRST_PLACE_NAME, "TEAM_RED" );
		trap_SetConfigstring( CS_SECOND_PLACE_NAME, "TEAM_BLUE" );
	} else {
		if ( level.numPlayingClients < 1 ) {
			trap_SetConfigstring( CS_SCORES1, va("%i", SCORE_NOT_PRESENT) );
			trap_SetConfigstring( CS_FIRST_PLACE_NAME, "" );
		} else {
			trap_SetConfigstring( CS_SCORES1, va("%i", level.clients[ level.sortedClients[0] ].ps.persistant[PERS_SCORE] ) );
			trap_SetConfigstring( CS_FIRST_PLACE_NAME, level.clients[ level.sortedClients[0] ].pers.netname );
		}

		if ( level.numPlayingClients < 2 ) {
			trap_SetConfigstring( CS_SCORES2, va("%i", SCORE_NOT_PRESENT) );
			trap_SetConfigstring( CS_SECOND_PLACE_NAME, "" );
		} else {
			trap_SetConfigstring( CS_SCORES2, va("%i", level.clients[ level.sortedClients[1] ].ps.persistant[PERS_SCORE] ) );
			trap_SetConfigstring( CS_SECOND_PLACE_NAME, level.clients[ level.sortedClients[1] ].pers.netname );
		}
	}

	// see if it is time to end the level
	CheckExitRules();

	// if we are at the intermission, send the new info to everyone
	if ( level.intermissiontime ) {
		SendScoreboardMessageToAllClients();
	}

	G_UpdateAwardConfigstrings();
}


/*
========================================================================

MAP CHANGING

========================================================================
*/

/*
========================
SendScoreboardMessageToAllClients

Do this at BeginIntermission time and whenever ranks are recalculated
due to enters/exits/forced team changes
========================
*/
void SendScoreboardMessageToAllClients( void ) {
	int		i;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if ( level.clients[ i ].pers.connected == CON_CONNECTED ) {
			DeathmatchScoreboardMessage( g_entities + i );
		}
	}

	G_UpdateAwardConfigstrings();
}

/*
========================
MoveClientToIntermission

When the intermission starts, this will be called for all players.
If a new client connects, this will be called after the spawn function.
========================
*/
void MoveClientToIntermission( gentity_t *ent ) {
	// take out of follow mode if needed
	if ( ent->client->sess.spectatorState == SPECTATOR_FOLLOW ) {
		StopFollowing( ent );
	}


	// move to the spot
	VectorCopy( level.intermission_origin, ent->s.origin );
	VectorCopy( level.intermission_origin, ent->client->ps.origin );
	VectorCopy (level.intermission_angle, ent->client->ps.viewangles);
	ent->client->ps.pm_type = PM_INTERMISSION;

	// clean up powerup info
	memset( ent->client->ps.powerups, 0, sizeof(ent->client->ps.powerups) );

	ent->client->ps.eFlags = 0;
	ent->s.eFlags = 0;
	ent->s.eType = ET_GENERAL;
	ent->s.modelindex = 0;
	ent->s.loopSound = 0;
	ent->s.event = 0;
	ent->r.contents = 0;
}

/*
==================
FindIntermissionPoint

This is also used for spectator spawns
==================
*/
void FindIntermissionPoint( void ) {
	gentity_t	*ent, *target;
	vec3_t		dir;

	// find the intermission spot
	ent = G_Find (NULL, FOFS(classname), "info_player_intermission");
	if ( !ent ) {	// the map creator forgot to put in an intermission point...
		SelectSpawnPoint ( vec3_origin, level.intermission_origin, level.intermission_angle );
	} else {
		VectorCopy (ent->s.origin, level.intermission_origin);
		VectorCopy (ent->s.angles, level.intermission_angle);
		// if it has a target, look towards it
		if ( ent->target ) {
			target = G_PickTarget( ent->target );
			if ( target ) {
				VectorSubtract( target->s.origin, level.intermission_origin, dir );
				vectoangles( dir, level.intermission_angle );
			}
		}
	}

}

/*
==================
G_ClearIntermissionReadyState

Clears the retail intermission-ready bitmask state and the one-shot exit latch.
==================
*/
static void G_ClearIntermissionReadyState( void ) {
	int		clientNum;

	level.readyToExit = qfalse;
	level.exitTime = 0;
	level.intermissionExitStatusLatched = qfalse;
	trap_SetConfigstring( CS_INTERMISSION_EXIT_STATUS, "" );

	if ( !level.clients ) {
		return;
	}

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		level.clients[clientNum].readyToExit = qfalse;
		level.clients[clientNum].ps.stats[STAT_CLIENTS_READY] = 0;
	}
}

/*
==================
G_PublishNextMapVoteCounts

Publishes the retail intermission next-map vote counts payload keyed by slot.
==================
*/
static void G_PublishNextMapVoteCounts( void ) {
	char	counts[MAX_INFO_STRING];
	int		slot;

	counts[0] = '\0';
	for ( slot = 0; slot < ROTATION_VOTE_SLOT_COUNT; slot++ ) {
		char	key[ROTATION_VOTE_KEY_BUFFER_SIZE];
		char	value[16];

		Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_COUNT_FORMAT, slot );
		Com_sprintf( value, sizeof( value ), "%i", level.nextMapVoteCounts[slot] );
		Info_SetValueForKey( counts, key, value );
	}

	trap_SetConfigstring( CS_ROTATION_CONFIGS, counts );
}

/*
==================
G_PublishRotationPreviewConfigstrings

Publishes the retail `nextmaps` title payload and zeroed intermission vote
counts when the host has queued preview cvars.
==================
*/
static void G_PublishRotationPreviewConfigstrings( void ) {
	char	nextmaps[MAX_STRING_CHARS];
	char	titles[MAX_INFO_STRING];
	int		slot;

	trap_SetConfigstring( CS_ROTATION_TITLES, "" );
	trap_SetConfigstring( CS_ROTATION_CONFIGS, "" );

	trap_Cvar_VariableStringBuffer( "nextmaps", nextmaps, sizeof( nextmaps ) );
	if ( !nextmaps[0] ) {
		return;
	}

	titles[0] = '\0';

	for ( slot = 0; slot < ROTATION_VOTE_SLOT_COUNT; slot++ ) {
		char	key[ROTATION_VOTE_KEY_BUFFER_SIZE];
		const char	*value;

		Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_MAP_FORMAT, slot );
		value = Info_ValueForKey( nextmaps, key );
		if ( value[0] ) {
			Info_SetValueForKey( titles, key, value );
		}

		Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_TITLE_FORMAT, slot );
		value = Info_ValueForKey( nextmaps, key );
		if ( value[0] ) {
			Info_SetValueForKey( titles, key, value );
		}

		Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_GAMETYPE_FORMAT, slot );
		value = Info_ValueForKey( nextmaps, key );
		if ( value[0] ) {
			Info_SetValueForKey( titles, key, value );
		}
	}

	trap_SetConfigstring( CS_ROTATION_TITLES, titles );
	level.voteTime = level.time;
	G_PublishNextMapVoteCounts();
	trap_SetConfigstring( CS_VOTE_TIME, va( "%i", level.voteTime ) );
}

/*
==================
G_SelectNextMapVoteSlot

Chooses the winning intermission vote slot using the retail highest-count rule
with random tie-breaking across equally voted arenas.
==================
*/
static int G_SelectNextMapVoteSlot( void ) {
	char		nextmaps[MAX_STRING_CHARS];
	char	mapName[MAX_QPATH];
	char	key[ROTATION_VOTE_KEY_BUFFER_SIZE];
	int		maxVotes;
	int		tiedSlots[ROTATION_VOTE_SLOT_COUNT];
	int		tiedSlotCount;
	int		slot;

	maxVotes = -1;
	tiedSlotCount = 0;
	trap_Cvar_VariableStringBuffer( "nextmaps", nextmaps, sizeof( nextmaps ) );

	for ( slot = 0; slot < ROTATION_VOTE_SLOT_COUNT; slot++ ) {
		const char	*value;

		Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_MAP_FORMAT, slot );
		value = Info_ValueForKey( nextmaps, key );
		Q_strncpyz( mapName, value ? value : "", sizeof( mapName ) );
		if ( !mapName[0] ) {
			continue;
		}

		if ( level.nextMapVoteCounts[slot] > maxVotes ) {
			maxVotes = level.nextMapVoteCounts[slot];
			tiedSlotCount = 0;
			tiedSlots[tiedSlotCount++] = slot;
		} else if ( level.nextMapVoteCounts[slot] == maxVotes ) {
			tiedSlots[tiedSlotCount++] = slot;
		}
	}

	if ( tiedSlotCount <= 0 ) {
		return -1;
	}

	if ( tiedSlotCount == 1 ) {
		return tiedSlots[0];
	}

	slot = (int)( (float)( rand() & 0x7fff ) / 32767.0f * tiedSlotCount );
	if ( slot >= tiedSlotCount ) {
		slot = tiedSlotCount - 1;
	}

	return tiedSlots[slot];
}

/*
==================
BeginIntermission
==================
*/
void BeginIntermission( void ) {
	int			i;
	gentity_t	*client;

	if ( level.intermissiontime ) {
		return;		// already active
	}

	trap_SetConfigstring( CS_INTERMISSION, "1" );

	// if in tournement mode, change the wins / losses
	if ( g_gametype.integer == GT_TOURNAMENT ) {
		AdjustTournamentScores();
	}

	level.intermissiontime = level.time;
	FindIntermissionPoint();

	if (g_singlePlayer.integer) {
		trap_Cvar_Set("ui_singlePlayerActive", "0");
		UpdateTournamentInfo();
	}

	G_ClearVoteState();
	G_ClearNextMapVoteState();
	G_ClearIntermissionReadyState();
	G_PublishRotationPreviewConfigstrings();

	// move all clients to the intermission point
	for (i=0 ; i< level.maxclients ; i++) {
		client = g_entities + i;
		if (!client->inuse)
			continue;
		// respawn if dead
		if (client->health <= 0) {
			respawn(client);
		}
		MoveClientToIntermission( client );
	}

	// send the current scoring to all clients
	SendScoreboardMessageToAllClients();

}


/*
=============
ExitLevel

When the intermission has been exited, the server is either killed
or moved to a new level based on the "nextmap" cvar 

=============
*/
void ExitLevel (void) {
	int		i;
	int		selectedSlot;
	gclient_t *cl;
	char		serverinfo[MAX_INFO_STRING];
	char		mapName[MAX_QPATH];
	char		nextmaps[MAX_STRING_CHARS];
	char		selectedMap[MAX_QPATH];
	char		selectedCfg[MAX_QPATH];

	trap_GetServerinfo( serverinfo, sizeof( serverinfo ) );
	Q_strncpyz( mapName, Info_ValueForKey( serverinfo, SERVERINFO_KEY_MAPNAME ), sizeof( mapName ) );

	if ( trap_Cvar_VariableIntegerValue( "sv_killserver" ) ) {
		trap_SendConsoleCommand( EXEC_APPEND, "killserver\n" );
		return;
	}

	if ( trap_Cvar_VariableIntegerValue( "sv_quitOnExitLevel" ) ) {
		trap_SendConsoleCommand( EXEC_APPEND, "quit\n" );
		return;
	}

	//bot interbreeding
	BotInterbreedEndMatch();
	trap_SetConfigstring( CS_INTERMISSION, "0" );

	if ( g_gametype.integer == GT_TOURNAMENT ) {
		RemoveTournamentLoser();
	}

	selectedSlot = -1;
	selectedMap[0] = '\0';
	selectedCfg[0] = '\0';

	if ( !g_singlePlayer.integer && !( g_voteFlags.integer & VF_NO_ENDVOTE ) ) {
		trap_Cvar_VariableStringBuffer( "nextmaps", nextmaps, sizeof( nextmaps ) );
		if ( nextmaps[0] ) {
			char	key[ROTATION_VOTE_KEY_BUFFER_SIZE];
			const char	*value;

			selectedSlot = G_SelectNextMapVoteSlot();
			if ( selectedSlot >= 0 ) {
				Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_MAP_FORMAT, selectedSlot );
				value = Info_ValueForKey( nextmaps, key );
				Q_strncpyz( selectedMap, value ? value : "", sizeof( selectedMap ) );
				Com_sprintf( key, sizeof( key ), ROTATION_VOTE_KEY_CONFIG_FORMAT, selectedSlot );
				value = Info_ValueForKey( nextmaps, key );
				Q_strncpyz( selectedCfg, value ? value : "", sizeof( selectedCfg ) );
			}
		}
	}

	if ( selectedMap[0] && Q_stricmp( selectedMap, "default" ) ) {
		if ( selectedCfg[0] ) {
			trap_Cvar_Set( "nextmap", va( "map %s %s", selectedMap, selectedCfg ) );
		} else {
			trap_Cvar_Set( "nextmap", va( "map %s", selectedMap ) );
		}
	}

	if ( !g_singlePlayer.integer && ( !Q_stricmp( mapName, selectedMap ) || !Q_stricmp( selectedMap, "default" ) ) ) {
		trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\n" );
		level.restarted = qtrue;
		level.intermissionQueued = 0;
	} else {
		trap_SendConsoleCommand( EXEC_APPEND, "vstr nextmap\n" );
	}

	G_ClearVoteState();
	G_ClearNextMapVoteState();
	G_ClearIntermissionReadyState();
	trap_SetConfigstring( CS_ROTATION_TITLES, "" );
	trap_SetConfigstring( CS_ROTATION_CONFIGS, "" );

	level.intermissionQueued = 0;
	level.changemap = NULL;
	level.intermissiontime = 0;

	// reset all the scores so we don't enter the intermission again
	level.teamScores[TEAM_RED] = 0;
	level.teamScores[TEAM_BLUE] = 0;
	for ( i=0 ; i< g_maxclients.integer ; i++ ) {
		cl = level.clients + i;
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}
		cl->ps.persistant[PERS_SCORE] = 0;
	}

	// we need to do this here before chaning to CON_CONNECTING
	G_WriteSessionData();

	// change all client states to connecting, so the early players into the
	// next level will know the others aren't done reconnecting
	for (i=0 ; i< g_maxclients.integer ; i++) {
		if ( level.clients[i].pers.connected == CON_CONNECTED ) {
			level.clients[i].pers.connected = CON_CONNECTING;
		}
	}

}

/*
=================
G_LogPrintf

Print to the logfile with a time stamp if it is open
=================
*/
void QDECL G_LogPrintf( const char *fmt, ... ) {
	va_list		argptr;
	char		string[1024];
	int			min, tens, sec;

	sec = level.time / 1000;

	min = sec / 60;
	sec -= min * 60;
	tens = sec / 10;
	sec -= tens * 10;

	Com_sprintf( string, sizeof(string), "%3i:%i%i ", min, tens, sec );

	va_start( argptr, fmt );
	vsprintf( string +7 , fmt,argptr );
	va_end( argptr );

	if ( g_dedicated.integer ) {
		G_Printf( "%s", string + 7 );
	}

	if ( !level.logFile ) {
		return;
	}

	trap_FS_Write( string, strlen( string ), level.logFile );
}

/*
================
G_RankAppendPayload

Appends formatted text to a rankings event payload buffer.
================
*/
static qboolean G_RankAppendPayload( char *buffer, size_t bufferSize, size_t *length, const char *fmt, ... ) {
	va_list args;
	int written;

	if ( !buffer || !length || !fmt || bufferSize == 0 || *length >= bufferSize ) {
		return qfalse;
	}

	va_start( args, fmt );
	written = Q_vsnprintf( buffer + *length, bufferSize - *length, fmt, args );
	va_end( args );

	if ( written < 0 || ( size_t )written >= ( bufferSize - *length ) ) {
		return qfalse;
	}

	*length += written;
	return qtrue;
}

/*
================
G_RankEscapeJsonString

Escapes control characters and quotes so netnames and hostnames remain valid
inside the source-side JSON payload proxy.
================
*/
static void G_RankEscapeJsonString( const char *src, char *dst, size_t dstSize ) {
	size_t outIndex;
	const char *cursor;

	if ( !dst || dstSize == 0 ) {
		return;
	}

	outIndex = 0;
	cursor = src ? src : "";

	while ( *cursor && outIndex + 1 < dstSize ) {
		const char *escape = NULL;
		size_t escapeLength = 0;
		unsigned char ch = ( unsigned char )*cursor;

		switch ( ch ) {
		case '\\':
			escape = "\\\\";
			escapeLength = 2;
			break;
		case '"':
			escape = "\\\"";
			escapeLength = 2;
			break;
		case '\n':
			escape = "\\n";
			escapeLength = 2;
			break;
		case '\r':
			escape = "\\r";
			escapeLength = 2;
			break;
		case '\t':
			escape = "\\t";
			escapeLength = 2;
			break;
		default:
			break;
		}

		if ( escape ) {
			if ( outIndex + escapeLength >= dstSize ) {
				break;
			}

			dst[outIndex++] = escape[0];
			dst[outIndex++] = escape[1];
			cursor++;
			continue;
		}

		if ( ch < 0x20 ) {
			dst[outIndex++] = ' ';
			cursor++;
			continue;
		}

		dst[outIndex++] = *cursor++;
	}

	dst[outIndex] = '\0';
}

/*
================
G_RankFormatSteamId

Formats the recovered 64-bit SteamID form used by the retail rankings event
publishers. Bots carry the retail "0" placeholder.
================
*/
static void G_RankFormatSteamId( const gentity_t *ent, char *buffer, size_t bufferSize ) {
	unsigned long long steamId;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	if ( !ent || !ent->client || ( ent->r.svFlags & SVF_BOT ) ) {
		Q_strncpyz( buffer, "0", bufferSize );
		return;
	}

	steamId = ( ( unsigned long long )ent->client->pers.steamIdHigh << 32 ) |
		ent->client->pers.steamIdLow;
	Com_sprintf( buffer, bufferSize, "%llu", steamId );
}

/*
================
G_RankBuildClientEventPayload

Retail qagame publishes Json::Value payloads for player connect and disconnect
events. The exact VM/native object ABI is still unrecovered in writable source,
so the reconstructed bridge serializes an equivalent JSON-text payload proxy.
================
*/
static qboolean G_RankBuildClientEventPayload( gentity_t *ent, char *buffer, size_t bufferSize ) {
	char escapedName[MAX_NETNAME * 2 + 1];
	char steamId[32];
	size_t length;

	if ( !ent || !ent->client || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	length = 0;

	G_RankEscapeJsonString( ent->client->pers.netname, escapedName, sizeof( escapedName ) );
	G_RankFormatSteamId( ent, steamId, sizeof( steamId ) );

	return G_RankAppendPayload( buffer, bufferSize, &length,
		"{\"TIME\":%i,\"WARMUP\":%s,\"MATCH_GUID\":\"%s\",\"NAME\":\"%s\",\"STEAM_ID\":\"%s\"}",
		( level.time - level.startTime ) / 1000,
		( level.warmupTime != 0 ) ? "true" : "false",
		level.rankMatchGuid,
		escapedName,
		steamId );
}

/*
================
G_RankBuildMatchStartedPayload

Serializes the recovered MATCH_STARTED roster payload fields into the writable
source's JSON-text proxy format.
================
*/
static qboolean G_RankBuildMatchStartedPayload( char *buffer, size_t bufferSize ) {
	char hostname[MAX_CVAR_VALUE_STRING];
	char escapedHostname[MAX_CVAR_VALUE_STRING * 2 + 1];
	size_t length;
	qboolean firstPlayer;
	int i;

	if ( !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	length = 0;
	firstPlayer = qtrue;

	trap_Cvar_VariableStringBuffer( "sv_hostname", hostname, sizeof( hostname ) );
	G_RankEscapeJsonString( hostname, escapedHostname, sizeof( escapedHostname ) );

	if ( !G_RankAppendPayload( buffer, bufferSize, &length,
		"{\"MATCH_GUID\":\"%s\",\"SERVER_TITLE\":\"%s\",\"PLAYERS\":[",
		level.rankMatchGuid,
		escapedHostname ) ) {
		return qfalse;
	}

	for ( i = 0; i < level.maxclients; i++ ) {
		gentity_t *ent;
		gclient_t *client;
		char escapedName[MAX_NETNAME * 2 + 1];
		char steamId[32];

		client = &level.clients[i];
		if ( client->pers.connected == CON_DISCONNECTED ) {
			continue;
		}

		ent = &g_entities[i];
		G_RankEscapeJsonString( client->pers.netname, escapedName, sizeof( escapedName ) );
		G_RankFormatSteamId( ent, steamId, sizeof( steamId ) );

		if ( !firstPlayer && !G_RankAppendPayload( buffer, bufferSize, &length, "," ) ) {
			return qfalse;
		}

		if ( !G_RankAppendPayload( buffer, bufferSize, &length,
			"{\"NAME\":\"%s\",\"STEAM_ID\":\"%s\",\"TEAM\":%i}",
			escapedName,
			steamId,
			client->sess.sessionTeam ) ) {
			return qfalse;
		}

		firstPlayer = qfalse;
	}

	return G_RankAppendPayload( buffer, bufferSize, &length, "]}" );
}

/*
================
G_RankAppendJsonFieldPrefix

Appends the `,"KEY":` or `"KEY":` prefix used by the source-side JSON proxy
builders.
================
*/
static qboolean G_RankAppendJsonFieldPrefix( char *buffer, size_t bufferSize, size_t *length,
	qboolean *firstField, const char *fieldName ) {
	if ( !buffer || !length || !firstField || !fieldName ) {
		return qfalse;
	}

	if ( !*firstField ) {
		if ( !G_RankAppendPayload( buffer, bufferSize, length, "," ) ) {
			return qfalse;
		}
	} else {
		*firstField = qfalse;
	}

	return G_RankAppendPayload( buffer, bufferSize, length, "\"%s\":", fieldName );
}

/*
================
G_RankAppendJsonStringField

Appends one quoted JSON string field to the active payload buffer.
================
*/
static qboolean G_RankAppendJsonStringField( char *buffer, size_t bufferSize, size_t *length,
	qboolean *firstField, const char *fieldName, const char *fieldValue ) {
	char escapedValue[MAX_STRING_CHARS * 2 + 1];

	if ( !G_RankAppendJsonFieldPrefix( buffer, bufferSize, length, firstField, fieldName ) ) {
		return qfalse;
	}

	G_RankEscapeJsonString( fieldValue ? fieldValue : "", escapedValue, sizeof( escapedValue ) );
	return G_RankAppendPayload( buffer, bufferSize, length, "\"%s\"", escapedValue );
}

/*
================
G_RankAppendJsonIntField

Appends one integer JSON field to the active payload buffer.
================
*/
static qboolean G_RankAppendJsonIntField( char *buffer, size_t bufferSize, size_t *length,
	qboolean *firstField, const char *fieldName, int fieldValue ) {
	if ( !G_RankAppendJsonFieldPrefix( buffer, bufferSize, length, firstField, fieldName ) ) {
		return qfalse;
	}

	return G_RankAppendPayload( buffer, bufferSize, length, "%i", fieldValue );
}

/*
================
G_RankAppendJsonBoolField

Appends one boolean JSON field to the active payload buffer.
================
*/
static qboolean G_RankAppendJsonBoolField( char *buffer, size_t bufferSize, size_t *length,
	qboolean *firstField, const char *fieldName, qboolean fieldValue ) {
	if ( !G_RankAppendJsonFieldPrefix( buffer, bufferSize, length, firstField, fieldName ) ) {
		return qfalse;
	}

	return G_RankAppendPayload( buffer, bufferSize, length, "%s", fieldValue ? "true" : "false" );
}

/*
================
G_RankAppendJsonFloatField

Appends one float JSON field to the active payload buffer.
================
*/
static qboolean G_RankAppendJsonFloatField( char *buffer, size_t bufferSize, size_t *length,
	qboolean *firstField, const char *fieldName, float fieldValue ) {
	if ( !G_RankAppendJsonFieldPrefix( buffer, bufferSize, length, firstField, fieldName ) ) {
		return qfalse;
	}

	return G_RankAppendPayload( buffer, bufferSize, length, "%.3f", fieldValue );
}

/*
================
G_RankAppendJsonRawField

Appends one prebuilt JSON object or scalar field to the active payload buffer.
================
*/
static qboolean G_RankAppendJsonRawField( char *buffer, size_t bufferSize, size_t *length,
	qboolean *firstField, const char *fieldName, const char *fieldValue ) {
	if ( !G_RankAppendJsonFieldPrefix( buffer, bufferSize, length, firstField, fieldName ) ) {
		return qfalse;
	}

	return G_RankAppendPayload( buffer, bufferSize, length, "%s", fieldValue ? fieldValue : "null" );
}

/*
================
G_RankWeaponName

Maps a gameplay weapon enum to the uppercase retail-style key used in the
rankings payload proxies.
================
*/
static const char *G_RankWeaponName( weapon_t weapon ) {
	switch ( weapon ) {
	case WP_GAUNTLET:
		return "GAUNTLET";
	case WP_MACHINEGUN:
		return "MACHINEGUN";
	case WP_SHOTGUN:
		return "SHOTGUN";
	case WP_GRENADE_LAUNCHER:
		return "GRENADE";
	case WP_ROCKET_LAUNCHER:
		return "ROCKET";
	case WP_LIGHTNING:
		return "LIGHTNING";
	case WP_RAILGUN:
		return "RAILGUN";
	case WP_PLASMAGUN:
		return "PLASMA";
	case WP_BFG:
		return "BFG10K";
	case WP_GRAPPLING_HOOK:
		return "GRAPPLE";
	case WP_NAILGUN:
		return "NAILGUN";
	case WP_PROX_LAUNCHER:
		return "PROXMINE";
	case WP_CHAINGUN:
		return "CHAINGUN";
	case WP_HEAVY_MACHINEGUN:
		return "HMG";
	default:
		break;
	}

	return "OTHER_WEAPON";
}

/*
================
G_RankMeansOfDeathName

Resolves the retail death-name token used by PLAYER_KILL and PLAYER_DEATH.
================
*/
static const char *G_RankMeansOfDeathName( int meansOfDeath ) {
	switch ( meansOfDeath ) {
	case MOD_GAUNTLET:
		return "GAUNTLET";
	case MOD_MACHINEGUN:
		return "MACHINEGUN";
	case MOD_SHOTGUN:
		return "SHOTGUN";
	case MOD_GRENADE:
	case MOD_GRENADE_SPLASH:
		return "GRENADE";
	case MOD_ROCKET:
	case MOD_ROCKET_SPLASH:
		return "ROCKET";
	case MOD_PLASMA:
	case MOD_PLASMA_SPLASH:
		return "PLASMA";
	case MOD_RAILGUN:
	case MOD_RAILGUN_HEADSHOT:
		return "RAILGUN";
	case MOD_LIGHTNING:
		return "LIGHTNING";
	case MOD_BFG:
	case MOD_BFG_SPLASH:
		return "BFG10K";
	case MOD_NAIL:
		return "NAILGUN";
	case MOD_CHAINGUN:
		return "CHAINGUN";
	case MOD_PROXIMITY_MINE:
		return "PROXMINE";
	case MOD_GRAPPLE:
		return "GRAPPLE";
	case MOD_SWITCHTEAM:
		return "SWITCHTEAM";
	case MOD_THAW:
		return "THAW";
	case MOD_LIGHTNING_DISCHARGE:
		return "LIGHTNING_DISCHARGE";
	case MOD_HMG:
		return "HMG";
	default:
		break;
	}

	return "OTHER_DEATH";
}

/*
================
G_RankMeansOfDeathWeapon

Maps a means-of-death enum back to the owning weapon slot for payload naming
and reduced damage buckets.
================
*/
static weapon_t G_RankMeansOfDeathWeapon( int meansOfDeath ) {
	switch ( meansOfDeath ) {
	case MOD_GAUNTLET:
		return WP_GAUNTLET;
	case MOD_MACHINEGUN:
		return WP_MACHINEGUN;
	case MOD_SHOTGUN:
		return WP_SHOTGUN;
	case MOD_GRENADE:
	case MOD_GRENADE_SPLASH:
		return WP_GRENADE_LAUNCHER;
	case MOD_ROCKET:
	case MOD_ROCKET_SPLASH:
		return WP_ROCKET_LAUNCHER;
	case MOD_PLASMA:
	case MOD_PLASMA_SPLASH:
		return WP_PLASMAGUN;
	case MOD_RAILGUN:
	case MOD_RAILGUN_HEADSHOT:
		return WP_RAILGUN;
	case MOD_LIGHTNING:
	case MOD_LIGHTNING_DISCHARGE:
		return WP_LIGHTNING;
	case MOD_BFG:
	case MOD_BFG_SPLASH:
		return WP_BFG;
	case MOD_NAIL:
		return WP_NAILGUN;
	case MOD_CHAINGUN:
		return WP_CHAINGUN;
	case MOD_PROXIMITY_MINE:
		return WP_PROX_LAUNCHER;
	case MOD_GRAPPLE:
		return WP_GRAPPLING_HOOK;
	case MOD_HMG:
		return WP_HEAVY_MACHINEGUN;
	default:
		break;
	}

	return WP_NONE;
}

/*
================
G_RankTeamName

Maps a session team enum to the retail string token used by FLAG_STATUS.
================
*/
static const char *G_RankTeamName( int team ) {
	switch ( team ) {
	case TEAM_RED:
		return "RED";
	case TEAM_BLUE:
		return "BLUE";
	case TEAM_SPECTATOR:
		return "SPECTATOR";
	default:
		break;
	}

	return "FREE";
}

/*
================
G_RankFlagStatusName

Collapses the internal flag-status enum onto the string values recovered from
the retail FLAG_STATUS publisher.
================
*/
static const char *G_RankFlagStatusName( int status ) {
	switch ( status ) {
	case FLAG_ATBASE:
		return "FLAG_ATBASE";
	case FLAG_DROPPED:
		return "FLAG_DROPPED";
	case FLAG_TAKEN:
	case FLAG_TAKEN_RED:
	case FLAG_TAKEN_BLUE:
		return "FLAG_TAKEN";
	default:
		break;
	}

	return "FLAG_UNKNOWN";
}

/*
================
G_RankGametypePublishesRound

Returns whether the active gametype carries the retail round metadata inside
PLAYER_KILL and PLAYER_DEATH.
================
*/
static qboolean G_RankGametypePublishesRound( void ) {
	switch ( g_gametype.integer ) {
	case GT_CLAN_ARENA:
	case GT_FREEZE:
	case GT_ATTACK_DEFEND:
	case GT_RED_ROVER:
		return qtrue;
	default:
		break;
	}

	return qfalse;
}

/*
================
G_RankCountAliveDeadByTeam

Builds the reduced team alive/dead counts consumed by the retail round-aware
kill and death payloads.
================
*/
static void G_RankCountAliveDeadByTeam( int deadCounts[TEAM_NUM_TEAMS], int aliveCounts[TEAM_NUM_TEAMS] ) {
	int clientNum;

	if ( !deadCounts || !aliveCounts ) {
		return;
	}

	memset( deadCounts, 0, sizeof( int ) * TEAM_NUM_TEAMS );
	memset( aliveCounts, 0, sizeof( int ) * TEAM_NUM_TEAMS );

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gclient_t *client;
		team_t team;

		client = &level.clients[clientNum];
		if ( client->pers.connected == CON_DISCONNECTED ) {
			continue;
		}

		team = client->sess.sessionTeam;
		if ( team < TEAM_FREE || team >= TEAM_NUM_TEAMS ) {
			continue;
		}

		if ( client->ps.pm_type == PM_NORMAL ) {
			aliveCounts[team]++;
		} else {
			deadCounts[team]++;
		}
	}
}

/*
================
G_RankBuildWeaponsUsedMask

Builds a compact bitmask of weapons the client held or used during the current
session, matching the payload style recovered for ranked race and match stats.
================
*/
static unsigned int G_RankBuildWeaponsUsedMask( const gclient_t *client ) {
	unsigned int weaponsUsed;
	weapon_t weapon;

	if ( !client ) {
		return 0u;
	}

	weaponsUsed = (unsigned int)client->ps.stats[STAT_WEAPONS];
	for ( weapon = WP_GAUNTLET; weapon < WP_NUM_WEAPONS; weapon++ ) {
		if ( weapon >= 32 ) {
			break;
		}

		if ( client->pers.weaponFrags[weapon] > 0
			|| client->pers.weaponDamage[weapon] > 0
			|| client->pers.accuracy_hits[weapon] > 0
			|| client->pers.accuracy_shots[weapon] > 0 ) {
			weaponsUsed |= ( 1u << weapon );
		}
	}

	return weaponsUsed;
}

/*
================
G_RankGetClientModel

Extracts the current userinfo model string used by the retail PLAYER_STATS
payload.
================
*/
static void G_RankGetClientModel( const gentity_t *ent, char *buffer, size_t bufferSize ) {
	char userinfo[MAX_INFO_STRING];
	const char *model;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !ent || !ent->client ) {
		return;
	}

	trap_GetUserinfo( ent->s.number, userinfo, sizeof( userinfo ) );
	model = Info_ValueForKey( userinfo, "model" );
	if ( !model || !model[0] ) {
		model = "default";
	}

	Q_strncpyz( buffer, model, bufferSize );
}

/*
================
G_RankResolveEventSteamIds

Feeds the native event bridge the same zeroed SteamID pair retail uses for bot
participants.
================
*/
static void G_RankResolveEventSteamIds( const gentity_t *ent, uint32_t *steamIdLow, uint32_t *steamIdHigh ) {
	if ( steamIdLow ) {
		*steamIdLow = 0;
	}
	if ( steamIdHigh ) {
		*steamIdHigh = 0;
	}

	if ( !ent || !ent->client || ( ent->r.svFlags & SVF_BOT ) ) {
		return;
	}

	if ( steamIdLow ) {
		*steamIdLow = ent->client->pers.steamIdLow;
	}
	if ( steamIdHigh ) {
		*steamIdHigh = ent->client->pers.steamIdHigh;
	}
}

/*
================
G_RankBuildVectorObject

Formats one `{"X":...,"Y":...,"Z":...}` object for the JSON proxy payloads.
================
*/
static qboolean G_RankBuildVectorObject( const vec3_t value, char *buffer, size_t bufferSize ) {
	size_t length;
	qboolean firstField;

	if ( !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	length = 0;
	firstField = qtrue;

	if ( !G_RankAppendPayload( buffer, bufferSize, &length, "{" ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonFloatField( buffer, bufferSize, &length, &firstField, "X", value[0] ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonFloatField( buffer, bufferSize, &length, &firstField, "Y", value[1] ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonFloatField( buffer, bufferSize, &length, &firstField, "Z", value[2] ) ) {
		return qfalse;
	}

	return G_RankAppendPayload( buffer, bufferSize, &length, "}" );
}

/*
================
G_RankResolveMedalIndex

Maps the retail medal tokens onto the reduced source-side medal counters.
================
*/
static rankMedal_t G_RankResolveMedalIndex( const char *medal ) {
	if ( !medal || !medal[0] ) {
		return RANK_MEDAL_COUNT;
	}
	if ( Q_stricmp( medal, "IMPRESSIVE" ) == 0 ) {
		return RANK_MEDAL_IMPRESSIVE;
	}
	if ( Q_stricmp( medal, "EXCELLENT" ) == 0 ) {
		return RANK_MEDAL_EXCELLENT;
	}
	if ( Q_stricmp( medal, "GAUNTLET" ) == 0 || Q_stricmp( medal, "HUMILIATION" ) == 0 ) {
		return RANK_MEDAL_HUMILIATION;
	}
	if ( Q_stricmp( medal, "REVENGE" ) == 0 ) {
		return RANK_MEDAL_REVENGE;
	}
	if ( Q_stricmp( medal, "COMBOKILL" ) == 0 ) {
		return RANK_MEDAL_COMBOKILL;
	}
	if ( Q_stricmp( medal, "RAMPAGE" ) == 0 ) {
		return RANK_MEDAL_RAMPAGE;
	}
	if ( Q_stricmp( medal, "MIDAIR" ) == 0 ) {
		return RANK_MEDAL_MIDAIR;
	}
	if ( Q_stricmp( medal, "PERFORATED" ) == 0 ) {
		return RANK_MEDAL_PERFORATED;
	}
	if ( Q_stricmp( medal, "HEADSHOT" ) == 0 ) {
		return RANK_MEDAL_HEADSHOT;
	}
	if ( Q_stricmp( medal, "ACCURACY" ) == 0 ) {
		return RANK_MEDAL_ACCURACY;
	}
	if ( Q_stricmp( medal, "QUADGOD" ) == 0 ) {
		return RANK_MEDAL_QUADGOD;
	}
	if ( Q_stricmp( medal, "FIRSTFRAG" ) == 0 ) {
		return RANK_MEDAL_FIRSTFRAG;
	}
	if ( Q_stricmp( medal, "PERFECT" ) == 0 ) {
		return RANK_MEDAL_PERFECT;
	}
	if ( Q_stricmp( medal, "DEFENDS" ) == 0 || Q_stricmp( medal, "DEFEND" ) == 0 || Q_stricmp( medal, "DEFENSE" ) == 0 ) {
		return RANK_MEDAL_DEFENDS;
	}
	if ( Q_stricmp( medal, "ASSISTS" ) == 0 || Q_stricmp( medal, "ASSIST" ) == 0 ) {
		return RANK_MEDAL_ASSISTS;
	}
	if ( Q_stricmp( medal, "CAPTURES" ) == 0 || Q_stricmp( medal, "CAPTURE" ) == 0 ) {
		return RANK_MEDAL_CAPTURES;
	}

	return RANK_MEDAL_COUNT;
}

/*
================
G_RankMedalPersistantTotal

Returns the medal totals still tracked by legacy replicated playerstate or
existing per-client gameplay counters.
================
*/
static int G_RankMedalPersistantTotal( const gclient_t *client, rankMedal_t medalIndex ) {
	if ( !client ) {
		return 0;
	}

	switch ( medalIndex ) {
	case RANK_MEDAL_IMPRESSIVE:
		return client->ps.persistant[PERS_IMPRESSIVE_COUNT];
	case RANK_MEDAL_EXCELLENT:
		return client->ps.persistant[PERS_EXCELLENT_COUNT];
	case RANK_MEDAL_HUMILIATION:
		return client->ps.persistant[PERS_GAUNTLET_FRAG_COUNT];
	case RANK_MEDAL_DEFENDS:
		return client->ps.persistant[PERS_DEFEND_COUNT];
	case RANK_MEDAL_ASSISTS:
		return client->ps.persistant[PERS_ASSIST_COUNT];
	case RANK_MEDAL_CAPTURES:
		return client->ps.persistant[PERS_CAPTURES];
	default:
		break;
	}

	return 0;
}

/*
================
G_RankGetMedalTotal

Returns the best source-side total available for one retail medal bucket.
================
*/
static int G_RankGetMedalTotal( const gclient_t *client, rankMedal_t medalIndex ) {
	int total;
	int persTotal;

	if ( !client || medalIndex < 0 || medalIndex >= RANK_MEDAL_COUNT ) {
		return 0;
	}

	total = client->pers.rankMedalCounts[medalIndex];
	persTotal = G_RankMedalPersistantTotal( client, medalIndex );
	if ( persTotal > total ) {
		total = persTotal;
	}

	return total;
}

/*
================
G_RankResolveAwardEventId

Maps retail medal counters onto the Quake Live EV_AWARD taxonomy.
================
*/
static int G_RankResolveAwardEventId( rankMedal_t medalIndex ) {
	switch ( medalIndex ) {
	case RANK_MEDAL_COMBOKILL:
		return 0;
	case RANK_MEDAL_RAMPAGE:
		return 1;
	case RANK_MEDAL_MIDAIR:
		return 2;
	case RANK_MEDAL_REVENGE:
		return 3;
	case RANK_MEDAL_PERFORATED:
		return 4;
	case RANK_MEDAL_HEADSHOT:
		return 5;
	case RANK_MEDAL_ACCURACY:
		return 6;
	case RANK_MEDAL_QUADGOD:
		return 7;
	case RANK_MEDAL_FIRSTFRAG:
		return 8;
	case RANK_MEDAL_PERFECT:
		return 9;
	default:
		break;
	}

	return -1;
}

/*
================
G_RankResolveAwardMedalIndex

Maps a Quake Live EV_AWARD identifier back to the owning medal counter.
================
*/
static rankMedal_t G_RankResolveAwardMedalIndex( int award ) {
	switch ( award ) {
	case 0:
		return RANK_MEDAL_COMBOKILL;
	case 1:
		return RANK_MEDAL_RAMPAGE;
	case 2:
		return RANK_MEDAL_MIDAIR;
	case 3:
		return RANK_MEDAL_REVENGE;
	case 4:
		return RANK_MEDAL_PERFORATED;
	case 5:
		return RANK_MEDAL_HEADSHOT;
	case 6:
		return RANK_MEDAL_ACCURACY;
	case 7:
		return RANK_MEDAL_QUADGOD;
	case 8:
		return RANK_MEDAL_FIRSTFRAG;
	case 9:
		return RANK_MEDAL_PERFECT;
	default:
		break;
	}

	return RANK_MEDAL_COUNT;
}

/*
================
G_AddAwardEntity

Publishes the recovered retail EV_AWARD temp entity for the scoring client.
================
*/
static void G_AddAwardEntity( gentity_t *ent, int award ) {
	gentity_t	*tent;
	rankMedal_t	medalIndex;
	int		awardCount;

	if ( !ent || !ent->client ) {
		return;
	}

	medalIndex = G_RankResolveAwardMedalIndex( award );
	if ( medalIndex < 0 || medalIndex >= RANK_MEDAL_COUNT ) {
		return;
	}

	awardCount = G_RankGetMedalTotal( ent->client, medalIndex );
	if ( awardCount <= 0 ) {
		return;
	}

	tent = G_TempEntity( ent->client->ps.origin, EV_AWARD );
	tent->r.svFlags |= SVF_SINGLECLIENT;
	tent->r.singleClient = ent->s.number;
	G_SetRetailEventRecipient( tent, ent->s.number );
	tent->s.frame = awardCount;
	G_SetRetailEventData( &tent->s, award );

	ent->client->rewardTime = level.time + REWARD_SPRITE_TIME;
}

/*
================
G_RankGetPlayerRank

Rebuilds the per-player scoreboard placement emitted by retail PLAYER_STATS,
including tied-rank detection in team and non-team modes.
================
*/
static int G_RankGetPlayerRank( const gclient_t *client, qboolean *tied ) {
	int i;
	int rank;
	int previousScore;

	if ( tied ) {
		*tied = qfalse;
	}

	if ( !client ) {
		return -1;
	}

	rank = -1;
	previousScore = 0;
	for ( i = 0; i < level.numPlayingClients; i++ ) {
		const gclient_t *sortedClient;
		int currentScore;
		qboolean isTied;

		sortedClient = &level.clients[level.sortedClients[i]];
		currentScore = sortedClient->ps.persistant[PERS_SCORE];
		if ( i == 0 || currentScore != previousScore ) {
			rank = i;
		}
		if ( sortedClient != client ) {
			previousScore = currentScore;
			continue;
		}

		isTied = qfalse;
		if ( i > 0 && level.clients[level.sortedClients[i - 1]].ps.persistant[PERS_SCORE] == currentScore ) {
			isTied = qtrue;
		} else if ( i + 1 < level.numPlayingClients &&
			level.clients[level.sortedClients[i + 1]].ps.persistant[PERS_SCORE] == currentScore ) {
			isTied = qtrue;
		}

		if ( tied ) {
			*tied = isTied;
		}
		return rank + 1;
	}

	return -1;
}

/*
================
G_RankUsesTeamResultFields

Returns whether retail PLAYER_STATS emits the team-rank/result fields for the
current gametype.
================
*/
static qboolean G_RankUsesTeamResultFields( void ) {
	return (qboolean)( g_gametype.integer >= GT_TEAM && g_gametype.integer != GT_RED_ROVER );
}

/*
================
G_RankGetTeamRank

Resolves the retail TEAM_RANK / TIED_TEAM_RANK pair for active team players.
================
*/
static int G_RankGetTeamRank( const gclient_t *client, qboolean *tied ) {
	if ( tied ) {
		*tied = qfalse;
	}

	if ( !client ) {
		return -1;
	}
	if ( !G_RankUsesTeamResultFields() ) {
		return -1;
	}
	if ( client->sess.sessionTeam != TEAM_RED && client->sess.sessionTeam != TEAM_BLUE ) {
		return -1;
	}

	if ( level.teamScores[TEAM_RED] == level.teamScores[TEAM_BLUE] ) {
		if ( tied ) {
			*tied = qtrue;
		}
		return 1;
	}

	if ( client->sess.sessionTeam == TEAM_RED ) {
		return ( level.teamScores[TEAM_RED] > level.teamScores[TEAM_BLUE] ) ? 1 : 2;
	}

	return ( level.teamScores[TEAM_BLUE] > level.teamScores[TEAM_RED] ) ? 1 : 2;
}

/*
================
G_RankResolveMatchOutcome

Reconstructs the retail non-aborted outcome tri-state published as QUIT, WIN,
and LOSE.
================
*/
static void G_RankResolveMatchOutcome( const gentity_t *ent, int rank, int *won, int *lost ) {
	team_t team;
	team_t otherTeam;
	int teamScore;
	int otherTeamScore;

	if ( won ) {
		*won = 0;
	}
	if ( lost ) {
		*lost = 0;
	}

	if ( !ent || !ent->client || !won || !lost ) {
		return;
	}

	if ( G_RankUsesTeamResultFields() ) {
		team = ent->client->sess.sessionTeam;
		if ( team != TEAM_RED && team != TEAM_BLUE ) {
			*lost = 1;
			return;
		}

		otherTeam = ( team == TEAM_RED ) ? TEAM_BLUE : TEAM_RED;
		teamScore = level.teamScores[team];
		otherTeamScore = level.teamScores[otherTeam];

		if ( teamScore != -999 ) {
			if ( teamScore > otherTeamScore ) {
				*won = 1;
				return;
			}

			if ( TeamCount( -1, otherTeam ) <= 0 ) {
				*won = 1;
				return;
			}
		}

		*lost = 1;
		return;
	}

	if ( ent->client->ps.persistant[PERS_SCORE] == -999 || rank < 1 || ( rank > 1 && !level.matchForfeited ) ) {
		*lost = 1;
		return;
	}

	*won = 1;
}

/*
================
G_RankGetPickupCount

Returns one mirrored retail pickup bucket, defaulting safely when state is
missing or the requested slot is outside the recovered range.
================
*/
static int G_RankGetPickupCount( const gclient_t *client, rankPickupStat_t pickupStat ) {
	if ( !client ) {
		return 0;
	}
	if ( pickupStat < 0 || pickupStat >= RANK_PICKUP_COUNT ) {
		return 0;
	}

	return client->pers.rankPickupCounts[pickupStat];
}

/*
================
G_RankGetItemTimingAverageSeconds

Converts the mirrored pickup interval telemetry into the integer second values
written by the retail ITEM_TIMING object.
================
*/
static int G_RankGetItemTimingAverageSeconds( const gclient_t *client, scorestatPickupIndex_t pickupIndex ) {
	int intervalCount;
	int totalIntervalMs;

	if ( !client ) {
		return 0;
	}
	if ( pickupIndex < 0 || pickupIndex >= SCORESTAT_PICKUP_COUNT ) {
		return 0;
	}

	intervalCount = client->pers.pickupIntervalCount[pickupIndex];
	totalIntervalMs = client->pers.pickupIntervalTotalMs[pickupIndex];
	if ( intervalCount <= 0 || totalIntervalMs <= 0 ) {
		return 0;
	}

	return ( totalIntervalMs / intervalCount ) / 1000;
}

/*
================
G_RankBuildMedalsObject

Serializes the medal counters carried in the replicated playerstate.
================
*/
static qboolean G_RankBuildMedalsObject( const gclient_t *client, char *buffer, size_t bufferSize ) {
	size_t length;
	qboolean firstField;

	if ( !client || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	length = 0;
	firstField = qtrue;

	if ( !G_RankAppendPayload( buffer, bufferSize, &length, "{" ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "IMPRESSIVE",
		G_RankGetMedalTotal( client, RANK_MEDAL_IMPRESSIVE ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "EXCELLENT",
		G_RankGetMedalTotal( client, RANK_MEDAL_EXCELLENT ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "HUMILIATION",
		G_RankGetMedalTotal( client, RANK_MEDAL_HUMILIATION ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "REVENGE",
		G_RankGetMedalTotal( client, RANK_MEDAL_REVENGE ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "COMBOKILL",
		G_RankGetMedalTotal( client, RANK_MEDAL_COMBOKILL ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "RAMPAGE",
		G_RankGetMedalTotal( client, RANK_MEDAL_RAMPAGE ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "MIDAIR",
		G_RankGetMedalTotal( client, RANK_MEDAL_MIDAIR ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "PERFORATED",
		G_RankGetMedalTotal( client, RANK_MEDAL_PERFORATED ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "HEADSHOT",
		G_RankGetMedalTotal( client, RANK_MEDAL_HEADSHOT ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "ACCURACY",
		G_RankGetMedalTotal( client, RANK_MEDAL_ACCURACY ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "QUADGOD",
		G_RankGetMedalTotal( client, RANK_MEDAL_QUADGOD ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "FIRSTFRAG",
		G_RankGetMedalTotal( client, RANK_MEDAL_FIRSTFRAG ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "PERFECT",
		G_RankGetMedalTotal( client, RANK_MEDAL_PERFECT ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "DEFENDS",
		G_RankGetMedalTotal( client, RANK_MEDAL_DEFENDS ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "ASSISTS",
		G_RankGetMedalTotal( client, RANK_MEDAL_ASSISTS ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "CAPTURES",
		G_RankGetMedalTotal( client, RANK_MEDAL_CAPTURES ) ) ) {
		return qfalse;
	}

	return G_RankAppendPayload( buffer, bufferSize, &length, "}" );
}

/*
================
G_RankBuildPickupsObject

Serializes the tracked pickup counters already mirrored for ownerdraw and rich
scoreboard output.
================
*/
static qboolean G_RankBuildPickupsObject( const gclient_t *client, char *buffer, size_t bufferSize ) {
	size_t length;
	qboolean firstField;

	if ( !client || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	length = 0;
	firstField = qtrue;

	if ( !G_RankAppendPayload( buffer, bufferSize, &length, "{" ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "QUAD",
		G_RankGetPickupCount( client, RANK_PICKUP_QUAD ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "BATTLESUIT",
		G_RankGetPickupCount( client, RANK_PICKUP_BATTLESUIT ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "HASTE",
		G_RankGetPickupCount( client, RANK_PICKUP_HASTE ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "INVIS",
		G_RankGetPickupCount( client, RANK_PICKUP_INVIS ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "REGEN",
		G_RankGetPickupCount( client, RANK_PICKUP_REGEN ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "FLIGHT",
		G_RankGetPickupCount( client, RANK_PICKUP_FLIGHT ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "INVULNERABILITY",
		G_RankGetPickupCount( client, RANK_PICKUP_INVULNERABILITY ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "SCOUT",
		G_RankGetPickupCount( client, RANK_PICKUP_SCOUT ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "GUARD",
		G_RankGetPickupCount( client, RANK_PICKUP_GUARD ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "DOUBLER",
		G_RankGetPickupCount( client, RANK_PICKUP_DOUBLER ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "ARMOR_REGEN",
		G_RankGetPickupCount( client, RANK_PICKUP_ARMOR_REGEN ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "OTHER_POWERUP",
		G_RankGetPickupCount( client, RANK_PICKUP_OTHER_POWERUP ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "TELEPORTER",
		G_RankGetPickupCount( client, RANK_PICKUP_TELEPORTER ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "MEDKIT",
		G_RankGetPickupCount( client, RANK_PICKUP_MEDKIT ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "KAMIKAZE",
		G_RankGetPickupCount( client, RANK_PICKUP_KAMIKAZE ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "PORTAL",
		G_RankGetPickupCount( client, RANK_PICKUP_PORTAL ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "OTHER_HOLDABLE",
		G_RankGetPickupCount( client, RANK_PICKUP_OTHER_HOLDABLE ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "MEGA_HEALTH",
		G_RankGetPickupCount( client, RANK_PICKUP_MEGA_HEALTH ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "RED_ARMOR",
		G_RankGetPickupCount( client, RANK_PICKUP_RED_ARMOR ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "GREEN_ARMOR",
		G_RankGetPickupCount( client, RANK_PICKUP_GREEN_ARMOR ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "YELLOW_ARMOR",
		G_RankGetPickupCount( client, RANK_PICKUP_YELLOW_ARMOR ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "HEALTH",
		G_RankGetPickupCount( client, RANK_PICKUP_HEALTH ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "ARMOR",
		G_RankGetPickupCount( client, RANK_PICKUP_ARMOR ) ) ) {
		return qfalse;
	}

	return G_RankAppendPayload( buffer, bufferSize, &length, "}" );
}

/*
================
G_RankBuildItemTimingObject

Builds the retail ITEM_TIMING object from the already mirrored placement-pickup
interval telemetry.
================
*/
static qboolean G_RankBuildItemTimingObject( const gclient_t *client, char *buffer, size_t bufferSize ) {
	size_t length;
	qboolean firstField;
	int averageSeconds;

	if ( !client || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	length = 0;
	firstField = qtrue;

	if ( !G_RankAppendPayload( buffer, bufferSize, &length, "{" ) ) {
		return qfalse;
	}

	averageSeconds = G_RankGetItemTimingAverageSeconds( client, SCORESTAT_PICKUP_MH );
	if ( averageSeconds > 0 &&
		!G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "MEGA_HEALTH", averageSeconds ) ) {
		return qfalse;
	}

	averageSeconds = G_RankGetItemTimingAverageSeconds( client, SCORESTAT_PICKUP_RA );
	if ( averageSeconds > 0 &&
		!G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "RED_ARMOR", averageSeconds ) ) {
		return qfalse;
	}

	averageSeconds = G_RankGetItemTimingAverageSeconds( client, SCORESTAT_PICKUP_YA );
	if ( averageSeconds > 0 &&
		!G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "YELLOW_ARMOR", averageSeconds ) ) {
		return qfalse;
	}

	averageSeconds = G_RankGetItemTimingAverageSeconds( client, SCORESTAT_PICKUP_GA );
	if ( averageSeconds > 0 &&
		!G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "GREEN_ARMOR", averageSeconds ) ) {
		return qfalse;
	}

	return G_RankAppendPayload( buffer, bufferSize, &length, "}" );
}

/*
================
G_RankBuildDamageObject

Serializes the recovered nested DAMAGE slab used by retail PLAYER_STATS.
================
*/
static qboolean G_RankBuildDamageObject( const gclient_t *client, char *buffer, size_t bufferSize ) {
	size_t length;
	qboolean firstField;

	if ( !client || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	length = 0;
	firstField = qtrue;

	if ( !G_RankAppendPayload( buffer, bufferSize, &length, "{" ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "DEALT",
		client->pers.damageGiven ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "TAKEN",
		client->pers.damageReceived ) ) {
		return qfalse;
	}

	return G_RankAppendPayload( buffer, bufferSize, &length, "}" );
}

/*
================
G_RankBuildWeaponsObject

Serializes the tracked per-weapon frag, damage, and accuracy slabs.
================
*/
static qboolean G_RankBuildWeaponsObject( const gclient_t *client, char *buffer, size_t bufferSize ) {
	size_t length;
	qboolean firstField;
	weapon_t weapon;

	if ( !client || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	length = 0;
	firstField = qtrue;

	if ( !G_RankAppendPayload( buffer, bufferSize, &length, "{" ) ) {
		return qfalse;
	}

	for ( weapon = WP_GAUNTLET; weapon < WP_NUM_WEAPONS; weapon++ ) {
		char weaponPayload[256];
		size_t weaponLength;
		qboolean firstWeaponField;
		const char *weaponName;
		int shots;
		int hits;
		int accuracy;

		weaponName = G_RankWeaponName( weapon );
		shots = client->pers.accuracy_shots[weapon];
		hits = client->pers.accuracy_hits[weapon];
		accuracy = ( shots > 0 ) ? ( hits * 100 / shots ) : 0;

		weaponPayload[0] = '\0';
		weaponLength = 0;
		firstWeaponField = qtrue;

		if ( !G_RankAppendPayload( weaponPayload, sizeof( weaponPayload ), &weaponLength, "{" ) ) {
			return qfalse;
		}
		if ( !G_RankAppendJsonIntField( weaponPayload, sizeof( weaponPayload ), &weaponLength, &firstWeaponField,
			"FRAGS", client->pers.weaponFrags[weapon] ) ) {
			return qfalse;
		}
		if ( !G_RankAppendJsonIntField( weaponPayload, sizeof( weaponPayload ), &weaponLength, &firstWeaponField,
			"DAMAGE", client->pers.weaponDamage[weapon] ) ) {
			return qfalse;
		}
		if ( !G_RankAppendJsonIntField( weaponPayload, sizeof( weaponPayload ), &weaponLength, &firstWeaponField,
			"TIME", client->rankStats.weaponTimeMs[weapon] / 1000 ) ) {
			return qfalse;
		}
		if ( !G_RankAppendJsonIntField( weaponPayload, sizeof( weaponPayload ), &weaponLength, &firstWeaponField,
			"HITS", hits ) ) {
			return qfalse;
		}
		if ( !G_RankAppendJsonIntField( weaponPayload, sizeof( weaponPayload ), &weaponLength, &firstWeaponField,
			"SHOTS", shots ) ) {
			return qfalse;
		}
		if ( !G_RankAppendJsonIntField( weaponPayload, sizeof( weaponPayload ), &weaponLength, &firstWeaponField,
			"ACCURACY", accuracy ) ) {
			return qfalse;
		}
		if ( !G_RankAppendPayload( weaponPayload, sizeof( weaponPayload ), &weaponLength, "}" ) ) {
			return qfalse;
		}
		if ( !G_RankAppendJsonRawField( buffer, bufferSize, &length, &firstField, weaponName, weaponPayload ) ) {
			return qfalse;
		}
	}

	return G_RankAppendPayload( buffer, bufferSize, &length, "}" );
}

/*
================
G_RankBuildPlayerPowerupsArray

Builds the retail POWERUPS array used by the PLAYER_KILL and PLAYER_DEATH
per-player payload objects.
================
*/
static qboolean G_RankBuildPlayerPowerupsArray( const playerState_t *ps, char *buffer, size_t bufferSize ) {
	size_t length;
	qboolean firstPowerup;
	int powerup;

	if ( !ps || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	length = 0;
	firstPowerup = qtrue;

	if ( !G_RankAppendPayload( buffer, bufferSize, &length, "[" ) ) {
		return qfalse;
	}

	for ( powerup = RANK_POWERUPS_FIRST_RETAIL; powerup < RANK_POWERUPS_LAST_RETAIL; powerup++ ) {
		if ( ps->powerups[powerup] == 0 ) {
			continue;
		}
		if ( !firstPowerup && !G_RankAppendPayload( buffer, bufferSize, &length, "," ) ) {
			return qfalse;
		}
		firstPowerup = qfalse;
		if ( !G_RankAppendPayload( buffer, bufferSize, &length, "%i", powerup ) ) {
			return qfalse;
		}
	}

	return G_RankAppendPayload( buffer, bufferSize, &length, "]" );
}

/*
================
G_RankBuildPlayerSummaryObject

Builds the reduced per-player object reused by the PLAYER_KILL and PLAYER_DEATH
payloads.
================
*/
static qboolean G_RankBuildPlayerSummaryObject( const gentity_t *ent, char *buffer, size_t bufferSize ) {
	char steamId[32];
	char positionPayload[128];
	char powerupsPayload[128];
	size_t length;
	qboolean firstField;
	vec3_t planarVelocity;
	float speed;

	if ( !ent || !ent->client || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	VectorCopy( ent->client->ps.velocity, planarVelocity );
	planarVelocity[2] = 0.0f;
	speed = VectorLength( planarVelocity );

	if ( !G_RankBuildVectorObject( ent->r.currentOrigin, positionPayload, sizeof( positionPayload ) ) ) {
		return qfalse;
	}
	if ( !G_RankBuildPlayerPowerupsArray( &ent->client->ps, powerupsPayload, sizeof( powerupsPayload ) ) ) {
		return qfalse;
	}

	buffer[0] = '\0';
	length = 0;
	firstField = qtrue;
	G_RankFormatSteamId( ent, steamId, sizeof( steamId ) );

	if ( !G_RankAppendPayload( buffer, bufferSize, &length, "{" ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonStringField( buffer, bufferSize, &length, &firstField, "NAME",
		ent->client->pers.netname ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonStringField( buffer, bufferSize, &length, &firstField, "STEAM_ID", steamId ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "TEAM",
		ent->client->sess.sessionTeam ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "SCORE",
		ent->client->ps.persistant[PERS_SCORE] ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "HEALTH",
		ent->health ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "ARMOR",
		ent->client->ps.stats[STAT_ARMOR] ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonBoolField( buffer, bufferSize, &length, &firstField, "SUBMERGED",
		( ent->waterlevel > 1 ) ? qtrue : qfalse ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonFloatField( buffer, bufferSize, &length, &firstField, "SPEED", speed ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonRawField( buffer, bufferSize, &length, &firstField, "POSITION", positionPayload ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonRawField( buffer, bufferSize, &length, &firstField, "POWERUPS", powerupsPayload ) ) {
		return qfalse;
	}

	return G_RankAppendPayload( buffer, bufferSize, &length, "}" );
}

/*
================
G_RankBuildPlayerStatsPayload

Builds the source-side PLAYER_STATS JSON proxy using the field names recovered
from the retail qagame rankings publisher.
================
*/
static qboolean G_RankBuildPlayerStatsPayload( gentity_t *ent, qboolean aborted,
	char *buffer, size_t bufferSize ) {
	char steamId[32];
	char model[MAX_QPATH];
	char medalsPayload[256];
	char pickupsPayload[768];
	char itemTimingPayload[128];
	char damagePayload[128];
	char weaponsPayload[4096];
	size_t length;
	qboolean firstField;
	int playTime;
	int accuracy;
	int rank;
	int teamRank;
	int teamJoinTime;
	int quitMatch;
	int matchWon;
	int matchLost;
	qboolean isBot;
	qboolean tiedRank;
	qboolean tiedTeamRank;
	float botSkill;
	char userinfo[MAX_INFO_STRING];
	const char *skillValue;

	if ( !ent || !ent->client || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	if ( ent->client->pers.connected != CON_CONNECTED ) {
		return qfalse;
	}

	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		return qfalse;
	}

	G_RankAccumulateWeaponTime( ent );

	if ( !G_RankBuildMedalsObject( ent->client, medalsPayload, sizeof( medalsPayload ) ) ) {
		Q_strncpyz( medalsPayload, "{}", sizeof( medalsPayload ) );
	}
	if ( !G_RankBuildPickupsObject( ent->client, pickupsPayload, sizeof( pickupsPayload ) ) ) {
		Q_strncpyz( pickupsPayload, "{}", sizeof( pickupsPayload ) );
	}
	if ( !G_RankBuildItemTimingObject( ent->client, itemTimingPayload, sizeof( itemTimingPayload ) ) ) {
		Q_strncpyz( itemTimingPayload, "{}", sizeof( itemTimingPayload ) );
	}
	if ( !G_RankBuildDamageObject( ent->client, damagePayload, sizeof( damagePayload ) ) ) {
		Q_strncpyz( damagePayload, "{}", sizeof( damagePayload ) );
	}
	if ( !G_RankBuildWeaponsObject( ent->client, weaponsPayload, sizeof( weaponsPayload ) ) ) {
		Q_strncpyz( weaponsPayload, "{}", sizeof( weaponsPayload ) );
	}

	G_RankFormatSteamId( ent, steamId, sizeof( steamId ) );
	G_RankGetClientModel( ent, model, sizeof( model ) );

	playTime = ent->client->rankStats.totalActiveTimeMs / 1000;
	if ( playTime <= 0 ) {
		playTime = ( ent->client->rankStats.sessionStartTime > 0 )
			? ( level.time - ent->client->rankStats.sessionStartTime ) / 1000
			: ( level.time - level.startTime ) / 1000;
	}
	if ( playTime < 0 ) {
		playTime = 0;
	}

	accuracy = ( ent->client->accuracy_shots > 0 )
		? ( ent->client->accuracy_hits * 100 / ent->client->accuracy_shots )
		: 0;
	isBot = ( ent->r.svFlags & SVF_BOT ) ? qtrue : qfalse;
	botSkill = 0.0f;
	if ( isBot ) {
		trap_GetUserinfo( ent->s.number, userinfo, sizeof( userinfo ) );
		skillValue = Info_ValueForKey( userinfo, "skill" );
		if ( skillValue && skillValue[0] ) {
			botSkill = (float)atof( skillValue );
		}
	}
	teamRank = -1;
	tiedRank = qfalse;
	tiedTeamRank = qfalse;
	quitMatch = 0;
	matchWon = 0;
	matchLost = 0;
	if ( aborted ) {
		rank = -1;
		tiedRank = qtrue;
		teamRank = -1;
		tiedTeamRank = qtrue;
		quitMatch = 1;
	} else {
		rank = G_RankGetPlayerRank( ent->client, &tiedRank );
		teamRank = G_RankGetTeamRank( ent->client, &tiedTeamRank );
		G_RankResolveMatchOutcome( ent, rank, &matchWon, &matchLost );
	}
	teamJoinTime = 0;
	if ( ent->client->pers.teamJoinStartTime > 0 && level.time > ent->client->pers.teamJoinStartTime ) {
		teamJoinTime = ( level.time - ent->client->pers.teamJoinStartTime ) / 1000;
	}

	buffer[0] = '\0';
	length = 0;
	firstField = qtrue;

	if ( !G_RankAppendPayload( buffer, bufferSize, &length, "{" ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "TIME",
		( level.time - level.startTime ) / 1000 ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonBoolField( buffer, bufferSize, &length, &firstField, "WARMUP",
		( level.warmupTime != 0 ) ? qtrue : qfalse ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonBoolField( buffer, bufferSize, &length, &firstField, "ABORTED", aborted ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonStringField( buffer, bufferSize, &length, &firstField, "MATCH_GUID",
		level.rankMatchGuid ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonStringField( buffer, bufferSize, &length, &firstField, "NAME",
		ent->client->pers.netname ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonStringField( buffer, bufferSize, &length, &firstField, "STEAM_ID",
		steamId ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "TEAM",
		ent->client->sess.sessionTeam ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonStringField( buffer, bufferSize, &length, &firstField, "MODEL",
		model ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "PLAY_TIME",
		playTime ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "SCORE",
		ent->client->ps.persistant[PERS_SCORE] ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "KILLS",
		ent->client->killCount ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "DEATHS",
		ent->client->deathCount ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "ACCURACY",
		accuracy ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonRawField( buffer, bufferSize, &length, &firstField, "DAMAGE",
		damagePayload ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "WEAPONS_USED",
		(int)G_RankBuildWeaponsUsedMask( ent->client ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "MAX_STREAK",
		ent->client->pers.maxKillStreak ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonFloatField( buffer, bufferSize, &length, &firstField, "BOT_SKILL",
		botSkill ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonRawField( buffer, bufferSize, &length, &firstField, "MEDALS",
		medalsPayload ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonRawField( buffer, bufferSize, &length, &firstField, "PICKUPS",
		pickupsPayload ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonRawField( buffer, bufferSize, &length, &firstField, "ITEM_TIMING",
		itemTimingPayload ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonRawField( buffer, bufferSize, &length, &firstField, "WEAPONS",
		weaponsPayload ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "HOLY_SHITS",
		ent->client->pers.holyShitCount ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "TEAM_JOIN_TIME",
		teamJoinTime ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "RED_FLAG_PICKUPS",
		G_RankGetPickupCount( ent->client, RANK_PICKUP_RED_FLAG ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "BLUE_FLAG_PICKUPS",
		G_RankGetPickupCount( ent->client, RANK_PICKUP_BLUE_FLAG ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "NEUTRAL_FLAG_PICKUPS",
		G_RankGetPickupCount( ent->client, RANK_PICKUP_NEUTRAL_FLAG ) ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "RANK", rank ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonBoolField( buffer, bufferSize, &length, &firstField, "TIED_RANK",
		tiedRank ) ) {
		return qfalse;
	}
	if ( G_RankUsesTeamResultFields() ) {
		if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "TEAM_RANK",
			teamRank ) ) {
			return qfalse;
		}
		if ( !G_RankAppendJsonBoolField( buffer, bufferSize, &length, &firstField, "TIED_TEAM_RANK",
			tiedTeamRank ) ) {
			return qfalse;
		}
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "QUIT", quitMatch ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "WIN", matchWon ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "LOSE", matchLost ) ) {
		return qfalse;
	}

	return G_RankAppendPayload( buffer, bufferSize, &length, "}" );
}

/*
================
G_RankResolveScorerName

Resolves one cached scoring client slot into the printable name string used by
the match-report proxy.
================
*/
static void G_RankResolveScorerName( int clientNum, char *buffer, size_t bufferSize ) {
	char cleanedName[40];

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( clientNum < 0 || clientNum >= level.maxclients ) {
		return;
	}
	if ( level.clients[clientNum].pers.connected == CON_DISCONNECTED ) {
		return;
	}

	G_CleanClientNameFromClientNum( clientNum, cleanedName );
	Q_strncpyz( buffer, cleanedName, bufferSize );
}

/*
================
G_RankBuildMatchReportPayload

Reconstructs the recovered high-signal match-report fields into the writable
JSON proxy format used by the native import bridge.
================
*/
static qboolean G_RankBuildMatchReportPayload( qboolean aborted, char *buffer, size_t bufferSize ) {
	char hostname[MAX_CVAR_VALUE_STRING];
	char lastScorer[40];
	char lastTeamScorer[40];
	size_t length;
	qboolean firstField;

	if ( !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	trap_Cvar_VariableStringBuffer( "sv_hostname", hostname, sizeof( hostname ) );
	G_RankResolveScorerName( level.rankLastScorer, lastScorer, sizeof( lastScorer ) );
	G_RankResolveScorerName( level.rankLastTeamScorer, lastTeamScorer, sizeof( lastTeamScorer ) );

	buffer[0] = '\0';
	length = 0;
	firstField = qtrue;

	if ( !G_RankAppendPayload( buffer, bufferSize, &length, "{" ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "TIME",
		( level.time - level.startTime ) / 1000 ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonBoolField( buffer, bufferSize, &length, &firstField, "WARMUP",
		( level.warmupTime != 0 ) ? qtrue : qfalse ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonBoolField( buffer, bufferSize, &length, &firstField, "ABORTED", aborted ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonStringField( buffer, bufferSize, &length, &firstField, "EXIT_MSG",
		level.rankExitMessage ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonStringField( buffer, bufferSize, &length, &firstField, "MATCH_GUID",
		level.rankMatchGuid ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonStringField( buffer, bufferSize, &length, &firstField, "SERVER_TITLE",
		hostname ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonStringField( buffer, bufferSize, &length, &firstField, "LAST_SCORER",
		lastScorer ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonStringField( buffer, bufferSize, &length, &firstField, "LAST_TEAMSCORER",
		lastTeamScorer ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "GAMETYPE",
		g_gametype.integer ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "TIMELIMIT",
		g_timelimit.integer ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "FRAGLIMIT",
		g_fraglimit.integer ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonBoolField( buffer, bufferSize, &length, &firstField, "TRAINING",
		level.trainingMapActive ? qtrue : qfalse ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "PRACTICEFLAGS",
		practiceflags.integer ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonBoolField( buffer, bufferSize, &length, &firstField, "INSTAGIB",
		g_instaGib.integer ? qtrue : qfalse ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "NUM_PLAYERS",
		level.numPlayingClients ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "RED_SCORE",
		level.teamScores[TEAM_RED] ) ) {
		return qfalse;
	}
	if ( !G_RankAppendJsonIntField( buffer, bufferSize, &length, &firstField, "BLUE_SCORE",
		level.teamScores[TEAM_BLUE] ) ) {
		return qfalse;
	}

	return G_RankAppendPayload( buffer, bufferSize, &length, "}" );
}

/*
================
G_RankResetClientStats

Reinitializes the lightweight source-side rankings/report bridge state. Retail
clears a substantially larger per-client slab here; the writable source still
carries the reduced proxy needed by the current event bridge.
================
*/
void G_RankResetClientStats( gclient_t *client ) {
	if ( !client ) {
		return;
	}

	memset( &client->rankStats, 0, sizeof( client->rankStats ) );
	client->rankStats.sessionStartTime = level.time;
	client->rankStats.matchStartTime = level.startTime;
	client->rankStats.lastUpdateTime = level.time;
	client->rankStats.steamIdLow = client->pers.steamIdLow;
	client->rankStats.steamIdHigh = client->pers.steamIdHigh;
	Com_sprintf( client->rankStats.sessionToken, sizeof( client->rankStats.sessionToken ),
		"%08X%08X%08X",
		client->rankStats.steamIdLow,
		client->rankStats.steamIdHigh,
		(unsigned int)( level.time ^ rand() ) );
}

/*
================
G_RankClientConnect

Mirrors the retail PLAYER_CONNECT publication timing. The native Json::Value
ABI is still unrecovered in writable source, so the bridge forwards a serialized
JSON-text proxy payload instead.
================
*/
void G_RankClientConnect( gentity_t *ent ) {
	gclient_t	*client;
	char		payload[RANK_EVENT_PAYLOAD_MAX];
	void		*payloadPtr;

	if ( !ent || !ent->client || ( ent->r.svFlags & SVF_BOT ) ) {
		return;
	}

	client = ent->client;
	payloadPtr = G_RankBuildClientEventPayload( ent, payload, sizeof( payload ) ) ? payload : NULL;
	trap_ReportPlayerEvent( client->pers.steamIdLow, client->pers.steamIdHigh,
		&client->rankStats, "PLAYER_CONNECT", payloadPtr );
}

/*
================
G_RankClientDisconnect

Mirrors the retail PLAYER_DISCONNECT publication timing before the client is
fully unlinked from the world, again using the source-side JSON payload proxy.
================
*/
void G_RankClientDisconnect( gentity_t *ent ) {
	gclient_t	*client;
	char		payload[RANK_EVENT_PAYLOAD_MAX];
	void		*payloadPtr;

	if ( !ent || !ent->client || ( ent->r.svFlags & SVF_BOT ) ) {
		return;
	}

	client = ent->client;
	G_RankAccumulateWeaponTime( ent );
	payloadPtr = G_RankBuildClientEventPayload( ent, payload, sizeof( payload ) ) ? payload : NULL;
	trap_ReportPlayerEvent( client->pers.steamIdLow, client->pers.steamIdHigh,
		&client->rankStats, "PLAYER_DISCONNECT", payloadPtr );
}

/*
================
G_RankAccumulateWeaponTime

Accumulates active weapon time into the reduced source-side rankings proxy.
================
*/
void G_RankAccumulateWeaponTime( gentity_t *ent ) {
	gclient_t *client;
	int delta;
	int weapon;

	if ( !ent || !ent->client ) {
		return;
	}

	client = ent->client;
	if ( client->rankStats.lastUpdateTime <= 0 ) {
		client->rankStats.lastUpdateTime = level.time;
		return;
	}

	delta = level.time - client->rankStats.lastUpdateTime;
	client->rankStats.lastUpdateTime = level.time;
	if ( delta <= 0 ) {
		return;
	}
	if ( client->pers.connected != CON_CONNECTED ) {
		return;
	}
	if ( client->sess.sessionTeam == TEAM_SPECTATOR || client->ps.pm_type != PM_NORMAL ) {
		return;
	}

	client->rankStats.totalActiveTimeMs += delta;
	weapon = client->ps.weapon;
	if ( weapon > WP_NONE && weapon < WP_NUM_WEAPONS ) {
		client->rankStats.weaponTimeMs[weapon] += delta;
	}
}

/*
================
G_RankAccumulateDamage

Accumulates the reduced damage buckets used by PLAYER_STATS.
================
*/
void G_RankAccumulateDamage( gentity_t *victim, gentity_t *attacker, int meansOfDeath, int damage ) {
	weapon_t weapon;

	if ( damage <= 0 ) {
		return;
	}

	if ( victim && victim->client ) {
		victim->client->pers.damageReceived += damage;
	}

	if ( !attacker || !attacker->client ) {
		return;
	}
	if ( attacker == victim ) {
		return;
	}
	if ( victim && victim->client && OnSameTeam( victim, attacker ) ) {
		return;
	}

	attacker->client->pers.damageGiven += damage;
	weapon = G_RankMeansOfDeathWeapon( meansOfDeath );
	if ( weapon > WP_NONE && weapon < WP_NUM_WEAPONS ) {
		attacker->client->pers.weaponDamage[weapon] += damage;
	}
}

/*
================
G_RankSendPlayerMedal

Publishes the recovered PLAYER_MEDAL event and tracks the source-side running
medal total used by later PLAYER_STATS snapshots.
================
*/
void G_RankSendPlayerMedal( gentity_t *ent, const char *medal ) {
	char		payload[RANK_EVENT_PAYLOAD_MAX];
	char		steamId[32];
	uint32_t	steamIdLow;
	uint32_t	steamIdHigh;
	size_t		length;
	qboolean	firstField;
	rankMedal_t	medalIndex;
	int		awardEventId;
	int		total;

	if ( !ent || !ent->client || !medal || !medal[0] ) {
		return;
	}

	medalIndex = G_RankResolveMedalIndex( medal );
	if ( medalIndex >= 0 && medalIndex < RANK_MEDAL_COUNT ) {
		ent->client->pers.rankMedalCounts[medalIndex]++;
	}
	total = G_RankGetMedalTotal( ent->client, medalIndex );
	awardEventId = G_RankResolveAwardEventId( medalIndex );
	if ( awardEventId >= 0 ) {
		G_AddAwardEntity( ent, awardEventId );
	}

	G_RankResolveEventSteamIds( ent, &steamIdLow, &steamIdHigh );
	G_RankFormatSteamId( ent, steamId, sizeof( steamId ) );

	payload[0] = '\0';
	length = 0;
	firstField = qtrue;

	if ( !G_RankAppendPayload( payload, sizeof( payload ), &length, "{" ) ) {
		return;
	}
	if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "TIME",
		( level.time - level.startTime ) / 1000 ) ) {
		return;
	}
	if ( !G_RankAppendJsonBoolField( payload, sizeof( payload ), &length, &firstField, "WARMUP",
		( level.warmupTime != 0 ) ? qtrue : qfalse ) ) {
		return;
	}
	if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "MATCH_GUID",
		level.rankMatchGuid ) ) {
		return;
	}
	if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "NAME",
		ent->client->pers.netname ) ) {
		return;
	}
	if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "STEAM_ID",
		steamId ) ) {
		return;
	}
	if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "MEDAL",
		medal ) ) {
		return;
	}
	if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "TOTAL",
		total ) ) {
		return;
	}
	if ( !G_RankAppendPayload( payload, sizeof( payload ), &length, "}" ) ) {
		return;
	}

	trap_ReportPlayerEvent( steamIdLow, steamIdHigh, &ent->client->rankStats, "PLAYER_MEDAL", payload );
}

/*
================
G_RankSendFlagStatus

Publishes the recovered FLAG_STATUS event whenever the server-side flag state
changes.
================
*/
void G_RankSendFlagStatus( gentity_t *ent, int team, int status ) {
	char		payload[RANK_EVENT_PAYLOAD_MAX];
	size_t		length;
	qboolean	firstField;
	uint32_t	steamIdLow;
	uint32_t	steamIdHigh;

	payload[0] = '\0';
	length = 0;
	firstField = qtrue;
	G_RankResolveEventSteamIds( ent, &steamIdLow, &steamIdHigh );

	if ( !G_RankAppendPayload( payload, sizeof( payload ), &length, "{" ) ) {
		return;
	}
	if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "TIME",
		( level.time - level.startTime ) / 1000 ) ) {
		return;
	}
	if ( !G_RankAppendJsonBoolField( payload, sizeof( payload ), &length, &firstField, "WARMUP",
		( level.warmupTime != 0 ) ? qtrue : qfalse ) ) {
		return;
	}
	if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "MATCH_GUID",
		level.rankMatchGuid ) ) {
		return;
	}
	if ( ent && ent->client ) {
		char steamId[32];

		G_RankFormatSteamId( ent, steamId, sizeof( steamId ) );
		if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "STEAM_ID",
			steamId ) ) {
			return;
		}
	}
	if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "TEAM",
		G_RankTeamName( team ) ) ) {
		return;
	}
	if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "STATUS",
		G_RankFlagStatusName( status ) ) ) {
		return;
	}
	if ( !G_RankAppendPayload( payload, sizeof( payload ), &length, "}" ) ) {
		return;
	}

	trap_ReportPlayerEvent( steamIdLow, steamIdHigh,
		( ent && ent->client ) ? &ent->client->rankStats : NULL, "FLAG_STATUS", payload );
}

/*
================
G_RankSendPlayerSwitchTeam

Publishes the recovered PLAYER_SWITCHTEAM event after the session team mutates.
================
*/
void G_RankSendPlayerSwitchTeam( gentity_t *ent, int oldTeam, int newTeam ) {
	char		payload[RANK_EVENT_PAYLOAD_MAX];
	uint32_t	steamIdLow;
	uint32_t	steamIdHigh;
	size_t		length;
	qboolean	firstField;

	if ( !ent || !ent->client ) {
		return;
	}

	G_RankResolveEventSteamIds( ent, &steamIdLow, &steamIdHigh );
	payload[0] = '\0';
	length = 0;
	firstField = qtrue;

	if ( !G_RankAppendPayload( payload, sizeof( payload ), &length, "{" ) ) {
		return;
	}
	if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "TIME",
		( level.time - level.startTime ) / 1000 ) ) {
		return;
	}
	if ( !G_RankAppendJsonBoolField( payload, sizeof( payload ), &length, &firstField, "WARMUP",
		( level.warmupTime != 0 ) ? qtrue : qfalse ) ) {
		return;
	}
	if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "MATCH_GUID",
		level.rankMatchGuid ) ) {
		return;
	}
	if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "NAME",
		ent->client->pers.netname ) ) {
		return;
	}
	if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "STEAM_ID",
		( ( ent->r.svFlags & SVF_BOT ) != 0 ) ? "0" : va( "%llu",
			( (unsigned long long)ent->client->pers.steamIdHigh << 32 ) | ent->client->pers.steamIdLow ) ) ) {
		return;
	}
	if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "OLD_TEAM",
		oldTeam ) ) {
		return;
	}
	if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "NEW_TEAM",
		newTeam ) ) {
		return;
	}
	if ( !G_RankAppendPayload( payload, sizeof( payload ), &length, "}" ) ) {
		return;
	}

	trap_ReportPlayerEvent( steamIdLow, steamIdHigh, &ent->client->rankStats, "PLAYER_SWITCHTEAM", payload );
}

/*
================
G_RankSendPlayerRaceComplete

Publishes the recovered PLAYER_RACECOMPLETE event once a run time is finalized.
================
*/
void G_RankSendPlayerRaceComplete( gentity_t *ent, int raceTime ) {
	char		payload[RANK_EVENT_PAYLOAD_MAX];
	uint32_t	steamIdLow;
	uint32_t	steamIdHigh;
	size_t		length;
	qboolean	firstField;

	if ( !ent || !ent->client ) {
		return;
	}

	G_RankResolveEventSteamIds( ent, &steamIdLow, &steamIdHigh );
	payload[0] = '\0';
	length = 0;
	firstField = qtrue;

	if ( !G_RankAppendPayload( payload, sizeof( payload ), &length, "{" ) ) {
		return;
	}
	if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "TIME",
		( level.time - level.startTime ) / 1000 ) ) {
		return;
	}
	if ( !G_RankAppendJsonBoolField( payload, sizeof( payload ), &length, &firstField, "WARMUP",
		( level.warmupTime != 0 ) ? qtrue : qfalse ) ) {
		return;
	}
	if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "MATCH_GUID",
		level.rankMatchGuid ) ) {
		return;
	}
	if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "NAME",
		ent->client->pers.netname ) ) {
		return;
	}
	if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "STEAM_ID",
		( ( ent->r.svFlags & SVF_BOT ) != 0 ) ? "0" : va( "%llu",
			( (unsigned long long)ent->client->pers.steamIdHigh << 32 ) | ent->client->pers.steamIdLow ) ) ) {
		return;
	}
	if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "RACE_TIME",
		raceTime ) ) {
		return;
	}
	if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "WEAPONS_USED",
		(int)G_RankBuildWeaponsUsedMask( ent->client ) ) ) {
		return;
	}
	if ( !G_RankAppendPayload( payload, sizeof( payload ), &length, "}" ) ) {
		return;
	}

	trap_ReportPlayerEvent( steamIdLow, steamIdHigh, &ent->client->rankStats, "PLAYER_RACECOMPLETE", payload );
}

/*
================
G_RankSendPlayerDeath

Publishes the shared PLAYER_KILL / PLAYER_DEATH payload pair recovered from the
retail death path.
================
*/
void G_RankSendPlayerDeath( gentity_t *victim, gentity_t *killer, int meansOfDeath ) {
	char		payload[RANK_EVENT_PAYLOAD_MAX];
	char		killerPayload[512];
	char		victimPayload[512];
	size_t		length;
	qboolean	firstField;
	uint32_t	killerSteamIdLow;
	uint32_t	killerSteamIdHigh;
	uint32_t	victimSteamIdLow;
	uint32_t	victimSteamIdHigh;
	weapon_t	weapon;
	int		aliveCounts[TEAM_NUM_TEAMS];
	int		deadCounts[TEAM_NUM_TEAMS];
	const char	*weaponName;
	qboolean	teamkill;
	qboolean	suicide;
	qboolean	airborne;

	if ( !victim || !victim->client ) {
		return;
	}

	if ( !G_RankBuildPlayerSummaryObject( victim, victimPayload, sizeof( victimPayload ) ) ) {
		Q_strncpyz( victimPayload, "{}", sizeof( victimPayload ) );
	}
	if ( killer && killer->client && G_RankBuildPlayerSummaryObject( killer, killerPayload, sizeof( killerPayload ) ) ) {
		/* keep killerPayload as built */
	} else {
		Q_strncpyz( killerPayload, "{}", sizeof( killerPayload ) );
	}

	weapon = G_RankMeansOfDeathWeapon( meansOfDeath );
	weaponName = ( weapon > WP_NONE && weapon < WP_NUM_WEAPONS )
		? G_RankWeaponName( weapon )
		: G_RankMeansOfDeathName( meansOfDeath );
	teamkill = ( killer && killer->client && killer != victim
		&& G_ClientsOnSameTeam( killer->client, victim->client ) ) ? qtrue : qfalse;
	suicide = ( !killer || killer == victim || !killer->client ) ? qtrue : qfalse;
	airborne = ( killer && killer->client && killer->client->ps.groundEntityNum == ENTITYNUM_NONE ) ? qtrue : qfalse;
	memset( aliveCounts, 0, sizeof( aliveCounts ) );
	memset( deadCounts, 0, sizeof( deadCounts ) );
	if ( G_RankGametypePublishesRound() ) {
		G_RankCountAliveDeadByTeam( deadCounts, aliveCounts );
	}

	payload[0] = '\0';
	length = 0;
	firstField = qtrue;

	if ( !G_RankAppendPayload( payload, sizeof( payload ), &length, "{" ) ) {
		return;
	}
	if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "TIME",
		( level.time - level.startTime ) / 1000 ) ) {
		return;
	}
	if ( !G_RankAppendJsonBoolField( payload, sizeof( payload ), &length, &firstField, "WARMUP",
		( level.warmupTime != 0 ) ? qtrue : qfalse ) ) {
		return;
	}
	if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "MATCH_GUID",
		level.rankMatchGuid ) ) {
		return;
	}
	if ( !G_RankAppendJsonBoolField( payload, sizeof( payload ), &length, &firstField, "TEAMKILL",
		teamkill ) ) {
		return;
	}
	if ( !G_RankAppendJsonBoolField( payload, sizeof( payload ), &length, &firstField, "SUICIDE",
		suicide ) ) {
		return;
	}
	if ( !G_RankAppendJsonStringField( payload, sizeof( payload ), &length, &firstField, "MOD",
		weaponName ) ) {
		return;
	}
	if ( !G_RankAppendJsonBoolField( payload, sizeof( payload ), &length, &firstField, "AIRBORNE",
		airborne ) ) {
		return;
	}
	if ( G_RankGametypePublishesRound() ) {
		team_t victimTeam;
		team_t otherTeam;

		victimTeam = victim->client->sess.sessionTeam;
		otherTeam = TEAM_FREE;
		if ( victimTeam == TEAM_RED ) {
			otherTeam = TEAM_BLUE;
		} else if ( victimTeam == TEAM_BLUE ) {
			otherTeam = TEAM_RED;
		}

		if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "ROUND",
			level.roundNumber ) ) {
			return;
		}
		if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "TEAM_ALIVE",
			( victimTeam >= TEAM_FREE && victimTeam < TEAM_NUM_TEAMS ) ? aliveCounts[victimTeam] : 0 ) ) {
			return;
		}
		if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "TEAM_DEAD",
			( victimTeam >= TEAM_FREE && victimTeam < TEAM_NUM_TEAMS ) ? deadCounts[victimTeam] : 0 ) ) {
			return;
		}
		if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "OTHER_TEAM_ALIVE",
			( otherTeam >= TEAM_FREE && otherTeam < TEAM_NUM_TEAMS ) ? aliveCounts[otherTeam] : 0 ) ) {
			return;
		}
		if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "OTHER_TEAM_DEAD",
			( otherTeam >= TEAM_FREE && otherTeam < TEAM_NUM_TEAMS ) ? deadCounts[otherTeam] : 0 ) ) {
			return;
		}
	}
	if ( !G_RankAppendJsonIntField( payload, sizeof( payload ), &length, &firstField, "STREAK",
		( killer && killer->client ) ? killer->client->killCount : 0 ) ) {
		return;
	}
	if ( !G_RankAppendJsonRawField( payload, sizeof( payload ), &length, &firstField, "KILLER",
		killerPayload ) ) {
		return;
	}
	if ( !G_RankAppendJsonRawField( payload, sizeof( payload ), &length, &firstField, "VICTIM",
		victimPayload ) ) {
		return;
	}
	if ( !G_RankAppendPayload( payload, sizeof( payload ), &length, "}" ) ) {
		return;
	}

	G_RankResolveEventSteamIds( killer, &killerSteamIdLow, &killerSteamIdHigh );
	G_RankResolveEventSteamIds( victim, &victimSteamIdLow, &victimSteamIdHigh );

	if ( killer && killer->client && meansOfDeath == MOD_RAILGUN_HEADSHOT ) {
		G_RankSendPlayerMedal( killer, "HEADSHOT" );
	}

	if ( killer && killer->client ) {
		trap_ReportPlayerEvent( killerSteamIdLow, killerSteamIdHigh, &killer->client->rankStats,
			"PLAYER_KILL", payload );
	}

	trap_ReportPlayerEvent( victimSteamIdLow, victimSteamIdHigh, &victim->client->rankStats,
		"PLAYER_DEATH", payload );
}

/*
================
G_RankSendPlayerStats

Publishes the reconstructed PLAYER_STATS payload used at match end and during
team-switch teardown.
================
*/
void G_RankSendPlayerStats( gentity_t *ent, qboolean aborted ) {
	char		payload[RANK_EVENT_PAYLOAD_MAX];
	void		*payloadPtr;
	uint32_t	steamIdLow;
	uint32_t	steamIdHigh;

	if ( !ent || !ent->client ) {
		return;
	}

	G_RankResolveEventSteamIds( ent, &steamIdLow, &steamIdHigh );
	payloadPtr = G_RankBuildPlayerStatsPayload( ent, aborted, payload, sizeof( payload ) ) ? payload : NULL;
	if ( !payloadPtr ) {
		return;
	}

	trap_ReportPlayerEvent( steamIdLow, steamIdHigh, &ent->client->rankStats, "PLAYER_STATS", payloadPtr );
}

/*
================
G_RankSendMatchStarted

Publishes the retail MATCH_STARTED transition once per match bootstrap, using a
serialized roster payload proxy until the retail Json::Value ABI is recovered.
================
*/
void G_RankSendMatchStarted( void ) {
	char payload[RANK_EVENT_PAYLOAD_MAX];

	if ( level.rankMatchStartedSent ) {
		return;
	}

	level.rankMatchStartedSent = qtrue;
	trap_ReportPlayerEvent( 0, 0, NULL, "MATCH_STARTED",
		G_RankBuildMatchStartedPayload( payload, sizeof( payload ) ) ? payload : NULL );
}

/*
================
G_RankSubmitMatchReport

Submits the reconstructed match-report payload once after LogExit finishes the
per-player stats pass.
================
*/
void G_RankSubmitMatchReport( qboolean aborted ) {
	char	payload[RANK_EVENT_PAYLOAD_MAX];
	void	*payloadPtr;

	if ( level.rankMatchReportSent ) {
		return;
	}

	level.rankMatchReportSent = qtrue;
	payloadPtr = G_RankBuildMatchReportPayload( aborted, payload, sizeof( payload ) ) ? payload : NULL;
	trap_SubmitMatchReport( payloadPtr );
}

/*
================
LogExit

Append information about this game to the log file
================
*/
void LogExit( const char *string ) {
	int				i, numSorted;
	gclient_t		*cl;
	gentity_t		*te;
	const char		*exitMessage;
	team_t			winningTeam;
	qboolean		teamMatchEnd;
	qboolean won = qtrue;

	exitMessage = string ? string : "";
	Q_strncpyz( level.rankExitMessage, exitMessage, sizeof( level.rankExitMessage ) );
	G_LogPrintf( "Exit: %s\n", exitMessage );

	level.intermissionQueued = level.time;

	// don't send more than 32 scores (FIXME?)
	numSorted = level.numConnectedClients;
	if ( numSorted > 32 ) {
		numSorted = 32;
	}

	teamMatchEnd = ( g_gametype.integer > GT_SINGLE_PLAYER && g_gametype.integer != GT_RED_ROVER );
	if ( teamMatchEnd ) {
		G_LogPrintf( "red:%i  blue:%i\n",
			level.teamScores[TEAM_RED], level.teamScores[TEAM_BLUE] );
	}

	for (i=0 ; i < numSorted ; i++) {
		int		ping;

		cl = &level.clients[level.sortedClients[i]];

		if ( cl->sess.sessionTeam == TEAM_SPECTATOR ) {
			continue;
		}
		if ( cl->pers.connected == CON_CONNECTING ) {
			continue;
		}

		ping = cl->ps.ping < 999 ? cl->ps.ping : 999;

		G_LogPrintf( "score: %i  ping: %i  client: %i %s\n", cl->ps.persistant[PERS_SCORE], ping, level.sortedClients[i],	cl->pers.netname );
		if (g_singlePlayer.integer && g_gametype.integer == GT_TOURNAMENT) {
			if (g_entities[cl - level.clients].r.svFlags & SVF_BOT && cl->ps.persistant[PERS_RANK] == 0) {
				won = qfalse;
			}
		}

	}

	if ( teamMatchEnd ) {
		winningTeam = ( level.teamScores[TEAM_RED] > level.teamScores[TEAM_BLUE] ) ? TEAM_RED : TEAM_BLUE;
		te = G_TempEntity( vec3_origin, EV_GLOBAL_TEAM_SOUND );
		te->r.svFlags |= SVF_BROADCAST;
		G_SetRetailGlobalTeamSoundPayload( te,
			( winningTeam == TEAM_RED ) ? GTS_REDTEAM_WINS : GTS_BLUETEAM_WINS,
			-1, winningTeam, 0 );
	} else {
		te = G_TempEntity( vec3_origin, EV_GAMEOVER );
		te->r.svFlags |= SVF_BROADCAST;
	}

	if (g_singlePlayer.integer) {
		if (g_gametype.integer >= GT_CTF) {
			won = level.teamScores[TEAM_RED] > level.teamScores[TEAM_BLUE];
		}
		trap_SendConsoleCommand( EXEC_APPEND, (won) ? "spWin\n" : "spLose\n" );
	}

	if ( !level.rankMatchReportSent && !trap_Cvar_VariableIntegerValue( "g_restarted" ) ) {
		for ( i = 0; i < level.maxclients; i++ ) {
			gentity_t *ent;

			ent = &g_entities[i];
			if ( !ent->client ) {
				continue;
			}
			if ( ent->client->pers.connected != CON_CONNECTED ) {
				continue;
			}
			if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
				continue;
			}

			G_RankSendPlayerStats( ent, qfalse );
		}

		G_RankSubmitMatchReport( qfalse );
	}


}

/*
=============
G_GetForfeitDuelLoser

Returns the duel-side client whose visible score should be marked as forfeited.
=============
*/
static gclient_t *G_GetForfeitDuelLoser( void ) {
	gclient_t	*first;
	gclient_t	*second;
	int			i;

	first = NULL;
	second = NULL;

	for ( i = 0; i < level.numConnectedClients && i < level.maxclients; i++ ) {
		int			clientNum;
		gclient_t	*client;

		clientNum = level.sortedClients[i];
		if ( clientNum < 0 || clientNum >= level.maxclients ) {
			continue;
		}

		client = &level.clients[clientNum];
		if ( client->pers.connected != CON_CONNECTED ) {
			continue;
		}

		if ( !first ) {
			first = client;
			continue;
		}

		second = client;
		break;
	}

	if ( !first || !second ) {
		return NULL;
	}

	if ( first->sess.sessionTeam != TEAM_FREE ) {
		return first;
	}

	if ( second->sess.sessionTeam != TEAM_FREE ) {
		return second;
	}

	return ( first->ps.persistant[PERS_SCORE] <= second->ps.persistant[PERS_SCORE] ) ? first : second;
}


/*
=============
G_ApplyForfeit

Ends the current match because a player or side forfeited.
=============
*/
void G_ApplyForfeit( void ) {
	team_t		losingTeam;
	gclient_t	*losingClient;
	int			redPlayerCount;
	int			bluePlayerCount;

	if ( level.matchForfeited ) {
		return;
	}

	level.matchForfeited = qtrue;
	losingTeam = TEAM_FREE;
	losingClient = NULL;

	if ( g_gametype.integer == GT_TOURNAMENT ) {
		losingClient = G_GetForfeitDuelLoser();
		if ( losingClient ) {
			losingClient->ps.persistant[PERS_SCORE] = -999;
		}
	} else if ( g_gametype.integer >= GT_TEAM ) {
		redPlayerCount = TeamCount( -1, TEAM_RED );
		bluePlayerCount = TeamCount( -1, TEAM_BLUE );

		if ( redPlayerCount < 1 && bluePlayerCount >= 1 ) {
			losingTeam = TEAM_RED;
		} else if ( bluePlayerCount < 1 && redPlayerCount >= 1 ) {
			losingTeam = TEAM_BLUE;
		} else if ( level.teamScores[TEAM_RED] < level.teamScores[TEAM_BLUE] ) {
			losingTeam = TEAM_RED;
		} else if ( level.teamScores[TEAM_BLUE] < level.teamScores[TEAM_RED] ) {
			losingTeam = TEAM_BLUE;
		}

		if ( losingTeam == TEAM_RED || losingTeam == TEAM_BLUE ) {
			level.teamScores[losingTeam] = -999;
			trap_SetConfigstring(
				( losingTeam == TEAM_RED ) ? CS_SCORES1 : CS_SCORES2,
				va( "%i", level.teamScores[losingTeam] ) );
		}
	}

	CalculateRanks();
	trap_SendServerCommand( -1, "print \"Game has been forfeited.\\n\"" );
	LogExit( "Players have forfeited." );
}

/*
=================
CheckIntermissionExit

Retail keeps the ready bitmask for scoreboard display, then waits a fixed
grace window before publishing the one-shot intermission-exit latch and
finally advancing to ExitLevel().
=================
*/
void CheckIntermissionExit( void ) {
	int			i;
	gclient_t	*cl;
	int			readyMask;
	int			intermissionDelay;
	char			nextmaps[MAX_STRING_CHARS];

	// see which players are ready
	readyMask = 0;
	for (i=0 ; i< g_maxclients.integer ; i++) {
		cl = level.clients + i;
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( g_entities[cl->ps.clientNum].r.svFlags & SVF_BOT ) {
			continue;
		}

		if ( cl->readyToExit ) {
			if ( i < 16 ) {
				readyMask |= 1 << i;
			}
		}
	}

	// copy the readyMask to each player's stats so
	// it can be displayed on the scoreboard
	for (i=0 ; i< g_maxclients.integer ; i++) {
		cl = level.clients + i;
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}
		cl->ps.stats[STAT_CLIENTS_READY] = readyMask;
	}

	intermissionDelay = 10000;
	trap_Cvar_VariableStringBuffer( "nextmaps", nextmaps, sizeof( nextmaps ) );
	if ( !g_singlePlayer.integer && nextmaps[0] ) {
		intermissionDelay = 20000;
	}

	if ( g_singlePlayer.integer ) {
		trap_SetConfigstring( CS_INTERMISSION_EXIT_STATUS, "1" );
		level.intermissionExitStatusLatched = qtrue;
	} else if ( !level.intermissionExitStatusLatched
		&& level.time > level.intermissiontime + intermissionDelay ) {
		trap_SetConfigstring( CS_INTERMISSION_EXIT_STATUS, "1" );
		level.intermissionExitStatusLatched = qtrue;
	}

	if ( level.time >= level.intermissiontime + intermissionDelay + 3000 ) {
		level.readyToExit = qtrue;
		level.exitTime = level.time;
		ExitLevel();
		return;
	}

	level.readyToExit = qfalse;
	level.exitTime = 0;
}

/*
=============
ScoreIsTied
=============
*/
qboolean ScoreIsTied( void ) {
	int		a, b;

	if ( level.numPlayingClients < 2 ) {
		return qfalse;
	}
	
	if ( g_gametype.integer < GT_FFA ||
		( g_gametype.integer > GT_SINGLE_PLAYER && g_gametype.integer != GT_RED_ROVER ) ) {
		return level.teamScores[TEAM_RED] == level.teamScores[TEAM_BLUE];
	}

	a = level.clients[level.sortedClients[0]].ps.persistant[PERS_SCORE];
	b = level.clients[level.sortedClients[1]].ps.persistant[PERS_SCORE];

	return a == b;
}

/*
=================
CheckExitRules

There will be a delay between the time the exit is qualified for
and the time everyone is moved to the intermission spot, so you
can see the last frag.
=================
*/
void CheckExitRules( void ) {
 	int			i;
	int			elapsed;
	int			timeLimitMsec;
	int			mercyLimitMsec;
	int			scoreDelta;
	gclient_t	*cl;
	gentity_t	*te;

	if ( level.timeoutActive ) {
		return;
	}
	// if at the intermission, wait for all non-bots to
	// signal ready, then go to next level
	if ( level.intermissiontime ) {
		CheckIntermissionExit ();
		return;
	}

	if ( level.intermissionQueued ) {
		if ( level.time - level.intermissionQueued >= 200 ) {
			level.intermissionQueued = 0;
			BeginIntermission();
		}
		return;
	}

	if ( level.warmupTime ) {
		return;
	}

	if ( G_CanForfeit( NULL, qfalse ) ) {
		G_ApplyForfeit();
		return;
	}

	switch ( g_gametype.integer ) {
	case GT_CLAN_ARENA:
	case GT_ATTACK_DEFEND:
	case GT_RED_ROVER:
		return;
	case GT_FREEZE:
		if ( g_freezeRoundDelay.integer != 0 ) {
			return;
		}
		break;
	default:
		break;
	}

	elapsed = level.time - level.startTime;
	timeLimitMsec = G_BuildExitRuleLimitMsec( g_timelimit.integer, level.overtimeAccumulatedMsec );
	mercyLimitMsec = G_BuildExitRuleLimitMsec( g_mercytime.integer, level.overtimeAccumulatedMsec );

	if ( ScoreIsTied() ) {
		if ( g_timelimit.integer == 0 || g_overtime.integer <= 0 ) {
			return;
		}

		if ( elapsed < timeLimitMsec ) {
			return;
		}

		if ( G_StartOrExtendOvertime() ) {
			te = G_TempEntity( vec3_origin, EV_OVERTIME );
			te->r.svFlags |= SVF_BROADCAST;
		}
		return;
	}

	if ( g_timelimit.integer && !level.warmupTime ) {
		if ( elapsed >= timeLimitMsec ) {
			trap_SendServerCommand( -1, "print \"Timelimit hit.\n\"" );
			LogExit( "Timelimit hit." );
			return;
		}
	}

	if ( ( g_gametype.integer == GT_FFA || g_gametype.integer == GT_TOURNAMENT ||
		g_gametype.integer == GT_TEAM ) && g_fraglimit.integer ) {
		if ( level.teamScores[TEAM_RED] >= g_fraglimit.integer ) {
			trap_SendServerCommand( -1, "print \"Red hit the fraglimit.\n\"" );
			LogExit( "Fraglimit hit." );
			return;
		}

		if ( level.teamScores[TEAM_BLUE] >= g_fraglimit.integer ) {
			trap_SendServerCommand( -1, "print \"Blue hit the fraglimit.\n\"" );
			LogExit( "Fraglimit hit." );
			return;
		}

		for ( i=0 ; i< g_maxclients.integer ; i++ ) {
			cl = level.clients + i;
			if ( cl->pers.connected != CON_CONNECTED ) {
				continue;
			}
			if ( cl->sess.sessionTeam != TEAM_FREE ) {
				continue;
			}

			if ( cl->ps.persistant[PERS_SCORE] >= g_fraglimit.integer ) {
				LogExit( "Fraglimit hit." );
				trap_SendServerCommand( -1, va("print \"%s" S_COLOR_WHITE " hit the fraglimit.\n\"",
					cl->pers.netname ) );
				return;
			}
		}
	}

	if ( ( g_gametype.integer == GT_CTF || g_gametype.integer == GT_1FCTF ||
		g_gametype.integer == GT_OBELISK || g_gametype.integer == GT_HARVESTER ) &&
		g_capturelimit.integer ) {
		if ( level.teamScores[TEAM_RED] >= g_capturelimit.integer ) {
			trap_SendServerCommand( -1, "print \"Red hit the capturelimit.\n\"" );
			LogExit( "Capturelimit hit." );
			return;
		}

		if ( level.teamScores[TEAM_BLUE] >= g_capturelimit.integer ) {
			trap_SendServerCommand( -1, "print \"Blue hit the capturelimit.\n\"" );
			LogExit( "Capturelimit hit." );
			return;
		}
	}

	if ( g_gametype.integer == GT_DOMINATION && g_scorelimit.integer ) {
		if ( level.teamScores[TEAM_RED] >= g_scorelimit.integer ) {
			trap_SendServerCommand( -1, "print \"Red hit the scorelimit.\n\"" );
			LogExit( "Scorelimit hit." );
			return;
		}

		if ( level.teamScores[TEAM_BLUE] >= g_scorelimit.integer ) {
			trap_SendServerCommand( -1, "print \"Blue hit the scorelimit.\n\"" );
			LogExit( "Scorelimit hit." );
			return;
		}
	}

	if ( g_gametype.integer >= GT_TEAM && mercylimit.integer > 0 && elapsed >= mercyLimitMsec ) {
		scoreDelta = level.teamScores[TEAM_RED] - level.teamScores[TEAM_BLUE];
		if ( scoreDelta >= mercylimit.integer ) {
			trap_SendServerCommand( -1, "print \"Red hit the mercylimit.\n\"" );
			LogExit( "Mercylimit hit." );
			return;
		}

		if ( -scoreDelta >= mercylimit.integer ) {
			trap_SendServerCommand( -1, "print \"Blue hit the mercylimit.\n\"" );
			LogExit( "Mercylimit hit." );
			return;
		}
	}
}




/*
=============
G_ResetTimeoutState

Clears the timeout bookkeeping so matches can resume immediately.
=============
*/
void G_ResetTimeoutState( void ) {
	level.timeoutActive = qfalse;
	level.timeoutOwner = -1;
	level.timeoutTeam = TEAM_FREE;
	level.timeoutExpireTime = 0;
	level.timeoutStartTime = 0;
}

/*
=============
G_UpdateReadyUpConfigstring

Publishes the next ready-up deadline for HUD consumers.
=============
*/
void G_UpdateReadyUpConfigstring( void ) {
	int	deadline;

	if ( level.readyUpDelayDeadline > 0 ) {
		deadline = level.readyUpDelayDeadline;
	} else {
		deadline = ( level.warmupTime > 0 ) ? level.warmupTime : 0;
	}
	trap_SetConfigstring( CS_READYUP_STATUS, va( "%i", deadline ) );
}

/*
=============
G_SetWarmupTime

Stores the warmup timestamp and refreshes the retail side effects tied to CS_WARMUP.
=============
*/
void G_SetWarmupTime( int warmupTime ) {
	const char	*state;

	level.warmupTime = warmupTime;
	trap_SetConfigstring( CS_WARMUP, va( "%i", level.warmupTime ) );
	G_UpdateReadyUpConfigstring();
	G_CheckAutoRecord();

	if ( warmupTime < 0 ) {
		state = GAME_STATE_PRE_GAME;
	} else if ( warmupTime == 0 ) {
		state = GAME_STATE_IN_PROGRESS;
	} else {
		state = GAME_STATE_COUNT_DOWN;
	}

	G_SetGameState( state );
}

/*
=============
G_RequestWarmupMapRestart

Runs the retail qagame-owned warmup expiration sequence before map_restart.
=============
*/
static void G_RequestWarmupMapRestart( void ) {
	G_RankSendMatchStarted();
	level.warmupTime += 10000;
	trap_Cvar_Set( "g_restarted", "1" );
	trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\n" );
	level.restarted = qtrue;
}

/*
=============
G_PublishWarmupReadyConfigstring

Publishes the retail warmup readiness snapshot consumed by the HUD.
=============
*/
static void G_PublishWarmupReadyConfigstring( int readyCount, int eligibleCount, int readyMask ) {
	char	info[MAX_INFO_STRING];
	char	value[16];
	int	i;
	int	percent;

	if ( readyCount < 0 ) {
		readyCount = 0;
	}
	if ( eligibleCount < 0 ) {
		eligibleCount = 0;
	}
	if ( readyCount > eligibleCount ) {
		readyCount = eligibleCount;
	}

	percent = (int)( g_svWarmupReadyPercentage.value * 100.0f + 0.5f );
	if ( percent < 0 ) {
		percent = 0;
	} else if ( percent > 100 ) {
		percent = 100;
	}

	info[0] = '\0';
	Com_sprintf( value, sizeof( value ), "%i", percent );
	Info_SetValueForKey( info, MATCH_STATE_KEY_WARMUP_READY_PERCENT, value );
	Com_sprintf( value, sizeof( value ), "%i", readyCount );
	Info_SetValueForKey( info, MATCH_STATE_KEY_WARMUP_READY_COUNT, value );
	Com_sprintf( value, sizeof( value ), "%i", eligibleCount );
	Info_SetValueForKey( info, MATCH_STATE_KEY_WARMUP_READY_ELIGIBLE, value );
	trap_SetConfigstring( CS_WARMUP_READY, info );

	for ( i = 0; i < level.maxclients; i++ ) {
		gclient_t	*client;

		client = &level.clients[i];
		if ( client->pers.connected != CON_CONNECTED ) {
			continue;
		}

		client->ps.stats[STAT_CLIENTS_READY] = readyMask;
	}
}

/*
=============
G_WarmupReadyToStart

Returns qtrue once warmup has enough ready players to enter or remain in the
retail start-countdown path, and republishes the HUD readiness snapshot.
=============
*/
qboolean G_WarmupReadyToStart( void ) {
	int	i;
	int	eligibleCount;
	int	readyCount;
	int	readyMask;
	float	readyRatio;

	eligibleCount = 0;
	readyCount = 0;
	readyMask = 0;

	for ( i = 0; i < level.maxclients; i++ ) {
		gclient_t	*client;

		client = &level.clients[i];
		if ( client->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( g_gametype.integer == GT_TOURNAMENT ) {
			if ( client->sess.sessionTeam != TEAM_FREE ) {
				continue;
			}
		} else if ( client->sess.sessionTeam == TEAM_SPECTATOR ) {
			continue;
		}

		eligibleCount++;
		if ( G_ClientIsReady( client ) ) {
			readyCount++;
			if ( i < 16 ) {
				readyMask |= 1 << i;
			}
		}
	}

	level.readyUpEligibleClients = eligibleCount;
	level.readyUpReadyClients = readyCount;
	G_PublishWarmupReadyConfigstring( readyCount, eligibleCount, readyMask );

	if ( level.trainingMapActive ) {
		return qtrue;
	}

	if ( !g_doWarmup.integer ) {
		return qtrue;
	}

	if ( g_dedicated.integer && g_gametype.integer != GT_TOURNAMENT
		&& level.time - level.startTime < g_warmupDelay.integer * 1000 ) {
		return qfalse;
	}

	if ( level.warmupTime >= 0 ) {
		return qtrue;
	}

	if ( g_gametype.integer == GT_TOURNAMENT ) {
		return ( eligibleCount == 2 && readyCount == 2 ) ? qtrue : qfalse;
	}

	if ( g_gametype.integer >= GT_TEAM ) {
		if ( !Team_HasMinimumPlayersForWarmup() ) {
			return qfalse;
		}
	} else if ( level.numPlayingClients < 2 ) {
		return qfalse;
	}

	if ( g_svWarmupReadyPercentage.value <= 0.0f ) {
		return qtrue;
	}
	if ( eligibleCount <= 0 || readyCount <= 0 ) {
		return qfalse;
	}

	readyRatio = (float)readyCount / (float)eligibleCount;
	return ( readyRatio >= g_svWarmupReadyPercentage.value ) ? qtrue : qfalse;
}

/*
=============
G_GetDuelReadyStateCounts

Counts active duelists and the subset that are currently marked ready.
=============
*/
static void G_GetDuelReadyStateCounts( int *eligibleCount, int *readyCount ) {
	int	i;

	if ( eligibleCount ) {
		*eligibleCount = 0;
	}
	if ( readyCount ) {
		*readyCount = 0;
	}

	for ( i = 0; i < level.maxclients; i++ ) {
		gclient_t	*client;

		client = &level.clients[i];
		if ( client->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( client->sess.sessionTeam != TEAM_FREE ) {
			continue;
		}

		if ( eligibleCount ) {
			( *eligibleCount )++;
		}
		if ( readyCount && G_ClientIsReady( client ) ) {
			( *readyCount )++;
		}
	}
}

/*
=============
G_ClearConnectedReadyStates

Clears the persistent ready latch for every connected client and optionally
refreshes the published player configstring state.
=============
*/
static qboolean G_ClearConnectedReadyStates( qboolean updateUserinfo ) {
	int		i;
	qboolean	changed;

	changed = qfalse;

	for ( i = 0; i < level.maxclients; i++ ) {
		gclient_t	*client;

		client = &level.clients[i];
		if ( client->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( !G_ClientIsReady( client ) ) {
			continue;
		}

		G_SetClientReadyState( client, qfalse );
		if ( updateUserinfo ) {
			ClientUserinfoChanged( i );
		}
		changed = qtrue;
	}

	return changed;
}

/*
=============
G_ResetDuelWarmupState

Returns duel warmup to the retail waiting state and optionally clears ready latches.
=============
*/
static void G_ResetDuelWarmupState( qboolean clearReadyFlags ) {
	qboolean	configChanged;
	qboolean	warmupChanged;

	configChanged = qfalse;
	warmupChanged = qfalse;
	if ( level.readyUpDelayDeadline != 0 ) {
		level.readyUpDelayDeadline = 0;
		configChanged = qtrue;
	}
	if ( level.warmupTime != -1 ) {
		G_SetWarmupTime( -1 );
		warmupChanged = qtrue;
	}

	if ( clearReadyFlags && G_ClearConnectedReadyStates( qtrue ) ) {
		configChanged = qtrue;
	}

	if ( configChanged ) {
		G_UpdateReadyUpConfigstring();
	}
	if ( warmupChanged ) {
		G_LogPrintf( "Warmup:\n" );
	}
}

/*
=============
G_CheckReadyUpDelayAction

Mirrors the retail duel delay controller keyed by g_warmupReadyDelay and g_warmupReadyDelayAction.
=============
*/
static void G_CheckReadyUpDelayAction( void ) {
	int		i;

	if ( g_gametype.integer != GT_TOURNAMENT || !g_doWarmup.integer || g_warmupReadyDelay.integer <= 0 ) {
		if ( level.readyUpDelayDeadline != 0 ) {
			level.readyUpDelayDeadline = 0;
			G_UpdateReadyUpConfigstring();
		}
		return;
	}

	if ( level.numPlayingClients != 2 || level.readyUpReadyClients != 1 ) {
		if ( level.readyUpDelayDeadline != 0 ) {
			level.readyUpDelayDeadline = 0;
			G_UpdateReadyUpConfigstring();
		}
		return;
	}

	if ( level.readyUpDelayDeadline == 0 ) {
		level.readyUpDelayDeadline = level.time + g_warmupReadyDelay.integer * 1000;
		G_UpdateReadyUpConfigstring();
		return;
	}

	if ( level.time <= level.readyUpDelayDeadline ) {
		return;
	}

	for ( i = 0; i < level.maxclients; i++ ) {
		gclient_t	*client;

		client = &level.clients[i];
		if ( client->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( client->sess.sessionTeam != TEAM_FREE ) {
			continue;
		}

		if ( g_warmupReadyDelayAction.integer == 1 ) {
			if ( !G_ClientIsReady( client ) ) {
				SetTeam( &g_entities[i], "s" );
			} else {
				G_SetClientReadyState( client, qfalse );
				ClientUserinfoChanged( i );
			}
		} else if ( g_warmupReadyDelayAction.integer == 2 ) {
			G_SetClientReadyState( client, qtrue );
		}
	}

	level.readyUpDelayDeadline = 0;
	G_UpdateReadyUpConfigstring();
}

/*
=============
G_ShiftTimeoutAbsoluteTime

Advances finite absolute timers across a paused timeout while preserving
disabled and infinite sentinel values.
=============
*/
static int G_ShiftTimeoutAbsoluteTime( int value, int msec ) {
	if ( value <= 0 || value == INT_MAX ) {
		return value;
	}

	if ( value > INT_MAX - msec ) {
		return INT_MAX;
	}

	return value + msec;
}

/*
=============
G_ApplyTimeoutPauseDeltaToClient

Replays the retail timeout-resume timer adjustments for a connected client.
=============
*/
static void G_ApplyTimeoutPauseDeltaToClient( gclient_t *client, int msec, qboolean freezeEnabled ) {
	int		powerup;

	client->ps.pm_flags &= ~PMF_TIME_WATERJUMP;
	client->respawnTime = G_ShiftTimeoutAbsoluteTime( client->respawnTime, msec );
	client->airOutTime = G_ShiftTimeoutAbsoluteTime( client->airOutTime, msec );
	client->invulnerabilityTime = G_ShiftTimeoutAbsoluteTime( client->invulnerabilityTime, msec );
	client->holdableInvulnerabilityTime = G_ShiftTimeoutAbsoluteTime( client->holdableInvulnerabilityTime, msec );

	for ( powerup = 0; powerup < MAX_POWERUPS; powerup++ ) {
		client->ps.powerups[powerup] = G_ShiftTimeoutAbsoluteTime( client->ps.powerups[powerup], msec );
	}

	if ( !freezeEnabled ) {
		return;
	}

	client->freezeTime = G_ShiftTimeoutAbsoluteTime( client->freezeTime, msec );
	client->freezeAutoThawTime = G_ShiftTimeoutAbsoluteTime( client->freezeAutoThawTime, msec );
	client->freezeEnvironmentalRespawnTime = G_ShiftTimeoutAbsoluteTime( client->freezeEnvironmentalRespawnTime, msec );
	client->freezeProtectedUntil = G_ShiftTimeoutAbsoluteTime( client->freezeProtectedUntil, msec );
}

void G_ApplyTimeoutPauseDelta( int msec ) {
	qboolean	freezeEnabled;

	if ( msec <= 0 ) {
		return;
	}

	if ( level.roundTransitionTime > 0 ) {
		level.roundTransitionTime += msec;
	}

	if ( level.roundStartTime > 0 ) {
		level.roundStartTime += msec;
	}

	if ( level.adStateChangeTime > 0 ) {
		level.adStateChangeTime += msec;
	}

	if ( level.rrStateChangeTime > 0 ) {
		level.rrStateChangeTime += msec;
	}

	if ( level.rrLastInfectionTime > 0 ) {
		level.rrLastInfectionTime += msec;
	}

	if ( level.rrNextSurvivalBonusTime > 0 ) {
		level.rrNextSurvivalBonusTime += msec;
	}

	freezeEnabled = G_FreezeGametypeEnabled();
	{
		int			clientNum;

		for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
			gclient_t	*client;

			client = &level.clients[clientNum];
			if ( client->pers.connected == CON_DISCONNECTED ) {
				continue;
			}

			G_ApplyTimeoutPauseDeltaToClient( client, msec, freezeEnabled );
		}
	}

	if ( level.warmupTime > 0 ) {
		level.warmupTime += msec;
		trap_SetConfigstring( CS_WARMUP, va( "%i", level.warmupTime ) );
		G_UpdateReadyUpConfigstring();
	}

	if ( level.intermissionQueued ) {
		level.intermissionQueued += msec;
	}

	if ( level.readyToExit ) {
		level.exitTime += msec;
	}
}

/*
=============
G_CheckTimeoutExpired

Resumes play once the active timeout countdown reaches its expiry time.
=============
*/
static void G_CheckTimeoutExpired( void ) {
	int	pausedDuration;

	if ( !level.timeoutActive ) {
		return;
	}
	if ( !level.timeoutExpireTime || level.time < level.timeoutExpireTime ) {
		return;
	}

	pausedDuration = 0;
	if ( level.timeoutStartTime > 0 && level.time > level.timeoutStartTime ) {
		pausedDuration = level.time - level.timeoutStartTime;
	}

	G_ApplyTimeoutPauseDelta( pausedDuration );
	G_ResetTimeoutState();
	G_UpdateMatchStateConfigString();
}

int G_GetSuddenDeathRespawnDelay( void ) {
	const matchFactoryConfig_t *config = &g_matchFactoryConfig;

	if ( !level.overtimeActive ) {
		return 0;
	}
	if ( !config->suddenDeathRespawnsEnabled ) {
		return -1;
	}
	int baseDelay = config->suddenDeathStartSeconds;
	int tick = config->suddenDeathTickSeconds;
	int increment = config->suddenDeathIncrementSeconds;
	int maxDelay = config->suddenDeathMaxSeconds;
	int elapsed = ( level.time - level.overtimeStartTime ) / 1000;
	if ( elapsed < 0 ) {
		elapsed = 0;
	}
	int steps = elapsed / tick;
	int delaySeconds = baseDelay + steps * increment;
	if ( delaySeconds > maxDelay ) {
		delaySeconds = maxDelay;
	}
	return delaySeconds * 1000;
}

/*
=============
G_BuildExitRuleLimitMsec

Combines the configured minute limit with the retail overtime accumulator while
clamping the result into the signed millisecond range.
=============
*/
int G_BuildExitRuleLimitMsec( int minutes, int bonusMsec ) {
	long long	totalMsec;

	if ( minutes < 0 ) {
		minutes = 0;
	}
	if ( bonusMsec < 0 ) {
		bonusMsec = 0;
	}

	totalMsec = (long long)minutes * 60000 + bonusMsec;
	if ( totalMsec > INT_MAX ) {
		return INT_MAX;
	}

	return (int)totalMsec;
}

/*
=============
G_StartOrExtendOvertime

Advances the retail overtime accumulator and mirrors the current overtime
window through the source-side match-state configstring payload.
=============
*/
static qboolean G_StartOrExtendOvertime( void ) {
	int	lengthSeconds;
	int	overtimeMillis;

	lengthSeconds = g_overtime.integer;
	overtimeMillis = ( lengthSeconds > 0 ) ? lengthSeconds * 1000 : 0;
	if ( overtimeMillis <= 0 ) {
		return qfalse;
	}
	if ( level.overtimeActive && level.overtimeEndTime > level.time ) {
		return qfalse;
	}

	level.overtimeAccumulatedMsec += overtimeMillis;
	level.overtimeActive = qtrue;
	level.overtimeStartTime = level.time;
	level.overtimeEndTime = level.startTime +
		G_BuildExitRuleLimitMsec( g_timelimit.integer, level.overtimeAccumulatedMsec );
	level.overtimeCount++;
	level.suddenDeathActive = qtrue;
	level.suddenDeathLastDelay = -1;
	level.suddenDeathNoRespawnLogged = qfalse;
	G_LogPrintf( "match: overtime period %i started (%i second window)\n",
		level.overtimeCount, lengthSeconds );
	G_UpdateMatchStateConfigString();
	return qtrue;
}

/*
=============
G_StopOvertime

Clears the source-side overtime mirror once regulation or intermission state
has fully reset.
=============
*/
static void G_StopOvertime( void ) {
	if ( !level.overtimeActive && level.overtimeAccumulatedMsec == 0 &&
		level.overtimeCount == 0 && !level.suddenDeathActive ) {
		return;
	}

	level.overtimeActive = qfalse;
	level.overtimeEndTime = 0;
	level.overtimeStartTime = 0;
	level.overtimeAccumulatedMsec = 0;
	level.overtimeCount = 0;
	level.suddenDeathActive = qfalse;
	trap_SetConfigstring( CS_WARMUP_READY, "" );
	level.suddenDeathLastDelay = -1;
	level.suddenDeathNoRespawnLogged = qfalse;
	G_LogPrintf( "match: overtime cleared\n" );
	G_UpdateMatchStateConfigString();
}


static void LevelCheckTimers( void ) {
	int team;
	int overtimeDeadline;
	matchFactoryConfig_t previousConfig = matchFlow_lastConfig;
	const matchFactoryConfig_t *config = &g_matchFactoryConfig;

	if ( previousConfig.timeoutCountPerTeam != config->timeoutCountPerTeam ) {
		for ( team = TEAM_FREE; team < TEAM_NUM_TEAMS; team++ ) {
			level.timeoutRemaining[team] = config->timeoutCountPerTeam;
		}
		G_UpdateMatchStateConfigString();
	}
	if ( previousConfig.overtimeLengthSeconds != config->overtimeLengthSeconds ) {
		if ( level.overtimeActive ) {
			overtimeDeadline = level.startTime +
				G_BuildExitRuleLimitMsec( g_timelimit.integer, level.overtimeAccumulatedMsec );
			level.overtimeEndTime = ( overtimeDeadline > level.startTime ) ? overtimeDeadline : 0;
			G_UpdateMatchStateConfigString();
		}
	}
	if ( previousConfig.suddenDeathRespawnsEnabled != config->suddenDeathRespawnsEnabled ||
		previousConfig.suddenDeathStartSeconds != config->suddenDeathStartSeconds ||
		previousConfig.suddenDeathTickSeconds != config->suddenDeathTickSeconds ||
		previousConfig.suddenDeathMaxSeconds != config->suddenDeathMaxSeconds ||
		previousConfig.suddenDeathIncrementSeconds != config->suddenDeathIncrementSeconds ) {
		level.suddenDeathLastDelay = -1;
		level.suddenDeathNoRespawnLogged = qfalse;
	}

	matchFlow_lastConfig = *config;

	if ( level.timeoutActive ) {
		level.previousTime += level.msec;
	}

	G_CheckTimeoutExpired();
	if ( level.timeoutActive ) {
		return;
	}

	if ( level.intermissiontime || level.intermissionQueued || level.warmupTime ) {
		G_StopOvertime();
	}

	if ( level.overtimeActive ) {
		G_SuddenDeathThink();
	} else {
		level.suddenDeathLastDelay = -1;
		level.suddenDeathNoRespawnLogged = qfalse;
	}
}

/*
========================================================================

FUNCTIONS CALLED EVERY FRAME

========================================================================
*/


/*
=============
CheckTournament

Once a frame, check for changes in tournement player state
=============
*/
void CheckTournament( void ) {
	qboolean	warmupReady;

	// check because we run 3 game frames before calling Connect and/or ClientBegin
	// for clients on a map_restart
	if ( level.numPlayingClients == 0 ) {
		return;
	}

	if ( level.trainingMapActive ) {
		G_WarmupReadyToStart();
		if ( level.warmupTime != 0 ) {
			G_SetWarmupTime( 0 );
		}
		return;
	}

	if ( level.timeoutActive ) {
		return;
	}

	warmupReady = G_WarmupReadyToStart();

	if ( g_gametype.integer == GT_TOURNAMENT ) {
		int	eligibleCount;
		int	readyCount;

		if ( level.warmupTime == 0 ) {
			if ( G_CanForfeit( NULL, qfalse ) ) {
				G_ApplyForfeit();
			}
			return;
		}

		// if we don't have two players, go back to "waiting for players"
		if ( level.numPlayingClients != 2 ) {
			G_ResetDuelWarmupState( ( level.warmupTime != -1 ) ? qtrue : qfalse );
			return;
		}

		eligibleCount = 0;
		readyCount = 0;
		if ( g_doWarmup.integer ) {
			G_GetDuelReadyStateCounts( &eligibleCount, &readyCount );
		}

		// if the warmup is changed at the console, restart it
		if ( g_warmup.modificationCount != level.warmupModificationCount ) {
			level.warmupModificationCount = g_warmup.modificationCount;
			level.readyUpDelayDeadline = 0;
			G_SetWarmupTime( -1 );
			G_InitWeaponConfig();
		}

		// if all players have arrived, start the countdown
		if ( level.warmupTime < 0 ) {
			if ( g_doWarmup.integer ) {
				if ( eligibleCount == 2 && readyCount == 2 ) {
					if ( warmupReady ) {
						G_SetWarmupTime( level.time + g_warmup.integer * 1000 );
					}
				} else {
					G_CheckReadyUpDelayAction();
				}
			} else if ( level.numPlayingClients == 2 ) {
				G_SetWarmupTime( level.time + g_warmup.integer * 1000 );
			}
			return;
		}

		// if the warmup time has counted down, restart
		if ( level.time >= level.warmupTime ) {
			G_RequestWarmupMapRestart();
			return;
		}
	} else if ( g_gametype.integer != GT_SINGLE_PLAYER && level.warmupTime != 0 ) {
		qboolean		notEnough = qfalse;

		if ( g_gametype.integer >= GT_TEAM ) {
			if ( !Team_HasMinimumPlayersForWarmup() ) {
				notEnough = qtrue;
			}
		} else if ( level.numPlayingClients < 2 ) {
			notEnough = qtrue;
		}

		if ( notEnough ) {
			if ( level.warmupTime != -1 ) {
				G_ClearConnectedReadyStates( qtrue );
				G_SetWarmupTime( -1 );
				G_LogPrintf( "Warmup:\n" );
			}
			return; // still waiting for team members
		}

		if ( level.warmupTime == 0 ) {
			return;
		}

		// if the warmup is changed at the console, restart it
		if ( g_warmup.modificationCount != level.warmupModificationCount ) {
			level.warmupModificationCount = g_warmup.modificationCount;
			G_SetWarmupTime( -1 );
			G_InitWeaponConfig();
		}

		// if all players have arrived, start the countdown
		if ( level.warmupTime < 0 ) {
			if ( g_doWarmup.integer ) {
				if ( warmupReady ) {
					G_SetWarmupTime( level.time + g_warmup.integer * 1000 );
				}
			} else {
				G_SetWarmupTime( level.time + g_warmup.integer * 1000 );
				Team_ClampWarmupToShuffleCountdown();
			}
			return;
		}

		// if the warmup time has counted down, restart
		if ( level.time >= level.warmupTime ) {
			G_RequestWarmupMapRestart();
			return;
		}
	}
}

/*
==================
CheckVote
==================
*/
void CheckVote( void ) {
	int	voteResult;

	if ( level.voteExecuteTime && level.voteExecuteTime < level.time ) {
		level.voteExecuteTime = 0;
		if ( G_TryExecuteVoteString( level.voteString ) == qfalse ) {
			trap_SendConsoleCommand( EXEC_APPEND, va( "%s\n", level.voteString ) );
		}
	}
	if ( !level.voteTime ) {
		return;
	}

	voteResult = G_UpdateVoteCounts();
	if ( voteResult == 1 ) {
		if ( level.time - level.voteTime >= VOTE_TIME ) {
			trap_SendServerCommand( -1, "print \"Voting time has expired.\n\"" );
			G_ClearVoteState();
		}
		return;
	}

	if ( voteResult == 2 ) {
		trap_SendServerCommand( -1, "print \"Vote passed.\n\"" );
		G_ClearVoteState();
		level.voteExecuteTime = level.time + 3000;
		return;
	}

	trap_SendServerCommand( -1, "print \"Vote failed.\n\"" );
	G_ClearVoteState();
}

/*
==================
PrintTeam
==================
*/
void PrintTeam( int team, char *message ) {
	int i;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if ( level.clients[i].sess.sessionTeam != team ) {
			continue;
		}
		trap_SendServerCommand( i, message );
	}
}

/*
==================
SetLeader
==================
*/
void SetLeader(int team, int client) {
	int i;

	if ( level.clients[client].pers.connected == CON_DISCONNECTED ) {
		PrintTeam(team, va("print \"%s is not connected\n\"", level.clients[client].pers.netname) );
		return;
	}
	if (level.clients[client].sess.sessionTeam != team) {
		PrintTeam(team, va("print \"%s is not on the team anymore\n\"", level.clients[client].pers.netname) );
		return;
	}
	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if (level.clients[i].sess.sessionTeam != team)
			continue;
		if (level.clients[i].sess.teamLeader) {
			level.clients[i].sess.teamLeader = qfalse;
			ClientUserinfoChanged(i);
		}
	}
	level.clients[client].sess.teamLeader = qtrue;
	ClientUserinfoChanged( client );
	PrintTeam(team, va("print \"%s is the new team leader\n\"", level.clients[client].pers.netname) );
}

/*
==================
CheckTeamLeader
==================
*/
void CheckTeamLeader( int team ) {
	int i;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if (level.clients[i].sess.sessionTeam != team)
			continue;
		if (level.clients[i].sess.teamLeader)
			break;
	}
	if (i >= level.maxclients) {
		for ( i = 0 ; i < level.maxclients ; i++ ) {
			if (level.clients[i].sess.sessionTeam != team)
				continue;
			if (!(g_entities[i].r.svFlags & SVF_BOT)) {
				level.clients[i].sess.teamLeader = qtrue;
				break;
			}
		}
		for ( i = 0 ; i < level.maxclients ; i++ ) {
			if (level.clients[i].sess.sessionTeam != team)
				continue;
			level.clients[i].sess.teamLeader = qtrue;
			break;
		}
	}
}

/*
==================
CheckTeamVote
==================
*/
void CheckTeamVote( int team ) {
	int cs_offset;

	if ( team == TEAM_RED )
		cs_offset = 0;
	else if ( team == TEAM_BLUE )
		cs_offset = 1;
	else
		return;

	if ( !level.teamVoteTime[cs_offset] ) {
		return;
	}
	if ( level.time - level.teamVoteTime[cs_offset] >= VOTE_TIME ) {
		trap_SendServerCommand( -1, "print \"Team vote failed.\n\"" );
	} else {
		if ( level.teamVoteYes[cs_offset] > level.numteamVotingClients[cs_offset]/2 ) {
			// execute the command, then remove the vote
			trap_SendServerCommand( -1, "print \"Team vote passed.\n\"" );
			//
			if ( !Q_strncmp( "leader", level.teamVoteString[cs_offset], 6) ) {
				//set the team leader
				SetLeader(team, atoi(level.teamVoteString[cs_offset] + 7));
			}
			else {
				trap_SendConsoleCommand( EXEC_APPEND, va("%s\n", level.teamVoteString[cs_offset] ) );
			}
		} else if ( level.teamVoteNo[cs_offset] >= level.numteamVotingClients[cs_offset]/2 ) {
			// same behavior as a timeout
			trap_SendServerCommand( -1, "print \"Team vote failed.\n\"" );
		} else {
			// still waiting for a majority
			return;
		}
	}
	level.teamVoteTime[cs_offset] = 0;
	trap_SetConfigstring( CS_TEAMVOTE_TIME + cs_offset, "" );

}


/*
=============
G_TrackSuddenDeathAnnouncements

Publishes the retail sudden-death respawn announcement text while the
match-side delay controller is active.
=============
*/
static void G_TrackSuddenDeathAnnouncements( void ) {
	const matchFactoryConfig_t *config = &g_matchFactoryConfig;
	int delay;

	if ( g_suddenDeathRespawn.integer <= 0 || !config->suddenDeathRespawnsEnabled ) {
		if ( !level.suddenDeathNoRespawnLogged ) {
			level.suddenDeathNoRespawnLogged = qtrue;
			level.suddenDeathLastDelay = -1;
			G_LogPrintf( "match: sudden-death respawns disabled\n" );
			if ( config->suddenDeathPrintAnnouncements ) {
				trap_SendServerCommand( -1, "cp \"Sudden-death respawns disabled\n\"" );
			}
		}
		return;
	}

	delay = G_GetSuddenDeathRespawnDelay();
	if ( delay < 0 ) {
		delay = 0;
	}

	if ( level.suddenDeathLastDelay != delay ) {
		level.suddenDeathLastDelay = delay;
		level.suddenDeathNoRespawnLogged = qfalse;
		G_LogPrintf( "match: sudden-death respawn delay %i ms\n", delay );
		if ( config->suddenDeathPrintAnnouncements ) {
			if ( delay > 0 ) {
				trap_SendServerCommand( -1, va( "cp \"Sudden-death respawns available in %i seconds\n\"", delay / 1000 ) );
			} else {
				trap_SendServerCommand( -1, "cp \"Sudden-death respawns available now\n\"" );
			}
		}
	}
}

/*
================
G_SuddenDeathThink
================
*/
void G_SuddenDeathThink( void ) {
	if ( !level.suddenDeathActive ) {
		return;
	}

	G_TrackSuddenDeathAnnouncements();
}

/*
==================
CheckCvars
==================
*/
void CheckCvars( void ) {
	static int lastMod = -1;

	if ( g_password.modificationCount != lastMod ) {
		lastMod = g_password.modificationCount;
		if ( *g_password.string && Q_stricmp( g_password.string, "none" ) ) {
			trap_Cvar_Set( "g_needpass", "1" );
		} else {
			trap_Cvar_Set( "g_needpass", "0" );
		}
	}
}

static qlr_game_frame_context_t *G_GetFrameContext( void ) {
	if ( !g_qlr_frame_ctx ) {
		return NULL;
	}

	g_qlr_frame_ctx->level = ( qlr_level_locals_t * )&level;
	g_qlr_frame_ctx->entities = ( qlr_gentity_t * )g_entities;
	g_qlr_frame_ctx->entity_count = level.num_entities;

	return g_qlr_frame_ctx;
}

/*
=============
G_RunFrameTimeoutAdvance

Applies the retail timeout frame adjustments that keep entity timers and trajectories paused.
=============
*/
static void G_RunFrameTimeoutAdvance( int msec ) {
	gentity_t	*ent;
	int		i;

	if ( !level.timeoutActive || msec <= 0 ) {
		return;
	}

	level.startTime += msec;

	ent = g_entities;
	for ( i = 0; i < level.num_entities; i++, ent++ ) {
		if ( !ent->inuse ) {
			continue;
		}

		if ( ent->s.eType == ET_MISSILE || ent->s.eType == ET_MOVER ) {
			ent->s.pos.trTime += msec;
		}

		if ( ent->nextthink > 0 ) {
			ent->nextthink += msec;
		}

		ent->eventTime += msec;
	}
}

static void G_DispatchScheduledThinks( qlr_game_frame_context_t *ctx, int msec ) {
	gentity_t       *ent;
	int                     i;

	ent = g_entities;
	for ( i = 0; i < level.num_entities; i++, ent++ ) {
		if ( !ent->inuse ) {
			continue;
		}

		if ( ent->freeAfterEvent ) {
			continue;
		}

		if ( !ent->r.linked && ent->neverFree ) {
			continue;
		}

		if ( i < MAX_CLIENTS ) {
			continue;
		}

		if ( ent->s.eType == ET_MISSILE ) {
			continue;
		}

		if ( ent->s.eType == ET_ITEM || ent->physicsObject ) {
			continue;
		}

		if ( ent->s.eType == ET_MOVER ) {
			continue;
		}

		G_RunThink( ent );
	}

	if ( ctx && ctx->hooks.run_scheduled_thinks ) {
		ctx->hooks.run_scheduled_thinks( msec );
	}
}

static void G_StepEntities( qlr_game_frame_context_t *ctx ) {
	gentity_t       *ent;
	int                     i;

	ent = g_entities;
	for ( i = 0; i < level.num_entities; i++, ent++ ) {
		if ( !ent->inuse ) {
			continue;
		}

		if ( ent->freeAfterEvent ) {
			continue;
		}

		if ( !ent->r.linked && ent->neverFree ) {
			continue;
		}

		if ( ent->s.eType == ET_MISSILE ) {
			G_RunMissile( ent );

			if ( ctx && ctx->hooks.physics_step && ent->inuse ) {
				ctx->hooks.physics_step( ( qlr_gentity_t * )ent );
			}
			continue;
		}

		if ( ent->s.eType == ET_ITEM || ent->physicsObject ) {
			G_RunItem( ent );

			if ( ctx && ctx->hooks.physics_step && ent->inuse ) {
				ctx->hooks.physics_step( ( qlr_gentity_t * )ent );
			}
			continue;
		}

		if ( ent->s.eType == ET_MOVER ) {
			G_RunMover( ent );

			if ( ctx && ctx->hooks.physics_step && ent->inuse ) {
				ctx->hooks.physics_step( ( qlr_gentity_t * )ent );
			}
			continue;
		}

		if ( i < MAX_CLIENTS ) {
			G_RunThink( ent );
			if ( ent->inuse && ent->client ) {
				if ( ent->r.svFlags & SVF_BOT ) {
					ent->client->pers.cmd.serverTime = level.time;
					ClientThink_real( ent );
				}
			}

			if ( ctx ) {
				if ( ctx->hooks.physics_step && ent->inuse ) {
					ctx->hooks.physics_step( ( qlr_gentity_t * )ent );
				}

				if ( ctx->hooks.client_think && ent->inuse && ent->client ) {
					ctx->hooks.client_think( ( qlr_gentity_t * )ent );
				}
			}
			continue;
		}

		if ( ctx && ctx->hooks.physics_step && ent->inuse ) {
			ctx->hooks.physics_step( ( qlr_gentity_t * )ent );
		}
	}
}

static void G_DispatchEvents( qlr_game_frame_context_t *ctx ) {
	gentity_t       *ent;
	int                     i;

	ent = g_entities;
	for ( i = 0; i < level.num_entities; i++, ent++ ) {
		if ( !ent->inuse ) {
			continue;
		}

		if ( ctx && ctx->hooks.fire_event && ent->s.event &&
			ent->eventTime > level.previousTime && ent->eventTime <= level.time ) {
			ctx->hooks.fire_event( ( qlr_gentity_t * )ent );
		}

		if ( level.time - ent->eventTime > EVENT_VALID_MSEC ) {
			if ( ent->s.event ) {
				ent->s.event = 0;       // &= EV_EVENT_BITS;
				if ( ent->client ) {
					ent->client->ps.externalEvent = 0;
					// predicted events should never be set to zero
					//ent->client->ps.events[0] = 0;
					//ent->client->ps.events[1] = 0;
				}
			}

			if ( ent->freeAfterEvent ) {
				G_FreeEntity( ent );
				continue;
			} else if ( ent->unlinkAfterEvent ) {
				ent->unlinkAfterEvent = qfalse;
				trap_UnlinkEntity( ent );
			}
		}
	}
}

static void G_FinishClientFrames( qlr_game_frame_context_t *ctx ) {
	gentity_t       *ent;
	int                     i;

	ent = g_entities;
	for ( i = 0; i < level.maxclients; i++, ent++ ) {
		if ( !ent->inuse ) {
			continue;
		}

		ClientEndFrame( ent );

		if ( ctx && ctx->hooks.client_end_frame && ent->client ) {
			ctx->hooks.client_end_frame( ( qlr_gentity_t * )ent );
		}
	}
}

/*
=============
G_UpdateGameStateForLevel

Evaluates warmup, intermission, and overtime state to keep g_gameState in sync.
=============
*/
static void G_UpdateGameStateForLevel( void ) {
	const char	*state;
	int		countdownRemaining;

	if ( level.intermissiontime || level.intermissionQueued ) {
		state = GAME_STATE_IN_PROGRESS;
	} else if ( level.warmupTime > 0 ) {
		countdownRemaining = level.warmupTime - level.time;
		if ( countdownRemaining <= 0 ) {
			state = GAME_STATE_IN_PROGRESS;
		} else {
			state = GAME_STATE_COUNT_DOWN;
		}
	} else if ( level.warmupTime == 0 ) {
		state = GAME_STATE_IN_PROGRESS;
	} else {
		state = GAME_STATE_PRE_GAME;
	}

	G_SetGameState( state );
	G_CheckAutoRecord();
}

/*
=============
G_RunFrameRoundModeCountHooks

Publishes the retail round-controller team-count auxiliaries in the pre-exit
slot used by the frame tail.
=============
*/
static void G_RunFrameRoundModeCountHooks( void ) {
	switch ( g_gametype.integer ) {
	case GT_CLAN_ARENA:
	case GT_FREEZE:
	case GT_ATTACK_DEFEND:
	case GT_RED_ROVER:
		G_UpdateTeamCountConfigstrings();
		break;

	default:
		break;
	}
}

/*
=============
G_RunFrameGametypeHooks

Runs the retail late-frame gametype switch after exit/team maintenance.
=============
*/
static void G_RunFrameGametypeHooks( void ) {
	if ( g_gametype.integer == GT_FFA ) {
		G_EnsureQuadHogQuad();
	} else if ( g_gametype.integer == GT_CLAN_ARENA || g_gametype.integer == GT_FREEZE ) {
		G_Frame_UpdateRoundController();
	} else if ( g_gametype.integer == GT_ATTACK_DEFEND ) {
		if ( level.adRoundState == AD_ROUNDSTATE_EXIT ) {
			G_Frame_UpdateRoundController();
			return;
		}

		G_Frame_UpdateRoundController();
	} else if ( g_gametype.integer == GT_RED_ROVER ) {
		G_RRTrackRoundActivity();
	} else if ( g_gametype.integer == GT_CTF ) {
		Team_ReturnFlagIfMissing( TEAM_RED );
		Team_ReturnFlagIfMissing( TEAM_BLUE );
	} else if ( g_gametype.integer == GT_DOMINATION ) {
		G_UpdateDominationPointCountConfigstrings();
	}
}

static void G_CheckLevelTimers( qlr_game_frame_context_t *ctx, int previousWarmupTime, int previousIntermissionQueued ) {
	CheckExitRules();
	if ( g_gametype.integer >= GT_TEAM ) {
		CheckTeamStatus();
		G_AutoShuffleCountdown_Frame();
		Team_UpdateAutoShuffleState();
	}
	G_RunFrameGametypeHooks();
	CheckVote();
	CheckCvars();
	G_UpdateGameStateForLevel();

	if ( !ctx ) {
		return;
	}

	if ( previousWarmupTime > 0 && level.warmupTime <= 0 ) {
		G_RankSendMatchStarted();
	}

	if ( ctx->hooks.begin_match && previousWarmupTime > 0 && level.warmupTime <= 0 ) {
		ctx->hooks.begin_match();
	}

	if ( ctx->hooks.begin_intermission && previousIntermissionQueued == 0 && level.intermissionQueued != 0 ) {
		ctx->hooks.begin_intermission();
	}
}

/*
=============
G_RunThink

Runs thinking code for this frame if necessary
=============
*/
void G_RunThink (gentity_t *ent) {
	float	thinktime;

	thinktime = ent->nextthink;
	if ( ent->runFrame ) {
		ent->runFrame( ent, thinktime );
	}
	if (thinktime <= 0) {
		return;
	}
	if (thinktime > level.time) {
		return;
	}
	
	ent->nextthink = 0;
	if (!ent->think) {
		G_Error ( "NULL ent->think");
	}
	ent->think (ent);
}

/*
=============
G_QuadHogReset

Clears the Quad Hog tracking state on the server.
=============
*/
static void G_QuadHogReset( void ) {
	level.quadHogOwner = ENTITYNUM_NONE;
	level.quadHogExpireTime = 0;
	level.quadHogLastActiveTime = 0;
	level.quadHogNextPingTime = 0;
}

/*
=============
G_QuadHogRemove

Revokes the Quad powerup from the current Quad Hog carrier.
=============
*/
static void G_QuadHogRemove( gentity_t *owner, const char *reason ) {
	if ( owner && owner->client ) {
		owner->client->ps.powerups[PW_QUAD] = 0;
		if ( reason && reason[0] ) {
			trap_SendServerCommand( owner->s.number, va( "print \"%s\n\"", reason ) );
		}
	}

	G_QuadHogReset();
}

/*
=============
G_QuadHogOnPickup

Initialises Quad Hog timers when a player claims the Quad.
=============
*/
void G_QuadHogOnPickup( gentity_t *player ) {
	if ( !level.quadHogEnabled ) {
		G_QuadHogReset();
		return;
	}

	if ( !player || !player->client ) {
		G_QuadHogReset();
		return;
	}

	level.quadHogOwner = player->s.number;
	level.quadHogLastActiveTime = level.time;
	if ( g_weaponConfig.quadHogTimeSeconds > 0 ) {
		level.quadHogExpireTime = level.time + g_weaponConfig.quadHogTimeSeconds * 1000;
	} else {
		level.quadHogExpireTime = 0;
	}
	if ( g_weaponConfig.quadHogPingRateMilliseconds > 0 ) {
		level.quadHogNextPingTime = level.time + g_weaponConfig.quadHogPingRateMilliseconds;
	} else {
		level.quadHogNextPingTime = 0;
	}
}

/*
=============
G_QuadHogFrame

Processes Quad Hog timers each server frame.
=============
*/
void G_QuadHogFrame( void ) {
	gentity_t	*owner;
	qboolean	active = qfalse;

	if ( !level.quadHogEnabled || g_gametype.integer != GT_FFA ) {
		G_QuadHogReset();
		return;
	}

	G_EnsureQuadHogQuad();

	if ( level.quadHogOwner < 0 || level.quadHogOwner >= level.maxclients ) {
		G_QuadHogReset();
		return;
	}

	owner = &g_entities[level.quadHogOwner];
	if ( !owner->inuse || !owner->client ) {
		G_QuadHogReset();
		return;
	}

	if ( owner->client->ps.powerups[PW_QUAD] <= level.time ) {
		G_QuadHogReset();
		return;
	}

	if ( g_weaponConfig.quadHogTimeSeconds > 0 && level.quadHogExpireTime > 0 && level.time >= level.quadHogExpireTime ) {
		G_QuadHogRemove( owner, "Quad Hog: timer expired!" );
		return;
	}

	if ( owner->client->pers.cmd.forwardmove || owner->client->pers.cmd.rightmove || owner->client->pers.cmd.upmove ) {
		active = qtrue;
	}
	if ( owner->client->pers.cmd.buttons & BUTTON_ATTACK ) {
		active = qtrue;
	}
	if ( !active ) {
		vec3_t	velocity;

		VectorCopy( owner->client->ps.velocity, velocity );
		if ( VectorLengthSquared( velocity ) > 1.0f ) {
			active = qtrue;
		}
	}

	if ( active ) {
		level.quadHogLastActiveTime = level.time;
	} else if ( g_weaponConfig.quadHogIdleSeconds > 0 ) {
		int	idleLimit = g_weaponConfig.quadHogIdleSeconds * 1000;
		if ( level.time - level.quadHogLastActiveTime >= idleLimit ) {
			G_QuadHogRemove( owner, "Quad Hog: idle penalty!" );
			return;
		}
	}

	if ( g_weaponConfig.quadHogPingRateMilliseconds > 0 ) {
		if ( level.quadHogNextPingTime == 0 ) {
			level.quadHogNextPingTime = level.time + g_weaponConfig.quadHogPingRateMilliseconds;
		} else if ( level.time >= level.quadHogNextPingTime ) {
			int	remainingMs = 0;

			if ( g_weaponConfig.quadHogTimeSeconds > 0 && level.quadHogExpireTime > 0 ) {
				remainingMs = level.quadHogExpireTime - level.time;
				if ( remainingMs < 0 ) {
					remainingMs = 0;
				}
			}

			trap_SendServerCommand( owner->s.number, va( "print \"Quad Hog: %d seconds remaining\\n\"", remainingMs / 1000 ) );
			level.quadHogNextPingTime = level.time + g_weaponConfig.quadHogPingRateMilliseconds;
		}
	}
}

/*
=============
G_RunFrame

Advance the game simulation by one frame.
=============
*/
void G_RunFrame( int levelTime ) {
	int		msec;
	int		previousWarmupTime;
	int		previousIntermissionQueued;
	qlr_game_frame_context_t	*ctx;

	if ( level.restarted ) {
		return;
	}

	msec = levelTime - level.time;
	if ( msec < 0 ) {
		msec = 0;
	}

	previousWarmupTime = level.warmupTime;
	previousIntermissionQueued = level.intermissionQueued;

	level.previousTime = level.time;
	level.time = levelTime;
	level.msec = msec;
	level.framenum++;

	ctx = G_GetFrameContext();

	G_UpdateCvars();
	G_RefreshPmoveSettings();
	G_UpdateVoteThrottle();

	if ( !level.timeoutActive ) {
		G_DispatchScheduledThinks( ctx, msec );
		G_StepEntities( ctx );
		G_DispatchEvents( ctx );
		Team_RunDomination();
	} else {
		G_RunFrameTimeoutAdvance( msec );
	}
	G_FinishClientFrames( ctx );
	AddTournamentPlayer();
	G_SyncTournamentQueueTeamTasks();
	CheckTournament();
	G_RunFrameRoundModeCountHooks();
	LevelCheckTimers();
	G_CheckLevelTimers( ctx, previousWarmupTime, previousIntermissionQueued );

}


/*
=============
G_UpdateGametypeTutorialText

Publishes Domination and Freeze Tag tutorial strings so clients see coaching tips.
=============
*/
static void G_UpdateGametypeTutorialText( void ) {
	const qlGametypeTutorialDef_t	*tutorial;

	trap_SetConfigstring( CS_FREEZE_TIP_OBJECTIVE, "" );
	trap_SetConfigstring( CS_FREEZE_TIP_THAW, "" );
	trap_SetConfigstring( CS_FREEZE_TIP_FREEZE, "" );
	trap_SetConfigstring( CS_FREEZE_TIP_SHOOT, "" );
	trap_SetConfigstring( CS_FREEZE_TIP_SUMMARY, "" );

	tutorial = QL_FindGametypeTutorial( g_gametype.integer );
	if ( !tutorial ) {
		trap_SetConfigstring( CS_TUTORIAL_NAME, "" );
		trap_SetConfigstring( CS_TUTORIAL_TEXT, "" );
		return;
	}

	trap_SetConfigstring( CS_TUTORIAL_NAME, tutorial->name );
	trap_SetConfigstring( CS_TUTORIAL_TEXT, tutorial->text );

	if ( tutorial->freezeTips ) {
		const qlFreezeHudTips_t	*tips = tutorial->freezeTips;

		trap_SetConfigstring( CS_FREEZE_TIP_OBJECTIVE, tips->objective );
		trap_SetConfigstring( CS_FREEZE_TIP_THAW, tips->thaw );
		trap_SetConfigstring( CS_FREEZE_TIP_FREEZE, tips->freeze );
		trap_SetConfigstring( CS_FREEZE_TIP_SHOOT, tips->shoot );
		trap_SetConfigstring( CS_FREEZE_TIP_SUMMARY, tips->summary );
	}
}

