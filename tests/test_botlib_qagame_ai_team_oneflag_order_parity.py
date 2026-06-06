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


AI_TEAM_ONEFLAG_ORDER_FUNCTIONS = (
	("10027750", "FUN_10027750", "BotCTFOrders", "void BotCTFOrders(bot_state_t *bs)", 95),
	("100277c0", "FUN_100277c0", "BotCreateGroup", "void BotCreateGroup(bot_state_t *bs, int *teammates, int groupsize)", 289),
	("100278f0", "FUN_100278f0", "BotTeamOrders", "void BotTeamOrders(bot_state_t *bs)", 476),
	("10027ae0", "FUN_10027ae0", "Bot1FCTFOrders_FlagAtCenter", "void Bot1FCTFOrders_FlagAtCenter(bot_state_t *bs)", 2104),
	("10028320", "FUN_10028320", "Bot1FCTFOrders_TeamHasFlag", "void Bot1FCTFOrders_TeamHasFlag(bot_state_t *bs)", 2507),
	("10028d10", "FUN_10028d10", "Bot1FCTFOrders_EnemyHasFlag", "void Bot1FCTFOrders_EnemyHasFlag(bot_state_t *bs)", 2107),
	("10029550", "FUN_10029550", "Bot1FCTFOrders_EnemyDroppedFlag", "void Bot1FCTFOrders_EnemyDroppedFlag(bot_state_t *bs)", 2102),
	("10029d90", "FUN_10029d90", "Bot1FCTFOrders", "void Bot1FCTFOrders(bot_state_t *bs)", 61),
)


SOURCE_ANCHORS = {
	"BotCTFOrders": (
		"if (BotTeam(bs) == TEAM_RED) flagstatus = bs->redflagstatus * 2 + bs->blueflagstatus;",
		"else flagstatus = bs->blueflagstatus * 2 + bs->redflagstatus;",
		"case 0: BotCTFOrders_BothFlagsAtBase(bs); break;",
		"case 1: BotCTFOrders_EnemyFlagNotAtBase(bs); break;",
		"case 2: BotCTFOrders_FlagNotAtBase(bs); break;",
		"case 3: BotCTFOrders_BothFlagsNotAtBase(bs); break;",
	),
	"BotCreateGroup": (
		"ClientName(teammates[0], leadername, sizeof(leadername));",
		"for (i = 1; i < groupsize; i++)",
		"if (teammates[0] == bs->client)",
		"BotAI_BotInitialChat(bs, \"cmd_accompanyme\", name, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_accompany\", name, leadername, NULL);",
		"BotSayTeamOrderAlways(bs, teammates[i]);",
	),
	"BotTeamOrders": (
		"static int cachedMaxClients;",
		"trap_Cvar_VariableIntegerValue(\"sv_maxclients\")",
		"trap_GetConfigstring(CS_PLAYERS+i, buf, sizeof(buf));",
		"if (atoi(Info_ValueForKey(buf, PLAYER_INFO_KEY_TEAM)) == TEAM_SPECTATOR) continue;",
		"BotSameTeam(bs, i)",
		"BotCreateGroup(bs, teammates, 2);",
		"BotCreateGroup(bs, &teammates[2], 2);",
		"BotCreateGroup(bs, &teammates[2], 3);",
		"BotCreateGroup(bs, &teammates[i*2], 2);",
	),
	"Bot1FCTFOrders_FlagAtCenter": (
		"BotSortTeamMatesByBaseTravelTime(bs, teammates, sizeof(teammates));",
		"BotSortTeamMatesByTaskPreference(bs, teammates, numteammates);",
		"if (!(bs->ctfstrategy & CTFS_AGRESSIVE))",
		"defenders = (int) (float) numteammates * 0.5 + 0.5;",
		"if (defenders > 5) defenders = 5;",
		"attackers = (int) (float) numteammates * 0.4 + 0.5;",
		"if (attackers > 4) attackers = 4;",
		"defenders = (int) (float) numteammates * 0.3 + 0.5;",
		"if (defenders > 3) defenders = 3;",
		"attackers = (int) (float) numteammates * 0.6 + 0.5;",
		"if (attackers > 6) attackers = 6;",
		"BotAI_BotInitialChat(bs, \"cmd_defendbase\", name, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_getflag\", name, NULL);",
		"BotSayVoiceTeamOrder(bs, teammates[0], VOICECHAT_DEFEND);",
		"BotSayVoiceTeamOrder(bs, teammates[numteammates - i - 1], VOICECHAT_GETFLAG);",
	),
	"Bot1FCTFOrders_TeamHasFlag": (
		"BotSortTeamMatesByBaseTravelTime(bs, teammates, sizeof(teammates));",
		"BotSortTeamMatesByTaskPreference(bs, teammates, numteammates);",
		"if (teammates[0] == bs->flagcarrier) other = teammates[1];",
		"BotAI_BotInitialChat(bs, \"cmd_attackenemybase\", name, NULL);",
		"BotSayVoiceTeamOrder(bs, other, VOICECHAT_OFFENSE);",
		"BotAI_BotInitialChat(bs, \"cmd_accompanyme\", name, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_accompany\", name, carriername, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_getflag\", name, NULL);",
		"defenders = (int) (float) numteammates * 0.3 + 0.5;",
		"if (defenders > 3) defenders = 3;",
		"attackers = (int) (float) numteammates * 0.7 + 0.5;",
		"if (attackers > 7) attackers = 7;",
		"defenders = (int) (float) numteammates * 0.2 + 0.5;",
		"if (defenders > 2) defenders = 2;",
		"attackers = (int) (float) numteammates * 0.8 + 0.5;",
		"if (attackers > 8) attackers = 8;",
	),
	"Bot1FCTFOrders_EnemyHasFlag": (
		"BotSortTeamMatesByBaseTravelTime(bs, teammates, sizeof(teammates));",
		"BotSortTeamMatesByTaskPreference(bs, teammates, numteammates);",
		"BotAI_BotInitialChat(bs, \"cmd_defendbase\", name, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_returnflag\", name, NULL);",
		"defenders = (int) (float) numteammates * 0.8 + 0.5;",
		"if (defenders > 8) defenders = 8;",
		"attackers = (int) (float) numteammates * 0.1 + 0.5;",
		"if (attackers > 2) attackers = 2;",
		"defenders = (int) (float) numteammates * 0.7 + 0.5;",
		"attackers = (int) (float) numteammates * 0.2 + 0.5;",
		"BotSayVoiceTeamOrder(bs, teammates[numteammates - i - 1], VOICECHAT_GETFLAG);",
	),
	"Bot1FCTFOrders_EnemyDroppedFlag": (
		"BotSortTeamMatesByBaseTravelTime(bs, teammates, sizeof(teammates));",
		"BotSortTeamMatesByTaskPreference(bs, teammates, numteammates);",
		"BotAI_BotInitialChat(bs, \"cmd_defendbase\", name, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_getflag\", name, NULL);",
		"defenders = (int) (float) numteammates * 0.5 + 0.5;",
		"if (defenders > 5) defenders = 5;",
		"attackers = (int) (float) numteammates * 0.4 + 0.5;",
		"if (attackers > 4) attackers = 4;",
		"defenders = (int) (float) numteammates * 0.3 + 0.5;",
		"if (defenders > 3) defenders = 3;",
		"attackers = (int) (float) numteammates * 0.6 + 0.5;",
		"if (attackers > 6) attackers = 6;",
		"BotSayVoiceTeamOrder(bs, teammates[numteammates - i - 1], VOICECHAT_DEFEND);",
	),
	"Bot1FCTFOrders": (
		"switch(bs->neutralflagstatus)",
		"case 0: Bot1FCTFOrders_FlagAtCenter(bs); break;",
		"case 1: Bot1FCTFOrders_TeamHasFlag(bs); break;",
		"case 2: Bot1FCTFOrders_EnemyHasFlag(bs); break;",
		"case 3: Bot1FCTFOrders_EnemyDroppedFlag(bs); break;",
	),
}


TEAM_AI_DISPATCH_ANCHORS = (
	"case GT_TEAM:",
	"BotTeamOrders(bs);",
	"case GT_CTF:",
	"BotCTFOrders(bs);",
	"case GT_1FCTF:",
	"Bot1FCTFOrders(bs);",
)


HLIL_ENTRY_ANCHORS = (
	'10027750    int32_t __convention("regparm") sub_10027750(void* arg1)',
	'100277c0    char* __convention("regparm") sub_100277c0(int32_t arg1, int32_t arg2, void* arg3, int32_t* arg4, int32_t arg5)',
	"100278f0    char* sub_100278f0(void* arg1)",
	"10027ae0    int32_t sub_10027ae0(void* arg1)",
	"10028320    int32_t sub_10028320()",
	"10028d10    int32_t sub_10028d10(void* arg1)",
	"10029550    int32_t sub_10029550(void* arg1)",
	'10029d90    int32_t __convention("regparm") sub_10029d90(void* arg1)',
)


HLIL_FLOW_ANCHORS = (
	"1002775c  bool cond:0 = sub_10013b00(arg1) != 1",
	"10027778      result = eax_1 + (*(arg1 + 0x1b2c) << 1)",
	"1002776d      result = *(arg1 + 0x1b2c) + (eax_1 << 1)",
	"10027791          return sub_10026f20(arg1)",
	"10027798          return sub_100269d0()",
	"100277a3          return sub_10026190(arg1)",
	"100277a5          return sub_10025bc0(arg1)",
	"100277f2  char* result = sub_10015ad0(&var_42c, 0x28, eax_2)",
	'10027892              sub_10020dc0(ebx, "cmd_accompanyme", &var_454)',
	'100278ac              sub_10020dc0(ebx, "cmd_accompany", &var_454)',
	"100278b9          result = sub_10025a40(arg4[esi_1])",
	'10027924      (*(data_104b13ac + 0x2c))("sv_maxclients")',
	"10027966          (*(data_104b13ac + 0x68))(i + 0x211, &var_404, 0x400)",
	"100279bd                  if (eax_10 != 3)",
	"100279c2                      eax_11, edx = sub_10018900(eax_10, edx, i, arg1)",
	"100279fd              char* eax_13 = sub_100277c0(&var_504, edx, arg1, &var_504, 2)",
	"10027a6b              char* eax_18 = sub_100277c0(eax_17, edx_3, arg1, &var_4fc, 3)",
	"10027aa6              i_3, edx_4 = sub_100277c0(i_3, edx_4, arg1, esi, 2)",
	"10027b0a  int32_t var_630",
	"10027b0a  int32_t ebx_1 = sub_100255c0(arg1, &var_630)",
	"10027b15  sub_10025890(&var_630, ebx_1)",
	"10027b67              int32_t esi_1 = sub_1007b550(x87_r7_1 * x87_r5_1 + x87_r5_1)",
	"10027b88              result = sub_1007b550(x87_r5_1 + x87_r7_1 * fconvert.t(0.40000000000000002))",
	"10027f2d                  sub_1007b550(fconvert.t(0.29999999999999999) * x87_r7_4 + x87_r5_3)",
	"10027f4e              result = sub_1007b550(x87_r5_3 + x87_r7_4 * fconvert.t(0.59999999999999998))",
	'1002826c              sub_10020dc0(arg1, "cmd_defendbase", &var_530)',
	'100282c8              sub_10020dc0(arg1, "cmd_getflag", &var_530)',
	"10028342  int32_t esi = sub_100255c0(ebx, &var_25c)",
	"1002834d  sub_10025890(&var_25c, esi)",
	"1002839e                  sub_1007b550(fconvert.t(0.29999999999999999) * x87_r7_1 + x87_r5_1)",
	"100283c1                  sub_1007b550(x87_r5_1 + x87_r7_1 * fconvert.t(0.69999999999999996))",
	'10028653                          sub_10020dc0(ebx, "cmd_getflag", &var_15c)',
	'100287b1                          sub_10020dc0(ebx, "cmd_accompanyme", &var_15c)',
	'100287d3                          sub_10020dc0(ebx, "cmd_accompany", &var_15c)',
	'10028875              sub_10020dc0(ebx, "cmd_attackenemybase", &var_15c)',
	"100288df                  sub_1007b550(fconvert.t(0.20000000000000001) * x87_r7_4 + x87_r5_3)",
	"10028902                  sub_1007b550(x87_r5_3 + x87_r7_4 * fconvert.t(0.80000000000000004))",
	"10028d3a  int32_t ebx_1 = sub_100255c0(arg1, &var_630)",
	"10028d45  sub_10025890(&var_630, ebx_1)",
	"10028d9b                  sub_1007b550(fconvert.t(0.80000000000000004) * x87_r7_1 + x87_r5_1)",
	"10028dbc                  sub_1007b550(x87_r5_1 + x87_r7_1 * fconvert.t(0.10000000000000001))",
	'10028e0e                      sub_10020dc0(arg1, "cmd_defendbase", &var_530)',
	'10028f33                      sub_10020dc0(arg1, "cmd_returnflag", &var_530)',
	"1002915b                  sub_1007b550(fconvert.t(0.69999999999999996) * x87_r7_4 + x87_r5_3)",
	"1002917c                  sub_1007b550(x87_r5_3 + x87_r7_4 * fconvert.t(0.20000000000000001))",
	'100292f2                      sub_10020dc0(arg1, "cmd_returnflag", &var_530)',
	'1002944a              sub_10020dc0(arg1, "cmd_returnflag", &var_530)',
	"1002957a  int32_t ebx_1 = sub_100255c0(arg1, &var_630)",
	"10029585  sub_10025890(&var_630, ebx_1)",
	"1002999b                  sub_1007b550(fconvert.t(0.29999999999999999) * x87_r7_4 + x87_r5_3)",
	"100299bc                  sub_1007b550(x87_r5_3 + x87_r7_4 * fconvert.t(0.59999999999999998))",
	'10029d35              sub_10020dc0(arg1, "cmd_getflag", &var_530)',
	"10029daf          return sub_10027ae0(arg1)",
	"10029db6          return sub_10028320()",
	"10029dc1          return sub_10028d10(arg1)",
	"10029dc3          return sub_10029550(arg1)",
)


GHIDRA_DECOMPILE_ANCHORS = (
	"/* FUN_10028320 @ 10028320 size 2507 */",
	"void FUN_10028320(void)",
	"piVar3 = (int *)FUN_100255c0();",
	"FUN_10025890(piVar3);",
	'pcVar5 = "followme";',
	'pcVar5 = "followflagcarrier";',
	'uVar4 = FUN_10070cb0("vtell %d %s",iVar1,"defend");',
	'uVar4 = FUN_10070cb0("vtell %d %s",iVar1,"getflag");',
	"/* FUN_10028d10 @ 10028d10 size 2107 */",
	'FUN_10020dc0(param_1,"cmd_returnflag",local_530,0);',
	"/* FUN_10027ae0 @ 10027ae0 size 2104 */",
	'FUN_10020dc0(param_1,"cmd_defendbase",local_530,0);',
	'FUN_10020dc0(param_1,"cmd_getflag",local_530,0);',
	"/* FUN_10029550 @ 10029550 size 2102 */",
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


def test_qagame_ai_team_oneflag_order_aliases_metadata_and_source_are_pinned() -> None:
	ai_team = _read(GAME_AI_TEAM)
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}

	for address, raw_name, normalized_name, signature, size in AI_TEAM_ONEFLAG_ORDER_FUNCTIONS:
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


def test_qagame_ai_team_oneflag_order_hlil_and_ghidra_are_pinned() -> None:
	hlil = _read(QAGAME_HLIL_PART01)
	decompile_top = _read(QAGAME_DECOMPILE_TOP)

	for expected in HLIL_ENTRY_ANCHORS:
		assert expected in hlil

	for expected in HLIL_FLOW_ANCHORS:
		assert expected in hlil

	for expected in GHIDRA_DECOMPILE_ANCHORS:
		assert expected in decompile_top


def test_qagame_ai_team_oneflag_order_team_ai_and_import_wiring_are_pinned() -> None:
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)
	ai_team = _read(GAME_AI_TEAM)

	for expected in TEAM_AI_DISPATCH_ANCHORS:
		assert expected in ai_team

	for expected in (
		"G_QL_IMPORT_CVAR_VARIABLE_INTEGER_VALUE = 11,",
		"G_QL_IMPORT_GET_CONFIGSTRING = 26,",
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
		"case BOTLIB_EA_COMMAND: return G_QL_IMPORT_BOTLIB_EA_COMMAND;",
		"case BOTLIB_AI_QUEUE_CONSOLE_MESSAGE: return G_QL_IMPORT_BOTLIB_AI_QUEUE_CONSOLE_MESSAGE;",
		"case BOTLIB_AI_INITIAL_CHAT: return G_QL_IMPORT_BOTLIB_AI_INITIAL_CHAT;",
		"case BOTLIB_AI_ENTER_CHAT: return G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT;",
		"case BOTLIB_AI_GET_CHAT_MESSAGE: return G_QL_IMPORT_BOTLIB_AI_GET_CHAT_MESSAGE;",
		"return syscall( G_CVAR_VARIABLE_INTEGER_VALUE, var_name );",
		"syscall( G_GET_CONFIGSTRING, num, buffer, bufferSize );",
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
		"[BOTLIB_EA_COMMAND] = (ql_import_f)QL_G_trap_EA_Command,",
		"[BOTLIB_AI_QUEUE_CONSOLE_MESSAGE] = (ql_import_f)QL_G_trap_BotQueueConsoleMessage,",
		"[BOTLIB_AI_INITIAL_CHAT] = (ql_import_f)QL_G_trap_BotInitialChat,",
		"[BOTLIB_AI_ENTER_CHAT] = (ql_import_f)QL_G_trap_BotEnterChat,",
		"[BOTLIB_AI_GET_CHAT_MESSAGE] = (ql_import_f)QL_G_trap_BotGetChatMessage,",
		"ql_game_imports[G_QL_IMPORT_CVAR_VARIABLE_INTEGER_VALUE] = (ql_import_f)QL_G_trap_Cvar_VariableIntegerValue;",
		"ql_game_imports[G_QL_IMPORT_GET_CONFIGSTRING] = (ql_import_f)QL_G_trap_GetConfigstring;",
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
		"BotAI_BotInitialChat(bs, \"cmd_accompanyme\", name, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_accompany\", name, leadername, NULL);",
		"BotSayTeamOrderAlways(bs, teammates[i]);",
		"BotAI_BotInitialChat(bs, \"cmd_attackenemybase\", name, NULL);",
		"BotAI_BotInitialChat(bs, \"cmd_returnflag\", name, NULL);",
		"BotSayVoiceTeamOrder(bs, teammates[numteammates - i - 1], VOICECHAT_GETFLAG);",
	):
		assert expected in ai_team
