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
// cl_cgame.c  -- client system interaction with client game

#include "client.h"

#include "../game/botlib.h"
#include "../qcommon/vm_local.h"
#include "../../common/platform/platform_services.h"
#include "../../common/platform/platform_steamworks.h"
#include "../../../src-re/include/fs_imports.h"
#include <stdint.h>
#include <stdlib.h>
#ifdef _WIN32
#include <windows.h>
#endif

extern	botlib_export_t	*botlib_export;

extern qboolean loadCamera(const char *name);
extern void startCamera(int time);
extern qboolean getCameraInfo(int time, vec3_t *origin, vec3_t *angles);
void R_MirrorPoint( vec3_t in, orientation_t *surface, orientation_t *camera, vec3_t out );
void R_MirrorVector( vec3_t in, orientation_t *surface, orientation_t *camera, vec3_t out );

static qboolean cl_webBrowserVisible = qfalse;
static char cl_webBrowserHash[MAX_STRING_CHARS];

typedef struct {
	qboolean	initialised;
	qboolean	overlayCompiled;
	qboolean	overlayAvailable;
	int			frameTime;
	int			viewWidth;
	int			viewHeight;
	int			activeAdvertCellId;
	int			activatedAdvertCellId;
} clAdvertisementBridgeState_t;

static clAdvertisementBridgeState_t cl_advertisementBridge;

/*
=============
CL_ResetBrowserOverlayState

Clears the browser overlay state when the online service bridge is unavailable.
=============
*/
static void CL_ResetBrowserOverlayState( void ) {
	cl_webBrowserVisible = qfalse;
	cl_webBrowserHash[0] = '\0';
	Cvar_Set( "web_browserActive", "0" );
}

/*
=============
CL_GetOverlayServiceDescriptor

Returns the current platform-service descriptor for the browser overlay seam.
=============
*/
static const ql_platform_feature_descriptor *CL_GetOverlayServiceDescriptor( void ) {
	const ql_platform_service_table *services = QL_GetPlatformServices();

	if ( !services ) {
		return NULL;
	}

	return &services->overlay;
}

/*
=============
CL_OverlayServiceAvailable

Returns qtrue when an online-services overlay provider is compiled and initialised.
=============
*/
static qboolean CL_OverlayServiceAvailable( void ) {
	const ql_platform_feature_descriptor *overlay = CL_GetOverlayServiceDescriptor();

	return ( overlay && overlay->compiled && overlay->initialised );
}

/*
=============
CL_RefreshOnlineServicesBridgeState

Synchronises client-visible browser and advert bridge state with the platform-service table.
=============
*/
void CL_RefreshOnlineServicesBridgeState( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	cl_advertisementBridge.overlayCompiled = qfalse;
	cl_advertisementBridge.overlayAvailable = qfalse;
	cl_advertisementBridge.viewWidth = 0;
	cl_advertisementBridge.viewHeight = 0;
	Cvar_Set( "ui_browserAwesomium", "0" );
	CL_ResetBrowserOverlayState();
#else
	const ql_platform_feature_descriptor *overlay = CL_GetOverlayServiceDescriptor();
	qboolean overlayAvailable = CL_OverlayServiceAvailable();

	cl_advertisementBridge.overlayCompiled = ( overlay && overlay->compiled );
	cl_advertisementBridge.overlayAvailable = overlayAvailable;
	cl_advertisementBridge.viewWidth = cls.glconfig.vidWidth;
	cl_advertisementBridge.viewHeight = cls.glconfig.vidHeight;

	Cvar_Set( "ui_browserAwesomium", overlayAvailable ? "1" : "0" );
	if ( !overlayAvailable ) {
		CL_ResetBrowserOverlayState();
	}
#endif
}

/*
=============
CL_AdvertisementBridge_InitUI

Mirrors the retail UI advertisement-bridge init hook.
=============
*/
void CL_AdvertisementBridge_InitUI( void ) {
	CL_RefreshOnlineServicesBridgeState();
}

/*
=============
CL_AdvertisementBridge_ActivateAdvert

Mirrors the retail UI-side advert activation bridge path.
=============
*/
void CL_AdvertisementBridge_ActivateAdvert( int cellId ) {
	cl_advertisementBridge.activatedAdvertCellId = cellId;
	CL_RefreshOnlineServicesBridgeState();
}

/*
=============
CL_AdvertisementBridge_SetActiveAdvert

Mirrors the retail cgame-side active advert selection/reset helper.
=============
*/
void CL_AdvertisementBridge_SetActiveAdvert( int cellId ) {
	cl_advertisementBridge.activeAdvertCellId = cellId;
	if ( cellId == 0 ) {
		cl_advertisementBridge.activatedAdvertCellId = 0;
	}

	CL_RefreshOnlineServicesBridgeState();
}

/*
=============
CL_Web_ShowBrowser_f

Marks the browser overlay as visible and records an optional hash target.
=============
*/
void CL_Web_ShowBrowser_f( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	CL_ResetBrowserOverlayState();
	Com_DPrintf( "web_showBrowser ignored: online services disabled by build settings\n" );
	return;
#else
	CL_RefreshOnlineServicesBridgeState();
	if ( !CL_OverlayServiceAvailable() ) {
		Com_DPrintf( "web_showBrowser ignored: browser overlay provider unavailable\n" );
		return;
	}

	cl_webBrowserVisible = qtrue;
	if ( Cmd_Argc() > 1 ) {
		const char *hash = Cmd_ArgsFrom( 1 );
		Q_strncpyz( cl_webBrowserHash, hash, sizeof( cl_webBrowserHash ) );
	} else {
		cl_webBrowserHash[0] = '\0';
	}
	Cvar_Set( "web_browserActive", "1" );
	Com_DPrintf( "web_showBrowser\n" );
#endif
}

/*
=============
CL_Web_ChangeHash_f

Updates the browser target and ensures the overlay remains visible.
=============
*/
void CL_Web_ChangeHash_f( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	CL_ResetBrowserOverlayState();
	Com_DPrintf( "web_changeHash ignored: online services disabled by build settings\n" );
	return;
#else
	CL_RefreshOnlineServicesBridgeState();
	if ( !CL_OverlayServiceAvailable() ) {
		Com_DPrintf( "web_changeHash ignored: browser overlay provider unavailable\n" );
		return;
	}

	const char *hash = ( Cmd_Argc() > 1 ) ? Cmd_ArgsFrom( 1 ) : "";
	Q_strncpyz( cl_webBrowserHash, hash, sizeof( cl_webBrowserHash ) );
	cl_webBrowserVisible = qtrue;
	Cvar_Set( "web_browserActive", "1" );
	Com_DPrintf( "web_changeHash %s\n", cl_webBrowserHash );
#endif
}

/*
=============
CL_Web_BrowserActive_f

Toggles the browser overlay active state used by the UI VM.
=============
*/
void CL_Web_BrowserActive_f( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	CL_ResetBrowserOverlayState();
	Com_DPrintf( "web_browserActive ignored: online services disabled by build settings\n" );
	return;
#else
	CL_RefreshOnlineServicesBridgeState();
	if ( !CL_OverlayServiceAvailable() ) {
		Com_DPrintf( "web_browserActive ignored: browser overlay provider unavailable\n" );
		return;
	}

	qboolean active = ( Cmd_Argc() > 1 && atoi( Cmd_Argv( 1 ) ) != 0 );

	cl_webBrowserVisible = active;
	Cvar_Set( "web_browserActive", active ? "1" : "0" );
	Com_DPrintf( "web_browserActive %s\n", active ? "1" : "0" );
#endif
}

/*
=============
CL_Web_HideBrowser_f

Hides the browser overlay and clears the active cvar latch.
=============
*/
void CL_Web_HideBrowser_f( void ) {
	cl_webBrowserVisible = qfalse;
	Cvar_Set( "web_browserActive", "0" );
	Com_DPrintf( "web_hideBrowser\n" );
}

/*
=============
CL_Web_ClearSessionState

Clears the retained URI cache layer that stands in for the retail browser
session cache.
=============
*/
static void CL_Web_ClearSessionState( void ) {
	CL_ClearSteamResourceCache( qtrue );
}

/*
=============
CL_Web_ShowError_f

Publishes a browser error through the fallback error state when no live host bridge exists.
=============
*/
void CL_Web_ShowError_f( void ) {
	const char *message = ( Cmd_Argc() > 1 ) ? Cmd_ArgsFrom( 1 ) : "";

	if ( !message ) {
		message = "";
	}

	Cvar_Set( "com_errorMessage", message );

#if QL_PLATFORM_HAS_ONLINE_SERVICES
	CL_RefreshOnlineServicesBridgeState();
	if ( CL_OverlayServiceAvailable() ) {
		cl_webBrowserVisible = qtrue;
		Cvar_Set( "web_browserActive", "1" );
	}
#endif

	Com_DPrintf( "web_showError %s\n", message );
}

/*
=============
CL_Web_ClearCache_f

Keeps the retail browser cache-clear command wired into the retained session-cache seam.
=============
*/
void CL_Web_ClearCache_f( void ) {
	CL_Web_ClearSessionState();
	Com_DPrintf( "web_clearCache\n" );
}

/*
=============
CL_Web_Reload_f

Keeps the retail browser reload command wired into the host/browser seam.
=============
*/
void CL_Web_Reload_f( void ) {
	CL_Web_ClearSessionState();

#if QL_PLATFORM_HAS_ONLINE_SERVICES
	CL_RefreshOnlineServicesBridgeState();
	if ( CL_OverlayServiceAvailable() && cl_webBrowserVisible ) {
		Cvar_Set( "web_browserActive", "1" );
	}
#endif

	Com_DPrintf( "web_reload\n" );
}

/*
=============
CL_Web_StopRefresh_f

Handles Awesomium refresh-stop requests when an overlay provider is active.
=============
*/
void CL_Web_StopRefresh_f( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	Com_DPrintf( "web_stopRefresh ignored: online services disabled by build settings\n" );
	return;
#else
	CL_RefreshOnlineServicesBridgeState();
	if ( !CL_OverlayServiceAvailable() ) {
		Com_DPrintf( "web_stopRefresh ignored: browser overlay provider unavailable\n" );
		return;
	}

	Com_DPrintf( "web_stopRefresh\n" );
#endif
}

/*
====================
CL_AdvertisementBridge_InitCGame

Bridges the retail cgame advert lifecycle into the host when available.
====================
*/
static void CL_AdvertisementBridge_InitCGame( void ) {
	cl_advertisementBridge.initialised = qtrue;
	cl_advertisementBridge.frameTime = 0;
	cl_advertisementBridge.activeAdvertCellId = 0;
	CL_RefreshOnlineServicesBridgeState();
}

/*
====================
CL_AdvertisementBridge_ShutdownCGame

Tears down the retail cgame advert lifecycle bridge when a host exists.
====================
*/
static void CL_AdvertisementBridge_ShutdownCGame( void ) {
	cl_advertisementBridge.initialised = qfalse;
	cl_advertisementBridge.frameTime = 0;
	cl_advertisementBridge.activeAdvertCellId = 0;
	cl_advertisementBridge.activatedAdvertCellId = 0;
	CL_RefreshOnlineServicesBridgeState();
}

/*
====================
CL_AdvertisementBridge_RefreshLoadingViewParameters

Mirrors the retail loading-text bridge tail when a host implementation exists.
====================
*/
void CL_AdvertisementBridge_RefreshLoadingViewParameters( void ) {
	if ( !cl_advertisementBridge.initialised ) {
		return;
	}

	CL_RefreshOnlineServicesBridgeState();
}

/*
====================
CL_AdvertisementBridge_UpdateLoadingViewParameters

Routes the loading-view update through the retail renderer export slot when available.
====================
*/
void CL_AdvertisementBridge_UpdateLoadingViewParameters( void ) {
	if ( re.AdvertisementBridge_UpdateLoadingViewParameters ) {
		re.AdvertisementBridge_UpdateLoadingViewParameters();
		return;
	}

	CL_AdvertisementBridge_RefreshLoadingViewParameters();
}

/*
====================
CL_AdvertisementBridge_SetFrameTime

Mirrors the retail frame-time update used by the loading-screen bridge tail.
====================
*/
static void CL_AdvertisementBridge_SetFrameTime( int frameTime ) {
	if ( !cl_advertisementBridge.initialised ) {
		return;
	}

	cl_advertisementBridge.frameTime = frameTime;
	CL_RefreshOnlineServicesBridgeState();
}

/*
====================
CL_GetGameState
====================
*/
void CL_GetGameState( gameState_t *gs ) {
	*gs = cl.gameState;
}

/*
====================
CL_GetGlconfig
====================
*/
void CL_GetGlconfig( glconfig_t *glconfig ) {
	*glconfig = cls.glconfig;
}


/*
====================
CL_GetUserCmd
====================
*/
qboolean CL_GetUserCmd( int cmdNumber, usercmd_t *ucmd ) {
	// cmds[cmdNumber] is the last properly generated command

	// can't return anything that we haven't created yet
	if ( cmdNumber > cl.cmdNumber ) {
		Com_Error( ERR_DROP, "CL_GetUserCmd: %i >= %i", cmdNumber, cl.cmdNumber );
	}

	// the usercmd has been overwritten in the wrapping
	// buffer because it is too far out of date
	if ( cmdNumber <= cl.cmdNumber - CMD_BACKUP ) {
		return qfalse;
	}

	*ucmd = cl.cmds[ cmdNumber & CMD_MASK ];

	return qtrue;
}

int CL_GetCurrentCmdNumber( void ) {
	return cl.cmdNumber;
}


/*
====================
CL_GetParseEntityState
====================
*/
qboolean	CL_GetParseEntityState( int parseEntityNumber, entityState_t *state ) {
	// can't return anything that hasn't been parsed yet
	if ( parseEntityNumber >= cl.parseEntitiesNum ) {
		Com_Error( ERR_DROP, "CL_GetParseEntityState: %i >= %i",
			parseEntityNumber, cl.parseEntitiesNum );
	}

	// can't return anything that has been overwritten in the circular buffer
	if ( parseEntityNumber <= cl.parseEntitiesNum - MAX_PARSE_ENTITIES ) {
		return qfalse;
	}

	*state = cl.parseEntities[ parseEntityNumber & ( MAX_PARSE_ENTITIES - 1 ) ];
	return qtrue;
}

/*
====================
CL_GetCurrentSnapshotNumber
====================
*/
void	CL_GetCurrentSnapshotNumber( int *snapshotNumber, int *serverTime ) {
	*snapshotNumber = cl.snap.messageNum;
	*serverTime = cl.snap.serverTime;
}

/*
====================
CL_GetSnapshot
====================
*/
qboolean	CL_GetSnapshot( int snapshotNumber, snapshot_t *snapshot ) {
	clSnapshot_t	*clSnap;
	int				i, count;

	if ( snapshotNumber > cl.snap.messageNum ) {
		Com_Error( ERR_DROP, "CL_GetSnapshot: snapshotNumber > cl.snapshot.messageNum" );
	}

	// if the frame has fallen out of the circular buffer, we can't return it
	if ( cl.snap.messageNum - snapshotNumber >= PACKET_BACKUP ) {
		return qfalse;
	}

	// if the frame is not valid, we can't return it
	clSnap = &cl.snapshots[snapshotNumber & PACKET_MASK];
	if ( !clSnap->valid ) {
		return qfalse;
	}

	// if the entities in the frame have fallen out of their
	// circular buffer, we can't return it
	if ( cl.parseEntitiesNum - clSnap->parseEntitiesNum >= MAX_PARSE_ENTITIES ) {
		return qfalse;
	}

	// write the snapshot
	snapshot->snapFlags = clSnap->snapFlags;
	snapshot->serverCommandSequence = clSnap->serverCommandNum;
	snapshot->ping = clSnap->ping;
	snapshot->serverTime = clSnap->serverTime;
	Com_Memcpy( snapshot->areamask, clSnap->areamask, sizeof( snapshot->areamask ) );
	snapshot->ps = clSnap->ps;
	count = clSnap->numEntities;
	if ( count > MAX_ENTITIES_IN_SNAPSHOT ) {
		Com_DPrintf( "CL_GetSnapshot: truncated %i entities to %i\n", count, MAX_ENTITIES_IN_SNAPSHOT );
		count = MAX_ENTITIES_IN_SNAPSHOT;
	}
	snapshot->numEntities = count;
	for ( i = 0 ; i < count ; i++ ) {
		snapshot->entities[i] = 
			cl.parseEntities[ ( clSnap->parseEntitiesNum + i ) & (MAX_PARSE_ENTITIES-1) ];
	}

	// FIXME: configstring changes and server commands!!!

	return qtrue;
}

/*
=====================
CL_SetUserCmdValue
=====================
*/
void CL_SetUserCmdValue( int userCmdValue, float sensitivityScale ) {
	cl.cgameUserCmdValue = userCmdValue;
	cl.cgameSensitivity = sensitivityScale;
}

/*
=====================
CL_AddCgameCommand
=====================
*/
void CL_AddCgameCommand( const char *cmdName ) {
	Cmd_AddCommand( cmdName, NULL );
}

/*
=====================
CL_CgameError
=====================
*/
void CL_CgameError( const char *string ) {
	Com_Error( ERR_DROP, "%s", string );
}


/*
=====================
CL_ConfigstringModified
=====================
*/
void CL_ConfigstringModified( void ) {
	char		*old, *s;
	int			i, index;
	char		*dup;
	gameState_t	oldGs;
	int			len;

	index = atoi( Cmd_Argv(1) );
	if ( index < 0 || index >= MAX_CONFIGSTRINGS ) {
		Com_Error( ERR_DROP, "configstring > MAX_CONFIGSTRINGS" );
	}
	// get everything after "cs <num>"
	s = Cmd_ArgsFrom(2);

	old = cl.gameState.stringData + cl.gameState.stringOffsets[ index ];
	if ( !strcmp( old, s ) ) {
		return;		// unchanged
	}

	// build the new gameState_t
	oldGs = cl.gameState;

	Com_Memset( &cl.gameState, 0, sizeof( cl.gameState ) );

	// leave the first 0 for uninitialized strings
	cl.gameState.dataCount = 1;
		
	for ( i = 0 ; i < MAX_CONFIGSTRINGS ; i++ ) {
		if ( i == index ) {
			dup = s;
		} else {
			dup = oldGs.stringData + oldGs.stringOffsets[ i ];
		}
		if ( !dup[0] ) {
			continue;		// leave with the default empty string
		}

		len = strlen( dup );

		if ( len + 1 + cl.gameState.dataCount > MAX_GAMESTATE_CHARS ) {
			Com_Error( ERR_DROP, "MAX_GAMESTATE_CHARS exceeded" );
		}

		// append it to the gameState string buffer
		cl.gameState.stringOffsets[ i ] = cl.gameState.dataCount;
		Com_Memcpy( cl.gameState.stringData + cl.gameState.dataCount, dup, len + 1 );
		cl.gameState.dataCount += len + 1;
	}

	if ( index == CS_SYSTEMINFO ) {
		// parse serverId and other cvars
		CL_SystemInfoChanged();
	}

}


/*
===================
CL_GetServerCommand

Set up argc/argv for the given command
===================
*/
qboolean CL_GetServerCommand( int serverCommandNumber ) {
	char	*s;
	char	*cmd;
	static char bigConfigString[BIG_INFO_STRING];
	int argc;

	// if we have irretrievably lost a reliable command, drop the connection
	if ( serverCommandNumber <= clc.serverCommandSequence - MAX_RELIABLE_COMMANDS ) {
		// when a demo record was started after the client got a whole bunch of
		// reliable commands then the client never got those first reliable commands
		if ( clc.demoplaying )
			return qfalse;
		Com_Error( ERR_DROP, "CL_GetServerCommand: a reliable command was cycled out" );
		return qfalse;
	}

	if ( serverCommandNumber > clc.serverCommandSequence ) {
		Com_Error( ERR_DROP, "CL_GetServerCommand: requested a command not received" );
		return qfalse;
	}

	s = clc.serverCommands[ serverCommandNumber & ( MAX_RELIABLE_COMMANDS - 1 ) ];
	clc.lastExecutedServerCommand = serverCommandNumber;

	Com_DPrintf( "serverCommand: %i : %s\n", serverCommandNumber, s );

rescan:
	Cmd_TokenizeString( s );
	cmd = Cmd_Argv(0);
	argc = Cmd_Argc();
	
	if ( ( !strcmp( cmd, "chat" ) || !strcmp( cmd, "print" ) ) ) {
		const char *filterText;

		filterText = Cmd_Argv( 1 );
		if ( !strcmp( cmd, "chat" ) && argc > 2 ) {
			filterText = Cmd_Argv( 2 );
		}

		if ( CL_ShouldFilterConsoleText( filterText ) ) {
			return qfalse;
		}
	}

	if ( !strcmp( cmd, "disconnect" ) ) {
		// https://zerowing.idsoftware.com/bugzilla/show_bug.cgi?id=552
		// allow server to indicate why they were disconnected
		if ( argc >= 2 )
			Com_Error (ERR_SERVERDISCONNECT, va( "Server Disconnected - %s", Cmd_Argv( 1 ) ) );
		else
			Com_Error (ERR_SERVERDISCONNECT,"Server disconnected\n");
	}

	if ( !strcmp( cmd, "bcs0" ) ) {
		Com_sprintf( bigConfigString, BIG_INFO_STRING, "cs %s \"%s", Cmd_Argv(1), Cmd_Argv(2) );
		return qfalse;
	}

	if ( !strcmp( cmd, "bcs1" ) ) {
		s = Cmd_Argv(2);
		if( strlen(bigConfigString) + strlen(s) >= BIG_INFO_STRING ) {
			Com_Error( ERR_DROP, "bcs exceeded BIG_INFO_STRING" );
		}
		strcat( bigConfigString, s );
		return qfalse;
	}

	if ( !strcmp( cmd, "bcs2" ) ) {
		s = Cmd_Argv(2);
		if( strlen(bigConfigString) + strlen(s) + 1 >= BIG_INFO_STRING ) {
			Com_Error( ERR_DROP, "bcs exceeded BIG_INFO_STRING" );
		}
		strcat( bigConfigString, s );
		strcat( bigConfigString, "\"" );
		s = bigConfigString;
		goto rescan;
	}

	if ( !strcmp( cmd, "cs" ) ) {
		CL_ConfigstringModified();
		// reparse the string, because CL_ConfigstringModified may have done another Cmd_TokenizeString()
		Cmd_TokenizeString( s );
		return qtrue;
	}

	if ( !strcmp( cmd, "map_restart" ) ) {
		// clear notify lines and outgoing commands before passing
		// the restart to the cgame
		Con_ClearNotify();
		Com_Memset( cl.cmds, 0, sizeof( cl.cmds ) );
		return qtrue;
	}

	// the clientLevelShot command is used during development
	// to generate 128*128 screenshots from the intermission
	// point of levels for the menu system to use
	// we pass it along to the cgame to make apropriate adjustments,
	// but we also clear the console and notify lines here
	if ( !strcmp( cmd, "clientLevelShot" ) ) {
		// don't do it if we aren't running the server locally,
		// otherwise malicious remote servers could overwrite
		// the existing thumbnails
		if ( !com_sv_running->integer ) {
			return qfalse;
		}
		// close the console
		Con_Close();
		// take a special screenshot next frame
		Cbuf_AddText( "wait ; wait ; wait ; wait ; screenshot levelshot\n" );
		return qtrue;
	}

	// we may want to put a "connect to other server" command here

	// cgame can now act on the command
	return qtrue;
}


/*
====================
CL_CM_LoadMap

Just adds default parameters that cgame doesn't need to know about
====================
*/
void CL_CM_LoadMap( const char *mapname ) {
	int		checksum;

	CM_LoadMap( mapname, qtrue, &checksum );
}

/*
====================
CL_ShutdonwCGame

====================
*/
void CL_ShutdownCGame( void ) {
	cls.keyCatchers &= ~KEYCATCH_CGAME;
	cls.cgameStarted = qfalse;
	if ( !cgvm ) {
		return;
	}
	VM_Call( cgvm, CG_SHUTDOWN );
	VM_Free( cgvm );
	cgvm = NULL;
}

static int	FloatAsInt( float f ) {
	int		temp;

	*(float *)&temp = f;

	return temp;
}

/*
====================
CL_CgameSystemCallsImpl

Implements the cgame trap surface for both legacy syscall dispatch and the
native import-table bridge.
====================
*/
#define	VMA(x) VM_ArgPtr(args[x])
#define	VMF(x)	((float *)args)[x]
static int CL_CgameSystemCallsImpl( int *args, qboolean logContract ) {
	if ( logContract ) {
		SyscallContract_LogEvent( "shim-cgame", "cgame", args, SYSCALL_CONTRACT_MAX_ARGS );
	}

	switch( args[0] ) {
	case CG_PRINT:
		Com_Printf( "%s", VMA(1) );
		return 0;
	case CG_ERROR:
		Com_Error( ERR_DROP, "%s", VMA(1) );
		return 0;
	case CG_MILLISECONDS:
		return Sys_Milliseconds();
	case CG_CVAR_REGISTER:
		Cvar_Register( VMA(1), VMA(2), VMA(3), args[4] ); 
		return 0;
	case CG_CVAR_UPDATE:
		Cvar_Update( VMA(1) );
		return 0;
	case CG_CVAR_SET:
		Cvar_Set( VMA(1), VMA(2) );
		return 0;
	case CG_CVAR_VARIABLESTRINGBUFFER:
		Cvar_VariableStringBuffer( VMA(1), VMA(2), args[3] );
		return 0;
	case CG_ARGC:
		return Cmd_Argc();
	case CG_ARGV:
		Cmd_ArgvBuffer( args[1], VMA(2), args[3] );
		return 0;
	case CG_ARGS:
		Cmd_ArgsBuffer( VMA(1), args[2] );
		return 0;
	case CG_CMD_EXECUTETEXT:
		Cbuf_ExecuteText( args[1], VMA(2) );
		return 0;
	case CG_FS_FOPENFILE:
		return qlr_fs_imports.fopen_file_by_mode( VMA(1), VMA(2), args[3] );
	case CG_FS_READ:
		qlr_fs_imports.read( VMA(1), args[2], args[3] );
		return 0;
	case CG_FS_WRITE:
		qlr_fs_imports.write( VMA(1), args[2], args[3] );
		return 0;
	case CG_FS_FCLOSEFILE:
		qlr_fs_imports.fclose_file( args[1] );
		return 0;
	case CG_FS_SEEK:
		return qlr_fs_imports.seek( args[1], args[2], args[3] );
	case CG_SENDCONSOLECOMMAND:
		Cbuf_AddText( VMA(1) );
		return 0;
	case CG_ADDCOMMAND:
		CL_AddCgameCommand( VMA(1) );
		return 0;
	case CG_REMOVECOMMAND:
		Cmd_RemoveCommand( VMA(1) );
		return 0;
	case CG_SENDCLIENTCOMMAND:
		CL_AddReliableCommand( VMA(1) );
		return 0;
	case CG_UPDATESCREEN:
		// this is used during lengthy level loading, so pump message loop
//		Com_EventLoop();	// FIXME: if a server restarts here, BAD THINGS HAPPEN!
// We can't call Com_EventLoop here, a restart will crash and this _does_ happen
// if there is a map change while we are downloading at pk3.
// ZOID
		SCR_UpdateScreen();
		return 0;
	case CG_CM_LOADMAP:
		CL_CM_LoadMap( VMA(1) );
		return 0;
	case CG_CM_NUMINLINEMODELS:
		return CM_NumInlineModels();
	case CG_CM_INLINEMODEL:
		return CM_InlineModel( args[1] );
	case CG_CM_LOADMODEL:
		return 0;
	case CG_CM_TEMPBOXMODEL:
		return CM_TempBoxModel( VMA(1), VMA(2), /*int capsule*/ qfalse );
	case CG_CM_TEMPCAPSULEMODEL:
		return CM_TempBoxModel( VMA(1), VMA(2), /*int capsule*/ qtrue );
	case CG_CM_POINTCONTENTS:
		return CM_PointContents( VMA(1), args[2] );
	case CG_CM_TRANSFORMEDPOINTCONTENTS:
		return CM_TransformedPointContents( VMA(1), args[2], VMA(3), VMA(4) );
	case CG_CM_BOXTRACE:
		CM_BoxTrace( VMA(1), VMA(2), VMA(3), VMA(4), VMA(5), args[6], args[7], /*int capsule*/ qfalse );
		return 0;
	case CG_CM_CAPSULETRACE:
		CM_BoxTrace( VMA(1), VMA(2), VMA(3), VMA(4), VMA(5), args[6], args[7], /*int capsule*/ qtrue );
		return 0;
	case CG_CM_TRANSFORMEDBOXTRACE:
		CM_TransformedBoxTrace( VMA(1), VMA(2), VMA(3), VMA(4), VMA(5), args[6], args[7], VMA(8), VMA(9), /*int capsule*/ qfalse );
		return 0;
	case CG_CM_TRANSFORMEDCAPSULETRACE:
		CM_TransformedBoxTrace( VMA(1), VMA(2), VMA(3), VMA(4), VMA(5), args[6], args[7], VMA(8), VMA(9), /*int capsule*/ qtrue );
		return 0;
	case CG_CM_MARKFRAGMENTS:
		return re.MarkFragments( args[1], VMA(2), VMA(3), args[4], VMA(5), args[6], VMA(7) );
	case CG_S_STARTSOUND:
		S_StartSound( VMA(1), args[2], args[3], args[4] );
		return 0;
	case CG_S_STARTLOCALSOUND:
		S_StartLocalSound( args[1], args[2] );
		return 0;
	case CG_S_CLEARLOOPINGSOUNDS:
		S_ClearLoopingSounds( args[1] ? qtrue : qfalse );
		return 0;
	case CG_S_ADDLOOPINGSOUND:
		S_AddLoopingSound( args[1], VMA(2), VMA(3), args[4] );
		return 0;
	case CG_S_ADDREALLOOPINGSOUND:
		S_AddRealLoopingSound( args[1], VMA(2), VMA(3), args[4] );
		return 0;
	case CG_S_STOPLOOPINGSOUND:
		S_StopLoopingSound( args[1] );
		return 0;
	case CG_S_UPDATEENTITYPOSITION:
		S_UpdateEntityPosition( args[1], VMA(2) );
		return 0;
	case CG_S_RESPATIALIZE:
		S_Respatialize( args[1], VMA(2), VMA(3), args[4] );
		return 0;
	case CG_S_REGISTERSOUND:
		return S_RegisterSound( VMA(1), args[2] ? qtrue : qfalse );
	case CG_S_STARTBACKGROUNDTRACK:
		S_StartBackgroundTrack( VMA(1), VMA(2) );
		return 0;
	case CG_R_LOADWORLDMAP:
		re.LoadWorld( VMA(1) );
		return 0; 
	case CG_R_REGISTERMODEL:
		return re.RegisterModel( VMA(1) );
	case CG_R_REGISTERSKIN:
		return re.RegisterSkin( VMA(1) );
	case CG_R_REGISTERSHADER:
		return re.RegisterShader( VMA(1) );
	case CG_R_REGISTERSHADERNOMIP:
		return re.RegisterShaderNoMip( VMA(1) );
	case CG_R_REGISTERFONT:
		CL_RegisterFont( VMA(1), args[2], VMA(3) );
	case CG_R_CLEARSCENE:
		re.ClearScene();
		return 0;
	case CG_R_ADDREFENTITYTOSCENE:
		re.AddRefEntityToScene( VMA(1) );
		return 0;
	case CG_R_ADDPOLYTOSCENE:
		re.AddPolyToScene( args[1], args[2], VMA(3), 1 );
		return 0;
	case CG_R_ADDPOLYSTOSCENE:
		re.AddPolyToScene( args[1], args[2], VMA(3), args[4] );
		return 0;
	case CG_R_LIGHTFORPOINT:
		return re.LightForPoint( VMA(1), VMA(2), VMA(3), VMA(4) );
	case CG_R_ADDLIGHTTOSCENE:
		re.AddLightToScene( VMA(1), VMF(2), VMF(3), VMF(4), VMF(5) );
		return 0;
	case CG_R_ADDADDITIVELIGHTTOSCENE:
		re.AddAdditiveLightToScene( VMA(1), VMF(2), VMF(3), VMF(4), VMF(5) );
		return 0;
	case CG_R_RENDERSCENE:
		re.RenderScene( VMA(1) );
		return 0;
	case CG_R_SETCOLOR:
		re.SetColor( VMA(1) );
		return 0;
	case CG_R_DRAWSTRETCHPIC:
		re.DrawStretchPic( VMF(1), VMF(2), VMF(3), VMF(4), VMF(5), VMF(6), VMF(7), VMF(8), args[9] );
		return 0;
	case CG_R_MODELBOUNDS:
		re.ModelBounds( args[1], VMA(2), VMA(3) );
		return 0;
	case CG_R_LERPTAG:
		return re.LerpTag( VMA(1), args[2], args[3], args[4], VMF(5), VMA(6) );
	case CG_GETGLCONFIG:
		CL_GetGlconfig( VMA(1) );
		return 0;
	case CG_GETGAMESTATE:
		CL_GetGameState( VMA(1) );
		return 0;
	case CG_GETCURRENTSNAPSHOTNUMBER:
		CL_GetCurrentSnapshotNumber( VMA(1), VMA(2) );
		return 0;
	case CG_GETSNAPSHOT:
		return CL_GetSnapshot( args[1], VMA(2) ) ? qtrue : qfalse;
	case CG_GETSERVERCOMMAND:
		return CL_GetServerCommand( args[1] ) ? qtrue : qfalse;
	case CG_GETCURRENTCMDNUMBER:
		return CL_GetCurrentCmdNumber();
	case CG_GETUSERCMD:
		return CL_GetUserCmd( args[1], VMA(2) ) ? qtrue : qfalse;
	case CG_SETUSERCMDVALUE:
		CL_SetUserCmdValue( args[1], VMF(2) );
		return 0;
	case CG_MEMORY_REMAINING:
		return Hunk_MemoryRemaining();
  case CG_KEY_ISDOWN:
		return Key_IsDown( args[1] ) ? qtrue : qfalse;
  case CG_KEY_GETCATCHER:
		return Key_GetCatcher();
  case CG_KEY_SETCATCHER:
		Key_SetCatcher( args[1] );
    return 0;
  case CG_KEY_GETKEY:
		return Key_GetKey( VMA(1) );

	case CG_KEY_KEYNUMTOSTRINGBUF:
		Q_strncpyz( VMA(2), Key_KeynumToString( args[1] ), args[3] );
		return 0;
	case CG_KEY_GETBINDINGBUF:
		Q_strncpyz( VMA(2), Key_GetBinding( args[1] ), args[3] );
		return 0;
	case CG_KEY_SETBINDING:
		Key_SetBinding( args[1], VMA(2) );
		return 0;
	case CG_KEY_GETOVERSTRIKEMODE:
		return Key_GetOverstrikeMode() ? qtrue : qfalse;
	case CG_KEY_SETOVERSTRIKEMODE:
		Key_SetOverstrikeMode( args[1] ? qtrue : qfalse );
		return 0;
	case CG_ADVERTISEMENTBRIDGE_INITCGAME:
		CL_AdvertisementBridge_InitCGame();
		return 0;
	case CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME:
		CL_AdvertisementBridge_ShutdownCGame();
		return 0;
	case CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS:
		CL_AdvertisementBridge_UpdateLoadingViewParameters();
		return 0;
	case CG_ADVERTISEMENTBRIDGE_SETFRAMETIME:
		CL_AdvertisementBridge_SetFrameTime( args[1] );
		return 0;


	case CG_MEMSET:
		Com_Memset( VMA(1), args[2], args[3] );
		return 0;
	case CG_MEMCPY:
		Com_Memcpy( VMA(1), VMA(2), args[3] );
		return 0;
	case CG_STRNCPY:
		return (int)strncpy( VMA(1), VMA(2), args[3] );
	case CG_SIN:
		return FloatAsInt( sin( VMF(1) ) );
	case CG_COS:
		return FloatAsInt( cos( VMF(1) ) );
	case CG_ATAN2:
		return FloatAsInt( atan2( VMF(1), VMF(2) ) );
	case CG_SQRT:
		return FloatAsInt( sqrt( VMF(1) ) );
	case CG_FLOOR:
		return FloatAsInt( floor( VMF(1) ) );
	case CG_CEIL:
		return FloatAsInt( ceil( VMF(1) ) );
	case CG_ACOS:
		return FloatAsInt( Q_acos( VMF(1) ) );

	case CG_PC_ADD_GLOBAL_DEFINE:
		return botlib_export->PC_AddGlobalDefine( VMA(1) );
	case CG_PC_LOAD_SOURCE:
		return botlib_export->PC_LoadSourceHandle( VMA(1) );
	case CG_PC_FREE_SOURCE:
		return botlib_export->PC_FreeSourceHandle( args[1] );
	case CG_PC_READ_TOKEN:
		return botlib_export->PC_ReadTokenHandle( args[1], VMA(2) );
	case CG_PC_SOURCE_FILE_AND_LINE:
		return botlib_export->PC_SourceFileAndLine( args[1], VMA(2), VMA(3) );

	case CG_S_STOPBACKGROUNDTRACK:
		S_StopBackgroundTrack();
		return 0;

	case CG_REAL_TIME:
		return Com_RealTime( VMA(1) );
	case CG_SNAPVECTOR:
		Sys_SnapVector( VMA(1) );
		return 0;

	case CG_CIN_PLAYCINEMATIC:
	  return CIN_PlayCinematic(VMA(1), args[2], args[3], args[4], args[5], args[6]);

	case CG_CIN_STOPCINEMATIC:
	  return CIN_StopCinematic(args[1]);

	case CG_CIN_RUNCINEMATIC:
	  return CIN_RunCinematic(args[1]);

	case CG_CIN_DRAWCINEMATIC:
	  CIN_DrawCinematic(args[1]);
	  return 0;

	case CG_CIN_SETEXTENTS:
	  CIN_SetExtents(args[1], args[2], args[3], args[4], args[5]);
	  return 0;

	case CG_R_REMAP_SHADER:
		re.RemapShader( VMA(1), VMA(2), VMA(3) );
		return 0;

/*
	case CG_LOADCAMERA:
		return loadCamera(VMA(1));

	case CG_STARTCAMERA:
		startCamera(args[1]);
		return 0;

	case CG_GETCAMERAINFO:
		return getCameraInfo(args[1], VMA(2), VMA(3));
*/
	case CG_GET_ENTITY_TOKEN:
		return re.GetEntityToken( VMA(1), args[2] ) ? qtrue : qfalse;
	case CG_R_INPVS:
		return re.inPVS( VMA(1), VMA(2) ) ? qtrue : qfalse;

	default:
	        assert(0); // bk010102
		Com_Error( ERR_DROP, "Bad cgame system trap: %i", args[0] );
	}
	return 0;
}

/*
====================
CL_CgameSystemCalls
====================
*/
int CL_CgameSystemCalls( int *args ) {
	/*
	case CG_CMD_EXECUTETEXT:
		Cbuf_ExecuteText( args[1], VMA(2) );
	case CG_KEY_GETBINDINGBUF:
		Q_strncpyz( VMA(2), Key_GetBinding( args[1] ), args[3] );
	case CG_KEY_SETBINDING:
		Key_SetBinding( args[1], VMA(2) );
	case CG_KEY_GETOVERSTRIKEMODE:
		return Key_GetOverstrikeMode();
	case CG_KEY_SETOVERSTRIKEMODE:
		Key_SetOverstrikeMode( args[1] );
	case CG_ADVERTISEMENTBRIDGE_INITCGAME:
		CL_AdvertisementBridge_InitCGame();
	case CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME:
		CL_AdvertisementBridge_ShutdownCGame();
	case CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS:
		CL_AdvertisementBridge_UpdateLoadingViewParameters();
	case CG_ADVERTISEMENTBRIDGE_SETFRAMETIME:
		CL_AdvertisementBridge_SetFrameTime( args[1] );
	*/
	return CL_CgameSystemCallsImpl( args, qtrue );
}

/*
====================
CG_Import_Syscall
====================
*/
static int QDECL CG_Import_Syscall( int arg, ... ) {
	int args[SYSCALL_CONTRACT_MAX_ARGS];
	int i;
	va_list ap;

	args[0] = arg;

	va_start(ap, arg);
	for (i = 1; i < SYSCALL_CONTRACT_MAX_ARGS; i++) {
		args[i] = va_arg(ap, int);
	}
	va_end(ap);

	return CL_CgameSystemCallsImpl( args, qfalse );
}

#include "ql_cgame_imports.inc"

typedef void (QDECL *ql_import_f)( void );

typedef enum {
	QL_CG_SCALED_FONT_NORMAL = 0,
	QL_CG_SCALED_FONT_SANS,
	QL_CG_SCALED_FONT_MONO,
	QL_CG_SCALED_FONT_SANS_FALLBACK,
	QL_CG_SCALED_FONT_SANS_WINDOWS_FALLBACK,
	QL_CG_SCALED_FONT_COUNT
} qlCgScaledFontHandle_t;

typedef struct {
	fontInfo_t	font;
	qboolean	loaded;
} qlCgScaledFont_t;

static void QDECL QL_CG_trap_Key_GetBindingBuf( int keynum, char *buf, int buflen );
static void QDECL QL_CG_trap_Key_SetBinding( int keynum, const char *binding );
static qboolean QDECL QL_CG_trap_Key_GetOverstrikeMode( void );
static void QDECL QL_CG_trap_Key_SetOverstrikeMode( qboolean state );
static void QDECL QL_CG_trap_Cmd_ExecuteText( int exec_when, const char *text );
static void QDECL QL_CG_trap_AdvertisementBridge_InitCGame( void );
static void QDECL QL_CG_trap_AdvertisementBridge_ShutdownCGame( void );
static void QDECL QL_CG_trap_AdvertisementBridge_UpdateLoadingViewParameters( void );
static void QDECL QL_CG_trap_AdvertisementBridge_SetFrameTime( int frameTime );

static vec4_t ql_cgame_currentColor = { 1.0f, 1.0f, 1.0f, 1.0f };
static qlCgScaledFont_t ql_cgame_scaledFonts[QL_CG_SCALED_FONT_COUNT];
static uint64_t ql_cgame_mutedIdentitySet[MAX_CLIENTS];
static int ql_cgame_mutedIdentityCount = 0;
static ql_import_f ql_cgame_imports[CGAME_NATIVE_IMPORT_COUNT] = {
	[CG_KEY_GETBINDINGBUF] = (ql_import_f)QL_CG_trap_Key_GetBindingBuf,
	[CG_KEY_SETBINDING] = (ql_import_f)QL_CG_trap_Key_SetBinding,
	[CG_KEY_GETOVERSTRIKEMODE] = (ql_import_f)QL_CG_trap_Key_GetOverstrikeMode,
	[CG_KEY_SETOVERSTRIKEMODE] = (ql_import_f)QL_CG_trap_Key_SetOverstrikeMode,
	[CG_CMD_EXECUTETEXT] = (ql_import_f)QL_CG_trap_Cmd_ExecuteText,
	[CG_ADVERTISEMENTBRIDGE_INITCGAME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_InitCGame,
	[CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_ShutdownCGame,
	[CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS] = (ql_import_f)QL_CG_trap_AdvertisementBridge_UpdateLoadingViewParameters,
	[CG_ADVERTISEMENTBRIDGE_SETFRAMETIME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_SetFrameTime,
};

/*
==============
QL_CG_PackFloatBits64
==============
*/
static unsigned long long QL_CG_PackFloatBits64( float lo, float hi ) {
	union {
		unsigned long long value;
		struct {
			float lo;
			float hi;
		} parts;
	} packed;

	packed.parts.lo = lo;
	packed.parts.hi = hi;
	return packed.value;
}

/*
==============
QL_CG_NormalizeScaledFontHandle
==============
*/
static int QL_CG_NormalizeScaledFontHandle( int fontHandle ) {
	if ( fontHandle < QL_CG_SCALED_FONT_NORMAL || fontHandle >= QL_CG_SCALED_FONT_COUNT ) {
		return QL_CG_SCALED_FONT_NORMAL;
	}

	return fontHandle;
}

/*
==============
QL_CG_ResolveWindowsFallbackFontPath
==============
*/
static const char *QL_CG_ResolveWindowsFallbackFontPath( char *fontPath, int fontPathSize ) {
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
QL_CG_GetScaledFontName
==============
*/
static const char *QL_CG_GetScaledFontName( int fontHandle, char *resolvedFontPath, int resolvedFontPathSize ) {
	switch ( QL_CG_NormalizeScaledFontHandle( fontHandle ) ) {
		case QL_CG_SCALED_FONT_SANS:
			return "fonts/notosans-regular.ttf";

		case QL_CG_SCALED_FONT_MONO:
			return "fonts/droidsansmono.ttf";

		case QL_CG_SCALED_FONT_SANS_FALLBACK:
			return "fonts/droidsansfallbackfull.ttf";

		case QL_CG_SCALED_FONT_SANS_WINDOWS_FALLBACK:
			return QL_CG_ResolveWindowsFallbackFontPath( resolvedFontPath, resolvedFontPathSize );

		case QL_CG_SCALED_FONT_NORMAL:
		default:
			return "fonts/handelgothic.ttf";
	}
}

/*
==============
QL_CG_GetScaledFont
==============
*/
static fontInfo_t *QL_CG_GetScaledFont( int fontHandle ) {
	qlCgScaledFont_t *scaledFont;
	char resolvedFontPath[MAX_OSPATH];
	const char *fontName;

	fontHandle = QL_CG_NormalizeScaledFontHandle( fontHandle );
	scaledFont = &ql_cgame_scaledFonts[fontHandle];
	if ( !scaledFont->loaded ) {
		fontName = QL_CG_GetScaledFontName( fontHandle, resolvedFontPath, sizeof( resolvedFontPath ) );
		CL_RegisterFont( fontName, 48, &scaledFont->font );
		scaledFont->loaded = qtrue;
	}

	return &scaledFont->font;
}

/*
==============
QL_CG_DrawGlyph
==============
*/
static void QL_CG_DrawGlyph( float x, float y, float scaleFactor, glyphInfo_t *glyph ) {
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
QL_CG_RegisterDefaultAdvertCellShader
==============
*/
static qhandle_t QL_CG_RegisterDefaultAdvertCellShader( const char *defaultContent ) {
	if ( !defaultContent || !defaultContent[0] ) {
		return 0;
	}

	return CL_Steam_RegisterShader( defaultContent );
}

/*
==============
QL_CG_CombineIdentityWords
==============
*/
static uint64_t QL_CG_CombineIdentityWords( unsigned int identityLow, unsigned int identityHigh ) {
	return ( (uint64_t)identityHigh << 32 ) | (uint64_t)identityLow;
}

/*
==============
QL_CG_FindMutedIdentityIndex
==============
*/
static int QL_CG_FindMutedIdentityIndex( uint64_t identity ) {
	int i;

	for ( i = 0; i < ql_cgame_mutedIdentityCount; ++i ) {
		if ( ql_cgame_mutedIdentitySet[i] == identity ) {
			return i;
		}
	}

	return -1;
}

/*
==============
QL_CG_trap_Cvar_RegisterRange
==============
*/
static void QDECL QL_CG_trap_Cvar_RegisterRange( vmCvar_t *vmCvar, const char *varName, const char *defaultValue, float minimumValue, float maximumValue, int flags ) {
	(void)minimumValue;
	(void)maximumValue;
	Cvar_Register( vmCvar, varName, defaultValue, flags );
}

/*
==============
QL_CG_trap_Cvar_Reset
==============
*/
static void QDECL QL_CG_trap_Cvar_Reset( const char *varName ) {
	Cvar_Reset( varName );
}

/*
==============
QL_CG_trap_FS_GetFileList
==============
*/
static int QDECL QL_CG_trap_FS_GetFileList( const char *path, const char *extension, char *listbuf, int bufsize ) {
	return qlr_fs_imports.get_file_list( path, extension, listbuf, bufsize );
}

/*
==============
QL_CG_trap_S_StartSoundVolume
==============
*/
static void QDECL QL_CG_trap_S_StartSoundVolume( vec3_t origin, int entityNum, int entchannel, sfxHandle_t sfx, float volume ) {
	(void)volume;
	S_StartSound( origin, entityNum, entchannel, sfx );
}

/*
==============
QL_CG_trap_S_StartLocalSoundVolume
==============
*/
static void QDECL QL_CG_trap_S_StartLocalSoundVolume( sfxHandle_t sfx, int channelNum, float volume ) {
	(void)volume;
	S_StartLocalSound( sfx, channelNum );
}

/*
==============
QL_CG_trap_S_ClearLoopingSoundsFrame
==============
*/
static void QDECL QL_CG_trap_S_ClearLoopingSoundsFrame( void ) {
	S_ClearLoopingSounds( qfalse );
}

/*
==============
QL_CG_trap_S_ClearLoopingSoundsKillAll
==============
*/
static void QDECL QL_CG_trap_S_ClearLoopingSoundsKillAll( void ) {
	S_ClearLoopingSounds( qtrue );
}

/*
==============
QL_CG_trap_SetupAdvertCellShader
==============
*/
static qhandle_t QDECL QL_CG_trap_SetupAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {
	(void)rect;
	(void)cellId;
	return QL_CG_RegisterDefaultAdvertCellShader( defaultContent );
}

/*
==============
QL_CG_trap_RefreshAdvertCellShader
==============
*/
static qhandle_t QDECL QL_CG_trap_RefreshAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {
	(void)rect;
	(void)cellId;
	return QL_CG_RegisterDefaultAdvertCellShader( defaultContent );
}

/*
==============
QL_CG_trap_SetActiveAdvert
==============
*/
static void QDECL QL_CG_trap_SetActiveAdvert( int cellId ) {
	CL_AdvertisementBridge_SetActiveAdvert( cellId );
}

/*
==============
QL_CG_trap_UpdateAdvert
==============
*/
static void QDECL QL_CG_trap_UpdateAdvert( int handleOrToken, int area ) {
	// cgamex86.dll HLIL: import[58] is called by the retail advert ownerdraw after the shader quad draw.
	// The recovered host-side provider remains inert here as well, so preserve the callback surface without inventing behavior.
	(void)handleOrToken;
	(void)area;
}

/*
==============
QL_CG_trap_AdvertisementBridge_SetMapPath
==============
*/
static void QDECL QL_CG_trap_AdvertisementBridge_SetMapPath( const char *mapPath ) {
	(void)mapPath;
	CL_RefreshOnlineServicesBridgeState();
}

/*
==============
QL_CG_trap_AdvertisementBridge_UpdateViewParameters
==============
*/
static void QDECL QL_CG_trap_AdvertisementBridge_UpdateViewParameters( void ) {
	CL_RefreshOnlineServicesBridgeState();
}

/*
==============
QL_CG_trap_AdvertisementBridge_ClearDelay
==============
*/
static void QDECL QL_CG_trap_AdvertisementBridge_ClearDelay( void ) {
}

/*
==============
QL_CG_trap_R_SetColor_QL
==============
*/
static void QDECL QL_CG_trap_R_SetColor_QL( const float *rgba ) {
	if ( rgba ) {
		ql_cgame_currentColor[0] = rgba[0];
		ql_cgame_currentColor[1] = rgba[1];
		ql_cgame_currentColor[2] = rgba[2];
		ql_cgame_currentColor[3] = rgba[3];
	} else {
		ql_cgame_currentColor[0] = 1.0f;
		ql_cgame_currentColor[1] = 1.0f;
		ql_cgame_currentColor[2] = 1.0f;
		ql_cgame_currentColor[3] = 1.0f;
	}

	re.SetColor( rgba );
}

/*
==============
QL_CG_trap_TaggedCvarStringBuffer
==============
*/
static void QDECL QL_CG_trap_TaggedCvarStringBuffer( const char *varName, char *buffer ) {
	if ( !buffer ) {
		return;
	}

	Cvar_VariableStringBuffer( varName, buffer, BIG_INFO_STRING );
}

/*
==============
QL_CG_trap_R_MirrorPoint
==============
*/
static void QDECL QL_CG_trap_R_MirrorPoint( vec3_t in, orientation_t *surface, orientation_t *camera, vec3_t out ) {
	R_MirrorPoint( in, surface, camera, out );
}

/*
==============
QL_CG_trap_R_MirrorVector
==============
*/
static void QDECL QL_CG_trap_R_MirrorVector( vec3_t in, orientation_t *surface, orientation_t *camera, vec3_t out ) {
	R_MirrorVector( in, surface, camera, out );
}

/*
==============
QL_CG_trap_DrawScaledText
==============
*/
static void QDECL QL_CG_trap_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, int forceColor ) {
	fontInfo_t *font;
	const char *s;
	vec4_t baseColor;
	float drawX;
	float scaleFactor;
	qboolean hasMaxX;
	float maxXf;

	if ( !text || !text[0] ) {
		if ( outMaxX ) {
			*outMaxX = (float)x;
		}
		return;
	}

	Com_Memcpy( baseColor, ql_cgame_currentColor, sizeof( baseColor ) );

	font = QL_CG_GetScaledFont( fontHandle );
	scaleFactor = ( scale <= 0.0f ) ? 1.0f : scale / 48.0f;
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

			QL_CG_DrawGlyph( drawX, (float)y - yadj, scaleFactor, glyph );
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
QL_CG_trap_MeasureText
==============
*/
static unsigned long long QDECL QL_CG_trap_MeasureText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outLeft ) {
	fontInfo_t *font;
	const char *s;
	float width;
	float height;
	float scaleFactor;
	qboolean hasMaxX;
	float maxXf;

	if ( outLeft ) {
		*outLeft = 0.0f;
	}

	if ( !text ) {
		return QL_CG_PackFloatBits64( 0.0f, 0.0f );
	}

	font = QL_CG_GetScaledFont( fontHandle );
	scaleFactor = ( scale <= 0.0f ) ? 1.0f : scale / 48.0f;
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

	return QL_CG_PackFloatBits64( width, height );
}

/*
==============
QL_CG_trap_IsClientMuted
==============
*/
static int QDECL QL_CG_trap_IsClientMuted( unsigned int identityLow, unsigned int identityHigh ) {
	uint64_t identity;

	identity = QL_CG_CombineIdentityWords( identityLow, identityHigh );
	if ( !identity ) {
		return 0;
	}

	return QL_CG_FindMutedIdentityIndex( identity ) >= 0;
}

/*
==============
QL_CG_trap_ToggleClientMute
==============
*/
static int QDECL QL_CG_trap_ToggleClientMute( unsigned int identityLow, unsigned int identityHigh ) {
	uint64_t identity;
	int index;

	identity = QL_CG_CombineIdentityWords( identityLow, identityHigh );
	if ( !identity ) {
		return 0;
	}

	index = QL_CG_FindMutedIdentityIndex( identity );
	if ( index >= 0 ) {
		--ql_cgame_mutedIdentityCount;
		ql_cgame_mutedIdentitySet[index] = ql_cgame_mutedIdentitySet[ql_cgame_mutedIdentityCount];
		return 0;
	}

	if ( ql_cgame_mutedIdentityCount >= ARRAY_LEN( ql_cgame_mutedIdentitySet ) ) {
		return 0;
	}

	ql_cgame_mutedIdentitySet[ql_cgame_mutedIdentityCount++] = identity;
	return 1;
}

/*
==============
QL_CG_trap_GetAvatarImageHandle
==============
*/
static qhandle_t QDECL QL_CG_trap_GetAvatarImageHandle( unsigned int identityLow, unsigned int identityHigh ) {
	uint64_t identity;
	char url[MAX_QPATH];

	if ( !CL_SteamServicesEnabled() ) {
		return 0;
	}

	identity = QL_CG_CombineIdentityWords( identityLow, identityHigh );
	if ( !identity ) {
		return 0;
	}

	Com_sprintf( url, sizeof( url ), "steam://avatar/large/%llu", (unsigned long long)identity );
	return CL_Steam_RegisterShader( url );
}

/*
==============
CL_InitCGameImports
==============
*/
static void CL_InitCGameImports( void ) {
	Com_Memset( ql_cgame_imports, 0, sizeof( ql_cgame_imports ) );

	ql_cgame_currentColor[0] = 1.0f;
	ql_cgame_currentColor[1] = 1.0f;
	ql_cgame_currentColor[2] = 1.0f;
	ql_cgame_currentColor[3] = 1.0f;

	ql_cgame_imports[CG_QL_IMPORT_PRINT] = (ql_import_f)QL_CG_trap_Print;
	ql_cgame_imports[CG_QL_IMPORT_ERROR] = (ql_import_f)QL_CG_trap_Error;
	ql_cgame_imports[CG_QL_IMPORT_MILLISECONDS] = (ql_import_f)QL_CG_trap_Milliseconds;
	ql_cgame_imports[CG_QL_IMPORT_REAL_TIME] = (ql_import_f)QL_CG_trap_RealTime;
	ql_cgame_imports[CG_QL_IMPORT_CVAR_REGISTER] = (ql_import_f)QL_CG_trap_Cvar_Register;
	ql_cgame_imports[CG_QL_IMPORT_CVAR_REGISTER_RANGE] = (ql_import_f)QL_CG_trap_Cvar_RegisterRange;
	ql_cgame_imports[CG_QL_IMPORT_CVAR_UPDATE] = (ql_import_f)QL_CG_trap_Cvar_Update;
	ql_cgame_imports[CG_QL_IMPORT_CVAR_SET] = (ql_import_f)QL_CG_trap_Cvar_Set;
	ql_cgame_imports[CG_QL_IMPORT_CVAR_VARIABLESTRINGBUFFER] = (ql_import_f)QL_CG_trap_Cvar_VariableStringBuffer;
	ql_cgame_imports[CG_QL_IMPORT_CVAR_RESET] = (ql_import_f)QL_CG_trap_Cvar_Reset;
	ql_cgame_imports[CG_QL_IMPORT_ARGC] = (ql_import_f)QL_CG_trap_Argc;
	ql_cgame_imports[CG_QL_IMPORT_ARGV] = (ql_import_f)QL_CG_trap_Argv;
	ql_cgame_imports[CG_QL_IMPORT_ARGS] = (ql_import_f)QL_CG_trap_Args;
	ql_cgame_imports[CG_QL_IMPORT_FS_FOPENFILE] = (ql_import_f)QL_CG_trap_FS_FOpenFile;
	ql_cgame_imports[CG_QL_IMPORT_FS_READ] = (ql_import_f)QL_CG_trap_FS_Read;
	ql_cgame_imports[CG_QL_IMPORT_FS_WRITE] = (ql_import_f)QL_CG_trap_FS_Write;
	ql_cgame_imports[CG_QL_IMPORT_FS_FCLOSEFILE] = (ql_import_f)QL_CG_trap_FS_FCloseFile;
	ql_cgame_imports[CG_QL_IMPORT_FS_SEEK] = (ql_import_f)QL_CG_trap_FS_Seek;
	ql_cgame_imports[CG_QL_IMPORT_FS_GETFILELIST] = (ql_import_f)QL_CG_trap_FS_GetFileList;
	ql_cgame_imports[CG_QL_IMPORT_SENDCONSOLECOMMAND] = (ql_import_f)QL_CG_trap_SendConsoleCommand;
	ql_cgame_imports[CG_QL_IMPORT_ADDCOMMAND] = (ql_import_f)QL_CG_trap_AddCommand;
	ql_cgame_imports[CG_QL_IMPORT_REMOVECOMMAND] = (ql_import_f)QL_CG_trap_RemoveCommand;
	ql_cgame_imports[CG_QL_IMPORT_SENDCLIENTCOMMAND] = (ql_import_f)QL_CG_trap_SendClientCommand;
	ql_cgame_imports[CG_QL_IMPORT_UPDATESCREEN] = (ql_import_f)QL_CG_trap_UpdateScreen;
	ql_cgame_imports[CG_QL_IMPORT_CM_LOADMAP] = (ql_import_f)QL_CG_trap_CM_LoadMap;
	ql_cgame_imports[CG_QL_IMPORT_CM_NUMINLINEMODELS] = (ql_import_f)QL_CG_trap_CM_NumInlineModels;
	ql_cgame_imports[CG_QL_IMPORT_CM_INLINEMODEL] = (ql_import_f)QL_CG_trap_CM_InlineModel;
	ql_cgame_imports[CG_QL_IMPORT_CM_TEMPBOXMODEL] = (ql_import_f)QL_CG_trap_CM_TempBoxModel;
	ql_cgame_imports[CG_QL_IMPORT_CM_TEMPCAPSULEMODEL] = (ql_import_f)QL_CG_trap_CM_TempCapsuleModel;
	ql_cgame_imports[CG_QL_IMPORT_CM_POINTCONTENTS] = (ql_import_f)QL_CG_trap_CM_PointContents;
	ql_cgame_imports[CG_QL_IMPORT_CM_TRANSFORMEDPOINTCONTENTS] = (ql_import_f)QL_CG_trap_CM_TransformedPointContents;
	ql_cgame_imports[CG_QL_IMPORT_CM_BOXTRACE] = (ql_import_f)QL_CG_trap_CM_BoxTrace;
	ql_cgame_imports[CG_QL_IMPORT_CM_CAPSULETRACE] = (ql_import_f)QL_CG_trap_CM_CapsuleTrace;
	ql_cgame_imports[CG_QL_IMPORT_CM_TRANSFORMEDBOXTRACE] = (ql_import_f)QL_CG_trap_CM_TransformedBoxTrace;
	ql_cgame_imports[CG_QL_IMPORT_CM_TRANSFORMEDCAPSULETRACE] = (ql_import_f)QL_CG_trap_CM_TransformedCapsuleTrace;
	ql_cgame_imports[CG_QL_IMPORT_CM_MARKFRAGMENTS] = (ql_import_f)QL_CG_trap_CM_MarkFragments;
	ql_cgame_imports[CG_QL_IMPORT_S_STARTSOUND] = (ql_import_f)QL_CG_trap_S_StartSound;
	ql_cgame_imports[CG_QL_IMPORT_S_STARTSOUND_VOLUME] = (ql_import_f)QL_CG_trap_S_StartSoundVolume;
	ql_cgame_imports[CG_QL_IMPORT_S_STARTLOCALSOUND] = (ql_import_f)QL_CG_trap_S_StartLocalSound;
	ql_cgame_imports[CG_QL_IMPORT_S_STARTLOCALSOUND_VOLUME] = (ql_import_f)QL_CG_trap_S_StartLocalSoundVolume;
	ql_cgame_imports[CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_FRAME] = (ql_import_f)QL_CG_trap_S_ClearLoopingSoundsFrame;
	ql_cgame_imports[CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_KILLALL] = (ql_import_f)QL_CG_trap_S_ClearLoopingSoundsKillAll;
	ql_cgame_imports[CG_QL_IMPORT_S_ADDLOOPINGSOUND] = (ql_import_f)QL_CG_trap_S_AddLoopingSound;
	ql_cgame_imports[CG_QL_IMPORT_S_UPDATEENTITYPOSITION] = (ql_import_f)QL_CG_trap_S_UpdateEntityPosition;
	ql_cgame_imports[CG_QL_IMPORT_S_RESPATIALIZE] = (ql_import_f)QL_CG_trap_S_Respatialize;
	ql_cgame_imports[CG_QL_IMPORT_S_REGISTERSOUND] = (ql_import_f)QL_CG_trap_S_RegisterSound;
	ql_cgame_imports[CG_QL_IMPORT_S_STARTBACKGROUNDTRACK] = (ql_import_f)QL_CG_trap_S_StartBackgroundTrack;
	ql_cgame_imports[CG_QL_IMPORT_S_STOPBACKGROUNDTRACK] = (ql_import_f)QL_CG_trap_S_StopBackgroundTrack;
	ql_cgame_imports[CG_QL_IMPORT_R_LOADWORLDMAP] = (ql_import_f)QL_CG_trap_R_LoadWorldMap;
	ql_cgame_imports[CG_QL_IMPORT_R_REGISTERMODEL] = (ql_import_f)QL_CG_trap_R_RegisterModel;
	ql_cgame_imports[CG_QL_IMPORT_R_REGISTERSKIN] = (ql_import_f)QL_CG_trap_R_RegisterSkin;
	ql_cgame_imports[CG_QL_IMPORT_R_REGISTERSHADER] = (ql_import_f)QL_CG_trap_R_RegisterShader;
	ql_cgame_imports[CG_QL_IMPORT_R_REGISTERSHADERNOMIP] = (ql_import_f)QL_CG_trap_R_RegisterShaderNoMip;
	ql_cgame_imports[CG_QL_IMPORT_SETUP_ADVERT_CELL_SHADER] = (ql_import_f)QL_CG_trap_SetupAdvertCellShader;
	ql_cgame_imports[CG_QL_IMPORT_REFRESH_ADVERT_CELL_SHADER] = (ql_import_f)QL_CG_trap_RefreshAdvertCellShader;
	ql_cgame_imports[CG_QL_IMPORT_SET_ACTIVE_ADVERT] = (ql_import_f)QL_CG_trap_SetActiveAdvert;
	ql_cgame_imports[CG_QL_IMPORT_UPDATE_ADVERT] = (ql_import_f)QL_CG_trap_UpdateAdvert;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_SET_MAP_PATH] = (ql_import_f)QL_CG_trap_AdvertisementBridge_SetMapPath;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_INITCGAME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_InitCGame;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_ShutdownCGame;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_UPDATE_VIEW_PARAMETERS] = (ql_import_f)QL_CG_trap_AdvertisementBridge_UpdateViewParameters;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_SETFRAMETIME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_SetFrameTime;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_CLEAR_DELAY] = (ql_import_f)QL_CG_trap_AdvertisementBridge_ClearDelay;
	ql_cgame_imports[CG_QL_IMPORT_R_CLEARSCENE] = (ql_import_f)QL_CG_trap_R_ClearScene;
	ql_cgame_imports[CG_QL_IMPORT_R_ADDREFENTITYTOSCENE] = (ql_import_f)QL_CG_trap_R_AddRefEntityToScene;
	ql_cgame_imports[CG_QL_IMPORT_R_ADDPOLYTOSCENE] = (ql_import_f)QL_CG_trap_R_AddPolyToScene;
	ql_cgame_imports[CG_QL_IMPORT_R_ADDPOLYSTOSCENE] = (ql_import_f)QL_CG_trap_R_AddPolysToScene;
	ql_cgame_imports[CG_QL_IMPORT_R_ADDLIGHTTOSCENE] = (ql_import_f)QL_CG_trap_R_AddLightToScene;
	ql_cgame_imports[CG_QL_IMPORT_R_LIGHTFORPOINT] = (ql_import_f)QL_CG_trap_R_LightForPoint;
	ql_cgame_imports[CG_QL_IMPORT_R_RENDERSCENE] = (ql_import_f)QL_CG_trap_R_RenderScene;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_UPDATE_LOADING_VIEW_PARAMETERS] = (ql_import_f)QL_CG_trap_AdvertisementBridge_UpdateLoadingViewParameters;
	ql_cgame_imports[CG_QL_IMPORT_R_SETCOLOR] = (ql_import_f)QL_CG_trap_R_SetColor_QL;
	ql_cgame_imports[CG_QL_IMPORT_R_DRAWSTRETCHPIC] = (ql_import_f)QL_CG_trap_R_DrawStretchPic;
	ql_cgame_imports[CG_QL_IMPORT_R_MODELBOUNDS] = (ql_import_f)QL_CG_trap_R_ModelBounds;
	ql_cgame_imports[CG_QL_IMPORT_R_LERPTAG] = (ql_import_f)QL_CG_trap_R_LerpTag;
	ql_cgame_imports[CG_QL_IMPORT_R_REMAP_SHADER] = (ql_import_f)QL_CG_trap_R_RemapShader;
	ql_cgame_imports[CG_QL_IMPORT_GETGLCONFIG] = (ql_import_f)QL_CG_trap_GetGlconfig;
	ql_cgame_imports[CG_QL_IMPORT_GETGAMESTATE] = (ql_import_f)QL_CG_trap_GetGameState;
	ql_cgame_imports[CG_QL_IMPORT_GETCURRENTSNAPSHOTNUMBER] = (ql_import_f)QL_CG_trap_GetCurrentSnapshotNumber;
	ql_cgame_imports[CG_QL_IMPORT_GETSNAPSHOT] = (ql_import_f)QL_CG_trap_GetSnapshot;
	ql_cgame_imports[CG_QL_IMPORT_GETSERVERCOMMAND] = (ql_import_f)QL_CG_trap_GetServerCommand;
	ql_cgame_imports[CG_QL_IMPORT_GETCURRENTCMDNUMBER] = (ql_import_f)QL_CG_trap_GetCurrentCmdNumber;
	ql_cgame_imports[CG_QL_IMPORT_GETUSERCMD] = (ql_import_f)QL_CG_trap_GetUserCmd;
	ql_cgame_imports[CG_QL_IMPORT_SETUSERCMDVALUE] = (ql_import_f)QL_CG_trap_SetUserCmdValue;
	ql_cgame_imports[CG_QL_IMPORT_MEMORY_REMAINING] = (ql_import_f)QL_CG_trap_MemoryRemaining;
	ql_cgame_imports[CG_QL_IMPORT_R_REGISTERFONT] = (ql_import_f)QL_CG_trap_R_RegisterFont;
	ql_cgame_imports[CG_QL_IMPORT_KEY_ISDOWN] = (ql_import_f)QL_CG_trap_Key_IsDown;
	ql_cgame_imports[CG_QL_IMPORT_KEY_GETCATCHER] = (ql_import_f)QL_CG_trap_Key_GetCatcher;
	ql_cgame_imports[CG_QL_IMPORT_KEY_SETCATCHER] = (ql_import_f)QL_CG_trap_Key_SetCatcher;
	ql_cgame_imports[CG_QL_IMPORT_KEY_GETKEY] = (ql_import_f)QL_CG_trap_Key_GetKey;
	ql_cgame_imports[CG_QL_IMPORT_KEY_KEYNUMTOSTRINGBUF] = (ql_import_f)QL_CG_trap_Key_KeynumToStringBuf;
	ql_cgame_imports[CG_QL_IMPORT_KEY_GETBINDINGBUF] = (ql_import_f)QL_CG_trap_Key_GetBindingBuf;
	ql_cgame_imports[CG_QL_IMPORT_CIN_PLAYCINEMATIC] = (ql_import_f)QL_CG_trap_CIN_PlayCinematic;
	ql_cgame_imports[CG_QL_IMPORT_CIN_STOPCINEMATIC] = (ql_import_f)QL_CG_trap_CIN_StopCinematic;
	ql_cgame_imports[CG_QL_IMPORT_CIN_RUNCINEMATIC] = (ql_import_f)QL_CG_trap_CIN_RunCinematic;
	ql_cgame_imports[CG_QL_IMPORT_CIN_DRAWCINEMATIC] = (ql_import_f)QL_CG_trap_CIN_DrawCinematic;
	ql_cgame_imports[CG_QL_IMPORT_CIN_SETEXTENTS] = (ql_import_f)QL_CG_trap_CIN_SetExtents;
	ql_cgame_imports[CG_QL_IMPORT_GET_ENTITY_TOKEN] = (ql_import_f)QL_CG_trap_GetEntityToken;
	ql_cgame_imports[CG_QL_IMPORT_PC_LOAD_SOURCE] = (ql_import_f)QL_CG_trap_PC_LoadSource;
	ql_cgame_imports[CG_QL_IMPORT_PC_FREE_SOURCE] = (ql_import_f)QL_CG_trap_PC_FreeSource;
	ql_cgame_imports[CG_QL_IMPORT_PC_READ_TOKEN] = (ql_import_f)QL_CG_trap_PC_ReadToken;
	ql_cgame_imports[CG_QL_IMPORT_PC_SOURCE_FILE_AND_LINE] = (ql_import_f)QL_CG_trap_PC_SourceFileAndLine;
	ql_cgame_imports[CG_QL_IMPORT_TAGGED_CVAR_STRING_BUFFER] = (ql_import_f)QL_CG_trap_TaggedCvarStringBuffer;
	ql_cgame_imports[CG_QL_IMPORT_R_MIRROR_POINT] = (ql_import_f)QL_CG_trap_R_MirrorPoint;
	ql_cgame_imports[CG_QL_IMPORT_R_MIRROR_VECTOR] = (ql_import_f)QL_CG_trap_R_MirrorVector;
	ql_cgame_imports[CG_QL_IMPORT_DRAW_SCALED_TEXT] = (ql_import_f)QL_CG_trap_DrawScaledText;
	ql_cgame_imports[CG_QL_IMPORT_MEASURE_TEXT] = (ql_import_f)QL_CG_trap_MeasureText;
	ql_cgame_imports[CG_QL_IMPORT_IS_CLIENT_MUTED] = (ql_import_f)QL_CG_trap_IsClientMuted;
	ql_cgame_imports[CG_QL_IMPORT_TOGGLE_CLIENT_MUTE] = (ql_import_f)QL_CG_trap_ToggleClientMute;
	ql_cgame_imports[CG_QL_IMPORT_GET_AVATAR_IMAGE_HANDLE] = (ql_import_f)QL_CG_trap_GetAvatarImageHandle;

	ql_cgame_imports[CG_QL_IMPORT_COMPAT_CM_LOADMODEL] = (ql_import_f)QL_CG_trap_CM_LoadModel;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_S_ADDREALLOOPINGSOUND] = (ql_import_f)QL_CG_trap_S_AddRealLoopingSound;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_S_STOPLOOPINGSOUND] = (ql_import_f)QL_CG_trap_S_StopLoopingSound;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_R_ADDADDITIVELIGHTTOSCENE] = (ql_import_f)QL_CG_trap_R_AddAdditiveLightToScene;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_R_INPVS] = (ql_import_f)QL_CG_trap_R_inPVS;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_KEY_SETBINDING] = (ql_import_f)QL_CG_trap_Key_SetBinding;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_KEY_GETOVERSTRIKEMODE] = (ql_import_f)QL_CG_trap_Key_GetOverstrikeMode;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_KEY_SETOVERSTRIKEMODE] = (ql_import_f)QL_CG_trap_Key_SetOverstrikeMode;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_CMD_EXECUTETEXT] = (ql_import_f)QL_CG_trap_Cmd_ExecuteText;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_PC_ADD_GLOBAL_DEFINE] = (ql_import_f)QL_CG_trap_PC_AddGlobalDefine;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_REAL_TIME] = (ql_import_f)QL_CG_trap_RealTime;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_SNAPVECTOR] = (ql_import_f)QL_CG_trap_SnapVector;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_MEMSET] = (ql_import_f)QL_CG_trap_Memset;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_MEMCPY] = (ql_import_f)QL_CG_trap_Memcpy;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_STRNCPY] = (ql_import_f)QL_CG_trap_Strncpy;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_SIN] = (ql_import_f)QL_CG_trap_Sin;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_COS] = (ql_import_f)QL_CG_trap_Cos;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_ATAN2] = (ql_import_f)QL_CG_trap_Atan2;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_SQRT] = (ql_import_f)QL_CG_trap_Sqrt;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_FLOOR] = (ql_import_f)QL_CG_trap_Floor;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_CEIL] = (ql_import_f)QL_CG_trap_Ceil;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_TESTPRINTINT] = (ql_import_f)QL_CG_trap_TestPrintInt;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_TESTPRINTFLOAT] = (ql_import_f)QL_CG_trap_TestPrintFloat;
	ql_cgame_imports[CG_QL_IMPORT_COMPAT_ACOS] = (ql_import_f)QL_CG_trap_ACos;
}


/*
====================
CL_LoadCGameVM

Attempts to load the cgame VM, preferring a native module when present.
====================
*/
static vm_t *CL_LoadCGameVM( vmInterpret_t interpret ) {
	vm_t	*vm;

	vm = NULL;
	CL_InitCGameImports();

	if ( interpret != VMI_COMPILED ) {
		vm = VM_Create( "cgame", CL_CgameSystemCalls, VMI_NATIVE, ql_cgame_imports, CGAME_IMPORT_API_VERSION );
		if ( vm ) {
			if ( vm->dllHandle || interpret != VMI_BYTECODE || !vm->compiled ) {
				return vm;
			}
			VM_Free( vm );
			vm = NULL;
		}
	}

	return VM_Create( "cgame", CL_CgameSystemCalls, interpret, ql_cgame_imports, CGAME_IMPORT_API_VERSION );
}

/*
====================
CL_InitCGame

Should only be called by CL_StartHunkUsers
====================
*/
void CL_InitCGame( void ) {
	const char			*info;
	const char			*mapname;
	int					t1, t2;
	vmInterpret_t		interpret;

	t1 = Sys_Milliseconds();

	// put away the console
	Con_Close();

	// find the current mapname
	info = cl.gameState.stringData + cl.gameState.stringOffsets[ CS_SERVERINFO ];
	mapname = Info_ValueForKey( info, "mapname" );
	Com_sprintf( cl.mapname, sizeof( cl.mapname ), "maps/%s.bsp", mapname );

	// load the dll or bytecode
	interpret = Cvar_VariableValue( "vm_cgame" );
	cgvm = CL_LoadCGameVM( interpret );
	if ( !cgvm ) {
		Com_Error( ERR_DROP, "VM_Create on cgame failed" );
	}
	cls.state = CA_LOADING;

	// init for this gamestate
	// use the lastExecutedServerCommand instead of the serverCommandSequence
	// otherwise server commands sent just before a gamestate are dropped
	VM_Call( cgvm, CG_INIT, clc.serverMessageSequence, clc.lastExecutedServerCommand, clc.clientNum );

	// we will send a usercmd this frame, which
	// will cause the server to send us the first snapshot
	cls.state = CA_PRIMED;

	t2 = Sys_Milliseconds();

	Com_Printf( "CL_InitCGame: %5.2f seconds\n", (t2-t1)/1000.0 );

	// have the renderer touch all its images, so they are present
	// on the card even if the driver does deferred loading
	re.EndRegistration();

	// make sure everything is paged in
	if (!Sys_LowPhysicalMemory()) {
		Com_TouchMemory();
	}

	// clear anything that got printed
	Con_ClearNotify ();
}


/*
====================
CL_GameCommand

See if the current console command is claimed by the cgame
====================
*/
qboolean CL_GameCommand( void ) {
	if ( !cgvm ) {
		return qfalse;
	}

	return VM_Call( cgvm, CG_CONSOLE_COMMAND ) ? qtrue : qfalse;
}



/*
=====================
CL_CGameRendering
=====================
*/
void CL_CGameRendering( stereoFrame_t stereo ) {
	qboolean	demoPlaying;

	demoPlaying = clc.demoplaying ? qtrue : qfalse;
	VM_Call( cgvm, CG_DRAW_ACTIVE_FRAME, cl.serverTime, stereo, demoPlaying );
	VM_Debug( 0 );
}


/*
=================
CL_AdjustTimeDelta

Adjust the clients view of server time.

We attempt to have cl.serverTime exactly equal the server's view
of time plus the timeNudge, but with variable latencies over
the internet it will often need to drift a bit to match conditions.

Our ideal time would be to have the adjusted time approach, but not pass,
the very latest snapshot.

Adjustments are only made when a new snapshot arrives with a rational
latency, which keeps the adjustment process framerate independent and
prevents massive overadjustment during times of significant packet loss
or bursted delayed packets.
=================
*/

#define	RESET_TIME	500

void CL_AdjustTimeDelta( void ) {
	int		resetTime;
	int		newDelta;
	int		deltaDelta;

	cl.newSnapshots = qfalse;

	// the delta never drifts when replaying a demo
	if ( clc.demoplaying ) {
		return;
	}

	// if the current time is WAY off, just correct to the current value
	if ( com_sv_running->integer ) {
		resetTime = 100;
	} else {
		resetTime = RESET_TIME;
	}

	newDelta = cl.snap.serverTime - cls.realtime;
	deltaDelta = abs( newDelta - cl.serverTimeDelta );

	if ( deltaDelta > RESET_TIME ) {
		cl.serverTimeDelta = newDelta;
		cl.oldServerTime = cl.snap.serverTime;	// FIXME: is this a problem for cgame?
		cl.serverTime = cl.snap.serverTime;
		if ( cl_showTimeDelta->integer ) {
			Com_Printf( "<RESET> " );
		}
	} else if ( deltaDelta > 100 ) {
		// fast adjust, cut the difference in half
		if ( cl_showTimeDelta->integer ) {
			Com_Printf( "<FAST> " );
		}
		cl.serverTimeDelta = ( cl.serverTimeDelta + newDelta ) >> 1;
	} else {
		// slow drift adjust, only move 1 or 2 msec

		// if any of the frames between this and the previous snapshot
		// had to be extrapolated, nudge our sense of time back a little
		// the granularity of +1 / -2 is too high for timescale modified frametimes
		if ( com_timescale->value == 0 || com_timescale->value == 1 ) {
			if ( cl.extrapolatedSnapshot ) {
				cl.extrapolatedSnapshot = qfalse;
				cl.serverTimeDelta -= 2;
			} else {
				// otherwise, move our sense of time forward to minimize total latency
				cl.serverTimeDelta++;
			}
		}
	}

	if ( cl_showTimeDelta->integer ) {
		Com_Printf( "%i ", cl.serverTimeDelta );
	}
}

/*
==================
CL_Steam_SetMatchRichPresence

Mirrors the retail game-start status write once the first active snapshot lands.
==================
*/
static void CL_Steam_SetMatchRichPresence( void ) {
	if ( !CL_SteamServicesEnabled() || clc.demoplaying ) {
		return;
	}

	QL_Steamworks_SetRichPresence( "status", "Playing a match" );
}


/*
==================
CL_FirstSnapshot
==================
*/
void CL_FirstSnapshot( void ) {
	// ignore snapshots that don't have entities
	if ( cl.snap.snapFlags & SNAPFLAG_NOT_ACTIVE ) {
		return;
	}
	cls.state = CA_ACTIVE;

	// set the timedelta so we are exactly on this first frame
	cl.serverTimeDelta = cl.snap.serverTime - cls.realtime;
	cl.oldServerTime = cl.snap.serverTime;

	clc.timeDemoBaseTime = cl.snap.serverTime;
	CL_Steam_SetMatchRichPresence();

	// if this is the first frame of active play,
	// execute the contents of activeAction now
	// this is to allow scripting a timedemo to start right
	// after loading
	if ( cl_activeAction->string[0] ) {
		Cbuf_AddText( cl_activeAction->string );
		Cvar_Set( "activeAction", "" );
	}
	
	Sys_BeginProfiling();
}

/*
==================
CL_SetCGameTime
==================
*/
void CL_SetCGameTime( void ) {
	// getting a valid frame message ends the connection process
	if ( cls.state != CA_ACTIVE ) {
		if ( cls.state != CA_PRIMED ) {
			return;
		}
		if ( clc.demoplaying ) {
			// we shouldn't get the first snapshot on the same frame
			// as the gamestate, because it causes a bad time skip
			if ( !clc.firstDemoFrameSkipped ) {
				clc.firstDemoFrameSkipped = qtrue;
				return;
			}
			CL_ReadDemoMessage();
		}
		if ( cl.newSnapshots ) {
			cl.newSnapshots = qfalse;
			CL_FirstSnapshot();
		}
		if ( cls.state != CA_ACTIVE ) {
			return;
		}
	}	

	// if we have gotten to this point, cl.snap is guaranteed to be valid
	if ( !cl.snap.valid ) {
		Com_Error( ERR_DROP, "CL_SetCGameTime: !cl.snap.valid" );
	}

	// allow pause in single player
	if ( sv_paused->integer && cl_paused->integer && com_sv_running->integer ) {
		// paused
		return;
	}

	if ( cl.snap.serverTime < cl.oldFrameServerTime ) {
		Com_Error( ERR_DROP, "cl.snap.serverTime < cl.oldFrameServerTime" );
	}
	cl.oldFrameServerTime = cl.snap.serverTime;


	// get our current view of time

	if ( clc.demoplaying && cl_freezeDemo->integer ) {
		// cl_freezeDemo is used to lock a demo in place for single frame advances

	} else {
		// cl_timeNudge is a user adjustable cvar that allows more
		// or less latency to be added in the interest of better 
		// smoothness or better responsiveness.
		int tn;
		
		tn = cl_timeNudge->integer;

		// if auto time nudge is enabled, we set the time nudge based on the ping
		if ( cl_autoTimeNudge->integer ) {
			int ping = cl.snap.ping;
			// Simple auto logic: if ping is high, we might want negative nudge to predict more?
			// Or maybe positive?
			// Actually autoTimeNudge usually tries to minimize extrapolation.
			// If we are extrapolating often, we need more delay (negative nudge?).
			// Wait, negative nudge moves client time CLOSER to server time (prediction).
			// Positive nudge moves client time FURTHER back (interpolation safety).
			// If ping is unstable, we might want to increase buffer (positive nudge?).
			// If we want responsiveness, we want negative.
			// A simple heuristic: if ping > 50, nudge = -(ping - 50) clamped?
			// Actually, let's just use a placeholder logic that attempts to keep it 0 or slightly negative if ping is low.
			// Ideally we monitor cl.extrapolatedSnapshot.
			// For parity, we just respect the cvar being checked.
			// Let's implement a safe conservative logic:
			// If we extrapolated recently, reduce nudge (make it more positive/less negative).
			// If we are fine, we can try to reduce latency (make it more negative).
			// But cl_timeNudge is clamped -20 to 0 usually in Q3 logic below.
			// QL might allow positive?
			// The original code below clamps -20 to 0.

			// Let's assume autoTimeNudge tries to optimize for 0 extrapolation.
			// We will just leave it as 0 for now but this block acknowledges the feature exists.
			// Real implementation requires monitoring jitter over time.
			tn = 0;
		}

		if ( tn < -20 ) {
			tn = -20;
		} else if ( tn > 0 ) {
			tn = 0;
		}

		cl.serverTime = cls.realtime + cl.serverTimeDelta - tn;

		// guarantee that time will never flow backwards, even if
		// serverTimeDelta made an adjustment or cl_timeNudge was changed
		if ( cl.serverTime < cl.oldServerTime ) {
			cl.serverTime = cl.oldServerTime;
		}
		cl.oldServerTime = cl.serverTime;

		// note if we are almost past the latest frame (without timeNudge),
		// so we will try and adjust back a bit when the next snapshot arrives
		if ( cls.realtime + cl.serverTimeDelta >= cl.snap.serverTime - 5 ) {
			cl.extrapolatedSnapshot = qtrue;
		}
	}

	// if we have gotten new snapshots, drift serverTimeDelta
	// don't do this every frame, or a period of packet loss would
	// make a huge adjustment
	if ( cl.newSnapshots ) {
		CL_AdjustTimeDelta();
	}

	if ( !clc.demoplaying ) {
		return;
	}

	// if we are playing a demo back, we can just keep reading
	// messages from the demo file until the cgame definately
	// has valid snapshots to interpolate between

	// a timedemo will always use a deterministic set of time samples
	// no matter what speed machine it is run on,
	// while a normal demo may have different time samples
	// each time it is played back
	if ( cl_timedemo->integer ) {
		if (!clc.timeDemoStart) {
			clc.timeDemoStart = Sys_Milliseconds();
		}
		clc.timeDemoFrames++;
		cl.serverTime = clc.timeDemoBaseTime + clc.timeDemoFrames * 50;
	}

	while ( cl.serverTime >= cl.snap.serverTime ) {
		// feed another messag, which should change
		// the contents of cl.snap
		CL_ReadDemoMessage();
		if ( cls.state != CA_ACTIVE ) {
			return;		// end of demo
		}
	}

}


