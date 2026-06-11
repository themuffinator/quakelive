from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_AI_DMQ3 = REPO_ROOT / "src" / "code" / "game" / "ai_dmq3.c"
GAME_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
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
QAGAME_HLIL_PART01 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part01.txt"
)


AI_DMQ3_VISIBILITY_FUNCTIONS = (
	("10017d20", "FUN_10017d20", "BotRoamGoal", "void BotRoamGoal(bot_state_t *bs, vec3_t goal)", 1372),
	("10018280", "FUN_10018280", "BotAttackMove", "bot_moveresult_t BotAttackMove(bot_state_t *bs, int tfl)", 1652),
	("10018900", "FUN_10018900", "BotSameTeam", "int BotSameTeam(bot_state_t *bs, int entnum)", 245),
	("10018a00", "FUN_10018a00", "InFieldOfVision", "int InFieldOfVision(vec3_t viewangles, float fov, vec3_t angles)", 276),
	("10018b20", "FUN_10018b20", "BotEntityVisible", "float BotEntityVisible(int viewer, vec3_t eye, vec3_t viewangles, float fov, int ent)", 1889),
	("10019290", "FUN_10019290", "BotFindEnemy", "int BotFindEnemy(bot_state_t *bs, int curenemy)", 1536),
	("100198a0", "FUN_100198a0", "BotTeamFlagCarrierVisible", "int BotTeamFlagCarrierVisible(bot_state_t *bs)", 201),
	("10019970", "FUN_10019970", "BotTeamFlagCarrier", "int BotTeamFlagCarrier(bot_state_t *bs)", 168),
	("10019a20", "FUN_10019a20", "BotEnemyFlagCarrierVisible", "int BotEnemyFlagCarrierVisible(bot_state_t *bs)", 201),
	("10019af0", "FUN_10019af0", "BotVisibleTeamMatesAndEnemies", "void BotVisibleTeamMatesAndEnemies(bot_state_t *bs, int *teammates, int *enemies, float range)", 357),
	("10019c60", "FUN_10019c60", "BotTeamCubeCarrierVisible", "int BotTeamCubeCarrierVisible(bot_state_t *bs)", 208),
	("10019d30", "FUN_10019d30", "BotEnemyCubeCarrierVisible", "int BotEnemyCubeCarrierVisible(bot_state_t *bs)", 208),
)


SOURCE_HELPERS = {
	"BotRoamGoal": (
		"void BotRoamGoal(bot_state_t *bs, vec3_t goal)",
		(
			"for (i = 0; i < 10; i++)",
			"800 * random() + 100",
			"bestorg[2] += 2 * 48 * crandom();",
			"BotAI_Trace(&trace, bs->origin, NULL, NULL, bestorg, bs->entitynum, MASK_SOLID);",
			"if (len > 200)",
			"BotAI_Trace(&trace, bestorg, NULL, NULL, belowbestorg, bs->entitynum, MASK_SOLID);",
			"pc = trap_PointContents(trace.endpos, bs->entitynum);",
			"CONTENTS_LAVA | CONTENTS_SLIME",
		),
	),
	"BotAttackMove": (
		"bot_moveresult_t BotAttackMove(bot_state_t *bs, int tfl)",
		(
			"if (bs->attackchase_time > FloatTime())",
			"goal.entitynum = attackentity;",
			"VectorSet(goal.mins, -8, -8, -8);",
			"VectorSet(goal.maxs, 8, 8, 8);",
			"BotSetupForMovement(bs);",
			"trap_BotMoveToGoal(&moveresult, bs->ms, &goal, tfl);",
			"CHARACTERISTIC_ATTACK_SKILL",
			"CHARACTERISTIC_JUMPER",
			"CHARACTERISTIC_CROUCHER",
			"if (attack_skill < 0.2) return moveresult;",
			"if (bs->cur_ps.weapon == WP_GAUNTLET)",
			"attack_dist = IDEAL_ATTACKDIST;",
			"attack_range = 40;",
			"if (trap_BotMoveInDirection(bs->ms, forward, 400, movetype)) return moveresult;",
			"bs->attackstrafe_time += bs->thinktime;",
			"strafechange_time = 0.4 + (1 - attack_skill) * 0.2;",
			"if (attack_skill > 0.7) strafechange_time += crandom() * 0.2;",
			"if (random() > 0.935)",
			"bs->flags ^= BFL_STRAFERIGHT;",
			"for (i = 0; i < 2; i++)",
			"CrossProduct(hordir, up, sideward);",
			"if (random() > 0.9)",
			"VectorAdd(sideward, backward, sideward);",
			"if (trap_BotMoveInDirection(bs->ms, sideward, 400, movetype))",
			"bs->attackstrafe_time = 0;",
		),
	),
	"BotSameTeam": (
		"int BotSameTeam(bot_state_t *bs, int entnum)",
		(
			"if ( gametype >= GT_TEAM )",
			"trap_GetConfigstring(CS_PLAYERS+bs->client, info1, sizeof(info1));",
			"trap_GetConfigstring(CS_PLAYERS+entnum, info2, sizeof(info2));",
			"PLAYER_INFO_KEY_TEAM",
		),
	),
	"InFieldOfVision": (
		"qboolean InFieldOfVision(vec3_t viewangles, float fov, vec3_t angles)",
		(
			"for (i = 0; i < 2; i++)",
			"angle = AngleMod(viewangles[i]);",
			"angles[i] = AngleMod(angles[i]);",
			"if (diff > 180.0) diff -= 360.0;",
			"if (diff < -180.0) diff += 360.0;",
			"if (diff > fov * 0.5) return qfalse;",
			"if (diff < -fov * 0.5) return qfalse;",
		),
	),
	"BotEntityVisible": (
		"float BotEntityVisible(int viewer, vec3_t eye, vec3_t viewangles, float fov, int ent)",
		(
			"VectorAdd(entinfo.mins, entinfo.maxs, middle);",
			"if (!InFieldOfVision(viewangles, fov, entangles)) return 0;",
			"pc = trap_AAS_PointContents(eye);",
			"CONTENTS_LAVA|CONTENTS_SLIME|CONTENTS_WATER",
			"BotAI_Trace(&trace, start, NULL, NULL, end, passent, contents_mask);",
			"BotAI_Trace(&trace, trace.endpos, NULL, NULL, end, passent, contents_mask);",
			"vis = 1 / ((squaredfogdist * 0.001) < 1 ? 1 : (squaredfogdist * 0.001));",
			"if (bestvis >= 0.95) return bestvis;",
		),
	),
	"BotFindEnemy": (
		"int BotFindEnemy(bot_state_t *bs, int curenemy)",
		(
			"CHARACTERISTIC_ALERTNESS",
			"CHARACTERISTIC_EASY_FRAGGER",
			"if (gametype == GT_OBELISK)",
			"if (EntityCarriesFlag(&curenemyinfo)) return qfalse;",
			"BotClientHasNoTargetFlag( i )",
			"EntityIsInvisible(&entinfo) && !EntityIsShooting(&entinfo)",
			"easyfragger < 0.5 && EntityIsChatting(&entinfo)",
			"lastteleport_time > FloatTime() - 3",
			"BotSameTeam(bs, i)",
			"BotEntityVisible(bs->entitynum, bs->eye, bs->viewangles, f, i)",
			"if (vis <= 0)",
			"BotAcceptOffscreenEnemyCandidate(bs, i)",
			"BotUpdateBattleInventory(bs, i);",
			"BotWantsToRetreat(bs)",
			"bs->enemyFromGoalStack = offscreenEnemy;",
		),
	),
	"BotTeamFlagCarrierVisible": (
		"int BotTeamFlagCarrierVisible(bot_state_t *bs)",
		(
			"if (!EntityCarriesFlag(&entinfo))",
			"if (!BotSameTeam(bs, i))",
			"vis = BotEntityVisible(bs->entitynum, bs->eye, bs->viewangles, 360, i);",
		),
	),
	"BotTeamFlagCarrier": (
		"int BotTeamFlagCarrier(bot_state_t *bs)",
		(
			"if (!EntityCarriesFlag(&entinfo))",
			"if (!BotSameTeam(bs, i))",
			"return i;",
		),
	),
	"BotEnemyFlagCarrierVisible": (
		"int BotEnemyFlagCarrierVisible(bot_state_t *bs)",
		(
			"if (!EntityCarriesFlag(&entinfo))",
			"if (BotSameTeam(bs, i))",
			"vis = BotEntityVisible(bs->entitynum, bs->eye, bs->viewangles, 360, i);",
		),
	),
	"BotVisibleTeamMatesAndEnemies": (
		"void BotVisibleTeamMatesAndEnemies(bot_state_t *bs, int *teammates, int *enemies, float range)",
		(
			"if (teammates)",
			"if (enemies)",
			"if (!EntityCarriesFlag(&entinfo))",
			"if (VectorLengthSquared(dir) > Square(range))",
			"vis = BotEntityVisible(bs->entitynum, bs->eye, bs->viewangles, 360, i);",
			"if (BotSameTeam(bs, i))",
			"(*teammates)++;",
			"(*enemies)++;",
		),
	),
	"BotTeamCubeCarrierVisible": (
		"int BotTeamCubeCarrierVisible(bot_state_t *bs)",
		(
			"if (!EntityCarriesCubes(&entinfo)) continue;",
			"if (!BotSameTeam(bs, i)) continue;",
			"vis = BotEntityVisible(bs->entitynum, bs->eye, bs->viewangles, 360, i);",
		),
	),
	"BotEnemyCubeCarrierVisible": (
		"int BotEnemyCubeCarrierVisible(bot_state_t *bs)",
		(
			"if (!EntityCarriesCubes(&entinfo)) continue;",
			"if (BotSameTeam(bs, i))",
			"vis = BotEntityVisible(bs->entitynum, bs->eye, bs->viewangles, 360, i);",
		),
	),
}


HLIL_ENTRY_ANCHORS = (
	"10017d20    long double sub_10017d20(void* arg1 @ edi, float* arg2)",
	"10018280    int32_t sub_10018280(void* arg1 @ edi, long double arg2 @ st1, long double arg3 @ st2, int32_t arg4, int32_t arg5)",
	'10018900    int32_t __convention("regparm") sub_10018900(int32_t arg1, int32_t arg2, int32_t arg3, void* arg4)',
	'10018a00    long double __convention("regparm") sub_10018a00(float* arg1, int32_t arg2, int32_t arg3, float arg4)',
	"10018b20    long double sub_10018b20(int32_t arg1, int32_t arg2, float arg3, int32_t arg4)",
	'10019290    int32_t __convention("regparm") sub_10019290(int32_t arg1, int32_t arg2, void* arg3, long double arg4 @ st0, long double arg5 @ st1, int32_t arg6)',
	"100198a0    int32_t sub_100198a0(void* arg1 @ edi)",
	"10019970    int32_t sub_10019970(void* arg1 @ edi, int32_t arg2)",
	"10019a20    int32_t sub_10019a20(void* arg1 @ edi)",
	"10019af0    int32_t* sub_10019af0(void* arg1 @ edi, int32_t* arg2, int32_t* arg3)",
	"10019c60    int32_t sub_10019c60(void* arg1 @ edi)",
	"10019d30    int32_t sub_10019d30(void* arg1 @ edi)",
)


HLIL_FLOW_ANCHORS = (
	"10017f23      (*(data_104b13ac + 0x80))(&var_b8, arg1 + 0x130c, 0, 0, &var_24, *(arg1 + 0xc), 1)",
	"1001805f      if (result_1 <= result_2)",
	"10018113          (*(ecx_5 + 0x80))(&var_b8, &var_24, 0, 0, &var_18, eax_20, 1)",
	"10018223              if (((*(data_104b13ac + 0x88))(&var_74, *(arg1 + 0xc)) & 0x18) == 0)",
	"1001837e      esi_1 = arg4",
	"1001838a      memset(esi_1, 0, 0x34)",
	"100183b3      (*(data_104b13ac + 0x1c4))(*(arg1 + 0x1958), 2, fconvert.s(float.t(0)),",
	"1001841c      if (not(fconvert.t(0.20000000000000001) > fconvert.t(var_174_1)))",
	"10018424          sub_10015f70(arg1)",
	"1001855c                              fconvert.s(x87_r2_17 * fconvert.t(5.0) + x87_r1_7)",
	"100185a9                  *(arg1 + 0x17d0) = fconvert.s(x87_r2_13 + fconvert.t(1.0))",
	"100185b9              var_17c_3 = 140f",
	"1001868f                  + (float.t(1) - x87_r2_21) * fconvert.t(0.20000000000000001))",
	"100186da                      <= fconvert.t(0.93500000000000005)))",
	"10018702                  *(arg1 + 0x173c) ^= 1",
	"100187c0                  eax_19, ecx_11 = rand()",
	"100187e5                          > fconvert.t(0.90000000000000002))",
	"100188b7                  if ((*(data_104b13ac + 0x2a0))(*(arg1 + 0x195c), &var_2c,",
	"100188b9                  *(arg1 + 0x173c) ^= 1",
	"100188c4                  *(arg1 + 0x17c4) = 0",
	"10018973          (*(data_104b13ac + 0x68))(eax_3 + 0x211, &var_404, 0x400)",
	"100189c0          if (atoi(sub_10070cf0()) == eax_8)",
	"10018a3d      float var_4_1 = fconvert.s(",
	"10018ae9  while (i s< 2)",
	"10018c51  result_1, eax_4 = sub_10018a00(&var_18, sub_100702b0(&var_254, &var_18), arg2,",
	"10018d3d      if (((*(ecx_7 + 0x118))(&var_3c) & 0x38) == 0)",
	"10018dde      (*(data_104b13ac + 0x80))(&var_168, &var_24, 0, 0, &var_30, esi_1, eax_8)",
	"100191f9          float var_248_3 = fconvert.s(fconvert.t(fconvert.s(x87_r6_25 / x87_r5_6)))",
	"10019225          if (fconvert.t(var_244) >= result_2)",
	"100192d6  (*(data_104b13ac + 0x1c4))(*(esi + 0x1958), 0x2e, fconvert.s(float.t(0)),",
	"1001931e      (*(data_104b13ac + 0x1c4))(*(esi + 0x1958), 0x2d, fconvert.s(float.t(0)),",
	"1001946b      if (data_105e4ae8 == 7 && (var_148 f>= 1f || var_11c == *(edi_1 + 0x28)))",
	"1001951e                      if (var_240 != 0 && sub_10013c00(&var_240) == 0",
	"1001968d                                      eax_16, ecx_11 = sub_10018900(eax_15, edx_5, i, esi)",
	"10019716                                          eax_17, edx_7, xmm0_6 = sub_10018b20(",
	"10019729                                              sub_10020c10(eax_17, edx_7, esi, i.b)",
	"100197c1                                              int32_t eax_20 = sub_10018a00(&var_18, edx_8,",
	"100197d5                                                  sub_10016670(i_1, esi)",
	"100197da                                                  eax_21 = sub_10017470(esi)",
	"100198f5                  eax_3, ecx_3 = sub_10018900(eax_2, edx_2, i, arg1)",
	"1001991d                          sub_10018b20(*(arg1 + 0xc), arg1 + 0x1984, var_10c_3, i)",
	"100199cb                      && sub_10018900(eax_2, edx_2, i, arg1) != 0)",
	"10019a75                  eax_3, ecx_3 = sub_10018900(eax_2, edx_2, i, arg1)",
	"10019a9d                          sub_10018b20(*(arg1 + 0xc), arg1 + 0x1984, var_10c_3, i)",
	"10019bfb                          sub_10018b20(*(arg1 + 0xc), arg1 + 0x1984, var_120_3, i)",
	"10019c0e                          result = sub_10018900(result, edx_2, i, arg1)",
	"10019cbc                      eax_3, ecx_3 = sub_10018900(eax_2, edx_2, i, arg1)",
	"10019ce4                              sub_10018b20(*(arg1 + 0xc), arg1 + 0x1984, var_10c_3, i)",
	"10019d7d                  eax_2, edx_2 = sub_10013c80(&var_f8)",
	"10019d8c                      eax_3, ecx_3 = sub_10018900(eax_2, edx_2, i, arg1)",
	"10019db4                              sub_10018b20(*(arg1 + 0xc), arg1 + 0x1984, var_10c_3, i)",
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _extract_function_block(text: str, signature: str) -> str:
	scan_text = "\n".join(line.split("//", 1)[0] for line in text.splitlines())
	start = scan_text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = scan_text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(scan_text)):
		char = scan_text[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return scan_text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def _function_rows_by_entry(path: Path) -> dict[str, dict[str, str]]:
	with path.open(newline="", encoding="utf-8") as file:
		return {row["entry"].lower(): row for row in csv.DictReader(file)}


def test_qagame_ai_dmq3_visibility_aliases_source_and_hlil_are_pinned() -> None:
	source = _read(GAME_AI_DMQ3)
	hlil = _read(QAGAME_HLIL_PART01)
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}

	for address, raw_name, normalized_name, signature, size in AI_DMQ3_VISIBILITY_FUNCTIONS:
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

		source_signature, source_anchors = SOURCE_HELPERS[normalized_name]
		block = _extract_function_block(source, source_signature)
		for anchor in source_anchors:
			assert anchor in block

	for expected in HLIL_ENTRY_ANCHORS:
		assert expected in hlil

	for expected in HLIL_FLOW_ANCHORS:
		assert expected in hlil


def test_qagame_ai_dmq3_visibility_botlib_import_wiring_is_pinned() -> None:
	ai_dmq3 = _read(GAME_AI_DMQ3)
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)

	for expected in (
		"G_QL_IMPORT_BOTLIB_AAS_POINT_CONTENTS = 70,",
		"G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT = 113,",
		"G_QL_IMPORT_BOTLIB_AI_MOVE_TO_GOAL = 167,",
		"G_QL_IMPORT_BOTLIB_AI_MOVE_IN_DIRECTION = 168,",
	):
		assert expected in game_public

	for expected in (
		"case BOTLIB_AAS_POINT_CONTENTS: return G_QL_IMPORT_BOTLIB_AAS_POINT_CONTENTS;",
		"case BOTLIB_AI_CHARACTERISTIC_BFLOAT: return G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT;",
		"case BOTLIB_AI_MOVE_TO_GOAL: return G_QL_IMPORT_BOTLIB_AI_MOVE_TO_GOAL;",
		"case BOTLIB_AI_MOVE_IN_DIRECTION: return G_QL_IMPORT_BOTLIB_AI_MOVE_IN_DIRECTION;",
		"return syscall( BOTLIB_AAS_POINT_CONTENTS, point );",
		"temp = syscall( BOTLIB_AI_CHARACTERISTIC_BFLOAT, character, index, PASSFLOAT(min), PASSFLOAT(max) );",
		"syscall( BOTLIB_AI_MOVE_TO_GOAL, result, movestate, goal, travelflags );",
		"return syscall( BOTLIB_AI_MOVE_IN_DIRECTION, movestate, dir, PASSFLOAT(speed), type );",
	):
		assert expected in game_syscalls

	for expected in (
		"case BOTLIB_AAS_POINT_CONTENTS:",
		"case BOTLIB_AI_CHARACTERISTIC_BFLOAT:",
		"case BOTLIB_AI_MOVE_TO_GOAL:",
		"case BOTLIB_AI_MOVE_IN_DIRECTION:",
		"[BOTLIB_AAS_POINT_CONTENTS] = (ql_import_f)QL_G_trap_AAS_PointContents,",
		"[BOTLIB_AI_CHARACTERISTIC_BFLOAT] = (ql_import_f)QL_G_trap_Characteristic_BFloat,",
		"[BOTLIB_AI_MOVE_TO_GOAL] = (ql_import_f)QL_G_trap_BotMoveToGoal,",
		"[BOTLIB_AI_MOVE_IN_DIRECTION] = (ql_import_f)QL_G_trap_BotMoveInDirection,",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_POINT_CONTENTS] = (ql_import_f)QL_G_trap_AAS_PointContents;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT] = (ql_import_f)QL_G_trap_Characteristic_BFloat;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVE_TO_GOAL] = (ql_import_f)QL_G_trap_BotMoveToGoal;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVE_IN_DIRECTION] = (ql_import_f)QL_G_trap_BotMoveInDirection;",
	):
		assert expected in server_game

	for expected in (
		"return G_Import_Syscall( BOTLIB_AAS_POINT_CONTENTS, point );",
		"temp = G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_BFLOAT, character, index, QL_G_PASSFLOAT(min), QL_G_PASSFLOAT(max) );",
		"G_Import_Syscall( BOTLIB_AI_MOVE_TO_GOAL, result, movestate, goal, travelflags );",
		"return G_Import_Syscall( BOTLIB_AI_MOVE_IN_DIRECTION, movestate, dir, QL_G_PASSFLOAT(speed), type );",
	):
		assert expected in ql_game_imports

	for expected in (
		"trap_AAS_PointContents(eye)",
		"trap_Characteristic_BFloat(bs->character, CHARACTERISTIC_ATTACK_SKILL, 0, 1);",
		"trap_Characteristic_BFloat(bs->character, CHARACTERISTIC_JUMPER, 0, 1);",
		"trap_Characteristic_BFloat(bs->character, CHARACTERISTIC_CROUCHER, 0, 1);",
		"trap_Characteristic_BFloat(bs->character, CHARACTERISTIC_ALERTNESS, 0, 1);",
		"trap_Characteristic_BFloat(bs->character, CHARACTERISTIC_EASY_FRAGGER, 0, 1);",
		"trap_BotMoveToGoal(&moveresult, bs->ms, &goal, tfl);",
		"trap_BotMoveInDirection(bs->ms, forward, 400, movetype)",
		"trap_BotMoveInDirection(bs->ms, sideward, 400, movetype)",
	):
		assert expected in ai_dmq3
