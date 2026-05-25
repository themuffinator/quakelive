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
typedef void (__stdcall *awe_websession_add_source_fn)( void *session, const unsigned short *sourceName, void *dataSource );
typedef void (__stdcall *awe_websession_release_fn)( void *session );
typedef void *(__stdcall *awe_new_weburl_fn)( const unsigned short *url );
typedef void (__stdcall *awe_webview_destroy_fn)( void *view );
typedef void (__stdcall *awe_webview_load_url_fn)( void *view, void *url );
typedef void (__stdcall *awe_webview_resize_fn)( void *view, int width, int height );
typedef void (__stdcall *awe_webview_focus_fn)( void *view );
typedef void (__stdcall *awe_webview_resume_rendering_fn)( void *view );
typedef void (__stdcall *awe_webview_reload_fn)( void *view, bool ignoreCache );
typedef void (__stdcall *awe_webview_stop_fn)( void *view );
typedef void (__stdcall *awe_webview_execute_javascript_fn)( void *view, const unsigned short *script, const unsigned short *frame );
typedef void (__stdcall *awe_webview_mouse_move_fn)( void *view, int x, int y );
typedef void (__stdcall *awe_webview_mouse_button_fn)( void *view, int button );
typedef void (__stdcall *awe_webview_mouse_wheel_fn)( void *view, int x, int y );
typedef void *(__stdcall *awe_webview_surface_fn)( void *view );
typedef void (__stdcall *awe_bitmap_copy_to_fn)( void *surface, byte *destination, int rowSpan, int depth, bool convertToRGBA, bool flipY );
typedef int (__stdcall *awe_bitmap_dimension_fn)( void *surface );
typedef bool (__stdcall *awe_bitmap_bool_fn)( void *surface );
typedef void (__stdcall *awe_bitmap_set_bool_fn)( void *surface, bool value );

#define CL_AWE_OBJECT_STORAGE_BYTES 256
#define CL_AWE_WEBCORE_CREATE_SESSION_SLOT 0x00
#define CL_AWE_WEBCORE_CREATE_VIEW_SLOT 0x04
#define CL_AWE_WEBCORE_UPDATE_SLOT 0x18
#define CL_AWE_WEBSESSION_ADD_SOURCE_SLOT 0x10
#define CL_AWE_WEBSESSION_RELEASE_SLOT 0x1c
#define CL_AWE_WEBVIEW_DESTROY_SLOT 0x00
#define CL_AWE_WEBVIEW_LOAD_URL_SLOT 0x64
#define CL_AWE_WEBVIEW_EXECUTE_JAVASCRIPT_SLOT 0x124
#define CL_AWE_WEBVIEW_RESIZE_SLOT 0x9c
#define CL_AWE_WEBVIEW_RESUME_RENDERING_SLOT 0xac
#define CL_AWE_WEBVIEW_FOCUS_SLOT 0xb0
#define CL_AWE_WEBVIEW_RELOAD_SLOT 0x78
#define CL_AWE_WEBVIEW_STOP_SLOT 0x74
#define CL_AWE_WEBVIEW_MOUSE_MOVE_SLOT 0xd0
#define CL_AWE_WEBVIEW_MOUSE_DOWN_SLOT 0xd4
#define CL_AWE_WEBVIEW_MOUSE_UP_SLOT 0xd8
#define CL_AWE_WEBVIEW_MOUSE_WHEEL_SLOT 0xdc
#define CL_AWE_WEBVIEW_SURFACE_SLOT 0x84
#define CL_AWE_BITMAP_PIXELS_OFFSET 0x04
#define CL_AWE_BITMAP_WIDTH_OFFSET 0x08
#define CL_AWE_BITMAP_HEIGHT_OFFSET 0x0c
#define CL_AWE_BITMAP_DIRTY_OFFSET 0x14

typedef void (__thiscall *awe_retail_ctor_fn)( void *object );
typedef void (__thiscall *awe_retail_dtor_fn)( void *object );
typedef void (__cdecl *awe_retail_webcore_shutdown_fn)( void );
typedef void *(__cdecl *awe_retail_webcore_initialize_fn)( const void *config );
typedef void (__cdecl *awe_retail_webstring_create_utf8_fn)( void *outString, const char *value, unsigned int length );
typedef void (__thiscall *awe_retail_weburl_ctor_fn)( void *object, const void *url );
typedef void (__thiscall *awe_retail_datapak_ctor_fn)( void *object, const void *pakPath );
typedef void (__thiscall *awe_retail_bitmap_copy_to_fn)( const void *surface, byte *destination, int rowSpan, int depth, bool convertToRGBA, bool flipY );

typedef void *(__thiscall *awe_webcore_create_session_method_fn)( void *core, const void *dataPath, void *preferences );
typedef void *(__thiscall *awe_webcore_create_view_method_fn)( void *core, int width, int height, void *session, int type );
typedef void (__thiscall *awe_webcore_update_method_fn)( void *core );
typedef void (__thiscall *awe_websession_add_source_method_fn)( void *session, const void *sourceName, void *source );
typedef void (__thiscall *awe_websession_release_method_fn)( void *session );
typedef void (__thiscall *awe_webview_void_method_fn)( void *view );
typedef void (__thiscall *awe_webview_load_url_method_fn)( void *view, void *url );
typedef void (__thiscall *awe_webview_execute_javascript_method_fn)( void *view, const void *script, const void *frame );
typedef void (__thiscall *awe_webview_resize_method_fn)( void *view, int width, int height );
typedef void (__thiscall *awe_webview_bool_method_fn)( void *view, bool value );
typedef void (__thiscall *awe_webview_mouse_move_method_fn)( void *view, int x, int y );
typedef void (__thiscall *awe_webview_mouse_button_method_fn)( void *view, int button );
typedef void (__thiscall *awe_webview_mouse_wheel_method_fn)( void *view, int x, int y );
typedef void *(__thiscall *awe_webview_surface_method_fn)( void *view );

typedef struct {
	awe_retail_ctor_fn					webConfigCtor;
	awe_retail_dtor_fn					webConfigDtor;
	awe_retail_ctor_fn					webPreferencesCtor;
	awe_retail_dtor_fn					webPreferencesDtor;
	awe_retail_webcore_initialize_fn		webCoreInitialize;
	awe_retail_webcore_shutdown_fn		webCoreShutdown;
	awe_retail_webstring_create_utf8_fn	webStringCreateFromUTF8;
	awe_retail_dtor_fn					webStringDtor;
	awe_retail_weburl_ctor_fn			webURLCtor;
	awe_retail_dtor_fn					webURLDtor;
	awe_retail_datapak_ctor_fn			dataPakSourceCtor;
	awe_retail_dtor_fn					dataPakSourceDtor;
	awe_retail_bitmap_copy_to_fn			bitmapCopyTo;
	qboolean							active;
} clAwesomiumRetailImports_t;

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
	awe_webprefs_set_bool_fn			webPrefsEnableJavascriptSet;
	awe_webprefs_set_bool_fn			webPrefsEnableLocalStorageSet;
	awe_webprefs_set_bool_fn			webPrefsEnableDatabasesSet;
	awe_webprefs_set_bool_fn			webPrefsEnableWebSecuritySet;
	awe_webprefs_set_bool_fn			webPrefsAllowFileAccessSet;
	awe_webprefs_set_bool_fn			webPrefsAllowUniversalAccessSet;
	awe_new_datapak_source_fn		newDataPakSource;
	awe_delete_object_fn			deleteDataPakSource;
	awe_new_weburl_fn				newWebURL;
	awe_delete_object_fn			deleteWebURL;
	awe_websession_add_source_fn		webSessionAddDataSource;
	awe_websession_release_fn		webSessionRelease;
	awe_webview_destroy_fn			webViewDestroy;
	awe_webview_load_url_fn			webViewLoadURL;
	awe_webview_execute_javascript_fn	webViewExecuteJavascript;
	awe_webview_resize_fn			webViewResize;
	awe_webview_focus_fn				webViewFocus;
	awe_webview_resume_rendering_fn	webViewResumeRendering;
	awe_webview_reload_fn			webViewReload;
	awe_webview_stop_fn				webViewStop;
	awe_webview_mouse_move_fn		webViewInjectMouseMove;
	awe_webview_mouse_button_fn		webViewInjectMouseDown;
	awe_webview_mouse_button_fn		webViewInjectMouseUp;
	awe_webview_mouse_wheel_fn		webViewInjectMouseWheel;
	awe_webview_surface_fn			webViewSurface;
	awe_bitmap_copy_to_fn			bitmapCopyTo;
	awe_bitmap_dimension_fn			bitmapWidth;
	awe_bitmap_dimension_fn			bitmapHeight;
	awe_bitmap_bool_fn				bitmapIsDirty;
	awe_bitmap_set_bool_fn			bitmapSetIsDirty;
} clAwesomiumImports_t;

#define CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT "bounded C-export substitution"
#define CL_AWE_RETAIL_ABI_SCOPE_SOURCE_KEYBOARD "source-owned keyboard event path"
#define CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT "bounded C-export bootstrap substitution"
#define CL_AWE_RETAIL_BOOTSTRAP_SCOPE_OBJECT_LIFETIME "retail object lifetime mapped to adapter handle"
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
pointers and vtable slots. This backend intentionally keeps the online-services
path as a dynamically resolved C-export adapter, so each row below records the
source-visible substitution boundary rather than claiming literal ABI identity.
=============
*/
static const clAwesomiumRetailAbiEquivalence_t cl_aweRetailAbiEquivalence[] = {
	{ 0x004F2590u, 0x18u, "WebCore::Update", "CL_Awesomium_Update", "_Awe_WebCore_Update@4", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F25C0u, 0x9cu, "WebView::Resize", "CL_Awesomium_Resize", "_Awe_WebView_Resize@12", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F2750u, 0xd0u, "WebView::InjectMouseMove", "CL_Awesomium_InjectMouseMove", "_Awe_WebView_InjectMouseMove@12", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F27C0u, 0xd4u, "WebView::InjectMouseDown", "CL_Awesomium_InjectMouseDown", "_Awe_WebView_InjectMouseDown@8", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F2820u, 0xd8u, "WebView::InjectMouseUp", "CL_Awesomium_InjectMouseUp", "_Awe_WebView_InjectMouseUp@8", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F2870u, 0xdcu, "WebView::InjectMouseWheel", "CL_Awesomium_InjectMouseWheel", "_Awe_WebView_InjectMouseWheel@12", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F28A0u, 0xe0u, "WebView::InjectKeyboardEvent", "QLWebView_InjectKeyboardEvent", "cl_cgame.c field model", CL_AWE_RETAIL_ABI_SCOPE_SOURCE_KEYBOARD },
};

/*
=============
Awesomium retail bootstrap mapping table

Retail `QLWebHost_OpenURL` constructs the Awesomium core, session, data-source,
view, URL, focus, and shutdown chain directly through C++ constructors and
vtable slots. This backend keeps those seams source-visible while routing them
through the bounded dynamic C-export adapter.
=============
*/
static const clAwesomiumBootstrapRetailMapping_t cl_aweBootstrapRetailMappings[] = {
	{ 0x004F2D30u, 0x0052C6A4u, "WebConfig::WebConfig", "CL_Awesomium_PrepareConfig", "_Awe_new_WebConfig@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x0052C6A0u, "WebCore::Initialize", "CL_Awesomium_Startup", "_Awe_WebCore_Initialize@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x0052C698u, "WebPreferences::WebPreferences", "CL_Awesomium_PreparePreferences", "_Awe_new_WebPreferences@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000000u, "WebCore::CreateWebSession slot 0x00", "CL_Awesomium_CreateSession", "_Awe_WebCore_CreateWebSession@12", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000018u, "WebSession bootstrap slot 0x18", "CL_Awesomium_CreateSession", "session initialisation boundary", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_OBJECT_LIFETIME },
	{ 0x004F2D30u, 0x0052C694u, "DataPakSource::DataPakSource", "CL_Awesomium_CreateSession", "_Awe_new_DataPakSource@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00548068u, "QL data-source name", "CL_Awesomium_CreateSession", "\"QL\"", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_SOURCE_LITERAL },
	{ 0x004F2D30u, 0x00548070u, "DataPakSource::vftable", "CL_Awesomium_CreateSession", "Awesomium built-in DataPakSource", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_OBJECT_LIFETIME },
	{ 0x004F2D30u, 0x00000010u, "WebSession::AddDataSource slot 0x10", "CL_Awesomium_CreateSession", "_Awe_WebSession_AddDataSource@12", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000004u, "WebCore::CreateWebView slot 0x04", "CL_Awesomium_Startup", "_Awe_WebCore_CreateWebView_0@20", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000064u, "WebView::LoadURL slot 0x64", "CL_Awesomium_OpenURL", "_Awe_WebView_LoadURL@8", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x000000ACu, "WebView::ResumeRendering slot 0xAC", "CL_Awesomium_OpenURL", "_Awe_WebView_ResumeRendering@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x000000B0u, "WebView::Focus slot 0xB0", "CL_Awesomium_OpenURL", "_Awe_WebView_Focus@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000084u, "WebView::surface slot 0x84", "CL_Awesomium_Surface", "_Awe_WebView_surface@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2A60u, 0x00000000u, "WebView::Destroy slot 0x00", "CL_Awesomium_Shutdown", "_Awe_WebView_Destroy@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2A60u, 0x0052C684u, "WebCore::Shutdown", "CL_Awesomium_Shutdown", "_Awe_WebCore_Shutdown@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0u, 0u, NULL, NULL, NULL, NULL },
};

static clAwesomiumState_t cl_awesomium;
static clAwesomiumImports_t cl_awe;
static clAwesomiumRetailImports_t cl_aweRetail;

static void CL_Awesomium_AppendPath( char *buffer, size_t bufferSize, const char *root, const char *fileName );
static qboolean CL_Awesomium_FileExists( const char *path );
static qboolean CL_Awesomium_LoadImports( const char *runtimePath, const char *basePath );
static qboolean CL_Awesomium_PrepareConfig( const char *runtimePath, const char *basePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh );
static qboolean CL_Awesomium_PreparePreferences( void );
static qboolean CL_Awesomium_CreateSession( const char *runtimePath, const char *basePath );

extern "C" void CL_Awesomium_Shutdown( void );
extern "C" void Com_Printf( const char *fmt, ... );

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
CL_Awesomium_AllocRetailObject
=============
*/
static void *CL_Awesomium_AllocRetailObject( void ) {
	return HeapAlloc( GetProcessHeap(), HEAP_ZERO_MEMORY, CL_AWE_OBJECT_STORAGE_BYTES );
}

/*
=============
CL_Awesomium_FreeRetailObject
=============
*/
static void CL_Awesomium_FreeRetailObject( void *object ) {
	if ( object ) {
		HeapFree( GetProcessHeap(), 0, object );
	}
}

/*
=============
CL_Awesomium_WideToUTF8
=============
*/
static qboolean CL_Awesomium_WideToUTF8( const unsigned short *value, char *buffer, size_t bufferSize ) {
	int converted;

	if ( !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';
	if ( !value ) {
		return qtrue;
	}

	converted = WideCharToMultiByte( CP_UTF8, 0, reinterpret_cast<const wchar_t *>( value ), -1, buffer, static_cast<int>( bufferSize ), NULL, NULL );
	if ( converted <= 0 ) {
		buffer[bufferSize - 1] = '\0';
		return qfalse;
	}

	buffer[bufferSize - 1] = '\0';
	return qtrue;
}

/*
=============
CL_Awesomium_InitWebStringUTF8
=============
*/
static qboolean CL_Awesomium_InitWebStringUTF8( void *webString, const char *value ) {
	if ( !webString || !cl_aweRetail.webStringCreateFromUTF8 ) {
		return qfalse;
	}

	if ( !value ) {
		value = "";
	}

	memset( webString, 0, CL_AWE_OBJECT_STORAGE_BYTES );
	cl_aweRetail.webStringCreateFromUTF8( webString, value, static_cast<unsigned int>( strlen( value ) ) );
	return qtrue;
}

/*
=============
CL_Awesomium_InitWebStringWide
=============
*/
static qboolean CL_Awesomium_InitWebStringWide( void *webString, const unsigned short *value ) {
	char utf8[MAX_PATH * 4];

	if ( !CL_Awesomium_WideToUTF8( value, utf8, sizeof( utf8 ) ) ) {
		return qfalse;
	}

	return CL_Awesomium_InitWebStringUTF8( webString, utf8 );
}

/*
=============
CL_Awesomium_DestroyWebString
=============
*/
static void CL_Awesomium_DestroyWebString( void *webString ) {
	if ( webString && cl_aweRetail.webStringDtor ) {
		cl_aweRetail.webStringDtor( webString );
	}
}

/*
=============
CL_Awesomium_VTableMethod
=============
*/
static void *CL_Awesomium_VTableMethod( void *object, size_t slotOffset ) {
	void **vtable;

	if ( !object ) {
		return NULL;
	}

	vtable = *reinterpret_cast<void ***>( object );
	if ( !vtable ) {
		return NULL;
	}

	return *reinterpret_cast<void **>( reinterpret_cast<byte *>( vtable ) + slotOffset );
}

/*
=============
CL_Awesomium_RetailNewWebConfig
=============
*/
static void *__stdcall CL_Awesomium_RetailNewWebConfig( void ) {
	void *config;

	config = CL_Awesomium_AllocRetailObject();
	if ( config && cl_aweRetail.webConfigCtor ) {
		cl_aweRetail.webConfigCtor( config );
	}

	return config;
}

/*
=============
CL_Awesomium_RetailDeleteWebConfig
=============
*/
static void __stdcall CL_Awesomium_RetailDeleteWebConfig( void *config ) {
	if ( config && cl_aweRetail.webConfigDtor ) {
		cl_aweRetail.webConfigDtor( config );
	}

	CL_Awesomium_FreeRetailObject( config );
}

/*
=============
CL_Awesomium_RetailNewWebPreferences
=============
*/
static void *__stdcall CL_Awesomium_RetailNewWebPreferences( void ) {
	void *preferences;

	preferences = CL_Awesomium_AllocRetailObject();
	if ( preferences && cl_aweRetail.webPreferencesCtor ) {
		cl_aweRetail.webPreferencesCtor( preferences );
	}

	return preferences;
}

/*
=============
CL_Awesomium_RetailDeleteWebPreferences
=============
*/
static void __stdcall CL_Awesomium_RetailDeleteWebPreferences( void *preferences ) {
	if ( preferences && cl_aweRetail.webPreferencesDtor ) {
		cl_aweRetail.webPreferencesDtor( preferences );
	}

	CL_Awesomium_FreeRetailObject( preferences );
}

/*
=============
CL_Awesomium_RetailIgnorePointer
=============
*/
static void __stdcall CL_Awesomium_RetailIgnorePointer( void *object, const void *value ) {
	(void)object;
	(void)value;
}

/*
=============
CL_Awesomium_RetailIgnoreInteger
=============
*/
static void __stdcall CL_Awesomium_RetailIgnoreInteger( void *object, int value ) {
	(void)object;
	(void)value;
}

/*
=============
CL_Awesomium_RetailWebCoreInitialize
=============
*/
static void *__stdcall CL_Awesomium_RetailWebCoreInitialize( void *config ) {
	if ( !cl_aweRetail.webCoreInitialize ) {
		return NULL;
	}

	return cl_aweRetail.webCoreInitialize( config );
}

/*
=============
CL_Awesomium_RetailWebCoreShutdown
=============
*/
static void __stdcall CL_Awesomium_RetailWebCoreShutdown( void ) {
	if ( cl_aweRetail.webCoreShutdown ) {
		cl_aweRetail.webCoreShutdown();
	}
}

/*
=============
CL_Awesomium_RetailWebCoreUpdate
=============
*/
static void __stdcall CL_Awesomium_RetailWebCoreUpdate( void *core ) {
	awe_webcore_update_method_fn update;

	update = reinterpret_cast<awe_webcore_update_method_fn>( CL_Awesomium_VTableMethod( core, CL_AWE_WEBCORE_UPDATE_SLOT ) );
	if ( update ) {
		update( core );
	}
}

/*
=============
CL_Awesomium_RetailWebCoreCreateWebSession
=============
*/
static void *__stdcall CL_Awesomium_RetailWebCoreCreateWebSession( void *core, const unsigned short *dataPath, void *preferences ) {
	byte pathString[CL_AWE_OBJECT_STORAGE_BYTES];
	awe_webcore_create_session_method_fn createSession;
	void *session;

	createSession = reinterpret_cast<awe_webcore_create_session_method_fn>( CL_Awesomium_VTableMethod( core, CL_AWE_WEBCORE_CREATE_SESSION_SLOT ) );
	if ( !createSession || !CL_Awesomium_InitWebStringWide( pathString, dataPath ) ) {
		return NULL;
	}

	session = createSession( core, pathString, preferences );
	CL_Awesomium_DestroyWebString( pathString );
	return session;
}

/*
=============
CL_Awesomium_RetailWebCoreCreateWebView
=============
*/
static void *__stdcall CL_Awesomium_RetailWebCoreCreateWebView( void *core, int width, int height, void *session, int type ) {
	awe_webcore_create_view_method_fn createView;

	createView = reinterpret_cast<awe_webcore_create_view_method_fn>( CL_Awesomium_VTableMethod( core, CL_AWE_WEBCORE_CREATE_VIEW_SLOT ) );
	if ( !createView ) {
		return NULL;
	}

	return createView( core, width, height, session, type );
}

/*
=============
CL_Awesomium_RetailNewDataPakSource
=============
*/
static void *__stdcall CL_Awesomium_RetailNewDataPakSource( const unsigned short *pakPath ) {
	byte pathString[CL_AWE_OBJECT_STORAGE_BYTES];
	void *dataSource;

	if ( !cl_aweRetail.dataPakSourceCtor || !CL_Awesomium_InitWebStringWide( pathString, pakPath ) ) {
		return NULL;
	}

	dataSource = CL_Awesomium_AllocRetailObject();
	if ( dataSource ) {
		cl_aweRetail.dataPakSourceCtor( dataSource, pathString );
	}

	CL_Awesomium_DestroyWebString( pathString );
	return dataSource;
}

/*
=============
CL_Awesomium_RetailDeleteDataPakSource
=============
*/
static void __stdcall CL_Awesomium_RetailDeleteDataPakSource( void *dataSource ) {
	if ( dataSource && cl_aweRetail.dataPakSourceDtor ) {
		cl_aweRetail.dataPakSourceDtor( dataSource );
	}

	CL_Awesomium_FreeRetailObject( dataSource );
}

/*
=============
CL_Awesomium_RetailWebSessionAddDataSource
=============
*/
static void __stdcall CL_Awesomium_RetailWebSessionAddDataSource( void *session, const unsigned short *sourceName, void *dataSource ) {
	byte nameString[CL_AWE_OBJECT_STORAGE_BYTES];
	awe_websession_add_source_method_fn addDataSource;

	addDataSource = reinterpret_cast<awe_websession_add_source_method_fn>( CL_Awesomium_VTableMethod( session, CL_AWE_WEBSESSION_ADD_SOURCE_SLOT ) );
	if ( !addDataSource || !CL_Awesomium_InitWebStringWide( nameString, sourceName ) ) {
		return;
	}

	addDataSource( session, nameString, dataSource );
	CL_Awesomium_DestroyWebString( nameString );
}

/*
=============
CL_Awesomium_RetailWebSessionRelease
=============
*/
static void __stdcall CL_Awesomium_RetailWebSessionRelease( void *session ) {
	awe_websession_release_method_fn release;

	release = reinterpret_cast<awe_websession_release_method_fn>( CL_Awesomium_VTableMethod( session, CL_AWE_WEBSESSION_RELEASE_SLOT ) );
	if ( release ) {
		release( session );
	}
}

/*
=============
CL_Awesomium_RetailNewWebURL
=============
*/
static void *__stdcall CL_Awesomium_RetailNewWebURL( const unsigned short *url ) {
	byte urlString[CL_AWE_OBJECT_STORAGE_BYTES];
	void *webURL;

	if ( !cl_aweRetail.webURLCtor || !CL_Awesomium_InitWebStringWide( urlString, url ) ) {
		return NULL;
	}

	webURL = CL_Awesomium_AllocRetailObject();
	if ( webURL ) {
		cl_aweRetail.webURLCtor( webURL, urlString );
	}

	CL_Awesomium_DestroyWebString( urlString );
	return webURL;
}

/*
=============
CL_Awesomium_RetailDeleteWebURL
=============
*/
static void __stdcall CL_Awesomium_RetailDeleteWebURL( void *url ) {
	if ( url && cl_aweRetail.webURLDtor ) {
		cl_aweRetail.webURLDtor( url );
	}

	CL_Awesomium_FreeRetailObject( url );
}

/*
=============
CL_Awesomium_RetailWebViewDestroy
=============
*/
static void __stdcall CL_Awesomium_RetailWebViewDestroy( void *view ) {
	awe_webview_void_method_fn destroy;

	destroy = reinterpret_cast<awe_webview_void_method_fn>( CL_Awesomium_VTableMethod( view, CL_AWE_WEBVIEW_DESTROY_SLOT ) );
	if ( destroy ) {
		destroy( view );
	}
}

/*
=============
CL_Awesomium_RetailWebViewLoadURL
=============
*/
static void __stdcall CL_Awesomium_RetailWebViewLoadURL( void *view, void *url ) {
	awe_webview_load_url_method_fn loadURL;

	loadURL = reinterpret_cast<awe_webview_load_url_method_fn>( CL_Awesomium_VTableMethod( view, CL_AWE_WEBVIEW_LOAD_URL_SLOT ) );
	if ( loadURL ) {
		loadURL( view, url );
	}
}

/*
=============
CL_Awesomium_RetailWebViewResize
=============
*/
static void __stdcall CL_Awesomium_RetailWebViewResize( void *view, int width, int height ) {
	awe_webview_resize_method_fn resize;

	resize = reinterpret_cast<awe_webview_resize_method_fn>( CL_Awesomium_VTableMethod( view, CL_AWE_WEBVIEW_RESIZE_SLOT ) );
	if ( resize ) {
		resize( view, width, height );
	}
}

/*
=============
CL_Awesomium_RetailWebViewFocus
=============
*/
static void __stdcall CL_Awesomium_RetailWebViewFocus( void *view ) {
	awe_webview_void_method_fn focus;

	focus = reinterpret_cast<awe_webview_void_method_fn>( CL_Awesomium_VTableMethod( view, CL_AWE_WEBVIEW_FOCUS_SLOT ) );
	if ( focus ) {
		focus( view );
	}
}

/*
=============
CL_Awesomium_RetailWebViewResumeRendering
=============
*/
static void __stdcall CL_Awesomium_RetailWebViewResumeRendering( void *view ) {
	awe_webview_void_method_fn resumeRendering;

	resumeRendering = reinterpret_cast<awe_webview_void_method_fn>( CL_Awesomium_VTableMethod( view, CL_AWE_WEBVIEW_RESUME_RENDERING_SLOT ) );
	if ( resumeRendering ) {
		resumeRendering( view );
	}
}

/*
=============
CL_Awesomium_RetailWebViewReload
=============
*/
static void __stdcall CL_Awesomium_RetailWebViewReload( void *view, qboolean ignoreCache ) {
	awe_webview_bool_method_fn reload;

	reload = reinterpret_cast<awe_webview_bool_method_fn>( CL_Awesomium_VTableMethod( view, CL_AWE_WEBVIEW_RELOAD_SLOT ) );
	if ( reload ) {
		reload( view, ignoreCache ? true : false );
	}
}

/*
=============
CL_Awesomium_RetailWebViewExecuteJavascript
=============
*/
static void __stdcall CL_Awesomium_RetailWebViewExecuteJavascript( void *view, const unsigned short *script, const unsigned short *frame ) {
	static const unsigned short emptyFrame[] = { 0 };
	byte scriptString[CL_AWE_OBJECT_STORAGE_BYTES];
	byte frameString[CL_AWE_OBJECT_STORAGE_BYTES];
	awe_webview_execute_javascript_method_fn executeJavascript;

	if ( !script ) {
		return;
	}

	executeJavascript = reinterpret_cast<awe_webview_execute_javascript_method_fn>( CL_Awesomium_VTableMethod( view, CL_AWE_WEBVIEW_EXECUTE_JAVASCRIPT_SLOT ) );
	if ( !executeJavascript || !CL_Awesomium_InitWebStringWide( scriptString, script ) ) {
		return;
	}
	if ( !CL_Awesomium_InitWebStringWide( frameString, frame ? frame : emptyFrame ) ) {
		CL_Awesomium_DestroyWebString( scriptString );
		return;
	}

	executeJavascript( view, scriptString, frameString );
	CL_Awesomium_DestroyWebString( frameString );
	CL_Awesomium_DestroyWebString( scriptString );
}
/*
=============
CL_Awesomium_RetailWebViewStop
=============
*/
static void __stdcall CL_Awesomium_RetailWebViewStop( void *view ) {
	awe_webview_void_method_fn stop;

	stop = reinterpret_cast<awe_webview_void_method_fn>( CL_Awesomium_VTableMethod( view, CL_AWE_WEBVIEW_STOP_SLOT ) );
	if ( stop ) {
		stop( view );
	}
}

/*
=============
CL_Awesomium_RetailWebViewInjectMouseMove
=============
*/
static void __stdcall CL_Awesomium_RetailWebViewInjectMouseMove( void *view, int x, int y ) {
	awe_webview_mouse_move_method_fn injectMouseMove;

	injectMouseMove = reinterpret_cast<awe_webview_mouse_move_method_fn>( CL_Awesomium_VTableMethod( view, CL_AWE_WEBVIEW_MOUSE_MOVE_SLOT ) );
	if ( injectMouseMove ) {
		injectMouseMove( view, x, y );
	}
}

/*
=============
CL_Awesomium_RetailWebViewInjectMouseDown
=============
*/
static void __stdcall CL_Awesomium_RetailWebViewInjectMouseDown( void *view, int button ) {
	awe_webview_mouse_button_method_fn injectMouseDown;

	injectMouseDown = reinterpret_cast<awe_webview_mouse_button_method_fn>( CL_Awesomium_VTableMethod( view, CL_AWE_WEBVIEW_MOUSE_DOWN_SLOT ) );
	if ( injectMouseDown ) {
		injectMouseDown( view, button );
	}
}

/*
=============
CL_Awesomium_RetailWebViewInjectMouseUp
=============
*/
static void __stdcall CL_Awesomium_RetailWebViewInjectMouseUp( void *view, int button ) {
	awe_webview_mouse_button_method_fn injectMouseUp;

	injectMouseUp = reinterpret_cast<awe_webview_mouse_button_method_fn>( CL_Awesomium_VTableMethod( view, CL_AWE_WEBVIEW_MOUSE_UP_SLOT ) );
	if ( injectMouseUp ) {
		injectMouseUp( view, button );
	}
}

/*
=============
CL_Awesomium_RetailWebViewInjectMouseWheel
=============
*/
static void __stdcall CL_Awesomium_RetailWebViewInjectMouseWheel( void *view, int x, int y ) {
	awe_webview_mouse_wheel_method_fn injectMouseWheel;

	injectMouseWheel = reinterpret_cast<awe_webview_mouse_wheel_method_fn>( CL_Awesomium_VTableMethod( view, CL_AWE_WEBVIEW_MOUSE_WHEEL_SLOT ) );
	if ( injectMouseWheel ) {
		injectMouseWheel( view, x, y );
	}
}

/*
=============
CL_Awesomium_RetailWebViewSurface
=============
*/
static void *__stdcall CL_Awesomium_RetailWebViewSurface( void *view ) {
	awe_webview_surface_method_fn surface;

	surface = reinterpret_cast<awe_webview_surface_method_fn>( CL_Awesomium_VTableMethod( view, CL_AWE_WEBVIEW_SURFACE_SLOT ) );
	if ( !surface ) {
		return NULL;
	}

	return surface( view );
}

/*
=============
CL_Awesomium_RetailBitmapSurfaceWidth
=============
*/
static int __stdcall CL_Awesomium_RetailBitmapSurfaceWidth( void *surface ) {
	if ( !surface ) {
		return 0;
	}

	return *reinterpret_cast<int *>( reinterpret_cast<byte *>( surface ) + CL_AWE_BITMAP_WIDTH_OFFSET );
}

/*
=============
CL_Awesomium_RetailBitmapSurfaceHeight
=============
*/
static int __stdcall CL_Awesomium_RetailBitmapSurfaceHeight( void *surface ) {
	if ( !surface ) {
		return 0;
	}

	return *reinterpret_cast<int *>( reinterpret_cast<byte *>( surface ) + CL_AWE_BITMAP_HEIGHT_OFFSET );
}

/*
=============
CL_Awesomium_RetailBitmapSurfaceIsDirty
=============
*/
static qboolean __stdcall CL_Awesomium_RetailBitmapSurfaceIsDirty( void *surface ) {
	if ( CL_Awesomium_RetailBitmapSurfaceWidth( surface ) <= 0 || CL_Awesomium_RetailBitmapSurfaceHeight( surface ) <= 0 ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_Awesomium_RetailBitmapSurfaceSetIsDirty
=============
*/
static void __stdcall CL_Awesomium_RetailBitmapSurfaceSetIsDirty( void *surface, qboolean dirty ) {
	if ( surface ) {
		*reinterpret_cast<bool *>( reinterpret_cast<byte *>( surface ) + CL_AWE_BITMAP_DIRTY_OFFSET ) = dirty ? true : false;
	}
}

/*
=============
CL_Awesomium_RetailBitmapSurfaceCopyTo
=============
*/
static void __stdcall CL_Awesomium_RetailBitmapSurfaceCopyTo( void *surface, byte *destination, int rowSpan, int depth, qboolean convertToRGBA, qboolean flipY ) {
	byte *source;
	int width;
	int height;
	int bytesPerPixel;
	int copyBytes;
	int y;

	if ( !surface || !destination ) {
		return;
	}

	if ( cl_aweRetail.bitmapCopyTo ) {
		cl_aweRetail.bitmapCopyTo( surface, destination, rowSpan, depth, convertToRGBA ? true : false, flipY ? true : false );
		CL_Awesomium_RetailBitmapSurfaceSetIsDirty( surface, qfalse );
		return;
	}

	source = *reinterpret_cast<byte **>( reinterpret_cast<byte *>( surface ) + CL_AWE_BITMAP_PIXELS_OFFSET );
	width = CL_Awesomium_RetailBitmapSurfaceWidth( surface );
	height = CL_Awesomium_RetailBitmapSurfaceHeight( surface );
	bytesPerPixel = ( depth > 8 ) ? ( depth / 8 ) : depth;

	if ( !source || width <= 0 || height <= 0 || rowSpan <= 0 ) {
		return;
	}
	if ( bytesPerPixel <= 0 || bytesPerPixel > 4 ) {
		bytesPerPixel = 4;
	}

	copyBytes = width * bytesPerPixel;
	if ( copyBytes > rowSpan ) {
		copyBytes = rowSpan;
	}

	for ( y = 0; y < height; y++ ) {
		const int sourceY = flipY ? ( height - 1 - y ) : y;
		memcpy( destination + y * rowSpan, source + sourceY * width * 4, copyBytes );
	}

	CL_Awesomium_RetailBitmapSurfaceSetIsDirty( surface, qfalse );
}

/*
=============
CL_Awesomium_LoadRetailImports
=============
*/
static qboolean CL_Awesomium_LoadRetailImports( void ) {
	FARPROC proc;
	char error[256];

	if ( cl_aweRetail.active ) {
		return qtrue;
	}
	if ( !cl_awesomium.module ) {
		return qfalse;
	}

#define CL_AWESOMIUM_RETAIL_IMPORT( field, type, importName ) \
	do { \
		proc = GetProcAddress( cl_awesomium.module, importName ); \
		if ( !proc ) { \
			_snprintf( error, sizeof( error ), "missing retail Awesomium import %s", importName ); \
			error[sizeof( error ) - 1] = '\0'; \
			CL_Awesomium_SetError( error ); \
			memset( &cl_aweRetail, 0, sizeof( cl_aweRetail ) ); \
			return qfalse; \
		} \
		cl_aweRetail.field = reinterpret_cast<type>( proc ); \
	} while ( 0 )

	CL_AWESOMIUM_RETAIL_IMPORT( webConfigCtor, awe_retail_ctor_fn, "??0WebConfig@Awesomium@@QAE@XZ" );
	CL_AWESOMIUM_RETAIL_IMPORT( webConfigDtor, awe_retail_dtor_fn, "??1WebConfig@Awesomium@@QAE@XZ" );
	CL_AWESOMIUM_RETAIL_IMPORT( webPreferencesCtor, awe_retail_ctor_fn, "??0WebPreferences@Awesomium@@QAE@XZ" );
	CL_AWESOMIUM_RETAIL_IMPORT( webPreferencesDtor, awe_retail_dtor_fn, "??1WebPreferences@Awesomium@@QAE@XZ" );
	CL_AWESOMIUM_RETAIL_IMPORT( webCoreInitialize, awe_retail_webcore_initialize_fn, "?Initialize@WebCore@Awesomium@@SAPAV12@ABUWebConfig@2@@Z" );
	CL_AWESOMIUM_RETAIL_IMPORT( webCoreShutdown, awe_retail_webcore_shutdown_fn, "?Shutdown@WebCore@Awesomium@@SAXXZ" );
	CL_AWESOMIUM_RETAIL_IMPORT( webStringCreateFromUTF8, awe_retail_webstring_create_utf8_fn, "?CreateFromUTF8@WebString@Awesomium@@SA?AV12@PBDI@Z" );
	CL_AWESOMIUM_RETAIL_IMPORT( webStringDtor, awe_retail_dtor_fn, "??1WebString@Awesomium@@QAE@XZ" );
	CL_AWESOMIUM_RETAIL_IMPORT( webURLCtor, awe_retail_weburl_ctor_fn, "??0WebURL@Awesomium@@QAE@ABVWebString@1@@Z" );
	CL_AWESOMIUM_RETAIL_IMPORT( webURLDtor, awe_retail_dtor_fn, "??1WebURL@Awesomium@@QAE@XZ" );
	CL_AWESOMIUM_RETAIL_IMPORT( dataPakSourceCtor, awe_retail_datapak_ctor_fn, "??0DataPakSource@Awesomium@@QAE@ABVWebString@1@@Z" );
	CL_AWESOMIUM_RETAIL_IMPORT( dataPakSourceDtor, awe_retail_dtor_fn, "??1DataPakSource@Awesomium@@UAE@XZ" );
	proc = GetProcAddress( cl_awesomium.module, "?CopyTo@BitmapSurface@Awesomium@@QBEXPAEHH_N1@Z" );
	cl_aweRetail.bitmapCopyTo = reinterpret_cast<awe_retail_bitmap_copy_to_fn>( proc );

#undef CL_AWESOMIUM_RETAIL_IMPORT

	cl_aweRetail.active = qtrue;
	return qtrue;
}

/*
=============
CL_Awesomium_RetailAdapterForImport
=============
*/
static FARPROC CL_Awesomium_RetailAdapterForImport( const char *name ) {
	if ( !name || !CL_Awesomium_LoadRetailImports() ) {
		return NULL;
	}

	if ( strstr( name, "new_WebConfig" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailNewWebConfig );
	}
	if ( strstr( name, "delete_WebConfig" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailDeleteWebConfig );
	}
	if ( strstr( name, "WebConfig_" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailIgnorePointer );
	}
	if ( strstr( name, "new_WebPreferences" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailNewWebPreferences );
	}
	if ( strstr( name, "delete_WebPreferences" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailDeleteWebPreferences );
	}
	if ( strstr( name, "WebPreferences_" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailIgnoreInteger );
	}
	if ( strstr( name, "WebCore_Initialize" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebCoreInitialize );
	}
	if ( strstr( name, "WebCore_Shutdown" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebCoreShutdown );
	}
	if ( strstr( name, "WebCore_Update" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebCoreUpdate );
	}
	if ( strstr( name, "WebCore_CreateWebSession" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebCoreCreateWebSession );
	}
	if ( strstr( name, "WebCore_CreateWebView" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebCoreCreateWebView );
	}
	if ( strstr( name, "new_DataPakSource" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailNewDataPakSource );
	}
	if ( strstr( name, "delete_DataPakSource" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailDeleteDataPakSource );
	}
	if ( strstr( name, "WebSession_AddDataSource" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebSessionAddDataSource );
	}
	if ( strstr( name, "WebSession_Release" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebSessionRelease );
	}
	if ( strstr( name, "new_WebURL" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailNewWebURL );
	}
	if ( strstr( name, "delete_WebURL" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailDeleteWebURL );
	}
	if ( strstr( name, "WebView_Destroy" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebViewDestroy );
	}
	if ( strstr( name, "WebView_LoadURL" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebViewLoadURL );
	}
	if ( strstr( name, "WebView_ExecuteJavascript" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebViewExecuteJavascript );
	}	if ( strstr( name, "WebView_Resize" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebViewResize );
	}
	if ( strstr( name, "WebView_Focus" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebViewFocus );
	}
	if ( strstr( name, "WebView_ResumeRendering" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebViewResumeRendering );
	}
	if ( strstr( name, "WebView_Reload" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebViewReload );
	}
	if ( strstr( name, "WebView_Stop" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebViewStop );
	}
	if ( strstr( name, "WebView_InjectMouseMove" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebViewInjectMouseMove );
	}
	if ( strstr( name, "WebView_InjectMouseDown" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebViewInjectMouseDown );
	}
	if ( strstr( name, "WebView_InjectMouseUp" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebViewInjectMouseUp );
	}
	if ( strstr( name, "WebView_InjectMouseWheel" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebViewInjectMouseWheel );
	}
	if ( strstr( name, "WebView_surface" ) || strstr( name, "WebView_Surface" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailWebViewSurface );
	}
	if ( strstr( name, "BitmapSurface_width" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailBitmapSurfaceWidth );
	}
	if ( strstr( name, "BitmapSurface_height" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailBitmapSurfaceHeight );
	}
	if ( strstr( name, "BitmapSurface_is_dirty" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailBitmapSurfaceIsDirty );
	}
	if ( strstr( name, "BitmapSurface_set_is_dirty" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailBitmapSurfaceSetIsDirty );
	}
	if ( strstr( name, "BitmapSurface_CopyTo" ) ) {
		return reinterpret_cast<FARPROC>( CL_Awesomium_RetailBitmapSurfaceCopyTo );
	}

	return NULL;
}

/*
=============
CL_Awesomium_ResolveImport
=============
*/
static qboolean CL_Awesomium_ResolveImport( FARPROC *target, const char *name ) {
	*target = GetProcAddress( cl_awesomium.module, name );
	if ( !*target ) {
		*target = CL_Awesomium_RetailAdapterForImport( name );
	}
	if ( !*target ) {
		char buffer[256];

		_snprintf( buffer, sizeof( buffer ), "missing Awesomium export %s", name );
		buffer[sizeof( buffer ) - 1] = '\0';
		CL_Awesomium_SetError( buffer );
		return qfalse;
	}

	return qtrue;
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
	CL_AWE_IMPORT( webConfigAssetProtocolSet, "_Awe_WebConfig_asset_protocol_set@8" );
	CL_AWE_IMPORT( webConfigChildProcessPathSet, "_Awe_WebConfig_child_process_path_set@8" );
	CL_AWE_IMPORT( webConfigLogPathSet, "_Awe_WebConfig_log_path_set@8" );
	CL_AWE_IMPORT( webConfigPackagePathSet, "_Awe_WebConfig_package_path_set@8" );
	CL_AWE_IMPORT( webConfigUserAgentSet, "_Awe_WebConfig_user_agent_set@8" );
	CL_AWE_IMPORT( webConfigUserScriptSet, "_Awe_WebConfig_user_script_set@8" );
	CL_AWE_IMPORT( webPrefsEnableJavascriptSet, "_Awe_WebPreferences_enable_javascript_set@8" );
	CL_AWE_IMPORT( webPrefsEnableLocalStorageSet, "_Awe_WebPreferences_enable_local_storage_set@8" );
	CL_AWE_IMPORT( webPrefsEnableDatabasesSet, "_Awe_WebPreferences_enable_databases_set@8" );
	CL_AWE_IMPORT( webPrefsEnableWebSecuritySet, "_Awe_WebPreferences_enable_web_security_set@8" );
	CL_AWE_IMPORT( webPrefsAllowFileAccessSet, "_Awe_WebPreferences_allow_file_access_from_file_url_set@8" );
	CL_AWE_IMPORT( webPrefsAllowUniversalAccessSet, "_Awe_WebPreferences_allow_universal_access_from_file_url_set@8" );
	CL_AWE_IMPORT( newDataPakSource, "_Awe_new_DataPakSource@4" );
	CL_AWE_IMPORT( deleteDataPakSource, "_Awe_delete_DataPakSource@4" );
	CL_AWE_IMPORT( newWebURL, "_Awe_new_WebURL_1@4" );
	CL_AWE_IMPORT( deleteWebURL, "_Awe_delete_WebURL@4" );
	CL_AWE_IMPORT( webSessionAddDataSource, "_Awe_WebSession_AddDataSource@12" );
	CL_AWE_IMPORT( webSessionRelease, "_Awe_WebSession_Release@4" );
	CL_AWE_IMPORT( webViewDestroy, "_Awe_WebView_Destroy@4" );
	CL_AWE_IMPORT( webViewLoadURL, "_Awe_WebView_LoadURL@8" );
	CL_AWE_IMPORT( webViewExecuteJavascript, "_Awe_WebView_ExecuteJavascript@12" );
	CL_AWE_IMPORT( webViewResize, "_Awe_WebView_Resize@12" );
	CL_AWE_IMPORT( webViewFocus, "_Awe_WebView_Focus@4" );
	CL_AWE_IMPORT( webViewResumeRendering, "_Awe_WebView_ResumeRendering@4" );
	CL_AWE_IMPORT( webViewReload, "_Awe_WebView_Reload@8" );
	CL_AWE_IMPORT( webViewStop, "_Awe_WebView_Stop@4" );
	CL_AWE_IMPORT( webViewInjectMouseMove, "_Awe_WebView_InjectMouseMove@12" );
	CL_AWE_IMPORT( webViewInjectMouseDown, "_Awe_WebView_InjectMouseDown@8" );
	CL_AWE_IMPORT( webViewInjectMouseUp, "_Awe_WebView_InjectMouseUp@8" );
	CL_AWE_IMPORT( webViewInjectMouseWheel, "_Awe_WebView_InjectMouseWheel@12" );
	CL_AWE_IMPORT( webViewSurface, "_Awe_WebView_surface@4" );
	CL_AWE_IMPORT( bitmapCopyTo, "_Awe_BitmapSurface_CopyTo@24" );
	CL_AWE_IMPORT( bitmapWidth, "_Awe_BitmapSurface_width@4" );
	CL_AWE_IMPORT( bitmapHeight, "_Awe_BitmapSurface_height@4" );
	CL_AWE_IMPORT( bitmapIsDirty, "_Awe_BitmapSurface_is_dirty@4" );
	CL_AWE_IMPORT( bitmapSetIsDirty, "_Awe_BitmapSurface_set_is_dirty@8" );

#undef CL_AWE_IMPORT

	if ( !CL_Awesomium_LoadRetailImports() ) {
		return qfalse;
	}

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
static void CL_Awesomium_BuildUserScript( char *buffer, size_t bufferSize, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh ) {
	char escapedName[256];
	char steamId[64];

	CL_Awesomium_EscapeScriptString( playerName ? playerName : "", escapedName, sizeof( escapedName ) );
	if ( steamIdHigh || steamIdLow ) {
		_snprintf( steamId, sizeof( steamId ), "%u%010u", steamIdHigh, steamIdLow );
	} else {
		strcpy( steamId, "0" );
	}
	steamId[sizeof( steamId ) - 1] = '\0';

	_snprintf(
		buffer,
		bufferSize,
		"(function(){if(window.__qlr_qz_instance_ready){return;}window.__qlr_qz_instance_ready=true;"
		"var noop=function(){return false;};var empty=function(){return [];};"
		"var maps={campgrounds:{id:'campgrounds',name:'Campgrounds',sysname:'campgrounds',gametypes:{0:true}}};"
		"var factories={ffa:{id:'ffa',title:'Free For All',basegt:0,settings:{}}};"
		"var config={cvars:{sv_servertype:'0',net_port:'27960',sv_hostname:'Quake Live Reverse',sv_maxclients:'8'},binds:[]};"
		"var qz={appId:%u,steamId:\"%s\",playerName:\"%s\","
		"SendGameCommand:function(cmd){console.log('qz SendGameCommand: '+cmd);},"
		"WriteTextFile:noop,OpenURL:function(url){document.location.href=url;},"
		"OpenSteamOverlayURL:function(url){console.log('qz OpenSteamOverlayURL: '+url);},"
		"GetClipboardText:function(){return '';},SetClipboardText:noop,"
		"RequestServers:noop,RequestServerDetails:noop,RefreshList:noop,"
		"CreateLobby:noop,LeaveLobby:noop,JoinLobby:noop,SetLobbyServer:noop,"
		"ShowInviteOverlay:noop,SayLobby:noop,RequestUserStats:noop,"
		"ActivateGameOverlayToUser:noop,Invite:noop,GetAllUGC:function(){return [];},"
		"GetNextKeyDown:noop,SetFavoriteServer:noop,"
		"IsPakFilePresent:function(){return true;},IsGameRunning:function(){return false;},"
		"FileExists:function(){return false;},GetCvar:function(name){return config.cvars[(name||'').toLowerCase()]||'';},"
		"SetCvar:function(name,value){config.cvars[(name||'').toLowerCase()]=String(value);},ResetCvar:noop,"
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
		"window.qz_instance=qz;window.main_hook_v2=function(){var f=window.FakeClient&&window.FakeClient.qz_instance;"
		"if(!f){return;}for(var k in qz){if(typeof f[k]==='undefined'){f[k]=qz[k];}}};})();",
		appId,
		steamId,
		escapedName
	);
	buffer[bufferSize - 1] = '\0';
}

/*
=============
CL_Awesomium_PrepareConfig
=============
*/
static qboolean CL_Awesomium_PrepareConfig( const char *runtimePath, const char *basePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh ) {
	char childProcessPath[MAX_PATH];
	char logPath[MAX_PATH];
	char packagePath[MAX_PATH];
	char packageRoot[MAX_PATH];
	char userScript[8192];
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
	CL_Awesomium_BuildUserScript( userScript, sizeof( userScript ), playerName, appId, steamIdLow, steamIdHigh );
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
		|| !CL_Awesomium_SetConfigString( cl_awe.webConfigUserScriptSet, cl_awesomium.webConfig, userScript ) ) {
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
	cl_awe.webPrefsEnableJavascriptSet( cl_awesomium.webPreferences, true );
	cl_awe.webPrefsEnableLocalStorageSet( cl_awesomium.webPreferences, true );
	cl_awe.webPrefsEnableDatabasesSet( cl_awesomium.webPreferences, true );
	cl_awe.webPrefsEnableWebSecuritySet( cl_awesomium.webPreferences, false );
	cl_awe.webPrefsAllowFileAccessSet( cl_awesomium.webPreferences, true );
	cl_awe.webPrefsAllowUniversalAccessSet( cl_awesomium.webPreferences, true );
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

	pakName = CL_Awesomium_AllocWideString( CL_Awesomium_FileExists( "web.pak" ) ? "web.pak" : pakPath );
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
extern "C" qboolean CL_Awesomium_Startup( const char *runtimePath, const char *basePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh, int width, int height ) {
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

	if ( !CL_Awesomium_PrepareConfig( runtimePath, basePath, playerName, appId, steamIdLow, steamIdHigh )
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
	cl_awe.webViewResumeRendering( cl_awesomium.webView );
	cl_awe.webViewFocus( cl_awesomium.webView );
	cl_awe.deleteWebURL( webURL );
	cl_awesomium.urlLoaded = qtrue;
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
CL_Awesomium_Update
=============
*/
extern "C" void CL_Awesomium_Update( void ) {
	if ( cl_awesomium.started && cl_awesomium.webCore ) {
		cl_awe.webCoreUpdate( cl_awesomium.webCore );
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
CL_Awesomium_CopySurface
=============
*/
extern "C" qboolean CL_Awesomium_CopySurface( byte *destination, int width, int height, int rowSpan ) {
	void *surface;
	int byteCount;

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

	cl_awe.bitmapCopyTo( surface, destination, rowSpan, 4, true, false );
	cl_awe.bitmapSetIsDirty( surface, false );
	return qtrue;
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
extern "C" qboolean CL_Awesomium_Startup( const char *runtimePath, const char *basePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh, int width, int height ) {
	(void)runtimePath;
	(void)basePath;
	(void)playerName;
	(void)appId;
	(void)steamIdLow;
	(void)steamIdHigh;
	(void)width;
	(void)height;
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
CL_Awesomium_Stop
=============
*/
extern "C" void CL_Awesomium_Stop( void ) {
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
