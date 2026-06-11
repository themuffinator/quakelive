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
#include "../../game/match_state_keys.h"
#include "../../common/platform/platform_steamworks.h"

#include "../game/botlib.h"
#include "../qcommon/vm_local.h"
#include "../../common/platform/platform_services.h"
#include "../../common/platform/platform_steamworks.h"
#include "../../../src-re/include/fs_imports.h"
#include <ctype.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#ifdef _WIN32
#include <windows.h>
#include "../win32/win_local.h"
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
	int			delayDeadline;
} clAdvertisementBridgeState_t;

static clAdvertisementBridgeState_t cl_advertisementBridge;
static qboolean cl_previousBrowserAvailable = qfalse;
static cvar_t *cl_webZoom = NULL;
static cvar_t *cl_webConsole = NULL;
static cvar_t *cl_webBrowserActive = NULL;

typedef struct {
	const char	*name;
	unsigned int	retailAddress;
	const char	*defaultValue;
	int			flags;
	const char	*owner;
} clWebCvarRetailMapping_t;

static const clWebCvarRetailMapping_t cl_webCvarRetailMappings[] = {
	{ "web_zoom", 0x012D3060u, "100", CVAR_ARCHIVE, "Awesomium WebView::SetZoom" },
	{ "web_console", 0x012D3064u, "0", CVAR_ARCHIVE, "QLViewHandler::OnAddConsoleMessage" },
	{ "web_browserActive", 0x0145CA50u, "0", CVAR_ROM, "browser-active client/renderer/UI state" },
	{ NULL, 0u, NULL, 0, NULL }
};

/*
=============
CL_SetCvarIfChanged

Suppresses no-op Cvar_Set2 debug churn from retained compatibility publishers.
=============
*/
static void CL_SetCvarIfChanged( const char *name, const char *value ) {
	const char *current;

	if ( !name || !value ) {
		return;
	}

	current = Cvar_VariableString( name );
	if ( strcmp( current, value ) ) {
		Cvar_Set( name, value );
	}
}

/*
=============
CL_WebCvarIntegerValue

Returns the cached web cvar integer value, falling back to a name lookup before
the retail registration helper has run.
=============
*/
static int CL_WebCvarIntegerValue( const cvar_t *cvar, const char *fallbackName ) {
	if ( cvar ) {
		return cvar->integer;
	}

	return Cvar_VariableIntegerValue( fallbackName );
}

/*
=============
QLWebHost_CountRecoveredWebCvarMappings

Counts source-visible retail web cvar mapping rows.
=============
*/
static int QLWebHost_CountRecoveredWebCvarMappings( void ) {
	int count;

	for ( count = 0; cl_webCvarRetailMappings[count].name; count++ ) {
	}

	return count;
}

#define CL_ADVERTISEMENT_DEBUG_LABEL_COUNT 2

#define CL_WEB_FRIEND_FLAGS 4
#define CL_WEB_MAX_QZ_METHODS 35
#define CL_WEB_QZ_METHOD_TABLE_RETAIL_BEGIN 0x0055C008u
#define CL_WEB_QZ_METHOD_TABLE_RETAIL_END 0x0055C1A0u
#define CL_WEB_QZ_METHOD_TABLE_ENTRY_BYTES 0x0Cu
#define CL_WEB_JSON_BUFFER_SIZE 32768
#define CL_WEB_LAUNCHER_SCRIPT_LIST_BUFFER 4096
#define CL_WEB_DEFAULT_URL "asset://ql/index.html"
#define CL_WEB_RETAIL_SURFACE_IMAGE "browser"
#define CL_WEB_SURFACE_IMAGE "*ql_web_browser"
#define CL_WEB_SURFACE_SHADER "browserShader"
#define CL_WEB_BOOTSTRAP_MAX_ATTEMPTS 10
#define CL_WEB_BOOTSTRAP_SLEEP_MSEC 100
#define CL_WEB_NATIVE_REQUESTS_PER_FRAME 1
#define CL_WEB_NATIVE_REQUEST_STARTUP_DELAY_FRAMES 120
#define CL_WEB_NATIVE_REQUEST_IDLE_POLL_FRAMES 15
#define CL_WEB_NATIVE_REQUEST_LOADING_POLL_FRAMES 30
#define CL_WEB_NATIVE_REQUEST_BUSY_POLL_FRAMES 1
#define CL_WEB_NATIVE_CONFIG_SYNC_FRAMES 300
#define CL_WEB_NATIVE_MAP_SYNC_FRAMES 300
#define CL_WEB_NATIVE_MAP_RETRY_FRAMES 15
#define CL_WEB_NATIVE_FACTORY_SYNC_FRAMES 300
#define CL_WEB_NATIVE_FACTORY_RETRY_FRAMES 15
#define CL_WEB_NATIVE_CONFIG_BUFFER_SIZE 131072
#define CL_WEB_MAP_JSON_BUFFER_SIZE 65536
#define CL_WEB_FACTORY_JSON_BUFFER_SIZE 65536
#define CL_WEB_MAP_SYNC_CHUNK_CHARS 8192
#define CL_WEB_FACTORY_SYNC_CHUNK_CHARS 8192
#define CL_WEB_LIVE_SURFACE_FAILURE_FRAMES 180

typedef struct clWebFactoryBasegt_s clWebFactoryBasegt_t;

static qboolean CL_OverlayServiceAvailable( void );
static void CL_WebHost_BuildConfigJson( char *buffer, size_t bufferSize );
static void CL_WebHost_BuildMapListJson( char *buffer, size_t bufferSize );
static void CL_WebHost_BuildFactoryListJson( char *buffer, size_t bufferSize );
static void CL_WebHost_LoadFactoryBasegtList( clWebFactoryBasegt_t *definitions, int *definitionCount, int maxDefinitions );
static void CL_WebHost_PumpNativeJavascriptRequests( void );
static void CL_WebHost_SyncConfigSnapshot( void );
static void CL_WebHost_SyncMapCatalogSnapshot( void );
static void CL_WebHost_SyncFactoryCatalogSnapshot( void );
static void CL_WebHost_CheckLiveAwesomiumSurfaceFailure( void );
static void CL_ResetBrowserOverlayState( void );

typedef enum {
	CL_WEB_METHOD_IS_PAK_FILE_PRESENT = 0,
	CL_WEB_METHOD_IS_GAME_RUNNING = 1,
	CL_WEB_METHOD_SEND_GAME_COMMAND = 2,
	CL_WEB_METHOD_WRITE_TEXT_FILE = 3,
	CL_WEB_METHOD_GET_CVAR = 4,
	CL_WEB_METHOD_SET_CVAR = 5,
	CL_WEB_METHOD_RESET_CVAR = 6,
	CL_WEB_METHOD_GET_MAP_LIST = 7,
	CL_WEB_METHOD_GET_FACTORY_LIST = 8,
	CL_WEB_METHOD_GET_DEMO_LIST = 9,
	CL_WEB_METHOD_OPEN_URL = 10,
	CL_WEB_METHOD_OPEN_STEAM_OVERLAY_URL = 11,
	CL_WEB_METHOD_GET_CLIPBOARD_TEXT = 12,
	CL_WEB_METHOD_SET_CLIPBOARD_TEXT = 13,
	CL_WEB_METHOD_REQUEST_SERVERS = 14,
	CL_WEB_METHOD_REQUEST_SERVER_DETAILS = 15,
	CL_WEB_METHOD_REFRESH_LIST = 16,
	CL_WEB_METHOD_CREATE_LOBBY = 17,
	CL_WEB_METHOD_LEAVE_LOBBY = 18,
	CL_WEB_METHOD_JOIN_LOBBY = 19,
	CL_WEB_METHOD_SET_LOBBY_SERVER = 20,
	CL_WEB_METHOD_SHOW_INVITE_OVERLAY = 21,
	CL_WEB_METHOD_SAY_LOBBY = 22,
	CL_WEB_METHOD_REQUEST_USER_STATS = 23,
	CL_WEB_METHOD_GET_FRIEND_LIST = 24,
	CL_WEB_METHOD_ACTIVATE_GAME_OVERLAY_TO_USER = 25,
	CL_WEB_METHOD_INVITE = 26,
	CL_WEB_METHOD_FILE_EXISTS = 27,
	CL_WEB_METHOD_GET_CONFIG = 28,
	CL_WEB_METHOD_GET_CURSOR_POSITION = 29,
	CL_WEB_METHOD_NO_OP = 30,
	CL_WEB_METHOD_GET_ALL_UGC = 31,
	CL_WEB_METHOD_GET_NEXT_KEY_DOWN = 32,
	CL_WEB_METHOD_SET_FAVORITE_SERVER = 33
} clWebMethodId_t;

typedef struct {
	const char	*name;
	unsigned int	retailTableAddress;
	int			methodId;
	qboolean	returnsValue;
} clWebMethodBinding_t;

typedef struct {
	const char		*listenerName;
	const char		*retailCallback;
	unsigned int	vtableAddress;
	unsigned int	slotOffset;
	unsigned int	retailAddress;
	const char		*sourceCallback;
	const char		*scope;
} clWebListenerCallbackMapping_t;

typedef struct {
	qboolean	coreInitialised;
	qboolean	sessionInitialised;
	qboolean	viewInitialised;
	qboolean	bootstrapReady;
	qboolean	documentReady;
	qboolean	loadingDocument;
	qboolean	loadFailed;
	qboolean	dataPakSourceInstalled;
	qboolean	steamDataSourceInstalled;
	qboolean	resourceInterceptorInstalled;
	qboolean	jsMethodHandlerInstalled;
	qboolean	dialogHandlerInstalled;
	qboolean	viewHandlerInstalled;
	qboolean	loadHandlerInstalled;
	qboolean	liveAwesomium;
	qboolean	windowObjectBound;
	qboolean	qzInstanceBound;
	qboolean	browserVisible;
	qboolean	browserActive;
	qboolean	refreshStopped;
	qboolean	surfaceImageInitialised;
	qboolean	surfaceDirty;
	qboolean	surfaceHasVisiblePixels;
	qboolean	surfaceHasUiContent;
	qboolean	surfacePresented;
	qboolean	keyCaptureArmed;
	qboolean	focused;
	qboolean	cursorPositionValid;
	int			viewWidth;
	int			viewHeight;
	int			surfaceContentWidth;
	int			surfaceContentHeight;
	int			surfaceWidth;
	int			surfaceHeight;
	int			cursorX;
	int			cursorY;
	int			frameSequence;
	int			nextConfigSyncFrame;
	int			nextMapCatalogSyncFrame;
	int			nextFactoryCatalogSyncFrame;
	int			nextNativeRequestPollFrame;
	int			zoomPercent;
	int			bootstrapAttemptCount;
	int			cvarMappingCount;
	int			listenerCallbackMappingCount;
	int			loadedDocumentScriptCount;
	int			executedDocumentScriptCount;
	int			failedDocumentScriptCount;
	int			liveSurfaceMissingFrames;
	int			surfaceUploadWidth;
	int			surfaceUploadHeight;
	uint32_t	appId;
	uint32_t	steamIdLow;
	uint32_t	steamIdHigh;
	qhandle_t	surfaceShader;
	byte		*surfaceBuffer;
	int			surfaceBufferLength;
	char		currentUrl[MAX_STRING_CHARS];
	char		currentDocument[MAX_QPATH];
	char		pendingHash[MAX_STRING_CHARS];
	char		playerName[MAX_NAME_LENGTH];
	char		sessionPath[MAX_OSPATH];
	char		surfaceImageName[MAX_QPATH];
	char		surfaceShaderName[MAX_QPATH];
	char		tooltip[MAX_QPATH];
#if defined( _WIN32 )
	HCURSOR		activeCursorHandle;
	HCURSOR		restoreCursorHandle;
	int			activeCursorType;
	qboolean	cursorOverrideActive;
#endif
	qboolean	configSynced;
	qboolean	mapCatalogSynced;
	qboolean	factoryCatalogSynced;
} clWebHostState_t;

typedef struct {
	char		*buffer;
	size_t		bufferSize;
	int			count;
} clWebJsonBuilder_t;

#define CL_WEB_ARENA_FILE_LIST_BUFFER 4096
#define CL_WEB_MAX_MAPS 256
#define CL_WEB_MAP_POOL_FILE_BYTES 0x8000
#define CL_WEB_MAX_FACTORY_DEFINITIONS 256
#define CL_WEB_FACTORY_JSON_STRING 8192

typedef struct {
	const char	*cursor;
	const char	*end;
	const char	*filename;
	int			line;
} clWebFactoryParseState_t;

typedef struct {
	char		id[MAX_QPATH];
	char		title[128];
	char		author[128];
	char		description[1024];
	char		basegt[64];
	char		settingsJson[CL_WEB_FACTORY_JSON_STRING];
} clWebFactoryDefinition_t;

struct clWebFactoryBasegt_s {
	char		id[MAX_QPATH];
	char		basegt[64];
};

typedef struct {
	char		sysname[MAX_QPATH];
	char		name[MAX_INFO_VALUE];
	unsigned int	typeBits;
} clWebMapDescriptor_t;

static clWebHostState_t cl_webHost;

/*
=============
CL_WebZoomIntegerValue

Returns the browser zoom percent, preserving retail's default when the cvar is
cleared or set to a non-positive value.
=============
*/
static int CL_WebZoomIntegerValue( void ) {
	int zoomPercent;

	zoomPercent = CL_WebCvarIntegerValue( cl_webZoom, "web_zoom" );
	if ( zoomPercent <= 0 ) {
		return 100;
	}

	return zoomPercent;
}

/*
=============
CL_WebZoomClearModified

Clears the cached web_zoom modified latch after the live view consumes it.
=============
*/
static void CL_WebZoomClearModified( void ) {
	if ( cl_webZoom ) {
		cl_webZoom->modified = qfalse;
	}
}

typedef struct {
	unsigned int	eventType;
	unsigned int	virtualKeyCode;
	long			nativeKeyCode;
} qlWebKeyboardEventFields_t;

#define QL_WEB_KEYBOARD_EVENT_KEYDOWN_TYPE 0u
#define QL_WEB_KEYBOARD_EVENT_KEYUP_TYPE 1u
#define QL_WEB_KEYBOARD_EVENT_CHAR_TYPE 2u
#define QL_WEB_KEYBOARD_EVENT_ACTIVATION_TYPE 0u
#define QL_WEB_KEYBOARD_EVENT_ACTIVATION_VIRTUAL_KEY 0x11u
#define QL_WEB_KEYBOARD_EVENT_ACTIVATION_NATIVE_KEY 0x1d0001L

typedef enum {
	QL_WEB_BRIDGE_SLOT_SET_ACTIVE_ADVERT = 0x08,
	QL_WEB_BRIDGE_SLOT_SET_APP_ACTIVATION = 0x0c,
	QL_WEB_BRIDGE_SLOT_SET_FRAME_TIME = 0x10,
	QL_WEB_BRIDGE_SLOT_UPDATE_VIEW_PARAMETERS = 0x14,
	QL_WEB_BRIDGE_SLOT_SET_VISIBILITY_TRACE_CALLBACK = 0x18,
	QL_WEB_BRIDGE_SLOT_RESERVED_1FC0 = 0x1c,
	QL_WEB_BRIDGE_SLOT_SET_MAP_PATH = 0x20,
	QL_WEB_BRIDGE_SLOT_INIT_CGAME = 0x24,
	QL_WEB_BRIDGE_SLOT_SHUTDOWN_CGAME = 0x28,
	QL_WEB_BRIDGE_SLOT_SET_CLIENT_STATE_FLAGS = 0x2c,
	QL_WEB_BRIDGE_SLOT_GET_CELL_DISPLAY_STATE = 0x38,
	QL_WEB_BRIDGE_SLOT_GET_CELL_LABEL = 0x3c,
	QL_WEB_BRIDGE_SLOT_RESERVED_21C0 = 0x40,
	QL_WEB_BRIDGE_SLOT_INIT_UI = 0x44,
	QL_WEB_BRIDGE_SLOT_GET_LABEL_LIST2_COUNT = 0x48,
	QL_WEB_BRIDGE_SLOT_GET_LABEL_LIST1_COUNT = 0x4c,
	QL_WEB_BRIDGE_SLOT_SETUP_ADVERT_CELL_SHADER = 0x50,
	QL_WEB_BRIDGE_SLOT_SETUP_UI_ADVERT_CELL_SHADER = 0x54,
	QL_WEB_BRIDGE_SLOT_REFRESH_ADVERT_CELL_SHADER = 0x58,
	QL_WEB_BRIDGE_SLOT_REFRESH_UI_ADVERT_CELL_SHADER = 0x5c,
	QL_WEB_BRIDGE_SLOT_GET_LABEL_LIST2_ENTRY = 0x60,
	QL_WEB_BRIDGE_SLOT_GET_LABEL_LIST1_ENTRY = 0x64,
	QL_WEB_BRIDGE_SLOT_ACTIVATE_ADVERT = 0x68
} qlWebBridgeSlotOffset_t;

#define QL_WEB_BRIDGE_RETAIL_OBJECT_ADDRESS 0x012D2670u

typedef struct ql_web_bridge_s ql_web_bridge_t;

typedef struct {
	void		*reservedDestructor;
	void		*reservedDelete;
	int			( *setActiveAdvert )( ql_web_bridge_t *bridge, int cellId );
	void		( *setAppActivation )( ql_web_bridge_t *bridge, int active );
	int			( *setFrameTime )( ql_web_bridge_t *bridge, int frameTime );
	int			( *updateViewParameters )( ql_web_bridge_t *bridge, int x, int y, int width, int height, float fovX, float fovY, float zFar, int time, int flags );
	void		( *setVisibilityTraceCallback )( ql_web_bridge_t *bridge, void *callback );
	int			( *reserved1FC0 )( ql_web_bridge_t *bridge, int value );
	int			( *setMapPath )( ql_web_bridge_t *bridge, const char *mapPath );
	int			( *initCGame )( ql_web_bridge_t *bridge );
	int			( *shutdownCGame )( ql_web_bridge_t *bridge );
	int			( *setClientStateFlags )( ql_web_bridge_t *bridge, int flags );
	void		*reserved30;
	void		*reserved34;
	int			( *getCellDisplayState )( ql_web_bridge_t *bridge, int cellId );
	int			( *getCellLabel )( ql_web_bridge_t *bridge, int cellId, char *buffer, int bufferSize );
	void		( *reserved21C0 )( ql_web_bridge_t *bridge );
	void		( *initUI )( ql_web_bridge_t *bridge );
	int			( *getLabelList2Count )( ql_web_bridge_t *bridge );
	int			( *getLabelList1Count )( ql_web_bridge_t *bridge );
	qhandle_t	( *setupAdvertCellShader )( ql_web_bridge_t *bridge, const char *defaultContent, const void *rect, int cellId );
	qhandle_t	( *setupUIAdvertCellShader )( ql_web_bridge_t *bridge, const char *defaultContent, const void *rect, int cellId );
	qhandle_t	( *refreshAdvertCellShader )( ql_web_bridge_t *bridge, const char *defaultContent, const void *rect, int cellId );
	qhandle_t	( *refreshUIAdvertCellShader )( ql_web_bridge_t *bridge, const char *defaultContent, const void *rect, int cellId );
	int			( *getLabelList2Entry )( ql_web_bridge_t *bridge, int index, char *buffer, int bufferSize );
	int			( *getLabelList1Entry )( ql_web_bridge_t *bridge, int index, char *buffer, int bufferSize );
	void		( *activateAdvert )( ql_web_bridge_t *bridge, int cellId );
} ql_web_bridge_vtbl_t;

struct ql_web_bridge_s {
	const ql_web_bridge_vtbl_t	*vtbl;
	clAdvertisementBridgeState_t	*advertisement;
	clWebHostState_t				*webHost;
	void						*visibilityTraceCallback;
	int							clientStateFlags;
	char						mapPath[MAX_QPATH];
};

#if defined( _M_IX86 ) || defined( __i386__ )
#define QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( field, offset ) \
	typedef char ql_web_bridge_vtbl_##field##_offset[( offsetof( ql_web_bridge_vtbl_t, field ) == ( offset ) ) ? 1 : -1]
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( setActiveAdvert, QL_WEB_BRIDGE_SLOT_SET_ACTIVE_ADVERT );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( setAppActivation, QL_WEB_BRIDGE_SLOT_SET_APP_ACTIVATION );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( setFrameTime, QL_WEB_BRIDGE_SLOT_SET_FRAME_TIME );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( updateViewParameters, QL_WEB_BRIDGE_SLOT_UPDATE_VIEW_PARAMETERS );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( setVisibilityTraceCallback, QL_WEB_BRIDGE_SLOT_SET_VISIBILITY_TRACE_CALLBACK );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( reserved1FC0, QL_WEB_BRIDGE_SLOT_RESERVED_1FC0 );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( setMapPath, QL_WEB_BRIDGE_SLOT_SET_MAP_PATH );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( initCGame, QL_WEB_BRIDGE_SLOT_INIT_CGAME );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( shutdownCGame, QL_WEB_BRIDGE_SLOT_SHUTDOWN_CGAME );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( setClientStateFlags, QL_WEB_BRIDGE_SLOT_SET_CLIENT_STATE_FLAGS );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( getCellDisplayState, QL_WEB_BRIDGE_SLOT_GET_CELL_DISPLAY_STATE );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( getCellLabel, QL_WEB_BRIDGE_SLOT_GET_CELL_LABEL );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( reserved21C0, QL_WEB_BRIDGE_SLOT_RESERVED_21C0 );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( initUI, QL_WEB_BRIDGE_SLOT_INIT_UI );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( getLabelList2Count, QL_WEB_BRIDGE_SLOT_GET_LABEL_LIST2_COUNT );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( getLabelList1Count, QL_WEB_BRIDGE_SLOT_GET_LABEL_LIST1_COUNT );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( setupAdvertCellShader, QL_WEB_BRIDGE_SLOT_SETUP_ADVERT_CELL_SHADER );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( setupUIAdvertCellShader, QL_WEB_BRIDGE_SLOT_SETUP_UI_ADVERT_CELL_SHADER );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( refreshAdvertCellShader, QL_WEB_BRIDGE_SLOT_REFRESH_ADVERT_CELL_SHADER );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( refreshUIAdvertCellShader, QL_WEB_BRIDGE_SLOT_REFRESH_UI_ADVERT_CELL_SHADER );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( getLabelList2Entry, QL_WEB_BRIDGE_SLOT_GET_LABEL_LIST2_ENTRY );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( getLabelList1Entry, QL_WEB_BRIDGE_SLOT_GET_LABEL_LIST1_ENTRY );
QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( activateAdvert, QL_WEB_BRIDGE_SLOT_ACTIVATE_ADVERT );
#undef QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET
#endif

static int QLWebBridge_SetActiveAdvert( ql_web_bridge_t *bridge, int cellId );
static void QLWebBridge_SetAppActivation( ql_web_bridge_t *bridge, int active );
static int QLWebBridge_SetFrameTime( ql_web_bridge_t *bridge, int frameTime );
static int QLWebBridge_UpdateViewParameters( ql_web_bridge_t *bridge, int x, int y, int width, int height, float fovX, float fovY, float zFar, int time, int flags );
static void QLWebBridge_SetVisibilityTraceCallback( ql_web_bridge_t *bridge, void *callback );
static int QLWebBridge_Reserved1FC0( ql_web_bridge_t *bridge, int value );
static int QLWebBridge_SetMapPath( ql_web_bridge_t *bridge, const char *mapPath );
static int QLWebBridge_InitCGame( ql_web_bridge_t *bridge );
static int QLWebBridge_ShutdownCGame( ql_web_bridge_t *bridge );
static int QLWebBridge_SetClientStateFlags( ql_web_bridge_t *bridge, int flags );
static int QLWebBridge_GetCellDisplayState( ql_web_bridge_t *bridge, int cellId );
static int QLWebBridge_GetCellLabel( ql_web_bridge_t *bridge, int cellId, char *buffer, int bufferSize );
static void QLWebBridge_Reserved21C0( ql_web_bridge_t *bridge );
static void QLWebBridge_InitUI( ql_web_bridge_t *bridge );
static int QLWebBridge_GetLabelList2Count( ql_web_bridge_t *bridge );
static int QLWebBridge_GetLabelList1Count( ql_web_bridge_t *bridge );
static qhandle_t QLWebBridge_SetupAdvertCellShader( ql_web_bridge_t *bridge, const char *defaultContent, const void *rect, int cellId );
static qhandle_t QLWebBridge_SetupUIAdvertCellShader( ql_web_bridge_t *bridge, const char *defaultContent, const void *rect, int cellId );
static qhandle_t QLWebBridge_RefreshAdvertCellShader( ql_web_bridge_t *bridge, const char *defaultContent, const void *rect, int cellId );
static qhandle_t QLWebBridge_RefreshUIAdvertCellShader( ql_web_bridge_t *bridge, const char *defaultContent, const void *rect, int cellId );
static int QLWebBridge_GetLabelList2Entry( ql_web_bridge_t *bridge, int index, char *buffer, int bufferSize );
static int QLWebBridge_GetLabelList1Entry( ql_web_bridge_t *bridge, int index, char *buffer, int bufferSize );
static void QLWebBridge_ActivateAdvert( ql_web_bridge_t *bridge, int cellId );

static const ql_web_bridge_vtbl_t cl_webBridgeVtbl = {
	NULL,
	NULL,
	QLWebBridge_SetActiveAdvert,
	QLWebBridge_SetAppActivation,
	QLWebBridge_SetFrameTime,
	QLWebBridge_UpdateViewParameters,
	QLWebBridge_SetVisibilityTraceCallback,
	QLWebBridge_Reserved1FC0,
	QLWebBridge_SetMapPath,
	QLWebBridge_InitCGame,
	QLWebBridge_ShutdownCGame,
	QLWebBridge_SetClientStateFlags,
	NULL,
	NULL,
	QLWebBridge_GetCellDisplayState,
	QLWebBridge_GetCellLabel,
	QLWebBridge_Reserved21C0,
	QLWebBridge_InitUI,
	QLWebBridge_GetLabelList2Count,
	QLWebBridge_GetLabelList1Count,
	QLWebBridge_SetupAdvertCellShader,
	QLWebBridge_SetupUIAdvertCellShader,
	QLWebBridge_RefreshAdvertCellShader,
	QLWebBridge_RefreshUIAdvertCellShader,
	QLWebBridge_GetLabelList2Entry,
	QLWebBridge_GetLabelList1Entry,
	QLWebBridge_ActivateAdvert
};

static ql_web_bridge_t cl_webBridge = {
	&cl_webBridgeVtbl,
	&cl_advertisementBridge,
	&cl_webHost,
	NULL,
	0,
	""
};

static void CL_Web_ClearSessionState( void );
static void CL_WebHost_ClearSurfaceImage( void );
static void CL_WebHost_ClearCursorOverride( void );
static void CL_WebHost_ResolveSessionPath( char *buffer, size_t bufferSize );
static qboolean QLDialogHandler_OnShowFileChooser( void );
static int QLWebHost_CountRecoveredListenerMappings( void );
static void QLWebView_PublishGameKey( int key );
static void *QLViewHandler_OnChangeCursor( int cursorType );
static void QLViewHandler_OnChangeTooltip( const char *tooltip );
static void QLWebHost_RegisterRuntimeSources( void );
static qboolean QLWebHost_WaitForBootstrapReady( void );
static void QLWebHost_InstallRuntimeListeners( void );
static qboolean QLWebView_WriteSurfacePixels( void );
static qboolean QLWebView_UploadSurfaceImage( void );
static qboolean CL_AwesomiumRuntimeAllowed( void );
static qboolean CL_BrowserRuntimeRequested( void );
static qboolean CL_AwesomiumRuntimeActive( void );
static qboolean CL_BrowserHostServiceAvailable( void );
void CL_Web_StopRefresh_f( void );
void CL_Steam_FormatFriendSummaryJson( const ql_steam_friend_summary_t *summary, char *buffer, size_t bufferSize );

static const clWebMethodBinding_t cl_webMethodBindings[CL_WEB_MAX_QZ_METHODS] = {
	{ "IsPakFilePresent", 0x0055C008u, CL_WEB_METHOD_IS_PAK_FILE_PRESENT, qtrue },
	{ "IsGameRunning", 0x0055C014u, CL_WEB_METHOD_IS_GAME_RUNNING, qtrue },
	{ "SendGameCommand", 0x0055C020u, CL_WEB_METHOD_SEND_GAME_COMMAND, qfalse },
	{ "WriteTextFile", 0x0055C02Cu, CL_WEB_METHOD_WRITE_TEXT_FILE, qfalse },
	{ "GetCvar", 0x0055C038u, CL_WEB_METHOD_GET_CVAR, qtrue },
	{ "SetCvar", 0x0055C044u, CL_WEB_METHOD_SET_CVAR, qtrue },
	{ "ResetCvar", 0x0055C050u, CL_WEB_METHOD_RESET_CVAR, qtrue },
	{ "GetMapList", 0x0055C05Cu, CL_WEB_METHOD_GET_MAP_LIST, qtrue },
	{ "GetFactoryList", 0x0055C068u, CL_WEB_METHOD_GET_FACTORY_LIST, qtrue },
	{ "GetDemoList", 0x0055C074u, CL_WEB_METHOD_GET_DEMO_LIST, qtrue },
	{ "OpenURL", 0x0055C080u, CL_WEB_METHOD_OPEN_URL, qfalse },
	{ "OpenSteamOverlayURL", 0x0055C08Cu, CL_WEB_METHOD_OPEN_STEAM_OVERLAY_URL, qfalse },
	{ "GetClipboardText", 0x0055C098u, CL_WEB_METHOD_GET_CLIPBOARD_TEXT, qtrue },
	{ "SetClipboardText", 0x0055C0A4u, CL_WEB_METHOD_SET_CLIPBOARD_TEXT, qfalse },
	{ "RequestServers", 0x0055C0B0u, CL_WEB_METHOD_REQUEST_SERVERS, qfalse },
	{ "RequestServerDetails", 0x0055C0BCu, CL_WEB_METHOD_REQUEST_SERVER_DETAILS, qfalse },
	{ "RefreshList", 0x0055C0C8u, CL_WEB_METHOD_REFRESH_LIST, qfalse },
	{ "CreateLobby", 0x0055C0D4u, CL_WEB_METHOD_CREATE_LOBBY, qfalse },
	{ "LeaveLobby", 0x0055C0E0u, CL_WEB_METHOD_LEAVE_LOBBY, qfalse },
	{ "JoinLobby", 0x0055C0ECu, CL_WEB_METHOD_JOIN_LOBBY, qfalse },
	{ "SetLobbyServer", 0x0055C0F8u, CL_WEB_METHOD_SET_LOBBY_SERVER, qfalse },
	{ "ShowInviteOverlay", 0x0055C104u, CL_WEB_METHOD_SHOW_INVITE_OVERLAY, qfalse },
	{ "SayLobby", 0x0055C110u, CL_WEB_METHOD_SAY_LOBBY, qfalse },
	{ "RequestUserStats", 0x0055C11Cu, CL_WEB_METHOD_REQUEST_USER_STATS, qfalse },
	{ "GetFriendList", 0x0055C128u, CL_WEB_METHOD_GET_FRIEND_LIST, qtrue },
	{ "ActivateGameOverlayToUser", 0x0055C134u, CL_WEB_METHOD_ACTIVATE_GAME_OVERLAY_TO_USER, qfalse },
	{ "Invite", 0x0055C140u, CL_WEB_METHOD_INVITE, qfalse },
	{ "FileExists", 0x0055C14Cu, CL_WEB_METHOD_FILE_EXISTS, qtrue },
	{ "GetConfig", 0x0055C158u, CL_WEB_METHOD_GET_CONFIG, qtrue },
	{ "GetCursorPosition", 0x0055C164u, CL_WEB_METHOD_GET_CURSOR_POSITION, qtrue },
	{ "GetAllUGC", 0x0055C170u, CL_WEB_METHOD_GET_ALL_UGC, qfalse },
	{ "GetNextKeyDown", 0x0055C17Cu, CL_WEB_METHOD_GET_NEXT_KEY_DOWN, qfalse },
	{ "SetFavoriteServer", 0x0055C188u, CL_WEB_METHOD_SET_FAVORITE_SERVER, qfalse },
	{ "NoOp", 0x0055C194u, CL_WEB_METHOD_NO_OP, qfalse },
	{ NULL, 0u, 0, qfalse }
};

#define CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK "source callback"
#define CL_WEB_LISTENER_SCOPE_NO_ENGINE_CALLBACK "retail no-engine callback"
#define CL_WEB_LISTENER_SCOPE_BUILTIN_FORWARD "Awesomium built-in forward"
#define CL_WEB_LISTENER_SCOPE_COMPATIBILITY_OWNER "bounded compatibility owner"
#define CL_WEB_LISTENER_SCOPE_DESTRUCTOR "retail destructor-owned"

static const clWebListenerCallbackMapping_t cl_webListenerCallbackMappings[] = {
	{ "QLResourceInterceptor", "OnRequest", 0x00547F94u, 0x00u, 0x00434620u, "QLResourceInterceptor_OnRequest", CL_WEB_LISTENER_SCOPE_COMPATIBILITY_OWNER },
	{ "QLResourceInterceptor", "OnFilterNavigation", 0x00547F94u, 0x04u, 0x00434600u, "QLResourceInterceptor_OnFilterNavigation", CL_WEB_LISTENER_SCOPE_COMPATIBILITY_OWNER },
	{ "QLResourceInterceptor", "base/no-engine slot", 0x00547F94u, 0x08u, 0x004317C0u, "QLResourceInterceptor_NoEngineCallback", CL_WEB_LISTENER_SCOPE_NO_ENGINE_CALLBACK },
	{ "QLResourceInterceptor", "destroy", 0x00547F94u, 0x0Cu, 0x004F2A80u, "QLResourceInterceptor_Destroy", CL_WEB_LISTENER_SCOPE_DESTRUCTOR },
	{ "QLDialogHandler", "base/no-engine slot 0", 0x00547FA8u, 0x00u, 0x00431660u, "QLDialogHandler_NoEngineCallback", CL_WEB_LISTENER_SCOPE_NO_ENGINE_CALLBACK },
	{ "QLDialogHandler", "base/no-engine slot 1", 0x00547FA8u, 0x04u, 0x00431660u, "QLDialogHandler_NoEngineCallback", CL_WEB_LISTENER_SCOPE_NO_ENGINE_CALLBACK },
	{ "QLDialogHandler", "OnShowFileChooser", 0x00547FA8u, 0x08u, 0x00431640u, "QLDialogHandler_OnShowFileChooser", CL_WEB_LISTENER_SCOPE_BUILTIN_FORWARD },
	{ "QLDialogHandler", "base/no-engine slot 3", 0x00547FA8u, 0x0Cu, 0x00431660u, "QLDialogHandler_NoEngineCallback", CL_WEB_LISTENER_SCOPE_NO_ENGINE_CALLBACK },
	{ "QLDialogHandler", "destroy", 0x00547FA8u, 0x10u, 0x004F2AB0u, "QLDialogHandler_Destroy", CL_WEB_LISTENER_SCOPE_DESTRUCTOR },
	{ "QLViewHandler", "base/no-engine slot 0", 0x00547FC0u, 0x00u, 0x00431660u, "QLViewHandler_NoEngineCallback", CL_WEB_LISTENER_SCOPE_NO_ENGINE_CALLBACK },
	{ "QLViewHandler", "base/no-engine slot 1", 0x00547FC0u, 0x04u, 0x00431660u, "QLViewHandler_NoEngineCallback", CL_WEB_LISTENER_SCOPE_NO_ENGINE_CALLBACK },
	{ "QLViewHandler", "OnChangeTooltip", 0x00547FC0u, 0x08u, 0x00434450u, "QLViewHandler_OnChangeTooltip", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },
	{ "QLViewHandler", "base/no-engine slot 3", 0x00547FC0u, 0x0Cu, 0x00431660u, "QLViewHandler_NoEngineCallback", CL_WEB_LISTENER_SCOPE_NO_ENGINE_CALLBACK },
	{ "QLViewHandler", "OnChangeCursor", 0x00547FC0u, 0x10u, 0x00431670u, "QLViewHandler_OnChangeCursor", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },
	{ "QLViewHandler", "base/no-engine slot 5", 0x00547FC0u, 0x14u, 0x00431660u, "QLViewHandler_NoEngineCallback", CL_WEB_LISTENER_SCOPE_NO_ENGINE_CALLBACK },
	{ "QLViewHandler", "OnAddConsoleMessage", 0x00547FC0u, 0x18u, 0x00434520u, "QLViewHandler_OnAddConsoleMessage", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },
	{ "QLViewHandler", "base/no-engine slot 7", 0x00547FC0u, 0x1Cu, 0x004317B0u, "QLViewHandler_NoEngineCallback", CL_WEB_LISTENER_SCOPE_NO_ENGINE_CALLBACK },
	{ "QLViewHandler", "destroy", 0x00547FC0u, 0x20u, 0x004F2AE0u, "QLViewHandler_Destroy", CL_WEB_LISTENER_SCOPE_DESTRUCTOR },
	{ "QLLoadHandler", "OnBeginLoadingFrame", 0x00547FE8u, 0x00u, 0x004317D0u, "QLLoadHandler_OnBeginLoadingFrame", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },
	{ "QLLoadHandler", "OnFailLoadingFrame", 0x00547FE8u, 0x04u, 0x00434AE0u, "QLLoadHandler_OnFailLoadingFrame", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },
	{ "QLLoadHandler", "OnFinishLoadingFrame", 0x00547FE8u, 0x08u, 0x004317E0u, "QLLoadHandler_OnFinishLoadingFrame", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },
	{ "QLLoadHandler", "OnDocumentReady", 0x00547FE8u, 0x0Cu, 0x004317F0u, "QLLoadHandler_OnDocumentReady", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },
	{ "QLLoadHandler", "destroy", 0x00547FE8u, 0x10u, 0x004F2B10u, "QLLoadHandler_Destroy", CL_WEB_LISTENER_SCOPE_DESTRUCTOR },
	{ "QLJSHandler", "OnMethodCall", 0x00548010u, 0x00u, 0x00431E50u, "QLJSHandler_OnMethodCall", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },
	{ "QLJSHandler", "OnMethodCallWithReturnValue", 0x00548010u, 0x04u, 0x004328B0u, "QLJSHandler_OnMethodCallWithReturnValue", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },
	{ "QLJSHandler", "destroy", 0x00548010u, 0x08u, 0x004F23B0u, "QLJSHandler_Destroy", CL_WEB_LISTENER_SCOPE_DESTRUCTOR },
	{ NULL, NULL, 0u, 0u, 0u, NULL, NULL }
};

#undef CL_WEB_LISTENER_SCOPE_DESTRUCTOR
#undef CL_WEB_LISTENER_SCOPE_COMPATIBILITY_OWNER
#undef CL_WEB_LISTENER_SCOPE_BUILTIN_FORWARD
#undef CL_WEB_LISTENER_SCOPE_NO_ENGINE_CALLBACK
#undef CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK

/*
=============
CL_WebHost_JsonEscape
=============
*/
static void CL_WebHost_JsonEscape( const char *value, char *buffer, size_t bufferSize ) {
	const char	*cursor;
	char		*out;
	char		*limit;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !value ) {
		return;
	}

	out = buffer;
	limit = buffer + bufferSize - 1;
	for ( cursor = value; *cursor && out < limit; ++cursor ) {
		unsigned char ch;

		ch = (unsigned char)*cursor;
		if ( ch == '\\' || ch == '"' ) {
			if ( out + 2 > limit ) {
				break;
			}
			*out++ = '\\';
			*out++ = (char)ch;
			continue;
		}

		if ( ch == '\n' || ch == '\r' || ch == '\t' ) {
			if ( out + 2 > limit ) {
				break;
			}
			*out++ = '\\';
			*out++ = ( ch == '\n' ) ? 'n' : ( ch == '\r' ) ? 'r' : 't';
			continue;
		}

		if ( ch < 0x20 ) {
			continue;
		}

		*out++ = (char)ch;
	}

	*out = '\0';
}

/*
=============
CL_WebHost_AppendJsonEscaped
=============
*/
static void CL_WebHost_AppendJsonEscaped( char *buffer, size_t bufferSize, const char *value ) {
	char escaped[MAX_STRING_CHARS * 2];

	CL_WebHost_JsonEscape( value ? value : "", escaped, sizeof( escaped ) );
	Q_strcat( buffer, bufferSize, escaped );
}

/*
=============
CL_WebHost_BeginJsonItem
=============
*/
static void CL_WebHost_BeginJsonItem( clWebJsonBuilder_t *builder ) {
	if ( !builder || !builder->buffer ) {
		return;
	}

	if ( builder->count > 0 ) {
		Q_strcat( builder->buffer, builder->bufferSize, "," );
	}
	builder->count++;
}

/*
=============
CL_WebHost_FormatSteamId
=============
*/
static void CL_WebHost_FormatSteamId( uint32_t idLow, uint32_t idHigh, char *buffer, size_t bufferSize ) {
	unsigned long long value;

	value = ( (unsigned long long)idHigh << 32 ) | idLow;
	Com_sprintf( buffer, bufferSize, "%llu", value );
}

/*
=============
CL_WebHost_NormalizeHash
=============
*/
static void CL_WebHost_NormalizeHash( const char *hash, char *buffer, size_t bufferSize ) {
	const char	*cursor;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	cursor = hash ? hash : "";
	while ( *cursor == '#' || *cursor == ' ' || *cursor == '\t' || *cursor == '\r' || *cursor == '\n' ) {
		cursor++;
	}

	Q_strncpyz( buffer, cursor, bufferSize );
}

/*
=============
CL_WebHost_BuildCurrentURL
=============
*/
static void CL_WebHost_BuildCurrentURL( const char *hash, char *buffer, size_t bufferSize ) {
	char normalizedHash[MAX_STRING_CHARS];

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	CL_WebHost_NormalizeHash( hash, normalizedHash, sizeof( normalizedHash ) );
	if ( normalizedHash[0] ) {
		Com_sprintf( buffer, bufferSize, "%s#%s", CL_WEB_DEFAULT_URL, normalizedHash );
		return;
	}

	Q_strncpyz( buffer, CL_WEB_DEFAULT_URL, bufferSize );
}

/*
=============
CL_GetWebHostModeLabel

Returns the overall online-services mode label used by the retained web host.
=============
*/
static const char *CL_GetWebHostModeLabel( void ) {
	return QL_GetOnlineServicesModeLabel();
}

/*
=============
CL_GetWebHostPolicyLabel

Returns the overall online-services policy label used by the retained web host.
=============
*/
static const char *CL_GetWebHostPolicyLabel( void ) {
	return QL_GetOnlineServicesPolicyLabel();
}

/*
=============
CL_GetWebHostMatchmakingServiceDescriptor

Returns the current platform-service descriptor for web-host social exports.
=============
*/
static const ql_platform_feature_descriptor *CL_GetWebHostMatchmakingServiceDescriptor( void ) {
	const ql_platform_service_table *services = QL_GetPlatformServices();

	if ( !services ) {
		return NULL;
	}

	return &services->matchmaking;
}

/*
=============
CL_GetWebHostMatchmakingProviderLabel

Returns the human-readable provider label for web-host social exports.
=============
*/
static const char *CL_GetWebHostMatchmakingProviderLabel( void ) {
	const ql_platform_feature_descriptor *descriptor = CL_GetWebHostMatchmakingServiceDescriptor();

	if ( !descriptor || !descriptor->provider ) {
		return "Unavailable";
	}

	return descriptor->provider;
}

/*
=============
CL_GetWebHostMatchmakingPolicyLabel

Returns the short compatibility policy label for web-host social exports.
=============
*/
static const char *CL_GetWebHostMatchmakingPolicyLabel( void ) {
	return QL_DescribePlatformFeaturePolicy( CL_GetWebHostMatchmakingServiceDescriptor() );
}

/*
=============
CL_GetWebHostWorkshopServiceDescriptor

Returns the current platform-service descriptor for web-host UGC exports.
=============
*/
static const ql_platform_feature_descriptor *CL_GetWebHostWorkshopServiceDescriptor( void ) {
	const ql_platform_service_table *services = QL_GetPlatformServices();

	if ( !services ) {
		return NULL;
	}

	return &services->workshop;
}

/*
=============
CL_GetWebHostWorkshopProviderLabel

Returns the human-readable provider label for web-host UGC exports.
=============
*/
static const char *CL_GetWebHostWorkshopProviderLabel( void ) {
	const ql_platform_feature_descriptor *descriptor = CL_GetWebHostWorkshopServiceDescriptor();

	if ( !descriptor || !descriptor->provider ) {
		return "Unavailable";
	}

	return descriptor->provider;
}

/*
=============
CL_GetWebHostWorkshopPolicyLabel

Returns the short compatibility policy label for web-host UGC exports.
=============
*/
static const char *CL_GetWebHostWorkshopPolicyLabel( void ) {
	return QL_DescribePlatformFeaturePolicy( CL_GetWebHostWorkshopServiceDescriptor() );
}

/*
=============
CL_LogWebHostMatchmakingExportLifecycle

Publishes provider-aware diagnostics whenever the retained web-host social
export lane falls back under the compatibility policy.
=============
*/
static void CL_LogWebHostMatchmakingExportLifecycle( const char *stage, const char *reason ) {
	Com_DPrintf( "Web host matchmaking %s: %s (%s [%s])\n",
		stage ? stage : "export",
		reason ? reason : "Steam social export unavailable for current compatibility lane",
		CL_GetWebHostMatchmakingProviderLabel(),
		CL_GetWebHostMatchmakingPolicyLabel() );
}

/*
=============
CL_LogWebHostWorkshopExportLifecycle

Publishes provider-aware diagnostics whenever the retained web-host UGC export
lane falls back under the compatibility policy.
=============
*/
static void CL_LogWebHostWorkshopExportLifecycle( const char *stage, const char *reason ) {
	Com_DPrintf( "Web host workshop %s: %s (%s [%s])\n",
		stage ? stage : "export",
		reason ? reason : "Steam UGC export unavailable for current compatibility lane",
		CL_GetWebHostWorkshopProviderLabel(),
		CL_GetWebHostWorkshopPolicyLabel() );
}

/*
=============
CL_WebHost_HasSteamIdentity

Returns qtrue when the retained web host can safely query Steam-backed social
and UGC data for the current session.
=============
*/
static qboolean CL_WebHost_HasSteamIdentity( void ) {
	if ( !CL_SteamServicesEnabled() ) {
		return qfalse;
	}

	if ( !SteamClient_IsInitialized() ) {
		SteamClient_InitForFilesystem();
	}

	return SteamClient_GetSteamID() != 0ull ? qtrue : qfalse;
}

/*
=============
CL_WebHost_RefreshBootstrapProperties
=============
*/
static void CL_WebHost_RefreshBootstrapProperties( void ) {
	unsigned long long steamId;
	char playerName[MAX_NAME_LENGTH];

	cl_webHost.appId = QL_Steamworks_GetAppID();
	cl_webHost.steamIdLow = 0u;
	cl_webHost.steamIdHigh = 0u;
	if ( CL_SteamServicesEnabled() && !SteamClient_IsInitialized() ) {
		SteamClient_InitForFilesystem();
	}
	steamId = SteamClient_GetSteamID();
	cl_webHost.steamIdLow = (uint32_t)( steamId & 0xffffffffull );
	cl_webHost.steamIdHigh = (uint32_t)( steamId >> 32 );

	playerName[0] = '\0';
	if ( !QL_Steamworks_GetPersonaName( playerName, sizeof( playerName ) ) || !playerName[0] ) {
		Cvar_VariableStringBuffer( "name", playerName, sizeof( playerName ) );
	}
	Q_strncpyz( cl_webHost.playerName, playerName, sizeof( cl_webHost.playerName ) );
}

/*
=============
CL_WebHost_ResetRuntime
=============
*/
static void CL_WebHost_ResetRuntime( qboolean clearVisibility ) {
	CL_WebHost_ClearCursorOverride();
	CL_WebHost_ClearSurfaceImage();
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		CL_Awesomium_Shutdown();
	}
#endif
	cl_webHost.coreInitialised = qfalse;
	cl_webHost.sessionInitialised = qfalse;
	cl_webHost.viewInitialised = qfalse;
	cl_webHost.bootstrapReady = qfalse;
	cl_webHost.documentReady = qfalse;
	cl_webHost.loadingDocument = qfalse;
	cl_webHost.loadFailed = qfalse;
	cl_webHost.dataPakSourceInstalled = qfalse;
	cl_webHost.steamDataSourceInstalled = qfalse;
	cl_webHost.resourceInterceptorInstalled = qfalse;
	cl_webHost.jsMethodHandlerInstalled = qfalse;
	cl_webHost.dialogHandlerInstalled = qfalse;
	cl_webHost.viewHandlerInstalled = qfalse;
	cl_webHost.loadHandlerInstalled = qfalse;
	cl_webHost.liveAwesomium = qfalse;
	cl_webHost.windowObjectBound = qfalse;
	cl_webHost.qzInstanceBound = qfalse;
	cl_webHost.browserActive = qfalse;
	cls.keyCatchers &= ~KEYCATCH_BROWSER;
	cl_webHost.refreshStopped = qfalse;
	cl_webHost.keyCaptureArmed = qfalse;
	cl_webHost.focused = qfalse;
	cl_webHost.cursorPositionValid = qfalse;
	cl_webHost.viewWidth = 0;
	cl_webHost.viewHeight = 0;
	cl_webHost.surfaceContentWidth = 0;
	cl_webHost.surfaceContentHeight = 0;
	cl_webHost.surfaceWidth = 0;
	cl_webHost.surfaceHeight = 0;
	cl_webHost.cursorX = 0;
	cl_webHost.cursorY = 0;
	cl_webHost.frameSequence = 0;
	cl_webHost.nextConfigSyncFrame = 0;
	cl_webHost.nextMapCatalogSyncFrame = 0;
	cl_webHost.nextFactoryCatalogSyncFrame = 0;
	cl_webHost.nextNativeRequestPollFrame = 0;
	cl_webHost.bootstrapAttemptCount = 0;
	cl_webHost.configSynced = qfalse;
	cl_webHost.mapCatalogSynced = qfalse;
	cl_webHost.factoryCatalogSynced = qfalse;
	cl_webHost.cvarMappingCount = QLWebHost_CountRecoveredWebCvarMappings();
	cl_webHost.loadedDocumentScriptCount = 0;
	cl_webHost.executedDocumentScriptCount = 0;
	cl_webHost.failedDocumentScriptCount = 0;
	cl_webHost.liveSurfaceMissingFrames = 0;
	cl_webHost.surfaceUploadWidth = 0;
	cl_webHost.surfaceUploadHeight = 0;
	cl_webHost.surfaceShader = 0;
	cl_webHost.surfaceHasVisiblePixels = qfalse;
	cl_webHost.surfaceHasUiContent = qfalse;
	cl_webHost.surfacePresented = qfalse;
	cl_webHost.currentUrl[0] = '\0';
	cl_webHost.currentDocument[0] = '\0';
	cl_webHost.pendingHash[0] = '\0';
	cl_webHost.tooltip[0] = '\0';
	cl_webHost.sessionPath[0] = '\0';
	cl_webHost.surfaceImageName[0] = '\0';
	cl_webHost.surfaceShaderName[0] = '\0';

	if ( clearVisibility ) {
		cl_webHost.browserVisible = qfalse;
	}
}

/*
=============
CL_WebHost_ClearSurfaceImage
=============
*/
static void CL_WebHost_ClearSurfaceImage( void ) {
	if ( cl_webHost.surfaceBuffer ) {
		Z_Free( cl_webHost.surfaceBuffer );
		cl_webHost.surfaceBuffer = NULL;
	}

	cl_webHost.surfaceBufferLength = 0;
	cl_webHost.surfaceShader = 0;
	cl_webHost.surfaceImageInitialised = qfalse;
	cl_webHost.surfaceDirty = qfalse;
	cl_webHost.surfaceHasVisiblePixels = qfalse;
	cl_webHost.surfaceHasUiContent = qfalse;
	cl_webHost.surfacePresented = qfalse;
	cl_webHost.surfaceContentWidth = 0;
	cl_webHost.surfaceContentHeight = 0;
	cl_webHost.surfaceUploadWidth = 0;
	cl_webHost.surfaceUploadHeight = 0;
	cl_webHost.surfaceImageName[0] = '\0';
	cl_webHost.surfaceShaderName[0] = '\0';
}

/*
=============
CL_WebHost_LoadWin32CursorHandle
=============
*/
#if defined( _WIN32 )
static HCURSOR CL_WebHost_LoadWin32CursorHandle( int cursorType ) {
	LPCSTR cursorId;

	switch ( cursorType ) {
		case 1:
			cursorId = IDC_CROSS;
			break;
		case 2:
			cursorId = IDC_HAND;
			break;
		case 3:
			cursorId = IDC_IBEAM;
			break;
		case 4:
			cursorId = IDC_WAIT;
			break;
		case 5:
			cursorId = IDC_HELP;
			break;
		case 7:
			cursorId = IDC_SIZEWE;
			break;
		case 8:
			cursorId = IDC_SIZENS;
			break;
		case 9:
			cursorId = IDC_SIZENESW;
			break;
		case 10:
			cursorId = IDC_SIZENWSE;
			break;
		case 11:
			cursorId = IDC_SIZEALL;
			break;
		case 14:
			cursorId = IDC_NO;
			break;
		default:
			cursorId = IDC_ARROW;
			break;
	}

	return LoadCursorA( NULL, cursorId );
}
#endif

/*
=============
CL_WebHost_ClearCursorOverride
=============
*/
static void CL_WebHost_ClearCursorOverride( void ) {
#if defined( _WIN32 )
	if ( cl_webHost.cursorOverrideActive && cl_webHost.restoreCursorHandle ) {
		SetCursor( cl_webHost.restoreCursorHandle );
	}

	cl_webHost.activeCursorHandle = NULL;
	cl_webHost.restoreCursorHandle = NULL;
	cl_webHost.activeCursorType = 0;
	cl_webHost.cursorOverrideActive = qfalse;
#endif
}

/*
=============
CL_WebHost_ResolveSessionPath
=============
*/
static void CL_WebHost_ResolveSessionPath( char *buffer, size_t bufferSize ) {
	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	Cvar_VariableStringBuffer( "fs_homepath", buffer, bufferSize );
	if ( !buffer[0] ) {
		Q_strncpyz( buffer, ".", bufferSize );
	}
}

/*
=============
QLDialogHandler_OnShowFileChooser

Retail forwards this dialog callback into the active Awesomium WebView rather
than building an engine-side file chooser.
=============
*/
static qboolean QLDialogHandler_OnShowFileChooser( void ) {
	return cl_webHost.liveAwesomium ? qtrue : qfalse;
}

/*
=============
QLWebHost_CountRecoveredListenerMappings
=============
*/
static int QLWebHost_CountRecoveredListenerMappings( void ) {
	int count;
	int i;

	count = 0;
	for ( i = 0; cl_webListenerCallbackMappings[i].listenerName; i++ ) {
		if ( cl_webListenerCallbackMappings[i].retailAddress != 0u ) {
			count++;
		}
	}

	return count;
}

/*
=============
QLJSHandler_LookupMethodBinding
=============
*/
static const clWebMethodBinding_t *QLJSHandler_LookupMethodBinding( const char *methodName ) {
	int i;

	if ( !methodName || !methodName[0] ) {
		return NULL;
	}

	for ( i = 0; i < CL_WEB_MAX_QZ_METHODS && cl_webMethodBindings[i].name; i++ ) {
		if ( !Q_stricmp( cl_webMethodBindings[i].name, methodName ) ) {
			return &cl_webMethodBindings[i];
		}
	}

	return NULL;
}

/*
=============
QLJSHandler_BindQzInstance
=============
*/
static void QLJSHandler_BindQzInstance( void ) {
	int i;

	if ( cl_webHost.qzInstanceBound ) {
		return;
	}

	for ( i = 0; i < CL_WEB_MAX_QZ_METHODS && cl_webMethodBindings[i].name; i++ ) {
		(void)cl_webMethodBindings[i].returnsValue;
	}

	CL_WebHost_RefreshBootstrapProperties();
	cl_webHost.qzInstanceBound = qtrue;
	cl_webHost.windowObjectBound = qtrue;
}

/*
=============
QLWebHost_RegisterRuntimeSources
=============
*/
static void QLWebHost_RegisterRuntimeSources( void ) {
	CL_WebHost_ResolveSessionPath( cl_webHost.sessionPath, sizeof( cl_webHost.sessionPath ) );
	cl_webHost.dataPakSourceInstalled = qtrue;
	cl_webHost.steamDataSourceInstalled = qtrue;
	cl_webHost.resourceInterceptorInstalled = qtrue;
}

/*
=============
QLWebHost_WaitForBootstrapReady
=============
*/
static qboolean QLWebHost_WaitForBootstrapReady( void ) {
	int attempt;

	for ( attempt = 0; attempt < CL_WEB_BOOTSTRAP_MAX_ATTEMPTS; attempt++ ) {
		cl_webHost.bootstrapAttemptCount = attempt + 1;
		if ( cl_webHost.sessionInitialised
			&& cl_webHost.viewInitialised
			&& cl_webHost.dataPakSourceInstalled
			&& cl_webHost.steamDataSourceInstalled
			&& cl_webHost.resourceInterceptorInstalled
			&& cl_webHost.jsMethodHandlerInstalled ) {
			cl_webHost.bootstrapReady = qtrue;
			return qtrue;
		}

		NET_Sleep( CL_WEB_BOOTSTRAP_SLEEP_MSEC );
	}

	return qfalse;
}

/*
=============
QLWebHost_InstallRuntimeListeners
=============
*/
static void QLWebHost_InstallRuntimeListeners( void ) {
	cl_webHost.listenerCallbackMappingCount = QLWebHost_CountRecoveredListenerMappings();
	cl_webHost.dialogHandlerInstalled = qtrue;
	cl_webHost.viewHandlerInstalled = qtrue;
	cl_webHost.loadHandlerInstalled = qtrue;
}

/*
=============
CL_WebHost_NormalizeDocumentPath
=============
*/
static qboolean CL_WebHost_NormalizeDocumentPath( const char *url, char *buffer, size_t bufferSize ) {
	const char	*pathStart;
	const char	*separator;
	size_t		index;

	if ( !url || !url[0] || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	pathStart = url;
	separator = strstr( url, "://" );
	if ( separator ) {
		pathStart = separator + 3;
		separator = strchr( pathStart, '/' );
		if ( separator ) {
			pathStart = separator + 1;
		}
	}

	while ( *pathStart == '/' || *pathStart == '\\' ) {
		pathStart++;
	}

	for ( index = 0; pathStart[index] && pathStart[index] != '?' && pathStart[index] != '#'; index++ ) {
		char ch;

		if ( index >= bufferSize - 1 ) {
			break;
		}

		ch = pathStart[index];
		buffer[index] = ( ch == '\\' ) ? '/' : ch;
	}
	buffer[index] = '\0';

	if ( !buffer[0] || strstr( buffer, ".." ) || strstr( buffer, "::" ) || strchr( buffer, ':' ) ) {
		return qfalse;
	}

	Q_strlwr( buffer );
	return qtrue;
}

/*
=============
QLLoadHandler_OnBeginLoadingFrame
=============
*/
static void QLLoadHandler_OnBeginLoadingFrame( void ) {
	cl_webHost.loadingDocument = qtrue;
	cl_webHost.loadFailed = qfalse;
	cl_webHost.documentReady = qfalse;
	cl_webHost.surfaceDirty = qtrue;
	if ( cl_webHost.tooltip[0] && cl_webHost.windowObjectBound ) {
		QLViewHandler_OnChangeTooltip( "" );
	} else {
		cl_webHost.tooltip[0] = '\0';
	}
	cl_webHost.windowObjectBound = qfalse;
	cl_webHost.qzInstanceBound = qfalse;
	cl_webHost.currentDocument[0] = '\0';
}

/*
=============
QLLoadHandler_OnFinishLoadingFrame
=============
*/
static void QLLoadHandler_OnFinishLoadingFrame( void ) {
	cl_webHost.loadingDocument = qfalse;
	cl_webHost.surfaceDirty = qtrue;
}

/*
=============
QLLoadHandler_ExecuteDocumentScript

Executes one recovered launcher script in the live Awesomium view. Retail calls
WebView::ExecuteJavascript for each `js/*.js` entry before `web.object.ready`.
=============
*/
static void QLLoadHandler_ExecuteDocumentScript( const char *scriptPath, char *scriptBuffer, int scriptLength ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( !cl_webHost.liveAwesomium || !scriptBuffer || scriptLength <= 0 ) {
		return;
	}

	scriptBuffer[scriptLength] = '\0';
	if ( CL_Awesomium_ExecuteJavascript( scriptBuffer, "" ) ) {
		cl_webHost.executedDocumentScriptCount++;
	} else {
		cl_webHost.failedDocumentScriptCount++;
		Com_DPrintf( "Awesomium failed to execute document script %s: %s\n", scriptPath ? scriptPath : "", CL_Awesomium_LastError() );
	}
#else
	(void)scriptPath;
	(void)scriptBuffer;
	(void)scriptLength;
#endif
}

/*
=============
CL_WebHost_PrimeLauncherDocument
=============
*/
static qboolean CL_WebHost_PrimeLauncherDocument( const char *url ) {
	void	*buffer;
	int		length;
	char	documentPath[MAX_QPATH];

	buffer = NULL;
	length = 0;

	if ( !url || !url[0] ) {
		return qfalse;
	}

	if ( !CL_LauncherRequestData( url, &buffer, &length ) ) {
		return qfalse;
	}

	if ( buffer ) {
		Z_Free( buffer );
	}

	if ( CL_WebHost_NormalizeDocumentPath( url, documentPath, sizeof( documentPath ) ) ) {
		Q_strncpyz( cl_webHost.currentDocument, documentPath, sizeof( cl_webHost.currentDocument ) );
	}

	return qtrue;
}

/*
=============
QLLoadHandler_LoadDocumentScripts

Stages the retail launcher js/* bundle through the retained web.pak and
filesystem bridge before the browser object is marked ready.
=============
*/
static void QLLoadHandler_LoadDocumentScripts( void ) {
	char	fileList[CL_WEB_LAUNCHER_SCRIPT_LIST_BUFFER];
	char	scriptPath[MAX_QPATH];
	char	*cursor;
	int	count;
	int	i;

	count = CL_WebPak_GetFileList( "js", ".js", fileList, sizeof( fileList ) );
	cursor = fileList;

	for ( i = 0; i < count && *cursor; i++ ) {
		char	*scriptBuffer;
		int	scriptLength;

		scriptBuffer = NULL;
		scriptLength = 0;

		Com_sprintf( scriptPath, sizeof( scriptPath ), "js/%s", cursor );
		if ( CL_LauncherRequestData( scriptPath, (void **)&scriptBuffer, &scriptLength ) && scriptBuffer ) {
			cl_webHost.loadedDocumentScriptCount++;
			QLLoadHandler_ExecuteDocumentScript( scriptPath, scriptBuffer, scriptLength );
			Z_Free( scriptBuffer );
		}

		cursor += strlen( cursor ) + 1;
	}
}

/*
=============
QLLoadHandler_OnDocumentReady
=============
*/
static void QLLoadHandler_OnDocumentReady( void ) {
	QLLoadHandler_LoadDocumentScripts();
	QLJSHandler_BindQzInstance();
	cl_webHost.documentReady = qtrue;
	cl_webHost.surfaceDirty = qtrue;
	QLViewHandler_OnChangeCursor( 0 );
	CL_WebView_PublishEvent( "web.object.ready", NULL );
}

/*
=============
QLLoadHandler_PollLiveDocumentReady

Projects the retail load-handler completion callback onto the source adapter's
frame pump while the native listener object remains mapped rather than rebuilt.
=============
*/
static void QLLoadHandler_PollLiveDocumentReady( void ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( !cl_webHost.liveAwesomium || !cl_webHost.loadingDocument || cl_webHost.documentReady ) {
		return;
	}
	if ( CL_Awesomium_IsLoading() ) {
		return;
	}

	QLLoadHandler_OnFinishLoadingFrame();
	QLLoadHandler_OnDocumentReady();
#endif
}

/*
=============
QLLoadHandler_OnFailLoadingFrame
=============
*/
static void QLLoadHandler_OnFailLoadingFrame( const char *url ) {
	char message[MAX_STRING_CHARS];

	cl_webHost.loadingDocument = qfalse;
	cl_webHost.loadFailed = qtrue;
	cl_webHost.documentReady = qfalse;
	if ( cl_webHost.tooltip[0] && cl_webHost.windowObjectBound ) {
		QLViewHandler_OnChangeTooltip( "" );
	}
	cl_webHost.windowObjectBound = qfalse;
	cl_webHost.qzInstanceBound = qfalse;
	cl_webHost.browserVisible = qfalse;
	cl_webHost.browserActive = qfalse;
	cl_webHost.focused = qfalse;
	cl_webHost.currentDocument[0] = '\0';
	cl_webHost.tooltip[0] = '\0';
	cl_webHost.surfaceDirty = qtrue;
	cl_webBrowserVisible = qfalse;
	CL_WebHost_ClearCursorOverride();

	Com_sprintf( message, sizeof( message ), "Failed to load QUAKE LIVE site... %s", url ? url : CL_WEB_DEFAULT_URL );
	Cvar_Set( "web_browserActive", "0" );
	Cvar_Set( "com_errorMessage", message );
	Com_DPrintf( "%s\n", message );
}

/*
=============
QLViewHandler_OnChangeCursor
=============
*/
static void *QLViewHandler_OnChangeCursor( int cursorType ) {
#if defined( _WIN32 )
	HCURSOR cursorHandle;

	if ( !cl_webHost.cursorOverrideActive ) {
		cl_webHost.restoreCursorHandle = GetCursor();
	}

	cursorHandle = CL_WebHost_LoadWin32CursorHandle( cursorType );
	if ( !cursorHandle ) {
		cursorHandle = LoadCursorA( NULL, IDC_ARROW );
	}

	cl_webHost.activeCursorType = cursorType;
	cl_webHost.activeCursorHandle = cursorHandle;
	cl_webHost.cursorOverrideActive = cursorHandle ? qtrue : qfalse;
	if ( cl_webHost.cursorOverrideActive ) {
		SetCursor( cl_webHost.activeCursorHandle );
	}

	return cl_webHost.activeCursorHandle;
#else
	(void)cursorType;
	return NULL;
#endif
}

/*
=============
QLViewHandler_OnChangeTooltip
=============
*/
static void QLViewHandler_OnChangeTooltip( const char *tooltip ) {
	char escapedTooltip[MAX_QPATH * 2];
	char payload[MAX_STRING_CHARS];

	Q_strncpyz( cl_webHost.tooltip, tooltip ? tooltip : "", sizeof( cl_webHost.tooltip ) );
	CL_WebHost_JsonEscape( cl_webHost.tooltip, escapedTooltip, sizeof( escapedTooltip ) );
	Com_sprintf( payload, sizeof( payload ), "{\"tooltip\":\"%s\"}", escapedTooltip );
	CL_WebView_PublishEvent( "web.tooltip", payload );
}

/*
=============
QLViewHandler_OnAddConsoleMessage
=============
*/
static void QLViewHandler_OnAddConsoleMessage( const char *source, int line, const char *message ) {
	if ( !CL_WebCvarIntegerValue( cl_webConsole, "web_console" ) ) {
		return;
	}

	Com_Printf( "%s:%i: %s\n", source ? source : "", line, message ? message : "" );
}

/*
=============
QLWebView_SetLocationHash
=============
*/
static qboolean QLWebView_SetLocationHash( const char *hash ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	char escapedHash[MAX_STRING_CHARS * 2];
	char script[MAX_STRING_CHARS * 3];
#endif

	CL_WebHost_NormalizeHash( hash, cl_webHost.pendingHash, sizeof( cl_webHost.pendingHash ) );
	CL_WebHost_BuildCurrentURL( cl_webHost.pendingHash, cl_webHost.currentUrl, sizeof( cl_webHost.currentUrl ) );

#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		CL_WebHost_JsonEscape( cl_webHost.pendingHash, escapedHash, sizeof( escapedHash ) );
		Com_sprintf(
			script,
			sizeof( script ),
			"(function(){var h=\"%s\";if(window.location.hash.replace(/^#/,\"\")!==h){window.location.hash=h;}if(window.main_hook_v2){window.main_hook_v2();}})();",
			escapedHash
		);
		if ( !CL_Awesomium_ExecuteJavascript( script, "" ) ) {
			return qfalse;
		}
	}
#endif

	return qtrue;
}

/*
=============
QLWebView_NextPowerOfTwo
=============
*/
static int QLWebView_NextPowerOfTwo( int value ) {
	int result;

	if ( value <= 0 ) {
		return 0;
	}

	for ( result = 1; result < value; result <<= 1 ) {
		/* loop until result is at least value */
	}

	return result;
}

/*
=============
QLWebView_MapCursorCoordinate
=============
*/
static int QLWebView_MapCursorCoordinate( int coordinate, int sourceDimension, int targetDimension ) {
	int clampedCoordinate;
	double mappedCoordinate;

	clampedCoordinate = coordinate;
	if ( clampedCoordinate < 0 ) {
		clampedCoordinate = 0;
	}

	if ( sourceDimension > 0 && clampedCoordinate > sourceDimension ) {
		clampedCoordinate = sourceDimension;
	}

	if ( targetDimension <= 0 ) {
		targetDimension = sourceDimension;
	}
	if ( targetDimension <= 0 || sourceDimension <= 0 ) {
		return clampedCoordinate;
	}

	mappedCoordinate = ( (double)clampedCoordinate / (double)sourceDimension ) * (double)targetDimension;
	clampedCoordinate = (int)( mappedCoordinate + 0.5 );
	if ( clampedCoordinate < 0 ) {
		clampedCoordinate = 0;
	} else if ( clampedCoordinate > targetDimension ) {
		clampedCoordinate = targetDimension;
	}

	return clampedCoordinate;
}

/*
=============
QLWebView_InjectMappedMouseMove
=============
*/
static void QLWebView_InjectMappedMouseMove( int x, int y ) {
	int cursorX;
	int cursorY;
	int cursorWidth;
	int cursorHeight;

	cursorX = x;
	cursorY = y;
	cursorWidth = cl_webHost.surfaceContentWidth > 0 ? cl_webHost.surfaceContentWidth : cl_webHost.viewWidth;
	cursorHeight = cl_webHost.surfaceContentHeight > 0 ? cl_webHost.surfaceContentHeight : cl_webHost.viewHeight;

	if ( cursorX < 0 ) {
		cursorX = 0;
	} else if ( cursorWidth > 0 && cursorX > cursorWidth ) {
		cursorX = cursorWidth;
	}

	if ( cursorY < 0 ) {
		cursorY = 0;
	} else if ( cursorHeight > 0 && cursorY > cursorHeight ) {
		cursorY = cursorHeight;
	}

	cl_webHost.cursorX = cursorX;
	cl_webHost.cursorY = cursorY;
	cl_webHost.cursorPositionValid = qtrue;
	cl_webHost.focused = qtrue;
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		CL_Awesomium_InjectMouseMove( cursorX, cursorY );
	}
#endif
}

/*
=============
QLWebView_Resize
=============
*/
static void QLWebView_Resize( int width, int height ) {
	cl_webHost.viewWidth = width;
	cl_webHost.viewHeight = height;
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		CL_Awesomium_Resize( width, height );
	}
#endif
}

/*
=============
QLWebView_RebuildSurfaceImage
=============
*/
static void QLWebView_RebuildSurfaceImage( void ) {
	int contentWidth;
	int contentHeight;

	contentWidth = cl_webHost.viewWidth;
	contentHeight = cl_webHost.viewHeight;
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		int awesomiumWidth;
		int awesomiumHeight;

		CL_Awesomium_Resize( cl_webHost.viewWidth, cl_webHost.viewHeight );
		CL_Awesomium_Update();
		awesomiumWidth = CL_Awesomium_SurfaceWidth();
		awesomiumHeight = CL_Awesomium_SurfaceHeight();
		if ( awesomiumWidth > 0 ) {
			contentWidth = awesomiumWidth;
		}
		if ( awesomiumHeight > 0 ) {
			contentHeight = awesomiumHeight;
		}
	}
#endif
	cl_webHost.surfaceContentWidth = contentWidth;
	cl_webHost.surfaceContentHeight = contentHeight;
	cl_webHost.surfaceWidth = QLWebView_NextPowerOfTwo( contentWidth );
	cl_webHost.surfaceHeight = QLWebView_NextPowerOfTwo( contentHeight );
	cl_webHost.surfaceDirty = qtrue;
	QLWebView_UploadSurfaceImage();
}

/*
=============
QLWebView_MakeAwesomiumSurfaceOpaque
=============
*/
static void QLWebView_MakeAwesomiumSurfaceOpaque( byte *pixels, int surfaceWidth, int surfaceHeight, int contentWidth, int contentHeight ) {
	int x;
	int y;
	int copyWidth;
	int copyHeight;

	if ( !pixels || surfaceWidth <= 0 || surfaceHeight <= 0 ) {
		return;
	}

	copyWidth = contentWidth;
	copyHeight = contentHeight;
	if ( copyWidth <= 0 || copyWidth > surfaceWidth ) {
		copyWidth = surfaceWidth;
	}
	if ( copyHeight <= 0 || copyHeight > surfaceHeight ) {
		copyHeight = surfaceHeight;
	}

	for ( y = 0; y < copyHeight; y++ ) {
		byte *row;

		row = pixels + y * surfaceWidth * 4;
		for ( x = 0; x < copyWidth; x++ ) {
			row[x * 4 + 3] = 0xff;
		}
	}
}

/*
=============
QLWebView_SurfaceHasVisiblePixels
=============
*/
static qboolean QLWebView_SurfaceHasVisiblePixels( const byte *pixels, int length ) {
	int pixelCount;
	int i;

	if ( !pixels || length < 4 ) {
		return qfalse;
	}

	pixelCount = length / 4;
	for ( i = 0; i < pixelCount; i++ ) {
		int offset = i * 4;

		if ( pixels[offset + 0] || pixels[offset + 1] || pixels[offset + 2] ) {
			return qtrue;
		}
	}

	return qfalse;
}

/*
=============
QLWebView_SurfaceHasUiContent

Filters shell-only Awesomium paints that contain a dark background/cursor but no
usable menu widgets.  The retail host gates the native UI on a completed browser
surface; this source-side guard approximates that completion signal until the
native JSValue callback path is fully reconstructed.
=============
*/
static qboolean QLWebView_SurfaceHasUiContent( const byte *pixels, int surfaceWidth, int surfaceHeight, int contentWidth, int contentHeight ) {
	int x;
	int y;
	int xStep;
	int yStep;
	int sampled;
	int contentPixels;

	if ( !pixels || surfaceWidth <= 0 || surfaceHeight <= 0 ) {
		return qfalse;
	}

	if ( contentWidth <= 0 || contentWidth > surfaceWidth ) {
		contentWidth = surfaceWidth;
	}
	if ( contentHeight <= 0 || contentHeight > surfaceHeight ) {
		contentHeight = surfaceHeight;
	}

	xStep = contentWidth / 200;
	yStep = contentHeight / 120;
	if ( xStep < 4 ) {
		xStep = 4;
	}
	if ( yStep < 4 ) {
		yStep = 4;
	}

	sampled = 0;
	contentPixels = 0;
	for ( y = 0; y < contentHeight; y += yStep ) {
		const byte *row = pixels + y * surfaceWidth * 4;

		for ( x = 0; x < contentWidth; x += xStep ) {
			const byte *pixel = row + x * 4;
			int red = pixel[0];
			int green = pixel[1];
			int blue = pixel[2];
			int minChannel;
			int maxChannel;
			int luma;

			sampled++;
			minChannel = red < green ? red : green;
			if ( blue < minChannel ) {
				minChannel = blue;
			}
			maxChannel = red > green ? red : green;
			if ( blue > maxChannel ) {
				maxChannel = blue;
			}
			luma = ( red * 77 + green * 150 + blue * 29 ) >> 8;
			if ( ( luma >= 160 ) || ( luma >= 96 && maxChannel - minChannel >= 16 ) ) {
				contentPixels++;
			}
		}
	}

	if ( sampled <= 0 ) {
		return qfalse;
	}

	return contentPixels >= 32 && contentPixels * 500 >= sampled ? qtrue : qfalse;
}

/*
=============
QLWebView_WriteSurfacePixels
=============
*/
static qboolean QLWebView_WriteSurfacePixels( void ) {
	int requiredLength;
	int pixelCount;
	int i;
	byte red;
	byte green;
	byte blue;
	byte alpha;

	requiredLength = cl_webHost.surfaceWidth * cl_webHost.surfaceHeight * 4;
	if ( cl_webHost.surfaceWidth <= 0 || cl_webHost.surfaceHeight <= 0 || requiredLength <= 0 ) {
		CL_WebHost_ClearSurfaceImage();
		return qfalse;
	}

	if ( !cl_webHost.surfaceBuffer || cl_webHost.surfaceBufferLength != requiredLength ) {
		if ( cl_webHost.surfaceBuffer ) {
			Z_Free( cl_webHost.surfaceBuffer );
		}

		cl_webHost.surfaceBuffer = Z_Malloc( requiredLength );
		cl_webHost.surfaceBufferLength = requiredLength;
	}

#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		int midOffset;
		qboolean copied;
		qboolean visible;
		qboolean contentful;
		qboolean dirty;
		qboolean loading;
		qboolean crashed;
		int lastError;
		static int liveSurfaceLogCounter;

		dirty = CL_Awesomium_SurfaceDirty();
		copied = CL_Awesomium_CopySurface( cl_webHost.surfaceBuffer, cl_webHost.surfaceWidth, cl_webHost.surfaceHeight, cl_webHost.surfaceWidth * 4 );
		if ( copied ) {
			QLWebView_MakeAwesomiumSurfaceOpaque( cl_webHost.surfaceBuffer, cl_webHost.surfaceWidth, cl_webHost.surfaceHeight, cl_webHost.surfaceContentWidth, cl_webHost.surfaceContentHeight );
		}
		visible = copied && QLWebView_SurfaceHasVisiblePixels( cl_webHost.surfaceBuffer, requiredLength );
		contentful = visible && QLWebView_SurfaceHasUiContent(
			cl_webHost.surfaceBuffer,
			cl_webHost.surfaceWidth,
			cl_webHost.surfaceHeight,
			cl_webHost.surfaceContentWidth,
			cl_webHost.surfaceContentHeight
		);
		loading = CL_Awesomium_IsLoading();
		crashed = CL_Awesomium_IsCrashed();
		lastError = CL_Awesomium_LastErrorCode();
		if ( copied ) {
			if ( !cl_webHost.surfaceHasVisiblePixels && visible ) {
				Com_Printf( "Awesomium surface became visible: copy=%d dirty=%d size=%dx%d content=%dx%d view=%dx%d\n",
					copied, dirty, cl_webHost.surfaceWidth, cl_webHost.surfaceHeight, cl_webHost.surfaceContentWidth, cl_webHost.surfaceContentHeight, cl_webHost.viewWidth, cl_webHost.viewHeight );
			}
			if ( !cl_webHost.surfaceHasUiContent && contentful ) {
				Com_Printf( "Awesomium surface became menu-contentful: size=%dx%d content=%dx%d view=%dx%d\n",
					cl_webHost.surfaceWidth, cl_webHost.surfaceHeight, cl_webHost.surfaceContentWidth, cl_webHost.surfaceContentHeight, cl_webHost.viewWidth, cl_webHost.viewHeight );
			}
			cl_webHost.surfaceHasVisiblePixels = visible;
			cl_webHost.surfaceHasUiContent = contentful;
			if ( contentful ) {
				cl_webHost.liveSurfaceMissingFrames = 0;
			} else {
				cl_webHost.liveSurfaceMissingFrames++;
			}
			return qtrue;
		}

		if ( liveSurfaceLogCounter <= 0 ) {
			midOffset = ( requiredLength / 8 ) * 4;
			if ( midOffset < 0 || midOffset + 3 >= requiredLength ) {
				midOffset = 0;
			}
			Com_Printf( "Awesomium surface not visible: copy=%d dirty=%d loading=%d crashed=%d lastError=%d size=%dx%d content=%dx%d view=%dx%d first=%02x%02x%02x%02x mid=%02x%02x%02x%02x\n",
				copied,
				dirty,
				loading,
				crashed,
				lastError,
				cl_webHost.surfaceWidth,
				cl_webHost.surfaceHeight,
				cl_webHost.surfaceContentWidth,
				cl_webHost.surfaceContentHeight,
				cl_webHost.viewWidth,
				cl_webHost.viewHeight,
				cl_webHost.surfaceBuffer[0],
				cl_webHost.surfaceBuffer[1],
				cl_webHost.surfaceBuffer[2],
				cl_webHost.surfaceBuffer[3],
				cl_webHost.surfaceBuffer[midOffset + 0],
				cl_webHost.surfaceBuffer[midOffset + 1],
				cl_webHost.surfaceBuffer[midOffset + 2],
				cl_webHost.surfaceBuffer[midOffset + 3] );
			liveSurfaceLogCounter = 120;
		} else {
			liveSurfaceLogCounter--;
		}

		cl_webHost.surfaceHasVisiblePixels = qfalse;
		cl_webHost.surfaceHasUiContent = qfalse;
		cl_webHost.liveSurfaceMissingFrames++;
		return qfalse;
	}
#endif

	red = 0x14;
	green = 0x14;
	blue = 0x14;
	alpha = 0xff;

	if ( cl_webHost.loadFailed ) {
		red = 0x6a;
		green = 0x12;
		blue = 0x12;
	} else if ( cl_webHost.loadingDocument ) {
		red = 0x12;
		green = 0x24;
		blue = 0x68;
	} else if ( cl_webHost.documentReady ) {
		red = 0x1f;
		green = 0x1f;
		blue = 0x1f;
	}

	pixelCount = cl_webHost.surfaceWidth * cl_webHost.surfaceHeight;
	for ( i = 0; i < pixelCount; i++ ) {
		int offset = i * 4;

		cl_webHost.surfaceBuffer[offset + 0] = red;
		cl_webHost.surfaceBuffer[offset + 1] = green;
		cl_webHost.surfaceBuffer[offset + 2] = blue;
		cl_webHost.surfaceBuffer[offset + 3] = alpha;
	}

	if ( cl_webHost.surfaceBufferLength >= 16 ) {
		cl_webHost.surfaceBuffer[0] = cl_webHost.dataPakSourceInstalled ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[1] = cl_webHost.steamDataSourceInstalled ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[2] = cl_webHost.resourceInterceptorInstalled ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[3] = 0xff;
		cl_webHost.surfaceBuffer[4] = cl_webHost.jsMethodHandlerInstalled ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[5] = cl_webHost.dialogHandlerInstalled ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[6] = cl_webHost.viewHandlerInstalled ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[7] = 0xff;
		cl_webHost.surfaceBuffer[8] = cl_webHost.loadHandlerInstalled ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[9] = cl_webHost.bootstrapReady ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[10] = cl_webHost.documentReady ? 0xff : 0x00;
		cl_webHost.surfaceBuffer[11] = 0xff;
		cl_webHost.surfaceBuffer[12] = (byte)( cl_webHost.bootstrapAttemptCount & 0xff );
		cl_webHost.surfaceBuffer[13] = 0xff;
		cl_webHost.surfaceBuffer[14] = 0xff;
		cl_webHost.surfaceBuffer[15] = 0xff;
	}

	cl_webHost.surfaceHasVisiblePixels = qtrue;
	cl_webHost.surfaceHasUiContent = qtrue;
	return qtrue;
}

/*
=============
QLWebView_UploadSurfaceImage
=============
*/
static qboolean QLWebView_UploadSurfaceImage( void ) {
	if ( !cl_webHost.viewInitialised || cl_webHost.surfaceWidth <= 0 || cl_webHost.surfaceHeight <= 0 ) {
		return qfalse;
	}

	if ( !QLWebView_WriteSurfacePixels() ) {
		return qfalse;
	}
	if ( !cl_webHost.surfaceBuffer || cl_webHost.surfaceBufferLength <= 0 ) {
		return qfalse;
	}

	if ( !cl_webHost.surfaceImageName[0] ) {
		Q_strncpyz( cl_webHost.surfaceImageName, CL_WEB_SURFACE_IMAGE, sizeof( cl_webHost.surfaceImageName ) );
	}
	if ( !cl_webHost.surfaceShaderName[0] ) {
		Q_strncpyz( cl_webHost.surfaceShaderName, CL_WEB_SURFACE_SHADER, sizeof( cl_webHost.surfaceShaderName ) );
	}

	cl_webHost.surfaceShader = CL_RegisterShaderFromRGBAWithImageName(
		cl_webHost.surfaceShaderName,
		cl_webHost.surfaceImageName,
		cl_webHost.surfaceBuffer,
		cl_webHost.surfaceWidth,
		cl_webHost.surfaceHeight,
		qfalse
	);
	if ( !cl_webHost.surfaceShader ) {
		return qfalse;
	}

	cl_webHost.surfaceUploadWidth = cl_webHost.surfaceWidth;
	cl_webHost.surfaceUploadHeight = cl_webHost.surfaceHeight;
	cl_webHost.surfaceImageInitialised = qtrue;
	cl_webHost.surfaceDirty = qfalse;
	return qtrue;
}

/*
=============
CL_WebHost_MapMouseButton
=============
*/
static int CL_WebHost_MapMouseButton( int key ) {
	switch ( key ) {
		case K_MOUSE1:
			return 0;

		case K_MOUSE2:
			return 2;

		case K_MOUSE3:
			return 1;

		default:
			return -1;
	}
}

/*
=============
QLWebView_InjectMouseMove
=============
*/
static void QLWebView_InjectMouseMove( int x, int y ) {
	if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {
		return;
	}

	QLWebView_InjectMappedMouseMove(
		QLWebView_MapCursorCoordinate( x, cl_webHost.viewWidth, cl_webHost.surfaceContentWidth ),
		QLWebView_MapCursorCoordinate( y, cl_webHost.viewHeight, cl_webHost.surfaceContentHeight )
	);
}

/*
=============
QLWebView_InjectMouseDown
=============
*/
static void QLWebView_InjectMouseDown( int key ) {
	int button;

	if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {
		return;
	}

	button = CL_WebHost_MapMouseButton( key );
	if ( button < 0 ) {
		return;
	}

	if ( cl_webHost.cursorPositionValid ) {
		QLWebView_InjectMappedMouseMove( cl_webHost.cursorX, cl_webHost.cursorY );
	}

#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		CL_Awesomium_InjectMouseDown( button );
	}
#endif
	cl_webHost.focused = qtrue;
}

/*
=============
QLWebView_InjectMouseUp
=============
*/
static void QLWebView_InjectMouseUp( int key ) {
	int button;

	if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {
		return;
	}

	button = CL_WebHost_MapMouseButton( key );
	if ( button < 0 ) {
		return;
	}

#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		CL_Awesomium_InjectMouseUp( button );
	}
#endif
	cl_webHost.focused = qtrue;
}

/*
=============
QLWebView_InjectMouseWheel
=============
*/
static void QLWebView_InjectMouseWheel( int direction ) {
	if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {
		return;
	}

	if ( direction == 0 ) {
		return;
	}

#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		CL_Awesomium_InjectMouseWheel( direction );
	}
#endif
	cl_webHost.focused = qtrue;
}

/*
=============
QLWebView_InjectKeyboardEvent
=============
*/
static void QLWebView_InjectKeyboardEvent( int key, qboolean down ) {
	if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {
		return;
	}

	if ( !down && cl_webHost.keyCaptureArmed ) {
		QLWebView_PublishGameKey( key );
		cl_webHost.keyCaptureArmed = qfalse;
	}

#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		if ( key & K_CHAR_FLAG ) {
			if ( down ) {
				CL_Awesomium_InjectKeyboardEvent( QL_WEB_KEYBOARD_EVENT_CHAR_TYPE, (unsigned int)( key & ~K_CHAR_FLAG ), 0 );
			}
		} else {
			CL_Awesomium_InjectKeyboardEvent(
				down ? QL_WEB_KEYBOARD_EVENT_KEYDOWN_TYPE : QL_WEB_KEYBOARD_EVENT_KEYUP_TYPE,
				(unsigned int)key,
				0 );
		}
	}
#endif

	if ( down ) {
		cl_webHost.focused = qtrue;
	}
}

/*
=============
QLWebView_InjectKeyboardEventFields

Models the Awesomium::WebKeyboardEvent constructor fields before forwarding
into the retained source keyboard path. Retail injects the constructed event
through the live WebView keyboard slot at +0xe0.
=============
*/
static void QLWebView_InjectKeyboardEventFields( const qlWebKeyboardEventFields_t *event, qboolean down ) {
	if ( !event ) {
		return;
	}

	QLWebView_InjectKeyboardEvent( (int)event->virtualKeyCode, down );

#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		CL_Awesomium_InjectKeyboardEvent( event->eventType, event->virtualKeyCode, event->nativeKeyCode );
	}
#endif
}

/*
=============
QLWebView_InjectActivationKeyboardEvent

Mirrors the retail synthetic modifier-key injection used when the native
window regains focus while a retained browser view exists.
=============
*/
static void QLWebView_InjectActivationKeyboardEvent( void ) {
	static const qlWebKeyboardEventFields_t activationEvent = {
		QL_WEB_KEYBOARD_EVENT_ACTIVATION_TYPE,
		QL_WEB_KEYBOARD_EVENT_ACTIVATION_VIRTUAL_KEY,
		QL_WEB_KEYBOARD_EVENT_ACTIVATION_NATIVE_KEY
	};

	if ( !cl_webHost.viewInitialised ) {
		return;
	}

	cl_webHost.focused = qtrue;
	if ( cl_webHost.browserVisible || cl_webHost.browserActive ) {
		QLWebView_InjectKeyboardEventFields( &activationEvent, qtrue );
	}
}

/*
=============
QLWebHost_EnsureRuntime
=============
*/
static qboolean QLWebHost_EnsureRuntime( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	return qfalse;
#else
	qboolean browserRequested = CL_BrowserRuntimeRequested();
	qboolean awesomiumAllowed = CL_AwesomiumRuntimeActive();
	qboolean overlayAvailable = browserRequested && CL_OverlayServiceAvailable();

	if ( !overlayAvailable && !awesomiumAllowed ) {
		return qfalse;
	}
	if ( cl_webHost.loadFailed && !overlayAvailable ) {
		return qfalse;
	}

	(void)QLViewHandler_OnAddConsoleMessage;
	(void)QLDialogHandler_OnShowFileChooser;

	if ( !cl_webHost.coreInitialised ) {
#if defined( _WIN32 )
		if ( awesomiumAllowed ) {
			char homePath[MAX_OSPATH];
			char basePath[MAX_OSPATH];
			char *initialConfigJson;
			char *initialMapJson;
			char *initialFactoryJson;

			Cvar_VariableStringBuffer( "fs_homepath", homePath, sizeof( homePath ) );
			Cvar_VariableStringBuffer( "fs_basepath", basePath, sizeof( basePath ) );
			CL_WebHost_RefreshBootstrapProperties();
			initialConfigJson = (char *)Z_Malloc( CL_WEB_NATIVE_CONFIG_BUFFER_SIZE );
			if ( initialConfigJson ) {
				initialConfigJson[0] = '\0';
				CL_WebHost_BuildConfigJson( initialConfigJson, CL_WEB_NATIVE_CONFIG_BUFFER_SIZE );
			}
			initialMapJson = (char *)Z_Malloc( CL_WEB_MAP_JSON_BUFFER_SIZE );
			if ( initialMapJson ) {
				initialMapJson[0] = '\0';
				CL_WebHost_BuildMapListJson( initialMapJson, CL_WEB_MAP_JSON_BUFFER_SIZE );
			}
			initialFactoryJson = (char *)Z_Malloc( CL_WEB_FACTORY_JSON_BUFFER_SIZE );
			if ( initialFactoryJson ) {
				initialFactoryJson[0] = '\0';
				CL_WebHost_BuildFactoryListJson( initialFactoryJson, CL_WEB_FACTORY_JSON_BUFFER_SIZE );
			}
			cl_webHost.bootstrapAttemptCount++;
			if ( CL_Awesomium_Startup( homePath, basePath, cl_webHost.playerName, cl_webHost.appId, cl_webHost.steamIdLow, cl_webHost.steamIdHigh, cls.glconfig.vidWidth, cls.glconfig.vidHeight, initialConfigJson, initialMapJson, initialFactoryJson ) ) {
				if ( initialConfigJson ) {
					Z_Free( initialConfigJson );
				}
				if ( initialMapJson ) {
					Z_Free( initialMapJson );
				}
				if ( initialFactoryJson ) {
					Z_Free( initialFactoryJson );
				}
				cl_webHost.liveAwesomium = qtrue;
				cl_webHost.coreInitialised = qtrue;
				cl_webHost.sessionInitialised = qtrue;
				cl_webHost.viewInitialised = qtrue;
				cl_webHost.bootstrapReady = qtrue;
				cl_webHost.dataPakSourceInstalled = qtrue;
				cl_webHost.steamDataSourceInstalled = qfalse;
				cl_webHost.resourceInterceptorInstalled = qfalse;
				cl_webHost.jsMethodHandlerInstalled = qfalse;
				cl_webHost.dialogHandlerInstalled = qfalse;
				cl_webHost.viewHandlerInstalled = qfalse;
				cl_webHost.loadHandlerInstalled = qfalse;
				cl_webHost.windowObjectBound = qtrue;
				cl_webHost.qzInstanceBound = qtrue;
				cl_webHost.configSynced = qtrue;
				cl_webHost.nextConfigSyncFrame = cl_webHost.frameSequence + CL_WEB_NATIVE_CONFIG_SYNC_FRAMES;
				cl_webHost.mapCatalogSynced = qfalse;
				cl_webHost.nextMapCatalogSyncFrame = 0;
				cl_webHost.factoryCatalogSynced = qfalse;
				cl_webHost.nextFactoryCatalogSyncFrame = 0;
				cl_webHost.nextNativeRequestPollFrame = cl_webHost.frameSequence + CL_WEB_NATIVE_REQUEST_STARTUP_DELAY_FRAMES;
				QLWebView_Resize( cls.glconfig.vidWidth, cls.glconfig.vidHeight );
				QLWebView_RebuildSurfaceImage();
				Com_Printf( "Awesomium WebCore live view initialised from %s\n", homePath );
				CL_RefreshOnlineServicesBridgeState();
				return qtrue;
			}
			if ( initialConfigJson ) {
				Z_Free( initialConfigJson );
			}
			if ( initialMapJson ) {
				Z_Free( initialMapJson );
			}
			if ( initialFactoryJson ) {
				Z_Free( initialFactoryJson );
			}
			Com_Printf( "Awesomium WebCore initialisation failed: %s\n", CL_Awesomium_LastError() );
			cl_webHost.loadFailed = qtrue;
			CL_RefreshOnlineServicesBridgeState();
			if ( !overlayAvailable ) {
				return qfalse;
			}
		}
#endif
		cl_webHost.coreInitialised = qtrue;
		cl_webHost.sessionInitialised = qtrue;
		QLWebHost_RegisterRuntimeSources();
		cl_webHost.viewInitialised = qtrue;
		cl_webHost.jsMethodHandlerInstalled = qtrue;
		if ( !QLWebHost_WaitForBootstrapReady() ) {
			CL_WebHost_ResetRuntime( qfalse );
			return qfalse;
		}
		QLWebHost_InstallRuntimeListeners();
		QLWebView_Resize( cls.glconfig.vidWidth, cls.glconfig.vidHeight );
		QLWebView_RebuildSurfaceImage();
	}

	return qtrue;
#endif
}

/*
=============
QLWebHost_OpenURL
=============
*/
static qboolean QLWebHost_OpenURL( const char *url ) {
	if ( !QLWebHost_EnsureRuntime() ) {
		return qfalse;
	}

	CL_WebHost_RefreshBootstrapProperties();
	Q_strncpyz( cl_webHost.currentUrl, url ? url : CL_WEB_DEFAULT_URL, sizeof( cl_webHost.currentUrl ) );
	cl_webHost.browserVisible = qtrue;
	cl_webHost.browserActive = qfalse;
	cl_webHost.refreshStopped = qfalse;
	cl_webHost.focused = qtrue;
	cl_webHost.configSynced = qfalse;
	cl_webHost.nextConfigSyncFrame = 0;
	cl_webHost.mapCatalogSynced = qfalse;
	cl_webHost.nextMapCatalogSyncFrame = 0;
	cl_webHost.factoryCatalogSynced = qfalse;
	cl_webHost.nextFactoryCatalogSyncFrame = 0;
	Cvar_Set( "web_browserActive", "1" );

#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		if ( !CL_Awesomium_OpenURL( cl_webHost.currentUrl ) ) {
			Com_Printf( "Awesomium WebView failed to load %s: %s\n", cl_webHost.currentUrl, CL_Awesomium_LastError() );
			QLLoadHandler_OnFailLoadingFrame( cl_webHost.currentUrl );
			cl_webHost.browserActive = qfalse;
			return qfalse;
		}
		cl_webHost.zoomPercent = CL_WebZoomIntegerValue();
		CL_Awesomium_SetZoom( cl_webHost.zoomPercent );
		CL_WebZoomClearModified();
		QLLoadHandler_OnBeginLoadingFrame();
		QLWebView_RebuildSurfaceImage();
		cl_webHost.browserActive = qtrue;
		return qtrue;
	}
#endif

	QLLoadHandler_OnBeginLoadingFrame();
	if ( CL_WebHost_PrimeLauncherDocument( cl_webHost.currentUrl ) ) {
		QLLoadHandler_OnFinishLoadingFrame();
		QLLoadHandler_OnDocumentReady();
	} else {
		QLLoadHandler_OnFailLoadingFrame( cl_webHost.currentUrl );
	}
	cl_webHost.browserActive = qtrue;

	return qtrue;
}

/*
=============
QLWebHost_OpenRelativeURL
=============
*/
static qboolean QLWebHost_OpenRelativeURL( const char *hash ) {
	char url[MAX_STRING_CHARS];

	CL_WebHost_NormalizeHash( hash, cl_webHost.pendingHash, sizeof( cl_webHost.pendingHash ) );
	CL_WebHost_BuildCurrentURL( hash, url, sizeof( url ) );
	return QLWebHost_OpenURL( url );
}

/*
=============
QLWebHost_NavigateOrOpen
=============
*/
static qboolean QLWebHost_NavigateOrOpen( const char *hash ) {
	char normalizedHash[MAX_STRING_CHARS];
	char expectedUrl[MAX_STRING_CHARS];

	CL_WebHost_NormalizeHash( hash, normalizedHash, sizeof( normalizedHash ) );
	CL_WebHost_BuildCurrentURL( normalizedHash, expectedUrl, sizeof( expectedUrl ) );

	if ( cl_webHost.viewInitialised && !Q_stricmp( cl_webHost.currentUrl, expectedUrl ) ) {
		cl_webHost.browserVisible = qtrue;
		cl_webHost.browserActive = qtrue;
		cl_webHost.focused = qtrue;
		return qtrue;
	}

	if ( cl_webHost.viewInitialised && cl_webHost.documentReady && cl_webHost.windowObjectBound ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
		if ( cl_webHost.liveAwesomium ) {
			if ( !QLWebView_SetLocationHash( normalizedHash ) ) {
				Com_Printf( "Awesomium WebView failed to update location hash %s: %s\n", normalizedHash, CL_Awesomium_LastError() );
				return qfalse;
			}
			cl_webHost.zoomPercent = CL_WebZoomIntegerValue();
			CL_Awesomium_SetZoom( cl_webHost.zoomPercent );
			CL_WebZoomClearModified();
			cl_webHost.browserVisible = qtrue;
			cl_webHost.browserActive = qtrue;
			cl_webHost.focused = qtrue;
			return qtrue;
		}
#endif
		if ( !QLWebView_SetLocationHash( normalizedHash ) ) {
			return qfalse;
		}
		cl_webHost.browserVisible = qtrue;
		cl_webHost.browserActive = qtrue;
		cl_webHost.focused = qtrue;
		return qtrue;
	}

	return QLWebHost_OpenRelativeURL( normalizedHash );
}

/*
=============
QLWebHost_ReloadView
=============
*/
static void QLWebHost_ReloadView( qboolean ignoreCache ) {
	if ( !cl_webHost.viewInitialised ) {
		return;
	}

	cl_webHost.refreshStopped = qfalse;
	(void)ignoreCache;

	if ( !cl_webHost.currentUrl[0] ) {
		return;
	}

#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		QLLoadHandler_OnBeginLoadingFrame();
		CL_Awesomium_Reload( ignoreCache );
		cl_webHost.zoomPercent = CL_WebZoomIntegerValue();
		CL_Awesomium_SetZoom( cl_webHost.zoomPercent );
		CL_WebZoomClearModified();
		cl_webHost.configSynced = qfalse;
		cl_webHost.nextConfigSyncFrame = 0;
		cl_webHost.mapCatalogSynced = qfalse;
		cl_webHost.nextMapCatalogSyncFrame = 0;
		cl_webHost.factoryCatalogSynced = qfalse;
		cl_webHost.nextFactoryCatalogSyncFrame = 0;
		cl_webHost.surfaceDirty = qtrue;
		return;
	}
#endif

	QLLoadHandler_OnBeginLoadingFrame();
	if ( CL_WebHost_PrimeLauncherDocument( cl_webHost.currentUrl ) ) {
		QLLoadHandler_OnFinishLoadingFrame();
		QLLoadHandler_OnDocumentReady();
	} else {
		QLLoadHandler_OnFailLoadingFrame( cl_webHost.currentUrl );
	}
}

/*
=============
QLWebHost_HideBrowser
=============
*/
static void QLWebHost_HideBrowser( void ) {
	if ( !cl_webHost.coreInitialised || !cl_webHost.viewInitialised || cl_webHost.keyCaptureArmed ) {
		return;
	}

#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		CL_Awesomium_PauseRendering();
		CL_Awesomium_Unfocus();
	}
#endif

	cl_webBrowserVisible = qfalse;
	cl_webHost.browserVisible = qfalse;
	cl_webHost.browserActive = qfalse;
	cl_webHost.focused = qfalse;
	cl_webHost.surfaceDirty = qtrue;
	Cvar_Set( "web_browserActive", "0" );
	cls.keyCatchers &= ~KEYCATCH_BROWSER;
	CL_WebHost_ClearCursorOverride();
	if ( cgvm ) {
		VM_Call( cgvm, CG_EVENT_HANDLING, CGAME_EVENT_CLOSECOMMANDOVERLAY );
	}
	if ( cl_webHost.tooltip[0] ) {
		QLViewHandler_OnChangeTooltip( "" );
	}
}

/*
=============
CL_WebHost_HideBrowser

Allows the client key dispatcher to close the retained browser host without
exposing the retail-named internal helper outside this owner.
=============
*/
void CL_WebHost_HideBrowser( void ) {
	QLWebHost_HideBrowser();
}

/*
=============
CL_WebHost_SurfaceReadyForOverlay

Returns true only when the retained browser has a surface that is safe to let
own fullscreen drawing and input.
=============
*/
static qboolean CL_WebHost_SurfaceReadyForOverlay( qboolean requireShader ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	return qfalse;
#else
	if ( !CL_BrowserHostServiceAvailable() ) {
		return qfalse;
	}

	if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {
		return qfalse;
	}

	if ( requireShader && !cl_webHost.surfaceShader ) {
		return qfalse;
	}

	if ( !cl_webHost.surfaceHasVisiblePixels || !cl_webHost.surfaceHasUiContent ) {
		return qfalse;
	}

	return qtrue;
#endif
}

/*
=============
CL_WebHost_CheckLiveAwesomiumSurfaceFailure

Stops the live Awesomium path from owning disconnected screen flow forever when
WebCore starts but never produces a usable BitmapSurface.
=============
*/
static void CL_WebHost_CheckLiveAwesomiumSurfaceFailure( void ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( !cl_webHost.liveAwesomium || !cl_webHost.viewInitialised || !cl_webHost.browserVisible ) {
		cl_webHost.liveSurfaceMissingFrames = 0;
		return;
	}

	if ( cl_webHost.surfaceHasUiContent ) {
		cl_webHost.liveSurfaceMissingFrames = 0;
		return;
	}

	if ( cl_webHost.liveSurfaceMissingFrames < CL_WEB_LIVE_SURFACE_FAILURE_FRAMES ) {
		cl_webHost.liveSurfaceMissingFrames++;
		return;
	}

	Com_Printf( "Awesomium WebCore surface failed after %d frames (loading=%d crashed=%d lastError=%d); falling back to native UI\n",
		cl_webHost.liveSurfaceMissingFrames,
		CL_Awesomium_IsLoading(),
		CL_Awesomium_IsCrashed(),
		CL_Awesomium_LastErrorCode() );

	CL_WebHost_ResetRuntime( qtrue );
	cl_webHost.loadFailed = qtrue;
	CL_ResetBrowserOverlayState();
	CL_RefreshOnlineServicesBridgeState();
#endif
}

/*
=============
CL_WebHost_UpdateOverlayOwnership

Keeps the UI-visible active cvar and browser key catcher tied to a usable
surface, not just a live Awesomium view.
=============
*/
static void CL_WebHost_UpdateOverlayOwnership( void ) {
	qboolean ownsOverlay;

	ownsOverlay = CL_WebHost_SurfaceReadyForOverlay( qtrue );
	if ( ownsOverlay ) {
		if ( !( cls.keyCatchers & KEYCATCH_BROWSER ) ) {
			cls.keyCatchers |= KEYCATCH_BROWSER;
		}
	} else {
		cls.keyCatchers &= ~KEYCATCH_BROWSER;
	}

	CL_SetCvarIfChanged( "web_browserActive", ownsOverlay ? "1" : "0" );
}

/*
=============
QLWebCore_Update
=============
*/
static void QLWebCore_Update( void ) {
	if ( !cl_webHost.coreInitialised ) {
		return;
	}

#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		int zoomPercent;

		zoomPercent = CL_WebZoomIntegerValue();
		if ( ( ( cl_webZoom && cl_webZoom->modified ) || zoomPercent != cl_webHost.zoomPercent )
			&& CL_Awesomium_SetZoom( zoomPercent ) ) {
			cl_webHost.zoomPercent = zoomPercent;
			cl_webHost.surfaceDirty = qtrue;
		}
		CL_WebZoomClearModified();

		CL_Awesomium_Update();
		QLLoadHandler_PollLiveDocumentReady();
		CL_WebHost_PumpNativeJavascriptRequests();
		CL_WebHost_SyncMapCatalogSnapshot();
		CL_WebHost_SyncFactoryCatalogSnapshot();
		CL_WebHost_SyncConfigSnapshot();
		if ( CL_Awesomium_SurfaceDirty() ) {
			cl_webHost.surfaceDirty = qtrue;
		}
	}
#endif

	cl_webHost.frameSequence++;
	if ( cl_webHost.viewInitialised && ( cl_webHost.browserVisible || cl_webHost.browserActive || cl_webHost.loadingDocument ) ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
		if ( cl_webHost.liveAwesomium ) {
			return;
		}
#endif
		cl_webHost.surfaceDirty = qtrue;
	}
}

/*
=============
QLWebHost_PumpFrame
=============
*/
static void QLWebHost_PumpFrame( void ) {
	if ( !cl_webHost.viewInitialised ) {
		return;
	}

	if ( cl_webHost.viewWidth != cls.glconfig.vidWidth || cl_webHost.viewHeight != cls.glconfig.vidHeight ) {
		QLWebView_Resize( cls.glconfig.vidWidth, cls.glconfig.vidHeight );
		QLWebView_RebuildSurfaceImage();
		return;
	}

#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		int awesomiumWidth;
		int awesomiumHeight;

		awesomiumWidth = CL_Awesomium_SurfaceWidth();
		awesomiumHeight = CL_Awesomium_SurfaceHeight();
		if ( awesomiumWidth > 0 && awesomiumHeight > 0
			&& ( awesomiumWidth != cl_webHost.surfaceContentWidth
				|| awesomiumHeight != cl_webHost.surfaceContentHeight
				|| QLWebView_NextPowerOfTwo( awesomiumWidth ) != cl_webHost.surfaceWidth
				|| QLWebView_NextPowerOfTwo( awesomiumHeight ) != cl_webHost.surfaceHeight ) ) {
			QLWebView_RebuildSurfaceImage();
			return;
		}
	}
#endif

	if ( !cl_webHost.surfaceImageInitialised ) {
		QLWebView_RebuildSurfaceImage();
		return;
	}

	if ( cl_webHost.surfaceUploadWidth != cl_webHost.surfaceWidth || cl_webHost.surfaceUploadHeight != cl_webHost.surfaceHeight ) {
		QLWebView_RebuildSurfaceImage();
		return;
	}

	if ( cl_webHost.surfaceDirty ) {
		QLWebView_UploadSurfaceImage();
	}
}

/*
=============
CL_WebHost_JsonAppendDemoCallback
=============
*/
static void CL_WebHost_JsonAppendDemoCallback( clWebJsonBuilder_t *builder, const char *name ) {
	if ( !builder || !builder->buffer || !name || !name[0] ) {
		return;
	}

	CL_WebHost_BeginJsonItem( builder );
	Q_strcat( builder->buffer, builder->bufferSize, "\"" );
	CL_WebHost_AppendJsonEscaped( builder->buffer, builder->bufferSize, name );
	Q_strcat( builder->buffer, builder->bufferSize, "\"" );
}

/*
=============
CL_WebHost_AppendGametypeAvailability
=============
*/
static void CL_WebHost_AppendGametypeAvailability( char *buffer, size_t bufferSize ) {
	int i;

	Q_strcat( buffer, bufferSize, "[" );
	for ( i = 0; i < 13; i++ ) {
		if ( i > 0 ) {
			Q_strcat( buffer, bufferSize, "," );
		}
		Q_strcat( buffer, bufferSize, "0" );
	}
	Q_strcat( buffer, bufferSize, "]" );
}

/*
=============
CL_WebHost_StringListContains
=============
*/
static qboolean CL_WebHost_StringListContains( char seen[][MAX_QPATH], int count, const char *value ) {
	int i;

	if ( !seen || !value || !value[0] ) {
		return qfalse;
	}

	for ( i = 0; i < count; i++ ) {
		if ( !Q_stricmp( seen[i], value ) ) {
			return qtrue;
		}
	}

	return qfalse;
}

/*
=============
CL_WebHost_TypeStringContains
=============
*/
static qboolean CL_WebHost_TypeStringContains( const char *typeList, const char *token ) {
	if ( !typeList || !typeList[0] || !token || !token[0] ) {
		return qfalse;
	}

	return strstr( typeList, token ) != NULL;
}

/*
=============
CL_WebHost_ResolveMapTypeBits
=============
*/
static unsigned int CL_WebHost_ResolveMapTypeBits( const char *typeList ) {
	unsigned int typeBits = 0u;

	if ( !typeList || !typeList[0] ) {
		return 1u << GT_FFA;
	}

	if ( CL_WebHost_TypeStringContains( typeList, "ffa" ) ) {
		typeBits |= 1u << GT_FFA;
	}
	if ( CL_WebHost_TypeStringContains( typeList, "duel" ) || CL_WebHost_TypeStringContains( typeList, "tourney" ) ) {
		typeBits |= 1u << GT_TOURNAMENT;
	}
	if ( CL_WebHost_TypeStringContains( typeList, "race" ) ) {
		typeBits |= 1u << GT_SINGLE_PLAYER;
	}
	if ( CL_WebHost_TypeStringContains( typeList, "tdm" ) ) {
		typeBits |= 1u << GT_TEAM;
	}
	if ( CL_WebHost_TypeStringContains( typeList, "ca" ) ) {
		typeBits |= 1u << GT_CLAN_ARENA;
	}
	if ( CL_WebHost_TypeStringContains( typeList, "ctf" ) ) {
		typeBits |= 1u << GT_CTF;
	}
	if ( CL_WebHost_TypeStringContains( typeList, "oneflag" ) ) {
		typeBits |= 1u << GT_1FCTF;
	}
	if ( CL_WebHost_TypeStringContains( typeList, "overload" ) ) {
		typeBits |= 1u << GT_OBELISK;
	}
	if ( CL_WebHost_TypeStringContains( typeList, "hh" ) || CL_WebHost_TypeStringContains( typeList, "har" ) ) {
		typeBits |= 1u << GT_HARVESTER;
	}
	if ( CL_WebHost_TypeStringContains( typeList, "ft" ) ) {
		typeBits |= 1u << GT_FREEZE;
	}
	if ( CL_WebHost_TypeStringContains( typeList, "dom" ) ) {
		typeBits |= 1u << GT_DOMINATION;
	}
	if ( CL_WebHost_TypeStringContains( typeList, "ad" ) ) {
		typeBits |= 1u << GT_ATTACK_DEFEND;
	}
	if ( CL_WebHost_TypeStringContains( typeList, "rr" ) ) {
		typeBits |= 1u << GT_RED_ROVER;
	}

	return typeBits;
}

/*
=============
CL_WebHost_AppendGametypeBitsJson
=============
*/
static void CL_WebHost_AppendGametypeBitsJson( unsigned int typeBits, char *buffer, size_t bufferSize ) {
	int i;

	Q_strcat( buffer, bufferSize, "[" );
	for ( i = 0; i < GT_MAX_GAME_TYPE; i++ ) {
		if ( i > 0 ) {
			Q_strcat( buffer, bufferSize, "," );
		}
		Q_strcat( buffer, bufferSize, ( typeBits & ( 1u << i ) ) ? "1" : "0" );
	}
	Q_strcat( buffer, bufferSize, "]" );
}

/*
=============
CL_WebHost_AppendMapDescriptorJson
=============
*/
static void CL_WebHost_AppendMapDescriptorJson( const char *sysname, const char *name, unsigned int typeBits, char *buffer, size_t bufferSize, int *entryCount ) {
	clWebJsonBuilder_t builder;

	if ( !sysname || !sysname[0] || !buffer || !entryCount ) {
		return;
	}

	builder.buffer = buffer;
	builder.bufferSize = bufferSize;
	builder.count = *entryCount;
	CL_WebHost_BeginJsonItem( &builder );
	Q_strcat( buffer, bufferSize, "{\"sysname\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, sysname );
	Q_strcat( buffer, bufferSize, "\",\"name\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, ( name && name[0] ) ? name : sysname );
	Q_strcat( buffer, bufferSize, "\",\"gametypes\":" );
	CL_WebHost_AppendGametypeBitsJson( typeBits, buffer, bufferSize );
	Q_strcat( buffer, bufferSize, "}" );
	( *entryCount )++;
}

/*
=============
CL_WebHost_FindMapDescriptorIndex
=============
*/
static int CL_WebHost_FindMapDescriptorIndex( const clWebMapDescriptor_t *descriptors, int descriptorCount, const char *sysname ) {
	int index;

	if ( !descriptors || !sysname || !sysname[0] ) {
		return -1;
	}

	for ( index = 0; index < descriptorCount; index++ ) {
		if ( !Q_stricmp( descriptors[index].sysname, sysname ) ) {
			return index;
		}
	}

	return -1;
}

/*
=============
CL_WebHost_RecordMapDescriptor
=============
*/
static void CL_WebHost_RecordMapDescriptor( clWebMapDescriptor_t *descriptors, int *descriptorCount, const char *sysname, const char *name, unsigned int typeBits ) {
	int index;

	if ( !descriptors || !descriptorCount || !sysname || !sysname[0] ) {
		return;
	}

	index = CL_WebHost_FindMapDescriptorIndex( descriptors, *descriptorCount, sysname );
	if ( index < 0 ) {
		if ( *descriptorCount >= CL_WEB_MAX_MAPS ) {
			return;
		}
		index = *descriptorCount;
		( *descriptorCount )++;
		Com_Memset( &descriptors[index], 0, sizeof( descriptors[index] ) );
		Q_strncpyz( descriptors[index].sysname, sysname, sizeof( descriptors[index].sysname ) );
		Q_strncpyz( descriptors[index].name, ( name && name[0] ) ? name : sysname, sizeof( descriptors[index].name ) );
	} else if ( name && name[0] && ( !descriptors[index].name[0] || !Q_stricmp( descriptors[index].name, descriptors[index].sysname ) ) ) {
		Q_strncpyz( descriptors[index].name, name, sizeof( descriptors[index].name ) );
	}

	descriptors[index].typeBits |= typeBits;
}

/*
=============
CL_WebHost_BuildMapDescriptorJson
=============
*/
static void CL_WebHost_BuildMapDescriptorJson( const clWebMapDescriptor_t *descriptors, int descriptorCount, char *buffer, size_t bufferSize ) {
	int index;
	int entryCount;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	Q_strcat( buffer, bufferSize, "[" );
	entryCount = 0;
	for ( index = 0; index < descriptorCount; index++ ) {
		CL_WebHost_AppendMapDescriptorJson( descriptors[index].sysname, descriptors[index].name, descriptors[index].typeBits, buffer, bufferSize, &entryCount );
	}
	Q_strcat( buffer, bufferSize, "]" );
}

/*
=============
CL_WebHost_ParseArenaInfosToJson
=============
*/
static void CL_WebHost_ParseArenaInfosToJson( char *data, char *buffer, size_t bufferSize, char seenMaps[][MAX_QPATH], int *entryCount ) {
	char		*token;
	char		key[MAX_TOKEN_CHARS];
	char		info[MAX_INFO_STRING];
	char		*cursor;

	if ( !data || !buffer || !entryCount ) {
		return;
	}

	cursor = data;
	while ( 1 ) {
		token = COM_Parse( &cursor );
		if ( !token[0] ) {
			break;
		}
		if ( strcmp( token, "{" ) ) {
			Com_DPrintf( "launcher browser map parser: missing '{' in arena data\n" );
			break;
		}

		info[0] = '\0';
		while ( 1 ) {
			token = COM_ParseExt( &cursor, qtrue );
			if ( !token[0] ) {
				break;
			}
			if ( !strcmp( token, "}" ) ) {
				break;
			}

			Q_strncpyz( key, token, sizeof( key ) );
			token = COM_ParseExt( &cursor, qfalse );
			Info_SetValueForKey( info, key, token[0] ? token : "<NULL>" );
		}

		{
			const char	*mapName;
			const char	*longName;
			const char	*typeList;
			unsigned int	typeBits;

			mapName = Info_ValueForKey( info, ARENA_INFO_KEY_MAP );
			if ( !mapName[0] || *entryCount >= CL_WEB_MAX_MAPS || CL_WebHost_StringListContains( seenMaps, *entryCount, mapName ) ) {
				continue;
			}

			longName = Info_ValueForKey( info, ARENA_INFO_KEY_LONGNAME );
			typeList = Info_ValueForKey( info, ARENA_INFO_KEY_TYPE );
			typeBits = CL_WebHost_ResolveMapTypeBits( typeList );
			Q_strncpyz( seenMaps[*entryCount], mapName, MAX_QPATH );
			CL_WebHost_AppendMapDescriptorJson( mapName, longName, typeBits, buffer, bufferSize, entryCount );
		}
	}
}

/*
=============
CL_WebHost_ParseArenaInfosToDescriptors
=============
*/
static void CL_WebHost_ParseArenaInfosToDescriptors( char *data, clWebMapDescriptor_t *descriptors, int *descriptorCount ) {
	char		*token;
	char		key[MAX_TOKEN_CHARS];
	char		info[MAX_INFO_STRING];
	char		*cursor;

	if ( !data || !descriptors || !descriptorCount ) {
		return;
	}

	cursor = data;
	while ( 1 ) {
		token = COM_Parse( &cursor );
		if ( !token[0] ) {
			break;
		}
		if ( strcmp( token, "{" ) ) {
			Com_DPrintf( "launcher browser map parser: missing '{' in arena data\n" );
			break;
		}

		info[0] = '\0';
		while ( 1 ) {
			token = COM_ParseExt( &cursor, qtrue );
			if ( !token[0] ) {
				break;
			}
			if ( !strcmp( token, "}" ) ) {
				break;
			}

			Q_strncpyz( key, token, sizeof( key ) );
			token = COM_ParseExt( &cursor, qfalse );
			Info_SetValueForKey( info, key, token[0] ? token : "<NULL>" );
		}

		{
			const char	*mapName;
			const char	*longName;
			const char	*typeList;

			mapName = Info_ValueForKey( info, ARENA_INFO_KEY_MAP );
			if ( !mapName[0] || *descriptorCount >= CL_WEB_MAX_MAPS ) {
				continue;
			}

			longName = Info_ValueForKey( info, ARENA_INFO_KEY_LONGNAME );
			typeList = Info_ValueForKey( info, ARENA_INFO_KEY_TYPE );
			CL_WebHost_RecordMapDescriptor( descriptors, descriptorCount, mapName, longName, CL_WebHost_ResolveMapTypeBits( typeList ) );
		}
	}
}

/*
=============
CL_WebHost_AppendArenasFromFile
=============
*/
static void CL_WebHost_AppendArenasFromFile( const char *filename, char *buffer, size_t bufferSize, char seenMaps[][MAX_QPATH], int *entryCount ) {
	void	*fileBuffer;
	int		length;

	fileBuffer = NULL;
	length = FS_ReadFile( filename, &fileBuffer );
	if ( length <= 0 || !fileBuffer ) {
		return;
	}
	if ( length >= MAX_ARENAS_TEXT ) {
		FS_FreeFile( fileBuffer );
		return;
	}

	CL_WebHost_ParseArenaInfosToJson( (char *)fileBuffer, buffer, bufferSize, seenMaps, entryCount );
	FS_FreeFile( fileBuffer );
}

/*
=============
CL_WebHost_AppendArenaDescriptorsFromFile
=============
*/
static void CL_WebHost_AppendArenaDescriptorsFromFile( const char *filename, clWebMapDescriptor_t *descriptors, int *descriptorCount ) {
	void	*fileBuffer;
	int		length;

	fileBuffer = NULL;
	length = FS_ReadFile( filename, &fileBuffer );
	if ( length <= 0 || !fileBuffer ) {
		return;
	}
	if ( length >= MAX_ARENAS_TEXT ) {
		FS_FreeFile( fileBuffer );
		return;
	}

	CL_WebHost_ParseArenaInfosToDescriptors( (char *)fileBuffer, descriptors, descriptorCount );
	FS_FreeFile( fileBuffer );
}

/*
=============
CL_WebHost_LoadArenaDescriptors
=============
*/
static void CL_WebHost_LoadArenaDescriptors( clWebMapDescriptor_t *descriptors, int *descriptorCount ) {
	char	arenasFile[MAX_QPATH];
	char	dirlist[CL_WEB_ARENA_FILE_LIST_BUFFER];
	char	*dirptr;
	char	filename[MAX_QPATH];
	int		numdirs;
	int		dirlen;
	int		i;

	if ( !descriptors || !descriptorCount ) {
		return;
	}

	*descriptorCount = 0;
	Cvar_VariableStringBuffer( "g_arenasFile", arenasFile, sizeof( arenasFile ) );
	if ( arenasFile[0] ) {
		CL_WebHost_AppendArenaDescriptorsFromFile( arenasFile, descriptors, descriptorCount );
	} else {
		CL_WebHost_AppendArenaDescriptorsFromFile( "scripts/arenas.txt", descriptors, descriptorCount );
	}

	numdirs = FS_GetFileList( "scripts", ".arena", dirlist, sizeof( dirlist ) );
	dirptr = dirlist;
	for ( i = 0; i < numdirs && *descriptorCount < CL_WEB_MAX_MAPS; i++, dirptr += dirlen + 1 ) {
		dirlen = strlen( dirptr );
		if ( dirlen <= 0 ) {
			continue;
		}

		Com_sprintf( filename, sizeof( filename ), "scripts/%s", dirptr );
		CL_WebHost_AppendArenaDescriptorsFromFile( filename, descriptors, descriptorCount );
	}
}

/*
=============
CL_WebHost_BuildMapListJsonFromBSPScan
=============
*/
static void CL_WebHost_BuildMapListJsonFromBSPScan( char *buffer, size_t bufferSize ) {
	char fileList[32768];
	char *cursor;
	int count;

	buffer[0] = '\0';
	Q_strcat( buffer, bufferSize, "[" );
	count = FS_GetFileList( "maps", ".bsp", fileList, sizeof( fileList ) );
	cursor = fileList;
	for ( ; count > 0 && *cursor; count-- ) {
		char mapName[MAX_QPATH];
		const char *extension;
		clWebJsonBuilder_t builder;

		Q_strncpyz( mapName, cursor, sizeof( mapName ) );
		extension = strrchr( mapName, '.' );
		if ( extension ) {
			*strrchr( mapName, '.' ) = '\0';
		}

		builder.buffer = buffer;
		builder.bufferSize = bufferSize;
		builder.count = ( buffer[1] != '\0' ) ? 1 : 0;
		CL_WebHost_BeginJsonItem( &builder );
		Q_strcat( buffer, bufferSize, "{\"sysname\":\"" );
		CL_WebHost_AppendJsonEscaped( buffer, bufferSize, mapName );
		Q_strcat( buffer, bufferSize, "\",\"name\":\"" );
		CL_WebHost_AppendJsonEscaped( buffer, bufferSize, mapName );
		Q_strcat( buffer, bufferSize, "\",\"gametypes\":" );
		CL_WebHost_AppendGametypeAvailability( buffer, bufferSize );
		Q_strcat( buffer, bufferSize, "}" );
		cursor += strlen( cursor ) + 1;
	}
	Q_strcat( buffer, bufferSize, "]" );
}

/*
=============
CL_WebHost_TrimMapPoolToken
=============
*/
static void CL_WebHost_TrimMapPoolToken( char *token ) {
	char *start;
	char *end;

	if ( !token ) {
		return;
	}

	start = token;
	while ( *start == ' ' || *start == '\t' ) {
		start++;
	}

	end = start + strlen( start );
	while ( end > start && ( end[-1] == ' ' || end[-1] == '\t' ) ) {
		end--;
	}
	*end = '\0';

	if ( start != token ) {
		memmove( token, start, ( end - start ) + 1 );
	}
}

/*
=============
CL_WebHost_ResolveGametypeTokenBit
=============
*/
static unsigned int CL_WebHost_ResolveGametypeTokenBit( const char *token ) {
	if ( !token || !token[0] ) {
		return 0u;
	}

	if ( !Q_stricmp( token, "ffa" ) ) {
		return 1u << GT_FFA;
	}
	if ( !Q_stricmp( token, "duel" ) || !Q_stricmp( token, "tourney" ) ) {
		return 1u << GT_TOURNAMENT;
	}
	if ( !Q_stricmp( token, "race" ) ) {
		return 1u << GT_RACE;
	}
	if ( !Q_stricmp( token, "tdm" ) ) {
		return 1u << GT_TEAM;
	}
	if ( !Q_stricmp( token, "ca" ) ) {
		return 1u << GT_CLAN_ARENA;
	}
	if ( !Q_stricmp( token, "ctf" ) ) {
		return 1u << GT_CTF;
	}
	if ( !Q_stricmp( token, "oneflag" ) ) {
		return 1u << GT_1FCTF;
	}
	if ( !Q_stricmp( token, "overload" ) ) {
		return 1u << GT_OBELISK;
	}
	if ( !Q_stricmp( token, "hh" ) || !Q_stricmp( token, "har" ) ) {
		return 1u << GT_HARVESTER;
	}
	if ( !Q_stricmp( token, "ft" ) ) {
		return 1u << GT_FREEZE;
	}
	if ( !Q_stricmp( token, "dom" ) ) {
		return 1u << GT_DOMINATION;
	}
	if ( !Q_stricmp( token, "ad" ) ) {
		return 1u << GT_ATTACK_DEFEND;
	}
	if ( !Q_stricmp( token, "rr" ) ) {
		return 1u << GT_RED_ROVER;
	}

	return 0u;
}

/*
=============
CL_WebHost_ResolveMapPoolFactoryBits
=============
*/
static unsigned int CL_WebHost_ResolveMapPoolFactoryBits( const char *factoryId, const clWebFactoryBasegt_t *factoryBasegts, int factoryBasegtCount ) {
	int index;

	if ( !factoryId || !factoryId[0] ) {
		return 0u;
	}

	if ( factoryBasegts ) {
		for ( index = 0; index < factoryBasegtCount; index++ ) {
			if ( !Q_stricmp( factoryBasegts[index].id, factoryId ) ) {
				return CL_WebHost_ResolveGametypeTokenBit( factoryBasegts[index].basegt );
			}
		}
	}

	return CL_WebHost_ResolveGametypeTokenBit( factoryId );
}

/*
=============
CL_WebHost_BuildMapListJsonFromMapPool

Builds the WebUI arena list from Quake Live's retail `mappool.txt` rotation
source, merging duplicate map entries into gametype availability bits.
=============
*/
static qboolean CL_WebHost_BuildMapListJsonFromMapPool( char *buffer, size_t bufferSize, const clWebMapDescriptor_t *arenaDescriptors, int arenaDescriptorCount ) {
	void *fileBuffer;
	int length;
	char *poolText;
	char *cursor;
	clWebMapDescriptor_t *poolDescriptors;
	int poolDescriptorCount;
	clWebFactoryBasegt_t factoryBasegts[CL_WEB_MAX_FACTORY_DEFINITIONS];
	int factoryBasegtCount;

	if ( !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	fileBuffer = NULL;
	length = FS_ReadFile( "mappool.txt", &fileBuffer );
	if ( length <= 0 || !fileBuffer ) {
		return qfalse;
	}
	if ( length >= CL_WEB_MAP_POOL_FILE_BYTES ) {
		FS_FreeFile( fileBuffer );
		return qfalse;
	}

	poolText = (char *)Z_Malloc( length + 1 );
	poolDescriptors = (clWebMapDescriptor_t *)Z_Malloc( sizeof( *poolDescriptors ) * CL_WEB_MAX_MAPS );
	if ( !poolText || !poolDescriptors ) {
		if ( poolText ) {
			Z_Free( poolText );
		}
		if ( poolDescriptors ) {
			Z_Free( poolDescriptors );
		}
		FS_FreeFile( fileBuffer );
		return qfalse;
	}

	Com_Memcpy( poolText, fileBuffer, length );
	poolText[length] = '\0';
	Com_Memset( poolDescriptors, 0, sizeof( *poolDescriptors ) * CL_WEB_MAX_MAPS );
	FS_FreeFile( fileBuffer );

	factoryBasegtCount = 0;
	Com_Memset( factoryBasegts, 0, sizeof( factoryBasegts ) );
	CL_WebHost_LoadFactoryBasegtList( factoryBasegts, &factoryBasegtCount, CL_WEB_MAX_FACTORY_DEFINITIONS );

	poolDescriptorCount = 0;
	cursor = poolText;
	while ( *cursor && poolDescriptorCount < CL_WEB_MAX_MAPS ) {
		char lineBuffer[MAX_STRING_CHARS * 2];
		char mapPath[MAX_QPATH];
		char *comment;
		char *separator;
		char *mapToken;
		char *factoryToken;
		const char *displayName;
		unsigned int typeBits;
		int lineLength;
		int arenaIndex;

		lineLength = 0;
		while ( cursor[lineLength] && cursor[lineLength] != '\n' && cursor[lineLength] != '\r' && lineLength < (int)sizeof( lineBuffer ) - 1 ) {
			lineBuffer[lineLength] = cursor[lineLength];
			lineLength++;
		}
		lineBuffer[lineLength] = '\0';

		cursor += lineLength;
		while ( *cursor == '\n' || *cursor == '\r' ) {
			cursor++;
		}

		mapToken = lineBuffer;
		while ( *mapToken == ' ' || *mapToken == '\t' ) {
			mapToken++;
		}
		if ( !mapToken[0] || mapToken[0] == '#' ) {
			continue;
		}

		comment = strchr( mapToken, '#' );
		if ( comment ) {
			*comment = '\0';
		}

		separator = strchr( mapToken, '|' );
		if ( !separator ) {
			continue;
		}
		*separator = '\0';
		factoryToken = separator + 1;
		CL_WebHost_TrimMapPoolToken( mapToken );
		CL_WebHost_TrimMapPoolToken( factoryToken );
		if ( !mapToken[0] || !factoryToken[0] || factoryToken[0] == '_' ) {
			continue;
		}

		Com_sprintf( mapPath, sizeof( mapPath ), "maps/%s.bsp", mapToken );
		if ( FS_ReadFile( mapPath, NULL ) == -1 ) {
			continue;
		}

		typeBits = CL_WebHost_ResolveMapPoolFactoryBits( factoryToken, factoryBasegts, factoryBasegtCount );
		if ( !typeBits ) {
			continue;
		}

		displayName = mapToken;
		arenaIndex = CL_WebHost_FindMapDescriptorIndex( arenaDescriptors, arenaDescriptorCount, mapToken );
		if ( arenaIndex >= 0 && arenaDescriptors[arenaIndex].name[0] ) {
			displayName = arenaDescriptors[arenaIndex].name;
		}

		CL_WebHost_RecordMapDescriptor( poolDescriptors, &poolDescriptorCount, mapToken, displayName, typeBits );
	}

	if ( poolDescriptorCount > 0 ) {
		CL_WebHost_BuildMapDescriptorJson( poolDescriptors, poolDescriptorCount, buffer, bufferSize );
	}

	Z_Free( poolDescriptors );
	Z_Free( poolText );
	return poolDescriptorCount > 0;
}

/*
=============
CL_WebHost_BuildMapListJson
=============
*/
static void CL_WebHost_BuildMapListJson( char *buffer, size_t bufferSize ) {
	clWebMapDescriptor_t *arenaDescriptors;
	int arenaDescriptorCount;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	arenaDescriptors = (clWebMapDescriptor_t *)Z_Malloc( sizeof( *arenaDescriptors ) * CL_WEB_MAX_MAPS );
	if ( !arenaDescriptors ) {
		CL_WebHost_BuildMapListJsonFromBSPScan( buffer, bufferSize );
		return;
	}

	Com_Memset( arenaDescriptors, 0, sizeof( *arenaDescriptors ) * CL_WEB_MAX_MAPS );
	arenaDescriptorCount = 0;
	CL_WebHost_LoadArenaDescriptors( arenaDescriptors, &arenaDescriptorCount );
	if ( !CL_WebHost_BuildMapListJsonFromMapPool( buffer, bufferSize, arenaDescriptors, arenaDescriptorCount ) ) {
		if ( arenaDescriptorCount > 0 ) {
			CL_WebHost_BuildMapDescriptorJson( arenaDescriptors, arenaDescriptorCount, buffer, bufferSize );
		} else {
			CL_WebHost_BuildMapListJsonFromBSPScan( buffer, bufferSize );
		}
	}

	Z_Free( arenaDescriptors );
}

/*
=============
CL_WebFactory_ReportParseError
=============
*/
static void CL_WebFactory_ReportParseError( const clWebFactoryParseState_t *state, const char *message ) {
	const char *filename;

	filename = ( state && state->filename && state->filename[0] ) ? state->filename : "<unknown>";
	Com_DPrintf( "launcher browser factory parser: %s:%d: %s\n",
		filename,
		state ? state->line : 0,
		message ? message : "unknown parse error" );
}

/*
=============
CL_WebFactory_SkipWhitespace
=============
*/
static void CL_WebFactory_SkipWhitespace( clWebFactoryParseState_t *state ) {
	if ( !state ) {
		return;
	}

	while ( state->cursor < state->end ) {
		char ch;

		ch = *state->cursor;
		if ( ch == '\n' ) {
			state->line++;
			state->cursor++;
			continue;
		}
		if ( ch == '\r' || ch == '\t' || ch == ' ' ) {
			state->cursor++;
			continue;
		}
		break;
	}
}

/*
=============
CL_WebFactory_ParseExpectedChar
=============
*/
static qboolean CL_WebFactory_ParseExpectedChar( clWebFactoryParseState_t *state, char ch ) {
	CL_WebFactory_SkipWhitespace( state );
	if ( !state || state->cursor >= state->end || *state->cursor != ch ) {
		CL_WebFactory_ReportParseError( state, va( "expected '%c'", ch ) );
		return qfalse;
	}

	state->cursor++;
	return qtrue;
}

/*
=============
CL_WebFactory_SkipJsonString
=============
*/
static qboolean CL_WebFactory_SkipJsonString( clWebFactoryParseState_t *state ) {
	if ( !state ) {
		return qfalse;
	}

	CL_WebFactory_SkipWhitespace( state );
	if ( state->cursor >= state->end || *state->cursor != '"' ) {
		CL_WebFactory_ReportParseError( state, "expected string" );
		return qfalse;
	}

	state->cursor++;
	while ( state->cursor < state->end ) {
		char ch;

		ch = *state->cursor++;
		if ( ch == '"' ) {
			return qtrue;
		}
		if ( ch == '\\' ) {
			if ( state->cursor >= state->end ) {
				break;
			}
			state->cursor++;
			continue;
		}
		if ( ch == '\n' ) {
			state->line++;
		}
	}

	CL_WebFactory_ReportParseError( state, "unterminated string" );
	return qfalse;
}

/*
=============
CL_WebFactory_ParseJsonString
=============
*/
static qboolean CL_WebFactory_ParseJsonString( clWebFactoryParseState_t *state, char *buffer, size_t bufferSize ) {
	size_t length;

	if ( !state || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	CL_WebFactory_SkipWhitespace( state );
	if ( state->cursor >= state->end || *state->cursor != '"' ) {
		CL_WebFactory_ReportParseError( state, "expected string" );
		return qfalse;
	}

	state->cursor++;
	length = 0u;
	while ( state->cursor < state->end ) {
		char ch;

		ch = *state->cursor++;
		if ( ch == '"' ) {
			buffer[length] = '\0';
			return qtrue;
		}

		if ( ch == '\\' ) {
			char escaped;

			if ( state->cursor >= state->end ) {
				break;
			}

			escaped = *state->cursor++;
			switch ( escaped ) {
				case '"': ch = '"'; break;
				case '\\': ch = '\\'; break;
				case '/': ch = '/'; break;
				case 'b': ch = '\b'; break;
				case 'f': ch = '\f'; break;
				case 'n': ch = '\n'; break;
				case 'r': ch = '\r'; break;
				case 't': ch = '\t'; break;
				case 'u': {
					int i;
					int value = 0;

					for ( i = 0; i < 4 && state->cursor < state->end; i++ ) {
						char hex;

						hex = *state->cursor++;
						value <<= 4;
						if ( hex >= '0' && hex <= '9' ) {
							value |= hex - '0';
						} else if ( hex >= 'a' && hex <= 'f' ) {
							value |= 10 + ( hex - 'a' );
						} else if ( hex >= 'A' && hex <= 'F' ) {
							value |= 10 + ( hex - 'A' );
						} else {
							CL_WebFactory_ReportParseError( state, "invalid unicode escape" );
							return qfalse;
						}
					}

					ch = ( value <= 0x7F ) ? (char)value : '?';
					break;
				}
				default:
					CL_WebFactory_ReportParseError( state, "invalid escape" );
					return qfalse;
			}
		}

		if ( ch == '\n' ) {
			state->line++;
		}

		if ( length + 1u < bufferSize ) {
			buffer[length++] = ch;
		}
	}

	CL_WebFactory_ReportParseError( state, "unterminated string" );
	return qfalse;
}

/*
=============
CL_WebFactory_ParseLiteralString
=============
*/
static qboolean CL_WebFactory_ParseLiteralString( clWebFactoryParseState_t *state, char *buffer, size_t bufferSize ) {
	size_t length;

	if ( !state || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	length = 0u;
	CL_WebFactory_SkipWhitespace( state );
	while ( state->cursor < state->end ) {
		char ch;

		ch = *state->cursor;
		if ( ch == ',' || ch == '}' || ch == ']' || ch == '\n' || ch == '\r' || ch == '\t' || ch == ' ' ) {
			break;
		}

		if ( length + 1u < bufferSize ) {
			buffer[length++] = ch;
		}
		state->cursor++;
	}

	buffer[length] = '\0';
	if ( length == 0u ) {
		CL_WebFactory_ReportParseError( state, "expected literal" );
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_WebFactory_ParseValueString
=============
*/
static qboolean CL_WebFactory_ParseValueString( clWebFactoryParseState_t *state, char *buffer, size_t bufferSize ) {
	CL_WebFactory_SkipWhitespace( state );
	if ( !state || state->cursor >= state->end ) {
		CL_WebFactory_ReportParseError( state, "unexpected end of data" );
		return qfalse;
	}

	if ( *state->cursor == '"' ) {
		return CL_WebFactory_ParseJsonString( state, buffer, bufferSize );
	}

	return CL_WebFactory_ParseLiteralString( state, buffer, bufferSize );
}

/*
=============
CL_WebFactory_SkipValue
=============
*/
static qboolean CL_WebFactory_SkipValue( clWebFactoryParseState_t *state ) {
	if ( !state ) {
		return qfalse;
	}

	CL_WebFactory_SkipWhitespace( state );
	if ( state->cursor >= state->end ) {
		CL_WebFactory_ReportParseError( state, "unexpected end of data" );
		return qfalse;
	}

	switch ( *state->cursor ) {
		case '{': {
			int depth = 0;
			do {
				char ch;

				ch = *state->cursor++;
				if ( ch == '{' ) {
					depth++;
				} else if ( ch == '}' ) {
					depth--;
				} else if ( ch == '"' ) {
					state->cursor--;
					if ( !CL_WebFactory_SkipJsonString( state ) ) {
						return qfalse;
					}
					continue;
				}

				if ( ch == '\n' ) {
					state->line++;
				}
			} while ( depth > 0 && state->cursor < state->end );
			if ( depth != 0 ) {
				CL_WebFactory_ReportParseError( state, "unterminated object" );
				return qfalse;
			}
			return qtrue;
		}
		case '[': {
			int depth = 0;
			do {
				char ch;

				ch = *state->cursor++;
				if ( ch == '[' ) {
					depth++;
				} else if ( ch == ']' ) {
					depth--;
				} else if ( ch == '"' ) {
					state->cursor--;
					if ( !CL_WebFactory_SkipJsonString( state ) ) {
						return qfalse;
					}
					continue;
				}

				if ( ch == '\n' ) {
					state->line++;
				}
			} while ( depth > 0 && state->cursor < state->end );
			if ( depth != 0 ) {
				CL_WebFactory_ReportParseError( state, "unterminated array" );
				return qfalse;
			}
			return qtrue;
		}
		case '"':
			return CL_WebFactory_SkipJsonString( state );
		default:
			while ( state->cursor < state->end ) {
				char ch;

				ch = *state->cursor;
				if ( ch == ',' || ch == '}' || ch == ']' || ch == '\n' ) {
					return qtrue;
				}
				state->cursor++;
			}
			return qtrue;
	}
}

/*
=============
CL_WebFactory_ParseSettingsObject
=============
*/
static qboolean CL_WebFactory_ParseSettingsObject( clWebFactoryParseState_t *state, char *buffer, size_t bufferSize ) {
	int entryCount;

	if ( !state || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	Q_strcat( buffer, bufferSize, "{" );
	entryCount = 0;

	if ( !CL_WebFactory_ParseExpectedChar( state, '{' ) ) {
		return qfalse;
	}

	CL_WebFactory_SkipWhitespace( state );
	if ( state->cursor < state->end && *state->cursor == '}' ) {
		state->cursor++;
		Q_strcat( buffer, bufferSize, "}" );
		return qtrue;
	}

	while ( state->cursor < state->end ) {
		char key[128];
		char loweredKey[128];
		char value[MAX_CVAR_VALUE_STRING];

		if ( !CL_WebFactory_ParseJsonString( state, key, sizeof( key ) ) ) {
			return qfalse;
		}
		if ( !CL_WebFactory_ParseExpectedChar( state, ':' ) ) {
			return qfalse;
		}
		if ( !CL_WebFactory_ParseValueString( state, value, sizeof( value ) ) ) {
			return qfalse;
		}

		Q_strncpyz( loweredKey, key, sizeof( loweredKey ) );
		Q_strlwr( loweredKey );
		if ( entryCount > 0 ) {
			Q_strcat( buffer, bufferSize, "," );
		}
		Q_strcat( buffer, bufferSize, "\"" );
		CL_WebHost_AppendJsonEscaped( buffer, bufferSize, loweredKey );
		Q_strcat( buffer, bufferSize, "\":\"" );
		CL_WebHost_AppendJsonEscaped( buffer, bufferSize, value );
		Q_strcat( buffer, bufferSize, "\"" );
		entryCount++;

		CL_WebFactory_SkipWhitespace( state );
		if ( state->cursor >= state->end ) {
			CL_WebFactory_ReportParseError( state, "unterminated cvars object" );
			return qfalse;
		}

		if ( *state->cursor == ',' ) {
			state->cursor++;
			CL_WebFactory_SkipWhitespace( state );
			if ( state->cursor < state->end && *state->cursor == '}' ) {
				state->cursor++;
				Q_strcat( buffer, bufferSize, "}" );
				return qtrue;
			}
			continue;
		}
		if ( *state->cursor == '}' ) {
			state->cursor++;
			Q_strcat( buffer, bufferSize, "}" );
			return qtrue;
		}

		CL_WebFactory_ReportParseError( state, "expected ',' or '}'" );
		return qfalse;
	}

	CL_WebFactory_ReportParseError( state, "unterminated cvars object" );
	return qfalse;
}

/*
=============
CL_WebFactory_ParseDefinition
=============
*/
static qboolean CL_WebFactory_ParseDefinition( clWebFactoryParseState_t *state, clWebFactoryDefinition_t *definition ) {
	qboolean sawTitle;
	qboolean sawCvars;

	if ( !state || !definition ) {
		return qfalse;
	}

	Com_Memset( definition, 0, sizeof( *definition ) );
	Q_strncpyz( definition->settingsJson, "{}", sizeof( definition->settingsJson ) );
	sawTitle = qfalse;
	sawCvars = qfalse;

	if ( !CL_WebFactory_ParseExpectedChar( state, '{' ) ) {
		return qfalse;
	}

	while ( state->cursor < state->end ) {
		char key[64];

		CL_WebFactory_SkipWhitespace( state );
		if ( state->cursor >= state->end ) {
			break;
		}
		if ( *state->cursor == '}' ) {
			state->cursor++;
			break;
		}

		if ( !CL_WebFactory_ParseJsonString( state, key, sizeof( key ) ) ) {
			return qfalse;
		}
		if ( !CL_WebFactory_ParseExpectedChar( state, ':' ) ) {
			return qfalse;
		}

		if ( !Q_stricmp( key, "id" ) ) {
			CL_WebFactory_SkipWhitespace( state );
			if ( state->cursor >= state->end || *state->cursor != '"' ) {
				CL_WebFactory_ReportParseError( state, "factory missing id string" );
				return qfalse;
			}
			if ( !CL_WebFactory_ParseJsonString( state, definition->id, sizeof( definition->id ) ) ) {
				return qfalse;
			}
		} else if ( !Q_stricmp( key, "title" ) ) {
			CL_WebFactory_SkipWhitespace( state );
			if ( state->cursor >= state->end || *state->cursor != '"' ) {
				CL_WebFactory_ReportParseError( state, "factory missing title string" );
				return qfalse;
			}
			if ( !CL_WebFactory_ParseJsonString( state, definition->title, sizeof( definition->title ) ) ) {
				return qfalse;
			}
			sawTitle = qtrue;
		} else if ( !Q_stricmp( key, "author" ) ) {
			CL_WebFactory_SkipWhitespace( state );
			if ( *state->cursor == '"' ) {
				if ( !CL_WebFactory_ParseJsonString( state, definition->author, sizeof( definition->author ) ) ) {
					return qfalse;
				}
			} else if ( !CL_WebFactory_SkipValue( state ) ) {
				return qfalse;
			}
		} else if ( !Q_stricmp( key, "description" ) ) {
			CL_WebFactory_SkipWhitespace( state );
			if ( *state->cursor == '"' ) {
				if ( !CL_WebFactory_ParseJsonString( state, definition->description, sizeof( definition->description ) ) ) {
					return qfalse;
				}
			} else if ( !CL_WebFactory_SkipValue( state ) ) {
				return qfalse;
			}
		} else if ( !Q_stricmp( key, "basegt" ) ) {
			CL_WebFactory_SkipWhitespace( state );
			if ( state->cursor >= state->end || *state->cursor != '"' ) {
				CL_WebFactory_ReportParseError( state, "factory missing basegt string" );
				return qfalse;
			}
			if ( !CL_WebFactory_ParseJsonString( state, definition->basegt, sizeof( definition->basegt ) ) ) {
				return qfalse;
			}
		} else if ( !Q_stricmp( key, "cvars" ) ) {
			CL_WebFactory_SkipWhitespace( state );
			if ( state->cursor >= state->end || *state->cursor != '{' ) {
				CL_WebFactory_ReportParseError( state, "factory missing cvars object" );
				return qfalse;
			}
			if ( !CL_WebFactory_ParseSettingsObject( state, definition->settingsJson, sizeof( definition->settingsJson ) ) ) {
				return qfalse;
			}
			sawCvars = qtrue;
		} else {
			if ( !CL_WebFactory_SkipValue( state ) ) {
				return qfalse;
			}
		}

		CL_WebFactory_SkipWhitespace( state );
		if ( state->cursor >= state->end ) {
			break;
		}
		if ( *state->cursor == ',' ) {
			state->cursor++;
			CL_WebFactory_SkipWhitespace( state );
			if ( state->cursor < state->end && *state->cursor == '}' ) {
				state->cursor++;
				break;
			}
			continue;
		}
		if ( *state->cursor == '}' ) {
			state->cursor++;
			break;
		}

		CL_WebFactory_ReportParseError( state, "expected ',' or '}'" );
		return qfalse;
	}

	if ( !definition->id[0] || !definition->basegt[0] || !sawTitle || !sawCvars ) {
		CL_WebFactory_ReportParseError( state, "factory missing required fields" );
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_WebHost_RecordFactoryBasegt
=============
*/
static void CL_WebHost_RecordFactoryBasegt( clWebFactoryBasegt_t *definitions, int *definitionCount, int maxDefinitions, const clWebFactoryDefinition_t *definition ) {
	int index;

	if ( !definitions || !definitionCount || !definition || !definition->id[0] || !definition->basegt[0] ) {
		return;
	}
	if ( *definitionCount >= maxDefinitions ) {
		return;
	}
	for ( index = 0; index < *definitionCount; index++ ) {
		if ( !Q_stricmp( definitions[index].id, definition->id ) ) {
			return;
		}
	}

	Q_strncpyz( definitions[*definitionCount].id, definition->id, sizeof( definitions[*definitionCount].id ) );
	Q_strncpyz( definitions[*definitionCount].basegt, definition->basegt, sizeof( definitions[*definitionCount].basegt ) );
	( *definitionCount )++;
}

/*
=============
CL_WebHost_AppendFactoryBasegtsFromBuffer
=============
*/
static void CL_WebHost_AppendFactoryBasegtsFromBuffer( const char *filename, char *data, int dataLength, clWebFactoryBasegt_t *definitions, int *definitionCount, int maxDefinitions ) {
	clWebFactoryParseState_t state;

	if ( !data || dataLength <= 0 || !definitions || !definitionCount ) {
		return;
	}

	state.cursor = data;
	state.end = data + dataLength;
	state.filename = filename;
	state.line = 1;

	CL_WebFactory_SkipWhitespace( &state );
	if ( state.cursor >= state.end ) {
		return;
	}

	if ( *state.cursor == '{' ) {
		clWebFactoryDefinition_t definition;

		if ( CL_WebFactory_ParseDefinition( &state, &definition ) ) {
			CL_WebHost_RecordFactoryBasegt( definitions, definitionCount, maxDefinitions, &definition );
		}
		return;
	}

	if ( !CL_WebFactory_ParseExpectedChar( &state, '[' ) ) {
		return;
	}

	CL_WebFactory_SkipWhitespace( &state );
	if ( state.cursor < state.end && *state.cursor == ']' ) {
		state.cursor++;
		return;
	}

	while ( state.cursor < state.end && *definitionCount < maxDefinitions ) {
		clWebFactoryDefinition_t definition;

		if ( !CL_WebFactory_ParseDefinition( &state, &definition ) ) {
			return;
		}
		CL_WebHost_RecordFactoryBasegt( definitions, definitionCount, maxDefinitions, &definition );

		CL_WebFactory_SkipWhitespace( &state );
		if ( state.cursor >= state.end ) {
			return;
		}
		if ( *state.cursor == ',' ) {
			state.cursor++;
			CL_WebFactory_SkipWhitespace( &state );
			if ( state.cursor < state.end && *state.cursor == ']' ) {
				state.cursor++;
				return;
			}
			continue;
		}
		if ( *state.cursor == ']' ) {
			state.cursor++;
			return;
		}
		CL_WebFactory_ReportParseError( &state, "expected ',' or ']'" );
		return;
	}
}

/*
=============
CL_WebHost_AppendFactoryBasegtsFromFile
=============
*/
static void CL_WebHost_AppendFactoryBasegtsFromFile( const char *filename, clWebFactoryBasegt_t *definitions, int *definitionCount, int maxDefinitions ) {
	void	*fileBuffer;
	int		length;

	fileBuffer = NULL;
	length = FS_ReadFile( filename, &fileBuffer );
	if ( length <= 0 || !fileBuffer ) {
		return;
	}

	CL_WebHost_AppendFactoryBasegtsFromBuffer( filename, (char *)fileBuffer, length, definitions, definitionCount, maxDefinitions );
	FS_FreeFile( fileBuffer );
}

/*
=============
CL_WebHost_LoadFactoryBasegtList
=============
*/
static void CL_WebHost_LoadFactoryBasegtList( clWebFactoryBasegt_t *definitions, int *definitionCount, int maxDefinitions ) {
	char fileList[32768];
	char *cursor;
	int count;

	if ( !definitions || !definitionCount || maxDefinitions <= 0 ) {
		return;
	}

	*definitionCount = 0;
	CL_WebHost_AppendFactoryBasegtsFromFile( "scripts/factories.txt", definitions, definitionCount, maxDefinitions );
	count = FS_GetFileList( "scripts", ".factories", fileList, sizeof( fileList ) );
	cursor = fileList;
	for ( ; count > 0 && *cursor && *definitionCount < maxDefinitions; count-- ) {
		char path[MAX_QPATH];

		Com_sprintf( path, sizeof( path ), "scripts/%s", cursor );
		CL_WebHost_AppendFactoryBasegtsFromFile( path, definitions, definitionCount, maxDefinitions );
		cursor += strlen( cursor ) + 1;
	}

	count = FS_GetFileList( "scripts", ".factory", fileList, sizeof( fileList ) );
	cursor = fileList;
	for ( ; count > 0 && *cursor && *definitionCount < maxDefinitions; count-- ) {
		char path[MAX_QPATH];

		Com_sprintf( path, sizeof( path ), "scripts/%s", cursor );
		CL_WebHost_AppendFactoryBasegtsFromFile( path, definitions, definitionCount, maxDefinitions );
		cursor += strlen( cursor ) + 1;
	}
}

/*
=============
CL_WebHost_AppendFactoryDefinitionJson
=============
*/
static void CL_WebHost_AppendFactoryDefinitionJson( const clWebFactoryDefinition_t *definition, char *buffer, size_t bufferSize, int *entryCount ) {
	clWebJsonBuilder_t builder;

	if ( !definition || !definition->id[0] || !buffer || !entryCount ) {
		return;
	}

	builder.buffer = buffer;
	builder.bufferSize = bufferSize;
	builder.count = *entryCount;
	CL_WebHost_BeginJsonItem( &builder );
	Q_strcat( buffer, bufferSize, "{\"sysname\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, definition->id );
	Q_strcat( buffer, bufferSize, "\",\"title\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, definition->title );
	Q_strcat( buffer, bufferSize, "\",\"basegt\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, definition->basegt );
	Q_strcat( buffer, bufferSize, "\"" );
	if ( definition->author[0] ) {
		Q_strcat( buffer, bufferSize, ",\"author\":\"" );
		CL_WebHost_AppendJsonEscaped( buffer, bufferSize, definition->author );
		Q_strcat( buffer, bufferSize, "\"" );
	}
	if ( definition->description[0] ) {
		Q_strcat( buffer, bufferSize, ",\"description\":\"" );
		CL_WebHost_AppendJsonEscaped( buffer, bufferSize, definition->description );
		Q_strcat( buffer, bufferSize, "\"" );
	}
	Q_strcat( buffer, bufferSize, ",\"settings\":" );
	Q_strcat( buffer, bufferSize, definition->settingsJson[0] ? definition->settingsJson : "{}" );
	Q_strcat( buffer, bufferSize, "}" );
	( *entryCount )++;
}

/*
=============
CL_WebHost_AppendFactoryDefinitionsFromBuffer
=============
*/
static void CL_WebHost_AppendFactoryDefinitionsFromBuffer( const char *filename, char *data, int dataLength, char *buffer, size_t bufferSize, char seenIds[][MAX_QPATH], int *entryCount ) {
	clWebFactoryParseState_t state;

	if ( !data || dataLength <= 0 || !buffer || !seenIds || !entryCount ) {
		return;
	}

	state.cursor = data;
	state.end = data + dataLength;
	state.filename = filename;
	state.line = 1;

	CL_WebFactory_SkipWhitespace( &state );
	if ( state.cursor >= state.end ) {
		return;
	}

	if ( *state.cursor == '{' ) {
		clWebFactoryDefinition_t definition;

		if ( !CL_WebFactory_ParseDefinition( &state, &definition ) ) {
			return;
		}
		if ( !CL_WebHost_StringListContains( seenIds, *entryCount, definition.id ) && *entryCount < CL_WEB_MAX_FACTORY_DEFINITIONS ) {
			Q_strncpyz( seenIds[*entryCount], definition.id, MAX_QPATH );
			CL_WebHost_AppendFactoryDefinitionJson( &definition, buffer, bufferSize, entryCount );
		}
		return;
	}

	if ( !CL_WebFactory_ParseExpectedChar( &state, '[' ) ) {
		return;
	}

	CL_WebFactory_SkipWhitespace( &state );
	if ( state.cursor < state.end && *state.cursor == ']' ) {
		state.cursor++;
		return;
	}

	while ( state.cursor < state.end ) {
		clWebFactoryDefinition_t definition;

		if ( !CL_WebFactory_ParseDefinition( &state, &definition ) ) {
			return;
		}
		if ( !CL_WebHost_StringListContains( seenIds, *entryCount, definition.id ) && *entryCount < CL_WEB_MAX_FACTORY_DEFINITIONS ) {
			Q_strncpyz( seenIds[*entryCount], definition.id, MAX_QPATH );
			CL_WebHost_AppendFactoryDefinitionJson( &definition, buffer, bufferSize, entryCount );
		}

		CL_WebFactory_SkipWhitespace( &state );
		if ( state.cursor >= state.end ) {
			return;
		}
		if ( *state.cursor == ',' ) {
			state.cursor++;
			CL_WebFactory_SkipWhitespace( &state );
			if ( state.cursor < state.end && *state.cursor == ']' ) {
				state.cursor++;
				return;
			}
			continue;
		}
		if ( *state.cursor == ']' ) {
			state.cursor++;
			return;
		}

		CL_WebFactory_ReportParseError( &state, "expected ',' or ']'" );
		return;
	}
}

/*
=============
CL_WebHost_AppendFactoryDefinitionsFromFile
=============
*/
static void CL_WebHost_AppendFactoryDefinitionsFromFile( const char *filename, char *buffer, size_t bufferSize, char seenIds[][MAX_QPATH], int *entryCount ) {
	void	*fileBuffer;
	int		length;

	fileBuffer = NULL;
	length = FS_ReadFile( filename, &fileBuffer );
	if ( length <= 0 || !fileBuffer ) {
		return;
	}

	CL_WebHost_AppendFactoryDefinitionsFromBuffer( filename, (char *)fileBuffer, length, buffer, bufferSize, seenIds, entryCount );
	FS_FreeFile( fileBuffer );
}

/*
=============
CL_WebHost_BuildFactoryListJson
=============
*/
static void CL_WebHost_BuildFactoryListJson( char *buffer, size_t bufferSize ) {
	char fileList[32768];
	char seenIds[CL_WEB_MAX_FACTORY_DEFINITIONS][MAX_QPATH];
	char *cursor;
	int count;
	int entryCount;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	Com_Memset( seenIds, 0, sizeof( seenIds ) );
	entryCount = 0;
	buffer[0] = '\0';
	Q_strcat( buffer, bufferSize, "[" );

	CL_WebHost_AppendFactoryDefinitionsFromFile( "scripts/factories.txt", buffer, bufferSize, seenIds, &entryCount );
	count = FS_GetFileList( "scripts", ".factories", fileList, sizeof( fileList ) );
	cursor = fileList;
	for ( ; count > 0 && *cursor; count-- ) {
		char path[MAX_QPATH];

		Com_sprintf( path, sizeof( path ), "scripts/%s", cursor );
		CL_WebHost_AppendFactoryDefinitionsFromFile( path, buffer, bufferSize, seenIds, &entryCount );
		cursor += strlen( cursor ) + 1;
	}

	count = FS_GetFileList( "scripts", ".factory", fileList, sizeof( fileList ) );
	cursor = fileList;
	for ( ; count > 0 && *cursor; count-- ) {
		char path[MAX_QPATH];

		Com_sprintf( path, sizeof( path ), "scripts/%s", cursor );
		CL_WebHost_AppendFactoryDefinitionsFromFile( path, buffer, bufferSize, seenIds, &entryCount );
		cursor += strlen( cursor ) + 1;
	}

	Q_strcat( buffer, bufferSize, "]" );
}

/*
=============
CL_WebHost_BuildDemoListJson
=============
*/
static void CL_WebHost_BuildDemoListJson( char *buffer, size_t bufferSize ) {
	char fileList[32768];
	char demoExt[32];
	char *cursor;
	int count;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	Q_strcat( buffer, bufferSize, "[" );
	Com_sprintf( demoExt, sizeof( demoExt ), "dm_%d", NET_DemoProtocol() );
	count = FS_GetFileList( "demos", demoExt, fileList, sizeof( fileList ) );
	cursor = fileList;
	for ( ; count > 0 && *cursor; count-- ) {
		char demoName[MAX_QPATH];
		clWebJsonBuilder_t builder;

		Q_strncpyz( demoName, cursor, sizeof( demoName ) );

		builder.buffer = buffer;
		builder.bufferSize = bufferSize;
		builder.count = ( buffer[1] != '\0' ) ? 1 : 0;
		CL_WebHost_JsonAppendDemoCallback( &builder, demoName );
		cursor += strlen( cursor ) + 1;
	}
	Q_strcat( buffer, bufferSize, "]" );
}

/*
=============
CL_WebHost_BuildFriendListJson
=============
*/
static void CL_WebHost_BuildFriendListJson( char *buffer, size_t bufferSize ) {
	int friendCount;
	int index;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	Q_strcat( buffer, bufferSize, "[" );

	if ( !CL_WebHost_HasSteamIdentity() ) {
		CL_LogWebHostMatchmakingExportLifecycle( "friend-list", "Steam social export unavailable for current compatibility lane" );
		Q_strcat( buffer, bufferSize, "]" );
		return;
	}

	friendCount = QL_Steamworks_GetFriendCount( CL_WEB_FRIEND_FLAGS );
	for ( index = 0; index < friendCount; index++ ) {
		uint32_t idLow;
		uint32_t idHigh;
		ql_steam_friend_summary_t summary;
		char friendJson[1024];
		clWebJsonBuilder_t builder;

		if ( !QL_Steamworks_GetFriendByIndex( index, CL_WEB_FRIEND_FLAGS, &idLow, &idHigh ) ) {
			continue;
		}
		if ( !QL_Steamworks_GetFriendSummary( idLow, idHigh, &summary ) ) {
			continue;
		}

		CL_Steam_FormatFriendSummaryJson( &summary, friendJson, sizeof( friendJson ) );

		builder.buffer = buffer;
		builder.bufferSize = bufferSize;
		builder.count = ( buffer[1] != '\0' ) ? 1 : 0;
		CL_WebHost_BeginJsonItem( &builder );
		Q_strcat( buffer, bufferSize, friendJson );
	}

	Q_strcat( buffer, bufferSize, "]" );
}

typedef struct {
	char	*buffer;
	size_t	bufferSize;
	int		count;
} clWebConfigArrayContext_t;

/*
=============
CL_WebHost_ConfigCvarCallback
=============
*/
static void CL_WebHost_ConfigCvarCallback( const cvar_t *var, void *userData ) {
	clWebConfigArrayContext_t *context;
	char value[MAX_CVAR_VALUE_STRING];

	context = (clWebConfigArrayContext_t *)userData;
	if ( !var || !context || !context->buffer ) {
		return;
	}

	if ( !var->name || !var->name[0] ) {
		return;
	}

	if ( context->count > 0 ) {
		Q_strcat( context->buffer, context->bufferSize, "," );
	}
	context->count++;

	value[0] = '\0';
	if ( var->latchedString && var->latchedString[0] ) {
		Q_strncpyz( value, var->latchedString, sizeof( value ) );
	} else if ( var->string ) {
		Q_strncpyz( value, var->string, sizeof( value ) );
	}

	Q_strcat( context->buffer, context->bufferSize, "\"" );
	CL_WebHost_AppendJsonEscaped( context->buffer, context->bufferSize, var->name );
	Q_strcat( context->buffer, context->bufferSize, "\":\"" );
	CL_WebHost_AppendJsonEscaped( context->buffer, context->bufferSize, value );
	Q_strcat( context->buffer, context->bufferSize, "\"" );
}

/*
=============
CL_WebHost_ConfigBindCallback
=============
*/
static void CL_WebHost_ConfigBindCallback( int keynum, const char *keyName, const char *binding, void *userData ) {
	clWebConfigArrayContext_t *context;

	context = (clWebConfigArrayContext_t *)userData;
	if ( !context || !context->buffer || !binding || !binding[0] ) {
		return;
	}

	if ( context->count > 0 ) {
		Q_strcat( context->buffer, context->bufferSize, "," );
	}
	context->count++;

	Q_strcat( context->buffer, context->bufferSize, "{\"id\":" );
	Q_strcat( context->buffer, context->bufferSize, va( "%d", keynum ) );
	Q_strcat( context->buffer, context->bufferSize, ",\"key\":\"" );
	CL_WebHost_AppendJsonEscaped( context->buffer, context->bufferSize, keyName ? keyName : "" );
	Q_strcat( context->buffer, context->bufferSize, "\",\"value\":\"" );
	CL_WebHost_AppendJsonEscaped( context->buffer, context->bufferSize, binding );
	Q_strcat( context->buffer, context->bufferSize, "\"}" );
}

/*
=============
CL_WebHost_BuildConfigJson
=============
*/
static void CL_WebHost_BuildConfigJson( char *buffer, size_t bufferSize ) {
	char cvarJson[CL_WEB_JSON_BUFFER_SIZE];
	char bindJson[CL_WEB_JSON_BUFFER_SIZE];
	char steamId[32];
	clWebConfigArrayContext_t cvarContext;
	clWebConfigArrayContext_t bindContext;
	const char *onlineServicesMode;
	const char *onlineServicesPolicy;
	const char *matchmakingProvider;
	const char *matchmakingPolicy;
	const char *workshopProvider;
	const char *workshopPolicy;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	CL_WebHost_RefreshBootstrapProperties();
	CL_WebHost_FormatSteamId( cl_webHost.steamIdLow, cl_webHost.steamIdHigh, steamId, sizeof( steamId ) );
	onlineServicesMode = CL_GetWebHostModeLabel();
	onlineServicesPolicy = CL_GetWebHostPolicyLabel();
	matchmakingProvider = CL_GetWebHostMatchmakingProviderLabel();
	matchmakingPolicy = CL_GetWebHostMatchmakingPolicyLabel();
	workshopProvider = CL_GetWebHostWorkshopProviderLabel();
	workshopPolicy = CL_GetWebHostWorkshopPolicyLabel();

	cvarJson[0] = '\0';
	bindJson[0] = '\0';

	cvarContext.buffer = cvarJson;
	cvarContext.bufferSize = sizeof( cvarJson );
	cvarContext.count = 0;
	Cvar_EnumerateVariables( CL_WebHost_ConfigCvarCallback, &cvarContext );

	bindContext.buffer = bindJson;
	bindContext.bufferSize = sizeof( bindJson );
	bindContext.count = 0;
	Key_EnumerateBindings( CL_WebHost_ConfigBindCallback, &bindContext );

	Com_sprintf(
		buffer,
		bufferSize,
		"{\"version\":\"%s\",\"steamId\":\"%s\",\"playerName\":\"",
		QL_ENGINE_VERSION,
		steamId
	);
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, cl_webHost.playerName );
	Q_strcat( buffer, bufferSize, "\",\"appId\":" );
	Q_strcat( buffer, bufferSize, va( "%u", cl_webHost.appId ) );
	Q_strcat( buffer, bufferSize, ",\"onlineServicesMode\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, onlineServicesMode );
	Q_strcat( buffer, bufferSize, "\",\"onlineServicesPolicy\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, onlineServicesPolicy );
	Q_strcat( buffer, bufferSize, "\",\"matchmakingProvider\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, matchmakingProvider );
	Q_strcat( buffer, bufferSize, "\",\"matchmakingPolicy\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, matchmakingPolicy );
	Q_strcat( buffer, bufferSize, "\",\"workshopProvider\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, workshopProvider );
	Q_strcat( buffer, bufferSize, "\",\"workshopPolicy\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, workshopPolicy );
	Q_strcat( buffer, bufferSize, "\",\"browserVisible\":" );
	Q_strcat( buffer, bufferSize, cl_webHost.browserVisible ? "1" : "0" );
	Q_strcat( buffer, bufferSize, ",\"browserActive\":" );
	Q_strcat( buffer, bufferSize, cl_webHost.browserActive ? "1" : "0" );
	Q_strcat( buffer, bufferSize, ",\"url\":\"" );
	CL_WebHost_AppendJsonEscaped( buffer, bufferSize, cl_webHost.currentUrl );
	Q_strcat( buffer, bufferSize, "\",\"cvars\":{" );
	Q_strcat( buffer, bufferSize, cvarJson );
	Q_strcat( buffer, bufferSize, "},\"binds\":[" );
	Q_strcat( buffer, bufferSize, bindJson );
	Q_strcat( buffer, bufferSize, "]}" );
}

/*
=============
CL_WebHost_UpdateBrowserCvarCache

Pushes one native cvar value back into the injected qz_instance cache so WebUI
GetCvar calls observe the engine value after queued set, reset, or get requests.
=============
*/
static void CL_WebHost_UpdateBrowserCvarCache( const char *name, const char *value ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	char escapedName[MAX_CVAR_VALUE_STRING * 2];
	char escapedValue[MAX_CVAR_VALUE_STRING * 2];
	char script[MAX_CVAR_VALUE_STRING * 4 + 128];

	if ( !cl_webHost.liveAwesomium || !name || !name[0] ) {
		return;
	}

	CL_WebHost_JsonEscape( name, escapedName, sizeof( escapedName ) );
	CL_WebHost_JsonEscape( value ? value : "", escapedValue, sizeof( escapedValue ) );
	Com_sprintf(
		script,
		sizeof( script ),
		"(function(){if(window.__qlr_set_native_cvar){window.__qlr_set_native_cvar(\"%s\",\"%s\");}})();",
		escapedName,
		escapedValue
	);
	CL_Awesomium_ExecuteJavascript( script, "" );
#else
	(void)name;
	(void)value;
#endif
}

/*
=============
CL_WebHost_ProcessNativeJavascriptRequest

Executes one request emitted by the injected qz_instance bridge using the same
command-buffer and cvar APIs as the recovered retail QLJSHandler methods.
=============
*/
static void CL_WebHost_ProcessNativeJavascriptRequest( const char *request ) {
	const char *payload;
	int kindLength;
	char kind[16];
	int i;

	if ( !request || !request[0] ) {
		return;
	}

	payload = strchr( request, '\n' );
	if ( !payload ) {
		return;
	}

	kindLength = (int)( payload - request );
	if ( kindLength <= 0 ) {
		return;
	}
	if ( kindLength >= (int)sizeof( kind ) ) {
		kindLength = (int)sizeof( kind ) - 1;
	}
	for ( i = 0; i < kindLength; i++ ) {
		kind[i] = request[i];
	}
	kind[kindLength] = '\0';
	payload++;

	if ( !Q_stricmp( kind, "cmd" ) ) {
		if ( payload[0] ) {
			Cbuf_ExecuteText( EXEC_APPEND, va( "%s\n", payload ) );
		}
		return;
	}

	if ( !Q_stricmp( kind, "get" ) ) {
		char name[MAX_CVAR_VALUE_STRING];
		char value[MAX_CVAR_VALUE_STRING];

		if ( !payload[0] ) {
			return;
		}
		Q_strncpyz( name, payload, sizeof( name ) );
		Cvar_VariableStringBuffer( name, value, sizeof( value ) );
		CL_WebHost_UpdateBrowserCvarCache( name, value );
		return;
	}

	if ( !Q_stricmp( kind, "set" ) ) {
		const char *valueStart;
		int nameLength;
		char name[MAX_CVAR_VALUE_STRING];
		char value[MAX_CVAR_VALUE_STRING];

		valueStart = strchr( payload, '\n' );
		if ( !valueStart ) {
			return;
		}

		nameLength = (int)( valueStart - payload );
		if ( nameLength <= 0 ) {
			return;
		}
		if ( nameLength >= (int)sizeof( name ) ) {
			nameLength = (int)sizeof( name ) - 1;
		}
		for ( i = 0; i < nameLength; i++ ) {
			name[i] = payload[i];
		}
		name[nameLength] = '\0';

		valueStart++;
		Q_strncpyz( value, valueStart, sizeof( value ) );
		Cvar_Set( name, value );
		CL_WebHost_UpdateBrowserCvarCache( name, value );
		return;
	}

	if ( !Q_stricmp( kind, "reset" ) ) {
		char name[MAX_CVAR_VALUE_STRING];
		char value[MAX_CVAR_VALUE_STRING];

		if ( !payload[0] ) {
			return;
		}
		Q_strncpyz( name, payload, sizeof( name ) );
		Cvar_Reset( name );
		Cvar_VariableStringBuffer( name, value, sizeof( value ) );
		CL_WebHost_UpdateBrowserCvarCache( name, value );
	}
}

/*
=============
CL_WebHost_PumpNativeJavascriptRequests

Drains a bounded number of qz_instance requests from the live Awesomium page each
frame, matching the retail native handler ownership without blocking rendering.
=============
*/
static void CL_WebHost_PumpNativeJavascriptRequests( void ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	int i;
	qboolean handledRequest;

	if ( !cl_webHost.liveAwesomium ) {
		return;
	}
	if ( cl_webHost.frameSequence < cl_webHost.nextNativeRequestPollFrame ) {
		return;
	}
	if ( CL_Awesomium_IsLoading() ) {
		cl_webHost.nextNativeRequestPollFrame = cl_webHost.frameSequence + CL_WEB_NATIVE_REQUEST_LOADING_POLL_FRAMES;
		return;
	}

	handledRequest = qfalse;
	for ( i = 0; i < CL_WEB_NATIVE_REQUESTS_PER_FRAME; i++ ) {
		char request[MAX_STRING_CHARS];

		if ( !CL_Awesomium_PopJavascriptRequest( request, sizeof( request ) ) ) {
			break;
		}
		if ( request[0] ) {
			CL_WebHost_ProcessNativeJavascriptRequest( request );
			handledRequest = qtrue;
		}
	}
	cl_webHost.nextNativeRequestPollFrame = cl_webHost.frameSequence + ( handledRequest ? CL_WEB_NATIVE_REQUEST_BUSY_POLL_FRAMES : CL_WEB_NATIVE_REQUEST_IDLE_POLL_FRAMES );
#endif
}

/*
=============
CL_WebHost_WriteJavascriptJsonCall

Builds a script around a large JSON literal without routing that literal
through Com_sprintf's 32K shared scratch buffer.
=============
*/
static qboolean CL_WebHost_WriteJavascriptJsonCall( char *script, int scriptSize, const char *prefix, const char *json, const char *suffix ) {
	if ( !script || scriptSize <= 0 || !prefix || !json || !suffix ) {
		return qfalse;
	}

	Q_strncpyz( script, prefix, scriptSize );
	Q_strcat( script, scriptSize, json );
	Q_strcat( script, scriptSize, suffix );
	return qtrue;
}

/*
=============
CL_WebHost_ExecuteConfigSnapshot

Pushes the current native cvar/bind snapshot into the browser helper using
bounded appends so oversized config payloads cannot trip Com_sprintf.
=============
*/
static qboolean CL_WebHost_ExecuteConfigSnapshot( const char *configJson ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	static const char prefix[] = "(function(){if(window.__qlr_apply_native_config){window.__qlr_apply_native_config(";
	static const char suffix[] = ");}})();";
	char *script;
	size_t scriptSize;
	qboolean executed;

	if ( !configJson || !configJson[0] ) {
		return qfalse;
	}

	scriptSize = strlen( prefix ) + strlen( configJson ) + strlen( suffix ) + 1;
	script = (char *)Z_Malloc( (int)scriptSize );
	if ( !script ) {
		return qfalse;
	}

	executed = CL_WebHost_WriteJavascriptJsonCall( script, (int)scriptSize, prefix, configJson, suffix ) && CL_Awesomium_ExecuteJavascript( script, "" );
	Z_Free( script );
	return executed;
#else
	(void)configJson;
	return qfalse;
#endif
}

/*
=============
CL_WebHost_SyncConfigSnapshot

Synchronizes the browser-side qz config cache from the native client cvar/bind
state, giving WebUI GetConfig/GetCvar callers a retail-like native data source.
=============
*/
static void CL_WebHost_SyncConfigSnapshot( void ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	char *configJson;

	if ( !cl_webHost.liveAwesomium ) {
		return;
	}
	if ( cl_webHost.configSynced && cl_webHost.frameSequence < cl_webHost.nextConfigSyncFrame ) {
		return;
	}
	if ( CL_Awesomium_IsLoading() ) {
		cl_webHost.nextConfigSyncFrame = cl_webHost.frameSequence + CL_WEB_NATIVE_REQUEST_LOADING_POLL_FRAMES;
		return;
	}

	configJson = (char *)Z_Malloc( CL_WEB_NATIVE_CONFIG_BUFFER_SIZE );
	if ( !configJson ) {
		return;
	}
	configJson[0] = '\0';
	CL_WebHost_BuildConfigJson( configJson, CL_WEB_NATIVE_CONFIG_BUFFER_SIZE );

	if ( CL_WebHost_ExecuteConfigSnapshot( configJson ) ) {
		cl_webHost.configSynced = qtrue;
		cl_webHost.nextConfigSyncFrame = cl_webHost.frameSequence + CL_WEB_NATIVE_CONFIG_SYNC_FRAMES;
	}

	Z_Free( configJson );
#endif
}

/*
=============
CL_WebHost_ExecuteMapCatalogBatch

Adds one bounded top-level arena batch to the pending browser-side map cache.
=============
*/
static qboolean CL_WebHost_ExecuteMapCatalogBatch( const char *entries, size_t entryLength ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	char *script;
	size_t scriptSize;
	qboolean executed;
	int result;

	if ( !entries || entryLength == 0 ) {
		return qtrue;
	}

	scriptSize = entryLength + 128;
	script = (char *)Z_Malloc( (int)scriptSize );
	if ( !script ) {
		return qfalse;
	}

	Com_sprintf(
		script,
		scriptSize,
		"(function(){return(window.__qlr_add_native_maps&&window.__qlr_add_native_maps([%.*s]))?1:0;})()",
		(int)entryLength,
		entries
	);
	executed = CL_Awesomium_ExecuteJavascriptInteger( script, "", &result ) && result != 0;
	Z_Free( script );
	return executed;
#else
	(void)entries;
	(void)entryLength;
	return qfalse;
#endif
}

/*
=============
CL_WebHost_QueueMapCatalogEntry

Extends the current arena transfer batch, flushing when the next entry would
make the JavaScript payload too large for a conservative Awesomium hand-off.
=============
*/
static qboolean CL_WebHost_QueueMapCatalogEntry( const char **batchStart, const char **batchEnd, size_t *batchLength, const char *entryStart, size_t entryLength ) {
	if ( !batchStart || !batchEnd || !batchLength || !entryStart || entryLength == 0 ) {
		return qtrue;
	}

	if ( *batchStart && *batchLength + 1 + entryLength > CL_WEB_MAP_SYNC_CHUNK_CHARS ) {
		if ( !CL_WebHost_ExecuteMapCatalogBatch( *batchStart, *batchLength ) ) {
			return qfalse;
		}
		*batchStart = NULL;
		*batchEnd = NULL;
		*batchLength = 0;
	}

	if ( !*batchStart ) {
		*batchStart = entryStart;
	}

	*batchEnd = entryStart + entryLength;
	*batchLength = (size_t)( *batchEnd - *batchStart );
	return qtrue;
}

/*
=============
CL_WebHost_QueryBrowserCatalogCount

Counts entries from the live WebUI module export when available, falling back to
the qz_instance getter so runtime logs can verify the data the bundle observes.
=============
*/
static qboolean CL_WebHost_QueryBrowserCatalogCount( const char *modulePath, const char *getterName, int *outCount ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	char script[1024];

	if ( outCount ) {
		*outCount = -1;
	}
	if ( !getterName || !getterName[0] ) {
		return qfalse;
	}

	Com_sprintf(
		script,
		sizeof( script ),
		"(function(){try{var has=Object.prototype.hasOwnProperty;var o=null;var p='%s';if(p&&window.req){try{o=window.req(p);}catch(e){}}if(!o&&window.qz_instance&&typeof window.qz_instance.%s==='function'){o=window.qz_instance.%s();}var c=0;for(var k in o){if(has.call(o,k)){c++;}}return c;}catch(e){return -1;}})()",
		modulePath ? modulePath : "",
		getterName,
		getterName
	);
	return CL_Awesomium_ExecuteJavascriptInteger( script, "", outCount );
#else
	(void)modulePath;
	(void)getterName;
	if ( outCount ) {
		*outCount = -1;
	}
	return qfalse;
#endif
}

/*
=============
CL_WebHost_MapCatalogBridgeReady

Verifies that the injected browser bridge has installed the native map-transfer
hooks before the client starts streaming arena data.
=============
*/
static qboolean CL_WebHost_MapCatalogBridgeReady( void ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	int ready;

	if ( !CL_Awesomium_ExecuteJavascriptInteger(
		"(function(){return(window.__qlr_browser_helpers_ready&&window.qz_instance&&typeof window.qz_instance.GetMapList==='function'&&typeof window.qz_instance.GetFactoryList==='function'&&typeof window.__qlr_begin_native_maps==='function'&&typeof window.__qlr_add_native_maps==='function'&&typeof window.__qlr_commit_native_maps==='function'&&typeof window.__qlr_begin_native_factories==='function'&&typeof window.__qlr_add_native_factories==='function'&&typeof window.__qlr_commit_native_factories==='function')?1:0;})()",
		"",
		&ready ) ) {
		return qfalse;
	}

	return ready != 0;
#else
	return qfalse;
#endif
}

/*
=============
CL_WebHost_ExecuteMapCatalogBatches

Streams the generated JSON array into the browser in top-level object batches,
then commits the pending map cache in one synchronous browser-side swap.
=============
*/
static qboolean CL_WebHost_ExecuteMapCatalogBatches( const char *mapJson, size_t mapJsonLength ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	const char *arrayEnd;
	const char *cursor;
	const char *entryStart;
	const char *batchStart;
	const char *batchEnd;
	size_t batchLength;
	int depth;
	int result;
	qboolean inString;
	qboolean escaped;

	if ( !mapJson || mapJsonLength < 2 || mapJson[0] != '[' || mapJson[mapJsonLength - 1] != ']' ) {
		return qfalse;
	}

	if ( !CL_WebHost_MapCatalogBridgeReady() ) {
		return qfalse;
	}
	if ( !CL_Awesomium_ExecuteJavascriptInteger( "(function(){return(window.__qlr_begin_native_maps&&window.__qlr_begin_native_maps())?1:0;})()", "", &result ) || result == 0 ) {
		return qfalse;
	}

	arrayEnd = mapJson + mapJsonLength - 1;
	entryStart = mapJson + 1;
	batchStart = NULL;
	batchEnd = NULL;
	batchLength = 0;
	depth = 0;
	inString = qfalse;
	escaped = qfalse;

	for ( cursor = mapJson + 1; cursor < arrayEnd; cursor++ ) {
		char ch;

		ch = *cursor;
		if ( inString ) {
			if ( escaped ) {
				escaped = qfalse;
			} else if ( ch == '\\' ) {
				escaped = qtrue;
			} else if ( ch == '"' ) {
				inString = qfalse;
			}
			continue;
		}

		if ( ch == '"' ) {
			inString = qtrue;
			continue;
		}
		if ( ch == '{' || ch == '[' ) {
			depth++;
			continue;
		}
		if ( ch == '}' || ch == ']' ) {
			if ( depth > 0 ) {
				depth--;
			}
			continue;
		}
		if ( ch == ',' && depth == 0 ) {
			if ( !CL_WebHost_QueueMapCatalogEntry( &batchStart, &batchEnd, &batchLength, entryStart, (size_t)( cursor - entryStart ) ) ) {
				return qfalse;
			}
			entryStart = cursor + 1;
		}
	}

	if ( !CL_WebHost_QueueMapCatalogEntry( &batchStart, &batchEnd, &batchLength, entryStart, (size_t)( arrayEnd - entryStart ) ) ) {
		return qfalse;
	}
	if ( !CL_WebHost_ExecuteMapCatalogBatch( batchStart, batchLength ) ) {
		return qfalse;
	}

	return CL_Awesomium_ExecuteJavascriptInteger( "(function(){return(window.__qlr_commit_native_maps&&window.__qlr_commit_native_maps())?1:0;})()", "", &result ) && result != 0;
#else
	(void)mapJson;
	(void)mapJsonLength;
	return qfalse;
#endif
}

/*
=============
CL_WebHost_SyncMapCatalogSnapshot

Pushes the retail arena catalog into the live Awesomium qz map cache after the
launcher document is ready. Keeping this out of the startup config avoids large
bootstrap script literals while preserving synchronous GetMapList callers.
=============
*/
static void CL_WebHost_SyncMapCatalogSnapshot( void ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	char *mapJson;
	size_t mapJsonLength;

	if ( !cl_webHost.liveAwesomium || !cl_webHost.documentReady || !cl_webHost.qzInstanceBound ) {
		return;
	}
	if ( cl_webHost.mapCatalogSynced ) {
		return;
	}
	if ( cl_webHost.frameSequence < cl_webHost.nextMapCatalogSyncFrame ) {
		return;
	}
	if ( CL_Awesomium_IsLoading() ) {
		cl_webHost.nextMapCatalogSyncFrame = cl_webHost.frameSequence + CL_WEB_NATIVE_REQUEST_LOADING_POLL_FRAMES;
		return;
	}
	if ( !CL_WebHost_MapCatalogBridgeReady() ) {
		cl_webHost.nextMapCatalogSyncFrame = cl_webHost.frameSequence + CL_WEB_NATIVE_MAP_RETRY_FRAMES;
		return;
	}

	mapJson = (char *)Z_Malloc( CL_WEB_MAP_JSON_BUFFER_SIZE );
	if ( !mapJson ) {
		return;
	}
	mapJson[0] = '\0';
	CL_WebHost_BuildMapListJson( mapJson, CL_WEB_MAP_JSON_BUFFER_SIZE );
	mapJsonLength = strlen( mapJson );
	if ( mapJsonLength < 2 || mapJson[0] != '[' || mapJson[mapJsonLength - 1] != ']' ) {
		Com_DPrintf( "Awesomium map catalog sync skipped malformed map JSON (%u bytes)\n", (unsigned int)mapJsonLength );
		cl_webHost.nextMapCatalogSyncFrame = cl_webHost.frameSequence + CL_WEB_NATIVE_MAP_RETRY_FRAMES;
		Z_Free( mapJson );
		return;
	}

	if ( CL_WebHost_ExecuteMapCatalogBatches( mapJson, mapJsonLength ) ) {
		int qzMapCount;
		int moduleMapCount;

		qzMapCount = -1;
		moduleMapCount = -1;
		CL_WebHost_QueryBrowserCatalogCount( "", "GetMapList", &qzMapCount );
		CL_WebHost_QueryBrowserCatalogCount( "../src/mapdb", "GetMapList", &moduleMapCount );
		cl_webHost.mapCatalogSynced = qtrue;
		cl_webHost.nextMapCatalogSyncFrame = 0;
		Com_DPrintf( "Awesomium map catalog synced (%u bytes, %d qz maps, %d module maps)\n", (unsigned int)mapJsonLength, qzMapCount, moduleMapCount );
	} else {
		cl_webHost.nextMapCatalogSyncFrame = cl_webHost.frameSequence + CL_WEB_NATIVE_MAP_RETRY_FRAMES;
	}

	Z_Free( mapJson );
#endif
}

/*
=============
CL_WebHost_ExecuteFactoryCatalogBatch

Adds one bounded top-level factory batch to the pending browser-side cache.
=============
*/
static qboolean CL_WebHost_ExecuteFactoryCatalogBatch( const char *entries, size_t entryLength ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	char *script;
	size_t scriptSize;
	qboolean executed;
	int result;

	if ( !entries || entryLength == 0 ) {
		return qtrue;
	}

	scriptSize = entryLength + 144;
	script = (char *)Z_Malloc( (int)scriptSize );
	if ( !script ) {
		return qfalse;
	}

	Com_sprintf(
		script,
		scriptSize,
		"(function(){return(window.__qlr_add_native_factories&&window.__qlr_add_native_factories([%.*s]))?1:0;})()",
		(int)entryLength,
		entries
	);
	executed = CL_Awesomium_ExecuteJavascriptInteger( script, "", &result ) && result != 0;
	Z_Free( script );
	return executed;
#else
	(void)entries;
	(void)entryLength;
	return qfalse;
#endif
}

/*
=============
CL_WebHost_QueueFactoryCatalogEntry

Extends the current factory transfer batch, flushing when the next entry would
make the JavaScript payload too large for a conservative Awesomium hand-off.
=============
*/
static qboolean CL_WebHost_QueueFactoryCatalogEntry( const char **batchStart, const char **batchEnd, size_t *batchLength, const char *entryStart, size_t entryLength ) {
	if ( !batchStart || !batchEnd || !batchLength || !entryStart || entryLength == 0 ) {
		return qtrue;
	}

	if ( *batchStart && *batchLength + 1 + entryLength > CL_WEB_FACTORY_SYNC_CHUNK_CHARS ) {
		if ( !CL_WebHost_ExecuteFactoryCatalogBatch( *batchStart, *batchLength ) ) {
			return qfalse;
		}
		*batchStart = NULL;
		*batchEnd = NULL;
		*batchLength = 0;
	}

	if ( !*batchStart ) {
		*batchStart = entryStart;
	}

	*batchEnd = entryStart + entryLength;
	*batchLength = (size_t)( *batchEnd - *batchStart );
	return qtrue;
}

/*
=============
CL_WebHost_ExecuteFactoryCatalogBatches

Streams the generated factory JSON into the browser in top-level object
batches, then commits the pending factory cache in one browser-side swap.
=============
*/
static qboolean CL_WebHost_ExecuteFactoryCatalogBatches( const char *factoryJson, size_t factoryJsonLength ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	const char *arrayEnd;
	const char *cursor;
	const char *entryStart;
	const char *batchStart;
	const char *batchEnd;
	size_t batchLength;
	int depth;
	int result;
	qboolean inString;
	qboolean escaped;

	if ( !factoryJson || factoryJsonLength < 2 || factoryJson[0] != '[' || factoryJson[factoryJsonLength - 1] != ']' ) {
		return qfalse;
	}

	if ( !CL_WebHost_MapCatalogBridgeReady() ) {
		return qfalse;
	}
	if ( !CL_Awesomium_ExecuteJavascriptInteger( "(function(){return(window.__qlr_begin_native_factories&&window.__qlr_begin_native_factories())?1:0;})()", "", &result ) || result == 0 ) {
		return qfalse;
	}

	arrayEnd = factoryJson + factoryJsonLength - 1;
	entryStart = factoryJson + 1;
	batchStart = NULL;
	batchEnd = NULL;
	batchLength = 0;
	depth = 0;
	inString = qfalse;
	escaped = qfalse;

	for ( cursor = factoryJson + 1; cursor < arrayEnd; cursor++ ) {
		char ch;

		ch = *cursor;
		if ( inString ) {
			if ( escaped ) {
				escaped = qfalse;
			} else if ( ch == '\\' ) {
				escaped = qtrue;
			} else if ( ch == '"' ) {
				inString = qfalse;
			}
			continue;
		}

		if ( ch == '"' ) {
			inString = qtrue;
			continue;
		}
		if ( ch == '{' || ch == '[' ) {
			depth++;
			continue;
		}
		if ( ch == '}' || ch == ']' ) {
			if ( depth > 0 ) {
				depth--;
			}
			continue;
		}
		if ( ch == ',' && depth == 0 ) {
			if ( !CL_WebHost_QueueFactoryCatalogEntry( &batchStart, &batchEnd, &batchLength, entryStart, (size_t)( cursor - entryStart ) ) ) {
				return qfalse;
			}
			entryStart = cursor + 1;
		}
	}

	if ( !CL_WebHost_QueueFactoryCatalogEntry( &batchStart, &batchEnd, &batchLength, entryStart, (size_t)( arrayEnd - entryStart ) ) ) {
		return qfalse;
	}
	if ( !CL_WebHost_ExecuteFactoryCatalogBatch( batchStart, batchLength ) ) {
		return qfalse;
	}

	return CL_Awesomium_ExecuteJavascriptInteger( "(function(){return(window.__qlr_commit_native_factories&&window.__qlr_commit_native_factories())?1:0;})()", "", &result ) && result != 0;
#else
	(void)factoryJson;
	(void)factoryJsonLength;
	return qfalse;
#endif
}

/*
=============
CL_WebHost_SyncFactoryCatalogSnapshot

Keeps the browser-side factory list synchronized with the native factory files.
This complements map catalog sync because retail Start Match derives the active
gametype from the selected factory before filtering arenas.
=============
*/
static void CL_WebHost_SyncFactoryCatalogSnapshot( void ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	char *factoryJson;
	size_t factoryJsonLength;

	if ( !cl_webHost.liveAwesomium || !cl_webHost.documentReady || !cl_webHost.qzInstanceBound ) {
		return;
	}
	if ( cl_webHost.factoryCatalogSynced ) {
		return;
	}
	if ( cl_webHost.frameSequence < cl_webHost.nextFactoryCatalogSyncFrame ) {
		return;
	}
	if ( CL_Awesomium_IsLoading() ) {
		cl_webHost.nextFactoryCatalogSyncFrame = cl_webHost.frameSequence + CL_WEB_NATIVE_REQUEST_LOADING_POLL_FRAMES;
		return;
	}
	if ( !CL_WebHost_MapCatalogBridgeReady() ) {
		cl_webHost.nextFactoryCatalogSyncFrame = cl_webHost.frameSequence + CL_WEB_NATIVE_FACTORY_RETRY_FRAMES;
		return;
	}

	factoryJson = (char *)Z_Malloc( CL_WEB_FACTORY_JSON_BUFFER_SIZE );
	if ( !factoryJson ) {
		return;
	}
	factoryJson[0] = '\0';
	CL_WebHost_BuildFactoryListJson( factoryJson, CL_WEB_FACTORY_JSON_BUFFER_SIZE );
	factoryJsonLength = strlen( factoryJson );
	if ( factoryJsonLength < 2 || factoryJson[0] != '[' || factoryJson[factoryJsonLength - 1] != ']' ) {
		Com_DPrintf( "Awesomium factory catalog sync skipped malformed factory JSON (%u bytes)\n", (unsigned int)factoryJsonLength );
		cl_webHost.nextFactoryCatalogSyncFrame = cl_webHost.frameSequence + CL_WEB_NATIVE_FACTORY_RETRY_FRAMES;
		Z_Free( factoryJson );
		return;
	}

	if ( CL_WebHost_ExecuteFactoryCatalogBatches( factoryJson, factoryJsonLength ) ) {
		int qzFactoryCount;
		int moduleFactoryCount;

		qzFactoryCount = -1;
		moduleFactoryCount = -1;
		CL_WebHost_QueryBrowserCatalogCount( "", "GetFactoryList", &qzFactoryCount );
		CL_WebHost_QueryBrowserCatalogCount( "../src/factories", "GetFactoryList", &moduleFactoryCount );
		cl_webHost.factoryCatalogSynced = qtrue;
		cl_webHost.nextFactoryCatalogSyncFrame = 0;
		Com_DPrintf( "Awesomium factory catalog synced (%u bytes, %d qz factories, %d module factories)\n", (unsigned int)factoryJsonLength, qzFactoryCount, moduleFactoryCount );
	} else {
		cl_webHost.nextFactoryCatalogSyncFrame = cl_webHost.frameSequence + CL_WEB_NATIVE_FACTORY_RETRY_FRAMES;
	}

	Z_Free( factoryJson );
#endif
}

/*
=============
CL_WebHost_RequestCursorPosition
=============
*/
static qboolean CL_WebHost_RequestCursorPosition( int *x, int *y ) {
	if ( cl_webHost.cursorPositionValid && cl_webHost.viewInitialised && ( cl_webHost.browserVisible || cl_webHost.browserActive ) ) {
		if ( x ) {
			*x = cl_webHost.cursorX;
		}
		if ( y ) {
			*y = cl_webHost.cursorY;
		}

		return qtrue;
	}

#if defined( _WIN32 )
	POINT point;

	if ( x ) {
		*x = 0;
	}
	if ( y ) {
		*y = 0;
	}

	if ( !GetCursorPos( &point ) ) {
		return qfalse;
	}

	if ( g_wv.hWnd ) {
		ScreenToClient( g_wv.hWnd, &point );
	}

	if ( x ) {
		*x = point.x;
	}
	if ( y ) {
		*y = point.y;
	}

	return qtrue;
#else
	if ( x ) {
		*x = 0;
	}
	if ( y ) {
		*y = 0;
	}
	return qfalse;
#endif
}

/*
=============
CL_WebHost_PathIsSafeRelative
=============
*/
static qboolean CL_WebHost_PathIsSafeRelative( const char *path ) {
	if ( !path || !path[0] ) {
		return qfalse;
	}

	if ( strstr( path, ".." ) || strstr( path, "::" ) || strchr( path, ':' ) ) {
		return qfalse;
	}

	if ( path[0] == '/' || path[0] == '\\' ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_WebHost_WriteTextFile
=============
*/
static qboolean CL_WebHost_WriteTextFile( const char *path, const char *contents ) {
	if ( !CL_WebHost_PathIsSafeRelative( path ) ) {
		return qfalse;
	}

	FS_WriteFile( path, contents ? contents : "", (int)strlen( contents ? contents : "" ) );
	return qtrue;
}

/*
=============
CL_WebHost_BuildFavoriteAddress
=============
*/
static void CL_WebHost_BuildFavoriteAddress( uint32_t ip, uint16_t port, char *buffer, size_t bufferSize ) {
	Com_sprintf(
		buffer,
		bufferSize,
		"%u.%u.%u.%u:%u",
		ip & 0xffu,
		( ip >> 8 ) & 0xffu,
		( ip >> 16 ) & 0xffu,
		( ip >> 24 ) & 0xffu,
		(unsigned int)port
	);
}

/*
=============
CL_WebHost_FindFavoriteServerIndex
=============
*/
static int CL_WebHost_FindFavoriteServerIndex( const netadr_t *address ) {
	int i;

	if ( !address ) {
		return -1;
	}

	for ( i = 0; i < cls.numfavoriteservers; i++ ) {
		if ( NET_CompareAdr( cls.favoriteServers[i].adr, *address ) ) {
			return i;
		}
	}

	return -1;
}

/*
=============
CL_WebHost_MirrorFavoriteServer
=============
*/
static qboolean CL_WebHost_MirrorFavoriteServer( uint32_t ip, uint16_t port, qboolean add ) {
	char addressString[64];
	netadr_t address;
	int index;

	CL_WebHost_BuildFavoriteAddress( ip, port, addressString, sizeof( addressString ) );
	if ( !NET_StringToAdr( addressString, &address ) ) {
		return qfalse;
	}

	index = CL_WebHost_FindFavoriteServerIndex( &address );
	if ( add ) {
		if ( index >= 0 ) {
			return qtrue;
		}
		if ( cls.numfavoriteservers >= MAX_OTHER_SERVERS ) {
			return qfalse;
		}

		index = cls.numfavoriteservers++;
		Com_Memset( &cls.favoriteServers[index], 0, sizeof( cls.favoriteServers[index] ) );
		cls.favoriteServers[index].adr = address;
		cls.favoriteServers[index].visible = qtrue;
		Q_strncpyz( cls.favoriteServers[index].hostName, addressString, sizeof( cls.favoriteServers[index].hostName ) );
		LAN_SaveServersToCache();
		return qtrue;
	}

	if ( index < 0 ) {
		return qfalse;
	}

	for ( ; index < cls.numfavoriteservers - 1; index++ ) {
		Com_Memcpy( &cls.favoriteServers[index], &cls.favoriteServers[index + 1], sizeof( cls.favoriteServers[index] ) );
	}
	cls.numfavoriteservers--;
	LAN_SaveServersToCache();
	return qtrue;
}

/*
=============
CL_WebHost_SetFavoriteServer

Mirrors the retail browser favorite-game owner through Steam matchmaking while
keeping the local favorites cache in sync as an explicit compatibility
fallback when the opted-in Steam provider cannot update favorites.
=============
*/
static qboolean CL_WebHost_SetFavoriteServer( uint32_t ip, uint16_t port, qboolean add ) {
	if ( CL_SteamServicesEnabled() && SteamClient_IsInitialized() &&
		!QL_Steamworks_SetFavoriteServerForApp( ip, port, CL_SteamBrowser_GetDiscoveryAppID(), add ) ) {
		Com_DPrintf(
			"Steam favorite server %s failed for %u:%u; using local favorites cache fallback\n",
			add ? "add" : "remove",
			(unsigned int)ip,
			(unsigned int)port
		);
	}

	return CL_WebHost_MirrorFavoriteServer( ip, port, add );
}

/*
=============
QLWebView_PublishGameKey
=============
*/
static void QLWebView_PublishGameKey( int key ) {
	char payload[128];
	const char *keyName;

	keyName = Key_KeynumToString( key );
	Com_sprintf( payload, sizeof( payload ), "{\"id\":%d,\"key\":\"%s\"}", key, keyName ? keyName : "" );
	CL_WebView_PublishEvent( "game.key", payload );
}

/*
=============
QLJSHandler_CoerceIntegerArgument
=============
*/
static int QLJSHandler_CoerceIntegerArgument( const char *argument ) {
	char *end;
	long value;

	if ( !argument ) {
		return 0;
	}

	value = strtol( argument, &end, 10 );
	if ( end == argument ) {
		return 0;
	}

	while ( *end && isspace( (unsigned char)*end ) ) {
		end++;
	}

	if ( *end ) {
		return 0;
	}

	return (int)value;
}

/*
=============
QLJSHandler_CoerceUnsignedIntegerArgument
=============
*/
static uint32_t QLJSHandler_CoerceUnsignedIntegerArgument( const char *argument ) {
	char *end;
	unsigned long value;

	if ( !argument ) {
		return 0u;
	}

	value = strtoul( argument, &end, 10 );
	if ( end == argument ) {
		return 0u;
	}

	while ( *end && isspace( (unsigned char)*end ) ) {
		end++;
	}

	if ( *end ) {
		return 0u;
	}

	return (uint32_t)value;
}

/*
=============
QLJSHandler_OnMethodCall
=============
*/
static qboolean QLJSHandler_OnMethodCall( const char *methodName, const char **arguments, int argumentCount ) {
	const clWebMethodBinding_t *binding;

	binding = QLJSHandler_LookupMethodBinding( methodName );
	if ( !binding || binding->returnsValue ) {
		return qfalse;
	}

	switch ( binding->methodId ) {
		case CL_WEB_METHOD_SEND_GAME_COMMAND:
			if ( argumentCount > 0 && arguments[0] && arguments[0][0] ) {
				Cbuf_ExecuteText( EXEC_APPEND, va( "%s\n", arguments[0] ) );
				return qtrue;
			}
			return qfalse;

		case CL_WEB_METHOD_WRITE_TEXT_FILE:
			if ( argumentCount < 2 ) {
				return qfalse;
			}
			return CL_WebHost_WriteTextFile( arguments[0], arguments[1] );

		case CL_WEB_METHOD_OPEN_URL:
			if ( argumentCount < 1 || !arguments[0] || !arguments[0][0] ) {
				return qfalse;
			}
			if ( strstr( arguments[0], "://" ) != NULL ) {
				return QLWebHost_OpenURL( arguments[0] );
			}
			return QLWebHost_NavigateOrOpen( arguments[0] );

		case CL_WEB_METHOD_OPEN_STEAM_OVERLAY_URL:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			return CL_Steam_OpenOverlayUrl( arguments[0] );

		case CL_WEB_METHOD_SET_CLIPBOARD_TEXT:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			Sys_SetClipboardData( arguments[0] ? arguments[0] : "" );
			return qtrue;

		case CL_WEB_METHOD_REQUEST_SERVERS:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			return CL_Steam_RequestServers( QLJSHandler_CoerceIntegerArgument( arguments[0] ) );

		case CL_WEB_METHOD_REQUEST_SERVER_DETAILS:
			if ( argumentCount < 2 ) {
				return qfalse;
			}
			return CL_Steam_RequestServerDetails(
				QLJSHandler_CoerceUnsignedIntegerArgument( arguments[0] ),
				(unsigned short)QLJSHandler_CoerceIntegerArgument( arguments[1] )
			);

		case CL_WEB_METHOD_REFRESH_LIST:
			return CL_Steam_RefreshServerList();

		case CL_WEB_METHOD_CREATE_LOBBY:
			return CL_Steam_CreateLobby();

		case CL_WEB_METHOD_LEAVE_LOBBY:
			return CL_Steam_LeaveLobby();

		case CL_WEB_METHOD_JOIN_LOBBY:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			return CL_Steam_JoinLobby( arguments[0] );

		case CL_WEB_METHOD_SET_LOBBY_SERVER:
			if ( argumentCount < 2 ) {
				return qfalse;
			}
			return CL_Steam_SetLobbyServer(
				QLJSHandler_CoerceUnsignedIntegerArgument( arguments[0] ),
				(unsigned short)QLJSHandler_CoerceIntegerArgument( arguments[1] )
			);

		case CL_WEB_METHOD_SHOW_INVITE_OVERLAY:
			return CL_Steam_ShowInviteOverlay();

		case CL_WEB_METHOD_SAY_LOBBY:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			return CL_Steam_SayLobby( arguments[0] ? arguments[0] : "" );

		case CL_WEB_METHOD_REQUEST_USER_STATS:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			return CL_Steam_RequestUserStats( arguments[0] );

		case CL_WEB_METHOD_ACTIVATE_GAME_OVERLAY_TO_USER:
			if ( argumentCount < 2 ) {
				return qfalse;
			}
			return CL_Steam_ActivateOverlayToUser( arguments[0], arguments[1] );

		case CL_WEB_METHOD_INVITE:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			return CL_Steam_Invite( arguments[0] );

		case CL_WEB_METHOD_GET_ALL_UGC:
			if ( argumentCount < 1 ) {
				return qfalse;
			}
			return CL_Steam_RequestAllUGC( QLJSHandler_CoerceIntegerArgument( arguments[0] ) );

		case CL_WEB_METHOD_GET_NEXT_KEY_DOWN:
			if ( argumentCount <= 0 ) {
				cl_webHost.keyCaptureArmed = qtrue;
			} else {
				cl_webHost.keyCaptureArmed = QLJSHandler_CoerceIntegerArgument( arguments[0] ) != 0 ? qtrue : qfalse;
			}
			return qtrue;

		case CL_WEB_METHOD_NO_OP:
			return qtrue;

		case CL_WEB_METHOD_SET_FAVORITE_SERVER:
			if ( argumentCount < 3 ) {
				return qfalse;
			}
			return CL_WebHost_SetFavoriteServer(
				QLJSHandler_CoerceUnsignedIntegerArgument( arguments[0] ),
				(uint16_t)QLJSHandler_CoerceIntegerArgument( arguments[1] ),
				QLJSHandler_CoerceIntegerArgument( arguments[2] ) != 0 ? qtrue : qfalse
			);

		default:
			break;
	}

	return qfalse;
}

/*
=============
QLJSHandler_OnMethodCallWithReturnValue
=============
*/
static qboolean QLJSHandler_OnMethodCallWithReturnValue( const char *methodName, const char **arguments, int argumentCount, char *outValue, size_t outValueSize ) {
	const clWebMethodBinding_t *binding;
	char clipboardBuffer[MAX_STRING_CHARS];

	if ( outValue && outValueSize > 0 ) {
		outValue[0] = '\0';
	}

	binding = QLJSHandler_LookupMethodBinding( methodName );
	if ( !binding || !binding->returnsValue || !outValue || outValueSize == 0 ) {
		return qfalse;
	}

	switch ( binding->methodId ) {
		case CL_WEB_METHOD_IS_PAK_FILE_PRESENT:
		case CL_WEB_METHOD_FILE_EXISTS:
			if ( argumentCount < 1 || !arguments[0] || !arguments[0][0] ) {
				Q_strncpyz( outValue, "0", outValueSize );
				return qtrue;
			}
			Q_strncpyz( outValue, FS_FileExists( arguments[0] ) ? "1" : "0", outValueSize );
			return qtrue;

		case CL_WEB_METHOD_IS_GAME_RUNNING:
			Q_strncpyz( outValue, ( cls.state >= CA_CONNECTED && cls.state < CA_CINEMATIC ) ? "1" : "0", outValueSize );
			return qtrue;

		case CL_WEB_METHOD_GET_CVAR:
			if ( argumentCount < 1 || !arguments[0] || !arguments[0][0] ) {
				return qfalse;
			}
			Cvar_VariableStringBuffer( arguments[0], outValue, (int)outValueSize );
			return qtrue;

		case CL_WEB_METHOD_SET_CVAR:
			if ( argumentCount < 2 || !arguments[0] || !arguments[0][0] ) {
				Q_strncpyz( outValue, "0", outValueSize );
				return qtrue;
			}
			Cvar_Set( arguments[0], arguments[1] ? arguments[1] : "" );
			Q_strncpyz( outValue, "1", outValueSize );
			return qtrue;

		case CL_WEB_METHOD_RESET_CVAR:
			if ( argumentCount < 1 || !arguments[0] || !arguments[0][0] ) {
				Q_strncpyz( outValue, "0", outValueSize );
				return qtrue;
			}
			Cvar_Reset( arguments[0] );
			Q_strncpyz( outValue, "1", outValueSize );
			return qtrue;

		case CL_WEB_METHOD_GET_MAP_LIST:
			CL_WebHost_BuildMapListJson( outValue, outValueSize );
			return qtrue;

		case CL_WEB_METHOD_GET_FACTORY_LIST:
			CL_WebHost_BuildFactoryListJson( outValue, outValueSize );
			return qtrue;

		case CL_WEB_METHOD_GET_DEMO_LIST:
			CL_WebHost_BuildDemoListJson( outValue, outValueSize );
			return qtrue;

		case CL_WEB_METHOD_GET_FRIEND_LIST:
			CL_WebHost_BuildFriendListJson( outValue, outValueSize );
			return qtrue;

		case CL_WEB_METHOD_GET_CONFIG:
			CL_WebHost_BuildConfigJson( outValue, outValueSize );
			return qtrue;

		case CL_WEB_METHOD_GET_CURSOR_POSITION:
			{
				int x;
				int y;

				CL_WebHost_RequestCursorPosition( &x, &y );
				Com_sprintf( outValue, outValueSize, "{\"x\":%d,\"y\":%d}", x, y );
				return qtrue;
			}

		case CL_WEB_METHOD_GET_CLIPBOARD_TEXT:
			clipboardBuffer[0] = '\0';
			{
				char *clipboardData;

				clipboardData = Sys_GetClipboardData();
				if ( clipboardData ) {
					Q_strncpyz( clipboardBuffer, clipboardData, sizeof( clipboardBuffer ) );
					Z_Free( clipboardData );
				}
			}
			Q_strncpyz( outValue, clipboardBuffer, outValueSize );
			return qtrue;

		default:
			break;
	}

	return qfalse;
}

/*
=============
CL_ResetBrowserOverlayState

Clears the browser overlay state when the online service bridge is unavailable.
=============
*/
static void CL_ResetBrowserOverlayState( void ) {
	cl_webBrowserVisible = qfalse;
	cl_webBrowserHash[0] = '\0';
	cl_webHost.browserVisible = qfalse;
	cl_webHost.browserActive = qfalse;
	cl_webHost.focused = qfalse;
	cls.keyCatchers &= ~KEYCATCH_BROWSER;
	CL_WebHost_ClearCursorOverride();
	CL_SetCvarIfChanged( "web_browserActive", "0" );
}

/*
=============
CL_WebHost_MarkBrowserUnavailable

Clears transient browser visibility after a failed live-browser bootstrap while
preserving the loadFailed latch so the UI VM keeps the retail menu root active.
=============
*/
static void CL_WebHost_MarkBrowserUnavailable( void ) {
	CL_ResetBrowserOverlayState();
	CL_RefreshOnlineServicesBridgeState();
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
CL_GetOverlayServiceProviderLabel

Returns the human-readable provider label for the browser overlay seam.
=============
*/
static const char *CL_GetOverlayServiceProviderLabel( void ) {
	const ql_platform_feature_descriptor *overlay = CL_GetOverlayServiceDescriptor();

	if ( !overlay || !overlay->provider ) {
		return "Unavailable";
	}

	return overlay->provider;
}

/*
=============
CL_GetOverlayServicePolicyLabel

Returns the short compatibility policy label for the browser overlay seam.
=============
*/
static const char *CL_GetOverlayServicePolicyLabel( void ) {
	return QL_DescribePlatformFeaturePolicy( CL_GetOverlayServiceDescriptor() );
}

/*
=============
CL_GetAdvertisementBridgeProviderLabel

Returns the human-readable provider label for the advert bridge seam.
=============
*/
static const char *CL_GetAdvertisementBridgeProviderLabel( void ) {
	return CL_GetOverlayServiceProviderLabel();
}

/*
=============
CL_GetAdvertisementBridgePolicyLabel

Returns the short compatibility policy label for the advert bridge seam.
=============
*/
static const char *CL_GetAdvertisementBridgePolicyLabel( void ) {
	return CL_GetOverlayServicePolicyLabel();
}

/*
=============
CL_LogAdvertisementBridgeLifecycle

Publishes provider-aware diagnostics whenever the retained advert bridge syncs
one of its compatibility-only lifecycle transitions.
=============
*/
static void CL_LogAdvertisementBridgeLifecycle( const char *stage, int cellId ) {
	Com_DPrintf( "Advert bridge %s: cell=%d active=%d activated=%d via %s [%s]\n",
		stage ? stage : "sync",
		cellId,
		cl_advertisementBridge.activeAdvertCellId,
		cl_advertisementBridge.activatedAdvertCellId,
		CL_GetAdvertisementBridgeProviderLabel(),
		CL_GetAdvertisementBridgePolicyLabel() );
}

/*
=============
CL_LogOverlayServiceIgnored

Publishes provider-aware diagnostics whenever a browser overlay command is
blocked by the compatibility-only service policy.
=============
*/
static void CL_LogOverlayServiceIgnored( const char *commandName, const char *reason ) {
	Com_DPrintf( "%s ignored: %s (%s [%s])\n",
		commandName ? commandName : "web",
		reason ? reason : "browser overlay provider unavailable",
		CL_GetOverlayServiceProviderLabel(),
		CL_GetOverlayServicePolicyLabel() );
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
CL_WebHost_StringRepresentsTrue

Returns qtrue for environment switch values that opt a retained web host path
in or out.
=============
*/
static qboolean CL_WebHost_StringRepresentsTrue( const char *value ) {
	if ( !value || !value[0] ) {
		return qfalse;
	}

	if ( value[0] == '0' && value[1] == '\0' ) {
		return qfalse;
	}

	if ( !Q_stricmp( value, "false" ) || !Q_stricmp( value, "no" ) || !Q_stricmp( value, "off" ) ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_AwesomiumRuntimeAllowed

Reports whether the explicit Windows Awesomium lane may be attempted.  This is
separate from the platform overlay descriptor because retail QL hosted the web
menu through Awesomium WebCore, not through the Steam overlay.
=============
*/
static qboolean CL_AwesomiumRuntimeAllowed( void ) {
#if QL_PLATFORM_HAS_ONLINE_SERVICES && defined( _WIN32 )
	const char *disabled;

	disabled = getenv( "QL_DISABLE_AWESOMIUM" );
	if ( CL_WebHost_StringRepresentsTrue( disabled ) ) {
		return qfalse;
	}

	disabled = getenv( "QL_DISABLE_EXTERNAL_ECOSYSTEMS" );
	if ( CL_WebHost_StringRepresentsTrue( disabled ) ) {
		return qfalse;
	}

	return qtrue;
#else
	return qfalse;
#endif
}

/*
=============
CL_BrowserRuntimeRequested

Honors explicit launch/profile requests to keep the browser host off while
leaving the online-services build capability intact.
=============
*/
static qboolean CL_BrowserRuntimeRequested( void ) {
	char requested[MAX_CVAR_VALUE_STRING];

	Cvar_VariableStringBuffer( "ui_browserAwesomium", requested, sizeof( requested ) );
	if ( !requested[0] ) {
		return qtrue;
	}

	if ( !Q_stricmp( requested, "0" )
		|| !Q_stricmp( requested, "false" )
		|| !Q_stricmp( requested, "no" )
		|| !Q_stricmp( requested, "off" ) ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_AwesomiumRuntimeActive

Returns whether the live Awesomium lane is both available and requested for
this launch profile.
=============
*/
static qboolean CL_AwesomiumRuntimeActive( void ) {
	return CL_BrowserRuntimeRequested() && CL_AwesomiumRuntimeAllowed();
}

/*
=============
CL_AwesomiumRuntimeRequired

Reports whether this launch profile requires the retail Awesomium menu lane.
This keeps stale offline Debug binaries from silently degrading into main.menu.
=============
*/
static qboolean CL_AwesomiumRuntimeRequired( void ) {
	return Cvar_VariableIntegerValue( "qlr_requireAwesomium" ) != 0;
}

/*
=============
CL_AwesomiumValidateRequiredRuntime

Turns an explicit Awesomium launch into a clear build/runtime policy failure
instead of the disconnected native UI fallback path.
=============
*/
static void CL_AwesomiumValidateRequiredRuntime( void ) {
	if ( !CL_AwesomiumRuntimeRequired() || CL_AwesomiumRuntimeActive() ) {
		return;
	}

	Com_Error( ERR_FATAL,
		"Awesomium launch requested, but this binary cannot start the Awesomium WebUI. "
		"Rebuild with QL_BUILD_ONLINE_SERVICES=1 (default Build or Build Debug Awesomium) "
		"and ensure QL_DISABLE_AWESOMIUM/QL_DISABLE_EXTERNAL_ECOSYSTEMS are not set." );
}

/*
=============
CL_BrowserHostServiceAvailable

Returns qtrue when either the compatibility overlay bridge or the explicit
Awesomium WebCore lane can service browser commands.
=============
*/
static qboolean CL_BrowserHostServiceAvailable( void ) {
	if ( !CL_BrowserRuntimeRequested() ) {
		return qfalse;
	}

	return CL_OverlayServiceAvailable() || CL_AwesomiumRuntimeAllowed();
}

/*
=============
CL_WebHost_AwesomiumPending

Returns qtrue only while a requested live Awesomium browser is waiting for a
drawable overlay surface.
=============
*/
static qboolean CL_WebHost_AwesomiumPending( qboolean awesomiumAllowed ) {
	if ( !awesomiumAllowed || cl_webHost.loadFailed ) {
		return qfalse;
	}

	if ( !cl_webBrowserVisible
		&& !cl_webHost.browserVisible
		&& !cl_webHost.browserActive
		&& !cl_webHost.loadingDocument ) {
		return qfalse;
	}

	return CL_WebHost_SurfaceReadyForOverlay( qtrue ) ? qfalse : qtrue;
}

/*
=============
CL_RefreshOnlineServicesBridgeState

Synchronises client-visible browser and advert bridge state with the platform-service table.
=============
*/
void CL_RefreshOnlineServicesBridgeState( void ) {
	const char *overlayProvider = CL_GetOverlayServiceProviderLabel();
	const char *overlayPolicy = CL_GetOverlayServicePolicyLabel();
	const char *advertProvider = CL_GetAdvertisementBridgeProviderLabel();
	const char *advertPolicy = CL_GetAdvertisementBridgePolicyLabel();
	const char *parityScope = QL_GetOnlineServicesParityScopeLabel();
	const char *parityReason = QL_GetOnlineServicesParityReasonLabel();
	qboolean browserRequested = CL_BrowserRuntimeRequested();
	qboolean awesomiumAllowed = CL_AwesomiumRuntimeActive();

#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	cl_advertisementBridge.overlayCompiled = qfalse;
	cl_advertisementBridge.overlayAvailable = qfalse;
	cl_advertisementBridge.viewWidth = 0;
	cl_advertisementBridge.viewHeight = 0;
	cl_previousBrowserAvailable = qfalse;
	CL_SetCvarIfChanged( "ui_browserAwesomium", "0" );
	CL_SetCvarIfChanged( "ui_browserAwesomiumPending", "0" );
	CL_SetCvarIfChanged( "ui_browserAwesomiumProvider", overlayProvider );
	CL_SetCvarIfChanged( "ui_browserAwesomiumPolicy", overlayPolicy );
	CL_SetCvarIfChanged( "ui_browserAwesomiumParityScope", parityScope );
	CL_SetCvarIfChanged( "ui_browserAwesomiumParityReason", parityReason );
	CL_SetCvarIfChanged( "ui_advertisementBridgeProvider", advertProvider );
	CL_SetCvarIfChanged( "ui_advertisementBridgePolicy", advertPolicy );
	CL_SetCvarIfChanged( "ui_advertisementBridgeParityScope", parityScope );
	CL_SetCvarIfChanged( "ui_advertisementBridgeParityReason", parityReason );
	CL_WebHost_ResetRuntime( qtrue );
	CL_ResetBrowserOverlayState();
#else
	const ql_platform_feature_descriptor *overlay = CL_GetOverlayServiceDescriptor();
	qboolean overlayAvailable = browserRequested && CL_OverlayServiceAvailable();
	qboolean browserAvailable = overlayAvailable || awesomiumAllowed;
	qboolean awesomiumPending = CL_WebHost_AwesomiumPending( awesomiumAllowed );

	cl_advertisementBridge.overlayCompiled = ( overlay && overlay->compiled );
	cl_advertisementBridge.overlayAvailable = overlayAvailable;
	cl_advertisementBridge.viewWidth = cls.glconfig.vidWidth;
	cl_advertisementBridge.viewHeight = cls.glconfig.vidHeight;

	CL_SetCvarIfChanged( "ui_browserAwesomium", browserAvailable ? "1" : "0" );
	CL_SetCvarIfChanged( "ui_browserAwesomiumPending", awesomiumPending ? "1" : "0" );
	CL_SetCvarIfChanged( "ui_browserAwesomiumProvider", awesomiumAllowed ? "Awesomium WebCore" : overlayProvider );
	CL_SetCvarIfChanged( "ui_browserAwesomiumPolicy", awesomiumAllowed ? "runtime-opt-in" : overlayPolicy );
	CL_SetCvarIfChanged( "ui_browserAwesomiumParityScope", parityScope );
	CL_SetCvarIfChanged( "ui_browserAwesomiumParityReason", parityReason );
	CL_SetCvarIfChanged( "ui_advertisementBridgeProvider", advertProvider );
	CL_SetCvarIfChanged( "ui_advertisementBridgePolicy", advertPolicy );
	CL_SetCvarIfChanged( "ui_advertisementBridgeParityScope", parityScope );
	CL_SetCvarIfChanged( "ui_advertisementBridgeParityReason", parityReason );
	if ( browserAvailable != cl_previousBrowserAvailable ) {
		cl_previousBrowserAvailable = browserAvailable;
		if ( cls.keyCatchers & KEYCATCH_UI ) {
			Cbuf_ExecuteText( EXEC_APPEND, "ui_load\n" );
		}
	}
	if ( !browserAvailable ) {
		CL_WebHost_ResetRuntime( qtrue );
		CL_ResetBrowserOverlayState();
	}
#endif
}

/*
=============
CL_AdvertisementBridge_ClearDelay

Mirrors retail sub_4F2310 by clearing the local advert delay deadline.
=============
*/
void CL_AdvertisementBridge_ClearDelay( void ) {
	cl_advertisementBridge.delayDeadline = 0;
}

/*
=============
CL_AdvertisementBridge_IsDelayElapsed

Mirrors retail sub_4F22E0: the advert delay gate is open when no deadline is
armed, or once the current host time has passed the stored deadline.
=============
*/
qboolean CL_AdvertisementBridge_IsDelayElapsed( void ) {
	if ( cl_advertisementBridge.delayDeadline == 0 ) {
		return qtrue;
	}

	return cls.realtime > cl_advertisementBridge.delayDeadline ? qtrue : qfalse;
}

/*
=============
CL_AdvertisementBridge_InitUI

Mirrors the retail UI advertisement-bridge init hook.
=============
*/
void CL_AdvertisementBridge_InitUI( void ) {
	cl_webBridge.vtbl->initUI( &cl_webBridge );
}

/*
=============
CL_AdvertisementBridge_ActivateAdvert

Mirrors the retail UI-side advert activation bridge path.
=============
*/
void CL_AdvertisementBridge_ActivateAdvert( int cellId ) {
	cl_webBridge.vtbl->activateAdvert( &cl_webBridge, cellId );
}

/*
=============
CL_AdvertisementBridge_SetActiveAdvert

Mirrors the retail cgame-side active advert selection/reset helper.
=============
*/
void CL_AdvertisementBridge_SetActiveAdvert( int cellId ) {
	cl_webBridge.vtbl->setActiveAdvert( &cl_webBridge, cellId );
}

/*
=============
CL_AdvertisementBridge_ClearLabel

Clears one advert-debug label buffer while preserving the size contract the
renderer-side bridge callbacks expect.
=============
*/
static void CL_AdvertisementBridge_ClearLabel( char *buffer, int bufferSize ) {
	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	buffer[0] = '\0';
}

/*
=============
QLWebBridge_SetActiveAdvert

Slot +0x08 in the retail data_12d2670 bridge: cgame active advert selection.
=============
*/
static int QLWebBridge_SetActiveAdvert( ql_web_bridge_t *bridge, int cellId ) {
	clAdvertisementBridgeState_t *advertisement;

	if ( !bridge || !bridge->advertisement ) {
		return -1;
	}

	advertisement = bridge->advertisement;
	advertisement->activeAdvertCellId = cellId;
	if ( cellId == 0 ) {
		advertisement->activatedAdvertCellId = 0;
	}

	CL_RefreshOnlineServicesBridgeState();
	CL_LogAdvertisementBridgeLifecycle( "set-active", cellId );
	return cellId;
}

/*
=============
QLWebBridge_SetAppActivation

Slot +0x0c in the retail data_12d2670 bridge: Win32 app activation mirror.
=============
*/
static void QLWebBridge_SetAppActivation( ql_web_bridge_t *bridge, int active ) {
	if ( !bridge ) {
		return;
	}

	CL_WebHost_NotifyAppActivation( active ? qtrue : qfalse );
}

/*
=============
QLWebBridge_SetFrameTime

Slot +0x10 in the retail data_12d2670 bridge: advert frame-time update.
=============
*/
static int QLWebBridge_SetFrameTime( ql_web_bridge_t *bridge, int frameTime ) {
	if ( !bridge || !bridge->advertisement || !bridge->advertisement->initialised ) {
		return -1;
	}

	bridge->advertisement->frameTime = frameTime;
	CL_RefreshOnlineServicesBridgeState();
	return frameTime;
}

/*
=============
QLWebBridge_UpdateViewParameters

Slot +0x14 in the retail data_12d2670 bridge: renderer view/projection sync.
=============
*/
static int QLWebBridge_UpdateViewParameters( ql_web_bridge_t *bridge, int x, int y, int width, int height, float fovX, float fovY, float zFar, int time, int flags ) {
	(void)x;
	(void)y;
	(void)fovX;
	(void)fovY;
	(void)zFar;

	if ( !bridge || !bridge->advertisement ) {
		return -1;
	}

	if ( width > 0 ) {
		bridge->advertisement->viewWidth = width;
	}
	if ( height > 0 ) {
		bridge->advertisement->viewHeight = height;
	}
	if ( time > 0 ) {
		bridge->advertisement->frameTime = time;
	}
	bridge->clientStateFlags = flags;

	CL_RefreshOnlineServicesBridgeState();
	return 0;
}

/*
=============
QLWebBridge_SetVisibilityTraceCallback

Slot +0x18 in the retail data_12d2670 bridge: advert visibility trace hook.
=============
*/
static void QLWebBridge_SetVisibilityTraceCallback( ql_web_bridge_t *bridge, void *callback ) {
	if ( !bridge ) {
		return;
	}

	bridge->visibilityTraceCallback = callback;
}

/*
=============
QLWebBridge_Reserved1FC0

Slot +0x1c in the retail data_12d2670 bridge; behavior is still opaque.
=============
*/
static int QLWebBridge_Reserved1FC0( ql_web_bridge_t *bridge, int value ) {
	(void)bridge;
	return value;
}

/*
=============
QLWebBridge_SetMapPath

Slot +0x20 in the retail data_12d2670 bridge: cgame map BSP path setter.
=============
*/
static int QLWebBridge_SetMapPath( ql_web_bridge_t *bridge, const char *mapPath ) {
	if ( !bridge ) {
		return -1;
	}

	Q_strncpyz( bridge->mapPath, mapPath ? mapPath : "", sizeof( bridge->mapPath ) );
	CL_RefreshOnlineServicesBridgeState();
	return 0;
}

/*
=============
QLWebBridge_InitCGame

Slot +0x24 in the retail data_12d2670 bridge: native cgame advert init.
=============
*/
static int QLWebBridge_InitCGame( ql_web_bridge_t *bridge ) {
	if ( !bridge || !bridge->advertisement ) {
		return -1;
	}

	bridge->advertisement->initialised = qtrue;
	bridge->advertisement->frameTime = 0;
	bridge->advertisement->activeAdvertCellId = 0;
	bridge->advertisement->delayDeadline = 0;
	CL_RefreshOnlineServicesBridgeState();
	return 0;
}

/*
=============
QLWebBridge_ShutdownCGame

Slot +0x28 in the retail data_12d2670 bridge: native cgame advert shutdown.
=============
*/
static int QLWebBridge_ShutdownCGame( ql_web_bridge_t *bridge ) {
	if ( !bridge || !bridge->advertisement ) {
		return -1;
	}

	bridge->advertisement->initialised = qfalse;
	bridge->advertisement->frameTime = 0;
	bridge->advertisement->activeAdvertCellId = 0;
	bridge->advertisement->activatedAdvertCellId = 0;
	bridge->advertisement->delayDeadline = 0;
	CL_RefreshOnlineServicesBridgeState();
	CL_LogAdvertisementBridgeLifecycle( "shutdown-cgame", 0 );
	return 0;
}

/*
=============
QLWebBridge_SetClientStateFlags

Slot +0x2c in the retail data_12d2670 bridge: per-frame client flag sync.
=============
*/
static int QLWebBridge_SetClientStateFlags( ql_web_bridge_t *bridge, int flags ) {
	if ( !bridge ) {
		return flags;
	}

	bridge->clientStateFlags = flags;
	return flags;
}

/*
=============
QLWebBridge_GetCellDisplayState

Slot +0x38 in the retail data_12d2670 bridge: advert debug cell palette.
=============
*/
static int QLWebBridge_GetCellDisplayState( ql_web_bridge_t *bridge, int cellId ) {
	const clAdvertisementBridgeState_t *advertisement;

	if ( !bridge || !bridge->advertisement || cellId <= 0 ) {
		return 0;
	}

	advertisement = bridge->advertisement;
	if ( cellId == advertisement->activatedAdvertCellId ) {
		return 2;
	}

	if ( cellId == advertisement->activeAdvertCellId ) {
		return 1;
	}

	return 0;
}

/*
=============
QLWebBridge_GetCellLabel

Slot +0x3c in the retail data_12d2670 bridge: advert debug cell label.
=============
*/
static int QLWebBridge_GetCellLabel( ql_web_bridge_t *bridge, int cellId, char *buffer, int bufferSize ) {
	const clAdvertisementBridgeState_t *advertisement;

	CL_AdvertisementBridge_ClearLabel( buffer, bufferSize );
	if ( !bridge || !bridge->advertisement || !buffer || bufferSize <= 0 || cellId <= 0 ) {
		return -1;
	}

	advertisement = bridge->advertisement;
	if ( cellId == advertisement->activatedAdvertCellId ) {
		Com_sprintf( buffer, bufferSize, "cell %d activated", cellId );
		return 0;
	}

	if ( cellId == advertisement->activeAdvertCellId ) {
		Com_sprintf( buffer, bufferSize, "cell %d active", cellId );
		return 0;
	}

	Com_sprintf( buffer, bufferSize, "cell %d available", cellId );
	return 0;
}

/*
=============
QLWebBridge_Reserved21C0

Slot +0x40 in the retail data_12d2670 bridge; behavior is still opaque.
=============
*/
static void QLWebBridge_Reserved21C0( ql_web_bridge_t *bridge ) {
	(void)bridge;
}

/*
=============
QLWebBridge_InitUI

Slot +0x44 in the retail data_12d2670 bridge: UI advert bridge init.
=============
*/
static void QLWebBridge_InitUI( ql_web_bridge_t *bridge ) {
	(void)bridge;
	CL_RefreshOnlineServicesBridgeState();
	CL_LogAdvertisementBridgeLifecycle( "init-ui", 0 );
}

/*
=============
QLWebBridge_GetLabelList2Count

Slot +0x48 in the retail data_12d2670 bridge: second debug label count.
=============
*/
static int QLWebBridge_GetLabelList2Count( ql_web_bridge_t *bridge ) {
	(void)bridge;
	return CL_ADVERTISEMENT_DEBUG_LABEL_COUNT;
}

/*
=============
QLWebBridge_GetLabelList1Count

Slot +0x4c in the retail data_12d2670 bridge: first debug label count.
=============
*/
static int QLWebBridge_GetLabelList1Count( ql_web_bridge_t *bridge ) {
	(void)bridge;
	return CL_ADVERTISEMENT_DEBUG_LABEL_COUNT;
}

/*
=============
QLWebBridge_RegisterDefaultAdvertCellShader

Shared fallback for the four shader-supplying bridge slots.
=============
*/
static qhandle_t QLWebBridge_RegisterDefaultAdvertCellShader( const char *defaultContent ) {
	if ( !defaultContent || !defaultContent[0] ) {
		return 0;
	}

	return CL_Steam_RegisterShader( defaultContent );
}

/*
=============
QLWebBridge_SetupAdvertCellShader

Slot +0x50 in the retail data_12d2670 bridge: cgame advert shader setup.
=============
*/
static qhandle_t QLWebBridge_SetupAdvertCellShader( ql_web_bridge_t *bridge, const char *defaultContent, const void *rect, int cellId ) {
	(void)bridge;
	(void)rect;
	(void)cellId;
	return QLWebBridge_RegisterDefaultAdvertCellShader( defaultContent );
}

/*
=============
QLWebBridge_SetupUIAdvertCellShader

Slot +0x54 in the retail data_12d2670 bridge: UI advert shader setup.
=============
*/
static qhandle_t QLWebBridge_SetupUIAdvertCellShader( ql_web_bridge_t *bridge, const char *defaultContent, const void *rect, int cellId ) {
	(void)bridge;
	(void)rect;
	(void)cellId;
	return QLWebBridge_RegisterDefaultAdvertCellShader( defaultContent );
}

/*
=============
QLWebBridge_RefreshAdvertCellShader

Slot +0x58 in the retail data_12d2670 bridge: cgame advert shader refresh.
=============
*/
static qhandle_t QLWebBridge_RefreshAdvertCellShader( ql_web_bridge_t *bridge, const char *defaultContent, const void *rect, int cellId ) {
	(void)bridge;
	(void)rect;
	(void)cellId;
	return QLWebBridge_RegisterDefaultAdvertCellShader( defaultContent );
}

/*
=============
QLWebBridge_RefreshUIAdvertCellShader

Slot +0x5c in the retail data_12d2670 bridge: UI advert shader refresh.
=============
*/
static qhandle_t QLWebBridge_RefreshUIAdvertCellShader( ql_web_bridge_t *bridge, const char *defaultContent, const void *rect, int cellId ) {
	(void)bridge;
	(void)rect;
	(void)cellId;
	return QLWebBridge_RegisterDefaultAdvertCellShader( defaultContent );
}

/*
=============
QLWebBridge_GetLabelList2Entry

Slot +0x60 in the retail data_12d2670 bridge: second debug label text.
=============
*/
static int QLWebBridge_GetLabelList2Entry( ql_web_bridge_t *bridge, int index, char *buffer, int bufferSize ) {
	const clAdvertisementBridgeState_t *advertisement;

	CL_AdvertisementBridge_ClearLabel( buffer, bufferSize );
	if ( !bridge || !bridge->advertisement || !buffer || bufferSize <= 0 ) {
		return -1;
	}

	advertisement = bridge->advertisement;
	switch ( index ) {
		case 0:
			Com_sprintf( buffer, bufferSize, "state: %s frame=%d view=%dx%d",
				advertisement->initialised ? "active" : "idle",
				advertisement->frameTime,
				advertisement->viewWidth,
				advertisement->viewHeight );
			return 0;

		case 1:
			Com_sprintf( buffer, bufferSize, "active=%d activated=%d",
				advertisement->activeAdvertCellId,
				advertisement->activatedAdvertCellId );
			return 0;
	}

	return -1;
}

/*
=============
QLWebBridge_GetLabelList1Entry

Slot +0x64 in the retail data_12d2670 bridge: first debug label text.
=============
*/
static int QLWebBridge_GetLabelList1Entry( ql_web_bridge_t *bridge, int index, char *buffer, int bufferSize ) {
	const clAdvertisementBridgeState_t *advertisement;
	const clWebHostState_t *webHost;

	CL_AdvertisementBridge_ClearLabel( buffer, bufferSize );
	if ( !bridge || !bridge->advertisement || !bridge->webHost || !buffer || bufferSize <= 0 ) {
		return -1;
	}

	advertisement = bridge->advertisement;
	webHost = bridge->webHost;
	switch ( index ) {
		case 0:
			Com_sprintf( buffer, bufferSize, "bridge: %s [%s]",
				CL_GetAdvertisementBridgeProviderLabel(),
				CL_GetAdvertisementBridgePolicyLabel() );
			return 0;

		case 1:
			Com_sprintf( buffer, bufferSize, "overlay: compiled=%d available=%d browser=%d",
				advertisement->overlayCompiled ? 1 : 0,
				advertisement->overlayAvailable ? 1 : 0,
				webHost->browserActive ? 1 : 0 );
			return 0;
	}

	return -1;
}

/*
=============
QLWebBridge_ActivateAdvert

Slot +0x68 in the retail data_12d2670 bridge: UI-side advert activation.
=============
*/
static void QLWebBridge_ActivateAdvert( ql_web_bridge_t *bridge, int cellId ) {
	if ( !bridge || !bridge->advertisement ) {
		return;
	}

	bridge->advertisement->activatedAdvertCellId = cellId;
	CL_RefreshOnlineServicesBridgeState();
	CL_LogAdvertisementBridgeLifecycle( "activate", cellId );
}

/*
=============
CL_AdvertisementBridge_GetCellDisplayState

Reconstructs the retained advert-debug palette split from the active and
activated cell ids mirrored through the client bridge.
=============
*/
int CL_AdvertisementBridge_GetCellDisplayState( int cellId ) {
	return cl_webBridge.vtbl->getCellDisplayState( &cl_webBridge, cellId );
}

/*
=============
CL_AdvertisementBridge_GetCellLabel

Formats one retained advert-debug cell label for the renderer overlay.
=============
*/
void CL_AdvertisementBridge_GetCellLabel( int cellId, char *buffer, int bufferSize ) {
	(void)cl_webBridge.vtbl->getCellLabel( &cl_webBridge, cellId, buffer, bufferSize );
}

/*
=============
CL_AdvertisementBridge_GetLabelList1Count

Publishes the retained advert-debug summary count for the first label list.
=============
*/
int CL_AdvertisementBridge_GetLabelList1Count( void ) {
	return cl_webBridge.vtbl->getLabelList1Count( &cl_webBridge );
}

/*
=============
CL_AdvertisementBridge_GetLabelList1Entry

Publishes provider and overlay-availability diagnostics for the first
renderer-side advert-debug summary list.
=============
*/
void CL_AdvertisementBridge_GetLabelList1Entry( int index, char *buffer, int bufferSize ) {
	(void)cl_webBridge.vtbl->getLabelList1Entry( &cl_webBridge, index, buffer, bufferSize );
}

/*
=============
CL_AdvertisementBridge_GetLabelList2Count

Publishes the retained advert-debug summary count for the second label list.
=============
*/
int CL_AdvertisementBridge_GetLabelList2Count( void ) {
	return cl_webBridge.vtbl->getLabelList2Count( &cl_webBridge );
}

/*
=============
CL_AdvertisementBridge_GetLabelList2Entry

Publishes frame, view, and active-cell diagnostics for the second renderer-side
advert-debug summary list.
=============
*/
void CL_AdvertisementBridge_GetLabelList2Entry( int index, char *buffer, int bufferSize ) {
	(void)cl_webBridge.vtbl->getLabelList2Entry( &cl_webBridge, index, buffer, bufferSize );
}

/*
=============
CL_AdvertisementBridge_SetupUIAdvertCellShader

Routes UI advert-cell setup through the recovered bridge slot +0x54.
=============
*/
qhandle_t CL_AdvertisementBridge_SetupUIAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {
	return cl_webBridge.vtbl->setupUIAdvertCellShader( &cl_webBridge, defaultContent, rect, cellId );
}

/*
=============
CL_AdvertisementBridge_RefreshUIAdvertCellShader

Routes UI advert-cell refresh through the recovered bridge slot +0x5c.
=============
*/
qhandle_t CL_AdvertisementBridge_RefreshUIAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {
	return cl_webBridge.vtbl->refreshUIAdvertCellShader( &cl_webBridge, defaultContent, rect, cellId );
}

/*
=============
CL_AdvertisementBridge_SetupAdvertCellShader

Routes cgame advert-cell setup through the recovered bridge slot +0x50.
=============
*/
qhandle_t CL_AdvertisementBridge_SetupAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {
	return cl_webBridge.vtbl->setupAdvertCellShader( &cl_webBridge, defaultContent, rect, cellId );
}

/*
=============
CL_AdvertisementBridge_RefreshAdvertCellShader

Routes cgame advert-cell refresh through the recovered bridge slot +0x58.
=============
*/
qhandle_t CL_AdvertisementBridge_RefreshAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {
	return cl_webBridge.vtbl->refreshAdvertCellShader( &cl_webBridge, defaultContent, rect, cellId );
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
	if ( UI_GameCommand() ) {
		return;
	}
	CL_LogOverlayServiceIgnored( "web_showBrowser", "online services disabled by build settings" );
	return;
#else
	CL_RefreshOnlineServicesBridgeState();
	if ( !CL_BrowserHostServiceAvailable() ) {
		CL_ResetBrowserOverlayState();
		if ( UI_GameCommand() ) {
			return;
		}
		CL_LogOverlayServiceIgnored( "web_showBrowser", "browser overlay provider unavailable" );
		return;
	}

	cl_webBrowserVisible = qtrue;
	if ( Cmd_Argc() > 1 ) {
		const char *hash = Cmd_ArgsFrom( 1 );
		CL_WebHost_NormalizeHash( hash, cl_webBrowserHash, sizeof( cl_webBrowserHash ) );
	} else {
		cl_webBrowserHash[0] = '\0';
	}
	qboolean browserOpened = QLWebHost_NavigateOrOpen( cl_webBrowserHash );
	if ( !browserOpened ) {
		CL_WebHost_MarkBrowserUnavailable();
	}
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
	CL_LogOverlayServiceIgnored( "web_changeHash", "online services disabled by build settings" );
	return;
#else
	CL_RefreshOnlineServicesBridgeState();
	if ( !CL_BrowserHostServiceAvailable() ) {
		CL_LogOverlayServiceIgnored( "web_changeHash", "browser overlay provider unavailable" );
		return;
	}

	const char *hash = ( Cmd_Argc() > 1 ) ? Cmd_ArgsFrom( 1 ) : "";
	CL_WebHost_NormalizeHash( hash, cl_webBrowserHash, sizeof( cl_webBrowserHash ) );
	cl_webBrowserVisible = qtrue;
	qboolean hashOpened = QLWebHost_NavigateOrOpen( cl_webBrowserHash );
	if ( !hashOpened ) {
		CL_WebHost_MarkBrowserUnavailable();
	}
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
	CL_LogOverlayServiceIgnored( "web_browserActive", "online services disabled by build settings" );
	return;
#else
	CL_RefreshOnlineServicesBridgeState();
	if ( !CL_BrowserHostServiceAvailable() ) {
		CL_LogOverlayServiceIgnored( "web_browserActive", "browser overlay provider unavailable" );
		return;
	}

	qboolean active = ( Cmd_Argc() > 1 && atoi( Cmd_Argv( 1 ) ) != 0 );

	cl_webBrowserVisible = active;
	if ( active ) {
		if ( !QLWebHost_NavigateOrOpen( cl_webBrowserHash ) ) {
			CL_WebHost_MarkBrowserUnavailable();
			return;
		}
	} else {
		QLWebHost_HideBrowser();
	}
	CL_WebHost_UpdateOverlayOwnership();
	Com_DPrintf( "web_browserActive %s\n", Cvar_VariableIntegerValue( "web_browserActive" ) ? "1" : "0" );
#endif
}

/*
=============
CL_Web_HideBrowser_f

Hides the browser overlay and clears the active cvar latch.
=============
*/
void CL_Web_HideBrowser_f( void ) {
	QLWebHost_HideBrowser();
}

/*
=============
CL_Web_ClearSessionState

Clears the retained URI cache layer that stands in for the retail browser
session cache.
=============
*/
static void CL_Web_ClearSessionState( void ) {
#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		CL_Awesomium_ClearCache();
	}
#endif
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
	CL_WebView_PublishGameError( message );
}

/*
=============
CL_Web_ClearCache_f

Keeps the retail browser cache-clear command wired into the retained session-cache seam.
=============
*/
void CL_Web_ClearCache_f( void ) {
	if ( !cl_webHost.sessionInitialised ) {
		return;
	}

	CL_Web_ClearSessionState();
}

/*
=============
CL_Web_Reload_f

Keeps the retail browser reload command wired into the host/browser seam.
=============
*/
void CL_Web_Reload_f( void ) {
	if ( !cl_webHost.viewInitialised ) {
		return;
	}

	CL_Web_ClearSessionState();
	QLWebHost_ReloadView( qtrue );
}

/*
=============
QLWebHost_RegisterCommands

Restores the retail browser-host command-registration helper used by CL_Init.
=============
*/
void QLWebHost_RegisterCommands( void ) {
	Cmd_AddCommand ("localservers", CL_LocalServers_f );
	Cmd_AddCommand ("globalservers", CL_GlobalServers_f );
	Cmd_AddCommand ("web_showBrowser", CL_Web_ShowBrowser_f );
	Cmd_AddCommand ("web_changeHash", CL_Web_ChangeHash_f );
	Cmd_AddCommand ("web_hideBrowser", CL_Web_HideBrowser_f );
	Cmd_AddCommand ("web_showError", CL_Web_ShowError_f );
	Cmd_AddCommand ("web_clearCache", CL_Web_ClearCache_f );
	Cmd_AddCommand ("web_reload", CL_Web_Reload_f );
	Cmd_AddCommand ("web_stopRefresh", CL_Web_StopRefresh_f );
	cl_webZoom = Cvar_Get ("web_zoom", "100", CVAR_ARCHIVE );
	cl_webConsole = Cvar_Get ("web_console", "0", CVAR_ARCHIVE );
	cl_webBrowserActive = Cvar_Get ("web_browserActive", "0", CVAR_ROM );
	cl_webHost.zoomPercent = CL_WebZoomIntegerValue();
	cl_webHost.cvarMappingCount = QLWebHost_CountRecoveredWebCvarMappings();
	Cvar_Set( "ui_browserAwesomiumPending", CL_WebHost_AwesomiumPending( CL_AwesomiumRuntimeActive() ) ? "1" : "0" );
}

/*
=============
CL_Web_StopRefresh_f

Handles Awesomium refresh-stop requests when an overlay provider is active.
=============
*/
void CL_Web_StopRefresh_f( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	CL_LogOverlayServiceIgnored( "web_stopRefresh", "online services disabled by build settings" );
	return;
#else
	CL_RefreshOnlineServicesBridgeState();
	if ( !CL_BrowserHostServiceAvailable() ) {
		CL_LogOverlayServiceIgnored( "web_stopRefresh", "browser overlay provider unavailable" );
		return;
	}

#if defined( _WIN32 ) && QL_PLATFORM_HAS_ONLINE_SERVICES
	if ( cl_webHost.liveAwesomium ) {
		cl_webHost.refreshStopped = qfalse;
		cl_webHost.surfaceDirty = qtrue;
		Com_DPrintf( "web_stopRefresh ignored for live Awesomium WebCore\n" );
		return;
	}
#endif

	cl_webHost.refreshStopped = qtrue;
	cl_webHost.surfaceDirty = qtrue;
	Com_DPrintf( "web_stopRefresh\n" );
#endif
}

/*
=============
CL_WebHost_Init

Initialises the retained browser-host shim from the client owner state.
=============
*/
void CL_WebHost_Init( void ) {
	cl_webBrowserVisible = qfalse;
	cl_webBrowserHash[0] = '\0';
	CL_WebHost_ResetRuntime( qtrue );
	CL_RefreshOnlineServicesBridgeState();
}

/*
=============
CL_WebHost_Shutdown

Releases the retained browser-host shim and clears the client-visible state.
=============
*/
void CL_WebHost_Shutdown( void ) {
	QLWebHost_HideBrowser();
	CL_Web_ClearSessionState();
	CL_WebHost_ResetRuntime( qtrue );
	CL_ResetBrowserOverlayState();
}

/*
=============
CL_WebHost_ShouldBootstrapMenu

Allows the retained Awesomium menu host to auto-start only while the client is
in a menu-side state. Match startup tears the menu host down before loading
game VMs, and this guard keeps it from immediately bootstrapping again.
=============
*/
static qboolean CL_WebHost_ShouldBootstrapMenu( void ) {
	return cls.state == CA_DISCONNECTED || cls.state == CA_CINEMATIC;
}

/*
=============
CL_WebHost_BootstrapAwesomiumMenu

Starts the opt-in Awesomium WebCore menu once the renderer has dimensions,
before the startup command buffer can request screenshots or browser commands.
=============
*/
void CL_WebHost_BootstrapAwesomiumMenu( void ) {
	CL_AwesomiumValidateRequiredRuntime();

#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	return;
#else
	qboolean awesomiumAllowed;

	CL_RefreshOnlineServicesBridgeState();
	awesomiumAllowed = CL_AwesomiumRuntimeActive();
	if ( !awesomiumAllowed
		|| !CL_WebHost_ShouldBootstrapMenu()
		|| cl_webHost.loadFailed
		|| cls.glconfig.vidWidth <= 0
		|| cls.glconfig.vidHeight <= 0 ) {
		return;
	}

	if ( cl_webHost.liveAwesomium ) {
		return;
	}

	if ( cl_webHost.coreInitialised || cl_webHost.viewInitialised ) {
		CL_WebHost_ResetRuntime( qfalse );
	}

	cl_webBrowserVisible = qtrue;
	cl_webBrowserHash[0] = '\0';
	if ( !QLWebHost_OpenURL( CL_WEB_DEFAULT_URL ) ) {
		CL_WebHost_MarkBrowserUnavailable();
	}
#endif
}

/*
=============
CL_WebHost_Frame

Pumps the retained browser-host shim so the overlay-facing state stays in sync.
=============
*/
void CL_WebHost_Frame( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	CL_WebHost_ResetRuntime( qtrue );
	return;
#else
	CL_RefreshOnlineServicesBridgeState();
	if ( !CL_BrowserHostServiceAvailable() ) {
		CL_WebHost_ResetRuntime( qtrue );
		return;
	}

	CL_WebHost_BootstrapAwesomiumMenu();

	if ( cl_webBrowserVisible ) {
		char expectedUrl[MAX_STRING_CHARS];

		CL_WebHost_BuildCurrentURL( cl_webBrowserHash, expectedUrl, sizeof( expectedUrl ) );
		if ( !cl_webHost.viewInitialised ) {
			if ( cl_webBrowserHash[0] ) {
				if ( !QLWebHost_OpenRelativeURL( cl_webBrowserHash ) ) {
					CL_WebHost_MarkBrowserUnavailable();
					return;
				}
			} else {
				QLWebHost_OpenURL( CL_WEB_DEFAULT_URL );
				if ( !cl_webHost.browserActive ) {
					CL_WebHost_MarkBrowserUnavailable();
					return;
				}
			}
		} else if ( Q_stricmp( cl_webHost.currentUrl, expectedUrl ) ) {
			if ( !QLWebHost_NavigateOrOpen( cl_webBrowserHash ) ) {
				CL_WebHost_MarkBrowserUnavailable();
				return;
			}
		} else {
			cl_webHost.browserVisible = qtrue;
			cl_webHost.browserActive = qtrue;
			cl_webHost.focused = qtrue;
		}

	} else if ( cl_webHost.browserVisible || cl_webHost.browserActive ) {
		QLWebHost_HideBrowser();
		CL_SetCvarIfChanged( "web_browserActive", "0" );
	}

	QLWebCore_Update();
	QLWebHost_PumpFrame();
	CL_WebHost_CheckLiveAwesomiumSurfaceFailure();
	CL_WebHost_UpdateOverlayOwnership();
#endif
}

/*
=============
CL_WebHost_DrawBrowserSurface

Draws the live browser texture over the current client/UI frame while the
Awesomium host owns the browser keycatcher.
=============
*/
void CL_WebHost_DrawBrowserSurface( void ) {
	float s1;
	float t1;
	int contentWidth;
	int contentHeight;

	if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {
		return;
	}

	if ( !cl_webHost.surfaceShader ) {
		return;
	}
	if ( !CL_WebHost_SurfaceReadyForOverlay( qtrue ) ) {
		return;
	}

	if ( cl_webHost.surfaceWidth <= 0 || cl_webHost.surfaceHeight <= 0 ) {
		return;
	}

	contentWidth = cl_webHost.surfaceContentWidth > 0 ? cl_webHost.surfaceContentWidth : cl_webHost.viewWidth;
	contentHeight = cl_webHost.surfaceContentHeight > 0 ? cl_webHost.surfaceContentHeight : cl_webHost.viewHeight;
	s1 = contentWidth > 0 ? (float)contentWidth / (float)cl_webHost.surfaceWidth : 1.0f;
	t1 = contentHeight > 0 ? (float)contentHeight / (float)cl_webHost.surfaceHeight : 1.0f;
	if ( s1 <= 0.0f || s1 > 1.0f ) {
		s1 = 1.0f;
	}
	if ( t1 <= 0.0f || t1 > 1.0f ) {
		t1 = 1.0f;
	}

	re.SetColor( NULL );
	re.DrawStretchPic( 0, 0, cls.glconfig.vidWidth, cls.glconfig.vidHeight, 0, 0, s1, t1, cl_webHost.surfaceShader );
	re.SetColor( NULL );
	cl_webHost.surfacePresented = qtrue;
}

/*
=============
CL_WebHost_HasLiveView

Reports whether the retained browser host owns an active view surface.
=============
*/
qboolean CL_WebHost_HasLiveView( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	return qfalse;
#else
	if ( !CL_BrowserHostServiceAvailable() ) {
		return qfalse;
	}

	return cl_webHost.viewInitialised && cl_webHost.bootstrapReady;
#endif
}

/*
=============
CL_WebHost_HasBoundWindowObject

Reports whether the retained browser host published the qz window object.
=============
*/
qboolean CL_WebHost_HasBoundWindowObject( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	return qfalse;
#else
	if ( !CL_BrowserHostServiceAvailable() ) {
		return qfalse;
	}

	return cl_webHost.windowObjectBound;
#endif
}

/*
=============
CL_WebHost_HasDrawableSurface

Reports whether the browser host currently owns a visible texture that can
stand in for a fullscreen UI frame.
=============
*/
qboolean CL_WebHost_HasDrawableSurface( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	return qfalse;
#else
	if ( !CL_BrowserHostServiceAvailable() ) {
		return qfalse;
	}

	return CL_WebHost_SurfaceReadyForOverlay( qtrue );
#endif
}

/*
=============
CL_WebHost_GetCursorHandle

Returns the active Win32 browser cursor override when the retained host owns one.
=============
*/
void *CL_WebHost_GetCursorHandle( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES || !defined( _WIN32 )
	return NULL;
#else
	if ( !CL_BrowserHostServiceAvailable() ) {
		return NULL;
	}

	if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {
		return NULL;
	}

	if ( !cl_webHost.cursorOverrideActive || !cl_webHost.activeCursorHandle ) {
		return NULL;
	}

	return cl_webHost.activeCursorHandle;
#endif
}

/*
=============
CL_WebHost_NotifyAppActivation

Mirrors retail Win32 app-activation changes into the retained browser host.
=============
*/
void CL_WebHost_NotifyAppActivation( qboolean active ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	(void)active;
	return;
#else
	if ( !CL_BrowserHostServiceAvailable() ) {
		return;
	}

	if ( !active ) {
		cl_webHost.focused = qfalse;
		return;
	}

	QLWebView_InjectActivationKeyboardEvent();
#endif
}

/*
=============
CL_WebView_OnMouseMove

Records browser-directed mouse motion for the retained host-text/browser seam.
=============
*/
void CL_WebView_OnMouseMove( int x, int y ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	(void)x;
	(void)y;
	return;
#else
	if ( !CL_BrowserHostServiceAvailable() ) {
		return;
	}

	QLWebView_InjectMouseMove( x, y );
#endif
}

/*
=============
CL_WebView_OnMouseButtonEvent

Records browser-directed mouse button activity for the retained host-text/browser seam.
=============
*/
void CL_WebView_OnMouseButtonEvent( int key, qboolean down ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	(void)key;
	(void)down;
	return;
#else
	if ( !CL_BrowserHostServiceAvailable() ) {
		return;
	}

	if ( down ) {
		QLWebView_InjectMouseDown( key );
	} else {
		QLWebView_InjectMouseUp( key );
	}
#endif
}

/*
=============
CL_WebView_OnMouseWheelEvent

Records browser-directed mouse wheel activity for the retained host-text/browser seam.
=============
*/
void CL_WebView_OnMouseWheelEvent( int direction ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	(void)direction;
	return;
#else
	if ( !CL_BrowserHostServiceAvailable() ) {
		return;
	}

	QLWebView_InjectMouseWheel( direction );
#endif
}

/*
=============
CL_WebView_OnKeyEvent

Records browser-directed key activity for the retained host-text/browser seam.
=============
*/
void CL_WebView_OnKeyEvent( int key, qboolean down ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	(void)key;
	(void)down;
	return;
#else
	if ( !CL_BrowserHostServiceAvailable() ) {
		return;
	}

	QLWebView_InjectKeyboardEvent( key, down );
#endif
}

/*
====================
CL_AdvertisementBridge_InitCGame

Bridges the retail cgame advert lifecycle into the host when available.
====================
*/
static void CL_AdvertisementBridge_InitCGame( void ) {
	(void)cl_webBridge.vtbl->initCGame( &cl_webBridge );
}

/*
====================
CL_AdvertisementBridge_ShutdownCGame

Tears down the retail cgame advert lifecycle bridge when a host exists.
====================
*/
static void CL_AdvertisementBridge_ShutdownCGame( void ) {
	(void)cl_webBridge.vtbl->shutdownCGame( &cl_webBridge );
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

	(void)cl_webBridge.vtbl->updateViewParameters(
		&cl_webBridge,
		0,
		0,
		cls.glconfig.vidWidth,
		cls.glconfig.vidHeight,
		0.0f,
		0.0f,
		0.0f,
		cl_advertisementBridge.frameTime,
		cl_webBridge.clientStateFlags );
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
	(void)cl_webBridge.vtbl->setFrameTime( &cl_webBridge, frameTime );
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

typedef struct {
	char					renderer_string[MAX_STRING_CHARS];
	char					vendor_string[MAX_STRING_CHARS];
	char					version_string[MAX_STRING_CHARS];
	char					extensions_string[BIG_INFO_STRING];

	int						maxTextureSize;
	int						maxActiveTextures;

	int						colorBits, depthBits, stencilBits;

	glDriverType_t			driverType;
	glHardwareType_t		hardwareType;

	qboolean				deviceSupportsGamma;
	textureCompression_t	textureCompression;
	qboolean				textureEnvAddAvailable;
	qboolean				multitextureAvailable;

	int						vidWidth, vidHeight;
	float					windowAspect;

	int						displayFrequency;

	qboolean				isFullscreen;
	qboolean				stereoEnabled;
} qlRetailGlconfig_t;

typedef char qlRetailGlconfigSizeCheck[( sizeof( qlRetailGlconfig_t ) == 0x2c44 ) ? 1 : -1 ];

/*
====================
CL_GetRetailGlconfig

Retail Quake Live stores GL_ARB_multitexture availability before vidWidth and
does not expose the engine-local smpActive tail slot retained by the shared
GPL-era renderer struct.
====================
*/
void CL_GetRetailGlconfig( void *glconfig ) {
	qlRetailGlconfig_t retailConfig;

	if ( !glconfig ) {
		return;
	}

	Com_Memset( &retailConfig, 0, sizeof( retailConfig ) );
	Q_strncpyz( retailConfig.renderer_string, cls.glconfig.renderer_string, sizeof( retailConfig.renderer_string ) );
	Q_strncpyz( retailConfig.vendor_string, cls.glconfig.vendor_string, sizeof( retailConfig.vendor_string ) );
	Q_strncpyz( retailConfig.version_string, cls.glconfig.version_string, sizeof( retailConfig.version_string ) );
	Q_strncpyz( retailConfig.extensions_string, cls.glconfig.extensions_string, sizeof( retailConfig.extensions_string ) );
	retailConfig.maxTextureSize = cls.glconfig.maxTextureSize;
	retailConfig.maxActiveTextures = cls.glconfig.maxActiveTextures;
	retailConfig.colorBits = cls.glconfig.colorBits;
	retailConfig.depthBits = cls.glconfig.depthBits;
	retailConfig.stencilBits = cls.glconfig.stencilBits;
	retailConfig.driverType = cls.glconfig.driverType;
	retailConfig.hardwareType = cls.glconfig.hardwareType;
	retailConfig.deviceSupportsGamma = cls.glconfig.deviceSupportsGamma;
	retailConfig.textureCompression = cls.glconfig.textureCompression;
	retailConfig.textureEnvAddAvailable = cls.glconfig.textureEnvAddAvailable;
	retailConfig.multitextureAvailable = cls.glconfig.multitextureAvailable;
	retailConfig.vidWidth = cls.glconfig.vidWidth;
	retailConfig.vidHeight = cls.glconfig.vidHeight;
	retailConfig.windowAspect = cls.glconfig.windowAspect;
	retailConfig.displayFrequency = cls.glconfig.displayFrequency;
	retailConfig.isFullscreen = cls.glconfig.isFullscreen;
	retailConfig.stereoEnabled = cls.glconfig.stereoEnabled;

	Com_Memcpy( glconfig, &retailConfig, sizeof( retailConfig ) );
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
void CL_SetUserCmdValue( int userCmdValue, int userCmdPrimary, float sensitivityScale, int userCmdFov ) {
	cl.cgameUserCmdValue = userCmdValue;
	cl.cgameUserCmdPrimary = userCmdPrimary;
	cl.cgameUserCmdFov = userCmdFov;
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
		CL_SetUserCmdValue( args[1], args[2], VMF(3), args[4] );
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

	if ( arg == CG_GETGLCONFIG ) {
		void *glconfig;

		va_start(ap, arg);
		glconfig = va_arg(ap, void *);
		va_end(ap);

		CL_GetRetailGlconfig( glconfig );
		return 0;
	}

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
CL_IsSteamIdentityMuted
==============
*/
qboolean CL_IsSteamIdentityMuted( unsigned int identityLow, unsigned int identityHigh ) {
	uint64_t identity;

	identity = QL_CG_CombineIdentityWords( identityLow, identityHigh );
	if ( !identity ) {
		return qfalse;
	}

	return QL_CG_FindMutedIdentityIndex( identity ) >= 0 ? qtrue : qfalse;
}

/*
==============
QL_CG_trap_Cvar_RegisterRange
==============
*/
static void QDECL QL_CG_trap_Cvar_RegisterRange( vmCvar_t *vmCvar, const char *varName, const char *defaultValue, const char *minimumValue, const char *maximumValue, int flags ) {
	Cvar_RegisterBounded( vmCvar, varName, defaultValue, minimumValue, maximumValue, flags );
}

/*
==============
QL_CG_trap_Cvar_SetValue
==============
*/
static void QDECL QL_CG_trap_Cvar_SetValue( const char *varName, float value ) {
	Cvar_SetValue( varName, value );
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
	S_StartSoundVolume( origin, entityNum, entchannel, sfx, volume );
}

/*
==============
QL_CG_trap_S_StartLocalSoundVolume
==============
*/
static void QDECL QL_CG_trap_S_StartLocalSoundVolume( sfxHandle_t sfx, int channelNum, float volume ) {
	S_StartLocalSoundVolume( sfx, channelNum, volume );
}

/*
==============
QL_CG_trap_S_ClearLoopingSoundsFrame
==============
*/
static void QDECL QL_CG_trap_S_ClearLoopingSoundsFrame( void ) {
	S_ClearLoopingSoundsFrame();
}

/*
==============
QL_CG_trap_S_ClearLoopingSoundsKillAll
==============
*/
static void QDECL QL_CG_trap_S_ClearLoopingSoundsKillAll( void ) {
	S_ClearSoundBuffer();
}

/*
==============
QL_CG_trap_SetupAdvertCellShader
==============
*/
static qhandle_t QDECL QL_CG_trap_SetupAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {
	return CL_AdvertisementBridge_SetupAdvertCellShader( defaultContent, rect, cellId );
}

/*
==============
QL_CG_trap_RefreshAdvertCellShader
==============
*/
static qhandle_t QDECL QL_CG_trap_RefreshAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {
	return CL_AdvertisementBridge_RefreshAdvertCellShader( defaultContent, rect, cellId );
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
QL_CG_trap_AdvertisementBridge_Reserved21C0
==============
*/
static void QDECL QL_CG_trap_AdvertisementBridge_Reserved21C0( void ) {
	// cgamex86.dll HLIL: CG_LoadHudMenu calls import[54], retail sub_4AFF10 -> bridge slot +0x40.
	cl_webBridge.vtbl->reserved21C0( &cl_webBridge );
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
QL_CG_trap_RetailReservedImport
==============
*/
static int QDECL QL_CG_trap_RetailReservedImport( void ) {
	// Address-backed retail import rows whose exact signatures remain unresolved fail closed.
	return 0;
}

/*
==============
QL_CG_trap_AdvertisementBridge_SetMapPath
==============
*/
static void QDECL QL_CG_trap_AdvertisementBridge_SetMapPath( const char *mapPath ) {
	(void)cl_webBridge.vtbl->setMapPath( &cl_webBridge, mapPath );
}

/*
==============
QL_CG_trap_AdvertisementBridge_UpdateViewParameters
==============
*/
static void QDECL QL_CG_trap_AdvertisementBridge_UpdateViewParameters( void ) {
	(void)cl_webBridge.vtbl->updateViewParameters(
		&cl_webBridge,
		0,
		0,
		cls.glconfig.vidWidth,
		cls.glconfig.vidHeight,
		0.0f,
		0.0f,
		0.0f,
		cl_advertisementBridge.frameTime,
		cl_webBridge.clientStateFlags );
}

/*
==============
QL_CG_trap_AdvertisementBridge_ClearDelay
==============
*/
static void QDECL QL_CG_trap_AdvertisementBridge_ClearDelay( void ) {
	CL_AdvertisementBridge_ClearDelay();
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
QL_CG_trap_PublishTaggedInfoString
==============
*/
static void QDECL QL_CG_trap_PublishTaggedInfoString( const char *messageType, const char *infoString ) {
	CL_WebView_PublishTaggedInfoString( messageType, infoString );
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
	RE_DrawScaledText( x, y, text, fontHandle, scale, maxX, outMaxX, forceColor != qfalse ? qtrue : qfalse, ql_cgame_currentColor );
}

/*
==============
QL_CG_trap_MeasureText
==============
*/
static unsigned long long QDECL QL_CG_trap_MeasureText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outLeft ) {
	float width;
	float height;

	RE_MeasureScaledText( text, end, fontHandle, scale, maxX, &width, &height, outLeft );

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
QL_CG_trap_IsSubscribedApp
==============
*/
static int QDECL QL_CG_trap_IsSubscribedApp( int appId ) {
	// quakelive_steam.exe HLIL: cgame import[122] is the shared SteamApps subscription wrapper.
	if ( !CL_SteamServicesEnabled() ) {
		Com_DPrintf( "CGame subscription bridge ignored for app %d: subscription bridge provider unavailable\n", appId );
		return 0;
	}

	return SteamApps_BIsSubscribedApp( (uint32_t)appId ) ? 1 : 0;
}

/*
==============
QL_CG_trap_GetAvatarImageHandle
==============
*/
static qhandle_t QDECL QL_CG_trap_GetAvatarImageHandle( unsigned int identityLow, unsigned int identityHigh ) {
	return SteamClient_GetAvatarImageHandle( identityLow, identityHigh );
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
	ql_cgame_imports[CG_QL_IMPORT_CVAR_SET_VALUE] = (ql_import_f)QL_CG_trap_Cvar_SetValue;
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
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_21C0] = (ql_import_f)QL_CG_trap_AdvertisementBridge_Reserved21C0;
	ql_cgame_imports[CG_QL_IMPORT_SETUP_ADVERT_CELL_SHADER] = (ql_import_f)QL_CG_trap_SetupAdvertCellShader;
	ql_cgame_imports[CG_QL_IMPORT_REFRESH_ADVERT_CELL_SHADER] = (ql_import_f)QL_CG_trap_RefreshAdvertCellShader;
	ql_cgame_imports[CG_QL_IMPORT_SET_ACTIVE_ADVERT] = (ql_import_f)QL_CG_trap_SetActiveAdvert;
	ql_cgame_imports[CG_QL_IMPORT_UPDATE_ADVERT] = (ql_import_f)QL_CG_trap_UpdateAdvert;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_59] = (ql_import_f)QL_CG_trap_RetailReservedImport;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_SET_MAP_PATH] = (ql_import_f)QL_CG_trap_AdvertisementBridge_SetMapPath;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_INITCGAME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_InitCGame;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_ShutdownCGame;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_63] = (ql_import_f)QL_CG_trap_RetailReservedImport;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_UPDATE_VIEW_PARAMETERS] = (ql_import_f)QL_CG_trap_AdvertisementBridge_UpdateViewParameters;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_SETFRAMETIME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_SetFrameTime;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_65] = (ql_import_f)QL_CG_trap_RetailReservedImport;
	ql_cgame_imports[CG_QL_IMPORT_RETAIL_RESERVED_66] = (ql_import_f)QL_CG_trap_RetailReservedImport;
	ql_cgame_imports[CG_QL_IMPORT_RETAIL_RESERVED_67] = (ql_import_f)QL_CG_trap_RetailReservedImport;
	ql_cgame_imports[CG_QL_IMPORT_RETAIL_RESERVED_68] = (ql_import_f)QL_CG_trap_RetailReservedImport;
	ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_69] = (ql_import_f)QL_CG_trap_RetailReservedImport;
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
	ql_cgame_imports[CG_QL_IMPORT_RETAIL_RESERVED_80] = (ql_import_f)QL_CG_trap_RetailReservedImport;
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
	ql_cgame_imports[CG_QL_IMPORT_PC_ADD_GLOBAL_DEFINE] = (ql_import_f)QL_CG_trap_PC_AddGlobalDefine;
	ql_cgame_imports[CG_QL_IMPORT_PC_LOAD_SOURCE] = (ql_import_f)QL_CG_trap_PC_LoadSource;
	ql_cgame_imports[CG_QL_IMPORT_PC_FREE_SOURCE] = (ql_import_f)QL_CG_trap_PC_FreeSource;
	ql_cgame_imports[CG_QL_IMPORT_PC_READ_TOKEN] = (ql_import_f)QL_CG_trap_PC_ReadToken;
	ql_cgame_imports[CG_QL_IMPORT_PC_SOURCE_FILE_AND_LINE] = (ql_import_f)QL_CG_trap_PC_SourceFileAndLine;
	ql_cgame_imports[CG_QL_IMPORT_RETAIL_RESERVED_112] = (ql_import_f)QL_CG_trap_RetailReservedImport;
	ql_cgame_imports[CG_QL_IMPORT_RETAIL_RESERVED_113] = (ql_import_f)QL_CG_trap_RetailReservedImport;
	ql_cgame_imports[CG_QL_IMPORT_PUBLISH_TAGGED_INFO_STRING] = (ql_import_f)QL_CG_trap_PublishTaggedInfoString;
	ql_cgame_imports[CG_QL_IMPORT_RETAIL_RESERVED_117] = (ql_import_f)QL_CG_trap_RetailReservedImport;
	ql_cgame_imports[CG_QL_IMPORT_R_MIRROR_POINT] = (ql_import_f)QL_CG_trap_R_MirrorPoint;
	ql_cgame_imports[CG_QL_IMPORT_R_MIRROR_VECTOR] = (ql_import_f)QL_CG_trap_R_MirrorVector;
	ql_cgame_imports[CG_QL_IMPORT_IS_SUBSCRIBED_APP] = (ql_import_f)QL_CG_trap_IsSubscribedApp;
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
CL_CheckCGameNativeImportIntegrity

Checks the native cgame import slots guarded by retail before cgame frame work.
====================
*/
void CL_CheckCGameNativeImportIntegrity( void ) {
	if ( ql_cgame_imports[CG_QL_IMPORT_R_ADDREFENTITYTOSCENE] != (ql_import_f)QL_CG_trap_R_AddRefEntityToScene ||
		ql_cgame_imports[CG_QL_IMPORT_R_RENDERSCENE] != (ql_import_f)QL_CG_trap_R_RenderScene ) {
		CL_SetRetailClientMessageCGameImportGuardFlag();
	}
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
		vm = VM_Create( "cgame", CL_CgameSystemCalls, VMI_NATIVE, ql_cgame_imports, CGAME_NATIVE_API_VERSION );
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
CL_LoadCGameForCvarRegistration

Retail startup-only owner for loading cgame before the register-cvars export call.
====================
*/
static vm_t *CL_LoadCGameForCvarRegistration( vmInterpret_t interpret ) {
	return CL_LoadCGameVM( interpret );
}

/*
====================
CL_RegisterCGameCvars

Loads cgame for the retail startup cvar pass and invokes its native register-cvars export.
====================
*/
void CL_RegisterCGameCvars( void ) {
	vmInterpret_t	interpret;

	interpret = Cvar_VariableValue( "vm_cgame" );
	cgvm = CL_LoadCGameForCvarRegistration( interpret );
	if ( !cgvm ) {
		Com_Error( ERR_FATAL, "Couldn't load cgame VM during cvar registration.\n" );
	}

	VM_CallCGameRegisterCvars( cgvm );
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

static int cl_autoTimeNudgePrevious;

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
CL_ClampTimeNudge
==================
*/
static int CL_ClampTimeNudge( int tn ) {
	if ( tn < -20 ) {
		return -20;
	} else if ( tn > 0 ) {
		return 0;
	}

	return tn;
}

/*
==================
CL_SelectClientTimeNudge
==================
*/
static int CL_SelectClientTimeNudge( void ) {
	int tn;

	if ( Cvar_VariableIntegerValue( "cg_spectating" ) ) {
		tn = 0;
	} else if ( Sys_IsLANAddress( clc.serverAddress ) ) {
		tn = 0;
	} else if ( !cl_autoTimeNudge->integer ) {
		tn = cl_timeNudge->integer;
	} else {
		tn = (int)( (float)cl.snap.ping * -0.5f );
		if ( cl_autoTimeNudgePrevious != 0 && cl_autoTimeNudgePrevious != tn ) {
			tn = cl_autoTimeNudgePrevious;
		}
	}

	tn = CL_ClampTimeNudge( tn );
	cl_autoTimeNudgePrevious = tn;

	return tn;
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
	CL_WebView_PublishGameStart();

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

		tn = CL_SelectClientTimeNudge();

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


