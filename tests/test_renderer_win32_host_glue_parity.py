from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WIN_GLIMP = REPO_ROOT / "src/code/win32/win_glimp.c"
WIN_MAIN = REPO_ROOT / "src/code/win32/win_main.c"
WIN_MANIFEST = REPO_ROOT / "src/code/win32/quakelive_steam.manifest"
WIN_SYSCON = REPO_ROOT / "src/code/win32/win_syscon.c"
WIN_WNDPROC = REPO_ROOT / "src/code/win32/win_wndproc.c"


def test_windowed_resize_restart_helper_matches_retail_message_flow() -> None:
	win_wndproc = WIN_WNDPROC.read_text()

	assert "WIN_SyncWindowedModeFromClientRect" in win_wndproc
	assert 'Cvar_SetValue( "r_windowedMode", -1 );' in win_wndproc
	assert 'Cvar_SetValue( "r_windowedWidth", rect.right );' in win_wndproc
	assert 'Cvar_SetValue( "r_windowedHeight", rect.bottom );' in win_wndproc
	assert 'Cbuf_AddText( "vid_restart fast\\n" );' in win_wndproc
	assert "case WM_SIZE:" in win_wndproc
	assert "case WM_SIZING:" in win_wndproc
	assert "case WM_EXITSIZEMOVE:" in win_wndproc
	assert "case WM_SYSCOMMAND:" in win_wndproc
	assert "s_pendingWindowedModeSync = qtrue;" in win_wndproc
	assert "g_wv.isMaximized = (qboolean)( wParam == SIZE_MAXIMIZED );" in win_wndproc
	assert "wParam == SC_RESTORE || wParam == SC_MAXIMIZE || wParam == 0xF122" in win_wndproc
	assert "wParam & 0xFFF0" not in win_wndproc


def test_shared_loading_window_wrappers_and_startup_order_are_present() -> None:
	win_syscon = WIN_SYSCON.read_text()
	win_main = WIN_MAIN.read_text()

	assert "void Sys_CreateLoadingWindow( void )" in win_syscon
	assert "void Sys_DestroyLoadingWindow( void )" in win_syscon
	assert '#define LOADING_WINDOW_TITLE\t"Loading Quake Live"' in win_syscon
	assert 'LoadImage( NULL, "splash.bmp", IMAGE_BITMAP, 0, 0, LR_LOADFROMFILE )' in win_syscon
	assert 'CONSOLE_WINDOW_CLASS,' in win_syscon
	assert 'LOADING_WINDOW_TITLE,' in win_syscon

	enable_dpi = win_main.index("Sys_EnableDpiAwareness();")
	create_loading = win_main.index("Sys_CreateLoadingWindow();")
	create_console = win_main.index("Sys_CreateConsole();")
	set_error_mode = win_main.index("SetErrorMode( SEM_FAILCRITICALERRORS );")
	destroy_loading = win_main.index("Sys_DestroyLoadingWindow();")
	com_init = win_main.index("Com_Init( sys_cmdline );")

	assert enable_dpi < create_loading < create_console < set_error_mode < destroy_loading < com_init


def test_windows_dpi_awareness_is_enabled_before_hwnd_creation() -> None:
	win_glimp = WIN_GLIMP.read_text()
	win_main = WIN_MAIN.read_text()
	win_manifest = WIN_MANIFEST.read_text()
	win_wndproc = WIN_WNDPROC.read_text()

	assert "DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2" in win_main
	assert "SetProcessDpiAwarenessContext" in win_main
	assert "SetProcessDPIAware" in win_main
	assert win_main.index("Sys_EnableDpiAwareness();") < win_main.index("Sys_CreateLoadingWindow();")
	assert '<dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true/pm</dpiAware>' in win_manifest
	assert '<dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2, PerMonitor</dpiAwareness>' in win_manifest
	assert "case WM_DPICHANGED:" in win_wndproc
	assert "SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED" in win_wndproc
	assert "SWP_FRAMECHANGED | SWP_SHOWWINDOW" in win_glimp
	assert "SWP_NOSENDCHANGING | SWP_FRAMECHANGED | SWP_SHOWWINDOW" in win_glimp


def test_fast_restart_preserves_windowed_maximize_state() -> None:
	win_glimp = WIN_GLIMP.read_text()

	assert "if ( g_wv.isMaximized ) {" in win_glimp
	assert "windowStyle |= WS_MAXIMIZE;" in win_glimp
	assert "AdjustWindowRect( &rect, windowStyle, FALSE );" in win_glimp


def test_windowed_size_cvars_can_expand_existing_windows() -> None:
	win_glimp = WIN_GLIMP.read_text()

	assert "if ( !r_fullscreen->integer && g_wv.isMaximized && GetClientRect( g_wv.hWnd, &rect ) )" in win_glimp
	assert "if ( !r_fullscreen->integer && GetClientRect( g_wv.hWnd, &rect ) )" not in win_glimp
	assert "width = rect.right;" in win_glimp
	assert "height = rect.bottom;" in win_glimp


def test_mode_switches_publish_retail_aspect_ratio_presets() -> None:
	win_glimp = WIN_GLIMP.read_text()

	assert "static qboolean GLW_GetModeInfo( int *width, int *height, int *aspectRatio, int mode, qboolean fullscreen )" in win_glimp
	assert "if ( mode != -2 )" in win_glimp
	assert "return R_GetModeInfo( width, height, aspectRatio, mode, fullscreen );" in win_glimp
	assert "if ( devmode.dmBitsPerPel == 32 && devmode.dmPelsWidth > bestWidth )" in win_glimp
	assert "*aspectRatio = R_GetModeAspectRatioPreset( *width, *height );" in win_glimp
	assert 'ri.Cvar_Set( "r_aspectRatio", "0" );' not in win_glimp
	assert 'ri.Cvar_Set( "r_aspectRatio", va( "%d", modeAspect ) );' in win_glimp


def test_icd_startup_retry_modes_match_retail_quake_live_safe_modes() -> None:
	win_glimp = WIN_GLIMP.read_text()
	load_block = win_glimp[
		win_glimp.index("static qboolean GLW_LoadOpenGL"):
		win_glimp.index("/*\n** GLimp_EndFrame")
	]

	assert "started = GLW_StartDriverAndSetMode( drivername, mode, r_colorbits->integer, cdsFullscreen );" in load_block
	assert "if ( !started && glConfig.driverType == GLDRV_ICD )" in load_block
	assert "started = GLW_StartDriverAndSetMode( drivername, 5, 16, qtrue );" in load_block
	assert "started = GLW_StartDriverAndSetMode( drivername, 12, 16, qtrue );" in load_block
	assert "glConfig.driverType == GLDRV_ICD ) && cdsFullscreen" not in load_block
	assert "r_colorbits->integer != 16" not in load_block
	assert "GLW_StartDriverAndSetMode( drivername, 3, 16, qtrue )" not in load_block
	assert "mode != 3" not in load_block


def test_win32_gl_start_driver_wrapper_keeps_retail_warning_contract() -> None:
	win_glimp = WIN_GLIMP.read_text()
	wrapper_block = win_glimp[
		win_glimp.index("static qboolean GLW_StartDriverAndSetMode"):
		win_glimp.index("/*\n** ChoosePFD")
	]

	assert "err = GLW_SetMode( drivername, mode, colorbits, cdsFullscreen );" in wrapper_block
	assert 'ri.Printf( PRINT_ALL, "...WARNING: fullscreen unavailable in this mode\\n" );' in wrapper_block
	assert 'ri.Printf( PRINT_ALL, "...WARNING: could not set the given mode (%d)\\n", mode );' in wrapper_block
	assert "default:\n\t\tbreak;\n\t}\n\treturn qtrue;" in wrapper_block


def test_win32_gl_startup_driver_retry_order_matches_retail() -> None:
	win_glimp = WIN_GLIMP.read_text()
	start_block = win_glimp[
		win_glimp.index("static void GLW_StartOpenGL"):
		win_glimp.index("/*\n** GLimp_Init")
	]

	initial = start_block.index("if ( !GLW_LoadOpenGL( r_glDriver->string ) )")
	mark_opengl32 = start_block.index("if ( !Q_stricmp( r_glDriver->string, OPENGL_DRIVER_NAME ) )")
	mark_3dfx = start_block.index("else if ( !Q_stricmp( r_glDriver->string, _3DFX_DRIVER_NAME ) )")
	try_3dfx = start_block.index("if ( GLW_LoadOpenGL( _3DFX_DRIVER_NAME ) )")
	set_3dfx = start_block.index('ri.Cvar_Set( "r_glDriver", _3DFX_DRIVER_NAME );')
	try_opengl_after_custom = start_block.index("if ( !GLW_LoadOpenGL( OPENGL_DRIVER_NAME ) )")
	try_opengl_after_3dfx = start_block.rindex("if ( GLW_LoadOpenGL( OPENGL_DRIVER_NAME ) )")
	set_opengl = start_block.rindex('ri.Cvar_Set( "r_glDriver", OPENGL_DRIVER_NAME );')

	assert initial < mark_opengl32 < mark_3dfx < try_3dfx < set_3dfx < try_opengl_after_custom
	assert mark_3dfx < try_opengl_after_3dfx < set_opengl
	assert start_block.count('ri.Error( ERR_FATAL, "GLW_StartOpenGL() - could not load OpenGL subsystem\\n" );') == 3


def test_glimp_init_keeps_retail_direct_gl_string_copy_after_startup() -> None:
	win_glimp = WIN_GLIMP.read_text()
	init_block = win_glimp[win_glimp.index("void GLimp_Init( void )"):win_glimp.index("/*\n** GLimp_Shutdown")]

	startup = init_block.index("GLW_StartOpenGL();")
	copy_vendor = init_block.index("Q_strncpyz( glConfig.vendor_string, qglGetString (GL_VENDOR), sizeof( glConfig.vendor_string ) );")
	copy_renderer = init_block.index("Q_strncpyz( glConfig.renderer_string, qglGetString (GL_RENDERER), sizeof( glConfig.renderer_string ) );")
	copy_version = init_block.index("Q_strncpyz( glConfig.version_string, qglGetString (GL_VERSION), sizeof( glConfig.version_string ) );")
	copy_extensions = init_block.index("Q_strncpyz( glConfig.extensions_string, qglGetString (GL_EXTENSIONS), sizeof( glConfig.extensions_string ) );")

	assert startup < copy_vendor < copy_renderer < copy_version < copy_extensions
	assert "vendorString" not in init_block
	assert "rendererString" not in init_block
	assert "versionString" not in init_block
	assert "extensionsString" not in init_block


def test_pfd_auto_select_restores_retail_icd_and_wgl_owner_split() -> None:
	win_glimp = WIN_GLIMP.read_text()

	assert 'ri.Cvar_Set( "r_textureMode", "GL_LINEAR_MIPMAP_LINEAR" );' in win_glimp
	assert 'ri.Cvar_Set( "r_texturemode", "GL_LINEAR_MIPMAP_LINEAR" );' not in win_glimp
	assert 'ri.Printf( PRINT_ALL, "...GLW_AutoSelectPFD( %d, %d, %d )\\n", ( int ) pPFD->cColorBits, ( int ) pPFD->cDepthBits, ( int ) pPFD->cStencilBits );' in win_glimp
	assert "useQWGL = (qboolean)( glConfig.driverType > GLDRV_ICD );" in win_glimp
	assert "autoPFD = GLW_ChoosePixelFormatSafe( hDC, pPFD, qtrue );" in win_glimp
	assert "autoPFD = GLW_ChoosePixelFormatSafe( hDC, pPFD, qfalse );" in win_glimp
	assert "result = qwglChoosePixelFormat ? qwglChoosePixelFormat( hDC, pPFD ) : 0;" in win_glimp
	assert "result = ChoosePixelFormat( hDC, pPFD );" in win_glimp


def test_pfd_enumeration_uses_retail_gdi_vs_wgl_describe_owner() -> None:
	win_glimp = WIN_GLIMP.read_text()

	assert "result = qwglDescribePixelFormat ? qwglDescribePixelFormat( hDC, index, bytes, pfd ) : 0;" in win_glimp
	assert "result = DescribePixelFormat( hDC, index, bytes, pfd );" in win_glimp
	assert "maxPFD = GLW_DescribePixelFormatSafe( hDC, 1, sizeof( PIXELFORMATDESCRIPTOR ), &pfds[0], useQWGL );" in win_glimp
	assert "if ( !GLW_DescribePixelFormatSafe( hDC, i, sizeof( PIXELFORMATDESCRIPTOR ), &pfds[i], useQWGL ) )" in win_glimp
	assert "if ( !GLW_DescribePixelFormatSafe( glw_state.hDC, pixelformat, sizeof( *pPFD ), pPFD, glConfig.driverType > GLDRV_ICD ) )" in win_glimp
