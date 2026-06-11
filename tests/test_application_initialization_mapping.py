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
	)["quakelive_steam_srp"]
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
		"picce.dwSize = 8",
		"picce.dwICC = 4",
		"InitCommonControlsEx(&picce)",
		'"tooltips_class32"',
		"dwStyle: 0x80000003",
		"SetWindowPos(hWnd, hWndInsertAfter: 0xfffffffe",
		"SendMessageA(hWnd: data_12d34b0, Msg: 0x404",
		"SendMessageA(hWnd: data_12d34b0, Msg: 0x401",
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
		"Sys_InitTooltipShell();",
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
		"Sys_InitTooltipShell();"
	)
	assert source_winmain.index("Sys_InitTooltipShell();") < source_winmain.index(
		"IN_Frame();"
	)
	assert source_winmain.index("IN_Frame();") < source_winmain.index("Com_Frame();")

	common_controls = _extract_function_block(
		win_main, "static qboolean Sys_InitCommonControls"
	)
	for snippet in [
		'GetModuleHandleA( "comctl32.dll" )',
		'LoadLibraryA( "comctl32.dll" )',
		'GetProcAddress( library, "InitCommonControlsEx" )',
		"sys_commonControlsLibrary = library;",
	]:
		assert snippet in common_controls

	tooltip_shell = _extract_function_block(win_main, "static void Sys_InitTooltipShell")
	for snippet in [
		"controls.dwSize = sizeof( controls );",
		"controls.dwICC = ICC_BAR_CLASSES;",
		"Sys_InitCommonControls( &controls )",
		"CreateWindowExA( 0, TOOLTIPS_CLASSA, NULL,",
		"WS_POPUP | TTS_ALWAYSTIP | TTS_NOPREFIX",
		"CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT",
		"SetWindowPos( sys_tooltipWindow, HWND_NOTOPMOST",
		"SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE",
		"tool.cbSize = sizeof( tool );",
		"tool.uFlags = TTF_SUBCLASS;",
		"tool.hwnd = g_wv.hWnd;",
		"tool.hinst = g_wv.hInstance;",
		'tool.lpszText = "";',
		"GetWindowRect( GetDesktopWindow(), &desktopRect );",
		"tool.rect = desktopRect;",
		"SendMessageA( sys_tooltipWindow, TTM_ADDTOOLA, 0, (LPARAM)&tool );",
		"SendMessageA( sys_tooltipWindow, TTM_ACTIVATE, 0, 0 );",
	]:
		assert snippet in tooltip_shell

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

	shutdown_tooltip = _extract_function_block(
		win_main, "static void Sys_ShutdownTooltipShell"
	)
	for snippet in [
		"DestroyWindow( sys_tooltipWindow );",
		"sys_tooltipWindow = NULL;",
		"FreeLibrary( sys_commonControlsLibrary );",
		"sys_commonControlsLibrary = NULL;",
	]:
		assert snippet in shutdown_tooltip

	sys_error = _extract_function_block(win_main, "void QDECL Sys_Error")
	sys_quit = _extract_function_block(win_main, "void Sys_Quit")
	assert sys_error.index("IN_Shutdown();") < sys_error.index("Sys_ShutdownWinkeyHook();")
	assert sys_error.index("Sys_ShutdownWinkeyHook();") < sys_error.index(
		"Sys_ShutdownTooltipShell();"
	)
	assert sys_error.index("Sys_ShutdownTooltipShell();") < sys_error.index("while ( 1 )")
	assert sys_quit.index("IN_Shutdown();") < sys_quit.index("Sys_ShutdownWinkeyHook();")
	assert sys_quit.index("Sys_ShutdownWinkeyHook();") < sys_quit.index(
		"Sys_ShutdownTooltipShell();"
	)
	assert sys_quit.index("Sys_ShutdownTooltipShell();") < sys_quit.index(
		"Sys_DestroyConsole();"
	)


def test_debug_crash_dump_prompt_preserves_dump_and_log_contract() -> None:
	win_main = (REPO_ROOT / "src/code/win32/win_main.c").read_text(encoding="utf-8")

	confirm_block = _extract_function_block(
		win_main, "static qboolean Sys_DebugCrashReportConfirmed"
	)
	result_block = _extract_function_block(
		win_main, "static void Sys_ShowDebugCrashReportResult"
	)
	filter_block = _extract_function_block(
		win_main, "static LONG WINAPI Sys_UnhandledExceptionFilter"
	)
	init_block = _extract_function_block(win_main, "static void Sys_InitCrashDumps")
	dump_type_block = _extract_function_block(win_main, "static MINIDUMP_TYPE Sys_GetCrashDumpType")

	assert '#define SYS_CRASH_DIALOG_TITLE\tQL_PRODUCT_NAME " Debug Crash"' in win_main
	assert "#ifdef _DEBUG\n/*\n==================\nSys_DebugCrashReportConfirmed" in win_main
	assert '"Create a memory dump and crash log?\\n\\n"' in confirm_block
	assert "MessageBoxA( NULL, message, SYS_CRASH_DIALOG_TITLE," in confirm_block
	assert "MB_ICONERROR | MB_YESNO | MB_DEFBUTTON1 | MB_TASKMODAL | MB_SETFOREGROUND" in confirm_block
	assert "return (qboolean)( result == IDYES );" in confirm_block

	for snippet in [
		"Crash dump and crash log written.",
		"Crash dump written, but crash log creation failed.",
		"Crash log written, but memory dump creation failed.",
		"Crash report creation failed.",
	]:
		assert snippet in result_block

	assert "envPath = getenv( \"QLR_DUMP_PATH\" );" in init_block
	assert "SetUnhandledExceptionFilter( Sys_UnhandledExceptionFilter );" in init_block
	assert "fullDump = getenv( \"QLR_FULL_DUMP\" );" in dump_type_block
	assert "MiniDumpWithFullMemory" in dump_type_block

	assert "if ( IsDebuggerPresent() ) {" in filter_block
	assert "if ( !Sys_DebugCrashReportConfirmed( dumpName, logName ) ) {" in filter_block
	assert "return EXCEPTION_EXECUTE_HANDLER;" in filter_block
	assert 'Com_sprintf( dumpName, sizeof( dumpName ), "%s.dmp", crashBaseName );' in filter_block
	assert 'Com_sprintf( logName, sizeof( logName ), "%s.log", crashBaseName );' in filter_block
	assert filter_block.index("CreateFileA( logName") < filter_block.index("CreateFileA( dumpName")
	assert "MiniDumpWriteDump( GetCurrentProcess(), GetCurrentProcessId(), dumpFile, dumpType, &dumpInfo, NULL, NULL );" in filter_block
	assert "Sys_ShowDebugCrashReportResult( (qboolean)dumpWritten, logWritten, dumpName, logName, dumpError );" in filter_block


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
	for snippet in [
		'004cc146      void** eax_7 = sub_4ce0d0(x87_r6, "dedicated", U"0", 0x10)',
		"004cc16e          sub_461500()",
		'004cc47f      data_145b948 = sub_4ce0d0(x87_r1, "com_build", U"0", 0)',
		'004cc5fd      if (sub_460510() == 0 && sub_4ccd80("com_build") == 0 && sub_4ccd80("dedicated") == 0)',
		'004cc626          sub_4ec6e0("Failed to initialize Steam.")',
	]:
		assert snippet in retail_common_init
	assert retail_common_init.index('004cc146      void** eax_7 = sub_4ce0d0(x87_r6, "dedicated", U"0", 0x10)') < retail_common_init.index(
		"004cc16e          sub_461500()"
	)
	assert retail_common_init.index("004cc16e          sub_461500()") < retail_common_init.index(
		'004cc47f      data_145b948 = sub_4ce0d0(x87_r1, "com_build", U"0", 0)'
	)
	assert retail_common_init.index("sub_4bc690") < retail_common_init.index(
		'004cc5fd      if (sub_460510() == 0 && sub_4ccd80("com_build") == 0 && sub_4ccd80("dedicated") == 0)'
	)
	assert retail_common_init.index(
		'004cc5fd      if (sub_460510() == 0 && sub_4ccd80("com_build") == 0 && sub_4ccd80("dedicated") == 0)'
	) < retail_common_init.index('004cc626          sub_4ec6e0("Failed to initialize Steam.")')
	assert 'sub_4ec6e0("Failed to initialize Steam.")' in retail_common_init

	common_init = _extract_function_block(common, "void Com_Init( char *commandLine )")
	for snippet in [
		"Com_ApplyOnlineServicesBuildPolicy();",
		"Com_InitSteamClientForFilesystem();",
		"FS_InitFilesystem ();",
		"Com_InitSteamGameServer();",
		"Sys_Init();",
		"Netchan_Init( Com_Milliseconds() & 0xffff );",
		"VM_Init();",
		"SV_Init();",
		"SV_RegisterGameCvars();",
		"CL_RegisterCGameCvars();",
		"SteamClient_Init();",
		"CL_Init();",
		"Com_VerifySteamClientStartup();",
		"CL_StartHunkUsers();",
	]:
		assert snippet in common_init
	assert common_init.index("Com_ApplyOnlineServicesBuildPolicy();") < common_init.index(
		"FS_InitFilesystem ();"
	)
	assert common_init.index("Com_InitSteamClientForFilesystem();") < common_init.index(
		"FS_InitFilesystem ();"
	)
	assert common_init.index("Com_InitSteamGameServer();") < common_init.index(
		"Sys_Init();"
	)
	steam_filesystem_block = _extract_function_block(
		common, "static void Com_InitSteamClientForFilesystem( void ) {"
	)
	assert 'Cvar_VariableIntegerValue( "dedicated" )' in steam_filesystem_block
	assert 'Cvar_VariableIntegerValue( "com_build" )' in steam_filesystem_block
	assert steam_filesystem_block.index('Cvar_VariableIntegerValue( "com_build" )') < steam_filesystem_block.index(
		"SteamClient_InitForFilesystem();"
	)
	assert "SteamClient_InitForFilesystem();" in steam_filesystem_block
	assert "QL_RefreshPlatformServices();" not in steam_filesystem_block
	assert common_init.index("Sys_Init();") < common_init.index("Netchan_Init")
	assert common_init.index("Netchan_Init") < common_init.index("VM_Init();")
	assert common_init.index("VM_Init();") < common_init.index("SV_Init();")
	assert common_init.index("SV_Init();") < common_init.index("SV_RegisterGameCvars();")
	assert common_init.index("SV_RegisterGameCvars();") < common_init.index("CL_RegisterCGameCvars();")
	assert common_init.index("CL_RegisterCGameCvars();") < common_init.index("SteamClient_Init();")
	assert common_init.index("SteamClient_Init();") < common_init.index("CL_Init();")
	assert common_init.index("CL_Init();") < common_init.index("Com_VerifySteamClientStartup();")
	assert common_init.index("Com_VerifySteamClientStartup();") < common_init.index("CL_StartHunkUsers();")
	assert common.count("SteamClient_Init();") == 1

	steam_startup_guard = _extract_function_block(
		common, "static void Com_VerifySteamClientStartup( void ) {"
	)
	assert "SteamClient_IsInitialized()" in steam_startup_guard
	assert "com_buildScript && com_buildScript->integer" in steam_startup_guard
	assert 'Cvar_VariableIntegerValue( "dedicated" )' in steam_startup_guard
	assert 'retail would abort with \\"Failed to initialize Steam.\\" here' in steam_startup_guard
	assert "Com_Error" not in steam_startup_guard
	assert "Sys_Error" not in steam_startup_guard
	assert steam_startup_guard.index("SteamClient_IsInitialized()") < steam_startup_guard.index(
		"com_buildScript && com_buildScript->integer"
	)
	assert steam_startup_guard.index("com_buildScript && com_buildScript->integer") < steam_startup_guard.index(
		'Cvar_VariableIntegerValue( "dedicated" )'
	)
	assert steam_startup_guard.index('Cvar_VariableIntegerValue( "dedicated" )') < steam_startup_guard.index(
		'retail would abort with \\"Failed to initialize Steam.\\" here'
	)
	assert "QL_GetOnlineServicesModeLabel()" in steam_startup_guard
	assert "QL_GetOnlineServicesPolicyLabel()" in steam_startup_guard

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


def test_policy_adjusted_steamid_native_dll_root_precedes_retail_basepath() -> None:
	aliases = json.loads(
		(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json").read_text(
			encoding="utf-8"
		)
	)["quakelive_steam_srp"]
	functions_csv = (
		REPO_ROOT / "references/reverse-engineering/ghidra/quakelive_steam/functions.csv"
	).read_text(encoding="utf-8")
	hlil_part05 = (
		REPO_ROOT
		/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt"
	).read_text(encoding="utf-8")
	hlil_part04 = (
		REPO_ROOT
		/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt"
	).read_text(encoding="utf-8")
	files_c = (REPO_ROOT / "src/code/qcommon/files.c").read_text(encoding="utf-8")
	win_main = (REPO_ROOT / "src/code/win32/win_main.c").read_text(encoding="utf-8")

	retail_load_dll = hlil_part05[
		hlil_part05.index("004eceb0    HMODULE sub_4eceb0") : hlil_part05.index(
			"004ed050    int32_t sub_4ed050"
		)
	]
	resolve_home_block = _extract_function_block(
		files_c, "static const char *FS_ResolveHomePath( const char *basePath ) {"
	)
	load_dll_block = _extract_function_block(
		win_main,
		"void * QDECL Sys_LoadDll( const char *name, char *fqpath, int (QDECL **entryPoint)(int, ...)",
	)
	materialize_block = _extract_function_block(
		win_main,
		"static qboolean Sys_MaterializeNativeDllFromBinPak( const char *name, const char *filename, char **roots, int rootCount,",
	)
	should_extract_block = _extract_function_block(
		win_main,
		"static qboolean Sys_ShouldExtractNativeDllFromBinPak( const char *name, const char *filename, const char *gamedir ) {",
	)

	assert aliases["sub_4ECEB0"] == "Sys_LoadDll"
	assert "FUN_004eceb0,004eceb0,358" in functions_csv
	assert "004d3202  if (sub_460510() == 0)" in hlil_part04
	assert "004d3204      eax_9, edx_1 = sub_460550()" in hlil_part04
	assert '004d3219      eax_7 = sub_4d9220("%s/%llu")' in hlil_part04
	assert '004d3245  data_1227bc8 = sub_4ce0d0(x87_r6, "fs_homepath", eax_7, 0x10)' in hlil_part04
	assert hlil_part04.index("004d3202  if (sub_460510() == 0)") < hlil_part04.index(
		"004d3204      eax_9, edx_1 = sub_460550()"
	)
	assert hlil_part04.index("004d3204      eax_9, edx_1 = sub_460550()") < hlil_part04.index(
		'004d3219      eax_7 = sub_4d9220("%s/%llu")'
	)
	assert hlil_part04.index('004d3219      eax_7 = sub_4d9220("%s/%llu")') < hlil_part04.index(
		'004d3245  data_1227bc8 = sub_4ce0d0(x87_r6, "fs_homepath", eax_7, 0x10)'
	)
	assert "004ecf6f      result = LoadLibraryA(lpLibFileName: sub_4cec90(eax_6, eax_8, &var_48))" in retail_load_dll
	assert "004ecf89          result = LoadLibraryA(lpLibFileName: sub_4cec90(eax_5, eax_8, &var_48))" in retail_load_dll
	assert "004ecfac              result = LoadLibraryA(lpLibFileName: sub_4cec90(eax_7, eax_8, &var_48))" in retail_load_dll
	assert retail_load_dll.index('sub_4ccda0("fs_homepath")') < retail_load_dll.index(
		'LoadLibraryA(lpLibFileName: sub_4cec90(eax_6'
	)
	assert retail_load_dll.index('LoadLibraryA(lpLibFileName: sub_4cec90(eax_6') < retail_load_dll.index(
		'LoadLibraryA(lpLibFileName: sub_4cec90(eax_5'
	)
	assert retail_load_dll.index('LoadLibraryA(lpLibFileName: sub_4cec90(eax_5') < retail_load_dll.index(
		'LoadLibraryA(lpLibFileName: sub_4cec90(eax_7'
	)

	assert 'steamId = SteamClient_GetSteamID();' in resolve_home_block
	assert 'Com_sprintf( steamHome, sizeof( steamHome ), "%s/%llu", basePath, (unsigned long long)steamId );' in resolve_home_block
	assert 'Cvar_VariableString( "fs_homepath" )' in load_dll_block
	assert "Retail probes fs_basepath before fs_homepath" in load_dll_block
	assert "replacement launches prefer fs_basepath/<steamid>" in load_dll_block
	assert load_dll_block.index("searchRoots[searchCount++] = homepath;") < load_dll_block.index(
		"searchRoots[searchCount++] = basepath;"
	)
	assert load_dll_block.index("searchRoots[searchCount++] = basepath;") < load_dll_block.index(
		"searchRoots[searchCount++] = cdpath;"
	)
	assert load_dll_block.index("searchRoots[searchCount++] = cdpath;") < load_dll_block.index(
		"searchRoots[searchCount++] = cwdpath;"
	)
	assert load_dll_block.index("binPakRoots[binPakRootCount++] = homepath;") < load_dll_block.index(
		"binPakRoots[binPakRootCount++] = basepath;"
	)
	assert load_dll_block.index("binPakRoots[binPakRootCount++] = basepath;") < load_dll_block.index(
		"binPakRoots[binPakRootCount++] = cdpath;"
	)
	assert 'if ( gamedir && gamedir[0] && Q_stricmp( gamedir, BASEGAME ) ) {' in should_extract_block
	assert 'if ( !Q_stricmp( name, "ui" ) && !Q_stricmp( filename, "uix86.dll" ) ) {' in should_extract_block
	assert 'if ( !Q_stricmp( name, "cgame" ) && !Q_stricmp( filename, "cgamex86.dll" ) ) {' in should_extract_block
	assert 'if ( !Q_stricmp( name, "qagame" ) && !Q_stricmp( filename, "qagamex86.dll" ) ) {' in should_extract_block
	assert should_extract_block.count("return qtrue;") == 3
	assert should_extract_block.rstrip().endswith("}")
	assert should_extract_block.index('Q_stricmp( gamedir, BASEGAME )') < should_extract_block.index(
		'!Q_stricmp( name, "ui" )'
	)
	assert "Sys_MaterializeNativeDllFromBinPak( name, filename, binPakRoots, binPakRootCount, dllGamedir," in load_dll_block
	assert 'FS_BuildOSPath( roots[i], BASEGAME, "bin.pk3" )' in materialize_block
	assert "pack = FS_LoadPackExplicit( pakPath );" in materialize_block
	assert "length = FS_ReadFileFromPak( pack, filename, &buffer );" in materialize_block
	assert "FS_FreePak( pack );" in materialize_block
	assert "Sys_GetNativeDllCachePath( filename, rootCount > 0 ? roots[0] : NULL, gamedir, cachePath, sizeof( cachePath ) )" in materialize_block
	assert "Sys_WriteFileToPath( cachePath, buffer, length )" in materialize_block
	assert "Sys_FileIsReadable( cachePath )" in materialize_block
	assert 'Com_Printf( "Sys_LoadDll: extracted %s from %s\\n", filename, pakPath );' in materialize_block
	assert load_dll_block.index("for ( i = 0; i < searchCount; i++ ) {") < load_dll_block.index(
		"Sys_MaterializeNativeDllFromBinPak( name, filename, binPakRoots, binPakRootCount, dllGamedir,"
	)
	assert "Sys_TryLoadDllFromPath( extractedPath, fqpath, entryPoint, dllExports, imports, apiVersion, systemcalls )" in load_dll_block
