from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_AI_DMNET = REPO_ROOT / "src" / "code" / "game" / "ai_dmnet.c"
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


AI_DMNET_BATTLE_FUNCTIONS = (
	("1000c6e0", "FUN_1000c6e0", "AINode_Seek_NBG", "int AINode_Seek_NBG(bot_state_t *bs)", 1089),
	("1000cb30", "FUN_1000cb30", "AIEnter_Seek_LTG", "void AIEnter_Seek_LTG(bot_state_t *bs, char *s)", 166),
	("1000cbe0", "FUN_1000cbe0", "AINode_Seek_LTG", "int AINode_Seek_LTG(bot_state_t *bs)", 1641),
	("1000d250", "FUN_1000d250", "AIEnter_Battle_Fight", "void AIEnter_Battle_Fight(bot_state_t *bs, char *s)", 71),
	("1000d2a0", "FUN_1000d2a0", "AIEnter_Battle_SuicidalFight", "void AIEnter_Battle_SuicidalFight(bot_state_t *bs, char *s)", 65),
	("1000d2f0", "FUN_1000d2f0", "AINode_Battle_Fight", "int AINode_Battle_Fight(bot_state_t *bs)", 1480),
	("1000d8c0", "FUN_1000d8c0", "AIEnter_Battle_Chase", "void AIEnter_Battle_Chase(bot_state_t *bs, char *s)", 66),
	("1000d910", "FUN_1000d910", "AINode_Battle_Chase", "int AINode_Battle_Chase(bot_state_t *bs)", 1630),
	("1000df70", "FUN_1000df70", "AIEnter_Battle_Retreat", "void AIEnter_Battle_Retreat(bot_state_t *bs, char *s)", 50),
	("1000dfb0", "FUN_1000dfb0", "AINode_Battle_Retreat", "int AINode_Battle_Retreat(bot_state_t *bs)", 1823),
	("1000e6d0", "FUN_1000e6d0", "AIEnter_Battle_NBG", "void AIEnter_Battle_NBG(bot_state_t *bs, char *s)", 43),
	("1000e700", "FUN_1000e700", "AINode_Battle_NBG", "int AINode_Battle_NBG(bot_state_t *bs)", 1463),
)


SOURCE_ANCHORS = {
	"AINode_Seek_NBG": (
		'AIEnter_Observer(bs, "seek nbg: observer");',
		'AIEnter_Seek_LTG(bs, "seek nbg: time out");',
		"BotAIPredictObstacles(bs, &goal)",
		"trap_BotMoveToGoal(&moveresult, bs->ms, &goal, bs->tfl);",
		"BotClearPath(bs, &moveresult);",
		"trap_BotGetSecondGoal(bs->gs, &goal)",
		'AIEnter_Battle_NBG(bs, "seek nbg: found enemy");',
		'AIEnter_Battle_Fight(bs, "seek nbg: found enemy");',
	),
	"AIEnter_Seek_LTG": (
		"if (trap_BotGetTopGoal(bs->gs, &goal))",
		'BotRecordNodeSwitch(bs, "seek LTG", buf, s);',
		'BotRecordNodeSwitch(bs, "seek LTG", "no goal", s);',
		"bs->ainode = AINode_Seek_LTG;",
	),
	"AINode_Seek_LTG": (
		'AIEnter_Observer(bs, "seek ltg: observer");',
		"if (BotChat_Random(bs))",
		"AIEnter_Battle_Retreat(bs, \"seek ltg: found enemy\");",
		"trap_BotEmptyGoalStack(bs->gs);",
		"BotTeamGoals(bs, qfalse);",
		"if (!BotLongTermGoal(bs, bs->tfl, qfalse, &goal))",
		"if (bs->ltgtype == LTG_DEFENDKEYAREA) range = 400;",
		'AIEnter_Seek_NBG(bs, "ltg seek: nbg");',
		"BotClearPath(bs, &moveresult);",
		"trap_BotMovementViewTarget(bs->ms, &goal, bs->tfl, 300, target)",
	),
	"AIEnter_Battle_Fight": (
		'BotRecordNodeSwitch(bs, "battle fight", "", s);',
		"trap_BotResetLastAvoidReach(bs->ms);",
		"bs->ainode = AINode_Battle_Fight;",
	),
	"AIEnter_Battle_SuicidalFight": (
		'BotRecordNodeSwitch(bs, "battle fight", "", s);',
		"trap_BotResetLastAvoidReach(bs->ms);",
		"bs->ainode = AINode_Battle_Fight;",
		"bs->flags |= BFL_FIGHTSUICIDAL;",
	),
	"AINode_Battle_Fight": (
		'AIEnter_Observer(bs, "battle fight: observer");',
		'AIEnter_Seek_LTG(bs, "battle fight: no enemy");',
		"bs->enemydeath_time < FloatTime() - 1.0",
		"BotChat_EnemySuicide(bs);",
		"EntityIsInvisible(&entinfo) && !EntityIsShooting(&entinfo)",
		"BotUpdateBattleInventory(bs, bs->enemy);",
		"BotChat_HitNoDeath(bs)",
		"BotChat_HitNoKill(bs)",
		'AIEnter_Battle_Chase(bs, "battle fight: enemy out of sight");',
		"moveresult = BotAttackMove(bs, bs->tfl);",
		'AIEnter_Battle_Retreat(bs, "battle fight: wants to retreat");',
	),
	"AIEnter_Battle_Chase": (
		'BotRecordNodeSwitch(bs, "battle chase", "", s);',
		"bs->chase_time = FloatTime();",
		"bs->ainode = AINode_Battle_Chase;",
	),
	"AINode_Battle_Chase": (
		'AIEnter_Seek_LTG(bs, "battle chase: no enemy");',
		'AIEnter_Battle_Fight(bs, "battle chase: better enemy");',
		'AIEnter_Seek_LTG(bs, "battle chase: no enemy area");',
		"goal.areanum = bs->lastenemyareanum;",
		"VectorSet(goal.mins, -8, -8, -8);",
		"bs->chase_time < FloatTime() - 10",
		"BotNearbyGoal(bs, bs->tfl, &goal, range)",
		'AIEnter_Battle_NBG(bs, "battle chase: nbg");',
		"trap_BotMoveToGoal(&moveresult, bs->ms, &goal, bs->tfl);",
		"if (bs->areanum == bs->lastenemyareanum) bs->chase_time = 0;",
		'AIEnter_Battle_Retreat(bs, "battle chase: wants to retreat");',
	),
	"AIEnter_Battle_Retreat": (
		'BotRecordNodeSwitch(bs, "battle retreat", "", s);',
		"bs->ainode = AINode_Battle_Retreat;",
	),
	"AINode_Battle_Retreat": (
		'AIEnter_Seek_LTG(bs, "battle retreat: no enemy");',
		'AIEnter_Seek_LTG(bs, "battle retreat: enemy dead");',
		"trap_BotEmptyGoalStack(bs->gs);",
		'AIEnter_Battle_Chase(bs, "battle retreat: wants to chase");',
		"bs->enemyvisible_time < FloatTime() - 4",
		'AIEnter_Battle_Fight(bs, "battle retreat: another enemy");',
		"BotTeamGoals(bs, qtrue);",
		"if (!BotLongTermGoal(bs, bs->tfl, qtrue, &goal))",
		'AIEnter_Battle_SuicidalFight(bs, "battle retreat: no way out");',
		'AIEnter_Battle_NBG(bs, "battle retreat: nbg");',
		"BotCheckAttack(bs);",
	),
	"AIEnter_Battle_NBG": (
		'BotRecordNodeSwitch(bs, "battle NBG", "", s);',
		"bs->ainode = AINode_Battle_NBG;",
	),
	"AINode_Battle_NBG": (
		'AIEnter_Seek_NBG(bs, "battle nbg: no enemy");',
		'AIEnter_Seek_NBG(bs, "battle nbg: enemy dead");',
		"if (!trap_BotGetTopGoal(bs->gs, &goal))",
		"trap_BotPopGoal(bs->gs);",
		'AIEnter_Battle_Retreat(bs, "battle nbg: time out");',
		'AIEnter_Battle_Fight(bs, "battle nbg: time out");',
		"trap_BotMoveToGoal(&moveresult, bs->ms, &goal, bs->tfl);",
		"BotUpdateBattleInventory(bs, bs->enemy);",
		"trap_BotMovementViewTarget(bs->ms, &goal, bs->tfl, 300, target)",
		"BotCheckAttack(bs);",
	),
}


HLIL_ENTRY_ANCHORS = (
	"1000c6e0    int32_t sub_1000c6e0(int32_t* arg1)",
	"1000cb30    int32_t sub_1000cb30(void* arg1, int32_t arg2)",
	"1000cbe0    int32_t sub_1000cbe0(int32_t* arg1)",
	'1000d250    int32_t __convention("regparm") sub_1000d250(int32_t arg1, void* arg2 @ esi)',
	"1000d2a0    int32_t sub_1000d2a0(void* arg1 @ esi)",
	"1000d2f0    int32_t sub_1000d2f0(int32_t* arg1)",
	'1000d8c0    int32_t __convention("regparm") sub_1000d8c0(int32_t arg1, void* arg2 @ esi)',
	"1000d910    int32_t sub_1000d910(int32_t* arg1)",
	'1000df70    int32_t __convention("regparm") sub_1000df70(int32_t arg1, void* arg2 @ esi)',
	"1000dfb0    int32_t sub_1000dfb0(int32_t* arg1)",
	'1000e6d0    int32_t __convention("regparm") sub_1000e6d0(int32_t arg1, void* arg2 @ esi)',
	"1000e700    int32_t sub_1000e700(int32_t* arg1)",
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


def test_qagame_ai_dmnet_battle_node_aliases_source_and_hlil_are_pinned() -> None:
	source = _read(GAME_AI_DMNET)
	hlil = _read(QAGAME_HLIL_PART01)
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}

	for address, raw_name, normalized_name, signature, size in AI_DMNET_BATTLE_FUNCTIONS:
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

		block = _extract_function_block(source, signature)
		for anchor in SOURCE_ANCHORS[normalized_name]:
			assert anchor in block

	for expected in HLIL_ENTRY_ANCHORS:
		assert expected in hlil

	for expected in (
		"1000c6c2  *(arg1 + 0x1304) = sub_1000c6e0",
		'1000c88a          sub_1000cb30(arg1, "seek nbg: time out")',
		'1000cb02                  sub_1000d250("seek nbg: found enemy", arg1)',
		'1000cac6                  sub_1000e6d0("seek nbg: found enemy", arg1)',
		"1000cbc0  *(arg1 + 0x1304) = sub_1000cbe0",
		'1000cdf5              sub_1000df70("seek ltg: found enemy", arg1)',
		'1000ce46          sub_1000d250("seek ltg: found enemy", arg1)',
		"1000d27f  *(arg2 + 0x1304) = sub_1000d2f0",
		"1000d2d5  *(arg1 + 0x1304) = sub_1000d2f0",
		'1000d77c      sub_1000d8c0("battle fight: enemy out of sight", arg1)',
		'1000d899          sub_1000df70("battle fight: wants to retreat", arg1)',
		"1000d8ea  *(arg2 + 0x1304) = sub_1000d910",
		'1000dd1f                          sub_1000e6d0("battle chase: nbg", var_198)',
		'1000df28                      sub_1000df70("battle chase: wants to retreat", edi)',
		"1000df8a  *(arg2 + 0x1304) = sub_1000dfb0",
		"1000e19f      edi[0x4c1] = sub_1000d910",
		"1000e3c4      sub_1000d2a0(edi)",
		'1000e4bf          sub_1000e6d0("battle retreat: nbg", var_18c)',
		"1000e6e5  *(arg2 + 0x1304) = sub_1000e700",
		"1000ea4a      edi[0x4c1] = sub_1000dfb0",
		"1000ea97          edi[0x4c1] = sub_1000d2f0",
	):
		assert expected in hlil


def test_qagame_ai_dmnet_battle_botlib_movement_wiring_is_pinned() -> None:
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)
	ai_dmnet = _read(GAME_AI_DMNET)

	for expected in (
		"BOTLIB_AI_EMPTY_GOAL_STACK,",
		"BOTLIB_AI_GET_SECOND_GOAL,",
		"BOTLIB_AI_MOVE_TO_GOAL,",
		"BOTLIB_AI_RESET_AVOID_REACH,",
		"BOTLIB_AI_RESET_LAST_AVOID_REACH,",
		"BOTLIB_AI_MOVEMENT_VIEW_TARGET,",
		"G_QL_IMPORT_BOTLIB_AI_EMPTY_GOAL_STACK = 142,",
		"G_QL_IMPORT_BOTLIB_AI_GET_SECOND_GOAL = 147,",
		"G_QL_IMPORT_BOTLIB_AI_MOVE_TO_GOAL = 167,",
		"G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_REACH = 169,",
		"G_QL_IMPORT_BOTLIB_AI_RESET_LAST_AVOID_REACH = 170,",
		"G_QL_IMPORT_BOTLIB_AI_MOVEMENT_VIEW_TARGET = 172,",
	):
		assert expected in game_public

	for expected in (
		"case BOTLIB_AI_EMPTY_GOAL_STACK: return G_QL_IMPORT_BOTLIB_AI_EMPTY_GOAL_STACK;",
		"case BOTLIB_AI_GET_SECOND_GOAL: return G_QL_IMPORT_BOTLIB_AI_GET_SECOND_GOAL;",
		"case BOTLIB_AI_MOVE_TO_GOAL: return G_QL_IMPORT_BOTLIB_AI_MOVE_TO_GOAL;",
		"case BOTLIB_AI_RESET_AVOID_REACH: return G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_REACH;",
		"case BOTLIB_AI_RESET_LAST_AVOID_REACH: return G_QL_IMPORT_BOTLIB_AI_RESET_LAST_AVOID_REACH;",
		"case BOTLIB_AI_MOVEMENT_VIEW_TARGET: return G_QL_IMPORT_BOTLIB_AI_MOVEMENT_VIEW_TARGET;",
		"syscall( BOTLIB_AI_EMPTY_GOAL_STACK, goalstate );",
		"return syscall( BOTLIB_AI_GET_SECOND_GOAL, goalstate, goal );",
		"syscall( BOTLIB_AI_MOVE_TO_GOAL, result, movestate, goal, travelflags );",
		"syscall( BOTLIB_AI_RESET_AVOID_REACH, movestate );",
		"syscall( BOTLIB_AI_RESET_LAST_AVOID_REACH,movestate  );",
		"return syscall( BOTLIB_AI_MOVEMENT_VIEW_TARGET, movestate, goal, travelflags, PASSFLOAT(lookahead), target );",
	):
		assert expected in game_syscalls

	for expected in (
		"[BOTLIB_AI_EMPTY_GOAL_STACK] = (ql_import_f)QL_G_trap_BotEmptyGoalStack,",
		"[BOTLIB_AI_GET_SECOND_GOAL] = (ql_import_f)QL_G_trap_BotGetSecondGoal,",
		"[BOTLIB_AI_MOVE_TO_GOAL] = (ql_import_f)QL_G_trap_BotMoveToGoal,",
		"[BOTLIB_AI_RESET_AVOID_REACH] = (ql_import_f)QL_G_trap_BotResetAvoidReach,",
		"[BOTLIB_AI_RESET_LAST_AVOID_REACH] = (ql_import_f)QL_G_trap_BotResetLastAvoidReach,",
		"[BOTLIB_AI_MOVEMENT_VIEW_TARGET] = (ql_import_f)QL_G_trap_BotMovementViewTarget,",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_EMPTY_GOAL_STACK] = (ql_import_f)QL_G_trap_BotEmptyGoalStack;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_SECOND_GOAL] = (ql_import_f)QL_G_trap_BotGetSecondGoal;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVE_TO_GOAL] = (ql_import_f)QL_G_trap_BotMoveToGoal;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_REACH] = (ql_import_f)QL_G_trap_BotResetAvoidReach;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_RESET_LAST_AVOID_REACH] = (ql_import_f)QL_G_trap_BotResetLastAvoidReach;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVEMENT_VIEW_TARGET] = (ql_import_f)QL_G_trap_BotMovementViewTarget;",
	):
		assert expected in server_game

	for expected in (
		"static void QDECL QL_G_trap_BotEmptyGoalStack( int goalstate )",
		"static int QDECL QL_G_trap_BotGetSecondGoal( int goalstate, void /* struct bot_goal_s */ *goal )",
		"static void QDECL QL_G_trap_BotMoveToGoal( void /* struct bot_moveresult_s */ *result, int movestate, void /* struct bot_goal_s */ *goal, int travelflags )",
		"static void QDECL QL_G_trap_BotResetAvoidReach( int movestate )",
		"static void QDECL QL_G_trap_BotResetLastAvoidReach( int movestate )",
		"static int QDECL QL_G_trap_BotMovementViewTarget( int movestate, void /* struct bot_goal_s */ *goal, int travelflags, float lookahead, vec3_t target )",
		"G_Import_Syscall( BOTLIB_AI_EMPTY_GOAL_STACK, goalstate );",
		"return G_Import_Syscall( BOTLIB_AI_GET_SECOND_GOAL, goalstate, goal );",
		"G_Import_Syscall( BOTLIB_AI_MOVE_TO_GOAL, result, movestate, goal, travelflags );",
		"G_Import_Syscall( BOTLIB_AI_RESET_AVOID_REACH, movestate );",
		"G_Import_Syscall( BOTLIB_AI_RESET_LAST_AVOID_REACH,movestate  );",
		"return G_Import_Syscall( BOTLIB_AI_MOVEMENT_VIEW_TARGET, movestate, goal, travelflags, QL_G_PASSFLOAT(lookahead), target );",
	):
		assert expected in ql_game_imports

	for expected in (
		"trap_BotEmptyGoalStack(bs->gs);",
		"trap_BotGetSecondGoal(bs->gs, &goal)",
		"trap_BotMoveToGoal(&moveresult, bs->ms, &goal, bs->tfl);",
		"trap_BotResetAvoidReach(bs->ms);",
		"trap_BotResetLastAvoidReach(bs->ms);",
		"trap_BotMovementViewTarget(bs->ms, &goal, bs->tfl, 300, target)",
	):
		assert expected in ai_dmnet
