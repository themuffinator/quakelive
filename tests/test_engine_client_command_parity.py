from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

# Retail command-owner evidence for this focused client slice comes from
# `references/analysis/quakelive_symbol_aliases.json`, the paired HLIL owners in
# `references/hlil/quakelive/quakelive_steam.exe/`, and the matching Ghidra
# registration surface in
# `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`:
# `sub_4B8AD0` -> `CL_ForwardToServer_f`
# `sub_4B90B0` -> `CL_Configstrings_f`
# `sub_4B9100` -> `CL_Clientinfo_f`
# `sub_4B9060` -> retail `postprocess_restart` client wrapper
# `sub_4BB9B0` -> `CL_Snd_Restart_f`
# `sub_4BB7E0` -> `CL_Vid_Restart_f`
# `sub_4B8C70` -> `CL_Disconnect_f`
# `sub_4B8300` -> `CL_StopRecord_f`
# `sub_4B8B30` -> `CL_Setenv_f`
# `LAB_004BB1A0` -> `CL_ShowIP_f`
# `sub_4B9070` -> `CL_OpenedPK3List_f`
# `sub_4B9090` -> `CL_ReferencedPK3List_f`
# `FUN_004D7980` -> retail no-op `userinfo` reservation owner
# `sub_4603F0` -> `+voice`
# `sub_460490` -> `-voice`
# `sub_460520` -> `stats_clear`
# `sub_460E60` -> `clientviewprofile` / `clientfriendinvite`
# `sub_464AA0` -> `connect_lobby`
# `sub_4B9D10` -> `CL_SetModel_f`
# `004F3CD0` -> retail browser command registration helper
# `004F3160` -> `web_showBrowser`
# `004F31D0` -> `web_changeHash`
# `004F24D0` -> `web_hideBrowser`
# `004F3CC0` -> `web_showError`


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	in_string = False
	escaped = False
	for index in range(brace_start, len(text)):
		char = text[index]

		if in_string:
			if escaped:
				escaped = False
			elif char == "\\":
				escaped = True
			elif char == '"':
				in_string = False
			continue

		if char == '"':
			in_string = True
		elif char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def test_client_command_registration_matches_retail_cl_init_surface() -> None:
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

	init_block = _extract_function_block(cl_main, "void CL_Init( void ) {")
	shutdown_block = _extract_function_block(cl_main, "void CL_Shutdown( void ) {")

	assert 'Cmd_AddCommand ("cmd", CL_ForwardToServer_f);' in init_block
	assert 'Cmd_AddCommand ("configstrings", CL_Configstrings_f);' in init_block
	assert 'Cmd_AddCommand ("clientinfo", CL_Clientinfo_f);' in init_block
	assert 'Cmd_AddCommand ("snd_restart", CL_Snd_Restart_f);' in init_block
	assert 'Cmd_AddCommand ("vid_restart", CL_Vid_Restart_f);' in init_block
	assert 'Cmd_AddCommand ("postprocess_restart", CL_PostProcessRestart_f);' in init_block
	assert 'Cmd_AddCommand ("disconnect", CL_Disconnect_f);' in init_block
	assert 'Cmd_AddCommand ("stoprecord", CL_StopRecord_f);' in init_block
	assert 'Cmd_AddCommand ("setenv", CL_Setenv_f );' in init_block
	assert 'Cmd_AddCommand ("showip", CL_ShowIP_f );' in init_block

	assert 'Cmd_AddCommand ("fs_openedList", CL_OpenedPK3List_f );' in init_block
	assert 'Cmd_AddCommand ("fs_referencedList", CL_ReferencedPK3List_f );' in init_block
	assert 'Cmd_AddCommand ("userinfo", CL_Userinfo_f );' in init_block

	assert 'Cmd_RemoveCommand ("userinfo");' in shutdown_block
	assert 'Cmd_RemoveCommand ("postprocess_restart");' in shutdown_block


def test_client_command_handlers_match_retail_forward_restart_and_info_contracts() -> None:
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

	userinfo_guard_block = _extract_function_block(
		cl_main, "static qboolean CL_CommandContainsUserinfoToken( const char *commandName ) {"
	)
	forward_block = _extract_function_block(cl_main, "void CL_ForwardToServer_f( void ) {")
	configstrings_block = _extract_function_block(cl_main, "void CL_Configstrings_f( void ) {")
	clientinfo_block = _extract_function_block(cl_main, "void CL_Clientinfo_f( void ) {")
	postprocess_block = _extract_function_block(cl_main, "static void CL_PostProcessRestart_f( void ) {")
	snd_restart_block = _extract_function_block(cl_main, "void CL_Snd_Restart_f( void ) {")
	vid_restart_block = _extract_function_block(cl_main, "void CL_Vid_Restart_f( void ) {")
	disconnect_block = _extract_function_block(cl_main, "void CL_Disconnect_f( void ) {")
	stoprecord_block = _extract_function_block(cl_main, "void CL_StopRecord_f( void ) {")
	setenv_block = _extract_function_block(cl_main, "void CL_Setenv_f( void ) {")
	showip_block = _extract_function_block(cl_main, "void CL_ShowIP_f(void) {")
	userinfo_block = _extract_function_block(cl_main, "static void CL_Userinfo_f( void ) {")

	assert 'if ( !Q_stricmpn( cursor, "userinfo", 8 ) ) {' in userinfo_guard_block
	assert 'Com_Printf ("Not connected to a server.\\n");' in forward_block
	assert 'if ( Cmd_Argc() > 1 && !CL_CommandContainsUserinfoToken( Cmd_Argv( 1 ) ) ) {' in forward_block
	assert "CL_AddReliableCommand( Cmd_Args() );" in forward_block

	assert 'Com_Printf( "Not connected to a server.\\n");' in configstrings_block
	assert 'Com_Printf( "%4i: %s\\n", i, cl.gameState.stringData + ofs );' in configstrings_block

	assert 'Com_Printf( "--------- Client Information ---------\\n" );' in clientinfo_block
	assert 'Com_Printf( "state: %i\\n", cls.state );' in clientinfo_block
	assert 'Com_Printf( "Server: %s\\n", cls.servername );' in clientinfo_block
	assert 'Com_Printf ("User info settings:\\n");' in clientinfo_block
	assert 'Info_Print( Cvar_InfoString( CVAR_USERINFO ) );' in clientinfo_block

	assert 'if ( !re.PostProcessRestart ) {' in postprocess_block
	assert "re.PostProcessRestart();" in postprocess_block

	assert "S_Shutdown();" in snd_restart_block
	assert "S_Init();" in snd_restart_block
	assert "CL_Vid_Restart_f();" in snd_restart_block

	assert 'if ( !Cvar_VariableIntegerValue( "r_noFastRestart" ) && Cmd_Argc() > 1 && !Q_stricmp( Cmd_Argv( 1 ), "fast" ) ) {' in vid_restart_block
	assert 'Cbuf_AddText( "postprocess_restart\\n" );' in vid_restart_block
	assert "VM_Call( cgvm, CG_EVENT_HANDLING, CGAME_EVENT_REFRESH_DISPLAY_CONTEXT );" in vid_restart_block
	assert "VM_Call( uivm, UI_REFRESH_DISPLAY_CONTEXT );" in vid_restart_block
	assert "CL_ResetPureClientAtServer();" in vid_restart_block
	assert "FS_ConditionalRestart( clc.checksumFeed );" in vid_restart_block

	assert 'Cvar_Set("ui_singlePlayerActive", "0");' in disconnect_block
	assert 'Com_Error (ERR_DISCONNECT, "Disconnected from server");' in disconnect_block

	assert 'Com_Printf ("Not recording a demo.\\n");' in stoprecord_block
	assert 'Com_Printf ("Stopped demo.\\n");' in stoprecord_block

	assert 'char buffer[1024];' in setenv_block
	assert 'strcpy( buffer, Cmd_Argv(1) );' in setenv_block
	assert 'putenv( buffer );' in setenv_block
	assert 'Com_Printf( "%s=%s\\n", Cmd_Argv(1), env );' in setenv_block
	assert 'Com_Printf( "%s undefined\\n", Cmd_Argv(1), env );' in setenv_block

	assert "Sys_ShowIP();" in showip_block

	assert ";" not in userinfo_block


def test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration() -> None:
	tr_public = (REPO_ROOT / "src/code/renderer/tr_public.h").read_text(encoding="utf-8")
	tr_init = (REPO_ROOT / "src/code/renderer/tr_init.c").read_text(encoding="utf-8")

	restart_block = _extract_function_block(tr_init, "static void R_PostProcessRestart( void ) {")
	register_block = _extract_function_block(tr_init, "void R_Register( void )")
	shutdown_block = _extract_function_block(tr_init, "void RE_Shutdown( qboolean destroyWindow ) {")
	api_block = _extract_function_block(tr_init, "refexport_t *GetRefAPI ( int apiVersion, refimport_t *rimp ) {")

	assert 'void\t(*PostProcessRestart)( void );' in tr_public
	assert "R_UpdatePostProcessCvars();" in restart_block
	assert "tr.postProcessNeedsReset = qtrue;" in restart_block
	assert "re.PostProcessRestart = R_PostProcessRestart;" in api_block
	assert 'ri.Cmd_AddCommand( "postprocess_restart", R_PostProcessRestart' not in register_block
	assert 'ri.Cmd_RemoveCommand( "postprocess_restart" );' not in shutdown_block


def test_client_steam_command_registration_and_identity_wiring_match_retail_surface() -> None:
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

	init_block = _extract_function_block(cl_main, "void CL_Init( void ) {")
	identity_block = _extract_function_block(
		cl_main, "static qboolean CL_CopyClientIdentity( int clientNum, cgameClientIdentity_t *identity ) {"
	)
	get_steam_id_block = _extract_function_block(
		cl_main, "static qboolean CL_GetClientSteamId( int clientNum, uint32_t *steamIdLow, uint32_t *steamIdHigh ) {"
	)
	overlay_block = _extract_function_block(cl_main, "static void CL_Steam_OverlayCommand_f( void ) {")
	connect_lobby_block = _extract_function_block(cl_main, "static void CL_Steam_ConnectLobby_f( void ) {")
	stats_gate_block = _extract_function_block(cl_main, "static qboolean CL_Steam_ShouldRegisterStatsClear( void ) {")

	assert 'Cmd_AddCommand ("fs_openedList", CL_OpenedPK3List_f );' in init_block
	assert 'Cmd_AddCommand ("fs_referencedList", CL_ReferencedPK3List_f );' in init_block
	assert 'Cmd_AddCommand ("model", CL_SetModel_f );' in init_block
	assert 'Cmd_AddCommand ("userinfo", CL_Userinfo_f );' in init_block
	assert 'Cmd_AddCommand ("+voice", CL_VoiceStartRecording_f );' in init_block
	assert 'Cmd_AddCommand ("-voice", CL_VoiceStopRecording_f );' in init_block
	assert 'Cmd_AddCommand ("connect_lobby", CL_Steam_ConnectLobby_f );' in init_block
	assert 'Cmd_AddCommand ("clientviewprofile", CL_Steam_OverlayCommand_f );' in init_block
	assert 'Cmd_AddCommand ("clientfriendinvite", CL_Steam_OverlayCommand_f );' in init_block
	assert 'Cmd_AddCommand ("stats_clear", CL_Steam_ClearStats_f );' in init_block

	assert 'if ( !cgvm || !( cgvm->entryPoint || cgvm->dllExports ) ) {' in identity_block
	assert 'VM_Call( cgvm, CG_COPY_CLIENT_IDENTITY, clientNum, (int)(intptr_t)identity )' in identity_block
	assert 'return ( identity->identityLow | identity->identityHigh ) ? qtrue : qfalse;' in identity_block

	assert "if ( CL_CopyClientIdentity( clientNum, &identity ) ) {" in get_steam_id_block
	assert "offset = cl.gameState.stringOffsets[CS_PLAYERS + clientNum];" in get_steam_id_block
	assert 'steamId = Info_ValueForKey( info, "steamid" );' in get_steam_id_block

	assert 'if ( !Q_stricmp( commandName, "clientviewprofile" ) ) {' in overlay_block
	assert 'dialog = "steamid";' in overlay_block
	assert 'dialog = "friendadd";' in overlay_block
	assert "clientNum = atoi( Cmd_Argv( 1 ) );" in overlay_block
	assert "if ( !CL_GetClientSteamId( clientNum, &steamIdLow, &steamIdHigh ) ) {" in overlay_block
	assert "QL_Steamworks_ActivateOverlayToUser( dialog, steamIdLow, steamIdHigh );" in overlay_block

	assert 'Cvar_Set( "lobby_autoconnect", Cmd_Argv( 1 ) );' in connect_lobby_block
	assert 'return QL_Steamworks_GetAppID() == 0x54100u ? qtrue : qfalse;' in stats_gate_block


def test_client_steam_command_handlers_match_retail_voice_stats_and_model_contracts() -> None:
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
	platform_h = (REPO_ROOT / "src/common/platform/platform_steamworks.h").read_text(encoding="utf-8")
	platform_c = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

	stats_block = _extract_function_block(cl_main, "static void CL_Steam_ClearStats_f( void ) {")
	voice_start_block = _extract_function_block(cl_main, "static void CL_VoiceStartRecording_f( void ) {")
	voice_stop_block = _extract_function_block(cl_main, "static void CL_VoiceStopRecording_f( void ) {")
	opened_block = _extract_function_block(cl_main, "void CL_OpenedPK3List_f( void ) {")
	referenced_block = _extract_function_block(cl_main, "void CL_ReferencedPK3List_f( void ) {")
	model_block = _extract_function_block(cl_main, "void CL_SetModel_f( void ) {")
	voice_helper_block = _extract_function_block(
		platform_c, "qboolean QL_Steamworks_SetInGameVoiceSpeaking( uint32_t idLow, uint32_t idHigh, qboolean speaking ) {"
	)

	assert "QL_Steamworks_ClearStats( qtrue );" in stats_block
	assert "Com_DPrintf" not in stats_block

	assert "QL_Steamworks_GetUserSteamID( &steamIdLow, &steamIdHigh )" in voice_start_block
	assert "QL_Steamworks_SetInGameVoiceSpeaking( steamIdLow, steamIdHigh, qtrue );" in voice_start_block
	assert "QL_Steamworks_StartVoiceRecording();" in voice_start_block
	assert 'Com_DPrintf( "Started recording - optimal sample rate %d\\n",' in voice_start_block
	assert "(int)QL_Steamworks_GetVoiceOptimalSampleRate()" in voice_start_block
	assert "CL_SetLocalSpeakingState( qtrue );" in voice_start_block

	assert "QL_Steamworks_StopVoiceRecording();" in voice_stop_block
	assert "QL_Steamworks_SetInGameVoiceSpeaking( steamIdLow, steamIdHigh, qfalse );" in voice_stop_block
	assert "cl_voiceRecordingActive = qfalse;" in voice_stop_block
	assert "CL_SetLocalSpeakingState( qfalse );" in voice_stop_block

	assert 'Com_Printf("Opened PK3 Names: %s\\n", FS_LoadedPakNames());' in opened_block
	assert 'Com_Printf("Referenced PK3 Names: %s\\n", FS_ReferencedPakNames());' in referenced_block
	assert 'Cvar_Set( "model", arg );' in model_block
	assert 'Cvar_Set( "headmodel", arg );' in model_block
	assert 'Com_Printf("model is set to %s\\n", name);' in model_block

	assert "qboolean QL_Steamworks_SetInGameVoiceSpeaking( uint32_t idLow, uint32_t idHigh, qboolean speaking );" in platform_h
	assert "static inline qboolean QL_Steamworks_SetInGameVoiceSpeaking( uint32_t idLow, uint32_t idHigh, qboolean speaking ) {" in platform_h
	assert "typedef void (__fastcall *QL_SteamFriends_SetInGameVoiceSpeakingFn)( void *self, void *unused, CSteamID steamId, int speaking );" in voice_helper_block
	assert "fn = (QL_SteamFriends_SetInGameVoiceSpeakingFn)vtable[0x6c / 4];" in voice_helper_block
	assert "fn( friends, NULL, QL_Steamworks_CombineIdentityWords( idLow, idHigh ), speaking ? 1 : 0 );" in voice_helper_block


def test_client_command_registration_matches_retail_cinematic_network_and_browser_surface() -> None:
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

	init_block = _extract_function_block(cl_main, "void CL_Init( void ) {")
	shutdown_block = _extract_function_block(cl_main, "void CL_Shutdown( void ) {")

	assert 'Cmd_AddCommand ("cinematic", CL_PlayCinematic_f);' in init_block
	assert 'Cmd_AddCommand ("localservers", CL_LocalServers_f);' in init_block
	assert 'Cmd_AddCommand ("globalservers", CL_GlobalServers_f);' in init_block
	assert 'Cmd_AddCommand ("rcon", CL_Rcon_f);' in init_block
	assert 'Cmd_AddCommand ("ping", CL_Ping_f );' in init_block
	assert 'Cmd_AddCommand ("serverstatus", CL_ServerStatus_f );' in init_block
	assert 'Cmd_AddCommand ("web_showBrowser", CL_Web_ShowBrowser_f );' in init_block
	assert 'Cmd_AddCommand ("web_changeHash", CL_Web_ChangeHash_f );' in init_block
	assert 'Cmd_AddCommand ("web_hideBrowser", CL_Web_HideBrowser_f );' in init_block
	assert 'Cmd_AddCommand ("web_showError", CL_Web_ShowError_f );' in init_block

	assert 'Cmd_RemoveCommand ("cinematic");' in shutdown_block
	assert 'Cmd_RemoveCommand ("localservers");' in shutdown_block
	assert 'Cmd_RemoveCommand ("globalservers");' in shutdown_block
	assert 'Cmd_RemoveCommand ("ping");' in shutdown_block
	assert 'Cmd_RemoveCommand ("web_showBrowser");' in shutdown_block
	assert 'Cmd_RemoveCommand ("web_changeHash");' in shutdown_block
	assert 'Cmd_RemoveCommand ("web_hideBrowser");' in shutdown_block
	assert 'Cmd_RemoveCommand ("web_showError");' in shutdown_block

	assert 'Cmd_AddCommand ("togglemenu", CL_ToggleMenu_f );' not in init_block
	assert 'Cmd_AddCommand ("web_browserActive", CL_Web_BrowserActive_f );' not in init_block
	assert 'Cmd_AddCommand ("web_stopRefresh", CL_Web_StopRefresh_f );' not in init_block
	assert 'Cmd_RemoveCommand ("togglemenu");' not in shutdown_block
	assert 'Cmd_RemoveCommand ("web_browserActive");' not in shutdown_block
	assert 'Cmd_RemoveCommand ("web_stopRefresh");' not in shutdown_block


def test_client_command_handlers_match_retail_cinematic_network_and_browser_contracts() -> None:
	cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
	cl_cin = (REPO_ROOT / "src/code/client/cl_cin.c").read_text(encoding="utf-8")
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

	play_cinematic_block = _extract_function_block(cl_cin, "void CL_PlayCinematic_f(void) {")
	rcon_block = _extract_function_block(cl_main, "void CL_Rcon_f( void ) {")
	localservers_block = _extract_function_block(cl_main, "void CL_LocalServers_f( void ) {")
	globalservers_block = _extract_function_block(cl_main, "void CL_GlobalServers_f( void ) {")
	ping_block = _extract_function_block(cl_main, "void CL_Ping_f( void ) {")
	serverstatus_block = _extract_function_block(cl_main, "void CL_ServerStatus_f(void) {")
	open_url_block = _extract_function_block(cl_cgame, "static qboolean QLWebHost_OpenURL( const char *url ) {")
	show_browser_block = _extract_function_block(cl_cgame, "void CL_Web_ShowBrowser_f( void ) {")
	change_hash_block = _extract_function_block(cl_cgame, "void CL_Web_ChangeHash_f( void ) {")
	hide_browser_block = _extract_function_block(cl_cgame, "static void QLWebHost_HideBrowser( void ) {")
	show_error_block = _extract_function_block(cl_cgame, "void CL_Web_ShowError_f( void ) {")

	assert 'if ((s && s[0] == \'1\') || Q_stricmp(arg,"demoend.roq")==0 || Q_stricmp(arg,"end.roq")==0) {' in play_cinematic_block
	assert "S_StopAllSounds ();" in play_cinematic_block
	assert "CL_handle = CIN_PlayCinematic( arg, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, bits );" in play_cinematic_block

	assert "Com_Printf (\"You must set 'rconpassword' before\\n\"" in rcon_block
	assert 'strcat (message, "rcon ");' in rcon_block
	assert "strcat (message, Cmd_Cmd()+5);" in rcon_block
	assert 'if (!strlen(rconAddress->string)) {' in rcon_block
	assert "NET_SendPacket (NS_CLIENT, strlen(message)+1, message, to);" in rcon_block

	assert 'Com_Printf( "Scanning for servers on the local network...\\n");' in localservers_block
	assert 'message = "\\377\\377\\377\\377getinfo xxx";' in localservers_block
	assert "to.type = NA_BROADCAST;" in localservers_block
	assert "to.type = NA_BROADCAST_IPX;" in localservers_block

	assert 'Com_Printf( "usage: globalservers <master# 0-1> <protocol> [keywords]\\n");' in globalservers_block
	assert 'cls.masterNum = atoi( Cmd_Argv(1) );' in globalservers_block
	assert 'sprintf( command, "getservers %s", Cmd_Argv(2) );' in globalservers_block
	assert 'buffptr += sprintf( buffptr, " demo" );' in globalservers_block
	assert "NET_OutOfBandPrint( NS_SERVER, to, command );" in globalservers_block

	assert 'Com_Printf( "usage: ping [server]\\n");' in ping_block
	assert "pingptr = CL_GetFreePing();" in ping_block
	assert "CL_SetServerInfoByAddress(pingptr->adr, NULL, 0);" in ping_block
	assert 'NET_OutOfBandPrint( NS_CLIENT, to, "getinfo xxx" );' in ping_block

	assert 'Com_Printf( "Usage: serverstatus [server]\\n");' in serverstatus_block
	assert 'server = cls.servername;' in serverstatus_block
	assert 'NET_OutOfBandPrint( NS_CLIENT, to, "getstatus" );' in serverstatus_block
	assert "serverStatus->print = qtrue;" in serverstatus_block
	assert "serverStatus->pending = qtrue;" in serverstatus_block

	assert 'Cvar_Set( "web_browserActive", "1" );' in open_url_block

	assert 'CL_WebHost_NormalizeHash( hash, cl_webBrowserHash, sizeof( cl_webBrowserHash ) );' in show_browser_block
	assert "QLWebHost_NavigateOrOpen( cl_webBrowserHash );" in show_browser_block
	assert 'Cvar_Set( "web_browserActive", cl_webHost.browserActive ? "1" : "0" );' not in show_browser_block

	assert 'CL_WebHost_NormalizeHash( hash, cl_webBrowserHash, sizeof( cl_webBrowserHash ) );' in change_hash_block
	assert "QLWebHost_NavigateOrOpen( cl_webBrowserHash );" in change_hash_block
	assert 'Cvar_Set( "web_browserActive", cl_webHost.browserActive ? "1" : "0" );' not in change_hash_block

	assert 'if ( !cl_webHost.coreInitialised || !cl_webHost.viewInitialised || cl_webHost.keyCaptureArmed ) {' in hide_browser_block
	assert "cl_webBrowserVisible = qfalse;" in hide_browser_block
	assert 'Cvar_Set( "web_browserActive", "0" );' in hide_browser_block
	assert "VM_Call( cgvm, CG_EVENT_HANDLING, CGAME_EVENT_CLOSECOMMANDOVERLAY );" in hide_browser_block

	assert 'const char *message = ( Cmd_Argc() > 1 ) ? Cmd_Argv( 1 ) : "";' in show_error_block
	assert 'Cvar_Set( "com_errorMessage", message );' in show_error_block
	assert "CL_WebView_PublishGameError( message );" in show_error_block
	assert "QLWebHost_NavigateOrOpen( cl_webBrowserHash );" not in show_error_block
