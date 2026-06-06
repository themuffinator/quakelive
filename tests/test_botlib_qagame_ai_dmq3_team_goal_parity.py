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


AI_DMQ3_TEAM_GOAL_FUNCTIONS = (
	("10013be0", "FUN_10013be0", "BotOppositeTeam", "int BotOppositeTeam(bot_state_t *bs)", 30),
	("10013c00", "FUN_10013c00", "EntityIsDead", "int EntityIsDead(aas_entityinfo_t *entinfo)", 95),
	("10013c60", "FUN_10013c60", "EntityCarriesFlag", "int EntityCarriesFlag(aas_entityinfo_t *entinfo)", 27),
	("10013c80", "FUN_10013c80", "EntityCarriesCubes", "int EntityCarriesCubes(aas_entityinfo_t *entinfo)", 125),
	("10013d00", "FUN_10013d00", "Bot1FCTFCarryingFlag", "int Bot1FCTFCarryingFlag(bot_state_t *bs)", 21),
	("10013d20", "FUN_10013d20", "BotHarvesterCarryingCubes", "int BotHarvesterCarryingCubes(bot_state_t *bs)", 41),
	("10013d50", "FUN_10013d50", "BotRememberLastOrderedTask", "void BotRememberLastOrderedTask(bot_state_t *bs)", 69),
	("10013da0", "FUN_10013da0", "BotSetTeamStatus", "void BotSetTeamStatus(bot_state_t *bs)", 95),
	("10013e20", "FUN_10013e20", "BotSetLastOrderedTask", "int BotSetLastOrderedTask(bot_state_t *bs)", 473),
	("10014020", "FUN_10014020", "BotRefuseOrder", "void BotRefuseOrder(bot_state_t *bs)", 120),
	("100140a0", "FUN_100140a0", "BotCTFSeekGoals", "void BotCTFSeekGoals(bot_state_t *bs)", 2187),
	("10014930", "FUN_10014930", "BotCTFRetreatGoals", "void BotCTFRetreatGoals(bot_state_t *bs)", 130),
	("100149c0", "FUN_100149c0", "Bot1FCTFSeekGoals", "void Bot1FCTFSeekGoals(bot_state_t *bs)", 1584),
	("10015010", "FUN_10015010", "Bot1FCTFRetreatGoals", "void Bot1FCTFRetreatGoals(bot_state_t *bs)", 244),
	("10015120", "FUN_10015120", "BotObeliskSeekGoals", "void BotObeliskSeekGoals(bot_state_t *bs)", 722),
	("10015400", "FUN_10015400", "BotGoHarvest", "void BotGoHarvest(bot_state_t *bs)", 104),
	("10015470", "FUN_10015470", "BotHarvesterSeekGoals", "void BotHarvesterSeekGoals(bot_state_t *bs)", 1104),
	("100158e0", "FUN_100158e0", "BotHarvesterRetreatGoals", "void BotHarvesterRetreatGoals(bot_state_t *bs)", 124),
	("10015960", "FUN_10015960", "BotTeamGoals", "void BotTeamGoals(bot_state_t *bs, int retreat)", 219),
)


SOURCE_HELPERS = {
	"BotOppositeTeam": (
		"int BotOppositeTeam(bot_state_t *bs)",
		(
			"switch(BotTeam(bs))",
			"case TEAM_RED: return TEAM_BLUE;",
			"case TEAM_BLUE: return TEAM_RED;",
			"default: return TEAM_FREE;",
		),
	),
	"EntityIsDead": (
		"qboolean EntityIsDead(aas_entityinfo_t *entinfo)",
		(
			"entinfo->number >= 0 && entinfo->number < MAX_CLIENTS",
			"BotAI_GetClientState( entinfo->number, &ps );",
			"if (ps.pm_type != PM_NORMAL) return qtrue;",
		),
	),
	"EntityCarriesFlag": (
		"qboolean EntityCarriesFlag(aas_entityinfo_t *entinfo)",
		(
			"( 1 << PW_REDFLAG )",
			"( 1 << PW_BLUEFLAG )",
			"( 1 << PW_NEUTRALFLAG )",
			"return qfalse;",
		),
	),
	"EntityCarriesCubes": (
		"qboolean EntityCarriesCubes(aas_entityinfo_t *entinfo)",
		(
			"if (gametype != GT_HARVESTER)",
			"BotAI_GetEntityState(entinfo->number, &state);",
			"if (state.generic1 > 0)",
		),
	),
	"Bot1FCTFCarryingFlag": (
		"int Bot1FCTFCarryingFlag(bot_state_t *bs)",
		(
			"if (gametype != GT_1FCTF) return qfalse;",
			"bs->inventory[INVENTORY_NEUTRALFLAG] > 0",
		),
	),
	"BotHarvesterCarryingCubes": (
		"int BotHarvesterCarryingCubes(bot_state_t *bs)",
		(
			"if (gametype != GT_HARVESTER) return qfalse;",
			"bs->inventory[INVENTORY_REDCUBE] > 0",
			"bs->inventory[INVENTORY_BLUECUBE] > 0",
		),
	),
	"BotRememberLastOrderedTask": (
		"void BotRememberLastOrderedTask(bot_state_t *bs)",
		(
			"if (!bs->ordered)",
			"bs->lastgoal_decisionmaker = bs->decisionmaker;",
			"bs->lastgoal_ltgtype = bs->ltgtype;",
			"memcpy(&bs->lastgoal_teamgoal, &bs->teamgoal, sizeof(bot_goal_t));",
			"bs->lastgoal_teammate = bs->teammate;",
		),
	),
	"BotSetTeamStatus": (
		"void BotSetTeamStatus(bot_state_t *bs)",
		(
			"teamtask = TEAMTASK_PATROL;",
			"case LTG_TEAMACCOMPANY:",
			"EntityCarriesFlag(&entinfo))",
			"EntityCarriesCubes(&entinfo))",
			"case LTG_HARVEST:",
			"case LTG_ATTACKENEMYBASE:",
			'BotSetUserInfo(bs, "teamtask", va("%d", teamtask));',
		),
	),
	"BotSetLastOrderedTask": (
		"int BotSetLastOrderedTask(bot_state_t *bs)",
		(
			"if (gametype == GT_CTF)",
			"bs->lastgoal_ltgtype == LTG_RETURNFLAG",
			"bs->teamgoal_time = FloatTime() + 300;",
			"trap_AAS_AreaTravelTimeToGoalArea(bs->areanum, bs->origin, tb->areanum, TFL_DEFAULT);",
			"trap_AAS_AreaTravelTimeToGoalArea(bs->areanum, bs->origin, eb->areanum, TFL_DEFAULT);",
			"BotGetAlternateRouteGoal(bs, BotOppositeTeam(bs));",
		),
	),
	"BotRefuseOrder": (
		"void BotRefuseOrder(bot_state_t *bs)",
		(
			"if (!bs->ordered)",
			"bs->order_time && bs->order_time > FloatTime() - 10",
			"trap_EA_Action(bs->client, ACTION_NEGATIVE);",
			"BotVoiceChat(bs, bs->decisionmaker, VOICECHAT_NO);",
			"bs->order_time = 0;",
		),
	),
	"BotCTFSeekGoals": (
		"void BotCTFSeekGoals(bot_state_t *bs)",
		(
			"if (BotCTFCarryingFlag(bs))",
			"bs->ltgtype = LTG_RUSHBASE;",
			"VectorLength(dir) < 128",
			"VOICECHAT_IHAVEFLAG",
			"flagstatus == 1",
			"flagstatus == 2",
			"flagstatus == 3",
			"BotTeamLeader(bs)",
			"BotSetLastOrderedTask(bs)",
			"BotAggression(bs) < 50",
			"TEAMTP_ATTACKER|TEAMTP_DEFENDER",
			"bs->ltgtype = LTG_GETFLAG;",
			"bs->ltgtype = LTG_DEFENDKEYAREA;",
		),
	),
	"BotCTFRetreatGoals": (
		"void BotCTFRetreatGoals(bot_state_t *bs)",
		(
			"if (BotCTFCarryingFlag(bs))",
			"bs->ltgtype != LTG_RUSHBASE",
			"bs->ltgtype = LTG_RUSHBASE;",
			"BotSetTeamStatus(bs);",
		),
	),
	"Bot1FCTFSeekGoals": (
		"void Bot1FCTFSeekGoals(bot_state_t *bs)",
		(
			"if (Bot1FCTFCarryingFlag(bs))",
			"BotGetAlternateRouteGoal(bs, BotOppositeTeam(bs));",
			"bs->neutralflagstatus == 1",
			"bs->neutralflagstatus == 2",
			"BotTeamFlagCarrierVisible(bs)",
			"LTG_ATTACKENEMYBASE",
			"ctf_neutralflag.areanum",
		),
	),
	"Bot1FCTFRetreatGoals": (
		"void Bot1FCTFRetreatGoals(bot_state_t *bs)",
		(
			"if (Bot1FCTFCarryingFlag(bs))",
			"bs->ltgtype = LTG_RUSHBASE;",
			"BotGetAlternateRouteGoal(bs, BotOppositeTeam(bs));",
			"BotSetTeamStatus(bs);",
		),
	),
	"BotObeliskSeekGoals": (
		"void BotObeliskSeekGoals(bot_state_t *bs)",
		(
			"if (BotTeamLeader(bs))",
			"BotSetLastOrderedTask(bs)",
			"redobelisk.areanum && blueobelisk.areanum",
			"LTG_ATTACKENEMYBASE",
			"LTG_DEFENDKEYAREA",
			"BotGetAlternateRouteGoal(bs, BotOppositeTeam(bs));",
		),
	),
	"BotGoHarvest": (
		"void BotGoHarvest(bot_state_t *bs)",
		(
			"bs->ltgtype = LTG_HARVEST;",
			"bs->teamgoal_time = FloatTime() + TEAM_HARVEST_TIME;",
			"bs->harvestaway_time = 0;",
			"BotSetTeamStatus(bs);",
		),
	),
	"BotHarvesterSeekGoals": (
		"void BotHarvesterSeekGoals(bot_state_t *bs)",
		(
			"if (BotHarvesterCarryingCubes(bs))",
			"BotGetAlternateRouteGoal(bs, BotOppositeTeam(bs));",
			"EntityCarriesCubes(&entinfo)",
			"BotEnemyCubeCarrierVisible(bs)",
			"BotTeamCubeCarrierVisible(bs)",
			"TEAMTP_ATTACKER|TEAMTP_DEFENDER",
			"BotGoHarvest(bs);",
			"bs->ltgtype = LTG_DEFENDKEYAREA;",
		),
	),
	"BotHarvesterRetreatGoals": (
		"void BotHarvesterRetreatGoals(bot_state_t *bs)",
		(
			"if (BotHarvesterCarryingCubes(bs))",
			"bs->ltgtype != LTG_RUSHBASE",
			"bs->ltgtype = LTG_RUSHBASE;",
			"BotSetTeamStatus(bs);",
		),
	),
	"BotTeamGoals": (
		"void BotTeamGoals(bot_state_t *bs, int retreat)",
		(
			"if ( retreat )",
			"BotCTFRetreatGoals(bs);",
			"Bot1FCTFRetreatGoals(bs);",
			"BotObeliskRetreatGoals(bs);",
			"BotHarvesterRetreatGoals(bs);",
			"BotCTFSeekGoals(bs);",
			"Bot1FCTFSeekGoals(bs);",
			"BotObeliskSeekGoals(bs);",
			"BotHarvesterSeekGoals(bs);",
			"bs->order_time = 0;",
		),
	),
}


HLIL_ENTRY_ANCHORS = (
	'10013be0    int32_t __convention("regparm") sub_10013be0(void* arg1)',
	'10013c00    int32_t __convention("regparm") sub_10013c00(void* arg1)',
	'10013c60    uint32_t __convention("regparm") sub_10013c60(void* arg1)',
	"10013c80    int32_t sub_10013c80(void* arg1)",
	"10013d00    int32_t __fastcall sub_10013d00(void* arg1)",
	'10013d20    int32_t __convention("regparm") sub_10013d20(void* arg1)',
	'10013d50    void __convention("regparm") sub_10013d50(void* arg1)',
	"10013da0    uint32_t __fastcall sub_10013da0(void* arg1)",
	"10013e20    int32_t sub_10013e20()",
	'10014020    void __convention("regparm") sub_10014020(void* arg1)',
	"100140a0    int32_t __fastcall sub_100140a0(void* arg1)",
	"10014930    int32_t __fastcall sub_10014930(int32_t arg1, void* arg2 @ esi)",
	"100149c0    int32_t __fastcall sub_100149c0(void* arg1)",
	"10015010    int32_t __fastcall sub_10015010(void* arg1)",
	'10015120    void __convention("regparm") sub_10015120(void* arg1)',
	"10015400    int32_t __fastcall sub_10015400(int32_t arg1)",
	"10015470    uint32_t sub_10015470(void* arg1)",
	"100158e0    int32_t __fastcall sub_100158e0(int32_t arg1, void* arg2 @ esi)",
	'10015960    int32_t __convention("regparm") sub_10015960(void* arg1, int32_t arg2)',
)


HLIL_FLOW_ANCHORS = (
	"10013be1  int32_t eax = sub_10013b00(arg1)",
	"10013c44      if (var_250 != 0)",
	"10013c60  char eax_4 = (*(arg1 + 0x7c)).b",
	"10013c95  if (data_105e4ae8 != 8)",
	"10013d09  if (data_105e4ae8 == 6)",
	"10013d27  if (data_105e4ae8 != 8)",
	"10013d57  if (*(arg1 + 0x19b4) != 0)",
	"10013dba  uint32_t result = *(arg1 + 0x19a8) - 1",
	"10013e4a  if ((eax_2 == 5 || eax_2 == 0xb) && *(ebx + 0x1a58) == 6)",
	"10013f18  if ((eax_6 == 5 || eax_6 == 0xb) && *(ebx + 0x19a8) == 4)",
	'10014336              char const* const var_128_4 = "ihaveflag"',
	'10014340              int32_t eax_12 = sub_10070cb0("vsay_team %s")',
	"10014650                      st0 = sub_10014020(arg1)",
	"10014761                          result = sub_10013e20()",
	"10014967      sub_10014020(arg2)",
	"10014e2a                      result = sub_10013e20()",
	"10015050      sub_10014020(arg1)",
	"100151d5              && eax_3 != 0xf && sub_10013e20() == 0",
	"10015338              sub_1001ed30(arg1, sub_10013be0(arg1))",
	"100155c4              int32_t eax_12 = sub_10013c80(&var_1e8)",
	"1001565c              result = sub_10013e20()",
	"1001580f                              result = sub_10015400(ecx_6)",
	"100159b9          int32_t eax_3 = sub_10014930(ecx, arg1)",
	"10015981          int32_t eax_1 = sub_10015010(arg1)",
	"100159a6          int32_t eax_2 = sub_100158e0(ecx, arg1)",
	"10015a28      eax = sub_100140a0(arg1)",
	"100159dd          int32_t eax_4 = sub_100149c0(arg1)",
	"100159f7          st0, eax_6 = sub_10015120(arg1)",
	"10015a10          uint32_t eax_7 = sub_10015470(arg1)",
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


def test_qagame_ai_dmq3_team_goal_aliases_source_and_hlil_are_pinned() -> None:
	source = _read(GAME_AI_DMQ3)
	hlil = _read(QAGAME_HLIL_PART01)
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}

	for address, raw_name, normalized_name, signature, size in AI_DMQ3_TEAM_GOAL_FUNCTIONS:
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


def test_qagame_ai_dmq3_team_goal_botlib_import_wiring_is_pinned() -> None:
	ai_dmq3 = _read(GAME_AI_DMQ3)
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)

	for expected in (
		"BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA,",
		"BOTLIB_EA_ACTION,",
		"G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA = 77,",
		"G_QL_IMPORT_BOTLIB_EA_ACTION = 88,",
	):
		assert expected in game_public

	for expected in (
		"case BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA: return G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA;",
		"case BOTLIB_EA_ACTION: return G_QL_IMPORT_BOTLIB_EA_ACTION;",
		"return syscall( BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA, areanum, origin, goalareanum, travelflags );",
		"syscall( BOTLIB_EA_ACTION, client, action );",
	):
		assert expected in game_syscalls

	for expected in (
		"case BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA:",
		"case BOTLIB_EA_ACTION:",
		"[BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA] = (ql_import_f)QL_G_trap_AAS_AreaTravelTimeToGoalArea,",
		"[BOTLIB_EA_ACTION] = (ql_import_f)QL_G_trap_EA_Action,",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA] = (ql_import_f)QL_G_trap_AAS_AreaTravelTimeToGoalArea;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_EA_ACTION] = (ql_import_f)QL_G_trap_EA_Action;",
	):
		assert expected in server_game

	for expected in (
		"static int QDECL QL_G_trap_AAS_AreaTravelTimeToGoalArea( int areanum, vec3_t origin, int goalareanum, int travelflags )",
		"return G_Import_Syscall( BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA, areanum, origin, goalareanum, travelflags );",
		"static void QDECL QL_G_trap_EA_Action( int client, int action )",
		"G_Import_Syscall( BOTLIB_EA_ACTION, client, action );",
	):
		assert expected in ql_game_imports

	for expected in (
		"trap_AAS_AreaTravelTimeToGoalArea(bs->areanum, bs->origin, tb->areanum, TFL_DEFAULT);",
		"trap_AAS_AreaTravelTimeToGoalArea(bs->areanum, bs->origin, eb->areanum, TFL_DEFAULT);",
		"trap_EA_Action(bs->client, ACTION_NEGATIVE);",
		"BotVoiceChat(bs, bs->decisionmaker, VOICECHAT_NO);",
		"BotGetAlternateRouteGoal(bs, BotOppositeTeam(bs));",
	):
		assert expected in ai_dmq3
