from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

# Retail command-owner evidence for this focused slice comes from
# `references/analysis/quakelive_symbol_aliases.json` plus the paired HLIL
# owners in `references/hlil/quakelive/quakelive_steam.exe/`:
# `sub_4B6D00` -> `Key_Unbind_f`
# `sub_4B6D60` -> `Key_Unbindall_f`
# `sub_4B6DF0` -> `Key_Bind_f`
# `sub_4B8430` -> `CL_Record_f`
# `sub_4BB450` -> `CL_PlayDemo_f`
# `sub_4B8CB0` -> `CL_Reconnect_f`
# `sub_4B8D30` -> `CL_Connect_f`
# `sub_4D12E0` -> `FS_Dir_f`
# `sub_4D1610` -> `FS_Path_f`
# `sub_4DEC60` -> `SV_Status_f`


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


def test_bind_family_commands_match_retail_handler_and_registration_shape() -> None:
	cl_keys = (REPO_ROOT / "src/code/client/cl_keys.c").read_text(encoding="utf-8")

	unbind_block = _extract_function_block(cl_keys, "void Key_Unbind_f (void)")
	unbindall_block = _extract_function_block(cl_keys, "void Key_Unbindall_f (void)")
	bind_block = _extract_function_block(cl_keys, "void Key_Bind_f (void)")
	init_block = _extract_function_block(cl_keys, "void CL_InitKeyCommands( void ) {")

	assert 'Com_Printf ("unbind <key> : remove commands from a key\\n");' in unbind_block
	assert 'Key_SetBinding (b, "");' in unbind_block
	assert 'for (i=0 ; i<256 ; i++)' in unbindall_block
	assert 'Key_SetBinding (i, "");' in unbindall_block
	assert 'Com_Printf ("bind <key> [command] : attach a command to a key\\n");' in bind_block
	assert 'Com_Printf ("\\"%s\\" = \\"%s\\"\\n", Cmd_Argv(1), keys[b].binding );' in bind_block
	assert 'Com_Printf ("\\"%s\\" is not bound\\n", Cmd_Argv(1) );' in bind_block
	assert 'Key_SetBinding (b, cmd);' in bind_block
	assert 'Cmd_AddCommand ("bind",Key_Bind_f);' in init_block
	assert 'Cmd_AddCommand ("unbind",Key_Unbind_f);' in init_block
	assert 'Cmd_AddCommand ("unbindall",Key_Unbindall_f);' in init_block


def test_client_connect_and_demo_commands_match_retail_contracts() -> None:
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

	record_block = _extract_function_block(cl_main, "void CL_Record_f( void ) {")
	demo_block = _extract_function_block(cl_main, "void CL_PlayDemo_f( void ) {")
	reconnect_block = _extract_function_block(cl_main, "void CL_Reconnect_f( void ) {")
	connect_block = _extract_function_block(cl_main, "void CL_Connect_f( void ) {")

	assert 'Com_Printf ("Correct usage: record <demoname>\\n");' in record_block
	assert 'Com_Printf ("Already recording.\\n");' in record_block
	assert "CL_StopRecord_f();" in record_block
	assert 'Com_Error( ERR_FATAL, "stoprecord failed" );' in record_block
	assert 'Com_Printf ("recording to %s.\\n", name);' in record_block
	assert 'MSG_WriteByte (&buf, svc_gamestate);' in record_block

	assert 'Com_Printf ("playdemo <demoname>\\n");' in demo_block
	assert 'SV_Shutdown( "Starting Demo.\\n" );' in demo_block
	assert 'CL_Disconnect( qfalse );' in demo_block
	assert 'CL_WalkDemoExt( arg, name, &clc.demofile );' in demo_block

	assert 'Com_Printf( "Can\'t reconnect to localhost.\\n" );' in reconnect_block
	assert 'Cbuf_AddText( va("connect %s\\n", cls.servername ) );' in reconnect_block

	assert 'Com_Printf( "usage: connect [server]\\n");' in connect_block
	assert "CL_RequestMotd();" in connect_block
	assert 'SV_Shutdown( "Server quit\\n" );' in connect_block
	assert 'Cvar_Set( "sv_killserver", "1" );' in connect_block
	assert 'CL_Disconnect( qtrue );' in connect_block
	assert "NET_StringToAdr( cls.servername, &clc.serverAddress)" in connect_block

	assert 'Cmd_AddCommand ("record", CL_Record_f);' in cl_main
	assert 'Cmd_AddCommand ("demo", CL_PlayDemo_f);' in cl_main
	assert 'Cmd_AddCommand ("connect", CL_Connect_f);' in cl_main
	assert 'Cmd_AddCommand ("reconnect", CL_Reconnect_f);' in cl_main


def test_filesystem_command_handlers_match_retail_dir_and_path_contracts() -> None:
	files_c = (REPO_ROOT / "src/code/qcommon/files.c").read_text(encoding="utf-8")

	dir_block = _extract_function_block(files_c, "void FS_Dir_f( void ) {")
	path_block = _extract_function_block(files_c, "void FS_Path_f( void ) {")

	assert 'Com_Printf( "usage: dir <directory> [extension]\\n" );' in dir_block
	assert "FS_ListFiles( path, extension, &ndirs );" in dir_block
	assert 'Com_Printf( "Directory of %s %s\\n", path, extension );' in dir_block
	assert 'Com_Printf ("%s (0x%08x - %i files)\\n", s->pack->pakFilename, s->pack->checksum, s->pack->numfiles);' in path_block
	assert 'Com_Printf( "    not on the pure list\\n" );' in path_block
	assert 'Com_Printf( "    on the pure list\\n" );' in path_block

	assert 'Cmd_AddCommand ("dir", FS_Dir_f );' in files_c
	assert 'Cmd_AddCommand ("path", FS_Path_f);' in files_c


def test_server_status_command_matches_retail_wiring_and_output_shape() -> None:
	sv_ccmds = (REPO_ROOT / "src/code/server/sv_ccmds.c").read_text(encoding="utf-8")

	steamid_block = _extract_function_block(sv_ccmds, "static unsigned long long SV_StatusClientSteamId( const client_t *cl ) {")
	status_block = _extract_function_block(sv_ccmds, "static void SV_Status_f( void ) {")

	assert 'steamId = Info_ValueForKey( cl->userinfo, "steamid" );' in steamid_block
	assert "value = value * 10ull + (unsigned long long)( *cursor - '0' );" in steamid_block
	assert 'Com_Printf ("num score ping name            lastmsg address               qport rate  steamid\\n");' in status_block
	assert 'Com_Printf ("--- ----- ---- --------------- ------- --------------------- ----- ----- -----------------\\n");' in status_block
	assert 'steamIdValue = SV_StatusClientSteamId( cl );' in status_block
	assert 'Com_Printf (" %llu", steamIdValue);' in status_block
	assert 'Cmd_AddCommand ("status", SV_Status_f);' in sv_ccmds
