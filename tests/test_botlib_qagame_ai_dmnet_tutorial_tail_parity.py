from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_AI_DMNET = REPO_ROOT / "src" / "code" / "game" / "ai_dmnet.c"
GAME_AI_DMQ3 = REPO_ROOT / "src" / "code" / "game" / "ai_dmq3.c"
GAME_AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
GAME_CMDS = REPO_ROOT / "src" / "code" / "game" / "g_cmds.c"
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


AI_DMNET_TUTORIAL_TAIL_FUNCTIONS = (
	("1000ecc0", "FUN_1000ecc0", "AIEnter_Seek_Teammate", "void AIEnter_Seek_Teammate(bot_state_t *bs)", 220),
	("1000eda0", "FUN_1000eda0", "AINode_Seek_Teammate", "int AINode_Seek_Teammate(bot_state_t *bs)", 2629),
	("1000f7f0", "FUN_1000f7f0", "BotSetLeadTeamGoal", "void BotSetLeadTeamGoal(bot_state_t *bs)", 129),
	("1000f880", "FUN_1000f880", "AIEnter_Lead_Teammate", "void AIEnter_Lead_Teammate(bot_state_t *bs)", 355),
	("1000fa00", "FUN_1000fa00", "AINode_Lead_Teammate", "int AINode_Lead_Teammate(bot_state_t *bs)", 7920),
	("10011900", "FUN_10011900", "AIEnter_Torment_Human", "void AIEnter_Torment_Human(bot_state_t *bs)", 110),
	("10011980", "FUN_10011980", "AINode_Torment_Human", "int AINode_Torment_Human(bot_state_t *bs)", 2733),
	("10012430", "FUN_10012430", "AIEnter_Lead_Teammate_FragBait", "void AIEnter_Lead_Teammate_FragBait(bot_state_t *bs)", 276),
	("10012560", "FUN_10012560", "AINode_Lead_Teammate_FragBait", "int AINode_Lead_Teammate_FragBait(bot_state_t *bs)", 3655),
	("100133c0", "FUN_100133c0", "AIEnter_InstaGib", "void AIEnter_InstaGib(bot_state_t *bs)", 65),
	("10013410", "FUN_10013410", "AINode_InstaGib", "int AINode_InstaGib(bot_state_t *bs)", 1711),
	("10013ac0", "FUN_10013ac0", "BotCTFCarryingFlag", "int BotCTFCarryingFlag(bot_state_t *bs)", 52),
	("10013b00", "FUN_10013b00", "BotTeam", "int BotTeam(bot_state_t *bs)", 209),
)


SOURCE_OWNED_HELPERS = {
	"BotCTFCarryingFlag": (
		GAME_AI_DMQ3,
		"int BotCTFCarryingFlag(bot_state_t *bs)",
		(
			"if (gametype != GT_CTF && gametype != GT_ATTACK_DEFEND) return CTF_FLAG_NONE;",
			"bs->inventory[INVENTORY_REDFLAG] > 0",
			"return CTF_FLAG_RED;",
			"bs->inventory[INVENTORY_BLUEFLAG] > 0",
			"return CTF_FLAG_BLUE;",
			"return CTF_FLAG_NONE;",
		),
	),
	"BotTeam": (
		GAME_AI_DMQ3,
		"int BotTeam(bot_state_t *bs)",
		(
			"if (bs->client < 0 || bs->client >= MAX_CLIENTS)",
			"trap_GetConfigstring(CS_PLAYERS+bs->client, info, sizeof(info));",
			"Info_ValueForKey(info, PLAYER_INFO_KEY_TEAM)",
			"return TEAM_RED;",
			"return TEAM_BLUE;",
			"return TEAM_FREE;",
		),
	),
}


HLIL_ENTRY_ANCHORS = (
	'1000ecc0    int32_t __fastcall sub_1000ecc0(int32_t arg1, void* arg2 @ esi)',
	"1000eda0    int32_t sub_1000eda0(int32_t* arg1)",
	'1000f7f0    void __convention("regparm") sub_1000f7f0(void* arg1)',
	"1000f880    int32_t sub_1000f880(void* arg1 @ esi)",
	"1000fa00    int32_t sub_1000fa00(void* arg1, float arg2, char arg3, int32_t arg4, float arg5, float arg6, int32_t arg7, float arg8, float arg9, float arg10, float arg11, float arg12, float arg13, char arg14, int32_t arg15, int32_t arg16, int32_t arg17, int32_t arg18, int32_t arg19, float arg20, float arg21, float arg22, float arg23, float arg24, float arg25, float arg26, float arg27, int32_t arg28, int32_t arg29, float arg30, int32_t arg31)",
	'10011900    int32_t __convention("regparm") sub_10011900(void* arg1)',
	"10011980    int32_t sub_10011980(int32_t* arg1)",
	'10012430    int32_t __convention("regparm") sub_10012430(void* arg1)',
	"10012560    int32_t sub_10012560(int32_t* arg1)",
	'100133c0    int32_t __convention("regparm") sub_100133c0(void* arg1)',
	"10013410    int32_t sub_10013410(int32_t* arg1)",
	'10013ac0    int32_t __convention("regparm") sub_10013ac0(void* arg1)',
	"10013b00    int32_t sub_10013b00(void* arg1)",
)


HLIL_CALL_ANCHORS = (
	'1000ed9b  return sub_10008460(arg2, "seek teammate", &data_1007c414, &data_1007c414)',
	'1000efe1      (*(eax_25 + 0x3c))("bot_followMe", &data_1007d0a8)',
	'1000f910  *(arg1 + 0x1304) = sub_1000fa00',
	'100118da          sub_1000ecc0((*(data_104b13ac + 0x3c))("bot_followMe", &data_1007d1d8), esi)',
	'1001196d  return sub_10008460(arg1, "torment human", &data_1007c414, &data_1007c414)',
	'100124af  *(arg1 + 0x1304) = sub_10012560',
	"say Well done! Let's get back to",
	"say Kill me if you can - fragbai",
	'100133ed  *(arg1 + 0x1304) = sub_10013410',
	'10013601      sub_1000d250("insta gib!: found enemy", arg1)',
	"10013ace  if (ecx_1 != 5 && ecx_1 != 0xb)",
	"10013b4a  (*(data_104b13ac + 0x68))(eax_3 + 0x211, &var_404, 0x400)",
)


GHIDRA_DECOMPILE_ANCHORS = (
	'FUN_10008460(param_1,"observer",&DAT_1007c414,"seek teammate: observer");',
	'FUN_1000cb30(param_1,"seek teammate: no ai node");',
	'FUN_1000cb30(param_1,"seek teammate: no client");',
	'FUN_10008460(param_1,"observer",&DAT_1007c414,"lead teammate: observer");',
	'FUN_1000cb30(param_1,"lead teammate: no ai node");',
	'FUN_1000cb30(param_1,"lead teammate: no client");',
	'FUN_10008460(param_1,"observer",&DAT_1007c414,"torment human: observer");',
	'FUN_1000cb30(param_1,"torment human: no ai node");',
	'FUN_10008460(param_1,"observer",&DAT_1007c414,"insta gib!: observer");',
	'FUN_1000cb30(param_1,"insta gib!: no ai node");',
	"say Well done! Let\\'s get back to the tutorial. Follow me.",
	"say Kill me if you can - fragbait!",
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


def test_qagame_ai_dmnet_tutorial_tail_aliases_hlil_and_ghidra_are_pinned() -> None:
	hlil = _read(QAGAME_HLIL_PART01)
	decompile_top = _read(QAGAME_DECOMPILE_TOP)
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}

	for address, raw_name, normalized_name, signature, size in AI_DMNET_TUTORIAL_TAIL_FUNCTIONS:
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

	for expected in HLIL_ENTRY_ANCHORS:
		assert expected in hlil

	for expected in HLIL_CALL_ANCHORS:
		assert expected in hlil

	for expected in GHIDRA_DECOMPILE_ANCHORS:
		assert expected in decompile_top


def test_qagame_ai_dmnet_tutorial_tail_source_owned_helpers_are_pinned() -> None:
	for normalized_name, (path, signature, anchors) in SOURCE_OWNED_HELPERS.items():
		block = _extract_function_block(_read(path), signature)
		for anchor in anchors:
			assert anchor in block


def test_qagame_ai_dmnet_tutorial_tail_training_and_import_wiring_is_pinned() -> None:
	ai_main = _read(GAME_AI_MAIN)
	g_cmds = _read(GAME_CMDS)
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)

	for expected in (
		'BotSetTrainingCvarIfChanged( "g_training", "1" );',
		'BotSetTrainingCvarIfChanged( "bot_followDist", "125" );',
		'BotSetTrainingCvarIfChanged( "bot_dynamicSkill", "1" );',
		'BotSetTrainingCvarIfChanged( "bot_itemDelayTime", "10" );',
		'BotSetTrainingCvarIfChanged( "bot_startingSkill", "1" );',
		'BotSetTrainingCvarIfChanged( "bot_followMe", "1" );',
		'BotSetTrainingCvarIfChanged( "bot_training", "0" );',
		'BotSetTrainingCvarIfChanged( "bot_followMe", "0" );',
	):
		assert expected in ai_main

	for expected in (
		'trap_Cvar_Set( "g_training", "1" );',
		'trap_Cvar_Set( "bot_training", "0" );',
		'trap_Cvar_Set( "bot_dynamicSkill", "1" );',
		'trap_Cvar_Set( "bot_followMe", "0" );',
		'trap_Cvar_Set( "g_skipTrainingEnable", "0" );',
	):
		assert expected in g_cmds

	for expected in (
		"BOTLIB_AAS_POINT_AREA_NUM,",
		"BOTLIB_AAS_AREA_REACHABILITY,",
		"BOTLIB_EA_COMMAND,",
		"BOTLIB_EA_GESTURE,",
		"BOTLIB_AI_MOVE_TO_GOAL,",
		"BOTLIB_AI_MOVEMENT_VIEW_TARGET,",
		"G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM = 67,",
		"G_QL_IMPORT_BOTLIB_AAS_AREA_REACHABILITY = 76,",
		"G_QL_IMPORT_BOTLIB_EA_COMMAND = 87,",
		"G_QL_IMPORT_BOTLIB_EA_GESTURE = 90,",
		"G_QL_IMPORT_BOTLIB_AI_MOVE_TO_GOAL = 167,",
		"G_QL_IMPORT_BOTLIB_AI_MOVEMENT_VIEW_TARGET = 172,",
	):
		assert expected in game_public

	for expected in (
		"case BOTLIB_AAS_POINT_AREA_NUM: return G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM;",
		"case BOTLIB_AAS_AREA_REACHABILITY: return G_QL_IMPORT_BOTLIB_AAS_AREA_REACHABILITY;",
		"case BOTLIB_EA_COMMAND: return G_QL_IMPORT_BOTLIB_EA_COMMAND;",
		"case BOTLIB_EA_GESTURE: return G_QL_IMPORT_BOTLIB_EA_GESTURE;",
		"case BOTLIB_AI_MOVE_TO_GOAL: return G_QL_IMPORT_BOTLIB_AI_MOVE_TO_GOAL;",
		"case BOTLIB_AI_MOVEMENT_VIEW_TARGET: return G_QL_IMPORT_BOTLIB_AI_MOVEMENT_VIEW_TARGET;",
		"return syscall( BOTLIB_AAS_POINT_AREA_NUM, point );",
		"return syscall( BOTLIB_AAS_AREA_REACHABILITY, areanum );",
		"syscall( BOTLIB_EA_COMMAND, client, command );",
		"syscall( BOTLIB_EA_GESTURE, client );",
		"syscall( BOTLIB_AI_MOVE_TO_GOAL, result, movestate, goal, travelflags );",
		"return syscall( BOTLIB_AI_MOVEMENT_VIEW_TARGET, movestate, goal, travelflags, PASSFLOAT(lookahead), target );",
	):
		assert expected in game_syscalls

	for expected in (
		"[BOTLIB_AAS_POINT_AREA_NUM] = (ql_import_f)QL_G_trap_AAS_PointAreaNum,",
		"[BOTLIB_AAS_AREA_REACHABILITY] = (ql_import_f)QL_G_trap_AAS_AreaReachability,",
		"[BOTLIB_EA_COMMAND] = (ql_import_f)QL_G_trap_EA_Command,",
		"[BOTLIB_EA_GESTURE] = (ql_import_f)QL_G_trap_EA_Gesture,",
		"[BOTLIB_AI_MOVE_TO_GOAL] = (ql_import_f)QL_G_trap_BotMoveToGoal,",
		"[BOTLIB_AI_MOVEMENT_VIEW_TARGET] = (ql_import_f)QL_G_trap_BotMovementViewTarget,",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM] = (ql_import_f)QL_G_trap_AAS_PointAreaNum;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_AREA_REACHABILITY] = (ql_import_f)QL_G_trap_AAS_AreaReachability;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_EA_COMMAND] = (ql_import_f)QL_G_trap_EA_Command;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_EA_GESTURE] = (ql_import_f)QL_G_trap_EA_Gesture;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVE_TO_GOAL] = (ql_import_f)QL_G_trap_BotMoveToGoal;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVEMENT_VIEW_TARGET] = (ql_import_f)QL_G_trap_BotMovementViewTarget;",
	):
		assert expected in server_game

	for expected in (
		"static int QDECL QL_G_trap_AAS_PointAreaNum( vec3_t point )",
		"static int QDECL QL_G_trap_AAS_AreaReachability( int areanum )",
		"static void QDECL QL_G_trap_EA_Command( int client, char *command )",
		"static void QDECL QL_G_trap_EA_Gesture( int client )",
		"static void QDECL QL_G_trap_BotMoveToGoal( void /* struct bot_moveresult_s */ *result, int movestate, void /* struct bot_goal_s */ *goal, int travelflags )",
		"static int QDECL QL_G_trap_BotMovementViewTarget( int movestate, void /* struct bot_goal_s */ *goal, int travelflags, float lookahead, vec3_t target )",
		"return G_Import_Syscall( BOTLIB_AAS_POINT_AREA_NUM, point );",
		"return G_Import_Syscall( BOTLIB_AAS_AREA_REACHABILITY, areanum );",
		"G_Import_Syscall( BOTLIB_EA_COMMAND, client, command );",
		"G_Import_Syscall( BOTLIB_EA_GESTURE, client );",
		"G_Import_Syscall( BOTLIB_AI_MOVE_TO_GOAL, result, movestate, goal, travelflags );",
		"return G_Import_Syscall( BOTLIB_AI_MOVEMENT_VIEW_TARGET, movestate, goal, travelflags, QL_G_PASSFLOAT(lookahead), target );",
	):
		assert expected in ql_game_imports
