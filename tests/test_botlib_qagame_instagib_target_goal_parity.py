from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_AI_DMQ3 = REPO_ROOT / "src" / "code" / "game" / "ai_dmq3.c"
GAME_AI_DMQ3_H = REPO_ROOT / "src" / "code" / "game" / "ai_dmq3.h"
GAME_AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
GAME_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
SERVER_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
QL_GAME_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
QAGAME_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "qagame.json"
QAGAME_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "functions.csv"
)
QAGAME_DECOMPILE_TOP = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "decompile_top_functions.c"
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


INSTAGIB_TARGET_FUNCTIONS = (
	("10020200", "FUN_10020200", "BotFindInstaGibTarget", "int BotFindInstaGibTarget(bot_state_t *bs)", 1018),
	("10020600", "FUN_10020600", "BotRefreshInstaGibTargetGoal", "int BotRefreshInstaGibTargetGoal(bot_state_t *bs)", 303),
	("10020730", "FUN_10020730", "BotGetInstaGibTargetGoal", "void BotGetInstaGibTargetGoal(bot_state_t *bs, bot_goal_t *goal)", 585),
)


SOURCE_ANCHORS = {
	"BotFindInstaGibTarget": (
		"target = -1;",
		"bestdist = 100000000.0f;",
		"BotEntityVisible(bs->entitynum, bs->eye, bs->viewangles, 360, bs->enemy) > 0",
		"BotEntityInfo(bs->enemy, &entinfo);",
		"areanum = BotPointAreaNum(entinfo.origin);",
		"trap_AAS_AreaTravelTimeToGoalArea(bs->areanum, bs->origin, areanum, TFL_DEFAULT) > 0",
		"for (i = 0; i < maxclients && i < MAX_CLIENTS; i++)",
		"if (i == bs->client)",
		"if (EntityIsDead(&entinfo))",
		"dist = VectorLength(dir);",
		"if (target != -1)",
		"areanum = trap_AAS_PointReachabilityAreaIndex(entinfo.origin);",
		"end[2] += 10;",
		"numareas = trap_AAS_TraceAreas(entinfo.origin, end, areas, NULL, 10);",
	),
	"BotRefreshInstaGibTargetGoal": (
		"if (bs->ltg_time < FloatTime())",
		"BotEntityInfo(bs->teamgoal.entitynum, &entinfo);",
		"if (!entinfo.valid)",
		"return qtrue;",
		"if (EntityIsDead(&entinfo))",
		"bs->ltg_time = 0;",
		"bs->ltg_time = FloatTime() + 5.0f;",
		"VectorCopy(entinfo.origin, bs->teamgoal.origin);",
		"bs->teamgoal.areanum = BotPointAreaNum(entinfo.origin);",
		"VectorSet(bs->teamgoal.mins, -8, -8, -8);",
		"VectorSet(bs->teamgoal.maxs, 8, 8, 8);",
		"bs->teamgoal.flags = 0;",
	),
	"BotGetInstaGibTargetGoal": (
		"if (!BotRefreshInstaGibTargetGoal(bs))",
		"target = -1;",
		"bestdist = 100000000.0f;",
		"if (BotSameTeam(bs, i))",
		"if (EntityIsDead(&entinfo))",
		"bs->ltgtype = LTG_KILL;",
		"bs->ltg_time = FloatTime() + 5.0f;",
		"bs->teamgoal_time = FloatTime() + 60.0f;",
		"bs->teamgoal.entitynum = target;",
		"BotRefreshInstaGibTargetGoal(bs);",
		"memcpy(goal, &bs->teamgoal, sizeof(bot_goal_t));",
	),
}


HLIL_ANCHORS = (
	"10020200    int32_t sub_10020200(void* arg1)",
	"10020235  int32_t var_384 = 0x4cbebc20",
	"10020260          sub_10018b20(*(arg1 + 8), arg1 + 0x1984, fconvert.s(fconvert.t(360f)), eax_2)",
	"100202d3          int32_t eax_6 = sub_10015a40(&var_110)",
	"100202da                  eax_6, 0x11c0fbe) s> 0)",
	"1002051b                      int32_t eax_21 = (*(data_104b13ac + 0x10c))(&var_110)",
	"1002058a                                  var_3ac_8) s> 0)",
	"10020600    int32_t sub_10020600(void* arg1 @ edi)",
	"10020625  if (not(fconvert.t(data_105e2ef8) > fconvert.t(*(arg1 + 0x1794))))",
	"1002063f      (*(data_104b13ac + 0xfc))(*(arg1 + 0x19e8), &var_f8)",
	"1002068f          *(arg1 + 0x1794) = fconvert.s(fconvert.t(data_105e2ef8) + fconvert.t(5.0))",
	"100206a0          *(arg1 + 0x19c0) = var_e0",
	"100206cc          *(arg1 + 0x19d0) = 0xc1000000",
	"100206ec          *(arg1 + 0x19cc) = eax_6",
	"1002070a          *(arg1 + 0x19f0) = 0",
	"10020730    void sub_10020730(int32_t arg1)",
	"1002075d  if (sub_10020600(ebx) == 0)",
	"10020789          eax_4, edx_1 = sub_10018900(eax_4, edx_1, i, ebx)",
	"10020919      *(ebx + 0x19a8) = 0xb",
	"1002092d      *(ebx + 0x1794) = fconvert.s(fconvert.t(5.0) + x87_r7_12)",
	"10020939      *(ebx + 0x1a48) = fconvert.s(x87_r7_12 + fconvert.t(60.0))",
	"10020942      *(ebx + 0x19e8) = *ebp",
	"10020948      sub_10020600(ebx)",
	"1002095f  __builtin_memcpy(dest: arg1, src: ebx + 0x19c0, n: 0x40)",
)


GHIDRA_ANCHORS = (
	"/* FUN_10020200 @ 10020200 size 1018 */",
	"void FUN_10020200(int param_1)",
	"FUN_10018b20(*(undefined4 *)(param_1 + 8),param_1 + 0x1984,DAT_1008b330,",
	"(*(undefined4 *)(param_1 + 0x1334),param_1 + 0x130c,iVar1,0x11c0fbe),",
	"local_380 = *(int *)(param_1 + 0x196c);",
	"FUN_10020730(param_2);",
	"iVar1 = FUN_10020200(param_1);",
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(text)):
		char = text[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def _function_rows_by_entry() -> dict[str, dict[str, str]]:
	with QAGAME_FUNCTIONS.open(newline="", encoding="utf-8") as file:
		return {row["entry"].lower(): row for row in csv.DictReader(file)}


def test_instagib_target_goal_aliases_metadata_and_source_are_pinned() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry()
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}
	source = _read(GAME_AI_DMQ3)
	header = _read(GAME_AI_DMQ3_H)

	for address, raw_name, normalized_name, signature, size in INSTAGIB_TARGET_FUNCTIONS:
		assert aliases[raw_name] == normalized_name
		assert aliases[f"sub_{address}"] == normalized_name

		row = function_rows[address]
		assert row["name"] == raw_name
		assert int(row["size"]) == size
		assert row["thunk"] == "0"

		symbol = symbol_map[f"0x{address}"]
		assert symbol["raw_name"] == raw_name
		assert symbol["normalized_name"] == normalized_name
		assert symbol["status"] == "matched"
		assert symbol["signature"] == signature

		assert f"{signature};" in header
		block = _extract_function_block(source, signature)
		for anchor in SOURCE_ANCHORS[normalized_name]:
			assert anchor in block, normalized_name


def test_instagib_target_goal_hlil_and_ghidra_evidence_is_pinned() -> None:
	hlil = _read(QAGAME_HLIL_PART01)
	decompile_top = _read(QAGAME_DECOMPILE_TOP)

	for anchor in HLIL_ANCHORS:
		assert anchor in hlil

	for anchor in GHIDRA_ANCHORS:
		assert anchor in decompile_top


def test_instagib_target_goal_botlib_route_wiring_is_pinned() -> None:
	ai_main = _read(GAME_AI_MAIN)
	g_public = _read(GAME_PUBLIC)
	g_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)

	assert "void BotEntityInfo(int entnum, aas_entityinfo_t *info)" in ai_main
	assert "trap_AAS_EntityInfo(entnum, info);" in ai_main

	for anchor in (
		"BOTLIB_AAS_ENTITY_INFO,",
		"BOTLIB_AAS_POINT_AREA_NUM,",
		"BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX,",
		"BOTLIB_AAS_TRACE_AREAS,",
		"BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA,",
		"G_QL_IMPORT_BOTLIB_AAS_ENTITY_INFO = 63,",
		"G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM = 67,",
		"G_QL_IMPORT_BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX = 68,",
		"G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS = 69,",
		"G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA = 77,",
	):
		assert anchor in g_public

	for anchor in (
		"case BOTLIB_AAS_ENTITY_INFO: return G_QL_IMPORT_BOTLIB_AAS_ENTITY_INFO;",
		"case BOTLIB_AAS_POINT_AREA_NUM: return G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM;",
		"case BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX: return G_QL_IMPORT_BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX;",
		"case BOTLIB_AAS_TRACE_AREAS: return G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS;",
		"case BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA: return G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA;",
		"void trap_AAS_EntityInfo(int entnum, void /* struct aas_entityinfo_s */ *info)",
		"return syscall( BOTLIB_AAS_POINT_AREA_NUM, point );",
		"return syscall( BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX, point );",
		"return syscall( BOTLIB_AAS_TRACE_AREAS, start, end, areas, points, maxareas );",
		"return syscall( BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA, areanum, origin, goalareanum, travelflags );",
	):
		assert anchor in g_syscalls

	for anchor in (
		"[BOTLIB_AAS_ENTITY_INFO] = (ql_import_f)QL_G_trap_AAS_EntityInfo,",
		"[BOTLIB_AAS_POINT_AREA_NUM] = (ql_import_f)QL_G_trap_AAS_PointAreaNum,",
		"[BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX] = (ql_import_f)QL_G_trap_AAS_PointReachabilityAreaIndex,",
		"[BOTLIB_AAS_TRACE_AREAS] = (ql_import_f)QL_G_trap_AAS_TraceAreas,",
		"[BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA] = (ql_import_f)QL_G_trap_AAS_AreaTravelTimeToGoalArea,",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_ENTITY_INFO] = (ql_import_f)QL_G_trap_AAS_EntityInfo;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM] = (ql_import_f)QL_G_trap_AAS_PointAreaNum;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX] = (ql_import_f)QL_G_trap_AAS_PointReachabilityAreaIndex;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS] = (ql_import_f)QL_G_trap_AAS_TraceAreas;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA] = (ql_import_f)QL_G_trap_AAS_AreaTravelTimeToGoalArea;",
	):
		assert anchor in server_game

	for anchor in (
		"static void QDECL QL_G_trap_AAS_EntityInfo( int entnum, void /* struct aas_entityinfo_s */ *info )",
		"static int QDECL QL_G_trap_AAS_PointAreaNum( vec3_t point )",
		"static int QDECL QL_G_trap_AAS_PointReachabilityAreaIndex( vec3_t point )",
		"static int QDECL QL_G_trap_AAS_TraceAreas( vec3_t start, vec3_t end, int *areas, vec3_t *points, int maxareas )",
		"static int QDECL QL_G_trap_AAS_AreaTravelTimeToGoalArea( int areanum, vec3_t origin, int goalareanum, int travelflags )",
		"G_Import_Syscall( BOTLIB_AAS_ENTITY_INFO, entnum, info );",
		"return G_Import_Syscall( BOTLIB_AAS_POINT_AREA_NUM, point );",
		"return G_Import_Syscall( BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX, point );",
		"return G_Import_Syscall( BOTLIB_AAS_TRACE_AREAS, start, end, areas, points, maxareas );",
		"return G_Import_Syscall( BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA, areanum, origin, goalareanum, travelflags );",
	):
		assert anchor in ql_game_imports
