from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CL_CGAME_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
CL_INPUT_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_input.c"
CL_KEYS_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_keys.c"
CL_MAIN_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_main.c"
CLIENT_H_PATH = REPO_ROOT / "src" / "code" / "client" / "client.h"
WIN_WNDPROC_PATH = REPO_ROOT / "src" / "code" / "win32" / "win_wndproc.c"


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
	set_hash_block = _extract_function_block(cl_cgame, "static void QLWebView_SetLocationHash( const char *hash ) {")

	assert "while ( *cursor == '#'" in normalize_block
	assert "CL_WebHost_NormalizeHash( hash, normalizedHash, sizeof( normalizedHash ) );" in build_url_block
	assert "Com_sprintf( buffer, bufferSize, \"%s#%s\", CL_WEB_DEFAULT_URL, normalizedHash );" in build_url_block
	assert "CL_WebHost_NormalizeHash( hash, cl_webBrowserHash, sizeof( cl_webBrowserHash ) );" in show_browser_block
	assert "CL_WebHost_NormalizeHash( hash, cl_webBrowserHash, sizeof( cl_webBrowserHash ) );" in change_hash_block
	assert "CL_WebHost_NormalizeHash( hash, cl_webHost.pendingHash, sizeof( cl_webHost.pendingHash ) );" in set_hash_block


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
	assert 'Cvar_Get ("web_console", "0", CVAR_ARCHIVE );' in register_block
	assert 'Q_strncpyz( cl_webHost.tooltip, tooltip ? tooltip : "", sizeof( cl_webHost.tooltip ) );' in tooltip_block
	assert 'Com_sprintf( payload, sizeof( payload ), "{\\"tooltip\\":\\"%s\\"}", escapedTooltip );' in tooltip_block
	assert 'CL_WebView_PublishEvent( "web.tooltip", payload );' in tooltip_block
	assert 'if ( !Cvar_VariableIntegerValue( "web_console" ) ) {' in console_block
	assert 'Com_Printf( "%s:%i: %s\\n", source ? source : "", line, message ? message : "" );' in console_block
	assert 'QLViewHandler_OnChangeTooltip( "" );' in hide_browser_block


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
	hide_browser_block = _extract_function_block(cl_cgame, "static void QLWebHost_HideBrowser( void ) {")
	update_block = _extract_function_block(cl_cgame, "static void QLWebCore_Update( void ) {")
	show_error_block = _extract_function_block(cl_cgame, "void CL_Web_ShowError_f( void ) {")
	clear_cache_block = _extract_function_block(cl_cgame, "void CL_Web_ClearCache_f( void ) {")
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
	assert "if ( cl_webHost.browserActive && !( cls.keyCatchers & KEYCATCH_BROWSER ) ) {" in update_block
	assert "cls.keyCatchers |= KEYCATCH_BROWSER;" in update_block
	assert "VM_Call( cgvm, CG_EVENT_HANDLING, CGAME_EVENT_CLOSECOMMANDOVERLAY );" in hide_browser_block

	assert 'Cvar_Set( "web_browserActive", cl_webHost.browserActive ? "1" : "0" );' not in show_browser_block
	assert 'Cvar_Set( "web_browserActive", cl_webHost.browserActive ? "1" : "0" );' not in change_hash_block
	assert 'const char *message = ( Cmd_Argc() > 1 ) ? Cmd_Argv( 1 ) : "";' in show_error_block
	assert "CL_WebView_PublishGameError( message );" in show_error_block
	assert "QLWebHost_NavigateOrOpen( cl_webBrowserHash );" not in show_error_block
	assert 'if ( !cl_webHost.sessionInitialised ) {' in clear_cache_block
	assert "CL_Web_ClearSessionState();" in clear_cache_block
	assert 'cl_webHost.refreshStopped = qfalse;' in reload_view_block
	assert "(void)ignoreCache;" in reload_view_block
	assert "CL_WebHost_PrimeLauncherDocument( cl_webHost.currentUrl )" in reload_view_block
	assert "QLLoadHandler_OnFailLoadingFrame( cl_webHost.currentUrl );" in reload_view_block
	assert "QLWebHost_ReloadView( qtrue );" in reload_block
	assert 'Cvar_Set( "web_browserActive", cl_webHost.browserActive ? "1" : "0" );' not in reload_block
	assert 'Cvar_Set( "web_browserActive", cl_webHost.browserActive ? "1" : "0" );' in frame_block


def test_awesomium_direct_input_helpers_reconstruct_browser_runtime_injection_surface() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_input = _read_text(CL_INPUT_PATH)
	client_h = _read_text(CLIENT_H_PATH)

	next_power_block = _extract_function_block(
		cl_cgame, "static int QLWebView_NextPowerOfTwo( int value ) {"
	)
	map_cursor_block = _extract_function_block(
		cl_cgame, "static int QLWebView_MapCursorCoordinate( int coordinate, int viewDimension, int surfaceDimension ) {"
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
	mouse_event_block = _extract_function_block(cl_input, "void CL_MouseEvent( int dx, int dy, int time ) {")

	assert "void CL_WebView_OnMouseMove( int x, int y );" in client_h
	assert "#define KEYCATCH_RETAIL_MOUSEPASS\t0x0010" in client_h
	assert "#define KEYCATCH_BROWSER\t\t\t0x0020" in client_h
	assert "if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {" in inject_mouse_block
	assert "for ( result = 1; result < value; result <<= 1 ) {" in next_power_block
	assert "mappedCoordinate = ( (double)clampedCoordinate / (double)viewDimension ) * (double)targetDimension;" in map_cursor_block
	assert "cl_webHost.cursorX = cursorX;" in inject_mapped_mouse_block
	assert "cl_webHost.cursorY = cursorY;" in inject_mapped_mouse_block
	assert "cl_webHost.cursorPositionValid = qtrue;" in inject_mapped_mouse_block
	assert "QLWebView_InjectMappedMouseMove(" in inject_mouse_block
	assert "QLWebView_MapCursorCoordinate( x, cl_webHost.viewWidth, cl_webHost.surfaceWidth )" in inject_mouse_block
	assert "QLWebView_MapCursorCoordinate( y, cl_webHost.viewHeight, cl_webHost.surfaceHeight )" in inject_mouse_block
	assert "if ( !down && cl_webHost.keyCaptureArmed ) {" in inject_keyboard_block
	assert "QLWebView_PublishGameKey( key );" in inject_keyboard_block
	assert "cl_webHost.keyCaptureArmed = qfalse;" in inject_keyboard_block
	assert "QLWebView_InjectMouseMove( x, y );" in on_mouse_block
	assert "QLWebView_InjectKeyboardEvent( key, down );" in on_key_block
	assert "if ( cl_webHost.cursorPositionValid && cl_webHost.viewInitialised && ( cl_webHost.browserVisible || cl_webHost.browserActive ) ) {" in request_cursor_block
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
	notify_block = _extract_function_block(
		cl_cgame, "void CL_WebHost_NotifyAppActivation( qboolean active ) {"
	)
	activate_block = _extract_function_block(
		win_wndproc, "static void VID_AppActivate(BOOL fActive, BOOL minimize)"
	)

	assert "void CL_WebHost_NotifyAppActivation( qboolean active );" in client_h
	assert "if ( !cl_webHost.viewInitialised ) {" in inject_activation_block
	assert "QLWebView_InjectKeyboardEvent( 0x11, qtrue );" in inject_activation_block
	assert "if ( !active ) {" in notify_block
	assert "cl_webHost.focused = qfalse;" in notify_block
	assert "QLWebView_InjectActivationKeyboardEvent();" in notify_block
	assert "SetFocus( g_wv.hWnd );" in activate_block
	assert "CL_WebHost_NotifyAppActivation( qtrue );" in activate_block
	assert "CL_WebHost_NotifyAppActivation( qfalse );" in activate_block


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
	assert "if ( cls.keyCatchers & KEYCATCH_BROWSER ) {" in key_event_block
	assert "CL_WebHost_HideBrowser();" in key_event_block
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
	assert 'count = CL_WebPak_GetFileList( "js", ".js", fileList, sizeof( fileList ) );' in load_scripts_block
	assert 'Com_sprintf( scriptPath, sizeof( scriptPath ), "js/%s", cursor );' in load_scripts_block
	assert "CL_LauncherRequestData( scriptPath, &scriptBuffer, &scriptLength )" in load_scripts_block
	assert "Z_Free( scriptBuffer );" in load_scripts_block
	assert "QLLoadHandler_LoadDocumentScripts();" in document_ready_block
	assert "QLJSHandler_BindQzInstance();" in document_ready_block
	assert "sourceCount = FS_GetPakFileList( cl_webPak, path, extension, sourceList, sizeof( sourceList ) );" in webpak_list_block
	assert "sourceCount = CL_WebDataPak_GetFileList( path, extension, sourceList, sizeof( sourceList ) );" in webpak_list_block
	assert "sourceCount = FS_GetFileList( path, extension, sourceList, sizeof( sourceList ) );" in webpak_list_block
	assert "nFiles = FS_AddFileToList( name + temp, list, nFiles );" in pak_list_block


def test_awesomium_surface_rebuild_and_mouse_mapping_reconstruct_browser_surface_space() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)

	rebuild_surface_block = _extract_function_block(
		cl_cgame, "static void QLWebView_RebuildSurfaceImage( void ) {"
	)
	map_cursor_block = _extract_function_block(
		cl_cgame, "static int QLWebView_MapCursorCoordinate( int coordinate, int viewDimension, int surfaceDimension ) {"
	)
	mouse_block = _extract_function_block(
		cl_cgame, "static void QLWebView_InjectMouseMove( int x, int y ) {"
	)

	assert "cl_webHost.surfaceWidth = QLWebView_NextPowerOfTwo( cl_webHost.viewWidth );" in rebuild_surface_block
	assert "cl_webHost.surfaceHeight = QLWebView_NextPowerOfTwo( cl_webHost.viewHeight );" in rebuild_surface_block
	assert "cl_webHost.surfaceDirty = qtrue;" in rebuild_surface_block
	assert "QLWebView_UploadSurfaceImage();" in rebuild_surface_block
	assert "targetDimension = surfaceDimension > 0 ? surfaceDimension : viewDimension;" in map_cursor_block
	assert "clampedCoordinate = (int)( mappedCoordinate + 0.5 );" in map_cursor_block
	assert "QLWebView_MapCursorCoordinate( x, cl_webHost.viewWidth, cl_webHost.surfaceWidth )" in mouse_block
	assert "QLWebView_MapCursorCoordinate( y, cl_webHost.viewHeight, cl_webHost.surfaceHeight )" in mouse_block


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
	runtime_block = _extract_function_block(
		cl_cgame, "static qboolean QLWebHost_EnsureRuntime( void ) {"
	)
	pump_block = _extract_function_block(
		cl_cgame, "static void QLWebHost_PumpFrame( void ) {"
	)
	live_view_block = _extract_function_block(
		cl_cgame, "qboolean CL_WebHost_HasLiveView( void ) {"
	)

	assert '#define CL_WEB_SURFACE_SHADER "browser"' in cl_cgame
	assert "#define CL_WEB_BOOTSTRAP_MAX_ATTEMPTS 10" in cl_cgame
	assert "#define CL_WEB_BOOTSTRAP_SLEEP_MSEC 100" in cl_cgame
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
	assert 'Q_strncpyz( cl_webHost.surfaceShaderName, CL_WEB_SURFACE_SHADER, sizeof( cl_webHost.surfaceShaderName ) );' in upload_surface_block
	assert "cl_webHost.surfaceShader = CL_RegisterShaderFromRGBA(" in upload_surface_block
	assert "cl_webHost.surfaceUploadWidth = cl_webHost.surfaceWidth;" in upload_surface_block
	assert "cl_webHost.surfaceUploadHeight = cl_webHost.surfaceHeight;" in upload_surface_block
	assert "cl_webHost.surfaceImageInitialised = qtrue;" in upload_surface_block
	assert "cl_webHost.surfaceDirty = qfalse;" in upload_surface_block
	assert "if ( !cl_webHost.surfaceImageInitialised ) {" in pump_block
	assert "if ( cl_webHost.surfaceUploadWidth != cl_webHost.surfaceWidth || cl_webHost.surfaceUploadHeight != cl_webHost.surfaceHeight ) {" in pump_block
	assert "if ( cl_webHost.surfaceDirty ) {" in pump_block
	assert "return cl_webHost.viewInitialised && cl_webHost.bootstrapReady;" in live_view_block


def test_awesomium_map_list_reconstructs_retail_arena_catalog() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)

	build_block = _extract_function_block(cl_cgame, "static void CL_WebHost_BuildMapListJson( char *buffer, size_t bufferSize ) {")
	parse_block = _extract_function_block(
		cl_cgame, "static void CL_WebHost_ParseArenaInfosToJson( char *data, char *buffer, size_t bufferSize, char seenMaps[][MAX_QPATH], int *entryCount ) {"
	)
	type_bits_block = _extract_function_block(
		cl_cgame, "static unsigned int CL_WebHost_ResolveMapTypeBits( const char *typeList ) {"
	)
	fallback_block = _extract_function_block(
		cl_cgame, "static void CL_WebHost_BuildMapListJsonFromBSPScan( char *buffer, size_t bufferSize ) {"
	)

	assert 'CL_WebHost_AppendArenasFromFile( "scripts/arenas.txt", buffer, bufferSize, seenMaps, &entryCount );' in build_block
	assert 'numdirs = FS_GetFileList( "scripts", ".arena", dirlist, sizeof( dirlist ) );' in build_block
	assert 'Com_sprintf( filename, sizeof( filename ), "scripts/%s", dirptr );' in build_block
	assert 'mapName = Info_ValueForKey( info, "map" );' in parse_block
	assert 'longName = Info_ValueForKey( info, "longname" );' in parse_block
	assert 'typeList = Info_ValueForKey( info, "type" );' in parse_block
	assert 'CL_WebHost_AppendMapDescriptorJson( mapName, longName, typeBits, buffer, bufferSize, entryCount );' in parse_block
	assert 'CL_WebHost_TypeStringHasToken( typeList, "duel" )' in type_bits_block
	assert 'CL_WebHost_TypeStringHasToken( typeList, "race" )' in type_bits_block
	assert 'CL_WebHost_TypeStringHasToken( typeList, "dom" )' in type_bits_block
	assert 'CL_WebHost_TypeStringHasToken( typeList, "rr" )' in type_bits_block
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
