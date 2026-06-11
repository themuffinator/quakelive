from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOTLIB_AI_CHAT = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_chat.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
GAME_AI_CHAT = REPO_ROOT / "src" / "code" / "game" / "ai_chat.c"
GAME_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
SERVER_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
QL_STEAM_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
)
QL_STEAM_HLIL_PART03 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part03.txt"
)
QAGAME_HLIL = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil.txt"
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
QAGAME_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "functions.csv"
)
QAGAME_GHIDRA_TOP = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "decompile_top_functions.c"
)
QAGAME_METADATA = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "metadata.txt"
)
QAGAME_IMPORTS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "imports.txt"
)
QAGAME_EXPORTS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "exports.txt"
)
QAGAME_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "qagame.json"


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(text)):
		char = text[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def _function_rows_by_entry(path: Path) -> dict[str, dict[str, str]]:
	with path.open(newline="", encoding="utf-8") as file:
		return {row["entry"].lower(): row for row in csv.DictReader(file)}


CHAT_GHIDRA_ALIAS_ROWS = (
	("497B00", "InitConsoleMessageHeap", 208),
	("497BD0", "BotRemoveConsoleMessage", 221),
	("497CB0", "BotQueueConsoleMessage", 289),
	("497DE0", "BotNextConsoleMessage", 121),
	("497E60", "BotNumConsoleMessages", 75),
	("497EB0", "BotRemoveTildes", 71),
	("497F00", "UnifyWhiteSpaces", 283),
	("498020", "StringContains", 222),
	("498100", "StringContainsWord", 272),
	("498210", "BotLoadSynonyms", 1272),
	("498710", "BotReplaceSynonyms", 376),
	("498890", "BotReplaceWeightedSynonyms", 480),
	("498A70", "BotReplaceReplySynonyms", 316),
	("498BB0", "BotLoadChatMessage", 526),
	("498DD0", "BotLoadRandomStrings", 742),
	("4990D0", "RandomString", 153),
	("499170", "BotFreeMatchPieces", 70),
	("4991C0", "BotLoadMatchPieces", 847),
	("499510", "BotFreeMatchTemplates", 110),
	("499580", "BotLoadMatchTemplates", 753),
	("499880", "StringsMatch", 303),
	("4999C0", "BotFindMatch", 541),
	("499BF0", "BotMatchVariable", 108),
	("499C60", "BotCheckInitialChatIntegrety", 507),
	("499E70", "BotCheckReplyChatIntegrety", 504),
	("49A080", "BotFreeReplyChat", 208),
	("49A160", "BotCheckValidReplyChatKeySet", 553),
	("49A3A0", "BotLoadReplyChat", 1438),
	("49A960", "BotLoadInitialChat", 1487),
	("49AF40", "BotFreeChatFile", 97),
	("49AFB0", "BotLoadChatFile", 437),
	("49B170", "BotConstructChatMessage", 858),
	("49B4D0", "BotChooseInitialChatMessage", 307),
	("49B610", "BotNumInitialChats", 176),
	("49B6C0", "BotInitialChat", 1044),
	("49BAE0", "BotReplyChat", 1732),
	("49C1B0", "BotChatLength", 91),
	("49C210", "BotEnterChat", 229),
	("49C300", "BotGetChatMessage", 109),
	("49C370", "BotSetChatGender", 96),
	("49C3D0", "BotSetChatName", 109),
	("49C480", "BotFreeChatState", 213),
	("49C560", "BotSetupChatAI", 144),
	("49C5F0", "BotShutdownChatAI", 196),
)


def test_botlib_chat_ghidra_alias_bridge_rows_are_pinned() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]
	function_rows = _function_rows_by_entry(QL_STEAM_FUNCTIONS)
	hlil = _read(QL_STEAM_HLIL_PART03)

	for address, name, size in CHAT_GHIDRA_ALIAS_ROWS:
		entry = f"00{address.lower()}"
		fun_key = f"FUN_{entry}"
		row = function_rows[entry]

		assert aliases[f"sub_{address}"] == name
		assert aliases[fun_key] == name
		assert row["name"] == fun_key
		assert int(row["size"]) == size
		assert row["thunk"] == "0"
		assert row["calling_convention"] == "unknown"

	assert aliases["sub_49C440"] == "BotAllocChatState"
	assert "FUN_0049c440" not in aliases
	assert "0049c440" not in function_rows
	assert "0049c440    int32_t sub_49c440()" in hlil
	assert "004a8140  arg1[7] = sub_49c440" in hlil


def test_qagame_bot_chat_prologue_aliases_source_and_hlil_are_pinned() -> None:
	game_chat = _read(GAME_AI_CHAT)
	hlil = _read(QAGAME_HLIL_PART01)
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}
	metadata = _read(QAGAME_METADATA)
	imports = _read(QAGAME_IMPORTS)
	exports = _read(QAGAME_EXPORTS)

	expected_functions = (
		("10001000", "BotNumActivePlayers", "int BotNumActivePlayers(void)", 230),
		("100010f0", "BotIsFirstInRankings", "int BotIsFirstInRankings(bot_state_t *bs)", 332),
		("10001240", "BotIsLastInRankings", "int BotIsLastInRankings(bot_state_t *bs)", 332),
		("10001390", "BotFirstClientInRankings", "char *BotFirstClientInRankings(void)", 340),
		("100014f0", "BotLastClientInRankings", "char *BotLastClientInRankings(void)", 340),
		("10001650", "BotRandomOpponentName", "char *BotRandomOpponentName(bot_state_t *bs)", 372),
		("100017d0", "BotMapTitle", "char *BotMapTitle(void)", 110),
		("10001840", "BotWeaponNameForMeansOfDeath", "char *BotWeaponNameForMeansOfDeath(int mod)", 122),
		("10001930", "BotRandomWeaponName", "char *BotRandomWeaponName(void)", 131),
		("100019e0", "BotVisibleEnemies", "int BotVisibleEnemies(bot_state_t *bs)", 290),
		("10001b10", "BotValidChatPosition", "int BotValidChatPosition(bot_state_t *bs)", 506),
		("10001d10", "BotChat_EnterGame", "int BotChat_EnterGame(bot_state_t *bs)", 374),
		("10001e90", "BotChat_ExitGame", "int BotChat_ExitGame(bot_state_t *bs)", 297),
		("10001fc0", "BotChat_StartLevel", "int BotChat_StartLevel(bot_state_t *bs)", 311),
		("10002100", "BotChat_EndLevel", "int BotChat_EndLevel(bot_state_t *bs)", 587),
		("10002350", "BotChat_Death", "int BotChat_Death(bot_state_t *bs)", 1102),
		("100027a0", "BotChat_Kill", "int BotChat_Kill(bot_state_t *bs)", 665),
		("10002a40", "BotChat_EnemySuicide", "int BotChat_EnemySuicide(bot_state_t *bs)", 326),
		("10002b90", "BotChat_HitTalking", "int BotChat_HitTalking(bot_state_t *bs)", 422),
		("10002d40", "BotChat_HitNoDeath", "int BotChat_HitNoDeath(bot_state_t *bs)", 476),
		("10002f20", "BotChat_HitNoKill", "int BotChat_HitNoKill(bot_state_t *bs)", 421),
		("100030d0", "BotChat_Random", "int BotChat_Random(bot_state_t *bs)", 724),
		("100033b0", "BotChatTime", "float BotChatTime(bot_state_t *bs)", 42),
		("100033f0", "BotChatTest", "void BotChatTest(bot_state_t *bs)", 4693),
	)

	assert "program_name=qagamex86.dll" in metadata
	assert "function_count=1027" in metadata
	assert "import_count=65" in metadata
	assert "export_count=2" in metadata
	assert "MSVCR100.DLL!rand" in imports
	assert "10053120 dllEntry" in exports
	assert "1007af8c entry" in exports

	for address, name, signature, size in expected_functions:
		fun_key = f"FUN_{address}"
		sub_key = f"sub_{address}"
		assert aliases[fun_key] == name
		assert aliases[sub_key] == name

		row = function_rows[address]
		assert row["name"] == fun_key
		assert int(row["size"]) == size
		assert row["thunk"] == "0"

		symbol = symbol_map[f"0x{address}"]
		assert symbol["raw_name"] == fun_key
		assert symbol["normalized_name"] == name
		assert symbol["status"] == "matched"
		assert symbol["signature"] == signature

	source_blocks = {
		name: _extract_function_block(game_chat, signature)
		for _, name, signature, _ in expected_functions
	}

	for expected in (
		'trap_Cvar_VariableIntegerValue("sv_maxclients")',
		"trap_GetConfigstring(CS_PLAYERS+i, buf, sizeof(buf));",
		"Info_ValueForKey(buf, PLAYER_INFO_KEY_NAME)",
		"TEAM_SPECTATOR",
		"return num;",
	):
		assert expected in source_blocks["BotNumActivePlayers"]

	for expected in (
		"score = bs->cur_ps.persistant[PERS_SCORE];",
		"BotAI_GetClientState(i, &ps);",
		"if (score < ps.persistant[PERS_SCORE]) return qfalse;",
	):
		assert expected in source_blocks["BotIsFirstInRankings"]

	for expected in (
		"if (score > ps.persistant[PERS_SCORE]) return qfalse;",
		"return qtrue;",
	):
		assert expected in source_blocks["BotIsLastInRankings"]

	for expected in (
		"bestscore = -999999;",
		"EasyClientName(bestclient, name, 32);",
		"return name;",
	):
		assert expected in source_blocks["BotFirstClientInRankings"]

	for expected in (
		"worstscore = 999999;",
		"if (ps.persistant[PERS_SCORE] < worstscore)",
		"EasyClientName(bestclient, name, 32);",
	):
		assert expected in source_blocks["BotLastClientInRankings"]

	for expected in (
		"if (i == bs->client) continue;",
		"if (BotSameTeam(bs, i)) continue;",
		"count = random() * numopponents;",
		"EasyClientName(opponents[0], name, sizeof(name));",
	):
		assert expected in source_blocks["BotRandomOpponentName"]

	for expected in (
		"trap_GetServerinfo(info, sizeof(info));",
		"SERVERINFO_KEY_MAPNAME",
		"mapname[sizeof(mapname)-1] = '\\0';",
	):
		assert expected in source_blocks["BotMapTitle"]

	for expected in (
		'case MOD_ROCKET_SPLASH: return "Rocket Launcher";',
		'case MOD_PROXIMITY_MINE: return "Proximity Launcher";',
		'case MOD_JUICED: return "Prox mine";',
		'case MOD_GRAPPLE: return "Grapple";',
		'default: return "[unknown weapon]";',
	):
		assert expected in source_blocks["BotWeaponNameForMeansOfDeath"]

	for expected in (
		"rnd = random() * 11.9;",
		'case 10: return "Proximity Launcher";',
		'default: return "BFG10K";',
	):
		assert expected in source_blocks["BotRandomWeaponName"]

	for expected in (
		"BotEntityInfo(i, &entinfo);",
		"if (!entinfo.valid) continue;",
		"if (EntityIsInvisible(&entinfo) && !EntityIsShooting(&entinfo))",
		"if (BotSameTeam(bs, i)) continue;",
		"vis = BotEntityVisible(bs->entitynum, bs->eye, bs->viewangles, 360, i);",
	):
		assert expected in source_blocks["BotVisibleEnemies"]

	for expected in (
		"if (BotIsDead(bs)) return qtrue;",
		"bs->inventory[INVENTORY_QUAD]",
		"CONTENTS_LAVA|CONTENTS_SLIME",
		"MASK_WATER",
		"trap_AAS_PresenceTypeBoundingBox(PRESENCE_CROUCH, mins, maxs);",
		"if (trace.ent != ENTITYNUM_WORLD) return qfalse;",
	):
		assert expected in source_blocks["BotValidChatPosition"]

	for expected in (
		"if (TeamPlayIsOn()) return qfalse;",
		"if (gametype == GT_TOURNAMENT) return qfalse;",
		"CHARACTERISTIC_CHAT_ENTEREXITGAME",
		"if (BotNumActivePlayers() <= 1) return qfalse;",
		"if (!BotValidChatPosition(bs)) return qfalse;",
		'BotAI_BotInitialChat(bs, "game_enter",',
		"bs->chatto = CHAT_ALL;",
	):
		assert expected in source_blocks["BotChat_EnterGame"]

	for expected in (
		'BotAI_BotInitialChat(bs, "game_exit",',
		"BotRandomOpponentName(bs)",
		"BotMapTitle()",
	):
		assert expected in source_blocks["BotChat_ExitGame"]

	for expected in (
		"if (BotIsObserver(bs)) return qfalse;",
		'trap_EA_Command(bs->client, "vtaunt");',
		"CHARACTERISTIC_CHAT_STARTENDLEVEL",
		'BotAI_BotInitialChat(bs, "level_start",',
	):
		assert expected in source_blocks["BotChat_StartLevel"]

	for expected in (
		"if (BotIsFirstInRankings(bs))",
		'trap_EA_Command(bs->client, "vtaunt");',
		'BotAI_BotInitialChat(bs, "level_end_victory",',
		'BotAI_BotInitialChat(bs, "level_end_lose",',
		'BotAI_BotInitialChat(bs, "level_end",',
		"BotLastClientInRankings()",
		"BotFirstClientInRankings()",
	):
		assert expected in source_blocks["BotChat_EndLevel"]

	for expected in (
		'BotAI_BotInitialChat(bs, "death_teammate", name, NULL);',
		'trap_EA_Command(bs->client, "vtaunt");',
		'"death_drown"',
		'"death_slime"',
		'"death_lava"',
		'"death_cratered"',
		'"death_suicide"',
		'"death_telefrag"',
		'trap_BotNumInitialChats(bs->cs, "death_kamikaze")',
		'"death_gauntlet"',
		'"death_rail"',
		'"death_bfg"',
		'"death_insult"',
		'"death_praise"',
	):
		assert expected in source_blocks["BotChat_Death"]

	for expected in (
		"if (!BotValidChatPosition(bs)) return qfalse;",
		"if (BotVisibleEnemies(bs)) return qfalse;",
		'"kill_teammate"',
		'"kill_gauntlet"',
		'"kill_rail"',
		'"kill_telefrag"',
		'trap_BotNumInitialChats(bs->cs, "kill_kamikaze")',
		'"kill_insult"',
		'"kill_praise"',
	):
		assert expected in source_blocks["BotChat_Kill"]

	for expected in (
		'"enemy_suicide"',
		"if (!BotValidChatPosition(bs)) return qfalse;",
		"if (BotVisibleEnemies(bs)) return qfalse;",
	):
		assert expected in source_blocks["BotChat_EnemySuicide"]

	for expected in (
		"lasthurt_client = g_entities[bs->client].client->lasthurt_client;",
		"ClientName(g_entities[bs->client].client->lasthurt_client, name, sizeof(name));",
		'BotAI_BotInitialChat(bs, "hit_talking", name, weap, NULL);',
	):
		assert expected in source_blocks["BotChat_HitTalking"]

	for expected in (
		"if (EntityIsShooting(&entinfo)) return qfalse;",
		"weap = BotWeaponNameForMeansOfDeath(g_entities[bs->client].client->lasthurt_mod);",
		'BotAI_BotInitialChat(bs, "hit_nodeath", name, weap, NULL);',
	):
		assert expected in source_blocks["BotChat_HitNoDeath"]

	for expected in (
		"ClientName(bs->enemy, name, sizeof(name));",
		"weap = BotWeaponNameForMeansOfDeath(g_entities[bs->enemy].client->lasthurt_mod);",
		'BotAI_BotInitialChat(bs, "hit_nokill", name, weap, NULL);',
	):
		assert expected in source_blocks["BotChat_HitNoKill"]

	for expected in (
		"bs->ltgtype == LTG_TEAMHELP",
		"bs->ltgtype == LTG_TEAMACCOMPANY",
		"bs->ltgtype == LTG_RUSHBASE",
		"if (BotVisibleEnemies(bs)) return qfalse;",
		'BotAI_BotInitialChat(bs, "random_misc",',
		'BotAI_BotInitialChat(bs, "random_insult",',
		"BotRandomWeaponName()",
	):
		assert expected in source_blocks["BotChat_Random"]

	assert "CHARACTERISTIC_CHAT_CPM" in source_blocks["BotChatTime"]
	assert "return 2.0;" in source_blocks["BotChatTime"]

	for expected in (
		'trap_BotNumInitialChats(bs->cs, "game_enter")',
		'trap_BotNumInitialChats(bs->cs, "level_end_victory")',
		'trap_BotNumInitialChats(bs->cs, "death_drown")',
		'trap_BotNumInitialChats(bs->cs, "kill_gauntlet")',
		'trap_BotNumInitialChats(bs->cs, "hit_talking")',
		'trap_BotNumInitialChats(bs->cs, "random_misc")',
		"trap_BotEnterChat(bs->cs, 0, CHAT_ALL);",
	):
		assert expected in source_blocks["BotChatTest"]

	for expected in (
		"10001000    int32_t sub_10001000()",
		"100010f0    int32_t sub_100010f0(void* arg1)",
		"10001240    int32_t sub_10001240(void* arg1)",
		"10001390    int32_t sub_10001390()",
		"100014f0    int32_t sub_100014f0()",
		"10001650    int32_t sub_10001650(void* arg1)",
		"100017d0    int32_t sub_100017d0()",
		'10001840    int32_t __convention("regparm") sub_10001840(int32_t arg1)',
		"10001930    int32_t __fastcall sub_10001930(int32_t arg1)",
		"100019e0    int32_t __fastcall sub_100019e0(void* arg1)",
		"10001b10    int32_t __fastcall sub_10001b10(void* arg1)",
		"10001d10    int32_t sub_10001d10(void* arg1 @ esi)",
		"10001e90    int32_t sub_10001e90(void* arg1 @ esi)",
		"10001fc0    int32_t sub_10001fc0(void* arg1 @ esi)",
		"10002100    int32_t sub_10002100(void* arg1 @ esi)",
		"10002350    int32_t sub_10002350(void* arg1 @ esi)",
		"100027a0    int32_t sub_100027a0(void* arg1 @ esi, long double arg2 @ st1)",
		"10002a40    int32_t sub_10002a40(void* arg1 @ esi)",
		"10002b90    int32_t sub_10002b90()",
		"10002d40    int32_t sub_10002d40()",
		"10002f20    int32_t sub_10002f20()",
		"100030d0    int32_t sub_100030d0(void* arg1 @ esi)",
		'100033b0    int32_t __convention("regparm") sub_100033b0(void* arg1)',
		"100033f0    int32_t sub_100033f0(void* arg1 @ esi)",
		"10001ded                      && sub_10001000() s> 1 && sub_10001b10(arg1) != 0)",
		"10001e0a                  sub_100017d0()",
		"10001e1b                  sub_10001650(arg1)",
		"10002194              if (sub_100010f0(arg1) != 0)",
		"1000228e                      if (sub_10001240(arg1) == 0)",
		"100022d5                          int32_t var_44_5 = sub_100014f0()",
		"100022d6                          sub_10001390()",
		"1000285e                      && sub_10001b10(arg1) != 0 && sub_100019e0(arg1) == 0)",
		"10002980                                  \"kill_kamikaze\")",
		"10002afe                      && sub_10001b10(arg1) != 0 && sub_100019e0(arg1) == 0)",
		"10003346                                  int32_t var_44_6 = sub_10001930(ecx_8)",
		"1000335d                                  sub_10001650(arg1)",
		"100033d9  return (*(data_104b13ac + 0x1cc))(*(arg1 + 0x1958), 0x17, 1, 0xfa0)",
		'1000341f  int32_t i_58 = (*(data_104b13ac + 0x1f0))(*(arg1 + 0x1964), "game_enter")',
	):
		assert expected in hlil


def test_botlib_chat_tail_exports_match_retail_hlil_body_shapes() -> None:
	ai_chat = _read(BOTLIB_AI_CHAT)
	hlil = _read(QL_STEAM_HLIL_PART03)
	aliases = json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]

	for address, name in (
		("49B6C0", "BotInitialChat"),
		("49BAE0", "BotReplyChat"),
		("49C1B0", "BotChatLength"),
		("49C210", "BotEnterChat"),
		("49C300", "BotGetChatMessage"),
		("49C370", "BotSetChatGender"),
		("49C3D0", "BotSetChatName"),
	):
		assert aliases[f"sub_{address}"] == name

	chat_length = _extract_function_block(ai_chat, "int BotChatLength(int chatstate)")
	enter_chat = _extract_function_block(ai_chat, "void BotEnterChat(int chatstate, int clientto, int sendto)")
	get_chat = _extract_function_block(ai_chat, "void BotGetChatMessage(int chatstate, char *buf, int size)")
	set_gender = _extract_function_block(ai_chat, "void BotSetChatGender(int chatstate, int gender)")
	set_name = _extract_function_block(ai_chat, "void BotSetChatName(int chatstate, char *name, int client)")

	assert "return strlen(cs->chatmessage);" in chat_length

	assert "BotRemoveTildes(cs->chatmessage);" in enter_chat
	assert 'LibVarGetValue("bot_testichat")' in enter_chat
	assert 'EA_Command(cs->client, va("say_team %s", cs->chatmessage));' in enter_chat
	assert 'EA_Command(cs->client, va("tell %d %s", clientto, cs->chatmessage));' in enter_chat
	assert 'EA_Command(cs->client, va("say %s", cs->chatmessage));' in enter_chat
	assert 'strcpy(cs->chatmessage, "");' in enter_chat

	assert "BotRemoveTildes(cs->chatmessage);" in get_chat
	assert "strncpy(buf, cs->chatmessage, size-1);" in get_chat
	assert "buf[size-1] = '\\0';" in get_chat
	assert 'strcpy(cs->chatmessage, "");' in get_chat

	assert "case CHAT_GENDERFEMALE: cs->gender = CHAT_GENDERFEMALE; break;" in set_gender
	assert "case CHAT_GENDERMALE: cs->gender = CHAT_GENDERMALE; break;" in set_gender
	assert "default: cs->gender = CHAT_GENDERLESS; break;" in set_gender

	assert "cs->client = client;" in set_name
	assert "Com_Memset(cs->name, 0, sizeof(cs->name));" in set_name
	assert "strncpy(cs->name, name, sizeof(cs->name));" in set_name
	assert "cs->name[sizeof(cs->name)-1] = '\\0';" in set_name

	for expected in (
		"0049c1b0    void* sub_49c1b0(int32_t arg1)",
		"0049c1f3  char* eax_4 = eax_1 + 0x28",
		"0049c20a  return eax_4 - &eax_4[1]",
		"0049c210    void* sub_49c210(int32_t arg1, int32_t arg2, int32_t arg3)",
		"0049c27a      st0_1, eax_5 = sub_4a8680(\"bot_testichat\")",
		"0049c2d7          var_14_1 = \"say_team %s\"",
		"0049c2be              int32_t eax_11 = sub_4d9220(\"tell %d %s\")",
		"0049c2ae          var_14_1 = \"say %s\"",
		"0049c300    int32_t sub_49c300(int32_t arg1, int32_t arg2, int32_t arg3)",
		"0049c346  sub_497eb0(eax_1 + 0x28)",
		"0049c357  int32_t result = strncpy(arg2, eax_1 + 0x28, arg3 - 1)",
		"0049c360  *(arg2 + arg3 - 1) = 0",
		"0049c366  *(eax_1 + 0x28) = 0",
		"0049c370    int32_t* sub_49c370(int32_t arg1, int32_t arg2)",
		"0049c3b3  if (arg2 == 1)",
		"0049c3b6  if (arg2 == 2)",
		"0049c3d0    int32_t sub_49c3d0(int32_t arg1, int32_t arg2, int32_t arg3)",
		"0049c41d  *(esi + 4) = arg3",
		"0049c420  sub_4c95e0(esi + 8, 0, 0x20)",
		"0049c42c  int32_t result = strncpy(esi + 8, arg2, 0x20)",
		"0049c436  *(esi + 0x27) = 0",
	):
		assert expected in hlil


def test_botlib_chat_matching_helpers_are_pinned_to_retail_reference_shape() -> None:
	ai_chat = _read(BOTLIB_AI_CHAT)
	hlil = _read(QL_STEAM_HLIL_PART03)
	functions = _read(QL_STEAM_FUNCTIONS)
	aliases = json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]

	for address, name in (
		("497F00", "UnifyWhiteSpaces"),
		("498020", "StringContains"),
		("498100", "StringContainsWord"),
		("4999C0", "BotFindMatch"),
		("499BF0", "BotMatchVariable"),
	):
		assert aliases[f"sub_{address}"] == name

	unify = _extract_function_block(ai_chat, "void UnifyWhiteSpaces(char *string)")
	contains = _extract_function_block(ai_chat, "int StringContains(char *str1, char *str2, int casesensitive)")
	word_contains = _extract_function_block(ai_chat, "char *StringContainsWord(char *str1, char *str2, int casesensitive)")
	find_match = _extract_function_block(ai_chat, "int BotFindMatch(char *str, bot_match_t *match, unsigned long int context)")
	match_var = _extract_function_block(ai_chat, "void BotMatchVariable(bot_match_t *match, int variable, char *buf, int size)")

	assert "while(*ptr && IsWhiteSpace(*ptr)) ptr++;" in unify
	assert "if (oldptr > string && *ptr) *oldptr++ = ' ';" in unify
	assert "if (ptr > oldptr) memmove(oldptr, ptr, strlen(ptr)+1);" in unify

	assert "if (str1 == NULL || str2 == NULL) return -1;" in contains
	assert "len = strlen(str1) - strlen(str2);" in contains
	assert "if (toupper(str1[j]) != toupper(str2[j])) break;" in contains
	assert "if (!str2[j]) return index;" in contains
	assert "return -1;" in contains

	assert "while(*str1 && *str1 != ' ' && *str1 != '.' && *str1 != ',' && *str1 != '!') str1++;" in word_contains
	assert "if (toupper(str1[j]) != toupper(str2[j])) break;" in word_contains
	assert "if (!str2[j])" in word_contains

	assert "strncpy(match->string, str, MAX_MESSAGE_SIZE);" in find_match
	assert "match->string[strlen(match->string)-1] = '\\0';" in find_match
	assert "for (ms = matchtemplates; ms; ms = ms->next)" in find_match
	assert "if (!(ms->context & context)) continue;" in find_match
	assert "for (i = 0; i < MAX_MATCHVARIABLES; i++) match->variables[i].offset = -1;" in find_match
	assert "match->type = ms->type;" in find_match
	assert "match->subtype = ms->subtype;" in find_match

	assert 'botimport.Print(PRT_FATAL, "BotMatchVariable: variable out of range\\n");' in match_var
	assert 'strcpy(buf, "");' in match_var
	assert "if (match->variables[variable].length < size)" in match_var
	assert "strncpy(buf, &match->string[ (int) match->variables[variable].offset], size-1);" in match_var
	assert "buf[size-1] = '\\0';" in match_var

	for expected in (
		"00498020    int32_t sub_498020(char* arg1, char* arg2, int32_t arg3)",
		"00498038  if (arg1 == 0 || arg2 == 0)",
		"004980fd      return 0xffffffff",
		"00498100    char* sub_498100(char* arg1, char* arg2, int32_t arg3)",
		"004981e8                      || eax_6.b == 0x21)",
		"004999c0    int32_t sub_4999c0(int32_t arg1, char* arg2, int32_t arg3)",
		"00499bf0    char* sub_499bf0(int32_t arg1, int32_t arg2, char* arg3, int32_t arg4)",
		"00499c4b      int32_t eax_3 = data_16dd800(4, \"BotMatchVariable: variable out o…\")",
	):
		assert expected in hlil

	assert "FUN_00498020,00498020,222,0,unknown" in functions
	assert "FUN_00498100,00498100,272,0,unknown" in functions


def test_botlib_chat_resource_loaders_are_pinned_to_retail_reference_shape() -> None:
	ai_chat = _read(BOTLIB_AI_CHAT)
	hlil = _read(QL_STEAM_HLIL_PART03)
	functions = _read(QL_STEAM_FUNCTIONS)
	aliases = json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]

	for address, name in (
		("498210", "BotLoadSynonyms"),
		("498DD0", "BotLoadRandomStrings"),
		("4990D0", "RandomString"),
		("499580", "BotLoadMatchTemplates"),
		("49A3A0", "BotLoadReplyChat"),
		("49A960", "BotLoadInitialChat"),
		("49AFB0", "BotLoadChatFile"),
	):
		assert aliases[f"sub_{address}"] == name

	load_synonyms = _extract_function_block(ai_chat, "bot_synonymlist_t *BotLoadSynonyms(char *filename)")
	load_randoms = _extract_function_block(ai_chat, "bot_randomlist_t *BotLoadRandomStrings(char *filename)")
	random_string = _extract_function_block(ai_chat, "char *RandomString(char *name)")
	load_matches = _extract_function_block(ai_chat, "bot_matchtemplate_t *BotLoadMatchTemplates(char *matchfile)")
	load_replies = _extract_function_block(ai_chat, "bot_replychat_t *BotLoadReplyChat(char *filename)")
	load_initial = _extract_function_block(ai_chat, "bot_chat_t *BotLoadInitialChat(char *chatfile, char *chatname)")
	load_chat_file = _extract_function_block(ai_chat, "int BotLoadChatFile(int chatstate, char *chatfile, char *chatname)")

	assert "for (pass = 0; pass < 2; pass++)" in load_synonyms
	assert "if (pass && size) ptr = (char *) GetClearedHunkMemory(size);" in load_synonyms
	assert "PC_SetBaseFolder(BOTFILESBASEFOLDER);" in load_synonyms
	assert "contextstack[contextlevel] = token.intvalue;" in load_synonyms
	assert 'SourceError(source, "more than 32 context levels");' in load_synonyms
	assert 'SourceError(source, "empty string", token.string);' in load_synonyms
	assert 'SourceError(source, "synonym must have at least two entries\\n");' in load_synonyms
	assert 'SourceError(source, "too many }");' in load_synonyms
	assert 'SourceError(source, "missing }");' in load_synonyms

	assert "for (pass = 0; pass < 2; pass++)" in load_randoms
	assert "if (pass && size) ptr = (char *) GetClearedHunkMemory(size);" in load_randoms
	assert 'SourceError(source, "unknown random %s", token.string);' in load_randoms
	assert "while(!PC_CheckTokenString(source, \"}\"))" in load_randoms
	assert "if (!BotLoadChatMessage(source, chatmessagestring))" in load_randoms
	assert "random->numstrings++;" in load_randoms
	assert "randomstring->next = random->firstrandomstring;" in load_randoms

	assert "for (random = randomstrings; random; random = random->next)" in random_string
	assert "if (!strcmp(random->string, name))" in random_string
	assert "i = random() * random->numstrings;" in random_string
	assert "if (--i < 0) break;" in random_string
	assert "return rs->string;" in random_string

	assert "PC_SetBaseFolder(BOTFILESBASEFOLDER);" in load_matches
	assert 'SourceError(source, "expected integer, found %s\\n", token.string);' in load_matches
	assert 'matchtemplate->first = BotLoadMatchPieces(source, "=");' in load_matches
	assert "matchtemplate->type = token.intvalue;" in load_matches
	assert "matchtemplate->subtype = token.intvalue;" in load_matches
	assert '!PC_ExpectTokenString(source, ";")' in load_matches

	assert 'SourceError(source, "expected [, found %s", token.string);' in load_replies
	assert 'if (PC_CheckTokenString(source, "&")) key->flags |= RCKFL_AND;' in load_replies
	assert 'else if (PC_CheckTokenString(source, "!")) key->flags |= RCKFL_NOT;' in load_replies
	assert 'if (PC_CheckTokenString(source, "name")) key->flags |= RCKFL_NAME;' in load_replies
	assert 'else if (PC_CheckTokenString(source, "female")) key->flags |= RCKFL_GENDERFEMALE;' in load_replies
	assert 'else if (PC_CheckTokenString(source, "male")) key->flags |= RCKFL_GENDERMALE;' in load_replies
	assert 'else if (PC_CheckTokenString(source, "it")) key->flags |= RCKFL_GENDERLESS;' in load_replies
	assert 'else if (PC_CheckTokenString(source, "(")) //match key' in load_replies
	assert 'else if (PC_CheckTokenString(source, "<")) //bot names' in load_replies
	assert "BotCheckValidReplyChatKeySet(source, replychat->keys);" in load_replies
	assert "replychat->priority = token.floatvalue;" in load_replies
	assert "chatmessage->time = -2*CHATMESSAGE_RECENTTIME;" in load_replies
	assert 'if (!replychatlist) botimport.Print(PRT_MESSAGE, "no rchats\\n");' in load_replies

	assert "for (pass = 0; pass < 2; pass++)" in load_initial
	assert "if (pass && size) ptr = (char *) GetClearedMemory(size);" in load_initial
	assert 'if (!strcmp(token.string, "chat"))' in load_initial
	assert "if (!Q_stricmp(token.string, chatname))" in load_initial
	assert 'if (strcmp(token.string, "type"))' in load_initial
	assert 'SourceError(source, "expected type found %s\\n", token.string);' in load_initial
	assert "indent = 1;" in load_initial
	assert 'SourceError(source, "unknown definition %s\\n", token.string);' in load_initial
	assert 'botimport.Print(PRT_ERROR, "couldn\'t find chat %s in %s\\n", chatname, chatfile);' in load_initial
	assert 'botimport.Print(PRT_MESSAGE, "loaded %s from %s\\n", chatname, chatfile);' in load_initial

	assert "BotFreeChatFile(chatstate);" in load_chat_file
	assert 'if (!LibVarGetValue("bot_reloadcharacters"))' in load_chat_file
	assert "for( n = 0; n < MAX_CLIENTS; n++ )" in load_chat_file
	assert "if( strcmp( chatfile, ichatdata[n]->filename ) != 0 )" in load_chat_file
	assert "if( strcmp( chatname, ichatdata[n]->chatname ) != 0 )" in load_chat_file
	assert "cs->chat = ichatdata[n]->chat;" in load_chat_file
	assert 'botimport.Print(PRT_FATAL, "ichatdata table full; couldn\'t load chat %s from %s\\n", chatname, chatfile);' in load_chat_file
	assert "cs->chat = BotLoadInitialChat(chatfile, chatname);" in load_chat_file
	assert 'botimport.Print(PRT_FATAL, "couldn\'t load chat %s from %s\\n", chatname, chatfile);' in load_chat_file
	assert "ichatdata[avail]->chat = cs->chat;" in load_chat_file

	for expected in (
		"00498210    char* sub_498210(char* arg1)",
		"00498640          data_16dd800(3, \"counldn't load %s\\n\", edi)",
		"0049865c                      var_4f4_13 = \"more than 32 context levels\"",
		"004986b8                          var_4f4_13 = \"synonym must have at least two e…\"",
		"004986f3          sub_4a8ad0(ebx_1, \"missing }\")",
		"00498dd0    char* sub_498dd0(char* arg1)",
		"00499088                  sub_4a8ad0(eax_4, \"unknown random %s\")",
		"004990d0    int32_t sub_4990d0(char* arg1)",
		"00499133              int32_t eax_6 = sub_526000(float.t(rand() & 0x7fff) / fconvert.t(32767.0)",
		"00499580    char* sub_499580(char* arg1)",
		"00499847              sub_4a8ad0(edi, \"expected integer, found %s\\n\")",
		"0049a3a0    char* sub_49a3a0(char* arg1)",
		"0049a8dc              sub_4a8ad0(edi, \"expected [, found %s\")",
		"0049a4ae              if (sub_4aca70(edi, U\"&\") == 0)",
		"0049a4f4                  if (sub_4aca70(edi, \"female\") != 0)",
		"0049a592                  if (sub_4aca70(edi, U\"<\") != 0)",
		"0049a88d  data_16dd800(1, \"loaded %s\\n\", arg1)",
		"0049a8b3      data_16dd800(1, \"no rchats\\n\")",
		"0049a960    char* sub_49a960(char* arg1, char* arg2)",
		"0049aa30              char const* const ecx_3 = \"chat\"",
		"0049ab3d                          char const* const ecx_8 = \"type\"",
		"0049aeb6                              sub_4a8ad0(eax_6, \"expected type found %s\\n\")",
		"0049af19          data_16dd800(3, \"couldn't find chat %s in %s\\n\", arg2, arg1)",
		"0049ade3  data_16dd800(1, \"loaded %s from %s\\n\", arg2, arg1)",
		"0049afb0    int32_t sub_49afb0(void* arg1, char* arg2, char* arg3)",
		"0049affe          st0, eax_2 = sub_4a8680(\"bot_reloadcharacters\")",
		"0049b0ac              var_1c_1 = \"ichatdata table full; couldn't l…\"",
	):
		assert expected in hlil

	for expected in (
		"FUN_00498210,00498210,1272,0,unknown",
		"FUN_00498dd0,00498dd0,742,0,unknown",
		"FUN_004990d0,004990d0,153,0,unknown",
		"FUN_00499580,00499580,753,0,unknown",
		"FUN_0049a3a0,0049a3a0,1438,0,unknown",
		"FUN_0049a960,0049a960,1487,0,unknown",
		"FUN_0049afb0,0049afb0,437,0,unknown",
	):
		assert expected in functions


def test_botlib_chat_construction_selection_and_lifecycle_match_retail_reference_shape() -> None:
	ai_chat = _read(BOTLIB_AI_CHAT)
	hlil = _read(QL_STEAM_HLIL_PART03)
	functions = _read(QL_STEAM_FUNCTIONS)
	aliases = json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]

	for address, name in (
		("49B170", "BotConstructChatMessage"),
		("49B4D0", "BotChooseInitialChatMessage"),
		("49B610", "BotNumInitialChats"),
		("49C440", "BotAllocChatState"),
		("49C480", "BotFreeChatState"),
		("49C560", "BotSetupChatAI"),
		("49C5F0", "BotShutdownChatAI"),
	):
		assert aliases[f"sub_{address}"] == name

	expand_message = _extract_function_block(
		ai_chat,
		"int BotExpandChatMessage(char *outmessage, char *message, unsigned long mcontext,",
	)
	construct_message = _extract_function_block(
		ai_chat,
		"void BotConstructChatMessage(bot_chatstate_t *chatstate, char *message, unsigned long mcontext,",
	)
	choose_initial = _extract_function_block(ai_chat, "char *BotChooseInitialChatMessage(bot_chatstate_t *cs, char *type)")
	num_initial = _extract_function_block(ai_chat, "int BotNumInitialChats(int chatstate, char *type)")
	alloc_state = _extract_function_block(ai_chat, "int BotAllocChatState(void)")
	free_state = _extract_function_block(ai_chat, "void BotFreeChatState(int handle)")
	setup_chat_ai = _extract_function_block(ai_chat, "int BotSetupChatAI(void)")
	shutdown_chat_ai = _extract_function_block(ai_chat, "void BotShutdownChatAI(void)")

	assert "case 'v': //variable" in expand_message
	assert "num = num * 10 + (*msgptr++) - '0';" in expand_message
	assert "if (num > MAX_MATCHVARIABLES)" in expand_message
	assert "BotReplaceReplySynonyms(temp, vcontext);" in expand_message
	assert "BotReplaceSynonyms(temp, vcontext);" in expand_message
	assert "case 'r': //random" in expand_message
	assert "ptr = RandomString(temp);" in expand_message
	assert 'botimport.Print(PRT_ERROR, "BotConstructChat: unknown random string %s\\n", temp);' in expand_message
	assert "BotReplaceWeightedSynonyms(outputbuf, mcontext);" in expand_message

	assert "strcpy(srcmessage, message);" in construct_message
	assert "for (i = 0; i < 10; i++)" in construct_message
	assert "BotExpandChatMessage(chatstate->chatmessage, srcmessage, mcontext, match, vcontext, reply)" in construct_message
	assert "strcpy(srcmessage, chatstate->chatmessage);" in construct_message
	assert 'botimport.Print(PRT_WARNING, "too many expansions in chat message\\n");' in construct_message
	assert 'botimport.Print(PRT_WARNING, "%s\\n", chatstate->chatmessage);' in construct_message

	assert "chat = cs->chat;" in choose_initial
	assert "for (t = chat->types; t; t = t->next)" in choose_initial
	assert "if (m->time > AAS_Time()) continue;" in choose_initial
	assert "if (numchatmessages <= 0)" in choose_initial
	assert "n = random() * numchatmessages;" in choose_initial
	assert "m->time = AAS_Time() + CHATMESSAGE_RECENTTIME;" in choose_initial
	assert "return m->chatmessage;" in choose_initial

	assert "cs = BotChatStateFromHandle(chatstate);" in num_initial
	assert "for (t = cs->chat->types; t; t = t->next)" in num_initial
	assert 'if (LibVarGetValue("bot_testichat"))' in num_initial
	assert 'botimport.Print(PRT_MESSAGE, "%s has %d chat lines\\n", type, t->numchatmessages);' in num_initial
	assert "return t->numchatmessages;" in num_initial

	assert "for (i = 1; i <= MAX_CLIENTS; i++)" in alloc_state
	assert "botchatstates[i] = GetClearedMemory(sizeof(bot_chatstate_t));" in alloc_state
	assert "return i;" in alloc_state

	assert "if (handle <= 0 || handle > MAX_CLIENTS)" in free_state
	assert 'botimport.Print(PRT_FATAL, "chat state handle %d out of range\\n", handle);' in free_state
	assert 'botimport.Print(PRT_FATAL, "invalid chat state %d\\n", handle);' in free_state
	assert 'if (LibVarGetValue("bot_reloadcharacters"))' in free_state
	assert "for (h = BotNextConsoleMessage(handle, &m); h; h = BotNextConsoleMessage(handle, &m))" in free_state
	assert "BotRemoveConsoleMessage(handle, h);" in free_state
	assert "FreeMemory(botchatstates[handle]);" in free_state
	assert "botchatstates[handle] = NULL;" in free_state

	assert 'file = LibVarString("synfile", "syn.c");' in setup_chat_ai
	assert "synonyms = BotLoadSynonyms(file);" in setup_chat_ai
	assert 'file = LibVarString("rndfile", "rnd.c");' in setup_chat_ai
	assert "randomstrings = BotLoadRandomStrings(file);" in setup_chat_ai
	assert 'file = LibVarString("matchfile", "match.c");' in setup_chat_ai
	assert "matchtemplates = BotLoadMatchTemplates(file);" in setup_chat_ai
	assert 'if (!LibVarValue("nochat", "0"))' in setup_chat_ai
	assert 'file = LibVarString("rchatfile", "rchat.c");' in setup_chat_ai
	assert "replychats = BotLoadReplyChat(file);" in setup_chat_ai
	assert "InitConsoleMessageHeap();" in setup_chat_ai
	assert "return BLERR_NOERROR;" in setup_chat_ai

	assert "for(i = 0; i < MAX_CLIENTS; i++)" in shutdown_chat_ai
	assert "BotFreeChatState(i);" in shutdown_chat_ai
	assert "FreeMemory(ichatdata[i]->chat);" in shutdown_chat_ai
	assert "FreeMemory(ichatdata[i]);" in shutdown_chat_ai
	assert "if (consolemessageheap) FreeMemory(consolemessageheap);" in shutdown_chat_ai
	assert "consolemessageheap = NULL;" in shutdown_chat_ai
	assert "if (matchtemplates) BotFreeMatchTemplates(matchtemplates);" in shutdown_chat_ai
	assert "if (randomstrings) FreeMemory(randomstrings);" in shutdown_chat_ai
	assert "if (synonyms) FreeMemory(synonyms);" in shutdown_chat_ai
	assert "if (replychats) BotFreeReplyChat(replychats);" in shutdown_chat_ai
	assert "replychats = NULL;" in shutdown_chat_ai

	for expected in (
		"0049b170    int32_t sub_49b170(void* arg1, char* arg2, int32_t arg3, char* arg4, char* arg5, int32_t arg6)",
		"0049b1aa  char* edi_1 = arg1 + 0x28",
		"0049b35b                  char* eax_12 = sub_4990d0(&var_108)",
		"0049b46d                          data_16dd800(3, \"BotConstructChat: unknown random…\", &var_108)",
		"0049b49b          *(esp_1 - 4) = \"too many expansions in chat mess…\"",
		"0049b4d0    void sub_49b4d0(int32_t arg1, char* arg2)",
		"0049b4e5  for (void* i = **(arg1 + 0x138); i != 0; i = *(i + 0x28))",
		"0049b5b1                  sub_526000(float.t(var_c_1:4.d) / fconvert.t(32767.0) * float.t(ebx_2))",
		"0049b5ed                              long double x87_r7_11 = sub_486400() + fconvert.t(20.0)",
		"0049b610    int32_t sub_49b610(int32_t arg1, char* arg2)",
		"0049b684          st0, eax_6 = sub_4a8680(\"bot_testichat\")",
		"0049b6a3              data_16dd800(1, \"%s has %d chat lines\\n\", arg2, *(i + 0x20))",
		"0049c440    int32_t sub_49c440()",
		"0049c454  for (int32_t i = 1; i s<= 0x40; i += 1)",
		"0049c464          *((i << 2) + &data_16de340) = sub_4a89d0(0x13c)",
		"0049c480    int32_t* sub_49c480(int32_t arg1)",
		"0049c4bd          st0, eax_3 = sub_4a8680(\"bot_reloadcharacters\")",
		"0049c4e1          i, ecx = sub_497de0(arg1, &var_11c)",
		"0049c4f2              sub_497bd0(arg1, i)",
		"0049c513          int32_t* eax_5 = sub_4a8aa0(*((arg1 << 2) + &data_16de340))",
		"0049c560    int32_t sub_49c560()",
		"0049c57f  data_e49f88 = sub_498210(sub_4a8750(\"synfile\", \"syn.c\"))",
		"0049c599  data_e49f8c = sub_498dd0(sub_4a8750(\"rndfile\", \"rnd.c\"))",
		"0049c5b3  data_e49f84 = sub_499580(sub_4a8750(\"matchfile\", \"match.c\"))",
		"0049c5b8  st0, eax_6 = sub_4a8770(\"nochat\", U\"0\")",
		"0049c5e3      data_e49f90 = sub_49a3a0(sub_4a8750(\"rchatfile\", \"rchat.c\"))",
		"0049c5e8  sub_497b00()",
		"0049c5f0    int32_t* sub_49c5f0()",
		"0049c60c  for (int32_t i = 0; i s< 0x40; i += 1)",
		"0049c600          sub_49c480(i)",
		"0049c637  for (void* i_1 = &data_16de460; i_1 s< &data_16de560; i_1 += 4)",
		"0049c65b      sub_499510(eax_4)",
		"0049c673      sub_4a8aa0(eax_5)",
		"0049c68b      sub_4a8aa0(eax_6)",
		"0049c6a3      result = sub_49a080(result)",
	):
		assert expected in hlil

	for expected in (
		"FUN_0049b170,0049b170,858,0,unknown",
		"FUN_0049b4d0,0049b4d0,307,0,unknown",
		"FUN_0049b610,0049b610,176,0,unknown",
		"FUN_0049c480,0049c480,213,0,unknown",
		"FUN_0049c560,0049c560,144,0,unknown",
		"FUN_0049c5f0,0049c5f0,196,0,unknown",
	):
		assert expected in functions


def test_botlib_chat_export_and_native_import_boundary_stays_split_by_retail_evidence() -> None:
	interface = _read(BOTLIB_INTERFACE)
	botlib_public = _read(BOTLIB_PUBLIC)
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	qagame_hlil = _read(QAGAME_HLIL)
	qagame_ghidra = _read(QAGAME_GHIDRA_TOP)

	init_ai_export = _extract_function_block(interface, "static void Init_AI_Export( ai_export_t *ai )")
	map_native_import = _extract_function_block(game_syscalls, "static int G_MapNativeImport( int arg, const intptr_t *stack )")

	for expected in (
		"ai->BotInitialChat = BotInitialChat;",
		"ai->BotNumInitialChats = BotNumInitialChats;",
		"ai->BotReplyChat = BotReplyChat;",
		"ai->BotChatLength = BotChatLength;",
		"ai->BotEnterChat = BotEnterChat;",
		"ai->BotGetChatMessage = BotGetChatMessage;",
		"ai->StringContains = StringContains;",
		"ai->BotFindMatch = BotFindMatch;",
		"ai->BotMatchVariable = BotMatchVariable;",
		"ai->UnifyWhiteSpaces = UnifyWhiteSpaces;",
		"ai->BotReplaceSynonyms = BotReplaceSynonyms;",
		"ai->BotLoadChatFile = BotLoadChatFile;",
		"ai->BotSetChatGender = BotSetChatGender;",
		"ai->BotSetChatName = BotSetChatName;",
	):
		assert expected in init_ai_export

	for expected in (
		"int\t\t(*BotChatLength)(int chatstate);",
		"void\t(*BotEnterChat)(int chatstate, int client, int sendto);",
		"void\t(*BotGetChatMessage)(int chatstate, char *buf, int size);",
		"int\t\t(*StringContains)(char *str1, char *str2, int casesensitive);",
		"int\t\t(*BotFindMatch)(char *str, struct bot_match_s *match, unsigned long int context);",
		"void\t(*BotMatchVariable)(struct bot_match_s *match, int variable, char *buf, int size);",
		"void\t(*UnifyWhiteSpaces)(char *string);",
		"void\t(*BotSetChatGender)(int chatstate, int gender);",
		"void\t(*BotSetChatName)(int chatstate, char *name, int client);",
	):
		assert expected in botlib_public

	assert "case BOTLIB_AI_ENTER_CHAT: return G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT;" in map_native_import
	assert "case BOTLIB_AI_GET_CHAT_MESSAGE: return G_QL_IMPORT_BOTLIB_AI_GET_CHAT_MESSAGE;" in map_native_import
	assert "case BOTLIB_AI_CHAT_LENGTH: return G_QL_IMPORT_BOTLIB_AI_CHAT_LENGTH;" in map_native_import
	assert "case BOTLIB_AI_STRING_CONTAINS: return G_QL_IMPORT_BOTLIB_AI_STRING_CONTAINS;" in map_native_import
	assert "case BOTLIB_AI_FIND_MATCH: return G_QL_IMPORT_BOTLIB_AI_FIND_MATCH;" in map_native_import
	assert "case BOTLIB_AI_MATCH_VARIABLE: return G_QL_IMPORT_BOTLIB_AI_MATCH_VARIABLE;" in map_native_import
	assert "case BOTLIB_AI_UNIFY_WHITE_SPACES: return G_QL_IMPORT_BOTLIB_AI_UNIFY_WHITE_SPACES;" in map_native_import
	assert "case BOTLIB_AI_SET_CHAT_GENDER: return G_QL_IMPORT_BOTLIB_AI_SET_CHAT_GENDER;" in map_native_import
	assert "case BOTLIB_AI_SET_CHAT_NAME: return G_QL_IMPORT_BOTLIB_AI_SET_CHAT_NAME;" in map_native_import

	assert "G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT = 127," in game_public
	assert "G_QL_IMPORT_BOTLIB_AI_GET_CHAT_MESSAGE = 128," in game_public
	assert "G_QL_IMPORT_BOTLIB_AI_CHAT_LENGTH = 126," in game_public
	assert "G_QL_IMPORT_BOTLIB_AI_STRING_CONTAINS = 129," in game_public
	assert "G_QL_IMPORT_BOTLIB_AI_FIND_MATCH = 130," in game_public
	assert "G_QL_IMPORT_BOTLIB_AI_MATCH_VARIABLE = 131," in game_public
	assert "G_QL_IMPORT_BOTLIB_AI_UNIFY_WHITE_SPACES = 132," in game_public
	assert "G_QL_IMPORT_BOTLIB_AI_SET_CHAT_GENDER = 135," in game_public
	assert "G_QL_IMPORT_BOTLIB_AI_SET_CHAT_NAME = 136," in game_public

	assert "[BOTLIB_AI_CHAT_LENGTH] = (ql_import_f)QL_G_trap_BotChatLength," in server_game
	assert "[BOTLIB_AI_STRING_CONTAINS] = (ql_import_f)QL_G_trap_StringContains," in server_game
	assert "[BOTLIB_AI_ENTER_CHAT] = (ql_import_f)QL_G_trap_BotEnterChat," in server_game
	assert "[BOTLIB_AI_GET_CHAT_MESSAGE] = (ql_import_f)QL_G_trap_BotGetChatMessage," in server_game

	assert "(*(data_104b13ac + 0x1fc))" in qagame_hlil
	assert "(*(data_104b13ac + 0x200))" in qagame_hlil
	assert "(*(data_104b13ac + 0x1f8))" not in qagame_hlil
	assert "(*(data_104b13ac + 0x204))" not in qagame_hlil
	assert "(**(code **)(DAT_104b13ac + 0x1fc))" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x200))" in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x1f8))" not in qagame_ghidra
	assert "(**(code **)(DAT_104b13ac + 0x204))" not in qagame_ghidra
