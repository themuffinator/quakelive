import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CL_MAIN_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_main.c"
CL_CGAME_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
CL_KEYS_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_keys.c"
CG_DRAW_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_VIEW_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_view.c"
COMMON_C_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "common.c"
QCOMMON_H_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "qcommon.h"
ALIASES_PATH = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
FUNCTIONS_CSV_PATH = REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "quakelive_steam_srp" / "functions.csv"
HLIL_PART01_PATH = REPO_ROOT / "references" / "hlil" / "quakelive" / "quakelive_steam.exe" / "quakelive_steam.exe_hlil_split" / "quakelive_steam.exe_hlil_part01.txt"
HLIL_PART04_PATH = REPO_ROOT / "references" / "hlil" / "quakelive" / "quakelive_steam.exe" / "quakelive_steam.exe_hlil_split" / "quakelive_steam.exe_hlil_part04.txt"
CGAME_SYMBOL_MAP_PATH = REPO_ROOT / "references" / "symbol-maps" / "cgame.json"
MAPPING_NOTE_PATH = REPO_ROOT / "docs" / "reverse-engineering" / "demo-record-playback-mapping-2026-06-06.md"


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _function_block(source: str, signature: str) -> str:
	start = source.index(signature)
	brace = source.index("{", start)
	depth = 0
	for index in range(brace, len(source)):
		char = source[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start:index + 1]
	raise AssertionError(f"function block not closed for {signature}")


def _assert_order(block: str, *needles: str) -> None:
	position = -1
	for needle in needles:
		next_position = block.find(needle, position + 1)
		assert next_position != -1, needle
		position = next_position


def test_demo_recording_envelope_and_protocol_91_extension_match_retail_evidence() -> None:
	cl_main = _read(CL_MAIN_PATH)
	common_c = _read(COMMON_C_PATH)
	qcommon_h = _read(QCOMMON_H_PATH)
	aliases = json.loads(_read(ALIASES_PATH))
	functions_csv = _read(FUNCTIONS_CSV_PATH)
	hlil = _read(HLIL_PART04_PATH)

	assert "#define\tQL_RETAIL_PROTOCOL_VERSION\t91" in qcommon_h
	assert "#define\tPROTOCOL_VERSION\tQL_RETAIL_PROTOCOL_VERSION" in qcommon_h
	assert "int demo_protocols[] =\n{ QL_RETAIL_PROTOCOL_VERSION, 0 };" in common_c
	assert "return NET_GetProtocolProfile()->demoProtocol;" in _function_block(common_c, "int NET_DemoProtocol( void )")

	assert aliases["quakelive_steam_srp"]["sub_4B82A0"] == "CL_WriteDemoMessage"
	assert aliases["quakelive_steam_srp"]["sub_4B8300"] == "CL_StopRecord_f"
	assert aliases["quakelive_steam_srp"]["sub_4B8390"] == "CL_DemoFilename"
	assert aliases["quakelive_steam_srp"]["sub_4B8430"] == "CL_Record_f"
	assert "FUN_004b82a0,004b82a0,93,0,unknown" in functions_csv
	assert "FUN_004b8300,004b8300,131,0,unknown" in functions_csv
	assert "FUN_004b8390,004b8390,145,0,unknown" in functions_csv
	assert "FUN_004b8430,004b8430,875,0,unknown" in functions_csv
	assert 'sub_4d9160(&var_108, 0x100, "demos/%s.dm_%d")' in hlil
	assert 'sub_4f3b90(&var_108)' in hlil

	write_demo = _function_block(cl_main, "void CL_WriteDemoMessage")
	_assert_order(
		write_demo,
		"len = clc.serverMessageSequence;",
		"swlen = LittleLong( len );",
		"FS_Write (&swlen, 4, clc.demofile);",
		"len = msg->cursize - headerBytes;",
		"swlen = LittleLong(len);",
		"FS_Write (&swlen, 4, clc.demofile);",
		"FS_Write ( msg->data + headerBytes, len, clc.demofile );",
	)

	stop_record = _function_block(cl_main, "void CL_StopRecord_f( void )")
	_assert_order(
		stop_record,
		"if ( !clc.demorecording ) {",
		"Com_Printf (\"Not recording a demo.\\n\");",
		"len = -1;",
		"FS_Write (&len, 4, clc.demofile);",
		"FS_Write (&len, 4, clc.demofile);",
		"FS_FCloseFile (clc.demofile);",
		"clc.demorecording = qfalse;",
		"clc.spDemoRecording = qfalse;",
		"Com_Printf (\"Stopped demo.\\n\");",
	)

	record = _function_block(cl_main, "void CL_Record_f( void )")
	assert 'Com_sprintf (name, sizeof(name), "demos/%s.dm_%d", demoName, NET_DemoProtocol() );' in record
	assert "CL_WebView_PublishGameDemo( name, name );" in record
	assert "clc.demowaiting = qtrue;" in record
	assert "MSG_WriteByte (&buf, svc_gamestate);" in record
	assert "MSG_WriteLong(&buf, clc.clientNum);" in record
	assert "MSG_WriteLong(&buf, clc.checksumFeed);" in record
	assert "len = LittleLong( clc.serverMessageSequence - 1 );" in record


def test_demo_playback_reader_fallback_completion_and_time_wiring_match_retail() -> None:
	cl_main = _read(CL_MAIN_PATH)
	cl_cgame = _read(CL_CGAME_PATH)
	aliases = json.loads(_read(ALIASES_PATH))
	functions_csv = _read(FUNCTIONS_CSV_PATH)
	hlil = _read(HLIL_PART04_PATH)

	assert aliases["quakelive_steam_srp"]["sub_4B87A0"] == "CL_WalkDemoExt"
	assert aliases["quakelive_steam_srp"]["sub_4B8830"] == "CL_NextDemo"
	assert aliases["quakelive_steam_srp"]["sub_4BB2A0"] == "CL_DemoCompleted"
	assert aliases["quakelive_steam_srp"]["sub_4BB330"] == "CL_ReadDemoMessage"
	assert aliases["quakelive_steam_srp"]["sub_4BB450"] == "CL_PlayDemo_f"
	assert "FUN_004bb2a0,004bb2a0,135,0,unknown" in functions_csv
	assert "FUN_004bb330,004bb330,285,0,unknown" in functions_csv
	assert "FUN_004bb450,004bb450,561,0,unknown" in functions_csv
	assert 'sub_4c9b60(1, "CL_ReadDemoMessage: demoMsglen >' in hlil
	assert 'sub_4c9860(esi_1, "Protocol %d not supported for de' in hlil
	assert 'sub_4d9160(&var_108, 0x100, "demos/%s")' in hlil

	read_demo = _function_block(cl_main, "void CL_ReadDemoMessage")
	_assert_order(
		read_demo,
		"r = FS_Read( &s, 4, clc.demofile);",
		"clc.serverMessageSequence = LittleLong( s );",
		"r = FS_Read (&buf.cursize, 4, clc.demofile);",
		"buf.cursize = LittleLong( buf.cursize );",
		"if ( buf.cursize == -1 ) {",
		"if ( buf.cursize > buf.maxsize ) {",
		"Com_Error (ERR_DROP, \"CL_ReadDemoMessage: demoMsglen > MAX_MSGLEN\");",
		"r = FS_Read( buf.data, buf.cursize, clc.demofile );",
		"Com_Printf( \"Demo file was truncated.\\n\");",
		"CL_ParseServerMessage( &buf );",
	)

	walk_demo = _function_block(cl_main, "static void CL_WalkDemoExt")
	assert "while(demo_protocols[i])" in walk_demo
	assert 'Com_sprintf (name, MAX_OSPATH, "demos/%s.dm_%d", arg, demo_protocols[i]);' in walk_demo
	assert 'Com_Printf("Demo file: %s\\n", name);' in walk_demo
	assert 'Com_Printf("Not found: %s\\n", name);' in walk_demo

	play_demo = _function_block(cl_main, "void CL_PlayDemo_f( void )")
	_assert_order(
		play_demo,
		"SV_Shutdown( \"Starting Demo.\\n\" );",
		"CL_Disconnect( qfalse );",
		"ext_test = arg + strlen(arg) - 6;",
		"protocol = atoi(ext_test+4);",
		"while(demo_protocols[i])",
		"Com_Printf(\"Protocol %d not supported for demos\\n\", protocol);",
		"CL_WalkDemoExt( retry, name, &clc.demofile );",
		"CL_WalkDemoExt( arg, name, &clc.demofile );",
		"cls.state = CA_CONNECTED;",
		"clc.demoplaying = qtrue;",
		"while ( cls.state >= CA_CONNECTED && cls.state < CA_PRIMED ) {",
		"clc.firstDemoFrameSkipped = qfalse;",
	)

	completed = _function_block(cl_main, "void CL_DemoCompleted( void )")
	assert "CL_Disconnect( qtrue );" in completed
	assert "CL_NextDemo();" in completed
	assert "if ( cl_quitOnDemoCompleted && cl_quitOnDemoCompleted->integer ) {" in completed
	assert 'Cbuf_AddText( "quit\\n" );' in completed

	set_time = _function_block(cl_cgame, "void CL_SetCGameTime( void )")
	assert "if ( clc.demoplaying ) {" in set_time
	assert "CL_ReadDemoMessage();" in set_time
	assert "if ( cl_timedemo->integer ) {" in set_time
	assert "cl.serverTime = clc.timeDemoBaseTime + clc.timeDemoFrames * 50;" in set_time


def test_browser_console_and_cgame_demo_wiring_preserve_retail_split() -> None:
	cl_cgame = _read(CL_CGAME_PATH)
	cl_keys = _read(CL_KEYS_PATH)
	cg_draw = _read(CG_DRAW_PATH)
	cg_view = _read(CG_VIEW_PATH)
	cgame_symbol_map = _read(CGAME_SYMBOL_MAP_PATH)
	hlil_part01 = _read(HLIL_PART01_PATH)

	demo_list = _function_block(cl_cgame, "static void CL_WebHost_BuildDemoListJson")
	assert 'Com_sprintf( demoExt, sizeof( demoExt ), "dm_%d", NET_DemoProtocol() );' in demo_list
	assert 'count = FS_GetFileList( "demos", demoExt, fileList, sizeof( fileList ) );' in demo_list
	assert "CL_WebHost_JsonAppendDemoCallback( &builder, demoName );" in demo_list
	assert "fullDemoExt" not in demo_list
	assert "demoName[length" not in demo_list
	assert 'sub_4d0db0("demos", "dm_91", j_2)' in hlil_part01
	assert "Awesomium::JSArray::Push" in hlil_part01

	demo_callback = _function_block(cl_cgame, "static void CL_WebHost_JsonAppendDemoCallback")
	assert 'Q_strcat( builder->buffer, builder->bufferSize, "\\"" );' in demo_callback
	assert "CL_WebHost_AppendJsonEscaped( builder->buffer, builder->bufferSize, name );" in demo_callback

	console_argument = _function_block(cl_keys, "static void Console_CompleteArgument")
	assert 'if ( Q_stricmp( command, "demo" ) && Q_stricmp( command, "\\\\demo" ) ) {' in console_argument
	assert 'files = FS_ListFiles( "demos", ".dm_73", &fileCount );' in console_argument

	cgame_rendering = _function_block(cl_cgame, "void CL_CGameRendering( stereoFrame_t stereo )")
	assert "qboolean\tdemoPlaying;" in cgame_rendering
	assert "demoPlaying = clc.demoplaying ? qtrue : qfalse;" in cgame_rendering
	assert "VM_Call( cgvm, CG_DRAW_ACTIVE_FRAME, cl.serverTime, stereo, demoPlaying );" in cgame_rendering

	draw_active = _function_block(cg_view, "void CG_DrawActiveFrame( int serverTime, stereoFrame_t stereoView, qboolean demoPlayback )")
	assert "cg.demoPlayback = demoPlayback;" in draw_active

	demo_controls = _function_block(cg_draw, "static void CG_DrawDemoPlaybackControls")
	assert 'freezeDemo = trap_Cvar_VariableValue( "cl_freezeDemo" );' in demo_controls
	assert '"[SPACE]"' in demo_controls
	assert '"[LEFT]"' in demo_controls
	assert '"[RIGHT]"' in demo_controls
	assert '"[DOWN]"' in demo_controls
	assert '"[DEL]"' in demo_controls
	assert "CG_DrawDemoPlaybackControls" in cgame_symbol_map

	draw_2d = _function_block(cg_draw, "static void CG_Draw2D")
	assert "if ( cg.demoPlayback && cg_drawDemoHUD.integer ) {" in draw_2d
	assert "CG_DrawDemoPlaybackControls( 0 );" in draw_2d


def test_demo_mapping_note_records_observed_facts_and_bounded_source_change() -> None:
	mapping_note = _read(MAPPING_NOTE_PATH)

	assert "sub_4B82A0" in mapping_note
	assert "sub_4B8300" in mapping_note
	assert "sub_4B8430" in mapping_note
	assert "sub_4BB330" in mapping_note
	assert "sub_4BB450" in mapping_note
	assert "0x0043335B" in mapping_note
	assert "`demos`, `dm_91`" in mapping_note
	assert "raw file-list entries" in mapping_note
	assert "console completion still scans `.dm_73`" in mapping_note
	assert "before 96% -> after 99%" in mapping_note
