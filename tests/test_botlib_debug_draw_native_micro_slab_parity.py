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
GAME_AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
BOTLIB_H = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_AI_MOVE = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_move.c"
SERVER_SV_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"

EXPECTED_DEBUG_DRAW_NATIVE_SLOTS = (
	(83, "G_QL_IMPORT_BOTLIB_AI_DRAW_DEBUG_AREAS", "QL_G_trap_BotDrawDebugAreas", "4E2680", 17, "0056d0cc", "0x1e8"),
	(84, "G_QL_IMPORT_BOTLIB_AI_DRAW_AVOID_SPOTS", "QL_G_trap_BotDrawAvoidSpots", "4E26A0", 18, "0056d0d0", "0x1ec"),
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


def test_debug_draw_native_micro_slab_rows_and_hlil_table_are_pinned() -> None:
	rows = _function_rows()
	game_hlil = _read(QL_STEAM_HLIL_PART05)
	table_hlil = _read(QL_STEAM_HLIL_PART07)

	for _, _, _, address, size, table_address, export_offset in EXPECTED_DEBUG_DRAW_NATIVE_SLOTS:
		assert rows[address] == f"FUN_00{address.lower()},00{address.lower()},{size},0,unknown"
		assert f"{table_address}  void* data_{table_address[2:]} = sub_{address.lower()}" in table_hlil
		assert f"00{address.lower()}    int32_t sub_{address.lower()}" in game_hlil
		assert f"jump(*(data_13e1844 + {export_offset}))" in game_hlil

	for table_anchor in (
		"0056d0c8  void* data_56d0c8 = sub_4e1980",
		"0056d0cc  void* data_56d0cc = sub_4e2680",
		"0056d0d0  void* data_56d0d0 = sub_4e26a0",
		"0056d0d4  void* data_56d0d4 = sub_4e19d0",
	):
		assert table_anchor in table_hlil

	assert table_hlil.index("0056d0c8  void* data_56d0c8 = sub_4e1980") < table_hlil.index(
		"0056d0cc  void* data_56d0cc = sub_4e2680"
	)
	assert table_hlil.index("0056d0cc  void* data_56d0cc = sub_4e2680") < table_hlil.index(
		"0056d0d0  void* data_56d0d0 = sub_4e26a0"
	)
	assert table_hlil.index("0056d0d0  void* data_56d0d0 = sub_4e26a0") < table_hlil.index(
		"0056d0d4  void* data_56d0d4 = sub_4e19d0"
	)
	assert game_hlil.index("*(data_13e1844 + 0x1e4)") < game_hlil.index("*(data_13e1844 + 0x1e8)")
	assert game_hlil.index("*(data_13e1844 + 0x1e8)") < game_hlil.index("*(data_13e1844 + 0x1ec)")


def test_debug_draw_native_micro_slab_source_wiring_matches_direct_host_bridge() -> None:
	g_public = _read(GAME_PUBLIC)
	g_syscalls = _read(GAME_SYSCALLS)
	ai_main = _read(GAME_AI_MAIN)
	botlib_h = _read(BOTLIB_H)
	be_interface = _read(BOTLIB_INTERFACE)
	ai_move = _read(BOTLIB_AI_MOVE)
	sv_game = _read(SERVER_SV_GAME)
	syscall_map = _extract_function_block(g_syscalls, "static int G_MapNativeImport")
	game_draw_debug_areas = _extract_function_block(g_syscalls, "void trap_BotDrawDebugAreas")
	game_draw_avoid_spots = _extract_function_block(g_syscalls, "void trap_BotDrawAvoidSpots")
	server_draw_debug_areas = _extract_function_block(sv_game, "static void QDECL QL_G_trap_BotDrawDebugAreas")
	server_draw_avoid_spots = _extract_function_block(sv_game, "static void QDECL QL_G_trap_BotDrawAvoidSpots")
	init_imports = _extract_function_block(sv_game, "static void SV_InitGameImports")
	bot_test_aas = _extract_function_block(ai_main, "void BotTestAAS")
	draw_debug_areas = _extract_function_block(be_interface, "void BotDrawDebugAreas")
	draw_avoid_spots = _extract_function_block(ai_move, "void BotDrawAvoidSpots")
	init_ai_export = _extract_function_block(be_interface, "static void Init_AI_Export")

	for slot, native_name, wrapper, _, _, _, _ in EXPECTED_DEBUG_DRAW_NATIVE_SLOTS:
		legacy_name = native_name.removeprefix("G_QL_IMPORT_")
		assert f"{native_name} = {slot}," in g_public
		assert f"case {legacy_name}:" not in syscall_map
		assert f"ql_game_imports[{native_name}] = (ql_import_f){wrapper};" in init_imports

	assert "G_GetDirectImport( G_QL_IMPORT_BOTLIB_AI_DRAW_DEBUG_AREAS )" in game_draw_debug_areas
	assert "((void (QDECL *)( vec3_t, int, int ))import)( origin, enable, areanum );" in game_draw_debug_areas
	assert "syscall( BOTLIB_AI_DRAW_DEBUG_AREAS" not in game_draw_debug_areas

	assert "G_GetDirectImport( G_QL_IMPORT_BOTLIB_AI_DRAW_AVOID_SPOTS )" in game_draw_avoid_spots
	assert "((void (QDECL *)( int ))import)( movestate );" in game_draw_avoid_spots
	assert "syscall( BOTLIB_AI_DRAW_AVOID_SPOTS" not in game_draw_avoid_spots

	assert "botlib_export->ai.BotDrawDebugAreas( origin, enable, areanum );" in server_draw_debug_areas
	assert "botlib_export->ai.BotDrawAvoidSpots( movestate );" in server_draw_avoid_spots
	assert init_imports.index("G_QL_IMPORT_BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT") < init_imports.index(
		"G_QL_IMPORT_BOTLIB_AI_DRAW_DEBUG_AREAS"
	)
	assert init_imports.index("G_QL_IMPORT_BOTLIB_AI_DRAW_AVOID_SPOTS") < init_imports.index(
		"G_QL_IMPORT_BOTLIB_EA_SAY"
	)
	assert g_public.index("G_QL_IMPORT_BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT = 82,") < g_public.index(
		"G_QL_IMPORT_BOTLIB_AI_DRAW_DEBUG_AREAS = 83,"
	)
	assert g_public.index("G_QL_IMPORT_BOTLIB_AI_DRAW_AVOID_SPOTS = 84,") < g_public.index(
		"G_QL_IMPORT_BOTLIB_EA_SAY = 85,"
	)

	assert "void\t(*BotDrawDebugAreas)(vec3_t origin, int enable, int areanum);" in botlib_h
	assert "void\t(*BotDrawAvoidSpots)(int movestate);" in botlib_h
	assert botlib_h.index("(*GeneticParentsAndChildSelection)") < botlib_h.index("(*BotDrawDebugAreas)")
	assert botlib_h.index("(*BotDrawDebugAreas)") < botlib_h.index("(*BotDrawAvoidSpots)")
	assert "ai->BotDrawDebugAreas = BotDrawDebugAreas;" in init_ai_export
	assert "ai->BotDrawAvoidSpots = BotDrawAvoidSpots;" in init_ai_export
	assert init_ai_export.index("ai->BotDrawDebugAreas = BotDrawDebugAreas;") < init_ai_export.index(
		"ai->BotDrawAvoidSpots = BotDrawAvoidSpots;"
	)

	for bot_test_anchor in (
		"trap_Cvar_Update(&bot_showAreaNumber);",
		"trap_Cvar_Update(&bot_showAvoidSpots);",
		"trap_Cvar_Update(&bot_showAreas);",
		"trap_BotDrawDebugAreas(origin, bot_showAreas.integer, bot_showAreaNumber.integer);",
		"client = bot_showAvoidSpots.integer;",
		"if ( client >= 1 && client < MAX_CLIENTS ) {",
		"trap_BotDrawAvoidSpots(bs->ms);",
		"trap_Cvar_Set(\"bot_showAvoidSpots\", \"0\");",
	):
		assert bot_test_anchor in bot_test_aas

	assert bot_test_aas.index("trap_Cvar_Update(&bot_showAreas);") < bot_test_aas.index(
		"trap_BotDrawDebugAreas(origin, bot_showAreas.integer, bot_showAreaNumber.integer);"
	)
	assert bot_test_aas.index("trap_BotDrawDebugAreas") < bot_test_aas.index("client = bot_showAvoidSpots.integer;")
	assert bot_test_aas.index("trap_BotDrawAvoidSpots(bs->ms);") < bot_test_aas.index(
		"trap_Cvar_Set(\"bot_showAvoidSpots\", \"0\");"
	)

	for draw_debug_anchor in (
		"static float nextshowtime;",
		"if (AAS_Time() < nextshowtime) {",
		"AAS_ClearShownDebugLines();",
		"AAS_ClearShownPolygons();",
		"nextshowtime = AAS_Time() + RETAIL_BOT_DEBUG_AREA_REFRESH;",
		"if (!aasworld.loaded) {",
		"startarea = areanum;",
		"startarea = 1;",
		"if (VectorLength(dir) > RETAIL_BOT_DEBUG_AREA_RADIUS) {",
		"AAS_ShowAreaPolygons(area, LINECOLOR_ORANGE, qtrue);",
		"AAS_DrawArrow(reach.start, reach.end, linecolor, LINECOLOR_YELLOW);",
	):
		assert draw_debug_anchor in draw_debug_areas

	for draw_avoid_anchor in (
		"ms = BotMoveStateFromHandle(movestate);",
		"AAS_ClearShownDebugLines();",
		"for (i = 0; i < ms->numavoidspots; i++) {",
		"AAS_DrawCross(ms->avoidspots[i].origin, ms->avoidspots[i].radius, LINECOLOR_RED);",
	):
		assert draw_avoid_anchor in draw_avoid_spots
