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
// cl_main.c  -- client main loop

#include "client.h"
#include "../qcommon/vm_local.h"
#include "../../common/auth_credentials.h"
#include "../../common/platform/platform_config.h"
#include "../../common/platform/platform_services.h"
#include "../../common/platform/platform_steamworks.h"
#include <limits.h>
#include <stdlib.h>

#ifdef _WIN32
#include "../win32/win_local.h"
#endif

/*
=============
CL_ShouldFilterConsoleText

Returns whether console-originated text should be hidden based on cl_allowConsoleChat.
=============
*/
qboolean CL_ShouldFilterConsoleText( const char *text ) {
	if ( !text || !*text ) {
		return qfalse;
	}
	
	if ( cl_allowConsoleChat && cl_allowConsoleChat->integer ) {
		return qfalse;
	}
	
	while ( Q_IsColorString( text ) ) {
		text += 2;
	}
	
	if ( !Q_stricmpn( text, "console:", 8 ) ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
CL_StringRepresentsTrue

Returns qtrue when an environment string should be treated as enabled.
=============
*/
static qboolean CL_StringRepresentsTrue( const char *value ) {
	if ( !value || !value[0] ) {
		return qfalse;
	}

	if ( value[0] == '0' && value[1] == '\0' ) {
		return qfalse;
	}

	if ( !Q_stricmp( value, "false" ) || !Q_stricmp( value, "no" ) || !Q_stricmp( value, "off" ) ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_OnlineServicesEnabled

Returns qtrue when Quake Live-specific online services are available in this build and runtime.
=============
*/
qboolean CL_OnlineServicesEnabled( void ) {
	const char *value;

	if ( !QL_PLATFORM_HAS_ONLINE_SERVICES ) {
		return qfalse;
	}

	value = getenv( "QL_DISABLE_EXTERNAL_ECOSYSTEMS" );
	if ( CL_StringRepresentsTrue( value ) ) {
		return qfalse;
	}

	value = getenv( "QL_DISABLE_AWESOMIUM" );
	if ( CL_StringRepresentsTrue( value ) ) {
		return qfalse;
	}

	value = getenv( "QL_DISABLE_STEAMWORKS" );
	if ( CL_StringRepresentsTrue( value ) ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_SteamServicesEnabled

Returns qtrue when Steam-backed services are compiled in and available for use.
=============
*/
qboolean CL_SteamServicesEnabled( void ) {
	if ( !QL_PLATFORM_HAS_STEAM_SERVICES ) {
		return qfalse;
	}

	return CL_OnlineServicesEnabled();
}

/*
=============
CL_GetWorkshopServiceDescriptor

Returns the current platform-service descriptor for the workshop seam.
=============
*/
static const ql_platform_feature_descriptor *CL_GetWorkshopServiceDescriptor( void ) {
	const ql_platform_service_table *services = QL_GetPlatformServices();

	if ( !services ) {
		return NULL;
	}

	return &services->workshop;
}

/*
=============
CL_GetWorkshopServiceProviderLabel

Returns the human-readable provider label for the workshop seam.
=============
*/
static const char *CL_GetWorkshopServiceProviderLabel( void ) {
	const ql_platform_feature_descriptor *workshop = CL_GetWorkshopServiceDescriptor();

	if ( !workshop || !workshop->provider ) {
		return "Unavailable";
	}

	return workshop->provider;
}

/*
=============
CL_GetWorkshopServicePolicyLabel

Returns the short compatibility policy label for the workshop seam.
=============
*/
static const char *CL_GetWorkshopServicePolicyLabel( void ) {
	return QL_DescribePlatformFeaturePolicy( CL_GetWorkshopServiceDescriptor() );
}

/*
=============
CL_LogWorkshopLifecycle

Publishes provider-aware diagnostics whenever the retained workshop bootstrap
or download lifecycle performs a compatibility-only transition.
=============
*/
static void CL_LogWorkshopLifecycle( const char *stage, const char *detail ) {
	Com_Printf( "Workshop %s via %s [%s]: %s\n",
		stage ? stage : "lifecycle",
		CL_GetWorkshopServiceProviderLabel(),
		CL_GetWorkshopServicePolicyLabel(),
		detail ? detail : "no detail" );
}

/*
=============
CL_GetMatchmakingServiceDescriptor

Returns the current platform-service descriptor for the client matchmaking and
social presence seam.
=============
*/
static const ql_platform_feature_descriptor *CL_GetMatchmakingServiceDescriptor( void ) {
	const ql_platform_service_table *services = QL_GetPlatformServices();

	if ( !services ) {
		return NULL;
	}

	return &services->matchmaking;
}

/*
=============
CL_GetMatchmakingServiceProviderLabel

Returns the human-readable provider label for the client matchmaking seam.
=============
*/
static const char *CL_GetMatchmakingServiceProviderLabel( void ) {
	const ql_platform_feature_descriptor *descriptor = CL_GetMatchmakingServiceDescriptor();

	if ( !descriptor || !descriptor->provider ) {
		return "Unavailable";
	}

	return descriptor->provider;
}

/*
=============
CL_GetMatchmakingServicePolicyLabel

Returns the short compatibility policy label for the client matchmaking seam.
=============
*/
static const char *CL_GetMatchmakingServicePolicyLabel( void ) {
	return QL_DescribePlatformFeaturePolicy( CL_GetMatchmakingServiceDescriptor() );
}

/*
=============
CL_GetStatsServiceDescriptor

Returns the current platform-service descriptor for the client stats seam.
=============
*/
static const ql_platform_feature_descriptor *CL_GetStatsServiceDescriptor( void ) {
	const ql_platform_service_table *services = QL_GetPlatformServices();

	if ( !services ) {
		return NULL;
	}

	return &services->stats;
}

/*
=============
CL_GetStatsServiceProviderLabel

Returns the human-readable provider label for the client stats seam.
=============
*/
static const char *CL_GetStatsServiceProviderLabel( void ) {
	const ql_platform_feature_descriptor *descriptor = CL_GetStatsServiceDescriptor();

	if ( !descriptor || !descriptor->provider ) {
		return "Unavailable";
	}

	return descriptor->provider;
}

/*
=============
CL_GetStatsServicePolicyLabel

Returns the short compatibility policy label for the client stats seam.
=============
*/
static const char *CL_GetStatsServicePolicyLabel( void ) {
	return QL_DescribePlatformFeaturePolicy( CL_GetStatsServiceDescriptor() );
}

/*
=============
CL_GetSocialOverlayServiceDescriptor

Returns the current platform-service descriptor for the Steam social-overlay
command seam.
=============
*/
static const ql_platform_feature_descriptor *CL_GetSocialOverlayServiceDescriptor( void ) {
	const ql_platform_service_table *services = QL_GetPlatformServices();

	if ( !services ) {
		return NULL;
	}

	return &services->overlay;
}

/*
=============
CL_GetSocialOverlayServiceProviderLabel

Returns the human-readable provider label for the Steam social-overlay command
seam.
=============
*/
static const char *CL_GetSocialOverlayServiceProviderLabel( void ) {
	const ql_platform_feature_descriptor *descriptor = CL_GetSocialOverlayServiceDescriptor();

	if ( !descriptor || !descriptor->provider ) {
		return "Unavailable";
	}

	return descriptor->provider;
}

/*
=============
CL_GetSocialOverlayServicePolicyLabel

Returns the short compatibility policy label for the Steam social-overlay
command seam.
=============
*/
static const char *CL_GetSocialOverlayServicePolicyLabel( void ) {
	return QL_DescribePlatformFeaturePolicy( CL_GetSocialOverlayServiceDescriptor() );
}

/*
=============
CL_GetIdentityBootstrapModeLabel

Returns the overall online-services mode label used by the retained client
identity bootstrap lane.
=============
*/
static const char *CL_GetIdentityBootstrapModeLabel( void ) {
	return QL_GetOnlineServicesModeLabel();
}

/*
=============
CL_GetIdentityBootstrapPolicyLabel

Returns the overall online-services policy label used by the retained client
identity bootstrap lane.
=============
*/
static const char *CL_GetIdentityBootstrapPolicyLabel( void ) {
	return QL_GetOnlineServicesPolicyLabel();
}

/*
=============
CL_LogIdentityBootstrapFallback

Publishes explicit diagnostics whenever the retained Steam persona/country
bootstrap lane falls back under the compatibility policy.
=============
*/
static void CL_LogIdentityBootstrapFallback( const char *stage, const char *reason ) {
	Com_DPrintf( "%s identity bootstrap: %s (%s [%s])\n",
		stage ? stage : "client_identity",
		reason ? reason : "identity bootstrap provider unavailable",
		CL_GetIdentityBootstrapModeLabel(),
		CL_GetIdentityBootstrapPolicyLabel() );
}

/*
=============
CL_GetVoiceServiceModeLabel

Returns the overall online-services mode label used by the retained voice
compatibility lane.
=============
*/
static const char *CL_GetVoiceServiceModeLabel( void ) {
	return QL_GetOnlineServicesModeLabel();
}

/*
=============
CL_GetVoiceServicePolicyLabel

Returns the overall online-services policy label used by the retained voice
compatibility lane.
=============
*/
static const char *CL_GetVoiceServicePolicyLabel( void ) {
	return QL_GetOnlineServicesPolicyLabel();
}

/*
=============
CL_LogVoiceServiceFallback

Publishes explicit diagnostics whenever the retained voice command surface
falls back to the local speaking-state bridge.
=============
*/
static void CL_LogVoiceServiceFallback( const char *commandName, const char *reason ) {
	Com_DPrintf( "%s voice fallback: %s (%s [%s])\n",
		commandName ? commandName : "voice",
		reason ? reason : "local speaking-state fallback active",
		CL_GetVoiceServiceModeLabel(),
		CL_GetVoiceServicePolicyLabel() );
}

/*
=============
CL_LogVoiceTransportLifecycle

Publishes explicit diagnostics whenever the retained Steam voice transport
lane hits a compatibility-only send or receive failure.
=============
*/
static void CL_LogVoiceTransportLifecycle( const char *stage, const char *reason ) {
	Com_DPrintf( "%s voice transport: %s (%s [%s])\n",
		stage ? stage : "voice_transport",
		reason ? reason : "voice transport unavailable",
		CL_GetVoiceServiceModeLabel(),
		CL_GetVoiceServicePolicyLabel() );
}

/*
=============
CL_LogMatchmakingServiceIgnored

Publishes provider-aware diagnostics whenever a client matchmaking or social
presence command is ignored by the retained compatibility policy.
=============
*/
void CL_LogMatchmakingServiceIgnored( const char *commandName, const char *reason ) {
	Com_DPrintf( "%s ignored: %s (%s [%s])\n",
		commandName ? commandName : "matchmaking",
		reason ? reason : "matchmaking provider unavailable",
		CL_GetMatchmakingServiceProviderLabel(),
		CL_GetMatchmakingServicePolicyLabel() );
}

/*
=============
CL_LogMatchmakingCallbackLifecycle

Publishes provider-aware diagnostics whenever the retained matchmaking callback
lane handles a Steam P2P session request.
=============
*/
static void CL_LogMatchmakingCallbackLifecycle( const char *stage, const char *reason ) {
	Com_DPrintf( "%s callback: %s (%s [%s])\n",
		stage ? stage : "matchmaking_callback",
		reason ? reason : "callback updated",
		CL_GetMatchmakingServiceProviderLabel(),
		CL_GetMatchmakingServicePolicyLabel() );
}

/*
=============
CL_LogStatsServiceIgnored

Publishes provider-aware diagnostics whenever a client stats command is ignored
by the retained compatibility policy.
=============
*/
static void CL_LogStatsServiceIgnored( const char *commandName, const char *reason ) {
	Com_DPrintf( "%s ignored: %s (%s [%s])\n",
		commandName ? commandName : "stats",
		reason ? reason : "stats provider unavailable",
		CL_GetStatsServiceProviderLabel(),
		CL_GetStatsServicePolicyLabel() );
}

/*
=============
CL_LogStatsServiceRegistrationSkipped

Publishes provider-aware diagnostics whenever the retained stats_clear command
is not registered during client bootstrap.
=============
*/
static void CL_LogStatsServiceRegistrationSkipped( const char *reason ) {
	Com_DPrintf( "stats_clear registration skipped: %s (%s [%s])\n",
		reason ? reason : "stats provider unavailable",
		CL_GetStatsServiceProviderLabel(),
		CL_GetStatsServicePolicyLabel() );
}

/*
=============
CL_LogSocialOverlayIgnored

Publishes provider-aware diagnostics whenever a Steam social-overlay command is
ignored by the retained compatibility policy.
=============
*/
static void CL_LogSocialOverlayIgnored( const char *commandName, const char *reason ) {
	Com_DPrintf( "%s ignored: %s (%s [%s])\n",
		commandName ? commandName : "social_overlay",
		reason ? reason : "social overlay provider unavailable",
		CL_GetSocialOverlayServiceProviderLabel(),
		CL_GetSocialOverlayServicePolicyLabel() );
}

/*
=============
CL_RefreshPlatformServiceCvars

Mirrors the retained client platform-service provider/policy labels through ROM
cvars for diagnostics and bounded compatibility reporting.
=============
*/
static void CL_RefreshPlatformServiceCvars( void ) {
	Cvar_Set( "cl_onlineServicesMode", QL_GetOnlineServicesModeLabel() );
	Cvar_Set( "cl_onlineServicesPolicy", QL_GetOnlineServicesPolicyLabel() );
	Cvar_Set( "cl_identityBootstrapMode", CL_GetIdentityBootstrapModeLabel() );
	Cvar_Set( "cl_identityBootstrapPolicy", CL_GetIdentityBootstrapPolicyLabel() );
	Cvar_Set( "cl_voiceServiceMode", CL_GetVoiceServiceModeLabel() );
	Cvar_Set( "cl_voiceServicePolicy", CL_GetVoiceServicePolicyLabel() );
	Cvar_Set( "cl_workshopProvider", CL_GetWorkshopServiceProviderLabel() );
	Cvar_Set( "cl_workshopPolicy", CL_GetWorkshopServicePolicyLabel() );
	Cvar_Set( "cl_matchmakingProvider", CL_GetMatchmakingServiceProviderLabel() );
	Cvar_Set( "cl_matchmakingPolicy", CL_GetMatchmakingServicePolicyLabel() );
	Cvar_Set( "cl_statsProvider", CL_GetStatsServiceProviderLabel() );
	Cvar_Set( "cl_statsPolicy", CL_GetStatsServicePolicyLabel() );
	Cvar_Set( "cl_socialOverlayProvider", CL_GetSocialOverlayServiceProviderLabel() );
	Cvar_Set( "cl_socialOverlayPolicy", CL_GetSocialOverlayServicePolicyLabel() );
	Cvar_Set( "ui_subscriptionBridgeMode", QL_GetOnlineServicesModeLabel() );
	Cvar_Set( "ui_subscriptionBridgePolicy", QL_GetOnlineServicesPolicyLabel() );
}

/*
=============
CL_WorkshopServiceSupportsSteamBootstrap

Returns qtrue when the retained Steam UGC bootstrap path is the active owner
for workshop item resolution in the current compatibility lane.
=============
*/
static qboolean CL_WorkshopServiceSupportsSteamBootstrap( void ) {
	const ql_platform_feature_descriptor *workshop = CL_GetWorkshopServiceDescriptor();
	const char *provider = CL_GetWorkshopServiceProviderLabel();

	if ( !workshop || !workshop->compiled || !workshop->initialised ) {
		return qfalse;
	}

	return ( strstr( provider, "Steam UGC" ) != NULL );
}

cvar_t	*cl_nodelta;
cvar_t	*cl_debugMove;
cvar_t	*cl_allowConsoleChat;

cvar_t	*cl_noprint;
cvar_t	*cl_motd;

cvar_t	*rcon_client_password;
cvar_t	*rconAddress;

cvar_t	*cl_timeout;
cvar_t	*cl_maxpackets;
cvar_t	*cl_packetdup;
cvar_t	*cl_timeNudge;
cvar_t	*cl_showTimeDelta;
cvar_t	*cl_freezeDemo;
cvar_t	*cl_quitOnDemoCompleted;
cvar_t	*cl_demoRecordMessage;
cvar_t	*cl_avidemo_latch;
cvar_t	*cl_avidemo_mintime;
cvar_t	*cl_avidemo_maxtime;

cvar_t	*cl_shownet;
cvar_t	*cl_showSend;
cvar_t	*cl_timedemo;
cvar_t	*cl_avidemo;
cvar_t	*cl_forceavidemo;

cvar_t	*cl_freelook;
cvar_t	*cl_sensitivity;

cvar_t	*cl_yawspeed;
cvar_t	*cl_pitchspeed;
cvar_t	*cl_run;
cvar_t	*cl_anglespeedkey;
cvar_t	*cl_viewAccel;

cvar_t	*cl_mouseAccel;
cvar_t	*cl_mouseAccelDebug;
cvar_t	*cl_mouseAccelOffset;
cvar_t	*cl_mouseAccelPower;
cvar_t	*cl_mouseSensCap;

cvar_t	*m_pitch;
cvar_t	*m_yaw;
cvar_t	*m_forward;
cvar_t	*m_side;
cvar_t	*m_filter;
cvar_t	*m_cpi;

cvar_t	*cl_activeAction;
cvar_t	*cl_platform;

cvar_t	*cl_motdString;

cvar_t	*cl_allowDownload;
cvar_t	*cl_conXOffset;
cvar_t	*cl_inGameVideo;

cvar_t	*cl_autoTimeNudge;
cvar_t	*cl_contimestamps;
cvar_t	*cl_mouseAccelStyle;
cvar_t	*cl_guid;
cvar_t	*cl_punkbuster;

cvar_t	*cl_serverStatusResendTime;
cvar_t	*cl_trn;
static cvar_t	*cl_lobbyAutoConnect;
static cvar_t	*cl_steamMaxLobbyClients;
clientActive_t		cl;
clientConnection_t	clc;
clientStatic_t		cls;
vm_t				*cgvm;

// Structure containing functions exported from refresh DLL
refexport_t	re;

typedef struct image_s image_t;

#ifndef GL_REPEAT
#define GL_REPEAT 0x2901
#endif

#ifndef GL_CLAMP
#define GL_CLAMP 0x2900
#endif

#ifndef LIGHTMAP_2D
#define LIGHTMAP_2D -4
#endif

void RE_RegisterFont( const char *fontName, int pointSize, fontInfo_t *font );
image_t *R_CreateImage( const char *name, const byte *pic, int width, int height, qboolean mipmap, qboolean allowPicmip, int glWrapClampMode );
image_t *R_LoadImageFromMemory( const char *name, const byte *buffer, int bufferLength, qboolean mipmap, qboolean allowPicmip, int glWrapClampMode );
qhandle_t RE_RegisterShaderFromImage( const char *name, int lightmapIndex, image_t *image, qboolean mipRawImage );

ping_t	cl_pinglist[MAX_PINGREQUESTS];

typedef struct serverStatus_s
{
	char string[BIG_INFO_STRING];
	netadr_t address;
	int time, startTime;
	qboolean pending;
	qboolean print;
	qboolean retrieved;
} serverStatus_t;

serverStatus_t cl_serverStatusList[MAX_SERVERSTATUSREQUESTS];
int serverStatusCount;

#if defined __USEA3D && defined __A3D_GEOM
	void hA3Dg_ExportRenderGeom (refexport_t *incoming_re);
#endif

extern void SV_BotFrame( int time );
void CL_CheckForResend( void );
void CL_ShowIP_f(void);
void CL_ServerStatus_f(void);
void CL_ServerStatusResponse( netadr_t from, msg_t *msg );
void CL_Web_ShowBrowser_f( void );
void CL_Web_ChangeHash_f( void );
void CL_Web_HideBrowser_f( void );
void CL_Web_ShowError_f( void );
void CL_Web_ClearCache_f( void );
void CL_Web_Reload_f( void );

/*
=============
CL_Steam_ClearStats_f

Mirrors the retail stats_clear command through the Steam user-stats reset path.
=============
*/
static void CL_Steam_ClearStats_f( void ) {
	if ( !CL_SteamServicesEnabled() ) {
		CL_LogStatsServiceIgnored( "stats_clear", "stats provider unavailable" );
		return;
	}

	if ( !QL_Steamworks_ClearStats( qtrue ) ) {
		CL_LogStatsServiceIgnored( "stats_clear", "clear request failed" );
	}
}

static qboolean cl_voiceRecordingActive;
static qboolean cl_statsClearRegistered;

#define CL_STEAM_BROWSER_EVENT_COUNT 32
#define CL_STEAM_BROWSER_EVENT_NAME_LENGTH 96
#define CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH 2048
#define CL_STEAM_SERVER_ID_CONFIGSTRING 0x2ca
#define CL_STEAM_WORKSHOP_ITEMS_CONFIGSTRING 0x2cb
#define CL_STEAM_WORKSHOP_ITEM_STATE_INSTALLED 0x4u
#define CL_STEAM_WORKSHOP_ITEM_DELIMS " \t\r\n"
#define CL_STEAM_MAX_WORKSHOP_ITEMS 256
#define CL_STEAM_VOICE_CHANNEL 1
#define CL_STEAM_VOICE_SAMPLE_RATE 22050u
#define CL_STEAM_VOICE_MAX_COMPRESSED 0x4000
#define CL_STEAM_VOICE_MAX_DECOMPRESSED 0x8000

typedef struct {
	int sequence;
	char name[CL_STEAM_BROWSER_EVENT_NAME_LENGTH];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];
} clSteamBrowserEvent_t;

typedef struct {
	qboolean callbackRegistrationActive;
	qboolean currentLobbyValid;
	uint64_t currentLobbyId;
	int eventSequence;
	int eventHead;
	clSteamBrowserEvent_t events[CL_STEAM_BROWSER_EVENT_COUNT];
} clSteamCallbackState_t;

static clSteamCallbackState_t cl_steamCallbackState;

typedef struct {
	uint32_t	itemIdLow;
	uint32_t	itemIdHigh;
	int			requestNumber;
	qboolean	downloadRequested;
	qboolean	completed;
} clSteamWorkshopItem_t;

typedef struct {
	qboolean				active;
	qboolean				queueActive;
	qboolean				downloadsRequested;
	int						totalItems;
	int						itemCount;
	int						activeItemIndex;
	uint64_t				downloadedBytes;
	uint64_t				totalBytes;
	clSteamWorkshopItem_t	items[CL_STEAM_MAX_WORKSHOP_ITEMS];
} clSteamWorkshopDownloadState_t;

static clSteamWorkshopDownloadState_t cl_steamWorkshopDownloadState;

/*
=============
CL_SetClientSpeakingState

Publishes a speaking-state update for the requested client through the native
cgame export used by the retail voice sidecar.
=============
*/
static void CL_SetClientSpeakingState( int clientNum, qboolean speaking ) {
	if ( !cgvm || cls.state != CA_ACTIVE || !cl.snap.valid ) {
		return;
	}

	VM_Call( cgvm, CG_SET_CLIENT_SPEAKING_STATE, clientNum, speaking ? 1 : 0 );
}

/*
=============
CL_SetLocalSpeakingState

Publishes the local speaking-state sidecar through the native cgame export
used by the retail host voice path.
=============
*/
static void CL_SetLocalSpeakingState( qboolean speaking ) {
	if ( !cgvm || cls.state != CA_ACTIVE || !cl.snap.valid ) {
		return;
	}

	VM_Call( cgvm, CG_SET_CLIENT_SPEAKING_STATE, cl.snap.ps.clientNum, speaking ? 1 : 0 );
}

/*
=============
CL_VoiceStartRecording_f

Provides the retail `+voice` command surface, using the local speaking-state
bridge as the current fallback when live voice services are unavailable.
=============
*/
static void CL_VoiceStartRecording_f( void ) {
	uint32_t steamIdLow;
	uint32_t steamIdHigh;

	if ( cl_voiceRecordingActive ) {
		return;
	}

	cl_voiceRecordingActive = qtrue;
	if ( !CL_SteamServicesEnabled() ) {
		CL_LogVoiceServiceFallback( "+voice", "local speaking-state fallback active" );
	} else {
		if ( QL_Steamworks_GetUserSteamID( &steamIdLow, &steamIdHigh ) ) {
			QL_Steamworks_SetInGameVoiceSpeaking( steamIdLow, steamIdHigh, qtrue );
		}
		QL_Steamworks_StartVoiceRecording();
		Com_DPrintf( "Started recording - optimal sample rate %d\n",
			(int)QL_Steamworks_GetVoiceOptimalSampleRate() );
	}
	CL_SetLocalSpeakingState( qtrue );
}

/*
=============
CL_VoiceStopRecording_f

Provides the retail `-voice` command surface, clearing the local speaking-state
fallback when the key is released.
=============
*/
static void CL_VoiceStopRecording_f( void ) {
	uint32_t steamIdLow;
	uint32_t steamIdHigh;

	if ( !cl_voiceRecordingActive ) {
		return;
	}

	if ( !CL_SteamServicesEnabled() ) {
		CL_LogVoiceServiceFallback( "-voice", "local speaking-state fallback active" );
	} else {
		QL_Steamworks_StopVoiceRecording();
		if ( QL_Steamworks_GetUserSteamID( &steamIdLow, &steamIdHigh ) ) {
			QL_Steamworks_SetInGameVoiceSpeaking( steamIdLow, steamIdHigh, qfalse );
		}
	}
	cl_voiceRecordingActive = qfalse;
	CL_SetLocalSpeakingState( qfalse );
}

/*
=============
CL_ParseSteamIdString

Parses a decimal SteamID string into two 32-bit identity words.
=============
*/
static qboolean CL_ParseSteamIdString( const char *steamId, uint32_t *steamIdLow, uint32_t *steamIdHigh ) {
	const char *ch;
	unsigned long long value;

	if ( steamIdLow ) {
		*steamIdLow = 0;
	}
	if ( steamIdHigh ) {
		*steamIdHigh = 0;
	}

	if ( !steamId || !steamId[0] || !steamIdLow || !steamIdHigh ) {
		return qfalse;
	}

	value = 0;
	for ( ch = steamId; *ch; ++ch ) {
		unsigned int digit;

		if ( *ch < '0' || *ch > '9' ) {
			return qfalse;
		}

		digit = (unsigned int)( *ch - '0' );
		if ( value > ( ULLONG_MAX - digit ) / 10ull ) {
			return qfalse;
		}

		value = value * 10ull + digit;
	}

	*steamIdLow = (uint32_t)( value & 0xffffffffull );
	*steamIdHigh = (uint32_t)( ( value >> 32 ) & 0xffffffffull );
	return qtrue;
}

/*
=============
CL_CopyClientIdentity

Uses the retail native cgame export when it is available to recover the
selected-client identity sidecar.
=============
*/
static qboolean CL_CopyClientIdentity( int clientNum, cgameClientIdentity_t *identity ) {
	if ( !identity ) {
		return qfalse;
	}

	memset( identity, 0, sizeof( *identity ) );

	if ( !cgvm || !( cgvm->entryPoint || cgvm->dllExports ) ) {
		return qfalse;
	}

	if ( !VM_Call( cgvm, CG_COPY_CLIENT_IDENTITY, clientNum, (int)(intptr_t)identity ) ) {
		return qfalse;
	}

	return ( identity->identityLow | identity->identityHigh ) ? qtrue : qfalse;
}

/*
=============
CL_ClearDownloadProgressCvars
=============
*/
static void CL_ClearDownloadProgressCvars( void ) {
	Cvar_Set( "cl_downloadName", "" );
	Cvar_Set( "cl_downloadItem", "" );
	Cvar_Set( "cl_downloadCount", "0" );
	Cvar_Set( "cl_downloadSize", "0" );
}

/*
=============
CL_Workshop_ClearBootstrapState
=============
*/
static void CL_Workshop_ClearBootstrapState( qboolean clearProgressCvars ) {
	Com_Memset( &cl_steamWorkshopDownloadState, 0, sizeof( cl_steamWorkshopDownloadState ) );
	cl_steamWorkshopDownloadState.activeItemIndex = -1;

	if ( clearProgressCvars ) {
		CL_ClearDownloadProgressCvars();
	}
}

/*
=============
CL_GetConfigStringValue
=============
*/
static const char *CL_GetConfigStringValue( int index ) {
	int offset;

	if ( index < 0 || index >= MAX_CONFIGSTRINGS ) {
		return "";
	}

	offset = cl.gameState.stringOffsets[index];
	if ( !offset ) {
		return "";
	}

	return cl.gameState.stringData + offset;
}

/*
=============
CL_GetServerSteamId

Resolves the published Steam gameserver identity from the retained client
configstring.
=============
*/
static qboolean CL_GetServerSteamId( uint32_t *steamIdLow, uint32_t *steamIdHigh ) {
	return CL_ParseSteamIdString( CL_GetConfigStringValue( CL_STEAM_SERVER_ID_CONFIGSTRING ), steamIdLow, steamIdHigh );
}

/*
=============
CL_Workshop_UpdateProgressCvars
=============
*/
static void CL_Workshop_UpdateProgressCvars( void ) {
	char downloaded[32];
	char total[32];

	Com_sprintf( downloaded, sizeof( downloaded ), "%llu", (unsigned long long)cl_steamWorkshopDownloadState.downloadedBytes );
	Com_sprintf( total, sizeof( total ), "%llu", (unsigned long long)cl_steamWorkshopDownloadState.totalBytes );
	Cvar_Set( "cl_downloadCount", downloaded );
	Cvar_Set( "cl_downloadSize", total );
}

/*
=============
CL_Workshop_RefreshProgress
=============
*/
static qboolean CL_Workshop_RefreshProgress( int itemIndex ) {
	clSteamWorkshopItem_t	*item;
	uint64_t				downloaded;
	uint64_t				total;

	if ( itemIndex < 0 || itemIndex >= cl_steamWorkshopDownloadState.itemCount ) {
		return qfalse;
	}

	item = &cl_steamWorkshopDownloadState.items[itemIndex];
	downloaded = cl_steamWorkshopDownloadState.downloadedBytes;
	total = cl_steamWorkshopDownloadState.totalBytes;

	if ( !QL_Steamworks_GetItemDownloadInfo( item->itemIdLow, item->itemIdHigh, &downloaded, &total ) ) {
		return qfalse;
	}

	cl_steamWorkshopDownloadState.downloadedBytes = downloaded;
	cl_steamWorkshopDownloadState.totalBytes = total;
	CL_Workshop_UpdateProgressCvars();
	return qtrue;
}

/*
=============
CL_Workshop_SetActiveItem
=============
*/
static void CL_Workshop_SetActiveItem( int itemIndex ) {
	clSteamWorkshopItem_t	*item;
	unsigned long long		itemId;
	char					itemString[32];
	char					downloadName[64];

	if ( itemIndex < 0 || itemIndex >= cl_steamWorkshopDownloadState.itemCount ) {
		return;
	}

	item = &cl_steamWorkshopDownloadState.items[itemIndex];
	itemId = ( (unsigned long long)item->itemIdHigh << 32 ) | item->itemIdLow;

	cl_steamWorkshopDownloadState.activeItemIndex = itemIndex;
	cl_steamWorkshopDownloadState.downloadedBytes = 0;
	cl_steamWorkshopDownloadState.totalBytes = 0;

	Com_sprintf( itemString, sizeof( itemString ), "%llu", itemId );
	Com_sprintf( downloadName, sizeof( downloadName ), "Workshop item %i of %i", item->requestNumber, cl_steamWorkshopDownloadState.totalItems );
	Cvar_Set( "cl_downloadItem", itemString );
	Cvar_Set( "cl_downloadName", downloadName );
	CL_Workshop_UpdateProgressCvars();
	Cvar_SetValue( "cl_downloadTime", cls.realtime );
	CL_Workshop_RefreshProgress( itemIndex );
}

/*
=============
CL_Workshop_FindItemIndex
=============
*/
static int CL_Workshop_FindItemIndex( uint32_t itemIdLow, uint32_t itemIdHigh ) {
	int i;

	for ( i = 0; i < cl_steamWorkshopDownloadState.itemCount; ++i ) {
		clSteamWorkshopItem_t *item = &cl_steamWorkshopDownloadState.items[i];

		if ( item->itemIdLow == itemIdLow && item->itemIdHigh == itemIdHigh ) {
			return i;
		}
	}

	return -1;
}

/*
=============
CL_Workshop_ClearActiveDownload
=============
*/
static void CL_Workshop_ClearActiveDownload( void ) {
	cl_steamWorkshopDownloadState.activeItemIndex = -1;
	cl_steamWorkshopDownloadState.downloadedBytes = 0;
	cl_steamWorkshopDownloadState.totalBytes = 0;
	CL_Workshop_UpdateProgressCvars();
}

/*
=============
CL_Workshop_StartDownload
=============
*/
static qboolean CL_Workshop_StartDownload( int itemIndex ) {
	clSteamWorkshopItem_t	*item;
	unsigned long long		itemId;
	char					detail[128];

	if ( itemIndex < 0 || itemIndex >= cl_steamWorkshopDownloadState.itemCount ) {
		return qfalse;
	}

	item = &cl_steamWorkshopDownloadState.items[itemIndex];
	itemId = ( (unsigned long long)item->itemIdHigh << 32 ) | item->itemIdLow;
	if ( !QL_Steamworks_DownloadItem( item->itemIdLow, item->itemIdHigh, qtrue ) ) {
		Com_sprintf( detail, sizeof( detail ), "item %llu download request failed", itemId );
		CL_LogWorkshopLifecycle( "start-download", detail );
		return qfalse;
	}

	item->downloadRequested = qtrue;
	cl_steamWorkshopDownloadState.queueActive = qtrue;
	cl_steamWorkshopDownloadState.downloadsRequested = qtrue;
	CL_Workshop_SetActiveItem( itemIndex );
	return qtrue;
}

/*
=============
CL_Workshop_AdvanceQueue
=============
*/
static qboolean CL_Workshop_AdvanceQueue( void ) {
	int						i;
	clSteamWorkshopItem_t	*item;

	for ( i = 0; i < cl_steamWorkshopDownloadState.itemCount; ++i ) {
		item = &cl_steamWorkshopDownloadState.items[i];

		if ( item->completed || item->downloadRequested ) {
			continue;
		}

		if ( CL_Workshop_StartDownload( i ) ) {
			return qtrue;
		}

		item->completed = qtrue;
	}

	cl_steamWorkshopDownloadState.activeItemIndex = -1;
	cl_steamWorkshopDownloadState.downloadedBytes = 0;
	cl_steamWorkshopDownloadState.totalBytes = 0;
	return qfalse;
}

/*
=============
CL_Workshop_FinalizeInstalledItem
=============
*/
static void CL_Workshop_FinalizeInstalledItem( int itemIndex ) {
	clSteamWorkshopItem_t *item;
	char detail[128];

	if ( itemIndex < 0 || itemIndex >= cl_steamWorkshopDownloadState.itemCount ) {
		return;
	}

	item = &cl_steamWorkshopDownloadState.items[itemIndex];
	if ( item->completed ) {
		return;
	}

	item->completed = qtrue;
	if ( cl_steamWorkshopDownloadState.activeItemIndex == itemIndex ) {
		unsigned long long itemId = ( (unsigned long long)item->itemIdHigh << 32 ) | item->itemIdLow;

		Com_sprintf( detail, sizeof( detail ), "item %llu download complete", itemId );
		CL_LogWorkshopLifecycle( "item-complete", detail );
		CL_Workshop_ClearActiveDownload();
	}
}

/*
=============
CL_Workshop_FailActiveDownload
=============
*/
static void CL_Workshop_FailActiveDownload( int result ) {
	clSteamWorkshopItem_t *item;
	unsigned long long itemId;
	int itemIndex;
	char detail[128];

	itemIndex = cl_steamWorkshopDownloadState.activeItemIndex;
	if ( itemIndex < 0 || itemIndex >= cl_steamWorkshopDownloadState.itemCount ) {
		return;
	}

	item = &cl_steamWorkshopDownloadState.items[itemIndex];
	itemId = ( (unsigned long long)item->itemIdHigh << 32 ) | item->itemIdLow;
	Com_sprintf( detail, sizeof( detail ), "item %llu failed with EResult code %i", itemId, result );
	CL_LogWorkshopLifecycle( "item-failed", detail );
	item->completed = qtrue;
	CL_Workshop_ClearActiveDownload();
}

/*
=============
CL_Workshop_DownloadsSettled
=============
*/
static qboolean CL_Workshop_DownloadsSettled( void ) {
	if ( cl_steamWorkshopDownloadState.activeItemIndex >= 0 ) {
		clSteamWorkshopItem_t *item = &cl_steamWorkshopDownloadState.items[cl_steamWorkshopDownloadState.activeItemIndex];

		CL_Workshop_RefreshProgress( cl_steamWorkshopDownloadState.activeItemIndex );
		if ( !( QL_Steamworks_GetItemState( item->itemIdLow, item->itemIdHigh ) & CL_STEAM_WORKSHOP_ITEM_STATE_INSTALLED ) ) {
			return qfalse;
		}

		CL_Workshop_FinalizeInstalledItem( cl_steamWorkshopDownloadState.activeItemIndex );
	}

	if ( CL_Workshop_AdvanceQueue() ) {
		return qfalse;
	}

	if ( cl_steamWorkshopDownloadState.queueActive ) {
		CL_LogWorkshopLifecycle( "queue-complete", "download completed for all required items" );
		cl_steamWorkshopDownloadState.queueActive = qfalse;
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_Workshop_BeginBootstrap
=============
*/
static qboolean CL_Workshop_BeginBootstrap( void ) {
	const char	*requiredItems;
	char		workshopItems[BIG_INFO_STRING];
	char		detail[256];
	char		*token;
	const char	*workshopProvider;
	const char	*workshopPolicy;
	int			totalItems;
	int			requestNumber;

	requiredItems = CL_GetConfigStringValue( CL_STEAM_WORKSHOP_ITEMS_CONFIGSTRING );
	if ( !requiredItems[0] ) {
		return qfalse;
	}

	Q_strncpyz( workshopItems, requiredItems, sizeof( workshopItems ) );
	workshopProvider = CL_GetWorkshopServiceProviderLabel();
	workshopPolicy = CL_GetWorkshopServicePolicyLabel();
	Com_Printf( "Server requires the following workshop items via %s [%s]: %s\n",
		workshopProvider, workshopPolicy, workshopItems );
	if ( !CL_WorkshopServiceSupportsSteamBootstrap() ) {
		Com_Printf( "Workshop bootstrap unavailable for %s [%s]; keeping compatibility-only fallback for required items.\n",
			workshopProvider, workshopPolicy );
		return qfalse;
	}

	totalItems = 0;
	for ( token = strtok( workshopItems, CL_STEAM_WORKSHOP_ITEM_DELIMS ); token; token = strtok( NULL, CL_STEAM_WORKSHOP_ITEM_DELIMS ) ) {
		totalItems++;
	}

	if ( totalItems <= 0 ) {
		return qfalse;
	}

	Com_sprintf( detail, sizeof( detail ), "server requires %i workshop item(s)", totalItems );
	CL_LogWorkshopLifecycle( "bootstrap-begin", detail );

	CL_Workshop_ClearBootstrapState( qtrue );
	cl_steamWorkshopDownloadState.active = qtrue;
	cl_steamWorkshopDownloadState.totalItems = totalItems;

	Q_strncpyz( workshopItems, requiredItems, sizeof( workshopItems ) );
	requestNumber = 0;
	for ( token = strtok( workshopItems, CL_STEAM_WORKSHOP_ITEM_DELIMS ); token; token = strtok( NULL, CL_STEAM_WORKSHOP_ITEM_DELIMS ) ) {
		clSteamWorkshopItem_t	*item;
		uint32_t				itemIdLow;
		uint32_t				itemIdHigh;
		int						itemIndex;

		if ( cl_steamWorkshopDownloadState.itemCount >= CL_STEAM_MAX_WORKSHOP_ITEMS ) {
			Com_sprintf( detail, sizeof( detail ), "ignoring workshop items beyond %i required entries", CL_STEAM_MAX_WORKSHOP_ITEMS );
			CL_LogWorkshopLifecycle( "bootstrap-truncate", detail );
			break;
		}

		if ( !CL_ParseSteamIdString( token, &itemIdLow, &itemIdHigh ) ) {
			continue;
		}

		itemIndex = cl_steamWorkshopDownloadState.itemCount++;
		item = &cl_steamWorkshopDownloadState.items[itemIndex];
		item->itemIdLow = itemIdLow;
		item->itemIdHigh = itemIdHigh;

		if ( QL_Steamworks_GetItemState( itemIdLow, itemIdHigh ) & CL_STEAM_WORKSHOP_ITEM_STATE_INSTALLED ) {
			item->completed = qtrue;
			continue;
		}

		item->requestNumber = ++requestNumber;
		if ( cl_steamWorkshopDownloadState.activeItemIndex < 0 ) {
			if ( !CL_Workshop_StartDownload( itemIndex ) ) {
				item->completed = qtrue;
			}
		}
	}

	if ( cl_steamWorkshopDownloadState.itemCount <= 0 ) {
		CL_Workshop_ClearBootstrapState( qtrue );
		return qfalse;
	}

	cls.state = CA_CONNECTED;
	return qtrue;
}

/*
=============
CL_GetWorkshopDownloadInfo
=============
*/
qboolean CL_GetWorkshopDownloadInfo( unsigned int itemIdLow, unsigned int itemIdHigh, unsigned long long *outDownloaded, unsigned long long *outTotal ) {
	clSteamWorkshopItem_t *item;

	if ( outDownloaded ) {
		*outDownloaded = 0;
	}
	if ( outTotal ) {
		*outTotal = 0;
	}

	if ( !cl_steamWorkshopDownloadState.active || cl_steamWorkshopDownloadState.activeItemIndex < 0 ) {
		return qfalse;
	}

	if ( itemIdLow || itemIdHigh ) {
		item = &cl_steamWorkshopDownloadState.items[cl_steamWorkshopDownloadState.activeItemIndex];
		if ( item->itemIdLow != itemIdLow || item->itemIdHigh != itemIdHigh ) {
			return qfalse;
		}
	}

	if ( outDownloaded ) {
		*outDownloaded = (unsigned long long)cl_steamWorkshopDownloadState.downloadedBytes;
	}
	if ( outTotal ) {
		*outTotal = (unsigned long long)cl_steamWorkshopDownloadState.totalBytes;
	}

	return qtrue;
}

/*
=============
CL_GetClientSteamId

Resolves a scoreboard client slot into the Steam identity used by the retail
overlay commands. Native cgame builds expose this through
CG_COPY_CLIENT_IDENTITY; qvm-style fallbacks rebuild it from CS_PLAYERS.
=============
*/
static qboolean CL_GetClientSteamId( int clientNum, uint32_t *steamIdLow, uint32_t *steamIdHigh ) {
	cgameClientIdentity_t identity;
	char info[MAX_INFO_STRING];
	int offset;
	const char *steamId;

	if ( steamIdLow ) {
		*steamIdLow = 0;
	}
	if ( steamIdHigh ) {
		*steamIdHigh = 0;
	}

	if ( !steamIdLow || !steamIdHigh || clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return qfalse;
	}

	if ( CL_CopyClientIdentity( clientNum, &identity ) ) {
		*steamIdLow = identity.identityLow;
		*steamIdHigh = identity.identityHigh;
		return qtrue;
	}

	offset = cl.gameState.stringOffsets[CS_PLAYERS + clientNum];
	if ( !offset ) {
		return qfalse;
	}

	Q_strncpyz( info, cl.gameState.stringData + offset, sizeof( info ) );
	steamId = Info_ValueForKey( info, "steamid" );

	return CL_ParseSteamIdString( steamId, steamIdLow, steamIdHigh );
}

/*
=============
CL_IsVoiceSenderMuted

Checks the reconstructed local mute set before mixing remote Steam voice.
=============
*/
static qboolean CL_IsVoiceSenderMuted( int clientNum ) {
	uint32_t steamIdLow;
	uint32_t steamIdHigh;

	if ( !CL_GetClientSteamId( clientNum, &steamIdLow, &steamIdHigh ) ) {
		return qfalse;
	}

	return CL_IsSteamIdentityMuted( steamIdLow, steamIdHigh );
}

/*
=============
CL_Steam_SendVoicePacket

Pulls compressed voice from Steam and relays it to the published server
SteamID over channel 1, matching the retail client voice transport.
=============
*/
static void CL_Steam_SendVoicePacket( void ) {
	byte compressedVoice[CL_STEAM_VOICE_MAX_COMPRESSED];
	uint32_t compressedBytes;
	uint32_t serverIdLow;
	uint32_t serverIdHigh;
	CSteamID serverId;

	if ( !cl_voiceRecordingActive || cls.state < CA_CONNECTED ) {
		return;
	}

	if ( !CL_GetServerSteamId( &serverIdLow, &serverIdHigh ) ) {
		return;
	}

	compressedBytes = 0u;
	if ( !QL_Steamworks_GetCompressedVoice( compressedVoice, sizeof( compressedVoice ), &compressedBytes ) ) {
		return;
	}

	if ( compressedBytes == 0u ) {
		return;
	}

	serverId.value = ( (uint64_t)serverIdHigh << 32 ) | serverIdLow;
	if ( !QL_Steamworks_SendP2PPacket( &serverId, compressedVoice, compressedBytes, 1, CL_STEAM_VOICE_CHANNEL ) ) {
		CL_LogVoiceTransportLifecycle( "voice_send", "voice packet send failed" );
	}
}

/*
=============
CL_Steam_ProcessVoicePackets

Consumes incoming relayed Steam voice packets, applies the reconstructed mute
filter, updates the speaking-state sidecar, and feeds PCM into the sound
voice mixer.
=============
*/
static void CL_Steam_ProcessVoicePackets( void ) {
	uint32_t packetSize;
	char detail[128];

	packetSize = 0u;
	while ( QL_Steamworks_IsP2PPacketAvailable( &packetSize, CL_STEAM_VOICE_CHANNEL ) ) {
		byte *packetBuffer;
		uint32_t bytesRead;
		uint32_t voiceBytes;
		CSteamID remoteId;
		short decompressedVoice[CL_STEAM_VOICE_MAX_DECOMPRESSED / sizeof( short )];
		int clientNum;

		if ( packetSize == 0u ) {
			break;
		}

		packetBuffer = malloc( packetSize );
		if ( !packetBuffer ) {
			break;
		}

		bytesRead = 0u;
		voiceBytes = 0u;
		remoteId.value = 0ull;
		if ( !QL_Steamworks_ReadP2PPacket( packetBuffer, packetSize, &bytesRead, &remoteId, CL_STEAM_VOICE_CHANNEL ) || bytesRead <= 1u ) {
			CL_LogVoiceTransportLifecycle( "voice_receive", "voice packet read failed" );
			free( packetBuffer );
			packetSize = 0u;
			continue;
		}

		if ( !QL_Steamworks_DecompressVoice( packetBuffer + 1, bytesRead - 1, decompressedVoice, sizeof( decompressedVoice ), &voiceBytes, CL_STEAM_VOICE_SAMPLE_RATE ) ) {
			CL_LogVoiceTransportLifecycle( "voice_receive", "voice decompress failed" );
			free( packetBuffer );
			packetSize = 0u;
			continue;
		}

		if ( voiceBytes == 0u ) {
			Com_sprintf( detail, sizeof( detail ), "%u compressed voice bytes decompressed to 0", bytesRead - 1 );
			CL_LogVoiceTransportLifecycle( "voice_receive", detail );
			free( packetBuffer );
			packetSize = 0u;
			continue;
		}

		clientNum = packetBuffer[0];
		if ( clientNum >= 0 && clientNum < MAX_CLIENTS && !CL_IsVoiceSenderMuted( clientNum ) ) {
			CL_SetClientSpeakingState( clientNum, qtrue );
			S_AddVoiceSamples( clientNum, (int)( voiceBytes >> 1 ), decompressedVoice );
		}

		free( packetBuffer );
		packetSize = 0u;
	}
}

/*
=============
CL_Steam_OverlayCommand_f

Mirrors the retail clientviewprofile and clientfriendinvite command handler.
=============
*/
static void CL_Steam_OverlayCommand_f( void ) {
	const char *commandName;
	const char *dialog;
	int clientNum;
	uint32_t steamIdLow;
	uint32_t steamIdHigh;

	commandName = Cmd_Argv( 0 );
	if ( Cmd_Argc() < 2 ) {
		CL_LogSocialOverlayIgnored( commandName, "missing target client" );
		return;
	}

	if ( !CL_SteamServicesEnabled() ) {
		CL_LogSocialOverlayIgnored( commandName, "social overlay provider unavailable" );
		return;
	}

	dialog = NULL;

	if ( !Q_stricmp( commandName, "clientviewprofile" ) ) {
		dialog = "steamid";
	} else if ( !Q_stricmp( commandName, "clientfriendinvite" ) ) {
		dialog = "friendadd";
	}

	if ( !dialog ) {
		CL_LogSocialOverlayIgnored( commandName, "unsupported social overlay verb" );
		return;
	}

	clientNum = atoi( Cmd_Argv( 1 ) );
	if ( !CL_GetClientSteamId( clientNum, &steamIdLow, &steamIdHigh ) ) {
		CL_LogSocialOverlayIgnored( commandName, "target client has no Steam identity" );
		return;
	}

	if ( !QL_Steamworks_ActivateOverlayToUser( dialog, steamIdLow, steamIdHigh ) ) {
		CL_LogSocialOverlayIgnored( commandName, "overlay activation failed" );
	}
}

/*
=============
CL_Steam_ExecuteImmediateCommand

Routes Steam callback payloads through the retail immediate command path.
=============
*/
static void CL_Steam_ExecuteImmediateCommand( const char *command ) {
	if ( !command || !command[0] ) {
		return;
	}

	Cbuf_ExecuteText( EXEC_NOW, command );
}

/*
=============
CL_Steam_OnRichPresenceJoinRequested

Mirrors the retail rich-presence join callback by executing the provided
command string immediately through the client command path.
=============
*/
void CL_Steam_OnRichPresenceJoinRequested( const char *command ) {
	CL_Steam_ExecuteImmediateCommand( command );
}

/*
=============
CL_Steam_OnGameServerChangeRequested

Mirrors the retail server-change callback by seeding the password cvar when
present and routing the server target through the immediate connect path.
=============
*/
void CL_Steam_OnGameServerChangeRequested( const char *server, const char *password ) {
	if ( !server || !server[0] ) {
		return;
	}

	if ( password && password[0] ) {
		Cvar_Set( "password", password );
	}

	CL_Steam_ExecuteImmediateCommand( va( "connect %s\n", server ) );
}

/*
=============
CL_Steam_FormatSteamId

Formats a 64-bit Steam identity for event-name and JSON payload usage.
=============
*/
static void CL_Steam_FormatSteamId( uint64_t steamId, char *buffer, size_t bufferSize ) {
	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	Com_sprintf( buffer, bufferSize, "%llu", (unsigned long long)steamId );
}

/*
=============
CL_Steam_JsonEscape

Escapes a UTF-8 string for the retained browser-event payload cache.
=============
*/
static void CL_Steam_JsonEscape( const char *value, char *buffer, size_t bufferSize ) {
	const char *cursor;
	char *out;
	char *limit;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !value ) {
		return;
	}

	out = buffer;
	limit = buffer + bufferSize - 1;
	for ( cursor = value; *cursor && out < limit; ++cursor ) {
		unsigned char ch;

		ch = (unsigned char)*cursor;
		if ( ch == '\\' || ch == '"' ) {
			if ( out + 2 > limit ) {
				break;
			}
			*out++ = '\\';
			*out++ = (char)ch;
			continue;
		}

		if ( ch == '\n' ) {
			if ( out + 2 > limit ) {
				break;
			}
			*out++ = '\\';
			*out++ = 'n';
			continue;
		}

		if ( ch == '\r' ) {
			if ( out + 2 > limit ) {
				break;
			}
			*out++ = '\\';
			*out++ = 'r';
			continue;
		}

		if ( ch == '\t' ) {
			if ( out + 2 > limit ) {
				break;
			}
			*out++ = '\\';
			*out++ = 't';
			continue;
		}

		if ( ch < 0x20 ) {
			continue;
		}

		*out++ = (char)ch;
	}

	*out = '\0';
}

/*
=============
CL_Steam_ClearBrowserEvents

Resets the retained browser-event owner cache.
=============
*/
static void CL_Steam_ClearBrowserEvents( void ) {
	Com_Memset( cl_steamCallbackState.events, 0, sizeof( cl_steamCallbackState.events ) );
	cl_steamCallbackState.eventSequence = 0;
	cl_steamCallbackState.eventHead = 0;
}

/*
=============
CL_LogMicroTransactionCallbackLifecycle

Publishes provider-aware diagnostics whenever the retained microtransaction
authorization callback forwards one browser-facing purchase update.
=============
*/
static void CL_LogMicroTransactionCallbackLifecycle( const ql_steam_microtxn_authorization_response_t *event ) {
	Com_DPrintf( "microtxn.authorization callback: appid=%u order=%llu authorized=%d (%s [%s])\n",
		event ? event->appId : 0u,
		event ? (unsigned long long)event->orderId : 0ull,
		( event && event->authorized ) ? 1 : 0,
		CL_GetSocialOverlayServiceProviderLabel(),
		CL_GetSocialOverlayServicePolicyLabel() );
}

/*
=============
CL_LogBrowserEventLifecycle

Publishes provider-aware diagnostics whenever the retained browser-event owner
queues or defers a browser-facing event.
=============
*/
static void CL_LogBrowserEventLifecycle( const char *eventName, const char *reason ) {
	Com_DPrintf( "%s browser event: %s (%s [%s])\n",
		eventName ? eventName : "browser_event",
		reason ? reason : "event queued",
		CL_GetSocialOverlayServiceProviderLabel(),
		CL_GetSocialOverlayServicePolicyLabel() );
}

/*
=============
CL_WebView_PublishEvent

Queues one browser-facing event through the retained client owner lane.
=============
*/
void CL_WebView_PublishEvent( const char *name, const char *payload ) {
	clSteamBrowserEvent_t *event;
	char detail[128];
	int payloadLength;
	int slot;

	if ( !name || !name[0] ) {
		return;
	}

	if ( !CL_WebHost_HasLiveView() ) {
		CL_LogBrowserEventLifecycle( name, "queued without live view" );
	} else if ( !CL_WebHost_HasBoundWindowObject() ) {
		CL_LogBrowserEventLifecycle( name, "queued without window object" );
	}

	slot = cl_steamCallbackState.eventHead % CL_STEAM_BROWSER_EVENT_COUNT;
	event = &cl_steamCallbackState.events[slot];
	cl_steamCallbackState.eventHead++;
	cl_steamCallbackState.eventSequence++;

	event->sequence = cl_steamCallbackState.eventSequence;
	Q_strncpyz( event->name, name, sizeof( event->name ) );
	Q_strncpyz( event->payload, payload ? payload : "", sizeof( event->payload ) );

	payloadLength = (int)strlen( event->payload );
	Com_sprintf( detail, sizeof( detail ), "queued payload bytes=%d sequence=%d", payloadLength, event->sequence );
	CL_LogBrowserEventLifecycle( event->name, detail );
}

/*
=============
CL_Steam_PublishBrowserEvent

Queues a browser-facing Steam event through the retained client owner path.
=============
*/
static void CL_Steam_PublishBrowserEvent( const char *name, const char *payload ) {
	CL_WebView_PublishEvent( name, payload );
}

/*
=============
CL_WebView_InvokeCommNotice

Routes the retained communication-notice callback through the browser event lane.
=============
*/
void CL_WebView_InvokeCommNotice( const char *channel, const char *message ) {
	char escapedChannel[256];
	char escapedMessage[1024];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	CL_Steam_JsonEscape( channel ? channel : "", escapedChannel, sizeof( escapedChannel ) );
	CL_Steam_JsonEscape( message ? message : "", escapedMessage, sizeof( escapedMessage ) );
	Com_sprintf( payload, sizeof( payload ), "{\"channel\":\"%s\",\"message\":\"%s\"}", escapedChannel, escapedMessage );
	CL_WebView_PublishEvent( "web.commNotice", payload );
}

/*
=============
CL_WebView_PublishGameError

Packages the retail browser-visible game error payload and clears the latched
error string after publication.
=============
*/
void CL_WebView_PublishGameError( const char *message ) {
	char escapedMessage[MAXPRINTMSG * 2];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	CL_Steam_JsonEscape( message ? message : "", escapedMessage, sizeof( escapedMessage ) );
	Com_sprintf( payload, sizeof( payload ), "{\"text\":\"%s\"}", escapedMessage );
	CL_WebView_PublishEvent( "game.error", payload );
	Cvar_Set( "com_errorMessage", "" );
}

/*
=============
CL_WebView_PublishGameEnd
=============
*/
void CL_WebView_PublishGameEnd( void ) {
	CL_WebView_PublishEvent( "game.end", NULL );
}

/*
=============
CL_WebView_PublishCvarChange

Publishes browser-facing cvar updates while preserving the retail exclusion
for the video-window position cvars.
=============
*/
void CL_WebView_PublishCvarChange( const char *name, const char *value, qboolean replicate ) {
	char escapedName[128];
	char escapedValue[MAX_CVAR_VALUE_STRING * 2];
	char eventName[CL_STEAM_BROWSER_EVENT_NAME_LENGTH];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	if ( !name || !name[0] ) {
		return;
	}

	if ( !Q_stricmp( name, "vid_xpos" ) || !Q_stricmp( name, "vid_ypos" ) ) {
		return;
	}

	CL_Steam_JsonEscape( name, escapedName, sizeof( escapedName ) );
	CL_Steam_JsonEscape( value ? value : "", escapedValue, sizeof( escapedValue ) );
	Com_sprintf( eventName, sizeof( eventName ), "cvar.%s", name );
	Com_sprintf( payload, sizeof( payload ), "{\"name\":\"%s\",\"value\":\"%s\",\"replicate\":%d}", escapedName, escapedValue, replicate ? 1 : 0 );
	CL_WebView_PublishEvent( eventName, payload );
}

/*
=============
CL_WebView_PublishBindChanged
=============
*/
void CL_WebView_PublishBindChanged( const char *name, const char *value ) {
	char escapedName[128];
	char escapedValue[1024];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	CL_Steam_JsonEscape( name ? name : "", escapedName, sizeof( escapedName ) );
	CL_Steam_JsonEscape( value ? value : "", escapedValue, sizeof( escapedValue ) );
	Com_sprintf( payload, sizeof( payload ), "{\"name\":\"%s\",\"value\":\"%s\"}", escapedName, escapedValue );
	CL_WebView_PublishEvent( "bind.changed", payload );
}

/*
=============
CL_WebView_PublishGameStart
=============
*/
void CL_WebView_PublishGameStart( void ) {
	char address[128];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];
	netadr_t serverAddress;

	serverAddress = clc.serverAddress;
	if ( serverAddress.type == NA_BAD ) {
		serverAddress = clc.netchan.remoteAddress;
	}

	Q_strncpyz( address, NET_AdrToString( serverAddress ), sizeof( address ) );
	Com_sprintf( payload, sizeof( payload ), "{\"ip\":\"%s\",\"port\":%u}", address, (unsigned int)BigShort( serverAddress.port ) );
	CL_WebView_PublishEvent( "game.start", payload );
}

/*
=============
CL_WebView_PublishGameDemo
=============
*/
void CL_WebView_PublishGameDemo( const char *id, const char *name ) {
	char escapedId[MAX_QPATH * 2];
	char escapedName[MAX_QPATH * 2];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	CL_Steam_JsonEscape( id ? id : "", escapedId, sizeof( escapedId ) );
	CL_Steam_JsonEscape( name ? name : "", escapedName, sizeof( escapedName ) );
	Com_sprintf( payload, sizeof( payload ), "{\"id\":\"%s\",\"name\":\"%s\"}", escapedId, escapedName );
	CL_WebView_PublishEvent( "game.demo", payload );
}

/*
=============
CL_WebView_PublishGameScreenshot
=============
*/
void CL_WebView_PublishGameScreenshot( const char *id, const char *name ) {
	char escapedId[MAX_QPATH * 2];
	char escapedName[MAX_QPATH * 2];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	CL_Steam_JsonEscape( id ? id : "", escapedId, sizeof( escapedId ) );
	CL_Steam_JsonEscape( name ? name : "", escapedName, sizeof( escapedName ) );
	Com_sprintf( payload, sizeof( payload ), "{\"id\":\"%s\",\"name\":\"%s\"}", escapedId, escapedName );
	CL_WebView_PublishEvent( "game.screenshot", payload );
}

/*
=============
CL_Steam_SetCurrentLobby

Tracks the current Steam lobby identity through the retail client owner.
=============
*/
static void CL_Steam_SetCurrentLobby( uint64_t lobbyId ) {
	cl_steamCallbackState.currentLobbyValid = ( lobbyId != 0ull ) ? qtrue : qfalse;
	cl_steamCallbackState.currentLobbyId = lobbyId;
}

/*
=============
CL_Steam_ClearCurrentLobby
=============
*/
static void CL_Steam_ClearCurrentLobby( void ) {
	cl_steamCallbackState.currentLobbyValid = qfalse;
	cl_steamCallbackState.currentLobbyId = 0ull;
}

/*
=============
CL_Steam_FormatFriendSummaryJson

Formats a Steam friend summary into the retained browser-event payload shape.
=============
*/
static void CL_Steam_FormatFriendSummaryJson( const ql_steam_friend_summary_t *summary, char *buffer, size_t bufferSize ) {
	char id[32];
	char lobbyId[32];
	char gameServerId[32];
	char name[QL_STEAM_NAME_LENGTH * 2];
	char nickname[QL_STEAM_NAME_LENGTH * 2];
	char status[QL_STEAM_STATUS_LENGTH * 2];
	char lanIp[128];

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	if ( !summary ) {
		Q_strncpyz( buffer, "{}", bufferSize );
		return;
	}

	CL_Steam_FormatSteamId( summary->steamId.value, id, sizeof( id ) );
	CL_Steam_FormatSteamId( summary->lobbyId.value, lobbyId, sizeof( lobbyId ) );
	CL_Steam_FormatSteamId( summary->gameServerId.value, gameServerId, sizeof( gameServerId ) );
	CL_Steam_JsonEscape( summary->name, name, sizeof( name ) );
	CL_Steam_JsonEscape( summary->nickname, nickname, sizeof( nickname ) );
	CL_Steam_JsonEscape( summary->status, status, sizeof( status ) );
	CL_Steam_JsonEscape( summary->lanIp, lanIp, sizeof( lanIp ) );

	Com_sprintf(
		buffer,
		bufferSize,
		"{\"id\":\"%s\",\"name\":\"%s\",\"nickname\":\"%s\",\"relationship\":%d,\"state\":%d,\"status\":\"%s\",\"lanIp\":\"%s\",\"playingQuake\":%d,\"game\":\"%llu\",\"lobby\":\"%s\",\"ip\":%u,\"port\":%u,\"queryport\":%u,\"server\":\"%s\"}",
		id,
		name,
		nickname,
		summary->relationship,
		summary->personaState,
		status,
		lanIp,
		summary->playingQuake ? 1 : 0,
		(unsigned long long)summary->gameId,
		lobbyId,
		summary->serverIp,
		(unsigned int)summary->serverPort,
		(unsigned int)summary->queryPort,
		gameServerId
	);
}

/*
=============
CL_Steam_Client_OnRichPresenceJoinRequested
=============
*/
static void CL_Steam_Client_OnRichPresenceJoinRequested( void *context, const ql_steam_rich_presence_join_requested_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	CL_Steam_OnRichPresenceJoinRequested( event->command );
}

/*
=============
CL_Steam_Client_OnUserStatsReceived
=============
*/
static void CL_Steam_Client_OnUserStatsReceived( void *context, const ql_steam_user_stats_received_t *event ) {
	char eventName[CL_STEAM_BROWSER_EVENT_NAME_LENGTH];
	char steamId[32];
	char name[QL_STEAM_NAME_LENGTH * 2];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	(void)context;

	if ( !event ) {
		return;
	}

	CL_Steam_FormatSteamId( event->steamId.value, steamId, sizeof( steamId ) );
	CL_Steam_JsonEscape( event->name, name, sizeof( name ) );
	Com_sprintf( eventName, sizeof( eventName ), "users.stats.%s.received", steamId );
	Com_sprintf( payload, sizeof( payload ), "{\"id\":\"%s\",\"name\":\"%s\",\"gameId\":%u,\"result\":%d}", steamId, name, event->gameId, event->result );
	CL_Steam_PublishBrowserEvent( eventName, payload );
}

/*
=============
CL_Steam_Client_OnPersonaStateChange
=============
*/
static void CL_Steam_Client_OnPersonaStateChange( void *context, const ql_steam_persona_state_change_t *event ) {
	char eventName[CL_STEAM_BROWSER_EVENT_NAME_LENGTH];
	char steamId[32];
	char summary[1024];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	(void)context;

	if ( !event ) {
		return;
	}

	CL_Steam_FormatSteamId( event->steamId.value, steamId, sizeof( steamId ) );
	CL_Steam_FormatFriendSummaryJson( &event->summary, summary, sizeof( summary ) );
	Com_sprintf( eventName, sizeof( eventName ), "users.persona.%s.change", steamId );
	Com_sprintf( payload, sizeof( payload ), "{\"changeFlags\":%u,\"friend\":%s}", event->changeFlags, summary );
	CL_Steam_PublishBrowserEvent( eventName, payload );
}

/*
=============
CL_Steam_Client_OnP2PSessionRequest
=============
*/
static void CL_Steam_Client_OnP2PSessionRequest( void *context, const ql_steam_p2p_session_request_t *event ) {
	char detail[96];
	char remoteId[32];

	(void)context;

	if ( !event ) {
		return;
	}

	CL_Steam_FormatSteamId( event->remoteId.value, remoteId, sizeof( remoteId ) );
	if ( !QL_Steamworks_AcceptP2PSession( &event->remoteId ) ) {
		Com_sprintf( detail, sizeof( detail ), "accept failed for %s", remoteId );
		CL_LogMatchmakingCallbackLifecycle( "p2p_session_request", detail );
		return;
	}

	Com_sprintf( detail, sizeof( detail ), "accepted %s", remoteId );
	CL_LogMatchmakingCallbackLifecycle( "p2p_session_request", detail );
}

/*
=============
CL_Steam_Client_OnGameServerChangeRequested
=============
*/
static void CL_Steam_Client_OnGameServerChangeRequested( void *context, const ql_steam_game_server_change_requested_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	CL_Steam_OnGameServerChangeRequested( event->server, event->password );
}

/*
=============
CL_Steam_Client_OnFriendRichPresenceUpdate
=============
*/
static void CL_Steam_Client_OnFriendRichPresenceUpdate( void *context, const ql_steam_friend_rich_presence_update_t *event ) {
	char eventName[CL_STEAM_BROWSER_EVENT_NAME_LENGTH];
	char steamId[32];
	char summary[1024];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	(void)context;

	if ( !event ) {
		return;
	}

	CL_Steam_FormatSteamId( event->steamId.value, steamId, sizeof( steamId ) );
	CL_Steam_FormatFriendSummaryJson( &event->summary, summary, sizeof( summary ) );
	Com_sprintf( eventName, sizeof( eventName ), "users.presence.%s.change", steamId );
	Com_sprintf( payload, sizeof( payload ), "{\"appId\":%u,\"friend\":%s}", event->appId, summary );
	CL_Steam_PublishBrowserEvent( eventName, payload );
}

/*
=============
CL_Steam_Client_OnUGCQueryCompleted
=============
*/
static void CL_Steam_Client_OnUGCQueryCompleted( void *context, const ql_steam_ugc_query_completed_t *event ) {
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];
	const char *eventName;

	(void)context;

	if ( !event ) {
		return;
	}

	eventName = ( event->result == 1 ) ? "web.ugc.results" : "web.ugc.failed";
	Com_sprintf(
		payload,
		sizeof( payload ),
		"{\"call\":\"%llu\",\"query\":\"%llu\",\"result\":%d,\"numResults\":%u,\"total\":%u,\"cached\":%d}",
		(unsigned long long)event->callHandle,
		(unsigned long long)event->queryHandle,
		event->result,
		event->numResultsReturned,
		event->totalMatchingResults,
		event->cachedData ? 1 : 0
	);
	CL_Steam_PublishBrowserEvent( eventName, payload );
}

/*
=============
CL_Steam_Lobby_OnLobbyCreated
=============
*/
static void CL_Steam_Lobby_OnLobbyCreated( void *context, const ql_steam_lobby_created_t *event ) {
	char eventName[CL_STEAM_BROWSER_EVENT_NAME_LENGTH];
	char lobbyId[32];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	(void)context;

	if ( !event ) {
		return;
	}

	CL_Steam_FormatSteamId( event->lobbyId.value, lobbyId, sizeof( lobbyId ) );
	if ( event->result != 1 || event->lobbyId.value == 0ull ) {
		Com_sprintf( payload, sizeof( payload ), "{\"result\":%d,\"id\":\"%s\"}", event->result, lobbyId );
		CL_Steam_PublishBrowserEvent( "lobby.error", payload );
		return;
	}

	Com_sprintf( eventName, sizeof( eventName ), "lobby.%s.create", lobbyId );
	Com_sprintf( payload, sizeof( payload ), "{\"id\":\"%s\",\"result\":%d}", lobbyId, event->result );
	CL_Steam_PublishBrowserEvent( eventName, payload );
}

/*
=============
CL_Steam_Lobby_OnLobbyEnter
=============
*/
static void CL_Steam_Lobby_OnLobbyEnter( void *context, const ql_steam_lobby_enter_t *event ) {
	char eventName[CL_STEAM_BROWSER_EVENT_NAME_LENGTH];
	char lobbyId[32];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	(void)context;

	if ( !event ) {
		return;
	}

	CL_Steam_FormatSteamId( event->lobbyId.value, lobbyId, sizeof( lobbyId ) );
	if ( event->response != 1 || event->lobbyId.value == 0ull ) {
		Com_sprintf( payload, sizeof( payload ), "{\"response\":%d,\"permissions\":%u,\"id\":\"%s\"}", event->response, event->chatPermissions, lobbyId );
		CL_Steam_PublishBrowserEvent( "lobby.error", payload );
		return;
	}

	CL_Steam_SetCurrentLobby( event->lobbyId.value );
	Com_sprintf( eventName, sizeof( eventName ), "lobby.%s.enter", lobbyId );
	Com_sprintf( payload, sizeof( payload ), "{\"id\":\"%s\",\"permissions\":%u,\"locked\":%d,\"response\":%d}", lobbyId, event->chatPermissions, event->locked ? 1 : 0, event->response );
	CL_Steam_PublishBrowserEvent( eventName, payload );
}

/*
=============
CL_Steam_Lobby_OnLobbyChatUpdate
=============
*/
static void CL_Steam_Lobby_OnLobbyChatUpdate( void *context, const ql_steam_lobby_chat_update_t *event ) {
	char eventName[CL_STEAM_BROWSER_EVENT_NAME_LENGTH];
	char lobbyId[32];
	char userId[32];
	char name[QL_STEAM_NAME_LENGTH * 2];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];
	ql_steam_friend_summary_t summary;
	const char *verb;

	(void)context;

	if ( !event ) {
		return;
	}

	memset( &summary, 0, sizeof( summary ) );
	QL_Steamworks_GetFriendSummary( (uint32_t)( event->changedUser.value & 0xffffffffu ), (uint32_t)( event->changedUser.value >> 32 ), &summary );
	CL_Steam_FormatSteamId( event->lobbyId.value, lobbyId, sizeof( lobbyId ) );
	CL_Steam_FormatSteamId( event->changedUser.value, userId, sizeof( userId ) );
	CL_Steam_JsonEscape( summary.name, name, sizeof( name ) );
	verb = ( event->stateChange & 0x01u ) ? "joined" : "left";
	Com_sprintf( eventName, sizeof( eventName ), "lobby.%s.user.%s", lobbyId, verb );
	Com_sprintf( payload, sizeof( payload ), "{\"id\":\"%s\",\"name\":\"%s\",\"stateChange\":%u}", userId, name, event->stateChange );
	CL_Steam_PublishBrowserEvent( eventName, payload );
}

/*
=============
CL_Steam_Lobby_OnLobbyChatMessage
=============
*/
static void CL_Steam_Lobby_OnLobbyChatMessage( void *context, const ql_steam_lobby_chat_message_t *event ) {
	char eventName[CL_STEAM_BROWSER_EVENT_NAME_LENGTH];
	char lobbyId[32];
	char userId[32];
	char name[QL_STEAM_NAME_LENGTH * 2];
	char message[QL_STEAM_LOBBY_MESSAGE_LENGTH * 2];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];
	ql_steam_friend_summary_t summary;

	(void)context;

	if ( !event ) {
		return;
	}

	memset( &summary, 0, sizeof( summary ) );
	QL_Steamworks_GetFriendSummary( (uint32_t)( event->chatter.value & 0xffffffffu ), (uint32_t)( event->chatter.value >> 32 ), &summary );
	CL_Steam_FormatSteamId( event->lobbyId.value, lobbyId, sizeof( lobbyId ) );
	CL_Steam_FormatSteamId( event->chatter.value, userId, sizeof( userId ) );
	CL_Steam_JsonEscape( summary.name, name, sizeof( name ) );
	CL_Steam_JsonEscape( event->message, message, sizeof( message ) );
	Com_sprintf( eventName, sizeof( eventName ), "lobby.%s.chat", lobbyId );
	Com_sprintf( payload, sizeof( payload ), "{\"id\":\"%s\",\"name\":\"%s\",\"msg\":\"%s\",\"type\":%d}", userId, name, message, event->chatEntryType );
	CL_Steam_PublishBrowserEvent( eventName, payload );
}

/*
=============
CL_Steam_Lobby_OnLobbyDataUpdate
=============
*/
static void CL_Steam_Lobby_OnLobbyDataUpdate( void *context, const ql_steam_lobby_data_update_t *event ) {
	char eventName[CL_STEAM_BROWSER_EVENT_NAME_LENGTH];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	(void)context;

	if ( !event ) {
		return;
	}

	Com_sprintf( eventName, sizeof( eventName ), "lobby.%llu.updated", (unsigned long long)event->lobbyId.value );
	Com_sprintf( payload, sizeof( payload ), "{\"id\":\"%llu\",\"member\":\"%llu\",\"success\":%d}", (unsigned long long)event->lobbyId.value, (unsigned long long)event->memberId.value, event->success ? 1 : 0 );
	CL_Steam_PublishBrowserEvent( eventName, payload );
}

/*
=============
CL_Steam_Lobby_OnLobbyGameCreated
=============
*/
static void CL_Steam_Lobby_OnLobbyGameCreated( void *context, const ql_steam_lobby_game_created_t *event ) {
	char eventName[CL_STEAM_BROWSER_EVENT_NAME_LENGTH];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	(void)context;

	if ( !event ) {
		return;
	}

	Com_sprintf( eventName, sizeof( eventName ), "lobby.%llu.game_created", (unsigned long long)event->lobbyId.value );
	Com_sprintf( payload, sizeof( payload ), "{\"id\":\"%llu\",\"ip\":%u,\"port\":%u,\"server\":\"%llu\"}", (unsigned long long)event->lobbyId.value, event->serverIp, (unsigned int)event->serverPort, (unsigned long long)event->serverId.value );
	CL_Steam_PublishBrowserEvent( eventName, payload );
}

/*
=============
CL_Steam_Lobby_OnLobbyKicked
=============
*/
static void CL_Steam_Lobby_OnLobbyKicked( void *context, const ql_steam_lobby_kicked_t *event ) {
	char eventName[CL_STEAM_BROWSER_EVENT_NAME_LENGTH];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	(void)context;

	if ( !event ) {
		return;
	}

	if ( cl_steamCallbackState.currentLobbyValid && cl_steamCallbackState.currentLobbyId == event->lobbyId.value ) {
		CL_Steam_ClearCurrentLobby();
	}

	Com_sprintf( eventName, sizeof( eventName ), "lobby.%llu.kicked", (unsigned long long)event->lobbyId.value );
	Com_sprintf( payload, sizeof( payload ), "{\"id\":\"%llu\",\"admin\":\"%llu\",\"disconnected\":%d}", (unsigned long long)event->lobbyId.value, (unsigned long long)event->adminId.value, event->disconnected ? 1 : 0 );
	CL_Steam_PublishBrowserEvent( eventName, payload );
}

/*
=============
CL_Steam_Lobby_OnGameLobbyJoinRequested
=============
*/
static void CL_Steam_Lobby_OnGameLobbyJoinRequested( void *context, const ql_steam_game_lobby_join_requested_t *event ) {
	char eventName[CL_STEAM_BROWSER_EVENT_NAME_LENGTH];
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	(void)context;

	if ( !event ) {
		return;
	}

	Com_sprintf( eventName, sizeof( eventName ), "lobby.%llu.join_requested", (unsigned long long)event->lobbyId.value );
	Com_sprintf( payload, sizeof( payload ), "{\"id\":\"%llu\",\"friend\":\"%llu\"}", (unsigned long long)event->lobbyId.value, (unsigned long long)event->friendId.value );
	CL_Steam_PublishBrowserEvent( eventName, payload );
}

/*
=============
CL_Steam_Micro_OnAuthorizationResponse
=============
*/
static void CL_Steam_Micro_OnAuthorizationResponse( void *context, const ql_steam_microtxn_authorization_response_t *event ) {
	char payload[CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH];

	(void)context;

	if ( !event ) {
		return;
	}

	Com_sprintf( payload, sizeof( payload ), "{\"appid\":%u,\"orderid\":\"%llu\",\"authorized\":%d}", event->appId, (unsigned long long)event->orderId, event->authorized ? 1 : 0 );
	CL_LogMicroTransactionCallbackLifecycle( event );
	CL_Steam_PublishBrowserEvent( "microtxn.authorization", payload );
}

/*
=============
CL_Steam_Workshop_OnItemInstalled
=============
*/
static void CL_Steam_Workshop_OnItemInstalled( void *context, const ql_steam_item_installed_t *event ) {
	uint32_t appId;
	int itemIndex;
	char detail[128];

	(void)context;

	if ( !event || !cl_steamWorkshopDownloadState.active ) {
		return;
	}

	appId = QL_Steamworks_GetAppID();
	if ( appId != 0u && event->appId != appId ) {
		Com_sprintf( detail, sizeof( detail ), "ignored installed callback for unexpected app id %u", event->appId );
		CL_LogWorkshopLifecycle( "callback-item-installed", detail );
		return;
	}

	itemIndex = CL_Workshop_FindItemIndex( event->itemIdLow, event->itemIdHigh );
	if ( itemIndex < 0 ) {
		return;
	}

	CL_Workshop_FinalizeInstalledItem( itemIndex );
	if ( cl_steamWorkshopDownloadState.activeItemIndex < 0 ) {
		CL_Workshop_AdvanceQueue();
	}
}

/*
=============
CL_Steam_Workshop_OnDownloadItemResult
=============
*/
static void CL_Steam_Workshop_OnDownloadItemResult( void *context, const ql_steam_download_item_result_t *event ) {
	clSteamWorkshopItem_t *item;
	unsigned long long itemId;
	uint32_t appId;
	char detail[128];

	(void)context;

	if ( !event || !cl_steamWorkshopDownloadState.active || cl_steamWorkshopDownloadState.activeItemIndex < 0 ) {
		return;
	}

	appId = QL_Steamworks_GetAppID();
	if ( appId != 0u && event->appId != appId ) {
		Com_sprintf( detail, sizeof( detail ), "ignored download callback for unexpected app id %u", event->appId );
		CL_LogWorkshopLifecycle( "callback-download-result", detail );
		return;
	}

	item = &cl_steamWorkshopDownloadState.items[cl_steamWorkshopDownloadState.activeItemIndex];
	itemId = ( (unsigned long long)event->itemIdHigh << 32 ) | event->itemIdLow;
	if ( item->itemIdLow != event->itemIdLow || item->itemIdHigh != event->itemIdHigh ) {
		Com_sprintf( detail, sizeof( detail ), "ignored download callback for inactive item %llu", itemId );
		CL_LogWorkshopLifecycle( "callback-download-result", detail );
		return;
	}

	if ( event->result == 1 ) {
		CL_Workshop_FinalizeInstalledItem( cl_steamWorkshopDownloadState.activeItemIndex );
		CL_Workshop_AdvanceQueue();
		return;
	}

	CL_Workshop_FailActiveDownload( event->result );
	CL_Workshop_AdvanceQueue();
}

/*
=============
CL_Steam_InitCallbacks
=============
*/
static void CL_Steam_InitCallbacks( void ) {
	ql_steam_client_callback_bindings_t clientBindings;
	ql_steam_lobby_callback_bindings_t lobbyBindings;
	ql_steam_micro_callback_bindings_t microBindings;
	ql_steam_workshop_callback_bindings_t workshopBindings;
	const char *matchmakingProvider;
	const char *matchmakingPolicy;
	const char *statsProvider;
	const char *statsPolicy;
	const char *workshopProvider;
	const char *workshopPolicy;

	cl_steamCallbackState.callbackRegistrationActive = qfalse;
	CL_Steam_ClearCurrentLobby();
	CL_Steam_ClearBrowserEvents();
	CL_RefreshPlatformServiceCvars();
	matchmakingProvider = CL_GetMatchmakingServiceProviderLabel();
	matchmakingPolicy = CL_GetMatchmakingServicePolicyLabel();
	statsProvider = CL_GetStatsServiceProviderLabel();
	statsPolicy = CL_GetStatsServicePolicyLabel();
	workshopProvider = CL_GetWorkshopServiceProviderLabel();
	workshopPolicy = CL_GetWorkshopServicePolicyLabel();
	if ( !CL_SteamServicesEnabled() ) {
		Com_DPrintf( "Client callback bundle unavailable for matchmaking=%s [%s], stats=%s [%s]; keeping compatibility-only browser event fallback\n",
			matchmakingProvider, matchmakingPolicy, statsProvider, statsPolicy );
		return;
	}

	memset( &clientBindings, 0, sizeof( clientBindings ) );
	clientBindings.onRichPresenceJoinRequested = CL_Steam_Client_OnRichPresenceJoinRequested;
	clientBindings.onUserStatsReceived = CL_Steam_Client_OnUserStatsReceived;
	clientBindings.onPersonaStateChange = CL_Steam_Client_OnPersonaStateChange;
	clientBindings.onP2PSessionRequest = CL_Steam_Client_OnP2PSessionRequest;
	clientBindings.onGameServerChangeRequested = CL_Steam_Client_OnGameServerChangeRequested;
	clientBindings.onFriendRichPresenceUpdate = CL_Steam_Client_OnFriendRichPresenceUpdate;
	clientBindings.onUGCQueryCompleted = CL_Steam_Client_OnUGCQueryCompleted;

	memset( &lobbyBindings, 0, sizeof( lobbyBindings ) );
	lobbyBindings.onLobbyCreated = CL_Steam_Lobby_OnLobbyCreated;
	lobbyBindings.onLobbyEnter = CL_Steam_Lobby_OnLobbyEnter;
	lobbyBindings.onLobbyChatUpdate = CL_Steam_Lobby_OnLobbyChatUpdate;
	lobbyBindings.onLobbyChatMessage = CL_Steam_Lobby_OnLobbyChatMessage;
	lobbyBindings.onLobbyDataUpdate = CL_Steam_Lobby_OnLobbyDataUpdate;
	lobbyBindings.onLobbyGameCreated = CL_Steam_Lobby_OnLobbyGameCreated;
	lobbyBindings.onLobbyKicked = CL_Steam_Lobby_OnLobbyKicked;
	lobbyBindings.onGameLobbyJoinRequested = CL_Steam_Lobby_OnGameLobbyJoinRequested;

	memset( &microBindings, 0, sizeof( microBindings ) );
	microBindings.onAuthorizationResponse = CL_Steam_Micro_OnAuthorizationResponse;

	memset( &workshopBindings, 0, sizeof( workshopBindings ) );
	workshopBindings.onItemInstalled = CL_Steam_Workshop_OnItemInstalled;
	workshopBindings.onDownloadItemResult = CL_Steam_Workshop_OnDownloadItemResult;

	if ( !QL_Steamworks_RegisterClientCallbacks( &clientBindings ) ||
		!QL_Steamworks_RegisterLobbyCallbacks( &lobbyBindings ) ||
		!QL_Steamworks_RegisterMicroCallbacks( &microBindings ) ) {
		Com_DPrintf( "Client callback bundle unavailable for matchmaking=%s [%s], stats=%s [%s]; keeping compatibility-only browser event fallback\n",
			matchmakingProvider, matchmakingPolicy, statsProvider, statsPolicy );
		QL_Steamworks_UnregisterMicroCallbacks();
		QL_Steamworks_UnregisterLobbyCallbacks();
		QL_Steamworks_UnregisterClientCallbacks();
		return;
	}

	if ( !QL_Steamworks_RegisterWorkshopCallbacks( &workshopBindings ) ) {
		Com_DPrintf( "Workshop callbacks unavailable for %s [%s]; keeping polling fallback\n",
			workshopProvider, workshopPolicy );
	}

	cl_steamCallbackState.callbackRegistrationActive = qtrue;
}

/*
=============
CL_Steam_ShutdownCallbacks
=============
*/
static void CL_Steam_ShutdownCallbacks( void ) {
	QL_Steamworks_UnregisterWorkshopCallbacks();
	QL_Steamworks_UnregisterMicroCallbacks();
	QL_Steamworks_UnregisterLobbyCallbacks();
	QL_Steamworks_UnregisterClientCallbacks();
	cl_steamCallbackState.callbackRegistrationActive = qfalse;
	CL_Steam_ClearCurrentLobby();
	CL_Steam_ClearBrowserEvents();
}

/*
=============
CL_Steam_Frame
=============
*/
static void CL_Steam_Frame( void ) {
	if ( !cl_steamCallbackState.callbackRegistrationActive ) {
		return;
	}

	QL_Steamworks_RunCallbacks();
	CL_Steam_SendVoicePacket();
	CL_Steam_ProcessVoicePackets();
}

/*
=============
CL_Steam_ShouldRegisterStatsClear
=============
*/
static qboolean CL_Steam_ShouldRegisterStatsClear( void ) {
	if ( !CL_SteamServicesEnabled() ) {
		CL_LogStatsServiceRegistrationSkipped( "stats provider unavailable" );
		return qfalse;
	}

	if ( !QL_Steamworks_Init() ) {
		CL_LogStatsServiceRegistrationSkipped( "stats provider initialisation failed" );
		return qfalse;
	}

	if ( QL_Steamworks_GetAppID() != 0x54100u ) {
		CL_LogStatsServiceRegistrationSkipped( "stats_clear unsupported for current app id" );
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_Steam_ConnectLobby_f

Mirrors the retail connect_lobby handler by storing the requested Steam lobby
ID into lobby_autoconnect.
=============
*/
static void CL_Steam_ConnectLobby_f( void ) {
	if ( Cmd_Argc() < 2 ) {
		CL_LogMatchmakingServiceIgnored( "connect_lobby", "missing lobby id" );
		return;
	}

	if ( !CL_SteamServicesEnabled() ) {
		CL_LogMatchmakingServiceIgnored( "connect_lobby", "matchmaking provider unavailable" );
	}

	Cvar_Set( "lobby_autoconnect", Cmd_Argv( 1 ) );
}

/*
=============
CL_Steam_SetMainMenuRichPresence

Seeds the retail main-menu Steam rich-presence value during client bootstrap.
=============
*/
static void CL_Steam_SetMainMenuRichPresence( void ) {
	if ( !CL_SteamServicesEnabled() ) {
		CL_LogMatchmakingServiceIgnored( "steam_presence_main_menu", "matchmaking provider unavailable" );
		return;
	}

	if ( !QL_Steamworks_SetRichPresence( "status", "At the main menu" ) ) {
		CL_LogMatchmakingServiceIgnored( "steam_presence_main_menu", "rich presence update failed" );
	}
}

/*
=============
CL_Steam_SyncPersonaNameCvar

Mirrors the retail Steam persona bootstrap and respects the retail com_build harness gate.
=============
*/
static void CL_Steam_SyncPersonaNameCvar( void ) {
	char personaName[MAX_CVAR_VALUE_STRING];

	if ( !CL_SteamServicesEnabled() ) {
		CL_LogIdentityBootstrapFallback( "steam_persona_name", "identity bootstrap provider unavailable" );
		return;
	}

	if ( com_buildScript && com_buildScript->integer ) {
		return;
	}

	if ( !QL_Steamworks_Init() ) {
		CL_LogIdentityBootstrapFallback( "steam_persona_name", "identity bootstrap initialisation failed" );
		return;
	}

	if ( QL_Steamworks_GetPersonaName( personaName, sizeof( personaName ) ) ) {
		Cvar_Set( "name", personaName );
		return;
	}

	CL_LogIdentityBootstrapFallback( "steam_persona_name", "persona unavailable; falling back to anon" );
	Cvar_Set( "name", "anon" );
}

/*
=============
CL_Steam_SeedCountryCvar

Seeds the country userinfo field from Steam when the current cvar is blank.
=============
*/
static void CL_Steam_SeedCountryCvar( void ) {
	char country[MAX_CVAR_VALUE_STRING];

	if ( !CL_SteamServicesEnabled() ) {
		CL_LogIdentityBootstrapFallback( "steam_country_seed", "identity bootstrap provider unavailable" );
		return;
	}

	Cvar_VariableStringBuffer( "country", country, sizeof( country ) );
	if ( country[0] ) {
		return;
	}

	if ( !QL_Steamworks_Init() ) {
		CL_LogIdentityBootstrapFallback( "steam_country_seed", "identity bootstrap initialisation failed" );
		return;
	}

	if ( QL_Steamworks_GetIPCountry( country, sizeof( country ) ) && country[0] ) {
		Cvar_Set( "country", country );
		return;
	}

	CL_LogIdentityBootstrapFallback( "steam_country_seed", "country seed unavailable" );
}

/*
===============
CL_CDDialog

Called by Com_Error when a cd is needed
===============
*/
void CL_CDDialog( void ) {
	cls.cddialog = qtrue;	// start it next frame
}


/*
=======================================================================

CLIENT RELIABLE COMMAND COMMUNICATION

=======================================================================
*/

/*
======================
CL_AddReliableCommand

The given command will be transmitted to the server, and is gauranteed to
not have future usercmd_t executed before it is executed
======================
*/
void CL_AddReliableCommand( const char *cmd ) {
	int		index;

	// if we would be losing an old command that hasn't been acknowledged,
	// we must drop the connection
	if ( clc.reliableSequence - clc.reliableAcknowledge > MAX_RELIABLE_COMMANDS ) {
		Com_Error( ERR_DROP, "Client command overflow" );
	}
	clc.reliableSequence++;
	index = clc.reliableSequence & ( MAX_RELIABLE_COMMANDS - 1 );
	Q_strncpyz( clc.reliableCommands[ index ], cmd, sizeof( clc.reliableCommands[ index ] ) );
}

/*
======================
CL_ChangeReliableCommand
======================
*/
void CL_ChangeReliableCommand( void ) {
	int r, index, l;

	r = clc.reliableSequence - (random() * 5);
	index = clc.reliableSequence & ( MAX_RELIABLE_COMMANDS - 1 );
	l = strlen(clc.reliableCommands[ index ]);
	if ( l >= MAX_STRING_CHARS - 1 ) {
		l = MAX_STRING_CHARS - 2;
	}
	clc.reliableCommands[ index ][ l ] = '\n';
	clc.reliableCommands[ index ][ l+1 ] = '\0';
}

/*
=======================================================================

CLIENT SIDE DEMO RECORDING

=======================================================================
*/

/*
====================
CL_WriteDemoMessage

Dumps the current net message, prefixed by the length
====================
*/
void CL_WriteDemoMessage ( msg_t *msg, int headerBytes ) {
	int		len, swlen;

	// write the packet sequence
	len = clc.serverMessageSequence;
	swlen = LittleLong( len );
	FS_Write (&swlen, 4, clc.demofile);

	// skip the packet sequencing information
	len = msg->cursize - headerBytes;
	swlen = LittleLong(len);
	FS_Write (&swlen, 4, clc.demofile);
	FS_Write ( msg->data + headerBytes, len, clc.demofile );
	
	if ( cl_demoRecordMessage->integer >= 2 ) {
		Com_DPrintf( "demo: wrote %i bytes from server seq %i\n", len, clc.serverMessageSequence );
	}
}


/*
====================
CL_StopRecording_f

stop recording a demo
====================
*/
void CL_StopRecord_f( void ) {
	int		len;

	if ( !clc.demorecording ) {
		Com_Printf ("Not recording a demo.\n");
		return;
	}

	// finish up
	len = -1;
	FS_Write (&len, 4, clc.demofile);
	FS_Write (&len, 4, clc.demofile);
	FS_FCloseFile (clc.demofile);
	clc.demofile = 0;
	clc.demorecording = qfalse;
	clc.spDemoRecording = qfalse;
	if ( clc.demoName[0] ) {
		CL_WebView_PublishGameDemo( clc.demoName, clc.demoName );
	}
	Com_Printf ("Stopped demo.\n");
}

/* 
================== 
CL_DemoFilename
================== 
*/  
void CL_DemoFilename( int number, char *fileName ) {
	int		a,b,c,d;

	if ( number < 0 || number > 9999 ) {
		Com_sprintf( fileName, MAX_OSPATH, "demo9999.tga" );
		return;
	}

	a = number / 1000;
	number -= a*1000;
	b = number / 100;
	number -= b*100;
	c = number / 10;
	number -= c*10;
	d = number;

	Com_sprintf( fileName, MAX_OSPATH, "demo%i%i%i%i"
		, a, b, c, d );
}

/*
====================
CL_Record_f

record <demoname>

Begins recording a demo from the current position
====================
*/
static char		demoName[MAX_QPATH];	// compiler bug workaround
void CL_Record_f( void ) {
	char		name[MAX_OSPATH];
	byte		bufData[MAX_MSGLEN];
	msg_t	buf;
	int			i;
	int			len;
	entityState_t	*ent;
	entityState_t	nullstate;
	char		*s;

	if ( Cmd_Argc() > 2 ) {
		Com_Printf ("Correct usage: record <demoname>\n");
		return;
	}

	if ( clc.demorecording ) {
		Com_Printf ("Already recording.\n");
		CL_StopRecord_f();
		if ( clc.demorecording ) {
			Com_Error( ERR_FATAL, "stoprecord failed" );
		}
	}

	if ( cls.state != CA_ACTIVE ) {
		Com_Printf ("You must be in a level to record.\n");
		return;
	}

	if ( Cmd_Argc() == 2 ) {
		s = Cmd_Argv(1);
		Q_strncpyz( demoName, s, sizeof( demoName ) );
		Com_sprintf (name, sizeof(name), "demos/%s.dm_%d", demoName, PROTOCOL_VERSION );
	} else {
		int		number;

		// scan for a free demo name
		for ( number = 0 ; number <= 9999 ; number++ ) {
			CL_DemoFilename( number, demoName );
			Com_sprintf (name, sizeof(name), "demos/%s.dm_%d", demoName, PROTOCOL_VERSION );

			len = FS_ReadFile( name, NULL );
			if ( len <= 0 ) {
				break;	// file doesn't exist
			}
		}
	}

	// open the demo file

	Com_Printf ("recording to %s.\n", name);
	clc.demofile = FS_FOpenFileWrite( name );
	if ( !clc.demofile ) {
		Com_Printf ("ERROR: couldn't open.\n");
		return;
	}
	clc.demorecording = qtrue;
	if (Cvar_VariableValue("ui_recordSPDemo")) {
	  clc.spDemoRecording = qtrue;
	} else {
	  clc.spDemoRecording = qfalse;
	}


	Q_strncpyz( clc.demoName, demoName, sizeof( clc.demoName ) );

	// don't start saving messages until a non-delta compressed message is received
	clc.demowaiting = qtrue;

	// write out the gamestate message
	MSG_Init (&buf, bufData, sizeof(bufData));
	MSG_Bitstream(&buf);

	// NOTE, MRE: all server->client messages now acknowledge
	MSG_WriteLong( &buf, clc.reliableSequence );

	MSG_WriteByte (&buf, svc_gamestate);
	MSG_WriteLong (&buf, clc.serverCommandSequence );

	// configstrings
	for ( i = 0 ; i < MAX_CONFIGSTRINGS ; i++ ) {
		if ( !cl.gameState.stringOffsets[i] ) {
			continue;
		}
		s = cl.gameState.stringData + cl.gameState.stringOffsets[i];
		MSG_WriteByte (&buf, svc_configstring);
		MSG_WriteShort (&buf, i);
		MSG_WriteBigString (&buf, s);
	}

	// baselines
	Com_Memset (&nullstate, 0, sizeof(nullstate));
	for ( i = 0; i < MAX_GENTITIES ; i++ ) {
		ent = &cl.entityBaselines[i];
		if ( !ent->number ) {
			continue;
		}
		MSG_WriteByte (&buf, svc_baseline);		
		MSG_WriteDeltaEntity (&buf, &nullstate, ent, qtrue );
	}

	MSG_WriteByte( &buf, svc_EOF );
	
	// finished writing the gamestate stuff

	// write the client num
	MSG_WriteLong(&buf, clc.clientNum);
	// write the checksum feed
	MSG_WriteLong(&buf, clc.checksumFeed);

	// finished writing the client packet
	MSG_WriteByte( &buf, svc_EOF );

	// write it to the demo file
	len = LittleLong( clc.serverMessageSequence - 1 );
	FS_Write (&len, 4, clc.demofile);

	len = LittleLong (buf.cursize);
	FS_Write (&len, 4, clc.demofile);
	FS_Write (buf.data, buf.cursize, clc.demofile);

	// the rest of the demo file will be copied from net messages
}

/*
=======================================================================

CLIENT SIDE DEMO PLAYBACK

=======================================================================
*/

/*
=================
CL_DemoCompleted
=================
*/
void CL_DemoCompleted( void ) {
	if (cl_timedemo && cl_timedemo->integer) {
		int	time;
		
		time = Sys_Milliseconds() - clc.timeDemoStart;
		if ( time > 0 ) {
			Com_Printf ("%i frames, %3.1f seconds: %3.1f fps\n", clc.timeDemoFrames,
			time/1000.0, clc.timeDemoFrames*1000.0 / time);
		}
	}

	CL_Disconnect( qtrue );
	CL_NextDemo();
}

/*
=================
CL_ReadDemoMessage
=================
*/
void CL_ReadDemoMessage( void ) {
	int			r;
	msg_t		buf;
	byte		bufData[ MAX_MSGLEN ];
	int			s;

	if ( !clc.demofile ) {
		CL_DemoCompleted ();
		return;
	}

	// get the sequence number
	r = FS_Read( &s, 4, clc.demofile);
	if ( r != 4 ) {
		CL_DemoCompleted ();
		return;
	}
	clc.serverMessageSequence = LittleLong( s );

	// init the message
	MSG_Init( &buf, bufData, sizeof( bufData ) );

	// get the length
	r = FS_Read (&buf.cursize, 4, clc.demofile);
	if ( r != 4 ) {
		CL_DemoCompleted ();
		return;
	}
	buf.cursize = LittleLong( buf.cursize );
	if ( buf.cursize == -1 ) {
		CL_DemoCompleted ();
		return;
	}
	if ( buf.cursize > buf.maxsize ) {
		Com_Error (ERR_DROP, "CL_ReadDemoMessage: demoMsglen > MAX_MSGLEN");
	}
	r = FS_Read( buf.data, buf.cursize, clc.demofile );
	if ( r != buf.cursize ) {
		Com_Printf( "Demo file was truncated.\n");
		CL_DemoCompleted ();
		return;
	}

	clc.lastPacketTime = cls.realtime;
	buf.readcount = 0;
	CL_ParseServerMessage( &buf );
}

/*
====================
CL_WalkDemoExt
====================
*/
static void CL_WalkDemoExt(char *arg, char *name, int *demofile)
{
	int i = 0;
	*demofile = 0;
	while(demo_protocols[i])
	{
		Com_sprintf (name, MAX_OSPATH, "demos/%s.dm_%d", arg, demo_protocols[i]);
		FS_FOpenFileRead( name, demofile, qtrue );
		if (*demofile)
		{
			Com_Printf("Demo file: %s\n", name);
			break;
		}
		else
			Com_Printf("Not found: %s\n", name);
		i++;
	}
}

/*
====================
CL_PlayDemo_f

demo <demoname>

====================
*/
void CL_PlayDemo_f( void ) {
	char		name[MAX_OSPATH];
	char		*arg, *ext_test;
	int			protocol, i;
	char		retry[MAX_OSPATH];

	if (Cmd_Argc() != 2) {
		Com_Printf ("playdemo <demoname>\n");
		return;
	}

	SV_Shutdown( "Starting Demo.\n" );
	CL_Disconnect( qfalse );

	// open the demo file
	arg = Cmd_Argv(1);
	
	// check for an extension .dm_?? (?? is protocol)
	ext_test = arg + strlen(arg) - 6;
	if ((strlen(arg) > 6) && (ext_test[0] == '.') && ((ext_test[1] == 'd') || (ext_test[1] == 'D')) && ((ext_test[2] == 'm') || (ext_test[2] == 'M')) && (ext_test[3] == '_'))
	{
		protocol = atoi(ext_test+4);
		i=0;
		while(demo_protocols[i])
		{
			if (demo_protocols[i] == protocol)
				break;
			i++;
		}
		if (demo_protocols[i])
		{
			Com_sprintf (name, sizeof(name), "demos/%s", arg);
			FS_FOpenFileRead( name, &clc.demofile, qtrue );
		} else {
			Com_Printf("Protocol %d not supported for demos\n", protocol);
			Q_strncpyz(retry, arg, sizeof(retry));
			retry[strlen(retry)-6] = 0;
			CL_WalkDemoExt( retry, name, &clc.demofile );
		}
	} else {
		CL_WalkDemoExt( arg, name, &clc.demofile );
	}
	
	if (!clc.demofile) {
		Com_Error( ERR_DROP, "couldn't open %s", name);
		return;
	}
	Q_strncpyz( clc.demoName, Cmd_Argv(1), sizeof( clc.demoName ) );

	Con_Close();

	cls.state = CA_CONNECTED;
	clc.demoplaying = qtrue;
	Q_strncpyz( cls.servername, Cmd_Argv(1), sizeof( cls.servername ) );

	// read demo messages until connected
	while ( cls.state >= CA_CONNECTED && cls.state < CA_PRIMED ) {
		CL_ReadDemoMessage();
	}
	// don't get the first snapshot this frame, to prevent the long
	// time from the gamestate load from messing causing a time skip
	clc.firstDemoFrameSkipped = qfalse;
}


/*
====================
CL_StartDemoLoop

Closing the main menu will restart the demo loop
====================
*/
void CL_StartDemoLoop( void ) {
	// start the demo loop again
	Cbuf_AddText ("d1\n");
	cls.keyCatchers = 0;
}

/*
==================
CL_NextDemo

Called when a demo or cinematic finishes
If the "nextdemo" cvar is set, that command will be issued
==================
*/
void CL_NextDemo( void ) {
	char	v[MAX_STRING_CHARS];

	Q_strncpyz( v, Cvar_VariableString ("nextdemo"), sizeof(v) );
	v[MAX_STRING_CHARS-1] = 0;
	Com_DPrintf("CL_NextDemo: %s\n", v );
	if (!v[0]) {
		return;
	}

	Cvar_Set ("nextdemo","");
	Cbuf_AddText (v);
	Cbuf_AddText ("\n");
	Cbuf_Execute();
}


//======================================================================

/*
=====================
CL_ShutdownAll
=====================
*/
void CL_ShutdownAll(void) {

	// clear sounds
	S_DisableSounds();
	// shutdown CGame
	CL_ShutdownCGame();
	// shutdown UI
	CL_ShutdownUI();

	// shutdown the renderer
	if ( re.Shutdown ) {
		re.Shutdown( qfalse );		// don't destroy window or context
	}

	cls.uiStarted = qfalse;
	cls.cgameStarted = qfalse;
	cls.rendererStarted = qfalse;
	cls.soundRegistered = qfalse;
}

/*
=================
CL_FlushMemory

Called by CL_MapLoading, CL_Connect_f, CL_PlayDemo_f, and CL_ParseGamestate the only
ways a client gets into a game
Also called by Com_Error
=================
*/
void CL_FlushMemory( void ) {

	// shutdown all the client stuff
	CL_ShutdownAll();

	// if not running a server clear the whole hunk
	if ( !com_sv_running->integer ) {
		// clear the whole hunk
		Hunk_Clear();
		// clear collision map data
		CM_ClearMap();
	}
	else {
		// clear all the client data on the hunk
		Hunk_ClearToMark();
	}

	CL_StartHunkUsers();
}

/*
=====================
CL_MapLoading

A local server is starting to load a map, so update the
screen to let the user know about it, then dump all client
memory on the hunk from cgame, ui, and renderer
=====================
*/
void CL_MapLoading( void ) {
	if ( !com_cl_running->integer ) {
		return;
	}

	Con_Close();
	cls.keyCatchers = 0;

	// if we are already connected to the local host, stay connected
	if ( cls.state >= CA_CONNECTED && !Q_stricmp( cls.servername, "localhost" ) ) {
		cls.state = CA_CONNECTED;		// so the connect screen is drawn
		Com_Memset( cls.updateInfoString, 0, sizeof( cls.updateInfoString ) );
		Com_Memset( clc.serverMessage, 0, sizeof( clc.serverMessage ) );
		Com_Memset( &cl.gameState, 0, sizeof( cl.gameState ) );
		clc.lastPacketSentTime = -9999;
		SCR_UpdateScreen();
	} else {
		// clear nextmap so the cinematic shutdown doesn't execute it
		Cvar_Set( "nextmap", "" );
		CL_Disconnect( qtrue );
		Q_strncpyz( cls.servername, "localhost", sizeof(cls.servername) );
		cls.state = CA_CHALLENGING;		// so the connect screen is drawn
		cls.keyCatchers = 0;
		SCR_UpdateScreen();
		clc.connectTime = -RETRANSMIT_TIMEOUT;
		NET_StringToAdr( cls.servername, &clc.serverAddress);
		// we don't need a challenge on the localhost

		CL_CheckForResend();
	}
}

/*
=====================
CL_ClearState

Called before parsing a gamestate
=====================
*/
void CL_ClearState (void) {

//	S_StopAllSounds();

	Com_Memset( &cl, 0, sizeof( cl ) );
}


/*
=====================
CL_Disconnect

Called when a connection, demo, or cinematic is being terminated.
Goes from a connected state to either a menu state or a console state
Sends a disconnect message to the server
This is also called on Com_Error and Com_Quit, so it shouldn't cause any errors
=====================
*/
void CL_Disconnect( qboolean showMainMenu ) {
	qboolean publishGameEnd;

	if ( !com_cl_running || !com_cl_running->integer ) {
		return;
	}

	publishGameEnd = ( cls.state >= CA_CONNECTED || clc.demoplaying || clc.demorecording ) ? qtrue : qfalse;

	// shutting down the client so enter full screen ui mode
	Cvar_Set("r_uiFullScreen", "1");

	if ( clc.demorecording ) {
		CL_StopRecord_f ();
	}

	QL_ClientAuth_CancelSteamTicket();
	if ( publishGameEnd ) {
		CL_WebView_PublishGameEnd();
	}

	if (clc.download) {
		FS_FCloseFile( clc.download );
		clc.download = 0;
	}
	*clc.downloadTempName = *clc.downloadName = 0;
	CL_Workshop_ClearBootstrapState( qtrue );

	if ( clc.demofile ) {
		FS_FCloseFile( clc.demofile );
		clc.demofile = 0;
	}

	if ( uivm && showMainMenu ) {
		VM_Call( uivm, UI_SET_ACTIVE_MENU, UIMENU_NONE );
	}

	SCR_StopCinematic ();
	S_ClearSoundBuffer();

	// send a disconnect message to the server
	// send it a few times in case one is dropped
	if ( cls.state >= CA_CONNECTED ) {
		CL_AddReliableCommand( "disconnect" );
		CL_WritePacket();
		CL_WritePacket();
		CL_WritePacket();
	}

	cl_voiceRecordingActive = qfalse;
	if ( CL_SteamServicesEnabled() ) {
		QL_Steamworks_StopVoiceRecording();
	}
	
	CL_ClearState ();

	// wipe the client connection
	Com_Memset( &clc, 0, sizeof( clc ) );

	cls.state = CA_DISCONNECTED;

	// allow cheats locally
	Cvar_Set( "sv_cheats", "1" );

	// not connected to a pure server anymore
	cl_connectedToPureServer = qfalse;
}


/*
===================
CL_ForwardCommandToServer

adds the current command line as a clientCommand
things like godmode, noclip, etc, are commands directed to the server,
so when they are typed in at the console, they will need to be forwarded.
===================
*/
void CL_ForwardCommandToServer( const char *string ) {
	char	*cmd;

	cmd = Cmd_Argv(0);

	// ignore key up commands
	if ( cmd[0] == '-' ) {
		return;
	}

	if ( clc.demoplaying || cls.state < CA_CONNECTED || cmd[0] == '+' ) {
		Com_Printf ("Unknown command \"%s\"\n", cmd);
		return;
	}

	if ( Cmd_Argc() > 1 ) {
		CL_AddReliableCommand( string );
	} else {
		CL_AddReliableCommand( cmd );
	}
}

/*
===================
CL_RequestMotd

===================
*/
void CL_RequestMotd( void ) {
	char		info[MAX_INFO_STRING];

	if ( !cl_motd->integer ) {
		return;
	}
	Com_Printf( "Resolving %s\n", UPDATE_SERVER_NAME );
	if ( !NET_StringToAdr( UPDATE_SERVER_NAME, &cls.updateServer  ) ) {
		Com_Printf( "Couldn't resolve address\n" );
		return;
	}
	cls.updateServer.port = BigShort( PORT_UPDATE );
	Com_Printf( "%s resolved to %i.%i.%i.%i:%i\n", UPDATE_SERVER_NAME,
		cls.updateServer.ip[0], cls.updateServer.ip[1],
		cls.updateServer.ip[2], cls.updateServer.ip[3],
		BigShort( cls.updateServer.port ) );
	
	info[0] = 0;
  // NOTE TTimo xoring against Com_Milliseconds, otherwise we may not have a true randomization
  // only srand I could catch before here is tr_noise.c l:26 srand(1001)
  // https://zerowing.idsoftware.com/bugzilla/show_bug.cgi?id=382
  // NOTE: the Com_Milliseconds xoring only affects the lower 16-bit word,
  //   but I decided it was enough randomization
	Com_sprintf( cls.updateChallenge, sizeof( cls.updateChallenge ), "%i", ((rand() << 16) ^ rand()) ^ Com_Milliseconds());

	Info_SetValueForKey( info, "challenge", cls.updateChallenge );
	Info_SetValueForKey( info, "renderer", cls.glconfig.renderer_string );
	Info_SetValueForKey( info, "version", com_version->string );

	NET_OutOfBandPrint( NS_CLIENT, cls.updateServer, "getmotd \"%s\"\n", info );
}

/*
===================
CL_RequestAuthorization

Authorization server protocol
-----------------------------

All commands are text in Q3 out of band packets (leading 0xff 0xff 0xff 0xff).

Whenever the client tries to get a challenge from the server it wants to
connect to, it also blindly fires off a packet to the authorize server:

getKeyAuthorize <challenge> <cdkey>

cdkey may be "demo"


#OLD The authorize server returns a:
#OLD 
#OLD keyAthorize <challenge> <accept | deny>
#OLD 
#OLD A client will be accepted if the cdkey is valid and it has not been used by any other IP
#OLD address in the last 15 minutes.


The server sends a:

getIpAuthorize <challenge> <ip>

The authorize server returns a:

ipAuthorize <challenge> <accept | deny | demo | unknown >

A client will be accepted if a valid cdkey was sent by that ip (only) in the last 15 minutes.
If no response is received from the authorize server after two tries, the client will be let
in anyway.
===================
*/
void CL_RequestAuthorization( void ) {
	char	authorizePayload[64];
	ql_auth_credential_t	credential;

	authorizePayload[0] = '\0';

	if ( !cls.authorizeServer.port ) {
		Com_Printf( "Resolving %s\n", AUTHORIZE_SERVER_NAME );
		if ( !NET_StringToAdr( AUTHORIZE_SERVER_NAME, &cls.authorizeServer  ) ) {
			Com_Printf( "Couldn't resolve address\n" );
			return;
		}

		cls.authorizeServer.port = BigShort( PORT_AUTHORIZE );
		Com_Printf( "%s resolved to %i.%i.%i.%i:%i\n", AUTHORIZE_SERVER_NAME,
			cls.authorizeServer.ip[0], cls.authorizeServer.ip[1],
			cls.authorizeServer.ip[2], cls.authorizeServer.ip[3],
			BigShort( cls.authorizeServer.port ) );
	}
	if ( cls.authorizeServer.type == NA_BAD ) {
		return;
	}

	if ( QL_ParseCredentialString( cl_cdkey, &credential ) ) {
		QL_FormatCredentialForAuthorize( &credential, authorizePayload, sizeof( authorizePayload ) );
	}

	NET_OutOfBandPrint(NS_CLIENT, cls.authorizeServer,
		va("getKeyAuthorize %i %s", Cvar_VariableIntegerValue( "cl_anonymous" ), authorizePayload) );
}

/*
======================================================================

CONSOLE COMMANDS

======================================================================
*/

/*
==================
CL_CommandContainsUserinfoToken

Retail cmd forwarding refuses to relay userinfo through the generic client command path.
==================
*/
static qboolean CL_CommandContainsUserinfoToken( const char *commandName ) {
	const char	*cursor;

	if ( !commandName || !commandName[0] ) {
		return qfalse;
	}

	for ( cursor = commandName; *cursor; cursor++ ) {
		if ( !Q_stricmpn( cursor, "userinfo", 8 ) ) {
			return qtrue;
		}
	}

	return qfalse;
}

/*
==================
CL_ForwardToServer_f
==================
*/
void CL_ForwardToServer_f( void ) {
	if ( cls.state != CA_ACTIVE || clc.demoplaying ) {
		Com_Printf ("Not connected to a server.\n");
		return;
	}
	
	// don't forward the first argument
	if ( Cmd_Argc() > 1 && !CL_CommandContainsUserinfoToken( Cmd_Argv( 1 ) ) ) {
		CL_AddReliableCommand( Cmd_Args() );
	}
}

/*
==================
CL_Setenv_f

Mostly for controlling voodoo environment variables
==================
*/
void CL_Setenv_f( void ) {
	int argc = Cmd_Argc();

	if ( argc > 2 ) {
		char buffer[1024];
		int i;

		strcpy( buffer, Cmd_Argv(1) );
		strcat( buffer, "=" );

		for ( i = 2; i < argc; i++ ) {
			strcat( buffer, Cmd_Argv( i ) );
			strcat( buffer, " " );
		}

		putenv( buffer );
	} else if ( argc == 2 ) {
		char *env = getenv( Cmd_Argv(1) );

		if ( env ) {
			Com_Printf( "%s=%s\n", Cmd_Argv(1), env );
		} else {
			Com_Printf( "%s undefined\n", Cmd_Argv(1), env );
		}
	}
}


/*
==================
CL_Disconnect_f
==================
*/
void CL_Disconnect_f( void ) {
	SCR_StopCinematic();
	Cvar_Set("ui_singlePlayerActive", "0");
	if ( cls.state != CA_DISCONNECTED && cls.state != CA_CINEMATIC ) {
		Com_Error (ERR_DISCONNECT, "Disconnected from server");
	}
}


/*
================
CL_Reconnect_f

================
*/
void CL_Reconnect_f( void ) {
	if ( !strlen( cls.servername ) || !strcmp( cls.servername, "localhost" ) ) {
		Com_Printf( "Can't reconnect to localhost.\n" );
		return;
	}
	Cvar_Set("ui_singlePlayerActive", "0");
	Cbuf_AddText( va("connect %s\n", cls.servername ) );
}

/*
================
CL_Connect_f

================
*/
void CL_Connect_f( void ) {
	char	*server;

	if ( Cmd_Argc() != 2 ) {
		Com_Printf( "usage: connect [server]\n");
		return;	
	}

	Cvar_Set("ui_singlePlayerActive", "0");

	// fire a message off to the motd server
	CL_RequestMotd();

	// clear any previous "server full" type messages
	clc.serverMessage[0] = 0;

	server = Cmd_Argv (1);

	if ( com_sv_running->integer && !strcmp( server, "localhost" ) ) {
		// if running a local server, kill it
		SV_Shutdown( "Server quit\n" );
	}

	// make sure a local server is killed
	Cvar_Set( "sv_killserver", "1" );
	SV_Frame( 0 );

	CL_Disconnect( qtrue );
	Con_Close();

	/* MrE: 2000-09-13: now called in CL_DownloadsComplete
	CL_FlushMemory( );
	*/

	Q_strncpyz( cls.servername, server, sizeof(cls.servername) );

	if (!NET_StringToAdr( cls.servername, &clc.serverAddress) ) {
		Com_Printf ("Bad server address\n");
		cls.state = CA_DISCONNECTED;
		return;
	}
	if (clc.serverAddress.port == 0) {
		clc.serverAddress.port = BigShort( PORT_SERVER );
	}
	Com_Printf( "%s resolved to %i.%i.%i.%i:%i\n", cls.servername,
		clc.serverAddress.ip[0], clc.serverAddress.ip[1],
		clc.serverAddress.ip[2], clc.serverAddress.ip[3],
		BigShort( clc.serverAddress.port ) );

	// if we aren't playing on a lan, we need to authenticate
	// with the cd key
	if ( NET_IsLocalAddress( clc.serverAddress ) ) {
		cls.state = CA_CHALLENGING;
	} else {
		cls.state = CA_CONNECTING;
	}

	cls.keyCatchers = 0;
	clc.connectTime = -99999;	// CL_CheckForResend() will fire immediately
	clc.connectPacketCount = 0;

	// server connection string
	Cvar_Set( "cl_currentServerAddress", server );
}


/*
=====================
CL_Rcon_f

  Send the rest of the command line over as
  an unconnected command.
=====================
*/
void CL_Rcon_f( void ) {
	char	message[1024];
	netadr_t	to;

	if ( !rcon_client_password->string ) {
		Com_Printf ("You must set 'rconpassword' before\n"
					"issuing an rcon command.\n");
		return;
	}

	message[0] = -1;
	message[1] = -1;
	message[2] = -1;
	message[3] = -1;
	message[4] = 0;

	strcat (message, "rcon ");

	strcat (message, rcon_client_password->string);
	strcat (message, " ");

	// https://zerowing.idsoftware.com/bugzilla/show_bug.cgi?id=543
	strcat (message, Cmd_Cmd()+5);

	if ( cls.state >= CA_CONNECTED ) {
		to = clc.netchan.remoteAddress;
	} else {
		if (!strlen(rconAddress->string)) {
			Com_Printf ("You must either be connected,\n"
						"or set the 'rconAddress' cvar\n"
						"to issue rcon commands\n");

			return;
		}
		NET_StringToAdr (rconAddress->string, &to);
		if (to.port == 0) {
			to.port = BigShort (PORT_SERVER);
		}
	}
	
	NET_SendPacket (NS_CLIENT, strlen(message)+1, message, to);
}

/*
=================
CL_SendPureChecksums
=================
*/
void CL_SendPureChecksums( void ) {
	const char *pChecksums;
	char cMsg[MAX_INFO_VALUE];
	int binChecksum;
	int i;

	// if we are pure we need to send back a command with our referenced pk3 checksums
	pChecksums = FS_ReferencedPakPureChecksums();
	if ( FS_FileIsInPAK( "cgamex86.dll", &binChecksum ) != 1 ) {
		Com_Error( ERR_FATAL, "CL_SendPureChecksums: no pak file for binaries" );
	}

	// "cp"
	// "Yf"
	Com_sprintf(cMsg, sizeof(cMsg), "Yf ");
	Q_strcat(cMsg, sizeof(cMsg), va("%d %d ", cl.serverId, binChecksum) );
	Q_strcat(cMsg, sizeof(cMsg), pChecksums);
	for (i = 0; i < 2; i++) {
		cMsg[i] += 10;
	}
	CL_AddReliableCommand( cMsg );
}

/*
=================
CL_ResetPureClientAtServer
=================
*/
void CL_ResetPureClientAtServer( void ) {
	CL_AddReliableCommand( va("vdr") );
}

/*
=================
CL_Vid_Restart_f

Restart the video subsystem

we also have to reload the UI and CGame because the renderer
doesn't know what graphics to reload
=================
*/
void CL_Vid_Restart_f( void ) {
#ifdef _WIN32
	if ( !Cvar_VariableIntegerValue( "r_noFastRestart" ) && Cmd_Argc() > 1 && !Q_stricmp( Cmd_Argv( 1 ), "fast" ) ) {
		float consoleScale;
		int vidWidth;
		int vidHeight;
		qboolean fullscreen;

		if ( WIN_FastVidRestart( &vidWidth, &vidHeight, &fullscreen ) ) {
			cls.glconfig.vidWidth = vidWidth;
			cls.glconfig.vidHeight = vidHeight;
			cls.glconfig.isFullscreen = fullscreen;
			consoleScale = Com_Clamp( 0.5f, 1.0f, Cvar_VariableValue( "con_scale" ) );
			if ( consoleScale <= 0.0f ) {
				consoleScale = 0.5f;
			}
			g_console_field_width = (int)( (float)cls.glconfig.vidWidth / ( consoleScale * 12.0f ) - 2.0f );
			g_consoleField.widthInChars = g_console_field_width;
			Cbuf_AddText( "postprocess_restart\n" );
			if ( cgvm ) {
				VM_Call( cgvm, CG_EVENT_HANDLING, CGAME_EVENT_REFRESH_DISPLAY_CONTEXT );
			}
			if ( uivm ) {
				VM_Call( uivm, UI_REFRESH_DISPLAY_CONTEXT );
			}
			return;
		}
	}
#endif

	// don't let them loop during the restart
	S_StopAllSounds();
	// shutdown the UI
	CL_ShutdownUI();
	// shutdown the CGame
	CL_ShutdownCGame();
	// shutdown the renderer and clear the renderer interface
	CL_ShutdownRef();
	// client is no longer pure untill new checksums are sent
	CL_ResetPureClientAtServer();
	// clear pak references
	FS_ClearPakReferences( FS_UI_REF | FS_CGAME_REF );
	// reinitialize the filesystem if the game directory or checksum has changed
	FS_ConditionalRestart( clc.checksumFeed );

	cls.rendererStarted = qfalse;
	cls.uiStarted = qfalse;
	cls.cgameStarted = qfalse;
	cls.soundRegistered = qfalse;

	// unpause so the cgame definately gets a snapshot and renders a frame
	Cvar_Set( "cl_paused", "0" );

	// if not running a server clear the whole hunk
	if ( !com_sv_running->integer ) {
		// clear the whole hunk
		Hunk_Clear();
	}
	else {
		// clear all the client data on the hunk
		Hunk_ClearToMark();
	}

	// initialize the renderer interface
	CL_InitRef();

	// startup all the client stuff
	CL_StartHunkUsers();

	// start the cgame if connected
	if ( cls.state > CA_CONNECTED && cls.state != CA_CINEMATIC ) {
		cls.cgameStarted = qtrue;
		CL_InitCGame();
		// send pure checksums
		CL_SendPureChecksums();
	}
}

/*
=================
CL_PostProcessRestart_f

Invokes the renderer-owned post-process restart hook exported through GetRefAPI.
=================
*/
static void CL_PostProcessRestart_f( void ) {
	if ( !re.PostProcessRestart ) {
		return;
	}

	re.PostProcessRestart();
}

/*
=================
CL_Snd_Restart_f

Restart the sound subsystem
The cgame and game must also be forced to restart because
handles will be invalid
=================
*/
void CL_Snd_Restart_f( void ) {
	S_Shutdown();
	S_Init();

	CL_Vid_Restart_f();
}


/*
==================
CL_PK3List_f
==================
*/
void CL_OpenedPK3List_f( void ) {
	Com_Printf("Opened PK3 Names: %s\n", FS_LoadedPakNames());
}

/*
==================
CL_PureList_f
==================
*/
void CL_ReferencedPK3List_f( void ) {
	Com_Printf("Referenced PK3 Names: %s\n", FS_ReferencedPakNames());
}

/*
==================
CL_Configstrings_f
==================
*/
void CL_Configstrings_f( void ) {
	int		i;
	int		ofs;

	if ( cls.state != CA_ACTIVE ) {
		Com_Printf( "Not connected to a server.\n");
		return;
	}

	for ( i = 0 ; i < MAX_CONFIGSTRINGS ; i++ ) {
		ofs = cl.gameState.stringOffsets[ i ];
		if ( !ofs ) {
			continue;
		}
		Com_Printf( "%4i: %s\n", i, cl.gameState.stringData + ofs );
	}
}

/*
==============
CL_Clientinfo_f
==============
*/
void CL_Clientinfo_f( void ) {
	Com_Printf( "--------- Client Information ---------\n" );
	Com_Printf( "state: %i\n", cls.state );
	Com_Printf( "Server: %s\n", cls.servername );
	Com_Printf ("User info settings:\n");
	Info_Print( Cvar_InfoString( CVAR_USERINFO ) );
	Com_Printf( "--------------------------------------\n" );
}

/*
==================
CL_Userinfo_f

Retail reserves the userinfo command name with a no-op owner.
==================
*/
static void CL_Userinfo_f( void ) {
}


//====================================================================

/*
=================
CL_DownloadsComplete

Called when all downloading has been completed
=================
*/
void CL_DownloadsComplete( void ) {

	// if we downloaded files we need to restart the file system
	if (clc.downloadRestart) {
		clc.downloadRestart = qfalse;

		FS_Restart(clc.checksumFeed); // We possibly downloaded a pak, restart the file system to load it

		// inform the server so we get new gamestate info
		CL_AddReliableCommand( "donedl" );

		// by sending the donedl command we request a new gamestate
		// so we don't want to load stuff yet
		return;
	}

	// let the client game init and load data
	cls.state = CA_LOADING;

	// Pump the loop, this may change gamestate!
	Com_EventLoop();

	// if the gamestate was changed by calling Com_EventLoop
	// then we loaded everything already and we don't want to do it again.
	if ( cls.state != CA_LOADING ) {
		return;
	}

	// starting to load a map so we get out of full screen ui mode
	Cvar_Set("r_uiFullScreen", "0");

	// flush client memory and start loading stuff
	// this will also (re)load the UI
	// if this is a local client then only the client part of the hunk
	// will be cleared, note that this is done after the hunk mark has been set
	CL_FlushMemory();

	// initialize the CGame
	cls.cgameStarted = qtrue;
	CL_InitCGame();

	// set pure checksums
	CL_SendPureChecksums();

	CL_WritePacket();
	CL_WritePacket();
	CL_WritePacket();
}

/*
=================
CL_Workshop_Frame

Mirrors the retail workshop/download completion helper called from CL_Frame.
=================
*/
static void CL_Workshop_Frame( void ) {
	char missingfiles[2048];

	if ( !cl_steamWorkshopDownloadState.active ) {
		return;
	}

	if ( !CL_Workshop_DownloadsSettled() ) {
		return;
	}

	if ( cl_steamWorkshopDownloadState.downloadsRequested ) {
		CL_LogWorkshopLifecycle( "filesystem-restart", "downloads complete; restarting filesystem" );
		FS_Restart( clc.checksumFeed );
		cl_steamWorkshopDownloadState.downloadsRequested = qfalse;
		return;
	}

	if ( FS_ComparePaks( missingfiles, sizeof( missingfiles ), qfalse ) ) {
		Com_Printf( "\nWARNING: You are missing some files referenced by the server:\n%s"
			"You might not be able to join the game\n"
			"Go to the setting menu to turn on autodownload, or get the file elsewhere\n\n", missingfiles );
	}

	CL_Workshop_ClearBootstrapState( qtrue );
	CL_DownloadsComplete();
}

/*
=================
CL_BeginDownload

Requests a file to download from the server.  Stores it in the current
game directory.
=================
*/
void CL_BeginDownload( const char *localName, const char *remoteName ) {

	Com_DPrintf("***** CL_BeginDownload *****\n"
				"Localname: %s\n"
				"Remotename: %s\n"
				"****************************\n", localName, remoteName);

	Q_strncpyz ( clc.downloadName, localName, sizeof(clc.downloadName) );
	Com_sprintf( clc.downloadTempName, sizeof(clc.downloadTempName), "%s.tmp", localName );

	// Set so UI gets access to it
	Cvar_Set( "cl_downloadName", remoteName );
	Cvar_Set( "cl_downloadSize", "0" );
	Cvar_Set( "cl_downloadCount", "0" );
	Cvar_SetValue( "cl_downloadTime", cls.realtime );

	clc.downloadBlock = 0; // Starting new file
	clc.downloadCount = 0;

	CL_AddReliableCommand( va("download %s", remoteName) );
}

/*
=================
CL_NextDownload

A download completed or failed
=================
*/
void CL_NextDownload(void) {
	char *s;
	char *remoteName, *localName;

	// We are looking to start a download here
	if (*clc.downloadList) {
		s = clc.downloadList;

		// format is:
		//  @remotename@localname@remotename@localname, etc.

		if (*s == '@')
			s++;
		remoteName = s;
		
		if ( (s = strchr(s, '@')) == NULL ) {
			CL_DownloadsComplete();
			return;
		}

		*s++ = 0;
		localName = s;
		if ( (s = strchr(s, '@')) != NULL )
			*s++ = 0;
		else
			s = localName + strlen(localName); // point at the nul byte

		CL_BeginDownload( localName, remoteName );

		clc.downloadRestart = qtrue;

		// move over the rest
		memmove( clc.downloadList, s, strlen(s) + 1);

		return;
	}

	CL_DownloadsComplete();
}

/*
=================
CL_InitDownloads

After receiving a valid game state, we valid the cgame and local zip files here
and determine if we need to download them
=================
*/
void CL_InitDownloads(void) {
	char missingfiles[1024];

	CL_Workshop_ClearBootstrapState( qtrue );
	if ( CL_Workshop_BeginBootstrap() ) {
		return;
	}

	if ( !cl_allowDownload->integer )
	{
		// autodownload is disabled on the client
		// but it's possible that some referenced files on the server are missing
		if (FS_ComparePaks( missingfiles, sizeof( missingfiles ), qfalse ) )
		{      
			// NOTE TTimo I would rather have that printed as a modal message box
			//   but at this point while joining the game we don't know wether we will successfully join or not
			Com_Printf( "\nWARNING: You are missing some files referenced by the server:\n%s"
					"You might not be able to join the game\n"
					"Go to the setting menu to turn on autodownload, or get the file elsewhere\n\n", missingfiles );
		}
	}
	else if ( FS_ComparePaks( clc.downloadList, sizeof( clc.downloadList ) , qtrue ) ) {

		Com_Printf("Need paks: %s\n", clc.downloadList );

		if ( *clc.downloadList ) {
			// if autodownloading is not enabled on the server
			cls.state = CA_CONNECTED;
			CL_NextDownload();
			return;
		}

	}
		
	CL_DownloadsComplete();
}

/*
=================
CL_CheckForResend

Resend a connect message if the last one has timed out
=================
*/
void CL_CheckForResend( void ) {
	int		port, i;
	char	info[MAX_INFO_STRING];
	char	data[MAX_INFO_STRING];

	// don't send anything if playing back a demo
	if ( clc.demoplaying ) {
		return;
	}

	// resend if we haven't gotten a reply yet
	if ( cls.state != CA_CONNECTING && cls.state != CA_CHALLENGING ) {
		return;
	}

	if ( cls.realtime - clc.connectTime < RETRANSMIT_TIMEOUT ) {
		return;
	}

	clc.connectTime = cls.realtime;	// for retransmit requests
	clc.connectPacketCount++;


	switch ( cls.state ) {
	case CA_CONNECTING:
		// requesting a challenge
		if ( !Sys_IsLANAddress( clc.serverAddress ) ) {
			CL_RequestAuthorization();
		}
		NET_OutOfBandPrint(NS_CLIENT, clc.serverAddress, "getchallenge");
		break;
		
	case CA_CHALLENGING:
		// sending back the challenge
		port = Cvar_VariableValue ("net_qport");

		Q_strncpyz( info, Cvar_InfoString( CVAR_USERINFO ), sizeof( info ) );
		Info_SetValueForKey( info, "protocol", va("%i", PROTOCOL_VERSION ) );
		Info_SetValueForKey( info, "qport", va("%i", port ) );
		Info_SetValueForKey( info, "challenge", va("%i", clc.challenge ) );
		
		strcpy(data, "connect ");
    // TTimo adding " " around the userinfo string to avoid truncated userinfo on the server
    //   (Com_TokenizeString tokenizes around spaces)
    data[8] = '"';

		for(i=0;i<strlen(info);i++) {
			data[9+i] = info[i];	// + (clc.challenge)&0x3;
		}
    data[9+i] = '"';
		data[10+i] = 0;

    // NOTE TTimo don't forget to set the right data length!
		NET_OutOfBandData( NS_CLIENT, clc.serverAddress, &data[0], i+10 );
		// the most current userinfo has been sent, so watch for any
		// newer changes to userinfo variables
		cvar_modifiedFlags &= ~CVAR_USERINFO;
		break;

	default:
		Com_Error( ERR_FATAL, "CL_CheckForResend: bad cls.state" );
	}
}

/*
===================
CL_DisconnectPacket

Sometimes the server can drop the client and the netchan based
disconnect can be lost.  If the client continues to send packets
to the server, the server will send out of band disconnect packets
to the client so it doesn't have to wait for the full timeout period.
===================
*/
void CL_DisconnectPacket( netadr_t from ) {
	if ( cls.state < CA_AUTHORIZING ) {
		return;
	}

	// if not from our server, ignore it
	if ( !NET_CompareAdr( from, clc.netchan.remoteAddress ) ) {
		return;
	}

	// if we have received packets within three seconds, ignore it
	// (it might be a malicious spoof)
	if ( cls.realtime - clc.lastPacketTime < 3000 ) {
		return;
	}

	// drop the connection
	Com_Printf( "Server disconnected for unknown reason\n" );
	Cvar_Set("com_errorMessage", "Server disconnected for unknown reason\n" );
	CL_Disconnect( qtrue );
}


/*
===================
CL_MotdPacket

===================
*/
void CL_MotdPacket( netadr_t from ) {
	char	*challenge;
	char	*info;

	// if not from our server, ignore it
	if ( !NET_CompareAdr( from, cls.updateServer ) ) {
		return;
	}

	info = Cmd_Argv(1);

	// check challenge
	challenge = Info_ValueForKey( info, "challenge" );
	if ( strcmp( challenge, cls.updateChallenge ) ) {
		return;
	}

	challenge = Info_ValueForKey( info, "motd" );

	Q_strncpyz( cls.updateInfoString, info, sizeof( cls.updateInfoString ) );
	Cvar_Set( "cl_motdString", challenge );
}

/*
===================
CL_InitServerInfo
===================
*/
void CL_InitServerInfo( serverInfo_t *server, serverAddress_t *address ) {
	server->adr.type  = NA_IP;
	server->adr.ip[0] = address->ip[0];
	server->adr.ip[1] = address->ip[1];
	server->adr.ip[2] = address->ip[2];
	server->adr.ip[3] = address->ip[3];
	server->adr.port  = address->port;
	server->clients = 0;
	server->hostName[0] = '\0';
	server->mapName[0] = '\0';
	server->maxClients = 0;
	server->maxPing = 0;
	server->minPing = 0;
	server->ping = -1;
	server->game[0] = '\0';
	server->gameType = 0;
	server->netType = 0;
}

#define MAX_SERVERSPERPACKET	256

/*
===================
CL_ServersResponsePacket
===================
*/
void CL_ServersResponsePacket( netadr_t from, msg_t *msg ) {
	int				i, count, max, total;
	serverAddress_t addresses[MAX_SERVERSPERPACKET];
	int				numservers;
	byte*			buffptr;
	byte*			buffend;
	
	Com_Printf("CL_ServersResponsePacket\n");

	if (cls.numglobalservers == -1) {
		// state to detect lack of servers or lack of response
		cls.numglobalservers = 0;
		cls.numGlobalServerAddresses = 0;
	}

	if (cls.nummplayerservers == -1) {
		cls.nummplayerservers = 0;
	}

	// parse through server response string
	numservers = 0;
	buffptr    = msg->data;
	buffend    = buffptr + msg->cursize;
	while (buffptr+1 < buffend) {
		// advance to initial token
		do {
			if (*buffptr++ == '\\')
				break;		
		}
		while (buffptr < buffend);

		if ( buffptr >= buffend - 6 ) {
			break;
		}

		// parse out ip
		addresses[numservers].ip[0] = *buffptr++;
		addresses[numservers].ip[1] = *buffptr++;
		addresses[numservers].ip[2] = *buffptr++;
		addresses[numservers].ip[3] = *buffptr++;

		// parse out port
		addresses[numservers].port = (*buffptr++)<<8;
		addresses[numservers].port += *buffptr++;
		addresses[numservers].port = BigShort( addresses[numservers].port );

		// syntax check
		if (*buffptr != '\\') {
			break;
		}

		Com_DPrintf( "server: %d ip: %d.%d.%d.%d:%d\n",numservers,
				addresses[numservers].ip[0],
				addresses[numservers].ip[1],
				addresses[numservers].ip[2],
				addresses[numservers].ip[3],
				addresses[numservers].port );

		numservers++;
		if (numservers >= MAX_SERVERSPERPACKET) {
			break;
		}

		// parse out EOT
		if (buffptr[1] == 'E' && buffptr[2] == 'O' && buffptr[3] == 'T') {
			break;
		}
	}

	if (cls.masterNum == 0) {
		count = cls.numglobalservers;
		max = MAX_GLOBAL_SERVERS;
	} else {
		count = cls.nummplayerservers;
		max = MAX_OTHER_SERVERS;
	}

	for (i = 0; i < numservers && count < max; i++) {
		// build net address
		serverInfo_t *server = (cls.masterNum == 0) ? &cls.globalServers[count] : &cls.mplayerServers[count];

		CL_InitServerInfo( server, &addresses[i] );
		// advance to next slot
		count++;
	}

	// if getting the global list
	if (cls.masterNum == 0) {
		if ( cls.numGlobalServerAddresses < MAX_GLOBAL_SERVERS ) {
			// if we couldn't store the servers in the main list anymore
			for (; i < numservers && count >= max; i++) {
				serverAddress_t *addr;
				// just store the addresses in an additional list
				addr = &cls.globalServerAddresses[cls.numGlobalServerAddresses++];
				addr->ip[0] = addresses[i].ip[0];
				addr->ip[1] = addresses[i].ip[1];
				addr->ip[2] = addresses[i].ip[2];
				addr->ip[3] = addresses[i].ip[3];
				addr->port  = addresses[i].port;
			}
		}
	}

	if (cls.masterNum == 0) {
		cls.numglobalservers = count;
		total = count + cls.numGlobalServerAddresses;
	} else {
		cls.nummplayerservers = count;
		total = count;
	}

	Com_Printf("%d servers parsed (total %d)\n", numservers, total);
}

/*
=================
CL_ConnectionlessPacket

Responses to broadcasts, etc
=================
*/
void CL_ConnectionlessPacket( netadr_t from, msg_t *msg ) {
	char	*s;
	char	*c;

	MSG_BeginReadingOOB( msg );
	MSG_ReadLong( msg );	// skip the -1

	s = MSG_ReadStringLine( msg );

	Cmd_TokenizeString( s );

	c = Cmd_Argv(0);

	Com_DPrintf ("CL packet %s: %s\n", NET_AdrToString(from), c);

	// challenge from the server we are connecting to
	if ( !Q_stricmp(c, "challengeResponse") ) {
		if ( cls.state != CA_CONNECTING ) {
			Com_Printf( "Unwanted challenge response received.  Ignored.\n" );
		} else {
			// start sending challenge repsonse instead of challenge request packets
			clc.challenge = atoi(Cmd_Argv(1));
			cls.state = CA_CHALLENGING;
			clc.connectPacketCount = 0;
			clc.connectTime = -99999;

			// take this address as the new server address.  This allows
			// a server proxy to hand off connections to multiple servers
			clc.serverAddress = from;
			Com_DPrintf ("challengeResponse: %d\n", clc.challenge);
		}
		return;
	}

	// server connection
	if ( !Q_stricmp(c, "connectResponse") ) {
		if ( cls.state >= CA_CONNECTED ) {
			Com_Printf ("Dup connect received.  Ignored.\n");
			return;
		}
		if ( cls.state != CA_CHALLENGING ) {
			Com_Printf ("connectResponse packet while not connecting.  Ignored.\n");
			return;
		}
		if ( !NET_CompareBaseAdr( from, clc.serverAddress ) ) {
			Com_Printf( "connectResponse from a different address.  Ignored.\n" );
			Com_Printf( "%s should have been %s\n", NET_AdrToString( from ), 
				NET_AdrToString( clc.serverAddress ) );
			return;
		}
		Netchan_Setup (NS_CLIENT, &clc.netchan, from, Cvar_VariableValue( "net_qport" ) );
		cls.state = CA_CONNECTED;
		clc.lastPacketSentTime = -9999;		// send first packet immediately
		return;
	}

	// server responding to an info broadcast
	if ( !Q_stricmp(c, "infoResponse") ) {
		CL_ServerInfoPacket( from, msg );
		return;
	}

	// server responding to a get playerlist
	if ( !Q_stricmp(c, "statusResponse") ) {
		CL_ServerStatusResponse( from, msg );
		return;
	}

	// a disconnect message from the server, which will happen if the server
	// dropped the connection but it is still getting packets from us
	if (!Q_stricmp(c, "disconnect")) {
		CL_DisconnectPacket( from );
		return;
	}

	// echo request from server
	if ( !Q_stricmp(c, "echo") ) {
		NET_OutOfBandPrint( NS_CLIENT, from, "%s", Cmd_Argv(1) );
		return;
	}

	// cd check
	if ( !Q_stricmp(c, "keyAuthorize") ) {
		// we don't use these now, so dump them on the floor
		return;
	}

	// global MOTD from id
	if ( !Q_stricmp(c, "motd") ) {
		CL_MotdPacket( from );
		return;
	}
	
	// echo request from server
	if ( !Q_stricmp(c, "print") ) {
		s = MSG_ReadString( msg );
		if ( CL_ShouldFilterConsoleText( s ) ) {
			return;
		}
		Q_strncpyz( clc.serverMessage, s, sizeof( clc.serverMessage ) );
		Com_Printf( "%s", s );
		return;
	}
	
	// echo request from server
	if ( !Q_strncmp(c, "getserversResponse", 18) ) {
		CL_ServersResponsePacket( from, msg );
		return;
	}

	Com_DPrintf ("Unknown connectionless packet command.\n");
}


/*
=================
CL_PacketEvent

A packet has arrived from the main event loop
=================
*/
void CL_PacketEvent( netadr_t from, msg_t *msg ) {
	int		headerBytes;

	clc.lastPacketTime = cls.realtime;

	if ( msg->cursize >= 4 && *(int *)msg->data == -1 ) {
		CL_ConnectionlessPacket( from, msg );
		return;
	}

	if ( cls.state < CA_CONNECTED ) {
		return;		// can't be a valid sequenced packet
	}

	if ( msg->cursize < 4 ) {
		Com_Printf ("%s: Runt packet\n",NET_AdrToString( from ));
		return;
	}

	//
	// packet from server
	//
	if ( !NET_CompareAdr( from, clc.netchan.remoteAddress ) ) {
		Com_DPrintf ("%s:sequenced packet without connection\n"
			,NET_AdrToString( from ) );
		// FIXME: send a client disconnect?
		return;
	}

	if (!CL_Netchan_Process( &clc.netchan, msg) ) {
		return;		// out of order, duplicated, etc
	}

	// the header is different lengths for reliable and unreliable messages
	headerBytes = msg->readcount;

	// track the last message received so it can be returned in 
	// client messages, allowing the server to detect a dropped
	// gamestate
	clc.serverMessageSequence = LittleLong( *(int *)msg->data );

	clc.lastPacketTime = cls.realtime;
	CL_ParseServerMessage( msg );

	//
	// we don't know if it is ok to save a demo message until
	// after we have parsed the frame
	//
	if ( clc.demorecording && !clc.demowaiting ) {
		CL_WriteDemoMessage( msg, headerBytes );
	}
}

/*
==================
CL_CheckTimeout

==================
*/
void CL_CheckTimeout( void ) {
	//
	// check timeout
	//
	if ( ( !cl_paused->integer || !sv_paused->integer ) 
		&& cls.state >= CA_CONNECTED && cls.state != CA_CINEMATIC
	    && cls.realtime - clc.lastPacketTime > cl_timeout->value*1000) {
		if (++cl.timeoutcount > 5) {	// timeoutcount saves debugger
			Com_Printf ("\nServer connection timed out.\n");
			CL_Disconnect( qtrue );
			return;
		}
	} else {
		cl.timeoutcount = 0;
	}
}


//============================================================================

/*
==================
CL_CheckUserinfo

==================
*/
void CL_CheckUserinfo( void ) {
	// don't add reliable commands when not yet connected
	if ( cls.state < CA_CHALLENGING ) {
		return;
	}
	// don't overflow the reliable command buffer when paused
	if ( cl_paused->integer ) {
		return;
	}
	// send a reliable userinfo update if needed
	if ( cvar_modifiedFlags & CVAR_USERINFO ) {
		cvar_modifiedFlags &= ~CVAR_USERINFO;
		CL_AddReliableCommand( va("userinfo \"%s\"", Cvar_InfoString( CVAR_USERINFO ) ) );
	}

}

/*
==================
CL_Frame

==================
*/
void CL_Frame ( int msec ) {
	if ( !com_cl_running->integer ) {
		return;
	}

	if ( cls.cddialog ) {
		// bring up the cd error dialog if needed
		cls.cddialog = qfalse;
		VM_Call( uivm, UI_SET_ACTIVE_MENU, UIMENU_NEED_CD );
	} else	if ( cls.state == CA_DISCONNECTED
		&& !com_sv_running->integer ) {
		if ( !( cls.keyCatchers & KEYCATCH_UI ) ) {
			// if disconnected, bring up the menu
			S_StopAllSounds();
			VM_Call( uivm, UI_SET_ACTIVE_MENU, UIMENU_MAIN );
		}
	}

	// retail QL can defer avidemo activation until demo time reaches the configured start point
	if ( cl_avidemo_latch->integer ) {
		if ( !cl_avidemo_mintime->integer || cl.serverTime > cl_avidemo_mintime->integer ) {
			Cvar_SetValue( "cl_avidemo", cl_avidemo_latch->integer );
			Cvar_Set( "cl_avidemo_latch", "0" );
		}
	}

	// if recording an avi, lock to a fixed fps
	if ( cl_avidemo->integer && msec) {
		// save the current screen
		if ( cls.state == CA_ACTIVE || cl_forceavidemo->integer) {
			if ( cl_avidemo_maxtime->integer && cl.serverTime > cl_avidemo_maxtime->integer ) {
				CL_Disconnect_f();
				return;
			}
			if ( !cl_avidemo_mintime->integer || cl.serverTime >= cl_avidemo_mintime->integer ) {
				Cbuf_ExecuteText( EXEC_NOW, "screenshot silent\n" );
			}
		}
		// fixed time for next frame'
		msec = (1000 / cl_avidemo->integer) * com_timescale->value;
		if (msec == 0) {
			msec = 1;
		}
	}
	
	// save the msec before checking pause
	cls.realFrametime = msec;

	// decide the simulation time
	cls.frametime = msec;

	cls.realtime += cls.frametime;

	if ( cl_timegraph->integer ) {
		SCR_DebugGraph ( cls.realFrametime * 0.25, 0 );
	}

	// see if we need to update any userinfo
	CL_CheckUserinfo();

	// if we haven't gotten a packet in a long time,
	// drop the connection
	CL_CheckTimeout();

	// send intentions now
	CL_SendCmd();

	CL_Steam_Frame();
	CL_Workshop_Frame();
	CL_WebHost_Frame();

	// resend a connection request if necessary
	CL_CheckForResend();

	// decide on the serverTime to render
	CL_SetCGameTime();

	// update the screen
	SCR_UpdateScreen();

	// update audio
	S_Update();

	// advance local effects for next frame
	SCR_RunCinematic();

	Con_RunConsole();

	cls.framecount++;
}


//============================================================================

/*
================
CL_RefPrintf

DLL glue
================
*/
void QDECL CL_RefPrintf( int print_level, const char *fmt, ...) {
	va_list		argptr;
	char		msg[MAXPRINTMSG];
	
	va_start (argptr,fmt);
	Q_vsnprintf (msg, sizeof(msg), fmt, argptr);
	va_end (argptr);

	if ( print_level == PRINT_ALL ) {
		Com_Printf ("%s", msg);
	} else if ( print_level == PRINT_WARNING ) {
		Com_Printf (S_COLOR_YELLOW "%s", msg);		// yellow
	} else if ( print_level == PRINT_DEVELOPER ) {
		Com_DPrintf (S_COLOR_RED "%s", msg);		// red
	}
}



/*
============
CL_ShutdownRef
============
*/
void CL_ShutdownRef( void ) {
	if ( !re.Shutdown ) {
		return;
	}
	re.Shutdown( qtrue );
	Com_Memset( &re, 0, sizeof( re ) );
}

/*
============
CL_InitRenderer
============
*/
void CL_InitRenderer( void ) {
	// this sets up the renderer and calls R_Init
	re.BeginRegistration( &cls.glconfig );

	// load character sets
	cls.charSetShader = re.RegisterShaderNoMip( "gfx/2d/bigchars" );
	if ( !cls.charSetShader ) {
		cls.charSetShader = re.RegisterShaderNoMip( "gfx/2d/bigchars.png" );
	}
	if ( !cls.charSetShader ) {
		cls.charSetShader = re.RegisterShaderNoMip( "gfx/2d/bigchars.tga" );
	}
	if ( cls.charSetShader ) {
		Com_Printf( "CL_InitRenderer: loaded charSetShader handle %d\n", cls.charSetShader );
	} else {
		Com_Printf( S_COLOR_YELLOW "WARNING: CL_InitRenderer failed to register charSetShader.\n" );
	}
	cls.whiteShader = re.RegisterShader( "white" );
	cls.consoleShader = re.RegisterShaderNoMip( "console" );
	if ( !cls.consoleShader ) {
		cls.consoleShader = re.RegisterShaderNoMip( "textures/effects2/console01.png" );
	}
	if ( !cls.consoleShader ) {
		cls.consoleShader = re.RegisterShaderNoMip( "textures/effects2/console01.tga" );
	}
	if ( cls.consoleShader ) {
		Com_Printf( "CL_InitRenderer: loaded consoleShader handle %d\n", cls.consoleShader );
	} else {
		Com_Printf( S_COLOR_YELLOW "WARNING: CL_InitRenderer failed to register consoleShader.\n" );
	}
	{
		float consoleScale;

		consoleScale = Com_Clamp( 0.5f, 1.0f, Cvar_VariableValue( "con_scale" ) );
		if ( consoleScale <= 0.0f ) {
			consoleScale = 0.5f;
		}
		g_console_field_width = (int)( (float)cls.glconfig.vidWidth / ( consoleScale * 12.0f ) - 2.0f );
	}
	g_consoleField.widthInChars = g_console_field_width;
}

/*
============================
CL_StartHunkUsers

After the server has cleared the hunk, these will need to be restarted
This is the only place that any of these functions are called from
============================
*/
void CL_StartHunkUsers( void ) {
	if (!com_cl_running) {
		return;
	}

	if ( !com_cl_running->integer ) {
		return;
	}

	if ( !cls.rendererStarted ) {
		cls.rendererStarted = qtrue;
		CL_InitRenderer();
	}

	if ( !cls.soundStarted ) {
		cls.soundStarted = qtrue;
		S_Init();
	}

	if ( !cls.soundRegistered ) {
		cls.soundRegistered = qtrue;
		S_BeginRegistration();
	}

	if ( !cls.uiStarted ) {
		cls.uiStarted = qtrue;
		CL_InitUI();
	}
}

/*
============
CL_RefMalloc
============
*/
void *CL_RefMalloc( int size ) {
	return Z_TagMalloc( size, TAG_RENDERER );
}

int CL_ScaledMilliseconds(void) {
	return Sys_Milliseconds()*com_timescale->value;
}

/*
============
CL_RegisterFont

Keeps source-era font registration on a compatibility lane outside the retail renderer ABI tail.
============
*/
void CL_RegisterFont( const char *fontName, int pointSize, fontInfo_t *font ) {
	RE_RegisterFont( fontName, pointSize, font );
}

/*
============
CL_RegisterShaderFromRGBA

Keeps direct renderer image creation for live RGBA payloads on an explicit
client compatibility lane outside the retail renderer export ABI.
============
*/
qhandle_t CL_RegisterShaderFromRGBA( const char *name, const byte *pic, int width, int height, qboolean mipRawImage ) {
	image_t *image;

	if ( !name || !pic || width <= 0 || height <= 0 || strlen( name ) >= MAX_QPATH ) {
		return 0;
	}

	image = R_CreateImage( name, pic, width, height, mipRawImage, mipRawImage, mipRawImage ? GL_REPEAT : GL_CLAMP );
	if ( !image ) {
		return 0;
	}

	return RE_RegisterShaderFromImage( name, LIGHTMAP_2D, image, mipRawImage );
}

/*
============
CL_RegisterShaderFromMemory

Routes encoded image payloads through the retail Quake Live in-memory image
loader, then wraps the decoded image in the normal 2D shader registration
path.
============
*/
qhandle_t CL_RegisterShaderFromMemory( const char *name, const byte *buffer, int bufferLength, qboolean mipRawImage ) {
	image_t *image;

	if ( !name || !buffer || bufferLength <= 0 || strlen( name ) >= MAX_QPATH ) {
		return 0;
	}

	image = R_LoadImageFromMemory( name, buffer, bufferLength, mipRawImage, mipRawImage, mipRawImage ? GL_REPEAT : GL_CLAMP );
	if ( !image ) {
		return 0;
	}

	return RE_RegisterShaderFromImage( name, LIGHTMAP_2D, image, mipRawImage );
}

/*
============
CL_InitRef
============
*/
void CL_InitRef( void ) {
	refimport_t	ri;
	refexport_t	*ret;

	Com_Printf( "----- Initializing Renderer ----\n" );

	ri.Cmd_AddCommand = Cmd_AddCommand;
	ri.Cmd_RemoveCommand = Cmd_RemoveCommand;
	ri.Cmd_Argc = Cmd_Argc;
	ri.Cmd_Argv = Cmd_Argv;
	ri.Cmd_ExecuteText = Cbuf_ExecuteText;
	ri.Printf = CL_RefPrintf;
	ri.Error = Com_Error;
	ri.Milliseconds = CL_ScaledMilliseconds;
	ri.Malloc = CL_RefMalloc;
	ri.Free = Z_Free;
#ifdef HUNK_DEBUG
	ri.Hunk_AllocDebug = Hunk_AllocDebug;
#else
	ri.Hunk_Alloc = Hunk_Alloc;
#endif
	ri.Hunk_AllocateTempMemory = Hunk_AllocateTempMemory;
	ri.Hunk_FreeTempMemory = Hunk_FreeTempMemory;
	ri.CM_DrawDebugSurface = CM_DrawDebugSurface;
	ri.FS_ReadFile = FS_ReadFile;
	ri.FS_FreeFile = FS_FreeFile;
	ri.FS_WriteFile = FS_WriteFile;
	ri.FS_FreeFileList = FS_FreeFileList;
	ri.FS_ListFiles = FS_ListFiles;
	ri.FS_FileIsInPAK = FS_FileIsInPAK;
	ri.FS_FileExists = FS_FileExists;
	ri.Cvar_Get = Cvar_Get;
	ri.Cvar_GetBounded = Cvar_GetBounded;
	ri.Cvar_Set = Cvar_Set;

	// cinematic stuff

	ri.CIN_UploadCinematic = CIN_UploadCinematic;
	ri.CIN_PlayCinematic = CIN_PlayCinematic;
	ri.CIN_RunCinematic = CIN_RunCinematic;

	ret = GetRefAPI( REF_API_VERSION, &ri );

#if defined __USEA3D && defined __A3D_GEOM
	hA3Dg_ExportRenderGeom (ret);
#endif

	Com_Printf( "-------------------------------\n");

	if ( !ret ) {
		Com_Error (ERR_FATAL, "Couldn't initialize refresh" );
	}

	re = *ret;

	// unpause so the cgame definately gets a snapshot and renders a frame
	Cvar_Set( "cl_paused", "0" );
}


//===========================================================================================


void CL_SetModel_f( void ) {
	char	*arg;
	char	name[256];

	arg = Cmd_Argv( 1 );
	if (arg[0]) {
		Cvar_Set( "model", arg );
		Cvar_Set( "headmodel", arg );
	} else {
		Cvar_VariableStringBuffer( "model", name, sizeof(name) );
		Com_Printf("model is set to %s\n", name);
	}
}

/*
====================
CL_Init
====================
*/
void CL_Init( void ) {
	Com_Printf( "----- Client Initialization -----\n" );

	Con_Init ();	

	CL_ClearState ();

	cls.state = CA_DISCONNECTED;	// no longer CA_UNINITIALIZED

	cls.realtime = 0;

	CL_InitInput ();

	//
	// register our variables
	//
	cl_noprint = Cvar_Get( "cl_noprint", "0", 0 );
	cl_motd = Cvar_Get ("cl_motd", "1", 0);

	cl_timeout = Cvar_Get ("cl_timeout", "40", 0);

	cl_timeNudge = Cvar_GetBounded( "cl_timeNudge", "0", "-20", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED );
	cl_shownet = Cvar_Get ("cl_shownet", "0", CVAR_TEMP );
	cl_showSend = Cvar_Get ("cl_showSend", "0", CVAR_TEMP );
	cl_showTimeDelta = Cvar_Get ("cl_showTimeDelta", "0", CVAR_TEMP );
	cl_freezeDemo = Cvar_Get ("cl_freezeDemo", "0", CVAR_TEMP );
	cl_quitOnDemoCompleted = Cvar_Get ("cl_quitOnDemoCompleted", "0", 0 );
	cl_allowConsoleChat = Cvar_Get ("cl_allowConsoleChat", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	Cvar_Get ("web_browserActive", "0", CVAR_ROM );
	Cvar_Get ("ui_browserAwesomiumProvider", "Unavailable", CVAR_ROM );
	Cvar_Get ("ui_browserAwesomiumPolicy", "compatibility-unavailable", CVAR_ROM );
	Cvar_Get ("ui_advertisementBridgeProvider", "Unavailable", CVAR_ROM );
	Cvar_Get ("ui_advertisementBridgePolicy", "compatibility-unavailable", CVAR_ROM );
	Cvar_Get ("ui_resourceBridgeProvider", "Unavailable", CVAR_ROM );
	Cvar_Get ("ui_resourceBridgePolicy", "compatibility-unavailable", CVAR_ROM );
	Cvar_Get ("ui_subscriptionBridgeMode", "Unavailable", CVAR_ROM );
	Cvar_Get ("ui_subscriptionBridgePolicy", "compatibility-unavailable", CVAR_ROM );
	Cvar_Get ("cl_onlineServicesMode", "Unavailable", CVAR_ROM );
	Cvar_Get ("cl_onlineServicesPolicy", "compatibility-unavailable", CVAR_ROM );
	Cvar_Get ("cl_identityBootstrapMode", "Unavailable", CVAR_ROM );
	Cvar_Get ("cl_identityBootstrapPolicy", "compatibility-unavailable", CVAR_ROM );
	Cvar_Get ("cl_voiceServiceMode", "Unavailable", CVAR_ROM );
	Cvar_Get ("cl_voiceServicePolicy", "compatibility-unavailable", CVAR_ROM );
	Cvar_Get ("cl_workshopProvider", "Unavailable", CVAR_ROM );
	Cvar_Get ("cl_workshopPolicy", "compatibility-unavailable", CVAR_ROM );
	Cvar_Get ("cl_matchmakingProvider", "Unavailable", CVAR_ROM );
	Cvar_Get ("cl_matchmakingPolicy", "compatibility-unavailable", CVAR_ROM );
	Cvar_Get ("cl_statsProvider", "Unavailable", CVAR_ROM );
	Cvar_Get ("cl_statsPolicy", "compatibility-unavailable", CVAR_ROM );
	Cvar_Get ("cl_socialOverlayProvider", "Unavailable", CVAR_ROM );
	Cvar_Get ("cl_socialOverlayPolicy", "compatibility-unavailable", CVAR_ROM );
	Cvar_Get ("web_zoom", "100", CVAR_ARCHIVE );
	Cvar_Get ("web_console", "0", CVAR_ARCHIVE );
	rcon_client_password = Cvar_Get ("rconPassword", "", CVAR_TEMP );
	cl_activeAction = Cvar_Get( "activeAction", "", CVAR_TEMP );
	cl_demoRecordMessage = Cvar_Get ("cl_demoRecordMessage", "2", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	cl_lobbyAutoConnect = Cvar_Get( "lobby_autoconnect", "", CVAR_TEMP );
	cl_steamMaxLobbyClients = Cvar_Get( "steam_maxLobbyClients", "16", CVAR_ARCHIVE );

	cl_timedemo = Cvar_Get ("timedemo", "0", 0);
	cl_avidemo = Cvar_Get ("cl_avidemo", "0", 0);
	cl_avidemo_latch = Cvar_Get ("cl_avidemo_latch", "0", 0 );
	cl_avidemo_mintime = Cvar_Get ("cl_avidemo_mintime", "0", 0 );
	cl_avidemo_maxtime = Cvar_Get ("cl_avidemo_maxtime", "0", 0 );
	cl_forceavidemo = Cvar_Get ("cl_forceavidemo", "0", 0);

	rconAddress = Cvar_Get ("rconAddress", "", 0);

	cl_yawspeed = Cvar_Get ("cl_yawspeed", "140", CVAR_CHEAT );
	cl_pitchspeed = Cvar_Get ("cl_pitchspeed", "140", CVAR_CHEAT );
	cl_anglespeedkey = Cvar_Get ("cl_anglespeedkey", "1.5", CVAR_CHEAT );

	cl_maxpackets = Cvar_Get ("cl_maxpackets", "125", CVAR_CHEAT );
	cl_packetdup = Cvar_Get ("cl_packetdup", "1", CVAR_ARCHIVE | CVAR_CLOUD );

	cl_run = Cvar_Get ("cl_run", "1", CVAR_ARCHIVE);
	cl_viewAccel = Cvar_Get ("cl_viewAccel", "1.7", CVAR_ARCHIVE | CVAR_CLOUD );
	cl_sensitivity = Cvar_Get ("sensitivity", "4", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	cl_mouseAccel = Cvar_Get ("cl_mouseAccel", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	cl_mouseAccelDebug = Cvar_Get ("cl_mouseAccelDebug", "0", 0 );
	cl_mouseAccelOffset = Cvar_Get ("cl_mouseAccelOffset", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	cl_mouseAccelPower = Cvar_Get ("cl_mouseAccelPower", "2", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	cl_mouseSensCap = Cvar_Get ("cl_mouseSensCap", "0", CVAR_ARCHIVE | CVAR_CLOUD );
	cl_freelook = Cvar_Get( "cl_freelook", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );

	cl_allowDownload = Cvar_Get ("cl_allowDownload", "1", CVAR_ARCHIVE );

	cl_conXOffset = Cvar_Get ("cl_conXOffset", "0", 0);
	cl_inGameVideo = Cvar_Get ("r_inGameVideo", "1", CVAR_ARCHIVE);

	cl_serverStatusResendTime = Cvar_Get ("cl_serverStatusResendTime", "750", 0);

	// init autoswitch so the ui will have it correctly even
	// if the cgame hasn't been started
	Cvar_Get ("cg_autoswitch", "1", CVAR_ARCHIVE);

	m_pitch = Cvar_Get ("m_pitch", "0.022", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	m_yaw = Cvar_Get ("m_yaw", "0.022", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	m_forward = Cvar_Get ("m_forward", "0.25", CVAR_ARCHIVE | CVAR_CLOUD );
	m_side = Cvar_Get ("m_side", "0.25", CVAR_ARCHIVE | CVAR_CLOUD );
	m_filter = Cvar_Get ("m_filter", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	m_cpi = Cvar_Get ("m_cpi", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );

	cl_motdString = Cvar_Get( "cl_motdString", "", CVAR_ROM );
	cl_platform = Cvar_Get ("cl_platform", "1", CVAR_ROM );

	cl_autoTimeNudge = Cvar_GetBounded( "cl_autoTimeNudge", "0", "0", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED );
	cl_contimestamps = Cvar_Get ("cl_contimestamps", "0", CVAR_ARCHIVE );
	cl_mouseAccelStyle = Cvar_Get ("cl_mouseAccelStyle", "0", CVAR_ARCHIVE );
	cl_guid = Cvar_Get ("cl_guid", "", CVAR_USERINFO | CVAR_ROM );
	cl_punkbuster = Cvar_Get ("cl_punkbuster", "1", CVAR_ARCHIVE | CVAR_USERINFO );

	Cvar_Get( "cl_maxPing", "800", CVAR_ARCHIVE );
	Cvar_Get( "cl_downloadName", "", CVAR_TEMP );
	Cvar_Get( "cl_downloadTime", "0", CVAR_TEMP );
	Cvar_Get( "cl_downloadItem", "", CVAR_TEMP );
	Cvar_Get( "cl_downloadCount", "0", CVAR_TEMP );
	Cvar_Get( "cl_downloadSize", "0", CVAR_TEMP );

	// userinfo
	Cvar_Get ("name", "UnnamedPlayer", CVAR_USERINFO | CVAR_ROM );
	Cvar_Get ("country", "", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	Cvar_GetBounded( "rate", "25000", "8000", "25000", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_LATCH | CVAR_VM_CREATED );
	Cvar_Get ("snaps", "20", CVAR_USERINFO | CVAR_ARCHIVE );
	Cvar_Get ("model", "sarge", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED );
	Cvar_Get ("headmodel", "sarge", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED );
	Cvar_Get ("team_model", "james", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED );
	Cvar_Get ("team_headmodel", "*james", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED );
	Cvar_Get ("g_redTeam", "Stroggs", CVAR_ARCHIVE);
	Cvar_Get ("g_blueTeam", "Pagans", CVAR_ARCHIVE);
	Cvar_GetBounded( "color1", "7", "1", "26", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	Cvar_GetBounded( "color2", "25", "1", "26", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	Cvar_Get ("handicap", "100", CVAR_USERINFO | CVAR_TEMP );
	Cvar_Get ("teamtask", "0", CVAR_USERINFO | CVAR_PROTECTED );
	Cvar_Get ("sex", "male", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED );
	Cvar_Get ("cl_anonymous", "0", CVAR_USERINFO | CVAR_ARCHIVE );

	Cvar_Get ("password", "", CVAR_USERINFO | CVAR_TEMP);
	Cvar_Get ("cg_predictItems", "1", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	Cvar_Get ("cg_autoAction", "", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );
	Cvar_Get ("cg_autoHop", "1", CVAR_USERINFO | CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD );

	// cgame might not be initialized before menu is used
	Cvar_Get ("cg_viewsize", "100", CVAR_ARCHIVE | CVAR_CLOUD );
	
	CL_RefreshPlatformServiceCvars();
	CL_InitSteamResources();
	CL_WebHost_Init();
	
	//
	// register our commands
	//
	Cmd_AddCommand ("cmd", CL_ForwardToServer_f);
	Cmd_AddCommand ("configstrings", CL_Configstrings_f);
	Cmd_AddCommand ("clientinfo", CL_Clientinfo_f);
	Cmd_AddCommand ("snd_restart", CL_Snd_Restart_f);
	Cmd_AddCommand ("vid_restart", CL_Vid_Restart_f);
	Cmd_AddCommand ("postprocess_restart", CL_PostProcessRestart_f);
	Cmd_AddCommand ("disconnect", CL_Disconnect_f);
	Cmd_AddCommand ("record", CL_Record_f);
	Cmd_AddCommand ("demo", CL_PlayDemo_f);
	Cmd_AddCommand ("cinematic", CL_PlayCinematic_f);
	Cmd_AddCommand ("stoprecord", CL_StopRecord_f);
	Cmd_AddCommand ("connect", CL_Connect_f);
	Cmd_AddCommand ("reconnect", CL_Reconnect_f);
	Cmd_AddCommand ("localservers", CL_LocalServers_f);
	Cmd_AddCommand ("globalservers", CL_GlobalServers_f);
	Cmd_AddCommand ("rcon", CL_Rcon_f);
	Cmd_AddCommand ("setenv", CL_Setenv_f );
	Cmd_AddCommand ("ping", CL_Ping_f );
	Cmd_AddCommand ("serverstatus", CL_ServerStatus_f );
	Cmd_AddCommand ("showip", CL_ShowIP_f );
	Cmd_AddCommand ("fs_openedList", CL_OpenedPK3List_f );
	Cmd_AddCommand ("fs_referencedList", CL_ReferencedPK3List_f );
	Cmd_AddCommand ("model", CL_SetModel_f );
	Cmd_AddCommand ("userinfo", CL_Userinfo_f );
	Cmd_AddCommand ("web_showBrowser", CL_Web_ShowBrowser_f );
	Cmd_AddCommand ("web_changeHash", CL_Web_ChangeHash_f );
	Cmd_AddCommand ("web_hideBrowser", CL_Web_HideBrowser_f );
	Cmd_AddCommand ("web_showError", CL_Web_ShowError_f );
	Cmd_AddCommand ("web_clearCache", CL_Web_ClearCache_f );
	Cmd_AddCommand ("web_reload", CL_Web_Reload_f );
	Cmd_AddCommand ("+voice", CL_VoiceStartRecording_f );
	Cmd_AddCommand ("-voice", CL_VoiceStopRecording_f );
	Cmd_AddCommand ("connect_lobby", CL_Steam_ConnectLobby_f );
	Cmd_AddCommand ("clientviewprofile", CL_Steam_OverlayCommand_f );
	Cmd_AddCommand ("clientfriendinvite", CL_Steam_OverlayCommand_f );
	cl_statsClearRegistered = qfalse;
	if ( CL_Steam_ShouldRegisterStatsClear() ) {
		Cmd_AddCommand ("stats_clear", CL_Steam_ClearStats_f );
		cl_statsClearRegistered = qtrue;
	}
	CL_Steam_InitCallbacks();
	CL_Steam_SetMainMenuRichPresence();
	CL_Steam_SyncPersonaNameCvar();
	CL_Steam_SeedCountryCvar();
	CL_WebPak_Init();
	CL_InitRef();

	SCR_Init ();

	Cbuf_Execute ();

	Cvar_Set( "cl_running", "1" );

	Com_Printf( "----- Client Initialization Complete -----\n" );
}


/*
===============
CL_Shutdown

===============
*/
void CL_Shutdown( void ) {
	static qboolean recursive = qfalse;
	
	Com_Printf( "----- CL_Shutdown -----\n" );

	if ( recursive ) {
		printf ("recursive shutdown\n");
		return;
	}
	recursive = qtrue;

	CL_Disconnect( qtrue );
	
	S_Shutdown();
	CL_ShutdownRef();

	CL_Steam_ShutdownCallbacks();
	CL_WebHost_Shutdown();
	CL_WebPak_Shutdown();
	CL_ShutdownUI();
	CL_ShutdownSteamResources();
	
	Cmd_RemoveCommand ("cmd");
	Cmd_RemoveCommand ("configstrings");
	Cmd_RemoveCommand ("userinfo");
	Cmd_RemoveCommand ("snd_restart");
	Cmd_RemoveCommand ("vid_restart");
	Cmd_RemoveCommand ("postprocess_restart");
	Cmd_RemoveCommand ("disconnect");
	Cmd_RemoveCommand ("record");
	Cmd_RemoveCommand ("demo");
	Cmd_RemoveCommand ("cinematic");
	Cmd_RemoveCommand ("stoprecord");
	Cmd_RemoveCommand ("connect");
	Cmd_RemoveCommand ("localservers");
	Cmd_RemoveCommand ("globalservers");
	Cmd_RemoveCommand ("rcon");
	Cmd_RemoveCommand ("setenv");
	Cmd_RemoveCommand ("ping");
	Cmd_RemoveCommand ("serverstatus");
	Cmd_RemoveCommand ("showip");
	Cmd_RemoveCommand ("model");
	Cmd_RemoveCommand ("web_showBrowser");
	Cmd_RemoveCommand ("web_changeHash");
	Cmd_RemoveCommand ("web_hideBrowser");
	Cmd_RemoveCommand ("web_showError");
	Cmd_RemoveCommand ("web_clearCache");
	Cmd_RemoveCommand ("web_reload");
	Cmd_RemoveCommand ("+voice");
	Cmd_RemoveCommand ("-voice");
	Cmd_RemoveCommand ("connect_lobby");
	Cmd_RemoveCommand ("clientviewprofile");
	Cmd_RemoveCommand ("clientfriendinvite");
	if ( cl_statsClearRegistered ) {
		Cmd_RemoveCommand ("stats_clear");
		cl_statsClearRegistered = qfalse;
	}

	Cvar_Set( "cl_running", "0" );

	recursive = qfalse;

	Com_Memset( &cls, 0, sizeof( cls ) );

	Com_Printf( "-----------------------\n" );

}

static void CL_SetServerInfo(serverInfo_t *server, const char *info, int ping) {
	if (server) {
		if (info) {
			server->clients = atoi(Info_ValueForKey(info, "clients"));
			Q_strncpyz(server->hostName,Info_ValueForKey(info, "hostname"), MAX_NAME_LENGTH);
			Q_strncpyz(server->mapName, Info_ValueForKey(info, "mapname"), MAX_NAME_LENGTH);
			server->maxClients = atoi(Info_ValueForKey(info, "sv_maxclients"));
			Q_strncpyz(server->game,Info_ValueForKey(info, "game"), MAX_NAME_LENGTH);
			server->gameType = atoi(Info_ValueForKey(info, "gametype"));
			server->netType = atoi(Info_ValueForKey(info, "nettype"));
		}
		server->ping = ping;
	}
}

static void CL_SetServerInfoByAddress(netadr_t from, const char *info, int ping) {
	int i;

	for (i = 0; i < MAX_OTHER_SERVERS; i++) {
		if (NET_CompareAdr(from, cls.localServers[i].adr)) {
			CL_SetServerInfo(&cls.localServers[i], info, ping);
		}
	}

	for (i = 0; i < MAX_OTHER_SERVERS; i++) {
		if (NET_CompareAdr(from, cls.mplayerServers[i].adr)) {
			CL_SetServerInfo(&cls.mplayerServers[i], info, ping);
		}
	}

	for (i = 0; i < MAX_GLOBAL_SERVERS; i++) {
		if (NET_CompareAdr(from, cls.globalServers[i].adr)) {
			CL_SetServerInfo(&cls.globalServers[i], info, ping);
		}
	}

	for (i = 0; i < MAX_OTHER_SERVERS; i++) {
		if (NET_CompareAdr(from, cls.favoriteServers[i].adr)) {
			CL_SetServerInfo(&cls.favoriteServers[i], info, ping);
		}
	}

}

/*
===================
CL_ServerInfoPacket
===================
*/
void CL_ServerInfoPacket( netadr_t from, msg_t *msg ) {
	int		i, type;
	char	info[MAX_INFO_STRING];
	char*	str;
	char	*infoString;
	int		prot;

	infoString = MSG_ReadString( msg );

	// if this isn't the correct protocol version, ignore it
	prot = atoi( Info_ValueForKey( infoString, "protocol" ) );
	if ( prot != PROTOCOL_VERSION ) {
		Com_DPrintf( "Different protocol info packet: %s\n", infoString );
		return;
	}

	// iterate servers waiting for ping response
	for (i=0; i<MAX_PINGREQUESTS; i++)
	{
		if ( cl_pinglist[i].adr.port && !cl_pinglist[i].time && NET_CompareAdr( from, cl_pinglist[i].adr ) )
		{
			// calc ping time
			cl_pinglist[i].time = cls.realtime - cl_pinglist[i].start + 1;
			Com_DPrintf( "ping time %dms from %s\n", cl_pinglist[i].time, NET_AdrToString( from ) );

			// save of info
			Q_strncpyz( cl_pinglist[i].info, infoString, sizeof( cl_pinglist[i].info ) );

			// tack on the net type
			// NOTE: make sure these types are in sync with the netnames strings in the UI
			switch (from.type)
			{
				case NA_BROADCAST:
				case NA_IP:
					str = "udp";
					type = 1;
					break;

				case NA_IPX:
				case NA_BROADCAST_IPX:
					str = "ipx";
					type = 2;
					break;

				default:
					str = "???";
					type = 0;
					break;
			}
			Info_SetValueForKey( cl_pinglist[i].info, "nettype", va("%d", type) );
			CL_SetServerInfoByAddress(from, infoString, cl_pinglist[i].time);

			return;
		}
	}

	// if not just sent a local broadcast or pinging local servers
	if (cls.pingUpdateSource != AS_LOCAL) {
		return;
	}

	for ( i = 0 ; i < MAX_OTHER_SERVERS ; i++ ) {
		// empty slot
		if ( cls.localServers[i].adr.port == 0 ) {
			break;
		}

		// avoid duplicate
		if ( NET_CompareAdr( from, cls.localServers[i].adr ) ) {
			return;
		}
	}

	if ( i == MAX_OTHER_SERVERS ) {
		Com_DPrintf( "MAX_OTHER_SERVERS hit, dropping infoResponse\n" );
		return;
	}

	// add this to the list
	cls.numlocalservers = i+1;
	cls.localServers[i].adr = from;
	cls.localServers[i].clients = 0;
	cls.localServers[i].hostName[0] = '\0';
	cls.localServers[i].mapName[0] = '\0';
	cls.localServers[i].maxClients = 0;
	cls.localServers[i].maxPing = 0;
	cls.localServers[i].minPing = 0;
	cls.localServers[i].ping = -1;
	cls.localServers[i].game[0] = '\0';
	cls.localServers[i].gameType = 0;
	cls.localServers[i].netType = from.type;
	cls.localServers[i].punkbuster = 0;
									 
	Q_strncpyz( info, MSG_ReadString( msg ), MAX_INFO_STRING );
	if (strlen(info)) {
		if (info[strlen(info)-1] != '\n') {
			strncat(info, "\n", sizeof(info));
		}
		Com_Printf( "%s: %s", NET_AdrToString( from ), info );
	}
}

/*
===================
CL_GetServerStatus
===================
*/
serverStatus_t *CL_GetServerStatus( netadr_t from ) {
	serverStatus_t *serverStatus;
	int i, oldest, oldestTime;

	serverStatus = NULL;
	for (i = 0; i < MAX_SERVERSTATUSREQUESTS; i++) {
		if ( NET_CompareAdr( from, cl_serverStatusList[i].address ) ) {
			return &cl_serverStatusList[i];
		}
	}
	for (i = 0; i < MAX_SERVERSTATUSREQUESTS; i++) {
		if ( cl_serverStatusList[i].retrieved ) {
			return &cl_serverStatusList[i];
		}
	}
	oldest = -1;
	oldestTime = 0;
	for (i = 0; i < MAX_SERVERSTATUSREQUESTS; i++) {
		if (oldest == -1 || cl_serverStatusList[i].startTime < oldestTime) {
			oldest = i;
			oldestTime = cl_serverStatusList[i].startTime;
		}
	}
	if (oldest != -1) {
		return &cl_serverStatusList[oldest];
	}
	serverStatusCount++;
	return &cl_serverStatusList[serverStatusCount & (MAX_SERVERSTATUSREQUESTS-1)];
}

/*
===================
CL_ServerStatus
===================
*/
int CL_ServerStatus( char *serverAddress, char *serverStatusString, int maxLen ) {
	int i;
	netadr_t	to;
	serverStatus_t *serverStatus;

	// if no server address then reset all server status requests
	if ( !serverAddress ) {
		for (i = 0; i < MAX_SERVERSTATUSREQUESTS; i++) {
			cl_serverStatusList[i].address.port = 0;
			cl_serverStatusList[i].retrieved = qtrue;
		}
		return qfalse;
	}
	// get the address
	if ( !NET_StringToAdr( serverAddress, &to ) ) {
		return qfalse;
	}
	serverStatus = CL_GetServerStatus( to );
	// if no server status string then reset the server status request for this address
	if ( !serverStatusString ) {
		serverStatus->retrieved = qtrue;
		return qfalse;
	}

	// if this server status request has the same address
	if ( NET_CompareAdr( to, serverStatus->address) ) {
		// if we recieved an response for this server status request
		if (!serverStatus->pending) {
			Q_strncpyz(serverStatusString, serverStatus->string, maxLen);
			serverStatus->retrieved = qtrue;
			serverStatus->startTime = 0;
			return qtrue;
		}
		// resend the request regularly
		else if ( serverStatus->startTime < Com_Milliseconds() - cl_serverStatusResendTime->integer ) {
			serverStatus->print = qfalse;
			serverStatus->pending = qtrue;
			serverStatus->retrieved = qfalse;
			serverStatus->time = 0;
			serverStatus->startTime = Com_Milliseconds();
			NET_OutOfBandPrint( NS_CLIENT, to, "getstatus" );
			return qfalse;
		}
	}
	// if retrieved
	else if ( serverStatus->retrieved ) {
		serverStatus->address = to;
		serverStatus->print = qfalse;
		serverStatus->pending = qtrue;
		serverStatus->retrieved = qfalse;
		serverStatus->startTime = Com_Milliseconds();
		serverStatus->time = 0;
		NET_OutOfBandPrint( NS_CLIENT, to, "getstatus" );
		return qfalse;
	}
	return qfalse;
}

/*
===================
CL_ServerStatusResponse
===================
*/
void CL_ServerStatusResponse( netadr_t from, msg_t *msg ) {
	char	*s;
	char	info[MAX_INFO_STRING];
	int		i, l, score, ping;
	int		len;
	serverStatus_t *serverStatus;

	serverStatus = NULL;
	for (i = 0; i < MAX_SERVERSTATUSREQUESTS; i++) {
		if ( NET_CompareAdr( from, cl_serverStatusList[i].address ) ) {
			serverStatus = &cl_serverStatusList[i];
			break;
		}
	}
	// if we didn't request this server status
	if (!serverStatus) {
		return;
	}

	s = MSG_ReadStringLine( msg );

	len = 0;
	Com_sprintf(&serverStatus->string[len], sizeof(serverStatus->string)-len, "%s", s);

	if (serverStatus->print) {
		Com_Printf("Server settings:\n");
		// print cvars
		while (*s) {
			for (i = 0; i < 2 && *s; i++) {
				if (*s == '\\')
					s++;
				l = 0;
				while (*s) {
					info[l++] = *s;
					if (l >= MAX_INFO_STRING-1)
						break;
					s++;
					if (*s == '\\') {
						break;
					}
				}
				info[l] = '\0';
				if (i) {
					Com_Printf("%s\n", info);
				}
				else {
					Com_Printf("%-24s", info);
				}
			}
		}
	}

	len = strlen(serverStatus->string);
	Com_sprintf(&serverStatus->string[len], sizeof(serverStatus->string)-len, "\\");

	if (serverStatus->print) {
		Com_Printf("\nPlayers:\n");
		Com_Printf("num: score: ping: name:\n");
	}
	for (i = 0, s = MSG_ReadStringLine( msg ); *s; s = MSG_ReadStringLine( msg ), i++) {

		len = strlen(serverStatus->string);
		Com_sprintf(&serverStatus->string[len], sizeof(serverStatus->string)-len, "\\%s", s);

		if (serverStatus->print) {
			score = ping = 0;
			sscanf(s, "%d %d", &score, &ping);
			s = strchr(s, ' ');
			if (s)
				s = strchr(s+1, ' ');
			if (s)
				s++;
			else
				s = "unknown";
			Com_Printf("%-2d   %-3d    %-3d   %s\n", i, score, ping, s );
		}
	}
	len = strlen(serverStatus->string);
	Com_sprintf(&serverStatus->string[len], sizeof(serverStatus->string)-len, "\\");

	serverStatus->time = Com_Milliseconds();
	serverStatus->address = from;
	serverStatus->pending = qfalse;
	if (serverStatus->print) {
		serverStatus->retrieved = qtrue;
	}
}

/*
==================
CL_LocalServers_f
==================
*/
void CL_LocalServers_f( void ) {
	char		*message;
	int			i, j;
	netadr_t	to;

	Com_Printf( "Scanning for servers on the local network...\n");

	// reset the list, waiting for response
	cls.numlocalservers = 0;
	cls.pingUpdateSource = AS_LOCAL;

	for (i = 0; i < MAX_OTHER_SERVERS; i++) {
		qboolean b = cls.localServers[i].visible;
		Com_Memset(&cls.localServers[i], 0, sizeof(cls.localServers[i]));
		cls.localServers[i].visible = b;
	}
	Com_Memset( &to, 0, sizeof( to ) );

	// The 'xxx' in the message is a challenge that will be echoed back
	// by the server.  We don't care about that here, but master servers
	// can use that to prevent spoofed server responses from invalid ip
	message = "\377\377\377\377getinfo xxx";

	// send each message twice in case one is dropped
	for ( i = 0 ; i < 2 ; i++ ) {
		// send a broadcast packet on each server port
		// we support multiple server ports so a single machine
		// can nicely run multiple servers
		for ( j = 0 ; j < NUM_SERVER_PORTS ; j++ ) {
			to.port = BigShort( (short)(PORT_SERVER + j) );

			to.type = NA_BROADCAST;
			NET_SendPacket( NS_CLIENT, strlen( message ), message, to );

			to.type = NA_BROADCAST_IPX;
			NET_SendPacket( NS_CLIENT, strlen( message ), message, to );
		}
	}
}

/*
==================
CL_GlobalServers_f
==================
*/
void CL_GlobalServers_f( void ) {
	netadr_t	to;
	int			i;
	int			count;
	char		*buffptr;
	char		command[1024];
	
	if ( Cmd_Argc() < 3) {
		Com_Printf( "usage: globalservers <master# 0-1> <protocol> [keywords]\n");
		return;	
	}

	cls.masterNum = atoi( Cmd_Argv(1) );

	Com_Printf( "Requesting servers from the master...\n");

	// reset the list, waiting for response
	// -1 is used to distinguish a "no response"

	if( cls.masterNum == 1 ) {
		NET_StringToAdr( MASTER_SERVER_NAME, &to );
		cls.nummplayerservers = -1;
		cls.pingUpdateSource = AS_MPLAYER;
	}
	else {
		NET_StringToAdr( MASTER_SERVER_NAME, &to );
		cls.numglobalservers = -1;
		cls.pingUpdateSource = AS_GLOBAL;
	}
	to.type = NA_IP;
	to.port = BigShort(PORT_MASTER);

	sprintf( command, "getservers %s", Cmd_Argv(2) );

	// tack on keywords
	buffptr = command + strlen( command );
	count   = Cmd_Argc();
	for (i=3; i<count; i++)
		buffptr += sprintf( buffptr, " %s", Cmd_Argv(i) );

	// if we are a demo, automatically add a "demo" keyword
	if ( Cvar_VariableValue( "fs_restrict" ) ) {
		buffptr += sprintf( buffptr, " demo" );
	}

	NET_OutOfBandPrint( NS_SERVER, to, command );
}


/*
==================
CL_GetPing
==================
*/
void CL_GetPing( int n, char *buf, int buflen, int *pingtime )
{
	const char	*str;
	int		time;
	int		maxPing;

	if (!cl_pinglist[n].adr.port)
	{
		// empty slot
		buf[0]    = '\0';
		*pingtime = 0;
		return;
	}

	str = NET_AdrToString( cl_pinglist[n].adr );
	Q_strncpyz( buf, str, buflen );

	time = cl_pinglist[n].time;
	if (!time)
	{
		// check for timeout
		time = cls.realtime - cl_pinglist[n].start;
		maxPing = Cvar_VariableIntegerValue( "cl_maxPing" );
		if( maxPing < 100 ) {
			maxPing = 100;
		}
		if (time < maxPing)
		{
			// not timed out yet
			time = 0;
		}
	}

	CL_SetServerInfoByAddress(cl_pinglist[n].adr, cl_pinglist[n].info, cl_pinglist[n].time);

	*pingtime = time;
}

/*
==================
CL_UpdateServerInfo
==================
*/
void CL_UpdateServerInfo( int n )
{
	if (!cl_pinglist[n].adr.port)
	{
		return;
	}

	CL_SetServerInfoByAddress(cl_pinglist[n].adr, cl_pinglist[n].info, cl_pinglist[n].time );
}

/*
==================
CL_GetPingInfo
==================
*/
void CL_GetPingInfo( int n, char *buf, int buflen )
{
	if (!cl_pinglist[n].adr.port)
	{
		// empty slot
		if (buflen)
			buf[0] = '\0';
		return;
	}

	Q_strncpyz( buf, cl_pinglist[n].info, buflen );
}

/*
==================
CL_ClearPing
==================
*/
void CL_ClearPing( int n )
{
	if (n < 0 || n >= MAX_PINGREQUESTS)
		return;

	cl_pinglist[n].adr.port = 0;
}

/*
==================
CL_GetPingQueueCount
==================
*/
int CL_GetPingQueueCount( void )
{
	int		i;
	int		count;
	ping_t*	pingptr;

	count   = 0;
	pingptr = cl_pinglist;

	for (i=0; i<MAX_PINGREQUESTS; i++, pingptr++ ) {
		if (pingptr->adr.port) {
			count++;
		}
	}

	return (count);
}

/*
==================
CL_GetFreePing
==================
*/
ping_t* CL_GetFreePing( void )
{
	ping_t*	pingptr;
	ping_t*	best;	
	int		oldest;
	int		i;
	int		time;

	pingptr = cl_pinglist;
	for (i=0; i<MAX_PINGREQUESTS; i++, pingptr++ )
	{
		// find free ping slot
		if (pingptr->adr.port)
		{
			if (!pingptr->time)
			{
				if (cls.realtime - pingptr->start < 500)
				{
					// still waiting for response
					continue;
				}
			}
			else if (pingptr->time < 500)
			{
				// results have not been queried
				continue;
			}
		}

		// clear it
		pingptr->adr.port = 0;
		return (pingptr);
	}

	// use oldest entry
	pingptr = cl_pinglist;
	best    = cl_pinglist;
	oldest  = INT_MIN;
	for (i=0; i<MAX_PINGREQUESTS; i++, pingptr++ )
	{
		// scan for oldest
		time = cls.realtime - pingptr->start;
		if (time > oldest)
		{
			oldest = time;
			best   = pingptr;
		}
	}

	return (best);
}

/*
==================
CL_Ping_f
==================
*/
void CL_Ping_f( void ) {
	netadr_t	to;
	ping_t*		pingptr;
	char*		server;

	if ( Cmd_Argc() != 2 ) {
		Com_Printf( "usage: ping [server]\n");
		return;	
	}

	Com_Memset( &to, 0, sizeof(netadr_t) );

	server = Cmd_Argv(1);

	if ( !NET_StringToAdr( server, &to ) ) {
		return;
	}

	pingptr = CL_GetFreePing();

	memcpy( &pingptr->adr, &to, sizeof (netadr_t) );
	pingptr->start = cls.realtime;
	pingptr->time  = 0;

	CL_SetServerInfoByAddress(pingptr->adr, NULL, 0);
		
	NET_OutOfBandPrint( NS_CLIENT, to, "getinfo xxx" );
}

/*
==================
CL_UpdateVisiblePings_f
==================
*/
qboolean CL_UpdateVisiblePings_f(int source) {
	int			slots, i;
	char		buff[MAX_STRING_CHARS];
	int			pingTime;
	int			max;
	qboolean status = qfalse;

	if (source < 0 || source > AS_FAVORITES) {
		return qfalse;
	}

	cls.pingUpdateSource = source;

	slots = CL_GetPingQueueCount();
	if (slots < MAX_PINGREQUESTS) {
		serverInfo_t *server = NULL;

		max = (source == AS_GLOBAL) ? MAX_GLOBAL_SERVERS : MAX_OTHER_SERVERS;
		switch (source) {
			case AS_LOCAL :
				server = &cls.localServers[0];
				max = cls.numlocalservers;
			break;
			case AS_MPLAYER :
				server = &cls.mplayerServers[0];
				max = cls.nummplayerservers;
			break;
			case AS_GLOBAL :
				server = &cls.globalServers[0];
				max = cls.numglobalservers;
			break;
			case AS_FAVORITES :
				server = &cls.favoriteServers[0];
				max = cls.numfavoriteservers;
			break;
		}
		for (i = 0; i < max; i++) {
			if (server[i].visible) {
				if (server[i].ping == -1) {
					int j;

					if (slots >= MAX_PINGREQUESTS) {
						break;
					}
					for (j = 0; j < MAX_PINGREQUESTS; j++) {
						if (!cl_pinglist[j].adr.port) {
							continue;
						}
						if (NET_CompareAdr( cl_pinglist[j].adr, server[i].adr)) {
							// already on the list
							break;
						}
					}
					if (j >= MAX_PINGREQUESTS) {
						status = qtrue;
						for (j = 0; j < MAX_PINGREQUESTS; j++) {
							if (!cl_pinglist[j].adr.port) {
								break;
							}
						}
						memcpy(&cl_pinglist[j].adr, &server[i].adr, sizeof(netadr_t));
						cl_pinglist[j].start = cls.realtime;
						cl_pinglist[j].time = 0;
						NET_OutOfBandPrint( NS_CLIENT, cl_pinglist[j].adr, "getinfo xxx" );
						slots++;
					}
				}
				// if the server has a ping higher than cl_maxPing or
				// the ping packet got lost
				else if (server[i].ping == 0) {
					// if we are updating global servers
					if (source == AS_GLOBAL) {
						//
						if ( cls.numGlobalServerAddresses > 0 ) {
							// overwrite this server with one from the additional global servers
							cls.numGlobalServerAddresses--;
							CL_InitServerInfo(&server[i], &cls.globalServerAddresses[cls.numGlobalServerAddresses]);
							// NOTE: the server[i].visible flag stays untouched
						}
					}
				}
			}
		}
	} 

	if (slots) {
		status = qtrue;
	}
	for (i = 0; i < MAX_PINGREQUESTS; i++) {
		if (!cl_pinglist[i].adr.port) {
			continue;
		}
		CL_GetPing( i, buff, MAX_STRING_CHARS, &pingTime );
		if (pingTime != 0) {
			CL_ClearPing(i);
			status = qtrue;
		}
	}

	return status;
}

/*
==================
CL_ServerStatus_f
==================
*/
void CL_ServerStatus_f(void) {
	netadr_t	to;
	char		*server;
	serverStatus_t *serverStatus;

	Com_Memset( &to, 0, sizeof(netadr_t) );

	if ( Cmd_Argc() != 2 ) {
		if ( cls.state != CA_ACTIVE || clc.demoplaying ) {
			Com_Printf ("Not connected to a server.\n");
			Com_Printf( "Usage: serverstatus [server]\n");
			return;	
		}
		server = cls.servername;
	}
	else {
		server = Cmd_Argv(1);
	}

	if ( !NET_StringToAdr( server, &to ) ) {
		return;
	}

	NET_OutOfBandPrint( NS_CLIENT, to, "getstatus" );

	serverStatus = CL_GetServerStatus( to );
	serverStatus->address = to;
	serverStatus->print = qtrue;
	serverStatus->pending = qtrue;
}

/*
==================
CL_ShowIP_f
==================
*/
void CL_ShowIP_f(void) {
	Sys_ShowIP();
}

/*
=================
bool CL_CDKeyValidate
=================
*/
static qboolean CL_CDKeyValidateLegacyValue( const char *key, const char *checksum ) {
	char	ch;
	byte	sum;
	char	chs[3];
	int	i, len;

	if ( !key ) {
		return qfalse;
	}

	len = strlen( key );
	if ( len != CDKEY_LEN ) {
		return qfalse;
	}

	if ( checksum && strlen( checksum ) != CDCHKSUM_LEN ) {
		return qfalse;
	}

	sum = 0;
	for ( i = 0; i < len; i++ ) {
		ch = key[i];
		if ( ch >= 'a' && ch <= 'z' ) {
			ch -= 32;
		}
		switch ( ch ) {
		case '2':
		case '3':
		case '7':
		case 'A':
		case 'B':
		case 'C':
		case 'D':
		case 'G':
		case 'H':
		case 'J':
		case 'L':
		case 'P':
		case 'R':
		case 'S':
		case 'T':
		case 'W':
			sum += ch;
			break;
		default:
			return qfalse;
		}
	}

	sprintf( chs, "%02x", sum );

	if ( checksum && !Q_stricmp( chs, checksum ) ) {
		return qtrue;
	}

	if ( !checksum ) {
		return qtrue;
	}

	return qfalse;
}

qboolean CL_CDKeyValidate( const char *key, const char *checksum ) {
	return CL_CDKeyValidateLegacyValue( key, checksum );
}
