#ifndef PLATFORM_STEAMWORKS_H
#define PLATFORM_STEAMWORKS_H

#include "platform_config.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "../auth_credentials.h"

typedef struct {
	uint64_t value;
} CSteamID;

typedef enum {
	QL_STEAM_AVATAR_SMALL = 0,
	QL_STEAM_AVATAR_MEDIUM = 1,
	QL_STEAM_AVATAR_LARGE = 2
} ql_steam_avatar_size_t;

typedef enum {
	QL_STEAM_AVATAR_IMAGE_UNAVAILABLE = 0,
	QL_STEAM_AVATAR_IMAGE_PENDING = 1,
	QL_STEAM_AVATAR_IMAGE_READY = 2
} ql_steam_avatar_image_state_t;

typedef uint64_t SteamAPICall_t;
typedef void *ql_steam_server_list_request_t;
typedef int ql_steam_server_query_t;

typedef enum {
	QL_STEAM_SERVER_BROWSER_INTERNET = 0,
	QL_STEAM_SERVER_BROWSER_LAN = 1,
	QL_STEAM_SERVER_BROWSER_FRIENDS = 2,
	QL_STEAM_SERVER_BROWSER_FAVORITES = 3,
	QL_STEAM_SERVER_BROWSER_HISTORY = 4
} ql_steam_server_browser_request_mode_t;

typedef enum {
	QL_STEAM_SERVER_BROWSER_DETAIL_RULES = 0,
	QL_STEAM_SERVER_BROWSER_DETAIL_PLAYERS = 1
} ql_steam_server_browser_detail_channel_t;

typedef enum {
	QL_STEAM_SERVER_BROWSER_DETAIL_RESPONSE = 0,
	QL_STEAM_SERVER_BROWSER_DETAIL_FAILED = 1,
	QL_STEAM_SERVER_BROWSER_DETAIL_END = 2
} ql_steam_server_browser_detail_phase_t;

typedef struct {
	qboolean refreshActive;
	ql_steam_server_list_request_t request;
} ql_steam_server_browser_owner_t;

#define QL_STEAM_NAME_LENGTH 128
#define QL_STEAM_STATUS_LENGTH 256
#define QL_STEAM_COMMAND_LENGTH 256
#define QL_STEAM_SERVER_LENGTH 128
#define QL_STEAM_PASSWORD_LENGTH 128
#define QL_STEAM_LOBBY_MESSAGE_LENGTH 256
#define QL_STEAM_APPID_PUBLIC_RETAIL 282440u
#define QL_STEAM_APPID_REFERENCE_RETAIL 0x54100u
#define QL_STEAM_GAMESERVER_DEFAULT_VERSION QL_RETAIL_VERSION
#define QL_STEAM_SERVER_BROWSER_GAME_DIR_LENGTH 32
#define QL_STEAM_SERVER_BROWSER_MAP_LENGTH 32
#define QL_STEAM_SERVER_BROWSER_GAME_DESCRIPTION_LENGTH 64
#define QL_STEAM_SERVER_BROWSER_NAME_LENGTH 64
#define QL_STEAM_SERVER_BROWSER_DISPLAY_NAME_LENGTH 64
#define QL_STEAM_SERVER_BROWSER_TAGS_LENGTH 128
#define QL_STEAM_SERVER_BROWSER_ID_LENGTH 32
#define QL_STEAM_SERVER_BROWSER_STEAM_ID_LENGTH 32
#define QL_STEAM_SERVER_BROWSER_EVENT_NAME_LENGTH 64
#define QL_STEAM_SERVER_BROWSER_RULE_LENGTH 256
#define QL_STEAM_SERVER_BROWSER_RULE_VALUE_LENGTH 256
#define QL_STEAM_SERVER_BROWSER_PLAYER_NAME_LENGTH 64
#define QL_STEAM_SERVER_BROWSER_DETAIL_COMPLETION_TARGET 3
#define QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PING 0x01u
#define QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_RULES 0x02u
#define QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PLAYERS 0x04u
#define QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_ALL (QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PING | QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_RULES | QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PLAYERS)
#define QL_STEAM_SERVER_BROWSER_DETAIL_RULES_RESPONSE_OFFSET 0
#define QL_STEAM_SERVER_BROWSER_DETAIL_PLAYERS_RESPONSE_OFFSET 4
#define QL_STEAM_SERVER_BROWSER_DETAIL_PING_RESPONSE_OFFSET 8

typedef struct {
	uint32_t serverIp;
	uint16_t serverPort;
	uint16_t queryPort;
	int ping;
	char gameDir[QL_STEAM_SERVER_BROWSER_GAME_DIR_LENGTH];
	char map[QL_STEAM_SERVER_BROWSER_MAP_LENGTH];
	char gameDescription[QL_STEAM_SERVER_BROWSER_GAME_DESCRIPTION_LENGTH];
	uint32_t appId;
	int numPlayers;
	int maxPlayers;
	int botPlayers;
	qboolean passwordProtected;
	qboolean vacSecured;
	uint32_t lastPlayed;
	int serverVersion;
	char name[QL_STEAM_SERVER_BROWSER_NAME_LENGTH];
	char displayName[QL_STEAM_SERVER_BROWSER_DISPLAY_NAME_LENGTH];
	char tags[QL_STEAM_SERVER_BROWSER_TAGS_LENGTH];
	CSteamID steamId;
} ql_steam_server_item_t;

typedef struct {
	char id[QL_STEAM_SERVER_BROWSER_ID_LENGTH];
	char name[QL_STEAM_SERVER_BROWSER_DISPLAY_NAME_LENGTH];
	int numPlayers;
	int maxPlayers;
	int ping;
	char map[QL_STEAM_SERVER_BROWSER_MAP_LENGTH];
	int botPlayers;
	qboolean passwordProtected;
	qboolean vacSecured;
	uint32_t serverIp;
	uint16_t serverPort;
	char steamId[QL_STEAM_SERVER_BROWSER_STEAM_ID_LENGTH];
	char tags[QL_STEAM_SERVER_BROWSER_TAGS_LENGTH];
	char gametype[QL_STEAM_SERVER_BROWSER_GAME_DESCRIPTION_LENGTH];
	uint32_t lastPlayed;
} ql_steam_server_browser_response_t;

typedef struct {
	int id;
	char eventName[QL_STEAM_SERVER_BROWSER_EVENT_NAME_LENGTH];
} ql_steam_server_browser_failure_t;

typedef struct {
	char eventName[QL_STEAM_SERVER_BROWSER_EVENT_NAME_LENGTH];
} ql_steam_server_browser_refresh_complete_t;

typedef struct {
	uint32_t serverIp;
	uint16_t serverPort;
	char id[QL_STEAM_SERVER_BROWSER_ID_LENGTH];
} ql_steam_server_browser_detail_identity_t;

typedef struct {
	ql_steam_server_browser_detail_identity_t identity;
	char eventName[QL_STEAM_SERVER_BROWSER_EVENT_NAME_LENGTH];
} ql_steam_server_browser_detail_event_t;

typedef struct {
	ql_steam_server_browser_detail_identity_t identity;
	char eventName[QL_STEAM_SERVER_BROWSER_EVENT_NAME_LENGTH];
	char rule[QL_STEAM_SERVER_BROWSER_RULE_LENGTH];
	char value[QL_STEAM_SERVER_BROWSER_RULE_VALUE_LENGTH];
} ql_steam_server_browser_rule_response_t;

typedef struct {
	ql_steam_server_browser_detail_identity_t identity;
	char eventName[QL_STEAM_SERVER_BROWSER_EVENT_NAME_LENGTH];
	char name[QL_STEAM_SERVER_BROWSER_PLAYER_NAME_LENGTH];
	int score;
	int time;
} ql_steam_server_browser_player_response_t;

typedef struct {
	ql_steam_server_browser_detail_identity_t identity;
	int completedCallbacks;
	uint32_t completedTerminalChannels;
	qboolean releaseReady;
} ql_steam_server_browser_detail_lifecycle_t;

typedef struct {
	void *rulesResponse;
	void *playersResponse;
	void *pingResponse;
} ql_steam_server_browser_detail_response_views_t;

typedef struct {
	ql_steam_server_browser_detail_lifecycle_t lifecycle;
	void *detailObjectBase;
	ql_steam_server_query_t pingQuery;
	ql_steam_server_query_t playersQuery;
	ql_steam_server_query_t rulesQuery;
	qboolean queriesActive;
} ql_steam_server_browser_detail_request_t;

typedef struct {
	CSteamID steamId;
	int relationship;
	int personaState;
	char name[QL_STEAM_NAME_LENGTH];
	char nickname[QL_STEAM_NAME_LENGTH];
	char status[QL_STEAM_STATUS_LENGTH];
	char lanIp[64];
	qboolean playingQuake;
	uint32_t appId;
	uint64_t gameId;
	uint32_t serverIp;
	uint16_t serverPort;
	uint16_t queryPort;
	CSteamID lobbyId;
	CSteamID gameServerId;
} ql_steam_friend_summary_t;

typedef struct {
	ql_steam_friend_summary_t requester;
	char command[QL_STEAM_COMMAND_LENGTH];
} ql_steam_rich_presence_join_requested_t;

typedef struct {
	CSteamID steamId;
	uint32_t gameId;
	int result;
	char name[QL_STEAM_NAME_LENGTH];
} ql_steam_user_stats_received_t;

typedef struct {
	CSteamID steamId;
	uint32_t changeFlags;
	ql_steam_friend_summary_t summary;
} ql_steam_persona_state_change_t;

typedef struct {
	CSteamID remoteId;
} ql_steam_p2p_session_request_t;

typedef struct {
	char server[QL_STEAM_SERVER_LENGTH];
	char password[QL_STEAM_PASSWORD_LENGTH];
} ql_steam_game_server_change_requested_t;

typedef struct {
	CSteamID steamId;
	uint32_t appId;
	ql_steam_friend_summary_t summary;
} ql_steam_friend_rich_presence_update_t;

typedef struct {
	CSteamID steamId;
	int image;
	int width;
	int height;
} ql_steam_avatar_image_loaded_t;

typedef struct {
	SteamAPICall_t callHandle;
	uint64_t queryHandle;
	int result;
	uint32_t numResultsReturned;
	uint32_t totalMatchingResults;
	qboolean cachedData;
} ql_steam_ugc_query_completed_t;

typedef struct {
	uint32_t appId;
	uint32_t itemIdLow;
	uint32_t itemIdHigh;
} ql_steam_item_installed_t;

typedef struct {
	uint32_t appId;
	uint32_t itemIdLow;
	uint32_t itemIdHigh;
	int result;
} ql_steam_download_item_result_t;

typedef struct {
	CSteamID lobbyId;
	int result;
} ql_steam_lobby_created_t;

typedef struct {
	CSteamID lobbyId;
	uint32_t permissions;
	qboolean locked;
	uint32_t chatPermissions;
	int response;
} ql_steam_lobby_enter_t;

typedef struct {
	CSteamID lobbyId;
	CSteamID changedUser;
	CSteamID makingChangeUser;
	uint32_t stateChange;
} ql_steam_lobby_chat_update_t;

typedef struct {
	CSteamID lobbyId;
	CSteamID chatter;
	int chatEntryType;
	int chatId;
	char message[QL_STEAM_LOBBY_MESSAGE_LENGTH];
} ql_steam_lobby_chat_message_t;

typedef struct {
	CSteamID lobbyId;
	CSteamID memberId;
	qboolean success;
} ql_steam_lobby_data_update_t;

typedef struct {
	CSteamID lobbyId;
	CSteamID serverId;
	uint32_t serverIp;
	uint16_t serverPort;
} ql_steam_lobby_game_created_t;

typedef struct {
	CSteamID lobbyId;
	CSteamID adminId;
	qboolean disconnected;
} ql_steam_lobby_kicked_t;

typedef struct {
	CSteamID lobbyId;
	CSteamID friendId;
} ql_steam_game_lobby_join_requested_t;

typedef struct {
	uint32_t appId;
	uint64_t orderId;
	qboolean authorized;
} ql_steam_microtxn_authorization_response_t;

typedef enum {
	k_EAuthSessionResponseOK = 0,
	k_EAuthSessionResponseUserNotConnectedToSteam = 1,
	k_EAuthSessionResponseNoLicenseOrExpired = 2,
	k_EAuthSessionResponseVACBanned = 3,
	k_EAuthSessionResponseLoggedInElseWhere = 4,
	k_EAuthSessionResponseVACCheckTimedOut = 5,
	k_EAuthSessionResponseAuthTicketCanceled = 6,
	k_EAuthSessionResponseAuthTicketInvalidAlreadyUsed = 7,
	k_EAuthSessionResponseAuthTicketInvalid = 8,
	k_EAuthSessionResponsePublisherIssuedBan = 9
} EAuthSessionResponse;

typedef struct {
	uint8_t reserved;
} ql_steam_server_connected_t;

typedef struct {
	int result;
	qboolean stillRetrying;
} ql_steam_server_connect_failure_t;

typedef struct {
	int result;
} ql_steam_server_disconnected_t;

typedef struct {
	int result;
	CSteamID steamId;
} ql_steam_gs_stats_received_t;

typedef struct {
	int result;
	CSteamID steamId;
} ql_steam_gs_stats_stored_t;

typedef struct {
	CSteamID steamId;
	CSteamID ownerSteamId;
	EAuthSessionResponse authSessionResponse;
} ql_steam_validate_auth_ticket_response_t;

typedef struct {
	void *context;
	void (*onRichPresenceJoinRequested)( void *context, const ql_steam_rich_presence_join_requested_t *event );
	void (*onUserStatsReceived)( void *context, const ql_steam_user_stats_received_t *event );
	void (*onPersonaStateChange)( void *context, const ql_steam_persona_state_change_t *event );
	void (*onP2PSessionRequest)( void *context, const ql_steam_p2p_session_request_t *event );
	void (*onGameServerChangeRequested)( void *context, const ql_steam_game_server_change_requested_t *event );
	void (*onFriendRichPresenceUpdate)( void *context, const ql_steam_friend_rich_presence_update_t *event );
	void (*onUGCQueryCompleted)( void *context, const ql_steam_ugc_query_completed_t *event );
} ql_steam_client_callback_bindings_t;

typedef struct {
	void *context;
	void (*onAvatarImageLoaded)( void *context, const ql_steam_avatar_image_loaded_t *event );
} ql_steam_avatar_callback_bindings_t;

typedef struct {
	void *context;
	void (*onLobbyCreated)( void *context, const ql_steam_lobby_created_t *event );
	void (*onLobbyEnter)( void *context, const ql_steam_lobby_enter_t *event );
	void (*onLobbyChatUpdate)( void *context, const ql_steam_lobby_chat_update_t *event );
	void (*onLobbyChatMessage)( void *context, const ql_steam_lobby_chat_message_t *event );
	void (*onLobbyDataUpdate)( void *context, const ql_steam_lobby_data_update_t *event );
	void (*onLobbyGameCreated)( void *context, const ql_steam_lobby_game_created_t *event );
	void (*onLobbyKicked)( void *context, const ql_steam_lobby_kicked_t *event );
	void (*onGameLobbyJoinRequested)( void *context, const ql_steam_game_lobby_join_requested_t *event );
} ql_steam_lobby_callback_bindings_t;

typedef struct {
	void *context;
	void (*onAuthorizationResponse)( void *context, const ql_steam_microtxn_authorization_response_t *event );
} ql_steam_micro_callback_bindings_t;

typedef struct {
	void *context;
	void (*onItemInstalled)( void *context, const ql_steam_item_installed_t *event );
	void (*onDownloadItemResult)( void *context, const ql_steam_download_item_result_t *event );
} ql_steam_workshop_callback_bindings_t;

typedef struct {
	void *context;
	void (*onServersConnected)( void *context, const ql_steam_server_connected_t *event );
	void (*onConnectFailure)( void *context, const ql_steam_server_connect_failure_t *event );
	void (*onServersDisconnected)( void *context, const ql_steam_server_disconnected_t *event );
	void (*onValidateAuthTicketResponse)( void *context, const ql_steam_validate_auth_ticket_response_t *event );
	void (*onP2PSessionRequest)( void *context, const ql_steam_p2p_session_request_t *event );
	void (*onGSStatsReceived)( void *context, const ql_steam_gs_stats_received_t *event );
	void (*onGSStatsStored)( void *context, const ql_steam_gs_stats_stored_t *event );
} ql_steam_server_callback_bindings_t;

#if QL_BUILD_STEAMWORKS

#include "platform_backend_shared.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t HAuthTicket;

typedef enum {
	k_EBeginAuthSessionResultOK = 0,
	k_EBeginAuthSessionResultInvalidTicket = 1,
	k_EBeginAuthSessionResultDuplicateRequest = 2,
	k_EBeginAuthSessionResultInvalidVersion = 3,
	k_EBeginAuthSessionResultGameMismatch = 4,
	k_EBeginAuthSessionResultExpiredTicket = 5
} EBeginAuthSessionResult;

qboolean QL_Steamworks_LoadLibrary( void );

void QL_Steamworks_UnloadLibrary( void );

qboolean QL_Steamworks_Init( void );

qboolean QL_Steamworks_IsInitialized( void );

void QL_Steamworks_Shutdown( void );

void QL_Steamworks_RunCallbacks( void );

void QL_Steamworks_RunServerCallbacks( void );

qboolean QL_Steamworks_ServerInitWithVersion( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated, const char *version );

qboolean QL_Steamworks_ServerInit( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated );

void QL_Steamworks_ServerShutdown( void );

qboolean QL_Steamworks_ServerIsInitialised( void );

qboolean QL_Steamworks_ServerEnableHeartbeats( qboolean enable );

qboolean QL_Steamworks_ServerSetDedicated( qboolean dedicated );

qboolean QL_Steamworks_ServerLogOn( const char *account );

qboolean QL_Steamworks_ServerSetProduct( const char *product );

qboolean QL_Steamworks_ServerSetGameDir( const char *gameDir );

qboolean QL_Steamworks_ServerSetGameDescription( const char *description );

qboolean QL_Steamworks_ServerSetMaxPlayerCount( int maxPlayers );

qboolean QL_Steamworks_ServerSetBotPlayerCount( int botPlayers );

qboolean QL_Steamworks_ServerSetServerName( const char *name );

qboolean QL_Steamworks_ServerSetMapName( const char *mapName );

qboolean QL_Steamworks_ServerSetPasswordProtected( qboolean passwordProtected );

qboolean QL_Steamworks_ServerGetSteamID( uint32_t *outIdLow, uint32_t *outIdHigh );

qboolean QL_Steamworks_ServerCreateUnauthenticatedUserConnection( uint32_t *outIdLow, uint32_t *outIdHigh );

qboolean QL_Steamworks_ServerSetGameTags( const char *tags );

qboolean QL_Steamworks_ServerSetKeyValue( const char *key, const char *value );

qboolean QL_Steamworks_ServerSetKeyValuesFromInfoString( const char *infoString );

qboolean QL_Steamworks_ServerUpdateUserData( const CSteamID *steamId, const char *playerName, uint32_t score );

uint32_t QL_Steamworks_ServerGetPublicIP( void );

qboolean QL_Steamworks_ClearStats( qboolean achievementsToo );

qboolean QL_Steamworks_GetPersonaName( char *buffer, size_t bufferSize );

qboolean QL_Steamworks_GetIPCountry( char *buffer, size_t bufferSize );

uint32_t QL_Steamworks_GetAppID( void );

qboolean QL_Steamworks_GetUserSteamID( uint32_t *outIdLow, uint32_t *outIdHigh );

qboolean QL_Steamworks_SetInGameVoiceSpeaking( uint32_t idLow, uint32_t idHigh, qboolean speaking );

int QL_Steamworks_GetFriendCount( int flags );

qboolean QL_Steamworks_GetFriendByIndex( int index, int flags, uint32_t *outIdLow, uint32_t *outIdHigh );

qboolean QL_Steamworks_GetFriendSummary( uint32_t idLow, uint32_t idHigh, ql_steam_friend_summary_t *outSummary );

const char *QL_Steamworks_GetP2PTransportLabel( void );

const char *QL_Steamworks_GetP2PModernGapLabel( void );

qboolean QL_Steamworks_SendP2PPacket( const CSteamID *steamId, const void *data, uint32_t length, int sendType, int channel );

qboolean QL_Steamworks_IsP2PPacketAvailable( uint32_t *outSize, int channel );

qboolean QL_Steamworks_ReadP2PPacket( void *data, uint32_t dataSize, uint32_t *outSize, CSteamID *outSteamId, int channel );

qboolean QL_Steamworks_AcceptP2PSession( const CSteamID *steamId );

qboolean QL_Steamworks_StartVoiceRecording( void );

qboolean QL_Steamworks_StopVoiceRecording( void );

qboolean QL_Steamworks_GetCompressedVoice( void *data, uint32_t dataSize, uint32_t *outSize );

qboolean QL_Steamworks_DecompressVoice( const void *compressedData, uint32_t compressedSize, void *data, uint32_t dataSize, uint32_t *outSize, uint32_t sampleRate );

uint32_t QL_Steamworks_GetVoiceOptimalSampleRate( void );

qboolean QL_Steamworks_ServerSendP2PPacket( const CSteamID *steamId, const void *data, uint32_t length, int sendType, int channel );

qboolean QL_Steamworks_ServerIsP2PPacketAvailable( uint32_t *outSize, int channel );

qboolean QL_Steamworks_ServerReadP2PPacket( void *data, uint32_t dataSize, uint32_t *outSize, CSteamID *outSteamId, int channel );

qboolean QL_Steamworks_ServerHandleIncomingPacket( const void *data, int dataSize, uint32_t ip, uint16_t port );

int QL_Steamworks_ServerGetNextOutgoingPacket( void *data, int dataSize, uint32_t *outIp, uint16_t *outPort );

qboolean QL_Steamworks_ServerAcceptP2PSession( const CSteamID *steamId );

qboolean QL_Steamworks_HexEncode( const uint8_t *data, uint32_t length, char *out, size_t outSize );

qboolean QL_Steamworks_HexDecode( const char *hex, uint8_t *out, size_t outSize, uint32_t *outLength );

const char *QL_Steamworks_GetAuthTicketApiLabel( void );

const char *QL_Steamworks_GetAuthTicketModernGapLabel( void );

qboolean QL_Steamworks_IsUserLoggedOn( void );

const char *QL_Steamworks_GetWebApiAuthTicketIdentity( void );

qboolean QL_Steamworks_HasWebApiAuthTicketAdapter( void );

qboolean QL_Steamworks_RequestWebApiAuthTicket( const char *identity, char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle, int *steamResult );

qboolean QL_Steamworks_RequestAuthTicket( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle );

qboolean QL_Steamworks_CancelAuthTicket( uint32_t ticketHandle );

qboolean QL_Steamworks_ServerBeginAuthSession( const CSteamID *steamId, const char *ticketHex, ql_auth_response_t *response );

void QL_Steamworks_ServerEndAuthSession( const CSteamID *steamId );

qboolean QL_Steamworks_ValidateTicket( const char *ticketHex, ql_auth_response_t *response );

qboolean QL_Steamworks_IsSubscribedApp( uint32_t appId );

qboolean QL_Steamworks_HasUGCInterface( void );

uint32_t QL_Steamworks_GetNumSubscribedItems( void );

uint32_t QL_Steamworks_GetSubscribedItems( uint64_t *outItemIds, uint32_t maxItems );

qboolean QL_Steamworks_GetItemInstallInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outSizeOnDisk, char *folder, size_t folderSize, uint32_t *outTimestamp );

qboolean QL_Steamworks_GetItemDownloadInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outDownloaded, uint64_t *outTotal );

qboolean QL_Steamworks_ActivateOverlayToUser( const char *dialog, uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_ActivateOverlayToWebPage( const char *url );

qboolean QL_Steamworks_SetRichPresence( const char *key, const char *value );

qboolean QL_Steamworks_CreateLobby( int maxMembers );

qboolean QL_Steamworks_SetFavoriteServerForApp( uint32_t serverIp, uint16_t serverPort, uint32_t appId, qboolean add );

qboolean QL_Steamworks_SetFavoriteServer( uint32_t serverIp, uint16_t serverPort, qboolean add );

qboolean QL_Steamworks_LeaveLobby( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_JoinLobby( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_GetLobbyOwner( uint32_t idLow, uint32_t idHigh, uint32_t *outIdLow, uint32_t *outIdHigh );

int QL_Steamworks_GetLobbyDataCount( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_SetLobbyData( uint32_t idLow, uint32_t idHigh, const char *key, const char *value );

qboolean QL_Steamworks_GetLobbyDataByIndex( uint32_t idLow, uint32_t idHigh, int index, char *key, size_t keySize, char *value, size_t valueSize );

int QL_Steamworks_GetNumLobbyMembers( uint32_t idLow, uint32_t idHigh );

int QL_Steamworks_GetLobbyMemberLimit( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_GetLobbyMemberByIndex( uint32_t idLow, uint32_t idHigh, int index, uint32_t *outIdLow, uint32_t *outIdHigh );

qboolean QL_Steamworks_GetFriendPersonaName( uint32_t idLow, uint32_t idHigh, char *buffer, size_t bufferSize );

qboolean QL_Steamworks_SetLobbyServer( uint32_t idLow, uint32_t idHigh, uint32_t serverIp, uint16_t serverPort );

qboolean QL_Steamworks_ShowInviteOverlay( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_InviteUserToLobby( uint32_t lobbyIdLow, uint32_t lobbyIdHigh, uint32_t userIdLow, uint32_t userIdHigh );

qboolean QL_Steamworks_InviteUserToGame( uint32_t idLow, uint32_t idHigh, const char *connectString );

qboolean QL_Steamworks_SayLobby( uint32_t idLow, uint32_t idHigh, const char *message );

qboolean QL_Steamworks_RequestUserStats( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_GetUserStatInt( uint32_t idLow, uint32_t idHigh, const char *name, int *outValue );

qboolean QL_Steamworks_GetUserStatFloat( uint32_t idLow, uint32_t idHigh, const char *name, float *outValue );

qboolean QL_Steamworks_GetUserAchievement( uint32_t idLow, uint32_t idHigh, const char *name, qboolean *outAchieved, int *outUnlockTime );

const char *QL_Steamworks_GetAchievementDisplayAttribute( const char *name, const char *key );

qboolean QL_Steamworks_HasServerBrowserInterface( void );

const char *QL_Steamworks_GetServerBrowserAdapterLabel( void );

const char *QL_Steamworks_GetServerBrowserIntegrationGapLabel( void );

const char *QL_Steamworks_GetServerBrowserRequestModeLabel( ql_steam_server_browser_request_mode_t requestMode );

qboolean QL_Steamworks_ServerBrowserRequestModeUsesGamedirFilter( ql_steam_server_browser_request_mode_t requestMode );

void QL_Steamworks_InitServerBrowserOwner( ql_steam_server_browser_owner_t *owner );

qboolean QL_Steamworks_BeginServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner, ql_steam_server_browser_request_mode_t requestMode, void *responseObject );

qboolean QL_Steamworks_BeginServerBrowserOwnerRequestForApp( ql_steam_server_browser_owner_t *owner, ql_steam_server_browser_request_mode_t requestMode, uint32_t appId, void *responseObject );

qboolean QL_Steamworks_RefreshServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner );

qboolean QL_Steamworks_CompleteServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner );

ql_steam_server_list_request_t QL_Steamworks_RequestServerList( ql_steam_server_browser_request_mode_t requestMode, void *responseObject );

ql_steam_server_list_request_t QL_Steamworks_RequestServerListForApp( ql_steam_server_browser_request_mode_t requestMode, uint32_t appId, void *responseObject );

const void *QL_Steamworks_GetServerListDetails( ql_steam_server_list_request_t request, int index );

qboolean QL_Steamworks_ReadServerListDetails( ql_steam_server_list_request_t request, int index, ql_steam_server_item_t *outServer );

qboolean QL_Steamworks_ReadServerListDetailsForApp( ql_steam_server_list_request_t request, int index, uint32_t appId, ql_steam_server_item_t *outServer );

void QL_Steamworks_FormatServerBrowserResponseId( uint32_t serverIp, uint16_t serverPort, char *buffer, size_t bufferSize );

qboolean QL_Steamworks_BuildServerBrowserResponse( const ql_steam_server_item_t *server, ql_steam_server_browser_response_t *outResponse );

qboolean QL_Steamworks_ReadServerBrowserResponse( ql_steam_server_list_request_t request, int index, ql_steam_server_browser_response_t *outResponse );

qboolean QL_Steamworks_ReadServerBrowserResponseForApp( ql_steam_server_list_request_t request, int index, uint32_t appId, ql_steam_server_browser_response_t *outResponse );

qboolean QL_Steamworks_ReadServerBrowserPingResponse( const void *serverDetails, ql_steam_server_browser_response_t *outResponse );

qboolean QL_Steamworks_ReadServerBrowserPingResponseForApp( const void *serverDetails, uint32_t appId, ql_steam_server_browser_response_t *outResponse );

void QL_Steamworks_FormatServerBrowserFailureEventName( int serverIndex, char *buffer, size_t bufferSize );

qboolean QL_Steamworks_BuildServerBrowserFailure( int serverIndex, ql_steam_server_browser_failure_t *outFailure );

qboolean QL_Steamworks_BuildServerBrowserRefreshComplete( ql_steam_server_browser_refresh_complete_t *outRefresh );

void QL_Steamworks_FormatServerBrowserDetailId( uint32_t serverIp, uint16_t serverPort, char *buffer, size_t bufferSize );

qboolean QL_Steamworks_BuildServerBrowserDetailIdentity( uint32_t serverIp, uint16_t serverPort, ql_steam_server_browser_detail_identity_t *outIdentity );

qboolean QL_Steamworks_FormatServerBrowserDetailEventName( ql_steam_server_browser_detail_channel_t channel, ql_steam_server_browser_detail_phase_t phase, const char *detailId, char *buffer, size_t bufferSize );

qboolean QL_Steamworks_BuildServerBrowserDetailEvent( const ql_steam_server_browser_detail_identity_t *identity, ql_steam_server_browser_detail_channel_t channel, ql_steam_server_browser_detail_phase_t phase, ql_steam_server_browser_detail_event_t *outEvent );

qboolean QL_Steamworks_BuildServerBrowserRuleResponse( const ql_steam_server_browser_detail_identity_t *identity, const char *rule, const char *value, ql_steam_server_browser_rule_response_t *outResponse );

qboolean QL_Steamworks_BuildServerBrowserPlayerResponse( const ql_steam_server_browser_detail_identity_t *identity, const char *name, int score, int time, ql_steam_server_browser_player_response_t *outResponse );

qboolean QL_Steamworks_InitServerBrowserDetailLifecycle( uint32_t serverIp, uint16_t serverPort, ql_steam_server_browser_detail_lifecycle_t *outLifecycle );

qboolean QL_Steamworks_CompleteServerBrowserDetailCallback( ql_steam_server_browser_detail_lifecycle_t *lifecycle, qboolean *outReleaseReady );

qboolean QL_Steamworks_CompleteServerBrowserDetailTerminal( ql_steam_server_browser_detail_lifecycle_t *lifecycle, uint32_t terminalChannel, qboolean *outReleaseReady );

qboolean QL_Steamworks_BuildServerBrowserDetailResponseViews( void *detailObjectBase, ql_steam_server_browser_detail_response_views_t *outViews );

void QL_Steamworks_InitServerBrowserDetailRequest( ql_steam_server_browser_detail_request_t *request );

qboolean QL_Steamworks_BeginServerBrowserDetailRequest( ql_steam_server_browser_detail_request_t *request, uint32_t serverIp, uint16_t serverPort, void *detailObjectBase );

qboolean QL_Steamworks_CompleteServerBrowserDetailRequestCallback( ql_steam_server_browser_detail_request_t *request, qboolean *outReleaseReady );

qboolean QL_Steamworks_CompleteServerBrowserDetailRequestTerminal( ql_steam_server_browser_detail_request_t *request, uint32_t terminalChannel, qboolean *outReleaseReady );

void QL_Steamworks_ReleaseServerListRequest( ql_steam_server_list_request_t request );

void QL_Steamworks_RefreshServerListRequest( ql_steam_server_list_request_t request );

qboolean QL_Steamworks_RequestServerDetails( uint32_t serverIp, uint16_t serverPort, void *pingResponse, void *playersResponse, void *rulesResponse, ql_steam_server_query_t *outPingQuery, ql_steam_server_query_t *outPlayersQuery, ql_steam_server_query_t *outRulesQuery );

void QL_Steamworks_CancelServerQuery( ql_steam_server_query_t query );

uint32_t QL_Steamworks_ServerGetAppID( void );

qboolean QL_Steamworks_ServerIsLoggedOn( void );

qboolean QL_Steamworks_ServerRequestUserStats( const CSteamID *steamId );

qboolean QL_Steamworks_ServerGetUserStatInt( const CSteamID *steamId, const char *name, int *outValue );

qboolean QL_Steamworks_ServerGetUserStatFloat( const CSteamID *steamId, const char *name, float *outValue );

qboolean QL_Steamworks_ServerGetUserAchievement( const CSteamID *steamId, const char *name, qboolean *outAchieved );

qboolean QL_Steamworks_ServerSetUserStatInt( const CSteamID *steamId, const char *name, int value );

qboolean QL_Steamworks_ServerSetUserStatFloat( const CSteamID *steamId, const char *name, float value );

qboolean QL_Steamworks_ServerUpdateAvgRateStat( const CSteamID *steamId, const char *name, float countThisSession, double sessionLength );

qboolean QL_Steamworks_ServerSetUserAchievement( const CSteamID *steamId, const char *name );

qboolean QL_Steamworks_ServerStoreUserStats( const CSteamID *steamId );

uint32_t QL_Steamworks_GetItemState( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_SubscribeItem( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_UnsubscribeItem( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_DownloadItem( uint32_t idLow, uint32_t idHigh, qboolean highPriority );

const char *QL_Steamworks_GetAllUGCFilterContractLabel( void );

const char *QL_Steamworks_GetAllUGCFilterSemanticGapLabel( void );

qboolean QL_Steamworks_RequestAllUGCQuery( uint32_t filter );

qboolean QL_Steamworks_GetQueryUGCResult( uint64_t queryHandle, uint32_t index, uint64_t *outPublishedFileId, char *title, size_t titleSize, char *description, size_t descriptionSize );

qboolean QL_Steamworks_GetQueryUGCPreviewURL( uint64_t queryHandle, uint32_t index, char *buffer, size_t bufferSize );

void QL_Steamworks_ReleaseQueryUGCRequest( uint64_t queryHandle );

ql_steam_avatar_image_state_t QL_Steamworks_RequestAvatarImage( uint32_t idLow, uint32_t idHigh, ql_steam_avatar_size_t size, int *outImage );

qboolean QL_Steamworks_LoadAvatarRGBA( uint32_t idLow, uint32_t idHigh, ql_steam_avatar_size_t size, uint8_t **outPixels, uint32_t *outWidth, uint32_t *outHeight );

qboolean QL_Steamworks_RegisterAvatarCallbacks( const ql_steam_avatar_callback_bindings_t *bindings );

void QL_Steamworks_UnregisterAvatarCallbacks( void );

qboolean QL_Steamworks_RegisterClientCallbacks( const ql_steam_client_callback_bindings_t *bindings );

void QL_Steamworks_UnregisterClientCallbacks( void );

qboolean QL_Steamworks_RegisterServerCallbacks( const ql_steam_server_callback_bindings_t *bindings );

void QL_Steamworks_UnregisterServerCallbacks( void );

qboolean QL_Steamworks_RegisterLobbyCallbacks( const ql_steam_lobby_callback_bindings_t *bindings );

void QL_Steamworks_UnregisterLobbyCallbacks( void );

qboolean QL_Steamworks_RegisterMicroCallbacks( const ql_steam_micro_callback_bindings_t *bindings );

void QL_Steamworks_UnregisterMicroCallbacks( void );

qboolean QL_Steamworks_RegisterWorkshopCallbacks( const ql_steam_workshop_callback_bindings_t *bindings );

void QL_Steamworks_UnregisterWorkshopCallbacks( void );

qboolean QL_Steamworks_BindUGCQueryCallResult( SteamAPICall_t callHandle );

void QL_Steamworks_FreeBuffer( void *buffer );

#ifdef __cplusplus
}
#endif

#else

/*
=============
QL_Steamworks_LoadLibrary
=============
*/
static inline qboolean QL_Steamworks_LoadLibrary( void ) {
	return qfalse;
}

/*
=============
QL_Steamworks_UnloadLibrary
=============
*/
static inline void QL_Steamworks_UnloadLibrary( void ) {
}

/*
=============
QL_Steamworks_Init
=============
*/
static inline qboolean QL_Steamworks_Init( void ) {
	return qfalse;
}

/*
=============
QL_Steamworks_IsInitialized
=============
*/
static inline qboolean QL_Steamworks_IsInitialized( void ) {
	return qfalse;
}

/*
=============
QL_Steamworks_Shutdown
=============
*/
static inline void QL_Steamworks_Shutdown( void ) {
}

/*
=============
QL_Steamworks_RunCallbacks
=============
*/
static inline void QL_Steamworks_RunCallbacks( void ) {
}

/*
=============
QL_Steamworks_RunServerCallbacks
=============
*/
static inline void QL_Steamworks_RunServerCallbacks( void ) {
}

/*
=============
QL_Steamworks_ServerInitWithVersion
=============
*/
static inline qboolean QL_Steamworks_ServerInitWithVersion( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated, const char *version ) {
	(void)ip;
	(void)gamePort;
	(void)secure;
	(void)dedicated;
	(void)version;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerInit
=============
*/
static inline qboolean QL_Steamworks_ServerInit( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated ) {
	return QL_Steamworks_ServerInitWithVersion( ip, gamePort, secure, dedicated, QL_STEAM_GAMESERVER_DEFAULT_VERSION );
}

/*
=============
QL_Steamworks_ServerShutdown
=============
*/
static inline void QL_Steamworks_ServerShutdown( void ) {
}

/*
=============
QL_Steamworks_ServerIsInitialised
=============
*/
static inline qboolean QL_Steamworks_ServerIsInitialised( void ) {
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetDedicated
=============
*/
static inline qboolean QL_Steamworks_ServerSetDedicated( qboolean dedicated ) {
	(void)dedicated;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerLogOn
=============
*/
static inline qboolean QL_Steamworks_ServerLogOn( const char *account ) {
	(void)account;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetProduct
=============
*/
static inline qboolean QL_Steamworks_ServerSetProduct( const char *product ) {
	(void)product;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetGameDir
=============
*/
static inline qboolean QL_Steamworks_ServerSetGameDir( const char *gameDir ) {
	(void)gameDir;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetGameDescription
=============
*/
static inline qboolean QL_Steamworks_ServerSetGameDescription( const char *description ) {
	(void)description;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetMaxPlayerCount
=============
*/
static inline qboolean QL_Steamworks_ServerSetMaxPlayerCount( int maxPlayers ) {
	(void)maxPlayers;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetBotPlayerCount
=============
*/
static inline qboolean QL_Steamworks_ServerSetBotPlayerCount( int botPlayers ) {
	(void)botPlayers;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetServerName
=============
*/
static inline qboolean QL_Steamworks_ServerSetServerName( const char *name ) {
	(void)name;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetMapName
=============
*/
static inline qboolean QL_Steamworks_ServerSetMapName( const char *mapName ) {
	(void)mapName;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetPasswordProtected
=============
*/
static inline qboolean QL_Steamworks_ServerSetPasswordProtected( qboolean passwordProtected ) {
	(void)passwordProtected;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerEnableHeartbeats
=============
*/
static inline qboolean QL_Steamworks_ServerEnableHeartbeats( qboolean enable ) {
	(void)enable;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerGetSteamID
=============
*/
static inline qboolean QL_Steamworks_ServerGetSteamID( uint32_t *outIdLow, uint32_t *outIdHigh ) {
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
QL_Steamworks_ServerCreateUnauthenticatedUserConnection
=============
*/
static inline qboolean QL_Steamworks_ServerCreateUnauthenticatedUserConnection( uint32_t *outIdLow, uint32_t *outIdHigh ) {
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
QL_Steamworks_ServerSetGameTags
=============
*/
static inline qboolean QL_Steamworks_ServerSetGameTags( const char *tags ) {
	(void)tags;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetKeyValue
=============
*/
static inline qboolean QL_Steamworks_ServerSetKeyValue( const char *key, const char *value ) {
	(void)key;
	(void)value;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetKeyValuesFromInfoString
=============
*/
static inline qboolean QL_Steamworks_ServerSetKeyValuesFromInfoString( const char *infoString ) {
	(void)infoString;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerUpdateUserData
=============
*/
static inline qboolean QL_Steamworks_ServerUpdateUserData( const CSteamID *steamId, const char *playerName, uint32_t score ) {
	(void)steamId;
	(void)playerName;
	(void)score;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerGetPublicIP
=============
*/
static inline uint32_t QL_Steamworks_ServerGetPublicIP( void ) {
	return 0u;
}

/*
=============
QL_Steamworks_ClearStats
=============
*/
static inline qboolean QL_Steamworks_ClearStats( qboolean achievementsToo ) {
	(void)achievementsToo;
	return qfalse;
}

/*
=============
QL_Steamworks_GetPersonaName
=============
*/
static inline qboolean QL_Steamworks_GetPersonaName( char *buffer, size_t bufferSize ) {
	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
	return qfalse;
}

/*
=============
QL_Steamworks_GetIPCountry
=============
*/
static inline qboolean QL_Steamworks_GetIPCountry( char *buffer, size_t bufferSize ) {
	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
	return qfalse;
}

/*
=============
QL_Steamworks_GetAppID
=============
*/
static inline uint32_t QL_Steamworks_GetAppID( void ) {
	return 0u;
}

/*
=============
QL_Steamworks_GetUserSteamID
=============
*/
static inline qboolean QL_Steamworks_GetUserSteamID( uint32_t *outIdLow, uint32_t *outIdHigh ) {
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
QL_Steamworks_SetInGameVoiceSpeaking
=============
*/
static inline qboolean QL_Steamworks_SetInGameVoiceSpeaking( uint32_t idLow, uint32_t idHigh, qboolean speaking ) {
	(void)idLow;
	(void)idHigh;
	(void)speaking;
	return qfalse;
}

/*
=============
QL_Steamworks_GetFriendCount
=============
*/
static inline int QL_Steamworks_GetFriendCount( int flags ) {
	(void)flags;
	return 0;
}

/*
=============
QL_Steamworks_GetFriendByIndex
=============
*/
static inline qboolean QL_Steamworks_GetFriendByIndex( int index, int flags, uint32_t *outIdLow, uint32_t *outIdHigh ) {
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
QL_Steamworks_GetFriendSummary
=============
*/
static inline qboolean QL_Steamworks_GetFriendSummary( uint32_t idLow, uint32_t idHigh, ql_steam_friend_summary_t *outSummary ) {
	(void)idLow;
	(void)idHigh;
	if ( outSummary ) {
		memset( outSummary, 0, sizeof( *outSummary ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_SetRichPresence
=============
*/
static inline qboolean QL_Steamworks_SetRichPresence( const char *key, const char *value ) {
	(void)key;
	(void)value;
	return qfalse;
}

/*
=============
QL_Steamworks_GetP2PTransportLabel
=============
*/
static inline const char *QL_Steamworks_GetP2PTransportLabel( void ) {
	return "unavailable";
}

/*
=============
QL_Steamworks_GetP2PModernGapLabel
=============
*/
static inline const char *QL_Steamworks_GetP2PModernGapLabel( void ) {
	return "unavailable";
}

/*
=============
QL_Steamworks_SendP2PPacket
=============
*/
static inline qboolean QL_Steamworks_SendP2PPacket( const CSteamID *steamId, const void *data, uint32_t length, int sendType, int channel ) {
	(void)steamId;
	(void)data;
	(void)length;
	(void)sendType;
	(void)channel;
	return qfalse;
}

/*
=============
QL_Steamworks_IsP2PPacketAvailable
=============
*/
static inline qboolean QL_Steamworks_IsP2PPacketAvailable( uint32_t *outSize, int channel ) {
	(void)outSize;
	(void)channel;
	return qfalse;
}

/*
=============
QL_Steamworks_ReadP2PPacket
=============
*/
static inline qboolean QL_Steamworks_ReadP2PPacket( void *data, uint32_t dataSize, uint32_t *outSize, CSteamID *outSteamId, int channel ) {
	(void)data;
	(void)dataSize;
	(void)outSize;
	(void)outSteamId;
	(void)channel;
	return qfalse;
}

/*
=============
QL_Steamworks_AcceptP2PSession
=============
*/
static inline qboolean QL_Steamworks_AcceptP2PSession( const CSteamID *steamId ) {
	(void)steamId;
	return qfalse;
}

/*
=============
QL_Steamworks_StartVoiceRecording
=============
*/
static inline qboolean QL_Steamworks_StartVoiceRecording( void ) {
	return qfalse;
}

/*
=============
QL_Steamworks_StopVoiceRecording
=============
*/
static inline qboolean QL_Steamworks_StopVoiceRecording( void ) {
	return qfalse;
}

/*
=============
QL_Steamworks_GetCompressedVoice
=============
*/
static inline qboolean QL_Steamworks_GetCompressedVoice( void *data, uint32_t dataSize, uint32_t *outSize ) {
	(void)data;
	(void)dataSize;
	(void)outSize;
	return qfalse;
}

/*
=============
QL_Steamworks_DecompressVoice
=============
*/
static inline qboolean QL_Steamworks_DecompressVoice( const void *compressedData, uint32_t compressedSize, void *data, uint32_t dataSize, uint32_t *outSize, uint32_t sampleRate ) {
	(void)compressedData;
	(void)compressedSize;
	(void)data;
	(void)dataSize;
	(void)outSize;
	(void)sampleRate;
	return qfalse;
}

/*
=============
QL_Steamworks_GetVoiceOptimalSampleRate
=============
*/
static inline uint32_t QL_Steamworks_GetVoiceOptimalSampleRate( void ) {
	return 0u;
}

/*
=============
QL_Steamworks_ServerSendP2PPacket
=============
*/
static inline qboolean QL_Steamworks_ServerSendP2PPacket( const CSteamID *steamId, const void *data, uint32_t length, int sendType, int channel ) {
	(void)steamId;
	(void)data;
	(void)length;
	(void)sendType;
	(void)channel;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerIsP2PPacketAvailable
=============
*/
static inline qboolean QL_Steamworks_ServerIsP2PPacketAvailable( uint32_t *outSize, int channel ) {
	(void)outSize;
	(void)channel;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerReadP2PPacket
=============
*/
static inline qboolean QL_Steamworks_ServerReadP2PPacket( void *data, uint32_t dataSize, uint32_t *outSize, CSteamID *outSteamId, int channel ) {
	(void)data;
	(void)dataSize;
	(void)outSize;
	(void)outSteamId;
	(void)channel;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerHandleIncomingPacket
=============
*/
static inline qboolean QL_Steamworks_ServerHandleIncomingPacket( const void *data, int dataSize, uint32_t ip, uint16_t port ) {
	(void)data;
	(void)dataSize;
	(void)ip;
	(void)port;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerGetNextOutgoingPacket
=============
*/
static inline int QL_Steamworks_ServerGetNextOutgoingPacket( void *data, int dataSize, uint32_t *outIp, uint16_t *outPort ) {
	(void)data;
	(void)dataSize;
	(void)outIp;
	(void)outPort;
	return 0;
}

/*
=============
QL_Steamworks_ServerAcceptP2PSession
=============
*/
static inline qboolean QL_Steamworks_ServerAcceptP2PSession( const CSteamID *steamId ) {
	(void)steamId;
	return qfalse;
}

/*
=============
QL_Steamworks_HexEncode
=============
*/
static inline qboolean QL_Steamworks_HexEncode( const uint8_t *data, uint32_t length, char *out, size_t outSize ) {
	(void)data;
	(void)length;
	(void)out;
	(void)outSize;
	return qfalse;
}

/*
=============
QL_Steamworks_HexDecode
=============
*/
static inline qboolean QL_Steamworks_HexDecode( const char *hex, uint8_t *out, size_t outSize, uint32_t *outLength ) {
	(void)hex;
	(void)out;
	(void)outSize;
	(void)outLength;
	return qfalse;
}

/*
=============
QL_Steamworks_GetAuthTicketApiLabel
=============
*/
static inline const char *QL_Steamworks_GetAuthTicketApiLabel( void ) {
	return "unavailable";
}

/*
=============
QL_Steamworks_GetAuthTicketModernGapLabel
=============
*/
static inline const char *QL_Steamworks_GetAuthTicketModernGapLabel( void ) {
	return "unavailable";
}

/*
=============
QL_Steamworks_IsUserLoggedOn
=============
*/
static inline qboolean QL_Steamworks_IsUserLoggedOn( void ) {
	return qfalse;
}

/*
=============
QL_Steamworks_GetWebApiAuthTicketIdentity
=============
*/
static inline const char *QL_Steamworks_GetWebApiAuthTicketIdentity( void ) {
	return "quake-live-srp-auth";
}

/*
=============
QL_Steamworks_HasWebApiAuthTicketAdapter
=============
*/
static inline qboolean QL_Steamworks_HasWebApiAuthTicketAdapter( void ) {
	return qfalse;
}

/*
=============
QL_Steamworks_RequestWebApiAuthTicket
=============
*/
static inline qboolean QL_Steamworks_RequestWebApiAuthTicket( const char *identity, char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle, int *steamResult ) {
	(void)identity;
	(void)ticketBuffer;
	(void)ticketBufferSize;
	(void)ticketLength;
	(void)ticketHandle;
	(void)steamResult;
	return qfalse;
}

/*
=============
QL_Steamworks_RequestAuthTicket
=============
*/
static inline qboolean QL_Steamworks_RequestAuthTicket( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle ) {
	(void)ticketBuffer;
	(void)ticketBufferSize;
	(void)ticketLength;
	(void)ticketHandle;
	return qfalse;
}

/*
=============
QL_Steamworks_CancelAuthTicket
=============
*/
static inline qboolean QL_Steamworks_CancelAuthTicket( uint32_t ticketHandle ) {
	(void)ticketHandle;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerBeginAuthSession
=============
*/
static inline qboolean QL_Steamworks_ServerBeginAuthSession( const CSteamID *steamId, const char *ticketHex, ql_auth_response_t *response ) {
	(void)steamId;
	(void)ticketHex;
	(void)response;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerEndAuthSession
=============
*/
static inline void QL_Steamworks_ServerEndAuthSession( const CSteamID *steamId ) {
	(void)steamId;
}

/*
=============
QL_Steamworks_ValidateTicket
=============
*/
static inline qboolean QL_Steamworks_ValidateTicket( const char *ticketHex, ql_auth_response_t *response ) {
	(void)ticketHex;
	(void)response;
	return qfalse;
}

/*
=============
QL_Steamworks_IsSubscribedApp
=============
*/
static inline qboolean QL_Steamworks_IsSubscribedApp( uint32_t appId ) {
	(void)appId;
	return qfalse;
}

/*
=============
QL_Steamworks_HasUGCInterface
=============
*/
static inline qboolean QL_Steamworks_HasUGCInterface( void ) {
	return qfalse;
}

/*
=============
QL_Steamworks_GetNumSubscribedItems
=============
*/
static inline uint32_t QL_Steamworks_GetNumSubscribedItems( void ) {
	return 0u;
}

/*
=============
QL_Steamworks_GetSubscribedItems
=============
*/
static inline uint32_t QL_Steamworks_GetSubscribedItems( uint64_t *outItemIds, uint32_t maxItems ) {
	(void)outItemIds;
	(void)maxItems;
	return 0u;
}

/*
=============
QL_Steamworks_GetItemInstallInfo
=============
*/
static inline qboolean QL_Steamworks_GetItemInstallInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outSizeOnDisk, char *folder, size_t folderSize, uint32_t *outTimestamp ) {
	(void)idLow;
	(void)idHigh;
	if ( outSizeOnDisk ) {
		*outSizeOnDisk = 0ull;
	}
	if ( folder && folderSize > 0 ) {
		folder[0] = '\0';
	}
	if ( outTimestamp ) {
		*outTimestamp = 0u;
	}
	return qfalse;
}

/*
=============
QL_Steamworks_GetItemDownloadInfo
=============
*/
static inline qboolean QL_Steamworks_GetItemDownloadInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outDownloaded, uint64_t *outTotal ) {
	(void)idLow;
	(void)idHigh;
	(void)outDownloaded;
	(void)outTotal;
	return qfalse;
}

/*
=============
QL_Steamworks_ActivateOverlayToUser
=============
*/
static inline qboolean QL_Steamworks_ActivateOverlayToUser( const char *dialog, uint32_t idLow, uint32_t idHigh ) {
	(void)dialog;
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QL_Steamworks_ActivateOverlayToWebPage
=============
*/
static inline qboolean QL_Steamworks_ActivateOverlayToWebPage( const char *url ) {
	(void)url;
	return qfalse;
}

/*
=============
QL_Steamworks_CreateLobby
=============
*/
static inline qboolean QL_Steamworks_CreateLobby( int maxMembers ) {
	(void)maxMembers;
	return qfalse;
}

/*
=============
QL_Steamworks_SetFavoriteServerForApp
=============
*/
static inline qboolean QL_Steamworks_SetFavoriteServerForApp( uint32_t serverIp, uint16_t serverPort, uint32_t appId, qboolean add ) {
	(void)serverIp;
	(void)serverPort;
	(void)appId;
	(void)add;
	return qfalse;
}

/*
=============
QL_Steamworks_SetFavoriteServer
=============
*/
static inline qboolean QL_Steamworks_SetFavoriteServer( uint32_t serverIp, uint16_t serverPort, qboolean add ) {
	(void)serverIp;
	(void)serverPort;
	(void)add;
	return qfalse;
}

/*
=============
QL_Steamworks_LeaveLobby
=============
*/
static inline qboolean QL_Steamworks_LeaveLobby( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QL_Steamworks_JoinLobby
=============
*/
static inline qboolean QL_Steamworks_JoinLobby( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QL_Steamworks_GetLobbyOwner
=============
*/
static inline qboolean QL_Steamworks_GetLobbyOwner( uint32_t idLow, uint32_t idHigh, uint32_t *outIdLow, uint32_t *outIdHigh ) {
	(void)idLow;
	(void)idHigh;
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
QL_Steamworks_GetLobbyDataCount
=============
*/
static inline int QL_Steamworks_GetLobbyDataCount( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return 0;
}

/*
=============
QL_Steamworks_SetLobbyData
=============
*/
static inline qboolean QL_Steamworks_SetLobbyData( uint32_t idLow, uint32_t idHigh, const char *key, const char *value ) {
	(void)idLow;
	(void)idHigh;
	(void)key;
	(void)value;
	return qfalse;
}

/*
=============
QL_Steamworks_GetLobbyDataByIndex
=============
*/
static inline qboolean QL_Steamworks_GetLobbyDataByIndex( uint32_t idLow, uint32_t idHigh, int index, char *key, size_t keySize, char *value, size_t valueSize ) {
	(void)idLow;
	(void)idHigh;
	(void)index;
	if ( key && keySize > 0 ) {
		key[0] = '\0';
	}
	if ( value && valueSize > 0 ) {
		value[0] = '\0';
	}
	return qfalse;
}

/*
=============
QL_Steamworks_GetNumLobbyMembers
=============
*/
static inline int QL_Steamworks_GetNumLobbyMembers( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return 0;
}

/*
=============
QL_Steamworks_GetLobbyMemberLimit
=============
*/
static inline int QL_Steamworks_GetLobbyMemberLimit( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return 0;
}

/*
=============
QL_Steamworks_GetLobbyMemberByIndex
=============
*/
static inline qboolean QL_Steamworks_GetLobbyMemberByIndex( uint32_t idLow, uint32_t idHigh, int index, uint32_t *outIdLow, uint32_t *outIdHigh ) {
	(void)idLow;
	(void)idHigh;
	(void)index;
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
QL_Steamworks_GetFriendPersonaName
=============
*/
static inline qboolean QL_Steamworks_GetFriendPersonaName( uint32_t idLow, uint32_t idHigh, char *buffer, size_t bufferSize ) {
	(void)idLow;
	(void)idHigh;
	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
	return qfalse;
}

/*
=============
QL_Steamworks_SetLobbyServer
=============
*/
static inline qboolean QL_Steamworks_SetLobbyServer( uint32_t idLow, uint32_t idHigh, uint32_t serverIp, uint16_t serverPort ) {
	(void)idLow;
	(void)idHigh;
	(void)serverIp;
	(void)serverPort;
	return qfalse;
}

/*
=============
QL_Steamworks_ShowInviteOverlay
=============
*/
static inline qboolean QL_Steamworks_ShowInviteOverlay( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QL_Steamworks_InviteUserToLobby
=============
*/
static inline qboolean QL_Steamworks_InviteUserToLobby( uint32_t lobbyIdLow, uint32_t lobbyIdHigh, uint32_t userIdLow, uint32_t userIdHigh ) {
	(void)lobbyIdLow;
	(void)lobbyIdHigh;
	(void)userIdLow;
	(void)userIdHigh;
	return qfalse;
}

/*
=============
QL_Steamworks_InviteUserToGame
=============
*/
static inline qboolean QL_Steamworks_InviteUserToGame( uint32_t idLow, uint32_t idHigh, const char *connectString ) {
	(void)idLow;
	(void)idHigh;
	(void)connectString;
	return qfalse;
}

/*
=============
QL_Steamworks_SayLobby
=============
*/
static inline qboolean QL_Steamworks_SayLobby( uint32_t idLow, uint32_t idHigh, const char *message ) {
	(void)idLow;
	(void)idHigh;
	(void)message;
	return qfalse;
}

/*
=============
QL_Steamworks_RequestUserStats
=============
*/
static inline qboolean QL_Steamworks_RequestUserStats( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QL_Steamworks_GetUserStatInt
=============
*/
static inline qboolean QL_Steamworks_GetUserStatInt( uint32_t idLow, uint32_t idHigh, const char *name, int *outValue ) {
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
QL_Steamworks_GetUserStatFloat
=============
*/
static inline qboolean QL_Steamworks_GetUserStatFloat( uint32_t idLow, uint32_t idHigh, const char *name, float *outValue ) {
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
QL_Steamworks_GetUserAchievement
=============
*/
static inline qboolean QL_Steamworks_GetUserAchievement( uint32_t idLow, uint32_t idHigh, const char *name, qboolean *outAchieved, int *outUnlockTime ) {
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
QL_Steamworks_GetAchievementDisplayAttribute
=============
*/
static inline const char *QL_Steamworks_GetAchievementDisplayAttribute( const char *name, const char *key ) {
	(void)name;
	(void)key;
	return "";
}

/*
=============
QL_Steamworks_HasServerBrowserInterface
=============
*/
static inline qboolean QL_Steamworks_HasServerBrowserInterface( void ) {
	return qfalse;
}

/*
=============
QL_Steamworks_GetServerBrowserAdapterLabel
=============
*/
static inline const char *QL_Steamworks_GetServerBrowserAdapterLabel( void ) {
	return "unavailable";
}

/*
=============
QL_Steamworks_GetServerBrowserIntegrationGapLabel
=============
*/
static inline const char *QL_Steamworks_GetServerBrowserIntegrationGapLabel( void ) {
	return "unavailable";
}

/*
=============
QL_Steamworks_GetServerBrowserRequestModeLabel
=============
*/
static inline const char *QL_Steamworks_GetServerBrowserRequestModeLabel( ql_steam_server_browser_request_mode_t requestMode ) {
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
=============
*/
static inline qboolean QL_Steamworks_ServerBrowserRequestModeUsesGamedirFilter( ql_steam_server_browser_request_mode_t requestMode ) {
	return requestMode == QL_STEAM_SERVER_BROWSER_LAN ? qfalse : qtrue;
}

/*
=============
QL_Steamworks_InitServerBrowserOwner
=============
*/
static inline void QL_Steamworks_InitServerBrowserOwner( ql_steam_server_browser_owner_t *owner ) {
	if ( owner ) {
		memset( owner, 0, sizeof( *owner ) );
	}
}

/*
=============
QL_Steamworks_BeginServerBrowserOwnerRequest
=============
*/
static inline qboolean QL_Steamworks_BeginServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner, ql_steam_server_browser_request_mode_t requestMode, void *responseObject ) {
	(void)requestMode;
	(void)responseObject;
	if ( owner ) {
		owner->refreshActive = qfalse;
		owner->request = NULL;
	}
	return qfalse;
}

/*
=============
QL_Steamworks_BeginServerBrowserOwnerRequestForApp
=============
*/
static inline qboolean QL_Steamworks_BeginServerBrowserOwnerRequestForApp( ql_steam_server_browser_owner_t *owner, ql_steam_server_browser_request_mode_t requestMode, uint32_t appId, void *responseObject ) {
	(void)requestMode;
	(void)appId;
	(void)responseObject;
	if ( owner ) {
		owner->refreshActive = qfalse;
		owner->request = NULL;
	}
	return qfalse;
}

/*
=============
QL_Steamworks_RefreshServerBrowserOwnerRequest
=============
*/
static inline qboolean QL_Steamworks_RefreshServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner ) {
	(void)owner;
	return qfalse;
}

/*
=============
QL_Steamworks_CompleteServerBrowserOwnerRequest
=============
*/
static inline qboolean QL_Steamworks_CompleteServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner ) {
	if ( owner ) {
		owner->refreshActive = qfalse;
	}
	return qfalse;
}

/*
=============
QL_Steamworks_RequestServerList
=============
*/
static inline ql_steam_server_list_request_t QL_Steamworks_RequestServerList( ql_steam_server_browser_request_mode_t requestMode, void *responseObject ) {
	(void)requestMode;
	(void)responseObject;
	return NULL;
}

/*
=============
QL_Steamworks_RequestServerListForApp
=============
*/
static inline ql_steam_server_list_request_t QL_Steamworks_RequestServerListForApp( ql_steam_server_browser_request_mode_t requestMode, uint32_t appId, void *responseObject ) {
	(void)requestMode;
	(void)appId;
	(void)responseObject;
	return NULL;
}

/*
=============
QL_Steamworks_GetServerListDetails
=============
*/
static inline const void *QL_Steamworks_GetServerListDetails( ql_steam_server_list_request_t request, int index ) {
	(void)request;
	(void)index;
	return NULL;
}

/*
=============
QL_Steamworks_ReadServerListDetails
=============
*/
static inline qboolean QL_Steamworks_ReadServerListDetails( ql_steam_server_list_request_t request, int index, ql_steam_server_item_t *outServer ) {
	(void)request;
	(void)index;
	if ( outServer ) {
		memset( outServer, 0, sizeof( *outServer ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_ReadServerListDetailsForApp
=============
*/
static inline qboolean QL_Steamworks_ReadServerListDetailsForApp( ql_steam_server_list_request_t request, int index, uint32_t appId, ql_steam_server_item_t *outServer ) {
	(void)request;
	(void)index;
	(void)appId;
	if ( outServer ) {
		memset( outServer, 0, sizeof( *outServer ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_FormatServerBrowserResponseId
=============
*/
static inline void QL_Steamworks_FormatServerBrowserResponseId( uint32_t serverIp, uint16_t serverPort, char *buffer, size_t bufferSize ) {
	(void)serverIp;
	(void)serverPort;
	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
}

/*
=============
QL_Steamworks_BuildServerBrowserResponse
=============
*/
static inline qboolean QL_Steamworks_BuildServerBrowserResponse( const ql_steam_server_item_t *server, ql_steam_server_browser_response_t *outResponse ) {
	(void)server;
	if ( outResponse ) {
		memset( outResponse, 0, sizeof( *outResponse ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_ReadServerBrowserResponse
=============
*/
static inline qboolean QL_Steamworks_ReadServerBrowserResponse( ql_steam_server_list_request_t request, int index, ql_steam_server_browser_response_t *outResponse ) {
	(void)request;
	(void)index;
	if ( outResponse ) {
		memset( outResponse, 0, sizeof( *outResponse ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_ReadServerBrowserResponseForApp
=============
*/
static inline qboolean QL_Steamworks_ReadServerBrowserResponseForApp( ql_steam_server_list_request_t request, int index, uint32_t appId, ql_steam_server_browser_response_t *outResponse ) {
	(void)request;
	(void)index;
	(void)appId;
	if ( outResponse ) {
		memset( outResponse, 0, sizeof( *outResponse ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_ReadServerBrowserPingResponse
=============
*/
static inline qboolean QL_Steamworks_ReadServerBrowserPingResponse( const void *serverDetails, ql_steam_server_browser_response_t *outResponse ) {
	(void)serverDetails;
	if ( outResponse ) {
		memset( outResponse, 0, sizeof( *outResponse ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_ReadServerBrowserPingResponseForApp
=============
*/
static inline qboolean QL_Steamworks_ReadServerBrowserPingResponseForApp( const void *serverDetails, uint32_t appId, ql_steam_server_browser_response_t *outResponse ) {
	(void)serverDetails;
	(void)appId;
	if ( outResponse ) {
		memset( outResponse, 0, sizeof( *outResponse ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_FormatServerBrowserFailureEventName
=============
*/
static inline void QL_Steamworks_FormatServerBrowserFailureEventName( int serverIndex, char *buffer, size_t bufferSize ) {
	(void)serverIndex;
	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
}

/*
=============
QL_Steamworks_BuildServerBrowserFailure
=============
*/
static inline qboolean QL_Steamworks_BuildServerBrowserFailure( int serverIndex, ql_steam_server_browser_failure_t *outFailure ) {
	(void)serverIndex;
	if ( outFailure ) {
		memset( outFailure, 0, sizeof( *outFailure ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_BuildServerBrowserRefreshComplete
=============
*/
static inline qboolean QL_Steamworks_BuildServerBrowserRefreshComplete( ql_steam_server_browser_refresh_complete_t *outRefresh ) {
	if ( outRefresh ) {
		memset( outRefresh, 0, sizeof( *outRefresh ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_FormatServerBrowserDetailId
=============
*/
static inline void QL_Steamworks_FormatServerBrowserDetailId( uint32_t serverIp, uint16_t serverPort, char *buffer, size_t bufferSize ) {
	(void)serverIp;
	(void)serverPort;
	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
}

/*
=============
QL_Steamworks_BuildServerBrowserDetailIdentity
=============
*/
static inline qboolean QL_Steamworks_BuildServerBrowserDetailIdentity( uint32_t serverIp, uint16_t serverPort, ql_steam_server_browser_detail_identity_t *outIdentity ) {
	(void)serverIp;
	(void)serverPort;
	if ( outIdentity ) {
		memset( outIdentity, 0, sizeof( *outIdentity ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_FormatServerBrowserDetailEventName
=============
*/
static inline qboolean QL_Steamworks_FormatServerBrowserDetailEventName( ql_steam_server_browser_detail_channel_t channel, ql_steam_server_browser_detail_phase_t phase, const char *detailId, char *buffer, size_t bufferSize ) {
	(void)channel;
	(void)phase;
	(void)detailId;
	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
	return qfalse;
}

/*
=============
QL_Steamworks_BuildServerBrowserDetailEvent
=============
*/
static inline qboolean QL_Steamworks_BuildServerBrowserDetailEvent( const ql_steam_server_browser_detail_identity_t *identity, ql_steam_server_browser_detail_channel_t channel, ql_steam_server_browser_detail_phase_t phase, ql_steam_server_browser_detail_event_t *outEvent ) {
	(void)identity;
	(void)channel;
	(void)phase;
	if ( outEvent ) {
		memset( outEvent, 0, sizeof( *outEvent ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_BuildServerBrowserRuleResponse
=============
*/
static inline qboolean QL_Steamworks_BuildServerBrowserRuleResponse( const ql_steam_server_browser_detail_identity_t *identity, const char *rule, const char *value, ql_steam_server_browser_rule_response_t *outResponse ) {
	(void)identity;
	(void)rule;
	(void)value;
	if ( outResponse ) {
		memset( outResponse, 0, sizeof( *outResponse ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_BuildServerBrowserPlayerResponse
=============
*/
static inline qboolean QL_Steamworks_BuildServerBrowserPlayerResponse( const ql_steam_server_browser_detail_identity_t *identity, const char *name, int score, int time, ql_steam_server_browser_player_response_t *outResponse ) {
	(void)identity;
	(void)name;
	(void)score;
	(void)time;
	if ( outResponse ) {
		memset( outResponse, 0, sizeof( *outResponse ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_InitServerBrowserDetailLifecycle
=============
*/
static inline qboolean QL_Steamworks_InitServerBrowserDetailLifecycle( uint32_t serverIp, uint16_t serverPort, ql_steam_server_browser_detail_lifecycle_t *outLifecycle ) {
	(void)serverIp;
	(void)serverPort;
	if ( outLifecycle ) {
		memset( outLifecycle, 0, sizeof( *outLifecycle ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_CompleteServerBrowserDetailCallback
=============
*/
static inline qboolean QL_Steamworks_CompleteServerBrowserDetailCallback( ql_steam_server_browser_detail_lifecycle_t *lifecycle, qboolean *outReleaseReady ) {
	if ( lifecycle ) {
		memset( lifecycle, 0, sizeof( *lifecycle ) );
	}
	if ( outReleaseReady ) {
		*outReleaseReady = qfalse;
	}
	return qfalse;
}

/*
=============
QL_Steamworks_CompleteServerBrowserDetailTerminal
=============
*/
static inline qboolean QL_Steamworks_CompleteServerBrowserDetailTerminal( ql_steam_server_browser_detail_lifecycle_t *lifecycle, uint32_t terminalChannel, qboolean *outReleaseReady ) {
	(void)terminalChannel;
	if ( lifecycle ) {
		memset( lifecycle, 0, sizeof( *lifecycle ) );
	}
	if ( outReleaseReady ) {
		*outReleaseReady = qfalse;
	}
	return qfalse;
}

/*
=============
QL_Steamworks_BuildServerBrowserDetailResponseViews
=============
*/
static inline qboolean QL_Steamworks_BuildServerBrowserDetailResponseViews( void *detailObjectBase, ql_steam_server_browser_detail_response_views_t *outViews ) {
	(void)detailObjectBase;
	if ( outViews ) {
		memset( outViews, 0, sizeof( *outViews ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_InitServerBrowserDetailRequest
=============
*/
static inline void QL_Steamworks_InitServerBrowserDetailRequest( ql_steam_server_browser_detail_request_t *request ) {
	if ( request ) {
		memset( request, 0, sizeof( *request ) );
	}
}

/*
=============
QL_Steamworks_BeginServerBrowserDetailRequest
=============
*/
static inline qboolean QL_Steamworks_BeginServerBrowserDetailRequest( ql_steam_server_browser_detail_request_t *request, uint32_t serverIp, uint16_t serverPort, void *detailObjectBase ) {
	(void)serverIp;
	(void)serverPort;
	(void)detailObjectBase;
	if ( request ) {
		memset( request, 0, sizeof( *request ) );
	}
	return qfalse;
}

/*
=============
QL_Steamworks_CompleteServerBrowserDetailRequestCallback
=============
*/
static inline qboolean QL_Steamworks_CompleteServerBrowserDetailRequestCallback( ql_steam_server_browser_detail_request_t *request, qboolean *outReleaseReady ) {
	if ( request ) {
		memset( request, 0, sizeof( *request ) );
	}
	if ( outReleaseReady ) {
		*outReleaseReady = qfalse;
	}
	return qfalse;
}

/*
=============
QL_Steamworks_CompleteServerBrowserDetailRequestTerminal
=============
*/
static inline qboolean QL_Steamworks_CompleteServerBrowserDetailRequestTerminal( ql_steam_server_browser_detail_request_t *request, uint32_t terminalChannel, qboolean *outReleaseReady ) {
	(void)terminalChannel;
	if ( request ) {
		memset( request, 0, sizeof( *request ) );
	}
	if ( outReleaseReady ) {
		*outReleaseReady = qfalse;
	}
	return qfalse;
}

/*
=============
QL_Steamworks_ReleaseServerListRequest
=============
*/
static inline void QL_Steamworks_ReleaseServerListRequest( ql_steam_server_list_request_t request ) {
	(void)request;
}

/*
=============
QL_Steamworks_RefreshServerListRequest
=============
*/
static inline void QL_Steamworks_RefreshServerListRequest( ql_steam_server_list_request_t request ) {
	(void)request;
}

/*
=============
QL_Steamworks_RequestServerDetails
=============
*/
static inline qboolean QL_Steamworks_RequestServerDetails( uint32_t serverIp, uint16_t serverPort, void *pingResponse, void *playersResponse, void *rulesResponse, ql_steam_server_query_t *outPingQuery, ql_steam_server_query_t *outPlayersQuery, ql_steam_server_query_t *outRulesQuery ) {
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
QL_Steamworks_CancelServerQuery
=============
*/
static inline void QL_Steamworks_CancelServerQuery( ql_steam_server_query_t query ) {
	(void)query;
}

/*
=============
QL_Steamworks_ServerGetAppID
=============
*/
static inline uint32_t QL_Steamworks_ServerGetAppID( void ) {
	return 0u;
}

/*
=============
QL_Steamworks_ServerIsLoggedOn
=============
*/
static inline qboolean QL_Steamworks_ServerIsLoggedOn( void ) {
	return qfalse;
}

/*
=============
QL_Steamworks_ServerRequestUserStats
=============
*/
static inline qboolean QL_Steamworks_ServerRequestUserStats( const CSteamID *steamId ) {
	(void)steamId;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerGetUserStatInt
=============
*/
static inline qboolean QL_Steamworks_ServerGetUserStatInt( const CSteamID *steamId, const char *name, int *outValue ) {
	(void)steamId;
	(void)name;
	if ( outValue ) {
		*outValue = 0;
	}
	return qfalse;
}

/*
=============
QL_Steamworks_ServerGetUserStatFloat
=============
*/
static inline qboolean QL_Steamworks_ServerGetUserStatFloat( const CSteamID *steamId, const char *name, float *outValue ) {
	(void)steamId;
	(void)name;
	if ( outValue ) {
		*outValue = 0.0f;
	}
	return qfalse;
}

/*
=============
QL_Steamworks_ServerGetUserAchievement
=============
*/
static inline qboolean QL_Steamworks_ServerGetUserAchievement( const CSteamID *steamId, const char *name, qboolean *outAchieved ) {
	(void)steamId;
	(void)name;
	if ( outAchieved ) {
		*outAchieved = qfalse;
	}
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetUserStatInt
=============
*/
static inline qboolean QL_Steamworks_ServerSetUserStatInt( const CSteamID *steamId, const char *name, int value ) {
	(void)steamId;
	(void)name;
	(void)value;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetUserStatFloat
=============
*/
static inline qboolean QL_Steamworks_ServerSetUserStatFloat( const CSteamID *steamId, const char *name, float value ) {
	(void)steamId;
	(void)name;
	(void)value;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerUpdateAvgRateStat
=============
*/
static inline qboolean QL_Steamworks_ServerUpdateAvgRateStat( const CSteamID *steamId, const char *name, float countThisSession, double sessionLength ) {
	(void)steamId;
	(void)name;
	(void)countThisSession;
	(void)sessionLength;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetUserAchievement
=============
*/
static inline qboolean QL_Steamworks_ServerSetUserAchievement( const CSteamID *steamId, const char *name ) {
	(void)steamId;
	(void)name;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerStoreUserStats
=============
*/
static inline qboolean QL_Steamworks_ServerStoreUserStats( const CSteamID *steamId ) {
	(void)steamId;
	return qfalse;
}

/*
=============
QL_Steamworks_GetItemState
=============
*/
static inline uint32_t QL_Steamworks_GetItemState( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return 0;
}

/*
=============
QL_Steamworks_SubscribeItem
=============
*/
static inline qboolean QL_Steamworks_SubscribeItem( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QL_Steamworks_UnsubscribeItem
=============
*/
static inline qboolean QL_Steamworks_UnsubscribeItem( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QL_Steamworks_DownloadItem
=============
*/
static inline qboolean QL_Steamworks_DownloadItem( uint32_t idLow, uint32_t idHigh, qboolean highPriority ) {
	(void)idLow;
	(void)idHigh;
	(void)highPriority;
	return qfalse;
}

/*
=============
QL_Steamworks_GetAllUGCFilterContractLabel
=============
*/
static inline const char *QL_Steamworks_GetAllUGCFilterContractLabel( void ) {
	return "unavailable";
}

/*
=============
QL_Steamworks_GetAllUGCFilterSemanticGapLabel
=============
*/
static inline const char *QL_Steamworks_GetAllUGCFilterSemanticGapLabel( void ) {
	return "unavailable";
}

/*
=============
QL_Steamworks_RequestAllUGCQuery
=============
*/
static inline qboolean QL_Steamworks_RequestAllUGCQuery( uint32_t filter ) {
	(void)filter;
	return qfalse;
}

/*
=============
QL_Steamworks_GetQueryUGCResult
=============
*/
static inline qboolean QL_Steamworks_GetQueryUGCResult( uint64_t queryHandle, uint32_t index, uint64_t *outPublishedFileId, char *title, size_t titleSize, char *description, size_t descriptionSize ) {
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
QL_Steamworks_GetQueryUGCPreviewURL
=============
*/
static inline qboolean QL_Steamworks_GetQueryUGCPreviewURL( uint64_t queryHandle, uint32_t index, char *buffer, size_t bufferSize ) {
	(void)queryHandle;
	(void)index;
	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
	return qfalse;
}

/*
=============
QL_Steamworks_ReleaseQueryUGCRequest
=============
*/
static inline void QL_Steamworks_ReleaseQueryUGCRequest( uint64_t queryHandle ) {
	(void)queryHandle;
}

/*
=============
QL_Steamworks_RequestAvatarImage
=============
*/
static inline ql_steam_avatar_image_state_t QL_Steamworks_RequestAvatarImage( uint32_t idLow, uint32_t idHigh, ql_steam_avatar_size_t size, int *outImage ) {
	(void)idLow;
	(void)idHigh;
	(void)size;
	if ( outImage ) {
		*outImage = 0;
	}
	return QL_STEAM_AVATAR_IMAGE_UNAVAILABLE;
}

/*
=============
QL_Steamworks_LoadAvatarRGBA
=============
*/
static inline qboolean QL_Steamworks_LoadAvatarRGBA( uint32_t idLow, uint32_t idHigh, ql_steam_avatar_size_t size, uint8_t **outPixels, uint32_t *outWidth, uint32_t *outHeight ) {
	(void)idLow;
	(void)idHigh;
	(void)size;
	if ( outPixels ) {
		*outPixels = NULL;
	}
	if ( outWidth ) {
		*outWidth = 0;
	}
	if ( outHeight ) {
		*outHeight = 0;
	}
	return qfalse;
}

/*
=============
QL_Steamworks_RegisterAvatarCallbacks
=============
*/
static inline qboolean QL_Steamworks_RegisterAvatarCallbacks( const ql_steam_avatar_callback_bindings_t *bindings ) {
	(void)bindings;
	return qfalse;
}

/*
=============
QL_Steamworks_UnregisterAvatarCallbacks
=============
*/
static inline void QL_Steamworks_UnregisterAvatarCallbacks( void ) {
}

/*
=============
QL_Steamworks_RegisterClientCallbacks
=============
*/
static inline qboolean QL_Steamworks_RegisterClientCallbacks( const ql_steam_client_callback_bindings_t *bindings ) {
	(void)bindings;
	return qfalse;
}

/*
=============
QL_Steamworks_UnregisterClientCallbacks
=============
*/
static inline void QL_Steamworks_UnregisterClientCallbacks( void ) {
}

/*
=============
QL_Steamworks_RegisterServerCallbacks
=============
*/
static inline qboolean QL_Steamworks_RegisterServerCallbacks( const ql_steam_server_callback_bindings_t *bindings ) {
	(void)bindings;
	return qfalse;
}

/*
=============
QL_Steamworks_UnregisterServerCallbacks
=============
*/
static inline void QL_Steamworks_UnregisterServerCallbacks( void ) {
}

/*
=============
QL_Steamworks_RegisterLobbyCallbacks
=============
*/
static inline qboolean QL_Steamworks_RegisterLobbyCallbacks( const ql_steam_lobby_callback_bindings_t *bindings ) {
	(void)bindings;
	return qfalse;
}

/*
=============
QL_Steamworks_UnregisterLobbyCallbacks
=============
*/
static inline void QL_Steamworks_UnregisterLobbyCallbacks( void ) {
}

/*
=============
QL_Steamworks_RegisterMicroCallbacks
=============
*/
static inline qboolean QL_Steamworks_RegisterMicroCallbacks( const ql_steam_micro_callback_bindings_t *bindings ) {
	(void)bindings;
	return qfalse;
}

/*
=============
QL_Steamworks_UnregisterMicroCallbacks
=============
*/
static inline void QL_Steamworks_UnregisterMicroCallbacks( void ) {
}

/*
=============
QL_Steamworks_RegisterWorkshopCallbacks
=============
*/
static inline qboolean QL_Steamworks_RegisterWorkshopCallbacks( const ql_steam_workshop_callback_bindings_t *bindings ) {
	(void)bindings;
	return qfalse;
}

/*
=============
QL_Steamworks_UnregisterWorkshopCallbacks
=============
*/
static inline void QL_Steamworks_UnregisterWorkshopCallbacks( void ) {
}

/*
=============
QL_Steamworks_BindUGCQueryCallResult
=============
*/
static inline qboolean QL_Steamworks_BindUGCQueryCallResult( SteamAPICall_t callHandle ) {
	(void)callHandle;
	return qfalse;
}

/*
=============
QL_Steamworks_FreeBuffer
=============
*/
static inline void QL_Steamworks_FreeBuffer( void *buffer ) {
	(void)buffer;
}

#endif

#endif // PLATFORM_STEAMWORKS_H

