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

#include "../client/client.h"

#define CL_NULL_BROWSER_PROVIDER_LABEL "Null host compatibility shim"
#define CL_NULL_BROWSER_POLICY_LABEL "compatibility-only null host"
#define CL_NULL_BROWSER_PARITY_SCOPE_LABEL "strict-retail-excluded"
#define CL_NULL_BROWSER_PARITY_REASON_LABEL "retail Windows Awesomium host is outside the null-client portability lane"

typedef struct {
	int		activeAdvertCellId;
	int		activatedAdvertCellId;
} nullAdvertisementBridgeState_t;

cvar_t *cl_shownet;
static nullAdvertisementBridgeState_t cl_nullAdvertisementBridge;

/*
================
CL_NullResetAdvertisementBridgeState
================
*/
static void CL_NullResetAdvertisementBridgeState( void ) {
	Com_Memset( &cl_nullAdvertisementBridge, 0, sizeof( cl_nullAdvertisementBridge ) );
}

/*
================
CL_NullRefreshBrowserCvars
================
*/
static void CL_NullRefreshBrowserCvars( void ) {
	Cvar_Set( "ui_browserAwesomium", "0" );
	Cvar_Set( "ui_browserAwesomiumProvider", CL_NULL_BROWSER_PROVIDER_LABEL );
	Cvar_Set( "ui_browserAwesomiumPolicy", CL_NULL_BROWSER_POLICY_LABEL );
	Cvar_Set( "ui_browserAwesomiumParityScope", CL_NULL_BROWSER_PARITY_SCOPE_LABEL );
	Cvar_Set( "ui_browserAwesomiumParityReason", CL_NULL_BROWSER_PARITY_REASON_LABEL );
	Cvar_Set( "web_browserActive", "0" );
	Cvar_Set( "ui_advertisementBridgeProvider", CL_NULL_BROWSER_PROVIDER_LABEL );
	Cvar_Set( "ui_advertisementBridgePolicy", CL_NULL_BROWSER_POLICY_LABEL );
	Cvar_Set( "ui_advertisementBridgeParityScope", CL_NULL_BROWSER_PARITY_SCOPE_LABEL );
	Cvar_Set( "ui_advertisementBridgeParityReason", CL_NULL_BROWSER_PARITY_REASON_LABEL );
}

/*
================
CL_Shutdown
================
*/
void CL_Shutdown( void ) {
}

/*
================
CL_Init
================
*/
void CL_Init( void ) {
	cl_shownet = Cvar_Get( "cl_shownet", "0", CVAR_TEMP );
	CL_NullResetAdvertisementBridgeState();
	CL_NullRefreshBrowserCvars();
}

/*
================
CL_MouseEvent
================
*/
void CL_MouseEvent( int dx, int dy, int time ) {
	(void)dx;
	(void)dy;
	(void)time;
}

/*
================
Key_WriteBindings
================
*/
void Key_WriteBindings( fileHandle_t f ) {
	(void)f;
}

/*
================
Key_EnumerateBindings
================
*/
void Key_EnumerateBindings( keyBindingEnumCallback_t callback, void *userData ) {
	(void)callback;
	(void)userData;
}

/*
================
CL_Frame
================
*/
void CL_Frame ( int msec ) {
	(void)msec;
}

/*
================
SteamClient_Frame
================
*/
void SteamClient_Frame( void ) {
}

/*
================
CL_PacketEvent
================
*/
void CL_PacketEvent( netadr_t from, msg_t *msg ) {
	(void)from;
	(void)msg;
}

/*
================
CL_CharEvent
================
*/
void CL_CharEvent( int key ) {
	(void)key;
}

/*
================
CL_Disconnect
================
*/
void CL_Disconnect( qboolean showMainMenu ) {
	(void)showMainMenu;
}

/*
================
CL_MapLoading
================
*/
void CL_MapLoading( void ) {
}

/*
================
CL_GameCommand
================
*/
qboolean CL_GameCommand( void ) {
	return qfalse; // bk001204 - non-void
}

/*
================
CL_KeyEvent
================
*/
void CL_KeyEvent (int key, qboolean down, unsigned time) {
	(void)key;
	(void)down;
	(void)time;
}

/*
================
UI_GameCommand
================
*/
qboolean UI_GameCommand( void ) {
	return qfalse;
}

/*
================
CL_RefreshOnlineServicesBridgeState
================
*/
void CL_RefreshOnlineServicesBridgeState( void ) {
	CL_NullRefreshBrowserCvars();
}

/*
================
CL_WebHost_Init
================
*/
void CL_WebHost_Init( void ) {
	CL_NullResetAdvertisementBridgeState();
	CL_NullRefreshBrowserCvars();
}

/*
================
CL_WebHost_Shutdown
================
*/
void CL_WebHost_Shutdown( void ) {
	CL_NullResetAdvertisementBridgeState();
	CL_NullRefreshBrowserCvars();
}

/*
================
CL_WebHost_Frame
================
*/
void CL_WebHost_Frame( void ) {
	CL_NullRefreshBrowserCvars();
}

/*
================
CL_WebHost_HasLiveView
================
*/
qboolean CL_WebHost_HasLiveView( void ) {
	return qfalse;
}

/*
================
CL_WebHost_HasBoundWindowObject
================
*/
qboolean CL_WebHost_HasBoundWindowObject( void ) {
	return qfalse;
}

/*
================
CL_WebHost_GetCursorHandle
================
*/
void *CL_WebHost_GetCursorHandle( void ) {
	return NULL;
}

/*
================
CL_WebHost_NotifyAppActivation
================
*/
void CL_WebHost_NotifyAppActivation( qboolean active ) {
	(void)active;
}

/*
================
CL_WebView_PublishEvent
================
*/
void CL_WebView_PublishEvent( const char *name, const char *payload ) {
	(void)name;
	(void)payload;
}

/*
================
CL_WebView_InvokeCommNotice
================
*/
void CL_WebView_InvokeCommNotice( const char *message ) {
	(void)message;
}

/*
================
CL_WebView_PublishTaggedInfoString
================
*/
void CL_WebView_PublishTaggedInfoString( const char *messageType, const char *infoString ) {
	(void)messageType;
	(void)infoString;
}

/*
================
CL_WebView_PublishGameError
================
*/
void CL_WebView_PublishGameError( const char *message ) {
	(void)message;
}

/*
================
CL_WebView_PublishGameEnd
================
*/
void CL_WebView_PublishGameEnd( void ) {
}

/*
================
CL_WebView_PublishCvarChange
================
*/
void CL_WebView_PublishCvarChange( const char *name, const char *value, qboolean replicate ) {
	(void)name;
	(void)value;
	(void)replicate;
}

/*
================
CL_WebView_PublishBindChanged
================
*/
void CL_WebView_PublishBindChanged( const char *name, const char *value ) {
	(void)name;
	(void)value;
}

/*
================
CL_WebView_PublishGameStart
================
*/
void CL_WebView_PublishGameStart( void ) {
}

/*
================
CL_WebView_PublishGameDemo
================
*/
void CL_WebView_PublishGameDemo( const char *id, const char *name ) {
	(void)id;
	(void)name;
}

/*
================
CL_WebView_PublishGameScreenshot
================
*/
void CL_WebView_PublishGameScreenshot( const char *id, const char *name ) {
	(void)id;
	(void)name;
}

/*
================
CL_WebView_OnMouseMove
================
*/
void CL_WebView_OnMouseMove( int x, int y ) {
	(void)x;
	(void)y;
}

/*
================
CL_WebView_OnMouseButtonEvent
================
*/
void CL_WebView_OnMouseButtonEvent( int key, qboolean down ) {
	(void)key;
	(void)down;
}

/*
================
CL_WebView_OnMouseWheelEvent
================
*/
void CL_WebView_OnMouseWheelEvent( int direction ) {
	(void)direction;
}

/*
================
CL_WebView_OnKeyEvent
================
*/
void CL_WebView_OnKeyEvent( int key, qboolean down ) {
	(void)key;
	(void)down;
}

/*
================
CL_AdvertisementBridge_RefreshLoadingViewParameters
================
*/
void CL_AdvertisementBridge_RefreshLoadingViewParameters( void ) {
	CL_NullRefreshBrowserCvars();
}

/*
================
CL_AdvertisementBridge_UpdateLoadingViewParameters
================
*/
void CL_AdvertisementBridge_UpdateLoadingViewParameters( void ) {
	CL_AdvertisementBridge_RefreshLoadingViewParameters();
}

/*
================
CL_AdvertisementBridge_InitUI
================
*/
void CL_AdvertisementBridge_InitUI( void ) {
	CL_NullResetAdvertisementBridgeState();
	CL_RefreshOnlineServicesBridgeState();
}

/*
================
CL_AdvertisementBridge_ActivateAdvert
================
*/
void CL_AdvertisementBridge_ActivateAdvert( int cellId ) {
	cl_nullAdvertisementBridge.activatedAdvertCellId = cellId;
	CL_RefreshOnlineServicesBridgeState();
}

/*
================
CL_AdvertisementBridge_SetActiveAdvert
================
*/
void CL_AdvertisementBridge_SetActiveAdvert( int cellId ) {
	cl_nullAdvertisementBridge.activeAdvertCellId = cellId;
	if ( cellId == 0 ) {
		cl_nullAdvertisementBridge.activatedAdvertCellId = 0;
	}

	CL_RefreshOnlineServicesBridgeState();
}

/*
================
CL_ForwardCommandToServer
================
*/
void CL_ForwardCommandToServer( const char *string ) {
	(void)string;
}

/*
================
CL_ConsolePrint
================
*/
void CL_ConsolePrint( char *txt ) {
	(void)txt;
}

/*
================
CL_JoystickEvent
================
*/
void CL_JoystickEvent( int axis, int value, int time ) {
	(void)axis;
	(void)value;
	(void)time;
}

/*
================
CL_InitKeyCommands
================
*/
void CL_InitKeyCommands( void ) {
}

/*
================
CL_CDDialog
================
*/
void CL_CDDialog( void ) {
}

/*
================
CL_FlushMemory
================
*/
void CL_FlushMemory( void ) {
}

/*
================
CL_StartHunkUsers
================
*/
void CL_StartHunkUsers( void ) {
}

/*
================
CL_ShutdownAll
================
*/
void CL_ShutdownAll( void ) {
}

/*
================
CL_CDKeyValidate
================
*/
qboolean CL_CDKeyValidate( const char *key, const char *checksum ) {
	(void)key;
	(void)checksum;
	return qtrue;
}
