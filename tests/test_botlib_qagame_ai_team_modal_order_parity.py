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


AI_TEAM_MODAL_ORDER_FUNCTIONS = (
	("10029df0", "FUN_10029df0", "BotObeliskOrders", "void BotObeliskOrders(bot_state_t *bs)", 2102),
	("1002a630", "FUN_1002a630", "BotHarvesterOrders", "void BotHarvesterOrders(bot_state_t *bs)", 2102),
	("1002ae70", "FUN_1002ae70", "FindHumanTeamLeader", "int FindHumanTeamLeader(bot_state_t *bs)", 125),
	("1002aef0", "FUN_1002aef0", "BotTeamAI", "void BotTeamAI(bot_state_t *bs)", 2710),
)


SOURCE_ANCHORS = {
	"BotObeliskOrders": (
		"BotSortTeamMatesByBaseTravelTime(bs, teammates, sizeof(teammates));",
		"BotSortTeamMatesByTaskPreference(bs, teammates, numteammates);",
		"BotAI_BotInitialChat(bs, \"cmd_defendbase\", name, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_attackenemybase\", name, NULL);",
		"BotSayVoiceTeamOrder(bs, teammates[0], VOICECHAT_DEFEND);",
		"BotSayVoiceTeamOrder(bs, teammates[1], VOICECHAT_OFFENSE);",
		"defenders = (int) (float) numteammates * 0.5 + 0.5;",
		"if (defenders > 5) defenders = 5;",
		"attackers = (int) (float) numteammates * 0.4 + 0.5;",
		"if (attackers > 4) attackers = 4;",
		"defenders = (int) (float) numteammates * 0.3 + 0.5;",
		"if (defenders > 3) defenders = 3;",
		"attackers = (int) (float) numteammates * 0.7 + 0.5;",
		"if (attackers > 7) attackers = 7;",
	),
	"BotHarvesterOrders": (
		"BotSortTeamMatesByBaseTravelTime(bs, teammates, sizeof(teammates));",
		"BotSortTeamMatesByTaskPreference(bs, teammates, numteammates);",
		"BotAI_BotInitialChat(bs, \"cmd_defendbase\", name, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_harvest\", name, NULL);",
		"BotSayVoiceTeamOrder(bs, teammates[0], VOICECHAT_DEFEND);",
		"BotSayVoiceTeamOrder(bs, teammates[1], VOICECHAT_OFFENSE);",
		"defenders = (int) (float) numteammates * 0.5 + 0.5;",
		"if (defenders > 5) defenders = 5;",
		"attackers = (int) (float) numteammates * 0.4 + 0.5;",
		"if (attackers > 4) attackers = 4;",
		"defenders = (int) (float) numteammates * 0.3 + 0.5;",
		"if (defenders > 3) defenders = 3;",
		"attackers = (int) (float) numteammates * 0.7 + 0.5;",
		"if (attackers > 7) attackers = 7;",
	),
	"FindHumanTeamLeader": (
		"for (i = 0; i < MAX_CLIENTS; i++)",
		"if ( g_entities[i].inuse )",
		"if ( !(g_entities[i].r.svFlags & SVF_BOT) )",
		"if (!notleader[i])",
		"if ( BotSameTeam(bs, i) )",
		"ClientName(i, bs->teamleader, sizeof(bs->teamleader));",
		"if ( !BotSetLastOrderedTask(bs) )",
		"BotVoiceChat_Defend(bs, i, SAY_TELL);",
		"return qtrue;",
		"return qfalse;",
	),
	"BotTeamAI": (
		"if ( gametype < GT_TEAM  )",
		"if (!BotValidTeamLeader(bs))",
		"if (!FindHumanTeamLeader(bs))",
		"bs->askteamleader_time = FloatTime() + 5 + random() * 10;",
		"bs->becometeamleader_time = FloatTime() + 8 + random() * 10;",
		"BotAI_BotInitialChat(bs, \"whoisteamleader\", NULL);",
		"BotAI_BotInitialChat(bs, \"iamteamleader\", NULL);",
		"trap_BotEnterChat(bs->cs, 0, CHAT_TEAM);",
		"BotSayVoiceTeamOrder(bs, -1, VOICECHAT_STARTLEADER);",
		"Q_strncpyz(bs->teamleader, netname, sizeof(bs->teamleader));",
		"if (Q_stricmp(netname, bs->teamleader) != 0) return;",
		"numteammates = BotNumTeamMates(bs);",
		"case GT_TEAM:",
		"BotTeamOrders(bs);",
		"bs->teamgiveorders_time = FloatTime() + 120;",
		"case GT_CTF:",
		"BotCTFOrders(bs);",
		"bs->teamgiveorders_time = 0;",
		"case GT_1FCTF:",
		"Bot1FCTFOrders(bs);",
		"case GT_OBELISK:",
		"BotObeliskOrders(bs);",
		"bs->teamgiveorders_time = FloatTime() + 30;",
		"case GT_HARVESTER:",
		"BotHarvesterOrders(bs);",
	),
}


HLIL_ENTRY_ANCHORS = (
	"10029df0    int32_t sub_10029df0(void* arg1)",
	"1002a630    int32_t sub_1002a630(void* arg1)",
	'1002ae70    int32_t __convention("regparm") sub_1002ae70(void* arg1)',
	"1002aef0    void sub_1002aef0(void* arg1)",
)


HLIL_FLOW_ANCHORS = (
	"10029e1a  int32_t ebx_1 = sub_100255c0(arg1, &var_630)",
	"10029e25  sub_10025890(&var_630, ebx_1)",
	"10029e77              int32_t esi_1 = sub_1007b550(x87_r7_1 * x87_r5_1 + x87_r5_1)",
	"10029e98              result = sub_1007b550(x87_r5_1 + x87_r7_1 * fconvert.t(0.40000000000000002))",
	"1002a23b                  sub_1007b550(fconvert.t(0.29999999999999999) * x87_r7_4 + x87_r5_3)",
	"1002a25c                  sub_1007b550(x87_r5_3 + x87_r7_4 * fconvert.t(0.69999999999999996))",
	'1002a013                      sub_10020dc0(arg1, "cmd_attackenemybase", &var_530)',
	'1002a5d5              sub_10020dc0(arg1, "cmd_attackenemybase", &var_530)',
	"1002a65a  int32_t ebx_1 = sub_100255c0(arg1, &var_630)",
	"1002a665  sub_10025890(&var_630, ebx_1)",
	"1002aa7b                  sub_1007b550(fconvert.t(0.29999999999999999) * x87_r7_4 + x87_r5_3)",
	"1002aa9c                  sub_1007b550(x87_r5_3 + x87_r7_4 * fconvert.t(0.69999999999999996))",
	'1002a853                      sub_10020dc0(arg1, "cmd_harvest", &var_530)',
	'1002ae15              sub_10020dc0(arg1, "cmd_harvest", &var_530)',
	"1002aeb1  for (void* i = &data_104b4180; i s< 0x104c2280; )",
	"1002ae93      if (*(i + 0x60) != 0 && (*i & 8) == 0 && *((ebp << 2) + &data_105e9de0) == 0)",
	"1002ae98          arg1, edx = sub_10018900(arg1, edx, ebp, ebx)",
	"1002aec6              sub_10015ad0(ebx + 0x1af4, 0x20, ebp)",
	"1002aed6              if (sub_10013e20() == 0)",
	"1002aedc                  sub_1002bbc0(ebx, ebp)",
	"1002af1b  if (eax_2 s>= 3 && data_10595d2c == 0)",
	"1002b38f              eax_25 = sub_1002ae70(arg1)",
	'1002b48a                      sub_10020dc0(arg1, "whoisteamleader", 0)',
	'1002b522                  sub_10020dc0(arg1, "iamteamleader", 0)',
	'1002b54b                  char const* const var_54_4 = "startleader"',
	"1002b5f6                  int32_t eax_36 = sub_10025390(arg1)",
	"1002b67d                              sub_100278f0(arg1)",
	"1002b691                                  fconvert.s(fconvert.t(data_105e2ef8) + fconvert.t(120.0))",
	"1002b77b                              sub_10027750(arg1)",
	"1002b86f                              sub_10029d90(arg1)",
	"1002b8df                              sub_10029df0(arg1)",
	"1002b8f3                                  fconvert.s(fconvert.t(data_105e2ef8) + fconvert.t(30.0))",
	"1002b96a                              sub_1002a630(arg1)",
)


GHIDRA_DECOMPILE_ANCHORS = (
	"/* FUN_10029df0 @ 10029df0 size 2102 */",
	'FUN_10020dc0(param_1,"cmd_attackenemybase",local_530,0);',
	'uVar3 = FUN_10070cb0("vtell %d %s",uVar2,"offense");',
	"/* FUN_1002a630 @ 1002a630 size 2102 */",
	'FUN_10020dc0(param_1,"cmd_harvest",local_530,0);',
	"/* FUN_1002aef0 @ 1002aef0 size 2710 */",
	'FUN_10020dc0(param_1,"whoisteamleader",0);',
	'FUN_10020dc0(param_1,"iamteamleader",0);',
	'uVar10 = FUN_10070cb0("vsay_team %s","startleader");',
	"iVar7 = FUN_10025390(param_1);",
	"FUN_100278f0(param_1);",
	"FUN_10027750();",
	"FUN_10029d90();",
	"FUN_10029df0(param_1);",
	"FUN_1002a630(param_1);",
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


def test_qagame_ai_team_modal_order_aliases_metadata_and_source_are_pinned() -> None:
	ai_team = _read(GAME_AI_TEAM)
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}

	for address, raw_name, normalized_name, signature, size in AI_TEAM_MODAL_ORDER_FUNCTIONS:
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


def test_qagame_ai_team_modal_order_hlil_and_ghidra_are_pinned() -> None:
	hlil = _read(QAGAME_HLIL_PART01)
	decompile_top = _read(QAGAME_DECOMPILE_TOP)

	for expected in HLIL_ENTRY_ANCHORS:
		assert expected in hlil

	for expected in HLIL_FLOW_ANCHORS:
		assert expected in hlil

	for expected in GHIDRA_DECOMPILE_ANCHORS:
		assert expected in decompile_top


def test_qagame_ai_team_modal_order_import_wiring_is_pinned() -> None:
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)
	ai_team = _read(GAME_AI_TEAM)

	for expected in (
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
		"case G_GET_CONFIGSTRING: return G_QL_IMPORT_GET_CONFIGSTRING;",
		"case BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA: return G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA;",
		"case BOTLIB_EA_COMMAND: return G_QL_IMPORT_BOTLIB_EA_COMMAND;",
		"case BOTLIB_AI_QUEUE_CONSOLE_MESSAGE: return G_QL_IMPORT_BOTLIB_AI_QUEUE_CONSOLE_MESSAGE;",
		"case BOTLIB_AI_INITIAL_CHAT: return G_QL_IMPORT_BOTLIB_AI_INITIAL_CHAT;",
		"case BOTLIB_AI_ENTER_CHAT: return G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT;",
		"case BOTLIB_AI_GET_CHAT_MESSAGE: return G_QL_IMPORT_BOTLIB_AI_GET_CHAT_MESSAGE;",
		"syscall( G_GET_CONFIGSTRING, num, buffer, bufferSize );",
		"return syscall( BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA, areanum, origin, goalareanum, travelflags );",
		"syscall( BOTLIB_EA_COMMAND, client, command );",
		"syscall( BOTLIB_AI_INITIAL_CHAT, chatstate, type, mcontext, var0, var1, var2, var3, var4, var5, var6, var7 );",
		"syscall( BOTLIB_AI_ENTER_CHAT, chatstate, client, sendto );",
	):
		assert expected in game_syscalls

	for expected in (
		"[G_GET_CONFIGSTRING] = (ql_import_f)QL_G_trap_GetConfigstring,",
		"[BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA] = (ql_import_f)QL_G_trap_AAS_AreaTravelTimeToGoalArea,",
		"[BOTLIB_EA_COMMAND] = (ql_import_f)QL_G_trap_EA_Command,",
		"[BOTLIB_AI_INITIAL_CHAT] = (ql_import_f)QL_G_trap_BotInitialChat,",
		"[BOTLIB_AI_ENTER_CHAT] = (ql_import_f)QL_G_trap_BotEnterChat,",
		"ql_game_imports[G_QL_IMPORT_GET_CONFIGSTRING] = (ql_import_f)QL_G_trap_GetConfigstring;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA] = (ql_import_f)QL_G_trap_AAS_AreaTravelTimeToGoalArea;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_EA_COMMAND] = (ql_import_f)QL_G_trap_EA_Command;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_INITIAL_CHAT] = (ql_import_f)QL_G_trap_BotInitialChat;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT] = (ql_import_f)QL_G_trap_BotEnterChat;",
	):
		assert expected in server_game

	for expected in (
		"G_Import_Syscall( G_GET_CONFIGSTRING, num, buffer, bufferSize );",
		"return G_Import_Syscall( BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA, areanum, origin, goalareanum, travelflags );",
		"G_Import_Syscall( BOTLIB_EA_COMMAND, client, command );",
		"G_Import_Syscall( BOTLIB_AI_INITIAL_CHAT, chatstate, type, mcontext, var0, var1, var2, var3, var4, var5, var6, var7 );",
		"G_Import_Syscall( BOTLIB_AI_ENTER_CHAT, chatstate, client, sendto );",
	):
		assert expected in ql_game_imports

	for expected in (
		"BotSortTeamMatesByBaseTravelTime(bs, teammates, sizeof(teammates));",
		"BotAI_BotInitialChat(bs, \"cmd_attackenemybase\", name, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_harvest\", name, NULL);",
		"BotAI_BotInitialChat(bs, \"whoisteamleader\", NULL);",
		"BotAI_BotInitialChat(bs, \"iamteamleader\", NULL);",
		"trap_BotEnterChat(bs->cs, 0, CHAT_TEAM);",
		"BotSayVoiceTeamOrder(bs, -1, VOICECHAT_STARTLEADER);",
	):
		assert expected in ai_team
