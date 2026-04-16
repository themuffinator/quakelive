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

typedef uint64_t SteamAPICall_t;

#define QL_STEAM_NAME_LENGTH 128
#define QL_STEAM_STATUS_LENGTH 256
#define QL_STEAM_COMMAND_LENGTH 256
#define QL_STEAM_SERVER_LENGTH 128
#define QL_STEAM_PASSWORD_LENGTH 128
#define QL_STEAM_LOBBY_MESSAGE_LENGTH 256

typedef struct {
	CSteamID steamId;
	int relationship;
	int personaState;
	char name[QL_STEAM_NAME_LENGTH];
	char nickname[QL_STEAM_NAME_LENGTH];
	char status[QL_STEAM_STATUS_LENGTH];
	char lanIp[64];
	qboolean playingQuake;
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

void QL_Steamworks_Shutdown( void );

void QL_Steamworks_RunCallbacks( void );

void QL_Steamworks_RunServerCallbacks( void );

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

int QL_Steamworks_GetFriendCount( int flags );

qboolean QL_Steamworks_GetFriendByIndex( int index, int flags, uint32_t *outIdLow, uint32_t *outIdHigh );

qboolean QL_Steamworks_GetFriendSummary( uint32_t idLow, uint32_t idHigh, ql_steam_friend_summary_t *outSummary );

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

int QL_Steamworks_ServerGetNextOutgoingPacket( void *data, int dataSize, uint32_t *outIp, uint16_t *outPort );

qboolean QL_Steamworks_ServerAcceptP2PSession( const CSteamID *steamId );

qboolean QL_Steamworks_HexEncode( const uint8_t *data, uint32_t length, char *out, size_t outSize );

qboolean QL_Steamworks_HexDecode( const char *hex, uint8_t *out, size_t outSize, uint32_t *outLength );

qboolean QL_Steamworks_RequestAuthTicket( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle );

qboolean QL_Steamworks_CancelAuthTicket( uint32_t ticketHandle );

qboolean QL_Steamworks_ServerBeginAuthSession( const CSteamID *steamId, const char *ticketHex, ql_auth_response_t *response );

void QL_Steamworks_ServerEndAuthSession( const CSteamID *steamId );

qboolean QL_Steamworks_ValidateTicket( const char *ticketHex, ql_auth_response_t *response );

qboolean QL_Steamworks_IsSubscribedApp( uint32_t appId );

uint32_t QL_Steamworks_GetNumSubscribedItems( void );

uint32_t QL_Steamworks_GetSubscribedItems( uint64_t *outItemIds, uint32_t maxItems );

qboolean QL_Steamworks_GetItemInstallInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outSizeOnDisk, char *folder, size_t folderSize, uint32_t *outTimestamp );

qboolean QL_Steamworks_GetItemDownloadInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outDownloaded, uint64_t *outTotal );

qboolean QL_Steamworks_ActivateOverlayToUser( const char *dialog, uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_SetRichPresence( const char *key, const char *value );

qboolean QL_Steamworks_CreateLobby( int maxMembers );

qboolean QL_Steamworks_LeaveLobby( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_JoinLobby( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_SetLobbyServer( uint32_t idLow, uint32_t idHigh, uint32_t serverIp, uint16_t serverPort );

qboolean QL_Steamworks_ShowInviteOverlay( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_SayLobby( uint32_t idLow, uint32_t idHigh, const char *message );

qboolean QL_Steamworks_RequestUserStats( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_ServerRequestUserStats( const CSteamID *steamId );

qboolean QL_Steamworks_ServerGetUserStatInt( const CSteamID *steamId, const char *name, int *outValue );

qboolean QL_Steamworks_ServerGetUserAchievement( const CSteamID *steamId, const char *name, qboolean *outAchieved );

qboolean QL_Steamworks_ServerSetUserStatInt( const CSteamID *steamId, const char *name, int value );

qboolean QL_Steamworks_ServerSetUserAchievement( const CSteamID *steamId, const char *name );

qboolean QL_Steamworks_ServerStoreUserStats( const CSteamID *steamId );

uint32_t QL_Steamworks_GetItemState( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_SubscribeItem( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_UnsubscribeItem( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_DownloadItem( uint32_t idLow, uint32_t idHigh, qboolean highPriority );

qboolean QL_Steamworks_LoadAvatarRGBA( uint32_t idLow, uint32_t idHigh, ql_steam_avatar_size_t size, uint8_t **outPixels, uint32_t *outWidth, uint32_t *outHeight );

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
QL_Steamworks_ServerInit
=============
*/
static inline qboolean QL_Steamworks_ServerInit( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated ) {
	(void)ip;
	(void)gamePort;
	(void)secure;
	(void)dedicated;
	return qfalse;
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
QL_Steamworks_CreateLobby
=============
*/
static inline qboolean QL_Steamworks_CreateLobby( int maxMembers ) {
	(void)maxMembers;
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

