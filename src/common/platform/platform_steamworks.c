#include "platform_steamworks.h"

#if QL_BUILD_STEAMWORKS

#include <limits.h>
#include <stdlib.h>
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
typedef void (*QL_SteamAPI_RegisterCallbackFn)( void *, int );
typedef void (*QL_SteamAPI_UnregisterCallbackFn)( void * );
typedef void (*QL_SteamAPI_RegisterCallResultFn)( void *, SteamAPICall_t );
typedef void (*QL_SteamAPI_UnregisterCallResultFn)( void *, SteamAPICall_t );
typedef void *(*QL_SteamAPI_InterfaceFn)( void );
typedef qboolean (*QL_SteamAPI_SteamGameServerInitFn)( uint32_t, uint16_t, uint16_t, uint16_t, int, const char * );
typedef void *(*QL_SteamAPI_SteamGameServerFn)( void );
typedef void (*QL_SteamAPI_SteamGameServerShutdownFn)( void );
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
typedef uint32_t (*QL_SteamGameServer_GetPublicIPFn)( void * );
typedef int (*QL_SteamGameServer_GetNextOutgoingPacketFn)( void *, void *, int, uint32_t *, uint16_t * );
typedef void (*QL_SteamGameServer_EnableHeartbeatsFn)( void *, int );
typedef void (*QL_SteamGameServer_SetDedicatedFn)( void *, int );
typedef void (*QL_SteamGameServer_LogOnFn)( void *, const char * );
typedef void (*QL_SteamGameServer_LogOnAnonymousFn)( void * );
typedef void (*QL_SteamGameServer_SetStringFn)( void *, const char * );
typedef void (*QL_SteamGameServer_SetIntFn)( void *, int );
typedef void (*QL_SteamGameServer_SetKeyValueFn)( void *, const char *, const char * );
typedef int (*QL_SteamGameServer_UpdateUserDataFn)( void *, uint32_t, uint32_t, const char *, uint32_t );

#if defined(_MSC_VER) && defined(_M_IX86)
#define QL_STEAMWORKS_THISCALL __thiscall
#elif defined(__GNUC__) && defined(__i386__)
#define QL_STEAMWORKS_THISCALL __attribute__((thiscall))
#else
#define QL_STEAMWORKS_THISCALL
#endif

typedef struct {
	CSteamID steamIDFriend;
	char connect[QL_STEAM_COMMAND_LENGTH];
} ql_steam_game_rich_presence_join_requested_raw_t;

typedef struct {
	uint64_t gameId;
	int result;
	CSteamID steamIDUser;
} ql_steam_user_stats_received_raw_t;

typedef struct {
	CSteamID steamID;
	uint32_t changeFlags;
} ql_steam_persona_state_change_raw_t;

typedef struct {
	CSteamID remoteId;
} ql_steam_p2p_session_request_raw_t;

typedef struct {
	char server[64];
	char password[64];
} ql_steam_game_server_change_requested_raw_t;

typedef struct {
	CSteamID steamIDFriend;
	uint32_t appId;
} ql_steam_friend_rich_presence_update_raw_t;

typedef struct {
	uint64_t queryHandle;
	int result;
	uint32_t numResultsReturned;
	uint32_t totalMatchingResults;
	qboolean cachedData;
	char nextCursor[256];
} ql_steam_ugc_query_completed_raw_t;

typedef struct {
	uint32_t appId;
	uint32_t reserved;
	uint32_t itemIdLow;
	uint32_t itemIdHigh;
} ql_steam_item_installed_raw_t;

typedef struct {
	uint32_t appId;
	uint32_t reserved;
	uint32_t itemIdLow;
	uint32_t itemIdHigh;
	int result;
} ql_steam_download_item_result_raw_t;

typedef struct {
	int result;
	CSteamID lobbyId;
} ql_steam_lobby_created_raw_t;

typedef struct {
	CSteamID lobbyId;
	uint32_t chatPermissions;
	qboolean locked;
	uint32_t response;
} ql_steam_lobby_enter_raw_t;

typedef struct {
	CSteamID lobbyId;
	CSteamID changedUser;
	CSteamID makingChangeUser;
	uint32_t stateChange;
} ql_steam_lobby_chat_update_raw_t;

typedef struct {
	CSteamID lobbyId;
	CSteamID chatter;
	int chatEntryType;
	int chatId;
} ql_steam_lobby_chat_message_raw_t;

typedef struct {
	CSteamID lobbyId;
	CSteamID memberId;
	qboolean success;
} ql_steam_lobby_data_update_raw_t;

typedef struct {
	CSteamID lobbyId;
	CSteamID serverId;
	uint32_t serverIp;
	uint16_t serverPort;
} ql_steam_lobby_game_created_raw_t;

typedef struct {
	CSteamID lobbyId;
	CSteamID adminId;
	qboolean disconnected;
} ql_steam_lobby_kicked_raw_t;

typedef struct {
	CSteamID lobbyId;
	CSteamID friendId;
} ql_steam_game_lobby_join_requested_raw_t;

typedef struct {
	uint32_t appId;
	uint64_t orderId;
	qboolean authorized;
} ql_steam_microtxn_authorization_response_raw_t;

typedef struct {
	uint8_t reserved;
} ql_steam_servers_connected_raw_t;

typedef struct {
	int result;
	qboolean stillRetrying;
} ql_steam_server_connect_failure_raw_t;

typedef struct {
	int result;
} ql_steam_servers_disconnected_raw_t;

typedef struct {
	CSteamID steamId;
	int authSessionResponse;
	CSteamID ownerSteamId;
} ql_steam_validate_auth_ticket_response_raw_t;

typedef struct {
	uint64_t gameId;
	uint32_t gameIp;
	uint16_t gamePort;
	uint16_t queryPort;
	CSteamID lobbyId;
	CSteamID gameServerId;
} ql_steam_friend_game_info_t;

typedef struct ql_steam_callback_base_s ql_steam_callback_base_t;

typedef void (QL_STEAMWORKS_THISCALL *ql_steam_callback_run_fn)( ql_steam_callback_base_t *self, void *payload );
typedef void (QL_STEAMWORKS_THISCALL *ql_steam_callback_run_call_result_fn)( ql_steam_callback_base_t *self, void *payload, qboolean ioFailure, SteamAPICall_t callHandle );
typedef int (QL_STEAMWORKS_THISCALL *ql_steam_callback_get_size_fn)( ql_steam_callback_base_t *self );

typedef struct {
	ql_steam_callback_run_fn run;
	ql_steam_callback_run_call_result_fn runCallResult;
	ql_steam_callback_get_size_fn getSize;
} ql_steam_callback_vtable_t;

struct ql_steam_callback_base_s {
	const ql_steam_callback_vtable_t *vtable;
	uint8_t callbackFlags;
	uint8_t reserved[3];
	int callbackId;
	int payloadSize;
	void *context;
	void (*dispatch)( void *context, const void *payload );
	void (*dispatchCallResult)( void *context, const void *payload, qboolean ioFailure, SteamAPICall_t callHandle );
};

typedef struct {
	ql_steam_client_callback_bindings_t bindings;
	qboolean registered;
	SteamAPICall_t ugcCallHandle;
	qboolean ugcCallBound;
	ql_steam_callback_base_t richPresenceJoinRequested;
	ql_steam_callback_base_t userStatsReceived;
	ql_steam_callback_base_t personaStateChange;
	ql_steam_callback_base_t p2pSessionRequest;
	ql_steam_callback_base_t gameServerChangeRequested;
	ql_steam_callback_base_t friendRichPresenceUpdate;
	ql_steam_callback_base_t ugcQueryCompleted;
} ql_steam_client_callback_state_t;

typedef struct {
	ql_steam_lobby_callback_bindings_t bindings;
	qboolean registered;
	ql_steam_callback_base_t lobbyCreated;
	ql_steam_callback_base_t lobbyEnter;
	ql_steam_callback_base_t lobbyChatUpdate;
	ql_steam_callback_base_t lobbyChatMessage;
	ql_steam_callback_base_t lobbyDataUpdate;
	ql_steam_callback_base_t lobbyGameCreated;
	ql_steam_callback_base_t lobbyKicked;
	ql_steam_callback_base_t gameLobbyJoinRequested;
} ql_steam_lobby_callback_state_t;

typedef struct {
	ql_steam_micro_callback_bindings_t bindings;
	qboolean registered;
	ql_steam_callback_base_t authorizationResponse;
} ql_steam_micro_callback_state_t;

typedef struct {
	ql_steam_workshop_callback_bindings_t bindings;
	qboolean registered;
	ql_steam_callback_base_t itemInstalled;
	ql_steam_callback_base_t downloadItemResult;
} ql_steam_workshop_callback_state_t;

typedef struct {
	ql_steam_server_callback_bindings_t bindings;
	qboolean registered;
	ql_steam_callback_base_t serversConnected;
	ql_steam_callback_base_t connectFailure;
	ql_steam_callback_base_t serversDisconnected;
	ql_steam_callback_base_t validateAuthTicketResponse;
	ql_steam_callback_base_t p2pSessionRequest;
} ql_steam_server_callback_state_t;

typedef struct {
	void *library;
	qboolean initialised;
	QL_SteamAPI_InitFn SteamAPI_Init;
	QL_SteamAPI_ShutdownFn SteamAPI_Shutdown;
	QL_SteamAPI_RunCallbacksFn SteamAPI_RunCallbacks;
	QL_SteamAPI_RegisterCallbackFn SteamAPI_RegisterCallback;
	QL_SteamAPI_UnregisterCallbackFn SteamAPI_UnregisterCallback;
	QL_SteamAPI_RegisterCallResultFn SteamAPI_RegisterCallResult;
	QL_SteamAPI_UnregisterCallResultFn SteamAPI_UnregisterCallResult;
	QL_SteamAPI_InterfaceFn SteamUser;
	QL_SteamAPI_InterfaceFn SteamFriends;
	QL_SteamAPI_InterfaceFn SteamNetworking;
	QL_SteamAPI_InterfaceFn SteamUtils;
	QL_SteamAPI_InterfaceFn SteamUserStats;
	QL_SteamAPI_InterfaceFn SteamMatchmaking;
	QL_SteamAPI_InterfaceFn SteamApps;
	QL_SteamAPI_InterfaceFn SteamUGC;
	QL_SteamAPI_InterfaceFn SteamGameServerUGC;
	QL_SteamAPI_SteamGameServerInitFn SteamGameServer_Init;
	QL_SteamAPI_SteamGameServerFn SteamGameServer;
	QL_SteamAPI_InterfaceFn SteamGameServerStats;
	QL_SteamAPI_SteamGameServerShutdownFn SteamGameServer_Shutdown;
	QL_SteamAPI_SteamGameServerRunCallbacksFn SteamGameServer_RunCallbacks;
	QL_SteamAPI_SteamGameServerNetworkingFn SteamGameServerNetworking;
	QL_SteamAPI_GetAuthSessionTicketFn GetAuthSessionTicket;
	QL_SteamAPI_BeginAuthSessionFn BeginAuthSession;
	QL_SteamAPI_CancelAuthTicketFn CancelAuthTicket;
	QL_SteamAPI_EndAuthSessionFn EndAuthSession;
	QL_SteamAPI_GetSteamIDFn GetSteamID;
	qboolean gameServerInitialised;
	qboolean useGameServerUGC;
	ql_steam_client_callback_state_t clientCallbacks;
	ql_steam_server_callback_state_t serverCallbacks;
	ql_steam_lobby_callback_state_t lobbyCallbacks;
	ql_steam_micro_callback_state_t microCallbacks;
	ql_steam_workshop_callback_state_t workshopCallbacks;
} ql_steamworks_state_t;

static ql_steamworks_state_t state;

#define QL_STEAM_GAMESERVER_VERSION "1069"
#define QL_STEAM_GAMESERVER_MODE_NO_AUTH 2
#define QL_STEAM_GAMESERVER_MODE_AUTH_SECURE 3

#define QL_STEAM_CALLBACK_RICH_PRESENCE_JOIN_REQUESTED 0x151
#define QL_STEAM_CALLBACK_USER_STATS_RECEIVED 0x44d
#define QL_STEAM_CALLBACK_PERSONA_STATE_CHANGE 0x130
#define QL_STEAM_CALLBACK_STEAM_SERVERS_CONNECTED 0x65
#define QL_STEAM_CALLBACK_STEAM_SERVER_CONNECT_FAILURE 0x66
#define QL_STEAM_CALLBACK_STEAM_SERVERS_DISCONNECTED 0x67
#define QL_STEAM_CALLBACK_VALIDATE_AUTH_TICKET_RESPONSE 0x8f
#define QL_STEAM_CALLBACK_P2P_SESSION_REQUEST 0x4b2
#define QL_STEAM_CALLBACK_GAME_SERVER_CHANGE_REQUESTED 0x14c
#define QL_STEAM_CALLBACK_FRIEND_RICH_PRESENCE_UPDATE 0x150
#define QL_STEAM_CALLBACK_UGC_QUERY_COMPLETED 0xd49
#define QL_STEAM_CALLBACK_ITEM_INSTALLED 0xd4d
#define QL_STEAM_CALLBACK_DOWNLOAD_ITEM_RESULT 0xd4e
#define QL_STEAM_CALLBACK_LOBBY_CREATED 0x201
#define QL_STEAM_CALLBACK_LOBBY_ENTER 0x1f8
#define QL_STEAM_CALLBACK_LOBBY_CHAT_UPDATE 0x1fa
#define QL_STEAM_CALLBACK_LOBBY_CHAT_MESSAGE 0x1fb
#define QL_STEAM_CALLBACK_LOBBY_DATA_UPDATE 0x1f9
#define QL_STEAM_CALLBACK_LOBBY_GAME_CREATED 0x1fd
#define QL_STEAM_CALLBACK_LOBBY_KICKED 0x200
#define QL_STEAM_CALLBACK_GAME_LOBBY_JOIN_REQUESTED 0x14d
#define QL_STEAM_CALLBACK_MICROTXN_AUTHORIZATION_RESPONSE 0x98

/*
=============
QL_Steamworks_CallbackRun

Dispatches a normal Steam callback into the retained binding owner.
=============
*/
static void QL_STEAMWORKS_THISCALL QL_Steamworks_CallbackRun( ql_steam_callback_base_t *self, void *payload ) {
	if ( !self || !self->dispatch ) {
		return;
	}

	self->dispatch( self->context, payload );
}

/*
=============
QL_Steamworks_CallbackRunCallResult

Dispatches a Steam call-result into the retained binding owner.
=============
*/
static void QL_STEAMWORKS_THISCALL QL_Steamworks_CallbackRunCallResult( ql_steam_callback_base_t *self, void *payload, qboolean ioFailure, SteamAPICall_t callHandle ) {
	if ( !self ) {
		return;
	}

	if ( self->dispatchCallResult ) {
		self->dispatchCallResult( self->context, payload, ioFailure, callHandle );
		return;
	}

	if ( !ioFailure && self->dispatch ) {
		self->dispatch( self->context, payload );
	}
}

/*
=============
QL_Steamworks_CallbackGetSize

Returns the payload size expected by the Steam callback object.
=============
*/
static int QL_STEAMWORKS_THISCALL QL_Steamworks_CallbackGetSize( ql_steam_callback_base_t *self ) {
	if ( !self ) {
		return 0;
	}

	return self->payloadSize;
}

static const ql_steam_callback_vtable_t ql_steam_callback_vtable = {
	QL_Steamworks_CallbackRun,
	QL_Steamworks_CallbackRunCallResult,
	QL_Steamworks_CallbackGetSize
};

static void QL_Steamworks_MapAuthResult( EBeginAuthSessionResult result, ql_auth_response_t *response );

/*
=============
QL_Steamworks_CopySteamString

Copies a Steam-owned UTF-8 string into a bounded local buffer.
=============
*/
static void QL_Steamworks_CopySteamString( char *buffer, size_t bufferSize, const char *value ) {
	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !value || !value[0] ) {
		return;
	}

	Q_strncpyz( buffer, value, bufferSize );
}

/*
=============
QL_Steamworks_PrepareCallbackObject

Initialises a CCallbackBase-compatible object with the retained binding owner.
=============
*/
static void QL_Steamworks_PrepareCallbackObject( ql_steam_callback_base_t *object, int callbackId, int payloadSize, void *context,
	void (*dispatch)( void *context, const void *payload ),
	void (*dispatchCallResult)( void *context, const void *payload, qboolean ioFailure, SteamAPICall_t callHandle ) ) {
	if ( !object ) {
		return;
	}

	memset( object, 0, sizeof( *object ) );
	object->vtable = &ql_steam_callback_vtable;
	object->callbackId = callbackId;
	object->payloadSize = payloadSize;
	object->context = context;
	object->dispatch = dispatch;
	object->dispatchCallResult = dispatchCallResult;
}

/*
=============
QL_Steamworks_RegisterCallbackObject

Registers one retained callback object with the Steam runtime.
=============
*/
static qboolean QL_Steamworks_RegisterCallbackObject( ql_steam_callback_base_t *object ) {
	if ( !object || !state.SteamAPI_RegisterCallback ) {
		return qfalse;
	}

	state.SteamAPI_RegisterCallback( object, object->callbackId );
	object->callbackFlags |= 0x01;
	return qtrue;
}

/*
=============
QL_Steamworks_UnregisterCallbackObject

Unregisters one retained callback object from the Steam runtime.
=============
*/
static void QL_Steamworks_UnregisterCallbackObject( ql_steam_callback_base_t *object ) {
	if ( !object || !state.SteamAPI_UnregisterCallback ) {
		return;
	}

	if ( !( object->callbackFlags & 0x01 ) ) {
		return;
	}

	state.SteamAPI_UnregisterCallback( object );
	object->callbackFlags &= ~0x01;
}

/*
=============
QL_Steamworks_UnbindCallResultObject

Unregisters one retained call-result object from the Steam runtime.
=============
*/
static void QL_Steamworks_UnbindCallResultObject( ql_steam_callback_base_t *object, SteamAPICall_t *callHandle, qboolean *bound ) {
	if ( !object || !callHandle || !bound || !*bound || !state.SteamAPI_UnregisterCallResult ) {
		return;
	}

	state.SteamAPI_UnregisterCallResult( object, *callHandle );
	*callHandle = 0;
	*bound = qfalse;
}

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

	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamAPI_RegisterCallback, "SteamAPI_RegisterCallback" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamAPI_UnregisterCallback, "SteamAPI_UnregisterCallback" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamAPI_RegisterCallResult, "SteamAPI_RegisterCallResult" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamAPI_UnregisterCallResult, "SteamAPI_UnregisterCallResult" );

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamUser, "SteamAPI_SteamUser" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamFriends, "SteamAPI_SteamFriends" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamNetworking, "SteamAPI_SteamNetworking" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamUtils, "SteamAPI_SteamUtils" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamUserStats, "SteamAPI_SteamUserStats" );

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
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServerStats, "SteamGameServerStats" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServerUGC, "SteamGameServerUGC" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServer_Init, "SteamGameServer_Init" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServer_Shutdown, "SteamGameServer_Shutdown" );
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
	if ( !state.initialised && !state.gameServerInitialised ) {
		return;
	}

	QL_Steamworks_UnregisterServerCallbacks();
	QL_Steamworks_UnregisterWorkshopCallbacks();
	QL_Steamworks_UnregisterMicroCallbacks();
	QL_Steamworks_UnregisterLobbyCallbacks();
	QL_Steamworks_UnregisterClientCallbacks();

	if ( state.initialised && state.SteamAPI_Shutdown ) {
		state.SteamAPI_Shutdown();
	}
	state.initialised = qfalse;
	QL_Steamworks_ServerShutdown();
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
QL_Steamworks_ClearStats
=============
*/
qboolean QL_Steamworks_ClearStats( qboolean achievementsToo ) {
	void *userStats;
	void **vtable;
	typedef int (__fastcall *QL_SteamUserStats_ResetAllStatsFn)( void *self, void *unused, int achievementsToo );
	QL_SteamUserStats_ResetAllStatsFn fn;

	if ( !state.initialised || !state.SteamUserStats ) {
		return qfalse;
	}

	userStats = state.SteamUserStats();
	if ( !userStats ) {
		return qfalse;
	}

	vtable = *(void ***)userStats;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUserStats_ResetAllStatsFn)vtable[0x54 / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( userStats, NULL, achievementsToo ? 1 : 0 ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetPersonaName
=============
*/
qboolean QL_Steamworks_GetPersonaName( char *buffer, size_t bufferSize ) {
	void *friends;
	void **vtable;
	typedef const char *(__fastcall *QL_SteamFriends_GetPersonaNameFn)( void *self, void *unused );
	QL_SteamFriends_GetPersonaNameFn fn;
	const char *personaName;

	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}

	if ( !buffer || bufferSize == 0 || !state.initialised || !state.SteamFriends ) {
		return qfalse;
	}

	friends = state.SteamFriends();
	if ( !friends ) {
		return qfalse;
	}

	vtable = *(void ***)friends;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamFriends_GetPersonaNameFn)vtable[0];
	if ( !fn ) {
		return qfalse;
	}

	personaName = fn( friends, NULL );
	if ( !personaName || !personaName[0] ) {
		return qfalse;
	}

	Q_strncpyz( buffer, personaName, bufferSize );
	return qtrue;
}

/*
=============
QL_Steamworks_GetIPCountry
=============
*/
qboolean QL_Steamworks_GetIPCountry( char *buffer, size_t bufferSize ) {
	void *utils;
	void **vtable;
	typedef const char *(__fastcall *QL_SteamUtils_GetIPCountryFn)( void *self, void *unused );
	QL_SteamUtils_GetIPCountryFn fn;
	const char *country;

	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}

	if ( !buffer || bufferSize == 0 || !state.initialised || !state.SteamUtils ) {
		return qfalse;
	}

	utils = state.SteamUtils();
	if ( !utils ) {
		return qfalse;
	}

	vtable = *(void ***)utils;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUtils_GetIPCountryFn)vtable[0x10 / 4];
	if ( !fn ) {
		return qfalse;
	}

	country = fn( utils, NULL );
	if ( !country || !country[0] ) {
		return qfalse;
	}

	Q_strncpyz( buffer, country, bufferSize );
	return qtrue;
}

/*
=============
QL_Steamworks_CombineIdentityWords
=============
*/
static CSteamID QL_Steamworks_CombineIdentityWords( uint32_t idLow, uint32_t idHigh ) {
	CSteamID steamId;

	steamId.value = ( (uint64_t)idHigh << 32 ) | idLow;
	return steamId;
}

/*
=============
QL_Steamworks_GetInterfaceVTable
=============
*/
static void **QL_Steamworks_GetInterfaceVTable( void *interfaceObject ) {
	if ( !interfaceObject ) {
		return NULL;
	}

	return *(void ***)interfaceObject;
}

/*
=============
QL_Steamworks_GetUserInterface
=============
*/
static void *QL_Steamworks_GetUserInterface( void ) {
	if ( !QL_Steamworks_Init() || !state.SteamUser ) {
		return NULL;
	}

	return state.SteamUser();
}

/*
=============
QL_Steamworks_GetFriendsInterface
=============
*/
static void *QL_Steamworks_GetFriendsInterface( void ) {
	if ( !QL_Steamworks_Init() || !state.SteamFriends ) {
		return NULL;
	}

	return state.SteamFriends();
}

/*
=============
QL_Steamworks_GetNetworkingInterface
=============
*/
static void *QL_Steamworks_GetNetworkingInterface( void ) {
	if ( !QL_Steamworks_Init() || !state.SteamNetworking ) {
		return NULL;
	}

	return state.SteamNetworking();
}

/*
=============
QL_Steamworks_GetMatchmakingInterface
=============
*/
static void *QL_Steamworks_GetMatchmakingInterface( void ) {
	if ( !QL_Steamworks_Init() || !state.SteamMatchmaking ) {
		return NULL;
	}

	return state.SteamMatchmaking();
}

/*
=============
QL_Steamworks_GetUserStatsInterface
=============
*/
static void *QL_Steamworks_GetUserStatsInterface( void ) {
	if ( !QL_Steamworks_Init() || !state.SteamUserStats ) {
		return NULL;
	}

	return state.SteamUserStats();
}

/*
=============
QL_Steamworks_GetUtilsInterface
=============
*/
static void *QL_Steamworks_GetUtilsInterface( void ) {
	if ( !QL_Steamworks_Init() || !state.SteamUtils ) {
		return NULL;
	}

	return state.SteamUtils();
}

/*
=============
QL_Steamworks_GetAppID
=============
*/
uint32_t QL_Steamworks_GetAppID( void ) {
	void *utils;
	void **vtable;
	typedef uint32_t (__fastcall *QL_SteamUtils_GetAppIDFn)( void *self, void *unused );
	QL_SteamUtils_GetAppIDFn fn;

	utils = QL_Steamworks_GetUtilsInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( utils );
	if ( !vtable ) {
		return 0u;
	}

	fn = (QL_SteamUtils_GetAppIDFn)vtable[0x24 / 4];
	if ( !fn ) {
		return 0u;
	}

	return fn( utils, NULL );
}

/*
=============
QL_Steamworks_GetUserSteamID
=============
*/
qboolean QL_Steamworks_GetUserSteamID( uint32_t *outIdLow, uint32_t *outIdHigh ) {
	void *user;
	void **vtable;
	CSteamID steamId;
	typedef CSteamID *(__fastcall *QL_SteamUser_GetSteamIDFn)( void *self, void *unused, CSteamID *outSteamId );
	QL_SteamUser_GetSteamIDFn fn;

	if ( outIdLow ) {
		*outIdLow = 0u;
	}
	if ( outIdHigh ) {
		*outIdHigh = 0u;
	}

	user = QL_Steamworks_GetUserInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( user );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUser_GetSteamIDFn)vtable[0x08 / 4];
	if ( !fn ) {
		return qfalse;
	}

	steamId.value = 0ull;
	fn( user, NULL, &steamId );
	if ( steamId.value == 0ull ) {
		return qfalse;
	}

	if ( outIdLow ) {
		*outIdLow = (uint32_t)( steamId.value & 0xffffffffu );
	}
	if ( outIdHigh ) {
		*outIdHigh = (uint32_t)( ( steamId.value >> 32 ) & 0xffffffffu );
	}

	return qtrue;
}

/*
=============
QL_Steamworks_SetInGameVoiceSpeaking
=============
*/
qboolean QL_Steamworks_SetInGameVoiceSpeaking( uint32_t idLow, uint32_t idHigh, qboolean speaking ) {
	void *friends;
	void **vtable;
	typedef void (__fastcall *QL_SteamFriends_SetInGameVoiceSpeakingFn)( void *self, void *unused, CSteamID steamId, int speaking );
	QL_SteamFriends_SetInGameVoiceSpeakingFn fn;

	if ( !( idLow | idHigh ) ) {
		return qfalse;
	}

	friends = QL_Steamworks_GetFriendsInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( friends );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamFriends_SetInGameVoiceSpeakingFn)vtable[0x6c / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( friends, NULL, QL_Steamworks_CombineIdentityWords( idLow, idHigh ), speaking ? 1 : 0 );
	return qtrue;
}

/*
=============
QL_Steamworks_GetFriendCount
=============
*/
int QL_Steamworks_GetFriendCount( int flags ) {
	void *friends;
	void **vtable;
	typedef int (__fastcall *QL_SteamFriends_GetFriendCountFn)( void *self, void *unused, int flags );
	QL_SteamFriends_GetFriendCountFn fn;

	friends = QL_Steamworks_GetFriendsInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( friends );
	if ( !vtable ) {
		return 0;
	}

	fn = (QL_SteamFriends_GetFriendCountFn)vtable[0x0c / 4];
	if ( !fn ) {
		return 0;
	}

	return fn( friends, NULL, flags );
}

/*
=============
QL_Steamworks_GetFriendByIndex
=============
*/
qboolean QL_Steamworks_GetFriendByIndex( int index, int flags, uint32_t *outIdLow, uint32_t *outIdHigh ) {
	void *friends;
	void **vtable;
	CSteamID steamId;
	typedef CSteamID *(__fastcall *QL_SteamFriends_GetFriendByIndexFn)( void *self, void *unused, CSteamID *outSteamId, int index, int flags );
	QL_SteamFriends_GetFriendByIndexFn fn;

	if ( outIdLow ) {
		*outIdLow = 0u;
	}
	if ( outIdHigh ) {
		*outIdHigh = 0u;
	}

	friends = QL_Steamworks_GetFriendsInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( friends );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamFriends_GetFriendByIndexFn)vtable[0x10 / 4];
	if ( !fn ) {
		return qfalse;
	}

	steamId.value = 0ull;
	fn( friends, NULL, &steamId, index, flags );
	if ( steamId.value == 0ull ) {
		return qfalse;
	}

	if ( outIdLow ) {
		*outIdLow = (uint32_t)( steamId.value & 0xffffffffu );
	}
	if ( outIdHigh ) {
		*outIdHigh = (uint32_t)( ( steamId.value >> 32 ) & 0xffffffffu );
	}

	return qtrue;
}

/*
=============
QL_Steamworks_GetFriendSummary
=============
*/
qboolean QL_Steamworks_GetFriendSummary( uint32_t idLow, uint32_t idHigh, ql_steam_friend_summary_t *outSummary ) {
	void *friends;
	void **vtable;
	CSteamID steamId;
	uint32_t currentAppId;
	typedef int (__fastcall *QL_SteamFriends_GetFriendRelationshipFn)( void *self, void *unused, CSteamID steamId );
	typedef int (__fastcall *QL_SteamFriends_GetFriendPersonaStateFn)( void *self, void *unused, CSteamID steamId );
	typedef const char *(__fastcall *QL_SteamFriends_GetFriendPersonaNameFn)( void *self, void *unused, CSteamID steamId );
	typedef int (__fastcall *QL_SteamFriends_GetFriendGamePlayedFn)( void *self, void *unused, CSteamID steamId, ql_steam_friend_game_info_t *outGameInfo );
	typedef const char *(__fastcall *QL_SteamFriends_GetPlayerNicknameFn)( void *self, void *unused, CSteamID steamId );
	typedef const char *(__fastcall *QL_SteamFriends_GetFriendRichPresenceFn)( void *self, void *unused, CSteamID steamId, const char *key );
	QL_SteamFriends_GetFriendRelationshipFn getRelationshipFn;
	QL_SteamFriends_GetFriendPersonaStateFn getPersonaStateFn;
	QL_SteamFriends_GetFriendPersonaNameFn getFriendNameFn;
	QL_SteamFriends_GetFriendGamePlayedFn getFriendGamePlayedFn;
	QL_SteamFriends_GetPlayerNicknameFn getPlayerNicknameFn;
	QL_SteamFriends_GetFriendRichPresenceFn getFriendRichPresenceFn;
	ql_steam_friend_game_info_t gameInfo;

	if ( !outSummary ) {
		return qfalse;
	}

	memset( outSummary, 0, sizeof( *outSummary ) );
	friends = QL_Steamworks_GetFriendsInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( friends );
	if ( !vtable ) {
		return qfalse;
	}

	getRelationshipFn = (QL_SteamFriends_GetFriendRelationshipFn)vtable[0x14 / 4];
	getPersonaStateFn = (QL_SteamFriends_GetFriendPersonaStateFn)vtable[0x18 / 4];
	getFriendNameFn = (QL_SteamFriends_GetFriendPersonaNameFn)vtable[0x1c / 4];
	getFriendGamePlayedFn = (QL_SteamFriends_GetFriendGamePlayedFn)vtable[0x20 / 4];
	getPlayerNicknameFn = (QL_SteamFriends_GetPlayerNicknameFn)vtable[0x2c / 4];
	getFriendRichPresenceFn = (QL_SteamFriends_GetFriendRichPresenceFn)vtable[0xb4 / 4];
	if ( !getRelationshipFn || !getPersonaStateFn || !getFriendNameFn || !getPlayerNicknameFn || !getFriendRichPresenceFn ) {
		return qfalse;
	}

	steamId = QL_Steamworks_CombineIdentityWords( idLow, idHigh );
	outSummary->steamId = steamId;
	outSummary->relationship = getRelationshipFn( friends, NULL, steamId );
	outSummary->personaState = getPersonaStateFn( friends, NULL, steamId );
	QL_Steamworks_CopySteamString( outSummary->name, sizeof( outSummary->name ), getFriendNameFn( friends, NULL, steamId ) );
	QL_Steamworks_CopySteamString( outSummary->nickname, sizeof( outSummary->nickname ), getPlayerNicknameFn( friends, NULL, steamId ) );
	QL_Steamworks_CopySteamString( outSummary->status, sizeof( outSummary->status ), getFriendRichPresenceFn( friends, NULL, steamId, "status" ) );
	QL_Steamworks_CopySteamString( outSummary->lanIp, sizeof( outSummary->lanIp ), getFriendRichPresenceFn( friends, NULL, steamId, "lanIp" ) );

	currentAppId = QL_Steamworks_GetAppID();
	memset( &gameInfo, 0, sizeof( gameInfo ) );
	if ( getFriendGamePlayedFn && getFriendGamePlayedFn( friends, NULL, steamId, &gameInfo ) ) {
		outSummary->gameId = gameInfo.gameId;
		outSummary->serverIp = gameInfo.gameIp;
		outSummary->serverPort = gameInfo.gamePort;
		outSummary->queryPort = gameInfo.queryPort;
		outSummary->lobbyId = gameInfo.lobbyId;
		outSummary->gameServerId = gameInfo.gameServerId;
		if ( currentAppId != 0u && (uint32_t)( gameInfo.gameId & 0x00ffffffull ) == currentAppId ) {
			outSummary->playingQuake = qtrue;
		}
	}

	return qtrue;
}

/*
=============
QL_Steamworks_ReadLobbyChatMessage

Reads a lobby chat message payload through the mapped matchmaking slot.
=============
*/
static qboolean QL_Steamworks_ReadLobbyChatMessage( uint32_t idLow, uint32_t idHigh, int chatId, CSteamID *outChatter, int *outEntryType, char *buffer, size_t bufferSize ) {
	void *matchmaking;
	void **vtable;
	typedef int (__fastcall *QL_SteamMatchmaking_GetLobbyChatEntryFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, int chatId, CSteamID *outChatter, void *buffer, int bufferSize, int *outEntryType );
	QL_SteamMatchmaking_GetLobbyChatEntryFn fn;
	int readLength;

	if ( outChatter ) {
		outChatter->value = 0ull;
	}
	if ( outEntryType ) {
		*outEntryType = 0;
	}
	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}

	if ( !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamMatchmaking_GetLobbyChatEntryFn)vtable[0x6c / 4];
	if ( !fn ) {
		return qfalse;
	}

	readLength = fn( matchmaking, NULL, idLow, idHigh, chatId, outChatter, buffer, (int)bufferSize, outEntryType );
	if ( readLength <= 0 ) {
		return qfalse;
	}

	buffer[bufferSize - 1] = '\0';
	return qtrue;
}

/*
=============
QL_Steamworks_DispatchRichPresenceJoinRequested
=============
*/
static void QL_Steamworks_DispatchRichPresenceJoinRequested( void *context, const void *payload ) {
	ql_steam_client_callback_state_t *callbackState;
	const ql_steam_game_rich_presence_join_requested_raw_t *raw;
	ql_steam_rich_presence_join_requested_t event;

	callbackState = (ql_steam_client_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onRichPresenceJoinRequested || !payload ) {
		return;
	}

	raw = (const ql_steam_game_rich_presence_join_requested_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.requester.steamId = raw->steamIDFriend;
	QL_Steamworks_GetFriendSummary( (uint32_t)( raw->steamIDFriend.value & 0xffffffffu ), (uint32_t)( raw->steamIDFriend.value >> 32 ), &event.requester );
	QL_Steamworks_CopySteamString( event.command, sizeof( event.command ), raw->connect );
	callbackState->bindings.onRichPresenceJoinRequested( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchUserStatsReceived
=============
*/
static void QL_Steamworks_DispatchUserStatsReceived( void *context, const void *payload ) {
	ql_steam_client_callback_state_t *callbackState;
	const ql_steam_user_stats_received_raw_t *raw;
	ql_steam_user_stats_received_t event;
	ql_steam_friend_summary_t summary;

	callbackState = (ql_steam_client_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onUserStatsReceived || !payload ) {
		return;
	}

	raw = (const ql_steam_user_stats_received_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	memset( &summary, 0, sizeof( summary ) );
	event.steamId = raw->steamIDUser;
	event.gameId = (uint32_t)( raw->gameId & 0xffffffffu );
	event.result = raw->result;
	if ( QL_Steamworks_GetFriendSummary( (uint32_t)( raw->steamIDUser.value & 0xffffffffu ), (uint32_t)( raw->steamIDUser.value >> 32 ), &summary ) ) {
		Q_strncpyz( event.name, summary.name, sizeof( event.name ) );
	}

	callbackState->bindings.onUserStatsReceived( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchPersonaStateChange
=============
*/
static void QL_Steamworks_DispatchPersonaStateChange( void *context, const void *payload ) {
	ql_steam_client_callback_state_t *callbackState;
	const ql_steam_persona_state_change_raw_t *raw;
	ql_steam_persona_state_change_t event;

	callbackState = (ql_steam_client_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onPersonaStateChange || !payload ) {
		return;
	}

	raw = (const ql_steam_persona_state_change_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.steamId = raw->steamID;
	event.changeFlags = raw->changeFlags;
	QL_Steamworks_GetFriendSummary( (uint32_t)( raw->steamID.value & 0xffffffffu ), (uint32_t)( raw->steamID.value >> 32 ), &event.summary );
	callbackState->bindings.onPersonaStateChange( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchP2PSessionRequest
=============
*/
static void QL_Steamworks_DispatchP2PSessionRequest( void *context, const void *payload ) {
	ql_steam_client_callback_state_t *callbackState;
	const ql_steam_p2p_session_request_raw_t *raw;
	ql_steam_p2p_session_request_t event;

	callbackState = (ql_steam_client_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onP2PSessionRequest || !payload ) {
		return;
	}

	raw = (const ql_steam_p2p_session_request_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.remoteId = raw->remoteId;
	callbackState->bindings.onP2PSessionRequest( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchGameServerChangeRequested
=============
*/
static void QL_Steamworks_DispatchGameServerChangeRequested( void *context, const void *payload ) {
	ql_steam_client_callback_state_t *callbackState;
	const ql_steam_game_server_change_requested_raw_t *raw;
	ql_steam_game_server_change_requested_t event;

	callbackState = (ql_steam_client_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onGameServerChangeRequested || !payload ) {
		return;
	}

	raw = (const ql_steam_game_server_change_requested_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	QL_Steamworks_CopySteamString( event.server, sizeof( event.server ), raw->server );
	QL_Steamworks_CopySteamString( event.password, sizeof( event.password ), raw->password );
	callbackState->bindings.onGameServerChangeRequested( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchFriendRichPresenceUpdate
=============
*/
static void QL_Steamworks_DispatchFriendRichPresenceUpdate( void *context, const void *payload ) {
	ql_steam_client_callback_state_t *callbackState;
	const ql_steam_friend_rich_presence_update_raw_t *raw;
	ql_steam_friend_rich_presence_update_t event;

	callbackState = (ql_steam_client_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onFriendRichPresenceUpdate || !payload ) {
		return;
	}

	raw = (const ql_steam_friend_rich_presence_update_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.steamId = raw->steamIDFriend;
	event.appId = raw->appId;
	QL_Steamworks_GetFriendSummary( (uint32_t)( raw->steamIDFriend.value & 0xffffffffu ), (uint32_t)( raw->steamIDFriend.value >> 32 ), &event.summary );
	callbackState->bindings.onFriendRichPresenceUpdate( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchUGCQueryCompleted
=============
*/
static void QL_Steamworks_DispatchUGCQueryCompleted( void *context, const void *payload, qboolean ioFailure, SteamAPICall_t callHandle ) {
	ql_steam_client_callback_state_t *callbackState;
	const ql_steam_ugc_query_completed_raw_t *raw;
	ql_steam_ugc_query_completed_t event;

	callbackState = (ql_steam_client_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onUGCQueryCompleted ) {
		return;
	}

	memset( &event, 0, sizeof( event ) );
	event.callHandle = callHandle;
	if ( payload ) {
		raw = (const ql_steam_ugc_query_completed_raw_t *)payload;
		event.queryHandle = raw->queryHandle;
		event.result = ioFailure ? -1 : raw->result;
		event.numResultsReturned = raw->numResultsReturned;
		event.totalMatchingResults = raw->totalMatchingResults;
		event.cachedData = raw->cachedData ? qtrue : qfalse;
	} else {
		event.result = ioFailure ? -1 : 0;
	}

	callbackState->bindings.onUGCQueryCompleted( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchItemInstalled
=============
*/
static void QL_Steamworks_DispatchItemInstalled( void *context, const void *payload ) {
	ql_steam_workshop_callback_state_t *callbackState;
	const ql_steam_item_installed_raw_t *raw;
	ql_steam_item_installed_t event;

	callbackState = (ql_steam_workshop_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onItemInstalled || !payload ) {
		return;
	}

	raw = (const ql_steam_item_installed_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.appId = raw->appId;
	event.itemIdLow = raw->itemIdLow;
	event.itemIdHigh = raw->itemIdHigh;
	callbackState->bindings.onItemInstalled( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchDownloadItemResult
=============
*/
static void QL_Steamworks_DispatchDownloadItemResult( void *context, const void *payload ) {
	ql_steam_workshop_callback_state_t *callbackState;
	const ql_steam_download_item_result_raw_t *raw;
	ql_steam_download_item_result_t event;

	callbackState = (ql_steam_workshop_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onDownloadItemResult || !payload ) {
		return;
	}

	raw = (const ql_steam_download_item_result_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.appId = raw->appId;
	event.itemIdLow = raw->itemIdLow;
	event.itemIdHigh = raw->itemIdHigh;
	event.result = raw->result;
	callbackState->bindings.onDownloadItemResult( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchLobbyCreated
=============
*/
static void QL_Steamworks_DispatchLobbyCreated( void *context, const void *payload ) {
	ql_steam_lobby_callback_state_t *callbackState;
	const ql_steam_lobby_created_raw_t *raw;
	ql_steam_lobby_created_t event;

	callbackState = (ql_steam_lobby_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onLobbyCreated || !payload ) {
		return;
	}

	raw = (const ql_steam_lobby_created_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.lobbyId = raw->lobbyId;
	event.result = raw->result;
	callbackState->bindings.onLobbyCreated( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchLobbyEnter
=============
*/
static void QL_Steamworks_DispatchLobbyEnter( void *context, const void *payload ) {
	ql_steam_lobby_callback_state_t *callbackState;
	const ql_steam_lobby_enter_raw_t *raw;
	ql_steam_lobby_enter_t event;

	callbackState = (ql_steam_lobby_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onLobbyEnter || !payload ) {
		return;
	}

	raw = (const ql_steam_lobby_enter_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.lobbyId = raw->lobbyId;
	event.chatPermissions = raw->chatPermissions;
	event.permissions = raw->chatPermissions;
	event.locked = raw->locked ? qtrue : qfalse;
	event.response = raw->response;
	callbackState->bindings.onLobbyEnter( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchLobbyChatUpdate
=============
*/
static void QL_Steamworks_DispatchLobbyChatUpdate( void *context, const void *payload ) {
	ql_steam_lobby_callback_state_t *callbackState;
	const ql_steam_lobby_chat_update_raw_t *raw;
	ql_steam_lobby_chat_update_t event;

	callbackState = (ql_steam_lobby_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onLobbyChatUpdate || !payload ) {
		return;
	}

	raw = (const ql_steam_lobby_chat_update_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.lobbyId = raw->lobbyId;
	event.changedUser = raw->changedUser;
	event.makingChangeUser = raw->makingChangeUser;
	event.stateChange = raw->stateChange;
	callbackState->bindings.onLobbyChatUpdate( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchLobbyChatMessage
=============
*/
static void QL_Steamworks_DispatchLobbyChatMessage( void *context, const void *payload ) {
	ql_steam_lobby_callback_state_t *callbackState;
	const ql_steam_lobby_chat_message_raw_t *raw;
	ql_steam_lobby_chat_message_t event;
	CSteamID chatter;
	int entryType;

	callbackState = (ql_steam_lobby_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onLobbyChatMessage || !payload ) {
		return;
	}

	raw = (const ql_steam_lobby_chat_message_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.lobbyId = raw->lobbyId;
	event.chatter = raw->chatter;
	event.chatEntryType = raw->chatEntryType;
	event.chatId = raw->chatId;

	chatter.value = raw->chatter.value;
	entryType = raw->chatEntryType;
	QL_Steamworks_ReadLobbyChatMessage(
		(uint32_t)( raw->lobbyId.value & 0xffffffffu ),
		(uint32_t)( raw->lobbyId.value >> 32 ),
		raw->chatId,
		&chatter,
		&entryType,
		event.message,
		sizeof( event.message )
	);
	event.chatter = chatter;
	event.chatEntryType = entryType;
	callbackState->bindings.onLobbyChatMessage( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchLobbyDataUpdate
=============
*/
static void QL_Steamworks_DispatchLobbyDataUpdate( void *context, const void *payload ) {
	ql_steam_lobby_callback_state_t *callbackState;
	const ql_steam_lobby_data_update_raw_t *raw;
	ql_steam_lobby_data_update_t event;

	callbackState = (ql_steam_lobby_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onLobbyDataUpdate || !payload ) {
		return;
	}

	raw = (const ql_steam_lobby_data_update_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.lobbyId = raw->lobbyId;
	event.memberId = raw->memberId;
	event.success = raw->success ? qtrue : qfalse;
	callbackState->bindings.onLobbyDataUpdate( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchLobbyGameCreated
=============
*/
static void QL_Steamworks_DispatchLobbyGameCreated( void *context, const void *payload ) {
	ql_steam_lobby_callback_state_t *callbackState;
	const ql_steam_lobby_game_created_raw_t *raw;
	ql_steam_lobby_game_created_t event;

	callbackState = (ql_steam_lobby_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onLobbyGameCreated || !payload ) {
		return;
	}

	raw = (const ql_steam_lobby_game_created_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.lobbyId = raw->lobbyId;
	event.serverId = raw->serverId;
	event.serverIp = raw->serverIp;
	event.serverPort = raw->serverPort;
	callbackState->bindings.onLobbyGameCreated( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchLobbyKicked
=============
*/
static void QL_Steamworks_DispatchLobbyKicked( void *context, const void *payload ) {
	ql_steam_lobby_callback_state_t *callbackState;
	const ql_steam_lobby_kicked_raw_t *raw;
	ql_steam_lobby_kicked_t event;

	callbackState = (ql_steam_lobby_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onLobbyKicked || !payload ) {
		return;
	}

	raw = (const ql_steam_lobby_kicked_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.lobbyId = raw->lobbyId;
	event.adminId = raw->adminId;
	event.disconnected = raw->disconnected ? qtrue : qfalse;
	callbackState->bindings.onLobbyKicked( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchGameLobbyJoinRequested
=============
*/
static void QL_Steamworks_DispatchGameLobbyJoinRequested( void *context, const void *payload ) {
	ql_steam_lobby_callback_state_t *callbackState;
	const ql_steam_game_lobby_join_requested_raw_t *raw;
	ql_steam_game_lobby_join_requested_t event;

	callbackState = (ql_steam_lobby_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onGameLobbyJoinRequested || !payload ) {
		return;
	}

	raw = (const ql_steam_game_lobby_join_requested_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.lobbyId = raw->lobbyId;
	event.friendId = raw->friendId;
	callbackState->bindings.onGameLobbyJoinRequested( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchMicroAuthorizationResponse
=============
*/
static void QL_Steamworks_DispatchMicroAuthorizationResponse( void *context, const void *payload ) {
	ql_steam_micro_callback_state_t *callbackState;
	const ql_steam_microtxn_authorization_response_raw_t *raw;
	ql_steam_microtxn_authorization_response_t event;

	callbackState = (ql_steam_micro_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onAuthorizationResponse || !payload ) {
		return;
	}

	raw = (const ql_steam_microtxn_authorization_response_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.appId = raw->appId;
	event.orderId = raw->orderId;
	event.authorized = raw->authorized ? qtrue : qfalse;
	callbackState->bindings.onAuthorizationResponse( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchServersConnected
=============
*/
static void QL_Steamworks_DispatchServersConnected( void *context, const void *payload ) {
	ql_steam_server_callback_state_t *callbackState;
	ql_steam_server_connected_t event;

	(void)payload;

	callbackState = (ql_steam_server_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onServersConnected ) {
		return;
	}

	memset( &event, 0, sizeof( event ) );
	callbackState->bindings.onServersConnected( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchServerConnectFailure
=============
*/
static void QL_Steamworks_DispatchServerConnectFailure( void *context, const void *payload ) {
	ql_steam_server_callback_state_t *callbackState;
	const ql_steam_server_connect_failure_raw_t *raw;
	ql_steam_server_connect_failure_t event;

	callbackState = (ql_steam_server_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onConnectFailure || !payload ) {
		return;
	}

	raw = (const ql_steam_server_connect_failure_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.result = raw->result;
	event.stillRetrying = raw->stillRetrying ? qtrue : qfalse;
	callbackState->bindings.onConnectFailure( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchServersDisconnected
=============
*/
static void QL_Steamworks_DispatchServersDisconnected( void *context, const void *payload ) {
	ql_steam_server_callback_state_t *callbackState;
	const ql_steam_servers_disconnected_raw_t *raw;
	ql_steam_server_disconnected_t event;

	callbackState = (ql_steam_server_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onServersDisconnected || !payload ) {
		return;
	}

	raw = (const ql_steam_servers_disconnected_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.result = raw->result;
	callbackState->bindings.onServersDisconnected( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchValidateAuthTicketResponse
=============
*/
static void QL_Steamworks_DispatchValidateAuthTicketResponse( void *context, const void *payload ) {
	ql_steam_server_callback_state_t *callbackState;
	const ql_steam_validate_auth_ticket_response_raw_t *raw;
	ql_steam_validate_auth_ticket_response_t event;

	callbackState = (ql_steam_server_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onValidateAuthTicketResponse || !payload ) {
		return;
	}

	raw = (const ql_steam_validate_auth_ticket_response_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.steamId = raw->steamId;
	event.ownerSteamId = raw->ownerSteamId;
	event.authSessionResponse = (EAuthSessionResponse)raw->authSessionResponse;
	callbackState->bindings.onValidateAuthTicketResponse( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchServerP2PSessionRequest
=============
*/
static void QL_Steamworks_DispatchServerP2PSessionRequest( void *context, const void *payload ) {
	ql_steam_server_callback_state_t *callbackState;
	const ql_steam_p2p_session_request_raw_t *raw;
	ql_steam_p2p_session_request_t event;

	callbackState = (ql_steam_server_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onP2PSessionRequest || !payload ) {
		return;
	}

	raw = (const ql_steam_p2p_session_request_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.remoteId = raw->remoteId;
	callbackState->bindings.onP2PSessionRequest( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_RegisterClientCallbacks
=============
*/
qboolean QL_Steamworks_RegisterClientCallbacks( const ql_steam_client_callback_bindings_t *bindings ) {
	ql_steam_client_callback_state_t *callbackState;

	if ( !bindings ) {
		return qfalse;
	}

	if ( !QL_Steamworks_Init() || !state.SteamAPI_RegisterCallback ) {
		return qfalse;
	}

	callbackState = &state.clientCallbacks;
	if ( callbackState->registered ) {
		QL_Steamworks_UnregisterClientCallbacks();
	}

	memset( callbackState, 0, sizeof( *callbackState ) );
	memcpy( &callbackState->bindings, bindings, sizeof( callbackState->bindings ) );

	QL_Steamworks_PrepareCallbackObject( &callbackState->richPresenceJoinRequested, QL_STEAM_CALLBACK_RICH_PRESENCE_JOIN_REQUESTED, sizeof( ql_steam_game_rich_presence_join_requested_raw_t ), callbackState, QL_Steamworks_DispatchRichPresenceJoinRequested, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->userStatsReceived, QL_STEAM_CALLBACK_USER_STATS_RECEIVED, sizeof( ql_steam_user_stats_received_raw_t ), callbackState, QL_Steamworks_DispatchUserStatsReceived, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->personaStateChange, QL_STEAM_CALLBACK_PERSONA_STATE_CHANGE, sizeof( ql_steam_persona_state_change_raw_t ), callbackState, QL_Steamworks_DispatchPersonaStateChange, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->p2pSessionRequest, QL_STEAM_CALLBACK_P2P_SESSION_REQUEST, sizeof( ql_steam_p2p_session_request_raw_t ), callbackState, QL_Steamworks_DispatchP2PSessionRequest, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->gameServerChangeRequested, QL_STEAM_CALLBACK_GAME_SERVER_CHANGE_REQUESTED, sizeof( ql_steam_game_server_change_requested_raw_t ), callbackState, QL_Steamworks_DispatchGameServerChangeRequested, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->friendRichPresenceUpdate, QL_STEAM_CALLBACK_FRIEND_RICH_PRESENCE_UPDATE, sizeof( ql_steam_friend_rich_presence_update_raw_t ), callbackState, QL_Steamworks_DispatchFriendRichPresenceUpdate, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->ugcQueryCompleted, QL_STEAM_CALLBACK_UGC_QUERY_COMPLETED, sizeof( ql_steam_ugc_query_completed_raw_t ), callbackState, NULL, QL_Steamworks_DispatchUGCQueryCompleted );

	if ( !QL_Steamworks_RegisterCallbackObject( &callbackState->richPresenceJoinRequested ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->userStatsReceived ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->personaStateChange ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->p2pSessionRequest ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->gameServerChangeRequested ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->friendRichPresenceUpdate ) ) {
		QL_Steamworks_UnregisterClientCallbacks();
		return qfalse;
	}

	callbackState->registered = qtrue;
	return qtrue;
}

/*
=============
QL_Steamworks_UnregisterClientCallbacks
=============
*/
void QL_Steamworks_UnregisterClientCallbacks( void ) {
	ql_steam_client_callback_state_t *callbackState;

	callbackState = &state.clientCallbacks;
	QL_Steamworks_UnbindCallResultObject( &callbackState->ugcQueryCompleted, &callbackState->ugcCallHandle, &callbackState->ugcCallBound );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->friendRichPresenceUpdate );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->gameServerChangeRequested );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->p2pSessionRequest );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->personaStateChange );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->userStatsReceived );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->richPresenceJoinRequested );
	memset( callbackState, 0, sizeof( *callbackState ) );
}

/*
=============
QL_Steamworks_RegisterServerCallbacks
=============
*/
qboolean QL_Steamworks_RegisterServerCallbacks( const ql_steam_server_callback_bindings_t *bindings ) {
	ql_steam_server_callback_state_t *callbackState;

	if ( !bindings ) {
		return qfalse;
	}

	if ( !QL_Steamworks_Init() || !state.SteamAPI_RegisterCallback ) {
		return qfalse;
	}

	callbackState = &state.serverCallbacks;
	if ( callbackState->registered ) {
		QL_Steamworks_UnregisterServerCallbacks();
	}

	memset( callbackState, 0, sizeof( *callbackState ) );
	memcpy( &callbackState->bindings, bindings, sizeof( callbackState->bindings ) );

	QL_Steamworks_PrepareCallbackObject( &callbackState->serversConnected, QL_STEAM_CALLBACK_STEAM_SERVERS_CONNECTED, sizeof( ql_steam_servers_connected_raw_t ), callbackState, QL_Steamworks_DispatchServersConnected, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->connectFailure, QL_STEAM_CALLBACK_STEAM_SERVER_CONNECT_FAILURE, sizeof( ql_steam_server_connect_failure_raw_t ), callbackState, QL_Steamworks_DispatchServerConnectFailure, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->serversDisconnected, QL_STEAM_CALLBACK_STEAM_SERVERS_DISCONNECTED, sizeof( ql_steam_servers_disconnected_raw_t ), callbackState, QL_Steamworks_DispatchServersDisconnected, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->validateAuthTicketResponse, QL_STEAM_CALLBACK_VALIDATE_AUTH_TICKET_RESPONSE, sizeof( ql_steam_validate_auth_ticket_response_raw_t ), callbackState, QL_Steamworks_DispatchValidateAuthTicketResponse, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->p2pSessionRequest, QL_STEAM_CALLBACK_P2P_SESSION_REQUEST, sizeof( ql_steam_p2p_session_request_raw_t ), callbackState, QL_Steamworks_DispatchServerP2PSessionRequest, NULL );

	if ( !QL_Steamworks_RegisterCallbackObject( &callbackState->serversConnected ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->connectFailure ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->serversDisconnected ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->validateAuthTicketResponse ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->p2pSessionRequest ) ) {
		QL_Steamworks_UnregisterServerCallbacks();
		return qfalse;
	}

	callbackState->registered = qtrue;
	return qtrue;
}

/*
=============
QL_Steamworks_UnregisterServerCallbacks
=============
*/
void QL_Steamworks_UnregisterServerCallbacks( void ) {
	ql_steam_server_callback_state_t *callbackState;

	callbackState = &state.serverCallbacks;
	QL_Steamworks_UnregisterCallbackObject( &callbackState->p2pSessionRequest );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->validateAuthTicketResponse );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->serversDisconnected );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->connectFailure );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->serversConnected );
	memset( callbackState, 0, sizeof( *callbackState ) );
}

/*
=============
QL_Steamworks_RegisterLobbyCallbacks
=============
*/
qboolean QL_Steamworks_RegisterLobbyCallbacks( const ql_steam_lobby_callback_bindings_t *bindings ) {
	ql_steam_lobby_callback_state_t *callbackState;

	if ( !bindings ) {
		return qfalse;
	}

	if ( !QL_Steamworks_Init() || !state.SteamAPI_RegisterCallback ) {
		return qfalse;
	}

	callbackState = &state.lobbyCallbacks;
	if ( callbackState->registered ) {
		QL_Steamworks_UnregisterLobbyCallbacks();
	}

	memset( callbackState, 0, sizeof( *callbackState ) );
	memcpy( &callbackState->bindings, bindings, sizeof( callbackState->bindings ) );

	QL_Steamworks_PrepareCallbackObject( &callbackState->lobbyCreated, QL_STEAM_CALLBACK_LOBBY_CREATED, sizeof( ql_steam_lobby_created_raw_t ), callbackState, QL_Steamworks_DispatchLobbyCreated, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->lobbyEnter, QL_STEAM_CALLBACK_LOBBY_ENTER, sizeof( ql_steam_lobby_enter_raw_t ), callbackState, QL_Steamworks_DispatchLobbyEnter, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->lobbyChatUpdate, QL_STEAM_CALLBACK_LOBBY_CHAT_UPDATE, sizeof( ql_steam_lobby_chat_update_raw_t ), callbackState, QL_Steamworks_DispatchLobbyChatUpdate, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->lobbyChatMessage, QL_STEAM_CALLBACK_LOBBY_CHAT_MESSAGE, sizeof( ql_steam_lobby_chat_message_raw_t ), callbackState, QL_Steamworks_DispatchLobbyChatMessage, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->lobbyDataUpdate, QL_STEAM_CALLBACK_LOBBY_DATA_UPDATE, sizeof( ql_steam_lobby_data_update_raw_t ), callbackState, QL_Steamworks_DispatchLobbyDataUpdate, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->lobbyGameCreated, QL_STEAM_CALLBACK_LOBBY_GAME_CREATED, sizeof( ql_steam_lobby_game_created_raw_t ), callbackState, QL_Steamworks_DispatchLobbyGameCreated, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->lobbyKicked, QL_STEAM_CALLBACK_LOBBY_KICKED, sizeof( ql_steam_lobby_kicked_raw_t ), callbackState, QL_Steamworks_DispatchLobbyKicked, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->gameLobbyJoinRequested, QL_STEAM_CALLBACK_GAME_LOBBY_JOIN_REQUESTED, sizeof( ql_steam_game_lobby_join_requested_raw_t ), callbackState, QL_Steamworks_DispatchGameLobbyJoinRequested, NULL );

	if ( !QL_Steamworks_RegisterCallbackObject( &callbackState->lobbyCreated ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->lobbyEnter ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->lobbyChatUpdate ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->lobbyChatMessage ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->lobbyDataUpdate ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->lobbyGameCreated ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->lobbyKicked ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->gameLobbyJoinRequested ) ) {
		QL_Steamworks_UnregisterLobbyCallbacks();
		return qfalse;
	}

	callbackState->registered = qtrue;
	return qtrue;
}

/*
=============
QL_Steamworks_UnregisterLobbyCallbacks
=============
*/
void QL_Steamworks_UnregisterLobbyCallbacks( void ) {
	ql_steam_lobby_callback_state_t *callbackState;

	callbackState = &state.lobbyCallbacks;
	QL_Steamworks_UnregisterCallbackObject( &callbackState->gameLobbyJoinRequested );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->lobbyKicked );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->lobbyGameCreated );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->lobbyDataUpdate );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->lobbyChatMessage );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->lobbyChatUpdate );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->lobbyEnter );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->lobbyCreated );
	memset( callbackState, 0, sizeof( *callbackState ) );
}

/*
=============
QL_Steamworks_RegisterMicroCallbacks
=============
*/
qboolean QL_Steamworks_RegisterMicroCallbacks( const ql_steam_micro_callback_bindings_t *bindings ) {
	ql_steam_micro_callback_state_t *callbackState;

	if ( !bindings ) {
		return qfalse;
	}

	if ( !QL_Steamworks_Init() || !state.SteamAPI_RegisterCallback ) {
		return qfalse;
	}

	callbackState = &state.microCallbacks;
	if ( callbackState->registered ) {
		QL_Steamworks_UnregisterMicroCallbacks();
	}

	memset( callbackState, 0, sizeof( *callbackState ) );
	memcpy( &callbackState->bindings, bindings, sizeof( callbackState->bindings ) );
	QL_Steamworks_PrepareCallbackObject( &callbackState->authorizationResponse, QL_STEAM_CALLBACK_MICROTXN_AUTHORIZATION_RESPONSE, sizeof( ql_steam_microtxn_authorization_response_raw_t ), callbackState, QL_Steamworks_DispatchMicroAuthorizationResponse, NULL );
	if ( !QL_Steamworks_RegisterCallbackObject( &callbackState->authorizationResponse ) ) {
		QL_Steamworks_UnregisterMicroCallbacks();
		return qfalse;
	}

	callbackState->registered = qtrue;
	return qtrue;
}

/*
=============
QL_Steamworks_UnregisterMicroCallbacks
=============
*/
void QL_Steamworks_UnregisterMicroCallbacks( void ) {
	ql_steam_micro_callback_state_t *callbackState;

	callbackState = &state.microCallbacks;
	QL_Steamworks_UnregisterCallbackObject( &callbackState->authorizationResponse );
	memset( callbackState, 0, sizeof( *callbackState ) );
}

/*
=============
QL_Steamworks_RegisterWorkshopCallbacks
=============
*/
qboolean QL_Steamworks_RegisterWorkshopCallbacks( const ql_steam_workshop_callback_bindings_t *bindings ) {
	ql_steam_workshop_callback_state_t *callbackState;

	if ( !bindings ) {
		return qfalse;
	}

	if ( !QL_Steamworks_Init() || !state.SteamAPI_RegisterCallback ) {
		return qfalse;
	}

	callbackState = &state.workshopCallbacks;
	if ( callbackState->registered ) {
		QL_Steamworks_UnregisterWorkshopCallbacks();
	}

	memset( callbackState, 0, sizeof( *callbackState ) );
	memcpy( &callbackState->bindings, bindings, sizeof( callbackState->bindings ) );
	QL_Steamworks_PrepareCallbackObject( &callbackState->itemInstalled, QL_STEAM_CALLBACK_ITEM_INSTALLED, sizeof( ql_steam_item_installed_raw_t ), callbackState, QL_Steamworks_DispatchItemInstalled, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->downloadItemResult, QL_STEAM_CALLBACK_DOWNLOAD_ITEM_RESULT, sizeof( ql_steam_download_item_result_raw_t ), callbackState, QL_Steamworks_DispatchDownloadItemResult, NULL );
	if ( !QL_Steamworks_RegisterCallbackObject( &callbackState->itemInstalled ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->downloadItemResult ) ) {
		QL_Steamworks_UnregisterWorkshopCallbacks();
		return qfalse;
	}

	callbackState->registered = qtrue;
	return qtrue;
}

/*
=============
QL_Steamworks_UnregisterWorkshopCallbacks
=============
*/
void QL_Steamworks_UnregisterWorkshopCallbacks( void ) {
	ql_steam_workshop_callback_state_t *callbackState;

	callbackState = &state.workshopCallbacks;
	QL_Steamworks_UnregisterCallbackObject( &callbackState->downloadItemResult );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->itemInstalled );
	memset( callbackState, 0, sizeof( *callbackState ) );
}

/*
=============
QL_Steamworks_BindUGCQueryCallResult
=============
*/
qboolean QL_Steamworks_BindUGCQueryCallResult( SteamAPICall_t callHandle ) {
	ql_steam_client_callback_state_t *callbackState;

	if ( callHandle == 0 || !state.SteamAPI_RegisterCallResult ) {
		return qfalse;
	}

	callbackState = &state.clientCallbacks;
	if ( !callbackState->registered ) {
		return qfalse;
	}

	QL_Steamworks_UnbindCallResultObject( &callbackState->ugcQueryCompleted, &callbackState->ugcCallHandle, &callbackState->ugcCallBound );
	state.SteamAPI_RegisterCallResult( &callbackState->ugcQueryCompleted, callHandle );
	callbackState->ugcCallHandle = callHandle;
	callbackState->ugcCallBound = qtrue;
	return qtrue;
}

/*
=============
QL_Steamworks_SetRichPresence
=============
*/
qboolean QL_Steamworks_SetRichPresence( const char *key, const char *value ) {
	void *friends;
	void **vtable;
	typedef int (__fastcall *QL_SteamFriends_SetRichPresenceFn)( void *self, void *unused, const char *key, const char *value );
	QL_SteamFriends_SetRichPresenceFn fn;

	if ( !key || !key[0] || !value ) {
		return qfalse;
	}

	friends = QL_Steamworks_GetFriendsInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( friends );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamFriends_SetRichPresenceFn)vtable[0xac / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( friends, NULL, key, value ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_ActivateOverlayToUser
=============
*/
qboolean QL_Steamworks_ActivateOverlayToUser( const char *dialog, uint32_t idLow, uint32_t idHigh ) {
	void *friends;
	void **vtable;
	typedef void (__fastcall *QL_SteamFriends_ActivateGameOverlayToUserFn)( void *self, void *unused, const char *dialog, CSteamID steamId );
	QL_SteamFriends_ActivateGameOverlayToUserFn fn;

	if ( !dialog || !dialog[0] ) {
		return qfalse;
	}

	friends = QL_Steamworks_GetFriendsInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( friends );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamFriends_ActivateGameOverlayToUserFn)vtable[0x74 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( friends, NULL, dialog, QL_Steamworks_CombineIdentityWords( idLow, idHigh ) );
	return qtrue;
}

/*
=============
QL_Steamworks_CreateLobby
=============
*/
qboolean QL_Steamworks_CreateLobby( int maxMembers ) {
	void *matchmaking;
	void **vtable;
	typedef uint64_t (__fastcall *QL_SteamMatchmaking_CreateLobbyFn)( void *self, void *unused, int lobbyType, int maxMembers );
	QL_SteamMatchmaking_CreateLobbyFn fn;

	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !matchmaking ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamMatchmaking_CreateLobbyFn)vtable[0x34 / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( matchmaking, NULL, 2, maxMembers ) != 0 ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_LeaveLobby
=============
*/
qboolean QL_Steamworks_LeaveLobby( uint32_t idLow, uint32_t idHigh ) {
	void *matchmaking;
	void **vtable;
	typedef void (__fastcall *QL_SteamMatchmaking_LeaveLobbyFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamMatchmaking_LeaveLobbyFn fn;

	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !matchmaking ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamMatchmaking_LeaveLobbyFn)vtable[0x3c / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( matchmaking, NULL, idLow, idHigh );
	return qtrue;
}

/*
=============
QL_Steamworks_JoinLobby
=============
*/
qboolean QL_Steamworks_JoinLobby( uint32_t idLow, uint32_t idHigh ) {
	void *matchmaking;
	void **vtable;
	typedef uint64_t (__fastcall *QL_SteamMatchmaking_JoinLobbyFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamMatchmaking_JoinLobbyFn fn;

	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !matchmaking ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamMatchmaking_JoinLobbyFn)vtable[0x38 / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( matchmaking, NULL, idLow, idHigh ) != 0 ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_SetLobbyServer
=============
*/
qboolean QL_Steamworks_SetLobbyServer( uint32_t idLow, uint32_t idHigh, uint32_t serverIp, uint16_t serverPort ) {
	void *user;
	void *matchmaking;
	void **userVTable;
	void **matchmakingVTable;
	CSteamID localSteamId;
	CSteamID lobbyOwnerId;
	typedef CSteamID *(__fastcall *QL_SteamUser_GetSteamIDFn)( void *self, void *unused, CSteamID *outSteamId );
	typedef CSteamID *(__fastcall *QL_SteamMatchmaking_GetLobbyOwnerFn)( void *self, void *unused, CSteamID *outSteamId, uint32_t idLow, uint32_t idHigh );
	typedef void (__fastcall *QL_SteamMatchmaking_SetLobbyGameServerFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, uint32_t serverIp, uint16_t serverPort, uint32_t serverIdLow, uint32_t serverIdHigh );
	QL_SteamUser_GetSteamIDFn getSteamIdFn;
	QL_SteamMatchmaking_GetLobbyOwnerFn getLobbyOwnerFn;
	QL_SteamMatchmaking_SetLobbyGameServerFn setLobbyServerFn;

	user = QL_Steamworks_GetUserInterface();
	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !user || !matchmaking ) {
		return qfalse;
	}

	userVTable = QL_Steamworks_GetInterfaceVTable( user );
	matchmakingVTable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !userVTable || !matchmakingVTable ) {
		return qfalse;
	}

	getSteamIdFn = (QL_SteamUser_GetSteamIDFn)userVTable[0x08 / 4];
	getLobbyOwnerFn = (QL_SteamMatchmaking_GetLobbyOwnerFn)matchmakingVTable[0x8c / 4];
	setLobbyServerFn = (QL_SteamMatchmaking_SetLobbyGameServerFn)matchmakingVTable[0x74 / 4];
	if ( !getSteamIdFn || !getLobbyOwnerFn || !setLobbyServerFn ) {
		return qfalse;
	}

	localSteamId.value = 0;
	lobbyOwnerId.value = 0;
	getSteamIdFn( user, NULL, &localSteamId );
	getLobbyOwnerFn( matchmaking, NULL, &lobbyOwnerId, idLow, idHigh );
	if ( lobbyOwnerId.value != localSteamId.value ) {
		return qfalse;
	}

	setLobbyServerFn( matchmaking, NULL, idLow, idHigh, serverIp, serverPort, idLow, idHigh );
	return qtrue;
}

/*
=============
QL_Steamworks_ShowInviteOverlay
=============
*/
qboolean QL_Steamworks_ShowInviteOverlay( uint32_t idLow, uint32_t idHigh ) {
	void *friends;
	void **vtable;
	typedef void (__fastcall *QL_SteamFriends_ActivateGameOverlayInviteDialogFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamFriends_ActivateGameOverlayInviteDialogFn fn;

	friends = QL_Steamworks_GetFriendsInterface();
	if ( !friends ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( friends );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamFriends_ActivateGameOverlayInviteDialogFn)vtable[0x84 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( friends, NULL, idLow, idHigh );
	return qtrue;
}

/*
=============
QL_Steamworks_SayLobby
=============
*/
qboolean QL_Steamworks_SayLobby( uint32_t idLow, uint32_t idHigh, const char *message ) {
	void *matchmaking;
	void **vtable;
	typedef int (__fastcall *QL_SteamMatchmaking_SendLobbyChatMsgFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *message, int messageLength );
	QL_SteamMatchmaking_SendLobbyChatMsgFn fn;
	int messageLength;

	if ( !message ) {
		return qfalse;
	}

	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !matchmaking ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamMatchmaking_SendLobbyChatMsgFn)vtable[0x68 / 4];
	if ( !fn ) {
		return qfalse;
	}

	messageLength = (int)strlen( message ) + 1;
	return fn( matchmaking, NULL, idLow, idHigh, message, messageLength ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_RequestUserStats
=============
*/
qboolean QL_Steamworks_RequestUserStats( uint32_t idLow, uint32_t idHigh ) {
	void *userStats;
	void **vtable;
	typedef uint64_t (__fastcall *QL_SteamUserStats_RequestUserStatsFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamUserStats_RequestUserStatsFn fn;

	userStats = QL_Steamworks_GetUserStatsInterface();
	if ( !userStats ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( userStats );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUserStats_RequestUserStatsFn)vtable[0x40 / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( userStats, NULL, idLow, idHigh ) != 0 ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetGameServerStatsInterface
=============
*/
static void *QL_Steamworks_GetGameServerStatsInterface( void ) {
	if ( !state.initialised || !state.gameServerInitialised || !state.SteamGameServerStats ) {
		return NULL;
	}

	return state.SteamGameServerStats();
}

/*
=============
QL_Steamworks_ServerRequestUserStats
=============
*/
qboolean QL_Steamworks_ServerRequestUserStats( const CSteamID *steamId ) {
	void *gameServerStats;
	void **vtable;
	typedef uint64_t (__fastcall *QL_SteamGameServerStats_RequestUserStatsFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamGameServerStats_RequestUserStatsFn fn;
	uint32_t idLow;
	uint32_t idHigh;

	if ( !steamId || steamId->value == 0ull ) {
		return qfalse;
	}

	gameServerStats = QL_Steamworks_GetGameServerStatsInterface();
	if ( !gameServerStats ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( gameServerStats );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServerStats_RequestUserStatsFn)vtable[0x00 / 4];
	if ( !fn ) {
		return qfalse;
	}

	idLow = (uint32_t)( steamId->value & 0xffffffffu );
	idHigh = (uint32_t)( ( steamId->value >> 32 ) & 0xffffffffu );
	return fn( gameServerStats, NULL, idLow, idHigh ) != 0 ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_ServerGetUserStatInt
=============
*/
qboolean QL_Steamworks_ServerGetUserStatInt( const CSteamID *steamId, const char *name, int *outValue ) {
	void *gameServerStats;
	void **vtable;
	typedef qboolean (__fastcall *QL_SteamGameServerStats_GetUserStatIntFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, int *outValue );
	QL_SteamGameServerStats_GetUserStatIntFn fn;
	uint32_t idLow;
	uint32_t idHigh;

	if ( outValue ) {
		*outValue = 0;
	}

	if ( !steamId || steamId->value == 0ull || !name || !name[0] || !outValue ) {
		return qfalse;
	}

	gameServerStats = QL_Steamworks_GetGameServerStatsInterface();
	if ( !gameServerStats ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( gameServerStats );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServerStats_GetUserStatIntFn)vtable[0x08 / 4];
	if ( !fn ) {
		return qfalse;
	}

	idLow = (uint32_t)( steamId->value & 0xffffffffu );
	idHigh = (uint32_t)( ( steamId->value >> 32 ) & 0xffffffffu );
	return fn( gameServerStats, NULL, idLow, idHigh, name, outValue ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_ServerGetUserAchievement
=============
*/
qboolean QL_Steamworks_ServerGetUserAchievement( const CSteamID *steamId, const char *name, qboolean *outAchieved ) {
	void *gameServerStats;
	void **vtable;
	typedef qboolean (__fastcall *QL_SteamGameServerStats_GetUserAchievementFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, qboolean *outAchieved );
	QL_SteamGameServerStats_GetUserAchievementFn fn;
	qboolean achieved;
	uint32_t idLow;
	uint32_t idHigh;

	if ( outAchieved ) {
		*outAchieved = qfalse;
	}

	if ( !steamId || steamId->value == 0ull || !name || !name[0] || !outAchieved ) {
		return qfalse;
	}

	gameServerStats = QL_Steamworks_GetGameServerStatsInterface();
	if ( !gameServerStats ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( gameServerStats );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServerStats_GetUserAchievementFn)vtable[0x0c / 4];
	if ( !fn ) {
		return qfalse;
	}

	idLow = (uint32_t)( steamId->value & 0xffffffffu );
	idHigh = (uint32_t)( ( steamId->value >> 32 ) & 0xffffffffu );
	achieved = qfalse;
	if ( !fn( gameServerStats, NULL, idLow, idHigh, name, &achieved ) ) {
		return qfalse;
	}

	*outAchieved = achieved ? qtrue : qfalse;
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetUserStatInt
=============
*/
qboolean QL_Steamworks_ServerSetUserStatInt( const CSteamID *steamId, const char *name, int value ) {
	void *gameServerStats;
	void **vtable;
	typedef qboolean (__fastcall *QL_SteamGameServerStats_SetUserStatIntFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, int value );
	QL_SteamGameServerStats_SetUserStatIntFn fn;
	uint32_t idLow;
	uint32_t idHigh;

	if ( !steamId || steamId->value == 0ull || !name || !name[0] ) {
		return qfalse;
	}

	gameServerStats = QL_Steamworks_GetGameServerStatsInterface();
	if ( !gameServerStats ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( gameServerStats );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServerStats_SetUserStatIntFn)vtable[0x14 / 4];
	if ( !fn ) {
		return qfalse;
	}

	idLow = (uint32_t)( steamId->value & 0xffffffffu );
	idHigh = (uint32_t)( ( steamId->value >> 32 ) & 0xffffffffu );
	return fn( gameServerStats, NULL, idLow, idHigh, name, value ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_ServerSetUserAchievement
=============
*/
qboolean QL_Steamworks_ServerSetUserAchievement( const CSteamID *steamId, const char *name ) {
	void *gameServerStats;
	void **vtable;
	typedef qboolean (__fastcall *QL_SteamGameServerStats_SetUserAchievementFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name );
	QL_SteamGameServerStats_SetUserAchievementFn fn;
	uint32_t idLow;
	uint32_t idHigh;

	if ( !steamId || steamId->value == 0ull || !name || !name[0] ) {
		return qfalse;
	}

	gameServerStats = QL_Steamworks_GetGameServerStatsInterface();
	if ( !gameServerStats ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( gameServerStats );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServerStats_SetUserAchievementFn)vtable[0x1c / 4];
	if ( !fn ) {
		return qfalse;
	}

	idLow = (uint32_t)( steamId->value & 0xffffffffu );
	idHigh = (uint32_t)( ( steamId->value >> 32 ) & 0xffffffffu );
	return fn( gameServerStats, NULL, idLow, idHigh, name ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_ServerStoreUserStats
=============
*/
qboolean QL_Steamworks_ServerStoreUserStats( const CSteamID *steamId ) {
	void *gameServerStats;
	void **vtable;
	typedef qboolean (__fastcall *QL_SteamGameServerStats_StoreUserStatsFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamGameServerStats_StoreUserStatsFn fn;
	uint32_t idLow;
	uint32_t idHigh;

	if ( !steamId || steamId->value == 0ull ) {
		return qfalse;
	}

	gameServerStats = QL_Steamworks_GetGameServerStatsInterface();
	if ( !gameServerStats ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( gameServerStats );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServerStats_StoreUserStatsFn)vtable[0x24 / 4];
	if ( !fn ) {
		return qfalse;
	}

	idLow = (uint32_t)( steamId->value & 0xffffffffu );
	idHigh = (uint32_t)( ( steamId->value >> 32 ) & 0xffffffffu );
	return fn( gameServerStats, NULL, idLow, idHigh ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetUGCInterface
=============
*/
static void *QL_Steamworks_GetUGCInterface( void ) {
	if ( !QL_Steamworks_Init() ) {
		return NULL;
	}

	if ( state.useGameServerUGC && state.gameServerInitialised && state.SteamGameServerUGC ) {
		return state.SteamGameServerUGC();
	}

	if ( !state.SteamUGC ) {
		return NULL;
	}

	return state.SteamUGC();
}

/*
=============
QL_Steamworks_GetNumSubscribedItems

Maps the retail SteamUGC subscribed-item count slot used by workshop startup.
=============
*/
uint32_t QL_Steamworks_GetNumSubscribedItems( void ) {
	void *ugc;
	void **vtable;
	typedef uint32_t (__fastcall *QL_SteamUGC_GetNumSubscribedItemsFn)( void *self, void *unused );
	QL_SteamUGC_GetNumSubscribedItemsFn fn;

	ugc = QL_Steamworks_GetUGCInterface();
	if ( !ugc ) {
		return 0u;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( ugc );
	if ( !vtable ) {
		return 0u;
	}

	fn = (QL_SteamUGC_GetNumSubscribedItemsFn)vtable[0xc8 / 4];
	if ( !fn ) {
		return 0u;
	}

	return fn( ugc, NULL );
}

/*
=============
QL_Steamworks_GetSubscribedItems

Copies the subscribed workshop item IDs through the mapped retail SteamUGC slot.
=============
*/
uint32_t QL_Steamworks_GetSubscribedItems( uint64_t *outItemIds, uint32_t maxItems ) {
	void *ugc;
	void **vtable;
	typedef uint32_t (__fastcall *QL_SteamUGC_GetSubscribedItemsFn)( void *self, void *unused, uint64_t *outItemIds, uint32_t maxItems );
	QL_SteamUGC_GetSubscribedItemsFn fn;

	if ( !outItemIds || maxItems == 0u ) {
		return 0u;
	}

	ugc = QL_Steamworks_GetUGCInterface();
	if ( !ugc ) {
		return 0u;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( ugc );
	if ( !vtable ) {
		return 0u;
	}

	fn = (QL_SteamUGC_GetSubscribedItemsFn)vtable[0xcc / 4];
	if ( !fn ) {
		return 0u;
	}

	return fn( ugc, NULL, outItemIds, maxItems );
}

/*
=============
QL_Steamworks_GetItemInstallInfo

Returns the install folder and metadata for one subscribed workshop item.
=============
*/
qboolean QL_Steamworks_GetItemInstallInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outSizeOnDisk, char *folder, size_t folderSize, uint32_t *outTimestamp ) {
	void *ugc;
	void **vtable;
	typedef int (__fastcall *QL_SteamUGC_GetItemInstallInfoFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, uint64_t *outSizeOnDisk, char *folder, uint32_t folderSize, uint32_t *outTimestamp );
	QL_SteamUGC_GetItemInstallInfoFn fn;

	if ( outSizeOnDisk ) {
		*outSizeOnDisk = 0ull;
	}
	if ( folder && folderSize > 0 ) {
		folder[0] = '\0';
	}
	if ( outTimestamp ) {
		*outTimestamp = 0u;
	}

	if ( !folder || folderSize == 0 ) {
		return qfalse;
	}

	ugc = QL_Steamworks_GetUGCInterface();
	if ( !ugc ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( ugc );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUGC_GetItemInstallInfoFn)vtable[0xd4 / 4];
	if ( !fn ) {
		return qfalse;
	}

	if ( !fn( ugc, NULL, idLow, idHigh, outSizeOnDisk, folder, (uint32_t)folderSize, outTimestamp ) ) {
		if ( folderSize > 0 ) {
			folder[0] = '\0';
		}
		return qfalse;
	}

	folder[folderSize - 1] = '\0';
	return qtrue;
}

/*
=============
QL_Steamworks_GetItemState
=============
*/
uint32_t QL_Steamworks_GetItemState( uint32_t idLow, uint32_t idHigh ) {
	void *ugc;
	void **vtable;
	typedef uint32_t (__fastcall *QL_SteamUGC_GetItemStateFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamUGC_GetItemStateFn fn;

	ugc = QL_Steamworks_GetUGCInterface();
	if ( !ugc ) {
		return 0;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( ugc );
	if ( !vtable ) {
		return 0;
	}

	fn = (QL_SteamUGC_GetItemStateFn)vtable[0xd0 / 4];
	if ( !fn ) {
		return 0;
	}

	return fn( ugc, NULL, idLow, idHigh );
}

/*
=============
QL_Steamworks_SubscribeItem
=============
*/
qboolean QL_Steamworks_SubscribeItem( uint32_t idLow, uint32_t idHigh ) {
	void *ugc;
	void **vtable;
	typedef int (__fastcall *QL_SteamUGC_SubscribeItemFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamUGC_SubscribeItemFn fn;

	ugc = QL_Steamworks_GetUGCInterface();
	if ( !ugc ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( ugc );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUGC_SubscribeItemFn)vtable[0xc0 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( ugc, NULL, idLow, idHigh );
	return qtrue;
}

/*
=============
QL_Steamworks_UnsubscribeItem
=============
*/
qboolean QL_Steamworks_UnsubscribeItem( uint32_t idLow, uint32_t idHigh ) {
	void *ugc;
	void **vtable;
	typedef int (__fastcall *QL_SteamUGC_UnsubscribeItemFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamUGC_UnsubscribeItemFn fn;

	ugc = QL_Steamworks_GetUGCInterface();
	if ( !ugc ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( ugc );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUGC_UnsubscribeItemFn)vtable[0xc4 / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( ugc, NULL, idLow, idHigh ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_DownloadItem
=============
*/
qboolean QL_Steamworks_DownloadItem( uint32_t idLow, uint32_t idHigh, qboolean highPriority ) {
	void *ugc;
	void **vtable;
	typedef int (__fastcall *QL_SteamUGC_DownloadItemFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, int highPriority );
	QL_SteamUGC_DownloadItemFn fn;

	ugc = QL_Steamworks_GetUGCInterface();
	if ( !ugc ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( ugc );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUGC_DownloadItemFn)vtable[0xdc / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( ugc, NULL, idLow, idHigh, highPriority ? 1 : 0 ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetAvatarMethodIndex
=============
*/
static int QL_Steamworks_GetAvatarMethodIndex( ql_steam_avatar_size_t size ) {
	switch ( size ) {
	case QL_STEAM_AVATAR_SMALL:
		return 0x88 / 4;
	case QL_STEAM_AVATAR_MEDIUM:
		return 0x8c / 4;
	case QL_STEAM_AVATAR_LARGE:
	default:
		return 0x90 / 4;
	}
}

/*
=============
QL_Steamworks_LoadAvatarRGBA
=============
*/
qboolean QL_Steamworks_LoadAvatarRGBA( uint32_t idLow, uint32_t idHigh, ql_steam_avatar_size_t size, uint8_t **outPixels, uint32_t *outWidth, uint32_t *outHeight ) {
	void *friends;
	void *utils;
	void **friendsVTable;
	void **utilsVTable;
	typedef int (__fastcall *QL_SteamFriends_GetAvatarFn)( void *self, void *unused, CSteamID steamId );
	typedef int (__fastcall *QL_SteamUtils_GetImageSizeFn)( void *self, void *unused, int image, uint32_t *width, uint32_t *height );
	typedef int (__fastcall *QL_SteamUtils_GetImageRGBAFn)( void *self, void *unused, int image, uint8_t *buffer, int length );
	QL_SteamFriends_GetAvatarFn getAvatar;
	QL_SteamUtils_GetImageSizeFn getImageSize;
	QL_SteamUtils_GetImageRGBAFn getImageRGBA;
	CSteamID steamId;
	int image;
	uint32_t width;
	uint32_t height;
	size_t pixelCount;
	size_t bufferSize;
	uint8_t *pixels;

	if ( outPixels ) {
		*outPixels = NULL;
	}
	if ( outWidth ) {
		*outWidth = 0;
	}
	if ( outHeight ) {
		*outHeight = 0;
	}

	if ( !outPixels || !outWidth || !outHeight ) {
		return qfalse;
	}

	if ( !QL_Steamworks_Init() || !state.SteamFriends || !state.SteamUtils ) {
		return qfalse;
	}

	friends = state.SteamFriends();
	utils = state.SteamUtils();
	if ( !friends || !utils ) {
		return qfalse;
	}

	friendsVTable = QL_Steamworks_GetInterfaceVTable( friends );
	utilsVTable = QL_Steamworks_GetInterfaceVTable( utils );
	if ( !friendsVTable || !utilsVTable ) {
		return qfalse;
	}

	getAvatar = (QL_SteamFriends_GetAvatarFn)friendsVTable[QL_Steamworks_GetAvatarMethodIndex( size )];
	getImageSize = (QL_SteamUtils_GetImageSizeFn)utilsVTable[0x14 / 4];
	getImageRGBA = (QL_SteamUtils_GetImageRGBAFn)utilsVTable[0x18 / 4];
	if ( !getAvatar || !getImageSize || !getImageRGBA ) {
		return qfalse;
	}

	steamId = QL_Steamworks_CombineIdentityWords( idLow, idHigh );
	image = getAvatar( friends, NULL, steamId );
	if ( image <= 0 ) {
		return qfalse;
	}

	width = 0;
	height = 0;
	if ( !getImageSize( utils, NULL, image, &width, &height ) || width == 0 || height == 0 ) {
		return qfalse;
	}

	pixelCount = (size_t)width * (size_t)height;
	if ( pixelCount > ( (size_t)INT_MAX / 4 ) ) {
		return qfalse;
	}

	bufferSize = pixelCount * 4;
	pixels = (uint8_t *)malloc( bufferSize );
	if ( !pixels ) {
		return qfalse;
	}

	if ( !getImageRGBA( utils, NULL, image, pixels, (int)bufferSize ) ) {
		free( pixels );
		return qfalse;
	}

	*outPixels = pixels;
	*outWidth = width;
	*outHeight = height;
	return qtrue;
}

/*
=============
QL_Steamworks_FreeBuffer
=============
*/
void QL_Steamworks_FreeBuffer( void *buffer ) {
	if ( buffer ) {
		free( buffer );
	}
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

	vtable = QL_Steamworks_GetInterfaceVTable( apps );
	if ( !vtable ) {
		return qfalse;
	}

	typedef int (__fastcall *QL_SteamApps_BIsSubscribedAppFn)( void *self, void *unused, uint32_t appId );
	QL_SteamApps_BIsSubscribedAppFn fn = (QL_SteamApps_BIsSubscribedAppFn)vtable[0x1c / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( apps, NULL, appId ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetItemDownloadInfo
=============
*/
qboolean QL_Steamworks_GetItemDownloadInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outDownloaded, uint64_t *outTotal ) {
	void *ugc;
	void **vtable;

	ugc = QL_Steamworks_GetUGCInterface();
	if ( !ugc ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( ugc );
	if ( !vtable ) {
		return qfalse;
	}

	typedef int (__fastcall *QL_SteamUGC_GetItemDownloadInfoFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, uint64_t *outDownloaded, uint64_t *outTotal );
	QL_SteamUGC_GetItemDownloadInfoFn fn = (QL_SteamUGC_GetItemDownloadInfoFn)vtable[0xd8 / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( ugc, NULL, idLow, idHigh, outDownloaded, outTotal ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_RunServerCallbacks

Runs Steam server callbacks if the GameServer interface is available.
=============
*/
void QL_Steamworks_RunServerCallbacks( void ) {
	if ( !state.initialised || !state.gameServerInitialised || !state.SteamGameServer_RunCallbacks ) {
		return;
	}

	state.SteamGameServer_RunCallbacks();
}

/*
=============
QL_Steamworks_ServerInit

Reconstructs the retail Steam game-server init gate and remembers which UGC
owner should back workshop calls for the active server path.
=============
*/
qboolean QL_Steamworks_ServerInit( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated ) {
	int serverMode;

	if ( gamePort == 0 ) {
		return qfalse;
	}

	if ( state.gameServerInitialised ) {
		state.useGameServerUGC = dedicated ? qtrue : qfalse;
		return qtrue;
	}

	if ( !QL_Steamworks_Init() || !state.SteamGameServer_Init ) {
		return qfalse;
	}

	serverMode = secure ? QL_STEAM_GAMESERVER_MODE_AUTH_SECURE : QL_STEAM_GAMESERVER_MODE_NO_AUTH;
	if ( !state.SteamGameServer_Init( ip, 0, gamePort, 0xffffu, serverMode, QL_STEAM_GAMESERVER_VERSION ) ) {
		return qfalse;
	}

	state.gameServerInitialised = qtrue;
	state.useGameServerUGC = dedicated ? qtrue : qfalse;
	return qtrue;
}

/*
=============
QL_Steamworks_ServerShutdown

Reconstructs the retail game-server shutdown gate and clears the active server
UGC owner.
=============
*/
void QL_Steamworks_ServerShutdown( void ) {
	if ( state.gameServerInitialised && state.SteamGameServer_Shutdown ) {
		state.SteamGameServer_Shutdown();
	}

	state.gameServerInitialised = qfalse;
	state.useGameServerUGC = qfalse;
}

/*
=============
QL_Steamworks_ServerIsInitialised
=============
*/
qboolean QL_Steamworks_ServerIsInitialised( void ) {
	return state.gameServerInitialised;
}

/*
=============
QL_Steamworks_GetGameServerNetworking

Returns the Steam GameServer networking interface when available.
=============
*/
static void *QL_Steamworks_GetGameServerNetworking( void ) {
	if ( !state.initialised || !state.gameServerInitialised || !state.SteamGameServerNetworking ) {
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
	if ( !state.initialised || !state.gameServerInitialised || !state.SteamGameServer ) {
		return NULL;
	}

	return state.SteamGameServer();
}

/*
=============
QL_Steamworks_ServerSetDedicated

Mirrors the retail dedicated-state bootstrap write for the Steam game-server.
=============
*/
qboolean QL_Steamworks_ServerSetDedicated( qboolean dedicated ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetDedicatedFn fn;

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetDedicatedFn)vtable[0x10 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, dedicated ? 1 : 0 );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerLogOn

Uses the mapped retail Steam account bootstrap path, including anonymous fallback.
=============
*/
qboolean QL_Steamworks_ServerLogOn( const char *account ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_LogOnFn logOnFn;
	QL_SteamGameServer_LogOnAnonymousFn anonymousFn;

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	if ( account && account[0] ) {
		logOnFn = (QL_SteamGameServer_LogOnFn)vtable[0x14 / 4];
		if ( !logOnFn ) {
			return qfalse;
		}

		logOnFn( gameServer, account );
		return qtrue;
	}

	anonymousFn = (QL_SteamGameServer_LogOnAnonymousFn)vtable[0x18 / 4];
	if ( !anonymousFn ) {
		return qfalse;
	}

	anonymousFn( gameServer );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetProduct

Publishes the retail Steam game-server product string.
=============
*/
qboolean QL_Steamworks_ServerSetProduct( const char *product ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetStringFn fn;

	if ( !product || !product[0] ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetStringFn)vtable[0x04 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, product );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetGameDir

Publishes the retail Steam game-server mod/game-dir string.
=============
*/
qboolean QL_Steamworks_ServerSetGameDir( const char *gameDir ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetStringFn fn;

	if ( !gameDir || !gameDir[0] ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetStringFn)vtable[0x0c / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, gameDir );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetGameDescription

Publishes the retail Steam game-server description string.
=============
*/
qboolean QL_Steamworks_ServerSetGameDescription( const char *description ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetStringFn fn;

	if ( !description || !description[0] ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetStringFn)vtable[0x08 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, description );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetMaxPlayerCount

Publishes the retail Steam game-server max-player count.
=============
*/
qboolean QL_Steamworks_ServerSetMaxPlayerCount( int maxPlayers ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetIntFn fn;

	if ( maxPlayers < 0 ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetIntFn)vtable[0x30 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, maxPlayers );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetBotPlayerCount

Publishes the retail Steam game-server bot-player count.
=============
*/
qboolean QL_Steamworks_ServerSetBotPlayerCount( int botPlayers ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetIntFn fn;

	if ( botPlayers < 0 ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetIntFn)vtable[0x34 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, botPlayers );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetServerName

Publishes the retail Steam game-server name string.
=============
*/
qboolean QL_Steamworks_ServerSetServerName( const char *name ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetStringFn fn;

	if ( !name || !name[0] ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetStringFn)vtable[0x38 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, name );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetMapName

Publishes the retail Steam game-server map string.
=============
*/
qboolean QL_Steamworks_ServerSetMapName( const char *mapName ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetStringFn fn;

	if ( !mapName || !mapName[0] ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetStringFn)vtable[0x3c / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, mapName );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetPasswordProtected

Publishes the retail Steam game-server passworded state.
=============
*/
qboolean QL_Steamworks_ServerSetPasswordProtected( qboolean passwordProtected ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetIntFn fn;

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetIntFn)vtable[0x40 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, passwordProtected ? 1 : 0 );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerEnableHeartbeats

Toggles the Steam game-server heartbeat state through the mapped server slot.
=============
*/
qboolean QL_Steamworks_ServerEnableHeartbeats( qboolean enable ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_EnableHeartbeatsFn fn;

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_EnableHeartbeatsFn)vtable[0x9c / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, enable ? 1 : 0 );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerGetSteamID

Returns the current Steam game-server identity split into low/high words.
=============
*/
qboolean QL_Steamworks_ServerGetSteamID( uint32_t *outIdLow, uint32_t *outIdHigh ) {
	void *gameServer;
	void **vtable;
	CSteamID steamId;
	typedef CSteamID *(__fastcall *QL_SteamGameServer_GetSteamIDFn)( void *self, void *unused, CSteamID *outSteamId );
	QL_SteamGameServer_GetSteamIDFn fn;

	if ( outIdLow ) {
		*outIdLow = 0u;
	}
	if ( outIdHigh ) {
		*outIdHigh = 0u;
	}

	if ( !outIdLow || !outIdHigh ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_GetSteamIDFn)vtable[0x28 / 4];
	if ( !fn ) {
		return qfalse;
	}

	steamId.value = 0ull;
	if ( !fn( gameServer, NULL, &steamId ) ) {
		return qfalse;
	}

	*outIdLow = (uint32_t)( steamId.value & 0xffffffffu );
	*outIdHigh = (uint32_t)( ( steamId.value >> 32 ) & 0xffffffffu );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetGameTags

Publishes the retail Steam game-server game-tags string.
=============
*/
qboolean QL_Steamworks_ServerSetGameTags( const char *tags ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetStringFn fn;

	if ( !tags ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetStringFn)vtable[0x54 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, tags );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetKeyValue

Publishes a single key/value pair through the mapped Steam game-server slot.
=============
*/
qboolean QL_Steamworks_ServerSetKeyValue( const char *key, const char *value ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetKeyValueFn fn;

	if ( !key || !key[0] || !value ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetKeyValueFn)vtable[0x50 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, key, value );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetKeyValuesFromInfoString

Publishes server-info key/value pairs through the mapped Steam game-server slot.
=============
*/
qboolean QL_Steamworks_ServerSetKeyValuesFromInfoString( const char *infoString ) {
	const char *head;
	char key[MAX_INFO_KEY];
	char value[MAX_INFO_VALUE];

	if ( !infoString ) {
		return qfalse;
	}

	head = infoString;
	while ( head && head[0] ) {
		Info_NextPair( &head, key, value );
		if ( !key[0] ) {
			break;
		}

		if ( !QL_Steamworks_ServerSetKeyValue( key, value ) ) {
			return qfalse;
		}
	}

	return qtrue;
}

/*
=============
QL_Steamworks_ServerUpdateUserData

Publishes a player's Steam identity, display name, and score.
=============
*/
qboolean QL_Steamworks_ServerUpdateUserData( const CSteamID *steamId, const char *playerName, uint32_t score ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_UpdateUserDataFn fn;
	uint32_t idLow;
	uint32_t idHigh;

	if ( !steamId || steamId->value == 0ull || !playerName || !playerName[0] ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_UpdateUserDataFn)vtable[0x6c / 4];
	if ( !fn ) {
		return qfalse;
	}

	idLow = (uint32_t)( steamId->value & 0xffffffffu );
	idHigh = (uint32_t)( ( steamId->value >> 32 ) & 0xffffffffu );

	return fn( gameServer, idLow, idHigh, playerName, score ) != 0 ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_ServerGetPublicIP

Returns the Steam-reported public IP for the current game-server instance.
=============
*/
uint32_t QL_Steamworks_ServerGetPublicIP( void ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_GetPublicIPFn fn;

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return 0u;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return 0u;
	}

	fn = (QL_SteamGameServer_GetPublicIPFn)vtable[0x90 / 4];
	if ( !fn ) {
		return 0u;
	}

	return fn( gameServer );
}

/*
=============
QL_Steamworks_SendP2PPacket

Dispatches a client-side P2P packet through the Steam networking interface.
=============
*/
qboolean QL_Steamworks_SendP2PPacket( const CSteamID *steamId, const void *data, uint32_t length, int sendType, int channel ) {
	void *networking;
	void **vtable;
	QL_SteamNetworking_SendP2PPacketFn sendPacket;

	if ( !steamId || !data || length == 0 ) {
		return qfalse;
	}

	networking = QL_Steamworks_GetNetworkingInterface();
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
QL_Steamworks_IsP2PPacketAvailable

Checks for pending client-side Steam P2P packets on the requested channel.
=============
*/
qboolean QL_Steamworks_IsP2PPacketAvailable( uint32_t *outSize, int channel ) {
	void *networking;
	void **vtable;
	QL_SteamNetworking_IsP2PPacketAvailableFn isAvailable;

	if ( !outSize ) {
		return qfalse;
	}

	networking = QL_Steamworks_GetNetworkingInterface();
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
QL_Steamworks_ReadP2PPacket

Reads a pending client-side Steam P2P packet from the requested channel.
=============
*/
qboolean QL_Steamworks_ReadP2PPacket( void *data, uint32_t dataSize, uint32_t *outSize, CSteamID *outSteamId, int channel ) {
	void *networking;
	void **vtable;
	QL_SteamNetworking_ReadP2PPacketFn readPacket;

	if ( !data || dataSize == 0 || !outSize || !outSteamId ) {
		return qfalse;
	}

	networking = QL_Steamworks_GetNetworkingInterface();
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
QL_Steamworks_AcceptP2PSession

Accepts an incoming client-side Steam P2P session.
=============
*/
qboolean QL_Steamworks_AcceptP2PSession( const CSteamID *steamId ) {
	void *networking;
	void **vtable;
	typedef qboolean (*QL_SteamNetworking_AcceptP2PSessionWithUserFn)( void *self, CSteamID steamId );
	QL_SteamNetworking_AcceptP2PSessionWithUserFn acceptSession;

	if ( !steamId ) {
		return qfalse;
	}

	networking = QL_Steamworks_GetNetworkingInterface();
	if ( !networking ) {
		return qfalse;
	}

	vtable = *(void ***)networking;
	if ( !vtable ) {
		return qfalse;
	}

	acceptSession = (QL_SteamNetworking_AcceptP2PSessionWithUserFn)vtable[0x0c / 4];
	if ( !acceptSession ) {
		return qfalse;
	}

	return acceptSession( networking, *steamId ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_StartVoiceRecording

Starts voice capture on the active Steam user interface.
=============
*/
qboolean QL_Steamworks_StartVoiceRecording( void ) {
	void *user;
	void **vtable;
	typedef void (__fastcall *QL_SteamUser_StartVoiceRecordingFn)( void *self, void *unused );
	QL_SteamUser_StartVoiceRecordingFn fn;

	user = QL_Steamworks_GetUserInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( user );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUser_StartVoiceRecordingFn)vtable[0x1c / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( user, NULL );
	return qtrue;
}

/*
=============
QL_Steamworks_StopVoiceRecording

Stops voice capture on the active Steam user interface.
=============
*/
qboolean QL_Steamworks_StopVoiceRecording( void ) {
	void *user;
	void **vtable;
	typedef void (__fastcall *QL_SteamUser_StopVoiceRecordingFn)( void *self, void *unused );
	QL_SteamUser_StopVoiceRecordingFn fn;

	user = QL_Steamworks_GetUserInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( user );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUser_StopVoiceRecordingFn)vtable[0x20 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( user, NULL );
	return qtrue;
}

/*
=============
QL_Steamworks_GetCompressedVoice

Pulls compressed voice capture bytes from the active Steam user interface.
=============
*/
qboolean QL_Steamworks_GetCompressedVoice( void *data, uint32_t dataSize, uint32_t *outSize ) {
	void *user;
	void **vtable;
	int result;
	typedef int (__fastcall *QL_SteamUser_GetVoiceFn)( void *self, void *unused, qboolean wantCompressed, void *destBuffer, uint32_t destBufferSize, uint32_t *outCompressedBytes, qboolean wantUncompressed, void *uncompressedBuffer, uint32_t uncompressedBufferSize, uint32_t *outUncompressedBytes, uint32_t uncompressedSampleRate );
	QL_SteamUser_GetVoiceFn fn;

	if ( outSize ) {
		*outSize = 0u;
	}

	if ( !data || dataSize == 0 || !outSize ) {
		return qfalse;
	}

	user = QL_Steamworks_GetUserInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( user );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUser_GetVoiceFn)vtable[0x28 / 4];
	if ( !fn ) {
		return qfalse;
	}

	result = fn( user, NULL, qtrue, data, dataSize, outSize, qfalse, NULL, 0u, NULL, 0u );
	return result == 0 ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_DecompressVoice

Decompresses a Steam voice payload into 16-bit PCM at the requested rate.
=============
*/
qboolean QL_Steamworks_DecompressVoice( const void *compressedData, uint32_t compressedSize, void *data, uint32_t dataSize, uint32_t *outSize, uint32_t sampleRate ) {
	void *user;
	void **vtable;
	int result;
	typedef int (__fastcall *QL_SteamUser_DecompressVoiceFn)( void *self, void *unused, const void *compressedData, uint32_t compressedSize, void *destBuffer, uint32_t destBufferSize, uint32_t *outBytesWritten, uint32_t sampleRate );
	QL_SteamUser_DecompressVoiceFn fn;

	if ( outSize ) {
		*outSize = 0u;
	}

	if ( !compressedData || compressedSize == 0 || !data || dataSize == 0 || !outSize ) {
		return qfalse;
	}

	user = QL_Steamworks_GetUserInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( user );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUser_DecompressVoiceFn)vtable[0x2c / 4];
	if ( !fn ) {
		return qfalse;
	}

	result = fn( user, NULL, compressedData, compressedSize, data, dataSize, outSize, sampleRate );
	return result == 0 ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetVoiceOptimalSampleRate

Returns the Steam-reported preferred voice sample rate for the active user.
=============
*/
uint32_t QL_Steamworks_GetVoiceOptimalSampleRate( void ) {
	void *user;
	void **vtable;
	typedef uint32_t (__fastcall *QL_SteamUser_GetVoiceOptimalSampleRateFn)( void *self, void *unused );
	QL_SteamUser_GetVoiceOptimalSampleRateFn fn;

	user = QL_Steamworks_GetUserInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( user );
	if ( !vtable ) {
		return 0u;
	}

	fn = (QL_SteamUser_GetVoiceOptimalSampleRateFn)vtable[0x30 / 4];
	if ( !fn ) {
		return 0u;
	}

	return fn( user, NULL );
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

	getPacket = (QL_SteamGameServer_GetNextOutgoingPacketFn)vtable[0x98 / 4];
	if ( !getPacket ) {
		return 0;
	}

	return getPacket( gameServer, data, dataSize, outIp, outPort );
}

/*
=============
QL_Steamworks_ServerAcceptP2PSession

Accepts an incoming Steam P2P session for the active game server.
=============
*/
qboolean QL_Steamworks_ServerAcceptP2PSession( const CSteamID *steamId ) {
	void *networking;
	void **vtable;
	typedef qboolean (*QL_SteamNetworking_AcceptP2PSessionWithUserFn)( void *self, CSteamID steamId );
	QL_SteamNetworking_AcceptP2PSessionWithUserFn acceptSession;

	if ( !steamId ) {
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

	acceptSession = (QL_SteamNetworking_AcceptP2PSessionWithUserFn)vtable[0x0c / 4];
	if ( !acceptSession ) {
		return qfalse;
	}

	return acceptSession( networking, *steamId ) ? qtrue : qfalse;
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
QL_Steamworks_CancelAuthTicket

Cancels a previously issued auth session ticket.
=============
*/
qboolean QL_Steamworks_CancelAuthTicket( uint32_t ticketHandle ) {
	void *user;

	if ( ticketHandle == 0 || !state.initialised || !state.SteamUser || !state.CancelAuthTicket ) {
		return qfalse;
	}

	user = state.SteamUser();
	if ( !user ) {
		return qfalse;
	}

	state.CancelAuthTicket( user, (HAuthTicket)ticketHandle );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerBeginAuthSession

Begins a Steam GameServer auth session for one connecting client ticket.
=============
*/
qboolean QL_Steamworks_ServerBeginAuthSession( const CSteamID *steamId, const char *ticketHex, ql_auth_response_t *response ) {
	void *gameServer;
	uint8_t ticketData[2048];
	uint32_t ticketLength;
	EBeginAuthSessionResult result;

	if ( response ) {
		memset( response, 0, sizeof( *response ) );
	}

	if ( !steamId || !ticketHex || !ticketHex[0] ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer || !state.BeginAuthSession ) {
		return qfalse;
	}

	ticketLength = 0;
	if ( !QL_Steamworks_HexDecode( ticketHex, ticketData, sizeof( ticketData ), &ticketLength ) || ticketLength == 0 ) {
		if ( response ) {
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED, "Steam ticket invalid" );
		}
		return qfalse;
	}

	result = state.BeginAuthSession( gameServer, ticketData, (int)ticketLength, *steamId );
	if ( response ) {
		QL_Steamworks_MapAuthResult( result, response );
	}

	return result == k_EBeginAuthSessionResultOK ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_ServerEndAuthSession

Ends one Steam GameServer auth session if the server interface is active.
=============
*/
void QL_Steamworks_ServerEndAuthSession( const CSteamID *steamId ) {
	void *gameServer;

	if ( !steamId ) {
		return;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer || !state.EndAuthSession ) {
		return;
	}

	state.EndAuthSession( gameServer, *steamId );
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
