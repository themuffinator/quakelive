from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

FUNCTIONS_CSV = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
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
QL_STEAM_HLIL_PART07 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part07.txt"
)
GAME_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
SERVER_SV_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SERVER_QL_GAME_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"

EXPECTED_AI_CHARACTER_CHAT_NATIVE_SLOTS = (
	(110, "G_QL_IMPORT_BOTLIB_AI_LOAD_CHARACTER", "BOTLIB_AI_LOAD_CHARACTER", "QL_G_trap_BotLoadCharacter", "4E1C80", 33, "0056d138", "0xbc"),
	(111, "G_QL_IMPORT_BOTLIB_AI_FREE_CHARACTER", "BOTLIB_AI_FREE_CHARACTER", "QL_G_trap_BotFreeCharacter", "4E1CB0", 18, "0056d13c", "0xc0"),
	(112, "G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_FLOAT", "BOTLIB_AI_CHARACTERISTIC_FLOAT", "QL_G_trap_Characteristic_Float", "4E1CD0", 18, "0056d140", "0xc4"),
	(113, "G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT", "BOTLIB_AI_CHARACTERISTIC_BFLOAT", "QL_G_trap_Characteristic_BFloat", "4E1CF0", 46, "0056d144", "0xc8"),
	(114, "G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_INTEGER", "BOTLIB_AI_CHARACTERISTIC_INTEGER", "QL_G_trap_Characteristic_Integer", "4E1D20", 18, "0056d148", "0xcc"),
	(115, "G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BINTEGER", "BOTLIB_AI_CHARACTERISTIC_BINTEGER", "QL_G_trap_Characteristic_BInteger", "4E1D40", 18, "0056d14c", "0xd0"),
	(116, "G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_STRING", "BOTLIB_AI_CHARACTERISTIC_STRING", "QL_G_trap_Characteristic_String", "4E1D60", 18, "0056d150", "0xd4"),
	(117, "G_QL_IMPORT_BOTLIB_AI_ALLOC_CHAT_STATE", "BOTLIB_AI_ALLOC_CHAT_STATE", "QL_G_trap_BotAllocChatState", "4E1D80", None, "0056d154", "0xd8"),
	(118, "G_QL_IMPORT_BOTLIB_AI_FREE_CHAT_STATE", "BOTLIB_AI_FREE_CHAT_STATE", "QL_G_trap_BotFreeChatState", "4E1D90", 18, "0056d158", "0xdc"),
	(119, "G_QL_IMPORT_BOTLIB_AI_QUEUE_CONSOLE_MESSAGE", "BOTLIB_AI_QUEUE_CONSOLE_MESSAGE", "QL_G_trap_BotQueueConsoleMessage", "4E1DB0", 17, "0056d15c", "0xe0"),
	(120, "G_QL_IMPORT_BOTLIB_AI_REMOVE_CONSOLE_MESSAGE", "BOTLIB_AI_REMOVE_CONSOLE_MESSAGE", "QL_G_trap_BotRemoveConsoleMessage", "4E1DD0", 18, "0056d160", "0xe4"),
	(121, "G_QL_IMPORT_BOTLIB_AI_NEXT_CONSOLE_MESSAGE", "BOTLIB_AI_NEXT_CONSOLE_MESSAGE", "QL_G_trap_BotNextConsoleMessage", "4E1DF0", 18, "0056d164", "0xe8"),
	(122, "G_QL_IMPORT_BOTLIB_AI_NUM_CONSOLE_MESSAGE", "BOTLIB_AI_NUM_CONSOLE_MESSAGE", "QL_G_trap_BotNumConsoleMessages", "4E1E10", 18, "0056d168", "0xec"),
	(123, "G_QL_IMPORT_BOTLIB_AI_INITIAL_CHAT", "BOTLIB_AI_INITIAL_CHAT", "QL_G_trap_BotInitialChat", "4E1E30", 18, "0056d16c", "0xf0"),
	(124, "G_QL_IMPORT_BOTLIB_AI_NUM_INITIAL_CHATS", "BOTLIB_AI_NUM_INITIAL_CHATS", "QL_G_trap_BotNumInitialChats", "4E1E50", 18, "0056d170", "0xf4"),
	(125, "G_QL_IMPORT_BOTLIB_AI_REPLY_CHAT", "BOTLIB_AI_REPLY_CHAT", "QL_G_trap_BotReplyChat", "4E1E70", 17, "0056d174", "0xf8"),
	(126, "G_QL_IMPORT_BOTLIB_AI_CHAT_LENGTH", "BOTLIB_AI_CHAT_LENGTH", "QL_G_trap_BotChatLength", "4E1E90", 18, "0056d178", "0xfc"),
	(127, "G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT", "BOTLIB_AI_ENTER_CHAT", "QL_G_trap_BotEnterChat", "4E1EB0", 17, "0056d17c", "0x100"),
	(128, "G_QL_IMPORT_BOTLIB_AI_GET_CHAT_MESSAGE", "BOTLIB_AI_GET_CHAT_MESSAGE", "QL_G_trap_BotGetChatMessage", "4E1ED0", 17, "0056d180", "0x104"),
	(129, "G_QL_IMPORT_BOTLIB_AI_STRING_CONTAINS", "BOTLIB_AI_STRING_CONTAINS", "QL_G_trap_StringContains", "4E1EF0", 17, "0056d184", "0x108"),
	(130, "G_QL_IMPORT_BOTLIB_AI_FIND_MATCH", "BOTLIB_AI_FIND_MATCH", "QL_G_trap_BotFindMatch", "4E1F10", 17, "0056d188", "0x10c"),
	(131, "G_QL_IMPORT_BOTLIB_AI_MATCH_VARIABLE", "BOTLIB_AI_MATCH_VARIABLE", "QL_G_trap_BotMatchVariable", "4E1F30", 18, "0056d18c", "0x110"),
	(132, "G_QL_IMPORT_BOTLIB_AI_UNIFY_WHITE_SPACES", "BOTLIB_AI_UNIFY_WHITE_SPACES", "QL_G_trap_UnifyWhiteSpaces", "4E1F50", 18, "0056d190", "0x114"),
	(133, "G_QL_IMPORT_BOTLIB_AI_REPLACE_SYNONYMS", "BOTLIB_AI_REPLACE_SYNONYMS", "QL_G_trap_BotReplaceSynonyms", "4E1F70", 18, "0056d194", "0x118"),
	(134, "G_QL_IMPORT_BOTLIB_AI_LOAD_CHAT_FILE", "BOTLIB_AI_LOAD_CHAT_FILE", "QL_G_trap_BotLoadChatFile", "4E1F90", 17, "0056d198", "0x11c"),
	(135, "G_QL_IMPORT_BOTLIB_AI_SET_CHAT_GENDER", "BOTLIB_AI_SET_CHAT_GENDER", "QL_G_trap_BotSetChatGender", "4E1FB0", 18, "0056d19c", "0x120"),
	(136, "G_QL_IMPORT_BOTLIB_AI_SET_CHAT_NAME", "BOTLIB_AI_SET_CHAT_NAME", "QL_G_trap_BotSetChatName", "4E1FD0", 17, "0056d1a0", "0x124"),
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _function_rows() -> dict[str, str]:
	rows: dict[str, str] = {}
	with FUNCTIONS_CSV.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			rows[row["entry"].upper()[2:]] = (
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


def test_ai_character_chat_native_slab_rows_and_hlil_table_are_pinned() -> None:
	rows = _function_rows()
	game_hlil = _read(QL_STEAM_HLIL_PART05)
	table_hlil = _read(QL_STEAM_HLIL_PART07)

	for _, _, _, _, address, size, table_address, export_offset in EXPECTED_AI_CHARACTER_CHAT_NATIVE_SLOTS:
		table_target = f"sub_{address.lower()}" if size is not None else f"0x{address.lower()}"
		assert f"{table_address}  void* data_{table_address[2:]} = {table_target}" in table_hlil

		if size is None:
			offset_byte = export_offset[2:].rjust(2, "0")
			assert address not in rows
			assert f"00{address.lower()}  a1 44 18 3e 01 8b 88 {offset_byte} 00 00 00 ff e1" in game_hlil
			continue

		assert rows[address] == f"FUN_00{address.lower()},00{address.lower()},{size},0,unknown"
		assert f"00{address.lower()}    int32_t sub_{address.lower()}" in game_hlil
		assert f"*(data_13e1844 + {export_offset})" in game_hlil

	for table_anchor in (
		"0056d134  void* data_56d134 = sub_4e1c60",
		"0056d138  void* data_56d138 = sub_4e1c80",
		"0056d154  void* data_56d154 = 0x4e1d80",
		"0056d178  void* data_56d178 = sub_4e1e90",
		"0056d184  void* data_56d184 = sub_4e1ef0",
		"0056d1a0  void* data_56d1a0 = sub_4e1fd0",
		"0056d1a4  void* data_56d1a4 = sub_4e1ff0",
	):
		assert table_anchor in table_hlil

	for float_anchor in (
		"004e1ca0  return (*(data_13e1844 + 0xbc))(arg1, fconvert.s(fconvert.t(arg2)))",
		"004e1d1d  return (*(data_13e1844 + 0xc8))(arg1, arg2, fconvert.s(fconvert.t(arg3)),",
		"004e1d1d      fconvert.s(fconvert.t(arg4)))",
	):
		assert float_anchor in game_hlil


def test_ai_character_chat_native_slab_source_wiring_matches_retail_slots() -> None:
	g_public = _read(GAME_PUBLIC)
	g_syscalls = _read(GAME_SYSCALLS)
	sv_game = _read(SERVER_SV_GAME)
	ql_imports = _read(SERVER_QL_GAME_IMPORTS)
	syscall_map = _extract_function_block(g_syscalls, "static int G_MapNativeImport")
	init_imports = _extract_function_block(sv_game, "static void SV_InitGameImports")

	for slot, native_name, legacy_name, wrapper, _, _, _, _ in EXPECTED_AI_CHARACTER_CHAT_NATIVE_SLOTS:
		assert f"{native_name} = {slot}," in g_public
		assert f"case {legacy_name}: return {native_name};" in syscall_map
		assert f"ql_game_imports[{native_name}] = (ql_import_f){wrapper};" in init_imports
		assert f"[{legacy_name}] = (ql_import_f){wrapper}," in sv_game
		assert f"QDECL {wrapper}" in ql_imports

	assert init_imports.index("G_QL_IMPORT_BOTLIB_AI_CHAT_LENGTH") < init_imports.index("G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT")
	assert init_imports.index("G_QL_IMPORT_BOTLIB_AI_GET_CHAT_MESSAGE") < init_imports.index("G_QL_IMPORT_BOTLIB_AI_STRING_CONTAINS")
	assert init_imports.index("G_QL_IMPORT_BOTLIB_AI_SET_CHAT_NAME") < init_imports.index("G_QL_IMPORT_BOTLIB_AI_RESET_GOAL_STATE")
	assert g_public.index("G_QL_IMPORT_BOTLIB_AI_CHAT_LENGTH = 126,") < g_public.index("G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT = 127,")
	assert g_public.index("G_QL_IMPORT_BOTLIB_AI_STRING_CONTAINS = 129,") < g_public.index("G_QL_IMPORT_BOTLIB_AI_FIND_MATCH = 130,")

	for wrapper_anchor in (
		"static int QDECL QL_G_trap_BotLoadCharacter( char *charfile, float skill )",
		"return G_Import_Syscall( BOTLIB_AI_LOAD_CHARACTER, charfile, QL_G_PASSFLOAT(skill));",
		"static float QDECL QL_G_trap_Characteristic_Float( int character, int index )",
		"temp = G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_FLOAT, character, index );",
		"static float QDECL QL_G_trap_Characteristic_BFloat( int character, int index, float min, float max )",
		"temp = G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_BFLOAT, character, index, QL_G_PASSFLOAT(min), QL_G_PASSFLOAT(max) );",
		"return (*(float*)&temp);",
		"static int QDECL QL_G_trap_BotChatLength( int chatstate )",
		"return G_Import_Syscall( BOTLIB_AI_CHAT_LENGTH, chatstate );",
		"static int QDECL QL_G_trap_StringContains( char *str1, char *str2, int casesensitive )",
		"return G_Import_Syscall( BOTLIB_AI_STRING_CONTAINS, str1, str2, casesensitive );",
		"static void QDECL QL_G_trap_BotSetChatName( int chatstate, char *name, int client )",
		"G_Import_Syscall( BOTLIB_AI_SET_CHAT_NAME, chatstate, name, client );",
	):
		assert wrapper_anchor in ql_imports
