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

static void SV_CloseDownload( client_t *cl );

#if SV_HAS_PLATFORM_AUTH
static qboolean sv_steamServerConnected;

#define SV_STEAM_STATS_FIELD_COUNT 88
#define SV_STEAM_ACHIEVEMENT_COUNT 59
#define SV_STEAM_STATS_P2P_HELLO "hello"
#define SV_STEAM_STATS_P2P_SEND_RELIABLE 2
#define SV_STEAM_STATS_P2P_CHANNEL 16

typedef struct {
	qboolean active;
	qboolean backendAvailable;
	qboolean requestIssued;
	CSteamID steamId;
	int statValue[SV_STEAM_STATS_FIELD_COUNT];
	int pendingStatDelta[SV_STEAM_STATS_FIELD_COUNT];
	qboolean statLoaded[SV_STEAM_STATS_FIELD_COUNT];
	qboolean statQueryAttempted[SV_STEAM_STATS_FIELD_COUNT];
	qboolean statDirty[SV_STEAM_STATS_FIELD_COUNT];
	qboolean achievementUnlocked[SV_STEAM_ACHIEVEMENT_COUNT];
	qboolean achievementLoaded[SV_STEAM_ACHIEVEMENT_COUNT];
	qboolean achievementQueryAttempted[SV_STEAM_ACHIEVEMENT_COUNT];
	qboolean achievementDirty[SV_STEAM_ACHIEVEMENT_COUNT];
} sv_steam_stats_session_t;

static sv_steam_stats_session_t sv_steamStatsSessions[MAX_CLIENTS];

static const char *s_svSteamStatNames[SV_STEAM_STATS_FIELD_COUNT] = {
	"version",
	"kill_gauntlet",
	"kill_machinegun",
	"kill_shotgun",
	"kill_grenade",
	"kill_rocket",
	"kill_lightning",
	"kill_railgun",
	"kill_plasma",
	"kill_bfg",
	"kill_nailgun",
	"kill_proxmine",
	"kill_chaingun",
	"kill_hmg",
	"hits_machinegun",
	"hits_shotgun",
	"hits_grenade",
	"hits_rocket",
	"hits_lightning",
	"hits_railgun",
	"hits_plasma",
	"hits_bfg",
	"hits_nailgun",
	"hits_proxmine",
	"hits_chaingun",
	"hits_hmg",
	"shots_machinegun",
	"shots_shotgun",
	"shots_grenade",
	"shots_rocket",
	"shots_lightning",
	"shots_railgun",
	"shots_plasma",
	"shots_bfg",
	"shots_nailgun",
	"shots_proxmine",
	"shots_chaingun",
	"shots_hmg",
	"mod_shotgun",
	"mod_gauntlet",
	"mod_machinegun",
	"mod_grenade",
	"mod_rocket",
	"mod_plasma",
	"mod_railgun",
	"mod_lightning",
	"mod_bfg",
	"mod_water",
	"mod_slime",
	"mod_lava",
	"mod_crush",
	"mod_telefrag",
	"mod_laser",
	"BROKEN1",
	"mod_nailgun",
	"mod_chaingun",
	"mod_proxmine",
	"mod_kamikaze",
	"mod_juiced",
	"mod_suicide",
	"mod_falling",
	"mod_grapple",
	"mod_hmg",
	"mod_lightning_discharge",
	"mod_other",
	"medal_firstfrag",
	"medal_gauntlet",
	"medal_excellent",
	"medal_revenge",
	"medal_combokill",
	"medal_midair",
	"medal_perforated",
	"medal_rampage",
	"medal_impressive",
	"medal_capture",
	"medal_assist",
	"medal_defense",
	"medal_headshot",
	"medal_quadgod",
	"medal_perfect",
	"medal_accuracy",
	"wins",
	"losses",
	"played",
	"BROKEN2",
	"mod_hurt",
	"total_kills",
	"total_deaths"
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
SV_SteamStats_GetFieldName

Returns the mapped retail Steam stat descriptor name for one field index while
labeling invalid or unmapped descriptor lookups through the shared stats
lifecycle logger.
=================
*/
static const char *SV_SteamStats_GetFieldName( int statIndex, const char *stage ) {
	const char *lookupStage;
	const char *name;
	char detail[128];

	lookupStage = stage ? stage : "descriptor-lookup";
	if ( statIndex < 0 || statIndex >= SV_STEAM_STATS_FIELD_COUNT ) {
		Com_sprintf( detail, sizeof( detail ), "ignored stat descriptor lookup for invalid index %d", statIndex );
		SV_LogSteamStatsLifecycle( NULL, lookupStage, detail );
		return NULL;
	}

	name = s_svSteamStatNames[statIndex];
	if ( !name ) {
		Com_sprintf( detail, sizeof( detail ), "ignored stat descriptor lookup for unmapped index %d", statIndex );
		SV_LogSteamStatsLifecycle( NULL, lookupStage, detail );
		return NULL;
	}

	return name;
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

	if ( !QL_Steamworks_ServerRequestUserStats( &session->steamId ) ) {
		SV_LogSteamStatsLifecycle( &session->steamId, "request-current-values", "request failed" );
		return qfalse;
	}

	session->backendAvailable = qtrue;
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
	const char *name;
	char detail[128];
	int value;

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

	name = SV_SteamStats_GetFieldName( statIndex, "value-query" );
	if ( !name ) {
		Com_sprintf( detail, sizeof( detail ), "ignored stat query for unmapped index %d", statIndex );
		SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
		return qfalse;
	}

	if ( session->statLoaded[statIndex] ) {
		Com_sprintf( detail, sizeof( detail ), "stat %s already cached as %d", name, session->statValue[statIndex] );
		SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
		return qtrue;
	}

	if ( !session->requestIssued ) {
		SV_SteamStats_RequestCurrentValues( session );
	}

	session->statQueryAttempted[statIndex] = qtrue;
	value = 0;
	if ( !QL_Steamworks_ServerGetUserStatInt( &session->steamId, name, &value ) ) {
		Com_sprintf( detail, sizeof( detail ), "stat %s query failed", name );
		SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );
		return qfalse;
	}

	session->backendAvailable = qtrue;
	session->statLoaded[statIndex] = qtrue;
	session->statValue[statIndex] = value + session->pendingStatDelta[statIndex];
	Com_sprintf( detail, sizeof( detail ), "stat %s loaded as %d", name, session->statValue[statIndex] );
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
SV_SteamStats_FlushPendingValues

Publishes pending stat deltas and achievement unlocks for one active session.
=================
*/
static void SV_SteamStats_FlushPendingValues( sv_steam_stats_session_t *session ) {
	const char *name;
	qboolean hasPending;
	qboolean failed;
	char detail[128];
	int pendingStats;
	int pendingAchievements;
	int i;

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
		name = SV_SteamStats_GetFieldName( i, "value-flush" );
		if ( !session->statLoaded[i] && !SV_SteamStats_LoadFieldValue( session, i ) ) {
			Com_sprintf( detail, sizeof( detail ), "stat %s unavailable during flush", name ? name : "<unknown>" );
			SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", detail );
			failed = qtrue;
			continue;
		}

		if ( !name || !QL_Steamworks_ServerSetUserStatInt( &session->steamId, name, session->statValue[i] ) ) {
			Com_sprintf( detail, sizeof( detail ), "stat %s publish failed", name ? name : "<unknown>" );
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

	if ( !hasPending ) {
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
		SV_SteamStats_RequestCurrentValues( session );
		return;
	}

	SV_SteamStats_ResetSession( session );
	session->active = qtrue;
	session->steamId = steamId;
	SV_LogSteamStatsLifecycle( &session->steamId, "session-bootstrap", "created session" );
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
	SV_SteamStats_FlushPendingValues( session );
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
	const char *name;
	char detail[128];
	char subject[128];

	if ( delta == 0 ) {
		Com_sprintf( detail, sizeof( detail ),
			"ignored stat index %d delta %d for client %d", statIndex, delta, clientNum );
		SV_LogSteamStatsLifecycle( NULL, "field-delta", detail );
		return;
	}

	name = SV_SteamStats_GetFieldName( statIndex, "field-delta" );
	if ( !name ) {
		Com_sprintf( detail, sizeof( detail ),
			"ignored stat index %d delta %d for client %d", statIndex, delta, clientNum );
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

	SV_SteamStats_LoadAchievement( session, achievementId );
	if ( session->achievementUnlocked[achievementId] ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s already unlocked for client %d", name, clientNum );
		SV_LogSteamStatsLifecycle( &session->steamId, "achievement-unlock", detail );
		return;
	}

	session->achievementUnlocked[achievementId] = qtrue;
	session->achievementDirty[achievementId] = qtrue;
	Com_sprintf( detail, sizeof( detail ), "queued achievement %s unlock for client %d", name, clientNum );
	SV_LogSteamStatsLifecycle( &session->steamId, "achievement-unlock", detail );
	SV_SteamStats_FlushPendingValues( session );
}

/*
=================
SV_SteamStats_HasAchievement

Reports whether the retained session already owns one mapped achievement.
=================
*/
qboolean SV_SteamStats_HasAchievement( int clientNum, int achievementId ) {
	client_t *cl;
	sv_steam_stats_session_t *session;
	const char *name;
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

	SV_SteamStats_CreatePlayerSession( cl );
	session = &sv_steamStatsSessions[clientNum];
	if ( !session->active ) {
		Com_sprintf( detail, sizeof( detail ), "achievement %s session unavailable for client %d", name, clientNum );
		SV_LogSteamStatsLifecycle( NULL, "achievement-query", detail );
		return qfalse;
	}

	SV_SteamStats_LoadAchievement( session, achievementId );
	Com_sprintf( detail, sizeof( detail ), "achievement %s ownership is %s for client %d",
		name, session->achievementUnlocked[achievementId] ? "present" : "absent", clientNum );
	SV_LogSteamStatsLifecycle( &session->steamId, "achievement-query", detail );
	return session->achievementUnlocked[achievementId] ? qtrue : qfalse;
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
SV_BeginPlatformAuthSession

Starts one Steam GameServer auth session after qagame has accepted the connection.
=================
*/
static const char *SV_BeginPlatformAuthSession( client_t *cl, const netadr_t *adr ) {
	ql_auth_response_t	response;
	CSteamID		steamId;
	const char		*message;

	if ( !cl || !cl->platformAuthToken[0] || NET_IsLocalAddress( cl->netchan.remoteAddress ) ) {
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
SV_SteamServerConnectedCallback

Publishes the current server identity once Steam confirms the GameServer session.
=================
*/
static void SV_SteamServerConnectedCallback( void *context, const ql_steam_server_connected_t *event ) {
	(void)context;
	(void)event;

	sv_steamServerConnected = qtrue;
	SV_LogSteamServerCallbackLifecycle( "connected", "published identity and state refresh" );
	SV_SteamServerPublishIdentity();
	SV_SteamServerUpdatePublishedState( qtrue );
	SV_SteamStats_RequerySessions();
}

/*
=================
SV_SteamServerConnectFailureCallback

Tracks retail-style Steam server connect failures in the server owner.
=================
*/
static void SV_SteamServerConnectFailureCallback( void *context, const ql_steam_server_connect_failure_t *event ) {
	char detail[96];

	(void)context;

	sv_steamServerConnected = qfalse;

	if ( !event ) {
		SV_LogSteamServerCallbackLifecycle( "connect_failure", "ignored null callback payload" );
		return;
	}

	Com_sprintf( detail, sizeof( detail ), "connect failure result=%d", event->result );
	SV_LogSteamServerCallbackLifecycle( "connect_failure", detail );
}

/*
=================
SV_SteamServerDisconnectedCallback

Tracks when the Steam GameServer session disconnects from Valve backends.
=================
*/
static void SV_SteamServerDisconnectedCallback( void *context, const ql_steam_server_disconnected_t *event ) {
	char detail[96];

	(void)context;

	sv_steamServerConnected = qfalse;

	if ( !event ) {
		SV_LogSteamServerCallbackLifecycle( "disconnected", "ignored null callback payload" );
		return;
	}

	Com_sprintf( detail, sizeof( detail ), "disconnected result=%d", event->result );
	SV_LogSteamServerCallbackLifecycle( "disconnected", detail );
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
	char				detail[96];
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
	Com_Printf( "Steam P2P session request %s for %llu via %s [%s]: %s\n",
		state ? state : "update",
		remoteId,
		SV_GetSteamServerProviderLabel(), SV_GetSteamServerPolicyLabel(),
		reason ? reason : "no detail" );
}

/*
=================
SV_SteamServerP2PSessionRequestCallback

Accepts server-side Steam P2P sessions only for live, authenticated clients.
=================
*/
static void SV_SteamServerP2PSessionRequestCallback( void *context, const ql_steam_p2p_session_request_t *event ) {
	client_t *cl;

	(void)context;

	if ( !event ) {
		SV_LogSteamServerP2PSessionRequest( NULL, "ignored", "null callback payload" );
		return;
	}

	cl = SV_FindClientBySteamId( &event->remoteId );
	if ( !cl ) {
		SV_LogSteamServerP2PSessionRequest( &event->remoteId, "ignored", "client not found" );
		return;
	}

	if ( !cl->platformAuthSucceeded ) {
		SV_LogSteamServerP2PSessionRequest( &event->remoteId, "ignored", "client not authenticated" );
		return;
	}

	if ( !QL_Steamworks_ServerAcceptP2PSession( &event->remoteId ) ) {
		SV_LogSteamServerP2PSessionRequest( &event->remoteId, "failed", "accept call failed" );
	}
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
void SV_GetChallenge( netadr_t from ) {
	int		i;
	int		oldest;
	int		oldestTime;
	challenge_t	*challenge;

	// ignore if we are in single player
	if ( Cvar_VariableValue( "g_gametype" ) == GT_SINGLE_PLAYER || Cvar_VariableValue("ui_singlePlayerActive")) {
		return;
	}

	if ( !sv_vac || !sv_vac->integer ) {
		const char *message;

		message = "VAC is disabled on this server";
		SV_LogVACStatus( &from, "rejected", "disabled", message );
		NET_OutOfBandPrint( NS_SERVER, from, "print\n%s\n", message );
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
		i = oldest;
	}

	// if they are on a lan address, send the challengeResponse immediately
	if ( Sys_IsLANAddress( from ) ) {
		challenge->pingTime = svs.time;
		NET_OutOfBandPrint( NS_SERVER, from, "challengeResponse %i", challenge->challenge );
		return;
	}

#if !( QL_PLATFORM_HAS_ONLINE_SERVICES && QL_ENABLE_LEGACY_Q3_SERVICES )
	Com_DPrintf( "legacy getIpAuthorize bypassed for %s: Quake III authorize server disabled by online-services policy\n", NET_AdrToString( from ) );
	challenge->pingTime = svs.time;
	NET_OutOfBandPrint( NS_SERVER, from, "challengeResponse %i", challenge->challenge );
	return;
#else
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
			"challengeResponse %i", challenge->challenge );
		return;
	}

	// otherwise send their ip to the authorize server
	if ( svs.authorizeAddress.type != NA_BAD ) {
		cvar_t	*fs;
		char	game[1024];

		Com_DPrintf( "sending getIpAuthorize for %s\n", NET_AdrToString( from ));
		
		strcpy(game, BASEGAME);
		fs = Cvar_Get ("fs_game", "", CVAR_INIT|CVAR_SYSTEMINFO );
		if (fs && fs->string[0] != 0) {
			strcpy(game, fs->string);
		}
		
		// the 0 is for backwards compatibility with obsolete sv_allowanonymous flags
		// getIpAuthorize <challenge> <IP> <game> 0 <auth-flag>
		NET_OutOfBandPrint( NS_SERVER, svs.authorizeAddress,
			"getIpAuthorize %i %i.%i.%i.%i %s 0 %s",  svs.challenges[i].challenge,
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
				"challengeResponse %i", svs.challenges[i].challenge );
			return;
		}
		// they are a demo client trying to connect to a real server
		NET_OutOfBandPrint( NS_SERVER, svs.challenges[i].adr, "print\nServer is not a demo server\n" );
		// clear the challenge record so it won't timeout and let them through
		Com_Memset( &svs.challenges[i], 0, sizeof( svs.challenges[i] ) );
		return;
	}
	if ( !Q_stricmp( s, "accept" ) ) {
		NET_OutOfBandPrint( NS_SERVER, svs.challenges[i].adr, 
			"challengeResponse %i", svs.challenges[i].challenge );
		return;
	}
        if ( !Q_stricmp( s, "unknown" ) ) {
                if ( !r ) {
                        NET_OutOfBandPrint( NS_SERVER, svs.challenges[i].adr, "print\nAwaiting credential authorization\n" );
                } else {
                        sprintf(ret, "print\n%s\n", r);
                        NET_OutOfBandPrint( NS_SERVER, svs.challenges[i].adr, ret );
                }
		// clear the challenge record so it won't timeout and let them through
		Com_Memset( &svs.challenges[i], 0, sizeof( svs.challenges[i] ) );
		return;
	}

	// authorization failed
        if ( !r ) {
                NET_OutOfBandPrint( NS_SERVER, svs.challenges[i].adr, "print\nSomeone is using this credential\n" );
        } else {
                sprintf(ret, "print\n%s\n", r);
                NET_OutOfBandPrint( NS_SERVER, svs.challenges[i].adr, ret );
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
	char		 serverTypeError[MAX_STRING_CHARS];

	Com_DPrintf ("SVC_DirectConnect ()\n");

	Q_strncpyz( userinfo, Cmd_Argv(1), sizeof(userinfo) );

	version = atoi( Info_ValueForKey( userinfo, "protocol" ) );
	if ( version != PROTOCOL_VERSION ) {
		NET_OutOfBandPrint( NS_SERVER, from, "print\nServer uses protocol version %i.\n", PROTOCOL_VERSION );
		Com_DPrintf ("    rejected connect from version %i\n", version);
		return;
	}

	challenge = atoi( Info_ValueForKey( userinfo, "challenge" ) );
	qport = atoi( Info_ValueForKey( userinfo, "qport" ) );

	if ( !sv_vac || !sv_vac->integer ) {
		const char *message;

		message = "VAC is disabled on this server";
		SV_LogVACStatus( &from, "rejected", "disabled", message );
		NET_OutOfBandPrint( NS_SERVER, from, "print\n%s\n", message );
		return;
	}

	serverTypeError[0] = '\0';

	if ( !SV_ServerTypeAllowsConnection( from, serverTypeError, sizeof( serverTypeError ) ) ) {
		const char *errorMessage;

		errorMessage = serverTypeError[0] ? serverTypeError : "Server is not accepting connections";
		NET_OutOfBandPrint( NS_SERVER, from, "print\n%s\n", errorMessage );
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
			NET_OutOfBandPrint( NS_SERVER, from, "print\nNo or bad challenge for address.\n" );
			return;
		}
		// force the IP key/value pair so the game can filter based on ip
		Info_SetValueForKey( userinfo, "ip", NET_AdrToString( from ) );

		ping = svs.time - svs.challenges[i].pingTime;
		Com_Printf( "Client %i connecting with %i challenge ping\n", i, ping );
		svs.challenges[i].connected = qtrue;

		// never reject a LAN client based on ping
		if ( !Sys_IsLANAddress( from ) ) {
			if ( sv_minPing->value && ping < sv_minPing->value ) {
				// don't let them keep trying until they get a big delay
				NET_OutOfBandPrint( NS_SERVER, from, "print\nServer is for high pings only\n" );
				Com_DPrintf ("Client %i rejected on a too low ping\n", i);
				// reset the address otherwise their ping will keep increasing
				// with each connect message and they'd eventually be able to connect
				svs.challenges[i].adr.port = 0;
				return;
			}
			if ( sv_maxPing->value && ping > sv_maxPing->value ) {
				NET_OutOfBandPrint( NS_SERVER, from, "print\nServer is for low pings only\n" );
				Com_DPrintf ("Client %i rejected on a too high ping\n", i);
				return;
			}
		}
	} else {
		// force the "ip" info key to "localhost"
		Info_SetValueForKey( userinfo, "ip", "localhost" );
	}

	SV_LogVACStatus( &from, "accepted", "enabled", "VAC is enabled on this server" );

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
	password = Info_ValueForKey( userinfo, "password" );
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
			NET_OutOfBandPrint( NS_SERVER, from, "print\nServer is full.\n" );
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
		SV_CapturePlatformAuthFromUserinfo( newcl, userinfo );

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

		NET_OutOfBandPrint( NS_SERVER, from, "print\n%s\n", denied );
		Com_DPrintf ("Game rejected a connection: %s.\n", denied);
		return;
	}

#if SV_HAS_PLATFORM_AUTH
	denied = SV_BeginPlatformAuthSession( newcl, &from );
	if ( denied ) {
		NET_OutOfBandPrint( NS_SERVER, from, "print\n%s\n", denied );
		return;
	}
#endif

	SV_UserinfoChanged( newcl );

	// send the connect packet to the client
	NET_OutOfBandPrint( NS_SERVER, from, "connectResponse" );

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
	SV_SendServerCommand( drop, "disconnect \"%s\"", reason);

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
	SV_SendClientGameState(cl);
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

	// cl->downloadName is non-zero now, SV_WriteDownloadToClient will see this and open
	// the file itself
	Q_strncpyz( cl->downloadName, Cmd_Argv(1), sizeof(cl->downloadName) );
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
		idPack = missionPack || FS_idPak(cl->downloadName, "baseq3");

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
	Q_strncpyz( cl->name, Info_ValueForKey (cl->userinfo, "name"), sizeof(cl->name) );

	// rate command

	// if the client is on the same subnet as the server and we aren't running an
	// internet public server, assume they don't need a rate choke
	if ( Sys_IsLANAddress( cl->netchan.remoteAddress ) && com_dedicated->integer != 2 && sv_lanForceRate->integer == 1) {
		cl->rate = 99999;	// lans should not rate limit
	} else {
		val = Info_ValueForKey (cl->userinfo, "rate");
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
	val = Info_ValueForKey (cl->userinfo, "handicap");
	if (strlen(val)) {
		i = atoi(val);
		if (i<=0 || i>100 || strlen(val) > 4) {
			Info_SetValueForKey( cl->userinfo, "handicap", "100" );
		}
	}

	// snaps command
	val = Info_ValueForKey (cl->userinfo, "snaps");
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
	val = Info_ValueForKey (cl->userinfo, "ip");
	if (!val[0])
	{
		//Com_DPrintf("Maintain IP in userinfo for '%s'\n", cl->name);
		if ( !NET_IsLocalAddress(cl->netchan.remoteAddress) )
			Info_SetValueForKey( cl->userinfo, "ip", NET_AdrToString( cl->netchan.remoteAddress ) );
		else
			// force the "ip" info key to "localhost" for local clients
			Info_SetValueForKey( cl->userinfo, "ip", "localhost" );
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
	char	*name;
	void	(*func)( client_t *cl );
} ucmd_t;

static ucmd_t ucmds[] = {
	{"userinfo", SV_UpdateUserinfo_f},
	{"disconnect", SV_Disconnect_f},
	{"cp", SV_VerifyPaks_f},
	{"vdr", SV_ResetPureClient_f},
	{"download", SV_BeginDownload_f},
	{"nextdl", SV_NextDownload_f},
	{"stopdl", SV_StopDownload_f},
	{"donedl", SV_DoneDownload_f},

	{NULL, NULL}
};

/*
==================
SV_ExecuteClientCommand

Also called by bot code
==================
*/
void SV_ExecuteClientCommand( client_t *cl, const char *s, qboolean clientOK ) {
	ucmd_t	*u;
	qboolean bProcessed = qfalse;
	
	Cmd_TokenizeString( s );

	// see if it is a server level command
	for (u=ucmds ; u->name ; u++) {
		if (!strcmp (Cmd_Argv(0), u->name) ) {
			u->func( cl );
			bProcessed = qtrue;
			break;
		}
	}

	if (clientOK) {
		// pass unknown strings to the game
		if (!u->name && sv.state == SS_GAME) {
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
	if ( serverId != sv.serverId && !*cl->downloadName && !strstr(cl->lastClientCommandString, "nextdl") ) {
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
