#include "platform_steamworks.h"
#include "platform_services.h"

#if QL_BUILD_STEAMWORKS

#include <limits.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

void QDECL Com_DPrintf( const char *fmt, ... );
void QDECL Com_Printf( const char *fmt, ... );

#ifdef _WIN32
#include <windows.h>
#if defined( _M_IX86 ) || defined( __i386__ )
#define QL_STEAMWORKS_LIB_PRIMARY "steam_api.dll"
#define QL_STEAMWORKS_LIB_SECONDARY "steam_api64.dll"
#else
#define QL_STEAMWORKS_LIB_PRIMARY "steam_api64.dll"
#define QL_STEAMWORKS_LIB_SECONDARY "steam_api.dll"
#endif
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

#define QL_STEAMWORKS_EXPORT_STEAM_API_INIT "SteamAPI_Init"
#define QL_STEAMWORKS_EXPORT_STEAM_API_SHUTDOWN "SteamAPI_Shutdown"
#define QL_STEAMWORKS_EXPORT_STEAM_API_RUN_CALLBACKS "SteamAPI_RunCallbacks"
#define QL_STEAMWORKS_EXPORT_STEAM_API_REGISTER_CALLBACK "SteamAPI_RegisterCallback"
#define QL_STEAMWORKS_EXPORT_STEAM_API_UNREGISTER_CALLBACK "SteamAPI_UnregisterCallback"
#define QL_STEAMWORKS_EXPORT_STEAM_API_REGISTER_CALL_RESULT "SteamAPI_RegisterCallResult"
#define QL_STEAMWORKS_EXPORT_STEAM_API_UNREGISTER_CALL_RESULT "SteamAPI_UnregisterCallResult"
#define QL_STEAMWORKS_EXPORT_STEAM_USER "SteamUser"
#define QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_USER "SteamAPI_SteamUser"
#define QL_STEAMWORKS_EXPORT_STEAM_FRIENDS "SteamFriends"
#define QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_FRIENDS "SteamAPI_SteamFriends"
#define QL_STEAMWORKS_EXPORT_STEAM_NETWORKING "SteamNetworking"
#define QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_NETWORKING "SteamAPI_SteamNetworking"
#define QL_STEAMWORKS_EXPORT_STEAM_UTILS "SteamUtils"
#define QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_UTILS "SteamAPI_SteamUtils"
#define QL_STEAMWORKS_EXPORT_STEAM_USER_STATS "SteamUserStats"
#define QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_USER_STATS "SteamAPI_SteamUserStats"
#define QL_STEAMWORKS_EXPORT_STEAM_MATCHMAKING "SteamMatchmaking"
#define QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_MATCHMAKING "SteamAPI_SteamMatchmaking"
#define QL_STEAMWORKS_EXPORT_STEAM_MATCHMAKING_SERVERS "SteamMatchmakingServers"
#define QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_MATCHMAKING_SERVERS "SteamAPI_SteamMatchmakingServers"
#define QL_STEAMWORKS_EXPORT_STEAM_APPS "SteamApps"
#define QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_APPS "SteamAPI_SteamApps"
#define QL_STEAMWORKS_EXPORT_STEAM_UGC "SteamUGC"
#define QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_UGC "SteamAPI_SteamUGC"
#define QL_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_GET_AUTH_SESSION_TICKET "SteamAPI_ISteamUser_GetAuthSessionTicket"
#define QL_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_GET_AUTH_TICKET_FOR_WEB_API "SteamAPI_ISteamUser_GetAuthTicketForWebApi"
#define QL_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_BEGIN_AUTH_SESSION "SteamAPI_ISteamUser_BeginAuthSession"
#define QL_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_CANCEL_AUTH_TICKET "SteamAPI_ISteamUser_CancelAuthTicket"
#define QL_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_END_AUTH_SESSION "SteamAPI_ISteamUser_EndAuthSession"
#define QL_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_GET_STEAM_ID "SteamAPI_ISteamUser_GetSteamID"
#define QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER "SteamGameServer"
#define QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_STATS "SteamGameServerStats"
#define QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_UTILS "SteamGameServerUtils"
#define QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_UGC "SteamGameServerUGC"
#define QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_INIT "SteamGameServer_Init"
#define QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_SHUTDOWN "SteamGameServer_Shutdown"
#define QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_RUN_CALLBACKS "SteamGameServer_RunCallbacks"
#define QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_NETWORKING "SteamGameServerNetworking"

#if defined(_MSC_VER)
#define QL_STEAMWORKS_FASTCALL __fastcall
#elif defined(__GNUC__) && defined(__i386__)
#define QL_STEAMWORKS_FASTCALL __attribute__((fastcall))
#else
#define QL_STEAMWORKS_FASTCALL
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
typedef HAuthTicket (*QL_SteamAPI_GetAuthTicketForWebApiFn)( void *, const char * );
typedef EBeginAuthSessionResult (*QL_SteamAPI_BeginAuthSessionFn)( void *, const void *, int, CSteamID );
typedef void (*QL_SteamAPI_CancelAuthTicketFn)( void *, HAuthTicket );
typedef void (*QL_SteamAPI_EndAuthSessionFn)( void *, CSteamID );
typedef CSteamID (*QL_SteamAPI_GetSteamIDFn)( void * );
typedef qboolean (QL_STEAMWORKS_FASTCALL *QL_SteamNetworking_SendP2PPacketFn)( void *, void *, CSteamID, const void *, uint32_t, int, int );
typedef qboolean (QL_STEAMWORKS_FASTCALL *QL_SteamNetworking_IsP2PPacketAvailableFn)( void *, void *, uint32_t *, int );
typedef qboolean (QL_STEAMWORKS_FASTCALL *QL_SteamNetworking_ReadP2PPacketFn)( void *, void *, void *, uint32_t, uint32_t *, CSteamID *, int );
typedef uint32_t (QL_STEAMWORKS_FASTCALL *QL_SteamGameServer_GetPublicIPFn)( void *, void * );
typedef qboolean (QL_STEAMWORKS_FASTCALL *QL_SteamGameServer_BLoggedOnFn)( void *, void * );
typedef EBeginAuthSessionResult (QL_STEAMWORKS_FASTCALL *QL_SteamGameServer_BeginAuthSessionFn)( void *, void *, const void *, int, CSteamID );
typedef void (QL_STEAMWORKS_FASTCALL *QL_SteamGameServer_EndAuthSessionFn)( void *, void *, CSteamID );
typedef qboolean (QL_STEAMWORKS_FASTCALL *QL_SteamGameServer_HandleIncomingPacketFn)( void *, void *, const void *, int, uint32_t, uint16_t );
typedef int (QL_STEAMWORKS_FASTCALL *QL_SteamGameServer_GetNextOutgoingPacketFn)( void *, void *, void *, int, uint32_t *, uint16_t * );
typedef void (QL_STEAMWORKS_FASTCALL *QL_SteamGameServer_EnableHeartbeatsFn)( void *, void *, int );
typedef CSteamID *(QL_STEAMWORKS_FASTCALL *QL_SteamGameServer_CreateUnauthenticatedUserConnectionFn)( void *, void *, CSteamID * );
typedef void (QL_STEAMWORKS_FASTCALL *QL_SteamGameServer_SetDedicatedFn)( void *, void *, int );
typedef void (QL_STEAMWORKS_FASTCALL *QL_SteamGameServer_LogOnFn)( void *, void *, const char * );
typedef void (QL_STEAMWORKS_FASTCALL *QL_SteamGameServer_LogOnAnonymousFn)( void *, void * );
typedef void (QL_STEAMWORKS_FASTCALL *QL_SteamGameServer_SetStringFn)( void *, void *, const char * );
typedef void (QL_STEAMWORKS_FASTCALL *QL_SteamGameServer_SetIntFn)( void *, void *, int );
typedef void (QL_STEAMWORKS_FASTCALL *QL_SteamGameServer_SetKeyValueFn)( void *, void *, const char *, const char * );
typedef int (QL_STEAMWORKS_FASTCALL *QL_SteamGameServer_UpdateUserDataFn)( void *, void *, uint32_t, uint32_t, const char *, uint32_t );

#if defined(_MSC_VER) && defined(_M_IX86) && !defined(__cplusplus)
#define QL_STEAMWORKS_USE_MSVC_C_THISCALL_THUNKS 1
#define QL_STEAMWORKS_THISCALL
#elif defined(_MSC_VER) && defined(_M_IX86)
#define QL_STEAMWORKS_USE_MSVC_C_THISCALL_THUNKS 0
#define QL_STEAMWORKS_THISCALL __thiscall
#elif defined(__GNUC__) && defined(__i386__)
#define QL_STEAMWORKS_USE_MSVC_C_THISCALL_THUNKS 0
#define QL_STEAMWORKS_THISCALL __attribute__((thiscall))
#else
#define QL_STEAMWORKS_USE_MSVC_C_THISCALL_THUNKS 0
#define QL_STEAMWORKS_THISCALL
#endif

#define QL_STEAM_FAVORITE_FLAG_FAVORITE 0x01u

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
	uint32_t steamIDFriendLow;
	uint32_t steamIDFriendHigh;
	uint32_t appId;
} ql_steam_friend_rich_presence_update_raw_t;

typedef struct {
	uint32_t steamIDLow;
	uint32_t steamIDHigh;
	int image;
	int wide;
	int tall;
} ql_steam_avatar_image_loaded_raw_t;

typedef struct {
	uint64_t queryHandle;
	int result;
	uint32_t numResultsReturned;
	uint32_t totalMatchingResults;
	qboolean cachedData;
} ql_steam_ugc_query_completed_raw_t;

typedef struct {
	HAuthTicket authTicket;
	int result;
	uint32_t ticketLength;
	uint8_t ticket[QL_STEAM_WEB_API_AUTH_TICKET_MAX_LENGTH];
} ql_steam_get_ticket_for_web_api_response_raw_t;

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
	uint32_t resultPadding;
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
} ql_steam_server_connect_failure_raw_t;

typedef struct {
	int result;
} ql_steam_servers_disconnected_raw_t;

typedef struct {
	int result;
	uint32_t steamIdLow;
	uint32_t steamIdHigh;
} ql_steam_gs_stats_received_raw_t;

typedef struct {
	int result;
	uint32_t steamIdLow;
	uint32_t steamIdHigh;
} ql_steam_gs_stats_stored_raw_t;

typedef struct {
	uint32_t steamIdLow;
	uint32_t steamIdHigh;
	int authSessionResponse;
	uint32_t ownerSteamIdLow;
	uint32_t ownerSteamIdHigh;
} ql_steam_validate_auth_ticket_response_raw_t;

#define QL_STEAM_CALLBACK_SIZE_GAME_RICH_PRESENCE_JOIN_REQUESTED 0x108
#define QL_STEAM_CALLBACK_SIZE_USER_STATS_RECEIVED 0x18
#define QL_STEAM_CALLBACK_SIZE_PERSONA_STATE_CHANGE 0x10
#define QL_STEAM_CALLBACK_SIZE_P2P_SESSION_REQUEST 0x08
#define QL_STEAM_CALLBACK_SIZE_GAME_SERVER_CHANGE_REQUESTED 0x80
#define QL_STEAM_CALLBACK_SIZE_FRIEND_RICH_PRESENCE_UPDATE 0x0c
#define QL_STEAM_CALLBACK_SIZE_AVATAR_IMAGE_LOADED 0x14
#define QL_STEAM_CALLBACK_SIZE_UGC_QUERY_COMPLETED 0x18
#define QL_STEAM_CALLBACK_SIZE_GET_TICKET_FOR_WEB_API_RESPONSE 0xa0c
#define QL_STEAM_CALLBACK_SIZE_ITEM_INSTALLED 0x10
#define QL_STEAM_CALLBACK_SIZE_DOWNLOAD_ITEM_RESULT 0x18
#define QL_STEAM_CALLBACK_SIZE_LOBBY_CREATED 0x10
#define QL_STEAM_CALLBACK_SIZE_LOBBY_ENTER 0x18
#define QL_STEAM_CALLBACK_SIZE_LOBBY_CHAT_UPDATE 0x20
#define QL_STEAM_CALLBACK_SIZE_LOBBY_CHAT_MESSAGE 0x18
#define QL_STEAM_CALLBACK_SIZE_LOBBY_DATA_UPDATE 0x18
#define QL_STEAM_CALLBACK_SIZE_LOBBY_GAME_CREATED 0x18
#define QL_STEAM_CALLBACK_SIZE_LOBBY_KICKED 0x18
#define QL_STEAM_CALLBACK_SIZE_GAME_LOBBY_JOIN_REQUESTED 0x10
#define QL_STEAM_CALLBACK_SIZE_MICROTXN_AUTHORIZATION_RESPONSE 0x18
#define QL_STEAM_CALLBACK_SIZE_SERVERS_CONNECTED 0x01
#define QL_STEAM_CALLBACK_SIZE_SERVER_CONNECT_FAILURE 0x04
#define QL_STEAM_CALLBACK_SIZE_SERVERS_DISCONNECTED 0x04
#define QL_STEAM_CALLBACK_SIZE_VALIDATE_AUTH_TICKET_RESPONSE 0x14
#define QL_STEAM_CALLBACK_SIZE_GS_STATS_RECEIVED 0x0c
#define QL_STEAM_CALLBACK_SIZE_GS_STATS_STORED 0x0c

#define QL_STEAMWORKS_STATIC_ASSERT_SIZE( name, type, size ) typedef char name[( sizeof( type ) == ( size ) ) ? 1 : -1]

QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_game_rich_presence_join_requested_raw, ql_steam_game_rich_presence_join_requested_raw_t, QL_STEAM_CALLBACK_SIZE_GAME_RICH_PRESENCE_JOIN_REQUESTED );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_user_stats_received_raw, ql_steam_user_stats_received_raw_t, QL_STEAM_CALLBACK_SIZE_USER_STATS_RECEIVED );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_persona_state_change_raw, ql_steam_persona_state_change_raw_t, QL_STEAM_CALLBACK_SIZE_PERSONA_STATE_CHANGE );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_p2p_session_request_raw, ql_steam_p2p_session_request_raw_t, QL_STEAM_CALLBACK_SIZE_P2P_SESSION_REQUEST );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_game_server_change_requested_raw, ql_steam_game_server_change_requested_raw_t, QL_STEAM_CALLBACK_SIZE_GAME_SERVER_CHANGE_REQUESTED );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_friend_rich_presence_update_raw, ql_steam_friend_rich_presence_update_raw_t, QL_STEAM_CALLBACK_SIZE_FRIEND_RICH_PRESENCE_UPDATE );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_avatar_image_loaded_raw, ql_steam_avatar_image_loaded_raw_t, QL_STEAM_CALLBACK_SIZE_AVATAR_IMAGE_LOADED );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_ugc_query_completed_raw, ql_steam_ugc_query_completed_raw_t, QL_STEAM_CALLBACK_SIZE_UGC_QUERY_COMPLETED );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_get_ticket_for_web_api_response_raw, ql_steam_get_ticket_for_web_api_response_raw_t, QL_STEAM_CALLBACK_SIZE_GET_TICKET_FOR_WEB_API_RESPONSE );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_item_installed_raw, ql_steam_item_installed_raw_t, QL_STEAM_CALLBACK_SIZE_ITEM_INSTALLED );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_download_item_result_raw, ql_steam_download_item_result_raw_t, QL_STEAM_CALLBACK_SIZE_DOWNLOAD_ITEM_RESULT );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_lobby_created_raw, ql_steam_lobby_created_raw_t, QL_STEAM_CALLBACK_SIZE_LOBBY_CREATED );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_lobby_enter_raw, ql_steam_lobby_enter_raw_t, QL_STEAM_CALLBACK_SIZE_LOBBY_ENTER );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_lobby_chat_update_raw, ql_steam_lobby_chat_update_raw_t, QL_STEAM_CALLBACK_SIZE_LOBBY_CHAT_UPDATE );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_lobby_chat_message_raw, ql_steam_lobby_chat_message_raw_t, QL_STEAM_CALLBACK_SIZE_LOBBY_CHAT_MESSAGE );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_lobby_data_update_raw, ql_steam_lobby_data_update_raw_t, QL_STEAM_CALLBACK_SIZE_LOBBY_DATA_UPDATE );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_lobby_game_created_raw, ql_steam_lobby_game_created_raw_t, QL_STEAM_CALLBACK_SIZE_LOBBY_GAME_CREATED );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_lobby_kicked_raw, ql_steam_lobby_kicked_raw_t, QL_STEAM_CALLBACK_SIZE_LOBBY_KICKED );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_game_lobby_join_requested_raw, ql_steam_game_lobby_join_requested_raw_t, QL_STEAM_CALLBACK_SIZE_GAME_LOBBY_JOIN_REQUESTED );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_microtxn_authorization_response_raw, ql_steam_microtxn_authorization_response_raw_t, QL_STEAM_CALLBACK_SIZE_MICROTXN_AUTHORIZATION_RESPONSE );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_servers_connected_raw, ql_steam_servers_connected_raw_t, QL_STEAM_CALLBACK_SIZE_SERVERS_CONNECTED );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_server_connect_failure_raw, ql_steam_server_connect_failure_raw_t, QL_STEAM_CALLBACK_SIZE_SERVER_CONNECT_FAILURE );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_servers_disconnected_raw, ql_steam_servers_disconnected_raw_t, QL_STEAM_CALLBACK_SIZE_SERVERS_DISCONNECTED );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_validate_auth_ticket_response_raw, ql_steam_validate_auth_ticket_response_raw_t, QL_STEAM_CALLBACK_SIZE_VALIDATE_AUTH_TICKET_RESPONSE );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_gs_stats_received_raw, ql_steam_gs_stats_received_raw_t, QL_STEAM_CALLBACK_SIZE_GS_STATS_RECEIVED );
QL_STEAMWORKS_STATIC_ASSERT_SIZE( ql_steam_size_gs_stats_stored_raw, ql_steam_gs_stats_stored_raw_t, QL_STEAM_CALLBACK_SIZE_GS_STATS_STORED );

#undef QL_STEAMWORKS_STATIC_ASSERT_SIZE

typedef struct {
	uint64_t gameId;
	uint32_t gameIp;
	uint16_t gamePort;
	uint16_t queryPort;
	CSteamID lobbyId;
	CSteamID gameServerId;
} ql_steam_friend_game_info_t;

typedef struct {
	char key[256];
	char value[256];
} ql_steam_matchmaking_key_value_pair_t;

#define QL_STEAM_GAMESERVERITEM_CONNECTION_PORT_OFFSET 0x00
#define QL_STEAM_GAMESERVERITEM_QUERY_PORT_OFFSET 0x02
#define QL_STEAM_GAMESERVERITEM_IP_OFFSET 0x04
#define QL_STEAM_GAMESERVERITEM_PING_OFFSET 0x08
#define QL_STEAM_GAMESERVERITEM_HAD_SUCCESSFUL_RESPONSE_OFFSET 0x0c
#define QL_STEAM_GAMESERVERITEM_DO_NOT_REFRESH_OFFSET 0x0d
#define QL_STEAM_GAMESERVERITEM_GAME_DIR_OFFSET 0x0e
#define QL_STEAM_GAMESERVERITEM_MAP_OFFSET 0x2e
#define QL_STEAM_GAMESERVERITEM_GAME_DESCRIPTION_OFFSET 0x4e
#define QL_STEAM_GAMESERVERITEM_APP_ID_OFFSET 0x90
#define QL_STEAM_GAMESERVERITEM_PLAYERS_OFFSET 0x94
#define QL_STEAM_GAMESERVERITEM_MAX_PLAYERS_OFFSET 0x98
#define QL_STEAM_GAMESERVERITEM_BOT_PLAYERS_OFFSET 0x9c
#define QL_STEAM_GAMESERVERITEM_PASSWORD_OFFSET 0xa0
#define QL_STEAM_GAMESERVERITEM_SECURE_OFFSET 0xa1
#define QL_STEAM_GAMESERVERITEM_LAST_PLAYED_OFFSET 0xa4
#define QL_STEAM_GAMESERVERITEM_SERVER_VERSION_OFFSET 0xa8
#define QL_STEAM_GAMESERVERITEM_SERVER_NAME_OFFSET 0xac
#define QL_STEAM_GAMESERVERITEM_GAME_TAGS_OFFSET 0xec
#define QL_STEAM_GAMESERVERITEM_STEAM_ID_LOW_OFFSET 0x16c
#define QL_STEAM_GAMESERVERITEM_STEAM_ID_HIGH_OFFSET 0x170
#define QL_STEAM_GAMESERVERITEM_SIZE 0x174

typedef struct {
	uint16_t connectionPort;
	uint16_t queryPort;
	uint32_t ip;
	int32_t ping;
	uint8_t hadSuccessfulResponse;
	uint8_t doNotRefresh;
	char gameDir[QL_STEAM_SERVER_BROWSER_GAME_DIR_LENGTH];
	char map[QL_STEAM_SERVER_BROWSER_MAP_LENGTH];
	char gameDescription[QL_STEAM_SERVER_BROWSER_GAME_DESCRIPTION_LENGTH];
	uint8_t appIdPadding[2];
	uint32_t appId;
	int32_t players;
	int32_t maxPlayers;
	int32_t botPlayers;
	uint8_t password;
	uint8_t secure;
	uint8_t lastPlayedPadding[2];
	uint32_t lastPlayed;
	int32_t serverVersion;
	char serverName[QL_STEAM_SERVER_BROWSER_NAME_LENGTH];
	char gameTags[QL_STEAM_SERVER_BROWSER_TAGS_LENGTH];
	uint32_t steamIdLow;
	uint32_t steamIdHigh;
} ql_steam_gameserveritem_raw_t;

#define QL_STEAMWORKS_STATIC_ASSERT_OFFSET( name, type, field, offset ) typedef char name[( offsetof( type, field ) == ( offset ) ) ? 1 : -1]
#define QL_STEAMWORKS_STATIC_ASSERT_RAW_SIZE( name, type, size ) typedef char name[( sizeof( type ) == ( size ) ) ? 1 : -1]

QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_connection_port_offset, ql_steam_gameserveritem_raw_t, connectionPort, QL_STEAM_GAMESERVERITEM_CONNECTION_PORT_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_query_port_offset, ql_steam_gameserveritem_raw_t, queryPort, QL_STEAM_GAMESERVERITEM_QUERY_PORT_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_ip_offset, ql_steam_gameserveritem_raw_t, ip, QL_STEAM_GAMESERVERITEM_IP_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_ping_offset, ql_steam_gameserveritem_raw_t, ping, QL_STEAM_GAMESERVERITEM_PING_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_had_successful_response_offset, ql_steam_gameserveritem_raw_t, hadSuccessfulResponse, QL_STEAM_GAMESERVERITEM_HAD_SUCCESSFUL_RESPONSE_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_do_not_refresh_offset, ql_steam_gameserveritem_raw_t, doNotRefresh, QL_STEAM_GAMESERVERITEM_DO_NOT_REFRESH_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_game_dir_offset, ql_steam_gameserveritem_raw_t, gameDir, QL_STEAM_GAMESERVERITEM_GAME_DIR_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_map_offset, ql_steam_gameserveritem_raw_t, map, QL_STEAM_GAMESERVERITEM_MAP_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_game_description_offset, ql_steam_gameserveritem_raw_t, gameDescription, QL_STEAM_GAMESERVERITEM_GAME_DESCRIPTION_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_app_id_offset, ql_steam_gameserveritem_raw_t, appId, QL_STEAM_GAMESERVERITEM_APP_ID_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_players_offset, ql_steam_gameserveritem_raw_t, players, QL_STEAM_GAMESERVERITEM_PLAYERS_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_max_players_offset, ql_steam_gameserveritem_raw_t, maxPlayers, QL_STEAM_GAMESERVERITEM_MAX_PLAYERS_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_bot_players_offset, ql_steam_gameserveritem_raw_t, botPlayers, QL_STEAM_GAMESERVERITEM_BOT_PLAYERS_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_password_offset, ql_steam_gameserveritem_raw_t, password, QL_STEAM_GAMESERVERITEM_PASSWORD_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_secure_offset, ql_steam_gameserveritem_raw_t, secure, QL_STEAM_GAMESERVERITEM_SECURE_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_last_played_offset, ql_steam_gameserveritem_raw_t, lastPlayed, QL_STEAM_GAMESERVERITEM_LAST_PLAYED_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_server_version_offset, ql_steam_gameserveritem_raw_t, serverVersion, QL_STEAM_GAMESERVERITEM_SERVER_VERSION_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_server_name_offset, ql_steam_gameserveritem_raw_t, serverName, QL_STEAM_GAMESERVERITEM_SERVER_NAME_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_game_tags_offset, ql_steam_gameserveritem_raw_t, gameTags, QL_STEAM_GAMESERVERITEM_GAME_TAGS_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_steam_id_low_offset, ql_steam_gameserveritem_raw_t, steamIdLow, QL_STEAM_GAMESERVERITEM_STEAM_ID_LOW_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_OFFSET( ql_steam_gameserveritem_steam_id_high_offset, ql_steam_gameserveritem_raw_t, steamIdHigh, QL_STEAM_GAMESERVERITEM_STEAM_ID_HIGH_OFFSET );
QL_STEAMWORKS_STATIC_ASSERT_RAW_SIZE( ql_steam_gameserveritem_size, ql_steam_gameserveritem_raw_t, QL_STEAM_GAMESERVERITEM_SIZE );

#undef QL_STEAMWORKS_STATIC_ASSERT_OFFSET
#undef QL_STEAMWORKS_STATIC_ASSERT_RAW_SIZE

typedef struct ql_steam_callback_base_s ql_steam_callback_base_t;

typedef void (QL_STEAMWORKS_THISCALL *ql_steam_callback_run_fn)( ql_steam_callback_base_t *self, void *payload );
typedef void (QL_STEAMWORKS_THISCALL *ql_steam_callback_run_call_result_fn)( ql_steam_callback_base_t *self, void *payload, qboolean ioFailure, SteamAPICall_t callHandle );
typedef int (QL_STEAMWORKS_THISCALL *ql_steam_callback_get_size_fn)( ql_steam_callback_base_t *self );
typedef void (QL_STEAMWORKS_THISCALL *ql_steam_callback_member_fn)( ql_steam_callback_base_t *self, void *payload );
typedef void (QL_STEAMWORKS_THISCALL *ql_steam_call_result_member_fn)( ql_steam_callback_base_t *self, void *payload, qboolean ioFailure );
typedef void (*ql_steam_callback_vfunc_t)( void );

typedef struct {
	ql_steam_callback_vfunc_t run;
	ql_steam_callback_vfunc_t runAdapter;
	ql_steam_callback_vfunc_t getSize;
} ql_steam_callback_vtable_t;

struct ql_steam_callback_base_s {
	const ql_steam_callback_vtable_t *vtable;
	uint8_t callbackFlags;
	uint8_t reserved[3];
	int callbackId;
	ql_steam_callback_base_t *owner;
	union {
		ql_steam_callback_member_fn memberFunction;
		uint32_t callResultHandleLow;
	};
	uint32_t callResultHandleHigh;
	ql_steam_callback_base_t *callResultOwner;
	ql_steam_call_result_member_fn callResultMemberFunction;
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
	qboolean webApiTicketActive;
	qboolean webApiTicketCompleted;
	HAuthTicket webApiTicketHandle;
	int webApiTicketResult;
	uint32_t webApiTicketLength;
	uint8_t webApiTicket[QL_STEAM_WEB_API_AUTH_TICKET_MAX_LENGTH];
	ql_steam_callback_base_t webApiTicketResponse;
	ql_steam_callback_base_t richPresenceJoinRequested;
	ql_steam_callback_base_t userStatsReceived;
	ql_steam_callback_base_t personaStateChange;
	ql_steam_callback_base_t p2pSessionRequest;
	ql_steam_callback_base_t gameServerChangeRequested;
	ql_steam_callback_base_t friendRichPresenceUpdate;
	ql_steam_callback_base_t ugcQueryCompleted;
} ql_steam_client_callback_state_t;

typedef struct {
	ql_steam_avatar_callback_bindings_t bindings;
	qboolean registered;
	ql_steam_callback_base_t avatarImageLoaded;
} ql_steam_avatar_callback_state_t;

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
	ql_steam_callback_base_t gsStatsReceived;
	ql_steam_callback_base_t gsStatsStored;
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
	QL_SteamAPI_InterfaceFn SteamMatchmakingServers;
	QL_SteamAPI_InterfaceFn SteamApps;
	QL_SteamAPI_InterfaceFn SteamUGC;
	QL_SteamAPI_InterfaceFn SteamGameServerUGC;
	QL_SteamAPI_SteamGameServerInitFn SteamGameServer_Init;
	QL_SteamAPI_SteamGameServerFn SteamGameServer;
	QL_SteamAPI_InterfaceFn SteamGameServerStats;
	QL_SteamAPI_InterfaceFn SteamGameServerUtils;
	QL_SteamAPI_SteamGameServerShutdownFn SteamGameServer_Shutdown;
	QL_SteamAPI_SteamGameServerRunCallbacksFn SteamGameServer_RunCallbacks;
	QL_SteamAPI_SteamGameServerNetworkingFn SteamGameServerNetworking;
	QL_SteamAPI_GetAuthSessionTicketFn GetAuthSessionTicket;
	QL_SteamAPI_GetAuthTicketForWebApiFn GetAuthTicketForWebApi;
	QL_SteamAPI_BeginAuthSessionFn BeginAuthSession;
	QL_SteamAPI_CancelAuthTicketFn CancelAuthTicket;
	QL_SteamAPI_EndAuthSessionFn EndAuthSession;
	QL_SteamAPI_GetSteamIDFn GetSteamID;
	qboolean gameServerInitialised;
	qboolean useGameServerUGC;
	ql_steam_client_callback_state_t clientCallbacks;
	ql_steam_avatar_callback_state_t avatarCallbacks;
	ql_steam_server_callback_state_t serverCallbacks;
	ql_steam_lobby_callback_state_t lobbyCallbacks;
	ql_steam_micro_callback_state_t microCallbacks;
	ql_steam_workshop_callback_state_t workshopCallbacks;
} ql_steamworks_state_t;

static ql_steamworks_state_t state;

#define QL_STEAM_UGC_DETAILS_BUFFER_SIZE 12288
#define QL_STEAM_UGC_DETAILS_PUBLISHED_FILE_ID_OFFSET 0x00
#define QL_STEAM_UGC_DETAILS_PUBLISHED_FILE_ID_SIZE 0x08
#define QL_STEAM_UGC_DETAILS_TITLE_OFFSET 0x18
#define QL_STEAM_UGC_DETAILS_DESCRIPTION_OFFSET 0x99
#define QL_STEAM_UGC_GET_ALL_QUERY_TYPE 1
#define QL_STEAM_UGC_GET_ALL_MATCHING_TYPE 0

#define QL_STEAM_GAMESERVER_MODE_NO_AUTH 2
#define QL_STEAM_GAMESERVER_MODE_AUTH_SECURE 3

#define QL_STEAM_CALLBACK_RICH_PRESENCE_JOIN_REQUESTED 0x151
#define QL_STEAM_CALLBACK_USER_STATS_RECEIVED 0x44d
#define QL_STEAM_CALLBACK_PERSONA_STATE_CHANGE 0x130
#define QL_STEAM_CALLBACK_STEAM_SERVERS_CONNECTED 0x65
#define QL_STEAM_CALLBACK_STEAM_SERVER_CONNECT_FAILURE 0x66
#define QL_STEAM_CALLBACK_STEAM_SERVERS_DISCONNECTED 0x67
#define QL_STEAM_CALLBACK_VALIDATE_AUTH_TICKET_RESPONSE 0x8f
#define QL_STEAM_CALLBACK_GET_TICKET_FOR_WEB_API_RESPONSE 0xa8
#define QL_STEAM_CALLBACK_P2P_SESSION_REQUEST 0x4b2
#define QL_STEAM_CALLBACK_GS_STATS_RECEIVED 0x708
#define QL_STEAM_CALLBACK_GS_STATS_STORED 0x709
#define QL_STEAM_CALLBACK_GAME_SERVER_CHANGE_REQUESTED 0x14c
#define QL_STEAM_CALLBACK_FRIEND_RICH_PRESENCE_UPDATE 0x150
#define QL_STEAM_CALLBACK_AVATAR_IMAGE_LOADED 0x14e
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
#define QL_STEAM_CALLBACK_FLAG_REGISTERED 0x01
#define QL_STEAM_CALLBACK_FLAG_GAMESERVER 0x02
#define QL_STEAM_ERESULT_OK 1
#define QL_STEAM_WEB_API_TICKET_CALLBACK_PUMPS 16
#define QL_STEAM_NETWORKING_SEND_P2P_PACKET_SLOT 0
#define QL_STEAM_NETWORKING_IS_P2P_PACKET_AVAILABLE_SLOT 1
#define QL_STEAM_NETWORKING_READ_P2P_PACKET_SLOT 2
#define QL_STEAM_NETWORKING_ACCEPT_P2P_SESSION_SLOT (0x0c / 4)
#define QL_STEAM_USER_BLOGGED_ON_SLOT (0x04 / 4)
#define QL_STEAM_USER_GET_STEAM_ID_SLOT (0x08 / 4)
#define QL_STEAM_USER_START_VOICE_RECORDING_SLOT (0x1c / 4)
#define QL_STEAM_USER_STOP_VOICE_RECORDING_SLOT (0x20 / 4)
#define QL_STEAM_USER_GET_VOICE_SLOT (0x28 / 4)
#define QL_STEAM_USER_DECOMPRESS_VOICE_SLOT (0x2c / 4)
#define QL_STEAM_USER_GET_VOICE_OPTIMAL_SAMPLE_RATE_SLOT (0x30 / 4)
#define QL_STEAM_FRIENDS_GET_PERSONA_NAME_SLOT 0
#define QL_STEAM_FRIENDS_GET_FRIEND_COUNT_SLOT (0x0c / 4)
#define QL_STEAM_FRIENDS_GET_FRIEND_BY_INDEX_SLOT (0x10 / 4)
#define QL_STEAM_FRIENDS_GET_FRIEND_RELATIONSHIP_SLOT (0x14 / 4)
#define QL_STEAM_FRIENDS_GET_FRIEND_PERSONA_STATE_SLOT (0x18 / 4)
#define QL_STEAM_FRIENDS_GET_FRIEND_PERSONA_NAME_SLOT (0x1c / 4)
#define QL_STEAM_FRIENDS_GET_FRIEND_GAME_PLAYED_SLOT (0x20 / 4)
#define QL_STEAM_FRIENDS_GET_PLAYER_NICKNAME_SLOT (0x2c / 4)
#define QL_STEAM_FRIENDS_SET_IN_GAME_VOICE_SPEAKING_SLOT (0x6c / 4)
#define QL_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_TO_USER_SLOT (0x74 / 4)
#define QL_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_TO_WEB_PAGE_SLOT (0x78 / 4)
#define QL_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_INVITE_DIALOG_SLOT (0x84 / 4)
#define QL_STEAM_FRIENDS_GET_SMALL_FRIEND_AVATAR_SLOT (0x88 / 4)
#define QL_STEAM_FRIENDS_GET_MEDIUM_FRIEND_AVATAR_SLOT (0x8c / 4)
#define QL_STEAM_FRIENDS_GET_LARGE_FRIEND_AVATAR_SLOT (0x90 / 4)
#define QL_STEAM_FRIENDS_SET_RICH_PRESENCE_SLOT (0xac / 4)
#define QL_STEAM_FRIENDS_GET_FRIEND_RICH_PRESENCE_SLOT (0xb4 / 4)
#define QL_STEAM_FRIENDS_INVITE_USER_TO_GAME_SLOT (0xc4 / 4)
#define QL_STEAM_UTILS_GET_IP_COUNTRY_SLOT (0x10 / 4)
#define QL_STEAM_UTILS_GET_IMAGE_SIZE_SLOT (0x14 / 4)
#define QL_STEAM_UTILS_GET_IMAGE_RGBA_SLOT (0x18 / 4)
#define QL_STEAM_UTILS_GET_APP_ID_SLOT (0x24 / 4)
#define QL_STEAM_APPS_BIS_SUBSCRIBED_APP_SLOT (0x1c / 4)
#define QL_STEAM_MATCHMAKING_ADD_FAVORITE_GAME_SLOT (0x08 / 4)
#define QL_STEAM_MATCHMAKING_REMOVE_FAVORITE_GAME_SLOT (0x0c / 4)
#define QL_STEAM_MATCHMAKING_CREATE_LOBBY_SLOT (0x34 / 4)
#define QL_STEAM_MATCHMAKING_JOIN_LOBBY_SLOT (0x38 / 4)
#define QL_STEAM_MATCHMAKING_LEAVE_LOBBY_SLOT (0x3c / 4)
#define QL_STEAM_MATCHMAKING_INVITE_USER_TO_LOBBY_SLOT (0x40 / 4)
#define QL_STEAM_MATCHMAKING_GET_NUM_LOBBY_MEMBERS_SLOT (0x44 / 4)
#define QL_STEAM_MATCHMAKING_GET_LOBBY_MEMBER_BY_INDEX_SLOT (0x48 / 4)
#define QL_STEAM_MATCHMAKING_SET_LOBBY_DATA_SLOT (0x50 / 4)
#define QL_STEAM_MATCHMAKING_GET_LOBBY_DATA_COUNT_SLOT (0x54 / 4)
#define QL_STEAM_MATCHMAKING_GET_LOBBY_DATA_BY_INDEX_SLOT (0x58 / 4)
#define QL_STEAM_MATCHMAKING_SEND_LOBBY_CHAT_MSG_SLOT (0x68 / 4)
#define QL_STEAM_MATCHMAKING_GET_LOBBY_CHAT_ENTRY_SLOT (0x6c / 4)
#define QL_STEAM_MATCHMAKING_SET_LOBBY_GAME_SERVER_SLOT (0x74 / 4)
#define QL_STEAM_MATCHMAKING_GET_LOBBY_MEMBER_LIMIT_SLOT (0x80 / 4)
#define QL_STEAM_MATCHMAKING_GET_LOBBY_OWNER_SLOT (0x8c / 4)
#define QL_STEAM_MATCHMAKING_SERVERS_REQUEST_INTERNET_SERVER_LIST_SLOT 0
#define QL_STEAM_MATCHMAKING_SERVERS_REQUEST_LAN_SERVER_LIST_SLOT (0x04 / 4)
#define QL_STEAM_MATCHMAKING_SERVERS_REQUEST_FRIENDS_SERVER_LIST_SLOT (0x08 / 4)
#define QL_STEAM_MATCHMAKING_SERVERS_REQUEST_FAVORITES_SERVER_LIST_SLOT (0x0c / 4)
#define QL_STEAM_MATCHMAKING_SERVERS_REQUEST_HISTORY_SERVER_LIST_SLOT (0x10 / 4)
#define QL_STEAM_MATCHMAKING_SERVERS_RELEASE_REQUEST_SLOT (0x18 / 4)
#define QL_STEAM_MATCHMAKING_SERVERS_GET_SERVER_DETAILS_SLOT (0x1c / 4)
#define QL_STEAM_MATCHMAKING_SERVERS_REFRESH_QUERY_SLOT (0x24 / 4)
#define QL_STEAM_MATCHMAKING_SERVERS_PING_SERVER_SLOT (0x34 / 4)
#define QL_STEAM_MATCHMAKING_SERVERS_PLAYER_DETAILS_SLOT (0x38 / 4)
#define QL_STEAM_MATCHMAKING_SERVERS_SERVER_RULES_SLOT (0x3c / 4)
#define QL_STEAM_MATCHMAKING_SERVERS_CANCEL_SERVER_QUERY_SLOT (0x40 / 4)
#define QL_STEAM_USERSTATS_GET_ACHIEVEMENT_DISPLAY_ATTRIBUTE_SLOT (0x30 / 4)
#define QL_STEAM_USERSTATS_REQUEST_USER_STATS_SLOT (0x40 / 4)
#define QL_STEAM_USERSTATS_GET_USER_STAT_FLOAT_SLOT (0x44 / 4)
#define QL_STEAM_USERSTATS_GET_USER_STAT_INT_SLOT (0x48 / 4)
#define QL_STEAM_USERSTATS_GET_USER_ACHIEVEMENT_SLOT (0x50 / 4)
#define QL_STEAM_USERSTATS_RESET_ALL_STATS_SLOT (0x54 / 4)
#define QL_STEAM_GAMESERVER_SET_PRODUCT_SLOT (0x04 / 4)
#define QL_STEAM_GAMESERVER_SET_GAME_DESCRIPTION_SLOT (0x08 / 4)
#define QL_STEAM_GAMESERVER_SET_GAME_DIR_SLOT (0x0c / 4)
#define QL_STEAM_GAMESERVER_SET_DEDICATED_SLOT (0x10 / 4)
#define QL_STEAM_GAMESERVER_LOG_ON_SLOT (0x14 / 4)
#define QL_STEAM_GAMESERVER_LOG_ON_ANONYMOUS_SLOT (0x18 / 4)
#define QL_STEAM_GAMESERVER_BLOGGED_ON_SLOT (0x20 / 4)
#define QL_STEAM_GAMESERVER_GET_STEAM_ID_SLOT (0x28 / 4)
#define QL_STEAM_GAMESERVER_SET_MAX_PLAYER_COUNT_SLOT (0x30 / 4)
#define QL_STEAM_GAMESERVER_SET_BOT_PLAYER_COUNT_SLOT (0x34 / 4)
#define QL_STEAM_GAMESERVER_SET_SERVER_NAME_SLOT (0x38 / 4)
#define QL_STEAM_GAMESERVER_SET_MAP_NAME_SLOT (0x3c / 4)
#define QL_STEAM_GAMESERVER_SET_PASSWORD_PROTECTED_SLOT (0x40 / 4)
#define QL_STEAM_GAMESERVER_SET_KEY_VALUE_SLOT (0x50 / 4)
#define QL_STEAM_GAMESERVER_SET_GAME_TAGS_SLOT (0x54 / 4)
#define QL_STEAM_GAMESERVER_CREATE_UNAUTHENTICATED_USER_SLOT (0x64 / 4)
#define QL_STEAM_GAMESERVER_UPDATE_USER_DATA_SLOT (0x6c / 4)
#define QL_STEAM_GAMESERVER_BEGIN_AUTH_SESSION_SLOT (0x74 / 4)
#define QL_STEAM_GAMESERVER_END_AUTH_SESSION_SLOT (0x78 / 4)
#define QL_STEAM_GAMESERVER_GET_PUBLIC_IP_SLOT (0x90 / 4)
#define QL_STEAM_GAMESERVER_HANDLE_INCOMING_PACKET_SLOT (0x94 / 4)
#define QL_STEAM_GAMESERVER_GET_NEXT_OUTGOING_PACKET_SLOT (0x98 / 4)
#define QL_STEAM_GAMESERVER_ENABLE_HEARTBEATS_SLOT (0x9c / 4)
#define QL_STEAM_GAMESERVER_UTILS_GET_APP_ID_SLOT (0x24 / 4)
#define QL_STEAM_GAMESERVERSTATS_REQUEST_USER_STATS_SLOT 0
#define QL_STEAM_GAMESERVERSTATS_GET_USER_STAT_FLOAT_SLOT (0x04 / 4)
#define QL_STEAM_GAMESERVERSTATS_GET_USER_STAT_INT_SLOT (0x08 / 4)
#define QL_STEAM_GAMESERVERSTATS_GET_USER_ACHIEVEMENT_SLOT (0x0c / 4)
#define QL_STEAM_GAMESERVERSTATS_SET_USER_STAT_FLOAT_SLOT (0x10 / 4)
#define QL_STEAM_GAMESERVERSTATS_SET_USER_STAT_INT_SLOT (0x14 / 4)
#define QL_STEAM_GAMESERVERSTATS_UPDATE_AVG_RATE_STAT_SLOT (0x18 / 4)
#define QL_STEAM_GAMESERVERSTATS_SET_USER_ACHIEVEMENT_SLOT (0x1c / 4)
#define QL_STEAM_GAMESERVERSTATS_STORE_USER_STATS_SLOT (0x24 / 4)
#define QL_STEAM_UGC_CREATE_QUERY_ALL_UGC_REQUEST_SLOT (0x04 / 4)
#define QL_STEAM_UGC_SEND_QUERY_UGC_REQUEST_SLOT (0x0c / 4)
#define QL_STEAM_UGC_GET_QUERY_UGC_RESULT_SLOT (0x10 / 4)
#define QL_STEAM_UGC_GET_QUERY_UGC_PREVIEW_URL_SLOT (0x14 / 4)
#define QL_STEAM_UGC_RELEASE_QUERY_UGC_REQUEST_SLOT (0x34 / 4)
#define QL_STEAM_UGC_SUBSCRIBE_ITEM_SLOT (0xc0 / 4)
#define QL_STEAM_UGC_UNSUBSCRIBE_ITEM_SLOT (0xc4 / 4)
#define QL_STEAM_UGC_GET_NUM_SUBSCRIBED_ITEMS_SLOT (0xc8 / 4)
#define QL_STEAM_UGC_GET_SUBSCRIBED_ITEMS_SLOT (0xcc / 4)
#define QL_STEAM_UGC_GET_ITEM_STATE_SLOT (0xd0 / 4)
#define QL_STEAM_UGC_GET_ITEM_INSTALL_INFO_SLOT (0xd4 / 4)
#define QL_STEAM_UGC_GET_ITEM_DOWNLOAD_INFO_SLOT (0xd8 / 4)
#define QL_STEAM_UGC_DOWNLOAD_ITEM_SLOT (0xdc / 4)

/*
=============
QL_Steamworks_CallHandleLow

Returns the low 32 bits of a SteamAPICall_t handle.
=============
*/
static uint32_t QL_Steamworks_CallHandleLow( SteamAPICall_t callHandle ) {
	return (uint32_t)callHandle;
}

/*
=============
QL_Steamworks_CallHandleHigh

Returns the high 32 bits of a SteamAPICall_t handle.
=============
*/
static uint32_t QL_Steamworks_CallHandleHigh( SteamAPICall_t callHandle ) {
	return (uint32_t)( callHandle >> 32 );
}

/*
=============
QL_Steamworks_CombineCallHandle

Rebuilds a SteamAPICall_t handle from retail low/high words.
=============
*/
static SteamAPICall_t QL_Steamworks_CombineCallHandle( uint32_t low, uint32_t high ) {
	return ( (SteamAPICall_t)high << 32 ) | (SteamAPICall_t)low;
}

/*
=============
QL_Steamworks_CallbackMemberRunImpl

Dispatches the retail CCallback member-function slot into SRP's retained
binding metadata.
=============
*/
static void QL_Steamworks_CallbackMemberRunImpl( ql_steam_callback_base_t *self, void *payload ) {
	if ( !self || !self->dispatch ) {
		return;
	}

	self->dispatch( self->context, payload );
}

/*
=============
QL_Steamworks_CallbackCallResultMemberRunImpl

Dispatches the retail CCallResult member-function slot into SRP's retained
binding metadata.
=============
*/
static void QL_Steamworks_CallbackCallResultMemberRunImpl( ql_steam_callback_base_t *self, void *payload, qboolean ioFailure ) {
	SteamAPICall_t callHandle;

	if ( !self ) {
		return;
	}

	callHandle = QL_Steamworks_CombineCallHandle( self->callResultHandleLow, self->callResultHandleHigh );
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
QL_Steamworks_CallbackRunImpl

Dispatches a normal Steam callback into the retained binding owner.
=============
*/
static void QL_Steamworks_CallbackRunImpl( ql_steam_callback_base_t *self, void *payload ) {
	if ( !self ) {
		return;
	}

	QL_Steamworks_CallbackMemberRunImpl( self, payload );
}

/*
=============
QL_Steamworks_CallbackRunCallResultAdapterImpl

Dispatches a call-result through the retail adapter slot without an explicit
call handle.
=============
*/
static void QL_Steamworks_CallbackRunCallResultAdapterImpl( ql_steam_callback_base_t *self, void *payload ) {
	SteamAPICall_t callHandle;

	if ( !self ) {
		return;
	}

	callHandle = QL_Steamworks_CombineCallHandle( self->callResultHandleLow, self->callResultHandleHigh );
	self->callResultHandleLow = 0u;
	self->callResultHandleHigh = 0u;

	if ( self->dispatchCallResult ) {
		self->dispatchCallResult( self->context, payload, qfalse, callHandle );
		return;
	}

	if ( self->dispatch ) {
		self->dispatch( self->context, payload );
	}
}

/*
=============
QL_Steamworks_CallbackRunCallResultImpl

Dispatches a Steam call-result into the retained binding owner.
=============
*/
static void QL_Steamworks_CallbackRunCallResultImpl( ql_steam_callback_base_t *self, void *payload, qboolean ioFailure, SteamAPICall_t callHandle ) {
	uint32_t low;
	uint32_t high;

	if ( !self ) {
		return;
	}

	low = QL_Steamworks_CallHandleLow( callHandle );
	high = QL_Steamworks_CallHandleHigh( callHandle );
	if ( low != self->callResultHandleLow || high != self->callResultHandleHigh ) {
		return;
	}

	self->callResultHandleLow = 0u;
	self->callResultHandleHigh = 0u;

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
QL_Steamworks_CallbackGetSizeImpl

Returns the payload size expected by the Steam callback object.
=============
*/
static int QL_Steamworks_CallbackGetSizeImpl( ql_steam_callback_base_t *self ) {
	if ( !self ) {
		return 0;
	}

	return self->payloadSize;
}

#if QL_STEAMWORKS_USE_MSVC_C_THISCALL_THUNKS
/*
=============
QL_Steamworks_CallbackMemberRun

Adapts Steam's retail CCallback member-function slot to C.
=============
*/
static __declspec(naked) void QL_Steamworks_CallbackMemberRun( ql_steam_callback_base_t *self, void *payload ) {
	__asm {
		push dword ptr [esp + 4]
		push ecx
		call QL_Steamworks_CallbackMemberRunImpl
		add esp, 8
		ret 4
	}
}

/*
=============
QL_Steamworks_CallbackCallResultMemberRun

Adapts Steam's retail CCallResult member-function slot to C.
=============
*/
static __declspec(naked) void QL_Steamworks_CallbackCallResultMemberRun( ql_steam_callback_base_t *self, void *payload, qboolean ioFailure ) {
	__asm {
		push dword ptr [esp + 8]
		push dword ptr [esp + 8]
		push ecx
		call QL_Steamworks_CallbackCallResultMemberRunImpl
		add esp, 12
		ret 8
	}
}

/*
=============
QL_Steamworks_CallbackRun

Adapts Steam's x86 thiscall callback ABI to the C implementation.
=============
*/
static __declspec(naked) void QL_Steamworks_CallbackRun( ql_steam_callback_base_t *self, void *payload ) {
	__asm {
		push dword ptr [esp + 4]
		push ecx
		call QL_Steamworks_CallbackRunImpl
		add esp, 8
		ret 4
	}
}

/*
=============
QL_Steamworks_CallbackRunAdapter

Adapts Steam's retail CCallback vtable adapter slot to C.
=============
*/
static __declspec(naked) void QL_Steamworks_CallbackRunAdapter( ql_steam_callback_base_t *self, void *payload ) {
	__asm {
		push dword ptr [esp + 4]
		push ecx
		call QL_Steamworks_CallbackRunImpl
		add esp, 8
		ret 4
	}
}

/*
=============
QL_Steamworks_CallbackRunCallResult

Adapts Steam's x86 thiscall call-result ABI to the C implementation.
=============
*/
static __declspec(naked) void QL_Steamworks_CallbackRunCallResult( ql_steam_callback_base_t *self, void *payload, qboolean ioFailure, SteamAPICall_t callHandle ) {
	__asm {
		push dword ptr [esp + 16]
		push dword ptr [esp + 16]
		push dword ptr [esp + 16]
		push dword ptr [esp + 16]
		push ecx
		call QL_Steamworks_CallbackRunCallResultImpl
		add esp, 20
		ret 16
	}
}

/*
=============
QL_Steamworks_CallbackRunCallResultAdapter

Adapts Steam's retail CCallResult vtable adapter slot to C.
=============
*/
static __declspec(naked) void QL_Steamworks_CallbackRunCallResultAdapter( ql_steam_callback_base_t *self, void *payload ) {
	__asm {
		push dword ptr [esp + 4]
		push ecx
		call QL_Steamworks_CallbackRunCallResultAdapterImpl
		add esp, 8
		ret 4
	}
}

/*
=============
QL_Steamworks_CallbackGetSize

Adapts Steam's x86 thiscall payload-size query ABI to the C implementation.
=============
*/
static __declspec(naked) int QL_Steamworks_CallbackGetSize( ql_steam_callback_base_t *self ) {
	__asm {
		push ecx
		call QL_Steamworks_CallbackGetSizeImpl
		add esp, 4
		ret
	}
}
#else
/*
=============
QL_Steamworks_CallbackMemberRun

Dispatches the retail CCallback member-function slot through the configured
calling convention.
=============
*/
static void QL_STEAMWORKS_THISCALL QL_Steamworks_CallbackMemberRun( ql_steam_callback_base_t *self, void *payload ) {
	QL_Steamworks_CallbackMemberRunImpl( self, payload );
}

/*
=============
QL_Steamworks_CallbackCallResultMemberRun

Dispatches the retail CCallResult member-function slot through the configured
calling convention.
=============
*/
static void QL_STEAMWORKS_THISCALL QL_Steamworks_CallbackCallResultMemberRun( ql_steam_callback_base_t *self, void *payload, qboolean ioFailure ) {
	QL_Steamworks_CallbackCallResultMemberRunImpl( self, payload, ioFailure );
}

/*
=============
QL_Steamworks_CallbackRun

Dispatches a normal Steam callback through the configured calling convention.
=============
*/
static void QL_STEAMWORKS_THISCALL QL_Steamworks_CallbackRun( ql_steam_callback_base_t *self, void *payload ) {
	QL_Steamworks_CallbackRunImpl( self, payload );
}

/*
=============
QL_Steamworks_CallbackRunAdapter

Dispatches a normal Steam callback through the retail adapter slot.
=============
*/
static void QL_STEAMWORKS_THISCALL QL_Steamworks_CallbackRunAdapter( ql_steam_callback_base_t *self, void *payload ) {
	QL_Steamworks_CallbackRunImpl( self, payload );
}

/*
=============
QL_Steamworks_CallbackRunCallResult

Dispatches a Steam call-result through the configured calling convention.
=============
*/
static void QL_STEAMWORKS_THISCALL QL_Steamworks_CallbackRunCallResult( ql_steam_callback_base_t *self, void *payload, qboolean ioFailure, SteamAPICall_t callHandle ) {
	QL_Steamworks_CallbackRunCallResultImpl( self, payload, ioFailure, callHandle );
}

/*
=============
QL_Steamworks_CallbackRunCallResultAdapter

Dispatches a call-result through the retail adapter slot.
=============
*/
static void QL_STEAMWORKS_THISCALL QL_Steamworks_CallbackRunCallResultAdapter( ql_steam_callback_base_t *self, void *payload ) {
	QL_Steamworks_CallbackRunCallResultAdapterImpl( self, payload );
}

/*
=============
QL_Steamworks_CallbackGetSize

Returns the callback payload size through the configured calling convention.
=============
*/
static int QL_STEAMWORKS_THISCALL QL_Steamworks_CallbackGetSize( ql_steam_callback_base_t *self ) {
	return QL_Steamworks_CallbackGetSizeImpl( self );
}
#endif

static const ql_steam_callback_vtable_t ql_steam_callback_vtable = {
	(ql_steam_callback_vfunc_t)QL_Steamworks_CallbackRun,
	(ql_steam_callback_vfunc_t)QL_Steamworks_CallbackRunAdapter,
	(ql_steam_callback_vfunc_t)QL_Steamworks_CallbackGetSize
};

static const ql_steam_callback_vtable_t ql_steam_call_result_vtable = {
	(ql_steam_callback_vfunc_t)QL_Steamworks_CallbackRunCallResult,
	(ql_steam_callback_vfunc_t)QL_Steamworks_CallbackRunCallResultAdapter,
	(ql_steam_callback_vfunc_t)QL_Steamworks_CallbackGetSize
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
QL_Steamworks_FormatServerListFallbackName

Builds the retail fallback name used for unnamed server-browser rows.
=============
*/
static void QL_Steamworks_FormatServerListFallbackName( char *buffer, size_t bufferSize, const ql_steam_gameserveritem_raw_t *raw ) {
	int safeSize;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !raw ) {
		return;
	}

	safeSize = ( bufferSize > (size_t)INT_MAX ) ? INT_MAX : (int)bufferSize;
	Com_sprintf(
		buffer,
		safeSize,
		"%u.%u.%u.%u:%i",
		(unsigned int)( ( raw->ip >> 24 ) & 0xffu ),
		(unsigned int)( ( raw->ip >> 16 ) & 0xffu ),
		(unsigned int)( ( raw->ip >> 8 ) & 0xffu ),
		(unsigned int)( raw->ip & 0xffu ),
		(int)raw->connectionPort
	);
}

/*
=============
QL_Steamworks_CopyServerListDisplayName

Copies the row name or reconstructs retail's address fallback when it is empty.
=============
*/
static void QL_Steamworks_CopyServerListDisplayName( ql_steam_server_item_t *outServer, const ql_steam_gameserveritem_raw_t *raw ) {
	if ( !outServer || !raw ) {
		return;
	}

	if ( raw->serverName[0] ) {
		QL_Steamworks_CopySteamString( outServer->displayName, sizeof( outServer->displayName ), raw->serverName );
		return;
	}

	QL_Steamworks_FormatServerListFallbackName( outServer->displayName, sizeof( outServer->displayName ), raw );
}

/*
=============
QL_Steamworks_CopyServerListDetails

Projects the retained gameserveritem_t-style row into the public wrapper type.
=============
*/
static void QL_Steamworks_CopyServerListDetails( ql_steam_server_item_t *outServer, const ql_steam_gameserveritem_raw_t *raw ) {
	if ( !outServer ) {
		return;
	}

	memset( outServer, 0, sizeof( *outServer ) );
	if ( !raw ) {
		return;
	}

	outServer->serverIp = raw->ip;
	outServer->serverPort = raw->connectionPort;
	outServer->queryPort = raw->queryPort;
	outServer->ping = raw->ping;
	outServer->appId = raw->appId;
	outServer->numPlayers = raw->players;
	outServer->maxPlayers = raw->maxPlayers;
	outServer->botPlayers = raw->botPlayers;
	outServer->passwordProtected = raw->password ? qtrue : qfalse;
	outServer->vacSecured = raw->secure ? qtrue : qfalse;
	outServer->lastPlayed = raw->lastPlayed;
	outServer->serverVersion = raw->serverVersion;
	outServer->steamId.value = ( (uint64_t)raw->steamIdHigh << 32 ) | raw->steamIdLow;
	QL_Steamworks_CopySteamString( outServer->gameDir, sizeof( outServer->gameDir ), raw->gameDir );
	QL_Steamworks_CopySteamString( outServer->map, sizeof( outServer->map ), raw->map );
	QL_Steamworks_CopySteamString( outServer->gameDescription, sizeof( outServer->gameDescription ), raw->gameDescription );
	QL_Steamworks_CopySteamString( outServer->name, sizeof( outServer->name ), raw->serverName );
	QL_Steamworks_CopyServerListDisplayName( outServer, raw );
	QL_Steamworks_CopySteamString( outServer->tags, sizeof( outServer->tags ), raw->gameTags );
}

/*
=============
QL_Steamworks_CopyServerBrowserResponse

Projects one typed server row into the retained browser response payload shape.
=============
*/
static void QL_Steamworks_CopyServerBrowserResponse( ql_steam_server_browser_response_t *outResponse, const ql_steam_server_item_t *server ) {
	if ( !outResponse ) {
		return;
	}

	memset( outResponse, 0, sizeof( *outResponse ) );
	if ( !server ) {
		return;
	}

	QL_Steamworks_FormatServerBrowserResponseId( server->serverIp, server->serverPort, outResponse->id, sizeof( outResponse->id ) );
	QL_Steamworks_CopySteamString( outResponse->name, sizeof( outResponse->name ), server->displayName );
	outResponse->numPlayers = server->numPlayers;
	outResponse->maxPlayers = server->maxPlayers;
	outResponse->ping = server->ping;
	QL_Steamworks_CopySteamString( outResponse->map, sizeof( outResponse->map ), server->map );
	outResponse->botPlayers = server->botPlayers;
	outResponse->passwordProtected = server->passwordProtected;
	outResponse->vacSecured = server->vacSecured;
	outResponse->serverIp = server->serverIp;
	outResponse->serverPort = server->serverPort;
	Com_sprintf( outResponse->steamId, sizeof( outResponse->steamId ), "%llu", (unsigned long long)server->steamId.value );
	QL_Steamworks_CopySteamString( outResponse->tags, sizeof( outResponse->tags ), server->tags );
	QL_Steamworks_CopySteamString( outResponse->gametype, sizeof( outResponse->gametype ), server->gameDescription );
	outResponse->lastPlayed = server->lastPlayed;
}

/*
=============
QL_Steamworks_ServerBrowserAppIdsCompatible

Accepts exact server-browser app-id matches, plus SRP's documented public
retail/reference app-id interop pair for native browser discovery.
=============
*/
static qboolean QL_Steamworks_ServerBrowserAppIdsCompatible( uint32_t rowAppId, uint32_t requestAppId ) {
	if ( rowAppId == 0u || requestAppId == 0u ) {
		return qfalse;
	}

	if ( rowAppId == requestAppId ) {
		return qtrue;
	}

	if ( ( rowAppId == QL_STEAM_APPID_PUBLIC_RETAIL && requestAppId == QL_STEAM_APPID_REFERENCE_RETAIL ) ||
		( rowAppId == QL_STEAM_APPID_REFERENCE_RETAIL && requestAppId == QL_STEAM_APPID_PUBLIC_RETAIL ) ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
QL_Steamworks_PrepareCallbackObject

Initialises a CCallbackBase-compatible object with the retained binding owner.
=============
*/
static void QL_Steamworks_PrepareCallbackObject( ql_steam_callback_base_t *object, int callbackId, int payloadSize, qboolean gameServer, void *context,
	void (*dispatch)( void *context, const void *payload ),
	void (*dispatchCallResult)( void *context, const void *payload, qboolean ioFailure, SteamAPICall_t callHandle ) ) {
	if ( !object ) {
		return;
	}

	memset( object, 0, sizeof( *object ) );
	object->vtable = dispatchCallResult ? &ql_steam_call_result_vtable : &ql_steam_callback_vtable;
	if ( gameServer ) {
		object->callbackFlags |= QL_STEAM_CALLBACK_FLAG_GAMESERVER;
	}
	object->callbackId = callbackId;
	object->owner = object;
	object->memberFunction = QL_Steamworks_CallbackMemberRun;
	object->callResultOwner = object;
	object->callResultMemberFunction = QL_Steamworks_CallbackCallResultMemberRun;
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
	object->callbackFlags |= QL_STEAM_CALLBACK_FLAG_REGISTERED;
	return qtrue;
}

/*
=============
QL_Steamworks_UnregisterCallbackObject

Unregisters one retained callback object from the Steam runtime.
=============
*/
static void QL_Steamworks_UnregisterCallbackObject( ql_steam_callback_base_t *object ) {
	if ( !object ) {
		return;
	}

	if ( !( object->callbackFlags & QL_STEAM_CALLBACK_FLAG_REGISTERED ) ) {
		return;
	}

	if ( state.SteamAPI_UnregisterCallback ) {
		state.SteamAPI_UnregisterCallback( object );
	}
	object->callbackFlags &= ~QL_STEAM_CALLBACK_FLAG_REGISTERED;
}

/*
=============
QL_Steamworks_ResetWebApiAuthTicketState

Clears the retained Web API ticket response without disturbing callback
registration.
=============
*/
static void QL_Steamworks_ResetWebApiAuthTicketState( ql_steam_client_callback_state_t *callbackState ) {
	if ( !callbackState ) {
		return;
	}

	callbackState->webApiTicketActive = qfalse;
	callbackState->webApiTicketCompleted = qfalse;
	callbackState->webApiTicketHandle = 0;
	callbackState->webApiTicketResult = 0;
	callbackState->webApiTicketLength = 0u;
	memset( callbackState->webApiTicket, 0, sizeof( callbackState->webApiTicket ) );
}

/*
=============
QL_Steamworks_DispatchGetTicketForWebApiResponse

Captures the callback generated by ISteamUser::GetAuthTicketForWebApi.
=============
*/
static void QL_Steamworks_DispatchGetTicketForWebApiResponse( void *context, const void *payload ) {
	ql_steam_client_callback_state_t *callbackState;
	const ql_steam_get_ticket_for_web_api_response_raw_t *raw;

	callbackState = (ql_steam_client_callback_state_t *)context;
	raw = (const ql_steam_get_ticket_for_web_api_response_raw_t *)payload;
	if ( !callbackState || !raw ) {
		return;
	}

	if ( !callbackState->webApiTicketActive || raw->authTicket != callbackState->webApiTicketHandle ) {
		return;
	}

	callbackState->webApiTicketCompleted = qtrue;
	callbackState->webApiTicketResult = raw->result;
	callbackState->webApiTicketLength = 0u;
	memset( callbackState->webApiTicket, 0, sizeof( callbackState->webApiTicket ) );

	if ( raw->ticketLength == 0u || raw->ticketLength > sizeof( callbackState->webApiTicket ) ) {
		return;
	}

	memcpy( callbackState->webApiTicket, raw->ticket, raw->ticketLength );
	callbackState->webApiTicketLength = raw->ticketLength;
}

/*
=============
QL_Steamworks_RegisterWebApiAuthTicketCallback

Registers the Web API ticket response callback on demand.
=============
*/
static qboolean QL_Steamworks_RegisterWebApiAuthTicketCallback( void ) {
	ql_steam_client_callback_state_t *callbackState;

	if ( !state.SteamAPI_RegisterCallback ) {
		return qfalse;
	}

	callbackState = &state.clientCallbacks;
	if ( callbackState->webApiTicketResponse.callbackFlags & QL_STEAM_CALLBACK_FLAG_REGISTERED ) {
		return qtrue;
	}

	QL_Steamworks_PrepareCallbackObject( &callbackState->webApiTicketResponse,
		QL_STEAM_CALLBACK_GET_TICKET_FOR_WEB_API_RESPONSE,
		QL_STEAM_CALLBACK_SIZE_GET_TICKET_FOR_WEB_API_RESPONSE,
		qfalse,
		callbackState,
		QL_Steamworks_DispatchGetTicketForWebApiResponse,
		NULL );

	return QL_Steamworks_RegisterCallbackObject( &callbackState->webApiTicketResponse );
}

/*
=============
QL_Steamworks_UnbindCallResultObject

Unregisters one retained call-result object from the Steam runtime.
=============
*/
static void QL_Steamworks_UnbindCallResultObject( ql_steam_callback_base_t *object, SteamAPICall_t *callHandle, qboolean *bound ) {
	if ( !object || !callHandle || !bound || !*bound ) {
		return;
	}

	if ( state.SteamAPI_UnregisterCallResult ) {
		state.SteamAPI_UnregisterCallResult( object, *callHandle );
	}
	object->callResultHandleLow = 0u;
	object->callResultHandleHigh = 0u;
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
QL_Steamworks_LoadSymbolAlias

Resolves a required Steam export, trying the retail name before the newer SDK alias.
=============
*/
static qboolean QL_Steamworks_LoadSymbolAlias( void **target, const char *retailName, const char *sdkName ) {
	if ( QL_Steamworks_LoadSymbol( target, retailName ) ) {
		return qtrue;
	}

	if ( sdkName && sdkName[0] && QL_Steamworks_LoadSymbol( target, sdkName ) ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
QL_Steamworks_LoadOptionalSymbolAlias

Resolves an optional Steam export, trying the retail name before the newer SDK alias.
=============
*/
static void QL_Steamworks_LoadOptionalSymbolAlias( void **target, const char *retailName, const char *sdkName ) {
	if ( QL_Steamworks_LoadSymbol( target, retailName ) ) {
		return;
	}

	if ( sdkName && sdkName[0] ) {
		QL_Steamworks_LoadOptionalSymbol( target, sdkName );
	}
}

/*
=============
QL_Steamworks_LoadLibrary

Dynamically loads the Steamworks runtime and resolves required exports.
=============
*/
qboolean QL_Steamworks_LoadLibrary( void ) {
	const char *loadedName;

	if ( state.library ) {
		return qtrue;
	}

	const char *candidates[] = {
		QL_STEAMWORKS_LIB_PRIMARY,
		QL_STEAMWORKS_LIB_SECONDARY
	};

	loadedName = NULL;
	for ( size_t i = 0; i < sizeof( candidates ) / sizeof( candidates[0] ); ++i ) {
		state.library = QL_STEAMWORKS_OPEN( candidates[i] );
		if ( state.library ) {
			loadedName = candidates[i];
			break;
		}
	}

	if ( !state.library ) {
		QL_Steamworks_ResetState();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamAPI_Init, QL_STEAMWORKS_EXPORT_STEAM_API_INIT ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamAPI_Shutdown, QL_STEAMWORKS_EXPORT_STEAM_API_SHUTDOWN ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamAPI_RunCallbacks, QL_STEAMWORKS_EXPORT_STEAM_API_RUN_CALLBACKS ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamAPI_RegisterCallback, QL_STEAMWORKS_EXPORT_STEAM_API_REGISTER_CALLBACK );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamAPI_UnregisterCallback, QL_STEAMWORKS_EXPORT_STEAM_API_UNREGISTER_CALLBACK );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamAPI_RegisterCallResult, QL_STEAMWORKS_EXPORT_STEAM_API_REGISTER_CALL_RESULT );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamAPI_UnregisterCallResult, QL_STEAMWORKS_EXPORT_STEAM_API_UNREGISTER_CALL_RESULT );

	if ( !QL_Steamworks_LoadSymbolAlias( (void **)&state.SteamUser, QL_STEAMWORKS_EXPORT_STEAM_USER, QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_USER ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbolAlias( (void **)&state.SteamFriends, QL_STEAMWORKS_EXPORT_STEAM_FRIENDS, QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_FRIENDS ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	QL_Steamworks_LoadOptionalSymbolAlias( (void **)&state.SteamNetworking, QL_STEAMWORKS_EXPORT_STEAM_NETWORKING, QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_NETWORKING );
	QL_Steamworks_LoadOptionalSymbolAlias( (void **)&state.SteamUtils, QL_STEAMWORKS_EXPORT_STEAM_UTILS, QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_UTILS );
	QL_Steamworks_LoadOptionalSymbolAlias( (void **)&state.SteamUserStats, QL_STEAMWORKS_EXPORT_STEAM_USER_STATS, QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_USER_STATS );

	if ( !QL_Steamworks_LoadSymbolAlias( (void **)&state.SteamMatchmaking, QL_STEAMWORKS_EXPORT_STEAM_MATCHMAKING, QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_MATCHMAKING ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	QL_Steamworks_LoadOptionalSymbolAlias( (void **)&state.SteamMatchmakingServers, QL_STEAMWORKS_EXPORT_STEAM_MATCHMAKING_SERVERS, QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_MATCHMAKING_SERVERS );

	if ( !QL_Steamworks_LoadSymbolAlias( (void **)&state.SteamApps, QL_STEAMWORKS_EXPORT_STEAM_APPS, QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_APPS ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbolAlias( (void **)&state.SteamUGC, QL_STEAMWORKS_EXPORT_STEAM_UGC, QL_STEAMWORKS_EXPORT_STEAM_API_STEAM_UGC ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.GetAuthSessionTicket, QL_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_GET_AUTH_SESSION_TICKET ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	QL_Steamworks_LoadOptionalSymbol( (void **)&state.GetAuthTicketForWebApi, QL_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_GET_AUTH_TICKET_FOR_WEB_API );

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.BeginAuthSession, QL_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_BEGIN_AUTH_SESSION ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.CancelAuthTicket, QL_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_CANCEL_AUTH_TICKET ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.EndAuthSession, QL_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_END_AUTH_SESSION ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.GetSteamID, QL_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_GET_STEAM_ID ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServer, QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServerStats, QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_STATS );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServerUtils, QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_UTILS );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServerUGC, QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_UGC );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServer_Init, QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_INIT );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServer_Shutdown, QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_SHUTDOWN );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServer_RunCallbacks, QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_RUN_CALLBACKS );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServerNetworking, QL_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_NETWORKING );

	Com_Printf( "Steamworks: loaded %s with retail-compatible exports\n", loadedName ? loadedName : "Steam runtime" );
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
	Com_Printf( "Steamworks: SteamAPI_Init succeeded\n" );
	return qtrue;
}

/*
=============
QL_Steamworks_IsInitialized

Returns the retained Steam API live flag set by QL_Steamworks_Init.
=============
*/
qboolean QL_Steamworks_IsInitialized( void ) {
	return state.initialised ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_Shutdown

Shuts down Steamworks and releases any loaded handles.
=============
*/
void QL_Steamworks_Shutdown( void ) {
	QL_ResetPlatformServices();

	if ( !state.initialised && !state.gameServerInitialised ) {
		return;
	}

	QL_Steamworks_UnregisterAvatarCallbacks();
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

	fn = (QL_SteamUserStats_ResetAllStatsFn)vtable[QL_STEAM_USERSTATS_RESET_ALL_STATS_SLOT];
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

	fn = (QL_SteamFriends_GetPersonaNameFn)vtable[QL_STEAM_FRIENDS_GET_PERSONA_NAME_SLOT];
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

	fn = (QL_SteamUtils_GetIPCountryFn)vtable[QL_STEAM_UTILS_GET_IP_COUNTRY_SLOT];
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
QL_Steamworks_GetServerBrowserInterface
=============
*/
static void *QL_Steamworks_GetServerBrowserInterface( void ) {
	if ( !QL_Steamworks_Init() || !state.SteamMatchmakingServers ) {
		return NULL;
	}

	return state.SteamMatchmakingServers();
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

	fn = (QL_SteamUtils_GetAppIDFn)vtable[QL_STEAM_UTILS_GET_APP_ID_SLOT];
	if ( !fn ) {
		return 0u;
	}

	return fn( utils, NULL );
}

/*
=============
QL_Steamworks_IsUserLoggedOn

Checks the active Steam user login state before client auth-ticket work.
=============
*/
qboolean QL_Steamworks_IsUserLoggedOn( void ) {
	void *user;
	void **vtable;
	typedef qboolean (__fastcall *QL_SteamUser_BLoggedOnFn)( void *self, void *unused );
	QL_SteamUser_BLoggedOnFn fn;

	user = QL_Steamworks_GetUserInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( user );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUser_BLoggedOnFn)vtable[QL_STEAM_USER_BLOGGED_ON_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	return fn( user, NULL ) ? qtrue : qfalse;
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
	static qboolean loggedSteamId;
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

	fn = (QL_SteamUser_GetSteamIDFn)vtable[QL_STEAM_USER_GET_STEAM_ID_SLOT];
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

	if ( !loggedSteamId ) {
		Com_Printf( "Steamworks: local SteamID64=%llu\n", (unsigned long long)steamId.value );
		loggedSteamId = qtrue;
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

	fn = (QL_SteamFriends_SetInGameVoiceSpeakingFn)vtable[QL_STEAM_FRIENDS_SET_IN_GAME_VOICE_SPEAKING_SLOT];
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

	fn = (QL_SteamFriends_GetFriendCountFn)vtable[QL_STEAM_FRIENDS_GET_FRIEND_COUNT_SLOT];
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

	fn = (QL_SteamFriends_GetFriendByIndexFn)vtable[QL_STEAM_FRIENDS_GET_FRIEND_BY_INDEX_SLOT];
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

	getRelationshipFn = (QL_SteamFriends_GetFriendRelationshipFn)vtable[QL_STEAM_FRIENDS_GET_FRIEND_RELATIONSHIP_SLOT];
	getPersonaStateFn = (QL_SteamFriends_GetFriendPersonaStateFn)vtable[QL_STEAM_FRIENDS_GET_FRIEND_PERSONA_STATE_SLOT];
	getFriendNameFn = (QL_SteamFriends_GetFriendPersonaNameFn)vtable[QL_STEAM_FRIENDS_GET_FRIEND_PERSONA_NAME_SLOT];
	getFriendGamePlayedFn = (QL_SteamFriends_GetFriendGamePlayedFn)vtable[QL_STEAM_FRIENDS_GET_FRIEND_GAME_PLAYED_SLOT];
	getPlayerNicknameFn = (QL_SteamFriends_GetPlayerNicknameFn)vtable[QL_STEAM_FRIENDS_GET_PLAYER_NICKNAME_SLOT];
	getFriendRichPresenceFn = (QL_SteamFriends_GetFriendRichPresenceFn)vtable[QL_STEAM_FRIENDS_GET_FRIEND_RICH_PRESENCE_SLOT];
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
		outSummary->appId = (uint32_t)( gameInfo.gameId & 0x00ffffffull );
		outSummary->gameId = gameInfo.gameId;
		outSummary->serverIp = gameInfo.gameIp;
		outSummary->serverPort = gameInfo.gamePort;
		outSummary->queryPort = gameInfo.queryPort;
		outSummary->lobbyId = gameInfo.lobbyId;
		outSummary->gameServerId = gameInfo.gameServerId;
		if ( currentAppId != 0u && outSummary->appId == currentAppId ) {
			outSummary->playingQuake = qtrue;
		}
	}

	return qtrue;
}

/*
=============
QL_Steamworks_GetFriendPersonaName
=============
*/
qboolean QL_Steamworks_GetFriendPersonaName( uint32_t idLow, uint32_t idHigh, char *buffer, size_t bufferSize ) {
	void *friends;
	void **vtable;
	typedef const char *(__fastcall *QL_SteamFriends_GetFriendPersonaNameFn)( void *self, void *unused, CSteamID steamId );
	QL_SteamFriends_GetFriendPersonaNameFn fn;

	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}

	if ( !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	friends = QL_Steamworks_GetFriendsInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( friends );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamFriends_GetFriendPersonaNameFn)vtable[QL_STEAM_FRIENDS_GET_FRIEND_PERSONA_NAME_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	QL_Steamworks_CopySteamString( buffer, bufferSize, fn( friends, NULL, QL_Steamworks_CombineIdentityWords( idLow, idHigh ) ) );
	return buffer[0] != '\0' ? qtrue : qfalse;
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

	fn = (QL_SteamMatchmaking_GetLobbyChatEntryFn)vtable[QL_STEAM_MATCHMAKING_GET_LOBBY_CHAT_ENTRY_SLOT];
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
	event.steamId = QL_Steamworks_CombineIdentityWords( raw->steamIDFriendLow, raw->steamIDFriendHigh );
	event.appId = raw->appId;
	QL_Steamworks_GetFriendSummary( raw->steamIDFriendLow, raw->steamIDFriendHigh, &event.summary );
	callbackState->bindings.onFriendRichPresenceUpdate( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchAvatarImageLoaded
=============
*/
static void QL_Steamworks_DispatchAvatarImageLoaded( void *context, const void *payload ) {
	ql_steam_avatar_callback_state_t *callbackState;
	const ql_steam_avatar_image_loaded_raw_t *raw;
	ql_steam_avatar_image_loaded_t event;

	callbackState = (ql_steam_avatar_callback_state_t *)context;
	if ( !callbackState || !callbackState->bindings.onAvatarImageLoaded || !payload ) {
		return;
	}

	raw = (const ql_steam_avatar_image_loaded_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.steamId = QL_Steamworks_CombineIdentityWords( raw->steamIDLow, raw->steamIDHigh );
	event.image = raw->image;
	event.width = raw->wide;
	event.height = raw->tall;
	callbackState->bindings.onAvatarImageLoaded( callbackState->bindings.context, &event );
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
QL_Steamworks_LogServerCallbackDispatch

Publishes provider-aware diagnostics whenever the retained Steam GameServer
callback dispatch layer ignores one callback surface.
=============
*/
static void QL_Steamworks_LogServerCallbackDispatch( const char *stage, const char *detail ) {
	const ql_platform_service_table *services;
	const char *provider;
	const char *policy;

	services = QL_GetPlatformServices();
	provider = "Unavailable";
	policy = "compatibility-unavailable";
	if ( services ) {
		provider = services->matchmaking.provider ? services->matchmaking.provider : "Unavailable";
		policy = QL_DescribePlatformFeaturePolicy( &services->matchmaking );
	}

	Com_DPrintf( "Steam server callback dispatch %s via %s [%s]: %s\n",
		stage ? stage : "update",
		provider,
		policy,
		detail ? detail : "no detail" );
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
	if ( !callbackState ) {
		QL_Steamworks_LogServerCallbackDispatch( "servers_connected", "ignored dispatch without callback state" );
		return;
	}

	if ( !callbackState->bindings.onServersConnected ) {
		QL_Steamworks_LogServerCallbackDispatch( "servers_connected", "ignored dispatch without registered callback" );
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
	if ( !callbackState ) {
		QL_Steamworks_LogServerCallbackDispatch( "connect_failure", "ignored dispatch without callback state" );
		return;
	}

	if ( !callbackState->bindings.onConnectFailure ) {
		QL_Steamworks_LogServerCallbackDispatch( "connect_failure", "ignored dispatch without registered callback" );
		return;
	}

	if ( !payload ) {
		QL_Steamworks_LogServerCallbackDispatch( "connect_failure", "ignored dispatch without payload" );
		return;
	}

	raw = (const ql_steam_server_connect_failure_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.result = raw->result;
	event.stillRetrying = qfalse;
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
	if ( !callbackState ) {
		QL_Steamworks_LogServerCallbackDispatch( "disconnected", "ignored dispatch without callback state" );
		return;
	}

	if ( !callbackState->bindings.onServersDisconnected ) {
		QL_Steamworks_LogServerCallbackDispatch( "disconnected", "ignored dispatch without registered callback" );
		return;
	}

	if ( !payload ) {
		QL_Steamworks_LogServerCallbackDispatch( "disconnected", "ignored dispatch without payload" );
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
	if ( !callbackState ) {
		QL_Steamworks_LogServerCallbackDispatch( "validate_auth_ticket_response", "ignored dispatch without callback state" );
		return;
	}

	if ( !callbackState->bindings.onValidateAuthTicketResponse ) {
		QL_Steamworks_LogServerCallbackDispatch( "validate_auth_ticket_response", "ignored dispatch without registered callback" );
		return;
	}

	if ( !payload ) {
		QL_Steamworks_LogServerCallbackDispatch( "validate_auth_ticket_response", "ignored dispatch without payload" );
		return;
	}

	raw = (const ql_steam_validate_auth_ticket_response_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.steamId = QL_Steamworks_CombineIdentityWords( raw->steamIdLow, raw->steamIdHigh );
	event.ownerSteamId = QL_Steamworks_CombineIdentityWords( raw->ownerSteamIdLow, raw->ownerSteamIdHigh );
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
	if ( !callbackState ) {
		QL_Steamworks_LogServerCallbackDispatch( "p2p_session_request", "ignored dispatch without callback state" );
		return;
	}

	if ( !callbackState->bindings.onP2PSessionRequest ) {
		QL_Steamworks_LogServerCallbackDispatch( "p2p_session_request", "ignored dispatch without registered callback" );
		return;
	}

	if ( !payload ) {
		QL_Steamworks_LogServerCallbackDispatch( "p2p_session_request", "ignored dispatch without payload" );
		return;
	}

	raw = (const ql_steam_p2p_session_request_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.remoteId = raw->remoteId;
	callbackState->bindings.onP2PSessionRequest( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchGSStatsReceived
=============
*/
static void QL_Steamworks_DispatchGSStatsReceived( void *context, const void *payload ) {
	ql_steam_server_callback_state_t *callbackState;
	const ql_steam_gs_stats_received_raw_t *raw;
	ql_steam_gs_stats_received_t event;

	callbackState = (ql_steam_server_callback_state_t *)context;
	if ( !callbackState ) {
		QL_Steamworks_LogServerCallbackDispatch( "gs_stats_received", "ignored dispatch without callback state" );
		return;
	}

	if ( !callbackState->bindings.onGSStatsReceived ) {
		QL_Steamworks_LogServerCallbackDispatch( "gs_stats_received", "ignored dispatch without registered callback" );
		return;
	}

	if ( !payload ) {
		QL_Steamworks_LogServerCallbackDispatch( "gs_stats_received", "ignored dispatch without payload" );
		return;
	}

	raw = (const ql_steam_gs_stats_received_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.result = raw->result;
	event.steamId = QL_Steamworks_CombineIdentityWords( raw->steamIdLow, raw->steamIdHigh );
	callbackState->bindings.onGSStatsReceived( callbackState->bindings.context, &event );
}

/*
=============
QL_Steamworks_DispatchGSStatsStored
=============
*/
static void QL_Steamworks_DispatchGSStatsStored( void *context, const void *payload ) {
	ql_steam_server_callback_state_t *callbackState;
	const ql_steam_gs_stats_stored_raw_t *raw;
	ql_steam_gs_stats_stored_t event;

	callbackState = (ql_steam_server_callback_state_t *)context;
	if ( !callbackState ) {
		QL_Steamworks_LogServerCallbackDispatch( "gs_stats_stored", "ignored dispatch without callback state" );
		return;
	}

	if ( !callbackState->bindings.onGSStatsStored ) {
		QL_Steamworks_LogServerCallbackDispatch( "gs_stats_stored", "ignored dispatch without registered callback" );
		return;
	}

	if ( !payload ) {
		QL_Steamworks_LogServerCallbackDispatch( "gs_stats_stored", "ignored dispatch without payload" );
		return;
	}

	raw = (const ql_steam_gs_stats_stored_raw_t *)payload;
	memset( &event, 0, sizeof( event ) );
	event.result = raw->result;
	event.steamId = QL_Steamworks_CombineIdentityWords( raw->steamIdLow, raw->steamIdHigh );
	callbackState->bindings.onGSStatsStored( callbackState->bindings.context, &event );
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
	if ( callbackState->registered || ( callbackState->webApiTicketResponse.callbackFlags & QL_STEAM_CALLBACK_FLAG_REGISTERED ) ) {
		QL_Steamworks_UnregisterClientCallbacks();
	}

	memset( callbackState, 0, sizeof( *callbackState ) );
	memcpy( &callbackState->bindings, bindings, sizeof( callbackState->bindings ) );

	QL_Steamworks_PrepareCallbackObject( &callbackState->richPresenceJoinRequested, QL_STEAM_CALLBACK_RICH_PRESENCE_JOIN_REQUESTED, QL_STEAM_CALLBACK_SIZE_GAME_RICH_PRESENCE_JOIN_REQUESTED, qfalse, callbackState, QL_Steamworks_DispatchRichPresenceJoinRequested, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->userStatsReceived, QL_STEAM_CALLBACK_USER_STATS_RECEIVED, QL_STEAM_CALLBACK_SIZE_USER_STATS_RECEIVED, qfalse, callbackState, QL_Steamworks_DispatchUserStatsReceived, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->personaStateChange, QL_STEAM_CALLBACK_PERSONA_STATE_CHANGE, QL_STEAM_CALLBACK_SIZE_PERSONA_STATE_CHANGE, qfalse, callbackState, QL_Steamworks_DispatchPersonaStateChange, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->p2pSessionRequest, QL_STEAM_CALLBACK_P2P_SESSION_REQUEST, QL_STEAM_CALLBACK_SIZE_P2P_SESSION_REQUEST, qfalse, callbackState, QL_Steamworks_DispatchP2PSessionRequest, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->gameServerChangeRequested, QL_STEAM_CALLBACK_GAME_SERVER_CHANGE_REQUESTED, QL_STEAM_CALLBACK_SIZE_GAME_SERVER_CHANGE_REQUESTED, qfalse, callbackState, QL_Steamworks_DispatchGameServerChangeRequested, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->friendRichPresenceUpdate, QL_STEAM_CALLBACK_FRIEND_RICH_PRESENCE_UPDATE, QL_STEAM_CALLBACK_SIZE_FRIEND_RICH_PRESENCE_UPDATE, qfalse, callbackState, QL_Steamworks_DispatchFriendRichPresenceUpdate, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->ugcQueryCompleted, QL_STEAM_CALLBACK_UGC_QUERY_COMPLETED, QL_STEAM_CALLBACK_SIZE_UGC_QUERY_COMPLETED, qfalse, callbackState, NULL, QL_Steamworks_DispatchUGCQueryCompleted );

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
	QL_Steamworks_UnregisterCallbackObject( &callbackState->webApiTicketResponse );
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
QL_Steamworks_RegisterAvatarCallbacks
=============
*/
qboolean QL_Steamworks_RegisterAvatarCallbacks( const ql_steam_avatar_callback_bindings_t *bindings ) {
	ql_steam_avatar_callback_state_t *callbackState;

	if ( !bindings ) {
		return qfalse;
	}

	if ( !QL_Steamworks_Init() || !state.SteamAPI_RegisterCallback ) {
		return qfalse;
	}

	callbackState = &state.avatarCallbacks;
	if ( callbackState->registered ) {
		QL_Steamworks_UnregisterAvatarCallbacks();
	}

	memset( callbackState, 0, sizeof( *callbackState ) );
	memcpy( &callbackState->bindings, bindings, sizeof( callbackState->bindings ) );

	QL_Steamworks_PrepareCallbackObject( &callbackState->avatarImageLoaded, QL_STEAM_CALLBACK_AVATAR_IMAGE_LOADED, QL_STEAM_CALLBACK_SIZE_AVATAR_IMAGE_LOADED, qfalse, callbackState, QL_Steamworks_DispatchAvatarImageLoaded, NULL );

	if ( !QL_Steamworks_RegisterCallbackObject( &callbackState->avatarImageLoaded ) ) {
		QL_Steamworks_UnregisterAvatarCallbacks();
		return qfalse;
	}

	callbackState->registered = qtrue;
	return qtrue;
}

/*
=============
QL_Steamworks_UnregisterAvatarCallbacks
=============
*/
void QL_Steamworks_UnregisterAvatarCallbacks( void ) {
	ql_steam_avatar_callback_state_t *callbackState;

	callbackState = &state.avatarCallbacks;
	QL_Steamworks_UnregisterCallbackObject( &callbackState->avatarImageLoaded );
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

	QL_Steamworks_PrepareCallbackObject( &callbackState->serversConnected, QL_STEAM_CALLBACK_STEAM_SERVERS_CONNECTED, QL_STEAM_CALLBACK_SIZE_SERVERS_CONNECTED, qtrue, callbackState, QL_Steamworks_DispatchServersConnected, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->connectFailure, QL_STEAM_CALLBACK_STEAM_SERVER_CONNECT_FAILURE, QL_STEAM_CALLBACK_SIZE_SERVER_CONNECT_FAILURE, qtrue, callbackState, QL_Steamworks_DispatchServerConnectFailure, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->serversDisconnected, QL_STEAM_CALLBACK_STEAM_SERVERS_DISCONNECTED, QL_STEAM_CALLBACK_SIZE_SERVERS_DISCONNECTED, qtrue, callbackState, QL_Steamworks_DispatchServersDisconnected, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->validateAuthTicketResponse, QL_STEAM_CALLBACK_VALIDATE_AUTH_TICKET_RESPONSE, QL_STEAM_CALLBACK_SIZE_VALIDATE_AUTH_TICKET_RESPONSE, qtrue, callbackState, QL_Steamworks_DispatchValidateAuthTicketResponse, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->p2pSessionRequest, QL_STEAM_CALLBACK_P2P_SESSION_REQUEST, QL_STEAM_CALLBACK_SIZE_P2P_SESSION_REQUEST, qtrue, callbackState, QL_Steamworks_DispatchServerP2PSessionRequest, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->gsStatsReceived, QL_STEAM_CALLBACK_GS_STATS_RECEIVED, QL_STEAM_CALLBACK_SIZE_GS_STATS_RECEIVED, qtrue, callbackState, QL_Steamworks_DispatchGSStatsReceived, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->gsStatsStored, QL_STEAM_CALLBACK_GS_STATS_STORED, QL_STEAM_CALLBACK_SIZE_GS_STATS_STORED, qtrue, callbackState, QL_Steamworks_DispatchGSStatsStored, NULL );

	if ( !QL_Steamworks_RegisterCallbackObject( &callbackState->serversConnected ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->connectFailure ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->serversDisconnected ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->validateAuthTicketResponse ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->p2pSessionRequest ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->gsStatsReceived ) ||
		!QL_Steamworks_RegisterCallbackObject( &callbackState->gsStatsStored ) ) {
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
	QL_Steamworks_UnregisterCallbackObject( &callbackState->gsStatsStored );
	QL_Steamworks_UnregisterCallbackObject( &callbackState->gsStatsReceived );
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

	QL_Steamworks_PrepareCallbackObject( &callbackState->lobbyCreated, QL_STEAM_CALLBACK_LOBBY_CREATED, QL_STEAM_CALLBACK_SIZE_LOBBY_CREATED, qfalse, callbackState, QL_Steamworks_DispatchLobbyCreated, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->lobbyEnter, QL_STEAM_CALLBACK_LOBBY_ENTER, QL_STEAM_CALLBACK_SIZE_LOBBY_ENTER, qfalse, callbackState, QL_Steamworks_DispatchLobbyEnter, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->lobbyChatUpdate, QL_STEAM_CALLBACK_LOBBY_CHAT_UPDATE, QL_STEAM_CALLBACK_SIZE_LOBBY_CHAT_UPDATE, qfalse, callbackState, QL_Steamworks_DispatchLobbyChatUpdate, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->lobbyChatMessage, QL_STEAM_CALLBACK_LOBBY_CHAT_MESSAGE, QL_STEAM_CALLBACK_SIZE_LOBBY_CHAT_MESSAGE, qfalse, callbackState, QL_Steamworks_DispatchLobbyChatMessage, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->lobbyDataUpdate, QL_STEAM_CALLBACK_LOBBY_DATA_UPDATE, QL_STEAM_CALLBACK_SIZE_LOBBY_DATA_UPDATE, qfalse, callbackState, QL_Steamworks_DispatchLobbyDataUpdate, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->lobbyGameCreated, QL_STEAM_CALLBACK_LOBBY_GAME_CREATED, QL_STEAM_CALLBACK_SIZE_LOBBY_GAME_CREATED, qfalse, callbackState, QL_Steamworks_DispatchLobbyGameCreated, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->lobbyKicked, QL_STEAM_CALLBACK_LOBBY_KICKED, QL_STEAM_CALLBACK_SIZE_LOBBY_KICKED, qfalse, callbackState, QL_Steamworks_DispatchLobbyKicked, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->gameLobbyJoinRequested, QL_STEAM_CALLBACK_GAME_LOBBY_JOIN_REQUESTED, QL_STEAM_CALLBACK_SIZE_GAME_LOBBY_JOIN_REQUESTED, qfalse, callbackState, QL_Steamworks_DispatchGameLobbyJoinRequested, NULL );

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
	QL_Steamworks_PrepareCallbackObject( &callbackState->authorizationResponse, QL_STEAM_CALLBACK_MICROTXN_AUTHORIZATION_RESPONSE, QL_STEAM_CALLBACK_SIZE_MICROTXN_AUTHORIZATION_RESPONSE, qfalse, callbackState, QL_Steamworks_DispatchMicroAuthorizationResponse, NULL );
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
	QL_Steamworks_PrepareCallbackObject( &callbackState->itemInstalled, QL_STEAM_CALLBACK_ITEM_INSTALLED, QL_STEAM_CALLBACK_SIZE_ITEM_INSTALLED, qfalse, callbackState, QL_Steamworks_DispatchItemInstalled, NULL );
	QL_Steamworks_PrepareCallbackObject( &callbackState->downloadItemResult, QL_STEAM_CALLBACK_DOWNLOAD_ITEM_RESULT, QL_STEAM_CALLBACK_SIZE_DOWNLOAD_ITEM_RESULT, qfalse, callbackState, QL_Steamworks_DispatchDownloadItemResult, NULL );
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
	callbackState->ugcQueryCompleted.callResultHandleLow = QL_Steamworks_CallHandleLow( callHandle );
	callbackState->ugcQueryCompleted.callResultHandleHigh = QL_Steamworks_CallHandleHigh( callHandle );
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

	fn = (QL_SteamFriends_SetRichPresenceFn)vtable[QL_STEAM_FRIENDS_SET_RICH_PRESENCE_SLOT];
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

	if ( !dialog ) {
		return qfalse;
	}

	friends = QL_Steamworks_GetFriendsInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( friends );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamFriends_ActivateGameOverlayToUserFn)vtable[QL_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_TO_USER_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( friends, NULL, dialog, QL_Steamworks_CombineIdentityWords( idLow, idHigh ) );
	return qtrue;
}

/*
=============
QL_Steamworks_ActivateOverlayToWebPage
=============
*/
qboolean QL_Steamworks_ActivateOverlayToWebPage( const char *url ) {
	void *friends;
	void **vtable;
	typedef void (__fastcall *QL_SteamFriends_ActivateGameOverlayToWebPageFn)( void *self, void *unused, const char *url );
	QL_SteamFriends_ActivateGameOverlayToWebPageFn fn;

	if ( !url ) {
		return qfalse;
	}

	friends = QL_Steamworks_GetFriendsInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( friends );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamFriends_ActivateGameOverlayToWebPageFn)vtable[QL_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_TO_WEB_PAGE_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( friends, NULL, url );
	return qtrue;
}

/*
=============
QL_Steamworks_HasServerBrowserInterface
=============
*/
qboolean QL_Steamworks_HasServerBrowserInterface( void ) {
	return QL_Steamworks_GetServerBrowserInterface() != NULL ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetServerBrowserAdapterLabel
=============
*/
const char *QL_Steamworks_GetServerBrowserAdapterLabel( void ) {
	return "ISteamMatchmakingServers";
}

/*
=============
QL_Steamworks_GetServerBrowserIntegrationGapLabel
=============
*/
const char *QL_Steamworks_GetServerBrowserIntegrationGapLabel( void ) {
	return "native request handle unavailable; source-browser fallback retained";
}

/*
=============
QL_Steamworks_GetServerBrowserRequestModeLabel
=============
*/
const char *QL_Steamworks_GetServerBrowserRequestModeLabel( ql_steam_server_browser_request_mode_t requestMode ) {
	switch ( requestMode ) {
		case QL_STEAM_SERVER_BROWSER_LAN:
			return "lan";
		case QL_STEAM_SERVER_BROWSER_FRIENDS:
			return "friends";
		case QL_STEAM_SERVER_BROWSER_FAVORITES:
			return "favorites";
		case QL_STEAM_SERVER_BROWSER_HISTORY:
			return "history";
		case QL_STEAM_SERVER_BROWSER_INTERNET:
		default:
			return "internet";
	}
}

/*
=============
QL_Steamworks_ServerBrowserRequestModeUsesGamedirFilter

Matches the retained JSBrowser_RequestServers filter contract.
=============
*/
qboolean QL_Steamworks_ServerBrowserRequestModeUsesGamedirFilter( ql_steam_server_browser_request_mode_t requestMode ) {
	return requestMode == QL_STEAM_SERVER_BROWSER_LAN ? qfalse : qtrue;
}

/*
=============
QL_Steamworks_InitServerBrowserOwner

Initialises the retained JSBrowser request owner state.
=============
*/
void QL_Steamworks_InitServerBrowserOwner( ql_steam_server_browser_owner_t *owner ) {
	if ( owner ) {
		memset( owner, 0, sizeof( *owner ) );
	}
}

/*
=============
QL_Steamworks_BeginServerBrowserOwnerRequest

Starts one native server-browser owner request when the retained owner is idle.
=============
*/
qboolean QL_Steamworks_BeginServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner, ql_steam_server_browser_request_mode_t requestMode, void *responseObject ) {
	return QL_Steamworks_BeginServerBrowserOwnerRequestForApp( owner, requestMode, QL_Steamworks_GetAppID(), responseObject );
}

/*
=============
QL_Steamworks_BeginServerBrowserOwnerRequestForApp

Starts one native server-browser owner request for the supplied Steam app id
when the retained owner is idle.
=============
*/
qboolean QL_Steamworks_BeginServerBrowserOwnerRequestForApp( ql_steam_server_browser_owner_t *owner, ql_steam_server_browser_request_mode_t requestMode, uint32_t appId, void *responseObject ) {
	ql_steam_server_list_request_t request;

	if ( !owner || !responseObject ) {
		return qfalse;
	}
	if ( owner->refreshActive ) {
		return qfalse;
	}
	if ( owner->request ) {
		QL_Steamworks_ReleaseServerListRequest( owner->request );
		owner->request = NULL;
	}
	if ( appId == 0u ) {
		owner->refreshActive = qfalse;
		return qfalse;
	}

	request = QL_Steamworks_RequestServerListForApp( requestMode, appId, responseObject );
	if ( !request ) {
		owner->refreshActive = qfalse;
		owner->request = NULL;
		return qfalse;
	}

	owner->refreshActive = qtrue;
	owner->request = request;
	return qtrue;
}

/*
=============
QL_Steamworks_RefreshServerBrowserOwnerRequest

Refreshes the retained JSBrowser request handle when one is live.
=============
*/
qboolean QL_Steamworks_RefreshServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner ) {
	if ( !owner || !owner->request ) {
		return qfalse;
	}

	QL_Steamworks_RefreshServerListRequest( owner->request );
	return qtrue;
}

/*
=============
QL_Steamworks_CompleteServerBrowserOwnerRequest

Marks the retained JSBrowser owner idle after the refresh-complete callback.
=============
*/
qboolean QL_Steamworks_CompleteServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner ) {
	if ( !owner ) {
		return qfalse;
	}

	if ( !owner->refreshActive ) {
		return qfalse;
	}

	owner->refreshActive = qfalse;
	return qtrue;
}

/*
=============
QL_Steamworks_PrepareServerBrowserGamedirFilter

Builds the retail browser filter pair used by JSBrowser_RequestServers.
=============
*/
static void QL_Steamworks_PrepareServerBrowserGamedirFilter( ql_steam_matchmaking_key_value_pair_t *filter, ql_steam_matchmaking_key_value_pair_t **filterPtr ) {
	if ( !filter || !filterPtr ) {
		return;
	}

	memset( filter, 0, sizeof( *filter ) );
	Q_strncpyz( filter->key, "gamedir", sizeof( filter->key ) );
	Q_strncpyz( filter->value, QL_BASEGAME, sizeof( filter->value ) );
	*filterPtr = filter;
}

/*
=============
QL_Steamworks_RequestServerList

Issues the retained JSBrowser SteamMatchmakingServers list request.
=============
*/
ql_steam_server_list_request_t QL_Steamworks_RequestServerList( ql_steam_server_browser_request_mode_t requestMode, void *responseObject ) {
	return QL_Steamworks_RequestServerListForApp( requestMode, QL_Steamworks_GetAppID(), responseObject );
}

/*
=============
QL_Steamworks_RequestServerListForApp

Issues the retained JSBrowser SteamMatchmakingServers list request for a
specific Steam app id.
=============
*/
ql_steam_server_list_request_t QL_Steamworks_RequestServerListForApp( ql_steam_server_browser_request_mode_t requestMode, uint32_t appId, void *responseObject ) {
	void *serverBrowser;
	void **vtable;
	ql_steam_matchmaking_key_value_pair_t filter;
	ql_steam_matchmaking_key_value_pair_t *filterPtr;
	typedef ql_steam_server_list_request_t (__fastcall *QL_SteamMatchmakingServers_RequestFilteredListFn)( void *self, void *unused, uint32_t appId, ql_steam_matchmaking_key_value_pair_t **filters, uint32_t filterCount, void *responseObject );
	typedef ql_steam_server_list_request_t (__fastcall *QL_SteamMatchmakingServers_RequestLANListFn)( void *self, void *unused, uint32_t appId, void *responseObject );
	QL_SteamMatchmakingServers_RequestFilteredListFn filteredFn;
	QL_SteamMatchmakingServers_RequestLANListFn lanFn;

	if ( !responseObject ) {
		return NULL;
	}

	serverBrowser = QL_Steamworks_GetServerBrowserInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( serverBrowser );
	if ( !vtable ) {
		return NULL;
	}

	if ( appId == 0u ) {
		return NULL;
	}

	filterPtr = NULL;
	if ( QL_Steamworks_ServerBrowserRequestModeUsesGamedirFilter( requestMode ) ) {
		QL_Steamworks_PrepareServerBrowserGamedirFilter( &filter, &filterPtr );
	}

	switch ( requestMode ) {
		case QL_STEAM_SERVER_BROWSER_LAN:
			lanFn = (QL_SteamMatchmakingServers_RequestLANListFn)vtable[QL_STEAM_MATCHMAKING_SERVERS_REQUEST_LAN_SERVER_LIST_SLOT];
			if ( !lanFn ) {
				return NULL;
			}
			return lanFn( serverBrowser, NULL, appId, responseObject );
		case QL_STEAM_SERVER_BROWSER_FRIENDS:
			filteredFn = (QL_SteamMatchmakingServers_RequestFilteredListFn)vtable[QL_STEAM_MATCHMAKING_SERVERS_REQUEST_FRIENDS_SERVER_LIST_SLOT];
			break;
		case QL_STEAM_SERVER_BROWSER_FAVORITES:
			filteredFn = (QL_SteamMatchmakingServers_RequestFilteredListFn)vtable[QL_STEAM_MATCHMAKING_SERVERS_REQUEST_FAVORITES_SERVER_LIST_SLOT];
			break;
		case QL_STEAM_SERVER_BROWSER_HISTORY:
			filteredFn = (QL_SteamMatchmakingServers_RequestFilteredListFn)vtable[QL_STEAM_MATCHMAKING_SERVERS_REQUEST_HISTORY_SERVER_LIST_SLOT];
			break;
		case QL_STEAM_SERVER_BROWSER_INTERNET:
		default:
			filteredFn = (QL_SteamMatchmakingServers_RequestFilteredListFn)vtable[QL_STEAM_MATCHMAKING_SERVERS_REQUEST_INTERNET_SERVER_LIST_SLOT];
			break;
	}

	if ( !filteredFn || !filterPtr ) {
		return NULL;
	}

	return filteredFn( serverBrowser, NULL, appId, &filterPtr, 1u, responseObject );
}

/*
=============
QL_Steamworks_GetServerListDetails

Returns the Steam server-list row pointer for one browser response index.
=============
*/
const void *QL_Steamworks_GetServerListDetails( ql_steam_server_list_request_t request, int index ) {
	void *serverBrowser;
	void **vtable;
	typedef const void *(__fastcall *QL_SteamMatchmakingServers_GetServerDetailsFn)( void *self, void *unused, ql_steam_server_list_request_t request, int index );
	QL_SteamMatchmakingServers_GetServerDetailsFn fn;

	if ( !request || index < 0 ) {
		return NULL;
	}

	serverBrowser = QL_Steamworks_GetServerBrowserInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( serverBrowser );
	if ( !vtable ) {
		return NULL;
	}

	fn = (QL_SteamMatchmakingServers_GetServerDetailsFn)vtable[QL_STEAM_MATCHMAKING_SERVERS_GET_SERVER_DETAILS_SLOT];
	if ( !fn ) {
		return NULL;
	}

	return fn( serverBrowser, NULL, request, index );
}

/*
=============
QL_Steamworks_ReadServerListDetails

Reads and validates one retained Steam server-browser row.
=============
*/
qboolean QL_Steamworks_ReadServerListDetails( ql_steam_server_list_request_t request, int index, ql_steam_server_item_t *outServer ) {
	return QL_Steamworks_ReadServerListDetailsForApp( request, index, QL_Steamworks_GetAppID(), outServer );
}

/*
=============
QL_Steamworks_ReadServerListDetailsForApp

Reads and validates one retained Steam server-browser row for the supplied
Steam app id.
=============
*/
qboolean QL_Steamworks_ReadServerListDetailsForApp( ql_steam_server_list_request_t request, int index, uint32_t appId, ql_steam_server_item_t *outServer ) {
	const ql_steam_gameserveritem_raw_t *raw;

	if ( outServer ) {
		memset( outServer, 0, sizeof( *outServer ) );
	}
	if ( !outServer ) {
		return qfalse;
	}

	raw = (const ql_steam_gameserveritem_raw_t *)QL_Steamworks_GetServerListDetails( request, index );
	if ( !raw ) {
		return qfalse;
	}

	if ( !QL_Steamworks_ServerBrowserAppIdsCompatible( raw->appId, appId ) ) {
		return qfalse;
	}

	QL_Steamworks_CopyServerListDetails( outServer, raw );
	return qtrue;
}

/*
=============
QL_Steamworks_FormatServerBrowserResponseId

Builds the retained JSBrowser_OnServerResponded id/event suffix.
=============
*/
void QL_Steamworks_FormatServerBrowserResponseId( uint32_t serverIp, uint16_t serverPort, char *buffer, size_t bufferSize ) {
	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	Com_sprintf( buffer, bufferSize, "%u_%u", (unsigned int)serverIp, (unsigned int)serverPort );
}

/*
=============
QL_Steamworks_BuildServerBrowserResponse

Builds the retained browser-facing server response projection.
=============
*/
qboolean QL_Steamworks_BuildServerBrowserResponse( const ql_steam_server_item_t *server, ql_steam_server_browser_response_t *outResponse ) {
	if ( outResponse ) {
		memset( outResponse, 0, sizeof( *outResponse ) );
	}
	if ( !server || !outResponse ) {
		return qfalse;
	}

	QL_Steamworks_CopyServerBrowserResponse( outResponse, server );
	return qtrue;
}

/*
=============
QL_Steamworks_ReadServerBrowserResponse

Reads a row and projects it into the retained JSBrowser response shape.
=============
*/
qboolean QL_Steamworks_ReadServerBrowserResponse( ql_steam_server_list_request_t request, int index, ql_steam_server_browser_response_t *outResponse ) {
	return QL_Steamworks_ReadServerBrowserResponseForApp( request, index, QL_Steamworks_GetAppID(), outResponse );
}

/*
=============
QL_Steamworks_ReadServerBrowserResponseForApp

Reads a row for the supplied Steam app id and projects it into the retained
JSBrowser response shape.
=============
*/
qboolean QL_Steamworks_ReadServerBrowserResponseForApp( ql_steam_server_list_request_t request, int index, uint32_t appId, ql_steam_server_browser_response_t *outResponse ) {
	ql_steam_server_item_t server;

	if ( outResponse ) {
		memset( outResponse, 0, sizeof( *outResponse ) );
	}
	if ( !outResponse ) {
		return qfalse;
	}
	if ( !QL_Steamworks_ReadServerListDetailsForApp( request, index, appId, &server ) ) {
		return qfalse;
	}

	QL_Steamworks_CopyServerBrowserResponse( outResponse, &server );
	return qtrue;
}

/*
=============
QL_Steamworks_ReadServerBrowserPingResponse

Projects the raw gameserveritem_t payload delivered by PingServer into the
retained JSBrowserDetails server response shape.
=============
*/
qboolean QL_Steamworks_ReadServerBrowserPingResponse( const void *serverDetails, ql_steam_server_browser_response_t *outResponse ) {
	return QL_Steamworks_ReadServerBrowserPingResponseForApp( serverDetails, QL_Steamworks_GetAppID(), outResponse );
}

/*
=============
QL_Steamworks_ReadServerBrowserPingResponseForApp

Projects the raw gameserveritem_t payload delivered by PingServer into the
retained JSBrowserDetails server response shape for the supplied Steam app id.
=============
*/
qboolean QL_Steamworks_ReadServerBrowserPingResponseForApp( const void *serverDetails, uint32_t appId, ql_steam_server_browser_response_t *outResponse ) {
	const ql_steam_gameserveritem_raw_t *raw;
	ql_steam_server_item_t server;

	if ( outResponse ) {
		memset( outResponse, 0, sizeof( *outResponse ) );
	}
	if ( !serverDetails || !outResponse ) {
		return qfalse;
	}

	raw = (const ql_steam_gameserveritem_raw_t *)serverDetails;
	if ( !QL_Steamworks_ServerBrowserAppIdsCompatible( raw->appId, appId ) ) {
		return qfalse;
	}

	QL_Steamworks_CopyServerListDetails( &server, raw );
	QL_Steamworks_CopyServerBrowserResponse( outResponse, &server );
	return qtrue;
}

/*
=============
QL_Steamworks_FormatServerBrowserFailureEventName

Builds the retained JSBrowser_OnServerFailedToRespond event name.
=============
*/
void QL_Steamworks_FormatServerBrowserFailureEventName( int serverIndex, char *buffer, size_t bufferSize ) {
	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	Com_sprintf( buffer, bufferSize, "servers.details.%i.failed", serverIndex );
}

/*
=============
QL_Steamworks_BuildServerBrowserFailure

Builds the retained browser-facing failed-row projection.
=============
*/
qboolean QL_Steamworks_BuildServerBrowserFailure( int serverIndex, ql_steam_server_browser_failure_t *outFailure ) {
	if ( outFailure ) {
		memset( outFailure, 0, sizeof( *outFailure ) );
	}
	if ( !outFailure ) {
		return qfalse;
	}

	outFailure->id = serverIndex;
	QL_Steamworks_FormatServerBrowserFailureEventName( serverIndex, outFailure->eventName, sizeof( outFailure->eventName ) );
	return qtrue;
}

/*
=============
QL_Steamworks_BuildServerBrowserRefreshComplete

Builds the retained browser-facing refresh-complete projection.
=============
*/
qboolean QL_Steamworks_BuildServerBrowserRefreshComplete( ql_steam_server_browser_refresh_complete_t *outRefresh ) {
	if ( outRefresh ) {
		memset( outRefresh, 0, sizeof( *outRefresh ) );
	}
	if ( !outRefresh ) {
		return qfalse;
	}

	Q_strncpyz( outRefresh->eventName, "servers.refresh.end", sizeof( outRefresh->eventName ) );
	return qtrue;
}

/*
=============
QL_Steamworks_GetServerBrowserDetailChannelLabel

Returns the retained JSBrowserDetails event-family label.
=============
*/
static const char *QL_Steamworks_GetServerBrowserDetailChannelLabel( ql_steam_server_browser_detail_channel_t channel ) {
	switch ( channel ) {
	case QL_STEAM_SERVER_BROWSER_DETAIL_RULES:
		return "rules";
	case QL_STEAM_SERVER_BROWSER_DETAIL_PLAYERS:
		return "players";
	default:
		return NULL;
	}
}

/*
=============
QL_Steamworks_GetServerBrowserDetailPhaseLabel

Returns the retained JSBrowserDetails event-phase label.
=============
*/
static const char *QL_Steamworks_GetServerBrowserDetailPhaseLabel( ql_steam_server_browser_detail_phase_t phase ) {
	switch ( phase ) {
	case QL_STEAM_SERVER_BROWSER_DETAIL_RESPONSE:
		return "response";
	case QL_STEAM_SERVER_BROWSER_DETAIL_FAILED:
		return "failed";
	case QL_STEAM_SERVER_BROWSER_DETAIL_END:
		return "end";
	default:
		return NULL;
	}
}

/*
=============
QL_Steamworks_FormatServerBrowserDetailId

Builds the retained JSBrowserDetails "%u_%i" server identity suffix.
=============
*/
void QL_Steamworks_FormatServerBrowserDetailId( uint32_t serverIp, uint16_t serverPort, char *buffer, size_t bufferSize ) {
	int signedPort;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	signedPort = ( serverPort & 0x8000u ) ? (int)serverPort - 0x10000 : (int)serverPort;
	Com_sprintf( buffer, bufferSize, "%u_%i", (unsigned int)serverIp, signedPort );
}

/*
=============
QL_Steamworks_BuildServerBrowserDetailIdentity

Builds the retained JSBrowserDetails server identity record.
=============
*/
qboolean QL_Steamworks_BuildServerBrowserDetailIdentity( uint32_t serverIp, uint16_t serverPort, ql_steam_server_browser_detail_identity_t *outIdentity ) {
	if ( outIdentity ) {
		memset( outIdentity, 0, sizeof( *outIdentity ) );
	}
	if ( serverIp == 0u || serverPort == 0 || !outIdentity ) {
		return qfalse;
	}

	outIdentity->serverIp = serverIp;
	outIdentity->serverPort = serverPort;
	QL_Steamworks_FormatServerBrowserDetailId( serverIp, serverPort, outIdentity->id, sizeof( outIdentity->id ) );
	return qtrue;
}

/*
=============
QL_Steamworks_FormatServerBrowserDetailEventName

Builds a retained JSBrowserDetails rules/players response, failed, or end event name.
=============
*/
qboolean QL_Steamworks_FormatServerBrowserDetailEventName( ql_steam_server_browser_detail_channel_t channel, ql_steam_server_browser_detail_phase_t phase, const char *detailId, char *buffer, size_t bufferSize ) {
	const char *channelLabel;
	const char *phaseLabel;

	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
	if ( !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	channelLabel = QL_Steamworks_GetServerBrowserDetailChannelLabel( channel );
	phaseLabel = QL_Steamworks_GetServerBrowserDetailPhaseLabel( phase );
	if ( !channelLabel || !phaseLabel ) {
		return qfalse;
	}

	Com_sprintf( buffer, bufferSize, "servers.%s.%s.%s", channelLabel, detailId ? detailId : "", phaseLabel );
	return qtrue;
}

/*
=============
QL_Steamworks_BuildServerBrowserDetailEvent

Builds the retained JSBrowserDetails event identity projection.
=============
*/
qboolean QL_Steamworks_BuildServerBrowserDetailEvent( const ql_steam_server_browser_detail_identity_t *identity, ql_steam_server_browser_detail_channel_t channel, ql_steam_server_browser_detail_phase_t phase, ql_steam_server_browser_detail_event_t *outEvent ) {
	ql_steam_server_browser_detail_event_t event;

	if ( outEvent ) {
		memset( outEvent, 0, sizeof( *outEvent ) );
	}
	if ( !identity || !identity->id[0] || !outEvent ) {
		return qfalse;
	}

	memset( &event, 0, sizeof( event ) );
	event.identity = *identity;
	if ( !QL_Steamworks_FormatServerBrowserDetailEventName( channel, phase, identity->id, event.eventName, sizeof( event.eventName ) ) ) {
		return qfalse;
	}

	*outEvent = event;
	return qtrue;
}

/*
=============
QL_Steamworks_BuildServerBrowserRuleResponse

Builds the retained JSBrowserDetails rules response payload projection.
=============
*/
qboolean QL_Steamworks_BuildServerBrowserRuleResponse( const ql_steam_server_browser_detail_identity_t *identity, const char *rule, const char *value, ql_steam_server_browser_rule_response_t *outResponse ) {
	ql_steam_server_browser_detail_event_t event;

	if ( outResponse ) {
		memset( outResponse, 0, sizeof( *outResponse ) );
	}
	if ( !outResponse ) {
		return qfalse;
	}
	if ( !QL_Steamworks_BuildServerBrowserDetailEvent( identity, QL_STEAM_SERVER_BROWSER_DETAIL_RULES, QL_STEAM_SERVER_BROWSER_DETAIL_RESPONSE, &event ) ) {
		return qfalse;
	}

	outResponse->identity = event.identity;
	Q_strncpyz( outResponse->eventName, event.eventName, sizeof( outResponse->eventName ) );
	Q_strncpyz( outResponse->rule, rule ? rule : "", sizeof( outResponse->rule ) );
	Q_strncpyz( outResponse->value, value ? value : "", sizeof( outResponse->value ) );
	return qtrue;
}

/*
=============
QL_Steamworks_BuildServerBrowserPlayerResponse

Builds the retained JSBrowserDetails player response payload projection.
=============
*/
qboolean QL_Steamworks_BuildServerBrowserPlayerResponse( const ql_steam_server_browser_detail_identity_t *identity, const char *name, int score, int time, ql_steam_server_browser_player_response_t *outResponse ) {
	ql_steam_server_browser_detail_event_t event;

	if ( outResponse ) {
		memset( outResponse, 0, sizeof( *outResponse ) );
	}
	if ( !outResponse ) {
		return qfalse;
	}
	if ( !QL_Steamworks_BuildServerBrowserDetailEvent( identity, QL_STEAM_SERVER_BROWSER_DETAIL_PLAYERS, QL_STEAM_SERVER_BROWSER_DETAIL_RESPONSE, &event ) ) {
		return qfalse;
	}

	outResponse->identity = event.identity;
	Q_strncpyz( outResponse->eventName, event.eventName, sizeof( outResponse->eventName ) );
	Q_strncpyz( outResponse->name, name ? name : "", sizeof( outResponse->name ) );
	outResponse->score = score;
	outResponse->time = time;
	return qtrue;
}

/*
=============
QL_Steamworks_InitServerBrowserDetailLifecycle

Initialises the retained JSBrowserDetails shared completion counter.
=============
*/
qboolean QL_Steamworks_InitServerBrowserDetailLifecycle( uint32_t serverIp, uint16_t serverPort, ql_steam_server_browser_detail_lifecycle_t *outLifecycle ) {
	ql_steam_server_browser_detail_identity_t identity;

	if ( outLifecycle ) {
		memset( outLifecycle, 0, sizeof( *outLifecycle ) );
	}
	if ( !outLifecycle ) {
		return qfalse;
	}
	if ( !QL_Steamworks_BuildServerBrowserDetailIdentity( serverIp, serverPort, &identity ) ) {
		return qfalse;
	}

	outLifecycle->identity = identity;
	outLifecycle->completedCallbacks = 0;
	outLifecycle->completedTerminalChannels = 0u;
	outLifecycle->releaseReady = qfalse;
	return qtrue;
}

/*
=============
QL_Steamworks_CountServerBrowserDetailTerminalChannels

Counts completed native JSBrowserDetails terminal channels.
=============
*/
static int QL_Steamworks_CountServerBrowserDetailTerminalChannels( uint32_t terminalChannels ) {
	int count;

	count = 0;
	if ( terminalChannels & QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PING ) {
		count++;
	}
	if ( terminalChannels & QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_RULES ) {
		count++;
	}
	if ( terminalChannels & QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PLAYERS ) {
		count++;
	}

	return count;
}

/*
=============
QL_Steamworks_IsServerBrowserDetailTerminalChannel

Returns qtrue for exactly one native JSBrowserDetails terminal channel.
=============
*/
static qboolean QL_Steamworks_IsServerBrowserDetailTerminalChannel( uint32_t terminalChannel ) {
	switch ( terminalChannel ) {
	case QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PING:
	case QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_RULES:
	case QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PLAYERS:
		return qtrue;
	default:
		return qfalse;
	}
}

/*
=============
QL_Steamworks_NextServerBrowserDetailTerminalChannel

Maps the legacy sequential completion API to the next terminal channel.
=============
*/
static uint32_t QL_Steamworks_NextServerBrowserDetailTerminalChannel( const ql_steam_server_browser_detail_lifecycle_t *lifecycle ) {
	if ( !lifecycle || !( lifecycle->completedTerminalChannels & QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PING ) ) {
		return QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PING;
	}
	if ( !( lifecycle->completedTerminalChannels & QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_RULES ) ) {
		return QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_RULES;
	}
	return QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PLAYERS;
}

/*
=============
QL_Steamworks_CompleteServerBrowserDetailTerminal

Advances one unique JSBrowserDetails terminal channel.
=============
*/
qboolean QL_Steamworks_CompleteServerBrowserDetailTerminal( ql_steam_server_browser_detail_lifecycle_t *lifecycle, uint32_t terminalChannel, qboolean *outReleaseReady ) {
	if ( outReleaseReady ) {
		*outReleaseReady = qfalse;
	}
	if ( !lifecycle || !lifecycle->identity.id[0] ) {
		return qfalse;
	}
	if ( lifecycle->releaseReady ) {
		if ( outReleaseReady ) {
			*outReleaseReady = qtrue;
		}
		return qfalse;
	}
	if ( !QL_Steamworks_IsServerBrowserDetailTerminalChannel( terminalChannel ) ) {
		return qfalse;
	}
	if ( lifecycle->completedTerminalChannels & terminalChannel ) {
		return qfalse;
	}

	lifecycle->completedTerminalChannels |= terminalChannel;
	lifecycle->completedCallbacks = QL_Steamworks_CountServerBrowserDetailTerminalChannels( lifecycle->completedTerminalChannels );
	if ( ( lifecycle->completedTerminalChannels & QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_ALL ) == QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_ALL ) {
		lifecycle->completedCallbacks = QL_STEAM_SERVER_BROWSER_DETAIL_COMPLETION_TARGET;
		lifecycle->releaseReady = qtrue;
	}

	if ( outReleaseReady ) {
		*outReleaseReady = lifecycle->releaseReady;
	}
	return qtrue;
}

/*
=============
QL_Steamworks_CompleteServerBrowserDetailCallback

Advances the retained JSBrowserDetails shared completion counter in legacy
ping, rules, then players order.
=============
*/
qboolean QL_Steamworks_CompleteServerBrowserDetailCallback( ql_steam_server_browser_detail_lifecycle_t *lifecycle, qboolean *outReleaseReady ) {
	return QL_Steamworks_CompleteServerBrowserDetailTerminal(
		lifecycle,
		QL_Steamworks_NextServerBrowserDetailTerminalChannel( lifecycle ),
		outReleaseReady );
}

/*
=============
QL_Steamworks_BuildServerBrowserDetailResponseViews

Builds the retained JSBrowserDetails callback views from the base object.
=============
*/
qboolean QL_Steamworks_BuildServerBrowserDetailResponseViews( void *detailObjectBase, ql_steam_server_browser_detail_response_views_t *outViews ) {
	unsigned char *base;

	if ( outViews ) {
		memset( outViews, 0, sizeof( *outViews ) );
	}
	if ( !detailObjectBase || !outViews ) {
		return qfalse;
	}

	base = (unsigned char *)detailObjectBase;
	outViews->rulesResponse = base + QL_STEAM_SERVER_BROWSER_DETAIL_RULES_RESPONSE_OFFSET;
	outViews->playersResponse = base + QL_STEAM_SERVER_BROWSER_DETAIL_PLAYERS_RESPONSE_OFFSET;
	outViews->pingResponse = base + QL_STEAM_SERVER_BROWSER_DETAIL_PING_RESPONSE_OFFSET;
	return qtrue;
}

/*
=============
QL_Steamworks_InitServerBrowserDetailRequest

Initialises the native wrapper state for one JSBrowserDetails request.
=============
*/
void QL_Steamworks_InitServerBrowserDetailRequest( ql_steam_server_browser_detail_request_t *request ) {
	if ( request ) {
		memset( request, 0, sizeof( *request ) );
	}
}

/*
=============
QL_Steamworks_BeginServerBrowserDetailRequest

Starts the retained JSBrowserDetails ping, rules, and players request bundle.
=============
*/
qboolean QL_Steamworks_BeginServerBrowserDetailRequest( ql_steam_server_browser_detail_request_t *request, uint32_t serverIp, uint16_t serverPort, void *detailObjectBase ) {
	ql_steam_server_browser_detail_lifecycle_t lifecycle;
	ql_steam_server_browser_detail_response_views_t views;
	ql_steam_server_query_t pingQuery;
	ql_steam_server_query_t playersQuery;
	ql_steam_server_query_t rulesQuery;

	if ( !request ) {
		return qfalse;
	}
	if ( request->queriesActive ) {
		return qfalse;
	}

	QL_Steamworks_InitServerBrowserDetailRequest( request );

	if ( !QL_Steamworks_InitServerBrowserDetailLifecycle( serverIp, serverPort, &lifecycle ) ) {
		return qfalse;
	}
	if ( !QL_Steamworks_BuildServerBrowserDetailResponseViews( detailObjectBase, &views ) ) {
		return qfalse;
	}
	if ( !QL_Steamworks_RequestServerDetails( serverIp, serverPort, views.pingResponse, views.playersResponse, views.rulesResponse, &pingQuery, &playersQuery, &rulesQuery ) ) {
		QL_Steamworks_InitServerBrowserDetailRequest( request );
		return qfalse;
	}

	request->lifecycle = lifecycle;
	request->detailObjectBase = detailObjectBase;
	request->pingQuery = pingQuery;
	request->playersQuery = playersQuery;
	request->rulesQuery = rulesQuery;
	request->queriesActive = qtrue;
	return qtrue;
}

/*
=============
QL_Steamworks_CompleteServerBrowserDetailRequestTerminal

Advances one terminal callback and retires the request bundle on release.
=============
*/
qboolean QL_Steamworks_CompleteServerBrowserDetailRequestTerminal( ql_steam_server_browser_detail_request_t *request, uint32_t terminalChannel, qboolean *outReleaseReady ) {
	qboolean releaseReady;
	qboolean completed;

	if ( outReleaseReady ) {
		*outReleaseReady = qfalse;
	}
	if ( !request ) {
		return qfalse;
	}

	releaseReady = qfalse;
	completed = QL_Steamworks_CompleteServerBrowserDetailTerminal( &request->lifecycle, terminalChannel, &releaseReady );
	if ( !completed ) {
		if ( outReleaseReady ) {
			*outReleaseReady = releaseReady;
		}
		return qfalse;
	}

	if ( releaseReady ) {
		request->detailObjectBase = NULL;
		request->pingQuery = 0;
		request->playersQuery = 0;
		request->rulesQuery = 0;
		request->queriesActive = qfalse;
	}

	if ( outReleaseReady ) {
		*outReleaseReady = releaseReady;
	}
	return qtrue;
}

/*
=============
QL_Steamworks_CompleteServerBrowserDetailRequestCallback

Advances one terminal callback in legacy ping, rules, then players order and
retires the request bundle on release.
=============
*/
qboolean QL_Steamworks_CompleteServerBrowserDetailRequestCallback( ql_steam_server_browser_detail_request_t *request, qboolean *outReleaseReady ) {
	uint32_t terminalChannel;

	terminalChannel = QL_Steamworks_NextServerBrowserDetailTerminalChannel( request ? &request->lifecycle : NULL );
	return QL_Steamworks_CompleteServerBrowserDetailRequestTerminal( request, terminalChannel, outReleaseReady );
}

/*
=============
QL_Steamworks_ReleaseServerListRequest

Releases one retained Steam server-list request handle.
=============
*/
void QL_Steamworks_ReleaseServerListRequest( ql_steam_server_list_request_t request ) {
	void *serverBrowser;
	void **vtable;
	typedef void (__fastcall *QL_SteamMatchmakingServers_RequestHandleFn)( void *self, void *unused, ql_steam_server_list_request_t request );
	QL_SteamMatchmakingServers_RequestHandleFn fn;

	if ( !request ) {
		return;
	}

	serverBrowser = QL_Steamworks_GetServerBrowserInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( serverBrowser );
	if ( !vtable ) {
		return;
	}

	fn = (QL_SteamMatchmakingServers_RequestHandleFn)vtable[QL_STEAM_MATCHMAKING_SERVERS_RELEASE_REQUEST_SLOT];
	if ( !fn ) {
		return;
	}

	fn( serverBrowser, NULL, request );
}

/*
=============
QL_Steamworks_RefreshServerListRequest

Refreshes one retained Steam server-list request handle.
=============
*/
void QL_Steamworks_RefreshServerListRequest( ql_steam_server_list_request_t request ) {
	void *serverBrowser;
	void **vtable;
	typedef void (__fastcall *QL_SteamMatchmakingServers_RequestHandleFn)( void *self, void *unused, ql_steam_server_list_request_t request );
	QL_SteamMatchmakingServers_RequestHandleFn fn;

	if ( !request ) {
		return;
	}

	serverBrowser = QL_Steamworks_GetServerBrowserInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( serverBrowser );
	if ( !vtable ) {
		return;
	}

	fn = (QL_SteamMatchmakingServers_RequestHandleFn)vtable[QL_STEAM_MATCHMAKING_SERVERS_REFRESH_QUERY_SLOT];
	if ( !fn ) {
		return;
	}

	fn( serverBrowser, NULL, request );
}

/*
=============
QL_Steamworks_RequestServerDetails

Starts the retained JSBrowserDetails ping, player, and rule detail probes.
=============
*/
qboolean QL_Steamworks_RequestServerDetails( uint32_t serverIp, uint16_t serverPort, void *pingResponse, void *playersResponse, void *rulesResponse, ql_steam_server_query_t *outPingQuery, ql_steam_server_query_t *outPlayersQuery, ql_steam_server_query_t *outRulesQuery ) {
	void *serverBrowser;
	void **vtable;
	typedef ql_steam_server_query_t (__fastcall *QL_SteamMatchmakingServers_RequestDetailFn)( void *self, void *unused, uint32_t serverIp, uint16_t serverPort, void *responseObject );
	QL_SteamMatchmakingServers_RequestDetailFn pingFn;
	QL_SteamMatchmakingServers_RequestDetailFn playersFn;
	QL_SteamMatchmakingServers_RequestDetailFn rulesFn;
	ql_steam_server_query_t pingQuery;
	ql_steam_server_query_t playersQuery;
	ql_steam_server_query_t rulesQuery;

	if ( outPingQuery ) {
		*outPingQuery = 0;
	}
	if ( outPlayersQuery ) {
		*outPlayersQuery = 0;
	}
	if ( outRulesQuery ) {
		*outRulesQuery = 0;
	}

	if ( serverIp == 0u || serverPort == 0 || !pingResponse || !playersResponse || !rulesResponse ) {
		return qfalse;
	}

	serverBrowser = QL_Steamworks_GetServerBrowserInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( serverBrowser );
	if ( !vtable ) {
		return qfalse;
	}

	pingFn = (QL_SteamMatchmakingServers_RequestDetailFn)vtable[QL_STEAM_MATCHMAKING_SERVERS_PING_SERVER_SLOT];
	playersFn = (QL_SteamMatchmakingServers_RequestDetailFn)vtable[QL_STEAM_MATCHMAKING_SERVERS_PLAYER_DETAILS_SLOT];
	rulesFn = (QL_SteamMatchmakingServers_RequestDetailFn)vtable[QL_STEAM_MATCHMAKING_SERVERS_SERVER_RULES_SLOT];
	if ( !pingFn || !playersFn || !rulesFn ) {
		return qfalse;
	}

	pingQuery = pingFn( serverBrowser, NULL, serverIp, serverPort, pingResponse );
	rulesQuery = rulesFn( serverBrowser, NULL, serverIp, serverPort, rulesResponse );
	playersQuery = playersFn( serverBrowser, NULL, serverIp, serverPort, playersResponse );

	if ( pingQuery <= 0 || rulesQuery <= 0 || playersQuery <= 0 ) {
		QL_Steamworks_CancelServerQuery( pingQuery );
		QL_Steamworks_CancelServerQuery( rulesQuery );
		QL_Steamworks_CancelServerQuery( playersQuery );
		return qfalse;
	}

	if ( outPingQuery ) {
		*outPingQuery = pingQuery;
	}
	if ( outPlayersQuery ) {
		*outPlayersQuery = playersQuery;
	}
	if ( outRulesQuery ) {
		*outRulesQuery = rulesQuery;
	}

	return qtrue;
}

/*
=============
QL_Steamworks_CancelServerQuery

Cancels one Steam server-details query handle.
=============
*/
void QL_Steamworks_CancelServerQuery( ql_steam_server_query_t query ) {
	void *serverBrowser;
	void **vtable;
	typedef void (__fastcall *QL_SteamMatchmakingServers_CancelServerQueryFn)( void *self, void *unused, ql_steam_server_query_t query );
	QL_SteamMatchmakingServers_CancelServerQueryFn fn;

	if ( query <= 0 ) {
		return;
	}

	serverBrowser = QL_Steamworks_GetServerBrowserInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( serverBrowser );
	if ( !vtable ) {
		return;
	}

	fn = (QL_SteamMatchmakingServers_CancelServerQueryFn)vtable[QL_STEAM_MATCHMAKING_SERVERS_CANCEL_SERVER_QUERY_SLOT];
	if ( !fn ) {
		return;
	}

	fn( serverBrowser, NULL, query );
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

	fn = (QL_SteamMatchmaking_CreateLobbyFn)vtable[QL_STEAM_MATCHMAKING_CREATE_LOBBY_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	return fn( matchmaking, NULL, 2, maxMembers ) != 0 ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_SetFavoriteServer
=============
*/
qboolean QL_Steamworks_SetFavoriteServer( uint32_t serverIp, uint16_t serverPort, qboolean add ) {
	return QL_Steamworks_SetFavoriteServerForApp( serverIp, serverPort, QL_Steamworks_GetAppID(), add );
}

/*
=============
QL_Steamworks_SetFavoriteServerForApp
=============
*/
qboolean QL_Steamworks_SetFavoriteServerForApp( uint32_t serverIp, uint16_t serverPort, uint32_t appId, qboolean add ) {
	void *matchmaking;
	void **vtable;
	time_t lastPlayedTime;
	typedef int (__fastcall *QL_SteamMatchmaking_AddFavoriteGameFn)( void *self, void *unused, uint32_t appId, uint32_t serverIp, uint16_t connPort, uint16_t queryPort, uint32_t flags, uint32_t lastPlayedOnServer );
	typedef qboolean (__fastcall *QL_SteamMatchmaking_RemoveFavoriteGameFn)( void *self, void *unused, uint32_t appId, uint32_t serverIp, uint16_t connPort, uint16_t queryPort, uint32_t flags );
	QL_SteamMatchmaking_AddFavoriteGameFn addFavoriteGameFn;
	QL_SteamMatchmaking_RemoveFavoriteGameFn removeFavoriteGameFn;

	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !matchmaking ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !vtable ) {
		return qfalse;
	}

	if ( appId == 0u ) {
		return qfalse;
	}

	if ( add ) {
		addFavoriteGameFn = (QL_SteamMatchmaking_AddFavoriteGameFn)vtable[QL_STEAM_MATCHMAKING_ADD_FAVORITE_GAME_SLOT];
		if ( !addFavoriteGameFn ) {
			return qfalse;
		}

		lastPlayedTime = time( NULL );
		if ( lastPlayedTime < 0 ) {
			lastPlayedTime = 0;
		}

		return addFavoriteGameFn(
			matchmaking,
			NULL,
			appId,
			serverIp,
			serverPort,
			serverPort,
			QL_STEAM_FAVORITE_FLAG_FAVORITE,
			(uint32_t)lastPlayedTime ) >= 0 ? qtrue : qfalse;
	}

	removeFavoriteGameFn = (QL_SteamMatchmaking_RemoveFavoriteGameFn)vtable[QL_STEAM_MATCHMAKING_REMOVE_FAVORITE_GAME_SLOT];
	if ( !removeFavoriteGameFn ) {
		return qfalse;
	}

	return removeFavoriteGameFn(
		matchmaking,
		NULL,
		appId,
		serverIp,
		serverPort,
		serverPort,
		QL_STEAM_FAVORITE_FLAG_FAVORITE );
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

	fn = (QL_SteamMatchmaking_LeaveLobbyFn)vtable[QL_STEAM_MATCHMAKING_LEAVE_LOBBY_SLOT];
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

	fn = (QL_SteamMatchmaking_JoinLobbyFn)vtable[QL_STEAM_MATCHMAKING_JOIN_LOBBY_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	return fn( matchmaking, NULL, idLow, idHigh ) != 0 ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetLobbyOwner
=============
*/
qboolean QL_Steamworks_GetLobbyOwner( uint32_t idLow, uint32_t idHigh, uint32_t *outIdLow, uint32_t *outIdHigh ) {
	void *matchmaking;
	void **vtable;
	CSteamID lobbyOwnerId;
	typedef CSteamID *(__fastcall *QL_SteamMatchmaking_GetLobbyOwnerFn)( void *self, void *unused, CSteamID *outSteamId, uint32_t idLow, uint32_t idHigh );
	QL_SteamMatchmaking_GetLobbyOwnerFn fn;

	if ( outIdLow ) {
		*outIdLow = 0u;
	}
	if ( outIdHigh ) {
		*outIdHigh = 0u;
	}

	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !matchmaking ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamMatchmaking_GetLobbyOwnerFn)vtable[QL_STEAM_MATCHMAKING_GET_LOBBY_OWNER_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	lobbyOwnerId.value = 0ull;
	fn( matchmaking, NULL, &lobbyOwnerId, idLow, idHigh );
	if ( lobbyOwnerId.value == 0ull ) {
		return qfalse;
	}

	if ( outIdLow ) {
		*outIdLow = (uint32_t)( lobbyOwnerId.value & 0xffffffffu );
	}
	if ( outIdHigh ) {
		*outIdHigh = (uint32_t)( ( lobbyOwnerId.value >> 32 ) & 0xffffffffu );
	}

	return qtrue;
}

/*
=============
QL_Steamworks_GetLobbyDataCount
=============
*/
int QL_Steamworks_GetLobbyDataCount( uint32_t idLow, uint32_t idHigh ) {
	void *matchmaking;
	void **vtable;
	typedef int (__fastcall *QL_SteamMatchmaking_GetLobbyDataCountFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamMatchmaking_GetLobbyDataCountFn fn;

	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !matchmaking ) {
		return 0;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !vtable ) {
		return 0;
	}

	fn = (QL_SteamMatchmaking_GetLobbyDataCountFn)vtable[QL_STEAM_MATCHMAKING_GET_LOBBY_DATA_COUNT_SLOT];
	if ( !fn ) {
		return 0;
	}

	return fn( matchmaking, NULL, idLow, idHigh );
}

/*
=============
QL_Steamworks_SetLobbyData
=============
*/
qboolean QL_Steamworks_SetLobbyData( uint32_t idLow, uint32_t idHigh, const char *key, const char *value ) {
	void *matchmaking;
	void **vtable;
	typedef int (__fastcall *QL_SteamMatchmaking_SetLobbyDataFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *key, const char *value );
	QL_SteamMatchmaking_SetLobbyDataFn fn;

	if ( !key || !key[0] || !value ) {
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

	fn = (QL_SteamMatchmaking_SetLobbyDataFn)vtable[QL_STEAM_MATCHMAKING_SET_LOBBY_DATA_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	return fn( matchmaking, NULL, idLow, idHigh, key, value ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetLobbyDataByIndex
=============
*/
qboolean QL_Steamworks_GetLobbyDataByIndex( uint32_t idLow, uint32_t idHigh, int index, char *key, size_t keySize, char *value, size_t valueSize ) {
	void *matchmaking;
	void **vtable;
	typedef void (__fastcall *QL_SteamMatchmaking_GetLobbyDataByIndexFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, int index, char *key, int keySize, char *value, int valueSize );
	QL_SteamMatchmaking_GetLobbyDataByIndexFn fn;

	if ( key && keySize > 0 ) {
		key[0] = '\0';
	}
	if ( value && valueSize > 0 ) {
		value[0] = '\0';
	}

	if ( !key || keySize == 0 || !value || valueSize == 0 || index < 0 ) {
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

	fn = (QL_SteamMatchmaking_GetLobbyDataByIndexFn)vtable[QL_STEAM_MATCHMAKING_GET_LOBBY_DATA_BY_INDEX_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( matchmaking, NULL, idLow, idHigh, index, key, (int)keySize, value, (int)valueSize );
	key[keySize - 1] = '\0';
	value[valueSize - 1] = '\0';
	return key[0] != '\0' ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetNumLobbyMembers
=============
*/
int QL_Steamworks_GetNumLobbyMembers( uint32_t idLow, uint32_t idHigh ) {
	void *matchmaking;
	void **vtable;
	typedef int (__fastcall *QL_SteamMatchmaking_GetNumLobbyMembersFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamMatchmaking_GetNumLobbyMembersFn fn;

	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !matchmaking ) {
		return 0;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !vtable ) {
		return 0;
	}

	fn = (QL_SteamMatchmaking_GetNumLobbyMembersFn)vtable[QL_STEAM_MATCHMAKING_GET_NUM_LOBBY_MEMBERS_SLOT];
	if ( !fn ) {
		return 0;
	}

	return fn( matchmaking, NULL, idLow, idHigh );
}

/*
=============
QL_Steamworks_GetLobbyMemberLimit
=============
*/
int QL_Steamworks_GetLobbyMemberLimit( uint32_t idLow, uint32_t idHigh ) {
	void *matchmaking;
	void **vtable;
	typedef int (__fastcall *QL_SteamMatchmaking_GetLobbyMemberLimitFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamMatchmaking_GetLobbyMemberLimitFn fn;

	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !matchmaking ) {
		return 0;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !vtable ) {
		return 0;
	}

	fn = (QL_SteamMatchmaking_GetLobbyMemberLimitFn)vtable[QL_STEAM_MATCHMAKING_GET_LOBBY_MEMBER_LIMIT_SLOT];
	if ( !fn ) {
		return 0;
	}

	return fn( matchmaking, NULL, idLow, idHigh );
}

/*
=============
QL_Steamworks_GetLobbyMemberByIndex
=============
*/
qboolean QL_Steamworks_GetLobbyMemberByIndex( uint32_t idLow, uint32_t idHigh, int index, uint32_t *outIdLow, uint32_t *outIdHigh ) {
	void *matchmaking;
	void **vtable;
	CSteamID memberId;
	typedef CSteamID *(__fastcall *QL_SteamMatchmaking_GetLobbyMemberByIndexFn)( void *self, void *unused, CSteamID *outSteamId, uint32_t idLow, uint32_t idHigh, int index );
	QL_SteamMatchmaking_GetLobbyMemberByIndexFn fn;

	if ( outIdLow ) {
		*outIdLow = 0u;
	}
	if ( outIdHigh ) {
		*outIdHigh = 0u;
	}

	if ( index < 0 ) {
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

	fn = (QL_SteamMatchmaking_GetLobbyMemberByIndexFn)vtable[QL_STEAM_MATCHMAKING_GET_LOBBY_MEMBER_BY_INDEX_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	memberId.value = 0ull;
	fn( matchmaking, NULL, &memberId, idLow, idHigh, index );
	if ( memberId.value == 0ull ) {
		return qfalse;
	}

	if ( outIdLow ) {
		*outIdLow = (uint32_t)( memberId.value & 0xffffffffu );
	}
	if ( outIdHigh ) {
		*outIdHigh = (uint32_t)( ( memberId.value >> 32 ) & 0xffffffffu );
	}

	return qtrue;
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

	getSteamIdFn = (QL_SteamUser_GetSteamIDFn)userVTable[QL_STEAM_USER_GET_STEAM_ID_SLOT];
	getLobbyOwnerFn = (QL_SteamMatchmaking_GetLobbyOwnerFn)matchmakingVTable[QL_STEAM_MATCHMAKING_GET_LOBBY_OWNER_SLOT];
	setLobbyServerFn = (QL_SteamMatchmaking_SetLobbyGameServerFn)matchmakingVTable[QL_STEAM_MATCHMAKING_SET_LOBBY_GAME_SERVER_SLOT];
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

	fn = (QL_SteamFriends_ActivateGameOverlayInviteDialogFn)vtable[QL_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_INVITE_DIALOG_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( friends, NULL, idLow, idHigh );
	return qtrue;
}

/*
=============
QL_Steamworks_InviteUserToLobby
=============
*/
qboolean QL_Steamworks_InviteUserToLobby( uint32_t lobbyIdLow, uint32_t lobbyIdHigh, uint32_t userIdLow, uint32_t userIdHigh ) {
	void *matchmaking;
	void **vtable;
	typedef int (__fastcall *QL_SteamMatchmaking_InviteUserToLobbyFn)( void *self, void *unused, uint32_t lobbyIdLow, uint32_t lobbyIdHigh, uint32_t userIdLow, uint32_t userIdHigh );
	QL_SteamMatchmaking_InviteUserToLobbyFn fn;

	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !matchmaking ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamMatchmaking_InviteUserToLobbyFn)vtable[QL_STEAM_MATCHMAKING_INVITE_USER_TO_LOBBY_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	return fn( matchmaking, NULL, lobbyIdLow, lobbyIdHigh, userIdLow, userIdHigh ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_InviteUserToGame
=============
*/
qboolean QL_Steamworks_InviteUserToGame( uint32_t idLow, uint32_t idHigh, const char *connectString ) {
	void *friends;
	void **vtable;
	typedef int (__fastcall *QL_SteamFriends_InviteUserToGameFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *connectString );
	QL_SteamFriends_InviteUserToGameFn fn;

	if ( !connectString || !connectString[0] ) {
		return qfalse;
	}

	friends = QL_Steamworks_GetFriendsInterface();
	if ( !friends ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( friends );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamFriends_InviteUserToGameFn)vtable[QL_STEAM_FRIENDS_INVITE_USER_TO_GAME_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	return fn( friends, NULL, idLow, idHigh, connectString ) ? qtrue : qfalse;
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

	fn = (QL_SteamMatchmaking_SendLobbyChatMsgFn)vtable[QL_STEAM_MATCHMAKING_SEND_LOBBY_CHAT_MSG_SLOT];
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

	fn = (QL_SteamUserStats_RequestUserStatsFn)vtable[QL_STEAM_USERSTATS_REQUEST_USER_STATS_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	return fn( userStats, NULL, idLow, idHigh ) != 0 ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetUserStatInt
=============
*/
qboolean QL_Steamworks_GetUserStatInt( uint32_t idLow, uint32_t idHigh, const char *name, int *outValue ) {
	void *userStats;
	void **vtable;
	typedef qboolean (__fastcall *QL_SteamUserStats_GetUserStatIntFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, int *outValue );
	QL_SteamUserStats_GetUserStatIntFn fn;

	if ( outValue ) {
		*outValue = 0;
	}

	if ( !( idLow | idHigh ) || !name || !name[0] || !outValue ) {
		return qfalse;
	}

	userStats = QL_Steamworks_GetUserStatsInterface();
	if ( !userStats ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( userStats );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUserStats_GetUserStatIntFn)vtable[QL_STEAM_USERSTATS_GET_USER_STAT_INT_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	return fn( userStats, NULL, idLow, idHigh, name, outValue ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetUserStatFloat
=============
*/
qboolean QL_Steamworks_GetUserStatFloat( uint32_t idLow, uint32_t idHigh, const char *name, float *outValue ) {
	void *userStats;
	void **vtable;
	typedef qboolean (__fastcall *QL_SteamUserStats_GetUserStatFloatFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, float *outValue );
	QL_SteamUserStats_GetUserStatFloatFn fn;

	if ( outValue ) {
		*outValue = 0.0f;
	}

	if ( !( idLow | idHigh ) || !name || !name[0] || !outValue ) {
		return qfalse;
	}

	userStats = QL_Steamworks_GetUserStatsInterface();
	if ( !userStats ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( userStats );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUserStats_GetUserStatFloatFn)vtable[QL_STEAM_USERSTATS_GET_USER_STAT_FLOAT_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	return fn( userStats, NULL, idLow, idHigh, name, outValue ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetUserAchievement
=============
*/
qboolean QL_Steamworks_GetUserAchievement( uint32_t idLow, uint32_t idHigh, const char *name, qboolean *outAchieved, int *outUnlockTime ) {
	void *userStats;
	void **vtable;
	typedef qboolean (__fastcall *QL_SteamUserStats_GetUserAchievementFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, qboolean *outAchieved, int *outUnlockTime );
	QL_SteamUserStats_GetUserAchievementFn fn;
	qboolean achieved;
	int unlockTime;

	if ( outAchieved ) {
		*outAchieved = qfalse;
	}
	if ( outUnlockTime ) {
		*outUnlockTime = 0;
	}

	if ( !( idLow | idHigh ) || !name || !name[0] || !outAchieved ) {
		return qfalse;
	}

	userStats = QL_Steamworks_GetUserStatsInterface();
	if ( !userStats ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( userStats );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUserStats_GetUserAchievementFn)vtable[QL_STEAM_USERSTATS_GET_USER_ACHIEVEMENT_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	achieved = qfalse;
	unlockTime = 0;
	if ( !fn( userStats, NULL, idLow, idHigh, name, &achieved, &unlockTime ) ) {
		return qfalse;
	}

	*outAchieved = achieved ? qtrue : qfalse;
	if ( outUnlockTime ) {
		*outUnlockTime = unlockTime;
	}
	return qtrue;
}

/*
=============
QL_Steamworks_GetAchievementDisplayAttribute
=============
*/
const char *QL_Steamworks_GetAchievementDisplayAttribute( const char *name, const char *key ) {
	void *userStats;
	void **vtable;
	const char *value;
	typedef const char *(__fastcall *QL_SteamUserStats_GetAchievementDisplayAttributeFn)( void *self, void *unused, const char *name, const char *key );
	QL_SteamUserStats_GetAchievementDisplayAttributeFn fn;

	if ( !name || !name[0] || !key || !key[0] ) {
		return "";
	}

	userStats = QL_Steamworks_GetUserStatsInterface();
	if ( !userStats ) {
		return "";
	}

	vtable = QL_Steamworks_GetInterfaceVTable( userStats );
	if ( !vtable ) {
		return "";
	}

	fn = (QL_SteamUserStats_GetAchievementDisplayAttributeFn)vtable[QL_STEAM_USERSTATS_GET_ACHIEVEMENT_DISPLAY_ATTRIBUTE_SLOT];
	if ( !fn ) {
		return "";
	}

	value = fn( userStats, NULL, name, key );
	return value ? value : "";
}

/*
=============
QL_Steamworks_GetGameServer
=============
*/
static void *QL_Steamworks_GetGameServer( void );

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
QL_Steamworks_GetGameServerUtilsInterface
=============
*/
static void *QL_Steamworks_GetGameServerUtilsInterface( void ) {
	if ( !state.initialised || !state.gameServerInitialised || !state.SteamGameServerUtils ) {
		return NULL;
	}

	return state.SteamGameServerUtils();
}

/*
=============
QL_Steamworks_ServerGetAppID
=============
*/
uint32_t QL_Steamworks_ServerGetAppID( void ) {
	void *gameServerUtils;
	void **vtable;
	typedef uint32_t (__fastcall *QL_SteamGameServerUtils_GetAppIDFn)( void *self, void *unused );
	QL_SteamGameServerUtils_GetAppIDFn fn;

	if ( !state.gameServerInitialised ) {
		return 0u;
	}

	gameServerUtils = QL_Steamworks_GetGameServerUtilsInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( gameServerUtils );
	if ( !vtable ) {
		return 0u;
	}

	fn = (QL_SteamGameServerUtils_GetAppIDFn)vtable[QL_STEAM_GAMESERVER_UTILS_GET_APP_ID_SLOT];
	if ( !fn ) {
		return 0u;
	}

	return fn( gameServerUtils, NULL );
}

/*
=============
QL_Steamworks_ServerIsLoggedOn
=============
*/
qboolean QL_Steamworks_ServerIsLoggedOn( void ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_BLoggedOnFn fn;

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_BLoggedOnFn)vtable[QL_STEAM_GAMESERVER_BLOGGED_ON_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	return fn( gameServer, NULL ) ? qtrue : qfalse;
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

	if ( !state.gameServerInitialised ) {
		return qfalse;
	}

	gameServerStats = QL_Steamworks_GetGameServerStatsInterface();
	if ( !gameServerStats ) {
		return qfalse;
	}

	if ( !QL_Steamworks_ServerIsLoggedOn() ) {
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

	fn = (QL_SteamGameServerStats_RequestUserStatsFn)vtable[QL_STEAM_GAMESERVERSTATS_REQUEST_USER_STATS_SLOT];
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServerStats_GetUserStatIntFn)vtable[QL_STEAM_GAMESERVERSTATS_GET_USER_STAT_INT_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	idLow = (uint32_t)( steamId->value & 0xffffffffu );
	idHigh = (uint32_t)( ( steamId->value >> 32 ) & 0xffffffffu );
	return fn( gameServerStats, NULL, idLow, idHigh, name, outValue ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_ServerGetUserStatFloat
=============
*/
qboolean QL_Steamworks_ServerGetUserStatFloat( const CSteamID *steamId, const char *name, float *outValue ) {
	void *gameServerStats;
	void **vtable;
	typedef qboolean (__fastcall *QL_SteamGameServerStats_GetUserStatFloatFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, float *outValue );
	QL_SteamGameServerStats_GetUserStatFloatFn fn;
	uint32_t idLow;
	uint32_t idHigh;

	if ( outValue ) {
		*outValue = 0.0f;
	}

	if ( !steamId || steamId->value == 0ull || !name || !name[0] || !outValue ) {
		return qfalse;
	}

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServerStats_GetUserStatFloatFn)vtable[QL_STEAM_GAMESERVERSTATS_GET_USER_STAT_FLOAT_SLOT];
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServerStats_GetUserAchievementFn)vtable[QL_STEAM_GAMESERVERSTATS_GET_USER_ACHIEVEMENT_SLOT];
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServerStats_SetUserStatIntFn)vtable[QL_STEAM_GAMESERVERSTATS_SET_USER_STAT_INT_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	idLow = (uint32_t)( steamId->value & 0xffffffffu );
	idHigh = (uint32_t)( ( steamId->value >> 32 ) & 0xffffffffu );
	return fn( gameServerStats, NULL, idLow, idHigh, name, value ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_ServerSetUserStatFloat
=============
*/
qboolean QL_Steamworks_ServerSetUserStatFloat( const CSteamID *steamId, const char *name, float value ) {
	void *gameServerStats;
	void **vtable;
	typedef qboolean (__fastcall *QL_SteamGameServerStats_SetUserStatFloatFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, float value );
	QL_SteamGameServerStats_SetUserStatFloatFn fn;
	uint32_t idLow;
	uint32_t idHigh;

	if ( !steamId || steamId->value == 0ull || !name || !name[0] ) {
		return qfalse;
	}

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServerStats_SetUserStatFloatFn)vtable[QL_STEAM_GAMESERVERSTATS_SET_USER_STAT_FLOAT_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	idLow = (uint32_t)( steamId->value & 0xffffffffu );
	idHigh = (uint32_t)( ( steamId->value >> 32 ) & 0xffffffffu );
	return fn( gameServerStats, NULL, idLow, idHigh, name, value ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_ServerUpdateAvgRateStat
=============
*/
qboolean QL_Steamworks_ServerUpdateAvgRateStat( const CSteamID *steamId, const char *name, float countThisSession, double sessionLength ) {
	void *gameServerStats;
	void **vtable;
	typedef qboolean (__fastcall *QL_SteamGameServerStats_UpdateAvgRateStatFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, float countThisSession, double sessionLength );
	QL_SteamGameServerStats_UpdateAvgRateStatFn fn;
	uint32_t idLow;
	uint32_t idHigh;

	if ( !steamId || steamId->value == 0ull || !name || !name[0] ) {
		return qfalse;
	}

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServerStats_UpdateAvgRateStatFn)vtable[QL_STEAM_GAMESERVERSTATS_UPDATE_AVG_RATE_STAT_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	idLow = (uint32_t)( steamId->value & 0xffffffffu );
	idHigh = (uint32_t)( ( steamId->value >> 32 ) & 0xffffffffu );
	return fn( gameServerStats, NULL, idLow, idHigh, name, countThisSession, sessionLength ) ? qtrue : qfalse;
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServerStats_SetUserAchievementFn)vtable[QL_STEAM_GAMESERVERSTATS_SET_USER_ACHIEVEMENT_SLOT];
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServerStats_StoreUserStatsFn)vtable[QL_STEAM_GAMESERVERSTATS_STORE_USER_STATS_SLOT];
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
QL_Steamworks_HasUGCInterface
=============
*/
qboolean QL_Steamworks_HasUGCInterface( void ) {
	return QL_Steamworks_GetUGCInterface() != NULL ? qtrue : qfalse;
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

	fn = (QL_SteamUGC_GetNumSubscribedItemsFn)vtable[QL_STEAM_UGC_GET_NUM_SUBSCRIBED_ITEMS_SLOT];
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

	fn = (QL_SteamUGC_GetSubscribedItemsFn)vtable[QL_STEAM_UGC_GET_SUBSCRIBED_ITEMS_SLOT];
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

	fn = (QL_SteamUGC_GetItemInstallInfoFn)vtable[QL_STEAM_UGC_GET_ITEM_INSTALL_INFO_SLOT];
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

	fn = (QL_SteamUGC_GetItemStateFn)vtable[QL_STEAM_UGC_GET_ITEM_STATE_SLOT];
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
	uint32_t itemState;

	ugc = QL_Steamworks_GetUGCInterface();
	if ( !ugc ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( ugc );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUGC_SubscribeItemFn)vtable[QL_STEAM_UGC_SUBSCRIBE_ITEM_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( ugc, NULL, idLow, idHigh );
	itemState = QL_Steamworks_GetItemState( idLow, idHigh );
	return itemState != 0u ? qtrue : qfalse;
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

	fn = (QL_SteamUGC_UnsubscribeItemFn)vtable[QL_STEAM_UGC_UNSUBSCRIBE_ITEM_SLOT];
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

	fn = (QL_SteamUGC_DownloadItemFn)vtable[QL_STEAM_UGC_DOWNLOAD_ITEM_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	return fn( ugc, NULL, idLow, idHigh, highPriority ? 1 : 0 ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetAllUGCFilterContractLabel

Returns the retained GetAllUGC integer handoff contract for diagnostics.
=============
*/
const char *QL_Steamworks_GetAllUGCFilterContractLabel( void ) {
	return "raw GetAllUGC integer filter";
}

/*
=============
QL_Steamworks_GetAllUGCFilterSemanticGapLabel

Returns the intentionally unpromoted semantic owner for the retained GetAllUGC
integer filter.
=============
*/
const char *QL_Steamworks_GetAllUGCFilterSemanticGapLabel( void ) {
	return "unpromoted GetAllUGC filter semantic";
}

/*
=============
QL_Steamworks_RequestAllUGCQuery

Issues the retained all-UGC query used by the browser GetAllUGC surface and
binds the asynchronous result to the shared client callback owner.
=============
*/
qboolean QL_Steamworks_RequestAllUGCQuery( uint32_t filter ) {
	void *ugc;
	void **vtable;
	typedef uint64_t (__fastcall *QL_SteamUGC_CreateQueryAllUGCRequestFn)( void *self, void *unused, int queryType, int matchingType, uint32_t creatorAppId, uint32_t consumerAppId, uint32_t filter );
	typedef uint64_t (__fastcall *QL_SteamUGC_SendQueryUGCRequestFn)( void *self, void *unused, uint32_t queryLow, uint32_t queryHigh );
	QL_SteamUGC_CreateQueryAllUGCRequestFn createQueryFn;
	QL_SteamUGC_SendQueryUGCRequestFn sendQueryFn;
	uint32_t appId;
	uint32_t queryHandleHigh;
	uint32_t queryHandleLow;
	uint64_t callHandle;
	uint64_t queryHandle;

	appId = QL_Steamworks_GetAppID();
	if ( appId == 0u ) {
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

	createQueryFn = (QL_SteamUGC_CreateQueryAllUGCRequestFn)vtable[QL_STEAM_UGC_CREATE_QUERY_ALL_UGC_REQUEST_SLOT];
	sendQueryFn = (QL_SteamUGC_SendQueryUGCRequestFn)vtable[QL_STEAM_UGC_SEND_QUERY_UGC_REQUEST_SLOT];
	if ( !createQueryFn || !sendQueryFn ) {
		return qfalse;
	}

	queryHandle = createQueryFn( ugc, NULL, QL_STEAM_UGC_GET_ALL_QUERY_TYPE, QL_STEAM_UGC_GET_ALL_MATCHING_TYPE, appId, appId, filter );
	if ( queryHandle == 0ull ) {
		return qfalse;
	}

	queryHandleLow = (uint32_t)( queryHandle & 0xffffffffu );
	queryHandleHigh = (uint32_t)( queryHandle >> 32 );
	callHandle = sendQueryFn( ugc, NULL, queryHandleLow, queryHandleHigh );
	if ( callHandle == 0ull ) {
		QL_Steamworks_ReleaseQueryUGCRequest( queryHandle );
		return qfalse;
	}

	if ( !QL_Steamworks_BindUGCQueryCallResult( (SteamAPICall_t)callHandle ) ) {
		QL_Steamworks_ReleaseQueryUGCRequest( queryHandle );
		return qfalse;
	}

	return qtrue;
}

/*
=============
QL_Steamworks_GetQueryUGCResult

Reads the title/description/item-id details for one query row through the
retained SteamUGC result slot without depending on the Steam SDK headers.
=============
*/
qboolean QL_Steamworks_GetQueryUGCResult( uint64_t queryHandle, uint32_t index, uint64_t *outPublishedFileId, char *title, size_t titleSize, char *description, size_t descriptionSize ) {
	void *ugc;
	void **vtable;
	typedef qboolean (__fastcall *QL_SteamUGC_GetQueryUGCResultFn)( void *self, void *unused, uint32_t queryLow, uint32_t queryHigh, uint32_t index, void *details );
	QL_SteamUGC_GetQueryUGCResultFn fn;
	unsigned char details[QL_STEAM_UGC_DETAILS_BUFFER_SIZE];
	uint32_t queryHandleHigh;
	uint32_t queryHandleLow;

	if ( outPublishedFileId ) {
		*outPublishedFileId = 0ull;
	}
	if ( title && titleSize > 0 ) {
		title[0] = '\0';
	}
	if ( description && descriptionSize > 0 ) {
		description[0] = '\0';
	}

	if ( queryHandle == 0ull || !title || titleSize == 0 || !description || descriptionSize == 0 ) {
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

	fn = (QL_SteamUGC_GetQueryUGCResultFn)vtable[QL_STEAM_UGC_GET_QUERY_UGC_RESULT_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	queryHandleLow = (uint32_t)( queryHandle & 0xffffffffu );
	queryHandleHigh = (uint32_t)( queryHandle >> 32 );
	memset( details, 0, sizeof( details ) );
	if ( !fn( ugc, NULL, queryHandleLow, queryHandleHigh, index, details ) ) {
		return qfalse;
	}

	if ( outPublishedFileId ) {
		memcpy( outPublishedFileId, details + QL_STEAM_UGC_DETAILS_PUBLISHED_FILE_ID_OFFSET, QL_STEAM_UGC_DETAILS_PUBLISHED_FILE_ID_SIZE );
	}

	QL_Steamworks_CopySteamString( title, titleSize, (const char *)( details + QL_STEAM_UGC_DETAILS_TITLE_OFFSET ) );
	QL_Steamworks_CopySteamString( description, descriptionSize, (const char *)( details + QL_STEAM_UGC_DETAILS_DESCRIPTION_OFFSET ) );
	return qtrue;
}

/*
=============
QL_Steamworks_GetQueryUGCPreviewURL
=============
*/
qboolean QL_Steamworks_GetQueryUGCPreviewURL( uint64_t queryHandle, uint32_t index, char *buffer, size_t bufferSize ) {
	void *ugc;
	void **vtable;
	typedef qboolean (__fastcall *QL_SteamUGC_GetQueryUGCPreviewURLFn)( void *self, void *unused, uint32_t queryLow, uint32_t queryHigh, uint32_t index, char *buffer, uint32_t bufferSize );
	QL_SteamUGC_GetQueryUGCPreviewURLFn fn;
	uint32_t queryHandleHigh;
	uint32_t queryHandleLow;

	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}

	if ( queryHandle == 0ull || !buffer || bufferSize == 0 ) {
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

	fn = (QL_SteamUGC_GetQueryUGCPreviewURLFn)vtable[QL_STEAM_UGC_GET_QUERY_UGC_PREVIEW_URL_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	queryHandleLow = (uint32_t)( queryHandle & 0xffffffffu );
	queryHandleHigh = (uint32_t)( queryHandle >> 32 );
	if ( !fn( ugc, NULL, queryHandleLow, queryHandleHigh, index, buffer, (uint32_t)bufferSize ) ) {
		buffer[0] = '\0';
		return qfalse;
	}

	buffer[bufferSize - 1] = '\0';
	return qtrue;
}

/*
=============
QL_Steamworks_ReleaseQueryUGCRequest
=============
*/
void QL_Steamworks_ReleaseQueryUGCRequest( uint64_t queryHandle ) {
	void *ugc;
	void **vtable;
	typedef qboolean (__fastcall *QL_SteamUGC_ReleaseQueryUGCRequestFn)( void *self, void *unused, uint32_t queryLow, uint32_t queryHigh );
	QL_SteamUGC_ReleaseQueryUGCRequestFn fn;
	uint32_t queryHandleHigh;
	uint32_t queryHandleLow;

	if ( queryHandle == 0ull ) {
		return;
	}

	ugc = QL_Steamworks_GetUGCInterface();
	if ( !ugc ) {
		return;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( ugc );
	if ( !vtable ) {
		return;
	}

	fn = (QL_SteamUGC_ReleaseQueryUGCRequestFn)vtable[QL_STEAM_UGC_RELEASE_QUERY_UGC_REQUEST_SLOT];
	if ( !fn ) {
		return;
	}

	queryHandleLow = (uint32_t)( queryHandle & 0xffffffffu );
	queryHandleHigh = (uint32_t)( queryHandle >> 32 );
	(void)fn( ugc, NULL, queryHandleLow, queryHandleHigh );
}

/*
=============
QL_Steamworks_GetAvatarMethodIndex
=============
*/
static int QL_Steamworks_GetAvatarMethodIndex( ql_steam_avatar_size_t size ) {
	switch ( size ) {
	case QL_STEAM_AVATAR_SMALL:
		return QL_STEAM_FRIENDS_GET_SMALL_FRIEND_AVATAR_SLOT;
	case QL_STEAM_AVATAR_MEDIUM:
		return QL_STEAM_FRIENDS_GET_MEDIUM_FRIEND_AVATAR_SLOT;
	case QL_STEAM_AVATAR_LARGE:
	default:
		return QL_STEAM_FRIENDS_GET_LARGE_FRIEND_AVATAR_SLOT;
	}
}

/*
=============
QL_Steamworks_RequestAvatarImage
=============
*/
ql_steam_avatar_image_state_t QL_Steamworks_RequestAvatarImage( uint32_t idLow, uint32_t idHigh, ql_steam_avatar_size_t size, int *outImage ) {
	void *friends;
	void **friendsVTable;
	typedef int (__fastcall *QL_SteamFriends_GetAvatarFn)( void *self, void *unused, CSteamID steamId );
	QL_SteamFriends_GetAvatarFn getAvatar;
	CSteamID steamId;
	int image;

	if ( outImage ) {
		*outImage = 0;
	}

	if ( !QL_Steamworks_Init() || !state.SteamFriends ) {
		return QL_STEAM_AVATAR_IMAGE_UNAVAILABLE;
	}

	friends = state.SteamFriends();
	if ( !friends ) {
		return QL_STEAM_AVATAR_IMAGE_UNAVAILABLE;
	}

	friendsVTable = QL_Steamworks_GetInterfaceVTable( friends );
	if ( !friendsVTable ) {
		return QL_STEAM_AVATAR_IMAGE_UNAVAILABLE;
	}

	getAvatar = (QL_SteamFriends_GetAvatarFn)friendsVTable[QL_Steamworks_GetAvatarMethodIndex( size )];
	if ( !getAvatar ) {
		return QL_STEAM_AVATAR_IMAGE_UNAVAILABLE;
	}

	steamId = QL_Steamworks_CombineIdentityWords( idLow, idHigh );
	image = getAvatar( friends, NULL, steamId );
	if ( outImage ) {
		*outImage = image;
	}

	if ( image == -1 ) {
		return QL_STEAM_AVATAR_IMAGE_PENDING;
	}

	if ( image <= 0 ) {
		return QL_STEAM_AVATAR_IMAGE_UNAVAILABLE;
	}

	return QL_STEAM_AVATAR_IMAGE_READY;
}

/*
=============
QL_Steamworks_LoadAvatarRGBA
=============
*/
qboolean QL_Steamworks_LoadAvatarRGBA( uint32_t idLow, uint32_t idHigh, ql_steam_avatar_size_t size, uint8_t **outPixels, uint32_t *outWidth, uint32_t *outHeight ) {
	void *utils;
	void **utilsVTable;
	typedef int (__fastcall *QL_SteamUtils_GetImageSizeFn)( void *self, void *unused, int image, uint32_t *width, uint32_t *height );
	typedef int (__fastcall *QL_SteamUtils_GetImageRGBAFn)( void *self, void *unused, int image, uint8_t *buffer, int length );
	QL_SteamUtils_GetImageSizeFn getImageSize;
	QL_SteamUtils_GetImageRGBAFn getImageRGBA;
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

	if ( QL_Steamworks_RequestAvatarImage( idLow, idHigh, size, &image ) != QL_STEAM_AVATAR_IMAGE_READY ) {
		return qfalse;
	}

	if ( !QL_Steamworks_Init() || !state.SteamUtils ) {
		return qfalse;
	}

	utils = state.SteamUtils();
	if ( !utils ) {
		return qfalse;
	}

	utilsVTable = QL_Steamworks_GetInterfaceVTable( utils );
	if ( !utilsVTable ) {
		return qfalse;
	}

	getImageSize = (QL_SteamUtils_GetImageSizeFn)utilsVTable[QL_STEAM_UTILS_GET_IMAGE_SIZE_SLOT];
	getImageRGBA = (QL_SteamUtils_GetImageRGBAFn)utilsVTable[QL_STEAM_UTILS_GET_IMAGE_RGBA_SLOT];
	if ( !getImageSize || !getImageRGBA ) {
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
	QL_SteamApps_BIsSubscribedAppFn fn = (QL_SteamApps_BIsSubscribedAppFn)vtable[QL_STEAM_APPS_BIS_SUBSCRIBED_APP_SLOT];
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
	QL_SteamUGC_GetItemDownloadInfoFn fn = (QL_SteamUGC_GetItemDownloadInfoFn)vtable[QL_STEAM_UGC_GET_ITEM_DOWNLOAD_INFO_SLOT];
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
QL_Steamworks_ServerInitWithVersion

Reconstructs the retail Steam game-server init gate and remembers which UGC
owner should back workshop calls for the active server path. The caller may
override the advertised Steam version string while the retail build string
remains the default.
=============
*/
qboolean QL_Steamworks_ServerInitWithVersion( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated, const char *version ) {
	int serverMode;
	const char *versionString;

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
	versionString = ( version && version[0] ) ? version : QL_STEAM_GAMESERVER_DEFAULT_VERSION;
	if ( !state.SteamGameServer_Init( ip, 0, gamePort, 0xffffu, serverMode, versionString ) ) {
		return qfalse;
	}

	state.gameServerInitialised = qtrue;
	state.useGameServerUGC = dedicated ? qtrue : qfalse;
	return qtrue;
}

/*
=============
QL_Steamworks_ServerInit

Initializes the Steam game-server path with the retained retail default
version string.
=============
*/
qboolean QL_Steamworks_ServerInit( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated ) {
	return QL_Steamworks_ServerInitWithVersion( ip, gamePort, secure, dedicated, QL_STEAM_GAMESERVER_DEFAULT_VERSION );
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_SetDedicatedFn)vtable[QL_STEAM_GAMESERVER_SET_DEDICATED_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, NULL, dedicated ? 1 : 0 );
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

	if ( !state.gameServerInitialised ) {
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

	if ( account && account[0] ) {
		logOnFn = (QL_SteamGameServer_LogOnFn)vtable[QL_STEAM_GAMESERVER_LOG_ON_SLOT];
		if ( !logOnFn ) {
			return qfalse;
		}

		logOnFn( gameServer, NULL, account );
		return qtrue;
	}

	anonymousFn = (QL_SteamGameServer_LogOnAnonymousFn)vtable[QL_STEAM_GAMESERVER_LOG_ON_ANONYMOUS_SLOT];
	if ( !anonymousFn ) {
		return qfalse;
	}

	anonymousFn( gameServer, NULL );
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_SetStringFn)vtable[QL_STEAM_GAMESERVER_SET_PRODUCT_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, NULL, product );
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_SetStringFn)vtable[QL_STEAM_GAMESERVER_SET_GAME_DIR_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, NULL, gameDir );
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_SetStringFn)vtable[QL_STEAM_GAMESERVER_SET_GAME_DESCRIPTION_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, NULL, description );
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_SetIntFn)vtable[QL_STEAM_GAMESERVER_SET_MAX_PLAYER_COUNT_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, NULL, maxPlayers );
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_SetIntFn)vtable[QL_STEAM_GAMESERVER_SET_BOT_PLAYER_COUNT_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, NULL, botPlayers );
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_SetStringFn)vtable[QL_STEAM_GAMESERVER_SET_SERVER_NAME_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, NULL, name );
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_SetStringFn)vtable[QL_STEAM_GAMESERVER_SET_MAP_NAME_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, NULL, mapName );
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_SetIntFn)vtable[QL_STEAM_GAMESERVER_SET_PASSWORD_PROTECTED_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, NULL, passwordProtected ? 1 : 0 );
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_EnableHeartbeatsFn)vtable[QL_STEAM_GAMESERVER_ENABLE_HEARTBEATS_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, NULL, enable ? 1 : 0 );
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_GetSteamIDFn)vtable[QL_STEAM_GAMESERVER_GET_STEAM_ID_SLOT];
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
QL_Steamworks_ServerCreateUnauthenticatedUserConnection

Creates the retail unauthenticated Steam identity used for local server-owned clients.
=============
*/
qboolean QL_Steamworks_ServerCreateUnauthenticatedUserConnection( uint32_t *outIdLow, uint32_t *outIdHigh ) {
	void *gameServer;
	void **vtable;
	CSteamID steamId;
	QL_SteamGameServer_CreateUnauthenticatedUserConnectionFn fn;

	if ( outIdLow ) {
		*outIdLow = 0u;
	}
	if ( outIdHigh ) {
		*outIdHigh = 0u;
	}

	if ( !outIdLow || !outIdHigh ) {
		return qfalse;
	}

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_CreateUnauthenticatedUserConnectionFn)vtable[QL_STEAM_GAMESERVER_CREATE_UNAUTHENTICATED_USER_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	steamId.value = 0ull;
	if ( !fn( gameServer, NULL, &steamId ) ) {
		return qfalse;
	}

	*outIdLow = (uint32_t)( steamId.value & 0xffffffffu );
	*outIdHigh = (uint32_t)( ( steamId.value >> 32 ) & 0xffffffffu );
	return steamId.value != 0ull ? qtrue : qfalse;
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_SetStringFn)vtable[QL_STEAM_GAMESERVER_SET_GAME_TAGS_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, NULL, tags );
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_SetKeyValueFn)vtable[QL_STEAM_GAMESERVER_SET_KEY_VALUE_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, NULL, key, value );
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

	if ( !state.gameServerInitialised ) {
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

	if ( !state.gameServerInitialised ) {
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

	fn = (QL_SteamGameServer_UpdateUserDataFn)vtable[QL_STEAM_GAMESERVER_UPDATE_USER_DATA_SLOT];
	if ( !fn ) {
		return qfalse;
	}

	idLow = (uint32_t)( steamId->value & 0xffffffffu );
	idHigh = (uint32_t)( ( steamId->value >> 32 ) & 0xffffffffu );

	return fn( gameServer, NULL, idLow, idHigh, playerName, score ) != 0 ? qtrue : qfalse;
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

	if ( !state.gameServerInitialised ) {
		return 0u;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return 0u;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return 0u;
	}

	fn = (QL_SteamGameServer_GetPublicIPFn)vtable[QL_STEAM_GAMESERVER_GET_PUBLIC_IP_SLOT];
	if ( !fn ) {
		return 0u;
	}

	return fn( gameServer, NULL );
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

	sendPacket = (QL_SteamNetworking_SendP2PPacketFn)vtable[QL_STEAM_NETWORKING_SEND_P2P_PACKET_SLOT];
	if ( !sendPacket ) {
		return qfalse;
	}

	return sendPacket( networking, NULL, *steamId, data, length, sendType, channel );
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

	isAvailable = (QL_SteamNetworking_IsP2PPacketAvailableFn)vtable[QL_STEAM_NETWORKING_IS_P2P_PACKET_AVAILABLE_SLOT];
	if ( !isAvailable ) {
		return qfalse;
	}

	return isAvailable( networking, NULL, outSize, channel );
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

	readPacket = (QL_SteamNetworking_ReadP2PPacketFn)vtable[QL_STEAM_NETWORKING_READ_P2P_PACKET_SLOT];
	if ( !readPacket ) {
		return qfalse;
	}

	return readPacket( networking, NULL, data, dataSize, outSize, outSteamId, channel );
}

/*
=============
QL_Steamworks_GetP2PTransportLabel

Returns the retained Steam P2P transport owner for diagnostics.
=============
*/
const char *QL_Steamworks_GetP2PTransportLabel( void ) {
	return "legacy ISteamNetworking";
}

/*
=============
QL_Steamworks_GetP2PModernGapLabel

Returns the modern P2P adapter that is intentionally not reconstructed.
=============
*/
const char *QL_Steamworks_GetP2PModernGapLabel( void ) {
	return "missing ISteamNetworkingSockets/ISteamNetworkingMessages adapter";
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
	typedef qboolean (QL_STEAMWORKS_FASTCALL *QL_SteamNetworking_AcceptP2PSessionWithUserFn)( void *self, void *unused, CSteamID steamId );
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

	acceptSession = (QL_SteamNetworking_AcceptP2PSessionWithUserFn)vtable[QL_STEAM_NETWORKING_ACCEPT_P2P_SESSION_SLOT];
	if ( !acceptSession ) {
		return qfalse;
	}

	return acceptSession( networking, NULL, *steamId ) ? qtrue : qfalse;
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

	fn = (QL_SteamUser_StartVoiceRecordingFn)vtable[QL_STEAM_USER_START_VOICE_RECORDING_SLOT];
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

	fn = (QL_SteamUser_StopVoiceRecordingFn)vtable[QL_STEAM_USER_STOP_VOICE_RECORDING_SLOT];
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

	fn = (QL_SteamUser_GetVoiceFn)vtable[QL_STEAM_USER_GET_VOICE_SLOT];
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

	fn = (QL_SteamUser_DecompressVoiceFn)vtable[QL_STEAM_USER_DECOMPRESS_VOICE_SLOT];
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

	fn = (QL_SteamUser_GetVoiceOptimalSampleRateFn)vtable[QL_STEAM_USER_GET_VOICE_OPTIMAL_SAMPLE_RATE_SLOT];
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

	if ( !state.gameServerInitialised ) {
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

	sendPacket = (QL_SteamNetworking_SendP2PPacketFn)vtable[QL_STEAM_NETWORKING_SEND_P2P_PACKET_SLOT];
	if ( !sendPacket ) {
		return qfalse;
	}

	return sendPacket( networking, NULL, *steamId, data, length, sendType, channel );
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

	if ( !state.gameServerInitialised ) {
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

	isAvailable = (QL_SteamNetworking_IsP2PPacketAvailableFn)vtable[QL_STEAM_NETWORKING_IS_P2P_PACKET_AVAILABLE_SLOT];
	if ( !isAvailable ) {
		return qfalse;
	}

	return isAvailable( networking, NULL, outSize, channel );
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

	if ( !state.gameServerInitialised ) {
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

	readPacket = (QL_SteamNetworking_ReadP2PPacketFn)vtable[QL_STEAM_NETWORKING_READ_P2P_PACKET_SLOT];
	if ( !readPacket ) {
		return qfalse;
	}

	return readPacket( networking, NULL, data, dataSize, outSize, outSteamId, channel );
}

/*
=============
QL_Steamworks_ServerHandleIncomingPacket

Hands one UDP packet received by the host socket to the Steam GameServer interface.
=============
*/
qboolean QL_Steamworks_ServerHandleIncomingPacket( const void *data, int dataSize, uint32_t ip, uint16_t port ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_HandleIncomingPacketFn handlePacket;

	if ( !data || dataSize <= 0 ) {
		return qfalse;
	}

	if ( !state.gameServerInitialised ) {
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

	handlePacket = (QL_SteamGameServer_HandleIncomingPacketFn)vtable[QL_STEAM_GAMESERVER_HANDLE_INCOMING_PACKET_SLOT];
	if ( !handlePacket ) {
		return qfalse;
	}

	return handlePacket( gameServer, NULL, data, dataSize, ip, port ) ? qtrue : qfalse;
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

	if ( !state.gameServerInitialised ) {
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

	getPacket = (QL_SteamGameServer_GetNextOutgoingPacketFn)vtable[QL_STEAM_GAMESERVER_GET_NEXT_OUTGOING_PACKET_SLOT];
	if ( !getPacket ) {
		return 0;
	}

	return getPacket( gameServer, NULL, data, dataSize, outIp, outPort );
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
	typedef qboolean (QL_STEAMWORKS_FASTCALL *QL_SteamNetworking_AcceptP2PSessionWithUserFn)( void *self, void *unused, CSteamID steamId );
	QL_SteamNetworking_AcceptP2PSessionWithUserFn acceptSession;

	if ( !steamId ) {
		return qfalse;
	}

	if ( !state.gameServerInitialised ) {
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

	acceptSession = (QL_SteamNetworking_AcceptP2PSessionWithUserFn)vtable[QL_STEAM_NETWORKING_ACCEPT_P2P_SESSION_SLOT];
	if ( !acceptSession ) {
		return qfalse;
	}

	return acceptSession( networking, NULL, *steamId ) ? qtrue : qfalse;
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
QL_Steamworks_GetAuthTicketApiLabel

Returns the retained Steam auth-ticket API owner for diagnostics.
=============
*/
const char *QL_Steamworks_GetAuthTicketApiLabel( void ) {
	return QL_Steamworks_HasWebApiAuthTicketAdapter() ? "GetAuthTicketForWebApi" : "retail GetAuthSessionTicket";
}

/*
=============
QL_Steamworks_GetAuthTicketModernGapLabel

Returns the modern auth-ticket adapter state for diagnostics.
=============
*/
const char *QL_Steamworks_GetAuthTicketModernGapLabel( void ) {
	return QL_Steamworks_HasWebApiAuthTicketAdapter() ? "GetAuthTicketForWebApi adapter available" : "missing GetAuthTicketForWebApi adapter";
}

/*
=============
QL_Steamworks_GetWebApiAuthTicketIdentity

Returns the service identity string sent to GetAuthTicketForWebApi.
=============
*/
const char *QL_Steamworks_GetWebApiAuthTicketIdentity( void ) {
	return "quake-live-srp-auth";
}

/*
=============
QL_Steamworks_HasWebApiAuthTicketAdapter

Reports whether the loaded Steam runtime exposes the Web API ticket adapter.
=============
*/
qboolean QL_Steamworks_HasWebApiAuthTicketAdapter( void ) {
	if ( !QL_Steamworks_Init() ) {
		return qfalse;
	}

	return state.GetAuthTicketForWebApi && state.SteamAPI_RegisterCallback && state.SteamAPI_RunCallbacks ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_RequestWebApiAuthTicket

Requests a Web API auth ticket and returns the callback ticket encoded as hex.
=============
*/
qboolean QL_Steamworks_RequestWebApiAuthTicket( const char *identity, char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle, int *steamResult ) {
	ql_steam_client_callback_state_t *callbackState;
	void *user;
	HAuthTicket handle;
	int pump;

	if ( ticketBuffer && ticketBufferSize > 0 ) {
		ticketBuffer[0] = '\0';
	}
	if ( ticketLength ) {
		*ticketLength = 0;
	}
	if ( ticketHandle ) {
		*ticketHandle = 0u;
	}
	if ( steamResult ) {
		*steamResult = 0;
	}

	if ( !ticketBuffer || ticketBufferSize == 0 ) {
		return qfalse;
	}

	if ( !QL_Steamworks_Init() ) {
		return qfalse;
	}

	if ( !QL_Steamworks_IsUserLoggedOn() ) {
		return qfalse;
	}

	if ( !state.GetAuthTicketForWebApi || !state.SteamAPI_RegisterCallback || !state.SteamAPI_RunCallbacks ) {
		return qfalse;
	}

	user = state.SteamUser ? state.SteamUser() : NULL;
	if ( !user ) {
		return qfalse;
	}

	if ( !QL_Steamworks_RegisterWebApiAuthTicketCallback() ) {
		return qfalse;
	}

	callbackState = &state.clientCallbacks;
	QL_Steamworks_ResetWebApiAuthTicketState( callbackState );

	handle = state.GetAuthTicketForWebApi( user, ( identity && identity[0] ) ? identity : QL_Steamworks_GetWebApiAuthTicketIdentity() );
	if ( handle == 0 ) {
		return qfalse;
	}

	callbackState->webApiTicketActive = qtrue;
	callbackState->webApiTicketHandle = handle;

	for ( pump = 0; pump < QL_STEAM_WEB_API_TICKET_CALLBACK_PUMPS && !callbackState->webApiTicketCompleted; ++pump ) {
		QL_Steamworks_RunCallbacks();
	}

	if ( !callbackState->webApiTicketCompleted ) {
		QL_Steamworks_CancelAuthTicket( handle );
		QL_Steamworks_ResetWebApiAuthTicketState( callbackState );
		return qfalse;
	}

	if ( steamResult ) {
		*steamResult = callbackState->webApiTicketResult;
	}

	if ( callbackState->webApiTicketResult != QL_STEAM_ERESULT_OK || callbackState->webApiTicketLength == 0u ) {
		QL_Steamworks_CancelAuthTicket( handle );
		QL_Steamworks_ResetWebApiAuthTicketState( callbackState );
		return qfalse;
	}

	if ( !QL_Steamworks_HexEncode( callbackState->webApiTicket, callbackState->webApiTicketLength, ticketBuffer, ticketBufferSize ) ) {
		QL_Steamworks_CancelAuthTicket( handle );
		QL_Steamworks_ResetWebApiAuthTicketState( callbackState );
		return qfalse;
	}

	if ( ticketLength ) {
		*ticketLength = (int)( callbackState->webApiTicketLength * 2u );
	}

	if ( ticketHandle ) {
		*ticketHandle = handle;
	}

	QL_Steamworks_ResetWebApiAuthTicketState( callbackState );
	return qtrue;
}

/*
=============
QL_Steamworks_RequestAuthTicket

Requests an auth session ticket and returns it encoded as hex.
=============
*/
qboolean QL_Steamworks_RequestAuthTicket( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle ) {
	if ( ticketBuffer && ticketBufferSize > 0 ) {
		ticketBuffer[0] = '\0';
	}
	if ( ticketLength ) {
		*ticketLength = 0;
	}
	if ( ticketHandle ) {
		*ticketHandle = 0u;
	}

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
	void **vtable;
	QL_SteamGameServer_BeginAuthSessionFn beginAuthSession;
	uint8_t ticketData[2048];
	uint32_t ticketLength;
	EBeginAuthSessionResult result;

	if ( response ) {
		memset( response, 0, sizeof( *response ) );
	}

	if ( !steamId || !ticketHex || !ticketHex[0] ) {
		return qfalse;
	}

	if ( !state.gameServerInitialised ) {
		return qfalse;
	}

	if ( !QL_Steamworks_ServerIsLoggedOn() ) {
		if ( response ) {
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, "Steam GameServer not logged on" );
		}
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

	beginAuthSession = (QL_SteamGameServer_BeginAuthSessionFn)vtable[QL_STEAM_GAMESERVER_BEGIN_AUTH_SESSION_SLOT];
	if ( !beginAuthSession ) {
		return qfalse;
	}

	ticketLength = 0;
	if ( !QL_Steamworks_HexDecode( ticketHex, ticketData, sizeof( ticketData ), &ticketLength ) || ticketLength == 0 ) {
		if ( response ) {
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED, "Steam ticket invalid" );
		}
		return qfalse;
	}

	result = beginAuthSession( gameServer, NULL, ticketData, (int)ticketLength, *steamId );
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
	void **vtable;
	QL_SteamGameServer_EndAuthSessionFn endAuthSession;

	if ( !steamId ) {
		return;
	}

	if ( !state.gameServerInitialised ) {
		return;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return;
	}

	endAuthSession = (QL_SteamGameServer_EndAuthSessionFn)vtable[QL_STEAM_GAMESERVER_END_AUTH_SESSION_SLOT];
	if ( !endAuthSession ) {
		return;
	}

	endAuthSession( gameServer, NULL, *steamId );
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

	if ( !QL_Steamworks_IsUserLoggedOn() ) {
		QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, "Steam user not logged on" );
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
