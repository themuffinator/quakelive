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
// cl_cgame.c  -- client system interaction with client game

#include "client.h"
#include "../../common/platform/platform_steamworks.h"

#include "../game/botlib.h"
#include "../qcommon/vm_local.h"
#include "../../common/platform/platform_services.h"
#include "../../common/platform/platform_steamworks.h"
#include "../../../src-re/include/fs_imports.h"
#include <ctype.h>
#include <stdint.h>
#include <stdlib.h>
#ifdef _WIN32
#include <windows.h>
#include "../win32/win_local.h"
#endif

extern	botlib_export_t	*botlib_export;

extern qboolean loadCamera(const char *name);
extern void startCamera(int time);
extern qboolean getCameraInfo(int time, vec3_t *origin, vec3_t *angles);
void R_MirrorPoint( vec3_t in, orientation_t *surface, orientation_t *camera, vec3_t out );
void R_MirrorVector( vec3_t in, orientation_t *surface, orientation_t *camera, vec3_t out );

static qboolean cl_webBrowserVisible = qfalse;
static char cl_webBrowserHash[MAX_STRING_CHARS];

typedef struct {
	qboolean	initialised;
	qboolean	overlayCompiled;
	qboolean	overlayAvailable;
	int			frameTime;
	int			viewWidth;
	int			viewHeight;
	int			activeAdvertCellId;
	int			activatedAdvertCellId;
} clAdvertisementBridgeState_t;

static clAdvertisementBridgeState_t cl_advertisementBridge;

#define CL_ADVERTISEMENT_DEBUG_LABEL_COUNT 2

#define CL_WEB_FRIEND_FLAGS 4
#define CL_WEB_MAX_QZ_METHODS 35
#define CL_WEB_JSON_BUFFER_SIZE 32768
#define CL_WEB_LAUNCHER_SCRIPT_LIST_BUFFER 4096
#define CL_WEB_DEFAULT_URL "asset://ql/index.html"
#define CL_WEB_SURFACE_SHADER "browser"
#define CL_WEB_BOOTSTRAP_MAX_ATTEMPTS 10
#define CL_WEB_BOOTSTRAP_SLEEP_MSEC 100

static qboolean CL_OverlayServiceAvailable( void );

typedef enum {
	CL_WEB_METHOD_IS_PAK_FILE_PRESENT = 0,
	CL_WEB_METHOD_IS_GAME_RUNNING = 1,
	CL_WEB_METHOD_SEND_GAME_COMMAND = 2,
	CL_WEB_METHOD_WRITE_TEXT_FILE = 3,
	CL_WEB_METHOD_GET_CVAR = 4,
	CL_WEB_METHOD_SET_CVAR = 5,
	CL_WEB_METHOD_RESET_CVAR = 6,
	CL_WEB_METHOD_GET_MAP_LIST = 7,
	CL_WEB_METHOD_GET_FACTORY_LIST = 8,
	CL_WEB_METHOD_GET_DEMO_LIST = 9,
	CL_WEB_METHOD_OPEN_URL = 10,
	CL_WEB_METHOD_OPEN_STEAM_OVERLAY_URL = 11,
	CL_WEB_METHOD_GET_CLIPBOARD_TEXT = 12,
	CL_WEB_METHOD_SET_CLIPBOARD_TEXT = 13,
	CL_WEB_METHOD_REQUEST_SERVERS = 14,
	CL_WEB_METHOD_REQUEST_SERVER_DETAILS = 15,
	CL_WEB_METHOD_REFRESH_LIST = 16,
	CL_WEB_METHOD_CREATE_LOBBY = 17,
	CL_WEB_METHOD_LEAVE_LOBBY = 18,
	CL_WEB_METHOD_JOIN_LOBBY = 19,
	CL_WEB_METHOD_SET_LOBBY_SERVER = 20,
	CL_WEB_METHOD_SHOW_INVITE_OVERLAY = 21,
	CL_WEB_METHOD_SAY_LOBBY = 22,
	CL_WEB_METHOD_REQUEST_USER_STATS = 23,
	CL_WEB_METHOD_GET_FRIEND_LIST = 24,
	CL_WEB_METHOD_ACTIVATE_GAME_OVERLAY_TO_USER = 25,
	CL_WEB_METHOD_INVITE = 26,
	CL_WEB_METHOD_FILE_EXISTS = 27,
	CL_WEB_METHOD_GET_CONFIG = 28,
	CL_WEB_METHOD_GET_CURSOR_POSITION = 29,
	CL_WEB_METHOD_NO_OP = 30,
	CL_WEB_METHOD_GET_ALL_UGC = 31,
	CL_WEB_METHOD_GET_NEXT_KEY_DOWN = 32,
	CL_WEB_METHOD_SET_FAVORITE_SERVER = 33
} clWebMethodId_t;

typedef struct {
	const char	*name;
	int			methodId;
	qboolean	returnsValue;
} clWebMethodBinding_t;

typedef struct {
	qboolean	coreInitialised;
	qboolean	sessionInitialised;
	qboolean	viewInitialised;
	qboolean	bootstrapReady;
	qboolean	documentReady;
	qboolean	loadingDocument;
	qboolean	loadFailed;
	qboolean	dataPakSourceInstalled;
	qboolean	steamDataSourceInstalled;
	qboolean	resourceInterceptorInstalled;
	qboolean	jsMethodHandlerInstalled;
	qboolean	dialogHandlerInstalled;
	qboolean	viewHandlerInstalled;
	qboolean	loadHandlerInstalled;
	qboolean	windowObjectBound;
	qboolean	qzInstanceBound;
	qboolean	browserVisible;
	qboolean	browserActive;
	qboolean	refreshStopped;
	qboolean	surfaceImageInitialised;
	qboolean	surfaceDirty;
	qboolean	keyCaptureArmed;
	qboolean	focused;
	qboolean	cursorPositionValid;
	int			viewWidth;
	int			viewHeight;
	int			surfaceWidth;
	int			surfaceHeight;
	int			cursorX;
	int			cursorY;
	int			frameSequence;
	int			bootstrapAttemptCount;
	int			surfaceUploadWidth;
	int			surfaceUploadHeight;
	uint32_t	appId;
	uint32_t	steamIdLow;
	uint32_t	steamIdHigh;
	qhandle_t	surfaceShader;
	byte		*surfaceBuffer;
	int			surfaceBufferLength;
	char		currentUrl[MAX_STRING_CHARS];
	char		currentDocument[MAX_QPATH];
	char		pendingHash[MAX_STRING_CHARS];
	char		playerName[MAX_NAME_LENGTH];
	char		sessionPath[MAX_OSPATH];
	char		surfaceShaderName[MAX_QPATH];
	char		tooltip[MAX_QPATH];
#if defined( _WIN32 )
	HCURSOR		activeCursorHandle;
	HCURSOR		restoreCursorHandle;
	int			activeCursorType;
	qboolean	cursorOverrideActive;
#endif
} clWebHostState_t;

typedef struct {
	char		*buffer;
	size_t		bufferSize;
	int			count;
} clWebJsonBuilder_t;

#define CL_WEB_ARENA_FILE_LIST_BUFFER 4096
#define CL_WEB_MAX_MAPS 128
#define CL_WEB_MAX_FACTORY_DEFINITIONS 256
#define CL_WEB_FACTORY_JSON_STRING 8192

typedef struct {
	const char	*cursor;
	const char	*end;
	const char	*filename;
	int			line;
} clWebFactoryParseState_t;

typedef struct {
	char		id[MAX_QPATH];
	char		title[128];
	char		author[128];
	char		description[1024];
	char		basegt[64];
	char		settingsJson[CL_WEB_FACTORY_JSON_STRING];
} clWebFactoryDefinition_t;

static clWebHostState_t cl_webHost;

static void CL_Web_ClearSessionState( void );
static void CL_WebHost_ClearSurfaceImage( void );
static void CL_WebHost_ClearCursorOverride( void );
static void CL_WebHost_ResolveSessionPath( char *buffer, size_t bufferSize );
static void QLWebView_PublishGameKey( int key );
static void *QLViewHandler_OnChangeCursor( int cursorType );
static void QLViewHandler_OnChangeTooltip( const char *tooltip );
static void QLWebHost_RegisterRuntimeSources( void );
static qboolean QLWebHost_WaitForBootstrapReady( void );
static void QLWebHost_InstallRuntimeListeners( void );
static void QLWebView_WriteSurfacePixels( void );
static qboolean QLWebView_UploadSurfaceImage( void );
void CL_Steam_FormatFriendSummaryJson( const ql_steam_friend_summary_t *summary, char *buffer, size_t bufferSize );

static const clWebMethodBinding_t cl_webMethodBindings[CL_WEB_MAX_QZ_METHODS] = {
	{ "IsPakFilePresent", CL_WEB_METHOD_IS_PAK_FILE_PRESENT, qtrue },
	{ "IsGameRunning", CL_WEB_METHOD_IS_GAME_RUNNING, qtrue },
	{ "SendGameCommand", CL_WEB_METHOD_SEND_GAME_COMMAND, qfalse },
	{ "WriteTextFile", CL_WEB_METHOD_WRITE_TEXT_FILE, qfalse },
	{ "GetCvar", CL_WEB_METHOD_GET_CVAR, qtrue },
	{ "SetCvar", CL_WEB_METHOD_SET_CVAR, qfalse },
	{ "ResetCvar", CL_WEB_METHOD_RESET_CVAR, qfalse },
	{ "GetMapList", CL_WEB_METHOD_GET_MAP_LIST, qtrue },
	{ "GetFactoryList", CL_WEB_METHOD_GET_FACTORY_LIST, qtrue },
	{ "GetDemoList", CL_WEB_METHOD_GET_DEMO_LIST, qtrue },
	{ "OpenURL", CL_WEB_METHOD_OPEN_URL, qfalse },
	{ "OpenSteamOverlayURL", CL_WEB_METHOD_OPEN_STEAM_OVERLAY_URL, qfalse },
	{ "GetClipboardText", CL_WEB_METHOD_GET_CLIPBOARD_TEXT, qtrue },
	{ "SetClipboardText", CL_WEB_METHOD_SET_CLIPBOARD_TEXT, qfalse },
	{ "RequestServers", CL_WEB_METHOD_REQUEST_SERVERS, qfalse },
	{ "RequestServerDetails", CL_WEB_METHOD_REQUEST_SERVER_DETAILS, qfalse },
	{ "RefreshList", CL_WEB_METHOD_REFRESH_LIST, qfalse },
	{ "CreateLobby", CL_WEB_METHOD_CREATE_LOBBY, qfalse },
	{ "LeaveLobby", CL_WEB_METHOD_LEAVE_LOBBY, qfalse },
	{ "JoinLobby", CL_WEB_METHOD_JOIN_LOBBY, qfalse },
	{ "SetLobbyServer", CL_WEB_METHOD_SET_LOBBY_SERVER, qfalse },
	{ "ShowInviteOverlay", CL_WEB_METHOD_SHOW_INVITE_OVERLAY, qfalse },
	{ "SayLobby", CL_WEB_METHOD_SAY_LOBBY, qfalse },
	{ "RequestUserStats", CL_WEB_METHOD_REQUEST_USER_STATS, qfalse },
	{ "GetFriendList", CL_WEB_METHOD_GET_FRIEND_LIST, qtrue },
	{ "ActivateGameOverlayToUser", CL_WEB_METHOD_ACTIVATE_GAME_OVERLAY_TO_USER, qfalse },
	{ "Invite", CL_WEB_METHOD_INVITE, qfalse },
	{ "FileExists", CL_WEB_METHOD_FILE_EXISTS, qtrue },
	{ "GetConfig", CL_WEB_METHOD_GET_CONFIG, qtrue },
	{ "GetCursorPosition", CL_WEB_METHOD_GET_CURSOR_POSITION, qtrue },
	{ "NoOp", CL_WEB_METHOD_NO_OP, qfalse },
	{ "GetAllUGC", CL_WEB_METHOD_GET_ALL_UGC, qfalse },
	{ "GetNextKeyDown", CL_WEB_METHOD_GET_NEXT_KEY_DOWN, qfalse },
	{ "SetFavoriteServer", CL_WEB_METHOD_SET_FAVORITE_SERVER, qfalse },
	{ NULL, 0, qfalse }
};

/*
=============
CL_WebHost_JsonEscape
=============
*/
static void CL_WebHost_JsonEscape( const char *value, char *buffer, size_t bufferSize ) {
	const char	*cursor;
	char		*out;
	char		*limit;

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

		if ( ch == '\n' || ch == '\r' || ch == '\t' ) {
			if ( out + 2 > limit ) {
				break;
			}
			*out++ = '\\';
			*out++ = ( ch == '\n' ) ? 'n' : ( ch == '\r' ) ? 'r' : 't';
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
CL_WebHost_AppendJsonEscaped
=============
*/
static void CL_WebHost_AppendJsonEscaped( char *buffer, size_t bufferSize, const char *value ) {
	char escaped[MAX_STRING_CHARS * 2];

	CL_WebHost_JsonEscape( value ? value : "", escaped, sizeof( escaped ) );
	Q_strcat( buffer, bufferSize, escaped );
}

/*
=============
CL_WebHost_BeginJsonItem
=============
*/
static void CL_WebHost_BeginJsonItem( clWebJsonBuilder_t *builder ) {
	if ( !builder || !builder->buffer ) {
		return;
	}

	if ( builder->count > 0 ) {
		Q_strcat( builder->buffer, builder->bufferSize, "," );
	}
	builder->count++;
}

/*
=============
CL_WebHost_FormatSteamId
=============
*/
static void CL_WebHost_FormatSteamId( uint32_t idLow, uint32_t idHigh, char *buffer, size_t bufferSize ) {
	unsigned long long value;

	value = ( (unsigned long long)idHigh << 32 ) | idLow;
	Com_sprintf( buffer, bufferSize, "%llu", value );
}

/*
=============
CL_WebHost_NormalizeHash
=============
*/
static void CL_WebHost_NormalizeHash( const char *hash, char *buffer, size_t bufferSize ) {
	const char	*cursor;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	cursor = hash ? hash : "";
	while ( *cursor == '#' || *cursor == ' ' || *cursor == '\t' || *cursor == '\r' || *cursor == '\n' ) {
		cursor++;
	}

	Q_strncpyz( buffer, cursor, bufferSize );
}

/*
=============
CL_WebHost_BuildCurrentURL
=============
*/
static void CL_WebHost_BuildCurrentURL( const char *hash, char *buffer, size_t bufferSize ) {
	char normalizedHash[MAX_STRING_CHARS];

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	CL_WebHost_NormalizeHash( hash, normalizedHash, sizeof( normalizedHash ) );
	if ( normalizedHash[0] ) {
		Com_sprintf( buffer, bufferSize, "%s#%s", CL_WEB_DEFAULT_URL, normalizedHash );
		return;
	}

	Q_strncpyz( buffer, CL_WEB_DEFAULT_URL, bufferSize );
}

/*
=============
CL_GetWebHostModeLabel

Returns the overall online-services mode label used by the retained web host.
=============
*/
static const char *CL_GetWebHostModeLabel( void ) {
	return QL_GetOnlineServicesModeLabel();
}

/*
=============
CL_GetWebHostPolicyLabel

Returns the overall online-services policy label used by the retained web host.
=============
*/
static const char *CL_GetWebHostPolicyLabel( void ) {
	return QL_GetOnlineServicesPolicyLabel();
}

/*
=============
CL_GetWebHostMatchmakingServiceDescriptor

Returns the current platform-service descriptor for web-host social exports.
=============
*/
static const ql_platform_feature_descriptor *CL_GetWebHostMatchmakingServiceDescriptor( void ) {
	const ql_platform_service_table *services = QL_GetPlatformServices();

	if ( !services ) {
		return NULL;
	}

	return &services->matchmaking;
}

/*
=============
CL_GetWebHostMatchmakingProviderLabel

Returns the human-readable provider label for web-host social exports.
=============
*/
static const char *CL_GetWebHostMatchmakingProviderLabel( void ) {
	const ql_platform_feature_descriptor *descriptor = CL_GetWebHostMatchmakingServiceDescriptor();

	if ( !descriptor || !descriptor->provider ) {
		return "Unavailable";
	}

	return descriptor->provider;
}

/*
=============
CL_GetWebHostMatchmakingPolicyLabel

Returns the short compatibility policy label for web-host social exports.
=============
*/
static const char *CL_GetWebHostMatchmakingPolicyLabel( void ) {
	return QL_DescribePlatformFeaturePolicy( CL_GetWebHostMatchmakingServiceDescriptor() );
}

/*
=============
CL_GetWebHostWorkshopServiceDescriptor

Returns the current platform-service descriptor for web-host UGC exports.
=============
*/
static const ql_platform_feature_descriptor *CL_GetWebHostWorkshopServiceDescriptor( void ) {
	const ql_platform_service_table *services = QL_GetPlatformServices();

	if ( !services ) {
		return NULL;
	}

	return &services->workshop;
}

/*
=============
CL_GetWebHostWorkshopProviderLabel

Returns the human-readable provider label for web-host UGC exports.
=============
*/
static const char *CL_GetWebHostWorkshopProviderLabel( void ) {
	const ql_platform_feature_descriptor *descriptor = CL_GetWebHostWorkshopServiceDescriptor();

	if ( !descriptor || !descriptor->provider ) {
		return "Unavailable";
	}

	return descriptor->provider;
}

/*
=============
CL_GetWebHostWorkshopPolicyLabel

Returns the short compatibility policy label for web-host UGC exports.
=============
*/
static const char *CL_GetWebHostWorkshopPolicyLabel( void ) {
	return QL_DescribePlatformFeaturePolicy( CL_GetWebHostWorkshopServiceDescriptor() );
}

/*
=============
CL_LogWebHostMatchmakingExportLifecycle

Publishes provider-aware diagnostics whenever the retained web-host social
export lane falls back under the compatibility policy.
=============
*/
static void CL_LogWebHostMatchmakingExportLifecycle( const char *stage, const char *reason ) {
	Com_DPrintf( "Web host matchmaking %s: %s (%s [%s])\n",
		stage ? stage : "export",
		reason ? reason : "Steam social export unavailable for current compatibility lane",
		CL_GetWebHostMatchmakingProviderLabel(),
		CL_GetWebHostMatchmakingPolicyLabel() );
}

/*
=============
CL_LogWebHostWorkshopExportLifecycle

Publishes provider-aware diagnostics whenever the retained web-host UGC export
lane falls back under the compatibility policy.
=============
*/
static void CL_LogWebHostWorkshopExportLifecycle( const char *stage, const char *reason ) {
	Com_DPrintf( "Web host workshop %s: %s (%s [%s])\n",
		stage ? stage : "export",
		reason ? reason : "Steam UGC export unavailable for current compatibility lane",
		CL_GetWebHostWorkshopProviderLabel(),
		CL_GetWebHostWorkshopPolicyLabel() );
}

/*
=============
CL_WebHost_HasSteamIdentity

Returns qtrue when the retained web host can safely query Steam-backed social
and UGC data for the current session.
=============
*/
static qboolean CL_WebHost_HasSteamIdentity( void ) {
	uint32_t steamIdLow;
	uint32_t steamIdHigh;

	if ( !CL_SteamServicesEnabled() ) {
		return qfalse;
	}

	steamIdLow = 0u;
	steamIdHigh = 0u;
	return QL_Steamworks_GetUserSteamID( &steamIdLow, &steamIdHigh );
}

/*
=============
CL_WebHost_RefreshBootstrapProperties
=============
*/
static void CL_WebHost_RefreshBootstrapProperties( void ) {
	char playerName[MAX_NAME_LENGTH];

	cl_webHost.appId = QL_Steamworks_GetAppID();
	cl_webHost.steamIdLow = 0u;
	cl_webHost.steamIdHigh = 0u;
	QL_Steamworks_GetUserSteamID( &cl_webHost.steamIdLow, &cl_webHost.steamIdHigh );

	playerName[0] = '\0';
	if ( !QL_Steamworks_GetPersonaName( playerName, sizeof( playerName ) ) || !playerName[0] ) {
		Cvar_VariableStringBuffer( "name", playerName, sizeof( playerName ) );
	}
	Q_strncpyz( cl_webHost.playerName, playerName, sizeof( cl_webHost.playerName ) );
}

/*
=============
CL_WebHost_ResetRuntime
=============
*/
static void CL_WebHost_ResetRuntime( qboolean clearVisibility ) {
	CL_WebHost_ClearCursorOverride();
	CL_WebHost_ClearSurfaceImage();
	cl_webHost.coreInitialised = qfalse;
	cl_webHost.sessionInitialised = qfalse;
	cl_webHost.viewInitialised = qfalse;
	cl_webHost.bootstrapReady = qfalse;
	cl_webHost.documentReady = qfalse;
	cl_webHost.loadingDocument = qfalse;
	cl_webHost.loadFailed = qfalse;
	cl_webHost.dataPakSourceInstalled = qfalse;
	cl_webHost.steamDataSourceInstalled = qfalse;
	cl_webHost.resourceInterceptorInstalled = qfalse;
	cl_webHost.jsMethodHandlerInstalled = qfalse;
	cl_webHost.dialogHandlerInstalled = qfalse;
	cl_webHost.viewHandlerInstalled = qfalse;
	cl_webHost.loadHandlerInstalled = qfalse;
	cl_webHost.windowObjectBound = qfalse;
	cl_webHost.qzInstanceBound = qfalse;
	cl_webHost.browserActive = qfalse;
	cls.keyCatchers &= ~KEYCATCH_BROWSER;
	cl_webHost.refreshStopped = qfalse;
	cl_webHost.keyCaptureArmed = qfalse;
	cl_webHost.focused = qfalse;
	cl_webHost.cursorPositionValid = qfalse;
	cl_webHost.viewWidth = 0;
	cl_webHost.viewHeight = 0;
	cl_webHost.surfaceWidth = 0;
	cl_webHost.surfaceHeight = 0;
	cl_webHost.cursorX = 0;
	cl_webHost.cursorY = 0;
	cl_webHost.frameSequence = 0;
	cl_webHost.bootstrapAttemptCount = 0;
	cl_webHost.surfaceUploadWidth = 0;
	cl_webHost.surfaceUploadHeight = 0;
	cl_webHost.surfaceShader = 0;
	cl_webHost.currentUrl[0] = '\0';
	cl_webHost.currentDocument[0] = '\0';
	cl_webHost.pendingHash[0] = '\0';
	cl_webHost.tooltip[0] = '\0';
	cl_webHost.sessionPath[0] = '\0';
	cl_webHost.surfaceShaderName[0] = '\0';

	if ( clearVisibility ) {
		cl_webHost.browserVisible = qfalse;
	}
}

/*
=============
CL_WebHost_ClearSurfaceImage
=============
*/
static void CL_WebHost_ClearSurfaceImage( void ) {
	if ( cl_webHost.surfaceBuffer ) {
		Z_Free( cl_webHost.surfaceBuffer );
		cl_webHost.surfaceBuffer = NULL;
	}

	cl_webHost.surfaceBufferLength = 0;
	cl_webHost.surfaceShader = 0;
	cl_webHost.surfaceImageInitialised = qfalse;
	cl_webHost.surfaceDirty = qfalse;
	cl_webHost.surfaceUploadWidth = 0;
	cl_webHost.surfaceUploadHeight = 0;
	cl_webHost.surfaceShaderName[0] = '\0';
}

/*
=============
CL_WebHost_LoadWin32CursorHandle
=============
*/
#if defined( _WIN32 )
static HCURSOR CL_WebHost_LoadWin32CursorHandle( int cursorType ) {
	LPCSTR cursorId;

	switch ( cursorType ) {
		case 1:
			cursorId = IDC_CROSS;
			break;
		case 2:
			cursorId = IDC_HAND;
			break;
		case 3:
			cursorId = IDC_IBEAM;
			break;
		case 4:
			cursorId = IDC_WAIT;
			break;
		case 5:
			cursorId = IDC_HELP;
			break;
		case 7:
			cursorId = IDC_SIZEWE;
			break;
		case 8:
			cursorId = IDC_SIZENS;
			break;
		case 9:
			cursorId = IDC_SIZENESW;
			break;
		case 10:
			cursorId = IDC_SIZENWSE;
			break;
		case 11:
			cursorId = IDC_SIZEALL;
			break;
		case 14:
			cursorId = IDC_NO;
			break;
		default:
			cursorId = IDC_ARROW;
			break;
	}

	return LoadCursorA( NULL, cursorId );
}
#endif

/*
=============
CL_WebHost_ClearCursorOverride
=============
*/
static void CL_WebHost_ClearCursorOverride( void ) {
#if defined( _WIN32 )
	if ( cl_webHost.cursorOverrideActive && cl_webHost.restoreCursorHandle ) {
		SetCursor( cl_webHost.restoreCursorHandle );
	}

	cl_webHost.activeCursorHandle = NULL;
	cl_webHost.restoreCursorHandle = NULL;
	cl_webHost.activeCursorType = 0;
	cl_webHost.cursorOverrideActive = qfalse;
#endif
}

/*
=============
CL_WebHost_ResolveSessionPath
=============
*/
static void CL_WebHost_ResolveSessionPath( char *buffer, size_t bufferSize ) {
	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	Cvar_VariableStringBuffer( "fs_homepath", buffer, bufferSize );
	if ( !buffer[0] ) {
		Q_strncpyz( buffer, ".", bufferSize );
	}
}

/*
=============
QLJSHandler_LookupMethodBinding
=============
*/
static const clWebMethodBinding_t *QLJSHandler_LookupMethodBinding( const char *methodName ) {
	int i;

	if ( !methodName || !methodName[0] ) {
		return NULL;
	}

	for ( i = 0; i < CL_WEB_MAX_QZ_METHODS && cl_webMethodBindings[i].name; i++ ) {
		if ( !Q_stricmp( cl_webMethodBindings[i].name, methodName ) ) {
			return &cl_webMethodBindings[i];
		}
	}

	return NULL;
}

/*
=============
QLJSHandler_BindQzInstance
=============
*/
static void QLJSHandler_BindQzInstance( void ) {
	int i;

	if ( cl_webHost.qzInstanceBound ) {
		return;
	}

	for ( i = 0; i < CL_WEB_MAX_QZ_METHODS && cl_webMethodBindings[i].name; i++ ) {
		(void)cl_webMethodBindings[i].returnsValue;
	}

	CL_WebHost_RefreshBootstrapProperties();
	cl_webHost.qzInstanceBound = qtrue;
	cl_webHost.windowObjectBound = qtrue;
}

/*
=============
QLWebHost_RegisterRuntimeSources
=============
*/
static void QLWebHost_RegisterRuntimeSources( void ) {
	CL_WebHost_ResolveSessionPath( cl_webHost.sessionPath, sizeof( cl_webHost.sessionPath ) );
	cl_webHost.dataPakSourceInstalled = qtrue;
	cl_webHost.steamDataSourceInstalled = qtrue;
	cl_webHost.resourceInterceptorInstalled = qtrue;
}

/*
=============
QLWebHost_WaitForBootstrapReady
=============
*/
static qboolean QLWebHost_WaitForBootstrapReady( void ) {
	int attempt;

	for ( attempt = 0; attempt < CL_WEB_BOOTSTRAP_MAX_ATTEMPTS; attempt++ ) {
		cl_webHost.bootstrapAttemptCount = attempt + 1;
		if ( cl_webHost.sessionInitialised
			&& cl_webHost.viewInitialised
			&& cl_webHost.dataPakSourceInstalled
			&& cl_webHost.steamDataSourceInstalled
			&& cl_webHost.resourceInterceptorInstalled
			&& cl_webHost.jsMethodHandlerInstalled ) {
			cl_webHost.bootstrapReady = qtrue;
			return qtrue;
		}

		NET_Sleep( CL_WEB_BOOTSTRAP_SLEEP_MSEC );
	}

	return qfalse;
}

/*
=============
QLWebHost_InstallRuntimeListeners
=============
*/
static void QLWebHost_InstallRuntimeListeners( void ) {
	cl_webHost.dialogHandlerInstalled = qtrue;
	cl_webHost.viewHandlerInstalled = qtrue;
	cl_webHost.loadHandlerInstalled = qtrue;
}

/*
=============
CL_WebHost_NormalizeDocumentPath
=============
*/
static qboolean CL_WebHost_NormalizeDocumentPath( const char *url, char *buffer, size_t bufferSize ) {
	const char	*pathStart;
	const char	*separator;
	size_t		index;

	if ( !url || !url[0] || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	pathStart = url;
	separator = strstr( url, "://" );
	if ( separator ) {
		pathStart = separator + 3;
		separator = strchr( pathStart, '/' );
		if ( separator ) {
			pathStart = separator + 1;
		}
	}

	while ( *pathStart == '/' || *pathStart == '\\' ) {
		pathStart++;
	}

	for ( index = 0; pathStart[index] && pathStart[index] != '?' && pathStart[index] != '#'; index++ ) {
		char ch;

		if ( index >= bufferSize - 1 ) {
			break;
		}

		ch = pathStart[index];
		buffer[index] = ( ch == '\\' ) ? '/' : ch;
	}
	buffer[index] = '\0';

	if ( !buffer[0] || strstr( buffer, ".." ) || strstr( buffer, "::" ) || strchr( buffer, ':' ) ) {
		return qfalse;
	}

	Q_strlwr( buffer );
	return qtrue;
}

/*
=============
QLLoadHandler_OnBeginLoadingFrame
=============
*/
static void QLLoadHandler_OnBeginLoadingFrame( void ) {
	cl_webHost.loadingDocument = qtrue;
	cl_webHost.loadFailed = qfalse;
	cl_webHost.documentReady = qfalse;
	cl_webHost.surfaceDirty = qtrue;
	if ( cl_webHost.tooltip[0] && cl_webHost.windowObjectBound ) {
		QLViewHandler_OnChangeTooltip( "" );
	} else {
		cl_webHost.tooltip[0] = '\0';
	}
	cl_webHost.windowObjectBound = qfalse;
	cl_webHost.qzInstanceBound = qfalse;
	cl_webHost.currentDocument[0] = '\0';
}

/*
=============
QLLoadHandler_OnFinishLoadingFrame
=============
*/
static void QLLoadHandler_OnFinishLoadingFrame( void ) {
	cl_webHost.loadingDocument = qfalse;
	cl_webHost.surfaceDirty = qtrue;
}

/*
=============
CL_WebHost_PrimeLauncherDocument
=============
*/
static qboolean CL_WebHost_PrimeLauncherDocument( const char *url ) {
	void	*buffer;
	int		length;
	char	documentPath[MAX_QPATH];

	buffer = NULL;
	length = 0;

	if ( !url || !url[0] ) {
		return qfalse;
	}

	if ( !CL_LauncherRequestData( url, &buffer, &length ) ) {
		return qfalse;
	}

	if ( buffer ) {
		Z_Free( buffer );
	}

	if ( CL_WebHost_NormalizeDocumentPath( url, documentPath, sizeof( documentPath ) ) ) {
		Q_strncpyz( cl_webHost.currentDocument, documentPath, sizeof( cl_webHost.currentDocument ) );
	}

	return qtrue;
}

/*
=============
QLLoadHandler_LoadDocumentScripts

Stages the retail launcher js/* bundle through the retained web.pak and
filesystem bridge before the browser object is marked ready.
=============
*/
static void QLLoadHandler_LoadDocumentScripts( void ) {
	char	fileList[CL_WEB_LAUNCHER_SCRIPT_LIST_BUFFER];
	char	scriptPath[MAX_QPATH];
	char	*cursor;
	int	count;
	int	i;

	count = CL_WebPak_GetFileList( "js", ".js", fileList, sizeof( fileList ) );
	cursor = fileList;

	for ( i = 0; i < count && *cursor; i++ ) {
		void	*scriptBuffer;
		int	scriptLength;

		scriptBuffer = NULL;
		scriptLength = 0;

		Com_sprintf( scriptPath, sizeof( scriptPath ), "js/%s", cursor );
		if ( CL_LauncherRequestData( scriptPath, &scriptBuffer, &scriptLength ) && scriptBuffer ) {
			Z_Free( scriptBuffer );
		}

		cursor += strlen( cursor ) + 1;
	}
}

/*
=============
QLLoadHandler_OnDocumentReady
=============
*/
static void QLLoadHandler_OnDocumentReady( void ) {
	QLLoadHandler_LoadDocumentScripts();
	QLJSHandler_BindQzInstance();
	cl_webHost.documentReady = qtrue;
	cl_webHost.surfaceDirty = qtrue;
	QLViewHandler_OnChangeCursor( 0 );
	CL_WebView_PublishEvent( "web.object.ready", NULL );
}

/*
=============
QLLoadHandler_OnFailLoadingFrame
=============
*/
static void QLLoadHandler_OnFailLoadingFrame( const char *url ) {
	char message[MAX_STRING_CHARS];

	cl_webHost.loadingDocument = qfalse;
	cl_webHost.loadFailed = qtrue;
	cl_webHost.documentReady = qfalse;
	if ( cl_webHost.tooltip[0] && cl_webHost.windowObjectBound ) {
		QLViewHandler_OnChangeTooltip( "" );
	}
	cl_webHost.windowObjectBound = qfalse;
	cl_webHost.qzInstanceBound = qfalse;
	cl_webHost.browserVisible = qfalse;
	cl_webHost.browserActive = qfalse;
	cl_webHost.focused = qfalse;
	cl_webHost.currentDocument[0] = '\0';
	cl_webHost.tooltip[0] = '\0';
	cl_webHost.surfaceDirty = qtrue;
	cl_webBrowserVisible = qfalse;
	CL_WebHost_ClearCursorOverride();

	Com_sprintf( message, sizeof( message ), "Failed to load QUAKE LIVE site... %s", url ? url : CL_WEB_DEFAULT_URL );
	Cvar_Set( "web_browserActive", "0" );
	Cvar_Set( "com_errorMessage", message );
	Com_DPrintf( "%s\n", message );
}

/*
=============
QLViewHandler_OnChangeCursor
=============
*/
static void *QLViewHandler_OnChangeCursor( int cursorType ) {
#if defined( _WIN32 )
	HCURSOR cursorHandle;

	if ( !cl_webHost.cursorOverrideActive ) {
		cl_webHost.restoreCursorHandle = GetCursor();
	}

	cursorHandle = CL_WebHost_LoadWin32CursorHandle( cursorType );
	if ( !cursorHandle ) {
		cursorHandle = LoadCursorA( NULL, IDC_ARROW );
	}

	cl_webHost.activeCursorType = cursorType;
	cl_webHost.activeCursorHandle = cursorHandle;
	cl_webHost.cursorOverrideActive = cursorHandle ? qtrue : qfalse;
	if ( cl_webHost.cursorOverrideActive ) {
		SetCursor( cl_webHost.activeCursorHandle );
	}

	return cl_webHost.activeCursorHandle;
#else
	(void)cursorType;
	return NULL;
#endif
}

/*
=============
QLViewHandler_OnChangeTooltip
=============
*/
static void QLViewHandler_OnChangeTooltip( const char *tooltip ) {
	char escapedTooltip[MAX_QPATH * 2];
	char payload[MAX_STRING_CHARS];

	Q_strncpyz( cl_webHost.tooltip, tooltip ? tooltip : "", sizeof( cl_webHost.tooltip ) );
	CL_WebHost_JsonEscape( cl_webHost.tooltip, escapedTooltip, sizeof( escapedTooltip ) );
	Com_sprintf( payload, sizeof( payload ), "{\"tooltip\":\"%s\"}", escapedTooltip );
	CL_WebView_PublishEvent( "web.tooltip", payload );
}

/*
=============
QLViewHandler_OnAddConsoleMessage
=============
*/
static void QLViewHandler_OnAddConsoleMessage( const char *source, int line, const char *message ) {
	if ( !Cvar_VariableIntegerValue( "web_console" ) ) {
		return;
	}

	Com_Printf( "%s:%i: %s\n", source ? source : "", line, message ? message : "" );
}

/*
=============
QLWebView_SetLocationHash
=============
*/
static void QLWebView_SetLocationHash( const char *hash ) {
	CL_WebHost_NormalizeHash( hash, cl_webHost.pendingHash, sizeof( cl_webHost.pendingHash ) );
	CL_WebHost_BuildCurrentURL( cl_webHost.pendingHash, cl_webHost.currentUrl, sizeof( cl_webHost.currentUrl ) );
}

/*
=============
QLWebView_NextPowerOfTwo
=============
*/
static int QLWebView_NextPowerOfTwo( int value ) {
	int result;

	if ( value <= 0 ) {
		return 0;
	}

	for ( result = 1; result < value; result <<= 1 ) {
		/* loop until result is at least value */
	}

	return result;
}

/*
=============
QLWebView_MapCursorCoordinate
=============
*/
static int QLWebView_MapCursorCoordinate( int coordinate, int viewDimension, int surfaceDimension ) {
	int clampedCoordinate;
	int targetDimension;
	double mappedCoordinate;

	clampedCoordinate = coordinate;
	if ( clampedCoordinate < 0 ) {
		clampedCoordinate = 0;
	}

	if ( viewDimension > 0 && clampedCoordinate > viewDimension ) {
		clampedCoordinate = viewDimension;
	}

	targetDimension = surfaceDimension > 0 ? surfaceDimension : viewDimension;
	if ( targetDimension <= 0 || viewDimension <= 0 ) {
		return clampedCoordinate;
	}

	mappedCoordinate = ( (double)clampedCoordinate / (double)viewDimension ) * (double)targetDimension;
	clampedCoordinate = (int)( mappedCoordinate + 0.5 );
	if ( clampedCoordinate < 0 ) {
		clampedCoordinate = 0;
	} else if ( clampedCoordinate > targetDimension ) {
		clampedCoordinate = targetDimension;
	}

	return clampedCoordinate;
}

/*
=============
QLWebView_InjectMappedMouseMove
=============
*/
static void QLWebView_InjectMappedMouseMove( int x, int y ) {
	int cursorX;
	int cursorY;
	int cursorWidth;
	int cursorHeight;

	cursorX = x;
	cursorY = y;
	cursorWidth = cl_webHost.surfaceWidth > 0 ? cl_webHost.surfaceWidth : cl_webHost.viewWidth;
	cursorHeight = cl_webHost.surfaceHeight > 0 ? cl_webHost.surfaceHeight : cl_webHost.viewHeight;

	if ( cursorX < 0 ) {
		cursorX = 0;
	} else if ( cursorWidth > 0 && cursorX > cursorWidth ) {
		cursorX = cursorWidth;
	}

	if ( cursorY < 0 ) {
		cursorY = 0;
	} else if ( cursorHeight > 0 && cursorY > cursorHeight ) {
		cursorY = cursorHeight;
	}

	cl_webHost.cursorX = cursorX;
	cl_webHost.cursorY = cursorY;
	cl_webHost.cursorPositionValid = qtrue;
	cl_webHost.focused = qtrue;
}

/*
=============
QLWebView_Resize
=============
*/
static void QLWebView_Resize( int width, int height ) {
	cl_webHost.viewWidth = width;
	cl_webHost.viewHeight = height;
}

/*
=============
QLWebView_RebuildSurfaceImage
=============
*/
static void QLWebView_RebuildSurfaceImage( void ) {
	cl_webHost.surfaceWidth = QLWebView_NextPowerOfTwo( cl_webHost.viewWidth );
	cl_webHost.surfaceHeight = QLWebView_NextPowerOfTwo( cl_webHost.viewHeight );
	cl_webHost.surfaceDirty = qtrue;
	QLWebView_UploadSurfaceImage();
}

/*
=============
QLWebView_WriteSurfacePixels
=============
*/
static void QLWebView_WriteSurfacePixels( void ) {
	int requiredLength;
	int pixelCount;
	int i;
	byte red;
	byte green;
	byte blue;
	byte alpha;

	requiredLength = cl_webHost.surfaceWidth * cl_webHost.surfaceHeight * 4;
	if ( cl_webHost.surfaceWidth <= 0 || cl_webHost.surfaceHeight <= 0 || requiredLength <= 0 ) {
		CL_WebHost_ClearSurfaceImage();
		return;
	}

	if ( !cl_webHost.surfaceBuffer || cl_webHost.surfaceBufferLength != requiredLength ) {
		if ( cl_webHost.surfaceBuffer ) {
			Z_Free( cl_webHost.surfaceBuffer );
		}

		cl_webHost.surfaceBuffer = Z_Malloc( requiredLength );
		cl_webHost.surfaceBufferLength = requiredLength;
	}

	red = 0x14;
	green = 0x14;
	blue = 0x14;
	alpha = 0xff;

	if ( cl_webHost.loadFailed ) {
		red = 0x6a;
		green = 0x12;
		blue = 0x12;
	} else if ( cl_webHost.loadingDocument ) {
		red = 0x12;
		green = 0x24;
		blue = 0x68;
	} else if ( cl_webHost.documentReady ) {
		red = 0x1f;
		green = 0x1f;
		blue = 0x1f;
	}

	pixelCount = cl_webHost.surfaceWidth * cl_webHost.surfaceHeight;
	for ( i = 0; i < pixelCount; i++ ) {
		int offset = i * 4;

		cl_webHost.surfaceBuffer[offset + 0] = red;
		cl_webHost.surfaceBuffer[offset + 1] = green;
		cl_webHost.surfaceBuffer[offset + 2] = blue;
		cl_webHost.surfaceBuffer[offset + 3] = alpha;
	}

	if ( cl_webHost.surfaceBufferLength >= 16 ) {
		cl_webHost.surfaceBuffer[0] = cl_webHost.dataPakSourceInstalled ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[1] = cl_webHost.steamDataSourceInstalled ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[2] = cl_webHost.resourceInterceptorInstalled ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[3] = 0xff;
		cl_webHost.surfaceBuffer[4] = cl_webHost.jsMethodHandlerInstalled ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[5] = cl_webHost.dialogHandlerInstalled ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[6] = cl_webHost.viewHandlerInstalled ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[7] = 0xff;
		cl_webHost.surfaceBuffer[8] = cl_webHost.loadHandlerInstalled ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[9] = cl_webHost.bootstrapReady ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[10] = cl_webHost.documentReady ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[11] = 0xff;
		cl_webHost.surfaceBuffer[12] = (byte)( cl_webHost.bootstrapAttemptCount & 0xff );
		cl_webHost.surfaceBuffer[13] = 0xff;
		cl_webHost.surfaceBuffer[14] = 0xff;
		cl_webHost.surfaceBuffer[15] = 0xff;
	}
}

/*
=============
QLWebView_UploadSurfaceImage
=============
*/
static qboolean QLWebView_UploadSurfaceImage( void ) {
	if ( !cl_webHost.viewInitialised || cl_webHost.surfaceWidth <= 0 || cl_webHost.surfaceHeight <= 0 ) {
		return qfalse;
	}

	QLWebView_WriteSurfacePixels();
	if ( !cl_webHost.surfaceBuffer || cl_webHost.surfaceBufferLength <= 0 ) {
		return qfalse;
	}

	if ( !cl_webHost.surfaceShaderName[0] ) {
		Q_strncpyz( cl_webHost.surfaceShaderName, CL_WEB_SURFACE_SHADER, sizeof( cl_webHost.surfaceShaderName ) );
	}

	cl_webHost.surfaceShader = CL_RegisterShaderFromRGBA(
		cl_webHost.surfaceShaderName,
		cl_webHost.surfaceBuffer,
		cl_webHost.surfaceWidth,
		cl_webHost.surfaceHeight,
		qfalse
	);
	if ( !cl_webHost.surfaceShader ) {
		return qfalse;
	}

	cl_webHost.surfaceUploadWidth = cl_webHost.surfaceWidth;
	cl_webHost.surfaceUploadHeight = cl_webHost.surfaceHeight;
	cl_webHost.surfaceImageInitialised = qtrue;
	cl_webHost.surfaceDirty = qfalse;
	return qtrue;
}

/*
=============
CL_WebHost_MapMouseButton
=============
*/
static int CL_WebHost_MapMouseButton( int key ) {
	switch ( key ) {
		case K_MOUSE1:
			return 0;

		case K_MOUSE2:
			return 2;

		case K_MOUSE3:
			return 1;

		default:
			return -1;
	}
}

/*
=============
QLWebView_InjectMouseMove
=============
*/
static void QLWebView_InjectMouseMove( int x, int y ) {
	if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {
		return;
	}

	QLWebView_InjectMappedMouseMove(
		QLWebView_MapCursorCoordinate( x, cl_webHost.viewWidth, cl_webHost.surfaceWidth ),
		QLWebView_MapCursorCoordinate( y, cl_webHost.viewHeight, cl_webHost.surfaceHeight )
	);
}

/*
=============
QLWebView_InjectMouseDown
=============
*/
static void QLWebView_InjectMouseDown( int key ) {
	int button;

	if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {
		return;
	}

	button = CL_WebHost_MapMouseButton( key );
	if ( button < 0 ) {
		return;
	}

	if ( cl_webHost.cursorPositionValid ) {
		QLWebView_InjectMappedMouseMove( cl_webHost.cursorX, cl_webHost.cursorY );
	}

	cl_webHost.focused = qtrue;
}

/*
=============
QLWebView_InjectMouseUp
=============
*/
static void QLWebView_InjectMouseUp( int key ) {
	int button;

	if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {
		return;
	}

	button = CL_WebHost_MapMouseButton( key );
	if ( button < 0 ) {
		return;
	}

	cl_webHost.focused = qtrue;
}

/*
=============
QLWebView_InjectMouseWheel
=============
*/
static void QLWebView_InjectMouseWheel( int direction ) {
	if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {
		return;
	}

	if ( direction == 0 ) {
		return;
	}

	cl_webHost.focused = qtrue;
}

/*
=============
QLWebView_InjectKeyboardEvent
=============
*/
static void QLWebView_InjectKeyboardEvent( int key, qboolean down ) {
	if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {
		return;
	}

	if ( !down && cl_webHost.keyCaptureArmed ) {
		QLWebView_PublishGameKey( key );
		cl_webHost.keyCaptureArmed = qfalse;
	}

	if ( down ) {
		cl_webHost.focused = qtrue;
	}
}

/*
=============
QLWebView_InjectActivationKeyboardEvent

Mirrors the retail synthetic modifier-key injection used when the native
window regains focus while a retained browser view exists.
=============
*/
static void QLWebView_InjectActivationKeyboardEvent( void ) {
	if ( !cl_webHost.viewInitialised ) {
		return;
	}

	cl_webHost.focused = qtrue;
	if ( cl_webHost.browserVisible || cl_webHost.browserActive ) {
		QLWebView_InjectKeyboardEvent( 0x11, qtrue );
	}
}

/*
=============
QLWebHost_EnsureRuntime
=============
*/
static qboolean QLWebHost_EnsureRuntime( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	return qfalse;
#else
	if ( !CL_OverlayServiceAvailable() ) {
		return qfalse;
	}

	(void)QLViewHandler_OnAddConsoleMessage;

	if ( !cl_webHost.coreInitialised ) {
		cl_webHost.coreInitialised = qtrue;
		cl_webHost.sessionInitialised = qtrue;
		QLWebHost_RegisterRuntimeSources();
		cl_webHost.viewInitialised = qtrue;
		cl_webHost.jsMethodHandlerInstalled = qtrue;
		if ( !QLWebHost_WaitForBootstrapReady() ) {
			CL_WebHost_ResetRuntime( qfalse );
			return qfalse;
		}
		QLWebHost_InstallRuntimeListeners();
		QLWebView_Resize( cls.glconfig.vidWidth, cls.glconfig.vidHeight );
		QLWebView_RebuildSurfaceImage();
	}

	return qtrue;
#endif
}

/*
=============
QLWebHost_OpenURL
=============
*/
static qboolean QLWebHost_OpenURL( const char *url ) {
	if ( !QLWebHost_EnsureRuntime() ) {
		return qfalse;
	}

	CL_WebHost_RefreshBootstrapProperties();
	Q_strncpyz( cl_webHost.currentUrl, url ? url : CL_WEB_DEFAULT_URL, sizeof( cl_webHost.currentUrl ) );
	cl_webHost.browserVisible = qtrue;
	cl_webHost.browserActive = qtrue;
	cl_webHost.refreshStopped = qfalse;
	cl_webHost.focused = qtrue;
	Cvar_Set( "web_browserActive", "1" );

	QLLoadHandler_OnBeginLoadingFrame();
	if ( CL_WebHost_PrimeLauncherDocument( cl_webHost.currentUrl ) ) {
		QLLoadHandler_OnFinishLoadingFrame();
		QLLoadHandler_OnDocumentReady();
	} else {
		QLLoadHandler_OnFailLoadingFrame( cl_webHost.currentUrl );
	}

	return qtrue;
}

/*
=============
QLWebHost_OpenRelativeURL
=============
*/
static qboolean QLWebHost_OpenRelativeURL( const char *hash ) {
	char url[MAX_STRING_CHARS];

	CL_WebHost_NormalizeHash( hash, cl_webHost.pendingHash, sizeof( cl_webHost.pendingHash ) );
	CL_WebHost_BuildCurrentURL( hash, url, sizeof( url ) );
	return QLWebHost_OpenURL( url );
}

/*
=============
QLWebHost_NavigateOrOpen
=============
*/
static qboolean QLWebHost_NavigateOrOpen( const char *hash ) {
	if ( cl_webHost.viewInitialised && cl_webHost.documentReady && cl_webHost.windowObjectBound ) {
		QLWebView_SetLocationHash( hash );
		cl_webHost.browserVisible = qtrue;
		cl_webHost.browserActive = qtrue;
		cl_webHost.focused = qtrue;
		return qtrue;
	}

	return QLWebHost_OpenRelativeURL( hash );
}

/*
=============
QLWebHost_ReloadView
=============
*/
static void QLWebHost_ReloadView( qboolean ignoreCache ) {
	if ( !cl_webHost.viewInitialised ) {
		return;
	}

	cl_webHost.refreshStopped = qfalse;
	(void)ignoreCache;

	if ( !cl_webHost.currentUrl[0] ) {
		return;
	}

	QLLoadHandler_OnBeginLoadingFrame();
	if ( CL_WebHost_PrimeLauncherDocument( cl_webHost.currentUrl ) ) {
		QLLoadHandler_OnFinishLoadingFrame();
		QLLoadHandler_OnDocumentReady();
	} else {
		QLLoadHandler_OnFailLoadingFrame( cl_webHost.currentUrl );
	}
}

/*
=============
QLWebHost_HideBrowser
=============
*/
static void QLWebHost_HideBrowser( void ) {
	if ( !cl_webHost.coreInitialised || !cl_webHost.viewInitialised || cl_webHost.keyCaptureArmed ) {
		return;
	}

	cl_webBrowserVisible = qfalse;
	cl_webHost.browserVisible = qfalse;
	cl_webHost.browserActive = qfalse;
	cl_webHost.focused = qfalse;
	cl_webHost.surfaceDirty = qtrue;
	Cvar_Set( "web_browserActive", "0" );
	cls.keyCatchers &= ~KEYCATCH_BROWSER;
	CL_WebHost_ClearCursorOverride();
	if ( cgvm ) {
		VM_Call( cgvm, CG_EVENT_HANDLING, CGAME_EVENT_CLOSECOMMANDOVERLAY );
	}
	if ( cl_webHost.tooltip[0] ) {
		QLViewHandler_OnChangeTooltip( "" );
	}
}

/*
=============
CL_WebHost_HideBrowser

Allows the client key dispatcher to close the retained browser host without
exposing the retail-named internal helper outside this owner.
=============
*/
void CL_WebHost_HideBrowser( void ) {
	QLWebHost_HideBrowser();
}

/*
=============
QLWebCore_Update
=============
*/
static void QLWebCore_Update( void ) {
	if ( !cl_webHost.coreInitialised || cl_webHost.refreshStopped ) {
		return;
	}

	if ( cl_webHost.browserActive && !( cls.keyCatchers & KEYCATCH_BROWSER ) ) {
		cls.keyCatchers |= KEYCATCH_BROWSER;
	}

	cl_webHost.frameSequence++;
	if ( cl_webHost.viewInitialised && ( cl_webHost.browserVisible || cl_webHost.browserActive || cl_webHost.loadingDocument ) ) {
		cl_webHost.surfaceDirty = qtrue;
	}
}

/*
=============
QLWebHost_PumpFrame
=============
*/
static void QLWebHost_PumpFrame( void ) {
	if ( !cl_webHost.viewInitialised ) {
		return;
	}

	if ( cl_webHost.viewWidth != cls.glconfig.vidWidth || cl_webHost.viewHeight != cls.glconfig.vidHeight ) {
		QLWebView_Resize( cls.glconfig.vidWidth, cls.glconfig.vidHeight );
		QLWebView_RebuildSurfaceImage();
		return;
	}

	if ( !cl_webHost.surfaceImageInitialised ) {
		QLWebView_RebuildSurfaceImage();
		return;
	}

	if ( cl_webHost.surfaceUploadWidth != cl_webHost.surfaceWidth || cl_webHost.surfaceUploadHeight != cl_webHost.surfaceHeight ) {
		QLWebView_RebuildSurfaceImage();
		return;
	}

	if ( cl_webHost.surfaceDirty ) {
		QLWebView_UploadSurfaceImage();
	}
}

/*
=============
CL_WebHost_JsonAppendDemoCallback
=============
*/
static void CL_WebHost_JsonAppendDemoCallback( clWebJsonBuilder_t *builder, const char *name ) {
	if ( !builder || !builder->buffer || !name || !name[0] ) {
		return;
	}

	CL_WebHost_BeginJsonItem( builder );
	Q_strcat( builder->buffer, builder->bufferSize, "\"" );
	CL_WebHost_AppendJsonEscaped( builder->buffer, builder->bufferSize, name );
	Q_strcat( builder->buffer, builder->bufferSize, "\"" );
}

/*
=============
CL_WebHost_AppendGametypeAvailability
=============
*/
static void CL_WebHost_AppendGametypeAvailability( char *buffer, size_t bufferSize ) {
	int i;

	Q_strcat( buffer, bufferSize, "[" );
	for ( i = 0; i < 13; i++ ) {
		if ( i > 0 ) {
			Q_strcat( buffer, bufferSize, "," );
		}
		Q_strcat( buffer, bufferSize, "0" );
	}
	Q_strcat( buffer, bufferSize, "]" );
}

/*
=============
CL_WebHost_StringListContains
=============
*/
static qboolean CL_WebHost_StringListContains( char seen[][MAX_QPATH], int count, const char *value ) {
	int i;

	if ( !seen || !value || !value[0] ) {
		return qfalse;
	}

	for ( i = 0; i < count; i++ ) {
		if ( !Q_stricmp( seen[i], value ) ) {
			return qtrue;
		}
	}

	return qfalse;
}

/*
=============
CL_WebHost_TypeStringHasToken
=============
*/
static qboolean CL_WebHost_TypeStringHasToken( const char *typeList, const char *token ) {
	char working[1024];
	char *cursor;
	char *parsedToken;

	if ( !typeList || !typeList[0] || !token || !token[0] ) {
		return qfalse;
	}

	Q_strncpyz( working, typeList, sizeof( working ) );
	Q_strlwr( working );

	cursor = working;
	while ( 1 ) {
		parsedToken = COM_ParseExt( &cursor, qfalse );
		if ( !parsedToken[0] ) {
			break;
		}

		if ( !Q_stricmp( parsedToken, token ) ) {
			return qtrue;
		}
	}

	return qfalse;
}

/*
=============
CL_WebHost_ResolveMapTypeBits
=============
*/
static unsigned int CL_WebHost_ResolveMapTypeBits( const char *typeList ) {
	unsigned int typeBits = 0u;

	if ( !typeList || !typeList[0] ) {
		return 1u << GT_FFA;
	}

	if ( CL_WebHost_TypeStringHasToken( typeList, "ffa" ) ) {
		typeBits |= 1u << GT_FFA;
	}
	if ( CL_WebHost_TypeStringHasToken( typeList, "duel" ) || CL_WebHost_TypeStringHasToken( typeList, "tourney" ) ) {
		typeBits |= 1u << GT_TOURNAMENT;
	}
	if ( CL_WebHost_TypeStringHasToken( typeList, "single" ) || CL_WebHost_TypeStringHasToken( typeList, "race" ) ) {
		typeBits |= 1u << GT_SINGLE_PLAYER;
	}
	if ( CL_WebHost_TypeStringHasToken( typeList, "team" ) || CL_WebHost_TypeStringHasToken( typeList, "tdm" ) ) {
		typeBits |= 1u << GT_TEAM;
	}
	if ( CL_WebHost_TypeStringHasToken( typeList, "clanarena" ) || CL_WebHost_TypeStringHasToken( typeList, "ca" ) ) {
		typeBits |= 1u << GT_CLAN_ARENA;
	}
	if ( CL_WebHost_TypeStringHasToken( typeList, "ctf" ) ) {
		typeBits |= 1u << GT_CTF;
	}
	if ( CL_WebHost_TypeStringHasToken( typeList, "oneflag" ) || CL_WebHost_TypeStringHasToken( typeList, "1fctf" ) ) {
		typeBits |= 1u << GT_1FCTF;
	}
	if ( CL_WebHost_TypeStringHasToken( typeList, "overload" ) || CL_WebHost_TypeStringHasToken( typeList, "obelisk" ) || CL_WebHost_TypeStringHasToken( typeList, "ovl" ) ) {
		typeBits |= 1u << GT_OBELISK;
	}
	if ( CL_WebHost_TypeStringHasToken( typeList, "harvester" ) || CL_WebHost_TypeStringHasToken( typeList, "har" ) ) {
		typeBits |= 1u << GT_HARVESTER;
	}
	if ( CL_WebHost_TypeStringHasToken( typeList, "freeze" ) || CL_WebHost_TypeStringHasToken( typeList, "freezetag" ) || CL_WebHost_TypeStringHasToken( typeList, "ft" ) ) {
		typeBits |= 1u << GT_FREEZE;
	}
	if ( CL_WebHost_TypeStringHasToken( typeList, "domination" ) || CL_WebHost_TypeStringHasToken( typeList, "dom" ) ) {
		typeBits |= 1u << GT_DOMINATION;
	}
	if ( CL_WebHost_TypeStringHasToken( typeList, "attackdefend" ) || CL_WebHost_TypeStringHasToken( typeList, "ad" ) ) {
		typeBits |= 1u << GT_ATTACK_DEFEND;
	}
	if ( CL_WebHost_TypeStringHasToken( typeList, "redrover" ) || CL_WebHost_TypeStringHasToken( typeList, "rr" ) ) {
		typeBits |= 1u << GT_RED_ROVER;
	}

	return typeBits ? typeBits : ( 1u << GT_FFA );
}

/*
=============
CL_WebHost_AppendGametypeBitsJson
=============
*/
static void CL_WebHost_AppendGametypeBitsJson( unsigned int typeBits, char *buffer, size_t bufferSize ) {
	int i;

	Q_strcat( buffer, bufferSize, "[" );
	for ( i = 0; i < GT_MAX_GAME_TYPE; i++ ) {
		if ( i > 0 ) {
			Q_strcat( buffer, bufferSize, "," );
		}
		Q_strcat( buffer, bufferSize, ( typeBits & ( 1u << i ) ) ? "1" : "0" );
	}
	Q_strcat( buffer, bufferSize, "]" );
}

/*
=============
CL_WebHost_AppendMapDescriptorJson
=============
*/
static void CL_WebHost_AppendMapDescriptorJson( const char *sysname, const char *name, unsigned int typeBits, char *buffer, size_t bufferSize, int *entryCount ) {
	clWebJsonBuilder_t builder;

	if ( !sysname || !sysname[0] || !buffer || !entryCount ) {
		return;
	}

	builder.buffer = buffer;
	builder.bufferSize = bufferSize;
	builder.count = *entryCount;
	CL_WebHost_BeginJsonItem( &builder );
	Q_strcat( buffer, bufferSize, "{\"sysname\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, sysname );
	Q_strcat( buffer, bufferSize, "\",\"name\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, ( name && name[0] ) ? name : sysname );
	Q_strcat( buffer, bufferSize, "\",\"gametypes\":" );
	CL_WebHost_AppendGametypeBitsJson( typeBits, buffer, bufferSize );
	Q_strcat( buffer, bufferSize, "}" );
	( *entryCount )++;
}

/*
=============
CL_WebHost_ParseArenaInfosToJson
=============
*/
static void CL_WebHost_ParseArenaInfosToJson( char *data, char *buffer, size_t bufferSize, char seenMaps[][MAX_QPATH], int *entryCount ) {
	char		*token;
	char		key[MAX_TOKEN_CHARS];
	char		info[MAX_INFO_STRING];
	char		*cursor;

	if ( !data || !buffer || !entryCount ) {
		return;
	}

	cursor = data;
	while ( 1 ) {
		token = COM_Parse( &cursor );
		if ( !token[0] ) {
			break;
		}
		if ( strcmp( token, "{" ) ) {
			Com_DPrintf( "launcher browser map parser: missing '{' in arena data\n" );
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

		{
			const char	*mapName;
			const char	*longName;
			const char	*typeList;
			unsigned int	typeBits;

			mapName = Info_ValueForKey( info, "map" );
			if ( !mapName[0] || *entryCount >= CL_WEB_MAX_MAPS || CL_WebHost_StringListContains( seenMaps, *entryCount, mapName ) ) {
				continue;
			}

			longName = Info_ValueForKey( info, "longname" );
			typeList = Info_ValueForKey( info, "type" );
			typeBits = CL_WebHost_ResolveMapTypeBits( typeList );
			Q_strncpyz( seenMaps[*entryCount], mapName, MAX_QPATH );
			CL_WebHost_AppendMapDescriptorJson( mapName, longName, typeBits, buffer, bufferSize, entryCount );
		}
	}
}

/*
=============
CL_WebHost_AppendArenasFromFile
=============
*/
static void CL_WebHost_AppendArenasFromFile( const char *filename, char *buffer, size_t bufferSize, char seenMaps[][MAX_QPATH], int *entryCount ) {
	void	*fileBuffer;
	int		length;

	fileBuffer = NULL;
	length = FS_ReadFile( filename, &fileBuffer );
	if ( length <= 0 || !fileBuffer ) {
		return;
	}

	CL_WebHost_ParseArenaInfosToJson( (char *)fileBuffer, buffer, bufferSize, seenMaps, entryCount );
	FS_FreeFile( fileBuffer );
}

/*
=============
CL_WebHost_BuildMapListJsonFromBSPScan
=============
*/
static void CL_WebHost_BuildMapListJsonFromBSPScan( char *buffer, size_t bufferSize ) {
	char fileList[32768];
	char *cursor;
	int count;

	buffer[0] = '\0';
	Q_strcat( buffer, bufferSize, "[" );
	count = FS_GetFileList( "maps", ".bsp", fileList, sizeof( fileList ) );
	cursor = fileList;
	for ( ; count > 0 && *cursor; count-- ) {
		char mapName[MAX_QPATH];
		const char *extension;
		clWebJsonBuilder_t builder;

		Q_strncpyz( mapName, cursor, sizeof( mapName ) );
		extension = strrchr( mapName, '.' );
		if ( extension ) {
			*strrchr( mapName, '.' ) = '\0';
		}

		builder.buffer = buffer;
		builder.bufferSize = bufferSize;
		builder.count = ( buffer[1] != '\0' ) ? 1 : 0;
		CL_WebHost_BeginJsonItem( &builder );
		Q_strcat( buffer, bufferSize, "{\"sysname\":\"" );
		CL_WebHost_AppendJsonEscaped( buffer, bufferSize, mapName );
		Q_strcat( buffer, bufferSize, "\",\"name\":\"" );
		CL_WebHost_AppendJsonEscaped( buffer, bufferSize, mapName );
		Q_strcat( buffer, bufferSize, "\",\"gametypes\":" );
		CL_WebHost_AppendGametypeAvailability( buffer, bufferSize );
		Q_strcat( buffer, bufferSize, "}" );
		cursor += strlen( cursor ) + 1;
	}
	Q_strcat( buffer, bufferSize, "]" );
}

/*
=============
CL_WebHost_BuildMapListJson
=============
*/
static void CL_WebHost_BuildMapListJson( char *buffer, size_t bufferSize ) {
	char	arenasFile[MAX_QPATH];
	char	dirlist[CL_WEB_ARENA_FILE_LIST_BUFFER];
	char	*dirptr;
	char	filename[MAX_QPATH];
	char	seenMaps[CL_WEB_MAX_MAPS][MAX_QPATH];
	int		numdirs;
	int		dirlen;
	int		i;
	int		entryCount;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	Com_Memset( seenMaps, 0, sizeof( seenMaps ) );
	entryCount = 0;
	buffer[0] = '\0';
	Q_strcat( buffer, bufferSize, "[" );

	Cvar_VariableStringBuffer( "g_arenasFile", arenasFile, sizeof( arenasFile ) );
	if ( arenasFile[0] ) {
		CL_WebHost_AppendArenasFromFile( arenasFile, buffer, bufferSize, seenMaps, &entryCount );
	} else {
		CL_WebHost_AppendArenasFromFile( "scripts/arenas.txt", buffer, bufferSize, seenMaps, &entryCount );
	}

	numdirs = FS_GetFileList( "scripts", ".arena", dirlist, sizeof( dirlist ) );
	dirptr = dirlist;
	for ( i = 0; i < numdirs && entryCount < CL_WEB_MAX_MAPS; i++, dirptr += dirlen + 1 ) {
		dirlen = strlen( dirptr );
		if ( dirlen <= 0 ) {
			continue;
		}

		Com_sprintf( filename, sizeof( filename ), "scripts/%s", dirptr );
		CL_WebHost_AppendArenasFromFile( filename, buffer, bufferSize, seenMaps, &entryCount );
	}

	Q_strcat( buffer, bufferSize, "]" );
	if ( entryCount == 0 ) {
		CL_WebHost_BuildMapListJsonFromBSPScan( buffer, bufferSize );
	}
}

/*
=============
CL_WebFactory_ReportParseError
=============
*/
static void CL_WebFactory_ReportParseError( const clWebFactoryParseState_t *state, const char *message ) {
	const char *filename;

	filename = ( state && state->filename && state->filename[0] ) ? state->filename : "<unknown>";
	Com_DPrintf( "launcher browser factory parser: %s:%d: %s\n",
		filename,
		state ? state->line : 0,
		message ? message : "unknown parse error" );
}

/*
=============
CL_WebFactory_SkipWhitespace
=============
*/
static void CL_WebFactory_SkipWhitespace( clWebFactoryParseState_t *state ) {
	if ( !state ) {
		return;
	}

	while ( state->cursor < state->end ) {
		char ch;

		ch = *state->cursor;
		if ( ch == '\n' ) {
			state->line++;
			state->cursor++;
			continue;
		}
		if ( ch == '\r' || ch == '\t' || ch == ' ' ) {
			state->cursor++;
			continue;
		}
		break;
	}
}

/*
=============
CL_WebFactory_ParseExpectedChar
=============
*/
static qboolean CL_WebFactory_ParseExpectedChar( clWebFactoryParseState_t *state, char ch ) {
	CL_WebFactory_SkipWhitespace( state );
	if ( !state || state->cursor >= state->end || *state->cursor != ch ) {
		CL_WebFactory_ReportParseError( state, va( "expected '%c'", ch ) );
		return qfalse;
	}

	state->cursor++;
	return qtrue;
}

/*
=============
CL_WebFactory_SkipJsonString
=============
*/
static qboolean CL_WebFactory_SkipJsonString( clWebFactoryParseState_t *state ) {
	if ( !state ) {
		return qfalse;
	}

	CL_WebFactory_SkipWhitespace( state );
	if ( state->cursor >= state->end || *state->cursor != '"' ) {
		CL_WebFactory_ReportParseError( state, "expected string" );
		return qfalse;
	}

	state->cursor++;
	while ( state->cursor < state->end ) {
		char ch;

		ch = *state->cursor++;
		if ( ch == '"' ) {
			return qtrue;
		}
		if ( ch == '\\' ) {
			if ( state->cursor >= state->end ) {
				break;
			}
			state->cursor++;
			continue;
		}
		if ( ch == '\n' ) {
			state->line++;
		}
	}

	CL_WebFactory_ReportParseError( state, "unterminated string" );
	return qfalse;
}

/*
=============
CL_WebFactory_ParseJsonString
=============
*/
static qboolean CL_WebFactory_ParseJsonString( clWebFactoryParseState_t *state, char *buffer, size_t bufferSize ) {
	size_t length;

	if ( !state || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	CL_WebFactory_SkipWhitespace( state );
	if ( state->cursor >= state->end || *state->cursor != '"' ) {
		CL_WebFactory_ReportParseError( state, "expected string" );
		return qfalse;
	}

	state->cursor++;
	length = 0u;
	while ( state->cursor < state->end ) {
		char ch;

		ch = *state->cursor++;
		if ( ch == '"' ) {
			buffer[length] = '\0';
			return qtrue;
		}

		if ( ch == '\\' ) {
			char escaped;

			if ( state->cursor >= state->end ) {
				break;
			}

			escaped = *state->cursor++;
			switch ( escaped ) {
				case '"': ch = '"'; break;
				case '\\': ch = '\\'; break;
				case '/': ch = '/'; break;
				case 'b': ch = '\b'; break;
				case 'f': ch = '\f'; break;
				case 'n': ch = '\n'; break;
				case 'r': ch = '\r'; break;
				case 't': ch = '\t'; break;
				case 'u': {
					int i;
					int value = 0;

					for ( i = 0; i < 4 && state->cursor < state->end; i++ ) {
						char hex;

						hex = *state->cursor++;
						value <<= 4;
						if ( hex >= '0' && hex <= '9' ) {
							value |= hex - '0';
						} else if ( hex >= 'a' && hex <= 'f' ) {
							value |= 10 + ( hex - 'a' );
						} else if ( hex >= 'A' && hex <= 'F' ) {
							value |= 10 + ( hex - 'A' );
						} else {
							CL_WebFactory_ReportParseError( state, "invalid unicode escape" );
							return qfalse;
						}
					}

					ch = ( value <= 0x7F ) ? (char)value : '?';
					break;
				}
				default:
					CL_WebFactory_ReportParseError( state, "invalid escape" );
					return qfalse;
			}
		}

		if ( ch == '\n' ) {
			state->line++;
		}

		if ( length + 1u < bufferSize ) {
			buffer[length++] = ch;
		}
	}

	CL_WebFactory_ReportParseError( state, "unterminated string" );
	return qfalse;
}

/*
=============
CL_WebFactory_ParseLiteralString
=============
*/
static qboolean CL_WebFactory_ParseLiteralString( clWebFactoryParseState_t *state, char *buffer, size_t bufferSize ) {
	size_t length;

	if ( !state || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	length = 0u;
	CL_WebFactory_SkipWhitespace( state );
	while ( state->cursor < state->end ) {
		char ch;

		ch = *state->cursor;
		if ( ch == ',' || ch == '}' || ch == ']' || ch == '\n' || ch == '\r' || ch == '\t' || ch == ' ' ) {
			break;
		}

		if ( length + 1u < bufferSize ) {
			buffer[length++] = ch;
		}
		state->cursor++;
	}

	buffer[length] = '\0';
	if ( length == 0u ) {
		CL_WebFactory_ReportParseError( state, "expected literal" );
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_WebFactory_ParseValueString
=============
*/
static qboolean CL_WebFactory_ParseValueString( clWebFactoryParseState_t *state, char *buffer, size_t bufferSize ) {
	CL_WebFactory_SkipWhitespace( state );
	if ( !state || state->cursor >= state->end ) {
		CL_WebFactory_ReportParseError( state, "unexpected end of data" );
		return qfalse;
	}

	if ( *state->cursor == '"' ) {
		return CL_WebFactory_ParseJsonString( state, buffer, bufferSize );
	}

	return CL_WebFactory_ParseLiteralString( state, buffer, bufferSize );
}

/*
=============
CL_WebFactory_SkipValue
=============
*/
static qboolean CL_WebFactory_SkipValue( clWebFactoryParseState_t *state ) {
	if ( !state ) {
		return qfalse;
	}

	CL_WebFactory_SkipWhitespace( state );
	if ( state->cursor >= state->end ) {
		CL_WebFactory_ReportParseError( state, "unexpected end of data" );
		return qfalse;
	}

	switch ( *state->cursor ) {
		case '{': {
			int depth = 0;
			do {
				char ch;

				ch = *state->cursor++;
				if ( ch == '{' ) {
					depth++;
				} else if ( ch == '}' ) {
					depth--;
				} else if ( ch == '"' ) {
					state->cursor--;
					if ( !CL_WebFactory_SkipJsonString( state ) ) {
						return qfalse;
					}
					continue;
				}

				if ( ch == '\n' ) {
					state->line++;
				}
			} while ( depth > 0 && state->cursor < state->end );
			if ( depth != 0 ) {
				CL_WebFactory_ReportParseError( state, "unterminated object" );
				return qfalse;
			}
			return qtrue;
		}
		case '[': {
			int depth = 0;
			do {
				char ch;

				ch = *state->cursor++;
				if ( ch == '[' ) {
					depth++;
				} else if ( ch == ']' ) {
					depth--;
				} else if ( ch == '"' ) {
					state->cursor--;
					if ( !CL_WebFactory_SkipJsonString( state ) ) {
						return qfalse;
					}
					continue;
				}

				if ( ch == '\n' ) {
					state->line++;
				}
			} while ( depth > 0 && state->cursor < state->end );
			if ( depth != 0 ) {
				CL_WebFactory_ReportParseError( state, "unterminated array" );
				return qfalse;
			}
			return qtrue;
		}
		case '"':
			return CL_WebFactory_SkipJsonString( state );
		default:
			while ( state->cursor < state->end ) {
				char ch;

				ch = *state->cursor;
				if ( ch == ',' || ch == '}' || ch == ']' || ch == '\n' ) {
					return qtrue;
				}
				state->cursor++;
			}
			return qtrue;
	}
}

/*
=============
CL_WebFactory_ParseSettingsObject
=============
*/
static qboolean CL_WebFactory_ParseSettingsObject( clWebFactoryParseState_t *state, char *buffer, size_t bufferSize ) {
	int entryCount;

	if ( !state || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	Q_strcat( buffer, bufferSize, "{" );
	entryCount = 0;

	if ( !CL_WebFactory_ParseExpectedChar( state, '{' ) ) {
		return qfalse;
	}

	CL_WebFactory_SkipWhitespace( state );
	if ( state->cursor < state->end && *state->cursor == '}' ) {
		state->cursor++;
		Q_strcat( buffer, bufferSize, "}" );
		return qtrue;
	}

	while ( state->cursor < state->end ) {
		char key[128];
		char loweredKey[128];
		char value[MAX_CVAR_VALUE_STRING];

		if ( !CL_WebFactory_ParseJsonString( state, key, sizeof( key ) ) ) {
			return qfalse;
		}
		if ( !CL_WebFactory_ParseExpectedChar( state, ':' ) ) {
			return qfalse;
		}
		if ( !CL_WebFactory_ParseValueString( state, value, sizeof( value ) ) ) {
			return qfalse;
		}

		Q_strncpyz( loweredKey, key, sizeof( loweredKey ) );
		Q_strlwr( loweredKey );
		if ( entryCount > 0 ) {
			Q_strcat( buffer, bufferSize, "," );
		}
		Q_strcat( buffer, bufferSize, "\"" );
		CL_WebHost_AppendJsonEscaped( buffer, bufferSize, loweredKey );
		Q_strcat( buffer, bufferSize, "\":\"" );
		CL_WebHost_AppendJsonEscaped( buffer, bufferSize, value );
		Q_strcat( buffer, bufferSize, "\"" );
		entryCount++;

		CL_WebFactory_SkipWhitespace( state );
		if ( state->cursor >= state->end ) {
			CL_WebFactory_ReportParseError( state, "unterminated cvars object" );
			return qfalse;
		}

		if ( *state->cursor == ',' ) {
			state->cursor++;
			CL_WebFactory_SkipWhitespace( state );
			if ( state->cursor < state->end && *state->cursor == '}' ) {
				state->cursor++;
				Q_strcat( buffer, bufferSize, "}" );
				return qtrue;
			}
			continue;
		}
		if ( *state->cursor == '}' ) {
			state->cursor++;
			Q_strcat( buffer, bufferSize, "}" );
			return qtrue;
		}

		CL_WebFactory_ReportParseError( state, "expected ',' or '}'" );
		return qfalse;
	}

	CL_WebFactory_ReportParseError( state, "unterminated cvars object" );
	return qfalse;
}

/*
=============
CL_WebFactory_ParseDefinition
=============
*/
static qboolean CL_WebFactory_ParseDefinition( clWebFactoryParseState_t *state, clWebFactoryDefinition_t *definition ) {
	qboolean sawTitle;
	qboolean sawCvars;

	if ( !state || !definition ) {
		return qfalse;
	}

	Com_Memset( definition, 0, sizeof( *definition ) );
	Q_strncpyz( definition->settingsJson, "{}", sizeof( definition->settingsJson ) );
	sawTitle = qfalse;
	sawCvars = qfalse;

	if ( !CL_WebFactory_ParseExpectedChar( state, '{' ) ) {
		return qfalse;
	}

	while ( state->cursor < state->end ) {
		char key[64];

		CL_WebFactory_SkipWhitespace( state );
		if ( state->cursor >= state->end ) {
			break;
		}
		if ( *state->cursor == '}' ) {
			state->cursor++;
			break;
		}

		if ( !CL_WebFactory_ParseJsonString( state, key, sizeof( key ) ) ) {
			return qfalse;
		}
		if ( !CL_WebFactory_ParseExpectedChar( state, ':' ) ) {
			return qfalse;
		}

		if ( !Q_stricmp( key, "id" ) ) {
			CL_WebFactory_SkipWhitespace( state );
			if ( state->cursor >= state->end || *state->cursor != '"' ) {
				CL_WebFactory_ReportParseError( state, "factory missing id string" );
				return qfalse;
			}
			if ( !CL_WebFactory_ParseJsonString( state, definition->id, sizeof( definition->id ) ) ) {
				return qfalse;
			}
		} else if ( !Q_stricmp( key, "title" ) ) {
			CL_WebFactory_SkipWhitespace( state );
			if ( state->cursor >= state->end || *state->cursor != '"' ) {
				CL_WebFactory_ReportParseError( state, "factory missing title string" );
				return qfalse;
			}
			if ( !CL_WebFactory_ParseJsonString( state, definition->title, sizeof( definition->title ) ) ) {
				return qfalse;
			}
			sawTitle = qtrue;
		} else if ( !Q_stricmp( key, "author" ) ) {
			CL_WebFactory_SkipWhitespace( state );
			if ( state->cursor == '"' ) {
				if ( !CL_WebFactory_ParseJsonString( state, definition->author, sizeof( definition->author ) ) ) {
					return qfalse;
				}
			} else if ( !CL_WebFactory_SkipValue( state ) ) {
				return qfalse;
			}
		} else if ( !Q_stricmp( key, "description" ) ) {
			CL_WebFactory_SkipWhitespace( state );
			if ( state->cursor == '"' ) {
				if ( !CL_WebFactory_ParseJsonString( state, definition->description, sizeof( definition->description ) ) ) {
					return qfalse;
				}
			} else if ( !CL_WebFactory_SkipValue( state ) ) {
				return qfalse;
			}
		} else if ( !Q_stricmp( key, "basegt" ) ) {
			CL_WebFactory_SkipWhitespace( state );
			if ( state->cursor >= state->end || *state->cursor != '"' ) {
				CL_WebFactory_ReportParseError( state, "factory missing basegt string" );
				return qfalse;
			}
			if ( !CL_WebFactory_ParseJsonString( state, definition->basegt, sizeof( definition->basegt ) ) ) {
				return qfalse;
			}
		} else if ( !Q_stricmp( key, "cvars" ) ) {
			CL_WebFactory_SkipWhitespace( state );
			if ( state->cursor >= state->end || *state->cursor != '{' ) {
				CL_WebFactory_ReportParseError( state, "factory missing cvars object" );
				return qfalse;
			}
			if ( !CL_WebFactory_ParseSettingsObject( state, definition->settingsJson, sizeof( definition->settingsJson ) ) ) {
				return qfalse;
			}
			sawCvars = qtrue;
		} else {
			if ( !CL_WebFactory_SkipValue( state ) ) {
				return qfalse;
			}
		}

		CL_WebFactory_SkipWhitespace( state );
		if ( state->cursor >= state->end ) {
			break;
		}
		if ( *state->cursor == ',' ) {
			state->cursor++;
			CL_WebFactory_SkipWhitespace( state );
			if ( state->cursor < state->end && *state->cursor == '}' ) {
				state->cursor++;
				break;
			}
			continue;
		}
		if ( *state->cursor == '}' ) {
			state->cursor++;
			break;
		}

		CL_WebFactory_ReportParseError( state, "expected ',' or '}'" );
		return qfalse;
	}

	if ( !definition->id[0] || !definition->basegt[0] || !sawTitle || !sawCvars ) {
		CL_WebFactory_ReportParseError( state, "factory missing required fields" );
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_WebHost_AppendFactoryDefinitionJson
=============
*/
static void CL_WebHost_AppendFactoryDefinitionJson( const clWebFactoryDefinition_t *definition, char *buffer, size_t bufferSize, int *entryCount ) {
	clWebJsonBuilder_t builder;

	if ( !definition || !definition->id[0] || !buffer || !entryCount ) {
		return;
	}

	builder.buffer = buffer;
	builder.bufferSize = bufferSize;
	builder.count = *entryCount;
	CL_WebHost_BeginJsonItem( &builder );
	Q_strcat( buffer, bufferSize, "{\"sysname\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, definition->id );
	Q_strcat( buffer, bufferSize, "\",\"title\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, definition->title );
	Q_strcat( buffer, bufferSize, "\",\"basegt\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, definition->basegt );
	Q_strcat( buffer, bufferSize, "\"" );
	if ( definition->author[0] ) {
		Q_strcat( buffer, bufferSize, ",\"author\":\"" );
		CL_WebHost_AppendJsonEscaped( buffer, bufferSize, definition->author );
		Q_strcat( buffer, bufferSize, "\"" );
	}
	if ( definition->description[0] ) {
		Q_strcat( buffer, bufferSize, ",\"description\":\"" );
		CL_WebHost_AppendJsonEscaped( buffer, bufferSize, definition->description );
		Q_strcat( buffer, bufferSize, "\"" );
	}
	Q_strcat( buffer, bufferSize, ",\"settings\":" );
	Q_strcat( buffer, bufferSize, definition->settingsJson[0] ? definition->settingsJson : "{}" );
	Q_strcat( buffer, bufferSize, "}" );
	( *entryCount )++;
}

/*
=============
CL_WebHost_AppendFactoryDefinitionsFromBuffer
=============
*/
static void CL_WebHost_AppendFactoryDefinitionsFromBuffer( const char *filename, char *data, int dataLength, char *buffer, size_t bufferSize, char seenIds[][MAX_QPATH], int *entryCount ) {
	clWebFactoryParseState_t state;

	if ( !data || dataLength <= 0 || !buffer || !seenIds || !entryCount ) {
		return;
	}

	state.cursor = data;
	state.end = data + dataLength;
	state.filename = filename;
	state.line = 1;

	CL_WebFactory_SkipWhitespace( &state );
	if ( state.cursor >= state.end ) {
		return;
	}

	if ( *state.cursor == '{' ) {
		clWebFactoryDefinition_t definition;

		if ( !CL_WebFactory_ParseDefinition( &state, &definition ) ) {
			return;
		}
		if ( !CL_WebHost_StringListContains( seenIds, *entryCount, definition.id ) && *entryCount < CL_WEB_MAX_FACTORY_DEFINITIONS ) {
			Q_strncpyz( seenIds[*entryCount], definition.id, MAX_QPATH );
			CL_WebHost_AppendFactoryDefinitionJson( &definition, buffer, bufferSize, entryCount );
		}
		return;
	}

	if ( !CL_WebFactory_ParseExpectedChar( &state, '[' ) ) {
		return;
	}

	CL_WebFactory_SkipWhitespace( &state );
	if ( state.cursor < state.end && *state.cursor == ']' ) {
		state.cursor++;
		return;
	}

	while ( state.cursor < state.end ) {
		clWebFactoryDefinition_t definition;

		if ( !CL_WebFactory_ParseDefinition( &state, &definition ) ) {
			return;
		}
		if ( !CL_WebHost_StringListContains( seenIds, *entryCount, definition.id ) && *entryCount < CL_WEB_MAX_FACTORY_DEFINITIONS ) {
			Q_strncpyz( seenIds[*entryCount], definition.id, MAX_QPATH );
			CL_WebHost_AppendFactoryDefinitionJson( &definition, buffer, bufferSize, entryCount );
		}

		CL_WebFactory_SkipWhitespace( &state );
		if ( state.cursor >= state.end ) {
			return;
		}
		if ( *state.cursor == ',' ) {
			state.cursor++;
			CL_WebFactory_SkipWhitespace( &state );
			if ( state.cursor < state.end && *state.cursor == ']' ) {
				state.cursor++;
				return;
			}
			continue;
		}
		if ( *state.cursor == ']' ) {
			state.cursor++;
			return;
		}

		CL_WebFactory_ReportParseError( &state, "expected ',' or ']'" );
		return;
	}
}

/*
=============
CL_WebHost_AppendFactoryDefinitionsFromFile
=============
*/
static void CL_WebHost_AppendFactoryDefinitionsFromFile( const char *filename, char *buffer, size_t bufferSize, char seenIds[][MAX_QPATH], int *entryCount ) {
	void	*fileBuffer;
	int		length;

	fileBuffer = NULL;
	length = FS_ReadFile( filename, &fileBuffer );
	if ( length <= 0 || !fileBuffer ) {
		return;
	}

	CL_WebHost_AppendFactoryDefinitionsFromBuffer( filename, (char *)fileBuffer, length, buffer, bufferSize, seenIds, entryCount );
	FS_FreeFile( fileBuffer );
}

/*
=============
CL_WebHost_BuildFactoryListJson
=============
*/
static void CL_WebHost_BuildFactoryListJson( char *buffer, size_t bufferSize ) {
	char fileList[32768];
	char seenIds[CL_WEB_MAX_FACTORY_DEFINITIONS][MAX_QPATH];
	char *cursor;
	int count;
	int entryCount;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	Com_Memset( seenIds, 0, sizeof( seenIds ) );
	entryCount = 0;
	buffer[0] = '\0';
	Q_strcat( buffer, bufferSize, "[" );

	CL_WebHost_AppendFactoryDefinitionsFromFile( "scripts/factories.txt", buffer, bufferSize, seenIds, &entryCount );
	count = FS_GetFileList( "scripts", ".factories", fileList, sizeof( fileList ) );
	cursor = fileList;
	for ( ; count > 0 && *cursor; count-- ) {
		char path[MAX_QPATH];

		Com_sprintf( path, sizeof( path ), "scripts/%s", cursor );
		CL_WebHost_AppendFactoryDefinitionsFromFile( path, buffer, bufferSize, seenIds, &entryCount );
		cursor += strlen( cursor ) + 1;
	}

	count = FS_GetFileList( "scripts", ".factory", fileList, sizeof( fileList ) );
	cursor = fileList;
	for ( ; count > 0 && *cursor; count-- ) {
		char path[MAX_QPATH];

		Com_sprintf( path, sizeof( path ), "scripts/%s", cursor );
		CL_WebHost_AppendFactoryDefinitionsFromFile( path, buffer, bufferSize, seenIds, &entryCount );
		cursor += strlen( cursor ) + 1;
	}

	Q_strcat( buffer, bufferSize, "]" );
}

/*
=============
CL_WebHost_BuildDemoListJson
=============
*/
static void CL_WebHost_BuildDemoListJson( char *buffer, size_t bufferSize ) {
	char fileList[32768];
	char demoExt[32];
	char fullDemoExt[32];
	char *cursor;
	int count;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	Q_strcat( buffer, bufferSize, "[" );
	Com_sprintf( demoExt, sizeof( demoExt ), "dm_%d", PROTOCOL_VERSION );
	Com_sprintf( fullDemoExt, sizeof( fullDemoExt ), ".dm_%d", PROTOCOL_VERSION );
	count = FS_GetFileList( "demos", demoExt, fileList, sizeof( fileList ) );
	cursor = fileList;
	for ( ; count > 0 && *cursor; count-- ) {
		char demoName[MAX_QPATH];
		size_t length;
		clWebJsonBuilder_t builder;

		Q_strncpyz( demoName, cursor, sizeof( demoName ) );
		length = strlen( demoName );
		if ( length > strlen( fullDemoExt ) && !Q_stricmp( demoName + length - strlen( fullDemoExt ), fullDemoExt ) ) {
			demoName[length - strlen( fullDemoExt )] = '\0';
		}

		builder.buffer = buffer;
		builder.bufferSize = bufferSize;
		builder.count = ( buffer[1] != '\0' ) ? 1 : 0;
		CL_WebHost_JsonAppendDemoCallback( &builder, demoName );
		cursor += strlen( cursor ) + 1;
	}
	Q_strcat( buffer, bufferSize, "]" );
}

/*
=============
CL_WebHost_BuildFriendListJson
=============
*/
static void CL_WebHost_BuildFriendListJson( char *buffer, size_t bufferSize ) {
	int friendCount;
	int index;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	Q_strcat( buffer, bufferSize, "[" );

	if ( !CL_WebHost_HasSteamIdentity() ) {
		CL_LogWebHostMatchmakingExportLifecycle( "friend-list", "Steam social export unavailable for current compatibility lane" );
		Q_strcat( buffer, bufferSize, "]" );
		return;
	}

	friendCount = QL_Steamworks_GetFriendCount( CL_WEB_FRIEND_FLAGS );
	for ( index = 0; index < friendCount; index++ ) {
		uint32_t idLow;
		uint32_t idHigh;
		ql_steam_friend_summary_t summary;
		char friendJson[1024];
		clWebJsonBuilder_t builder;

		if ( !QL_Steamworks_GetFriendByIndex( index, CL_WEB_FRIEND_FLAGS, &idLow, &idHigh ) ) {
			continue;
		}
		if ( !QL_Steamworks_GetFriendSummary( idLow, idHigh, &summary ) ) {
			continue;
		}

		CL_Steam_FormatFriendSummaryJson( &summary, friendJson, sizeof( friendJson ) );

		builder.buffer = buffer;
		builder.bufferSize = bufferSize;
		builder.count = ( buffer[1] != '\0' ) ? 1 : 0;
		CL_WebHost_BeginJsonItem( &builder );
		Q_strcat( buffer, bufferSize, friendJson );
	}

	Q_strcat( buffer, bufferSize, "]" );
}

typedef struct {
	char	*buffer;
	size_t	bufferSize;
	int		count;
} clWebConfigArrayContext_t;

/*
=============
CL_WebHost_ConfigCvarCallback
=============
*/
static void CL_WebHost_ConfigCvarCallback( const cvar_t *var, void *userData ) {
	clWebConfigArrayContext_t *context;
	char value[MAX_CVAR_VALUE_STRING];

	context = (clWebConfigArrayContext_t *)userData;
	if ( !var || !context || !context->buffer ) {
		return;
	}

	if ( !var->name || !var->name[0] ) {
		return;
	}

	if ( context->count > 0 ) {
		Q_strcat( context->buffer, context->bufferSize, "," );
	}
	context->count++;

	value[0] = '\0';
	if ( var->latchedString && var->latchedString[0] ) {
		Q_strncpyz( value, var->latchedString, sizeof( value ) );
	} else if ( var->string ) {
		Q_strncpyz( value, var->string, sizeof( value ) );
	}

	Q_strcat( context->buffer, context->bufferSize, "{\"name\":\"" );
	CL_WebHost_AppendJsonEscaped( context->buffer, context->bufferSize, var->name );
	Q_strcat( context->buffer, context->bufferSize, "\",\"value\":\"" );
	CL_WebHost_AppendJsonEscaped( context->buffer, context->bufferSize, value );
	Q_strcat( context->buffer, context->bufferSize, "\",\"flags\":" );
	Q_strcat( context->buffer, context->bufferSize, va( "%d", var->flags ) );
	Q_strcat( context->buffer, context->bufferSize, "}" );
}

/*
=============
CL_WebHost_ConfigBindCallback
=============
*/
static void CL_WebHost_ConfigBindCallback( int keynum, const char *keyName, const char *binding, void *userData ) {
	clWebConfigArrayContext_t *context;

	context = (clWebConfigArrayContext_t *)userData;
	if ( !context || !context->buffer || !binding || !binding[0] ) {
		return;
	}

	if ( context->count > 0 ) {
		Q_strcat( context->buffer, context->bufferSize, "," );
	}
	context->count++;

	Q_strcat( context->buffer, context->bufferSize, "{\"id\":" );
	Q_strcat( context->buffer, context->bufferSize, va( "%d", keynum ) );
	Q_strcat( context->buffer, context->bufferSize, ",\"name\":\"" );
	CL_WebHost_AppendJsonEscaped( context->buffer, context->bufferSize, keyName ? keyName : "" );
	Q_strcat( context->buffer, context->bufferSize, "\",\"value\":\"" );
	CL_WebHost_AppendJsonEscaped( context->buffer, context->bufferSize, binding );
	Q_strcat( context->buffer, context->bufferSize, "\"}" );
}

/*
=============
CL_WebHost_BuildConfigJson
=============
*/
static void CL_WebHost_BuildConfigJson( char *buffer, size_t bufferSize ) {
	char cvarJson[CL_WEB_JSON_BUFFER_SIZE];
	char bindJson[CL_WEB_JSON_BUFFER_SIZE];
	char steamId[32];
	clWebConfigArrayContext_t cvarContext;
	clWebConfigArrayContext_t bindContext;
	const char *onlineServicesMode;
	const char *onlineServicesPolicy;
	const char *matchmakingProvider;
	const char *matchmakingPolicy;
	const char *workshopProvider;
	const char *workshopPolicy;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	CL_WebHost_RefreshBootstrapProperties();
	CL_WebHost_FormatSteamId( cl_webHost.steamIdLow, cl_webHost.steamIdHigh, steamId, sizeof( steamId ) );
	onlineServicesMode = CL_GetWebHostModeLabel();
	onlineServicesPolicy = CL_GetWebHostPolicyLabel();
	matchmakingProvider = CL_GetWebHostMatchmakingProviderLabel();
	matchmakingPolicy = CL_GetWebHostMatchmakingPolicyLabel();
	workshopProvider = CL_GetWebHostWorkshopProviderLabel();
	workshopPolicy = CL_GetWebHostWorkshopPolicyLabel();

	cvarJson[0] = '\0';
	bindJson[0] = '\0';

	cvarContext.buffer = cvarJson;
	cvarContext.bufferSize = sizeof( cvarJson );
	cvarContext.count = 0;
	Cvar_EnumerateVariables( CL_WebHost_ConfigCvarCallback, &cvarContext );

	bindContext.buffer = bindJson;
	bindContext.bufferSize = sizeof( bindJson );
	bindContext.count = 0;
	Key_EnumerateBindings( CL_WebHost_ConfigBindCallback, &bindContext );

	Com_sprintf(
		buffer,
		bufferSize,
		"{\"version\":\"%s\",\"steamId\":\"%s\",\"playerName\":\"",
		Q3_VERSION,
		steamId
	);
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, cl_webHost.playerName );
	Q_strcat( buffer, bufferSize, "\",\"appId\":" );
	Q_strcat( buffer, bufferSize, va( "%u", cl_webHost.appId ) );
	Q_strcat( buffer, bufferSize, ",\"onlineServicesMode\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, onlineServicesMode );
	Q_strcat( buffer, bufferSize, "\",\"onlineServicesPolicy\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, onlineServicesPolicy );
	Q_strcat( buffer, bufferSize, "\",\"matchmakingProvider\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, matchmakingProvider );
	Q_strcat( buffer, bufferSize, "\",\"matchmakingPolicy\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, matchmakingPolicy );
	Q_strcat( buffer, bufferSize, "\",\"workshopProvider\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, workshopProvider );
	Q_strcat( buffer, bufferSize, "\",\"workshopPolicy\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, workshopPolicy );
	Q_strcat( buffer, bufferSize, "\",\"browserVisible\":" );
	Q_strcat( buffer, bufferSize, cl_webHost.browserVisible ? "1" : "0" );
	Q_strcat( buffer, bufferSize, ",\"browserActive\":" );
	Q_strcat( buffer, bufferSize, cl_webHost.browserActive ? "1" : "0" );
	Q_strcat( buffer, bufferSize, ",\"url\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, cl_webHost.currentUrl );
	Q_strcat( buffer, bufferSize, "\",\"cvars\":[" );
	Q_strcat( buffer, bufferSize, cvarJson );
	Q_strcat( buffer, bufferSize, "],\"binds\":[" );
	Q_strcat( buffer, bufferSize, bindJson );
	Q_strcat( buffer, bufferSize, "]}" );
}

/*
=============
CL_WebHost_RequestCursorPosition
=============
*/
static qboolean CL_WebHost_RequestCursorPosition( int *x, int *y ) {
	if ( cl_webHost.cursorPositionValid && cl_webHost.viewInitialised && ( cl_webHost.browserVisible || cl_webHost.browserActive ) ) {
		if ( x ) {
			*x = cl_webHost.cursorX;
		}
		if ( y ) {
			*y = cl_webHost.cursorY;
		}

		return qtrue;
	}

#if defined( _WIN32 )
	POINT point;

	if ( x ) {
		*x = 0;
	}
	if ( y ) {
		*y = 0;
	}

	if ( !GetCursorPos( &point ) ) {
		return qfalse;
	}

	if ( g_wv.hWnd ) {
		ScreenToClient( g_wv.hWnd, &point );
	}

	if ( x ) {
		*x = point.x;
	}
	if ( y ) {
		*y = point.y;
	}

	return qtrue;
#else
	if ( x ) {
		*x = 0;
	}
	if ( y ) {
		*y = 0;
	}
	return qfalse;
#endif
}

/*
=============
CL_WebHost_PathIsSafeRelative
=============
*/
static qboolean CL_WebHost_PathIsSafeRelative( const char *path ) {
	if ( !path || !path[0] ) {
		return qfalse;
	}

	if ( strstr( path, ".." ) || strstr( path, "::" ) || strchr( path, ':' ) ) {
		return qfalse;
	}

	if ( path[0] == '/' || path[0] == '\\' ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_WebHost_WriteTextFile
=============
*/
static qboolean CL_WebHost_WriteTextFile( const char *path, const char *contents ) {
	if ( !CL_WebHost_PathIsSafeRelative( path ) ) {
		return qfalse;
	}

	FS_WriteFile( path, contents ? contents : "", (int)strlen( contents ? contents : "" ) );
	return qtrue;
}

/*
=============
CL_WebHost_BuildFavoriteAddress
=============
*/
static void CL_WebHost_BuildFavoriteAddress( uint32_t ip, uint16_t port, char *buffer, size_t bufferSize ) {
	Com_sprintf(
		buffer,
		bufferSize,
		"%u.%u.%u.%u:%u",
		ip & 0xffu,
		( ip >> 8 ) & 0xffu,
		( ip >> 16 ) & 0xffu,
		( ip >> 24 ) & 0xffu,
		(unsigned int)port
	);
}

/*
=============
CL_WebHost_FindFavoriteServerIndex
=============
*/
static int CL_WebHost_FindFavoriteServerIndex( const netadr_t *address ) {
	int i;

	if ( !address ) {
		return -1;
	}

	for ( i = 0; i < cls.numfavoriteservers; i++ ) {
		if ( NET_CompareAdr( cls.favoriteServers[i].adr, *address ) ) {
			return i;
		}
	}

	return -1;
}

/*
=============
CL_WebHost_MirrorFavoriteServer
=============
*/
static qboolean CL_WebHost_MirrorFavoriteServer( uint32_t ip, uint16_t port, qboolean add ) {
	char addressString[64];
	netadr_t address;
	int index;

	CL_WebHost_BuildFavoriteAddress( ip, port, addressString, sizeof( addressString ) );
	if ( !NET_StringToAdr( addressString, &address ) ) {
		return qfalse;
	}

	index = CL_WebHost_FindFavoriteServerIndex( &address );
	if ( add ) {
		if ( index >= 0 ) {
			return qtrue;
		}
		if ( cls.numfavoriteservers >= MAX_OTHER_SERVERS ) {
			return qfalse;
		}

		index = cls.numfavoriteservers++;
		Com_Memset( &cls.favoriteServers[index], 0, sizeof( cls.favoriteServers[index] ) );
		cls.favoriteServers[index].adr = address;
		cls.favoriteServers[index].visible = qtrue;
		Q_strncpyz( cls.favoriteServers[index].hostName, addressString, sizeof( cls.favoriteServers[index].hostName ) );
		LAN_SaveServersToCache();
		return qtrue;
	}

	if ( index < 0 ) {
		return qfalse;
	}

	for ( ; index < cls.numfavoriteservers - 1; index++ ) {
		Com_Memcpy( &cls.favoriteServers[index], &cls.favoriteServers[index + 1], sizeof( cls.favoriteServers[index] ) );
	}
	cls.numfavoriteservers--;
	LAN_SaveServersToCache();
	return qtrue;
}

/*
=============
CL_WebHost_SetFavoriteServer

Mirrors the retail browser favorite-game owner through Steam matchmaking while
keeping the local favorites cache in sync until the deeper favorites browser
backend is reconstructed in source.
=============
*/
static qboolean CL_WebHost_SetFavoriteServer( uint32_t ip, uint16_t port, qboolean add ) {
	if ( CL_SteamServicesEnabled() && !QL_Steamworks_SetFavoriteServer( ip, port, add ) ) {
		return qfalse;
	}

	return CL_WebHost_MirrorFavoriteServer( ip, port, add );
}

/*
=============
QLWebView_PublishGameKey
=============
*/
static void QLWebView_PublishGameKey( int key ) {
	char payload[128];
	const char *keyName;

	keyName = Key_KeynumToString( key );
	Com_sprintf( payload, sizeof( payload ), "{\"id\":%d,\"key\":\"%s\"}", key, keyName ? keyName : "" );
	CL_WebView_PublishEvent( "game.key", payload );
}

/*
=============
QLJSHandler_CoerceIntegerArgument
=============
*/
static int QLJSHandler_CoerceIntegerArgument( const char *argument ) {
	char *end;
	long value;

	if ( !argument ) {
		return 0;
	}

	value = strtol( argument, &end, 10 );
	if ( end == argument ) {
		return 0;
	}

	while ( *end && isspace( (unsigned char)*end ) ) {
		end++;
	}

	if ( *end ) {
		return 0;
	}

	return (int)value;
}

/*
=============
QLJSHandler_CoerceUnsignedIntegerArgument
=============
*/
static uint32_t QLJSHandler_CoerceUnsignedIntegerArgument( const char *argument ) {
	char *end;
	unsigned long value;

	if ( !argument ) {
		return 0u;
	}

	value = strtoul( argument, &end, 10 );
	if ( end == argument ) {
		return 0u;
	}

	while ( *end && isspace( (unsigned char)*end ) ) {
		end++;
	}

	if ( *end ) {
		return 0u;
	}

	return (uint32_t)value;
}

/*
=============
QLJSHandler_OnMethodCall
=============
*/
static qboolean QLJSHandler_OnMethodCall( const char *methodName, const char **arguments, int argumentCount ) {
	const clWebMethodBinding_t *binding;

	binding = QLJSHandler_LookupMethodBinding( methodName );
	if ( !binding || binding->returnsValue ) {
		return qfalse;
	}

	switch ( binding->methodId ) {
		case CL_WEB_METHOD_SEND_GAME_COMMAND:
			if ( argumentCount > 0 && arguments[0] && arguments[0][0] ) {
				Cbuf_ExecuteText( EXEC_APPEND, va( "%s\n", arguments[0] ) );
				return qtrue;
			}
			return qfalse;

		case CL_WEB_METHOD_WRITE_TEXT_FILE:
			if ( argumentCount < 2 ) {
				return qfalse;
			}
			return CL_WebHost_WriteTextFile( arguments[0], arguments[1] );

		case CL_WEB_METHOD_SET_CVAR:
			if ( argumentCount < 2 || !arguments[0] || !arguments[0][0] ) {
				return qfalse;
			}
			Cvar_Set( arguments[0], arguments[1] ? arguments[1] : "" );
			return qtrue;

		case CL_WEB_METHOD_RESET_CVAR:
			if ( argumentCount < 1 || !arguments[0] || !arguments[0][0] ) {
				return qfalse;
			}
			Cvar_Reset( arguments[0] );
			return qtrue;

		case CL_WEB_METHOD_OPEN_URL:
			if ( argumentCount < 1 || !arguments[0] || !arguments[0][0] ) {
				return qfalse;
			}
			if ( strstr( arguments[0], "://" ) != NULL ) {
				return QLWebHost_OpenURL( arguments[0] );
			}
			return QLWebHost_NavigateOrOpen( arguments[0] );

		case CL_WEB_METHOD_OPEN_STEAM_OVERLAY_URL:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			return CL_Steam_OpenOverlayUrl( arguments[0] );

		case CL_WEB_METHOD_SET_CLIPBOARD_TEXT:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			Sys_SetClipboardData( arguments[0] ? arguments[0] : "" );
			return qtrue;

		case CL_WEB_METHOD_REQUEST_SERVERS:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			return CL_Steam_RequestServers( QLJSHandler_CoerceIntegerArgument( arguments[0] ) );

		case CL_WEB_METHOD_REQUEST_SERVER_DETAILS:
			if ( argumentCount < 2 ) {
				return qfalse;
			}
			return CL_Steam_RequestServerDetails(
				QLJSHandler_CoerceUnsignedIntegerArgument( arguments[0] ),
				(unsigned short)QLJSHandler_CoerceIntegerArgument( arguments[1] )
			);

		case CL_WEB_METHOD_REFRESH_LIST:
			return CL_Steam_RefreshServerList();

		case CL_WEB_METHOD_CREATE_LOBBY:
			return CL_Steam_CreateLobby();

		case CL_WEB_METHOD_LEAVE_LOBBY:
			return CL_Steam_LeaveLobby();

		case CL_WEB_METHOD_JOIN_LOBBY:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			return CL_Steam_JoinLobby( arguments[0] );

		case CL_WEB_METHOD_SET_LOBBY_SERVER:
			if ( argumentCount < 2 ) {
				return qfalse;
			}
			return CL_Steam_SetLobbyServer(
				QLJSHandler_CoerceUnsignedIntegerArgument( arguments[0] ),
				(unsigned short)QLJSHandler_CoerceIntegerArgument( arguments[1] )
			);

		case CL_WEB_METHOD_SHOW_INVITE_OVERLAY:
			return CL_Steam_ShowInviteOverlay();

		case CL_WEB_METHOD_SAY_LOBBY:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			return CL_Steam_SayLobby( arguments[0] ? arguments[0] : "" );

		case CL_WEB_METHOD_REQUEST_USER_STATS:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			return CL_Steam_RequestUserStats( arguments[0] );

		case CL_WEB_METHOD_ACTIVATE_GAME_OVERLAY_TO_USER:
			if ( argumentCount < 2 ) {
				return qfalse;
			}
			return CL_Steam_ActivateOverlayToUser( arguments[0], arguments[1] );

		case CL_WEB_METHOD_INVITE:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			return CL_Steam_Invite( arguments[0] );

		case CL_WEB_METHOD_GET_ALL_UGC:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			return CL_Steam_RequestAllUGC( QLJSHandler_CoerceIntegerArgument( arguments[0] ) );

		case CL_WEB_METHOD_GET_NEXT_KEY_DOWN:
			if ( argumentCount <= 0 ) {
				cl_webHost.keyCaptureArmed = qtrue;
			} else {
				cl_webHost.keyCaptureArmed = QLJSHandler_CoerceIntegerArgument( arguments[0] ) != 0 ? qtrue : qfalse;
			}
			return qtrue;

		case CL_WEB_METHOD_NO_OP:
			return qtrue;

		case CL_WEB_METHOD_SET_FAVORITE_SERVER:
			if ( argumentCount < 3 ) {
				return qfalse;
			}
			return CL_WebHost_SetFavoriteServer(
				QLJSHandler_CoerceUnsignedIntegerArgument( arguments[0] ),
				(uint16_t)QLJSHandler_CoerceIntegerArgument( arguments[1] ),
				QLJSHandler_CoerceIntegerArgument( arguments[2] ) != 0 ? qtrue : qfalse
			);

		default:
			break;
	}

	return qfalse;
}

/*
=============
QLJSHandler_OnMethodCallWithReturnValue
=============
*/
static qboolean QLJSHandler_OnMethodCallWithReturnValue( const char *methodName, const char **arguments, int argumentCount, char *outValue, size_t outValueSize ) {
	const clWebMethodBinding_t *binding;
	char clipboardBuffer[MAX_STRING_CHARS];

	if ( outValue && outValueSize > 0 ) {
		outValue[0] = '\0';
	}

	binding = QLJSHandler_LookupMethodBinding( methodName );
	if ( !binding || !binding->returnsValue || !outValue || outValueSize == 0 ) {
		return qfalse;
	}

	switch ( binding->methodId ) {
		case CL_WEB_METHOD_IS_PAK_FILE_PRESENT:
		case CL_WEB_METHOD_FILE_EXISTS:
			if ( argumentCount < 1 || !arguments[0] || !arguments[0][0] ) {
				Q_strncpyz( outValue, "0", outValueSize );
				return qtrue;
			}
			Q_strncpyz( outValue, FS_FileExists( arguments[0] ) ? "1" : "0", outValueSize );
			return qtrue;

		case CL_WEB_METHOD_IS_GAME_RUNNING:
			Q_strncpyz( outValue, ( cls.state >= CA_CONNECTED && cls.state < CA_CINEMATIC ) ? "1" : "0", outValueSize );
			return qtrue;

		case CL_WEB_METHOD_GET_CVAR:
			if ( argumentCount < 1 || !arguments[0] || !arguments[0][0] ) {
				return qfalse;
			}
			Cvar_VariableStringBuffer( arguments[0], outValue, (int)outValueSize );
			return qtrue;

		case CL_WEB_METHOD_GET_MAP_LIST:
			CL_WebHost_BuildMapListJson( outValue, outValueSize );
			return qtrue;

		case CL_WEB_METHOD_GET_FACTORY_LIST:
			CL_WebHost_BuildFactoryListJson( outValue, outValueSize );
			return qtrue;

		case CL_WEB_METHOD_GET_DEMO_LIST:
			CL_WebHost_BuildDemoListJson( outValue, outValueSize );
			return qtrue;

		case CL_WEB_METHOD_GET_FRIEND_LIST:
			CL_WebHost_BuildFriendListJson( outValue, outValueSize );
			return qtrue;

		case CL_WEB_METHOD_GET_CONFIG:
			CL_WebHost_BuildConfigJson( outValue, outValueSize );
			return qtrue;

		case CL_WEB_METHOD_GET_CURSOR_POSITION:
			{
				int x;
				int y;

				CL_WebHost_RequestCursorPosition( &x, &y );
				Com_sprintf( outValue, outValueSize, "{\"x\":%d,\"y\":%d}", x, y );
				return qtrue;
			}

		case CL_WEB_METHOD_GET_CLIPBOARD_TEXT:
			clipboardBuffer[0] = '\0';
			{
				char *clipboardData;

				clipboardData = Sys_GetClipboardData();
				if ( clipboardData ) {
					Q_strncpyz( clipboardBuffer, clipboardData, sizeof( clipboardBuffer ) );
					Z_Free( clipboardData );
				}
			}
			Q_strncpyz( outValue, clipboardBuffer, outValueSize );
			return qtrue;

		default:
			break;
	}

	return qfalse;
}

/*
=============
CL_ResetBrowserOverlayState

Clears the browser overlay state when the online service bridge is unavailable.
=============
*/
static void CL_ResetBrowserOverlayState( void ) {
	cl_webBrowserVisible = qfalse;
	cl_webBrowserHash[0] = '\0';
	cl_webHost.browserVisible = qfalse;
	cl_webHost.browserActive = qfalse;
	cl_webHost.focused = qfalse;
	CL_WebHost_ClearCursorOverride();
	Cvar_Set( "web_browserActive", "0" );
}

/*
=============
CL_GetOverlayServiceDescriptor

Returns the current platform-service descriptor for the browser overlay seam.
=============
*/
static const ql_platform_feature_descriptor *CL_GetOverlayServiceDescriptor( void ) {
	const ql_platform_service_table *services = QL_GetPlatformServices();

	if ( !services ) {
		return NULL;
	}

	return &services->overlay;
}

/*
=============
CL_GetOverlayServiceProviderLabel

Returns the human-readable provider label for the browser overlay seam.
=============
*/
static const char *CL_GetOverlayServiceProviderLabel( void ) {
	const ql_platform_feature_descriptor *overlay = CL_GetOverlayServiceDescriptor();

	if ( !overlay || !overlay->provider ) {
		return "Unavailable";
	}

	return overlay->provider;
}

/*
=============
CL_GetOverlayServicePolicyLabel

Returns the short compatibility policy label for the browser overlay seam.
=============
*/
static const char *CL_GetOverlayServicePolicyLabel( void ) {
	return QL_DescribePlatformFeaturePolicy( CL_GetOverlayServiceDescriptor() );
}

/*
=============
CL_GetAdvertisementBridgeProviderLabel

Returns the human-readable provider label for the advert bridge seam.
=============
*/
static const char *CL_GetAdvertisementBridgeProviderLabel( void ) {
	return CL_GetOverlayServiceProviderLabel();
}

/*
=============
CL_GetAdvertisementBridgePolicyLabel

Returns the short compatibility policy label for the advert bridge seam.
=============
*/
static const char *CL_GetAdvertisementBridgePolicyLabel( void ) {
	return CL_GetOverlayServicePolicyLabel();
}

/*
=============
CL_LogAdvertisementBridgeLifecycle

Publishes provider-aware diagnostics whenever the retained advert bridge syncs
one of its compatibility-only lifecycle transitions.
=============
*/
static void CL_LogAdvertisementBridgeLifecycle( const char *stage, int cellId ) {
	Com_DPrintf( "Advert bridge %s: cell=%d active=%d activated=%d via %s [%s]\n",
		stage ? stage : "sync",
		cellId,
		cl_advertisementBridge.activeAdvertCellId,
		cl_advertisementBridge.activatedAdvertCellId,
		CL_GetAdvertisementBridgeProviderLabel(),
		CL_GetAdvertisementBridgePolicyLabel() );
}

/*
=============
CL_LogOverlayServiceIgnored

Publishes provider-aware diagnostics whenever a browser overlay command is
blocked by the compatibility-only service policy.
=============
*/
static void CL_LogOverlayServiceIgnored( const char *commandName, const char *reason ) {
	Com_DPrintf( "%s ignored: %s (%s [%s])\n",
		commandName ? commandName : "web",
		reason ? reason : "browser overlay provider unavailable",
		CL_GetOverlayServiceProviderLabel(),
		CL_GetOverlayServicePolicyLabel() );
}

/*
=============
CL_OverlayServiceAvailable

Returns qtrue when an online-services overlay provider is compiled and initialised.
=============
*/
static qboolean CL_OverlayServiceAvailable( void ) {
	const ql_platform_feature_descriptor *overlay = CL_GetOverlayServiceDescriptor();

	return ( overlay && overlay->compiled && overlay->initialised );
}

/*
=============
CL_RefreshOnlineServicesBridgeState

Synchronises client-visible browser and advert bridge state with the platform-service table.
=============
*/
void CL_RefreshOnlineServicesBridgeState( void ) {
	const char *overlayProvider = CL_GetOverlayServiceProviderLabel();
	const char *overlayPolicy = CL_GetOverlayServicePolicyLabel();
	const char *advertProvider = CL_GetAdvertisementBridgeProviderLabel();
	const char *advertPolicy = CL_GetAdvertisementBridgePolicyLabel();

#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	cl_advertisementBridge.overlayCompiled = qfalse;
	cl_advertisementBridge.overlayAvailable = qfalse;
	cl_advertisementBridge.viewWidth = 0;
	cl_advertisementBridge.viewHeight = 0;
	Cvar_Set( "ui_browserAwesomium", "0" );
	Cvar_Set( "ui_browserAwesomiumProvider", overlayProvider );
	Cvar_Set( "ui_browserAwesomiumPolicy", overlayPolicy );
	Cvar_Set( "ui_advertisementBridgeProvider", advertProvider );
	Cvar_Set( "ui_advertisementBridgePolicy", advertPolicy );
	CL_WebHost_ResetRuntime( qtrue );
	CL_ResetBrowserOverlayState();
#else
	const ql_platform_feature_descriptor *overlay = CL_GetOverlayServiceDescriptor();
	qboolean overlayAvailable = CL_OverlayServiceAvailable();

	cl_advertisementBridge.overlayCompiled = ( overlay && overlay->compiled );
	cl_advertisementBridge.overlayAvailable = overlayAvailable;
	cl_advertisementBridge.viewWidth = cls.glconfig.vidWidth;
	cl_advertisementBridge.viewHeight = cls.glconfig.vidHeight;

	Cvar_Set( "ui_browserAwesomium", overlayAvailable ? "1" : "0" );
	Cvar_Set( "ui_browserAwesomiumProvider", overlayProvider );
	Cvar_Set( "ui_browserAwesomiumPolicy", overlayPolicy );
	Cvar_Set( "ui_advertisementBridgeProvider", advertProvider );
	Cvar_Set( "ui_advertisementBridgePolicy", advertPolicy );
	if ( !overlayAvailable ) {
		CL_WebHost_ResetRuntime( qtrue );
		CL_ResetBrowserOverlayState();
	}
#endif
}

/*
=============
CL_AdvertisementBridge_InitUI

Mirrors the retail UI advertisement-bridge init hook.
=============
*/
void CL_AdvertisementBridge_InitUI( void ) {
	CL_RefreshOnlineServicesBridgeState();
	CL_LogAdvertisementBridgeLifecycle( "init-ui", 0 );
}

/*
=============
CL_AdvertisementBridge_ActivateAdvert

Mirrors the retail UI-side advert activation bridge path.
=============
*/
void CL_AdvertisementBridge_ActivateAdvert( int cellId ) {
	cl_advertisementBridge.activatedAdvertCellId = cellId;
	CL_RefreshOnlineServicesBridgeState();
	CL_LogAdvertisementBridgeLifecycle( "activate", cellId );
}

/*
=============
CL_AdvertisementBridge_SetActiveAdvert

Mirrors the retail cgame-side active advert selection/reset helper.
=============
*/
void CL_AdvertisementBridge_SetActiveAdvert( int cellId ) {
	cl_advertisementBridge.activeAdvertCellId = cellId;
	if ( cellId == 0 ) {
		cl_advertisementBridge.activatedAdvertCellId = 0;
	}

	CL_RefreshOnlineServicesBridgeState();
	CL_LogAdvertisementBridgeLifecycle( "set-active", cellId );
}

/*
=============
CL_AdvertisementBridge_ClearLabel

Clears one advert-debug label buffer while preserving the size contract the
renderer-side bridge callbacks expect.
=============
*/
static void CL_AdvertisementBridge_ClearLabel( char *buffer, int bufferSize ) {
	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	buffer[0] = '\0';
}

/*
=============
CL_AdvertisementBridge_GetCellDisplayState

Reconstructs the retained advert-debug palette split from the active and
activated cell ids mirrored through the client bridge.
=============
*/
int CL_AdvertisementBridge_GetCellDisplayState( int cellId ) {
	if ( cellId <= 0 ) {
		return 0;
	}

	if ( cellId == cl_advertisementBridge.activatedAdvertCellId ) {
		return 2;
	}

	if ( cellId == cl_advertisementBridge.activeAdvertCellId ) {
		return 1;
	}

	return 0;
}

/*
=============
CL_AdvertisementBridge_GetCellLabel

Formats one retained advert-debug cell label for the renderer overlay.
=============
*/
void CL_AdvertisementBridge_GetCellLabel( int cellId, char *buffer, int bufferSize ) {
	CL_AdvertisementBridge_ClearLabel( buffer, bufferSize );
	if ( !buffer || bufferSize <= 0 || cellId <= 0 ) {
		return;
	}

	if ( cellId == cl_advertisementBridge.activatedAdvertCellId ) {
		Com_sprintf( buffer, bufferSize, "cell %d activated", cellId );
		return;
	}

	if ( cellId == cl_advertisementBridge.activeAdvertCellId ) {
		Com_sprintf( buffer, bufferSize, "cell %d active", cellId );
		return;
	}

	Com_sprintf( buffer, bufferSize, "cell %d available", cellId );
}

/*
=============
CL_AdvertisementBridge_GetLabelList1Count

Publishes the retained advert-debug summary count for the first label list.
=============
*/
int CL_AdvertisementBridge_GetLabelList1Count( void ) {
	return CL_ADVERTISEMENT_DEBUG_LABEL_COUNT;
}

/*
=============
CL_AdvertisementBridge_GetLabelList1Entry

Publishes provider and overlay-availability diagnostics for the first
renderer-side advert-debug summary list.
=============
*/
void CL_AdvertisementBridge_GetLabelList1Entry( int index, char *buffer, int bufferSize ) {
	CL_AdvertisementBridge_ClearLabel( buffer, bufferSize );
	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	switch ( index ) {
		case 0:
			Com_sprintf( buffer, bufferSize, "bridge: %s [%s]",
				CL_GetAdvertisementBridgeProviderLabel(),
				CL_GetAdvertisementBridgePolicyLabel() );
			break;

		case 1:
			Com_sprintf( buffer, bufferSize, "overlay: compiled=%d available=%d browser=%d",
				cl_advertisementBridge.overlayCompiled ? 1 : 0,
				cl_advertisementBridge.overlayAvailable ? 1 : 0,
				cl_webHost.browserActive ? 1 : 0 );
			break;
	}
}

/*
=============
CL_AdvertisementBridge_GetLabelList2Count

Publishes the retained advert-debug summary count for the second label list.
=============
*/
int CL_AdvertisementBridge_GetLabelList2Count( void ) {
	return CL_ADVERTISEMENT_DEBUG_LABEL_COUNT;
}

/*
=============
CL_AdvertisementBridge_GetLabelList2Entry

Publishes frame, view, and active-cell diagnostics for the second renderer-side
advert-debug summary list.
=============
*/
void CL_AdvertisementBridge_GetLabelList2Entry( int index, char *buffer, int bufferSize ) {
	CL_AdvertisementBridge_ClearLabel( buffer, bufferSize );
	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	switch ( index ) {
		case 0:
			Com_sprintf( buffer, bufferSize, "state: %s frame=%d view=%dx%d",
				cl_advertisementBridge.initialised ? "active" : "idle",
				cl_advertisementBridge.frameTime,
				cl_advertisementBridge.viewWidth,
				cl_advertisementBridge.viewHeight );
			break;

		case 1:
			Com_sprintf( buffer, bufferSize, "active=%d activated=%d",
				cl_advertisementBridge.activeAdvertCellId,
				cl_advertisementBridge.activatedAdvertCellId );
			break;
	}
}

/*
=============
CL_Web_ShowBrowser_f

Marks the browser overlay as visible and records an optional hash target.
=============
*/
void CL_Web_ShowBrowser_f( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	CL_ResetBrowserOverlayState();
	CL_LogOverlayServiceIgnored( "web_showBrowser", "online services disabled by build settings" );
	return;
#else
	CL_RefreshOnlineServicesBridgeState();
	if ( !CL_OverlayServiceAvailable() ) {
		CL_LogOverlayServiceIgnored( "web_showBrowser", "browser overlay provider unavailable" );
		return;
	}

	cl_webBrowserVisible = qtrue;
	if ( Cmd_Argc() > 1 ) {
		const char *hash = Cmd_ArgsFrom( 1 );
		CL_WebHost_NormalizeHash( hash, cl_webBrowserHash, sizeof( cl_webBrowserHash ) );
	} else {
		cl_webBrowserHash[0] = '\0';
	}
	QLWebHost_NavigateOrOpen( cl_webBrowserHash );
#endif
}

/*
=============
CL_Web_ChangeHash_f

Updates the browser target and ensures the overlay remains visible.
=============
*/
void CL_Web_ChangeHash_f( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	CL_ResetBrowserOverlayState();
	CL_LogOverlayServiceIgnored( "web_changeHash", "online services disabled by build settings" );
	return;
#else
	CL_RefreshOnlineServicesBridgeState();
	if ( !CL_OverlayServiceAvailable() ) {
		CL_LogOverlayServiceIgnored( "web_changeHash", "browser overlay provider unavailable" );
		return;
	}

	const char *hash = ( Cmd_Argc() > 1 ) ? Cmd_ArgsFrom( 1 ) : "";
	CL_WebHost_NormalizeHash( hash, cl_webBrowserHash, sizeof( cl_webBrowserHash ) );
	cl_webBrowserVisible = qtrue;
	QLWebHost_NavigateOrOpen( cl_webBrowserHash );
#endif
}

/*
=============
CL_Web_BrowserActive_f

Toggles the browser overlay active state used by the UI VM.
=============
*/
void CL_Web_BrowserActive_f( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	CL_ResetBrowserOverlayState();
	CL_LogOverlayServiceIgnored( "web_browserActive", "online services disabled by build settings" );
	return;
#else
	CL_RefreshOnlineServicesBridgeState();
	if ( !CL_OverlayServiceAvailable() ) {
		CL_LogOverlayServiceIgnored( "web_browserActive", "browser overlay provider unavailable" );
		return;
	}

	qboolean active = ( Cmd_Argc() > 1 && atoi( Cmd_Argv( 1 ) ) != 0 );

	cl_webBrowserVisible = active;
	if ( active ) {
		QLWebHost_NavigateOrOpen( cl_webBrowserHash );
	} else {
		QLWebHost_HideBrowser();
	}
	Cvar_Set( "web_browserActive", cl_webHost.browserActive ? "1" : "0" );
	Com_DPrintf( "web_browserActive %s\n", cl_webHost.browserActive ? "1" : "0" );
#endif
}

/*
=============
CL_Web_HideBrowser_f

Hides the browser overlay and clears the active cvar latch.
=============
*/
void CL_Web_HideBrowser_f( void ) {
	QLWebHost_HideBrowser();
}

/*
=============
CL_Web_ClearSessionState

Clears the retained URI cache layer that stands in for the retail browser
session cache.
=============
*/
static void CL_Web_ClearSessionState( void ) {
	CL_ClearSteamResourceCache( qtrue );
}

/*
=============
CL_Web_ShowError_f

Publishes a browser error through the fallback error state when no live host bridge exists.
=============
*/
void CL_Web_ShowError_f( void ) {
	const char *message = ( Cmd_Argc() > 1 ) ? Cmd_Argv( 1 ) : "";

	if ( !message ) {
		message = "";
	}

	Cvar_Set( "com_errorMessage", message );
	CL_WebView_PublishGameError( message );
}

/*
=============
CL_Web_ClearCache_f

Keeps the retail browser cache-clear command wired into the retained session-cache seam.
=============
*/
void CL_Web_ClearCache_f( void ) {
	if ( !cl_webHost.sessionInitialised ) {
		return;
	}

	CL_Web_ClearSessionState();
}

/*
=============
CL_Web_Reload_f

Keeps the retail browser reload command wired into the host/browser seam.
=============
*/
void CL_Web_Reload_f( void ) {
	if ( !cl_webHost.viewInitialised ) {
		return;
	}

	CL_Web_ClearSessionState();
	QLWebHost_ReloadView( qtrue );
}

/*
=============
QLWebHost_RegisterCommands

Restores the retail browser-host command-registration helper used by CL_Init.
=============
*/
void QLWebHost_RegisterCommands( void ) {
	Cmd_AddCommand ("web_showBrowser", CL_Web_ShowBrowser_f );
	Cmd_AddCommand ("web_changeHash", CL_Web_ChangeHash_f );
	Cmd_AddCommand ("web_hideBrowser", CL_Web_HideBrowser_f );
	Cmd_AddCommand ("web_showError", CL_Web_ShowError_f );
	Cmd_AddCommand ("web_clearCache", CL_Web_ClearCache_f );
	Cmd_AddCommand ("web_reload", CL_Web_Reload_f );
	Cvar_Get ("web_zoom", "100", CVAR_ARCHIVE );
	Cvar_Get ("web_console", "0", CVAR_ARCHIVE );
	Cvar_Get ("web_browserActive", "0", CVAR_ROM );
}

/*
=============
CL_Web_StopRefresh_f

Handles Awesomium refresh-stop requests when an overlay provider is active.
=============
*/
void CL_Web_StopRefresh_f( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	CL_LogOverlayServiceIgnored( "web_stopRefresh", "online services disabled by build settings" );
	return;
#else
	CL_RefreshOnlineServicesBridgeState();
	if ( !CL_OverlayServiceAvailable() ) {
		CL_LogOverlayServiceIgnored( "web_stopRefresh", "browser overlay provider unavailable" );
		return;
	}

	cl_webHost.refreshStopped = qtrue;
	Com_DPrintf( "web_stopRefresh\n" );
#endif
}

/*
=============
CL_WebHost_Init

Initialises the retained browser-host shim from the client owner state.
=============
*/
void CL_WebHost_Init( void ) {
	cl_webBrowserVisible = qfalse;
	cl_webBrowserHash[0] = '\0';
	CL_WebHost_ResetRuntime( qtrue );
	CL_RefreshOnlineServicesBridgeState();
}

/*
=============
CL_WebHost_Shutdown

Releases the retained browser-host shim and clears the client-visible state.
=============
*/
void CL_WebHost_Shutdown( void ) {
	QLWebHost_HideBrowser();
	CL_Web_ClearSessionState();
	CL_WebHost_ResetRuntime( qtrue );
	CL_ResetBrowserOverlayState();
}

/*
=============
CL_WebHost_Frame

Pumps the retained browser-host shim so the overlay-facing state stays in sync.
=============
*/
void CL_WebHost_Frame( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	CL_WebHost_ResetRuntime( qtrue );
	return;
#else
	CL_RefreshOnlineServicesBridgeState();
	if ( !CL_OverlayServiceAvailable() ) {
		CL_WebHost_ResetRuntime( qtrue );
		return;
	}

	if ( cl_webBrowserVisible ) {
		char expectedUrl[MAX_STRING_CHARS];

		CL_WebHost_BuildCurrentURL( cl_webBrowserHash, expectedUrl, sizeof( expectedUrl ) );
		if ( !cl_webHost.viewInitialised ) {
			if ( cl_webBrowserHash[0] ) {
				QLWebHost_OpenRelativeURL( cl_webBrowserHash );
			} else {
				QLWebHost_OpenURL( CL_WEB_DEFAULT_URL );
			}
		} else if ( Q_stricmp( cl_webHost.currentUrl, expectedUrl ) ) {
			QLWebHost_NavigateOrOpen( cl_webBrowserHash );
		} else {
			cl_webHost.browserVisible = qtrue;
			cl_webHost.browserActive = qtrue;
			cl_webHost.focused = qtrue;
		}

		Cvar_Set( "web_browserActive", cl_webHost.browserActive ? "1" : "0" );
	} else if ( cl_webHost.browserVisible || cl_webHost.browserActive ) {
		QLWebHost_HideBrowser();
		Cvar_Set( "web_browserActive", "0" );
	}

	QLWebCore_Update();
	QLWebHost_PumpFrame();
#endif
}

/*
=============
CL_WebHost_HasLiveView

Reports whether the retained browser host owns an active view surface.
=============
*/
qboolean CL_WebHost_HasLiveView( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	return qfalse;
#else
	if ( !CL_OverlayServiceAvailable() ) {
		return qfalse;
	}

	return cl_webHost.viewInitialised && cl_webHost.bootstrapReady;
#endif
}

/*
=============
CL_WebHost_HasBoundWindowObject

Reports whether the retained browser host published the qz window object.
=============
*/
qboolean CL_WebHost_HasBoundWindowObject( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	return qfalse;
#else
	if ( !CL_OverlayServiceAvailable() ) {
		return qfalse;
	}

	return cl_webHost.windowObjectBound;
#endif
}

/*
=============
CL_WebHost_GetCursorHandle

Returns the active Win32 browser cursor override when the retained host owns one.
=============
*/
void *CL_WebHost_GetCursorHandle( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES || !defined( _WIN32 )
	return NULL;
#else
	if ( !CL_OverlayServiceAvailable() ) {
		return NULL;
	}

	if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {
		return NULL;
	}

	if ( !cl_webHost.cursorOverrideActive || !cl_webHost.activeCursorHandle ) {
		return NULL;
	}

	return cl_webHost.activeCursorHandle;
#endif
}

/*
=============
CL_WebHost_NotifyAppActivation

Mirrors retail Win32 app-activation changes into the retained browser host.
=============
*/
void CL_WebHost_NotifyAppActivation( qboolean active ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	(void)active;
	return;
#else
	if ( !CL_OverlayServiceAvailable() ) {
		return;
	}

	if ( !active ) {
		cl_webHost.focused = qfalse;
		return;
	}

	QLWebView_InjectActivationKeyboardEvent();
#endif
}

/*
=============
CL_WebView_OnMouseMove

Records browser-directed mouse motion for the retained host-text/browser seam.
=============
*/
void CL_WebView_OnMouseMove( int x, int y ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	(void)x;
	(void)y;
	return;
#else
	if ( !CL_OverlayServiceAvailable() ) {
		return;
	}

	QLWebView_InjectMouseMove( x, y );
#endif
}

/*
=============
CL_WebView_OnMouseButtonEvent

Records browser-directed mouse button activity for the retained host-text/browser seam.
=============
*/
void CL_WebView_OnMouseButtonEvent( int key, qboolean down ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	(void)key;
	(void)down;
	return;
#else
	if ( !CL_OverlayServiceAvailable() ) {
		return;
	}

	if ( down ) {
		QLWebView_InjectMouseDown( key );
	} else {
		QLWebView_InjectMouseUp( key );
	}
#endif
}

/*
=============
CL_WebView_OnMouseWheelEvent

Records browser-directed mouse wheel activity for the retained host-text/browser seam.
=============
*/
void CL_WebView_OnMouseWheelEvent( int direction ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	(void)direction;
	return;
#else
	if ( !CL_OverlayServiceAvailable() ) {
		return;
	}

	QLWebView_InjectMouseWheel( direction );
#endif
}

/*
=============
CL_WebView_OnKeyEvent

Records browser-directed key activity for the retained host-text/browser seam.
=============
*/
void CL_WebView_OnKeyEvent( int key, qboolean down ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	(void)key;
	(void)down;
	return;
#else
	if ( !CL_OverlayServiceAvailable() ) {
		return;
	}

	QLWebView_InjectKeyboardEvent( key, down );
#endif
}

/*
====================
CL_AdvertisementBridge_InitCGame

Bridges the retail cgame advert lifecycle into the host when available.
====================
*/
static void CL_AdvertisementBridge_InitCGame( void ) {
	cl_advertisementBridge.initialised = qtrue;
	cl_advertisementBridge.frameTime = 0;
	cl_advertisementBridge.activeAdvertCellId = 0;
	CL_RefreshOnlineServicesBridgeState();
}

/*
====================
CL_AdvertisementBridge_ShutdownCGame

Tears down the retail cgame advert lifecycle bridge when a host exists.
====================
*/
static void CL_AdvertisementBridge_ShutdownCGame( void ) {
	cl_advertisementBridge.initialised = qfalse;
	cl_advertisementBridge.frameTime = 0;
	cl_advertisementBridge.activeAdvertCellId = 0;
	cl_advertisementBridge.activatedAdvertCellId = 0;
	CL_RefreshOnlineServicesBridgeState();
	CL_LogAdvertisementBridgeLifecycle( "shutdown-cgame", 0 );
}

/*
====================
CL_AdvertisementBridge_RefreshLoadingViewParameters

Mirrors the retail loading-text bridge tail when a host implementation exists.
====================
*/
void CL_AdvertisementBridge_RefreshLoadingViewParameters( void ) {
	if ( !cl_advertisementBridge.initialised ) {
		return;
	}

	CL_RefreshOnlineServicesBridgeState();
}

/*
====================
CL_AdvertisementBridge_UpdateLoadingViewParameters

Routes the loading-view update through the retail renderer export slot when available.
====================
*/
void CL_AdvertisementBridge_UpdateLoadingViewParameters( void ) {
	if ( re.AdvertisementBridge_UpdateLoadingViewParameters ) {
		re.AdvertisementBridge_UpdateLoadingViewParameters();
		return;
	}

	CL_AdvertisementBridge_RefreshLoadingViewParameters();
}

/*
====================
CL_AdvertisementBridge_SetFrameTime

Mirrors the retail frame-time update used by the loading-screen bridge tail.
====================
*/
static void CL_AdvertisementBridge_SetFrameTime( int frameTime ) {
	if ( !cl_advertisementBridge.initialised ) {
		return;
	}

	cl_advertisementBridge.frameTime = frameTime;
	CL_RefreshOnlineServicesBridgeState();
}

/*
====================
CL_GetGameState
====================
*/
void CL_GetGameState( gameState_t *gs ) {
	*gs = cl.gameState;
}

/*
====================
CL_GetGlconfig
====================
*/
void CL_GetGlconfig( glconfig_t *glconfig ) {
	*glconfig = cls.glconfig;
}


/*
====================
CL_GetUserCmd
====================
*/
qboolean CL_GetUserCmd( int cmdNumber, usercmd_t *ucmd ) {
	// cmds[cmdNumber] is the last properly generated command

	// can't return anything that we haven't created yet
	if ( cmdNumber > cl.cmdNumber ) {
		Com_Error( ERR_DROP, "CL_GetUserCmd: %i >= %i", cmdNumber, cl.cmdNumber );
	}

	// the usercmd has been overwritten in the wrapping
	// buffer because it is too far out of date
	if ( cmdNumber <= cl.cmdNumber - CMD_BACKUP ) {
		return qfalse;
	}

	*ucmd = cl.cmds[ cmdNumber & CMD_MASK ];

	return qtrue;
}

int CL_GetCurrentCmdNumber( void ) {
	return cl.cmdNumber;
}


/*
====================
CL_GetParseEntityState
====================
*/
qboolean	CL_GetParseEntityState( int parseEntityNumber, entityState_t *state ) {
	// can't return anything that hasn't been parsed yet
	if ( parseEntityNumber >= cl.parseEntitiesNum ) {
		Com_Error( ERR_DROP, "CL_GetParseEntityState: %i >= %i",
			parseEntityNumber, cl.parseEntitiesNum );
	}

	// can't return anything that has been overwritten in the circular buffer
	if ( parseEntityNumber <= cl.parseEntitiesNum - MAX_PARSE_ENTITIES ) {
		return qfalse;
	}

	*state = cl.parseEntities[ parseEntityNumber & ( MAX_PARSE_ENTITIES - 1 ) ];
	return qtrue;
}

/*
====================
CL_GetCurrentSnapshotNumber
====================
*/
void	CL_GetCurrentSnapshotNumber( int *snapshotNumber, int *serverTime ) {
	*snapshotNumber = cl.snap.messageNum;
	*serverTime = cl.snap.serverTime;
}

/*
====================
CL_GetSnapshot
====================
*/
qboolean	CL_GetSnapshot( int snapshotNumber, snapshot_t *snapshot ) {
	clSnapshot_t	*clSnap;
	int				i, count;

	if ( snapshotNumber > cl.snap.messageNum ) {
		Com_Error( ERR_DROP, "CL_GetSnapshot: snapshotNumber > cl.snapshot.messageNum" );
	}

	// if the frame has fallen out of the circular buffer, we can't return it
	if ( cl.snap.messageNum - snapshotNumber >= PACKET_BACKUP ) {
		return qfalse;
	}

	// if the frame is not valid, we can't return it
	clSnap = &cl.snapshots[snapshotNumber & PACKET_MASK];
	if ( !clSnap->valid ) {
		return qfalse;
	}

	// if the entities in the frame have fallen out of their
	// circular buffer, we can't return it
	if ( cl.parseEntitiesNum - clSnap->parseEntitiesNum >= MAX_PARSE_ENTITIES ) {
		return qfalse;
	}

	// write the snapshot
	snapshot->snapFlags = clSnap->snapFlags;
	snapshot->serverCommandSequence = clSnap->serverCommandNum;
	snapshot->ping = clSnap->ping;
	snapshot->serverTime = clSnap->serverTime;
	Com_Memcpy( snapshot->areamask, clSnap->areamask, sizeof( snapshot->areamask ) );
	snapshot->ps = clSnap->ps;
	count = clSnap->numEntities;
	if ( count > MAX_ENTITIES_IN_SNAPSHOT ) {
		Com_DPrintf( "CL_GetSnapshot: truncated %i entities to %i\n", count, MAX_ENTITIES_IN_SNAPSHOT );
		count = MAX_ENTITIES_IN_SNAPSHOT;
	}
	snapshot->numEntities = count;
	for ( i = 0 ; i < count ; i++ ) {
		snapshot->entities[i] = 
			cl.parseEntities[ ( clSnap->parseEntitiesNum + i ) & (MAX_PARSE_ENTITIES-1) ];
	}

	// FIXME: configstring changes and server commands!!!

	return qtrue;
}

/*
=====================
CL_SetUserCmdValue
=====================
*/
void CL_SetUserCmdValue( int userCmdValue, int userCmdPrimary, float sensitivityScale, int userCmdFov ) {
	cl.cgameUserCmdValue = userCmdValue;
	cl.cgameUserCmdPrimary = userCmdPrimary;
	cl.cgameUserCmdFov = userCmdFov;
	cl.cgameSensitivity = sensitivityScale;
}

/*
=====================
CL_AddCgameCommand
=====================
*/
void CL_AddCgameCommand( const char *cmdName ) {
	Cmd_AddCommand( cmdName, NULL );
}

/*
=====================
CL_CgameError
=====================
*/
void CL_CgameError( const char *string ) {
	Com_Error( ERR_DROP, "%s", string );
}


/*
=====================
CL_ConfigstringModified
=====================
*/
void CL_ConfigstringModified( void ) {
	char		*old, *s;
	int			i, index;
	char		*dup;
	gameState_t	oldGs;
	int			len;

	index = atoi( Cmd_Argv(1) );
	if ( index < 0 || index >= MAX_CONFIGSTRINGS ) {
		Com_Error( ERR_DROP, "configstring > MAX_CONFIGSTRINGS" );
	}
	// get everything after "cs <num>"
	s = Cmd_ArgsFrom(2);

	old = cl.gameState.stringData + cl.gameState.stringOffsets[ index ];
	if ( !strcmp( old, s ) ) {
		return;		// unchanged
	}

	// build the new gameState_t
	oldGs = cl.gameState;

	Com_Memset( &cl.gameState, 0, sizeof( cl.gameState ) );

	// leave the first 0 for uninitialized strings
	cl.gameState.dataCount = 1;
		
	for ( i = 0 ; i < MAX_CONFIGSTRINGS ; i++ ) {
		if ( i == index ) {
			dup = s;
		} else {
			dup = oldGs.stringData + oldGs.stringOffsets[ i ];
		}
		if ( !dup[0] ) {
			continue;		// leave with the default empty string
		}

		len = strlen( dup );

		if ( len + 1 + cl.gameState.dataCount > MAX_GAMESTATE_CHARS ) {
			Com_Error( ERR_DROP, "MAX_GAMESTATE_CHARS exceeded" );
		}

		// append it to the gameState string buffer
		cl.gameState.stringOffsets[ i ] = cl.gameState.dataCount;
		Com_Memcpy( cl.gameState.stringData + cl.gameState.dataCount, dup, len + 1 );
		cl.gameState.dataCount += len + 1;
	}

	if ( index == CS_SYSTEMINFO ) {
		// parse serverId and other cvars
		CL_SystemInfoChanged();
	}

}


/*
===================
CL_GetServerCommand

Set up argc/argv for the given command
===================
*/
qboolean CL_GetServerCommand( int serverCommandNumber ) {
	char	*s;
	char	*cmd;
	static char bigConfigString[BIG_INFO_STRING];
	int argc;

	// if we have irretrievably lost a reliable command, drop the connection
	if ( serverCommandNumber <= clc.serverCommandSequence - MAX_RELIABLE_COMMANDS ) {
		// when a demo record was started after the client got a whole bunch of
		// reliable commands then the client never got those first reliable commands
		if ( clc.demoplaying )
			return qfalse;
		Com_Error( ERR_DROP, "CL_GetServerCommand: a reliable command was cycled out" );
		return qfalse;
	}

	if ( serverCommandNumber > clc.serverCommandSequence ) {
		Com_Error( ERR_DROP, "CL_GetServerCommand: requested a command not received" );
		return qfalse;
	}

	s = clc.serverCommands[ serverCommandNumber & ( MAX_RELIABLE_COMMANDS - 1 ) ];
	clc.lastExecutedServerCommand = serverCommandNumber;

	Com_DPrintf( "serverCommand: %i : %s\n", serverCommandNumber, s );

rescan:
	Cmd_TokenizeString( s );
	cmd = Cmd_Argv(0);
	argc = Cmd_Argc();
	
	if ( ( !strcmp( cmd, "chat" ) || !strcmp( cmd, "print" ) ) ) {
		const char *filterText;

		filterText = Cmd_Argv( 1 );
		if ( !strcmp( cmd, "chat" ) && argc > 2 ) {
			filterText = Cmd_Argv( 2 );
		}

		if ( CL_ShouldFilterConsoleText( filterText ) ) {
			return qfalse;
		}
	}

	if ( !strcmp( cmd, "disconnect" ) ) {
		// https://zerowing.idsoftware.com/bugzilla/show_bug.cgi?id=552
		// allow server to indicate why they were disconnected
		if ( argc >= 2 )
			Com_Error (ERR_SERVERDISCONNECT, va( "Server Disconnected - %s", Cmd_Argv( 1 ) ) );
		else
			Com_Error (ERR_SERVERDISCONNECT,"Server disconnected\n");
	}

	if ( !strcmp( cmd, "bcs0" ) ) {
		Com_sprintf( bigConfigString, BIG_INFO_STRING, "cs %s \"%s", Cmd_Argv(1), Cmd_Argv(2) );
		return qfalse;
	}

	if ( !strcmp( cmd, "bcs1" ) ) {
		s = Cmd_Argv(2);
		if( strlen(bigConfigString) + strlen(s) >= BIG_INFO_STRING ) {
			Com_Error( ERR_DROP, "bcs exceeded BIG_INFO_STRING" );
		}
		strcat( bigConfigString, s );
		return qfalse;
	}

	if ( !strcmp( cmd, "bcs2" ) ) {
		s = Cmd_Argv(2);
		if( strlen(bigConfigString) + strlen(s) + 1 >= BIG_INFO_STRING ) {
			Com_Error( ERR_DROP, "bcs exceeded BIG_INFO_STRING" );
		}
		strcat( bigConfigString, s );
		strcat( bigConfigString, "\"" );
		s = bigConfigString;
		goto rescan;
	}

	if ( !strcmp( cmd, "cs" ) ) {
		CL_ConfigstringModified();
		// reparse the string, because CL_ConfigstringModified may have done another Cmd_TokenizeString()
		Cmd_TokenizeString( s );
		return qtrue;
	}

	if ( !strcmp( cmd, "map_restart" ) ) {
		// clear notify lines and outgoing commands before passing
		// the restart to the cgame
		Con_ClearNotify();
		Com_Memset( cl.cmds, 0, sizeof( cl.cmds ) );
		return qtrue;
	}

	// the clientLevelShot command is used during development
	// to generate 128*128 screenshots from the intermission
	// point of levels for the menu system to use
	// we pass it along to the cgame to make apropriate adjustments,
	// but we also clear the console and notify lines here
	if ( !strcmp( cmd, "clientLevelShot" ) ) {
		// don't do it if we aren't running the server locally,
		// otherwise malicious remote servers could overwrite
		// the existing thumbnails
		if ( !com_sv_running->integer ) {
			return qfalse;
		}
		// close the console
		Con_Close();
		// take a special screenshot next frame
		Cbuf_AddText( "wait ; wait ; wait ; wait ; screenshot levelshot\n" );
		return qtrue;
	}

	// we may want to put a "connect to other server" command here

	// cgame can now act on the command
	return qtrue;
}


/*
====================
CL_CM_LoadMap

Just adds default parameters that cgame doesn't need to know about
====================
*/
void CL_CM_LoadMap( const char *mapname ) {
	int		checksum;

	CM_LoadMap( mapname, qtrue, &checksum );
}

/*
====================
CL_ShutdonwCGame

====================
*/
void CL_ShutdownCGame( void ) {
	cls.keyCatchers &= ~KEYCATCH_CGAME;
	cls.cgameStarted = qfalse;
	if ( !cgvm ) {
		return;
	}
	VM_Call( cgvm, CG_SHUTDOWN );
	VM_Free( cgvm );
	cgvm = NULL;
}

static int	FloatAsInt( float f ) {
	int		temp;

	*(float *)&temp = f;

	return temp;
}

/*
====================
CL_CgameSystemCallsImpl

Implements the cgame trap surface for both legacy syscall dispatch and the
native import-table bridge.
====================
*/
#define	VMA(x) VM_ArgPtr(args[x])
#define	VMF(x)	((float *)args)[x]
static int CL_CgameSystemCallsImpl( int *args, qboolean logContract ) {
	if ( logContract ) {
		SyscallContract_LogEvent( "shim-cgame", "cgame", args, SYSCALL_CONTRACT_MAX_ARGS );
	}

	switch( args[0] ) {
	case CG_PRINT:
		Com_Printf( "%s", VMA(1) );
		return 0;
	case CG_ERROR:
		Com_Error( ERR_DROP, "%s", VMA(1) );
		return 0;
	case CG_MILLISECONDS:
		return Sys_Milliseconds();
	case CG_CVAR_REGISTER:
		Cvar_Register( VMA(1), VMA(2), VMA(3), args[4] ); 
		return 0;
	case CG_CVAR_UPDATE:
		Cvar_Update( VMA(1) );
		return 0;
	case CG_CVAR_SET:
		Cvar_Set( VMA(1), VMA(2) );
		return 0;
	case CG_CVAR_VARIABLESTRINGBUFFER:
		Cvar_VariableStringBuffer( VMA(1), VMA(2), args[3] );
		return 0;
	case CG_ARGC:
		return Cmd_Argc();
	case CG_ARGV:
		Cmd_ArgvBuffer( args[1], VMA(2), args[3] );
		return 0;
	case CG_ARGS:
		Cmd_ArgsBuffer( VMA(1), args[2] );
		return 0;
	case CG_CMD_EXECUTETEXT:
		Cbuf_ExecuteText( args[1], VMA(2) );
		return 0;
	case CG_FS_FOPENFILE:
		return qlr_fs_imports.fopen_file_by_mode( VMA(1), VMA(2), args[3] );
	case CG_FS_READ:
		qlr_fs_imports.read( VMA(1), args[2], args[3] );
		return 0;
	case CG_FS_WRITE:
		qlr_fs_imports.write( VMA(1), args[2], args[3] );
		return 0;
	case CG_FS_FCLOSEFILE:
		qlr_fs_imports.fclose_file( args[1] );
		return 0;
	case CG_FS_SEEK:
		return qlr_fs_imports.seek( args[1], args[2], args[3] );
	case CG_SENDCONSOLECOMMAND:
		Cbuf_AddText( VMA(1) );
		return 0;
	case CG_ADDCOMMAND:
		CL_AddCgameCommand( VMA(1) );
		return 0;
	case CG_REMOVECOMMAND:
		Cmd_RemoveCommand( VMA(1) );
		return 0;
	case CG_SENDCLIENTCOMMAND:
		CL_AddReliableCommand( VMA(1) );
		return 0;
	case CG_UPDATESCREEN:
		// this is used during lengthy level loading, so pump message loop
//		Com_EventLoop();	// FIXME: if a server restarts here, BAD THINGS HAPPEN!
// We can't call Com_EventLoop here, a restart will crash and this _does_ happen
// if there is a map change while we are downloading at pk3.
// ZOID
		SCR_UpdateScreen();
		return 0;
	case CG_CM_LOADMAP:
		CL_CM_LoadMap( VMA(1) );
		return 0;
	case CG_CM_NUMINLINEMODELS:
		return CM_NumInlineModels();
	case CG_CM_INLINEMODEL:
		return CM_InlineModel( args[1] );
	case CG_CM_LOADMODEL:
		return 0;
	case CG_CM_TEMPBOXMODEL:
		return CM_TempBoxModel( VMA(1), VMA(2), /*int capsule*/ qfalse );
	case CG_CM_TEMPCAPSULEMODEL:
		return CM_TempBoxModel( VMA(1), VMA(2), /*int capsule*/ qtrue );
	case CG_CM_POINTCONTENTS:
		return CM_PointContents( VMA(1), args[2] );
	case CG_CM_TRANSFORMEDPOINTCONTENTS:
		return CM_TransformedPointContents( VMA(1), args[2], VMA(3), VMA(4) );
	case CG_CM_BOXTRACE:
		CM_BoxTrace( VMA(1), VMA(2), VMA(3), VMA(4), VMA(5), args[6], args[7], /*int capsule*/ qfalse );
		return 0;
	case CG_CM_CAPSULETRACE:
		CM_BoxTrace( VMA(1), VMA(2), VMA(3), VMA(4), VMA(5), args[6], args[7], /*int capsule*/ qtrue );
		return 0;
	case CG_CM_TRANSFORMEDBOXTRACE:
		CM_TransformedBoxTrace( VMA(1), VMA(2), VMA(3), VMA(4), VMA(5), args[6], args[7], VMA(8), VMA(9), /*int capsule*/ qfalse );
		return 0;
	case CG_CM_TRANSFORMEDCAPSULETRACE:
		CM_TransformedBoxTrace( VMA(1), VMA(2), VMA(3), VMA(4), VMA(5), args[6], args[7], VMA(8), VMA(9), /*int capsule*/ qtrue );
		return 0;
	case CG_CM_MARKFRAGMENTS:
		return re.MarkFragments( args[1], VMA(2), VMA(3), args[4], VMA(5), args[6], VMA(7) );
	case CG_S_STARTSOUND:
		S_StartSound( VMA(1), args[2], args[3], args[4] );
		return 0;
	case CG_S_STARTLOCALSOUND:
		S_StartLocalSound( args[1], args[2] );
		return 0;
	case CG_S_CLEARLOOPINGSOUNDS:
		S_ClearLoopingSounds( args[1] ? qtrue : qfalse );
		return 0;
	case CG_S_ADDLOOPINGSOUND:
		S_AddLoopingSound( args[1], VMA(2), VMA(3), args[4] );
		return 0;
	case CG_S_ADDREALLOOPINGSOUND:
		S_AddRealLoopingSound( args[1], VMA(2), VMA(3), args[4] );
		return 0;
	case CG_S_STOPLOOPINGSOUND:
		S_StopLoopingSound( args[1] );
		return 0;
	case CG_S_UPDATEENTITYPOSITION:
		S_UpdateEntityPosition( args[1], VMA(2) );
		return 0;
	case CG_S_RESPATIALIZE:
		S_Respatialize( args[1], VMA(2), VMA(3), args[4] );
		return 0;
	case CG_S_REGISTERSOUND:
		return S_RegisterSound( VMA(1), args[2] ? qtrue : qfalse );
	case CG_S_STARTBACKGROUNDTRACK:
		S_StartBackgroundTrack( VMA(1), VMA(2) );
		return 0;
	case CG_R_LOADWORLDMAP:
		re.LoadWorld( VMA(1) );
		return 0; 
	case CG_R_REGISTERMODEL:
		return re.RegisterModel( VMA(1) );
	case CG_R_REGISTERSKIN:
		return re.RegisterSkin( VMA(1) );
	case CG_R_REGISTERSHADER:
		return re.RegisterShader( VMA(1) );
	case CG_R_REGISTERSHADERNOMIP:
		return re.RegisterShaderNoMip( VMA(1) );
	case CG_R_REGISTERFONT:
		CL_RegisterFont( VMA(1), args[2], VMA(3) );
	case CG_R_CLEARSCENE:
		re.ClearScene();
		return 0;
	case CG_R_ADDREFENTITYTOSCENE:
		re.AddRefEntityToScene( VMA(1) );
		return 0;
	case CG_R_ADDPOLYTOSCENE:
		re.AddPolyToScene( args[1], args[2], VMA(3), 1 );
		return 0;
	case CG_R_ADDPOLYSTOSCENE:
		re.AddPolyToScene( args[1], args[2], VMA(3), args[4] );
		return 0;
	case CG_R_LIGHTFORPOINT:
		return re.LightForPoint( VMA(1), VMA(2), VMA(3), VMA(4) );
	case CG_R_ADDLIGHTTOSCENE:
		re.AddLightToScene( VMA(1), VMF(2), VMF(3), VMF(4), VMF(5) );
		return 0;
	case CG_R_ADDADDITIVELIGHTTOSCENE:
		re.AddAdditiveLightToScene( VMA(1), VMF(2), VMF(3), VMF(4), VMF(5) );
		return 0;
	case CG_R_RENDERSCENE:
		re.RenderScene( VMA(1) );
		return 0;
	case CG_R_SETCOLOR:
		re.SetColor( VMA(1) );
		return 0;
	case CG_R_DRAWSTRETCHPIC:
		re.DrawStretchPic( VMF(1), VMF(2), VMF(3), VMF(4), VMF(5), VMF(6), VMF(7), VMF(8), args[9] );
		return 0;
	case CG_R_MODELBOUNDS:
		re.ModelBounds( args[1], VMA(2), VMA(3) );
		return 0;
	case CG_R_LERPTAG:
		return re.LerpTag( VMA(1), args[2], args[3], args[4], VMF(5), VMA(6) );
	case CG_GETGLCONFIG:
		CL_GetGlconfig( VMA(1) );
		return 0;
	case CG_GETGAMESTATE:
		CL_GetGameState( VMA(1) );
		return 0;
	case CG_GETCURRENTSNAPSHOTNUMBER:
		CL_GetCurrentSnapshotNumber( VMA(1), VMA(2) );
		return 0;
	case CG_GETSNAPSHOT:
		return CL_GetSnapshot( args[1], VMA(2) ) ? qtrue : qfalse;
	case CG_GETSERVERCOMMAND:
		return CL_GetServerCommand( args[1] ) ? qtrue : qfalse;
	case CG_GETCURRENTCMDNUMBER:
		return CL_GetCurrentCmdNumber();
	case CG_GETUSERCMD:
		return CL_GetUserCmd( args[1], VMA(2) ) ? qtrue : qfalse;
	case CG_SETUSERCMDVALUE:
		CL_SetUserCmdValue( args[1], args[2], VMF(3), args[4] );
		return 0;
	case CG_MEMORY_REMAINING:
		return Hunk_MemoryRemaining();
  case CG_KEY_ISDOWN:
		return Key_IsDown( args[1] ) ? qtrue : qfalse;
  case CG_KEY_GETCATCHER:
		return Key_GetCatcher();
  case CG_KEY_SETCATCHER:
		Key_SetCatcher( args[1] );
    return 0;
  case CG_KEY_GETKEY:
		return Key_GetKey( VMA(1) );

	case CG_KEY_KEYNUMTOSTRINGBUF:
		Q_strncpyz( VMA(2), Key_KeynumToString( args[1] ), args[3] );
		return 0;
	case CG_KEY_GETBINDINGBUF:
		Q_strncpyz( VMA(2), Key_GetBinding( args[1] ), args[3] );
		return 0;
	case CG_KEY_SETBINDING:
		Key_SetBinding( args[1], VMA(2) );
		return 0;
	case CG_KEY_GETOVERSTRIKEMODE:
		return Key_GetOverstrikeMode() ? qtrue : qfalse;
	case CG_KEY_SETOVERSTRIKEMODE:
		Key_SetOverstrikeMode( args[1] ? qtrue : qfalse );
		return 0;
	case CG_ADVERTISEMENTBRIDGE_INITCGAME:
		CL_AdvertisementBridge_InitCGame();
		return 0;
	case CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME:
		CL_AdvertisementBridge_ShutdownCGame();
		return 0;
	case CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS:
		CL_AdvertisementBridge_UpdateLoadingViewParameters();
		return 0;
	case CG_ADVERTISEMENTBRIDGE_SETFRAMETIME:
		CL_AdvertisementBridge_SetFrameTime( args[1] );
		return 0;


	case CG_MEMSET:
		Com_Memset( VMA(1), args[2], args[3] );
		return 0;
	case CG_MEMCPY:
		Com_Memcpy( VMA(1), VMA(2), args[3] );
		return 0;
	case CG_STRNCPY:
		return (int)strncpy( VMA(1), VMA(2), args[3] );
	case CG_SIN:
		return FloatAsInt( sin( VMF(1) ) );
	case CG_COS:
		return FloatAsInt( cos( VMF(1) ) );
	case CG_ATAN2:
		return FloatAsInt( atan2( VMF(1), VMF(2) ) );
	case CG_SQRT:
		return FloatAsInt( sqrt( VMF(1) ) );
	case CG_FLOOR:
		return FloatAsInt( floor( VMF(1) ) );
	case CG_CEIL:
		return FloatAsInt( ceil( VMF(1) ) );
	case CG_ACOS:
		return FloatAsInt( Q_acos( VMF(1) ) );

	case CG_PC_ADD_GLOBAL_DEFINE:
		return botlib_export->PC_AddGlobalDefine( VMA(1) );
	case CG_PC_LOAD_SOURCE:
		return botlib_export->PC_LoadSourceHandle( VMA(1) );
	case CG_PC_FREE_SOURCE:
		return botlib_export->PC_FreeSourceHandle( args[1] );
	case CG_PC_READ_TOKEN:
		return botlib_export->PC_ReadTokenHandle( args[1], VMA(2) );
	case CG_PC_SOURCE_FILE_AND_LINE:
		return botlib_export->PC_SourceFileAndLine( args[1], VMA(2), VMA(3) );

	case CG_S_STOPBACKGROUNDTRACK:
		S_StopBackgroundTrack();
		return 0;

	case CG_REAL_TIME:
		return Com_RealTime( VMA(1) );
	case CG_SNAPVECTOR:
		Sys_SnapVector( VMA(1) );
		return 0;

	case CG_CIN_PLAYCINEMATIC:
	  return CIN_PlayCinematic(VMA(1), args[2], args[3], args[4], args[5], args[6]);

	case CG_CIN_STOPCINEMATIC:
	  return CIN_StopCinematic(args[1]);

	case CG_CIN_RUNCINEMATIC:
	  return CIN_RunCinematic(args[1]);

	case CG_CIN_DRAWCINEMATIC:
	  CIN_DrawCinematic(args[1]);
	  return 0;

	case CG_CIN_SETEXTENTS:
	  CIN_SetExtents(args[1], args[2], args[3], args[4], args[5]);
	  return 0;

	case CG_R_REMAP_SHADER:
		re.RemapShader( VMA(1), VMA(2), VMA(3) );
		return 0;

/*
	case CG_LOADCAMERA:
		return loadCamera(VMA(1));

	case CG_STARTCAMERA:
		startCamera(args[1]);
		return 0;

	case CG_GETCAMERAINFO:
		return getCameraInfo(args[1], VMA(2), VMA(3));
*/
	case CG_GET_ENTITY_TOKEN:
		return re.GetEntityToken( VMA(1), args[2] ) ? qtrue : qfalse;
	case CG_R_INPVS:
		return re.inPVS( VMA(1), VMA(2) ) ? qtrue : qfalse;

	default:
	        assert(0); // bk010102
		Com_Error( ERR_DROP, "Bad cgame system trap: %i", args[0] );
	}
	return 0;
}

/*
====================
CL_CgameSystemCalls
====================
*/
int CL_CgameSystemCalls( int *args ) {
	/*
	case CG_CMD_EXECUTETEXT:
		Cbuf_ExecuteText( args[1], VMA(2) );
	case CG_KEY_GETBINDINGBUF:
		Q_strncpyz( VMA(2), Key_GetBinding( args[1] ), args[3] );
	case CG_KEY_SETBINDING:
		Key_SetBinding( args[1], VMA(2) );
	case CG_KEY_GETOVERSTRIKEMODE:
		return Key_GetOverstrikeMode();
	case CG_KEY_SETOVERSTRIKEMODE:
		Key_SetOverstrikeMode( args[1] );
	case CG_ADVERTISEMENTBRIDGE_INITCGAME:
		CL_AdvertisementBridge_InitCGame();
	case CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME:
		CL_AdvertisementBridge_ShutdownCGame();
	case CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS:
		CL_AdvertisementBridge_UpdateLoadingViewParameters();
	case CG_ADVERTISEMENTBRIDGE_SETFRAMETIME:
		CL_AdvertisementBridge_SetFrameTime( args[1] );
	*/
	return CL_CgameSystemCallsImpl( args, qtrue );
}

/*
====================
CG_Import_Syscall
====================
*/
static int QDECL CG_Import_Syscall( int arg, ... ) {
	int args[SYSCALL_CONTRACT_MAX_ARGS];
	int i;
	va_list ap;

	args[0] = arg;

	va_start(ap, arg);
	for (i = 1; i < SYSCALL_CONTRACT_MAX_ARGS; i++) {
		args[i] = va_arg(ap, int);
	}
	va_end(ap);

	return CL_CgameSystemCallsImpl( args, qfalse );
}

#include "ql_cgame_imports.inc"

typedef void (QDECL *ql_import_f)( void );

static void QDECL QL_CG_trap_Key_GetBindingBuf( int keynum, char *buf, int buflen );
static void QDECL QL_CG_trap_Key_SetBinding( int keynum, const char *binding );
static qboolean QDECL QL_CG_trap_Key_GetOverstrikeMode( void );
static void QDECL QL_CG_trap_Key_SetOverstrikeMode( qboolean state );
static void QDECL QL_CG_trap_Cmd_ExecuteText( int exec_when, const char *text );
static void QDECL QL_CG_trap_AdvertisementBridge_InitCGame( void );
static void QDECL QL_CG_trap_AdvertisementBridge_ShutdownCGame( void );
static void QDECL QL_CG_trap_AdvertisementBridge_UpdateLoadingViewParameters( void );
static void QDECL QL_CG_trap_AdvertisementBridge_SetFrameTime( int frameTime );

static vec4_t ql_cgame_currentColor = { 1.0f, 1.0f, 1.0f, 1.0f };
static uint64_t ql_cgame_mutedIdentitySet[MAX_CLIENTS];
static int ql_cgame_mutedIdentityCount = 0;
static ql_import_f ql_cgame_imports[CGAME_NATIVE_IMPORT_COUNT] = {
	[CG_KEY_GETBINDINGBUF] = (ql_import_f)QL_CG_trap_Key_GetBindingBuf,
	[CG_KEY_SETBINDING] = (ql_import_f)QL_CG_trap_Key_SetBinding,
	[CG_KEY_GETOVERSTRIKEMODE] = (ql_import_f)QL_CG_trap_Key_GetOverstrikeMode,
	[CG_KEY_SETOVERSTRIKEMODE] = (ql_import_f)QL_CG_trap_Key_SetOverstrikeMode,
	[CG_CMD_EXECUTETEXT] = (ql_import_f)QL_CG_trap_Cmd_ExecuteText,
	[CG_ADVERTISEMENTBRIDGE_INITCGAME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_InitCGame,
	[CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_ShutdownCGame,
	[CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS] = (ql_import_f)QL_CG_trap_AdvertisementBridge_UpdateLoadingViewParameters,
	[CG_ADVERTISEMENTBRIDGE_SETFRAMETIME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_SetFrameTime,
};

/*
==============
QL_CG_PackFloatBits64
==============
*/
static unsigned long long QL_CG_PackFloatBits64( float lo, float hi ) {
	union {
		unsigned long long value;
		struct {
			float lo;
			float hi;
		} parts;
	} packed;

	packed.parts.lo = lo;
	packed.parts.hi = hi;
	return packed.value;
}

/*
==============
QL_CG_RegisterDefaultAdvertCellShader
==============
*/
static qhandle_t QL_CG_RegisterDefaultAdvertCellShader( const char *defaultContent ) {
	if ( !defaultContent || !defaultContent[0] ) {
		return 0;
	}

	return CL_Steam_RegisterShader( defaultContent );
}

/*
==============
QL_CG_CombineIdentityWords
==============
*/
static uint64_t QL_CG_CombineIdentityWords( unsigned int identityLow, unsigned int identityHigh ) {
	return ( (uint64_t)identityHigh << 32 ) | (uint64_t)identityLow;
}

/*
==============
QL_CG_FindMutedIdentityIndex
==============
*/
static int QL_CG_FindMutedIdentityIndex( uint64_t identity ) {
	int i;

	for ( i = 0; i < ql_cgame_mutedIdentityCount; ++i ) {
		if ( ql_cgame_mutedIdentitySet[i] == identity ) {
			return i;
		}
	}

	return -1;
}

/*
==============
CL_IsSteamIdentityMuted
==============
*/
qboolean CL_IsSteamIdentityMuted( unsigned int identityLow, unsigned int identityHigh ) {
	uint64_t identity;

	identity = QL_CG_CombineIdentityWords( identityLow, identityHigh );
	if ( !identity ) {
		return qfalse;
	}

	return QL_CG_FindMutedIdentityIndex( identity ) >= 0 ? qtrue : qfalse;
}

/*
==============
QL_CG_trap_Cvar_RegisterRange
==============
*/
static void QDECL QL_CG_trap_Cvar_RegisterRange( vmCvar_t *vmCvar, const char *varName, const char *defaultValue, const char *minimumValue, const char *maximumValue, int flags ) {
	Cvar_GetBounded( varName, defaultValue, minimumValue, maximumValue, flags );
	Cvar_Register( vmCvar, varName, defaultValue, flags );
}

/*
==============
QL_CG_trap_Cvar_Reset
==============
*/
static void QDECL QL_CG_trap_Cvar_Reset( const char *varName ) {
	Cvar_Reset( varName );
}

/*
==============
QL_CG_trap_FS_GetFileList
==============
*/
static int QDECL QL_CG_trap_FS_GetFileList( const char *path, const char *extension, char *listbuf, int bufsize ) {
	return qlr_fs_imports.get_file_list( path, extension, listbuf, bufsize );
}

/*
==============
QL_CG_trap_S_StartSoundVolume
==============
*/
static void QDECL QL_CG_trap_S_StartSoundVolume( vec3_t origin, int entityNum, int entchannel, sfxHandle_t sfx, float volume ) {
	S_StartSoundVolume( origin, entityNum, entchannel, sfx, volume );
}

/*
==============
QL_CG_trap_S_StartLocalSoundVolume
==============
*/
static void QDECL QL_CG_trap_S_StartLocalSoundVolume( sfxHandle_t sfx, int channelNum, float volume ) {
	S_StartLocalSoundVolume( sfx, channelNum, volume );
}

/*
==============
QL_CG_trap_S_ClearLoopingSoundsFrame
==============
*/
static void QDECL QL_CG_trap_S_ClearLoopingSoundsFrame( void ) {
	S_ClearLoopingSounds( qfalse );
}

/*
==============
QL_CG_trap_S_ClearLoopingSoundsKillAll
==============
*/
static void QDECL QL_CG_trap_S_ClearLoopingSoundsKillAll( void ) {
	S_ClearLoopingSounds( qtrue );
}

/*
==============
QL_CG_trap_SetupAdvertCellShader
==============
*/
static qhandle_t QDECL QL_CG_trap_SetupAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {
	(void)rect;
	(void)cellId;
	return QL_CG_RegisterDefaultAdvertCellShader( defaultContent );
}

/*
==============
QL_CG_trap_RefreshAdvertCellShader
==============
*/
static qhandle_t QDECL QL_CG_trap_RefreshAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {
	(void)rect;
	(void)cellId;
	return QL_CG_RegisterDefaultAdvertCellShader( defaultContent );
}

/*
==============
QL_CG_trap_SetActiveAdvert
==============
*/
static void QDECL QL_CG_trap_SetActiveAdvert( int cellId ) {
	CL_AdvertisementBridge_SetActiveAdvert( cellId );
}

/*
==============
QL_CG_trap_UpdateAdvert
==============
*/
static void QDECL QL_CG_trap_UpdateAdvert( int handleOrToken, int area ) {
	// cgamex86.dll HLIL: import[58] is called by the retail advert ownerdraw after the shader quad draw.
	// The recovered host-side provider remains inert here as well, so preserve the callback surface without inventing behavior.
	(void)handleOrToken;
	(void)area;
}

/*
==============
QL_CG_trap_AdvertisementBridge_SetMapPath
==============
*/
static void QDECL QL_CG_trap_AdvertisementBridge_SetMapPath( const char *mapPath ) {
	(void)mapPath;
	CL_RefreshOnlineServicesBridgeState();
}

/*
==============
QL_CG_trap_AdvertisementBridge_UpdateViewParameters
==============
*/
static void QDECL QL_CG_trap_AdvertisementBridge_UpdateViewParameters( void ) {
	CL_RefreshOnlineServicesBridgeState();
}

/*
==============
QL_CG_trap_AdvertisementBridge_ClearDelay
==============
*/
static void QDECL QL_CG_trap_AdvertisementBridge_ClearDelay( void ) {
}

/*
==============
QL_CG_trap_R_SetColor_QL
==============
*/
static void QDECL QL_CG_trap_R_SetColor_QL( const float *rgba ) {
	if ( rgba ) {
		ql_cgame_currentColor[0] = rgba[0];
		ql_cgame_currentColor[1] = rgba[1];
		ql_cgame_currentColor[2] = rgba[2];
		ql_cgame_currentColor[3] = rgba[3];
	} else {
		ql_cgame_currentColor[0] = 1.0f;
		ql_cgame_currentColor[1] = 1.0f;
		ql_cgame_currentColor[2] = 1.0f;
		ql_cgame_currentColor[3] = 1.0f;
	}

	re.SetColor( rgba );
}

/*
==============
QL_CG_trap_TaggedCvarStringBuffer
==============
*/
static void QDECL QL_CG_trap_TaggedCvarStringBuffer( const char *varName, char *buffer ) {
	if ( !buffer ) {
		return;
	}

	Cvar_VariableStringBuffer( varName, buffer, BIG_INFO_STRING );
}

/*
==============
QL_CG_trap_R_MirrorPoint
==============
*/
static void QDECL QL_CG_trap_R_MirrorPoint( vec3_t in, orientation_t *surface, orientation_t *camera, vec3_t out ) {
	R_MirrorPoint( in, surface, camera, out );
}

/*
==============
QL_CG_trap_R_MirrorVector
==============
*/
static void QDECL QL_CG_trap_R_MirrorVector( vec3_t in, orientation_t *surface, orientation_t *camera, vec3_t out ) {
	R_MirrorVector( in, surface, camera, out );
}

/*
==============
QL_CG_trap_DrawScaledText
==============
*/
static void QDECL QL_CG_trap_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, int forceColor ) {
	RE_DrawScaledText( x, y, text, fontHandle, scale, maxX, outMaxX, forceColor != qfalse ? qtrue : qfalse, ql_cgame_currentColor );
}

/*
==============
QL_CG_trap_MeasureText
==============
*/
static unsigned long long QDECL QL_CG_trap_MeasureText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outLeft ) {
	float width;
	float height;

	RE_MeasureScaledText( text, end, fontHandle, scale, maxX, &width, &height, outLeft );

	return QL_CG_PackFloatBits64( width, height );
}

/*
==============
QL_CG_trap_IsClientMuted
==============
*/
static int QDECL QL_CG_trap_IsClientMuted( unsigned int identityLow, unsigned int identityHigh ) {
	uint64_t identity;

	identity = QL_CG_CombineIdentityWords( identityLow, identityHigh );
	if ( !identity ) {
		return 0;
	}

	return QL_CG_FindMutedIdentityIndex( identity ) >= 0;
}

/*
==============
QL_CG_trap_ToggleClientMute
==============
*/
static int QDECL QL_CG_trap_ToggleClientMute( unsigned int identityLow, unsigned int identityHigh ) {
	uint64_t identity;
	int index;

	identity = QL_CG_CombineIdentityWords( identityLow, identityHigh );
	if ( !identity ) {
		return 0;
	}

	index = QL_CG_FindMutedIdentityIndex( identity );
	if ( index >= 0 ) {
		--ql_cgame_mutedIdentityCount;
		ql_cgame_mutedIdentitySet[index] = ql_cgame_mutedIdentitySet[ql_cgame_mutedIdentityCount];
		return 0;
	}

	if ( ql_cgame_mutedIdentityCount >= ARRAY_LEN( ql_cgame_mutedIdentitySet ) ) {
		return 0;
	}

	ql_cgame_mutedIdentitySet[ql_cgame_mutedIdentityCount++] = identity;
	return 1;
}

/*
==============
QL_CG_trap_GetAvatarImageHandle
==============
*/
static qhandle_t QDECL QL_CG_trap_GetAvatarImageHandle( unsigned int identityLow, unsigned int identityHigh ) {
	uint64_t identity;
	char url[MAX_QPATH];

	identity = QL_CG_CombineIdentityWords( identityLow, identityHigh );
	if ( !identity ) {
		return 0;
	}

	Com_sprintf( url, sizeof( url ), "steam://avatar/large/%llu", (unsigned long long)identity );
	return CL_Steam_RegisterShader( url );
}

/*
==============
CL_InitCGameImports
==============
*/
static void CL_InitCGameImports( void ) {
	Com_Memset( ql_cgame_imports, 0, sizeof( ql_cgame_imports ) );

	ql_cgame_currentColor[0] = 1.0f;
	ql_cgame_currentColor[1] = 1.0f;
	ql_cgame_currentColor[2] = 1.0f;
	ql_cgame_currentColor[3] = 1.0f;

	ql_cgame_imports[CG_QL_IMPORT_PRINT] = (ql_import_f)QL_CG_trap_Print;
	ql_cgame_imports[CG_QL_IMPORT_ERROR] = (ql_import_f)QL_CG_trap_Error;
	ql_cgame_imports[CG_QL_IMPORT_MILLISECONDS] = (ql_import_f)QL_CG_trap_Milliseconds;
	ql_cgame_imports[CG_QL_IMPORT_REAL_TIME] = (ql_import_f)QL_CG_trap_RealTime;
	ql_cgame_imports[CG_QL_IMPORT_CVAR_REGISTER] = (ql_import_f)QL_CG_trap_Cvar_Register;
	ql_cgame_imports[CG_QL_IMPORT_CVAR_REGISTER_RANGE] = (ql_import_f)QL_CG_trap_Cvar_RegisterRange;
	ql_cgame_imports[CG_QL_IMPORT_CVAR_UPDATE] = (ql_import_f)QL_CG_trap_Cvar_Update;
	ql_cgame_imports[CG_QL_IMPORT_CVAR_SET] = (ql_import_f)QL_CG_trap_Cvar_Set;
	ql_cgame_imports[CG_QL_IMPORT_CVAR_VARIABLESTRINGBUFFER] = (ql_import_f)QL_CG_trap_Cvar_VariableStringBuffer;
	ql_cgame_imports[CG_QL_IMPORT_CVAR_RESET] = (ql_import_f)QL_CG_trap_Cvar_Reset;
	ql_cgame_imports[CG_QL_IMPORT_ARGC] = (ql_import_f)QL_CG_trap_Argc;
	ql_cgame_imports[CG_QL_IMPORT_ARGV] = (ql_import_f)QL_CG_trap_Argv;
	ql_cgame_imports[CG_QL_IMPORT_ARGS] = (ql_import_f)QL_CG_trap_Args;
	ql_cgame_imports[CG_QL_IMPORT_FS_FOPENFILE] = (ql_import_f)QL_CG_trap_FS_FOpenFile;
	ql_cgame_imports[CG_QL_IMPORT_FS_READ] = (ql_import_f)QL_CG_trap_FS_Read;
	ql_cgame_imports[CG_QL_IMPORT_FS_WRITE] = (ql_import_f)QL_CG_trap_FS_Write;
	ql_cgame_imports[CG_QL_IMPORT_FS_FCLOSEFILE] = (ql_import_f)QL_CG_trap_FS_FCloseFile;
	ql_cgame_imports[CG_QL_IMPORT_FS_SEEK] = (ql_import_f)QL_CG_trap_FS_Seek;
	ql_cgame_imports[CG_QL_IMPORT_FS_GETFILELIST] = (ql_import_f)QL_CG_trap_FS_GetFileList;
	ql_cgame_imports[CG_QL_IMPORT_SENDCONSOLECOMMAND] = (ql_import_f)QL_CG_trap_SendConsoleCommand;
	ql_cgame_imports[CG_QL_IMPORT_ADDCOMMAND] = (ql_import_f)QL_CG_trap_AddCommand;
	ql_cgame_imports[CG_QL_IMPORT_REMOVECOMMAND] = (ql_import_f)QL_CG_trap_RemoveCommand;
	ql_cgame_imports[CG_QL_IMPORT_SENDCLIENTCOMMAND] = (ql_import_f)QL_CG_trap_SendClientCommand;
	ql_cgame_imports[CG_QL_IMPORT_UPDATESCREEN] = (ql_import_f)QL_CG_trap_UpdateScreen;
	ql_cgame_imports[CG_QL_IMPORT_CM_LOADMAP] = (ql_import_f)QL_CG_trap_CM_LoadMap;
	ql_cgame_imports[CG_QL_IMPORT_CM_NUMINLINEMODELS] = (ql_import_f)QL_CG_trap_CM_NumInlineModels;
	ql_cgame_imports[CG_QL_IMPORT_CM_INLINEMODEL] = (ql_import_f)QL_CG_trap_CM_InlineModel;
	ql_cgame_imports[CG_QL_IMPORT_CM_TEMPBOXMODEL] = (ql_import_f)QL_CG_trap_CM_TempBoxModel;
	ql_cgame_imports[CG_QL_IMPORT_CM_TEMPCAPSULEMODEL] = (ql_import_f)QL_CG_trap_CM_TempCapsuleModel;
	ql_cgame_imports[CG_QL_IMPORT_CM_POINTCONTENTS] = (ql_import_f)QL_CG_trap_CM_PointContents;
	ql_cgame_imports[CG_QL_IMPORT_CM_TRANSFORMEDPOINTCONTENTS] = (ql_import_f)QL_CG_trap_CM_TransformedPointContents;
	ql_cgame_imports[CG_QL_IMPORT_CM_BOXTRACE] = (ql_import_f)QL_CG_trap_CM_BoxTrace;
	ql_cgame_imports[CG_QL_IMPORT_CM_CAPSULETRACE] = (ql_import_f)QL_CG_trap_CM_CapsuleTrace;
	ql_cgame_imports[CG_QL_IMPORT_CM_TRANSFORMEDBOXTRACE] = (ql_import_f)QL_CG_trap_CM_TransformedBoxTrace;
	ql_cgame_imports[CG_QL_IMPORT_CM_TRANSFORMEDCAPSULETRACE] = (ql_import_f)QL_CG_trap_CM_TransformedCapsuleTrace;
	ql_cgame_imports[CG_QL_IMPORT_CM_MARKFRAGMENTS] = (ql_import_f)QL_CG_trap_CM_MarkFragments;
	ql_cgame_imports[CG_QL_IMPORT_S_STARTSOUND] = (ql_import_f)QL_CG_trap_S_StartSound;
	ql_cgame_imports[CG_QL_IMPORT_S_STARTSOUND_VOLUME] = (ql_import_f)QL_CG_trap_S_StartSoundVolume;
	ql_cgame_imports[CG_QL_IMPORT_S_STARTLOCALSOUND] = (ql_import_f)QL_CG_trap_S_StartLocalSound;
	ql_cgame_imports[CG_QL_IMPORT_S_STARTLOCALSOUND_VOLUME] = (ql_import_f)QL_CG_trap_S_StartLocalSoundVolume;
	ql_cgame_imports[CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_FRAME] = (ql_import_f)QL_CG_trap_S_ClearLoopingSoundsFrame;
	ql_cgame_imports[CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_KILLALL] = (ql_import_f)QL_CG_trap_S_ClearLoopingSoundsKillAll;
	ql_cgame_imports[CG_QL_IMPORT_S_ADDLOOPINGSOUND] = (ql_import_f)QL_CG_trap_S_AddLoopingSound;
	ql_cgame_imports[CG_QL_IMPORT_S_UPDATEENTITYPOSITION] = (ql_import_f)QL_CG_trap_S_UpdateEntityPosition;
	ql_cgame_imports[CG_QL_IMPORT_S_RESPATIALIZE] = (ql_import_f)QL_CG_trap_S_Respatialize;
	ql_cgame_imports[CG_QL_IMPORT_S_REGISTERSOUND] = (ql_import_f)QL_CG_trap_S_RegisterSound;
	ql_cgame_imports[CG_QL_IMPORT_S_STARTBACKGROUNDTRACK] = (ql_import_f)QL_CG_trap_S_StartBackgroundTrack;
	ql_cgame_imports[CG_QL_IMPORT_S_STOPBACKGROUNDTRACK] = (ql_import_f)QL_CG_trap_S_StopBackgroundTrack;
	ql_cgame_imports[CG_QL_IMPORT_R_LOADWORLDMAP] = (ql_import_f)QL_CG_trap_R_LoadWorldMap;
	ql_cgame_imports[CG_QL_IMPORT_R_REGISTERMODEL] = (ql_import_f)QL_CG_trap_R_RegisterModel;
	ql_cgame_imports[CG_QL_IMPORT_R_REGISTERSKIN] = (ql_import_f)QL_CG_trap_R_RegisterSkin;
	ql_cgame_imports[CG_QL_IMPORT_R_REGISTERSHADER] = (ql_import_f)QL_CG_trap_R_RegisterShader;
	ql_cgame_imports[CG_QL_IMPORT_R_REGISTERSHADERNOMIP] = (ql_import_f)QL_CG_trap_R_RegisterShaderNoMip;
	ql_cgame_imports[CG_QL_IMPORT_SETUP_ADVERT_CELL_SHADER] = (ql_import_f)QL_CG_trap_SetupAdvertCellShader;
	ql_cgame_imports[CG_QL_IMPORT_REFRESH_ADVERT_CELL_SHADER] = (ql_import_f)QL_CG_trap_RefreshAdvertCellShader;
	ql_cgame_imports[CG_QL_IMPORT_SET_ACTIVE_ADVERT] = (ql_import_f)QL_CG_trap_SetActiveAdvert;
	ql_cgame_imports[CG_QL_IMPORT_UPDATE_ADVERT] = (ql_import_f)QL_CG_trap_UpdateAdvert;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_SET_MAP_PATH] = (ql_import_f)QL_CG_trap_AdvertisementBridge_SetMapPath;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_INITCGAME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_InitCGame;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_ShutdownCGame;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_UPDATE_VIEW_PARAMETERS] = (ql_import_f)QL_CG_trap_AdvertisementBridge_UpdateViewParameters;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_SETFRAMETIME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_SetFrameTime;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_CLEAR_DELAY] = (ql_import_f)QL_CG_trap_AdvertisementBridge_ClearDelay;
	ql_cgame_imports[CG_QL_IMPORT_R_CLEARSCENE] = (ql_import_f)QL_CG_trap_R_ClearScene;
	ql_cgame_imports[CG_QL_IMPORT_R_ADDREFENTITYTOSCENE] = (ql_import_f)QL_CG_trap_R_AddRefEntityToScene;
	ql_cgame_imports[CG_QL_IMPORT_R_ADDPOLYTOSCENE] = (ql_import_f)QL_CG_trap_R_AddPolyToScene;
	ql_cgame_imports[CG_QL_IMPORT_R_ADDPOLYSTOSCENE] = (ql_import_f)QL_CG_trap_R_AddPolysToScene;
	ql_cgame_imports[CG_QL_IMPORT_R_ADDLIGHTTOSCENE] = (ql_import_f)QL_CG_trap_R_AddLightToScene;
	ql_cgame_imports[CG_QL_IMPORT_R_LIGHTFORPOINT] = (ql_import_f)QL_CG_trap_R_LightForPoint;
	ql_cgame_imports[CG_QL_IMPORT_R_RENDERSCENE] = (ql_import_f)QL_CG_trap_R_RenderScene;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_UPDATE_LOADING_VIEW_PARAMETERS] = (ql_import_f)QL_CG_trap_AdvertisementBridge_UpdateLoadingViewParameters;
	ql_cgame_imports[CG_QL_IMPORT_R_SETCOLOR] = (ql_import_f)QL_CG_trap_R_SetColor_QL;
	ql_cgame_imports[CG_QL_IMPORT_R_DRAWSTRETCHPIC] = (ql_import_f)QL_CG_trap_R_DrawStretchPic;
	ql_cgame_imports[CG_QL_IMPORT_R_MODELBOUNDS] = (ql_import_f)QL_CG_trap_R_ModelBounds;
	ql_cgame_imports[CG_QL_IMPORT_R_LERPTAG] = (ql_import_f)QL_CG_trap_R_LerpTag;
	ql_cgame_imports[CG_QL_IMPORT_R_REMAP_SHADER] = (ql_import_f)QL_CG_trap_R_RemapShader;
	ql_cgame_imports[CG_QL_IMPORT_GETGLCONFIG] = (ql_import_f)QL_CG_trap_GetGlconfig;
	ql_cgame_imports[CG_QL_IMPORT_GETGAMESTATE] = (ql_import_f)QL_CG_trap_GetGameState;
	ql_cgame_imports[CG_QL_IMPORT_GETCURRENTSNAPSHOTNUMBER] = (ql_import_f)QL_CG_trap_GetCurrentSnapshotNumber;
	ql_cgame_imports[CG_QL_IMPORT_GETSNAPSHOT] = (ql_import_f)QL_CG_trap_GetSnapshot;
	ql_cgame_imports[CG_QL_IMPORT_GETSERVERCOMMAND] = (ql_import_f)QL_CG_trap_GetServerCommand;
	ql_cgame_imports[CG_QL_IMPORT_GETCURRENTCMDNUMBER] = (ql_import_f)QL_CG_trap_GetCurrentCmdNumber;
	ql_cgame_imports[CG_QL_IMPORT_GETUSERCMD] = (ql_import_f)QL_CG_trap_GetUserCmd;
	ql_cgame_imports[CG_QL_IMPORT_SETUSERCMDVALUE] = (ql_import_f)QL_CG_trap_SetUserCmdValue;
	ql_cgame_imports[CG_QL_IMPORT_MEMORY_REMAINING] = (ql_import_f)QL_CG_trap_MemoryRemaining;
	ql_cgame_imports[CG_QL_IMPORT_R_REGISTERFONT] = (ql_import_f)QL_CG_trap_R_RegisterFont;
	ql_cgame_imports[CG_QL_IMPORT_KEY_ISDOWN] = (ql_import_f)QL_CG_trap_Key_IsDown;
	ql_cgame_imports[CG_QL_IMPORT_KEY_GETCATCHER] = (ql_import_f)QL_CG_trap_Key_GetCatcher;
	ql_cgame_imports[CG_QL_IMPORT_KEY_SETCATCHER] = (ql_import_f)QL_CG_trap_Key_SetCatcher;
	ql_cgame_imports[CG_QL_IMPORT_KEY_GETKEY] = (ql_import_f)QL_CG_trap_Key_GetKey;
	ql_cgame_imports[CG_QL_IMPORT_KEY_KEYNUMTOSTRINGBUF] = (ql_import_f)QL_CG_trap_Key_KeynumToStringBuf;
	ql_cgame_imports[CG_QL_IMPORT_KEY_GETBINDINGBUF] = (ql_import_f)QL_CG_trap_Key_GetBindingBuf;
	ql_cgame_imports[CG_QL_IMPORT_CIN_PLAYCINEMATIC] = (ql_import_f)QL_CG_trap_CIN_PlayCinematic;
	ql_cgame_imports[CG_QL_IMPORT_CIN_STOPCINEMATIC] = (ql_import_f)QL_CG_trap_CIN_StopCinematic;
	ql_cgame_imports[CG_QL_IMPORT_CIN_RUNCINEMATIC] = (ql_import_f)QL_CG_trap_CIN_RunCinematic;
	ql_cgame_imports[CG_QL_IMPORT_CIN_DRAWCINEMATIC] = (ql_import_f)QL_CG_trap_CIN_DrawCinematic;
	ql_cgame_imports[CG_QL_IMPORT_CIN_SETEXTENTS] = (ql_import_f)QL_CG_trap_CIN_SetExtents;
	ql_cgame_imports[CG_QL_IMPORT_GET_ENTITY_TOKEN] = (ql_import_f)QL_CG_trap_GetEntityToken;
	ql_cgame_imports[CG_QL_IMPORT_PC_LOAD_SOURCE] = (ql_import_f)QL_CG_trap_PC_LoadSource;
	ql_cgame_imports[CG_QL_IMPORT_PC_FREE_SOURCE] = (ql_import_f)QL_CG_trap_PC_FreeSource;
	ql_cgame_imports[CG_QL_IMPORT_PC_READ_TOKEN] = (ql_import_f)QL_CG_trap_PC_ReadToken;
	ql_cgame_imports[CG_QL_IMPORT_PC_SOURCE_FILE_AND_LINE] = (ql_import_f)QL_CG_trap_PC_SourceFileAndLine;
	ql_cgame_imports[CG_QL_IMPORT_TAGGED_CVAR_STRING_BUFFER] = (ql_import_f)QL_CG_trap_TaggedCvarStringBuffer;
	ql_cgame_imports[CG_QL_IMPORT_R_MIRROR_POINT] = (ql_import_f)QL_CG_trap_R_MirrorPoint;
	ql_cgame_imports[CG_QL_IMPORT_R_MIRROR_VECTOR] = (ql_import_f)QL_CG_trap_R_MirrorVector;
	ql_cgame_imports[CG_QL_IMPORT_DRAW_SCALED_TEXT] = (ql_import_f)QL_CG_trap_DrawScaledText;
	ql_cgame_imports[CG_QL_IMPORT_MEASURE_TEXT] = (ql_import_f)QL_CG_trap_MeasureText;
	ql_cgame_imports[CG_QL_IMPORT_IS_CLIENT_MUTED] = (ql_import_f)QL_CG_trap_IsClientMuted;
	ql_cgame_imports[CG_QL_IMPORT_TOGGLE_CLIENT_MUTE] = (ql_import_f)QL_CG_trap_ToggleClientMute;
	ql_cgame_imports[CG_QL_IMPORT_GET_AVATAR_IMAGE_HANDLE] = (ql_import_f)QL_CG_trap_GetAvatarImageHandle;

	ql_cgame_imports[CG_QL_IMPORT_COMPAT_CM_LOADMODEL] = (ql_import_f)QL_CG_trap_CM_LoadModel;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_S_ADDREALLOOPINGSOUND] = (ql_import_f)QL_CG_trap_S_AddRealLoopingSound;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_S_STOPLOOPINGSOUND] = (ql_import_f)QL_CG_trap_S_StopLoopingSound;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_R_ADDADDITIVELIGHTTOSCENE] = (ql_import_f)QL_CG_trap_R_AddAdditiveLightToScene;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_R_INPVS] = (ql_import_f)QL_CG_trap_R_inPVS;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_KEY_SETBINDING] = (ql_import_f)QL_CG_trap_Key_SetBinding;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_KEY_GETOVERSTRIKEMODE] = (ql_import_f)QL_CG_trap_Key_GetOverstrikeMode;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_KEY_SETOVERSTRIKEMODE] = (ql_import_f)QL_CG_trap_Key_SetOverstrikeMode;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_CMD_EXECUTETEXT] = (ql_import_f)QL_CG_trap_Cmd_ExecuteText;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_PC_ADD_GLOBAL_DEFINE] = (ql_import_f)QL_CG_trap_PC_AddGlobalDefine;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_REAL_TIME] = (ql_import_f)QL_CG_trap_RealTime;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_SNAPVECTOR] = (ql_import_f)QL_CG_trap_SnapVector;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_MEMSET] = (ql_import_f)QL_CG_trap_Memset;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_MEMCPY] = (ql_import_f)QL_CG_trap_Memcpy;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_STRNCPY] = (ql_import_f)QL_CG_trap_Strncpy;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_SIN] = (ql_import_f)QL_CG_trap_Sin;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_COS] = (ql_import_f)QL_CG_trap_Cos;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_ATAN2] = (ql_import_f)QL_CG_trap_Atan2;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_SQRT] = (ql_import_f)QL_CG_trap_Sqrt;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_FLOOR] = (ql_import_f)QL_CG_trap_Floor;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_CEIL] = (ql_import_f)QL_CG_trap_Ceil;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_TESTPRINTINT] = (ql_import_f)QL_CG_trap_TestPrintInt;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_TESTPRINTFLOAT] = (ql_import_f)QL_CG_trap_TestPrintFloat;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_ACOS] = (ql_import_f)QL_CG_trap_ACos;
}


/*
====================
CL_LoadCGameVM

Attempts to load the cgame VM, preferring a native module when present.
====================
*/
static vm_t *CL_LoadCGameVM( vmInterpret_t interpret ) {
	vm_t	*vm;

	vm = NULL;
	CL_InitCGameImports();

	if ( interpret != VMI_COMPILED ) {
		vm = VM_Create( "cgame", CL_CgameSystemCalls, VMI_NATIVE, ql_cgame_imports, CGAME_IMPORT_API_VERSION );
		if ( vm ) {
			if ( vm->dllHandle || interpret != VMI_BYTECODE || !vm->compiled ) {
				return vm;
			}
			VM_Free( vm );
			vm = NULL;
		}
	}

	return VM_Create( "cgame", CL_CgameSystemCalls, interpret, ql_cgame_imports, CGAME_IMPORT_API_VERSION );
}

/*
====================
CL_InitCGame

Should only be called by CL_StartHunkUsers
====================
*/
void CL_InitCGame( void ) {
	const char			*info;
	const char			*mapname;
	int					t1, t2;
	vmInterpret_t		interpret;

	t1 = Sys_Milliseconds();

	// put away the console
	Con_Close();

	// find the current mapname
	info = cl.gameState.stringData + cl.gameState.stringOffsets[ CS_SERVERINFO ];
	mapname = Info_ValueForKey( info, "mapname" );
	Com_sprintf( cl.mapname, sizeof( cl.mapname ), "maps/%s.bsp", mapname );

	// load the dll or bytecode
	interpret = Cvar_VariableValue( "vm_cgame" );
	cgvm = CL_LoadCGameVM( interpret );
	if ( !cgvm ) {
		Com_Error( ERR_DROP, "VM_Create on cgame failed" );
	}
	cls.state = CA_LOADING;

	// init for this gamestate
	// use the lastExecutedServerCommand instead of the serverCommandSequence
	// otherwise server commands sent just before a gamestate are dropped
	VM_Call( cgvm, CG_INIT, clc.serverMessageSequence, clc.lastExecutedServerCommand, clc.clientNum );

	// we will send a usercmd this frame, which
	// will cause the server to send us the first snapshot
	cls.state = CA_PRIMED;

	t2 = Sys_Milliseconds();

	Com_Printf( "CL_InitCGame: %5.2f seconds\n", (t2-t1)/1000.0 );

	// have the renderer touch all its images, so they are present
	// on the card even if the driver does deferred loading
	re.EndRegistration();

	// make sure everything is paged in
	if (!Sys_LowPhysicalMemory()) {
		Com_TouchMemory();
	}

	// clear anything that got printed
	Con_ClearNotify ();
}


/*
====================
CL_GameCommand

See if the current console command is claimed by the cgame
====================
*/
qboolean CL_GameCommand( void ) {
	if ( !cgvm ) {
		return qfalse;
	}

	return VM_Call( cgvm, CG_CONSOLE_COMMAND ) ? qtrue : qfalse;
}



/*
=====================
CL_CGameRendering
=====================
*/
void CL_CGameRendering( stereoFrame_t stereo ) {
	qboolean	demoPlaying;

	demoPlaying = clc.demoplaying ? qtrue : qfalse;
	VM_Call( cgvm, CG_DRAW_ACTIVE_FRAME, cl.serverTime, stereo, demoPlaying );
	VM_Debug( 0 );
}


/*
=================
CL_AdjustTimeDelta

Adjust the clients view of server time.

We attempt to have cl.serverTime exactly equal the server's view
of time plus the timeNudge, but with variable latencies over
the internet it will often need to drift a bit to match conditions.

Our ideal time would be to have the adjusted time approach, but not pass,
the very latest snapshot.

Adjustments are only made when a new snapshot arrives with a rational
latency, which keeps the adjustment process framerate independent and
prevents massive overadjustment during times of significant packet loss
or bursted delayed packets.
=================
*/

#define	RESET_TIME	500

static int cl_autoTimeNudgePrevious;

void CL_AdjustTimeDelta( void ) {
	int		resetTime;
	int		newDelta;
	int		deltaDelta;

	cl.newSnapshots = qfalse;

	// the delta never drifts when replaying a demo
	if ( clc.demoplaying ) {
		return;
	}

	// if the current time is WAY off, just correct to the current value
	if ( com_sv_running->integer ) {
		resetTime = 100;
	} else {
		resetTime = RESET_TIME;
	}

	newDelta = cl.snap.serverTime - cls.realtime;
	deltaDelta = abs( newDelta - cl.serverTimeDelta );

	if ( deltaDelta > RESET_TIME ) {
		cl.serverTimeDelta = newDelta;
		cl.oldServerTime = cl.snap.serverTime;	// FIXME: is this a problem for cgame?
		cl.serverTime = cl.snap.serverTime;
		if ( cl_showTimeDelta->integer ) {
			Com_Printf( "<RESET> " );
		}
	} else if ( deltaDelta > 100 ) {
		// fast adjust, cut the difference in half
		if ( cl_showTimeDelta->integer ) {
			Com_Printf( "<FAST> " );
		}
		cl.serverTimeDelta = ( cl.serverTimeDelta + newDelta ) >> 1;
	} else {
		// slow drift adjust, only move 1 or 2 msec

		// if any of the frames between this and the previous snapshot
		// had to be extrapolated, nudge our sense of time back a little
		// the granularity of +1 / -2 is too high for timescale modified frametimes
		if ( com_timescale->value == 0 || com_timescale->value == 1 ) {
			if ( cl.extrapolatedSnapshot ) {
				cl.extrapolatedSnapshot = qfalse;
				cl.serverTimeDelta -= 2;
			} else {
				// otherwise, move our sense of time forward to minimize total latency
				cl.serverTimeDelta++;
			}
		}
	}

	if ( cl_showTimeDelta->integer ) {
		Com_Printf( "%i ", cl.serverTimeDelta );
	}
}

/*
==================
CL_ClampTimeNudge
==================
*/
static int CL_ClampTimeNudge( int tn ) {
	if ( tn < -20 ) {
		return -20;
	} else if ( tn > 0 ) {
		return 0;
	}

	return tn;
}

/*
==================
CL_SelectClientTimeNudge
==================
*/
static int CL_SelectClientTimeNudge( void ) {
	int tn;

	if ( Cvar_VariableIntegerValue( "cg_spectating" ) ) {
		tn = 0;
	} else if ( Sys_IsLANAddress( clc.serverAddress ) ) {
		tn = 0;
	} else if ( !cl_autoTimeNudge->integer ) {
		tn = cl_timeNudge->integer;
	} else {
		tn = (int)( (float)cl.snap.ping * -0.5f );
		if ( cl_autoTimeNudgePrevious != 0 && cl_autoTimeNudgePrevious != tn ) {
			tn = cl_autoTimeNudgePrevious;
		}
	}

	tn = CL_ClampTimeNudge( tn );
	cl_autoTimeNudgePrevious = tn;

	return tn;
}

/*
==================
CL_FirstSnapshot
==================
*/
void CL_FirstSnapshot( void ) {
	// ignore snapshots that don't have entities
	if ( cl.snap.snapFlags & SNAPFLAG_NOT_ACTIVE ) {
		return;
	}
	cls.state = CA_ACTIVE;

	// set the timedelta so we are exactly on this first frame
	cl.serverTimeDelta = cl.snap.serverTime - cls.realtime;
	cl.oldServerTime = cl.snap.serverTime;

	clc.timeDemoBaseTime = cl.snap.serverTime;
	CL_WebView_PublishGameStart();

	// if this is the first frame of active play,
	// execute the contents of activeAction now
	// this is to allow scripting a timedemo to start right
	// after loading
	if ( cl_activeAction->string[0] ) {
		Cbuf_AddText( cl_activeAction->string );
		Cvar_Set( "activeAction", "" );
	}
	
	Sys_BeginProfiling();
}

/*
==================
CL_SetCGameTime
==================
*/
void CL_SetCGameTime( void ) {
	// getting a valid frame message ends the connection process
	if ( cls.state != CA_ACTIVE ) {
		if ( cls.state != CA_PRIMED ) {
			return;
		}
		if ( clc.demoplaying ) {
			// we shouldn't get the first snapshot on the same frame
			// as the gamestate, because it causes a bad time skip
			if ( !clc.firstDemoFrameSkipped ) {
				clc.firstDemoFrameSkipped = qtrue;
				return;
			}
			CL_ReadDemoMessage();
		}
		if ( cl.newSnapshots ) {
			cl.newSnapshots = qfalse;
			CL_FirstSnapshot();
		}
		if ( cls.state != CA_ACTIVE ) {
			return;
		}
	}	

	// if we have gotten to this point, cl.snap is guaranteed to be valid
	if ( !cl.snap.valid ) {
		Com_Error( ERR_DROP, "CL_SetCGameTime: !cl.snap.valid" );
	}

	// allow pause in single player
	if ( sv_paused->integer && cl_paused->integer && com_sv_running->integer ) {
		// paused
		return;
	}

	if ( cl.snap.serverTime < cl.oldFrameServerTime ) {
		Com_Error( ERR_DROP, "cl.snap.serverTime < cl.oldFrameServerTime" );
	}
	cl.oldFrameServerTime = cl.snap.serverTime;


	// get our current view of time

	if ( clc.demoplaying && cl_freezeDemo->integer ) {
		// cl_freezeDemo is used to lock a demo in place for single frame advances

	} else {
		// cl_timeNudge is a user adjustable cvar that allows more
		// or less latency to be added in the interest of better 
		// smoothness or better responsiveness.
		int tn;

		tn = CL_SelectClientTimeNudge();

		cl.serverTime = cls.realtime + cl.serverTimeDelta - tn;

		// guarantee that time will never flow backwards, even if
		// serverTimeDelta made an adjustment or cl_timeNudge was changed
		if ( cl.serverTime < cl.oldServerTime ) {
			cl.serverTime = cl.oldServerTime;
		}
		cl.oldServerTime = cl.serverTime;

		// note if we are almost past the latest frame (without timeNudge),
		// so we will try and adjust back a bit when the next snapshot arrives
		if ( cls.realtime + cl.serverTimeDelta >= cl.snap.serverTime - 5 ) {
			cl.extrapolatedSnapshot = qtrue;
		}
	}

	// if we have gotten new snapshots, drift serverTimeDelta
	// don't do this every frame, or a period of packet loss would
	// make a huge adjustment
	if ( cl.newSnapshots ) {
		CL_AdjustTimeDelta();
	}

	if ( !clc.demoplaying ) {
		return;
	}

	// if we are playing a demo back, we can just keep reading
	// messages from the demo file until the cgame definately
	// has valid snapshots to interpolate between

	// a timedemo will always use a deterministic set of time samples
	// no matter what speed machine it is run on,
	// while a normal demo may have different time samples
	// each time it is played back
	if ( cl_timedemo->integer ) {
		if (!clc.timeDemoStart) {
			clc.timeDemoStart = Sys_Milliseconds();
		}
		clc.timeDemoFrames++;
		cl.serverTime = clc.timeDemoBaseTime + clc.timeDemoFrames * 50;
	}

	while ( cl.serverTime >= cl.snap.serverTime ) {
		// feed another messag, which should change
		// the contents of cl.snap
		CL_ReadDemoMessage();
		if ( cls.state != CA_ACTIVE ) {
			return;		// end of demo
		}
	}

}


