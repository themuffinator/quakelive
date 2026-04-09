from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WIN_GLIMP = REPO_ROOT / "src/code/win32/win_glimp.c"
WIN_MAIN = REPO_ROOT / "src/code/win32/win_main.c"
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


def test_shared_loading_window_wrappers_and_startup_order_are_present() -> None:
	win_syscon = WIN_SYSCON.read_text()
	win_main = WIN_MAIN.read_text()

	assert "void Sys_CreateLoadingWindow( void )" in win_syscon
	assert "void Sys_DestroyLoadingWindow( void )" in win_syscon
	assert '#define LOADING_WINDOW_TITLE\t"Loading Quake Live"' in win_syscon
	assert 'LoadImage( NULL, "splash.bmp", IMAGE_BITMAP, 0, 0, LR_LOADFROMFILE )' in win_syscon
	assert 'CONSOLE_WINDOW_CLASS,' in win_syscon
	assert 'LOADING_WINDOW_TITLE,' in win_syscon

	create_loading = win_main.index("Sys_CreateLoadingWindow();")
	create_console = win_main.index("Sys_CreateConsole();")
	set_error_mode = win_main.index("SetErrorMode( SEM_FAILCRITICALERRORS );")
	destroy_loading = win_main.index("Sys_DestroyLoadingWindow();")
	com_init = win_main.index("Com_Init( sys_cmdline );")

	assert create_loading < create_console < set_error_mode < destroy_loading < com_init


def test_fast_restart_preserves_windowed_maximize_state() -> None:
	win_glimp = WIN_GLIMP.read_text()

	assert "if ( g_wv.isMaximized ) {" in win_glimp
	assert "windowStyle |= WS_MAXIMIZE;" in win_glimp
	assert "AdjustWindowRect( &rect, windowStyle, FALSE );" in win_glimp
