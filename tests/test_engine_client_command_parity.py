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
	assert "R_UpdatePostProcessCvars();" in restart_block
	assert "tr.postProcessNeedsReset = qtrue;" in restart_block
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

	assert "void\tCL_LocalServers_f( void );" not in client_h
	assert "void\tCL_GlobalServers_f( void );" not in client_h
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
	assert "void CL_LocalServers_f( void ) {" not in cl_main
	assert "void CL_GlobalServers_f( void ) {" not in cl_main
	assert "void CL_Ping_f( void ) {" not in cl_main
	assert "void CL_ServerStatus_f(void) {" not in cl_main

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
