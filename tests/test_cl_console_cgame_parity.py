"""Guard the retail cgame/chat host seam against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_PUBLIC = REPO_ROOT / "src" / "code" / "cgame" / "cg_public.h"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CL_MAIN = REPO_ROOT / "src" / "code" / "client" / "cl_main.c"
CL_CONSOLE = REPO_ROOT / "src" / "code" / "client" / "cl_console.c"
CL_KEYS = REPO_ROOT / "src" / "code" / "client" / "cl_keys.c"
CL_SCRN = REPO_ROOT / "src" / "code" / "client" / "cl_scrn.c"
VM_C = REPO_ROOT / "src" / "code" / "qcommon" / "vm.c"


def _block_from_marker(source: str, marker: str) -> str:
	start = source.rindex(marker)
	brace_start = source.index("{", start)
	depth = 0

	for index in range(brace_start, len(source)):
		char = source[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start:index + 1]

	raise AssertionError(f"Unbalanced block for marker: {marker}")


def test_cgame_export_enum_includes_retail_native_tail() -> None:
	source = CG_PUBLIC.read_text(encoding="utf-8")

	assert "#define CG_CLIENT_IDENTITY_NAME_CHARS\t40" in source
	assert "typedef struct {" in source
	assert "char\t\t\tdisplayName[CG_CLIENT_IDENTITY_NAME_CHARS];" in source
	assert "char\t\t\tcleanName[CG_CLIENT_IDENTITY_NAME_CHARS];" in source

	enum_order = (
		"CG_CHAT_DOWN",
		"CG_CHAT_UP",
		"CG_SHOW_1ST_TRACKED_PLAYER",
		"CG_SHOW_2ND_TRACKED_PLAYER",
		"CG_COPY_CLIENT_IDENTITY",
		"CG_GET_CHAT_FIELD_Y",
		"CG_GET_CHAT_FIELD_PIXEL_WIDTH",
		"CG_GET_CHAT_FIELD_WIDTH_IN_CHARS",
		"CG_SET_CLIENT_SPEAKING_STATE",
		"CG_GET_PHYSICS_TIME",
	)

	positions = [source.index(name) for name in enum_order]
	assert positions == sorted(positions)


def test_vmMain_and_native_dispatch_expose_retail_tail_slots() -> None:
	cg_main_source = CG_MAIN.read_text(encoding="utf-8")
	vm_source = VM_C.read_text(encoding="utf-8")
	vm_main_block = _block_from_marker(cg_main_source, "int vmMain")

	for expected in (
		"case CG_CHAT_DOWN:",
		"case CG_CHAT_UP:",
		"case CG_SHOW_1ST_TRACKED_PLAYER:",
		"case CG_SHOW_2ND_TRACKED_PLAYER:",
		"case CG_COPY_CLIENT_IDENTITY:",
		"case CG_GET_CHAT_FIELD_Y:",
		"case CG_GET_CHAT_FIELD_PIXEL_WIDTH:",
		"case CG_GET_CHAT_FIELD_WIDTH_IN_CHARS:",
		"case CG_SET_CLIENT_SPEAKING_STATE:",
		"case CG_GET_PHYSICS_TIME:",
	):
		assert expected in vm_main_block
		assert expected in vm_source

	assert "return CG_CopyClientIdentity( arg0, (void *)(intptr_t)arg1 );" in vm_main_block
	assert "return CG_NativeGetChatFieldY();" in vm_main_block
	assert "return CG_NativeGetChatFieldPixelWidth();" in vm_main_block
	assert "return CG_GetChatFieldWidthInChars();" in vm_main_block
	assert "return CG_NativeSetClientSpeakingState( arg0, arg1 );" in vm_main_block
	assert "return CG_GetPhysicsTime();" in vm_main_block
	assert "static int CG_NativeGetChatFieldY( void ) {" in cg_main_source
	assert "return (int)CG_GetChatFieldY();" in cg_main_source
	assert "static int CG_NativeGetChatFieldPixelWidth( void ) {" in cg_main_source
	assert "return (int)CG_GetChatFieldPixelWidth();" in cg_main_source
	assert "static int CG_NativeSetClientSpeakingState( int clientNum, int speaking ) {" in cg_main_source
	assert "return (int)(intptr_t)CG_SetClientSpeakingState( clientNum, speaking );" in cg_main_source


def test_cgame_copy_client_identity_uses_reconstructed_sidecar_contract() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	block = _block_from_marker(source, "static qboolean CG_CopyClientIdentity")

	assert "cgameClientIdentity_t\t*identity;" in block
	assert "identity->clientNum = clientNum;" in block
	assert "identity->identityTransport = 0;" in block
	assert "identity->identityLow = ci->identityLow;" in block
	assert "identity->identityHigh = ci->identityHigh;" in block
	assert "Q_strncpyz( identity->displayName, ci->name, sizeof( identity->displayName ) );" in block
	assert "Q_CleanStr( cleanName );" in block
	assert 'cleanName[0] ? cleanName : ci->name' in block


def test_console_chat_field_uses_cgame_geometry_exports() -> None:
	source = CL_CONSOLE.read_text(encoding="utf-8")
	width_block = _block_from_marker(source, "static int Con_GetChatFieldWidthInChars")
	prompt_block = _block_from_marker(source, "static const char *Con_GetChatPrompt")
	draw_block = _block_from_marker(source, "if ( cls.keyCatchers & KEYCATCH_MESSAGE )")

	assert "int width = 73;" in width_block
	assert "VM_Call( cgvm, CG_GET_CHAT_FIELD_WIDTH_IN_CHARS )" in width_block
	assert "if ( teamChat && width > 5 )" in width_block

	assert "if ( chat_reply ) {" in prompt_block
	assert 'return "reply:";' in prompt_block
	assert 'return "say team:";' in prompt_block
	assert 'return "say:";' in prompt_block
	assert "*skip = 7;" in prompt_block
	assert "*skip = 11;" in prompt_block
	assert "*skip = 6;" in prompt_block
	assert "if ( chat_playerNum != -1 )" not in prompt_block

	for expected in (
		"chatFieldY = Con_GetChatFieldY();",
		"screenX = 8.0f;",
		"screenY = (float)chatFieldY;",
		"SCR_AdjustFrom640( &screenX, &screenY, NULL, NULL );",
		"fieldX = promptX + skip * charWidth;",
		"Con_DrawHostText( promptX, promptY, charWidth, charHeight, prompt, g_color_table[ColorIndex( COLOR_WHITE )], qtrue );",
		"Con_DrawHostField( &chatField, fieldX, promptY, charWidth, charHeight, qtrue );",
	):
		assert expected in draw_block

	assert '"say_team:"' not in source


def test_console_message_modes_and_timestamps_follow_retail_cgame_path() -> None:
	source = CL_CONSOLE.read_text(encoding="utf-8")
	keys_source = CL_KEYS.read_text(encoding="utf-8")
	mode_block = _block_from_marker(source, "void Con_MessageMode_f")
	mode2_block = _block_from_marker(source, "void Con_MessageMode2_f")
	mode3_block = _block_from_marker(source, "void Con_MessageMode3_f")
	mode4_block = _block_from_marker(source, "void Con_MessageMode4_f")
	message_block = _block_from_marker(keys_source, "void Message_Key")
	time_block = _block_from_marker(source, "static int Con_GetTimestampTime")
	format_block = _block_from_marker(source, "static void Con_FormatTimestamp")
	print_block = _block_from_marker(source, "void CL_ConsolePrint")

	assert "Con_ResetChatField( qfalse );" in mode_block
	assert "Con_ResetChatField( qtrue );" in mode2_block
	assert "Con_ResetChatField( qfalse );" in mode3_block
	assert "Con_ResetChatField( qfalse );" in mode4_block
	assert 'Cmd_AddCommand ("messagemode", Con_MessageMode_f);' in source
	assert 'Cmd_AddCommand ("messagemode2", Con_MessageMode2_f);' in source
	assert 'Cmd_AddCommand ("messagemode3", Con_MessageMode3_f);' not in source
	assert 'Cmd_AddCommand ("messagemode4", Con_MessageMode4_f);' not in source
	assert "chat_reply = qfalse;" in mode_block
	assert "chat_reply = qfalse;" in mode2_block
	assert "chat_reply = qfalse;" in mode3_block
	assert "chat_reply = qfalse;" in mode4_block
	assert "VM_Call( cgvm, CG_CHAT_DOWN );" in mode_block
	assert "VM_Call( cgvm, CG_CHAT_DOWN );" in mode2_block
	assert "VM_Call( cgvm, CG_CHAT_DOWN );" in mode3_block
	assert "VM_Call( cgvm, CG_CHAT_DOWN );" in mode4_block
	assert message_block.count( "VM_Call( cgvm, CG_CHAT_UP );" ) == 2
	assert 'Com_sprintf( buffer, sizeof( buffer ), "reply \\"%s\\"\\n", chatField.buffer );' in message_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "tell %i \\"%s\\"\\n", chat_playerNum, chatField.buffer );' in message_block
	assert "Cbuf_ExecuteText( EXEC_APPEND, buffer );" in message_block
	assert "if ( !chat_reply ) {" in message_block
	assert "CL_AddReliableCommand( buffer );" in message_block

	assert "timestampTime = cl.serverTime;" in time_block
	assert "cls.realtime" not in time_block
	assert "VM_Call( cgvm, CG_GET_PHYSICS_TIME )" in time_block
	assert "con_timestamps->integer == 1" in time_block
	assert 'Com_sprintf( buffer, bufferSize, "[%d:%02d.%03d] ", minutes, seconds, millis );' in format_block
	assert "if ( timestampMode && con.x == 0 ) {" in print_block
	assert "Con_FormatTimestamp( timestamp, sizeof( timestamp ) );" in print_block
	assert "timestampPrinted" not in print_block
	assert '"^7[%i] "' not in source


def test_console_host_field_draw_matches_retail_utf8_cursor_windowing() -> None:
	source = CL_CONSOLE.read_text(encoding="utf-8")
	helper_block = _block_from_marker(source, "static void Con_DrawHostField_helper( field_t *edit, int x, int y, int charWidth, int charHeight, qboolean showCursor ) {")
	field_block = _block_from_marker(source, "static void Con_DrawHostField( field_t *edit, int x, int y, int charWidth, int charHeight, qboolean showCursor ) {")

	for expected in (
		"static qboolean Con_IsUtf8ContinuationByte( unsigned char ch ) {",
		"static int Con_ClampUtf8Boundary( const char *text, int index ) {",
		"static int Con_PrevUtf8CharStart( const char *text, int index ) {",
		"cursor = Con_ClampUtf8Boundary( edit->buffer, edit->cursor );",
		"while ( visibleChars < edit->widthInChars && start > 0 ) {",
		"start = Con_PrevUtf8CharStart( edit->buffer, start );",
		"if ( visibleChars == edit->widthInChars && cursor < start ) {",
		"end = Con_PrevUtf8CharStart( edit->buffer, end );",
		"RE_MeasureScaledText( drawText, drawText + prefixBytes, CONSOLE_HOST_FONT_MONO, Con_GetHostTextScale( charWidth ), 0, &prefixWidth, NULL, NULL );",
		"if ( !Key_GetOverstrikeMode() ) {",
		"cursorX -= charWidth / 2;",
	):
		assert expected in source

	assert "Con_DrawHostField_helper( edit, x, y, charWidth, charHeight, showCursor );" in field_block
	assert "Con_DrawHostText( cursorX, y, charWidth, charHeight, Key_GetOverstrikeMode() ? \"_\" : \"|\", g_color_table[ColorIndex( COLOR_WHITE )], qtrue );" in helper_block
	assert "prestep = edit->scroll;" not in field_block
	assert "drawLen = edit->widthInChars;" not in field_block


def test_console_cell_geometry_and_alignment_match_retail_engine_scaling() -> None:
	source = CL_CONSOLE.read_text(encoding="utf-8")
	scale_block = _block_from_marker(source, "static float Con_GetPixelScale")
	width_block = _block_from_marker(source, "static int Con_GetScaledSmallCharWidth")
	height_block = _block_from_marker(source, "static int Con_GetScaledSmallCharHeight")
	host_metrics_block = _block_from_marker(source, "static void Con_GetHostFontMetrics")
	draw_host_block = _block_from_marker(source, "static void Con_DrawHostText")
	resize_block = _block_from_marker(source, "void Con_CheckResize (void)")
	solid_block = _block_from_marker(source, "void Con_DrawSolidConsole( float frac )")

	assert "#define\t\tCONSOLE_CHAR_WIDTH\t12" in source
	assert "#define\t\tCONSOLE_CHAR_HEIGHT\t24" in source
	assert "pixelScale = Con_GetScale();" in scale_block
	assert "cls.glconfig.vidHeight" not in scale_block
	assert "CONSOLE_CHAR_WIDTH * Con_GetPixelScale()" in width_block
	assert "CONSOLE_CHAR_HEIGHT * Con_GetPixelScale()" in height_block
	assert "Con_GetHostFontMetrics( Con_GetScaledSmallCharWidth(), height, NULL, &lineHeight );" in height_block
	assert "RE_GetScaledFontMetrics( CONSOLE_HOST_FONT_MONO, scale, &ascent, &descent, &lineHeight )" in host_metrics_block
	assert "Con_GetHostFontMetrics( charWidth, charHeight, &ascent, NULL );" in draw_host_block
	assert "baselineY = y + (int)( ascent + 0.5f );" in draw_host_block
	assert "RE_DrawScaledText( x, baselineY, text, CONSOLE_HOST_FONT_MONO, scale, 0, NULL, forceColor, drawColor );" in draw_host_block
	assert "y + charHeight" not in draw_host_block
	assert "width = (int)( (float)cls.glconfig.vidWidth / ( scale * CONSOLE_CHAR_WIDTH ) - 2.0f );" in resize_block
	assert "con.xadjust = 0;" in solid_block
	assert "SCR_AdjustFrom640( &con.xadjust, NULL, NULL, NULL );" not in solid_block


def test_screen_overlay_text_uses_retail_host_mono_lane() -> None:
	source = CL_SCRN.read_text(encoding="utf-8")
	draw_block = _block_from_marker(source, "void SCR_DrawStringExt")
	big_block = _block_from_marker(source, "void SCR_DrawBigString( int x, int y, const char *s, float alpha )")
	big_color_block = _block_from_marker(source, "void SCR_DrawBigStringColor( int x, int y, const char *s, vec4_t color )")
	demo_block = _block_from_marker(source, "void SCR_DrawDemoRecording")

	assert "#define\tSCREEN_OVERLAY_HOST_FONT_MONO\t2" in source
	for expected in (
		"xscale = cls.glconfig.vidWidth / 640.0f;",
		"yscale = cls.glconfig.vidHeight / 480.0f;",
		"screenX = (int)( x * xscale );",
		"screenY = (int)( y * yscale );",
		"RE_DrawScaledText( screenX, screenY, string, SCREEN_OVERLAY_HOST_FONT_MONO,",
		"size * yscale, -1, NULL, forceColor, setColor );",
	):
		assert expected in draw_block

	assert "SCR_DrawChar(" not in draw_block
	assert "static void SCR_DrawChar" not in source
	assert "while ( *s )" not in draw_block
	assert "re.SetColor" not in draw_block
	assert "SCR_DrawStringExt( x, y, BIGCHAR_WIDTH, s, color, qfalse );" in big_block
	assert "SCR_DrawStringExt( x, y, BIGCHAR_WIDTH, s, color, qtrue );" in big_color_block
	assert 'SCR_DrawStringExt( ( 80 - strlen( string ) ) * 4, 420, 8, string, g_color_table[7], qtrue );' in demo_block
	assert 'SCR_DrawStringExt( 9, 477, 8, "REC", g_color_table[7], qtrue );' in demo_block


def test_console_bootstrap_width_uses_retail_engine_cell_width() -> None:
	source = CL_MAIN.read_text(encoding="utf-8")

	assert 'consoleScale = Com_Clamp( 0.5f, 1.0f, Cvar_VariableValue( "con_scale" ) );' in source
	assert 'g_console_field_width = (int)( (float)cls.glconfig.vidWidth / ( consoleScale * 12.0f ) - 2.0f );' in source
	assert 'g_console_field_width = cls.glconfig.vidWidth / SMALLCHAR_WIDTH - 2;' not in source
