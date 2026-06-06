from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_AI_CMD = REPO_ROOT / "src" / "code" / "game" / "ai_cmd.c"
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


AI_CMD_FUNCTIONS = (
	("10004930", "FUN_10004930", "BotGetItemTeamGoal", "int BotGetItemTeamGoal(char *goalname, bot_goal_t *goal)", 60),
	("10004970", "FUN_10004970", "BotGetMessageTeamGoal", "int BotGetMessageTeamGoal(bot_state_t *bs, char *goalname, bot_goal_t *goal)", 90),
	("100049d0", "FUN_100049d0", "BotGetTime", "float BotGetTime(bot_match_t *match)", 468),
	("10004bb0", "FUN_10004bb0", "FindClientByName", "int FindClientByName(char *name)", 534),
	("10004dd0", "FUN_10004dd0", "FindEnemyByName", "int FindEnemyByName(bot_state_t *bs, char *name)", 476),
	("10004fb0", "FUN_10004fb0", "NumPlayersOnSameTeam", "int NumPlayersOnSameTeam(bot_state_t *bs)", 368),
	("10005120", "FUN_10005120", "BotGetPatrolWaypoints", "int BotGetPatrolWaypoints(bot_state_t *bs, bot_match_t *match)", 655),
	("100053b0", "FUN_100053b0", "BotAddressedToBot", "int BotAddressedToBot(bot_state_t *bs, bot_match_t *match)", 727),
	("10005690", "FUN_10005690", "BotMatch_HelpAccompany", "void BotMatch_HelpAccompany(bot_state_t *bs, bot_match_t *match)", 1112),
	("10005af0", "FUN_10005af0", "BotMatch_DefendKeyArea", "void BotMatch_DefendKeyArea(bot_state_t *bs, bot_match_t *match)", 334),
	("10005c40", "FUN_10005c40", "BotMatch_GetItem", "void BotMatch_GetItem(bot_state_t *bs, bot_match_t *match)", 283),
	("10005d60", "FUN_10005d60", "BotMatch_Camp", "void BotMatch_Camp(bot_state_t *bs, bot_match_t *match)", 862),
	("100060c0", "FUN_100060c0", "BotMatch_Patrol", "void BotMatch_Patrol(bot_state_t *bs, bot_match_t *match)", 280),
	("100061e0", "FUN_100061e0", "BotMatch_GetFlag", "void BotMatch_GetFlag(bot_state_t *bs, bot_match_t *match)", 340),
	("10006340", "FUN_10006340", "BotMatch_AttackEnemyBase", "void BotMatch_AttackEnemyBase(bot_state_t *bs, bot_match_t *match)", 359),
	("100064b0", "FUN_100064b0", "BotMatch_Harvest", "void BotMatch_Harvest(bot_state_t *bs, bot_match_t *match)", 274),
	("100065d0", "FUN_100065d0", "BotMatch_RushBase", "void BotMatch_RushBase(bot_state_t *bs, bot_match_t *match)", 308),
	("10006710", "FUN_10006710", "BotMatch_TaskPreference", "void BotMatch_TaskPreference(bot_state_t *bs, bot_match_t *match)", 393),
	("100068a0", "FUN_100068a0", "BotMatch_ReturnFlag", "void BotMatch_ReturnFlag(bot_state_t *bs, bot_match_t *match)", 227),
	("10006990", "FUN_10006990", "BotMatch_JoinSubteam", "void BotMatch_JoinSubteam(bot_state_t *bs, bot_match_t *match)", 218),
	("10006a70", "FUN_10006a70", "BotMatch_LeaveSubteam", "void BotMatch_LeaveSubteam(bot_state_t *bs, bot_match_t *match)", 171),
	("10006b20", "FUN_10006b20", "BotMatch_WhichTeam", "void BotMatch_WhichTeam(bot_state_t *bs, bot_match_t *match)", 114),
	("10006ba0", "FUN_10006ba0", "BotMatch_CheckPoint", "void BotMatch_CheckPoint(bot_state_t *bs, bot_match_t *match)", 524),
	("10006db0", "FUN_10006db0", "BotMatch_FormationSpace", "void BotMatch_FormationSpace(bot_state_t *bs, bot_match_t *match)", 204),
	("10006e80", "FUN_10006e80", "BotMatch_Dismiss", "void BotMatch_Dismiss(bot_state_t *bs, bot_match_t *match)", 193),
	("10006f50", "FUN_10006f50", "BotMatch_Suicide", "void BotMatch_Suicide(bot_state_t *bs, bot_match_t *match)", 237),
	("10007040", "FUN_10007040", "BotMatch_StartTeamLeaderShip", "void BotMatch_StartTeamLeaderShip(bot_state_t *bs, bot_match_t *match)", 203),
	("10007110", "FUN_10007110", "BotMatch_StopTeamLeaderShip", "void BotMatch_StopTeamLeaderShip(bot_state_t *bs, bot_match_t *match)", 233),
	("10007200", "FUN_10007200", "BotMatch_WhoIsTeamLeader", "void BotMatch_WhoIsTeamLeader(bot_state_t *bs, bot_match_t *match)", 114),
	("10007280", "FUN_10007280", "BotMatch_WhatAreYouDoing", "void BotMatch_WhatAreYouDoing(bot_state_t *bs, bot_match_t *match)", 517),
	("100074c0", "FUN_100074c0", "BotMatch_WhatIsMyCommand", "void BotMatch_WhatIsMyCommand(bot_state_t *bs, bot_match_t *match)", 86),
	("10007520", "FUN_10007520", "BotNearestVisibleItem", "float BotNearestVisibleItem(bot_state_t *bs, char *itemname, bot_goal_t *goal)", 381),
	("100076b0", "FUN_100076b0", "BotMatch_WhereAreYou", "void BotMatch_WhereAreYou(bot_state_t *bs, bot_match_t *match)", 908),
	("10007a40", "FUN_10007a40", "BotMatch_LeadTheWay", "void BotMatch_LeadTheWay(bot_state_t *bs, bot_match_t *match)", 651),
	("10007cd0", "FUN_10007cd0", "BotMatch_Kill", "void BotMatch_Kill(bot_state_t *bs, bot_match_t *match)", 306),
	("10007e10", "FUN_10007e10", "BotMatch_CTF", "void BotMatch_CTF(bot_state_t *bs, bot_match_t *match)", 414),
	("10007fb0", "FUN_10007fb0", "BotMatch_EnterGame", "void BotMatch_EnterGame(bot_state_t *bs, bot_match_t *match)", 85),
	("10008010", "FUN_10008010", "BotMatch_NewLeader", "void BotMatch_NewLeader(bot_state_t *bs, bot_match_t *match)", 129),
	("100080a0", "FUN_100080a0", "BotMatchMessage", "int BotMatchMessage(bot_state_t *bs, char *message)", 665),
)


SOURCE_ANCHORS = {
	"BotGetItemTeamGoal": (
		"if (!strlen(goalname)) return qfalse;",
		"i = trap_BotGetLevelItemGoal(i, goalname, goal);",
		"if (goal->flags & GFL_DROPPED)",
	),
	"BotGetMessageTeamGoal": (
		"if (BotGetItemTeamGoal(goalname, goal)) return qtrue;",
		"cp = BotFindWayPoint(bs->checkpoints, goalname);",
		"memcpy(goal, &cp->goal, sizeof(bot_goal_t));",
	),
	"BotGetTime": (
		"if (match->subtype & ST_TIME)",
		"trap_BotMatchVariable(match, TIME, timestring, MAX_MESSAGE_SIZE);",
		"trap_BotFindMatch(timestring, &timematch, MTCONTEXT_TIME)",
		"timematch.type == MSG_FOREVER",
		"if (t > 0) return FloatTime() + t;",
	),
	"FindClientByName": (
		'trap_Cvar_VariableIntegerValue("sv_maxclients")',
		"if (!Q_stricmp(buf, name)) return i;",
		"if (stristr(buf, name)) return i;",
	),
	"FindEnemyByName": (
		"if (BotSameTeam(bs, i)) continue;",
		"if (!Q_stricmp(buf, name)) return i;",
		"if (stristr(buf, name)) return i;",
	),
	"NumPlayersOnSameTeam": (
		"trap_GetConfigstring(CS_PLAYERS+i, buf, MAX_INFO_STRING);",
		"if (BotSameTeam(bs, i+1)) num++;",
	),
	"BotGetPatrolWaypoints": (
		"trap_BotFindMatch(keyarea, &keyareamatch, MTCONTEXT_PATROLKEYAREA)",
		'trap_EA_SayTeam(bs->client, "what do you say?");',
		"BotCreateWayPoint(keyarea, goal.origin, goal.areanum);",
		"patrolflags = PATROL_LOOP;",
		"patrolflags = PATROL_REVERSE;",
		'trap_EA_SayTeam(bs->client, "I need more key points to patrol\\n");',
	),
	"BotAddressedToBot": (
		"trap_BotMatchVariable(match, NETNAME, netname, sizeof(netname));",
		"ClientOnSameTeamFromName(bs, netname);",
		"trap_BotMatchVariable(match, ADDRESSEE, addressedto, sizeof(addressedto));",
		"while(trap_BotFindMatch(addressedto, &addresseematch, MTCONTEXT_ADDRESSEE))",
		"if (addresseematch.type == MSG_EVERYONE)",
		"tellmatch.type != MSG_CHATTELL",
		"random() > (float ) 1.0 / (NumPlayersOnSameTeam(bs)-1)",
	),
	"BotMatch_HelpAccompany": (
		"if (!TeamPlayIsOn()) return;",
		"if (!BotAddressedToBot(bs, match)) return;",
		"trap_BotFindMatch(teammate, &teammatematch, MTCONTEXT_TEAMMATE)",
		"BotEntityInfo(client, &entinfo);",
		"bs->ltgtype = LTG_TEAMHELP;",
		"bs->ltgtype = LTG_TEAMACCOMPANY;",
		"BotRememberLastOrderedTask(bs);",
	),
	"BotMatch_DefendKeyArea": (
		"trap_BotMatchVariable(match, KEYAREA, itemname, sizeof(itemname));",
		"bs->ltgtype = LTG_DEFENDKEYAREA;",
		"TEAM_DEFENDKEYAREA_TIME",
	),
	"BotMatch_GetItem": (
		"trap_BotMatchVariable(match, ITEM, itemname, sizeof(itemname));",
		"bs->ltgtype = LTG_GETITEM;",
		"TEAM_GETITEM_TIME",
	),
	"BotMatch_Camp": (
		"if (match->subtype & ST_THERE)",
		"else if (match->subtype & ST_HERE)",
		"bs->ltgtype = LTG_CAMPORDER;",
		"TEAM_CAMP_TIME",
	),
	"BotMatch_Patrol": (
		"if (!BotGetPatrolWaypoints(bs, match)) return;",
		"bs->ltgtype = LTG_PATROL;",
		"TEAM_PATROL_TIME",
	),
	"BotMatch_GetFlag": (
		"if (gametype == GT_CTF)",
		"else if (gametype == GT_1FCTF)",
		"bs->ltgtype = LTG_GETFLAG;",
		"BotGetAlternateRouteGoal(bs, BotOppositeTeam(bs));",
	),
	"BotMatch_AttackEnemyBase": (
		"BotMatch_GetFlag(bs, match);",
		"gametype == GT_OBELISK",
		"bs->ltgtype = LTG_ATTACKENEMYBASE;",
	),
	"BotMatch_Harvest": (
		"if (gametype == GT_HARVESTER)",
		"bs->ltgtype = LTG_HARVEST;",
		"TEAM_HARVEST_TIME",
	),
	"BotMatch_RushBase": (
		"gametype == GT_1FCTF || gametype == GT_HARVESTER",
		"bs->ltgtype = LTG_RUSHBASE;",
		"CTF_RUSHBASE_TIME",
	),
	"BotMatch_TaskPreference": (
		"preference &= ~TEAMTP_ATTACKER;",
		"preference |= TEAMTP_DEFENDER;",
		"BotSetTeamMateTaskPreference(bs, teammate, preference);",
		'BotAI_BotInitialChat(bs, "keepinmind", teammatename, NULL);',
	),
	"BotMatch_ReturnFlag": (
		"gametype != GT_CTF",
		"gametype != GT_1FCTF",
		"bs->ltgtype = LTG_RETURNFLAG;",
		"CTF_RETURNFLAG_TIME",
	),
	"BotMatch_JoinSubteam": (
		"trap_BotMatchVariable(match, TEAMNAME, teammate, sizeof(teammate));",
		"strncpy(bs->subteam, teammate, 32);",
		'BotAI_BotInitialChat(bs, "joinedteam", teammate, NULL);',
	),
	"BotMatch_LeaveSubteam": (
		'BotAI_BotInitialChat(bs, "leftteam", bs->subteam, NULL);',
		'strcpy(bs->subteam, "");',
	),
	"BotMatch_WhichTeam": (
		'BotAI_BotInitialChat(bs, "inteam", bs->subteam, NULL);',
		'BotAI_BotInitialChat(bs, "noteam", NULL);',
	),
	"BotMatch_CheckPoint": (
		'sscanf(buf, "%f %f %f", &position[0], &position[1], &position[2]);',
		'BotAI_BotInitialChat(bs, "checkpoint_invalid", NULL);',
		"cp = BotCreateWayPoint(buf, position, areanum);",
		'BotAI_BotInitialChat(bs, "checkpoint_confirm", cp->name, buf, NULL);',
	),
	"BotMatch_FormationSpace": (
		"if (match->subtype & ST_FEET) space = 0.3048 * 32 * atof(buf);",
		"else space = 32 * atof(buf);",
		"if (space < 48 || space > 500) space = 100;",
	),
	"BotMatch_Dismiss": (
		"bs->ltgtype = 0;",
		"bs->lead_time = 0;",
		'BotAI_BotInitialChat(bs, "dismissed", NULL);',
	),
	"BotMatch_Suicide": (
		'trap_EA_Command(bs->client, "kill");',
		"BotVoiceChat(bs, client, VOICECHAT_TAUNT);",
		"trap_EA_Action(bs->client, ACTION_AFFIRMATIVE);",
	),
	"BotMatch_StartTeamLeaderShip": (
		"if (match->subtype & ST_I)",
		"Q_strncpyz(bs->teamleader, teammate, sizeof(bs->teamleader));",
		"if (client >= 0) ClientName(client, bs->teamleader, sizeof(bs->teamleader));",
	),
	"BotMatch_StopTeamLeaderShip": (
		"trap_BotMatchVariable(match, TEAMMATE, teammate, sizeof(teammate));",
		"bs->teamleader[0] = '\\0';",
		"notleader[client] = qtrue;",
	),
	"BotMatch_WhoIsTeamLeader": (
		'trap_EA_SayTeam(bs->client, "I\'m the team leader\\n");',
	),
	"BotMatch_WhatAreYouDoing": (
		'"helping"',
		'"accompanying"',
		'"defending"',
		'"gettingitem"',
		'"killing"',
		'"capturingflag"',
		'"attackingenemybase"',
		'"roaming"',
	),
	"BotMatch_WhatIsMyCommand": (
		"if (Q_stricmp(netname, bs->teamleader) != 0) return;",
		"bs->forceorders = qtrue;",
	),
	"BotNearestVisibleItem": (
		"i = trap_BotGetLevelItemGoal(i, itemname, &tmpgoal);",
		"trap_BotGoalName(tmpgoal.number, name, sizeof(name));",
		"BotAI_Trace(&trace, bs->eye, NULL, NULL, tmpgoal.origin, bs->client, CONTENTS_SOLID|CONTENTS_PLAYERCLIP);",
		"memcpy(goal, &tmpgoal, sizeof(bot_goal_t));",
	),
	"BotMatch_WhereAreYou": (
		'"Neutral Obelisk"',
		"BotNearestVisibleItem(bs, nearbyitems[i], &goal);",
		'BotAI_BotInitialChat(bs, "teamlocation", nearbyitems[bestitem], "red", NULL);',
		'BotAI_BotInitialChat(bs, "location", nearbyitems[bestitem], NULL);',
	),
	"BotMatch_LeadTheWay": (
		"if (match->subtype & ST_SOMEONE)",
		"bs->lead_teamgoal.entitynum = -1;",
		"bs->lead_teammate = client;",
		"bs->lead_time = FloatTime() + TEAM_LEAD_TIME;",
	),
	"BotMatch_Kill": (
		"trap_BotMatchVariable(match, ENEMY, enemy, sizeof(enemy));",
		"client = FindEnemyByName(bs, enemy);",
		'BotAI_BotInitialChat(bs, "whois", enemy, NULL);',
		"bs->ltgtype = LTG_KILL;",
	),
	"BotMatch_CTF": (
		"if (gametype == GT_CTF)",
		"trap_BotMatchVariable(match, FLAG, flag, sizeof(flag));",
		"bs->redflagstatus = 1;",
		"bs->blueflagstatus = 1;",
		"bs->flagstatuschanged = 1;",
		"else if (gametype == GT_1FCTF)",
	),
	"BotMatch_EnterGame": (
		"client = FindClientByName(netname);",
		"notleader[client] = qfalse;",
	),
	"BotMatch_NewLeader": (
		"client = FindClientByName(netname);",
		"if (!BotSameTeam(bs, client))",
		"Q_strncpyz(bs->teamleader, netname, sizeof(bs->teamleader));",
	),
	"BotMatchMessage": (
		"trap_BotFindMatch(message, &match, MTCONTEXT_MISC",
		"|MTCONTEXT_INITIALTEAMCHAT",
		"|MTCONTEXT_CTF",
		"case MSG_HELP:",
		"case MSG_DEFENDKEYAREA:",
		"case MSG_CTF:",
		"case MSG_SUICIDE:",
		'BotAI_Print(PRT_MESSAGE, "unknown match type\\n");',
	),
}


HLIL_ENTRY_ANCHORS = (
	"10004930    int32_t __fastcall sub_10004930(int32_t arg1, void* arg2 @ esi, char* arg3 @ edi)",
	'10004970    int32_t __convention("regparm") sub_10004970(char* arg1, void* arg2)',
	"100049d0    int32_t sub_100049d0(long double arg1 @ st0, int32_t arg2)",
	"10004bb0    int32_t sub_10004bb0(char* arg1)",
	'10004dd0    int32_t __convention("regparm") sub_10004dd0(int32_t arg1, int32_t arg2, char* arg3, void* arg4)',
	"10004fb0    int32_t sub_10004fb0(void* arg1)",
	"10005120    int32_t sub_10005120(void* arg1 @ edi, int32_t arg2)",
	"100053b0    void __fastcall sub_100053b0(void* arg1, void* arg2)",
	"10005690    int32_t sub_10005690(int32_t arg1 @ edi, long double arg2 @ st0, int32_t arg3)",
	"10005af0    void* sub_10005af0(void* arg1 @ esi, int32_t arg2 @ edi)",
	"10005c40    void* __fastcall sub_10005c40(void* arg1, void* arg2 @ esi)",
	"10005d60    void* __fastcall sub_10005d60(int32_t arg1, void* arg2 @ edi)",
	"100060c0    void* __fastcall sub_100060c0(void* arg1, int32_t arg2 @ esi)",
	"100061e0    void* __fastcall sub_100061e0(void* arg1, void* arg2 @ edi)",
	"10006340    int32_t __fastcall sub_10006340(void* arg1)",
	"100064b0    void* sub_100064b0(void* arg1 @ esi, void* arg2 @ edi)",
	"100065d0    void* sub_100065d0(void* arg1 @ esi, void* arg2 @ edi)",
	'10006710    void* __convention("regparm") sub_10006710(int32_t arg1, int32_t arg2, void* arg3, void* arg4)',
	"100068a0    int32_t sub_100068a0(void* arg1 @ esi, void* arg2 @ edi)",
	"10006990    int32_t sub_10006990(void* arg1 @ esi, void* arg2 @ edi)",
	"10006a70    void* sub_10006a70(void* arg1 @ esi)",
	"10006b20    void sub_10006b20(void* arg1 @ esi)",
	"10006ba0    int32_t sub_10006ba0(void* arg1)",
	"10006db0    int32_t sub_10006db0(void* arg1 @ esi, void* arg2 @ edi)",
	"10006e80    int32_t __fastcall sub_10006e80(void* arg1, void* arg2 @ esi)",
	"10006f50    int32_t __fastcall sub_10006f50(void* arg1, void* arg2 @ esi)",
	'10007040    char* __convention("regparm") sub_10007040(int32_t arg1, int32_t arg2, void* arg3, char* arg4)',
	'10007110    char* __convention("regparm") sub_10007110(int32_t arg1, int32_t arg2, void* arg3, void* arg4)',
	"10007200    void* sub_10007200()",
	'10007280    int80_t __convention("regparm") sub_10007280(int32_t arg1, int32_t arg2, void* arg3, void* arg4)',
	"100074c0    void* sub_100074c0()",
	'10007520    void __convention("regparm") sub_10007520(int32_t arg1, int32_t arg2, void* arg3, int32_t arg4)',
	"100076b0    int32_t sub_100076b0(void* arg1 @ esi)",
	"10007a40    int32_t __fastcall sub_10007a40(void* arg1, void* arg2 @ edi)",
	"10007cd0    void* sub_10007cd0(void* arg1 @ esi, void* arg2 @ edi)",
	"10007e10    int32_t sub_10007e10(void* arg1 @ esi, void* arg2 @ edi)",
	"10007fb0    int32_t sub_10007fb0(int32_t arg1)",
	'10008010    int32_t __convention("regparm") sub_10008010(int32_t arg1, int32_t arg2, void* arg3, int32_t arg4)',
	"100080a0    int32_t sub_100080a0(int32_t arg1, int32_t arg2)",
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


def test_qagame_ai_cmd_team_order_aliases_source_and_hlil_are_pinned() -> None:
	source = _read(GAME_AI_CMD)
	hlil = _read(QAGAME_HLIL_PART01)
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}

	for address, raw_name, normalized_name, signature, size in AI_CMD_FUNCTIONS:
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
		"10004976  eax, edx = sub_10004930(ecx, ebx, arg1)",
		'10005291      (*(data_104b13ac + 0x158))(*(arg1 + 8), "what do you say?")',
		"100056bf      st0_1, eax_1 = sub_100053b0(arg1, arg3)",
		"10005a1a                      sub_100049d0(st0_1, arg3)",
		"10005b49              sub_10004970(&var_20c, (*(data_104b13ac + 0x20c))(arg2, 5, &var_20c, 0x100))",
		"10006057              sub_100049d0(st0_1, esi)",
		"100077fa              st0_2, result, edx_1, xmm0_1 = sub_10007520(&var_14c, edx_1, arg1, &var_14c)",
		'10007995                      sub_10020dc0(arg1, "teamlocation", eax_15)',
		"100080a0    int32_t sub_100080a0(int32_t arg1, int32_t arg2)",
		"10008125                  sub_10005690(arg1, x87_r0, &var_154)",
		"100082d7                  sub_10007fb0(&var_154)",
		"10008305          sub_10007e10(arg1, &var_154)",
		'1000830c          char const* const var_168_10 = "unknown match type\\n"',
	):
		assert expected in hlil


def test_qagame_ai_cmd_botlib_match_imports_are_wired() -> None:
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)
	ai_cmd = _read(GAME_AI_CMD)

	assert "BOTLIB_AI_FIND_MATCH," in game_public
	assert "BOTLIB_AI_MATCH_VARIABLE," in game_public
	assert "G_QL_IMPORT_BOTLIB_AI_FIND_MATCH = 130," in game_public
	assert "G_QL_IMPORT_BOTLIB_AI_MATCH_VARIABLE = 131," in game_public

	assert "case BOTLIB_AI_FIND_MATCH: return G_QL_IMPORT_BOTLIB_AI_FIND_MATCH;" in game_syscalls
	assert "case BOTLIB_AI_MATCH_VARIABLE: return G_QL_IMPORT_BOTLIB_AI_MATCH_VARIABLE;" in game_syscalls
	assert "int trap_BotFindMatch(char *str, void /* struct bot_match_s */ *match, unsigned long int context)" in game_syscalls
	assert "void trap_BotMatchVariable(void /* struct bot_match_s */ *match, int variable, char *buf, int size)" in game_syscalls

	assert "[BOTLIB_AI_FIND_MATCH] = (ql_import_f)QL_G_trap_BotFindMatch," in server_game
	assert "[BOTLIB_AI_MATCH_VARIABLE] = (ql_import_f)QL_G_trap_BotMatchVariable," in server_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_FIND_MATCH] = (ql_import_f)QL_G_trap_BotFindMatch;" in server_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MATCH_VARIABLE] = (ql_import_f)QL_G_trap_BotMatchVariable;" in server_game

	assert "static int QDECL QL_G_trap_BotFindMatch( char *str, void /* struct bot_match_s */ *match, unsigned long int context )" in ql_game_imports
	assert "return G_Import_Syscall( BOTLIB_AI_FIND_MATCH, str, match, context );" in ql_game_imports
	assert "static void QDECL QL_G_trap_BotMatchVariable( void /* struct bot_match_s */ *match, int variable, char *buf, int size )" in ql_game_imports
	assert "G_Import_Syscall( BOTLIB_AI_MATCH_VARIABLE, match, variable, buf, size );" in ql_game_imports

	for expected in (
		"trap_BotFindMatch(timestring, &timematch, MTCONTEXT_TIME)",
		"trap_BotFindMatch(keyarea, &keyareamatch, MTCONTEXT_PATROLKEYAREA)",
		"trap_BotFindMatch(addressedto, &addresseematch, MTCONTEXT_ADDRESSEE)",
		"trap_BotFindMatch(match->string, &tellmatch, MTCONTEXT_REPLYCHAT)",
		"trap_BotFindMatch(message, &match, MTCONTEXT_MISC",
		"trap_BotMatchVariable(match, TIME, timestring, MAX_MESSAGE_SIZE);",
		"trap_BotMatchVariable(match, NETNAME, netname, sizeof(netname));",
		"trap_BotMatchVariable(match, KEYAREA, itemname, sizeof(itemname));",
		"trap_BotMatchVariable(match, ENEMY, enemy, sizeof(enemy));",
		"trap_BotMatchVariable(match, FLAG, flag, sizeof(flag));",
	):
		assert expected in ai_cmd
