from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

GAME_AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
GAME_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
SERVER_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
QL_GAME_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
QL_STEAM_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
)
QAGAME_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "functions.csv"
)
QAGAME_HLIL_PART01 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part01.txt"
)
QL_STEAM_HLIL_PART05 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part05.txt"
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _function_rows(path: Path) -> dict[str, str]:
	rows: dict[str, str] = {}
	with path.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			rows[row["entry"].upper()] = (
				f'{row["name"]},{row["entry"]},{row["size"]},{row["thunk"]},{row["calling_convention"]}'
			)
	return rows


def _extract_function_block(source: str, signature: str) -> str:
	start = source.find(signature)
	assert start != -1, signature
	brace = source.find("{", start)
	assert brace != -1, signature

	depth = 0
	for offset in range(brace, len(source)):
		if source[offset] == "{":
			depth += 1
		elif source[offset] == "}":
			depth -= 1
			if depth == 0:
				return source[start : offset + 1]

	raise AssertionError(f"unterminated function block: {signature}")


def _assert_ordered(text: str, anchors: tuple[str, ...]) -> None:
	offset = 0
	for anchor in anchors:
		found = text.find(anchor, offset)
		assert found != -1, anchor
		offset = found + len(anchor)


def test_qagame_bot_command_ingestion_aliases_and_rows_are_pinned() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))
	qagame_aliases = aliases["qagamex86"]
	ql_aliases = aliases["quakelive_steam_srp"]
	qagame_rows = _function_rows(QAGAME_FUNCTIONS)
	ql_rows = _function_rows(QL_STEAM_FUNCTIONS)

	for address, name in (
		("FUN_10021e10", "BotUpdateInput"),
		("sub_10021e10", "BotUpdateInput"),
		("FUN_10021f90", "RemoveColorEscapeSequences"),
		("sub_10021f90", "RemoveColorEscapeSequences"),
		("FUN_10021fe0", "BotAI"),
		("sub_10021fe0", "BotAI"),
		("FUN_1002c7d0", "BotVoiceChatCommand"),
		("sub_1002c7d0", "BotVoiceChatCommand"),
		("FUN_10023400", "BotAIStartFrame"),
		("sub_10023400", "BotAIStartFrame"),
	):
		assert qagame_aliases[address] == name

	for address, name in (
		("sub_4E17F0", "QL_G_trap_BotGetServerCommand"),
		("sub_4E1800", "QL_G_trap_BotUserCommand"),
	):
		assert ql_aliases[address] == name

	assert qagame_rows["10021E10"] == "FUN_10021e10,10021e10,372,0,unknown"
	assert qagame_rows["10021F90"] == "FUN_10021f90,10021f90,70,0,unknown"
	assert qagame_rows["10021FE0"] == "FUN_10021fe0,10021fe0,1187,0,unknown"
	assert qagame_rows["1002C7D0"] == "FUN_1002c7d0,1002c7d0,379,0,unknown"
	assert qagame_rows["10023400"] == "FUN_10023400,10023400,2038,0,unknown"
	assert ql_rows["004E17F0"] == "FUN_004e17f0,004e17f0,9,0,unknown"
	assert ql_rows["004E1800"] == "FUN_004e1800,004e1800,33,0,unknown"


def test_source_bot_command_ingestion_and_usercmd_bridge_match_retail_shape() -> None:
	ai_main = _read(GAME_AI_MAIN)
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)

	remove_color = _extract_function_block(ai_main, "void RemoveColorEscapeSequences( char *text )")
	for expected in (
		"if (Q_IsColorString(&text[i]))",
		"if (text[i] > 0x7E)",
		"text[l++] = text[i];",
		"text[l] = '\\0';",
	):
		assert expected in remove_color

	bot_ai = _extract_function_block(ai_main, "int BotAI(int client, float thinktime)")
	_assert_ordered(
		bot_ai,
		(
			"trap_EA_ResetInput(client);",
			"bs = botstates[client];",
			'BotAI_Print(PRT_FATAL, "BotAI: client %d is not setup\\n", client);',
			"BotAI_GetClientState( client, &bs->cur_ps );",
			"while( trap_BotGetServerCommand(client, buf, sizeof(buf)) )",
			"args = strchr( buf, ' ');",
			"*args++ = '\\0';",
			"RemoveColorEscapeSequences( args );",
			'if (!Q_stricmp(buf, "cp "))',
			'else if (!Q_stricmp(buf, "cs"))',
			'else if (!Q_stricmp(buf, "print"))',
			"trap_BotQueueConsoleMessage(bs->cs, CMS_NORMAL, args);",
			'else if (!Q_stricmp(buf, "chat"))',
			"args[0] >= '0' && args[0] <= '9'",
			"args += 3;",
			"trap_BotQueueConsoleMessage(bs->cs, CMS_CHAT, args);",
			'else if (!Q_stricmp(buf, "tchat"))',
			"trap_BotQueueConsoleMessage(bs->cs, CMS_CHAT, args);",
			'else if (!Q_stricmp(buf, "vchat"))',
			"BotVoiceChatCommand(bs, SAY_ALL, args);",
			'else if (!Q_stricmp(buf, "vtchat"))',
			"BotVoiceChatCommand(bs, SAY_TEAM, args);",
			'else if (!Q_stricmp(buf, "vtell"))',
			"BotVoiceChatCommand(bs, SAY_TELL, args);",
			"BotDeathmatchAI(bs, thinktime);",
			"trap_EA_SelectWeapon(bs->client, bs->weaponnum);",
		),
	)

	chat_branch = bot_ai[
		bot_ai.index('else if (!Q_stricmp(buf, "chat"))') : bot_ai.index('else if (!Q_stricmp(buf, "tchat"))')
	]
	tchat_branch = bot_ai[
		bot_ai.index('else if (!Q_stricmp(buf, "tchat"))') : bot_ai.index('else if (!Q_stricmp(buf, "vchat"))')
	]
	assert "args += 3;" in chat_branch
	assert "args += 3;" not in tchat_branch

	update_input = _extract_function_block(ai_main, "void BotUpdateInput(bot_state_t *bs, int time, int elapsed_time)")
	_assert_ordered(
		update_input,
		(
			"BotChangeViewAngles(bs, (float) elapsed_time / 1000);",
			"trap_EA_GetInput(bs->client, (float) time / 1000, &bi);",
			"if (bi.actionflags & ACTION_RESPAWN)",
			"BotInputToUserCommand(&bi, &bs->lastucmd, bs->cur_ps.delta_angles, time);",
		),
	)

	start_frame = _extract_function_block(ai_main, "int BotAIStartFrame(int time)")
	_assert_ordered(
		start_frame,
		(
			"BotAI(i, (float) thinktime / 1000);",
			"BotUpdateInput(botstates[i], time, elapsed_time);",
			"trap_BotUserCommand(botstates[i]->client, &botstates[i]->lastucmd);",
			"BotUpdateItemDelayTime( time );",
			"BotUpdateDynamicSkill( time );",
			"BotUpdateTrainingState();",
		),
	)

	for expected in (
		"G_QL_IMPORT_BOTLIB_GET_CONSOLE_MESSAGE = 59,",
		"G_QL_IMPORT_BOTLIB_USER_COMMAND = 60,",
	):
		assert expected in game_public

	for expected in (
		"case BOTLIB_GET_CONSOLE_MESSAGE: return G_QL_IMPORT_BOTLIB_GET_CONSOLE_MESSAGE;",
		"case BOTLIB_USER_COMMAND: return G_QL_IMPORT_BOTLIB_USER_COMMAND;",
		"return syscall( BOTLIB_GET_CONSOLE_MESSAGE, clientNum, message, size );",
		"syscall( BOTLIB_USER_COMMAND, clientNum, ucmd );",
	):
		assert expected in game_syscalls

	for expected in (
		"case BOTLIB_GET_CONSOLE_MESSAGE:",
		"return SV_BotGetConsoleMessage( args[1], VMA(2), args[3] );",
		"case BOTLIB_USER_COMMAND:",
		"SV_ClientThink( &svs.clients[args[1]], VMA(2) );",
		"[BOTLIB_GET_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotGetServerCommand,",
		"[BOTLIB_USER_COMMAND] = (ql_import_f)QL_G_trap_BotUserCommand,",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_GET_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotGetServerCommand;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_USER_COMMAND] = (ql_import_f)QL_G_trap_BotUserCommand;",
	):
		assert expected in server_game

	for expected in (
		"return G_Import_Syscall( BOTLIB_GET_CONSOLE_MESSAGE, clientNum, message, size );",
		"G_Import_Syscall( BOTLIB_USER_COMMAND, clientNum, ucmd );",
	):
		assert expected in ql_game_imports


def test_retail_hlil_pins_qagame_command_ingestion_and_native_wrappers() -> None:
	qagame_hlil = _read(QAGAME_HLIL_PART01)
	ql_hlil = _read(QL_STEAM_HLIL_PART05)

	for expected in (
		"10021f90    void sub_10021f90(char* arg1 @ esi)",
		"if (ecx != 0 && *ecx == 0x5e)",
		"if (eax s<= 0x7e)",
		"10021fe0    void __convention(\"regparm\") sub_10021fe0",
		"(*(data_104b13ac + 0x1b4))(edi)",
		"(*(data_104b13ac + 0xec))(edi, &var_408, 0x400)",
		"eax_9, edx_3 = sub_10070a40(\"cp \", sub_10021f90(esi_3), &var_408)",
		"eax_10, edx_4 = sub_10070a40(\"cs\", edx_3, &var_408)",
		"eax_11, edx_5 = sub_10070a40(\"print\", edx_4, &var_408)",
		"eax_17, edx_10 = sub_10070a40(\"chat\", edx_5, &var_408)",
		"eax_27, edx_14 = sub_10070a40(\"tchat\", edx_10, &var_408)",
		"sub_10070a40(\"vchat\", edx_14, &var_408)",
		"sub_10070a40(\"vtchat\", edx_18, &var_408)",
		"sub_10070a40(\"vtell\", edx_19, &var_408)",
		"if (sx.d(*esi_3) - 0x30 u<= 9",
		"&& sx.d(esi_3[1]) - 0x30 u<= 9",
		"&& esi_3[2] == 0x20)",
		"esi_3 = &esi_3[3]",
		"(*(data_104b13ac + 0x1dc))(ebp[0x659], 1, esi_3)",
		"10021e10    uint32_t __convention(\"regparm\") sub_10021e10",
		"int32_t eax_3 = *(data_104b13ac + 0x1b0)",
		"sub_10021b20(arg3 + 0x48, arg4, ecx_4, &var_30, arg3 + 0x264, arg4)",
		"10023aff                      st0 = sub_10021fe0()",
		"10023b3c              sub_10021e10()",
	):
		assert expected in qagame_hlil

	for expected in (
		"004e17f0    int32_t sub_4e17f0()",
		"004e17f4  return sub_4dda50() __tailcall",
		"004e1800    int32_t sub_4e1800(int32_t arg1, int32_t arg2)",
		"004e1820  return sub_4e02d0(arg1 * 0x25b68 + data_13337ac, arg2)",
		"004e1e20  jump(*(data_13e1844 + 0xec))",
	):
		assert expected in ql_hlil
