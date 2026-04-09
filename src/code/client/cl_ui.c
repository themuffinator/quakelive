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

#include "client.h"

#include "../game/botlib.h"
#include "../../common/auth_credentials.h"
#include "../../common/platform/platform_steamworks.h"
#include "../../../src-re/include/fs_imports.h"
#ifdef _WIN32
#include <windows.h>
#endif

extern	botlib_export_t	*botlib_export;

vm_t *uivm;

/*
====================
GetClientState
====================
*/
static void GetClientState( uiClientState_t *state ) {
	state->connectPacketCount = clc.connectPacketCount;
	state->connState = cls.state;
	Q_strncpyz( state->servername, cls.servername, sizeof( state->servername ) );
	Q_strncpyz( state->updateInfoString, cls.updateInfoString, sizeof( state->updateInfoString ) );
	Q_strncpyz( state->messageString, clc.serverMessage, sizeof( state->messageString ) );
	state->clientNum = cl.snap.ps.clientNum;
}

/*
====================
LAN_LoadCachedServers
====================
*/
void LAN_LoadCachedServers( ) {
	int size;
	fileHandle_t fileIn;
	cls.numglobalservers = cls.nummplayerservers = cls.numfavoriteservers = 0;
	cls.numGlobalServerAddresses = 0;
	if (FS_SV_FOpenFileRead("servercache.dat", &fileIn)) {
		FS_Read(&cls.numglobalservers, sizeof(int), fileIn);
		FS_Read(&cls.nummplayerservers, sizeof(int), fileIn);
		FS_Read(&cls.numfavoriteservers, sizeof(int), fileIn);
		FS_Read(&size, sizeof(int), fileIn);
		if (size == sizeof(cls.globalServers) + sizeof(cls.favoriteServers) + sizeof(cls.mplayerServers)) {
			FS_Read(&cls.globalServers, sizeof(cls.globalServers), fileIn);
			FS_Read(&cls.mplayerServers, sizeof(cls.mplayerServers), fileIn);
			FS_Read(&cls.favoriteServers, sizeof(cls.favoriteServers), fileIn);
		} else {
			cls.numglobalservers = cls.nummplayerservers = cls.numfavoriteservers = 0;
			cls.numGlobalServerAddresses = 0;
		}
		FS_FCloseFile(fileIn);
	}
}

/*
====================
LAN_SaveServersToCache
====================
*/
void LAN_SaveServersToCache( ) {
	int size;
	fileHandle_t fileOut = FS_SV_FOpenFileWrite("servercache.dat");
	FS_Write(&cls.numglobalservers, sizeof(int), fileOut);
	FS_Write(&cls.nummplayerservers, sizeof(int), fileOut);
	FS_Write(&cls.numfavoriteservers, sizeof(int), fileOut);
	size = sizeof(cls.globalServers) + sizeof(cls.favoriteServers) + sizeof(cls.mplayerServers);
	FS_Write(&size, sizeof(int), fileOut);
	FS_Write(&cls.globalServers, sizeof(cls.globalServers), fileOut);
	FS_Write(&cls.mplayerServers, sizeof(cls.mplayerServers), fileOut);
	FS_Write(&cls.favoriteServers, sizeof(cls.favoriteServers), fileOut);
	FS_FCloseFile(fileOut);
}


/*
====================
LAN_ResetPings
====================
*/
static void LAN_ResetPings(int source) {
	int count,i;
	serverInfo_t *servers = NULL;
	count = 0;

	switch (source) {
		case AS_LOCAL :
			servers = &cls.localServers[0];
			count = MAX_OTHER_SERVERS;
			break;
		case AS_MPLAYER :
			servers = &cls.mplayerServers[0];
			count = MAX_OTHER_SERVERS;
			break;
		case AS_GLOBAL :
			servers = &cls.globalServers[0];
			count = MAX_GLOBAL_SERVERS;
			break;
		case AS_FAVORITES :
			servers = &cls.favoriteServers[0];
			count = MAX_OTHER_SERVERS;
			break;
	}
	if (servers) {
		for (i = 0; i < count; i++) {
			servers[i].ping = -1;
		}
	}
}

/*
====================
LAN_AddServer
====================
*/
static int LAN_AddServer(int source, const char *name, const char *address) {
	int max, *count, i;
	netadr_t adr;
	serverInfo_t *servers = NULL;
	max = MAX_OTHER_SERVERS;
	count = 0;

	switch (source) {
		case AS_LOCAL :
			count = &cls.numlocalservers;
			servers = &cls.localServers[0];
			break;
		case AS_MPLAYER :
			count = &cls.nummplayerservers;
			servers = &cls.mplayerServers[0];
			break;
		case AS_GLOBAL :
			max = MAX_GLOBAL_SERVERS;
			count = &cls.numglobalservers;
			servers = &cls.globalServers[0];
			break;
		case AS_FAVORITES :
			count = &cls.numfavoriteservers;
			servers = &cls.favoriteServers[0];
			break;
	}
	if (servers && *count < max) {
		NET_StringToAdr( address, &adr );
		for ( i = 0; i < *count; i++ ) {
			if (NET_CompareAdr(servers[i].adr, adr)) {
				break;
			}
		}
		if (i >= *count) {
			servers[*count].adr = adr;
			Q_strncpyz(servers[*count].hostName, name, sizeof(servers[*count].hostName));
			servers[*count].visible = qtrue;
			(*count)++;
			return 1;
		}
		return 0;
	}
	return -1;
}

/*
====================
LAN_RemoveServer
====================
*/
static void LAN_RemoveServer(int source, const char *addr) {
	int *count, i;
	serverInfo_t *servers = NULL;
	count = 0;
	switch (source) {
		case AS_LOCAL :
			count = &cls.numlocalservers;
			servers = &cls.localServers[0];
			break;
		case AS_MPLAYER :
			count = &cls.nummplayerservers;
			servers = &cls.mplayerServers[0];
			break;
		case AS_GLOBAL :
			count = &cls.numglobalservers;
			servers = &cls.globalServers[0];
			break;
		case AS_FAVORITES :
			count = &cls.numfavoriteservers;
			servers = &cls.favoriteServers[0];
			break;
	}
	if (servers) {
		netadr_t comp;
		NET_StringToAdr( addr, &comp );
		for (i = 0; i < *count; i++) {
			if (NET_CompareAdr( comp, servers[i].adr)) {
				int j = i;
				while (j < *count - 1) {
					Com_Memcpy(&servers[j], &servers[j+1], sizeof(servers[j]));
					j++;
				}
				(*count)--;
				break;
			}
		}
	}
}


/*
====================
LAN_GetServerCount
====================
*/
static int LAN_GetServerCount( int source ) {
	switch (source) {
		case AS_LOCAL :
			return cls.numlocalservers;
			break;
		case AS_MPLAYER :
			return cls.nummplayerservers;
			break;
		case AS_GLOBAL :
			return cls.numglobalservers;
			break;
		case AS_FAVORITES :
			return cls.numfavoriteservers;
			break;
	}
	return 0;
}

/*
====================
LAN_GetLocalServerAddressString
====================
*/
static void LAN_GetServerAddressString( int source, int n, char *buf, int buflen ) {
	switch (source) {
		case AS_LOCAL :
			if (n >= 0 && n < MAX_OTHER_SERVERS) {
				Q_strncpyz(buf, NET_AdrToString( cls.localServers[n].adr) , buflen );
				return;
			}
			break;
		case AS_MPLAYER :
			if (n >= 0 && n < MAX_OTHER_SERVERS) {
				Q_strncpyz(buf, NET_AdrToString( cls.mplayerServers[n].adr) , buflen );
				return;
			}
			break;
		case AS_GLOBAL :
			if (n >= 0 && n < MAX_GLOBAL_SERVERS) {
				Q_strncpyz(buf, NET_AdrToString( cls.globalServers[n].adr) , buflen );
				return;
			}
			break;
		case AS_FAVORITES :
			if (n >= 0 && n < MAX_OTHER_SERVERS) {
				Q_strncpyz(buf, NET_AdrToString( cls.favoriteServers[n].adr) , buflen );
				return;
			}
			break;
	}
	buf[0] = '\0';
}

/*
====================
LAN_GetServerInfo
====================
*/
static void LAN_GetServerInfo( int source, int n, char *buf, int buflen ) {
	char info[MAX_STRING_CHARS];
	serverInfo_t *server = NULL;
	info[0] = '\0';
	switch (source) {
		case AS_LOCAL :
			if (n >= 0 && n < MAX_OTHER_SERVERS) {
				server = &cls.localServers[n];
			}
			break;
		case AS_MPLAYER :
			if (n >= 0 && n < MAX_OTHER_SERVERS) {
				server = &cls.mplayerServers[n];
			}
			break;
		case AS_GLOBAL :
			if (n >= 0 && n < MAX_GLOBAL_SERVERS) {
				server = &cls.globalServers[n];
			}
			break;
		case AS_FAVORITES :
			if (n >= 0 && n < MAX_OTHER_SERVERS) {
				server = &cls.favoriteServers[n];
			}
			break;
	}
	if (server && buf) {
		buf[0] = '\0';
		Info_SetValueForKey( info, "hostname", server->hostName);
		Info_SetValueForKey( info, "mapname", server->mapName);
		Info_SetValueForKey( info, "clients", va("%i",server->clients));
		Info_SetValueForKey( info, "sv_maxclients", va("%i",server->maxClients));
		Info_SetValueForKey( info, "ping", va("%i",server->ping));
		Info_SetValueForKey( info, "minping", va("%i",server->minPing));
		Info_SetValueForKey( info, "maxping", va("%i",server->maxPing));
		Info_SetValueForKey( info, "game", server->game);
		Info_SetValueForKey( info, "gametype", va("%i",server->gameType));
		Info_SetValueForKey( info, "nettype", va("%i",server->netType));
		Info_SetValueForKey( info, "addr", NET_AdrToString(server->adr));
		Info_SetValueForKey( info, "punkbuster", va("%i", server->punkbuster));
		Q_strncpyz(buf, info, buflen);
	} else {
		if (buf) {
			buf[0] = '\0';
		}
	}
}

/*
====================
LAN_GetServerPing
====================
*/
static int LAN_GetServerPing( int source, int n ) {
	serverInfo_t *server = NULL;
	switch (source) {
		case AS_LOCAL :
			if (n >= 0 && n < MAX_OTHER_SERVERS) {
				server = &cls.localServers[n];
			}
			break;
		case AS_MPLAYER :
			if (n >= 0 && n < MAX_OTHER_SERVERS) {
				server = &cls.mplayerServers[n];
			}
			break;
		case AS_GLOBAL :
			if (n >= 0 && n < MAX_GLOBAL_SERVERS) {
				server = &cls.globalServers[n];
			}
			break;
		case AS_FAVORITES :
			if (n >= 0 && n < MAX_OTHER_SERVERS) {
				server = &cls.favoriteServers[n];
			}
			break;
	}
	if (server) {
		return server->ping;
	}
	return -1;
}

/*
====================
LAN_GetServerPtr
====================
*/
static serverInfo_t *LAN_GetServerPtr( int source, int n ) {
	switch (source) {
		case AS_LOCAL :
			if (n >= 0 && n < MAX_OTHER_SERVERS) {
				return &cls.localServers[n];
			}
			break;
		case AS_MPLAYER :
			if (n >= 0 && n < MAX_OTHER_SERVERS) {
				return &cls.mplayerServers[n];
			}
			break;
		case AS_GLOBAL :
			if (n >= 0 && n < MAX_GLOBAL_SERVERS) {
				return &cls.globalServers[n];
			}
			break;
		case AS_FAVORITES :
			if (n >= 0 && n < MAX_OTHER_SERVERS) {
				return &cls.favoriteServers[n];
			}
			break;
	}
	return NULL;
}

/*
====================
LAN_CompareServers
====================
*/
static int LAN_CompareServers( int source, int sortKey, int sortDir, int s1, int s2 ) {
	int res;
	serverInfo_t *server1, *server2;

	server1 = LAN_GetServerPtr(source, s1);
	server2 = LAN_GetServerPtr(source, s2);
	if (!server1 || !server2) {
		return 0;
	}

	res = 0;
	switch( sortKey ) {
		case SORT_HOST:
			res = Q_stricmp( server1->hostName, server2->hostName );
			break;

		case SORT_MAP:
			res = Q_stricmp( server1->mapName, server2->mapName );
			break;
		case SORT_CLIENTS:
			if (server1->clients < server2->clients) {
				res = -1;
			}
			else if (server1->clients > server2->clients) {
				res = 1;
			}
			else {
				res = 0;
			}
			break;
		case SORT_GAME:
			if (server1->gameType < server2->gameType) {
				res = -1;
			}
			else if (server1->gameType > server2->gameType) {
				res = 1;
			}
			else {
				res = 0;
			}
			break;
		case SORT_PING:
			if (server1->ping < server2->ping) {
				res = -1;
			}
			else if (server1->ping > server2->ping) {
				res = 1;
			}
			else {
				res = 0;
			}
			break;
	}

	if (sortDir) {
		if (res < 0)
			return 1;
		if (res > 0)
			return -1;
		return 0;
	}
	return res;
}

/*
====================
LAN_GetPingQueueCount
====================
*/
static int LAN_GetPingQueueCount( void ) {
	return (CL_GetPingQueueCount());
}

/*
====================
LAN_ClearPing
====================
*/
static void LAN_ClearPing( int n ) {
	CL_ClearPing( n );
}

/*
====================
LAN_GetPing
====================
*/
static void LAN_GetPing( int n, char *buf, int buflen, int *pingtime ) {
	CL_GetPing( n, buf, buflen, pingtime );
}

/*
====================
LAN_GetPingInfo
====================
*/
static void LAN_GetPingInfo( int n, char *buf, int buflen ) {
	CL_GetPingInfo( n, buf, buflen );
}

/*
====================
LAN_MarkServerVisible
====================
*/
static void LAN_MarkServerVisible(int source, int n, qboolean visible ) {
	if (n == -1) {
		int count = MAX_OTHER_SERVERS;
		serverInfo_t *server = NULL;
		switch (source) {
			case AS_LOCAL :
				server = &cls.localServers[0];
				break;
			case AS_MPLAYER :
				server = &cls.mplayerServers[0];
				break;
			case AS_GLOBAL :
				server = &cls.globalServers[0];
				count = MAX_GLOBAL_SERVERS;
				break;
			case AS_FAVORITES :
				server = &cls.favoriteServers[0];
				break;
		}
		if (server) {
			for (n = 0; n < count; n++) {
				server[n].visible = visible;
			}
		}

	} else {
		switch (source) {
			case AS_LOCAL :
				if (n >= 0 && n < MAX_OTHER_SERVERS) {
					cls.localServers[n].visible = visible;
				}
				break;
			case AS_MPLAYER :
				if (n >= 0 && n < MAX_OTHER_SERVERS) {
					cls.mplayerServers[n].visible = visible;
				}
				break;
			case AS_GLOBAL :
				if (n >= 0 && n < MAX_GLOBAL_SERVERS) {
					cls.globalServers[n].visible = visible;
				}
				break;
			case AS_FAVORITES :
				if (n >= 0 && n < MAX_OTHER_SERVERS) {
					cls.favoriteServers[n].visible = visible;
				}
				break;
		}
	}
}


/*
=======================
LAN_ServerIsVisible
=======================
*/
static int LAN_ServerIsVisible(int source, int n ) {
	switch (source) {
		case AS_LOCAL :
			if (n >= 0 && n < MAX_OTHER_SERVERS) {
				return cls.localServers[n].visible;
			}
			break;
		case AS_MPLAYER :
			if (n >= 0 && n < MAX_OTHER_SERVERS) {
				return cls.mplayerServers[n].visible;
			}
			break;
		case AS_GLOBAL :
			if (n >= 0 && n < MAX_GLOBAL_SERVERS) {
				return cls.globalServers[n].visible;
			}
			break;
		case AS_FAVORITES :
			if (n >= 0 && n < MAX_OTHER_SERVERS) {
				return cls.favoriteServers[n].visible;
			}
			break;
	}
	return qfalse;
}

/*
=======================
LAN_UpdateVisiblePings
=======================
*/
qboolean LAN_UpdateVisiblePings(int source ) {
	return CL_UpdateVisiblePings_f(source);
}

/*
====================
LAN_GetServerStatus
====================
*/
int LAN_GetServerStatus( char *serverAddress, char *serverStatus, int maxLen ) {
	return CL_ServerStatus( serverAddress, serverStatus, maxLen );
}

/*
====================
CL_GetGlConfig
====================
*/
static void CL_GetGlconfig( glconfig_t *config ) {
	*config = cls.glconfig;
}

/*
====================
CL_UI_GetClipboardData
====================
*/
static void CL_UI_GetClipboardData( char *buf, int buflen ) {
	char	*cbd;

	cbd = Sys_GetClipboardData();

	if ( !cbd ) {
		*buf = 0;
		return;
	}

	Q_strncpyz( buf, cbd, buflen );

	Z_Free( cbd );
}

/*
====================
Key_KeynumToStringBuf
====================
*/
static void Key_KeynumToStringBuf( int keynum, char *buf, int buflen ) {
	Q_strncpyz( buf, Key_KeynumToString( keynum ), buflen );
}

/*
====================
Key_GetBindingBuf
====================
*/
static void Key_GetBindingBuf( int keynum, char *buf, int buflen ) {
	char	*value;

	value = Key_GetBinding( keynum );
	if ( value ) {
		Q_strncpyz( buf, value, buflen );
	}
	else {
		*buf = 0;
	}
}

/*
====================
Key_GetCatcher
====================
*/
int Key_GetCatcher( void ) {
	return cls.keyCatchers;
}

/*
====================
Ket_SetCatcher
====================
*/
void Key_SetCatcher( int catcher ) {
	cls.keyCatchers = catcher;
}


/*
====================
CLUI_SyncCredentialCvars
====================
*/
static void CLUI_SyncCredentialCvars( const char *rawValue ) {
	ql_auth_credential_t credential;
	qboolean parsed;
	qboolean autoProvisioned;
	qlAuthCredentialKind kind;

	if ( !rawValue ) {
		rawValue = "";
	}

	parsed = QL_ParseCredentialString( rawValue, &credential );
	if ( !parsed ) {
		QL_InitAuthCredential( &credential );
	}

	kind = credential.kind;
	if ( kind == QL_AUTH_CREDENTIAL_EMPTY ) {
		kind = QL_AUTH_CREDENTIAL_LEGACY_CDKEY;
	}

	autoProvisioned = ( credential.length > 0 && kind != QL_AUTH_CREDENTIAL_LEGACY_CDKEY );

	Cvar_SetValue( "ui_credentialKind", (float)kind );
	Cvar_Set( "ui_credentialAuto", autoProvisioned ? "1" : "0" );
	Cvar_Set( "ui_credentialManualHidden", autoProvisioned ? "1" : "0" );
}

/*
====================
CLUI_GetCDKey
====================
*/
static void CLUI_GetCDKey( char *buf, int buflen ) {
	cvar_t	*fs;
	const char *source = cl_cdkey;

	if ( !buf || buflen <= 0 ) {
		return;
	}

	fs = Cvar_Get ("fs_game", "", CVAR_INIT|CVAR_SYSTEMINFO );
	if (UI_usesUniqueCDKey() && fs && fs->string[0] != 0) {
		if ( cl_cdkey_mod[0] ) {
			source = cl_cdkey_mod;
		}
	}

	Q_strncpyz( buf, source, buflen );

	CLUI_SyncCredentialCvars( source );
}


/*
====================
CLUI_SetCDKey
====================
*/
static void CLUI_SetCDKey( char *buf ) {
	cvar_t	*fs;
	const char *input = buf ? buf : "";

	fs = Cvar_Get ("fs_game", "", CVAR_INIT|CVAR_SYSTEMINFO );
	if (UI_usesUniqueCDKey() && fs && fs->string[0] != 0) {
		Q_strncpyz( cl_cdkey_mod, input, sizeof( cl_cdkey_mod ) );
	} else {
		Q_strncpyz( cl_cdkey, input, sizeof( cl_cdkey ) );
	}
	// set the flag so the file will be written at the next opportunity
	cvar_modifiedFlags |= CVAR_ARCHIVE;

	CLUI_SyncCredentialCvars( input );
}

/*
====================
GetConfigString
====================
*/
static int GetConfigString(int index, char *buf, int size)
{
	int		offset;

	if (index < 0 || index >= MAX_CONFIGSTRINGS)
		return qfalse;

	offset = cl.gameState.stringOffsets[index];
	if (!offset) {
		if( size ) {
			buf[0] = 0;
		}
		return qfalse;
	}

	Q_strncpyz( buf, cl.gameState.stringData+offset, size);
 
	return qtrue;
}

/*
====================
FloatAsInt
====================
*/
static int FloatAsInt( float f ) {
	int		temp;

	*(float *)&temp = f;

	return temp;
}

void *VM_ArgPtr( int intValue );
#define	VMA(x) VM_ArgPtr(args[x])
#define	VMF(x)	((float *)args)[x]

static fileHandle_t cl_uiFsLogHandle;
static qboolean cl_uiFsLogInitialized;
static qboolean cl_uiFsLogWarned;

/*
====================
CL_UI_OpenFsLog
====================
*/
static void CL_UI_OpenFsLog( void ) {
	if ( cl_uiFsLogHandle ) {
		return;
	}

	if ( !cl_uiFsLogInitialized ) {
		cl_uiFsLogHandle = FS_FOpenFileWrite( "logs/ui_fs.log" );
		cl_uiFsLogInitialized = qtrue;
	} else {
		cl_uiFsLogHandle = FS_FOpenFileAppend( "logs/ui_fs.log" );
	}

	if ( !cl_uiFsLogHandle && !cl_uiFsLogWarned ) {
		cl_uiFsLogWarned = qtrue;
		Com_Printf( "WARNING: unable to open logs/ui_fs.log for UI FS logging\n" );
	}
}

/*
====================
CL_UI_LogFsOpen
====================
*/
static void CL_UI_LogFsOpen( const char *request, int mode, int length, const char *resolved ) {
	char buffer[MAXPRINTMSG];
	int offset;

	if ( !request || !request[0] ) {
		return;
	}

	CL_UI_OpenFsLog();
	if ( !cl_uiFsLogHandle ) {
		return;
	}

	if ( !resolved ) {
		resolved = "";
	}

	offset = Com_sprintf( buffer, sizeof( buffer ), "open mode=%d len=%d req=\"%s\" resolved=\"%s\"\n", mode, length, request, resolved );
	FS_Write( buffer, offset, cl_uiFsLogHandle );
	FS_Flush( cl_uiFsLogHandle );
}

/*
====================
CL_UISystemCallsImpl

Implements the UI trap surface for both legacy syscall dispatch and the
native import-table bridge.
====================
*/
static int CL_UISystemCallsImpl( int *args, qboolean logContract ) {
	if ( logContract ) {
		SyscallContract_LogEvent( "shim-ui", "ui", args, SYSCALL_CONTRACT_MAX_ARGS );
	}

	switch( args[0] ) {
	case UI_ERROR:
		Com_Error( ERR_DROP, "%s", VMA(1) );
		return 0;

	case UI_PRINT:
		Com_Printf( "%s", VMA(1) );
		return 0;

	case UI_MILLISECONDS:
		return Sys_Milliseconds();

	case UI_CVAR_REGISTER:
		Cvar_Register( VMA(1), VMA(2), VMA(3), args[4] ); 
		return 0;

	case UI_CVAR_UPDATE:
		Cvar_Update( VMA(1) );
		return 0;

	case UI_CVAR_SET:
		Cvar_Set( VMA(1), VMA(2) );
		return 0;

	case UI_CVAR_VARIABLEVALUE:
		return FloatAsInt( Cvar_VariableValue( VMA(1) ) );

	case UI_CVAR_VARIABLESTRINGBUFFER:
		if ( args[3] <= 0 || args[3] > MAX_STRING_CHARS ) {
			// Native UI import tables can be mis-ordered; treat this as a Cvar_Set call.
			Cvar_Set( VMA(1), VMA(2) );
			return 0;
		}
		if ( !VMA(2) ) {
			return 0;
		}
		Cvar_VariableStringBuffer( VMA(1), VMA(2), args[3] );
		return 0;

	case UI_CVAR_SETVALUE:
		Cvar_SetValue( VMA(1), VMF(2) );
		return 0;

	case UI_CVAR_RESET:
		Cvar_Reset( VMA(1) );
		return 0;

	case UI_CVAR_CREATE:
		Cvar_Get( VMA(1), VMA(2), args[3] );
		return 0;

	case UI_CVAR_INFOSTRINGBUFFER:
		if ( args[3] <= 0 || args[3] > MAX_INFO_STRING ) {
			if ( VMA(2) ) {
				((char *)VMA(2))[0] = '\0';
			}
			return 0;
		}
		if ( !VMA(2) ) {
			return 0;
		}
		{
			const int allowedBits = CVAR_USERINFO | CVAR_SERVERINFO | CVAR_SYSTEMINFO;
			int bit = args[1] & allowedBits;
			if ( bit == 0 ) {
				((char *)VMA(2))[0] = '\0';
				return 0;
			}
			Cvar_InfoStringBuffer( bit, VMA(2), args[3] );
		}
		return 0;

	case UI_ARGC:
		return Cmd_Argc();

	case UI_ARGV:
		Cmd_ArgvBuffer( args[1], VMA(2), args[3] );
		return 0;

	case UI_CMD_EXECUTETEXT:
		Cbuf_ExecuteText( args[1], VMA(2) );
		return 0;

	case UI_FS_FOPENFILE:
	{
		const char *request;
		fileHandle_t *file;
		int length;
		char resolved[MAX_QPATH];

		request = VMA( 1 );
		file = VMA( 2 );
		length = qlr_fs_imports.fopen_file_by_mode( request, file, args[3] );
		if ( length <= 0 && args[3] == FS_READ ) {
			CL_UI_LogFsOpen( request, args[3], length, "" );
		}
		if ( length > 0 || args[3] != FS_READ ) {
			return length;
		}

		if ( !CL_OnlineServicesEnabled() ) {
			return length;
		}

		Com_Memset( resolved, 0, sizeof( resolved ) );
		if ( qlr_fs_imports.fopen_web_file_read( request, file, resolved, sizeof( resolved ) ) && *file ) {
			CL_UI_LogFsOpen( request, args[3], qlr_fs_imports.filelength( *file ), resolved );
			return qlr_fs_imports.filelength( *file );
		}

		return length;
	}

	case UI_FS_READ:
		qlr_fs_imports.read( VMA(1), args[2], args[3] );
		return 0;

	case UI_FS_WRITE:
		qlr_fs_imports.write( VMA(1), args[2], args[3] );
		return 0;

	case UI_FS_FCLOSEFILE:
		qlr_fs_imports.fclose_file( args[1] );
		return 0;

	case UI_FS_GETFILELIST:
		return qlr_fs_imports.get_file_list( VMA(1), VMA(2), VMA(3), args[4] );

	case UI_FS_SEEK:
		return qlr_fs_imports.seek( args[1], args[2], args[3] );
	case UI_LAUNCHER_READSCREENSHOT:
		return CL_MenuReadScreenshot( VMA(1), VMA(2), args[3] );
	
	case UI_R_REGISTERMODEL:
		return re.RegisterModel( VMA(1) );

	case UI_R_REGISTERSKIN:
		return re.RegisterSkin( VMA(1) );

	case UI_R_REGISTERSHADERNOMIP:
		return CL_Steam_RegisterShader( VMA(1) );

	case UI_R_CLEARSCENE:
		re.ClearScene();
		return 0;

	case UI_R_ADDREFENTITYTOSCENE:
		re.AddRefEntityToScene( VMA(1) );
		return 0;

	case UI_R_ADDPOLYTOSCENE:
		re.AddPolyToScene( args[1], args[2], VMA(3), 1 );
		return 0;

	case UI_R_ADDLIGHTTOSCENE:
		re.AddLightToScene( VMA(1), VMF(2), VMF(3), VMF(4), VMF(5) );
		return 0;

	case UI_R_RENDERSCENE:
		re.RenderScene( VMA(1) );
		return 0;

	case UI_R_SETCOLOR:
		re.SetColor( VMA(1) );
		return 0;

	case UI_R_DRAWSTRETCHPIC:
		re.DrawStretchPic( VMF(1), VMF(2), VMF(3), VMF(4), VMF(5), VMF(6), VMF(7), VMF(8), args[9] );
		return 0;

  case UI_R_MODELBOUNDS:
		re.ModelBounds( args[1], VMA(2), VMA(3) );
		return 0;

	case UI_UPDATESCREEN:
		SCR_UpdateScreen();
		return 0;

	case UI_CM_LERPTAG:
		re.LerpTag( VMA(1), args[2], args[3], args[4], VMF(5), VMA(6) );
		return 0;

	case UI_S_REGISTERSOUND:
		return S_RegisterSound( VMA(1), args[2] ? qtrue : qfalse );

	case UI_S_STARTLOCALSOUND:
		S_StartLocalSound( args[1], args[2] );
		return 0;

	case UI_KEY_KEYNUMTOSTRINGBUF:
		Key_KeynumToStringBuf( args[1], VMA(2), args[3] );
		return 0;

	case UI_KEY_GETBINDINGBUF:
		Key_GetBindingBuf( args[1], VMA(2), args[3] );
		return 0;

	case UI_KEY_SETBINDING:
		Key_SetBinding( args[1], VMA(2) );
		return 0;

	case UI_KEY_ISDOWN:
		return Key_IsDown( args[1] ) ? qtrue : qfalse;

	case UI_KEY_GETOVERSTRIKEMODE:
		return Key_GetOverstrikeMode() ? qtrue : qfalse;

	case UI_KEY_SETOVERSTRIKEMODE:
		Key_SetOverstrikeMode( args[1] ? qtrue : qfalse );
		return 0;

	case UI_KEY_CLEARSTATES:
		Key_ClearStates();
		return 0;

	case UI_KEY_GETCATCHER:
		return Key_GetCatcher();

	case UI_KEY_SETCATCHER:
		Key_SetCatcher( args[1] );
		return 0;

	case UI_GETCLIPBOARDDATA:
		CL_UI_GetClipboardData( VMA(1), args[2] );
		return 0;

	case UI_GETCLIENTSTATE:
		GetClientState( VMA(1) );
		return 0;		

	case UI_GETGLCONFIG:
		CL_GetGlconfig( VMA(1) );
		return 0;

	case UI_GETCONFIGSTRING:
		return GetConfigString( args[1], VMA(2), args[3] );

	case UI_LAN_LOADCACHEDSERVERS:
		LAN_LoadCachedServers();
		return 0;

	case UI_LAN_SAVECACHEDSERVERS:
		LAN_SaveServersToCache();
		return 0;

	case UI_LAN_ADDSERVER:
		return LAN_AddServer(args[1], VMA(2), VMA(3));

	case UI_LAN_REMOVESERVER:
		LAN_RemoveServer(args[1], VMA(2));
		return 0;

	case UI_LAN_GETPINGQUEUECOUNT:
		return LAN_GetPingQueueCount();

	case UI_LAN_CLEARPING:
		LAN_ClearPing( args[1] );
		return 0;

	case UI_LAN_GETPING:
		LAN_GetPing( args[1], VMA(2), args[3], VMA(4) );
		return 0;

	case UI_LAN_GETPINGINFO:
		LAN_GetPingInfo( args[1], VMA(2), args[3] );
		return 0;

	case UI_LAN_GETSERVERCOUNT:
		return LAN_GetServerCount(args[1]);

	case UI_LAN_GETSERVERADDRESSSTRING:
		LAN_GetServerAddressString( args[1], args[2], VMA(3), args[4] );
		return 0;

	case UI_LAN_GETSERVERINFO:
		LAN_GetServerInfo( args[1], args[2], VMA(3), args[4] );
		return 0;

	case UI_LAN_GETSERVERPING:
		return LAN_GetServerPing( args[1], args[2] );

	case UI_LAN_MARKSERVERVISIBLE:
		LAN_MarkServerVisible( args[1], args[2], args[3] ? qtrue : qfalse );
		return 0;

	case UI_LAN_SERVERISVISIBLE:
		return LAN_ServerIsVisible( args[1], args[2] ) ? qtrue : qfalse;

	case UI_LAN_UPDATEVISIBLEPINGS:
		return LAN_UpdateVisiblePings( args[1] ) ? qtrue : qfalse;

	case UI_LAN_RESETPINGS:
		LAN_ResetPings( args[1] );
		return 0;

	case UI_LAN_SERVERSTATUS:
		return LAN_GetServerStatus( VMA(1), VMA(2), args[3] );

	case UI_LAN_COMPARESERVERS:
		return LAN_CompareServers( args[1], args[2], args[3], args[4], args[5] );

	case UI_MEMORY_REMAINING:
		return Hunk_MemoryRemaining();

	case UI_GET_CDKEY:
		CLUI_GetCDKey( VMA(1), args[2] );
		return 0;

	case UI_SET_CDKEY:
		CLUI_SetCDKey( VMA(1) );
		return 0;
	
	case UI_SET_PBCLSTATUS:
		return 0;	

	case UI_R_REGISTERFONT:
		CL_RegisterFont( VMA(1), args[2], VMA(3) );
		return 0;

	case UI_MEMSET:
		Com_Memset( VMA(1), args[2], args[3] );
		return 0;

	case UI_MEMCPY:
		Com_Memcpy( VMA(1), VMA(2), args[3] );
		return 0;

	case UI_STRNCPY:
		return (int)strncpy( VMA(1), VMA(2), args[3] );

	case UI_SIN:
		return FloatAsInt( sin( VMF(1) ) );

	case UI_COS:
		return FloatAsInt( cos( VMF(1) ) );

	case UI_ATAN2:
		return FloatAsInt( atan2( VMF(1), VMF(2) ) );

	case UI_SQRT:
		return FloatAsInt( sqrt( VMF(1) ) );

	case UI_FLOOR:
		return FloatAsInt( floor( VMF(1) ) );

	case UI_CEIL:
		return FloatAsInt( ceil( VMF(1) ) );

	case UI_PC_ADD_GLOBAL_DEFINE:
		return botlib_export->PC_AddGlobalDefine( VMA(1) );
	case UI_PC_LOAD_SOURCE:
		return botlib_export->PC_LoadSourceHandle( VMA(1) );
	case UI_PC_FREE_SOURCE:
		return botlib_export->PC_FreeSourceHandle( args[1] );
	case UI_PC_READ_TOKEN:
		return botlib_export->PC_ReadTokenHandle( args[1], VMA(2) );
	case UI_PC_SOURCE_FILE_AND_LINE:
		return botlib_export->PC_SourceFileAndLine( args[1], VMA(2), VMA(3) );

	case UI_S_STOPBACKGROUNDTRACK:
		S_StopBackgroundTrack();
		return 0;
	case UI_S_STARTBACKGROUNDTRACK:
		S_StartBackgroundTrack( VMA(1), VMA(2));
		return 0;

	case UI_REAL_TIME:
		return Com_RealTime( VMA(1) );

	case UI_CIN_PLAYCINEMATIC:
	  Com_DPrintf("UI_CIN_PlayCinematic\n");
	  return CIN_PlayCinematic(VMA(1), args[2], args[3], args[4], args[5], args[6]);

	case UI_CIN_STOPCINEMATIC:
	  return CIN_StopCinematic(args[1]);

	case UI_CIN_RUNCINEMATIC:
	  return CIN_RunCinematic(args[1]);

	case UI_CIN_DRAWCINEMATIC:
	  CIN_DrawCinematic(args[1]);
	  return 0;

	case UI_CIN_SETEXTENTS:
	  CIN_SetExtents(args[1], args[2], args[3], args[4], args[5]);
	  return 0;

	case UI_R_REMAP_SHADER:
		re.RemapShader( VMA(1), VMA(2), VMA(3) );
		return 0;

	case UI_VERIFY_CDKEY:
		return CL_CDKeyValidate(VMA(1), VMA(2)) ? qtrue : qfalse;


		
	default:
		Com_Error( ERR_DROP, "Bad UI system trap: %i", args[0] );

	}

	return 0;
}

/*
====================
CL_UISystemCalls
====================
*/
int CL_UISystemCalls( int *args ) {
	return CL_UISystemCallsImpl( args, qtrue );
}

/*
====================
UI_Import_Syscall
====================
*/
static int QDECL UI_Import_Syscall( int arg, ... ) {
	int args[SYSCALL_CONTRACT_MAX_ARGS];
	int i;
	va_list ap;

	args[0] = arg;

	va_start(ap, arg);
	for (i = 1; i < SYSCALL_CONTRACT_MAX_ARGS; i++) {
		args[i] = va_arg(ap, int);
	}
	va_end(ap);

	return CL_UISystemCallsImpl( args, qfalse );
}

#include "ql_ui_imports.inc"

typedef void (QDECL *ql_import_f)( void );

/*
==============
QL_UI_trap_Cmd_ExecuteText_QL
==============
*/
static void QDECL QL_UI_trap_Cmd_ExecuteText_QL( int maybeExec, const char *maybeText ) {
	const char *text = maybeText;
	int exec_when = maybeExec;

	if ( exec_when < EXEC_NOW || exec_when > EXEC_APPEND ) {
		text = (const char *)maybeExec;
		exec_when = EXEC_APPEND;
	}

	if ( !text ) {
		return;
	}

	Cbuf_ExecuteText( exec_when, text );
}

/*
==============
QL_UI_trap_Cmd_ArgsBuffer_QL
==============
*/
static void QDECL QL_UI_trap_Cmd_ArgsBuffer_QL( char *buffer, int bufferLength ) {
	Cmd_ArgsBuffer( buffer, bufferLength );
}

/*
==============
QL_UI_trap_S_RegisterSound_QL
==============
*/
static sfxHandle_t QDECL QL_UI_trap_S_RegisterSound_QL( const char *sample, int compressed ) {
	if ( compressed != qfalse && compressed != qtrue ) {
		compressed = qfalse;
	}

	return S_RegisterSound( sample, compressed );
}

/*
==============
QL_UI_trap_SetCDKey_QL
==============
*/
static int QDECL QL_UI_trap_SetCDKey_QL( char *buf ) {
	QL_UI_trap_SetCDKey( buf );
	return 0;
}

typedef enum {
	QL_UI_SCALED_FONT_NORMAL = 0,
	QL_UI_SCALED_FONT_SANS,
	QL_UI_SCALED_FONT_MONO,
	QL_UI_SCALED_FONT_SANS_FALLBACK,
	QL_UI_SCALED_FONT_SANS_WINDOWS_FALLBACK,
	QL_UI_SCALED_FONT_COUNT
} qlUiScaledFontHandle_t;

typedef struct {
	fontInfo_t	font;
	qboolean	loaded;
} qlUiScaledFont_t;

static vec4_t ql_ui_currentColor = { 1.0f, 1.0f, 1.0f, 1.0f };
static qlUiScaledFont_t ql_ui_scaledFonts[QL_UI_SCALED_FONT_COUNT];

/*
==============
QL_UI_PackFloatBits64
==============
*/
static unsigned long long QL_UI_PackFloatBits64( float lo, float hi ) {
	unsigned long long result = (unsigned long long)(unsigned int)FloatAsInt( lo );
	result |= (unsigned long long)(unsigned int)FloatAsInt( hi ) << 32;
	return result;
}

/*
==============
QL_UI_NormalizeScaledFontHandle
==============
*/
static int QL_UI_NormalizeScaledFontHandle( int fontHandle ) {
	if ( fontHandle < QL_UI_SCALED_FONT_NORMAL || fontHandle >= QL_UI_SCALED_FONT_COUNT ) {
		return QL_UI_SCALED_FONT_NORMAL;
	}

	return fontHandle;
}

/*
==============
QL_UI_ResolveWindowsFallbackFontPath
==============
*/
static const char *QL_UI_ResolveWindowsFallbackFontPath( char *fontPath, int fontPathSize ) {
#if defined( _WIN32 )
	char windowsDirectory[MAX_OSPATH];
	WIN32_FIND_DATAA findData;
	HANDLE findHandle;

	if ( GetWindowsDirectoryA( windowsDirectory, sizeof( windowsDirectory ) ) > 0 ) {
		Com_sprintf( fontPath, fontPathSize, "%s\\fonts\\ARIALUNI.TTF", windowsDirectory );
		findHandle = FindFirstFileA( fontPath, &findData );
		if ( findHandle != INVALID_HANDLE_VALUE ) {
			FindClose( findHandle );
			return fontPath;
		}

		Com_sprintf( fontPath, fontPathSize, "%s\\fonts\\segoeui.ttf", windowsDirectory );
		findHandle = FindFirstFileA( fontPath, &findData );
		if ( findHandle != INVALID_HANDLE_VALUE ) {
			FindClose( findHandle );
			return fontPath;
		}

		Com_sprintf( fontPath, fontPathSize, "%s\\fonts\\l_10646.ttf", windowsDirectory );
		return fontPath;
	}
#endif

	Q_strncpyz( fontPath, "fonts/droidsansfallbackfull.ttf", fontPathSize );
	return fontPath;
}

/*
==============
QL_UI_GetScaledFontName
==============
*/
static const char *QL_UI_GetScaledFontName( int fontHandle, char *resolvedFontPath, int resolvedFontPathSize ) {
	switch ( QL_UI_NormalizeScaledFontHandle( fontHandle ) ) {
		case QL_UI_SCALED_FONT_SANS:
			return "fonts/notosans-regular.ttf";

		case QL_UI_SCALED_FONT_MONO:
			return "fonts/droidsansmono.ttf";

		case QL_UI_SCALED_FONT_SANS_FALLBACK:
			return "fonts/droidsansfallbackfull.ttf";

		case QL_UI_SCALED_FONT_SANS_WINDOWS_FALLBACK:
			return QL_UI_ResolveWindowsFallbackFontPath( resolvedFontPath, resolvedFontPathSize );

		case QL_UI_SCALED_FONT_NORMAL:
		default:
			return "fonts/handelgothic.ttf";
	}
}

/*
==============
QL_UI_GetScaledFont
==============
*/
static fontInfo_t *QL_UI_GetScaledFont( int fontHandle ) {
	qlUiScaledFont_t *scaledFont;
	char resolvedFontPath[MAX_OSPATH];
	const char *fontName;

	fontHandle = QL_UI_NormalizeScaledFontHandle( fontHandle );
	scaledFont = &ql_ui_scaledFonts[fontHandle];
	if ( !scaledFont->loaded ) {
		fontName = QL_UI_GetScaledFontName( fontHandle, resolvedFontPath, sizeof( resolvedFontPath ) );
		CL_RegisterFont( fontName, 48, &scaledFont->font );
		scaledFont->loaded = qtrue;
	}

	return &scaledFont->font;
}

/*
==============
QL_UI_trap_R_SetColor_QL
==============
*/
static void QDECL QL_UI_trap_R_SetColor_QL( const float *rgba ) {
	if ( rgba ) {
		ql_ui_currentColor[0] = rgba[0];
		ql_ui_currentColor[1] = rgba[1];
		ql_ui_currentColor[2] = rgba[2];
		ql_ui_currentColor[3] = rgba[3];
	} else {
		ql_ui_currentColor[0] = 1.0f;
		ql_ui_currentColor[1] = 1.0f;
		ql_ui_currentColor[2] = 1.0f;
		ql_ui_currentColor[3] = 1.0f;
	}

	re.SetColor( rgba );
}

/*
==============
QL_UI_DrawGlyph
==============
*/
static void QL_UI_DrawGlyph( float x, float y, float scaleFactor, glyphInfo_t *glyph ) {
	float w;
	float h;

	if ( !glyph ) {
		return;
	}

	w = glyph->imageWidth * scaleFactor;
	h = glyph->imageHeight * scaleFactor;

	re.DrawStretchPic( x, y, w, h, glyph->s, glyph->t, glyph->s2, glyph->t2, glyph->glyph );
}

/*
==============
QL_UI_RegisterDefaultAdvertCellShader
==============
*/
static qhandle_t QL_UI_RegisterDefaultAdvertCellShader( const char *defaultContent ) {
	if ( !defaultContent || !defaultContent[0] ) {
		return 0;
	}

	return CL_Steam_RegisterShader( defaultContent );
}

/*
==============
QL_UI_trap_SetupAdvertCellShader
==============
*/
static qhandle_t QDECL QL_UI_trap_SetupAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {
	// uix86.dll HLIL: import[80] (offset 0x140) prepares an advert cell shader and falls back to default content.
	(void)rect;
	(void)cellId;

	return QL_UI_RegisterDefaultAdvertCellShader( defaultContent );
}

/*
==============
QL_UI_trap_RefreshAdvertCellShader
==============
*/
static qhandle_t QDECL QL_UI_trap_RefreshAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {
	// uix86.dll HLIL: import[81] (offset 0x144) refreshes an advert cell shader and falls back to default content.
	(void)rect;
	(void)cellId;

	return QL_UI_RegisterDefaultAdvertCellShader( defaultContent );
}

/*
==============
QL_UI_trap_InitAdvertisementBridge
==============
*/
static void QDECL QL_UI_trap_InitAdvertisementBridge( void ) {
	// uix86.dll HLIL: import[82] (offset 0x148) is invoked during UI init with no args.
	// Quake Live retail thunks to AdvertisementBridge_InitUI; mirror the host bridge init even when the live provider is absent.
	CL_AdvertisementBridge_InitUI();
}

/*
==============
QL_UI_trap_UpdateAdvert
==============
*/
static void QDECL QL_UI_trap_UpdateAdvert( int handleOrToken, int area ) {
	// uix86.dll HLIL: import[83] (offset 0x14c) is called by the retail UI advert ownerdraw after the quad draw.
	// The committed host slab resolves the provider to the inert sub_4d7980 stub, so the arguments remain opaque.
	(void)handleOrToken;
	(void)area;
}

/*
==============
QL_UI_trap_ActivateAdvert
==============
*/
static void QDECL QL_UI_trap_ActivateAdvert( int cellId ) {
	// uix86.dll HLIL: import[84] (offset 0x150) forwards the retail activateAdvert script command into AdvertisementBridge_ActivateAdvert.
	CL_AdvertisementBridge_ActivateAdvert( cellId );
}

/*
==============
QL_UI_trap_Unused85
==============
*/
static int QDECL QL_UI_trap_Unused85( void ) {
	// uix86.dll HLIL: import[85] (offset 0x154) resolves to a no-op placeholder in retail.
	return 0;
}

/*
==============
QL_UI_trap_SetCursorPos
==============
*/
static int QDECL QL_UI_trap_SetCursorPos( int x, int y ) {
#if defined( _WIN32 )
	return SetCursorPos( x, y ) ? 1 : 0;
#else
	(void)x;
	(void)y;
	return 0;
#endif
}

/*
==============
QL_UI_trap_GetCursorPos
==============
*/
static int QDECL QL_UI_trap_GetCursorPos( int *x, int *y ) {
#if defined( _WIN32 )
	POINT point;

	if ( !GetCursorPos( &point ) ) {
		if ( x ) {
			*x = 0;
		}
		if ( y ) {
			*y = 0;
		}
		return 0;
	}

	if ( x ) {
		*x = point.x;
	}
	if ( y ) {
		*y = point.y;
	}
	return 1;
#else
	if ( x ) {
		*x = 0;
	}
	if ( y ) {
		*y = 0;
	}
	return 0;
#endif
}

/*
==============
QL_UI_trap_IsSubscribedApp
==============
*/
static int QDECL QL_UI_trap_IsSubscribedApp( int arg1 ) {
	// uix86.dll HLIL: import[93] (offset 0x174) checks Steam subscription for app IDs.
	if ( !CL_SteamServicesEnabled() ) {
		return 0;
	}

	return QL_Steamworks_IsSubscribedApp( (uint32_t)arg1 ) ? 1 : 0;
}

/*
==============
QL_UI_trap_DrawScaledText
==============
*/
static void QDECL QL_UI_trap_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, int forceColor ) {
	fontInfo_t *font;
	const char *s;
	vec4_t baseColor;
	float drawX;
	float scaleFactor;
	qboolean hasMaxX;
	float maxXf;

	// uix86.dll HLIL: import[94] (offset 0x178) draws scaled text with maxX/outMaxX.

	if ( !text || !text[0] ) {
		if ( outMaxX ) {
			*outMaxX = (float)x;
		}
		return;
	}

	Com_Memcpy( baseColor, ql_ui_currentColor, sizeof( baseColor ) );

	font = QL_UI_GetScaledFont( fontHandle );
	if ( scale <= 0.0f ) {
		scaleFactor = 1.0f;
	} else {
		scaleFactor = scale / 48.0f;
	}

	drawX = (float)x;
	s = text;
	hasMaxX = ( maxX > 0 );
	maxXf = (float)maxX;

	while ( *s ) {
		unsigned char ch = (unsigned char)*s;

		if ( !forceColor && Q_IsColorString( s ) ) {
			vec4_t newColor;
			Com_Memcpy( newColor, g_color_table[ColorIndex( *( s + 1 ) )], sizeof( newColor ) );
			newColor[3] = baseColor[3];
			re.SetColor( newColor );
			s += 2;
			continue;
		}

		if ( ch >= GLYPH_START && ch <= GLYPH_END ) {
			glyphInfo_t *glyph = &font->glyphs[ch];
			float yadj = glyph->top * scaleFactor;
			float nextX = drawX + glyph->xSkip * scaleFactor;

			if ( hasMaxX && nextX > maxXf ) {
				if ( outMaxX ) {
					*outMaxX = 0.0f;
				}
				break;
			}

			QL_UI_DrawGlyph( drawX, (float)y - yadj, scaleFactor, glyph );
			drawX = nextX;
			if ( outMaxX ) {
				*outMaxX = drawX;
			}
		}

		++s;
	}

	re.SetColor( baseColor );
}

/*
==============
QL_UI_trap_MeasureText
==============
*/
static unsigned long long QDECL QL_UI_trap_MeasureText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outLeft ) {
	fontInfo_t *font;
	const char *s;
	float width;
	float height;
	float scaleFactor;
	qboolean hasMaxX;
	float maxXf;

	// uix86.dll HLIL: import[95] (offset 0x17c) measures text and returns packed floats.

	if ( outLeft ) {
		*outLeft = 0.0f;
	}

	if ( !text ) {
		return QL_UI_PackFloatBits64( 0.0f, 0.0f );
	}

	font = QL_UI_GetScaledFont( fontHandle );
	if ( scale <= 0.0f ) {
		scaleFactor = 1.0f;
	} else {
		scaleFactor = scale / 48.0f;
	}

	width = 0.0f;
	height = 0.0f;
	hasMaxX = ( maxX > 0 );
	maxXf = (float)maxX;

	for ( s = text; *s && ( !end || s < end ); ++s ) {
		unsigned char ch = (unsigned char)*s;

		if ( Q_IsColorString( s ) ) {
			++s;
			if ( !*s ) {
				break;
			}
			continue;
		}

		if ( ch >= GLYPH_START && ch <= GLYPH_END ) {
			glyphInfo_t *glyph = &font->glyphs[ch];
			float nextW = width + glyph->xSkip * scaleFactor;
			float glyphH = glyph->height * scaleFactor;

			if ( hasMaxX && nextW > maxXf ) {
				break;
			}

			width = nextW;
			if ( glyphH > height ) {
				height = glyphH;
			}
		}
	}

	return QL_UI_PackFloatBits64( width, height );
}

/*
==============
QL_UI_trap_GetItemDownloadInfo
==============
*/
static void QDECL QL_UI_trap_GetItemDownloadInfo( unsigned int arg1, unsigned int arg2, unsigned long long *outDownloaded, unsigned long long *outTotal ) {
	unsigned long long downloaded = 0;
	unsigned long long total = 0;

	// uix86.dll HLIL: import[96] (offset 0x180) returns download stats for workshop items.
	if ( !QL_Steamworks_GetItemDownloadInfo( arg1, arg2, &downloaded, &total ) ) {
		downloaded = (unsigned long long)(unsigned int)clc.downloadCount;
		total = (unsigned long long)(unsigned int)clc.downloadSize;
	}

	if ( outDownloaded ) {
		*outDownloaded = downloaded;
	}
	if ( outTotal ) {
		*outTotal = total;
	}
}

static ql_import_f ql_ui_imports[UI_QL_NATIVE_IMPORT_COUNT];

/*
==============
CL_InitUIImports
==============
*/
static void CL_InitUIImports( void ) {
	Com_Memset( ql_ui_imports, 0, sizeof( ql_ui_imports ) );

	// uix86.dll HLIL: import[0] is Print, import[1] is Error.
	ql_ui_imports[UI_QL_IMPORT_PRINT] = (ql_import_f)QL_UI_trap_Print;
	ql_ui_imports[UI_QL_IMPORT_ERROR] = (ql_import_f)QL_UI_trap_Error;
	ql_ui_imports[UI_QL_IMPORT_MILLISECONDS] = (ql_import_f)QL_UI_trap_Milliseconds;
	// uix86.dll HLIL: import[3] is RealTime, import[6] is Cvar_Update.
	ql_ui_imports[UI_QL_IMPORT_REAL_TIME] = (ql_import_f)QL_UI_trap_RealTime;
	ql_ui_imports[UI_QL_IMPORT_CVAR_REGISTER] = (ql_import_f)QL_UI_trap_Cvar_Register;
	ql_ui_imports[UI_QL_IMPORT_CVAR_CREATE] = (ql_import_f)QL_UI_trap_Cvar_Create;
	ql_ui_imports[UI_QL_IMPORT_CVAR_UPDATE] = (ql_import_f)QL_UI_trap_Cvar_Update;
	ql_ui_imports[UI_QL_IMPORT_CVAR_SET] = (ql_import_f)QL_UI_trap_Cvar_Set;
	ql_ui_imports[UI_QL_IMPORT_CVAR_SET_VALUE] = (ql_import_f)QL_UI_trap_Cvar_SetValue;
	ql_ui_imports[UI_QL_IMPORT_CVAR_VARIABLE_STRING_BUFFER] = (ql_import_f)QL_UI_trap_Cvar_VariableStringBuffer;
	ql_ui_imports[UI_QL_IMPORT_CVAR_VARIABLE_VALUE] = (ql_import_f)QL_UI_trap_Cvar_VariableValue;
	ql_ui_imports[UI_QL_IMPORT_ARGC] = (ql_import_f)QL_UI_trap_Argc;
	ql_ui_imports[UI_QL_IMPORT_ARGV] = (ql_import_f)QL_UI_trap_Argv;
	ql_ui_imports[UI_QL_IMPORT_CMD_ARGS_BUFFER] = (ql_import_f)QL_UI_trap_Cmd_ArgsBuffer_QL;
	ql_ui_imports[UI_QL_IMPORT_FS_FOPENFILE] = (ql_import_f)QL_UI_trap_FS_FOpenFile;
	ql_ui_imports[UI_QL_IMPORT_FS_READ] = (ql_import_f)QL_UI_trap_FS_Read;
	ql_ui_imports[UI_QL_IMPORT_FS_WRITE] = (ql_import_f)QL_UI_trap_FS_Write;
	ql_ui_imports[UI_QL_IMPORT_FS_FCLOSEFILE] = (ql_import_f)QL_UI_trap_FS_FCloseFile;
	ql_ui_imports[UI_QL_IMPORT_FS_SEEK] = (ql_import_f)QL_UI_trap_FS_Seek;
	ql_ui_imports[UI_QL_IMPORT_FS_GETFILELIST] = (ql_import_f)QL_UI_trap_FS_GetFileList;
	ql_ui_imports[UI_QL_IMPORT_CMD_EXECUTETEXT] = (ql_import_f)QL_UI_trap_Cmd_ExecuteText_QL;
	// uix86.dll HLIL: no dedicated Cvar_Reset import appears (no data_106b40a8 + 0x20/0x2c usage).
	// The "resetDefaults" command path uses Cmd_ExecuteText("cvar_restart\n") instead.
	ql_ui_imports[UI_QL_IMPORT_R_REGISTERMODEL] = (ql_import_f)QL_UI_trap_R_RegisterModel;
	ql_ui_imports[UI_QL_IMPORT_R_REGISTERSKIN] = (ql_import_f)QL_UI_trap_R_RegisterSkin;
	ql_ui_imports[UI_QL_IMPORT_R_REGISTERSHADERNOMIP] = (ql_import_f)QL_UI_trap_R_RegisterShaderNoMip;
	ql_ui_imports[UI_QL_IMPORT_R_CLEARSCENE] = (ql_import_f)QL_UI_trap_R_ClearScene;
	ql_ui_imports[UI_QL_IMPORT_R_ADDREFENTITYTOSCENE] = (ql_import_f)QL_UI_trap_R_AddRefEntityToScene;
	ql_ui_imports[UI_QL_IMPORT_R_ADDPOLYTOSCENE] = (ql_import_f)QL_UI_trap_R_AddPolyToScene;
	ql_ui_imports[UI_QL_IMPORT_R_ADDLIGHTTOSCENE] = (ql_import_f)QL_UI_trap_R_AddLightToScene;
	ql_ui_imports[UI_QL_IMPORT_R_RENDERSCENE] = (ql_import_f)QL_UI_trap_R_RenderScene;
	ql_ui_imports[UI_QL_IMPORT_R_SETCOLOR] = (ql_import_f)QL_UI_trap_R_SetColor_QL;
	ql_ui_imports[UI_QL_IMPORT_R_DRAWSTRETCHPIC] = (ql_import_f)QL_UI_trap_R_DrawStretchPic;
	ql_ui_imports[UI_QL_IMPORT_R_MODELBOUNDS] = (ql_import_f)QL_UI_trap_R_ModelBounds;
	ql_ui_imports[UI_QL_IMPORT_UPDATESCREEN] = (ql_import_f)QL_UI_trap_UpdateScreen;
	ql_ui_imports[UI_QL_IMPORT_CM_LERPTAG] = (ql_import_f)QL_UI_trap_CM_LerpTag;
	ql_ui_imports[UI_QL_IMPORT_S_STARTLOCALSOUND] = (ql_import_f)QL_UI_trap_S_StartLocalSound;
	ql_ui_imports[UI_QL_IMPORT_S_REGISTERSOUND] = (ql_import_f)QL_UI_trap_S_RegisterSound_QL;
	ql_ui_imports[UI_QL_IMPORT_KEY_KEYNUMTOSTRINGBUF] = (ql_import_f)QL_UI_trap_Key_KeynumToStringBuf;
	ql_ui_imports[UI_QL_IMPORT_KEY_GETBINDINGBUF] = (ql_import_f)QL_UI_trap_Key_GetBindingBuf;
	ql_ui_imports[UI_QL_IMPORT_KEY_SETBINDING] = (ql_import_f)QL_UI_trap_Key_SetBinding;
	ql_ui_imports[UI_QL_IMPORT_KEY_ISDOWN] = (ql_import_f)QL_UI_trap_Key_IsDown;
	ql_ui_imports[UI_QL_IMPORT_KEY_GETOVERSTRIKEMODE] = (ql_import_f)QL_UI_trap_Key_GetOverstrikeMode;
	ql_ui_imports[UI_QL_IMPORT_KEY_SETOVERSTRIKEMODE] = (ql_import_f)QL_UI_trap_Key_SetOverstrikeMode;
	ql_ui_imports[UI_QL_IMPORT_KEY_CLEARSTATES] = (ql_import_f)QL_UI_trap_Key_ClearStates;
	ql_ui_imports[UI_QL_IMPORT_KEY_GETCATCHER] = (ql_import_f)QL_UI_trap_Key_GetCatcher;
	ql_ui_imports[UI_QL_IMPORT_KEY_SETCATCHER] = (ql_import_f)QL_UI_trap_Key_SetCatcher;
	ql_ui_imports[UI_QL_IMPORT_GETCLIPBOARDDATA] = (ql_import_f)QL_UI_trap_GetClipboardData;
	ql_ui_imports[UI_QL_IMPORT_GETCLIENTSTATE] = (ql_import_f)QL_UI_trap_GetClientState;
	ql_ui_imports[UI_QL_IMPORT_GETGLCONFIG] = (ql_import_f)QL_UI_trap_GetGlconfig;
	ql_ui_imports[UI_QL_IMPORT_GETCONFIGSTRING] = (ql_import_f)QL_UI_trap_GetConfigString;
	ql_ui_imports[UI_QL_IMPORT_LAN_GETSERVERCOUNT] = (ql_import_f)QL_UI_trap_LAN_GetServerCount;
	ql_ui_imports[UI_QL_IMPORT_LAN_GETSERVERADDRESSSTRING] = (ql_import_f)QL_UI_trap_LAN_GetServerAddressString;
	ql_ui_imports[UI_QL_IMPORT_LAN_GETSERVERINFO] = (ql_import_f)QL_UI_trap_LAN_GetServerInfo;
	ql_ui_imports[UI_QL_IMPORT_LAN_GETSERVERPING] = (ql_import_f)QL_UI_trap_LAN_GetServerPing;
	ql_ui_imports[UI_QL_IMPORT_LAN_GETPINGQUEUECOUNT] = (ql_import_f)QL_UI_trap_LAN_GetPingQueueCount;
	ql_ui_imports[UI_QL_IMPORT_LAN_CLEARPING] = (ql_import_f)QL_UI_trap_LAN_ClearPing;
	ql_ui_imports[UI_QL_IMPORT_LAN_GETPING] = (ql_import_f)QL_UI_trap_LAN_GetPing;
	ql_ui_imports[UI_QL_IMPORT_LAN_GETPINGINFO] = (ql_import_f)QL_UI_trap_LAN_GetPingInfo;
	ql_ui_imports[UI_QL_IMPORT_LAN_LOADCACHEDSERVERS] = (ql_import_f)QL_UI_trap_LAN_LoadCachedServers;
	ql_ui_imports[UI_QL_IMPORT_LAN_SAVECACHEDSERVERS] = (ql_import_f)QL_UI_trap_LAN_SaveCachedServers;
	ql_ui_imports[UI_QL_IMPORT_LAN_MARKSERVERVISIBLE] = (ql_import_f)QL_UI_trap_LAN_MarkServerVisible;
	ql_ui_imports[UI_QL_IMPORT_LAN_SERVERISVISIBLE] = (ql_import_f)QL_UI_trap_LAN_ServerIsVisible;
	ql_ui_imports[UI_QL_IMPORT_LAN_UPDATEVISIBLEPINGS] = (ql_import_f)QL_UI_trap_LAN_UpdateVisiblePings;
	ql_ui_imports[UI_QL_IMPORT_LAN_ADDSERVER] = (ql_import_f)QL_UI_trap_LAN_AddServer;
	ql_ui_imports[UI_QL_IMPORT_LAN_REMOVESERVER] = (ql_import_f)QL_UI_trap_LAN_RemoveServer;
	ql_ui_imports[UI_QL_IMPORT_LAN_RESETPINGS] = (ql_import_f)QL_UI_trap_LAN_ResetPings;
	ql_ui_imports[UI_QL_IMPORT_LAN_SERVERSTATUS] = (ql_import_f)QL_UI_trap_LAN_ServerStatus;
	ql_ui_imports[UI_QL_IMPORT_LAN_COMPARESERVERS] = (ql_import_f)QL_UI_trap_LAN_CompareServers;

	// Retail native UI order keeps MemoryRemaining directly before the cdkey slice.
	ql_ui_imports[UI_QL_IMPORT_MEMORY_REMAINING] = (ql_import_f)QL_UI_trap_MemoryRemaining;

	// uix86.dll/native UI: cdkey helpers at offsets 0x110..0x13c.
	ql_ui_imports[UI_QL_IMPORT_GET_CDKEY] = (ql_import_f)QL_UI_trap_GetCDKey;
	ql_ui_imports[UI_QL_IMPORT_SET_CDKEY] = (ql_import_f)QL_UI_trap_SetCDKey_QL;

	// uix86.dll HLIL: import[70] (offset 0x118) is trap_R_RegisterFont(fontName, pointSize, fontInfo*).
	ql_ui_imports[UI_QL_IMPORT_R_REGISTERFONT] = (ql_import_f)QL_UI_trap_R_RegisterFont;
	ql_ui_imports[UI_QL_IMPORT_S_STOPBACKGROUNDTRACK] = (ql_import_f)QL_UI_trap_S_StopBackgroundTrack;
	ql_ui_imports[UI_QL_IMPORT_S_STARTBACKGROUNDTRACK] = (ql_import_f)QL_UI_trap_S_StartBackgroundTrack;
	ql_ui_imports[UI_QL_IMPORT_CIN_PLAYCINEMATIC] = (ql_import_f)QL_UI_trap_CIN_PlayCinematic;
	ql_ui_imports[UI_QL_IMPORT_CIN_STOPCINEMATIC] = (ql_import_f)QL_UI_trap_CIN_StopCinematic;
	ql_ui_imports[UI_QL_IMPORT_CIN_DRAWCINEMATIC] = (ql_import_f)QL_UI_trap_CIN_DrawCinematic;
	ql_ui_imports[UI_QL_IMPORT_CIN_RUNCINEMATIC] = (ql_import_f)QL_UI_trap_CIN_RunCinematic;
	ql_ui_imports[UI_QL_IMPORT_CIN_SETEXTENTS] = (ql_import_f)QL_UI_trap_CIN_SetExtents;
	ql_ui_imports[UI_QL_IMPORT_R_REMAP_SHADER] = (ql_import_f)QL_UI_trap_R_RemapShader;
	ql_ui_imports[UI_QL_IMPORT_VERIFY_CDKEY] = (ql_import_f)QL_UI_trap_VerifyCDKey;

	// uix86.dll HLIL: Quake Live-specific imports at offsets 0x140..0x180.
	ql_ui_imports[UI_QL_IMPORT_SETUP_ADVERT_CELL_SHADER] = (ql_import_f)QL_UI_trap_SetupAdvertCellShader;
	ql_ui_imports[UI_QL_IMPORT_REFRESH_ADVERT_CELL_SHADER] = (ql_import_f)QL_UI_trap_RefreshAdvertCellShader;
	ql_ui_imports[UI_QL_IMPORT_INIT_ADVERTISEMENT_BRIDGE] = (ql_import_f)QL_UI_trap_InitAdvertisementBridge;
	ql_ui_imports[UI_QL_IMPORT_UNUSED_83] = (ql_import_f)QL_UI_trap_UpdateAdvert;
	ql_ui_imports[UI_QL_IMPORT_ACTIVATE_ADVERT] = (ql_import_f)QL_UI_trap_ActivateAdvert;
	ql_ui_imports[UI_QL_IMPORT_UNUSED_85] = (ql_import_f)QL_UI_trap_Unused85;
	ql_ui_imports[UI_QL_IMPORT_SET_CURSOR_POS] = (ql_import_f)QL_UI_trap_SetCursorPos;
	ql_ui_imports[UI_QL_IMPORT_GET_CURSOR_POS] = (ql_import_f)QL_UI_trap_GetCursorPos;

	// uix86.dll HLIL: parser imports at offsets 0x160..0x170 (indices 88-92).
	ql_ui_imports[UI_QL_IMPORT_PC_ADD_GLOBAL_DEFINE] = (ql_import_f)QL_UI_trap_PC_AddGlobalDefine;
	ql_ui_imports[UI_QL_IMPORT_PC_LOAD_SOURCE] = (ql_import_f)QL_UI_trap_PC_LoadSource;
	ql_ui_imports[UI_QL_IMPORT_PC_FREE_SOURCE] = (ql_import_f)QL_UI_trap_PC_FreeSource;
	ql_ui_imports[UI_QL_IMPORT_PC_READ_TOKEN] = (ql_import_f)QL_UI_trap_PC_ReadToken;
	ql_ui_imports[UI_QL_IMPORT_PC_SOURCE_FILE_AND_LINE] = (ql_import_f)QL_UI_trap_PC_SourceFileAndLine;

	ql_ui_imports[UI_QL_IMPORT_IS_SUBSCRIBED_APP] = (ql_import_f)QL_UI_trap_IsSubscribedApp;
	ql_ui_imports[UI_QL_IMPORT_DRAW_SCALED_TEXT] = (ql_import_f)QL_UI_trap_DrawScaledText;
	ql_ui_imports[UI_QL_IMPORT_MEASURE_TEXT] = (ql_import_f)QL_UI_trap_MeasureText;
	ql_ui_imports[UI_QL_IMPORT_GET_ITEM_DOWNLOAD_INFO] = (ql_import_f)QL_UI_trap_GetItemDownloadInfo;

	// Source-side native bridge extensions beyond the recovered retail slab.
	ql_ui_imports[UI_QL_IMPORT_CVAR_RESET] = (ql_import_f)QL_UI_trap_Cvar_Reset;
	ql_ui_imports[UI_QL_IMPORT_CVAR_INFOSTRINGBUFFER] = (ql_import_f)QL_UI_trap_Cvar_InfoStringBuffer;
	ql_ui_imports[UI_QL_IMPORT_CM_LOADMODEL] = (ql_import_f)QL_UI_trap_CM_LoadModel;
	ql_ui_imports[UI_QL_IMPORT_SET_PBCLSTATUS] = (ql_import_f)QL_UI_trap_SetPbClStatus;
	ql_ui_imports[UI_QL_IMPORT_LAUNCHER_READSCREENSHOT] = (ql_import_f)QL_UI_trap_Launcher_ReadScreenshot;
}

/*
====================
CL_ShutdownUI
====================
*/
void CL_ShutdownUI( void ) {
	cls.keyCatchers &= ~KEYCATCH_UI;
	cls.uiStarted = qfalse;
	if ( cl_uiFsLogHandle ) {
		FS_FCloseFile( cl_uiFsLogHandle );
		cl_uiFsLogHandle = 0;
	}
	if ( !uivm ) {
		return;
	}
	VM_Call( uivm, UI_SHUTDOWN );
	VM_Free( uivm );
	uivm = NULL;
}

/*
====================
CL_InitUI
====================
*/
#define UI_OLD_API_VERSION	4

void CL_InitUI( void ) {
	int		v;
	qboolean	inGame;
	vmInterpret_t		interpret;

	Com_Printf( "----- UI Initialization -----\n" );
	CL_RefreshOnlineServicesBridgeState();

	// load the dll or bytecode
	interpret = Cvar_VariableValue( "vm_ui" );
	CL_InitUIImports();

	uivm = VM_Create( "ui", CL_UISystemCalls, interpret, ql_ui_imports, UI_QL_API_VERSION );
	if ( !uivm ) {
		Com_Error( ERR_FATAL, "VM_Create on UI failed" );
	}

	v = VM_Call( uivm, UI_GETAPIVERSION );
	inGame = ( cls.state >= CA_AUTHORIZING && cls.state < CA_ACTIVE ) ? qtrue : qfalse;
	if (v == UI_OLD_API_VERSION) {
//		Com_Printf(S_COLOR_YELLOW "WARNING: loading old Quake III Arena User Interface version %d\n", v );
		// init for this gamestate
		VM_Call( uivm, UI_INIT, inGame );
	}
	else if (v != UI_API_VERSION && v != UI_QL_API_VERSION) {
		Com_Error( ERR_DROP, "User Interface is version %d, expected %d", v, UI_QL_API_VERSION );
		cls.uiStarted = qfalse;
	}
	else {
		// init for this gamestate
		VM_Call( uivm, UI_INIT, inGame );
	}
	Com_Printf( "----- UI Initialization Complete -----\n" );
}

qboolean UI_usesUniqueCDKey() {
	if (uivm) {
		return VM_Call( uivm, UI_HASUNIQUECDKEY ) ? qtrue : qfalse;
	} else {
		return qfalse;
	}
}

/*
====================
UI_GameCommand

See if the current console command is claimed by the ui
====================
*/
qboolean UI_GameCommand( void ) {
	if ( !uivm ) {
		return qfalse;
	}

	return VM_Call( uivm, UI_CONSOLE_COMMAND, cls.realtime ) ? qtrue : qfalse;
}
