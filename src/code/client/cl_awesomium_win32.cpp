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
// cl_awesomium_win32.cpp -- runtime Awesomium host adapter

#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef QL_BUILD_ONLINE_SERVICES
#define QL_BUILD_ONLINE_SERVICES 0
#endif

typedef int qboolean;
typedef unsigned char byte;

#ifndef qfalse
#define qfalse 0
#endif

#ifndef qtrue
#define qtrue 1
#endif

#if QL_BUILD_ONLINE_SERVICES

#define CL_AWE_STARTUP_SCRIPT_RETRY_FRAMES 240
#define CL_AWE_STARTUP_SCRIPT_RETRY_INTERVAL 10

typedef void *(__stdcall *awe_new_void_fn)( void );
typedef void (__stdcall *awe_delete_object_fn)( void *object );
typedef void *(__stdcall *awe_webcore_initialize_fn)( void *config );
typedef void (__stdcall *awe_webcore_shutdown_fn)( void );
typedef void (__stdcall *awe_webcore_update_fn)( void *core );
typedef void *(__stdcall *awe_webcore_create_session_fn)( void *core, const unsigned short *dataPath, void *preferences );
typedef void *(__stdcall *awe_webcore_create_view_fn)( void *core, int width, int height, void *session, int type );
typedef void (__stdcall *awe_webcore_set_string_fn)( void *object, const unsigned short *value );
typedef void (__stdcall *awe_webprefs_set_bool_fn)( void *preferences, bool value );
typedef void *(__stdcall *awe_new_datapak_source_fn)( const unsigned short *pakPath );
typedef void (__stdcall *awe_websession_void_fn)( void *session );
typedef void (__stdcall *awe_websession_add_source_fn)( void *session, const unsigned short *sourceName, void *dataSource );
typedef void *(__stdcall *awe_new_weburl_fn)( const unsigned short *url );
typedef void (__stdcall *awe_webview_destroy_fn)( void *view );
typedef void (__stdcall *awe_webview_load_url_fn)( void *view, void *url );
typedef void (__stdcall *awe_webview_resize_fn)( void *view, int width, int height );
typedef void (__stdcall *awe_webview_focus_fn)( void *view );
typedef void (__stdcall *awe_webview_unfocus_fn)( void *view );
typedef void (__stdcall *awe_webview_resume_rendering_fn)( void *view );
typedef void (__stdcall *awe_webview_pause_rendering_fn)( void *view );
typedef void (__stdcall *awe_webview_reload_fn)( void *view, bool ignoreCache );
typedef void (__stdcall *awe_webview_stop_fn)( void *view );
typedef void (__stdcall *awe_webview_execute_javascript_fn)( void *view, const unsigned short *script, const unsigned short *frame );
typedef void *(__stdcall *awe_webview_execute_javascript_with_result_fn)( void *view, const unsigned short *script, const unsigned short *frame );
typedef void (__stdcall *awe_webview_set_transparent_fn)( void *view, bool transparent );
typedef void (__stdcall *awe_webview_set_zoom_fn)( void *view, int zoomPercent );
typedef void (__stdcall *awe_webview_mouse_move_fn)( void *view, int x, int y );
typedef void (__stdcall *awe_webview_mouse_button_fn)( void *view, int button );
typedef void (__stdcall *awe_webview_mouse_wheel_fn)( void *view, int x, int y );
typedef void *(__stdcall *awe_new_keyboard_event_fn)( unsigned int eventType, unsigned int virtualKeyCode, long nativeKeyCode );
typedef void (__stdcall *awe_webview_keyboard_event_fn)( void *view, void *event );
typedef void *(__stdcall *awe_webview_surface_fn)( void *view );
typedef bool (__stdcall *awe_webview_query_bool_fn)( void *view );
typedef int (__stdcall *awe_webview_query_int_fn)( void *view );
typedef void (__stdcall *awe_bitmap_copy_to_fn)( void *surface, byte *destination, int rowSpan, int depth, bool convertToRGBA, bool flipY );
typedef int (__stdcall *awe_bitmap_dimension_fn)( void *surface );
typedef const byte *(__stdcall *awe_bitmap_buffer_fn)( void *surface );
typedef bool (__stdcall *awe_bitmap_bool_fn)( void *surface );
typedef void (__stdcall *awe_bitmap_set_bool_fn)( void *surface, bool value );
typedef int (__stdcall *awe_jsvalue_to_integer_fn)( void *value );

typedef struct {
	void	*webConfig;
	void	*webPreferences;
	void	*webCore;
	void	*webSession;
	void	*webView;
	void	*dataPakSource;
	HMODULE	module;
	int		bootstrapMappingCount;
	qboolean importsResolved;
	qboolean started;
	qboolean urlLoaded;
	int		startupScriptInjectionFrames;
	char	startupScript[196608];
	char	startupRetryScript[256];
	char	lastError[256];
} clAwesomiumState_t;

typedef struct {
	awe_new_void_fn					newWebConfig;
	awe_delete_object_fn			deleteWebConfig;
	awe_new_void_fn					newWebPreferences;
	awe_delete_object_fn			deleteWebPreferences;
	awe_webcore_initialize_fn		webCoreInitialize;
	awe_webcore_shutdown_fn			webCoreShutdown;
	awe_webcore_update_fn			webCoreUpdate;
	awe_webcore_create_session_fn	webCoreCreateWebSession;
	awe_webcore_create_view_fn		webCoreCreateWebView;
	awe_webcore_set_string_fn		webConfigAssetProtocolSet;
	awe_webcore_set_string_fn		webConfigChildProcessPathSet;
	awe_webcore_set_string_fn		webConfigLogPathSet;
	awe_webcore_set_string_fn		webConfigPackagePathSet;
	awe_webcore_set_string_fn		webConfigUserAgentSet;
	awe_webcore_set_string_fn		webConfigUserScriptSet;
	awe_webprefs_set_bool_fn			webPrefsEnablePluginsSet;
	awe_webprefs_set_bool_fn			webPrefsEnableWebSecuritySet;
	awe_new_datapak_source_fn		newDataPakSource;
	awe_delete_object_fn			deleteDataPakSource;
	awe_new_weburl_fn				newWebURL;
	awe_delete_object_fn			deleteWebURL;
	awe_websession_void_fn			webSessionInitialize;
	awe_websession_void_fn			webSessionClearCache;
	awe_websession_add_source_fn		webSessionAddDataSource;
	awe_webview_destroy_fn			webViewDestroy;
	awe_webview_load_url_fn			webViewLoadURL;
	awe_webview_execute_javascript_fn	webViewExecuteJavascript;
	awe_webview_execute_javascript_with_result_fn	webViewExecuteJavascriptWithResult;
	awe_webview_set_transparent_fn	webViewSetTransparent;
	awe_webview_set_zoom_fn			webViewSetZoom;
	awe_webview_resize_fn			webViewResize;
	awe_webview_focus_fn				webViewFocus;
	awe_webview_unfocus_fn			webViewUnfocus;
	awe_webview_resume_rendering_fn	webViewResumeRendering;
	awe_webview_pause_rendering_fn	webViewPauseRendering;
	awe_webview_reload_fn			webViewReload;
	awe_webview_stop_fn				webViewStop;
	awe_webview_mouse_move_fn		webViewInjectMouseMove;
	awe_webview_mouse_button_fn		webViewInjectMouseDown;
	awe_webview_mouse_button_fn		webViewInjectMouseUp;
	awe_webview_mouse_wheel_fn		webViewInjectMouseWheel;
	awe_new_keyboard_event_fn		newWebKeyboardEvent;
	awe_delete_object_fn			deleteWebKeyboardEvent;
	awe_webview_keyboard_event_fn	webViewInjectKeyboardEvent;
	awe_webview_surface_fn			webViewSurface;
	awe_webview_query_bool_fn		webViewIsLoading;
	awe_webview_query_bool_fn		webViewIsCrashed;
	awe_webview_query_int_fn			webViewLastError;
	awe_websession_void_fn			webSessionRelease;
	awe_bitmap_copy_to_fn			bitmapCopyTo;
	awe_bitmap_dimension_fn			bitmapWidth;
	awe_bitmap_dimension_fn			bitmapHeight;
	awe_bitmap_dimension_fn			bitmapRowSpan;
	awe_bitmap_buffer_fn			bitmapBuffer;
	awe_bitmap_bool_fn				bitmapIsDirty;
	awe_bitmap_set_bool_fn			bitmapSetIsDirty;
	awe_jsvalue_to_integer_fn		jsValueToInteger;
	awe_delete_object_fn			deleteJSValue;
} clAwesomiumImports_t;

#define CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT "external SDK C API dependency"
#define CL_AWE_RETAIL_ABI_SCOPE_SOURCE_KEYBOARD "source-owned keyboard event path"
#define CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT "external SDK C API dependency"
#define CL_AWE_RETAIL_BOOTSTRAP_SCOPE_OBJECT_LIFETIME "SDK-owned object lifetime"
#define CL_AWE_RETAIL_BOOTSTRAP_SCOPE_SOURCE_LITERAL "retail literal retained in source adapter"

typedef struct {
	unsigned int	retailAddress;
	unsigned int	retailVtableSlot;
	const char		*retailMethod;
	const char		*adapterOwner;
	const char		*adapterBinding;
	const char		*substitutionKind;
} clAwesomiumRetailAbiEquivalence_t;

typedef struct {
	unsigned int	retailOwnerAddress;
	unsigned int	retailAnchor;
	const char		*retailMember;
	const char		*adapterOwner;
	const char		*adapterBinding;
	const char		*substitutionKind;
} clAwesomiumBootstrapRetailMapping_t;

/*
=============
Awesomium retail ABI equivalence table

Retail `quakelive_steam.exe` calls Awesomium through retained C++ object
pointers and vtable slots. This backend records those retail anchors as
evidence, but runtime calls are restricted to the external Awesomium SDK C API
exports resolved from `awesomium.dll`.
=============
*/
static const clAwesomiumRetailAbiEquivalence_t cl_aweRetailAbiEquivalence[] = {
	{ 0x004F2590u, 0x18u, "WebCore::Update", "CL_Awesomium_Update", "_Awe_WebCore_Update@4", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F25C0u, 0x9cu, "WebView::Resize", "CL_Awesomium_Resize", "_Awe_WebView_Resize@12", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F2750u, 0xd0u, "WebView::InjectMouseMove", "CL_Awesomium_InjectMouseMove", "_Awe_WebView_InjectMouseMove@12", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F27C0u, 0xd4u, "WebView::InjectMouseDown", "CL_Awesomium_InjectMouseDown", "_Awe_WebView_InjectMouseDown@8", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F2820u, 0xd8u, "WebView::InjectMouseUp", "CL_Awesomium_InjectMouseUp", "_Awe_WebView_InjectMouseUp@8", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F2870u, 0xdcu, "WebView::InjectMouseWheel", "CL_Awesomium_InjectMouseWheel", "_Awe_WebView_InjectMouseWheel@12", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F28A0u, 0xe0u, "WebView::InjectKeyboardEvent", "CL_Awesomium_InjectKeyboardEvent", "_Awe_new_WebKeyboardEvent_1@12 + _Awe_WebView_InjectKeyboardEvent@8", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
};

/*
=============
Awesomium retail bootstrap mapping table

Retail `QLWebHost_OpenURL` constructs the Awesomium core, session, data-source,
view, URL, focus, and shutdown chain directly through C++ constructors and
vtable slots. This backend keeps those seams source-visible while routing them
through the external SDK C API dependency.
=============
*/
static const clAwesomiumBootstrapRetailMapping_t cl_aweBootstrapRetailMappings[] = {
	{ 0x004F2D30u, 0x0052C6A4u, "WebConfig::WebConfig", "CL_Awesomium_PrepareConfig", "_Awe_new_WebConfig@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x0052C6A0u, "WebCore::Initialize", "CL_Awesomium_Startup", "_Awe_WebCore_Initialize@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x0052C698u, "WebPreferences::WebPreferences", "CL_Awesomium_PreparePreferences", "_Awe_new_WebPreferences@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000002u, "WebPreferences::enable_plugins byte", "CL_Awesomium_PreparePreferences", "_Awe_WebPreferences_enable_plugins_set@8", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000008u, "WebPreferences::enable_web_security byte", "CL_Awesomium_PreparePreferences", "_Awe_WebPreferences_enable_web_security_set@8", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000000u, "WebCore::CreateWebSession slot 0x00", "CL_Awesomium_CreateSession", "_Awe_WebCore_CreateWebSession@12", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000018u, "WebSession bootstrap slot 0x18", "CL_Awesomium_CreateSession", "_Awe_WebSession_Initialize@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2A10u, 0x0000001Cu, "WebSession::ClearCache slot 0x1C", "CL_Awesomium_ClearCache", "_Awe_WebSession_ClearCache@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x0052C694u, "DataPakSource::DataPakSource", "CL_Awesomium_CreateSession", "_Awe_new_DataPakSource@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00548068u, "QL data-source name", "CL_Awesomium_CreateSession", "\"QL\"", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_SOURCE_LITERAL },
	{ 0x004F2D30u, 0x00548070u, "DataPakSource::vftable", "CL_Awesomium_CreateSession", "Awesomium built-in DataPakSource", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_OBJECT_LIFETIME },
	{ 0x004F2D30u, 0x00000010u, "WebSession::AddDataSource slot 0x10", "CL_Awesomium_CreateSession", "_Awe_WebSession_AddDataSource@12", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000004u, "WebCore::CreateWebView slot 0x04", "CL_Awesomium_Startup", "_Awe_WebCore_CreateWebView_0@20", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x000000A0u, "WebView::SetTransparent slot 0xA0", "CL_Awesomium_Startup", "_Awe_WebView_SetTransparent@8", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000064u, "WebView::LoadURL slot 0x64", "CL_Awesomium_OpenURL", "_Awe_WebView_LoadURL@8", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F24D0u, 0x000000A8u, "WebView::PauseRendering slot 0xA8", "CL_Awesomium_PauseRendering", "_Awe_WebView_PauseRendering@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x000000ACu, "WebView::ResumeRendering slot 0xAC", "CL_Awesomium_OpenURL", "_Awe_WebView_ResumeRendering@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x000000B0u, "WebView::Focus slot 0xB0", "CL_Awesomium_OpenURL", "_Awe_WebView_Focus@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F24D0u, 0x000000B4u, "WebView::Unfocus slot 0xB4", "CL_Awesomium_Unfocus", "_Awe_WebView_Unfocus@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x000000C4u, "WebView::SetZoom slot 0xC4", "CL_Awesomium_SetZoom", "_Awe_WebView_SetZoom@8", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000124u, "WebView::ExecuteJavascript slot 0x124", "CL_Awesomium_ExecuteJavascript", "_Awe_WebView_ExecuteJavascript@12", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x0000012Cu, "WebView::set_js_method_handler slot 0x12C", "CL_Awesomium_BuildStartupScript", "qz_instance startup bridge", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_SOURCE_LITERAL },
	{ 0x004F2D30u, 0x00000084u, "WebView::surface slot 0x84", "CL_Awesomium_Surface", "_Awe_WebView_surface@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2A60u, 0x00000000u, "WebView::Destroy slot 0x00", "CL_Awesomium_Shutdown", "_Awe_WebView_Destroy@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2A60u, 0x0052C684u, "WebCore::Shutdown", "CL_Awesomium_Shutdown", "_Awe_WebCore_Shutdown@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0u, 0u, NULL, NULL, NULL, NULL },
};

static clAwesomiumState_t cl_awesomium;
static clAwesomiumImports_t cl_awe;

static void CL_Awesomium_AppendPath( char *buffer, size_t bufferSize, const char *root, const char *fileName );
static qboolean CL_Awesomium_FileExists( const char *path );
static qboolean CL_Awesomium_LoadImports( const char *runtimePath, const char *basePath );
static qboolean CL_Awesomium_PrepareConfig( const char *runtimePath, const char *basePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh, const char *initialConfigJson );
static void CL_Awesomium_BuildRetryScript( char *buffer, size_t bufferSize );
static qboolean CL_Awesomium_PreparePreferences( void );
static qboolean CL_Awesomium_CreateSession( const char *runtimePath, const char *basePath );

extern "C" void CL_Awesomium_Shutdown( void );
extern "C" void Com_Printf( const char *fmt, ... );
extern "C" qboolean CL_Awesomium_ExecuteJavascript( const char *script, const char *frame );
extern "C" qboolean CL_Awesomium_SetZoom( int zoomPercent );

/*
=============
CL_Awesomium_CountBootstrapRetailMappings

Returns the number of recovered bootstrap anchors retained as source-visible
documentation for the Win32 Awesomium adapter.
=============
*/
static int CL_Awesomium_CountBootstrapRetailMappings( void ) {
	int i;
	int count;

	count = 0;
	for ( i = 0; cl_aweBootstrapRetailMappings[i].retailMember; i++ ) {
		if ( cl_aweBootstrapRetailMappings[i].retailOwnerAddress != 0u || cl_aweBootstrapRetailMappings[i].retailAnchor != 0u ) {
			count++;
		}
	}

	return count;
}

/*
=============
CL_Awesomium_SetError
=============
*/
static void CL_Awesomium_SetError( const char *message ) {
	if ( !message ) {
		message = "unknown Awesomium error";
	}

	strncpy( cl_awesomium.lastError, message, sizeof( cl_awesomium.lastError ) - 1 );
	cl_awesomium.lastError[sizeof( cl_awesomium.lastError ) - 1] = '\0';
}


/*
=============
CL_Awesomium_ResolveImport
=============
*/
static qboolean CL_Awesomium_ResolveImport( FARPROC *target, const char *name ) {
	*target = GetProcAddress( cl_awesomium.module, name );
	if ( !*target ) {
		char buffer[256];

		_snprintf( buffer, sizeof( buffer ), "missing Awesomium SDK C API export %s", name );
		buffer[sizeof( buffer ) - 1] = '\0';
		CL_Awesomium_SetError( buffer );
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_Awesomium_ResolveOptionalImport
=============
*/
static FARPROC CL_Awesomium_ResolveOptionalImport( const char *name ) {
	return GetProcAddress( cl_awesomium.module, name );
}

/*
=============
CL_Awesomium_LoadLibraryCandidate
=============
*/
static HMODULE CL_Awesomium_LoadLibraryCandidate( const char *libraryPath, char *errorBuffer, size_t errorBufferSize ) {
	HMODULE module;
	DWORD errorCode;
	qboolean explicitPath;

	if ( !libraryPath || !libraryPath[0] ) {
		return NULL;
	}

	explicitPath = ( strchr( libraryPath, '\\' ) || strchr( libraryPath, '/' ) ) ? qtrue : qfalse;
	if ( explicitPath ) {
		module = LoadLibraryExA( libraryPath, NULL, LOAD_WITH_ALTERED_SEARCH_PATH );
	} else {
		module = LoadLibraryA( libraryPath );
	}
	if ( module ) {
		return module;
	}

	errorCode = GetLastError();
	if ( errorBuffer && errorBufferSize > 0 ) {
		_snprintf( errorBuffer, errorBufferSize, "%s (Win32 error %lu)", libraryPath, static_cast<unsigned long>( errorCode ) );
		errorBuffer[errorBufferSize - 1] = '\0';
	}

	return NULL;
}

/*
=============
CL_Awesomium_LoadImports
=============
*/
static qboolean CL_Awesomium_LoadImports( const char *runtimePath, const char *basePath ) {
	char libraryPath[MAX_PATH];
	char loadError[512];

	if ( cl_awesomium.importsResolved ) {
		return qtrue;
	}
	loadError[0] = '\0';

	if ( !cl_awesomium.module ) {
		cl_awesomium.module = CL_Awesomium_LoadLibraryCandidate( "awesomium.dll", loadError, sizeof( loadError ) );
		if ( !cl_awesomium.module ) {
			if ( runtimePath && runtimePath[0] ) {
				CL_Awesomium_AppendPath( libraryPath, sizeof( libraryPath ), runtimePath, "awesomium.dll" );
				cl_awesomium.module = CL_Awesomium_LoadLibraryCandidate( libraryPath, loadError, sizeof( loadError ) );
			}
		}
		if ( !cl_awesomium.module && basePath && basePath[0] ) {
			CL_Awesomium_AppendPath( libraryPath, sizeof( libraryPath ), basePath, "awesomium.dll" );
			cl_awesomium.module = CL_Awesomium_LoadLibraryCandidate( libraryPath, loadError, sizeof( loadError ) );
		}
		if ( !cl_awesomium.module ) {
			char buffer[768];

			_snprintf( buffer, sizeof( buffer ), "awesomium.dll was not found beside quakelive_steam.exe, runtimePath, or basePath; last load attempt: %s", loadError[0] ? loadError : "no Win32 error captured" );
			buffer[sizeof( buffer ) - 1] = '\0';
			CL_Awesomium_SetError( buffer );
			return qfalse;
		}
	}

#define CL_AWE_IMPORT( field, name ) \
	if ( !CL_Awesomium_ResolveImport( (FARPROC *)&cl_awe.field, name ) ) { \
		return qfalse; \
	}

	CL_AWE_IMPORT( newWebConfig, "_Awe_new_WebConfig@0" );
	CL_AWE_IMPORT( deleteWebConfig, "_Awe_delete_WebConfig@4" );
	CL_AWE_IMPORT( newWebPreferences, "_Awe_new_WebPreferences@0" );
	CL_AWE_IMPORT( deleteWebPreferences, "_Awe_delete_WebPreferences@4" );
	CL_AWE_IMPORT( webCoreInitialize, "_Awe_WebCore_Initialize@4" );
	CL_AWE_IMPORT( webCoreShutdown, "_Awe_WebCore_Shutdown@0" );
	CL_AWE_IMPORT( webCoreUpdate, "_Awe_WebCore_Update@4" );
	CL_AWE_IMPORT( webCoreCreateWebSession, "_Awe_WebCore_CreateWebSession@12" );
	CL_AWE_IMPORT( webCoreCreateWebView, "_Awe_WebCore_CreateWebView_0@20" );
	cl_awe.webConfigAssetProtocolSet = reinterpret_cast<awe_webcore_set_string_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_WebConfig_asset_protocol_set@8" ) );
	CL_AWE_IMPORT( webConfigChildProcessPathSet, "_Awe_WebConfig_child_process_path_set@8" );
	CL_AWE_IMPORT( webConfigLogPathSet, "_Awe_WebConfig_log_path_set@8" );
	CL_AWE_IMPORT( webConfigPackagePathSet, "_Awe_WebConfig_package_path_set@8" );
	CL_AWE_IMPORT( webConfigUserAgentSet, "_Awe_WebConfig_user_agent_set@8" );
	cl_awe.webConfigUserScriptSet = reinterpret_cast<awe_webcore_set_string_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_WebConfig_user_script_set@8" ) );
	CL_AWE_IMPORT( webPrefsEnablePluginsSet, "_Awe_WebPreferences_enable_plugins_set@8" );
	CL_AWE_IMPORT( webPrefsEnableWebSecuritySet, "_Awe_WebPreferences_enable_web_security_set@8" );
	CL_AWE_IMPORT( newDataPakSource, "_Awe_new_DataPakSource@4" );
	CL_AWE_IMPORT( deleteDataPakSource, "_Awe_delete_DataPakSource@4" );
	CL_AWE_IMPORT( newWebURL, "_Awe_new_WebURL_1@4" );
	CL_AWE_IMPORT( deleteWebURL, "_Awe_delete_WebURL@4" );
	CL_AWE_IMPORT( webSessionAddDataSource, "_Awe_WebSession_AddDataSource@12" );
	cl_awe.webSessionInitialize = reinterpret_cast<awe_websession_void_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_WebSession_Initialize@4" ) );
	cl_awe.webSessionClearCache = reinterpret_cast<awe_websession_void_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_WebSession_ClearCache@4" ) );
	CL_AWE_IMPORT( webSessionRelease, "_Awe_WebSession_Release@4" );
	CL_AWE_IMPORT( webViewDestroy, "_Awe_WebView_Destroy@4" );
	CL_AWE_IMPORT( webViewLoadURL, "_Awe_WebView_LoadURL@8" );
	CL_AWE_IMPORT( webViewExecuteJavascript, "_Awe_WebView_ExecuteJavascript@12" );
	cl_awe.webViewExecuteJavascriptWithResult = reinterpret_cast<awe_webview_execute_javascript_with_result_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_WebView_ExecuteJavascriptWithResult@12" ) );
	CL_AWE_IMPORT( webViewSetTransparent, "_Awe_WebView_SetTransparent@8" );
	cl_awe.webViewSetZoom = reinterpret_cast<awe_webview_set_zoom_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_WebView_SetZoom@8" ) );
	CL_AWE_IMPORT( webViewResize, "_Awe_WebView_Resize@12" );
	CL_AWE_IMPORT( webViewFocus, "_Awe_WebView_Focus@4" );
	CL_AWE_IMPORT( webViewUnfocus, "_Awe_WebView_Unfocus@4" );
	CL_AWE_IMPORT( webViewResumeRendering, "_Awe_WebView_ResumeRendering@4" );
	CL_AWE_IMPORT( webViewPauseRendering, "_Awe_WebView_PauseRendering@4" );
	CL_AWE_IMPORT( webViewReload, "_Awe_WebView_Reload@8" );
	CL_AWE_IMPORT( webViewStop, "_Awe_WebView_Stop@4" );
	CL_AWE_IMPORT( webViewInjectMouseMove, "_Awe_WebView_InjectMouseMove@12" );
	CL_AWE_IMPORT( webViewInjectMouseDown, "_Awe_WebView_InjectMouseDown@8" );
	CL_AWE_IMPORT( webViewInjectMouseUp, "_Awe_WebView_InjectMouseUp@8" );
	CL_AWE_IMPORT( webViewInjectMouseWheel, "_Awe_WebView_InjectMouseWheel@12" );
	CL_AWE_IMPORT( newWebKeyboardEvent, "_Awe_new_WebKeyboardEvent_1@12" );
	CL_AWE_IMPORT( deleteWebKeyboardEvent, "_Awe_delete_WebKeyboardEvent@4" );
	CL_AWE_IMPORT( webViewInjectKeyboardEvent, "_Awe_WebView_InjectKeyboardEvent@8" );
	CL_AWE_IMPORT( webViewSurface, "_Awe_WebView_surface@4" );
	CL_AWE_IMPORT( bitmapCopyTo, "_Awe_BitmapSurface_CopyTo@24" );
	CL_AWE_IMPORT( bitmapWidth, "_Awe_BitmapSurface_width@4" );
	CL_AWE_IMPORT( bitmapHeight, "_Awe_BitmapSurface_height@4" );
	CL_AWE_IMPORT( bitmapIsDirty, "_Awe_BitmapSurface_is_dirty@4" );
	CL_AWE_IMPORT( bitmapSetIsDirty, "_Awe_BitmapSurface_set_is_dirty@8" );
	cl_awe.bitmapRowSpan = reinterpret_cast<awe_bitmap_dimension_fn>( GetProcAddress( cl_awesomium.module, "_Awe_BitmapSurface_row_span@4" ) );
	cl_awe.bitmapBuffer = reinterpret_cast<awe_bitmap_buffer_fn>( GetProcAddress( cl_awesomium.module, "_Awe_BitmapSurface_buffer@4" ) );
	cl_awe.webViewIsLoading = reinterpret_cast<awe_webview_query_bool_fn>( GetProcAddress( cl_awesomium.module, "_Awe_WebView_IsLoading@4" ) );
	cl_awe.webViewIsCrashed = reinterpret_cast<awe_webview_query_bool_fn>( GetProcAddress( cl_awesomium.module, "_Awe_WebView_IsCrashed@4" ) );
	cl_awe.webViewLastError = reinterpret_cast<awe_webview_query_int_fn>( GetProcAddress( cl_awesomium.module, "_Awe_WebView_last_error@4" ) );
	cl_awe.jsValueToInteger = reinterpret_cast<awe_jsvalue_to_integer_fn>( GetProcAddress( cl_awesomium.module, "_Awe_JSValue_ToInteger@4" ) );
	cl_awe.deleteJSValue = reinterpret_cast<awe_delete_object_fn>( GetProcAddress( cl_awesomium.module, "_Awe_delete_JSValue@4" ) );

#undef CL_AWE_IMPORT

	cl_awesomium.bootstrapMappingCount = CL_Awesomium_CountBootstrapRetailMappings();
	cl_awesomium.importsResolved = qtrue;
	CL_Awesomium_SetError( "" );
	return qtrue;
}

/*
=============
CL_Awesomium_AllocWideString
=============
*/
static unsigned short *CL_Awesomium_AllocWideString( const char *value ) {
	int required;
	wchar_t *wide;

	if ( !value ) {
		value = "";
	}

	required = MultiByteToWideChar( CP_UTF8, 0, value, -1, NULL, 0 );
	if ( required <= 0 ) {
		required = MultiByteToWideChar( CP_ACP, 0, value, -1, NULL, 0 );
		if ( required <= 0 ) {
			return NULL;
		}

		wide = new wchar_t[required];
		if ( !wide ) {
			return NULL;
		}
		MultiByteToWideChar( CP_ACP, 0, value, -1, wide, required );
		return (unsigned short *)wide;
	}

	wide = new wchar_t[required];
	if ( !wide ) {
		return NULL;
	}

	MultiByteToWideChar( CP_UTF8, 0, value, -1, wide, required );
	return (unsigned short *)wide;
}

/*
=============
CL_Awesomium_SetConfigString
=============
*/
static qboolean CL_Awesomium_SetConfigString( awe_webcore_set_string_fn setter, void *config, const char *value ) {
	unsigned short *wide;

	if ( !setter ) {
		return qtrue;
	}

	wide = CL_Awesomium_AllocWideString( value );
	if ( !wide ) {
		CL_Awesomium_SetError( "could not convert string for Awesomium" );
		return qfalse;
	}

	setter( config, wide );
	delete[] (wchar_t *)wide;
	return qtrue;
}

/*
=============
CL_Awesomium_AppendPath
=============
*/
static void CL_Awesomium_AppendPath( char *buffer, size_t bufferSize, const char *root, const char *fileName ) {
	size_t length;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !root || !root[0] || !fileName || !fileName[0] ) {
		return;
	}

	length = strlen( root );
	if ( root[length - 1] == '\\' || root[length - 1] == '/' ) {
		_snprintf( buffer, bufferSize, "%s%s", root, fileName );
	} else {
	_snprintf( buffer, bufferSize, "%s\\%s", root, fileName );
	}
	buffer[bufferSize - 1] = '\0';
}

/*
=============
CL_Awesomium_FileExists
=============
*/
static qboolean CL_Awesomium_FileExists( const char *path ) {
	if ( !path || !path[0] ) {
		return qfalse;
	}

	return GetFileAttributesA( path ) != INVALID_FILE_ATTRIBUTES;
}

/*
=============
CL_Awesomium_EscapeScriptString
=============
*/
static void CL_Awesomium_EscapeScriptString( const char *value, char *buffer, size_t bufferSize ) {
	size_t out;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !value ) {
		return;
	}

	out = 0;
	while ( *value && out + 2 < bufferSize ) {
		unsigned char ch;

		ch = (unsigned char)*value++;
		if ( ch == '\\' || ch == '"' ) {
			buffer[out++] = '\\';
			buffer[out++] = (char)ch;
		} else if ( ch == '\n' || ch == '\r' || ch == '\t' ) {
			buffer[out++] = ' ';
		} else if ( ch >= 32 ) {
			buffer[out++] = (char)ch;
		}
	}

	buffer[out] = '\0';
}

/*
=============
CL_Awesomium_BuildUserScript
=============
*/
static void CL_Awesomium_BuildUserScript( char *buffer, size_t bufferSize, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh, const char *initialConfigJson ) {
	char escapedName[256];
	char steamId[64];
	const char *configJson;

	CL_Awesomium_EscapeScriptString( playerName ? playerName : "", escapedName, sizeof( escapedName ) );
	if ( steamIdHigh || steamIdLow ) {
		_snprintf( steamId, sizeof( steamId ), "%u%010u", steamIdHigh, steamIdLow );
	} else {
		strcpy( steamId, "0" );
	}
	steamId[sizeof( steamId ) - 1] = '\0';
	configJson = ( initialConfigJson && initialConfigJson[0] ) ? initialConfigJson : "null";

	int written;

	written = _snprintf(
		buffer,
		bufferSize,
		"(function(){if(window.__qlr_qz_instance_ready){if(window.main_hook_v2){window.main_hook_v2();}return;}window.__qlr_qz_instance_ready=true;"
		"var noop=function(){return false;};var empty=function(){return [];};"
		"var maps={campgrounds:{id:'campgrounds',name:'Campgrounds',sysname:'campgrounds',gametypes:{0:true}}};"
		"var factories={ffa:{id:'ffa',title:'Free For All',basegt:0,settings:{}}};"
		"var config={cvars:{sv_servertype:'0',net_port:'27960',sv_hostname:'Quake Live Reverse',sv_maxclients:'8'},binds:[]};"
		"var nativeQueue=window.__qlr_native_requests=window.__qlr_native_requests||[];"
		"var canon=function(n){return String(n||'').toLowerCase();};"
		"var queue=function(kind,payload){try{nativeQueue.push(String(kind||'')+'\\n'+String(payload||''));return true;}catch(e){return false;}};"
		"var setNativeCvar=function(n,v){var k=canon(n);if(k){config.cvars[k]=String(v||'');}return true;};"
		"var applyNativeConfig=function(cfg){try{if(!cfg){return false;}config.version=cfg.version||config.version;"
		"if(typeof cfg.appId!=='undefined'){qz.appId=cfg.appId;}if(cfg.steamId){qz.steamId=String(cfg.steamId);}"
		"if(cfg.playerName){qz.playerName=String(cfg.playerName);}if(cfg.cvars){var out={};"
		"if(typeof cfg.cvars.length==='number'){for(var ci=0;ci<cfg.cvars.length;ci++){var cv=cfg.cvars[ci];if(cv&&cv.name){out[canon(cv.name)]=String(cv.value||'');}}}"
		"else{for(var ck in cfg.cvars){out[canon(ck)]=String(cfg.cvars[ck]||'');}}config.cvars=out;}if(cfg.binds){config.binds=cfg.binds;}return true;}catch(e){return false;}};"
		"var qz={appId:%u,steamId:\"%s\",playerName:\"%s\","
		"SendGameCommand:function(cmd){cmd=String(cmd||'');console.log('qz SendGameCommand: '+cmd);var m=/^\\s*web_changeHash(?:\\s+(.*))?\\s*$/.exec(cmd);if(m){window.location.hash=(m[1]||'').replace(/^#/,'');}return queue('cmd',cmd);},"
		"WriteTextFile:noop,OpenURL:function(url){document.location.href=url;},"
		"OpenSteamOverlayURL:function(url){console.log('qz OpenSteamOverlayURL: '+url);},"
		"GetClipboardText:function(){return '';},SetClipboardText:noop,"
		"RequestServers:noop,RequestServerDetails:noop,RefreshList:noop,"
		"CreateLobby:noop,LeaveLobby:noop,JoinLobby:noop,SetLobbyServer:noop,"
		"ShowInviteOverlay:noop,SayLobby:noop,RequestUserStats:noop,"
		"ActivateGameOverlayToUser:noop,Invite:noop,GetAllUGC:function(){return [];},"
		"GetNextKeyDown:noop,SetFavoriteServer:noop,"
		"IsPakFilePresent:function(){return true;},IsGameRunning:function(){return false;},"
		"FileExists:function(){return false;},GetCvar:function(name){var k=canon(name);if(k&&typeof config.cvars[k]==='undefined'){queue('get',k);}return config.cvars[k]||'';},"
		"SetCvar:function(name,value){var k=canon(name);if(!k){return false;}value=String(value||'');config.cvars[k]=value;return queue('set',k+'\\n'+value);},ResetCvar:function(name){var k=canon(name);if(!k){return false;}delete config.cvars[k];return queue('reset',k);},"
		"GetMapList:function(){return maps;},GetFactoryList:function(){return factories;},GetDemoList:empty,"
		"GetFriendList:empty,GetConfig:function(){return config;},GetCursorPosition:function(){return {x:0,y:0};}};"
		"var loading=function(){try{var show=function(){if(document.getElementById('__qlr_menu_loading')){return;}"
		"document.documentElement.style.backgroundColor='#07131d';document.body.style.backgroundColor='#07131d';"
		"var d=document.createElement('div');d.id='__qlr_menu_loading';"
		"d.style.cssText='position:fixed;left:0;top:0;right:0;bottom:0;z-index:2147483647;"
		"background:radial-gradient(circle at 60%% 35%%,#204f66,#03080c 65%%);color:white;"
		"font:24px sans-serif;display:flex;align-items:center;justify-content:center;text-shadow:0 0 8px #000';"
		"d.appendChild(document.createTextNode('Loading Quake Live menu...'));document.body.appendChild(d);"
		"var t=setInterval(function(){var app=document.getElementById('app');if(app&&app.childNodes&&app.childNodes.length){"
		"if(d.parentNode){d.parentNode.removeChild(d);}clearInterval(t);}},250);};"
		"if(document.body){show();}else{document.addEventListener('DOMContentLoaded',show,false);}}catch(e){}};loading();"
		"var ret=function(v){return function(){return v;};};var bind=function(n,f){if(typeof qz[n]==='undefined'){qz[n]=f;}};"
		"var fm='IsPakFilePresent IsGameRunning FileExists'.split(' ');for(var i=0;i<fm.length;i++){bind(fm[i],ret(false));}"
		"var nm='WriteTextFile OpenURL OpenSteamOverlayURL SetClipboardText RequestServers RequestServerDetails RefreshList CreateLobby LeaveLobby JoinLobby SetLobbyServer ShowInviteOverlay SayLobby RequestUserStats ActivateGameOverlayToUser Invite GetAllUGC GetNextKeyDown SetFavoriteServer NoOp'.split(' ');for(i=0;i<nm.length;i++){bind(nm[i],noop);}"
		"var em='GetDemoList GetFriendList'.split(' ');for(i=0;i<em.length;i++){bind(em[i],empty);}"
		"bind('GetCvar',function(n){var k=canon(n);if(k&&typeof config.cvars[k]==='undefined'){queue('get',k);}return config.cvars[k]||'';});bind('SetCvar',function(n,v){var k=canon(n);if(!k){return false;}v=String(v||'');config.cvars[k]=v;return queue('set',k+'\\n'+v);});bind('ResetCvar',function(n){var k=canon(n);if(!k){return false;}delete config.cvars[k];return queue('reset',k);});"
		"bind('GetMapList',function(){return maps;});bind('GetFactoryList',function(){return factories;});bind('GetClipboardText',ret(''));bind('GetConfig',function(){return config;});bind('GetCursorPosition',function(){return {x:0,y:0};});"
		"if(!window.FakeClient){window.FakeClient={};}if(!window.FakeClient.qz_instance){window.FakeClient.qz_instance={};}"
		"window.__qlr_apply_native_config=applyNativeConfig;window.__qlr_set_native_cvar=setNativeCvar;"
		"window.__qlr_initial_config_applied=applyNativeConfig(%s);"
		"window.qz_instance=qz;window.main_hook_v2=function(){var f=window.FakeClient&&window.FakeClient.qz_instance;"
		"if(f){for(var k in qz){f[k]=qz[k];}}window.qz_instance=qz;if(typeof window.EnginePublish==='function'&&!window.EnginePublish.__qlr_wrapped){var oldPublish=window.EnginePublish;var wrapped=function(topic,data){try{if(String(topic).indexOf('cvar.')===0){var d=typeof data==='string'?JSON.parse(data):data;if(d){setNativeCvar(d.name||String(topic).substr(5),d.value||'');}}}catch(e){}return oldPublish.apply(this,arguments);};wrapped.__qlr_wrapped=true;window.EnginePublish=wrapped;}};window.main_hook_v2();"
		"if(document.addEventListener){document.addEventListener('DOMContentLoaded',window.main_hook_v2,false);}"
		"window.__qlr_browser_helpers_ready=true;try{var qlrReadyEvent=document.createEvent('Event');"
		"qlrReadyEvent.initEvent('qz_instance.ready',false,false);document.dispatchEvent(qlrReadyEvent);}catch(qlrReadyError){}"
		"var qlrBridgeTries=0;var qlrBridgeTimer=setInterval(function(){window.main_hook_v2();"
		"if(++qlrBridgeTries>=40){clearInterval(qlrBridgeTimer);}},250);window.__qlr_qz_instance_script_complete=true;})();",
		appId,
		steamId,
		escapedName,
		configJson
	);
	buffer[bufferSize - 1] = '\0';
	if ( written < 0 || (size_t)written >= bufferSize ) {
		Com_Printf( "Awesomium startup script truncated before injection\n" );
	}
}

/*
=============
CL_Awesomium_BuildRetryScript

Re-runs only the lightweight browser helper hook after page scripts mutate the
FakeClient object. The full startup bridge carries the native config snapshot
and is intentionally not reparsed every retry frame.
=============
*/
static void CL_Awesomium_BuildRetryScript( char *buffer, size_t bufferSize ) {
	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	_snprintf(
		buffer,
		bufferSize,
		"(function(){if(window.main_hook_v2){window.main_hook_v2();}})();"
	);
	buffer[bufferSize - 1] = '\0';
}

/*
=============
CL_Awesomium_PrepareConfig
=============
*/
static qboolean CL_Awesomium_PrepareConfig( const char *runtimePath, const char *basePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh, const char *initialConfigJson ) {
	char childProcessPath[MAX_PATH];
	char logPath[MAX_PATH];
	char packagePath[MAX_PATH];
	char packageRoot[MAX_PATH];
	const char *sessionPath;
	const char *assetsPath;

	Com_Printf( "Awesomium startup phase: creating WebConfig\n" );
	cl_awesomium.webConfig = cl_awe.newWebConfig();
	if ( !cl_awesomium.webConfig ) {
		CL_Awesomium_SetError( "could not allocate Awesomium WebConfig" );
		return qfalse;
	}

	sessionPath = runtimePath;
	assetsPath = basePath && basePath[0] ? basePath : runtimePath;

	CL_Awesomium_AppendPath( childProcessPath, sizeof( childProcessPath ), assetsPath, "awesomium_process.exe" );
	CL_Awesomium_AppendPath( logPath, sizeof( logPath ), sessionPath, "awesomium.log" );
	CL_Awesomium_AppendPath( packagePath, sizeof( packagePath ), assetsPath, "web.pak" );
	strncpy( packageRoot, assetsPath, sizeof( packageRoot ) - 1 );
	packageRoot[sizeof( packageRoot ) - 1] = '\0';
	if ( !CL_Awesomium_FileExists( packagePath ) && sessionPath && sessionPath[0] ) {
		CL_Awesomium_AppendPath( packagePath, sizeof( packagePath ), sessionPath, "web.pak" );
		strncpy( packageRoot, sessionPath, sizeof( packageRoot ) - 1 );
		packageRoot[sizeof( packageRoot ) - 1] = '\0';
	}
	if ( !CL_Awesomium_FileExists( childProcessPath ) && sessionPath && sessionPath[0] ) {
		CL_Awesomium_AppendPath( childProcessPath, sizeof( childProcessPath ), sessionPath, "awesomium_process.exe" );
	}
	CL_Awesomium_BuildUserScript( cl_awesomium.startupScript, sizeof( cl_awesomium.startupScript ), playerName, appId, steamIdLow, steamIdHigh, initialConfigJson );
	CL_Awesomium_BuildRetryScript( cl_awesomium.startupRetryScript, sizeof( cl_awesomium.startupRetryScript ) );
	if ( !CL_Awesomium_FileExists( childProcessPath ) ) {
		CL_Awesomium_SetError( "awesomium_process.exe was not found in runtimePath or basePath" );
		return qfalse;
	}
	if ( !CL_Awesomium_FileExists( packagePath ) ) {
		CL_Awesomium_SetError( "web.pak was not found in runtimePath or basePath; install or stage web assets" );
		return qfalse;
	}

	Com_Printf( "Awesomium startup phase: applying WebConfig\n" );
	if ( !CL_Awesomium_SetConfigString( cl_awe.webConfigAssetProtocolSet, cl_awesomium.webConfig, "asset" )
		|| !CL_Awesomium_SetConfigString( cl_awe.webConfigChildProcessPathSet, cl_awesomium.webConfig, childProcessPath )
		|| !CL_Awesomium_SetConfigString( cl_awe.webConfigLogPathSet, cl_awesomium.webConfig, logPath )
		|| !CL_Awesomium_SetConfigString( cl_awe.webConfigPackagePathSet, cl_awesomium.webConfig, packageRoot )
		|| !CL_Awesomium_SetConfigString( cl_awe.webConfigUserAgentSet, cl_awesomium.webConfig, "Mozilla/5.0 (Windows NT 10.0; Win32; x86) QuakeLiveReverse/1.0" )
		|| !CL_Awesomium_SetConfigString( cl_awe.webConfigUserScriptSet, cl_awesomium.webConfig, cl_awesomium.startupScript ) ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_Awesomium_PreparePreferences
=============
*/
static qboolean CL_Awesomium_PreparePreferences( void ) {
	Com_Printf( "Awesomium startup phase: creating WebPreferences\n" );
	cl_awesomium.webPreferences = cl_awe.newWebPreferences();
	if ( !cl_awesomium.webPreferences ) {
		CL_Awesomium_SetError( "could not allocate Awesomium WebPreferences" );
		return qfalse;
	}

	Com_Printf( "Awesomium startup phase: applying WebPreferences\n" );
	cl_awe.webPrefsEnablePluginsSet( cl_awesomium.webPreferences, true );
	cl_awe.webPrefsEnableWebSecuritySet( cl_awesomium.webPreferences, false );
	return qtrue;
}

/*
=============
CL_Awesomium_CreateSession
=============
*/
static qboolean CL_Awesomium_CreateSession( const char *runtimePath, const char *basePath ) {
	unsigned short *dataPath;
	unsigned short *sourceName;
	unsigned short *pakName;
	char pakPath[MAX_PATH];
	const char *sessionPath;
	const char *assetsPath;

	dataPath = CL_Awesomium_AllocWideString( runtimePath );
	if ( !dataPath ) {
		CL_Awesomium_SetError( "could not convert session path for Awesomium" );
		return qfalse;
	}

	Com_Printf( "Awesomium startup phase: creating WebSession\n" );
	cl_awesomium.webSession = cl_awe.webCoreCreateWebSession( cl_awesomium.webCore, dataPath, cl_awesomium.webPreferences );
	delete[] (wchar_t *)dataPath;
	if ( !cl_awesomium.webSession ) {
		CL_Awesomium_SetError( "could not create Awesomium WebSession" );
		return qfalse;
	}
	if ( cl_awe.webSessionInitialize ) {
		Com_Printf( "Awesomium startup phase: initializing WebSession\n" );
		cl_awe.webSessionInitialize( cl_awesomium.webSession );
	}

	sessionPath = runtimePath;
	assetsPath = basePath && basePath[0] ? basePath : runtimePath;
	CL_Awesomium_AppendPath( pakPath, sizeof( pakPath ), assetsPath, "web.pak" );
	if ( !CL_Awesomium_FileExists( pakPath ) && sessionPath && sessionPath[0] ) {
		CL_Awesomium_AppendPath( pakPath, sizeof( pakPath ), sessionPath, "web.pak" );
	}
	if ( !CL_Awesomium_FileExists( pakPath ) ) {
		CL_Awesomium_SetError( "web.pak was not found in runtimePath or basePath; install or stage web assets" );
		return qfalse;
	}

	pakName = CL_Awesomium_AllocWideString( "web.pak" );
	if ( !pakName ) {
		CL_Awesomium_SetError( "could not convert web.pak path for Awesomium" );
		return qfalse;
	}
	Com_Printf( "Awesomium startup phase: creating DataPakSource\n" );
	cl_awesomium.dataPakSource = cl_awe.newDataPakSource( pakName );
	delete[] (wchar_t *)pakName;
	if ( !cl_awesomium.dataPakSource ) {
		CL_Awesomium_SetError( "could not create Awesomium DataPakSource for web.pak" );
		return qfalse;
	}

	sourceName = CL_Awesomium_AllocWideString( "QL" );
	if ( !sourceName ) {
		CL_Awesomium_SetError( "could not convert Awesomium data source name" );
		return qfalse;
	}
	Com_Printf( "Awesomium startup phase: attaching DataPakSource\n" );
	cl_awe.webSessionAddDataSource( cl_awesomium.webSession, sourceName, cl_awesomium.dataPakSource );
	delete[] (wchar_t *)sourceName;
	return qtrue;
}

/*
=============
CL_Awesomium_Surface
=============
*/
static void *CL_Awesomium_Surface( void ) {
	if ( !cl_awesomium.webView ) {
		return NULL;
	}

	return cl_awe.webViewSurface( cl_awesomium.webView );
}

/*
=============
CL_Awesomium_Startup
=============
*/
extern "C" qboolean CL_Awesomium_Startup( const char *runtimePath, const char *basePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh, int width, int height, const char *initialConfigJson ) {
	if ( cl_awesomium.started ) {
		if ( cl_awesomium.webView ) {
			cl_awe.webViewResize( cl_awesomium.webView, width, height );
		}
		return qtrue;
	}

	if ( !runtimePath || !runtimePath[0] ) {
		CL_Awesomium_SetError( "runtime path is empty" );
		return qfalse;
	}

	if ( !CL_Awesomium_LoadImports( runtimePath, basePath ) ) {
		return qfalse;
	}
	Com_Printf( "Awesomium startup phase: imports loaded\n" );

	if ( !CL_Awesomium_PrepareConfig( runtimePath, basePath, playerName, appId, steamIdLow, steamIdHigh, initialConfigJson )
		|| !CL_Awesomium_PreparePreferences() ) {
		CL_Awesomium_Shutdown();
		return qfalse;
	}

	Com_Printf( "Awesomium startup phase: initializing WebCore\n" );
	cl_awesomium.webCore = cl_awe.webCoreInitialize( cl_awesomium.webConfig );
	if ( !cl_awesomium.webCore ) {
		CL_Awesomium_SetError( "Unable to initialize WebCore" );
		CL_Awesomium_Shutdown();
		return qfalse;
	}

	if ( !CL_Awesomium_CreateSession( runtimePath, basePath ) ) {
		CL_Awesomium_Shutdown();
		return qfalse;
	}

	Com_Printf( "Awesomium startup phase: creating WebView\n" );
	cl_awesomium.webView = cl_awe.webCoreCreateWebView( cl_awesomium.webCore, width, height, cl_awesomium.webSession, 0 );
	if ( !cl_awesomium.webView ) {
		CL_Awesomium_SetError( "could not create Awesomium WebView" );
		CL_Awesomium_Shutdown();
		return qfalse;
	}

	cl_awe.webViewSetTransparent( cl_awesomium.webView, true );
	cl_awe.webViewResumeRendering( cl_awesomium.webView );
	cl_awe.webViewFocus( cl_awesomium.webView );
	Com_Printf( "Awesomium startup phase: live WebView ready\n" );
	cl_awesomium.started = qtrue;
	CL_Awesomium_SetError( "" );
	return qtrue;
}

/*
=============
CL_Awesomium_OpenURL
=============
*/
extern "C" qboolean CL_Awesomium_OpenURL( const char *url ) {
	unsigned short *wideUrl;
	void *webURL;

	if ( !cl_awesomium.started || !cl_awesomium.webView ) {
		CL_Awesomium_SetError( "Awesomium WebView is not active" );
		return qfalse;
	}

	if ( !url || !url[0] ) {
		url = "asset://ql/index.html";
	}

	wideUrl = CL_Awesomium_AllocWideString( url );
	if ( !wideUrl ) {
		CL_Awesomium_SetError( "could not convert URL for Awesomium" );
		return qfalse;
	}

	webURL = cl_awe.newWebURL( wideUrl );
	delete[] (wchar_t *)wideUrl;
	if ( !webURL ) {
		CL_Awesomium_SetError( "could not create Awesomium WebURL" );
		return qfalse;
	}

	cl_awe.webViewLoadURL( cl_awesomium.webView, webURL );
	CL_Awesomium_SetZoom( 100 );
	cl_awe.webViewResumeRendering( cl_awesomium.webView );
	cl_awe.webViewFocus( cl_awesomium.webView );
	cl_awe.deleteWebURL( webURL );
	cl_awesomium.urlLoaded = qtrue;
	cl_awesomium.startupScriptInjectionFrames = CL_AWE_STARTUP_SCRIPT_RETRY_FRAMES;
	return qtrue;
}

/*
=============
CL_Awesomium_ExecuteJavascript
=============
*/
extern "C" qboolean CL_Awesomium_ExecuteJavascript( const char *script, const char *frame ) {
	unsigned short *wideScript;
	unsigned short *wideFrame;

	if ( !cl_awesomium.started || !cl_awesomium.webView || !cl_awe.webViewExecuteJavascript || !script || !script[0] ) {
		return qfalse;
	}

	wideScript = CL_Awesomium_AllocWideString( script );
	wideFrame = CL_Awesomium_AllocWideString( frame ? frame : "" );
	if ( !wideScript || !wideFrame ) {
		delete[] (wchar_t *)wideScript;
		delete[] (wchar_t *)wideFrame;
		CL_Awesomium_SetError( "could not convert JavaScript for Awesomium" );
		return qfalse;
	}

	cl_awe.webViewExecuteJavascript( cl_awesomium.webView, wideScript, wideFrame );
	delete[] (wchar_t *)wideFrame;
	delete[] (wchar_t *)wideScript;
	return qtrue;
}

/*
=============
CL_Awesomium_ExecuteJavascriptInteger

Executes JavaScript through the Awesomium C API and converts the return value to
an integer. This is used for the source-owned qz bridge poller instead of full
JSValue string marshalling.
=============
*/
static qboolean CL_Awesomium_ExecuteJavascriptInteger( const char *script, const char *frame, int *outValue ) {
	unsigned short *wideScript;
	unsigned short *wideFrame;
	void *value;

	if ( outValue ) {
		*outValue = 0;
	}
	if ( !cl_awesomium.started || !cl_awesomium.webView || !cl_awe.webViewExecuteJavascriptWithResult
		|| !cl_awe.jsValueToInteger || !cl_awe.deleteJSValue || !script || !script[0] ) {
		return qfalse;
	}

	wideScript = CL_Awesomium_AllocWideString( script );
	wideFrame = CL_Awesomium_AllocWideString( frame ? frame : "" );
	if ( !wideScript || !wideFrame ) {
		delete[] (wchar_t *)wideScript;
		delete[] (wchar_t *)wideFrame;
		return qfalse;
	}

	value = cl_awe.webViewExecuteJavascriptWithResult( cl_awesomium.webView, wideScript, wideFrame );
	delete[] (wchar_t *)wideScript;
	delete[] (wchar_t *)wideFrame;
	if ( !value ) {
		return qfalse;
	}

	if ( outValue ) {
		*outValue = cl_awe.jsValueToInteger( value );
	}
	cl_awe.deleteJSValue( value );
	return qtrue;
}

/*
=============
CL_Awesomium_PopJavascriptRequest

Pops one queued qz_instance request from the injected WebUI bridge. Awesomium's
string JSValue conversion is intentionally avoided here; requests are copied
out one UTF-16 code unit at a time through integer return values.
=============
*/
extern "C" qboolean CL_Awesomium_PopJavascriptRequest( char *buffer, int bufferSize ) {
	int length;
	int i;

	if ( !buffer || bufferSize <= 0 ) {
		return qfalse;
	}
	buffer[0] = '\0';

	if ( !CL_Awesomium_ExecuteJavascriptInteger(
		"(function(){var q=window.__qlr_native_requests||[];if(!q.length){return -1;}window.__qlr_native_read=String(q.shift());return window.__qlr_native_read.length;})()",
		"",
		&length ) ) {
		return qfalse;
	}
	if ( length < 0 ) {
		return qfalse;
	}
	if ( length >= bufferSize ) {
		length = bufferSize - 1;
	}

	for ( i = 0; i < length; i++ ) {
		char script[160];
		int codepoint;

		_snprintf(
			script,
			sizeof( script ),
			"(function(){var s=window.__qlr_native_read||'';return s.charCodeAt(%d)||0;})()",
			i
		);
		script[sizeof( script ) - 1] = '\0';
		if ( !CL_Awesomium_ExecuteJavascriptInteger( script, "", &codepoint ) ) {
			buffer[0] = '\0';
			return qfalse;
		}
		if ( codepoint <= 0 || codepoint > 255 ) {
			buffer[i] = '?';
		} else {
			buffer[i] = (char)codepoint;
		}
	}
	buffer[length] = '\0';
	CL_Awesomium_ExecuteJavascript(
		"(function(){window.__qlr_native_read='';})()",
		""
	);
	return qtrue;
}

/*
=============
CL_Awesomium_SetZoom
=============
*/
extern "C" qboolean CL_Awesomium_SetZoom( int zoomPercent ) {
	if ( !cl_awesomium.started || !cl_awesomium.webView || !cl_awe.webViewSetZoom ) {
		return qfalse;
	}

	if ( zoomPercent <= 0 ) {
		zoomPercent = 100;
	}

	cl_awe.webViewSetZoom( cl_awesomium.webView, zoomPercent );
	return qtrue;
}

/*
=============
CL_Awesomium_PauseRendering
=============
*/
extern "C" void CL_Awesomium_PauseRendering( void ) {
	if ( cl_awesomium.started && cl_awesomium.webView && cl_awe.webViewPauseRendering ) {
		cl_awe.webViewPauseRendering( cl_awesomium.webView );
	}
}

/*
=============
CL_Awesomium_Unfocus
=============
*/
extern "C" void CL_Awesomium_Unfocus( void ) {
	if ( cl_awesomium.started && cl_awesomium.webView && cl_awe.webViewUnfocus ) {
		cl_awe.webViewUnfocus( cl_awesomium.webView );
	}
}

/*
=============
CL_Awesomium_Update
=============
*/
extern "C" void CL_Awesomium_Update( void ) {
	if ( cl_awesomium.started && cl_awesomium.webCore ) {
		cl_awe.webCoreUpdate( cl_awesomium.webCore );
		if ( cl_awesomium.startupScriptInjectionFrames > 0 && cl_awesomium.webView && cl_awesomium.startupScript[0] ) {
			if ( ( cl_awesomium.startupScriptInjectionFrames % CL_AWE_STARTUP_SCRIPT_RETRY_INTERVAL ) == 0 ) {
				const char *script;

				if ( cl_awesomium.startupScriptInjectionFrames == CL_AWE_STARTUP_SCRIPT_RETRY_FRAMES || !cl_awesomium.startupRetryScript[0] ) {
					script = cl_awesomium.startupScript;
				} else {
					script = cl_awesomium.startupRetryScript;
				}
				CL_Awesomium_ExecuteJavascript( script, "" );
			}
			cl_awesomium.startupScriptInjectionFrames--;
		}
	}
}

/*
=============
CL_Awesomium_Resize
=============
*/
extern "C" qboolean CL_Awesomium_Resize( int width, int height ) {
	if ( !cl_awesomium.started || !cl_awesomium.webView || width <= 0 || height <= 0 ) {
		return qfalse;
	}

	cl_awe.webViewResize( cl_awesomium.webView, width, height );
	return qtrue;
}

/*
=============
CL_Awesomium_SurfaceWidth
=============
*/
extern "C" int CL_Awesomium_SurfaceWidth( void ) {
	void *surface = CL_Awesomium_Surface();
	return surface ? cl_awe.bitmapWidth( surface ) : 0;
}

/*
=============
CL_Awesomium_SurfaceHeight
=============
*/
extern "C" int CL_Awesomium_SurfaceHeight( void ) {
	void *surface = CL_Awesomium_Surface();
	return surface ? cl_awe.bitmapHeight( surface ) : 0;
}

/*
=============
CL_Awesomium_SurfaceDirty
=============
*/
extern "C" qboolean CL_Awesomium_SurfaceDirty( void ) {
	void *surface = CL_Awesomium_Surface();
	return ( surface && cl_awe.bitmapIsDirty( surface ) ) ? qtrue : qfalse;
}

/*
=============
CL_Awesomium_IsLoading
=============
*/
extern "C" qboolean CL_Awesomium_IsLoading( void ) {
	if ( cl_awesomium.started && cl_awesomium.webView && cl_awe.webViewIsLoading && cl_awe.webViewIsLoading( cl_awesomium.webView ) ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
CL_Awesomium_IsCrashed
=============
*/
extern "C" qboolean CL_Awesomium_IsCrashed( void ) {
	if ( cl_awesomium.started && cl_awesomium.webView && cl_awe.webViewIsCrashed && cl_awe.webViewIsCrashed( cl_awesomium.webView ) ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
CL_Awesomium_LastErrorCode
=============
*/
extern "C" int CL_Awesomium_LastErrorCode( void ) {
	if ( cl_awesomium.started && cl_awesomium.webView && cl_awe.webViewLastError ) {
		return cl_awe.webViewLastError( cl_awesomium.webView );
	}

	return 0;
}

/*
=============
CL_Awesomium_CopySurface
=============
*/
extern "C" qboolean CL_Awesomium_CopySurface( byte *destination, int width, int height, int rowSpan ) {
	void *surface;
	const byte *source;
	int sourceRowSpan;
	int copyBytes;
	int byteCount;
	int y;

	if ( !destination || width <= 0 || height <= 0 || rowSpan <= 0 ) {
		return qfalse;
	}

	surface = CL_Awesomium_Surface();
	if ( !surface ) {
		return qfalse;
	}

	byteCount = rowSpan * height;
	if ( byteCount > 0 ) {
		memset( destination, 0, byteCount );
	}

	if ( cl_awe.bitmapCopyTo ) {
		cl_awe.bitmapCopyTo( surface, destination, rowSpan, 4, true, false );
		cl_awe.bitmapSetIsDirty( surface, false );
		return qtrue;
	}

	source = cl_awe.bitmapBuffer ? cl_awe.bitmapBuffer( surface ) : NULL;
	sourceRowSpan = cl_awe.bitmapRowSpan ? cl_awe.bitmapRowSpan( surface ) : 0;
	if ( source && sourceRowSpan > 0 ) {
		int copyPixels;

		copyPixels = width;
		if ( copyPixels > rowSpan / 4 ) {
			copyPixels = rowSpan / 4;
		}
		if ( copyPixels > sourceRowSpan / 4 ) {
			copyPixels = sourceRowSpan / 4;
		}
		copyBytes = copyPixels * 4;
		for ( y = 0; y < height; y++ ) {
			const byte *src;
			byte *dst;
			int x;

			src = source + y * sourceRowSpan;
			dst = destination + y * rowSpan;
			for ( x = 0; x < copyBytes; x += 4 ) {
				dst[x + 0] = src[x + 2];
				dst[x + 1] = src[x + 1];
				dst[x + 2] = src[x + 0];
				dst[x + 3] = src[x + 3];
			}
		}
		cl_awe.bitmapSetIsDirty( surface, false );
		return qtrue;
	}

	return qfalse;
}

/*
=============
CL_Awesomium_InjectMouseMove
=============
*/
extern "C" void CL_Awesomium_InjectMouseMove( int x, int y ) {
	if ( cl_awesomium.started && cl_awesomium.webView ) {
		cl_awe.webViewInjectMouseMove( cl_awesomium.webView, x, y );
	}
}

/*
=============
CL_Awesomium_InjectMouseDown
=============
*/
extern "C" void CL_Awesomium_InjectMouseDown( int button ) {
	if ( cl_awesomium.started && cl_awesomium.webView ) {
		cl_awe.webViewInjectMouseDown( cl_awesomium.webView, button );
	}
}

/*
=============
CL_Awesomium_InjectMouseUp
=============
*/
extern "C" void CL_Awesomium_InjectMouseUp( int button ) {
	if ( cl_awesomium.started && cl_awesomium.webView ) {
		cl_awe.webViewInjectMouseUp( cl_awesomium.webView, button );
	}
}

/*
=============
CL_Awesomium_InjectMouseWheel
=============
*/
extern "C" void CL_Awesomium_InjectMouseWheel( int direction ) {
	if ( cl_awesomium.started && cl_awesomium.webView ) {
		cl_awe.webViewInjectMouseWheel( cl_awesomium.webView, 0, direction * 30 );
	}
}

/*
=============
CL_Awesomium_InjectKeyboardEvent
=============
*/
extern "C" void CL_Awesomium_InjectKeyboardEvent( unsigned int eventType, unsigned int virtualKeyCode, long nativeKeyCode ) {
	if ( cl_awesomium.started && cl_awesomium.webView && cl_awe.newWebKeyboardEvent && cl_awe.webViewInjectKeyboardEvent ) {
		void *event;

		event = cl_awe.newWebKeyboardEvent( eventType, virtualKeyCode, nativeKeyCode );
		if ( event ) {
			cl_awe.webViewInjectKeyboardEvent( cl_awesomium.webView, event );
			cl_awe.deleteWebKeyboardEvent( event );
		}
	}
}

/*
=============
CL_Awesomium_Stop
=============
*/
extern "C" void CL_Awesomium_Stop( void ) {
	if ( cl_awesomium.started && cl_awesomium.webView ) {
		cl_awe.webViewStop( cl_awesomium.webView );
	}
}

/*
=============
CL_Awesomium_ClearCache
=============
*/
extern "C" void CL_Awesomium_ClearCache( void ) {
	if ( cl_awesomium.started && cl_awesomium.webSession && cl_awe.webSessionClearCache ) {
		cl_awe.webSessionClearCache( cl_awesomium.webSession );
	}
}

/*
=============
CL_Awesomium_Reload
=============
*/
extern "C" void CL_Awesomium_Reload( qboolean ignoreCache ) {
	if ( cl_awesomium.started && cl_awesomium.webView ) {
		cl_awe.webViewReload( cl_awesomium.webView, ignoreCache ? true : false );
	}
}

/*
=============
CL_Awesomium_Shutdown
=============
*/
extern "C" void CL_Awesomium_Shutdown( void ) {
	if ( cl_awesomium.webView && cl_awe.webViewDestroy ) {
		cl_awe.webViewDestroy( cl_awesomium.webView );
	}
	cl_awesomium.webView = NULL;

	if ( cl_awesomium.webSession && cl_awe.webSessionRelease ) {
		cl_awe.webSessionRelease( cl_awesomium.webSession );
	}
	cl_awesomium.webSession = NULL;
	cl_awesomium.dataPakSource = NULL;

	if ( cl_awesomium.webCore && cl_awe.webCoreShutdown ) {
		cl_awe.webCoreShutdown();
	}
	cl_awesomium.webCore = NULL;

	if ( cl_awesomium.webPreferences && cl_awe.deleteWebPreferences ) {
		cl_awe.deleteWebPreferences( cl_awesomium.webPreferences );
	}
	cl_awesomium.webPreferences = NULL;

	if ( cl_awesomium.webConfig && cl_awe.deleteWebConfig ) {
		cl_awe.deleteWebConfig( cl_awesomium.webConfig );
	}
	cl_awesomium.webConfig = NULL;
	cl_awesomium.started = qfalse;
	cl_awesomium.urlLoaded = qfalse;
}

/*
=============
CL_Awesomium_LastError
=============
*/
extern "C" const char *CL_Awesomium_LastError( void ) {
	return cl_awesomium.lastError[0] ? cl_awesomium.lastError : "";
}

#else

/*
=============
CL_Awesomium_Startup
=============
*/
extern "C" qboolean CL_Awesomium_Startup( const char *runtimePath, const char *basePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh, int width, int height, const char *initialConfigJson ) {
	(void)runtimePath;
	(void)basePath;
	(void)playerName;
	(void)appId;
	(void)steamIdLow;
	(void)steamIdHigh;
	(void)width;
	(void)height;
	(void)initialConfigJson;
	return qfalse;
}

/*
=============
CL_Awesomium_OpenURL
=============
*/
extern "C" qboolean CL_Awesomium_OpenURL( const char *url ) {
	(void)url;
	return qfalse;
}

/*
=============
CL_Awesomium_ExecuteJavascript
=============
*/
extern "C" qboolean CL_Awesomium_ExecuteJavascript( const char *script, const char *frame ) {
	(void)script;
	(void)frame;
	return qfalse;
}

/*
=============
CL_Awesomium_PopJavascriptRequest
=============
*/
extern "C" qboolean CL_Awesomium_PopJavascriptRequest( char *buffer, int bufferSize ) {
	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
	return qfalse;
}

/*
=============
CL_Awesomium_SetZoom
=============
*/
extern "C" qboolean CL_Awesomium_SetZoom( int zoomPercent ) {
	(void)zoomPercent;
	return qfalse;
}

/*
=============
CL_Awesomium_PauseRendering
=============
*/
extern "C" void CL_Awesomium_PauseRendering( void ) {
}

/*
=============
CL_Awesomium_Unfocus
=============
*/
extern "C" void CL_Awesomium_Unfocus( void ) {
}

/*
=============
CL_Awesomium_Update
=============
*/
extern "C" void CL_Awesomium_Update( void ) {
}

/*
=============
CL_Awesomium_Resize
=============
*/
extern "C" qboolean CL_Awesomium_Resize( int width, int height ) {
	(void)width;
	(void)height;
	return qfalse;
}

/*
=============
CL_Awesomium_SurfaceWidth
=============
*/
extern "C" int CL_Awesomium_SurfaceWidth( void ) {
	return 0;
}

/*
=============
CL_Awesomium_SurfaceHeight
=============
*/
extern "C" int CL_Awesomium_SurfaceHeight( void ) {
	return 0;
}

/*
=============
CL_Awesomium_SurfaceDirty
=============
*/
extern "C" qboolean CL_Awesomium_SurfaceDirty( void ) {
	return qfalse;
}

/*
=============
CL_Awesomium_IsLoading
=============
*/
extern "C" qboolean CL_Awesomium_IsLoading( void ) {
	return qfalse;
}

/*
=============
CL_Awesomium_IsCrashed
=============
*/
extern "C" qboolean CL_Awesomium_IsCrashed( void ) {
	return qfalse;
}

/*
=============
CL_Awesomium_LastErrorCode
=============
*/
extern "C" int CL_Awesomium_LastErrorCode( void ) {
	return 0;
}

/*
=============
CL_Awesomium_CopySurface
=============
*/
extern "C" qboolean CL_Awesomium_CopySurface( byte *destination, int width, int height, int rowSpan ) {
	(void)destination;
	(void)width;
	(void)height;
	(void)rowSpan;
	return qfalse;
}

/*
=============
CL_Awesomium_InjectMouseMove
=============
*/
extern "C" void CL_Awesomium_InjectMouseMove( int x, int y ) {
	(void)x;
	(void)y;
}

/*
=============
CL_Awesomium_InjectMouseDown
=============
*/
extern "C" void CL_Awesomium_InjectMouseDown( int button ) {
	(void)button;
}

/*
=============
CL_Awesomium_InjectMouseUp
=============
*/
extern "C" void CL_Awesomium_InjectMouseUp( int button ) {
	(void)button;
}

/*
=============
CL_Awesomium_InjectMouseWheel
=============
*/
extern "C" void CL_Awesomium_InjectMouseWheel( int direction ) {
	(void)direction;
}

/*
=============
CL_Awesomium_InjectKeyboardEvent
=============
*/
extern "C" void CL_Awesomium_InjectKeyboardEvent( unsigned int eventType, unsigned int virtualKeyCode, long nativeKeyCode ) {
	(void)eventType;
	(void)virtualKeyCode;
	(void)nativeKeyCode;
}

/*
=============
CL_Awesomium_Stop
=============
*/
extern "C" void CL_Awesomium_Stop( void ) {
}

/*
=============
CL_Awesomium_ClearCache
=============
*/
extern "C" void CL_Awesomium_ClearCache( void ) {
}

/*
=============
CL_Awesomium_Reload
=============
*/
extern "C" void CL_Awesomium_Reload( qboolean ignoreCache ) {
	(void)ignoreCache;
}

/*
=============
CL_Awesomium_Shutdown
=============
*/
extern "C" void CL_Awesomium_Shutdown( void ) {
}

/*
=============
CL_Awesomium_LastError
=============
*/
extern "C" const char *CL_Awesomium_LastError( void ) {
	return "online services disabled by build settings";
}

#endif
