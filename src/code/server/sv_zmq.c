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
#define QL_ZMQ_NO_FLAGS 0
#define QL_ZMQ_DONTWAIT 1
#define QL_ZMQ_SNDMORE 2
#define QL_ZMQ_SEND_DONTWAIT QL_ZMQ_DONTWAIT
#define QL_ZMQ_SEND_MORE_DONTWAIT ( QL_ZMQ_SNDMORE | QL_ZMQ_DONTWAIT )
#define QL_ZMQ_SEND_SUCCESS_MIN 0
#define QL_ZMQ_POLLIN 1
#define QL_ZMQ_POLL_FD_NONE 0
#define QL_ZMQ_POLL_REVENTS_NONE 0
#define QL_ZMQ_SINGLE_POLL_ITEM 1
#define QL_ZMQ_POLL_TIMEOUT_IMMEDIATE 0
#define QL_ZMQ_POLL_READY_MIN 1
#define QL_ZMQ_RCVMORE 13
#define QL_ZMQ_GETSOCKOPT_SUCCESS 0
#define QL_ZMQ_BIND_SUCCESS 0
#define QL_ZMQ_ROUTER_MANDATORY 33
#define QL_ZMQ_PLAIN_SERVER 44
#define QL_ZMQ_ZAP_DOMAIN 55
#define QL_ZMQ_SOCKET_OPTION_DISABLED 0
#define QL_ZMQ_SOCKET_OPTION_ENABLED 1
#define QL_ZMQ_SOCKET_OPTION_INT_SIZE sizeof( int )
#define QL_ZMQ_SOCKET_OPTION_STRING_SIZE( value ) strlen( value )
#define QL_ZMQ_SOCKET_SLOT_EMPTY NULL
#define QL_ZMQ_CONTEXT_SLOT_EMPTY NULL
#define QL_ZMQ_LIBRARY_SLOT_EMPTY NULL
#define QL_ZMQ_SYMBOL_SLOT_EMPTY NULL
#define QL_ZMQ_RCON_POLL_SLOT_EMPTY NULL
#define QL_ZMQ_RCON_PEER_SLOT_EMPTY NULL

#define QL_ZMQ_ENDPOINT_MAX 256
#define QL_ZMQ_ENDPOINT_IP_BUFFER_SIZE 64
#define QL_ZMQ_MAX_IDENTITY 256
#define QL_ZMQ_MAX_PUBLISH 32768
#define QL_ZMQ_DRAIN_SCRATCH_SIZE MAX_STRING_CHARS
#define QL_ZMQ_RCON_IDENTITY_BUFFER_SIZE QL_ZMQ_MAX_IDENTITY
#define QL_ZMQ_RCON_COMMAND_BUFFER_SIZE MAX_STRING_CHARS
#define QL_ZMQ_FRAME_READ_SUCCESS_MIN 0
#define QL_ZMQ_RCON_MIN_IDENTITY_LENGTH 1
#define QL_ZMQ_RCON_MIN_COMMAND_LENGTH 1
#define QL_ZMQ_RCON_PEER_COUNT_EMPTY 0
#define QL_ZMQ_STRING_TERMINATOR_LENGTH 1
#define QL_ZMQ_STRING_TERMINATOR '\0'
#define QL_ZMQ_ENDPOINT_EMPTY QL_ZMQ_STRING_TERMINATOR
#define QL_ZMQ_RCVMORE_NONE 0
#define QL_ZMQ_FRAME_MORE qtrue
#define QL_ZMQ_FRAME_NO_MORE qfalse
#define QL_ZMQ_CVAR_RCON_ENABLE "zmq_rcon_enable"
#define QL_ZMQ_CVAR_STATS_ENABLE "zmq_stats_enable"
#define QL_ZMQ_CVAR_RCON_IP "zmq_rcon_ip"
#define QL_ZMQ_CVAR_RCON_PORT "zmq_rcon_port"
#define QL_ZMQ_CVAR_STATS_IP "zmq_stats_ip"
#define QL_ZMQ_CVAR_STATS_PORT "zmq_stats_port"
#define QL_ZMQ_CVAR_RCON_PASSWORD "zmq_rcon_password"
#define QL_ZMQ_CVAR_STATS_PASSWORD "zmq_stats_password"
#define QL_ZMQ_CVAR_NET_IP "net_ip"
#define QL_ZMQ_CVAR_NET_PORT "net_port"
#define QL_ZMQ_CVAR_INIT_FLAGS CVAR_INIT
#define QL_ZMQ_CVAR_PASSWORD_FLAGS CVAR_ARCHIVE
#define QL_ZMQ_CVAR_NET_FALLBACK_FLAGS CVAR_LATCH
#define QL_ZMQ_DEFAULT_DISABLED "0"
#define QL_ZMQ_DEFAULT_EMPTY ""
#define QL_ZMQ_DEFAULT_RCON_IP "0.0.0.0"
#define QL_ZMQ_DEFAULT_RCON_PORT "28960"
#define QL_ZMQ_DEFAULT_RCON_PORT_VALUE 28960
#define QL_ZMQ_DEFAULT_NET_IP "localhost"
#define QL_ZMQ_DEFAULT_NET_PORT_FORMAT "%i"
#define QL_ZMQ_PASSFILE "zmqpass.txt"
#define QL_ZMQ_PASSFILE_RECORD_SLACK 32
#define QL_ZMQ_PASSFILE_RECORD_BUFFER_SIZE ( MAX_STRING_CHARS + QL_ZMQ_PASSFILE_RECORD_SLACK )
#define QL_ZMQ_STATS_TRANSCRIPT "zmq_stats.ndjson"
#define QL_ZMQ_STATS_TRANSCRIPT_HANDLE_EMPTY 0
#define QL_ZMQ_STATS_TRANSCRIPT_RECORD_TERMINATOR "\n"
#define QL_ZMQ_STATS_TRANSCRIPT_RECORD_TERMINATOR_LENGTH 1
#define QL_ZMQ_LAST_ERROR_UNKNOWN "unknown"
#define QL_ZMQ_RUNTIME_UNAVAILABLE_FORMAT "ZMQ runtime unavailable: %s\n"
#define QL_ZMQ_RUNTIME_DISABLED_MESSAGE "ZMQ runtime disabled by build policy (QL_BUILD_ONLINE_SERVICES=0); keeping retained fallback paths.\n"
#define QL_ZMQ_RUNTIME_LOAD_FAILED_REASON "unable to load libzmq"
#define QL_ZMQ_RUNTIME_EXPORTS_MISSING_REASON "libzmq is missing required exports"
#define QL_ZMQ_EXPORT_CTX_NEW "zmq_ctx_new"
#define QL_ZMQ_EXPORT_CTX_TERM "zmq_ctx_term"
#define QL_ZMQ_EXPORT_SOCKET "zmq_socket"
#define QL_ZMQ_EXPORT_CLOSE "zmq_close"
#define QL_ZMQ_EXPORT_BIND "zmq_bind"
#define QL_ZMQ_EXPORT_SEND "zmq_send"
#define QL_ZMQ_EXPORT_RECV "zmq_recv"
#define QL_ZMQ_EXPORT_POLL "zmq_poll"
#define QL_ZMQ_EXPORT_ERRNO "zmq_errno"
#define QL_ZMQ_EXPORT_STRERROR "zmq_strerror"
#define QL_ZMQ_EXPORT_SETSOCKOPT "zmq_setsockopt"
#define QL_ZMQ_EXPORT_GETSOCKOPT "zmq_getsockopt"
#define QL_ZMQ_CONTEXT_CREATE_FAILED_FORMAT "failed to create context: %s"
#define QL_ZMQ_AUTH_SOCKET_CREATE_FAILED_FORMAT "failed to create auth socket: %s"
#define QL_ZMQ_AUTH_SOCKET_BIND_FAILED_FORMAT "failed to bind auth socket: %s"
#define QL_ZMQ_RCON_SOCKET_CREATE_FAILED_FORMAT "failed to create RCON socket: %s"
#define QL_ZMQ_STATS_SOCKET_CREATE_FAILED_FORMAT "failed to create stats publisher socket: %s"
#define QL_ZMQ_PASSFILE_OPEN_FAILED_FORMAT "Failed to open %s\n"
#define QL_ZMQ_ENDPOINT_FORMAT "tcp://%s:%i"
#define QL_ZMQ_IPV4_FORMAT "%i.%i.%i.%i"
#define QL_ZMQ_PASSWORD_STATS_RECORD_FORMAT "stats_stats=%s\n"
#define QL_ZMQ_PASSWORD_RCON_RECORD_FORMAT "rcon_rcon=%s\n"
#define QL_ZMQ_AUTH_KEY_FORMAT "%s_%s"
#define QL_ZMQ_RCON_BIND_ERROR_FORMAT "zmq RCON socket error, bind failed: %s\n"
#define QL_ZMQ_RCON_BIND_SUCCESS_FORMAT "zmq RCON socket: %s\n"
#define QL_ZMQ_STATS_BIND_ERROR_FORMAT "zmq PUB socket error, bind failed: %s\n"
#define QL_ZMQ_STATS_BIND_SUCCESS_FORMAT "zmq PUB socket: %s\n"
#define QL_ZMQ_RCON_BROADCAST_ACTIVE qtrue
#define QL_ZMQ_RCON_BROADCAST_IDLE qfalse
#define QL_ZMQ_RCON_CLIENT_DISCONNECT_FORMAT "zmq RCON client disconnected: %s\n"
#define QL_ZMQ_RCON_CLIENT_CONNECT_FORMAT "zmq RCON client connected: %s\n"
#define QL_ZMQ_RCON_COMMAND_FORMAT "zmq RCON command from %s: %s\n"
#define QL_ZMQ_RCON_EMPTY_PAYLOAD QL_ZMQ_DEFAULT_EMPTY
#define QL_ZMQ_PUBLICATION_TYPE_KEY "TYPE"
#define QL_ZMQ_PUBLICATION_DATA_KEY "DATA"
#define QL_ZMQ_MATCH_REPORT_TYPE "MATCH_REPORT"
#define QL_ZMQ_PUBLICATION_PAYLOAD_FORMAT "{\"" QL_ZMQ_PUBLICATION_TYPE_KEY "\":\"%s\",\"" QL_ZMQ_PUBLICATION_DATA_KEY "\":%s}"
#define QL_ZMQ_PUBLICATION_NULL_PAYLOAD_FORMAT "{\"" QL_ZMQ_PUBLICATION_TYPE_KEY "\":\"%s\",\"" QL_ZMQ_PUBLICATION_DATA_KEY "\":null}"
#define QL_ZMQ_PASSWORD_UPDATE_MESSAGE "zmq stats and rcon passwords updated\n"
#define QL_ZMQ_ZAP_ENDPOINT "inproc://zeromq.zap.01"
#define QL_ZMQ_DOMAIN_RCON "rcon"
#define QL_ZMQ_DOMAIN_STATS "stats"
#define QL_ZMQ_ZAP_VERSION "1.0"
#define QL_ZMQ_ZAP_MECHANISM_NULL "NULL"
#define QL_ZMQ_ZAP_MECHANISM_PLAIN "PLAIN"
#define QL_ZMQ_ZAP_VERSION_BUFFER_SIZE 16
#define QL_ZMQ_ZAP_REQUEST_ID_BUFFER_SIZE 64
#define QL_ZMQ_ZAP_DOMAIN_BUFFER_SIZE 64
#define QL_ZMQ_ZAP_ADDRESS_BUFFER_SIZE 128
#define QL_ZMQ_ZAP_IDENTITY_BUFFER_SIZE QL_ZMQ_MAX_IDENTITY
#define QL_ZMQ_ZAP_MECHANISM_BUFFER_SIZE 16
#define QL_ZMQ_ZAP_USERNAME_BUFFER_SIZE QL_ZMQ_MAX_IDENTITY
#define QL_ZMQ_ZAP_PASSWORD_BUFFER_SIZE MAX_STRING_CHARS
#define QL_ZMQ_ZAP_EMPTY_FIELD QL_ZMQ_STRING_TERMINATOR
#define QL_ZMQ_AUTH_EMPTY_FRAME ""
#define QL_ZMQ_AUTH_EMPTY_USER_ID QL_ZMQ_AUTH_EMPTY_FRAME
#define QL_ZMQ_AUTH_EMPTY_CREDENTIAL QL_ZMQ_AUTH_EMPTY_FRAME
#define QL_ZMQ_ZAP_STATUS_OK "200"
#define QL_ZMQ_ZAP_STATUS_NO_ACCESS "400"
#define QL_ZMQ_ZAP_TEXT_OK "OK"
#define QL_ZMQ_ZAP_TEXT_BAD_REQUEST "BAD REQUEST"
#define QL_ZMQ_ZAP_TEXT_NO_ACCESS "No access"
#define QL_ZMQ_AUTH_ACTOR_COMMAND_VERBOSE "VERBOSE"
#define QL_ZMQ_AUTH_ACTOR_COMMAND_PLAIN "PLAIN"
#define QL_ZMQ_RETAIL_SOURCE_FILE "zmq\\id_zmq.cpp"
#define QL_ZMQ_RETAIL_STATS_PUB_CREATE_LINE 0x5c
#define QL_ZMQ_RETAIL_STATS_PUB_DESTROY_LINE 0x73
#define QL_ZMQ_RETAIL_RCON_CREATE_LINE 0xc7
#define QL_ZMQ_RETAIL_RCON_DESTROY_LINE 0xe2
#define QL_ZMQ_RETAIL_ZACTOR_SOURCE_FILE "..\\..\\..\\..\\src\\zactor.c"
#define QL_ZMQ_RETAIL_ZACTOR_MAGIC 0x5cafe
#define QL_ZMQ_RETAIL_ZACTOR_THREAD_DESTROY_LINE 0x58
#define QL_ZMQ_RETAIL_ZACTOR_ALLOC_LINE 0x66
#define QL_ZMQ_RETAIL_ZACTOR_ARGS_ALLOC_LINE 0x6a

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

static qboolean idZMQ_EnsureRconSocket( void );
static qboolean idZMQ_EnsureStatsPublisher( void );
static void idZMQ_UpdatePasswords( void );

typedef struct zmqRconPeer_s {
	int						identityLength;
	char					identity[QL_ZMQ_MAX_IDENTITY];
	char					label[QL_ZMQ_MAX_IDENTITY];
	struct zmqRconPeer_s	*left;
	struct zmqRconPeer_s	*right;
	struct zmqRconPeer_s	*parent;
	struct zmqRconPeer_s	*prev;
	struct zmqRconPeer_s	*next;
} zmqRconPeer_t;

typedef struct {
	void					*library;
	void					*context;
	/* Retail idZMQ slots represented here: +4 auth actor, +8 stats PUB, +0xc RCON, +0x10 resolved RCON poll socket, +0x14 peer table. */
	void					*authSocket;
	void					*pubSocket;
	void					*rconSocket;
	void					*rconPollSocket;
	fileHandle_t			statsTranscript;
	/* Portable decomposition of the retail std::tree header/sentinel peer table. */
	zmqRconPeer_t			*rconPeers;
	zmqRconPeer_t			*rconPeerRoot;
	zmqRconPeer_t			*rconPeerLast;
	int						rconPeerCount;
	char					statsEndpoint[QL_ZMQ_ENDPOINT_MAX];
	char					rconEndpoint[QL_ZMQ_ENDPOINT_MAX];
	char					statsPassword[MAX_STRING_CHARS];
	char					rconPassword[MAX_STRING_CHARS];
	int						statsPasswordRevision;
	int						rconPasswordRevision;
	qboolean				passwordsPrimed;
	qboolean				broadcastingRconOutput;
	qboolean				authActorReady;
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
	s_zmq.zmq_ctx_new = QL_ZMQ_SYMBOL_SLOT_EMPTY;
	s_zmq.zmq_ctx_term = QL_ZMQ_SYMBOL_SLOT_EMPTY;
	s_zmq.zmq_socket = QL_ZMQ_SYMBOL_SLOT_EMPTY;
	s_zmq.zmq_close = QL_ZMQ_SYMBOL_SLOT_EMPTY;
	s_zmq.zmq_bind = QL_ZMQ_SYMBOL_SLOT_EMPTY;
	s_zmq.zmq_setsockopt = QL_ZMQ_SYMBOL_SLOT_EMPTY;
	s_zmq.zmq_getsockopt = QL_ZMQ_SYMBOL_SLOT_EMPTY;
	s_zmq.zmq_send = QL_ZMQ_SYMBOL_SLOT_EMPTY;
	s_zmq.zmq_recv = QL_ZMQ_SYMBOL_SLOT_EMPTY;
	s_zmq.zmq_poll = QL_ZMQ_SYMBOL_SLOT_EMPTY;
	s_zmq.zmq_errno = QL_ZMQ_SYMBOL_SLOT_EMPTY;
	s_zmq.zmq_strerror = QL_ZMQ_SYMBOL_SLOT_EMPTY;
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
		return QL_ZMQ_LAST_ERROR_UNKNOWN;
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
	Com_Printf( QL_ZMQ_RUNTIME_UNAVAILABLE_FORMAT, reason );
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
		Com_Printf( QL_ZMQ_RUNTIME_DISABLED_MESSAGE );
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
		idZMQ_LogRuntimeUnavailable( QL_ZMQ_RUNTIME_LOAD_FAILED_REASON );
		return qfalse;
	}

	if ( !idZMQ_LoadSymbol( (void **)&s_zmq.zmq_ctx_new, QL_ZMQ_EXPORT_CTX_NEW ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_ctx_term, QL_ZMQ_EXPORT_CTX_TERM ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_socket, QL_ZMQ_EXPORT_SOCKET ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_close, QL_ZMQ_EXPORT_CLOSE ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_bind, QL_ZMQ_EXPORT_BIND ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_send, QL_ZMQ_EXPORT_SEND ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_recv, QL_ZMQ_EXPORT_RECV ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_poll, QL_ZMQ_EXPORT_POLL ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_errno, QL_ZMQ_EXPORT_ERRNO ) ||
		!idZMQ_LoadSymbol( (void **)&s_zmq.zmq_strerror, QL_ZMQ_EXPORT_STRERROR ) ) {
		idZMQ_LogRuntimeUnavailable( QL_ZMQ_RUNTIME_EXPORTS_MISSING_REASON );
		QL_ZMQ_CLOSE();
		s_zmq.library = QL_ZMQ_LIBRARY_SLOT_EMPTY;
		idZMQ_ResetResolvedSymbols();
		return qfalse;
	}

	idZMQ_LoadOptionalSymbol( (void **)&s_zmq.zmq_setsockopt, QL_ZMQ_EXPORT_SETSOCKOPT );
	idZMQ_LoadOptionalSymbol( (void **)&s_zmq.zmq_getsockopt, QL_ZMQ_EXPORT_GETSOCKOPT );
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
		s_zmq.library = QL_ZMQ_LIBRARY_SLOT_EMPTY;
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

	*socketPointer = QL_ZMQ_SOCKET_SLOT_EMPTY;
}

/*
==================
idZMQ_CloseStatsTranscript
==================
*/
static void idZMQ_CloseStatsTranscript( void ) {
	if ( s_zmq.statsTranscript ) {
		FS_FCloseFile( s_zmq.statsTranscript );
		s_zmq.statsTranscript = QL_ZMQ_STATS_TRANSCRIPT_HANDLE_EMPTY;
	}
}

/*
==================
idZMQ_CloseAuthSocket
==================
*/
static void idZMQ_CloseAuthSocket( void ) {
	idZMQ_CloseSocket( &s_zmq.authSocket );
	s_zmq.authActorReady = qfalse;
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
	char line[QL_ZMQ_PASSFILE_RECORD_BUFFER_SIZE];
	int lineLength;

	if ( !FS_Initialized() ) {
		return;
	}

	passFile = FS_FOpenFileWrite( QL_ZMQ_PASSFILE );
	if ( !passFile ) {
		Com_Printf( QL_ZMQ_PASSFILE_OPEN_FAILED_FORMAT, QL_ZMQ_PASSFILE );
		return;
	}

	if ( s_zmq.statsPassword[0] ) {
		Com_sprintf( line, sizeof( line ), QL_ZMQ_PASSWORD_STATS_RECORD_FORMAT, s_zmq.statsPassword );
		lineLength = strlen( line );
		FS_Write( line, lineLength, passFile );
	}

	if ( s_zmq.rconPassword[0] ) {
		Com_sprintf( line, sizeof( line ), QL_ZMQ_PASSWORD_RCON_RECORD_FORMAT, s_zmq.rconPassword );
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
		buffer[0] = QL_ZMQ_STRING_TERMINATOR;
	}
	if ( more ) {
		*more = QL_ZMQ_FRAME_NO_MORE;
	}

	length = s_zmq.zmq_recv( socket, buffer, bufferSize > 0 ? bufferSize - QL_ZMQ_STRING_TERMINATOR_LENGTH : 0, QL_ZMQ_DONTWAIT );
	if ( length < QL_ZMQ_FRAME_READ_SUCCESS_MIN ) {
		return length;
	}
	if ( bufferSize > 0 ) {
		if ( length >= (int)bufferSize ) {
			length = (int)bufferSize - QL_ZMQ_STRING_TERMINATOR_LENGTH;
		}
		buffer[length] = QL_ZMQ_STRING_TERMINATOR;
	}
	if ( !more || !s_zmq.zmq_getsockopt ) {
		return length;
	}

	moreValue = QL_ZMQ_RCVMORE_NONE;
	moreSize = sizeof( moreValue );
	if ( s_zmq.zmq_getsockopt( socket, QL_ZMQ_RCVMORE, &moreValue, &moreSize ) == QL_ZMQ_GETSOCKOPT_SUCCESS && moreValue != QL_ZMQ_RCVMORE_NONE ) {
		*more = QL_ZMQ_FRAME_MORE;
	}

	return length;
}

/*
==================
idZMQ_DrainRemainingFrames
==================
*/
static void idZMQ_DrainRemainingFrames( void *socket, qboolean more ) {
	char scratch[QL_ZMQ_DRAIN_SCRATCH_SIZE];

	while ( more ) {
		if ( idZMQ_ReadFrameString( socket, scratch, sizeof( scratch ), &more ) < QL_ZMQ_FRAME_READ_SUCCESS_MIN ) {
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
	int compare;

	if ( !identity || !identity[0] ) {
		return NULL;
	}

	for ( peer = s_zmq.rconPeerRoot; peer; ) {
		compare = strcmp( identity, peer->identity );
		if ( compare == 0 ) {
			return peer;
		}
		peer = ( compare < 0 ) ? peer->left : peer->right;
	}

	return NULL;
}

/*
==================
idZMQ_LeftmostRconPeer
==================
*/
static zmqRconPeer_t *idZMQ_LeftmostRconPeer( zmqRconPeer_t *peer ) {
	while ( peer && peer->left ) {
		peer = peer->left;
	}

	return peer;
}

/*
==================
idZMQ_LinkRconPeerInOrder
==================
*/
static void idZMQ_LinkRconPeerInOrder( zmqRconPeer_t *peer, zmqRconPeer_t *previous, zmqRconPeer_t *next ) {
	peer->prev = previous;
	peer->next = next;

	if ( previous ) {
		previous->next = peer;
	} else {
		s_zmq.rconPeers = peer;
	}
	if ( next ) {
		next->prev = peer;
	} else {
		s_zmq.rconPeerLast = peer;
	}
}

/*
==================
idZMQ_AllocRconPeer
==================
*/
static zmqRconPeer_t *idZMQ_AllocRconPeer( const char *identity ) {
	zmqRconPeer_t *peer;

	if ( !identity || !identity[0] ) {
		return NULL;
	}

	peer = Z_Malloc( sizeof( *peer ) );
	Com_Memset( peer, 0, sizeof( *peer ) );
	Q_strncpyz( peer->identity, identity, sizeof( peer->identity ) );
	Q_strncpyz( peer->label, identity, sizeof( peer->label ) );
	peer->identityLength = strlen( peer->identity );

	return peer;
}

/*
==================
idZMQ_InsertRconPeer
==================
*/
static zmqRconPeer_t *idZMQ_InsertRconPeer( const char *identity ) {
	zmqRconPeer_t *peer;
	zmqRconPeer_t *cursor;
	zmqRconPeer_t *parent;
	zmqRconPeer_t *previousPeer;
	zmqRconPeer_t *nextPeer;
	int compare;

	if ( !identity || !identity[0] ) {
		return NULL;
	}

	parent = NULL;
	previousPeer = NULL;
	nextPeer = NULL;
	compare = 0;
	for ( cursor = s_zmq.rconPeerRoot; cursor; ) {
		parent = cursor;
		compare = strcmp( identity, cursor->identity );
		if ( compare == 0 ) {
			return NULL;
		}
		if ( compare < 0 ) {
			nextPeer = cursor;
			cursor = cursor->left;
		} else {
			previousPeer = cursor;
			cursor = cursor->right;
		}
	}

	peer = idZMQ_AllocRconPeer( identity );
	if ( !peer ) {
		return NULL;
	}
	peer->parent = parent;

	if ( parent ) {
		if ( compare < 0 ) {
			parent->left = peer;
			if ( !previousPeer ) {
				previousPeer = parent->prev;
			}
			nextPeer = parent;
		} else {
			parent->right = peer;
			previousPeer = parent;
			if ( !nextPeer ) {
				nextPeer = parent->next;
			}
		}
	} else {
		s_zmq.rconPeerRoot = peer;
	}

	idZMQ_LinkRconPeerInOrder( peer, previousPeer, nextPeer );
	s_zmq.rconPeerCount++;

	return peer;
}

/*
==================
idZMQ_TransplantRconPeer
==================
*/
static void idZMQ_TransplantRconPeer( zmqRconPeer_t *oldPeer, zmqRconPeer_t *newPeer ) {
	if ( !oldPeer->parent ) {
		s_zmq.rconPeerRoot = newPeer;
	} else if ( oldPeer == oldPeer->parent->left ) {
		oldPeer->parent->left = newPeer;
	} else {
		oldPeer->parent->right = newPeer;
	}

	if ( newPeer ) {
		newPeer->parent = oldPeer->parent;
	}
}

/*
==================
idZMQ_EraseRconPeer
==================
*/
static void idZMQ_EraseRconPeer( zmqRconPeer_t *peer ) {
	zmqRconPeer_t *successor;

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
	} else {
		s_zmq.rconPeerLast = peer->prev;
	}

	if ( !peer->left ) {
		idZMQ_TransplantRconPeer( peer, peer->right );
	} else if ( !peer->right ) {
		idZMQ_TransplantRconPeer( peer, peer->left );
	} else {
		successor = idZMQ_LeftmostRconPeer( peer->right );
		if ( successor->parent != peer ) {
			idZMQ_TransplantRconPeer( successor, successor->right );
			successor->right = peer->right;
			successor->right->parent = successor;
		}
		idZMQ_TransplantRconPeer( peer, successor );
		successor->left = peer->left;
		successor->left->parent = successor;
	}

	if ( s_zmq.rconPeerCount > QL_ZMQ_RCON_PEER_COUNT_EMPTY ) {
		s_zmq.rconPeerCount--;
	}

	Z_Free( peer );
}

/*
==================
idZMQ_FreeRconPeerSubtree
==================
*/
static void idZMQ_FreeRconPeerSubtree( zmqRconPeer_t *peer ) {
	if ( !peer ) {
		return;
	}

	idZMQ_FreeRconPeerSubtree( peer->left );
	idZMQ_FreeRconPeerSubtree( peer->right );
	Z_Free( peer );
}

/*
==================
idZMQ_EraseRconPeerRange
==================
*/
static void idZMQ_EraseRconPeerRange( zmqRconPeer_t *first, zmqRconPeer_t *last ) {
	zmqRconPeer_t *peer;
	zmqRconPeer_t *next;

	if ( !first ) {
		return;
	}

	if ( first == s_zmq.rconPeers && !last ) {
		idZMQ_FreeRconPeerSubtree( s_zmq.rconPeerRoot );
		s_zmq.rconPeers = QL_ZMQ_RCON_PEER_SLOT_EMPTY;
		s_zmq.rconPeerRoot = QL_ZMQ_RCON_PEER_SLOT_EMPTY;
		s_zmq.rconPeerLast = QL_ZMQ_RCON_PEER_SLOT_EMPTY;
		s_zmq.rconPeerCount = QL_ZMQ_RCON_PEER_COUNT_EMPTY;
		return;
	}

	for ( peer = first; peer && peer != last; peer = next ) {
		next = peer->next;
		idZMQ_EraseRconPeer( peer );
	}
}

/*
==================
idZMQ_ClearRconPeers
==================
*/
static void idZMQ_ClearRconPeers( void ) {
	idZMQ_EraseRconPeerRange( s_zmq.rconPeers, NULL );
}

/*
==================
idZMQ_Destroy
==================
*/
static void idZMQ_Destroy( void ) {
	idZMQ_ClearRconPeers();
}

/*
==================
idZMQ_ResolveStatsHost
==================
*/
static void idZMQ_ResolveStatsHost( char *resolvedAddress, size_t resolvedIpSize ) {
	cvar_t *netIp;
	netadr_t address;

	if ( s_zmqStatsIp && s_zmqStatsIp->string[0] ) {
		Q_strncpyz( resolvedAddress, s_zmqStatsIp->string, resolvedIpSize );
		return;
	}

	netIp = Cvar_Get( QL_ZMQ_CVAR_NET_IP, QL_ZMQ_DEFAULT_NET_IP, QL_ZMQ_CVAR_NET_FALLBACK_FLAGS );
	Com_Memset( &address, 0, sizeof( address ) );
	if ( netIp ) {
		NET_StringToAdr( netIp->string, &address );
	}
	Com_sprintf( resolvedAddress, resolvedIpSize, QL_ZMQ_IPV4_FORMAT,
		address.ip[0], address.ip[1], address.ip[2], address.ip[3] );
}

/*
==================
idZMQ_ResolveRconEndpoint
==================
*/
static void idZMQ_ResolveRconEndpoint( char *endpoint, size_t endpointSize ) {
	char resolvedIp[QL_ZMQ_ENDPOINT_IP_BUFFER_SIZE];
	int resolvedPort;

	if ( s_zmqRconIp && s_zmqRconIp->string[0] ) {
		Q_strncpyz( resolvedIp, s_zmqRconIp->string, sizeof( resolvedIp ) );
	} else {
		Q_strncpyz( resolvedIp, QL_ZMQ_DEFAULT_RCON_IP, sizeof( resolvedIp ) );
	}

	resolvedPort = ( s_zmqRconPort && s_zmqRconPort->string[0] ) ? s_zmqRconPort->integer : QL_ZMQ_DEFAULT_RCON_PORT_VALUE;
	Com_sprintf( endpoint, endpointSize, QL_ZMQ_ENDPOINT_FORMAT, resolvedIp, resolvedPort );
}

/*
==================
idZMQ_ResolveStatsEndpoint
==================
*/
static void idZMQ_ResolveStatsEndpoint( char *endpoint, size_t endpointSize ) {
	char resolvedIp[QL_ZMQ_ENDPOINT_IP_BUFFER_SIZE];
	int resolvedPort;
	cvar_t *netPort;

	idZMQ_ResolveStatsHost( resolvedIp, sizeof( resolvedIp ) );

	if ( s_zmqStatsPort && s_zmqStatsPort->string[0] ) {
		resolvedPort = s_zmqStatsPort->integer;
	} else {
		netPort = Cvar_Get( QL_ZMQ_CVAR_NET_PORT, va( QL_ZMQ_DEFAULT_NET_PORT_FORMAT, PORT_SERVER ), QL_ZMQ_CVAR_NET_FALLBACK_FLAGS );
		resolvedPort = netPort->integer;
	}

	Com_sprintf( endpoint, endpointSize, QL_ZMQ_ENDPOINT_FORMAT, resolvedIp, resolvedPort );
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
		idZMQ_LogRuntimeUnavailable( va( QL_ZMQ_CONTEXT_CREATE_FAILED_FORMAT, idZMQ_LastErrorString() ) );
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

	s_zmq.zmq_setsockopt( socket, option, &value, QL_ZMQ_SOCKET_OPTION_INT_SIZE );
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

	s_zmq.zmq_setsockopt( socket, option, value, QL_ZMQ_SOCKET_OPTION_STRING_SIZE( value ) );
}

/*
==================
idZMQ_SendAuthFrame
==================
*/
static int idZMQ_SendAuthFrame( void *socket, const char *value, qboolean more ) {
	const char *frame;
	int flags;

	frame = value ? value : QL_ZMQ_AUTH_EMPTY_FRAME;
	flags = more ? QL_ZMQ_SNDMORE : QL_ZMQ_NO_FLAGS;
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

	if ( idZMQ_SendAuthFrame( s_zmq.authSocket, version, qtrue ) < QL_ZMQ_SEND_SUCCESS_MIN ||
		idZMQ_SendAuthFrame( s_zmq.authSocket, requestId, qtrue ) < QL_ZMQ_SEND_SUCCESS_MIN ||
		idZMQ_SendAuthFrame( s_zmq.authSocket, statusCode, qtrue ) < QL_ZMQ_SEND_SUCCESS_MIN ||
		idZMQ_SendAuthFrame( s_zmq.authSocket, statusText, qtrue ) < QL_ZMQ_SEND_SUCCESS_MIN ||
		idZMQ_SendAuthFrame( s_zmq.authSocket, userId, qtrue ) < QL_ZMQ_SEND_SUCCESS_MIN ) {
		return;
	}

	idZMQ_SendAuthFrame( s_zmq.authSocket, QL_ZMQ_AUTH_EMPTY_FRAME, qfalse );
}

/*
==================
idZMQ_GetPlainCredentials
==================
*/
static qboolean idZMQ_GetPlainCredentials( const char *domain, const char **expectedUsername, const char **expectedPassword ) {
	if ( expectedUsername ) {
		*expectedUsername = QL_ZMQ_AUTH_EMPTY_CREDENTIAL;
	}
	if ( expectedPassword ) {
		*expectedPassword = QL_ZMQ_AUTH_EMPTY_CREDENTIAL;
	}
	if ( !domain ) {
		return qfalse;
	}

	if ( !Q_stricmp( domain, QL_ZMQ_DOMAIN_RCON ) ) {
		if ( expectedUsername ) {
			*expectedUsername = QL_ZMQ_DOMAIN_RCON;
		}
		if ( expectedPassword ) {
			*expectedPassword = s_zmq.rconPassword;
		}
		return qtrue;
	}
	if ( !Q_stricmp( domain, QL_ZMQ_DOMAIN_STATS ) ) {
		if ( expectedUsername ) {
			*expectedUsername = QL_ZMQ_DOMAIN_STATS;
		}
		if ( expectedPassword ) {
			*expectedPassword = s_zmq.statsPassword;
		}
		return qtrue;
	}

	return qfalse;
}

/*
==================
idZMQ_ValidatePlainCredentials
==================
*/
static qboolean idZMQ_ValidatePlainCredentials( const char *domain, const char *username, const char *password, const char **userId ) {
	const char *expectedPassword;
	const char *expectedUsername;

	expectedPassword = QL_ZMQ_AUTH_EMPTY_CREDENTIAL;
	expectedUsername = QL_ZMQ_AUTH_EMPTY_CREDENTIAL;
	if ( userId ) {
		*userId = QL_ZMQ_AUTH_EMPTY_USER_ID;
	}

	if ( !idZMQ_GetPlainCredentials( domain, &expectedUsername, &expectedPassword ) ) {
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
idZMQ_ApplyPasswords
==================
*/
static void idZMQ_ApplyPasswords( void ) {
	if ( !s_zmq.authActorReady ) {
		return;
	}

	/* Retail sends QL_ZMQ_AUTH_ACTOR_COMMAND_PLAIN; the manual ZAP path reads
	 * these retained buffers directly. */
	idZMQ_WritePasswordFile();
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
		s_zmq.authActorReady = qtrue;
		return qtrue;
	}
	if ( !idZMQ_EnsureRuntime() ) {
		return qfalse;
	}

	/*
	 * Retail starts a shared CZMQ auth actor, sends VERBOSE, waits for the
	 * actor pipe, and then applies passwords. SRP keeps CZMQ outside the repo
	 * and services the same ZAP endpoint directly through external libzmq.
	 */
	socket = s_zmq.zmq_socket( s_zmq.context, QL_ZMQ_REP );
	if ( !socket ) {
		idZMQ_LogRuntimeUnavailable( va( QL_ZMQ_AUTH_SOCKET_CREATE_FAILED_FORMAT, idZMQ_LastErrorString() ) );
		return qfalse;
	}
	if ( s_zmq.zmq_bind( socket, QL_ZMQ_ZAP_ENDPOINT ) != QL_ZMQ_BIND_SUCCESS ) {
		idZMQ_LogRuntimeUnavailable( va( QL_ZMQ_AUTH_SOCKET_BIND_FAILED_FORMAT, idZMQ_LastErrorString() ) );
		idZMQ_CloseSocket( &socket );
		return qfalse;
	}

	s_zmq.authSocket = socket;
	s_zmq.authActorReady = qtrue;
	idZMQ_ApplyPasswords();
	return qtrue;
}

/*
==================
idZMQ_PumpAuthSocket
==================
*/
static void idZMQ_PumpAuthSocket( void ) {
	ql_zmq_pollitem_t item;
	char version[QL_ZMQ_ZAP_VERSION_BUFFER_SIZE];
	char requestId[QL_ZMQ_ZAP_REQUEST_ID_BUFFER_SIZE];
	char domain[QL_ZMQ_ZAP_DOMAIN_BUFFER_SIZE];
	char address[QL_ZMQ_ZAP_ADDRESS_BUFFER_SIZE];
	char identity[QL_ZMQ_ZAP_IDENTITY_BUFFER_SIZE];
	char mechanism[QL_ZMQ_ZAP_MECHANISM_BUFFER_SIZE];
	char username[QL_ZMQ_ZAP_USERNAME_BUFFER_SIZE];
	char password[QL_ZMQ_ZAP_PASSWORD_BUFFER_SIZE];
	const char *statusCode;
	const char *statusText;
	const char *userId;
	int length;
	qboolean more;

	if ( !s_zmq.authActorReady || !s_zmq.authSocket || !s_zmq.zmq_poll || !s_zmq.zmq_recv || !s_zmq.zmq_send ) {
		return;
	}

	item.socket = s_zmq.authSocket;
	item.fd = QL_ZMQ_POLL_FD_NONE;
	item.events = QL_ZMQ_POLLIN;
	item.revents = QL_ZMQ_POLL_REVENTS_NONE;

	while ( s_zmq.zmq_poll( &item, QL_ZMQ_SINGLE_POLL_ITEM, QL_ZMQ_POLL_TIMEOUT_IMMEDIATE ) >= QL_ZMQ_POLL_READY_MIN && ( item.revents & QL_ZMQ_POLLIN ) ) {
		Q_strncpyz( version, QL_ZMQ_ZAP_VERSION, sizeof( version ) );
		requestId[0] = QL_ZMQ_ZAP_EMPTY_FIELD;
		domain[0] = QL_ZMQ_ZAP_EMPTY_FIELD;
		address[0] = QL_ZMQ_ZAP_EMPTY_FIELD;
		identity[0] = QL_ZMQ_ZAP_EMPTY_FIELD;
		mechanism[0] = QL_ZMQ_ZAP_EMPTY_FIELD;
		username[0] = QL_ZMQ_ZAP_EMPTY_FIELD;
		password[0] = QL_ZMQ_ZAP_EMPTY_FIELD;
		statusCode = QL_ZMQ_ZAP_STATUS_NO_ACCESS;
		statusText = QL_ZMQ_ZAP_TEXT_BAD_REQUEST;
		userId = QL_ZMQ_AUTH_EMPTY_USER_ID;
		more = QL_ZMQ_FRAME_NO_MORE;

		length = idZMQ_ReadFrameString( s_zmq.authSocket, version, sizeof( version ), &more );
		if ( length < QL_ZMQ_FRAME_READ_SUCCESS_MIN ) {
			break;
		}
		if ( !more ) {
			idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
			item.revents = QL_ZMQ_POLL_REVENTS_NONE;
			continue;
		}

		length = idZMQ_ReadFrameString( s_zmq.authSocket, requestId, sizeof( requestId ), &more );
		if ( length < QL_ZMQ_FRAME_READ_SUCCESS_MIN ) {
			break;
		}
		if ( !more ) {
			idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
			item.revents = QL_ZMQ_POLL_REVENTS_NONE;
			continue;
		}

		length = idZMQ_ReadFrameString( s_zmq.authSocket, domain, sizeof( domain ), &more );
		if ( length < QL_ZMQ_FRAME_READ_SUCCESS_MIN ) {
			break;
		}
		if ( !more ) {
			idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
			item.revents = QL_ZMQ_POLL_REVENTS_NONE;
			continue;
		}

		length = idZMQ_ReadFrameString( s_zmq.authSocket, address, sizeof( address ), &more );
		if ( length < QL_ZMQ_FRAME_READ_SUCCESS_MIN ) {
			break;
		}
		if ( !more ) {
			idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
			item.revents = QL_ZMQ_POLL_REVENTS_NONE;
			continue;
		}

		length = idZMQ_ReadFrameString( s_zmq.authSocket, identity, sizeof( identity ), &more );
		if ( length < QL_ZMQ_FRAME_READ_SUCCESS_MIN ) {
			break;
		}
		if ( !more ) {
			idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
			item.revents = QL_ZMQ_POLL_REVENTS_NONE;
			continue;
		}

		length = idZMQ_ReadFrameString( s_zmq.authSocket, mechanism, sizeof( mechanism ), &more );
		if ( length < QL_ZMQ_FRAME_READ_SUCCESS_MIN ) {
			break;
		}
		if ( !Q_stricmp( mechanism, QL_ZMQ_ZAP_MECHANISM_NULL ) ) {
			statusCode = QL_ZMQ_ZAP_STATUS_OK;
			statusText = QL_ZMQ_ZAP_TEXT_OK;
			idZMQ_DrainRemainingFrames( s_zmq.authSocket, more );
			idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
			item.revents = QL_ZMQ_POLL_REVENTS_NONE;
			continue;
		}
		if ( !Q_stricmp( mechanism, QL_ZMQ_ZAP_MECHANISM_PLAIN ) ) {
			if ( !more ) {
				idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
				item.revents = QL_ZMQ_POLL_REVENTS_NONE;
				continue;
			}

			length = idZMQ_ReadFrameString( s_zmq.authSocket, username, sizeof( username ), &more );
			if ( length < QL_ZMQ_FRAME_READ_SUCCESS_MIN ) {
				break;
			}
			if ( !more ) {
				idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
				item.revents = QL_ZMQ_POLL_REVENTS_NONE;
				continue;
			}

			length = idZMQ_ReadFrameString( s_zmq.authSocket, password, sizeof( password ), &more );
			if ( length < QL_ZMQ_FRAME_READ_SUCCESS_MIN ) {
				break;
			}

			statusText = QL_ZMQ_ZAP_TEXT_NO_ACCESS;
			if ( idZMQ_ValidatePlainCredentials( domain, username, password, &userId ) ) {
				statusCode = QL_ZMQ_ZAP_STATUS_OK;
				statusText = QL_ZMQ_ZAP_TEXT_OK;
			}
			idZMQ_DrainRemainingFrames( s_zmq.authSocket, more );
			idZMQ_SendAuthResponse( version, requestId, statusCode, statusText, userId );
			item.revents = QL_ZMQ_POLL_REVENTS_NONE;
			continue;
		}

		idZMQ_DrainRemainingFrames( s_zmq.authSocket, more );
		idZMQ_SendAuthResponse( version, requestId, statusCode, QL_ZMQ_ZAP_TEXT_NO_ACCESS, userId );
		item.revents = QL_ZMQ_POLL_REVENTS_NONE;
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
		idZMQ_Destroy();
		s_zmq.rconPollSocket = QL_ZMQ_RCON_POLL_SLOT_EMPTY;
		idZMQ_CloseSocket( &s_zmq.rconSocket );
		s_zmq.rconEndpoint[0] = QL_ZMQ_ENDPOINT_EMPTY;
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
		idZMQ_LogRuntimeUnavailable( va( QL_ZMQ_RCON_SOCKET_CREATE_FAILED_FORMAT, idZMQ_LastErrorString() ) );
		return qfalse;
	}

	idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, QL_ZMQ_DOMAIN_RCON );
	idZMQ_TrySetSocketInt( socket, QL_ZMQ_ROUTER_MANDATORY, QL_ZMQ_SOCKET_OPTION_ENABLED );
	idZMQ_TrySetSocketInt( socket, QL_ZMQ_PLAIN_SERVER, s_zmq.rconPassword[0] ? QL_ZMQ_SOCKET_OPTION_ENABLED : QL_ZMQ_SOCKET_OPTION_DISABLED );
	idZMQ_ResolveRconEndpoint( s_zmq.rconEndpoint, sizeof( s_zmq.rconEndpoint ) );
	s_zmq.rconSocket = socket;
	if ( s_zmq.zmq_bind( socket, s_zmq.rconEndpoint ) != QL_ZMQ_BIND_SUCCESS ) {
		Com_Printf( QL_ZMQ_RCON_BIND_ERROR_FORMAT, idZMQ_LastErrorString() );
	} else {
		Com_Printf( QL_ZMQ_RCON_BIND_SUCCESS_FORMAT, s_zmq.rconEndpoint );
	}

	s_zmq.rconPollSocket = s_zmq.rconSocket;
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
		s_zmq.statsEndpoint[0] = QL_ZMQ_ENDPOINT_EMPTY;
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
		idZMQ_LogRuntimeUnavailable( va( QL_ZMQ_STATS_SOCKET_CREATE_FAILED_FORMAT, idZMQ_LastErrorString() ) );
		return qfalse;
	}

	idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, QL_ZMQ_DOMAIN_STATS );
	idZMQ_TrySetSocketInt( socket, QL_ZMQ_PLAIN_SERVER, s_zmq.statsPassword[0] ? QL_ZMQ_SOCKET_OPTION_ENABLED : QL_ZMQ_SOCKET_OPTION_DISABLED );
	idZMQ_ResolveStatsEndpoint( s_zmq.statsEndpoint, sizeof( s_zmq.statsEndpoint ) );
	s_zmq.pubSocket = socket;
	if ( s_zmq.zmq_bind( socket, s_zmq.statsEndpoint ) != QL_ZMQ_BIND_SUCCESS ) {
		Com_Printf( QL_ZMQ_STATS_BIND_ERROR_FORMAT, idZMQ_LastErrorString() );
		return qtrue;
	}

	Com_Printf( QL_ZMQ_STATS_BIND_SUCCESS_FORMAT, s_zmq.statsEndpoint );
	return qtrue;
}

/*
==================
idZMQ_BuildPublication
==================
*/
static void idZMQ_BuildPublication( const char *type, const char *payload, char *buffer, size_t bufferSize ) {
	if ( payload && payload[0] ) {
		Com_sprintf( buffer, bufferSize, QL_ZMQ_PUBLICATION_PAYLOAD_FORMAT, type, payload );
	} else {
		Com_sprintf( buffer, bufferSize, QL_ZMQ_PUBLICATION_NULL_PAYLOAD_FORMAT, type );
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
		FS_Write( QL_ZMQ_STATS_TRANSCRIPT_RECORD_TERMINATOR, QL_ZMQ_STATS_TRANSCRIPT_RECORD_TERMINATOR_LENGTH, s_zmq.statsTranscript );
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
	if ( !type || !type[0] ) {
		return;
	}

	idZMQ_BuildPublication( type, payload, message, sizeof( message ) );
	idZMQ_WriteStatsTranscript( message );
	if ( s_zmq.pubSocket && s_zmq.zmq_send ) {
		s_zmq.zmq_send( s_zmq.pubSocket, message, strlen( message ), QL_ZMQ_NO_FLAGS );
	}
}

/*
==================
idZMQ_RegisterCvarsAndInitRcon
==================
*/
static void idZMQ_RegisterCvarsAndInitRcon( void ) {
	s_zmqRconEnable = Cvar_Get( QL_ZMQ_CVAR_RCON_ENABLE, QL_ZMQ_DEFAULT_DISABLED, QL_ZMQ_CVAR_INIT_FLAGS );
	s_zmqStatsEnable = Cvar_Get( QL_ZMQ_CVAR_STATS_ENABLE, QL_ZMQ_DEFAULT_DISABLED, QL_ZMQ_CVAR_INIT_FLAGS );
	s_zmqRconIp = Cvar_Get( QL_ZMQ_CVAR_RCON_IP, QL_ZMQ_DEFAULT_RCON_IP, QL_ZMQ_CVAR_INIT_FLAGS );
	s_zmqRconPort = Cvar_Get( QL_ZMQ_CVAR_RCON_PORT, QL_ZMQ_DEFAULT_RCON_PORT, QL_ZMQ_CVAR_INIT_FLAGS );
	s_zmqStatsIp = Cvar_Get( QL_ZMQ_CVAR_STATS_IP, QL_ZMQ_DEFAULT_EMPTY, QL_ZMQ_CVAR_INIT_FLAGS );
	s_zmqStatsPort = Cvar_Get( QL_ZMQ_CVAR_STATS_PORT, QL_ZMQ_DEFAULT_EMPTY, QL_ZMQ_CVAR_INIT_FLAGS );
	s_zmqStatsPassword = Cvar_Get( QL_ZMQ_CVAR_STATS_PASSWORD, QL_ZMQ_DEFAULT_EMPTY, QL_ZMQ_CVAR_PASSWORD_FLAGS );
	s_zmqRconPassword = Cvar_Get( QL_ZMQ_CVAR_RCON_PASSWORD, QL_ZMQ_DEFAULT_EMPTY, QL_ZMQ_CVAR_PASSWORD_FLAGS );

	idZMQ_UpdatePasswords();
	idZMQ_EnsureRconSocket();
}

/*
==================
Zmq_RegisterCvarsAndInitRcon
==================
*/
void Zmq_RegisterCvarsAndInitRcon( void ) {
	idZMQ_RegisterCvarsAndInitRcon();
}

/*
==================
idZMQ_UpdatePasswords
==================
*/
static void idZMQ_UpdatePasswords( void ) {
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
		idZMQ_ApplyPasswords();
		return;
	}

	changed = (qboolean)( s_zmq.statsPasswordRevision != s_zmqStatsPassword->modificationCount ||
		s_zmq.rconPasswordRevision != s_zmqRconPassword->modificationCount );
	if ( !changed ) {
		return;
	}

	Q_strncpyz( s_zmq.statsPassword, s_zmqStatsPassword->string, sizeof( s_zmq.statsPassword ) );
	Q_strncpyz( s_zmq.rconPassword, s_zmqRconPassword->string, sizeof( s_zmq.rconPassword ) );
	s_zmq.statsPasswordRevision = s_zmqStatsPassword->modificationCount;
	s_zmq.rconPasswordRevision = s_zmqRconPassword->modificationCount;
	idZMQ_ApplyPasswords();
	Com_Printf( QL_ZMQ_PASSWORD_UPDATE_MESSAGE );
}

/*
==================
Zmq_UpdatePasswords
==================
*/
void Zmq_UpdatePasswords( void ) {
	idZMQ_UpdatePasswords();
}

/*
==================
idZMQ_InitStatsPublisher
==================
*/
static void idZMQ_InitStatsPublisher( void ) {
	idZMQ_EnsureStatsPublisher();
}

/*
==================
Zmq_InitStatsPublisher
==================
*/
void Zmq_InitStatsPublisher( void ) {
	idZMQ_InitStatsPublisher();
}

/*
==================
Zmq_ShutdownStatsPublisher
==================
*/
void Zmq_ShutdownStatsPublisher( void ) {
	idZMQ_CloseStatsTranscript();
	idZMQ_CloseSocket( &s_zmq.pubSocket );
	s_zmq.statsEndpoint[0] = QL_ZMQ_ENDPOINT_EMPTY;
}

/*
==================
idZMQ_SubmitMatchReport
==================
*/
static void idZMQ_SubmitMatchReport( const void *report ) {
	idZMQ_Publish( QL_ZMQ_MATCH_REPORT_TYPE, (const char *)report );
}

/*
==================
Zmq_SubmitMatchReport
==================
*/
void Zmq_SubmitMatchReport( const void *report ) {
	idZMQ_SubmitMatchReport( report );
}

/*
==================
idZMQ_ReportPlayerEvent
==================
*/
static void idZMQ_ReportPlayerEvent( uint32_t steamIdLow, uint32_t steamIdHigh, const void *clientStats, const char *eventName, const void *payload ) {
	(void)steamIdLow;
	(void)steamIdHigh;
	(void)clientStats;

	idZMQ_Publish( eventName, (const char *)payload );
}

/*
==================
Zmq_ReportPlayerEvent
==================
*/
void Zmq_ReportPlayerEvent( uint32_t steamIdLow, uint32_t steamIdHigh, const void *clientStats, const char *eventName, const void *payload ) {
	idZMQ_ReportPlayerEvent( steamIdLow, steamIdHigh, clientStats, eventName, payload );
}

/*
==================
idZMQ_BroadcastRconOutput
==================
*/
static void idZMQ_BroadcastRconOutput( const char *message ) {
	zmqRconPeer_t *peer;
	zmqRconPeer_t *next;
	const char *payload;

	if ( !s_zmq.rconSocket || !s_zmq.rconPeers || !s_zmq.zmq_send ) {
		return;
	}
	if ( s_zmq.broadcastingRconOutput ) {
		return;
	}

	payload = message ? message : QL_ZMQ_RCON_EMPTY_PAYLOAD;
	s_zmq.broadcastingRconOutput = QL_ZMQ_RCON_BROADCAST_ACTIVE;
	for ( peer = s_zmq.rconPeers; peer; peer = next ) {
		next = peer->next;
		if ( s_zmq.zmq_send( s_zmq.rconSocket, peer->identity, peer->identityLength, QL_ZMQ_SEND_MORE_DONTWAIT ) < QL_ZMQ_SEND_SUCCESS_MIN ) {
			Com_Printf( QL_ZMQ_RCON_CLIENT_DISCONNECT_FORMAT, peer->label );
			idZMQ_EraseRconPeer( peer );
			continue;
		}
		s_zmq.zmq_send( s_zmq.rconSocket, payload, strlen( payload ), QL_ZMQ_SEND_DONTWAIT );
	}
	s_zmq.broadcastingRconOutput = QL_ZMQ_RCON_BROADCAST_IDLE;
}

/*
==================
Zmq_BroadcastRconOutput
==================
*/
void Zmq_BroadcastRconOutput( const char *message ) {
	idZMQ_BroadcastRconOutput( message );
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
	if ( commandLength >= QL_ZMQ_FRAME_READ_SUCCESS_MIN ) {
		idZMQ_DrainRemainingFrames( s_zmq.rconSocket, more );
	}
	return commandLength;
}

/*
==================
idZMQ_PumpRcon
==================
*/
static void idZMQ_PumpRcon( void ) {
	ql_zmq_pollitem_t item;
	char identity[QL_ZMQ_RCON_IDENTITY_BUFFER_SIZE];
	char command[QL_ZMQ_RCON_COMMAND_BUFFER_SIZE];
	int identityLength;
	int commandLength;
	qboolean more;
	zmqRconPeer_t *peer;

	idZMQ_PumpAuthSocket();
	if ( !s_zmq.rconSocket || !s_zmq.rconPollSocket || !s_zmq.zmq_poll || !s_zmq.zmq_recv ) {
		return;
	}

	item.socket = s_zmq.rconPollSocket;
	item.fd = QL_ZMQ_POLL_FD_NONE;
	item.events = QL_ZMQ_POLLIN;
	item.revents = QL_ZMQ_POLL_REVENTS_NONE;

	if ( s_zmq.zmq_poll( &item, QL_ZMQ_SINGLE_POLL_ITEM, QL_ZMQ_POLL_TIMEOUT_IMMEDIATE ) < QL_ZMQ_POLL_READY_MIN || !( item.revents & QL_ZMQ_POLLIN ) ) {
		return;
	}

	identityLength = idZMQ_ReadFrameString( s_zmq.rconSocket, identity, sizeof( identity ), &more );
	if ( identityLength < QL_ZMQ_RCON_MIN_IDENTITY_LENGTH ) {
		idZMQ_DrainRemainingFrames( s_zmq.rconSocket, more );
		return;
	}
	if ( !more ) {
		return;
	}

	commandLength = idZMQ_ReadRconCommand( command, sizeof( command ) );
	if ( commandLength < QL_ZMQ_RCON_MIN_COMMAND_LENGTH ) {
		return;
	}

	peer = idZMQ_FindRconPeer( identity );
	if ( !peer ) {
		peer = idZMQ_InsertRconPeer( identity );
		if ( peer ) {
			Com_Printf( QL_ZMQ_RCON_CLIENT_CONNECT_FORMAT, peer->label );
		}
		return;
	}

	Com_Printf( QL_ZMQ_RCON_COMMAND_FORMAT, peer->label, command );
	Cmd_ExecuteString( command );
}

/*
==================
Zmq_PumpRcon
==================
*/
void Zmq_PumpRcon( void ) {
	idZMQ_PumpRcon();
}

/*
==================
Zmq_ShutdownRuntime
==================
*/
void Zmq_ShutdownRuntime( void ) {
	s_zmq.rconPollSocket = QL_ZMQ_RCON_POLL_SLOT_EMPTY;
	idZMQ_CloseSocket( &s_zmq.rconSocket );
	s_zmq.rconEndpoint[0] = QL_ZMQ_ENDPOINT_EMPTY;
	idZMQ_CloseAuthSocket();
	if ( s_zmq.context && s_zmq.zmq_ctx_term ) {
		s_zmq.zmq_ctx_term( s_zmq.context );
	}
	s_zmq.context = QL_ZMQ_CONTEXT_SLOT_EMPTY;
	idZMQ_UnloadLibrary();
}
