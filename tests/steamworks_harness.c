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
#define QLR_AVATAR_BUFFER ( 256 * 256 * 4 )

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

#define QLR_MAX_CALLBACK_REGISTRATIONS 32
#define QLR_MAX_PENDING_CALLBACKS 32
#define QLR_MAX_SUBSCRIBED_ITEMS 32

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
	int callbackId;
	SteamAPICall_t callHandle;
	qboolean ioFailure;
	uint32_t payloadSize;
	uint8_t payload[512];
} qlr_pending_callback_t;

typedef struct {
	qboolean library_available;
	qboolean init_result;
	qboolean user_available;
	EBeginAuthSessionResult auth_result;
	uint8_t ticket[QLR_TICKET_BUFFER];
	uint32_t ticket_length;
	HAuthTicket ticket_handle;
	HAuthTicket cancelled_ticket_handle;
	int cancel_auth_ticket_calls;
	uint32_t app_id;
	uint64_t steam_id_value;
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
	char rich_presence_key[32];
	char rich_presence_value[128];
	int rich_presence_calls;
	int rich_presence_result;
	int steam_game_server_init_calls;
	int steam_game_server_shutdown_calls;
	int steam_game_server_init_result;
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
	uint64_t steam_game_server_last_user_data_id;
	uint32_t steam_game_server_public_ip;
	uint32_t steam_game_server_last_user_data_score;
	int steam_game_server_last_max_player_count;
	int steam_game_server_last_bot_player_count;
	int steam_game_server_last_password_protected;
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
	int lobby_say_calls;
	int lobby_set_server_calls;
	int user_stats_request_calls;
	int lobby_create_type;
	int lobby_create_max_members;
	uint64_t lobby_leave_id;
	uint64_t lobby_join_id;
	uint64_t lobby_invite_id;
	uint64_t lobby_say_id;
	uint64_t lobby_set_server_id;
	uint64_t lobby_owner_id;
	uint64_t lobby_set_server_game_server_id;
	uint32_t lobby_set_server_ip;
	uint16_t lobby_set_server_port;
	char lobby_say_message[256];
	uint64_t user_stats_request_id;
	uint64_t create_lobby_result;
	uint64_t join_lobby_result;
	int say_lobby_result;
	uint64_t request_user_stats_result;
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

static qlr_steamworks_mock_state_t qlr_mock_state = {
	.library_available = qtrue,
	.init_result = qtrue,
	.user_available = qtrue,
	.auth_result = k_EBeginAuthSessionResultOK,
	.ticket = { 0x12, 0x34, 0x56, 0x78 },
	.ticket_length = 4,
	.ticket_handle = 1,
	.cancelled_ticket_handle = 0,
	.cancel_auth_ticket_calls = 0,
	.app_id = 0x54100,
	.steam_id_value = 0xDEADBEEFULL,
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
	.rich_presence_key = "",
	.rich_presence_value = "",
	.rich_presence_calls = 0,
	.rich_presence_result = 1,
	.steam_game_server_init_calls = 0,
	.steam_game_server_shutdown_calls = 0,
	.steam_game_server_init_result = 1,
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
	.steam_game_server_last_user_data_id = 0ULL,
	.steam_game_server_public_ip = 0x01020304,
	.steam_game_server_last_user_data_score = 0u,
	.steam_game_server_last_max_player_count = 0,
	.steam_game_server_last_bot_player_count = 0,
	.steam_game_server_last_password_protected = -1,
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
	.create_lobby_result = 1,
	.join_lobby_result = 1,
	.say_lobby_result = 1,
	.request_user_stats_result = 1,
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

void *QLR_SteamAPI_SteamUserStats( void );

void *QLR_SteamAPI_SteamMatchmaking( void );

void *QLR_SteamAPI_SteamUGC( void );

void *QLR_SteamAPI_SteamGameServerUGC( void );

qboolean QLR_SteamAPI_SteamGameServerInit( uint32_t ip, uint16_t steamPort, uint16_t gamePort, uint16_t queryPort, int serverMode, const char *version );

void *QLR_SteamAPI_SteamGameServer( void );

void QLR_SteamAPI_SteamGameServerShutdown( void );

void QLR_SteamAPI_SteamGameServerRunCallbacks( void );

void *QLR_SteamAPI_SteamGameServerNetworking( void );

static CSteamID *QLR_FASTCALL QLR_SteamUser_GetSteamID( void *self, void *unused, CSteamID *outSteamId );

HAuthTicket QLR_SteamAPI_GetAuthSessionTicket( void *user, void *ticket, int ticket_size, uint32_t *length );

EBeginAuthSessionResult QLR_SteamAPI_BeginAuthSession( void *user, const void *ticket, int length, CSteamID steamId );

void QLR_SteamAPI_CancelAuthTicket( void *user, HAuthTicket handle );

void QLR_SteamAPI_EndAuthSession( void *user, CSteamID steamId );

CSteamID QLR_SteamAPI_GetSteamID( void *user );

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
QLR_SteamworksMock_Reset

Restore default mock state for Steamworks entry points.
=============
*/
QLR_EXPORT void QLR_SteamworksMock_Reset( void ) {
	qlr_mock_state.library_available = qtrue;
	qlr_mock_state.init_result = qtrue;
	qlr_mock_state.user_available = qtrue;
	qlr_mock_state.auth_result = k_EBeginAuthSessionResultOK;
	memcpy( qlr_mock_state.ticket, (uint8_t[]){ 0x12, 0x34, 0x56, 0x78 }, 4 );
	qlr_mock_state.ticket_length = 4;
	qlr_mock_state.ticket_handle = 1;
	qlr_mock_state.cancelled_ticket_handle = 0;
	qlr_mock_state.cancel_auth_ticket_calls = 0;
	qlr_mock_state.app_id = 0x54100;
	qlr_mock_state.steam_id_value = 0xDEADBEEFULL;
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
	qlr_mock_state.rich_presence_key[0] = '\0';
	qlr_mock_state.rich_presence_value[0] = '\0';
	qlr_mock_state.rich_presence_calls = 0;
	qlr_mock_state.rich_presence_result = 1;
	qlr_mock_state.steam_game_server_init_calls = 0;
	qlr_mock_state.steam_game_server_shutdown_calls = 0;
	qlr_mock_state.steam_game_server_init_result = 1;
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
	qlr_mock_state.steam_game_server_last_user_data_id = 0ULL;
	qlr_mock_state.steam_game_server_public_ip = 0x01020304;
	qlr_mock_state.steam_game_server_last_user_data_score = 0u;
	qlr_mock_state.steam_game_server_last_max_player_count = 0;
	qlr_mock_state.steam_game_server_last_bot_player_count = 0;
	qlr_mock_state.steam_game_server_last_password_protected = -1;
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
	qlr_mock_state.lobby_say_calls = 0;
	qlr_mock_state.lobby_set_server_calls = 0;
	qlr_mock_state.user_stats_request_calls = 0;
	qlr_mock_state.lobby_create_type = 0;
	qlr_mock_state.lobby_create_max_members = 0;
	qlr_mock_state.lobby_leave_id = 0;
	qlr_mock_state.lobby_join_id = 0;
	qlr_mock_state.lobby_invite_id = 0;
	qlr_mock_state.lobby_say_id = 0;
	qlr_mock_state.lobby_set_server_id = 0;
	qlr_mock_state.lobby_owner_id = qlr_mock_state.steam_id_value;
	qlr_mock_state.lobby_set_server_game_server_id = 0;
	qlr_mock_state.lobby_set_server_ip = 0;
	qlr_mock_state.lobby_set_server_port = 0;
	qlr_mock_state.lobby_say_message[0] = '\0';
	qlr_mock_state.user_stats_request_id = 0;
	qlr_mock_state.create_lobby_result = 1;
	qlr_mock_state.join_lobby_result = 1;
	qlr_mock_state.say_lobby_result = 1;
	qlr_mock_state.request_user_stats_result = 1;
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
QLR_SteamworksMock_GetSteamGameServerLastInitGamePort
=============
*/
QLR_EXPORT uint16_t QLR_SteamworksMock_GetSteamGameServerLastInitGamePort( void ) {
	return qlr_mock_state.steam_game_server_last_init_game_port;
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

	if ( strcmp( symbol, "SteamAPI_Init" ) == 0 ) {
		return QLR_SteamAPI_Init;
	}

	if ( strcmp( symbol, "SteamAPI_Shutdown" ) == 0 ) {
		return QLR_SteamAPI_Shutdown;
	}

	if ( strcmp( symbol, "SteamAPI_RunCallbacks" ) == 0 ) {
		return QLR_SteamAPI_RunCallbacks;
	}

	if ( strcmp( symbol, "SteamAPI_RegisterCallback" ) == 0 ) {
		return QLR_SteamAPI_RegisterCallback;
	}

	if ( strcmp( symbol, "SteamAPI_UnregisterCallback" ) == 0 ) {
		return QLR_SteamAPI_UnregisterCallback;
	}

	if ( strcmp( symbol, "SteamAPI_RegisterCallResult" ) == 0 ) {
		return QLR_SteamAPI_RegisterCallResult;
	}

	if ( strcmp( symbol, "SteamAPI_UnregisterCallResult" ) == 0 ) {
		return QLR_SteamAPI_UnregisterCallResult;
	}

	if ( strcmp( symbol, "SteamAPI_SteamUser" ) == 0 ) {
		return QLR_SteamAPI_SteamUser;
	}

	if ( strcmp( symbol, "SteamAPI_SteamFriends" ) == 0 ) {
		return QLR_SteamAPI_SteamFriends;
	}

	if ( strcmp( symbol, "SteamAPI_SteamUtils" ) == 0 ) {
		return QLR_SteamAPI_SteamUtils;
	}

	if ( strcmp( symbol, "SteamAPI_SteamUserStats" ) == 0 ) {
		return QLR_SteamAPI_SteamUserStats;
	}

	if ( strcmp( symbol, "SteamAPI_SteamMatchmaking" ) == 0 ) {
		return QLR_SteamAPI_SteamMatchmaking;
	}

	if ( strcmp( symbol, "SteamAPI_SteamUGC" ) == 0 ) {
		return QLR_SteamAPI_SteamUGC;
	}

	if ( strcmp( symbol, "SteamGameServer" ) == 0 ) {
		return QLR_SteamAPI_SteamGameServer;
	}

	if ( strcmp( symbol, "SteamGameServer_RunCallbacks" ) == 0 ) {
		return QLR_SteamAPI_SteamGameServerRunCallbacks;
	}

	if ( strcmp( symbol, "SteamGameServerNetworking" ) == 0 ) {
		return QLR_SteamAPI_SteamGameServerNetworking;
	}

	if ( strcmp( symbol, "SteamAPI_ISteamUser_GetAuthSessionTicket" ) == 0 ) {
		return QLR_SteamAPI_GetAuthSessionTicket;
	}

	if ( strcmp( symbol, "SteamAPI_ISteamUser_BeginAuthSession" ) == 0 ) {
		return QLR_SteamAPI_BeginAuthSession;
	}

	if ( strcmp( symbol, "SteamAPI_ISteamUser_CancelAuthTicket" ) == 0 ) {
		return QLR_SteamAPI_CancelAuthTicket;
	}

	if ( strcmp( symbol, "SteamAPI_ISteamUser_EndAuthSession" ) == 0 ) {
		return QLR_SteamAPI_EndAuthSession;
	}

	if ( strcmp( symbol, "SteamAPI_ISteamUser_GetSteamID" ) == 0 ) {
		return QLR_SteamAPI_GetSteamID;
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
QLR_SteamAPI_RunCallbacks
=============
*/
void QLR_SteamAPI_RunCallbacks( void ) {
	int pendingIndex;

	for ( pendingIndex = 0; pendingIndex < qlr_mock_state.pending_callback_count; ++pendingIndex ) {
		qlr_pending_callback_t *pending;
		int registrationIndex;

		pending = &qlr_mock_state.pending_callbacks[pendingIndex];
		for ( registrationIndex = 0; registrationIndex < qlr_mock_state.registered_callback_count; ++registrationIndex ) {
			qlr_callback_registration_t *registration;
			qlr_callback_base_t *callbackBase;

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

			if ( pending->callResult ) {
				if ( callbackBase->vtable->runCallResult ) {
					callbackBase->vtable->runCallResult( callbackBase, pending->payload, pending->ioFailure, pending->callHandle );
				}
			} else if ( callbackBase->vtable->run ) {
				callbackBase->vtable->run( callbackBase, pending->payload );
			}
		}
	}

	qlr_mock_state.pending_callback_count = 0;
	memset( qlr_mock_state.pending_callbacks, 0, sizeof( qlr_mock_state.pending_callbacks ) );
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
}

/*
=============
QLR_SteamAPI_SteamUser
=============
*/
void *QLR_SteamAPI_SteamUser( void ) {
	static void *vtable[0x08 / 4 + 1];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[0x08 / 4] = QLR_SteamUser_GetSteamID;
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
QLR_SteamUser_GetSteamID
=============
*/
static CSteamID *QLR_FASTCALL QLR_SteamUser_GetSteamID( void *self, void *unused, CSteamID *outSteamId ) {
	(void)self;
	(void)unused;

	if ( outSteamId ) {
		outSteamId->value = qlr_mock_state.steam_id_value;
	}

	return outSteamId;
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
QLR_SteamGameServer_GetPublicIP
=============
*/
static uint32_t QLR_FASTCALL QLR_SteamGameServer_GetPublicIP( void *self ) {
	(void)self;
	return qlr_mock_state.steam_game_server_public_ip;
}

/*
=============
QLR_SteamGameServer_GetNextOutgoingPacket
=============
*/
static int QLR_FASTCALL QLR_SteamGameServer_GetNextOutgoingPacket( void *self, void *data, int dataSize, uint32_t *outIp, uint16_t *outPort ) {
	(void)self;
	(void)data;
	(void)dataSize;
	(void)outIp;
	(void)outPort;
	return 0;
}

/*
=============
QLR_SteamGameServer_EnableHeartbeats
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_EnableHeartbeats( void *self, int enable ) {
	(void)self;

	qlr_mock_state.steam_game_server_heartbeat_calls++;
	qlr_mock_state.steam_game_server_last_heartbeat_enabled = enable;
}

/*
=============
QLR_SteamGameServer_SetDedicated
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetDedicated( void *self, int dedicated ) {
	(void)self;

	qlr_mock_state.steam_game_server_dedicated_calls++;
	qlr_mock_state.steam_game_server_last_dedicated = dedicated;
}

/*
=============
QLR_SteamGameServer_LogOn
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_LogOn( void *self, const char *account ) {
	(void)self;

	qlr_mock_state.steam_game_server_logon_calls++;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_account, account ? account : "", sizeof( qlr_mock_state.steam_game_server_last_account ) );
}

/*
=============
QLR_SteamGameServer_LogOnAnonymous
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_LogOnAnonymous( void *self ) {
	(void)self;

	qlr_mock_state.steam_game_server_logon_anonymous_calls++;
}

/*
=============
QLR_SteamGameServer_SetProduct
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetProduct( void *self, const char *product ) {
	(void)self;

	qlr_mock_state.steam_game_server_product_calls++;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_product, product ? product : "", sizeof( qlr_mock_state.steam_game_server_last_product ) );
}

/*
=============
QLR_SteamGameServer_SetGameDir
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetGameDir( void *self, const char *gameDir ) {
	(void)self;

	qlr_mock_state.steam_game_server_game_dir_calls++;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_game_dir, gameDir ? gameDir : "", sizeof( qlr_mock_state.steam_game_server_last_game_dir ) );
}

/*
=============
QLR_SteamGameServer_SetGameDescription
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetGameDescription( void *self, const char *description ) {
	(void)self;

	qlr_mock_state.steam_game_server_game_description_calls++;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_game_description, description ? description : "", sizeof( qlr_mock_state.steam_game_server_last_game_description ) );
}

/*
=============
QLR_SteamGameServer_SetMaxPlayerCount
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetMaxPlayerCount( void *self, int maxPlayers ) {
	(void)self;

	qlr_mock_state.steam_game_server_max_player_count_calls++;
	qlr_mock_state.steam_game_server_last_max_player_count = maxPlayers;
}

/*
=============
QLR_SteamGameServer_SetBotPlayerCount
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetBotPlayerCount( void *self, int botPlayers ) {
	(void)self;

	qlr_mock_state.steam_game_server_bot_player_count_calls++;
	qlr_mock_state.steam_game_server_last_bot_player_count = botPlayers;
}

/*
=============
QLR_SteamGameServer_SetServerName
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetServerName( void *self, const char *name ) {
	(void)self;

	qlr_mock_state.steam_game_server_server_name_calls++;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_server_name, name ? name : "", sizeof( qlr_mock_state.steam_game_server_last_server_name ) );
}

/*
=============
QLR_SteamGameServer_SetMapName
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetMapName( void *self, const char *mapName ) {
	(void)self;

	qlr_mock_state.steam_game_server_map_name_calls++;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_map_name, mapName ? mapName : "", sizeof( qlr_mock_state.steam_game_server_last_map_name ) );
}

/*
=============
QLR_SteamGameServer_SetPasswordProtected
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetPasswordProtected( void *self, int passwordProtected ) {
	(void)self;

	qlr_mock_state.steam_game_server_password_calls++;
	qlr_mock_state.steam_game_server_last_password_protected = passwordProtected;
}

/*
=============
QLR_SteamGameServer_SetGameTags
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetGameTags( void *self, const char *tags ) {
	(void)self;

	qlr_mock_state.steam_game_server_game_tags_calls++;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_game_tags, tags ? tags : "", sizeof( qlr_mock_state.steam_game_server_last_game_tags ) );
}

/*
=============
QLR_SteamGameServer_SetKeyValue
=============
*/
static void QLR_FASTCALL QLR_SteamGameServer_SetKeyValue( void *self, const char *key, const char *value ) {
	(void)self;

	Q_strncpyz( qlr_mock_state.steam_game_server_last_key, key ? key : "", sizeof( qlr_mock_state.steam_game_server_last_key ) );
	Q_strncpyz( qlr_mock_state.steam_game_server_last_value, value ? value : "", sizeof( qlr_mock_state.steam_game_server_last_value ) );
	qlr_mock_state.steam_game_server_key_value_calls++;
}

/*
=============
QLR_SteamGameServer_UpdateUserData
=============
*/
static int QLR_FASTCALL QLR_SteamGameServer_UpdateUserData( void *self, uint32_t idLow, uint32_t idHigh, const char *playerName, uint32_t score ) {
	(void)self;

	qlr_mock_state.steam_game_server_user_data_calls++;
	qlr_mock_state.steam_game_server_last_user_data_id = ((uint64_t)idHigh << 32) | (uint64_t)idLow;
	qlr_mock_state.steam_game_server_last_user_data_score = score;
	Q_strncpyz( qlr_mock_state.steam_game_server_last_user_data_name, playerName ? playerName : "", sizeof( qlr_mock_state.steam_game_server_last_user_data_name ) );
	return 1;
}

/*
=============
QLR_SteamFriends_GetPersonaName
=============
*/
static const char *QLR_FASTCALL QLR_SteamFriends_GetPersonaName( void *self, void *unused ) {
	(void)self;
	(void)unused;
	return qlr_mock_state.persona_name;
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
QLR_SteamworksMock_CombineIdentityWords
=============
*/
static uint64_t QLR_SteamworksMock_CombineIdentityWords( uint32_t idLow, uint32_t idHigh ) {
	return ( (uint64_t)idHigh << 32 ) | idLow;
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
	static void *vtable[0xb4 / 4 + 1];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[0] = QLR_SteamFriends_GetPersonaName;
	vtable[0x14 / 4] = QLR_SteamFriends_GetFriendRelationship;
	vtable[0x18 / 4] = QLR_SteamFriends_GetFriendPersonaState;
	vtable[0x1c / 4] = QLR_SteamFriends_GetFriendPersonaName;
	vtable[0x20 / 4] = QLR_SteamFriends_GetFriendGamePlayed;
	vtable[0x2c / 4] = QLR_SteamFriends_GetPlayerNickname;
	vtable[0x74 / 4] = QLR_SteamFriends_ActivateGameOverlayToUser;
	vtable[0x84 / 4] = QLR_SteamFriends_ActivateGameOverlayInviteDialog;
	vtable[0x88 / 4] = QLR_SteamFriends_GetSmallFriendAvatar;
	vtable[0x8c / 4] = QLR_SteamFriends_GetMediumFriendAvatar;
	vtable[0x90 / 4] = QLR_SteamFriends_GetLargeFriendAvatar;
	vtable[0xac / 4] = QLR_SteamFriends_SetRichPresence;
	vtable[0xb4 / 4] = QLR_SteamFriends_GetFriendRichPresence;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamUtils
=============
*/
void *QLR_SteamAPI_SteamUtils( void ) {
	static void *vtable[0x24 / 4 + 1];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[0x10 / 4] = QLR_SteamUtils_GetIPCountry;
	vtable[0x14 / 4] = QLR_SteamUtils_GetImageSize;
	vtable[0x18 / 4] = QLR_SteamUtils_GetImageRGBA;
	vtable[0x24 / 4] = QLR_SteamUtils_GetAppID;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamUserStats
=============
*/
void *QLR_SteamAPI_SteamUserStats( void ) {
	static void *vtable[0x54 / 4 + 1];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[0x40 / 4] = QLR_SteamUserStats_RequestUserStats;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamMatchmaking
=============
*/
void *QLR_SteamAPI_SteamMatchmaking( void ) {
	static void *vtable[0x8c / 4 + 1];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[0x34 / 4] = QLR_SteamMatchmaking_CreateLobby;
	vtable[0x3c / 4] = QLR_SteamMatchmaking_LeaveLobby;
	vtable[0x38 / 4] = QLR_SteamMatchmaking_JoinLobby;
	vtable[0x68 / 4] = QLR_SteamMatchmaking_SendLobbyChatMsg;
	vtable[0x6c / 4] = QLR_SteamMatchmaking_GetLobbyChatEntry;
	vtable[0x74 / 4] = QLR_SteamMatchmaking_SetLobbyGameServer;
	vtable[0x8c / 4] = QLR_SteamMatchmaking_GetLobbyOwner;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamGameServer
=============
*/
void *QLR_SteamAPI_SteamGameServer( void ) {
	static void *vtable[0x9c / 4 + 1];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[0x04 / 4] = QLR_SteamGameServer_SetProduct;
	vtable[0x08 / 4] = QLR_SteamGameServer_SetGameDescription;
	vtable[0x0c / 4] = QLR_SteamGameServer_SetGameDir;
	vtable[0x10 / 4] = QLR_SteamGameServer_SetDedicated;
	vtable[0x14 / 4] = QLR_SteamGameServer_LogOn;
	vtable[0x18 / 4] = QLR_SteamGameServer_LogOnAnonymous;
	vtable[0x28 / 4] = QLR_SteamGameServer_GetSteamID;
	vtable[0x30 / 4] = QLR_SteamGameServer_SetMaxPlayerCount;
	vtable[0x34 / 4] = QLR_SteamGameServer_SetBotPlayerCount;
	vtable[0x38 / 4] = QLR_SteamGameServer_SetServerName;
	vtable[0x3c / 4] = QLR_SteamGameServer_SetMapName;
	vtable[0x40 / 4] = QLR_SteamGameServer_SetPasswordProtected;
	vtable[0x54 / 4] = QLR_SteamGameServer_SetGameTags;
	vtable[0x50 / 4] = QLR_SteamGameServer_SetKeyValue;
	vtable[0x6c / 4] = QLR_SteamGameServer_UpdateUserData;
	vtable[0x90 / 4] = QLR_SteamGameServer_GetPublicIP;
	vtable[0x98 / 4] = QLR_SteamGameServer_GetNextOutgoingPacket;
	vtable[0x9c / 4] = QLR_SteamGameServer_EnableHeartbeats;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamGameServerNetworking
=============
*/
void *QLR_SteamAPI_SteamGameServerNetworking( void ) {
	return NULL;
}

/*
=============
QLR_SteamAPI_SteamUGC
=============
*/
void *QLR_SteamAPI_SteamUGC( void ) {
	static void *vtable[0xdc / 4 + 1];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[0xc0 / 4] = QLR_SteamUGC_SubscribeItem;
	vtable[0xc4 / 4] = QLR_SteamUGC_UnsubscribeItem;
	vtable[0xc8 / 4] = QLR_SteamUGC_GetNumSubscribedItems;
	vtable[0xcc / 4] = QLR_SteamUGC_GetSubscribedItems;
	vtable[0xd0 / 4] = QLR_SteamUGC_GetItemState;
	vtable[0xd4 / 4] = QLR_SteamUGC_GetItemInstallInfo;
	vtable[0xd8 / 4] = QLR_SteamUGC_GetItemDownloadInfo;
	vtable[0xdc / 4] = QLR_SteamUGC_DownloadItem;
	return &iface;
}

/*
=============
QLR_SteamAPI_SteamGameServerUGC
=============
*/
void *QLR_SteamAPI_SteamGameServerUGC( void ) {
	static void *vtable[0xdc / 4 + 1];
	static qlr_steamworks_mock_interface_t iface = { vtable };

	vtable[0xc0 / 4] = QLR_SteamGameServerUGC_SubscribeItem;
	vtable[0xc4 / 4] = QLR_SteamGameServerUGC_UnsubscribeItem;
	vtable[0xc8 / 4] = QLR_SteamUGC_GetNumSubscribedItems;
	vtable[0xcc / 4] = QLR_SteamUGC_GetSubscribedItems;
	vtable[0xd0 / 4] = QLR_SteamGameServerUGC_GetItemState;
	vtable[0xd4 / 4] = QLR_SteamUGC_GetItemInstallInfo;
	vtable[0xd8 / 4] = QLR_SteamGameServerUGC_GetItemDownloadInfo;
	vtable[0xdc / 4] = QLR_SteamGameServerUGC_DownloadItem;
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

#include "../src/common/platform/platform_steamworks.c"

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
	state.SteamAPI_Init = QLR_SteamAPI_Init;
	state.SteamAPI_Shutdown = QLR_SteamAPI_Shutdown;
	state.SteamAPI_RunCallbacks = QLR_SteamAPI_RunCallbacks;
	state.SteamAPI_RegisterCallback = QLR_SteamAPI_RegisterCallback;
	state.SteamAPI_UnregisterCallback = QLR_SteamAPI_UnregisterCallback;
	state.SteamAPI_RegisterCallResult = QLR_SteamAPI_RegisterCallResult;
	state.SteamAPI_UnregisterCallResult = QLR_SteamAPI_UnregisterCallResult;
	state.SteamUser = QLR_SteamAPI_SteamUser;
	state.SteamFriends = QLR_SteamAPI_SteamFriends;
	state.SteamUtils = QLR_SteamAPI_SteamUtils;
	state.SteamUserStats = QLR_SteamAPI_SteamUserStats;
	state.SteamMatchmaking = QLR_SteamAPI_SteamMatchmaking;
	state.SteamUGC = QLR_SteamAPI_SteamUGC;
	state.SteamGameServerUGC = QLR_SteamAPI_SteamGameServerUGC;
	state.SteamGameServer_Init = QLR_SteamAPI_SteamGameServerInit;
	state.SteamGameServer = QLR_SteamAPI_SteamGameServer;
	state.SteamGameServer_Shutdown = QLR_SteamAPI_SteamGameServerShutdown;
	state.SteamGameServer_RunCallbacks = QLR_SteamAPI_SteamGameServerRunCallbacks;
	state.SteamGameServerNetworking = QLR_SteamAPI_SteamGameServerNetworking;
	state.GetAuthSessionTicket = QLR_SteamAPI_GetAuthSessionTicket;
	state.BeginAuthSession = QLR_SteamAPI_BeginAuthSession;
	state.CancelAuthTicket = QLR_SteamAPI_CancelAuthTicket;
	state.EndAuthSession = QLR_SteamAPI_EndAuthSession;
	state.GetSteamID = QLR_SteamAPI_GetSteamID;
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
QLR_SteamworksMock_QueueCallback
=============
*/
static qboolean QLR_SteamworksMock_QueueCallback( qboolean callResult, int callbackId, SteamAPICall_t callHandle, const void *payload, uint32_t payloadSize, qboolean ioFailure ) {
	qlr_pending_callback_t *pending;

	if ( qlr_mock_state.pending_callback_count >= QLR_MAX_PENDING_CALLBACKS ) {
		return qfalse;
	}

	pending = &qlr_mock_state.pending_callbacks[qlr_mock_state.pending_callback_count++];
	memset( pending, 0, sizeof( *pending ) );
	pending->callResult = callResult;
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
	ql_steam_lobby_callback_bindings_t lobbyBindings;
	ql_steam_micro_callback_bindings_t microBindings;
	ql_steam_workshop_callback_bindings_t workshopBindings;

	memset( &clientBindings, 0, sizeof( clientBindings ) );
	memset( &lobbyBindings, 0, sizeof( lobbyBindings ) );
	memset( &microBindings, 0, sizeof( microBindings ) );
	memset( &workshopBindings, 0, sizeof( workshopBindings ) );

	clientBindings.onRichPresenceJoinRequested = QLR_SteamworksHarness_OnRichPresenceJoinRequested;
	clientBindings.onUGCQueryCompleted = QLR_SteamworksHarness_OnUGCQueryCompleted;
	lobbyBindings.onLobbyEnter = QLR_SteamworksHarness_OnLobbyEnter;
	microBindings.onAuthorizationResponse = QLR_SteamworksHarness_OnMicroAuthorizationResponse;
	workshopBindings.onItemInstalled = QLR_SteamworksHarness_OnItemInstalled;
	workshopBindings.onDownloadItemResult = QLR_SteamworksHarness_OnDownloadItemResult;

	if ( !QL_Steamworks_RegisterClientCallbacks( &clientBindings ) ) {
		return qfalse;
	}
	if ( !QL_Steamworks_RegisterLobbyCallbacks( &lobbyBindings ) ) {
		QL_Steamworks_UnregisterClientCallbacks();
		return qfalse;
	}
	if ( !QL_Steamworks_RegisterMicroCallbacks( &microBindings ) ) {
		QL_Steamworks_UnregisterLobbyCallbacks();
		QL_Steamworks_UnregisterClientCallbacks();
		return qfalse;
	}
	if ( !QL_Steamworks_RegisterWorkshopCallbacks( &workshopBindings ) ) {
		QL_Steamworks_UnregisterMicroCallbacks();
		QL_Steamworks_UnregisterLobbyCallbacks();
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
	QL_Steamworks_UnregisterClientCallbacks();
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
QLR_Steamworks_RunCallbackPump
=============
*/
QLR_EXPORT void QLR_Steamworks_RunCallbackPump( void ) {
	QL_Steamworks_RunCallbacks();
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
	return QLR_SteamworksMock_QueueCallback( qfalse, 0x151, 0ull, &event, sizeof( event ), qfalse );
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
	return QLR_SteamworksMock_QueueCallback( qfalse, 0x1f8, 0ull, &event, sizeof( event ), qfalse );
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
	return QLR_SteamworksMock_QueueCallback( qfalse, 0x98, 0ull, &event, sizeof( event ), qfalse );
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
	return QLR_SteamworksMock_QueueCallback( qfalse, QL_STEAM_CALLBACK_ITEM_INSTALLED, 0ull, &event, sizeof( event ), qfalse );
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
	return QLR_SteamworksMock_QueueCallback( qfalse, QL_STEAM_CALLBACK_DOWNLOAD_ITEM_RESULT, 0ull, &event, sizeof( event ), qfalse );
}

/*
=============
QLR_SteamworksMock_QueueUGCQueryCompleted
=============
*/
QLR_EXPORT qboolean QLR_SteamworksMock_QueueUGCQueryCompleted( uint64_t callHandle, uint64_t queryHandle, int result, uint32_t numResultsReturned, uint32_t totalMatchingResults, int cachedData ) {
	ql_steam_ugc_query_completed_raw_t event;

	memset( &event, 0, sizeof( event ) );
	event.queryHandle = queryHandle;
	event.result = result;
	event.numResultsReturned = numResultsReturned;
	event.totalMatchingResults = totalMatchingResults;
	event.cachedData = cachedData ? qtrue : qfalse;
	return QLR_SteamworksMock_QueueCallback( qtrue, 0xd49, (SteamAPICall_t)callHandle, &event, sizeof( event ), qfalse );
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
QLR_Steamworks_SetRichPresence
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SetRichPresence( const char *key, const char *value ) {
	return QL_Steamworks_SetRichPresence( key, value );
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
QLR_Steamworks_CreateLobby
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CreateLobby( int maxMembers ) {
	return QL_Steamworks_CreateLobby( maxMembers );
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
QLR_Steamworks_SayLobby
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_SayLobby( uint32_t idLow, uint32_t idHigh, const char *message ) {
	return QL_Steamworks_SayLobby( idLow, idHigh, message );
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
QLR_Steamworks_CreateLobby
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_CreateLobby( int maxMembers ) {
	(void)maxMembers;
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
QLR_Steamworks_Init
=============
*/
QLR_EXPORT qboolean QLR_Steamworks_Init( void ) {
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
QLR_Steamworks_Shutdown
=============
*/
QLR_EXPORT void QLR_Steamworks_Shutdown( void ) {
	QL_Steamworks_Shutdown();
}

#endif

