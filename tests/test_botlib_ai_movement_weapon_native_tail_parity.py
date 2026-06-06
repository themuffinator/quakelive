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

EXPECTED_AI_MOVEMENT_WEAPON_NATIVE_SLOTS = (
	(166, "G_QL_IMPORT_BOTLIB_AI_RESET_MOVE_STATE", "BOTLIB_AI_RESET_MOVE_STATE", "QL_G_trap_BotResetMoveState", "4E23B0", 18, "0056d218", "sub_4e23b0", "0x19c", True),
	(167, "G_QL_IMPORT_BOTLIB_AI_MOVE_TO_GOAL", "BOTLIB_AI_MOVE_TO_GOAL", "QL_G_trap_BotMoveToGoal", "4E2400", 18, "0056d21c", "sub_4e2400", "0x1a0", True),
	(168, "G_QL_IMPORT_BOTLIB_AI_MOVE_IN_DIRECTION", "BOTLIB_AI_MOVE_IN_DIRECTION", "QL_G_trap_BotMoveInDirection", "4E2420", 40, "0056d220", "sub_4e2420", "0x1a4", True),
	(169, "G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_REACH", "BOTLIB_AI_RESET_AVOID_REACH", "QL_G_trap_BotResetAvoidReach", "4E2450", 18, "0056d224", "sub_4e2450", "0x1a8", True),
	(170, "G_QL_IMPORT_BOTLIB_AI_RESET_LAST_AVOID_REACH", "BOTLIB_AI_RESET_LAST_AVOID_REACH", "QL_G_trap_BotResetLastAvoidReach", "4E2470", 18, "0056d228", "sub_4e2470", "0x1ac", True),
	(171, "G_QL_IMPORT_BOTLIB_AI_REACHABILITY_AREA", "BOTLIB_AI_REACHABILITY_AREA", "QL_G_trap_BotReachabilityArea", "4E2490", 18, "0056d22c", "sub_4e2490", "0x1b0", True),
	(172, "G_QL_IMPORT_BOTLIB_AI_MOVEMENT_VIEW_TARGET", "BOTLIB_AI_MOVEMENT_VIEW_TARGET", "QL_G_trap_BotMovementViewTarget", "4E24B0", 45, "0056d230", "sub_4e24b0", "0x1b4", True),
	(173, "G_QL_IMPORT_BOTLIB_AI_PREDICT_VISIBLE_POSITION", "BOTLIB_AI_PREDICT_VISIBLE_POSITION", "QL_G_trap_BotPredictVisiblePosition", "4E24E0", 18, "0056d234", "sub_4e24e0", "0x1b8", True),
	(174, "G_QL_IMPORT_BOTLIB_AI_ALLOC_MOVE_STATE", "BOTLIB_AI_ALLOC_MOVE_STATE", "QL_G_trap_BotAllocMoveState", "4E2500", None, "0056d238", "0x4e2500", "0x1bc", False),
	(175, "G_QL_IMPORT_BOTLIB_AI_FREE_MOVE_STATE", "BOTLIB_AI_FREE_MOVE_STATE", "QL_G_trap_BotFreeMoveState", "4E2510", 18, "0056d23c", "sub_4e2510", "0x1c0", True),
	(176, "G_QL_IMPORT_BOTLIB_AI_INIT_MOVE_STATE", "BOTLIB_AI_INIT_MOVE_STATE", "QL_G_trap_BotInitMoveState", "4E2530", 18, "0056d240", "sub_4e2530", "0x1c4", True),
	(177, "G_QL_IMPORT_BOTLIB_AI_ADD_AVOID_SPOT", "BOTLIB_AI_ADD_AVOID_SPOT", "QL_G_trap_BotAddAvoidSpot", "4E23D0", 40, "0056d244", "sub_4e23d0", "0x1c8", True),
	(178, "G_QL_IMPORT_BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON", "BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON", "QL_G_trap_BotChooseBestFightWeapon", "4E2550", 18, "0056d248", "sub_4e2550", "0x1cc", True),
	(179, "G_QL_IMPORT_BOTLIB_AI_GET_WEAPON_INFO", "BOTLIB_AI_GET_WEAPON_INFO", "QL_G_trap_BotGetWeaponInfo", "4E2570", 17, "0056d24c", "sub_4e2570", "0x1d0", True),
	(180, "G_QL_IMPORT_BOTLIB_AI_LOAD_WEAPON_WEIGHTS", "BOTLIB_AI_LOAD_WEAPON_WEIGHTS", "QL_G_trap_BotLoadWeaponWeights", "4E2590", 18, "0056d250", "sub_4e2590", "0x1d4", True),
	(181, "G_QL_IMPORT_BOTLIB_AI_ALLOC_WEAPON_STATE", "BOTLIB_AI_ALLOC_WEAPON_STATE", "QL_G_trap_BotAllocWeaponState", "4E25B0", None, "0056d254", "0x4e25b0", "0x1d8", False),
	(182, "G_QL_IMPORT_BOTLIB_AI_FREE_WEAPON_STATE", "BOTLIB_AI_FREE_WEAPON_STATE", "QL_G_trap_BotFreeWeaponState", "4E25C0", 18, "0056d258", "sub_4e25c0", "0x1dc", True),
	(183, "G_QL_IMPORT_BOTLIB_AI_RESET_WEAPON_STATE", "BOTLIB_AI_RESET_WEAPON_STATE", "QL_G_trap_BotResetWeaponState", "4E25E0", 18, "0056d25c", "sub_4e25e0", "0x1e0", True),
	(184, "G_QL_IMPORT_BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION", "BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION", "QL_G_trap_GeneticParentsAndChildSelection", "4E2600", 18, "0056d260", "sub_4e2600", "0x1e4", True),
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


def test_ai_movement_weapon_native_tail_rows_and_hlil_table_are_pinned() -> None:
	rows = _function_rows()
	game_hlil = _read(QL_STEAM_HLIL_PART05)
	table_hlil = _read(QL_STEAM_HLIL_PART07)

	for _, _, _, _, address, size, table_address, table_target, export_offset, has_header in EXPECTED_AI_MOVEMENT_WEAPON_NATIVE_SLOTS:
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
		"0056d214  void* data_56d214 = sub_4e2390",
		"0056d218  void* data_56d218 = sub_4e23b0",
		"0056d220  void* data_56d220 = sub_4e2420",
		"0056d238  void* data_56d238 = 0x4e2500",
		"0056d240  void* data_56d240 = sub_4e2530",
		"0056d244  void* data_56d244 = sub_4e23d0",
		"0056d254  void* data_56d254 = 0x4e25b0",
		"0056d260  void* data_56d260 = sub_4e2600",
		"0056d264  void* data_56d264 = sub_4e2620",
	):
		assert table_anchor in table_hlil

	for float_anchor in (
		"004e23f7  return (*(data_13e1844 + 0x1c8))(arg1, arg2, fconvert.s(fconvert.t(arg3)), arg4)",
		"004e2447  return (*(data_13e1844 + 0x1a4))(arg1, arg2, fconvert.s(fconvert.t(arg3)), arg4)",
		"004e24dc  return (*(data_13e1844 + 0x1b4))(arg1, arg2, arg3, fconvert.s(fconvert.t(arg4)), arg5)",
	):
		assert float_anchor in game_hlil


def test_ai_movement_weapon_native_tail_source_wiring_matches_retail_slots() -> None:
	g_public = _read(GAME_PUBLIC)
	g_syscalls = _read(GAME_SYSCALLS)
	sv_game = _read(SERVER_SV_GAME)
	ql_imports = _read(SERVER_QL_GAME_IMPORTS)
	syscall_map = _extract_function_block(g_syscalls, "static int G_MapNativeImport")
	init_imports = _extract_function_block(sv_game, "static void SV_InitGameImports")

	for slot, native_name, legacy_name, wrapper, _, _, _, _, _, _ in EXPECTED_AI_MOVEMENT_WEAPON_NATIVE_SLOTS:
		assert f"{native_name} = {slot}," in g_public
		assert f"case {legacy_name}: return {native_name};" in syscall_map
		assert f"ql_game_imports[{native_name}] = (ql_import_f){wrapper};" in init_imports
		assert f"[{legacy_name}] = (ql_import_f){wrapper}," in sv_game
		assert f"QDECL {wrapper}" in ql_imports

	assert init_imports.index("G_QL_IMPORT_BOTLIB_AI_INIT_MOVE_STATE") < init_imports.index("G_QL_IMPORT_BOTLIB_AI_ADD_AVOID_SPOT")
	assert ql_imports.index("QL_G_trap_BotAddAvoidSpot") < ql_imports.index("QL_G_trap_BotMoveToGoal")
	assert init_imports.index("G_QL_IMPORT_BOTLIB_AI_ADD_AVOID_SPOT") < init_imports.index("G_QL_IMPORT_BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON")
	assert init_imports.index("G_QL_IMPORT_BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION") < init_imports.index("G_QL_IMPORT_SUBMIT_MATCH_REPORT")
	assert g_public.index("G_QL_IMPORT_BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION = 184,") < g_public.index("G_QL_IMPORT_SUBMIT_MATCH_REPORT = 185,")

	for wrapper_anchor in (
		"G_Import_Syscall( BOTLIB_AI_ADD_AVOID_SPOT, movestate, origin, QL_G_PASSFLOAT(radius), type);",
		"return G_Import_Syscall( BOTLIB_AI_MOVE_IN_DIRECTION, movestate, dir, QL_G_PASSFLOAT(speed), type );",
		"return G_Import_Syscall( BOTLIB_AI_MOVEMENT_VIEW_TARGET, movestate, goal, travelflags, QL_G_PASSFLOAT(lookahead), target );",
		"return G_Import_Syscall( BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION, numranks, ranks, parent1, parent2, child );",
	):
		assert wrapper_anchor in ql_imports

	for syscall_anchor in (
		"syscall( BOTLIB_AI_ADD_AVOID_SPOT, movestate, origin, PASSFLOAT(radius), type);",
		"return syscall( BOTLIB_AI_MOVE_IN_DIRECTION, movestate, dir, PASSFLOAT(speed), type );",
		"return syscall( BOTLIB_AI_MOVEMENT_VIEW_TARGET, movestate, goal, travelflags, PASSFLOAT(lookahead), target );",
		"return syscall( BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION, numranks, ranks, parent1, parent2, child );",
	):
		assert syscall_anchor in g_syscalls

	for dispatch_anchor in (
		"return botlib_export->ai.BotMoveInDirection( args[1], VMA(2), VMF(3), args[4] );",
		"return botlib_export->ai.BotMovementViewTarget( args[1], VMA(2), args[3], VMF(4), VMA(5) );",
		"botlib_export->ai.BotAddAvoidSpot( args[1], VMA(2), VMF(3), args[4] );",
		"return botlib_export->ai.GeneticParentsAndChildSelection(args[1], VMA(2), VMA(3), VMA(4), VMA(5));",
	):
		assert dispatch_anchor in sv_game
