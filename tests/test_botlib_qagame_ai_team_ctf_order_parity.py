from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_AI_TEAM = REPO_ROOT / "src" / "code" / "game" / "ai_team.c"
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


AI_TEAM_CTF_ORDER_FUNCTIONS = (
	("10025390", "FUN_10025390", "BotNumTeamMates", "int BotNumTeamMates(bot_state_t *bs)", 269),
	("100254a0", "FUN_100254a0", "BotClientTravelTimeToGoal", "int BotClientTravelTimeToGoal(int client, bot_goal_t *goal)", 287),
	("100255c0", "FUN_100255c0", "BotSortTeamMatesByBaseTravelTime", "int BotSortTeamMatesByBaseTravelTime(bot_state_t *bs, int *teammates, int maxteammates)", 500),
	("100257c0", "FUN_100257c0", "BotSetTeamMateTaskPreference", "void BotSetTeamMateTaskPreference(bot_state_t *bs, int teammate, int preference)", 94),
	("10025820", "FUN_10025820", "BotGetTeamMateTaskPreference", "int BotGetTeamMateTaskPreference(bot_state_t *bs, int teammate)", 108),
	("10025890", "FUN_10025890", "BotSortTeamMatesByTaskPreference", "int BotSortTeamMatesByTaskPreference(bot_state_t *bs, int *teammates, int numteammates)", 427),
	("10025a40", "FUN_10025a40", "BotSayTeamOrderAlways", "void BotSayTeamOrderAlways(bot_state_t *bs, int toclient)", 223),
	("10025b20", "FUN_10025b20", "BotVoiceChat", "void BotVoiceChat(bot_state_t *bs, int toclient, char *voicechat)", 70),
	("10025b70", "FUN_10025b70", "BotVoiceChatOnly", "void BotVoiceChatOnly(bot_state_t *bs, int toclient, char *voicechat)", 70),
	("10025bc0", "FUN_10025bc0", "BotCTFOrders_BothFlagsNotAtBase", "void BotCTFOrders_BothFlagsNotAtBase(bot_state_t *bs)", 1463),
	("10026190", "FUN_10026190", "BotCTFOrders_FlagNotAtBase", "void BotCTFOrders_FlagNotAtBase(bot_state_t *bs)", 2111),
	("100269d0", "FUN_100269d0", "BotCTFOrders_EnemyFlagNotAtBase", "void BotCTFOrders_EnemyFlagNotAtBase(bot_state_t *bs)", 1351),
	("10026f20", "FUN_10026f20", "BotCTFOrders_BothFlagsAtBase", "void BotCTFOrders_BothFlagsAtBase(bot_state_t *bs)", 2093),
)


SOURCE_ANCHORS = {
	"BotNumTeamMates": (
		"trap_Cvar_VariableIntegerValue(\"sv_maxclients\")",
		"trap_GetConfigstring(CS_PLAYERS+i, buf, sizeof(buf));",
		"atoi(Info_ValueForKey(buf, PLAYER_INFO_KEY_TEAM)) == TEAM_SPECTATOR",
		"BotSameTeam(bs, i)",
	),
	"BotClientTravelTimeToGoal": (
		"BotAI_GetClientState(client, &ps);",
		"areanum = BotPointAreaNum(ps.origin);",
		"if (!areanum) return 1;",
		"trap_AAS_AreaTravelTimeToGoalArea(areanum, ps.origin, goal->areanum, TFL_DEFAULT)",
	),
	"BotSortTeamMatesByBaseTravelTime": (
		"gametype == GT_CTF || gametype == GT_1FCTF",
		"goal = &ctf_redflag;",
		"goal = &blueobelisk;",
		"trap_Cvar_VariableIntegerValue(\"sv_maxclients\")",
		"traveltime = BotClientTravelTimeToGoal(i, goal);",
		"traveltime < traveltimes[j]",
		"if (numteammates >= maxteammates) break;",
	),
	"BotSetTeamMateTaskPreference": (
		"ctftaskpreferences[teammate].preference = preference;",
		"ClientName(teammate, teammatename, sizeof(teammatename));",
		"strcpy(ctftaskpreferences[teammate].name, teammatename);",
	),
	"BotGetTeamMateTaskPreference": (
		"if (!ctftaskpreferences[teammate].preference) return 0;",
		"ClientName(teammate, teammatename, sizeof(teammatename));",
		"Q_stricmp(teammatename, ctftaskpreferences[teammate].name)",
		"return ctftaskpreferences[teammate].preference;",
	),
	"BotSortTeamMatesByTaskPreference": (
		"preference = BotGetTeamMateTaskPreference(bs, teammates[i]);",
		"preference & TEAMTP_DEFENDER",
		"preference & TEAMTP_ATTACKER",
		"memcpy(&teammates[numteammates], defenders, numdefenders * sizeof(int));",
		"memcpy(&teammates[numteammates], roamers, numroamers * sizeof(int));",
		"memcpy(&teammates[numteammates], attackers, numattackers * sizeof(int));",
	),
	"BotSayTeamOrderAlways": (
		"if (bs->client == toclient)",
		"trap_BotGetChatMessage(bs->cs, buf, sizeof(buf));",
		"Com_sprintf(teamchat, sizeof(teamchat), EC\"(%s\"EC\")\"EC\": %s\", name, buf);",
		"trap_BotQueueConsoleMessage(bs->cs, CMS_CHAT, teamchat);",
		"trap_BotEnterChat(bs->cs, toclient, CHAT_TELL);",
	),
	"BotVoiceChat": (
		"trap_EA_Command(bs->client, va(\"vsay_team %s\", voicechat));",
		"trap_EA_Command(bs->client, va(\"vtell %d %s\", toclient, voicechat));",
	),
	"BotVoiceChatOnly": (
		"trap_EA_Command(bs->client, va(\"vosay_team %s\", voicechat));",
		"trap_EA_Command(bs->client, va(\"votell %d %s\", toclient, voicechat));",
	),
	"BotCTFOrders_BothFlagsNotAtBase": (
		"BotSortTeamMatesByBaseTravelTime(bs, teammates, sizeof(teammates));",
		"BotSortTeamMatesByTaskPreference(bs, teammates, numteammates);",
		"switch(bs->numteammates)",
		"BotAI_BotInitialChat(bs, \"cmd_accompanyme\", name, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_accompany\", name, carriername, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_getflag\", name, NULL);",
		"defenders = (int) (float) numteammates * 0.4 + 0.5;",
		"attackers = (int) (float) numteammates * 0.5 + 0.5;",
		"BotSayVoiceTeamOrder(bs, teammates[numteammates - i - 1], VOICECHAT_RETURNFLAG);",
	),
	"BotCTFOrders_FlagNotAtBase": (
		"BotSortTeamMatesByBaseTravelTime(bs, teammates, sizeof(teammates));",
		"if (!(bs->ctfstrategy & CTFS_AGRESSIVE))",
		"defenders = (int) (float) numteammates * 0.3 + 0.5;",
		"if (defenders > 3) defenders = 3;",
		"attackers = (int) (float) numteammates * 0.7 + 0.5;",
		"if (attackers > 6) attackers = 6;",
		"defenders = (int) (float) numteammates * 0.2 + 0.5;",
		"if (defenders > 2) defenders = 2;",
		"if (attackers > 7) attackers = 7;",
		"BotSayVoiceTeamOrder(bs, teammates[numteammates - i - 1], VOICECHAT_GETFLAG);",
	),
	"BotCTFOrders_EnemyFlagNotAtBase": (
		"BotSortTeamMatesByBaseTravelTime(bs, teammates, sizeof(teammates));",
		"switch(numteammates)",
		"defenders = (int) (float) numteammates * 0.6 + 0.5;",
		"if (defenders > 6) defenders = 6;",
		"attackers = (int) (float) numteammates * 0.3 + 0.5;",
		"if (attackers > 3) attackers = 3;",
		"BotAI_BotInitialChat(bs, \"cmd_accompanyme\", name, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_accompany\", name, carriername, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_getflag\", name, NULL);",
	),
	"BotCTFOrders_BothFlagsAtBase": (
		"BotSortTeamMatesByBaseTravelTime(bs, teammates, sizeof(teammates));",
		"if (!(bs->ctfstrategy & CTFS_AGRESSIVE))",
		"defenders = (int) (float) numteammates * 0.5 + 0.5;",
		"if (defenders > 5) defenders = 5;",
		"attackers = (int) (float) numteammates * 0.4 + 0.5;",
		"if (attackers > 4) attackers = 4;",
		"defenders = (int) (float) numteammates * 0.4 + 0.5;",
		"if (defenders > 4) defenders = 4;",
		"attackers = (int) (float) numteammates * 0.5 + 0.5;",
		"if (attackers > 5) attackers = 5;",
	),
}


HLIL_ENTRY_ANCHORS = (
	"10025390    int32_t sub_10025390(void* arg1)",
	"100254a0    int32_t sub_100254a0(int32_t arg1)",
	"100255c0    int32_t __fastcall sub_100255c0(void* arg1, void* arg2)",
	'100257c0    void* __convention("regparm") sub_100257c0(int32_t arg1, int32_t arg2, int32_t arg3, int32_t arg4)',
	"10025820    int32_t sub_10025820()",
	"10025890    int32_t sub_10025890(int32_t arg1 @ edi, int32_t arg2)",
	"10025a40    int32_t sub_10025a40(int32_t arg1)",
	"10025b20    int32_t __fastcall sub_10025b20(int32_t arg1, void* arg2 @ edi)",
	"10025b70    int32_t __fastcall sub_10025b70(int32_t arg1, void* arg2 @ edi)",
	"10025bc0    int32_t sub_10025bc0(void* arg1)",
	"10026190    int32_t sub_10026190(void* arg1)",
	"100269d0    char* sub_100269d0()",
	"10026f20    int32_t sub_10026f20(void* arg1)",
)


HLIL_FLOW_ANCHORS = (
	'100253c6      (*(data_104b13ac + 0x2c))("sv_maxclients")',
	"10025413          (*(data_104b13ac + 0x68))(i + 0x211, &var_404, 0x400)",
	"10025462                  if (eax_10 != 3 && sub_10018900(eax_10, edx_4, i, arg1) != 0)",
	"100254e6          __builtin_memcpy(dest: &var_288, src: eax_5, n: 0x250)",
	"100255a3  int32_t result = (*(data_104b13ac + 0x134))(eax_6, &var_274, *(ebx + 0xc), 0x11c0fbe)",
	"10025623      int32_t eax_4 = sub_10013b00(arg1)",
	'10025656      (*(data_104b13ac + 0x2c))("sv_maxclients")',
	"1002571f                      int32_t eax_15 = sub_100254a0(i)",
	"100257dc  int32_t ebx_3 = arg4 * 0x28",
	"10025853          && sub_10070a40(esi_4 + 0x105e2080, sub_10015ad0(&var_2c, 0x28, ebx), &var_2c)",
	"10025986          if ((eax_4 & 1) != 0)",
	"100259dc  memcpy(arg1, &var_72c, esi_7)",
	"10025a83  void var_204",
	'10025b32      int32_t eax_1 = sub_10070cb0("vsay_team %s")',
	'10025b4f  int32_t eax_4 = sub_10070cb0("vtell %d %s")',
	'10025b82      int32_t eax_1 = sub_10070cb0("vosay_team %s")',
	'10025b9f  int32_t eax_4 = sub_10070cb0("votell %d %s")',
	"10025be5  int32_t eax_2 = sub_100255c0(arg1, &var_758)",
	"10025bf5  sub_10025890(&var_758, eax_2)",
	'10026100          sub_10020dc0(arg1, "cmd_getflag", &var_658)',
	'10025fea                      sub_10020dc0(arg1, "cmd_accompany", &var_658)',
	'10025fc8                      sub_10020dc0(arg1, "cmd_accompanyme", &var_658)',
	"100261ba  int32_t ebx_1 = sub_100255c0(arg1, &var_630)",
	'1002682a              sub_10020dc0(arg1, "cmd_defendbase", &var_530)',
	"100269f2  int32_t esi = sub_100255c0(ebx, &var_25c)",
	"10026a41              sub_1007b550(fconvert.t(0.59999999999999998) * x87_r7_1 + x87_r5_1)",
	'10026c10                              sub_10020dc0(ebx, "cmd_accompany", &var_15c)',
	'10026bcd                              sub_10020dc0(ebx, "cmd_accompanyme", &var_15c)',
	'10026cef                      sub_10020dc0(ebx, "cmd_getflag", &var_15c)',
	"10026f4a  int32_t ebx_1 = sub_100255c0(arg1, &var_630)",
	'100276a1              sub_10020dc0(arg1, "cmd_defendbase", &var_530)',
	'100276fc              sub_10020dc0(arg1, "cmd_getflag", &var_530)',
	"10027791          return sub_10026f20(arg1)",
	"10027798          return sub_100269d0()",
	"100277a3          return sub_10026190(arg1)",
	"100277a5          return sub_10025bc0(arg1)",
)


GHIDRA_DECOMPILE_ANCHORS = (
	"/* FUN_10025bc0 @ 10025bc0 size 1463 */",
	"uVar2 = FUN_100255c0();",
	"FUN_10025890(uVar2);",
	'FUN_10020dc0(param_1,"cmd_accompanyme",local_658);',
	'FUN_10020dc0(param_1,"cmd_accompany",local_658,local_630,0);',
	"/* FUN_10026190 @ 10026190 size 2111 */",
	'FUN_10020dc0(param_1,"cmd_defendbase",local_530,0);',
	'FUN_10020dc0(param_1,"cmd_getflag",local_530,0);',
	"/* FUN_100269d0 @ 100269d0 size 1351 */",
	'FUN_10070cb0("vtell %d %s",iVar5,"defend");',
	'FUN_10070cb0("vtell %d %s",iVar5,"getflag");',
	"/* FUN_10026f20 @ 10026f20 size 2093 */",
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


def test_qagame_ai_team_ctf_order_aliases_metadata_and_source_are_pinned() -> None:
	ai_team = _read(GAME_AI_TEAM)
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}

	for address, raw_name, normalized_name, signature, size in AI_TEAM_CTF_ORDER_FUNCTIONS:
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

		block = _extract_function_block(ai_team, signature)
		for anchor in SOURCE_ANCHORS[normalized_name]:
			assert anchor in block, normalized_name


def test_qagame_ai_team_ctf_order_hlil_and_ghidra_are_pinned() -> None:
	hlil = _read(QAGAME_HLIL_PART01)
	decompile_top = _read(QAGAME_DECOMPILE_TOP)

	for expected in HLIL_ENTRY_ANCHORS:
		assert expected in hlil

	for expected in HLIL_FLOW_ANCHORS:
		assert expected in hlil

	for expected in GHIDRA_DECOMPILE_ANCHORS:
		assert expected in decompile_top


def test_qagame_ai_team_ctf_order_botlib_import_wiring_is_pinned() -> None:
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)
	ai_team = _read(GAME_AI_TEAM)

	for expected in (
		"G_QL_IMPORT_CVAR_VARIABLE_INTEGER_VALUE = 11,",
		"G_QL_IMPORT_GET_CONFIGSTRING = 26,",
		"G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA = 77,",
		"G_QL_IMPORT_BOTLIB_EA_COMMAND = 87,",
		"G_QL_IMPORT_BOTLIB_AI_QUEUE_CONSOLE_MESSAGE = 119,",
		"G_QL_IMPORT_BOTLIB_AI_INITIAL_CHAT = 123,",
		"G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT = 127,",
		"G_QL_IMPORT_BOTLIB_AI_GET_CHAT_MESSAGE = 128,",
	):
		assert expected in game_public

	for expected in (
		"case G_CVAR_VARIABLE_INTEGER_VALUE: return G_QL_IMPORT_CVAR_VARIABLE_INTEGER_VALUE;",
		"case G_GET_CONFIGSTRING: return G_QL_IMPORT_GET_CONFIGSTRING;",
		"case BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA: return G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA;",
		"case BOTLIB_EA_COMMAND: return G_QL_IMPORT_BOTLIB_EA_COMMAND;",
		"case BOTLIB_AI_QUEUE_CONSOLE_MESSAGE: return G_QL_IMPORT_BOTLIB_AI_QUEUE_CONSOLE_MESSAGE;",
		"case BOTLIB_AI_INITIAL_CHAT: return G_QL_IMPORT_BOTLIB_AI_INITIAL_CHAT;",
		"case BOTLIB_AI_ENTER_CHAT: return G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT;",
		"case BOTLIB_AI_GET_CHAT_MESSAGE: return G_QL_IMPORT_BOTLIB_AI_GET_CHAT_MESSAGE;",
		"return syscall( G_CVAR_VARIABLE_INTEGER_VALUE, var_name );",
		"syscall( G_GET_CONFIGSTRING, num, buffer, bufferSize );",
		"return syscall( BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA, areanum, origin, goalareanum, travelflags );",
		"syscall( BOTLIB_EA_COMMAND, client, command );",
		"syscall( BOTLIB_AI_QUEUE_CONSOLE_MESSAGE, chatstate, type, message );",
		"syscall( BOTLIB_AI_INITIAL_CHAT, chatstate, type, mcontext, var0, var1, var2, var3, var4, var5, var6, var7 );",
		"syscall( BOTLIB_AI_ENTER_CHAT, chatstate, client, sendto );",
		"syscall( BOTLIB_AI_GET_CHAT_MESSAGE, chatstate, buf, size);",
	):
		assert expected in game_syscalls

	for expected in (
		"[G_CVAR_VARIABLE_INTEGER_VALUE] = (ql_import_f)QL_G_trap_Cvar_VariableIntegerValue,",
		"[G_GET_CONFIGSTRING] = (ql_import_f)QL_G_trap_GetConfigstring,",
		"[BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA] = (ql_import_f)QL_G_trap_AAS_AreaTravelTimeToGoalArea,",
		"[BOTLIB_EA_COMMAND] = (ql_import_f)QL_G_trap_EA_Command,",
		"[BOTLIB_AI_QUEUE_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotQueueConsoleMessage,",
		"[BOTLIB_AI_INITIAL_CHAT] = (ql_import_f)QL_G_trap_BotInitialChat,",
		"[BOTLIB_AI_ENTER_CHAT] = (ql_import_f)QL_G_trap_BotEnterChat,",
		"[BOTLIB_AI_GET_CHAT_MESSAGE] = (ql_import_f)QL_G_trap_BotGetChatMessage,",
		"ql_game_imports[G_QL_IMPORT_CVAR_VARIABLE_INTEGER_VALUE] = (ql_import_f)QL_G_trap_Cvar_VariableIntegerValue;",
		"ql_game_imports[G_QL_IMPORT_GET_CONFIGSTRING] = (ql_import_f)QL_G_trap_GetConfigstring;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA] = (ql_import_f)QL_G_trap_AAS_AreaTravelTimeToGoalArea;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_EA_COMMAND] = (ql_import_f)QL_G_trap_EA_Command;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_QUEUE_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotQueueConsoleMessage;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_INITIAL_CHAT] = (ql_import_f)QL_G_trap_BotInitialChat;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT] = (ql_import_f)QL_G_trap_BotEnterChat;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GET_CHAT_MESSAGE] = (ql_import_f)QL_G_trap_BotGetChatMessage;",
	):
		assert expected in server_game

	for expected in (
		"return G_Import_Syscall( G_CVAR_VARIABLE_INTEGER_VALUE, var_name );",
		"G_Import_Syscall( G_GET_CONFIGSTRING, num, buffer, bufferSize );",
		"return G_Import_Syscall( BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA, areanum, origin, goalareanum, travelflags );",
		"G_Import_Syscall( BOTLIB_EA_COMMAND, client, command );",
		"G_Import_Syscall( BOTLIB_AI_QUEUE_CONSOLE_MESSAGE, chatstate, type, message );",
		"G_Import_Syscall( BOTLIB_AI_INITIAL_CHAT, chatstate, type, mcontext, var0, var1, var2, var3, var4, var5, var6, var7 );",
		"G_Import_Syscall( BOTLIB_AI_ENTER_CHAT, chatstate, client, sendto );",
		"G_Import_Syscall( BOTLIB_AI_GET_CHAT_MESSAGE, chatstate, buf, size);",
	):
		assert expected in ql_game_imports

	for expected in (
		"trap_Cvar_VariableIntegerValue(\"sv_maxclients\")",
		"trap_GetConfigstring(CS_PLAYERS+i, buf, sizeof(buf));",
		"trap_AAS_AreaTravelTimeToGoalArea(areanum, ps.origin, goal->areanum, TFL_DEFAULT)",
		"trap_BotGetChatMessage(bs->cs, buf, sizeof(buf));",
		"trap_BotQueueConsoleMessage(bs->cs, CMS_CHAT, teamchat);",
		"trap_BotEnterChat(bs->cs, toclient, CHAT_TELL);",
		"trap_EA_Command(bs->client, va(\"vsay_team %s\", voicechat));",
		"trap_EA_Command(bs->client, va(\"votell %d %s\", toclient, voicechat));",
		"BotAI_BotInitialChat(bs, \"cmd_defendbase\", name, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_accompany\", name, carriername, NULL);",
	):
		assert expected in ai_team
