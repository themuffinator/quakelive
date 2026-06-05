from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(text)):
		if text[index] == "{":
			depth += 1
		elif text[index] == "}":
			depth -= 1
			if depth == 0:
				return text[start : index + 1]

	raise AssertionError(f"closing brace not found for: {signature}")


def test_retail_application_startup_chain_maps_primary_owners() -> None:
	aliases = json.loads(
		(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json").read_text(
			encoding="utf-8"
		)
	)["quakelive_steam"]
	functions_csv = (
		REPO_ROOT / "references/reverse-engineering/ghidra/quakelive_steam/functions.csv"
	).read_text(encoding="utf-8")
	hlil = (
		REPO_ROOT
		/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt"
	).read_text(encoding="utf-8")
	win_main = (REPO_ROOT / "src/code/win32/win_main.c").read_text(encoding="utf-8")
	sv_init = (REPO_ROOT / "src/code/server/sv_init.c").read_text(encoding="utf-8")

	expected_aliases = {
		"sub_4ED830": "WinMain",
		"sub_4CBFD0": "Com_Init",
		"sub_4ED400": "Sys_Init",
		"sub_4EF320": "NET_Init",
		"sub_4BC690": "CL_Init",
		"sub_4E3AD0": "SV_Init",
		"sub_4EC580": "Sys_WinkeyHookProc",
		"sub_4F4140": "Zmq_RegisterCvarsAndInitRcon",
	}
	for raw_name, reconstructed_name in expected_aliases.items():
		assert aliases[raw_name] == reconstructed_name

	for row in [
		"FUN_004ed830,004ed830,598",
		"FUN_004cbfd0,004cbfd0,1773",
		"FUN_004ed400,004ed400,898",
		"FUN_004ef320,004ef320,156",
		"FUN_004bc690,004bc690,1951",
		"FUN_004e3ad0,004e3ad0,1015",
		"FUN_004ec580,004ec580,117",
		"FUN_004f4140,004f4140,10",
	]:
		assert row in functions_csv

	retail_winmain = hlil[
		hlil.index("004ed864  data_12d34b8 = arg1") : hlil.index(
			"004eda56  while (true)"
		)
	]
	for snippet in [
		"sub_4ef520()",
		"sub_4f0d70()",
		"sub_4f0260()",
		"SetErrorMode(uMode: SEM_FAILCRITICALERRORS)",
		"sub_4f0220()",
		"sub_4cbfd0(edi, eax_4, 0)",
		"sub_4ef320()",
		"sub_4f4140()",
		'_getcwd(&var_108, 0x100)',
		"SetWindowsHookExA(idHook: WH_KEYBOARD_LL, lpfn: sub_4ec580",
		'"winkey_disable"',
		'"tooltips_class32"',
		'sub_4f2d30("asset://ql/index.html")',
	]:
		assert snippet in retail_winmain
	assert retail_winmain.index("sub_4cbfd0") < retail_winmain.index("sub_4ef320")
	assert retail_winmain.index("sub_4ef320") < retail_winmain.index("sub_4f4140")
	assert retail_winmain.index("SetWindowsHookExA") < retail_winmain.index(
		'"winkey_disable"'
	)
	assert retail_winmain.index('"winkey_disable"') < retail_winmain.index(
		'"tooltips_class32"'
	)
	assert retail_winmain.index('"tooltips_class32"') < retail_winmain.index(
		'"asset://ql/index.html"'
	)

	source_winmain = _extract_function_block(win_main, "int WINAPI WinMain")
	for snippet in [
		"Sys_EnableDpiAwareness();",
		"Sys_CreateLoadingWindow();",
		"Sys_CreateConsole();",
		"SetErrorMode( SEM_FAILCRITICALERRORS );",
		"Sys_DestroyLoadingWindow();",
		"Sys_Milliseconds();",
		"Sys_InitStreamThread();",
		"Com_Init( sys_cmdline );",
		"NET_Init();",
		"_getcwd (cwd, sizeof(cwd));",
		"Sys_InitWinkeyHook();",
		"IN_Frame();",
		"Com_Frame();",
	]:
		assert snippet in source_winmain
	assert source_winmain.index("Sys_CreateLoadingWindow();") < source_winmain.index(
		"Sys_CreateConsole();"
	)
	assert source_winmain.index("Com_Init( sys_cmdline );") < source_winmain.index(
		"NET_Init();"
	)
	assert source_winmain.index("NET_Init();") < source_winmain.index(
		"Sys_InitWinkeyHook();"
	)
	assert source_winmain.index("Sys_InitWinkeyHook();") < source_winmain.index(
		"IN_Frame();"
	)
	assert source_winmain.index("IN_Frame();") < source_winmain.index("Com_Frame();")

	assert "Zmq_RegisterCvarsAndInitRcon();" not in win_main
	assert "Zmq_RegisterCvarsAndInitRcon();" in _extract_function_block(
		sv_init, "void SV_Init (void) {"
	)


def test_winkey_hook_reconstructs_retail_keyboard_filter_and_shutdown() -> None:
	hlil = (
		REPO_ROOT
		/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt"
	).read_text(encoding="utf-8")
	win_main = (REPO_ROOT / "src/code/win32/win_main.c").read_text(encoding="utf-8")

	retail_hook = hlil[
		hlil.index("004ec580    LRESULT __stdcall sub_4ec580") : hlil.index(
			"004ec600    int32_t sub_4ec600()"
		)
	]
	for snippet in [
		"if (arg1 s< 0)",
		"CallNextHookEx(hhk: data_12d0088",
		"arg1 == 0",
		"*(data_12d51c4 + 0x30) != 0",
		"arg2 == 0x104 || arg2 == 0x100",
		"ecx_3 == 0x5b || ecx_3 == 0x5c",
		"return 1",
	]:
		assert snippet in retail_hook

	hook_proc = _extract_function_block(
		win_main, "static LRESULT CALLBACK Sys_WinkeyHookProc"
	)
	for snippet in [
		"if ( nCode < 0 )",
		"CallNextHookEx( sys_winkeyHook, nCode, wParam, lParam );",
		"nCode == HC_ACTION",
		"sys_winkeyDisable->integer",
		"wParam == WM_SYSKEYDOWN || wParam == WM_KEYDOWN",
		"key->vkCode == VK_LWIN || key->vkCode == VK_RWIN",
		"return 1;",
	]:
		assert snippet in hook_proc

	init_hook = _extract_function_block(win_main, "static void Sys_InitWinkeyHook")
	assert (
		"SetWindowsHookExA( WH_KEYBOARD_LL, Sys_WinkeyHookProc, g_wv.hInstance, 0 )"
		in init_hook
	)
	assert 'Cvar_Get( "winkey_disable", "0", CVAR_CLOUD );' in init_hook

	shutdown_hook = _extract_function_block(win_main, "static void Sys_ShutdownWinkeyHook")
	assert "UnhookWindowsHookEx( sys_winkeyHook );" in shutdown_hook
	assert "sys_winkeyHook = NULL;" in shutdown_hook

	sys_error = _extract_function_block(win_main, "void QDECL Sys_Error")
	sys_quit = _extract_function_block(win_main, "void Sys_Quit")
	assert sys_error.index("IN_Shutdown();") < sys_error.index("Sys_ShutdownWinkeyHook();")
	assert sys_error.index("Sys_ShutdownWinkeyHook();") < sys_error.index("while ( 1 )")
	assert sys_quit.index("IN_Shutdown();") < sys_quit.index("Sys_ShutdownWinkeyHook();")
	assert sys_quit.index("Sys_ShutdownWinkeyHook();") < sys_quit.index(
		"Sys_DestroyConsole();"
	)


def test_policy_adjusted_common_client_server_wiring_matches_mapped_retail_chain() -> None:
	hlil = (
		REPO_ROOT
		/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt"
	).read_text(encoding="utf-8")
	common = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
	cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
	sv_init = (REPO_ROOT / "src/code/server/sv_init.c").read_text(encoding="utf-8")

	retail_common_init = hlil[
		hlil.index("004cbfd0    int32_t sub_4cbfd0") : hlil.index(
			"004cc6c0    void* const sub_4cc6c0()"
		)
	]
	assert retail_common_init.index("sub_4ed400()") < retail_common_init.index(
		"sub_4e9fd0()"
	)
	assert retail_common_init.index("sub_4e9fd0()") < retail_common_init.index(
		"sub_4e3ad0()"
	)
	assert retail_common_init.index("sub_4e3ad0()") < retail_common_init.index(
		"sub_4bc690"
	)
	assert 'sub_4ec6e0("Failed to initialize Steam.")' in retail_common_init

	common_init = _extract_function_block(common, "void Com_Init( char *commandLine )")
	for snippet in [
		"Com_ApplyOnlineServicesBuildPolicy();",
		"FS_InitFilesystem ();",
		"Com_InitSteamGameServer();",
		"Sys_Init();",
		"Netchan_Init( Com_Milliseconds() & 0xffff );",
		"VM_Init();",
		"SV_Init();",
		"SteamClient_Init();",
		"CL_Init();",
		"CL_StartHunkUsers();",
	]:
		assert snippet in common_init
	assert common_init.index("Com_ApplyOnlineServicesBuildPolicy();") < common_init.index(
		"FS_InitFilesystem ();"
	)
	assert common_init.index("Com_InitSteamGameServer();") < common_init.index(
		"Sys_Init();"
	)
	assert common_init.index("Sys_Init();") < common_init.index("Netchan_Init")
	assert common_init.index("Netchan_Init") < common_init.index("VM_Init();")
	assert common_init.index("VM_Init();") < common_init.index("SV_Init();")
	assert common_init.index("SV_Init();") < common_init.index("SteamClient_Init();")
	assert common_init.index("SteamClient_Init();") < common_init.index("CL_Init();")
	assert common.count("SteamClient_Init();") == 1

	client_init = _extract_function_block(cl_main, "void CL_Init( void ) {")
	for snippet in [
		"CL_RefreshPlatformServiceCvars();",
		"CL_InitSteamResources();",
		"CL_WebHost_Init();",
		"QLWebHost_RegisterCommands();",
		"SteamClient_SyncPersonaNameCvar();",
		"CL_WebPak_Init();",
		"CL_InitRef();",
		"SCR_Init ();",
		"CL_WebHost_BootstrapAwesomiumMenu();",
		"Cbuf_Execute ();",
	]:
		assert snippet in client_init
	assert client_init.index("QLWebHost_RegisterCommands();") < client_init.index(
		"SteamClient_SyncPersonaNameCvar();"
	)
	assert client_init.index("CL_InitRef();") < client_init.index("SCR_Init ();")
	assert client_init.index("SCR_Init ();") < client_init.index(
		"CL_WebHost_BootstrapAwesomiumMenu();"
	)
	assert client_init.index("CL_WebHost_BootstrapAwesomiumMenu();") < client_init.index(
		"Cbuf_Execute ();"
	)

	bootstrap = _extract_function_block(
		cl_cgame, "void CL_WebHost_BootstrapAwesomiumMenu( void )"
	)
	assert "#if !QL_PLATFORM_HAS_ONLINE_SERVICES" in bootstrap
	assert "CL_AwesomiumValidateRequiredRuntime();" in bootstrap
	assert 'Cvar_VariableIntegerValue( "qlr_requireAwesomium" )' in cl_cgame
	assert "Com_Error( ERR_FATAL," in cl_cgame
	assert "return;" in bootstrap
	assert "CL_AwesomiumRuntimeActive();" in bootstrap
	assert "QLWebHost_OpenURL( CL_WEB_DEFAULT_URL )" in bootstrap

	server_init = _extract_function_block(sv_init, "void SV_Init (void) {")
	assert "SV_RefreshPlatformServiceCvars();" in server_init
	assert "SV_SteamServerInitCallbacks();" in server_init
	assert "Zmq_RegisterCvarsAndInitRcon();" in server_init
	assert server_init.index("Zmq_RegisterCvarsAndInitRcon();") < server_init.index(
		"SV_BotInitCvars();"
	)
