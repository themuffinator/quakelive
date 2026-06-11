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


AI_DMQ3_AIM_ATTACK_FUNCTIONS = (
	("10019e00", "FUN_10019e00", "BotAimAtEnemy", "void BotAimAtEnemy(bot_state_t *bs)", 5112),
	("1001b200", "FUN_1001b200", "BotCheckAttack", "void BotCheckAttack(bot_state_t *bs)", 1410),
	("1001b790", "FUN_1001b790", "BotMapScripts", "void BotMapScripts(bot_state_t *bs)", 855),
	("1001baf0", "FUN_1001baf0", "BotSetMovedir", "void BotSetMovedir(vec3_t angles, vec3_t movedir)", 237),
	("1001bbe0", "FUN_1001bbe0", "BotModelMinsMaxs", "int BotModelMinsMaxs(int modelindex, int eType, int contents, vec3_t mins, vec3_t maxs)", 225),
)


SOURCE_HELPERS = {
	"BotAimAtEnemy": (
		"void BotAimAtEnemy(bot_state_t *bs)",
		(
			"if (bs->enemy < 0)",
			"bs->enemy == redobelisk.entitynum",
			"CHARACTERISTIC_AIM_SKILL",
			"CHARACTERISTIC_AIM_ACCURACY_RAILGUN",
			"trap_BotGetWeaponInfo(bs->ws, bs->weaponnum, &wi);",
			"EntityIsInvisible(&entinfo)",
			"VectorScale(enemyvelocity, 1 / entinfo.update_time, enemyvelocity);",
			"BotEntityVisible(bs->entitynum, bs->eye, bs->viewangles, 360, bs->enemy);",
			"trap_AAS_PredictClientMovement(&move, bs->enemy, origin,",
			"trap_BotPredictVisiblePosition(bs->lastenemyorigin, bs->lastenemyareanum, &goal, TFL_DEFAULT, target)",
			"DAMAGETYPE_RADIAL",
			"trap_EA_View(bs->client, bs->viewangles);",
		),
	),
	"BotCheckAttack": (
		"void BotCheckAttack(bot_state_t *bs)",
		(
			"entinfo.number == redobelisk.entitynum",
			"CHARACTERISTIC_REACTIONTIME",
			"CHARACTERISTIC_FIRETHROTTLE",
			"if (!InFieldOfVision(bs->viewangles, fov, angles))",
			"BotAI_Trace(&bsptrace, bs->eye, NULL, NULL, bs->aimtarget, bs->client, CONTENTS_SOLID|CONTENTS_PLAYERCLIP);",
			"trap_BotGetWeaponInfo(bs->ws, bs->weaponnum, &wi);",
			"if (BotSameTeam(bs, trace.ent))",
			"wi.proj.damagetype & DAMAGETYPE_RADIAL",
			"wi.flags & WFL_FIRERELEASED",
			"bs->flags ^= BFL_ATTACKED;",
		),
	),
	"BotMapScripts": (
		"void BotMapScripts(bot_state_t *bs)",
		(
			"trap_GetServerinfo(info, sizeof(info));",
			"SERVERINFO_KEY_MAPNAME",
			'if (!Q_stricmp(mapname, "q3tourney6"))',
			"vec3_t buttonorg = {304, 352, 920};",
			"bs->tfl &= ~TFL_FUNCBOB;",
			"EntityIsDead(&entinfo)",
			"BotSameTeam(bs, i)",
			"CHARACTERISTIC_AIM_ACCURACY",
			"if (InFieldOfVision(bs->viewangles, 20, bs->ideal_viewangles))",
			"trap_EA_Attack(bs->client);",
			'else if (!Q_stricmp(mapname, "beyondreality"))',
			"BotApplyBeyondRealityTravelFlags(&bs->tfl);",
		),
	),
	"BotApplyBeyondRealityTravelFlags": (
		"void BotApplyBeyondRealityTravelFlags(int *travelFlags)",
		(
			"trap_GetServerinfo(info, sizeof(info));",
			"SERVERINFO_KEY_MAPNAME",
			'if (!Q_stricmp(mapname, "beyondreality"))',
			"*travelFlags &= ~TFL_FUNCBOB;",
		),
	),
	"BotSetMovedir": (
		"void BotSetMovedir(vec3_t angles, vec3_t movedir)",
		(
			"VectorCompare(angles, VEC_UP)",
			"VectorCopy(MOVEDIR_UP, movedir);",
			"VectorCompare(angles, VEC_DOWN)",
			"VectorCopy(MOVEDIR_DOWN, movedir);",
			"AngleVectors(angles, movedir, NULL, NULL);",
		),
	),
	"BotModelMinsMaxs": (
		"int BotModelMinsMaxs(int modelindex, int eType, int contents, vec3_t mins, vec3_t maxs)",
		(
			"ent = &g_entities[0];",
			"for (i = 0; i < level.num_entities; i++, ent++)",
			"if ( eType && ent->s.eType != eType)",
			"if ( contents && ent->r.contents != contents)",
			"if (ent->s.modelindex == modelindex)",
			"VectorAdd(ent->r.currentOrigin, ent->r.mins, mins);",
			"VectorAdd(ent->r.currentOrigin, ent->r.maxs, maxs);",
			"VectorClear(mins);",
		),
	),
}


HLIL_ENTRY_ANCHORS = (
	"10019e00    uint32_t sub_10019e00(long double arg1 @ st0, long double arg2 @ st1, void* arg3)",
	"1001b200    void* sub_1001b200(long double arg1 @ st0, void* arg2)",
	"1001b790    void sub_1001b790(long double arg1 @ st0, void* arg2)",
	'1001baf0    float* __convention("regparm") sub_1001baf0(int32_t* arg1, int32_t arg2, float* arg3)',
	"1001bbe0    int32_t sub_1001bbe0(int32_t* arg1 @ esi, int32_t arg2 @ edi, int32_t arg3, float* arg4)",
)


HLIL_FLOW_ANCHORS = (
	"10019e25  uint32_t result = *(arg3 + 0x196c)",
	"10019f66          (*(data_104b13ac + 0x1c4))(*(arg3 + 0x1958), 0x10, fconvert.s(float.t(0)),",
	"1001a02f              (*(data_104b13ac + 0x2cc))(*(arg3 + 0x1968), *(arg3 + 0x1980), &var_2a8)",
	"1001a46b                  st0_1, xmm0_12 = sub_10018b20()",
	"1001ae2b                          if ((*(eax_40 + 0x2b4))() != 0)",
	"1001b061                  sub_100702b0(&esp_1[0x10c], arg3 + 0x1990)",
	"1001b1d6                              result = edx_25()",
	"1001b365              result = (*(data_104b13ac + 0x1c4))(*(arg2 + 0x1958), 0x2f,",
	"1001b4a5              st0_1, result = sub_10018a00(&var_34, sub_100702b0(&var_3bc, &var_34),",
	"1001b51a                      (*(data_104b13ac + 0x2cc))(*(arg2 + 0x1968), *(arg2 + 0x1980),",
	"1001b6be                          result = sub_10018900(result, edx_6, var_360, arg2)",
	"1001b756                                  result = (*(data_104b13ac + 0x170))(*(arg2 + 8))",
	"1001b75b                              *(arg2 + 0x173c) ^= 2",
	'1001b803      sub_10070a40("q3tourney6", strncpy(&var_488, sub_10070cf0(), 0x7f), &var_488)',
	'1001bac2      if (sub_10070a40("beyondreality", edx_2, &var_488) == 0)',
	"1001b955                  *(arg2 + 0x173c) |= 0x20",
	"1001ba8d                  st0_1, eax_18 = sub_10018a00(arg2 + 0x1990, edx_6, arg2 + 0x1984,",
	"1001baa8                      (*(data_104b13ac + 0x170))(*(arg2 + 8))",
	"1001bb46              *edi = data_10090284",
	"1001bba9              *edi = data_1009029c",
	"1001bbdc  return sub_100706e0(arg3, edi, nullptr)",
	"1001bbf4  if (edx_1 s> 0)",
	"1001bc12          if (*(ecx + 0x240) != 0 && (ebx == 0 || *(ecx + 4) == ebx)",
	"1001bca0                  *arg4 =",
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


def test_qagame_ai_dmq3_aim_attack_aliases_source_and_hlil_are_pinned() -> None:
	source = _read(GAME_AI_DMQ3)
	hlil = _read(QAGAME_HLIL_PART01)
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}

	assert "mpq3tourney6" not in _extract_function_block(source, SOURCE_HELPERS["BotMapScripts"][0])

	for address, raw_name, normalized_name, signature, size in AI_DMQ3_AIM_ATTACK_FUNCTIONS:
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


def test_qagame_ai_dmq3_aim_attack_botlib_import_wiring_is_pinned() -> None:
	ai_dmq3 = _read(GAME_AI_DMQ3)
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)

	for expected in (
		"G_QL_IMPORT_BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT = 82,",
		"G_QL_IMPORT_BOTLIB_EA_ATTACK = 92,",
		"G_QL_IMPORT_BOTLIB_EA_VIEW = 106,",
		"G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT = 113,",
		"G_QL_IMPORT_BOTLIB_AI_PREDICT_VISIBLE_POSITION = 173,",
		"G_QL_IMPORT_BOTLIB_AI_GET_WEAPON_INFO = 179,",
	):
		assert expected in game_public

	for expected in (
		"case BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT: return G_QL_IMPORT_BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT;",
		"case BOTLIB_EA_ATTACK: return G_QL_IMPORT_BOTLIB_EA_ATTACK;",
		"case BOTLIB_EA_VIEW: return G_QL_IMPORT_BOTLIB_EA_VIEW;",
		"case BOTLIB_AI_CHARACTERISTIC_BFLOAT: return G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT;",
		"case BOTLIB_AI_PREDICT_VISIBLE_POSITION: return G_QL_IMPORT_BOTLIB_AI_PREDICT_VISIBLE_POSITION;",
		"case BOTLIB_AI_GET_WEAPON_INFO: return G_QL_IMPORT_BOTLIB_AI_GET_WEAPON_INFO;",
		"return syscall( BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT, move, entnum, origin, presencetype, onground, velocity, cmdmove, cmdframes, maxframes, PASSFLOAT(frametime), stopevent, stopareanum, visualize );",
		"syscall( BOTLIB_EA_ATTACK, client );",
		"syscall( BOTLIB_EA_VIEW, client, viewangles );",
		"temp = syscall( BOTLIB_AI_CHARACTERISTIC_BFLOAT, character, index, PASSFLOAT(min), PASSFLOAT(max) );",
		"return syscall( BOTLIB_AI_PREDICT_VISIBLE_POSITION, origin, areanum, goal, travelflags, target );",
		"syscall( BOTLIB_AI_GET_WEAPON_INFO, weaponstate, weapon, weaponinfo );",
	):
		assert expected in game_syscalls

	for expected in (
		"case BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT:",
		"case BOTLIB_EA_ATTACK:",
		"case BOTLIB_EA_VIEW:",
		"case BOTLIB_AI_CHARACTERISTIC_BFLOAT:",
		"case BOTLIB_AI_PREDICT_VISIBLE_POSITION:",
		"case BOTLIB_AI_GET_WEAPON_INFO:",
		"[BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT] = (ql_import_f)QL_G_trap_AAS_PredictClientMovement,",
		"[BOTLIB_EA_ATTACK] = (ql_import_f)QL_G_trap_EA_Attack,",
		"[BOTLIB_EA_VIEW] = (ql_import_f)QL_G_trap_EA_View,",
		"[BOTLIB_AI_CHARACTERISTIC_BFLOAT] = (ql_import_f)QL_G_trap_Characteristic_BFloat,",
		"[BOTLIB_AI_PREDICT_VISIBLE_POSITION] = (ql_import_f)QL_G_trap_BotPredictVisiblePosition,",
		"[BOTLIB_AI_GET_WEAPON_INFO] = (ql_import_f)QL_G_trap_BotGetWeaponInfo,",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT] = (ql_import_f)QL_G_trap_AAS_PredictClientMovement;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_EA_ATTACK] = (ql_import_f)QL_G_trap_EA_Attack;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_EA_VIEW] = (ql_import_f)QL_G_trap_EA_View;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT] = (ql_import_f)QL_G_trap_Characteristic_BFloat;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_PREDICT_VISIBLE_POSITION] = (ql_import_f)QL_G_trap_BotPredictVisiblePosition;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_WEAPON_INFO] = (ql_import_f)QL_G_trap_BotGetWeaponInfo;",
	):
		assert expected in server_game

	for expected in (
		"return G_Import_Syscall( BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT, move, entnum, origin, presencetype, onground, velocity, cmdmove, cmdframes, maxframes, QL_G_PASSFLOAT(frametime), stopevent, stopareanum, visualize );",
		"G_Import_Syscall( BOTLIB_EA_ATTACK, client );",
		"G_Import_Syscall( BOTLIB_EA_VIEW, client, viewangles );",
		"temp = G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_BFLOAT, character, index, QL_G_PASSFLOAT(min), QL_G_PASSFLOAT(max) );",
		"return G_Import_Syscall( BOTLIB_AI_PREDICT_VISIBLE_POSITION, origin, areanum, goal, travelflags, target );",
		"G_Import_Syscall( BOTLIB_AI_GET_WEAPON_INFO, weaponstate, weapon, weaponinfo );",
	):
		assert expected in ql_game_imports

	for expected in (
		"trap_BotGetWeaponInfo(bs->ws, bs->weaponnum, &wi);",
		"trap_AAS_PredictClientMovement(&move, bs->enemy, origin,",
		"trap_BotPredictVisiblePosition(bs->lastenemyorigin, bs->lastenemyareanum, &goal, TFL_DEFAULT, target)",
		"trap_EA_View(bs->client, bs->viewangles);",
		"trap_EA_Attack(bs->client);",
		"trap_Characteristic_BFloat(bs->character, CHARACTERISTIC_AIM_SKILL, 0, 1);",
		"trap_Characteristic_BFloat(bs->character, CHARACTERISTIC_FIRETHROTTLE, 0, 1);",
	):
		assert expected in ai_dmq3
