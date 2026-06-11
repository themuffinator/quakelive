from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SYMBOL_ALIASES_PATH = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
QL_STEAM_FUNCTIONS_CSV_PATH = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
)
QL_STEAM_HLIL_PART01_PATH = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part01.txt"
)
QL_STEAM_HLIL_PART02_PATH = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part02.txt"
)
QL_STEAM_HLIL_PART04_PATH = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part04.txt"
)
QL_STEAM_HLIL_PART05_PATH = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part05.txt"
)
QL_STEAM_HLIL_PART06_PATH = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part06.txt"
)
QL_STEAM_HLIL_PART07_PATH = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part07.txt"
)
QL_STEAM_HLIL_PART19_PATH = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part19.txt"
)
QL_STEAM_ANALYSIS_SYMBOLS_PATH = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "analysis_symbols.txt"
)
AWESOMIUM_PROCESS_METADATA_PATH = (
	REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "awesomium_process" / "metadata.txt"
)
AWESOMIUM_PROCESS_FUNCTIONS_CSV_PATH = (
	REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "awesomium_process" / "functions.csv"
)
AWESOMIUM_PROCESS_IMPORTS_PATH = (
	REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "awesomium_process" / "imports.txt"
)
AWESOMIUM_PROCESS_EXPORTS_PATH = (
	REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "awesomium_process" / "exports.txt"
)
AWESOMIUM_PROCESS_DECOMPILE_TOP_FUNCTIONS_PATH = (
	REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "awesomium_process" / "decompile_top_functions.c"
)
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
COMMON_C_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "common.c"
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


def _aliases() -> dict[str, str]:
	return json.loads(_read_text(SYMBOL_ALIASES_PATH))["quakelive_steam_srp"]


def _function_rows() -> dict[int, dict[str, str]]:
	return _function_rows_from(QL_STEAM_FUNCTIONS_CSV_PATH)


def _function_rows_from(path: Path) -> dict[int, dict[str, str]]:
	rows: dict[int, dict[str, str]] = {}
	with path.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			rows[int(row["entry"], 16)] = row
	return rows


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


def _assert_ordered_anchors(text: str, anchors: tuple[str, ...]) -> None:
	cursor = -1
	for anchor in anchors:
		next_cursor = text.find(anchor, cursor + 1)
		if next_cursor == -1:
			raise AssertionError(f"ordered anchor not found after offset {cursor}: {anchor}")
		cursor = next_cursor


def test_awesomium_webui_ghidra_and_binary_ninja_alias_bridge_is_pinned() -> None:
	aliases = _aliases()
	rows = _function_rows()
	cl_cgame = _read_text(CL_CGAME_PATH)
	hlil_part01 = _read_text(QL_STEAM_HLIL_PART01_PATH)
	hlil_part05 = _read_text(QL_STEAM_HLIL_PART05_PATH)

	expected_rows = {
		0x00431510: ("CGameID_IsValid", 74),
		0x00431570: ("QLJSHandler_LookupMethodId", 199),
		0x00431640: ("QLDialogHandler_OnShowFileChooser", 20),
		0x00431660: ("AwesomiumListener_NoEngineCallback", 3),
		0x00431670: ("QLViewHandler_OnChangeCursor", 52),
		0x004317B0: ("QLViewHandler_NoEngineCallback", 3),
		0x004317C0: ("QLResourceInterceptor_NoEngineCallback", 3),
		0x004317D0: ("QLLoadHandler_OnBeginLoadingFrame", 10),
		0x004317E0: ("QLLoadHandler_OnFinishLoadingFrame", 10),
		0x004317F0: ("QLLoadHandler_OnDocumentReady", 544),
		0x00431A10: ("QLJSHandler_BindQzInstance", 674),
		0x00431E50: ("QLJSHandler_OnMethodCall", 241),
		0x004328B0: ("QLJSHandler_OnMethodCallWithReturnValue", 284),
		0x00434450: ("QLViewHandler_OnChangeTooltip", 206),
		0x00434520: ("QLViewHandler_OnAddConsoleMessage", 219),
		0x00434600: ("QLResourceInterceptor_OnFilterNavigation", 32),
		0x00434620: ("QLResourceInterceptor_OnRequest", 1204),
		0x00434AE0: ("QLLoadHandler_OnFailLoadingFrame", 222),
		0x004F1EF0: ("AdvertisementBridge_SetActiveAdvert", 21),
		0x004F1F10: ("AdvertisementBridge_SetAppActivation", 26),
		0x004F1F30: ("AdvertisementBridge_SetClientStateFlags", 31),
		0x004F1F50: ("AdvertisementBridge_SetFrameTime", 31),
		0x004F1F70: ("AdvertisementBridge_UpdateViewParameters", 74),
		0x004F1FC0: ("AdvertisementBridge_Reserved1FC0", 31),
		0x004F1FE0: ("AdvertisementBridge_SetMapPath", 31),
		0x004F2040: ("AdvertisementBridge_GetCellLabel", 51),
		0x004F2080: ("AdvertisementBridge_GetCellDisplayState", 30),
		0x004F20A0: ("AdvertisementBridge_SetVisibilityTraceCallback", 26),
		0x004F20E0: ("AdvertisementBridge_SetupUIAdvertCellShader", 53),
		0x004F2120: ("AdvertisementBridge_RefreshUIAdvertCellShader", 53),
		0x004F2160: ("AdvertisementBridge_GetLabelList1Count", 20),
		0x004F2180: ("AdvertisementBridge_GetLabelList1Entry", 51),
		0x004F21E0: ("AdvertisementBridge_SetupAdvertCellShader", 53),
		0x004F2220: ("AdvertisementBridge_RefreshAdvertCellShader", 53),
		0x004F2260: ("AdvertisementBridge_GetLabelList2Count", 20),
		0x004F2280: ("AdvertisementBridge_GetLabelList2Entry", 51),
		0x004F22C0: ("AdvertisementBridge_ActivateAdvert", 26),
		0x004F22E0: ("AdvertisementBridge_IsDelayElapsed", 34),
		0x004F2310: ("AdvertisementBridge_ClearDelay", 11),
		0x004F23B0: ("QLJSHandler_Destroy", 34),
		0x004F23E0: ("QLWebView_SetLocationHash", 234),
		0x004F24D0: ("QLWebHost_HideBrowser", 182),
		0x004F2590: ("QLWebCore_Update", 46),
		0x004F25C0: ("QLWebView_Resize", 35),
		0x004F25F0: ("QLWebView_RebuildSurfaceImage", 345),
		0x004F2750: ("QLWebView_InjectMouseMove", 100),
		0x004F27C0: ("QLWebView_InjectMouseDown", 89),
		0x004F2820: ("QLWebView_InjectMouseUp", 67),
		0x004F2870: ("QLWebView_InjectMouseWheel", 42),
		0x004F28A0: ("QLWebView_InjectKeyboardEvent", 93),
		0x004F2900: ("QLWebView_InjectActivationKeyboardEvent", 77),
		0x004F2950: ("QLWebView_InvokeCommNotice", 192),
		0x004F2A60: ("QLWebHost_Shutdown", 32),
		0x004F2A80: ("QLResourceInterceptor_Destroy", 35),
		0x004F2AB0: ("QLDialogHandler_Destroy", 35),
		0x004F2AE0: ("QLViewHandler_Destroy", 35),
		0x004F2B10: ("QLLoadHandler_Destroy", 35),
		0x004F2B40: ("QLWebHost_PumpFrame", 487),
		0x004F2D30: ("QLWebHost_OpenURL", 1024),
		0x004F3130: ("AwesomiumDataPakSource_Destroy", 34),
		0x004F3160: ("QLWebHost_OpenRelativeURL", 107),
		0x004F31D0: ("QLWebHost_NavigateOrOpen", 129),
		0x004F3260: ("QLWebView_PublishEvent", 448),
		0x004F3420: ("QLWebView_PublishGameKey", 332),
		0x004F3570: ("QLWebView_PublishGameError", 138),
		0x004F3600: ("QLWebView_PublishGameEnd", 40),
		0x004F3630: ("QLWebView_PublishCvarChange", 391),
		0x004F37C0: ("QLWebView_PublishBindChanged", 300),
		0x004F38F0: ("QLWebView_PublishGameStart", 667),
		0x004F3B90: ("QLWebView_PublishGameDemo", 134),
		0x004F3C20: ("QLWebView_PublishGameScreenshot", 134),
		0x004F3CD0: ("QLWebHost_RegisterCommands", 158),
	}

	for address, (owner, size) in expected_rows.items():
		fun_key = f"FUN_{address:08x}"
		upper_sub_key = f"sub_{address:06X}"
		lower_sub_key = f"sub_{address:06x}"
		row = rows[address]

		assert aliases[fun_key] == owner
		assert aliases[upper_sub_key] == owner
		assert aliases[lower_sub_key] == owner
		assert row["name"] == fun_key
		assert int(row["size"]) == size

	for binary_ninja_only_address in (0x004F2000, 0x004F2020, 0x004F20C0):
		assert f"FUN_{binary_ninja_only_address:08x}" not in aliases
		assert binary_ninja_only_address not in rows

	assert aliases["sub_4F2000"] == "AdvertisementBridge_InitCGame"
	assert aliases["sub_4f2000"] == "AdvertisementBridge_InitCGame"
	assert aliases["sub_4F2020"] == "AdvertisementBridge_ShutdownCGame"
	assert aliases["sub_4f2020"] == "AdvertisementBridge_ShutdownCGame"
	assert aliases["sub_4F20C0"] == "AdvertisementBridge_InitUI"
	assert aliases["sub_4f20c0"] == "AdvertisementBridge_InitUI"
	assert "QL_WEB_BRIDGE_SLOT_RESERVED_1FC0 = 0x1c," in cl_cgame
	assert "QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( reserved1FC0, QL_WEB_BRIDGE_SLOT_RESERVED_1FC0 );" in cl_cgame
	assert "static int QLWebBridge_Reserved1FC0( ql_web_bridge_t *bridge, int value ) {" in cl_cgame

	for hlil_anchor in (
		"004317f0    int32_t __stdcall sub_4317f0(int32_t* arg1)",
		"004319ea      sub_4f3260(Awesomium::WebString::~WebString, edi, \"web.object.ready\", nullptr)",
		"00434620    class Awesomium::ResourceResponse* __stdcall sub_434620(int32_t* arg1)",
	):
		assert hlil_anchor in hlil_part01

	for hlil_anchor in (
		"004f1fc0    int32_t sub_4f1fc0(int32_t arg1)",
		"004f1fd9  return (*(*ecx + 0x1c))(arg1)",
		"004f2d30    HCURSOR sub_4f2d30(uint32_t arg1)",
		"004f2d71          eax, ecx_2 = Awesomium::WebCore::Initialize(&var_3c)",
		"004f3260    bool sub_4f3260(class Awesomium::JSArray* arg1 @ esi, class Awesomium::WebString* arg2 @ edi, uint32_t arg3, int32_t* arg4)",
		"004f3407      eax_17 = sub_4c9860(esi, \"PublishEvent failed: no view\\n\")",
	):
		assert hlil_anchor in hlil_part05


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
	assert "CL_WebHost_NormalizeHash( hash, normalizedHash, sizeof( normalizedHash ) );" in navigate_block
	assert "CL_WebHost_BuildCurrentURL( normalizedHash, expectedUrl, sizeof( expectedUrl ) );" in navigate_block
	assert "if ( cl_webHost.viewInitialised && !Q_stricmp( cl_webHost.currentUrl, expectedUrl ) ) {" in navigate_block
	assert "if ( !QLWebView_SetLocationHash( normalizedHash ) ) {" in navigate_block
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


def test_awesomium_pending_state_requires_requested_browser_without_drawable_surface() -> None:
	cl_cgame = _read_text(CL_CGAME_PATH)

	pending_block = _extract_function_block(
		cl_cgame, "static qboolean CL_WebHost_AwesomiumPending( qboolean awesomiumAllowed ) {"
	)
	bridge_block = _extract_function_block(cl_cgame, "void CL_RefreshOnlineServicesBridgeState( void ) {")
	register_block = _extract_function_block(cl_cgame, "void QLWebHost_RegisterCommands( void ) {")

	assert "if ( !awesomiumAllowed || cl_webHost.loadFailed ) {" in pending_block
	assert "!cl_webBrowserVisible" in pending_block
	assert "!cl_webHost.browserVisible" in pending_block
	assert "!cl_webHost.browserActive" in pending_block
	assert "!cl_webHost.loadingDocument" in pending_block
	assert "return CL_WebHost_SurfaceReadyForOverlay( qtrue ) ? qfalse : qtrue;" in pending_block
	assert "qboolean awesomiumPending = CL_WebHost_AwesomiumPending( awesomiumAllowed );" in bridge_block
	assert 'CL_SetCvarIfChanged( "ui_browserAwesomiumPending", awesomiumPending ? "1" : "0" );' in bridge_block
	assert 'Cvar_Set( "ui_browserAwesomiumPending", CL_WebHost_AwesomiumPending( CL_AwesomiumRuntimeActive() ) ? "1" : "0" );' in register_block
	assert '( awesomiumAllowed && !cl_webHost.loadFailed ) ? "1" : "0"' not in cl_cgame


def test_awesomium_default_menu_launch_retail_winmain_bootstrap_flow_is_pinned() -> None:
	rows = _function_rows()
	aliases = _aliases()
	hlil_part05 = _read_text(QL_STEAM_HLIL_PART05_PATH)
	hlil_part06 = _read_text(QL_STEAM_HLIL_PART06_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_main = _read_text(CL_MAIN_PATH)
	common = _read_text(COMMON_C_PATH)

	for address, owner, size in (
		(0x004ED830, "WinMain", 598),
		(0x00460510, "SteamClient_IsInitialized", 6),
		(0x004F2D30, "QLWebHost_OpenURL", 1024),
	):
		assert aliases[f"FUN_{address:08x}"] == owner
		assert aliases[f"sub_{address:06X}"] == owner
		assert aliases[f"sub_{address:06x}"] == owner
		assert rows[address]["name"] == f"FUN_{address:08x}"
		assert int(rows[address]["size"]) == size

	_assert_ordered_anchors(
		hlil_part05,
		(
			"004ed830    int32_t __stdcall sub_4ed830",
			"data_12d34b8 = arg1",
			"sub_4ef520()",
			"sub_4f0d70()",
			"sub_4f0260()",
			"SetErrorMode(uMode: SEM_FAILCRITICALERRORS)",
			"sub_4cbfd0(edi, eax_4, 0)",
			"sub_4ef320()",
			"sub_4f4140()",
			'CreateWindowExA(dwExStyle: WS_EX_LEFT, lpClassName: "tooltips_class32"',
			"SetWindowPos(hWnd, hWndInsertAfter: 0xfffffffe",
			"SendMessageA(hWnd: data_12d34b0, Msg: 0x404",
			"SendMessageA(hWnd: data_12d34b0, Msg: 0x401",
			"if (sub_460510() != 0 && *(data_1205e28 + 0x30) == 0)",
			'sub_4f2d30("asset://ql/index.html")',
			"while (true)",
			"sub_4ef510()",
			"sub_4ec4f0()",
			"sub_4cc6c0()",
			"data_12d51c0 += 1",
		),
	)
	_assert_ordered_anchors(
		hlil_part06,
		(
			'005472fc  char const data_5472fc[0x16] = "asset://ql/index.html", 0',
			'00548078  char const data_548078[0x8] = "web.pak", 0',
		),
	)

	client_init_block = _extract_function_block(cl_main, "void CL_Init( void ) {")
	client_shutdown_block = _extract_function_block(cl_main, "void CL_Shutdown( void ) {")
	common_frame_block = _extract_function_block(common, "void Com_Frame( void ) {")
	service_available_block = _extract_function_block(
		cl_cgame, "static qboolean CL_BrowserHostServiceAvailable( void ) {"
	)
	bootstrap_allowed_block = _extract_function_block(
		cl_cgame, "static qboolean CL_WebHost_ShouldBootstrapMenu( void ) {"
	)
	bootstrap_block = _extract_function_block(
		cl_cgame, "void CL_WebHost_BootstrapAwesomiumMenu( void ) {"
	)
	frame_block = _extract_function_block(cl_cgame, "void CL_WebHost_Frame( void ) {")
	bridge_block = _extract_function_block(cl_cgame, "void CL_RefreshOnlineServicesBridgeState( void ) {")

	_assert_ordered_anchors(
		client_init_block,
		(
			"CL_RefreshPlatformServiceCvars();",
			"CL_InitSteamResources();",
			"CL_WebHost_Init();",
			"QLWebHost_RegisterCommands();",
			"CL_WebPak_Init();",
			"CL_InitRef();",
			"SCR_Init ();",
			"CL_WebHost_BootstrapAwesomiumMenu();",
			"Cbuf_Execute ();",
		),
	)
	_assert_ordered_anchors(
		client_shutdown_block,
		(
			"CL_Disconnect( qtrue );",
			"S_Shutdown();",
			"CL_ShutdownRef();",
			"CL_Steam_ShutdownCallbacks();",
			"CL_WebHost_Shutdown();",
			"CL_WebPak_Shutdown();",
			"CL_ShutdownUI();",
			"CL_ShutdownSteamResources();",
		),
	)
	_assert_ordered_anchors(
		common_frame_block,
		(
			"Com_EventLoop();",
			"Cbuf_Execute ();",
			"CL_WebHost_Frame();",
			"SteamClient_Frame();",
			"CL_Frame( msec );",
		),
	)
	_assert_ordered_anchors(
		service_available_block,
		(
			"if ( !CL_BrowserRuntimeRequested() ) {",
			"return qfalse;",
			"return CL_OverlayServiceAvailable() || CL_AwesomiumRuntimeAllowed();",
		),
	)
	assert "return cls.state == CA_DISCONNECTED || cls.state == CA_CINEMATIC;" in bootstrap_allowed_block
	_assert_ordered_anchors(
		bootstrap_block,
		(
			"CL_AwesomiumValidateRequiredRuntime();",
			"CL_RefreshOnlineServicesBridgeState();",
			"awesomiumAllowed = CL_AwesomiumRuntimeActive();",
			"if ( !awesomiumAllowed",
			"|| !CL_WebHost_ShouldBootstrapMenu()",
			"|| cl_webHost.loadFailed",
			"|| cls.glconfig.vidWidth <= 0",
			"|| cls.glconfig.vidHeight <= 0 ) {",
			"if ( cl_webHost.liveAwesomium ) {",
			"if ( cl_webHost.coreInitialised || cl_webHost.viewInitialised ) {",
			"CL_WebHost_ResetRuntime( qfalse );",
			"cl_webBrowserVisible = qtrue;",
			"cl_webBrowserHash[0] = '\\0';",
			"if ( !QLWebHost_OpenURL( CL_WEB_DEFAULT_URL ) ) {",
			"CL_WebHost_MarkBrowserUnavailable();",
		),
	)
	_assert_ordered_anchors(
		frame_block,
		(
			"CL_RefreshOnlineServicesBridgeState();",
			"if ( !CL_BrowserHostServiceAvailable() ) {",
			"CL_WebHost_ResetRuntime( qtrue );",
			"CL_WebHost_BootstrapAwesomiumMenu();",
			"if ( cl_webBrowserVisible ) {",
			"CL_WebHost_BuildCurrentURL( cl_webBrowserHash, expectedUrl, sizeof( expectedUrl ) );",
			"if ( !cl_webHost.viewInitialised ) {",
			"if ( cl_webBrowserHash[0] ) {",
			"QLWebHost_OpenRelativeURL( cl_webBrowserHash )",
			"QLWebHost_OpenURL( CL_WEB_DEFAULT_URL );",
			"if ( !cl_webHost.browserActive ) {",
			"CL_WebHost_MarkBrowserUnavailable();",
			"} else if ( Q_stricmp( cl_webHost.currentUrl, expectedUrl ) ) {",
			"QLWebHost_NavigateOrOpen( cl_webBrowserHash )",
			"cl_webHost.browserVisible = qtrue;",
			"cl_webHost.browserActive = qtrue;",
			"cl_webHost.focused = qtrue;",
			"} else if ( cl_webHost.browserVisible || cl_webHost.browserActive ) {",
			"QLWebHost_HideBrowser();",
			'CL_SetCvarIfChanged( "web_browserActive", "0" );',
			"QLWebCore_Update();",
			"QLWebHost_PumpFrame();",
			"CL_WebHost_CheckLiveAwesomiumSurfaceFailure();",
			"CL_WebHost_UpdateOverlayOwnership();",
		),
	)
	_assert_ordered_anchors(
		bridge_block,
		(
			"qboolean browserRequested = CL_BrowserRuntimeRequested();",
			"qboolean awesomiumAllowed = CL_AwesomiumRuntimeActive();",
			"qboolean overlayAvailable = browserRequested && CL_OverlayServiceAvailable();",
			"qboolean browserAvailable = overlayAvailable || awesomiumAllowed;",
			"qboolean awesomiumPending = CL_WebHost_AwesomiumPending( awesomiumAllowed );",
			'CL_SetCvarIfChanged( "ui_browserAwesomium", browserAvailable ? "1" : "0" );',
			'CL_SetCvarIfChanged( "ui_browserAwesomiumPending", awesomiumPending ? "1" : "0" );',
			'CL_SetCvarIfChanged( "ui_browserAwesomiumProvider", awesomiumAllowed ? "Awesomium WebCore" : overlayProvider );',
			'CL_SetCvarIfChanged( "ui_browserAwesomiumPolicy", awesomiumAllowed ? "runtime-opt-in" : overlayPolicy );',
			"if ( !browserAvailable ) {",
			"CL_WebHost_ResetRuntime( qtrue );",
		),
	)


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
	assert "#define QL_WEB_KEYBOARD_EVENT_KEYDOWN_TYPE 0u" in cl_cgame
	assert "#define QL_WEB_KEYBOARD_EVENT_KEYUP_TYPE 1u" in cl_cgame
	assert "#define QL_WEB_KEYBOARD_EVENT_CHAR_TYPE 2u" in cl_cgame
	assert "if ( key & K_CHAR_FLAG ) {" in inject_keyboard_block
	assert "CL_Awesomium_InjectKeyboardEvent( QL_WEB_KEYBOARD_EVENT_CHAR_TYPE, (unsigned int)( key & ~K_CHAR_FLAG ), 0 );" in inject_keyboard_block
	assert "down ? QL_WEB_KEYBOARD_EVENT_KEYDOWN_TYPE : QL_WEB_KEYBOARD_EVENT_KEYUP_TYPE" in inject_keyboard_block
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


def test_awesomium_input_injection_retail_hlil_flow_is_pinned() -> None:
	rows = _function_rows()
	aliases = _aliases()
	hlil_part05 = _read_text(QL_STEAM_HLIL_PART05_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_input = _read_text(CL_INPUT_PATH)
	cl_keys = _read_text(CL_KEYS_PATH)
	cl_main = _read_text(CL_MAIN_PATH)
	cl_awesomium = _read_text(CL_AWESOMIUM_WIN32_PATH)
	client_h = _read_text(CLIENT_H_PATH)

	for address, owner, size in (
		(0x004F2750, "QLWebView_InjectMouseMove", 100),
		(0x004F27C0, "QLWebView_InjectMouseDown", 89),
		(0x004F2820, "QLWebView_InjectMouseUp", 67),
		(0x004F2870, "QLWebView_InjectMouseWheel", 42),
		(0x004F28A0, "QLWebView_InjectKeyboardEvent", 93),
		(0x004F2900, "QLWebView_InjectActivationKeyboardEvent", 77),
		(0x004F2950, "QLWebView_InvokeCommNotice", 192),
	):
		assert aliases[f"FUN_{address:08x}"] == owner
		assert aliases[f"sub_{address:06X}"] == owner
		assert aliases[f"sub_{address:06x}"] == owner
		assert rows[address]["name"] == f"FUN_{address:08x}"
		assert int(rows[address]["size"]) == size

	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f2750    int32_t sub_4f2750(int32_t arg1, int32_t arg2)",
			"float.t(arg1) / float.t(data_1743bcc) * float.t(data_12d3070)",
			"data_12d3054 = eax",
			"float.t(arg2) / float.t(data_1743bd0) * float.t(data_12d3074)",
			"data_12d3048 = result",
			"if (ecx != 0 && data_12d34bc != 0 && (data_1528ba4 & 1) == 0)",
			"return (*(*ecx + 0xd0))(eax, result)",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f27c0    void sub_4f27c0(int32_t arg1)",
			"int32_t esi_2 = arg1 - 0xb2",
			"if (esi_2 == 2)",
			"esi_2 = 1",
			"else if (esi_2 == 1)",
			"esi_2 = 2",
			"(*(*ecx + 0xd0))(data_12d3054, data_12d3048)",
			"(*(*data_12d3050 + 0xd4))(esi_2)",
			"004f2820    void sub_4f2820(int32_t arg1)",
			"int32_t eax_2 = arg1 - 0xb2",
			"if (eax_2 == 2)",
			"(*(*ecx + 0xd8))(1)",
			"if (eax_2 == 1)",
			"eax_2 = 2",
			"(*(*ecx + 0xd8))(eax_2)",
			"004f2870    void sub_4f2870(int32_t arg1)",
			"(*(*ecx + 0xdc))(arg1 * 0x1e, 0)",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f28a0    int32_t sub_4f28a0(uint32_t arg1, Awesomium::WebKeyboardEvent* arg2, long arg3)",
			"if (data_12d3050 != 0)",
			"result.b = data_1528ba4",
			"if ((result.b & 0x20) != 0 && (result.b & 1) == 0)",
			"Awesomium::WebKeyboardEvent::WebKeyboardEvent(this: arg2, arg1, arg2, arg3)",
			"result = (*(*data_12d3050 + 0xe0))(&var_40)",
			"004f2900    int32_t sub_4f2900()",
			"Awesomium::WebKeyboardEvent::WebKeyboardEvent(this: ecx, 0, 0x11, 0x1d0001)",
			"result = (*(*data_12d3050 + 0xe0))(&var_40)",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f2950    void sub_4f2950(uint32_t arg1)",
			"Awesomium::JSValue::IsUndefined(this: &data_12d3078)",
			"Awesomium::JSValue::JSValue(this: Awesomium::JSArray::JSArray(this: ecx_1), 0)",
			"Awesomium::JSArray::Push(this: ecx_3, eax_1)",
			"sub_4314d0(&var_10, arg1)",
			"Awesomium::JSValue::JSValue(this: ecx_5, eax_3)",
			"sub_4314d0(&var_10, \"OnCommNotice\")",
			"Awesomium::JSObject::InvokeAsync(",
		),
	)

	map_button_block = _extract_function_block(cl_cgame, "static int CL_WebHost_MapMouseButton( int key ) {")
	inject_mouse_block = _extract_function_block(cl_cgame, "static void QLWebView_InjectMouseMove( int x, int y ) {")
	inject_down_block = _extract_function_block(cl_cgame, "static void QLWebView_InjectMouseDown( int key ) {")
	inject_up_block = _extract_function_block(cl_cgame, "static void QLWebView_InjectMouseUp( int key ) {")
	inject_wheel_block = _extract_function_block(cl_cgame, "static void QLWebView_InjectMouseWheel( int direction ) {")
	inject_keyboard_block = _extract_function_block(cl_cgame, "static void QLWebView_InjectKeyboardEvent( int key, qboolean down ) {")
	inject_fields_block = _extract_function_block(
		cl_cgame, "static void QLWebView_InjectKeyboardEventFields( const qlWebKeyboardEventFields_t *event, qboolean down ) {"
	)
	inject_activation_block = _extract_function_block(
		cl_cgame, "static void QLWebView_InjectActivationKeyboardEvent( void ) {"
	)
	on_mouse_move_block = _extract_function_block(cl_cgame, "void CL_WebView_OnMouseMove( int x, int y ) {")
	on_mouse_button_block = _extract_function_block(cl_cgame, "void CL_WebView_OnMouseButtonEvent( int key, qboolean down ) {")
	on_mouse_wheel_block = _extract_function_block(cl_cgame, "void CL_WebView_OnMouseWheelEvent( int direction ) {")
	on_key_block = _extract_function_block(cl_cgame, "void CL_WebView_OnKeyEvent( int key, qboolean down ) {")
	mouse_event_block = _extract_function_block(cl_input, "void CL_MouseEvent( int dx, int dy, int time ) {")
	dispatch_key_block = _extract_function_block(cl_keys, "static void CL_DispatchBrowserKeyEvent( int key, qboolean down ) {")
	publish_comm_block = _extract_function_block(cl_main, "void CL_WebView_InvokeCommNotice( const char *message ) {")
	mouse_move_adapter_block = _extract_function_block(
		cl_awesomium, 'extern "C" void CL_Awesomium_InjectMouseMove( int x, int y ) {'
	)
	mouse_down_adapter_block = _extract_function_block(
		cl_awesomium, 'extern "C" void CL_Awesomium_InjectMouseDown( int button ) {'
	)
	mouse_up_adapter_block = _extract_function_block(
		cl_awesomium, 'extern "C" void CL_Awesomium_InjectMouseUp( int button ) {'
	)
	mouse_wheel_adapter_block = _extract_function_block(
		cl_awesomium, 'extern "C" void CL_Awesomium_InjectMouseWheel( int direction ) {'
	)
	keyboard_adapter_block = _extract_function_block(
		cl_awesomium, 'extern "C" void CL_Awesomium_InjectKeyboardEvent( unsigned int eventType, unsigned int virtualKeyCode, long nativeKeyCode ) {'
	)

	_assert_ordered_anchors(
		map_button_block,
		(
			"case K_MOUSE1:",
			"return 0;",
			"case K_MOUSE2:",
			"return 2;",
			"case K_MOUSE3:",
			"return 1;",
			"return -1;",
		),
	)
	_assert_ordered_anchors(
		inject_mouse_block,
		(
			"if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {",
			"QLWebView_InjectMappedMouseMove(",
			"QLWebView_MapCursorCoordinate( x, cl_webHost.viewWidth, cl_webHost.surfaceContentWidth )",
			"QLWebView_MapCursorCoordinate( y, cl_webHost.viewHeight, cl_webHost.surfaceContentHeight )",
		),
	)
	_assert_ordered_anchors(
		inject_down_block,
		(
			"button = CL_WebHost_MapMouseButton( key );",
			"if ( button < 0 ) {",
			"if ( cl_webHost.cursorPositionValid ) {",
			"QLWebView_InjectMappedMouseMove( cl_webHost.cursorX, cl_webHost.cursorY );",
			"CL_Awesomium_InjectMouseDown( button );",
			"cl_webHost.focused = qtrue;",
		),
	)
	_assert_ordered_anchors(
		inject_up_block,
		(
			"button = CL_WebHost_MapMouseButton( key );",
			"if ( button < 0 ) {",
			"CL_Awesomium_InjectMouseUp( button );",
			"cl_webHost.focused = qtrue;",
		),
	)
	_assert_ordered_anchors(
		inject_wheel_block,
		(
			"if ( direction == 0 ) {",
			"CL_Awesomium_InjectMouseWheel( direction );",
			"cl_webHost.focused = qtrue;",
		),
	)
	_assert_ordered_anchors(
		inject_keyboard_block,
		(
			"if ( !cl_webHost.viewInitialised || !cl_webHost.browserVisible || !cl_webHost.browserActive ) {",
			"if ( !down && cl_webHost.keyCaptureArmed ) {",
			"QLWebView_PublishGameKey( key );",
			"cl_webHost.keyCaptureArmed = qfalse;",
			"if ( down ) {",
			"cl_webHost.focused = qtrue;",
		),
	)
	_assert_ordered_anchors(
		inject_fields_block,
		(
			"QLWebView_InjectKeyboardEvent( (int)event->virtualKeyCode, down );",
			"CL_Awesomium_InjectKeyboardEvent( event->eventType, event->virtualKeyCode, event->nativeKeyCode );",
		),
	)
	_assert_ordered_anchors(
		inject_activation_block,
		(
			"QL_WEB_KEYBOARD_EVENT_ACTIVATION_TYPE,",
			"QL_WEB_KEYBOARD_EVENT_ACTIVATION_VIRTUAL_KEY,",
			"QL_WEB_KEYBOARD_EVENT_ACTIVATION_NATIVE_KEY",
			"if ( !cl_webHost.viewInitialised ) {",
			"cl_webHost.focused = qtrue;",
			"QLWebView_InjectKeyboardEventFields( &activationEvent, qtrue );",
		),
	)
	_assert_ordered_anchors(
		dispatch_key_block,
		(
			"if ( key >= K_MOUSE1 && key <= K_MOUSE9 ) {",
			"CL_WebView_OnMouseButtonEvent( key, down );",
			"else if ( key == K_MWHEELUP )",
			"CL_WebView_OnMouseWheelEvent( 1 );",
			"else if ( key == K_MWHEELDOWN )",
			"CL_WebView_OnMouseWheelEvent( -1 );",
			"CL_WebView_OnKeyEvent( key, down );",
		),
	)
	assert "if ( cls.keyCatchers & KEYCATCH_BROWSER ) {" in mouse_event_block
	assert "CL_WebView_OnMouseMove( dx, dy );" in mouse_event_block
	assert "QLWebView_InjectMouseMove( x, y );" in on_mouse_move_block
	assert "QLWebView_InjectMouseDown( key );" in on_mouse_button_block
	assert "QLWebView_InjectMouseUp( key );" in on_mouse_button_block
	assert "QLWebView_InjectMouseWheel( direction );" in on_mouse_wheel_block
	assert "QLWebView_InjectKeyboardEvent( key, down );" in on_key_block
	assert 'CL_WebView_PublishEvent( "web.commNotice", message ? message : "" );' in publish_comm_block
	assert "void CL_WebView_OnMouseButtonEvent( int key, qboolean down );" in client_h
	assert "void CL_Awesomium_InjectKeyboardEvent( unsigned int eventType, unsigned int virtualKeyCode, long nativeKeyCode );" in client_h
	assert "cl_awe.webViewInjectMouseMove( cl_awesomium.webView, x, y );" in mouse_move_adapter_block
	assert "cl_awe.webViewInjectMouseDown( cl_awesomium.webView, button );" in mouse_down_adapter_block
	assert "cl_awe.webViewInjectMouseUp( cl_awesomium.webView, button );" in mouse_up_adapter_block
	assert "cl_awe.webViewInjectMouseWheel( cl_awesomium.webView, 0, direction * 30 );" in mouse_wheel_adapter_block
	assert "event = cl_awe.newWebKeyboardEvent( eventType, virtualKeyCode, nativeKeyCode );" in keyboard_adapter_block
	assert "cl_awe.webViewInjectKeyboardEvent( cl_awesomium.webView, event );" in keyboard_adapter_block


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
		"CL_Awesomium_CopyPath( childProcessConfigPath, sizeof( childProcessConfigPath ), childProcessPath );",
		'Com_Printf( "Awesomium startup phase: child process path %s (validated %s)\\n", childProcessConfigPath, childProcessPath );',
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
	assert "does not import or dynamically resolve Awesomium::ChildProcessMain" in cl_awesomium
	assert "valid awesomium_process.exe was not found in runtimePath or basePath" in cl_awesomium
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


def test_awesomium_retail_import_name_table_maps_to_guarded_c_export_adapter() -> None:
	hlil_part07 = _read_text(QL_STEAM_HLIL_PART07_PATH)
	analysis_symbols = _read_text(QL_STEAM_ANALYSIS_SYMBOLS_PATH)
	cl_awesomium = _read_text(CL_AWESOMIUM_WIN32_PATH)
	mapping_round = _read_text(
		REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_573.md"
	)

	load_block = _extract_function_block(
		cl_awesomium, "static qboolean CL_Awesomium_LoadImports( const char *runtimePath, const char *basePath ) {"
	)

	_assert_ordered_anchors(
		hlil_part07,
		(
			'00558b98  uint16_t __export_name_ptr_table_5(awesomium:?Push@JSArray@Awesomium@@QAEXABVJSValue@2@@Z) = 0x105',
			'00558bc8  uint16_t __export_name_ptr_table_5(awesomium:??0JSArray@Awesomium@@QAE@XZ) = 0x10',
			'00558be8  uint16_t __export_name_ptr_table_5(awesomium:??0JSObject@Awesomium@@QAE@XZ) = 0x13',
			'00558c08  uint16_t __export_name_ptr_table_5(awesomium:??0JSValue@Awesomium@@QAE@_N@Z) = 0x1b',
			'00558c2a  uint16_t __export_name_ptr_table_5(awesomium:?Create@ResourceResponse@Awesomium@@SAPAV12@ABVWebString@2@@Z) = 0xde',
			'00558c6a  uint16_t __export_name_ptr_table_5(awesomium:?filename@WebURL@Awesomium@@QBE?AVWebString@2@XZ) = 0x123',
			'00558c9e  uint16_t __export_name_ptr_table_5(awesomium:?path@WebURL@Awesomium@@QBE?AVWebString@2@XZ) = 0x12d',
			'00558cce  uint16_t __export_name_ptr_table_5(awesomium:??1WebURL@Awesomium@@QAE@XZ) = 0x82',
			'00558cec  uint16_t __export_name_ptr_table_5(awesomium:?host@WebURL@Awesomium@@QBE?AVWebString@2@XZ) = 0x125',
			'00558d1c  uint16_t __export_name_ptr_table_5(awesomium:?SendResponse@DataSource@Awesomium@@QAEXHIPAEABVWebString@2@@Z) = 0x10c',
			'00558d5e  uint16_t __export_name_ptr_table_5(awesomium:??1DataSource@Awesomium@@UAE@XZ) = 0x63',
			'00558d80  uint16_t __export_name_ptr_table_5(awesomium:??0DataSource@Awesomium@@IAE@XZ) = 0x6',
			'00558da2  uint16_t __export_name_ptr_table_5(awesomium:??0JSObject@Awesomium@@QAE@ABV01@@Z) = 0x12',
			'00558dc8  uint16_t __export_name_ptr_table_5(awesomium:?IsUndefined@JSValue@Awesomium@@QBE_NXZ) = 0xfc',
			'00558df2  uint16_t __export_name_ptr_table_5(awesomium:??_7ResourceInterceptor@Awesomium@@6B@) = 0xc4',
			'00558e1c  uint16_t __export_name_ptr_table_5(awesomium:??_7Dialog@WebViewListener@Awesomium@@6B@) = 0xbd',
			'00558e48  uint16_t __export_name_ptr_table_5(awesomium:??_7View@WebViewListener@Awesomium@@6B@) = 0xc9',
			'00558e72  uint16_t __export_name_ptr_table_5(awesomium:??_7Load@WebViewListener@Awesomium@@6B@) = 0xc0',
			'00558e9c  uint16_t __export_name_ptr_table_5(awesomium:?CopyTo@BitmapSurface@Awesomium@@QBEXPAEHH_N1@Z) = 0xdd',
			'00558ece  uint16_t __export_name_ptr_table_5(awesomium:??0WebKeyboardEvent@Awesomium@@QAE@IIJ@Z) = 0x3e',
			'00558efa  uint16_t __export_name_ptr_table_5(awesomium:?InvokeAsync@JSObject@Awesomium@@QAEXABVWebString@2@ABVJSArray@2@@Z) = 0xef',
			'00558f40  uint16_t __export_name_ptr_table_5(awesomium:?Shutdown@WebCore@Awesomium@@SAXXZ) = 0x110',
			'00558f66  uint16_t __export_name_ptr_table_5(awesomium:?set_is_dirty@BitmapSurface@Awesomium@@QAEX_N@Z) = 0x134',
			'00558f98  uint16_t __export_name_ptr_table_5(awesomium:??0WebURL@Awesomium@@QAE@ABVWebString@1@@Z) = 0x5c',
			'00558fc6  uint16_t __export_name_ptr_table_5(awesomium:??1WebPreferences@Awesomium@@QAE@XZ) = 0x7e',
			'00558fec  uint16_t __export_name_ptr_table_5(awesomium:??0DataPakSource@Awesomium@@QAE@ABVWebString@1@@Z) = 0x5',
			'00559020  uint16_t __export_name_ptr_table_5(awesomium:??0WebPreferences@Awesomium@@QAE@XZ) = 0x4c',
			'00559046  uint16_t __export_name_ptr_table_5(awesomium:??1WebConfig@Awesomium@@QAE@XZ) = 0x75',
			'00559068  uint16_t __export_name_ptr_table_5(awesomium:?Initialize@WebCore@Awesomium@@SAPAV12@ABUWebConfig@2@@Z) = 0xec',
			'005590a4  uint16_t __export_name_ptr_table_5(awesomium:??0WebConfig@Awesomium@@QAE@XZ) = 0x37',
			'005590c6  uint16_t __export_name_ptr_table_5(awesomium:?OnRequest@DataPakSource@Awesomium@@UAEXHABVResourceRequest@2@ABVWebString@2@@Z) = 0x100',
			'00559118  uint16_t __export_name_ptr_table_5(awesomium:??1DataPakSource@Awesomium@@UAE@XZ) = 0x62',
			'0055913e  char __import_dll_name(awesomium)[0xe] = "awesomium.dll", 0',
		),
	)

	for ghidra_listener_anchor in (
		"00547f94 IMPORTED QLResourceInterceptor::vftable",
		"00547fa8 IMPORTED QLDialogHandler::vftable",
		"00547fc0 IMPORTED QLViewHandler::vftable",
		"00547fe8 IMPORTED QLLoadHandler::vftable",
		"00548010 IMPORTED QLJSHandler::vftable",
		"00548070 IMPORTED Awesomium::DataPakSource::vftable",
	):
		assert ghidra_listener_anchor in analysis_symbols

	_assert_ordered_anchors(
		load_block,
		(
			'cl_awesomium.module = CL_Awesomium_LoadLibraryCandidate( "awesomium.dll", loadError, sizeof( loadError ) );',
			'CL_Awesomium_AppendPath( libraryPath, sizeof( libraryPath ), runtimePath, "awesomium.dll" );',
			'CL_Awesomium_AppendPath( libraryPath, sizeof( libraryPath ), basePath, "awesomium.dll" );',
			'CL_AWE_IMPORT( newWebConfig, "_Awe_new_WebConfig@0" );',
			'CL_AWE_IMPORT( deleteWebConfig, "_Awe_delete_WebConfig@4" );',
			'CL_AWE_IMPORT( newWebPreferences, "_Awe_new_WebPreferences@0" );',
			'CL_AWE_IMPORT( deleteWebPreferences, "_Awe_delete_WebPreferences@4" );',
			'CL_AWE_IMPORT( webCoreInitialize, "_Awe_WebCore_Initialize@4" );',
			'CL_AWE_IMPORT( webCoreShutdown, "_Awe_WebCore_Shutdown@0" );',
			'CL_AWE_IMPORT( webCoreUpdate, "_Awe_WebCore_Update@4" );',
			'CL_AWE_IMPORT( webCoreCreateWebSession, "_Awe_WebCore_CreateWebSession@12" );',
			'CL_AWE_IMPORT( webCoreCreateWebView, "_Awe_WebCore_CreateWebView_0@20" );',
			'cl_awe.webConfigAssetProtocolSet = reinterpret_cast<awe_webcore_set_string_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_WebConfig_asset_protocol_set@8" ) );',
			'CL_AWE_IMPORT( webConfigChildProcessPathSet, "_Awe_WebConfig_child_process_path_set@8" );',
			'CL_AWE_IMPORT( webConfigLogPathSet, "_Awe_WebConfig_log_path_set@8" );',
			'CL_AWE_IMPORT( webConfigPackagePathSet, "_Awe_WebConfig_package_path_set@8" );',
			'CL_AWE_IMPORT( webPrefsEnablePluginsSet, "_Awe_WebPreferences_enable_plugins_set@8" );',
			'CL_AWE_IMPORT( webPrefsEnableWebSecuritySet, "_Awe_WebPreferences_enable_web_security_set@8" );',
			'CL_AWE_IMPORT( newDataPakSource, "_Awe_new_DataPakSource@4" );',
			'CL_AWE_IMPORT( deleteDataPakSource, "_Awe_delete_DataPakSource@4" );',
			'CL_AWE_IMPORT( newWebURL, "_Awe_new_WebURL_1@4" );',
			'CL_AWE_IMPORT( deleteWebURL, "_Awe_delete_WebURL@4" );',
			'CL_AWE_IMPORT( webSessionAddDataSource, "_Awe_WebSession_AddDataSource@12" );',
			'CL_AWE_IMPORT( webViewDestroy, "_Awe_WebView_Destroy@4" );',
			'CL_AWE_IMPORT( webViewLoadURL, "_Awe_WebView_LoadURL@8" );',
			'CL_AWE_IMPORT( webViewExecuteJavascript, "_Awe_WebView_ExecuteJavascript@12" );',
			'CL_AWE_IMPORT( webViewSetTransparent, "_Awe_WebView_SetTransparent@8" );',
			'CL_AWE_IMPORT( webViewResize, "_Awe_WebView_Resize@12" );',
			'CL_AWE_IMPORT( webViewFocus, "_Awe_WebView_Focus@4" );',
			'CL_AWE_IMPORT( webViewUnfocus, "_Awe_WebView_Unfocus@4" );',
			'CL_AWE_IMPORT( webViewResumeRendering, "_Awe_WebView_ResumeRendering@4" );',
			'CL_AWE_IMPORT( webViewPauseRendering, "_Awe_WebView_PauseRendering@4" );',
			'CL_AWE_IMPORT( webViewInjectMouseMove, "_Awe_WebView_InjectMouseMove@12" );',
			'CL_AWE_IMPORT( webViewInjectMouseDown, "_Awe_WebView_InjectMouseDown@8" );',
			'CL_AWE_IMPORT( webViewInjectMouseUp, "_Awe_WebView_InjectMouseUp@8" );',
			'CL_AWE_IMPORT( webViewInjectMouseWheel, "_Awe_WebView_InjectMouseWheel@12" );',
			'CL_AWE_IMPORT( newWebKeyboardEvent, "_Awe_new_WebKeyboardEvent_1@12" );',
			'CL_AWE_IMPORT( webViewInjectKeyboardEvent, "_Awe_WebView_InjectKeyboardEvent@8" );',
			'CL_AWE_IMPORT( webViewSurface, "_Awe_WebView_surface@4" );',
			'CL_AWE_IMPORT( bitmapCopyTo, "_Awe_BitmapSurface_CopyTo@24" );',
			'CL_AWE_IMPORT( bitmapWidth, "_Awe_BitmapSurface_width@4" );',
			'CL_AWE_IMPORT( bitmapHeight, "_Awe_BitmapSurface_height@4" );',
			'CL_AWE_IMPORT( bitmapIsDirty, "_Awe_BitmapSurface_is_dirty@4" );',
			'CL_AWE_IMPORT( bitmapSetIsDirty, "_Awe_BitmapSurface_set_is_dirty@8" );',
			'cl_awe.newWebStringArray = reinterpret_cast<awe_new_void_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_new_WebStringArray_0@0" ) );',
			'cl_awe.webStringArrayPush = reinterpret_cast<awe_webstring_array_push_fn>( CL_Awesomium_ResolveOptionalImport( "_Awe_WebStringArray_Push@8" ) );',
			'cl_awe.jsValueToInteger = reinterpret_cast<awe_jsvalue_to_integer_fn>( GetProcAddress( cl_awesomium.module, "_Awe_JSValue_ToInteger@4" ) );',
			"cl_awesomium.bootstrapMappingCount = CL_Awesomium_CountBootstrapRetailMappings();",
		),
	)

	for adapter_anchor in (
		'#define CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT "external SDK C API dependency"',
		'#define CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT "external SDK C API dependency"',
		"static const clAwesomiumRetailAbiEquivalence_t cl_aweRetailAbiEquivalence[] = {",
		"static const clAwesomiumBootstrapRetailMapping_t cl_aweBootstrapRetailMappings[] = {",
		'{ 0x004F2D30u, 0x0052C6A4u, "WebConfig::WebConfig", "CL_Awesomium_PrepareConfig", "_Awe_new_WebConfig@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x0052C6A0u, "WebCore::Initialize", "CL_Awesomium_Startup", "_Awe_WebCore_Initialize@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x0052C694u, "DataPakSource::DataPakSource", "CL_Awesomium_CreateSession", "_Awe_new_DataPakSource@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x00000064u, "WebView::LoadURL slot 0x64", "CL_Awesomium_OpenURL", "_Awe_WebView_LoadURL@8", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F28A0u, 0xe0u, "WebView::InjectKeyboardEvent", "CL_Awesomium_InjectKeyboardEvent", "_Awe_new_WebKeyboardEvent_1@12 + _Awe_WebView_InjectKeyboardEvent@8", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },',
		'{ 0x004F2A60u, 0x0052C684u, "WebCore::Shutdown", "CL_Awesomium_Shutdown", "_Awe_WebCore_Shutdown@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
	):
		assert adapter_anchor in cl_awesomium

	for direct_retail_import in (
		"?Initialize@WebCore@Awesomium@@SAPAV12@ABUWebConfig@2@@Z",
		"?Shutdown@WebCore@Awesomium@@SAXXZ",
		"??0WebConfig@Awesomium@@QAE@XZ",
		"??0DataPakSource@Awesomium@@QAE@ABVWebString@1@@Z",
		"??_7ResourceInterceptor@Awesomium@@6B@",
		"__thiscall",
	):
		assert direct_retail_import not in cl_awesomium

	for round_anchor in (
		"Quake Live Steam Mapping Round 573: Awesomium DLL Import Name Table and C Export Adapter",
		"`0x00558b98..0x0055913e`",
		"`0x0055913e`: import DLL name literal `awesomium.dll`",
		"`WebCore::Initialize` -> `_Awe_WebCore_Initialize@4`",
		"`WebCore::Shutdown` -> `_Awe_WebCore_Shutdown@0`",
		"Overall Awesomium/WebUI launch/runtime integration mapping confidence:",
		"**99.15% -> 99.20%**",
	):
		assert round_anchor in mapping_round


def test_awesomium_webui_retail_import_vtable_and_helper_abi_bridge_is_pinned() -> None:
	all_aliases = json.loads(_read_text(SYMBOL_ALIASES_PATH))
	helper_aliases = all_aliases["awesomium_process"]
	helper_rows = _function_rows_from(AWESOMIUM_PROCESS_FUNCTIONS_CSV_PATH)
	helper_metadata = _read_text(AWESOMIUM_PROCESS_METADATA_PATH)
	cl_awesomium = _read_text(CL_AWESOMIUM_WIN32_PATH)
	process_cpp = _read_text(AWESOMIUM_PROCESS_CPP_PATH)
	analysis_symbols = _read_text(QL_STEAM_ANALYSIS_SYMBOLS_PATH)
	hlil_part05 = _read_text(QL_STEAM_HLIL_PART05_PATH)
	hlil_part19 = _read_text(QL_STEAM_HLIL_PART19_PATH)

	helper_row = helper_rows[0x00401000]
	assert helper_aliases["FUN_00401000"] == "AwesomiumProcess_RunChildProcessMain"
	assert helper_row["name"] == "FUN_00401000"
	assert int(helper_row["size"]) == 98
	assert helper_row["calling_convention"] == "__stdcall"
	assert "program_name=awesomium_process.exe" in helper_metadata
	assert "function_count=139" in helper_metadata
	assert "import_count=54" in helper_metadata
	assert "export_count=1" in helper_metadata
	assert "#if QL_PLATFORM_HAS_ONLINE_SERVICES" in process_cpp
	assert "#if QL_AWESOMIUM_USE_SDK" in process_cpp
	assert "Awesomium::ChildProcessMain( instance );" in process_cpp
	assert 'LoadLibraryA( QLR_AWESOMIUM_RUNTIME_DLL )' in process_cpp
	assert "symbol = GetProcAddress( awesomium, QLR_AWESOMIUM_CHILD_PROCESS_MAIN_SYMBOL );" in process_cpp

	for awesomium_import_anchor in (
		"017c664c  extern void __thiscall Awesomium::DataPakSource::DataPakSource",
		"017c6680  extern void __thiscall Awesomium::WebConfig::WebConfig",
		"017c6688  extern void __thiscall Awesomium::WebPreferences::WebPreferences",
		"017c66f8  extern const Awesomium::WebViewListener::Dialog::`vftable'",
		"017c66fc  extern const Awesomium::WebViewListener::Load::`vftable'",
		"017c6700  extern const Awesomium::ResourceInterceptor::`vftable'",
		"017c6704  extern const Awesomium::WebViewListener::View::`vftable'",
		"017c670c  extern void __thiscall Awesomium::BitmapSurface::CopyTo",
		"017c6710  extern class Awesomium::ResourceResponse* __cdecl Awesomium::ResourceResponse::Create",
		"017c6714  extern class Awesomium::WebString __cdecl Awesomium::WebString::CreateFromUTF8",
		"017c6718  extern class Awesomium::WebCore* __cdecl Awesomium::WebCore::Initialize",
		"017c671c  extern void __thiscall Awesomium::JSObject::InvokeAsync",
		"017c672c  extern void __thiscall Awesomium::DataPakSource::OnRequest",
		"017c6734  extern void __thiscall Awesomium::DataSource::SendResponse",
		"017c6744  extern void __cdecl Awesomium::WebCore::Shutdown()()",
		"017c6790  extern void __thiscall Awesomium::BitmapSurface::set_is_dirty",
		"017c67a0  extern uint32_t __thiscall Awesomium::JSArray::size",
	):
		assert awesomium_import_anchor in hlil_part19

	for listener_symbol in (
		"00547f68 IMPORTED Awesomium::JSMethodHandler::vftable",
		"00547f94 IMPORTED QLResourceInterceptor::vftable",
		"00547fa8 IMPORTED QLDialogHandler::vftable",
		"00547fc0 IMPORTED QLViewHandler::vftable",
		"00547fe8 IMPORTED QLLoadHandler::vftable",
		"00548010 IMPORTED QLJSHandler::vftable",
		"00548070 IMPORTED Awesomium::DataPakSource::vftable",
		"005527a8 IMPORTED QLResourceInterceptor::RTTI_Complete_Object_Locator",
		"00552828 IMPORTED QLDialogHandler::RTTI_Complete_Object_Locator",
		"005528a8 IMPORTED QLViewHandler::RTTI_Complete_Object_Locator",
		"00552928 IMPORTED QLLoadHandler::RTTI_Complete_Object_Locator",
		"005529a8 IMPORTED QLJSHandler::RTTI_Complete_Object_Locator",
		"005529f4 IMPORTED Awesomium::DataPakSource::RTTI_Complete_Object_Locator",
		"00574570 IMPORTED QLResourceInterceptor::RTTI_Type_Descriptor",
		"005745c0 IMPORTED QLDialogHandler::RTTI_Type_Descriptor",
		"00574610 IMPORTED QLViewHandler::RTTI_Type_Descriptor",
		"0057465c IMPORTED QLLoadHandler::RTTI_Type_Descriptor",
		"005746a8 IMPORTED QLJSHandler::RTTI_Type_Descriptor",
		"005746c4 IMPORTED Awesomium::DataPakSource::RTTI_Type_Descriptor",
	):
		assert listener_symbol in analysis_symbols

	for startup_anchor in (
		"004f2d55          Awesomium::WebConfig::WebConfig(this: ecx)",
		"004f2d71          eax, ecx_2 = Awesomium::WebCore::Initialize(&var_3c)",
		"004f2dd2              Awesomium::WebPreferences::WebPreferences(this: ecx_3)",
		'004f2e52                  ecx_7 = Awesomium::DataPakSource::DataPakSource(this: esi_2,',
		"004f2e58                  *esi_2 = &Awesomium::DataPakSource::`vftable'{for `Awesomium::DataSource'}",
		"004f2e7e              char* eax_10 = sub_4314d0(&var_c, &data_548068)",
		"(*(edi_2 + 0x10))(eax_10, esi_2)",
		'004f2ec8              char* eax_13 = sub_4314d0(&var_c, "steam")',
		"004f2eef                      QLResourceInterceptor::`vftable'{for `Awesomium::ResourceInterceptor'}",
		"(*(*data_12d304c + 0x10))(eax_15)",
		"004f2f3d                  *eax_19 = &QLJSHandler::`vftable'{for `Awesomium::JSMethodHandler'}",
		"(*(*data_12d3050 + 0x12c))(eax_19)",
		"004f2fa4                      &QLDialogHandler::`vftable'{for `Awesomium::WebViewListener::Dialog'}",
		"(*(*data_12d3050 + 0x34))(eax_22)",
		"004f2fca                      &QLViewHandler::`vftable'{for `Awesomium::WebViewListener::View'}",
		"(*(*data_12d3050 + 0x24))(eax_24)",
		"004f2ff0                      &QLLoadHandler::`vftable'{for `Awesomium::WebViewListener::Load'}",
		"(*(*data_12d3050 + 0x28))(eax_26)",
	):
		assert startup_anchor in hlil_part05

	for adapter_anchor in (
		'{ 0x004F2D30u, 0x00548070u, "DataPakSource::vftable", "CL_Awesomium_CreateSession", "Awesomium built-in DataPakSource", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_OBJECT_LIFETIME },',
		'{ 0x004F2D30u, 0x00000010u, "WebSession::AddDataSource slot 0x10", "CL_Awesomium_CreateSession", "_Awe_WebSession_AddDataSource@12", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'{ 0x004F2D30u, 0x00000124u, "WebView::ExecuteJavascript slot 0x124", "CL_Awesomium_ExecuteJavascript", "_Awe_WebView_ExecuteJavascript@12", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },',
		'CL_AWE_IMPORT( webViewExecuteJavascript, "_Awe_WebView_ExecuteJavascript@12" );',
		'CL_AWE_IMPORT( bitmapCopyTo, "_Awe_BitmapSurface_CopyTo@24" );',
		'CL_AWE_IMPORT( bitmapSetIsDirty, "_Awe_BitmapSurface_set_is_dirty@8" );',
		'CL_AWE_IMPORT( deleteDataPakSource, "_Awe_delete_DataPakSource@4" );',
		'CL_AWE_IMPORT( webViewReload, "_Awe_WebView_Reload@8" );',
		'CL_AWE_IMPORT( webViewStop, "_Awe_WebView_Stop@4" );',
		"cl_awe.webSessionAddDataSource( cl_awesomium.webSession, sourceName, cl_awesomium.dataPakSource );",
		"cl_awe.webViewExecuteJavascript( cl_awesomium.webView, wideScript, wideFrame );",
		"cl_awe.bitmapCopyTo( surface, destination, rowSpan, 4, true, false );",
		"cl_awe.bitmapSetIsDirty( surface, false );",
	):
		assert adapter_anchor in cl_awesomium


def test_awesomium_child_process_helper_dynamic_sdk_boundary_matches_retail_corpus() -> None:
	all_aliases = json.loads(_read_text(SYMBOL_ALIASES_PATH))
	helper_aliases = all_aliases["awesomium_process"]
	helper_rows = _function_rows_from(AWESOMIUM_PROCESS_FUNCTIONS_CSV_PATH)
	helper_metadata = _read_text(AWESOMIUM_PROCESS_METADATA_PATH)
	helper_imports = _read_text(AWESOMIUM_PROCESS_IMPORTS_PATH)
	helper_exports = _read_text(AWESOMIUM_PROCESS_EXPORTS_PATH)
	helper_decompile = _read_text(AWESOMIUM_PROCESS_DECOMPILE_TOP_FUNCTIONS_PATH)
	process_cpp = _read_text(AWESOMIUM_PROCESS_CPP_PATH)
	process_rc = _read_text(AWESOMIUM_PROCESS_RC_PATH)
	process_project = _read_text(AWESOMIUM_PROCESS_VCXPROJ_PATH)
	mapping_round = _read_text(
		REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_583.md"
	)

	helper_row = helper_rows[0x00401000]
	assert helper_aliases["FUN_00401000"] == "AwesomiumProcess_RunChildProcessMain"
	assert helper_row["name"] == "FUN_00401000"
	assert int(helper_row["size"]) == 98
	assert helper_row["calling_convention"] == "__stdcall"
	assert "program_name=awesomium_process.exe" in helper_metadata
	assert "function_count=139" in helper_metadata
	assert "import_count=54" in helper_metadata
	assert "export_count=1" in helper_metadata
	assert helper_exports.strip() == "004013a5 entry"

	for import_anchor in (
		"KERNEL32.DLL!GetProcAddress @ 00007c80",
		"KERNEL32.DLL!GetModuleFileNameW @ 00007cd2",
		"KERNEL32.DLL!LoadLibraryW @ 00007f14",
		"KERNEL32.DLL!GetCommandLineW @ 00007c1c",
		"KERNEL32.DLL!GetStartupInfoW @ 00007c44",
		"KERNEL32.DLL!ExitProcess @ 00007bbc",
	):
		assert import_anchor in helper_imports
	assert "awesomium.dll" not in helper_imports
	assert "ChildProcessMain@Awesomium" not in helper_imports

	_assert_ordered_anchors(
		helper_decompile,
		(
			"local_24 = FUN_00401000((HINSTANCE__ *)&IMAGE_DOS_HEADER_00400000);",
			"if (local_20 == 0) {",
			"_exit(local_24);",
			"__cexit();",
			"return local_24;",
			"/* FUN_00401000 @ 00401000 size 98 */",
			"void FUN_00401000(HINSTANCE__ *param_1)",
			"pcStack_10 = __except_handler4;",
			"local_8 = 0;",
			"Awesomium::ChildProcessMain(param_1);",
			"ExceptionList = local_14;",
			"return;",
		),
	)

	_assert_ordered_anchors(
		process_cpp,
		(
			"#ifndef QL_AWESOMIUM_USE_SDK",
			"#define QL_AWESOMIUM_USE_SDK 0",
			"#if QL_PLATFORM_HAS_ONLINE_SERVICES && QL_AWESOMIUM_USE_SDK",
			"#include <Awesomium/ChildProcess.h>",
			"#if QL_PLATFORM_HAS_ONLINE_SERVICES && !QL_AWESOMIUM_USE_SDK",
			'#define QLR_AWESOMIUM_RUNTIME_DLL "awesomium.dll"',
			'#define QLR_AWESOMIUM_CHILD_PROCESS_MAIN_SYMBOL "?ChildProcessMain@Awesomium@@YAHPAUHINSTANCE__@@@Z"',
			'#define QLR_AWESOMIUM_DYNAMIC_HELPER_MARKER "QLR_AWESOMIUM_CHILDPROCESSMAIN_DYNAMIC"',
			"typedef int (__cdecl *awesomium_child_process_main_fn)( HINSTANCE instance );",
			"static int AwesomiumProcess_ReportLoadFailure( const char *message ) {",
			"OutputDebugStringA( message );",
			"static int AwesomiumProcess_RunDynamicChildProcessMain( HINSTANCE instance ) {",
			"awesomium = LoadLibraryA( QLR_AWESOMIUM_RUNTIME_DLL );",
			"return AwesomiumProcess_ReportLoadFailure( QLR_AWESOMIUM_DYNAMIC_HELPER_MARKER \": failed to load awesomium.dll\" );",
			"symbol = GetProcAddress( awesomium, QLR_AWESOMIUM_CHILD_PROCESS_MAIN_SYMBOL );",
			"FreeLibrary( awesomium );",
			"return AwesomiumProcess_ReportLoadFailure( QLR_AWESOMIUM_DYNAMIC_HELPER_MARKER \": failed to resolve Awesomium::ChildProcessMain\" );",
			"childProcessMain = (awesomium_child_process_main_fn)symbol;",
			"return childProcessMain( instance );",
			"static int AwesomiumProcess_RunChildProcessMain( HINSTANCE instance ) {",
			"#if QL_AWESOMIUM_USE_SDK",
			"return Awesomium::ChildProcessMain( instance );",
			"return AwesomiumProcess_RunDynamicChildProcessMain( instance );",
			"(void)instance;",
			"return 0;",
			"int APIENTRY WinMain( HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow ) {",
			"return AwesomiumProcess_RunChildProcessMain( hInstance );",
		),
	)

	for project_anchor in (
		"<ConfigurationType>Application</ConfigurationType>",
		"<SubSystem>Windows</SubSystem>",
		"<TargetMachine>MachineX86</TargetMachine>",
		"<RandomizedBaseAddress>true</RandomizedBaseAddress>",
		"<DataExecutionPrevention>true</DataExecutionPrevention>",
		"<TerminalServerAware>true</TerminalServerAware>",
		"<ImageHasSafeExceptionHandlers>true</ImageHasSafeExceptionHandlers>",
		"<QLBuildOnlineServices Condition=\"'$(QLBuildOnlineServices)'=='' and ('$(Configuration)'=='Release' Or '$(Configuration)'=='Release Alpha' Or '$(Configuration)'=='Release TA' Or '$(Configuration)'=='Release TA DEMO')\">1</QLBuildOnlineServices>",
		"<QLBuildOnlineServices Condition=\"'$(QLBuildOnlineServices)'==''\">0</QLBuildOnlineServices>",
		"<QLUseAwesomiumSdk Condition=\"'$(QLUseAwesomiumSdk)'==''\">0</QLUseAwesomiumSdk>",
		"<PreprocessorDefinitions>QL_BUILD_ONLINE_SERVICES=$(QLBuildOnlineServices);QL_AWESOMIUM_USE_SDK=$(QLUseAwesomiumSdk);%(PreprocessorDefinitions)</PreprocessorDefinitions>",
		"<Target Name=\"ValidateAwesomiumSdk\" BeforeTargets=\"ClCompile;Link\" Condition=\"'$(QLBuildOnlineServices)'=='1' and '$(QLUseAwesomiumSdk)'=='1'\">",
		"Awesomium child-process support enabled with external SDK",
		"<ItemDefinitionGroup Condition=\"'$(QLBuildOnlineServices)'=='1' and '$(QLUseAwesomiumSdk)'=='1'\">",
		"<AdditionalLibraryDirectories>$(AwesomiumLibDir);%(AdditionalLibraryDirectories)</AdditionalLibraryDirectories>",
		"<AdditionalDependencies>$(AwesomiumLib);%(AdditionalDependencies)</AdditionalDependencies>",
	):
		assert project_anchor in process_project

	_assert_ordered_anchors(
		process_rc,
		(
			"#define QLR_AWESOMIUM_PROCESS_FILE_VERSION 1,0,0,0",
			'#define QLR_AWESOMIUM_PROCESS_FILE_VERSION_STR "1.0.0.0\\0"',
			'1                       RT_MANIFEST             "awesomium_process.manifest"',
			'VALUE "CompanyName", "Quake Live Reverse\\0"',
			'VALUE "FileDescription", "Quake Live Reverse Awesomium child-process host\\0"',
			'VALUE "InternalName", "awesomium_process.exe\\0"',
			'VALUE "OriginalFilename", "awesomium_process.exe\\0"',
		),
	)
	assert "Awesomium Child Process Helper SDK/Dynamic Boundary" in mapping_round
	assert "Overall Awesomium/WebUI launch/runtime integration mapping confidence: **99.26% -> 99.27%**." in mapping_round


def test_awesomium_document_ready_resource_and_failure_retail_hlil_flow_is_pinned() -> None:
	rows = _function_rows()
	aliases = _aliases()
	hlil_part01 = _read_text(QL_STEAM_HLIL_PART01_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	steam_resources = _read_text(CL_STEAM_RESOURCES_PATH)

	for address, owner in (
		(0x004317F0, "QLLoadHandler_OnDocumentReady"),
		(0x00431A10, "QLJSHandler_BindQzInstance"),
		(0x00434620, "QLResourceInterceptor_OnRequest"),
		(0x00434AE0, "QLLoadHandler_OnFailLoadingFrame"),
	):
		assert aliases[f"FUN_{address:08x}"] == owner
		assert rows[address]["name"] == f"FUN_{address:08x}"

	_assert_ordered_anchors(
		hlil_part01,
		(
			"004317f0    int32_t __stdcall sub_4317f0(int32_t* arg1)",
			'0043183d  int32_t i_2 = sub_4d2d80("js", &data_52ca10, &var_494, 0x400)',
			"00431876          int32_t var_94 = 0x2f736a",
			"(*(*var_49c + 0x124))",
			'(*(*data_12d3050 + 0x128))(&var_4a0, sub_4314d0(&var_49c, "window"), eax_12)',
			'sub_4f3260(Awesomium::WebString::~WebString, edi, "web.object.ready", nullptr)',
		),
	)
	_assert_ordered_anchors(
		hlil_part01,
		(
			"00431a10    int32_t sub_431a10()",
			"Awesomium::JSValue::IsObject",
			'sub_4314d0(&var_18, "qz_instance")',
			"Awesomium::JSValue::ToObject",
			"for (char const (** i)[0x11] = &data_55c008;",
			"Awesomium::JSObject::SetCustomMethod(",
			'sub_4314d0(&var_1c, "version")',
			'sub_4d9220("%llu")',
			'sub_4314d0(&var_20, "steamId")',
			"(**SteamFriends())()",
			'sub_4314d0(&var_20, "playerName")',
			"(*(*SteamUtils() + 0x24))()",
			'sub_4314d0(&var_20, "appId")',
		),
	)
	_assert_ordered_anchors(
		hlil_part01,
		(
			"00434620    class Awesomium::ResourceResponse* __stdcall sub_434620(int32_t* arg1)",
			'00434656  char* eax_3 = sub_4ccda0("fs_webpath")',
			"Awesomium::WebURL::host(this: (*(*arg1 + 0xc))",
			"Awesomium::WebURL::path(this: (*(*arg1 + 0xc))",
			'sub_406970(eax_13, "/screenshot", ecx_11)',
		),
	)
	for resource_anchor in (
		'&data_52cbfc',
		'sub_4cec90(sub_4ccda0("fs_homepath"), eax_15, "screenshots/")',
		"004348ad      result_3, ecx_17 = Awesomium::ResourceResponse::Create",
		"004349d8              Awesomium::ResourceResponse::Create",
		"00434ab4          result = nullptr",
	):
		assert resource_anchor in hlil_part01

	_assert_ordered_anchors(
		hlil_part01,
		(
			"00434ae0    Awesomium::WebString* __stdcall sub_434ae0(char arg1, int32_t arg2, Awesomium::WebString* arg3)",
			"00434b13  data_12d3068 = 0",
			"00434b1a  if (arg1 != 0)",
			"Failed to load QUAKE LIVE site.",
			"00434b4f      data_12d3069 = 1",
			"00434b67          result = sub_4f24d0()",
			'00434b7b              sub_4cd250("com_errorMessage", eax_4)',
		),
	)

	load_scripts_block = _extract_function_block(
		cl_cgame, "static void QLLoadHandler_LoadDocumentScripts( void ) {"
	)
	bind_qz_block = _extract_function_block(cl_cgame, "static void QLJSHandler_BindQzInstance( void ) {")
	document_ready_block = _extract_function_block(
		cl_cgame, "static void QLLoadHandler_OnDocumentReady( void ) {"
	)
	load_failure_block = _extract_function_block(
		cl_cgame, "static void QLLoadHandler_OnFailLoadingFrame( const char *url ) {"
	)
	retail_host_block = _extract_function_block(
		steam_resources,
		"static qboolean QLResourceInterceptor_RequestRetailHost( const char *url, clSteamDataSourceResponse_t *response ) {",
	)
	interceptor_block = _extract_function_block(
		steam_resources, "static qboolean QLResourceInterceptor_OnRequest( const char *url, clSteamDataSourceResponse_t *response ) {"
	)

	_assert_ordered_anchors(
		load_scripts_block,
		(
			'count = CL_WebPak_GetFileList( "js", ".js", fileList, sizeof( fileList ) );',
			'Com_sprintf( scriptPath, sizeof( scriptPath ), "js/%s", cursor );',
			"CL_LauncherRequestData( scriptPath, (void **)&scriptBuffer, &scriptLength )",
			"cl_webHost.loadedDocumentScriptCount++;",
			"QLLoadHandler_ExecuteDocumentScript( scriptPath, scriptBuffer, scriptLength );",
		),
	)
	_assert_ordered_anchors(
		bind_qz_block,
		(
			"for ( i = 0; i < CL_WEB_MAX_QZ_METHODS && cl_webMethodBindings[i].name; i++ ) {",
			"(void)cl_webMethodBindings[i].returnsValue;",
			"CL_WebHost_RefreshBootstrapProperties();",
			"cl_webHost.qzInstanceBound = qtrue;",
			"cl_webHost.windowObjectBound = qtrue;",
		),
	)
	_assert_ordered_anchors(
		document_ready_block,
		(
			"QLLoadHandler_LoadDocumentScripts();",
			"QLJSHandler_BindQzInstance();",
			"cl_webHost.documentReady = qtrue;",
			"QLViewHandler_OnChangeCursor( 0 );",
			'CL_WebView_PublishEvent( "web.object.ready", NULL );',
		),
	)
	_assert_ordered_anchors(
		retail_host_block,
		(
			"QLResourceInterceptor_ParseURL( url, &parsed )",
			"QLResourceInterceptor_BuildMappedRequest( &parsed, mappedUrl, sizeof( mappedUrl ) )",
			"CL_SteamDataSource_ClearResponse( response );",
			"CL_LauncherRequestData( mappedUrl, (void **)&response->buffer, &response->bufferLength )",
			"Q_strncpyz( response->mimeType, CL_SteamDataSource_GuessMimeType( mappedUrl ), sizeof( response->mimeType ) );",
		),
	)
	_assert_ordered_anchors(
		interceptor_block,
		(
			"QLResourceInterceptor_OnFilterNavigation( url )",
			"CL_SteamDataSource_Request( url, response )",
			"QLResourceInterceptor_RequestRetailHost( url, response )",
			"CL_LauncherRequestData( url, (void **)&response->buffer, &response->bufferLength )",
			'CL_LogLauncherResourceFallbackUnavailable( url, "no launcher/web resource owner is available" );',
		),
	)
	_assert_ordered_anchors(
		load_failure_block,
		(
			"cl_webHost.loadingDocument = qfalse;",
			"cl_webHost.loadFailed = qtrue;",
			"cl_webHost.browserVisible = qfalse;",
			"cl_webBrowserVisible = qfalse;",
			"CL_WebHost_ClearCursorOverride();",
			'Com_sprintf( message, sizeof( message ), "Failed to load QUAKE LIVE site... %s", url ? url : CL_WEB_DEFAULT_URL );',
			'Cvar_Set( "web_browserActive", "0" );',
			'Cvar_Set( "com_errorMessage", message );',
		),
	)
	for source_anchor in (
		'#define QL_RESOURCE_INTERCEPTOR_HOST "ql"',
		'#define QL_RESOURCE_INTERCEPTOR_SCREENSHOT_PATH "/screenshot"',
		'#define QL_RESOURCE_INTERCEPTOR_WEB_FALLBACK_PREFIX "https://cdn.quakelive.com/"',
		'#define QL_RESOURCE_INTERCEPTOR_SCREENSHOT_FALLBACK_PREFIX "quakelive://screenshots/"',
	):
		assert source_anchor in steam_resources


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
	assert "QL_AWESOMIUM_USE_SDK" in process_cpp
	assert "LoadLibraryA( QLR_AWESOMIUM_RUNTIME_DLL )" in process_cpp
	assert "?ChildProcessMain@Awesomium@@YAHPAUHINSTANCE__@@@Z" in process_cpp
	assert "QLR_AWESOMIUM_CHILDPROCESSMAIN_DYNAMIC" in process_cpp

	for expected in (
		"<QLBuildOnlineServices Condition=\"'$(QLBuildOnlineServices)'=='' and ('$(Configuration)'=='Release' Or '$(Configuration)'=='Release Alpha' Or '$(Configuration)'=='Release TA' Or '$(Configuration)'=='Release TA DEMO')\">1</QLBuildOnlineServices>",
		"<QLUseAwesomiumSdk Condition=\"'$(QLUseAwesomiumSdk)'==''\">0</QLUseAwesomiumSdk>",
		"QL_AWESOMIUM_USE_SDK=$(QLUseAwesomiumSdk)",
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
		'<ProjectReference Include="awesomium_process.vcxproj" Condition="\'$(QLBuildOnlineServices)\'!=\'0\'">',
		"<AdditionalProperties>QLBuildOnlineServices=$(QLBuildOnlineServices);QLUseAwesomiumSdk=$(QLUseAwesomiumSdk);AwesomiumSdkDir=$(AwesomiumSdkDir)</AdditionalProperties>",
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
		"ui_resourceBridgeSteamDataSourceSubset",
		"ui_resourceBridgeSteamDataSourceNativeGap",
		"ui_resourceBridgeSteamDataSourceFallbackOwner",
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
	assert 'Cvar_Set( "ui_resourceBridgeSteamDataSourceSubset", CL_GetSteamDataSourceSubsetLabel() );' in refresh_block
	assert 'Cvar_Set( "ui_resourceBridgeSteamDataSourceNativeGap", CL_GetSteamDataSourceNativeGapLabel() );' in refresh_block
	assert 'Cvar_Set( "ui_resourceBridgeSteamDataSourceFallbackOwner", CL_GetSteamDataSourceFallbackOwnerLabel() );' in refresh_block
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


def test_awesomium_handler_destroyers_and_shutdown_cleanup_match_retail_lifetime_boundary() -> None:
	rows = _function_rows()
	aliases = _aliases()
	hlil_part05 = _read_text(QL_STEAM_HLIL_PART05_PATH)
	hlil_part06 = _read_text(QL_STEAM_HLIL_PART06_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_awesomium = _read_text(CL_AWESOMIUM_WIN32_PATH)
	mapping_round = _read_text(
		REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_581.md"
	)

	for address, owner, size in (
		(0x004F23B0, "QLJSHandler_Destroy", 34),
		(0x004F2A60, "QLWebHost_Shutdown", 32),
		(0x004F2A80, "QLResourceInterceptor_Destroy", 35),
		(0x004F2AB0, "QLDialogHandler_Destroy", 35),
		(0x004F2AE0, "QLViewHandler_Destroy", 35),
		(0x004F2B10, "QLLoadHandler_Destroy", 35),
		(0x004F3130, "AwesomiumDataPakSource_Destroy", 34),
	):
		assert aliases[f"FUN_{address:08x}"] == owner
		assert aliases[f"sub_{address:06X}"] == owner
		assert aliases[f"sub_{address:06x}"] == owner
		assert rows[address]["name"] == f"FUN_{address:08x}"
		assert int(rows[address]["size"]) == size

	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f23b0    struct Awesomium::JSMethodHandler::VTable** __thiscall sub_4f23b0(struct Awesomium::JSMethodHandler::VTable** arg1, char arg2)",
			"*arg1 = &Awesomium::JSMethodHandler::`vftable'",
			"if ((arg2 & 1) != 0)",
			"operator delete(arg1)",
			"return arg1",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f2a60    void sub_4f2a60()",
			"int32_t* ecx_1 = data_12d3050",
			"if (ecx_1 != 0)",
			"(**ecx_1)()",
			"if (data_12d304c == 0)",
			"return Awesomium::WebCore::Shutdown() __tailcall",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f2a80    ** __thiscall sub_4f2a80(** arg1, char arg2)",
			"*arg1 = Awesomium::ResourceInterceptor::`vftable'",
			"operator delete(arg1)",
			"004f2ab0    ** __thiscall sub_4f2ab0(** arg1, char arg2)",
			"*arg1 = Awesomium::WebViewListener::Dialog::`vftable'",
			"operator delete(arg1)",
			"004f2ae0    ** __thiscall sub_4f2ae0(** arg1, char arg2)",
			"*arg1 = Awesomium::WebViewListener::View::`vftable'",
			"operator delete(arg1)",
			"004f2b10    ** __thiscall sub_4f2b10(** arg1, char arg2)",
			"*arg1 = Awesomium::WebViewListener::Load::`vftable'",
			"operator delete(arg1)",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f3130    Awesomium::DataPakSource* __thiscall sub_4f3130(Awesomium::DataPakSource* arg1, char arg2)",
			"Awesomium::DataPakSource::~DataPakSource(this: arg1)",
			"if ((arg2 & 1) != 0)",
			"operator delete(arg1)",
			"return arg1",
		),
	)
	_assert_ordered_anchors(
		hlil_part06,
		(
			"00547f94  struct Awesomium::ResourceInterceptor::QLResourceInterceptor::VTable QLResourceInterceptor::`vftable'{for `Awesomium::ResourceInterceptor'} =",
			"vFunc_3)(** arg1, char arg2) = sub_4f2a80",
			"00547fa8  struct Awesomium::WebViewListener::Dialog::QLDialogHandler::VTable QLDialogHandler::`vftable'{for `Awesomium::WebViewListener::Dialog'} =",
			"vFunc_4)(** arg1, char arg2) = sub_4f2ab0",
			"00547fc0  struct Awesomium::WebViewListener::View::QLViewHandler::VTable QLViewHandler::`vftable'{for `Awesomium::WebViewListener::View'} =",
			"vFunc_8)(** arg1, char arg2) = sub_4f2ae0",
			"00547fe8  struct Awesomium::WebViewListener::Load::QLLoadHandler::VTable QLLoadHandler::`vftable'{for `Awesomium::WebViewListener::Load'} =",
			"vFunc_4)(** arg1, char arg2) = sub_4f2b10",
			"00548010  struct Awesomium::JSMethodHandler::QLJSHandler::VTable QLJSHandler::`vftable'{for `Awesomium::JSMethodHandler'} =",
			"vFunc_2)(void*** arg1, char arg2) = sub_4f23b0",
			"00548070  struct Awesomium::DataSource::Awesomium::DataPakSource::VTable Awesomium::DataPakSource::`vftable'{for `Awesomium::DataSource'} =",
			"vFunc_0)(Awesomium::DataPakSource* arg1, char arg2) = sub_4f3130",
		),
	)

	for source_anchor in (
		'{ "QLResourceInterceptor", "destroy", 0x00547F94u, 0x0Cu, 0x004F2A80u, "QLResourceInterceptor_Destroy", CL_WEB_LISTENER_SCOPE_DESTRUCTOR },',
		'{ "QLDialogHandler", "destroy", 0x00547FA8u, 0x10u, 0x004F2AB0u, "QLDialogHandler_Destroy", CL_WEB_LISTENER_SCOPE_DESTRUCTOR },',
		'{ "QLViewHandler", "destroy", 0x00547FC0u, 0x20u, 0x004F2AE0u, "QLViewHandler_Destroy", CL_WEB_LISTENER_SCOPE_DESTRUCTOR },',
		'{ "QLLoadHandler", "destroy", 0x00547FE8u, 0x10u, 0x004F2B10u, "QLLoadHandler_Destroy", CL_WEB_LISTENER_SCOPE_DESTRUCTOR },',
		'{ "QLJSHandler", "destroy", 0x00548010u, 0x08u, 0x004F23B0u, "QLJSHandler_Destroy", CL_WEB_LISTENER_SCOPE_DESTRUCTOR },',
	):
		assert source_anchor in cl_cgame

	reset_block = _extract_function_block(cl_cgame, "static void CL_WebHost_ResetRuntime( qboolean clearVisibility ) {")
	shutdown_block = _extract_function_block(
		cl_awesomium, 'extern "C" void CL_Awesomium_Shutdown( void ) {'
	)
	_assert_ordered_anchors(
		reset_block,
		(
			"CL_WebHost_ClearCursorOverride();",
			"CL_WebHost_ClearSurfaceImage();",
			"if ( cl_webHost.liveAwesomium ) {",
			"CL_Awesomium_Shutdown();",
			"cl_webHost.coreInitialised = qfalse;",
			"cl_webHost.sessionInitialised = qfalse;",
			"cl_webHost.viewInitialised = qfalse;",
			"cl_webHost.dataPakSourceInstalled = qfalse;",
			"cl_webHost.resourceInterceptorInstalled = qfalse;",
			"cl_webHost.jsMethodHandlerInstalled = qfalse;",
			"cl_webHost.dialogHandlerInstalled = qfalse;",
			"cl_webHost.viewHandlerInstalled = qfalse;",
			"cl_webHost.loadHandlerInstalled = qfalse;",
			"cl_webHost.liveAwesomium = qfalse;",
			"cls.keyCatchers &= ~KEYCATCH_BROWSER;",
		),
	)
	_assert_ordered_anchors(
		shutdown_block,
		(
			"if ( cl_awesomium.webView && cl_awe.webViewDestroy ) {",
			"cl_awe.webViewDestroy( cl_awesomium.webView );",
			"cl_awesomium.webView = NULL;",
			"if ( cl_awesomium.webSession && cl_awe.webSessionRelease ) {",
			"cl_awesomium.webSession = NULL;",
			"cl_awesomium.dataPakSource = NULL;",
			"if ( cl_awesomium.webCore && cl_awe.webCoreShutdown ) {",
			"cl_awe.webCoreShutdown();",
			"cl_awesomium.webCore = NULL;",
			"cl_awesomium.started = qfalse;",
			"cl_awesomium.urlLoaded = qfalse;",
		),
	)
	assert "Awesomium Handler Destroyer and Shutdown Cleanup Boundary" in mapping_round
	assert "Overall Awesomium/WebUI launch/runtime integration mapping confidence: **99.24% -> 99.26%**." in mapping_round


def test_awesomium_string_and_no_engine_helper_aliases_track_retail_reference_rows() -> None:
	aliases = _aliases()
	rows = _function_rows()
	hlil_part01 = _read_text(QL_STEAM_HLIL_PART01_PATH)
	hlil_part06 = _read_text(QL_STEAM_HLIL_PART06_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_awesomium = _read_text(CL_AWESOMIUM_WIN32_PATH)
	mapping_round = _read_text(
		REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_569.md"
	)

	expected_aliases = {
		"FUN_00431660": "AwesomiumListener_NoEngineCallback",
		"sub_431660": "AwesomiumListener_NoEngineCallback",
		"FUN_004317b0": "QLViewHandler_NoEngineCallback",
		"sub_4317B0": "QLViewHandler_NoEngineCallback",
		"sub_4317b0": "QLViewHandler_NoEngineCallback",
		"FUN_004317c0": "QLResourceInterceptor_NoEngineCallback",
		"sub_4317C0": "QLResourceInterceptor_NoEngineCallback",
		"sub_4317c0": "QLResourceInterceptor_NoEngineCallback",
		"FUN_00431cc0": "std_string_find_last_of_char_set",
		"sub_431CC0": "std_string_find_last_of_char_set",
		"sub_431cc0": "std_string_find_last_of_char_set",
		"FUN_00431d60": "AwesomiumWebString_ToStdStringUTF8",
		"sub_431D60": "AwesomiumWebString_ToStdStringUTF8",
		"sub_431d60": "AwesomiumWebString_ToStdStringUTF8",
	}
	for symbol, alias in expected_aliases.items():
		assert aliases[symbol] == alias

	for address, size in (
		(0x00431660, 3),
		(0x004317B0, 3),
		(0x004317C0, 3),
		(0x00431CC0, 148),
		(0x00431D60, 238),
	):
		row = rows[address]
		assert row["name"] == f"FUN_{address:08x}"
		assert int(row["size"]) == size

	for doc_anchor in (
		"| `sub_431660` | `AwesomiumListener_NoEngineCallback` |",
		"| `sub_4317b0` | `QLViewHandler_NoEngineCallback` |",
		"| `sub_4317c0` | `QLResourceInterceptor_NoEngineCallback` |",
		"| `sub_431cc0` | `std_string_find_last_of_char_set` |",
		"| `sub_431d60` | `AwesomiumWebString_ToStdStringUTF8` |",
	):
		assert doc_anchor in mapping_round

	for body_anchor in (
		"00431660    int32_t sub_431660() __pure",
		"004317b0    int32_t sub_4317b0() __pure",
		"004317c0    int32_t sub_4317c0() __pure",
		"00431cc0    void* __thiscall sub_431cc0(int32_t* arg1, int32_t arg2, int32_t arg3, int32_t arg4)",
		"00431d08          if (memchr(arg2, sx.d(*esi_2), arg4) == 0)",
		"00431d1a                  if (esi_2 == sub_406ff0(var_8_1))",
		"00431d51  return 0xffffffff",
		"00431d60    char* sub_431d60(char* arg1, Awesomium::WebString* arg2)",
		"00431db3  if (Awesomium::WebString::IsEmpty(this: arg2) == 0)",
		"00431dd1      uint32_t eax_5 = Awesomium::WebString::ToUTF8(this: arg2, nullptr, 0)",
		"00431de9      Awesomium::WebString::ToUTF8(this: arg2, eax_6, eax_5)",
		"00431df4      sub_406e80(&var_30, eax_6, eax_5)",
		"00431e4d  return arg1",
		"004327aa      char* eax_95 = sub_431d60(&var_4c, var_13c)",
		"00434726  sub_409ed0(&var_4c, &var_30, 0, sub_431cc0(&var_4c, &data_550004, 0xffffffff, 1))",
	):
		assert body_anchor in hlil_part01

	for vtable_anchor in (
		"00547f9c      int32_t (* const vFunc_2)() __pure = sub_4317c0",
		"00547fa8      int32_t (* const vFunc_0)() __pure = sub_431660",
		"00547fac      int32_t (* const vFunc_1)() __pure = sub_431660",
		"00547fb4      int32_t (* const vFunc_3)() __pure = sub_431660",
		"00547fc0      int32_t (* const vFunc_0)() __pure = sub_431660",
		"00547fdc      int32_t (* const vFunc_7)() __pure = sub_4317b0",
	):
		assert vtable_anchor in hlil_part06

	for source_anchor in (
		'{ "QLResourceInterceptor", "base/no-engine slot", 0x00547F94u, 0x08u, 0x004317C0u, "QLResourceInterceptor_NoEngineCallback", CL_WEB_LISTENER_SCOPE_NO_ENGINE_CALLBACK },',
		'{ "QLDialogHandler", "base/no-engine slot 0", 0x00547FA8u, 0x00u, 0x00431660u, "QLDialogHandler_NoEngineCallback", CL_WEB_LISTENER_SCOPE_NO_ENGINE_CALLBACK },',
		'{ "QLViewHandler", "base/no-engine slot 7", 0x00547FC0u, 0x1Cu, 0x004317B0u, "QLViewHandler_NoEngineCallback", CL_WEB_LISTENER_SCOPE_NO_ENGINE_CALLBACK },',
		"static qboolean QLJSHandler_OnMethodCall( const char *methodName, const char **arguments, int argumentCount ) {",
		"static qboolean QLJSHandler_OnMethodCallWithReturnValue( const char *methodName, const char **arguments, int argumentCount, char *outValue, size_t outValueSize ) {",
	):
		assert source_anchor in cl_cgame

	assert "Pops one queued qz_instance request from the injected WebUI bridge. Awesomium's" in cl_awesomium
	assert "string JSValue conversion is intentionally avoided here; requests are copied" in cl_awesomium
	assert "required = MultiByteToWideChar( CP_UTF8, 0, value, -1, NULL, 0 );" in cl_awesomium
	assert "Retail string conversion helpers are mapped as ABI evidence; source keeps the public WebUI contract on the injected qz_instance bridge." in mapping_round


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
	write_json_call_block = _extract_function_block(
		cl_cgame,
		"static qboolean CL_WebHost_WriteJavascriptJsonCall( char *script, int scriptSize, const char *prefix, const char *json, const char *suffix ) {",
	)
	config_sync_block = _extract_function_block(
		cl_cgame, "static void CL_WebHost_SyncConfigSnapshot( void ) {"
	)
	map_sync_block = _extract_function_block(
		cl_cgame, "static void CL_WebHost_SyncMapCatalogSnapshot( void ) {"
	)
	factory_sync_block = _extract_function_block(
		cl_cgame, "static void CL_WebHost_SyncFactoryCatalogSnapshot( void ) {"
	)
	execute_config_block = _extract_function_block(
		cl_cgame, "static qboolean CL_WebHost_ExecuteConfigSnapshot( const char *configJson ) {"
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
		"var pendingNativeFactories={};",
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
		"var beginNativeFactories=function(){pendingNativeFactories={};return true;};",
		"var addNativeFactories=function(list){var nextFactories=normalizeFactoryList(list);for(var pfk in nextFactories){if(hasOwn.call(nextFactories,pfk)){pendingNativeFactories[pfk]=nextFactories[pfk];}}return true;};",
		"var commitNativeFactories=function(){var ok=applyNativeFactories(pendingNativeFactories);pendingNativeFactories={};return ok;};",
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
		"window.__qlr_apply_native_config=applyNativeConfig;window.__qlr_apply_native_maps=applyNativeMaps;window.__qlr_apply_native_factories=applyNativeFactories;window.__qlr_begin_native_maps=beginNativeMaps;window.__qlr_add_native_maps=addNativeMaps;window.__qlr_commit_native_maps=commitNativeMaps;window.__qlr_begin_native_factories=beginNativeFactories;window.__qlr_add_native_factories=addNativeFactories;window.__qlr_commit_native_factories=commitNativeFactories;window.__qlr_set_native_cvar=setNativeCvar;",
		"if(window.__qlr_pending_native_maps){applyNativeMaps(window.__qlr_pending_native_maps);window.__qlr_pending_native_maps=null;}",
		"if(window.__qlr_pending_native_factories){applyNativeFactories(window.__qlr_pending_native_factories);window.__qlr_pending_native_factories=null;}",
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
	assert "Q_strncpyz( script, prefix, scriptSize );" in write_json_call_block
	assert "Q_strcat( script, scriptSize, json );" in write_json_call_block
	assert "Q_strcat( script, scriptSize, suffix );" in write_json_call_block
	assert "CL_WebHost_ExecuteConfigSnapshot( configJson )" in config_sync_block
	assert "Com_sprintf(" not in config_sync_block
	assert "Com_sprintf(" not in execute_config_block
	assert "if ( cl_webHost.mapCatalogSynced ) {" in map_sync_block
	assert "cl_webHost.nextMapCatalogSyncFrame = 0;" in map_sync_block
	assert "cl_webHost.mapCatalogSynced && cl_webHost.frameSequence" not in map_sync_block
	assert "if ( cl_webHost.factoryCatalogSynced ) {" in factory_sync_block
	assert "cl_webHost.nextFactoryCatalogSyncFrame = 0;" in factory_sync_block
	assert "cl_webHost.factoryCatalogSynced && cl_webHost.frameSequence" not in factory_sync_block

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
		"#define CL_WEB_FACTORY_SYNC_CHUNK_CHARS 8192",
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
		"CL_WebHost_ExecuteConfigSnapshot",
		"CL_WebHost_WriteJavascriptJsonCall",
		"CL_WebHost_MapCatalogBridgeReady",
		"typeof window.qz_instance.GetFactoryList==='function'",
		"typeof window.__qlr_begin_native_factories==='function'",
		"typeof window.__qlr_add_native_factories==='function'",
		"typeof window.__qlr_commit_native_factories==='function'",
		"CL_WebHost_ExecuteMapCatalogBatches",
		"CL_WebHost_ExecuteMapCatalogBatch",
		"CL_WebHost_ExecuteFactoryCatalogBatches",
		"CL_WebHost_ExecuteFactoryCatalogBatch",
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


def test_awesomium_js_method_handler_dispatch_retail_hlil_flow_is_pinned() -> None:
	rows = _function_rows()
	aliases = _aliases()
	hlil_part01 = _read_text(QL_STEAM_HLIL_PART01_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)

	for address, owner, size in (
		(0x00431570, "QLJSHandler_LookupMethodId", 199),
		(0x00431E50, "QLJSHandler_OnMethodCall", 241),
		(0x004328B0, "QLJSHandler_OnMethodCallWithReturnValue", 284),
	):
		assert aliases[f"FUN_{address:08x}"] == owner
		assert aliases[f"sub_{address:06X}"] == owner
		assert aliases[f"sub_{address:06x}"] == owner
		assert rows[address]["name"] == f"FUN_{address:08x}"
		assert int(rows[address]["size"]) == size

	_assert_ordered_anchors(
		hlil_part01,
		(
			"00431570    int32_t sub_431570()",
			"for (char const (** i)[0x11] = &data_55c008; i s< 0x55c1a0; i = &i[3])",
			"sub_4314d0(&var_18, *i)",
			"Awesomium::WebString::operator==(this: ecx_1, eax_4)",
			"int32_t result = *(var_14 * 0xc + &data_55c00c)",
			"return 0x22",
		),
	)
	_assert_ordered_anchors(
		hlil_part01,
		(
			"00431e50    uint32_t __thiscall sub_431e50(Awesomium::WebString* arg1, void* arg2, Awesomium::JSArray* arg3)",
			"Awesomium::WebString::WebString(this: arg1, arg2)",
			"int32_t eax_3 = sub_431570()",
			"if (eax_3 - 2 u> 0x1f)",
			"switch (result)",
			"Awesomium::JSArray::size(this: arg3)",
			"Awesomium::JSValue::ToString(this: Awesomium::JSArray::operator[](",
			"sub_4c8900(2, var_13c)",
			"sub_4ec650(eax_10, var_13c)",
			"SteamFriends()",
			"OpenClipboard(hWndNewOwner: var_13c)",
			"SetClipboardData(uFormat: 1, hMem: var_13c)",
			"sub_463090(var_138)",
			"sub_4630b0(var_138, var_134)",
			"result = sub_462e80()",
			"result = sub_4649b0()",
			"result = sub_4649e0()",
			"sub_465630(var_13c)",
			"sub_464b10(var_138, var_134)",
			"result = sub_464bb0()",
			"sub_464ac0(var_13c)",
			"SteamUserStats() + 0x40",
			"SteamFriends()",
			"SteamMatchmaking()",
			"result = sub_460dc0(var_138)",
			"data_12d306c = edi_3",
			"SteamUtils()",
			'"Unimplemented plugin call %s (%s',
		),
	)
	_assert_ordered_anchors(
		hlil_part01,
		(
			"004328b0    Awesomium::JSValue* __thiscall sub_4328b0(Awesomium::WebString* arg1, Awesomium::JSValue* arg2, int32_t** arg3, Awesomium::JSArray* arg4)",
			"Awesomium::WebString::WebString(this: arg1, arg3)",
			"j_3, ecx = sub_431570()",
			"switch (j_3)",
			"fopen(sub_4cec90(sub_4ccda0(\"fs_basepath\"), eax_8, j_2), &data_52cb90)",
			"Awesomium::JSValue::JSValue(this: arg2, j_2.b)",
			"ecx.b = data_1528ba0 != 1",
			"sub_4314d0(&var_224, sub_4ccda0(j_2))",
			"sub_4cce90(x87_r0, x87_r1, j_70, j_72, j_2)",
			"sub_4cce90(x87_r0, x87_r1, j_71, nullptr, j_2)",
			"Awesomium::JSObject::JSObject(this: ecx)",
			'"sysname"',
			'"gametypes"',
			'"title"',
			'"basegt"',
		),
	)

	method_call_block = _extract_function_block(
		cl_cgame, "static qboolean QLJSHandler_OnMethodCall( const char *methodName, const char **arguments, int argumentCount ) {"
	)
	return_call_block = _extract_function_block(
		cl_cgame,
		"static qboolean QLJSHandler_OnMethodCallWithReturnValue( const char *methodName, const char **arguments, int argumentCount, char *outValue, size_t outValueSize ) {",
	)
	lookup_block = _extract_function_block(
		cl_cgame, "static const clWebMethodBinding_t *QLJSHandler_LookupMethodBinding( const char *methodName ) {"
	)

	for method_anchor in (
		'{ "IsPakFilePresent", 0x0055C008u, CL_WEB_METHOD_IS_PAK_FILE_PRESENT, qtrue },',
		'{ "SendGameCommand", 0x0055C020u, CL_WEB_METHOD_SEND_GAME_COMMAND, qfalse },',
		'{ "GetCvar", 0x0055C038u, CL_WEB_METHOD_GET_CVAR, qtrue },',
		'{ "OpenURL", 0x0055C080u, CL_WEB_METHOD_OPEN_URL, qfalse },',
		'{ "RequestServers", 0x0055C0B0u, CL_WEB_METHOD_REQUEST_SERVERS, qfalse },',
		'{ "GetFriendList", 0x0055C128u, CL_WEB_METHOD_GET_FRIEND_LIST, qtrue },',
		'{ "GetAllUGC", 0x0055C170u, CL_WEB_METHOD_GET_ALL_UGC, qfalse },',
		'{ "GetNextKeyDown", 0x0055C17Cu, CL_WEB_METHOD_GET_NEXT_KEY_DOWN, qfalse },',
		'{ "SetFavoriteServer", 0x0055C188u, CL_WEB_METHOD_SET_FAVORITE_SERVER, qfalse },',
		'{ "NoOp", 0x0055C194u, CL_WEB_METHOD_NO_OP, qfalse },',
	):
		assert method_anchor in cl_cgame

	_assert_ordered_anchors(
		lookup_block,
		(
			"for ( i = 0; i < CL_WEB_MAX_QZ_METHODS && cl_webMethodBindings[i].name; i++ ) {",
			"!Q_stricmp( cl_webMethodBindings[i].name, methodName )",
			"return &cl_webMethodBindings[i];",
			"return NULL;",
		),
	)
	_assert_ordered_anchors(
		method_call_block,
		(
			"binding = QLJSHandler_LookupMethodBinding( methodName );",
			"if ( !binding || binding->returnsValue ) {",
			"case CL_WEB_METHOD_SEND_GAME_COMMAND:",
			'Cbuf_ExecuteText( EXEC_APPEND, va( "%s\\n", arguments[0] ) );',
			"case CL_WEB_METHOD_WRITE_TEXT_FILE:",
			"return CL_WebHost_WriteTextFile( arguments[0], arguments[1] );",
			"case CL_WEB_METHOD_OPEN_URL:",
			'strstr( arguments[0], "://" )',
			"return QLWebHost_OpenURL( arguments[0] );",
			"return QLWebHost_NavigateOrOpen( arguments[0] );",
			"case CL_WEB_METHOD_OPEN_STEAM_OVERLAY_URL:",
			"return CL_Steam_OpenOverlayUrl( arguments[0] );",
			"case CL_WEB_METHOD_SET_CLIPBOARD_TEXT:",
			"Sys_SetClipboardData( arguments[0] ? arguments[0] : \"\" );",
			"case CL_WEB_METHOD_REQUEST_SERVERS:",
			"return CL_Steam_RequestServers( QLJSHandler_CoerceIntegerArgument( arguments[0] ) );",
			"case CL_WEB_METHOD_REQUEST_SERVER_DETAILS:",
			"return CL_Steam_RequestServerDetails(",
			"case CL_WEB_METHOD_REFRESH_LIST:",
			"return CL_Steam_RefreshServerList();",
			"case CL_WEB_METHOD_CREATE_LOBBY:",
			"return CL_Steam_CreateLobby();",
			"case CL_WEB_METHOD_GET_ALL_UGC:",
			"return CL_Steam_RequestAllUGC( QLJSHandler_CoerceIntegerArgument( arguments[0] ) );",
			"case CL_WEB_METHOD_GET_NEXT_KEY_DOWN:",
			"cl_webHost.keyCaptureArmed = qtrue;",
			"case CL_WEB_METHOD_NO_OP:",
			"return qtrue;",
			"case CL_WEB_METHOD_SET_FAVORITE_SERVER:",
			"return CL_WebHost_SetFavoriteServer(",
		),
	)
	_assert_ordered_anchors(
		return_call_block,
		(
			"binding = QLJSHandler_LookupMethodBinding( methodName );",
			"if ( !binding || !binding->returnsValue || !outValue || outValueSize == 0 ) {",
			"case CL_WEB_METHOD_IS_PAK_FILE_PRESENT:",
			"case CL_WEB_METHOD_FILE_EXISTS:",
			'Q_strncpyz( outValue, FS_FileExists( arguments[0] ) ? "1" : "0", outValueSize );',
			"case CL_WEB_METHOD_IS_GAME_RUNNING:",
			"cls.state >= CA_CONNECTED && cls.state < CA_CINEMATIC",
			"case CL_WEB_METHOD_GET_CVAR:",
			"Cvar_VariableStringBuffer( arguments[0], outValue, (int)outValueSize );",
			"case CL_WEB_METHOD_SET_CVAR:",
			"Cvar_Set( arguments[0], arguments[1] ? arguments[1] : \"\" );",
			"case CL_WEB_METHOD_RESET_CVAR:",
			"Cvar_Reset( arguments[0] );",
			"case CL_WEB_METHOD_GET_MAP_LIST:",
			"CL_WebHost_BuildMapListJson( outValue, outValueSize );",
			"case CL_WEB_METHOD_GET_FACTORY_LIST:",
			"CL_WebHost_BuildFactoryListJson( outValue, outValueSize );",
			"case CL_WEB_METHOD_GET_DEMO_LIST:",
			"CL_WebHost_BuildDemoListJson( outValue, outValueSize );",
			"case CL_WEB_METHOD_GET_FRIEND_LIST:",
			"CL_WebHost_BuildFriendListJson( outValue, outValueSize );",
			"case CL_WEB_METHOD_GET_CONFIG:",
			"CL_WebHost_BuildConfigJson( outValue, outValueSize );",
			"case CL_WEB_METHOD_GET_CURSOR_POSITION:",
			"CL_WebHost_RequestCursorPosition( &x, &y );",
			"case CL_WEB_METHOD_GET_CLIPBOARD_TEXT:",
			"clipboardData = Sys_GetClipboardData();",
		),
	)


def test_awesomium_tagged_info_string_comm_notice_wiring_matches_retail_slot() -> None:
	aliases = _aliases()
	rows = _function_rows()
	hlil_part04 = _read_text(QL_STEAM_HLIL_PART04_PATH)
	hlil_part05 = _read_text(QL_STEAM_HLIL_PART05_PATH)
	mapping_round = _read_text(
		REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_576.md"
	)
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
	append_pair_block = _extract_function_block(
		cl_main, "static void CL_WebView_AppendTaggedInfoPair( char *payload, size_t payloadSize, const char *key, const char *value, qboolean *first ) {"
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

	for address, owner, size in (
		(0x004BF5D0, "QLWebView_PublishTaggedInfoString", 312),
		(0x004EC6D0, "QLWebView_InvokeCommNoticeThunk", 9),
		(0x004F2950, "QLWebView_InvokeCommNotice", 192),
	):
		assert aliases[f"FUN_{address:08x}"] == owner
		assert aliases[f"sub_{address:06X}"] == owner
		assert aliases[f"sub_{address:06x}"] == owner
		assert rows[address]["name"] == f"FUN_{address:08x}"
		assert int(rows[address]["size"]) == size

	_assert_ordered_anchors(
		hlil_part04,
		(
			"004b03b0    int32_t sub_4b03b0()",
			"004b03b4  return sub_4bf5d0() __tailcall",
			"004bf5d0    int32_t sub_4bf5d0(int32_t arg1, char* arg2)",
			"sub_429250(&var_838, nullptr)",
			'004bf60b  sub_429440(sub_42a110(&var_838, "MSG_TYPE"), arg1)',
			"if (*arg2 != 0)",
			"sub_4d9380(&var_828, &var_408, &var_808)",
			"sub_429440(sub_42a110(&var_838, &var_408), &var_808)",
			"sub_42a850(&var_838, &var_824)",
			"int32_t eax_4 = sub_525ed8()",
			"strncpy(eax_4, eax_5, var_814)",
			"004bf6b5  sub_4ec6d0()",
			"int32_t result = sub_429620(&var_838)",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004ec6d0    int32_t sub_4ec6d0()",
			"004ec6d4  return sub_4f2950() __tailcall",
			"004f2950    void sub_4f2950(uint32_t arg1)",
			"if (data_12d3050 != 0)",
			"Awesomium::JSValue::IsUndefined(this: &data_12d3078)",
			"Awesomium::JSArray::Push(this: ecx_3, eax_1)",
			"sub_4314d0(&var_10, arg1)",
			"Awesomium::JSArray::Push(this: ecx_6, eax_4)",
			'char* eax_5 = sub_4314d0(&var_10, "OnCommNotice")',
			"Awesomium::JSObject::InvokeAsync(",
		),
	)

	assert "CG_QL_IMPORT_PUBLISH_TAGGED_INFO_STRING = 116," in cg_public
	assert "CG_QL_IMPORT_TAGGED_CVAR_STRING_BUFFER" not in cg_public
	assert "void CL_WebView_InvokeCommNotice( const char *message );" in client_h
	assert "void CL_WebView_PublishTaggedInfoString( const char *messageType, const char *infoString );" in client_h
	assert 'CL_WebView_PublishEvent( "web.commNotice", message ? message : "" );' in invoke_block
	_assert_ordered_anchors(
		append_pair_block,
		(
			"CL_Steam_JsonEscape( key, escapedKey, sizeof( escapedKey ) );",
			'CL_Steam_JsonEscape( value ? value : "", escapedValue, sizeof( escapedValue ) );',
			'CL_Steam_AppendJsonFragment( payload, payloadSize, "%s\\"%s\\":\\"%s\\"", *first ? "" : ",", escapedKey, escapedValue );',
			"*first = qfalse;",
		),
	)
	_assert_ordered_anchors(
		publish_block,
		(
			"payload[0] = '\\0';",
			"first = qtrue;",
			'CL_Steam_AppendJsonFragment( payload, sizeof( payload ), "{" );',
			'CL_WebView_AppendTaggedInfoPair( payload, sizeof( payload ), "MSG_TYPE", messageType ? messageType : "", &first );',
			"while ( *cursor ) {",
			"Info_NextPair( &cursor, key, value );",
			"if ( !key[0] ) {",
			"CL_WebView_AppendTaggedInfoPair( payload, sizeof( payload ), key, value, &first );",
			'CL_Steam_AppendJsonFragment( payload, sizeof( payload ), "}" );',
			"CL_WebView_InvokeCommNotice( payload );",
		),
	)
	assert "CL_WebView_PublishTaggedInfoString( messageType, infoString );" in cgame_trap_block
	assert "CG_GetNativeImportFunction( CG_QL_IMPORT_PUBLISH_TAGGED_INFO_STRING )" in syscall_block
	assert '((void (QDECL *)( const char *, const char * ))import)( messageType, infoString );' in syscall_block
	assert "(void)messageType;" in null_publish_block
	assert "(void)infoString;" in null_publish_block
	assert "TaggedCvarStringBuffer" not in cl_cgame
	assert "TaggedCvarStringBuffer" not in cg_syscalls
	for round_anchor in (
		"Quake Live Steam Mapping Round 576: Awesomium Tagged Info Comm Notice Alias Closure",
		"`0x004BF5D0`: `QLWebView_PublishTaggedInfoString`",
		"`0x004EC6D0`: `QLWebView_InvokeCommNoticeThunk`",
		"`0x004F2950`: `QLWebView_InvokeCommNotice`",
		"`MSG_TYPE`",
		"`OnCommNotice`",
		"Overall Awesomium/WebUI launch/runtime integration mapping confidence:",
		"**99.20% -> 99.22%**",
	):
		assert round_anchor in mapping_round


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
	console_escape_index = key_event_block.index("if ( cls.keyCatchers & KEYCATCH_CONSOLE ) {", escape_block_index)
	console_escape_return_index = key_event_block.index("return;", console_escape_index)
	browser_escape_index = key_event_block.index("if ( cls.keyCatchers & KEYCATCH_BROWSER ) {", escape_block_index)
	browser_escape_return_index = key_event_block.index("return;", browser_escape_index)
	menu_toggle_index = key_event_block.index("CL_ToggleMenuInternal", escape_block_index)
	assert console_escape_return_index < browser_escape_index
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
		"QL_WEB_BRIDGE_SLOT_RESERVED_21C0 = 0x40",
		"QL_WEB_BRIDGE_SLOT_SETUP_ADVERT_CELL_SHADER = 0x50",
		"QL_WEB_BRIDGE_SLOT_SETUP_UI_ADVERT_CELL_SHADER = 0x54",
		"QL_WEB_BRIDGE_SLOT_REFRESH_ADVERT_CELL_SHADER = 0x58",
		"QL_WEB_BRIDGE_SLOT_REFRESH_UI_ADVERT_CELL_SHADER = 0x5c",
		"QL_WEB_BRIDGE_SLOT_ACTIVATE_ADVERT = 0x68",
		"QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( setActiveAdvert, QL_WEB_BRIDGE_SLOT_SET_ACTIVE_ADVERT );",
		"QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( reserved21C0, QL_WEB_BRIDGE_SLOT_RESERVED_21C0 );",
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


def test_awesomium_advert_bridge_retail_hlil_forwarders_are_pinned() -> None:
	rows = _function_rows()
	aliases = _aliases()
	hlil_part05 = _read_text(QL_STEAM_HLIL_PART05_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	client_h = _read_text(CLIENT_H_PATH)

	for address, owner, size in (
		(0x004F1EF0, "AdvertisementBridge_SetActiveAdvert", 21),
		(0x004F1F10, "AdvertisementBridge_SetAppActivation", 26),
		(0x004F1F30, "AdvertisementBridge_SetClientStateFlags", 31),
		(0x004F1F50, "AdvertisementBridge_SetFrameTime", 31),
		(0x004F1F70, "AdvertisementBridge_UpdateViewParameters", 74),
		(0x004F1FC0, "AdvertisementBridge_Reserved1FC0", 31),
		(0x004F1FE0, "AdvertisementBridge_SetMapPath", 31),
		(0x004F2040, "AdvertisementBridge_GetCellLabel", 51),
		(0x004F2080, "AdvertisementBridge_GetCellDisplayState", 30),
		(0x004F20A0, "AdvertisementBridge_SetVisibilityTraceCallback", 26),
		(0x004F20E0, "AdvertisementBridge_SetupUIAdvertCellShader", 53),
		(0x004F2120, "AdvertisementBridge_RefreshUIAdvertCellShader", 53),
		(0x004F2160, "AdvertisementBridge_GetLabelList1Count", 20),
		(0x004F2180, "AdvertisementBridge_GetLabelList1Entry", 51),
		(0x004F21E0, "AdvertisementBridge_SetupAdvertCellShader", 53),
		(0x004F2220, "AdvertisementBridge_RefreshAdvertCellShader", 53),
		(0x004F2260, "AdvertisementBridge_GetLabelList2Count", 20),
		(0x004F2280, "AdvertisementBridge_GetLabelList2Entry", 51),
		(0x004F22C0, "AdvertisementBridge_ActivateAdvert", 26),
		(0x004F22E0, "AdvertisementBridge_IsDelayElapsed", 34),
		(0x004F2310, "AdvertisementBridge_ClearDelay", 11),
	):
		assert aliases[f"FUN_{address:08x}"] == owner
		assert aliases[f"sub_{address:06X}"] == owner
		assert aliases[f"sub_{address:06x}"] == owner
		assert rows[address]["name"] == f"FUN_{address:08x}"
		assert int(rows[address]["size"]) == size

	for symbol, owner in (
		("sub_4F2000", "AdvertisementBridge_InitCGame"),
		("sub_4f2000", "AdvertisementBridge_InitCGame"),
		("sub_4F2020", "AdvertisementBridge_ShutdownCGame"),
		("sub_4f2020", "AdvertisementBridge_ShutdownCGame"),
		("sub_4F20C0", "AdvertisementBridge_InitUI"),
		("sub_4f20c0", "AdvertisementBridge_InitUI"),
		("sub_4F21C0", "AdvertisementBridge_Reserved21C0"),
		("sub_4f21c0", "AdvertisementBridge_Reserved21C0"),
	):
		assert aliases[symbol] == owner

	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f1ef0    int32_t sub_4f1ef0()",
			"int32_t* ecx = data_12d2670",
			"if (ecx == 0)",
			"return 0xffffffff",
			"jump(*(*ecx + 8))",
			"004f1f10    void sub_4f1f10(int32_t arg1)",
			"(*(*ecx + 0xc))(arg1)",
			"004f1f30    int32_t sub_4f1f30(int32_t arg1)",
			"return arg1",
			"return (*(*ecx + 0x2c))(arg1)",
			"004f1f50    int32_t sub_4f1f50(int32_t arg1)",
			"return (*(*ecx + 0x10))(arg1)",
			"004f1f70    int32_t sub_4f1f70(int32_t arg1, int32_t arg2, int32_t arg3, int32_t arg4, float arg5, float arg6, float arg7, int32_t arg8, int32_t arg9)",
			"return (*(*ecx + 0x14))(arg1, arg2, arg3, arg4, fconvert.s(fconvert.t(arg5)),",
			"004f1fc0    int32_t sub_4f1fc0(int32_t arg1)",
			"return (*(*ecx + 0x1c))(arg1)",
			"004f1fe0    int32_t sub_4f1fe0(int32_t arg1)",
			"return (*(*ecx + 0x20))(arg1)",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f2000    int32_t sub_4f2000()",
			"jump(*(*ecx + 0x24))",
			"004f2020    int32_t sub_4f2020()",
			"jump(*(*ecx + 0x28))",
			"004f2040    int32_t sub_4f2040(int32_t arg1, char* arg2, int32_t arg3)",
			"return (*(*ecx + 0x3c))(arg1, arg2, arg3)",
			"if (arg3 s>= 1)",
			"*arg2 = 0",
			"return 0xffffffff",
			"004f2080    int32_t sub_4f2080(int32_t arg1)",
			"return (*(*ecx + 0x38))(arg1)",
			"004f20a0    void sub_4f20a0(int32_t arg1)",
			"(*(*ecx + 0x18))(arg1)",
			"004f20c0    void sub_4f20c0()",
			"jump(*(*ecx + 0x44))",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f20e0    int32_t sub_4f20e0(char* arg1, int32_t arg2, int32_t arg3)",
			"int32_t result = (*(*ecx + 0x54))(arg1, arg2, arg3)",
			"if (result != 0)",
			"return result",
			"return sub_4589d0(arg1, nullptr, 0)",
			"004f2120    int32_t sub_4f2120(char* arg1, int32_t arg2, int32_t arg3)",
			"int32_t result = (*(*ecx + 0x5c))(arg1, arg2, arg3)",
			"return sub_4589d0(arg1, nullptr, 0)",
			"004f2160    int32_t sub_4f2160()",
			"jump(*(*ecx + 0x4c))",
			"004f2180    int32_t sub_4f2180(int32_t arg1, char* arg2, int32_t arg3)",
			"return (*(*ecx + 0x64))(arg1, arg2, arg3)",
			"if (arg3 s>= 1)",
			"*arg2 = 0",
			"return 0xffffffff",
			"004f21c0    void sub_4f21c0()",
			"jump(*(*ecx + 0x40))",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f21e0    int32_t sub_4f21e0(char* arg1, int32_t arg2, int32_t arg3)",
			"int32_t result = (*(*ecx + 0x50))(arg1, arg2, arg3)",
			"return sub_4589d0(arg1, nullptr, 0)",
			"004f2220    int32_t sub_4f2220(char* arg1, int32_t arg2, int32_t arg3)",
			"int32_t result = (*(*ecx + 0x58))(arg1, arg2, arg3)",
			"return sub_4589d0(arg1, nullptr, 0)",
			"004f2260    int32_t sub_4f2260()",
			"jump(*(*ecx + 0x48))",
			"004f2280    int32_t sub_4f2280(int32_t arg1, char* arg2, int32_t arg3)",
			"return (*(*ecx + 0x60))(arg1, arg2, arg3)",
			"if (arg3 s>= 1)",
			"*arg2 = 0",
			"return 0xffffffff",
			"004f22c0    void sub_4f22c0(int32_t arg1)",
			"(*(*ecx + 0x68))(arg1)",
			"004f22e0    int32_t sub_4f22e0()",
			"if (data_12d2674 == 0)",
			"return 1",
			"result.b = sub_4ef510() s> data_12d2674",
			"004f2310    int32_t sub_4f2310()",
			"data_12d2674 = 0",
		),
	)

	for expected in (
		"QL_WEB_BRIDGE_SLOT_SET_ACTIVE_ADVERT = 0x08",
		"QL_WEB_BRIDGE_SLOT_SET_APP_ACTIVATION = 0x0c",
		"QL_WEB_BRIDGE_SLOT_SET_FRAME_TIME = 0x10",
		"QL_WEB_BRIDGE_SLOT_UPDATE_VIEW_PARAMETERS = 0x14",
		"QL_WEB_BRIDGE_SLOT_SET_VISIBILITY_TRACE_CALLBACK = 0x18",
		"QL_WEB_BRIDGE_SLOT_RESERVED_1FC0 = 0x1c",
		"QL_WEB_BRIDGE_SLOT_SET_MAP_PATH = 0x20",
		"QL_WEB_BRIDGE_SLOT_INIT_CGAME = 0x24",
		"QL_WEB_BRIDGE_SLOT_SHUTDOWN_CGAME = 0x28",
		"QL_WEB_BRIDGE_SLOT_SET_CLIENT_STATE_FLAGS = 0x2c",
		"QL_WEB_BRIDGE_SLOT_GET_CELL_DISPLAY_STATE = 0x38",
		"QL_WEB_BRIDGE_SLOT_GET_CELL_LABEL = 0x3c",
		"QL_WEB_BRIDGE_SLOT_RESERVED_21C0 = 0x40",
		"QL_WEB_BRIDGE_SLOT_INIT_UI = 0x44",
		"QL_WEB_BRIDGE_SLOT_GET_LABEL_LIST2_COUNT = 0x48",
		"QL_WEB_BRIDGE_SLOT_GET_LABEL_LIST1_COUNT = 0x4c",
		"QL_WEB_BRIDGE_SLOT_SETUP_ADVERT_CELL_SHADER = 0x50",
		"QL_WEB_BRIDGE_SLOT_SETUP_UI_ADVERT_CELL_SHADER = 0x54",
		"QL_WEB_BRIDGE_SLOT_REFRESH_ADVERT_CELL_SHADER = 0x58",
		"QL_WEB_BRIDGE_SLOT_REFRESH_UI_ADVERT_CELL_SHADER = 0x5c",
		"QL_WEB_BRIDGE_SLOT_GET_LABEL_LIST2_ENTRY = 0x60",
		"QL_WEB_BRIDGE_SLOT_GET_LABEL_LIST1_ENTRY = 0x64",
		"QL_WEB_BRIDGE_SLOT_ACTIVATE_ADVERT = 0x68",
		"QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( setFrameTime, QL_WEB_BRIDGE_SLOT_SET_FRAME_TIME );",
		"QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( reserved21C0, QL_WEB_BRIDGE_SLOT_RESERVED_21C0 );",
		"QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( getLabelList2Entry, QL_WEB_BRIDGE_SLOT_GET_LABEL_LIST2_ENTRY );",
	):
		assert expected in cl_cgame

	for signature, anchors in (
		(
			"static int QLWebBridge_SetFrameTime( ql_web_bridge_t *bridge, int frameTime ) {",
			(
				"if ( !bridge || !bridge->advertisement || !bridge->advertisement->initialised ) {",
				"bridge->advertisement->frameTime = frameTime;",
				"CL_RefreshOnlineServicesBridgeState();",
				"return frameTime;",
			),
		),
		(
			"static int QLWebBridge_UpdateViewParameters( ql_web_bridge_t *bridge, int x, int y, int width, int height, float fovX, float fovY, float zFar, int time, int flags ) {",
			(
				"bridge->advertisement->viewWidth = width;",
				"bridge->advertisement->viewHeight = height;",
				"bridge->advertisement->frameTime = time;",
				"bridge->clientStateFlags = flags;",
			),
		),
		(
			"static int QLWebBridge_GetCellDisplayState( ql_web_bridge_t *bridge, int cellId ) {",
			(
				"cellId == advertisement->activatedAdvertCellId",
				"return 2;",
				"cellId == advertisement->activeAdvertCellId",
				"return 1;",
				"return 0;",
			),
		),
		(
			"static int QLWebBridge_GetCellLabel( ql_web_bridge_t *bridge, int cellId, char *buffer, int bufferSize ) {",
			(
				"CL_AdvertisementBridge_ClearLabel( buffer, bufferSize );",
				"cellId == advertisement->activatedAdvertCellId",
				"cell %d activated",
				"cellId == advertisement->activeAdvertCellId",
				"cell %d active",
				"cell %d available",
			),
		),
		(
			"static qhandle_t QLWebBridge_RegisterDefaultAdvertCellShader( const char *defaultContent ) {",
			(
				"if ( !defaultContent || !defaultContent[0] ) {",
				"return CL_Steam_RegisterShader( defaultContent );",
			),
		),
		(
			"static int QLWebBridge_GetLabelList2Entry( ql_web_bridge_t *bridge, int index, char *buffer, int bufferSize ) {",
			(
				"state: %s frame=%d view=%dx%d",
				"active=%d activated=%d",
			),
		),
		(
			"static int QLWebBridge_GetLabelList1Entry( ql_web_bridge_t *bridge, int index, char *buffer, int bufferSize ) {",
			(
				"bridge: %s [%s]",
				"overlay: compiled=%d available=%d browser=%d",
			),
		),
	):
		_assert_ordered_anchors(_extract_function_block(cl_cgame, signature), anchors)

	for expected in (
		"qboolean CL_AdvertisementBridge_IsDelayElapsed( void );",
		"void CL_AdvertisementBridge_ClearDelay( void );",
		"void CL_AdvertisementBridge_RefreshLoadingViewParameters( void );",
		"void CL_AdvertisementBridge_UpdateLoadingViewParameters( void );",
		"void CL_AdvertisementBridge_InitUI( void );",
		"void CL_AdvertisementBridge_ActivateAdvert( int cellId );",
		"void CL_AdvertisementBridge_SetActiveAdvert( int cellId );",
		"int CL_AdvertisementBridge_GetCellDisplayState( int cellId );",
		"void CL_AdvertisementBridge_GetCellLabel( int cellId, char *buffer, int bufferSize );",
	):
		assert expected in client_h

	assert "return cls.realtime > cl_advertisementBridge.delayDeadline ? qtrue : qfalse;" in _extract_function_block(
		cl_cgame, "qboolean CL_AdvertisementBridge_IsDelayElapsed( void ) {"
	)
	assert "cl_advertisementBridge.delayDeadline = 0;" in _extract_function_block(
		cl_cgame, "void CL_AdvertisementBridge_ClearDelay( void ) {"
	)


def test_awesomium_browser_control_navigation_retail_hlil_flow_is_pinned() -> None:
	rows = _function_rows()
	aliases = _aliases()
	hlil_part05 = _read_text(QL_STEAM_HLIL_PART05_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)

	for address, owner, size in (
		(0x004F23E0, "QLWebView_SetLocationHash", 234),
		(0x004F24D0, "QLWebHost_HideBrowser", 182),
		(0x004F2A60, "QLWebHost_Shutdown", 32),
		(0x004F3160, "QLWebHost_OpenRelativeURL", 107),
		(0x004F31D0, "QLWebHost_NavigateOrOpen", 129),
	):
		assert aliases[f"FUN_{address:08x}"] == owner
		assert aliases[f"sub_{address:06X}"] == owner
		assert aliases[f"sub_{address:06x}"] == owner
		assert rows[address]["name"] == f"FUN_{address:08x}"
		assert int(rows[address]["size"]) == size

	for symbol, owner in (
		("sub_4F2A10", "CL_Web_ClearCache_f"),
		("sub_4F2A30", "CL_Web_Reload_f"),
		("sub_4F3CB0", "CL_Web_ShowError_f"),
	):
		assert aliases[symbol] == owner

	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f23e0    int32_t* sub_4f23e0(uint32_t arg1)",
			"int32_t* result = data_12d3050",
			"if (result == 0)",
			'char* eax_1 = sub_4314d0(&var_c, "document.location")',
			"Awesomium::JSValue::IsUndefined",
			"Awesomium::JSValue::ToObject(this: ecx_5)",
			"Awesomium::JSObject::JSObject(this: ecx_6, eax_5)",
			"sub_4314d0(&var_14, arg1)",
			"Awesomium::JSValue::JSValue(this: ecx_8, eax_6)",
			'sub_4314d0(&var_10, "hash")',
			"Awesomium::JSObject::SetPropertyAsync(",
			"004f24d0    void sub_4f24d0()",
			"if (data_12d304c != 0)",
			"if (ecx_1 != 0 && data_12d306c == 0)",
			"(*(*ecx_1 + 0xa8))()",
			"(*(*data_12d3050 + 0xb4))()",
			"data_15ee390 = 0",
			'sub_4cd250("web_browserActive", U"0")',
			"data_1528ba4.d ^= 0x20",
			"LoadCursorA(hInstance: nullptr, lpCursorName: 0x7f00)",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f2a10    void sub_4f2a10()",
			"int32_t* ecx = data_12d3044",
			"if (ecx == 0)",
			"jump(*(*ecx + 0x1c))",
			"004f2a30    void sub_4f2a30()",
			"if (data_12d3050 != 0)",
			"(*(*data_12d3044 + 0x1c))()",
			"(*(*data_12d3050 + 0x78))(1)",
			"004f2a60    void sub_4f2a60()",
			"int32_t* ecx_1 = data_12d3050",
			"(**ecx_1)()",
			"if (data_12d304c == 0)",
			"return Awesomium::WebCore::Shutdown() __tailcall",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f3160    HCURSOR sub_4f3160()",
			"char* eax_2 = sub_4c7ee0(0)",
			"sub_4d90c0(&i_1, 0x400, eax_2 - &eax_2[1] + 0x11f81b9)",
			"HCURSOR result = sub_4f2d30(&i_1)",
			"004f31d0    int32_t* sub_4f31d0()",
			"char* eax_2 = sub_4c7ee0(0)",
			"sub_4d90c0(&i_1, 0x400, eax_2 - &eax_2[1] + 0x11f81b9)",
			"int32_t* result = sub_4f23e0(&i_1)",
			"if (data_15ee390 == 0)",
			"result = sub_4f2d30(&data_54f9da)",
			"004f3cb0    int32_t sub_4f3cb0()",
			"return sub_4f3570(sub_4c7ee0(1))",
		),
	)

	set_hash_block = _extract_function_block(cl_cgame, "static qboolean QLWebView_SetLocationHash( const char *hash ) {")
	hide_block = _extract_function_block(cl_cgame, "static void QLWebHost_HideBrowser( void ) {")
	open_relative_block = _extract_function_block(cl_cgame, "static qboolean QLWebHost_OpenRelativeURL( const char *hash ) {")
	navigate_block = _extract_function_block(cl_cgame, "static qboolean QLWebHost_NavigateOrOpen( const char *hash ) {")
	reload_view_block = _extract_function_block(cl_cgame, "static void QLWebHost_ReloadView( qboolean ignoreCache ) {")
	show_error_block = _extract_function_block(cl_cgame, "void CL_Web_ShowError_f( void ) {")
	clear_cache_block = _extract_function_block(cl_cgame, "void CL_Web_ClearCache_f( void ) {")
	reload_block = _extract_function_block(cl_cgame, "void CL_Web_Reload_f( void ) {")
	shutdown_block = _extract_function_block(cl_cgame, "void CL_WebHost_Shutdown( void ) {")

	_assert_ordered_anchors(
		set_hash_block,
		(
			"CL_WebHost_NormalizeHash( hash, cl_webHost.pendingHash, sizeof( cl_webHost.pendingHash ) );",
			"CL_WebHost_BuildCurrentURL( cl_webHost.pendingHash, cl_webHost.currentUrl, sizeof( cl_webHost.currentUrl ) );",
			"CL_WebHost_JsonEscape( cl_webHost.pendingHash, escapedHash, sizeof( escapedHash ) );",
			"window.location.hash.replace(/^#/,\\\"\\\")!==h",
			'CL_Awesomium_ExecuteJavascript( script, "" )',
			"return qtrue;",
		),
	)
	_assert_ordered_anchors(
		hide_block,
		(
			"if ( !cl_webHost.coreInitialised || !cl_webHost.viewInitialised || cl_webHost.keyCaptureArmed ) {",
			"CL_Awesomium_PauseRendering();",
			"CL_Awesomium_Unfocus();",
			"cl_webBrowserVisible = qfalse;",
			"cl_webHost.browserVisible = qfalse;",
			"cl_webHost.browserActive = qfalse;",
			"Cvar_Set( \"web_browserActive\", \"0\" );",
			"cls.keyCatchers &= ~KEYCATCH_BROWSER;",
			"CL_WebHost_ClearCursorOverride();",
			"VM_Call( cgvm, CG_EVENT_HANDLING, CGAME_EVENT_CLOSECOMMANDOVERLAY );",
			"QLViewHandler_OnChangeTooltip( \"\" );",
		),
	)
	_assert_ordered_anchors(
		open_relative_block,
		(
			"CL_WebHost_NormalizeHash( hash, cl_webHost.pendingHash, sizeof( cl_webHost.pendingHash ) );",
			"CL_WebHost_BuildCurrentURL( hash, url, sizeof( url ) );",
			"return QLWebHost_OpenURL( url );",
		),
	)
	_assert_ordered_anchors(
		navigate_block,
		(
			"CL_WebHost_NormalizeHash( hash, normalizedHash, sizeof( normalizedHash ) );",
			"CL_WebHost_BuildCurrentURL( normalizedHash, expectedUrl, sizeof( expectedUrl ) );",
			"if ( cl_webHost.viewInitialised && !Q_stricmp( cl_webHost.currentUrl, expectedUrl ) ) {",
			"if ( cl_webHost.viewInitialised && cl_webHost.documentReady && cl_webHost.windowObjectBound ) {",
			"if ( !QLWebView_SetLocationHash( normalizedHash ) ) {",
			"CL_Awesomium_SetZoom( cl_webHost.zoomPercent );",
			"if ( !QLWebView_SetLocationHash( normalizedHash ) ) {",
			"return QLWebHost_OpenRelativeURL( normalizedHash );",
		),
	)
	_assert_ordered_anchors(
		reload_view_block,
		(
			"if ( !cl_webHost.viewInitialised ) {",
			"cl_webHost.refreshStopped = qfalse;",
			"QLLoadHandler_OnBeginLoadingFrame();",
			"CL_Awesomium_Reload( ignoreCache );",
			"cl_webHost.configSynced = qfalse;",
			"cl_webHost.mapCatalogSynced = qfalse;",
			"cl_webHost.factoryCatalogSynced = qfalse;",
			"cl_webHost.surfaceDirty = qtrue;",
			"QLLoadHandler_OnBeginLoadingFrame();",
			"CL_WebHost_PrimeLauncherDocument( cl_webHost.currentUrl )",
		),
	)
	_assert_ordered_anchors(
		show_error_block,
		(
			"const char *message = ( Cmd_Argc() > 1 ) ? Cmd_ArgsFrom( 1 ) : \"\";",
			"Cvar_Set( \"com_errorMessage\", message );",
			"CL_WebView_PublishGameError( message );",
		),
	)
	_assert_ordered_anchors(
		clear_cache_block,
		(
			"if ( !cl_webHost.sessionInitialised ) {",
			"CL_Web_ClearSessionState();",
		),
	)
	_assert_ordered_anchors(
		reload_block,
		(
			"if ( !cl_webHost.viewInitialised ) {",
			"CL_Web_ClearSessionState();",
			"QLWebHost_ReloadView( qtrue );",
		),
	)
	_assert_ordered_anchors(
		shutdown_block,
		(
			"QLWebHost_HideBrowser();",
			"CL_Web_ClearSessionState();",
			"CL_WebHost_ResetRuntime( qtrue );",
			"CL_ResetBrowserOverlayState();",
		),
	)


def test_awesomium_open_url_bootstrap_construction_retail_hlil_flow_is_pinned() -> None:
	rows = _function_rows()
	aliases = _aliases()
	hlil_part05 = _read_text(QL_STEAM_HLIL_PART05_PATH)
	hlil_part06 = _read_text(QL_STEAM_HLIL_PART06_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_awesomium = _read_text(CL_AWESOMIUM_WIN32_PATH)

	for address, owner, size in (
		(0x004F2D30, "QLWebHost_OpenURL", 1024),
		(0x004F3130, "AwesomiumDataPakSource_Destroy", 34),
	):
		assert aliases[f"FUN_{address:08x}"] == owner
		assert aliases[f"sub_{address:06X}"] == owner
		assert aliases[f"sub_{address:06x}"] == owner
		assert rows[address]["name"] == f"FUN_{address:08x}"
		assert int(rows[address]["size"]) == size

	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f2d30    HCURSOR sub_4f2d30(uint32_t arg1)",
			"Awesomium::WebConfig::WebConfig(this: ecx)",
			"if (*(data_12d3064 + 0x30) != 0)",
			"int32_t var_24_1 = 0xa6aa",
			"Awesomium::WebCore::Initialize(&var_3c)",
			"data_12d304c = eax",
			'sub_4c9b60(eax, "Unable to initialize WebCore")',
			"Awesomium::WebConfig::~WebConfig(this: ecx_2)",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"label_4f3034:",
			"sub_4314d0(&var_c, arg1)",
			"Awesomium::WebURL::WebURL(",
			"(*(*data_12d3050 + 0x64))(&var_8)",
			"if (data_12d3069 != 0)",
			"(*(*ecx_3 + 0x78))(0)",
			"data_12d3069 = 0",
			"(*(*ecx_3 + 0xac))()",
			"(*(*data_12d3050 + 0xb0))()",
			"sub_4f25f0((*(*data_12d3050 + 0xc4))(*(data_12d3060 + 0x30)))",
			"data_15ee390 = 1",
			'sub_4cd250("web_browserActive", U"1")',
			"data_1528ba4.d ^= 0x20",
			"SetCursor(hCursor)",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"Awesomium::WebPreferences::WebPreferences(this: ecx_3)",
			'sub_4314d0(&var_8, sub_4ccda0("fs_homepath"))',
			"data_12d3044 = eax_6",
			"(*(*data_12d3044 + 0x18))()",
			"operator new(0x10)",
			"Awesomium::DataPakSource::DataPakSource(this: esi_2,",
			'sub_4314d0(&var_8, "web.pak")',
			"*esi_2 = &Awesomium::DataPakSource::`vftable'{for `Awesomium::DataSource'}",
			"(*(edi_2 + 0x10))(eax_10, esi_2)",
			"operator new(0x40)",
			"eax_12 = sub_464300(eax_11)",
			'sub_4314d0(&var_c, "steam")',
			"(*(esi_3 + 0x10))(eax_13, eax_12)",
			"QLResourceInterceptor::`vftable'{for `Awesomium::ResourceInterceptor'}",
			"(*(*data_12d304c + 0x10))(eax_15)",
			"data_12d3050 =",
			"(*(*data_12d304c + 4))(data_1743bcc, data_1743bd0, data_12d3044, 0)",
			"QLJSHandler::`vftable'{for `Awesomium::JSMethodHandler'}",
			"(*(*data_12d3050 + 0x12c))(eax_19)",
			"if (edi_4 s>= 0xa)",
			"i_1 = sub_431a10()",
			"sub_4ed7e0(0x64)",
			"QLDialogHandler::`vftable'{for `Awesomium::WebViewListener::Dialog'}",
			"(*(*data_12d3050 + 0x34))(eax_22)",
			"QLViewHandler::`vftable'{for `Awesomium::WebViewListener::View'}",
			"(*(*data_12d3050 + 0x24))(eax_24)",
			"QLLoadHandler::`vftable'{for `Awesomium::WebViewListener::Load'}",
			"(*(*data_12d3050 + 0x28))(eax_26)",
			"Awesomium::WebPreferences::~WebPreferences(this: (*(*data_12d3050 + 0xa0))(1))",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f3130    Awesomium::DataPakSource* __thiscall sub_4f3130(Awesomium::DataPakSource* arg1, char arg2)",
			"Awesomium::DataPakSource::~DataPakSource(this: arg1)",
			"operator delete(arg1)",
		),
	)
	_assert_ordered_anchors(
		hlil_part06,
		(
			"00548068  data_548068:",
			"00548070  struct Awesomium::DataSource::Awesomium::DataPakSource::VTable Awesomium::DataPakSource::`vftable'{for `Awesomium::DataSource'} =",
			"vFunc_0)(Awesomium::DataPakSource* arg1, char arg2) = sub_4f3130",
			"OnRequest)(Awesomium::DataPakSource* this, int32_t arg2",
			'00548078  char const data_548078[0x8] = "web.pak", 0',
		),
	)

	ensure_runtime_block = _extract_function_block(
		cl_cgame, "static qboolean QLWebHost_EnsureRuntime( void ) {"
	)
	open_url_block = _extract_function_block(
		cl_cgame, "static qboolean QLWebHost_OpenURL( const char *url ) {"
	)
	prepare_config_block = _extract_function_block(
		cl_awesomium,
		"static qboolean CL_Awesomium_PrepareConfig( const char *runtimePath, const char *basePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh, const char *initialConfigJson, const char *initialMapJson, const char *initialFactoryJson ) {",
	)
	create_session_block = _extract_function_block(
		cl_awesomium, "static qboolean CL_Awesomium_CreateSession( const char *runtimePath, const char *basePath ) {"
	)
	startup_block = _extract_function_block(
		cl_awesomium,
		'extern "C" qboolean CL_Awesomium_Startup( const char *runtimePath, const char *basePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh, int width, int height, const char *initialConfigJson, const char *initialMapJson, const char *initialFactoryJson ) {',
	)
	adapter_open_url_block = _extract_function_block(
		cl_awesomium, 'extern "C" qboolean CL_Awesomium_OpenURL( const char *url ) {'
	)
	shutdown_block = _extract_function_block(
		cl_awesomium, 'extern "C" void CL_Awesomium_Shutdown( void ) {'
	)

	_assert_ordered_anchors(
		ensure_runtime_block,
		(
			'Cvar_VariableStringBuffer( "fs_homepath", homePath, sizeof( homePath ) );',
			'Cvar_VariableStringBuffer( "fs_basepath", basePath, sizeof( basePath ) );',
			"CL_WebHost_RefreshBootstrapProperties();",
			"CL_WebHost_BuildConfigJson( initialConfigJson, CL_WEB_NATIVE_CONFIG_BUFFER_SIZE );",
			"CL_WebHost_BuildMapListJson( initialMapJson, CL_WEB_MAP_JSON_BUFFER_SIZE );",
			"CL_WebHost_BuildFactoryListJson( initialFactoryJson, CL_WEB_FACTORY_JSON_BUFFER_SIZE );",
			"CL_Awesomium_Startup( homePath, basePath, cl_webHost.playerName, cl_webHost.appId, cl_webHost.steamIdLow, cl_webHost.steamIdHigh, cls.glconfig.vidWidth, cls.glconfig.vidHeight, initialConfigJson, initialMapJson, initialFactoryJson )",
			"cl_webHost.liveAwesomium = qtrue;",
			"cl_webHost.coreInitialised = qtrue;",
			"cl_webHost.sessionInitialised = qtrue;",
			"cl_webHost.viewInitialised = qtrue;",
			"cl_webHost.bootstrapReady = qtrue;",
			"cl_webHost.dataPakSourceInstalled = qtrue;",
			"cl_webHost.steamDataSourceInstalled = qfalse;",
			"cl_webHost.resourceInterceptorInstalled = qfalse;",
			"cl_webHost.jsMethodHandlerInstalled = qfalse;",
			"cl_webHost.dialogHandlerInstalled = qfalse;",
			"cl_webHost.viewHandlerInstalled = qfalse;",
			"cl_webHost.loadHandlerInstalled = qfalse;",
			"cl_webHost.windowObjectBound = qtrue;",
			"cl_webHost.qzInstanceBound = qtrue;",
			"cl_webHost.configSynced = qtrue;",
			"QLWebView_Resize( cls.glconfig.vidWidth, cls.glconfig.vidHeight );",
			"QLWebView_RebuildSurfaceImage();",
			"CL_RefreshOnlineServicesBridgeState();",
			"return qtrue;",
		),
	)
	_assert_ordered_anchors(
		ensure_runtime_block,
		(
			"cl_webHost.coreInitialised = qtrue;",
			"cl_webHost.sessionInitialised = qtrue;",
			"QLWebHost_RegisterRuntimeSources();",
			"cl_webHost.viewInitialised = qtrue;",
			"cl_webHost.jsMethodHandlerInstalled = qtrue;",
			"if ( !QLWebHost_WaitForBootstrapReady() ) {",
			"CL_WebHost_ResetRuntime( qfalse );",
			"QLWebHost_InstallRuntimeListeners();",
			"QLWebView_Resize( cls.glconfig.vidWidth, cls.glconfig.vidHeight );",
			"QLWebView_RebuildSurfaceImage();",
		),
	)
	_assert_ordered_anchors(
		open_url_block,
		(
			"if ( !QLWebHost_EnsureRuntime() ) {",
			"CL_WebHost_RefreshBootstrapProperties();",
			"Q_strncpyz( cl_webHost.currentUrl, url ? url : CL_WEB_DEFAULT_URL, sizeof( cl_webHost.currentUrl ) );",
			"cl_webHost.browserVisible = qtrue;",
			"cl_webHost.browserActive = qfalse;",
			"cl_webHost.refreshStopped = qfalse;",
			"cl_webHost.focused = qtrue;",
			"cl_webHost.configSynced = qfalse;",
			'Cvar_Set( "web_browserActive", "1" );',
			"if ( cl_webHost.liveAwesomium ) {",
			"if ( !CL_Awesomium_OpenURL( cl_webHost.currentUrl ) ) {",
			"QLLoadHandler_OnFailLoadingFrame( cl_webHost.currentUrl );",
			"cl_webHost.browserActive = qfalse;",
			"return qfalse;",
			"cl_webHost.zoomPercent = CL_WebZoomIntegerValue();",
			"CL_Awesomium_SetZoom( cl_webHost.zoomPercent );",
			"CL_WebZoomClearModified();",
			"QLLoadHandler_OnBeginLoadingFrame();",
			"QLWebView_RebuildSurfaceImage();",
			"cl_webHost.browserActive = qtrue;",
			"return qtrue;",
			"QLLoadHandler_OnBeginLoadingFrame();",
			"if ( CL_WebHost_PrimeLauncherDocument( cl_webHost.currentUrl ) ) {",
			"QLLoadHandler_OnFinishLoadingFrame();",
			"QLLoadHandler_OnDocumentReady();",
			"QLLoadHandler_OnFailLoadingFrame( cl_webHost.currentUrl );",
			"cl_webHost.browserActive = qtrue;",
			"return qtrue;",
		),
	)
	_assert_ordered_anchors(
		prepare_config_block,
		(
			'"--no-sandbox"',
			"cl_awesomium.webConfig = cl_awe.newWebConfig();",
			'CL_Awesomium_AppendPath( logPath, sizeof( logPath ), sessionPath, "awesomium.log" );',
			'CL_Awesomium_AppendPath( packagePath, sizeof( packagePath ), assetsPath, "web.pak" );',
			"CL_Awesomium_BuildUserScript( cl_awesomium.startupScript, sizeof( cl_awesomium.startupScript ), playerName, appId, steamIdLow, steamIdHigh, initialConfigJson, initialMapJson, initialFactoryJson );",
			"CL_Awesomium_BuildRetryScript( cl_awesomium.startupRetryScript, sizeof( cl_awesomium.startupRetryScript ) );",
			"CL_Awesomium_SelectChildProcessPath( childProcessPath, sizeof( childProcessPath ), runtimePath, basePath )",
			'!CL_Awesomium_SetConfigString( cl_awe.webConfigAssetProtocolSet, cl_awesomium.webConfig, "asset" )',
			"!CL_Awesomium_SetConfigStringArrayOptions( cl_awe.webConfigAdditionalOptionsSet, cl_awesomium.webConfig, awesomiumOptions, sizeof( awesomiumOptions ) / sizeof( awesomiumOptions[0] ) )",
			"!CL_Awesomium_SetConfigString( cl_awe.webConfigChildProcessPathSet, cl_awesomium.webConfig, childProcessConfigPath )",
			"!CL_Awesomium_SetConfigString( cl_awe.webConfigLogPathSet, cl_awesomium.webConfig, logPath )",
			"!CL_Awesomium_SetConfigString( cl_awe.webConfigPackagePathSet, cl_awesomium.webConfig, packageRoot )",
			"!CL_Awesomium_SetConfigString( cl_awe.webConfigUserAgentSet, cl_awesomium.webConfig,",
		),
	)
	_assert_ordered_anchors(
		create_session_block,
		(
			"dataPath = CL_Awesomium_AllocWideString( runtimePath );",
			"cl_awesomium.webSession = cl_awe.webCoreCreateWebSession( cl_awesomium.webCore, dataPath, cl_awesomium.webPreferences );",
			"cl_awe.webSessionInitialize( cl_awesomium.webSession );",
			'CL_Awesomium_AppendPath( pakPath, sizeof( pakPath ), assetsPath, "web.pak" );',
			'CL_Awesomium_AppendPath( pakPath, sizeof( pakPath ), basePath, "web.pak" );',
			'pakName = CL_Awesomium_AllocWideString( "web.pak" );',
			"cl_awesomium.dataPakSource = cl_awe.newDataPakSource( pakName );",
			'sourceName = CL_Awesomium_AllocWideString( "QL" );',
			"cl_awe.webSessionAddDataSource( cl_awesomium.webSession, sourceName, cl_awesomium.dataPakSource );",
		),
	)
	_assert_ordered_anchors(
		startup_block,
		(
			"CL_Awesomium_LoadImports( runtimePath, basePath )",
			"CL_Awesomium_PrepareConfig( runtimePath, basePath, playerName, appId, steamIdLow, steamIdHigh, initialConfigJson, initialMapJson, initialFactoryJson )",
			"CL_Awesomium_PreparePreferences()",
			"cl_awesomium.webCore = cl_awe.webCoreInitialize( cl_awesomium.webConfig );",
			"CL_Awesomium_CreateSession( runtimePath, basePath )",
			"cl_awesomium.webView = cl_awe.webCoreCreateWebView( cl_awesomium.webCore, width, height, cl_awesomium.webSession, 0 );",
			"cl_awe.webViewSetTransparent( cl_awesomium.webView, true );",
			"cl_awe.webViewResumeRendering( cl_awesomium.webView );",
			"cl_awe.webViewFocus( cl_awesomium.webView );",
			"cl_awesomium.started = qtrue;",
		),
	)
	_assert_ordered_anchors(
		adapter_open_url_block,
		(
			'url = "asset://ql/index.html";',
			"wideUrl = CL_Awesomium_AllocWideString( url );",
			"webURL = cl_awe.newWebURL( wideUrl );",
			"cl_awe.webViewLoadURL( cl_awesomium.webView, webURL );",
			"CL_Awesomium_SetZoom( 100 );",
			"cl_awe.webViewResumeRendering( cl_awesomium.webView );",
			"cl_awe.webViewFocus( cl_awesomium.webView );",
			"cl_awe.deleteWebURL( webURL );",
			"cl_awesomium.urlLoaded = qtrue;",
			"cl_awesomium.startupScriptInjectionFrames = CL_AWE_STARTUP_SCRIPT_RETRY_FRAMES;",
		),
	)
	_assert_ordered_anchors(
		shutdown_block,
		(
			"cl_awe.webViewDestroy( cl_awesomium.webView );",
			"cl_awe.webSessionRelease( cl_awesomium.webSession );",
			"cl_awesomium.dataPakSource = NULL;",
			"cl_awe.webCoreShutdown();",
			"cl_awe.deleteWebPreferences( cl_awesomium.webPreferences );",
			"cl_awe.deleteWebConfig( cl_awesomium.webConfig );",
			"cl_awesomium.started = qfalse;",
			"cl_awesomium.urlLoaded = qfalse;",
		),
	)
	assert 'CL_AWE_IMPORT( deleteDataPakSource, "_Awe_delete_DataPakSource@4" );' in cl_awesomium
	assert "cl_awe.deleteDataPakSource( cl_awesomium.dataPakSource );" not in shutdown_block


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
	assert "cl_webHost.liveSurfaceMissingFrames++;" in live_failure_block
	assert 'Com_Printf( "Awesomium WebCore surface failed after %d frames' in live_failure_block
	assert "CL_WebHost_ResetRuntime( qtrue );" in live_failure_block
	assert "cl_webHost.loadFailed = qtrue;" in live_failure_block
	assert "CL_ResetBrowserOverlayState();" in live_failure_block
	assert "CL_RefreshOnlineServicesBridgeState();" in live_failure_block
	assert "return cl_webHost.viewInitialised && cl_webHost.bootstrapReady;" in live_view_block
	assert "CL_WebHost_CheckLiveAwesomiumSurfaceFailure();" in frame_block
	assert frame_block.find("QLWebHost_PumpFrame();") < frame_block.find("CL_WebHost_CheckLiveAwesomiumSurfaceFailure();")
	assert frame_block.find("CL_WebHost_CheckLiveAwesomiumSurfaceFailure();") < frame_block.find("CL_WebHost_UpdateOverlayOwnership();")


def test_awesomium_surface_pump_and_bitmap_upload_retail_hlil_flow_is_pinned() -> None:
	rows = _function_rows()
	aliases = _aliases()
	hlil_part05 = _read_text(QL_STEAM_HLIL_PART05_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_awesomium = _read_text(CL_AWESOMIUM_WIN32_PATH)

	for address, owner, size in (
		(0x004F2590, "QLWebCore_Update", 46),
		(0x004F25C0, "QLWebView_Resize", 35),
		(0x004F25F0, "QLWebView_RebuildSurfaceImage", 345),
		(0x004F2B40, "QLWebHost_PumpFrame", 487),
	):
		assert aliases[f"FUN_{address:08x}"] == owner
		assert aliases[f"sub_{address:06X}"] == owner
		assert aliases[f"sub_{address:06x}"] == owner
		assert rows[address]["name"] == f"FUN_{address:08x}"
		assert int(rows[address]["size"]) == size

	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f2590    void sub_4f2590()",
			"int32_t* ecx = data_12d304c",
			"if (data_15ee390 != 0 && (data_1528ba4 & 0x20) == 0)",
			"jump(*(*ecx + 0x18))",
			"004f25c0    void sub_4f25c0()",
			"int32_t* ecx = data_12d3050",
			"(*(*ecx + 0x9c))(data_1743bcc, data_1743bd0)",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f25f0    void __fastcall sub_4f25f0(int32_t arg1)",
			"(*(*ecx + 0x84))()",
			"data_12d3058 = eax",
			"int32_t ebx_1 = *(eax + 0xc)",
			"int32_t esi_1 = *(eax + 8)",
			"1 << (sub_4d8280(esi_1) + 1)",
			"1 << (sub_4d8280(ebx_1) + 1)",
			"int32_t var_18_3 = ebx_1 * esi_1 * 4",
			"void* eax_8 = sub_525ed8()",
			"Awesomium::BitmapSurface::CopyTo(this: data_12d3058, eax_8, esi_1 << 2, 4, true,",
			'char const* const eax_9 = "browser"',
			'void* eax_13 = sub_445910("browser", eax_8, esi_1, ebx_1, 0, nullptr, 0x2900)',
			"data_12d305c = eax_13",
			"data_12d3040 = eax_14",
			"*(*(eax_14 + 0x180) + 4) = data_12d305c",
			"operator delete[](eax_8)",
			"data_16e3fb4(1, &var_8)",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f2b40    void __fastcall sub_4f2b40(int32_t arg1)",
			"int32_t* ecx = data_12d3050",
			"if (ecx != 0 && data_15ee390 != 0)",
			"if (*(eax_1 + 0x20) != 0)",
			"(*(*ecx + 0xc4))(*(eax_1 + 0x30))",
			"*(data_12d3060 + 0x20) = 0",
			"data_15ee370, arg1)",
			"if (eax_4 == 0 || data_12d3070 != *(eax_4 + 8) || ecx != *(eax_4 + 0xc))",
			"sub_4f25f0(ecx)",
			"if (*(eax_4 + 0x14) != 0)",
			"sub_435730(data_12d305c, 0xde1)",
			"data_16e3d20(0xde1, 0, 0, 0, *(eax_5 + 8), *(eax_5 + 0xc), 0x80e1, 0x1401,",
			"Awesomium::BitmapSurface::set_is_dirty(this: data_12d3058, false)",
			"data_15ee380, arg1)",
			"data_12d3070 = *(eax_8 + 8)",
			"data_12d3074 = *(eax_8 + 0xc)",
			"if (data_12d3068 != 0)",
			"data_15ee384, edx_8)",
		),
	)

	rebuild_surface_block = _extract_function_block(
		cl_cgame, "static void QLWebView_RebuildSurfaceImage( void ) {"
	)
	write_surface_block = _extract_function_block(
		cl_cgame, "static qboolean QLWebView_WriteSurfacePixels( void ) {"
	)
	upload_surface_block = _extract_function_block(
		cl_cgame, "static qboolean QLWebView_UploadSurfaceImage( void ) {"
	)
	pump_block = _extract_function_block(
		cl_cgame, "static void QLWebHost_PumpFrame( void ) {"
	)
	frame_block = _extract_function_block(
		cl_cgame, "void CL_WebHost_Frame( void ) {"
	)
	copy_surface_block = _extract_function_block(
		cl_awesomium, 'extern "C" qboolean CL_Awesomium_CopySurface( byte *destination, int width, int height, int rowSpan ) {'
	)
	surface_dirty_block = _extract_function_block(
		cl_awesomium, 'extern "C" qboolean CL_Awesomium_SurfaceDirty( void ) {'
	)

	_assert_ordered_anchors(
		rebuild_surface_block,
		(
			"contentWidth = cl_webHost.viewWidth;",
			"contentHeight = cl_webHost.viewHeight;",
			"CL_Awesomium_Resize( cl_webHost.viewWidth, cl_webHost.viewHeight );",
			"CL_Awesomium_Update();",
			"awesomiumWidth = CL_Awesomium_SurfaceWidth();",
			"awesomiumHeight = CL_Awesomium_SurfaceHeight();",
			"cl_webHost.surfaceContentWidth = contentWidth;",
			"cl_webHost.surfaceContentHeight = contentHeight;",
			"cl_webHost.surfaceWidth = QLWebView_NextPowerOfTwo( contentWidth );",
			"cl_webHost.surfaceHeight = QLWebView_NextPowerOfTwo( contentHeight );",
			"cl_webHost.surfaceDirty = qtrue;",
			"QLWebView_UploadSurfaceImage();",
		),
	)
	_assert_ordered_anchors(
		write_surface_block,
		(
			"dirty = CL_Awesomium_SurfaceDirty();",
			"copied = CL_Awesomium_CopySurface( cl_webHost.surfaceBuffer, cl_webHost.surfaceWidth, cl_webHost.surfaceHeight, cl_webHost.surfaceWidth * 4 );",
			"QLWebView_MakeAwesomiumSurfaceOpaque(",
			"visible = copied && QLWebView_SurfaceHasVisiblePixels( cl_webHost.surfaceBuffer, requiredLength );",
			"contentful = visible && QLWebView_SurfaceHasUiContent(",
			"cl_webHost.surfaceHasVisiblePixels = visible;",
			"cl_webHost.surfaceHasUiContent = contentful;",
			"cl_webHost.liveSurfaceMissingFrames = 0;",
		),
	)
	_assert_ordered_anchors(
		upload_surface_block,
		(
			"QLWebView_WriteSurfacePixels()",
			"cl_webHost.surfaceShader = CL_RegisterShaderFromRGBAWithImageName(",
			"cl_webHost.surfaceUploadWidth = cl_webHost.surfaceWidth;",
			"cl_webHost.surfaceUploadHeight = cl_webHost.surfaceHeight;",
			"cl_webHost.surfaceImageInitialised = qtrue;",
			"cl_webHost.surfaceDirty = qfalse;",
		),
	)
	_assert_ordered_anchors(
		pump_block,
		(
			"if ( cl_webHost.viewWidth != cls.glconfig.vidWidth || cl_webHost.viewHeight != cls.glconfig.vidHeight ) {",
			"QLWebView_Resize( cls.glconfig.vidWidth, cls.glconfig.vidHeight );",
			"QLWebView_RebuildSurfaceImage();",
			"awesomiumWidth = CL_Awesomium_SurfaceWidth();",
			"awesomiumHeight = CL_Awesomium_SurfaceHeight();",
			"QLWebView_RebuildSurfaceImage();",
			"if ( !cl_webHost.surfaceImageInitialised ) {",
			"QLWebView_RebuildSurfaceImage();",
			"if ( cl_webHost.surfaceUploadWidth != cl_webHost.surfaceWidth || cl_webHost.surfaceUploadHeight != cl_webHost.surfaceHeight ) {",
			"QLWebView_RebuildSurfaceImage();",
			"if ( cl_webHost.surfaceDirty ) {",
			"QLWebView_UploadSurfaceImage();",
		),
	)
	_assert_ordered_anchors(
		copy_surface_block,
		(
			"surface = CL_Awesomium_Surface();",
			"cl_awe.bitmapCopyTo( surface, destination, rowSpan, 4, true, false );",
			"cl_awe.bitmapSetIsDirty( surface, false );",
			"source = cl_awe.bitmapBuffer ? cl_awe.bitmapBuffer( surface ) : NULL;",
			"sourceRowSpan = cl_awe.bitmapRowSpan ? cl_awe.bitmapRowSpan( surface ) : 0;",
			"dst[x + 0] = src[x + 2];",
			"dst[x + 1] = src[x + 1];",
			"dst[x + 2] = src[x + 0];",
			"dst[x + 3] = src[x + 3];",
			"cl_awe.bitmapSetIsDirty( surface, false );",
		),
	)
	assert "cl_awe.bitmapIsDirty( surface )" in surface_dirty_block
	assert frame_block.index("QLWebCore_Update();") < frame_block.index("QLWebHost_PumpFrame();")
	assert frame_block.index("QLWebHost_PumpFrame();") < frame_block.index("CL_WebHost_CheckLiveAwesomiumSurfaceFailure();")


def test_awesomium_event_publication_and_command_registration_retail_hlil_flow_is_pinned() -> None:
	rows = _function_rows()
	aliases = _aliases()
	hlil_part05 = _read_text(QL_STEAM_HLIL_PART05_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_main = _read_text(CL_MAIN_PATH)

	for address, owner, size in (
		(0x004F3260, "QLWebView_PublishEvent", 448),
		(0x004F3420, "QLWebView_PublishGameKey", 332),
		(0x004F3570, "QLWebView_PublishGameError", 138),
		(0x004F3600, "QLWebView_PublishGameEnd", 40),
		(0x004F3630, "QLWebView_PublishCvarChange", 391),
		(0x004F37C0, "QLWebView_PublishBindChanged", 300),
		(0x004F38F0, "QLWebView_PublishGameStart", 667),
		(0x004F3B90, "QLWebView_PublishGameDemo", 134),
		(0x004F3C20, "QLWebView_PublishGameScreenshot", 134),
		(0x004F3CD0, "QLWebHost_RegisterCommands", 158),
	):
		assert aliases[f"FUN_{address:08x}"] == owner
		assert aliases[f"sub_{address:06X}"] == owner
		assert aliases[f"sub_{address:06x}"] == owner
		assert rows[address]["name"] == f"FUN_{address:08x}"
		assert int(rows[address]["size"]) == size

	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f3260    bool sub_4f3260(class Awesomium::JSArray* arg1 @ esi, class Awesomium::WebString* arg2 @ edi, uint32_t arg3, int32_t* arg4)",
			"if (data_12d3050 == 0)",
			'"PublishEvent failed: no view\\n"',
			"Awesomium::JSValue::IsUndefined(this: &data_12d3078)",
			"Awesomium::JSArray::JSArray(this: ecx_1)",
			"sub_4314d0(&var_28, arg3)",
			"Awesomium::JSArray::Push(this: ecx_3, eax_4)",
			"if (esi != 0)",
			"sub_42a850(esi, &var_24)",
			"Awesomium::JSArray::Push(this: ecx_8, eax_7)",
			'sub_4314d0(&var_28, "EnginePublish")',
			"Awesomium::JSObject::InvokeAsync(",
			'sub_4314d0(&var_2c, "window")',
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f3420    void sub_4f3420(class Awesomium::JSArray* arg1, void* arg2)",
			"if (arg2 == 0 && data_12d306c == 1)",
			"data_12d306c = arg2",
			'sub_4296c0(sub_42a110(&var_14, "id"), &var_24)',
			'sub_4296c0(sub_42a110(&var_14, "key"), &var_24)',
			'sub_4f3260(arg1, edi, sub_4d9220("game.key"), &var_14)',
			"if (arg1 == 0xb2 || arg1 == 0xb3 || arg1 == 0xb4)",
			"sub_4f27c0(arg1)",
			"sub_4f2820(arg1)",
			"sub_4f2870(0xffffffff)",
			"sub_4f2870(1)",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f3570    void sub_4f3570(int32_t arg1)",
			"data_12d3050 != 0",
			"Awesomium::JSValue::IsUndefined(this: &data_12d3078)",
			"data_12d3069 == eax",
			"sub_4f2d30(&data_54f9da)",
			'sub_4cd250("com_errorMessage", &data_54f9da)',
			'sub_429440(sub_42a110(&var_14, "text"), arg1)',
			'sub_4f3260(esi, edi, sub_4d9220("game.error"), &var_14)',
			"004f3600    void sub_4f3600()",
			'Awesomium::JSValue::IsUndefined(this: &data_12d3078) == 0',
			'sub_4f3260(esi, edi, "game.end", nullptr)',
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f3630    void sub_4f3630(class Awesomium::WebString* arg1)",
			"_strdup(eax_1)",
			"var_8 = 1",
			'"vid_xpos"',
			'"vid_ypos"',
			'sub_4296c0(sub_42a110(&var_18, "name"), &var_28)',
			'sub_4296c0(sub_42a110(&var_18, "value"), &var_28)',
			'sub_4296c0(sub_42a110(&var_18, "replicate"), &var_28)',
			'sub_4f3260(esi_1, arg1, sub_4d9220("cvar.%s"), &var_18)',
			"004f37c0    void sub_4f37c0(class Awesomium::JSArray* arg1, uint32_t arg2)",
			"Awesomium::JSArray::JSArray(this: ecx_1)",
			'Awesomium::JSArray::Push(this: ecx_3, eax_2)',
			'Awesomium::JSArray::Push(this: ecx_8, eax_4)',
			'sub_4296c0(sub_42a110(&var_20, "name"), &var_30)',
			'sub_4296c0(sub_42a110(&var_20, "value"), &var_30)',
			'sub_4f3260(arg1, Awesomium::JSValue::JSValue, sub_4d9220("bind.changed"), &var_20)',
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f38f0    int32_t sub_4f38f0(class Awesomium::JSArray* arg1 @ esi, void* arg2)",
			"if (*(result + 0x30) != 0)",
			'sub_4296c0(sub_42a110(&var_30, "ip"), &var_1c)',
			'sub_4296c0(sub_42a110(&var_30, "port"), &var_1c)',
			'(*(*SteamFriends() + 0xac))("lanIp", eax_10)',
			'(*(*SteamFriends() + 0xac))("status", "Playing a match")',
			'sub_4f3260(arg1, edi, "game.start", &var_30)',
			"004f3b90    int32_t sub_4f3b90(class Awesomium::JSArray* arg1)",
			'sub_429440(sub_42a110(&var_58, "id"), &var_48)',
			'sub_429440(sub_42a110(&var_58, "name"), arg1)',
			'sub_4f3260(arg1, edi, "game.demo", &var_58)',
			"004f3c20    int32_t sub_4f3c20(class Awesomium::JSArray* arg1)",
			'sub_429440(sub_42a110(&var_58, "id"), &var_48)',
			'sub_429440(sub_42a110(&var_58, "name"), arg1)',
			'sub_4f3260(arg1, edi, "game.screenshot", &var_58)',
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f3cd0    void** sub_4f3cd0()",
			'sub_4c81d0("web_showBrowser", sub_4f3160)',
			'sub_4c81d0("web_changeHash", sub_4f31d0)',
			'sub_4c81d0("web_hideBrowser", sub_4f24d0)',
			'sub_4c81d0("web_showError", sub_4f3cb0)',
			'sub_4c81d0("web_clearCache", sub_4f2a10)',
			'sub_4c81d0("web_reload", sub_4f2a30)',
			'data_12d3060 = sub_4ce0d0(x87_r0, "web_zoom", "100", 1)',
			'data_12d3064 = sub_4ce0d0(x87_r2, "web_console", U"0", 1)',
			'return sub_4ce0d0(x87_r4, "web_browserActive", U"0", 0x40)',
		),
	)

	dispatch_event_block = _extract_function_block(
		cl_main, "static void CL_WebView_DispatchLiveEvent( const char *name, const char *payload ) {"
	)
	publish_event_block = _extract_function_block(
		cl_main, "void CL_WebView_PublishEvent( const char *name, const char *payload ) {"
	)
	game_key_block = _extract_function_block(cl_cgame, "static void QLWebView_PublishGameKey( int key ) {")
	game_error_block = _extract_function_block(cl_main, "void CL_WebView_PublishGameError( const char *message ) {")
	game_end_block = _extract_function_block(cl_main, "void CL_WebView_PublishGameEnd( void ) {")
	cvar_block = _extract_function_block(
		cl_main, "void CL_WebView_PublishCvarChange( const char *name, const char *value, qboolean replicate ) {"
	)
	bind_block = _extract_function_block(
		cl_main, "void CL_WebView_PublishBindChanged( const char *name, const char *value ) {"
	)
	packed_start_block = _extract_function_block(
		cl_main, "static void CL_WebView_PublishPackedGameStart( uint32_t packedIp, unsigned int port, qboolean publishLanIp ) {"
	)
	game_start_block = _extract_function_block(cl_main, "void CL_WebView_PublishGameStart( void ) {")
	demo_block = _extract_function_block(cl_main, "void CL_WebView_PublishGameDemo( const char *id, const char *name ) {")
	screenshot_block = _extract_function_block(
		cl_main, "void CL_WebView_PublishGameScreenshot( const char *id, const char *name ) {"
	)
	register_block = _extract_function_block(cl_cgame, "void QLWebHost_RegisterCommands( void ) {")

	_assert_ordered_anchors(
		dispatch_event_block,
		(
			"CL_WebHost_HasDrawableSurface()",
			"CL_Steam_JsonEscape( name, escapedName, sizeof( escapedName ) );",
			"JSON.parse(p)",
			"window.EnginePublish",
			'CL_Awesomium_ExecuteJavascript( script, "" );',
		),
	)
	_assert_ordered_anchors(
		publish_event_block,
		(
			"if ( !name || !name[0] ) {",
			"CL_WebHost_HasLiveView()",
			"CL_WebHost_HasBoundWindowObject()",
			"event = &cl_steamCallbackState.events[slot];",
			"event->sequence = cl_steamCallbackState.eventSequence;",
			"Q_strncpyz( event->name, name, sizeof( event->name ) );",
			"Q_strncpyz( event->payload, payload ? payload : \"\", sizeof( event->payload ) );",
			"CL_LogBrowserEventLifecycle( event->name, detail );",
			"CL_WebView_DispatchLiveEvent( event->name, event->payload );",
		),
	)
	_assert_ordered_anchors(
		game_key_block,
		(
			"keyName = Key_KeynumToString( key );",
			'Com_sprintf( payload, sizeof( payload ), "{\\"id\\":%d,\\"key\\":\\"%s\\"}", key, keyName ? keyName : "" );',
			'CL_WebView_PublishEvent( "game.key", payload );',
		),
	)
	_assert_ordered_anchors(
		game_error_block,
		(
			"CL_Steam_JsonEscape( message ? message : \"\", escapedMessage, sizeof( escapedMessage ) );",
			'Com_sprintf( payload, sizeof( payload ), "{\\"text\\":\\"%s\\"}", escapedMessage );',
			'CL_WebView_PublishEvent( "game.error", payload );',
			'Cvar_Set( "com_errorMessage", "" );',
		),
	)
	assert 'CL_WebView_PublishEvent( "game.end", NULL );' in game_end_block
	_assert_ordered_anchors(
		cvar_block,
		(
			'!Q_stricmp( name, "vid_xpos" ) || !Q_stricmp( name, "vid_ypos" )',
			"CL_Steam_JsonEscape( name, escapedName, sizeof( escapedName ) );",
			'Com_sprintf( eventName, sizeof( eventName ), "cvar.%s", name );',
			'Com_sprintf( payload, sizeof( payload ), "{\\"name\\":\\"%s\\",\\"value\\":\\"%s\\",\\"replicate\\":%d}", escapedName, escapedValue, replicate ? 1 : 0 );',
			"CL_WebView_PublishEvent( eventName, payload );",
		),
	)
	_assert_ordered_anchors(
		bind_block,
		(
			"CL_Steam_JsonEscape( name ? name : \"\", escapedName, sizeof( escapedName ) );",
			"CL_Steam_JsonEscape( value ? value : \"\", escapedValue, sizeof( escapedValue ) );",
			'Com_sprintf( payload, sizeof( payload ), "{\\"name\\":\\"%s\\",\\"value\\":\\"%s\\"}", escapedName, escapedValue );',
			'CL_WebView_PublishEvent( "bind.changed", payload );',
		),
	)
	_assert_ordered_anchors(
		packed_start_block,
		(
			"if ( clc.demoplaying ) {",
			'QL_Steamworks_SetRichPresence( "lanIp", lanAddress );',
			"CL_Steam_SetMatchRichPresence();",
			'Com_sprintf( payload, sizeof( payload ), "{\\"ip\\":%u,\\"port\\":%u}", packedIp, port );',
			'CL_WebView_PublishEvent( "game.start", payload );',
		),
	)
	_assert_ordered_anchors(
		game_start_block,
		(
			"serverAddress = clc.serverAddress;",
			"NET_IsLocalAddress( serverAddress )",
			"NET_GetLocalAddressIP( &localAddress )",
			"QL_Steamworks_ServerGetPublicIP();",
			"CL_WebView_PublishGameStartForAddress( &serverAddress );",
		),
	)
	for block, event_name in (
		(demo_block, "game.demo"),
		(screenshot_block, "game.screenshot"),
	):
		assert "CL_Steam_JsonEscape( id ? id : \"\", escapedId, sizeof( escapedId ) );" in block
		assert "CL_Steam_JsonEscape( name ? name : \"\", escapedName, sizeof( escapedName ) );" in block
		assert 'Com_sprintf( payload, sizeof( payload ), "{\\"id\\":\\"%s\\",\\"name\\":\\"%s\\"}", escapedId, escapedName );' in block
		assert f'CL_WebView_PublishEvent( "{event_name}", payload );' in block

	_assert_ordered_anchors(
		register_block,
		(
			'Cmd_AddCommand ("web_showBrowser", CL_Web_ShowBrowser_f );',
			'Cmd_AddCommand ("web_changeHash", CL_Web_ChangeHash_f );',
			'Cmd_AddCommand ("web_hideBrowser", CL_Web_HideBrowser_f );',
			'Cmd_AddCommand ("web_showError", CL_Web_ShowError_f );',
			'Cmd_AddCommand ("web_clearCache", CL_Web_ClearCache_f );',
			'Cmd_AddCommand ("web_reload", CL_Web_Reload_f );',
			'cl_webZoom = Cvar_Get ("web_zoom", "100", CVAR_ARCHIVE );',
			'cl_webConsole = Cvar_Get ("web_console", "0", CVAR_ARCHIVE );',
			'cl_webBrowserActive = Cvar_Get ("web_browserActive", "0", CVAR_ROM );',
		),
	)


def test_awesomium_stop_refresh_is_explicit_non_retail_ui_bridge_compatibility() -> None:
	rows = _function_rows()
	aliases = _aliases()
	hlil_part05 = _read_text(QL_STEAM_HLIL_PART05_PATH)
	hlil_part06 = _read_text(QL_STEAM_HLIL_PART06_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_awesomium = _read_text(CL_AWESOMIUM_WIN32_PATH)
	ui_main = _read_text(REPO_ROOT / "src" / "code" / "ui" / "ui_main.c")
	main_menu = _read_text(REPO_ROOT / "src" / "ui" / "main.menu")
	mapping_round = _read_text(
		REPO_ROOT
		/ "docs"
		/ "reverse-engineering"
		/ "awesomium-stoprefresh-compatibility-boundary-2026-06-11.md"
	)

	register_row = rows[0x004F3CD0]
	assert aliases["FUN_004f3cd0"] == "QLWebHost_RegisterCommands"
	assert aliases["sub_4F3CD0"] == "QLWebHost_RegisterCommands"
	assert aliases["sub_4f3cd0"] == "QLWebHost_RegisterCommands"
	assert register_row["name"] == "FUN_004f3cd0"
	assert int(register_row["size"]) == 158

	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f3cd0    void** sub_4f3cd0()",
			'sub_4c81d0("web_showBrowser", sub_4f3160)',
			'sub_4c81d0("web_changeHash", sub_4f31d0)',
			'sub_4c81d0("web_hideBrowser", sub_4f24d0)',
			'sub_4c81d0("web_showError", sub_4f3cb0)',
			'sub_4c81d0("web_clearCache", sub_4f2a10)',
			'sub_4c81d0("web_reload", sub_4f2a30)',
			'data_12d3060 = sub_4ce0d0(x87_r0, "web_zoom", "100", 1)',
			'data_12d3064 = sub_4ce0d0(x87_r2, "web_console", U"0", 1)',
			'return sub_4ce0d0(x87_r4, "web_browserActive", U"0", 0x40)',
		),
	)
	assert "web_stopRefresh" not in hlil_part05
	assert "web_stopRefresh" not in hlil_part06

	register_block = _extract_function_block(cl_cgame, "void QLWebHost_RegisterCommands( void ) {")
	stop_refresh_block = _extract_function_block(cl_cgame, "void CL_Web_StopRefresh_f( void ) {")
	update_block = _extract_function_block(cl_cgame, "static void QLWebCore_Update( void ) {")
	ui_stop_block = _extract_function_block(ui_main, "static void UI_RunMenuScript(char **args) {")

	_assert_ordered_anchors(
		register_block,
		(
			'Cmd_AddCommand ("web_showBrowser", CL_Web_ShowBrowser_f );',
			'Cmd_AddCommand ("web_changeHash", CL_Web_ChangeHash_f );',
			'Cmd_AddCommand ("web_hideBrowser", CL_Web_HideBrowser_f );',
			'Cmd_AddCommand ("web_showError", CL_Web_ShowError_f );',
			'Cmd_AddCommand ("web_clearCache", CL_Web_ClearCache_f );',
			'Cmd_AddCommand ("web_reload", CL_Web_Reload_f );',
			'Cmd_AddCommand ("web_stopRefresh", CL_Web_StopRefresh_f );',
		),
	)
	_assert_ordered_anchors(
		stop_refresh_block,
		(
			'CL_LogOverlayServiceIgnored( "web_stopRefresh", "online services disabled by build settings" );',
			"CL_RefreshOnlineServicesBridgeState();",
			"if ( !CL_BrowserHostServiceAvailable() ) {",
			'CL_LogOverlayServiceIgnored( "web_stopRefresh", "browser overlay provider unavailable" );',
			"if ( cl_webHost.liveAwesomium ) {",
			"cl_webHost.refreshStopped = qfalse;",
			"cl_webHost.surfaceDirty = qtrue;",
			'Com_DPrintf( "web_stopRefresh ignored for live Awesomium WebCore\\n" );',
			"return;",
			"cl_webHost.refreshStopped = qtrue;",
			"cl_webHost.surfaceDirty = qtrue;",
			'Com_DPrintf( "web_stopRefresh\\n" );',
		),
	)
	assert "CL_Awesomium_Stop();" not in stop_refresh_block
	assert 'CL_AWE_IMPORT( webViewStop, "_Awe_WebView_Stop@4" );' in cl_awesomium
	assert 'extern "C" void CL_Awesomium_Stop( void ) {' in cl_awesomium
	assert "CL_Awesomium_Update();" in update_block
	assert "refreshStopped" not in update_block

	assert 'static const char *ui_browserRefreshCommand = "web_stopRefresh\\n";' in ui_main
	_assert_ordered_anchors(
		ui_stop_block,
		(
			'if (Q_stricmp(name, "stopRefresh") == 0) {',
			"UI_StopServerRefresh();",
			"if (UI_BrowserOverlayAvailable() && ui_browserRefreshCommand && *ui_browserRefreshCommand) {",
			"trap_Cmd_ExecuteText(EXEC_NOW, ui_browserRefreshCommand);",
			"} else {",
			'Com_DPrintf("UI: stopRefresh requested without browser overlay; only native refresh stopped.\\n");',
			"return;",
		),
	)
	assert "uiScript stopRefresh ;" in main_menu
	assert "Awesomium StopRefresh Compatibility Boundary" in mapping_round
	assert "Overall Awesomium/WebUI launch/runtime integration mapping confidence: **99.27% -> 99.28%**." in mapping_round


def test_awesomium_lobby_callbacks_publish_through_retail_webui_event_bridge() -> None:
	rows = _function_rows()
	aliases = _aliases()
	hlil_part02 = _read_text(QL_STEAM_HLIL_PART02_PATH)
	hlil_part05 = _read_text(QL_STEAM_HLIL_PART05_PATH)
	cl_main = _read_text(CL_MAIN_PATH)
	mapping_round = _read_text(
		REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_579.md"
	)

	for address, owner, size in (
		(0x004645A0, "SteamLobbyCallbacks_OnLobbyChatMessage", 377),
		(0x00464BF0, "SteamLobbyCallbacks_OnLobbyCreated", 416),
		(0x00464D90, "SteamLobbyCallbacks_OnLobbyEnter", 1350),
		(0x004652E0, "SteamLobbyCallbacks_OnLobbyChatUpdate", 418),
	):
		assert aliases[f"FUN_{address:08x}"] == owner
		assert aliases[f"sub_{address:06X}"] == owner
		assert aliases[f"sub_{address:06x}"] == owner
		assert rows[address]["name"] == f"FUN_{address:08x}"
		assert int(rows[address]["size"]) == size

	_assert_ordered_anchors(
		hlil_part02,
		(
			"004645a0    int32_t __stdcall sub_4645a0(class Awesomium::JSArray* arg1)",
			"*(*SteamMatchmaking(eax_2) + 0x6c)",
			"00464626  if (var_860 == 1)",
			'sub_429440(sub_42a110(&var_870, "id"), &var_54)',
			'sub_429440(sub_42a110(&var_870, "name"), eax_5)',
			'sub_429440(sub_42a110(&var_870, "msg"), &var_854)',
			'sub_4f3260(arg1, eax_5, sub_4d9220("lobby.%s.chat"), &var_870)',
		),
	)
	_assert_ordered_anchors(
		hlil_part02,
		(
			"00464bf0    int32_t __stdcall sub_464bf0(int32_t* arg1)",
			"00464c26  if (eax_3 == 1)",
			'(*(*SteamMatchmaking(eax_2) + 0x50))(edi_1, arg1[3], "hello", "world")',
			'sub_429440(sub_42a110(&var_64, "id"), &var_54)',
			'sub_4296c0(sub_42a110(&var_64, "status"), &var_94)',
			'sub_4f3260(arg1, edi_1, sub_4d9220("lobby.%s.create"), &var_64)',
			'sub_429440(sub_42a110(&var_74, "message"), "Unable to create lobby")',
			'sub_4f3260(arg1, edi, "lobby.error", &var_74)',
		),
	)
	_assert_ordered_anchors(
		hlil_part02,
		(
			"00464d90    int32_t __stdcall sub_464d90(int32_t* arg1)",
			"00464de0  if (eax_4 == 1)",
			"sub_4649e0()",
			'sub_429440(sub_42a110(&var_87c, "id"), &var_54)',
			'sub_4296c0(sub_42a110(&var_87c, "is_owner"), var_8c8_11)',
			'sub_4296c0(sub_42a110(&var_87c, "lobbydata"), &var_8b4)',
			'sub_4296c0(sub_42a110(&var_87c, "num_players"), &var_86c)',
			'sub_4296c0(sub_42a110(&var_87c, "max_players"), &var_86c)',
			'sub_429d00(sub_42a110(&var_87c, "players"))',
			'sub_429440(sub_42a110(&var_8a4, "name"), eax_49)',
			'sub_4f3260(esi_1, edi_1, sub_4d9220("lobby.%s.enter"), &var_87c)',
			'sub_429440(sub_42a110(&var_894, "message"), (&data_55fb30)[arg1[4]])',
			'sub_4f3260(esi, arg1, "lobby.error", &var_894)',
		),
	)
	_assert_ordered_anchors(
		hlil_part02,
		(
			"004652e0    int32_t __stdcall sub_4652e0(class Awesomium::JSArray* arg1)",
			'sub_429440(sub_42a110(&var_64, "id"), eax_4)',
			'sub_429440(sub_42a110(&var_64, "name"), eax_8)',
			'sub_4296c0(sub_42a110(&var_64, "num_players"), &var_74)',
			'sub_4296c0(sub_42a110(&var_64, "max_players"), &var_74)',
			'var_90 = "lobby.%s.user.left"',
			'var_90 = "lobby.%s.user.joined"',
			"sub_4f3260(arg1, SteamMatchmaking, sub_4d9220(var_90), var_88_10)",
		),
	)
	_assert_ordered_anchors(
		hlil_part05,
		(
			"004f3260    bool sub_4f3260(class Awesomium::JSArray* arg1 @ esi, class Awesomium::WebString* arg2 @ edi, uint32_t arg3, int32_t* arg4)",
			'sub_4314d0(&var_28, "EnginePublish")',
			"Awesomium::JSObject::InvokeAsync(",
			'sub_4314d0(&var_2c, "window")',
		),
	)

	steam_publish_block = _extract_function_block(
		cl_main, "static void CL_Steam_PublishBrowserEvent( const char *name, const char *payload ) {"
	)
	publish_event_block = _extract_function_block(
		cl_main, "void CL_WebView_PublishEvent( const char *name, const char *payload ) {"
	)
	lobby_created_block = _extract_function_block(
		cl_main, "static void CL_Steam_Lobby_OnLobbyCreated( void *context, const ql_steam_lobby_created_t *event ) {"
	)
	lobby_enter_block = _extract_function_block(
		cl_main, "static void CL_Steam_Lobby_OnLobbyEnter( void *context, const ql_steam_lobby_enter_t *event ) {"
	)
	lobby_chat_update_block = _extract_function_block(
		cl_main, "static void CL_Steam_Lobby_OnLobbyChatUpdate( void *context, const ql_steam_lobby_chat_update_t *event ) {"
	)
	lobby_chat_message_block = _extract_function_block(
		cl_main, "static void CL_Steam_Lobby_OnLobbyChatMessage( void *context, const ql_steam_lobby_chat_message_t *event ) {"
	)
	lobby_callbacks_init_block = _extract_function_block(
		cl_main, "static qboolean SteamLobbyCallbacks_Init( void ) {"
	)

	assert "CL_WebView_PublishEvent( name, payload );" in steam_publish_block
	_assert_ordered_anchors(
		publish_event_block,
		(
			"Q_strncpyz( event->name, name, sizeof( event->name ) );",
			"Q_strncpyz( event->payload, payload ? payload : \"\", sizeof( event->payload ) );",
			"CL_LogBrowserEventLifecycle( event->name, detail );",
			"CL_WebView_DispatchLiveEvent( event->name, event->payload );",
		),
	)
	_assert_ordered_anchors(
		lobby_created_block,
		(
			"CL_Steam_FormatSteamId( event->lobbyId.value, lobbyId, sizeof( lobbyId ) );",
			'CL_Steam_PublishBrowserEvent( "lobby.error", payload );',
			'QL_Steamworks_SetLobbyData( lobbyIdLow, lobbyIdHigh, "hello", "world" );',
			'Com_sprintf( eventName, sizeof( eventName ), "lobby.%s.create", lobbyId );',
			'Com_sprintf( payload, sizeof( payload ), "{\\"id\\":\\"%s\\",\\"status\\":%d}", lobbyId, event->result );',
			"CL_Steam_PublishBrowserEvent( eventName, payload );",
		),
	)
	_assert_ordered_anchors(
		lobby_enter_block,
		(
			"responseMessage = CL_Steam_GetLobbyEnterResponseMessage( event->response );",
			'CL_Steam_PublishBrowserEvent( "lobby.error", payload );',
			"if ( CL_Steam_GetCurrentLobbyIdentityWords( NULL, NULL ) ) {",
			"CL_Steam_LeaveCurrentLobby();",
			"CL_Steam_SetCurrentLobby( event->lobbyId.value );",
			"CL_Steam_AppendLobbyDataJson( payload, sizeof( payload ), lobbyIdLow, lobbyIdHigh );",
			"QL_Steamworks_GetLobbyMemberByIndex( lobbyIdLow, lobbyIdHigh, i, &memberIdLow, &memberIdHigh )",
			'Com_sprintf( eventName, sizeof( eventName ), "lobby.%s.enter", lobbyId );',
			"CL_Steam_PublishBrowserEvent( eventName, payload );",
		),
	)
	_assert_ordered_anchors(
		lobby_chat_update_block,
		(
			"QL_Steamworks_GetFriendSummary(",
			"numPlayers = QL_Steamworks_GetNumLobbyMembers( lobbyIdLow, lobbyIdHigh );",
			'Com_sprintf( eventName, sizeof( eventName ), "lobby.%s.user.joined", lobbyId );',
			'Com_sprintf( eventName, sizeof( eventName ), "lobby.%s.user.left", lobbyId );',
			'Com_sprintf( payload, sizeof( payload ), "{\\"id\\":\\"%s\\",\\"name\\":\\"%s\\",\\"num_players\\":%d,\\"max_players\\":%d}",',
			"CL_Steam_PublishBrowserEvent( eventName, payload );",
		),
	)
	_assert_ordered_anchors(
		lobby_chat_message_block,
		(
			"if ( event->chatEntryType != 1 ) {",
			"return;",
			"QL_Steamworks_GetFriendSummary(",
			"CL_Steam_JsonEscape( event->message, message, sizeof( message ) );",
			'Com_sprintf( eventName, sizeof( eventName ), "lobby.%s.chat", lobbyId );',
			'Com_sprintf( payload, sizeof( payload ), "{\\"id\\":\\"%s\\",\\"name\\":\\"%s\\",\\"msg\\":\\"%s\\"}", userId, name, message );',
			"CL_Steam_PublishBrowserEvent( eventName, payload );",
		),
	)
	_assert_ordered_anchors(
		lobby_callbacks_init_block,
		(
			"lobbyBindings.onLobbyCreated = CL_Steam_Lobby_OnLobbyCreated;",
			"lobbyBindings.onLobbyEnter = CL_Steam_Lobby_OnLobbyEnter;",
			"lobbyBindings.onLobbyChatUpdate = CL_Steam_Lobby_OnLobbyChatUpdate;",
			"lobbyBindings.onLobbyChatMessage = CL_Steam_Lobby_OnLobbyChatMessage;",
			"return QL_Steamworks_RegisterLobbyCallbacks( &lobbyBindings );",
		),
	)
	assert "Awesomium Lobby Callback Event Publication Crosscheck" in mapping_round
	assert "SteamLobbyCallbacks_OnLobbyChatMessage" in mapping_round
	assert "QLWebView_PublishEvent" in mapping_round
	assert "Overall Awesomium/WebUI launch/runtime integration mapping confidence: **99.22% -> 99.24%**." in mapping_round


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
	assert "CL_WebHost_ExecuteFactoryCatalogBatches( factoryJson, factoryJsonLength )" in cl_cgame
	assert "CL_WebHost_ExecuteFactoryCatalogBatch" in cl_cgame
	assert "window.__qlr_begin_native_maps" in cl_cgame
	assert "window.__qlr_add_native_maps" in cl_cgame
	assert "window.__qlr_commit_native_maps" in cl_cgame
	assert "window.__qlr_begin_native_factories" in cl_cgame
	assert "window.__qlr_add_native_factories" in cl_cgame
	assert "window.__qlr_commit_native_factories" in cl_cgame
	assert "CL_WEB_MAP_SYNC_CHUNK_CHARS" in cl_cgame
	assert "CL_WEB_FACTORY_SYNC_CHUNK_CHARS" in cl_cgame
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
