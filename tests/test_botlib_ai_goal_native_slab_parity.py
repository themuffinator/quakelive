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

EXPECTED_AI_GOAL_NATIVE_SLOTS = (
	(137, "G_QL_IMPORT_BOTLIB_AI_RESET_GOAL_STATE", "BOTLIB_AI_RESET_GOAL_STATE", "QL_G_trap_BotResetGoalState", "4E1FF0", 18, "0056d1a4", "sub_4e1ff0", "0x128", True),
	(138, "G_QL_IMPORT_BOTLIB_AI_REMOVE_FROM_AVOID_GOALS", "BOTLIB_AI_REMOVE_FROM_AVOID_GOALS", "QL_G_trap_BotRemoveFromAvoidGoals", "4E2030", 18, "0056d1a8", "sub_4e2030", "0x130", True),
	(139, "G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_GOALS", "BOTLIB_AI_RESET_AVOID_GOALS", "QL_G_trap_BotResetAvoidGoals", "4E2010", 18, "0056d1ac", "sub_4e2010", "0x12c", True),
	(140, "G_QL_IMPORT_BOTLIB_AI_PUSH_GOAL", "BOTLIB_AI_PUSH_GOAL", "QL_G_trap_BotPushGoal", "4E2050", 18, "0056d1b0", "sub_4e2050", "0x134", True),
	(141, "G_QL_IMPORT_BOTLIB_AI_POP_GOAL", "BOTLIB_AI_POP_GOAL", "QL_G_trap_BotPopGoal", "4E2070", 18, "0056d1b4", "sub_4e2070", "0x138", True),
	(142, "G_QL_IMPORT_BOTLIB_AI_EMPTY_GOAL_STACK", "BOTLIB_AI_EMPTY_GOAL_STACK", "QL_G_trap_BotEmptyGoalStack", "4E2090", 18, "0056d1b8", "sub_4e2090", "0x13c", True),
	(143, "G_QL_IMPORT_BOTLIB_AI_DUMP_AVOID_GOALS", "BOTLIB_AI_DUMP_AVOID_GOALS", "QL_G_trap_BotDumpAvoidGoals", "4E20B0", 18, "0056d1bc", "sub_4e20b0", "0x140", True),
	(144, "G_QL_IMPORT_BOTLIB_AI_DUMP_GOAL_STACK", "BOTLIB_AI_DUMP_GOAL_STACK", "QL_G_trap_BotDumpGoalStack", "4E20D0", 18, "0056d1c0", "sub_4e20d0", "0x144", True),
	(145, "G_QL_IMPORT_BOTLIB_AI_GOAL_NAME", "BOTLIB_AI_GOAL_NAME", "QL_G_trap_BotGoalName", "4E20F0", 17, "0056d1c4", "sub_4e20f0", "0x148", True),
	(146, "G_QL_IMPORT_BOTLIB_AI_GET_TOP_GOAL", "BOTLIB_AI_GET_TOP_GOAL", "QL_G_trap_BotGetTopGoal", "4E2110", 18, "0056d1c8", "sub_4e2110", "0x14c", True),
	(147, "G_QL_IMPORT_BOTLIB_AI_GET_SECOND_GOAL", "BOTLIB_AI_GET_SECOND_GOAL", "QL_G_trap_BotGetSecondGoal", "4E2130", 18, "0056d1cc", "sub_4e2130", "0x150", True),
	(148, "G_QL_IMPORT_BOTLIB_AI_CHOOSE_LTG_ITEM", "BOTLIB_AI_CHOOSE_LTG_ITEM", "QL_G_trap_BotChooseLTGItem", "4E2150", 18, "0056d1d0", "sub_4e2150", "0x154", True),
	(149, "G_QL_IMPORT_BOTLIB_AI_CHOOSE_NBG_ITEM", "BOTLIB_AI_CHOOSE_NBG_ITEM", "QL_G_trap_BotChooseNBGItem", "4E2170", 49, "0056d1d4", "sub_4e2170", "0x158", True),
	(150, "G_QL_IMPORT_BOTLIB_AI_TOUCHING_GOAL", "BOTLIB_AI_TOUCHING_GOAL", "QL_G_trap_BotTouchingGoal", "4E21B0", 18, "0056d1d8", "sub_4e21b0", "0x15c", True),
	(151, "G_QL_IMPORT_BOTLIB_AI_ITEM_GOAL_IN_VIS_BUT_NOT_VISIBLE", "BOTLIB_AI_ITEM_GOAL_IN_VIS_BUT_NOT_VISIBLE", "QL_G_trap_BotItemGoalInVisButNotVisible", "4E21D0", 18, "0056d1dc", "sub_4e21d0", "0x160", True),
	(152, "G_QL_IMPORT_BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL", "BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL", "QL_G_trap_BotGetNextCampSpotGoal", "4E2210", 18, "0056d1e0", "sub_4e2210", "0x168", True),
	(153, "G_QL_IMPORT_BOTLIB_AI_GET_MAP_LOCATION_GOAL", "BOTLIB_AI_GET_MAP_LOCATION_GOAL", "QL_G_trap_BotGetMapLocationGoal", "4E2230", 18, "0056d1e4", "sub_4e2230", "0x16c", True),
	(154, "G_QL_IMPORT_BOTLIB_AI_GET_LEVEL_ITEM_GOAL", "BOTLIB_AI_GET_LEVEL_ITEM_GOAL", "QL_G_trap_BotGetLevelItemGoal", "4E21F0", 17, "0056d1e8", "sub_4e21f0", "0x164", True),
	(155, "G_QL_IMPORT_BOTLIB_AI_AVOID_GOAL_TIME", "BOTLIB_AI_AVOID_GOAL_TIME", "QL_G_trap_BotAvoidGoalTime", "4E2250", 18, "0056d1ec", "sub_4e2250", "0x170", True),
	(156, "G_QL_IMPORT_BOTLIB_AI_SET_AVOID_GOAL_TIME", "BOTLIB_AI_SET_AVOID_GOAL_TIME", "QL_G_trap_BotSetAvoidGoalTime", "4E2270", 37, "0056d1f0", "sub_4e2270", "0x174", True),
	(157, "G_QL_IMPORT_BOTLIB_AI_INIT_LEVEL_ITEMS", "BOTLIB_AI_INIT_LEVEL_ITEMS", "QL_G_trap_BotInitLevelItems", "4E22A0", None, "0056d1f4", "sub_4e22a0", "0x178", True),
	(158, "G_QL_IMPORT_BOTLIB_AI_UPDATE_ENTITY_ITEMS", "BOTLIB_AI_UPDATE_ENTITY_ITEMS", "QL_G_trap_BotUpdateEntityItems", "4E22B0", None, "0056d1f8", "0x4e22b0", "0x17c", False),
	(159, "G_QL_IMPORT_BOTLIB_AI_LOAD_ITEM_WEIGHTS", "BOTLIB_AI_LOAD_ITEM_WEIGHTS", "QL_G_trap_BotLoadItemWeights", "4E22C0", 18, "0056d1fc", "sub_4e22c0", "0x180", True),
	(160, "G_QL_IMPORT_BOTLIB_AI_FREE_ITEM_WEIGHTS", "BOTLIB_AI_FREE_ITEM_WEIGHTS", "QL_G_trap_BotFreeItemWeights", "4E22E0", 18, "0056d200", "sub_4e22e0", "0x184", True),
	(161, "G_QL_IMPORT_BOTLIB_AI_INTERBREED_GOAL_FUZZY_LOGIC", "BOTLIB_AI_INTERBREED_GOAL_FUZZY_LOGIC", "QL_G_trap_BotInterbreedGoalFuzzyLogic", "4E2300", 17, "0056d204", "sub_4e2300", "0x188", True),
	(162, "G_QL_IMPORT_BOTLIB_AI_SAVE_GOAL_FUZZY_LOGIC", "BOTLIB_AI_SAVE_GOAL_FUZZY_LOGIC", "QL_G_trap_BotSaveGoalFuzzyLogic", "4E2320", 18, "0056d208", "sub_4e2320", "0x18c", True),
	(163, "G_QL_IMPORT_BOTLIB_AI_MUTATE_GOAL_FUZZY_LOGIC", "BOTLIB_AI_MUTATE_GOAL_FUZZY_LOGIC", "QL_G_trap_BotMutateGoalFuzzyLogic", "4E2340", 33, "0056d20c", "sub_4e2340", "0x190", True),
	(164, "G_QL_IMPORT_BOTLIB_AI_ALLOC_GOAL_STATE", "BOTLIB_AI_ALLOC_GOAL_STATE", "QL_G_trap_BotAllocGoalState", "4E2370", 18, "0056d210", "sub_4e2370", "0x194", True),
	(165, "G_QL_IMPORT_BOTLIB_AI_FREE_GOAL_STATE", "BOTLIB_AI_FREE_GOAL_STATE", "QL_G_trap_BotFreeGoalState", "4E2390", 18, "0056d214", "sub_4e2390", "0x198", True),
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


def _raw_offset_bytes(export_offset: str) -> str:
	value = int(export_offset, 16)
	return " ".join(f"{(value >> (8 * shift)) & 0xff:02x}" for shift in range(4))


def test_ai_goal_native_slab_rows_and_hlil_table_are_pinned() -> None:
	rows = _function_rows()
	game_hlil = _read(QL_STEAM_HLIL_PART05)
	table_hlil = _read(QL_STEAM_HLIL_PART07)

	for _, _, _, _, address, size, table_address, table_target, export_offset, has_header in EXPECTED_AI_GOAL_NATIVE_SLOTS:
		assert f"{table_address}  void* data_{table_address[2:]} = {table_target}" in table_hlil

		if size is None:
			assert address not in rows
		else:
			assert rows[address] == f"FUN_00{address.lower()},00{address.lower()},{size},0,unknown"

		if has_header:
			assert f"00{address.lower()}    int32_t sub_{address.lower()}" in game_hlil
			assert f"*(data_13e1844 + {export_offset})" in game_hlil
		else:
			assert f"a1 44 18 3e 01 8b 88 {_raw_offset_bytes(export_offset)} ff e1" in game_hlil

	for table_anchor in (
		"0056d1a0  void* data_56d1a0 = sub_4e1fd0",
		"0056d1a4  void* data_56d1a4 = sub_4e1ff0",
		"0056d1a8  void* data_56d1a8 = sub_4e2030",
		"0056d1ac  void* data_56d1ac = sub_4e2010",
		"0056d1d4  void* data_56d1d4 = sub_4e2170",
		"0056d1e0  void* data_56d1e0 = sub_4e2210",
		"0056d1e4  void* data_56d1e4 = sub_4e2230",
		"0056d1e8  void* data_56d1e8 = sub_4e21f0",
		"0056d1f4  void* data_56d1f4 = sub_4e22a0",
		"0056d1f8  void* data_56d1f8 = 0x4e22b0",
		"0056d214  void* data_56d214 = sub_4e2390",
		"0056d218  void* data_56d218 = sub_4e23b0",
	):
		assert table_anchor in table_hlil

	for float_anchor in (
		"004e21a0      fconvert.s(fconvert.t(arg6)))",
		"004e2294  return (*(data_13e1844 + 0x174))(arg1, arg2, fconvert.s(fconvert.t(arg3)))",
		"004e2360  return (*(data_13e1844 + 0x190))(arg1, fconvert.s(fconvert.t(arg2)))",
	):
		assert float_anchor in game_hlil


def test_ai_goal_native_slab_source_wiring_and_float_marshal_are_pinned() -> None:
	g_public = _read(GAME_PUBLIC)
	g_syscalls = _read(GAME_SYSCALLS)
	sv_game = _read(SERVER_SV_GAME)
	ql_imports = _read(SERVER_QL_GAME_IMPORTS)
	syscall_map = _extract_function_block(g_syscalls, "static int G_MapNativeImport")
	init_imports = _extract_function_block(sv_game, "static void SV_InitGameImports")

	for slot, native_name, legacy_name, wrapper, _, _, _, _, _, _ in EXPECTED_AI_GOAL_NATIVE_SLOTS:
		assert f"{native_name} = {slot}," in g_public
		assert f"case {legacy_name}: return {native_name};" in syscall_map
		assert f"ql_game_imports[{native_name}] = (ql_import_f){wrapper};" in init_imports
		assert f"[{legacy_name}] = (ql_import_f){wrapper}," in sv_game
		assert f"QDECL {wrapper}" in ql_imports

	assert init_imports.index("G_QL_IMPORT_BOTLIB_AI_REMOVE_FROM_AVOID_GOALS") < init_imports.index("G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_GOALS")
	assert sv_game.index("[BOTLIB_AI_RESET_AVOID_GOALS]") < sv_game.index("[BOTLIB_AI_REMOVE_FROM_AVOID_GOALS]")
	assert ql_imports.index("QL_G_trap_BotResetAvoidGoals") < ql_imports.index("QL_G_trap_BotRemoveFromAvoidGoals")

	assert init_imports.index("G_QL_IMPORT_BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL") < init_imports.index("G_QL_IMPORT_BOTLIB_AI_GET_LEVEL_ITEM_GOAL")
	assert ql_imports.index("QL_G_trap_BotGetLevelItemGoal") < ql_imports.index("QL_G_trap_BotGetNextCampSpotGoal")
	assert init_imports.index("G_QL_IMPORT_BOTLIB_AI_INTERBREED_GOAL_FUZZY_LOGIC") < init_imports.index("G_QL_IMPORT_BOTLIB_AI_SAVE_GOAL_FUZZY_LOGIC")
	assert g_public.index("G_QL_IMPORT_BOTLIB_AI_FREE_GOAL_STATE = 165,") < g_public.index("G_QL_IMPORT_BOTLIB_AI_RESET_MOVE_STATE = 166,")

	for wrapper_anchor in (
		"return G_Import_Syscall( BOTLIB_AI_CHOOSE_NBG_ITEM, goalstate, origin, inventory, travelflags, ltg, QL_G_PASSFLOAT(maxtime) );",
		"temp = G_Import_Syscall( BOTLIB_AI_AVOID_GOAL_TIME, goalstate, number );",
		"return (*(float*)&temp);",
		"G_Import_Syscall( BOTLIB_AI_SET_AVOID_GOAL_TIME, goalstate, number, QL_G_PASSFLOAT(avoidtime));",
		"G_Import_Syscall( BOTLIB_AI_MUTATE_GOAL_FUZZY_LOGIC, goalstate, QL_G_PASSFLOAT(range) );",
	):
		assert wrapper_anchor in ql_imports

	for syscall_anchor in (
		"return syscall( BOTLIB_AI_CHOOSE_NBG_ITEM, goalstate, origin, inventory, travelflags, ltg, PASSFLOAT(maxtime) );",
		"temp = syscall( BOTLIB_AI_AVOID_GOAL_TIME, goalstate, number );",
		"syscall( BOTLIB_AI_SET_AVOID_GOAL_TIME, goalstate, number, PASSFLOAT(avoidtime));",
		"syscall( BOTLIB_AI_MUTATE_GOAL_FUZZY_LOGIC, goalstate, PASSFLOAT(range) );",
	):
		assert syscall_anchor in g_syscalls

	assert "botlib_export->ai.BotMutateGoalFuzzyLogic( args[1], VMF(2) );" in sv_game
