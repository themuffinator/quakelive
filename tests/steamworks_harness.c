#include <ctype.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "../src/common/platform/platform_steamworks.h"
#include "../src/common/platform/platform_services.h"

#ifdef _WIN32
#define QLR_EXPORT __declspec(dllexport)
#else
#define QLR_EXPORT
#endif

#if QL_BUILD_STEAMWORKS

#define QLR_TICKET_BUFFER 1024
#define QLR_WEB_API_TICKET_BUFFER QL_STEAM_WEB_API_AUTH_TICKET_MAX_LENGTH
#define QLR_PENDING_CALLBACK_BUFFER ( QL_STEAM_WEB_API_AUTH_TICKET_MAX_LENGTH + 16 )
#define QLR_AVATAR_BUFFER ( 256 * 256 * 4 )
#define QLR_P2P_PACKET_BUFFER 512
#define QLR_VOICE_BUFFER 512

#if defined(_MSC_VER)
#define QLR_FASTCALL __fastcall
#define QLR_THISCALL __thiscall
#elif defined(__GNUC__) && defined(__i386__)
#define QLR_FASTCALL __attribute__((fastcall))
#define QLR_THISCALL __attribute__((thiscall))
#else
#define QLR_FASTCALL
#define QLR_THISCALL
#endif

#define QLR_STEAMWORKS_EXPORT_STEAM_API_INIT "SteamAPI_Init"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_SHUTDOWN "SteamAPI_Shutdown"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_RUN_CALLBACKS "SteamAPI_RunCallbacks"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_REGISTER_CALLBACK "SteamAPI_RegisterCallback"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_UNREGISTER_CALLBACK "SteamAPI_UnregisterCallback"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_REGISTER_CALL_RESULT "SteamAPI_RegisterCallResult"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_UNREGISTER_CALL_RESULT "SteamAPI_UnregisterCallResult"
#define QLR_STEAMWORKS_EXPORT_STEAM_USER "SteamUser"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_USER "SteamAPI_SteamUser"
#define QLR_STEAMWORKS_EXPORT_STEAM_FRIENDS "SteamFriends"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_FRIENDS "SteamAPI_SteamFriends"
#define QLR_STEAMWORKS_EXPORT_STEAM_NETWORKING "SteamNetworking"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_NETWORKING "SteamAPI_SteamNetworking"
#define QLR_STEAMWORKS_EXPORT_STEAM_UTILS "SteamUtils"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_UTILS "SteamAPI_SteamUtils"
#define QLR_STEAMWORKS_EXPORT_STEAM_USER_STATS "SteamUserStats"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_USER_STATS "SteamAPI_SteamUserStats"
#define QLR_STEAMWORKS_EXPORT_STEAM_MATCHMAKING "SteamMatchmaking"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_MATCHMAKING "SteamAPI_SteamMatchmaking"
#define QLR_STEAMWORKS_EXPORT_STEAM_MATCHMAKING_SERVERS "SteamMatchmakingServers"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_MATCHMAKING_SERVERS "SteamAPI_SteamMatchmakingServers"
#define QLR_STEAMWORKS_EXPORT_STEAM_APPS "SteamApps"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_APPS "SteamAPI_SteamApps"
#define QLR_STEAMWORKS_EXPORT_STEAM_UGC "SteamUGC"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_UGC "SteamAPI_SteamUGC"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_GET_AUTH_SESSION_TICKET "SteamAPI_ISteamUser_GetAuthSessionTicket"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_GET_AUTH_TICKET_FOR_WEB_API "SteamAPI_ISteamUser_GetAuthTicketForWebApi"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_BEGIN_AUTH_SESSION "SteamAPI_ISteamUser_BeginAuthSession"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_CANCEL_AUTH_TICKET "SteamAPI_ISteamUser_CancelAuthTicket"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_END_AUTH_SESSION "SteamAPI_ISteamUser_EndAuthSession"
#define QLR_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_GET_STEAM_ID "SteamAPI_ISteamUser_GetSteamID"
#define QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER "SteamGameServer"
#define QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_STATS "SteamGameServerStats"
#define QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_UTILS "SteamGameServerUtils"
#define QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_UGC "SteamGameServerUGC"
#define QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_INIT "SteamGameServer_Init"
#define QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_SHUTDOWN "SteamGameServer_Shutdown"
#define QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_RUN_CALLBACKS "SteamGameServer_RunCallbacks"
#define QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_NETWORKING "SteamGameServerNetworking"

#define QLR_MAX_CALLBACK_REGISTRATIONS 32
#define QLR_MAX_PENDING_CALLBACKS 32
#define QLR_MAX_SUBSCRIBED_ITEMS 32
#define QLR_STEAM_CALLBACK_FLAG_GAMESERVER 0x02
#define QLR_STEAM_CALLBACK_GET_TICKET_FOR_WEB_API_RESPONSE 0xa8
#define QLR_STEAM_ERESULT_OK 1
#define QLR_STEAM_UGC_DETAILS_PUBLISHED_FILE_ID_OFFSET 0x00
#define QLR_STEAM_UGC_DETAILS_PUBLISHED_FILE_ID_SIZE 0x08
#define QLR_STEAM_UGC_DETAILS_TITLE_OFFSET 0x18
#define QLR_STEAM_UGC_DETAILS_DESCRIPTION_OFFSET 0x99
#define QLR_STEAM_NETWORKING_SEND_P2P_PACKET_SLOT 0
#define QLR_STEAM_NETWORKING_IS_P2P_PACKET_AVAILABLE_SLOT 1
#define QLR_STEAM_NETWORKING_READ_P2P_PACKET_SLOT 2
#define QLR_STEAM_NETWORKING_ACCEPT_P2P_SESSION_SLOT (0x0c / 4)
#define QLR_STEAM_NETWORKING_VTABLE_SLOT_COUNT (QLR_STEAM_NETWORKING_ACCEPT_P2P_SESSION_SLOT + 1)
#define QLR_STEAM_MATCHMAKING_ADD_FAVORITE_GAME_SLOT (0x08 / 4)
#define QLR_STEAM_MATCHMAKING_REMOVE_FAVORITE_GAME_SLOT (0x0c / 4)
#define QLR_STEAM_MATCHMAKING_CREATE_LOBBY_SLOT (0x34 / 4)
#define QLR_STEAM_MATCHMAKING_JOIN_LOBBY_SLOT (0x38 / 4)
#define QLR_STEAM_MATCHMAKING_LEAVE_LOBBY_SLOT (0x3c / 4)
#define QLR_STEAM_MATCHMAKING_INVITE_USER_TO_LOBBY_SLOT (0x40 / 4)
#define QLR_STEAM_MATCHMAKING_GET_NUM_LOBBY_MEMBERS_SLOT (0x44 / 4)
#define QLR_STEAM_MATCHMAKING_GET_LOBBY_MEMBER_BY_INDEX_SLOT (0x48 / 4)
#define QLR_STEAM_MATCHMAKING_SET_LOBBY_DATA_SLOT (0x50 / 4)
#define QLR_STEAM_MATCHMAKING_GET_LOBBY_DATA_COUNT_SLOT (0x54 / 4)
#define QLR_STEAM_MATCHMAKING_GET_LOBBY_DATA_BY_INDEX_SLOT (0x58 / 4)
#define QLR_STEAM_MATCHMAKING_SEND_LOBBY_CHAT_MSG_SLOT (0x68 / 4)
#define QLR_STEAM_MATCHMAKING_GET_LOBBY_CHAT_ENTRY_SLOT (0x6c / 4)
#define QLR_STEAM_MATCHMAKING_SET_LOBBY_GAME_SERVER_SLOT (0x74 / 4)
#define QLR_STEAM_MATCHMAKING_GET_LOBBY_MEMBER_LIMIT_SLOT (0x80 / 4)
#define QLR_STEAM_MATCHMAKING_GET_LOBBY_OWNER_SLOT (0x8c / 4)
#define QLR_STEAM_MATCHMAKING_VTABLE_SLOT_COUNT (QLR_STEAM_MATCHMAKING_GET_LOBBY_OWNER_SLOT + 1)
#define QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_INTERNET_SERVER_LIST_SLOT 0
#define QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_LAN_SERVER_LIST_SLOT (0x04 / 4)
#define QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_FRIENDS_SERVER_LIST_SLOT (0x08 / 4)
#define QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_FAVORITES_SERVER_LIST_SLOT (0x0c / 4)
#define QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_HISTORY_SERVER_LIST_SLOT (0x10 / 4)
#define QLR_STEAM_MATCHMAKING_SERVERS_RELEASE_REQUEST_SLOT (0x18 / 4)
#define QLR_STEAM_MATCHMAKING_SERVERS_GET_SERVER_DETAILS_SLOT (0x1c / 4)
#define QLR_STEAM_MATCHMAKING_SERVERS_REFRESH_QUERY_SLOT (0x24 / 4)
#define QLR_STEAM_MATCHMAKING_SERVERS_PING_SERVER_SLOT (0x34 / 4)
#define QLR_STEAM_MATCHMAKING_SERVERS_PLAYER_DETAILS_SLOT (0x38 / 4)
#define QLR_STEAM_MATCHMAKING_SERVERS_SERVER_RULES_SLOT (0x3c / 4)
#define QLR_STEAM_MATCHMAKING_SERVERS_CANCEL_SERVER_QUERY_SLOT (0x40 / 4)
#define QLR_STEAM_MATCHMAKING_SERVERS_VTABLE_SLOT_COUNT (QLR_STEAM_MATCHMAKING_SERVERS_CANCEL_SERVER_QUERY_SLOT + 1)
#define QLR_STEAM_GAMESERVER_SET_PRODUCT_SLOT (0x04 / 4)
#define QLR_STEAM_GAMESERVER_SET_GAME_DESCRIPTION_SLOT (0x08 / 4)
#define QLR_STEAM_GAMESERVER_SET_GAME_DIR_SLOT (0x0c / 4)
#define QLR_STEAM_GAMESERVER_SET_DEDICATED_SLOT (0x10 / 4)
#define QLR_STEAM_GAMESERVER_LOG_ON_SLOT (0x14 / 4)
#define QLR_STEAM_GAMESERVER_LOG_ON_ANONYMOUS_SLOT (0x18 / 4)
#define QLR_STEAM_GAMESERVER_BLOGGED_ON_SLOT (0x20 / 4)
#define QLR_STEAM_GAMESERVER_GET_STEAM_ID_SLOT (0x28 / 4)
#define QLR_STEAM_GAMESERVER_SET_MAX_PLAYER_COUNT_SLOT (0x30 / 4)
#define QLR_STEAM_GAMESERVER_SET_BOT_PLAYER_COUNT_SLOT (0x34 / 4)
#define QLR_STEAM_GAMESERVER_SET_SERVER_NAME_SLOT (0x38 / 4)
#define QLR_STEAM_GAMESERVER_SET_MAP_NAME_SLOT (0x3c / 4)
#define QLR_STEAM_GAMESERVER_SET_PASSWORD_PROTECTED_SLOT (0x40 / 4)
#define QLR_STEAM_GAMESERVER_SET_KEY_VALUE_SLOT (0x50 / 4)
#define QLR_STEAM_GAMESERVER_SET_GAME_TAGS_SLOT (0x54 / 4)
#define QLR_STEAM_GAMESERVER_CREATE_UNAUTHENTICATED_USER_SLOT (0x64 / 4)
#define QLR_STEAM_GAMESERVER_UPDATE_USER_DATA_SLOT (0x6c / 4)
#define QLR_STEAM_GAMESERVER_BEGIN_AUTH_SESSION_SLOT (0x74 / 4)
#define QLR_STEAM_GAMESERVER_END_AUTH_SESSION_SLOT (0x78 / 4)
#define QLR_STEAM_GAMESERVER_GET_PUBLIC_IP_SLOT (0x90 / 4)
#define QLR_STEAM_GAMESERVER_HANDLE_INCOMING_PACKET_SLOT (0x94 / 4)
#define QLR_STEAM_GAMESERVER_GET_NEXT_OUTGOING_PACKET_SLOT (0x98 / 4)
#define QLR_STEAM_GAMESERVER_ENABLE_HEARTBEATS_SLOT (0x9c / 4)
#define QLR_STEAM_GAMESERVER_VTABLE_SLOT_COUNT (QLR_STEAM_GAMESERVER_ENABLE_HEARTBEATS_SLOT + 1)
#define QLR_STEAM_GAMESERVER_UTILS_GET_APP_ID_SLOT (0x24 / 4)
#define QLR_STEAM_GAMESERVER_UTILS_VTABLE_SLOT_COUNT (QLR_STEAM_GAMESERVER_UTILS_GET_APP_ID_SLOT + 1)
#define QLR_STEAM_APPS_BIS_SUBSCRIBED_APP_SLOT (0x1c / 4)
#define QLR_STEAM_APPS_VTABLE_SLOT_COUNT (QLR_STEAM_APPS_BIS_SUBSCRIBED_APP_SLOT + 1)
#define QLR_STEAM_GAMESERVERSTATS_REQUEST_USER_STATS_SLOT 0
#define QLR_STEAM_GAMESERVERSTATS_GET_USER_STAT_FLOAT_SLOT (0x04 / 4)
#define QLR_STEAM_GAMESERVERSTATS_GET_USER_STAT_INT_SLOT (0x08 / 4)
#define QLR_STEAM_GAMESERVERSTATS_GET_USER_ACHIEVEMENT_SLOT (0x0c / 4)
#define QLR_STEAM_GAMESERVERSTATS_SET_USER_STAT_FLOAT_SLOT (0x10 / 4)
#define QLR_STEAM_GAMESERVERSTATS_SET_USER_STAT_INT_SLOT (0x14 / 4)
#define QLR_STEAM_GAMESERVERSTATS_UPDATE_AVG_RATE_STAT_SLOT (0x18 / 4)
#define QLR_STEAM_GAMESERVERSTATS_SET_USER_ACHIEVEMENT_SLOT (0x1c / 4)
#define QLR_STEAM_GAMESERVERSTATS_STORE_USER_STATS_SLOT (0x24 / 4)
#define QLR_STEAM_GAMESERVERSTATS_VTABLE_SLOT_COUNT (QLR_STEAM_GAMESERVERSTATS_STORE_USER_STATS_SLOT + 1)
#define QLR_STEAM_UGC_CREATE_QUERY_ALL_UGC_REQUEST_SLOT (0x04 / 4)
#define QLR_STEAM_UGC_SEND_QUERY_UGC_REQUEST_SLOT (0x0c / 4)
#define QLR_STEAM_UGC_GET_QUERY_UGC_RESULT_SLOT (0x10 / 4)
#define QLR_STEAM_UGC_GET_QUERY_UGC_PREVIEW_URL_SLOT (0x14 / 4)
#define QLR_STEAM_UGC_RELEASE_QUERY_UGC_REQUEST_SLOT (0x34 / 4)
#define QLR_STEAM_UGC_SUBSCRIBE_ITEM_SLOT (0xc0 / 4)
#define QLR_STEAM_UGC_UNSUBSCRIBE_ITEM_SLOT (0xc4 / 4)
#define QLR_STEAM_UGC_GET_NUM_SUBSCRIBED_ITEMS_SLOT (0xc8 / 4)
#define QLR_STEAM_UGC_GET_SUBSCRIBED_ITEMS_SLOT (0xcc / 4)
#define QLR_STEAM_UGC_GET_ITEM_STATE_SLOT (0xd0 / 4)
#define QLR_STEAM_UGC_GET_ITEM_INSTALL_INFO_SLOT (0xd4 / 4)
#define QLR_STEAM_UGC_GET_ITEM_DOWNLOAD_INFO_SLOT (0xd8 / 4)
#define QLR_STEAM_UGC_DOWNLOAD_ITEM_SLOT (0xdc / 4)
#define QLR_STEAM_UGC_VTABLE_SLOT_COUNT (QLR_STEAM_UGC_DOWNLOAD_ITEM_SLOT + 1)
#define QLR_STEAM_USER_BLOGGED_ON_SLOT (0x04 / 4)
#define QLR_STEAM_USER_GET_STEAM_ID_SLOT (0x08 / 4)
#define QLR_STEAM_USER_START_VOICE_RECORDING_SLOT (0x1c / 4)
#define QLR_STEAM_USER_STOP_VOICE_RECORDING_SLOT (0x20 / 4)
#define QLR_STEAM_USER_GET_VOICE_SLOT (0x28 / 4)
#define QLR_STEAM_USER_DECOMPRESS_VOICE_SLOT (0x2c / 4)
#define QLR_STEAM_USER_GET_VOICE_OPTIMAL_SAMPLE_RATE_SLOT (0x30 / 4)
#define QLR_STEAM_USER_VTABLE_SLOT_COUNT (QLR_STEAM_USER_GET_VOICE_OPTIMAL_SAMPLE_RATE_SLOT + 1)
#define QLR_STEAM_FRIENDS_GET_PERSONA_NAME_SLOT 0
#define QLR_STEAM_FRIENDS_GET_FRIEND_COUNT_SLOT (0x0c / 4)
#define QLR_STEAM_FRIENDS_GET_FRIEND_BY_INDEX_SLOT (0x10 / 4)
#define QLR_STEAM_FRIENDS_GET_FRIEND_RELATIONSHIP_SLOT (0x14 / 4)
#define QLR_STEAM_FRIENDS_GET_FRIEND_PERSONA_STATE_SLOT (0x18 / 4)
#define QLR_STEAM_FRIENDS_GET_FRIEND_PERSONA_NAME_SLOT (0x1c / 4)
#define QLR_STEAM_FRIENDS_GET_FRIEND_GAME_PLAYED_SLOT (0x20 / 4)
#define QLR_STEAM_FRIENDS_GET_PLAYER_NICKNAME_SLOT (0x2c / 4)
#define QLR_STEAM_FRIENDS_SET_IN_GAME_VOICE_SPEAKING_SLOT (0x6c / 4)
#define QLR_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_TO_USER_SLOT (0x74 / 4)
#define QLR_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_TO_WEB_PAGE_SLOT (0x78 / 4)
#define QLR_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_INVITE_DIALOG_SLOT (0x84 / 4)
#define QLR_STEAM_FRIENDS_GET_SMALL_FRIEND_AVATAR_SLOT (0x88 / 4)
#define QLR_STEAM_FRIENDS_GET_MEDIUM_FRIEND_AVATAR_SLOT (0x8c / 4)
#define QLR_STEAM_FRIENDS_GET_LARGE_FRIEND_AVATAR_SLOT (0x90 / 4)
#define QLR_STEAM_FRIENDS_SET_RICH_PRESENCE_SLOT (0xac / 4)
#define QLR_STEAM_FRIENDS_GET_FRIEND_RICH_PRESENCE_SLOT (0xb4 / 4)
#define QLR_STEAM_FRIENDS_INVITE_USER_TO_GAME_SLOT (0xc4 / 4)
#define QLR_STEAM_FRIENDS_VTABLE_SLOT_COUNT (QLR_STEAM_FRIENDS_INVITE_USER_TO_GAME_SLOT + 1)
#define QLR_STEAM_UTILS_GET_IP_COUNTRY_SLOT (0x10 / 4)
#define QLR_STEAM_UTILS_GET_IMAGE_SIZE_SLOT (0x14 / 4)
#define QLR_STEAM_UTILS_GET_IMAGE_RGBA_SLOT (0x18 / 4)
#define QLR_STEAM_UTILS_GET_APP_ID_SLOT (0x24 / 4)
#define QLR_STEAM_UTILS_VTABLE_SLOT_COUNT (QLR_STEAM_UTILS_GET_APP_ID_SLOT + 1)
#define QLR_STEAM_USERSTATS_GET_ACHIEVEMENT_DISPLAY_ATTRIBUTE_SLOT (0x30 / 4)
#define QLR_STEAM_USERSTATS_REQUEST_USER_STATS_SLOT (0x40 / 4)
#define QLR_STEAM_USERSTATS_GET_USER_STAT_FLOAT_SLOT (0x44 / 4)
#define QLR_STEAM_USERSTATS_GET_USER_STAT_INT_SLOT (0x48 / 4)
#define QLR_STEAM_USERSTATS_GET_USER_ACHIEVEMENT_SLOT (0x50 / 4)
#define QLR_STEAM_USERSTATS_RESET_ALL_STATS_SLOT (0x54 / 4)
#define QLR_STEAM_USERSTATS_VTABLE_SLOT_COUNT (QLR_STEAM_USERSTATS_RESET_ALL_STATS_SLOT + 1)

typedef struct qlr_callback_base_s qlr_callback_base_t;

typedef void (QLR_THISCALL *qlr_callback_run_fn)( qlr_callback_base_t *self, void *payload );
typedef void (QLR_THISCALL *qlr_callback_run_call_result_fn)( qlr_callback_base_t *self, void *payload, qboolean ioFailure, SteamAPICall_t callHandle );
typedef int (QLR_THISCALL *qlr_callback_get_size_fn)( qlr_callback_base_t *self );

typedef struct {
	qlr_callback_run_fn run;
	qlr_callback_run_call_result_fn runCallResult;
	qlr_callback_get_size_fn getSize;
} qlr_callback_vtable_t;

struct qlr_callback_base_s {
	const qlr_callback_vtable_t *vtable;
	uint8_t callbackFlags;
	uint8_t reserved[3];
	int callbackId;
};

typedef struct {
	qboolean callResult;
	void *object;
	int callbackId;
	SteamAPICall_t callHandle;
} qlr_callback_registration_t;

typedef struct {
	qboolean callResult;
	qboolean gameServer;
	int callbackId;
	SteamAPICall_t callHandle;
	qboolean ioFailure;
	uint32_t payloadSize;
	uint8_t payload[QLR_PENDING_CALLBACK_BUFFER];
} qlr_pending_callback_t;

typedef struct {
	HAuthTicket authTicket;
	int result;
	uint32_t ticketLength;
	uint8_t ticket[QL_STEAM_WEB_API_AUTH_TICKET_MAX_LENGTH];
} qlr_steam_get_ticket_for_web_api_response_raw_t;

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
} qlr_steam_gameserveritem_raw_t;

typedef struct {
	qboolean library_available;
	qboolean init_result;
	qboolean steam_api_init_export_available;
	qboolean steam_api_shutdown_export_available;
	qboolean steam_api_run_callbacks_export_available;
	qboolean steam_api_register_callback_export_available;
	qboolean steam_api_unregister_callback_export_available;
	qboolean steam_api_register_call_result_export_available;
	qboolean steam_api_unregister_call_result_export_available;
	qboolean steam_user_export_available;
	qboolean steam_friends_export_available;
	qboolean steam_utils_export_available;
	qboolean steam_user_stats_export_available;
	qboolean steam_networking_export_available;
	qboolean steam_matchmaking_export_available;
	qboolean steam_matchmaking_servers_export_available;
	qboolean steam_apps_export_available;
	qboolean steam_ugc_export_available;
	qboolean steam_game_server_export_available;
	qboolean steam_game_server_stats_export_available;
	qboolean steam_game_server_utils_export_available;
	qboolean steam_game_server_ugc_export_available;
	qboolean steam_game_server_init_export_available;
	qboolean steam_game_server_shutdown_export_available;
	qboolean steam_game_server_run_callbacks_export_available;
	qboolean steam_game_server_networking_export_available;
	qboolean user_available;
	qboolean user_logged_on_result;
	int user_logged_on_calls;
	EBeginAuthSessionResult auth_result;
	uint8_t ticket[QLR_TICKET_BUFFER];
	uint32_t ticket_length;
	HAuthTicket ticket_handle;
	qboolean auth_session_ticket_export_available;
	qboolean begin_auth_session_export_available;
	qboolean cancel_auth_ticket_export_available;
	qboolean end_auth_session_export_available;
	qboolean get_steam_id_export_available;
	uint8_t web_api_ticket[QLR_WEB_API_TICKET_BUFFER];
	uint32_t web_api_ticket_length;
	HAuthTicket web_api_ticket_handle;
	HAuthTicket web_api_ticket_callback_handle;
	uint32_t web_api_ticket_callback_length;
	qboolean web_api_ticket_queue_callback;
	qboolean web_api_ticket_export_available;
	int web_api_ticket_result;
	int web_api_ticket_calls;
	char web_api_ticket_identity[128];
	HAuthTicket cancelled_ticket_handle;
	int cancel_auth_ticket_calls;
	uint32_t app_id;
	uint64_t steam_id_value;
	int persona_name_calls;
	int user_steam_id_calls;
	int ip_country_calls;
	int app_id_calls;
	int steam_apps_interface_calls;
	int steam_apps_subscribed_result;
	uint32_t steam_apps_last_app_id;
	int friend_count;
	uint64_t friend_by_index_id;
	int friend_count_calls;
	int friend_last_count_flags;
	int friend_by_index_calls;
	int friend_last_index;
	int friend_last_index_flags;
	const char *persona_name;
	const char *friend_nickname;
	const char *friend_status;
	const char *friend_lan_ip;
	int friend_relationship;
	int friend_persona_state;
	uint64_t friend_game_id;
	uint32_t friend_game_ip;
	uint16_t friend_game_port;
	uint16_t friend_query_port;
	uint64_t friend_lobby_id;
	uint64_t friend_game_server_id;
	const char *ip_country;
	int avatar_handle_small;
	int avatar_handle_medium;
	int avatar_handle_large;
	uint32_t avatar_width;
	uint32_t avatar_height;
	uint8_t avatar_rgba[QLR_AVATAR_BUFFER];
	uint32_t avatar_rgba_length;
	char overlay_dialog[32];
	uint64_t overlay_steam_id;
	int overlay_calls;
	char overlay_web_url[256];
	int overlay_web_calls;
	char rich_presence_key[32];
	char rich_presence_value[128];
	int rich_presence_calls;
	int rich_presence_result;
	int friend_voice_speaking_calls;
	uint64_t friend_voice_last_steam_id;
	int friend_voice_last_speaking;
	int p2p_send_calls;
	uint64_t p2p_last_send_steam_id;
	uint8_t p2p_last_send_data[QLR_P2P_PACKET_BUFFER];
	uint32_t p2p_last_send_length;
	int p2p_last_send_type;
	int p2p_last_send_channel;
	int p2p_send_result;
	int p2p_available_calls;
	uint32_t p2p_available_size;
	int p2p_last_available_channel;
	int p2p_available_result;
	int p2p_read_calls;
	uint8_t p2p_read_data[QLR_P2P_PACKET_BUFFER];
	uint32_t p2p_read_length;
	uint64_t p2p_read_steam_id;
	int p2p_last_read_channel;
	int p2p_read_result;
	int p2p_accept_calls;
	uint64_t p2p_last_accept_steam_id;
	int p2p_accept_result;
	int voice_start_calls;
	int voice_stop_calls;
	int voice_get_calls;
	int voice_decompress_calls;
	int voice_optimal_rate_calls;
	uint8_t voice_compressed_data[QLR_VOICE_BUFFER];
	uint32_t voice_compressed_length;
	uint8_t voice_decompressed_data[QLR_VOICE_BUFFER];
	uint32_t voice_decompressed_length;
	int voice_get_result;
	int voice_decompress_result;
	uint32_t voice_optimal_sample_rate;
	int voice_last_want_compressed;
	int voice_last_want_uncompressed;
	uint32_t voice_last_compressed_buffer_size;
	uint32_t voice_last_uncompressed_buffer_size;
	uint32_t voice_last_decompress_input_size;
	uint32_t voice_last_decompress_buffer_size;
	uint32_t voice_last_decompress_sample_rate;
	int server_p2p_send_calls;
	uint64_t server_p2p_last_send_steam_id;
	uint8_t server_p2p_last_send_data[QLR_P2P_PACKET_BUFFER];
	uint32_t server_p2p_last_send_length;
	int server_p2p_last_send_type;
	int server_p2p_last_send_channel;
	int server_p2p_send_result;
	int server_p2p_available_calls;
	uint32_t server_p2p_available_size;
	int server_p2p_last_available_channel;
	int server_p2p_available_result;
	int server_p2p_read_calls;
	uint8_t server_p2p_read_data[QLR_P2P_PACKET_BUFFER];
	uint32_t server_p2p_read_length;
	uint64_t server_p2p_read_steam_id;
	int server_p2p_last_read_channel;
	int server_p2p_read_result;
	int server_p2p_accept_calls;
	uint64_t server_p2p_last_accept_steam_id;
	int server_p2p_accept_result;
	int steam_game_server_incoming_packet_calls;
	uint8_t steam_game_server_incoming_packet_data[QLR_P2P_PACKET_BUFFER];
	int steam_game_server_incoming_packet_length;
	uint32_t steam_game_server_incoming_packet_ip;
	uint16_t steam_game_server_incoming_packet_port;
	int steam_game_server_incoming_packet_result;
	int steam_game_server_outgoing_packet_calls;
	uint8_t steam_game_server_outgoing_packet_data[QLR_P2P_PACKET_BUFFER];
	int steam_game_server_outgoing_packet_length;
	uint32_t steam_game_server_outgoing_packet_ip;
	uint16_t steam_game_server_outgoing_packet_port;
	int steam_game_server_init_calls;
	int steam_game_server_shutdown_calls;
	int steam_game_server_init_result;
	int steam_game_server_logged_on_calls;
	int steam_game_server_logged_on_result;
	int steam_game_server_callback_calls;
	int steam_game_server_heartbeat_calls;
	int steam_game_server_last_heartbeat_enabled;
	int steam_game_server_key_value_calls;
	int steam_game_server_dedicated_calls;
	int steam_game_server_last_dedicated;
	int steam_game_server_logon_calls;
	int steam_game_server_logon_anonymous_calls;
	int steam_game_server_product_calls;
	int steam_game_server_game_dir_calls;
	int steam_game_server_game_description_calls;
	int steam_game_server_max_player_count_calls;
	int steam_game_server_bot_player_count_calls;
	int steam_game_server_server_name_calls;
	int steam_game_server_map_name_calls;
	int steam_game_server_password_calls;
	int steam_game_server_game_tags_calls;
	int steam_game_server_user_data_calls;
	uint64_t steam_game_server_id_value;
	uint64_t steam_game_server_unauthenticated_user_id_value;
	int steam_game_server_unauthenticated_user_calls;
	uint64_t steam_game_server_last_user_data_id;
	uint32_t steam_game_server_public_ip;
	uint32_t steam_game_server_last_user_data_score;
	int steam_game_server_stats_request_calls;
	int steam_game_server_stats_get_int_calls;
	int steam_game_server_stats_get_float_calls;
	int steam_game_server_stats_get_achievement_calls;
	int steam_game_server_stats_set_int_calls;
	int steam_game_server_stats_set_float_calls;
	int steam_game_server_stats_update_avg_rate_calls;
	int steam_game_server_stats_set_achievement_calls;
	int steam_game_server_stats_store_calls;
	qboolean steam_game_server_stats_available;
	int steam_game_server_stats_interface_calls;
	int steam_game_server_stats_result;
	int steam_game_server_stats_int_value;
	int steam_game_server_stats_last_int_value;
	qboolean steam_game_server_stats_achievement_value;
	float steam_game_server_stats_float_value;
	float steam_game_server_stats_last_float_value;
	float steam_game_server_stats_last_avg_count;
	double steam_game_server_stats_last_avg_session_length;
	uint64_t steam_game_server_stats_last_user_id;
	int steam_game_server_last_max_player_count;
	int steam_game_server_last_bot_player_count;
	int steam_game_server_last_password_protected;
	char steam_game_server_stats_last_name[128];
	char steam_game_server_last_key[MAX_INFO_KEY];
	char steam_game_server_last_value[MAX_INFO_VALUE];
	char steam_game_server_last_account[128];
	char steam_game_server_last_product[64];
	char steam_game_server_last_game_dir[64];
	char steam_game_server_last_game_description[64];
	char steam_game_server_last_server_name[128];
	char steam_game_server_last_map_name[64];
	char steam_game_server_last_game_tags[MAX_CVAR_VALUE_STRING];
	char steam_game_server_last_user_data_name[128];
	uint32_t steam_game_server_last_init_ip;
	uint16_t steam_game_server_last_init_steam_port;
	uint16_t steam_game_server_last_init_game_port;
	uint16_t steam_game_server_last_init_query_port;
	int steam_game_server_last_init_server_mode;
	char steam_game_server_last_init_version[32];
	int lobby_create_calls;
	int lobby_leave_calls;
	int lobby_join_calls;
	int lobby_invite_calls;
	int lobby_user_invite_calls;
	int lobby_say_calls;
	int lobby_set_server_calls;
	int favorite_add_calls;
	int favorite_remove_calls;
	int user_stats_request_calls;
	int user_stats_reset_calls;
	int user_stats_last_reset_achievements;
	int user_stats_get_int_calls;
	int user_stats_get_float_calls;
	int user_stats_get_achievement_calls;
	int user_stats_get_display_attribute_calls;
	int game_invite_calls;
	int lobby_create_type;
	int lobby_create_max_members;
	uint64_t lobby_leave_id;
	uint64_t lobby_join_id;
	uint64_t lobby_invite_id;
	uint64_t lobby_user_invite_lobby_id;
	uint64_t lobby_user_invite_target_id;
	uint64_t lobby_say_id;
	uint64_t lobby_set_server_id;
	uint64_t lobby_owner_id;
	uint64_t lobby_set_server_game_server_id;
	uint64_t game_invite_target_id;
	uint32_t lobby_set_server_ip;
	uint16_t lobby_set_server_port;
	uint32_t favorite_last_app_id;
	uint32_t favorite_last_ip;
	uint16_t favorite_last_conn_port;
	uint16_t favorite_last_query_port;
	uint32_t favorite_last_flags;
	uint32_t favorite_last_played;
	char lobby_say_message[256];
	char game_invite_connect_string[256];
	uint64_t user_stats_request_id;
	uint64_t user_stats_last_read_id;
	int user_stats_int_value;
	float user_stats_float_value;
	qboolean user_stats_achievement_value;
	int user_stats_unlock_time;
	uint64_t create_lobby_result;
	uint64_t join_lobby_result;
	int say_lobby_result;
	int favorite_add_result;
	int favorite_remove_result;
	uint64_t request_user_stats_result;
	int reset_user_stats_result;
	int user_stats_get_int_result;
	int user_stats_get_float_result;
	int user_stats_get_achievement_result;
	int user_stats_get_display_attribute_result;
	char user_stats_last_name[128];
	char user_stats_last_attribute_key[64];
	char user_stats_display_attribute_value[128];
	int server_browser_internet_calls;
	int server_browser_lan_calls;
	int server_browser_friends_calls;
	int server_browser_favorites_calls;
	int server_browser_history_calls;
	int server_browser_release_calls;
	int server_browser_refresh_calls;
	int server_browser_get_details_calls;
	int server_browser_ping_calls;
	int server_browser_players_calls;
	int server_browser_rules_calls;
	int server_browser_cancel_query_calls;
	int server_browser_detail_order;
	int server_browser_ping_order;
	int server_browser_players_order;
	int server_browser_rules_order;
	uint32_t server_browser_last_app_id;
	uint32_t server_browser_last_filter_count;
	char server_browser_last_filter_key[256];
	char server_browser_last_filter_value[256];
	uintptr_t server_browser_last_response;
	uintptr_t server_browser_last_request;
	int server_browser_last_index;
	uint32_t server_browser_last_ip;
	uint16_t server_browser_last_port;
	uintptr_t server_browser_last_ping_response;
	uintptr_t server_browser_last_players_response;
	uintptr_t server_browser_last_rules_response;
	int server_browser_last_cancel_query;
	uintptr_t server_browser_request_result;
	uintptr_t server_browser_details_result;
	qlr_steam_gameserveritem_raw_t server_browser_details;
	int server_browser_ping_query_result;
	int server_browser_players_query_result;
	int server_browser_rules_query_result;
	uint32_t ugc_item_state;
	uint64_t ugc_downloaded;
	uint64_t ugc_total;
	uint32_t ugc_subscribed_item_count;
	uint64_t ugc_subscribed_items[QLR_MAX_SUBSCRIBED_ITEMS];
	uint64_t ugc_install_item_id;
	uint64_t ugc_install_size_on_disk;
	char ugc_install_folder[MAX_OSPATH];
	uint32_t ugc_install_timestamp;
	int ugc_subscribe_calls;
	int ugc_unsubscribe_calls;
	int ugc_download_calls;
	uint64_t ugc_last_item_id;
	int ugc_last_high_priority;
	int ugc_create_query_calls;
	int ugc_send_query_calls;
	int ugc_release_query_calls;
	int ugc_get_query_result_calls;
	int ugc_get_query_preview_calls;
	int ugc_last_query_type;
	int ugc_last_matching_type;
	uint32_t ugc_last_creator_app_id;
	uint32_t ugc_last_consumer_app_id;
	uint32_t ugc_last_filter;
	uint64_t ugc_query_handle_result;
	uint64_t ugc_query_call_result;
	uint64_t ugc_last_query_handle;
	uint64_t ugc_last_sent_query_handle;
	uint64_t ugc_last_released_query_handle;
	uint64_t ugc_last_result_query_handle;
	uint64_t ugc_last_preview_query_handle;
	uint32_t ugc_last_result_index;
	uint32_t ugc_last_preview_index;
	uint64_t ugc_result_published_file_id;
	int ugc_query_result_success;
	int ugc_preview_success;
	char ugc_result_title[256];
	char ugc_result_description[512];
	char ugc_preview_url[512];
	int steam_game_server_ugc_subscribe_calls;
	int steam_game_server_ugc_unsubscribe_calls;
	int steam_game_server_ugc_download_calls;
	uint64_t steam_game_server_ugc_last_item_id;
	int steam_game_server_ugc_last_high_priority;
	char lobby_chat_entry_message[QL_STEAM_LOBBY_MESSAGE_LENGTH];
	int register_callback_calls;
	int unregister_callback_calls;
	int register_call_result_calls;
	int unregister_call_result_calls;
	int client_callback_capture_count;
	char last_callback_kind[64];
	char last_callback_text[256];
	uint64_t last_callback_id;
	uint64_t last_callback_aux_id;
	uint32_t last_callback_app_id;
	int last_callback_result;
	int registered_callback_count;
	int pending_callback_count;
	qlr_callback_registration_t registrations[QLR_MAX_CALLBACK_REGISTRATIONS];
	qlr_pending_callback_t pending_callbacks[QLR_MAX_PENDING_CALLBACKS];
} qlr_steamworks_mock_state_t;

typedef struct {
	void **vtable;
} qlr_steamworks_mock_interface_t;

typedef struct {
	char key[256];
	char value[256];
} qlr_matchmaking_key_value_pair_t;

static qlr_steamworks_mock_state_t qlr_mock_state = {
	.library_available = qtrue,
	.init_result = qtrue,
	.steam_api_init_export_available = qtrue,
	.steam_api_shutdown_export_available = qtrue,
	.steam_api_run_callbacks_export_available = qtrue,
	.steam_api_register_callback_export_available = qtrue,
	.steam_api_unregister_callback_export_available = qtrue,
	.steam_api_register_call_result_export_available = qtrue,
	.steam_api_unregister_call_result_export_available = qtrue,
	.steam_user_export_available = qtrue,
	.steam_friends_export_available = qtrue,
	.steam_utils_export_available = qtrue,
	.steam_user_stats_export_available = qtrue,
	.steam_networking_export_available = qtrue,
	.steam_matchmaking_export_available = qtrue,
	.steam_matchmaking_servers_export_available = qtrue,
	.steam_apps_export_available = qtrue,
	.steam_ugc_export_available = qtrue,
	.steam_game_server_export_available = qtrue,
	.steam_game_server_stats_export_available = qtrue,
	.steam_game_server_utils_export_available = qtrue,
	.steam_game_server_ugc_export_available = qtrue,
	.steam_game_server_init_export_available = qtrue,
	.steam_game_server_shutdown_export_available = qtrue,
	.steam_game_server_run_callbacks_export_available = qtrue,
	.steam_game_server_networking_export_available = qtrue,
	.user_available = qtrue,
	.user_logged_on_result = qtrue,
	.user_logged_on_calls = 0,
	.auth_result = k_EBeginAuthSessionResultOK,
	.ticket = { 0x12, 0x34, 0x56, 0x78 },
	.ticket_length = 4,
	.ticket_handle = 1,
	.auth_session_ticket_export_available = qtrue,
	.begin_auth_session_export_available = qtrue,
	.cancel_auth_ticket_export_available = qtrue,
	.end_auth_session_export_available = qtrue,
	.get_steam_id_export_available = qtrue,
	.web_api_ticket = { 0xAB, 0xCD, 0xEF },
	.web_api_ticket_length = 3,
	.web_api_ticket_handle = 41,
	.web_api_ticket_callback_handle = 41,
	.web_api_ticket_callback_length = 3,
	.web_api_ticket_queue_callback = qtrue,
	.web_api_ticket_export_available = qtrue,
	.web_api_ticket_result = QLR_STEAM_ERESULT_OK,
	.web_api_ticket_calls = 0,
	.web_api_ticket_identity = "",
	.cancelled_ticket_handle = 0,
	.cancel_auth_ticket_calls = 0,
	.app_id = 0x54100,
	.steam_id_value = 0xDEADBEEFULL,
	.persona_name_calls = 0,
	.user_steam_id_calls = 0,
	.ip_country_calls = 0,
	.app_id_calls = 0,
	.steam_apps_interface_calls = 0,
	.steam_apps_subscribed_result = qtrue,
	.steam_apps_last_app_id = 0u,
	.friend_count = 1,
	.friend_by_index_id = 0x0123456789ABCDEFULL,
	.friend_count_calls = 0,
	.friend_last_count_flags = -1,
	.friend_by_index_calls = 0,
	.friend_last_index = -1,
	.friend_last_index_flags = -1,
	.persona_name = "QLR Persona",
	.friend_nickname = "QLR Nick",
	.friend_status = "At the main menu",
	.friend_lan_ip = "",
	.friend_relationship = 3,
	.friend_persona_state = 1,
	.friend_game_id = 0x54100,
	.friend_game_ip = 0,
	.friend_game_port = 0,
	.friend_query_port = 0,
	.friend_lobby_id = 0,
	.friend_game_server_id = 0,
	.ip_country = "US",
	.avatar_handle_small = 11,
	.avatar_handle_medium = 12,
	.avatar_handle_large = 13,
	.avatar_width = 2,
	.avatar_height = 2,
	.avatar_rgba = {
		0x10, 0x20, 0x30, 0x40,
		0x50, 0x60, 0x70, 0x80,
		0x90, 0xA0, 0xB0, 0xC0,
		0xD0, 0xE0, 0xF0, 0xFF
	},
	.avatar_rgba_length = 16,
	.overlay_dialog = "",
	.overlay_steam_id = 0,
	.overlay_calls = 0,
	.overlay_web_url = "",
	.overlay_web_calls = 0,
	.rich_presence_key = "",
	.rich_presence_value = "",
	.rich_presence_calls = 0,
	.rich_presence_result = 1,
	.friend_voice_speaking_calls = 0,
	.friend_voice_last_steam_id = 0ull,
	.friend_voice_last_speaking = -1,
	.p2p_send_calls = 0,
	.p2p_last_send_steam_id = 0ull,
	.p2p_last_send_data = { 0 },
	.p2p_last_send_length = 0u,
	.p2p_last_send_type = 0,
	.p2p_last_send_channel = 0,
	.p2p_send_result = qtrue,
	.p2p_available_calls = 0,
	.p2p_available_size = 0u,
	.p2p_last_available_channel = 0,
	.p2p_available_result = qfalse,
	.p2p_read_calls = 0,
	.p2p_read_data = { 0 },
	.p2p_read_length = 0u,
	.p2p_read_steam_id = 0ull,
	.p2p_last_read_channel = 0,
	.p2p_read_result = qfalse,
	.p2p_accept_calls = 0,
	.p2p_last_accept_steam_id = 0ull,
	.p2p_accept_result = qtrue,
	.voice_start_calls = 0,
	.voice_stop_calls = 0,
	.voice_get_calls = 0,
	.voice_decompress_calls = 0,
	.voice_optimal_rate_calls = 0,
	.voice_compressed_data = { 0 },
	.voice_compressed_length = 0u,
	.voice_decompressed_data = { 0 },
	.voice_decompressed_length = 0u,
	.voice_get_result = 0,
	.voice_decompress_result = 0,
	.voice_optimal_sample_rate = 24000u,
	.voice_last_want_compressed = 0,
	.voice_last_want_uncompressed = 0,
	.voice_last_compressed_buffer_size = 0u,
	.voice_last_uncompressed_buffer_size = 0u,
	.voice_last_decompress_input_size = 0u,
	.voice_last_decompress_buffer_size = 0u,
	.voice_last_decompress_sample_rate = 0u,
	.server_p2p_send_calls = 0,
	.server_p2p_last_send_steam_id = 0ull,
	.server_p2p_last_send_data = { 0 },
	.server_p2p_last_send_length = 0u,
	.server_p2p_last_send_type = 0,
	.server_p2p_last_send_channel = 0,
	.server_p2p_send_result = qtrue,
	.server_p2p_available_calls = 0,
	.server_p2p_available_size = 0u,
	.server_p2p_last_available_channel = 0,
	.server_p2p_available_result = qfalse,
	.server_p2p_read_calls = 0,
	.server_p2p_read_data = { 0 },
	.server_p2p_read_length = 0u,
	.server_p2p_read_steam_id = 0ull,
	.server_p2p_last_read_channel = 0,
	.server_p2p_read_result = qfalse,
	.server_p2p_accept_calls = 0,
	.server_p2p_last_accept_steam_id = 0ull,
	.server_p2p_accept_result = qtrue,
	.steam_game_server_incoming_packet_calls = 0,
	.steam_game_server_incoming_packet_data = { 0 },
	.steam_game_server_incoming_packet_length = 0,
	.steam_game_server_incoming_packet_ip = 0u,
	.steam_game_server_incoming_packet_port = 0u,
	.steam_game_server_incoming_packet_result = qtrue,
	.steam_game_server_outgoing_packet_calls = 0,
	.steam_game_server_outgoing_packet_data = { 0 },
	.steam_game_server_outgoing_packet_length = 0,
	.steam_game_server_outgoing_packet_ip = 0u,
	.steam_game_server_outgoing_packet_port = 0u,
	.steam_game_server_init_calls = 0,
	.steam_game_server_shutdown_calls = 0,
	.steam_game_server_init_result = 1,
	.steam_game_server_logged_on_calls = 0,
	.steam_game_server_logged_on_result = qtrue,
	.steam_game_server_callback_calls = 0,
	.steam_game_server_heartbeat_calls = 0,
	.steam_game_server_last_heartbeat_enabled = -1,
	.steam_game_server_key_value_calls = 0,
	.steam_game_server_dedicated_calls = 0,
	.steam_game_server_last_dedicated = -1,
	.steam_game_server_logon_calls = 0,
	.steam_game_server_logon_anonymous_calls = 0,
	.steam_game_server_product_calls = 0,
	.steam_game_server_game_dir_calls = 0,
	.steam_game_server_game_description_calls = 0,
	.steam_game_server_max_player_count_calls = 0,
	.steam_game_server_bot_player_count_calls = 0,
	.steam_game_server_server_name_calls = 0,
	.steam_game_server_map_name_calls = 0,
	.steam_game_server_password_calls = 0,
	.steam_game_server_game_tags_calls = 0,
	.steam_game_server_user_data_calls = 0,
	.steam_game_server_id_value = 0x0123456789ABCDEFULL,
	.steam_game_server_unauthenticated_user_id_value = 0x0011223344556677ULL,
	.steam_game_server_unauthenticated_user_calls = 0,
	.steam_game_server_last_user_data_id = 0ULL,
	.steam_game_server_public_ip = 0x01020304,
	.steam_game_server_last_user_data_score = 0u,
	.steam_game_server_stats_request_calls = 0,
	.steam_game_server_stats_get_int_calls = 0,
	.steam_game_server_stats_get_float_calls = 0,
	.steam_game_server_stats_get_achievement_calls = 0,
	.steam_game_server_stats_set_int_calls = 0,
	.steam_game_server_stats_set_float_calls = 0,
	.steam_game_server_stats_update_avg_rate_calls = 0,
	.steam_game_server_stats_set_achievement_calls = 0,
	.steam_game_server_stats_store_calls = 0,
	.steam_game_server_stats_available = qtrue,
	.steam_game_server_stats_interface_calls = 0,
	.steam_game_server_stats_result = qtrue,
	.steam_game_server_stats_int_value = 0,
	.steam_game_server_stats_last_int_value = 0,
	.steam_game_server_stats_achievement_value = qfalse,
	.steam_game_server_stats_float_value = 0.0f,
	.steam_game_server_stats_last_float_value = 0.0f,
	.steam_game_server_stats_last_avg_count = 0.0f,
	.steam_game_server_stats_last_avg_session_length = 0.0,
	.steam_game_server_stats_last_user_id = 0ull,
	.steam_game_server_last_max_player_count = 0,
	.steam_game_server_last_bot_player_count = 0,
	.steam_game_server_last_password_protected = -1,
	.steam_game_server_stats_last_name = "",
	.steam_game_server_last_key = "",
	.steam_game_server_last_value = "",
	.steam_game_server_last_account = "",
	.steam_game_server_last_product = "",
	.steam_game_server_last_game_dir = "",
	.steam_game_server_last_game_description = "",
	.steam_game_server_last_server_name = "",
	.steam_game_server_last_map_name = "",
	.steam_game_server_last_game_tags = "",
	.steam_game_server_last_user_data_name = "",
	.steam_game_server_last_init_ip = 0u,
	.steam_game_server_last_init_steam_port = 0u,
	.steam_game_server_last_init_game_port = 0u,
	.steam_game_server_last_init_query_port = 0u,
	.steam_game_server_last_init_server_mode = 0,
	.steam_game_server_last_init_version = "",
	.lobby_create_calls = 0,
	.lobby_leave_calls = 0,
	.lobby_join_calls = 0,
	.lobby_invite_calls = 0,
	.lobby_say_calls = 0,
	.lobby_set_server_calls = 0,
	.user_stats_request_calls = 0,
	.user_stats_reset_calls = 0,
	.user_stats_last_reset_achievements = -1,
	.user_stats_get_int_calls = 0,
	.user_stats_get_float_calls = 0,
	.user_stats_get_achievement_calls = 0,
	.user_stats_get_display_attribute_calls = 0,
	.lobby_create_type = 0,
	.lobby_create_max_members = 0,
	.lobby_leave_id = 0,
	.lobby_join_id = 0,
	.lobby_invite_id = 0,
	.lobby_say_id = 0,
	.lobby_set_server_id = 0,
	.lobby_owner_id = 0xDEADBEEFULL,
	.lobby_set_server_game_server_id = 0,
	.lobby_set_server_ip = 0,
	.lobby_set_server_port = 0,
	.lobby_say_message = "",
	.user_stats_request_id = 0,
	.user_stats_last_read_id = 0,
	.user_stats_int_value = 0,
	.user_stats_float_value = 0.0f,
	.user_stats_achievement_value = qfalse,
	.user_stats_unlock_time = 0,
	.create_lobby_result = 1,
	.join_lobby_result = 1,
	.say_lobby_result = 1,
	.request_user_stats_result = 1,
	.reset_user_stats_result = 1,
	.user_stats_get_int_result = 1,
	.user_stats_get_float_result = 1,
	.user_stats_get_achievement_result = 1,
	.user_stats_get_display_attribute_result = 1,
	.user_stats_last_name = "",
	.user_stats_last_attribute_key = "",
	.user_stats_display_attribute_value = "QLR Display Attribute",
	.server_browser_internet_calls = 0,
	.server_browser_lan_calls = 0,
	.server_browser_friends_calls = 0,
	.server_browser_favorites_calls = 0,
	.server_browser_history_calls = 0,
	.server_browser_release_calls = 0,
	.server_browser_refresh_calls = 0,
	.server_browser_get_details_calls = 0,
	.server_browser_ping_calls = 0,
	.server_browser_players_calls = 0,
	.server_browser_rules_calls = 0,
	.server_browser_cancel_query_calls = 0,
	.server_browser_detail_order = 0,
	.server_browser_ping_order = 0,
	.server_browser_players_order = 0,
	.server_browser_rules_order = 0,
	.server_browser_last_app_id = 0u,
	.server_browser_last_filter_count = 0u,
	.server_browser_last_filter_key = "",
	.server_browser_last_filter_value = "",
	.server_browser_last_response = 0,
	.server_browser_last_request = 0,
	.server_browser_last_index = 0,
	.server_browser_last_ip = 0u,
	.server_browser_last_port = 0u,
	.server_browser_last_ping_response = 0,
	.server_browser_last_players_response = 0,
	.server_browser_last_rules_response = 0,
	.server_browser_last_cancel_query = 0,
	.server_browser_request_result = 0x13572468u,
	.server_browser_details_result = 0,
	.server_browser_details = {
		.connectionPort = 27960,
		.queryPort = 27961,
		.ip = 0x01020304u,
		.ping = 42,
		.hadSuccessfulResponse = 1,
		.doNotRefresh = 0,
		.gameDir = "baseq3",
		.map = "campgrounds",
		.gameDescription = "Clan Arena",
		.appIdPadding = { 0, 0 },
		.appId = 0x54100u,
		.players = 7,
		.maxPlayers = 16,
		.botPlayers = 2,
		.password = 1,
		.secure = 1,
		.lastPlayedPadding = { 0, 0 },
		.lastPlayed = 123456789u,
		.serverVersion = 1069,
		.serverName = "QLR Test Server",
		.gameTags = "duel,instagib",
		.steamIdLow = 0x89ABCDEFu,
		.steamIdHigh = 0x01234567u
	},
	.server_browser_ping_query_result = 11,
	.server_browser_players_query_result = 12,
	.server_browser_rules_query_result = 13,
	.ugc_item_state = 0,
	.ugc_downloaded = 0,
	.ugc_total = 0,
	.ugc_subscribed_item_count = 0,
	.ugc_subscribed_items = { 0 },
	.ugc_install_item_id = 0,
	.ugc_install_size_on_disk = 0,
	.ugc_install_folder = "",
	.ugc_install_timestamp = 0,
	.ugc_subscribe_calls = 0,
	.ugc_unsubscribe_calls = 0,
	.ugc_download_calls = 0,
	.ugc_last_item_id = 0,
	.ugc_last_high_priority = 0,
	.ugc_create_query_calls = 0,
	.ugc_send_query_calls = 0,
	.ugc_release_query_calls = 0,
	.ugc_get_query_result_calls = 0,
	.ugc_get_query_preview_calls = 0,
	.ugc_last_query_type = 0,
	.ugc_last_matching_type = 0,
	.ugc_last_creator_app_id = 0,
	.ugc_last_consumer_app_id = 0,
	.ugc_last_filter = 0,
	.ugc_query_handle_result = 0x1122334455667788ULL,
	.ugc_query_call_result = 0xAABBCCDDEEFF0011ULL,
	.ugc_last_query_handle = 0,
	.ugc_last_sent_query_handle = 0,
	.ugc_last_released_query_handle = 0,
	.ugc_last_result_query_handle = 0,
	.ugc_last_preview_query_handle = 0,
	.ugc_last_result_index = 0,
	.ugc_last_preview_index = 0,
	.ugc_result_published_file_id = 0x8877665544332211ULL,
	.ugc_query_result_success = qtrue,
	.ugc_preview_success = qtrue,
	.ugc_result_title = "QLR Workshop Item",
	.ugc_result_description = "Recovered UGC details",
	.ugc_preview_url = "https://cdn.example.test/preview.jpg",
	.steam_game_server_ugc_subscribe_calls = 0,
	.steam_game_server_ugc_unsubscribe_calls = 0,
	.steam_game_server_ugc_download_calls = 0,
	.steam_game_server_ugc_last_item_id = 0,
	.steam_game_server_ugc_last_high_priority = 0,
	.lobby_chat_entry_message = "",
	.register_callback_calls = 0,
	.unregister_callback_calls = 0,
	.register_call_result_calls = 0,
	.unregister_call_result_calls = 0,
	.client_callback_capture_count = 0,
	.last_callback_kind = "",
	.last_callback_text = "",
	.last_callback_id = 0,
	.last_callback_aux_id = 0,
	.last_callback_app_id = 0,
	.last_callback_result = 0,
	.registered_callback_count = 0,
	.pending_callback_count = 0
};

qboolean QLR_SteamAPI_Init( void );

void QLR_SteamAPI_Shutdown( void );

void QLR_SteamAPI_RunCallbacks( void );

void QLR_SteamAPI_RegisterCallback( void *object, int callbackId );

void QLR_SteamAPI_UnregisterCallback( void *object );

void QLR_SteamAPI_RegisterCallResult( void *object, SteamAPICall_t callHandle );

void QLR_SteamAPI_UnregisterCallResult( void *object, SteamAPICall_t callHandle );

void *QLR_SteamAPI_SteamUser( void );

void *QLR_SteamAPI_SteamFriends( void );

void *QLR_SteamAPI_SteamUtils( void );

void *QLR_SteamAPI_SteamApps( void );

void *QLR_SteamAPI_SteamUserStats( void );

void *QLR_SteamAPI_SteamNetworking( void );

void *QLR_SteamAPI_SteamMatchmaking( void );

void *QLR_SteamAPI_SteamMatchmakingServers( void );

void *QLR_SteamAPI_SteamUGC( void );

void *QLR_SteamAPI_SteamGameServerUGC( void );

qboolean QLR_SteamAPI_SteamGameServerInit( uint32_t ip, uint16_t steamPort, uint16_t gamePort, uint16_t queryPort, int serverMode, const char *version );

void *QLR_SteamAPI_SteamGameServer( void );

void *QLR_SteamAPI_SteamGameServerUtils( void );

void *QLR_SteamAPI_SteamGameServerStats( void );

void QLR_SteamAPI_SteamGameServerShutdown( void );

void QLR_SteamAPI_SteamGameServerRunCallbacks( void );

void *QLR_SteamAPI_SteamGameServerNetworking( void );

static CSteamID *QLR_FASTCALL QLR_SteamUser_GetSteamID( void *self, void *unused, CSteamID *outSteamId );

static EBeginAuthSessionResult QLR_FASTCALL QLR_SteamGameServer_BeginAuthSession( void *self, void *unused, const void *ticket, int length, CSteamID steamId );

static void QLR_FASTCALL QLR_SteamGameServer_EndAuthSession( void *self, void *unused, CSteamID steamId );

static qboolean QLR_FASTCALL QLR_SteamUser_BLoggedOn( void *self, void *unused );

static void QLR_FASTCALL QLR_SteamUser_StartVoiceRecording( void *self, void *unused );

static void QLR_FASTCALL QLR_SteamUser_StopVoiceRecording( void *self, void *unused );

static int QLR_FASTCALL QLR_SteamUser_GetVoice( void *self, void *unused, qboolean wantCompressed, void *destBuffer, uint32_t destBufferSize, uint32_t *outCompressedBytes, qboolean wantUncompressed, void *uncompressedBuffer, uint32_t uncompressedBufferSize, uint32_t *outUncompressedBytes, uint32_t uncompressedSampleRate );

static int QLR_FASTCALL QLR_SteamUser_DecompressVoice( void *self, void *unused, const void *compressedData, uint32_t compressedSize, void *destBuffer, uint32_t destBufferSize, uint32_t *outBytesWritten, uint32_t sampleRate );

static uint32_t QLR_FASTCALL QLR_SteamUser_GetVoiceOptimalSampleRate( void *self, void *unused );

static int QLR_FASTCALL QLR_SteamApps_BIsSubscribedApp( void *self, void *unused, uint32_t appId );

HAuthTicket QLR_SteamAPI_GetAuthSessionTicket( void *user, void *ticket, int ticket_size, uint32_t *length );

HAuthTicket QLR_SteamAPI_GetAuthTicketForWebApi( void *user, const char *identity );

EBeginAuthSessionResult QLR_SteamAPI_BeginAuthSession( void *user, const void *ticket, int length, CSteamID steamId );

void QLR_SteamAPI_CancelAuthTicket( void *user, HAuthTicket handle );

void QLR_SteamAPI_EndAuthSession( void *user, CSteamID steamId );

CSteamID QLR_SteamAPI_GetSteamID( void *user );

void Q_strncpyz( char *dest, const char *src, int destsize );

static qboolean QLR_SteamworksMock_QueueCallback( qboolean callResult, qboolean gameServer, int callbackId, SteamAPICall_t callHandle, const void *payload, uint32_t payloadSize, qboolean ioFailure );

/*
=============
qlower
=============
*/
static int qlower( int ch ) {
	return tolower( ch & 0xff );
}

/*
=============
QLR_SteamworksMock_ClearCallbackState
=============
*/
static void QLR_SteamworksMock_ClearCallbackState( void ) {
	qlr_mock_state.register_callback_calls = 0;
	qlr_mock_state.unregister_callback_calls = 0;
	qlr_mock_state.register_call_result_calls = 0;
	qlr_mock_state.unregister_call_result_calls = 0;
	qlr_mock_state.client_callback_capture_count = 0;
	qlr_mock_state.last_callback_kind[0] = '\0';
	qlr_mock_state.last_callback_text[0] = '\0';
	qlr_mock_state.last_callback_id = 0ull;
	qlr_mock_state.last_callback_aux_id = 0ull;
	qlr_mock_state.last_callback_app_id = 0u;
	qlr_mock_state.last_callback_result = 0;
	qlr_mock_state.registered_callback_count = 0;
	qlr_mock_state.pending_callback_count = 0;
	memset( qlr_mock_state.registrations, 0, sizeof( qlr_mock_state.registrations ) );
	memset( qlr_mock_state.pending_callbacks, 0, sizeof( qlr_mock_state.pending_callbacks ) );
}

/*
=============
QLR_SteamworksMock_ResetServerBrowserDetails

Restore the retained server-list row exposed by GetServerDetails.
=============
*/
static void QLR_SteamworksMock_ResetServerBrowserDetails( void ) {
	memset( &qlr_mock_state.server_browser_details, 0, sizeof( qlr_mock_state.server_browser_details ) );
	qlr_mock_state.server_browser_details.connectionPort = 27960;
	qlr_mock_state.server_browser_details.queryPort = 27961;
	qlr_mock_state.server_browser_details.ip = 0x01020304u;
	qlr_mock_state.server_browser_details.ping = 42;
	qlr_mock_state.server_browser_details.hadSuccessfulResponse = 1;
	qlr_mock_state.server_browser_details.doNotRefresh = 0;
	Q_strncpyz( qlr_mock_state.server_browser_details.gameDir, "baseq3", sizeof( qlr_mock_state.server_browser_details.gameDir ) );
	Q_strncpyz( qlr_mock_state.server_browser_details.map, "campgrounds", sizeof( qlr_mock_state.server_browser_details.map ) );
	Q_strncpyz( qlr_mock_state.server_browser_details.gameDescription, "Clan Arena", sizeof( qlr_mock_state.server_browser_details.gameDescription ) );
	qlr_mock_state.server_browser_details.appId = 0x54100u;
	qlr_mock_state.server_browser_details.players = 7;
	qlr_mock_state.server_browser_details.maxPlayers = 16;
	qlr_mock_state.server_browser_details.botPlayers = 2;
	qlr_mock_state.server_browser_details.password = 1;
	qlr_mock_state.server_browser_details.secure = 1;
	qlr_mock_state.server_browser_details.lastPlayed = 123456789u;
	qlr_mock_state.server_browser_details.serverVersion = 1069;
	Q_strncpyz( qlr_mock_state.server_browser_details.serverName, "QLR Test Server", sizeof( qlr_mock_state.server_browser_details.serverName ) );
	Q_strncpyz( qlr_mock_state.server_browser_details.gameTags, "duel,instagib", sizeof( qlr_mock_state.server_browser_details.gameTags ) );
	qlr_mock_state.server_browser_details.steamIdLow = 0x89ABCDEFu;
	qlr_mock_state.server_browser_details.steamIdHigh = 0x01234567u;
}

/*
=============
QLR_SteamworksMock_Reset

Restore default mock state for Steamworks entry points.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_Reset( void ) {
	qlr_mock_state.library_available = qtrue;
	qlr_mock_state.init_result = qtrue;
	qlr_mock_state.steam_api_init_export_available = qtrue;
	qlr_mock_state.steam_api_shutdown_export_available = qtrue;
	qlr_mock_state.steam_api_run_callbacks_export_available = qtrue;
	qlr_mock_state.steam_api_register_callback_export_available = qtrue;
	qlr_mock_state.steam_api_unregister_callback_export_available = qtrue;
	qlr_mock_state.steam_api_register_call_result_export_available = qtrue;
	qlr_mock_state.steam_api_unregister_call_result_export_available = qtrue;
	qlr_mock_state.steam_user_export_available = qtrue;
	qlr_mock_state.steam_friends_export_available = qtrue;
	qlr_mock_state.steam_utils_export_available = qtrue;
	qlr_mock_state.steam_user_stats_export_available = qtrue;
	qlr_mock_state.steam_networking_export_available = qtrue;
	qlr_mock_state.steam_matchmaking_export_available = qtrue;
	qlr_mock_state.steam_matchmaking_servers_export_available = qtrue;
	qlr_mock_state.steam_apps_export_available = qtrue;
	qlr_mock_state.steam_ugc_export_available = qtrue;
	qlr_mock_state.steam_game_server_export_available = qtrue;
	qlr_mock_state.steam_game_server_stats_export_available = qtrue;
	qlr_mock_state.steam_game_server_utils_export_available = qtrue;
	qlr_mock_state.steam_game_server_ugc_export_available = qtrue;
	qlr_mock_state.steam_game_server_init_export_available = qtrue;
	qlr_mock_state.steam_game_server_shutdown_export_available = qtrue;
	qlr_mock_state.steam_game_server_run_callbacks_export_available = qtrue;
	qlr_mock_state.steam_game_server_networking_export_available = qtrue;
	qlr_mock_state.user_available = qtrue;
	qlr_mock_state.user_logged_on_result = qtrue;
	qlr_mock_state.user_logged_on_calls = 0;
	qlr_mock_state.auth_result = k_EBeginAuthSessionResultOK;
	memcpy( qlr_mock_state.ticket, (uint8_t[]){ 0x12, 0x34, 0x56, 0x78 }, 4 );
	qlr_mock_state.ticket_length = 4;
	qlr_mock_state.ticket_handle = 1;
	qlr_mock_state.auth_session_ticket_export_available = qtrue;
	qlr_mock_state.begin_auth_session_export_available = qtrue;
	qlr_mock_state.cancel_auth_ticket_export_available = qtrue;
	qlr_mock_state.end_auth_session_export_available = qtrue;
	qlr_mock_state.get_steam_id_export_available = qtrue;
	memcpy( qlr_mock_state.web_api_ticket, (uint8_t[]){ 0xAB, 0xCD, 0xEF }, 3 );
	qlr_mock_state.web_api_ticket_length = 3;
	qlr_mock_state.web_api_ticket_handle = 41;
	qlr_mock_state.web_api_ticket_callback_handle = 41;
	qlr_mock_state.web_api_ticket_callback_length = 3;
	qlr_mock_state.web_api_ticket_queue_callback = qtrue;
	qlr_mock_state.web_api_ticket_export_available = qtrue;
	qlr_mock_state.web_api_ticket_result = QLR_STEAM_ERESULT_OK;
	qlr_mock_state.web_api_ticket_calls = 0;
	qlr_mock_state.web_api_ticket_identity[0] = '\0';
	qlr_mock_state.cancelled_ticket_handle = 0;
	qlr_mock_state.cancel_auth_ticket_calls = 0;
	qlr_mock_state.app_id = 0x54100;
	qlr_mock_state.steam_id_value = 0xDEADBEEFULL;
	qlr_mock_state.persona_name_calls = 0;
	qlr_mock_state.user_steam_id_calls = 0;
	qlr_mock_state.ip_country_calls = 0;
	qlr_mock_state.app_id_calls = 0;
	qlr_mock_state.steam_apps_interface_calls = 0;
	qlr_mock_state.steam_apps_subscribed_result = qtrue;
	qlr_mock_state.steam_apps_last_app_id = 0u;
	qlr_mock_state.friend_count = 1;
	qlr_mock_state.friend_by_index_id = 0x0123456789ABCDEFULL;
	qlr_mock_state.friend_count_calls = 0;
	qlr_mock_state.friend_last_count_flags = -1;
	qlr_mock_state.friend_by_index_calls = 0;
	qlr_mock_state.friend_last_index = -1;
	qlr_mock_state.friend_last_index_flags = -1;
	qlr_mock_state.persona_name = "QLR Persona";
	qlr_mock_state.friend_nickname = "QLR Nick";
	qlr_mock_state.friend_status = "At the main menu";
	qlr_mock_state.friend_lan_ip = "";
	qlr_mock_state.friend_relationship = 3;
	qlr_mock_state.friend_persona_state = 1;
	qlr_mock_state.friend_game_id = 0x54100;
	qlr_mock_state.friend_game_ip = 0;
	qlr_mock_state.friend_game_port = 0;
	qlr_mock_state.friend_query_port = 0;
	qlr_mock_state.friend_lobby_id = 0;
	qlr_mock_state.friend_game_server_id = 0;
	qlr_mock_state.ip_country = "US";
	qlr_mock_state.avatar_handle_small = 11;
	qlr_mock_state.avatar_handle_medium = 12;
	qlr_mock_state.avatar_handle_large = 13;
	qlr_mock_state.avatar_width = 2;
	qlr_mock_state.avatar_height = 2;
	memcpy( qlr_mock_state.avatar_rgba, (uint8_t[]){
		0x10, 0x20, 0x30, 0x40,
		0x50, 0x60, 0x70, 0x80,
		0x90, 0xA0, 0xB0, 0xC0,
		0xD0, 0xE0, 0xF0, 0xFF
	}, 16 );
	qlr_mock_state.avatar_rgba_length = 16;
	qlr_mock_state.overlay_dialog[0] = '\0';
	qlr_mock_state.overlay_steam_id = 0;
	qlr_mock_state.overlay_calls = 0;
	qlr_mock_state.overlay_web_url[0] = '\0';
	qlr_mock_state.overlay_web_calls = 0;
	qlr_mock_state.rich_presence_key[0] = '\0';
	qlr_mock_state.rich_presence_value[0] = '\0';
	qlr_mock_state.rich_presence_calls = 0;
	qlr_mock_state.rich_presence_result = 1;
	qlr_mock_state.friend_voice_speaking_calls = 0;
	qlr_mock_state.friend_voice_last_steam_id = 0ull;
	qlr_mock_state.friend_voice_last_speaking = -1;
	qlr_mock_state.p2p_send_calls = 0;
	qlr_mock_state.p2p_last_send_steam_id = 0ull;
	memset( qlr_mock_state.p2p_last_send_data, 0, sizeof( qlr_mock_state.p2p_last_send_data ) );
	qlr_mock_state.p2p_last_send_length = 0u;
	qlr_mock_state.p2p_last_send_type = 0;
	qlr_mock_state.p2p_last_send_channel = 0;
	qlr_mock_state.p2p_send_result = qtrue;
	qlr_mock_state.p2p_available_calls = 0;
	qlr_mock_state.p2p_available_size = 0u;
	qlr_mock_state.p2p_last_available_channel = 0;
	qlr_mock_state.p2p_available_result = qfalse;
	qlr_mock_state.p2p_read_calls = 0;
	memset( qlr_mock_state.p2p_read_data, 0, sizeof( qlr_mock_state.p2p_read_data ) );
	qlr_mock_state.p2p_read_length = 0u;
	qlr_mock_state.p2p_read_steam_id = 0ull;
	qlr_mock_state.p2p_last_read_channel = 0;
	qlr_mock_state.p2p_read_result = qfalse;
	qlr_mock_state.p2p_accept_calls = 0;
	qlr_mock_state.p2p_last_accept_steam_id = 0ull;
	qlr_mock_state.p2p_accept_result = qtrue;
	qlr_mock_state.voice_start_calls = 0;
	qlr_mock_state.voice_stop_calls = 0;
	qlr_mock_state.voice_get_calls = 0;
	qlr_mock_state.voice_decompress_calls = 0;
	qlr_mock_state.voice_optimal_rate_calls = 0;
	memset( qlr_mock_state.voice_compressed_data, 0, sizeof( qlr_mock_state.voice_compressed_data ) );
	qlr_mock_state.voice_compressed_length = 0u;
	memset( qlr_mock_state.voice_decompressed_data, 0, sizeof( qlr_mock_state.voice_decompressed_data ) );
	qlr_mock_state.voice_decompressed_length = 0u;
	qlr_mock_state.voice_get_result = 0;
	qlr_mock_state.voice_decompress_result = 0;
	qlr_mock_state.voice_optimal_sample_rate = 24000u;
	qlr_mock_state.voice_last_want_compressed = 0;
	qlr_mock_state.voice_last_want_uncompressed = 0;
	qlr_mock_state.voice_last_compressed_buffer_size = 0u;
	qlr_mock_state.voice_last_uncompressed_buffer_size = 0u;
	qlr_mock_state.voice_last_decompress_input_size = 0u;
	qlr_mock_state.voice_last_decompress_buffer_size = 0u;
	qlr_mock_state.voice_last_decompress_sample_rate = 0u;
	qlr_mock_state.server_p2p_send_calls = 0;
	qlr_mock_state.server_p2p_last_send_steam_id = 0ull;
	memset( qlr_mock_state.server_p2p_last_send_data, 0, sizeof( qlr_mock_state.server_p2p_last_send_data ) );
	qlr_mock_state.server_p2p_last_send_length = 0u;
	qlr_mock_state.server_p2p_last_send_type = 0;
	qlr_mock_state.server_p2p_last_send_channel = 0;
	qlr_mock_state.server_p2p_send_result = qtrue;
	qlr_mock_state.server_p2p_available_calls = 0;
	qlr_mock_state.server_p2p_available_size = 0u;
	qlr_mock_state.server_p2p_last_available_channel = 0;
	qlr_mock_state.server_p2p_available_result = qfalse;
	qlr_mock_state.server_p2p_read_calls = 0;
	memset( qlr_mock_state.server_p2p_read_data, 0, sizeof( qlr_mock_state.server_p2p_read_data ) );
	qlr_mock_state.server_p2p_read_length = 0u;
	qlr_mock_state.server_p2p_read_steam_id = 0ull;
	qlr_mock_state.server_p2p_last_read_channel = 0;
	qlr_mock_state.server_p2p_read_result = qfalse;
	qlr_mock_state.server_p2p_accept_calls = 0;
	qlr_mock_state.server_p2p_last_accept_steam_id = 0ull;
	qlr_mock_state.server_p2p_accept_result = qtrue;
	qlr_mock_state.steam_game_server_incoming_packet_calls = 0;
	memset( qlr_mock_state.steam_game_server_incoming_packet_data, 0, sizeof( qlr_mock_state.steam_game_server_incoming_packet_data ) );
	qlr_mock_state.steam_game_server_incoming_packet_length = 0;
	qlr_mock_state.steam_game_server_incoming_packet_ip = 0u;
	qlr_mock_state.steam_game_server_incoming_packet_port = 0u;
	qlr_mock_state.steam_game_server_incoming_packet_result = qtrue;
	qlr_mock_state.steam_game_server_outgoing_packet_calls = 0;
	memset( qlr_mock_state.steam_game_server_outgoing_packet_data, 0, sizeof( qlr_mock_state.steam_game_server_outgoing_packet_data ) );
	qlr_mock_state.steam_game_server_outgoing_packet_length = 0;
	qlr_mock_state.steam_game_server_outgoing_packet_ip = 0u;
	qlr_mock_state.steam_game_server_outgoing_packet_port = 0u;
	qlr_mock_state.steam_game_server_init_calls = 0;
	qlr_mock_state.steam_game_server_shutdown_calls = 0;
	qlr_mock_state.steam_game_server_init_result = 1;
	qlr_mock_state.steam_game_server_logged_on_calls = 0;
	qlr_mock_state.steam_game_server_logged_on_result = qtrue;
	qlr_mock_state.steam_game_server_callback_calls = 0;
	qlr_mock_state.steam_game_server_heartbeat_calls = 0;
	qlr_mock_state.steam_game_server_last_heartbeat_enabled = -1;
	qlr_mock_state.steam_game_server_key_value_calls = 0;
	qlr_mock_state.steam_game_server_dedicated_calls = 0;
	qlr_mock_state.steam_game_server_last_dedicated = -1;
	qlr_mock_state.steam_game_server_logon_calls = 0;
	qlr_mock_state.steam_game_server_logon_anonymous_calls = 0;
	qlr_mock_state.steam_game_server_product_calls = 0;
	qlr_mock_state.steam_game_server_game_dir_calls = 0;
	qlr_mock_state.steam_game_server_game_description_calls = 0;
	qlr_mock_state.steam_game_server_max_player_count_calls = 0;
	qlr_mock_state.steam_game_server_bot_player_count_calls = 0;
	qlr_mock_state.steam_game_server_server_name_calls = 0;
	qlr_mock_state.steam_game_server_map_name_calls = 0;
	qlr_mock_state.steam_game_server_password_calls = 0;
	qlr_mock_state.steam_game_server_game_tags_calls = 0;
	qlr_mock_state.steam_game_server_user_data_calls = 0;
	qlr_mock_state.steam_game_server_id_value = 0x0123456789ABCDEFULL;
	qlr_mock_state.steam_game_server_unauthenticated_user_id_value = 0x0011223344556677ULL;
	qlr_mock_state.steam_game_server_unauthenticated_user_calls = 0;
	qlr_mock_state.steam_game_server_last_user_data_id = 0ULL;
	qlr_mock_state.steam_game_server_public_ip = 0x01020304;
	qlr_mock_state.steam_game_server_last_user_data_score = 0u;
	qlr_mock_state.steam_game_server_stats_request_calls = 0;
	qlr_mock_state.steam_game_server_stats_get_int_calls = 0;
	qlr_mock_state.steam_game_server_stats_get_float_calls = 0;
	qlr_mock_state.steam_game_server_stats_get_achievement_calls = 0;
	qlr_mock_state.steam_game_server_stats_set_int_calls = 0;
	qlr_mock_state.steam_game_server_stats_set_float_calls = 0;
	qlr_mock_state.steam_game_server_stats_update_avg_rate_calls = 0;
	qlr_mock_state.steam_game_server_stats_set_achievement_calls = 0;
	qlr_mock_state.steam_game_server_stats_store_calls = 0;
	qlr_mock_state.steam_game_server_stats_available = qtrue;
	qlr_mock_state.steam_game_server_stats_interface_calls = 0;
	qlr_mock_state.steam_game_server_stats_result = qtrue;
	qlr_mock_state.steam_game_server_stats_int_value = 0;
	qlr_mock_state.steam_game_server_stats_last_int_value = 0;
	qlr_mock_state.steam_game_server_stats_achievement_value = qfalse;
	qlr_mock_state.steam_game_server_stats_float_value = 0.0f;
	qlr_mock_state.steam_game_server_stats_last_float_value = 0.0f;
	qlr_mock_state.steam_game_server_stats_last_avg_count = 0.0f;
	qlr_mock_state.steam_game_server_stats_last_avg_session_length = 0.0;
	qlr_mock_state.steam_game_server_stats_last_user_id = 0ull;
	qlr_mock_state.steam_game_server_last_max_player_count = 0;
	qlr_mock_state.steam_game_server_last_bot_player_count = 0;
	qlr_mock_state.steam_game_server_last_password_protected = -1;
	qlr_mock_state.steam_game_server_stats_last_name[0] = '\0';
	qlr_mock_state.steam_game_server_last_key[0] = '\0';
	qlr_mock_state.steam_game_server_last_value[0] = '\0';
	qlr_mock_state.steam_game_server_last_account[0] = '\0';
	qlr_mock_state.steam_game_server_last_product[0] = '\0';
	qlr_mock_state.steam_game_server_last_game_dir[0] = '\0';
	qlr_mock_state.steam_game_server_last_game_description[0] = '\0';
	qlr_mock_state.steam_game_server_last_server_name[0] = '\0';
	qlr_mock_state.steam_game_server_last_map_name[0] = '\0';
	qlr_mock_state.steam_game_server_last_game_tags[0] = '\0';
	qlr_mock_state.steam_game_server_last_user_data_name[0] = '\0';
	qlr_mock_state.steam_game_server_last_init_ip = 0u;
	qlr_mock_state.steam_game_server_last_init_steam_port = 0u;
	qlr_mock_state.steam_game_server_last_init_game_port = 0u;
	qlr_mock_state.steam_game_server_last_init_query_port = 0u;
	qlr_mock_state.steam_game_server_last_init_server_mode = 0;
	qlr_mock_state.steam_game_server_last_init_version[0] = '\0';
	qlr_mock_state.lobby_create_calls = 0;
	qlr_mock_state.lobby_leave_calls = 0;
	qlr_mock_state.lobby_join_calls = 0;
	qlr_mock_state.lobby_invite_calls = 0;
	qlr_mock_state.lobby_user_invite_calls = 0;
	qlr_mock_state.lobby_say_calls = 0;
	qlr_mock_state.lobby_set_server_calls = 0;
	qlr_mock_state.favorite_add_calls = 0;
	qlr_mock_state.favorite_remove_calls = 0;
	qlr_mock_state.user_stats_request_calls = 0;
	qlr_mock_state.user_stats_reset_calls = 0;
	qlr_mock_state.user_stats_last_reset_achievements = -1;
	qlr_mock_state.user_stats_get_int_calls = 0;
	qlr_mock_state.user_stats_get_float_calls = 0;
	qlr_mock_state.user_stats_get_achievement_calls = 0;
	qlr_mock_state.user_stats_get_display_attribute_calls = 0;
	qlr_mock_state.game_invite_calls = 0;
	qlr_mock_state.lobby_create_type = 0;
	qlr_mock_state.lobby_create_max_members = 0;
	qlr_mock_state.lobby_leave_id = 0;
	qlr_mock_state.lobby_join_id = 0;
	qlr_mock_state.lobby_invite_id = 0;
	qlr_mock_state.lobby_user_invite_lobby_id = 0;
	qlr_mock_state.lobby_user_invite_target_id = 0;
	qlr_mock_state.lobby_say_id = 0;
	qlr_mock_state.lobby_set_server_id = 0;
	qlr_mock_state.lobby_owner_id = qlr_mock_state.steam_id_value;
	qlr_mock_state.lobby_set_server_game_server_id = 0;
	qlr_mock_state.game_invite_target_id = 0;
	qlr_mock_state.lobby_set_server_ip = 0;
	qlr_mock_state.lobby_set_server_port = 0;
	qlr_mock_state.favorite_last_app_id = 0u;
	qlr_mock_state.favorite_last_ip = 0u;
	qlr_mock_state.favorite_last_conn_port = 0u;
	qlr_mock_state.favorite_last_query_port = 0u;
	qlr_mock_state.favorite_last_flags = 0u;
	qlr_mock_state.favorite_last_played = 0u;
	qlr_mock_state.lobby_say_message[0] = '\0';
	qlr_mock_state.game_invite_connect_string[0] = '\0';
	qlr_mock_state.user_stats_request_id = 0;
	qlr_mock_state.user_stats_last_read_id = 0;
	qlr_mock_state.user_stats_int_value = 0;
	qlr_mock_state.user_stats_float_value = 0.0f;
	qlr_mock_state.user_stats_achievement_value = qfalse;
	qlr_mock_state.user_stats_unlock_time = 0;
	qlr_mock_state.create_lobby_result = 1;
	qlr_mock_state.join_lobby_result = 1;
	qlr_mock_state.say_lobby_result = 1;
	qlr_mock_state.favorite_add_result = 1;
	qlr_mock_state.favorite_remove_result = qtrue;
	qlr_mock_state.request_user_stats_result = 1;
	qlr_mock_state.reset_user_stats_result = 1;
	qlr_mock_state.user_stats_get_int_result = 1;
	qlr_mock_state.user_stats_get_float_result = 1;
	qlr_mock_state.user_stats_get_achievement_result = 1;
	qlr_mock_state.user_stats_get_display_attribute_result = 1;
	qlr_mock_state.user_stats_last_name[0] = '\0';
	qlr_mock_state.user_stats_last_attribute_key[0] = '\0';
	Q_strncpyz( qlr_mock_state.user_stats_display_attribute_value, "QLR Display Attribute", sizeof( qlr_mock_state.user_stats_display_attribute_value ) );
	qlr_mock_state.server_browser_internet_calls = 0;
	qlr_mock_state.server_browser_lan_calls = 0;
	qlr_mock_state.server_browser_friends_calls = 0;
	qlr_mock_state.server_browser_favorites_calls = 0;
	qlr_mock_state.server_browser_history_calls = 0;
	qlr_mock_state.server_browser_release_calls = 0;
	qlr_mock_state.server_browser_refresh_calls = 0;
	qlr_mock_state.server_browser_get_details_calls = 0;
	qlr_mock_state.server_browser_ping_calls = 0;
	qlr_mock_state.server_browser_players_calls = 0;
	qlr_mock_state.server_browser_rules_calls = 0;
	qlr_mock_state.server_browser_cancel_query_calls = 0;
	qlr_mock_state.server_browser_detail_order = 0;
	qlr_mock_state.server_browser_ping_order = 0;
	qlr_mock_state.server_browser_players_order = 0;
	qlr_mock_state.server_browser_rules_order = 0;
	qlr_mock_state.server_browser_last_app_id = 0u;
	qlr_mock_state.server_browser_last_filter_count = 0u;
	qlr_mock_state.server_browser_last_filter_key[0] = '\0';
	qlr_mock_state.server_browser_last_filter_value[0] = '\0';
	qlr_mock_state.server_browser_last_response = 0;
	qlr_mock_state.server_browser_last_request = 0;
	qlr_mock_state.server_browser_last_index = 0;
	qlr_mock_state.server_browser_last_ip = 0u;
	qlr_mock_state.server_browser_last_port = 0u;
	qlr_mock_state.server_browser_last_ping_response = 0;
	qlr_mock_state.server_browser_last_players_response = 0;
	qlr_mock_state.server_browser_last_rules_response = 0;
	qlr_mock_state.server_browser_last_cancel_query = 0;
	qlr_mock_state.server_browser_request_result = 0x13572468u;
	qlr_mock_state.server_browser_details_result = 0;
	QLR_SteamworksMock_ResetServerBrowserDetails();
	qlr_mock_state.server_browser_ping_query_result = 11;
	qlr_mock_state.server_browser_players_query_result = 12;
	qlr_mock_state.server_browser_rules_query_result = 13;
	qlr_mock_state.ugc_item_state = 0;
	qlr_mock_state.ugc_downloaded = 0;
	qlr_mock_state.ugc_total = 0;
	qlr_mock_state.ugc_subscribed_item_count = 0u;
	memset( qlr_mock_state.ugc_subscribed_items, 0, sizeof( qlr_mock_state.ugc_subscribed_items ) );
	qlr_mock_state.ugc_install_item_id = 0ull;
	qlr_mock_state.ugc_install_size_on_disk = 0ull;
	qlr_mock_state.ugc_install_folder[0] = '\0';
	qlr_mock_state.ugc_install_timestamp = 0u;
	qlr_mock_state.ugc_subscribe_calls = 0;
	qlr_mock_state.ugc_unsubscribe_calls = 0;
	qlr_mock_state.ugc_download_calls = 0;
	qlr_mock_state.ugc_last_item_id = 0;
	qlr_mock_state.ugc_last_high_priority = 0;
	qlr_mock_state.ugc_create_query_calls = 0;
	qlr_mock_state.ugc_send_query_calls = 0;
	qlr_mock_state.ugc_release_query_calls = 0;
	qlr_mock_state.ugc_get_query_result_calls = 0;
	qlr_mock_state.ugc_get_query_preview_calls = 0;
	qlr_mock_state.ugc_last_query_type = 0;
	qlr_mock_state.ugc_last_matching_type = 0;
	qlr_mock_state.ugc_last_creator_app_id = 0u;
	qlr_mock_state.ugc_last_consumer_app_id = 0u;
	qlr_mock_state.ugc_last_filter = 0u;
	qlr_mock_state.ugc_query_handle_result = 0x1122334455667788ULL;
	qlr_mock_state.ugc_query_call_result = 0xAABBCCDDEEFF0011ULL;
	qlr_mock_state.ugc_last_query_handle = 0ull;
	qlr_mock_state.ugc_last_sent_query_handle = 0ull;
	qlr_mock_state.ugc_last_released_query_handle = 0ull;
	qlr_mock_state.ugc_last_result_query_handle = 0ull;
	qlr_mock_state.ugc_last_preview_query_handle = 0ull;
	qlr_mock_state.ugc_last_result_index = 0u;
	qlr_mock_state.ugc_last_preview_index = 0u;
	qlr_mock_state.ugc_result_published_file_id = 0x8877665544332211ULL;
	qlr_mock_state.ugc_query_result_success = qtrue;
	qlr_mock_state.ugc_preview_success = qtrue;
	Q_strncpyz( qlr_mock_state.ugc_result_title, "QLR Workshop Item", sizeof( qlr_mock_state.ugc_result_title ) );
	Q_strncpyz( qlr_mock_state.ugc_result_description, "Recovered UGC details", sizeof( qlr_mock_state.ugc_result_description ) );
	Q_strncpyz( qlr_mock_state.ugc_preview_url, "https://cdn.example.test/preview.jpg", sizeof( qlr_mock_state.ugc_preview_url ) );
	qlr_mock_state.steam_game_server_ugc_subscribe_calls = 0;
	qlr_mock_state.steam_game_server_ugc_unsubscribe_calls = 0;
	qlr_mock_state.steam_game_server_ugc_download_calls = 0;
	qlr_mock_state.steam_game_server_ugc_last_item_id = 0;
	qlr_mock_state.steam_game_server_ugc_last_high_priority = 0;
	qlr_mock_state.lobby_chat_entry_message[0] = '\0';
	QLR_SteamworksMock_ClearCallbackState();
}

/*
=============
QLR_SteamworksMock_SetLibraryAvailable

Configure whether dlopen succeeds when loading Steamworks.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetLibraryAvailable( qboolean available ) {
	qlr_mock_state.library_available = available;
}

/*
=============
QLR_SteamworksMock_SetInitResult

Set the return value for SteamAPI_Init.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetInitResult( qboolean result ) {
	qlr_mock_state.init_result = result;
}

/*
=============
QLR_SteamworksMock_SetSteamAPIInitExportAvailable

Toggle whether the mock Steam runtime exposes SteamAPI_Init.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamAPIInitExportAvailable( qboolean available ) {
	qlr_mock_state.steam_api_init_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamAPIShutdownExportAvailable

Toggle whether the mock Steam runtime exposes SteamAPI_Shutdown.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamAPIShutdownExportAvailable( qboolean available ) {
	qlr_mock_state.steam_api_shutdown_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamAPIRunCallbacksExportAvailable

Toggle whether the mock Steam runtime exposes SteamAPI_RunCallbacks.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamAPIRunCallbacksExportAvailable( qboolean available ) {
	qlr_mock_state.steam_api_run_callbacks_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamAPIRegisterCallbackExportAvailable

Toggle whether the mock Steam runtime exposes SteamAPI_RegisterCallback.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamAPIRegisterCallbackExportAvailable( qboolean available ) {
	qlr_mock_state.steam_api_register_callback_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamAPIUnregisterCallbackExportAvailable

Toggle whether the mock Steam runtime exposes SteamAPI_UnregisterCallback.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamAPIUnregisterCallbackExportAvailable( qboolean available ) {
	qlr_mock_state.steam_api_unregister_callback_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamAPIRegisterCallResultExportAvailable

Toggle whether the mock Steam runtime exposes SteamAPI_RegisterCallResult.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamAPIRegisterCallResultExportAvailable( qboolean available ) {
	qlr_mock_state.steam_api_register_call_result_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamAPIUnregisterCallResultExportAvailable

Toggle whether the mock Steam runtime exposes SteamAPI_UnregisterCallResult.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamAPIUnregisterCallResultExportAvailable( qboolean available ) {
	qlr_mock_state.steam_api_unregister_call_result_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamUserExportAvailable

Toggle whether the mock Steam runtime exposes SteamUser.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamUserExportAvailable( qboolean available ) {
	qlr_mock_state.steam_user_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamFriendsExportAvailable

Toggle whether the mock Steam runtime exposes SteamFriends.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamFriendsExportAvailable( qboolean available ) {
	qlr_mock_state.steam_friends_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamUtilsExportAvailable

Toggle whether the mock Steam runtime exposes SteamUtils.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamUtilsExportAvailable( qboolean available ) {
	qlr_mock_state.steam_utils_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamUserStatsExportAvailable

Toggle whether the mock Steam runtime exposes SteamUserStats.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamUserStatsExportAvailable( qboolean available ) {
	qlr_mock_state.steam_user_stats_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamNetworkingExportAvailable

Toggle whether the mock Steam runtime exposes SteamNetworking.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamNetworkingExportAvailable( qboolean available ) {
	qlr_mock_state.steam_networking_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamMatchmakingExportAvailable

Toggle whether the mock Steam runtime exposes SteamMatchmaking.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamMatchmakingExportAvailable( qboolean available ) {
	qlr_mock_state.steam_matchmaking_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamMatchmakingServersExportAvailable

Toggle whether the mock Steam runtime exposes SteamMatchmakingServers.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamMatchmakingServersExportAvailable( qboolean available ) {
	qlr_mock_state.steam_matchmaking_servers_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamAppsExportAvailable

Toggle whether the mock Steam runtime exposes SteamApps.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamAppsExportAvailable( qboolean available ) {
	qlr_mock_state.steam_apps_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamUGCExportAvailable

Toggle whether the mock Steam runtime exposes SteamUGC.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamUGCExportAvailable( qboolean available ) {
	qlr_mock_state.steam_ugc_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerExportAvailable

Toggle whether the mock Steam runtime exposes SteamGameServer.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerExportAvailable( qboolean available ) {
	qlr_mock_state.steam_game_server_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerStatsExportAvailable

Toggle whether the mock Steam runtime exposes SteamGameServerStats.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerStatsExportAvailable( qboolean available ) {
	qlr_mock_state.steam_game_server_stats_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerUtilsExportAvailable

Toggle whether the mock Steam runtime exposes SteamGameServerUtils.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerUtilsExportAvailable( qboolean available ) {
	qlr_mock_state.steam_game_server_utils_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerUGCExportAvailable

Toggle whether the mock Steam runtime exposes SteamGameServerUGC.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerUGCExportAvailable( qboolean available ) {
	qlr_mock_state.steam_game_server_ugc_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerInitExportAvailable

Toggle whether the mock Steam runtime exposes SteamGameServer_Init.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerInitExportAvailable( qboolean available ) {
	qlr_mock_state.steam_game_server_init_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerShutdownExportAvailable

Toggle whether the mock Steam runtime exposes SteamGameServer_Shutdown.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerShutdownExportAvailable( qboolean available ) {
	qlr_mock_state.steam_game_server_shutdown_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerRunCallbacksExportAvailable

Toggle whether the mock Steam runtime exposes SteamGameServer_RunCallbacks.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerRunCallbacksExportAvailable( qboolean available ) {
	qlr_mock_state.steam_game_server_run_callbacks_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerNetworkingExportAvailable

Toggle whether the mock Steam runtime exposes SteamGameServerNetworking.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerNetworkingExportAvailable( qboolean available ) {
	qlr_mock_state.steam_game_server_networking_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerInitResult
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerInitResult( qboolean result ) {
	qlr_mock_state.steam_game_server_init_result = result;
}

/*
=============
QLR_SteamworksMock_SetUserAvailable

Toggle whether SteamAPI_SteamUser returns a valid handle.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetUserAvailable( qboolean available ) {
	qlr_mock_state.user_available = available;
}

/*
=============
QLR_SteamworksMock_SetUserLoggedOn

Toggle whether SteamUser()->BLoggedOn reports an authenticated user.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetUserLoggedOn( qboolean loggedOn ) {
	qlr_mock_state.user_logged_on_result = loggedOn ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetTicket

Override the raw ticket contents and handle returned by GetAuthSessionTicket.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetTicket( const uint8_t *ticket, uint32_t length, HAuthTicket handle ) {
	if ( ticket && length > 0 && length <= QLR_TICKET_BUFFER ) {
		memcpy( qlr_mock_state.ticket, ticket, length );
		qlr_mock_state.ticket_length = length;
	}

	qlr_mock_state.ticket_handle = handle;
}

/*
=============
QLR_SteamworksMock_SetAuthSessionTicketExportAvailable

Toggle whether the mock Steam runtime exposes GetAuthSessionTicket.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetAuthSessionTicketExportAvailable( qboolean available ) {
	qlr_mock_state.auth_session_ticket_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetBeginAuthSessionExportAvailable

Toggle whether the mock Steam runtime exposes BeginAuthSession.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetBeginAuthSessionExportAvailable( qboolean available ) {
	qlr_mock_state.begin_auth_session_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetCancelAuthTicketExportAvailable

Toggle whether the mock Steam runtime exposes CancelAuthTicket.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetCancelAuthTicketExportAvailable( qboolean available ) {
	qlr_mock_state.cancel_auth_ticket_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetEndAuthSessionExportAvailable

Toggle whether the mock Steam runtime exposes EndAuthSession.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetEndAuthSessionExportAvailable( qboolean available ) {
	qlr_mock_state.end_auth_session_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetGetSteamIDExportAvailable

Toggle whether the mock Steam runtime exposes GetSteamID.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetGetSteamIDExportAvailable( qboolean available ) {
	qlr_mock_state.get_steam_id_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetWebApiTicket

Override the callback ticket returned by GetAuthTicketForWebApi.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetWebApiTicket( const uint8_t *ticket, uint32_t length, HAuthTicket handle, int result ) {
	if ( ticket && length > 0 && length <= QLR_WEB_API_TICKET_BUFFER ) {
		memcpy( qlr_mock_state.web_api_ticket, ticket, length );
		qlr_mock_state.web_api_ticket_length = length;
	}

	qlr_mock_state.web_api_ticket_handle = handle;
	qlr_mock_state.web_api_ticket_callback_handle = handle;
	qlr_mock_state.web_api_ticket_callback_length = length;
	qlr_mock_state.web_api_ticket_result = result;
}

/*
=============
QLR_SteamworksMock_SetWebApiTicketCallbackBehavior

Override how the mock GetTicketForWebApi callback is queued.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetWebApiTicketCallbackBehavior( qboolean queueCallback, HAuthTicket callbackHandle, uint32_t callbackLength ) {
	qlr_mock_state.web_api_ticket_queue_callback = queueCallback ? qtrue : qfalse;
	qlr_mock_state.web_api_ticket_callback_handle = callbackHandle;
	qlr_mock_state.web_api_ticket_callback_length = callbackLength;
}

/*
=============
QLR_SteamworksMock_SetWebApiTicketExportAvailable

Toggle whether the mock Steam runtime exposes GetAuthTicketForWebApi.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetWebApiTicketExportAvailable( qboolean available ) {
	qlr_mock_state.web_api_ticket_export_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetAuthResult

Set the BeginAuthSession result returned by the mock.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetAuthResult( EBeginAuthSessionResult result ) {
	qlr_mock_state.auth_result = result;
}

/*
=============
QLR_SteamworksMock_SetSteamId

Define the SteamID returned by GetSteamID.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamId( uint64_t steamId ) {
	qlr_mock_state.steam_id_value = steamId;
}

/*
=============
QLR_SteamworksMock_SetAppId
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetAppId( uint32_t appId ) {
	qlr_mock_state.app_id = appId;
}

/*
=============
QLR_SteamworksMock_SetSteamAppsSubscribedResult
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamAppsSubscribedResult( int result ) {
	qlr_mock_state.steam_apps_subscribed_result = result ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetServerBrowserServerName
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetServerBrowserServerName( const char *name ) {
	Q_strncpyz( qlr_mock_state.server_browser_details.serverName, name ? name : "", sizeof( qlr_mock_state.server_browser_details.serverName ) );
}

/*
=============
QLR_SteamworksMock_SetServerBrowserDetailAppId
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetServerBrowserDetailAppId( uint32_t appId ) {
	qlr_mock_state.server_browser_details.appId = appId;
}

/*
=============
QLR_SteamworksMock_SetServerBrowserRequestResult
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetServerBrowserRequestResult( uintptr_t request ) {
	qlr_mock_state.server_browser_request_result = request;
}

/*
=============
QLR_SteamworksMock_SetServerBrowserDetailQueryResults
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetServerBrowserDetailQueryResults( int pingQuery, int playersQuery, int rulesQuery ) {
	qlr_mock_state.server_browser_ping_query_result = pingQuery;
	qlr_mock_state.server_browser_players_query_result = playersQuery;
	qlr_mock_state.server_browser_rules_query_result = rulesQuery;
}

/*
=============
QLR_SteamworksMock_SetLobbyOwnerId
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetLobbyOwnerId( uint64_t steamId ) {
	qlr_mock_state.lobby_owner_id = steamId;
}

/*
=============
QLR_SteamworksMock_SetLobbyChatEntryMessage
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetLobbyChatEntryMessage( const char *message ) {
	Q_strncpyz( qlr_mock_state.lobby_chat_entry_message, message ? message : "", sizeof( qlr_mock_state.lobby_chat_entry_message ) );
}

/*
=============
QLR_SteamworksMock_SetFavoriteResults
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetFavoriteResults( int addResult, int removeResult ) {
	qlr_mock_state.favorite_add_result = addResult;
	qlr_mock_state.favorite_remove_result = removeResult;
}

/*
=============
QLR_SteamworksMock_SetP2PResults
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetP2PResults( int sendResult, int availableResult, int readResult, int acceptResult ) {
	qlr_mock_state.p2p_send_result = sendResult ? qtrue : qfalse;
	qlr_mock_state.p2p_available_result = availableResult ? qtrue : qfalse;
	qlr_mock_state.p2p_read_result = readResult ? qtrue : qfalse;
	qlr_mock_state.p2p_accept_result = acceptResult ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetP2PReadPacket
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetP2PReadPacket( uint64_t steamId, const uint8_t *data, uint32_t length ) {
	if ( length > sizeof( qlr_mock_state.p2p_read_data ) ) {
		length = sizeof( qlr_mock_state.p2p_read_data );
	}

	memset( qlr_mock_state.p2p_read_data, 0, sizeof( qlr_mock_state.p2p_read_data ) );
	if ( data && length > 0u ) {
		memcpy( qlr_mock_state.p2p_read_data, data, length );
	}
	qlr_mock_state.p2p_read_length = length;
	qlr_mock_state.p2p_available_size = length;
	qlr_mock_state.p2p_read_steam_id = steamId;
	qlr_mock_state.p2p_available_result = length > 0u ? qtrue : qfalse;
	qlr_mock_state.p2p_read_result = length > 0u ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetServerP2PResults
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetServerP2PResults( int sendResult, int availableResult, int readResult, int acceptResult ) {
	qlr_mock_state.server_p2p_send_result = sendResult ? qtrue : qfalse;
	qlr_mock_state.server_p2p_available_result = availableResult ? qtrue : qfalse;
	qlr_mock_state.server_p2p_read_result = readResult ? qtrue : qfalse;
	qlr_mock_state.server_p2p_accept_result = acceptResult ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetServerP2PReadPacket
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetServerP2PReadPacket( uint64_t steamId, const uint8_t *data, uint32_t length ) {
	if ( length > sizeof( qlr_mock_state.server_p2p_read_data ) ) {
		length = sizeof( qlr_mock_state.server_p2p_read_data );
	}

	memset( qlr_mock_state.server_p2p_read_data, 0, sizeof( qlr_mock_state.server_p2p_read_data ) );
	if ( data && length > 0u ) {
		memcpy( qlr_mock_state.server_p2p_read_data, data, length );
	}
	qlr_mock_state.server_p2p_read_length = length;
	qlr_mock_state.server_p2p_available_size = length;
	qlr_mock_state.server_p2p_read_steam_id = steamId;
	qlr_mock_state.server_p2p_available_result = length > 0u ? qtrue : qfalse;
	qlr_mock_state.server_p2p_read_result = length > 0u ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetVoiceResults
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetVoiceResults( int getVoiceResult, int decompressResult ) {
	qlr_mock_state.voice_get_result = getVoiceResult;
	qlr_mock_state.voice_decompress_result = decompressResult;
}

/*
=============
QLR_SteamworksMock_SetCompressedVoice
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetCompressedVoice( const uint8_t *data, uint32_t length ) {
	if ( length > sizeof( qlr_mock_state.voice_compressed_data ) ) {
		length = sizeof( qlr_mock_state.voice_compressed_data );
	}

	memset( qlr_mock_state.voice_compressed_data, 0, sizeof( qlr_mock_state.voice_compressed_data ) );
	if ( data && length > 0u ) {
		memcpy( qlr_mock_state.voice_compressed_data, data, length );
	}
	qlr_mock_state.voice_compressed_length = length;
}

/*
=============
QLR_SteamworksMock_SetDecompressedVoice
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetDecompressedVoice( const uint8_t *data, uint32_t length ) {
	if ( length > sizeof( qlr_mock_state.voice_decompressed_data ) ) {
		length = sizeof( qlr_mock_state.voice_decompressed_data );
	}

	memset( qlr_mock_state.voice_decompressed_data, 0, sizeof( qlr_mock_state.voice_decompressed_data ) );
	if ( data && length > 0u ) {
		memcpy( qlr_mock_state.voice_decompressed_data, data, length );
	}
	qlr_mock_state.voice_decompressed_length = length;
}

/*
=============
QLR_SteamworksMock_SetVoiceOptimalSampleRate
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetVoiceOptimalSampleRate( uint32_t sampleRate ) {
	qlr_mock_state.voice_optimal_sample_rate = sampleRate;
}

/*
=============
QLR_SteamworksMock_SetServerIncomingPacketResult
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetServerIncomingPacketResult( int result ) {
	qlr_mock_state.steam_game_server_incoming_packet_result = result ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetServerOutgoingPacket
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetServerOutgoingPacket( const uint8_t *data, int length, uint32_t ip, uint16_t port ) {
	if ( length < 0 ) {
		length = 0;
	}
	if ( length > (int)sizeof( qlr_mock_state.steam_game_server_outgoing_packet_data ) ) {
		length = (int)sizeof( qlr_mock_state.steam_game_server_outgoing_packet_data );
	}

	memset( qlr_mock_state.steam_game_server_outgoing_packet_data, 0, sizeof( qlr_mock_state.steam_game_server_outgoing_packet_data ) );
	if ( data && length > 0 ) {
		memcpy( qlr_mock_state.steam_game_server_outgoing_packet_data, data, (size_t)length );
	}
	qlr_mock_state.steam_game_server_outgoing_packet_length = length;
	qlr_mock_state.steam_game_server_outgoing_packet_ip = ip;
	qlr_mock_state.steam_game_server_outgoing_packet_port = port;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerLoggedOn
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerLoggedOn( int loggedOn ) {
	qlr_mock_state.steam_game_server_logged_on_result = loggedOn ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerPublicIP
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerPublicIP( uint32_t address ) {
	qlr_mock_state.steam_game_server_public_ip = address;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerId
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerId( uint64_t steamId ) {
	qlr_mock_state.steam_game_server_id_value = steamId;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerUnauthenticatedUserId
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerUnauthenticatedUserId( uint64_t steamId ) {
	qlr_mock_state.steam_game_server_unauthenticated_user_id_value = steamId;
}

/*
=============
QLR_SteamworksMock_SetAvatarHandles

Configure the Steam avatar handles returned for each requested size.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetAvatarHandles( int smallHandle, int mediumHandle, int largeHandle ) {
	qlr_mock_state.avatar_handle_small = smallHandle;
	qlr_mock_state.avatar_handle_medium = mediumHandle;
	qlr_mock_state.avatar_handle_large = largeHandle;
}

/*
=============
QLR_SteamworksMock_SetAvatarPixels

Override the RGBA payload returned by the SteamUtils avatar helpers.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetAvatarPixels( uint32_t width, uint32_t height, const uint8_t *pixels, uint32_t length ) {
	size_t requiredLength = (size_t)width * (size_t)height * 4;

	qlr_mock_state.avatar_width = 0;
	qlr_mock_state.avatar_height = 0;
	qlr_mock_state.avatar_rgba_length = 0;

	if ( !pixels || width == 0 || height == 0 || requiredLength == 0 || requiredLength > QLR_AVATAR_BUFFER || length < requiredLength ) {
		return;
	}

	qlr_mock_state.avatar_width = width;
	qlr_mock_state.avatar_height = height;
	qlr_mock_state.avatar_rgba_length = (uint32_t)requiredLength;
	memcpy( qlr_mock_state.avatar_rgba, pixels, requiredLength );
}

/*
=============
QLR_SteamworksMock_SetUGCItemState
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetUGCItemState( uint32_t itemState ) {
	qlr_mock_state.ugc_item_state = itemState;
}

/*
=============
QLR_SteamworksMock_SetUGCDownloadInfo
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetUGCDownloadInfo( uint64_t downloaded, uint64_t total ) {
	qlr_mock_state.ugc_downloaded = downloaded;
	qlr_mock_state.ugc_total = total;
}

/*
=============
QLR_SteamworksMock_SetSubscribedItems
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSubscribedItems( const uint64_t *itemIds, uint32_t count ) {
	qlr_mock_state.ugc_subscribed_item_count = 0u;
	memset( qlr_mock_state.ugc_subscribed_items, 0, sizeof( qlr_mock_state.ugc_subscribed_items ) );

	if ( !itemIds || count == 0u ) {
		return;
	}

	if ( count > QLR_MAX_SUBSCRIBED_ITEMS ) {
		count = QLR_MAX_SUBSCRIBED_ITEMS;
	}

	memcpy( qlr_mock_state.ugc_subscribed_items, itemIds, count * sizeof( qlr_mock_state.ugc_subscribed_items[0] ) );
	qlr_mock_state.ugc_subscribed_item_count = count;
}

/*
=============
QLR_SteamworksMock_SetUGCInstallInfo
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetUGCInstallInfo( uint64_t itemId, uint64_t sizeOnDisk, const char *folder, uint32_t timestamp ) {
	qlr_mock_state.ugc_install_item_id = itemId;
	qlr_mock_state.ugc_install_size_on_disk = sizeOnDisk;
	Q_strncpyz( qlr_mock_state.ugc_install_folder, folder ? folder : "", sizeof( qlr_mock_state.ugc_install_folder ) );
	qlr_mock_state.ugc_install_timestamp = timestamp;
}

/*
=============
QLR_SteamworksMock_GetOverlayCallCount
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetOverlayCallCount( void ) {
	return qlr_mock_state.overlay_calls;
}

/*
=============
QLR_SteamworksMock_GetOverlayDialog
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetOverlayDialog( void ) {
	return qlr_mock_state.overlay_dialog;
}

/*
=============
QLR_SteamworksMock_GetOverlaySteamId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetOverlaySteamId( void ) {
	return qlr_mock_state.overlay_steam_id;
}

/*
=============
QLR_SteamworksMock_GetOverlayWebCallCount
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetOverlayWebCallCount( void ) {
	return qlr_mock_state.overlay_web_calls;
}

/*
=============
QLR_SteamworksMock_GetOverlayWebUrl
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetOverlayWebUrl( void ) {
	return qlr_mock_state.overlay_web_url;
}

/*
=============
QLR_SteamworksMock_GetRichPresenceCallCount
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetRichPresenceCallCount( void ) {
	return qlr_mock_state.rich_presence_calls;
}

/*
=============
QLR_SteamworksMock_GetRichPresenceKey
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetRichPresenceKey( void ) {
	return qlr_mock_state.rich_presence_key;
}

/*
=============
QLR_SteamworksMock_GetRichPresenceValue
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetRichPresenceValue( void ) {
	return qlr_mock_state.rich_presence_value;
}

/*
=============
QLR_SteamworksMock_GetPersonaNameCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetPersonaNameCalls( void ) {
	return qlr_mock_state.persona_name_calls;
}

/*
=============
QLR_SteamworksMock_GetUserSteamIdCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUserSteamIdCalls( void ) {
	return qlr_mock_state.user_steam_id_calls;
}

/*
=============
QLR_SteamworksMock_GetIPCountryCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetIPCountryCalls( void ) {
	return qlr_mock_state.ip_country_calls;
}

/*
=============
QLR_SteamworksMock_GetAppIdCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetAppIdCalls( void ) {
	return qlr_mock_state.app_id_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamAppsInterfaceCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamAppsInterfaceCalls( void ) {
	return qlr_mock_state.steam_apps_interface_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamAppsLastAppId
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetSteamAppsLastAppId( void ) {
	return qlr_mock_state.steam_apps_last_app_id;
}

/*
=============
QLR_SteamworksMock_SetFriendEnumeration
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetFriendEnumeration( int count, uint64_t steamId ) {
	qlr_mock_state.friend_count = count < 0 ? 0 : count;
	qlr_mock_state.friend_by_index_id = steamId;
}

/*
=============
QLR_SteamworksMock_GetFriendCountCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetFriendCountCalls( void ) {
	return qlr_mock_state.friend_count_calls;
}

/*
=============
QLR_SteamworksMock_GetFriendLastCountFlags
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetFriendLastCountFlags( void ) {
	return qlr_mock_state.friend_last_count_flags;
}

/*
=============
QLR_SteamworksMock_GetFriendByIndexCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetFriendByIndexCalls( void ) {
	return qlr_mock_state.friend_by_index_calls;
}

/*
=============
QLR_SteamworksMock_GetFriendLastIndex
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetFriendLastIndex( void ) {
	return qlr_mock_state.friend_last_index;
}

/*
=============
QLR_SteamworksMock_GetFriendLastIndexFlags
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetFriendLastIndexFlags( void ) {
	return qlr_mock_state.friend_last_index_flags;
}

/*
=============
QLR_SteamworksMock_GetFriendVoiceSpeakingCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetFriendVoiceSpeakingCalls( void ) {
	return qlr_mock_state.friend_voice_speaking_calls;
}

/*
=============
QLR_SteamworksMock_GetFriendVoiceLastSteamId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetFriendVoiceLastSteamId( void ) {
	return qlr_mock_state.friend_voice_last_steam_id;
}

/*
=============
QLR_SteamworksMock_GetFriendVoiceLastSpeaking
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetFriendVoiceLastSpeaking( void ) {
	return qlr_mock_state.friend_voice_last_speaking;
}

/*
=============
QLR_SteamworksMock_GetP2PSendCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetP2PSendCalls( void ) {
	return qlr_mock_state.p2p_send_calls;
}

/*
=============
QLR_SteamworksMock_GetP2PLastSendSteamId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetP2PLastSendSteamId( void ) {
	return qlr_mock_state.p2p_last_send_steam_id;
}

/*
=============
QLR_SteamworksMock_GetP2PLastSendLength
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetP2PLastSendLength( void ) {
	return qlr_mock_state.p2p_last_send_length;
}

/*
=============
QLR_SteamworksMock_GetP2PLastSendType
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetP2PLastSendType( void ) {
	return qlr_mock_state.p2p_last_send_type;
}

/*
=============
QLR_SteamworksMock_GetP2PLastSendChannel
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetP2PLastSendChannel( void ) {
	return qlr_mock_state.p2p_last_send_channel;
}

/*
=============
QLR_SteamworksMock_GetP2PLastSendByte
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetP2PLastSendByte( int index ) {
	if ( index < 0 || index >= (int)qlr_mock_state.p2p_last_send_length || index >= (int)sizeof( qlr_mock_state.p2p_last_send_data ) ) {
		return -1;
	}
	return qlr_mock_state.p2p_last_send_data[index];
}

/*
=============
QLR_SteamworksMock_GetP2PAvailableCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetP2PAvailableCalls( void ) {
	return qlr_mock_state.p2p_available_calls;
}

/*
=============
QLR_SteamworksMock_GetP2PLastAvailableChannel
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetP2PLastAvailableChannel( void ) {
	return qlr_mock_state.p2p_last_available_channel;
}

/*
=============
QLR_SteamworksMock_GetP2PReadCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetP2PReadCalls( void ) {
	return qlr_mock_state.p2p_read_calls;
}

/*
=============
QLR_SteamworksMock_GetP2PLastReadChannel
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetP2PLastReadChannel( void ) {
	return qlr_mock_state.p2p_last_read_channel;
}

/*
=============
QLR_SteamworksMock_GetP2PAcceptCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetP2PAcceptCalls( void ) {
	return qlr_mock_state.p2p_accept_calls;
}

/*
=============
QLR_SteamworksMock_GetP2PLastAcceptSteamId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetP2PLastAcceptSteamId( void ) {
	return qlr_mock_state.p2p_last_accept_steam_id;
}

/*
=============
QLR_SteamworksMock_GetVoiceStartCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetVoiceStartCalls( void ) {
	return qlr_mock_state.voice_start_calls;
}

/*
=============
QLR_SteamworksMock_GetVoiceStopCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetVoiceStopCalls( void ) {
	return qlr_mock_state.voice_stop_calls;
}

/*
=============
QLR_SteamworksMock_GetVoiceGetCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetVoiceGetCalls( void ) {
	return qlr_mock_state.voice_get_calls;
}

/*
=============
QLR_SteamworksMock_GetVoiceDecompressCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetVoiceDecompressCalls( void ) {
	return qlr_mock_state.voice_decompress_calls;
}

/*
=============
QLR_SteamworksMock_GetVoiceOptimalRateCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetVoiceOptimalRateCalls( void ) {
	return qlr_mock_state.voice_optimal_rate_calls;
}

/*
=============
QLR_SteamworksMock_GetVoiceLastWantCompressed
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetVoiceLastWantCompressed( void ) {
	return qlr_mock_state.voice_last_want_compressed;
}

/*
=============
QLR_SteamworksMock_GetVoiceLastWantUncompressed
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetVoiceLastWantUncompressed( void ) {
	return qlr_mock_state.voice_last_want_uncompressed;
}

/*
=============
QLR_SteamworksMock_GetVoiceLastCompressedBufferSize
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetVoiceLastCompressedBufferSize( void ) {
	return qlr_mock_state.voice_last_compressed_buffer_size;
}

/*
=============
QLR_SteamworksMock_GetVoiceLastUncompressedBufferSize
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetVoiceLastUncompressedBufferSize( void ) {
	return qlr_mock_state.voice_last_uncompressed_buffer_size;
}

/*
=============
QLR_SteamworksMock_GetVoiceLastDecompressInputSize
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetVoiceLastDecompressInputSize( void ) {
	return qlr_mock_state.voice_last_decompress_input_size;
}

/*
=============
QLR_SteamworksMock_GetVoiceLastDecompressBufferSize
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetVoiceLastDecompressBufferSize( void ) {
	return qlr_mock_state.voice_last_decompress_buffer_size;
}

/*
=============
QLR_SteamworksMock_GetVoiceLastDecompressSampleRate
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetVoiceLastDecompressSampleRate( void ) {
	return qlr_mock_state.voice_last_decompress_sample_rate;
}

/*
=============
QLR_SteamworksMock_GetServerP2PSendCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerP2PSendCalls( void ) {
	return qlr_mock_state.server_p2p_send_calls;
}

/*
=============
QLR_SteamworksMock_GetServerP2PLastSendSteamId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetServerP2PLastSendSteamId( void ) {
	return qlr_mock_state.server_p2p_last_send_steam_id;
}

/*
=============
QLR_SteamworksMock_GetServerP2PLastSendLength
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetServerP2PLastSendLength( void ) {
	return qlr_mock_state.server_p2p_last_send_length;
}

/*
=============
QLR_SteamworksMock_GetServerP2PLastSendType
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerP2PLastSendType( void ) {
	return qlr_mock_state.server_p2p_last_send_type;
}

/*
=============
QLR_SteamworksMock_GetServerP2PLastSendChannel
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerP2PLastSendChannel( void ) {
	return qlr_mock_state.server_p2p_last_send_channel;
}

/*
=============
QLR_SteamworksMock_GetServerP2PLastSendByte
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerP2PLastSendByte( int index ) {
	if ( index < 0 || index >= (int)qlr_mock_state.server_p2p_last_send_length || index >= (int)sizeof( qlr_mock_state.server_p2p_last_send_data ) ) {
		return -1;
	}
	return qlr_mock_state.server_p2p_last_send_data[index];
}

/*
=============
QLR_SteamworksMock_GetServerP2PAvailableCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerP2PAvailableCalls( void ) {
	return qlr_mock_state.server_p2p_available_calls;
}

/*
=============
QLR_SteamworksMock_GetServerP2PLastAvailableChannel
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerP2PLastAvailableChannel( void ) {
	return qlr_mock_state.server_p2p_last_available_channel;
}

/*
=============
QLR_SteamworksMock_GetServerP2PReadCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerP2PReadCalls( void ) {
	return qlr_mock_state.server_p2p_read_calls;
}

/*
=============
QLR_SteamworksMock_GetServerP2PLastReadChannel
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerP2PLastReadChannel( void ) {
	return qlr_mock_state.server_p2p_last_read_channel;
}

/*
=============
QLR_SteamworksMock_GetServerP2PAcceptCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerP2PAcceptCalls( void ) {
	return qlr_mock_state.server_p2p_accept_calls;
}

/*
=============
QLR_SteamworksMock_GetServerP2PLastAcceptSteamId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetServerP2PLastAcceptSteamId( void ) {
	return qlr_mock_state.server_p2p_last_accept_steam_id;
}

/*
=============
QLR_SteamworksMock_GetServerIncomingPacketCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerIncomingPacketCalls( void ) {
	return qlr_mock_state.steam_game_server_incoming_packet_calls;
}

/*
=============
QLR_SteamworksMock_GetServerIncomingPacketLength
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerIncomingPacketLength( void ) {
	return qlr_mock_state.steam_game_server_incoming_packet_length;
}

/*
=============
QLR_SteamworksMock_GetServerIncomingPacketByte
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerIncomingPacketByte( int index ) {
	if ( index < 0 || index >= qlr_mock_state.steam_game_server_incoming_packet_length || index >= (int)sizeof( qlr_mock_state.steam_game_server_incoming_packet_data ) ) {
		return -1;
	}
	return qlr_mock_state.steam_game_server_incoming_packet_data[index];
}

/*
=============
QLR_SteamworksMock_GetServerIncomingPacketIP
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetServerIncomingPacketIP( void ) {
	return qlr_mock_state.steam_game_server_incoming_packet_ip;
}

/*
=============
QLR_SteamworksMock_GetServerIncomingPacketPort
=============
*/
QLR_EXPORT uint16_t QLR_SteamworksMock_GetServerIncomingPacketPort( void ) {
	return qlr_mock_state.steam_game_server_incoming_packet_port;
}

/*
=============
QLR_SteamworksMock_GetServerOutgoingPacketCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerOutgoingPacketCalls( void ) {
	return qlr_mock_state.steam_game_server_outgoing_packet_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerInitCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerInitCalls( void ) {
	return qlr_mock_state.steam_game_server_init_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerShutdownCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerShutdownCalls( void ) {
	return qlr_mock_state.steam_game_server_shutdown_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastInitIP
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetSteamGameServerLastInitIP( void ) {
	return qlr_mock_state.steam_game_server_last_init_ip;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastInitSteamPort
=============
*/
QLR_EXPORT uint16_t QLR_SteamworksMock_GetSteamGameServerLastInitSteamPort( void ) {
	return qlr_mock_state.steam_game_server_last_init_steam_port;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastInitGamePort
=============
*/
QLR_EXPORT uint16_t QLR_SteamworksMock_GetSteamGameServerLastInitGamePort( void ) {
	return qlr_mock_state.steam_game_server_last_init_game_port;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastInitQueryPort
=============
*/
QLR_EXPORT uint16_t QLR_SteamworksMock_GetSteamGameServerLastInitQueryPort( void ) {
	return qlr_mock_state.steam_game_server_last_init_query_port;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastInitServerMode
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerLastInitServerMode( void ) {
	return qlr_mock_state.steam_game_server_last_init_server_mode;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastInitVersion
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetSteamGameServerLastInitVersion( void ) {
	return qlr_mock_state.steam_game_server_last_init_version;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLoggedOnCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerLoggedOnCalls( void ) {
	return qlr_mock_state.steam_game_server_logged_on_calls;
}

/*
=============
QLR_SteamworksMock_GetUserLoggedOnCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUserLoggedOnCalls( void ) {
	return qlr_mock_state.user_logged_on_calls;
}

/*
=============
QLR_SteamworksMock_GetWebApiTicketCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetWebApiTicketCalls( void ) {
	return qlr_mock_state.web_api_ticket_calls;
}

/*
=============
QLR_SteamworksMock_GetWebApiTicketIdentity
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetWebApiTicketIdentity( void ) {
	return qlr_mock_state.web_api_ticket_identity;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerCallbackCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerCallbackCalls( void ) {
	return qlr_mock_state.steam_game_server_callback_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerHeartbeatCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerHeartbeatCalls( void ) {
	return qlr_mock_state.steam_game_server_heartbeat_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastHeartbeatEnabled
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerLastHeartbeatEnabled( void ) {
	return qlr_mock_state.steam_game_server_last_heartbeat_enabled;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerDedicatedCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerDedicatedCalls( void ) {
	return qlr_mock_state.steam_game_server_dedicated_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastDedicated
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerLastDedicated( void ) {
	return qlr_mock_state.steam_game_server_last_dedicated;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLogOnCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerLogOnCalls( void ) {
	return qlr_mock_state.steam_game_server_logon_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLogOnAnonymousCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerLogOnAnonymousCalls( void ) {
	return qlr_mock_state.steam_game_server_logon_anonymous_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerProductCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerProductCalls( void ) {
	return qlr_mock_state.steam_game_server_product_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerGameDirCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerGameDirCalls( void ) {
	return qlr_mock_state.steam_game_server_game_dir_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerGameDescriptionCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerGameDescriptionCalls( void ) {
	return qlr_mock_state.steam_game_server_game_description_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerMaxPlayerCountCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerMaxPlayerCountCalls( void ) {
	return qlr_mock_state.steam_game_server_max_player_count_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerBotPlayerCountCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerBotPlayerCountCalls( void ) {
	return qlr_mock_state.steam_game_server_bot_player_count_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerServerNameCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerServerNameCalls( void ) {
	return qlr_mock_state.steam_game_server_server_name_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerMapNameCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerMapNameCalls( void ) {
	return qlr_mock_state.steam_game_server_map_name_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerPasswordCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerPasswordCalls( void ) {
	return qlr_mock_state.steam_game_server_password_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerGameTagsCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerGameTagsCalls( void ) {
	return qlr_mock_state.steam_game_server_game_tags_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerUserDataCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerUserDataCalls( void ) {
	return qlr_mock_state.steam_game_server_user_data_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerKeyValueCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerKeyValueCalls( void ) {
	return qlr_mock_state.steam_game_server_key_value_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastAccount
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetSteamGameServerLastAccount( void ) {
	return qlr_mock_state.steam_game_server_last_account;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastKey
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetSteamGameServerLastKey( void ) {
	return qlr_mock_state.steam_game_server_last_key;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastProduct
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetSteamGameServerLastProduct( void ) {
	return qlr_mock_state.steam_game_server_last_product;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastGameDir
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetSteamGameServerLastGameDir( void ) {
	return qlr_mock_state.steam_game_server_last_game_dir;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastGameDescription
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetSteamGameServerLastGameDescription( void ) {
	return qlr_mock_state.steam_game_server_last_game_description;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastServerName
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetSteamGameServerLastServerName( void ) {
	return qlr_mock_state.steam_game_server_last_server_name;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastMapName
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetSteamGameServerLastMapName( void ) {
	return qlr_mock_state.steam_game_server_last_map_name;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastGameTags
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetSteamGameServerLastGameTags( void ) {
	return qlr_mock_state.steam_game_server_last_game_tags;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastUserDataName
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetSteamGameServerLastUserDataName( void ) {
	return qlr_mock_state.steam_game_server_last_user_data_name;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastUserDataId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetSteamGameServerLastUserDataId( void ) {
	return qlr_mock_state.steam_game_server_last_user_data_id;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerUnauthenticatedUserCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerUnauthenticatedUserCalls( void ) {
	return qlr_mock_state.steam_game_server_unauthenticated_user_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastUserDataScore
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetSteamGameServerLastUserDataScore( void ) {
	return qlr_mock_state.steam_game_server_last_user_data_score;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastMaxPlayerCount
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerLastMaxPlayerCount( void ) {
	return qlr_mock_state.steam_game_server_last_max_player_count;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastBotPlayerCount
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerLastBotPlayerCount( void ) {
	return qlr_mock_state.steam_game_server_last_bot_player_count;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastPasswordProtected
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerLastPasswordProtected( void ) {
	return qlr_mock_state.steam_game_server_last_password_protected;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerLastValue
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetSteamGameServerLastValue( void ) {
	return qlr_mock_state.steam_game_server_last_value;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerStatsAvailable
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerStatsAvailable( qboolean available ) {
	qlr_mock_state.steam_game_server_stats_available = available ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerStatsResult
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerStatsResult( qboolean result ) {
	qlr_mock_state.steam_game_server_stats_result = result ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerStatsIntValue
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerStatsIntValue( int value ) {
	qlr_mock_state.steam_game_server_stats_int_value = value;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerStatsFloatValue
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerStatsFloatValue( float value ) {
	qlr_mock_state.steam_game_server_stats_float_value = value;
}

/*
=============
QLR_SteamworksMock_SetSteamGameServerStatsAchievementValue
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetSteamGameServerStatsAchievementValue( qboolean value ) {
	qlr_mock_state.steam_game_server_stats_achievement_value = value ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsRequestCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerStatsRequestCalls( void ) {
	return qlr_mock_state.steam_game_server_stats_request_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsInterfaceCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerStatsInterfaceCalls( void ) {
	return qlr_mock_state.steam_game_server_stats_interface_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsGetIntCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerStatsGetIntCalls( void ) {
	return qlr_mock_state.steam_game_server_stats_get_int_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsGetFloatCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerStatsGetFloatCalls( void ) {
	return qlr_mock_state.steam_game_server_stats_get_float_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsGetAchievementCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerStatsGetAchievementCalls( void ) {
	return qlr_mock_state.steam_game_server_stats_get_achievement_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsSetIntCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerStatsSetIntCalls( void ) {
	return qlr_mock_state.steam_game_server_stats_set_int_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsSetFloatCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerStatsSetFloatCalls( void ) {
	return qlr_mock_state.steam_game_server_stats_set_float_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsUpdateAvgRateCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerStatsUpdateAvgRateCalls( void ) {
	return qlr_mock_state.steam_game_server_stats_update_avg_rate_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsSetAchievementCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerStatsSetAchievementCalls( void ) {
	return qlr_mock_state.steam_game_server_stats_set_achievement_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsStoreCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerStatsStoreCalls( void ) {
	return qlr_mock_state.steam_game_server_stats_store_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsLastUserId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetSteamGameServerStatsLastUserId( void ) {
	return qlr_mock_state.steam_game_server_stats_last_user_id;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsLastName
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetSteamGameServerStatsLastName( void ) {
	return qlr_mock_state.steam_game_server_stats_last_name;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsLastIntValue
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerStatsLastIntValue( void ) {
	return qlr_mock_state.steam_game_server_stats_last_int_value;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsLastFloatValue
=============
*/
QLR_EXPORT float QLR_SteamworksMock_GetSteamGameServerStatsLastFloatValue( void ) {
	return qlr_mock_state.steam_game_server_stats_last_float_value;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsLastAvgCount
=============
*/
QLR_EXPORT float QLR_SteamworksMock_GetSteamGameServerStatsLastAvgCount( void ) {
	return qlr_mock_state.steam_game_server_stats_last_avg_count;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerStatsLastAvgSessionLength
=============
*/
QLR_EXPORT double QLR_SteamworksMock_GetSteamGameServerStatsLastAvgSessionLength( void ) {
	return qlr_mock_state.steam_game_server_stats_last_avg_session_length;
}

/*
=============
QLR_SteamworksMock_GetLobbyLeaveCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetLobbyLeaveCalls( void ) {
	return qlr_mock_state.lobby_leave_calls;
}

/*
=============
QLR_SteamworksMock_GetLobbyCreateCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetLobbyCreateCalls( void ) {
	return qlr_mock_state.lobby_create_calls;
}

/*
=============
QLR_SteamworksMock_GetLobbySetServerCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetLobbySetServerCalls( void ) {
	return qlr_mock_state.lobby_set_server_calls;
}

/*
=============
QLR_SteamworksMock_GetFavoriteAddCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetFavoriteAddCalls( void ) {
	return qlr_mock_state.favorite_add_calls;
}

/*
=============
QLR_SteamworksMock_GetFavoriteRemoveCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetFavoriteRemoveCalls( void ) {
	return qlr_mock_state.favorite_remove_calls;
}

/*
=============
QLR_SteamworksMock_GetLobbyJoinCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetLobbyJoinCalls( void ) {
	return qlr_mock_state.lobby_join_calls;
}

/*
=============
QLR_SteamworksMock_GetLobbyInviteCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetLobbyInviteCalls( void ) {
	return qlr_mock_state.lobby_invite_calls;
}

/*
=============
QLR_SteamworksMock_GetLobbyUserInviteCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetLobbyUserInviteCalls( void ) {
	return qlr_mock_state.lobby_user_invite_calls;
}

/*
=============
QLR_SteamworksMock_GetLobbySayCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetLobbySayCalls( void ) {
	return qlr_mock_state.lobby_say_calls;
}

/*
=============
QLR_SteamworksMock_GetUserStatsRequestCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUserStatsRequestCalls( void ) {
	return qlr_mock_state.user_stats_request_calls;
}

/*
=============
QLR_SteamworksMock_SetResetAllStatsResult
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetResetAllStatsResult( int result ) {
	qlr_mock_state.reset_user_stats_result = result;
}

/*
=============
QLR_SteamworksMock_GetResetAllStatsCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetResetAllStatsCalls( void ) {
	return qlr_mock_state.user_stats_reset_calls;
}

/*
=============
QLR_SteamworksMock_GetResetAllStatsLastAchievements
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetResetAllStatsLastAchievements( void ) {
	return qlr_mock_state.user_stats_last_reset_achievements;
}

/*
=============
QLR_SteamworksMock_SetUserStatsReadback
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetUserStatsReadback( int statValue, float floatValue, int achieved, int unlockTime, const char *displayAttribute ) {
	qlr_mock_state.user_stats_int_value = statValue;
	qlr_mock_state.user_stats_float_value = floatValue;
	qlr_mock_state.user_stats_achievement_value = achieved ? qtrue : qfalse;
	qlr_mock_state.user_stats_unlock_time = unlockTime;
	Q_strncpyz( qlr_mock_state.user_stats_display_attribute_value, displayAttribute ? displayAttribute : "", sizeof( qlr_mock_state.user_stats_display_attribute_value ) );
}

/*
=============
QLR_SteamworksMock_SetUserStatsReadbackResults
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetUserStatsReadbackResults( int statResult, int floatResult, int achievementResult, int attributeResult ) {
	qlr_mock_state.user_stats_get_int_result = statResult;
	qlr_mock_state.user_stats_get_float_result = floatResult;
	qlr_mock_state.user_stats_get_achievement_result = achievementResult;
	qlr_mock_state.user_stats_get_display_attribute_result = attributeResult;
}

/*
=============
QLR_SteamworksMock_GetUserStatsGetIntCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUserStatsGetIntCalls( void ) {
	return qlr_mock_state.user_stats_get_int_calls;
}

/*
=============
QLR_SteamworksMock_GetUserStatsGetFloatCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUserStatsGetFloatCalls( void ) {
	return qlr_mock_state.user_stats_get_float_calls;
}

/*
=============
QLR_SteamworksMock_GetUserStatsGetAchievementCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUserStatsGetAchievementCalls( void ) {
	return qlr_mock_state.user_stats_get_achievement_calls;
}

/*
=============
QLR_SteamworksMock_GetUserStatsGetDisplayAttributeCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUserStatsGetDisplayAttributeCalls( void ) {
	return qlr_mock_state.user_stats_get_display_attribute_calls;
}

/*
=============
QLR_SteamworksMock_GetUserStatsLastReadId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetUserStatsLastReadId( void ) {
	return qlr_mock_state.user_stats_last_read_id;
}

/*
=============
QLR_SteamworksMock_GetUserStatsLastName
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetUserStatsLastName( void ) {
	return qlr_mock_state.user_stats_last_name;
}

/*
=============
QLR_SteamworksMock_GetUserStatsLastAttributeKey
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetUserStatsLastAttributeKey( void ) {
	return qlr_mock_state.user_stats_last_attribute_key;
}

/*
=============
QLR_SteamworksMock_GetLobbyCreateType
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetLobbyCreateType( void ) {
	return qlr_mock_state.lobby_create_type;
}

/*
=============
QLR_SteamworksMock_GetLobbyCreateMaxMembers
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetLobbyCreateMaxMembers( void ) {
	return qlr_mock_state.lobby_create_max_members;
}

/*
=============
QLR_SteamworksMock_GetLobbyLeaveId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetLobbyLeaveId( void ) {
	return qlr_mock_state.lobby_leave_id;
}

/*
=============
QLR_SteamworksMock_GetLobbyJoinId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetLobbyJoinId( void ) {
	return qlr_mock_state.lobby_join_id;
}

/*
=============
QLR_SteamworksMock_GetLobbySetServerId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetLobbySetServerId( void ) {
	return qlr_mock_state.lobby_set_server_id;
}

/*
=============
QLR_SteamworksMock_GetLobbyInviteId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetLobbyInviteId( void ) {
	return qlr_mock_state.lobby_invite_id;
}

/*
=============
QLR_SteamworksMock_GetLobbyUserInviteLobbyId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetLobbyUserInviteLobbyId( void ) {
	return qlr_mock_state.lobby_user_invite_lobby_id;
}

/*
=============
QLR_SteamworksMock_GetLobbyUserInviteTargetId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetLobbyUserInviteTargetId( void ) {
	return qlr_mock_state.lobby_user_invite_target_id;
}

/*
=============
QLR_SteamworksMock_GetLobbySetServerIp
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetLobbySetServerIp( void ) {
	return qlr_mock_state.lobby_set_server_ip;
}

/*
=============
QLR_SteamworksMock_GetLobbySetServerPort
=============
*/
QLR_EXPORT uint16_t QLR_SteamworksMock_GetLobbySetServerPort( void ) {
	return qlr_mock_state.lobby_set_server_port;
}

/*
=============
QLR_SteamworksMock_GetFavoriteLastAppId
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetFavoriteLastAppId( void ) {
	return qlr_mock_state.favorite_last_app_id;
}

/*
=============
QLR_SteamworksMock_GetFavoriteLastIp
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetFavoriteLastIp( void ) {
	return qlr_mock_state.favorite_last_ip;
}

/*
=============
QLR_SteamworksMock_GetFavoriteLastConnPort
=============
*/
QLR_EXPORT uint16_t QLR_SteamworksMock_GetFavoriteLastConnPort( void ) {
	return qlr_mock_state.favorite_last_conn_port;
}

/*
=============
QLR_SteamworksMock_GetFavoriteLastQueryPort
=============
*/
QLR_EXPORT uint16_t QLR_SteamworksMock_GetFavoriteLastQueryPort( void ) {
	return qlr_mock_state.favorite_last_query_port;
}

/*
=============
QLR_SteamworksMock_GetFavoriteLastFlags
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetFavoriteLastFlags( void ) {
	return qlr_mock_state.favorite_last_flags;
}

/*
=============
QLR_SteamworksMock_GetFavoriteLastPlayed
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetFavoriteLastPlayed( void ) {
	return qlr_mock_state.favorite_last_played;
}

/*
=============
QLR_SteamworksMock_GetLobbySetServerGameServerId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetLobbySetServerGameServerId( void ) {
	return qlr_mock_state.lobby_set_server_game_server_id;
}

/*
=============
QLR_SteamworksMock_GetLobbySayId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetLobbySayId( void ) {
	return qlr_mock_state.lobby_say_id;
}

/*
=============
QLR_SteamworksMock_GetLobbySayMessage
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetLobbySayMessage( void ) {
	return qlr_mock_state.lobby_say_message;
}

/*
=============
QLR_SteamworksMock_GetUserStatsRequestId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetUserStatsRequestId( void ) {
	return qlr_mock_state.user_stats_request_id;
}

/*
=============
QLR_SteamworksMock_GetGameInviteCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetGameInviteCalls( void ) {
	return qlr_mock_state.game_invite_calls;
}

/*
=============
QLR_SteamworksMock_GetGameInviteTargetId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetGameInviteTargetId( void ) {
	return qlr_mock_state.game_invite_target_id;
}

/*
=============
QLR_SteamworksMock_GetGameInviteConnectString
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetGameInviteConnectString( void ) {
	return qlr_mock_state.game_invite_connect_string;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserInternetCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserInternetCalls( void ) {
	return qlr_mock_state.server_browser_internet_calls;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserLanCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserLanCalls( void ) {
	return qlr_mock_state.server_browser_lan_calls;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserFriendsCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserFriendsCalls( void ) {
	return qlr_mock_state.server_browser_friends_calls;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserFavoritesCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserFavoritesCalls( void ) {
	return qlr_mock_state.server_browser_favorites_calls;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserHistoryCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserHistoryCalls( void ) {
	return qlr_mock_state.server_browser_history_calls;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserReleaseCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserReleaseCalls( void ) {
	return qlr_mock_state.server_browser_release_calls;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserRefreshCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserRefreshCalls( void ) {
	return qlr_mock_state.server_browser_refresh_calls;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserGetDetailsCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserGetDetailsCalls( void ) {
	return qlr_mock_state.server_browser_get_details_calls;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserPingCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserPingCalls( void ) {
	return qlr_mock_state.server_browser_ping_calls;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserPlayersCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserPlayersCalls( void ) {
	return qlr_mock_state.server_browser_players_calls;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserRulesCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserRulesCalls( void ) {
	return qlr_mock_state.server_browser_rules_calls;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserCancelQueryCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserCancelQueryCalls( void ) {
	return qlr_mock_state.server_browser_cancel_query_calls;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserPingOrder
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserPingOrder( void ) {
	return qlr_mock_state.server_browser_ping_order;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserPlayersOrder
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserPlayersOrder( void ) {
	return qlr_mock_state.server_browser_players_order;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserRulesOrder
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserRulesOrder( void ) {
	return qlr_mock_state.server_browser_rules_order;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserLastAppId
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetServerBrowserLastAppId( void ) {
	return qlr_mock_state.server_browser_last_app_id;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserLastFilterCount
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetServerBrowserLastFilterCount( void ) {
	return qlr_mock_state.server_browser_last_filter_count;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserLastFilterKey
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetServerBrowserLastFilterKey( void ) {
	return qlr_mock_state.server_browser_last_filter_key;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserLastFilterValue
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetServerBrowserLastFilterValue( void ) {
	return qlr_mock_state.server_browser_last_filter_value;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserLastResponse
=============
*/
QLR_EXPORT uintptr_t QLR_SteamworksMock_GetServerBrowserLastResponse( void ) {
	return qlr_mock_state.server_browser_last_response;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserLastRequest
=============
*/
QLR_EXPORT uintptr_t QLR_SteamworksMock_GetServerBrowserLastRequest( void ) {
	return qlr_mock_state.server_browser_last_request;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserLastIndex
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserLastIndex( void ) {
	return qlr_mock_state.server_browser_last_index;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserLastIp
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetServerBrowserLastIp( void ) {
	return qlr_mock_state.server_browser_last_ip;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserLastPort
=============
*/
QLR_EXPORT uint16_t QLR_SteamworksMock_GetServerBrowserLastPort( void ) {
	return qlr_mock_state.server_browser_last_port;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserLastPingResponse
=============
*/
QLR_EXPORT uintptr_t QLR_SteamworksMock_GetServerBrowserLastPingResponse( void ) {
	return qlr_mock_state.server_browser_last_ping_response;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserLastPlayersResponse
=============
*/
QLR_EXPORT uintptr_t QLR_SteamworksMock_GetServerBrowserLastPlayersResponse( void ) {
	return qlr_mock_state.server_browser_last_players_response;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserLastRulesResponse
=============
*/
QLR_EXPORT uintptr_t QLR_SteamworksMock_GetServerBrowserLastRulesResponse( void ) {
	return qlr_mock_state.server_browser_last_rules_response;
}

/*
=============
QLR_SteamworksMock_GetServerBrowserLastCancelQuery
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetServerBrowserLastCancelQuery( void ) {
	return qlr_mock_state.server_browser_last_cancel_query;
}

/*
=============
QLR_SteamworksMock_GetUGCSubscribeCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCSubscribeCalls( void ) {
	return qlr_mock_state.ugc_subscribe_calls;
}

/*
=============
QLR_SteamworksMock_GetUGCUnsubscribeCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCUnsubscribeCalls( void ) {
	return qlr_mock_state.ugc_unsubscribe_calls;
}

/*
=============
QLR_SteamworksMock_GetUGCDownloadCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCDownloadCalls( void ) {
	return qlr_mock_state.ugc_download_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerUGCSubscribeCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerUGCSubscribeCalls( void ) {
	return qlr_mock_state.steam_game_server_ugc_subscribe_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerUGCUnsubscribeCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerUGCUnsubscribeCalls( void ) {
	return qlr_mock_state.steam_game_server_ugc_unsubscribe_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerUGCDownloadCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerUGCDownloadCalls( void ) {
	return qlr_mock_state.steam_game_server_ugc_download_calls;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerUGCLastItemId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetSteamGameServerUGCLastItemId( void ) {
	return qlr_mock_state.steam_game_server_ugc_last_item_id;
}

/*
=============
QLR_SteamworksMock_GetSteamGameServerUGCLastHighPriority
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetSteamGameServerUGCLastHighPriority( void ) {
	return qlr_mock_state.steam_game_server_ugc_last_high_priority;
}

/*
=============
QLR_SteamworksMock_GetUGCLastItemId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetUGCLastItemId( void ) {
	return qlr_mock_state.ugc_last_item_id;
}

/*
=============
QLR_SteamworksMock_GetUGCLastHighPriority
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCLastHighPriority( void ) {
	return qlr_mock_state.ugc_last_high_priority;
}

/*
=============
QLR_SteamworksMock_GetUGCCreateQueryCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCCreateQueryCalls( void ) {
	return qlr_mock_state.ugc_create_query_calls;
}

/*
=============
QLR_SteamworksMock_GetUGCSendQueryCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCSendQueryCalls( void ) {
	return qlr_mock_state.ugc_send_query_calls;
}

/*
=============
QLR_SteamworksMock_GetUGCReleaseQueryCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCReleaseQueryCalls( void ) {
	return qlr_mock_state.ugc_release_query_calls;
}

/*
=============
QLR_SteamworksMock_GetUGCLastQueryType
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCLastQueryType( void ) {
	return qlr_mock_state.ugc_last_query_type;
}

/*
=============
QLR_SteamworksMock_GetUGCLastMatchingType
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCLastMatchingType( void ) {
	return qlr_mock_state.ugc_last_matching_type;
}

/*
=============
QLR_SteamworksMock_GetUGCLastCreatorAppId
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetUGCLastCreatorAppId( void ) {
	return qlr_mock_state.ugc_last_creator_app_id;
}

/*
=============
QLR_SteamworksMock_GetUGCLastConsumerAppId
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetUGCLastConsumerAppId( void ) {
	return qlr_mock_state.ugc_last_consumer_app_id;
}

/*
=============
QLR_SteamworksMock_GetUGCLastFilter
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetUGCLastFilter( void ) {
	return qlr_mock_state.ugc_last_filter;
}

/*
=============
QLR_SteamworksMock_GetUGCLastQueryHandle
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetUGCLastQueryHandle( void ) {
	return qlr_mock_state.ugc_last_query_handle;
}

/*
=============
QLR_SteamworksMock_GetUGCLastSentQueryHandle
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetUGCLastSentQueryHandle( void ) {
	return qlr_mock_state.ugc_last_sent_query_handle;
}

/*
=============
QLR_SteamworksMock_GetUGCLastReleasedQueryHandle
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetUGCLastReleasedQueryHandle( void ) {
	return qlr_mock_state.ugc_last_released_query_handle;
}

/*
=============
QLR_SteamworksMock_GetUGCGetQueryResultCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCGetQueryResultCalls( void ) {
	return qlr_mock_state.ugc_get_query_result_calls;
}

/*
=============
QLR_SteamworksMock_GetUGCGetQueryPreviewCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCGetQueryPreviewCalls( void ) {
	return qlr_mock_state.ugc_get_query_preview_calls;
}

/*
=============
QLR_SteamworksMock_GetUGCLastResultQueryHandle
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetUGCLastResultQueryHandle( void ) {
	return qlr_mock_state.ugc_last_result_query_handle;
}

/*
=============
QLR_SteamworksMock_GetUGCLastPreviewQueryHandle
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetUGCLastPreviewQueryHandle( void ) {
	return qlr_mock_state.ugc_last_preview_query_handle;
}

/*
=============
QLR_SteamworksMock_GetUGCLastResultIndex
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetUGCLastResultIndex( void ) {
	return qlr_mock_state.ugc_last_result_index;
}

/*
=============
QLR_SteamworksMock_GetUGCLastPreviewIndex
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetUGCLastPreviewIndex( void ) {
	return qlr_mock_state.ugc_last_preview_index;
}

/*
=============
QLR_SteamworksMock_SetUGCQueryResult
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetUGCQueryResult( uint64_t publishedFileId, const char *title, const char *description, const char *previewUrl, int result, int previewResult ) {
	qlr_mock_state.ugc_result_published_file_id = publishedFileId;
	qlr_mock_state.ugc_query_result_success = result ? qtrue : qfalse;
	qlr_mock_state.ugc_preview_success = previewResult ? qtrue : qfalse;
	Q_strncpyz( qlr_mock_state.ugc_result_title, title ? title : "", sizeof( qlr_mock_state.ugc_result_title ) );
	Q_strncpyz( qlr_mock_state.ugc_result_description, description ? description : "", sizeof( qlr_mock_state.ugc_result_description ) );
	Q_strncpyz( qlr_mock_state.ugc_preview_url, previewUrl ? previewUrl : "", sizeof( qlr_mock_state.ugc_preview_url ) );
}

/*
=============
Com_DPrintf
=============
*/
void QDECL Com_DPrintf( const char *fmt, ... ) {
	(void)fmt;
}

/*
=============
Com_Printf
=============
*/
void QDECL Com_Printf( const char *fmt, ... ) {
	va_list args;
	va_start( args, fmt );
	vfprintf( stdout, fmt, args );
	va_end( args );
}

/*
=============
Com_sprintf
=============
*/
int QDECL Com_sprintf( char *dest, int size, const char *fmt, ... ) {
	va_list args;
	va_start( args, fmt );
	int written = vsnprintf( dest, (size_t)size, fmt, args );
	va_end( args );
	return written;
}

static const ql_platform_service_table qlr_platform_services = {
	{ qtrue, qtrue, "Steam Auth" },
	{ qtrue, qtrue, "Steam Matchmaking" },
	{ qtrue, qtrue, "Steam UGC" },
	{ qtrue, qtrue, "Steam Overlay" },
	{ qtrue, qtrue, "Steam Stats" },
};

/*
=============
QL_GetPlatformServices
=============
*/
const ql_platform_service_table *QL_GetPlatformServices( void ) {
	return &qlr_platform_services;
}

/*
=============
QL_DescribePlatformFeaturePolicy
=============
*/
const char *QL_DescribePlatformFeaturePolicy( const ql_platform_feature_descriptor *descriptor ) {
	if ( !descriptor ) {
		return "compatibility-unavailable";
	}

	if ( !descriptor->compiled ) {
		return "build-disabled";
	}

	if ( !descriptor->initialised ) {
		return "runtime-disabled";
	}

	return "enabled";
}

/*
=============
QL_GetOnlineServicesModeLabel
=============
*/
const char *QL_GetOnlineServicesModeLabel( void ) {
	return "steamworks";
}

/*
=============
QL_GetOnlineServicesPolicyLabel
=============
*/
const char *QL_GetOnlineServicesPolicyLabel( void ) {
	return "enabled";
}

/*
=============
Q_strncpyz
=============
*/
void Q_strncpyz( char *dest, const char *src, int destsize ) {
	if ( !dest || destsize <= 0 ) {
		return;
	}

	if ( !src ) {
		dest[0] = '\0';
		return;
	}

	size_t limit = (size_t)( destsize - 1 );
	strncpy( dest, src, limit );
	dest[limit] = '\0';
}

/*
=============
Info_NextPair
=============
*/
void Info_NextPair( const char **head, char *key, char *value ) {
	char *out;
	const char *cursor;

	cursor = *head;

	if ( *cursor == '\\' ) {
		cursor++;
	}

	key[0] = '\0';
	value[0] = '\0';

	out = key;
	while ( *cursor != '\\' ) {
		if ( !*cursor ) {
			*out = '\0';
			*head = cursor;
			return;
		}

		*out++ = *cursor++;
	}
	*out = '\0';
	cursor++;

	out = value;
	while ( *cursor != '\\' && *cursor ) {
		*out++ = *cursor++;
	}
	*out = '\0';

	*head = cursor;
}

/*
=============
Q_stricmp
=============
*/
int Q_stricmp( const char *s1, const char *s2 ) {
	if ( !s1 ) {
		s1 = "";
	}

	if ( !s2 ) {
		s2 = "";
	}

	while ( *s1 && *s2 ) {
		int diff = qlower( *s1++ ) - qlower( *s2++ );
		if ( diff ) {
			return diff;
		}
	}

	return qlower( *s1 ) - qlower( *s2 );
}

/*
=============
Q_stricmpn
=============
*/
int Q_stricmpn( const char *s1, const char *s2, int n ) {
	if ( n <= 0 ) {
		return 0;
	}

	if ( !s1 ) {
		s1 = "";
	}

	if ( !s2 ) {
		s2 = "";
	}

	while ( n-- > 0 ) {
		unsigned char c1 = (unsigned char)*s1++;
		unsigned char c2 = (unsigned char)*s2++;
		int diff = qlower( c1 ) - qlower( c2 );
		if ( diff || !c1 || !c2 ) {
			return diff;
		}
	}

	return 0;
}

/*
=============
dlopen
=============
*/
void *dlopen( const char *filename, int flag ) {
	(void)filename;
	(void)flag;

	return qlr_mock_state.library_available ? (void *)0x1 : NULL;
}

/*
=============
dlsym
=============
*/
void *dlsym( void *handle, const char *symbol ) {
	(void)handle;

	if ( !symbol ) {
		return NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_INIT ) == 0 ) {
		return qlr_mock_state.steam_api_init_export_available ? QLR_SteamAPI_Init : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_SHUTDOWN ) == 0 ) {
		return qlr_mock_state.steam_api_shutdown_export_available ? QLR_SteamAPI_Shutdown : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_RUN_CALLBACKS ) == 0 ) {
		return qlr_mock_state.steam_api_run_callbacks_export_available ? QLR_SteamAPI_RunCallbacks : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_REGISTER_CALLBACK ) == 0 ) {
		return qlr_mock_state.steam_api_register_callback_export_available ? QLR_SteamAPI_RegisterCallback : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_UNREGISTER_CALLBACK ) == 0 ) {
		return qlr_mock_state.steam_api_unregister_callback_export_available ? QLR_SteamAPI_UnregisterCallback : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_REGISTER_CALL_RESULT ) == 0 ) {
		return qlr_mock_state.steam_api_register_call_result_export_available ? QLR_SteamAPI_RegisterCallResult : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_UNREGISTER_CALL_RESULT ) == 0 ) {
		return qlr_mock_state.steam_api_unregister_call_result_export_available ? QLR_SteamAPI_UnregisterCallResult : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_USER ) == 0 || strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_USER ) == 0 ) {
		return qlr_mock_state.steam_user_export_available ? QLR_SteamAPI_SteamUser : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_FRIENDS ) == 0 || strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_FRIENDS ) == 0 ) {
		return qlr_mock_state.steam_friends_export_available ? QLR_SteamAPI_SteamFriends : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_UTILS ) == 0 || strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_UTILS ) == 0 ) {
		return qlr_mock_state.steam_utils_export_available ? QLR_SteamAPI_SteamUtils : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_APPS ) == 0 || strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_APPS ) == 0 ) {
		return qlr_mock_state.steam_apps_export_available ? QLR_SteamAPI_SteamApps : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_USER_STATS ) == 0 || strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_USER_STATS ) == 0 ) {
		return qlr_mock_state.steam_user_stats_export_available ? QLR_SteamAPI_SteamUserStats : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_NETWORKING ) == 0 || strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_NETWORKING ) == 0 ) {
		return qlr_mock_state.steam_networking_export_available ? QLR_SteamAPI_SteamNetworking : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_MATCHMAKING ) == 0 || strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_MATCHMAKING ) == 0 ) {
		return qlr_mock_state.steam_matchmaking_export_available ? QLR_SteamAPI_SteamMatchmaking : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_MATCHMAKING_SERVERS ) == 0 || strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_MATCHMAKING_SERVERS ) == 0 ) {
		return qlr_mock_state.steam_matchmaking_servers_export_available ? QLR_SteamAPI_SteamMatchmakingServers : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_UGC ) == 0 || strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_STEAM_UGC ) == 0 ) {
		return qlr_mock_state.steam_ugc_export_available ? QLR_SteamAPI_SteamUGC : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER ) == 0 ) {
		return qlr_mock_state.steam_game_server_export_available ? QLR_SteamAPI_SteamGameServer : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_UTILS ) == 0 ) {
		return qlr_mock_state.steam_game_server_utils_export_available ? QLR_SteamAPI_SteamGameServerUtils : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_STATS ) == 0 ) {
		return qlr_mock_state.steam_game_server_stats_export_available ? QLR_SteamAPI_SteamGameServerStats : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_UGC ) == 0 ) {
		return qlr_mock_state.steam_game_server_ugc_export_available ? QLR_SteamAPI_SteamGameServerUGC : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_INIT ) == 0 ) {
		return qlr_mock_state.steam_game_server_init_export_available ? QLR_SteamAPI_SteamGameServerInit : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_SHUTDOWN ) == 0 ) {
		return qlr_mock_state.steam_game_server_shutdown_export_available ? QLR_SteamAPI_SteamGameServerShutdown : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_RUN_CALLBACKS ) == 0 ) {
		return qlr_mock_state.steam_game_server_run_callbacks_export_available ? QLR_SteamAPI_SteamGameServerRunCallbacks : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_GAME_SERVER_NETWORKING ) == 0 ) {
		return qlr_mock_state.steam_game_server_networking_export_available ? QLR_SteamAPI_SteamGameServerNetworking : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_GET_AUTH_SESSION_TICKET ) == 0 ) {
		return qlr_mock_state.auth_session_ticket_export_available ? QLR_SteamAPI_GetAuthSessionTicket : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_GET_AUTH_TICKET_FOR_WEB_API ) == 0 ) {
		return qlr_mock_state.web_api_ticket_export_available ? QLR_SteamAPI_GetAuthTicketForWebApi : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_BEGIN_AUTH_SESSION ) == 0 ) {
		return qlr_mock_state.begin_auth_session_export_available ? QLR_SteamAPI_BeginAuthSession : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_CANCEL_AUTH_TICKET ) == 0 ) {
		return qlr_mock_state.cancel_auth_ticket_export_available ? QLR_SteamAPI_CancelAuthTicket : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_END_AUTH_SESSION ) == 0 ) {
		return qlr_mock_state.end_auth_session_export_available ? QLR_SteamAPI_EndAuthSession : NULL;
	}

	if ( strcmp( symbol, QLR_STEAMWORKS_EXPORT_STEAM_API_ISTEAMUSER_GET_STEAM_ID ) == 0 ) {
		return qlr_mock_state.get_steam_id_export_available ? QLR_SteamAPI_GetSteamID : NULL;
	}

	return NULL;
}

/*
=============
dlclose
=============
*/
int dlclose( void *handle ) {
	(void)handle;
	return 0;
}

/*
=============
QLR_SteamAPI_Init
=============
*/
qboolean QLR_SteamAPI_Init( void ) {
	return qlr_mock_state.init_result;
}

/*
=============
QLR_SteamAPI_Shutdown
=============
*/
void QLR_SteamAPI_Shutdown( void ) {
}

/*
=============
QLR_SteamAPI_RegisterCallback
=============
*/
void QLR_SteamAPI_RegisterCallback( void *object, int callbackId ) {
	qlr_callback_registration_t *registration;

	if ( !object || qlr_mock_state.registered_callback_count >= QLR_MAX_CALLBACK_REGISTRATIONS ) {
		return;
	}

	registration = &qlr_mock_state.registrations[qlr_mock_state.registered_callback_count++];
	memset( registration, 0, sizeof( *registration ) );
	registration->callResult = qfalse;
	registration->object = object;
	registration->callbackId = callbackId;
	qlr_mock_state.register_callback_calls++;
}

/*
=============
QLR_SteamAPI_UnregisterCallback
=============
*/
void QLR_SteamAPI_UnregisterCallback( void *object ) {
	int index;

	if ( !object ) {
		return;
	}

	for ( index = 0; index < qlr_mock_state.registered_callback_count; ++index ) {
		qlr_callback_registration_t *registration;

		registration = &qlr_mock_state.registrations[index];
		if ( registration->object != object || registration->callResult ) {
			continue;
		}

		if ( index + 1 < qlr_mock_state.registered_callback_count ) {
			memmove( registration, registration + 1, (size_t)( qlr_mock_state.registered_callback_count - index - 1 ) * sizeof( *registration ) );
		}
		qlr_mock_state.registered_callback_count--;
		memset( &qlr_mock_state.registrations[qlr_mock_state.registered_callback_count], 0, sizeof( qlr_mock_state.registrations[0] ) );
		qlr_mock_state.unregister_callback_calls++;
		return;
	}
}

/*
=============
QLR_SteamAPI_RegisterCallResult
=============
*/
void QLR_SteamAPI_RegisterCallResult( void *object, SteamAPICall_t callHandle ) {
	qlr_callback_registration_t *registration;

	if ( !object || callHandle == 0 || qlr_mock_state.registered_callback_count >= QLR_MAX_CALLBACK_REGISTRATIONS ) {
		return;
	}

	registration = &qlr_mock_state.registrations[qlr_mock_state.registered_callback_count++];
	memset( registration, 0, sizeof( *registration ) );
	registration->callResult = qtrue;
	registration->object = object;
	registration->callHandle = callHandle;
	qlr_mock_state.register_call_result_calls++;
}

/*
=============
QLR_SteamAPI_UnregisterCallResult
=============
*/
void QLR_SteamAPI_UnregisterCallResult( void *object, SteamAPICall_t callHandle ) {
	int index;

	if ( !object || callHandle == 0 ) {
		return;
	}

	for ( index = 0; index < qlr_mock_state.registered_callback_count; ++index ) {
		qlr_callback_registration_t *registration;

		registration = &qlr_mock_state.registrations[index];
		if ( registration->object != object || !registration->callResult || registration->callHandle != callHandle ) {
			continue;
		}

		if ( index + 1 < qlr_mock_state.registered_callback_count ) {
			memmove( registration, registration + 1, (size_t)( qlr_mock_state.registered_callback_count - index - 1 ) * sizeof( *registration ) );
		}
		qlr_mock_state.registered_callback_count--;
		memset( &qlr_mock_state.registrations[qlr_mock_state.registered_callback_count], 0, sizeof( qlr_mock_state.registrations[0] ) );
		qlr_mock_state.unregister_call_result_calls++;
		return;
	}
}

/*
=============
QLR_SteamworksMock_DispatchPendingCallbacks

Delivers queued callback payloads through the registered Steam callback objects.
=============
*/
static void QLR_SteamworksMock_DispatchPendingCallbacks( qboolean gameServer ) {
	int pendingIndex;
	int retainedCount;

	retainedCount = 0;
	for ( pendingIndex = 0; pendingIndex < qlr_mock_state.pending_callback_count; ++pendingIndex ) {
		qlr_pending_callback_t *pending;
		int registrationIndex;

		pending = &qlr_mock_state.pending_callbacks[pendingIndex];
		if ( pending->gameServer != gameServer ) {
			if ( retainedCount != pendingIndex ) {
				memcpy( &qlr_mock_state.pending_callbacks[retainedCount], pending, sizeof( *pending ) );
			}
			retainedCount++;
			continue;
		}

		for ( registrationIndex = 0; registrationIndex < qlr_mock_state.registered_callback_count; ++registrationIndex ) {
			qlr_callback_registration_t *registration;
			qlr_callback_base_t *callbackBase;
			qboolean callbackGameServer;

			registration = &qlr_mock_state.registrations[registrationIndex];
			if ( pending->callResult != registration->callResult ) {
				continue;
			}

			if ( pending->callResult ) {
				if ( registration->callHandle != pending->callHandle ) {
					continue;
				}
			} else if ( registration->callbackId != pending->callbackId ) {
				continue;
			}

			callbackBase = (qlr_callback_base_t *)registration->object;
			if ( !callbackBase || !callbackBase->vtable ) {
				continue;
			}

			callbackGameServer = ( callbackBase->callbackFlags & QLR_STEAM_CALLBACK_FLAG_GAMESERVER ) ? qtrue : qfalse;
			if ( callbackGameServer != gameServer ) {
				continue;
			}

			if ( pending->callResult ) {
				if ( callbackBase->vtable->runCallResult ) {
					callbackBase->vtable->runCallResult( callbackBase, pending->payload, pending->ioFailure, pending->callHandle );
				}
			} else if ( callbackBase->vtable->run ) {
				callbackBase->vtable->run( callbackBase, pending->payload );
			}
		}
	}

	if ( retainedCount < qlr_mock_state.pending_callback_count ) {
		memset( &qlr_mock_state.pending_callbacks[retainedCount], 0, (size_t)( qlr_mock_state.pending_callback_count - retainedCount ) * sizeof( qlr_mock_state.pending_callbacks[0] ) );
	}
	qlr_mock_state.pending_callback_count = retainedCount;
}

/*
=============
QLR_SteamAPI_RunCallbacks
=============
*/
void QLR_SteamAPI_RunCallbacks( void ) {
	QLR_SteamworksMock_DispatchPendingCallbacks( qfalse );
}

/*
=============
QLR_SteamAPI_SteamGameServerInit
=============
*/
qboolean QLR_SteamAPI_SteamGameServerInit( uint32_t ip, uint16_t steamPort, uint16_t gamePort, uint16_t queryPort, int serverMode, const char *version ) {
	qlr_mock_state.steam_game_server_init_calls++;
	qlr_mock_state.steam_game_server_last_init_ip = ip;
	qlr_mock_state.steam_game_server_last_init_steam_port = steamPort;
	qlr_mock_state.steam_game_server_last_init_game_port = gamePort;
	qlr_mock_state.steam_game_server_last_init_query_port = queryPort;
	qlr_mock_state.steam_game_server_last_init_server_mode = serverMode;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_init_version, version ? version : "", sizeof( qlr_mock_state.steam_game_server_last_init_version ) );
	return qlr_mock_state.steam_game_server_init_result;
}

/*
=============
QLR_SteamAPI_SteamGameServerShutdown
=============
*/
void QLR_SteamAPI_SteamGameServerShutdown( void ) {
	qlr_mock_state.steam_game_server_shutdown_calls++;
}

/*
=============
QLR_SteamAPI_SteamGameServerRunCallbacks
=============
*/
void QLR_SteamAPI_SteamGameServerRunCallbacks( void ) {
	qlr_mock_state.steam_game_server_callback_calls++;
	QLR_SteamworksMock_DispatchPendingCallbacks( qtrue );
}

/*
=============
QLR_SteamAPI_SteamUser
=============
*/
void *QLR_SteamAPI_SteamUser( void ) {
	static void *vtable[QLR_STEAM_USER_VTABLE_SLOT_COUNT];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[QLR_STEAM_USER_BLOGGED_ON_SLOT] = QLR_SteamUser_BLoggedOn;
	vtable[QLR_STEAM_USER_GET_STEAM_ID_SLOT] = QLR_SteamUser_GetSteamID;
	vtable[QLR_STEAM_USER_START_VOICE_RECORDING_SLOT] = QLR_SteamUser_StartVoiceRecording;
	vtable[QLR_STEAM_USER_STOP_VOICE_RECORDING_SLOT] = QLR_SteamUser_StopVoiceRecording;
	vtable[QLR_STEAM_USER_GET_VOICE_SLOT] = QLR_SteamUser_GetVoice;
	vtable[QLR_STEAM_USER_DECOMPRESS_VOICE_SLOT] = QLR_SteamUser_DecompressVoice;
	vtable[QLR_STEAM_USER_GET_VOICE_OPTIMAL_SAMPLE_RATE_SLOT] = QLR_SteamUser_GetVoiceOptimalSampleRate;
	return qlr_mock_state.user_available ? &iface : NULL;
}

/*
=============
QLR_SteamworksMock_IsAvatarHandle
=============
*/
static qboolean QLR_SteamworksMock_IsAvatarHandle( int image ) {
	return image > 0 &&
		( image == qlr_mock_state.avatar_handle_small ||
			image == qlr_mock_state.avatar_handle_medium ||
			image == qlr_mock_state.avatar_handle_large );
}

/*
=============
QLR_SteamUser_BLoggedOn
=============
*/
static qboolean QLR_FASTCALL QLR_SteamUser_BLoggedOn( void *self, void *unused ) {
	(void)self;
	(void)unused;

	qlr_mock_state.user_logged_on_calls++;
	return qlr_mock_state.user_logged_on_result ? qtrue : qfalse;
}

/*
=============
QLR_SteamUser_GetSteamID
=============
*/
static CSteamID *QLR_FASTCALL QLR_SteamUser_GetSteamID( void *self, void *unused, CSteamID *outSteamId ) {
	(void)self;
	(void)unused;

	qlr_mock_state.user_steam_id_calls++;
	if ( outSteamId ) {
		outSteamId->value = qlr_mock_state.steam_id_value;
	}

	return outSteamId;
}

/*
=============
QLR_SteamUser_StartVoiceRecording
=============
*/
static void QLR_FASTCALL QLR_SteamUser_StartVoiceRecording( void *self, void *unused ) {
	(void)self;
	(void)unused;

	qlr_mock_state.voice_start_calls++;
}

/*
=============
QLR_SteamUser_StopVoiceRecording
=============
*/
static void QLR_FASTCALL QLR_SteamUser_StopVoiceRecording( void *self, void *unused ) {
	(void)self;
	(void)unused;

	qlr_mock_state.voice_stop_calls++;
}

/*
=============
QLR_SteamUser_GetVoice
=============
*/
static int QLR_FASTCALL QLR_SteamUser_GetVoice( void *self, void *unused, qboolean wantCompressed, void *destBuffer, uint32_t destBufferSize, uint32_t *outCompressedBytes, qboolean wantUncompressed, void *uncompressedBuffer, uint32_t uncompressedBufferSize, uint32_t *outUncompressedBytes, uint32_t uncompressedSampleRate ) {
	(void)self;
	(void)unused;
	(void)uncompressedBuffer;
	(void)uncompressedSampleRate;

	qlr_mock_state.voice_get_calls++;
	qlr_mock_state.voice_last_want_compressed = wantCompressed;
	qlr_mock_state.voice_last_want_uncompressed = wantUncompressed;
	qlr_mock_state.voice_last_compressed_buffer_size = destBufferSize;
	qlr_mock_state.voice_last_uncompressed_buffer_size = uncompressedBufferSize;

	if ( outCompressedBytes ) {
		*outCompressedBytes = 0u;
	}
	if ( outUncompressedBytes ) {
		*outUncompressedBytes = 0u;
	}

	if ( qlr_mock_state.voice_get_result != 0 ) {
		return qlr_mock_state.voice_get_result;
	}
	if ( wantCompressed && destBuffer && outCompressedBytes && destBufferSize >= qlr_mock_state.voice_compressed_length ) {
		if ( qlr_mock_state.voice_compressed_length > 0u ) {
			memcpy( destBuffer, qlr_mock_state.voice_compressed_data, qlr_mock_state.voice_compressed_length );
		}
		*outCompressedBytes = qlr_mock_state.voice_compressed_length;
	}
	if ( wantUncompressed && outUncompressedBytes ) {
		*outUncompressedBytes = 0u;
	}

	return 0;
}

/*
=============
QLR_SteamUser_DecompressVoice
=============
*/
static int QLR_FASTCALL QLR_SteamUser_DecompressVoice( void *self, void *unused, const void *compressedData, uint32_t compressedSize, void *destBuffer, uint32_t destBufferSize, uint32_t *outBytesWritten, uint32_t sampleRate ) {
	(void)self;
	(void)unused;
	(void)compressedData;

	qlr_mock_state.voice_decompress_calls++;
	qlr_mock_state.voice_last_decompress_input_size = compressedSize;
	qlr_mock_state.voice_last_decompress_buffer_size = destBufferSize;
	qlr_mock_state.voice_last_decompress_sample_rate = sampleRate;

	if ( outBytesWritten ) {
		*outBytesWritten = 0u;
	}

	if ( qlr_mock_state.voice_decompress_result != 0 ) {
		return qlr_mock_state.voice_decompress_result;
	}
	if ( !destBuffer || !outBytesWritten || destBufferSize < qlr_mock_state.voice_decompressed_length ) {
		return 2;
	}
	if ( qlr_mock_state.voice_decompressed_length > 0u ) {
		memcpy( destBuffer, qlr_mock_state.voice_decompressed_data, qlr_mock_state.voice_decompressed_length );
	}
	*outBytesWritten = qlr_mock_state.voice_decompressed_length;
	return 0;
}

/*
=============
QLR_SteamUser_GetVoiceOptimalSampleRate
=============
*/
static uint32_t QLR_FASTCALL QLR_SteamUser_GetVoiceOptimalSampleRate( void *self, void *unused ) {
	(void)self;
	(void)unused;

	qlr_mock_state.voice_optimal_rate_calls++;
	return qlr_mock_state.voice_optimal_sample_rate;
}

/*
=============
QLR_SteamGameServer_GetSteamID
=============
*/
static CSteamID *QLR_FASTCALL QLR_SteamGameServer_GetSteamID( void *self, void *unused, CSteamID *outSteamId ) {
	(void)self;
	(void)unused;

	if ( outSteamId ) {
		outSteamId->value = qlr_mock_state.steam_game_server_id_value;
	}

	return outSteamId;
}

/*
=============
QLR_SteamGameServer_CreateUnauthenticatedUserConnection
=============
*/
static CSteamID *QLR_FASTCALL QLR_SteamGameServer_CreateUnauthenticatedUserConnection( void *self, void *unused, CSteamID *outSteamId ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_unauthenticated_user_calls++;

	if ( outSteamId ) {
		outSteamId->value = qlr_mock_state.steam_game_server_unauthenticated_user_id_value;
	}

	return outSteamId;
}

/*
=============
QLR_SteamGameServer_BLoggedOn
=============
*/
static qboolean QLR_FASTCALL QLR_SteamGameServer_BLoggedOn( void *self, void *unused ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_logged_on_calls++;
	return qlr_mock_state.steam_game_server_logged_on_result ? qtrue : qfalse;
}

/*
=============
QLR_SteamGameServer_GetPublicIP
=============
*/
static uint32_t QLR_FASTCALL QLR_SteamGameServer_GetPublicIP( void *self, void *unused ) {
	(void)self;
	(void)unused;
	return qlr_mock_state.steam_game_server_public_ip;
}

/*
=============
QLR_SteamGameServer_HandleIncomingPacket
=============
*/
static qboolean QLR_FASTCALL QLR_SteamGameServer_HandleIncomingPacket( void *self, void *unused, const void *data, int dataSize, uint32_t ip, uint16_t port ) {
	int copiedLength;

	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_incoming_packet_calls++;
	qlr_mock_state.steam_game_server_incoming_packet_ip = ip;
	qlr_mock_state.steam_game_server_incoming_packet_port = port;

	copiedLength = dataSize;
	if ( copiedLength < 0 ) {
		copiedLength = 0;
	}
	if ( copiedLength > (int)sizeof( qlr_mock_state.steam_game_server_incoming_packet_data ) ) {
		copiedLength = (int)sizeof( qlr_mock_state.steam_game_server_incoming_packet_data );
	}

	memset( qlr_mock_state.steam_game_server_incoming_packet_data, 0, sizeof( qlr_mock_state.steam_game_server_incoming_packet_data ) );
	if ( data && copiedLength > 0 ) {
		memcpy( qlr_mock_state.steam_game_server_incoming_packet_data, data, (size_t)copiedLength );
	}
	qlr_mock_state.steam_game_server_incoming_packet_length = copiedLength;

	return data && dataSize > 0 && qlr_mock_state.steam_game_server_incoming_packet_result ? qtrue : qfalse;
}

/*
=============
QLR_SteamGameServer_GetNextOutgoingPacket
=============
*/
static int QLR_FASTCALL QLR_SteamGameServer_GetNextOutgoingPacket( void *self, void *unused, void *data, int dataSize, uint32_t *outIp, uint16_t *outPort ) {
	int length;

	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_outgoing_packet_calls++;

	if ( outIp ) {
		*outIp = 0u;
	}
	if ( outPort ) {
		*outPort = 0u;
	}

	length = qlr_mock_state.steam_game_server_outgoing_packet_length;
	if ( !data || dataSize <= 0 || !outIp || !outPort || length <= 0 || dataSize < length ) {
		return 0;
	}

	memcpy( data, qlr_mock_state.steam_game_server_outgoing_packet_data, (size_t)length );
	*outIp = qlr_mock_state.steam_game_server_outgoing_packet_ip;
	*outPort = qlr_mock_state.steam_game_server_outgoing_packet_port;
	qlr_mock_state.steam_game_server_outgoing_packet_length = 0;
	return length;
}

/*
=============
QLR_SteamNetworking_SendP2PPacket
=============
*/
static qboolean QLR_FASTCALL QLR_SteamNetworking_SendP2PPacket( void *self, void *unused, CSteamID steamId, const void *data, uint32_t length, int sendType, int channel ) {
	uint32_t copiedLength;

	(void)self;
	(void)unused;

	qlr_mock_state.p2p_send_calls++;
	qlr_mock_state.p2p_last_send_steam_id = steamId.value;
	qlr_mock_state.p2p_last_send_type = sendType;
	qlr_mock_state.p2p_last_send_channel = channel;

	copiedLength = length;
	if ( copiedLength > sizeof( qlr_mock_state.p2p_last_send_data ) ) {
		copiedLength = sizeof( qlr_mock_state.p2p_last_send_data );
	}

	memset( qlr_mock_state.p2p_last_send_data, 0, sizeof( qlr_mock_state.p2p_last_send_data ) );
	if ( data && copiedLength > 0u ) {
		memcpy( qlr_mock_state.p2p_last_send_data, data, copiedLength );
	}
	qlr_mock_state.p2p_last_send_length = copiedLength;

	return data && length > 0u && qlr_mock_state.p2p_send_result ? qtrue : qfalse;
}

/*
=============
QLR_SteamNetworking_IsP2PPacketAvailable
=============
*/
static qboolean QLR_FASTCALL QLR_SteamNetworking_IsP2PPacketAvailable( void *self, void *unused, uint32_t *outSize, int channel ) {
	(void)self;
	(void)unused;

	qlr_mock_state.p2p_available_calls++;
	qlr_mock_state.p2p_last_available_channel = channel;

	if ( outSize ) {
		*outSize = qlr_mock_state.p2p_available_result ? qlr_mock_state.p2p_available_size : 0u;
	}

	return outSize && qlr_mock_state.p2p_available_result ? qtrue : qfalse;
}

/*
=============
QLR_SteamNetworking_ReadP2PPacket
=============
*/
static qboolean QLR_FASTCALL QLR_SteamNetworking_ReadP2PPacket( void *self, void *unused, void *data, uint32_t dataSize, uint32_t *outSize, CSteamID *outSteamId, int channel ) {
	(void)self;
	(void)unused;

	qlr_mock_state.p2p_read_calls++;
	qlr_mock_state.p2p_last_read_channel = channel;

	if ( outSize ) {
		*outSize = 0u;
	}
	if ( outSteamId ) {
		outSteamId->value = 0ull;
	}

	if ( !data || !outSize || !outSteamId || !qlr_mock_state.p2p_read_result || dataSize < qlr_mock_state.p2p_read_length ) {
		return qfalse;
	}

	memcpy( data, qlr_mock_state.p2p_read_data, qlr_mock_state.p2p_read_length );
	*outSize = qlr_mock_state.p2p_read_length;
	outSteamId->value = qlr_mock_state.p2p_read_steam_id;
	return qtrue;
}

/*
=============
QLR_SteamNetworking_AcceptP2PSessionWithUser
=============
*/
static qboolean QLR_FASTCALL QLR_SteamNetworking_AcceptP2PSessionWithUser( void *self, void *unused, CSteamID steamId ) {
	(void)self;
	(void)unused;

	qlr_mock_state.p2p_accept_calls++;
	qlr_mock_state.p2p_last_accept_steam_id = steamId.value;
	return qlr_mock_state.p2p_accept_result ? qtrue : qfalse;
}

/*
=============
QLR_SteamGameServerNetworking_SendP2PPacket
=============
*/
static qboolean QLR_FASTCALL QLR_SteamGameServerNetworking_SendP2PPacket( void *self, void *unused, CSteamID steamId, const void *data, uint32_t length, int sendType, int channel ) {
	uint32_t copiedLength;

	(void)self;
	(void)unused;

	qlr_mock_state.server_p2p_send_calls++;
	qlr_mock_state.server_p2p_last_send_steam_id = steamId.value;
	qlr_mock_state.server_p2p_last_send_type = sendType;
	qlr_mock_state.server_p2p_last_send_channel = channel;

	copiedLength = length;
	if ( copiedLength > sizeof( qlr_mock_state.server_p2p_last_send_data ) ) {
		copiedLength = sizeof( qlr_mock_state.server_p2p_last_send_data );
	}

	memset( qlr_mock_state.server_p2p_last_send_data, 0, sizeof( qlr_mock_state.server_p2p_last_send_data ) );
	if ( data && copiedLength > 0u ) {
		memcpy( qlr_mock_state.server_p2p_last_send_data, data, copiedLength );
	}
	qlr_mock_state.server_p2p_last_send_length = copiedLength;

	return data && length > 0u && qlr_mock_state.server_p2p_send_result ? qtrue : qfalse;
}

/*
=============
QLR_SteamGameServerNetworking_IsP2PPacketAvailable
=============
*/
static qboolean QLR_FASTCALL QLR_SteamGameServerNetworking_IsP2PPacketAvailable( void *self, void *unused, uint32_t *outSize, int channel ) {
	(void)self;
	(void)unused;

	qlr_mock_state.server_p2p_available_calls++;
	qlr_mock_state.server_p2p_last_available_channel = channel;

	if ( outSize ) {
		*outSize = qlr_mock_state.server_p2p_available_result ? qlr_mock_state.server_p2p_available_size : 0u;
	}

	return outSize && qlr_mock_state.server_p2p_available_result ? qtrue : qfalse;
}

/*
=============
QLR_SteamGameServerNetworking_ReadP2PPacket
=============
*/
static qboolean QLR_FASTCALL QLR_SteamGameServerNetworking_ReadP2PPacket( void *self, void *unused, void *data, uint32_t dataSize, uint32_t *outSize, CSteamID *outSteamId, int channel ) {
	(void)self;
	(void)unused;

	qlr_mock_state.server_p2p_read_calls++;
	qlr_mock_state.server_p2p_last_read_channel = channel;

	if ( outSize ) {
		*outSize = 0u;
	}
	if ( outSteamId ) {
		outSteamId->value = 0ull;
	}

	if ( !data || !outSize || !outSteamId || !qlr_mock_state.server_p2p_read_result || dataSize < qlr_mock_state.server_p2p_read_length ) {
		return qfalse;
	}

	memcpy( data, qlr_mock_state.server_p2p_read_data, qlr_mock_state.server_p2p_read_length );
	*outSize = qlr_mock_state.server_p2p_read_length;
	outSteamId->value = qlr_mock_state.server_p2p_read_steam_id;
	return qtrue;
}

/*
=============
QLR_SteamGameServerNetworking_AcceptP2PSessionWithUser
=============
*/
static qboolean QLR_FASTCALL QLR_SteamGameServerNetworking_AcceptP2PSessionWithUser( void *self, void *unused, CSteamID steamId ) {
	(void)self;
	(void)unused;

	qlr_mock_state.server_p2p_accept_calls++;
	qlr_mock_state.server_p2p_last_accept_steam_id = steamId.value;
	return qlr_mock_state.server_p2p_accept_result ? qtrue : qfalse;
}

/*
=============
QLR_SteamGameServer_EnableHeartbeats
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_EnableHeartbeats( void *self, void *unused, int enable ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_heartbeat_calls++;
	qlr_mock_state.steam_game_server_last_heartbeat_enabled = enable;
}

/*
=============
QLR_SteamGameServer_SetDedicated
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetDedicated( void *self, void *unused, int dedicated ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_dedicated_calls++;
	qlr_mock_state.steam_game_server_last_dedicated = dedicated;
}

/*
=============
QLR_SteamGameServer_LogOn
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_LogOn( void *self, void *unused, const char *account ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_logon_calls++;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_account, account ? account : "", sizeof( qlr_mock_state.steam_game_server_last_account ) );
}

/*
=============
QLR_SteamGameServer_LogOnAnonymous
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_LogOnAnonymous( void *self, void *unused ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_logon_anonymous_calls++;
}

/*
=============
QLR_SteamGameServer_SetProduct
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetProduct( void *self, void *unused, const char *product ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_product_calls++;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_product, product ? product : "", sizeof( qlr_mock_state.steam_game_server_last_product ) );
}

/*
=============
QLR_SteamGameServer_SetGameDir
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetGameDir( void *self, void *unused, const char *gameDir ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_game_dir_calls++;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_game_dir, gameDir ? gameDir : "", sizeof( qlr_mock_state.steam_game_server_last_game_dir ) );
}

/*
=============
QLR_SteamGameServer_SetGameDescription
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetGameDescription( void *self, void *unused, const char *description ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_game_description_calls++;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_game_description, description ? description : "", sizeof( qlr_mock_state.steam_game_server_last_game_description ) );
}

/*
=============
QLR_SteamGameServer_SetMaxPlayerCount
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetMaxPlayerCount( void *self, void *unused, int maxPlayers ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_max_player_count_calls++;
	qlr_mock_state.steam_game_server_last_max_player_count = maxPlayers;
}

/*
=============
QLR_SteamGameServer_SetBotPlayerCount
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetBotPlayerCount( void *self, void *unused, int botPlayers ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_bot_player_count_calls++;
	qlr_mock_state.steam_game_server_last_bot_player_count = botPlayers;
}

/*
=============
QLR_SteamGameServer_SetServerName
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetServerName( void *self, void *unused, const char *name ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_server_name_calls++;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_server_name, name ? name : "", sizeof( qlr_mock_state.steam_game_server_last_server_name ) );
}

/*
=============
QLR_SteamGameServer_SetMapName
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetMapName( void *self, void *unused, const char *mapName ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_map_name_calls++;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_map_name, mapName ? mapName : "", sizeof( qlr_mock_state.steam_game_server_last_map_name ) );
}

/*
=============
QLR_SteamGameServer_SetPasswordProtected
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetPasswordProtected( void *self, void *unused, int passwordProtected ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_password_calls++;
	qlr_mock_state.steam_game_server_last_password_protected = passwordProtected;
}

/*
=============
QLR_SteamGameServer_SetGameTags
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetGameTags( void *self, void *unused, const char *tags ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_game_tags_calls++;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_game_tags, tags ? tags : "", sizeof( qlr_mock_state.steam_game_server_last_game_tags ) );
}

/*
=============
QLR_SteamGameServer_SetKeyValue
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetKeyValue( void *self, void *unused, const char *key, const char *value ) {
	(void)self;
	(void)unused;

	Q_strncpyz( qlr_mock_state.steam_game_server_last_key, key ? key : "", sizeof( qlr_mock_state.steam_game_server_last_key ) );
	Q_strncpyz( qlr_mock_state.steam_game_server_last_value, value ? value : "", sizeof( qlr_mock_state.steam_game_server_last_value ) );
	qlr_mock_state.steam_game_server_key_value_calls++;
}

/*
=============
QLR_SteamGameServer_UpdateUserData
=============
*/
static int QLR_FASTCALL QLR_SteamGameServer_UpdateUserData( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *playerName, uint32_t score ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_user_data_calls++;
	qlr_mock_state.steam_game_server_last_user_data_id = ((uint64_t)idHigh << 32) | (uint64_t)idLow;
	qlr_mock_state.steam_game_server_last_user_data_score = score;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_user_data_name, playerName ? playerName : "", sizeof( qlr_mock_state.steam_game_server_last_user_data_name ) );
	return 1;
}

/*
=============
QLR_SteamGameServer_BeginAuthSession
=============
*/
static EBeginAuthSessionResult QLR_FASTCALL QLR_SteamGameServer_BeginAuthSession( void *self, void *unused, const void *ticket, int length, CSteamID steamId ) {
	(void)unused;
	return QLR_SteamAPI_BeginAuthSession( self, ticket, length, steamId );
}

/*
=============
QLR_SteamGameServer_EndAuthSession
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_EndAuthSession( void *self, void *unused, CSteamID steamId ) {
	(void)unused;
	QLR_SteamAPI_EndAuthSession( self, steamId );
}

/*
=============
QLR_SteamFriends_GetPersonaName
=============
*/
static const char *QLR_FASTCALL QLR_SteamFriends_GetPersonaName( void *self, void *unused ) {
	(void)self;
	(void)unused;

	qlr_mock_state.persona_name_calls++;
	return qlr_mock_state.persona_name;
}

/*
=============
QLR_SteamFriends_GetFriendCount
=============
*/
static int QLR_FASTCALL QLR_SteamFriends_GetFriendCount( void *self, void *unused, int flags ) {
	(void)self;
	(void)unused;

	qlr_mock_state.friend_count_calls++;
	qlr_mock_state.friend_last_count_flags = flags;
	return qlr_mock_state.friend_count;
}

/*
=============
QLR_SteamFriends_GetFriendByIndex
=============
*/
static CSteamID *QLR_FASTCALL QLR_SteamFriends_GetFriendByIndex( void *self, void *unused, CSteamID *outSteamId, int index, int flags ) {
	(void)self;
	(void)unused;

	qlr_mock_state.friend_by_index_calls++;
	qlr_mock_state.friend_last_index = index;
	qlr_mock_state.friend_last_index_flags = flags;

	if ( outSteamId ) {
		outSteamId->value = 0ull;
		if ( index >= 0 && index < qlr_mock_state.friend_count ) {
			outSteamId->value = qlr_mock_state.friend_by_index_id;
		}
	}

	return outSteamId;
}

/*
=============
QLR_SteamFriends_GetFriendRelationship
=============
*/
static int QLR_FASTCALL QLR_SteamFriends_GetFriendRelationship( void *self, void *unused, CSteamID steamId ) {
	(void)self;
	(void)unused;
	(void)steamId;
	return qlr_mock_state.friend_relationship;
}

/*
=============
QLR_SteamFriends_GetFriendPersonaState
=============
*/
static int QLR_FASTCALL QLR_SteamFriends_GetFriendPersonaState( void *self, void *unused, CSteamID steamId ) {
	(void)self;
	(void)unused;
	(void)steamId;
	return qlr_mock_state.friend_persona_state;
}

/*
=============
QLR_SteamFriends_GetFriendPersonaName
=============
*/
static const char *QLR_FASTCALL QLR_SteamFriends_GetFriendPersonaName( void *self, void *unused, CSteamID steamId ) {
	(void)self;
	(void)unused;
	(void)steamId;
	return qlr_mock_state.persona_name;
}

/*
=============
QLR_SteamFriends_GetFriendGamePlayed
=============
*/
static int QLR_FASTCALL QLR_SteamFriends_GetFriendGamePlayed( void *self, void *unused, CSteamID steamId, void *outGameInfo ) {
	typedef struct {
		uint64_t gameId;
		uint32_t gameIp;
		uint16_t gamePort;
		uint16_t queryPort;
		CSteamID lobbyId;
		CSteamID gameServerId;
	} qlr_friend_game_info_t;
	qlr_friend_game_info_t *gameInfo;

	(void)self;
	(void)unused;
	(void)steamId;

	if ( !outGameInfo || qlr_mock_state.friend_game_id == 0ull ) {
		return 0;
	}

	gameInfo = (qlr_friend_game_info_t *)outGameInfo;
	memset( gameInfo, 0, sizeof( *gameInfo ) );
	gameInfo->gameId = qlr_mock_state.friend_game_id;
	gameInfo->gameIp = qlr_mock_state.friend_game_ip;
	gameInfo->gamePort = qlr_mock_state.friend_game_port;
	gameInfo->queryPort = qlr_mock_state.friend_query_port;
	gameInfo->lobbyId.value = qlr_mock_state.friend_lobby_id;
	gameInfo->gameServerId.value = qlr_mock_state.friend_game_server_id;
	return 1;
}

/*
=============
QLR_SteamFriends_GetPlayerNickname
=============
*/
static const char *QLR_FASTCALL QLR_SteamFriends_GetPlayerNickname( void *self, void *unused, CSteamID steamId ) {
	(void)self;
	(void)unused;
	(void)steamId;
	return qlr_mock_state.friend_nickname;
}

/*
=============
QLR_SteamFriends_GetFriendRichPresence
=============
*/
static const char *QLR_FASTCALL QLR_SteamFriends_GetFriendRichPresence( void *self, void *unused, CSteamID steamId, const char *key ) {
	(void)self;
	(void)unused;
	(void)steamId;

	if ( !key ) {
		return "";
	}

	if ( strcmp( key, "status" ) == 0 ) {
		return qlr_mock_state.friend_status;
	}

	if ( strcmp( key, "lanIp" ) == 0 ) {
		return qlr_mock_state.friend_lan_ip;
	}

	return "";
}

/*
=============
QLR_SteamFriends_ActivateGameOverlayToUser
=============
*/
static void QLR_FASTCALL QLR_SteamFriends_ActivateGameOverlayToUser( void *self, void *unused, const char *dialog, CSteamID steamId ) {
	(void)self;
	(void)unused;

	Q_strncpyz( qlr_mock_state.overlay_dialog, dialog ? dialog : "", sizeof( qlr_mock_state.overlay_dialog ) );
	qlr_mock_state.overlay_steam_id = steamId.value;
	qlr_mock_state.overlay_calls++;
}

/*
=============
QLR_SteamFriends_ActivateGameOverlayToWebPage
=============
*/
static void QLR_FASTCALL QLR_SteamFriends_ActivateGameOverlayToWebPage( void *self, void *unused, const char *url ) {
	(void)self;
	(void)unused;

	Q_strncpyz( qlr_mock_state.overlay_web_url, url ? url : "", sizeof( qlr_mock_state.overlay_web_url ) );
	qlr_mock_state.overlay_web_calls++;
}

/*
=============
QLR_SteamFriends_SetInGameVoiceSpeaking
=============
*/
static void QLR_FASTCALL QLR_SteamFriends_SetInGameVoiceSpeaking( void *self, void *unused, CSteamID steamId, int speaking ) {
	(void)self;
	(void)unused;

	qlr_mock_state.friend_voice_speaking_calls++;
	qlr_mock_state.friend_voice_last_steam_id = steamId.value;
	qlr_mock_state.friend_voice_last_speaking = speaking;
}

/*
=============
QLR_SteamFriends_SetRichPresence
=============
*/
static int QLR_FASTCALL QLR_SteamFriends_SetRichPresence( void *self, void *unused, const char *key, const char *value ) {
	(void)self;
	(void)unused;

	Q_strncpyz( qlr_mock_state.rich_presence_key, key ? key : "", sizeof( qlr_mock_state.rich_presence_key ) );
	Q_strncpyz( qlr_mock_state.rich_presence_value, value ? value : "", sizeof( qlr_mock_state.rich_presence_value ) );
	qlr_mock_state.rich_presence_calls++;
	return qlr_mock_state.rich_presence_result;
}

/*
=============
QLR_SteamFriends_ActivateGameOverlayInviteDialog
=============
*/
static void QLR_FASTCALL QLR_SteamFriends_ActivateGameOverlayInviteDialog( void *self, void *unused, uint32_t idLow, uint32_t idHigh ) {
	(void)self;
	(void)unused;

	qlr_mock_state.lobby_invite_calls++;
	qlr_mock_state.lobby_invite_id = ( (uint64_t)idHigh << 32 ) | idLow;
}

/*
=============
QLR_SteamFriends_InviteUserToGame
=============
*/
static int QLR_FASTCALL QLR_SteamFriends_InviteUserToGame( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *connectString ) {
	(void)self;
	(void)unused;

	qlr_mock_state.game_invite_calls++;
	qlr_mock_state.game_invite_target_id = ( (uint64_t)idHigh << 32 ) | idLow;
	Q_strncpyz( qlr_mock_state.game_invite_connect_string, connectString ? connectString : "", sizeof( qlr_mock_state.game_invite_connect_string ) );
	return 1;
}

/*
=============
QLR_SteamFriends_GetSmallFriendAvatar
=============
*/
static int QLR_FASTCALL QLR_SteamFriends_GetSmallFriendAvatar( void *self, void *unused, CSteamID steamId ) {
	(void)self;
	(void)unused;
	(void)steamId;
	return qlr_mock_state.avatar_handle_small;
}

/*
=============
QLR_SteamFriends_GetMediumFriendAvatar
=============
*/
static int QLR_FASTCALL QLR_SteamFriends_GetMediumFriendAvatar( void *self, void *unused, CSteamID steamId ) {
	(void)self;
	(void)unused;
	(void)steamId;
	return qlr_mock_state.avatar_handle_medium;
}

/*
=============
QLR_SteamFriends_GetLargeFriendAvatar
=============
*/
static int QLR_FASTCALL QLR_SteamFriends_GetLargeFriendAvatar( void *self, void *unused, CSteamID steamId ) {
	(void)self;
	(void)unused;
	(void)steamId;
	return qlr_mock_state.avatar_handle_large;
}

/*
=============
QLR_SteamUtils_GetIPCountry
=============
*/
static const char *QLR_FASTCALL QLR_SteamUtils_GetIPCountry( void *self, void *unused ) {
	(void)self;
	(void)unused;

	qlr_mock_state.ip_country_calls++;
	return qlr_mock_state.ip_country;
}

/*
=============
QLR_SteamUtils_GetAppID
=============
*/
static uint32_t QLR_FASTCALL QLR_SteamUtils_GetAppID( void *self, void *unused ) {
	(void)self;
	(void)unused;

	qlr_mock_state.app_id_calls++;
	return qlr_mock_state.app_id;
}

/*
=============
QLR_SteamGameServerUtils_GetAppID
=============
*/
static uint32_t QLR_FASTCALL QLR_SteamGameServerUtils_GetAppID( void *self, void *unused ) {
	(void)self;
	(void)unused;
	return qlr_mock_state.app_id;
}

/*
=============
QLR_SteamUtils_GetImageSize
=============
*/
static int QLR_FASTCALL QLR_SteamUtils_GetImageSize( void *self, void *unused, int image, uint32_t *width, uint32_t *height ) {
	(void)self;
	(void)unused;

	if ( width ) {
		*width = 0;
	}
	if ( height ) {
		*height = 0;
	}

	if ( !width || !height || !QLR_SteamworksMock_IsAvatarHandle( image ) || !qlr_mock_state.avatar_width || !qlr_mock_state.avatar_height ) {
		return 0;
	}

	*width = qlr_mock_state.avatar_width;
	*height = qlr_mock_state.avatar_height;
	return 1;
}

/*
=============
QLR_SteamUtils_GetImageRGBA
=============
*/
static int QLR_FASTCALL QLR_SteamUtils_GetImageRGBA( void *self, void *unused, int image, uint8_t *buffer, int length ) {
	size_t requiredLength = (size_t)qlr_mock_state.avatar_width * (size_t)qlr_mock_state.avatar_height * 4;

	(void)self;
	(void)unused;

	if ( !buffer || length <= 0 || !QLR_SteamworksMock_IsAvatarHandle( image ) ) {
		return 0;
	}

	if ( requiredLength == 0 || requiredLength > qlr_mock_state.avatar_rgba_length || (size_t)length < requiredLength ) {
		return 0;
	}

	memcpy( buffer, qlr_mock_state.avatar_rgba, requiredLength );
	return 1;
}

/*
=============
QLR_SteamMatchmaking_CreateLobby
=============
*/
static uint64_t QLR_FASTCALL QLR_SteamMatchmaking_CreateLobby( void *self, void *unused, int lobbyType, int maxMembers ) {
	(void)self;
	(void)unused;

	qlr_mock_state.lobby_create_calls++;
	qlr_mock_state.lobby_create_type = lobbyType;
	qlr_mock_state.lobby_create_max_members = maxMembers;
	return qlr_mock_state.create_lobby_result;
}

/*
=============
QLR_SteamMatchmaking_AddFavoriteGame
=============
*/
static int QLR_FASTCALL QLR_SteamMatchmaking_AddFavoriteGame( void *self, void *unused, uint32_t appId, uint32_t serverIp, uint16_t connPort, uint16_t queryPort, uint32_t flags, uint32_t lastPlayedOnServer ) {
	(void)self;
	(void)unused;

	qlr_mock_state.favorite_add_calls++;
	qlr_mock_state.favorite_last_app_id = appId;
	qlr_mock_state.favorite_last_ip = serverIp;
	qlr_mock_state.favorite_last_conn_port = connPort;
	qlr_mock_state.favorite_last_query_port = queryPort;
	qlr_mock_state.favorite_last_flags = flags;
	qlr_mock_state.favorite_last_played = lastPlayedOnServer;
	return qlr_mock_state.favorite_add_result;
}

/*
=============
QLR_SteamMatchmaking_RemoveFavoriteGame
=============
*/
static qboolean QLR_FASTCALL QLR_SteamMatchmaking_RemoveFavoriteGame( void *self, void *unused, uint32_t appId, uint32_t serverIp, uint16_t connPort, uint16_t queryPort, uint32_t flags ) {
	(void)self;
	(void)unused;

	qlr_mock_state.favorite_remove_calls++;
	qlr_mock_state.favorite_last_app_id = appId;
	qlr_mock_state.favorite_last_ip = serverIp;
	qlr_mock_state.favorite_last_conn_port = connPort;
	qlr_mock_state.favorite_last_query_port = queryPort;
	qlr_mock_state.favorite_last_flags = flags;
	qlr_mock_state.favorite_last_played = 0u;
	return qlr_mock_state.favorite_remove_result ? qtrue : qfalse;
}

/*
=============
QLR_SteamMatchmaking_LeaveLobby
=============
*/
static void QLR_FASTCALL QLR_SteamMatchmaking_LeaveLobby( void *self, void *unused, uint32_t idLow, uint32_t idHigh ) {
	(void)self;
	(void)unused;

	qlr_mock_state.lobby_leave_calls++;
	qlr_mock_state.lobby_leave_id = ( (uint64_t)idHigh << 32 ) | idLow;
}

/*
=============
QLR_SteamMatchmaking_JoinLobby
=============
*/
static uint64_t QLR_FASTCALL QLR_SteamMatchmaking_JoinLobby( void *self, void *unused, uint32_t idLow, uint32_t idHigh ) {
	(void)self;
	(void)unused;

	qlr_mock_state.lobby_join_calls++;
	qlr_mock_state.lobby_join_id = ( (uint64_t)idHigh << 32 ) | idLow;
	return qlr_mock_state.join_lobby_result;
}

/*
=============
QLR_SteamMatchmaking_InviteUserToLobby
=============
*/
static int QLR_FASTCALL QLR_SteamMatchmaking_InviteUserToLobby( void *self, void *unused, uint32_t lobbyIdLow, uint32_t lobbyIdHigh, uint32_t userIdLow, uint32_t userIdHigh ) {
	(void)self;
	(void)unused;

	qlr_mock_state.lobby_user_invite_calls++;
	qlr_mock_state.lobby_user_invite_lobby_id = ( (uint64_t)lobbyIdHigh << 32 ) | lobbyIdLow;
	qlr_mock_state.lobby_user_invite_target_id = ( (uint64_t)userIdHigh << 32 ) | userIdLow;
	return 1;
}

/*
=============
QLR_SteamMatchmaking_GetLobbyOwner
=============
*/
static CSteamID *QLR_FASTCALL QLR_SteamMatchmaking_GetLobbyOwner( void *self, void *unused, CSteamID *outSteamId, uint32_t idLow, uint32_t idHigh ) {
	(void)self;
	(void)unused;
	(void)idLow;
	(void)idHigh;

	if ( outSteamId ) {
		outSteamId->value = qlr_mock_state.lobby_owner_id;
	}

	return outSteamId;
}

/*
=============
QLR_SteamMatchmaking_SetLobbyGameServer
=============
*/
static void QLR_FASTCALL QLR_SteamMatchmaking_SetLobbyGameServer( void *self, void *unused, uint32_t idLow, uint32_t idHigh, uint32_t serverIp, uint16_t serverPort, uint32_t serverIdLow, uint32_t serverIdHigh ) {
	(void)self;
	(void)unused;

	qlr_mock_state.lobby_set_server_calls++;
	qlr_mock_state.lobby_set_server_id = ( (uint64_t)idHigh << 32 ) | idLow;
	qlr_mock_state.lobby_set_server_ip = serverIp;
	qlr_mock_state.lobby_set_server_port = serverPort;
	qlr_mock_state.lobby_set_server_game_server_id = ( (uint64_t)serverIdHigh << 32 ) | serverIdLow;
}

/*
=============
QLR_SteamMatchmaking_SendLobbyChatMsg
=============
*/
static int QLR_FASTCALL QLR_SteamMatchmaking_SendLobbyChatMsg( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *message, int messageLength ) {
	(void)self;
	(void)unused;
	(void)messageLength;

	qlr_mock_state.lobby_say_calls++;
	qlr_mock_state.lobby_say_id = ( (uint64_t)idHigh << 32 ) | idLow;
	Q_strncpyz( qlr_mock_state.lobby_say_message, message ? message : "", sizeof( qlr_mock_state.lobby_say_message ) );
	return qlr_mock_state.say_lobby_result;
}

/*
=============
QLR_SteamMatchmaking_GetLobbyChatEntry
=============
*/
static int QLR_FASTCALL QLR_SteamMatchmaking_GetLobbyChatEntry( void *self, void *unused, uint32_t idLow, uint32_t idHigh, int chatId, CSteamID *outChatter, void *buffer, int bufferSize, int *outEntryType ) {
	size_t length;

	(void)self;
	(void)unused;
	(void)idLow;
	(void)idHigh;
	(void)chatId;

	if ( outChatter ) {
		outChatter->value = qlr_mock_state.steam_id_value;
	}
	if ( outEntryType ) {
		*outEntryType = 1;
	}
	if ( !buffer || bufferSize <= 0 ) {
		return 0;
	}

	Q_strncpyz( (char *)buffer, qlr_mock_state.lobby_chat_entry_message, bufferSize );
	length = strlen( (const char *)buffer ) + 1;
	return (int)length;
}

/*
=============
QLR_SteamMatchmakingServers_CaptureListRequest
=============
*/
static void QLR_SteamMatchmakingServers_CaptureListRequest( uint32_t appId, qlr_matchmaking_key_value_pair_t **filters, uint32_t filterCount, void *responseObject ) {
	qlr_mock_state.server_browser_last_app_id = appId;
	qlr_mock_state.server_browser_last_filter_count = filterCount;
	qlr_mock_state.server_browser_last_response = (uintptr_t)responseObject;
	qlr_mock_state.server_browser_last_filter_key[0] = '\0';
	qlr_mock_state.server_browser_last_filter_value[0] = '\0';

	if ( filters && filterCount > 0u && filters[0] ) {
		Q_strncpyz( qlr_mock_state.server_browser_last_filter_key, filters[0]->key, sizeof( qlr_mock_state.server_browser_last_filter_key ) );
		Q_strncpyz( qlr_mock_state.server_browser_last_filter_value, filters[0]->value, sizeof( qlr_mock_state.server_browser_last_filter_value ) );
	}
}

/*
=============
QLR_SteamMatchmakingServers_RequestInternetServerList
=============
*/
static void *QLR_FASTCALL QLR_SteamMatchmakingServers_RequestInternetServerList( void *self, void *unused, uint32_t appId, qlr_matchmaking_key_value_pair_t **filters, uint32_t filterCount, void *responseObject ) {
	(void)self;
	(void)unused;

	qlr_mock_state.server_browser_internet_calls++;
	QLR_SteamMatchmakingServers_CaptureListRequest( appId, filters, filterCount, responseObject );
	return (void *)qlr_mock_state.server_browser_request_result;
}

/*
=============
QLR_SteamMatchmakingServers_RequestLANServerList
=============
*/
static void *QLR_FASTCALL QLR_SteamMatchmakingServers_RequestLANServerList( void *self, void *unused, uint32_t appId, void *responseObject ) {
	(void)self;
	(void)unused;

	qlr_mock_state.server_browser_lan_calls++;
	QLR_SteamMatchmakingServers_CaptureListRequest( appId, NULL, 0u, responseObject );
	return (void *)qlr_mock_state.server_browser_request_result;
}

/*
=============
QLR_SteamMatchmakingServers_RequestFriendsServerList
=============
*/
static void *QLR_FASTCALL QLR_SteamMatchmakingServers_RequestFriendsServerList( void *self, void *unused, uint32_t appId, qlr_matchmaking_key_value_pair_t **filters, uint32_t filterCount, void *responseObject ) {
	(void)self;
	(void)unused;

	qlr_mock_state.server_browser_friends_calls++;
	QLR_SteamMatchmakingServers_CaptureListRequest( appId, filters, filterCount, responseObject );
	return (void *)qlr_mock_state.server_browser_request_result;
}

/*
=============
QLR_SteamMatchmakingServers_RequestFavoritesServerList
=============
*/
static void *QLR_FASTCALL QLR_SteamMatchmakingServers_RequestFavoritesServerList( void *self, void *unused, uint32_t appId, qlr_matchmaking_key_value_pair_t **filters, uint32_t filterCount, void *responseObject ) {
	(void)self;
	(void)unused;

	qlr_mock_state.server_browser_favorites_calls++;
	QLR_SteamMatchmakingServers_CaptureListRequest( appId, filters, filterCount, responseObject );
	return (void *)qlr_mock_state.server_browser_request_result;
}

/*
=============
QLR_SteamMatchmakingServers_RequestHistoryServerList
=============
*/
static void *QLR_FASTCALL QLR_SteamMatchmakingServers_RequestHistoryServerList( void *self, void *unused, uint32_t appId, qlr_matchmaking_key_value_pair_t **filters, uint32_t filterCount, void *responseObject ) {
	(void)self;
	(void)unused;

	qlr_mock_state.server_browser_history_calls++;
	QLR_SteamMatchmakingServers_CaptureListRequest( appId, filters, filterCount, responseObject );
	return (void *)qlr_mock_state.server_browser_request_result;
}

/*
=============
QLR_SteamMatchmakingServers_ReleaseRequest
=============
*/
static void QLR_FASTCALL QLR_SteamMatchmakingServers_ReleaseRequest( void *self, void *unused, void *request ) {
	(void)self;
	(void)unused;

	qlr_mock_state.server_browser_release_calls++;
	qlr_mock_state.server_browser_last_request = (uintptr_t)request;
}

/*
=============
QLR_SteamMatchmakingServers_GetServerDetails
=============
*/
static const void *QLR_FASTCALL QLR_SteamMatchmakingServers_GetServerDetails( void *self, void *unused, void *request, int index ) {
	(void)self;
	(void)unused;

	qlr_mock_state.server_browser_get_details_calls++;
	qlr_mock_state.server_browser_last_request = (uintptr_t)request;
	qlr_mock_state.server_browser_last_index = index;
	if ( qlr_mock_state.server_browser_details_result != 0 ) {
		return (const void *)qlr_mock_state.server_browser_details_result;
	}
	return &qlr_mock_state.server_browser_details;
}

/*
=============
QLR_SteamMatchmakingServers_RefreshQuery
=============
*/
static void QLR_FASTCALL QLR_SteamMatchmakingServers_RefreshQuery( void *self, void *unused, void *request ) {
	(void)self;
	(void)unused;

	qlr_mock_state.server_browser_refresh_calls++;
	qlr_mock_state.server_browser_last_request = (uintptr_t)request;
}

/*
=============
QLR_SteamMatchmakingServers_PingServer
=============
*/
static int QLR_FASTCALL QLR_SteamMatchmakingServers_PingServer( void *self, void *unused, uint32_t serverIp, uint16_t serverPort, void *responseObject ) {
	(void)self;
	(void)unused;

	qlr_mock_state.server_browser_ping_calls++;
	qlr_mock_state.server_browser_ping_order = ++qlr_mock_state.server_browser_detail_order;
	qlr_mock_state.server_browser_last_ip = serverIp;
	qlr_mock_state.server_browser_last_port = serverPort;
	qlr_mock_state.server_browser_last_ping_response = (uintptr_t)responseObject;
	return qlr_mock_state.server_browser_ping_query_result;
}

/*
=============
QLR_SteamMatchmakingServers_PlayerDetails
=============
*/
static int QLR_FASTCALL QLR_SteamMatchmakingServers_PlayerDetails( void *self, void *unused, uint32_t serverIp, uint16_t serverPort, void *responseObject ) {
	(void)self;
	(void)unused;

	qlr_mock_state.server_browser_players_calls++;
	qlr_mock_state.server_browser_players_order = ++qlr_mock_state.server_browser_detail_order;
	qlr_mock_state.server_browser_last_ip = serverIp;
	qlr_mock_state.server_browser_last_port = serverPort;
	qlr_mock_state.server_browser_last_players_response = (uintptr_t)responseObject;
	return qlr_mock_state.server_browser_players_query_result;
}

/*
=============
QLR_SteamMatchmakingServers_ServerRules
=============
*/
static int QLR_FASTCALL QLR_SteamMatchmakingServers_ServerRules( void *self, void *unused, uint32_t serverIp, uint16_t serverPort, void *responseObject ) {
	(void)self;
	(void)unused;

	qlr_mock_state.server_browser_rules_calls++;
	qlr_mock_state.server_browser_rules_order = ++qlr_mock_state.server_browser_detail_order;
	qlr_mock_state.server_browser_last_ip = serverIp;
	qlr_mock_state.server_browser_last_port = serverPort;
	qlr_mock_state.server_browser_last_rules_response = (uintptr_t)responseObject;
	return qlr_mock_state.server_browser_rules_query_result;
}

/*
=============
QLR_SteamMatchmakingServers_CancelServerQuery
=============
*/
static void QLR_FASTCALL QLR_SteamMatchmakingServers_CancelServerQuery( void *self, void *unused, int query ) {
	(void)self;
	(void)unused;

	qlr_mock_state.server_browser_cancel_query_calls++;
	qlr_mock_state.server_browser_last_cancel_query = query;
}

/*
=============
QLR_SteamUserStats_RequestUserStats
=============
*/
static uint64_t QLR_FASTCALL QLR_SteamUserStats_RequestUserStats( void *self, void *unused, uint32_t idLow, uint32_t idHigh ) {
	(void)self;
	(void)unused;

	qlr_mock_state.user_stats_request_calls++;
	qlr_mock_state.user_stats_request_id = ( (uint64_t)idHigh << 32 ) | idLow;
	return qlr_mock_state.request_user_stats_result;
}

/*
=============
QLR_SteamUserStats_ResetAllStats
=============
*/
static int QLR_FASTCALL QLR_SteamUserStats_ResetAllStats( void *self, void *unused, int achievementsToo ) {
	(void)self;
	(void)unused;

	qlr_mock_state.user_stats_reset_calls++;
	qlr_mock_state.user_stats_last_reset_achievements = achievementsToo;
	return qlr_mock_state.reset_user_stats_result;
}

/*
=============
QLR_SteamworksMock_CombineIdentityWords
=============
*/
static uint64_t QLR_SteamworksMock_CombineIdentityWords( uint32_t idLow, uint32_t idHigh ) {
	return ( (uint64_t)idHigh << 32 ) | idLow;
}

/*
=============
QLR_SteamUserStats_CaptureReadback
=============
*/
static void QLR_SteamUserStats_CaptureReadback( uint32_t idLow, uint32_t idHigh, const char *name ) {
	qlr_mock_state.user_stats_last_read_id = QLR_SteamworksMock_CombineIdentityWords( idLow, idHigh );
	Q_strncpyz( qlr_mock_state.user_stats_last_name, name ? name : "", sizeof( qlr_mock_state.user_stats_last_name ) );
}

/*
=============
QLR_SteamUserStats_GetUserStatFloat
=============
*/
static qboolean QLR_FASTCALL QLR_SteamUserStats_GetUserStatFloat( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, float *outValue ) {
	(void)self;
	(void)unused;

	qlr_mock_state.user_stats_get_float_calls++;
	QLR_SteamUserStats_CaptureReadback( idLow, idHigh, name );

	if ( outValue ) {
		*outValue = 0.0f;
	}

	if ( !outValue || !qlr_mock_state.user_stats_get_float_result ) {
		return qfalse;
	}

	*outValue = qlr_mock_state.user_stats_float_value;
	return qtrue;
}

/*
=============
QLR_SteamUserStats_GetUserStatInt
=============
*/
static qboolean QLR_FASTCALL QLR_SteamUserStats_GetUserStatInt( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, int *outValue ) {
	(void)self;
	(void)unused;

	qlr_mock_state.user_stats_get_int_calls++;
	QLR_SteamUserStats_CaptureReadback( idLow, idHigh, name );

	if ( outValue ) {
		*outValue = 0;
	}

	if ( !outValue || !qlr_mock_state.user_stats_get_int_result ) {
		return qfalse;
	}

	*outValue = qlr_mock_state.user_stats_int_value;
	return qtrue;
}

/*
=============
QLR_SteamUserStats_GetUserAchievement
=============
*/
static qboolean QLR_FASTCALL QLR_SteamUserStats_GetUserAchievement( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, qboolean *outAchieved, int *outUnlockTime ) {
	(void)self;
	(void)unused;

	qlr_mock_state.user_stats_get_achievement_calls++;
	QLR_SteamUserStats_CaptureReadback( idLow, idHigh, name );

	if ( outAchieved ) {
		*outAchieved = qfalse;
	}
	if ( outUnlockTime ) {
		*outUnlockTime = 0;
	}

	if ( !outAchieved || !qlr_mock_state.user_stats_get_achievement_result ) {
		return qfalse;
	}

	*outAchieved = qlr_mock_state.user_stats_achievement_value ? qtrue : qfalse;
	if ( outUnlockTime ) {
		*outUnlockTime = qlr_mock_state.user_stats_unlock_time;
	}
	return qtrue;
}

/*
=============
QLR_SteamUserStats_GetAchievementDisplayAttribute
=============
*/
static const char *QLR_FASTCALL QLR_SteamUserStats_GetAchievementDisplayAttribute( void *self, void *unused, const char *name, const char *key ) {
	(void)self;
	(void)unused;

	qlr_mock_state.user_stats_get_display_attribute_calls++;
	Q_strncpyz( qlr_mock_state.user_stats_last_name, name ? name : "", sizeof( qlr_mock_state.user_stats_last_name ) );
	Q_strncpyz( qlr_mock_state.user_stats_last_attribute_key, key ? key : "", sizeof( qlr_mock_state.user_stats_last_attribute_key ) );

	if ( !qlr_mock_state.user_stats_get_display_attribute_result ) {
		return NULL;
	}

	return qlr_mock_state.user_stats_display_attribute_value;
}

/*
=============
QLR_SteamworksMock_CombineItemWords
=============
*/
static uint64_t QLR_SteamworksMock_CombineItemWords( uint32_t idLow, uint32_t idHigh ) {
	return QLR_SteamworksMock_CombineIdentityWords( idLow, idHigh );
}

/*
=============
QLR_SteamGameServerStats_CaptureUserStat
=============
*/
static void QLR_SteamGameServerStats_CaptureUserStat( uint32_t idLow, uint32_t idHigh, const char *name ) {
	qlr_mock_state.steam_game_server_stats_last_user_id = QLR_SteamworksMock_CombineIdentityWords( idLow, idHigh );
	Q_strncpyz( qlr_mock_state.steam_game_server_stats_last_name, name ? name : "", sizeof( qlr_mock_state.steam_game_server_stats_last_name ) );
}

/*
=============
QLR_SteamGameServerStats_RequestUserStats
=============
*/
static uint64_t QLR_FASTCALL QLR_SteamGameServerStats_RequestUserStats( void *self, void *unused, uint32_t idLow, uint32_t idHigh ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_stats_request_calls++;
	QLR_SteamGameServerStats_CaptureUserStat( idLow, idHigh, "" );
	return qlr_mock_state.steam_game_server_stats_result ? 1ull : 0ull;
}

/*
=============
QLR_SteamGameServerStats_GetUserStatFloat
=============
*/
static qboolean QLR_FASTCALL QLR_SteamGameServerStats_GetUserStatFloat( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, float *outValue ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_stats_get_float_calls++;
	QLR_SteamGameServerStats_CaptureUserStat( idLow, idHigh, name );

	if ( outValue ) {
		*outValue = 0.0f;
	}

	if ( !outValue || !qlr_mock_state.steam_game_server_stats_result ) {
		return qfalse;
	}

	*outValue = qlr_mock_state.steam_game_server_stats_float_value;
	return qtrue;
}

/*
=============
QLR_SteamGameServerStats_GetUserStatInt
=============
*/
static qboolean QLR_FASTCALL QLR_SteamGameServerStats_GetUserStatInt( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, int *outValue ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_stats_get_int_calls++;
	QLR_SteamGameServerStats_CaptureUserStat( idLow, idHigh, name );

	if ( outValue ) {
		*outValue = 0;
	}

	if ( !outValue || !qlr_mock_state.steam_game_server_stats_result ) {
		return qfalse;
	}

	*outValue = qlr_mock_state.steam_game_server_stats_int_value;
	return qtrue;
}

/*
=============
QLR_SteamGameServerStats_GetUserAchievement
=============
*/
static qboolean QLR_FASTCALL QLR_SteamGameServerStats_GetUserAchievement( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, qboolean *outAchieved ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_stats_get_achievement_calls++;
	QLR_SteamGameServerStats_CaptureUserStat( idLow, idHigh, name );

	if ( outAchieved ) {
		*outAchieved = qfalse;
	}

	if ( !outAchieved || !qlr_mock_state.steam_game_server_stats_result ) {
		return qfalse;
	}

	*outAchieved = qlr_mock_state.steam_game_server_stats_achievement_value ? qtrue : qfalse;
	return qtrue;
}

/*
=============
QLR_SteamGameServerStats_SetUserStatFloat
=============
*/
static qboolean QLR_FASTCALL QLR_SteamGameServerStats_SetUserStatFloat( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, float value ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_stats_set_float_calls++;
	qlr_mock_state.steam_game_server_stats_last_float_value = value;
	QLR_SteamGameServerStats_CaptureUserStat( idLow, idHigh, name );
	return qlr_mock_state.steam_game_server_stats_result ? qtrue : qfalse;
}

/*
=============
QLR_SteamGameServerStats_SetUserStatInt
=============
*/
static qboolean QLR_FASTCALL QLR_SteamGameServerStats_SetUserStatInt( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, int value ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_stats_set_int_calls++;
	qlr_mock_state.steam_game_server_stats_last_int_value = value;
	QLR_SteamGameServerStats_CaptureUserStat( idLow, idHigh, name );
	return qlr_mock_state.steam_game_server_stats_result ? qtrue : qfalse;
}

/*
=============
QLR_SteamGameServerStats_UpdateAvgRateStat
=============
*/
static qboolean QLR_FASTCALL QLR_SteamGameServerStats_UpdateAvgRateStat( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name, float countThisSession, double sessionLength ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_stats_update_avg_rate_calls++;
	qlr_mock_state.steam_game_server_stats_last_avg_count = countThisSession;
	qlr_mock_state.steam_game_server_stats_last_avg_session_length = sessionLength;
	QLR_SteamGameServerStats_CaptureUserStat( idLow, idHigh, name );
	return qlr_mock_state.steam_game_server_stats_result ? qtrue : qfalse;
}

/*
=============
QLR_SteamGameServerStats_SetUserAchievement
=============
*/
static qboolean QLR_FASTCALL QLR_SteamGameServerStats_SetUserAchievement( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *name ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_stats_set_achievement_calls++;
	QLR_SteamGameServerStats_CaptureUserStat( idLow, idHigh, name );
	return qlr_mock_state.steam_game_server_stats_result ? qtrue : qfalse;
}

/*
=============
QLR_SteamGameServerStats_StoreUserStats
=============
*/
static qboolean QLR_FASTCALL QLR_SteamGameServerStats_StoreUserStats( void *self, void *unused, uint32_t idLow, uint32_t idHigh ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_stats_store_calls++;
	QLR_SteamGameServerStats_CaptureUserStat( idLow, idHigh, "" );
	return qlr_mock_state.steam_game_server_stats_result ? qtrue : qfalse;
}

/*
=============
QLR_SteamUGC_CreateQueryAllUGCRequest
=============
*/
static uint64_t QLR_FASTCALL QLR_SteamUGC_CreateQueryAllUGCRequest( void *self, void *unused, int queryType, int matchingType, uint32_t creatorAppId, uint32_t consumerAppId, uint32_t filter ) {
	(void)self;
	(void)unused;

	qlr_mock_state.ugc_create_query_calls++;
	qlr_mock_state.ugc_last_query_type = queryType;
	qlr_mock_state.ugc_last_matching_type = matchingType;
	qlr_mock_state.ugc_last_creator_app_id = creatorAppId;
	qlr_mock_state.ugc_last_consumer_app_id = consumerAppId;
	qlr_mock_state.ugc_last_filter = filter;
	qlr_mock_state.ugc_last_query_handle = qlr_mock_state.ugc_query_handle_result;
	return qlr_mock_state.ugc_query_handle_result;
}

/*
=============
QLR_SteamUGC_SendQueryUGCRequest
=============
*/
static uint64_t QLR_FASTCALL QLR_SteamUGC_SendQueryUGCRequest( void *self, void *unused, uint32_t queryLow, uint32_t queryHigh ) {
	(void)self;
	(void)unused;

	qlr_mock_state.ugc_send_query_calls++;
	qlr_mock_state.ugc_last_sent_query_handle = ( (uint64_t)queryHigh << 32 ) | queryLow;
	return qlr_mock_state.ugc_query_call_result;
}

/*
=============
QLR_SteamUGC_GetQueryUGCResult
=============
*/
static qboolean QLR_FASTCALL QLR_SteamUGC_GetQueryUGCResult( void *self, void *unused, uint32_t queryLow, uint32_t queryHigh, uint32_t index, void *details ) {
	uint64_t queryHandle;

	(void)self;
	(void)unused;

	queryHandle = ( (uint64_t)queryHigh << 32 ) | queryLow;
	qlr_mock_state.ugc_get_query_result_calls++;
	qlr_mock_state.ugc_last_result_query_handle = queryHandle;
	qlr_mock_state.ugc_last_result_index = index;

	if ( !details || !qlr_mock_state.ugc_query_result_success ) {
		return qfalse;
	}

	memcpy( (char *)details + QLR_STEAM_UGC_DETAILS_PUBLISHED_FILE_ID_OFFSET, &qlr_mock_state.ugc_result_published_file_id, QLR_STEAM_UGC_DETAILS_PUBLISHED_FILE_ID_SIZE );
	Q_strncpyz( (char *)details + QLR_STEAM_UGC_DETAILS_TITLE_OFFSET, qlr_mock_state.ugc_result_title, QLR_STEAM_UGC_DETAILS_DESCRIPTION_OFFSET - QLR_STEAM_UGC_DETAILS_TITLE_OFFSET );
	Q_strncpyz( (char *)details + QLR_STEAM_UGC_DETAILS_DESCRIPTION_OFFSET, qlr_mock_state.ugc_result_description, sizeof( qlr_mock_state.ugc_result_description ) );
	return qtrue;
}

/*
=============
QLR_SteamUGC_GetQueryUGCPreviewURL
=============
*/
static qboolean QLR_FASTCALL QLR_SteamUGC_GetQueryUGCPreviewURL( void *self, void *unused, uint32_t queryLow, uint32_t queryHigh, uint32_t index, char *buffer, uint32_t bufferSize ) {
	uint64_t queryHandle;

	(void)self;
	(void)unused;

	queryHandle = ( (uint64_t)queryHigh << 32 ) | queryLow;
	qlr_mock_state.ugc_get_query_preview_calls++;
	qlr_mock_state.ugc_last_preview_query_handle = queryHandle;
	qlr_mock_state.ugc_last_preview_index = index;

	if ( !buffer || bufferSize == 0u || !qlr_mock_state.ugc_preview_success ) {
		return qfalse;
	}

	Q_strncpyz( buffer, qlr_mock_state.ugc_preview_url, (int)bufferSize );
	return qtrue;
}

/*
=============
QLR_SteamUGC_ReleaseQueryUGCRequest
=============
*/
static qboolean QLR_FASTCALL QLR_SteamUGC_ReleaseQueryUGCRequest( void *self, void *unused, uint32_t queryLow, uint32_t queryHigh ) {
	(void)self;
	(void)unused;

	qlr_mock_state.ugc_release_query_calls++;
	qlr_mock_state.ugc_last_released_query_handle = ( (uint64_t)queryHigh << 32 ) | queryLow;
	return qtrue;
}

/*
=============
QLR_SteamUGC_SubscribeItem
=============
*/
static int QLR_FASTCALL QLR_SteamUGC_SubscribeItem( void *self, void *unused, uint32_t idLow, uint32_t idHigh ) {
	(void)self;
	(void)unused;

	qlr_mock_state.ugc_subscribe_calls++;
	qlr_mock_state.ugc_last_item_id = QLR_SteamworksMock_CombineItemWords( idLow, idHigh );
	return 1;
}

/*
=============
QLR_SteamUGC_UnsubscribeItem
=============
*/
static int QLR_FASTCALL QLR_SteamUGC_UnsubscribeItem( void *self, void *unused, uint32_t idLow, uint32_t idHigh ) {
	(void)self;
	(void)unused;

	qlr_mock_state.ugc_unsubscribe_calls++;
	qlr_mock_state.ugc_last_item_id = QLR_SteamworksMock_CombineItemWords( idLow, idHigh );
	return 1;
}

/*
=============
QLR_SteamUGC_GetNumSubscribedItems
=============
*/
static uint32_t QLR_FASTCALL QLR_SteamUGC_GetNumSubscribedItems( void *self, void *unused ) {
	(void)self;
	(void)unused;

	return qlr_mock_state.ugc_subscribed_item_count;
}

/*
=============
QLR_SteamUGC_GetSubscribedItems
=============
*/
static uint32_t QLR_FASTCALL QLR_SteamUGC_GetSubscribedItems( void *self, void *unused, uint64_t *outItemIds, uint32_t maxItems ) {
	uint32_t copyCount;

	(void)self;
	(void)unused;

	if ( !outItemIds || maxItems == 0u ) {
		return 0u;
	}

	copyCount = qlr_mock_state.ugc_subscribed_item_count;
	if ( copyCount > maxItems ) {
		copyCount = maxItems;
	}

	memcpy( outItemIds, qlr_mock_state.ugc_subscribed_items, copyCount * sizeof( qlr_mock_state.ugc_subscribed_items[0] ) );
	return copyCount;
}

/*
=============
QLR_SteamUGC_GetItemState
=============
*/
static uint32_t QLR_FASTCALL QLR_SteamUGC_GetItemState( void *self, void *unused, uint32_t idLow, uint32_t idHigh ) {
	(void)self;
	(void)unused;
	(void)idLow;
	(void)idHigh;

	return qlr_mock_state.ugc_item_state;
}

/*
=============
QLR_SteamUGC_GetItemInstallInfo
=============
*/
static int QLR_FASTCALL QLR_SteamUGC_GetItemInstallInfo( void *self, void *unused, uint32_t idLow, uint32_t idHigh, uint64_t *outSizeOnDisk, char *folder, uint32_t folderSize, uint32_t *outTimestamp ) {
	uint64_t itemId;

	(void)self;
	(void)unused;

	if ( outSizeOnDisk ) {
		*outSizeOnDisk = 0ull;
	}
	if ( folder && folderSize > 0u ) {
		folder[0] = '\0';
	}
	if ( outTimestamp ) {
		*outTimestamp = 0u;
	}

	if ( !folder || folderSize == 0u ) {
		return 0;
	}

	itemId = QLR_SteamworksMock_CombineItemWords( idLow, idHigh );
	if ( itemId != qlr_mock_state.ugc_install_item_id || !qlr_mock_state.ugc_install_folder[0] ) {
		return 0;
	}

	if ( outSizeOnDisk ) {
		*outSizeOnDisk = qlr_mock_state.ugc_install_size_on_disk;
	}
	if ( outTimestamp ) {
		*outTimestamp = qlr_mock_state.ugc_install_timestamp;
	}

	Q_strncpyz( folder, qlr_mock_state.ugc_install_folder, folderSize );
	return 1;
}

/*
=============
QLR_SteamUGC_GetItemDownloadInfo
=============
*/
static int QLR_FASTCALL QLR_SteamUGC_GetItemDownloadInfo( void *self, void *unused, uint32_t idLow, uint32_t idHigh, uint64_t *outDownloaded, uint64_t *outTotal ) {
	(void)self;
	(void)unused;
	(void)idLow;
	(void)idHigh;

	if ( outDownloaded ) {
		*outDownloaded = qlr_mock_state.ugc_downloaded;
	}
	if ( outTotal ) {
		*outTotal = qlr_mock_state.ugc_total;
	}

	return 1;
}

/*
=============
QLR_SteamUGC_DownloadItem
=============
*/
static int QLR_FASTCALL QLR_SteamUGC_DownloadItem( void *self, void *unused, uint32_t idLow, uint32_t idHigh, int highPriority ) {
	(void)self;
	(void)unused;

	qlr_mock_state.ugc_download_calls++;
	qlr_mock_state.ugc_last_item_id = QLR_SteamworksMock_CombineItemWords( idLow, idHigh );
	qlr_mock_state.ugc_last_high_priority = highPriority;
	return 1;
}

/*
=============
QLR_SteamGameServerUGC_SubscribeItem
=============
*/
static int QLR_FASTCALL QLR_SteamGameServerUGC_SubscribeItem( void *self, void *unused, uint32_t idLow, uint32_t idHigh ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_ugc_subscribe_calls++;
	qlr_mock_state.steam_game_server_ugc_last_item_id = QLR_SteamworksMock_CombineItemWords( idLow, idHigh );
	return 1;
}

/*
=============
QLR_SteamGameServerUGC_UnsubscribeItem
=============
*/
static int QLR_FASTCALL QLR_SteamGameServerUGC_UnsubscribeItem( void *self, void *unused, uint32_t idLow, uint32_t idHigh ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_ugc_unsubscribe_calls++;
	qlr_mock_state.steam_game_server_ugc_last_item_id = QLR_SteamworksMock_CombineItemWords( idLow, idHigh );
	return 1;
}

/*
=============
QLR_SteamGameServerUGC_GetItemState
=============
*/
static uint32_t QLR_FASTCALL QLR_SteamGameServerUGC_GetItemState( void *self, void *unused, uint32_t idLow, uint32_t idHigh ) {
	(void)self;
	(void)unused;
	(void)idLow;
	(void)idHigh;

	return qlr_mock_state.ugc_item_state;
}

/*
=============
QLR_SteamGameServerUGC_GetItemDownloadInfo
=============
*/
static int QLR_FASTCALL QLR_SteamGameServerUGC_GetItemDownloadInfo( void *self, void *unused, uint32_t idLow, uint32_t idHigh, uint64_t *outDownloaded, uint64_t *outTotal ) {
	(void)self;
	(void)unused;
	(void)idLow;
	(void)idHigh;

	if ( outDownloaded ) {
		*outDownloaded = qlr_mock_state.ugc_downloaded;
	}
	if ( outTotal ) {
		*outTotal = qlr_mock_state.ugc_total;
	}

	return 1;
}

/*
=============
QLR_SteamGameServerUGC_DownloadItem
=============
*/
static int QLR_FASTCALL QLR_SteamGameServerUGC_DownloadItem( void *self, void *unused, uint32_t idLow, uint32_t idHigh, int highPriority ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_game_server_ugc_download_calls++;
	qlr_mock_state.steam_game_server_ugc_last_item_id = QLR_SteamworksMock_CombineItemWords( idLow, idHigh );
	qlr_mock_state.steam_game_server_ugc_last_high_priority = highPriority;
	return 1;
}

/*
=============
QLR_SteamAPI_SteamFriends
=============
*/
void *QLR_SteamAPI_SteamFriends( void ) {
	static void *vtable[QLR_STEAM_FRIENDS_VTABLE_SLOT_COUNT];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[QLR_STEAM_FRIENDS_GET_PERSONA_NAME_SLOT] = QLR_SteamFriends_GetPersonaName;
	vtable[QLR_STEAM_FRIENDS_GET_FRIEND_COUNT_SLOT] = QLR_SteamFriends_GetFriendCount;
	vtable[QLR_STEAM_FRIENDS_GET_FRIEND_BY_INDEX_SLOT] = QLR_SteamFriends_GetFriendByIndex;
	vtable[QLR_STEAM_FRIENDS_GET_FRIEND_RELATIONSHIP_SLOT] = QLR_SteamFriends_GetFriendRelationship;
	vtable[QLR_STEAM_FRIENDS_GET_FRIEND_PERSONA_STATE_SLOT] = QLR_SteamFriends_GetFriendPersonaState;
	vtable[QLR_STEAM_FRIENDS_GET_FRIEND_PERSONA_NAME_SLOT] = QLR_SteamFriends_GetFriendPersonaName;
	vtable[QLR_STEAM_FRIENDS_GET_FRIEND_GAME_PLAYED_SLOT] = QLR_SteamFriends_GetFriendGamePlayed;
	vtable[QLR_STEAM_FRIENDS_GET_PLAYER_NICKNAME_SLOT] = QLR_SteamFriends_GetPlayerNickname;
	vtable[QLR_STEAM_FRIENDS_SET_IN_GAME_VOICE_SPEAKING_SLOT] = QLR_SteamFriends_SetInGameVoiceSpeaking;
	vtable[QLR_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_TO_USER_SLOT] = QLR_SteamFriends_ActivateGameOverlayToUser;
	vtable[QLR_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_TO_WEB_PAGE_SLOT] = QLR_SteamFriends_ActivateGameOverlayToWebPage;
	vtable[QLR_STEAM_FRIENDS_ACTIVATE_GAME_OVERLAY_INVITE_DIALOG_SLOT] = QLR_SteamFriends_ActivateGameOverlayInviteDialog;
	vtable[QLR_STEAM_FRIENDS_GET_SMALL_FRIEND_AVATAR_SLOT] = QLR_SteamFriends_GetSmallFriendAvatar;
	vtable[QLR_STEAM_FRIENDS_GET_MEDIUM_FRIEND_AVATAR_SLOT] = QLR_SteamFriends_GetMediumFriendAvatar;
	vtable[QLR_STEAM_FRIENDS_GET_LARGE_FRIEND_AVATAR_SLOT] = QLR_SteamFriends_GetLargeFriendAvatar;
	vtable[QLR_STEAM_FRIENDS_SET_RICH_PRESENCE_SLOT] = QLR_SteamFriends_SetRichPresence;
	vtable[QLR_STEAM_FRIENDS_GET_FRIEND_RICH_PRESENCE_SLOT] = QLR_SteamFriends_GetFriendRichPresence;
	vtable[QLR_STEAM_FRIENDS_INVITE_USER_TO_GAME_SLOT] = QLR_SteamFriends_InviteUserToGame;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamUtils
=============
*/
void *QLR_SteamAPI_SteamUtils( void ) {
	static void *vtable[QLR_STEAM_UTILS_VTABLE_SLOT_COUNT];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[QLR_STEAM_UTILS_GET_IP_COUNTRY_SLOT] = QLR_SteamUtils_GetIPCountry;
	vtable[QLR_STEAM_UTILS_GET_IMAGE_SIZE_SLOT] = QLR_SteamUtils_GetImageSize;
	vtable[QLR_STEAM_UTILS_GET_IMAGE_RGBA_SLOT] = QLR_SteamUtils_GetImageRGBA;
	vtable[QLR_STEAM_UTILS_GET_APP_ID_SLOT] = QLR_SteamUtils_GetAppID;
	return &iface;
}

/*
=============
QLR_SteamApps_BIsSubscribedApp
=============
*/
static int QLR_FASTCALL QLR_SteamApps_BIsSubscribedApp( void *self, void *unused, uint32_t appId ) {
	(void)self;
	(void)unused;

	qlr_mock_state.steam_apps_last_app_id = appId;
	return qlr_mock_state.steam_apps_subscribed_result;
}

/*
=============
QLR_SteamAPI_SteamApps
=============
*/
void *QLR_SteamAPI_SteamApps( void ) {
	static void *vtable[QLR_STEAM_APPS_VTABLE_SLOT_COUNT];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	++qlr_mock_state.steam_apps_interface_calls;
	vtable[QLR_STEAM_APPS_BIS_SUBSCRIBED_APP_SLOT] = QLR_SteamApps_BIsSubscribedApp;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamUserStats
=============
*/
void *QLR_SteamAPI_SteamUserStats( void ) {
	static void *vtable[QLR_STEAM_USERSTATS_VTABLE_SLOT_COUNT];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[QLR_STEAM_USERSTATS_GET_ACHIEVEMENT_DISPLAY_ATTRIBUTE_SLOT] = QLR_SteamUserStats_GetAchievementDisplayAttribute;
	vtable[QLR_STEAM_USERSTATS_REQUEST_USER_STATS_SLOT] = QLR_SteamUserStats_RequestUserStats;
	vtable[QLR_STEAM_USERSTATS_GET_USER_STAT_FLOAT_SLOT] = QLR_SteamUserStats_GetUserStatFloat;
	vtable[QLR_STEAM_USERSTATS_GET_USER_STAT_INT_SLOT] = QLR_SteamUserStats_GetUserStatInt;
	vtable[QLR_STEAM_USERSTATS_GET_USER_ACHIEVEMENT_SLOT] = QLR_SteamUserStats_GetUserAchievement;
	vtable[QLR_STEAM_USERSTATS_RESET_ALL_STATS_SLOT] = QLR_SteamUserStats_ResetAllStats;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamNetworking
=============
*/
void *QLR_SteamAPI_SteamNetworking( void ) {
	static void *vtable[QLR_STEAM_NETWORKING_VTABLE_SLOT_COUNT];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[QLR_STEAM_NETWORKING_SEND_P2P_PACKET_SLOT] = QLR_SteamNetworking_SendP2PPacket;
	vtable[QLR_STEAM_NETWORKING_IS_P2P_PACKET_AVAILABLE_SLOT] = QLR_SteamNetworking_IsP2PPacketAvailable;
	vtable[QLR_STEAM_NETWORKING_READ_P2P_PACKET_SLOT] = QLR_SteamNetworking_ReadP2PPacket;
	vtable[QLR_STEAM_NETWORKING_ACCEPT_P2P_SESSION_SLOT] = QLR_SteamNetworking_AcceptP2PSessionWithUser;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamMatchmaking
=============
*/
void *QLR_SteamAPI_SteamMatchmaking( void ) {
	static void *vtable[QLR_STEAM_MATCHMAKING_VTABLE_SLOT_COUNT];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[QLR_STEAM_MATCHMAKING_ADD_FAVORITE_GAME_SLOT] = QLR_SteamMatchmaking_AddFavoriteGame;
	vtable[QLR_STEAM_MATCHMAKING_REMOVE_FAVORITE_GAME_SLOT] = QLR_SteamMatchmaking_RemoveFavoriteGame;
	vtable[QLR_STEAM_MATCHMAKING_CREATE_LOBBY_SLOT] = QLR_SteamMatchmaking_CreateLobby;
	vtable[QLR_STEAM_MATCHMAKING_LEAVE_LOBBY_SLOT] = QLR_SteamMatchmaking_LeaveLobby;
	vtable[QLR_STEAM_MATCHMAKING_JOIN_LOBBY_SLOT] = QLR_SteamMatchmaking_JoinLobby;
	vtable[QLR_STEAM_MATCHMAKING_INVITE_USER_TO_LOBBY_SLOT] = QLR_SteamMatchmaking_InviteUserToLobby;
	vtable[QLR_STEAM_MATCHMAKING_SEND_LOBBY_CHAT_MSG_SLOT] = QLR_SteamMatchmaking_SendLobbyChatMsg;
	vtable[QLR_STEAM_MATCHMAKING_GET_LOBBY_CHAT_ENTRY_SLOT] = QLR_SteamMatchmaking_GetLobbyChatEntry;
	vtable[QLR_STEAM_MATCHMAKING_SET_LOBBY_GAME_SERVER_SLOT] = QLR_SteamMatchmaking_SetLobbyGameServer;
	vtable[QLR_STEAM_MATCHMAKING_GET_LOBBY_OWNER_SLOT] = QLR_SteamMatchmaking_GetLobbyOwner;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamMatchmakingServers
=============
*/
void *QLR_SteamAPI_SteamMatchmakingServers( void ) {
	static void *vtable[QLR_STEAM_MATCHMAKING_SERVERS_VTABLE_SLOT_COUNT];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_INTERNET_SERVER_LIST_SLOT] = QLR_SteamMatchmakingServers_RequestInternetServerList;
	vtable[QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_LAN_SERVER_LIST_SLOT] = QLR_SteamMatchmakingServers_RequestLANServerList;
	vtable[QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_FRIENDS_SERVER_LIST_SLOT] = QLR_SteamMatchmakingServers_RequestFriendsServerList;
	vtable[QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_FAVORITES_SERVER_LIST_SLOT] = QLR_SteamMatchmakingServers_RequestFavoritesServerList;
	vtable[QLR_STEAM_MATCHMAKING_SERVERS_REQUEST_HISTORY_SERVER_LIST_SLOT] = QLR_SteamMatchmakingServers_RequestHistoryServerList;
	vtable[QLR_STEAM_MATCHMAKING_SERVERS_RELEASE_REQUEST_SLOT] = QLR_SteamMatchmakingServers_ReleaseRequest;
	vtable[QLR_STEAM_MATCHMAKING_SERVERS_GET_SERVER_DETAILS_SLOT] = QLR_SteamMatchmakingServers_GetServerDetails;
	vtable[QLR_STEAM_MATCHMAKING_SERVERS_REFRESH_QUERY_SLOT] = QLR_SteamMatchmakingServers_RefreshQuery;
	vtable[QLR_STEAM_MATCHMAKING_SERVERS_PING_SERVER_SLOT] = QLR_SteamMatchmakingServers_PingServer;
	vtable[QLR_STEAM_MATCHMAKING_SERVERS_PLAYER_DETAILS_SLOT] = QLR_SteamMatchmakingServers_PlayerDetails;
	vtable[QLR_STEAM_MATCHMAKING_SERVERS_SERVER_RULES_SLOT] = QLR_SteamMatchmakingServers_ServerRules;
	vtable[QLR_STEAM_MATCHMAKING_SERVERS_CANCEL_SERVER_QUERY_SLOT] = QLR_SteamMatchmakingServers_CancelServerQuery;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamGameServer
=============
*/
void *QLR_SteamAPI_SteamGameServer( void ) {
	static void *vtable[QLR_STEAM_GAMESERVER_VTABLE_SLOT_COUNT];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[QLR_STEAM_GAMESERVER_SET_PRODUCT_SLOT] = QLR_SteamGameServer_SetProduct;
	vtable[QLR_STEAM_GAMESERVER_SET_GAME_DESCRIPTION_SLOT] = QLR_SteamGameServer_SetGameDescription;
	vtable[QLR_STEAM_GAMESERVER_SET_GAME_DIR_SLOT] = QLR_SteamGameServer_SetGameDir;
	vtable[QLR_STEAM_GAMESERVER_SET_DEDICATED_SLOT] = QLR_SteamGameServer_SetDedicated;
	vtable[QLR_STEAM_GAMESERVER_LOG_ON_SLOT] = QLR_SteamGameServer_LogOn;
	vtable[QLR_STEAM_GAMESERVER_LOG_ON_ANONYMOUS_SLOT] = QLR_SteamGameServer_LogOnAnonymous;
	vtable[QLR_STEAM_GAMESERVER_BLOGGED_ON_SLOT] = QLR_SteamGameServer_BLoggedOn;
	vtable[QLR_STEAM_GAMESERVER_GET_STEAM_ID_SLOT] = QLR_SteamGameServer_GetSteamID;
	vtable[QLR_STEAM_GAMESERVER_SET_MAX_PLAYER_COUNT_SLOT] = QLR_SteamGameServer_SetMaxPlayerCount;
	vtable[QLR_STEAM_GAMESERVER_SET_BOT_PLAYER_COUNT_SLOT] = QLR_SteamGameServer_SetBotPlayerCount;
	vtable[QLR_STEAM_GAMESERVER_SET_SERVER_NAME_SLOT] = QLR_SteamGameServer_SetServerName;
	vtable[QLR_STEAM_GAMESERVER_SET_MAP_NAME_SLOT] = QLR_SteamGameServer_SetMapName;
	vtable[QLR_STEAM_GAMESERVER_SET_PASSWORD_PROTECTED_SLOT] = QLR_SteamGameServer_SetPasswordProtected;
	vtable[QLR_STEAM_GAMESERVER_SET_GAME_TAGS_SLOT] = QLR_SteamGameServer_SetGameTags;
	vtable[QLR_STEAM_GAMESERVER_SET_KEY_VALUE_SLOT] = QLR_SteamGameServer_SetKeyValue;
	vtable[QLR_STEAM_GAMESERVER_CREATE_UNAUTHENTICATED_USER_SLOT] = QLR_SteamGameServer_CreateUnauthenticatedUserConnection;
	vtable[QLR_STEAM_GAMESERVER_UPDATE_USER_DATA_SLOT] = QLR_SteamGameServer_UpdateUserData;
	vtable[QLR_STEAM_GAMESERVER_BEGIN_AUTH_SESSION_SLOT] = QLR_SteamGameServer_BeginAuthSession;
	vtable[QLR_STEAM_GAMESERVER_END_AUTH_SESSION_SLOT] = QLR_SteamGameServer_EndAuthSession;
	vtable[QLR_STEAM_GAMESERVER_GET_PUBLIC_IP_SLOT] = QLR_SteamGameServer_GetPublicIP;
	vtable[QLR_STEAM_GAMESERVER_HANDLE_INCOMING_PACKET_SLOT] = QLR_SteamGameServer_HandleIncomingPacket;
	vtable[QLR_STEAM_GAMESERVER_GET_NEXT_OUTGOING_PACKET_SLOT] = QLR_SteamGameServer_GetNextOutgoingPacket;
	vtable[QLR_STEAM_GAMESERVER_ENABLE_HEARTBEATS_SLOT] = QLR_SteamGameServer_EnableHeartbeats;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamGameServerUtils
=============
*/
void *QLR_SteamAPI_SteamGameServerUtils( void ) {
	static void *vtable[QLR_STEAM_GAMESERVER_UTILS_VTABLE_SLOT_COUNT];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[QLR_STEAM_GAMESERVER_UTILS_GET_APP_ID_SLOT] = QLR_SteamGameServerUtils_GetAppID;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamGameServerStats
=============
*/
void *QLR_SteamAPI_SteamGameServerStats( void ) {
	static void *vtable[QLR_STEAM_GAMESERVERSTATS_VTABLE_SLOT_COUNT];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	++qlr_mock_state.steam_game_server_stats_interface_calls;
	if ( !qlr_mock_state.steam_game_server_stats_available ) {
		return NULL;
	}

	vtable[QLR_STEAM_GAMESERVERSTATS_REQUEST_USER_STATS_SLOT] = QLR_SteamGameServerStats_RequestUserStats;
	vtable[QLR_STEAM_GAMESERVERSTATS_GET_USER_STAT_FLOAT_SLOT] = QLR_SteamGameServerStats_GetUserStatFloat;
	vtable[QLR_STEAM_GAMESERVERSTATS_GET_USER_STAT_INT_SLOT] = QLR_SteamGameServerStats_GetUserStatInt;
	vtable[QLR_STEAM_GAMESERVERSTATS_GET_USER_ACHIEVEMENT_SLOT] = QLR_SteamGameServerStats_GetUserAchievement;
	vtable[QLR_STEAM_GAMESERVERSTATS_SET_USER_STAT_FLOAT_SLOT] = QLR_SteamGameServerStats_SetUserStatFloat;
	vtable[QLR_STEAM_GAMESERVERSTATS_SET_USER_STAT_INT_SLOT] = QLR_SteamGameServerStats_SetUserStatInt;
	vtable[QLR_STEAM_GAMESERVERSTATS_UPDATE_AVG_RATE_STAT_SLOT] = QLR_SteamGameServerStats_UpdateAvgRateStat;
	vtable[QLR_STEAM_GAMESERVERSTATS_SET_USER_ACHIEVEMENT_SLOT] = QLR_SteamGameServerStats_SetUserAchievement;
	vtable[QLR_STEAM_GAMESERVERSTATS_STORE_USER_STATS_SLOT] = QLR_SteamGameServerStats_StoreUserStats;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamGameServerNetworking
=============
*/
void *QLR_SteamAPI_SteamGameServerNetworking( void ) {
	static void *vtable[QLR_STEAM_NETWORKING_VTABLE_SLOT_COUNT];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[QLR_STEAM_NETWORKING_SEND_P2P_PACKET_SLOT] = QLR_SteamGameServerNetworking_SendP2PPacket;
	vtable[QLR_STEAM_NETWORKING_IS_P2P_PACKET_AVAILABLE_SLOT] = QLR_SteamGameServerNetworking_IsP2PPacketAvailable;
	vtable[QLR_STEAM_NETWORKING_READ_P2P_PACKET_SLOT] = QLR_SteamGameServerNetworking_ReadP2PPacket;
	vtable[QLR_STEAM_NETWORKING_ACCEPT_P2P_SESSION_SLOT] = QLR_SteamGameServerNetworking_AcceptP2PSessionWithUser;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamUGC
=============
*/
void *QLR_SteamAPI_SteamUGC( void ) {
	static void *vtable[QLR_STEAM_UGC_VTABLE_SLOT_COUNT];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[QLR_STEAM_UGC_CREATE_QUERY_ALL_UGC_REQUEST_SLOT] = QLR_SteamUGC_CreateQueryAllUGCRequest;
	vtable[QLR_STEAM_UGC_SEND_QUERY_UGC_REQUEST_SLOT] = QLR_SteamUGC_SendQueryUGCRequest;
	vtable[QLR_STEAM_UGC_GET_QUERY_UGC_RESULT_SLOT] = QLR_SteamUGC_GetQueryUGCResult;
	vtable[QLR_STEAM_UGC_GET_QUERY_UGC_PREVIEW_URL_SLOT] = QLR_SteamUGC_GetQueryUGCPreviewURL;
	vtable[QLR_STEAM_UGC_RELEASE_QUERY_UGC_REQUEST_SLOT] = QLR_SteamUGC_ReleaseQueryUGCRequest;
	vtable[QLR_STEAM_UGC_SUBSCRIBE_ITEM_SLOT] = QLR_SteamUGC_SubscribeItem;
	vtable[QLR_STEAM_UGC_UNSUBSCRIBE_ITEM_SLOT] = QLR_SteamUGC_UnsubscribeItem;
	vtable[QLR_STEAM_UGC_GET_NUM_SUBSCRIBED_ITEMS_SLOT] = QLR_SteamUGC_GetNumSubscribedItems;
	vtable[QLR_STEAM_UGC_GET_SUBSCRIBED_ITEMS_SLOT] = QLR_SteamUGC_GetSubscribedItems;
	vtable[QLR_STEAM_UGC_GET_ITEM_STATE_SLOT] = QLR_SteamUGC_GetItemState;
	vtable[QLR_STEAM_UGC_GET_ITEM_INSTALL_INFO_SLOT] = QLR_SteamUGC_GetItemInstallInfo;
	vtable[QLR_STEAM_UGC_GET_ITEM_DOWNLOAD_INFO_SLOT] = QLR_SteamUGC_GetItemDownloadInfo;
	vtable[QLR_STEAM_UGC_DOWNLOAD_ITEM_SLOT] = QLR_SteamUGC_DownloadItem;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamGameServerUGC
=============
*/
void *QLR_SteamAPI_SteamGameServerUGC( void ) {
	static void *vtable[QLR_STEAM_UGC_VTABLE_SLOT_COUNT];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[QLR_STEAM_UGC_SUBSCRIBE_ITEM_SLOT] = QLR_SteamGameServerUGC_SubscribeItem;
	vtable[QLR_STEAM_UGC_UNSUBSCRIBE_ITEM_SLOT] = QLR_SteamGameServerUGC_UnsubscribeItem;
	vtable[QLR_STEAM_UGC_GET_NUM_SUBSCRIBED_ITEMS_SLOT] = QLR_SteamUGC_GetNumSubscribedItems;
	vtable[QLR_STEAM_UGC_GET_SUBSCRIBED_ITEMS_SLOT] = QLR_SteamUGC_GetSubscribedItems;
	vtable[QLR_STEAM_UGC_GET_ITEM_STATE_SLOT] = QLR_SteamGameServerUGC_GetItemState;
	vtable[QLR_STEAM_UGC_GET_ITEM_INSTALL_INFO_SLOT] = QLR_SteamUGC_GetItemInstallInfo;
	vtable[QLR_STEAM_UGC_GET_ITEM_DOWNLOAD_INFO_SLOT] = QLR_SteamGameServerUGC_GetItemDownloadInfo;
	vtable[QLR_STEAM_UGC_DOWNLOAD_ITEM_SLOT] = QLR_SteamGameServerUGC_DownloadItem;
	return &iface;
}

/*
=============
QLR_SteamAPI_GetAuthSessionTicket
=============
*/
HAuthTicket QLR_SteamAPI_GetAuthSessionTicket( void *user, void *ticket, int ticket_size, uint32_t *length ) {
	(void)user;

	if ( !ticket || ticket_size <= 0 || !length ) {
		return 0;
	}

	if ( qlr_mock_state.ticket_length == 0 || qlr_mock_state.ticket_length > (uint32_t)ticket_size ) {
		return 0;
	}

	memcpy( ticket, qlr_mock_state.ticket, qlr_mock_state.ticket_length );
	*length = qlr_mock_state.ticket_length;
	return qlr_mock_state.ticket_handle;
}

/*
=============
QLR_SteamAPI_GetAuthTicketForWebApi
=============
*/
HAuthTicket QLR_SteamAPI_GetAuthTicketForWebApi( void *user, const char *identity ) {
	qlr_steam_get_ticket_for_web_api_response_raw_t event;
	uint32_t copyLength;

	(void)user;

	qlr_mock_state.web_api_ticket_calls++;
	Q_strncpyz( qlr_mock_state.web_api_ticket_identity, identity ? identity : "", sizeof( qlr_mock_state.web_api_ticket_identity ) );

	if ( qlr_mock_state.web_api_ticket_handle == 0 || qlr_mock_state.web_api_ticket_length == 0u ) {
		return 0;
	}

	if ( !qlr_mock_state.web_api_ticket_queue_callback ) {
		return qlr_mock_state.web_api_ticket_handle;
	}

	memset( &event, 0, sizeof( event ) );
	event.authTicket = qlr_mock_state.web_api_ticket_callback_handle;
	event.result = qlr_mock_state.web_api_ticket_result;
	event.ticketLength = qlr_mock_state.web_api_ticket_callback_length;

	copyLength = qlr_mock_state.web_api_ticket_callback_length;
	if ( copyLength > qlr_mock_state.web_api_ticket_length ) {
		copyLength = qlr_mock_state.web_api_ticket_length;
	}
	if ( copyLength > sizeof( event.ticket ) ) {
		copyLength = sizeof( event.ticket );
	}
	if ( copyLength > 0u ) {
		memcpy( event.ticket, qlr_mock_state.web_api_ticket, copyLength );
	}

	QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QLR_STEAM_CALLBACK_GET_TICKET_FOR_WEB_API_RESPONSE, 0ull, &event, sizeof( event ), qfalse );
	return qlr_mock_state.web_api_ticket_handle;
}

/*
=============
QLR_SteamAPI_BeginAuthSession
=============
*/
EBeginAuthSessionResult QLR_SteamAPI_BeginAuthSession( void *user, const void *ticket, int length, CSteamID steamId ) {
	(void)user;
	(void)ticket;
	(void)length;
	(void)steamId;
	return qlr_mock_state.auth_result;
}

/*
=============
QLR_SteamAPI_CancelAuthTicket
=============
*/
void QLR_SteamAPI_CancelAuthTicket( void *user, HAuthTicket handle ) {
	(void)user;

	qlr_mock_state.cancelled_ticket_handle = handle;
	qlr_mock_state.cancel_auth_ticket_calls++;
}

/*
=============
QLR_SteamAPI_EndAuthSession
=============
*/
void QLR_SteamAPI_EndAuthSession( void *user, CSteamID steamId ) {
	(void)user;
	(void)steamId;
}

/*
=============
QLR_SteamAPI_GetSteamID
=============
*/
CSteamID QLR_SteamAPI_GetSteamID( void *user ) {
	(void)user;
	CSteamID id = { .value = qlr_mock_state.steam_id_value };
	return id;
}

/*
=============
QL_ResetPlatformServices

Harness-local stub for the platform service cache reset owned by
platform_services.c in the engine build.
=============
*/
void QL_ResetPlatformServices( void ) {
}

#ifdef _WIN32
#include <windows.h>

/*
=============
QLR_LoadLibraryA
=============
*/
static HMODULE WINAPI QLR_LoadLibraryA( LPCSTR filename ) {
	(void)filename;
	return qlr_mock_state.library_available ? (HMODULE)(uintptr_t)0x1 : NULL;
}

/*
=============
QLR_GetProcAddress
=============
*/
static FARPROC WINAPI QLR_GetProcAddress( HMODULE module, LPCSTR symbol ) {
	return (FARPROC)dlsym( module, symbol );
}

/*
=============
QLR_FreeLibrary
=============
*/
static BOOL WINAPI QLR_FreeLibrary( HMODULE module ) {
	(void)module;
	return TRUE;
}

#define LoadLibraryA QLR_LoadLibraryA
#define GetProcAddress QLR_GetProcAddress
#define FreeLibrary QLR_FreeLibrary
#endif

#include "../src/common/platform/platform_steamworks.c"

#ifdef _WIN32
#undef LoadLibraryA
#undef GetProcAddress
#undef FreeLibrary
#endif

/*
=============
QLR_SteamworksMock_PrimeState

Inject mock bindings directly into the Steamworks state for harness usage.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_PrimeState( void ) {
	state.library = qlr_mock_state.library_available ? (void *)0x1 : NULL;
	state.initialised = qfalse;
	state.gameServerInitialised = qfalse;
	state.useGameServerUGC = qfalse;
	state.SteamAPI_Init = qlr_mock_state.steam_api_init_export_available ? QLR_SteamAPI_Init : NULL;
	state.SteamAPI_Shutdown = qlr_mock_state.steam_api_shutdown_export_available ? QLR_SteamAPI_Shutdown : NULL;
	state.SteamAPI_RunCallbacks = qlr_mock_state.steam_api_run_callbacks_export_available ? QLR_SteamAPI_RunCallbacks : NULL;
	state.SteamAPI_RegisterCallback = qlr_mock_state.steam_api_register_callback_export_available ? QLR_SteamAPI_RegisterCallback : NULL;
	state.SteamAPI_UnregisterCallback = qlr_mock_state.steam_api_unregister_callback_export_available ? QLR_SteamAPI_UnregisterCallback : NULL;
	state.SteamAPI_RegisterCallResult = qlr_mock_state.steam_api_register_call_result_export_available ? QLR_SteamAPI_RegisterCallResult : NULL;
	state.SteamAPI_UnregisterCallResult = qlr_mock_state.steam_api_unregister_call_result_export_available ? QLR_SteamAPI_UnregisterCallResult : NULL;
	state.SteamUser = qlr_mock_state.steam_user_export_available ? QLR_SteamAPI_SteamUser : NULL;
	state.SteamFriends = qlr_mock_state.steam_friends_export_available ? QLR_SteamAPI_SteamFriends : NULL;
	state.SteamUtils = qlr_mock_state.steam_utils_export_available ? QLR_SteamAPI_SteamUtils : NULL;
	state.SteamApps = qlr_mock_state.steam_apps_export_available ? QLR_SteamAPI_SteamApps : NULL;
	state.SteamUserStats = qlr_mock_state.steam_user_stats_export_available ? QLR_SteamAPI_SteamUserStats : NULL;
	state.SteamNetworking = qlr_mock_state.steam_networking_export_available ? QLR_SteamAPI_SteamNetworking : NULL;
	state.SteamMatchmaking = qlr_mock_state.steam_matchmaking_export_available ? QLR_SteamAPI_SteamMatchmaking : NULL;
	state.SteamMatchmakingServers = qlr_mock_state.steam_matchmaking_servers_export_available ? QLR_SteamAPI_SteamMatchmakingServers : NULL;
	state.SteamUGC = qlr_mock_state.steam_ugc_export_available ? QLR_SteamAPI_SteamUGC : NULL;
	state.SteamGameServerUGC = qlr_mock_state.steam_game_server_ugc_export_available ? QLR_SteamAPI_SteamGameServerUGC : NULL;
	state.SteamGameServer_Init = qlr_mock_state.steam_game_server_init_export_available ? QLR_SteamAPI_SteamGameServerInit : NULL;
	state.SteamGameServer = qlr_mock_state.steam_game_server_export_available ? QLR_SteamAPI_SteamGameServer : NULL;
	state.SteamGameServerUtils = qlr_mock_state.steam_game_server_utils_export_available ? QLR_SteamAPI_SteamGameServerUtils : NULL;
	state.SteamGameServerStats = qlr_mock_state.steam_game_server_stats_export_available ? QLR_SteamAPI_SteamGameServerStats : NULL;
	state.SteamGameServer_Shutdown = qlr_mock_state.steam_game_server_shutdown_export_available ? QLR_SteamAPI_SteamGameServerShutdown : NULL;
	state.SteamGameServer_RunCallbacks = qlr_mock_state.steam_game_server_run_callbacks_export_available ? QLR_SteamAPI_SteamGameServerRunCallbacks : NULL;
	state.SteamGameServerNetworking = qlr_mock_state.steam_game_server_networking_export_available ? QLR_SteamAPI_SteamGameServerNetworking : NULL;
	state.GetAuthSessionTicket = qlr_mock_state.auth_session_ticket_export_available ? QLR_SteamAPI_GetAuthSessionTicket : NULL;
	state.GetAuthTicketForWebApi = qlr_mock_state.web_api_ticket_export_available ? QLR_SteamAPI_GetAuthTicketForWebApi : NULL;
	state.BeginAuthSession = qlr_mock_state.begin_auth_session_export_available ? QLR_SteamAPI_BeginAuthSession : NULL;
	state.CancelAuthTicket = qlr_mock_state.cancel_auth_ticket_export_available ? QLR_SteamAPI_CancelAuthTicket : NULL;
	state.EndAuthSession = qlr_mock_state.end_auth_session_export_available ? QLR_SteamAPI_EndAuthSession : NULL;
	state.GetSteamID = qlr_mock_state.get_steam_id_export_available ? QLR_SteamAPI_GetSteamID : NULL;
	memset( &state.clientCallbacks, 0, sizeof( state.clientCallbacks ) );
	QLR_SteamworksMock_ClearCallbackState();
}

/*
=============
QLR_SteamworksMock_Capture
=============
*/
static void QLR_SteamworksMock_Capture( const char *kind, const char *text, uint64_t id, uint64_t auxId, uint32_t appId, int result ) {
	qlr_mock_state.client_callback_capture_count++;
	Q_strncpyz( qlr_mock_state.last_callback_kind, kind ? kind : "", sizeof( qlr_mock_state.last_callback_kind ) );
	Q_strncpyz( qlr_mock_state.last_callback_text, text ? text : "", sizeof( qlr_mock_state.last_callback_text ) );
	qlr_mock_state.last_callback_id = id;
	qlr_mock_state.last_callback_aux_id = auxId;
	qlr_mock_state.last_callback_app_id = appId;
	qlr_mock_state.last_callback_result = result;
}

/*
=============
QLR_SteamworksHarness_OnRichPresenceJoinRequested
=============
*/
static void QLR_SteamworksHarness_OnRichPresenceJoinRequested( void *context, const ql_steam_rich_presence_join_requested_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "rich_presence", event->command, event->requester.steamId.value, 0ull, 0u, 0 );
}

/*
=============
QLR_SteamworksHarness_OnUserStatsReceived
=============
*/
static void QLR_SteamworksHarness_OnUserStatsReceived( void *context, const ql_steam_user_stats_received_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "user_stats_received", event->name, event->steamId.value, 0ull, event->gameId, event->result );
}

/*
=============
QLR_SteamworksHarness_OnPersonaStateChange
=============
*/
static void QLR_SteamworksHarness_OnPersonaStateChange( void *context, const ql_steam_persona_state_change_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "persona_state_change", event->summary.name, event->steamId.value, event->changeFlags, event->summary.appId, event->summary.personaState );
}

/*
=============
QLR_SteamworksHarness_OnP2PSessionRequest
=============
*/
static void QLR_SteamworksHarness_OnP2PSessionRequest( void *context, const ql_steam_p2p_session_request_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "p2p_session_request", "", event->remoteId.value, 0ull, 0u, 0 );
}

/*
=============
QLR_SteamworksHarness_OnGameServerChangeRequested
=============
*/
static void QLR_SteamworksHarness_OnGameServerChangeRequested( void *context, const ql_steam_game_server_change_requested_t *event ) {
	char serverAndPassword[QL_STEAM_SERVER_LENGTH + QL_STEAM_PASSWORD_LENGTH + 2];

	(void)context;

	if ( !event ) {
		return;
	}

	Com_sprintf( serverAndPassword, sizeof( serverAndPassword ), "%s|%s", event->server, event->password );
	QLR_SteamworksMock_Capture( "game_server_change_requested", serverAndPassword, 0ull, 0ull, 0u, 0 );
}

/*
=============
QLR_SteamworksHarness_OnFriendRichPresenceUpdate
=============
*/
static void QLR_SteamworksHarness_OnFriendRichPresenceUpdate( void *context, const ql_steam_friend_rich_presence_update_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "friend_rich_presence_update", event->summary.status, event->steamId.value, event->summary.gameId, event->appId, event->summary.playingQuake ? 1 : 0 );
}

/*
=============
QLR_SteamworksHarness_OnAvatarImageLoaded
=============
*/
static void QLR_SteamworksHarness_OnAvatarImageLoaded( void *context, const ql_steam_avatar_image_loaded_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "avatar_image_loaded", "", event->steamId.value, (uint64_t)event->image, (uint32_t)event->width, event->height );
}

/*
=============
QLR_SteamworksHarness_OnLobbyCreated
=============
*/
static void QLR_SteamworksHarness_OnLobbyCreated( void *context, const ql_steam_lobby_created_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "lobby_created", "", event->lobbyId.value, 0ull, 0u, event->result );
}

/*
=============
QLR_SteamworksHarness_OnLobbyEnter
=============
*/
static void QLR_SteamworksHarness_OnLobbyEnter( void *context, const ql_steam_lobby_enter_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "lobby_enter", "", event->lobbyId.value, 0ull, event->chatPermissions, event->response );
}

/*
=============
QLR_SteamworksHarness_OnLobbyChatUpdate
=============
*/
static void QLR_SteamworksHarness_OnLobbyChatUpdate( void *context, const ql_steam_lobby_chat_update_t *event ) {
	char makingChangeUser[32];

	(void)context;

	if ( !event ) {
		return;
	}

	Com_sprintf( makingChangeUser, sizeof( makingChangeUser ), "%llx", (unsigned long long)event->makingChangeUser.value );
	QLR_SteamworksMock_Capture( "lobby_chat_update", makingChangeUser, event->lobbyId.value, event->changedUser.value, 0u, (int)event->stateChange );
}

/*
=============
QLR_SteamworksHarness_OnLobbyChatMessage
=============
*/
static void QLR_SteamworksHarness_OnLobbyChatMessage( void *context, const ql_steam_lobby_chat_message_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "lobby_chat_message", event->message, event->lobbyId.value, event->chatter.value, (uint32_t)event->chatId, event->chatEntryType );
}

/*
=============
QLR_SteamworksHarness_OnLobbyDataUpdate
=============
*/
static void QLR_SteamworksHarness_OnLobbyDataUpdate( void *context, const ql_steam_lobby_data_update_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "lobby_data_update", "", event->lobbyId.value, event->memberId.value, 0u, event->success ? 1 : 0 );
}

/*
=============
QLR_SteamworksHarness_OnLobbyGameCreated
=============
*/
static void QLR_SteamworksHarness_OnLobbyGameCreated( void *context, const ql_steam_lobby_game_created_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "lobby_game_created", "", event->lobbyId.value, event->serverId.value, event->serverIp, event->serverPort );
}

/*
=============
QLR_SteamworksHarness_OnLobbyKicked
=============
*/
static void QLR_SteamworksHarness_OnLobbyKicked( void *context, const ql_steam_lobby_kicked_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "lobby_kicked", "", event->lobbyId.value, event->adminId.value, 0u, event->disconnected ? 1 : 0 );
}

/*
=============
QLR_SteamworksHarness_OnGameLobbyJoinRequested
=============
*/
static void QLR_SteamworksHarness_OnGameLobbyJoinRequested( void *context, const ql_steam_game_lobby_join_requested_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "game_lobby_join_requested", "", event->lobbyId.value, event->friendId.value, 0u, 0 );
}

/*
=============
QLR_SteamworksHarness_OnMicroAuthorizationResponse
=============
*/
static void QLR_SteamworksHarness_OnMicroAuthorizationResponse( void *context, const ql_steam_microtxn_authorization_response_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "microtxn", "", event->orderId, 0ull, event->appId, event->authorized ? 1 : 0 );
}

/*
=============
QLR_SteamworksHarness_OnUGCQueryCompleted
=============
*/
static void QLR_SteamworksHarness_OnUGCQueryCompleted( void *context, const ql_steam_ugc_query_completed_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "ugc", "", event->callHandle, event->queryHandle, event->numResultsReturned, event->result );
}

/*
=============
QLR_SteamworksHarness_OnItemInstalled
=============
*/
static void QLR_SteamworksHarness_OnItemInstalled( void *context, const ql_steam_item_installed_t *event ) {
	uint64_t itemId;

	(void)context;

	if ( !event ) {
		return;
	}

	itemId = ( (uint64_t)event->itemIdHigh << 32 ) | event->itemIdLow;
	QLR_SteamworksMock_Capture( "workshop_installed", "", itemId, 0ull, event->appId, 0 );
}

/*
=============
QLR_SteamworksHarness_OnDownloadItemResult
=============
*/
static void QLR_SteamworksHarness_OnDownloadItemResult( void *context, const ql_steam_download_item_result_t *event ) {
	uint64_t itemId;

	(void)context;

	if ( !event ) {
		return;
	}

	itemId = ( (uint64_t)event->itemIdHigh << 32 ) | event->itemIdLow;
	QLR_SteamworksMock_Capture( "workshop_download_result", "", itemId, 0ull, event->appId, event->result );
}

/*
=============
QLR_SteamworksHarness_OnServersConnected
=============
*/
static void QLR_SteamworksHarness_OnServersConnected( void *context, const ql_steam_server_connected_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "server_connected", "", 0ull, 0ull, 0u, 0 );
}

/*
=============
QLR_SteamworksHarness_OnConnectFailure
=============
*/
static void QLR_SteamworksHarness_OnConnectFailure( void *context, const ql_steam_server_connect_failure_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "server_connect_failure", "", 0ull, 0ull, event->stillRetrying ? 1u : 0u, event->result );
}

/*
=============
QLR_SteamworksHarness_OnServersDisconnected
=============
*/
static void QLR_SteamworksHarness_OnServersDisconnected( void *context, const ql_steam_server_disconnected_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "server_disconnected", "", 0ull, 0ull, 0u, event->result );
}

/*
=============
QLR_SteamworksHarness_OnValidateAuthTicketResponse
=============
*/
static void QLR_SteamworksHarness_OnValidateAuthTicketResponse( void *context, const ql_steam_validate_auth_ticket_response_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "server_validate_auth", "", event->steamId.value, event->ownerSteamId.value, 0u, (int)event->authSessionResponse );
}

/*
=============
QLR_SteamworksHarness_OnServerP2PSessionRequest
=============
*/
static void QLR_SteamworksHarness_OnServerP2PSessionRequest( void *context, const ql_steam_p2p_session_request_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "server_p2p_session_request", "", event->remoteId.value, 0ull, 0u, 0 );
}

/*
=============
QLR_SteamworksHarness_OnGSStatsReceived
=============
*/
static void QLR_SteamworksHarness_OnGSStatsReceived( void *context, const ql_steam_gs_stats_received_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "server_gs_stats_received", "", event->steamId.value, 0ull, 0u, event->result );
}

/*
=============
QLR_SteamworksHarness_OnGSStatsStored
=============
*/
static void QLR_SteamworksHarness_OnGSStatsStored( void *context, const ql_steam_gs_stats_stored_t *event ) {
	(void)context;

	if ( !event ) {
		return;
	}

	QLR_SteamworksMock_Capture( "server_gs_stats_stored", "", event->steamId.value, 0ull, 0u, event->result );
}

/*
=============
QLR_SteamworksMock_QueueCallback
=============
*/
static qboolean QLR_SteamworksMock_QueueCallback( qboolean callResult, qboolean gameServer, int callbackId, SteamAPICall_t callHandle, const void *payload, uint32_t payloadSize, qboolean ioFailure ) {
	qlr_pending_callback_t *pending;

	if ( qlr_mock_state.pending_callback_count >= QLR_MAX_PENDING_CALLBACKS ) {
		return qfalse;
	}

	pending = &qlr_mock_state.pending_callbacks[qlr_mock_state.pending_callback_count++];
	memset( pending, 0, sizeof( *pending ) );
	pending->callResult = callResult;
	pending->gameServer = gameServer;
	pending->callbackId = callbackId;
	pending->callHandle = callHandle;
	pending->ioFailure = ioFailure;
	pending->payloadSize = payloadSize;
	if ( payload && payloadSize > 0 ) {
		if ( payloadSize > sizeof( pending->payload ) ) {
			qlr_mock_state.pending_callback_count--;
			memset( pending, 0, sizeof( *pending ) );
			return qfalse;
		}
		memcpy( pending->payload, payload, payloadSize );
	}

	return qtrue;
}

/*
=============
QLR_Steamworks_RegisterHarnessCallbacks
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_RegisterHarnessCallbacks( void ) {
	ql_steam_client_callback_bindings_t clientBindings;
	ql_steam_avatar_callback_bindings_t avatarBindings;
	ql_steam_lobby_callback_bindings_t lobbyBindings;
	ql_steam_micro_callback_bindings_t microBindings;
	ql_steam_workshop_callback_bindings_t workshopBindings;

	memset( &clientBindings, 0, sizeof( clientBindings ) );
	memset( &avatarBindings, 0, sizeof( avatarBindings ) );
	memset( &lobbyBindings, 0, sizeof( lobbyBindings ) );
	memset( &microBindings, 0, sizeof( microBindings ) );
	memset( &workshopBindings, 0, sizeof( workshopBindings ) );

	clientBindings.onRichPresenceJoinRequested = QLR_SteamworksHarness_OnRichPresenceJoinRequested;
	clientBindings.onUserStatsReceived = QLR_SteamworksHarness_OnUserStatsReceived;
	clientBindings.onPersonaStateChange = QLR_SteamworksHarness_OnPersonaStateChange;
	clientBindings.onP2PSessionRequest = QLR_SteamworksHarness_OnP2PSessionRequest;
	clientBindings.onGameServerChangeRequested = QLR_SteamworksHarness_OnGameServerChangeRequested;
	clientBindings.onFriendRichPresenceUpdate = QLR_SteamworksHarness_OnFriendRichPresenceUpdate;
	clientBindings.onUGCQueryCompleted = QLR_SteamworksHarness_OnUGCQueryCompleted;
	avatarBindings.onAvatarImageLoaded = QLR_SteamworksHarness_OnAvatarImageLoaded;
	lobbyBindings.onLobbyCreated = QLR_SteamworksHarness_OnLobbyCreated;
	lobbyBindings.onLobbyEnter = QLR_SteamworksHarness_OnLobbyEnter;
	lobbyBindings.onLobbyChatUpdate = QLR_SteamworksHarness_OnLobbyChatUpdate;
	lobbyBindings.onLobbyChatMessage = QLR_SteamworksHarness_OnLobbyChatMessage;
	lobbyBindings.onLobbyDataUpdate = QLR_SteamworksHarness_OnLobbyDataUpdate;
	lobbyBindings.onLobbyGameCreated = QLR_SteamworksHarness_OnLobbyGameCreated;
	lobbyBindings.onLobbyKicked = QLR_SteamworksHarness_OnLobbyKicked;
	lobbyBindings.onGameLobbyJoinRequested = QLR_SteamworksHarness_OnGameLobbyJoinRequested;
	microBindings.onAuthorizationResponse = QLR_SteamworksHarness_OnMicroAuthorizationResponse;
	workshopBindings.onItemInstalled = QLR_SteamworksHarness_OnItemInstalled;
	workshopBindings.onDownloadItemResult = QLR_SteamworksHarness_OnDownloadItemResult;

	if ( !QL_Steamworks_RegisterClientCallbacks( &clientBindings ) ) {
		return qfalse;
	}
	if ( !QL_Steamworks_RegisterAvatarCallbacks( &avatarBindings ) ) {
		QL_Steamworks_UnregisterClientCallbacks();
		return qfalse;
	}
	if ( !QL_Steamworks_RegisterLobbyCallbacks( &lobbyBindings ) ) {
		QL_Steamworks_UnregisterAvatarCallbacks();
		QL_Steamworks_UnregisterClientCallbacks();
		return qfalse;
	}
	if ( !QL_Steamworks_RegisterMicroCallbacks( &microBindings ) ) {
		QL_Steamworks_UnregisterLobbyCallbacks();
		QL_Steamworks_UnregisterAvatarCallbacks();
		QL_Steamworks_UnregisterClientCallbacks();
		return qfalse;
	}
	if ( !QL_Steamworks_RegisterWorkshopCallbacks( &workshopBindings ) ) {
		QL_Steamworks_UnregisterMicroCallbacks();
		QL_Steamworks_UnregisterLobbyCallbacks();
		QL_Steamworks_UnregisterAvatarCallbacks();
		QL_Steamworks_UnregisterClientCallbacks();
		return qfalse;
	}

	return qtrue;
}

/*
=============
QLR_Steamworks_UnregisterHarnessCallbacks
=============
*/
QLR_EXPORT void QLR_Steamworks_UnregisterHarnessCallbacks( void ) {
	QL_Steamworks_UnregisterWorkshopCallbacks();
	QL_Steamworks_UnregisterMicroCallbacks();
	QL_Steamworks_UnregisterLobbyCallbacks();
	QL_Steamworks_UnregisterAvatarCallbacks();
	QL_Steamworks_UnregisterClientCallbacks();
}

/*
=============
QLR_Steamworks_UnregisterRichPresenceJoinRequestedCallback
=============
*/
QLR_EXPORT void QLR_Steamworks_UnregisterRichPresenceJoinRequestedCallback( void ) {
	ql_steam_client_callback_state_t *callbackState;

	callbackState = &state.clientCallbacks;
	QL_Steamworks_UnregisterCallbackObject( &callbackState->richPresenceJoinRequested );
}

/*
=============
QLR_SteamworksMock_SetUnregisterCallbackAvailable
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetUnregisterCallbackAvailable( qboolean available ) {
	state.SteamAPI_UnregisterCallback = available ? QLR_SteamAPI_UnregisterCallback : NULL;
}

/*
=============
QLR_SteamworksMock_GetRichPresenceJoinRequestedCallbackRegistered
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_GetRichPresenceJoinRequestedCallbackRegistered( void ) {
	return ( state.clientCallbacks.richPresenceJoinRequested.callbackFlags & 0x01 ) ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_GetWebApiTicketCallbackRegistered
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_GetWebApiTicketCallbackRegistered( void ) {
	return ( state.clientCallbacks.webApiTicketResponse.callbackFlags & 0x01 ) ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_GetRegisteredCallbackCount
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetRegisteredCallbackCount( void ) {
	return qlr_mock_state.registered_callback_count;
}

/*
=============
QLR_Steamworks_RegisterServerHarnessCallbacks
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_RegisterServerHarnessCallbacks( void ) {
	ql_steam_server_callback_bindings_t serverBindings;

	memset( &serverBindings, 0, sizeof( serverBindings ) );
	serverBindings.onServersConnected = QLR_SteamworksHarness_OnServersConnected;
	serverBindings.onConnectFailure = QLR_SteamworksHarness_OnConnectFailure;
	serverBindings.onServersDisconnected = QLR_SteamworksHarness_OnServersDisconnected;
	serverBindings.onValidateAuthTicketResponse = QLR_SteamworksHarness_OnValidateAuthTicketResponse;
	serverBindings.onP2PSessionRequest = QLR_SteamworksHarness_OnServerP2PSessionRequest;
	serverBindings.onGSStatsReceived = QLR_SteamworksHarness_OnGSStatsReceived;
	serverBindings.onGSStatsStored = QLR_SteamworksHarness_OnGSStatsStored;

	return QL_Steamworks_RegisterServerCallbacks( &serverBindings );
}

/*
=============
QLR_Steamworks_UnregisterServerHarnessCallbacks
=============
*/
QLR_EXPORT void QLR_Steamworks_UnregisterServerHarnessCallbacks( void ) {
	QL_Steamworks_UnregisterServerCallbacks();
}

/*
=============
QLR_Steamworks_BindUGCQueryCallResult
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BindUGCQueryCallResult( uint64_t callHandle ) {
	return QL_Steamworks_BindUGCQueryCallResult( (SteamAPICall_t)callHandle );
}

/*
=============
QLR_Steamworks_UnbindUGCQueryCallResult
=============
*/
QLR_EXPORT void QLR_Steamworks_UnbindUGCQueryCallResult( void ) {
	ql_steam_client_callback_state_t *callbackState;

	callbackState = &state.clientCallbacks;
	QL_Steamworks_UnbindCallResultObject( &callbackState->ugcQueryCompleted, &callbackState->ugcCallHandle, &callbackState->ugcCallBound );
}

/*
=============
QLR_SteamworksMock_SetUnregisterCallResultAvailable
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetUnregisterCallResultAvailable( qboolean available ) {
	state.SteamAPI_UnregisterCallResult = available ? QLR_SteamAPI_UnregisterCallResult : NULL;
}

/*
=============
QLR_SteamworksMock_GetUGCQueryCallResultBound
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_GetUGCQueryCallResultBound( void ) {
	return state.clientCallbacks.ugcCallBound ? qtrue : qfalse;
}

/*
=============
QLR_SteamworksMock_GetUGCQueryCallResultHandle
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetUGCQueryCallResultHandle( void ) {
	return (uint64_t)state.clientCallbacks.ugcCallHandle;
}

/*
=============
QLR_Steamworks_RequestAllUGCQuery
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_RequestAllUGCQuery( uint32_t filter ) {
	return QL_Steamworks_RequestAllUGCQuery( filter );
}

/*
=============
QLR_Steamworks_GetQueryUGCResult
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetQueryUGCResult( uint64_t queryHandle, uint32_t index, uint64_t *outPublishedFileId, char *title, size_t titleSize, char *description, size_t descriptionSize ) {
	return QL_Steamworks_GetQueryUGCResult( queryHandle, index, outPublishedFileId, title, titleSize, description, descriptionSize );
}

/*
=============
QLR_Steamworks_GetQueryUGCPreviewURL
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetQueryUGCPreviewURL( uint64_t queryHandle, uint32_t index, char *buffer, size_t bufferSize ) {
	return QL_Steamworks_GetQueryUGCPreviewURL( queryHandle, index, buffer, bufferSize );
}

/*
=============
QLR_Steamworks_ReleaseQueryUGCRequest
=============
*/
QLR_EXPORT void QLR_Steamworks_ReleaseQueryUGCRequest( uint64_t queryHandle ) {
	QL_Steamworks_ReleaseQueryUGCRequest( queryHandle );
}

/*
=============
QLR_Steamworks_RunCallbackPump
=============
*/
QLR_EXPORT void QLR_Steamworks_RunCallbackPump( void ) {
	QL_Steamworks_RunCallbacks();
}

/*
=============
QLR_Steamworks_RunServerCallbackPump
=============
*/
QLR_EXPORT void QLR_Steamworks_RunServerCallbackPump( void ) {
	QL_Steamworks_RunServerCallbacks();
}

/*
=============
QLR_SteamworksMock_QueueRichPresenceJoinRequested
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueRichPresenceJoinRequested( uint64_t friendId, const char *command ) {
	ql_steam_game_rich_presence_join_requested_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.steamIDFriend.value = friendId;
	Q_strncpyz( event.connect, command ? command : "", sizeof( event.connect ) );
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, 0x151, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueUserStatsReceived
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueUserStatsReceived( uint64_t gameId, int result, uint64_t steamId ) {
	ql_steam_user_stats_received_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.gameId = gameId;
	event.result = result;
	event.steamIDUser.value = steamId;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_USER_STATS_RECEIVED, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueuePersonaStateChange
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueuePersonaStateChange( uint64_t steamId, uint32_t changeFlags ) {
	ql_steam_persona_state_change_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.steamID.value = steamId;
	event.changeFlags = changeFlags;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_PERSONA_STATE_CHANGE, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueP2PSessionRequest
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueP2PSessionRequest( uint64_t remoteId ) {
	ql_steam_p2p_session_request_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.remoteId.value = remoteId;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_P2P_SESSION_REQUEST, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueGameServerChangeRequested
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueGameServerChangeRequested( const char *server, const char *password ) {
	ql_steam_game_server_change_requested_raw_t event;

	memset( &event, 0, sizeof( event ) );
	Q_strncpyz( event.server, server ? server : "", sizeof( event.server ) );
	Q_strncpyz( event.password, password ? password : "", sizeof( event.password ) );
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_GAME_SERVER_CHANGE_REQUESTED, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueFriendRichPresenceUpdate
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueFriendRichPresenceUpdate( uint64_t steamId, uint32_t appId ) {
	ql_steam_friend_rich_presence_update_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.steamIDFriendLow = (uint32_t)( steamId & 0xffffffffu );
	event.steamIDFriendHigh = (uint32_t)( steamId >> 32 );
	event.appId = appId;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_FRIEND_RICH_PRESENCE_UPDATE, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueAvatarImageLoaded
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueAvatarImageLoaded( uint64_t steamId, int image, int width, int height ) {
	ql_steam_avatar_image_loaded_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.steamIDLow = (uint32_t)( steamId & 0xffffffffu );
	event.steamIDHigh = (uint32_t)( steamId >> 32 );
	event.image = image;
	event.wide = width;
	event.tall = height;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_AVATAR_IMAGE_LOADED, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueLobbyCreated
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueLobbyCreated( uint64_t lobbyId, int result ) {
	ql_steam_lobby_created_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.lobbyId.value = lobbyId;
	event.result = result;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_LOBBY_CREATED, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueLobbyEnter
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueLobbyEnter( uint64_t lobbyId, uint32_t chatPermissions, int locked, uint32_t response ) {
	ql_steam_lobby_enter_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.lobbyId.value = lobbyId;
	event.chatPermissions = chatPermissions;
	event.locked = locked ? qtrue : qfalse;
	event.response = response;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_LOBBY_ENTER, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueLobbyChatUpdate
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueLobbyChatUpdate( uint64_t lobbyId, uint64_t changedUser, uint64_t makingChangeUser, uint32_t stateChange ) {
	ql_steam_lobby_chat_update_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.lobbyId.value = lobbyId;
	event.changedUser.value = changedUser;
	event.makingChangeUser.value = makingChangeUser;
	event.stateChange = stateChange;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_LOBBY_CHAT_UPDATE, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueLobbyChatMessage
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueLobbyChatMessage( uint64_t lobbyId, uint64_t chatter, int chatEntryType, int chatId ) {
	ql_steam_lobby_chat_message_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.lobbyId.value = lobbyId;
	event.chatter.value = chatter;
	event.chatEntryType = chatEntryType;
	event.chatId = chatId;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_LOBBY_CHAT_MESSAGE, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueLobbyDataUpdate
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueLobbyDataUpdate( uint64_t lobbyId, uint64_t memberId, int success ) {
	ql_steam_lobby_data_update_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.lobbyId.value = lobbyId;
	event.memberId.value = memberId;
	event.success = success ? qtrue : qfalse;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_LOBBY_DATA_UPDATE, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueLobbyGameCreated
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueLobbyGameCreated( uint64_t lobbyId, uint64_t serverId, uint32_t serverIp, uint16_t serverPort ) {
	ql_steam_lobby_game_created_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.lobbyId.value = lobbyId;
	event.serverId.value = serverId;
	event.serverIp = serverIp;
	event.serverPort = serverPort;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_LOBBY_GAME_CREATED, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueLobbyKicked
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueLobbyKicked( uint64_t lobbyId, uint64_t adminId, int disconnected ) {
	ql_steam_lobby_kicked_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.lobbyId.value = lobbyId;
	event.adminId.value = adminId;
	event.disconnected = disconnected ? qtrue : qfalse;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_LOBBY_KICKED, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueGameLobbyJoinRequested
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueGameLobbyJoinRequested( uint64_t lobbyId, uint64_t friendId ) {
	ql_steam_game_lobby_join_requested_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.lobbyId.value = lobbyId;
	event.friendId.value = friendId;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_GAME_LOBBY_JOIN_REQUESTED, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueMicroAuthorizationResponse
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueMicroAuthorizationResponse( uint32_t appId, uint64_t orderId, int authorized ) {
	ql_steam_microtxn_authorization_response_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.appId = appId;
	event.orderId = orderId;
	event.authorized = authorized ? qtrue : qfalse;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, 0x98, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueItemInstalled
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueItemInstalled( uint32_t appId, uint32_t itemIdLow, uint32_t itemIdHigh ) {
	ql_steam_item_installed_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.appId = appId;
	event.itemIdLow = itemIdLow;
	event.itemIdHigh = itemIdHigh;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_ITEM_INSTALLED, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueDownloadItemResult
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueDownloadItemResult( uint32_t appId, uint32_t itemIdLow, uint32_t itemIdHigh, int result ) {
	ql_steam_download_item_result_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.appId = appId;
	event.itemIdLow = itemIdLow;
	event.itemIdHigh = itemIdHigh;
	event.result = result;
	return QLR_SteamworksMock_QueueCallback( qfalse, qfalse, QL_STEAM_CALLBACK_DOWNLOAD_ITEM_RESULT, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueUGCQueryCompletedEx
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueUGCQueryCompletedEx( uint64_t callHandle, uint64_t queryHandle, int result, uint32_t numResultsReturned, uint32_t totalMatchingResults, int cachedData, int ioFailure, int includePayload ) {
	ql_steam_ugc_query_completed_raw_t event;

	if ( !includePayload ) {
		return QLR_SteamworksMock_QueueCallback( qtrue, qfalse, QL_STEAM_CALLBACK_UGC_QUERY_COMPLETED, (SteamAPICall_t)callHandle, NULL, 0u, ioFailure ? qtrue : qfalse );
	}

	memset( &event, 0, sizeof( event ) );
	event.queryHandle = queryHandle;
	event.result = result;
	event.numResultsReturned = numResultsReturned;
	event.totalMatchingResults = totalMatchingResults;
	event.cachedData = cachedData ? qtrue : qfalse;
	return QLR_SteamworksMock_QueueCallback( qtrue, qfalse, QL_STEAM_CALLBACK_UGC_QUERY_COMPLETED, (SteamAPICall_t)callHandle, &event, sizeof( event ), ioFailure ? qtrue : qfalse );
}

/*
=============
QLR_SteamworksMock_QueueUGCQueryCompleted
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueUGCQueryCompleted( uint64_t callHandle, uint64_t queryHandle, int result, uint32_t numResultsReturned, uint32_t totalMatchingResults, int cachedData ) {
	return QLR_SteamworksMock_QueueUGCQueryCompletedEx( callHandle, queryHandle, result, numResultsReturned, totalMatchingResults, cachedData, qfalse, qtrue );
}

/*
=============
QLR_SteamworksMock_QueueServersConnected
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueServersConnected( void ) {
	ql_steam_servers_connected_raw_t event;

	memset( &event, 0, sizeof( event ) );
	return QLR_SteamworksMock_QueueCallback( qfalse, qtrue, QL_STEAM_CALLBACK_STEAM_SERVERS_CONNECTED, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueServerConnectFailure
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueServerConnectFailure( int result, int stillRetrying ) {
	ql_steam_server_connect_failure_raw_t event;

	(void)stillRetrying;

	memset( &event, 0, sizeof( event ) );
	event.result = result;
	return QLR_SteamworksMock_QueueCallback( qfalse, qtrue, QL_STEAM_CALLBACK_STEAM_SERVER_CONNECT_FAILURE, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueServersDisconnected
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueServersDisconnected( int result ) {
	ql_steam_servers_disconnected_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.result = result;
	return QLR_SteamworksMock_QueueCallback( qfalse, qtrue, QL_STEAM_CALLBACK_STEAM_SERVERS_DISCONNECTED, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueValidateAuthTicketResponse
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueValidateAuthTicketResponse( uint64_t steamId, uint64_t ownerSteamId, int authSessionResponse ) {
	ql_steam_validate_auth_ticket_response_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.steamIdLow = (uint32_t)( steamId & 0xffffffffu );
	event.steamIdHigh = (uint32_t)( steamId >> 32 );
	event.ownerSteamIdLow = (uint32_t)( ownerSteamId & 0xffffffffu );
	event.ownerSteamIdHigh = (uint32_t)( ownerSteamId >> 32 );
	event.authSessionResponse = authSessionResponse;
	return QLR_SteamworksMock_QueueCallback( qfalse, qtrue, QL_STEAM_CALLBACK_VALIDATE_AUTH_TICKET_RESPONSE, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueServerP2PSessionRequest
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueServerP2PSessionRequest( uint64_t remoteId ) {
	ql_steam_p2p_session_request_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.remoteId.value = remoteId;
	return QLR_SteamworksMock_QueueCallback( qfalse, qtrue, QL_STEAM_CALLBACK_P2P_SESSION_REQUEST, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueGSStatsReceived
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueGSStatsReceived( uint64_t steamId, int result ) {
	ql_steam_gs_stats_received_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.result = result;
	event.steamIdLow = (uint32_t)( steamId & 0xffffffffu );
	event.steamIdHigh = (uint32_t)( steamId >> 32 );
	return QLR_SteamworksMock_QueueCallback( qfalse, qtrue, QL_STEAM_CALLBACK_GS_STATS_RECEIVED, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueGSStatsStored
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueGSStatsStored( uint64_t steamId, int result ) {
	ql_steam_gs_stats_stored_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.result = result;
	event.steamIdLow = (uint32_t)( steamId & 0xffffffffu );
	event.steamIdHigh = (uint32_t)( steamId >> 32 );
	return QLR_SteamworksMock_QueueCallback( qfalse, qtrue, QL_STEAM_CALLBACK_GS_STATS_STORED, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_GetRegisterCallbackCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetRegisterCallbackCalls( void ) {
	return qlr_mock_state.register_callback_calls;
}

/*
=============
QLR_SteamworksMock_GetUnregisterCallbackCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUnregisterCallbackCalls( void ) {
	return qlr_mock_state.unregister_callback_calls;
}

/*
=============
QLR_SteamworksMock_GetRegisterCallResultCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetRegisterCallResultCalls( void ) {
	return qlr_mock_state.register_call_result_calls;
}

/*
=============
QLR_SteamworksMock_GetUnregisterCallResultCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUnregisterCallResultCalls( void ) {
	return qlr_mock_state.unregister_call_result_calls;
}

/*
=============
QLR_SteamworksMock_GetClientCallbackCaptureCount
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetClientCallbackCaptureCount( void ) {
	return qlr_mock_state.client_callback_capture_count;
}

/*
=============
QLR_SteamworksMock_GetLastCallbackKind
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetLastCallbackKind( void ) {
	return qlr_mock_state.last_callback_kind;
}

/*
=============
QLR_SteamworksMock_GetLastCallbackText
=============
*/
QLR_EXPORT const char *QLR_SteamworksMock_GetLastCallbackText( void ) {
	return qlr_mock_state.last_callback_text;
}

/*
=============
QLR_SteamworksMock_GetLastCallbackId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetLastCallbackId( void ) {
	return qlr_mock_state.last_callback_id;
}

/*
=============
QLR_SteamworksMock_GetLastCallbackAuxId
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetLastCallbackAuxId( void ) {
	return qlr_mock_state.last_callback_aux_id;
}

/*
=============
QLR_SteamworksMock_GetLastCallbackAppId
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetLastCallbackAppId( void ) {
	return qlr_mock_state.last_callback_app_id;
}

/*
=============
QLR_SteamworksMock_GetLastCallbackResult
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetLastCallbackResult( void ) {
	return qlr_mock_state.last_callback_result;
}

/*
=============
QLR_Steamworks_Request

Wrapper exposing QL_Steamworks_RequestAuthTicket for ctypes.
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_Request( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle ) {
	if ( !qlr_mock_state.library_available || !qlr_mock_state.init_result ) {
		if ( ticketBuffer && ticketBufferSize > 0 ) {
			ticketBuffer[0] = '\0';
		}

		if ( ticketLength ) {
			*ticketLength = 0;
		}

		if ( ticketHandle ) {
			*ticketHandle = 0;
		}

		return qfalse;
	}

	return QL_Steamworks_RequestAuthTicket( ticketBuffer, ticketBufferSize, ticketLength, ticketHandle );
}

/*
=============
QLR_Steamworks_HasWebApiAuthTicketAdapter
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_HasWebApiAuthTicketAdapter( void ) {
	if ( !qlr_mock_state.library_available || !qlr_mock_state.init_result ) {
		return qfalse;
	}

	return QL_Steamworks_HasWebApiAuthTicketAdapter();
}

/*
=============
QLR_Steamworks_RequestWebApi

Wrapper exposing QL_Steamworks_RequestWebApiAuthTicket for ctypes.
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_RequestWebApi( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle, int *steamResult ) {
	if ( !qlr_mock_state.library_available || !qlr_mock_state.init_result ) {
		if ( ticketBuffer && ticketBufferSize > 0 ) {
			ticketBuffer[0] = '\0';
		}

		if ( ticketLength ) {
			*ticketLength = 0;
		}

		if ( ticketHandle ) {
			*ticketHandle = 0;
		}

		if ( steamResult ) {
			*steamResult = 0;
		}

		return qfalse;
	}

	return QL_Steamworks_RequestWebApiAuthTicket( QL_Steamworks_GetWebApiAuthTicketIdentity(),
		ticketBuffer, ticketBufferSize, ticketLength, ticketHandle, steamResult );
}

/*
=============
QLR_Steamworks_IsUserLoggedOn
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_IsUserLoggedOn( void ) {
	return QL_Steamworks_IsUserLoggedOn();
}

/*
=============
QLR_Steamworks_CancelTicket

Wrapper exposing QL_Steamworks_CancelAuthTicket for ctypes.
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CancelTicket( uint32_t ticketHandle ) {
	if ( !qlr_mock_state.library_available || !qlr_mock_state.init_result ) {
		return qfalse;
	}

	return QL_Steamworks_CancelAuthTicket( ticketHandle );
}

/*
=============
QLR_SteamworksMock_GetCancelledTicketHandle
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetCancelledTicketHandle( void ) {
	return (uint32_t)qlr_mock_state.cancelled_ticket_handle;
}

/*
=============
QLR_SteamworksMock_GetCancelAuthTicketCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetCancelAuthTicketCalls( void ) {
	return qlr_mock_state.cancel_auth_ticket_calls;
}

/*
=============
QLR_Steamworks_LoadAvatar

Wrapper exposing QL_Steamworks_LoadAvatarRGBA for ctypes.
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_LoadAvatar( uint32_t idLow, uint32_t idHigh, int size, uint8_t *buffer, uint32_t bufferSize, uint32_t *outWidth, uint32_t *outHeight, uint32_t *outLength ) {
	uint8_t *pixels;
	uint32_t width;
	uint32_t height;
	size_t requiredLength;

	if ( outWidth ) {
		*outWidth = 0;
	}
	if ( outHeight ) {
		*outHeight = 0;
	}
	if ( outLength ) {
		*outLength = 0;
	}

	pixels = NULL;
	width = 0;
	height = 0;
	if ( !QL_Steamworks_LoadAvatarRGBA( idLow, idHigh, (ql_steam_avatar_size_t)size, &pixels, &width, &height ) || !pixels ) {
		return qfalse;
	}

	requiredLength = (size_t)width * (size_t)height * 4;
	if ( !buffer || requiredLength == 0 || requiredLength > bufferSize ) {
		QL_Steamworks_FreeBuffer( pixels );
		return qfalse;
	}

	memcpy( buffer, pixels, requiredLength );
	QL_Steamworks_FreeBuffer( pixels );

	if ( outWidth ) {
		*outWidth = width;
	}
	if ( outHeight ) {
		*outHeight = height;
	}
	if ( outLength ) {
		*outLength = (uint32_t)requiredLength;
	}

	return qtrue;
}

/*
=============
QLR_Steamworks_GetPersonaName
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetPersonaName( char *buffer, size_t bufferSize ) {
	return QL_Steamworks_GetPersonaName( buffer, bufferSize );
}

/*
=============
QLR_Steamworks_GetIPCountry
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetIPCountry( char *buffer, size_t bufferSize ) {
	return QL_Steamworks_GetIPCountry( buffer, bufferSize );
}

/*
=============
QLR_Steamworks_GetAppID
=============
*/
QLR_EXPORT uint32_t QLR_Steamworks_GetAppID( void ) {
	return QL_Steamworks_GetAppID();
}

/*
=============
QLR_Steamworks_GetUserSteamID
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetUserSteamID( uint32_t *outIdLow, uint32_t *outIdHigh ) {
	return QL_Steamworks_GetUserSteamID( outIdLow, outIdHigh );
}

/*
=============
QLR_Steamworks_GetFriendCount
=============
*/
QLR_EXPORT int QLR_Steamworks_GetFriendCount( int flags ) {
	return QL_Steamworks_GetFriendCount( flags );
}

/*
=============
QLR_Steamworks_GetFriendByIndex
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetFriendByIndex( int index, int flags, uint32_t *outIdLow, uint32_t *outIdHigh ) {
	return QL_Steamworks_GetFriendByIndex( index, flags, outIdLow, outIdHigh );
}

/*
=============
QLR_Steamworks_GetFriendSummary
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetFriendSummary( uint32_t idLow, uint32_t idHigh, ql_steam_friend_summary_t *outSummary ) {
	return QL_Steamworks_GetFriendSummary( idLow, idHigh, outSummary );
}

/*
=============
QLR_Steamworks_GetFriendPersonaName
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetFriendPersonaName( uint32_t idLow, uint32_t idHigh, char *buffer, size_t bufferSize ) {
	return QL_Steamworks_GetFriendPersonaName( idLow, idHigh, buffer, bufferSize );
}

/*
=============
QLR_Steamworks_SetRichPresence
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SetRichPresence( const char *key, const char *value ) {
	return QL_Steamworks_SetRichPresence( key, value );
}

/*
=============
QLR_Steamworks_SetInGameVoiceSpeaking
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SetInGameVoiceSpeaking( uint32_t idLow, uint32_t idHigh, qboolean speaking ) {
	return QL_Steamworks_SetInGameVoiceSpeaking( idLow, idHigh, speaking );
}

/*
=============
QLR_Steamworks_ActivateOverlay
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ActivateOverlay( const char *dialog, uint32_t idLow, uint32_t idHigh ) {
	return QL_Steamworks_ActivateOverlayToUser( dialog, idLow, idHigh );
}

/*
=============
QLR_Steamworks_ActivateOverlayToWebPage
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ActivateOverlayToWebPage( const char *url ) {
	return QL_Steamworks_ActivateOverlayToWebPage( url );
}

/*
=============
QLR_Steamworks_HasServerBrowserInterface
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_HasServerBrowserInterface( void ) {
	return QL_Steamworks_HasServerBrowserInterface();
}

/*
=============
QLR_Steamworks_GetServerBrowserRequestModeLabel
=============
*/
QLR_EXPORT const char *QLR_Steamworks_GetServerBrowserRequestModeLabel( int requestMode ) {
	return QL_Steamworks_GetServerBrowserRequestModeLabel( (ql_steam_server_browser_request_mode_t)requestMode );
}

/*
=============
QLR_Steamworks_ServerBrowserRequestModeUsesGamedirFilter
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerBrowserRequestModeUsesGamedirFilter( int requestMode ) {
	return QL_Steamworks_ServerBrowserRequestModeUsesGamedirFilter( (ql_steam_server_browser_request_mode_t)requestMode );
}

/*
=============
QLR_Steamworks_InitServerBrowserOwner
=============
*/
QLR_EXPORT void QLR_Steamworks_InitServerBrowserOwner( ql_steam_server_browser_owner_t *owner ) {
	QL_Steamworks_InitServerBrowserOwner( owner );
}

/*
=============
QLR_Steamworks_BeginServerBrowserOwnerRequest
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BeginServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner, int requestMode, uintptr_t responseObject ) {
	return QL_Steamworks_BeginServerBrowserOwnerRequest( owner, (ql_steam_server_browser_request_mode_t)requestMode, (void *)responseObject );
}

/*
=============
QLR_Steamworks_BeginServerBrowserOwnerRequestForApp
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BeginServerBrowserOwnerRequestForApp( ql_steam_server_browser_owner_t *owner, int requestMode, uint32_t appId, uintptr_t responseObject ) {
	return QL_Steamworks_BeginServerBrowserOwnerRequestForApp( owner, (ql_steam_server_browser_request_mode_t)requestMode, appId, (void *)responseObject );
}

/*
=============
QLR_Steamworks_RefreshServerBrowserOwnerRequest
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_RefreshServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner ) {
	return QL_Steamworks_RefreshServerBrowserOwnerRequest( owner );
}

/*
=============
QLR_Steamworks_CompleteServerBrowserOwnerRequest
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CompleteServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner ) {
	return QL_Steamworks_CompleteServerBrowserOwnerRequest( owner );
}

/*
=============
QLR_Steamworks_RequestServerList
=============
*/
QLR_EXPORT uintptr_t QLR_Steamworks_RequestServerList( int requestMode, uintptr_t responseObject ) {
	return (uintptr_t)QL_Steamworks_RequestServerList( (ql_steam_server_browser_request_mode_t)requestMode, (void *)responseObject );
}

/*
=============
QLR_Steamworks_RequestServerListForApp
=============
*/
QLR_EXPORT uintptr_t QLR_Steamworks_RequestServerListForApp( int requestMode, uint32_t appId, uintptr_t responseObject ) {
	return (uintptr_t)QL_Steamworks_RequestServerListForApp( (ql_steam_server_browser_request_mode_t)requestMode, appId, (void *)responseObject );
}

/*
=============
QLR_Steamworks_GetServerListDetails
=============
*/
QLR_EXPORT uintptr_t QLR_Steamworks_GetServerListDetails( uintptr_t request, int index ) {
	return (uintptr_t)QL_Steamworks_GetServerListDetails( (ql_steam_server_list_request_t)request, index );
}

/*
=============
QLR_Steamworks_ReadServerListDetails
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ReadServerListDetails( uintptr_t request, int index, ql_steam_server_item_t *outServer ) {
	return QL_Steamworks_ReadServerListDetails( (ql_steam_server_list_request_t)request, index, outServer );
}

/*
=============
QLR_Steamworks_ReadServerListDetailsForApp
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ReadServerListDetailsForApp( uintptr_t request, int index, uint32_t appId, ql_steam_server_item_t *outServer ) {
	return QL_Steamworks_ReadServerListDetailsForApp( (ql_steam_server_list_request_t)request, index, appId, outServer );
}

/*
=============
QLR_Steamworks_FormatServerBrowserResponseId
=============
*/
QLR_EXPORT void QLR_Steamworks_FormatServerBrowserResponseId( uint32_t serverIp, uint16_t serverPort, char *buffer, size_t bufferSize ) {
	QL_Steamworks_FormatServerBrowserResponseId( serverIp, serverPort, buffer, bufferSize );
}

/*
=============
QLR_Steamworks_BuildServerBrowserResponse
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserResponse( const ql_steam_server_item_t *server, ql_steam_server_browser_response_t *outResponse ) {
	return QL_Steamworks_BuildServerBrowserResponse( server, outResponse );
}

/*
=============
QLR_Steamworks_ReadServerBrowserResponse
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ReadServerBrowserResponse( uintptr_t request, int index, ql_steam_server_browser_response_t *outResponse ) {
	return QL_Steamworks_ReadServerBrowserResponse( (ql_steam_server_list_request_t)request, index, outResponse );
}

/*
=============
QLR_Steamworks_ReadServerBrowserResponseForApp
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ReadServerBrowserResponseForApp( uintptr_t request, int index, uint32_t appId, ql_steam_server_browser_response_t *outResponse ) {
	return QL_Steamworks_ReadServerBrowserResponseForApp( (ql_steam_server_list_request_t)request, index, appId, outResponse );
}

/*
=============
QLR_Steamworks_ReadServerBrowserPingResponse
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ReadServerBrowserPingResponse( ql_steam_server_browser_response_t *outResponse ) {
	return QL_Steamworks_ReadServerBrowserPingResponse( &qlr_mock_state.server_browser_details, outResponse );
}

/*
=============
QLR_Steamworks_ReadServerBrowserPingResponseForApp
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ReadServerBrowserPingResponseForApp( uint32_t appId, ql_steam_server_browser_response_t *outResponse ) {
	return QL_Steamworks_ReadServerBrowserPingResponseForApp( &qlr_mock_state.server_browser_details, appId, outResponse );
}

/*
=============
QLR_Steamworks_FormatServerBrowserFailureEventName
=============
*/
QLR_EXPORT void QLR_Steamworks_FormatServerBrowserFailureEventName( int serverIndex, char *buffer, size_t bufferSize ) {
	QL_Steamworks_FormatServerBrowserFailureEventName( serverIndex, buffer, bufferSize );
}

/*
=============
QLR_Steamworks_BuildServerBrowserFailure
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserFailure( int serverIndex, ql_steam_server_browser_failure_t *outFailure ) {
	return QL_Steamworks_BuildServerBrowserFailure( serverIndex, outFailure );
}

/*
=============
QLR_Steamworks_BuildServerBrowserRefreshComplete
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserRefreshComplete( ql_steam_server_browser_refresh_complete_t *outRefresh ) {
	return QL_Steamworks_BuildServerBrowserRefreshComplete( outRefresh );
}

/*
=============
QLR_Steamworks_FormatServerBrowserDetailId
=============
*/
QLR_EXPORT void QLR_Steamworks_FormatServerBrowserDetailId( uint32_t serverIp, uint16_t serverPort, char *buffer, size_t bufferSize ) {
	QL_Steamworks_FormatServerBrowserDetailId( serverIp, serverPort, buffer, bufferSize );
}

/*
=============
QLR_Steamworks_BuildServerBrowserDetailIdentity
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserDetailIdentity( uint32_t serverIp, uint16_t serverPort, ql_steam_server_browser_detail_identity_t *outIdentity ) {
	return QL_Steamworks_BuildServerBrowserDetailIdentity( serverIp, serverPort, outIdentity );
}

/*
=============
QLR_Steamworks_FormatServerBrowserDetailEventName
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_FormatServerBrowserDetailEventName( int channel, int phase, const char *detailId, char *buffer, size_t bufferSize ) {
	return QL_Steamworks_FormatServerBrowserDetailEventName( (ql_steam_server_browser_detail_channel_t)channel, (ql_steam_server_browser_detail_phase_t)phase, detailId, buffer, bufferSize );
}

/*
=============
QLR_Steamworks_BuildServerBrowserDetailEvent
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserDetailEvent( const ql_steam_server_browser_detail_identity_t *identity, int channel, int phase, ql_steam_server_browser_detail_event_t *outEvent ) {
	return QL_Steamworks_BuildServerBrowserDetailEvent( identity, (ql_steam_server_browser_detail_channel_t)channel, (ql_steam_server_browser_detail_phase_t)phase, outEvent );
}

/*
=============
QLR_Steamworks_BuildServerBrowserRuleResponse
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserRuleResponse( const ql_steam_server_browser_detail_identity_t *identity, const char *rule, const char *value, ql_steam_server_browser_rule_response_t *outResponse ) {
	return QL_Steamworks_BuildServerBrowserRuleResponse( identity, rule, value, outResponse );
}

/*
=============
QLR_Steamworks_BuildServerBrowserPlayerResponse
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserPlayerResponse( const ql_steam_server_browser_detail_identity_t *identity, const char *name, int score, int time, ql_steam_server_browser_player_response_t *outResponse ) {
	return QL_Steamworks_BuildServerBrowserPlayerResponse( identity, name, score, time, outResponse );
}

/*
=============
QLR_Steamworks_InitServerBrowserDetailLifecycle
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_InitServerBrowserDetailLifecycle( uint32_t serverIp, uint16_t serverPort, ql_steam_server_browser_detail_lifecycle_t *outLifecycle ) {
	return QL_Steamworks_InitServerBrowserDetailLifecycle( serverIp, serverPort, outLifecycle );
}

/*
=============
QLR_Steamworks_CompleteServerBrowserDetailCallback
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CompleteServerBrowserDetailCallback( ql_steam_server_browser_detail_lifecycle_t *lifecycle, qboolean *outReleaseReady ) {
	return QL_Steamworks_CompleteServerBrowserDetailCallback( lifecycle, outReleaseReady );
}

/*
=============
QLR_Steamworks_CompleteServerBrowserDetailTerminal
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CompleteServerBrowserDetailTerminal( ql_steam_server_browser_detail_lifecycle_t *lifecycle, uint32_t terminalChannel, qboolean *outReleaseReady ) {
	return QL_Steamworks_CompleteServerBrowserDetailTerminal( lifecycle, terminalChannel, outReleaseReady );
}

/*
=============
QLR_Steamworks_BuildServerBrowserDetailResponseViews
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserDetailResponseViews( uintptr_t detailObjectBase, ql_steam_server_browser_detail_response_views_t *outViews ) {
	return QL_Steamworks_BuildServerBrowserDetailResponseViews( (void *)detailObjectBase, outViews );
}

/*
=============
QLR_Steamworks_InitServerBrowserDetailRequest
=============
*/
QLR_EXPORT void QLR_Steamworks_InitServerBrowserDetailRequest( ql_steam_server_browser_detail_request_t *request ) {
	QL_Steamworks_InitServerBrowserDetailRequest( request );
}

/*
=============
QLR_Steamworks_BeginServerBrowserDetailRequest
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BeginServerBrowserDetailRequest( ql_steam_server_browser_detail_request_t *request, uint32_t serverIp, uint16_t serverPort, uintptr_t detailObjectBase ) {
	return QL_Steamworks_BeginServerBrowserDetailRequest( request, serverIp, serverPort, (void *)detailObjectBase );
}

/*
=============
QLR_Steamworks_CompleteServerBrowserDetailRequestCallback
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CompleteServerBrowserDetailRequestCallback( ql_steam_server_browser_detail_request_t *request, qboolean *outReleaseReady ) {
	return QL_Steamworks_CompleteServerBrowserDetailRequestCallback( request, outReleaseReady );
}

/*
=============
QLR_Steamworks_CompleteServerBrowserDetailRequestTerminal
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CompleteServerBrowserDetailRequestTerminal( ql_steam_server_browser_detail_request_t *request, uint32_t terminalChannel, qboolean *outReleaseReady ) {
	return QL_Steamworks_CompleteServerBrowserDetailRequestTerminal( request, terminalChannel, outReleaseReady );
}

/*
=============
QLR_Steamworks_ReleaseServerListRequest
=============
*/
QLR_EXPORT void QLR_Steamworks_ReleaseServerListRequest( uintptr_t request ) {
	QL_Steamworks_ReleaseServerListRequest( (ql_steam_server_list_request_t)request );
}

/*
=============
QLR_Steamworks_RefreshServerListRequest
=============
*/
QLR_EXPORT void QLR_Steamworks_RefreshServerListRequest( uintptr_t request ) {
	QL_Steamworks_RefreshServerListRequest( (ql_steam_server_list_request_t)request );
}

/*
=============
QLR_Steamworks_RequestServerDetails
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_RequestServerDetails( uint32_t serverIp, uint16_t serverPort, uintptr_t pingResponse, uintptr_t playersResponse, uintptr_t rulesResponse, int *outPingQuery, int *outPlayersQuery, int *outRulesQuery ) {
	ql_steam_server_query_t pingQuery;
	ql_steam_server_query_t playersQuery;
	ql_steam_server_query_t rulesQuery;
	qboolean result;

	pingQuery = 0;
	playersQuery = 0;
	rulesQuery = 0;
	result = QL_Steamworks_RequestServerDetails(
		serverIp,
		serverPort,
		(void *)pingResponse,
		(void *)playersResponse,
		(void *)rulesResponse,
		&pingQuery,
		&playersQuery,
		&rulesQuery
	);
	if ( outPingQuery ) {
		*outPingQuery = pingQuery;
	}
	if ( outPlayersQuery ) {
		*outPlayersQuery = playersQuery;
	}
	if ( outRulesQuery ) {
		*outRulesQuery = rulesQuery;
	}

	return result;
}

/*
=============
QLR_Steamworks_CancelServerQuery
=============
*/
QLR_EXPORT void QLR_Steamworks_CancelServerQuery( int query ) {
	QL_Steamworks_CancelServerQuery( (ql_steam_server_query_t)query );
}

/*
=============
QLR_Steamworks_CreateLobby
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CreateLobby( int maxMembers ) {
	return QL_Steamworks_CreateLobby( maxMembers );
}

/*
=============
QLR_Steamworks_SetFavoriteServer
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SetFavoriteServer( uint32_t serverIp, uint16_t serverPort, qboolean add ) {
	return QL_Steamworks_SetFavoriteServer( serverIp, serverPort, add );
}

/*
=============
QLR_Steamworks_SetFavoriteServerForApp
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SetFavoriteServerForApp( uint32_t serverIp, uint16_t serverPort, uint32_t appId, qboolean add ) {
	return QL_Steamworks_SetFavoriteServerForApp( serverIp, serverPort, appId, add );
}

/*
=============
QLR_Steamworks_LeaveLobby
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_LeaveLobby( uint32_t idLow, uint32_t idHigh ) {
	return QL_Steamworks_LeaveLobby( idLow, idHigh );
}

/*
=============
QLR_Steamworks_JoinLobby
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_JoinLobby( uint32_t idLow, uint32_t idHigh ) {
	return QL_Steamworks_JoinLobby( idLow, idHigh );
}

/*
=============
QLR_Steamworks_SetLobbyServer
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SetLobbyServer( uint32_t idLow, uint32_t idHigh, uint32_t serverIp, uint16_t serverPort ) {
	return QL_Steamworks_SetLobbyServer( idLow, idHigh, serverIp, serverPort );
}

/*
=============
QLR_Steamworks_ShowInviteOverlay
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ShowInviteOverlay( uint32_t idLow, uint32_t idHigh ) {
	return QL_Steamworks_ShowInviteOverlay( idLow, idHigh );
}

/*
=============
QLR_Steamworks_InviteUserToLobby
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_InviteUserToLobby( uint32_t lobbyIdLow, uint32_t lobbyIdHigh, uint32_t userIdLow, uint32_t userIdHigh ) {
	return QL_Steamworks_InviteUserToLobby( lobbyIdLow, lobbyIdHigh, userIdLow, userIdHigh );
}

/*
=============
QLR_Steamworks_InviteUserToGame
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_InviteUserToGame( uint32_t idLow, uint32_t idHigh, const char *connectString ) {
	return QL_Steamworks_InviteUserToGame( idLow, idHigh, connectString );
}

/*
=============
QLR_Steamworks_SayLobby
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SayLobby( uint32_t idLow, uint32_t idHigh, const char *message ) {
	return QL_Steamworks_SayLobby( idLow, idHigh, message );
}

/*
=============
QLR_Steamworks_ClearStats
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ClearStats( qboolean achievementsToo ) {
	return QL_Steamworks_ClearStats( achievementsToo );
}

/*
=============
QLR_Steamworks_RequestUserStats
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_RequestUserStats( uint32_t idLow, uint32_t idHigh ) {
	return QL_Steamworks_RequestUserStats( idLow, idHigh );
}

/*
=============
QLR_Steamworks_GetUserStatInt
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetUserStatInt( uint32_t idLow, uint32_t idHigh, const char *name, int *outValue ) {
	return QL_Steamworks_GetUserStatInt( idLow, idHigh, name, outValue );
}

/*
=============
QLR_Steamworks_GetUserStatFloat
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetUserStatFloat( uint32_t idLow, uint32_t idHigh, const char *name, float *outValue ) {
	return QL_Steamworks_GetUserStatFloat( idLow, idHigh, name, outValue );
}

/*
=============
QLR_Steamworks_GetUserAchievement
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetUserAchievement( uint32_t idLow, uint32_t idHigh, const char *name, qboolean *outAchieved, int *outUnlockTime ) {
	return QL_Steamworks_GetUserAchievement( idLow, idHigh, name, outAchieved, outUnlockTime );
}

/*
=============
QLR_Steamworks_GetAchievementDisplayAttribute
=============
*/
QLR_EXPORT const char *QLR_Steamworks_GetAchievementDisplayAttribute( const char *name, const char *key ) {
	return QL_Steamworks_GetAchievementDisplayAttribute( name, key );
}

/*
=============
QLR_Steamworks_IsSubscribedApp
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_IsSubscribedApp( uint32_t appId ) {
	return QL_Steamworks_IsSubscribedApp( appId );
}

/*
=============
QLR_Steamworks_GetNumSubscribedItems
=============
*/
QLR_EXPORT uint32_t QLR_Steamworks_GetNumSubscribedItems( void ) {
	return QL_Steamworks_GetNumSubscribedItems();
}

/*
=============
QLR_Steamworks_GetSubscribedItems
=============
*/
QLR_EXPORT uint32_t QLR_Steamworks_GetSubscribedItems( uint64_t *outItemIds, uint32_t maxItems ) {
	return QL_Steamworks_GetSubscribedItems( outItemIds, maxItems );
}

/*
=============
QLR_Steamworks_GetItemInstallInfo
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetItemInstallInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outSizeOnDisk, char *folder, uint32_t folderSize, uint32_t *outTimestamp ) {
	return QL_Steamworks_GetItemInstallInfo( idLow, idHigh, outSizeOnDisk, folder, (size_t)folderSize, outTimestamp );
}

/*
=============
QLR_Steamworks_SubscribeItem
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SubscribeItem( uint32_t idLow, uint32_t idHigh ) {
	return QL_Steamworks_SubscribeItem( idLow, idHigh );
}

/*
=============
QLR_Steamworks_UnsubscribeItem
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_UnsubscribeItem( uint32_t idLow, uint32_t idHigh ) {
	return QL_Steamworks_UnsubscribeItem( idLow, idHigh );
}

/*
=============
QLR_Steamworks_DownloadItem
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_DownloadItem( uint32_t idLow, uint32_t idHigh, int highPriority ) {
	return QL_Steamworks_DownloadItem( idLow, idHigh, highPriority ? qtrue : qfalse );
}

/*
=============
QLR_Steamworks_Init
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_Init( void ) {
	return QL_Steamworks_Init();
}

/*
=============
QLR_Steamworks_ServerInitWithVersion
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerInitWithVersion( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated, const char *version ) {
	return QL_Steamworks_ServerInitWithVersion( ip, gamePort, secure, dedicated, version );
}

/*
=============
QLR_Steamworks_ServerInit
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerInit( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated ) {
	return QL_Steamworks_ServerInit( ip, gamePort, secure, dedicated );
}

/*
=============
QLR_Steamworks_ServerShutdown
=============
*/
QLR_EXPORT void QLR_Steamworks_ServerShutdown( void ) {
	QL_Steamworks_ServerShutdown();
}

/*
=============
QLR_Steamworks_ServerIsInitialised
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerIsInitialised( void ) {
	return QL_Steamworks_ServerIsInitialised();
}

/*
=============
QLR_Steamworks_ServerIsLoggedOn
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerIsLoggedOn( void ) {
	return QL_Steamworks_ServerIsLoggedOn();
}

/*
=============
QLR_Steamworks_ServerGetAppID
=============
*/
QLR_EXPORT uint32_t QLR_Steamworks_ServerGetAppID( void ) {
	return QL_Steamworks_ServerGetAppID();
}

/*
=============
QLR_Steamworks_ServerRequestUserStats
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerRequestUserStats( uint64_t steamIdValue ) {
	CSteamID steamId;

	steamId.value = steamIdValue;
	return QL_Steamworks_ServerRequestUserStats( &steamId );
}

/*
=============
QLR_Steamworks_ServerGetUserStatInt
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerGetUserStatInt( uint64_t steamIdValue, const char *name, int *outValue ) {
	CSteamID steamId;

	steamId.value = steamIdValue;
	return QL_Steamworks_ServerGetUserStatInt( &steamId, name, outValue );
}

/*
=============
QLR_Steamworks_ServerGetUserStatFloat
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerGetUserStatFloat( uint64_t steamIdValue, const char *name, float *outValue ) {
	CSteamID steamId;

	steamId.value = steamIdValue;
	return QL_Steamworks_ServerGetUserStatFloat( &steamId, name, outValue );
}

/*
=============
QLR_Steamworks_ServerGetUserAchievement
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerGetUserAchievement( uint64_t steamIdValue, const char *name, qboolean *outAchieved ) {
	CSteamID steamId;

	steamId.value = steamIdValue;
	return QL_Steamworks_ServerGetUserAchievement( &steamId, name, outAchieved );
}

/*
=============
QLR_Steamworks_ServerSetUserStatInt
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetUserStatInt( uint64_t steamIdValue, const char *name, int value ) {
	CSteamID steamId;

	steamId.value = steamIdValue;
	return QL_Steamworks_ServerSetUserStatInt( &steamId, name, value );
}

/*
=============
QLR_Steamworks_ServerSetUserStatFloat
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetUserStatFloat( uint64_t steamIdValue, const char *name, float value ) {
	CSteamID steamId;

	steamId.value = steamIdValue;
	return QL_Steamworks_ServerSetUserStatFloat( &steamId, name, value );
}

/*
=============
QLR_Steamworks_ServerUpdateAvgRateStat
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerUpdateAvgRateStat( uint64_t steamIdValue, const char *name, float countThisSession, double sessionLength ) {
	CSteamID steamId;

	steamId.value = steamIdValue;
	return QL_Steamworks_ServerUpdateAvgRateStat( &steamId, name, countThisSession, sessionLength );
}

/*
=============
QLR_Steamworks_ServerSetUserAchievement
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetUserAchievement( uint64_t steamIdValue, const char *name ) {
	CSteamID steamId;

	steamId.value = steamIdValue;
	return QL_Steamworks_ServerSetUserAchievement( &steamId, name );
}

/*
=============
QLR_Steamworks_ServerStoreUserStats
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerStoreUserStats( uint64_t steamIdValue ) {
	CSteamID steamId;

	steamId.value = steamIdValue;
	return QL_Steamworks_ServerStoreUserStats( &steamId );
}

/*
=============
QLR_Steamworks_ServerEnableHeartbeats
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerEnableHeartbeats( qboolean enable ) {
	return QL_Steamworks_ServerEnableHeartbeats( enable );
}

/*
=============
QLR_Steamworks_ServerSetDedicated
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetDedicated( qboolean dedicated ) {
	return QL_Steamworks_ServerSetDedicated( dedicated );
}

/*
=============
QLR_Steamworks_ServerLogOn
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerLogOn( const char *account ) {
	return QL_Steamworks_ServerLogOn( account );
}

/*
=============
QLR_Steamworks_ServerSetProduct
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetProduct( const char *product ) {
	return QL_Steamworks_ServerSetProduct( product );
}

/*
=============
QLR_Steamworks_ServerSetGameDir
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetGameDir( const char *gameDir ) {
	return QL_Steamworks_ServerSetGameDir( gameDir );
}

/*
=============
QLR_Steamworks_ServerSetGameDescription
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetGameDescription( const char *description ) {
	return QL_Steamworks_ServerSetGameDescription( description );
}

/*
=============
QLR_Steamworks_ServerSetMaxPlayerCount
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetMaxPlayerCount( int maxPlayers ) {
	return QL_Steamworks_ServerSetMaxPlayerCount( maxPlayers );
}

/*
=============
QLR_Steamworks_ServerSetBotPlayerCount
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetBotPlayerCount( int botPlayers ) {
	return QL_Steamworks_ServerSetBotPlayerCount( botPlayers );
}

/*
=============
QLR_Steamworks_ServerSetServerName
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetServerName( const char *name ) {
	return QL_Steamworks_ServerSetServerName( name );
}

/*
=============
QLR_Steamworks_ServerSetMapName
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetMapName( const char *mapName ) {
	return QL_Steamworks_ServerSetMapName( mapName );
}

/*
=============
QLR_Steamworks_ServerSetPasswordProtected
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetPasswordProtected( qboolean passwordProtected ) {
	return QL_Steamworks_ServerSetPasswordProtected( passwordProtected );
}

/*
=============
QLR_Steamworks_ServerGetSteamID
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerGetSteamID( uint32_t *outIdLow, uint32_t *outIdHigh ) {
	return QL_Steamworks_ServerGetSteamID( outIdLow, outIdHigh );
}

/*
=============
QLR_Steamworks_ServerCreateUnauthenticatedUserConnection
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerCreateUnauthenticatedUserConnection( uint32_t *outIdLow, uint32_t *outIdHigh ) {
	return QL_Steamworks_ServerCreateUnauthenticatedUserConnection( outIdLow, outIdHigh );
}

/*
=============
QLR_Steamworks_ServerSetGameTags
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetGameTags( const char *tags ) {
	return QL_Steamworks_ServerSetGameTags( tags );
}

/*
=============
QLR_Steamworks_ServerSetKeyValue
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetKeyValue( const char *key, const char *value ) {
	return QL_Steamworks_ServerSetKeyValue( key, value );
}

/*
=============
QLR_Steamworks_ServerSetKeyValuesFromInfoString
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetKeyValuesFromInfoString( const char *infoString ) {
	return QL_Steamworks_ServerSetKeyValuesFromInfoString( infoString );
}

/*
=============
QLR_Steamworks_ServerUpdateUserData
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerUpdateUserData( uint32_t idLow, uint32_t idHigh, const char *playerName, uint32_t score ) {
	CSteamID steamId;

	steamId.value = ((uint64_t)idHigh << 32) | (uint64_t)idLow;
	return QL_Steamworks_ServerUpdateUserData( &steamId, playerName, score );
}

/*
=============
QLR_Steamworks_ServerGetPublicIP
=============
*/
QLR_EXPORT uint32_t QLR_Steamworks_ServerGetPublicIP( void ) {
	return QL_Steamworks_ServerGetPublicIP();
}

/*
=============
QLR_Steamworks_SendP2PPacket
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SendP2PPacket( uint64_t steamIdValue, const uint8_t *data, uint32_t length, int sendType, int channel ) {
	CSteamID steamId;

	steamId.value = steamIdValue;
	return QL_Steamworks_SendP2PPacket( &steamId, data, length, sendType, channel );
}

/*
=============
QLR_Steamworks_IsP2PPacketAvailable
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_IsP2PPacketAvailable( uint32_t *outSize, int channel ) {
	return QL_Steamworks_IsP2PPacketAvailable( outSize, channel );
}

/*
=============
QLR_Steamworks_ReadP2PPacket
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ReadP2PPacket( uint8_t *data, uint32_t dataSize, uint32_t *outSize, uint64_t *outSteamIdValue, int channel ) {
	CSteamID steamId;
	qboolean result;

	if ( outSteamIdValue ) {
		*outSteamIdValue = 0ull;
	}

	steamId.value = 0ull;
	result = QL_Steamworks_ReadP2PPacket( data, dataSize, outSize, &steamId, channel );
	if ( result && outSteamIdValue ) {
		*outSteamIdValue = steamId.value;
	}
	return result;
}

/*
=============
QLR_Steamworks_AcceptP2PSession
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_AcceptP2PSession( uint64_t steamIdValue ) {
	CSteamID steamId;

	steamId.value = steamIdValue;
	return QL_Steamworks_AcceptP2PSession( &steamId );
}

/*
=============
QLR_Steamworks_ServerSendP2PPacket
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSendP2PPacket( uint64_t steamIdValue, const uint8_t *data, uint32_t length, int sendType, int channel ) {
	CSteamID steamId;

	steamId.value = steamIdValue;
	return QL_Steamworks_ServerSendP2PPacket( &steamId, data, length, sendType, channel );
}

/*
=============
QLR_Steamworks_ServerIsP2PPacketAvailable
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerIsP2PPacketAvailable( uint32_t *outSize, int channel ) {
	return QL_Steamworks_ServerIsP2PPacketAvailable( outSize, channel );
}

/*
=============
QLR_Steamworks_ServerReadP2PPacket
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerReadP2PPacket( uint8_t *data, uint32_t dataSize, uint32_t *outSize, uint64_t *outSteamIdValue, int channel ) {
	CSteamID steamId;
	qboolean result;

	if ( outSteamIdValue ) {
		*outSteamIdValue = 0ull;
	}

	steamId.value = 0ull;
	result = QL_Steamworks_ServerReadP2PPacket( data, dataSize, outSize, &steamId, channel );
	if ( result && outSteamIdValue ) {
		*outSteamIdValue = steamId.value;
	}
	return result;
}

/*
=============
QLR_Steamworks_ServerHandleIncomingPacket
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerHandleIncomingPacket( const uint8_t *data, int dataSize, uint32_t ip, uint16_t port ) {
	return QL_Steamworks_ServerHandleIncomingPacket( data, dataSize, ip, port );
}

/*
=============
QLR_Steamworks_ServerGetNextOutgoingPacket
=============
*/
QLR_EXPORT int QLR_Steamworks_ServerGetNextOutgoingPacket( uint8_t *data, int dataSize, uint32_t *outIp, uint16_t *outPort ) {
	return QL_Steamworks_ServerGetNextOutgoingPacket( data, dataSize, outIp, outPort );
}

/*
=============
QLR_Steamworks_ServerAcceptP2PSession
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerAcceptP2PSession( uint64_t steamIdValue ) {
	CSteamID steamId;

	steamId.value = steamIdValue;
	return QL_Steamworks_ServerAcceptP2PSession( &steamId );
}

/*
=============
QLR_Steamworks_StartVoiceRecording
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_StartVoiceRecording( void ) {
	return QL_Steamworks_StartVoiceRecording();
}

/*
=============
QLR_Steamworks_StopVoiceRecording
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_StopVoiceRecording( void ) {
	return QL_Steamworks_StopVoiceRecording();
}

/*
=============
QLR_Steamworks_GetCompressedVoice
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetCompressedVoice( uint8_t *data, uint32_t dataSize, uint32_t *outSize ) {
	return QL_Steamworks_GetCompressedVoice( data, dataSize, outSize );
}

/*
=============
QLR_Steamworks_DecompressVoice
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_DecompressVoice( const uint8_t *compressedData, uint32_t compressedSize, uint8_t *data, uint32_t dataSize, uint32_t *outSize, uint32_t sampleRate ) {
	return QL_Steamworks_DecompressVoice( compressedData, compressedSize, data, dataSize, outSize, sampleRate );
}

/*
=============
QLR_Steamworks_GetVoiceOptimalSampleRate
=============
*/
QLR_EXPORT uint32_t QLR_Steamworks_GetVoiceOptimalSampleRate( void ) {
	return QL_Steamworks_GetVoiceOptimalSampleRate();
}

/*
=============
QLR_Steamworks_Shutdown
=============
*/
QLR_EXPORT void QLR_Steamworks_Shutdown( void ) {
	QL_Steamworks_Shutdown();
}

/*
=============
QLR_Steamworks_Validate

Wrapper exposing QL_Steamworks_ValidateTicket for ctypes.
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_Validate( const char *ticketHex, ql_auth_response_t *response ) {
	if ( !qlr_mock_state.library_available || !qlr_mock_state.init_result ) {
		QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, "Steam runtime unavailable" );
		return qtrue;
	}

	return QL_Steamworks_ValidateTicket( ticketHex, response );
}

#else

#include <stddef.h>

/*
=============
QLR_Steamworks_Request
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_Request( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle ) {
	(void)ticketBuffer;
	(void)ticketBufferSize;
	(void)ticketLength;
	(void)ticketHandle;
	return QL_Steamworks_RequestAuthTicket( ticketBuffer, ticketBufferSize, ticketLength, ticketHandle );
}

/*
=============
QLR_Steamworks_HasWebApiAuthTicketAdapter
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_HasWebApiAuthTicketAdapter( void ) {
	return qfalse;
}

/*
=============
QLR_Steamworks_RequestWebApi
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_RequestWebApi( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle, int *steamResult ) {
	return QL_Steamworks_RequestWebApiAuthTicket( QL_Steamworks_GetWebApiAuthTicketIdentity(),
		ticketBuffer, ticketBufferSize, ticketLength, ticketHandle, steamResult );
}

/*
=============
QLR_Steamworks_CancelTicket
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CancelTicket( uint32_t ticketHandle ) {
	return QL_Steamworks_CancelAuthTicket( ticketHandle );
}

/*
=============
QLR_SteamworksMock_GetCancelledTicketHandle
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetCancelledTicketHandle( void ) {
	return 0;
}

/*
=============
QLR_SteamworksMock_GetCancelAuthTicketCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetCancelAuthTicketCalls( void ) {
	return 0;
}

/*
=============
QLR_Steamworks_Validate
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_Validate( const char *ticketHex, ql_auth_response_t *response ) {
	return QL_Steamworks_ValidateTicket( ticketHex, response );
}

/*
=============
QLR_Steamworks_IsUserLoggedOn
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_IsUserLoggedOn( void ) {
	return qfalse;
}

/*
=============
QLR_Steamworks_LoadAvatar
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_LoadAvatar( uint32_t idLow, uint32_t idHigh, int size, uint8_t *buffer, uint32_t bufferSize, uint32_t *outWidth, uint32_t *outHeight, uint32_t *outLength ) {
	(void)idLow;
	(void)idHigh;
	(void)size;
	(void)buffer;
	(void)bufferSize;
	if ( outWidth ) {
		*outWidth = 0;
	}
	if ( outHeight ) {
		*outHeight = 0;
	}
	if ( outLength ) {
		*outLength = 0;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_GetPersonaName
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetPersonaName( char *buffer, size_t bufferSize ) {
	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_GetIPCountry
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetIPCountry( char *buffer, size_t bufferSize ) {
	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_GetAppID
=============
*/
QLR_EXPORT uint32_t QLR_Steamworks_GetAppID( void ) {
	return 0u;
}

/*
=============
QLR_Steamworks_GetUserSteamID
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetUserSteamID( uint32_t *outIdLow, uint32_t *outIdHigh ) {
	if ( outIdLow ) {
		*outIdLow = 0u;
	}
	if ( outIdHigh ) {
		*outIdHigh = 0u;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_GetFriendCount
=============
*/
QLR_EXPORT int QLR_Steamworks_GetFriendCount( int flags ) {
	(void)flags;
	return 0;
}

/*
=============
QLR_Steamworks_GetFriendByIndex
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetFriendByIndex( int index, int flags, uint32_t *outIdLow, uint32_t *outIdHigh ) {
	(void)index;
	(void)flags;

	if ( outIdLow ) {
		*outIdLow = 0u;
	}
	if ( outIdHigh ) {
		*outIdHigh = 0u;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_GetFriendSummary
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetFriendSummary( uint32_t idLow, uint32_t idHigh, ql_steam_friend_summary_t *outSummary ) {
	(void)idLow;
	(void)idHigh;

	if ( outSummary ) {
		memset( outSummary, 0, sizeof( *outSummary ) );
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_GetFriendPersonaName
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetFriendPersonaName( uint32_t idLow, uint32_t idHigh, char *buffer, size_t bufferSize ) {
	(void)idLow;
	(void)idHigh;

	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_SetRichPresence
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SetRichPresence( const char *key, const char *value ) {
	(void)key;
	(void)value;
	return qfalse;
}

/*
=============
QLR_Steamworks_SetInGameVoiceSpeaking
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SetInGameVoiceSpeaking( uint32_t idLow, uint32_t idHigh, qboolean speaking ) {
	(void)idLow;
	(void)idHigh;
	(void)speaking;
	return qfalse;
}

/*
=============
QLR_Steamworks_ActivateOverlay
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ActivateOverlay( const char *dialog, uint32_t idLow, uint32_t idHigh ) {
	(void)dialog;
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QLR_Steamworks_ActivateOverlayToWebPage
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ActivateOverlayToWebPage( const char *url ) {
	(void)url;
	return qfalse;
}

/*
=============
QLR_Steamworks_HasServerBrowserInterface
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_HasServerBrowserInterface( void ) {
	return QL_Steamworks_HasServerBrowserInterface();
}

/*
=============
QLR_Steamworks_GetServerBrowserRequestModeLabel
=============
*/
QLR_EXPORT const char *QLR_Steamworks_GetServerBrowserRequestModeLabel( int requestMode ) {
	return QL_Steamworks_GetServerBrowserRequestModeLabel( (ql_steam_server_browser_request_mode_t)requestMode );
}

/*
=============
QLR_Steamworks_ServerBrowserRequestModeUsesGamedirFilter
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerBrowserRequestModeUsesGamedirFilter( int requestMode ) {
	return QL_Steamworks_ServerBrowserRequestModeUsesGamedirFilter( (ql_steam_server_browser_request_mode_t)requestMode );
}

/*
=============
QLR_Steamworks_InitServerBrowserOwner
=============
*/
QLR_EXPORT void QLR_Steamworks_InitServerBrowserOwner( ql_steam_server_browser_owner_t *owner ) {
	QL_Steamworks_InitServerBrowserOwner( owner );
}

/*
=============
QLR_Steamworks_BeginServerBrowserOwnerRequest
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BeginServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner, int requestMode, uintptr_t responseObject ) {
	return QL_Steamworks_BeginServerBrowserOwnerRequest( owner, (ql_steam_server_browser_request_mode_t)requestMode, (void *)responseObject );
}

/*
=============
QLR_Steamworks_BeginServerBrowserOwnerRequestForApp
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BeginServerBrowserOwnerRequestForApp( ql_steam_server_browser_owner_t *owner, int requestMode, uint32_t appId, uintptr_t responseObject ) {
	return QL_Steamworks_BeginServerBrowserOwnerRequestForApp( owner, (ql_steam_server_browser_request_mode_t)requestMode, appId, (void *)responseObject );
}

/*
=============
QLR_Steamworks_RefreshServerBrowserOwnerRequest
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_RefreshServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner ) {
	return QL_Steamworks_RefreshServerBrowserOwnerRequest( owner );
}

/*
=============
QLR_Steamworks_CompleteServerBrowserOwnerRequest
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CompleteServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner ) {
	return QL_Steamworks_CompleteServerBrowserOwnerRequest( owner );
}

/*
=============
QLR_Steamworks_RequestServerList
=============
*/
QLR_EXPORT uintptr_t QLR_Steamworks_RequestServerList( int requestMode, uintptr_t responseObject ) {
	return (uintptr_t)QL_Steamworks_RequestServerList( (ql_steam_server_browser_request_mode_t)requestMode, (void *)responseObject );
}

/*
=============
QLR_Steamworks_RequestServerListForApp
=============
*/
QLR_EXPORT uintptr_t QLR_Steamworks_RequestServerListForApp( int requestMode, uint32_t appId, uintptr_t responseObject ) {
	return (uintptr_t)QL_Steamworks_RequestServerListForApp( (ql_steam_server_browser_request_mode_t)requestMode, appId, (void *)responseObject );
}

/*
=============
QLR_Steamworks_GetServerListDetails
=============
*/
QLR_EXPORT uintptr_t QLR_Steamworks_GetServerListDetails( uintptr_t request, int index ) {
	return (uintptr_t)QL_Steamworks_GetServerListDetails( (ql_steam_server_list_request_t)request, index );
}

/*
=============
QLR_Steamworks_ReadServerListDetails
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ReadServerListDetails( uintptr_t request, int index, ql_steam_server_item_t *outServer ) {
	return QL_Steamworks_ReadServerListDetails( (ql_steam_server_list_request_t)request, index, outServer );
}

/*
=============
QLR_Steamworks_ReadServerListDetailsForApp
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ReadServerListDetailsForApp( uintptr_t request, int index, uint32_t appId, ql_steam_server_item_t *outServer ) {
	return QL_Steamworks_ReadServerListDetailsForApp( (ql_steam_server_list_request_t)request, index, appId, outServer );
}

/*
=============
QLR_Steamworks_FormatServerBrowserResponseId
=============
*/
QLR_EXPORT void QLR_Steamworks_FormatServerBrowserResponseId( uint32_t serverIp, uint16_t serverPort, char *buffer, size_t bufferSize ) {
	QL_Steamworks_FormatServerBrowserResponseId( serverIp, serverPort, buffer, bufferSize );
}

/*
=============
QLR_Steamworks_BuildServerBrowserResponse
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserResponse( const ql_steam_server_item_t *server, ql_steam_server_browser_response_t *outResponse ) {
	return QL_Steamworks_BuildServerBrowserResponse( server, outResponse );
}

/*
=============
QLR_Steamworks_ReadServerBrowserResponse
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ReadServerBrowserResponse( uintptr_t request, int index, ql_steam_server_browser_response_t *outResponse ) {
	return QL_Steamworks_ReadServerBrowserResponse( (ql_steam_server_list_request_t)request, index, outResponse );
}

/*
=============
QLR_Steamworks_ReadServerBrowserResponseForApp
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ReadServerBrowserResponseForApp( uintptr_t request, int index, uint32_t appId, ql_steam_server_browser_response_t *outResponse ) {
	return QL_Steamworks_ReadServerBrowserResponseForApp( (ql_steam_server_list_request_t)request, index, appId, outResponse );
}

/*
=============
QLR_Steamworks_ReadServerBrowserPingResponse
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ReadServerBrowserPingResponse( ql_steam_server_browser_response_t *outResponse ) {
	return QL_Steamworks_ReadServerBrowserPingResponse( NULL, outResponse );
}

/*
=============
QLR_Steamworks_ReadServerBrowserPingResponseForApp
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ReadServerBrowserPingResponseForApp( uint32_t appId, ql_steam_server_browser_response_t *outResponse ) {
	(void)appId;
	return QL_Steamworks_ReadServerBrowserPingResponseForApp( NULL, appId, outResponse );
}

/*
=============
QLR_Steamworks_FormatServerBrowserFailureEventName
=============
*/
QLR_EXPORT void QLR_Steamworks_FormatServerBrowserFailureEventName( int serverIndex, char *buffer, size_t bufferSize ) {
	QL_Steamworks_FormatServerBrowserFailureEventName( serverIndex, buffer, bufferSize );
}

/*
=============
QLR_Steamworks_BuildServerBrowserFailure
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserFailure( int serverIndex, ql_steam_server_browser_failure_t *outFailure ) {
	return QL_Steamworks_BuildServerBrowserFailure( serverIndex, outFailure );
}

/*
=============
QLR_Steamworks_BuildServerBrowserRefreshComplete
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserRefreshComplete( ql_steam_server_browser_refresh_complete_t *outRefresh ) {
	return QL_Steamworks_BuildServerBrowserRefreshComplete( outRefresh );
}

/*
=============
QLR_Steamworks_FormatServerBrowserDetailId
=============
*/
QLR_EXPORT void QLR_Steamworks_FormatServerBrowserDetailId( uint32_t serverIp, uint16_t serverPort, char *buffer, size_t bufferSize ) {
	QL_Steamworks_FormatServerBrowserDetailId( serverIp, serverPort, buffer, bufferSize );
}

/*
=============
QLR_Steamworks_BuildServerBrowserDetailIdentity
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserDetailIdentity( uint32_t serverIp, uint16_t serverPort, ql_steam_server_browser_detail_identity_t *outIdentity ) {
	return QL_Steamworks_BuildServerBrowserDetailIdentity( serverIp, serverPort, outIdentity );
}

/*
=============
QLR_Steamworks_FormatServerBrowserDetailEventName
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_FormatServerBrowserDetailEventName( int channel, int phase, const char *detailId, char *buffer, size_t bufferSize ) {
	return QL_Steamworks_FormatServerBrowserDetailEventName( (ql_steam_server_browser_detail_channel_t)channel, (ql_steam_server_browser_detail_phase_t)phase, detailId, buffer, bufferSize );
}

/*
=============
QLR_Steamworks_BuildServerBrowserDetailEvent
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserDetailEvent( const ql_steam_server_browser_detail_identity_t *identity, int channel, int phase, ql_steam_server_browser_detail_event_t *outEvent ) {
	return QL_Steamworks_BuildServerBrowserDetailEvent( identity, (ql_steam_server_browser_detail_channel_t)channel, (ql_steam_server_browser_detail_phase_t)phase, outEvent );
}

/*
=============
QLR_Steamworks_BuildServerBrowserRuleResponse
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserRuleResponse( const ql_steam_server_browser_detail_identity_t *identity, const char *rule, const char *value, ql_steam_server_browser_rule_response_t *outResponse ) {
	return QL_Steamworks_BuildServerBrowserRuleResponse( identity, rule, value, outResponse );
}

/*
=============
QLR_Steamworks_BuildServerBrowserPlayerResponse
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserPlayerResponse( const ql_steam_server_browser_detail_identity_t *identity, const char *name, int score, int time, ql_steam_server_browser_player_response_t *outResponse ) {
	return QL_Steamworks_BuildServerBrowserPlayerResponse( identity, name, score, time, outResponse );
}

/*
=============
QLR_Steamworks_InitServerBrowserDetailLifecycle
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_InitServerBrowserDetailLifecycle( uint32_t serverIp, uint16_t serverPort, ql_steam_server_browser_detail_lifecycle_t *outLifecycle ) {
	return QL_Steamworks_InitServerBrowserDetailLifecycle( serverIp, serverPort, outLifecycle );
}

/*
=============
QLR_Steamworks_CompleteServerBrowserDetailCallback
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CompleteServerBrowserDetailCallback( ql_steam_server_browser_detail_lifecycle_t *lifecycle, qboolean *outReleaseReady ) {
	return QL_Steamworks_CompleteServerBrowserDetailCallback( lifecycle, outReleaseReady );
}

/*
=============
QLR_Steamworks_CompleteServerBrowserDetailTerminal
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CompleteServerBrowserDetailTerminal( ql_steam_server_browser_detail_lifecycle_t *lifecycle, uint32_t terminalChannel, qboolean *outReleaseReady ) {
	return QL_Steamworks_CompleteServerBrowserDetailTerminal( lifecycle, terminalChannel, outReleaseReady );
}

/*
=============
QLR_Steamworks_BuildServerBrowserDetailResponseViews
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BuildServerBrowserDetailResponseViews( uintptr_t detailObjectBase, ql_steam_server_browser_detail_response_views_t *outViews ) {
	return QL_Steamworks_BuildServerBrowserDetailResponseViews( (void *)detailObjectBase, outViews );
}

/*
=============
QLR_Steamworks_InitServerBrowserDetailRequest
=============
*/
QLR_EXPORT void QLR_Steamworks_InitServerBrowserDetailRequest( ql_steam_server_browser_detail_request_t *request ) {
	QL_Steamworks_InitServerBrowserDetailRequest( request );
}

/*
=============
QLR_Steamworks_BeginServerBrowserDetailRequest
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_BeginServerBrowserDetailRequest( ql_steam_server_browser_detail_request_t *request, uint32_t serverIp, uint16_t serverPort, uintptr_t detailObjectBase ) {
	return QL_Steamworks_BeginServerBrowserDetailRequest( request, serverIp, serverPort, (void *)detailObjectBase );
}

/*
=============
QLR_Steamworks_CompleteServerBrowserDetailRequestCallback
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CompleteServerBrowserDetailRequestCallback( ql_steam_server_browser_detail_request_t *request, qboolean *outReleaseReady ) {
	return QL_Steamworks_CompleteServerBrowserDetailRequestCallback( request, outReleaseReady );
}

/*
=============
QLR_Steamworks_CompleteServerBrowserDetailRequestTerminal
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CompleteServerBrowserDetailRequestTerminal( ql_steam_server_browser_detail_request_t *request, uint32_t terminalChannel, qboolean *outReleaseReady ) {
	return QL_Steamworks_CompleteServerBrowserDetailRequestTerminal( request, terminalChannel, outReleaseReady );
}

/*
=============
QLR_Steamworks_ReleaseServerListRequest
=============
*/
QLR_EXPORT void QLR_Steamworks_ReleaseServerListRequest( uintptr_t request ) {
	QL_Steamworks_ReleaseServerListRequest( (ql_steam_server_list_request_t)request );
}

/*
=============
QLR_Steamworks_RefreshServerListRequest
=============
*/
QLR_EXPORT void QLR_Steamworks_RefreshServerListRequest( uintptr_t request ) {
	QL_Steamworks_RefreshServerListRequest( (ql_steam_server_list_request_t)request );
}

/*
=============
QLR_Steamworks_RequestServerDetails
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_RequestServerDetails( uint32_t serverIp, uint16_t serverPort, uintptr_t pingResponse, uintptr_t playersResponse, uintptr_t rulesResponse, int *outPingQuery, int *outPlayersQuery, int *outRulesQuery ) {
	(void)serverIp;
	(void)serverPort;
	(void)pingResponse;
	(void)playersResponse;
	(void)rulesResponse;
	if ( outPingQuery ) {
		*outPingQuery = 0;
	}
	if ( outPlayersQuery ) {
		*outPlayersQuery = 0;
	}
	if ( outRulesQuery ) {
		*outRulesQuery = 0;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_CancelServerQuery
=============
*/
QLR_EXPORT void QLR_Steamworks_CancelServerQuery( int query ) {
	QL_Steamworks_CancelServerQuery( (ql_steam_server_query_t)query );
}

/*
=============
QLR_Steamworks_CreateLobby
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CreateLobby( int maxMembers ) {
	(void)maxMembers;
	return qfalse;
}

/*
=============
QLR_Steamworks_SetFavoriteServer
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SetFavoriteServer( uint32_t serverIp, uint16_t serverPort, qboolean add ) {
	(void)serverIp;
	(void)serverPort;
	(void)add;
	return qfalse;
}

/*
=============
QLR_Steamworks_SetFavoriteServerForApp
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SetFavoriteServerForApp( uint32_t serverIp, uint16_t serverPort, uint32_t appId, qboolean add ) {
	(void)serverIp;
	(void)serverPort;
	(void)appId;
	(void)add;
	return qfalse;
}

/*
=============
QLR_Steamworks_LeaveLobby
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_LeaveLobby( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QLR_Steamworks_JoinLobby
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_JoinLobby( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QLR_Steamworks_SetLobbyServer
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SetLobbyServer( uint32_t idLow, uint32_t idHigh, uint32_t serverIp, uint16_t serverPort ) {
	(void)idLow;
	(void)idHigh;
	(void)serverIp;
	(void)serverPort;
	return qfalse;
}

/*
=============
QLR_Steamworks_ShowInviteOverlay
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ShowInviteOverlay( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QLR_Steamworks_InviteUserToLobby
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_InviteUserToLobby( uint32_t lobbyIdLow, uint32_t lobbyIdHigh, uint32_t userIdLow, uint32_t userIdHigh ) {
	(void)lobbyIdLow;
	(void)lobbyIdHigh;
	(void)userIdLow;
	(void)userIdHigh;
	return qfalse;
}

/*
=============
QLR_Steamworks_InviteUserToGame
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_InviteUserToGame( uint32_t idLow, uint32_t idHigh, const char *connectString ) {
	(void)idLow;
	(void)idHigh;
	(void)connectString;
	return qfalse;
}

/*
=============
QLR_Steamworks_SayLobby
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SayLobby( uint32_t idLow, uint32_t idHigh, const char *message ) {
	(void)idLow;
	(void)idHigh;
	(void)message;
	return qfalse;
}

/*
=============
QLR_Steamworks_ClearStats
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ClearStats( qboolean achievementsToo ) {
	(void)achievementsToo;
	return qfalse;
}

/*
=============
QLR_Steamworks_RequestUserStats
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_RequestUserStats( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QLR_Steamworks_GetUserStatInt
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetUserStatInt( uint32_t idLow, uint32_t idHigh, const char *name, int *outValue ) {
	(void)idLow;
	(void)idHigh;
	(void)name;
	if ( outValue ) {
		*outValue = 0;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_GetUserStatFloat
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetUserStatFloat( uint32_t idLow, uint32_t idHigh, const char *name, float *outValue ) {
	(void)idLow;
	(void)idHigh;
	(void)name;
	if ( outValue ) {
		*outValue = 0.0f;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_GetUserAchievement
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetUserAchievement( uint32_t idLow, uint32_t idHigh, const char *name, qboolean *outAchieved, int *outUnlockTime ) {
	(void)idLow;
	(void)idHigh;
	(void)name;
	if ( outAchieved ) {
		*outAchieved = qfalse;
	}
	if ( outUnlockTime ) {
		*outUnlockTime = 0;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_GetAchievementDisplayAttribute
=============
*/
QLR_EXPORT const char *QLR_Steamworks_GetAchievementDisplayAttribute( const char *name, const char *key ) {
	(void)name;
	(void)key;
	return "";
}

/*
=============
QLR_Steamworks_IsSubscribedApp
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_IsSubscribedApp( uint32_t appId ) {
	(void)appId;
	return qfalse;
}

/*
=============
QLR_Steamworks_GetNumSubscribedItems
=============
*/
QLR_EXPORT uint32_t QLR_Steamworks_GetNumSubscribedItems( void ) {
	return 0u;
}

/*
=============
QLR_Steamworks_GetSubscribedItems
=============
*/
QLR_EXPORT uint32_t QLR_Steamworks_GetSubscribedItems( uint64_t *outItemIds, uint32_t maxItems ) {
	(void)outItemIds;
	(void)maxItems;
	return 0u;
}

/*
=============
QLR_Steamworks_GetItemInstallInfo
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetItemInstallInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outSizeOnDisk, char *folder, uint32_t folderSize, uint32_t *outTimestamp ) {
	(void)idLow;
	(void)idHigh;
	if ( outSizeOnDisk ) {
		*outSizeOnDisk = 0ull;
	}
	if ( folder && folderSize > 0u ) {
		folder[0] = '\0';
	}
	if ( outTimestamp ) {
		*outTimestamp = 0u;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_SubscribeItem
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SubscribeItem( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QLR_Steamworks_UnsubscribeItem
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_UnsubscribeItem( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QLR_Steamworks_DownloadItem
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_DownloadItem( uint32_t idLow, uint32_t idHigh, int highPriority ) {
	(void)idLow;
	(void)idHigh;
	(void)highPriority;
	return qfalse;
}

/*
=============
QLR_Steamworks_RequestAllUGCQuery
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_RequestAllUGCQuery( uint32_t filter ) {
	(void)filter;
	return qfalse;
}

/*
=============
QLR_Steamworks_GetQueryUGCResult
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetQueryUGCResult( uint64_t queryHandle, uint32_t index, uint64_t *outPublishedFileId, char *title, size_t titleSize, char *description, size_t descriptionSize ) {
	(void)queryHandle;
	(void)index;

	if ( outPublishedFileId ) {
		*outPublishedFileId = 0ull;
	}
	if ( title && titleSize > 0 ) {
		title[0] = '\0';
	}
	if ( description && descriptionSize > 0 ) {
		description[0] = '\0';
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_GetQueryUGCPreviewURL
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetQueryUGCPreviewURL( uint64_t queryHandle, uint32_t index, char *buffer, size_t bufferSize ) {
	(void)queryHandle;
	(void)index;

	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_ReleaseQueryUGCRequest
=============
*/
QLR_EXPORT void QLR_Steamworks_ReleaseQueryUGCRequest( uint64_t queryHandle ) {
	(void)queryHandle;
}

/*
=============
QLR_SteamworksMock_GetUGCCreateQueryCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCCreateQueryCalls( void ) {
	return 0;
}

/*
=============
QLR_SteamworksMock_GetUGCSendQueryCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCSendQueryCalls( void ) {
	return 0;
}

/*
=============
QLR_SteamworksMock_GetUGCReleaseQueryCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCReleaseQueryCalls( void ) {
	return 0;
}

/*
=============
QLR_SteamworksMock_GetUGCLastQueryType
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCLastQueryType( void ) {
	return 0;
}

/*
=============
QLR_SteamworksMock_GetUGCLastMatchingType
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCLastMatchingType( void ) {
	return 0;
}

/*
=============
QLR_SteamworksMock_GetUGCLastCreatorAppId
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetUGCLastCreatorAppId( void ) {
	return 0u;
}

/*
=============
QLR_SteamworksMock_GetUGCLastConsumerAppId
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetUGCLastConsumerAppId( void ) {
	return 0u;
}

/*
=============
QLR_SteamworksMock_GetUGCLastFilter
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetUGCLastFilter( void ) {
	return 0u;
}

/*
=============
QLR_SteamworksMock_GetUGCLastQueryHandle
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetUGCLastQueryHandle( void ) {
	return 0ull;
}

/*
=============
QLR_SteamworksMock_GetUGCLastSentQueryHandle
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetUGCLastSentQueryHandle( void ) {
	return 0ull;
}

/*
=============
QLR_SteamworksMock_GetUGCLastReleasedQueryHandle
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetUGCLastReleasedQueryHandle( void ) {
	return 0ull;
}

/*
=============
QLR_SteamworksMock_GetUGCGetQueryResultCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCGetQueryResultCalls( void ) {
	return 0;
}

/*
=============
QLR_SteamworksMock_GetUGCGetQueryPreviewCalls
=============
*/
QLR_EXPORT int QLR_SteamworksMock_GetUGCGetQueryPreviewCalls( void ) {
	return 0;
}

/*
=============
QLR_SteamworksMock_GetUGCLastResultQueryHandle
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetUGCLastResultQueryHandle( void ) {
	return 0ull;
}

/*
=============
QLR_SteamworksMock_GetUGCLastPreviewQueryHandle
=============
*/
QLR_EXPORT uint64_t QLR_SteamworksMock_GetUGCLastPreviewQueryHandle( void ) {
	return 0ull;
}

/*
=============
QLR_SteamworksMock_GetUGCLastResultIndex
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetUGCLastResultIndex( void ) {
	return 0u;
}

/*
=============
QLR_SteamworksMock_GetUGCLastPreviewIndex
=============
*/
QLR_EXPORT uint32_t QLR_SteamworksMock_GetUGCLastPreviewIndex( void ) {
	return 0u;
}

/*
=============
QLR_SteamworksMock_SetUGCQueryResult
=============
*/
QLR_EXPORT void QLR_SteamworksMock_SetUGCQueryResult( uint64_t publishedFileId, const char *title, const char *description, const char *previewUrl, int result, int previewResult ) {
	(void)publishedFileId;
	(void)title;
	(void)description;
	(void)previewUrl;
	(void)result;
	(void)previewResult;
}

/*
=============
QLR_Steamworks_Init
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_Init( void ) {
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerInitWithVersion
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerInitWithVersion( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated, const char *version ) {
	(void)ip;
	(void)gamePort;
	(void)secure;
	(void)dedicated;
	(void)version;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerInit
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerInit( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated ) {
	(void)ip;
	(void)gamePort;
	(void)secure;
	(void)dedicated;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerShutdown
=============
*/
QLR_EXPORT void QLR_Steamworks_ServerShutdown( void ) {
}

/*
=============
QLR_Steamworks_ServerIsInitialised
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerIsInitialised( void ) {
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerGetAppID
=============
*/
QLR_EXPORT uint32_t QLR_Steamworks_ServerGetAppID( void ) {
	return 0u;
}

/*
=============
QLR_Steamworks_ServerIsLoggedOn
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerIsLoggedOn( void ) {
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerRequestUserStats
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerRequestUserStats( uint64_t steamIdValue ) {
	(void)steamIdValue;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerGetUserStatInt
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerGetUserStatInt( uint64_t steamIdValue, const char *name, int *outValue ) {
	(void)steamIdValue;
	(void)name;
	if ( outValue ) {
		*outValue = 0;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerGetUserStatFloat
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerGetUserStatFloat( uint64_t steamIdValue, const char *name, float *outValue ) {
	(void)steamIdValue;
	(void)name;
	if ( outValue ) {
		*outValue = 0.0f;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerGetUserAchievement
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerGetUserAchievement( uint64_t steamIdValue, const char *name, qboolean *outAchieved ) {
	(void)steamIdValue;
	(void)name;
	if ( outAchieved ) {
		*outAchieved = qfalse;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSetUserStatInt
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetUserStatInt( uint64_t steamIdValue, const char *name, int value ) {
	(void)steamIdValue;
	(void)name;
	(void)value;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSetUserStatFloat
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetUserStatFloat( uint64_t steamIdValue, const char *name, float value ) {
	(void)steamIdValue;
	(void)name;
	(void)value;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerUpdateAvgRateStat
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerUpdateAvgRateStat( uint64_t steamIdValue, const char *name, float countThisSession, double sessionLength ) {
	(void)steamIdValue;
	(void)name;
	(void)countThisSession;
	(void)sessionLength;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSetUserAchievement
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetUserAchievement( uint64_t steamIdValue, const char *name ) {
	(void)steamIdValue;
	(void)name;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerStoreUserStats
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerStoreUserStats( uint64_t steamIdValue ) {
	(void)steamIdValue;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerEnableHeartbeats
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerEnableHeartbeats( qboolean enable ) {
	(void)enable;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSetDedicated
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetDedicated( qboolean dedicated ) {
	(void)dedicated;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerLogOn
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerLogOn( const char *account ) {
	(void)account;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSetProduct
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetProduct( const char *product ) {
	(void)product;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSetGameDir
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetGameDir( const char *gameDir ) {
	(void)gameDir;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSetGameDescription
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetGameDescription( const char *description ) {
	(void)description;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSetMaxPlayerCount
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetMaxPlayerCount( int maxPlayers ) {
	(void)maxPlayers;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSetBotPlayerCount
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetBotPlayerCount( int botPlayers ) {
	(void)botPlayers;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSetServerName
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetServerName( const char *name ) {
	(void)name;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSetMapName
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetMapName( const char *mapName ) {
	(void)mapName;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSetPasswordProtected
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetPasswordProtected( qboolean passwordProtected ) {
	(void)passwordProtected;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerGetSteamID
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerGetSteamID( uint32_t *outIdLow, uint32_t *outIdHigh ) {
	if ( outIdLow ) {
		*outIdLow = 0u;
	}
	if ( outIdHigh ) {
		*outIdHigh = 0u;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerCreateUnauthenticatedUserConnection
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerCreateUnauthenticatedUserConnection( uint32_t *outIdLow, uint32_t *outIdHigh ) {
	if ( outIdLow ) {
		*outIdLow = 0u;
	}
	if ( outIdHigh ) {
		*outIdHigh = 0u;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSetGameTags
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetGameTags( const char *tags ) {
	(void)tags;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSetKeyValue
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetKeyValue( const char *key, const char *value ) {
	(void)key;
	(void)value;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSetKeyValuesFromInfoString
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSetKeyValuesFromInfoString( const char *infoString ) {
	(void)infoString;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerUpdateUserData
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerUpdateUserData( uint32_t idLow, uint32_t idHigh, const char *playerName, uint32_t score ) {
	(void)idLow;
	(void)idHigh;
	(void)playerName;
	(void)score;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerGetPublicIP
=============
*/
QLR_EXPORT uint32_t QLR_Steamworks_ServerGetPublicIP( void ) {
	return 0u;
}

/*
=============
QLR_Steamworks_SendP2PPacket
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SendP2PPacket( uint64_t steamIdValue, const uint8_t *data, uint32_t length, int sendType, int channel ) {
	(void)steamIdValue;
	(void)data;
	(void)length;
	(void)sendType;
	(void)channel;
	return qfalse;
}

/*
=============
QLR_Steamworks_IsP2PPacketAvailable
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_IsP2PPacketAvailable( uint32_t *outSize, int channel ) {
	(void)channel;
	if ( outSize ) {
		*outSize = 0u;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_ReadP2PPacket
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ReadP2PPacket( uint8_t *data, uint32_t dataSize, uint32_t *outSize, uint64_t *outSteamIdValue, int channel ) {
	(void)data;
	(void)dataSize;
	(void)channel;
	if ( outSize ) {
		*outSize = 0u;
	}
	if ( outSteamIdValue ) {
		*outSteamIdValue = 0ull;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_AcceptP2PSession
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_AcceptP2PSession( uint64_t steamIdValue ) {
	(void)steamIdValue;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerSendP2PPacket
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerSendP2PPacket( uint64_t steamIdValue, const uint8_t *data, uint32_t length, int sendType, int channel ) {
	(void)steamIdValue;
	(void)data;
	(void)length;
	(void)sendType;
	(void)channel;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerIsP2PPacketAvailable
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerIsP2PPacketAvailable( uint32_t *outSize, int channel ) {
	(void)channel;
	if ( outSize ) {
		*outSize = 0u;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerReadP2PPacket
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerReadP2PPacket( uint8_t *data, uint32_t dataSize, uint32_t *outSize, uint64_t *outSteamIdValue, int channel ) {
	(void)data;
	(void)dataSize;
	(void)channel;
	if ( outSize ) {
		*outSize = 0u;
	}
	if ( outSteamIdValue ) {
		*outSteamIdValue = 0ull;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerHandleIncomingPacket
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerHandleIncomingPacket( const uint8_t *data, int dataSize, uint32_t ip, uint16_t port ) {
	(void)data;
	(void)dataSize;
	(void)ip;
	(void)port;
	return qfalse;
}

/*
=============
QLR_Steamworks_ServerGetNextOutgoingPacket
=============
*/
QLR_EXPORT int QLR_Steamworks_ServerGetNextOutgoingPacket( uint8_t *data, int dataSize, uint32_t *outIp, uint16_t *outPort ) {
	(void)data;
	(void)dataSize;
	if ( outIp ) {
		*outIp = 0u;
	}
	if ( outPort ) {
		*outPort = 0u;
	}
	return 0;
}

/*
=============
QLR_Steamworks_ServerAcceptP2PSession
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_ServerAcceptP2PSession( uint64_t steamIdValue ) {
	(void)steamIdValue;
	return qfalse;
}

/*
=============
QLR_Steamworks_StartVoiceRecording
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_StartVoiceRecording( void ) {
	return qfalse;
}

/*
=============
QLR_Steamworks_StopVoiceRecording
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_StopVoiceRecording( void ) {
	return qfalse;
}

/*
=============
QLR_Steamworks_GetCompressedVoice
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_GetCompressedVoice( uint8_t *data, uint32_t dataSize, uint32_t *outSize ) {
	(void)data;
	(void)dataSize;
	if ( outSize ) {
		*outSize = 0u;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_DecompressVoice
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_DecompressVoice( const uint8_t *compressedData, uint32_t compressedSize, uint8_t *data, uint32_t dataSize, uint32_t *outSize, uint32_t sampleRate ) {
	(void)compressedData;
	(void)compressedSize;
	(void)data;
	(void)dataSize;
	(void)sampleRate;
	if ( outSize ) {
		*outSize = 0u;
	}
	return qfalse;
}

/*
=============
QLR_Steamworks_GetVoiceOptimalSampleRate
=============
*/
QLR_EXPORT uint32_t QLR_Steamworks_GetVoiceOptimalSampleRate( void ) {
	return 0u;
}

/*
=============
QLR_Steamworks_Shutdown
=============
*/
QLR_EXPORT void QLR_Steamworks_Shutdown( void ) {
	QL_Steamworks_Shutdown();
}

#endif

