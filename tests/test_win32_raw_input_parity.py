from __future__ import annotations

import ctypes
import os
import re
from pathlib import Path

import pytest

from tests.compiler_support import compile_c_binary, find_c_compiler, shared_library_name

REPO_ROOT = Path(__file__).resolve().parent.parent
WIN_INPUT = REPO_ROOT / "src" / "code" / "win32" / "win_input.c"
WIN_LOCAL = REPO_ROOT / "src" / "code" / "win32" / "win_local.h"
WIN_MAIN = REPO_ROOT / "src" / "code" / "win32" / "win_main.c"
WIN_WNDPROC = REPO_ROOT / "src" / "code" / "win32" / "win_wndproc.c"
CL_KEYS = REPO_ROOT / "src" / "code" / "client" / "cl_keys.c"
KEYCODES = REPO_ROOT / "src" / "code" / "ui" / "keycodes.h"

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
	main_wndproc = _extract_function_block(win_wndproc, "LONG WINAPI MainWndProc (")

	assert "ListInputDevices is only supported for Raw Input (in_mouse 2).\\n" in list_block
	assert "GetRawInputDeviceList" in list_block
	assert "GetRawInputDeviceInfoA" in list_block
	assert "Raw Input Mouse Devices: \\n" in list_block

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
	relative_block = _extract_function_block(win_input, "static qboolean IN_ShouldUseRelativeMouse( void ) {")
	window_block = _extract_function_block(win_input, "static void IN_WindowMouse( void ) {")
	mouse_move_block = _extract_function_block(win_input, "void IN_MouseMove ( void ) {")
	frame_block = _extract_function_block(win_input, "void IN_Frame (void) {")

	assert "SM_CXVIRTUALSCREEN" in activate_block
	assert "SM_CYVIRTUALSCREEN" in activate_block
	assert 'Cvar_SetValue( "vid_xpos", (float)window_rect.left );' in activate_block
	assert 'Cvar_SetValue( "vid_ypos", (float)window_rect.top );' in activate_block

	assert "!s_wmv.mouseActive" in relative_block
	assert "KEYCATCH_MESSAGE | KEYCATCH_RETAIL_MOUSEPASS" in relative_block
	assert "in_nograb && in_nograb->integer" in relative_block
	assert "ScreenToClient( g_wv.hWnd, &current_pos );" in window_block
	assert "oldCursorX" in window_block
	assert "oldCursorY" in window_block
	assert "Sys_QueEvent( 0, SE_MOUSE, current_pos.x, current_pos.y, 0, NULL );" in window_block

	assert "if ( !IN_ShouldUseRelativeMouse() ) {" in mouse_move_block
	assert "IN_WindowMouse();" in mouse_move_block
	assert len(re.findall(r"IN_DeactivateMouse\s*\(\s*\);\s*IN_MouseMove\s*\(\s*\);", frame_block)) >= 3


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
	di_block = _extract_function_block(win_input, "void IN_DIMouse( int *mx, int *my ) {")
	mouse_event_block = _extract_function_block(win_input, "void IN_MouseEvent (int mstate)\n{")

	assert "#define DINPUT_BUFFERSIZE           0x200" in win_input
	assert "#define DIMOFS_BUTTON7              (DIMOFS_BUTTON0 + 7)" in win_input
	assert "bButtonH" in win_input
	assert "DIDEVICEOBJECTDATA\tod[DINPUT_BUFFERSIZE];" in di_block
	assert "IDirectInputDevice_GetDeviceData( g_pMouse, sizeof( DIDEVICEOBJECTDATA ), od, &dwElements, 0 );" in di_block
	assert "DI_BUFFEROVERFLOW" in di_block
	assert "*mx += (int)od[i].dwData;" in di_block
	assert "*my += (int)od[i].dwData;" in di_block
	assert "DIMOFS_BUTTON7" in di_block
	assert "K_MOUSE1 + (int)( od[i].dwOfs - DIMOFS_BUTTON0 )" in di_block
	assert "IDirectInputDevice_GetDeviceState" not in di_block
	assert "i < 8" in mouse_event_block


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
