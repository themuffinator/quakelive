from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_MAIN = REPO_ROOT / "src" / "code" / "game" / "g_main.c"
GAME_AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
GAME_CMDS = REPO_ROOT / "src" / "code" / "game" / "g_cmds.c"
QAGAME_GHIDRA_DECOMPILE = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "decompile_top_functions.c"
)
QAGAME_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "functions.csv"
)
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
QAGAME_HLIL_PART02 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part02.txt"
)
QAGAME_HLIL_PART03 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part03.txt"
)


BOT_CVAR_SOURCE_ROWS = (
	('{ &bot_autoReady, "bot_autoReady", "1", CVAR_GAMERULE', "bot_autoReady"),
	('{ &bot_breakPoint, "bot_breakPoint", "0", 0', "bot_breakPoint"),
	('{ &bot_debugVar, "bot_debugVar", "0", 0', "bot_debugVar"),
	('{ &bot_dynamicSkill, "bot_dynamicSkill", "0", CVAR_GAMERULE', "bot_dynamicSkill"),
	('{ &bot_followDist, "bot_followDist", "250", CVAR_GAMERULE', "bot_followDist"),
	('{ &bot_followMe, "bot_followMe", "", CVAR_GAMERULE', "bot_followMe"),
	('{ &bot_gauntlet, "bot_gauntlet", "0", CVAR_GAMERULE', "bot_gauntlet"),
	('{ &bot_gauntletOnly, "bot_gauntletOnly", "0", CVAR_GAMERULE', "bot_gauntletOnly"),
	('{ &bot_hud, "bot_hud", "-1", CVAR_CHEAT', "bot_hud"),
	('{ &bot_instaGibAimSkill, "bot_instaGibAimSkill", "0.4", CVAR_GAMERULE', "bot_instaGibAimSkill"),
	('{ &bot_itemDelayTime, "bot_itemDelayTime", "0", CVAR_GAMERULE', "bot_itemDelayTime"),
	('{ &bot_teamkill, "bot_teamkill", "0", CVAR_GAMERULE', "bot_teamkill"),
	('{ &bot_showAreaNumber, "bot_showAreaNumber", "0", CVAR_GAMERULE', "bot_showAreaNumber"),
	('{ &bot_showAreas, "bot_showAreas", "0", CVAR_GAMERULE', "bot_showAreas"),
	('{ &bot_showAvoidSpots, "bot_showAvoidSpots", "0", CVAR_GAMERULE', "bot_showAvoidSpots"),
	('{ &bot_showPath, "bot_showPath", "0", CVAR_GAMERULE', "bot_showPath"),
	('{ &bot_showTourPoints, "bot_showTourPoints", "0", CVAR_GAMERULE', "bot_showTourPoints"),
	('{ &bot_startingSkill, "bot_startingSkill", "1", CVAR_GAMERULE', "bot_startingSkill"),
	('{ &bot_training, "bot_training", "0", CVAR_GAMERULE', "bot_training"),
)


EXPORTED_BOT_DEBUG_CVARS = {"bot_showAreaNumber", "bot_showAreas", "bot_showAvoidSpots"}


BOT_CVAR_HLIL_NAMES = (
	'1008d894  char const (* data_1008d894)[0xe] = data_10087610 {"bot_autoReady"}',
	'1008d8ac  char const (* data_1008d8ac)[0xf] = data_1007dd64 {"bot_breakPoint"}',
	'1008d8c4  char const (* data_1008d8c4)[0xd] = data_1007d114 {"bot_debugVar"}',
	'1008d8dc  char const (* data_1008d8dc)[0x11] = data_1007d1dc {"bot_dynamicSkill"}',
	'1008d8f4  char const (* data_1008d8f4)[0xf] = data_1007e24c {"bot_followDist"}',
	'1008d90c  char const (* data_1008d90c)[0xd] = data_1007d0ac {"bot_followMe"}',
	'1008d924  char const (* data_1008d924)[0xd] = data_1007e238 {"bot_gauntlet"}',
	'1008d93c  char const (* data_1008d93c)[0x11] = data_100875f8 {"bot_gauntletOnly"}',
	'1008d954  char const (* data_1008d954)[0x8] = data_100875f0 {"bot_hud"}',
	'1008d96c  char const (* data_1008d96c)[0x15] = data_100875d4 {"bot_instaGibAimSkill"}',
	'1008d984  char const (* data_1008d984)[0x12] = data_1007e1c4 {"bot_itemDelayTime"}',
	'1008d99c  char const (* data_1008d99c)[0xd] = data_100875c0 {"bot_teamkill"}',
	'1008d9b4  char const (* data_1008d9b4)[0x13] = data_100875ac {"bot_showAreaNumber"}',
	'1008d9cc  char const (* data_1008d9cc)[0xe] = data_1008759c {"bot_showAreas"}',
	'1008d9e4  char const (* data_1008d9e4)[0x13] = data_1007dc8c {"bot_showAvoidSpots"}',
	'1008d9fc  char const (* data_1008d9fc)[0xd] = data_1007dff4 {"bot_showPath"}',
	'1008da14  char const (* data_1008da14)[0x13] = data_10087588 {"bot_showTourPoints"}',
	'1008da2c  char const (* data_1008da2c)[0x12] = data_1007e2b4 {"bot_startingSkill"}',
	'1008da44  char const (* data_1008da44)[0xd] = data_1007d0d8 {"bot_training"}',
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _text_block(text: str, start_marker: str, end_marker: str) -> str:
	start = text.find(start_marker)
	if start == -1:
		raise AssertionError(f"start marker not found: {start_marker}")

	end = text.find(end_marker, start)
	if end == -1:
		raise AssertionError(f"end marker not found after {start_marker}: {end_marker}")

	return text[start:end]


def test_qagame_bot_cvar_table_rows_match_retail_hlil_defaults_flags_and_order() -> None:
	g_main = _read(GAME_MAIN)
	qagame_hlil_part02 = _read(QAGAME_HLIL_PART02)
	qagame_hlil_part03 = _read(QAGAME_HLIL_PART03)

	source_table = _text_block(g_main, "static cvarTable_t\t\tgameCvarTable[]", "static int gameCvarTableSize")
	hlil_table = _text_block(qagame_hlil_part03, "1008d894  char const", "1008da58  void* data_1008da58")

	previous_index = -1
	for source_row, cvar_name in BOT_CVAR_SOURCE_ROWS:
		if cvar_name in EXPORTED_BOT_DEBUG_CVARS:
			assert f"vmCvar_t\t{cvar_name};" in g_main
			assert f"static vmCvar_t\t{cvar_name};" not in g_main
		else:
			assert f"static vmCvar_t\t{cvar_name};" in g_main
		row_index = source_table.find(source_row)
		assert row_index > previous_index, f"missing or out-of-order qagame cvar row: {cvar_name}"
		previous_index = row_index

	assert source_table.index('bot_autoReady') > source_table.index('g_skipTrainingEnable')
	assert source_table.index('bot_training') < source_table.index('g_floodprot_maxcount')

	previous_index = -1
	for hlil_name in BOT_CVAR_HLIL_NAMES:
		row_index = hlil_table.find(hlil_name)
		assert row_index > previous_index, f"missing or out-of-order retail HLIL row: {hlil_name}"
		previous_index = row_index

	for default_pointer in (
		"1008d898  void* data_1008d898 = data_1007d1d8",
		"1008d8f8  void* data_1008d8f8 = 0x1008760c",
		"1008d910  void* data_1008d910 = data_1007c414",
		"1008d958  void* data_1008d958 = data_100875ec",
		"1008d970  void* data_1008d970 = 0x100875d0",
		"1008da30  void* data_1008da30 = data_1007d1d8",
	):
		assert default_pointer in hlil_table

	assert hlil_table.count("00 00 10 00") == 16
	assert "1008d95c                                                                                      00 02 00 00" in hlil_table

	for string_anchor in (
		'10087588  char const data_10087588[0x13] = "bot_showTourPoints", 0',
		'100875c0  char const data_100875c0[0xd] = "bot_teamkill", 0',
		'100875d4  char const data_100875d4[0x15] = "bot_instaGibAimSkill", 0',
		'100875ec                                      2d 31 00 00',
		'10087609                             00 00 00 32 35 30 00',
	):
		assert string_anchor in qagame_hlil_part02


def test_qagame_bot_cvar_table_is_tied_to_training_debug_and_symbol_evidence() -> None:
	ai_main = _read(GAME_AI_MAIN)
	g_cmds = _read(GAME_CMDS)
	ghidra_decompile = _read(QAGAME_GHIDRA_DECOMPILE)
	functions = _read(QAGAME_FUNCTIONS)
	aliases = _read(SYMBOL_ALIASES)

	for function_row in (
		"FUN_10020f00,10020f00,580,0,unknown",
		"FUN_100241c0,100241c0,436,0,unknown",
		"FUN_10024640,10024640,183,0,unknown",
		"FUN_100247c0,100247c0,1596,0,unknown",
		"FUN_10024fa0,10024fa0,993,0,unknown",
	):
		assert function_row in functions

	for alias_anchor in (
		'"FUN_10020f00": "BotTestAAS"',
		'"FUN_100241c0": "BotAISetup"',
		'"FUN_10024640": "BotUpdateItemDelayTime"',
		'"FUN_100247c0": "BotUpdateDynamicSkill"',
		'"FUN_10024fa0": "BotUpdateTrainingState"',
	):
		assert alias_anchor in aliases

	for ghidra_anchor in (
		'(**(code **)(DAT_104b13ac + 0x3c))("bot_training",&DAT_1007d0a8);',
		'(**(code **)(DAT_104b13ac + 0x3c))("bot_dynamicSkill",&DAT_1007d1d8);',
		'(**(code **)(iVar1 + 0x3c))("bot_startingSkill",uVar3);',
	):
		assert ghidra_anchor in ghidra_decompile

	for training_source_anchor in (
		'BotSetTrainingCvarIfChanged( "bot_followDist", "125" );',
		'BotSetTrainingCvarIfChanged( "bot_itemDelayTime", "10" );',
		'BotSetTrainingCvarIfChanged( "bot_startingSkill", "1" );',
		'BotSetTrainingCvarIfChanged( "bot_training", "0" );',
		'BotSetTrainingCvarIfChanged( "bot_dynamicSkill", "0" );',
		'BotSetTrainingCvarIfChanged( "bot_followMe", "1" );',
		'trap_BotLibVarSet("bot_showPath", "0");',
	):
		assert training_source_anchor in ai_main

	for duplicate_register in (
		'trap_Cvar_Register(&bot_showAreaNumber, "bot_showAreaNumber", "0", CVAR_VM_CREATED);',
		'trap_Cvar_Register(&bot_showAreas, "bot_showAreas", "0", CVAR_VM_CREATED);',
		'trap_Cvar_Register(&bot_showAvoidSpots, "bot_showAvoidSpots", "0", CVAR_VM_CREATED);',
	):
		assert duplicate_register not in ai_main

	for command_source_anchor in (
		'trap_Cvar_Set( "bot_training", "0" );',
		'trap_Cvar_Set( "bot_dynamicSkill", "1" );',
		'trap_Cvar_Set( "bot_followMe", "0" );',
		'trap_Cvar_Set( "bot_gauntlet", "0" );',
	):
		assert command_source_anchor in g_cmds
