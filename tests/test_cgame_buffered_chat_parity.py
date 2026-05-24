"""Guard the retail-backed cgame buffered chat path against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_CONSOLECMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_consolecmds.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"


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


def test_buffered_chat_headers_expose_latch_and_writer() -> None:
	source = CG_LOCAL.read_text(encoding="utf-8")

	assert "qboolean\t\tchatHistoryVisible;" in source
	assert "void CG_PushPrintString( const char *text, int type, int holdTime );" in source


def test_console_command_tail_exposes_retail_chat_handlers() -> None:
	source = CG_CONSOLECMDS.read_text(encoding="utf-8")
	chat_down = _block_from_marker(source, "static void CG_ChatDown_f")
	chat_up = _block_from_marker(source, "static void CG_ChatUp_f")
	toggle = _block_from_marker(source, "static void CG_ToggleChatHistory_f")
	print_block = _block_from_marker(source, "static void CG_Print_f")

	for expected in (
		'{ "+chat", CG_ChatDown_f },',
		'{ "-chat", CG_ChatUp_f },',
		'{ "togglechathistory", CG_ToggleChatHistory_f },',
		'{ "print", CG_Print_f },',
	):
		assert expected in source

	assert "cg.chatHistoryVisible = qtrue;" in chat_down
	assert "cg.chatHistoryVisible = qfalse;" in chat_up
	assert "cg.chatHistoryVisible = (qboolean)!cg.chatHistoryVisible;" in toggle
	assert "argc = trap_Argc();" in print_block
	assert 'Q_strcat( buffer, sizeof( buffer ), " " );' in print_block
	assert "CG_PushPrintString( buffer, SYSTEM_PRINT, 0 );" in print_block


def test_buffered_chat_writer_updates_ring_and_lastmsg() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	block = _block_from_marker(source, "void CG_PushPrintString( const char *text, int type, int holdTime )")
	replay_block = _block_from_marker(source, "static void CG_ReplayLastMessageFromCvar")

	assert "Q_strncpyz( cleanText, text, sizeof( cleanText ) );" in block
	assert "cleanText[len - 1] == '\\n'" in block
	assert "CG_SetPrintString( type, cleanText );" in block
	assert "CG_WriteLastMessageCvar( cg.time, cleanText );" in block
	assert "messageTime = cg.time + holdTime;" in block
	assert "cgs.teamChatMsgTimes[cgs.teamChatPos % chatHeight] = messageTime;" in block
	assert "cgs.teamChatPos++;" in block
	assert "CG_PushPrintString( message, SYSTEM_PRINT, 0 );" in replay_block


def test_cgame_printf_does_not_play_chat_sound() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	block = _block_from_marker(source, "void QDECL CG_Printf")

	assert "trap_Print( text );" in block
	assert "trap_S_StartLocalSound" not in block
	assert "cg_chatbeep" not in block


def test_new_chat_area_obeys_history_latch() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	init_block = _block_from_marker(source, "void CG_InitTeamChat()")
	draw_block = _block_from_marker(source, "static void CG_DrawNewChatArea")
	visible_block = _block_from_marker(source, "static qboolean CG_OwnerDrawPrimaryFlagVisible")

	assert "memset( cgs.teamChatMsgs, 0, sizeof( cgs.teamChatMsgs ) );" in init_block
	assert "memset( cgs.teamChatMsgTimes, 0, sizeof( cgs.teamChatMsgTimes ) );" in init_block
	assert "cgs.teamChatPos = 0;" in init_block
	assert "cgs.teamLastChatPos = 0;" in init_block
	assert "cg.chatHistoryVisible = qfalse;" in init_block

	assert "maxLines = cg.chatHistoryVisible ? chatHeight : 1;" in draw_block
	assert "if (elapsed < 0) {" in draw_block
	assert "elapsed = 0;" in draw_block
	assert "cg.chatHistoryVisible || cg.scoreBoardShowing" in visible_block


def test_server_command_path_uses_shared_buffered_writer() -> None:
	source = CG_SERVERCMDS.read_text(encoding="utf-8")
	add_block = _block_from_marker(source, "static void CG_AddToTeamChat( const char *str )")
	buffered_block = _block_from_marker(source, "static void CG_ParseBufferedChat( void )")
	clear_block = _block_from_marker(source, "static void CG_ParseClearChat( void )")
	ui_priv_block = _block_from_marker(source, "static void CG_ParseUiPriv( void )")
	stoprecord_block = _block_from_marker(source, "static void CG_ParseStopRecord( void )")
	server_command = _block_from_marker(source, "static void CG_ServerCommand( void )")

	assert "CG_PushPrintString( str, TEAMCHAT_PRINT, 0 );" in add_block
	assert "trap_S_StartLocalSound( cgs.media.talkSound, CHAN_LOCAL_SOUND );" in buffered_block
	assert "CG_RemoveChatEscapeChar( text );" in buffered_block
	assert 'CG_Printf( "%s\\n", text );' in buffered_block
	assert "holdTime = atoi( CG_Argv( 2 ) ) * 1000;" in buffered_block
	assert "CG_PushPrintString( text, SYSTEM_PRINT, holdTime );" in buffered_block
	assert "CG_InitTeamChat();" in clear_block
	assert 'trap_Cvar_Set( "ui_priv", CG_Argv( 1 ) );' in ui_priv_block
	assert 'trap_SendConsoleCommand( "stoprecord; wait\\n" );' in stoprecord_block
	assert 'CG_PushPrintString( CG_Argv(1), SYSTEM_PRINT, 0 );' in server_command
	assert "CG_PushPrintString( text, CHAT_PRINT, 0 );" in server_command
	assert "CG_PushPrintString( text, TEAMCHAT_PRINT, 0 );" in server_command
	assert 'if ( !strcmp( cmd, "bchat" ) ) {' in server_command
	assert "CG_ParseBufferedChat();" in server_command
	assert 'if ( !strcmp( cmd, "clearChat" ) ) {' in server_command
	assert "CG_ParseClearChat();" in server_command
	assert 'if ( !strcmp( cmd, "ui_priv" ) ) {' in server_command
	assert "CG_ParseUiPriv();" in server_command
