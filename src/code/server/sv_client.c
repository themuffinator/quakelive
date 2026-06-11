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
// sv_client.c -- server code for dealing with clients

#include "server.h"
#include "../../common/platform/platform_steamworks.h"

#include <limits.h>
#include <stdarg.h>
#include <stdlib.h>

static void SV_CloseDownload( client_t *cl );

#if SV_HAS_PLATFORM_AUTH
static qboolean sv_steamServerConnected;

#define SV_STEAM_STATS_FIELD_COUNT 88
#define SV_STEAM_ACHIEVEMENT_COUNT 59
#define SV_STEAM_STAT_MEDAL_FIRSTFRAG 0x41
#define SV_STEAM_STAT_MEDAL_GAUNTLET 0x42
#define SV_STEAM_STAT_MEDAL_EXCELLENT 0x43
#define SV_STEAM_STAT_MEDAL_REVENGE 0x44
#define SV_STEAM_STAT_MEDAL_COMBOKILL 0x45
#define SV_STEAM_STAT_MEDAL_MIDAIR 0x46
#define SV_STEAM_STAT_MEDAL_PERFORATED 0x47
#define SV_STEAM_STAT_MEDAL_RAMPAGE 0x48
#define SV_STEAM_STAT_MEDAL_IMPRESSIVE 0x49
#define SV_STEAM_STAT_MEDAL_CAPTURE 0x4a
#define SV_STEAM_STAT_MEDAL_ASSIST 0x4b
#define SV_STEAM_STAT_MEDAL_DEFENSE 0x4c
#define SV_STEAM_STAT_MEDAL_HEADSHOT 0x4d
#define SV_STEAM_STAT_MEDAL_QUADGOD 0x4e
#define SV_STEAM_STAT_MEDAL_PERFECT 0x4f
#define SV_STEAM_STAT_MEDAL_ACCURACY 0x50
#define SV_STEAM_STAT_WINS 0x51
#define SV_STEAM_STAT_LOSSES 0x52
#define SV_STEAM_STAT_PLAYED 0x53
#define SV_STEAM_ACHIEVEMENT_SPEED_KILLS 1
#define SV_STEAM_ACHIEVEMENT_TRAINING_3_2 9
#define SV_STEAM_ACHIEVEMENT_WICKED 0x0e
#define SV_STEAM_ACHIEVEMENT_MVP 0x2e
#define SV_STEAM_PLAYER_STATS_TRAINING_MAP "qztraining"
#define SV_STEAM_PLAYER_KILL_SPEED_THRESHOLD 500.0f
#define SV_STEAM_PLAYER_MEDAL_MVP_TOTAL 0x3e8
#define SV_STEAM_PLAYER_DEATH_EVENT_LIMIT 0x3e8
#define SV_STEAM_PLAYER_DEATH_TOKEN_CHARS 64
#define SV_STEAM_PLAYER_DEATH_STEAMID_CHARS 32
#define SV_STEAM_PLAYER_DEATH_POWERUPS_CHARS 128
#define SV_STEAM_PLAYER_DEATH_RAW_PAYLOAD_CHARS 1024
#define SV_STEAM_PLAYER_STATS_WICKED_SCORE 0x29a
#define SV_STEAM_PLAYER_STATS_WICKED_GAMETYPE 5
#define SV_STEAM_JSON_OBJECT_OPEN 0x7b
#define SV_STEAM_JSON_OBJECT_CLOSE 0x7d
#define SV_STEAM_JSON_ARRAY_OPEN 0x5b
#define SV_STEAM_JSON_ARRAY_CLOSE 0x5d
#define SV_STEAM_JSON_STRING_QUOTE 0x22
#define SV_STEAM_JSON_ESCAPE 0x5c
#define SV_STEAM_STATS_P2P_HELLO "hello"
#define SV_STEAM_STATS_P2P_SEND_RELIABLE 2
#define SV_STEAM_STATS_P2P_CHANNEL 16
#define SV_STEAM_STATS_SUMMARY_PEER_LIMIT MAX_CLIENTS
#define SV_STEAM_STATS_SUMMARY_SEND_RELIABLE 2
#define SV_STEAM_STATS_SUMMARY_CHANNEL 0

typedef enum {
	SV_STEAM_STAT_INT = 0,
	SV_STEAM_STAT_FLOAT = 1,
	SV_STEAM_STAT_AVG_RATE = 2
} sv_steam_stat_type_t;

typedef struct {
	const char *name;
	sv_steam_stat_type_t type;
} sv_steam_stat_descriptor_t;

typedef struct {
	const char *medalName;
	int statIndex;
} sv_steam_medal_stat_map_t;

typedef struct {
	int time;
	int killerTeam;
	int victimTeam;
	char modName[SV_STEAM_PLAYER_DEATH_TOKEN_CHARS];
	char killerName[MAX_NAME_LENGTH];
	char killerSteamId[SV_STEAM_PLAYER_DEATH_STEAMID_CHARS];
	char killerPowerups[SV_STEAM_PLAYER_DEATH_POWERUPS_CHARS];
	char victimName[MAX_NAME_LENGTH];
	char victimSteamId[SV_STEAM_PLAYER_DEATH_STEAMID_CHARS];
	char victimPowerups[SV_STEAM_PLAYER_DEATH_POWERUPS_CHARS];
	char rawPayload[SV_STEAM_PLAYER_DEATH_RAW_PAYLOAD_CHARS];
} sv_steam_player_death_event_t;

typedef struct {
	qboolean active;
	qboolean backendAvailable;
	qboolean requestIssued;
	CSteamID steamId;
	uint32_t appId;
	int statValue[SV_STEAM_STATS_FIELD_COUNT];
	int pendingStatDelta[SV_STEAM_STATS_FIELD_COUNT];
	float statFloatValue[SV_STEAM_STATS_FIELD_COUNT];
	float pendingStatFloatDelta[SV_STEAM_STATS_FIELD_COUNT];
	float pendingAvgRateCount[SV_STEAM_STATS_FIELD_COUNT];
	double pendingAvgRateSessionLength[SV_STEAM_STATS_FIELD_COUNT];
	qboolean statLoaded[SV_STEAM_STATS_FIELD_COUNT];
	qboolean statQueryAttempted[SV_STEAM_STATS_FIELD_COUNT];
	qboolean statDirty[SV_STEAM_STATS_FIELD_COUNT];
	qboolean achievementUnlocked[SV_STEAM_ACHIEVEMENT_COUNT];
	qboolean achievementLoaded[SV_STEAM_ACHIEVEMENT_COUNT];
	qboolean achievementQueryAttempted[SV_STEAM_ACHIEVEMENT_COUNT];
	qboolean achievementDirty[SV_STEAM_ACHIEVEMENT_COUNT];
} sv_steam_stats_session_t;

typedef struct {
	qboolean active;
	CSteamID steamId;
} sv_steam_stats_summary_peer_t;

static sv_steam_stats_session_t sv_steamStatsSessions[MAX_CLIENTS];
static sv_steam_stats_summary_peer_t s_svSteamSummaryPeers[SV_STEAM_STATS_SUMMARY_PEER_LIMIT];
static int s_svSteamSummaryPeerCount;
static sv_steam_player_death_event_t s_svSteamPlayerDeathEvents[SV_STEAM_PLAYER_DEATH_EVENT_LIMIT];
static int s_svSteamPlayerDeathEventCount;

#define SV_STEAM_STAT_DESCRIPTOR( name, type ) { name, type }

static const sv_steam_stat_descriptor_t s_svSteamStatDescriptors[SV_STEAM_STATS_FIELD_COUNT] = {
	SV_STEAM_STAT_DESCRIPTOR( "version", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "kill_gauntlet", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "kill_machinegun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "kill_shotgun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "kill_grenade", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "kill_rocket", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "kill_lightning", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "kill_railgun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "kill_plasma", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "kill_bfg", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "kill_nailgun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "kill_proxmine", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "kill_chaingun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "kill_hmg", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "hits_machinegun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "hits_shotgun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "hits_grenade", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "hits_rocket", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "hits_lightning", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "hits_railgun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "hits_plasma", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "hits_bfg", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "hits_nailgun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "hits_proxmine", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "hits_chaingun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "hits_hmg", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "shots_machinegun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "shots_shotgun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "shots_grenade", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "shots_rocket", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "shots_lightning", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "shots_railgun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "shots_plasma", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "shots_bfg", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "shots_nailgun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "shots_proxmine", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "shots_chaingun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "shots_hmg", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_shotgun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_gauntlet", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_machinegun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_grenade", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_rocket", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_plasma", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_railgun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_lightning", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_bfg", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_water", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_slime", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_lava", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_crush", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_telefrag", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_laser", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "BROKEN1", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_nailgun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_chaingun", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_proxmine", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_kamikaze", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_juiced", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_suicide", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_falling", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_grapple", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_hmg", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_lightning_discharge", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_other", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_firstfrag", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_gauntlet", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_excellent", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_revenge", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_combokill", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_midair", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_perforated", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_rampage", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_impressive", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_capture", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_assist", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_defense", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_headshot", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_quadgod", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_perfect", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "medal_accuracy", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "wins", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "losses", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "played", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "BROKEN2", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "mod_hurt", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "total_kills", SV_STEAM_STAT_INT ),
	SV_STEAM_STAT_DESCRIPTOR( "total_deaths", SV_STEAM_STAT_INT )
};

#undef SV_STEAM_STAT_DESCRIPTOR

static const sv_steam_medal_stat_map_t s_svSteamMedalStatMap[] = {
	{ "FIRSTFRAG", SV_STEAM_STAT_MEDAL_FIRSTFRAG },
	{ "GAUNTLET", SV_STEAM_STAT_MEDAL_GAUNTLET },
	{ "EXCELLENT", SV_STEAM_STAT_MEDAL_EXCELLENT },
	{ "REVENGE", SV_STEAM_STAT_MEDAL_REVENGE },
	{ "COMBOKILL", SV_STEAM_STAT_MEDAL_COMBOKILL },
	{ "MIDAIR", SV_STEAM_STAT_MEDAL_MIDAIR },
	{ "PERFORATED", SV_STEAM_STAT_MEDAL_PERFORATED },
	{ "RAMPAGE", SV_STEAM_STAT_MEDAL_RAMPAGE },
	{ "IMPRESSIVE", SV_STEAM_STAT_MEDAL_IMPRESSIVE },
	{ "CAPTURE", SV_STEAM_STAT_MEDAL_CAPTURE },
	{ "ASSIST", SV_STEAM_STAT_MEDAL_ASSIST },
	{ "DEFENSE", SV_STEAM_STAT_MEDAL_DEFENSE },
	{ "HEADSHOT", SV_STEAM_STAT_MEDAL_HEADSHOT },
	{ "QUADGOD", SV_STEAM_STAT_MEDAL_QUADGOD },
	{ "PERFECT", SV_STEAM_STAT_MEDAL_PERFECT },
	{ "ACCURACY", SV_STEAM_STAT_MEDAL_ACCURACY }
};

static const char *s_svSteamAchievementNames[SV_STEAM_ACHIEVEMENT_COUNT] = {
	"AW_MIDAIR",
	"AW_SPEED_KILLS",
	"AW_TRAINING_1_1",
	"AW_TRAINING_1_2",
	"AW_TRAINING_1_3",
	"AW_TRAINING_2_1",
	"AW_TRAINING_2_2",
	"AW_TRAINING_2_3",
	"AW_TRAINING_3_1",
	"AW_TRAINING_3_2",
	"AW_FIRST_FRAG",
	"AW_TESTING",
	"AW_BIG_TIME",
	"AW_PRIZE_FIGHTER",
	"AW_WICKED",
	"AW_BANDIT",
	"AW_CAMPER",
	"AW_PSYCHIC",
	"AW_WTF_WAS_THAT",
	"AW_OVERKILL",
	"AW_RAPTOR",
	"AW_PLUS_ONE",
	"AW_KILLJOY",
	"AW_HAT_TRICK",
	"AW_MIRACLE_MAKER",
	"AW_BRAWLER",
	"AW_AIR_HAMMER",
	"AW_AIM_BOT",
	"AW_SUCKER_PUNCH",
	"AW_RESOURCE_HOG",
	"AW_NINJA_CAP",
	"AW_MISSED_OPPORTUNITY",
	"AW_SKULL_TRUMPET",
	"AW_FIGHT_CLUB",
	"AW_GUARDIAN",
	"AW_SIDEKICK",
	"AW_COLOR_GUARD",
	"AW_2_IN_2",
	"AW_ASSASSIN",
	"AW_EVIL_EYE",
	"AW_VICTORY",
	"AW_POINT_DENIED",
	"AW_FIRST_TASTE",
	"AW_HOOKED",
	"AW_FEAR_ME",
	"AW_VADRIGAR",
	"AW_MVP",
	"AW_SMACK_DOWN",
	"AW_HERE_GOES_NOTHING",
	"AW_LAST_HOPE",
	"AW_PUNCH_OUT",
	"AW_NADE_SPAM",
	"AW_ROCKET_MAN",
	"AW_PULL",
	"AW_CLUTCH",
	"AW_JESSE_JAMES",
	"AW_FULL_HOUSE",
	"AW_TRIFECTA",
	"AW_MAX"
};

static void SV_LogSteamStatsLifecycle( const CSteamID *steamId, const char *stage, const char *detail );

/*
=================
SV_ClearPlatformAuthState

Resets all retained server-side Steam auth state for one client slot.
=================
*/
static void SV_ClearPlatformAuthState( client_t *cl ) {
	if ( !cl ) {
		return;
	}

	cl->platformAuthPending = qfalse;
	cl->platformAuthSucceeded = qfalse;
	cl->platformAuthSessionActive = qfalse;
	cl->platformAuthLabel[0] = '\0';
	cl->platformAuthToken[0] = '\0';
	cl->platformAuthResult[0] = '\0';
	cl->platformAuthOutcome[0] = '\0';
	cl->platformAuthMessage[0] = '\0';
	cl->platformSteamId[0] = '\0';
}

/*
=================
SV_ClearChallengePlatformAuth

Clears the Steam auth data retained by one challenge entry.
=================
*/
static void SV_ClearChallengePlatformAuth( challenge_t *challenge ) {
	if ( !challenge ) {
		return;
	}

	challenge->platformSteamIdLow = 0u;
	challenge->platformSteamIdHigh = 0u;
	challenge->platformAuthTicketLength = 0;
	Com_Memset( challenge->platformAuthTicket, 0, sizeof( challenge->platformAuthTicket ) );
}

/*
=================
SV_ReadSteamChallengeWord

Reads one little-endian SteamID word from the retail getchallenge payload.
=================
*/
static uint32_t SV_ReadSteamChallengeWord( const byte *buffer ) {
	return (uint32_t)buffer[0]
		| ( (uint32_t)buffer[1] << 8 )
		| ( (uint32_t)buffer[2] << 16 )
		| ( (uint32_t)buffer[3] << 24 );
}

/*
=================
SV_FormatPlatformSteamIdWords

Formats two retail SteamID words as the decimal userinfo identity.
=================
*/
static void SV_FormatPlatformSteamIdWords( uint32_t steamIdLow, uint32_t steamIdHigh, char *buffer, size_t bufferSize ) {
	unsigned long long steamId;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	steamId = ( (unsigned long long)steamIdHigh << 32 ) | steamIdLow;
	Com_sprintf( buffer, (int)bufferSize, "%llu", steamId );
}

/*
=================
SV_ParseSteamChallengeAuth

Parses the SteamID and auth ticket appended to the retail getchallenge packet.
=================
*/
static qboolean SV_ParseSteamChallengeAuth( challenge_t *challenge, const msg_t *msg, const char **rejectMessage ) {
	const byte	*data;
	const char	*command;
	int			steamIdOffset;
	int			ticketOffset;
	int			ticketLength;

	if ( rejectMessage ) {
		*rejectMessage = "No Steam auth token.";
	}

	if ( !challenge || !msg || !msg->data ) {
		return qfalse;
	}

	SV_ClearChallengePlatformAuth( challenge );

	command = NET_GetChallengeRequestCommand();
	steamIdOffset = 4 + (int)strlen( command ) + 1;
	ticketOffset = steamIdOffset + 8;
	ticketLength = msg->cursize - ticketOffset;

	if ( ticketLength <= QL_STEAM_CHALLENGE_TOKEN_MIN_LENGTH ) {
		if ( rejectMessage ) {
			*rejectMessage = "No Steam auth token.";
		}
		return qfalse;
	}

	if ( ticketLength > QL_STEAM_AUTH_TICKET_MAX_LENGTH ) {
		if ( rejectMessage ) {
			*rejectMessage = "Auth token too large.";
		}
		return qfalse;
	}

	data = msg->data;
	challenge->platformSteamIdLow = SV_ReadSteamChallengeWord( data + steamIdOffset );
	challenge->platformSteamIdHigh = SV_ReadSteamChallengeWord( data + steamIdOffset + 4 );
	challenge->platformAuthTicketLength = ticketLength;
	Com_Memcpy( challenge->platformAuthTicket, data + ticketOffset, ticketLength );

	return qtrue;
}

/*
=================
SV_CapturePlatformAuthFromChallenge

Moves the retained challenge SteamID and ticket into the accepted client slot.
=================
*/
static qboolean SV_CapturePlatformAuthFromChallenge( client_t *cl, const challenge_t *challenge ) {
	if ( !cl || !challenge || challenge->platformAuthTicketLength <= 0 ) {
		return qfalse;
	}

	SV_ClearPlatformAuthState( cl );

	if ( !QL_Steamworks_HexEncode( challenge->platformAuthTicket,
		(uint32_t)challenge->platformAuthTicketLength,
		cl->platformAuthToken, sizeof( cl->platformAuthToken ) ) ) {
		return qfalse;
	}

	SV_FormatPlatformSteamIdWords( challenge->platformSteamIdLow, challenge->platformSteamIdHigh,
		cl->platformSteamId, sizeof( cl->platformSteamId ) );
	Q_strncpyz( cl->platformAuthLabel, "steam", sizeof( cl->platformAuthLabel ) );
	cl->platformAuthPending = qtrue;
	Q_strncpyz( cl->platformAuthResult, "pending", sizeof( cl->platformAuthResult ) );
	cl->platformAuthOutcome[0] = '\0';
	cl->platformAuthMessage[0] = '\0';
	return qtrue;
}

/*
=================
SV_CapturePlatformAuthFromUserinfo

Captures the SteamID and auth ticket fragments supplied by the client.
=================
*/
static void SV_CapturePlatformAuthFromUserinfo( client_t *cl, const char *userinfo ) {
	const char	*steamId;
	const char	*auth;
	const char	*authPart1;
	const char	*authPart2;
	char		combined[QL_AUTH_MAX_CREDENTIAL_STORAGE];

	if ( !cl || !userinfo ) {
		return;
	}

	SV_ClearPlatformAuthState( cl );

	steamId = Info_ValueForKey( userinfo, "steamid" );
	auth = Info_ValueForKey( userinfo, "auth" );
	authPart1 = Info_ValueForKey( userinfo, "author" );
	authPart2 = Info_ValueForKey( userinfo, "author2" );

	combined[0] = '\0';

	if ( auth && auth[0] ) {
		Q_strncpyz( combined, auth, sizeof( combined ) );
	} else {
		if ( authPart1 && authPart1[0] ) {
			Q_strncpyz( combined, authPart1, sizeof( combined ) );
		}

		if ( authPart2 && authPart2[0] ) {
			Q_strcat( combined, sizeof( combined ), authPart2 );
		}
	}

	if ( steamId && steamId[0] ) {
		Q_strncpyz( cl->platformSteamId, steamId, sizeof( cl->platformSteamId ) );

		if ( !cl->platformAuthLabel[0] ) {
			Q_strncpyz( cl->platformAuthLabel, "steam", sizeof( cl->platformAuthLabel ) );
		}
	}

	if ( combined[0] ) {
		Q_strncpyz( cl->platformAuthToken, combined, sizeof( cl->platformAuthToken ) );
		Q_strncpyz( cl->platformAuthLabel, "steam", sizeof( cl->platformAuthLabel ) );
		cl->platformAuthPending = qtrue;
		Q_strncpyz( cl->platformAuthResult, "pending", sizeof( cl->platformAuthResult ) );
		cl->platformAuthOutcome[0] = '\0';
	}
}

/*
=================
SV_FinalisePlatformAuthState

Copies the final userinfo-visible auth fields back into the retained client slot.
=================
*/
static void SV_FinalisePlatformAuthState( client_t *cl, qboolean accepted, const char *detail ) {
	const char	*result;
	const char	*outcome;
	const char	*message;

	if ( !cl ) {
		return;
	}

	cl->platformAuthPending = qfalse;
	cl->platformAuthSucceeded = accepted;

	result = Info_ValueForKey( cl->userinfo, QL_AUTH_USERINFO_KEY_RESULT );
	outcome = Info_ValueForKey( cl->userinfo, QL_AUTH_USERINFO_KEY_OUTCOME );
	message = Info_ValueForKey( cl->userinfo, QL_AUTH_USERINFO_KEY_MESSAGE );

	if ( result && result[0] ) {
		Q_strncpyz( cl->platformAuthResult, result, sizeof( cl->platformAuthResult ) );
	} else {
		cl->platformAuthResult[0] = '\0';
	}

	if ( outcome && outcome[0] ) {
		Q_strncpyz( cl->platformAuthOutcome, outcome, sizeof( cl->platformAuthOutcome ) );
	} else {
		cl->platformAuthOutcome[0] = '\0';
	}

	if ( message && message[0] ) {
		Q_strncpyz( cl->platformAuthMessage, message, sizeof( cl->platformAuthMessage ) );
	} else if ( detail && detail[0] ) {
		Q_strncpyz( cl->platformAuthMessage, detail, sizeof( cl->platformAuthMessage ) );
	} else {
		cl->platformAuthMessage[0] = '\0';
	}
}

/*
=================
SV_BuildPlatformAuthCompatibilityDetail

Builds the final server-auth telemetry detail with explicit compatibility
provider and policy labels.
=================
*/
static void SV_BuildPlatformAuthCompatibilityDetail( const char *detail, char *buffer, int bufferSize ) {
	const char	*provider;
	const char	*policy;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	provider = SV_GetPlatformAuthProviderLabel();
	policy = SV_GetPlatformAuthPolicyLabel();
	buffer[0] = '\0';

	if ( detail && detail[0] ) {
		Q_strncpyz( buffer, detail, bufferSize );
		Q_strcat( buffer, bufferSize, " | " );
	}

	Q_strcat( buffer, bufferSize, "provider=" );
	Q_strcat( buffer, bufferSize, provider && provider[0] ? provider : "Unavailable" );
	Q_strcat( buffer, bufferSize, " policy=" );
	Q_strcat( buffer, bufferSize, policy && policy[0] ? policy : "compatibility-unavailable" );
}

/*
=================
SV_LogPlatformAuthConnectRejected

Publishes provider-aware diagnostics whenever the retained server-auth
bootstrap rejects a connection under the compatibility policy.
=================
*/
static void SV_LogPlatformAuthConnectRejected( const char *detail ) {
	Com_DPrintf( "Server auth rejected connection via %s [%s]: %s\n",
		SV_GetPlatformAuthProviderLabel(), SV_GetPlatformAuthPolicyLabel(),
		detail ? detail : "no detail" );
}

/*
=================
SV_LogPlatformAuth

Emits one unified telemetry record for the server-side auth owner.
=================
*/
static void SV_LogPlatformAuth( const netadr_t *adr, const client_t *cl, const char *status, const char *detail ) {
	char		detailMessage[QL_AUTH_MAX_RESPONSE_MESSAGE * 2];
	char		message[QL_AUTH_MAX_RESPONSE_MESSAGE * 2];
	const char	*label;
	const char	*steamId;
	const char	*result;
	const char	*outcome;

	detailMessage[0] = '\0';
	message[0] = '\0';

	if ( !cl ) {
		return;
	}

	label = cl->platformAuthLabel[0] ? cl->platformAuthLabel : NULL;
	steamId = cl->platformSteamId[0] ? cl->platformSteamId : NULL;
	result = cl->platformAuthResult[0] ? cl->platformAuthResult : NULL;
	outcome = cl->platformAuthOutcome[0] ? cl->platformAuthOutcome : NULL;

	if ( detail && detail[0] ) {
		Q_strncpyz( detailMessage, detail, sizeof( detailMessage ) );
	}

	if ( cl->platformAuthMessage[0] ) {
		if ( !detailMessage[0] ) {
			Q_strncpyz( detailMessage, cl->platformAuthMessage, sizeof( detailMessage ) );
		} else if ( Q_stricmp( detailMessage, cl->platformAuthMessage ) ) {
			Q_strcat( detailMessage, sizeof( detailMessage ), " | " );
			Q_strcat( detailMessage, sizeof( detailMessage ), cl->platformAuthMessage );
		}
	}

	SV_BuildPlatformAuthCompatibilityDetail( detailMessage[0] ? detailMessage : NULL, message, sizeof( message ) );
	NET_LogAuthTelemetry( NS_SERVER, adr, steamId, label, status, result, outcome, message[0] ? message : NULL );
}

/*
=================
SV_ParsePlatformSteamId

Parses a numeric SteamID string into the compact runtime form.
=================
*/
static qboolean SV_ParsePlatformSteamId( const char *steamIdString, CSteamID *steamId ) {
	unsigned long long	value;
	const char		*ch;

	if ( !steamId ) {
		return qfalse;
	}

	steamId->value = 0ull;

	if ( !steamIdString || !steamIdString[0] ) {
		return qfalse;
	}

	value = 0ull;

	for ( ch = steamIdString; *ch; ch++ ) {
		if ( *ch < '0' || *ch > '9' ) {
			return qfalse;
		}

		if ( value > ( ULLONG_MAX / 10ull ) ) {
			return qfalse;
		}

		value *= 10ull;

		if ( value > ( ULLONG_MAX - (unsigned long long)( *ch - '0' ) ) ) {
			return qfalse;
		}

		value += (unsigned long long)( *ch - '0' );
	}

	steamId->value = (uint64_t)value;
	return qtrue;
}

/*
=================
SV_SetPlatformAuthUserinfo

Writes the current auth telemetry triplet into the client's userinfo.
=================
*/
static void SV_SetPlatformAuthUserinfo( client_t *cl, const char *result, const char *outcome, const char *message ) {
	if ( !cl ) {
		return;
	}

	Info_SetValueForKey( cl->userinfo, QL_AUTH_USERINFO_KEY_RESULT, result ? result : "" );
	Info_SetValueForKey( cl->userinfo, QL_AUTH_USERINFO_KEY_OUTCOME, outcome ? outcome : "" );
	Info_SetValueForKey( cl->userinfo, QL_AUTH_USERINFO_KEY_MESSAGE, message ? message : "" );
}

/*
=================
SV_FormatPlatformAuthCode

Formats a Steam auth response code for userinfo and telemetry publication.
=================
*/
static void SV_FormatPlatformAuthCode( EAuthSessionResponse response, char *buffer, size_t bufferSize ) {
	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	Com_sprintf( buffer, (int)bufferSize, "%d", (int)response );
}

/*
=================
SV_GetPlatformAuthReason

Maps Steam auth callback responses to the retail-facing reason labels.
=================
*/
static const char *SV_GetPlatformAuthReason( EAuthSessionResponse response ) {
	switch ( response ) {
		case k_EAuthSessionResponseOK:
		return "accepted";
		case k_EAuthSessionResponseUserNotConnectedToSteam:
		return "User not connected to Steam";
		case k_EAuthSessionResponseNoLicenseOrExpired:
		return "No license or expired";
		case k_EAuthSessionResponseVACBanned:
		return "VAC ban on record";
		case k_EAuthSessionResponseLoggedInElseWhere:
		return "Logged in elsewhere";
		case k_EAuthSessionResponseVACCheckTimedOut:
		return "VAC check timed out";
		case k_EAuthSessionResponseAuthTicketCanceled:
		return "Issuer canceled auth ticket";
		case k_EAuthSessionResponseAuthTicketInvalidAlreadyUsed:
		return "Auth ticket already used";
		case k_EAuthSessionResponseAuthTicketInvalid:
		return "Auth ticket invalid";
		case k_EAuthSessionResponsePublisherIssuedBan:
		return "Game ban on record";
		default:
		return "Unknown Steam auth failure";
	}
}

/*
=================
SV_IsPlatformAuthAccepted

Matches the retail callback accept list for Steam auth responses.
=================
*/
static qboolean SV_IsPlatformAuthAccepted( EAuthSessionResponse response ) {
	return ( response == k_EAuthSessionResponseOK || response == k_EAuthSessionResponseAuthTicketCanceled ) ? qtrue : qfalse;
}

/*
=================
SV_BuildPlatformAuthMessage

Builds the outward-facing auth message for one callback response.
=================
*/
static void SV_BuildPlatformAuthMessage( EAuthSessionResponse response, char *buffer, size_t bufferSize ) {
	const char *reason;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	reason = SV_GetPlatformAuthReason( response );

	if ( SV_IsPlatformAuthAccepted( response ) ) {
		Q_strncpyz( buffer, reason, bufferSize );
		return;
	}

	Com_sprintf( buffer, (int)bufferSize, "Failed to authenticate with Steam: %s", reason );
}

/*
=================
SV_SteamStats_ResetSession

Clears one retained server-owned Steam stats session.
=================
*/
static void SV_SteamStats_ResetSession( sv_steam_stats_session_t *session ) {
	CSteamID steamId;

	if ( !session ) {
		SV_LogSteamStatsLifecycle( NULL, "session-reset", "ignored reset for null session" );
		return;
	}

	steamId = session->steamId;
	if ( session->active || steamId.value != 0ull || session->requestIssued || session->backendAvailable ) {
		SV_LogSteamStatsLifecycle( steamId.value != 0ull ? &steamId : NULL,
			"session-reset", "cleared retained session state" );
	}

	Com_Memset( session, 0, sizeof( *session ) );
}

/*
=================
SV_SteamStats_GetFieldTypeLabel

Names one retail Steam stat descriptor type for diagnostics.
=================
*/
static const char *SV_SteamStats_GetFieldTypeLabel( sv_steam_stat_type_t type ) {
	switch ( type ) {
		case SV_STEAM_STAT_INT:
			return "int";
		case SV_STEAM_STAT_FLOAT:
			return "float";
		case SV_STEAM_STAT_AVG_RATE:
			return "avg-rate";
		default:
			return "unknown";
	}
}

/*
=================
SV_SteamStats_GetFieldDescriptor

Returns the mapped retail Steam stat descriptor for one field index while
labeling invalid or unmapped lookups through the shared stats lifecycle logger.
=================
*/
static const sv_steam_stat_descriptor_t *SV_SteamStats_GetFieldDescriptor( int statIndex, const char *stage ) {
	const char *lookupStage;
	const sv_steam_stat_descriptor_t *descriptor;
	char detail[128];

	lookupStage = stage ? stage : "descriptor-lookup";
	if ( statIndex < 0 || statIndex >= SV_STEAM_STATS_FIELD_COUNT ) {
		Com_sprintf( detail, sizeof( detail ), "ignored stat descriptor lookup for invalid index %d", statIndex );
		SV_LogSteamStatsLifecycle( NULL, lookupStage, detail );
		return NULL;
	}

	descriptor = &s_svSteamStatDescriptors[statIndex];
	if ( !descriptor->name ) {
		Com_sprintf( detail, sizeof( detail ), "ignored stat descriptor lookup for unmapped index %d", statIndex );
		SV_LogSteamStatsLifecycle( NULL, lookupStage, detail );
		return NULL;
	}

	return descriptor;
}

/*
=================
SV_SteamStats_GetFieldName

Returns the mapped retail Steam stat descriptor name for one field index while
labeling invalid or unmapped descriptor lookups through the shared stats
lifecycle logger.
=================
*/
static const char *SV_SteamStats_GetFieldName( int statIndex, const char *stage ) {
	const sv_steam_stat_descriptor_t *descriptor;

	descriptor = SV_SteamStats_GetFieldDescriptor( statIndex, stage );
	return descriptor ? descriptor->name : NULL;
}

/*
=================
SV_SteamStats_GetMedalStatIndex

Maps a recovered `PLAYER_MEDAL` token to the retail medal stat index table at
`data_561b80`/`data_561b84`, with narrow aliases for source-side medal names.
=================
*/
static int SV_SteamStats_GetMedalStatIndex( const char *medalName ) {
	int i;

	if ( !medalName || !medalName[0] ) {
		return -1;
	}

	for ( i = 0; i < (int)( sizeof( s_svSteamMedalStatMap ) / sizeof( s_svSteamMedalStatMap[0] ) ); i++ ) {
		if ( !strcmp( medalName, s_svSteamMedalStatMap[i].medalName ) ) {
			return s_svSteamMedalStatMap[i].statIndex;
		}
	}

	if ( !Q_stricmp( medalName, "HUMILIATION" ) ) {
		return SV_STEAM_STAT_MEDAL_GAUNTLET;
	}
	if ( !Q_stricmp( medalName, "DEFENDS" ) || !Q_stricmp( medalName, "DEFEND" ) ) {
		return SV_STEAM_STAT_MEDAL_DEFENSE;
	}
	if ( !Q_stricmp( medalName, "ASSISTS" ) ) {
		return SV_STEAM_STAT_MEDAL_ASSIST;
	}
	if ( !Q_stricmp( medalName, "CAPTURES" ) ) {
		return SV_STEAM_STAT_MEDAL_CAPTURE;
	}

	return -1;
}

/*
=================
SV_SteamStats_GetAchievementName

Returns the mapped retail Steam achievement name for one achievement index while
labeling invalid or unmapped descriptor lookups through the shared stats
lifecycle logger.
=================
*/
static const char *SV_SteamStats_GetAchievementName( int achievementId, const char *stage ) {
	const char *lookupStage;
	const char *name;
	char detail[128];

	lookupStage = stage ? stage : "descriptor-lookup";
	if ( achievementId < 0 || achievementId >= SV_STEAM_ACHIEVEMENT_COUNT ) {
		Com_sprintf( detail, sizeof( detail ), "ignored achievement descriptor lookup for invalid id %d", achievementId );
		SV_LogSteamStatsLifecycle( NULL, lookupStage, detail );
		return NULL;
	}

	name = s_svSteamAchievementNames[achievementId];
	if ( !name ) {
		Com_sprintf( detail, sizeof( detail ), "ignored achievement descriptor lookup for unmapped id %d", achievementId );
		SV_LogSteamStatsLifecycle( NULL, lookupStage, detail );
		return NULL;
	}

	return name;
}

/*
=================
SV_SteamStats_GetClientSlot

Returns the retained client slot for a stats/achievement request when it is live
and not a bot-owned surrogate.
=================
*/
static client_t *SV_SteamStats_GetClientSlot( int clientNum, const char *stage, const char *subject ) {
	client_t *cl;
	CSteamID steamId;
	char detail[128];
	const char *label;

	label = subject ? subject : "stats request";

	if ( clientNum < 0 || clientNum >= sv_maxclients->integer ) {
		Com_sprintf( detail, sizeof( detail ), "%s unavailable for out-of-range client %d", label, clientNum );
		SV_LogSteamStatsLifecycle( NULL, stage, detail );
		return NULL;
	}

	cl = &svs.clients[clientNum];
	if ( cl->state < CS_CONNECTED ) {
		Com_sprintf( detail, sizeof( detail ), "%s unavailable for inactive client %d", label, clientNum );
		SV_LogSteamStatsLifecycle( NULL, stage, detail );
		return NULL;
	}

	if ( cl->state == CS_ZOMBIE ) {
		Com_sprintf( detail, sizeof( detail ), "%s unavailable for zombie client %d", label, clientNum );
		SV_LogSteamStatsLifecycle( NULL, stage, detail );
		return NULL;
	}

	if ( !cl->gentity ) {
		Com_sprintf( detail, sizeof( detail ), "%s unavailable for client %d without gentity", label, clientNum );
		SV_LogSteamStatsLifecycle( NULL, stage, detail );
		return NULL;
	}

	if ( !cl->platformSteamId[0] ) {
		Com_sprintf( detail, sizeof( detail ), "%s unavailable for client %d without steam id", label, clientNum );
		SV_LogSteamStatsLifecycle( NULL, stage, detail );
		return NULL;
	}

	if ( SV_ClientIsBot( cl ) || ( cl->gentity->r.svFlags & SVF_BOT ) ) {
		Com_sprintf( detail, sizeof( detail ), "%s unavailable for bot-owned client %d", label, clientNum );
		SV_LogSteamStatsLifecycle( NULL, stage, detail );
		return NULL;
	}

	if ( !SV_ParsePlatformSteamId( cl->platformSteamId, &steamId ) || steamId.value == 0ull ) {
		Com_sprintf( detail, sizeof( detail ), "%s unavailable for client %d with invalid steam id", label, clientNum );
		SV_LogSteamStatsLifecycle( NULL, stage, detail );
		return NULL;
	}

	return cl;
}

/*
=================
SV_SteamStats_FindSessionBySteamId

Finds the retained stats session for one Steam GameServerStats callback.
=================
*/
static sv_steam_stats_session_t *SV_SteamStats_FindSessionBySteamId( const CSteamID *steamId ) {
	sv_steam_stats_session_t *session;
	int i;

	if ( !steamId || steamId->value == 0ull ) {
		return NULL;
	}

	for ( i = 0; i < sv_maxclients->integer && i < MAX_CLIENTS; i++ ) {
		session = &sv_steamStatsSessions[i];
		if ( !session->active ) {
			continue;
		}

		if ( session->steamId.value == steamId->value ) {
			return session;
		}
	}

	return NULL;
}

/*
=================
SV_LogSteamStatsLifecycle

Publishes provider-aware diagnostics for the retained dedicated-server stats
compatibility lane.
=================
*/
static void SV_LogSteamStatsLifecycle( const CSteamID *steamId, const char *stage, const char *detail ) {
	unsigned long long remoteId;

	remoteId = steamId ? (unsigned long long)steamId->value : 0ull;
	Com_DPrintf( "Server stats %s for %llu via %s [%s]: %s\n",
		stage ? stage : "update",
		remoteId,
		SV_GetServerStatsProviderLabel(), SV_GetServerStatsPolicyLabel(),
		detail ? detail : "no detail" );
}

/*
=================
SV_SteamStats_RequestCurrentValues

Reissues the retail SteamGameServerStats request for one active player session.
=================
*/
static qboolean SV_SteamStats_RequestCurrentValues( sv_steam_stats_session_t *session ) {
	if ( !session ) {
		SV_LogSteamStatsLifecycle( NULL, "request-current-values", "ignored request for null session" );
		return qfalse;
	}

	if ( !session->active ) {
		SV_LogSteamStatsLifecycle( &session->steamId, "request-current-values", "ignored request for inactive session" );
		return qfalse;
	}

	if ( session->steamId.value == 0ull ) {
		SV_LogSteamStatsLifecycle( NULL, "request-current-values", "ignored request for session without steam id" );
		return qfalse;
	}

	session->requestIssued = qfalse;
	if ( !QL_Steamworks_ServerRequestUserStats( &session->steamId ) ) {
		SV_LogSteamStatsLifecycle( &session->steamId, "request-current-values", "request failed" );
		return qfalse;
	}

	session->requestIssued = qtrue;
	SV_LogSteamStatsLifecycle( &session->steamId, "request-current-values", "request issued" );
	return qtrue;
}

/*
=================
SV_SteamStats_LoadFieldValue

Loads one stat value from SteamGameServerStats when the backend is available.
=================
*/
static qboolean SV_SteamStats_LoadFieldValue( sv_steam_stats_session_t *session, int statIndex ) {
	const sv_steam_stat_descriptor_t *descriptor;
	const char *name;
	char detail[128];
	int value;
	float floatValue;

	if ( !session ) {
		Com_sprintf( detail, sizeof( detail ), "ignored stat query for null session at index %d", statIndex );
		SV_LogSteamStatsLifecycle( NULL, "value-query", detail );
		return qfalse;
	}

	if ( !session->active ) {
		Com_sprintf( detail, sizeof( detail ), "ignored stat query for inactive session at index %d", statIndex );
		SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
		return qfalse;
	}

	if ( statIndex < 0 || statIndex >= SV_STEAM_STATS_FIELD_COUNT ) {
		Com_sprintf( detail, sizeof( detail ), "ignored stat query for invalid index %d", statIndex );
		SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
		return qfalse;
	}

	descriptor = SV_SteamStats_GetFieldDescriptor( statIndex, "value-query" );
	if ( !descriptor ) {
		Com_sprintf( detail, sizeof( detail ), "ignored stat query for unmapped index %d", statIndex );
		SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
		return qfalse;
	}
	name = descriptor->name;

	if ( session->statLoaded[statIndex] ) {
		if ( descriptor->type == SV_STEAM_STAT_INT ) {
			Com_sprintf( detail, sizeof( detail ), "stat %s already cached as %d", name, session->statValue[statIndex] );
		} else {
			Com_sprintf( detail, sizeof( detail ), "stat %s already cached as %.3f", name, session->statFloatValue[statIndex] );
		}
		SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
		return qtrue;
	}

	if ( !session->requestIssued ) {
		SV_SteamStats_RequestCurrentValues( session );
	}

	if ( !session->backendAvailable ) {
		Com_sprintf( detail, sizeof( detail ), "stat %s unavailable pending stats response", name );
		SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
		return qfalse;
	}

	session->statQueryAttempted[statIndex] = qtrue;

	switch ( descriptor->type ) {
		case SV_STEAM_STAT_INT:
			value = 0;
			if ( !QL_Steamworks_ServerGetUserStatInt( &session->steamId, name, &value ) ) {
				Com_sprintf( detail, sizeof( detail ), "stat %s query failed", name );
				SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
				return qfalse;
			}
			session->statValue[statIndex] = value + session->pendingStatDelta[statIndex];
			Com_sprintf( detail, sizeof( detail ), "stat %s loaded as %d", name, session->statValue[statIndex] );
			break;
		case SV_STEAM_STAT_FLOAT:
			floatValue = 0.0f;
			if ( !QL_Steamworks_ServerGetUserStatFloat( &session->steamId, name, &floatValue ) ) {
				Com_sprintf( detail, sizeof( detail ), "float stat %s query failed", name );
				SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
				return qfalse;
			}
			session->statFloatValue[statIndex] = floatValue + session->pendingStatFloatDelta[statIndex];
			Com_sprintf( detail, sizeof( detail ), "float stat %s loaded as %.3f", name, session->statFloatValue[statIndex] );
			break;
		case SV_STEAM_STAT_AVG_RATE:
			floatValue = 0.0f;
			if ( !QL_Steamworks_ServerGetUserStatFloat( &session->steamId, name, &floatValue ) ) {
				Com_sprintf( detail, sizeof( detail ), "avg-rate stat %s query failed", name );
				SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
				return qfalse;
			}
			session->statFloatValue[statIndex] = floatValue;
			Com_sprintf( detail, sizeof( detail ), "avg-rate stat %s loaded as %.3f", name, session->statFloatValue[statIndex] );
			break;
		default:
			Com_sprintf( detail, sizeof( detail ), "stat %s has unsupported descriptor type %d", name, (int)descriptor->type );
			SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
			return qfalse;
	}

	session->backendAvailable = qtrue;
	session->statLoaded[statIndex] = qtrue;
	SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
	return qtrue;
}

/*
=================
SV_SteamStats_LoadAchievement

Loads one achievement bit from SteamGameServerStats when the backend is available.
=================
*/
static qboolean SV_SteamStats_LoadAchievement( sv_steam_stats_session_t *session, int achievementId ) {
	const char *name;
	char detail[128];
	qboolean achieved;

	if ( !session ) {
		Com_sprintf( detail, sizeof( detail ), "ignored achievement query for null session at id %d", achievementId );
		SV_LogSteamStatsLifecycle( NULL, "value-query", detail );
		return qfalse;
	}

	if ( !session->active ) {
		Com_sprintf( detail, sizeof( detail ), "ignored achievement query for inactive session at id %d", achievementId );
		SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
		return qfalse;
	}

	if ( achievementId < 0 || achievementId >= SV_STEAM_ACHIEVEMENT_COUNT ) {
		Com_sprintf( detail, sizeof( detail ), "ignored achievement query for invalid id %d", achievementId );
		SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
		return qfalse;
	}

	name = SV_SteamStats_GetAchievementName( achievementId, "value-query" );
	if ( !name ) {
		Com_sprintf( detail, sizeof( detail ), "ignored achievement query for unmapped id %d", achievementId );
		SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
		return qfalse;
	}

	if ( session->achievementLoaded[achievementId] ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s already cached as %s",
			name, session->achievementUnlocked[achievementId] ? "unlocked" : "locked" );
		SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
		return qtrue;
	}

	if ( !session->requestIssued ) {
		SV_SteamStats_RequestCurrentValues( session );
	}

	if ( !session->backendAvailable ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s unavailable pending stats response", name );
		SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
		return qfalse;
	}

	session->achievementQueryAttempted[achievementId] = qtrue;
	achieved = qfalse;
	if ( !QL_Steamworks_ServerGetUserAchievement( &session->steamId, name, &achieved ) ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s query failed", name );
		SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
		return qfalse;
	}

	session->backendAvailable = qtrue;
	session->achievementLoaded[achievementId] = qtrue;
	session->achievementUnlocked[achievementId] = ( session->achievementUnlocked[achievementId] || achieved ) ? qtrue : qfalse;
	Com_sprintf( detail, sizeof( detail ), "achievement %s loaded as %s",
		name, session->achievementUnlocked[achievementId] ? "unlocked" : "locked" );
	SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
	return qtrue;
}

/*
=================
SV_SteamStats_PrimeReceivedValues

Refreshes mapped stat baselines after Steam reports that current values are
available.
=================
*/
static void SV_SteamStats_PrimeReceivedValues( sv_steam_stats_session_t *session ) {
	int i;

	if ( !session || !session->active ) {
		return;
	}

	session->backendAvailable = qtrue;
	session->requestIssued = qtrue;
	for ( i = 0; i < SV_STEAM_STATS_FIELD_COUNT; i++ ) {
		session->statLoaded[i] = qfalse;
		SV_SteamStats_LoadFieldValue( session, i );
	}
}

/*
=================
SV_SteamStats_FlushPendingValues

Publishes pending stat deltas and achievement unlocks for one active session.
=================
*/
static void SV_SteamStats_FlushPendingValues( sv_steam_stats_session_t *session, qboolean forceStore ) {
	const sv_steam_stat_descriptor_t *descriptor;
	const char *name;
	qboolean hasPending;
	qboolean failed;
	char detail[128];
	int pendingStats;
	int pendingAchievements;
	int i;
	float floatValue;

	if ( !session ) {
		SV_LogSteamStatsLifecycle( NULL, "value-flush", "ignored flush for null session" );
		return;
	}

	if ( !session->active ) {
		SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", "ignored flush for inactive session" );
		return;
	}

	if ( session->steamId.value == 0ull ) {
		SV_LogSteamStatsLifecycle( NULL, "value-flush", "ignored flush for session without steam id" );
		return;
	}

	hasPending = qfalse;
	failed = qfalse;
	pendingStats = 0;
	pendingAchievements = 0;

	for ( i = 0; i < SV_STEAM_STATS_FIELD_COUNT; i++ ) {
		if ( !session->statDirty[i] ) {
			continue;
		}

		hasPending = qtrue;
		pendingStats++;
		descriptor = SV_SteamStats_GetFieldDescriptor( i, "value-flush" );
		name = descriptor ? descriptor->name : NULL;
		if ( !descriptor ) {
			Com_sprintf( detail, sizeof( detail ), "stat %s publish failed", name ? name : "<unknown>" );
			SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", detail );
			failed = qtrue;
			continue;
		}
		if ( !session->statLoaded[i] && !SV_SteamStats_LoadFieldValue( session, i ) ) {
			Com_sprintf( detail, sizeof( detail ), "stat %s unavailable during flush", name );
			SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", detail );
			failed = qtrue;
			continue;
		}

		switch ( descriptor->type ) {
			case SV_STEAM_STAT_INT:
				if ( !QL_Steamworks_ServerSetUserStatInt( &session->steamId, name, session->statValue[i] ) ) {
					Com_sprintf( detail, sizeof( detail ), "stat %s publish failed", name );
					SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", detail );
					failed = qtrue;
					continue;
				}
				break;
			case SV_STEAM_STAT_FLOAT:
				if ( !QL_Steamworks_ServerSetUserStatFloat( &session->steamId, name, session->statFloatValue[i] ) ) {
					Com_sprintf( detail, sizeof( detail ), "float stat %s publish failed", name );
					SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", detail );
					failed = qtrue;
					continue;
				}
				break;
			case SV_STEAM_STAT_AVG_RATE:
				if ( !QL_Steamworks_ServerUpdateAvgRateStat( &session->steamId, name, session->pendingAvgRateCount[i], session->pendingAvgRateSessionLength[i] ) ) {
					Com_sprintf( detail, sizeof( detail ), "avg-rate stat %s publish failed", name );
					SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", detail );
					failed = qtrue;
					continue;
				}
				floatValue = 0.0f;
				if ( QL_Steamworks_ServerGetUserStatFloat( &session->steamId, name, &floatValue ) ) {
					session->statFloatValue[i] = floatValue;
				}
				break;
			default:
				Com_sprintf( detail, sizeof( detail ), "stat %s has unsupported descriptor type %d", name, (int)descriptor->type );
				SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", detail );
				failed = qtrue;
				continue;
		}

		session->backendAvailable = qtrue;
	}

	for ( i = 0; i < SV_STEAM_ACHIEVEMENT_COUNT; i++ ) {
		if ( !session->achievementDirty[i] ) {
			continue;
		}

		hasPending = qtrue;
		name = SV_SteamStats_GetAchievementName( i, "value-flush" );
		pendingAchievements++;
		if ( !name || !QL_Steamworks_ServerSetUserAchievement( &session->steamId, name ) ) {
			Com_sprintf( detail, sizeof( detail ), "achievement %s publish failed", name ? name : "<unknown>" );
			SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", detail );
			failed = qtrue;
			continue;
		}

		session->backendAvailable = qtrue;
	}

	if ( !hasPending && !forceStore ) {
		SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", "no pending stat or achievement updates" );
		return;
	}

	if ( failed ) {
		Com_sprintf( detail, sizeof( detail ), "retained %d stat field(s) and %d achievement(s) after publish failure",
			pendingStats, pendingAchievements );
		SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", detail );
		return;
	}

	if ( !QL_Steamworks_ServerStoreUserStats( &session->steamId ) ) {
		SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", "store request failed" );
		return;
	}

	session->backendAvailable = qtrue;
	Com_sprintf( detail, sizeof( detail ), "stored %d stat field(s) and %d achievement(s)", pendingStats, pendingAchievements );
	SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", detail );

	for ( i = 0; i < SV_STEAM_STATS_FIELD_COUNT; i++ ) {
		if ( !session->statDirty[i] ) {
			continue;
		}

		session->statDirty[i] = qfalse;
		session->pendingStatDelta[i] = 0;
		session->pendingStatFloatDelta[i] = 0.0f;
		session->pendingAvgRateCount[i] = 0.0f;
		session->pendingAvgRateSessionLength[i] = 0.0;
	}

	for ( i = 0; i < SV_STEAM_ACHIEVEMENT_COUNT; i++ ) {
		if ( !session->achievementDirty[i] ) {
			continue;
		}

		session->achievementDirty[i] = qfalse;
	}
}

/*
=================
SV_SteamStats_SetAchievement

Sets one achievement through SteamGameServerStats and stores the active session
when the current-values response has primed the retail ready flag.
=================
*/
static qboolean SV_SteamStats_SetAchievement( sv_steam_stats_session_t *session, int achievementId ) {
	const char *name;
	char detail[128];

	if ( !session ) {
		Com_sprintf( detail, sizeof( detail ), "ignored achievement set for null session at id %d", achievementId );
		SV_LogSteamStatsLifecycle( NULL, "achievement-unlock", detail );
		return qfalse;
	}

	if ( !session->active ) {
		Com_sprintf( detail, sizeof( detail ), "ignored achievement set for inactive session at id %d", achievementId );
		SV_LogSteamStatsLifecycle( &session->steamId, "achievement-unlock", detail );
		return qfalse;
	}

	if ( session->steamId.value == 0ull ) {
		Com_sprintf( detail, sizeof( detail ), "ignored achievement set for session without steam id at id %d", achievementId );
		SV_LogSteamStatsLifecycle( NULL, "achievement-unlock", detail );
		return qfalse;
	}

	if ( achievementId < 0 || achievementId >= SV_STEAM_ACHIEVEMENT_COUNT ) {
		Com_sprintf( detail, sizeof( detail ), "ignored achievement set for invalid id %d", achievementId );
		SV_LogSteamStatsLifecycle( &session->steamId, "achievement-unlock", detail );
		return qfalse;
	}

	name = SV_SteamStats_GetAchievementName( achievementId, "achievement-unlock" );
	if ( !name ) {
		Com_sprintf( detail, sizeof( detail ), "ignored achievement set for unmapped id %d", achievementId );
		SV_LogSteamStatsLifecycle( &session->steamId, "achievement-unlock", detail );
		return qfalse;
	}

	if ( !session->backendAvailable ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s unavailable pending stats response", name );
		SV_LogSteamStatsLifecycle( &session->steamId, "achievement-unlock", detail );
		return qfalse;
	}

	if ( !QL_Steamworks_ServerSetUserAchievement( &session->steamId, name ) ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s publish failed", name );
		SV_LogSteamStatsLifecycle( &session->steamId, "achievement-unlock", detail );
		return qfalse;
	}

	session->backendAvailable = qtrue;
	SV_SteamStats_FlushPendingValues( session, qtrue );
	return qtrue;
}

/*
=================
SV_SteamStats_ShouldUnlockAchievement

Applies the recovered retail achievement gate around match state, training, and
practice flows.
=================
*/
static qboolean SV_SteamStats_ShouldUnlockAchievement( void ) {
	char gameState[MAX_STRING_CHARS];

	gameState[0] = '\0';
	Cvar_VariableStringBuffer( "g_gameState", gameState, sizeof( gameState ) );

	if ( !gameState[0] || !Q_stricmp( gameState, "IN_PROGRESS" ) ) {
		return qtrue;
	}

	if ( Cvar_VariableIntegerValue( "g_training" ) != 0 ) {
		return qtrue;
	}

	if ( Cvar_VariableIntegerValue( "practiceflags" ) != 0 ) {
		return qtrue;
	}

	return qfalse;
}

/*
=================
SV_SteamStats_ClearSummaryPeers

Clears the source-side mirror of retail `data_e30374`, the transient Steam
summary-recipient tree drained after a match-report broadcast.
=================
*/
static void SV_SteamStats_ClearSummaryPeers( void ) {
	if ( s_svSteamSummaryPeerCount <= 0 ) {
		return;
	}

	Com_Memset( s_svSteamSummaryPeers, 0, sizeof( s_svSteamSummaryPeers ) );
	s_svSteamSummaryPeerCount = 0;
}

/*
=================
SV_SteamStats_AddSummaryPeer

Tracks one SteamID as a pending recipient for the retained retail
match-report summary fanout.
=================
*/
static void SV_SteamStats_AddSummaryPeer( const CSteamID *steamId ) {
	sv_steam_stats_summary_peer_t *peer;
	char detail[128];
	int i;

	if ( !steamId || steamId->value == 0ull ) {
		SV_LogSteamStatsLifecycle( steamId, "match-summary-peer", "ignored peer without steam id" );
		return;
	}

	for ( i = 0; i < s_svSteamSummaryPeerCount; i++ ) {
		peer = &s_svSteamSummaryPeers[i];
		if ( peer->active && peer->steamId.value == steamId->value ) {
			return;
		}
	}

	if ( s_svSteamSummaryPeerCount >= SV_STEAM_STATS_SUMMARY_PEER_LIMIT ) {
		Com_sprintf( detail, sizeof( detail ), "ignored summary peer overflow at %d",
			s_svSteamSummaryPeerCount );
		SV_LogSteamStatsLifecycle( steamId, "match-summary-peer", detail );
		return;
	}

	peer = &s_svSteamSummaryPeers[s_svSteamSummaryPeerCount++];
	peer->active = qtrue;
	peer->steamId = *steamId;
	SV_LogSteamStatsLifecycle( steamId, "match-summary-peer", "tracked pending MATCH_REPORT summary peer" );
}

/*
=================
SV_SteamStats_SendSummaryToPeers

Broadcasts the prepared match-report summary through the retained
SteamGameServerNetworking wrapper, matching retail send type `2` on channel `0`.
=================
*/
static void SV_SteamStats_SendSummaryToPeers( const char *report ) {
	const sv_steam_stats_summary_peer_t *peer;
	size_t reportLength;
	char detail[128];
	int failed;
	int sent;
	int i;

	if ( s_svSteamSummaryPeerCount <= 0 ) {
		return;
	}

	if ( !report || !report[0] ) {
		SV_LogSteamStatsLifecycle( NULL, "match-summary", "cleared pending summary peers without report payload" );
		SV_SteamStats_ClearSummaryPeers();
		return;
	}

	reportLength = strlen( report );
	if ( reportLength == 0 ) {
		SV_LogSteamStatsLifecycle( NULL, "match-summary", "cleared pending summary peers for empty report payload" );
		SV_SteamStats_ClearSummaryPeers();
		return;
	}

	sent = 0;
	failed = 0;
	for ( i = 0; i < s_svSteamSummaryPeerCount; i++ ) {
		peer = &s_svSteamSummaryPeers[i];
		if ( !peer->active || peer->steamId.value == 0ull ) {
			continue;
		}

		if ( QL_Steamworks_ServerSendP2PPacket( &peer->steamId, report, (uint32_t)reportLength,
			SV_STEAM_STATS_SUMMARY_SEND_RELIABLE, SV_STEAM_STATS_SUMMARY_CHANNEL ) ) {
			sent++;
		} else {
			failed++;
		}
	}

	Com_sprintf( detail, sizeof( detail ),
		"sent MATCH_REPORT summary to %d peers (%d failed) on p2p channel %d",
		sent, failed, SV_STEAM_STATS_SUMMARY_CHANNEL );
	SV_LogSteamStatsLifecycle( NULL, "match-summary", detail );
	SV_SteamStats_ClearSummaryPeers();
}

/*
=================
SV_SteamStats_CreatePlayerSession

Creates or refreshes the retained retail-style Steam stats session for one
authenticated client slot.
=================
*/
static void SV_SteamStats_CreatePlayerSession( client_t *cl ) {
	sv_steam_stats_session_t *session;
	CSteamID steamId;
	char detail[128];
	int clientNum;

	if ( !cl ) {
		SV_LogSteamStatsLifecycle( NULL, "session-bootstrap", "ignored bootstrap for null client" );
		return;
	}

	clientNum = (int)( cl - svs.clients );
	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		Com_sprintf( detail, sizeof( detail ), "ignored bootstrap for out-of-range client %d", clientNum );
		SV_LogSteamStatsLifecycle( NULL, "session-bootstrap", detail );
		return;
	}

	if ( cl->state == CS_ZOMBIE ) {
		Com_sprintf( detail, sizeof( detail ), "ignored bootstrap for zombie client %d", clientNum );
		SV_LogSteamStatsLifecycle( NULL, "session-bootstrap", detail );
		return;
	}

	if ( !cl->gentity ) {
		Com_sprintf( detail, sizeof( detail ), "ignored bootstrap for client %d without gentity", clientNum );
		SV_LogSteamStatsLifecycle( NULL, "session-bootstrap", detail );
		return;
	}

	if ( !cl->platformSteamId[0] ) {
		Com_sprintf( detail, sizeof( detail ), "ignored bootstrap for client %d without steam id", clientNum );
		SV_LogSteamStatsLifecycle( NULL, "session-bootstrap", detail );
		return;
	}

	if ( SV_ClientIsBot( cl ) || ( cl->gentity->r.svFlags & SVF_BOT ) ) {
		Com_sprintf( detail, sizeof( detail ), "ignored bootstrap for bot-owned client %d", clientNum );
		SV_LogSteamStatsLifecycle( NULL, "session-bootstrap", detail );
		return;
	}

	if ( !SV_ParsePlatformSteamId( cl->platformSteamId, &steamId ) || steamId.value == 0ull ) {
		Com_sprintf( detail, sizeof( detail ), "ignored bootstrap for client %d with invalid steam id", clientNum );
		SV_LogSteamStatsLifecycle( NULL, "session-bootstrap", detail );
		return;
	}

	session = &sv_steamStatsSessions[clientNum];
	if ( session->active && session->steamId.value == steamId.value ) {
		SV_LogSteamStatsLifecycle( &session->steamId, "session-bootstrap", "reusing active session" );
		SV_SteamStats_AddSummaryPeer( &session->steamId );
		SV_SteamStats_RequestCurrentValues( session );
		return;
	}

	SV_SteamStats_ResetSession( session );
	session->active = qtrue;
	session->steamId = steamId;
	session->appId = QL_Steamworks_ServerGetAppID();
	SV_LogSteamStatsLifecycle( &session->steamId, "session-bootstrap", "created session" );
	SV_SteamStats_AddSummaryPeer( &session->steamId );
	SV_SteamStats_RequestCurrentValues( session );
	if ( !QL_Steamworks_ServerSendP2PPacket( &session->steamId, SV_STEAM_STATS_P2P_HELLO, 5, SV_STEAM_STATS_P2P_SEND_RELIABLE, SV_STEAM_STATS_P2P_CHANNEL ) ) {
		SV_LogSteamStatsLifecycle( &session->steamId, "session-bootstrap", "p2p hello send failed" );
	} else {
		SV_LogSteamStatsLifecycle( &session->steamId, "session-bootstrap", "p2p hello sent" );
	}
}

/*
=================
SV_SteamStats_RemovePlayerSession

Flushes and clears the retained Steam stats session for one client slot.
=================
*/
static void SV_SteamStats_RemovePlayerSession( client_t *cl ) {
	sv_steam_stats_session_t *session;
	CSteamID steamId;
	char detail[128];
	int clientNum;

	if ( !cl ) {
		return;
	}

	clientNum = (int)( cl - svs.clients );
	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return;
	}

	session = &sv_steamStatsSessions[clientNum];
	if ( !session->active ) {
		Com_sprintf( detail, sizeof( detail ), "session teardown skipped for inactive client %d", clientNum );
		SV_LogSteamStatsLifecycle( NULL, "session-teardown", detail );
		return;
	}

	steamId = session->steamId;
	SV_SteamStats_FlushPendingValues( session, qfalse );
	SV_SteamStats_ResetSession( session );
	Com_sprintf( detail, sizeof( detail ), "cleared session for client %d", clientNum );
	SV_LogSteamStatsLifecycle( &steamId, "session-teardown", detail );
}

/*
=================
SV_SteamStats_RequerySessions

Reissues Steam stats requests for active sessions after the GameServer backend
reconnects.
=================
*/
static void SV_SteamStats_RequerySessions( void ) {
	sv_steam_stats_session_t *session;
	int i;

	for ( i = 0; i < sv_maxclients->integer && i < MAX_CLIENTS; i++ ) {
		session = &sv_steamStatsSessions[i];
		if ( !session->active ) {
			continue;
		}

		session->requestIssued = qfalse;
		session->backendAvailable = qfalse;
		SV_LogSteamStatsLifecycle( &session->steamId, "session-requery", "backend reconnected; request reset" );
		SV_SteamStats_RequestCurrentValues( session );
	}
}

/*
=================
SV_SteamStats_AddFieldValue

Adds one mapped Steam stat delta for a live, non-bot client slot.
=================
*/
void SV_SteamStats_AddFieldValue( int clientNum, int statIndex, int delta ) {
	client_t *cl;
	sv_steam_stats_session_t *session;
	const sv_steam_stat_descriptor_t *descriptor;
	const char *name;
	char detail[128];
	char subject[128];

	if ( delta == 0 ) {
		Com_sprintf( detail, sizeof( detail ),
			"ignored stat index %d delta %d for client %d", statIndex, delta, clientNum );
		SV_LogSteamStatsLifecycle( NULL, "field-delta", detail );
		return;
	}

	descriptor = SV_SteamStats_GetFieldDescriptor( statIndex, "field-delta" );
	if ( !descriptor ) {
		Com_sprintf( detail, sizeof( detail ),
			"ignored stat index %d delta %d for client %d", statIndex, delta, clientNum );
		SV_LogSteamStatsLifecycle( NULL, "field-delta", detail );
		return;
	}
	name = descriptor->name;

	if ( descriptor->type != SV_STEAM_STAT_INT ) {
		Com_sprintf( detail, sizeof( detail ),
			"ignored non-int %s stat %s delta %d for client %d",
			SV_SteamStats_GetFieldTypeLabel( descriptor->type ), name, delta, clientNum );
		SV_LogSteamStatsLifecycle( NULL, "field-delta", detail );
		return;
	}

	Com_sprintf( subject, sizeof( subject ), "stat %s", name );
	cl = SV_SteamStats_GetClientSlot( clientNum, "field-delta", subject );
	if ( !cl ) {
		return;
	}

	SV_SteamStats_CreatePlayerSession( cl );
	session = &sv_steamStatsSessions[clientNum];
	if ( !session->active ) {
		Com_sprintf( detail, sizeof( detail ), "stat %s session unavailable for client %d", name, clientNum );
		SV_LogSteamStatsLifecycle( NULL, "field-delta", detail );
		return;
	}

	SV_SteamStats_LoadFieldValue( session, statIndex );
	if ( !session->statLoaded[statIndex] ) {
		Com_sprintf( detail, sizeof( detail ),
			"stat %s baseline unavailable; queuing delta %d for client %d", name, delta, clientNum );
		SV_LogSteamStatsLifecycle( &session->steamId, "field-delta", detail );
	}

	session->statValue[statIndex] += delta;
	session->pendingStatDelta[statIndex] += delta;
	session->statDirty[statIndex] = qtrue;

	Com_sprintf( detail, sizeof( detail ), "stat %s += %d -> %d for client %d", name, delta, session->statValue[statIndex], clientNum );
	SV_LogSteamStatsLifecycle( &session->steamId, "field-delta", detail );
}

/*
=================
SV_SteamStats_UnlockAchievement

Unlocks one mapped Steam achievement through the retained server-owned owner.
=================
*/
void SV_SteamStats_UnlockAchievement( int clientNum, int achievementId ) {
	client_t *cl;
	sv_steam_stats_session_t *session;
	const char *name;
	char detail[128];
	char subject[128];

	name = SV_SteamStats_GetAchievementName( achievementId, "achievement-unlock" );
	if ( !name ) {
		Com_sprintf( detail, sizeof( detail ), "ignored achievement %d for client %d", achievementId, clientNum );
		SV_LogSteamStatsLifecycle( NULL, "achievement-unlock", detail );
		return;
	}

	if ( !SV_SteamStats_ShouldUnlockAchievement() ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s blocked by gameplay gate for client %d", name, clientNum );
		SV_LogSteamStatsLifecycle( NULL, "achievement-unlock", detail );
		return;
	}

	Com_sprintf( subject, sizeof( subject ), "achievement %s", name );
	cl = SV_SteamStats_GetClientSlot( clientNum, "achievement-unlock", subject );
	if ( !cl ) {
		return;
	}

	SV_SteamStats_CreatePlayerSession( cl );
	session = &sv_steamStatsSessions[clientNum];
	if ( !session->active ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s session unavailable for client %d", name, clientNum );
		SV_LogSteamStatsLifecycle( NULL, "achievement-unlock", detail );
		return;
	}

	if ( !SV_SteamStats_SetAchievement( session, achievementId ) ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s publish failed for client %d", name, clientNum );
		SV_LogSteamStatsLifecycle( &session->steamId, "achievement-unlock", detail );
		return;
	}

	session->achievementUnlocked[achievementId] = qtrue;
	session->achievementLoaded[achievementId] = qtrue;
	Com_sprintf( detail, sizeof( detail ), "unlocked achievement %s for client %d", name, clientNum );
	SV_LogSteamStatsLifecycle( &session->steamId, "achievement-unlock", detail );
}

/*
=================
SV_SteamStats_HasAchievement

Reports whether the retained ready session already owns one mapped achievement.
=================
*/
qboolean SV_SteamStats_HasAchievement( int clientNum, int achievementId ) {
	client_t *cl;
	sv_steam_stats_session_t *session;
	const char *name;
	CSteamID steamId;
	char detail[128];
	char subject[128];

	name = SV_SteamStats_GetAchievementName( achievementId, "achievement-query" );
	if ( !name ) {
		Com_sprintf( detail, sizeof( detail ), "query unavailable for achievement %d on client %d", achievementId, clientNum );
		SV_LogSteamStatsLifecycle( NULL, "achievement-query", detail );
		return qfalse;
	}

	Com_sprintf( subject, sizeof( subject ), "achievement %s", name );
	cl = SV_SteamStats_GetClientSlot( clientNum, "achievement-query", subject );
	if ( !cl ) {
		return qfalse;
	}

	if ( !SV_ParsePlatformSteamId( cl->platformSteamId, &steamId ) || steamId.value == 0ull ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s session unavailable for client %d", name, clientNum );
		SV_LogSteamStatsLifecycle( NULL, "achievement-query", detail );
		return qfalse;
	}

	session = SV_SteamStats_FindSessionBySteamId( &steamId );
	if ( !session ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s session unavailable for client %d", name, clientNum );
		SV_LogSteamStatsLifecycle( NULL, "achievement-query", detail );
		return qfalse;
	}

	if ( !session->backendAvailable ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s unavailable pending stats response for client %d", name, clientNum );
		SV_LogSteamStatsLifecycle( &session->steamId, "achievement-query", detail );
		return qfalse;
	}

	Com_sprintf( detail, sizeof( detail ), "achievement %s ownership is %s for client %d",
		name, session->achievementUnlocked[achievementId] ? "present" : "absent", clientNum );
	SV_LogSteamStatsLifecycle( &session->steamId, "achievement-query", detail );
	return session->achievementUnlocked[achievementId] ? qtrue : qfalse;
}

/*
=================
SV_SteamStats_SkipEventPayloadWhitespace

Advances over JSON whitespace in the source-side qagame event payload proxy.
=================
*/
static const char *SV_SteamStats_SkipEventPayloadWhitespace( const char *cursor ) {
	if ( !cursor ) {
		return NULL;
	}

	while ( *cursor == ' ' || *cursor == '\t' || *cursor == '\r' || *cursor == '\n' ) {
		cursor++;
	}

	return cursor;
}

/*
=================
SV_SteamStats_FindEventPayloadFieldValue

Finds the value cursor for one flat field in the source-side qagame event
payload proxy.
=================
*/
static const char *SV_SteamStats_FindEventPayloadFieldValue( const char *payload, const char *fieldName ) {
	char key[64];
	const char *cursor;

	if ( !payload || !fieldName || !fieldName[0] ) {
		return NULL;
	}

	Com_sprintf( key, sizeof( key ), "\"%s\"", fieldName );
	cursor = strstr( payload, key );
	if ( !cursor ) {
		return NULL;
	}

	cursor += strlen( key );
	cursor = SV_SteamStats_SkipEventPayloadWhitespace( cursor );
	if ( !cursor || *cursor != ':' ) {
		return NULL;
	}

	cursor++;
	return SV_SteamStats_SkipEventPayloadWhitespace( cursor );
}

/*
=================
SV_SteamStats_ParseEventPayloadInt

Reads one flat integer field from the source-side JSON proxy used for qagame
ranking events.
=================
*/
static qboolean SV_SteamStats_ParseEventPayloadInt( const char *payload, const char *fieldName, int *outValue ) {
	char key[64];
	const char *cursor;
	int sign;
	int value;

	if ( outValue ) {
		*outValue = 0;
	}

	if ( !payload || !fieldName || !fieldName[0] || !outValue ) {
		return qfalse;
	}

	Com_sprintf( key, sizeof( key ), "\"%s\"", fieldName );
	cursor = strstr( payload, key );
	if ( !cursor ) {
		return qfalse;
	}

	cursor += strlen( key );
	while ( *cursor == ' ' || *cursor == '\t' || *cursor == '\r' || *cursor == '\n' ) {
		cursor++;
	}
	if ( *cursor != ':' ) {
		return qfalse;
	}

	cursor++;
	while ( *cursor == ' ' || *cursor == '\t' || *cursor == '\r' || *cursor == '\n' ) {
		cursor++;
	}

	sign = 1;
	if ( *cursor == '-' ) {
		sign = -1;
		cursor++;
	}

	if ( *cursor < '0' || *cursor > '9' ) {
		return qfalse;
	}

	value = 0;
	while ( *cursor >= '0' && *cursor <= '9' ) {
		if ( value > ( INT_MAX - ( *cursor - '0' ) ) / 10 ) {
			value = INT_MAX;
			break;
		}
		value = ( value * 10 ) + ( *cursor - '0' );
		cursor++;
	}

	*outValue = value * sign;
	return qtrue;
}

/*
=================
SV_SteamStats_ParseEventPayloadBool

Reads one flat boolean field from the source-side JSON proxy used for qagame
ranking events.
=================
*/
static qboolean SV_SteamStats_ParseEventPayloadBool( const char *payload, const char *fieldName, qboolean *outValue ) {
	const char *cursor;

	if ( outValue ) {
		*outValue = qfalse;
	}

	if ( !outValue ) {
		return qfalse;
	}

	cursor = SV_SteamStats_FindEventPayloadFieldValue( payload, fieldName );
	if ( !cursor ) {
		return qfalse;
	}

	if ( !strncmp( cursor, "true", 4 ) ) {
		*outValue = qtrue;
		return qtrue;
	}
	if ( !strncmp( cursor, "false", 5 ) ) {
		*outValue = qfalse;
		return qtrue;
	}
	if ( *cursor == '1' ) {
		*outValue = qtrue;
		return qtrue;
	}
	if ( *cursor == '0' ) {
		*outValue = qfalse;
		return qtrue;
	}

	return qfalse;
}

/*
=================
SV_SteamStats_ShouldSendMatchSummary

Mirrors the retail `SteamStats_BroadcastSummary` guard: send only when the
prepared match report explicitly has `TRAINING == false` and is not aborted.
=================
*/
static qboolean SV_SteamStats_ShouldSendMatchSummary( const char *report ) {
	qboolean aborted;
	qboolean training;

	if ( s_svSteamSummaryPeerCount <= 0 ) {
		return qfalse;
	}

	if ( !report || !report[0] ) {
		SV_LogSteamStatsLifecycle( NULL, "match-summary", "suppressed summary without report payload" );
		return qfalse;
	}

	if ( !SV_SteamStats_ParseEventPayloadBool( report, "TRAINING", &training ) ) {
		SV_LogSteamStatsLifecycle( NULL, "match-summary", "suppressed summary without TRAINING=false" );
		return qfalse;
	}

	if ( training ) {
		SV_LogSteamStatsLifecycle( NULL, "match-summary", "suppressed training MATCH_REPORT summary" );
		return qfalse;
	}

	if ( SV_SteamStats_ParseEventPayloadBool( report, "ABORTED", &aborted ) && aborted ) {
		SV_LogSteamStatsLifecycle( NULL, "match-summary", "suppressed aborted MATCH_REPORT summary" );
		return qfalse;
	}

	return qtrue;
}

/*
=================
SV_SteamStats_ParseEventPayloadString

Reads one flat string field from the source-side JSON proxy used for qagame
ranking events.
=================
*/
static qboolean SV_SteamStats_ParseEventPayloadString( const char *payload, const char *fieldName, char *outValue, size_t outSize ) {
	const char *cursor;
	char *write;
	size_t remaining;

	if ( outValue && outSize > 0 ) {
		outValue[0] = '\0';
	}

	if ( !outValue || outSize == 0 ) {
		return qfalse;
	}

	cursor = SV_SteamStats_FindEventPayloadFieldValue( payload, fieldName );
	if ( !cursor || *cursor != SV_STEAM_JSON_STRING_QUOTE ) {
		return qfalse;
	}

	cursor++;
	write = outValue;
	remaining = outSize;
	while ( *cursor && *cursor != SV_STEAM_JSON_STRING_QUOTE ) {
		int value;

		value = (unsigned char)*cursor;
		if ( value == SV_STEAM_JSON_ESCAPE && cursor[1] ) {
			cursor++;
			value = (unsigned char)*cursor;
		}
		if ( remaining > 1 ) {
			*write++ = (char)value;
			remaining--;
		}
		cursor++;
	}

	if ( *cursor != SV_STEAM_JSON_STRING_QUOTE ) {
		outValue[0] = '\0';
		return qfalse;
	}

	*write = '\0';
	return qtrue;
}

/*
=================
SV_SteamStats_FindNestedEventPayloadFieldValue

Finds the value cursor for one field inside a named object in the source-side
qagame event payload proxy.
=================
*/
static const char *SV_SteamStats_FindNestedEventPayloadFieldValue( const char *payload, const char *objectName, const char *fieldName ) {
	char fieldKey[64];
	const char *objectStart;
	const char *objectEnd;
	const char *field;
	const char *cursor;
	int depth;
	qboolean inString;
	qboolean escaped;

	objectStart = SV_SteamStats_FindEventPayloadFieldValue( payload, objectName );
	if ( !objectStart || *objectStart != SV_STEAM_JSON_OBJECT_OPEN ) {
		return NULL;
	}

	depth = 0;
	inString = qfalse;
	escaped = qfalse;
	for ( objectEnd = objectStart; *objectEnd; objectEnd++ ) {
		if ( inString ) {
			if ( escaped ) {
				escaped = qfalse;
			} else if ( *objectEnd == SV_STEAM_JSON_ESCAPE ) {
				escaped = qtrue;
			} else if ( *objectEnd == SV_STEAM_JSON_STRING_QUOTE ) {
				inString = qfalse;
			}
			continue;
		}

		if ( *objectEnd == SV_STEAM_JSON_STRING_QUOTE ) {
			inString = qtrue;
			continue;
		}
		if ( *objectEnd == SV_STEAM_JSON_OBJECT_OPEN ) {
			depth++;
			continue;
		}
		if ( *objectEnd == SV_STEAM_JSON_OBJECT_CLOSE ) {
			depth--;
			if ( depth == 0 ) {
				break;
			}
		}
	}

	if ( depth != 0 ) {
		return NULL;
	}

	Com_sprintf( fieldKey, sizeof( fieldKey ), "\"%s\"", fieldName );
	for ( field = objectStart; field && field < objectEnd; field = strstr( field + 1, fieldKey ) ) {
		field = strstr( field, fieldKey );
		if ( !field || field >= objectEnd ) {
			break;
		}

		cursor = field + strlen( fieldKey );
		cursor = SV_SteamStats_SkipEventPayloadWhitespace( cursor );
		if ( !cursor || cursor >= objectEnd || *cursor != ':' ) {
			continue;
		}

		cursor++;
		cursor = SV_SteamStats_SkipEventPayloadWhitespace( cursor );
		return ( cursor && cursor < objectEnd ) ? cursor : NULL;
	}

	return NULL;
}

/*
=================
SV_SteamStats_ParseNestedEventPayloadFloat

Reads one float field from a nested source-side qagame event payload object.
=================
*/
static qboolean SV_SteamStats_ParseNestedEventPayloadFloat( const char *payload, const char *objectName, const char *fieldName, float *outValue ) {
	const char *cursor;
	char *end;
	double value;

	if ( outValue ) {
		*outValue = 0.0f;
	}

	if ( !outValue ) {
		return qfalse;
	}

	cursor = SV_SteamStats_FindNestedEventPayloadFieldValue( payload, objectName, fieldName );
	if ( !cursor ) {
		return qfalse;
	}

	value = strtod( cursor, &end );
	if ( end == cursor ) {
		return qfalse;
	}

	*outValue = (float)value;
	return qtrue;
}

/*
=================
SV_SteamStats_ParseNestedEventPayloadInt

Reads one integer field from a nested source-side qagame event payload object.
=================
*/
static qboolean SV_SteamStats_ParseNestedEventPayloadInt( const char *payload, const char *objectName, const char *fieldName, int *outValue ) {
	const char *cursor;
	char *end;
	long value;

	if ( outValue ) {
		*outValue = 0;
	}

	if ( !outValue ) {
		return qfalse;
	}

	cursor = SV_SteamStats_FindNestedEventPayloadFieldValue( payload, objectName, fieldName );
	if ( !cursor ) {
		return qfalse;
	}

	value = strtol( cursor, &end, 10 );
	if ( end == cursor || value < INT_MIN || value > INT_MAX ) {
		return qfalse;
	}

	*outValue = (int)value;
	return qtrue;
}

/*
=================
SV_SteamStats_ParseNestedEventPayloadString

Reads one string field from a nested source-side qagame event payload object.
=================
*/
static qboolean SV_SteamStats_ParseNestedEventPayloadString( const char *payload, const char *objectName, const char *fieldName, char *outValue, size_t outSize ) {
	const char *cursor;
	char *write;
	size_t remaining;

	if ( outValue && outSize > 0 ) {
		outValue[0] = '\0';
	}

	if ( !outValue || outSize == 0 ) {
		return qfalse;
	}

	cursor = SV_SteamStats_FindNestedEventPayloadFieldValue( payload, objectName, fieldName );
	if ( !cursor || *cursor != SV_STEAM_JSON_STRING_QUOTE ) {
		return qfalse;
	}

	cursor++;
	write = outValue;
	remaining = outSize;
	while ( *cursor && *cursor != SV_STEAM_JSON_STRING_QUOTE ) {
		int value;

		value = (unsigned char)*cursor;
		if ( value == SV_STEAM_JSON_ESCAPE && cursor[1] ) {
			cursor++;
			value = (unsigned char)*cursor;
		}
		if ( remaining > 1 ) {
			*write++ = (char)value;
			remaining--;
		}
		cursor++;
	}

	if ( *cursor != SV_STEAM_JSON_STRING_QUOTE ) {
		outValue[0] = '\0';
		return qfalse;
	}

	*write = '\0';
	return qtrue;
}

/*
=================
SV_SteamStats_CopyNestedEventPayloadArray

Copies one nested JSON array value from the source-side qagame event payload.
=================
*/
static qboolean SV_SteamStats_CopyNestedEventPayloadArray( const char *payload, const char *objectName, const char *fieldName, char *outValue, size_t outSize ) {
	const char *cursor;
	const char *scan;
	size_t length;
	int depth;
	qboolean inString;
	qboolean escaped;

	if ( outValue && outSize > 0 ) {
		outValue[0] = '\0';
	}

	if ( !outValue || outSize == 0 ) {
		return qfalse;
	}

	cursor = SV_SteamStats_FindNestedEventPayloadFieldValue( payload, objectName, fieldName );
	if ( !cursor || *cursor != SV_STEAM_JSON_ARRAY_OPEN ) {
		return qfalse;
	}

	depth = 0;
	inString = qfalse;
	escaped = qfalse;
	for ( scan = cursor; *scan; scan++ ) {
		if ( inString ) {
			if ( escaped ) {
				escaped = qfalse;
			} else if ( *scan == SV_STEAM_JSON_ESCAPE ) {
				escaped = qtrue;
			} else if ( *scan == SV_STEAM_JSON_STRING_QUOTE ) {
				inString = qfalse;
			}
			continue;
		}

		if ( *scan == SV_STEAM_JSON_STRING_QUOTE ) {
			inString = qtrue;
			continue;
		}
		if ( *scan == SV_STEAM_JSON_ARRAY_OPEN ) {
			depth++;
			continue;
		}
		if ( *scan == SV_STEAM_JSON_ARRAY_CLOSE ) {
			depth--;
			if ( depth == 0 ) {
				length = (size_t)( scan - cursor ) + 1;
				if ( length >= outSize ) {
					return qfalse;
				}
				memcpy( outValue, cursor, length );
				outValue[length] = '\0';
				return qtrue;
			}
		}
	}

	return qfalse;
}

/*
=================
SV_SteamStats_AddSessionFieldValue

Applies one recovered `sub_467d40`-style integer stat delta to an existing
retained Steam stats session.
=================
*/
static qboolean SV_SteamStats_AddSessionFieldValue( sv_steam_stats_session_t *session, int statIndex, int delta, const char *stage ) {
	const sv_steam_stat_descriptor_t *descriptor;
	const char *name;
	const char *logStage;
	char detail[128];

	logStage = stage ? stage : "field-delta";
	descriptor = SV_SteamStats_GetFieldDescriptor( statIndex, logStage );
	if ( !descriptor ) {
		return qfalse;
	}
	name = descriptor->name;

	if ( !session ) {
		Com_sprintf( detail, sizeof( detail ), "ignored stat %s delta %d for null session", name, delta );
		SV_LogSteamStatsLifecycle( NULL, logStage, detail );
		return qfalse;
	}

	if ( !session->active ) {
		Com_sprintf( detail, sizeof( detail ), "ignored stat %s delta %d for inactive session", name, delta );
		SV_LogSteamStatsLifecycle( &session->steamId, logStage, detail );
		return qfalse;
	}

	if ( descriptor->type != SV_STEAM_STAT_INT ) {
		Com_sprintf( detail, sizeof( detail ), "ignored non-int %s stat %s delta %d",
			SV_SteamStats_GetFieldTypeLabel( descriptor->type ), name, delta );
		SV_LogSteamStatsLifecycle( &session->steamId, logStage, detail );
		return qfalse;
	}

	if ( delta == 0 ) {
		Com_sprintf( detail, sizeof( detail ), "stat %s += 0 skipped", name );
		SV_LogSteamStatsLifecycle( &session->steamId, logStage, detail );
		return qtrue;
	}

	SV_SteamStats_LoadFieldValue( session, statIndex );
	if ( !session->statLoaded[statIndex] ) {
		Com_sprintf( detail, sizeof( detail ), "stat %s baseline unavailable; queuing delta %d", name, delta );
		SV_LogSteamStatsLifecycle( &session->steamId, logStage, detail );
	}

	session->statValue[statIndex] += delta;
	session->pendingStatDelta[statIndex] += delta;
	session->statDirty[statIndex] = qtrue;

	Com_sprintf( detail, sizeof( detail ), "stat %s += %d -> %d", name, delta, session->statValue[statIndex] );
	SV_LogSteamStatsLifecycle( &session->steamId, logStage, detail );
	return qtrue;
}

/*
=================
SV_SteamStats_HasSessionAchievement

Reports whether one retained Steam stats session already owns a mapped
achievement, mirroring retail `sub_467f70` without issuing a fresh query.
=================
*/
static qboolean SV_SteamStats_HasSessionAchievement( sv_steam_stats_session_t *session, int achievementId ) {
	const char *name;
	char detail[128];

	name = SV_SteamStats_GetAchievementName( achievementId, "achievement-query" );
	if ( !name ) {
		return qfalse;
	}

	if ( !session ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s session unavailable for event query", name );
		SV_LogSteamStatsLifecycle( NULL, "achievement-query", detail );
		return qfalse;
	}

	if ( !session->active ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s unavailable for inactive event session", name );
		SV_LogSteamStatsLifecycle( &session->steamId, "achievement-query", detail );
		return qfalse;
	}

	if ( !session->backendAvailable ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s unavailable pending stats response", name );
		SV_LogSteamStatsLifecycle( &session->steamId, "achievement-query", detail );
		return qfalse;
	}

	Com_sprintf( detail, sizeof( detail ), "achievement %s event ownership is %s",
		name, session->achievementUnlocked[achievementId] ? "present" : "absent" );
	SV_LogSteamStatsLifecycle( &session->steamId, "achievement-query", detail );
	return session->achievementUnlocked[achievementId] ? qtrue : qfalse;
}

/*
=================
SV_SteamStats_UnlockSessionAchievement

Unlocks one mapped Steam achievement from a retained event session, matching
retail `sub_467e00`'s gameplay gate before the direct SetAchievement dispatch.
=================
*/
static qboolean SV_SteamStats_UnlockSessionAchievement( sv_steam_stats_session_t *session, int achievementId, const char *reason ) {
	const char *name;
	const char *unlockReason;
	char detail[128];

	unlockReason = reason ? reason : "event-process";
	name = SV_SteamStats_GetAchievementName( achievementId, "achievement-unlock" );
	if ( !name ) {
		return qfalse;
	}

	if ( SV_SteamStats_HasSessionAchievement( session, achievementId ) ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s already unlocked from %s", name, unlockReason );
		SV_LogSteamStatsLifecycle( &session->steamId, "achievement-unlock", detail );
		return qtrue;
	}

	if ( !SV_SteamStats_ShouldUnlockAchievement() ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s blocked by gameplay gate from %s", name, unlockReason );
		SV_LogSteamStatsLifecycle( session ? &session->steamId : NULL, "achievement-unlock", detail );
		return qfalse;
	}

	if ( !SV_SteamStats_SetAchievement( session, achievementId ) ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s publish failed from %s", name, unlockReason );
		SV_LogSteamStatsLifecycle( session ? &session->steamId : NULL, "achievement-unlock", detail );
		return qfalse;
	}

	session->achievementUnlocked[achievementId] = qtrue;
	session->achievementLoaded[achievementId] = qtrue;
	Com_sprintf( detail, sizeof( detail ), "unlocked achievement %s from %s", name, unlockReason );
	SV_LogSteamStatsLifecycle( &session->steamId, "achievement-unlock", detail );
	return qtrue;
}

/*
=================
SV_SteamStats_ClearPlayerDeathEvents

Clears the source-side mirror of retail `data_e30380`, the pending PLAYER_DEATH
event array merged by the retail match-report path.
=================
*/
static void SV_SteamStats_ClearPlayerDeathEvents( void ) {
	if ( s_svSteamPlayerDeathEventCount <= 0 ) {
		return;
	}

	memset( s_svSteamPlayerDeathEvents, 0, sizeof( s_svSteamPlayerDeathEvents ) );
	s_svSteamPlayerDeathEventCount = 0;
}

/*
=================
SV_SteamStats_ProcessPlayerDeathEvent

Reconstructs the recovered `PLAYER_DEATH` pending-event cache branch from
retail `SteamStats_ProcessEvent`.
=================
*/
static void SV_SteamStats_ProcessPlayerDeathEvent( const char *payload ) {
	sv_steam_player_death_event_t *event;
	char detail[256];

	if ( !payload || !payload[0] ) {
		SV_LogSteamStatsLifecycle( NULL, "event-process", "ignored PLAYER_DEATH event without payload" );
		return;
	}

	if ( s_svSteamPlayerDeathEventCount >= SV_STEAM_PLAYER_DEATH_EVENT_LIMIT ) {
		Com_sprintf( detail, sizeof( detail ), "ignored PLAYER_DEATH event cache overflow at %d",
			s_svSteamPlayerDeathEventCount );
		SV_LogSteamStatsLifecycle( NULL, "event-process", detail );
		return;
	}

	event = &s_svSteamPlayerDeathEvents[s_svSteamPlayerDeathEventCount];
	memset( event, 0, sizeof( *event ) );
	event->killerTeam = -1;
	event->victimTeam = -1;
	Q_strncpyz( event->killerPowerups, "[]", sizeof( event->killerPowerups ) );
	Q_strncpyz( event->victimPowerups, "[]", sizeof( event->victimPowerups ) );
	Q_strncpyz( event->rawPayload, payload, sizeof( event->rawPayload ) );

	if ( !SV_SteamStats_ParseEventPayloadInt( payload, "TIME", &event->time ) ) {
		SV_LogSteamStatsLifecycle( NULL, "event-process", "PLAYER_DEATH missing TIME; defaulting to 0" );
	}
	if ( !SV_SteamStats_ParseEventPayloadString( payload, "MOD", event->modName, sizeof( event->modName ) )
		&& !SV_SteamStats_ParseEventPayloadString( payload, "WEAPON", event->modName, sizeof( event->modName ) ) ) {
		Q_strncpyz( event->modName, "UNKNOWN", sizeof( event->modName ) );
	}

	SV_SteamStats_ParseNestedEventPayloadString( payload, "KILLER", "NAME",
		event->killerName, sizeof( event->killerName ) );
	SV_SteamStats_ParseNestedEventPayloadString( payload, "KILLER", "STEAM_ID",
		event->killerSteamId, sizeof( event->killerSteamId ) );
	SV_SteamStats_ParseNestedEventPayloadInt( payload, "KILLER", "TEAM", &event->killerTeam );
	SV_SteamStats_CopyNestedEventPayloadArray( payload, "KILLER", "POWERUPS",
		event->killerPowerups, sizeof( event->killerPowerups ) );

	if ( !SV_SteamStats_ParseNestedEventPayloadString( payload, "VICTIM", "NAME",
		event->victimName, sizeof( event->victimName ) ) ) {
		SV_LogSteamStatsLifecycle( NULL, "event-process", "PLAYER_DEATH missing VICTIM.NAME" );
	}
	if ( !SV_SteamStats_ParseNestedEventPayloadString( payload, "VICTIM", "STEAM_ID",
		event->victimSteamId, sizeof( event->victimSteamId ) ) ) {
		SV_LogSteamStatsLifecycle( NULL, "event-process", "PLAYER_DEATH missing VICTIM.STEAM_ID" );
	}
	if ( !SV_SteamStats_ParseNestedEventPayloadInt( payload, "VICTIM", "TEAM", &event->victimTeam ) ) {
		SV_LogSteamStatsLifecycle( NULL, "event-process", "PLAYER_DEATH missing VICTIM.TEAM" );
	}
	SV_SteamStats_CopyNestedEventPayloadArray( payload, "VICTIM", "POWERUPS",
		event->victimPowerups, sizeof( event->victimPowerups ) );

	s_svSteamPlayerDeathEventCount++;
	Com_sprintf( detail, sizeof( detail ),
		"cached PLAYER_DEATH event %d time=%d mod=%s killer=%s victim=%s",
		s_svSteamPlayerDeathEventCount, event->time, event->modName,
		event->killerName[0] ? event->killerName : "<none>",
		event->victimName[0] ? event->victimName : "<none>" );
	SV_LogSteamStatsLifecycle( NULL, "event-process", detail );
}

/*
=================
SV_SteamStats_AppendJsonFragment

Appends formatted text to a server-owned JSON proxy buffer.
=================
*/
static qboolean SV_SteamStats_AppendJsonFragment( char *buffer, size_t bufferSize, size_t *length, const char *fmt, ... ) {
	va_list args;
	int written;

	if ( !buffer || !length || !fmt || bufferSize == 0 || *length >= bufferSize ) {
		return qfalse;
	}

	va_start( args, fmt );
	written = Q_vsnprintf( buffer + *length, bufferSize - *length, fmt, args );
	va_end( args );

	if ( written < 0 || (size_t)written >= ( bufferSize - *length ) ) {
		return qfalse;
	}

	*length += written;
	return qtrue;
}

/*
=================
SV_SteamStats_EscapeJsonString

Escapes one parsed rankings string before placing it back into the retained
server-side JSON report proxy.
=================
*/
static void SV_SteamStats_EscapeJsonString( const char *src, char *dst, size_t dstSize ) {
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
		unsigned char ch = (unsigned char)*cursor;

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
=================
SV_SteamStats_FindMatchReportObjectClose

Finds the closing brace for a root JSON object in the source-side match-report
proxy so the retained Steam stats owner can splice in `PLYR_EVENTS`.
=================
*/
static const char *SV_SteamStats_FindMatchReportObjectClose( const char *report ) {
	const char *cursor;
	const char *scan;
	int depth;
	qboolean inString;
	qboolean escaped;

	cursor = SV_SteamStats_SkipEventPayloadWhitespace( report );
	if ( !cursor || *cursor != SV_STEAM_JSON_OBJECT_OPEN ) {
		return NULL;
	}

	depth = 0;
	inString = qfalse;
	escaped = qfalse;
	for ( scan = cursor; *scan; scan++ ) {
		if ( inString ) {
			if ( escaped ) {
				escaped = qfalse;
			} else if ( *scan == SV_STEAM_JSON_ESCAPE ) {
				escaped = qtrue;
			} else if ( *scan == SV_STEAM_JSON_STRING_QUOTE ) {
				inString = qfalse;
			}
			continue;
		}

		if ( *scan == SV_STEAM_JSON_STRING_QUOTE ) {
			inString = qtrue;
			continue;
		}
		if ( *scan == SV_STEAM_JSON_OBJECT_OPEN ) {
			depth++;
			continue;
		}
		if ( *scan == SV_STEAM_JSON_OBJECT_CLOSE ) {
			const char *tail;

			depth--;
			if ( depth != 0 ) {
				continue;
			}

			tail = SV_SteamStats_SkipEventPayloadWhitespace( scan + 1 );
			return ( tail && *tail == '\0' ) ? scan : NULL;
		}
	}

	return NULL;
}

/*
=================
SV_SteamStats_MatchReportHasFields

Returns whether the root match-report object already contains at least one
field before `PLYR_EVENTS` is appended.
=================
*/
static qboolean SV_SteamStats_MatchReportHasFields( const char *report, const char *objectClose ) {
	const char *cursor;

	cursor = SV_SteamStats_SkipEventPayloadWhitespace( report );
	if ( !cursor || *cursor != SV_STEAM_JSON_OBJECT_OPEN || !objectClose ) {
		return qfalse;
	}

	for ( cursor++; cursor < objectClose; cursor++ ) {
		if ( *cursor != ' ' && *cursor != '\t' && *cursor != '\n' && *cursor != '\r' ) {
			return qtrue;
		}
	}

	return qfalse;
}

/*
=================
SV_SteamStats_AppendPlayerDeathReportEvent

Serializes one cached retail `PLAYER_DEATH` event into the match-report
`PLYR_EVENTS` array shape recovered from `sub_468ee0`.
=================
*/
static qboolean SV_SteamStats_AppendPlayerDeathReportEvent( char *buffer, size_t bufferSize, size_t *length, const sv_steam_player_death_event_t *event ) {
	char modName[SV_STEAM_PLAYER_DEATH_TOKEN_CHARS * 2 + 1];
	char killerName[MAX_NAME_LENGTH * 2 + 1];
	char killerSteamId[SV_STEAM_PLAYER_DEATH_STEAMID_CHARS * 2 + 1];
	char victimName[MAX_NAME_LENGTH * 2 + 1];
	char victimSteamId[SV_STEAM_PLAYER_DEATH_STEAMID_CHARS * 2 + 1];
	const char *killerPowerups;
	const char *victimPowerups;

	if ( !event ) {
		return qfalse;
	}

	SV_SteamStats_EscapeJsonString( event->modName[0] ? event->modName : "UNKNOWN",
		modName, sizeof( modName ) );
	SV_SteamStats_EscapeJsonString( event->killerName,
		killerName, sizeof( killerName ) );
	SV_SteamStats_EscapeJsonString( event->killerSteamId,
		killerSteamId, sizeof( killerSteamId ) );
	SV_SteamStats_EscapeJsonString( event->victimName,
		victimName, sizeof( victimName ) );
	SV_SteamStats_EscapeJsonString( event->victimSteamId,
		victimSteamId, sizeof( victimSteamId ) );

	killerPowerups = ( event->killerPowerups[0] == SV_STEAM_JSON_ARRAY_OPEN ) ? event->killerPowerups : "[]";
	victimPowerups = ( event->victimPowerups[0] == SV_STEAM_JSON_ARRAY_OPEN ) ? event->victimPowerups : "[]";

	return SV_SteamStats_AppendJsonFragment( buffer, bufferSize, length,
		"{\"TIME\":%d,\"MOD\":\"%s\",\"KILLER\":{\"NAME\":\"%s\",\"ID\":\"%s\",\"TEAM\":%d,\"POWERUPS\":%s},"
		"\"VICTIM\":{\"NAME\":\"%s\",\"ID\":\"%s\",\"TEAM\":%d,\"POWERUPS\":%s}}",
		event->time, modName,
		killerName, killerSteamId, event->killerTeam, killerPowerups,
		victimName, victimSteamId, event->victimTeam, victimPowerups );
}

/*
=================
SV_SteamStats_AppendPlayerDeathReportEvents

Appends the full cached `PLYR_EVENTS` array to an already-open match-report
object.
=================
*/
static qboolean SV_SteamStats_AppendPlayerDeathReportEvents( char *buffer, size_t bufferSize, size_t *length ) {
	int i;

	if ( !SV_SteamStats_AppendJsonFragment( buffer, bufferSize, length, "\"PLYR_EVENTS\":[" ) ) {
		return qfalse;
	}

	for ( i = 0; i < s_svSteamPlayerDeathEventCount; i++ ) {
		if ( i > 0 && !SV_SteamStats_AppendJsonFragment( buffer, bufferSize, length, "," ) ) {
			return qfalse;
		}
		if ( !SV_SteamStats_AppendPlayerDeathReportEvent( buffer, bufferSize, length,
			&s_svSteamPlayerDeathEvents[i] ) ) {
			return qfalse;
		}
	}

	return SV_SteamStats_AppendJsonFragment( buffer, bufferSize, length, "]" );
}

/*
=================
SV_SteamStats_BuildMatchReportWithPlayerEvents

Copies the qagame match-report JSON proxy and splices cached retail
`PLAYER_DEATH` events into the root object as `PLYR_EVENTS`.
=================
*/
static qboolean SV_SteamStats_BuildMatchReportWithPlayerEvents( const char *report, char *buffer, size_t bufferSize ) {
	const char *objectClose;
	size_t prefixLength;
	size_t length;
	qboolean hasFields;

	if ( !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	if ( s_svSteamPlayerDeathEventCount <= 0 ) {
		return qfalse;
	}

	if ( !report || !report[0] ) {
		length = 0;
		if ( !SV_SteamStats_AppendJsonFragment( buffer, bufferSize, &length, "{" ) ) {
			return qfalse;
		}
		if ( !SV_SteamStats_AppendPlayerDeathReportEvents( buffer, bufferSize, &length ) ) {
			return qfalse;
		}
		return SV_SteamStats_AppendJsonFragment( buffer, bufferSize, &length, "}" );
	}

	if ( SV_SteamStats_FindEventPayloadFieldValue( report, "PLYR_EVENTS" ) ) {
		return qfalse;
	}

	objectClose = SV_SteamStats_FindMatchReportObjectClose( report );
	if ( !objectClose ) {
		return qfalse;
	}

	prefixLength = (size_t)( objectClose - report );
	if ( prefixLength >= bufferSize ) {
		return qfalse;
	}

	memcpy( buffer, report, prefixLength );
	length = prefixLength;
	buffer[length] = '\0';
	hasFields = SV_SteamStats_MatchReportHasFields( report, objectClose );

	if ( hasFields && !SV_SteamStats_AppendJsonFragment( buffer, bufferSize, &length, "," ) ) {
		return qfalse;
	}
	if ( !SV_SteamStats_AppendPlayerDeathReportEvents( buffer, bufferSize, &length ) ) {
		return qfalse;
	}
	return SV_SteamStats_AppendJsonFragment( buffer, bufferSize, &length, "}" );
}

/*
=================
SV_SteamStats_ProcessMatchReport

Handles the retained Steam stats side of the qagame MATCH_REPORT bridge and
returns the report payload that should be published through the shared runtime
path.
=================
*/
const void *SV_SteamStats_ProcessMatchReport( const void *report, char *buffer, int bufferSize ) {
	char detail[128];
	const void *preparedReport;

	preparedReport = report;

	if ( s_svSteamPlayerDeathEventCount > 0 ) {
		if ( SV_SteamStats_BuildMatchReportWithPlayerEvents( (const char *)report,
			buffer, bufferSize > 0 ? (size_t)bufferSize : 0 ) ) {
			preparedReport = buffer;
			Com_sprintf( detail, sizeof( detail ),
				"attached %d cached PLAYER_DEATH events as PLYR_EVENTS for MATCH_REPORT",
				s_svSteamPlayerDeathEventCount );
			SV_LogSteamStatsLifecycle( NULL, "match-report", detail );
		} else {
			Com_sprintf( detail, sizeof( detail ),
				"cleared %d cached PLAYER_DEATH events for MATCH_REPORT without PLYR_EVENTS merge",
				s_svSteamPlayerDeathEventCount );
			SV_LogSteamStatsLifecycle( NULL, "match-report", detail );
		}
	}

	if ( SV_SteamStats_ShouldSendMatchSummary( (const char *)preparedReport ) ) {
		SV_SteamStats_SendSummaryToPeers( (const char *)preparedReport );
	} else {
		SV_SteamStats_ClearSummaryPeers();
	}
	SV_SteamStats_ClearPlayerDeathEvents();
	return preparedReport;
}

/*
=================
SV_SteamStats_ProcessPlayerStatsEvent

Reconstructs recovered `PLAYER_STATS` win/loss/played stat updates and the
achievement branches from retail `SteamStats_ProcessEvent`.
=================
*/
static void SV_SteamStats_ProcessPlayerStatsEvent( sv_steam_stats_session_t *session, const char *payload ) {
	int wins;
	int losses;
	int score;
	char mapName[MAX_QPATH];
	char detail[128];

	wins = 0;
	losses = 0;
	score = 0;
	mapName[0] = '\0';

	if ( !payload || !payload[0] ) {
		SV_LogSteamStatsLifecycle( session ? &session->steamId : NULL,
			"event-process", "ignored PLAYER_STATS event without payload" );
		return;
	}

	if ( !SV_SteamStats_ParseEventPayloadInt( payload, "WIN", &wins ) ) {
		SV_LogSteamStatsLifecycle( &session->steamId, "event-process", "PLAYER_STATS missing WIN; defaulting to 0" );
	}
	if ( !SV_SteamStats_ParseEventPayloadInt( payload, "LOSE", &losses ) ) {
		SV_LogSteamStatsLifecycle( &session->steamId, "event-process", "PLAYER_STATS missing LOSE; defaulting to 0" );
	}

	SV_SteamStats_AddSessionFieldValue( session, SV_STEAM_STAT_WINS, wins, "event-process" );
	SV_SteamStats_AddSessionFieldValue( session, SV_STEAM_STAT_LOSSES, losses, "event-process" );
	SV_SteamStats_AddSessionFieldValue( session, SV_STEAM_STAT_PLAYED, 1, "event-process" );
	SV_SteamStats_FlushPendingValues( session, qtrue );

	if ( !SV_SteamStats_HasSessionAchievement( session, SV_STEAM_ACHIEVEMENT_TRAINING_3_2 ) ) {
		Cvar_VariableStringBuffer( "mapname", mapName, sizeof( mapName ) );
		if ( !strcmp( mapName, SV_STEAM_PLAYER_STATS_TRAINING_MAP )
			&& Cvar_VariableIntegerValue( "g_training" ) > 0
			&& wins != 0 ) {
			SV_SteamStats_UnlockSessionAchievement( session, SV_STEAM_ACHIEVEMENT_TRAINING_3_2, "PLAYER_STATS WIN" );
		}
	}

	if ( !SV_SteamStats_HasSessionAchievement( session, SV_STEAM_ACHIEVEMENT_WICKED )
		&& Cvar_VariableIntegerValue( "g_gametype" ) == SV_STEAM_PLAYER_STATS_WICKED_GAMETYPE ) {
		if ( !SV_SteamStats_ParseEventPayloadInt( payload, "SCORE", &score ) ) {
			SV_LogSteamStatsLifecycle( &session->steamId, "event-process", "PLAYER_STATS missing SCORE for AW_WICKED gate" );
		} else if ( score == SV_STEAM_PLAYER_STATS_WICKED_SCORE ) {
			SV_SteamStats_UnlockSessionAchievement( session, SV_STEAM_ACHIEVEMENT_WICKED, "PLAYER_STATS SCORE" );
		}
	}

	Com_sprintf( detail, sizeof( detail ), "processed PLAYER_STATS win=%d lose=%d played=1", wins, losses );
	SV_LogSteamStatsLifecycle( &session->steamId, "event-process", detail );
}

/*
=================
SV_SteamStats_ProcessPlayerKillEvent

Reconstructs the recovered `PLAYER_KILL` speed achievement branch from retail
`SteamStats_ProcessEvent`.
=================
*/
static void SV_SteamStats_ProcessPlayerKillEvent( sv_steam_stats_session_t *session, const char *payload ) {
	qboolean teamKill;
	qboolean suicide;
	float killerSpeed;
	char detail[128];

	teamKill = qfalse;
	suicide = qfalse;
	killerSpeed = 0.0f;

	if ( !payload || !payload[0] ) {
		SV_LogSteamStatsLifecycle( session ? &session->steamId : NULL,
			"event-process", "ignored PLAYER_KILL event without payload" );
		return;
	}

	if ( !SV_SteamStats_ParseEventPayloadBool( payload, "TEAMKILL", &teamKill ) ) {
		SV_LogSteamStatsLifecycle( &session->steamId, "event-process", "PLAYER_KILL missing TEAMKILL; defaulting to false" );
	}
	if ( !SV_SteamStats_ParseEventPayloadBool( payload, "SUICIDE", &suicide ) ) {
		SV_LogSteamStatsLifecycle( &session->steamId, "event-process", "PLAYER_KILL missing SUICIDE; defaulting to false" );
	}

	if ( teamKill || suicide ) {
		Com_sprintf( detail, sizeof( detail ), "ignored PLAYER_KILL speed gate teamkill=%d suicide=%d", teamKill, suicide );
		SV_LogSteamStatsLifecycle( &session->steamId, "event-process", detail );
		return;
	}

	if ( !SV_SteamStats_HasSessionAchievement( session, SV_STEAM_ACHIEVEMENT_SPEED_KILLS ) ) {
		if ( !SV_SteamStats_ParseNestedEventPayloadFloat( payload, "KILLER", "SPEED", &killerSpeed ) ) {
			SV_LogSteamStatsLifecycle( &session->steamId, "event-process", "PLAYER_KILL missing KILLER.SPEED for AW_SPEED_KILLS gate" );
		} else if ( killerSpeed > SV_STEAM_PLAYER_KILL_SPEED_THRESHOLD ) {
			SV_SteamStats_UnlockSessionAchievement( session, SV_STEAM_ACHIEVEMENT_SPEED_KILLS, "PLAYER_KILL KILLER.SPEED" );
		}
	}

	Com_sprintf( detail, sizeof( detail ), "processed PLAYER_KILL teamkill=%d suicide=%d speed=%.3f",
		teamKill, suicide, killerSpeed );
	SV_LogSteamStatsLifecycle( &session->steamId, "event-process", detail );
}

/*
=================
SV_SteamStats_ProcessPlayerMedalEvent

Reconstructs the recovered `PLAYER_MEDAL` medal-stat increment and support
medal `AW_MVP` achievement branch from retail `SteamStats_ProcessEvent`.
=================
*/
static void SV_SteamStats_ProcessPlayerMedalEvent( sv_steam_stats_session_t *session, const char *payload ) {
	char medalName[64];
	int statIndex;
	int supportTotal;
	char detail[128];

	medalName[0] = '\0';

	if ( !payload || !payload[0] ) {
		SV_LogSteamStatsLifecycle( session ? &session->steamId : NULL,
			"event-process", "ignored PLAYER_MEDAL event without payload" );
		return;
	}

	if ( !SV_SteamStats_ParseEventPayloadString( payload, "MEDAL", medalName, sizeof( medalName ) ) ) {
		SV_LogSteamStatsLifecycle( &session->steamId, "event-process", "PLAYER_MEDAL missing MEDAL token" );
		return;
	}

	statIndex = SV_SteamStats_GetMedalStatIndex( medalName );
	if ( statIndex < 0 ) {
		Com_sprintf( detail, sizeof( detail ), "ignored PLAYER_MEDAL unknown medal %s", medalName );
		SV_LogSteamStatsLifecycle( &session->steamId, "event-process", detail );
		return;
	}

	SV_SteamStats_AddSessionFieldValue( session, statIndex, 1, "event-process" );
	SV_SteamStats_FlushPendingValues( session, qtrue );

	if ( !SV_SteamStats_HasSessionAchievement( session, SV_STEAM_ACHIEVEMENT_MVP ) ) {
		supportTotal = session->statValue[SV_STEAM_STAT_MEDAL_CAPTURE]
			+ session->statValue[SV_STEAM_STAT_MEDAL_ASSIST]
			+ session->statValue[SV_STEAM_STAT_MEDAL_DEFENSE];
		if ( supportTotal >= SV_STEAM_PLAYER_MEDAL_MVP_TOTAL ) {
			SV_SteamStats_UnlockSessionAchievement( session, SV_STEAM_ACHIEVEMENT_MVP, "PLAYER_MEDAL support" );
		}
	} else {
		supportTotal = 0;
	}

	Com_sprintf( detail, sizeof( detail ), "processed PLAYER_MEDAL medal=%s stat=%d support=%d",
		medalName, statIndex, supportTotal );
	SV_LogSteamStatsLifecycle( &session->steamId, "event-process", detail );
}

/*
=================
SV_SteamStats_EventHasRetailSideEffects

Returns whether one qagame report event belongs to the retail Steam stats
event processor handled by `sub_468030`.
=================
*/
static qboolean SV_SteamStats_EventHasRetailSideEffects( const char *eventName ) {
	if ( !eventName || !eventName[0] ) {
		return qfalse;
	}

	if ( !strcmp( eventName, "PLAYER_STATS" ) ) {
		return qtrue;
	}
	if ( !strcmp( eventName, "PLAYER_KILL" ) ) {
		return qtrue;
	}
	if ( !strcmp( eventName, "PLAYER_DEATH" ) ) {
		return qtrue;
	}
	if ( !strcmp( eventName, "PLAYER_MEDAL" ) ) {
		return qtrue;
	}

	return qfalse;
}

/*
=================
SV_SteamStats_ProcessEvent

Reconstructs the retail `SteamStats_ProcessEvent` owner boundary reached by
`SV_ReportPlayerEvent` before the same payload is published through ZMQ.
=================
*/
void SV_SteamStats_ProcessEvent( uint32_t steamIdLow, uint32_t steamIdHigh, const void *clientStats, const char *eventName, const void *payload ) {
	CSteamID steamId;
	sv_steam_stats_session_t *session;
	char detail[128];

	if ( !eventName || !eventName[0] ) {
		SV_LogSteamStatsLifecycle( NULL, "event-process", "ignored unnamed player event" );
		return;
	}

	if ( !strcmp( eventName, "PLAYER_DEATH" ) ) {
		SV_SteamStats_ProcessPlayerDeathEvent( (const char *)payload );
	}

	steamId.value = ( (uint64_t)steamIdHigh << 32 ) | steamIdLow;
	if ( steamId.value == 0ull ) {
		Com_sprintf( detail, sizeof( detail ), "ignored %s event without steam id", eventName );
		SV_LogSteamStatsLifecycle( NULL, "event-process", detail );
		return;
	}

	if ( !SV_SteamStats_EventHasRetailSideEffects( eventName ) ) {
		Com_sprintf( detail, sizeof( detail ), "ignored %s event without mapped Steam stats side effects", eventName );
		SV_LogSteamStatsLifecycle( &steamId, "event-process", detail );
		return;
	}

	session = SV_SteamStats_FindSessionBySteamId( &steamId );
	if ( !session ) {
		Com_sprintf( detail, sizeof( detail ), "deferred %s event without retained session", eventName );
		SV_LogSteamStatsLifecycle( &steamId, "event-process", detail );
		return;
	}

	if ( !strcmp( eventName, "PLAYER_STATS" ) ) {
		SV_SteamStats_ProcessPlayerStatsEvent( session, (const char *)payload );
		return;
	}
	if ( !strcmp( eventName, "PLAYER_KILL" ) ) {
		SV_SteamStats_ProcessPlayerKillEvent( session, (const char *)payload );
		return;
	}
	if ( !strcmp( eventName, "PLAYER_MEDAL" ) ) {
		SV_SteamStats_ProcessPlayerMedalEvent( session, (const char *)payload );
		return;
	}

	Com_sprintf( detail, sizeof( detail ), "accepted %s event for retained Steam stats owner", eventName );
	SV_LogSteamStatsLifecycle( &session->steamId, "event-process", detail );

	(void)clientStats;
	(void)payload;
}

/*
=================
SV_FindClientBySteamId

Finds a live client slot that owns one SteamID.
=================
*/
static client_t *SV_FindClientBySteamId( const CSteamID *steamId ) {
	client_t	*cl;
	CSteamID	parsedSteamId;
	int		i;

	if ( !steamId || steamId->value == 0ull ) {
		return NULL;
	}

	for ( i = 0, cl = svs.clients; i < sv_maxclients->integer; i++, cl++ ) {
		if ( cl->state < CS_CONNECTED || cl->state == CS_ZOMBIE || !cl->platformSteamId[0] ) {
			continue;
		}

		if ( !SV_ParsePlatformSteamId( cl->platformSteamId, &parsedSteamId ) ) {
			continue;
		}

		if ( parsedSteamId.value == steamId->value ) {
			return cl;
		}
	}

	return NULL;
}

/*
=================
SV_FindActiveClientBySteamId

Finds a fully entered client slot that owns one SteamID.
=================
*/
static client_t *SV_FindActiveClientBySteamId( const CSteamID *steamId ) {
	client_t	*cl;
	CSteamID	parsedSteamId;
	int		i;

	if ( !steamId || steamId->value == 0ull ) {
		return NULL;
	}

	for ( i = 0, cl = svs.clients; i < sv_maxclients->integer; i++, cl++ ) {
		if ( cl->state != CS_ACTIVE || !cl->platformSteamId[0] ) {
			continue;
		}

		if ( !SV_ParsePlatformSteamId( cl->platformSteamId, &parsedSteamId ) ) {
			continue;
		}

		if ( parsedSteamId.value == steamId->value ) {
			return cl;
		}
	}

	return NULL;
}

/*
=================
SV_EndPlatformAuthSession

Closes any active Steam GameServer auth session retained for one client slot.
=================
*/
static void SV_EndPlatformAuthSession( client_t *cl ) {
	CSteamID steamId;

	if ( !cl || !cl->platformAuthSessionActive ) {
		return;
	}

	cl->platformAuthSessionActive = qfalse;
	SV_SteamStats_RemovePlayerSession( cl );

	if ( !SV_ParsePlatformSteamId( cl->platformSteamId, &steamId ) ) {
		return;
	}

	QL_Steamworks_ServerEndAuthSession( &steamId );
}

/*
=================
SV_SteamServerClientOwnsAuthSteamId

Returns whether a Steam auth session is still owned by a live server client.
=================
*/
static qboolean SV_SteamServerClientOwnsAuthSteamId( const CSteamID *steamId ) {
	client_t	*cl;
	CSteamID	parsedSteamId;
	int		i;

	if ( !steamId || steamId->value == 0ull || !svs.clients || !sv_maxclients ) {
		return qfalse;
	}

	for ( i = 0, cl = svs.clients; i < sv_maxclients->integer; i++, cl++ ) {
		if ( cl->state == CS_FREE || !cl->platformSteamId[0] ) {
			continue;
		}

		if ( !SV_ParsePlatformSteamId( cl->platformSteamId, &parsedSteamId ) ) {
			continue;
		}

		if ( parsedSteamId.value == steamId->value ) {
			return qtrue;
		}
	}

	return qfalse;
}

/*
=================
SV_SteamServerEndOrphanedAuthSessions

Ends Steam GameServer auth sessions whose Steam IDs no longer belong to a live
server client before spawning a fresh server instance.
=================
*/
void SV_SteamServerEndOrphanedAuthSessions( void ) {
	client_t	*cl;
	CSteamID	steamId;
	int		i;

	if ( !svs.clients || !sv_maxclients ) {
		return;
	}

	for ( i = 0, cl = svs.clients; i < sv_maxclients->integer; i++, cl++ ) {
		if ( !cl->platformAuthSessionActive ) {
			continue;
		}

		if ( !SV_ParsePlatformSteamId( cl->platformSteamId, &steamId ) ) {
			cl->platformAuthSessionActive = qfalse;
			SV_SteamStats_RemovePlayerSession( cl );
			continue;
		}

		if ( SV_SteamServerClientOwnsAuthSteamId( &steamId ) ) {
			continue;
		}

		Com_Printf( "Found an authed client with steam id %llu that is no longer a live client\n",
			(unsigned long long)steamId.value );
		cl->platformAuthSessionActive = qfalse;
		SV_SteamStats_RemovePlayerSession( cl );

		if ( QL_Steamworks_ServerIsInitialised() ) {
			QL_Steamworks_ServerEndAuthSession( &steamId );
			Com_Printf( "Called EndAuthSession on steam id %llu\n",
				(unsigned long long)steamId.value );
		} else {
			Com_Printf( "Can't end auth session on steam id %llu because Steam GameServer is not initialized\n",
				(unsigned long long)steamId.value );
		}
	}
}

/*
=================
SV_BeginPlatformAuthSession

Starts one Steam GameServer auth session after qagame has accepted the connection.
=================
*/
static const char *SV_BeginPlatformAuthSession( client_t *cl, const netadr_t *adr ) {
	ql_auth_response_t	response;
	CSteamID		steamId;
	const char		*message;

	if ( !cl || !cl->platformAuthToken[0] || Sys_IsLANAddress( cl->netchan.remoteAddress ) ) {
		return NULL;
	}

	if ( !SV_ParsePlatformSteamId( cl->platformSteamId, &steamId ) ) {
		message = "Failed to verify Steam auth token";
		SV_SetPlatformAuthUserinfo( cl, "error", "failure", message );
		SV_FinalisePlatformAuthState( cl, qfalse, message );
		SV_LogPlatformAuth( adr, cl, "failed", message );
		SV_LogPlatformAuthConnectRejected( message );
		return message;
	}

	Com_Memset( &response, 0, sizeof( response ) );

	if ( !QL_Steamworks_ServerBeginAuthSession( &steamId, cl->platformAuthToken, &response ) ) {
		message = response.message[0] ? response.message : "Failed to verify Steam auth token";
		SV_SetPlatformAuthUserinfo( cl,
			response.result == QL_AUTH_RESULT_ERROR ? "error" : "denied",
			response.outcome == QL_AUTH_OUTCOME_RETRY ? "retry" : "failure",
			message );
		SV_FinalisePlatformAuthState( cl, qfalse, message );
		SV_LogPlatformAuth( adr, cl, "failed", message );
		SV_LogPlatformAuthConnectRejected( message );
		return message;
	}

	cl->platformAuthSessionActive = qtrue;
	cl->platformAuthPending = qtrue;
	cl->platformAuthSucceeded = qfalse;
	SV_SetPlatformAuthUserinfo( cl, "pending", "retry", "" );
	Q_strncpyz( cl->platformAuthResult, "pending", sizeof( cl->platformAuthResult ) );
	Q_strncpyz( cl->platformAuthOutcome, "retry", sizeof( cl->platformAuthOutcome ) );
	cl->platformAuthMessage[0] = '\0';
	SV_SteamStats_CreatePlayerSession( cl );
	SV_LogPlatformAuth( adr, cl, "pending", NULL );
	return NULL;
}

/*
=================
SV_LogSteamServerCallbackLifecycle

Publishes provider-aware diagnostics for the retained Steam GameServer
callback-owner lifecycle.
=================
*/
static void SV_LogSteamServerCallbackLifecycle( const char *stage, const char *detail ) {
	Com_Printf( "Steam server callback %s via %s [%s]: %s\n",
		stage ? stage : "update",
		SV_GetSteamServerProviderLabel(),
		SV_GetSteamServerPolicyLabel(),
		detail ? detail : "no detail" );
}

/*
=================
SV_LogSteamServerCallbackBootstrapLifecycle

Publishes provider-aware diagnostics when the retained Steam GameServer
callback bootstrap falls back before registration succeeds.
=================
*/
static void SV_LogSteamServerCallbackBootstrapLifecycle( const char *stage, const char *detail ) {
	Com_DPrintf( "Steam server callback bootstrap %s via %s [%s]: %s\n",
		stage ? stage : "update",
		SV_GetSteamServerProviderLabel(),
		SV_GetSteamServerPolicyLabel(),
		detail ? detail : "no detail" );
}

/*
=================
SV_GetSteamAuthOwnershipLabel

Returns an observational ownership label for one validation callback without
changing the retained retail auth policy.
=================
*/
static const char *SV_GetSteamAuthOwnershipLabel( const ql_steam_validate_auth_ticket_response_t *event ) {
	if ( !event || event->ownerSteamId.value == 0ull ) {
		return "owner-unset";
	}

	if ( event->ownerSteamId.value == event->steamId.value ) {
		return "self-owned";
	}

	return "owner-mismatch";
}

/*
=================
SV_SteamServerConnectedCallback

Publishes the current server identity once Steam confirms the GameServer session.
=================
*/
static void SV_SteamServerConnectedCallback( void *context, const ql_steam_server_connected_t *event ) {
	const char *serverInfo;

	(void)context;
	(void)event;

	sv_steamServerConnected = qtrue;
	SV_LogSteamServerCallbackLifecycle( "connected", "published identity and state refresh" );
	SV_SteamServerPublishIdentity();
	SV_SteamServerUpdatePublishedState( qtrue );
	SV_SteamStats_RequerySessions();
	serverInfo = Cvar_InfoString( CVAR_SERVERINFO );
	QL_Steamworks_ServerSetKeyValuesFromInfoString( serverInfo );
}

/*
=================
SV_SteamServerConnectFailureCallback

Tracks retail-style Steam server connect failures in the server owner.
=================
*/
static void SV_SteamServerConnectFailureCallback( void *context, const ql_steam_server_connect_failure_t *event ) {
	(void)context;
	(void)event;

	sv_steamServerConnected = qfalse;
	Com_Printf( "Failed to connect to Steam servers\n" );
}

/*
=================
SV_SteamServerDisconnectedCallback

Tracks when the Steam GameServer session disconnects from Valve backends.
=================
*/
static void SV_SteamServerDisconnectedCallback( void *context, const ql_steam_server_disconnected_t *event ) {
	(void)context;
	(void)event;

	sv_steamServerConnected = qfalse;
	Com_Printf( "Disconnected from Steam servers\n" );
}

/*
=================
SV_SteamServerValidateAuthTicketResponseCallback

Finalises one pending client auth session from the retail ValidateAuthTicketResponse_t path.
=================
*/
static void SV_SteamServerValidateAuthTicketResponseCallback( void *context, const ql_steam_validate_auth_ticket_response_t *event ) {
	client_t			*cl;
	EAuthSessionResponse	response;
	char				result[16];
	char				outcome[64];
	char				message[QL_AUTH_MAX_RESPONSE_MESSAGE];
	char				detail[128];
	qboolean			accepted;

	(void)context;

	if ( !event ) {
		SV_LogSteamServerCallbackLifecycle( "validate_auth_ticket_response", "ignored null callback payload" );
		return;
	}

	response = event->authSessionResponse;
	if ( net_fakevacban && net_fakevacban->integer ) {
		response = k_EAuthSessionResponseVACBanned;
	}

	cl = SV_FindClientBySteamId( &event->steamId );
	if ( !cl ) {
		Com_sprintf( detail, sizeof( detail ), "ignored auth response for missing client %llu",
			(unsigned long long)event->steamId.value );
		SV_LogSteamServerCallbackLifecycle( "validate_auth_ticket_response", detail );
		return;
	}

	SV_FormatPlatformAuthCode( response, result, sizeof( result ) );
	Q_strncpyz( outcome, SV_GetPlatformAuthReason( response ), sizeof( outcome ) );
	SV_BuildPlatformAuthMessage( response, message, sizeof( message ) );
	Com_sprintf( detail, sizeof( detail ), "auth response steam=%llu owner=%llu ownership=%s code=%d",
		(unsigned long long)event->steamId.value,
		(unsigned long long)event->ownerSteamId.value,
		SV_GetSteamAuthOwnershipLabel( event ),
		response );
	SV_LogSteamServerCallbackLifecycle( "validate_auth_ticket_response", detail );
	SV_SetPlatformAuthUserinfo( cl, result, outcome, message );

	accepted = SV_IsPlatformAuthAccepted( response );
	SV_FinalisePlatformAuthState( cl, accepted, message );
	SV_LogPlatformAuth( &cl->netchan.remoteAddress, cl, accepted ? "accepted" : "failed", message );

	if ( accepted ) {
		return;
	}

	SV_DropClient( cl, message );
}

/*
=================
SV_LogSteamServerP2PSessionRequest

Publishes provider-aware diagnostics for the retained Steam GameServer P2P
session-request surface.
=================
*/
static void SV_LogSteamServerP2PSessionRequest( const CSteamID *steamId, const char *state, const char *reason ) {
	unsigned long long remoteId;

	remoteId = steamId ? (unsigned long long)steamId->value : 0ull;
	Com_Printf( "Steam P2P session request %s [%s; modern=%s] for %llu via %s [%s]: %s\n",
		state ? state : "update",
		QL_Steamworks_GetP2PTransportLabel(),
		QL_Steamworks_GetP2PModernGapLabel(),
		remoteId,
		SV_GetSteamServerProviderLabel(), SV_GetSteamServerPolicyLabel(),
		reason ? reason : "no detail" );
}

/*
=================
SV_SteamServerP2PSessionRequestCallback

Accepts server-side Steam P2P sessions only for active clients.
=================
*/
static void SV_SteamServerP2PSessionRequestCallback( void *context, const ql_steam_p2p_session_request_t *event ) {
	client_t *cl;

	(void)context;

	if ( !event ) {
		SV_LogSteamServerP2PSessionRequest( NULL, "ignored", "null callback payload" );
		return;
	}

	cl = SV_FindActiveClientBySteamId( &event->remoteId );
	if ( !cl ) {
		SV_LogSteamServerP2PSessionRequest( &event->remoteId, "ignored", "client not found" );
		return;
	}

	SV_LogSteamServerP2PSessionRequest( &event->remoteId, "accepted", "active client match" );
	if ( !QL_Steamworks_ServerAcceptP2PSession( &event->remoteId ) ) {
		SV_LogSteamServerP2PSessionRequest( &event->remoteId, "failed", "accept call failed" );
	}
}

/*
=================
SV_SteamServerGSStatsReceivedCallback

Tracks SteamGameServerStats request completion for the retained stats session.
=================
*/
static void SV_SteamServerGSStatsReceivedCallback( void *context, const ql_steam_gs_stats_received_t *event ) {
	sv_steam_stats_session_t *session;
	char detail[128];

	(void)context;

	if ( !event ) {
		SV_LogSteamStatsLifecycle( NULL, "stats-received", "ignored null callback payload" );
		return;
	}

	session = SV_SteamStats_FindSessionBySteamId( &event->steamId );
	if ( !session ) {
		Com_sprintf( detail, sizeof( detail ), "ignored stats received result=%d for missing session",
			event->result );
		SV_LogSteamStatsLifecycle( &event->steamId, "stats-received", detail );
		return;
	}

	if ( event->result == 1 ) {
		SV_SteamStats_PrimeReceivedValues( session );
		Com_sprintf( detail, sizeof( detail ), "received result=%d appid=%u",
			event->result, session->appId );
	} else {
		session->backendAvailable = qfalse;
		session->requestIssued = qfalse;
		Com_sprintf( detail, sizeof( detail ), "receive failed result=%d appid=%u",
			event->result, session->appId );
	}

	SV_LogSteamStatsLifecycle( &session->steamId, "stats-received", detail );
}

/*
=================
SV_SteamServerGSStatsStoredCallback

Tracks SteamGameServerStats store completion and re-requests values after the
retail partial-validation result.
=================
*/
static void SV_SteamServerGSStatsStoredCallback( void *context, const ql_steam_gs_stats_stored_t *event ) {
	sv_steam_stats_session_t *session;
	char detail[128];

	(void)context;

	if ( !event ) {
		SV_LogSteamStatsLifecycle( NULL, "stats-stored", "ignored null callback payload" );
		return;
	}

	session = SV_SteamStats_FindSessionBySteamId( &event->steamId );
	if ( !session ) {
		Com_sprintf( detail, sizeof( detail ), "ignored stats stored result=%d for missing session",
			event->result );
		SV_LogSteamStatsLifecycle( &event->steamId, "stats-stored", detail );
		return;
	}

	if ( event->result == 1 ) {
		Com_sprintf( detail, sizeof( detail ), "store confirmed result=%d appid=%u",
			event->result, session->appId );
		SV_LogSteamStatsLifecycle( &session->steamId, "stats-stored", detail );
		return;
	}

	if ( event->result == 8 ) {
		Com_sprintf( detail, sizeof( detail ), "store validation warning result=%d appid=%u",
			event->result, session->appId );
		SV_LogSteamStatsLifecycle( &session->steamId, "stats-stored", detail );
		SV_SteamStats_PrimeReceivedValues( session );
		return;
	}

	Com_sprintf( detail, sizeof( detail ), "store failed result=%d appid=%u",
		event->result, session->appId );
	SV_LogSteamStatsLifecycle( &session->steamId, "stats-stored", detail );
}

/*
=================
SV_SteamServerInitCallbacks

Registers the retail Steam GameServer callback bundle with the retained platform layer.
=================
*/
void SV_SteamServerInitCallbacks( void ) {
	ql_steam_server_callback_bindings_t bindings;

	Com_Memset( &bindings, 0, sizeof( bindings ) );
	bindings.onServersConnected = SV_SteamServerConnectedCallback;
	bindings.onConnectFailure = SV_SteamServerConnectFailureCallback;
	bindings.onServersDisconnected = SV_SteamServerDisconnectedCallback;
	bindings.onValidateAuthTicketResponse = SV_SteamServerValidateAuthTicketResponseCallback;
	bindings.onP2PSessionRequest = SV_SteamServerP2PSessionRequestCallback;
	bindings.onGSStatsReceived = SV_SteamServerGSStatsReceivedCallback;
	bindings.onGSStatsStored = SV_SteamServerGSStatsStoredCallback;

	if ( !QL_Steamworks_RegisterServerCallbacks( &bindings ) ) {
		SV_LogSteamServerCallbackBootstrapLifecycle( "unavailable", "register callbacks failed" );
		return;
	}

	sv_steamServerConnected = qfalse;
}
#else
#define SV_CapturePlatformAuthFromUserinfo(cl, userinfo) ((void)0)
#define SV_FinalisePlatformAuthState(cl, accepted, detail) ((void)(cl), (void)(accepted), (void)(detail))
#define SV_LogPlatformAuth(adr, cl, status, detail) ((void)(adr), (void)(cl), (void)(status), (void)(detail))

/*
=================
SV_LogSteamStatsStubLifecycle

Publishes provider-aware diagnostics whenever the retained dedicated-server
stats owner falls back through the build-disabled compatibility stub.
=================
*/
static void SV_LogSteamStatsStubLifecycle( const char *stage, const char *detail ) {
	Com_DPrintf( "Server stats %s via %s [%s]: %s\n",
		stage ? stage : "update",
		SV_GetServerStatsProviderLabel(), SV_GetServerStatsPolicyLabel(),
		detail ? detail : "no detail" );
}

/*
=================
SV_LogSteamServerCallbackBootstrapLifecycle

Publishes provider-aware diagnostics when the retained Steam GameServer
callback bootstrap falls back through the build-disabled stub.
=================
*/
static void SV_LogSteamServerCallbackBootstrapLifecycle( const char *stage, const char *detail ) {
	Com_DPrintf( "Steam server callback bootstrap %s via %s [%s]: %s\n",
		stage ? stage : "update",
		SV_GetSteamServerProviderLabel(),
		SV_GetSteamServerPolicyLabel(),
		detail ? detail : "no detail" );
}

/*
=================
SV_SteamServerInitCallbacks

Build-disabled stub for server auth callback registration.
=================
*/
void SV_SteamServerInitCallbacks( void ) {
	SV_LogSteamServerCallbackBootstrapLifecycle( "unavailable", "build-disabled stub" );
}

/*
=================
SV_SteamServerEndOrphanedAuthSessions

Build-disabled stub for the retained Steam GameServer auth-session cleanup owner.
=================
*/
void SV_SteamServerEndOrphanedAuthSessions( void ) {
}

/*
=================
SV_SteamStats_AddFieldValue

Build-disabled stub for the retained server-owned Steam stat owner.
=================
*/
void SV_SteamStats_AddFieldValue( int clientNum, int statIndex, int delta ) {
	char detail[128];

	if ( delta == 0 ) {
		return;
	}

	Com_sprintf( detail, sizeof( detail ),
		"ignored stat index %d delta %d for client %d", statIndex, delta, clientNum );
	SV_LogSteamStatsStubLifecycle( "field-delta", detail );

	(void)clientNum;
	(void)statIndex;
	(void)delta;
}

/*
=================
SV_SteamStats_UnlockAchievement

Build-disabled stub for the retained server-owned achievement owner.
=================
*/
void SV_SteamStats_UnlockAchievement( int clientNum, int achievementId ) {
	char detail[128];

	Com_sprintf( detail, sizeof( detail ),
		"ignored achievement %d for client %d", achievementId, clientNum );
	SV_LogSteamStatsStubLifecycle( "achievement-unlock", detail );

	(void)clientNum;
	(void)achievementId;
}

/*
=================
SV_SteamStats_HasAchievement

Build-disabled stub for the retained server-owned achievement query.
=================
*/
qboolean SV_SteamStats_HasAchievement( int clientNum, int achievementId ) {
	char detail[128];

	Com_sprintf( detail, sizeof( detail ),
		"query unavailable for achievement %d on client %d", achievementId, clientNum );
	SV_LogSteamStatsStubLifecycle( "achievement-query", detail );

	(void)clientNum;
	(void)achievementId;
	return qfalse;
}

/*
=================
SV_SteamStats_ProcessMatchReport

Build-disabled stub for the retained server-owned Steam stats match-report
processor.
=================
*/
const void *SV_SteamStats_ProcessMatchReport( const void *report, char *buffer, int bufferSize ) {
	SV_LogSteamStatsStubLifecycle( "match-report", "ignored MATCH_REPORT for disabled Steam stats owner" );

	(void)buffer;
	(void)bufferSize;
	return report;
}

/*
=================
SV_SteamStats_ProcessEvent

Build-disabled stub for the retained server-owned Steam stats event processor.
=================
*/
void SV_SteamStats_ProcessEvent( uint32_t steamIdLow, uint32_t steamIdHigh, const void *clientStats, const char *eventName, const void *payload ) {
	char detail[128];

	Com_sprintf( detail, sizeof( detail ),
		"ignored %s event for %llu",
		eventName && eventName[0] ? eventName : "unnamed",
		( (unsigned long long)steamIdHigh << 32 ) | steamIdLow );
	SV_LogSteamStatsStubLifecycle( "event-process", detail );

	(void)clientStats;
	(void)payload;
}
#endif

/*
=================
SV_LogVACStatus

Logs VAC acceptance or rejection alongside shared telemetry.
=================
*/
static void SV_LogVACStatus( const netadr_t *adr, const char *status, const char *outcome, const char *message ) {
	NET_LogAuthTelemetry( NS_SERVER, adr, NULL, "vac", status, NULL, outcome, message );

	if ( message && message[0] ) {
		Com_Printf( "VAC %s (%s) for %s\n", status, message, NET_AdrToString( *adr ) );
	} else {
		Com_Printf( "VAC %s for %s\n", status, NET_AdrToString( *adr ) );
	}
}

/*
=============
SV_ServerTypeAllowsConnection

Validates sv_serverType for incoming connection attempts.
=============
*/
static qboolean SV_ServerTypeAllowsConnection( netadr_t from, char *reason, size_t reasonSize ) {
	int	serverType;

	serverType = sv_serverType ? sv_serverType->integer : 0;

	if ( serverType < 0 || serverType > 2 ) {
		if ( reason && reasonSize ) {
			Com_sprintf( reason, reasonSize, "Invalid server type (%d)", serverType );
		}

		return qfalse;
	}

	if ( serverType == 2 && !NET_IsLocalAddress( from ) ) {
		if ( reason && reasonSize ) {
			Q_strncpyz( reason, "Server is not accepting external connections", reasonSize );
		}

		return qfalse;
	}

	return qtrue;
}

/*
=================
SV_GetChallenge

A "getchallenge" OOB command has been received
Returns a challenge number that can be used
in a subsequent connectResponse command.
We do this to prevent denial of service attacks that
flood the server with invalid connection IPs.  With a
challenge, they must give a valid IP address.

If we are authorizing, a challenge request will cause a packet
to be sent to the authorize server.

When an authorizeip is returned, a challenge response will be
sent to that ip.
=================
*/
void SV_GetChallenge( netadr_t from, msg_t *msg ) {
	int		i;
	int		oldest;
	int		oldestTime;
	challenge_t	*challenge;

	// ignore if we are in single player
	if ( Cvar_VariableValue( "g_gametype" ) == GT_SINGLE_PLAYER || Cvar_VariableValue("ui_singlePlayerActive")) {
		return;
	}

	oldest = 0;
	oldestTime = 0x7fffffff;

	// see if we already have a challenge for this ip
	challenge = &svs.challenges[0];
	for (i = 0 ; i < MAX_CHALLENGES ; i++, challenge++) {
		if ( !challenge->connected && NET_CompareAdr( from, challenge->adr ) ) {
			break;
		}
		if ( challenge->time < oldestTime ) {
			oldestTime = challenge->time;
			oldest = i;
		}
	}

	if (i == MAX_CHALLENGES) {
		// this is the first time this client has asked for a challenge
		challenge = &svs.challenges[oldest];

		challenge->challenge = ( (rand() << 16) ^ rand() ) ^ svs.time;
		challenge->adr = from;
		challenge->firstTime = svs.time;
		challenge->time = svs.time;
		challenge->connected = qfalse;
#if SV_HAS_PLATFORM_AUTH
		SV_ClearChallengePlatformAuth( challenge );
#endif
		i = oldest;
	}

	// if they are on a lan address, send the challengeResponse immediately
	if ( Sys_IsLANAddress( from ) ) {
		challenge->pingTime = svs.time;
		NET_OutOfBandPrint( NS_SERVER, from, "%s %i", NET_GetChallengeResponseCommand(), challenge->challenge );
		return;
	}

#if SV_HAS_PLATFORM_AUTH
	if ( NET_ProtocolSupportsPlatformAuth() ) {
		const char	*rejectMessage;

		if ( !SV_ParseSteamChallengeAuth( challenge, msg, &rejectMessage ) ) {
			NET_OutOfBandPrint( NS_SERVER, from, "%s\n%s\n", NET_GetPrintCommand(),
				rejectMessage ? rejectMessage : "No Steam auth token." );
			return;
		}

		challenge->pingTime = svs.time;
		NET_OutOfBandPrint( NS_SERVER, from, "%s %i", NET_GetChallengeResponseCommand(), challenge->challenge );
		return;
	}
#endif

#if !( QL_PLATFORM_HAS_ONLINE_SERVICES && QL_ENABLE_LEGACY_Q3_SERVICES )
	Com_DPrintf( "legacy getIpAuthorize bypassed for %s: Quake III authorize server disabled by online-services policy\n", NET_AdrToString( from ) );
	challenge->pingTime = svs.time;
	NET_OutOfBandPrint( NS_SERVER, from, "%s %i", NET_GetChallengeResponseCommand(), challenge->challenge );
	return;
#else
	if ( !NET_ProtocolUsesLegacyAuthorize() ) {
		Com_DPrintf( "legacy getIpAuthorize bypassed for %s: protocol profile %s does not use the Quake III authorize lane\n",
			NET_AdrToString( from ), NET_ProtocolName() );
		challenge->pingTime = svs.time;
		NET_OutOfBandPrint( NS_SERVER, from, "%s %i", NET_GetChallengeResponseCommand(), challenge->challenge );
		return;
	}

	// look up the authorize server's IP
	if ( !svs.authorizeAddress.ip[0] && svs.authorizeAddress.type != NA_BAD ) {
		Com_Printf( "Resolving %s\n", AUTHORIZE_SERVER_NAME );
		if ( !NET_StringToAdr( AUTHORIZE_SERVER_NAME, &svs.authorizeAddress ) ) {
			Com_Printf( "Couldn't resolve address\n" );
			return;
		}
		svs.authorizeAddress.port = BigShort( PORT_AUTHORIZE );
		Com_Printf( "%s resolved to %i.%i.%i.%i:%i\n", AUTHORIZE_SERVER_NAME,
			svs.authorizeAddress.ip[0], svs.authorizeAddress.ip[1],
			svs.authorizeAddress.ip[2], svs.authorizeAddress.ip[3],
			BigShort( svs.authorizeAddress.port ) );
	}

	// if they have been challenging for a long time and we
	// haven't heard anything from the authorize server, go ahead and
	// let them in, assuming the id server is down
	if ( svs.time - challenge->firstTime > AUTHORIZE_TIMEOUT ) {
		Com_DPrintf( "authorize server timed out\n" );

		challenge->pingTime = svs.time;
		NET_OutOfBandPrint( NS_SERVER, challenge->adr, 
			"%s %i", NET_GetChallengeResponseCommand(), challenge->challenge );
		return;
	}

	// otherwise send their ip to the authorize server
	if ( svs.authorizeAddress.type != NA_BAD ) {
		cvar_t	*fs;
		char	game[1024];

		Com_DPrintf( "sending %s for %s\n", NET_GetIpAuthorizeRequestCommand(), NET_AdrToString( from ));
		
		strcpy(game, BASEGAME);
		fs = Cvar_Get ("fs_game", "", CVAR_INIT|CVAR_SYSTEMINFO );
		if (fs && fs->string[0] != 0) {
			strcpy(game, fs->string);
		}
		
		// the 0 is for backwards compatibility with obsolete sv_allowanonymous flags
		// legacy authorize: <challenge> <IP> <game> 0 <auth-flag>
		NET_OutOfBandPrint( NS_SERVER, svs.authorizeAddress,
			"%s %i %i.%i.%i.%i %s 0 %s", NET_GetIpAuthorizeRequestCommand(), svs.challenges[i].challenge,
			from.ip[0], from.ip[1], from.ip[2], from.ip[3], game, sv_strictAuth->string );
	}
#endif
}

/*
====================
SV_AuthorizeIpPacket

A packet has been returned from the authorize server.
If we have a challenge adr for that ip, send the
challengeResponse to it
====================
*/
void SV_AuthorizeIpPacket( netadr_t from ) {
#if !( QL_PLATFORM_HAS_ONLINE_SERVICES && QL_ENABLE_LEGACY_Q3_SERVICES )
	Com_DPrintf( "SV_AuthorizeIpPacket ignored: Quake III authorize server disabled by online-services policy\n" );
	return;
#else
	int		challenge;
	int		i;
	char	*s;
	char	*r;
	char	ret[1024];

	if ( !NET_CompareBaseAdr( from, svs.authorizeAddress ) ) {
		Com_Printf( "SV_AuthorizeIpPacket: not from authorize server\n" );
		return;
	}

	challenge = atoi( Cmd_Argv( 1 ) );

	for (i = 0 ; i < MAX_CHALLENGES ; i++) {
		if ( svs.challenges[i].challenge == challenge ) {
			break;
		}
	}
	if ( i == MAX_CHALLENGES ) {
		Com_Printf( "SV_AuthorizeIpPacket: challenge not found\n" );
		return;
	}

	// send a packet back to the original client
	svs.challenges[i].pingTime = svs.time;
	s = Cmd_Argv( 2 );
	r = Cmd_Argv( 3 );			// reason

	if ( !Q_stricmp( s, "demo" ) ) {
		if ( Cvar_VariableValue( "fs_restrict" ) ) {
			// a demo client connecting to a demo server
			NET_OutOfBandPrint( NS_SERVER, svs.challenges[i].adr, 
				"%s %i", NET_GetChallengeResponseCommand(), svs.challenges[i].challenge );
			return;
		}
		// they are a demo client trying to connect to a real server
		NET_OutOfBandPrint( NS_SERVER, svs.challenges[i].adr, "%s\nServer is not a demo server\n", NET_GetPrintCommand() );
		// clear the challenge record so it won't timeout and let them through
		Com_Memset( &svs.challenges[i], 0, sizeof( svs.challenges[i] ) );
		return;
	}
	if ( !Q_stricmp( s, "accept" ) ) {
		NET_OutOfBandPrint( NS_SERVER, svs.challenges[i].adr, 
			"%s %i", NET_GetChallengeResponseCommand(), svs.challenges[i].challenge );
		return;
	}
	if ( !Q_stricmp( s, "unknown" ) ) {
		if ( !r ) {
			NET_OutOfBandPrint( NS_SERVER, svs.challenges[i].adr, "%s\nAwaiting credential authorization\n", NET_GetPrintCommand() );
		} else {
			Com_sprintf( ret, sizeof( ret ), "%s\n%s\n", NET_GetPrintCommand(), r );
			NET_OutOfBandPrint( NS_SERVER, svs.challenges[i].adr, "%s", ret );
		}
		// clear the challenge record so it won't timeout and let them through
		Com_Memset( &svs.challenges[i], 0, sizeof( svs.challenges[i] ) );
		return;
	}

	// authorization failed
	if ( !r ) {
		NET_OutOfBandPrint( NS_SERVER, svs.challenges[i].adr, "%s\nSomeone is using this credential\n", NET_GetPrintCommand() );
	} else {
		Com_sprintf( ret, sizeof( ret ), "%s\n%s\n", NET_GetPrintCommand(), r );
		NET_OutOfBandPrint( NS_SERVER, svs.challenges[i].adr, "%s", ret );
	}

	// clear the challenge record so it won't timeout and let them through
	Com_Memset( &svs.challenges[i], 0, sizeof( svs.challenges[i] ) );
#endif
}

/*
==================
SV_DirectConnect

A "connect" OOB command has been received
==================
*/

#define PB_MESSAGE "PunkBuster Anti-Cheat software must be installed " \
				"and Enabled in order to join this server. An updated game patch can be downloaded from " \
				"www.idsoftware.com"

void SV_DirectConnect( netadr_t from ) {
	char		userinfo[MAX_INFO_STRING];
	int			i;
	client_t	*cl, *newcl;
	MAC_STATIC client_t	temp;
	sharedEntity_t *ent;
	int			clientNum;
	int			version;
	int			qport;
	int			challenge;
	char		*password;
	int			startIndex;
	const char	*denied;
	int			count;
	int			challengeIndex;
	char		 serverTypeError[MAX_STRING_CHARS];

	Com_DPrintf ("SVC_DirectConnect ()\n");

	Q_strncpyz( userinfo, Cmd_Argv(1), sizeof(userinfo) );

	version = atoi( Info_ValueForKey( userinfo, NET_GetProtocolInfoKey() ) );
	if ( !NET_ProtocolSupports( version ) ) {
		NET_OutOfBandPrint( NS_SERVER, from, "%s\nServer uses protocol version %i.\n", NET_GetPrintCommand(), NET_ProtocolVersion() );
		Com_DPrintf ("    rejected connect from version %i\n", version);
		return;
	}

	challenge = atoi( Info_ValueForKey( userinfo, NET_GetChallengeInfoKey() ) );
	if ( NET_ProtocolUsesClientQport() ) {
		qport = atoi( Info_ValueForKey( userinfo, NET_GetQportInfoKey() ) );
	} else {
		qport = 0;
	}

	serverTypeError[0] = '\0';

	if ( !SV_ServerTypeAllowsConnection( from, serverTypeError, sizeof( serverTypeError ) ) ) {
		const char *errorMessage;

		errorMessage = serverTypeError[0] ? serverTypeError : "Server is not accepting connections";
		NET_OutOfBandPrint( NS_SERVER, from, "%s\n%s\n", NET_GetPrintCommand(), errorMessage );
		return;
	}

	// quick reject
	for (i=0,cl=svs.clients ; i < sv_maxclients->integer ; i++,cl++) {
		if ( cl->state == CS_FREE ) {
			continue;
		}
		if ( NET_CompareBaseAdr( from, cl->netchan.remoteAddress )
			&& ( cl->netchan.qport == qport 
			|| from.port == cl->netchan.remoteAddress.port ) ) {
			if (( svs.time - cl->lastConnectTime) 
				< (sv_reconnectlimit->integer * 1000)) {
				Com_DPrintf ("%s:reconnect rejected : too soon\n", NET_AdrToString (from));
				return;
			}
			break;
		}
	}

	// see if the challenge is valid (LAN clients don't need to challenge)
	challengeIndex = -1;
	if ( !NET_IsLocalAddress (from) ) {
		int		ping;

		for (i=0 ; i<MAX_CHALLENGES ; i++) {
			if (NET_CompareAdr(from, svs.challenges[i].adr)) {
				if ( challenge == svs.challenges[i].challenge ) {
					break;		// good
				}
			}
		}
		if (i == MAX_CHALLENGES) {
			NET_OutOfBandPrint( NS_SERVER, from, "%s\nNo or bad challenge for address.\n", NET_GetPrintCommand() );
			return;
		}
		challengeIndex = i;
		// force the IP key/value pair so the game can filter based on ip
		Info_SetValueForKey( userinfo, NET_GetClientIpInfoKey(), NET_AdrToString( from ) );

		ping = svs.time - svs.challenges[i].pingTime;
		Com_Printf( "Client %i connecting with %i challenge ping\n", i, ping );
		svs.challenges[i].connected = qtrue;

		// never reject a LAN client based on ping
		if ( !Sys_IsLANAddress( from ) ) {
			if ( sv_minPing->value && ping < sv_minPing->value ) {
				// don't let them keep trying until they get a big delay
				NET_OutOfBandPrint( NS_SERVER, from, "%s\nServer is for high pings only\n", NET_GetPrintCommand() );
				Com_DPrintf ("Client %i rejected on a too low ping\n", i);
				// reset the address otherwise their ping will keep increasing
				// with each connect message and they'd eventually be able to connect
				svs.challenges[i].adr.port = 0;
				return;
			}
			if ( sv_maxPing->value && ping > sv_maxPing->value ) {
				NET_OutOfBandPrint( NS_SERVER, from, "%s\nServer is for low pings only\n", NET_GetPrintCommand() );
				Com_DPrintf ("Client %i rejected on a too high ping\n", i);
				return;
			}
		}
	} else {
		// force the client IP info key to "localhost"
		Info_SetValueForKey( userinfo, NET_GetClientIpInfoKey(), "localhost" );
	}

	SV_LogVACStatus( &from, "accepted", ( sv_vac && sv_vac->integer ) ? "enabled" : "disabled",
		( sv_vac && sv_vac->integer ) ? "VAC is enabled on this server" : NULL );

	newcl = &temp;
	Com_Memset (newcl, 0, sizeof(client_t));

	// if there is already a slot for this ip, reuse it
	for (i=0,cl=svs.clients ; i < sv_maxclients->integer ; i++,cl++) {
		if ( cl->state == CS_FREE ) {
			continue;
		}
		if ( NET_CompareBaseAdr( from, cl->netchan.remoteAddress )
			&& ( cl->netchan.qport == qport 
			|| from.port == cl->netchan.remoteAddress.port ) ) {
			Com_Printf ("%s:reconnect\n", NET_AdrToString (from));
			newcl = cl;

			// this doesn't work because it nukes the players userinfo

//			// disconnect the client from the game first so any flags the
//			// player might have are dropped
//			VM_Call( gvm, GAME_CLIENT_DISCONNECT, newcl - svs.clients );
			//
			goto gotnewcl;
		}
	}

	// find a client slot
	// if "sv_privateClients" is set > 0, then that number
	// of client slots will be reserved for connections that
	// have "password" set to the value of "sv_privatePassword"
	// Info requests will report the maxclients as if the private
	// slots didn't exist, to prevent people from trying to connect
	// to a full server.
	// This is to allow us to reserve a couple slots here on our
	// servers so we can play without having to kick people.

	// check for privateClient password
	password = Info_ValueForKey( userinfo, NET_GetPasswordInfoKey() );
	if ( !strcmp( password, sv_privatePassword->string ) ) {
		startIndex = 0;
	} else {
		// skip past the reserved slots
		startIndex = sv_privateClients->integer;
	}

	newcl = NULL;
	for ( i = startIndex; i < sv_maxclients->integer ; i++ ) {
		cl = &svs.clients[i];
		if (cl->state == CS_FREE) {
			newcl = cl;
			break;
		}
	}

	if ( !newcl ) {
		if ( NET_IsLocalAddress( from ) ) {
			qboolean onlyBots = qtrue;
			int lastBotSlot = -1;

			for ( i = startIndex; i < sv_maxclients->integer ; i++ ) {
				cl = &svs.clients[i];

				if ( cl->state == CS_FREE ) {
					onlyBots = qfalse;
					break;
				}

				if ( !SV_ClientIsBot( cl ) ) {
					onlyBots = qfalse;
					break;
				}

				lastBotSlot = i;
			}

			if ( onlyBots && lastBotSlot >= startIndex ) {
				SV_DropClient( &svs.clients[lastBotSlot], "only bots on server" );
				newcl = &svs.clients[lastBotSlot];
			} else {
				Com_Error( ERR_FATAL, "server is full on local connect\n" );
				return;
			}
		}
		else {
			NET_OutOfBandPrint( NS_SERVER, from, "%s\nServer is full.\n", NET_GetPrintCommand() );
			Com_DPrintf ("Rejected a connection.\n");
			return;
		}
	}

	// we got a newcl, so reset the reliableSequence and reliableAcknowledge
	cl->reliableAcknowledge = 0;
	cl->reliableSequence = 0;

gotnewcl:
	// build a new connection
	// accept the new client
	// this is the only place a client_t is ever initialized
	*newcl = temp;
	clientNum = newcl - svs.clients;
	ent = SV_GentityNum( clientNum );
	newcl->gentity = ent;
	newcl->isBot = qfalse;

	// save the challenge
	newcl->challenge = challenge;


	// save the address
	Netchan_Setup (NS_SERVER, &newcl->netchan , from, qport);
	// init the netchan queue
	newcl->netchan_end_queue = &newcl->netchan_start_queue;

	// save the userinfo
	Q_strncpyz( newcl->userinfo, userinfo, sizeof(newcl->userinfo) );

#if SV_HAS_PLATFORM_AUTH
	{
		char tokenSummary[64];
		qboolean capturedFromChallenge;

		capturedFromChallenge = ( challengeIndex >= 0 )
			? SV_CapturePlatformAuthFromChallenge( newcl, &svs.challenges[challengeIndex] )
			: qfalse;

		if ( !capturedFromChallenge ) {
			SV_CapturePlatformAuthFromUserinfo( newcl, userinfo );
		}

		if ( newcl->platformSteamId[0] ) {
			Info_SetValueForKey( userinfo, "steam", newcl->platformSteamId );
			Info_SetValueForKey( userinfo, "steamid", newcl->platformSteamId );
			Q_strncpyz( newcl->userinfo, userinfo, sizeof( newcl->userinfo ) );
		}

		if ( newcl->platformAuthPending && newcl->platformAuthToken[0] ) {
			Com_sprintf( tokenSummary, sizeof( tokenSummary ), "token_len=%i", (int)strlen( newcl->platformAuthToken ) );
			SV_LogPlatformAuth( &from, newcl, "connect", tokenSummary );
		} else {
			SV_LogPlatformAuth( &from, newcl, "connect", "token_absent" );
		}
	}
#endif

	// get the game a chance to reject this connection or modify the userinfo
	denied = SV_GameClientConnect( clientNum, qtrue, qfalse ); // firstTime = qtrue
	if ( denied ) {
#if SV_HAS_PLATFORM_AUTH
		SV_FinalisePlatformAuthState( newcl, qfalse, denied );
		SV_LogPlatformAuth( &from, newcl, "denied", denied );
#endif

		NET_OutOfBandPrint( NS_SERVER, from, "%s\n%s\n", NET_GetPrintCommand(), denied );
		Com_DPrintf ("Game rejected a connection: %s.\n", denied);
		return;
	}

#if SV_HAS_PLATFORM_AUTH
	denied = SV_BeginPlatformAuthSession( newcl, &from );
	if ( denied ) {
		NET_OutOfBandPrint( NS_SERVER, from, "%s\n%s\n", NET_GetPrintCommand(), denied );
		return;
	}
#endif

	SV_UserinfoChanged( newcl );

	// send the connect packet to the client
	NET_OutOfBandPrint( NS_SERVER, from, "%s", NET_GetConnectResponseCommand() );

	Com_DPrintf( "Going from CS_FREE to CS_CONNECTED for %s\n", newcl->name );

	newcl->state = CS_CONNECTED;
	SV_BotRefreshEntityBotFlag( newcl );
	newcl->nextSnapshotTime = svs.time;
	newcl->lastPacketTime = svs.time;
	newcl->lastConnectTime = svs.time;
	
	// when we receive the first packet from the client, we will
	// notice that it is from a different serverid and that the
	// gamestate message was not just sent, forcing a retransmit
	newcl->gamestateMessageNum = -1;

	// if this was the first client on the server, or the last client
	// the server can hold, send a heartbeat to the master.
	count = 0;
	for (i=0,cl=svs.clients ; i < sv_maxclients->integer ; i++,cl++) {
		if ( svs.clients[i].state >= CS_CONNECTED ) {
			count++;
		}
	}
	if ( count == 1 || count == sv_maxclients->integer ) {
		SV_Heartbeat_f();
	}
}


/*
=====================
SV_DropClient

Called when the player is totally leaving the server, either willingly
or unwillingly.  This is NOT called if the entire server is quiting
or crashing -- SV_FinalMessage() will handle that
=====================
*/
void SV_DropClient( client_t *drop, const char *reason ) {
	int		i;
	challenge_t	*challenge;
	qboolean	wasBot;

	if ( drop->state == CS_ZOMBIE ) {
		return;		// already dropped
	}

	wasBot = SV_ClientIsBot( drop );

	if ( !wasBot ) {
		// see if we already have a challenge for this ip
		challenge = &svs.challenges[0];

		for (i = 0 ; i < MAX_CHALLENGES ; i++, challenge++) {
			if ( NET_CompareAdr( drop->netchan.remoteAddress, challenge->adr ) ) {
				challenge->connected = qfalse;
				break;
			}
		}
	}

	// Kill any download
	SV_CloseDownload( drop );

	// tell everyone why they got dropped
	SV_SendServerCommand( NULL, "print \"%s" S_COLOR_WHITE " %s\n\"", drop->name, reason );

	Com_DPrintf( "Going to CS_ZOMBIE for %s\n", drop->name );
	drop->state = CS_ZOMBIE;		// become free in a few seconds

	if (drop->download)	{
		FS_FCloseFile( drop->download );
		drop->download = 0;
	}

	// call the prog function for removing a client
	// this will remove the body, among other things
	VM_Call( gvm, GAME_CLIENT_DISCONNECT, drop - svs.clients );

	// add the disconnect command
	SV_SendServerCommand( drop, "%s \"%s\"", NET_GetReliableDisconnectCommand(), reason);

	if ( wasBot ) {
		SV_BotFreeClient( drop - svs.clients );
	}

#if SV_HAS_PLATFORM_AUTH
	SV_EndPlatformAuthSession( drop );
#endif

	// nuke user info
	SV_SetUserinfo( drop - svs.clients, "" );

	// if this was the last client on the server, send a heartbeat
	// to the master so it is known the server is empty
	// send a heartbeat now so the master will get up to date info
	// if there is already a slot for this ip, reuse it
	for (i=0 ; i < sv_maxclients->integer ; i++ ) {
		if ( svs.clients[i].state >= CS_CONNECTED ) {
			break;
		}
	}
	if ( i == sv_maxclients->integer ) {
		SV_Heartbeat_f();
	}
}

/*
================
SV_SendClientGameState

Sends the first message from the server to a connected client.
This will be sent on the initial connection and upon each new map load.

It will be resent if the client acknowledges a later message but has
the wrong gamestate.
================
*/
void SV_SendClientGameState( client_t *client ) {
	int			start;
	entityState_t	*base, nullstate;
	msg_t		msg;
	byte		msgBuffer[MAX_MSGLEN];

 	Com_DPrintf ("SV_SendClientGameState() for %s\n", client->name);
	Com_DPrintf( "Going from CS_CONNECTED to CS_PRIMED for %s\n", client->name );
	client->state = CS_PRIMED;
	client->pureAuthentic = 0;
	client->gotCP = qfalse;

	// when we receive the first packet from the client, we will
	// notice that it is from a different serverid and that the
	// gamestate message was not just sent, forcing a retransmit
	client->gamestateMessageNum = client->netchan.outgoingSequence;

	MSG_Init( &msg, msgBuffer, sizeof( msgBuffer ) );

	// NOTE, MRE: all server->client messages now acknowledge
	// let the client know which reliable clientCommands we have received
	MSG_WriteLong( &msg, client->lastClientCommand );

	// send any server commands waiting to be sent first.
	// we have to do this cause we send the client->reliableSequence
	// with a gamestate and it sets the clc.serverCommandSequence at
	// the client side
	SV_UpdateServerCommandsToClient( client, &msg );

	// send the gamestate
	MSG_WriteByte( &msg, svc_gamestate );
	MSG_WriteLong( &msg, client->reliableSequence );

	// write the configstrings
	for ( start = 0 ; start < MAX_CONFIGSTRINGS ; start++ ) {
		if (sv.configstrings[start][0]) {
			MSG_WriteByte( &msg, svc_configstring );
			MSG_WriteShort( &msg, start );
			MSG_WriteBigString( &msg, sv.configstrings[start] );
		}
	}

	// write the baselines
	Com_Memset( &nullstate, 0, sizeof( nullstate ) );
	for ( start = 0 ; start < MAX_GENTITIES; start++ ) {
		base = &sv.svEntities[start].baseline;
		if ( !base->number ) {
			continue;
		}
		MSG_WriteByte( &msg, svc_baseline );
		MSG_WriteDeltaEntity( &msg, &nullstate, base, qtrue );
	}

	MSG_WriteByte( &msg, svc_EOF );

	MSG_WriteLong( &msg, client - svs.clients);

	// write the checksum feed
	MSG_WriteLong( &msg, sv.checksumFeed);

	// deliver this to the client
	SV_SendMessageToClient( &msg, client );
}


/*
==================
SV_ClientEnterWorld
==================
*/
void SV_ClientEnterWorld( client_t *client, usercmd_t *cmd ) {
	int		clientNum;
	sharedEntity_t *ent;

	Com_DPrintf( "Going from CS_PRIMED to CS_ACTIVE for %s\n", client->name );
	client->state = CS_ACTIVE;

	// set up the entity for the client
	clientNum = client - svs.clients;
	ent = SV_GentityNum( clientNum );
	ent->s.number = clientNum;
	client->gentity = ent;
	SV_BotRefreshEntityBotFlag( client );

	client->deltaMessage = -1;
	client->nextSnapshotTime = svs.time;	// generate a snapshot immediately
	client->lastUsercmd = *cmd;

	// call the game begin function
	VM_Call( gvm, GAME_CLIENT_BEGIN, client - svs.clients );
}

/*
============================================================

CLIENT COMMAND EXECUTION

============================================================
*/

/*
==================
SV_CloseDownload

clear/free any download vars
==================
*/
static void SV_CloseDownload( client_t *cl ) {
	int i;

	// EOF
	if (cl->download) {
		FS_FCloseFile( cl->download );
	}
	cl->download = 0;
	*cl->downloadName = 0;

	// Free the temporary buffer space
	for (i = 0; i < MAX_DOWNLOAD_WINDOW; i++) {
		if (cl->downloadBlocks[i]) {
			Z_Free( cl->downloadBlocks[i] );
			cl->downloadBlocks[i] = NULL;
		}
	}

}

/*
==================
SV_StopDownload_f

Abort a download if in progress
==================
*/
void SV_StopDownload_f( client_t *cl ) {
	if (*cl->downloadName)
		Com_DPrintf( "clientDownload: %d : file \"%s\" aborted\n", cl - svs.clients, cl->downloadName );

	SV_CloseDownload( cl );
}

/*
==================
SV_DoneDownload_f

Downloads are finished
==================
*/
void SV_DoneDownload_f( client_t *cl ) {
	Com_DPrintf( "clientDownload: %s Done\n", cl->name);
	// resend the game state to update any clients that entered during the download
	if ( cl->state != CS_ACTIVE ) {
		SV_SendClientGameState( cl );
	}
}

/*
==================
SV_NextDownload_f

The argument will be the last acknowledged block from the client, it should be
the same as cl->downloadClientBlock
==================
*/
void SV_NextDownload_f( client_t *cl )
{
	int block = atoi( Cmd_Argv(1) );

	if (block == cl->downloadClientBlock) {
		Com_DPrintf( "clientDownload: %d : client acknowledge of block %d\n", cl - svs.clients, block );

		// Find out if we are done.  A zero-length block indicates EOF
		if (cl->downloadBlockSize[cl->downloadClientBlock % MAX_DOWNLOAD_WINDOW] == 0) {
			Com_Printf( "clientDownload: %d : file \"%s\" completed\n", cl - svs.clients, cl->downloadName );
			SV_CloseDownload( cl );
			return;
		}

		cl->downloadSendTime = svs.time;
		cl->downloadClientBlock++;
		return;
	}
	// We aren't getting an acknowledge for the correct block, drop the client
	// FIXME: this is bad... the client will never parse the disconnect message
	//			because the cgame isn't loaded yet
	SV_DropClient( cl, "broken download" );
}

/*
==================
SV_BeginDownload_f
==================
*/
void SV_BeginDownload_f( client_t *cl ) {

	// Kill any existing download
	SV_CloseDownload( cl );

	Com_DPrintf( "clientDownload: %d : legacy UDP download request \"%s\" ignored in Quake Live retail snapshot path\n",
		cl - svs.clients, Cmd_Argv(1) );
}

/*
==================
SV_WriteDownloadToClient

Check to see if the client wants a file, open it if needed and start pumping the client
Fill up msg with data 
==================
*/
void SV_WriteDownloadToClient( client_t *cl , msg_t *msg )
{
	int curindex;
	int rate;
	int blockspersnap;
	int idPack, missionPack;
	char errorMessage[1024];

	if (!*cl->downloadName)
		return;	// Nothing being downloaded

	if (!cl->download) {
		// We open the file here

		Com_Printf( "clientDownload: %d : begining \"%s\"\n", cl - svs.clients, cl->downloadName );

		missionPack = FS_idPak(cl->downloadName, "missionpack");
		idPack = missionPack || FS_idPak(cl->downloadName, BASEGAME);

		if ( !sv_allowDownload->integer || idPack ||
			( cl->downloadSize = FS_SV_FOpenFileRead( cl->downloadName, &cl->download ) ) <= 0 ) {
			// cannot auto-download file
			if (idPack) {
				Com_Printf("clientDownload: %d : \"%s\" cannot download id pk3 files\n", cl - svs.clients, cl->downloadName);
				if (missionPack) {
					Com_sprintf(errorMessage, sizeof(errorMessage), "Cannot autodownload Team Arena file \"%s\"\n"
									"The Team Arena mission pack can be found in your local game store.", cl->downloadName);
				}
				else {
					Com_sprintf(errorMessage, sizeof(errorMessage), "Cannot autodownload id pk3 file \"%s\"", cl->downloadName);
				}
			} else if ( !sv_allowDownload->integer ) {
				Com_Printf("clientDownload: %d : \"%s\" download disabled", cl - svs.clients, cl->downloadName);
				if (sv_pure->integer) {
					Com_sprintf(errorMessage, sizeof(errorMessage), "Could not download \"%s\" because autodownloading is disabled on the server.\n\n"
										"You will need to get this file elsewhere before you "
										"can connect to this pure server.\n", cl->downloadName);
				} else {
					Com_sprintf(errorMessage, sizeof(errorMessage), "Could not download \"%s\" because autodownloading is disabled on the server.\n\n"
                    "The server you are connecting to is not a pure server, "
                    "set autodownload to No in your settings and you might be "
                    "able to join the game anyway.\n", cl->downloadName);
				}
			} else {
        // NOTE TTimo this is NOT supposed to happen unless bug in our filesystem scheme?
        //   if the pk3 is referenced, it must have been found somewhere in the filesystem
				Com_Printf("clientDownload: %d : \"%s\" file not found on server\n", cl - svs.clients, cl->downloadName);
				Com_sprintf(errorMessage, sizeof(errorMessage), "File \"%s\" not found on server for autodownloading.\n", cl->downloadName);
			}
			MSG_WriteByte( msg, svc_download );
			MSG_WriteShort( msg, 0 ); // client is expecting block zero
			MSG_WriteLong( msg, -1 ); // illegal file size
			MSG_WriteString( msg, errorMessage );

			*cl->downloadName = 0;
			return;
		}
 
		// Init
		cl->downloadCurrentBlock = cl->downloadClientBlock = cl->downloadXmitBlock = 0;
		cl->downloadCount = 0;
		cl->downloadEOF = qfalse;
	}

	// Perform any reads that we need to
	while (cl->downloadCurrentBlock - cl->downloadClientBlock < MAX_DOWNLOAD_WINDOW &&
		cl->downloadSize != cl->downloadCount) {

		curindex = (cl->downloadCurrentBlock % MAX_DOWNLOAD_WINDOW);

		if (!cl->downloadBlocks[curindex])
			cl->downloadBlocks[curindex] = Z_Malloc( MAX_DOWNLOAD_BLKSIZE );

		cl->downloadBlockSize[curindex] = FS_Read( cl->downloadBlocks[curindex], MAX_DOWNLOAD_BLKSIZE, cl->download );

		if (cl->downloadBlockSize[curindex] < 0) {
			// EOF right now
			cl->downloadCount = cl->downloadSize;
			break;
		}

		cl->downloadCount += cl->downloadBlockSize[curindex];

		// Load in next block
		cl->downloadCurrentBlock++;
	}

	// Check to see if we have eof condition and add the EOF block
	if (cl->downloadCount == cl->downloadSize &&
		!cl->downloadEOF &&
		cl->downloadCurrentBlock - cl->downloadClientBlock < MAX_DOWNLOAD_WINDOW) {

		cl->downloadBlockSize[cl->downloadCurrentBlock % MAX_DOWNLOAD_WINDOW] = 0;
		cl->downloadCurrentBlock++;

		cl->downloadEOF = qtrue;  // We have added the EOF block
	}

	// Loop up to window size times based on how many blocks we can fit in the
	// client snapMsec and rate

	// based on the rate, how many bytes can we fit in the snapMsec time of the client
	// normal rate / snapshotMsec calculation
	rate = cl->rate;
	if ( sv_maxRate->integer ) {
		if ( sv_maxRate->integer < 1000 ) {
			Cvar_Set( "sv_MaxRate", "1000" );
		}
		if ( sv_maxRate->integer < rate ) {
			rate = sv_maxRate->integer;
		}
	}

	if (!rate) {
		blockspersnap = 1;
	} else {
		blockspersnap = ( (rate * cl->snapshotMsec) / 1000 + MAX_DOWNLOAD_BLKSIZE ) /
			MAX_DOWNLOAD_BLKSIZE;
	}

	if (blockspersnap < 0)
		blockspersnap = 1;

	while (blockspersnap--) {

		// Write out the next section of the file, if we have already reached our window,
		// automatically start retransmitting

		if (cl->downloadClientBlock == cl->downloadCurrentBlock)
			return; // Nothing to transmit

		if (cl->downloadXmitBlock == cl->downloadCurrentBlock) {
			// We have transmitted the complete window, should we start resending?

			//FIXME:  This uses a hardcoded one second timeout for lost blocks
			//the timeout should be based on client rate somehow
			if (svs.time - cl->downloadSendTime > 1000)
				cl->downloadXmitBlock = cl->downloadClientBlock;
			else
				return;
		}

		// Send current block
		curindex = (cl->downloadXmitBlock % MAX_DOWNLOAD_WINDOW);

		MSG_WriteByte( msg, svc_download );
		MSG_WriteShort( msg, cl->downloadXmitBlock );

		// block zero is special, contains file size
		if ( cl->downloadXmitBlock == 0 )
			MSG_WriteLong( msg, cl->downloadSize );
 
		MSG_WriteShort( msg, cl->downloadBlockSize[curindex] );

		// Write the block
		if ( cl->downloadBlockSize[curindex] ) {
			MSG_WriteData( msg, cl->downloadBlocks[curindex], cl->downloadBlockSize[curindex] );
		}

		Com_DPrintf( "clientDownload: %d : writing block %d\n", cl - svs.clients, cl->downloadXmitBlock );

		// Move on to the next block
		// It will get sent with next snap shot.  The rate will keep us in line.
		cl->downloadXmitBlock++;

		cl->downloadSendTime = svs.time;
	}
}

/*
=================
SV_Disconnect_f

The client is going to disconnect, so remove the connection immediately  FIXME: move to game?
=================
*/
static void SV_Disconnect_f( client_t *cl ) {
	SV_DropClient( cl, "disconnected" );
}

/*
=================
SV_VerifyPaks_f

If we are pure, disconnect the client if they do no meet the following conditions:

1. the first two checksums match our view of cgame and ui
2. there are no any additional checksums that we do not have

This routine would be a bit simpler with a goto but i abstained

=================
*/
static void SV_VerifyPaks_f( client_t *cl ) {
	int nBinChkSum, nChkSum1, nClientPaks, nServerPaks, i, j, nCurArg;
	int nClientChkSum[1024];
	int nServerChkSum[1024];
	const char *pPaks, *pArg;
	qboolean bGood = qtrue;

	// if we are pure, we "expect" the client to load certain things from 
	// certain pk3 files, namely we want the client to have loaded the
	// ui and cgame that we think should be loaded based on the pure setting
	//
	if ( sv_pure->integer != 0 ) {

		bGood = qtrue;
		nBinChkSum = nChkSum1 = 0;
		// Quake Live pure mode verifies a single binary pack checksum before the delimiter.
		bGood = (FS_FileIsInPAK("cgamex86.dll", &nBinChkSum) == 1);

		nClientPaks = Cmd_Argc();

		// start at arg 2 ( skip serverId cl_paks )
		nCurArg = 1;

		pArg = Cmd_Argv(nCurArg++);
		if(!pArg) {
			bGood = qfalse;
		}
		else
		{
			// https://zerowing.idsoftware.com/bugzilla/show_bug.cgi?id=475
			// we may get incoming cp sequences from a previous checksumFeed, which we need to ignore
			// since serverId is a frame count, it always goes up
			if (atoi(pArg) < sv.checksumFeedServerId)
			{
				Com_DPrintf("ignoring outdated cp command from client %s\n", cl->name);
				return;
			}
		}
	
		// we basically use this while loop to avoid using 'goto' :)
		while (bGood) {

			// must be at least 6: "serverId bin @ firstref ... numChecksums"
			// numChecksums is encoded
			if (nClientPaks < 6) {
				bGood = qfalse;
				break;
			}
			// verify first to be the binary checksum
			pArg = Cmd_Argv(nCurArg++);
			if (!pArg || *pArg == '@' || atoi(pArg) != nBinChkSum ) {
				bGood = qfalse;
				break;
			}
			// should be sitting at the delimeter now
			pArg = Cmd_Argv(nCurArg++);
			if (!pArg || *pArg != '@') {
				bGood = qfalse;
				break;
			}
			// store checksums since tokenization is not re-entrant
			for (i = 0; nCurArg < nClientPaks; i++) {
				nClientChkSum[i] = atoi(Cmd_Argv(nCurArg++));
			}

			// store number to compare against (minus one cause the last is the number of checksums)
			nClientPaks = i - 1;

			// make sure none of the client check sums are the same
			// so the client can't send 5 the same checksums
			for (i = 0; i < nClientPaks; i++) {
				for (j = 0; j < nClientPaks; j++) {
					if (i == j)
						continue;
					if (nClientChkSum[i] == nClientChkSum[j]) {
						bGood = qfalse;
						break;
					}
				}
				if (bGood == qfalse)
					break;
			}
			if (bGood == qfalse)
				break;

			// get the pure checksums of the pk3 files loaded by the server
			pPaks = FS_LoadedPakPureChecksums();
			Cmd_TokenizeString( pPaks );
			nServerPaks = Cmd_Argc();
			if (nServerPaks > 1024)
				nServerPaks = 1024;

			for (i = 0; i < nServerPaks; i++) {
				nServerChkSum[i] = atoi(Cmd_Argv(i));
			}

			// check if the client has provided any pure checksums of pk3 files not loaded by the server
			for (i = 0; i < nClientPaks; i++) {
				for (j = 0; j < nServerPaks; j++) {
					if (nClientChkSum[i] == nServerChkSum[j]) {
						break;
					}
				}
				if (j >= nServerPaks) {
					bGood = qfalse;
					break;
				}
			}
			if ( bGood == qfalse ) {
				break;
			}

			// check if the number of checksums was correct
			nChkSum1 = sv.checksumFeed;
			for (i = 0; i < nClientPaks; i++) {
				nChkSum1 ^= nClientChkSum[i];
			}
			nChkSum1 ^= nClientPaks;
			if (nChkSum1 != nClientChkSum[nClientPaks]) {
				bGood = qfalse;
				break;
			}

			// break out
			break;
		}

		cl->gotCP = qtrue;

		if (bGood) {
			cl->pureAuthentic = 1;
		} 
		else {
			cl->pureAuthentic = 0;
			cl->nextSnapshotTime = -1;
			cl->state = CS_ACTIVE;
			SV_SendClientSnapshot( cl );
			SV_DropClient( cl, "Unpure client detected. Invalid .PK3 files referenced!" );
		}
	}
}

/*
=================
SV_ResetPureClient_f
=================
*/
static void SV_ResetPureClient_f( client_t *cl ) {
	cl->pureAuthentic = 0;
	cl->gotCP = qfalse;
}

/*
=================
SV_UserinfoChanged

Pull specific info from a newly changed userinfo string
into a more C friendly form.
=================
*/
void SV_UserinfoChanged( client_t *cl ) {
	char	*val;
	int		i;

	// name for C code
	Q_strncpyz( cl->name, Info_ValueForKey (cl->userinfo, NET_GetNameInfoKey()), sizeof(cl->name) );

	// rate command

	// if the client is on the same subnet as the server and we aren't running an
	// internet public server, assume they don't need a rate choke
	if ( Sys_IsLANAddress( cl->netchan.remoteAddress ) && com_dedicated->integer != 2 && sv_lanForceRate->integer == 1) {
		cl->rate = 99999;	// lans should not rate limit
	} else {
		val = Info_ValueForKey (cl->userinfo, NET_GetRateInfoKey());
		if (strlen(val)) {
			i = atoi(val);
			cl->rate = i;
			if (cl->rate < 1000) {
				cl->rate = 1000;
			} else if (cl->rate > 90000) {
				cl->rate = 90000;
			}
		} else {
			cl->rate = 3000;
		}
	}
	val = Info_ValueForKey (cl->userinfo, NET_GetHandicapInfoKey());
	if (strlen(val)) {
		i = atoi(val);
		if (i<=0 || i>100 || strlen(val) > 4) {
			Info_SetValueForKey( cl->userinfo, NET_GetHandicapInfoKey(), "100" );
		}
	}

	// snaps command
	val = Info_ValueForKey (cl->userinfo, NET_GetSnapsInfoKey());
	if (strlen(val)) {
		i = atoi(val);
		if ( i < 1 ) {
			i = 1;
		} else if ( i > 30 ) {
			i = 30;
		}
		cl->snapshotMsec = 1000/i;
	} else {
		cl->snapshotMsec = 50;
	}
	
	// TTimo
	// maintain the IP information
	// this is set in SV_DirectConnect (directly on the server, not transmitted), may be lost when client updates it's userinfo
	// the banning code relies on this being consistently present
	val = Info_ValueForKey (cl->userinfo, NET_GetClientIpInfoKey());
	if (!val[0])
	{
		//Com_DPrintf("Maintain IP in userinfo for '%s'\n", cl->name);
		if ( !NET_IsLocalAddress(cl->netchan.remoteAddress) )
			Info_SetValueForKey( cl->userinfo, NET_GetClientIpInfoKey(), NET_AdrToString( cl->netchan.remoteAddress ) );
		else
			// force the client IP info key to "localhost" for local clients
			Info_SetValueForKey( cl->userinfo, NET_GetClientIpInfoKey(), "localhost" );
	}
}


/*
==================
SV_UpdateUserinfo_f
==================
*/
static void SV_UpdateUserinfo_f( client_t *cl ) {
	Q_strncpyz( cl->userinfo, Cmd_Argv(1), sizeof(cl->userinfo) );

	SV_UserinfoChanged( cl );
	// call prog code to allow overrides
	VM_Call( gvm, GAME_CLIENT_USERINFO_CHANGED, cl - svs.clients );
}

typedef struct {
	const char	*name;
	const char	*(*profileName)( void );
	void		(*func)( client_t *cl );
} ucmd_t;

static ucmd_t ucmds[] = {
	{NULL, NET_GetUserinfoCommand, SV_UpdateUserinfo_f},
	{NULL, NET_GetReliableDisconnectCommand, SV_Disconnect_f},
	{NULL, NET_GetPureChecksumsCommand, SV_VerifyPaks_f},
	{NULL, NET_GetPureResetCommand, SV_ResetPureClient_f},
	{NULL, NET_GetDownloadRequestCommand, SV_BeginDownload_f},
	{NULL, NET_GetDownloadNextCommand, SV_NextDownload_f},
	{NULL, NET_GetDownloadStopCommand, SV_StopDownload_f},
	{NULL, NET_GetDownloadDoneCommand, SV_DoneDownload_f},

	{NULL, NULL, NULL}
};

/*
==================
SV_ExecuteClientCommand

Also called by bot code
==================
*/
void SV_ExecuteClientCommand( client_t *cl, const char *s, qboolean clientOK ) {
	ucmd_t	*u;
	const char *commandName;
	qboolean bProcessed = qfalse;
	
	Cmd_TokenizeString( s );

	// see if it is a server level command
	for (u=ucmds ; u->name || u->profileName ; u++) {
		commandName = u->name ? u->name : u->profileName();
		if ( commandName && !strcmp( Cmd_Argv(0), commandName ) ) {
			u->func( cl );
			bProcessed = qtrue;
			break;
		}
	}

	if (clientOK) {
		// pass unknown strings to the game
		if ( !bProcessed && sv.state == SS_GAME ) {
			VM_Call( gvm, GAME_CLIENT_COMMAND, cl - svs.clients );
		}
	}
	else if (!bProcessed)
		Com_DPrintf( "client text ignored for %s: %s\n", cl->name, Cmd_Argv(0) );
}

/*
===============
SV_ClientCommand
===============
*/
static qboolean SV_ClientCommand( client_t *cl, msg_t *msg ) {
	int		seq;
	const char	*s;
	qboolean clientOk = qtrue;

	seq = MSG_ReadLong( msg );
	s = MSG_ReadString( msg );

	// see if we have already executed it
	if ( cl->lastClientCommand >= seq ) {
		return qtrue;
	}

	Com_DPrintf( "clientCommand: %s : %i : %s\n", cl->name, seq, s );

	// drop the connection if we have somehow lost commands
	if ( seq > cl->lastClientCommand + 1 ) {
		Com_Printf( "Client %s lost %i clientCommands\n", cl->name, 
			seq - cl->lastClientCommand + 1 );
		SV_DropClient( cl, "Lost reliable commands" );
		return qfalse;
	}

	// malicious users may try using too many string commands
	// to lag other players.  If we decide that we want to stall
	// the command, we will stop processing the rest of the packet,
	// including the usercmd.  This causes flooders to lag themselves
	// but not other people
	// We don't do this when the client hasn't been active yet since its
	// normal to spam a lot of commands when downloading
	if ( !com_cl_running->integer && 
		cl->state >= CS_ACTIVE &&
		sv_floodProtect->integer && 
		svs.time < cl->nextReliableTime ) {
		// ignore any other text messages from this client but let them keep playing
		// TTimo - moved the ignored verbose to the actual processing in SV_ExecuteClientCommand, only printing if the core doesn't intercept
		clientOk = qfalse;
	} 

	// don't allow another command for one second
	cl->nextReliableTime = svs.time + 1000;

	SV_ExecuteClientCommand( cl, s, clientOk );

	cl->lastClientCommand = seq;
	Com_sprintf(cl->lastClientCommandString, sizeof(cl->lastClientCommandString), "%s", s);

	return qtrue;		// continue procesing
}


//==================================================================================


/*
==================
SV_ClientThink

Also called by bot code
==================
*/
void SV_ClientThink (client_t *cl, usercmd_t *cmd) {
	cl->lastUsercmd = *cmd;

	if ( cl->state != CS_ACTIVE ) {
		return;		// may have been kicked during the last usercmd
	}

	VM_Call( gvm, GAME_CLIENT_THINK, cl - svs.clients );
}

/*
==================
SV_UserMove

The message usually contains all the movement commands 
that were in the last three packets, so that the information
in dropped packets can be recovered.

On very fast clients, there may be multiple usercmd packed into
each of the backup packets.
==================
*/
static void SV_UserMove( client_t *cl, msg_t *msg, qboolean delta ) {
	int			i, key;
	int			cmdCount;
	usercmd_t	nullcmd;
	usercmd_t	cmds[MAX_PACKET_USERCMDS];
	usercmd_t	*cmd, *oldcmd;

	if ( delta ) {
		cl->deltaMessage = cl->messageAcknowledge;
	} else {
		cl->deltaMessage = -1;
	}

	cmdCount = MSG_ReadByte( msg );

	if ( cmdCount < 1 ) {
		Com_Printf( "cmdCount < 1\n" );
		return;
	}

	if ( cmdCount > MAX_PACKET_USERCMDS ) {
		Com_Printf( "cmdCount > MAX_PACKET_USERCMDS\n" );
		return;
	}

	// use the checksum feed in the key
	key = sv.checksumFeed;
	// also use the message acknowledge
	key ^= cl->messageAcknowledge;
	// also use the last acknowledged server command in the key
	key ^= Com_HashKey(cl->reliableCommands[ cl->reliableAcknowledge & (MAX_RELIABLE_COMMANDS-1) ], 32);

	Com_Memset( &nullcmd, 0, sizeof(nullcmd) );
	oldcmd = &nullcmd;
	for ( i = 0 ; i < cmdCount ; i++ ) {
		cmd = &cmds[i];
		MSG_ReadDeltaUsercmdKey( msg, key, oldcmd, cmd );
		oldcmd = cmd;
	}

	// save time for ping calculation
	cl->frames[ cl->messageAcknowledge & PACKET_MASK ].messageAcked = svs.time;

	// TTimo
	// catch the no-cp-yet situation before SV_ClientEnterWorld
	// if CS_ACTIVE, then it's time to trigger a new gamestate emission
	// if not, then we are getting remaining parasite usermove commands, which we should ignore
	if (sv_pure->integer != 0 && cl->pureAuthentic == 0 && !cl->gotCP) {
		if (cl->state == CS_ACTIVE)
		{
			// we didn't get a cp yet, don't assume anything and just send the gamestate all over again
			Com_DPrintf( "%s: didn't get cp command, resending gamestate\n", cl->name, cl->state );
			SV_SendClientGameState( cl );
		}
		return;
	}			
	
	// if this is the first usercmd we have received
	// this gamestate, put the client into the world
	if ( cl->state == CS_PRIMED ) {
		SV_ClientEnterWorld( cl, &cmds[0] );
		// the moves can be processed normaly
	}
	
	// a bad cp command was sent, drop the client
	if (sv_pure->integer != 0 && cl->pureAuthentic == 0) {		
		SV_DropClient( cl, "Cannot validate pure client!");
		return;
	}

	if ( cl->state != CS_ACTIVE ) {
		cl->deltaMessage = -1;
		return;
	}

	// usually, the first couple commands will be duplicates
	// of ones we have previously received, but the servertimes
	// in the commands will cause them to be immediately discarded
	for ( i =  0 ; i < cmdCount ; i++ ) {
		// if this is a cmd from before a map_restart ignore it
		if ( cmds[i].serverTime > cmds[cmdCount-1].serverTime ) {
			continue;
		}
		// extremely lagged or cmd from before a map_restart
		//if ( cmds[i].serverTime > svs.time + 3000 ) {
		//	continue;
		//}
		// don't execute if this is an old cmd which is already executed
		// these old cmds are included when cl_packetdup > 0
		if ( cmds[i].serverTime <= cl->lastUsercmd.serverTime ) {
			continue;
		}
		SV_ClientThink (cl, &cmds[ i ]);
	}
}


/*
===========================================================================

USER CMD EXECUTION

===========================================================================
*/

/*
===================
SV_ExecuteClientMessage

Parse a client packet
===================
*/
void SV_ExecuteClientMessage( client_t *cl, msg_t *msg ) {
	int			c;
	int			serverId;

	MSG_Bitstream(msg);

	serverId = MSG_ReadLong( msg );
	cl->messageAcknowledge = MSG_ReadLong( msg );

	if (cl->messageAcknowledge < 0) {
		// usually only hackers create messages like this
		// it is more annoying for them to let them hanging
#ifndef NDEBUG
		SV_DropClient( cl, "DEBUG: illegible client message" );
#endif
		return;
	}

	cl->reliableAcknowledge = MSG_ReadLong( msg );
	(void)MSG_ReadByte( msg );

	// NOTE: when the client message is fux0red the acknowledgement numbers
	// can be out of range, this could cause the server to send thousands of server
	// commands which the server thinks are not yet acknowledged in SV_UpdateServerCommandsToClient
	if (cl->reliableAcknowledge < cl->reliableSequence - MAX_RELIABLE_COMMANDS) {
		// usually only hackers create messages like this
		// it is more annoying for them to let them hanging
#ifndef NDEBUG
		SV_DropClient( cl, "DEBUG: illegible client message" );
#endif
		cl->reliableAcknowledge = cl->reliableSequence;
		return;
	}
	// if this is a usercmd from a previous gamestate,
	// ignore it or retransmit the current gamestate
	// 
	// if the client was downloading, let it stay at whatever serverId and
	// gamestate it was at.  This allows it to keep downloading even when
	// the gamestate changes.  After the download is finished, we'll
	// notice and send it a new game state
	//
	// https://zerowing.idsoftware.com/bugzilla/show_bug.cgi?id=536
	// don't drop as long as previous command was a nextdl, after a dl is done, downloadName is set back to ""
	// but we still need to read the next message to move to next download or send gamestate
	// I don't like this hack though, it must have been working fine at some point, suspecting the fix is somewhere else
	if ( serverId != sv.serverId && !*cl->downloadName && !strstr(cl->lastClientCommandString, NET_GetDownloadNextCommand()) ) {
		if ( serverId >= sv.restartedServerId && serverId < sv.serverId ) { // TTimo - use a comparison here to catch multiple map_restart
			// they just haven't caught the map_restart yet
			Com_DPrintf("%s : ignoring pre map_restart / outdated client message\n", cl->name);
			return;
		}
		// if we can tell that the client has dropped the last
		// gamestate we sent them, resend it
		if ( cl->messageAcknowledge > cl->gamestateMessageNum ) {
			Com_DPrintf( "%s : dropped gamestate, resending\n", cl->name );
			SV_SendClientGameState( cl );
		}
		return;
	}

	// read optional clientCommand strings
	do {
		c = MSG_ReadByte( msg );
		if ( c == clc_EOF ) {
			break;
		}
		if ( c != clc_clientCommand ) {
			break;
		}
		if ( !SV_ClientCommand( cl, msg ) ) {
			return;	// we couldn't execute it because of the flood protection
		}
		if (cl->state == CS_ZOMBIE) {
			return;	// disconnect command
		}
	} while ( 1 );

	// read the usercmd_t
	if ( c == clc_move ) {
		SV_UserMove( cl, msg, qtrue );
	} else if ( c == clc_moveNoDelta ) {
		SV_UserMove( cl, msg, qfalse );
	} else if ( c != clc_EOF ) {
		Com_Printf( "WARNING: bad command byte for client %i\n", cl - svs.clients );
	}
//	if ( msg->readcount != msg->cursize ) {
//		Com_Printf( "WARNING: Junk at end of packet for client %i\n", cl - svs.clients );
//	}
}
