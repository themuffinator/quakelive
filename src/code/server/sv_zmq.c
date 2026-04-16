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
// sv_zmq.c -- retained Quake Live server-side ZMQ runtime and publication path

#include "server.h"

#if defined(_WIN32)
#include <winsock2.h>
#include <windows.h>
#define QL_ZMQ_LIB_PRIMARY "libzmq.dll"
#define QL_ZMQ_LIB_SECONDARY "zmq.dll"
#define QL_ZMQ_SYM( name ) GetProcAddress( (HMODULE)s_zmq.library, name )
#define QL_ZMQ_OPEN( name ) LoadLibraryA( name )
#define QL_ZMQ_CLOSE() FreeLibrary( (HMODULE)s_zmq.library )
typedef SOCKET ql_zmq_os_socket_t;
#else
#include <dlfcn.h>
#define QL_ZMQ_LIB_PRIMARY "libzmq.so.5"
#define QL_ZMQ_LIB_SECONDARY "libzmq.so"
#define QL_ZMQ_SYM( name ) dlsym( s_zmq.library, name )
#define QL_ZMQ_OPEN( name ) dlopen( name, RTLD_LAZY | RTLD_LOCAL )
#define QL_ZMQ_CLOSE() dlclose( s_zmq.library )
typedef int ql_zmq_os_socket_t;
#endif

#define QL_ZMQ_REP 4
#define QL_ZMQ_PUB 1
#define QL_ZMQ_ROUTER 6
#define QL_ZMQ_DONTWAIT 1
#define QL_ZMQ_SNDMORE 2
#define QL_ZMQ_POLLIN 1
#define QL_ZMQ_RCVMORE 13
#define QL_ZMQ_ROUTER_MANDATORY 33
#define QL_ZMQ_PLAIN_SERVER 44
#define QL_ZMQ_ZAP_DOMAIN 55

#define QL_ZMQ_ENDPOINT_MAX 256
#define QL_ZMQ_MAX_IDENTITY 256
#define QL_ZMQ_MAX_PUBLISH 32768
#define QL_ZMQ_PASSFILE "zmqpass.txt"
#define QL_ZMQ_STATS_TRANSCRIPT "zmq_stats.ndjson"
#define QL_ZMQ_ZAP_ENDPOINT "inproc://zeromq.zap.01"

typedef struct ql_zmq_pollitem_s {
	void				*socket;
	ql_zmq_os_socket_t	fd;
	short				events;
	short				revents;
} ql_zmq_pollitem_t;

typedef void *(*ql_zmq_ctx_new_fn)( void );
typedef int (*ql_zmq_ctx_term_fn)( void *context );
typedef void *(*ql_zmq_socket_fn)( void *context, int type );
typedef int (*ql_zmq_close_fn)( void *socket );
typedef int (*ql_zmq_bind_fn)( void *socket, const char *endpoint );
typedef int (*ql_zmq_setsockopt_fn)( void *socket, int option, const void *value, size_t valueSize );
typedef int (*ql_zmq_getsockopt_fn)( void *socket, int option, void *value, size_t *valueSize );
typedef int (*ql_zmq_send_fn)( void *socket, const void *buffer, size_t length, int flags );
typedef int (*ql_zmq_recv_fn)( void *socket, void *buffer, size_t length, int flags );
typedef int (*ql_zmq_poll_fn)( ql_zmq_pollitem_t *items, int itemCount, long timeout );
typedef int (*ql_zmq_errno_fn)( void );
typedef const char *(*ql_zmq_strerror_fn)( int error );

typedef struct zmqRconPeer_s {
	int						identityLength;
	char					identity[QL_ZMQ_MAX_IDENTITY];
	char					label[QL_ZMQ_MAX_IDENTITY];
	struct zmqRconPeer_s	*prev;
	struct zmqRconPeer_s	*next;
} zmqRconPeer_t;

typedef struct {
	void					*library;
	void					*context;
	void					*authSocket;
	void					*pubSocket;
	void					*rconSocket;
	fileHandle_t			statsTranscript;
	zmqRconPeer_t			*rconPeers;
	char					statsEndpoint[QL_ZMQ_ENDPOINT_MAX];
	char					rconEndpoint[QL_ZMQ_ENDPOINT_MAX];
	char					statsPassword[MAX_STRING_CHARS];
	char					rconPassword[MAX_STRING_CHARS];
	int						statsPasswordRevision;
	int						rconPasswordRevision;
	qboolean				passwordsPrimed;
	qboolean				broadcastingRconOutput;
	qboolean				buildDisabledLogged;
	qboolean				runtimeUnavailableLogged;
	ql_zmq_ctx_new_fn		zmq_ctx_new;
	ql_zmq_ctx_term_fn		zmq_ctx_term;
	ql_zmq_socket_fn		zmq_socket;
	ql_zmq_close_fn			zmq_close;
	ql_zmq_bind_fn			zmq_bind;
	ql_zmq_setsockopt_fn	zmq_setsockopt;
	ql_zmq_getsockopt_fn	zmq_getsockopt;
	ql_zmq_send_fn			zmq_send;
	ql_zmq_recv_fn			zmq_recv;
	ql_zmq_poll_fn			zmq_poll;
	ql_zmq_errno_fn			zmq_errno;
	ql_zmq_strerror_fn		zmq_strerror;
} idZMQ_t;

static idZMQ_t s_zmq;
static cvar_t *s_zmqRconEnable;
static cvar_t *s_zmqStatsEnable;
static cvar_t *s_zmqRconIp;
static cvar_t *s_zmqRconPort;
static cvar_t *s_zmqStatsIp;
static cvar_t *s_zmqStatsPort;
static cvar_t *s_zmqRconPassword;
static cvar_t *s_zmqStatsPassword;

/*
==================
idZMQ_ResetResolvedSymbols
==================
*/
static void idZMQ_ResetResolvedSymbols( void ) {
	s_zmq.zmq_ctx_new = NULL;
	s_zmq.zmq_ctx_term = NULL;
	s_zmq.zmq_socket = NULL;
	s_zmq.zmq_close = NULL;
	s_zmq.zmq_bind = NULL;
	s_zmq.zmq_setsockopt = NULL;
	s_zmq.zmq_getsockopt = NULL;
	s_zmq.zmq_send = NULL;
	s_zmq.zmq_recv = NULL;
	s_zmq.zmq_poll = NULL;
	s_zmq.zmq_errno = NULL;
	s_zmq.zmq_strerror = NULL;
}

/*
==================
idZMQ_LoadSymbol
==================
*/
static qboolean idZMQ_LoadSymbol( void **target, const char *name ) {
	*target = QL_ZMQ_SYM( name );
	return (qboolean)( *target != NULL );
}

/*
==================
idZMQ_LoadOptionalSymbol
==================
*/
static void idZMQ_LoadOptionalSymbol( void **target, const char *name ) {
	*target = QL_ZMQ_SYM( name );
}

/*
==================
idZMQ_LastErrorString
==================
*/
static const char *idZMQ_LastErrorString( void ) {
	int error;

	if ( !s_zmq.zmq_errno || !s_zmq.zmq_strerror ) {
		return "unknown";
	}

	error = s_zmq.zmq_errno();
	return s_zmq.zmq_strerror( error );
}

/*
==================
idZMQ_LogRuntimeUnavailable
==================
*/
static void idZMQ_LogRuntimeUnavailable( const char *reason ) {
	if ( s_zmq.runtimeUnavailableLogged ) {
		return;
	}

	s_zmq.runtimeUnavailableLogged = qtrue;
	Com_Printf( "ZMQ runtime unavailable: %s\n", reason );
}

/*
==================
idZMQ_LoadLibrary
==================
*/
static qboolean idZMQ_LoadLibrary( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( !s_zmq.buildDisabledLogged ) {
		s_zmq.buildDisabledLogged = qtrue;
		Com_Printf( "ZMQ runtime disabled by build policy (QL_BUILD_ONLINE_SERVICES=0); keeping retained fallback paths.\n" );
	}
	return qfalse;
#else
	const char *candidates[] = {
		QL_ZMQ_LIB_PRIMARY,
		QL_ZMQ_LIB_SECONDARY
	};
	int i;

	if ( s_zmq.library ) {
		return qtrue;
	}

	for ( i = 0; i < ARRAY_LEN( candidates ); i++ ) {
		s_zmq.library = QL_ZMQ_OPEN( candidates[i] );
		if ( s_zmq.library ) {
			break;
		}
	}

	if ( !s_zmq.library ) {
		idZMQ_LogRuntimeUnavailable( "unable to load libzmq" );
		return qfalse;
	}

	if ( !idZMQ_LoadSymbol( (void **)&s_zmq.zmq_ctx_new, "zmq_ctx_new" ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_ctx_term, "zmq_ctx_term" ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_socket, "zmq_socket" ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_close, "zmq_close" ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_bind, "zmq_bind" ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_send, "zmq_send" ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_recv, "zmq_recv" ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_poll, "zmq_poll" ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_errno, "zmq_errno" ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_strerror, "zmq_strerror" ) ) {
		idZMQ_LogRuntimeUnavailable( "libzmq is missing required exports" );
		QL_ZMQ_CLOSE();
		s_zmq.library = NULL;
		idZMQ_ResetResolvedSymbols();
		return qfalse;
	}

	idZMQ_LoadOptionalSymbol( (void **)&s_zmq.zmq_setsockopt, "zmq_setsockopt" );
	idZMQ_LoadOptionalSymbol( (void **)&s_zmq.zmq_getsockopt, "zmq_getsockopt" );
	return qtrue;
#endif
}

/*
==================
idZMQ_UnloadLibrary
==================
*/
static void idZMQ_UnloadLibrary( void ) {
	if ( s_zmq.library ) {
		QL_ZMQ_CLOSE();
		s_zmq.library = NULL;
	}

	idZMQ_ResetResolvedSymbols();
}

/*
==================
idZMQ_CloseSocket
==================
*/
static void idZMQ_CloseSocket( void **socketPointer ) {
	if ( *socketPointer && s_zmq.zmq_close ) {
		s_zmq.zmq_close( *socketPointer );
	}

	*socketPointer = NULL;
}

/*
==================
idZMQ_CloseStatsTranscript
==================
*/
static void idZMQ_CloseStatsTranscript( void ) {
	if ( s_zmq.statsTranscript ) {
		FS_FCloseFile( s_zmq.statsTranscript );
		s_zmq.statsTranscript = 0;
	}
}

/*
==================
idZMQ_CloseAuthSocket
==================
*/
static void idZMQ_CloseAuthSocket( void ) {
	idZMQ_CloseSocket( &s_zmq.authSocket );
}

/*
==================
idZMQ_OpenStatsTranscript
==================
*/
static void idZMQ_OpenStatsTranscript( void ) {
	if ( s_zmq.statsTranscript || !FS_Initialized() ) {
		return;
	}

	s_zmq.statsTranscript = FS_FOpenFileWrite( QL_ZMQ_STATS_TRANSCRIPT );
}

/*
==================
idZMQ_WritePasswordFile
==================
*/
static void idZMQ_WritePasswordFile( void ) {
	fileHandle_t passFile;
	char line[MAX_STRING_CHARS + 32];
	int lineLength;

	if ( !FS_Initialized() ) {
		return;
	}

	passFile = FS_FOpenFileWrite( QL_ZMQ_PASSFILE );
	if ( !passFile ) {
		Com_Printf( "Failed to open %s\n", QL_ZMQ_PASSFILE );
		return;
	}

	if ( s_zmq.statsPassword[0] ) {
		Com_sprintf( line, sizeof( line ), "stats_stats=%s\n", s_zmq.statsPassword );
		lineLength = strlen( line );
		FS_Write( line, lineLength, passFile );
	}

	if ( s_zmq.rconPassword[0] ) {
		Com_sprintf( line, sizeof( line ), "rcon_rcon=%s\n", s_zmq.rconPassword );
		lineLength = strlen( line );
		FS_Write( line, lineLength, passFile );
	}

	FS_FCloseFile( passFile );
}

/*
==================
idZMQ_ReadFrameString
==================
*/
static int idZMQ_ReadFrameString( void *socket, char *buffer, size_t bufferSize, qboolean *more ) {
	int length;
	int moreValue;
	size_t moreSize;

	if ( bufferSize > 0 ) {
		buffer[0] = '\0';
	}
	if ( more ) {
		*more = qfalse;
	}

	length = s_zmq.zmq_recv( socket, buffer, bufferSize > 0 ? bufferSize - 1 : 0, QL_ZMQ_DONTWAIT );
	if ( length < 0 ) {
		return length;
	}
	if ( bufferSize > 0 ) {
		if ( length >= (int)bufferSize ) {
			length = (int)bufferSize - 1;
		}
		buffer[length] = '\0';
	}
	if ( !more || !s_zmq.zmq_getsockopt ) {
		return length;
	}

	moreValue = 0;
	moreSize = sizeof( moreValue );
	if ( s_zmq.zmq_getsockopt( socket, QL_ZMQ_RCVMORE, &moreValue, &moreSize ) == 0 && moreValue ) {
		*more = qtrue;
	}

	return length;
}

/*
==================
idZMQ_DrainRemainingFrames
==================
*/
static void idZMQ_DrainRemainingFrames( void *socket, qboolean more ) {
	char scratch[MAX_STRING_CHARS];

	while ( more ) {
		if ( idZMQ_ReadFrameString( socket, scratch, sizeof( scratch ), &more ) < 0 ) {
			break;
		}
	}
}

/*
==================
idZMQ_FindRconPeer
==================
*/
static zmqRconPeer_t *idZMQ_FindRconPeer( const char *identity ) {
	zmqRconPeer_t *peer;

	for ( peer = s_zmq.rconPeers; peer; peer = peer->next ) {
		if ( !Q_stricmp( peer->identity, identity ) ) {
			return peer;
		}
	}

	return NULL;
}

/*
==================
idZMQ_InsertRconPeer
==================
*/
static zmqRconPeer_t *idZMQ_InsertRconPeer( const char *identity ) {
	zmqRconPeer_t *peer;
	zmqRconPeer_t *cursor;
	zmqRconPeer_t *previous;

	if ( !identity || !identity[0] ) {
		return NULL;
	}
	if ( idZMQ_FindRconPeer( identity ) ) {
		return NULL;
	}

	peer = Z_Malloc( sizeof( *peer ) );
	Com_Memset( peer, 0, sizeof( *peer ) );
	Q_strncpyz( peer->identity, identity, sizeof( peer->identity ) );
	Q_strncpyz( peer->label, identity, sizeof( peer->label ) );
	peer->identityLength = strlen( peer->identity );

	previous = NULL;
	for ( cursor = s_zmq.rconPeers; cursor; cursor = cursor->next ) {
		if ( Q_stricmp( cursor->identity, peer->identity ) > 0 ) {
			break;
		}
		previous = cursor;
	}

	peer->prev = previous;
	peer->next = cursor;
	if ( previous ) {
		previous->next = peer;
	} else {
		s_zmq.rconPeers = peer;
	}
	if ( cursor ) {
		cursor->prev = peer;
	}

	return peer;
}

/*
==================
idZMQ_EraseRconPeer
==================
*/
static void idZMQ_EraseRconPeer( zmqRconPeer_t *peer ) {
	if ( !peer ) {
		return;
	}

	if ( peer->prev ) {
		peer->prev->next = peer->next;
	} else {
		s_zmq.rconPeers = peer->next;
	}
	if ( peer->next ) {
		peer->next->prev = peer->prev;
	}

	Z_Free( peer );
}

/*
==================
idZMQ_ClearRconPeers
==================
*/
static void idZMQ_ClearRconPeers( void ) {
	zmqRconPeer_t *peer;
	zmqRconPeer_t *next;

	for ( peer = s_zmq.rconPeers; peer; peer = next ) {
		next = peer->next;
		Z_Free( peer );
	}

	s_zmq.rconPeers = NULL;
}

/*
==================
idZMQ_ResolveStatsHost
==================
*/
static void idZMQ_ResolveStatsHost( char *resolvedAddress, size_t resolvedIpSize ) {
	char resolvedIp[64];
	netadr_t address;

	if ( s_zmqStatsIp && s_zmqStatsIp->string[0] ) {
		Q_strncpyz( resolvedAddress, s_zmqStatsIp->string, resolvedIpSize );
		return;
	}

	Cvar_VariableStringBuffer( "net_ip", resolvedIp, sizeof( resolvedIp ) );
	if ( !resolvedIp[0] ) {
		Q_strncpyz( resolvedIp, "localhost", sizeof( resolvedIp ) );
	}

	if ( NET_StringToAdr( resolvedIp, &address ) &&
		( address.type == NA_IP || address.type == NA_LOOPBACK ) ) {
		Com_sprintf( resolvedAddress, resolvedIpSize, "%u.%u.%u.%u",
			address.ip[0], address.ip[1], address.ip[2], address.ip[3] );
		return;
	}

	Q_strncpyz( resolvedAddress, resolvedIp, resolvedIpSize );
}

/*
==================
idZMQ_ResolveRconEndpoint
==================
*/
static void idZMQ_ResolveRconEndpoint( char *endpoint, size_t endpointSize ) {
	char resolvedIp[64];
	int resolvedPort;

	if ( s_zmqRconIp && s_zmqRconIp->string[0] ) {
		Q_strncpyz( resolvedIp, s_zmqRconIp->string, sizeof( resolvedIp ) );
	} else {
		Q_strncpyz( resolvedIp, "0.0.0.0", sizeof( resolvedIp ) );
	}

	resolvedPort = ( s_zmqRconPort && s_zmqRconPort->string[0] ) ? s_zmqRconPort->integer : 28960;
	Com_sprintf( endpoint, endpointSize, "tcp://%s:%i", resolvedIp, resolvedPort );
}

/*
==================
idZMQ_ResolveStatsEndpoint
==================
*/
static void idZMQ_ResolveStatsEndpoint( char *endpoint, size_t endpointSize ) {
	char resolvedIp[64];
	int resolvedPort;
	cvar_t *netPort;

	idZMQ_ResolveStatsHost( resolvedIp, sizeof( resolvedIp ) );

	if ( s_zmqStatsPort && s_zmqStatsPort->string[0] ) {
		resolvedPort = s_zmqStatsPort->integer;
	} else {
		netPort = Cvar_Get( "net_port", va( "%i", PORT_SERVER ), CVAR_LATCH );
		resolvedPort = netPort->integer;
	}

	Com_sprintf( endpoint, endpointSize, "tcp://%s:%i", resolvedIp, resolvedPort );
}

/*
==================
idZMQ_EnsureRuntime
==================
*/
static qboolean idZMQ_EnsureRuntime( void ) {
	if ( s_zmq.context ) {
		return qtrue;
	}

	if ( !idZMQ_LoadLibrary() ) {
		return qfalse;
	}

	s_zmq.context = s_zmq.zmq_ctx_new();
	if ( !s_zmq.context ) {
		idZMQ_LogRuntimeUnavailable( va( "failed to create context: %s", idZMQ_LastErrorString() ) );
		return qfalse;
	}

	return qtrue;
}

/*
==================
idZMQ_TrySetSocketInt
==================
*/
static void idZMQ_TrySetSocketInt( void *socket, int option, int value ) {
	if ( !socket || !s_zmq.zmq_setsockopt ) {
		return;
	}

	s_zmq.zmq_setsockopt( socket, option, &value, sizeof( value ) );
}

/*
==================
idZMQ_TrySetSocketString
==================
*/
static void idZMQ_TrySetSocketString( void *socket, int option, const char *value ) {
	if ( !socket || !s_zmq.zmq_setsockopt || !value ) {
		return;
	}

	s_zmq.zmq_setsockopt( socket, option, value, strlen( value ) );
}

/*
==================
idZMQ_SendAuthFrame
==================
*/
static int idZMQ_SendAuthFrame( void *socket, const char *value, qboolean more ) {
	const char *frame;
	int flags;

	frame = value ? value : "";
	flags = more ? QL_ZMQ_SNDMORE : 0;
	return s_zmq.zmq_send( socket, frame, strlen( frame ), flags );
}

/*
==================
idZMQ_SendAuthResponse
==================
*/
static void idZMQ_SendAuthResponse( const char *version, const char *requestId, const char *statusCode, const char *statusText, const char *userId ) {
	if ( !s_zmq.authSocket || !s_zmq.zmq_send ) {
		return;
	}

	if ( idZMQ_SendAuthFrame( s_zmq.authSocket, version, qtrue ) < 0 ||
		idZMQ_SendAuthFrame( s_zmq.authSocket, requestId, qtrue ) < 0 ||
		idZMQ_SendAuthFrame( s_zmq.authSocket, statusCode, qtrue ) < 0 ||
		idZMQ_SendAuthFrame( s_zmq.authSocket, statusText, qtrue ) < 0 ||
		idZMQ_SendAuthFrame( s_zmq.authSocket, userId, qtrue ) < 0 ) {
		return;
	}

	idZMQ_SendAuthFrame( s_zmq.authSocket, "", qfalse );
}

/*
==================
idZMQ_ValidatePlainCredentials
==================
*/
static qboolean idZMQ_ValidatePlainCredentials( const char *domain, const char *username, const char *password, const char **userId ) {
	const char *expectedPassword;
	const char *expectedUsername;

	expectedPassword = "";
	expectedUsername = "";
	if ( userId ) {
		*userId = "";
	}

	if ( !Q_stricmp( domain, "rcon" ) ) {
		expectedUsername = "rcon";
		expectedPassword = s_zmq.rconPassword;
	} else if ( !Q_stricmp( domain, "stats" ) ) {
		expectedUsername = "stats";
		expectedPassword = s_zmq.statsPassword;
	} else {
		return qfalse;
	}

	if ( !expectedPassword[0] ) {
		return qfalse;
	}
	if ( Q_stricmp( username, expectedUsername ) != 0 || strcmp( password, expectedPassword ) != 0 ) {
		return qfalse;
	}

	if ( userId ) {
		*userId = expectedUsername;
	}

	return qtrue;
}

/*
==================
idZMQ_EnsureAuthSocket
==================
*/
static qboolean idZMQ_EnsureAuthSocket( void ) {
	void *socket;
	int enabled;

	enabled = ( s_zmqRconEnable && s_zmqRconEnable->integer ) || ( s_zmqStatsEnable && s_zmqStatsEnable->integer );
	if ( !enabled ) {
		idZMQ_CloseAuthSocket();
		return qfalse;
	}
	if ( s_zmq.authSocket ) {
		return qtrue;
	}
	if ( !idZMQ_EnsureRuntime() ) {
		return qfalse;
	}

	socket = s_zmq.zmq_socket( s_zmq.context, QL_ZMQ_REP );
	if ( !socket ) {
		idZMQ_LogRuntimeUnavailable( va( "failed to create auth socket: %s", idZMQ_LastErrorString() ) );
		return qfalse;
	}
	if ( s_zmq.zmq_bind( socket, QL_ZMQ_ZAP_ENDPOINT ) != 0 ) {
		idZMQ_LogRuntimeUnavailable( va( "failed to bind auth socket: %s", idZMQ_LastErrorString() ) );
		s_zmq.zmq_close( socket );
		return qfalse;
	}

	s_zmq.authSocket = socket;
	return qtrue;
}

/*
==================
idZMQ_PumpAuthSocket
==================
*/
static void idZMQ_PumpAuthSocket( void ) {
	ql_zmq_pollitem_t item;
	char version[16];
	char requestId[64];
	char domain[64];
	char address[128];
	char identity[QL_ZMQ_MAX_IDENTITY];
	char mechanism[16];
	char username[QL_ZMQ_MAX_IDENTITY];
	char password[MAX_STRING_CHARS];
	const char *statusCode;
	const char *statusText;
	const char *userId;
	int length;
	qboolean more;

	if ( !idZMQ_EnsureAuthSocket() || !s_zmq.zmq_poll || !s_zmq.zmq_recv || !s_zmq.zmq_send ) {
		return;
	}

	item.socket = s_zmq.authSocket;
	item.fd = 0;
	item.events = QL_ZMQ_POLLIN;
	item.revents = 0;

	while ( s_zmq.zmq_poll( &item, 1, 0 ) > 0 && ( item.revents & QL_ZMQ_POLLIN ) ) {
		Q_strncpyz( version, "1.0", sizeof( version ) );
		requestId[0] = '\0';
		domain[0] = '\0';
		address[0] = '\0';
		identity[0] = '\0';
		mechanism[0] = '\0';
		username[0] = '\0';
		password[0] = '\0';
		statusCode = "400";
		statusText = "BAD REQUEST";
		userId = "";
		more = qfalse;

		length = idZMQ_ReadFrameString( s_zmq.authSocket, version, sizeof( version ), &more );
		if ( length < 0 ) {
			break;
		}
		if ( !more ) {
			idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
			item.revents = 0;
			continue;
		}

		length = idZMQ_ReadFrameString( s_zmq.authSocket, requestId, sizeof( requestId ), &more );
		if ( length < 0 ) {
			break;
		}
		if ( !more ) {
			idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
			item.revents = 0;
			continue;
		}

		length = idZMQ_ReadFrameString( s_zmq.authSocket, domain, sizeof( domain ), &more );
		if ( length < 0 ) {
			break;
		}
		if ( !more ) {
			idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
			item.revents = 0;
			continue;
		}

		length = idZMQ_ReadFrameString( s_zmq.authSocket, address, sizeof( address ), &more );
		if ( length < 0 ) {
			break;
		}
		if ( !more ) {
			idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
			item.revents = 0;
			continue;
		}

		length = idZMQ_ReadFrameString( s_zmq.authSocket, identity, sizeof( identity ), &more );
		if ( length < 0 ) {
			break;
		}
		if ( !more ) {
			idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
			item.revents = 0;
			continue;
		}

		length = idZMQ_ReadFrameString( s_zmq.authSocket, mechanism, sizeof( mechanism ), &more );
		if ( length < 0 ) {
			break;
		}
		if ( !Q_stricmp( mechanism, "NULL" ) ) {
			statusCode = "200";
			statusText = "OK";
			idZMQ_DrainRemainingFrames( s_zmq.authSocket, more );
			idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
			item.revents = 0;
			continue;
		}
		if ( !Q_stricmp( mechanism, "PLAIN" ) ) {
			if ( !more ) {
				idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
				item.revents = 0;
				continue;
			}

			length = idZMQ_ReadFrameString( s_zmq.authSocket, username, sizeof( username ), &more );
			if ( length < 0 ) {
				break;
			}
			if ( !more ) {
				idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
				item.revents = 0;
				continue;
			}

			length = idZMQ_ReadFrameString( s_zmq.authSocket, password, sizeof( password ), &more );
			if ( length < 0 ) {
				break;
			}

			statusText = "NO ACCESS";
			if ( idZMQ_ValidatePlainCredentials( domain, username, password, &userId ) ) {
				statusCode = "200";
				statusText = "OK";
			}
			idZMQ_DrainRemainingFrames( s_zmq.authSocket, more );
			idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
			item.revents = 0;
			continue;
		}

		idZMQ_DrainRemainingFrames( s_zmq.authSocket, more );
		idZMQ_SendAuthResponse( version, requestId, statusCode, "NO ACCESS", userId );
		item.revents = 0;
	}
}

/*
==================
idZMQ_ApplyPasswords
==================
*/
static void idZMQ_ApplyPasswords( qboolean rconModeChanged, qboolean statsModeChanged ) {
	idZMQ_WritePasswordFile();

	if ( rconModeChanged ) {
		idZMQ_ClearRconPeers();
		idZMQ_CloseSocket( &s_zmq.rconSocket );
		s_zmq.rconEndpoint[0] = '\0';
	}
	if ( statsModeChanged ) {
		idZMQ_CloseSocket( &s_zmq.pubSocket );
		s_zmq.statsEndpoint[0] = '\0';
	}
	if ( rconModeChanged || statsModeChanged ) {
		idZMQ_CloseAuthSocket();
	}
	if ( statsModeChanged ) {
		idZMQ_EnsureStatsPublisher();
	}
	if ( rconModeChanged ) {
		idZMQ_EnsureRconSocket();
	}
}

/*
==================
idZMQ_EnsureRconSocket
==================
*/
static qboolean idZMQ_EnsureRconSocket( void ) {
	void *socket;
	int enabled;

	enabled = ( s_zmqRconEnable && s_zmqRconEnable->integer );
	if ( !enabled ) {
		idZMQ_ClearRconPeers();
		idZMQ_CloseSocket( &s_zmq.rconSocket );
		s_zmq.rconEndpoint[0] = '\0';
		return qfalse;
	}

	if ( s_zmq.rconSocket ) {
		return qtrue;
	}

	if ( !idZMQ_EnsureRuntime() ) {
		return qfalse;
	}
	if ( !idZMQ_EnsureAuthSocket() ) {
		return qfalse;
	}

	socket = s_zmq.zmq_socket( s_zmq.context, QL_ZMQ_ROUTER );
	if ( !socket ) {
		idZMQ_LogRuntimeUnavailable( va( "failed to create RCON socket: %s", idZMQ_LastErrorString() ) );
		return qfalse;
	}

	idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, "rcon" );
	idZMQ_TrySetSocketInt( socket, QL_ZMQ_ROUTER_MANDATORY, 1 );
	idZMQ_TrySetSocketInt( socket, QL_ZMQ_PLAIN_SERVER, s_zmq.rconPassword[0] ? 1 : 0 );
	idZMQ_ResolveRconEndpoint( s_zmq.rconEndpoint, sizeof( s_zmq.rconEndpoint ) );
	if ( s_zmq.zmq_bind( socket, s_zmq.rconEndpoint ) != 0 ) {
		Com_Printf( "zmq RCON socket error, bind failed: %s\n", idZMQ_LastErrorString() );
		s_zmq.zmq_close( socket );
		return qfalse;
	}

	s_zmq.rconSocket = socket;
	Com_Printf( "zmq RCON socket: %s\n", s_zmq.rconEndpoint );
	return qtrue;
}

/*
==================
idZMQ_EnsureStatsPublisher
==================
*/
static qboolean idZMQ_EnsureStatsPublisher( void ) {
	void *socket;
	int enabled;

	enabled = ( s_zmqStatsEnable && s_zmqStatsEnable->integer );
	if ( !enabled ) {
		idZMQ_CloseStatsTranscript();
		idZMQ_CloseSocket( &s_zmq.pubSocket );
		s_zmq.statsEndpoint[0] = '\0';
		return qfalse;
	}

	idZMQ_OpenStatsTranscript();
	if ( s_zmq.pubSocket ) {
		return qtrue;
	}

	if ( !idZMQ_EnsureRuntime() ) {
		return qfalse;
	}
	if ( !idZMQ_EnsureAuthSocket() ) {
		return qfalse;
	}

	socket = s_zmq.zmq_socket( s_zmq.context, QL_ZMQ_PUB );
	if ( !socket ) {
		idZMQ_LogRuntimeUnavailable( va( "failed to create stats publisher socket: %s", idZMQ_LastErrorString() ) );
		return qfalse;
	}

	idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, "stats" );
	idZMQ_TrySetSocketInt( socket, QL_ZMQ_PLAIN_SERVER, s_zmq.statsPassword[0] ? 1 : 0 );
	idZMQ_ResolveStatsEndpoint( s_zmq.statsEndpoint, sizeof( s_zmq.statsEndpoint ) );
	if ( s_zmq.zmq_bind( socket, s_zmq.statsEndpoint ) != 0 ) {
		Com_Printf( "zmq PUB socket error, bind failed: %s\n", idZMQ_LastErrorString() );
		s_zmq.zmq_close( socket );
		return qfalse;
	}

	s_zmq.pubSocket = socket;
	Com_Printf( "zmq PUB socket: %s\n", s_zmq.statsEndpoint );
	return qtrue;
}

/*
==================
idZMQ_BuildPublication
==================
*/
static void idZMQ_BuildPublication( const char *type, const char *payload, char *buffer, size_t bufferSize ) {
	if ( payload && payload[0] ) {
		Com_sprintf( buffer, bufferSize, "{\"TYPE\":\"%s\",\"DATA\":%s}\n", type, payload );
	} else {
		Com_sprintf( buffer, bufferSize, "{\"TYPE\":\"%s\",\"DATA\":null}\n", type );
	}
}

/*
==================
idZMQ_WriteStatsTranscript
==================
*/
static void idZMQ_WriteStatsTranscript( const char *message ) {
	int length;

	if ( !s_zmqStatsEnable || !s_zmqStatsEnable->integer || !message || !message[0] ) {
		return;
	}

	idZMQ_OpenStatsTranscript();
	if ( !s_zmq.statsTranscript ) {
		return;
	}

	length = (int)strlen( message );
	if ( length > 0 ) {
		FS_Write( message, length, s_zmq.statsTranscript );
	}
}

/*
==================
idZMQ_Publish
==================
*/
static void idZMQ_Publish( const char *type, const char *payload ) {
	char message[QL_ZMQ_MAX_PUBLISH];

	if ( !s_zmqStatsEnable || !s_zmqStatsEnable->integer ) {
		return;
	}

	idZMQ_BuildPublication( type, payload, message, sizeof( message ) );
	idZMQ_WriteStatsTranscript( message );
	idZMQ_EnsureStatsPublisher();
	if ( s_zmq.pubSocket && s_zmq.zmq_send ) {
		s_zmq.zmq_send( s_zmq.pubSocket, message, strlen( message ), 0 );
	}
}

/*
==================
Zmq_RegisterCvarsAndInitRcon
==================
*/
void Zmq_RegisterCvarsAndInitRcon( void ) {
	s_zmqRconEnable = Cvar_Get( "zmq_rcon_enable", "0", CVAR_ARCHIVE );
	s_zmqStatsEnable = Cvar_Get( "zmq_stats_enable", "0", CVAR_ARCHIVE );
	s_zmqRconIp = Cvar_Get( "zmq_rcon_ip", "0.0.0.0", CVAR_ARCHIVE );
	s_zmqRconPort = Cvar_Get( "zmq_rcon_port", "28960", CVAR_ARCHIVE );
	s_zmqStatsIp = Cvar_Get( "zmq_stats_ip", "", CVAR_ARCHIVE );
	s_zmqStatsPort = Cvar_Get( "zmq_stats_port", "", CVAR_ARCHIVE );
	s_zmqStatsPassword = Cvar_Get( "zmq_stats_password", "", CVAR_ARCHIVE | CVAR_PROTECTED );
	s_zmqRconPassword = Cvar_Get( "zmq_rcon_password", "", CVAR_ARCHIVE | CVAR_PROTECTED );

	Zmq_UpdatePasswords();
	idZMQ_EnsureRconSocket();
}

/*
==================
Zmq_UpdatePasswords
==================
*/
void Zmq_UpdatePasswords( void ) {
	qboolean statsModeChanged;
	qboolean rconModeChanged;
	qboolean changed;

	if ( !s_zmqStatsPassword || !s_zmqRconPassword ) {
		return;
	}

	if ( !s_zmq.passwordsPrimed ) {
		Q_strncpyz( s_zmq.statsPassword, s_zmqStatsPassword->string, sizeof( s_zmq.statsPassword ) );
		Q_strncpyz( s_zmq.rconPassword, s_zmqRconPassword->string, sizeof( s_zmq.rconPassword ) );
		s_zmq.statsPasswordRevision = s_zmqStatsPassword->modificationCount;
		s_zmq.rconPasswordRevision = s_zmqRconPassword->modificationCount;
		s_zmq.passwordsPrimed = qtrue;
		idZMQ_ApplyPasswords( qfalse, qfalse );
		return;
	}

	changed = (qboolean)( s_zmq.statsPasswordRevision != s_zmqStatsPassword->modificationCount ||
		s_zmq.rconPasswordRevision != s_zmqRconPassword->modificationCount );
	if ( !changed ) {
		return;
	}

	statsModeChanged = (qboolean)( ( s_zmq.statsPassword[0] != '\0' ) != ( s_zmqStatsPassword->string[0] != '\0' ) );
	rconModeChanged = (qboolean)( ( s_zmq.rconPassword[0] != '\0' ) != ( s_zmqRconPassword->string[0] != '\0' ) );
	Q_strncpyz( s_zmq.statsPassword, s_zmqStatsPassword->string, sizeof( s_zmq.statsPassword ) );
	Q_strncpyz( s_zmq.rconPassword, s_zmqRconPassword->string, sizeof( s_zmq.rconPassword ) );
	s_zmq.statsPasswordRevision = s_zmqStatsPassword->modificationCount;
	s_zmq.rconPasswordRevision = s_zmqRconPassword->modificationCount;
	idZMQ_ApplyPasswords( rconModeChanged, statsModeChanged );
	Com_Printf( "zmq stats and rcon passwords updated\n" );
}

/*
==================
Zmq_InitStatsPublisher
==================
*/
void Zmq_InitStatsPublisher( void ) {
	idZMQ_CloseStatsTranscript();
	idZMQ_CloseSocket( &s_zmq.pubSocket );
	idZMQ_EnsureStatsPublisher();
}

/*
==================
Zmq_ShutdownStatsPublisher
==================
*/
void Zmq_ShutdownStatsPublisher( void ) {
	idZMQ_CloseStatsTranscript();
	idZMQ_CloseSocket( &s_zmq.pubSocket );
	s_zmq.statsEndpoint[0] = '\0';
}

/*
==================
Zmq_SubmitMatchReport
==================
*/
void Zmq_SubmitMatchReport( const void *report ) {
	idZMQ_Publish( "MATCH_REPORT", (const char *)report );
}

/*
==================
Zmq_ReportPlayerEvent
==================
*/
void Zmq_ReportPlayerEvent( uint32_t steamIdLow, uint32_t steamIdHigh, const void *clientStats, const char *eventName, const void *payload ) {
	(void)steamIdLow;
	(void)steamIdHigh;
	(void)clientStats;

	idZMQ_Publish( eventName && eventName[0] ? eventName : "UNKNOWN_EVENT", (const char *)payload );
}

/*
==================
Zmq_BroadcastRconOutput
==================
*/
void Zmq_BroadcastRconOutput( const char *message ) {
	zmqRconPeer_t *peer;
	zmqRconPeer_t *next;

	if ( !message || !message[0] || !s_zmq.rconSocket || !s_zmq.rconPeers || !s_zmq.zmq_send ) {
		return;
	}
	if ( s_zmq.broadcastingRconOutput ) {
		return;
	}

	s_zmq.broadcastingRconOutput = qtrue;
	for ( peer = s_zmq.rconPeers; peer; peer = next ) {
		next = peer->next;
		if ( s_zmq.zmq_send( s_zmq.rconSocket, peer->identity, peer->identityLength, QL_ZMQ_SNDMORE | QL_ZMQ_DONTWAIT ) < 0 ||
			s_zmq.zmq_send( s_zmq.rconSocket, message, strlen( message ), QL_ZMQ_DONTWAIT ) < 0 ) {
			Com_Printf( "zmq RCON client disconnected: %s\n", peer->label );
			idZMQ_EraseRconPeer( peer );
		}
	}
	s_zmq.broadcastingRconOutput = qfalse;
}

/*
==================
idZMQ_ReadRconCommand
==================
*/
static int idZMQ_ReadRconCommand( char *command, size_t commandSize ) {
	int commandLength;
	qboolean more;

	commandLength = idZMQ_ReadFrameString( s_zmq.rconSocket, command, commandSize, &more );
	if ( commandLength >= 0 ) {
		idZMQ_DrainRemainingFrames( s_zmq.rconSocket, more );
	}
	return commandLength;
}

/*
==================
Zmq_PumpRcon
==================
*/
void Zmq_PumpRcon( void ) {
	ql_zmq_pollitem_t item;
	char identity[QL_ZMQ_MAX_IDENTITY];
	char command[MAX_STRING_CHARS];
	int identityLength;
	int commandLength;
	qboolean more;
	zmqRconPeer_t *peer;

	idZMQ_PumpAuthSocket();
	if ( !idZMQ_EnsureRconSocket() || !s_zmq.zmq_poll || !s_zmq.zmq_recv ) {
		return;
	}

	item.socket = s_zmq.rconSocket;
	item.fd = 0;
	item.events = QL_ZMQ_POLLIN;
	item.revents = 0;

	if ( s_zmq.zmq_poll( &item, 1, 0 ) <= 0 || !( item.revents & QL_ZMQ_POLLIN ) ) {
		return;
	}

	identityLength = idZMQ_ReadFrameString( s_zmq.rconSocket, identity, sizeof( identity ), &more );
	if ( identityLength <= 0 ) {
		idZMQ_DrainRemainingFrames( s_zmq.rconSocket, more );
		return;
	}
	if ( !more ) {
		return;
	}

	commandLength = idZMQ_ReadRconCommand( command, sizeof( command ) );
	if ( commandLength <= 0 ) {
		return;
	}

	peer = idZMQ_FindRconPeer( identity );
	if ( !peer ) {
		peer = idZMQ_InsertRconPeer( identity );
		if ( peer ) {
			Com_Printf( "zmq RCON client connected: %s\n", peer->label );
		}
	}

	if ( peer ) {
		Com_Printf( "zmq RCON command from %s: %s\n", peer->label, command );
	}
	Cmd_ExecuteString( command );
}

/*
==================
Zmq_ShutdownRuntime
==================
*/
void Zmq_ShutdownRuntime( void ) {
	Zmq_ShutdownStatsPublisher();
	idZMQ_ClearRconPeers();
	idZMQ_CloseAuthSocket();
	idZMQ_CloseSocket( &s_zmq.rconSocket );
	s_zmq.rconEndpoint[0] = '\0';
	if ( s_zmq.context && s_zmq.zmq_ctx_term ) {
		s_zmq.zmq_ctx_term( s_zmq.context );
	}
	s_zmq.context = NULL;
	idZMQ_UnloadLibrary();
}
