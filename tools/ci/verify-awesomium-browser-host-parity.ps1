[CmdletBinding()]
param(
	[string]$RepoRoot
)

$ErrorActionPreference = 'Stop'

$scriptRoot = $PSScriptRoot
if (-not $scriptRoot) {
	$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}

if (-not $RepoRoot) {
	$RepoRoot = (Resolve-Path (Join-Path $scriptRoot '../..')).Path
}

function Get-RepoFileText {
	param(
		[string]$RelativePath
	)

	$path = Join-Path $RepoRoot $RelativePath
	if (-not (Test-Path $path)) {
		throw "Required file not found: $RelativePath"
	}

	return Get-Content -LiteralPath $path -Raw
}

function Assert-FileContainsLiteral {
	param(
		[string]$RelativePath,
		[string]$Literal,
		[string]$Description
	)

	$content = Get-RepoFileText -RelativePath $RelativePath
	if (-not $content.Contains($Literal)) {
		throw "Expected $Description in ${RelativePath}: $Literal"
	}

	Write-Host "Verified ${RelativePath}: $Description"
}

function Assert-FileContainsRegex {
	param(
		[string]$RelativePath,
		[string]$Pattern,
		[string]$Description
	)

	$content = Get-RepoFileText -RelativePath $RelativePath
	if ($content -notmatch $Pattern) {
		throw "Expected $Description in ${RelativePath}: $Pattern"
	}

	Write-Host "Verified ${RelativePath}: $Description"
}

$sourceAnchors = @(
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = '#define QL_WEB_BRIDGE_RETAIL_OBJECT_ADDRESS 0x012D2670u'
		Description = 'retail data_12d2670 bridge object address'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'typedef struct ql_web_bridge_s ql_web_bridge_t;'
		Description = 'source-visible browser bridge owner type'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'static const clWebListenerCallbackMapping_t cl_webListenerCallbackMappings[] = {'
		Description = 'source-visible Awesomium listener vtable mapping table'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = '{ "QLDialogHandler", "OnShowFileChooser", 0x00547FA8u, 0x08u, 0x00431640u, "QLDialogHandler_OnShowFileChooser", CL_WEB_LISTENER_SCOPE_BUILTIN_FORWARD },'
		Description = 'dialog file-chooser listener mapping'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'static qboolean QLDialogHandler_OnShowFileChooser( void ) {'
		Description = 'dialog file-chooser source callback stub'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'cl_webHost.listenerCallbackMappingCount = QLWebHost_CountRecoveredListenerMappings();'
		Description = 'listener mapping count recorded during listener installation'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = '#define CL_WEB_QZ_METHOD_TABLE_RETAIL_BEGIN 0x0055C008u'
		Description = 'retail qz_instance method table start address'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = '#define CL_WEB_QZ_METHOD_TABLE_RETAIL_END 0x0055C1A0u'
		Description = 'retail qz_instance method table end address'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'unsigned int	retailTableAddress;'
		Description = 'source-visible qz method table address field'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = '{ "SetCvar", 0x0055C044u, CL_WEB_METHOD_SET_CVAR, qtrue },'
		Description = 'SetCvar preserved as return-valued qz method'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = '{ "ResetCvar", 0x0055C050u, CL_WEB_METHOD_RESET_CVAR, qtrue },'
		Description = 'ResetCvar preserved as return-valued qz method'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'Cvar_Set( arguments[0], arguments[1] ? arguments[1] : "" );'
		Description = 'return-valued SetCvar handler implementation'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'Cvar_Reset( arguments[0] );'
		Description = 'return-valued ResetCvar handler implementation'
	},
	@{
		Path = 'src/code/cgame/cg_public.h'
		Literal = 'CG_QL_IMPORT_PUBLISH_TAGGED_INFO_STRING = 116,'
		Description = 'native cgame tagged info-string import slot'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'static void QDECL QL_CG_trap_PublishTaggedInfoString( const char *messageType, const char *infoString ) {'
		Description = 'native cgame tagged info-string host shim'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'ql_cgame_imports[CG_QL_IMPORT_PUBLISH_TAGGED_INFO_STRING] = (ql_import_f)QL_CG_trap_PublishTaggedInfoString;'
		Description = 'native cgame tagged info-string slot wiring'
	},
	@{
		Path = 'src/code/client/client.h'
		Literal = 'void CL_WebView_InvokeCommNotice( const char *message );'
		Description = 'retail one-argument comm-notice bridge declaration'
	},
	@{
		Path = 'src/code/client/cl_main.c'
		Literal = 'void CL_WebView_PublishTaggedInfoString( const char *messageType, const char *infoString ) {'
		Description = 'tagged info-string browser publisher'
	},
	@{
		Path = 'src/code/client/cl_main.c'
		Literal = 'Info_NextPair( &cursor, key, value );'
		Description = 'tagged info-string parser loop'
	},
	@{
		Path = 'src/code/client/cl_main.c'
		Literal = 'CL_WebView_InvokeCommNotice( payload );'
		Description = 'tagged info-string comm-notice handoff'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = 'static qboolean QLResourceInterceptor_OnFilterNavigation( const char *url ) {'
		Description = 'retail resource-interceptor navigation filter'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = '#define QL_RESOURCE_INTERCEPTOR_HOST "ql"'
		Description = 'retail resource-interceptor ql host literal'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = '#define QL_RESOURCE_INTERCEPTOR_SCREENSHOT_PATH "/screenshot"'
		Description = 'retail resource-interceptor screenshot path literal'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = 'static qboolean QLResourceInterceptor_RequestRetailHost( const char *url, clSteamDataSourceResponse_t *response ) {'
		Description = 'retail ql host compatibility projection'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = 'QLResourceInterceptor_RequestRetailHost( url, response )'
		Description = 'resource-interceptor ql host branch before generic fallback'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = 'static const clSteamDataSourceRetailMapping_t cl_steamDataSourceRetailMappings[] = {'
		Description = 'source-visible SteamDataSource retail wiring table'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = '{ "SteamDataSource", "OnRequest", 0x00532B80u, 0x04u, 0x004640C0u, "CL_SteamDataSource_Request", CL_STEAM_DATA_SOURCE_SCOPE_COMPATIBILITY_OWNER },'
		Description = 'SteamDataSource OnRequest vtable slot mapping'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = '{ "CCallback<class SteamDataSource, struct AvatarImageLoaded_t, 0>", "callback target", 0x00532B68u, 0x10u, 0x00464290u, "CL_SteamResources_OnAvatarImageLoaded", CL_STEAM_DATA_SOURCE_SCOPE_AVATAR_CALLBACK },'
		Description = 'SteamDataSource AvatarImageLoaded callback target mapping'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = 'static int CL_CountSteamDataSourceRetailMappings( void ) {'
		Description = 'SteamDataSource recovered mapping counter'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = 'Cvar_Set( "ui_resourceBridgeSteamDataSourceMappings", va( "%i", CL_CountSteamDataSourceRetailMappings() ) );'
		Description = 'SteamDataSource mapping count diagnostic cvar'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = '#define CL_STEAM_RESPONSE_THREAD_RETAIL_VTABLE 0x00532B44u'
		Description = 'retail ResponseThread vtable address'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = 'static const clSteamResponseThreadRetailMapping_t cl_steamResponseThreadRetailMappings[] = {'
		Description = 'source-visible ResponseThread retail wiring table'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = '{ "ResponseThread", "run", CL_STEAM_RESPONSE_THREAD_RETAIL_VTABLE, 0x04u, 0x00463440u, CL_STEAM_RESPONSE_THREAD_MIME_TYPE, "CL_SteamResources_RequestAvatarRGBA", CL_STEAM_RESPONSE_THREAD_SCOPE_ASYNC_BOUNDARY },'
		Description = 'ResponseThread run vtable slot mapping'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = '{ "ResponseThread", "EncodeAvatarPNG", 0u, 0u, 0x00463180u, CL_STEAM_RESPONSE_THREAD_PNG_VERSION, "CL_SteamResources_RequestAvatarRGBA", CL_STEAM_RESPONSE_THREAD_SCOPE_PNG_HELPER },'
		Description = 'ResponseThread PNG encoder mapping'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = '{ "Awesomium::DataSource", "SendResponse import", 0u, 0u, 0x0052C6B0u, CL_STEAM_RESPONSE_THREAD_MIME_TYPE, "QLResourceInterceptor_OnRequest", CL_STEAM_RESPONSE_THREAD_SCOPE_SEND_RESPONSE },'
		Description = 'Awesomium DataSource SendResponse boundary mapping'
	},
	@{
		Path = 'src/code/client/cl_steam_resources.c'
		Literal = 'Cvar_Set( "ui_resourceBridgeResponseThreadMappings", va( "%i", CL_CountSteamResponseThreadRetailMappings() ) );'
		Description = 'ResponseThread mapping count diagnostic cvar'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'QL_WEB_BRIDGE_SLOT_SET_ACTIVE_ADVERT = 0x08'
		Description = 'retail bridge slot 0x08'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'QL_WEB_BRIDGE_SLOT_ACTIVATE_ADVERT = 0x68'
		Description = 'retail bridge final recovered slot'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( setActiveAdvert, QL_WEB_BRIDGE_SLOT_SET_ACTIVE_ADVERT );'
		Description = 'x86 bridge vtable offset assertion'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = '#define QL_WEB_KEYBOARD_EVENT_ACTIVATION_TYPE 0u'
		Description = 'retail activation keyboard event type'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = '#define QL_WEB_KEYBOARD_EVENT_ACTIVATION_VIRTUAL_KEY 0x11u'
		Description = 'retail activation keyboard virtual key'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = '#define QL_WEB_KEYBOARD_EVENT_ACTIVATION_NATIVE_KEY 0x1d0001L'
		Description = 'retail activation keyboard native key'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'static void QLWebView_InjectActivationKeyboardEvent( void ) {'
		Description = 'activation injection helper'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'qboolean CL_AdvertisementBridge_IsDelayElapsed( void ) {'
		Description = 'advertisement bridge delay predicate'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'cl_advertisementBridge.delayDeadline = 0;'
		Description = 'advertisement bridge delay clear'
	},
	@{
		Path = 'src/code/client/cl_input.c'
		Literal = 'if ( !CL_AdvertisementBridge_IsDelayElapsed() ) {'
		Description = 'CL_MouseEvent advertisement-delay gate'
	},
	@{
		Path = 'src/code/client/client.h'
		Literal = '#define KEYCATCH_BROWSER'
		Description = 'retail browser key catcher bit'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'if ( cl_webHost.browserActive && !( cls.keyCatchers & KEYCATCH_BROWSER ) ) {'
		Description = 'retail browser-active keycatcher arm without surface gate'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'Cvar_Set( "web_browserActive", cl_webHost.browserActive ? "1" : "0" );'
		Description = 'retail browser-active cvar publish without surface gate'
	},
	@{
		Path = 'src/code/client/cl_keys.c'
		Literal = 'CL_WebView_OnKeyEvent( key, down );'
		Description = 'browser keyboard route'
	},
	@{
		Path = 'src/code/win32/win_wndproc.c'
		Literal = 'CL_WebHost_NotifyAppActivation( qtrue );'
		Description = 'Win32 activation callback'
	},
	@{
		Path = 'src/code/win32/win_wndproc.c'
		Literal = 'browserCursor = (HCURSOR)CL_WebHost_GetCursorHandle();'
		Description = 'Win32 browser cursor override'
	},
	@{
		Path = 'src/code/null/null_client.c'
		Literal = '#define CL_NULL_BROWSER_PARITY_SCOPE_LABEL "strict-retail-excluded"'
		Description = 'null-host strict retail exclusion label'
	},
	@{
		Path = 'src/code/null/null_client.c'
		Literal = 'Cvar_Set( "ui_advertisementBridgeParityReason", CL_NULL_BROWSER_PARITY_REASON_LABEL );'
		Description = 'null-host advert parity reason cvar'
	}
)

foreach ($anchor in $sourceAnchors) {
	Assert-FileContainsLiteral -RelativePath $anchor.Path -Literal $anchor.Literal -Description $anchor.Description
}

$adapterAnchors = @(
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = 'static const clAwesomiumRetailAbiEquivalence_t cl_aweRetailAbiEquivalence[] = {'
		Description = 'retail ABI equivalence table'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = 'static const clAwesomiumBootstrapRetailMapping_t cl_aweBootstrapRetailMappings[] = {'
		Description = 'retail bootstrap lifecycle mapping table'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = '{ 0x004F2D30u, 0x0052C6A4u, "WebConfig::WebConfig", "CL_Awesomium_PrepareConfig", "_Awe_new_WebConfig@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },'
		Description = 'WebConfig constructor bootstrap substitution'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = '{ 0x004F2D30u, 0x0052C6A0u, "WebCore::Initialize", "CL_Awesomium_Startup", "_Awe_WebCore_Initialize@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },'
		Description = 'WebCore initialize bootstrap substitution'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = '{ 0x004F2D30u, 0x00000000u, "WebCore::CreateWebSession slot 0x00", "CL_Awesomium_CreateSession", "_Awe_WebCore_CreateWebSession@12", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },'
		Description = 'WebCore create-session bootstrap substitution'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = '{ 0x004F2D30u, 0x00000018u, "WebSession bootstrap slot 0x18", "CL_Awesomium_CreateSession", "_Awe_WebSession_Initialize@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },'
		Description = 'WebSession bootstrap initialize substitution'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = '{ 0x004F2D30u, 0x00000010u, "WebSession::AddDataSource slot 0x10", "CL_Awesomium_CreateSession", "_Awe_WebSession_AddDataSource@12", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },'
		Description = 'WebSession AddDataSource bootstrap substitution'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = '{ 0x004F2A10u, 0x0000001Cu, "WebSession::ClearCache slot 0x1C", "CL_Awesomium_ClearCache", "_Awe_WebSession_Release@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },'
		Description = 'WebSession cache-clear command substitution'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = '{ 0x004F2D30u, 0x00548068u, "QL data-source name", "CL_Awesomium_CreateSession", "\"QL\"", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_SOURCE_LITERAL },'
		Description = 'retail QL data-source literal'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = '{ 0x004F2D30u, 0x00000064u, "WebView::LoadURL slot 0x64", "CL_Awesomium_OpenURL", "_Awe_WebView_LoadURL@8", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },'
		Description = 'WebView LoadURL bootstrap substitution'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = '{ 0x004F2A60u, 0x0052C684u, "WebCore::Shutdown", "CL_Awesomium_Shutdown", "_Awe_WebCore_Shutdown@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },'
		Description = 'WebCore shutdown bootstrap substitution'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = '{ 0x004F2590u, 0x18u, "WebCore::Update", "CL_Awesomium_Update", "_Awe_WebCore_Update@4", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },'
		Description = 'WebCore::Update vtable slot substitution'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = '{ 0x004F2750u, 0xd0u, "WebView::InjectMouseMove", "CL_Awesomium_InjectMouseMove", "_Awe_WebView_InjectMouseMove@12", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },'
		Description = 'WebView mouse-move vtable slot substitution'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = '{ 0x004F28A0u, 0xe0u, "WebView::InjectKeyboardEvent", "CL_Awesomium_InjectKeyboardEvent", "_Awe_WebView_InjectKeyboardEvent@16", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },'
		Description = 'WebView keyboard event adapter import substitution'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = 'cl_awesomium.module = CL_Awesomium_LoadLibraryCandidate( "awesomium.dll", loadError, sizeof( loadError ) );'
		Description = 'Awesomium DLL dynamic load from process directory'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = 'CL_AWE_IMPORT( webCoreUpdate, "_Awe_WebCore_Update@4" );'
		Description = 'WebCore update adapter import'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = 'CL_AWE_IMPORT( webViewInjectMouseWheel, "_Awe_WebView_InjectMouseWheel@12" );'
		Description = 'WebView wheel adapter import'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = 'cl_awe.webSessionInitialize = reinterpret_cast<awe_websession_void_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_WebSession_Initialize@4" ) );'
		Description = 'optional WebSession initialize adapter import'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = 'CL_AWE_IMPORT( webSessionClearCache, "_Awe_WebSession_Release@4" );'
		Description = 'WebSession cache-clear adapter import'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = 'cl_awe.webSessionInitialize( cl_awesomium.webSession );'
		Description = 'WebSession initialize after create'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = 'extern "C" void CL_Awesomium_ClearCache( void ) {'
		Description = 'live WebSession cache-clear API'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = 'CL_AWE_IMPORT( bitmapCopyTo, "_Awe_BitmapSurface_CopyTo@24" );'
		Description = 'Bitmap surface copy adapter import'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = 'CL_AWE_IMPORT( webConfigChildProcessPathSet, "_Awe_WebConfig_child_process_path_set@8" );'
		Description = 'WebConfig child-process path adapter import'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = 'cl_awesomium.bootstrapMappingCount = CL_Awesomium_CountBootstrapRetailMappings();'
		Description = 'bootstrap mapping count recorded during import resolution'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = 'CL_Awesomium_AppendPath( childProcessPath, sizeof( childProcessPath ), assetsPath, "awesomium_process.exe" );'
		Description = 'Awesomium child process path configured from selected asset root'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = 'CL_Awesomium_BuildUserScript( cl_awesomium.startupScript, sizeof( cl_awesomium.startupScript ), playerName, appId, steamIdLow, steamIdHigh );'
		Description = 'WebConfig user-script bootstrap projection'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = "SetCvar:function(name,value){config.cvars[(name||'').toLowerCase()]=String(value);return true;}"
		Description = 'startup qz_instance SetCvar return-valued projection'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = "ResetCvar:function(name){delete config.cvars[(name||'').toLowerCase()];return true;}"
		Description = 'startup qz_instance ResetCvar return-valued projection'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = '!CL_Awesomium_SetConfigString( cl_awe.webConfigPackagePathSet, cl_awesomium.webConfig, packageRoot )'
		Description = 'Awesomium package path configured on WebConfig'
	},
	@{
		Path = 'src/code/client/cl_awesomium_win32.cpp'
		Literal = 'pakName = CL_Awesomium_AllocWideString( "web.pak" );'
		Description = 'retail web.pak DataPakSource literal'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'if ( !cl_webHost.surfaceShader || cl_webHost.surfaceDirty ) {'
		Description = 'browser draw uploads on shader absence or dirty surface'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'cl_webHost.surfaceHasVisiblePixels = visible;'
		Description = 'browser surface visibility kept diagnostic rather than draw-gating'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'CL_Awesomium_ClearCache();'
		Description = 'clear-cache command reaches live Awesomium session cache'
	},
	@{
		Path = 'src/code/client/cl_cgame.c'
		Literal = 'const char *message = ( Cmd_Argc() > 1 ) ? Cmd_ArgsFrom( 1 ) : "";'
		Description = 'web_showError consumes full command tail'
	}
)

foreach ($anchor in $adapterAnchors) {
	Assert-FileContainsLiteral -RelativePath $anchor.Path -Literal $anchor.Literal -Description $anchor.Description
}

$aliasAnchors = @(
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_434600": "QLResourceInterceptor_OnFilterNavigation"'
		Description = 'resource-interceptor navigation filter alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_434620": "QLResourceInterceptor_OnRequest"'
		Description = 'resource-interceptor request alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_4640C0": "SteamDataSource_OnRequest"'
		Description = 'SteamDataSource request alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_464290": "SteamDataSource_OnAvatarImageLoaded"'
		Description = 'SteamDataSource avatar callback alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_464300": "SteamDataSource_Init"'
		Description = 'SteamDataSource init alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_464440": "SteamDataSource_Shutdown"'
		Description = 'SteamDataSource shutdown alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_464510": "SteamDataSource_Destroy"'
		Description = 'SteamDataSource destroy alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_463110": "ResponseThread_PNGWriteCallback"'
		Description = 'ResponseThread PNG write callback alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_463180": "ResponseThread_EncodeAvatarPNG"'
		Description = 'ResponseThread PNG encoder alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_463440": "ResponseThread_Run"'
		Description = 'ResponseThread run alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_463550": "SteamDataSource_StartResponseThread"'
		Description = 'SteamDataSource response-thread starter alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_431640": "QLDialogHandler_OnShowFileChooser"'
		Description = 'dialog file-chooser listener alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_4B03B0": "QLCGImport_PublishTaggedInfoString"'
		Description = 'native cgame tagged info-string import alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_4BF5D0": "QLWebView_PublishTaggedInfoString"'
		Description = 'tagged info-string publisher alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_4EC6D0": "QLWebView_InvokeCommNoticeThunk"'
		Description = 'comm-notice tail thunk alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_4F2950": "QLWebView_InvokeCommNotice"'
		Description = 'comm-notice invoker alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_4F22E0": "AdvertisementBridge_IsDelayElapsed"'
		Description = 'advertisement delay alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_4F2590": "QLWebCore_Update"'
		Description = 'WebCore update alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_4F2750": "QLWebView_InjectMouseMove"'
		Description = 'mouse move injection alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_4F2900": "QLWebView_InjectActivationKeyboardEvent"'
		Description = 'activation keyboard helper alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_4F2A60": "QLWebHost_Shutdown"'
		Description = 'Awesomium web-host shutdown alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_4F2D30": "QLWebHost_OpenURL"'
		Description = 'Awesomium web-host bootstrap/open-url alias'
	},
	@{
		Path = 'references/analysis/quakelive_symbol_aliases.json'
		Literal = '"sub_4B54E0": "CL_MouseEvent"'
		Description = 'mouse event dispatcher alias'
	}
)

foreach ($anchor in $aliasAnchors) {
	Assert-FileContainsLiteral -RelativePath $anchor.Path -Literal $anchor.Literal -Description $anchor.Description
}

$mappingAnchors = @(
	@{
		Path = 'docs/reverse-engineering/quakelive_steam_mapping_round_94.md'
		Pattern = '0x004F2750.+QLWebView_InjectMouseMove.+\+0xd0'
		Description = 'round 94 mouse-move vtable slot evidence'
	},
	@{
		Path = 'docs/reverse-engineering/quakelive_steam_mapping_round_96.md'
		Pattern = '0x004F2590.+QLWebCore_Update'
		Description = 'round 96 WebCore update evidence'
	},
	@{
		Path = 'docs/reverse-engineering/quakelive_steam_mapping_round_257.md'
		Pattern = '(?s)CL_MouseEvent.+AdvertisementBridge_IsDelayElapsed'
		Description = 'round 257 mouse delay-gate evidence'
	},
	@{
		Path = 'docs/reverse-engineering/quakelive_steam_mapping_round_286.md'
		Pattern = '(?s)QLWebView_PublishTaggedInfoString.+Info_NextPair.+OnCommNotice'
		Description = 'round 286 tagged info-string source reconstruction evidence'
	},
	@{
		Path = 'docs/reverse-engineering/quakelive_steam_mapping_round_287.md'
		Pattern = '(?s)QLResourceInterceptor_OnFilterNavigation.+QLResourceInterceptor_OnRequest.+/screenshot'
		Description = 'round 287 resource-interceptor host/filter evidence'
	},
	@{
		Path = 'docs/reverse-engineering/quakelive_steam_mapping_round_288.md'
		Pattern = '(?s)QLDialogHandler.+OnShowFileChooser.+0x00431640'
		Description = 'round 288 listener vtable source reconstruction evidence'
	},
	@{
		Path = 'docs/reverse-engineering/quakelive_steam_mapping_round_289.md'
		Pattern = '(?s)SteamDataSource::vftable.+0x00532B80.+SteamDataSource.+OnRequest.+0x004640C0'
		Description = 'round 289 SteamDataSource source-visible wiring evidence'
	},
	@{
		Path = 'docs/reverse-engineering/quakelive_steam_mapping_round_54.md'
		Pattern = '(?s)ResponseThread::vftable.+0x00532B44.+image/png.+request_%i'
		Description = 'round 54 ResponseThread async response source-visible wiring evidence'
	},
	@{
		Path = 'docs/reverse-engineering/quakelive_steam_mapping_round_291.md'
		Pattern = '(?s)WebCore::Initialize.+WebSession::AddDataSource.+WebView::LoadURL.+WebCore::Shutdown'
		Description = 'round 291 Awesomium bootstrap lifecycle source-visible wiring evidence'
	},
	@{
		Path = 'docs/reverse-engineering/quakelive_steam_mapping_round_331.md'
		Pattern = '(?s)data_55c008.+SetCustomMethod.+SetCvar.+0x0055C044.+ResetCvar.+0x0055C050.+NoOp.+0x0055C194'
		Description = 'round 331 qz method table return-flag evidence'
	},
	@{
		Path = 'docs/reverse-engineering/quakelive_steam_mapping_round_285.md'
		Pattern = 'WebKeyboardEvent\(0, 0x11, 0x1d0001\)'
		Description = 'round 285 activation keyboard-event evidence'
	}
)

foreach ($anchor in $mappingAnchors) {
	Assert-FileContainsRegex -RelativePath $anchor.Path -Pattern $anchor.Pattern -Description $anchor.Description
}

Write-Host 'Awesomium browser host source, alias, mapping, and adapter parity anchors are present.'
