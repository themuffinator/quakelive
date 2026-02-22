#include "platform_steamworks.h"

#if QL_BUILD_STEAMWORKS

#include <string.h>

#ifdef _WIN32
#include <windows.h>
#define QL_STEAMWORKS_LIB_PRIMARY "steam_api64.dll"
#define QL_STEAMWORKS_LIB_SECONDARY "steam_api.dll"
#define QL_STEAMWORKS_SYM( name ) GetProcAddress( (HMODULE)state.library, name )
#define QL_STEAMWORKS_CLOSE() FreeLibrary( (HMODULE)state.library )
#define QL_STEAMWORKS_OPEN( name ) LoadLibraryA( name )
#else
#include <dlfcn.h>
#define QL_STEAMWORKS_LIB_PRIMARY "libsteam_api.so"
#define QL_STEAMWORKS_LIB_SECONDARY "steam_api64.so"
#define QL_STEAMWORKS_SYM( name ) dlsym( state.library, name )
#define QL_STEAMWORKS_CLOSE() dlclose( state.library )
#define QL_STEAMWORKS_OPEN( name ) dlopen( name, RTLD_LAZY | RTLD_LOCAL )
#endif

typedef qboolean (*QL_SteamAPI_InitFn)( void );
typedef void (*QL_SteamAPI_ShutdownFn)( void );
typedef void (*QL_SteamAPI_RunCallbacksFn)( void );
typedef void *(*QL_SteamAPI_InterfaceFn)( void );
typedef void *(*QL_SteamAPI_SteamGameServerFn)( void );
typedef void (*QL_SteamAPI_SteamGameServerRunCallbacksFn)( void );
typedef void *(*QL_SteamAPI_SteamGameServerNetworkingFn)( void );
typedef HAuthTicket (*QL_SteamAPI_GetAuthSessionTicketFn)( void *, void *, int, uint32_t * );
typedef EBeginAuthSessionResult (*QL_SteamAPI_BeginAuthSessionFn)( void *, const void *, int, CSteamID );
typedef void (*QL_SteamAPI_CancelAuthTicketFn)( void *, HAuthTicket );
typedef void (*QL_SteamAPI_EndAuthSessionFn)( void *, CSteamID );
typedef CSteamID (*QL_SteamAPI_GetSteamIDFn)( void * );
typedef qboolean (*QL_SteamNetworking_SendP2PPacketFn)( void *, CSteamID, const void *, uint32_t, int, int );
typedef qboolean (*QL_SteamNetworking_IsP2PPacketAvailableFn)( void *, uint32_t *, int );
typedef qboolean (*QL_SteamNetworking_ReadP2PPacketFn)( void *, void *, uint32_t, uint32_t *, CSteamID *, int );
typedef int (*QL_SteamGameServer_GetNextOutgoingPacketFn)( void *, void *, int, uint32_t *, uint16_t * );

typedef struct {
	void *library;
	qboolean initialised;
	QL_SteamAPI_InitFn SteamAPI_Init;
	QL_SteamAPI_ShutdownFn SteamAPI_Shutdown;
	QL_SteamAPI_RunCallbacksFn SteamAPI_RunCallbacks;
	QL_SteamAPI_InterfaceFn SteamUser;
	QL_SteamAPI_InterfaceFn SteamFriends;
	QL_SteamAPI_InterfaceFn SteamMatchmaking;
	QL_SteamAPI_InterfaceFn SteamApps;
	QL_SteamAPI_InterfaceFn SteamUGC;
	QL_SteamAPI_SteamGameServerFn SteamGameServer;
	QL_SteamAPI_SteamGameServerRunCallbacksFn SteamGameServer_RunCallbacks;
	QL_SteamAPI_SteamGameServerNetworkingFn SteamGameServerNetworking;
	QL_SteamAPI_GetAuthSessionTicketFn GetAuthSessionTicket;
	QL_SteamAPI_BeginAuthSessionFn BeginAuthSession;
	QL_SteamAPI_CancelAuthTicketFn CancelAuthTicket;
	QL_SteamAPI_EndAuthSessionFn EndAuthSession;
	QL_SteamAPI_GetSteamIDFn GetSteamID;
} ql_steamworks_state_t;

static ql_steamworks_state_t state;

/*
=============
QL_Steamworks_ResetState

Clears cached state and function pointers.
=============
*/
static void QL_Steamworks_ResetState( void ) {
	memset( &state, 0, sizeof( state ) );
}

/*
=============
QL_Steamworks_LoadSymbol

Resolves a symbol from the loaded Steam library.
=============
*/
static qboolean QL_Steamworks_LoadSymbol( void **target, const char *name ) {
	if ( !target || !name ) {
		return qfalse;
	}

	*target = QL_STEAMWORKS_SYM( name );

	return *target != NULL;
}

/*
=============
QL_Steamworks_LoadOptionalSymbol

Resolves a symbol without failing if it is missing.
=============
*/
static void QL_Steamworks_LoadOptionalSymbol( void **target, const char *name ) {
	if ( !target || !name ) {
		return;
	}

	*target = QL_STEAMWORKS_SYM( name );
}

/*
=============
QL_Steamworks_LoadLibrary

Dynamically loads the Steamworks runtime and resolves required exports.
=============
*/
qboolean QL_Steamworks_LoadLibrary( void ) {
	if ( state.library ) {
		return qtrue;
	}

	const char *candidates[] = {
		QL_STEAMWORKS_LIB_PRIMARY,
		QL_STEAMWORKS_LIB_SECONDARY
	};

	for ( size_t i = 0; i < sizeof( candidates ) / sizeof( candidates[0] ); ++i ) {
		state.library = QL_STEAMWORKS_OPEN( candidates[i] );
		if ( state.library ) {
			break;
		}
	}

	if ( !state.library ) {
		QL_Steamworks_ResetState();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamAPI_Init, "SteamAPI_Init" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamAPI_Shutdown, "SteamAPI_Shutdown" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamAPI_RunCallbacks, "SteamAPI_RunCallbacks" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamUser, "SteamAPI_SteamUser" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamFriends, "SteamAPI_SteamFriends" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamMatchmaking, "SteamAPI_SteamMatchmaking" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamApps, "SteamAPI_SteamApps" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamUGC, "SteamAPI_SteamUGC" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.GetAuthSessionTicket, "SteamAPI_ISteamUser_GetAuthSessionTicket" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.BeginAuthSession, "SteamAPI_ISteamUser_BeginAuthSession" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.CancelAuthTicket, "SteamAPI_ISteamUser_CancelAuthTicket" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.EndAuthSession, "SteamAPI_ISteamUser_EndAuthSession" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.GetSteamID, "SteamAPI_ISteamUser_GetSteamID" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServer, "SteamGameServer" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServer_RunCallbacks, "SteamGameServer_RunCallbacks" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServerNetworking, "SteamGameServerNetworking" );

	return qtrue;
}

/*
=============
QL_Steamworks_UnloadLibrary

Unloads the Steamworks runtime if it was loaded.
=============
*/
void QL_Steamworks_UnloadLibrary( void ) {
	if ( state.library ) {
		QL_STEAMWORKS_CLOSE();
	}

	QL_Steamworks_ResetState();
}

/*
=============
QL_Steamworks_Init

Initialises the Steamworks runtime, loading the library as needed.
=============
*/
qboolean QL_Steamworks_Init( void ) {
	if ( state.initialised ) {
		return qtrue;
	}

	if ( !QL_Steamworks_LoadLibrary() ) {
		return qfalse;
	}

	if ( !state.SteamAPI_Init() ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	state.initialised = qtrue;
	return qtrue;
}

/*
=============
QL_Steamworks_Shutdown

Shuts down Steamworks and releases any loaded handles.
=============
*/
void QL_Steamworks_Shutdown( void ) {
	if ( !state.initialised ) {
		return;
	}

	state.SteamAPI_Shutdown();
	QL_Steamworks_UnloadLibrary();
}

/*
=============
QL_Steamworks_RunCallbacks

Runs pending Steam callbacks if the runtime is initialised.
=============
*/
void QL_Steamworks_RunCallbacks( void ) {
	if ( !state.initialised || !state.SteamAPI_RunCallbacks ) {
		return;
	}

	state.SteamAPI_RunCallbacks();
}

/*
=============
QL_Steamworks_IsSubscribedApp
=============
*/
qboolean QL_Steamworks_IsSubscribedApp( uint32_t appId ) {
	void *apps;
	void **vtable;

	if ( !state.initialised || !state.SteamApps ) {
		return qfalse;
	}

	apps = state.SteamApps();
	if ( !apps ) {
		return qfalse;
	}

	vtable = *(void ***)apps;
	if ( !vtable ) {
		return qfalse;
	}

	typedef int (__thiscall *QL_SteamApps_BIsSubscribedAppFn)( void *self, uint32_t appId );
	QL_SteamApps_BIsSubscribedAppFn fn = (QL_SteamApps_BIsSubscribedAppFn)vtable[0x1c / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( apps, appId ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetItemDownloadInfo
=============
*/
qboolean QL_Steamworks_GetItemDownloadInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outDownloaded, uint64_t *outTotal ) {
	void *ugc;
	void **vtable;

	if ( !state.initialised || !state.SteamUGC ) {
		return qfalse;
	}

	ugc = state.SteamUGC();
	if ( !ugc ) {
		return qfalse;
	}

	vtable = *(void ***)ugc;
	if ( !vtable ) {
		return qfalse;
	}

	typedef int (__thiscall *QL_SteamUGC_GetItemDownloadInfoFn)( void *self, uint32_t idLow, uint32_t idHigh, uint64_t *outDownloaded, uint64_t *outTotal );
	QL_SteamUGC_GetItemDownloadInfoFn fn = (QL_SteamUGC_GetItemDownloadInfoFn)vtable[0xd8 / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( ugc, idLow, idHigh, outDownloaded, outTotal ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_RunServerCallbacks

Runs Steam server callbacks if the GameServer interface is available.
=============
*/
void QL_Steamworks_RunServerCallbacks( void ) {
	if ( !state.initialised || !state.SteamGameServer_RunCallbacks ) {
		return;
	}

	state.SteamGameServer_RunCallbacks();
}

/*
=============
QL_Steamworks_GetGameServerNetworking

Returns the Steam GameServer networking interface when available.
=============
*/
static void *QL_Steamworks_GetGameServerNetworking( void ) {
	if ( !state.initialised || !state.SteamGameServerNetworking ) {
		return NULL;
	}

	return state.SteamGameServerNetworking();
}

/*
=============
QL_Steamworks_GetGameServer

Returns the Steam GameServer interface when available.
=============
*/
static void *QL_Steamworks_GetGameServer( void ) {
	if ( !state.initialised || !state.SteamGameServer ) {
		return NULL;
	}

	return state.SteamGameServer();
}

/*
=============
QL_Steamworks_ServerSendP2PPacket

Dispatches a P2P packet through the Steam GameServer networking interface.
=============
*/
qboolean QL_Steamworks_ServerSendP2PPacket( const CSteamID *steamId, const void *data, uint32_t length, int sendType, int channel ) {
	void *networking;
	void **vtable;
	QL_SteamNetworking_SendP2PPacketFn sendPacket;

	if ( !steamId || !data || length == 0 ) {
		return qfalse;
	}

	networking = QL_Steamworks_GetGameServerNetworking();
	if ( !networking ) {
		return qfalse;
	}

	vtable = *(void ***)networking;
	if ( !vtable ) {
		return qfalse;
	}

	sendPacket = (QL_SteamNetworking_SendP2PPacketFn)vtable[0];
	if ( !sendPacket ) {
		return qfalse;
	}

	return sendPacket( networking, *steamId, data, length, sendType, channel );
}

/*
=============
QL_Steamworks_ServerIsP2PPacketAvailable

Checks for pending P2P packets for the Steam GameServer networking interface.
=============
*/
qboolean QL_Steamworks_ServerIsP2PPacketAvailable( uint32_t *outSize, int channel ) {
	void *networking;
	void **vtable;
	QL_SteamNetworking_IsP2PPacketAvailableFn isAvailable;

	if ( !outSize ) {
		return qfalse;
	}

	networking = QL_Steamworks_GetGameServerNetworking();
	if ( !networking ) {
		return qfalse;
	}

	vtable = *(void ***)networking;
	if ( !vtable ) {
		return qfalse;
	}

	isAvailable = (QL_SteamNetworking_IsP2PPacketAvailableFn)vtable[1];
	if ( !isAvailable ) {
		return qfalse;
	}

	return isAvailable( networking, outSize, channel );
}

/*
=============
QL_Steamworks_ServerReadP2PPacket

Reads a pending P2P packet from the Steam GameServer networking interface.
=============
*/
qboolean QL_Steamworks_ServerReadP2PPacket( void *data, uint32_t dataSize, uint32_t *outSize, CSteamID *outSteamId, int channel ) {
	void *networking;
	void **vtable;
	QL_SteamNetworking_ReadP2PPacketFn readPacket;

	if ( !data || dataSize == 0 || !outSize || !outSteamId ) {
		return qfalse;
	}

	networking = QL_Steamworks_GetGameServerNetworking();
	if ( !networking ) {
		return qfalse;
	}

	vtable = *(void ***)networking;
	if ( !vtable ) {
		return qfalse;
	}

	readPacket = (QL_SteamNetworking_ReadP2PPacketFn)vtable[2];
	if ( !readPacket ) {
		return qfalse;
	}

	return readPacket( networking, data, dataSize, outSize, outSteamId, channel );
}

/*
=============
QL_Steamworks_ServerGetNextOutgoingPacket

Pulls the next outgoing Steam GameServer packet destined for a UDP socket.
=============
*/
int QL_Steamworks_ServerGetNextOutgoingPacket( void *data, int dataSize, uint32_t *outIp, uint16_t *outPort ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_GetNextOutgoingPacketFn getPacket;
	int index;

	if ( !data || dataSize <= 0 || !outIp || !outPort ) {
		return 0;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return 0;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return 0;
	}

	index = 0x98 / (int)sizeof( void * );
	getPacket = (QL_SteamGameServer_GetNextOutgoingPacketFn)vtable[index];
	if ( !getPacket ) {
		return 0;
	}

	return getPacket( gameServer, data, dataSize, outIp, outPort );
}

/*
=============
QL_Steamworks_HexEncode

Converts binary data to a lower-case hexadecimal representation.
=============
*/
qboolean QL_Steamworks_HexEncode( const uint8_t *data, uint32_t length, char *out, size_t outSize ) {
	static const char *hex = "0123456789abcdef";

	if ( !data || !out || outSize == 0 ) {
		return qfalse;
	}

	size_t required = (size_t)length * 2 + 1;
	if ( outSize < required ) {
		return qfalse;
	}

	for ( uint32_t i = 0; i < length; ++i ) {
		out[i * 2] = hex[data[i] >> 4];
		out[i * 2 + 1] = hex[data[i] & 0x0F];
	}

	out[length * 2] = '\0';
	return qtrue;
}

/*
=============
QL_Steamworks_HexDecode

Decodes a hexadecimal string back into binary data.
=============
*/
qboolean QL_Steamworks_HexDecode( const char *hex, uint8_t *out, size_t outSize, uint32_t *outLength ) {
	if ( !hex || !out ) {
		return qfalse;
	}

	size_t hexLength = strlen( hex );
	if ( hexLength % 2 != 0 ) {
		return qfalse;
	}

	size_t required = hexLength / 2;
	if ( outSize < required ) {
		return qfalse;
	}

	for ( size_t i = 0; i < required; ++i ) {
		char hi = hex[i * 2];
		char lo = hex[i * 2 + 1];

		uint8_t value = 0;

		if ( hi >= '0' && hi <= '9' ) {
			value |= (uint8_t)( (hi - '0') << 4 );
		} else if ( hi >= 'a' && hi <= 'f' ) {
			value |= (uint8_t)( (hi - 'a' + 10) << 4 );
		} else if ( hi >= 'A' && hi <= 'F' ) {
			value |= (uint8_t)( (hi - 'A' + 10) << 4 );
		} else {
			return qfalse;
		}

		if ( lo >= '0' && lo <= '9' ) {
			value |= (uint8_t)( lo - '0' );
		} else if ( lo >= 'a' && lo <= 'f' ) {
			value |= (uint8_t)( lo - 'a' + 10 );
		} else if ( lo >= 'A' && lo <= 'F' ) {
			value |= (uint8_t)( lo - 'A' + 10 );
		} else {
			return qfalse;
		}

		out[i] = value;
	}

	if ( outLength ) {
		*outLength = (uint32_t)required;
	}

	return qtrue;
}

/*
=============
QL_Steamworks_RequestAuthTicket

Requests an auth session ticket and returns it encoded as hex.
=============
*/
qboolean QL_Steamworks_RequestAuthTicket( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle ) {
	if ( !ticketBuffer || ticketBufferSize == 0 ) {
		return qfalse;
	}

	if ( !QL_Steamworks_Init() ) {
		return qfalse;
	}

	void *user = state.SteamUser ? state.SteamUser() : NULL;
	if ( !user || !state.GetAuthSessionTicket ) {
		return qfalse;
	}

	uint8_t rawTicket[1024];
	uint32_t rawLength = 0;
	HAuthTicket handle = state.GetAuthSessionTicket( user, rawTicket, sizeof( rawTicket ), &rawLength );

	if ( handle == 0 || rawLength == 0 ) {
		return qfalse;
	}

	if ( !QL_Steamworks_HexEncode( rawTicket, rawLength, ticketBuffer, ticketBufferSize ) ) {
		return qfalse;
	}

	if ( ticketLength ) {
		*ticketLength = (int)( rawLength * 2 );
	}

	if ( ticketHandle ) {
		*ticketHandle = handle;
	}

	return qtrue;
}

/*
=============
QL_Steamworks_MapAuthResult

Converts a BeginAuthSession result into a ql_auth_response_t.
=============
*/
static void QL_Steamworks_MapAuthResult( EBeginAuthSessionResult result, ql_auth_response_t *response ) {
	if ( !response ) {
		return;
	}

	switch ( result ) {
		case k_EBeginAuthSessionResultOK:
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ACCEPTED, "Steam ticket accepted" );
			break;
		case k_EBeginAuthSessionResultDuplicateRequest:
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_PENDING, "Steam already processing auth ticket" );
			break;
		case k_EBeginAuthSessionResultInvalidTicket:
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED, "Steam ticket invalid" );
			break;
		case k_EBeginAuthSessionResultInvalidVersion:
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED, "Steam ticket version mismatch" );
			break;
		case k_EBeginAuthSessionResultGameMismatch:
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED, "Steam ticket issued for another game" );
			break;
		case k_EBeginAuthSessionResultExpiredTicket:
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_PENDING, "Steam ticket expired, request refresh" );
			break;
		default:
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, "Steam returned unknown auth result (%d)", (int)result );
			break;
	}
}

/*
=============
QL_Steamworks_ValidateTicket

Validates a hex-encoded auth ticket with Steam and populates a response.
=============
*/
qboolean QL_Steamworks_ValidateTicket( const char *ticketHex, ql_auth_response_t *response ) {
	if ( !ticketHex || !response ) {
		return qfalse;
	}

	if ( !QL_Steamworks_Init() ) {
		QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, "Steam runtime unavailable" );
		return qtrue;
	}

	void *user = state.SteamUser ? state.SteamUser() : NULL;
	if ( !user || !state.BeginAuthSession || !state.GetSteamID ) {
		QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, "Steam user interface unavailable" );
		return qtrue;
	}

	uint8_t ticketData[1024];
	uint32_t ticketLength = 0;

	if ( !QL_Steamworks_HexDecode( ticketHex, ticketData, sizeof( ticketData ), &ticketLength ) ) {
		QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED, "Steam ticket malformed" );
		return qtrue;
	}

	CSteamID steamId = state.GetSteamID( user );
	EBeginAuthSessionResult result = state.BeginAuthSession( user, ticketData, (int)ticketLength, steamId );
	QL_Steamworks_MapAuthResult( result, response );

	if ( result == k_EBeginAuthSessionResultOK && state.EndAuthSession ) {
		state.EndAuthSession( user, steamId );
	}

	return qtrue;
}

#endif
