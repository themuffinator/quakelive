#ifndef PLATFORM_STEAMWORKS_H
#define PLATFORM_STEAMWORKS_H

#include "platform_config.h"

#include <stddef.h>
#include <stdint.h>

#include "../auth_credentials.h"

typedef struct {
	uint64_t value;
} CSteamID;

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

qboolean QL_Steamworks_ServerSendP2PPacket( const CSteamID *steamId, const void *data, uint32_t length, int sendType, int channel );

qboolean QL_Steamworks_ServerIsP2PPacketAvailable( uint32_t *outSize, int channel );

qboolean QL_Steamworks_ServerReadP2PPacket( void *data, uint32_t dataSize, uint32_t *outSize, CSteamID *outSteamId, int channel );

int QL_Steamworks_ServerGetNextOutgoingPacket( void *data, int dataSize, uint32_t *outIp, uint16_t *outPort );

qboolean QL_Steamworks_HexEncode( const uint8_t *data, uint32_t length, char *out, size_t outSize );

qboolean QL_Steamworks_HexDecode( const char *hex, uint8_t *out, size_t outSize, uint32_t *outLength );

qboolean QL_Steamworks_RequestAuthTicket( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle );

qboolean QL_Steamworks_ValidateTicket( const char *ticketHex, ql_auth_response_t *response );

qboolean QL_Steamworks_IsSubscribedApp( uint32_t appId );

qboolean QL_Steamworks_GetItemDownloadInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outDownloaded, uint64_t *outTotal );

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

#endif

#endif // PLATFORM_STEAMWORKS_H

