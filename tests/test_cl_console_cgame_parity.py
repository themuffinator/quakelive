"""Guard the retail cgame/chat host seam against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_PUBLIC = REPO_ROOT / "src" / "code" / "cgame" / "cg_public.h"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CL_CONSOLE = REPO_ROOT / "src" / "code" / "client" / "cl_console.c"
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

	assert "VM_Call( cgvm, CG_GET_CHAT_FIELD_WIDTH_IN_CHARS )" in width_block
	assert "if ( teamChat && width > 5 )" in width_block

	assert 'return "reply:";' in prompt_block
	assert 'return "say team:";' in prompt_block
	assert 'return "say:";' in prompt_block
	assert "*skip = 7;" in prompt_block
	assert "*skip = 11;" in prompt_block
	assert "*skip = 6;" in prompt_block

	for expected in (
		"chatFieldY = Con_GetChatFieldY();",
		"chatFieldWidth = Con_GetChatFieldPixelWidth();",
		"SCR_DrawBigString (8, chatFieldY, prompt, 1.0f );",
		"Field_BigDraw( &chatField, skip * BIGCHAR_WIDTH, chatFieldY, drawWidth, qtrue );",
	):
		assert expected in draw_block

	assert '"say_team:"' not in source


def test_console_message_modes_and_timestamps_follow_retail_cgame_path() -> None:
	source = CL_CONSOLE.read_text(encoding="utf-8")
	mode_block = _block_from_marker(source, "void Con_MessageMode_f")
	mode2_block = _block_from_marker(source, "void Con_MessageMode2_f")
	mode3_block = _block_from_marker(source, "void Con_MessageMode3_f")
	mode4_block = _block_from_marker(source, "void Con_MessageMode4_f")
	time_block = _block_from_marker(source, "static int Con_GetTimestampTime")
	format_block = _block_from_marker(source, "static void Con_FormatTimestamp")
	print_block = _block_from_marker(source, "void CL_ConsolePrint")

	assert "Con_ResetChatField( qfalse );" in mode_block
	assert "Con_ResetChatField( qtrue );" in mode2_block
	assert "Con_ResetChatField( qfalse );" in mode3_block
	assert "Con_ResetChatField( qfalse );" in mode4_block

	assert "VM_Call( cgvm, CG_GET_PHYSICS_TIME )" in time_block
	assert "cl_contimestamps->integer == 1" in time_block
	assert 'Com_sprintf( buffer, bufferSize, "[%d:%02d.%03d] ", minutes, seconds, millis );' in format_block
	assert "Con_FormatTimestamp( timestamp, sizeof( timestamp ) );" in print_block
	assert '"^7[%i] "' not in source
