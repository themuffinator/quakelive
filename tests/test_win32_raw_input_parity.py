from __future__ import annotations

import ctypes
import json
import os
import re
from pathlib import Path

import pytest

from tests.compiler_support import compile_c_binary, find_c_compiler, shared_library_name

REPO_ROOT = Path(__file__).resolve().parent.parent
WIN_INPUT = REPO_ROOT / "src" / "code" / "win32" / "win_input.c"
WIN_GLIMP = REPO_ROOT / "src" / "code" / "win32" / "win_glimp.c"
WIN_LOCAL = REPO_ROOT / "src" / "code" / "win32" / "win_local.h"
WIN_MAIN = REPO_ROOT / "src" / "code" / "win32" / "win_main.c"
WIN_WNDPROC = REPO_ROOT / "src" / "code" / "win32" / "win_wndproc.c"
CL_INPUT = REPO_ROOT / "src" / "code" / "client" / "cl_input.c"
CL_KEYS = REPO_ROOT / "src" / "code" / "client" / "cl_keys.c"
COMMON = REPO_ROOT / "src" / "code" / "qcommon" / "common.c"
UI_MAIN = REPO_ROOT / "src" / "code" / "ui" / "ui_main.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
KEYCODES = REPO_ROOT / "src" / "code" / "ui" / "keycodes.h"
ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
GHIDRA_FUNCTIONS = REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "quakelive_steam" / "functions.csv"
GHIDRA_IMPORTS = REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "quakelive_steam" / "imports.txt"
CGAME_GHIDRA_FUNCTIONS = REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "cgamex86" / "functions.csv"
HLIL_PART04 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part04.txt"
)
HLIL_PART05 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part05.txt"
)
UI_HLIL_PART01 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "uix86.all"
	/ "uix86.dll_hlil_split"
	/ "uix86.dll_hlil_part01.txt"
)
CGAME_HLIL = REPO_ROOT / "references" / "hlil" / "quakelive" / "cgamex86.dll" / "cgamex86.dll_hlil.txt"

RIDEV_REMOVE = 0x00000001

RI_MOUSE_BUTTON_1_DOWN = 0x0001
RI_MOUSE_BUTTON_1_UP = 0x0002
RI_MOUSE_BUTTON_2_DOWN = 0x0004
RI_MOUSE_BUTTON_4_DOWN = 0x0040
RI_MOUSE_BUTTON_5_UP = 0x0200
RI_MOUSE_WHEEL = 0x0400
WHEEL_DELTA = 120

# Retail command-owner evidence for this console-facing raw-input slice comes
# from `references/analysis/quakelive_symbol_aliases.json` plus the paired HLIL
# owner in `references/hlil/quakelive/quakelive_steam.exe/`:
# `sub_4EAB90` -> `ListInputDevices_f`
# `sub_4ED3E0` -> `Sys_In_Restart_f`


class RawInputDevice(ctypes.Structure):
	_fields_ = [
		("usUsagePage", ctypes.c_ushort),
		("usUsage", ctypes.c_ushort),
		("dwFlags", ctypes.c_ulong),
		("hwndTarget", ctypes.c_void_p),
	]


class RawMouseSample(ctypes.Structure):
	_fields_ = [
		("dx", ctypes.c_long),
		("dy", ctypes.c_long),
		("buttonFlags", ctypes.c_ushort),
		("wheelDelta", ctypes.c_short),
	]


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


def _parse_key_enum_values(keycodes: str) -> dict[str, int]:
	start = keycodes.index("typedef enum {")
	end = keycodes.index("} keyNum_t;", start)
	enum_body = keycodes[start:end]
	values: dict[str, int] = {}
	value = -1

	for line in enum_body.splitlines():
		match = re.search(r"\b(K_[A-Z0-9_]+)\s*(?:=\s*(\d+))?\s*,", line)
		if not match:
			continue

		if match.group(2) is not None:
			value = int(match.group(2))
		else:
			value += 1
		values[match.group(1)] = value

	return values


@pytest.fixture(scope="session")
def win_raw_input_harness(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	if os.name != "nt":
		pytest.skip("Win32 raw-input harness only applies on Windows")

	build_dir = tmp_path_factory.mktemp("win_raw_input_harness_build")
	lib_path = build_dir / shared_library_name("win_raw_input_harness")
	compiler = find_c_compiler()

	if compiler is None:
		pytest.skip("no supported C compiler is available for the Win32 raw-input harness")

	compile_c_binary(
		compiler,
		[
			REPO_ROOT / "tests" / "win_raw_input_harness.c",
		],
		lib_path,
		include_dirs=[
			REPO_ROOT / "src" / "code" / "win32",
		],
		shared=True,
		workdir=REPO_ROOT,
	)

	lib = ctypes.CDLL(str(lib_path))
	lib.QLR_WinRawInputBuildRegistration.argtypes = [
		ctypes.POINTER(RawInputDevice),
		ctypes.c_void_p,
		ctypes.c_int,
		ctypes.c_int,
	]
	lib.QLR_WinRawInputBuildRegistration.restype = None
	lib.QLR_WinRawInputExtractMouseSampleFromFields.argtypes = [
		ctypes.c_long,
		ctypes.c_long,
		ctypes.c_ushort,
		ctypes.c_ushort,
		ctypes.POINTER(RawMouseSample),
	]
	lib.QLR_WinRawInputExtractMouseSampleFromFields.restype = ctypes.c_int
	lib.QLR_WinRawInputTranslateButtonFlags.argtypes = [
		ctypes.c_ushort,
		ctypes.c_short,
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.c_int,
	]
	lib.QLR_WinRawInputTranslateButtonFlags.restype = ctypes.c_int
	lib.QLR_WinRawInputKeyMouse1.argtypes = []
	lib.QLR_WinRawInputKeyMouse1.restype = ctypes.c_int
	lib.QLR_WinRawInputKeyWheelDown.argtypes = []
	lib.QLR_WinRawInputKeyWheelDown.restype = ctypes.c_int
	lib.QLR_WinRawInputKeyWheelUp.argtypes = []
	lib.QLR_WinRawInputKeyWheelUp.restype = ctypes.c_int
	return lib


def test_raw_input_registration_defaults_to_mouse_usage_page_and_null_target(
	win_raw_input_harness: ctypes.CDLL,
) -> None:
	device = RawInputDevice()

	win_raw_input_harness.QLR_WinRawInputBuildRegistration(
		ctypes.byref(device),
		ctypes.c_void_p(0x1234),
		0,
		0,
	)

	assert device.usUsagePage == 1
	assert device.usUsage == 2
	assert device.dwFlags == 0
	assert not device.hwndTarget


def test_raw_input_registration_can_bind_the_window_handle(
	win_raw_input_harness: ctypes.CDLL,
) -> None:
	device = RawInputDevice()

	win_raw_input_harness.QLR_WinRawInputBuildRegistration(
		ctypes.byref(device),
		ctypes.c_void_p(0x1234),
		1,
		0,
	)

	assert device.usUsagePage == 1
	assert device.usUsage == 2
	assert device.dwFlags == 0
	assert device.hwndTarget == 0x1234


def test_raw_input_removal_uses_ridev_remove_and_clears_the_target(
	win_raw_input_harness: ctypes.CDLL,
) -> None:
	device = RawInputDevice()

	win_raw_input_harness.QLR_WinRawInputBuildRegistration(
		ctypes.byref(device),
		ctypes.c_void_p(0x1234),
		1,
		1,
	)

	assert device.usUsagePage == 1
	assert device.usUsage == 2
	assert device.dwFlags == RIDEV_REMOVE
	assert not device.hwndTarget


def test_raw_input_mouse_sample_extraction_matches_synthetic_rawinput_fields(
	win_raw_input_harness: ctypes.CDLL,
) -> None:
	sample = RawMouseSample()
	result = win_raw_input_harness.QLR_WinRawInputExtractMouseSampleFromFields(
		21,
		-13,
		RI_MOUSE_BUTTON_1_DOWN | RI_MOUSE_WHEEL,
		WHEEL_DELTA,
		ctypes.byref(sample),
	)

	assert result == 1
	assert sample.dx == 21
	assert sample.dy == -13
	assert sample.buttonFlags == (RI_MOUSE_BUTTON_1_DOWN | RI_MOUSE_WHEEL)
	assert sample.wheelDelta == WHEEL_DELTA


def test_raw_input_button_translation_emits_buttons_and_positive_wheel_events(
	win_raw_input_harness: ctypes.CDLL,
) -> None:
	keys = (ctypes.c_int * 12)()
	down = (ctypes.c_int * 12)()
	mouse1 = win_raw_input_harness.QLR_WinRawInputKeyMouse1()
	wheel_up = win_raw_input_harness.QLR_WinRawInputKeyWheelUp()

	count = win_raw_input_harness.QLR_WinRawInputTranslateButtonFlags(
		RI_MOUSE_BUTTON_1_DOWN | RI_MOUSE_BUTTON_1_UP | RI_MOUSE_BUTTON_4_DOWN | RI_MOUSE_BUTTON_5_UP | RI_MOUSE_WHEEL,
		WHEEL_DELTA,
		keys,
		down,
		12,
	)

	assert count == 6
	assert list(keys)[:count] == [mouse1, mouse1, mouse1 + 3, mouse1 + 4, wheel_up, wheel_up]
	assert list(down)[:count] == [1, 0, 1, 0, 1, 0]


def test_raw_input_button_translation_emits_negative_wheel_events(
	win_raw_input_harness: ctypes.CDLL,
) -> None:
	keys = (ctypes.c_int * 12)()
	down = (ctypes.c_int * 12)()
	mouse1 = win_raw_input_harness.QLR_WinRawInputKeyMouse1()
	wheel_down = win_raw_input_harness.QLR_WinRawInputKeyWheelDown()

	count = win_raw_input_harness.QLR_WinRawInputTranslateButtonFlags(
		RI_MOUSE_BUTTON_2_DOWN | RI_MOUSE_WHEEL,
		-WHEEL_DELTA,
		keys,
		down,
		12,
	)

	assert count == 3
	assert list(keys)[:count] == [mouse1 + 1, wheel_down, wheel_down]
	assert list(down)[:count] == [1, 1, 0]


def test_win32_raw_input_source_registers_cvars_and_raw_fallback_lane() -> None:
	source = WIN_INPUT.read_text(encoding="utf-8")
	init_block = _extract_function_block(source, "void IN_Init( void ) {")
	shutdown_block = _extract_function_block(source, "void IN_Shutdown( void ) {")
	startup_block = _extract_function_block(source, "void IN_StartupMouse( void )")

	assert re.search(r'in_mouse\s*=\s*Cvar_Get\s*\(\s*"in_mouse"\s*,\s*"2"', init_block)
	assert 'Cvar_Get ("in_mouseMode"' in init_block
	assert 'Cvar_Get ("in_debugMouse"' in init_block
	assert 'Cvar_Get ("in_nograb"' in init_block
	assert 'Cvar_Get ("in_raw_useWindowHandle"' in init_block
	assert 'Cmd_AddCommand( "ListInputDevices", ListInputDevices_f );' in init_block
	assert 'Cmd_RemoveCommand("ListInputDevices" );' in shutdown_block

	assert "IN_InitRawInput()" in startup_block
	assert 'Com_Printf( "Falling back on raw input...\\n" );' in startup_block
	assert 'Cvar_Set( "in_mouse", "2" );' in startup_block


def test_win32_raw_input_source_includes_device_listing_and_wm_input_dispatch() -> None:
	win_input = WIN_INPUT.read_text(encoding="utf-8")
	win_wndproc = WIN_WNDPROC.read_text(encoding="utf-8")
	list_block = _extract_function_block(win_input, "static void ListInputDevices_f( void )\n{")
	mouse_mode_block = _extract_function_block(win_wndproc, "static int WIN_GetMouseInputMode( void )\n{")
	main_wndproc = _extract_function_block(win_wndproc, "LONG WINAPI MainWndProc (")

	assert "ListInputDevices is only supported for Raw Input (in_mouse 2).\\n" in list_block
	assert "GetRawInputDeviceList" in list_block
	assert "GetRawInputDeviceInfoA" in list_block
	assert "Raw Input Mouse Devices: \\n" in list_block

	assert "if ( !in_mouse )" in mouse_mode_block
	assert "return 0;" in mouse_mode_block
	assert "return in_mouse->integer;" in mouse_mode_block
	assert "mouseInputMode = WIN_GetMouseInputMode();" in main_wndproc
	assert "mouseInputMode != 1" in main_wndproc
	assert "in_mouse->integer != 1" not in main_wndproc
	assert "case WM_INPUT:" in main_wndproc
	assert "IN_RawInputEvent( wParam, lParam );" in main_wndproc
	assert "IN_RawInputIsActive()" in main_wndproc


def test_retail_mouse_key_range_extends_through_mouse9_before_wheel_and_joy_keys() -> None:
	keycodes = KEYCODES.read_text(encoding="utf-8")
	cl_keys = CL_KEYS.read_text(encoding="utf-8")
	browser_key_block = _extract_function_block(
		cl_keys, "static void CL_DispatchBrowserKeyEvent( int key, qboolean down ) {"
	)

	key_order = [
		"K_MOUSE5",
		"K_MOUSE6",
		"K_MOUSE7",
		"K_MOUSE8",
		"K_MOUSE9",
		"K_MWHEELDOWN",
		"K_MWHEELUP",
		"K_JOY1",
	]
	key_values = _parse_key_enum_values(keycodes)
	positions = [keycodes.index(key) for key in key_order]

	assert positions == sorted(positions)
	assert key_values["K_MOUSE1"] == 0xB2
	assert key_values["K_MOUSE9"] == 0xBA
	assert key_values["K_MWHEELDOWN"] == 0xBB
	assert key_values["K_MWHEELUP"] == 0xBC
	assert key_values["K_JOY1"] == 0xBD
	for key_name in ("MOUSE6", "MOUSE7", "MOUSE8", "MOUSE9"):
		assert f'{{"{key_name}", K_{key_name}}},' in cl_keys
	assert "key >= K_MOUSE1 && key <= K_MOUSE9" in browser_key_block


def test_win32_mouse_capture_falls_back_to_absolute_client_coordinates_for_ui_lanes() -> None:
	win_input = WIN_INPUT.read_text(encoding="utf-8")
	activate_block = _extract_function_block(win_input, "void IN_ActivateWin32Mouse( void ) {")
	rect_block = _extract_function_block(win_input, "static qboolean IN_GetClampedWindowRect( RECT *window_rect ) {")
	cursor_request_block = _extract_function_block(win_input, "static qboolean IN_CursorCaptureRequested( void ) {")
	cursor_activate_block = _extract_function_block(win_input, "static void IN_ActivateCursorCapture( void ) {")
	cursor_deactivate_block = _extract_function_block(win_input, "static void IN_DeactivateCursorCapture( void ) {")
	cursor_update_block = _extract_function_block(win_input, "static void IN_UpdateCursorCapture( void ) {")
	relative_block = _extract_function_block(win_input, "static qboolean IN_ShouldUseRelativeMouse( void ) {")
	window_block = _extract_function_block(win_input, "static void IN_WindowMouse( void ) {")
	mouse_move_block = _extract_function_block(win_input, "void IN_MouseMove ( void ) {")
	frame_block = _extract_function_block(win_input, "void IN_Frame (void) {")

	assert "qboolean\tcursorCaptured;" in win_input
	assert "SM_CXVIRTUALSCREEN" in rect_block
	assert "SM_CYVIRTUALSCREEN" in rect_block
	assert "GetWindowRect( g_wv.hWnd, window_rect );" in rect_block
	assert "KEYCATCH_UI | KEYCATCH_CGAME | KEYCATCH_BROWSER" in cursor_request_block
	assert "in_nograb && in_nograb->integer" in cursor_request_block
	assert "IN_GetClampedWindowRect( &window_rect )" in cursor_activate_block
	assert "SetCapture( g_wv.hWnd );" in cursor_activate_block
	assert "ClipCursor( &window_rect );" in cursor_activate_block
	assert "s_wmv.cursorCaptured = qtrue;" in cursor_activate_block
	assert "ClipCursor( NULL );" in cursor_deactivate_block
	assert "ReleaseCapture();" in cursor_deactivate_block
	assert "s_wmv.cursorCaptured = qfalse;" in cursor_deactivate_block
	assert "IN_CursorCaptureRequested()" in cursor_update_block
	assert "IN_ActivateCursorCapture();" in cursor_update_block
	assert "IN_DeactivateCursorCapture();" in cursor_update_block
	assert 'Cvar_SetValue( "vid_xpos", (float)window_rect.left );' in activate_block
	assert 'Cvar_SetValue( "vid_ypos", (float)window_rect.top );' in activate_block

	assert "!s_wmv.mouseActive" in relative_block
	assert "KEYCATCH_MESSAGE | KEYCATCH_RETAIL_MOUSEPASS" in relative_block
	assert "in_nograb && in_nograb->integer" in relative_block
	assert "ScreenToClient( g_wv.hWnd, &current_pos );" in window_block
	assert "oldCursorX" in window_block
	assert "oldCursorY" in window_block
	assert "Sys_QueEvent( 0, SE_MOUSE, current_pos.x, current_pos.y, 0, NULL );" in window_block

	assert "g_wv.hWnd && ( s_wmv.mouseStartupDelayed || ( in_mouse && in_mouse->integer != 0 ) )" in frame_block
	assert 'Com_Printf( "Proceeding with delayed mouse init\\n" );' in frame_block
	assert 'Com_Printf( "Retrying mouse init now that a window is available\\n" );' in frame_block
	assert "if ( !s_wmv.mouseInitialized ) {" in frame_block
	assert "if ( cls.keyCatchers & ( KEYCATCH_UI | KEYCATCH_CGAME | KEYCATCH_BROWSER ) ) {" in frame_block
	assert frame_block.index("IN_StartupMouse();") < frame_block.rindex(
		"if ( !s_wmv.mouseInitialized ) {"
	)
	assert frame_block.index("IN_UpdateCursorCapture();") < frame_block.index("IN_WindowMouse();")

	assert "cls.keyCatchers & ~( KEYCATCH_MESSAGE | KEYCATCH_RETAIL_MOUSEPASS )" in frame_block
	assert "Cvar_VariableValue (\"r_fullscreen\")" not in frame_block
	assert 'Cvar_VariableString("r_glDriver")' not in frame_block
	assert frame_block.index(
		"cls.keyCatchers & ~( KEYCATCH_MESSAGE | KEYCATCH_RETAIL_MOUSEPASS )"
	) < frame_block.index("in_nograb && in_nograb->integer")
	assert frame_block.index("in_nograb && in_nograb->integer") < frame_block.index(
		"!in_appactive"
	)
	assert "IN_UpdateCursorCapture();" in frame_block
	keycatcher_branch = frame_block[
		frame_block.index("if ( cls.keyCatchers & ~( KEYCATCH_MESSAGE | KEYCATCH_RETAIL_MOUSEPASS ) ) {"):
		frame_block.index("if ( in_nograb && in_nograb->integer ) {")
	]
	assert keycatcher_branch.index("IN_DeactivateMouse();") < keycatcher_branch.index("IN_UpdateCursorCapture();")
	assert frame_block.count("IN_DeactivateCursorCapture();") >= 2
	assert "if ( !IN_ShouldUseRelativeMouse() ) {" in mouse_move_block
	assert "IN_WindowMouse();" in mouse_move_block


def test_win32_window_class_registration_survives_restart_recreate_races() -> None:
	win_glimp = WIN_GLIMP.read_text(encoding="utf-8")
	register_block = _extract_function_block(win_glimp, "static void GLW_RegisterWindowClass( void ) {")
	unregister_block = _extract_function_block(win_glimp, "static void GLW_UnregisterWindowClass( void ) {")
	create_block = _extract_function_block(
		win_glimp,
		"static qboolean GLW_CreateWindow( const char *drivername, int width, int height, int colorbits, qboolean cdsFullscreen )",
	)
	shutdown_block = _extract_function_block(win_glimp, "void GLimp_Shutdown( void )")

	assert "RegisterClassW( &wc )" in register_block
	assert "ERROR_CLASS_ALREADY_EXISTS" in register_block
	assert "ri.Error( ERR_FATAL, \"GLW_CreateWindow: could not register window class\" );" in register_block
	assert "s_classRegistered = qtrue;" in register_block
	assert "UnregisterClassW( WINDOW_CLASS_NAME, g_wv.hInstance )" in unregister_block
	assert "ERROR_CLASS_DOES_NOT_EXIST" in unregister_block
	assert "s_classRegistered = qfalse;" in unregister_block
	assert "PRINT_WARNING" in unregister_block
	assert "GLW_RegisterWindowClass();" in create_block
	assert "GLW_UnregisterWindowClass();" in create_block
	assert "GLW_UnregisterWindowClass();" in shutdown_block


def test_win32_game_cursor_hides_the_os_cursor_for_ui_and_cgame_lanes() -> None:
	win_input = WIN_INPUT.read_text(encoding="utf-8")
	win_local = WIN_LOCAL.read_text(encoding="utf-8")
	win_wndproc = WIN_WNDPROC.read_text(encoding="utf-8")
	game_cursor_block = _extract_function_block(win_input, "qboolean IN_GameCursorActive( void ) {")
	update_cursor_block = _extract_function_block(win_input, "void IN_UpdateSystemCursor( void ) {")
	deactivate_block = _extract_function_block(win_input, "void IN_DeactivateWin32Mouse( void )")
	frame_block = _extract_function_block(win_input, "void IN_Frame (void) {")
	main_wndproc = _extract_function_block(win_wndproc, "LONG WINAPI MainWndProc (")

	assert "qboolean IN_GameCursorActive( void );" in win_local
	assert "void\tIN_UpdateSystemCursor( void );" in win_local
	assert "static qboolean s_systemCursorHiddenForGameCursor;" in win_input
	assert "if ( !in_appactive )" in game_cursor_block
	assert "cls.keyCatchers & KEYCATCH_BROWSER" in game_cursor_block
	assert "KEYCATCH_UI | KEYCATCH_CGAME" in game_cursor_block

	assert "SetCursor( NULL );" in update_cursor_block
	assert "s_systemCursorHiddenForGameCursor = qtrue;" in update_cursor_block
	assert "SetCursor( LoadCursor( NULL, IDC_ARROW ) );" in update_cursor_block
	assert "s_systemCursorHiddenForGameCursor = qfalse;" in update_cursor_block

	assert deactivate_block.index("while (ShowCursor (TRUE) < 0)") < deactivate_block.index(
		"IN_UpdateSystemCursor();"
	)
	assert frame_block.count("IN_UpdateSystemCursor();") >= 4
	assert frame_block.index("IN_ActivateMouse();") < frame_block.rindex("IN_UpdateSystemCursor();")

	set_cursor_case = main_wndproc[main_wndproc.index("case WM_SETCURSOR:") :]
	assert "browserCursor = (HCURSOR)CL_WebHost_GetCursorHandle();" in set_cursor_case
	assert "SetCursor( browserCursor );" in set_cursor_case
	assert "if ( IN_GameCursorActive() )" in set_cursor_case
	assert "IN_UpdateSystemCursor();" in set_cursor_case
	assert set_cursor_case.index("CL_WebHost_GetCursorHandle()") < set_cursor_case.index(
		"IN_GameCursorActive()"
	)


def test_fast_vid_restart_deactivates_mouse_without_flipping_appactive_state() -> None:
	win_input = WIN_INPUT.read_text(encoding="utf-8")
	win_glimp = WIN_GLIMP.read_text(encoding="utf-8")
	win_local = WIN_LOCAL.read_text(encoding="utf-8")
	activate_block = _extract_function_block(win_input, "void IN_Activate (qboolean active) {")
	fast_restart_block = _extract_function_block(
		win_glimp, "qboolean WIN_FastVidRestart( int *width, int *height, qboolean *fullscreen )"
	)

	assert "void\tIN_DeactivateMouse( void );" in win_local
	assert "in_appactive = active;" in activate_block
	assert "IN_DeactivateMouse();" in activate_block
	assert "if ( !active )" not in activate_block

	assert "IN_DeactivateMouse();" in fast_restart_block
	assert "IN_Activate( qfalse );" not in fast_restart_block
	assert fast_restart_block.index("IN_DeactivateMouse();") < fast_restart_block.index(
		"GLW_ChangeWindowMode()"
	)


def test_win32_raw_buttons_fall_back_to_window_messages_for_menu_catchers() -> None:
	win_input = WIN_INPUT.read_text(encoding="utf-8")
	win_local = WIN_LOCAL.read_text(encoding="utf-8")
	win_wndproc = WIN_WNDPROC.read_text(encoding="utf-8")
	raw_append_block = _extract_function_block(
		win_input, "static void IN_RawInputAppendSample( const qlr_win32_raw_mouse_sample_t *sample ) {"
	)
	button_gate_block = _extract_function_block(
		win_input, "qboolean IN_ShouldProcessWin32MouseButtons( void ) {"
	)
	main_wndproc = _extract_function_block(win_wndproc, "LONG WINAPI MainWndProc (")

	assert "qboolean IN_ShouldProcessWin32MouseButtons( void );" in win_local
	assert "cls.keyCatchers & ~KEYCATCH_RETAIL_MOUSEPASS" in raw_append_block
	assert "IN_ClearRawInputSamples();" in raw_append_block
	assert "if ( !IN_RawInputIsActive() ) {" in button_gate_block
	assert "if ( !IN_ShouldUseRelativeMouse() ) {" in button_gate_block
	assert "return qfalse;" in button_gate_block
	assert "if ( IN_ShouldProcessWin32MouseButtons() )" in main_wndproc
	assert "IN_MouseEvent (temp);" in main_wndproc


def test_directinput_mouse_uses_retail_buffered_event_stream_and_eight_buttons() -> None:
	win_input = WIN_INPUT.read_text(encoding="utf-8")
	win_local = WIN_LOCAL.read_text(encoding="utf-8")
	init_block = _extract_function_block(win_input, "qboolean IN_InitDIMouse( void ) {")
	di_block = _extract_function_block(win_input, "void IN_DIMouse( int *mx, int *my ) {")
	mouse_event_block = _extract_function_block(win_input, "void IN_MouseEvent (int mstate)\n{")

	assert "#define\tDIRECTINPUT_VERSION\t0x0800" in win_local
	assert "DirectInput8CreateProc_t" in win_input
	assert 'LoadLibrary("dinput8.dll")' in init_block
	assert 'GetProcAddress(hInstDI,"DirectInput8Create")' in init_block
	assert "iDirectInput8Create( g_wv.hInstance, DIRECTINPUT_VERSION, &ql_IID_IDirectInput8A, (LPVOID *)&g_pdi, NULL)" in init_block
	assert "IDirectInput8_CreateDevice(g_pdi, &GUID_SysMouse, &g_pMouse, NULL);" in init_block
	assert "DirectInputCreateA" not in win_input
	assert 'LoadLibrary("dinput.dll")' not in win_input
	assert "#define DINPUT_BUFFERSIZE           0x200" in win_input
	assert "#define DIMOFS_BUTTON7              (DIMOFS_BUTTON0 + 7)" in win_input
	assert "bButtonH" in win_input
	assert "DIDEVICEOBJECTDATA\tod[DINPUT_BUFFERSIZE];" in di_block
	assert "IDirectInputDevice8_GetDeviceData( g_pMouse, sizeof( DIDEVICEOBJECTDATA ), od, &dwElements, 0 );" in di_block
	assert "DI_BUFFEROVERFLOW" in di_block
	assert "*mx += (int)od[i].dwData;" in di_block
	assert "*my += (int)od[i].dwData;" in di_block
	assert "DIMOFS_BUTTON7" in di_block
	assert "K_MOUSE1 + (int)( od[i].dwOfs - DIMOFS_BUTTON0 )" in di_block
	assert "IDirectInputDevice_GetDeviceState" not in di_block
	assert "i < 8" in mouse_event_block


def test_win32_mouse_owner_aliases_pin_retail_hlil_mapping() -> None:
	aliases = json.loads(ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]
	functions = GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	hlil = HLIL_PART05.read_text(encoding="utf-8")

	expected_aliases = {
		"FUN_004ea390": "IN_UpdateWin32MouseClip",
		"sub_4EA390": "IN_UpdateWin32MouseClip",
		"sub_4ea390": "IN_UpdateWin32MouseClip",
		"FUN_004ea480": "IN_ActivateWin32Mouse",
		"sub_4EA480": "IN_ActivateWin32Mouse",
		"sub_4ea480": "IN_ActivateWin32Mouse",
		"FUN_004ea4b0": "IN_Win32Mouse",
		"sub_4EA4B0": "IN_Win32Mouse",
		"sub_4ea4b0": "IN_Win32Mouse",
		"FUN_004ea540": "IN_ShutdownDIMouse",
		"sub_4EA540": "IN_ShutdownDIMouse",
		"sub_4ea540": "IN_ShutdownDIMouse",
		"FUN_004ea590": "IN_ActivateDIMouse",
		"sub_4EA590": "IN_ActivateDIMouse",
		"sub_4ea590": "IN_ActivateDIMouse",
		"FUN_004ea690": "IN_DIMouse",
		"sub_4EA690": "IN_DIMouse",
		"sub_4ea690": "IN_DIMouse",
		"FUN_004eaa80": "IN_MouseEvent",
		"sub_4EAA80": "IN_MouseEvent",
		"sub_4eaa80": "IN_MouseEvent",
		"FUN_004ebaa0": "IN_RawInputAppendSample",
		"sub_4EBAA0": "IN_RawInputAppendSample",
		"sub_4ebaa0": "IN_RawInputAppendSample",
		"FUN_004ebb20": "IN_InitRawInput",
		"sub_4EBB20": "IN_InitRawInput",
		"sub_4ebb20": "IN_InitRawInput",
		"FUN_004eb830": "IN_RawInputMouse",
		"sub_4EB830": "IN_RawInputMouse",
		"sub_4eb830": "IN_RawInputMouse",
		"FUN_004ebba0": "IN_InitDIMouse",
		"sub_4EBBA0": "IN_InitDIMouse",
		"sub_4ebba0": "IN_InitDIMouse",
		"FUN_004ebe40": "IN_DeactivateMouse",
		"sub_4EBE40": "IN_DeactivateMouse",
		"sub_4ebe40": "IN_DeactivateMouse",
		"FUN_004ebee0": "IN_StartupMouse",
		"sub_4EBEE0": "IN_StartupMouse",
		"sub_4ebee0": "IN_StartupMouse",
		"FUN_004ec030": "IN_MouseMove",
		"sub_4EC030": "IN_MouseMove",
		"sub_4ec030": "IN_MouseMove",
		"FUN_004ec160": "IN_Startup",
		"sub_4EC160": "IN_Startup",
		"sub_4ec160": "IN_Startup",
		"FUN_004ec1d0": "IN_Shutdown",
		"sub_4EC1D0": "IN_Shutdown",
		"sub_4ec1d0": "IN_Shutdown",
		"FUN_004ec2a0": "IN_Init",
		"sub_4EC2A0": "IN_Init",
		"sub_4ec2a0": "IN_Init",
		"FUN_004ec470": "IN_Activate",
		"sub_4EC470": "IN_Activate",
		"sub_4ec470": "IN_Activate",
		"FUN_004ec490": "IN_ActivateMouse",
		"sub_4EC490": "IN_ActivateMouse",
		"sub_4ec490": "IN_ActivateMouse",
		"FUN_004ec4f0": "IN_Frame",
		"sub_4EC4F0": "IN_Frame",
		"sub_4ec4f0": "IN_Frame",
	}

	for raw_name, normalized_name in expected_aliases.items():
		assert aliases[raw_name] == normalized_name

	for expected_row in (
		"FUN_004ea390,004ea390,236,0,unknown",
		"FUN_004ea690,004ea690,926,0,unknown",
		"FUN_004eb830,004eb830,609,0,unknown",
		"FUN_004ebba0,004ebba0,663,0,unknown",
		"FUN_004ebaa0,004ebaa0,127,0,unknown",
		"FUN_004ebb20,004ebb20,121,0,unknown",
		"FUN_004ebee0,004ebee0,323,0,unknown",
		"FUN_004ec030,004ec030,303,0,unknown",
		"FUN_004ec4f0,004ec4f0,143,0,unknown",
	):
		assert expected_row in functions

	for expected in (
		"004ebb20    int32_t sub_4ebb20()",
		"004ebb35      rawInputDevices.usUsagePage = 1",
		"004ebb3c      rawInputDevices.dwFlags = 0",
		"004ebba0    int32_t sub_4ebba0(int32_t arg1)",
		"004ebbf8  HRESULT punkOuter_1 = DirectInput8Create(hinst, dwVersion: 0x800",
		"004ec030    int32_t sub_4ec030()",
		"004ec083  ScreenToClient(hWnd: data_12d34b4, lpPoint: &point)",
		"004ec160    void* sub_4ec160()",
		"004ec2a0    int32_t sub_4ec2a0()",
		'004ec32d  data_12cfe54 = sub_4ce0d0(x87_r0, "in_mouse", U"2", 0x80021)',
		"004ec470    int32_t sub_4ec470(int32_t arg1)",
		"004ec490    void sub_4ec490()",
		"004ec4f0    int32_t sub_4ec4f0()",
	):
		assert expected in hlil


def test_win32_joystick_midi_device_and_client_wiring_match_retail_evidence() -> None:
	aliases = json.loads(ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]
	functions = GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	imports = GHIDRA_IMPORTS.read_text(encoding="utf-8")
	host_hlil = HLIL_PART05.read_text(encoding="utf-8")
	client_hlil = HLIL_PART04.read_text(encoding="utf-8")
	win_input = WIN_INPUT.read_text(encoding="utf-8")
	cl_input = CL_INPUT.read_text(encoding="utf-8")
	common = COMMON.read_text(encoding="utf-8")

	expected_aliases = {
		"FUN_004b5570": "CL_JoystickEvent",
		"sub_4B5570": "CL_JoystickEvent",
		"sub_4b5570": "CL_JoystickEvent",
		"FUN_004b55b0": "CL_JoystickMove",
		"sub_4B55B0": "CL_JoystickMove",
		"sub_4b55b0": "CL_JoystickMove",
		"FUN_004eacd0": "IN_StartupJoystick",
		"sub_4EACD0": "IN_StartupJoystick",
		"sub_4eacd0": "IN_StartupJoystick",
		"FUN_004eae90": "JoyToF",
		"sub_4EAE90": "JoyToF",
		"sub_4eae90": "JoyToF",
		"FUN_004eaef0": "IN_JoyMove",
		"sub_4EAEF0": "IN_JoyMove",
		"sub_4eaef0": "IN_JoyMove",
		"FUN_004eb520": "MIDI_NoteOff",
		"sub_4EB520": "MIDI_NoteOff",
		"sub_4eb520": "MIDI_NoteOff",
		"FUN_004eb550": "MIDI_NoteOn",
		"sub_4EB550": "MIDI_NoteOn",
		"sub_4eb550": "MIDI_NoteOn",
		"FUN_004eb5b0": "MidiInProc",
		"sub_4EB5B0": "MidiInProc",
		"sub_4eb5b0": "MidiInProc",
		"FUN_004eb640": "MidiInfo_f",
		"sub_4EB640": "MidiInfo_f",
		"sub_4eb640": "MidiInfo_f",
		"FUN_004eb770": "IN_StartupMIDI",
		"sub_4EB770": "IN_StartupMIDI",
		"sub_4eb770": "IN_StartupMIDI",
	}
	for raw_name, normalized_name in expected_aliases.items():
		assert aliases[raw_name] == normalized_name

	for expected in (
		"WINMM.DLL!joyGetDevCapsA",
		"WINMM.DLL!joyGetNumDevs",
		"WINMM.DLL!joyGetPosEx",
		"WINMM.DLL!midiInClose",
		"WINMM.DLL!midiInGetDevCapsA",
		"WINMM.DLL!midiInGetNumDevs",
		"WINMM.DLL!midiInOpen",
		"WINMM.DLL!midiInStart",
	):
		assert expected in imports

	for expected_row in (
		"FUN_004b5570,004b5570,58,0,unknown",
		"FUN_004b55b0,004b55b0,139,0,unknown",
		"FUN_004eacd0,004eacd0,444,0,unknown",
		"FUN_004eae90,004eae90,81,0,unknown",
		"FUN_004eaef0,004eaef0,1536,0,unknown",
		"FUN_004eb520,004eb520,41,0,unknown",
		"FUN_004eb550,004eb550,93,0,unknown",
		"FUN_004eb5b0,004eb5b0,131,0,unknown",
		"FUN_004eb640,004eb640,282,0,unknown",
		"FUN_004eb770,004eb770,189,0,unknown",
		"FUN_004ec160,004ec160,99,0,unknown",
		"FUN_004ec2a0,004ec2a0,462,0,unknown",
		"FUN_004ec4f0,004ec4f0,143,0,unknown",
	):
		assert expected_row in functions

	for expected in (
		"004eacd0    int32_t sub_4eacd0()",
		'004eace3  sub_4cd250("ui_joyavail", U"0")',
		"004ead05  uint32_t eax_2 = joyGetNumDevs()",
		"004ead4e          data_12cfe1c = 0x34",
		"004ead58          data_12cfe20 = 0x400",
		"004ead62          uint32_t eax_4 = joyGetPosEx(uJoyID, pji: &data_12cfe1c)",
		"004eadb0  uint32_t eax_6 = joyGetDevCapsA(uJoyID: data_12cfc7c, pjc: &data_12cfc80, cbjc: 0x194)",
		'004eae8b  return sub_4cd250("ui_joyavail", U"1")',
		"004eae90    long double sub_4eae90(int32_t arg1)",
		"float.t(arg1 - 0x8000) * fconvert.t(3.0517578125e-05)",
		"004eaef0    void sub_4eaef0()",
		"004eaf29      data_12cfe20 = 0xff",
		"004eaf33      uint32_t eax = joyGetPosEx(uJoyID, pji: &data_12cfe1c)",
		"004eb00e                      sub_4ed050(data_12d3568, 1, i + 0xbd, 1, 0, 0)",
		"004eb1f2                          sub_4ed050(0, 4, 0, i, 0, 0)",
		"004eb183                          sub_4ed050(0, 4, 1, i, 0, 0)",
		"004eb2c5                  sub_4ed050(data_12d3568, 1, *i_2, 1, 0, 0)",
		"004eb4e4                  sub_4ed050(data_12d3568, 3, edi_3, esi_1, 0, 0)",
		'004ec359  data_12df9ec = sub_4ce0d0(x87_r4, "in_joystick", U"1", 0x21)',
		'004ec36f  data_12cfe5c = sub_4ce0d0(x87_r6, "in_joystick_inverted", U"0", 1)',
		'004ec3b7  data_12df9f8 = sub_4ce0d0(x87_r4, "joy_threshold", "0.15", 1)',
		"004eb520    int32_t __convention(\"regparm\") sub_4eb520(int32_t arg1)",
		"004eb540  return sub_4ed050(data_12d3568, 1, result, 0, 0, 0)",
		"004eb550    int32_t sub_4eb550(int32_t arg1 @ esi, int32_t arg2)",
		"004eb5a3  return sub_4ed050(data_12d3568, 1, result, 1, 0, 0)",
		"004eb5b0    void __stdcall sub_4eb5b0(int32_t arg1, int32_t arg2)",
		"004eb62a              sub_4eb520(zx.d((arg2 u>> 8).b))",
		"004eb5fe          sub_4eb550(zx.d((arg2 u>> 8).b), zx.d((arg2 u>> 0x10).b))",
		"004eb640    int32_t sub_4eb640()",
		'004eb66d  sub_4c9860(esi, "\\nMIDI control:       %s\\n")',
		"004eb770    uint32_t sub_4eb770()",
		'004eb778  st0, result = sub_4ccd60("in_midi")',
		"004eb78f  uint32_t eax = midiInGetNumDevs()",
		"004eb7b4          midiInGetDevCapsA(uDeviceID, pmic, cbmic: 0x2c)",
		"004eb7e4          dwCallback: sub_4eb5b0, dwInstance: 0, fdwOpen: CALLBACK_FUNCTION) == 0)",
		"004eb826      return midiInStart(hmi: data_12ce454)",
		'004ec302  sub_4c81d0("midiinfo", sub_4eb640)',
		"004ec197  sub_4eb770()",
		"004ec22d      midiInClose(hmi)",
	):
		assert expected in host_hlil

	for expected in (
		"004b5570    int32_t sub_4b5570(int32_t arg1, int32_t arg2)",
		"004b557e  if (arg1 s>= 0 && arg1 s< 6)",
		"004b55a0      (&data_1471ea4)[arg1] = arg2",
		'004b5588  sub_4c9b60(1, "CL_JoystickEvent: bad axis %i")',
		"004b55b0    int32_t sub_4b55b0(void* arg1)",
		"004b55bc      result = sub_4eb500()",
		"004b5629          data_1471ea4 = 0",
		"004b562e          data_1471ea8 = 0",
		"004b5633          data_1471eac = 0",
		"004b5ca8  sub_4b5800(arg1)",
		"004b5cae  sub_4b55b0(arg1)",
	):
		assert expected in client_hlil

	init_block = _extract_function_block(win_input, "void IN_Init( void ) {")
	startup_block = _extract_function_block(win_input, "void IN_StartupJoystick (void) {")
	joy_to_f_block = _extract_function_block(win_input, "float JoyToF( int value ) {")
	queue_axis_block = _extract_function_block(win_input, "static void IN_QueueJoystickAxis( int axis, int value ) {")
	joy_mouse_move_block = _extract_function_block(
		win_input, "static int IN_JoyMouseMove( float axisValue, float deadzone, float sensitivity, qboolean invert ) {"
	)
	joy_move_block = _extract_function_block(win_input, "void IN_JoyMove( void ) {")
	midi_note_off_block = _extract_function_block(win_input, "static void MIDI_NoteOff( int note )\n{")
	midi_note_on_block = _extract_function_block(win_input, "static void MIDI_NoteOn( int note, int velocity )\n{")
	midi_callback_block = _extract_function_block(
		win_input,
		"static void CALLBACK MidiInProc( HMIDIIN hMidiIn, UINT uMsg, DWORD dwInstance, \n\t\t\t\t\t\t\t\t DWORD dwParam1, DWORD dwParam2 )\n{",
	)
	midi_info_block = _extract_function_block(win_input, "static void MidiInfo_f( void )\n{")
	midi_startup_block = _extract_function_block(win_input, "static void IN_StartupMIDI( void )\n{")
	midi_shutdown_block = _extract_function_block(win_input, "static void IN_ShutdownMIDI( void )\n{")
	frame_block = _extract_function_block(win_input, "void IN_Frame (void) {")
	event_loop_block = _extract_function_block(common, "int Com_EventLoop( void ) {")
	cl_joystick_event_block = _extract_function_block(cl_input, "void CL_JoystickEvent( int axis, int value, int time ) {")
	cl_joystick_move_block = _extract_function_block(cl_input, "void CL_JoystickMove( usercmd_t *cmd ) {")
	create_cmd_block = _extract_function_block(cl_input, "usercmd_t CL_CreateCmd( void ) {")

	for expected in (
		'in_joystick\t\t\t\t= Cvar_Get ("in_joystick",\t\t\t\t"1",\t\tCVAR_ARCHIVE|CVAR_LATCH);',
		'in_joystickInverted\t\t= Cvar_Get ("in_joystick_inverted",\t\t"0",\t\tCVAR_ARCHIVE);',
		'in_joyBallScale\t\t\t= Cvar_Get ("in_joyBallScale",\t\t\t"1.0",\t\tCVAR_ARCHIVE);',
		'in_debugJoystick\t\t= Cvar_Get ("in_debugjoystick",\t\t\t"0",\t\tCVAR_TEMP);',
		'joy_threshold\t\t\t= Cvar_Get ("joy_threshold",\t\t\t"0.15",\t\tCVAR_ARCHIVE);',
		'in_joyHorizViewSensitivity = Cvar_Get ("in_joyHorizViewSensitivity",\t"20.0",\tCVAR_ARCHIVE);',
		'in_joyVertViewSensitivity = Cvar_Get ("in_joyVertViewSensitivity",\t"15.0",\tCVAR_ARCHIVE);',
		'in_joyHorizMoveDeadzone\t= Cvar_Get ("in_joyHorizMoveDeadzone",\t"0.50",\tCVAR_ARCHIVE);',
		'in_midi\t\t\t\t\t= Cvar_Get ("in_midi",\t\t\t\t\t"0",\t\tCVAR_ARCHIVE);',
		'in_midiport\t\t\t\t= Cvar_Get ("in_midiport",\t\t\t\t"1",\t\tCVAR_ARCHIVE);',
		'in_midichannel\t\t\t= Cvar_Get ("in_midichannel",\t\t\t"1",\t\tCVAR_ARCHIVE);',
		'in_mididevice\t\t\t= Cvar_Get ("in_mididevice",\t\t\t"0",\t\tCVAR_ARCHIVE);',
		'Cmd_AddCommand( "midiinfo", MidiInfo_f );',
	):
		assert expected in init_block

	for expected in (
		"joy.avail = qfalse;",
		"joy.oldbuttonstate = 0;",
		"joy.oldpovstate = 0;",
		"joy.oldmoveaxisstate[AXIS_SIDE] = 0;",
		"joy.oldmoveaxisstate[AXIS_FORWARD] = 0;",
		'Cvar_Set( "ui_joyavail", "0" );',
		"joyGetNumDevs ()",
		"joy.ji.dwSize = sizeof(joy.ji);",
		"joy.ji.dwFlags = JOY_RETURNCENTERED;",
		"joyGetPosEx (joy.id, &joy.ji)",
		"joyGetDevCaps (joy.id, &joy.jc, sizeof(joy.jc))",
		'Cvar_Set( "ui_joyavail", "1" );',
	):
		assert expected in startup_block

	assert "value -= 32768;" in joy_to_f_block
	assert "fValue = (float)value / 32768.0;" in joy_to_f_block
	assert "if ( fValue < -1 ) {" in joy_to_f_block
	assert "if ( fValue > 1 ) {" in joy_to_f_block

	assert "value = (int)Com_Clamp( -127.0f, 127.0f, (float)value );" in queue_axis_block
	assert "Sys_QueEvent( g_wv.sysMsgTime, SE_JOYSTICK_AXIS, axis, value, 0, NULL );" in queue_axis_block

	assert "axisValue = Com_Clamp( -1.0f, 1.0f, axisValue );" in joy_mouse_move_block
	assert "move = powf( fabsf( move ), accel ) * sign;" in joy_mouse_move_block
	assert "if ( invert ) {" in joy_mouse_move_block

	for expected in (
		"joy.ji.dwFlags = JOY_RETURNALL;",
		"Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, K_JOY1 + i, qtrue, 0, NULL );",
		"Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, K_JOY1 + i, qfalse, 0, NULL );",
		"IN_QueueJoystickAxis( AXIS_SIDE, side );",
		"IN_QueueJoystickAxis( AXIS_FORWARD, forward );",
		"povstate |= 1<<12;",
		"povstate |= 1<<15;",
		"Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, joyDirectionKeys[i], qtrue, 0, NULL );",
		"x = IN_JoyMouseMove( JoyToF( joy.ji.dwRpos ), in_joyHorizViewDeadzone->value, in_joyHorizViewSensitivity->value, qfalse );",
		"y = IN_JoyMouseMove( JoyToF( joy.ji.dwUpos ), in_joyVertViewDeadzone->value, in_joyVertViewSensitivity->value, in_joystickInverted && in_joystickInverted->integer );",
		"Sys_QueEvent( g_wv.sysMsgTime, SE_MOUSE, x, y, 0, NULL );",
	):
		assert expected in joy_move_block

	for expected in (
		"qkey = note - 60 + K_AUX1;",
		"if ( qkey > 255 || qkey < K_AUX1 )",
		"Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, qkey, qfalse, 0, NULL );",
	):
		assert expected in midi_note_off_block
	for expected in (
		"if ( velocity == 0 )",
		"MIDI_NoteOff( note );",
		"qkey = note - 60 + K_AUX1;",
		"Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, qkey, qtrue, 0, NULL );",
	):
		assert expected in midi_note_on_block
	for expected in (
		"case MIM_DATA:",
		"message = dwParam1 & 0xff;",
		"if ( ( message & 0xf0 ) == 0x90 )",
		"if ( ( ( message & 0x0f ) + 1 ) == in_midichannel->integer )",
		"MIDI_NoteOn( ( dwParam1 & 0xff00 ) >> 8, ( dwParam1 & 0xff0000 ) >> 16 );",
		"else if ( ( message & 0xf0 ) == 0x80 )",
		"MIDI_NoteOff( ( dwParam1 & 0xff00 ) >> 8 );",
	):
		assert expected in midi_callback_block
	for expected in (
		'Com_Printf( "\\nMIDI control:       %s\\n", enableStrings[in_midi->integer != 0] );',
		'Com_Printf( "channel:            %d\\n", in_midichannel->integer );',
		'Com_Printf( "current device:     %d\\n", in_mididevice->integer );',
	):
		assert expected in midi_info_block
	for expected in (
		'if ( !Cvar_VariableValue( "in_midi" ) )',
		"s_midiInfo.numDevices = midiInGetNumDevs();",
		"midiInGetDevCaps( i, &s_midiInfo.caps[i], sizeof( s_midiInfo.caps[i] ) );",
		"midiInOpen( &s_midiInfo.hMidiIn,",
		"( unsigned long ) MidiInProc,",
		"CALLBACK_FUNCTION",
		"midiInStart( s_midiInfo.hMidiIn );",
	):
		assert expected in midi_startup_block
	assert "midiInClose( s_midiInfo.hMidiIn );" in midi_shutdown_block
	assert "Com_Memset( &s_midiInfo, 0, sizeof( s_midiInfo ) );" in midi_shutdown_block
	assert _extract_function_block(win_input, "void IN_Startup( void ) {").index("IN_StartupJoystick ();") < _extract_function_block(
		win_input, "void IN_Startup( void ) {"
	).index("IN_StartupMIDI();")
	assert "IN_ShutdownMIDI();" in _extract_function_block(win_input, "void IN_Shutdown( void ) {")
	assert 'Cmd_RemoveCommand("midiinfo" );' in _extract_function_block(win_input, "void IN_Shutdown( void ) {")

	assert frame_block.index("IN_JoyMove();") < frame_block.index("if ( !s_wmv.mouseInitialized ) {")
	assert "case SE_JOYSTICK_AXIS:" in event_loop_block
	assert "CL_JoystickEvent( ev.evValue, ev.evValue2, ev.evTime );" in event_loop_block
	assert "case SE_MOUSE:" in event_loop_block
	assert "CL_MouseEvent( ev.evValue, ev.evValue2, ev.evTime );" in event_loop_block

	assert "if ( axis < 0 || axis >= MAX_JOYSTICK_AXIS ) {" in cl_joystick_event_block
	assert 'Com_Error( ERR_DROP, "CL_JoystickEvent: bad axis %i", axis );' in cl_joystick_event_block
	assert "cl.joystickAxis[axis] = value;" in cl_joystick_event_block
	assert "cl.viewangles[YAW] += anglespeed * cl_yawspeed->value * cl.joystickAxis[AXIS_SIDE];" in cl_joystick_move_block
	assert "cmd->rightmove = ClampChar( cmd->rightmove + cl.joystickAxis[AXIS_SIDE] );" in cl_joystick_move_block
	assert "cl.viewangles[PITCH] += anglespeed * cl_pitchspeed->value * cl.joystickAxis[AXIS_FORWARD];" in cl_joystick_move_block
	assert "cmd->upmove = ClampChar( cmd->upmove + cl.joystickAxis[AXIS_UP] );" in cl_joystick_move_block

	assert create_cmd_block.index("CL_MouseMove( &cmd );") < create_cmd_block.index("CL_JoystickMove( &cmd );")


def test_win32_keyboard_character_event_and_vm_key_wiring_match_retail_evidence() -> None:
	all_aliases = json.loads(ALIASES.read_text(encoding="utf-8"))
	aliases = all_aliases["quakelive_steam_srp"]
	ui_aliases = all_aliases["ui"]
	cgame_aliases = all_aliases["cgame"]
	functions = GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	cgame_functions = CGAME_GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	host_hlil_part04 = HLIL_PART04.read_text(encoding="utf-8")
	host_hlil_part05 = HLIL_PART05.read_text(encoding="utf-8")
	ui_hlil = UI_HLIL_PART01.read_text(encoding="utf-8")
	cgame_hlil = CGAME_HLIL.read_text(encoding="utf-8")
	win_wndproc = WIN_WNDPROC.read_text(encoding="utf-8")
	win_main = WIN_MAIN.read_text(encoding="utf-8")
	common = COMMON.read_text(encoding="utf-8")
	cl_keys = CL_KEYS.read_text(encoding="utf-8")
	ui_main = UI_MAIN.read_text(encoding="utf-8")
	cg_main = CG_MAIN.read_text(encoding="utf-8")

	expected_host_aliases = {
		"FUN_004b6890": "Field_CharEvent",
		"sub_4B6890": "Field_CharEvent",
		"sub_4b6890": "Field_CharEvent",
		"FUN_004b71c0": "CL_CharEvent",
		"sub_4B71C0": "CL_CharEvent",
		"sub_4b71c0": "CL_CharEvent",
		"FUN_004b7b00": "CL_KeyEvent",
		"sub_4B7B00": "CL_KeyEvent",
		"sub_4b7b00": "CL_KeyEvent",
		"FUN_004ed050": "Sys_QueEvent",
		"sub_4ED050": "Sys_QueEvent",
		"sub_4ed050": "Sys_QueEvent",
		"sub_4F15C0": "MapKey",
		"sub_4f15c0": "MapKey",
		"FUN_004f1750": "MainWndProc",
		"sub_4F1750": "MainWndProc",
		"sub_4f1750": "MainWndProc",
	}
	for raw_name, normalized_name in expected_host_aliases.items():
		assert aliases[raw_name] == normalized_name

	for raw_name in ("sub_1000FF40", "sub_1000ff40"):
		assert ui_aliases[raw_name] == "_UI_KeyEvent"
	for raw_name in ("FUN_1003c6f0", "sub_1003C6F0", "sub_1003c6f0"):
		assert cgame_aliases[raw_name] == "CG_KeyEvent"

	for expected_row in (
		"FUN_004b6890,004b6890,456,0,unknown",
		"FUN_004b71c0,004b71c0,211,0,unknown",
		"FUN_004b7b00,004b7b00,1314,0,unknown",
		"FUN_004ed050,004ed050,129,0,unknown",
		"FUN_004f1750,004f1750,404,0,unknown",
	):
		assert expected_row in functions
	assert "FUN_1003c6f0,1003c6f0,369,0,unknown" in cgame_functions

	for expected in (
		"004b71c0    int32_t __fastcall sub_4b71c0(int32_t arg1)",
		"004b71d3  if (result != 0x60 && result != 0x7e)",
		"004b71f4      result = WideCharToMultiByte(CodePage: 0xfde9, dwFlags: 0,",
		"004b722a              if ((result.b & 0x20) == 0 || (result.b & 1) != 0)",
		"004b724f                      (*(data_146cc18 + 8))(sx.d(*(&multiByteStr + esi_1)), 1, 1)",
		"004b727b                      sub_4b6890(&data_1647f40, var_14_1)",
		"004b727b                      sub_4b6890(&data_1648c80, *(&multiByteStr + esi_1))",
		"004b7b00    int32_t sub_4b7b00(class Awesomium::JSArray* arg1, void* arg2, int32_t arg3)",
		"004b7b25  *(eax_4 + &data_1648060) = arg2",
		"004b7cff                          int32_t eax_15 = sub_4c8900(2, \"toggle cl_freezeDemo\\n\")",
		"004b7d8a                          int32_t eax_19 = sub_4c8900(2, \"timescale 1\\n\")",
		"004b7d6a                          int32_t eax_18 = sub_4c8900(2, \"cvarAdd timescale -0.1\\n\")",
		"004b7d4a                          int32_t eax_17 = sub_4c8900(2, \"cvarAdd timescale 0.1\\n\")",
		"004b7daa                          int32_t eax_20 = sub_4c8900(2, \"toggle cg_drawDemoHUD\\n\")",
		"004b7dea              int32_t eax_22 = sub_4f3420(arg1, arg2)",
		"004b7e1b              int32_t eax_23 = (*(data_146cc18 + 8))(arg1, 0, arg2)",
		"004b7e4f              int32_t eax_25 = (*(data_146cc38 + 0x1c))(arg1, arg2)",
		"004b7e94              int32_t eax_27 = (*(data_146cc18 + 8))(arg1, 0, arg2)",
	):
		assert expected in host_hlil_part04

	for expected in (
		"004ed050    int32_t sub_4ed050(int32_t arg1, int32_t arg2, int32_t arg3, int32_t arg4, int32_t arg5, int32_t arg6)",
		"004ed077  if (ecx - data_12d51c8 s>= 0x100)",
		"004ed07e      sub_4c9860(eax_1 * 0x18 + &data_12d39c0, \"Sys_QueEvent: overflow\\n\")",
		"004ed0a7  if (eax_3 == 0)",
		"004ed0a9      eax_3 = sub_4ef510()",
		"004ed0b9  *(eax_1 * 0x18 + 0x12d39c4) = arg2",
		"004ed0bf  *(eax_1 * 0x18 + 0x12d39c8) = arg3",
		"004ed191          data_12d3568 = msg.time",
		"004ed1ae              TranslateMessage(lpMsg: &msg)",
		"004ed1b8          DispatchMessageA(lpMsg: &msg)",
		"004f15c0    uint32_t __convention(\"regparm\") sub_4f15c0(int32_t arg1)",
		"004f15c5  uint32_t ecx_1 = zx.d((arg1 s>> 0x10).b)",
		"004f15ce  if (ecx_1 s> 0x7f)",
		"004f15d9  uint32_t result = zx.d(*(ecx_1 + 0x5734b8))",
		"004f15e0  if ((arg1 u>> 0x18 & 1) != 0)",
		"004f15ff              return 0xa1",
		"004f164e                  return 0xaf",
		"004f1654                  return 0xa9",
		"004f165a                  return 0xac",
		"004f19d6              char const* const var_3c_3 = \"vid_restart fast\\n\"",
	):
		assert expected in host_hlil_part05

	for expected in (
		"1000ff40    void sub_1000ff40(int32_t arg1, int32_t arg2, int32_t arg3)",
		"1000ff47  if (data_106b40e4 s> 0)",
		"1000ff6f      if (arg1 == 0x1b && arg2 == 0 && arg3 != 0 && sub_10010380() == 0)",
		"1000ff87      st0_1, eax = sub_10019a10(eax_1, arg1, arg3, arg2)",
		"1000ffad          (*(eax_4 + 0xb0))((*(eax_4 + 0xac))() & 0xfffffffd)",
		"1002aeac  void* data_1002aeac = sub_1000ff40",
	):
		assert expected in ui_hlil

	for expected in (
		"1003c6f0    float* sub_1003c6f0(int32_t arg1, int32_t arg2)",
		"1003c750      (*(data_1074cccc + 0x18c))(arg1, &s, 0x20)",
		"1003c76a      if (sub_10057330(\"messagemode\", 0xb, &s) == 0)",
		"1003c7c0      if (eax_5 == 0 || eax_6 == 0)",
		"1003c7d7      else",
		"100769c4  void* data_100769c4 = sub_1003c6f0",
	):
		assert expected in cgame_hlil

	map_key_block = _extract_function_block(win_wndproc, "static int MapKey (int key)\n{")
	main_wndproc = _extract_function_block(win_wndproc, "LONG WINAPI MainWndProc (")
	sys_que_event_block = _extract_function_block(
		win_main,
		"void Sys_QueEvent( int time, sysEventType_t type, int value, int value2, int ptrLength, void *ptr ) {",
	)
	sys_get_event_block = _extract_function_block(win_main, "sysEvent_t Sys_GetEvent( void ) {")
	event_loop_block = _extract_function_block(common, "int Com_EventLoop( void ) {")
	key_event_block = _extract_function_block(cl_keys, "void CL_KeyEvent (int key, qboolean down, unsigned time) {")
	char_event_block = _extract_function_block(cl_keys, "void CL_CharEvent( int key ) {")
	ui_key_wrapper = _extract_function_block(ui_main, "static void UI_NativeKeyEvent( int key, qboolean down, int time ) {")
	cg_key_wrapper = _extract_function_block(cg_main, "static void CG_NativeKeyEvent( int key, qboolean down ) {")

	assert "modified = ( key >> 16 ) & 255;" in map_key_block
	assert "if ( modified > 127 )" in map_key_block
	assert "if ( key & ( 1 << 24 ) )" in map_key_block
	assert "result = s_scantokey[modified];" in map_key_block
	assert "case K_HOME:" in map_key_block
	assert "return K_KP_HOME;" in map_key_block
	assert "case K_PAUSE:" in map_key_block
	assert "return K_KP_NUMLOCK;" in map_key_block
	assert "case 0x0D:" in map_key_block
	assert "return K_KP_ENTER;" in map_key_block
	assert "case 0x2F:" in map_key_block
	assert "return K_KP_SLASH;" in map_key_block
	assert "case 0xAF:" in map_key_block
	assert "return K_KP_PLUS;" in map_key_block

	assert main_wndproc.index("case WM_SYSKEYDOWN:") < main_wndproc.index("case WM_KEYDOWN:")
	assert "if ( wParam == 13 )" in main_wndproc
	assert 'Cbuf_AddText( "vid_restart fast\\n" );' in main_wndproc
	assert "Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, MapKey( lParam ), qtrue, 0, NULL );" in main_wndproc
	assert "Sys_QueEvent( g_wv.sysMsgTime, SE_KEY, MapKey( lParam ), qfalse, 0, NULL );" in main_wndproc
	assert "Sys_QueEvent( g_wv.sysMsgTime, SE_CHAR, wParam, 0, 0, NULL );" in main_wndproc

	assert 'Com_Printf("Sys_QueEvent: overflow\\n");' in sys_que_event_block
	assert "Z_Free( ev->evPtr );" in sys_que_event_block
	assert "time = Sys_Milliseconds();" in sys_que_event_block
	assert "ev->evTime = time;" in sys_que_event_block
	assert "ev->evType = type;" in sys_que_event_block
	assert "ev->evValue = value;" in sys_que_event_block
	assert "ev->evValue2 = value2;" in sys_que_event_block
	assert "g_wv.sysMsgTime = msg.time;" in sys_get_event_block
	assert "TranslateMessage (&msg);" in sys_get_event_block
	assert "DispatchMessage (&msg);" in sys_get_event_block

	assert "case SE_KEY:" in event_loop_block
	assert "CL_KeyEvent( ev.evValue, ev.evValue2, ev.evTime );" in event_loop_block
	assert "case SE_CHAR:" in event_loop_block
	assert "CL_CharEvent( ev.evValue );" in event_loop_block
	assert "case SE_MOUSE:" in event_loop_block
	assert "CL_MouseEvent( ev.evValue, ev.evValue2, ev.evTime );" in event_loop_block
	assert "case SE_JOYSTICK_AXIS:" in event_loop_block
	assert "CL_JoystickEvent( ev.evValue, ev.evValue2, ev.evTime );" in event_loop_block

	assert "translated = CL_TranslateRetailKeycode( key );" in key_event_block
	assert "keys[key].down = dispatchDown;" in key_event_block
	assert "CL_ToggleMenuInternal( dispatchKey, qfalse, time );" in key_event_block
	assert "CL_HandleDemoPlaybackKeyEvent( key )" in key_event_block
	assert "CL_AddKeyUpCommands( key, kb );" in key_event_block
	assert "CL_DispatchBrowserKeyEvent( dispatchKey, dispatchDown );" in key_event_block
	assert "VM_Call( uivm, UI_KEY_EVENT, dispatchKey, dispatchDown, time );" in key_event_block
	assert "VM_Call( cgvm, CG_KEY_EVENT, dispatchKey, dispatchDown );" in key_event_block
	assert "Console_Key( key );" in key_event_block
	assert "Message_Key( key );" in key_event_block
	assert "Com_sprintf (cmd, sizeof(cmd), \"%s %i %i\\n\", button, key, time);" in key_event_block

	assert "translated = CL_TranslateRetailKeycode( key );" in char_event_block
	assert "byteCount = CL_EncodeUtf8Codepoint( translated.charCode, utf8, sizeof( utf8 ) );" in char_event_block
	assert "Field_CharEvent( &g_consoleField, utf8Byte );" in char_event_block
	assert "CL_WebView_OnKeyEvent( utf8Byte | K_CHAR_FLAG, qtrue );" in char_event_block
	assert "VM_Call( uivm, UI_KEY_EVENT, utf8Byte | K_CHAR_FLAG, qtrue, cls.realtime );" in char_event_block
	assert "Field_CharEvent( &chatField, utf8Byte );" in char_event_block

	assert "(void)time;" in ui_key_wrapper
	assert "_UI_KeyEvent( key, down );" in ui_key_wrapper
	assert "case UI_KEY_EVENT:" in ui_main
	assert "UI_NativeKeyEvent( arg0, arg1 ? qtrue : qfalse, arg2 );" in ui_main
	assert "[UI_NATIVE_EXPORT_KEY_EVENT] = UI_NativeKeyEvent," in ui_main

	assert "CG_KeyEvent( key, down );" in cg_key_wrapper
	assert "case CG_KEY_EVENT:" in cg_main
	assert "CG_NativeKeyEvent( arg0, arg1 ? qtrue : qfalse );" in cg_main
	assert "[CG_NATIVE_EXPORT_KEY_EVENT] = CG_NativeKeyEvent," in cg_main


def test_win32_mainwndproc_raw_input_bridge_is_pinned_to_retail_hlil() -> None:
	aliases = json.loads(ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]
	functions = GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	hlil = HLIL_PART05.read_text(encoding="utf-8")
	win_wndproc = WIN_WNDPROC.read_text(encoding="utf-8")
	win_input = WIN_INPUT.read_text(encoding="utf-8")
	main_wndproc = _extract_function_block(win_wndproc, "LONG WINAPI MainWndProc (")
	raw_event_block = _extract_function_block(win_input, "void IN_RawInputEvent( WPARAM wParam, LPARAM lParam ) {")
	wm_input_case = main_wndproc[
		main_wndproc.index("case WM_INPUT:") : main_wndproc.index("case WM_MOUSEWHEEL:")
	]

	for raw_name in ("FUN_004f1750", "sub_4F1750", "sub_4f1750"):
		assert aliases[raw_name] == "MainWndProc"

	assert "FUN_004f1750,004f1750,404,0,unknown" in functions

	for expected in (
		"004f1750    int32_t __stdcall sub_4f1750(HWND arg1, int32_t arg2, int32_t arg3, HRAWINPUT arg4)",
		"004f1778  if (eax_3 == 0)",
		"004f177f      eax_4 = 0",
		"004f1a68      case 0xff",
		"004f1a95          if (GetRawInputData(hRawInput: arg4, uiCommand: RID_INPUT, pData: nullptr,",
		"004f1ac1          if (pcbSize_2 u<= 0x400)",
		"004f1ac3          var_34 = pcbSize_2",
		"004f1b34          if (*pData == 0)",
		"004f1b48              sub_4ebaa0(*(pData + 0x1c), ecx_13, eax_31, var_34.w)",
	):
		assert expected in hlil

	assert "case WM_INPUT:" in wm_input_case
	assert wm_input_case.index("case WM_INPUT:") < wm_input_case.index("IN_RawInputEvent( wParam, lParam );")
	assert wm_input_case.index("IN_RawInputEvent( wParam, lParam );") < wm_input_case.index(
		"return DefWindowProcW( hWnd, uMsg, wParam, lParam );"
	)
	assert "GET_RAWINPUT_CODE_WPARAM( wParam ) != RIM_INPUT" in raw_event_block
	assert "BYTE\t\t\t\t\t\tstackBuffer[0x400];" in raw_event_block
	assert raw_event_block.count("GetRawInputData(") == 2
	assert "rawInputSize > sizeof( stackBuffer )" in raw_event_block
	assert "rawInputHeap = (PRAWINPUT)malloc( rawInputSize );" in raw_event_block
	assert "free( rawInputHeap );" in raw_event_block
	assert "QLR_Win32RawInputExtractMouseSample( rawInput, &sample )" in raw_event_block
	assert "IN_RawInputAppendSample( &sample );" in raw_event_block


def test_win32_fallback_mouse_messages_include_xbutton_state_bits() -> None:
	win_wndproc = WIN_WNDPROC.read_text(encoding="utf-8")
	main_wndproc = _extract_function_block(win_wndproc, "LONG WINAPI MainWndProc (")

	assert "#define WM_XBUTTONDOWN 0x020B" in win_wndproc
	assert "#define WM_XBUTTONUP 0x020C" in win_wndproc
	assert "#define MK_XBUTTON1 0x0020" in win_wndproc
	assert "#define MK_XBUTTON2 0x0040" in win_wndproc
	assert "case WM_XBUTTONDOWN:" in main_wndproc
	assert "case WM_XBUTTONUP:" in main_wndproc
	assert "wParam & MK_XBUTTON1" in main_wndproc
	assert "temp |= 8;" in main_wndproc
	assert "wParam & MK_XBUTTON2" in main_wndproc
	assert "temp |= 16;" in main_wndproc


def test_win32_input_restart_command_matches_retail_registration_and_handler() -> None:
	win_main = WIN_MAIN.read_text(encoding="utf-8")

	sys_init_block = _extract_function_block(win_main, "void Sys_Init( void ) {")
	restart_block = _extract_function_block(win_main, "void Sys_In_Restart_f( void ) {")

	assert 'Cmd_AddCommand ("in_restart", Sys_In_Restart_f);' in sys_init_block
	assert "IN_Shutdown();" in restart_block
	assert "IN_Init();" in restart_block
