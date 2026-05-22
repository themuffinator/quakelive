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
# `sub_4B4FD0` -> alias execution helper
# `sub_4B5060` -> `Cmd_Alias_f`
# `sub_4B5170` -> `Cmd_UnAlias_f`
# `sub_4B51C0` -> `Cmd_UnAliasAll_f`
# `sub_4B6FE0` -> `Key_Bindlist_f`
# `sub_4C7CB0` -> `Cbuf_Init`
# `sub_4C7CF0` -> `Cbuf_AddText`
# `sub_4C7D50` -> `Cbuf_AddTokenized`
# `sub_4C7E50` -> `Cbuf_InsertText`
# `sub_4C7ED0` -> `Cmd_Argc`
# `sub_4C7EE0` -> `Cmd_Argv`
# `sub_4C7F00` -> `Cmd_ArgvBuffer`
# `sub_4C7F40` -> `Cmd_Args`
# `sub_4C7FD0` -> `Cmd_ArgsFrom`
# `sub_4C8060` -> `Cmd_ArgsBuffer`
# `sub_4C8080` -> `Cmd_Cmd`
# `sub_4C8090` -> `Cmd_TokenizeString`
# `sub_4C82F0` -> `Cmd_CommandCompletion`
# `sub_4C8320` -> `Cmd_ExecuteString`
# `sub_4C8430` -> `Cmd_List_f`
# `sub_4C84B0` -> `Cmd_Wait_f`
# `sub_4C84E0` -> `Cbuf_Execute`
# `sub_4C86D0` -> `Cmd_Exec_f`
# `sub_4C87B0` -> `Cmd_Vstr_f`
# `sub_4C87F0` -> `Cmd_Echo_f`
# `sub_4C8890` -> `Cmd_Init`
# `sub_4C8900` -> `Cbuf_ExecuteText`
# `sub_4C8970` -> `Com_BeginRedirect`
# `sub_4C89A0` -> `Com_EndRedirect`
# `sub_4C89E0` -> `Com_SafeMode`
# `sub_4C8A70` -> `Com_StartupVariable`
# `sub_4C8AE0` -> `Com_AddStartupCommands`
# `sub_4C8B40` -> `Com_StringContains`
# `sub_4C9160` -> `Com_HashKey`
# `sub_4C91B0` -> `Com_RealTime`
# `sub_4C9390` -> `Com_RunAndTimeServerPacket`
# `sub_4C93D0` -> `Com_Crash_f`
# `sub_4C93E0` -> `Com_ProfilePidIsCurrentProcess`
# `sub_4C94A0` -> `Com_Shutdown`
# `sub_4C9EB0` -> `Com_ParseCommandLine`
# `sub_4C9E70` -> `Com_Quit_f`
# `sub_4CA010` -> `Info_Print`
# `sub_4CA1D0` -> `Z_Free`
# `sub_4CA2C0` -> `Z_TagMalloc`
# `sub_4CA3A0` -> `Z_Malloc`
# `sub_4CA3D0` -> `S_Malloc`
# `sub_4CA3F0` -> `Z_CheckHeap`
# `sub_4CA470` -> `CopyString`
# `sub_4CA4E0` -> `Com_Meminfo_f`
# `sub_4CA750` -> `Com_TouchMemory`
# `sub_4CA790` -> `Com_InitSmallZoneMemory`
# `sub_4CA840` -> `Com_InitZoneMemory`
# `sub_4CA910` -> `Hunk_Clear`
# `sub_4CAAA0` -> `Hunk_AllocateTempMemory`
# `sub_4CAB80` -> `Hunk_FreeTempMemory`
# `sub_4CAC00` -> `Com_InitJournaling`
# `sub_4CACE0` -> `Com_GetRealEvent`
# `sub_4CAE10` -> `Com_PushEvent`
# `sub_4CAEB0` -> `Com_GetEvent`
# `sub_4CAF40` -> `Com_Milliseconds`
# `sub_4CAF90` -> `Com_Error_f`
# `sub_4CAFC0` -> `Com_Freeze_f`
# `sub_4CB070` -> `Com_ReadCDKey`
# `sub_4CB170` -> `Com_AppendCDKey`
# `sub_4CD4D0` -> `Cvar_Add_f`
# `sub_4CD560` -> `Cvar_Mult_f`
# `sub_4CD860` -> `Cvar_Clear_f`
# `sub_4CD9B0` -> `Cvar_List_f`
# `sub_4CDB50` -> `Cvar_Restart_f`
# `sub_4D12E0` -> `FS_Dir_f`
# `sub_4D1510` -> `FS_NewDir_f`
# `sub_4D1610` -> `FS_Path_f`
# `sub_4D1700` -> `FS_TouchFile_f`
# `sub_4D5750` -> `MSG_ReportChangeVectors_f`
# `sub_4DEC60` -> `SV_Status_f`
# `sub_4ED7E0` -> `Com_IdleSleep`
# `sub_4CB630` -> `Com_WriteClientConfig_f`
# `sub_4B6A60` -> `Console_CompleteArgument`
# `sub_4C9700` -> `FindMatches`
# `sub_4CB900` -> `PrintMatches`
# `sub_4CB950` -> `Field_CompleteCommand`


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
	bindlist_block = _extract_function_block(cl_keys, "void Key_Bindlist_f( void ) {")
	init_block = _extract_function_block(cl_keys, "void CL_InitKeyCommands( void ) {")

	assert 'Com_Printf ("unbind <key> : remove commands from a key\\n");' in unbind_block
	assert 'Key_SetBinding (b, "");' in unbind_block
	assert 'for (i=0 ; i<256 ; i++)' in unbindall_block
	assert 'Key_SetBinding (i, "");' in unbindall_block
	assert 'Com_Printf ("bind <key> [command] : attach a command to a key\\n");' in bind_block
	assert 'Com_Printf ("\\"%s\\" = \\"%s\\"\\n", Cmd_Argv(1), keys[b].binding );' in bind_block
	assert 'Com_Printf ("\\"%s\\" is not bound\\n", Cmd_Argv(1) );' in bind_block
	assert 'Key_SetBinding (b, cmd);' in bind_block
	assert 'Com_Printf( "%s \\"%s\\"\\n", Key_KeynumToString(i), keys[i].binding );' in bindlist_block
	assert 'Cmd_AddCommand ("bind",Key_Bind_f);' in init_block
	assert 'Cmd_AddCommand ("unbind",Key_Unbind_f);' in init_block
	assert 'Cmd_AddCommand ("unbindall",Key_Unbindall_f);' in init_block
	assert 'Cmd_AddCommand ("bindlist",Key_Bindlist_f);' in init_block


def test_console_autocomplete_matches_retail_argument_sources_and_field_rebuild() -> None:
	cl_keys = (REPO_ROOT / "src/code/client/cl_keys.c").read_text(encoding="utf-8")
	common_c = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")
	vm_c = (REPO_ROOT / "src/code/qcommon/vm.c").read_text(encoding="utf-8")

	argument_block = _extract_function_block(cl_keys, "static void Console_CompleteArgument( const char *command, void(*callback)( const char *s ) ) {")
	field_block = _extract_function_block(common_c, "void Field_CompleteCommand( field_t *field, fieldCompletionCallback_t callback ) {")
	native_call_block = _extract_function_block(vm_c, "static int VM_CallNativeExports( vm_t *vm, int callnum, const int *args ) {")

	assert '#include "../qcommon/vm_local.h"' in cl_keys
	assert "if ( uivm && uivm->dllExports ) {" in argument_block
	assert "VM_Call( uivm, UI_FOR_EACH_ARENA_NAME, (int)(intptr_t)callback );" in argument_block
	assert "case UI_FOR_EACH_ARENA_NAME:" in native_call_block
	assert "((void (QDECL *)( uiArenaNameCallback_t ))exportFunc)( (uiArenaNameCallback_t)(intptr_t)args[0] );" in native_call_block

	assert 'if ( Q_stricmp( command, "demo" ) && Q_stricmp( command, "\\\\demo" ) ) {' in argument_block
	assert 'FS_ListFiles( "demos", ".dm_73", &fileCount );' in argument_block
	assert "for ( i = 0 ; i < fileCount ; i++ ) {" in argument_block
	assert "callback( files[i] );" in argument_block
	assert "FS_FreeFileList( files );" in argument_block
	assert "FS_GetFileList" not in argument_block
	assert "PROTOCOL_VERSION" not in argument_block
	assert "commandName" not in argument_block
	assert "commandName++" not in argument_block

	assert "Cmd_CommandCompletion( FindMatches );" in field_block
	assert "Cvar_CommandCompletion( FindMatches );" in field_block
	assert "callback( command, FindMatches );" in field_block
	assert "Q_strcat( completionField->buffer, sizeof( completionField->buffer ), Cmd_Argv( i ) );" in field_block
	assert 'Q_strcat( completionField->buffer, sizeof( completionField->buffer ), " " );' in field_block
	assert "Field_AppendCompletionArgument" not in common_c
	assert "needsQuotes" not in common_c


def test_console_and_alias_command_families_match_retail_wiring() -> None:
	cl_console = (REPO_ROOT / "src/code/client/cl_console.c").read_text(encoding="utf-8")
	cmd_c = (REPO_ROOT / "src/code/qcommon/cmd.c").read_text(encoding="utf-8")

	toggle_block = _extract_function_block(cl_console, "void Con_ToggleConsole_f (void) {")
	condump_block = _extract_function_block(cl_console, "void Con_Dump_f (void)")
	find_block = _extract_function_block(cl_console, "void Con_Find_f( void ) {")
	find_matches_block = _extract_function_block(cl_console, "static void Con_FindMatchesInHistory( void ) {")
	alias_block = _extract_function_block(cmd_c, "void Cmd_Alias_f( void ) {")
	unalias_block = _extract_function_block(cmd_c, "void Cmd_UnAlias_f( void ) {")
	unaliasall_block = _extract_function_block(cmd_c, "void Cmd_UnAliasAll_f( void ) {")
	write_aliases_block = _extract_function_block(cmd_c, "void Cmd_WriteAliases( fileHandle_t f ) {")
	execute_block = _extract_function_block(cmd_c, "Cmd_ExecuteString( const char *text ) {")
	init_block = _extract_function_block(cmd_c, "void Cmd_Init (void) {")

	assert 'Com_Printf( "com_allowConsole won\'t allow toggleconsole command\\n" );' in toggle_block
	assert 'Con_ClearNotify ();' in toggle_block
	assert 'cls.keyCatchers ^= KEYCATCH_CONSOLE;' in toggle_block

	assert 'Com_Printf ("usage: condump <filename>\\n");' in condump_block
	assert 'Com_Printf ("Dumped console text to %s.\\n", Cmd_Argv(1) );' in condump_block
	assert 'Com_Printf ("ERROR: couldn\'t open.\\n");' in condump_block
	assert 'strcat( buffer, "\\n" );' in condump_block

	assert 'Com_Printf( "usage: find <substring>  ; This is a case sensitive search of the console history.\\n" );' in find_block
	assert 'Con_FindMatchesInHistory();' in find_block
	assert 'limit = con_matchlimit ? con_matchlimit->integer : 16;' in find_matches_block
	assert 'if ( matches > 0 && matches >= limit ) {' in find_matches_block
	assert 'if ( strstr( buffer, needle ) && !strstr( buffer, "\\\\find" ) && !strstr( buffer, "usage: find " ) ) {' in find_matches_block

	assert 'Cmd_AddCommand ("toggleconsole", Con_ToggleConsole_f);' in cl_console
	assert 'Cmd_AddCommand ("messagemode", Con_MessageMode_f);' in cl_console
	assert 'Cmd_AddCommand ("messagemode2", Con_MessageMode2_f);' in cl_console
	assert 'Cmd_AddCommand ("clear", Con_Clear_f);' in cl_console
	assert 'Cmd_AddCommand ("condump", Con_Dump_f);' in cl_console
	assert 'Cmd_AddCommand( "find", Con_Find_f );' in cl_console
	assert 'Cmd_AddCommand ("messagemode3", Con_MessageMode3_f);' not in cl_console
	assert 'Cmd_AddCommand ("messagemode4", Con_MessageMode4_f);' not in cl_console

	assert 'Com_Printf( "Usage: alias \\"command\\"\\n" );' in alias_block
	assert 'Com_Printf( "^1No free alias slots. Use UnAlias to remove an alias before adding this one.^7\\n" );' in alias_block
	assert 'Com_Printf( "Alias: %s \\"%s\\"\\n", alias->name, alias->command );' in alias_block
	assert 'Com_Printf( "Usage: unalias \\"command\\"\\n" );' in unalias_block
	assert 'Com_Printf( "Alias List:\\n" );' in cmd_c
	assert 'cmd_aliases[i].inuse = qfalse;' in unaliasall_block
	assert 'FS_Printf( f, "unaliasall\\n" );' in write_aliases_block
	assert 'FS_Printf( f, "alias %s \\"%s\\"\\n", cmd_aliases[i].name, cmd_aliases[i].command );' in write_aliases_block

	assert 'if ( Cmd_FindAlias( cmd_argv[0] ) ) {' in execute_block
	assert 'Cmd_ExecuteAlias();' in execute_block
	assert 'Cmd_AddCommand ("alias",Cmd_Alias_f);' in init_block
	assert 'Cmd_AddCommand ("unalias",Cmd_UnAlias_f);' in init_block
	assert 'Cmd_AddCommand ("unaliasall",Cmd_UnAliasAll_f);' in init_block


def test_qcommon_script_command_surface_matches_retail_registration_order() -> None:
	cmd_c = (REPO_ROOT / "src/code/qcommon/cmd.c").read_text(encoding="utf-8")
	common_c = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")

	cmd_init_block = _extract_function_block(cmd_c, "void Cmd_Init (void) {")
	hunk_init_block = _extract_function_block(common_c, "void Com_InitHunkMemory( void ) {")
	com_init_block = _extract_function_block(common_c, "void Com_Init( char *commandLine ) {")

	command_lines = [
		'Cmd_AddCommand ("cmdlist",Cmd_List_f);',
		'Cmd_AddCommand ("listcmds",Cmd_List_f);',
		'Cmd_AddCommand ("exec",Cmd_Exec_f);',
		'Cmd_AddCommand ("vstr",Cmd_Vstr_f);',
		'Cmd_AddCommand ("echo",Cmd_Echo_f);',
		'Cmd_AddCommand ("wait", Cmd_Wait_f);',
	]
	positions = []
	for command_line in command_lines:
		assert command_line in cmd_init_block
		positions.append(cmd_init_block.index(command_line))

	assert positions == sorted(positions)
	assert 'Cmd_AddCommand( "meminfo", Com_Meminfo_f );' in hunk_init_block
	assert 'Cmd_AddCommand ("error", Com_Error_f);' in com_init_block
	assert 'Cmd_AddCommand ("crash", Com_Crash_f );' in com_init_block
	assert 'Cmd_AddCommand ("freeze", Com_Freeze_f);' in com_init_block
	assert 'Cmd_AddCommand ("quit", Com_Quit_f);' in com_init_block
	assert 'memset( com_pushedEvents, 0, sizeof( com_pushedEvents ) );' in com_init_block
	assert 'com_pushedEventsHead = 0;' in com_init_block
	assert 'com_pushedEventsTail = 0;' in com_init_block


def test_qcommon_command_buffer_and_dispatch_helpers_match_retail_contracts() -> None:
	cmd_c = (REPO_ROOT / "src/code/qcommon/cmd.c").read_text(encoding="utf-8")

	init_buffer_block = _extract_function_block(cmd_c, "void Cbuf_Init (void)")
	add_text_block = _extract_function_block(cmd_c, "void Cbuf_AddText( const char *text ) {")
	add_tokenized_block = _extract_function_block(cmd_c, "void Cbuf_AddTokenized( const char *text ) {")
	insert_text_block = _extract_function_block(cmd_c, "void Cbuf_InsertText( const char *text ) {")
	argc_block = _extract_function_block(cmd_c, "Cmd_Argc( void ) {")
	argv_block = _extract_function_block(cmd_c, "Cmd_Argv( int arg ) {")
	argv_buffer_block = _extract_function_block(cmd_c, "Cmd_ArgvBuffer( int arg, char *buffer, int bufferLength ) {")
	args_block = _extract_function_block(cmd_c, "Cmd_Args( void ) {")
	args_from_block = _extract_function_block(cmd_c, "Cmd_ArgsFrom( int arg ) {")
	args_buffer_block = _extract_function_block(cmd_c, "Cmd_ArgsBuffer( char *buffer, int bufferLength ) {")
	cmd_cmd_block = _extract_function_block(cmd_c, "char *Cmd_Cmd()")
	tokenize_block = _extract_function_block(cmd_c, "void Cmd_TokenizeString( const char *text_in ) {")
	completion_block = _extract_function_block(cmd_c, "Cmd_CommandCompletion( void(*callback)(const char *s) ) {")
	execute_block = _extract_function_block(cmd_c, "Cmd_ExecuteString( const char *text ) {")

	assert 'cmd_text.data = cmd_text_buf;' in init_buffer_block
	assert 'cmd_text.maxsize = MAX_CMD_BUFFER;' in init_buffer_block
	assert 'cmd_text.cursize = 0;' in init_buffer_block

	assert 'l = strlen (text);' in add_text_block
	assert 'Com_Printf ("Cbuf_AddText: overflow\\n");' in add_text_block
	assert 'Com_Memcpy(&cmd_text.data[cmd_text.cursize], text, l);' in add_text_block
	assert 'cmd_text.cursize += l;' in add_text_block

	assert 'for ( token = text ; *token ; token += tokenLength + 1 ) {' in add_tokenized_block
	assert 'Com_Printf( "Cbuf_AddTokenized: overflow\\n" );' in add_tokenized_block
	assert 'totalLength += tokenLength;' in add_tokenized_block
	assert '*dest++ = \' \';' in add_tokenized_block
	assert '*dest++ = \'"\';' in add_tokenized_block
	assert '*dest++ = \'\\n\';' in add_tokenized_block
	assert 'cmd_text.cursize += totalLength;' in add_tokenized_block

	assert 'len = strlen( text ) + 1;' in insert_text_block
	assert 'Com_Printf( "Cbuf_InsertText overflowed\\n" );' in insert_text_block
	assert 'for ( i = cmd_text.cursize - 1 ; i >= 0 ; i-- ) {' in insert_text_block
	assert "cmd_text.data[ len - 1 ] = '\\n';" in insert_text_block
	assert 'cmd_text.cursize += len;' in insert_text_block

	assert 'return cmd_argc;' in argc_block
	assert 'if ( (unsigned)arg >= cmd_argc ) {' in argv_block
	assert 'return "";' in argv_block
	assert 'Q_strncpyz( buffer, Cmd_Argv( arg ), bufferLength );' in argv_buffer_block

	assert 'cmd_args[0] = 0;' in args_block
	assert 'for ( i = 1 ; i < cmd_argc ; i++ ) {' in args_block
	assert 'strcat( cmd_args, cmd_argv[i] );' in args_block
	assert 'strcat( cmd_args, " " );' in args_block

	assert 'if (arg < 0)' in args_from_block
	assert 'for ( i = arg ; i < cmd_argc ; i++ ) {' in args_from_block
	assert 'Q_strncpyz( buffer, Cmd_Args(), bufferLength );' in args_buffer_block
	assert 'return cmd_cmd;' in cmd_cmd_block

	assert 'cmd_argc = 0;' in tokenize_block
	assert 'Q_strncpyz( cmd_cmd, text_in, sizeof(cmd_cmd) );' in tokenize_block
	assert "if ( text[0] == '/' && text[1] == '/' ) {" in tokenize_block
	assert "if ( text[0] == '/' && text[1] =='*' ) {" in tokenize_block
	assert 'if ( *text == \'"\' ) {' in tokenize_block
	assert 'cmd_argv[cmd_argc] = textOut;' in tokenize_block

	assert 'for (cmd=cmd_functions ; cmd ; cmd=cmd->next) {' in completion_block
	assert 'callback( cmd->name );' in completion_block

	assert 'Cmd_TokenizeString( text );' in execute_block
	assert 'if ( !Q_stricmp( cmd_argv[0],cmd->name ) ) {' in execute_block
	assert '*prev = cmd->next;' in execute_block
	assert 'cmd->next = cmd_functions;' in execute_block
	assert 'if ( !cmd->function ) {' in execute_block
	assert 'if ( Cvar_Command() ) {' in execute_block
	assert 'if ( com_cl_running && com_cl_running->integer && CL_GameCommand() ) {' in execute_block
	assert 'if ( com_sv_running && com_sv_running->integer && SV_GameCommand() ) {' in execute_block
	assert 'if ( com_cl_running && com_cl_running->integer && UI_GameCommand() ) {' in execute_block
	assert 'CL_ForwardCommandToServer ( text );' in execute_block


def test_qcommon_script_and_debug_command_handlers_match_retail_contracts() -> None:
	cmd_c = (REPO_ROOT / "src/code/qcommon/cmd.c").read_text(encoding="utf-8")
	common_c = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")

	wait_block = _extract_function_block(cmd_c, "void Cmd_Wait_f( void ) {")
	execute_text_block = _extract_function_block(cmd_c, "void Cbuf_ExecuteText (int exec_when, const char *text)")
	execute_buffer_block = _extract_function_block(cmd_c, "void Cbuf_Execute (void)")
	exec_block = _extract_function_block(cmd_c, "void Cmd_Exec_f( void ) {")
	vstr_block = _extract_function_block(cmd_c, "void Cmd_Vstr_f( void ) {")
	echo_block = _extract_function_block(cmd_c, "void Cmd_Echo_f (void)")
	list_block = _extract_function_block(cmd_c, "void Cmd_List_f (void)")
	idle_sleep_block = _extract_function_block(common_c, "static void Com_IdleSleep( int msec ) {")
	hash_block = _extract_function_block(common_c, "int Com_HashKey(char *string, int maxlen) {")
	packet_block = _extract_function_block(common_c, "void Com_RunAndTimeServerPacket( netadr_t *evFrom, msg_t *buf ) {")
	real_time_block = _extract_function_block(common_c, "int Com_RealTime(qtime_t *qtime) {")
	milliseconds_block = _extract_function_block(common_c, "int Com_Milliseconds (void) {")
	meminfo_block = _extract_function_block(common_c, "void Com_Meminfo_f( void ) {")
	error_block = _extract_function_block(common_c, "static void Com_Error_f (void) {")
	freeze_block = _extract_function_block(common_c, "static void Com_Freeze_f (void) {")
	crash_block = _extract_function_block(common_c, "static void Com_Crash_f( void ) {")
	quit_block = _extract_function_block(common_c, "void Com_Quit_f( void ) {")

	assert 'cmd_wait = atoi( Cmd_Argv( 1 ) );' in wait_block
	assert 'cmd_wait = 1;' in wait_block

	assert 'case EXEC_NOW:' in execute_text_block
	assert 'Cmd_ExecuteString (text);' in execute_text_block
	assert 'Cbuf_Execute();' in execute_text_block
	assert 'case EXEC_INSERT:' in execute_text_block
	assert 'Cbuf_InsertText (text);' in execute_text_block
	assert 'case EXEC_APPEND:' in execute_text_block
	assert 'Cbuf_AddText (text);' in execute_text_block
	assert 'Com_Error (ERR_FATAL, "Cbuf_ExecuteText: bad exec_when");' in execute_text_block

	assert 'while (cmd_text.cursize)' in execute_buffer_block
	assert 'if ( cmd_wait )\t{' in execute_buffer_block
	assert 'if ( !(quotes&1) &&  text[i] == \';\')' in execute_buffer_block
	assert 'if (text[i] == \'\\n\' || text[i] == \'\\r\' )' in execute_buffer_block
	assert 'memmove (text, text+i, cmd_text.cursize);' in execute_buffer_block
	assert 'Cmd_ExecuteString (line);' in execute_buffer_block

	assert 'Com_Printf ("exec <filename> : execute a script file\\n");' in exec_block
	assert 'COM_DefaultExtension( filename, sizeof( filename ), ".cfg" );' in exec_block
	assert 'len = FS_ReadFile( filename, (void **)&f);' in exec_block
	assert 'Com_Printf ("couldn\'t exec %s\\n",Cmd_Argv(1));' in exec_block
	assert 'Com_Printf ("execing %s\\n",Cmd_Argv(1));' in exec_block
	assert 'Cbuf_InsertText (f);' in exec_block
	assert 'FS_FreeFile (f);' in exec_block

	assert 'Com_Printf ("vstr <variablename> : execute a variable command\\n");' in vstr_block
	assert 'v = Cvar_VariableString( Cmd_Argv( 1 ) );' in vstr_block
	assert 'Cbuf_InsertText( va("%s\\n", v ) );' in vstr_block

	assert 'for (i=1 ; i<Cmd_Argc() ; i++)' in echo_block
	assert 'Com_Printf ("%s ",Cmd_Argv(i));' in echo_block
	assert 'Com_Printf ("\\n");' in echo_block

	assert 'if (match && !Com_Filter(match, cmd->name, qfalse)) continue;' in list_block
	assert 'Com_Printf ("%s\\n", cmd->name);' in list_block
	assert 'Com_Printf ("%i commands\\n", i);' in list_block

	assert 'if ( msec <= 0 ) {' in idle_sleep_block
	assert 'dueTime.QuadPart = -( (LONGLONG)msec * 10000 );' in idle_sleep_block
	assert 'timer = CreateWaitableTimer( NULL, qtrue, NULL );' in idle_sleep_block
	assert 'SetWaitableTimer( timer, &dueTime, 0, NULL, NULL, qfalse );' in idle_sleep_block
	assert 'WaitForSingleObject( timer, INFINITE );' in idle_sleep_block
	assert 'CloseHandle( timer );' in idle_sleep_block
	assert 'usleep( msec * 1000 );' in idle_sleep_block
	assert 'if ( !timer ) {' not in idle_sleep_block
	assert 'if ( SetWaitableTimer( timer, &dueTime, 0, NULL, NULL, qfalse ) ) {' not in idle_sleep_block

	assert 'hash = 0;' in hash_block
	assert "for (i = 0; i < maxlen && string[i] != '\\0'; i++) {" in hash_block
	assert 'hash += string[i] * (119 + i);' in hash_block
	assert 'hash = (hash ^ (hash >> 10) ^ (hash >> 20));' in hash_block
	assert 'return hash;' in hash_block

	assert 'SV_PacketEvent( *evFrom, buf );' in packet_block

	assert 't = time(NULL);' in real_time_block
	assert 'if (!qtime)' in real_time_block
	assert 'tms = localtime(&t);' in real_time_block
	assert 'qtime->tm_sec = tms->tm_sec;' in real_time_block
	assert 'qtime->tm_isdst = tms->tm_isdst;' in real_time_block
	assert 'return t;' in real_time_block

	assert 'ev = Com_GetRealEvent();' in milliseconds_block
	assert 'if ( ev.evType != SE_NONE ) {' in milliseconds_block
	assert 'Com_PushEvent( &ev );' in milliseconds_block
	assert '} while ( ev.evType != SE_NONE );' in milliseconds_block
	assert 'return ev.evTime;' in milliseconds_block

	assert 'Com_Printf( "%8i bytes total hunk\\n", s_hunkTotal );' in meminfo_block
	assert 'Com_Printf( "%8i bytes total zone\\n", s_zoneTotal );' in meminfo_block
	assert 'Com_Printf( "        %8i bytes in dynamic botlib\\n", botlibBytes );' in meminfo_block
	assert 'Com_Printf( "        %8i bytes in dynamic renderer\\n", rendererBytes );' in meminfo_block
	assert 'Com_Printf( "        %8i bytes in small Zone memory\\n", smallZoneBytes );' in meminfo_block

	assert 'Com_Error( ERR_DROP, "Testing drop error" );' in error_block
	assert 'Com_Error( ERR_FATAL, "Testing fatal error" );' in error_block

	assert 'Com_Printf( "freeze <seconds>\\n" );' in freeze_block
	assert 's = atof( Cmd_Argv(1) );' in freeze_block
	assert 'start = Com_Milliseconds();' in freeze_block
	assert 'now = Com_Milliseconds();' in freeze_block

	assert '* ( int * ) 0 = 0x12345678;' in crash_block

	assert 'SV_Shutdown ("Server quit\\n");' in quit_block
	assert 'CL_Shutdown ();' in quit_block
	assert 'Com_Shutdown ();' in quit_block
	assert 'FS_Shutdown(qtrue);' in quit_block
	assert 'Sys_Quit ();' in quit_block


def test_qcommon_redirect_and_startup_helpers_match_retail_contracts() -> None:
	common_c = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")

	begin_redirect_block = _extract_function_block(common_c, "void Com_BeginRedirect (char *buffer, int buffersize, void (*flush)( char *) )")
	end_redirect_block = _extract_function_block(common_c, "void Com_EndRedirect (void)")
	free_startup_lines_block = _extract_function_block(common_c, "static void Com_FreeStartupCommandLines( void ) {")
	startup_argv_block = _extract_function_block(common_c, "static char *Com_StartupLineArgv( char *line, int arg ) {")
	parse_block = _extract_function_block(common_c, "void Com_ParseCommandLine( char *commandLine ) {")
	profile_pid_block = _extract_function_block(common_c, "static qboolean Com_ProfilePidIsCurrentProcess( void ) {")
	safe_mode_block = _extract_function_block(common_c, "qboolean Com_SafeMode( void ) {")
	startup_variable_block = _extract_function_block(common_c, "void Com_StartupVariable( const char *match ) {")
	startup_commands_block = _extract_function_block(common_c, "qboolean Com_AddStartupCommands( void ) {")
	shutdown_block = _extract_function_block(common_c, "void Com_Shutdown (void) {")
	string_contains_block = _extract_function_block(common_c, "char *Com_StringContains(char *str1, char *str2, int casesensitive) {")

	assert 'if (!buffer || !buffersize || !flush)' in begin_redirect_block
	assert 'rd_buffer = buffer;' in begin_redirect_block
	assert 'rd_buffersize = buffersize;' in begin_redirect_block
	assert 'rd_flush = flush;' in begin_redirect_block
	assert '*rd_buffer = 0;' in begin_redirect_block

	assert 'if ( rd_flush ) {' in end_redirect_block
	assert 'rd_flush(rd_buffer);' in end_redirect_block
	assert 'rd_buffer = NULL;' in end_redirect_block
	assert 'rd_buffersize = 0;' in end_redirect_block
	assert 'rd_flush = NULL;' in end_redirect_block

	assert 'if ( com_consoleLineBuffer ) {' in free_startup_lines_block
	assert 'free( com_consoleLineBuffer );' in free_startup_lines_block
	assert 'Com_Memset( com_consoleLines, 0, sizeof( com_consoleLines ) );' in free_startup_lines_block
	assert 'com_numConsoleLines = 0;' in free_startup_lines_block

	assert 'if ( !line || !line[0] || arg < 0 ) {' in startup_argv_block
	assert 'line += strlen( line ) + 1;' in startup_argv_block
	assert 'if ( !line[0] ) {' in startup_argv_block
	assert 'return "";' in startup_argv_block

	assert 'Com_FreeStartupCommandLines();' in parse_block
	assert 'Cmd_TokenizeString( commandLine );' in parse_block
	assert 'argc = Cmd_Argc();' in parse_block
	assert 'if ( token[0] == \'+\' ) {' in parse_block
	assert 'if ( !Q_stricmp( token, "+bind" ) ) {' in parse_block
	assert 'if ( bindCommandIndex <= 0 || effectiveIndex - 2 != bindCommandIndex ) {' in parse_block
	assert 'token++;' in parse_block
	assert 'if ( com_numConsoleLines != 0 ) {' in parse_block
	assert '*cursor++ = \'\\0\';' in parse_block
	assert 'com_consoleLines[com_numConsoleLines] = cursor;' in parse_block
	assert 'Com_Memcpy( cursor, token, tokenLength + 1 );' in parse_block

	assert 'pidLength = FS_FOpenFileRead( "profile.pid", &f, qtrue );' in profile_pid_block
	assert 'if ( pidLength < 0 || !f ) {' in profile_pid_block
	assert 'Com_Memset( pidBuffer, 0, sizeof( pidBuffer ) );' in profile_pid_block
	assert 'if ( FS_Read( pidBuffer, sizeof( pidBuffer ) - 1, f ) < 0 ) {' in profile_pid_block
	assert 'FS_FCloseFile( f );' in profile_pid_block
	assert 'retainedPid = atoi( pidBuffer );' in profile_pid_block
	assert 'if ( retainedPid > 0 && com_pid && retainedPid != com_pid->integer ) {' in profile_pid_block

	assert 'if ( com_crashed && com_crashed->integer' in safe_mode_block
	assert '&& ( !com_ignorecrash || !com_ignorecrash->integer ) ) {' in safe_mode_block
	assert 'if ( !Q_stricmp( com_consoleLines[i], "safe" )' in safe_mode_block
	assert '|| !Q_stricmp( com_consoleLines[i], "cvar_restart" ) ) {' in safe_mode_block
	assert 'com_consoleLines[i][0] = 0;' in safe_mode_block

	assert 'if ( strcmp( com_consoleLines[i], "set" ) ) {' in startup_variable_block
	assert 's = Com_StartupLineArgv( com_consoleLines[i], 1 );' in startup_variable_block
	assert 'Cvar_Set( s, Com_StartupLineArgv( com_consoleLines[i], 2 ) );' in startup_variable_block
	assert 'cv = Cvar_Get( s, "", 0 );' in startup_variable_block
	assert 'cv->flags |= CVAR_USER_CREATED;' in startup_variable_block

	assert 'added = qfalse;' in startup_commands_block
	assert 'if ( Q_stricmp( com_consoleLines[i], "set" ) ) {' in startup_commands_block
	assert 'added = qtrue;' in startup_commands_block
	assert 'Cbuf_AddTokenized( com_consoleLines[i] );' in startup_commands_block

	assert 'if (logfile) {' in shutdown_block
	assert 'FS_FCloseFile (logfile);' in shutdown_block
	assert 'FS_WriteFile( "profile.pid", "0", 1 );' in shutdown_block
	assert 'Zmq_ShutdownRuntime();' in shutdown_block
	assert 'QL_Steamworks_Shutdown();' in shutdown_block
	assert 'SyscallContract_Shutdown();' in shutdown_block
	assert 'Com_FreeStartupCommandLines();' in shutdown_block

	assert 'len = strlen(str1) - strlen(str2);' in string_contains_block
	assert 'if (casesensitive) {' in string_contains_block
	assert 'if (toupper(str1[j]) != toupper(str2[j])) {' in string_contains_block
	assert 'return NULL;' in string_contains_block


def test_qcommon_memory_allocator_and_hunk_helpers_match_retail_contracts() -> None:
	common_c = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")

	info_print_block = _extract_function_block(common_c, "void Info_Print( const char *s ) {")
	free_block = _extract_function_block(common_c, "void Z_Free( void *ptr ) {")
	tag_malloc_block = _extract_function_block(common_c, "void *Z_TagMalloc( int size, int tag ) {")
	malloc_block = _extract_function_block(common_c, "void *Z_Malloc( int size ) {")
	s_malloc_block = _extract_function_block(common_c, "void *S_Malloc( int size ) {")
	check_heap_block = _extract_function_block(common_c, "void Z_CheckHeap( void ) {")
	copy_string_block = _extract_function_block(common_c, "char *CopyString( const char *in ) {")
	init_small_zone_block = _extract_function_block(common_c, "void Com_InitSmallZoneMemory( void ) {")
	init_zone_block = _extract_function_block(common_c, "void Com_InitZoneMemory( void ) {")
	hunk_clear_block = _extract_function_block(common_c, "void Hunk_Clear( void ) {")
	alloc_temp_block = _extract_function_block(common_c, "void *Hunk_AllocateTempMemory( int size ) {")
	free_temp_block = _extract_function_block(common_c, "void Hunk_FreeTempMemory( void *buf ) {")

	assert "if (*s == '\\\\')" in info_print_block
	assert "Com_Memset (o, ' ', 20-l);" in info_print_block
	assert 'Com_Printf ("%s", key);' in info_print_block
	assert 'Com_Printf ("MISSING VALUE\\n");' in info_print_block
	assert 'Com_Printf ("%s\\n", value);' in info_print_block

	assert 'block = (memblock_t *) ( (byte *)ptr - sizeof(memblock_t));' in free_block
	assert 'if (block->id != ZONEID) {' in free_block
	assert 'if (block->tag == TAG_STATIC) {' in free_block
	assert 'Com_Memset( ptr, 0xaa, block->size - sizeof( *block ) );' in free_block
	assert 'zone->rover = block;' in free_block
	assert 'if ( !other->tag ) {' in free_block

	assert 'if (!tag) {' in tag_malloc_block
	assert 'Com_Error( ERR_FATAL, "Z_TagMalloc: tried to use a 0 tag" );' in tag_malloc_block
	assert 'size += sizeof(memblock_t);' in tag_malloc_block
	assert 'size += 4;' in tag_malloc_block
	assert 'size = (size + 3) & ~3;' in tag_malloc_block
	assert 'Com_Error( ERR_FATAL, "Z_Malloc: failed on allocation of %i bytes from the %s zone",' in tag_malloc_block
	assert '*(int *)((byte *)base + base->size - 4) = ZONEID;' in tag_malloc_block

	assert 'buf = Z_TagMalloc( size, TAG_GENERAL );' in malloc_block
	assert 'Com_Memset( buf, 0, size );' in malloc_block
	assert 'return Z_TagMalloc( size, TAG_SMALL );' in s_malloc_block

	assert 'Com_Error( ERR_FATAL, "Z_CheckHeap: block size does not touch the next block\\n" );' in check_heap_block
	assert 'Com_Error( ERR_FATAL, "Z_CheckHeap: next block doesn\'t have proper back link\\n" );' in check_heap_block
	assert 'Com_Error( ERR_FATAL, "Z_CheckHeap: two consecutive free blocks\\n" );' in check_heap_block

	assert 'return ((char *)&emptystring) + sizeof(memblock_t);' in copy_string_block
	assert "return ((char *)&numberstring[in[0]-'0']) + sizeof(memblock_t);" in copy_string_block
	assert 'out = S_Malloc (strlen(in)+1);' in copy_string_block
	assert 'strcpy (out, in);' in copy_string_block

	assert 's_smallZoneTotal = 512 * 1024;' in init_small_zone_block
	assert 'smallzone = calloc( s_smallZoneTotal, 1 );' in init_small_zone_block
	assert 'Com_Error( ERR_FATAL, "Small zone data failed to allocate %1.1f megs", (float)s_smallZoneTotal / (1024*1024) );' in init_small_zone_block
	assert 'Z_ClearZone( smallzone, s_smallZoneTotal );' in init_small_zone_block

	assert 'cv = Cvar_Get( "com_zoneMegs", DEF_COMZONEMEGS, CVAR_LATCH | CVAR_ARCHIVE );' in init_zone_block
	assert 'if ( cv->integer < 20 ) {' in init_zone_block
	assert 's_zoneTotal = 1024 * 1024 * 16;' in init_zone_block
	assert 'mainzone = calloc( s_zoneTotal, 1 );' in init_zone_block
	assert 'Com_Error( ERR_FATAL, "Zone data failed to allocate %i megs", s_zoneTotal / (1024*1024) );' in init_zone_block
	assert 'Z_ClearZone( mainzone, s_zoneTotal );' in init_zone_block

	assert 'CL_ShutdownCGame();' in hunk_clear_block
	assert 'CL_ShutdownUI();' in hunk_clear_block
	assert 'SV_ShutdownGameProgs();' in hunk_clear_block
	assert 'CIN_CloseAllVideos();' in hunk_clear_block
	assert 'hunk_permanent = &hunk_low;' in hunk_clear_block
	assert 'hunk_temp = &hunk_high;' in hunk_clear_block
	assert 'Com_Printf( "Hunk_Clear: reset the hunk ok\\n" );' in hunk_clear_block
	assert 'VM_Clear();' in hunk_clear_block

	assert 'if ( s_hunkData == NULL )' in alloc_temp_block
	assert 'return Z_Malloc(size);' in alloc_temp_block
	assert 'Hunk_SwapBanks();' in alloc_temp_block
	assert 'size = ( (size+3)&~3 ) + sizeof( hunkHeader_t );' in alloc_temp_block
	assert 'Com_Error( ERR_DROP, "Hunk_AllocateTempMemory: failed on %i", size );' in alloc_temp_block
	assert 'hdr->magic = HUNK_MAGIC;' in alloc_temp_block
	assert 'hdr->size = size;' in alloc_temp_block

	assert 'if ( s_hunkData == NULL )' in free_temp_block
	assert 'Z_Free(buf);' in free_temp_block
	assert 'if ( hdr->magic != HUNK_MAGIC ) {' in free_temp_block
	assert 'Com_Error( ERR_FATAL, "Hunk_FreeTempMemory: bad magic" );' in free_temp_block
	assert 'hdr->magic = HUNK_FREE_MAGIC;' in free_temp_block
	assert 'Com_Printf( "Hunk_FreeTempMemory: not the final block\\n" );' in free_temp_block


def test_qcommon_journaling_and_event_helpers_match_retail_contracts() -> None:
	common_c = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")

	init_journaling_block = _extract_function_block(common_c, "void Com_InitJournaling( void ) {")
	get_real_event_block = _extract_function_block(common_c, "Com_GetRealEvent( void ) {")
	push_event_block = _extract_function_block(common_c, "void Com_PushEvent( sysEvent_t *event ) {")
	get_event_block = _extract_function_block(common_c, "Com_GetEvent( void ) {")

	assert 'Com_StartupVariable( "journal" );' in init_journaling_block
	assert 'com_journal = Cvar_Get ("journal", "0", CVAR_INIT);' in init_journaling_block
	assert 'com_journalFile = FS_FOpenFileWrite( "journal.dat" );' in init_journaling_block
	assert 'com_journalDataFile = FS_FOpenFileWrite( "journaldata.dat" );' in init_journaling_block
	assert 'FS_FOpenFileRead( "journal.dat", &com_journalFile, qtrue );' in init_journaling_block
	assert 'FS_FOpenFileRead( "journaldata.dat", &com_journalDataFile, qtrue );' in init_journaling_block
	assert 'Cvar_Set( "com_journal", "0" );' in init_journaling_block
	assert 'Com_Printf( "Couldn\'t open journal files\\n" );' in init_journaling_block

	assert 'if ( com_journal->integer == 2 ) {' in get_real_event_block
	assert 'r = FS_Read( &ev, sizeof(ev), com_journalFile );' in get_real_event_block
	assert 'Com_Error( ERR_FATAL, "Error reading from journal file" );' in get_real_event_block
	assert 'if ( ev.evPtrLength ) {' in get_real_event_block
	assert 'ev.evPtr = Z_Malloc( ev.evPtrLength );' in get_real_event_block
	assert 'ev = Sys_GetEvent();' in get_real_event_block
	assert 'if ( com_journal->integer == 1 ) {' in get_real_event_block
	assert 'r = FS_Write( &ev, sizeof(ev), com_journalFile );' in get_real_event_block
	assert 'Com_Error( ERR_FATAL, "Error writing to journal file" );' in get_real_event_block

	assert 'static int printedWarning = 0;' in push_event_block
	assert 'ev = &com_pushedEvents[ com_pushedEventsHead & (MAX_PUSHED_EVENTS-1) ];' in push_event_block
	assert 'if ( com_pushedEventsHead - com_pushedEventsTail >= MAX_PUSHED_EVENTS ) {' in push_event_block
	assert 'printedWarning = qtrue;' in push_event_block
	assert 'Com_Printf( "WARNING: Com_PushEvent overflow\\n" );' in push_event_block
	assert 'if ( ev->evPtr ) {' in push_event_block
	assert 'Z_Free( ev->evPtr );' in push_event_block
	assert 'com_pushedEventsTail++;' in push_event_block
	assert '*ev = *event;' in push_event_block
	assert 'com_pushedEventsHead++;' in push_event_block

	assert 'if ( com_pushedEventsHead > com_pushedEventsTail ) {' in get_event_block
	assert 'com_pushedEventsTail++;' in get_event_block
	assert 'return com_pushedEvents[ (com_pushedEventsTail-1) & (MAX_PUSHED_EVENTS-1) ];' in get_event_block
	assert 'return Com_GetRealEvent();' in get_event_block


def test_qcommon_cvar_and_changevectors_command_surface_matches_retail_registration_order() -> None:
	cvar_c = (REPO_ROOT / "src/code/qcommon/cvar.c").read_text(encoding="utf-8")
	common_c = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")

	cvar_init_block = _extract_function_block(cvar_c, "void Cvar_Init (void) {")
	com_init_block = _extract_function_block(common_c, "void Com_Init( char *commandLine ) {")

	command_lines = [
		'Cmd_AddCommand ("reset", Cvar_Reset_f);',
		'Cmd_AddCommand ("clearcvar", Cvar_Clear_f);',
		'Cmd_AddCommand ("cvarlist", Cvar_List_f);',
		'Cmd_AddCommand ("listcvars", Cvar_List_f);',
		'Cmd_AddCommand ("cvar_restart", Cvar_Restart_f);',
		'Cmd_AddCommand ("cvarAdd", Cvar_Add_f);',
		'Cmd_AddCommand ("cvarMult", Cvar_Mult_f);',
	]
	positions = []
	for command_line in command_lines:
		assert command_line in cvar_init_block
		positions.append(cvar_init_block.index(command_line))

	assert positions == sorted(positions)
	assert 'Cmd_AddCommand ("changeVectors", MSG_ReportChangeVectors_f );' in com_init_block


def test_qcommon_cvar_and_changevectors_handlers_match_retail_contracts() -> None:
	cvar_c = (REPO_ROOT / "src/code/qcommon/cvar.c").read_text(encoding="utf-8")
	msg_c = (REPO_ROOT / "src/code/qcommon/msg.c").read_text(encoding="utf-8")

	clear_block = _extract_function_block(cvar_c, "void Cvar_Clear_f( void ) {")
	list_block = _extract_function_block(cvar_c, "void Cvar_List_f( void ) {")
	restart_block = _extract_function_block(cvar_c, "void Cvar_Restart_f( void ) {")
	add_block = _extract_function_block(cvar_c, "void Cvar_Add_f( void ) {")
	mult_block = _extract_function_block(cvar_c, "void Cvar_Mult_f( void ) {")
	change_vectors_block = _extract_function_block(msg_c, "void MSG_ReportChangeVectors_f( void ) {")

	assert 'Com_Printf ("usage: clearcvar <variable>\\n");' in clear_block
	assert 'Cvar_Set2( Cmd_Argv( 1 ), "", qtrue );' in clear_block

	assert 'if (match && !Com_Filter(match, var->name, qfalse)) continue;' in list_block
	assert 'Com_Printf (" %s \\"%s\\"\\n", var->name, var->string);' in list_block
	assert 'Com_Printf ("\\n%i total cvars\\n", i);' in list_block
	assert 'Com_Printf ("%i cvar indexes\\n", cvar_numIndexes);' in list_block

	assert 'if ( var->flags & ( CVAR_ROM | CVAR_INIT | CVAR_NORESTART | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD ) ) {' in restart_block
	assert 'Com_DPrintf( "Skipping restart of protected cvar %s\\n", var->name );' in restart_block
	assert 'if ( var->flags & CVAR_USER_CREATED ) {' in restart_block
	assert 'Com_Memset( var, 0, sizeof( *var ) );' in restart_block
	assert 'Cvar_Set( var->name, var->resetString );' in restart_block

	assert 'Com_Printf ("usage: cvarAdd <variable> <amount>\\n");' in add_block
	assert 'var = Cvar_FindVar( Cmd_Argv( 1 ) );' in add_block
	assert 'currentValue = var->value;' in add_block
	assert 'currentValue = 0.0f;' in add_block
	assert 'amount = (float)atof( Cmd_Argv( 2 ) );' in add_block
	assert 'Cvar_Set2( Cmd_Argv( 1 ), va("%0.3f", currentValue + amount), qfalse );' in add_block

	assert 'Com_Printf ("usage: cvarMult <variable> <amount>\\n");' in mult_block
	assert 'var = Cvar_FindVar( Cmd_Argv( 1 ) );' in mult_block
	assert 'currentValue = var->value;' in mult_block
	assert 'currentValue = 0.0f;' in mult_block
	assert 'amount = (float)atof( Cmd_Argv( 2 ) );' in mult_block
	assert 'Cvar_Set2( Cmd_Argv( 1 ), va("%0.3f", currentValue * amount), qfalse );' in mult_block

	assert 'for(i=0;i<256;i++) {' in change_vectors_block
	assert 'if (pcount[i]) {' in change_vectors_block
	assert 'Com_Printf("%d used %d\\n", i, pcount[i]);' in change_vectors_block


def test_client_connect_and_demo_commands_match_retail_contracts() -> None:
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

	record_block = _extract_function_block(cl_main, "void CL_Record_f( void ) {")
	stop_record_block = _extract_function_block(cl_main, "void CL_StopRecord_f( void ) {")
	demo_block = _extract_function_block(cl_main, "void CL_PlayDemo_f( void ) {")
	demo_completed_block = _extract_function_block(cl_main, "void CL_DemoCompleted( void ) {")
	reconnect_block = _extract_function_block(cl_main, "void CL_Reconnect_f( void ) {")
	connect_block = _extract_function_block(cl_main, "void CL_Connect_f( void ) {")

	assert 'Com_Printf ("Correct usage: record <demoname>\\n");' in record_block
	assert 'Com_Printf ("Already recording.\\n");' in record_block
	assert "CL_StopRecord_f();" in record_block
	assert 'Com_Error( ERR_FATAL, "stoprecord failed" );' in record_block
	assert 'Com_Printf ("recording to %s.\\n", name);' in record_block
	assert "CL_WebView_PublishGameDemo( name, name );" in record_block
	assert 'MSG_WriteByte (&buf, svc_gamestate);' in record_block
	assert "CL_WebView_PublishGameDemo" not in stop_record_block

	assert 'Com_Printf ("playdemo <demoname>\\n");' in demo_block
	assert 'SV_Shutdown( "Starting Demo.\\n" );' in demo_block
	assert 'CL_Disconnect( qfalse );' in demo_block
	assert 'CL_WalkDemoExt( arg, name, &clc.demofile );' in demo_block
	assert "CL_Disconnect( qtrue );" in demo_completed_block
	assert "CL_NextDemo();" in demo_completed_block
	assert "if ( cl_quitOnDemoCompleted && cl_quitOnDemoCompleted->integer ) {" in demo_completed_block
	assert 'Cbuf_AddText( "quit\\n" );' in demo_completed_block

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


def test_filesystem_filtered_directory_and_touch_commands_match_retail_contracts() -> None:
	files_c = (REPO_ROOT / "src/code/qcommon/files.c").read_text(encoding="utf-8")

	newdir_block = _extract_function_block(files_c, "void FS_NewDir_f( void ) {")
	touch_block = _extract_function_block(files_c, "void FS_TouchFile_f( void ) {")

	assert 'Com_Printf( "usage: fdir <filter>\\n" );' in newdir_block
	assert 'Com_Printf( "example: fdir *q3dm*.bsp\\n");' in newdir_block
	assert 'dirnames = FS_ListFilteredFiles( "", "", filter, &ndirs );' in newdir_block
	assert 'FS_SortFileList(dirnames, ndirs);' in newdir_block
	assert 'FS_ConvertPath(dirnames[i]);' in newdir_block
	assert 'Com_Printf( "%d files listed\\n", ndirs );' in newdir_block

	assert 'if ( Cmd_Argc() != 2 ) {' in touch_block
	assert 'Com_Printf( "Usage: touchFile <file>\\n" );' in touch_block
	assert 'FS_FOpenFileRead( Cmd_Argv( 1 ), &f, qfalse );' in touch_block
	assert 'FS_FCloseFile( f );' in touch_block

	assert 'Cmd_AddCommand ("fdir", FS_NewDir_f );' in files_c
	assert 'Cmd_AddCommand ("touchFile", FS_TouchFile_f );' in files_c


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
