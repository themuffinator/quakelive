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


AI_DMQ3_SUPPORT_FUNCTIONS = (
	("10015a40", "FUN_10015a40", "BotPointAreaNum", "int BotPointAreaNum(vec3_t origin)", 129),
	("10015ad0", "FUN_10015ad0", "ClientName", "char *ClientName(int client, char *name, int size)", 167),
	("10015b80", "FUN_10015b80", "ClientFromName", "int ClientFromName(char *name)", 269),
	("10015c90", "FUN_10015c90", "ClientOnSameTeamFromName", "int ClientOnSameTeamFromName(bot_state_t *bs, char *name)", 235),
	("10015d80", "FUN_10015d80", "stristr", "char *stristr(char *str, char *charset)", 107),
	("10015df0", "FUN_10015df0", "EasyClientName", "char *EasyClientName(int client, char *buf, int size)", 219),
	("10015ed0", "FUN_10015ed0", "BotChooseWeapon", "void BotChooseWeapon(bot_state_t *bs)", 155),
	("10015f70", "FUN_10015f70", "BotSetupForMovement", "void BotSetupForMovement(bot_state_t *bs)", 330),
	("100160c0", "FUN_100160c0", "BotCheckItemPickup", "void BotCheckItemPickup(bot_state_t *bs, int *oldinventory)", 519),
	("100162d0", "FUN_100162d0", "BotNormalizeAmmoInventory", "void BotNormalizeAmmoInventory(bot_state_t *bs)", 163),
	("10016380", "FUN_10016380", "BotUpdateInventory", "void BotUpdateInventory(bot_state_t *bs)", 747),
	("10016670", "FUN_10016670", "BotUpdateBattleInventory", "void BotUpdateBattleInventory(bot_state_t *bs, int enemy)", 167),
	("10016720", "FUN_10016720", "BotUseKamikaze", "void BotUseKamikaze(bot_state_t *bs)", 1377),
	("10016c90", "FUN_10016c90", "BotUseInvulnerability", "void BotUseInvulnerability(bot_state_t *bs)", 862),
	("10016ff0", "FUN_10016ff0", "BotBattleUseItems", "void BotBattleUseItems(bot_state_t *bs)", 151),
	("10017090", "FUN_10017090", "BotIsObserver", "int BotIsObserver(bot_state_t *bs)", 146),
	("10017130", "FUN_10017130", "BotInLavaOrSlime", "int BotInLavaOrSlime(bot_state_t *bs)", 100),
	("100171a0", "FUN_100171a0", "BotCreateWayPoint", "bot_waypoint_t *BotCreateWayPoint(char *name, vec3_t origin, int areanum)", 202),
	("10017270", "FUN_10017270", "BotFindWayPoint", "bot_waypoint_t *BotFindWayPoint(bot_waypoint_t *waypoints, char *name)", 44),
	("100172a0", "FUN_100172a0", "BotFreeWaypoints", "void BotFreeWaypoints(bot_waypoint_t *wp)", 37),
	("100172d0", "FUN_100172d0", "BotAggression", "float BotAggression(bot_state_t *bs)", 327),
	("10017420", "FUN_10017420", "BotFeelingBad", "float BotFeelingBad(bot_state_t *bs)", 72),
	("10017470", "FUN_10017470", "BotWantsToRetreat", "int BotWantsToRetreat(bot_state_t *bs)", 419),
	("10017620", "FUN_10017620", "BotWantsToChase", "int BotWantsToChase(bot_state_t *bs)", 282),
	("10017740", "FUN_10017740", "BotCanAndWantsToRocketJump", "int BotCanAndWantsToRocketJump(bot_state_t *bs)", 158),
	("100177e0", "FUN_100177e0", "BotHasPersistantPowerupAndWeapon", "int BotHasPersistantPowerupAndWeapon(bot_state_t *bs)", 302),
	("10017910", "FUN_10017910", "BotGoCamp", "void BotGoCamp(bot_state_t *bs, bot_goal_t *goal)", 234),
	("10017a00", "FUN_10017a00", "BotWantsToCamp", "int BotWantsToCamp(bot_state_t *bs)", 581),
	("10017c50", "FUN_10017c50", "BotDontAvoid", "void BotDontAvoid(bot_state_t *bs, char *itemname)", 120),
	("10017cd0", "FUN_10017cd0", "BotGoForPowerups", "void BotGoForPowerups(bot_state_t *bs)", 70),
)


SOURCE_HELPERS = {
	"BotPointAreaNum": (
		"int BotPointAreaNum(vec3_t origin)",
		(
			"areanum = trap_AAS_PointAreaNum(origin);",
			"end[2] += 10;",
			"trap_AAS_TraceAreas(origin, end, areas, NULL, 10);",
		),
	),
	"ClientName": (
		"char *ClientName(int client, char *name, int size)",
		(
			"client < 0 || client >= MAX_CLIENTS",
			'BotAI_Print(PRT_ERROR, "ClientName: client out of range\\n");',
			"trap_GetConfigstring(CS_PLAYERS+client, buf, sizeof(buf));",
			"Info_ValueForKey(buf, PLAYER_INFO_KEY_NAME)",
			"Q_CleanStr( name );",
		),
	),
	"ClientFromName": (
		"int ClientFromName(char *name)",
		(
			'cachedMaxClients = trap_Cvar_VariableIntegerValue("sv_maxclients");',
			"trap_GetConfigstring(CS_PLAYERS+i, buf, sizeof(buf));",
			"Q_CleanStr( buf );",
			"if (!Q_stricmp(Info_ValueForKey(buf, PLAYER_INFO_KEY_NAME), name)) return i;",
		),
	),
	"ClientOnSameTeamFromName": (
		"int ClientOnSameTeamFromName(bot_state_t *bs, char *name)",
		(
			'cachedMaxClients = trap_Cvar_VariableIntegerValue("sv_maxclients");',
			"if (!BotSameTeam(bs, i))",
			"trap_GetConfigstring(CS_PLAYERS+i, buf, sizeof(buf));",
			"if (!Q_stricmp(Info_ValueForKey(buf, PLAYER_INFO_KEY_NAME), name)) return i;",
		),
	),
	"stristr": (
		"char *stristr(char *str, char *charset)",
		(
			"while(*str)",
			"toupper(charset[i]) != toupper(str[i])",
			"if (!charset[i]) return str;",
		),
	),
	"EasyClientName": (
		"char *EasyClientName(int client, char *buf, int size)",
		(
			"strcpy(name, ClientName(client, name, sizeof(name)));",
			'for (ptr = strstr(name, " "); ptr; ptr = strstr(name, " "))',
			"if (str1 && str2)",
			"memmove(name, name+2, strlen(name+2)+1);",
			"*ptr += 'a' - 'A';",
		),
	),
	"BotChooseWeapon": (
		"void BotChooseWeapon(bot_state_t *bs)",
		(
			"bs->cur_ps.weaponstate == WEAPON_RAISING",
			"trap_EA_SelectWeapon(bs->client, bs->weaponnum);",
			"trap_BotChooseBestFightWeapon(bs->ws, bs->inventory);",
			"bs->weaponchange_time = FloatTime();",
		),
	),
	"BotSetupForMovement": (
		"void BotSetupForMovement(bot_state_t *bs)",
		(
			"memset(&initmove, 0, sizeof(bot_initmove_t));",
			"PMF_TIME_KNOCKBACK",
			"initmove.or_moveflags |= MFL_TELEPORTED;",
			"PMF_TIME_WATERJUMP",
			"initmove.or_moveflags |= MFL_WATERJUMP;",
			"initmove.presencetype = PRESENCE_CROUCH;",
			"trap_BotInitMoveState(bs->ms, &initmove);",
		),
	),
	"BotCheckItemPickup": (
		"void BotCheckItemPickup(bot_state_t *bs, int *oldinventory)",
		(
			"if (gametype <= GT_TEAM)",
			"INVENTORY_KAMIKAZE",
			"INVENTORY_INVULNERABILITY",
			"INVENTORY_SCOUT",
			"INVENTORY_GUARD",
			"INVENTORY_DOUBLER",
			"INVENTORY_AMMOREGEN",
			"BotVoiceChat(bs, leader, VOICECHAT_WANTONOFFENSE);",
			"BotVoiceChat(bs, -1, VOICECHAT_WANTONDEFENSE);",
		),
	),
	"BotNormalizeAmmoInventory": (
		"static void BotNormalizeAmmoInventory( bot_state_t *bs )",
		(
			"static const int ammoSlots[]",
			"INVENTORY_SHELLS",
			"INVENTORY_BELT",
			"bs->inventory[ammoSlots[i]] = 999;",
		),
	),
	"BotUpdateInventory": (
		"void BotUpdateInventory(bot_state_t *bs)",
		(
			"memcpy(oldinventory, bs->inventory, sizeof(oldinventory));",
			"bs->inventory[INVENTORY_ARMOR] = bs->cur_ps.stats[STAT_ARMOR];",
			"bs->inventory[INVENTORY_REDFLAG] = bs->cur_ps.powerups[PW_REDFLAG] != 0;",
			"bs->inventory[INVENTORY_NEUTRALFLAG] = bs->cur_ps.powerups[PW_NEUTRALFLAG] != 0;",
			"BotNormalizeAmmoInventory( bs );",
			"BotCheckItemPickup(bs, oldinventory);",
		),
	),
	"BotUpdateBattleInventory": (
		"void BotUpdateBattleInventory(bot_state_t *bs, int enemy)",
		(
			"BotEntityInfo(enemy, &entinfo);",
			"bs->inventory[ENEMY_HEIGHT] = (int) dir[2];",
			"bs->inventory[ENEMY_HORIZONTAL_DIST] = (int) VectorLength(dir);",
		),
	),
	"BotUseKamikaze": (
		"void BotUseKamikaze(bot_state_t *bs)",
		(
			"bs->inventory[INVENTORY_KAMIKAZE] <= 0",
			"BotCTFCarryingFlag(bs)",
			"Bot1FCTFCarryingFlag(bs)",
			"BotHarvesterCarryingCubes(bs)",
			"BotVisibleTeamMatesAndEnemies(bs, &teammates, &enemies, KAMIKAZE_DIST);",
			"trap_EA_Use(bs->client);",
		),
	),
	"BotUseInvulnerability": (
		"void BotUseInvulnerability(bot_state_t *bs)",
		(
			"bs->inventory[INVENTORY_INVULNERABILITY] <= 0",
			"BotCTFCarryingFlag(bs)",
			"Bot1FCTFCarryingFlag(bs)",
			"BotHarvesterCarryingCubes(bs)",
			"VectorLengthSquared(dir) < Square(200)",
			"trap_EA_Use(bs->client);",
		),
	),
	"BotBattleUseItems": (
		"void BotBattleUseItems(bot_state_t *bs)",
		(
			"bs->inventory[INVENTORY_HEALTH] < 40",
			"bs->inventory[INVENTORY_TELEPORTER] > 0",
			"bs->inventory[INVENTORY_MEDKIT] > 0",
			"BotUseKamikaze(bs);",
			"BotUseInvulnerability(bs);",
		),
	),
	"BotIsObserver": (
		"qboolean BotIsObserver(bot_state_t *bs)",
		(
			"bs->cur_ps.pm_type == PM_SPECTATOR",
			"trap_GetConfigstring(CS_PLAYERS+bs->client, buf, sizeof(buf));",
			"TEAM_SPECTATOR",
		),
	),
	"BotInLavaOrSlime": (
		"qboolean BotInLavaOrSlime(bot_state_t *bs)",
		(
			"VectorCopy(bs->origin, feet);",
			"feet[2] -= 23;",
			"trap_AAS_PointContents(feet) & (CONTENTS_LAVA|CONTENTS_SLIME)",
		),
	),
	"BotCreateWayPoint": (
		"bot_waypoint_t *BotCreateWayPoint(char *name, vec3_t origin, int areanum)",
		(
			"wp = botai_freewaypoints;",
			'BotAI_Print( PRT_WARNING, "BotCreateWayPoint: Out of waypoints\\n" );',
			"botai_freewaypoints = botai_freewaypoints->next;",
			"Q_strncpyz( wp->name, name, sizeof(wp->name) );",
			"wp->goal.areanum = areanum;",
		),
	),
	"BotFindWayPoint": (
		"bot_waypoint_t *BotFindWayPoint(bot_waypoint_t *waypoints, char *name)",
		(
			"for (wp = waypoints; wp; wp = wp->next)",
			"if (!Q_stricmp(wp->name, name)) return wp;",
		),
	),
	"BotFreeWaypoints": (
		"void BotFreeWaypoints(bot_waypoint_t *wp)",
		(
			"for (; wp; wp = nextwp)",
			"nextwp = wp->next;",
			"wp->next = botai_freewaypoints;",
			"botai_freewaypoints = wp;",
		),
	),
	"BotAggression": (
		"float BotAggression(bot_state_t *bs)",
		(
			"bs->inventory[INVENTORY_QUAD]",
			"bs->inventory[ENEMY_HEIGHT] > 200",
			"bs->inventory[INVENTORY_HEALTH] < 60",
			"bs->inventory[INVENTORY_BFG10K] > 0",
			"bs->inventory[INVENTORY_RAILGUN] > 0",
			"bs->inventory[INVENTORY_SHOTGUN] > 0",
		),
	),
	"BotFeelingBad": (
		"float BotFeelingBad(bot_state_t *bs)",
		(
			"bs->weaponnum == WP_GAUNTLET",
			"bs->inventory[INVENTORY_HEALTH] < 40",
			"bs->weaponnum == WP_MACHINEGUN",
			"bs->inventory[INVENTORY_HEALTH] < 60",
		),
	),
	"BotWantsToRetreat": (
		"int BotWantsToRetreat(bot_state_t *bs)",
		(
			"if (gametype == GT_CTF)",
			"BotCTFCarryingFlag(bs)",
			"Bot1FCTFCarryingFlag(bs)",
			"BotHarvesterCarryingCubes(bs)",
			"EntityCarriesFlag(&entinfo)",
			"bs->ltgtype == LTG_GETFLAG",
			"BotAggression(bs) < 50",
		),
	),
	"BotWantsToChase": (
		"int BotWantsToChase(bot_state_t *bs)",
		(
			"if (gametype == GT_CTF)",
			"BotCTFCarryingFlag(bs)",
			"Bot1FCTFCarryingFlag(bs)",
			"BotHarvesterCarryingCubes(bs)",
			"if (bs->enemy >= 0)",
			"EntityCarriesFlag(&entinfo)",
			"bs->ltgtype == LTG_GETFLAG",
			"BotAggression(bs) > 50",
		),
	),
	"BotCanAndWantsToRocketJump": (
		"int BotCanAndWantsToRocketJump(bot_state_t *bs)",
		(
			"if (!bot_rocketjump.integer) return qfalse;",
			"bs->inventory[INVENTORY_ROCKETLAUNCHER] <= 0",
			"bs->inventory[INVENTORY_ROCKETS] < 3",
			"bs->inventory[INVENTORY_QUAD]",
			"CHARACTERISTIC_WEAPONJUMPING",
			"rocketjumper < 0.5",
		),
	),
	"BotHasPersistantPowerupAndWeapon": (
		"int BotHasPersistantPowerupAndWeapon(bot_state_t *bs)",
		(
			"INVENTORY_SCOUT",
			"INVENTORY_GUARD",
			"INVENTORY_DOUBLER",
			"INVENTORY_AMMOREGEN",
			"bs->inventory[INVENTORY_BFG10K] > 0",
			"bs->inventory[INVENTORY_CHAINGUN] > 0",
		),
	),
	"BotGoCamp": (
		"void BotGoCamp(bot_state_t *bs, bot_goal_t *goal)",
		(
			"bs->ltgtype = LTG_CAMP;",
			"memcpy(&bs->teamgoal, goal, sizeof(bot_goal_t));",
			"CHARACTERISTIC_CAMPER",
			"bs->teamgoal_time = FloatTime() + 99999;",
			"bs->camp_time = FloatTime();",
			"bs->arrive_time = 1;",
		),
	),
	"BotWantsToCamp": (
		"int BotWantsToCamp(bot_state_t *bs)",
		(
			"CHARACTERISTIC_CAMPER",
			"camper < 0.1",
			"bs->ltgtype == LTG_TEAMHELP",
			"bs->camp_time > FloatTime() - 60 + 300 * (1-camper)",
			"BotAggression(bs) < 50",
			"trap_BotGetNextCampSpotGoal(0, &goal)",
			"trap_AAS_AreaTravelTimeToGoalArea(bs->areanum, bs->origin, goal.areanum, TFL_DEFAULT);",
			"BotGoCamp(bs, &bestgoal);",
		),
	),
	"BotDontAvoid": (
		"void BotDontAvoid(bot_state_t *bs, char *itemname)",
		(
			"trap_BotGetLevelItemGoal(-1, itemname, &goal);",
			"trap_BotRemoveFromAvoidGoals(bs->gs, goal.number);",
			"trap_BotGetLevelItemGoal(num, itemname, &goal);",
		),
	),
	"BotGoForPowerups": (
		"void BotGoForPowerups(bot_state_t *bs)",
		(
			'BotDontAvoid(bs, "Quad Damage");',
			'BotDontAvoid(bs, "Regeneration");',
			'BotDontAvoid(bs, "Battle Suit");',
			'BotDontAvoid(bs, "Speed");',
			'BotDontAvoid(bs, "Invisibility");',
			"bs->ltg_time = 0;",
		),
	),
}


HLIL_ENTRY_ANCHORS = (
	"10015a40    int32_t sub_10015a40(int32_t* arg1 @ esi)",
	"10015ad0    char* sub_10015ad0(char* arg1 @ esi, int32_t arg2 @ edi, int32_t arg3)",
	"10015b80    int32_t sub_10015b80(char* arg1)",
	"10015c90    int32_t sub_10015c90(char* arg1 @ edi, void* arg2)",
	"10015d80    int32_t sub_10015d80(int32_t arg1, char* arg2)",
	"10015df0    int32_t sub_10015df0(int32_t arg1, int32_t arg2)",
	"10015ed0    int32_t sub_10015ed0(void* arg1 @ esi)",
	"10015f70    int32_t sub_10015f70(void* arg1 @ esi)",
	'100160c0    void __convention("regparm") sub_100160c0(void* const arg1, int32_t arg2, void* arg3)',
	'100162d0    void __convention("regparm") sub_100162d0(void* arg1)',
	"10016380    void* sub_10016380()",
	"10016670    int32_t __fastcall sub_10016670(int32_t arg1, void* arg2 @ esi)",
	"10016720    void __fastcall sub_10016720(int32_t arg1)",
	"10016c90    void sub_10016c90()",
	'10016ff0    int80_t __convention("regparm") sub_10016ff0(void* arg1)',
	"10017090    int32_t sub_10017090(void* arg1)",
	"10017130    int32_t sub_10017130(void* arg1)",
	"100171a0    void* sub_100171a0(int32_t arg1, float* arg2, int32_t arg3)",
	'10017270    void* __convention("regparm") sub_10017270(void* arg1, char* arg2 @ edi)',
	'100172a0    void __convention("regparm") sub_100172a0(void* arg1)',
	'100172d0    void __convention("regparm") sub_100172d0(void* arg1)',
	'10017420    void __convention("regparm") sub_10017420(void* arg1)',
	"10017470    long double sub_10017470(void* arg1 @ esi)",
	"10017620    void sub_10017620(void* arg1 @ esi)",
	'10017740    int32_t __convention("regparm") sub_10017740(void* arg1, long double arg2 @ st0)',
	'100177e0    int32_t __convention("regparm") sub_100177e0(void* arg1)',
	"10017910    int32_t __fastcall sub_10017910(int32_t arg1, int32_t arg2, long double arg3 @ st0)",
	"10017a00    int32_t __fastcall sub_10017a00(void* arg1, long double arg2 @ st0)",
	"10017c50    int32_t sub_10017c50()",
	'10017cd0    int32_t __convention("regparm") sub_10017cd0(void* arg1)',
)


HLIL_FLOW_ANCHORS = (
	"10015a5a  int32_t result = (*(data_104b13ac + 0x10c))(arg1)",
	"10015aa8          (*(ecx_1 + 0x114))(arg1, &var_38, &var_2c, result, 0xa, var_38, arg1[1], var_30_1)",
	'10015b55      sub_10020980(3, "ClientName: client out of range\\n")',
	"10015ba6  if (eax_2 == 0)",
	"10015ce8          eax_2, edx = sub_10018900(eax_2, edx, i, arg2)",
	"10015e1f  char* eax_3 = sub_10015ad0(&var_84, 0x80, arg1)",
	"10015f03      int32_t eax_2 = (*(data_104b13ac + 0x2c8))(*(arg1 + 0x1968), arg1 + 0x1338)",
	"100160a6  int32_t result = (*(data_104b13ac + 0x2c0))(*(arg1 + 0x195c), &var_48)",
	'1001623d                  int32_t eax_7 = sub_10070cb0("vsay_team %s")',
	"100162de  if (*(arg1 + 0x1380) == 0xffffffff)",
	"10016659  sub_100160c0(&var_408, edx_29, result)",
	"10016660  sub_100162d0(result)",
	"1001707b  sub_10016720(ecx)",
	"10017086  return sub_10016c90()",
	"10017188      edx(&var_10, var_10, *(arg1 + 0x1310), fconvert.s(x87_r7_1), eax_1) & 0x18",
	'100171b7      sub_10020980(2, "BotCreateWayPoint: Out of waypoi…")',
	"10017280      if (i != 0xfffffffc && arg2 != 0)",
	"100172bc      while (i != 0)",
	"10017583              var_f4 = sub_10017420(arg1)",
	"100175e8          var_f4 = sub_100172d0(arg1)",
	"100177c4              (*(data_104b13ac + 0x1c4))(*(arg1 + 0x1958), 0x26, fconvert.s(float.t(0)),",
	"10017b9a                      int32_t i = (*(data_104b13ac + 0x260))(0, &var_4c)",
	"10017bd4                              int32_t eax_14 = (*(data_104b13ac + 0x134))(*(arg1 + 0x1334),",
	"10017c1f                              sub_10017910(ecx_3, &var_8c, x87_r0_7)",
	"10017c73  int32_t result = (*(data_104b13ac + 0x268))(0xffffffff)",
	"10017c98      (*(data_104b13ac + 0x228))(*(ebx + 0x1960), var_20)",
	"10017cda  sub_10017c50()",
	"10017d0b  *(arg1 + 0x1794) = 0",
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


def test_qagame_ai_dmq3_support_aliases_source_and_hlil_are_pinned() -> None:
	source = _read(GAME_AI_DMQ3)
	hlil = _read(QAGAME_HLIL_PART01)
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}

	for address, raw_name, normalized_name, signature, size in AI_DMQ3_SUPPORT_FUNCTIONS:
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


def test_qagame_ai_dmq3_support_botlib_import_wiring_is_pinned() -> None:
	ai_dmq3 = _read(GAME_AI_DMQ3)
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)

	for expected in (
		"G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM = 67,",
		"G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS = 69,",
		"G_QL_IMPORT_BOTLIB_AAS_POINT_CONTENTS = 70,",
		"G_QL_IMPORT_BOTLIB_EA_USE = 93,",
		"G_QL_IMPORT_BOTLIB_EA_SELECT_WEAPON = 102,",
		"G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT = 113,",
		"G_QL_IMPORT_BOTLIB_AI_REMOVE_FROM_AVOID_GOALS = 138,",
		"G_QL_IMPORT_BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL = 152,",
		"G_QL_IMPORT_BOTLIB_AI_GET_LEVEL_ITEM_GOAL = 154,",
		"G_QL_IMPORT_BOTLIB_AI_INIT_MOVE_STATE = 176,",
		"G_QL_IMPORT_BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON = 178,",
	):
		assert expected in game_public

	for expected in (
		"case BOTLIB_AAS_POINT_AREA_NUM: return G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM;",
		"case BOTLIB_AAS_TRACE_AREAS: return G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS;",
		"case BOTLIB_AAS_POINT_CONTENTS: return G_QL_IMPORT_BOTLIB_AAS_POINT_CONTENTS;",
		"case BOTLIB_EA_USE: return G_QL_IMPORT_BOTLIB_EA_USE;",
		"case BOTLIB_EA_SELECT_WEAPON: return G_QL_IMPORT_BOTLIB_EA_SELECT_WEAPON;",
		"case BOTLIB_AI_CHARACTERISTIC_BFLOAT: return G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT;",
		"case BOTLIB_AI_REMOVE_FROM_AVOID_GOALS: return G_QL_IMPORT_BOTLIB_AI_REMOVE_FROM_AVOID_GOALS;",
		"case BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL: return G_QL_IMPORT_BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL;",
		"case BOTLIB_AI_GET_LEVEL_ITEM_GOAL: return G_QL_IMPORT_BOTLIB_AI_GET_LEVEL_ITEM_GOAL;",
		"case BOTLIB_AI_INIT_MOVE_STATE: return G_QL_IMPORT_BOTLIB_AI_INIT_MOVE_STATE;",
		"case BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON: return G_QL_IMPORT_BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON;",
		"return syscall( BOTLIB_AAS_POINT_AREA_NUM, point );",
		"return syscall( BOTLIB_AAS_TRACE_AREAS, start, end, areas, points, maxareas );",
		"return syscall( BOTLIB_AAS_POINT_CONTENTS, point );",
		"syscall( BOTLIB_EA_USE, client );",
		"syscall( BOTLIB_EA_SELECT_WEAPON, client, weapon );",
		"temp = syscall( BOTLIB_AI_CHARACTERISTIC_BFLOAT, character, index, PASSFLOAT(min), PASSFLOAT(max) );",
		"syscall( BOTLIB_AI_REMOVE_FROM_AVOID_GOALS, goalstate, number);",
		"return syscall( BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL, num, goal );",
		"return syscall( BOTLIB_AI_GET_LEVEL_ITEM_GOAL, index, classname, goal );",
		"syscall( BOTLIB_AI_INIT_MOVE_STATE, handle, initmove );",
		"return syscall( BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON, weaponstate, inventory );",
	):
		assert expected in game_syscalls

	for expected in (
		"[BOTLIB_AAS_POINT_AREA_NUM] = (ql_import_f)QL_G_trap_AAS_PointAreaNum,",
		"[BOTLIB_AAS_TRACE_AREAS] = (ql_import_f)QL_G_trap_AAS_TraceAreas,",
		"[BOTLIB_AAS_POINT_CONTENTS] = (ql_import_f)QL_G_trap_AAS_PointContents,",
		"[BOTLIB_EA_USE] = (ql_import_f)QL_G_trap_EA_Use,",
		"[BOTLIB_EA_SELECT_WEAPON] = (ql_import_f)QL_G_trap_EA_SelectWeapon,",
		"[BOTLIB_AI_CHARACTERISTIC_BFLOAT] = (ql_import_f)QL_G_trap_Characteristic_BFloat,",
		"[BOTLIB_AI_REMOVE_FROM_AVOID_GOALS] = (ql_import_f)QL_G_trap_BotRemoveFromAvoidGoals,",
		"[BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL] = (ql_import_f)QL_G_trap_BotGetNextCampSpotGoal,",
		"[BOTLIB_AI_GET_LEVEL_ITEM_GOAL] = (ql_import_f)QL_G_trap_BotGetLevelItemGoal,",
		"[BOTLIB_AI_INIT_MOVE_STATE] = (ql_import_f)QL_G_trap_BotInitMoveState,",
		"[BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON] = (ql_import_f)QL_G_trap_BotChooseBestFightWeapon,",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM] = (ql_import_f)QL_G_trap_AAS_PointAreaNum;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS] = (ql_import_f)QL_G_trap_AAS_TraceAreas;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_POINT_CONTENTS] = (ql_import_f)QL_G_trap_AAS_PointContents;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_EA_USE] = (ql_import_f)QL_G_trap_EA_Use;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_EA_SELECT_WEAPON] = (ql_import_f)QL_G_trap_EA_SelectWeapon;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT] = (ql_import_f)QL_G_trap_Characteristic_BFloat;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_REMOVE_FROM_AVOID_GOALS] = (ql_import_f)QL_G_trap_BotRemoveFromAvoidGoals;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL] = (ql_import_f)QL_G_trap_BotGetNextCampSpotGoal;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_LEVEL_ITEM_GOAL] = (ql_import_f)QL_G_trap_BotGetLevelItemGoal;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_INIT_MOVE_STATE] = (ql_import_f)QL_G_trap_BotInitMoveState;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON] = (ql_import_f)QL_G_trap_BotChooseBestFightWeapon;",
	):
		assert expected in server_game

	for expected in (
		"return G_Import_Syscall( BOTLIB_AAS_POINT_AREA_NUM, point );",
		"return G_Import_Syscall( BOTLIB_AAS_TRACE_AREAS, start, end, areas, points, maxareas );",
		"return G_Import_Syscall( BOTLIB_AAS_POINT_CONTENTS, point );",
		"G_Import_Syscall( BOTLIB_EA_USE, client );",
		"G_Import_Syscall( BOTLIB_EA_SELECT_WEAPON, client, weapon );",
		"temp = G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_BFLOAT, character, index, QL_G_PASSFLOAT(min), QL_G_PASSFLOAT(max) );",
		"G_Import_Syscall( BOTLIB_AI_REMOVE_FROM_AVOID_GOALS, goalstate, number);",
		"return G_Import_Syscall( BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL, num, goal );",
		"return G_Import_Syscall( BOTLIB_AI_GET_LEVEL_ITEM_GOAL, index, classname, goal );",
		"G_Import_Syscall( BOTLIB_AI_INIT_MOVE_STATE, handle, initmove );",
		"return G_Import_Syscall( BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON, weaponstate, inventory );",
	):
		assert expected in ql_game_imports

	for expected in (
		"trap_AAS_PointAreaNum(origin);",
		"trap_AAS_TraceAreas(origin, end, areas, NULL, 10);",
		"trap_AAS_PointContents(feet)",
		"trap_EA_Use(bs->client);",
		"trap_EA_SelectWeapon(bs->client, bs->weaponnum);",
		"trap_Characteristic_BFloat(bs->character, CHARACTERISTIC_WEAPONJUMPING, 0, 1);",
		"trap_Characteristic_BFloat(bs->character, CHARACTERISTIC_CAMPER, 0, 1);",
		"trap_BotRemoveFromAvoidGoals(bs->gs, goal.number);",
		"trap_BotGetNextCampSpotGoal(0, &goal)",
		"trap_BotGetLevelItemGoal(-1, itemname, &goal);",
		"trap_BotInitMoveState(bs->ms, &initmove);",
		"trap_BotChooseBestFightWeapon(bs->ws, bs->inventory);",
	):
		assert expected in ai_dmq3
