#include <ctype.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "../src/common/platform/platform_steamworks.h"

#if QL_BUILD_STEAMWORKS

#define QLR_TICKET_BUFFER 1024

typedef struct {
	qboolean library_available;
	qboolean init_result;
	qboolean user_available;
	EBeginAuthSessionResult auth_result;
	uint8_t ticket[QLR_TICKET_BUFFER];
	uint32_t ticket_length;
	HAuthTicket ticket_handle;
	uint64_t steam_id_value;
} qlr_steamworks_mock_state_t;

static qlr_steamworks_mock_state_t qlr_mock_state = {
.library_available = qtrue,
.init_result = qtrue,
.user_available = qtrue,
.auth_result = k_EBeginAuthSessionResultOK,
.ticket = { 0x12, 0x34, 0x56, 0x78 },
.ticket_length = 4,
.ticket_handle = 1,
.steam_id_value = 0xDEADBEEFULL
};

qboolean QLR_SteamAPI_Init( void );

void QLR_SteamAPI_Shutdown( void );

void QLR_SteamAPI_RunCallbacks( void );

void *QLR_SteamAPI_SteamUser( void );

void *QLR_SteamAPI_SteamFriends( void );

void *QLR_SteamAPI_SteamMatchmaking( void );

void *QLR_SteamAPI_SteamUGC( void );

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
QLR_SteamworksMock_Reset

Restore default mock state for Steamworks entry points.
=============
*/
void QLR_SteamworksMock_Reset( void ) {
	qlr_mock_state.library_available = qtrue;
	qlr_mock_state.init_result = qtrue;
	qlr_mock_state.user_available = qtrue;
	qlr_mock_state.auth_result = k_EBeginAuthSessionResultOK;
	memcpy( qlr_mock_state.ticket, (uint8_t[]){ 0x12, 0x34, 0x56, 0x78 }, 4 );
	qlr_mock_state.ticket_length = 4;
	qlr_mock_state.ticket_handle = 1;
	qlr_mock_state.steam_id_value = 0xDEADBEEFULL;
}

/*
=============
QLR_SteamworksMock_SetLibraryAvailable

Configure whether dlopen succeeds when loading Steamworks.
=============
*/
void QLR_SteamworksMock_SetLibraryAvailable( qboolean available ) {
	qlr_mock_state.library_available = available;
}

/*
=============
QLR_SteamworksMock_SetInitResult

Set the return value for SteamAPI_Init.
=============
*/
void QLR_SteamworksMock_SetInitResult( qboolean result ) {
	qlr_mock_state.init_result = result;
}

/*
=============
QLR_SteamworksMock_SetUserAvailable

Toggle whether SteamAPI_SteamUser returns a valid handle.
=============
*/
void QLR_SteamworksMock_SetUserAvailable( qboolean available ) {
	qlr_mock_state.user_available = available;
}

/*
=============
QLR_SteamworksMock_SetTicket

Override the raw ticket contents and handle returned by GetAuthSessionTicket.
=============
*/
void QLR_SteamworksMock_SetTicket( const uint8_t *ticket, uint32_t length, HAuthTicket handle ) {
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
void QLR_SteamworksMock_SetAuthResult( EBeginAuthSessionResult result ) {
	qlr_mock_state.auth_result = result;
}

/*
=============
QLR_SteamworksMock_SetSteamId

Define the SteamID returned by GetSteamID.
=============
*/
void QLR_SteamworksMock_SetSteamId( uint64_t steamId ) {
	qlr_mock_state.steam_id_value = steamId;
}

/*
=============
Com_Printf
=============
*/
void Com_Printf( const char *fmt, ... ) {
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
void Com_sprintf( char *dest, int size, const char *fmt, ... ) {
	va_list args;
	va_start( args, fmt );
	vsnprintf( dest, (size_t)size, fmt, args );
	va_end( args );
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

	if ( strcmp( symbol, "SteamAPI_SteamUser" ) == 0 ) {
		return QLR_SteamAPI_SteamUser;
	}

	if ( strcmp( symbol, "SteamAPI_SteamFriends" ) == 0 ) {
		return QLR_SteamAPI_SteamFriends;
	}

	if ( strcmp( symbol, "SteamAPI_SteamMatchmaking" ) == 0 ) {
		return QLR_SteamAPI_SteamMatchmaking;
	}

	if ( strcmp( symbol, "SteamAPI_SteamUGC" ) == 0 ) {
		return QLR_SteamAPI_SteamUGC;
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

	return QLR_SteamAPI_Init;
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
QLR_SteamAPI_RunCallbacks
=============
*/
void QLR_SteamAPI_RunCallbacks( void ) {
}

/*
=============
QLR_SteamAPI_SteamUser
=============
*/
void *QLR_SteamAPI_SteamUser( void ) {
	static int dummy_user = 7;
	return qlr_mock_state.user_available ? &dummy_user : NULL;
}

/*
=============
QLR_SteamAPI_SteamFriends
=============
*/
void *QLR_SteamAPI_SteamFriends( void ) {
	return NULL;
}

/*
=============
QLR_SteamAPI_SteamMatchmaking
=============
*/
void *QLR_SteamAPI_SteamMatchmaking( void ) {
	return NULL;
}

/*
=============
QLR_SteamAPI_SteamUGC
=============
*/
void *QLR_SteamAPI_SteamUGC( void ) {
	return NULL;
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
	(void)handle;
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
void QLR_SteamworksMock_PrimeState( void ) {
	state.library = qlr_mock_state.library_available ? (void *)0x1 : NULL;
	state.initialised = qfalse;
	state.SteamAPI_Init = QLR_SteamAPI_Init;
	state.SteamAPI_Shutdown = QLR_SteamAPI_Shutdown;
	state.SteamAPI_RunCallbacks = QLR_SteamAPI_RunCallbacks;
	state.SteamUser = QLR_SteamAPI_SteamUser;
	state.SteamFriends = QLR_SteamAPI_SteamFriends;
	state.SteamMatchmaking = QLR_SteamAPI_SteamMatchmaking;
	state.SteamUGC = QLR_SteamAPI_SteamUGC;
	state.GetAuthSessionTicket = QLR_SteamAPI_GetAuthSessionTicket;
	state.BeginAuthSession = QLR_SteamAPI_BeginAuthSession;
	state.CancelAuthTicket = QLR_SteamAPI_CancelAuthTicket;
	state.EndAuthSession = QLR_SteamAPI_EndAuthSession;
	state.GetSteamID = QLR_SteamAPI_GetSteamID;
}

/*
=============
QLR_Steamworks_Request

Wrapper exposing QL_Steamworks_RequestAuthTicket for ctypes.
=============
*/
qboolean QLR_Steamworks_Request( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle ) {
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
QLR_Steamworks_Shutdown
=============
*/
void QLR_Steamworks_Shutdown( void ) {
	QL_Steamworks_Shutdown();
}

/*
=============
QLR_Steamworks_Validate

Wrapper exposing QL_Steamworks_ValidateTicket for ctypes.
=============
*/
qboolean QLR_Steamworks_Validate( const char *ticketHex, ql_auth_response_t *response ) {
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
qboolean QLR_Steamworks_Request( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle ) {
	(void)ticketBuffer;
	(void)ticketBufferSize;
	(void)ticketLength;
	(void)ticketHandle;
	return QL_Steamworks_RequestAuthTicket( ticketBuffer, ticketBufferSize, ticketLength, ticketHandle );
}

/*
=============
QLR_Steamworks_Validate
=============
*/
qboolean QLR_Steamworks_Validate( const char *ticketHex, ql_auth_response_t *response ) {
	return QL_Steamworks_ValidateTicket( ticketHex, response );
}

/*
=============
QLR_Steamworks_Shutdown
=============
*/
void QLR_Steamworks_Shutdown( void ) {
	QL_Steamworks_Shutdown();
}

#endif

