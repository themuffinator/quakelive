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


AI_DMNET_GOAL_FUNCTIONS = (
	("100083c0", "FUN_100083c0", "BotDumpNodeSwitches", "void BotDumpNodeSwitches(bot_state_t *bs)", 146),
	("10008460", "FUN_10008460", "BotRecordNodeSwitch", "void BotRecordNodeSwitch(bot_state_t *bs, char *node, char *str, char *s)", 169),
	("10008510", "FUN_10008510", "BotGetAirGoal", "int BotGetAirGoal(bot_state_t *bs, bot_goal_t *goal)", 887),
	("10008890", "FUN_10008890", "BotGoForAir", "int BotGoForAir(bot_state_t *bs, int tfl, bot_goal_t *ltg, float range)", 340),
	("100089f0", "FUN_100089f0", "BotNearbyGoal", "int BotNearbyGoal(bot_state_t *bs, int tfl, bot_goal_t *ltg, float range)", 181),
	("10008ab0", "FUN_10008ab0", "BotReachedGoal", "int BotReachedGoal(bot_state_t *bs, bot_goal_t *goal)", 427),
	("10008c60", "FUN_10008c60", "BotGetItemLongTermGoal", "int BotGetItemLongTermGoal(bot_state_t *bs, int tfl, bot_goal_t *goal)", 262),
	("10008d90", "FUN_10008d90", "BotGetLongTermGoal", "int BotGetLongTermGoal(bot_state_t *bs, int tfl, int retreat, bot_goal_t *goal)", 8762),
	("1000afd0", "FUN_1000afd0", "BotLongTermGoal", "int BotLongTermGoal(bot_state_t *bs, int tfl, int retreat, bot_goal_t *goal)", 1141),
	("1000b450", "FUN_1000b450", "AIEnter_Intermission", "void AIEnter_Intermission(bot_state_t *bs, char *s)", 93),
	("1000b4b0", "FUN_1000b4b0", "AINode_Intermission", "int AINode_Intermission(bot_state_t *bs)", 149),
	("1000b550", "FUN_1000b550", "AINode_Observer", "int AINode_Observer(bot_state_t *bs)", 96),
	("1000b5b0", "FUN_1000b5b0", "AIEnter_Stand", "void AIEnter_Stand(bot_state_t *bs, char *s)", 68),
	("1000b600", "FUN_1000b600", "AINode_Stand", "int AINode_Stand(bot_state_t *bs)", 371),
	("1000b780", "FUN_1000b780", "AIEnter_Respawn", "void AIEnter_Respawn(bot_state_t *bs, char *s)", 268),
	("1000b890", "FUN_1000b890", "AINode_Respawn", "int AINode_Respawn(bot_state_t *bs)", 252),
	("1000b990", "FUN_1000b990", "BotSelectActivateWeapon", "int BotSelectActivateWeapon(bot_state_t *bs)", 274),
	("1000bab0", "FUN_1000bab0", "BotClearPath", "void BotClearPath(bot_state_t *bs, bot_moveresult_t *moveresult)", 1221),
	("1000bf80", "FUN_1000bf80", "AINode_Seek_ActivateEntity", "int AINode_Seek_ActivateEntity(bot_state_t *bs)", 1715),
	("1000c640", "FUN_1000c640", "AIEnter_Seek_NBG", "void AIEnter_Seek_NBG(bot_state_t *bs, char *s)", 152),
)


SOURCE_ANCHORS = {
	"BotDumpNodeSwitches": (
		'BotAI_Print(PRT_MESSAGE, "%s at %1.1f switched more than %d AI nodes\\n", netname, FloatTime(), MAX_NODESWITCHES);',
		"BotAI_Print(PRT_MESSAGE, nodeswitch[i]);",
		'BotAI_Print(PRT_FATAL, "");',
	),
	"BotRecordNodeSwitch": (
		'Com_sprintf(nodeswitch[numnodeswitches], 144, "%s at %2.1f entered %s: %s from %s\\n", netname, FloatTime(), node, str, s);',
		'Com_sprintf(bs->ainodename, sizeof(bs->ainodename), "%s", node);',
		"numnodeswitches++;",
	),
	"BotGetAirGoal": (
		"vec3_t end, mins = {-15, -15, -2}, maxs = {15, 15, 2};",
		"end[2] += 1000;",
		"CONTENTS_SOLID|CONTENTS_PLAYERCLIP",
		"CONTENTS_WATER|CONTENTS_SLIME|CONTENTS_LAVA",
		"goal->flags = GFL_AIR;",
		"goal->entitynum = 0;",
	),
	"BotGoForAir": (
		"if (bs->lastair_time < FloatTime() - 6)",
		"if (BotGetAirGoal(bs, &goal))",
		"trap_BotPushGoal(bs->gs, &goal);",
		"while(trap_BotChooseNBGItem(bs->gs, bs->origin, bs->inventory, tfl, ltg, range))",
		"trap_AAS_PointContents(goal.origin) & (CONTENTS_WATER|CONTENTS_SLIME|CONTENTS_LAVA)",
		"trap_BotResetAvoidGoals(bs->gs);",
	),
	"BotNearbyGoal": (
		"if (BotGoForAir(bs, tfl, ltg, range)) return qtrue;",
		"if (BotCTFCarryingFlag(bs))",
		"< 300",
		"range = 50;",
		"ret = trap_BotChooseNBGItem(bs->gs, bs->origin, bs->inventory, tfl, ltg, range);",
	),
	"BotReachedGoal": (
		"if (goal->flags & GFL_ITEM)",
		"trap_BotTouchingGoal(bs->origin, goal)",
		"trap_BotSetAvoidGoalTime(bs->gs, goal->number, -1);",
		"trap_BotItemGoalInVisButNotVisible(bs->entitynum, bs->eye, bs->viewangles, goal)",
		"else if (goal->flags & GFL_AIR)",
		"if (bs->lastair_time > FloatTime() - 1) return qtrue;",
	),
	"BotGetItemLongTermGoal": (
		"if (!trap_BotGetTopGoal(bs->gs, goal))",
		"else if (BotReachedGoal(bs, goal))",
		"BotChooseWeapon(bs);",
		"if (trap_BotChooseLTGItem(bs->gs, bs->origin, bs->inventory, tfl))",
		"trap_BotResetAvoidGoals(bs->gs);",
		"trap_BotResetAvoidReach(bs->ms);",
	),
	"BotGetLongTermGoal": (
		"if (bs->ltgtype == LTG_TEAMHELP && !retreat)",
		'"help_start"',
		"if (VectorLengthSquared(dir) < Square(100))",
		"if (bs->ltgtype == LTG_TEAMACCOMPANY && !retreat)",
		'"accompany_arrive"',
		"if (BotGoForAir(bs, bs->tfl, &bs->teamgoal, 400))",
		'AIEnter_Seek_NBG(bs, "BotLongTermGoal: go for air");',
		"if (bs->ltgtype == LTG_DEFENDKEYAREA && !retreat",
		'"defend_start"',
		"if (bs->ltgtype == LTG_KILL && !retreat)",
		'"kill_start"',
		"if (bs->ltgtype == LTG_GETITEM && !retreat)",
		'"getitem_start"',
		"if (bs->ltgtype == LTG_PATROL && !retreat)",
		'"patrol_start"',
		'"captureflag_start"',
		'"attackenemybase_start"',
		'"harvest_start"',
	),
	"BotLongTermGoal": (
		"if (bs->lead_time > 0 && !retreat)",
		'"lead_stop"',
		'"followme"',
		"BotEntityInfo(bs->lead_teammate, &entinfo);",
		"bs->lead_teamgoal.entitynum = bs->lead_teammate;",
		"bs->leadvisible_time = FloatTime();",
		"bs->leadbackup_time = FloatTime() + 2;",
		"return BotGetLongTermGoal(bs, tfl, retreat, goal);",
	),
	"AIEnter_Intermission": (
		'BotRecordNodeSwitch(bs, "intermission", "", s);',
		"BotResetState(bs);",
		"if (BotChat_EndLevel(bs))",
		"bs->ainode = AINode_Intermission;",
	),
	"AINode_Intermission": (
		"if (!BotIntermission(bs))",
		"if (BotChat_StartLevel(bs))",
		"bs->stand_time = FloatTime() + BotChatTime(bs);",
		'AIEnter_Stand(bs, "intermission: chat");',
	),
	"AINode_Observer": (
		"if (!BotIsObserver(bs))",
		'AIEnter_Stand(bs, "observer: left observer");',
	),
	"AIEnter_Stand": (
		'BotRecordNodeSwitch(bs, "stand", "", s);',
		"bs->standfindenemy_time = FloatTime() + 1;",
		"bs->ainode = AINode_Stand;",
	),
	"AINode_Stand": (
		"if (bs->lastframe_health > bs->inventory[INVENTORY_HEALTH])",
		"if (BotChat_HitTalking(bs))",
		"if (BotFindEnemy(bs, -1))",
		'AIEnter_Battle_Fight(bs, "stand: found enemy");',
		"trap_EA_Talk(bs->client);",
		'AIEnter_Seek_LTG(bs, "stand: time out");',
	),
	"AIEnter_Respawn": (
		'BotRecordNodeSwitch(bs, "respawn", "", s);',
		"trap_BotResetMoveState(bs->ms);",
		"trap_BotResetGoalState(bs->gs);",
		"trap_BotResetAvoidGoals(bs->gs);",
		"if (BotChat_Death(bs))",
		"bs->ainode = AINode_Respawn;",
	),
	"AINode_Respawn": (
		"if (bs->respawn_wait)",
		'AIEnter_Seek_LTG(bs, "respawn: respawned");',
		"trap_EA_Respawn(bs->client);",
		"trap_BotEnterChat(bs->cs, 0, bs->chatto);",
		"trap_EA_Talk(bs->client);",
	),
	"BotSelectActivateWeapon": (
		"INVENTORY_MACHINEGUN",
		"WEAPONINDEX_MACHINEGUN",
		"INVENTORY_PLASMAGUN",
		"WEAPONINDEX_ROCKET_LAUNCHER",
		"WEAPONINDEX_BFG",
		"return -1;",
	),
	"BotClearPath": (
		"if (bs->kamikazebody)",
		"BotAI_GetEntityState(bs->kamikazebody, &state);",
		"moveresult->weapon = BotSelectActivateWeapon(bs);",
		"MOVERESULT_BLOCKEDBYAVOIDSPOT",
		"for (i = 0; i < bs->numproxmines; i++)",
		"BotAI_GetEntityState(bs->proxmines[bestmine], &state);",
		"trap_EA_Attack(bs->client);",
	),
	"AINode_Seek_ActivateEntity": (
		"BotClearActivateGoalStack(bs);",
		'AIEnter_Seek_NBG(bs, "activate entity: no goal");',
		"BotAI_Trace(&bsptrace, bs->eye, NULL, NULL, bs->activatestack->target, bs->entitynum, MASK_SHOT);",
		"BotPopFromActivateGoalStack(bs);",
		'AIEnter_Seek_NBG(bs, "activate entity: time out");',
		"BotAIPredictObstacles(bs, goal)",
		"trap_BotMoveToGoal(&moveresult, bs->ms, goal, bs->tfl);",
		"BotClearPath(bs, &moveresult);",
		"trap_BotMovementViewTarget(bs->ms, goal, bs->tfl, 300, target)",
		'AIEnter_Battle_Fight(bs, "activate entity: found enemy");',
	),
	"AIEnter_Seek_NBG": (
		"if (trap_BotGetTopGoal(bs->gs, &goal))",
		"trap_BotGoalName(goal.number, buf, 144);",
		'BotRecordNodeSwitch(bs, "seek NBG", buf, s);',
		'BotRecordNodeSwitch(bs, "seek NBG", "no goal", s);',
		"bs->ainode = AINode_Seek_NBG;",
	),
}


HLIL_ENTRY_ANCHORS = (
	"100083c0    int32_t sub_100083c0(void* arg1)",
	"10008460    int32_t sub_10008460(void* arg1, int32_t arg2, int32_t arg3, int32_t arg4)",
	"10008510    int32_t __fastcall sub_10008510(void* arg1, int32_t* arg2 @ edi)",
	"10008890    int32_t sub_10008890(void* arg1 @ esi, int32_t arg2, int32_t arg3, float arg4)",
	'100089f0    int32_t __convention("regparm") sub_100089f0(void* arg1, int32_t arg2 @ edi, float arg3)',
	'10008ab0    void __convention("regparm") sub_10008ab0(void* arg1, float* arg2 @ esi)',
	"10008c60    long double sub_10008c60(void* arg1 @ edi, int32_t arg2)",
	'10008d90    int32_t __convention("regparm") sub_10008d90(int32_t arg1, float* arg2, int32_t arg3, void* arg4, int32_t arg5)',
	'1000afd0    int32_t __convention("regparm") sub_1000afd0(int32_t arg1, int32_t arg2, float* arg3, void* arg4, int32_t arg5, int32_t arg6)',
	'1000b450    int32_t __convention("regparm") sub_1000b450(int32_t arg1, int32_t arg2, int32_t* arg3)',
	"1000b4b0    int32_t sub_1000b4b0(void* arg1)",
	"1000b550    int32_t sub_1000b550(void* arg1)",
	'1000b5b0    int32_t __convention("regparm") sub_1000b5b0(int32_t arg1, void* arg2 @ esi)',
	"1000b600    int32_t sub_1000b600(void* arg1)",
	'1000b780    int32_t __convention("regparm") sub_1000b780(int32_t arg1, int32_t arg2, void* arg3)',
	"1000b890    void sub_1000b890(float arg1)",
	'1000b990    int32_t __convention("regparm") sub_1000b990(void* arg1)',
	'1000bab0    int32_t __convention("regparm") sub_1000bab0(int32_t arg1, int32_t arg2, void* arg3, void* arg4)',
	"1000bf80    int32_t sub_1000bf80(int32_t* arg1)",
	"1000c640    int32_t sub_1000c640(void* arg1 @ esi, int32_t arg2 @ edi)",
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


def test_qagame_ai_dmnet_goal_prelude_aliases_source_and_hlil_are_pinned() -> None:
	source = _read(GAME_AI_DMNET)
	hlil = _read(QAGAME_HLIL_PART01)
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}

	for address, raw_name, normalized_name, signature, size in AI_DMNET_GOAL_FUNCTIONS:
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
		"100088c7      eax_2, ecx_2 = sub_10008510(arg1, &var_48)",
		"100089fe  eax, ecx_1 = sub_10008890(arg1, ebx, arg2, fconvert.s(fconvert.t(arg3)))",
		"10008c8f      st0_1, eax_2 = sub_10008ab0(arg1, __saved_esi_4)",
		"100096e8                      sub_10008890(arg4, *(arg4 + 0x1738), arg4 + 0x19c0, var_358_19)",
		'10009722                      sub_1000c640(arg4, "BotLongTermGoal: go for air")',
		"1000b424      result = sub_10008d90(eax_1, arg3, arg6, arg4, arg5)",
		'1000b45f  sub_10008460(arg3, "intermission", &data_1007c414, arg1)',
		"1000b4a1  arg3[0x4c1] = sub_1000b4b0",
		'1000b50d      sub_10008460(arg1, "stand", &data_1007c414, "intermission: chat")',
		"1000b521      *(arg1 + 0x1304) = sub_1000b600",
		'1000b792  sub_10008460(arg3, "respawn", &data_1007c414, arg1)',
		"1000b877  *(arg3 + 0x1304) = sub_1000b890",
		"1000bb9e      eax_5, ecx = sub_1000b990(arg4)",
		'1000c018          sub_1000b450("activate entity: intermission", sub_1001cbb0(arg1), arg1)',
		'1000c0c6          sub_1000c640(arg1, "activate entity: no goal")',
		"1000c3cb          int32_t ecx_31 = sub_1000bab0(eax_21, edx_8, &esp_1[0x22])",
		'1000c640    int32_t sub_1000c640(void* arg1 @ esi, int32_t arg2 @ edi)',
		'1000c6a7  int32_t result = sub_10008460(arg1, "seek NBG", var_e4_2, var_e0_1)',
	):
		assert expected in hlil


def test_qagame_ai_dmnet_goal_botlib_import_wiring_is_pinned() -> None:
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)
	ai_dmnet = _read(GAME_AI_DMNET)

	for expected in (
		"BOTLIB_AI_RESET_AVOID_GOALS,",
		"BOTLIB_AI_PUSH_GOAL,",
		"BOTLIB_AI_POP_GOAL,",
		"BOTLIB_AI_GET_TOP_GOAL,",
		"BOTLIB_AI_CHOOSE_LTG_ITEM,",
		"BOTLIB_AI_CHOOSE_NBG_ITEM,",
		"BOTLIB_AI_AVOID_GOAL_TIME,",
		"BOTLIB_AI_RESET_AVOID_REACH,",
		"G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_GOALS = 139,",
		"G_QL_IMPORT_BOTLIB_AI_PUSH_GOAL = 140,",
		"G_QL_IMPORT_BOTLIB_AI_POP_GOAL = 141,",
		"G_QL_IMPORT_BOTLIB_AI_GET_TOP_GOAL = 146,",
		"G_QL_IMPORT_BOTLIB_AI_CHOOSE_LTG_ITEM = 148,",
		"G_QL_IMPORT_BOTLIB_AI_CHOOSE_NBG_ITEM = 149,",
		"G_QL_IMPORT_BOTLIB_AI_AVOID_GOAL_TIME = 155,",
		"G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_REACH = 169,",
	):
		assert expected in game_public

	for expected in (
		"case BOTLIB_AI_RESET_AVOID_GOALS: return G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_GOALS;",
		"case BOTLIB_AI_PUSH_GOAL: return G_QL_IMPORT_BOTLIB_AI_PUSH_GOAL;",
		"case BOTLIB_AI_POP_GOAL: return G_QL_IMPORT_BOTLIB_AI_POP_GOAL;",
		"case BOTLIB_AI_GET_TOP_GOAL: return G_QL_IMPORT_BOTLIB_AI_GET_TOP_GOAL;",
		"case BOTLIB_AI_CHOOSE_LTG_ITEM: return G_QL_IMPORT_BOTLIB_AI_CHOOSE_LTG_ITEM;",
		"case BOTLIB_AI_CHOOSE_NBG_ITEM: return G_QL_IMPORT_BOTLIB_AI_CHOOSE_NBG_ITEM;",
		"case BOTLIB_AI_AVOID_GOAL_TIME: return G_QL_IMPORT_BOTLIB_AI_AVOID_GOAL_TIME;",
		"case BOTLIB_AI_RESET_AVOID_REACH: return G_QL_IMPORT_BOTLIB_AI_RESET_AVOID_REACH;",
		"return syscall( BOTLIB_AI_CHOOSE_NBG_ITEM, goalstate, origin, inventory, travelflags, ltg, PASSFLOAT(maxtime) );",
	):
		assert expected in game_syscalls

	for expected in (
		"[BOTLIB_AI_RESET_AVOID_GOALS] = (ql_import_f)QL_G_trap_BotResetAvoidGoals,",
		"[BOTLIB_AI_PUSH_GOAL] = (ql_import_f)QL_G_trap_BotPushGoal,",
		"[BOTLIB_AI_POP_GOAL] = (ql_import_f)QL_G_trap_BotPopGoal,",
		"[BOTLIB_AI_GET_TOP_GOAL] = (ql_import_f)QL_G_trap_BotGetTopGoal,",
		"[BOTLIB_AI_CHOOSE_LTG_ITEM] = (ql_import_f)QL_G_trap_BotChooseLTGItem,",
		"[BOTLIB_AI_CHOOSE_NBG_ITEM] = (ql_import_f)QL_G_trap_BotChooseNBGItem,",
		"[BOTLIB_AI_AVOID_GOAL_TIME] = (ql_import_f)QL_G_trap_BotAvoidGoalTime,",
		"[BOTLIB_AI_RESET_AVOID_REACH] = (ql_import_f)QL_G_trap_BotResetAvoidReach,",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHOOSE_NBG_ITEM] = (ql_import_f)QL_G_trap_BotChooseNBGItem;",
	):
		assert expected in server_game

	for expected in (
		"static void QDECL QL_G_trap_BotResetAvoidGoals( int goalstate )",
		"static void QDECL QL_G_trap_BotPushGoal( int goalstate, void /* struct bot_goal_s */ *goal )",
		"static void QDECL QL_G_trap_BotPopGoal( int goalstate )",
		"static int QDECL QL_G_trap_BotGetTopGoal( int goalstate, void /* struct bot_goal_s */ *goal )",
		"static int QDECL QL_G_trap_BotChooseLTGItem( int goalstate, vec3_t origin, int *inventory, int travelflags )",
		"static int QDECL QL_G_trap_BotChooseNBGItem( int goalstate, vec3_t origin, int *inventory, int travelflags, void /* struct bot_goal_s */ *ltg, float maxtime )",
		"return G_Import_Syscall( BOTLIB_AI_CHOOSE_NBG_ITEM, goalstate, origin, inventory, travelflags, ltg, QL_G_PASSFLOAT(maxtime) );",
		"static float QDECL QL_G_trap_BotAvoidGoalTime( int goalstate, int number )",
		"static void QDECL QL_G_trap_BotResetAvoidReach( int movestate )",
	):
		assert expected in ql_game_imports

	for expected in (
		"trap_BotPushGoal(bs->gs, &goal);",
		"trap_BotChooseNBGItem(bs->gs, bs->origin, bs->inventory, tfl, ltg, range)",
		"trap_BotGetTopGoal(bs->gs, &goal);",
		"trap_BotPopGoal(bs->gs);",
		"trap_BotResetAvoidGoals(bs->gs);",
		"trap_BotSetAvoidGoalTime(bs->gs, goal->number, -1);",
		"trap_BotChooseLTGItem(bs->gs, bs->origin, bs->inventory, tfl)",
		"trap_BotResetAvoidReach(bs->ms);",
	):
		assert expected in ai_dmnet
