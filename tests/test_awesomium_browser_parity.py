from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CL_AWESOMIUM_WIN32_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_awesomium_win32.cpp"
AWESOMIUM_PROCESS_CPP_PATH = REPO_ROOT / "src" / "code" / "win32" / "awesomium_process.cpp"
AWESOMIUM_PROCESS_RC_PATH = REPO_ROOT / "src" / "code" / "win32" / "awesomium_process.rc"
AWESOMIUM_DEF_PATH = REPO_ROOT / "src" / "code" / "win32" / "awesomium.def"
AWESOMIUM_PROCESS_VCXPROJ_PATH = REPO_ROOT / "src" / "code" / "awesomium_process.vcxproj"
QUAKELIVE_STEAM_VCXPROJ_PATH = REPO_ROOT / "src" / "code" / "quakelive_steam.vcxproj"
CL_CGAME_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
CL_STEAM_RESOURCES_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_steam_resources.c"
CG_PUBLIC_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_public.h"
CG_SYSCALLS_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_syscalls.c"
CL_INPUT_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_input.c"
CL_KEYS_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_keys.c"
CL_MAIN_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_main.c"
CLIENT_H_PATH = REPO_ROOT / "src" / "code" / "client" / "client.h"
NULL_CLIENT_PATH = REPO_ROOT / "src" / "code" / "null" / "null_client.c"
WIN_WNDPROC_PATH = REPO_ROOT / "src" / "code" / "win32" / "win_wndproc.c"
AWESOMIUM_PLAN_PATH = REPO_ROOT / "docs" / "plans" / "awesomium-parity-plan.md"
AWESOMIUM_BROWSER_HOST_VERIFY_PATH = REPO_ROOT / "tools" / "ci" / "verify-awesomium-browser-host-parity.ps1"
FUNCTION_PARITY_GAP_AUDIT_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "function-parity-gap-audit-2026-04-24.md"
)
NULL_CLIENT_GAP_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "source-file-gap-notes" / "rw-g02-null-client.md"
)


def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(text)):
		char = text[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def test_awesomium_hash_navigation_normalizes_leading_hash_tokens() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)

	normalize_block = _extract_function_block(
		cl_cgame, "static void CL_WebHost_NormalizeHash( const char *hash, char *buffer, size_t bufferSize ) {"
	)
	build_url_block = _extract_function_block(
		cl_cgame, "static void CL_WebHost_BuildCurrentURL( const char *hash, char *buffer, size_t bufferSize ) {"
	)
	show_browser_block = _extract_function_block(cl_cgame, "void CL_Web_ShowBrowser_f( void ) {")
	change_hash_block = _extract_function_block(cl_cgame, "void CL_Web_ChangeHash_f( void ) {")
	set_hash_block = _extract_function_block(cl_cgame, "static qboolean QLWebView_SetLocationHash( const char *hash ) {")

	assert "while ( *cursor == '#'" in normalize_block
	assert "CL_WebHost_NormalizeHash( hash, normalizedHash, sizeof( normalizedHash ) );" in build_url_block
	assert "Com_sprintf( buffer, bufferSize, \"%s#%s\", CL_WEB_DEFAULT_URL, normalizedHash );" in build_url_block
	assert "CL_WebHost_NormalizeHash( hash, cl_webBrowserHash, sizeof( cl_webBrowserHash ) );" in show_browser_block
	assert "CL_WebHost_NormalizeHash( hash, cl_webBrowserHash, sizeof( cl_webBrowserHash ) );" in change_hash_block
	assert "CL_WebHost_NormalizeHash( hash, cl_webHost.pendingHash, sizeof( cl_webHost.pendingHash ) );" in set_hash_block
	assert "CL_Awesomium_ExecuteJavascript( script, \"\" )" in set_hash_block
	assert "return qtrue;" in set_hash_block


def test_awesomium_view_callbacks_reconstruct_tooltip_and_console_contracts() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_main = _read_text(CL_MAIN_PATH)

	tooltip_block = _extract_function_block(
		cl_cgame, "static void QLViewHandler_OnChangeTooltip( const char *tooltip ) {"
	)
	console_block = _extract_function_block(
		cl_cgame, "static void QLViewHandler_OnAddConsoleMessage( const char *source, int line, const char *message ) {"
	)
	hide_browser_block = _extract_function_block(cl_cgame, "static void QLWebHost_HideBrowser( void ) {")
	register_block = _extract_function_block(cl_cgame, "void QLWebHost_RegisterCommands( void ) {")

	assert 'Cvar_Get ("web_console", "0", CVAR_ARCHIVE );' not in cl_main
	assert 'cl_webConsole = Cvar_Get ("web_console", "0", CVAR_ARCHIVE );' in register_block
	assert 'Q_strncpyz( cl_webHost.tooltip, tooltip ? tooltip : "", sizeof( cl_webHost.tooltip ) );' in tooltip_block
	assert 'Com_sprintf( payload, sizeof( payload ), "{\\"tooltip\\":\\"%s\\"}", escapedTooltip );' in tooltip_block
	assert 'CL_WebView_PublishEvent( "web.tooltip", payload );' in tooltip_block
	assert 'if ( !CL_WebCvarIntegerValue( cl_webConsole, "web_console" ) ) {' in console_block
	assert 'Com_Printf( "%s:%i: %s\\n", source ? source : "", line, message ? message : "" );' in console_block
	assert 'QLViewHandler_OnChangeTooltip( "" );' in hide_browser_block


def test_awesomium_web_cvar_reconstruction_keeps_cached_retail_globals() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)
	common = _read_text(REPO_ROOT / "src" / "code" / "qcommon" / "common.c")
	mapping_round = _read_text(REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_333.md")

	register_block = _extract_function_block(cl_cgame, "void QLWebHost_RegisterCommands( void ) {")
	update_block = _extract_function_block(cl_cgame, "static void QLWebCore_Update( void ) {")

	for expected in (
		'static cvar_t *cl_webZoom = NULL;',
		'static cvar_t *cl_webConsole = NULL;',
		'static cvar_t *cl_webBrowserActive = NULL;',
		"static const clWebCvarRetailMapping_t cl_webCvarRetailMappings[] = {",
		'{ "web_zoom", 0x012D3060u, "100", CVAR_ARCHIVE, "Awesomium WebView::SetZoom" },',
		'{ "web_console", 0x012D3064u, "0", CVAR_ARCHIVE, "QLViewHandler::OnAddConsoleMessage" },',
		'{ "web_browserActive", 0x0145CA50u, "0", CVAR_ROM, "browser-active client/renderer/UI state" },',
		"static int QLWebHost_CountRecoveredWebCvarMappings( void )",
	):
		assert expected in cl_cgame

	assert 'cl_webZoom = Cvar_Get ("web_zoom", "100", CVAR_ARCHIVE );' in register_block
	assert 'cl_webConsole = Cvar_Get ("web_console", "0", CVAR_ARCHIVE );' in register_block
	assert 'cl_webBrowserActive = Cvar_Get ("web_browserActive", "0", CVAR_ROM );' in register_block
	assert "cl_webHost.cvarMappingCount = QLWebHost_CountRecoveredWebCvarMappings();" in register_block
	assert "CL_WebZoomIntegerValue();" in update_block
	assert "cl_webZoom->modified" in update_block
	assert "CL_WebZoomClearModified();" in update_block

	assert 'cvar_t\t*com_webBrowserActive;' in common
	assert 'com_webBrowserActive = Cvar_Get( "web_browserActive", "0", CVAR_ROM );' in common
	assert '( com_webBrowserActive && com_webBrowserActive->integer == 1 ) || ( com_idleSleep && com_idleSleep->integer == 1 )' in common

	for expected in (
		"`web_zoom` | `0x012D3060` | `100` | `CVAR_ARCHIVE`",
		"`web_console` | `0x012D3064` | `0` | `CVAR_ARCHIVE`",
		"`web_browserActive` | `0x0145CA50` | `0` | `CVAR_ROM`",
		"No additional `web_*` cvar names were found",
	):
		assert expected in mapping_round


def test_awesomium_cursor_override_reconstructs_retail_win32_callback_surface() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)
	client_h = _read_text(CLIENT_H_PATH)
	win_wndproc = _read_text(WIN_WNDPROC_PATH)

	load_cursor_block = _extract_function_block(
		cl_cgame, "static HCURSOR CL_WebHost_LoadWin32CursorHandle( int cursorType ) {"
	)
	change_cursor_block = _extract_function_block(
		cl_cgame, "static void *QLViewHandler_OnChangeCursor( int cursorType ) {"
	)
	clear_cursor_block = _extract_function_block(
		cl_cgame, "static void CL_WebHost_ClearCursorOverride( void ) {"
	)
	get_cursor_block = _extract_function_block(
		cl_cgame, "void *CL_WebHost_GetCursorHandle( void ) {"
	)

	assert "void *CL_WebHost_GetCursorHandle( void );" in client_h
	assert "cursorId = IDC_ARROW;" in load_cursor_block
	assert "cursorId = IDC_HAND;" in load_cursor_block
	assert "cursorId = IDC_IBEAM;" in load_cursor_block
	assert "cursorId = IDC_SIZEWE;" in load_cursor_block
	assert "LoadCursorA( NULL, cursorId );" in load_cursor_block
	assert "cl_webHost.restoreCursorHandle = GetCursor();" in change_cursor_block
	assert "cl_webHost.activeCursorHandle = cursorHandle;" in change_cursor_block
	assert "SetCursor( cl_webHost.activeCursorHandle );" in change_cursor_block
	assert "cl_webHost.cursorOverrideActive = qfalse;" in clear_cursor_block
	assert "return cl_webHost.activeCursorHandle;" in get_cursor_block
	assert "case WM_SETCURSOR:" in win_wndproc
	assert "browserCursor = (HCURSOR)CL_WebHost_GetCursorHandle();" in win_wndproc
	assert "SetCursor( browserCursor );" in win_wndproc
	assert "return TRUE;" in win_wndproc


def test_awesomium_load_failure_hides_host_and_suppresses_error_publish_until_recovered() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)

	fail_block = _extract_function_block(
		cl_cgame, "static void QLLoadHandler_OnFailLoadingFrame( const char *url ) {"
	)
	open_url_block = _extract_function_block(
		cl_cgame, "static qboolean QLWebHost_OpenURL( const char *url ) {"
	)
	show_browser_block = _extract_function_block(cl_cgame, "void CL_Web_ShowBrowser_f( void ) {")
	change_hash_block = _extract_function_block(cl_cgame, "void CL_Web_ChangeHash_f( void ) {")
	navigate_block = _extract_function_block(cl_cgame, "static qboolean QLWebHost_NavigateOrOpen( const char *hash ) {")
	hide_browser_block = _extract_function_block(cl_cgame, "static void QLWebHost_HideBrowser( void ) {")
	update_block = _extract_function_block(cl_cgame, "static void QLWebCore_Update( void ) {")
	ownership_block = _extract_function_block(cl_cgame, "static void CL_WebHost_UpdateOverlayOwnership( void ) {")
	show_error_block = _extract_function_block(cl_cgame, "void CL_Web_ShowError_f( void ) {")
	clear_cache_block = _extract_function_block(cl_cgame, "void CL_Web_ClearCache_f( void ) {")
	clear_session_block = _extract_function_block(cl_cgame, "static void CL_Web_ClearSessionState( void ) {")
	reload_view_block = _extract_function_block(cl_cgame, "static void QLWebHost_ReloadView( qboolean ignoreCache ) {")
	reload_block = _extract_function_block(cl_cgame, "void CL_Web_Reload_f( void ) {")
	frame_block = _extract_function_block(cl_cgame, "void CL_WebHost_Frame( void ) {")

	assert 'cl_webBrowserVisible = qfalse;' in fail_block
	assert 'cl_webHost.browserActive = qfalse;' in fail_block
	assert 'CL_WebHost_ClearCursorOverride();' in fail_block
	assert 'Cvar_Set( "web_browserActive", "0" );' in fail_block
	assert 'Failed to load QUAKE LIVE site...' in fail_block

	assert 'Cvar_Set( "web_browserActive", "1" );' in open_url_block
	assert 'if ( !cl_webHost.coreInitialised || !cl_webHost.viewInitialised || cl_webHost.keyCaptureArmed ) {' in hide_browser_block
	assert 'Cvar_Set( "web_browserActive", "0" );' in hide_browser_block
	assert "cls.keyCatchers &= ~KEYCATCH_BROWSER;" in hide_browser_block
	assert "KEYCATCH_BROWSER" not in update_block
	assert "QLLoadHandler_PollLiveDocumentReady();" in update_block
	assert "ownsOverlay = CL_WebHost_SurfaceReadyForOverlay( qtrue );" in ownership_block
	assert "cls.keyCatchers |= KEYCATCH_BROWSER;" in ownership_block
	assert 'CL_SetCvarIfChanged( "web_browserActive", ownsOverlay ? "1" : "0" );' in ownership_block
	assert "VM_Call( cgvm, CG_EVENT_HANDLING, CGAME_EVENT_CLOSECOMMANDOVERLAY );" in hide_browser_block
	assert "if ( !QLWebView_SetLocationHash( hash ) ) {" in navigate_block
	assert "CL_Awesomium_OpenURL( cl_webHost.currentUrl )" not in navigate_block

	assert 'Cvar_Set( "web_browserActive", cl_webHost.browserActive ? "1" : "0" );' not in show_browser_block
	assert 'Cvar_Set( "web_browserActive", cl_webHost.browserActive ? "1" : "0" );' not in change_hash_block
	assert 'const char *message = ( Cmd_Argc() > 1 ) ? Cmd_ArgsFrom( 1 ) : "";' in show_error_block
	assert "CL_WebView_PublishGameError( message );" in show_error_block
	assert "QLWebHost_NavigateOrOpen( cl_webBrowserHash );" not in show_error_block
	assert 'if ( !cl_webHost.sessionInitialised ) {' in clear_cache_block
	assert "CL_Web_ClearSessionState();" in clear_cache_block
	assert "CL_Awesomium_ClearCache();" in clear_session_block
	assert 'cl_webHost.refreshStopped = qfalse;' in reload_view_block
	assert "(void)ignoreCache;" in reload_view_block
	assert "CL_WebHost_PrimeLauncherDocument( cl_webHost.currentUrl )" in reload_view_block
	assert "QLLoadHandler_OnFailLoadingFrame( cl_webHost.currentUrl );" in reload_view_block
	assert "QLWebHost_ReloadView( qtrue );" in reload_block
	assert 'Cvar_Set( "web_browserActive", cl_webHost.browserActive ? "1" : "0" );' not in reload_block
	assert "CL_WebHost_UpdateOverlayOwnership();" in frame_block


def test_awesomium_menu_runtime_is_torn_down_before_match_loading() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_main = _read_text(CL_MAIN_PATH)

	map_loading_block = _extract_function_block(cl_main, "void CL_MapLoading( void ) {")
	bootstrap_allowed_block = _extract_function_block(cl_cgame, "static qboolean CL_WebHost_ShouldBootstrapMenu( void ) {")
	bootstrap_block = _extract_function_block(cl_cgame, "void CL_WebHost_BootstrapAwesomiumMenu( void ) {")

	assert "CL_WebHost_Shutdown();" in map_loading_block
	assert "return cls.state == CA_DISCONNECTED || cls.state == CA_CINEMATIC;" in bootstrap_allowed_block
	assert "|| !CL_WebHost_ShouldBootstrapMenu()" in bootstrap_block


def test_awesomium_direct_input_helpers_reconstruct_browser_runtime_injection_surface() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_input = _read_text(CL_INPUT_PATH)
	cl_main = _read_text(CL_MAIN_PATH)
	client_h = _read_text(CLIENT_H_PATH)

	next_power_block = _extract_function_block(
		cl_cgame, "static int QLWebView_NextPowerOfTwo( int value ) {"
	)
	map_cursor_block = _extract_function_block(
		cl_cgame, "static int QLWebView_MapCursorCoordinate( int coordinate, int sourceDimension, int targetDimension ) {"
	)
	inject_mapped_mouse_block = _extract_function_block(
		cl_cgame, "static void QLWebView_InjectMappedMouseMove( int x, int y ) {"
	)
	inject_mouse_block = _extract_function_block(
		cl_cgame, "static void QLWebView_InjectMouseMove( int x, int y ) {"
	)
	inject_keyboard_block = _extract_function_block(
		cl_cgame, "static void QLWebView_InjectKeyboardEvent( int key, qboolean down ) {"
	)
	request_cursor_block = _extract_function_block(
		cl_cgame, "static qboolean CL_WebHost_RequestCursorPosition( int *x, int *y ) {"
	)
	on_mouse_block = _extract_function_block(cl_cgame, "void CL_WebView_OnMouseMove( int x, int y ) {")
	on_key_block = _extract_function_block(cl_cgame, "void CL_WebView_OnKeyEvent( int key, qboolean down ) {")
	delay_block = _extract_function_block(cl_cgame, "qboolean CL_AdvertisementBridge_IsDelayElapsed( void ) {")
	clear_delay_block = _extract_function_block(cl_cgame, "void CL_AdvertisementBridge_ClearDelay( void ) {")
	cg_clear_delay_block = _extract_function_block(
		cl_cgame, "static void QDECL QL_CG_trap_AdvertisementBridge_ClearDelay( void ) {"
	)
	mouse_event_block = _extract_function_block(cl_input, "void CL_MouseEvent( int dx, int dy, int time ) {")
	disconnect_block = _extract_function_block(cl_main, "void CL_Disconnect( qboolean showMainMenu ) {")

	assert "void CL_WebView_OnMouseMove( int x, int y );" in client_h
	assert "void CL_Awesomium_ClearCache( void );" in client_h
	assert "qboolean CL_AdvertisementBridge_IsDelayElapsed( void );" in client_h
	assert "void CL_AdvertisementBridge_ClearDelay( void );" in client_h
	assert "#define KEYCATCH_RETAIL_MOUSEPASS\t0x0010" in client_h
	assert "#define KEYCATCH_BROWSER\t\t\t0x0020" in client_h
	assert "if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {" in inject_mouse_block
	assert "for ( result = 1; result < value; result <<= 1 ) {" in next_power_block
	assert "mappedCoordinate = ( (double)clampedCoordinate / (double)sourceDimension ) * (double)targetDimension;" in map_cursor_block
	assert "cursorWidth = cl_webHost.surfaceContentWidth > 0 ? cl_webHost.surfaceContentWidth : cl_webHost.viewWidth;" in inject_mapped_mouse_block
	assert "cursorHeight = cl_webHost.surfaceContentHeight > 0 ? cl_webHost.surfaceContentHeight : cl_webHost.viewHeight;" in inject_mapped_mouse_block
	assert "cl_webHost.cursorX = cursorX;" in inject_mapped_mouse_block
	assert "cl_webHost.cursorY = cursorY;" in inject_mapped_mouse_block
	assert "cl_webHost.cursorPositionValid = qtrue;" in inject_mapped_mouse_block
	assert "QLWebView_InjectMappedMouseMove(" in inject_mouse_block
	assert "QLWebView_MapCursorCoordinate( x, cl_webHost.viewWidth, cl_webHost.surfaceContentWidth )" in inject_mouse_block
	assert "QLWebView_MapCursorCoordinate( y, cl_webHost.viewHeight, cl_webHost.surfaceContentHeight )" in inject_mouse_block
	assert "QLWebView_MapCursorCoordinate( x, cl_webHost.viewWidth, cl_webHost.surfaceWidth )" not in inject_mouse_block
	assert "QLWebView_MapCursorCoordinate( y, cl_webHost.viewHeight, cl_webHost.surfaceHeight )" not in inject_mouse_block
	assert "if ( !down && cl_webHost.keyCaptureArmed ) {" in inject_keyboard_block
	assert "QLWebView_PublishGameKey( key );" in inject_keyboard_block
	assert "cl_webHost.keyCaptureArmed = qfalse;" in inject_keyboard_block
	assert "QLWebView_InjectMouseMove( x, y );" in on_mouse_block
	assert "QLWebView_InjectKeyboardEvent( key, down );" in on_key_block
	assert "if ( cl_webHost.cursorPositionValid && cl_webHost.viewInitialised && ( cl_webHost.browserVisible || cl_webHost.browserActive ) ) {" in request_cursor_block
	assert "int\t\t\tdelayDeadline;" in cl_cgame
	assert "cl_advertisementBridge.delayDeadline = 0;" in clear_delay_block
	assert "if ( cl_advertisementBridge.delayDeadline == 0 ) {" in delay_block
	assert "return cls.realtime > cl_advertisementBridge.delayDeadline ? qtrue : qfalse;" in delay_block
	assert "CL_AdvertisementBridge_ClearDelay();" in cg_clear_delay_block
	assert "if ( !CL_AdvertisementBridge_IsDelayElapsed() ) {" in mouse_event_block
	assert mouse_event_block.index("CL_AdvertisementBridge_IsDelayElapsed()") < mouse_event_block.index("Cvar_VariableIntegerValue")
	assert "CL_AdvertisementBridge_ClearDelay();" in disconnect_block
	assert disconnect_block.index("QL_ClientAuth_CancelSteamTicket();") < disconnect_block.index("CL_AdvertisementBridge_ClearDelay();")
	assert "if ( cls.keyCatchers & KEYCATCH_BROWSER ) {" in mouse_event_block
	assert "CL_WebView_OnMouseMove( dx, dy );" in mouse_event_block
	assert "CL_WebView_OnMouseMove( cursorX, cursorY );" not in mouse_event_block


def test_awesomium_activation_path_reconstructs_retail_modifier_injection_on_app_focus() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)
	client_h = _read_text(CLIENT_H_PATH)
	win_wndproc = _read_text(WIN_WNDPROC_PATH)

	inject_activation_block = _extract_function_block(
		cl_cgame, "static void QLWebView_InjectActivationKeyboardEvent( void ) {"
	)
	inject_fields_block = _extract_function_block(
		cl_cgame, "static void QLWebView_InjectKeyboardEventFields( const qlWebKeyboardEventFields_t *event, qboolean down ) {"
	)
	notify_block = _extract_function_block(
		cl_cgame, "void CL_WebHost_NotifyAppActivation( qboolean active ) {"
	)
	activate_block = _extract_function_block(
		win_wndproc, "static void VID_AppActivate(BOOL fActive, BOOL minimize)"
	)

	assert "void CL_WebHost_NotifyAppActivation( qboolean active );" in client_h
	assert "unsigned int\teventType;" in cl_cgame
	assert "unsigned int\tvirtualKeyCode;" in cl_cgame
	assert "long\t\t\tnativeKeyCode;" in cl_cgame
	assert "#define QL_WEB_KEYBOARD_EVENT_ACTIVATION_TYPE 0u" in cl_cgame
	assert "#define QL_WEB_KEYBOARD_EVENT_ACTIVATION_VIRTUAL_KEY 0x11u" in cl_cgame
	assert "#define QL_WEB_KEYBOARD_EVENT_ACTIVATION_NATIVE_KEY 0x1d0001L" in cl_cgame
	assert "QLWebView_InjectKeyboardEvent( (int)event->virtualKeyCode, down );" in inject_fields_block
	assert "if ( !cl_webHost.viewInitialised ) {" in inject_activation_block
	assert "QL_WEB_KEYBOARD_EVENT_ACTIVATION_TYPE," in inject_activation_block
	assert "QL_WEB_KEYBOARD_EVENT_ACTIVATION_VIRTUAL_KEY," in inject_activation_block
	assert "QL_WEB_KEYBOARD_EVENT_ACTIVATION_NATIVE_KEY" in inject_activation_block
	assert "QLWebView_InjectKeyboardEventFields( &activationEvent, qtrue );" in inject_activation_block
	assert "if ( !active ) {" in notify_block
	assert "cl_webHost.focused = qfalse;" in notify_block
	assert "QLWebView_InjectActivationKeyboardEvent();" in notify_block
	assert "SetFocus( g_wv.hWnd );" in activate_block
	assert "CL_WebHost_NotifyAppActivation( qtrue );" in activate_block
	assert "CL_WebHost_NotifyAppActivation( qfalse );" in activate_block


def test_awesomium_win32_backend_documents_retail_slot_to_export_substitution() -> None:
	cl_awesomium = _read_text(CL_AWESOMIUM_WIN32_PATH)

	load_block = _extract_function_block(
		cl_awesomium, "static qboolean CL_Awesomium_LoadImports( const char *runtimePath, const char *basePath ) {"
	)
	count_bootstrap_block = _extract_function_block(
		cl_awesomium, "static int CL_Awesomium_CountBootstrapRetailMappings( void ) {"
	)
	prepare_config_block = _extract_function_block(
		cl_awesomium,
		"static qboolean CL_Awesomium_PrepareConfig( const char *runtimePath, const char *basePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh, const char *initialConfigJson, const char *initialMapJson, const char *initialFactoryJson ) {",
	)
	prepare_prefs_block = _extract_function_block(
		cl_awesomium, "static qboolean CL_Awesomium_PreparePreferences( void ) {"
	)
	create_session_block = _extract_function_block(
		cl_awesomium, "static qboolean CL_Awesomium_CreateSession( const char *runtimePath, const char *basePath ) {"
	)
	startup_block = _extract_function_block(
		cl_awesomium,
		'extern "C" qboolean CL_Awesomium_Startup( const char *runtimePath, const char *basePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh, int width, int height, const char *initialConfigJson, const char *initialMapJson, const char *initialFactoryJson ) {',
	)
	open_url_block = _extract_function_block(
		cl_awesomium, 'extern "C" qboolean CL_Awesomium_OpenURL( const char *url ) {'
	)
	update_block = _extract_function_block(
		cl_awesomium, 'extern "C" void CL_Awesomium_Update( void ) {'
	)
	resize_block = _extract_function_block(
		cl_awesomium, 'extern "C" qboolean CL_Awesomium_Resize( int width, int height ) {'
	)
	mouse_move_block = _extract_function_block(
		cl_awesomium, 'extern "C" void CL_Awesomium_InjectMouseMove( int x, int y ) {'
	)
	mouse_down_block = _extract_function_block(
		cl_awesomium, 'extern "C" void CL_Awesomium_InjectMouseDown( int button ) {'
	)
	mouse_up_block = _extract_function_block(
		cl_awesomium, 'extern "C" void CL_Awesomium_InjectMouseUp( int button ) {'
	)
	wheel_block = _extract_function_block(
		cl_awesomium, 'extern "C" void CL_Awesomium_InjectMouseWheel( int direction ) {'
	)
	shutdown_block = _extract_function_block(
		cl_awesomium, 'extern "C" void CL_Awesomium_Shutdown( void ) {'
	)
	clear_cache_live_block = _extract_function_block(
		cl_awesomium, 'extern "C" void CL_Awesomium_ClearCache( void ) {'
	)

	for expected in (
		'#define CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT "external SDK C API dependency"',
		'#define CL_AWE_RETAIL_ABI_SCOPE_SOURCE_KEYBOARD "source-owned keyboard event path"',
		'#define CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT "external SDK C API dependency"',
		'#define CL_AWE_RETAIL_BOOTSTRAP_SCOPE_OBJECT_LIFETIME "SDK-owned object lifetime"',
		'#define CL_AWE_RETAIL_BOOTSTRAP_SCOPE_SOURCE_LITERAL "retail literal retained in source adapter"',
		"clAwesomiumRetailAbiEquivalence_t",
		"clAwesomiumBootstrapRetailMapping_t",
		"retailOwnerAddress;",
		"retailAnchor;",
		"retailAddress;",
		"retailVtableSlot;",
		"retailMethod;",
		"adapterOwner;",
		"adapterBinding;",
		"substitutionKind;",
		"webSessionClearCache;",
		"static const clAwesomiumRetailAbiEquivalence_t cl_aweRetailAbiEquivalence[] = {",
		"static const clAwesomiumBootstrapRetailMapping_t cl_aweBootstrapRetailMappings[] = {",
		"exports resolved from `awesomium.dll`.",
		"view, URL, focus, and shutdown chain",
		"bootstrapMappingCount;",
	):
		assert expected in cl_awesomium

	for disallowed in (
		"CL_AWE_OBJECT_STORAGE_BYTES",
		"CL_AWESOMIUM_RETAIL_IMPORT",
		"CL_Awesomium_RetailAdapterForImport",
		"CL_Awesomium_VTableMethod",
		"__thiscall",
		"CL_AWE_BITMAP_WIDTH_OFFSET",
		"??0WebConfig@Awesomium@@QAE@XZ",
	):
		assert disallowed not in cl_awesomium

	for expected in (
		'{ 0x004F2590u, 0x18u, "WebCore::Update", "CL_Awesomium_Update", "_Awe_WebCore_Update@4", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },',
		'{ 0x004F25C0u, 0x9cu, "WebView::Resize", "CL_Awesomium_Resize", "_Awe_WebView_Resize@12", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },',
		'{ 0x004F2750u, 0xd0u, "WebView::InjectMouseMove", "CL_Awesomium_InjectMouseMove", "_Awe_WebView_InjectMouseMove@12", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },',
		'{ 0x004F27C0u, 0xd4u, "WebView::InjectMouseDown", "CL_Awesomium_InjectMouseDown", "_Awe_WebView_InjectMouseDown@8", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },',
		'{ 0x004F2820u, 0xd8u, "WebView::InjectMouseUp", "CL_Awesomium_InjectMouseUp", "_Awe_WebView_InjectMouseUp@8", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },',
		'{ 0x004F2870u, 0xdcu, "WebView::InjectMouseWheel", "CL_Awesomium_InjectMouseWheel", "_Awe_WebView_InjectMouseWheel@12", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },',
		'{ 0x004F28A0u, 0xe0u, "WebView::InjectKeyboardEvent", "CL_Awesomium_InjectKeyboardEvent", "_Awe_new_WebKeyboardEvent_1@12 + _Awe_WebView_InjectKeyboardEvent@8", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },',
	):
		assert expected in cl_awesomium

	for expected in (
		'{ 0x004F2D30u, 0x0052C6A4u, "WebConfig::WebConfig", "CL_Awesomium_PrepareConfig", "_Awe_new_WebConfig@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x0052C6A0u, "WebCore::Initialize", "CL_Awesomium_Startup", "_Awe_WebCore_Initialize@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x0052C698u, "WebPreferences::WebPreferences", "CL_Awesomium_PreparePreferences", "_Awe_new_WebPreferences@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x00000002u, "WebPreferences::enable_plugins byte", "CL_Awesomium_PreparePreferences", "_Awe_WebPreferences_enable_plugins_set@8", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x00000008u, "WebPreferences::enable_web_security byte", "CL_Awesomium_PreparePreferences", "_Awe_WebPreferences_enable_web_security_set@8", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x00000000u, "WebCore::CreateWebSession slot 0x00", "CL_Awesomium_CreateSession", "_Awe_WebCore_CreateWebSession@12", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x00000018u, "WebSession bootstrap slot 0x18", "CL_Awesomium_CreateSession", "_Awe_WebSession_Initialize@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2A10u, 0x0000001Cu, "WebSession::ClearCache slot 0x1C", "CL_Awesomium_ClearCache", "_Awe_WebSession_ClearCache@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x0052C694u, "DataPakSource::DataPakSource", "CL_Awesomium_CreateSession", "_Awe_new_DataPakSource@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x00548068u, "QL data-source name", "CL_Awesomium_CreateSession", "\\"QL\\"", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_SOURCE_LITERAL },',
		'{ 0x004F2D30u, 0x00548070u, "DataPakSource::vftable", "CL_Awesomium_CreateSession", "Awesomium built-in DataPakSource", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_OBJECT_LIFETIME },',
		'{ 0x004F2D30u, 0x00000010u, "WebSession::AddDataSource slot 0x10", "CL_Awesomium_CreateSession", "_Awe_WebSession_AddDataSource@12", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x00000004u, "WebCore::CreateWebView slot 0x04", "CL_Awesomium_Startup", "_Awe_WebCore_CreateWebView_0@20", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x000000A0u, "WebView::SetTransparent slot 0xA0", "CL_Awesomium_Startup", "_Awe_WebView_SetTransparent@8", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x00000064u, "WebView::LoadURL slot 0x64", "CL_Awesomium_OpenURL", "_Awe_WebView_LoadURL@8", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F24D0u, 0x000000A8u, "WebView::PauseRendering slot 0xA8", "CL_Awesomium_PauseRendering", "_Awe_WebView_PauseRendering@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x000000ACu, "WebView::ResumeRendering slot 0xAC", "CL_Awesomium_OpenURL", "_Awe_WebView_ResumeRendering@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x000000B0u, "WebView::Focus slot 0xB0", "CL_Awesomium_OpenURL", "_Awe_WebView_Focus@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F24D0u, 0x000000B4u, "WebView::Unfocus slot 0xB4", "CL_Awesomium_Unfocus", "_Awe_WebView_Unfocus@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x000000C4u, "WebView::SetZoom slot 0xC4", "CL_Awesomium_SetZoom", "_Awe_WebView_SetZoom@8", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x00000124u, "WebView::ExecuteJavascript slot 0x124", "CL_Awesomium_ExecuteJavascript", "_Awe_WebView_ExecuteJavascript@12", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x0000012Cu, "WebView::set_js_method_handler slot 0x12C", "CL_Awesomium_BuildStartupScript", "qz_instance startup bridge", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_SOURCE_LITERAL },',
		'{ 0x004F2D30u, 0x00000084u, "WebView::surface slot 0x84", "CL_Awesomium_Surface", "_Awe_WebView_surface@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2A60u, 0x00000000u, "WebView::Destroy slot 0x00", "CL_Awesomium_Shutdown", "_Awe_WebView_Destroy@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2A60u, 0x0052C684u, "WebCore::Shutdown", "CL_Awesomium_Shutdown", "_Awe_WebCore_Shutdown@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
	):
		assert expected in cl_awesomium

	for expected in (
		'CL_AWE_IMPORT( newWebConfig, "_Awe_new_WebConfig@0" );',
		'CL_AWE_IMPORT( newWebPreferences, "_Awe_new_WebPreferences@0" );',
		'CL_AWE_IMPORT( webPrefsEnablePluginsSet, "_Awe_WebPreferences_enable_plugins_set@8" );',
		'CL_AWE_IMPORT( webPrefsEnableWebSecuritySet, "_Awe_WebPreferences_enable_web_security_set@8" );',
		'cl_awe.webPrefsEnableGpuAccelerationSet = reinterpret_cast<awe_webprefs_set_bool_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_WebPreferences_enable_gpu_acceleration_set@8" ) );',
		'CL_AWE_IMPORT( webCoreInitialize, "_Awe_WebCore_Initialize@4" );',
		'CL_AWE_IMPORT( webCoreShutdown, "_Awe_WebCore_Shutdown@0" );',
		'CL_AWE_IMPORT( webCoreCreateWebSession, "_Awe_WebCore_CreateWebSession@12" );',
		'CL_AWE_IMPORT( webCoreCreateWebView, "_Awe_WebCore_CreateWebView_0@20" );',
		'CL_AWE_IMPORT( webConfigChildProcessPathSet, "_Awe_WebConfig_child_process_path_set@8" );',
		'cl_awe.webConfigAdditionalOptionsSet = reinterpret_cast<awe_webcore_set_object_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_WebConfig_additional_options_set@8" ) );',
		'CL_AWE_IMPORT( webConfigPackagePathSet, "_Awe_WebConfig_package_path_set@8" );',
		'CL_AWE_IMPORT( newDataPakSource, "_Awe_new_DataPakSource@4" );',
		'CL_AWE_IMPORT( webSessionAddDataSource, "_Awe_WebSession_AddDataSource@12" );',
		'cl_awe.webSessionInitialize = reinterpret_cast<awe_websession_void_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_WebSession_Initialize@4" ) );',
		'cl_awe.webSessionClearCache = reinterpret_cast<awe_websession_void_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_WebSession_ClearCache@4" ) );',
		'CL_AWE_IMPORT( webSessionRelease, "_Awe_WebSession_Release@4" );',
		'CL_AWE_IMPORT( webViewDestroy, "_Awe_WebView_Destroy@4" );',
		'CL_AWE_IMPORT( webViewLoadURL, "_Awe_WebView_LoadURL@8" );',
		'CL_AWE_IMPORT( webViewFocus, "_Awe_WebView_Focus@4" );',
		'CL_AWE_IMPORT( webViewSurface, "_Awe_WebView_surface@4" );',
		'CL_AWE_IMPORT( webCoreUpdate, "_Awe_WebCore_Update@4" );',
		'CL_AWE_IMPORT( webViewSetTransparent, "_Awe_WebView_SetTransparent@8" );',
		'cl_awe.webViewSetZoom = reinterpret_cast<awe_webview_set_zoom_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_WebView_SetZoom@8" ) );',
		'CL_AWE_IMPORT( webViewResize, "_Awe_WebView_Resize@12" );',
		'CL_AWE_IMPORT( webViewInjectMouseMove, "_Awe_WebView_InjectMouseMove@12" );',
		'CL_AWE_IMPORT( webViewInjectMouseDown, "_Awe_WebView_InjectMouseDown@8" );',
		'CL_AWE_IMPORT( webViewInjectMouseUp, "_Awe_WebView_InjectMouseUp@8" );',
		'CL_AWE_IMPORT( webViewInjectMouseWheel, "_Awe_WebView_InjectMouseWheel@12" );',
		'CL_AWE_IMPORT( newWebKeyboardEvent, "_Awe_new_WebKeyboardEvent_1@12" );',
		'CL_AWE_IMPORT( deleteWebKeyboardEvent, "_Awe_delete_WebKeyboardEvent@4" );',
		'CL_AWE_IMPORT( webViewInjectKeyboardEvent, "_Awe_WebView_InjectKeyboardEvent@8" );',
		'cl_awe.newWebStringArray = reinterpret_cast<awe_new_void_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_new_WebStringArray_0@0" ) );',
		'cl_awe.webStringArrayPush = reinterpret_cast<awe_webstring_array_push_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_WebStringArray_Push@8" ) );',
		'cl_awe.deleteWebStringArray = reinterpret_cast<awe_delete_object_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_delete_WebStringArray@4" ) );',
	):
		assert expected in load_block

	assert "for ( i = 0; cl_aweBootstrapRetailMappings[i].retailMember; i++ ) {" in count_bootstrap_block
	assert "cl_aweBootstrapRetailMappings[i].retailOwnerAddress != 0u" in count_bootstrap_block
	assert "cl_awe.webPrefsEnablePluginsSet( cl_awesomium.webPreferences, true );" in prepare_prefs_block
	assert "cl_awe.webPrefsEnableWebSecuritySet( cl_awesomium.webPreferences, false );" in prepare_prefs_block
	assert "cl_awe.webPrefsEnableGpuAccelerationSet( cl_awesomium.webPreferences, false );" in prepare_prefs_block
	for retail_default in (
		"webPrefsEnableJavascriptSet",
		"webPrefsEnableLocalStorageSet",
		"webPrefsEnableDatabasesSet",
		"webPrefsAllowFileAccessSet",
		"webPrefsAllowUniversalAccessSet",
	):
		assert retail_default not in cl_awesomium
	assert 'cl_awesomium.module = CL_Awesomium_LoadLibraryCandidate( "awesomium.dll", loadError, sizeof( loadError ) );' in load_block
	assert 'CL_Awesomium_AppendPath( libraryPath, sizeof( libraryPath ), runtimePath, "awesomium.dll" );' in load_block
	assert 'CL_Awesomium_AppendPath( libraryPath, sizeof( libraryPath ), basePath, "awesomium.dll" );' in load_block
	assert "cl_awesomium.bootstrapMappingCount = CL_Awesomium_CountBootstrapRetailMappings();" in load_block

	for expected in (
		"char childProcessPath[MAX_PATH];",
		"char childProcessConfigPath[MAX_PATH];",
		"char logPath[MAX_PATH];",
		"char packagePath[MAX_PATH];",
		"char packageRoot[MAX_PATH];",
		"const char *sessionPath;",
		"const char *assetsPath;",
		"sessionPath = runtimePath;",
		"assetsPath = runtimePath && runtimePath[0] ? runtimePath : basePath;",
		'CL_Awesomium_AppendPath( logPath, sizeof( logPath ), sessionPath, "awesomium.log" );',
		'CL_Awesomium_AppendPath( packagePath, sizeof( packagePath ), assetsPath, "web.pak" );',
		'CL_Awesomium_AppendPath( packagePath, sizeof( packagePath ), basePath, "web.pak" );',
		"CL_Awesomium_BuildUserScript( cl_awesomium.startupScript, sizeof( cl_awesomium.startupScript ), playerName, appId, steamIdLow, steamIdHigh, initialConfigJson, initialMapJson, initialFactoryJson );",
		"CL_Awesomium_SelectChildProcessPath( childProcessPath, sizeof( childProcessPath ), runtimePath, basePath )",
		'CL_Awesomium_CopyPath( childProcessConfigPath, sizeof( childProcessConfigPath ), "awesomium_process.exe" );',
		'"--no-sandbox"',
		'!CL_Awesomium_SetConfigString( cl_awe.webConfigAssetProtocolSet, cl_awesomium.webConfig, "asset" )',
		'!CL_Awesomium_SetConfigStringArrayOptions( cl_awe.webConfigAdditionalOptionsSet, cl_awesomium.webConfig, awesomiumOptions, sizeof( awesomiumOptions ) / sizeof( awesomiumOptions[0] ) )',
		"!CL_Awesomium_SetConfigString( cl_awe.webConfigChildProcessPathSet, cl_awesomium.webConfig, childProcessConfigPath )",
		"!CL_Awesomium_SetConfigString( cl_awe.webConfigLogPathSet, cl_awesomium.webConfig, logPath )",
		"!CL_Awesomium_SetConfigString( cl_awe.webConfigPackagePathSet, cl_awesomium.webConfig, packageRoot )",
		'Com_Printf( "Awesomium startup phase: deferring bridge script to WebView ExecuteJavascript\\n" );',
	):
		assert expected in prepare_config_block
	assert "!CL_Awesomium_SetConfigString( cl_awe.webConfigUserScriptSet" not in prepare_config_block
	assert "(void)runtimePath;" not in prepare_config_block
	assert "(void)basePath;" not in prepare_config_block
	assert "(void)playerName;" not in prepare_config_block
	assert "CL_Awesomium_HelperImportsChildProcessMain" in cl_awesomium
	assert "IMAGE_DIRECTORY_ENTRY_IMPORT" in cl_awesomium
	assert "ChildProcessMain@Awesomium" in cl_awesomium
	assert "must be staged beside the executable" in cl_awesomium
	assert '"--single-process"' not in prepare_config_block

	assert 'cl_awesomium.webSession = cl_awe.webCoreCreateWebSession( cl_awesomium.webCore, dataPath, cl_awesomium.webPreferences );' in create_session_block
	assert "cl_awe.webSessionInitialize( cl_awesomium.webSession );" in create_session_block
	assert "assetsPath = runtimePath && runtimePath[0] ? runtimePath : basePath;" in create_session_block
	assert 'CL_Awesomium_AppendPath( pakPath, sizeof( pakPath ), assetsPath, "web.pak" );' in create_session_block
	assert 'CL_Awesomium_AppendPath( pakPath, sizeof( pakPath ), basePath, "web.pak" );' in create_session_block
	assert 'pakName = CL_Awesomium_AllocWideString( "web.pak" );' in create_session_block
	assert 'Com_Printf( "Awesomium startup phase: creating DataPakSource from web.pak (validated %s)\\n", pakPath );' in create_session_block
	assert "cl_awesomium.dataPakSource = cl_awe.newDataPakSource( pakName );" in create_session_block
	assert 'sourceName = CL_Awesomium_AllocWideString( "QL" );' in create_session_block
	assert "cl_awe.webSessionAddDataSource( cl_awesomium.webSession, sourceName, cl_awesomium.dataPakSource );" in create_session_block
	assert "cl_awesomium.webCore = cl_awe.webCoreInitialize( cl_awesomium.webConfig );" in startup_block
	assert "cl_awesomium.webView = cl_awe.webCoreCreateWebView( cl_awesomium.webCore, width, height, cl_awesomium.webSession, 0 );" in startup_block
	assert "cl_awe.webViewFocus( cl_awesomium.webView );" in startup_block
	assert 'url = "asset://ql/index.html";' in open_url_block
	assert "cl_awe.webViewLoadURL( cl_awesomium.webView, webURL );" in open_url_block
	assert "CL_Awesomium_SetZoom( 100 );" in open_url_block
	assert "cl_awe.webViewFocus( cl_awesomium.webView );" in open_url_block
	assert "cl_awe.webCoreUpdate( cl_awesomium.webCore );" in update_block
	assert "cl_awe.webViewResize( cl_awesomium.webView, width, height );" in resize_block
	assert "cl_awe.webViewInjectMouseMove( cl_awesomium.webView, x, y );" in mouse_move_block
	assert "cl_awe.webViewInjectMouseDown( cl_awesomium.webView, button );" in mouse_down_block
	assert "cl_awe.webViewInjectMouseUp( cl_awesomium.webView, button );" in mouse_up_block
	assert "cl_awe.webViewInjectMouseWheel( cl_awesomium.webView, 0, direction * 30 );" in wheel_block
	assert "event = cl_awe.newWebKeyboardEvent( eventType, virtualKeyCode, nativeKeyCode );" in cl_awesomium
	assert "cl_awe.webViewInjectKeyboardEvent( cl_awesomium.webView, event );" in cl_awesomium
	assert "cl_awe.deleteWebKeyboardEvent( event );" in cl_awesomium
	assert "if ( cl_awesomium.started && cl_awesomium.webSession && cl_awe.webSessionClearCache ) {" in clear_cache_live_block
	assert "cl_awe.webSessionClearCache( cl_awesomium.webSession );" in clear_cache_live_block
	assert "cl_awe.webViewDestroy( cl_awesomium.webView );" in shutdown_block
	assert "cl_awe.webSessionRelease( cl_awesomium.webSession );" in shutdown_block
	assert "cl_awe.webCoreShutdown();" in shutdown_block


def test_awesomium_sdk_dependency_is_external_and_non_replicated() -> None:
	process_cpp = _read_text(AWESOMIUM_PROCESS_CPP_PATH)
	process_rc = _read_text(AWESOMIUM_PROCESS_RC_PATH)
	process_project = _read_text(AWESOMIUM_PROCESS_VCXPROJ_PATH)
	steam_project = _read_text(QUAKELIVE_STEAM_VCXPROJ_PATH)

	assert not AWESOMIUM_DEF_PATH.exists()
	assert "#include <Awesomium/ChildProcess.h>" in process_cpp
	assert "namespace Awesomium" not in process_cpp
	assert "int __cdecl ChildProcessMain" not in process_cpp
	assert "Awesomium::ChildProcessMain( instance );" in process_cpp

	for expected in (
		"AwesomiumSdkDir",
		"AWESOMIUM_SDK_DIR",
		"ValidateAwesomiumSdk",
		"Awesomium\\ChildProcess.h",
		"awesomium.lib",
		"do not commit or generate Awesomium SDK import libraries",
	):
		assert expected in process_project

	for disallowed in (
		"AwesomiumImportDef",
		"AwesomiumImportLib",
		"BuildAwesomiumImportLib",
		"awesomium.def",
		"awesomium_import.lib",
		"lib.exe",
	):
		assert disallowed not in process_project

	for expected in (
		"QLRequireAwesomiumSdk",
		"AwesomiumSdkDir",
		"AWESOMIUM_SDK_DIR",
		"ValidateAwesomiumSdk",
		"Awesomium\\WebCore.h",
		"awesomium.dll",
		"avcodec-53.dll",
		"avformat-53.dll",
		"avutil-51.dll",
		"icudt.dll",
		"libEGL.dll",
		"libGLESv2.dll",
		"AwesomiumRuntimeRootFile",
		"AwesomiumRuntimeLocaleFile",
		"CopyAwesomiumRuntime",
		'<Copy SourceFiles="@(AwesomiumRuntimeRootFile)" DestinationFolder="$(OutDir)" SkipUnchangedFiles="true"',
		'<Copy SourceFiles="@(AwesomiumRuntimeLocaleFile)" DestinationFiles="@(AwesomiumRuntimeLocaleFile->\'$(OutDir)locales\\%(RecursiveDir)%(Filename)%(Extension)\')"',
		'<ProjectReference Include="awesomium_process.vcxproj" Condition="\'$(QLBuildOnlineServices)\'!=\'0\' and \'$(AwesomiumSdkDir)\'!=\'\'">',
		"<AdditionalProperties>QLBuildOnlineServices=$(QLBuildOnlineServices);AwesomiumSdkDir=$(AwesomiumSdkDir)</AdditionalProperties>",
		"The SDK remains external and is not vendored.",
	):
		assert expected in steam_project

	for disallowed in (
		"BuildAwesomiumImportLib",
		"AwesomiumImportLib",
		"awesomium.def",
		"awesomium_import.lib",
	):
		assert disallowed not in steam_project

	assert 'VALUE "CompanyName", "Quake Live Reverse\\0"' in process_rc
	assert 'VALUE "FileDescription", "Quake Live Reverse Awesomium child-process host\\0"' in process_rc
	assert 'VALUE "ProductName", "Quake Live Reverse\\0"' in process_rc
	assert "Awesomium Technologies" not in process_rc
	assert 'VALUE "ProductName", "Awesomium\\0"' not in process_rc


def test_awesomium_null_host_browser_lane_is_explicit_compatibility_scope() -> None:
	null_client = _read_text(NULL_CLIENT_PATH)
	awesomium_plan = _read_text(AWESOMIUM_PLAN_PATH)
	function_gap_audit = _read_text(FUNCTION_PARITY_GAP_AUDIT_PATH)
	null_gap_note = _read_text(NULL_CLIENT_GAP_NOTE_PATH)

	refresh_block = _extract_function_block(
		null_client, "static void CL_NullRefreshBrowserCvars( void ) {"
	)
	live_view_block = _extract_function_block(null_client, "qboolean CL_WebHost_HasLiveView( void ) {")
	bound_window_block = _extract_function_block(
		null_client, "qboolean CL_WebHost_HasBoundWindowObject( void ) {"
	)
	cursor_block = _extract_function_block(null_client, "void *CL_WebHost_GetCursorHandle( void ) {")
	publish_block = _extract_function_block(
		null_client, "void CL_WebView_PublishEvent( const char *name, const char *payload ) {"
	)
	mouse_block = _extract_function_block(null_client, "void CL_WebView_OnMouseMove( int x, int y ) {")
	advert_init_block = _extract_function_block(null_client, "void CL_AdvertisementBridge_InitUI( void ) {")

	for expected in (
		'#define CL_NULL_BROWSER_PROVIDER_LABEL "Null host compatibility shim"',
		'#define CL_NULL_BROWSER_POLICY_LABEL "compatibility-only null host"',
		'#define CL_NULL_BROWSER_PARITY_SCOPE_LABEL "strict-retail-excluded"',
		'#define CL_NULL_BROWSER_PARITY_REASON_LABEL "retail Windows Awesomium host is outside the null-client portability lane"',
	):
		assert expected in null_client

	for expected in (
		'Cvar_Set( "ui_browserAwesomium", "0" );',
		'Cvar_Set( "ui_browserAwesomiumProvider", CL_NULL_BROWSER_PROVIDER_LABEL );',
		'Cvar_Set( "ui_browserAwesomiumPolicy", CL_NULL_BROWSER_POLICY_LABEL );',
		'Cvar_Set( "ui_browserAwesomiumParityScope", CL_NULL_BROWSER_PARITY_SCOPE_LABEL );',
		'Cvar_Set( "ui_browserAwesomiumParityReason", CL_NULL_BROWSER_PARITY_REASON_LABEL );',
		'Cvar_Set( "web_browserActive", "0" );',
		'Cvar_Set( "ui_advertisementBridgeProvider", CL_NULL_BROWSER_PROVIDER_LABEL );',
		'Cvar_Set( "ui_advertisementBridgePolicy", CL_NULL_BROWSER_POLICY_LABEL );',
		'Cvar_Set( "ui_advertisementBridgeParityScope", CL_NULL_BROWSER_PARITY_SCOPE_LABEL );',
		'Cvar_Set( "ui_advertisementBridgeParityReason", CL_NULL_BROWSER_PARITY_REASON_LABEL );',
	):
		assert expected in refresh_block

	assert "return qfalse;" in live_view_block
	assert "return qfalse;" in bound_window_block
	assert "return NULL;" in cursor_block
	assert "(void)name;" in publish_block
	assert "(void)payload;" in publish_block
	assert "(void)x;" in mouse_block
	assert "(void)y;" in mouse_block
	assert "CL_NullResetAdvertisementBridgeState();" in advert_init_block
	assert "CL_RefreshOnlineServicesBridgeState();" in advert_init_block

	assert "| Closed 2026-05-24 | Repo-wide non-Windows and null-host lanes keep the browser host stubbed or compatibility-only |" in awesomium_plan
	assert "null host publishes its strict-retail exclusion through provider, policy, parity-scope, and parity-reason cvars" in awesomium_plan
	assert "Current classification: Closed as explicit compatibility-only null browser/advert lane" in null_gap_note
	assert "strict-retail-excluded" in null_gap_note
	assert "`src/code/null/null_client.c`" in function_gap_audit
	assert "Null browser/advert lane now publishes the strict-retail exclusion through source-visible cvars" in function_gap_audit


def test_awesomium_browser_host_verifier_covers_closed_gap_anchors() -> None:
	verifier = _read_text(AWESOMIUM_BROWSER_HOST_VERIFY_PATH)

	for expected in (
		"QL_WEB_BRIDGE_RETAIL_OBJECT_ADDRESS 0x012D2670u",
		'QL_RESOURCE_INTERCEPTOR_HOST "ql"',
		"QLResourceInterceptor_OnFilterNavigation",
		"QLResourceInterceptor_RequestRetailHost",
		"cl_steamDataSourceRetailMappings",
		"cl_steamResponseThreadRetailMappings",
		"0x00532B80u",
		"0x00532B68u",
		"0x00532B44u",
		"0x004640C0u",
		"0x00464290u",
		"0x00463440u",
		"image/png",
		"request_%i",
		"ui_resourceBridgeSteamDataSourceMappings",
		"ui_resourceBridgeResponseThreadMappings",
		"QLDialogHandler_OnShowFileChooser",
		"cl_webListenerCallbackMappings",
		"0x00547FA8u",
		"0x00431640u",
		"CL_WEB_QZ_METHOD_TABLE_RETAIL_BEGIN 0x0055C008u",
		'{ "SetCvar", 0x0055C044u, CL_WEB_METHOD_SET_CVAR, qtrue },',
		'{ "ResetCvar", 0x0055C050u, CL_WEB_METHOD_RESET_CVAR, qtrue },',
		"CG_QL_IMPORT_PUBLISH_TAGGED_INFO_STRING = 116",
		"QL_CG_trap_PublishTaggedInfoString",
		"CL_WebView_PublishTaggedInfoString",
		"Info_NextPair( &cursor, key, value );",
		"QL_WEB_KEYBOARD_EVENT_ACTIVATION_NATIVE_KEY 0x1d0001L",
		"CL_AdvertisementBridge_IsDelayElapsed",
		"cl_aweRetailAbiEquivalence",
		"cl_aweBootstrapRetailMappings",
		"0x0052C6A4u",
		"0x0052C6A0u",
		"0x00548068u",
		"_Awe_WebCore_CreateWebSession@12",
		"_Awe_WebSession_AddDataSource@12",
		"_Awe_WebConfig_child_process_path_set@8",
		"CL_Awesomium_CountBootstrapRetailMappings",
		"CL_Awesomium_BuildUserScript",
		"_Awe_WebCore_Update@4",
		"_Awe_WebView_InjectMouseMove@12",
		'"sub_4F2900": "QLWebView_InjectActivationKeyboardEvent"',
		'"sub_4F2A60": "QLWebHost_Shutdown"',
		'"sub_4F2D30": "QLWebHost_OpenURL"',
		'"sub_434600": "QLResourceInterceptor_OnFilterNavigation"',
		'"sub_434620": "QLResourceInterceptor_OnRequest"',
		'"sub_4640C0": "SteamDataSource_OnRequest"',
		'"sub_464290": "SteamDataSource_OnAvatarImageLoaded"',
		'"sub_464300": "SteamDataSource_Init"',
		'"sub_464440": "SteamDataSource_Shutdown"',
		'"sub_464510": "SteamDataSource_Destroy"',
		'"sub_463110": "ResponseThread_PNGWriteCallback"',
		'"sub_463180": "ResponseThread_EncodeAvatarPNG"',
		'"sub_463440": "ResponseThread_Run"',
		'"sub_463550": "SteamDataSource_StartResponseThread"',
		'"sub_431640": "QLDialogHandler_OnShowFileChooser"',
		"WebKeyboardEvent\\(0, 0x11, 0x1d0001\\)",
		"QLResourceInterceptor_OnFilterNavigation.+QLResourceInterceptor_OnRequest.+/screenshot",
		"QLDialogHandler.+OnShowFileChooser.+0x00431640",
		"SteamDataSource::vftable.+0x00532B80",
		"SteamDataSource.+OnRequest.+0x004640C0",
		"ResponseThread::vftable.+0x00532B44",
		"ResponseThread::vftable.+0x00532B44.+image/png.+request_%i",
		"WebCore::Initialize.+WebSession::AddDataSource.+WebView::LoadURL.+WebCore::Shutdown",
		"data_55c008.+SetCustomMethod.+SetCvar.+0x0055C044.+ResetCvar.+0x0055C050.+NoOp.+0x0055C194",
	):
		assert expected in verifier

	assert "Awesomium browser host source, alias, mapping, and adapter parity anchors are present." in verifier


def test_awesomium_resource_interceptor_reconstructs_retail_ql_host_filter_lane() -> None:
	steam_resources = _read_text(CL_STEAM_RESOURCES_PATH)

	filter_block = _extract_function_block(
		steam_resources, "static qboolean QLResourceInterceptor_OnFilterNavigation( const char *url ) {"
	)
	parse_block = _extract_function_block(
		steam_resources, "static qboolean QLResourceInterceptor_ParseURL( const char *url, clResourceInterceptorUrl_t *parsed ) {"
	)
	map_block = _extract_function_block(
		steam_resources,
		"static qboolean QLResourceInterceptor_BuildMappedRequest( const clResourceInterceptorUrl_t *parsed, char *mappedUrl, size_t mappedUrlSize ) {",
	)
	retail_host_block = _extract_function_block(
		steam_resources,
		"static qboolean QLResourceInterceptor_RequestRetailHost( const char *url, clSteamDataSourceResponse_t *response ) {",
	)
	interceptor_block = _extract_function_block(
		steam_resources,
		"static qboolean QLResourceInterceptor_OnRequest( const char *url, clSteamDataSourceResponse_t *response ) {",
	)

	for expected in (
		'#define QL_RESOURCE_INTERCEPTOR_HOST "ql"',
		'#define QL_RESOURCE_INTERCEPTOR_SCREENSHOT_PATH "/screenshot"',
		'#define QL_RESOURCE_INTERCEPTOR_WEB_FALLBACK_PREFIX "https://cdn.quakelive.com/"',
		'#define QL_RESOURCE_INTERCEPTOR_SCREENSHOT_FALLBACK_PREFIX "quakelive://screenshots/"',
		"clResourceInterceptorUrl_t",
		"char\thost[64];",
		"char\tpath[MAX_QPATH];",
		"char\tfilename[MAX_QPATH];",
	):
		assert expected in steam_resources

	assert "(void)url;" in filter_block
	assert "return qfalse;" in filter_block
	assert 'scheme = strstr( url, "://" );' in parse_block
	assert "while ( *hostEnd && *hostEnd != '/' && *hostEnd != '\\\\' && *hostEnd != '?' && *hostEnd != '#' ) {" in parse_block
	assert "while ( *pathEnd && *pathEnd != '?' && *pathEnd != '#' ) {" in parse_block
	assert "Q_strncpyz( parsed->filename, filename, sizeof( parsed->filename ) );" in parse_block
	assert "QLResourceInterceptor_IsRetailHost( parsed )" in map_block
	assert "QLResourceInterceptor_IsScreenshotPath( parsed->path )" in map_block
	assert "QL_RESOURCE_INTERCEPTOR_SCREENSHOT_FALLBACK_PREFIX" in map_block
	assert "QL_RESOURCE_INTERCEPTOR_WEB_FALLBACK_PREFIX" in map_block
	assert "QLResourceInterceptor_ParseURL( url, &parsed )" in retail_host_block
	assert "QLResourceInterceptor_BuildMappedRequest( &parsed, mappedUrl, sizeof( mappedUrl ) )" in retail_host_block
	assert "CL_LauncherRequestData( mappedUrl, (void **)&response->buffer, &response->bufferLength )" in retail_host_block
	assert "CL_SteamDataSource_GuessMimeType( mappedUrl )" in retail_host_block
	assert "QLResourceInterceptor_OnFilterNavigation( url )" in interceptor_block
	assert "CL_SteamDataSource_Request( url, response )" in interceptor_block
	assert "QLResourceInterceptor_RequestRetailHost( url, response )" in interceptor_block
	assert interceptor_block.index("QLResourceInterceptor_OnFilterNavigation( url )") < interceptor_block.index(
		"CL_SteamDataSource_Request( url, response )"
	)
	assert interceptor_block.index("QLResourceInterceptor_RequestRetailHost( url, response )") < interceptor_block.index(
		"CL_LauncherRequestData( url, (void **)&response->buffer, &response->bufferLength )"
	)


def test_awesomium_steam_data_source_retail_wiring_is_source_visible() -> None:
	steam_resources = _read_text(CL_STEAM_RESOURCES_PATH)

	count_block = _extract_function_block(
		steam_resources, "static int CL_CountSteamDataSourceRetailMappings( void ) {"
	)
	refresh_block = _extract_function_block(
		steam_resources, "static void CL_RefreshSteamResourceBridgeCvars( void ) {"
	)

	for expected in (
		"clSteamDataSourceRetailMapping_t",
		"retailOwner;",
		"retailMember;",
		"retailVtableAddress;",
		"retailOffset;",
		"retailAddress;",
		"sourceOwner;",
		"static const clSteamDataSourceRetailMapping_t cl_steamDataSourceRetailMappings[] = {",
		'{ "SteamDataSource", "destroy", 0x00532B80u, 0x00u, 0x00464510u, "CL_ShutdownSteamResources", CL_STEAM_DATA_SOURCE_SCOPE_DESTRUCTOR },',
		'{ "SteamDataSource", "OnRequest", 0x00532B80u, 0x04u, 0x004640C0u, "CL_SteamDataSource_Request", CL_STEAM_DATA_SOURCE_SCOPE_COMPATIBILITY_OWNER },',
		'{ "SteamDataSource", "StartResponseThread", 0u, 0u, 0x00463550u, "CL_SteamResources_RequestAvatarRGBA", CL_STEAM_DATA_SOURCE_SCOPE_ASYNC_BOUNDARY },',
		'{ "SteamDataSource", "Init", 0u, 0u, 0x00464300u, "CL_InitSteamResources", CL_STEAM_DATA_SOURCE_SCOPE_LIFECYCLE_BOUNDARY },',
		'{ "SteamDataSource", "Shutdown", 0u, 0u, 0x00464440u, "CL_ShutdownSteamResources", CL_STEAM_DATA_SOURCE_SCOPE_LIFECYCLE_BOUNDARY },',
		'{ "CCallback<class SteamDataSource, struct AvatarImageLoaded_t, 0>", "callback target", 0x00532B68u, 0x10u, 0x00464290u, "CL_SteamResources_OnAvatarImageLoaded", CL_STEAM_DATA_SOURCE_SCOPE_AVATAR_CALLBACK },',
		'{ "CCallback<class SteamDataSource, struct AvatarImageLoaded_t, 0>", "callback id", 0x00532B68u, 0x14Eu, 0x00464300u, "CL_SteamResources_RegisterAvatarCallbacks", CL_STEAM_DATA_SOURCE_SCOPE_AVATAR_CALLBACK },',
	):
		assert expected in steam_resources

	assert "for ( i = 0; cl_steamDataSourceRetailMappings[i].retailOwner; i++ ) {" in count_block
	assert "cl_steamDataSourceRetailMappings[i].retailAddress != 0u" in count_block
	assert 'Cvar_Set( "ui_resourceBridgeSteamDataSourceMappings", va( "%i", CL_CountSteamDataSourceRetailMappings() ) );' in refresh_block


def test_awesomium_response_thread_async_wiring_is_source_visible() -> None:
	steam_resources = _read_text(CL_STEAM_RESOURCES_PATH)

	count_block = _extract_function_block(
		steam_resources, "static int CL_CountSteamResponseThreadRetailMappings( void ) {"
	)
	refresh_block = _extract_function_block(
		steam_resources, "static void CL_RefreshSteamResourceBridgeCvars( void ) {"
	)

	for expected in (
		"clSteamResponseThreadRetailMapping_t",
		"retailLiteral;",
		"#define CL_STEAM_RESPONSE_THREAD_RETAIL_VTABLE 0x00532B44u",
		'#define CL_STEAM_RESPONSE_THREAD_MIME_TYPE "image/png"',
		'#define CL_STEAM_RESPONSE_THREAD_THREAD_NAME "request_%i"',
		'#define CL_STEAM_RESPONSE_THREAD_PNG_VERSION "1.2.24"',
		'#define CL_STEAM_RESPONSE_THREAD_WRITE_ERROR "Write Error"',
		'#define CL_STEAM_RESPONSE_THREAD_STACK_RESERVE "0x100000"',
		"static const clSteamResponseThreadRetailMapping_t cl_steamResponseThreadRetailMappings[] = {",
		'{ "ResponseThread", "run", CL_STEAM_RESPONSE_THREAD_RETAIL_VTABLE, 0x04u, 0x00463440u, CL_STEAM_RESPONSE_THREAD_MIME_TYPE, "CL_SteamResources_RequestAvatarRGBA", CL_STEAM_RESPONSE_THREAD_SCOPE_ASYNC_BOUNDARY },',
		'{ "ResponseThread", "PNGWriteCallback", 0u, 0u, 0x00463110u, CL_STEAM_RESPONSE_THREAD_WRITE_ERROR, "CL_SteamResources_RequestAvatarRGBA", CL_STEAM_RESPONSE_THREAD_SCOPE_PNG_HELPER },',
		'{ "ResponseThread", "EncodeAvatarPNG", 0u, 0u, 0x00463180u, CL_STEAM_RESPONSE_THREAD_PNG_VERSION, "CL_SteamResources_RequestAvatarRGBA", CL_STEAM_RESPONSE_THREAD_SCOPE_PNG_HELPER },',
		'{ "Awesomium::DataSource", "SendResponse import", 0u, 0u, 0x0052C6B0u, CL_STEAM_RESPONSE_THREAD_MIME_TYPE, "QLResourceInterceptor_OnRequest", CL_STEAM_RESPONSE_THREAD_SCOPE_SEND_RESPONSE },',
		'{ "SteamDataSource", "StartResponseThread", 0u, 0u, 0x00463550u, CL_STEAM_RESPONSE_THREAD_THREAD_NAME, "CL_SteamResources_RequestAvatarRGBA", CL_STEAM_RESPONSE_THREAD_SCOPE_THREAD_START },',
		'{ "SteamDataSource", "ResponseThread stack reserve", 0u, 0x100000u, 0x00463550u, CL_STEAM_RESPONSE_THREAD_STACK_RESERVE, "CL_SteamResources_RequestAvatarRGBA", CL_STEAM_RESPONSE_THREAD_SCOPE_THREAD_START },',
	):
		assert expected in steam_resources

	assert "for ( i = 0; cl_steamResponseThreadRetailMappings[i].retailOwner; i++ ) {" in count_block
	assert "cl_steamResponseThreadRetailMappings[i].retailAddress != 0u" in count_block
	assert 'Cvar_Set( "ui_resourceBridgeResponseThreadMappings", va( "%i", CL_CountSteamResponseThreadRetailMappings() ) );' in refresh_block


def test_awesomium_listener_vtable_wiring_is_source_visible() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)

	dialog_block = _extract_function_block(cl_cgame, "static qboolean QLDialogHandler_OnShowFileChooser( void ) {")
	count_block = _extract_function_block(cl_cgame, "static int QLWebHost_CountRecoveredListenerMappings( void ) {")
	install_block = _extract_function_block(cl_cgame, "static void QLWebHost_InstallRuntimeListeners( void ) {")
	runtime_block = _extract_function_block(cl_cgame, "static qboolean QLWebHost_EnsureRuntime( void ) {")

	for expected in (
		"clWebListenerCallbackMapping_t",
		"listenerName;",
		"retailCallback;",
		"vtableAddress;",
		"slotOffset;",
		"retailAddress;",
		"sourceCallback;",
		"static const clWebListenerCallbackMapping_t cl_webListenerCallbackMappings[] = {",
		'{ "QLResourceInterceptor", "OnRequest", 0x00547F94u, 0x00u, 0x00434620u, "QLResourceInterceptor_OnRequest", CL_WEB_LISTENER_SCOPE_COMPATIBILITY_OWNER },',
		'{ "QLResourceInterceptor", "OnFilterNavigation", 0x00547F94u, 0x04u, 0x00434600u, "QLResourceInterceptor_OnFilterNavigation", CL_WEB_LISTENER_SCOPE_COMPATIBILITY_OWNER },',
		'{ "QLDialogHandler", "OnShowFileChooser", 0x00547FA8u, 0x08u, 0x00431640u, "QLDialogHandler_OnShowFileChooser", CL_WEB_LISTENER_SCOPE_BUILTIN_FORWARD },',
		'{ "QLViewHandler", "OnChangeTooltip", 0x00547FC0u, 0x08u, 0x00434450u, "QLViewHandler_OnChangeTooltip", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },',
		'{ "QLViewHandler", "OnChangeCursor", 0x00547FC0u, 0x10u, 0x00431670u, "QLViewHandler_OnChangeCursor", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },',
		'{ "QLViewHandler", "OnAddConsoleMessage", 0x00547FC0u, 0x18u, 0x00434520u, "QLViewHandler_OnAddConsoleMessage", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },',
		'{ "QLLoadHandler", "OnBeginLoadingFrame", 0x00547FE8u, 0x00u, 0x004317D0u, "QLLoadHandler_OnBeginLoadingFrame", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },',
		'{ "QLLoadHandler", "OnFailLoadingFrame", 0x00547FE8u, 0x04u, 0x00434AE0u, "QLLoadHandler_OnFailLoadingFrame", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },',
		'{ "QLLoadHandler", "OnFinishLoadingFrame", 0x00547FE8u, 0x08u, 0x004317E0u, "QLLoadHandler_OnFinishLoadingFrame", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },',
		'{ "QLLoadHandler", "OnDocumentReady", 0x00547FE8u, 0x0Cu, 0x004317F0u, "QLLoadHandler_OnDocumentReady", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },',
		'{ "QLJSHandler", "OnMethodCall", 0x00548010u, 0x00u, 0x00431E50u, "QLJSHandler_OnMethodCall", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },',
		'{ "QLJSHandler", "OnMethodCallWithReturnValue", 0x00548010u, 0x04u, 0x004328B0u, "QLJSHandler_OnMethodCallWithReturnValue", CL_WEB_LISTENER_SCOPE_SOURCE_CALLBACK },',
		'{ "QLJSHandler", "destroy", 0x00548010u, 0x08u, 0x004F23B0u, "QLJSHandler_Destroy", CL_WEB_LISTENER_SCOPE_DESTRUCTOR },',
		'{ "QLDialogHandler", "base/no-engine slot 0", 0x00547FA8u, 0x00u, 0x00431660u, "QLDialogHandler_NoEngineCallback", CL_WEB_LISTENER_SCOPE_NO_ENGINE_CALLBACK },',
	):
		assert expected in cl_cgame

	assert "int\t\t\tlistenerCallbackMappingCount;" in cl_cgame
	assert "return cl_webHost.liveAwesomium ? qtrue : qfalse;" in dialog_block
	assert "for ( i = 0; cl_webListenerCallbackMappings[i].listenerName; i++ ) {" in count_block
	assert "cl_webListenerCallbackMappings[i].retailAddress != 0u" in count_block
	assert "cl_webHost.listenerCallbackMappingCount = QLWebHost_CountRecoveredListenerMappings();" in install_block
	assert "cl_webHost.dialogHandlerInstalled = qtrue;" in install_block
	assert "cl_webHost.viewHandlerInstalled = qtrue;" in install_block
	assert "cl_webHost.loadHandlerInstalled = qtrue;" in install_block
	assert "(void)QLDialogHandler_OnShowFileChooser;" in runtime_block


def test_awesomium_qz_method_table_preserves_retail_return_flags() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_awesomium = _read_text(CL_AWESOMIUM_WIN32_PATH)
	cl_main = _read_text(CL_MAIN_PATH)

	method_call_block = _extract_function_block(
		cl_cgame, "static qboolean QLJSHandler_OnMethodCall( const char *methodName, const char **arguments, int argumentCount ) {"
	)
	return_call_block = _extract_function_block(
		cl_cgame,
		"static qboolean QLJSHandler_OnMethodCallWithReturnValue( const char *methodName, const char **arguments, int argumentCount, char *outValue, size_t outValueSize ) {",
	)
	startup_script_block = _extract_function_block(
		cl_awesomium,
		"static void CL_Awesomium_BuildUserScript( char *buffer, size_t bufferSize, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh, const char *initialConfigJson, const char *initialMapJson, const char *initialFactoryJson ) {",
	)
	dispatch_event_block = _extract_function_block(
		cl_main,
		"static void CL_WebView_DispatchLiveEvent( const char *name, const char *payload ) {",
	)
	publish_event_block = _extract_function_block(
		cl_main,
		"void CL_WebView_PublishEvent( const char *name, const char *payload ) {",
	)

	for expected in (
		"#define CL_WEB_QZ_METHOD_TABLE_RETAIL_BEGIN 0x0055C008u",
		"#define CL_WEB_QZ_METHOD_TABLE_RETAIL_END 0x0055C1A0u",
		"#define CL_WEB_QZ_METHOD_TABLE_ENTRY_BYTES 0x0Cu",
		"retailTableAddress;",
		'{ "SetCvar", 0x0055C044u, CL_WEB_METHOD_SET_CVAR, qtrue },',
		'{ "ResetCvar", 0x0055C050u, CL_WEB_METHOD_RESET_CVAR, qtrue },',
		'{ "GetAllUGC", 0x0055C170u, CL_WEB_METHOD_GET_ALL_UGC, qfalse },',
		'{ "SetFavoriteServer", 0x0055C188u, CL_WEB_METHOD_SET_FAVORITE_SERVER, qfalse },',
		'{ "NoOp", 0x0055C194u, CL_WEB_METHOD_NO_OP, qfalse },',
	):
		assert expected in cl_cgame

	assert "case CL_WEB_METHOD_SET_CVAR:" not in method_call_block
	assert "case CL_WEB_METHOD_RESET_CVAR:" not in method_call_block
	assert "case CL_WEB_METHOD_SET_CVAR:" in return_call_block
	assert 'Cvar_Set( arguments[0], arguments[1] ? arguments[1] : "" );' in return_call_block
	assert 'Q_strncpyz( outValue, "1", outValueSize );' in return_call_block
	assert "case CL_WEB_METHOD_RESET_CVAR:" in return_call_block
	assert "Cvar_Reset( arguments[0] );" in return_call_block

	for expected in (
		"const char *configJson;",
		"const char *mapJson;",
		"const char *factoryJson;",
		"configJson = ( initialConfigJson && initialConfigJson[0] ) ? initialConfigJson : \"null\";",
		"mapJson = ( initialMapJson && initialMapJson[0] ) ? initialMapJson : \"null\";",
		"factoryJson = ( initialFactoryJson && initialFactoryJson[0] ) ? initialFactoryJson : \"null\";",
		"window.__qlr_initial_config_applied=applyNativeConfig(%s);",
		"var nativeQueue=window.__qlr_native_requests=window.__qlr_native_requests||[];",
		"var pendingNativeMaps={};",
		"var basegtMap={ffa:0,duel:1,race:2,tdm:3,ca:4,ctf:5,oneflag:6,overload:7,har:8,ft:9,dom:10,ad:11,rr:12};",
		"var basegtValue=function(v){if(typeof v==='number'){return v|0;}var s=canon(v);if(hasOwn.call(basegtMap,s)){return basegtMap[s];}var n=parseInt(v,10);return isNaN(n)?0:n;};",
		"var copyObject=function(target,source){if(!target||!source){return false;}for(var oldKey in target){if(hasOwn.call(target,oldKey)){delete target[oldKey];}}for(var newKey in source){if(hasOwn.call(source,newKey)){target[newKey]=source[newKey];}}return true;};",
		"var syncModuleObject=function(path,source){try{if(window.req){var moduleObject=window.req(path);if(moduleObject&&moduleObject!==source){copyObject(moduleObject,source);}}}catch(e){}};",
		"var normalizeMapList=function(list){var out={};try{if(!list){return out;}",
		"var normalizeFactoryList=function(list){var out={};try{if(!list){return out;}",
		"f.basegt=basegtValue(f.basegt);",
		"fm.basegt=basegtValue(fm.basegt);",
		"var applyNativeMaps=function(list){var nextMaps=normalizeMapList(list);if(!objectHasEntries(nextMaps)){return false;}copyObject(maps,nextMaps);syncModuleObject('../src/mapdb',maps);return true;};",
		"var applyNativeFactories=function(list){var nextFactories=normalizeFactoryList(list);if(!objectHasEntries(nextFactories)){return false;}copyObject(factories,nextFactories);syncModuleObject('../src/factories',factories);return true;};",
		"var beginNativeMaps=function(){pendingNativeMaps={};return true;};",
		"var addNativeMaps=function(list){var nextMaps=normalizeMapList(list);for(var pk in nextMaps){if(hasOwn.call(nextMaps,pk)){pendingNativeMaps[pk]=nextMaps[pk];}}return true;};",
		"var commitNativeMaps=function(){var ok=applyNativeMaps(pendingNativeMaps);pendingNativeMaps={};return ok;};",
		"if(cfg.maps){applyNativeMaps(cfg.maps);}if(cfg.factories){applyNativeFactories(cfg.factories);}",
		"window.__qlr_initial_maps_applied=applyNativeMaps(%s);window.__qlr_initial_factories_applied=applyNativeFactories(%s);",
		"return queue('cmd',cmd);",
		"SetCvar:function(name,value){var k=canon(name);if(!k){return false;}value=String(value||'');config.cvars[k]=value;return queue('set',k+'\\\\n'+value);}",
		"ResetCvar:function(name){var k=canon(name);if(!k){return false;}delete config.cvars[k];return queue('reset',k);}",
		"Invite GetAllUGC GetNextKeyDown SetFavoriteServer NoOp",
		"bind('GetCvar',function(n){var k=canon(n);if(k&&typeof config.cvars[k]==='undefined'){queue('get',k);}return config.cvars[k]||'';});",
		"bind('SetCvar',function(n,v){var k=canon(n);if(!k){return false;}v=String(v||'');config.cvars[k]=v;return queue('set',k+'\\\\n'+v);});",
		"bind('ResetCvar',function(n){var k=canon(n);if(!k){return false;}delete config.cvars[k];return queue('reset',k);});",
		"window.qz_instance=qz;for(var fk0 in qz){window.FakeClient.qz_instance[fk0]=qz[fk0];}",
		"window.__qlr_apply_native_config=applyNativeConfig;window.__qlr_apply_native_maps=applyNativeMaps;window.__qlr_apply_native_factories=applyNativeFactories;window.__qlr_begin_native_maps=beginNativeMaps;window.__qlr_add_native_maps=addNativeMaps;window.__qlr_commit_native_maps=commitNativeMaps;window.__qlr_set_native_cvar=setNativeCvar;",
		"if(window.__qlr_pending_native_maps){applyNativeMaps(window.__qlr_pending_native_maps);window.__qlr_pending_native_maps=null;}",
		"if(f){for(var k in qz){f[k]=qz[k];}}window.qz_instance=qz;",
	):
		assert expected in startup_script_block
	assert "char\tstartupScript[393216];" in cl_awesomium
	assert "#define CL_AWE_STARTUP_SCRIPT_RETRY_FRAMES 240" in cl_awesomium
	assert "#define CL_AWE_STARTUP_SCRIPT_RETRY_INTERVAL 10" in cl_awesomium
	assert "char\tstartupRetryScript[256];" in cl_awesomium
	assert "CL_Awesomium_BuildRetryScript( cl_awesomium.startupRetryScript, sizeof( cl_awesomium.startupRetryScript ) );" in cl_awesomium
	assert "CL_Awesomium_StartupScriptReady" in cl_awesomium
	assert "script = cl_awesomium.startupScript;" in cl_awesomium
	assert "script = cl_awesomium.startupRetryScript;" in cl_awesomium

	for expected in (
		"#define CL_WEB_NATIVE_REQUESTS_PER_FRAME 1",
		"#define CL_WEB_NATIVE_REQUEST_STARTUP_DELAY_FRAMES 120",
		"#define CL_WEB_NATIVE_REQUEST_IDLE_POLL_FRAMES 15",
		"#define CL_WEB_NATIVE_REQUEST_LOADING_POLL_FRAMES 30",
		"#define CL_WEB_NATIVE_CONFIG_SYNC_FRAMES 300",
		"#define CL_WEB_NATIVE_MAP_SYNC_FRAMES 300",
		"#define CL_WEB_NATIVE_FACTORY_SYNC_FRAMES 300",
		"#define CL_WEB_NATIVE_FACTORY_RETRY_FRAMES 15",
		"#define CL_WEB_MAP_JSON_BUFFER_SIZE 65536",
		"#define CL_WEB_FACTORY_JSON_BUFFER_SIZE 65536",
		"#define CL_WEB_MAP_SYNC_CHUNK_CHARS 8192",
		"initialConfigJson = (char *)Z_Malloc( CL_WEB_NATIVE_CONFIG_BUFFER_SIZE );",
		"CL_WebHost_BuildConfigJson( initialConfigJson, CL_WEB_NATIVE_CONFIG_BUFFER_SIZE );",
		"initialMapJson = (char *)Z_Malloc( CL_WEB_MAP_JSON_BUFFER_SIZE );",
		"CL_WebHost_BuildMapListJson( initialMapJson, CL_WEB_MAP_JSON_BUFFER_SIZE );",
		"initialFactoryJson = (char *)Z_Malloc( CL_WEB_FACTORY_JSON_BUFFER_SIZE );",
		"CL_WebHost_BuildFactoryListJson( initialFactoryJson, CL_WEB_FACTORY_JSON_BUFFER_SIZE );",
		"CL_Awesomium_Startup( homePath, basePath, cl_webHost.playerName, cl_webHost.appId, cl_webHost.steamIdLow, cl_webHost.steamIdHigh, cls.glconfig.vidWidth, cls.glconfig.vidHeight, initialConfigJson, initialMapJson, initialFactoryJson )",
		"cl_webHost.configSynced = qtrue;",
		"cl_webHost.nextNativeRequestPollFrame = cl_webHost.frameSequence + CL_WEB_NATIVE_REQUEST_STARTUP_DELAY_FRAMES;",
		'Q_strcat( context->buffer, context->bufferSize, "\\\"" );',
		'Q_strcat( context->buffer, context->bufferSize, "\\":\\"" );',
		'Q_strcat( context->buffer, context->bufferSize, ",\\"key\\":\\"" );',
		'Q_strcat( buffer, bufferSize, "\\",\\"cvars\\":{" );',
		'Q_strcat( buffer, bufferSize, "},\\"binds\\":[" );',
		"static void CL_WebHost_PumpNativeJavascriptRequests( void );",
		"static void CL_WebHost_SyncConfigSnapshot( void );",
		"static void CL_WebHost_SyncMapCatalogSnapshot( void );",
		"static void CL_WebHost_SyncFactoryCatalogSnapshot( void );",
		"CL_WebHost_MapCatalogBridgeReady",
		"typeof window.qz_instance.GetFactoryList==='function'",
		"typeof window.__qlr_apply_native_factories==='function'",
		"CL_WebHost_ExecuteMapCatalogBatches",
		"CL_WebHost_ExecuteMapCatalogBatch",
		"CL_WebHost_ExecuteFactoryCatalogSnapshot",
		"CL_Awesomium_ExecuteJavascriptInteger",
		"cl_webHost.frameSequence < cl_webHost.nextNativeRequestPollFrame",
		"CL_Awesomium_IsLoading()",
		"CL_Awesomium_PopJavascriptRequest( request, sizeof( request ) )",
		'CL_WebHost_ProcessNativeJavascriptRequest( request );',
		'Cbuf_ExecuteText( EXEC_APPEND, va( "%s\\n", payload ) );',
		"Cvar_VariableStringBuffer( name, value, sizeof( value ) );",
		"Cvar_Set( name, value );",
		"Cvar_Reset( name );",
		"CL_WebHost_UpdateBrowserCvarCache( name, value );",
		"CL_WebHost_PumpNativeJavascriptRequests();",
		"CL_WebHost_SyncMapCatalogSnapshot();",
		"CL_WebHost_SyncFactoryCatalogSnapshot();",
		"CL_WebHost_SyncConfigSnapshot();",
	):
		assert expected in cl_cgame

	for expected in (
		"typedef void *(__stdcall *awe_webview_execute_javascript_with_result_fn)",
		"_Awe_WebView_ExecuteJavascriptWithResult@12",
		"_Awe_JSValue_ToInteger@4",
		"_Awe_delete_JSValue@4",
		'extern "C" qboolean CL_Awesomium_ExecuteJavascriptInteger( const char *script, const char *frame, int *outValue )',
		"CL_Awesomium_PopJavascriptRequest",
		"window.__qlr_native_requests||[]",
		"window.__qlr_native_read=String(q.shift())",
	):
		assert expected in cl_awesomium

	for expected in (
		"CL_WebHost_HasDrawableSurface()",
		"JSON.parse(p)",
		"window.EnginePublish",
		'CL_Awesomium_ExecuteJavascript( script, "" );',
	):
		assert expected in dispatch_event_block
	assert "CL_WebView_DispatchLiveEvent( event->name, event->payload );" in publish_event_block


def test_awesomium_tagged_info_string_comm_notice_wiring_matches_retail_slot() -> None:
	cg_public = _read_text(CG_PUBLIC_PATH)
	cg_syscalls = _read_text(CG_SYSCALLS_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_main = _read_text(CL_MAIN_PATH)
	client_h = _read_text(CLIENT_H_PATH)
	null_client = _read_text(NULL_CLIENT_PATH)

	invoke_block = _extract_function_block(cl_main, "void CL_WebView_InvokeCommNotice( const char *message ) {")
	publish_block = _extract_function_block(
		cl_main, "void CL_WebView_PublishTaggedInfoString( const char *messageType, const char *infoString ) {"
	)
	cgame_trap_block = _extract_function_block(
		cl_cgame, "static void QDECL QL_CG_trap_PublishTaggedInfoString( const char *messageType, const char *infoString ) {"
	)
	syscall_block = _extract_function_block(
		cg_syscalls, "void trap_QL_PublishTaggedInfoString( const char *messageType, const char *infoString ) {"
	)
	null_publish_block = _extract_function_block(
		null_client, "void CL_WebView_PublishTaggedInfoString( const char *messageType, const char *infoString ) {"
	)

	assert "CG_QL_IMPORT_PUBLISH_TAGGED_INFO_STRING = 116," in cg_public
	assert "CG_QL_IMPORT_TAGGED_CVAR_STRING_BUFFER" not in cg_public
	assert "void CL_WebView_InvokeCommNotice( const char *message );" in client_h
	assert "void CL_WebView_PublishTaggedInfoString( const char *messageType, const char *infoString );" in client_h
	assert 'CL_WebView_PublishEvent( "web.commNotice", message ? message : "" );' in invoke_block
	assert 'CL_WebView_AppendTaggedInfoPair( payload, sizeof( payload ), "MSG_TYPE", messageType ? messageType : "", &first );' in publish_block
	assert "Info_NextPair( &cursor, key, value );" in publish_block
	assert "CL_WebView_InvokeCommNotice( payload );" in publish_block
	assert "CL_WebView_PublishTaggedInfoString( messageType, infoString );" in cgame_trap_block
	assert "CG_GetNativeImportFunction( CG_QL_IMPORT_PUBLISH_TAGGED_INFO_STRING )" in syscall_block
	assert '((void (QDECL *)( const char *, const char * ))import)( messageType, infoString );' in syscall_block
	assert "(void)messageType;" in null_publish_block
	assert "(void)infoString;" in null_publish_block
	assert "TaggedCvarStringBuffer" not in cl_cgame
	assert "TaggedCvarStringBuffer" not in cg_syscalls


def test_awesomium_mouse_button_and_wheel_helpers_reconstruct_retail_pointer_injection_surface() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_keys = _read_text(CL_KEYS_PATH)
	client_h = _read_text(CLIENT_H_PATH)

	map_button_block = _extract_function_block(
		cl_cgame, "static int CL_WebHost_MapMouseButton( int key ) {"
	)
	mouse_down_block = _extract_function_block(
		cl_cgame, "static void QLWebView_InjectMouseDown( int key ) {"
	)
	mouse_up_block = _extract_function_block(
		cl_cgame, "static void QLWebView_InjectMouseUp( int key ) {"
	)
	wheel_block = _extract_function_block(
		cl_cgame, "static void QLWebView_InjectMouseWheel( int direction ) {"
	)
	public_button_block = _extract_function_block(
		cl_cgame, "void CL_WebView_OnMouseButtonEvent( int key, qboolean down ) {"
	)
	public_wheel_block = _extract_function_block(
		cl_cgame, "void CL_WebView_OnMouseWheelEvent( int direction ) {"
	)
	browser_key_block = _extract_function_block(
		cl_keys, "static void CL_DispatchBrowserKeyEvent( int key, qboolean down ) {"
	)
	key_event_block = _extract_function_block(cl_keys, "void CL_KeyEvent (int key, qboolean down, unsigned time) {")

	assert "void CL_WebView_OnMouseButtonEvent( int key, qboolean down );" in client_h
	assert "void CL_WebView_OnMouseWheelEvent( int direction );" in client_h
	assert "void CL_WebHost_HideBrowser( void );" in client_h
	assert "case K_MOUSE1:" in map_button_block
	assert "case K_MOUSE2:" in map_button_block
	assert "case K_MOUSE3:" in map_button_block
	assert "QLWebView_InjectMappedMouseMove( cl_webHost.cursorX, cl_webHost.cursorY );" in mouse_down_block
	assert "button = CL_WebHost_MapMouseButton( key );" in mouse_down_block
	assert "button = CL_WebHost_MapMouseButton( key );" in mouse_up_block
	assert "if ( direction == 0 ) {" in wheel_block
	assert "QLWebView_InjectMouseDown( key );" in public_button_block
	assert "QLWebView_InjectMouseUp( key );" in public_button_block
	assert "QLWebView_InjectMouseWheel( direction );" in public_wheel_block
	assert "if ( key >= K_MOUSE1 && key <= K_MOUSE9 ) {" in browser_key_block
	assert "CL_WebView_OnMouseButtonEvent( key, down );" in browser_key_block
	assert 'key == K_MWHEELUP' in browser_key_block
	assert 'CL_WebView_OnMouseWheelEvent( 1 );' in browser_key_block
	assert 'key == K_MWHEELDOWN' in browser_key_block
	assert 'CL_WebView_OnMouseWheelEvent( -1 );' in browser_key_block
	assert "CL_WebView_OnKeyEvent( key, down );" in browser_key_block
	escape_block_index = key_event_block.index("if ( key == K_ESCAPE && dispatchDown ) {")
	browser_escape_index = key_event_block.index("if ( cls.keyCatchers & KEYCATCH_BROWSER ) {", escape_block_index)
	browser_escape_return_index = key_event_block.index("return;", browser_escape_index)
	menu_toggle_index = key_event_block.index("CL_ToggleMenuInternal", escape_block_index)
	assert browser_escape_return_index < menu_toggle_index
	assert "CL_WebHost_HideBrowser();" not in key_event_block
	assert "CL_DispatchBrowserKeyEvent( dispatchKey, dispatchDown );" in key_event_block
	assert "CL_WebView_OnMouseButtonEvent( dispatchKey, dispatchDown );" not in key_event_block


def test_awesomium_document_ready_stages_launcher_script_bundle_before_ready_event() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_webpak = _read_text(REPO_ROOT / "src/code/client/cl_webpak.c")
	client_h = _read_text(CLIENT_H_PATH)
	qcommon_h = _read_text(REPO_ROOT / "src/code/qcommon/qcommon.h")
	files_c = _read_text(REPO_ROOT / "src/code/qcommon/files.c")

	load_scripts_block = _extract_function_block(
		cl_cgame, "static void QLLoadHandler_LoadDocumentScripts( void ) {"
	)
	execute_script_block = _extract_function_block(
		cl_cgame, "static void QLLoadHandler_ExecuteDocumentScript( const char *scriptPath, char *scriptBuffer, int scriptLength ) {"
	)
	poll_ready_block = _extract_function_block(
		cl_cgame, "static void QLLoadHandler_PollLiveDocumentReady( void ) {"
	)
	document_ready_block = _extract_function_block(
		cl_cgame, "static void QLLoadHandler_OnDocumentReady( void ) {"
	)
	webpak_list_block = _extract_function_block(
		cl_webpak, "int CL_WebPak_GetFileList( const char *path, const char *extension, char *listbuf, int bufsize ) {"
	)
	pak_list_block = _extract_function_block(
		files_c, "int FS_GetPakFileList( const pack_t *pack, const char *path, const char *extension, char *listbuf, int bufsize ) {"
	)

	assert "int CL_WebPak_GetFileList( const char *path, const char *extension, char *listbuf, int bufsize );" in client_h
	assert "int\t\tFS_GetPakFileList( const pack_t *pack, const char *path, const char *extension, char *listbuf, int bufsize );" in qcommon_h
	assert "int\t\t\tloadedDocumentScriptCount;" in cl_cgame
	assert "int\t\t\texecutedDocumentScriptCount;" in cl_cgame
	assert "int\t\t\tfailedDocumentScriptCount;" in cl_cgame
	assert 'count = CL_WebPak_GetFileList( "js", ".js", fileList, sizeof( fileList ) );' in load_scripts_block
	assert 'Com_sprintf( scriptPath, sizeof( scriptPath ), "js/%s", cursor );' in load_scripts_block
	assert "CL_LauncherRequestData( scriptPath, (void **)&scriptBuffer, &scriptLength )" in load_scripts_block
	assert "cl_webHost.loadedDocumentScriptCount++;" in load_scripts_block
	assert "QLLoadHandler_ExecuteDocumentScript( scriptPath, scriptBuffer, scriptLength );" in load_scripts_block
	assert "scriptBuffer[scriptLength] = '\\0';" in execute_script_block
	assert 'CL_Awesomium_ExecuteJavascript( scriptBuffer, "" )' in execute_script_block
	assert "cl_webHost.executedDocumentScriptCount++;" in execute_script_block
	assert "cl_webHost.failedDocumentScriptCount++;" in execute_script_block
	assert "Z_Free( scriptBuffer );" in load_scripts_block
	assert "if ( CL_Awesomium_IsLoading() ) {" in poll_ready_block
	assert "QLLoadHandler_OnFinishLoadingFrame();" in poll_ready_block
	assert "QLLoadHandler_OnDocumentReady();" in poll_ready_block
	assert "QLLoadHandler_LoadDocumentScripts();" in document_ready_block
	assert "QLJSHandler_BindQzInstance();" in document_ready_block
	assert "sourceCount = FS_GetPakFileList( cl_webPak, path, extension, sourceList, sizeof( sourceList ) );" in webpak_list_block
	assert "sourceCount = CL_WebDataPak_GetFileList( path, extension, sourceList, sizeof( sourceList ) );" in webpak_list_block
	assert "sourceCount = FS_GetFileList( path, extension, sourceList, sizeof( sourceList ) );" in webpak_list_block
	assert "nFiles = FS_AddFileToList( name + temp, list, nFiles );" in pak_list_block


def test_awesomium_advert_bridge_models_retail_data_12d2670_slot_layout() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)
	client_h = _read_text(CLIENT_H_PATH)
	cl_ui = _read_text(REPO_ROOT / "src/code/client/cl_ui.c")

	init_ui_block = _extract_function_block(cl_cgame, "void CL_AdvertisementBridge_InitUI( void ) {")
	activate_block = _extract_function_block(cl_cgame, "void CL_AdvertisementBridge_ActivateAdvert( int cellId ) {")
	set_active_block = _extract_function_block(cl_cgame, "void CL_AdvertisementBridge_SetActiveAdvert( int cellId ) {")
	bridge_set_active_block = _extract_function_block(
		cl_cgame, "static int QLWebBridge_SetActiveAdvert( ql_web_bridge_t *bridge, int cellId ) {"
	)
	bridge_shader_block = _extract_function_block(
		cl_cgame, "static qhandle_t QLWebBridge_RegisterDefaultAdvertCellShader( const char *defaultContent ) {"
	)
	ui_setup_block = _extract_function_block(
		cl_ui, "static qhandle_t QDECL QL_UI_trap_SetupAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {"
	)
	cg_setup_block = _extract_function_block(
		cl_cgame, "static qhandle_t QDECL QL_CG_trap_SetupAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {"
	)
	map_path_block = _extract_function_block(
		cl_cgame, "static void QDECL QL_CG_trap_AdvertisementBridge_SetMapPath( const char *mapPath ) {"
	)

	for expected in (
		"#define QL_WEB_BRIDGE_RETAIL_OBJECT_ADDRESS 0x012D2670u",
		"typedef struct ql_web_bridge_s ql_web_bridge_t;",
		"const ql_web_bridge_vtbl_t\t*vtbl;",
		"clAdvertisementBridgeState_t\t*advertisement;",
		"QL_WEB_BRIDGE_SLOT_SET_ACTIVE_ADVERT = 0x08",
		"QL_WEB_BRIDGE_SLOT_SET_APP_ACTIVATION = 0x0c",
		"QL_WEB_BRIDGE_SLOT_UPDATE_VIEW_PARAMETERS = 0x14",
		"QL_WEB_BRIDGE_SLOT_SET_VISIBILITY_TRACE_CALLBACK = 0x18",
		"QL_WEB_BRIDGE_SLOT_SET_MAP_PATH = 0x20",
		"QL_WEB_BRIDGE_SLOT_INIT_CGAME = 0x24",
		"QL_WEB_BRIDGE_SLOT_SHUTDOWN_CGAME = 0x28",
		"QL_WEB_BRIDGE_SLOT_GET_CELL_DISPLAY_STATE = 0x38",
		"QL_WEB_BRIDGE_SLOT_GET_CELL_LABEL = 0x3c",
		"QL_WEB_BRIDGE_SLOT_SETUP_ADVERT_CELL_SHADER = 0x50",
		"QL_WEB_BRIDGE_SLOT_SETUP_UI_ADVERT_CELL_SHADER = 0x54",
		"QL_WEB_BRIDGE_SLOT_REFRESH_ADVERT_CELL_SHADER = 0x58",
		"QL_WEB_BRIDGE_SLOT_REFRESH_UI_ADVERT_CELL_SHADER = 0x5c",
		"QL_WEB_BRIDGE_SLOT_ACTIVATE_ADVERT = 0x68",
		"QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( setActiveAdvert, QL_WEB_BRIDGE_SLOT_SET_ACTIVE_ADVERT );",
		"QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( setupUIAdvertCellShader, QL_WEB_BRIDGE_SLOT_SETUP_UI_ADVERT_CELL_SHADER );",
		"static const ql_web_bridge_vtbl_t cl_webBridgeVtbl = {",
		"static ql_web_bridge_t cl_webBridge = {",
	):
		assert expected in cl_cgame
	assert "clWebHostState_t" in cl_cgame and "*webHost;" in cl_cgame

	for expected in (
		"qhandle_t CL_AdvertisementBridge_SetupUIAdvertCellShader( const char *defaultContent, const void *rect, int cellId );",
		"qhandle_t CL_AdvertisementBridge_RefreshUIAdvertCellShader( const char *defaultContent, const void *rect, int cellId );",
		"qhandle_t CL_AdvertisementBridge_SetupAdvertCellShader( const char *defaultContent, const void *rect, int cellId );",
		"qhandle_t CL_AdvertisementBridge_RefreshAdvertCellShader( const char *defaultContent, const void *rect, int cellId );",
	):
		assert expected in client_h

	assert "cl_webBridge.vtbl->initUI( &cl_webBridge );" in init_ui_block
	assert "cl_webBridge.vtbl->activateAdvert( &cl_webBridge, cellId );" in activate_block
	assert "cl_webBridge.vtbl->setActiveAdvert( &cl_webBridge, cellId );" in set_active_block
	assert "advertisement->activeAdvertCellId = cellId;" in bridge_set_active_block
	assert "advertisement->activatedAdvertCellId = 0;" in bridge_set_active_block
	assert "return CL_Steam_RegisterShader( defaultContent );" in bridge_shader_block
	assert "return CL_AdvertisementBridge_SetupUIAdvertCellShader( defaultContent, rect, cellId );" in ui_setup_block
	assert "return CL_AdvertisementBridge_SetupAdvertCellShader( defaultContent, rect, cellId );" in cg_setup_block
	assert "cl_webBridge.vtbl->setMapPath( &cl_webBridge, mapPath );" in map_path_block


def test_awesomium_surface_rebuild_and_mouse_mapping_reconstruct_browser_surface_space() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)

	rebuild_surface_block = _extract_function_block(
		cl_cgame, "static void QLWebView_RebuildSurfaceImage( void ) {"
	)
	map_cursor_block = _extract_function_block(
		cl_cgame, "static int QLWebView_MapCursorCoordinate( int coordinate, int sourceDimension, int targetDimension ) {"
	)
	mouse_block = _extract_function_block(
		cl_cgame, "static void QLWebView_InjectMouseMove( int x, int y ) {"
	)

	assert "contentWidth = cl_webHost.viewWidth;" in rebuild_surface_block
	assert "contentHeight = cl_webHost.viewHeight;" in rebuild_surface_block
	assert "cl_webHost.surfaceContentWidth = contentWidth;" in rebuild_surface_block
	assert "cl_webHost.surfaceContentHeight = contentHeight;" in rebuild_surface_block
	assert "cl_webHost.surfaceWidth = QLWebView_NextPowerOfTwo( contentWidth );" in rebuild_surface_block
	assert "cl_webHost.surfaceHeight = QLWebView_NextPowerOfTwo( contentHeight );" in rebuild_surface_block
	assert "cl_webHost.surfaceDirty = qtrue;" in rebuild_surface_block
	assert "QLWebView_UploadSurfaceImage();" in rebuild_surface_block
	assert "if ( targetDimension <= 0 ) {" in map_cursor_block
	assert "targetDimension = sourceDimension;" in map_cursor_block
	assert "clampedCoordinate = (int)( mappedCoordinate + 0.5 );" in map_cursor_block
	assert "QLWebView_MapCursorCoordinate( x, cl_webHost.viewWidth, cl_webHost.surfaceContentWidth )" in mouse_block
	assert "QLWebView_MapCursorCoordinate( y, cl_webHost.viewHeight, cl_webHost.surfaceContentHeight )" in mouse_block


def test_awesomium_runtime_bootstrap_and_surface_pump_reconstruct_retail_host_contract() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)

	resolve_session_block = _extract_function_block(
		cl_cgame, "static void CL_WebHost_ResolveSessionPath( char *buffer, size_t bufferSize ) {"
	)
	register_sources_block = _extract_function_block(
		cl_cgame, "static void QLWebHost_RegisterRuntimeSources( void ) {"
	)
	wait_bootstrap_block = _extract_function_block(
		cl_cgame, "static qboolean QLWebHost_WaitForBootstrapReady( void ) {"
	)
	install_listeners_block = _extract_function_block(
		cl_cgame, "static void QLWebHost_InstallRuntimeListeners( void ) {"
	)
	upload_surface_block = _extract_function_block(
		cl_cgame, "static qboolean QLWebView_UploadSurfaceImage( void ) {"
	)
	write_surface_block = _extract_function_block(
		cl_cgame, "static qboolean QLWebView_WriteSurfacePixels( void ) {"
	)
	content_surface_block = _extract_function_block(
		cl_cgame, "static qboolean QLWebView_SurfaceHasUiContent( const byte *pixels, int surfaceWidth, int surfaceHeight, int contentWidth, int contentHeight ) {"
	)
	update_block = _extract_function_block(
		cl_cgame, "static void QLWebCore_Update( void ) {"
	)
	runtime_block = _extract_function_block(
		cl_cgame, "static qboolean QLWebHost_EnsureRuntime( void ) {"
	)
	pump_block = _extract_function_block(
		cl_cgame, "static void QLWebHost_PumpFrame( void ) {"
	)
	draw_block = _extract_function_block(
		cl_cgame, "void CL_WebHost_DrawBrowserSurface( void ) {"
	)
	drawable_block = _extract_function_block(
		cl_cgame, "qboolean CL_WebHost_HasDrawableSurface( void ) {"
	)
	surface_ready_block = _extract_function_block(
		cl_cgame, "static qboolean CL_WebHost_SurfaceReadyForOverlay( qboolean requireShader ) {"
	)
	live_failure_block = _extract_function_block(
		cl_cgame, "static void CL_WebHost_CheckLiveAwesomiumSurfaceFailure( void ) {"
	)
	live_view_block = _extract_function_block(
		cl_cgame, "qboolean CL_WebHost_HasLiveView( void ) {"
	)
	frame_block = _extract_function_block(
		cl_cgame, "void CL_WebHost_Frame( void ) {"
	)

	assert '#define CL_WEB_RETAIL_SURFACE_IMAGE "browser"' in cl_cgame
	assert '#define CL_WEB_SURFACE_IMAGE "*ql_web_browser"' in cl_cgame
	assert '#define CL_WEB_SURFACE_SHADER "browserShader"' in cl_cgame
	assert "#define CL_WEB_BOOTSTRAP_MAX_ATTEMPTS 10" in cl_cgame
	assert "#define CL_WEB_BOOTSTRAP_SLEEP_MSEC 100" in cl_cgame
	assert "#define CL_WEB_LIVE_SURFACE_FAILURE_FRAMES 180" in cl_cgame
	assert 'Cvar_VariableStringBuffer( "fs_homepath", buffer, bufferSize );' in resolve_session_block
	assert 'Q_strncpyz( buffer, ".", bufferSize );' in resolve_session_block
	assert "cl_webHost.dataPakSourceInstalled = qtrue;" in register_sources_block
	assert "cl_webHost.steamDataSourceInstalled = qtrue;" in register_sources_block
	assert "cl_webHost.resourceInterceptorInstalled = qtrue;" in register_sources_block
	assert "for ( attempt = 0; attempt < CL_WEB_BOOTSTRAP_MAX_ATTEMPTS; attempt++ ) {" in wait_bootstrap_block
	assert "cl_webHost.bootstrapAttemptCount = attempt + 1;" in wait_bootstrap_block
	assert "NET_Sleep( CL_WEB_BOOTSTRAP_SLEEP_MSEC );" in wait_bootstrap_block
	assert "cl_webHost.bootstrapReady = qtrue;" in wait_bootstrap_block
	assert "cl_webHost.dialogHandlerInstalled = qtrue;" in install_listeners_block
	assert "cl_webHost.viewHandlerInstalled = qtrue;" in install_listeners_block
	assert "cl_webHost.loadHandlerInstalled = qtrue;" in install_listeners_block
	assert "QLWebHost_RegisterRuntimeSources();" in runtime_block
	assert "cl_webHost.jsMethodHandlerInstalled = qtrue;" in runtime_block
	assert "if ( !QLWebHost_WaitForBootstrapReady() ) {" in runtime_block
	assert "QLWebHost_InstallRuntimeListeners();" in runtime_block
	assert "char\t\tsurfaceImageName[MAX_QPATH];" in cl_cgame
	assert "qboolean\tsurfaceHasUiContent;" in cl_cgame
	assert "int\t\t\tliveSurfaceMissingFrames;" in cl_cgame
	assert 'Q_strncpyz( cl_webHost.surfaceImageName, CL_WEB_SURFACE_IMAGE, sizeof( cl_webHost.surfaceImageName ) );' in upload_surface_block
	assert 'Q_strncpyz( cl_webHost.surfaceShaderName, CL_WEB_SURFACE_SHADER, sizeof( cl_webHost.surfaceShaderName ) );' in upload_surface_block
	assert "cl_webHost.surfaceShader = CL_RegisterShaderFromRGBAWithImageName(" in upload_surface_block
	assert "cl_webHost.surfaceImageName," in upload_surface_block
	assert "cl_webHost.surfaceUploadWidth = cl_webHost.surfaceWidth;" in upload_surface_block
	assert "cl_webHost.surfaceUploadHeight = cl_webHost.surfaceHeight;" in upload_surface_block
	assert "cl_webHost.surfaceImageInitialised = qtrue;" in upload_surface_block
	assert "cl_webHost.surfaceDirty = qfalse;" in upload_surface_block
	assert "if ( copied ) {" in write_surface_block
	assert "cl_webHost.surfaceHasVisiblePixels = visible;" in write_surface_block
	assert "cl_webHost.surfaceHasUiContent = contentful;" in write_surface_block
	assert "cl_webHost.liveSurfaceMissingFrames = 0;" in write_surface_block
	assert "cl_webHost.liveSurfaceMissingFrames++;" in write_surface_block
	assert "QLWebView_SurfaceHasUiContent(" in write_surface_block
	assert "contentPixels >= 32 && contentPixels * 500 >= sampled" in content_surface_block
	assert "return qtrue;" in write_surface_block
	assert "if ( cl_webHost.liveAwesomium ) {" in update_block
	assert "if ( CL_Awesomium_SurfaceDirty() ) {" in update_block
	assert "return;" in update_block
	assert "if ( !cl_webHost.surfaceImageInitialised ) {" in pump_block
	assert "awesomiumWidth != cl_webHost.surfaceContentWidth" in pump_block
	assert "awesomiumHeight != cl_webHost.surfaceContentHeight" in pump_block
	assert "if ( cl_webHost.surfaceUploadWidth != cl_webHost.surfaceWidth || cl_webHost.surfaceUploadHeight != cl_webHost.surfaceHeight ) {" in pump_block
	assert "if ( cl_webHost.surfaceDirty ) {" in pump_block
	assert "QLWebView_UploadSurfaceImage();" in pump_block
	assert "QLWebView_UploadSurfaceImage();" not in draw_block
	assert "if ( !CL_WebHost_SurfaceReadyForOverlay( qtrue ) ) {" in draw_block
	assert "contentWidth = cl_webHost.surfaceContentWidth > 0 ? cl_webHost.surfaceContentWidth : cl_webHost.viewWidth;" in draw_block
	assert "contentHeight = cl_webHost.surfaceContentHeight > 0 ? cl_webHost.surfaceContentHeight : cl_webHost.viewHeight;" in draw_block
	assert "if ( !cl_webHost.surfaceShader ) {" in draw_block
	assert "return CL_WebHost_SurfaceReadyForOverlay( qtrue );" in drawable_block
	assert "if ( requireShader && !cl_webHost.surfaceShader ) {" in surface_ready_block
	assert "if ( !cl_webHost.surfaceHasVisiblePixels || !cl_webHost.surfaceHasUiContent ) {" in surface_ready_block
	assert "!cl_webHost.liveAwesomium || !cl_webHost.viewInitialised || !cl_webHost.browserVisible" in live_failure_block
	assert "cl_webHost.surfaceHasUiContent" in live_failure_block
	assert "cl_webHost.liveSurfaceMissingFrames < CL_WEB_LIVE_SURFACE_FAILURE_FRAMES" in live_failure_block
	assert 'Com_Printf( "Awesomium WebCore surface failed after %d frames' in live_failure_block
	assert "CL_WebHost_ResetRuntime( qtrue );" in live_failure_block
	assert "cl_webHost.loadFailed = qtrue;" in live_failure_block
	assert "CL_ResetBrowserOverlayState();" in live_failure_block
	assert "CL_RefreshOnlineServicesBridgeState();" in live_failure_block
	assert "return cl_webHost.viewInitialised && cl_webHost.bootstrapReady;" in live_view_block
	assert "CL_WebHost_CheckLiveAwesomiumSurfaceFailure();" in frame_block
	assert frame_block.find("QLWebHost_PumpFrame();") < frame_block.find("CL_WebHost_CheckLiveAwesomiumSurfaceFailure();")
	assert frame_block.find("CL_WebHost_CheckLiveAwesomiumSurfaceFailure();") < frame_block.find("CL_WebHost_UpdateOverlayOwnership();")


def test_awesomium_map_list_reconstructs_retail_arena_catalog() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)

	build_block = _extract_function_block(cl_cgame, "static void CL_WebHost_BuildMapListJson( char *buffer, size_t bufferSize ) {")
	parse_block = _extract_function_block(
		cl_cgame, "static void CL_WebHost_ParseArenaInfosToJson( char *data, char *buffer, size_t bufferSize, char seenMaps[][MAX_QPATH], int *entryCount ) {"
	)
	type_bits_block = _extract_function_block(
		cl_cgame, "static unsigned int CL_WebHost_ResolveMapTypeBits( const char *typeList ) {"
	)
	load_descriptors_block = _extract_function_block(
		cl_cgame, "static void CL_WebHost_LoadArenaDescriptors( clWebMapDescriptor_t *descriptors, int *descriptorCount ) {"
	)
	mappool_block = _extract_function_block(
		cl_cgame, "static qboolean CL_WebHost_BuildMapListJsonFromMapPool( char *buffer, size_t bufferSize, const clWebMapDescriptor_t *arenaDescriptors, int arenaDescriptorCount ) {"
	)
	fallback_block = _extract_function_block(
		cl_cgame, "static void CL_WebHost_BuildMapListJsonFromBSPScan( char *buffer, size_t bufferSize ) {"
	)

	assert "CL_WebHost_LoadArenaDescriptors( arenaDescriptors, &arenaDescriptorCount );" in build_block
	assert "CL_WebHost_BuildMapListJsonFromMapPool( buffer, bufferSize, arenaDescriptors, arenaDescriptorCount )" in build_block
	assert "CL_WebHost_BuildMapDescriptorJson( arenaDescriptors, arenaDescriptorCount, buffer, bufferSize );" in build_block
	assert 'CL_WebHost_AppendArenaDescriptorsFromFile( "scripts/arenas.txt", descriptors, descriptorCount );' in load_descriptors_block
	assert 'numdirs = FS_GetFileList( "scripts", ".arena", dirlist, sizeof( dirlist ) );' in load_descriptors_block
	assert 'Com_sprintf( filename, sizeof( filename ), "scripts/%s", dirptr );' in load_descriptors_block
	assert 'length = FS_ReadFile( "mappool.txt", &fileBuffer );' in mappool_block
	assert "CL_WebHost_LoadFactoryBasegtList( factoryBasegts, &factoryBasegtCount, CL_WEB_MAX_FACTORY_DEFINITIONS );" in mappool_block
	assert "CL_WebHost_ResolveMapPoolFactoryBits( factoryToken, factoryBasegts, factoryBasegtCount );" in mappool_block
	assert "CL_WebHost_RecordMapDescriptor( poolDescriptors, &poolDescriptorCount, mapToken, displayName, typeBits );" in mappool_block
	assert "CL_WEB_MAP_POOL_FILE_BYTES" in cl_cgame
	assert "CL_WebHost_SyncMapCatalogSnapshot" in cl_cgame
	assert "mapJson = (char *)Z_Malloc( CL_WEB_MAP_JSON_BUFFER_SIZE );" in cl_cgame
	assert "CL_WebHost_BuildMapListJson( mapJson, CL_WEB_MAP_JSON_BUFFER_SIZE );" in cl_cgame
	assert "CL_WebHost_ExecuteMapCatalogBatches( mapJson, mapJsonLength )" in cl_cgame
	assert "CL_WebHost_MapCatalogBridgeReady()" in cl_cgame
	assert "CL_Awesomium_ExecuteJavascriptInteger( script, \"\", &result ) && result != 0" in cl_cgame
	assert "window.__qlr_begin_native_maps" in cl_cgame
	assert "window.__qlr_add_native_maps" in cl_cgame
	assert "window.__qlr_commit_native_maps" in cl_cgame
	assert "CL_WEB_MAP_SYNC_CHUNK_CHARS" in cl_cgame
	assert 'Q_strcat( buffer, bufferSize, "\\",\\"maps\\":" );' not in cl_cgame
	assert "mapName = Info_ValueForKey( info, ARENA_INFO_KEY_MAP );" in parse_block
	assert "longName = Info_ValueForKey( info, ARENA_INFO_KEY_LONGNAME );" in parse_block
	assert "typeList = Info_ValueForKey( info, ARENA_INFO_KEY_TYPE );" in parse_block
	assert 'CL_WebHost_AppendMapDescriptorJson( mapName, longName, typeBits, buffer, bufferSize, entryCount );' in parse_block
	assert 'CL_WebHost_TypeStringContains( typeList, "duel" )' in type_bits_block
	assert 'CL_WebHost_TypeStringContains( typeList, "race" )' in type_bits_block
	assert 'CL_WebHost_TypeStringContains( typeList, "overload" )' in type_bits_block
	assert 'CL_WebHost_TypeStringContains( typeList, "hh" )' in type_bits_block
	assert 'CL_WebHost_TypeStringContains( typeList, "har" )' in type_bits_block
	assert 'CL_WebHost_TypeStringContains( typeList, "ft" )' in type_bits_block
	assert 'CL_WebHost_TypeStringContains( typeList, "dom" )' in type_bits_block
	assert 'CL_WebHost_TypeStringContains( typeList, "ad" )' in type_bits_block
	assert 'CL_WebHost_TypeStringContains( typeList, "rr" )' in type_bits_block
	assert "return typeBits ? typeBits" not in type_bits_block
	assert 'count = FS_GetFileList( "maps", ".bsp", fileList, sizeof( fileList ) );' in fallback_block


def test_awesomium_factory_list_reconstructs_retail_factory_catalog() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)

	build_block = _extract_function_block(cl_cgame, "static void CL_WebHost_BuildFactoryListJson( char *buffer, size_t bufferSize ) {")
	parse_definition_block = _extract_function_block(
		cl_cgame, "static qboolean CL_WebFactory_ParseDefinition( clWebFactoryParseState_t *state, clWebFactoryDefinition_t *definition ) {"
	)
	parse_settings_block = _extract_function_block(
		cl_cgame, "static qboolean CL_WebFactory_ParseSettingsObject( clWebFactoryParseState_t *state, char *buffer, size_t bufferSize ) {"
	)
	append_block = _extract_function_block(
		cl_cgame, "static void CL_WebHost_AppendFactoryDefinitionJson( const clWebFactoryDefinition_t *definition, char *buffer, size_t bufferSize, int *entryCount ) {"
	)

	assert 'CL_WebHost_AppendFactoryDefinitionsFromFile( "scripts/factories.txt", buffer, bufferSize, seenIds, &entryCount );' in build_block
	assert 'count = FS_GetFileList( "scripts", ".factories", fileList, sizeof( fileList ) );' in build_block
	assert 'count = FS_GetFileList( "scripts", ".factory", fileList, sizeof( fileList ) );' in build_block
	assert 'if ( !Q_stricmp( key, "author" ) ) {' in parse_definition_block
	assert 'if ( !Q_stricmp( key, "description" ) ) {' in parse_definition_block
	assert 'if ( *state->cursor == \'"\' ) {' in parse_definition_block
	assert "if ( state->cursor == '\"' ) {" not in parse_definition_block
	assert 'if ( !Q_stricmp( key, "basegt" ) ) {' in parse_definition_block
	assert 'if ( !Q_stricmp( key, "cvars" ) ) {' in parse_definition_block
	assert "qboolean sawTitle;" in parse_definition_block
	assert "qboolean sawCvars;" in parse_definition_block
	assert "sawTitle = qtrue;" in parse_definition_block
	assert "sawCvars = qtrue;" in parse_definition_block
	assert 'Q_strncpyz( definition->title, definition->id, sizeof( definition->title ) );' not in parse_definition_block
	assert 'Q_strlwr( loweredKey );' in parse_settings_block
	assert 'if ( *state->cursor == \',\' ) {' in parse_settings_block
	assert 'if ( state->cursor < state->end && *state->cursor == \'}\' ) {' in parse_settings_block
	assert 'Q_strcat( buffer, bufferSize, ",\\"settings\\":" );' in append_block
	assert 'CL_WebHost_AppendJsonEscaped( buffer, bufferSize, definition->basegt );' in append_block
	assert '",\\"basegt\\":\\"\\",\\"settings\\":{}}' not in cl_cgame
