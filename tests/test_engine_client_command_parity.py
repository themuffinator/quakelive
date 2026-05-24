from __future__ import annotations

import json
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
# `sub_4BB1A0` -> retail `showip` jump-stub owner for `CL_ShowIP_f`
# `sub_4B9070` -> `CL_OpenedPK3List_f`
# `sub_4B9090` -> `CL_ReferencedPK3List_f`
# `FUN_004D7980` -> retail no-op `userinfo` reservation owner
# `sub_4603F0` -> `CL_VoiceStartRecording_f`
# `sub_460490` -> `CL_VoiceStopRecording_f`
# `sub_460520` -> `CL_Steam_ClearStats_f`
# `sub_461500` -> `SteamClient_Init`
# `sub_460E60` -> `CL_Steam_OverlayCommand_f`
# `sub_464AA0` -> `CL_Steam_ConnectLobby_f`
# `sub_465840` -> `SteamLobby_Init`
# `sub_4B4F60` -> `centerview`
# `sub_4B4D80` / `sub_4B4D90` -> `+moveup` / `-moveup`
# `sub_4B4DA0` / `sub_4B4DB0` -> `+movedown` / `-movedown`
# `sub_4B4DC0` / `sub_4B4DD0` -> `+left` / `-left`
# `sub_4B4DE0` / `sub_4B4DF0` -> `+right` / `-right`
# `sub_4B4E00` / `sub_4B4E10` -> `+forward` / `-forward`
# `sub_4B4E20` / `sub_4B4E30` -> `+back` / `-back`
# `sub_4B4E40` / `sub_4B4E50` -> `+lookup` / `-lookup`
# `sub_4B4E60` / `sub_4B4E70` -> `+lookdown` / `-lookdown`
# `sub_4B4EE0` / `sub_4B4EF0` -> `+strafe` / `-strafe`
# `sub_4B4E80` -> `+moveleft`
# `sub_4B4E90` -> `-moveleft`
# `sub_4B4EA0` / `sub_4B4EB0` -> `+moveright` / `-moveright`
# `sub_4B4EC0` / `sub_4B4ED0` -> `+speed` / `-speed`
# `sub_4B4F00` / `sub_4B4F10` -> `+attack` / `-attack`
# `sub_4B4F20` / `sub_4B4F30` -> `+button2` / `-button2`
# `sub_4B4F40` / `sub_4B4F50` -> `+button3` / `-button3`
# `sub_4B4BD0` / `sub_4B6300` -> `+mlook` / `-mlook`
# `sub_4B4BE0` / `sub_4B4C60` -> retail key down / key up helpers
# `sub_4B5360` -> retail keyboard movement assembly helper
# `sub_4B9D10` -> `CL_SetModel_f`
# `004F3CD0` -> `QLWebHost_RegisterCommands`
# `004F3160` -> `web_showBrowser`
# `004F31D0` -> `web_changeHash`
# `004F24D0` -> `web_hideBrowser`
# `004F2A10` -> `CL_Web_ClearCache_f`
# `004F2A30` -> `CL_Web_Reload_f`
# `004F3CB0` -> `CL_Web_ShowError_f`


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
	assert 'Cmd_RemoveCommand ("postprocess_restart");' not in shutdown_block
	assert 'Cmd_RemoveCommand ("clientinfo");' not in shutdown_block
	assert 'Cmd_RemoveCommand ("reconnect");' not in shutdown_block


def test_usercmd_cgame_bridge_matches_retail_weapon_primary_and_fov_bytes() -> None:
	client_h = (REPO_ROOT / "src/code/client/client.h").read_text(encoding="utf-8")
	cl_input = (REPO_ROOT / "src/code/client/cl_input.c").read_text(encoding="utf-8")
	cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
	q_shared = (REPO_ROOT / "src/code/game/q_shared.h").read_text(encoding="utf-8")
	cg_local = (REPO_ROOT / "src/code/cgame/cg_local.h").read_text(encoding="utf-8")
	cg_syscalls = (REPO_ROOT / "src/code/cgame/cg_syscalls.c").read_text(encoding="utf-8")
	cg_view = (REPO_ROOT / "src/code/cgame/cg_view.c").read_text(encoding="utf-8")
	ql_imports = (REPO_ROOT / "src/code/client/ql_cgame_imports.inc").read_text(encoding="utf-8")

	usercmd_decl = q_shared[q_shared.index("typedef struct usercmd_s {") : q_shared.index("} usercmd_t;")]
	finish_move_block = _extract_function_block(cl_input, "void CL_FinishMove( usercmd_t *cmd ) {")
	set_value_block = _extract_function_block(
		cl_cgame,
		"void CL_SetUserCmdValue( int userCmdValue, int userCmdPrimary, float sensitivityScale, int userCmdFov ) {",
	)
	draw_active_block = _extract_function_block(
		cg_view,
		"void CG_DrawActiveFrame( int serverTime, stereoFrame_t stereoView, qboolean demoPlayback ) {",
	)

	assert "byte\t\t\tweapon;" in usercmd_decl
	assert "byte\t\t\tweaponPrimary;" in usercmd_decl
	assert "byte\t\t\tfov;" in usercmd_decl
	assert usercmd_decl.index("byte\t\t\tweapon;") < usercmd_decl.index("byte\t\t\tweaponPrimary;")
	assert usercmd_decl.index("byte\t\t\tweaponPrimary;") < usercmd_decl.index("byte\t\t\tfov;")
	assert usercmd_decl.index("byte\t\t\tfov;") < usercmd_decl.index("signed char\tforwardmove, rightmove, upmove;")

	assert "int\t\t\tcgameUserCmdValue;" in client_h
	assert "int\t\t\tcgameUserCmdPrimary;" in client_h
	assert "int\t\t\tcgameUserCmdFov;" in client_h
	assert "cl.cgameUserCmdPrimary = userCmdPrimary;" in set_value_block
	assert "cl.cgameUserCmdFov = userCmdFov;" in set_value_block
	assert "CL_SetUserCmdValue( args[1], args[2], VMF(3), args[4] );" in cl_cgame

	assert "cmd->weapon = cl.cgameUserCmdValue;" in finish_move_block
	assert "cmd->weaponPrimary = cl.cgameUserCmdPrimary;" in finish_move_block
	assert "cmd->fov = cl.cgameUserCmdFov;" in finish_move_block

	assert "void\t\ttrap_SetUserCmdValue( int stateValue, int primaryValue, float sensitivityScale, int fov );" in cg_local
	assert "syscall( CG_SETUSERCMDVALUE, stateValue, primaryValue, PASSFLOAT(sensitivityScale), fov );" in cg_syscalls
	assert "CG_Import_Syscall( CG_SETUSERCMDVALUE, stateValue, primaryValue, QL_CG_PASSFLOAT(sensitivityScale), fov );" in ql_imports
	assert "cg.userCmdFov = (int)fov_x;" in cg_view
	assert "cg.weaponPrimary = CG_StartingWeaponIndexFromToken( cg_weaponPrimaryQueued.string );" in draw_active_block
	assert "trap_SetUserCmdValue( cg.weaponSelect, cg.weaponPrimary, cg.zoomSensitivity, cg.userCmdFov );" in draw_active_block


def test_client_command_handlers_match_retail_forward_restart_and_info_contracts() -> None:
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
	aliases = json.loads(
		(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json").read_text(encoding="utf-8")
	)["quakelive_steam"]

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
	assert aliases["sub_4B9060"] == "CL_PostProcessRestart_f"

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

	assert aliases["sub_4BB1A0"] == "CL_ShowIP_f"
	assert "Sys_ShowIP();" in showip_block

	assert ";" not in userinfo_block


def test_client_input_command_registration_matches_retail_navigation_surface() -> None:
	cl_input = (REPO_ROOT / "src/code/client/cl_input.c").read_text(encoding="utf-8")
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

	init_input_block = _extract_function_block(cl_input, "void CL_InitInput( void ) {")
	init_block = _extract_function_block(cl_main, "void CL_Init( void ) {")

	command_lines = [
		'Cmd_AddCommand ("centerview",IN_CenterView);',
		'Cmd_AddCommand ("+moveup",IN_UpDown);',
		'Cmd_AddCommand ("-moveup",IN_UpUp);',
		'Cmd_AddCommand ("+movedown",IN_DownDown);',
		'Cmd_AddCommand ("-movedown",IN_DownUp);',
		'Cmd_AddCommand ("+left",IN_LeftDown);',
		'Cmd_AddCommand ("-left",IN_LeftUp);',
		'Cmd_AddCommand ("+right",IN_RightDown);',
		'Cmd_AddCommand ("-right",IN_RightUp);',
		'Cmd_AddCommand ("+forward",IN_ForwardDown);',
	]
	positions = []
	for command_line in command_lines:
		assert command_line in init_input_block
		positions.append(init_input_block.index(command_line))

	assert positions == sorted(positions)
	assert "CL_InitInput ();" in init_block


def test_client_input_navigation_commands_follow_retail_key_state_and_usercmd_path() -> None:
	cl_input = (REPO_ROOT / "src/code/client/cl_input.c").read_text(encoding="utf-8")

	keydown_block = _extract_function_block(cl_input, "void IN_KeyDown( kbutton_t *b ) {")
	keyup_block = _extract_function_block(cl_input, "void IN_KeyUp( kbutton_t *b ) {")
	key_state_block = _extract_function_block(cl_input, "float CL_KeyState( kbutton_t *key ) {")
	moveup_block = _extract_function_block(cl_input, "void IN_UpDown(void) {")
	moveup_up_block = _extract_function_block(cl_input, "void IN_UpUp(void) {")
	movedown_block = _extract_function_block(cl_input, "void IN_DownDown(void) {")
	movedown_up_block = _extract_function_block(cl_input, "void IN_DownUp(void) {")
	left_block = _extract_function_block(cl_input, "void IN_LeftDown(void) {")
	left_up_block = _extract_function_block(cl_input, "void IN_LeftUp(void) {")
	right_block = _extract_function_block(cl_input, "void IN_RightDown(void) {")
	right_up_block = _extract_function_block(cl_input, "void IN_RightUp(void) {")
	forward_block = _extract_function_block(cl_input, "void IN_ForwardDown(void) {")
	center_block = _extract_function_block(cl_input, "void IN_CenterView (void) {")
	adjust_block = _extract_function_block(cl_input, "void CL_AdjustAngles( void ) {")
	key_move_block = _extract_function_block(cl_input, "void CL_KeyMove( usercmd_t *cmd ) {")
	create_cmd_block = _extract_function_block(cl_input, "usercmd_t CL_CreateCmd( void ) {")

	assert 'k = -1;\t\t// typed manually at the console for continuous down' in keydown_block
	assert 'Com_Printf ("Three keys down for a button!\\n");' in keydown_block
	assert 'b->downtime = atoi(c);' in keydown_block
	assert 'b->active = qtrue;' in keydown_block
	assert 'b->wasPressed = qtrue;' in keydown_block

	assert 'b->down[0] = b->down[1] = 0;' in keyup_block
	assert 'b->msec += uptime - b->downtime;' in keyup_block
	assert 'b->msec += frame_msec / 2;' in keyup_block

	assert 'val = (float)msec / frame_msec;' in key_state_block
	assert 'if ( val > 1 ) {' in key_state_block

	assert 'IN_KeyDown(&in_up);' in moveup_block
	assert 'IN_KeyUp(&in_up);' in moveup_up_block
	assert 'IN_KeyDown(&in_down);' in movedown_block
	assert 'IN_KeyUp(&in_down);' in movedown_up_block
	assert 'IN_KeyDown(&in_left);' in left_block
	assert 'IN_KeyUp(&in_left);' in left_up_block
	assert 'IN_KeyDown(&in_right);' in right_block
	assert 'IN_KeyUp(&in_right);' in right_up_block
	assert 'IN_KeyDown(&in_forward);' in forward_block

	assert 'cl.viewangles[PITCH] = -SHORT2ANGLE(cl.snap.ps.delta_angles[PITCH]);' in center_block

	assert 'if ( !in_strafe.active ) {' in adjust_block
	assert 'cl.viewangles[YAW] -= speed*cl_yawspeed->value*CL_KeyState (&in_right);' in adjust_block
	assert 'cl.viewangles[YAW] += speed*cl_yawspeed->value*CL_KeyState (&in_left);' in adjust_block

	assert 'if ( in_speed.active ^ cl_run->integer ) {' in key_move_block
	assert 'cmd->buttons &= ~BUTTON_WALKING;' in key_move_block
	assert 'cmd->buttons |= BUTTON_WALKING;' in key_move_block
	assert 'if ( in_strafe.active ) {' in key_move_block
	assert 'side += movespeed * CL_KeyState (&in_right);' in key_move_block
	assert 'side -= movespeed * CL_KeyState (&in_left);' in key_move_block
	assert 'up += movespeed * CL_KeyState (&in_up);' in key_move_block
	assert 'up -= movespeed * CL_KeyState (&in_down);' in key_move_block
	assert 'forward += movespeed * CL_KeyState (&in_forward);' in key_move_block
	assert 'cmd->forwardmove = ClampChar( forward );' in key_move_block
	assert 'cmd->rightmove = ClampChar( side );' in key_move_block
	assert 'cmd->upmove = ClampChar( up );' in key_move_block

	assert "CL_AdjustAngles ();" in create_cmd_block
	assert "CL_KeyMove( &cmd );" in create_cmd_block


def test_client_input_command_registration_matches_retail_forward_pitch_strafe_surface() -> None:
	cl_input = (REPO_ROOT / "src/code/client/cl_input.c").read_text(encoding="utf-8")

	init_input_block = _extract_function_block(cl_input, "void CL_InitInput( void ) {")

	command_lines = [
		'Cmd_AddCommand ("-forward",IN_ForwardUp);',
		'Cmd_AddCommand ("+back",IN_BackDown);',
		'Cmd_AddCommand ("-back",IN_BackUp);',
		'Cmd_AddCommand ("+lookup", IN_LookupDown);',
		'Cmd_AddCommand ("-lookup", IN_LookupUp);',
		'Cmd_AddCommand ("+lookdown", IN_LookdownDown);',
		'Cmd_AddCommand ("-lookdown", IN_LookdownUp);',
		'Cmd_AddCommand ("+strafe", IN_StrafeDown);',
		'Cmd_AddCommand ("-strafe", IN_StrafeUp);',
		'Cmd_AddCommand ("+moveleft", IN_MoveleftDown);',
	]
	positions = []
	for command_line in command_lines:
		assert command_line in init_input_block
		positions.append(init_input_block.index(command_line))

	assert positions == sorted(positions)
	assert positions[0] > init_input_block.index('Cmd_AddCommand ("+forward",IN_ForwardDown);')
	assert positions[-1] < init_input_block.index('Cmd_AddCommand ("-moveleft", IN_MoveleftUp);')


def test_client_input_forward_pitch_strafe_commands_follow_retail_usercmd_path() -> None:
	cl_input = (REPO_ROOT / "src/code/client/cl_input.c").read_text(encoding="utf-8")

	forward_up_block = _extract_function_block(cl_input, "void IN_ForwardUp(void) {")
	back_block = _extract_function_block(cl_input, "void IN_BackDown(void) {")
	back_up_block = _extract_function_block(cl_input, "void IN_BackUp(void) {")
	lookup_block = _extract_function_block(cl_input, "void IN_LookupDown(void) {")
	lookup_up_block = _extract_function_block(cl_input, "void IN_LookupUp(void) {")
	lookdown_block = _extract_function_block(cl_input, "void IN_LookdownDown(void) {")
	lookdown_up_block = _extract_function_block(cl_input, "void IN_LookdownUp(void) {")
	strafe_block = _extract_function_block(cl_input, "void IN_StrafeDown(void) {")
	strafe_up_block = _extract_function_block(cl_input, "void IN_StrafeUp(void) {")
	moveleft_block = _extract_function_block(cl_input, "void IN_MoveleftDown(void) {")
	adjust_block = _extract_function_block(cl_input, "void CL_AdjustAngles( void ) {")
	key_move_block = _extract_function_block(cl_input, "void CL_KeyMove( usercmd_t *cmd ) {")

	assert 'IN_KeyUp(&in_forward);' in forward_up_block
	assert 'IN_KeyDown(&in_back);' in back_block
	assert 'IN_KeyUp(&in_back);' in back_up_block
	assert 'IN_KeyDown(&in_lookup);' in lookup_block
	assert 'IN_KeyUp(&in_lookup);' in lookup_up_block
	assert 'IN_KeyDown(&in_lookdown);' in lookdown_block
	assert 'IN_KeyUp(&in_lookdown);' in lookdown_up_block
	assert 'IN_KeyDown(&in_strafe);' in strafe_block
	assert 'IN_KeyUp(&in_strafe);' in strafe_up_block
	assert 'IN_KeyDown(&in_moveleft);' in moveleft_block

	assert 'cl.viewangles[PITCH] -= speed*cl_pitchspeed->value * CL_KeyState (&in_lookup);' in adjust_block
	assert 'cl.viewangles[PITCH] += speed*cl_pitchspeed->value * CL_KeyState (&in_lookdown);' in adjust_block

	assert 'if ( in_strafe.active ) {' in key_move_block
	assert 'side += movespeed * CL_KeyState (&in_right);' in key_move_block
	assert 'side -= movespeed * CL_KeyState (&in_left);' in key_move_block
	assert 'side -= movespeed * CL_KeyState (&in_moveleft);' in key_move_block
	assert 'forward -= movespeed * CL_KeyState (&in_back);' in key_move_block


def test_client_input_command_registration_matches_retail_movement_button_surface() -> None:
	cl_input = (REPO_ROOT / "src/code/client/cl_input.c").read_text(encoding="utf-8")

	init_input_block = _extract_function_block(cl_input, "void CL_InitInput( void ) {")

	command_lines = [
		'Cmd_AddCommand ("-moveleft", IN_MoveleftUp);',
		'Cmd_AddCommand ("+moveright", IN_MoverightDown);',
		'Cmd_AddCommand ("-moveright", IN_MoverightUp);',
		'Cmd_AddCommand ("+speed", IN_SpeedDown);',
		'Cmd_AddCommand ("-speed", IN_SpeedUp);',
		'Cmd_AddCommand ("+attack", IN_Button0Down);',
		'Cmd_AddCommand ("-attack", IN_Button0Up);',
		'Cmd_AddCommand ("+button2", IN_Button2Down);',
		'Cmd_AddCommand ("-button2", IN_Button2Up);',
		'Cmd_AddCommand ("+button3", IN_Button3Down);',
	]
	positions = []
	for command_line in command_lines:
		assert command_line in init_input_block
		positions.append(init_input_block.index(command_line))

	assert positions == sorted(positions)
	assert positions[0] > init_input_block.index('Cmd_AddCommand ("+moveleft", IN_MoveleftDown);')
	assert positions[-1] < init_input_block.index('Cmd_AddCommand ("-button3", IN_Button3Up);')


def test_client_input_movement_button_commands_follow_retail_speed_and_button_bit_path() -> None:
	cl_input = (REPO_ROOT / "src/code/client/cl_input.c").read_text(encoding="utf-8")

	moveleft_up_block = _extract_function_block(cl_input, "void IN_MoveleftUp(void) {")
	moveright_block = _extract_function_block(cl_input, "void IN_MoverightDown(void) {")
	moveright_up_block = _extract_function_block(cl_input, "void IN_MoverightUp(void) {")
	speed_block = _extract_function_block(cl_input, "void IN_SpeedDown(void) {")
	speed_up_block = _extract_function_block(cl_input, "void IN_SpeedUp(void) {")
	attack_block = _extract_function_block(cl_input, "void IN_Button0Down(void) {")
	attack_up_block = _extract_function_block(cl_input, "void IN_Button0Up(void) {")
	button2_block = _extract_function_block(cl_input, "void IN_Button2Down(void) {")
	button2_up_block = _extract_function_block(cl_input, "void IN_Button2Up(void) {")
	button3_block = _extract_function_block(cl_input, "void IN_Button3Down(void) {")
	key_move_block = _extract_function_block(cl_input, "void CL_KeyMove( usercmd_t *cmd ) {")
	cmd_buttons_block = _extract_function_block(cl_input, "void CL_CmdButtons( usercmd_t *cmd ) {")
	create_cmd_block = _extract_function_block(cl_input, "usercmd_t CL_CreateCmd( void ) {")

	assert 'IN_KeyUp(&in_moveleft);' in moveleft_up_block
	assert 'IN_KeyDown(&in_moveright);' in moveright_block
	assert 'IN_KeyUp(&in_moveright);' in moveright_up_block
	assert 'IN_KeyDown(&in_speed);' in speed_block
	assert 'IN_KeyUp(&in_speed);' in speed_up_block

	assert 'IN_KeyDown(&in_buttons[0]);' in attack_block
	assert 'IN_KeyUp(&in_buttons[0]);' in attack_up_block
	assert 'IN_KeyDown(&in_buttons[2]);' in button2_block
	assert 'IN_KeyUp(&in_buttons[2]);' in button2_up_block
	assert 'IN_KeyDown(&in_buttons[3]);' in button3_block

	assert 'if ( in_speed.active ^ cl_run->integer ) {' in key_move_block
	assert 'movespeed = 127;' in key_move_block
	assert 'movespeed = 64;' in key_move_block
	assert 'side += movespeed * CL_KeyState (&in_moveright);' in key_move_block
	assert 'side -= movespeed * CL_KeyState (&in_moveleft);' in key_move_block

	assert 'for (i = 0 ; i < 15 ; i++) {' in cmd_buttons_block
	assert 'cmd->buttons |= 1 << i;' in cmd_buttons_block
	assert 'in_buttons[i].wasPressed = qfalse;' in cmd_buttons_block
	assert 'cmd->buttons |= BUTTON_TALK;' in cmd_buttons_block
	assert 'cmd->buttons |= BUTTON_ANY;' in cmd_buttons_block

	assert "CL_CmdButtons( &cmd );" in create_cmd_block


def test_client_input_command_registration_matches_retail_button3_release_and_mlook_surface() -> None:
	cl_input = (REPO_ROOT / "src/code/client/cl_input.c").read_text(encoding="utf-8")

	init_input_block = _extract_function_block(cl_input, "void CL_InitInput( void ) {")

	command_lines = [
		'Cmd_AddCommand ("-button3", IN_Button3Up);',
		'Cmd_AddCommand ("+button4", IN_Button4Down);',
		'Cmd_AddCommand ("-button4", IN_Button4Up);',
		'Cmd_AddCommand ("+button14", IN_Button14Down);',
		'Cmd_AddCommand ("-button14", IN_Button14Up);',
		'Cmd_AddCommand ("+mlook", IN_MLookDown);',
		'Cmd_AddCommand ("-mlook", IN_MLookUp);',
	]
	positions = []
	for command_line in command_lines:
		assert command_line in init_input_block
		positions.append(init_input_block.index(command_line))

	assert positions == sorted(positions)
	assert positions[0] > init_input_block.index('Cmd_AddCommand ("+button3", IN_Button3Down);')
	assert positions[-1] < init_input_block.index('cl_nodelta = Cvar_Get ("cl_nodelta", "0", 0);')


def test_client_input_button3_release_and_mlook_follow_retail_mouse_and_joystick_path() -> None:
	cl_input = (REPO_ROOT / "src/code/client/cl_input.c").read_text(encoding="utf-8")

	button3_up_block = _extract_function_block(cl_input, "void IN_Button3Up(void) {")
	mlook_down_block = _extract_function_block(cl_input, "void IN_MLookDown( void ) {")
	mlook_up_block = _extract_function_block(cl_input, "void IN_MLookUp( void ) {")
	mouse_move_block = _extract_function_block(cl_input, "void CL_MouseMove( usercmd_t *cmd ) {")
	joystick_move_block = _extract_function_block(cl_input, "void CL_JoystickMove( usercmd_t *cmd ) {")

	assert 'IN_KeyUp(&in_buttons[3]);' in button3_up_block
	assert 'in_mlooking = qtrue;' in mlook_down_block
	assert 'in_mlooking = qfalse;' in mlook_up_block
	assert 'if ( !cl_freelook->integer ) {' in mlook_up_block
	assert 'IN_CenterView ();' in mlook_up_block

	assert 'if ( (in_mlooking || cl_freelook->integer) && !in_strafe.active ) {' in mouse_move_block
	assert 'cl.viewangles[PITCH] += m_pitch->value * mouseScale * my;' in mouse_move_block
	assert 'cl_viewAccel->value * m_pitch->value * my' not in mouse_move_block
	assert 'cmd->forwardmove = ClampChar( cmd->forwardmove - m_forward->value * my );' in mouse_move_block

	assert 'if ( in_mlooking ) {' in joystick_move_block
	assert 'cl.viewangles[PITCH] += anglespeed * cl_pitchspeed->value * cl.joystickAxis[AXIS_FORWARD];' in joystick_move_block
	assert 'cmd->forwardmove = ClampChar( cmd->forwardmove + cl.joystickAxis[AXIS_FORWARD] );' in joystick_move_block


def test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration() -> None:
	tr_public = (REPO_ROOT / "src/code/renderer/tr_public.h").read_text(encoding="utf-8")
	tr_init = (REPO_ROOT / "src/code/renderer/tr_init.c").read_text(encoding="utf-8")

	restart_block = _extract_function_block(tr_init, "static void R_PostProcessRestart( void ) {")
	register_block = _extract_function_block(tr_init, "void R_Register( void )")
	shutdown_block = _extract_function_block(tr_init, "void RE_Shutdown( qboolean destroyWindow ) {")
	api_block = _extract_function_block(tr_init, "refexport_t *GetRefAPI ( int apiVersion, refimport_t *rimp ) {")

	assert 'void\t(*PostProcessRestart)( void );' in tr_public
	assert "#define\tREF_API_VERSION\t\t9" in tr_public
	assert tr_public.index('(*SetColor)') < tr_public.index('(*PostProcessRestart)')
	assert "R_UpdatePostProcessCvars();" in restart_block
	assert "R_SyncRenderThread();" in restart_block
	assert "RB_ShutdownRenderTargets();" in restart_block
	assert "RB_InitRenderTargets();" in restart_block
	assert "R_SetColorMappings();" in restart_block
	assert api_block.index("re.SetColor = RE_SetColor;") < api_block.index("re.PostProcessRestart = R_PostProcessRestart;")
	assert "re.PostProcessRestart = R_PostProcessRestart;" in api_block
	assert 'ri.Cmd_AddCommand( "postprocess_restart", R_PostProcessRestart' not in register_block
	assert 'ri.Cmd_RemoveCommand( "postprocess_restart" );' not in shutdown_block


def test_client_steam_command_registration_and_identity_wiring_match_retail_surface() -> None:
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
	common = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")
	qcommon_h = (REPO_ROOT / "src/code/qcommon/qcommon.h").read_text(encoding="utf-8")
	aliases = json.loads(
		(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json").read_text(encoding="utf-8")
	)["quakelive_steam"]

	init_block = _extract_function_block(cl_main, "void CL_Init( void ) {")
	steam_client_init_block = _extract_function_block(cl_main, "void SteamClient_Init( void ) {")
	steam_callbacks_init_block = _extract_function_block(cl_main, "static qboolean SteamCallbacks_Init( void ) {")
	steam_micro_callbacks_init_block = _extract_function_block(cl_main, "static qboolean SteamMicroCallbacks_Init( void ) {")
	steam_lobby_callbacks_init_block = _extract_function_block(cl_main, "static qboolean SteamLobbyCallbacks_Init( void ) {")
	steam_lobby_init_block = _extract_function_block(cl_main, "static qboolean SteamLobby_Init( void ) {")
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
	assert 'Cmd_AddCommand ("+voice", CL_VoiceStartRecording_f );' not in init_block
	assert 'Cmd_AddCommand ("-voice", CL_VoiceStopRecording_f );' not in init_block
	assert 'Cmd_AddCommand ("connect_lobby", CL_Steam_ConnectLobby_f );' not in init_block
	assert 'Cmd_AddCommand ("clientviewprofile", CL_Steam_OverlayCommand_f );' in init_block
	assert 'Cmd_AddCommand ("clientfriendinvite", CL_Steam_OverlayCommand_f );' in init_block
	assert "QLWebHost_RegisterCommands();" in init_block
	assert "SteamClient_SyncPersonaNameCvar();" in init_block
	assert 'Cmd_AddCommand ("stats_clear", CL_Steam_ClearStats_f );' not in init_block
	assert init_block.index('Cmd_AddCommand ("clientviewprofile", CL_Steam_OverlayCommand_f );') < init_block.index("QLWebHost_RegisterCommands();")
	assert init_block.index('Cmd_AddCommand ("clientfriendinvite", CL_Steam_OverlayCommand_f );') < init_block.index("QLWebHost_RegisterCommands();")
	assert init_block.index("QLWebHost_RegisterCommands();") < init_block.index("SteamClient_SyncPersonaNameCvar();")
	assert 'Cmd_AddCommand ("+voice", CL_VoiceStartRecording_f );' in steam_client_init_block
	assert 'Cmd_AddCommand ("-voice", CL_VoiceStopRecording_f );' in steam_client_init_block
	assert 'Cmd_AddCommand ("stats_clear", CL_Steam_ClearStats_f );' in steam_client_init_block
	assert "SteamCallbacks_Init();" in steam_client_init_block
	assert "SteamMicroCallbacks_Init();" in steam_client_init_block
	assert "SteamLobby_Init();" in steam_client_init_block
	assert "CL_Steam_SetMainMenuRichPresence();" in steam_client_init_block
	assert "return QL_Steamworks_RegisterClientCallbacks( &clientBindings );" in steam_callbacks_init_block
	assert "return QL_Steamworks_RegisterMicroCallbacks( &microBindings );" in steam_micro_callbacks_init_block
	assert "return QL_Steamworks_RegisterLobbyCallbacks( &lobbyBindings );" in steam_lobby_callbacks_init_block
	assert "callbacksRegistered = SteamLobbyCallbacks_Init();" in steam_lobby_init_block
	assert 'Cvar_Get( "lobby_autoconnect", "", CVAR_TEMP );' in steam_lobby_init_block
	assert 'Cvar_Get( "steam_maxLobbyClients", "16", CVAR_ARCHIVE );' in steam_lobby_init_block
	assert 'Cmd_AddCommand ("connect_lobby", CL_Steam_ConnectLobby_f );' in steam_lobby_init_block
	assert "void SteamClient_Init( void );" in qcommon_h
	assert common.count( "SteamClient_Init();" ) == 1
	assert aliases["sub_4603F0"] == "CL_VoiceStartRecording_f"
	assert aliases["sub_460490"] == "CL_VoiceStopRecording_f"
	assert aliases["sub_460520"] == "CL_Steam_ClearStats_f"
	assert aliases["sub_460610"] == "SteamClient_SyncPersonaNameCvar"
	assert aliases["sub_461500"] == "SteamClient_Init"
	assert aliases["sub_460E60"] == "CL_Steam_OverlayCommand_f"
	assert aliases["sub_464AA0"] == "CL_Steam_ConnectLobby_f"
	assert aliases["sub_465840"] == "SteamLobby_Init"

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
	assert "if ( !QL_Steamworks_ActivateOverlayToUser( dialog, steamIdLow, steamIdHigh ) ) {" in overlay_block

	assert 'Cvar_Set( "lobby_autoconnect", Cmd_Argv( 1 ) );' in connect_lobby_block
	assert "if ( QL_Steamworks_GetAppID() != 0x54100u ) {" in stats_gate_block
	assert "return qtrue;" in stats_gate_block


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

	assert 'if ( !QL_Steamworks_ClearStats( qtrue ) ) {' in stats_block
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
	cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
	client_h = (REPO_ROOT / "src/code/client/client.h").read_text(encoding="utf-8")
	aliases = json.loads(
		(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json").read_text(encoding="utf-8")
	)["quakelive_steam"]

	init_block = _extract_function_block(cl_main, "void CL_Init( void ) {")
	shutdown_block = _extract_function_block(cl_main, "void CL_Shutdown( void ) {")
	register_block = _extract_function_block(cl_cgame, "void QLWebHost_RegisterCommands( void ) {")

	assert 'Cmd_AddCommand ("cinematic", CL_PlayCinematic_f);' not in init_block
	assert 'Cmd_AddCommand ("rcon", CL_Rcon_f);' not in init_block
	assert 'Cmd_AddCommand ("localservers", CL_LocalServers_f);' not in init_block
	assert 'Cmd_AddCommand ("globalservers", CL_GlobalServers_f);' not in init_block
	assert 'Cmd_AddCommand ("ping", CL_Ping_f );' not in init_block
	assert 'Cmd_AddCommand ("serverstatus", CL_ServerStatus_f );' not in init_block
	assert 'Cmd_AddCommand ("testy"' not in init_block
	assert 'Cmd_AddCommand ("joinqueue"' not in init_block
	assert 'Cmd_AddCommand ("leavequeue"' not in init_block
	assert 'Cmd_AddCommand ("advert_done"' not in init_block
	assert "QLWebHost_RegisterCommands();" in init_block
	assert 'Cmd_AddCommand ("web_showBrowser", CL_Web_ShowBrowser_f );' not in init_block
	assert 'Cmd_AddCommand ("web_changeHash", CL_Web_ChangeHash_f );' not in init_block
	assert 'Cmd_AddCommand ("web_hideBrowser", CL_Web_HideBrowser_f );' not in init_block
	assert 'Cmd_AddCommand ("web_showError", CL_Web_ShowError_f );' not in init_block
	assert 'Cmd_AddCommand ("web_clearCache", CL_Web_ClearCache_f );' not in init_block
	assert 'Cmd_AddCommand ("web_reload", CL_Web_Reload_f );' not in init_block
	assert 'Cmd_AddCommand ("localservers", CL_LocalServers_f );' in register_block
	assert 'Cmd_AddCommand ("globalservers", CL_GlobalServers_f );' in register_block
	assert 'Cmd_AddCommand ("web_showBrowser", CL_Web_ShowBrowser_f );' in register_block
	assert 'Cmd_AddCommand ("web_changeHash", CL_Web_ChangeHash_f );' in register_block
	assert 'Cmd_AddCommand ("web_hideBrowser", CL_Web_HideBrowser_f );' in register_block
	assert 'Cmd_AddCommand ("web_showError", CL_Web_ShowError_f );' in register_block
	assert 'Cmd_AddCommand ("web_clearCache", CL_Web_ClearCache_f );' in register_block
	assert 'Cmd_AddCommand ("web_reload", CL_Web_Reload_f );' in register_block
	assert 'Cvar_Get ("web_zoom", "100", CVAR_ARCHIVE );' in register_block
	assert 'Cvar_Get ("web_console", "0", CVAR_ARCHIVE );' in register_block
	assert 'Cvar_Get ("web_browserActive", "0", CVAR_ROM );' in register_block
	assert aliases["sub_4F3CD0"] == "QLWebHost_RegisterCommands"

	assert 'Cmd_RemoveCommand ("cinematic");' in shutdown_block
	assert 'Cmd_RemoveCommand ("localservers");' in shutdown_block
	assert 'Cmd_RemoveCommand ("globalservers");' in shutdown_block
	assert 'Cmd_RemoveCommand ("ping");' in shutdown_block
	assert 'Cmd_RemoveCommand ("rcon");' not in shutdown_block
	assert 'Cmd_RemoveCommand ("serverstatus");' not in shutdown_block
	assert 'Cmd_RemoveCommand ("testy");' in shutdown_block
	assert 'Cmd_RemoveCommand ("joinqueue");' in shutdown_block
	assert 'Cmd_RemoveCommand ("leavequeue");' in shutdown_block
	assert 'Cmd_RemoveCommand ("advert_done");' in shutdown_block
	assert 'Cmd_RemoveCommand ("web_showBrowser");' not in shutdown_block
	assert 'Cmd_RemoveCommand ("web_changeHash");' not in shutdown_block
	assert 'Cmd_RemoveCommand ("web_hideBrowser");' not in shutdown_block
	assert 'Cmd_RemoveCommand ("web_showError");' not in shutdown_block
	assert 'Cmd_RemoveCommand ("web_clearCache");' not in shutdown_block
	assert 'Cmd_RemoveCommand ("web_reload");' not in shutdown_block

	assert 'Cmd_AddCommand ("togglemenu", CL_ToggleMenu_f );' not in init_block
	assert 'Cmd_AddCommand ("web_browserActive", CL_Web_BrowserActive_f );' not in init_block
	assert 'Cmd_AddCommand ("web_stopRefresh", CL_Web_StopRefresh_f );' not in init_block
	assert 'Cmd_RemoveCommand ("togglemenu");' not in shutdown_block
	assert 'Cmd_RemoveCommand ("web_browserActive");' not in shutdown_block
	assert 'Cmd_RemoveCommand ("web_stopRefresh");' not in shutdown_block

	assert "void CL_LocalServers_f( void );" in client_h
	assert "void CL_GlobalServers_f( void );" in client_h
	assert "void\tCL_Ping_f( void );" not in client_h
	assert "void QLWebHost_RegisterCommands( void );" in client_h


def test_client_key_event_matches_retail_demo_playback_controls() -> None:
	cl_keys = (REPO_ROOT / "src/code/client/cl_keys.c").read_text(encoding="utf-8")

	demo_block = _extract_function_block(
		cl_keys, "static qboolean CL_HandleDemoPlaybackKeyEvent( int key ) {"
	)
	key_event_block = _extract_function_block(cl_keys, "void CL_KeyEvent (int key, qboolean down, unsigned time) {")

	assert "if ( !clc.demoplaying || ( cls.keyCatchers & ~KEYCATCH_RETAIL_MOUSEPASS ) != 0 ) {" in demo_block
	assert "case K_SPACE:" in demo_block
	assert 'Cbuf_ExecuteText( EXEC_APPEND, "toggle cl_freezeDemo\\n" );' in demo_block
	assert "case K_DOWNARROW:" in demo_block
	assert "case K_MOUSE3:" in demo_block
	assert 'Cbuf_ExecuteText( EXEC_APPEND, "timescale 1\\n" );' in demo_block
	assert "case K_LEFTARROW:" in demo_block
	assert "case K_MWHEELDOWN:" in demo_block
	assert 'Cbuf_ExecuteText( EXEC_APPEND, "cvarAdd timescale -0.1\\n" );' in demo_block
	assert "case K_RIGHTARROW:" in demo_block
	assert "case K_MWHEELUP:" in demo_block
	assert "if ( cl_freezeDemo && cl_freezeDemo->integer ) {" in demo_block
	assert 'Cbuf_ExecuteText( EXEC_APPEND, "timescale 1; cl_freezeDemo 0; wait; wait; cl_freezeDemo 1\\n" );' in demo_block
	assert 'Cbuf_ExecuteText( EXEC_APPEND, "cvarAdd timescale 0.1\\n" );' in demo_block
	assert "case K_DEL:" in demo_block
	assert 'Cbuf_ExecuteText( EXEC_APPEND, "toggle cg_drawDemoHUD\\n" );' in demo_block

	assert "if ( dispatchDown && CL_HandleDemoPlaybackKeyEvent( key ) ) {" in key_event_block
	assert "clc.demoplaying || cls.state == CA_CINEMATIC" not in key_event_block


def test_client_command_handlers_match_retail_cinematic_network_and_browser_contracts() -> None:
	cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
	cl_cin = (REPO_ROOT / "src/code/client/cl_cin.c").read_text(encoding="utf-8")
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
	aliases = json.loads(
		(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json").read_text(encoding="utf-8")
	)["quakelive_steam"]

	play_cinematic_block = _extract_function_block(cl_cin, "void CL_PlayCinematic_f(void) {")
	request_local_block = _extract_function_block(cl_main, "static void CL_RequestLocalServers( void ) {")
	request_global_block = _extract_function_block(cl_main, "static void CL_RequestGlobalServers( int masterNum, const char *protocol, const char *keywords ) {")
	local_servers_block = _extract_function_block(cl_main, "void CL_LocalServers_f( void ) {")
	global_servers_block = _extract_function_block(cl_main, "void CL_GlobalServers_f( void ) {")
	request_servers_block = _extract_function_block(cl_main, "qboolean CL_Steam_RequestServers( int requestMode ) {")
	open_url_block = _extract_function_block(cl_cgame, "static qboolean QLWebHost_OpenURL( const char *url ) {")
	show_browser_block = _extract_function_block(cl_cgame, "void CL_Web_ShowBrowser_f( void ) {")
	change_hash_block = _extract_function_block(cl_cgame, "void CL_Web_ChangeHash_f( void ) {")
	hide_browser_block = _extract_function_block(cl_cgame, "static void QLWebHost_HideBrowser( void ) {")
	show_error_block = _extract_function_block(cl_cgame, "void CL_Web_ShowError_f( void ) {")
	clear_cache_block = _extract_function_block(cl_cgame, "void CL_Web_ClearCache_f( void ) {")
	reload_block = _extract_function_block(cl_cgame, "void CL_Web_Reload_f( void ) {")

	assert 'if ((s && s[0] == \'1\') || Q_stricmp(arg,"demoend.roq")==0 || Q_stricmp(arg,"end.roq")==0) {' in play_cinematic_block
	assert "S_StopAllSounds ();" in play_cinematic_block
	assert "CL_handle = CIN_PlayCinematic( arg, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, bits );" in play_cinematic_block

	assert 'Com_Printf( "Scanning for servers on the local network...\\n");' in request_local_block
	assert 'message = "\\377\\377\\377\\377getinfo xxx";' in request_local_block
	assert "to.type = NA_BROADCAST;" in request_local_block
	assert "to.type = NA_BROADCAST_IPX;" not in request_local_block

	assert "cls.masterNum = masterNum;" in request_global_block
	assert 'Com_sprintf( command, sizeof( command ), "getservers %s", protocol );' in request_global_block
	assert 'Q_strcat( command, sizeof( command ), " " );' in request_global_block
	assert 'Q_strcat( command, sizeof( command ), keywords );' in request_global_block
	assert 'Q_strcat( command, sizeof( command ), " demo" );' in request_global_block
	assert "NET_OutOfBandPrint( NS_SERVER, to, command );" in request_global_block

	assert "CL_RequestLocalServers();" in request_servers_block
	assert 'CL_RequestGlobalServers( masterNum, debugProtocol, "full empty" );' in request_servers_block
	assert 'CL_RequestGlobalServers( masterNum, va( "%d", protocol ), "full empty" );' in request_servers_block
	assert "void CL_Rcon_f( void ) {" not in cl_main
	assert "void CL_Ping_f( void ) {" not in cl_main
	assert "void CL_ServerStatus_f(void) {" not in cl_main
	assert "CL_RequestLocalServers();" in local_servers_block
	assert "argc = Cmd_Argc();" in global_servers_block
	assert "masterNum = atoi( Cmd_Argv( 1 ) );" in global_servers_block
	assert 'keywords = ( argc > 3 ) ? Cmd_ArgsFrom( 3 ) : "";' in global_servers_block
	assert "CL_RequestGlobalServers( masterNum, protocol, keywords );" in global_servers_block

	assert 'Cvar_Get ("rconPassword", "", CVAR_TEMP );' not in cl_main
	assert 'Cvar_Get ("rconAddress", "", 0);' not in cl_main

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
	assert aliases["sub_4F3CB0"] == "CL_Web_ShowError_f"

	assert 'if ( !cl_webHost.sessionInitialised ) {' in clear_cache_block
	assert "CL_Web_ClearSessionState();" in clear_cache_block
	assert 'Com_DPrintf( "web_clearCache\\n" );' not in clear_cache_block
	assert aliases["sub_4F2A10"] == "CL_Web_ClearCache_f"

	assert 'if ( !cl_webHost.viewInitialised ) {' in reload_block
	assert "CL_Web_ClearSessionState();" in reload_block
	assert "QLWebHost_ReloadView( qtrue );" in reload_block
	assert 'Cvar_Set( "web_browserActive", cl_webHost.browserActive ? "1" : "0" );' not in reload_block
	assert "CL_RefreshOnlineServicesBridgeState();" not in reload_block
	assert "QLWebHost_NavigateOrOpen( cl_webBrowserHash );" not in reload_block
	assert aliases["sub_4F2A30"] == "CL_Web_Reload_f"


def test_client_cgame_native_bridge_mapping_round_275_promotes_hlil_backed_symbols() -> None:
	aliases = json.loads(
		(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json").read_text(encoding="utf-8")
	)["quakelive_steam"]
	host_hlil = (
		REPO_ROOT
		/ "references"
		/ "hlil"
		/ "quakelive"
		/ "quakelive_steam.exe"
		/ "quakelive_steam.exe_hlil.txt"
	).read_text(encoding="utf-8")
	cgame_hlil = (
		REPO_ROOT
		/ "references"
		/ "hlil"
		/ "quakelive"
		/ "cgamex86.dll"
		/ "cgamex86.dll_hlil.txt"
	).read_text(encoding="utf-8")
	ghidra_functions = (
		REPO_ROOT / "references/reverse-engineering/ghidra/quakelive_steam/functions.csv"
	).read_text(encoding="utf-8")
	cg_public = (REPO_ROOT / "src/code/cgame/cg_public.h").read_text(encoding="utf-8")
	cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
	mapping_round = (
		REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_275.md"
	).read_text(encoding="utf-8")

	expected_aliases = {
		"sub_4B03B0": "QLCGImport_PublishTaggedInfoString",
		"sub_4B03C0": "QLCGImport_R_MirrorPoint",
		"sub_4B03D0": "QLCGImport_R_MirrorVector",
		"sub_4B0460": "CL_LoadCGameForCvarRegistration",
		"sub_4B04C0": "CL_InitCGame",
		"sub_4B0610": "CL_GameCommand",
		"sub_4B0630": "CL_CGameRendering",
		"sub_4B0660": "CL_AdjustServerTimeDelta",
		"sub_4B0760": "CL_FirstSnapshot",
		"sub_4B07C0": "CL_SetCGameTime",
		"sub_4BF5D0": "QLWebView_PublishTaggedInfoString",
		"sub_4EC6D0": "QLWebView_InvokeCommNoticeThunk",
		"sub_4F2950": "QLWebView_InvokeCommNotice",
	}

	for address, normalized_name in expected_aliases.items():
		assert aliases[address] == normalized_name

	for expected_row in (
		"FUN_004b03b0,004b03b0,9,0,unknown",
		"FUN_004b03c0,004b03c0,10,0,unknown",
		"FUN_004b03d0,004b03d0,10,0,unknown",
		"FUN_004b0460,004b0460,87,0,unknown",
		"FUN_004b04c0,004b04c0,321,0,unknown",
		"FUN_004b0610,004b0610,22,0,unknown",
		"FUN_004b0630,004b0630,35,0,unknown",
		"FUN_004b0660,004b0660,255,0,unknown",
		"FUN_004b0760,004b0760,92,0,unknown",
		"FUN_004bf5d0,004bf5d0,312,0,unknown",
		"FUN_004ec6d0,004ec6d0,9,0,unknown",
	):
		assert expected_row in ghidra_functions

	for expected in (
		"004b03b4  return sub_4bf5d0() __tailcall",
		"004b03c4  jump(data_146cce8)",
		"004b03d4  jump(data_146ccec)",
		'004b047e  void* result = sub_4e9ff0("cgame", &data_146cc38, &data_565958, &var_8)',
		'004b0523  void* eax_4 = sub_4e9ff0("cgame", &data_146cc38, &data_565958, &var_8)',
		"004b0624      jump(*(data_146cc38 + 0xc))",
		"004b0652  return (*(data_146cc38 + 0x10))(data_146cfbc, arg1, data_16177e0)",
		"004b0767  if ((data_146cd28 & 2) != 0",
		'004bf60b  sub_429440(sub_42a110(&var_838, "MSG_TYPE"), arg1)',
		"004bf635          sub_4d9380(&var_828, &var_408, &var_808)",
		"004bf6b5  sub_4ec6d0()",
		"004ec6d4  return sub_4f2950() __tailcall",
		'004f29e0          char* eax_5 = sub_4314d0(&var_10, "OnCommNotice")',
	):
		assert expected in host_hlil

	for expected in (
		'10048931  (*(data_1074cccc + 0x1d0))("serverinfo", data_10a38420 + 0x10a39420)',
		'10049440  (*(data_1074cccc + 0x1d0))("serverinfo", data_10a38420 + 0x10a39420)',
		"10011794                  (*(data_1074cccc + 0x1e0))(&var_64, &var_38, &var_48)",
		"100117b4                  (*(data_1074cccc + 0x1e4))(&var_48, &var_28, &var_58)",
	):
		assert expected in cgame_hlil

	for expected in (
		"CG_QL_IMPORT_TAGGED_CVAR_STRING_BUFFER = 116,",
		"CG_QL_IMPORT_R_MIRROR_POINT = 120,",
		"CG_QL_IMPORT_R_MIRROR_VECTOR = 121,",
		"ql_cgame_imports[CG_QL_IMPORT_TAGGED_CVAR_STRING_BUFFER] = (ql_import_f)QL_CG_trap_TaggedCvarStringBuffer;",
		"ql_cgame_imports[CG_QL_IMPORT_R_MIRROR_POINT] = (ql_import_f)QL_CG_trap_R_MirrorPoint;",
		"ql_cgame_imports[CG_QL_IMPORT_R_MIRROR_VECTOR] = (ql_import_f)QL_CG_trap_R_MirrorVector;",
	):
		assert expected in cg_public or expected in cl_cgame

	for expected in (
		"# Quake Live Steam Host Mapping Round 275",
		"| `sub_4B03B0` | `QLCGImport_PublishTaggedInfoString` |",
		"| `sub_4B04C0` | `CL_InitCGame` |",
		"| `sub_4BF5D0` | `QLWebView_PublishTaggedInfoString` |",
	):
		assert expected in mapping_round


def test_client_input_mapping_round_277_promotes_console_input_and_usercmd_symbols() -> None:
	aliases = json.loads(
		(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json").read_text(encoding="utf-8")
	)["quakelive_steam"]
	host_hlil = (
		REPO_ROOT
		/ "references"
		/ "hlil"
		/ "quakelive"
		/ "quakelive_steam.exe"
		/ "quakelive_steam.exe_hlil.txt"
	).read_text(encoding="utf-8")
	ghidra_functions = (
		REPO_ROOT / "references/reverse-engineering/ghidra/quakelive_steam/functions.csv"
	).read_text(encoding="utf-8")
	cl_input = (REPO_ROOT / "src/code/client/cl_input.c").read_text(encoding="utf-8")
	mapping_round = (
		REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_277.md"
	).read_text(encoding="utf-8")

	expected_aliases = {
		"sub_4B4A30": "Con_Init",
		"sub_4B4BD0": "IN_MLookDown",
		"sub_4B4BE0": "IN_KeyDown",
		"sub_4B4C60": "IN_KeyUp",
		"sub_4B4CF0": "CL_KeyState",
		"sub_4B4D80": "IN_UpDown",
		"sub_4B4D90": "IN_UpUp",
		"sub_4B4DA0": "IN_DownDown",
		"sub_4B4DB0": "IN_DownUp",
		"sub_4B4DC0": "IN_LeftDown",
		"sub_4B4DD0": "IN_LeftUp",
		"sub_4B4DE0": "IN_RightDown",
		"sub_4B4DF0": "IN_RightUp",
		"sub_4B4E00": "IN_ForwardDown",
		"sub_4B4E10": "IN_ForwardUp",
		"sub_4B4E20": "IN_BackDown",
		"sub_4B4E30": "IN_BackUp",
		"sub_4B4E40": "IN_LookupDown",
		"sub_4B4E50": "IN_LookupUp",
		"sub_4B4E60": "IN_LookdownDown",
		"sub_4B4E70": "IN_LookdownUp",
		"sub_4B4E80": "IN_MoveleftDown",
		"sub_4B4E90": "IN_MoveleftUp",
		"sub_4B4EA0": "IN_MoverightDown",
		"sub_4B4EB0": "IN_MoverightUp",
		"sub_4B4EC0": "IN_SpeedDown",
		"sub_4B4ED0": "IN_SpeedUp",
		"sub_4B4EE0": "IN_StrafeDown",
		"sub_4B4EF0": "IN_StrafeUp",
		"sub_4B4F00": "IN_Button0Down",
		"sub_4B4F10": "IN_Button0Up",
		"sub_4B4F20": "IN_Button2Down",
		"sub_4B4F30": "IN_Button2Up",
		"sub_4B4F40": "IN_Button3Down",
		"sub_4B4F50": "IN_Button3Up",
		"sub_4B4F60": "IN_CenterView",
		"sub_4B5290": "CL_AdjustAngles",
		"sub_4B5360": "CL_KeyMove",
		"sub_4B5570": "CL_JoystickEvent",
		"sub_4B55B0": "CL_JoystickMove",
		"sub_4B5640": "CL_BeginMouseFilter",
		"sub_4B5710": "CL_EndMouseFilter",
		"sub_4B5BD0": "CL_CmdButtons",
		"sub_4B5C70": "CL_CreateCmd",
		"sub_4B5DE0": "CL_CreateNewCommands",
		"sub_4B5E60": "CL_ReadyToSendPacket",
		"sub_4B62A0": "CL_SendCmd",
		"sub_4B6300": "IN_MLookUp",
		"sub_4B6330": "CL_InitInput",
	}

	for address, normalized_name in expected_aliases.items():
		assert aliases[address] == normalized_name

	for expected_row in (
		"FUN_004b4a30,004b4a30,408,0,unknown",
		"FUN_004b4be0,004b4be0,125,0,unknown",
		"FUN_004b4c60,004b4c60,130,0,unknown",
		"FUN_004b4cf0,004b4cf0,136,0,unknown",
		"FUN_004b5290,004b5290,203,0,unknown",
		"FUN_004b5360,004b5360,381,0,unknown",
		"FUN_004b5570,004b5570,58,0,unknown",
		"FUN_004b55b0,004b55b0,139,0,unknown",
		"FUN_004b5640,004b5640,197,0,unknown",
		"FUN_004b5710,004b5710,236,0,unknown",
		"FUN_004b5bd0,004b5bd0,160,0,unknown",
		"FUN_004b5c70,004b5c70,364,0,unknown",
		"FUN_004b5de0,004b5de0,118,0,unknown",
		"FUN_004b5e60,004b5e60,265,0,unknown",
		"FUN_004b62a0,004b62a0,88,0,unknown",
		"FUN_004b6330,004b6330,570,0,unknown",
	):
		assert expected_row in ghidra_functions

	for expected in (
		'004b4a68      sub_4cdd30(x87_r0, x87_r1, x87_r2, "con_background", U"0", U"0", U"1", 0x81800)',
		'004b4b73  sub_4c81d0("toggleconsole", sub_4b49d0)',
		'004b4c51                  return sub_4c9860(arg1, "Three keys down for a button!\\n")',
		"004b4cd7      arg1[1] = 0",
		"004b4d47  long double x87_r6_1 = fconvert.t(fconvert.s(float.t(arg1) / x87_r6))",
		"004b4d8b  return sub_4b4be0(&data_164af20)",
		"004b4d9b  return sub_4b4c60(&data_164af20)",
		"004b52a3  long double x87_r7_1 = float.t(data_1528cc4) * fconvert.t(0.001)",
		"004b5366  int32_t result = sub_4f22e0()",
		"004b557e  if (arg1 s>= 0 && arg1 s< 6)",
		'004b5588  sub_4c9b60(1, "CL_JoystickEvent: bad axis %i")',
		"004b5629          data_1471ea4 = 0",
		"004b564c  if (result != 0)",
		"004b571f  if (*(result + 0x30) != 0)",
		"004b5c43  for (void* i = &data_164af74; i s< 0x164b0dc; )",
		"004b5c89  sub_4b5290()",
		"004b5ca2  sub_4b5360(arg1)",
		"004b5ca8  sub_4b5800(arg1)",
		"004b5cae  sub_4b55b0(arg1)",
		"004b5ded  if (data_1528ba0 s>= 7)",
		'004b5f28                          sub_4cd250("cl_maxpackets", "125")',
		"004b62cc      sub_4b5de0()",
		"004b62f3          return sub_4b5f70(esi) __tailcall",
		"004b6305  data_165d59c = 0",
		'004b633a  sub_4c81d0("centerview", sub_4b4f60)',
		'004b64ba  sub_4c81d0("+attack", sub_4b4f00)',
		'004b6514  sub_4c81d0("+mlook", sub_4b4bd0)',
		'004b6526  sub_4c81d0("-mlook", sub_4b6300)',
		'004b6535  sub_4c81d0("ListInputDevices", sub_4eab90)',
		'004b6557  data_146ccfc = sub_4ce0d0(x87_r0, "cl_nodelta", U"0", 0)',
		'004b655c  void** result = sub_4ce0d0(x87_r2, "cl_debugMove", U"0", 0)',
	):
		assert expected in host_hlil

	finish_move_block = _extract_function_block(cl_input, "void CL_FinishMove( usercmd_t *cmd ) {")
	create_cmd_block = _extract_function_block(cl_input, "usercmd_t CL_CreateCmd( void ) {")
	assert "CL_FinishMove( &cmd );" in create_cmd_block
	assert "cmd->serverTime = cl.serverTime;" in finish_move_block
	assert "cmd->angles[i] = ANGLE2SHORT(cl.viewangles[i]);" in finish_move_block

	for expected in (
		"# Quake Live Steam Host Mapping Round 277",
		"| `sub_4B4A30` | `Con_Init` |",
		"| `sub_4B4BE0` | `IN_KeyDown` |",
		"| `sub_4B5C70` | `CL_CreateCmd` |",
		"| `sub_4B62A0` | `CL_SendCmd` |",
		"Retail `0x004B5C70` appears to inline the final move storage",
		"Higher `+button4` through `+button14` source registrations remain a",
	):
		assert expected in mapping_round


def test_client_parse_screen_ui_mapping_round_280_promotes_hlil_backed_symbols() -> None:
	aliases = json.loads(
		(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json").read_text(encoding="utf-8")
	)["quakelive_steam"]
	host_hlil = (
		REPO_ROOT
		/ "references"
		/ "hlil"
		/ "quakelive"
		/ "quakelive_steam.exe"
		/ "quakelive_steam.exe_hlil.txt"
	).read_text(encoding="utf-8")
	ghidra_functions = (
		REPO_ROOT / "references/reverse-engineering/ghidra/quakelive_steam/functions.csv"
	).read_text(encoding="utf-8")
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
	cl_net_chan = (REPO_ROOT / "src/code/client/cl_net_chan.c").read_text(encoding="utf-8")
	cl_parse = (REPO_ROOT / "src/code/client/cl_parse.c").read_text(encoding="utf-8")
	cl_scrn = (REPO_ROOT / "src/code/client/cl_scrn.c").read_text(encoding="utf-8")
	cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")
	mapping_round = (
		REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_280.md"
	).read_text(encoding="utf-8")

	expected_aliases = {
		"sub_4BC320": "CL_Workshop_Frame",
		"sub_4BCE30": "CL_Netchan_Encode",
		"sub_4BCEF0": "CL_Netchan_Decode",
		"sub_4BCF80": "CL_Netchan_TransmitNextFragment",
		"sub_4BCF90": "CL_Netchan_Transmit",
		"sub_4BCFC0": "CL_Netchan_Process",
		"sub_4BD620": "CL_SystemInfoChanged",
		"sub_4BDA00": "CL_ParseServerMessage",
		"sub_4BDB90": "SCR_AdjustFrom640",
		"sub_4BDC00": "SCR_FillRect",
		"sub_4BDCB0": "SCR_DrawPic",
		"sub_4BDEB0": "SCR_DrawDemoRecording",
		"sub_4BE040": "SCR_DebugGraph",
		"sub_4BE080": "SCR_Init",
		"sub_4BE3A0": "SCR_UpdateScreen",
		"sub_4BE460": "CL_GetClientState",
		"sub_4BE4C0": "LAN_ResetPings",
		"sub_4BE520": "LAN_AddServer",
		"sub_4BE6B0": "LAN_RemoveServer",
		"sub_4BE7F0": "LAN_GetServerAddressString",
		"sub_4BEB00": "LAN_GetServerPing",
		"sub_4BEB80": "LAN_CompareServers",
		"sub_4BED10": "LAN_MarkServerVisible",
		"sub_4BEDE0": "LAN_ServerIsVisible",
	}

	for address, normalized_name in expected_aliases.items():
		assert aliases[address] == normalized_name

	for expected_row in (
		"FUN_004bc320,004bc320,187,0,unknown",
		"FUN_004bce30,004bce30,173,0,unknown",
		"FUN_004bcef0,004bcef0,140,0,unknown",
		"FUN_004bcf80,004bcf80,9,0,unknown",
		"FUN_004bcf90,004bcf90,43,0,unknown",
		"FUN_004bcfc0,004bcfc0,49,0,unknown",
		"FUN_004bd620,004bd620,360,0,unknown",
		"FUN_004bda00,004bda00,367,0,unknown",
		"FUN_004bdb90,004bdb90,108,0,unknown",
		"FUN_004bdc00,004bdc00,163,0,unknown",
		"FUN_004bdcb0,004bdcb0,141,0,unknown",
		"FUN_004bdeb0,004bdeb0,392,0,unknown",
		"FUN_004be040,004be040,49,0,unknown",
		"FUN_004be080,004be080,139,0,unknown",
		"FUN_004be3a0,004be3a0,184,0,unknown",
		"FUN_004be460,004be460,92,0,unknown",
		"FUN_004be4c0,004be4c0,79,0,unknown",
		"FUN_004be520,004be520,377,0,unknown",
		"FUN_004be6b0,004be6b0,297,0,unknown",
		"FUN_004be7f0,004be7f0,145,0,unknown",
		"FUN_004beb00,004beb00,99,0,unknown",
		"FUN_004beb80,004beb80,347,0,unknown",
		"FUN_004bed10,004bed10,163,0,unknown",
		"FUN_004bede0,004bede0,15,0,unknown",
	):
		assert expected_row in ghidra_functions

	for expected in (
		'004bc392          sub_4c9ab0("Steamworks downloads complete\\n")',
		"004bce5a      char eax_2 = sub_4d5020(arg1)",
		"004bce8f      int32_t eax = ((eax_4 & 0x3f) << 0xa) + 0x1606b88",
		"004bcf2b  result.b = *edx",
		"004bcf84  return sub_4d7370() __tailcall",
		"004bcf9a  sub_4d4dc0(arg2, 5)",
		"004bcfba  return sub_4d74e0(arg1, arg2[4], arg2[2])",
		"004bcfcc  int32_t result = sub_4d7640(&__saved_ebp, arg2, edi, arg1, arg2)",
		"004bcfdb  sub_4bcef0(arg2)",
		'004bd657  int32_t result = atoi(sub_4d9260(i_2, "sv_serverid"))',
		'004bd69f      i = sub_4d9260(i_2, "sv_paks")',
		"004bda3b  sub_4d4a70(arg1)",
		"004bdb04                      sub_4bd790(arg1)",
		"004bdb0f                      sub_4bd350(arg1)",
		'0053f4c8  char const data_53f4c8[0x37] = "CL_ParseServerMessage: read past end of server message", 0',
		'0053f500  char const data_53f500[0x34] = "CL_ParseServerMessage: Illegible server message %d\\n", 0',
		"004bdbb4  float var_c = fconvert.s(float.t(data_15ee344) / fconvert.t(480.0))",
		"004bdc0a  data_146cca4(arg5)",
		"004bdcc9  float var_8 = fconvert.s(float.t(data_15ee340) / fconvert.t(640.0))",
		'004bdfdd              sprintf(&var_408, "RECORDING %s: %ik", 0x1617798, ',
		"004be043  int32_t ecx = data_114e14c",
		'004be0a3  data_146cc2c = sub_4ce0d0(x87_r0, "timegraph", U"0", 0x200)',
		'0053f5f0  char const data_53f5f0[0x25] = "SCR_UpdateScreen: recursively called", 0',
		"004be40e          sub_4be110(0)",
		"004be46a  arg1[1] = data_15f6768",
		"004be500              *arg1 = 0xffffffff",
		"004be643          sub_4d8f40(*esi_1 * 0xac + var_20_1 + 0x14, arg4, 0x28)",
		"004be7b0                  eax_2 = sub_4cb7d0(edi_2, edi_2 + 0xac, 0xac)",
		"004be832              sub_4d6dd0(*eax_1, *(eax_1 + 4), *(eax_1 + 8), *(eax_1 + 0xc), ",
		'004be950          sub_4d9620(&var_408, "hostname", esi_2 + 0x14)',
		"004beb5e                  return *(eax_1 + 0xa4)",
		"004bed52                  *eax = arg2",
		"004bed74                  *(arg1 * 0xac + 0x1528d7c) = arg2",
		"004bee38  return 0",
	):
		assert expected in host_hlil

	for expected in (
		"static void CL_Workshop_Frame( void ) {",
		"static void CL_Netchan_Encode( msg_t *msg ) {",
		"static void CL_Netchan_Decode( msg_t *msg ) {",
		"void CL_Netchan_TransmitNextFragment( netchan_t *chan ) {",
		"void CL_Netchan_Transmit( netchan_t *chan, msg_t* msg ) {",
		"qboolean CL_Netchan_Process( netchan_t *chan, msg_t *msg ) {",
		"void CL_SystemInfoChanged( void ) {",
		"void CL_ParseServerMessage( msg_t *msg ) {",
		"void SCR_AdjustFrom640( float *x, float *y, float *w, float *h ) {",
		"void SCR_FillRect( float x, float y, float width, float height, const float *color ) {",
		"void SCR_DrawPic( float x, float y, float width, float height, qhandle_t hShader ) {",
		"void SCR_DrawDemoRecording( void ) {",
		"void SCR_DebugGraph (float value, int color)",
		"void SCR_Init( void ) {",
		"void SCR_UpdateScreen( void ) {",
		"static void GetClientState( uiClientState_t *state ) {",
		"static void LAN_ResetPings(int source) {",
		"static int LAN_AddServer(int source, const char *name, const char *address) {",
		"static void LAN_RemoveServer(int source, const char *addr) {",
		"static void LAN_GetServerAddressString( int source, int n, char *buf, int buflen ) {",
		"static int LAN_GetServerPing( int source, int n ) {",
		"static int LAN_CompareServers( int source, int sortKey, int sortDir, int s1, int s2 ) {",
		"static void LAN_MarkServerVisible(int source, int n, qboolean visible ) {",
		"static int LAN_ServerIsVisible(int source, int n ) {",
	):
		assert (
			expected in cl_main
			or expected in cl_net_chan
			or expected in cl_parse
			or expected in cl_scrn
			or expected in cl_ui
		)

	for expected in (
		"# Quake Live Steam Host Mapping Round 280",
		"| `sub_4BCE30` | `CL_Netchan_Encode` |",
		"| `sub_4BDA00` | `CL_ParseServerMessage` |",
		"| `sub_4BE3A0` | `SCR_UpdateScreen` |",
		"| `sub_4BEB80` | `LAN_CompareServers` |",
		"0x004BDDF0` and `0x004BDE80` remain",
	):
		assert expected in mapping_round


def test_demo_recording_overlay_matches_retail_modes() -> None:
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
	cl_scrn = (REPO_ROOT / "src/code/client/cl_scrn.c").read_text(encoding="utf-8")
	client_h = (REPO_ROOT / "src/code/client/client.h").read_text(encoding="utf-8")

	demo_overlay_block = _extract_function_block(cl_scrn, "void SCR_DrawDemoRecording( void ) {")

	assert "qhandle_t\trecordShader;" in client_h
	assert 'cls.consoleShader = re.RegisterShader( "console" );' in cl_main
	assert 'cls.recordShader = re.RegisterShaderNoMip( "icons/record" );' in cl_main
	assert 'textures/effects2/console01' not in cl_main
	assert "if ( !cl_demoRecordMessage || !cl_demoRecordMessage->integer ) {" in demo_overlay_block
	assert "if ( cl_demoRecordMessage->integer == 1 ) {" in demo_overlay_block
	assert 'SCR_DrawStringExt( ( 80 - strlen( string ) ) * 4, 420, 8, string, g_color_table[7], qtrue );' in demo_overlay_block
	assert "else if ( cl_demoRecordMessage->integer == 2 ) {" in demo_overlay_block
	assert "SCR_DrawPic( 1, 470, 11, 11, cls.recordShader );" in demo_overlay_block
	assert 'SCR_DrawStringExt( 9, 477, 8, "REC", g_color_table[7], qtrue );' in demo_overlay_block
	assert 'SCR_DrawStringExt( 320 - strlen( string ) * 4, 20, 8, string, g_color_table[7], qtrue );' not in demo_overlay_block


def test_client_collision_mapping_round_283_promotes_hlil_backed_symbols() -> None:
	aliases = json.loads(
		(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json").read_text(encoding="utf-8")
	)["quakelive_steam"]
	host_hlil = (
		REPO_ROOT
		/ "references"
		/ "hlil"
		/ "quakelive"
		/ "quakelive_steam.exe"
		/ "quakelive_steam.exe_hlil.txt"
	).read_text(encoding="utf-8")
	ghidra_functions = (
		REPO_ROOT / "references/reverse-engineering/ghidra/quakelive_steam/functions.csv"
	).read_text(encoding="utf-8")
	cm_load = (REPO_ROOT / "src/code/qcommon/cm_load.c").read_text(encoding="utf-8")
	cm_patch = (REPO_ROOT / "src/code/qcommon/cm_patch.c").read_text(encoding="utf-8")
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
	cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
	bridge_round = (
		REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_13.md"
	).read_text(encoding="utf-8")
	mapping_round = (
		REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_283.md"
	).read_text(encoding="utf-8")

	expected_aliases = {
		"sub_4B9430": "CL_GetConfigStringValue",
		"sub_4B9940": "CL_IsClientPaused",
		"sub_4B9DA0": "CL_AdvertisementBridge_VisibilityTraceCallback",
		"sub_4BF710": "CMod_LoadShaders",
		"sub_4BF7A0": "CMod_LoadSubmodels",
		"sub_4BF910": "CMod_LoadNodes",
		"sub_4BF9C0": "CMod_LoadBrushes",
		"sub_4BFAD0": "CMod_LoadLeafs",
		"sub_4BFBD0": "CMod_LoadPlanes",
		"sub_4BFCF0": "CMod_LoadLeafBrushes",
		"sub_4BFD60": "CMod_LoadLeafSurfaces",
		"sub_4BFDD0": "CMod_LoadBrushSides",
		"sub_4BFE80": "CMod_LoadVisibility",
		"sub_4BFF10": "CMod_LoadPatches",
		"sub_4C0160": "CM_ClearMap",
		"sub_4C0240": "CM_NumInlineModels",
		"sub_4C0260": "CM_LeafCluster",
		"sub_4C02A0": "CM_LeafArea",
		"sub_4C02E0": "CM_InitBoxHull",
		"sub_4C0830": "CM_ClearLevelPatches",
	}

	for address, normalized_name in expected_aliases.items():
		assert aliases[address] == normalized_name

	for expected_row in (
		"FUN_004bf7a0,004bf7a0,364,0,unknown",
		"FUN_004bfbd0,004bfbd0,281,0,unknown",
		"FUN_004bf9c0,004bf9c0,258,0,unknown",
		"FUN_004bfad0,004bfad0,254,0,unknown",
		"FUN_004bfdd0,004bfdd0,163,0,unknown",
		"FUN_004bf910,004bf910,161,0,unknown",
		"FUN_004bf710,004bf710,143,0,unknown",
		"FUN_004bfe80,004bfe80,136,0,unknown",
		"FUN_004b9da0,004b9da0,102,0,unknown",
		"FUN_004bfcf0,004bfcf0,97,0,unknown",
		"FUN_004bfd60,004bfd60,97,0,unknown",
		"FUN_004b9940,004b9940,26,0,unknown",
		"FUN_004b9430,004b9430,20,0,unknown",
		"FUN_004c02e0,004c02e0,278,0,unknown",
		"FUN_004c02a0,004c02a0,50,0,unknown",
		"FUN_004c0260,004c0260,49,0,unknown",
		"FUN_004c0160,004c0160,25,0,unknown",
		"FUN_004c0830,004c0830,13,0,unknown",
	):
		assert expected_row in ghidra_functions

	for expected in (
		"004b9443  return (&data_146cfd4)[arg1] + 0x146dfd4",
		"004b994f  if (*(eax_2 + 0x30) == 0 && *(eax_2 + 0x20) == 0)",
		"004b9dcf  sub_4c78c0(&var_40, arg1, arg2, &data_124a6b4, &data_124a6b4, 0, 0x6000001, 0)",
		"004bce19  sub_4f20a0(sub_4b9da0)",
		"CMod_LoadShaders: funny lump",
		"Map with no shaders",
		"MAX_SUBMODELS exceeded",
		"Map has no nodes",
		"CMod_LoadBrushes: bad shaderNum",
		"CMod_LoadBrushSides: bad shaderN",
		"004bfe96      int32_t eax_3 = (data_146cbc8 + 0x1f) & 0xffffffe0",
		"004bfec1      return sub_4c95e0(eax_4, 0xff, ecx)",
		"004c016c  sub_4c95e0(&data_146cb00, 0, 0xfc)",
		"004c0245  return data_146cbb8",
		"004c027a  sub_4c9b60(1, \"CM_LeafCluster: bad number\")",
		"004c02ba  sub_4c9b60(1, \"CM_LeafArea: bad number\")",
		"004c0330  *(data_146cc00 + 4) = 0x2000000",
		"004c0832  data_114e160 = 0",
	):
		assert expected in host_hlil

	cm_load_order = [
		"004c0746  sub_4bf710(var_b4_8)",
		"004c074f  sub_4bfad0(&var_78)",
		"004c0758  sub_4bfcf0(&var_68)",
		"004c0761  sub_4bfd60(&var_70)",
		"004c076d  sub_4bfbd0(&var_88)",
		"004c0776  sub_4bfdd0(&var_50)",
		"004c077f  sub_4bf9c0(&var_58)",
		"004c0788  sub_4bf7a0(&var_60)",
		"004c0791  sub_4bf910(&var_80)",
		"004c07c7  sub_4bfe80(&var_18)",
		"004c07d4  sub_4bff10(&var_30, &var_48)",
	]
	call_offsets = [host_hlil.index(line) for line in cm_load_order]
	assert call_offsets == sorted(call_offsets)

	for expected in (
		"void CMod_LoadShaders( lump_t *l ) {",
		"void CMod_LoadSubmodels( lump_t *l ) {",
		"void CMod_LoadNodes( lump_t *l ) {",
		"void CMod_LoadBrushes( lump_t *l ) {",
		"void CMod_LoadLeafs (lump_t *l)",
		"void CMod_LoadPlanes (lump_t *l)",
		"void CMod_LoadLeafBrushes (lump_t *l)",
		"void CMod_LoadLeafSurfaces( lump_t *l )",
		"void CMod_LoadBrushSides (lump_t *l)",
		"void CMod_LoadVisibility( lump_t *l ) {",
		"void CMod_LoadPatches( lump_t *surfs, lump_t *verts ) {",
		"void CM_ClearMap( void ) {",
		"CM_NumInlineModels( void )",
		"CM_LeafCluster( int leafnum )",
		"CM_LeafArea( int leafnum )",
		"void CM_InitBoxHull (void)",
	):
		assert expected in cm_load

	config_string_block = _extract_function_block(
		cl_main, "static const char *CL_GetConfigStringValue( int index ) {"
	)
	set_cgame_time_block = _extract_function_block(cl_cgame, "void CL_SetCGameTime( void ) {")

	assert "offset = cl.gameState.stringOffsets[index];" in config_string_block
	assert "return cl.gameState.stringData + offset;" in config_string_block
	assert "if ( sv_paused->integer && cl_paused->integer && com_sv_running->integer ) {" in set_cgame_time_block
	assert "void CM_ClearLevelPatches( void ) {" in cm_patch
	assert "debugPatchCollide = NULL;" in cm_patch
	assert "debugFacet = NULL;" in cm_patch
	assert "| `sub_4F20A0` (`0x004F20A0`) | `AdvertisementBridge_SetVisibilityTraceCallback` |" in bridge_round

	for expected in (
		"# Quake Live Steam Host Mapping Round 283",
		"| `sub_4BF710` | `CMod_LoadShaders` |",
		"| `sub_4BF9C0` | `CMod_LoadBrushes` |",
		"| `sub_4BFE80` | `CMod_LoadVisibility` |",
		"| `sub_4C02E0` | `CM_InitBoxHull` |",
		"`CMod_LoadEntityString` is not a separate retail function",
	):
		assert expected in mapping_round


def test_client_cinematic_and_browser_mapping_round_285_promotes_hlil_backed_symbols() -> None:
	aliases = json.loads(
		(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json").read_text(encoding="utf-8")
	)["quakelive_steam"]
	host_hlil = (
		REPO_ROOT
		/ "references"
		/ "hlil"
		/ "quakelive"
		/ "quakelive_steam.exe"
		/ "quakelive_steam.exe_hlil.txt"
	).read_text(encoding="utf-8")
	ghidra_functions = (
		REPO_ROOT / "references/reverse-engineering/ghidra/quakelive_steam/functions.csv"
	).read_text(encoding="utf-8")
	cl_cin = (REPO_ROOT / "src/code/client/cl_cin.c").read_text(encoding="utf-8")
	cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
	browser_note = (
		REPO_ROOT
		/ "docs/reverse-engineering/awesomium-browser-host-parity-audit-and-implementation-plan-2026-04-16.md"
	).read_text(encoding="utf-8")
	mapping_round = (
		REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_285.md"
	).read_text(encoding="utf-8")

	expected_aliases = {
		"sub_4B0A70": "RllDecodeStereoToStereo",
		"sub_4B0AF0": "move8_32",
		"sub_4B0BD0": "blit8_32",
		"sub_4B0F60": "ROQ_GenYUVTables",
		"sub_4B1010": "yuv_to_rgb",
		"sub_4B1080": "yuv_to_rgb24",
		"sub_4B1DA0": "recurseQuad",
		"sub_4B1EB0": "setupQuad",
		"sub_4B1FC0": "readQuadInfo",
		"sub_4B2110": "RoQPrepMcomp",
		"sub_4B21C0": "initRoQ",
		"sub_4B2220": "RoQ_init",
		"sub_4B2300": "RoQShutdown",
		"sub_4B2790": "SCR_DrawCinematic",
		"sub_4B27B0": "SCR_StopCinematic",
		"sub_4B27E0": "CIN_UploadCinematic",
		"sub_4B2890": "CIN_CloseAllVideos",
		"sub_4B2910": "RoQReset",
		"sub_4B3510": "SCR_RunCinematic",
		"sub_4F2900": "QLWebView_InjectActivationKeyboardEvent",
	}

	for address, normalized_name in expected_aliases.items():
		assert aliases[address] == normalized_name

	for expected_row in (
		"FUN_004b1fc0,004b1fc0,322,0,unknown",
		"FUN_004b1eb0,004b1eb0,260,0,unknown",
		"FUN_004b1da0,004b1da0,259,0,unknown",
		"FUN_004b0bd0,004b0bd0,255,0,unknown",
		"FUN_004b2300,004b2300,254,0,unknown",
		"FUN_004b2220,004b2220,223,0,unknown",
		"FUN_004b0af0,004b0af0,214,0,unknown",
		"FUN_004b2910,004b2910,179,0,unknown",
		"FUN_004b0f60,004b0f60,173,0,unknown",
		"FUN_004b27e0,004b27e0,172,0,unknown",
		"FUN_004b2110,004b2110,161,0,unknown",
		"FUN_004b0a70,004b0a70,128,0,unknown",
		"FUN_004b1080,004b1080,124,0,unknown",
		"FUN_004b2890,004b2890,122,0,unknown",
		"FUN_004b1010,004b1010,111,0,unknown",
		"FUN_004b21c0,004b21c0,83,0,unknown",
		"FUN_004f2900,004f2900,77,0,unknown",
		"FUN_004b27b0,004b27b0,35,0,unknown",
		"FUN_004b2790,004b2790,18,0,unknown",
		"FUN_004b3510,004b3510,18,0,unknown",
	):
		assert expected_row in ghidra_functions

	for expected in (
		"004b0a8e  if (arg4 != 0)",
		"004b0aef  return eax u>> 1",
		"004b0af5  *arg3 = fconvert.d(fconvert.t(*arg1))",
		"004b0bd5  *arg3 = fconvert.d(fconvert.t(*arg1))",
		"004b0f94      long double x87_r2_2 = fconvert.t(fconvert.s(float.t(i_1)))",
		"004b101f  int32_t esi = *((arg1 << 2) + &data_114b930)",
		"004b1088  int32_t esi = *((arg3 << 2) + &data_114b930)",
		"004b1e61      sub_4b1da0(ebx, edi, esi, arg4, arg5)",
		"004b1f6c                      sub_4b1da0(edi_1, i, 0x10, arg1, arg2)",
		"004b1fe0      *(result + 0x1149a6c) = (zx.d(arg1[1]) << 8) + zx.d(*arg1)",
		"004b211b  void* eax_1 = data_565b5c * 0x1c4",
		"004b21d4      *(eax + 0x1149a5c) = sub_4b0cd0",
		"004b21ea      sub_4b0f60()",
		"004b222e  long double x87_r7 = float.t(sub_4b9bd0())",
		"004b232a      sub_4c9ab0(\"finished cinematic\\n\")",
		"004b27bb      sub_4b2400(result)",
		"004b2861          data_146ccb0(0x100, 0x100, 0x100, 0x100, ecx_1, arg1, *(esi_2 + 0x1149a10))",
		"004b28be          sub_4c9ab0(\"trFMV::stop(), closing %s\\n\")",
		"004b299f      sub_4ed020(&data_1050ad8, 0x10, 1, *(data_565b5c * 0x1c4 + 0x1149a20))",
		"004b351b      result = sub_4b2f40(result)",
		"004f2925      Awesomium::WebKeyboardEvent::WebKeyboardEvent(this: ecx, 0, 0x11, 0x1d0001)",
		"004f293d      result = (*(*data_12d3050 + 0xe0))(&var_40)",
	):
		assert expected in host_hlil

	for expected in (
		"long RllDecodeStereoToStereo(unsigned char *from,short *to,unsigned int size,char signedOutput, unsigned short flag)",
		"static void move8_32( byte *src, byte *dst, int spl )",
		"static void blit8_32( byte *src, byte *dst, int spl  )",
		"static void ROQ_GenYUVTables( void )",
		"static unsigned short yuv_to_rgb( long y, long u, long v )",
		"static unsigned int yuv_to_rgb24( long y, long u, long v )",
		"static void recurseQuad( long startX, long startY, long quadSize, long xOff, long yOff )",
		"static void setupQuad( long xOff, long yOff )",
		"static void readQuadInfo( byte *qData )",
		"static void RoQPrepMcomp( long xoff, long yoff )",
		"static void initRoQ()",
		"static void RoQReset() {",
		"static void RoQShutdown( void ) {",
		"void CIN_CloseAllVideos(void) {",
		"void SCR_DrawCinematic (void) {",
		"void SCR_RunCinematic (void)",
		"void SCR_StopCinematic(void) {",
		"void CIN_UploadCinematic(int handle) {",
	):
		assert expected in cl_cin

	init_ref_block = _extract_function_block(cl_main, "void CL_InitRef( void ) {")
	activation_block = _extract_function_block(
		cl_cgame, "static void QLWebView_InjectActivationKeyboardEvent( void ) {"
	)
	notify_activation_block = _extract_function_block(
		cl_cgame, "void CL_WebHost_NotifyAppActivation( qboolean active ) {"
	)

	assert "ri.CIN_UploadCinematic = CIN_UploadCinematic;" in init_ref_block
	assert "ri.CIN_PlayCinematic = CIN_PlayCinematic;" in init_ref_block
	assert "ri.CIN_RunCinematic = CIN_RunCinematic;" in init_ref_block
	assert "QLWebView_InjectKeyboardEvent( 0x11, qtrue );" in activation_block
	assert "QLWebView_InjectActivationKeyboardEvent();" in notify_activation_block
	assert "Added retained `QLWebView_InjectActivationKeyboardEvent()`" in browser_note

	for expected in (
		"# Quake Live Steam Host Mapping Round 285",
		"| `sub_4B0A70` | `RllDecodeStereoToStereo` |",
		"| `sub_4B1FC0` | `readQuadInfo` |",
		"| `sub_4B27E0` | `CIN_UploadCinematic` |",
		"| `sub_4F2900` | `QLWebView_InjectActivationKeyboardEvent` |",
		"`0x004F2320`, `0x004F2330`, `0x004F2380`, and",
		"Client cinematic helper symbol coverage: before 58%, after 96%.",
	):
		assert expected in mapping_round
