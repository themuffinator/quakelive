from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

BOTLIB_AI_CHAT = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_chat.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
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


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _aliases() -> dict[str, str]:
	return json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	assert start != -1, signature
	brace = text.find("{", start)
	assert brace != -1, signature

	depth = 0
	for offset in range(brace, len(text)):
		if text[offset] == "{":
			depth += 1
		elif text[offset] == "}":
			depth -= 1
			if depth == 0:
				return text[start : offset + 1]

	raise AssertionError(f"unterminated function block: {signature}")


def _assert_function_row(functions_csv: str, address: str, size: int) -> None:
	row = f"FUN_00{address.lower()},00{address.lower()},{size},0,unknown"
	assert row in functions_csv


def _assert_order(text: str, *needles: str) -> None:
	position = -1
	for needle in needles:
		next_position = text.find(needle)
		assert next_position != -1, needle
		assert next_position > position, needle
		position = next_position


def test_chat_private_helper_aliases_and_retail_rows_are_pinned() -> None:
	aliases = _aliases()
	functions = _read(QL_STEAM_FUNCTIONS)
	hlil = _read(QL_STEAM_HLIL_PART03)

	expected_aliases = {
		"497B00": "InitConsoleMessageHeap",
		"497EB0": "BotRemoveTildes",
		"498890": "BotReplaceWeightedSynonyms",
		"498A70": "BotReplaceReplySynonyms",
		"499880": "StringsMatch",
		"4999C0": "BotFindMatch",
		"49B170": "BotConstructChatMessage",
		"49BAE0": "BotReplyChat",
		"49C560": "BotSetupChatAI",
		"49C5F0": "BotShutdownChatAI",
	}
	expected_sizes = {
		"497B00": 208,
		"497EB0": 71,
		"498890": 480,
		"498A70": 316,
		"499880": 303,
		"4999C0": 541,
		"49B170": 858,
		"49BAE0": 1732,
		"49C560": 144,
		"49C5F0": 196,
	}

	for address, name in expected_aliases.items():
		assert aliases[f"sub_{address}"] == name
		_assert_function_row(functions, address, expected_sizes[address])

	for evidence in (
		"00497b00    int32_t sub_497b00()",
		'00497b23  int32_t eax = sub_526000(sub_4a8770("max_messages", "1024"))',
		"00497b33  char* eax_1 = sub_4a8a50(esi_1)",
		"00497bc9  data_e49f80 = result",
		"00497eb0    char* sub_497eb0(char* arg1)",
		"00497edf              memmove(esi + result, esi + result + 1, eax - ebx_1 + 1)",
		"00498890    void sub_498890(char* arg1, int32_t arg2)",
		"00498961                                          int32_t* j = sub_498100(arg1, eax_3, 0)",
		"00498a70    void sub_498a70(int32_t* arg1, char* arg2)",
		"00498ad7                      eax, ecx = sub_498100(esi, *edi_1, 0)",
		"00499880    int32_t sub_499880(int32_t* arg1, void* arg2)",
		"004998cf                  eax_2, ecx = sub_498020(ebx, edx, 0)",
		"0049b3f6          result, ecx_2 = sub_498890(edi_1, arg3)",
		"0049b2af                          sub_498a70(&var_108, arg5)",
		"0049bc6a                              eax_6 = sub_499880(esi_1[2], &var_298)",
		"0049c126                              sub_497eb0(&ebx_1[0xa])",
		"0049c270      sub_497eb0(edi + 0x28)",
		"0049c346  sub_497eb0(eax_1 + 0x28)",
		"0049c5e8  sub_497b00()",
	):
		assert evidence in hlil


def test_chat_private_helper_source_shape_matches_retail_behavior() -> None:
	source = _read(BOTLIB_AI_CHAT)

	init_heap = _extract_function_block(source, "void InitConsoleMessageHeap(void)")
	remove_tildes = _extract_function_block(source, "void BotRemoveTildes(char *message)")
	replace_weighted = _extract_function_block(
		source, "void BotReplaceWeightedSynonyms(char *string, unsigned long int context)"
	)
	replace_reply = _extract_function_block(
		source, "void BotReplaceReplySynonyms(char *string, unsigned long int context)"
	)
	strings_match = _extract_function_block(source, "int StringsMatch(bot_matchpiece_t *pieces, bot_match_t *match)")

	assert "if (consolemessageheap) FreeMemory(consolemessageheap);" in init_heap
	assert 'max_messages = (int) LibVarValue("max_messages", "1024");' in init_heap
	assert "consolemessageheap = (bot_consolemessage_t *) GetClearedHunkMemory(max_messages *" in init_heap
	assert "consolemessageheap[0].prev = NULL;" in init_heap
	assert "consolemessageheap[0].next = &consolemessageheap[1];" in init_heap
	assert "for (i = 1; i < max_messages-1; i++)" in init_heap
	assert "consolemessageheap[i].prev = &consolemessageheap[i - 1];" in init_heap
	assert "consolemessageheap[i].next = &consolemessageheap[i + 1];" in init_heap
	assert "consolemessageheap[max_messages-1].prev = &consolemessageheap[max_messages-2];" in init_heap
	assert "consolemessageheap[max_messages-1].next = NULL;" in init_heap
	assert "freeconsolemessages = consolemessageheap;" in init_heap

	assert "for (i = 0; message[i]; i++)" in remove_tildes
	assert "if (message[i] == '~')" in remove_tildes
	assert "memmove(&message[i], &message[i+1], strlen(&message[i+1])+1);" in remove_tildes

	assert "for (syn = synonyms; syn; syn = syn->next)" in replace_weighted
	assert "if (!(syn->context & context)) continue;" in replace_weighted
	assert "weight = random() * syn->totalweight;" in replace_weighted
	assert "if (!weight) continue;" in replace_weighted
	assert "curweight = 0;" in replace_weighted
	assert "curweight += replacement->weight;" in replace_weighted
	assert "if (weight < curweight) break;" in replace_weighted
	assert "if (!replacement) continue;" in replace_weighted
	assert "if (synonym == replacement) continue;" in replace_weighted
	assert "StringReplaceWords(string, synonym->string, replacement->string);" in replace_weighted

	assert "for (str1 = string; *str1; )" in replace_reply
	assert "while(*str1 && *str1 <= ' ') str1++;" in replace_reply
	assert "if (!(syn->context & context)) continue;" in replace_reply
	assert "str2 = StringContainsWord(str1, synonym->string, qfalse);" in replace_reply
	assert "if (!str2 || str2 != str1) continue;" in replace_reply
	assert "replacement = syn->firstsynonym->string;" in replace_reply
	assert "str2 = StringContainsWord(str1, replacement, qfalse);" in replace_reply
	assert "if (str2 && str2 == str1) continue;" in replace_reply
	assert "memmove(str1 + strlen(replacement), str1+strlen(synonym->string)," in replace_reply
	assert "Com_Memcpy(str1, replacement, strlen(replacement));" in replace_reply
	assert "while(*str1 && *str1 > ' ') str1++;" in replace_reply

	assert "lastvariable = -1;" in strings_match
	assert "strptr = match->string;" in strings_match
	assert "if (mp->type == MT_STRING)" in strings_match
	assert "if (!strlen(ms->string))" in strings_match
	assert "index = StringContains(strptr, ms->string, qfalse);" in strings_match
	assert "match->variables[lastvariable].length =" in strings_match
	assert "strptr = newstrptr + strlen(ms->string);" in strings_match
	assert "else if (mp->type == MT_VARIABLE)" in strings_match
	assert "match->variables[mp->variable].offset = strptr - match->string;" in strings_match
	assert "lastvariable = mp->variable;" in strings_match
	assert "assert( match->variables[lastvariable].offset >= 0 );" in strings_match
	assert "return qtrue;" in strings_match
	assert "return qfalse;" in strings_match


def test_chat_private_helpers_are_wired_through_setup_matching_and_expansion() -> None:
	source = _read(BOTLIB_AI_CHAT)
	interface = _read(BOTLIB_INTERFACE)
	public_api = _read(BOTLIB_PUBLIC)

	setup_chat_ai = _extract_function_block(source, "int BotSetupChatAI(void)")
	shutdown_chat_ai = _extract_function_block(source, "void BotShutdownChatAI(void)")
	find_match = _extract_function_block(source, "int BotFindMatch(char *str, bot_match_t *match, unsigned long int context)")
	expand_message = _extract_function_block(
		source,
		"int BotExpandChatMessage(char *outmessage, char *message, unsigned long mcontext,",
	)
	reply_chat = _extract_function_block(
		source,
		"int BotReplyChat(int chatstate, char *message, int mcontext, int vcontext,",
	)
	enter_chat = _extract_function_block(source, "void BotEnterChat(int chatstate, int clientto, int sendto)")
	get_chat = _extract_function_block(source, "void BotGetChatMessage(int chatstate, char *buf, int size)")
	init_export = _extract_function_block(interface, "static void Init_AI_Export( ai_export_t *ai )")

	_assert_order(
		setup_chat_ai,
		'file = LibVarString("synfile", "syn.c");',
		"synonyms = BotLoadSynonyms(file);",
		'file = LibVarString("rndfile", "rnd.c");',
		"randomstrings = BotLoadRandomStrings(file);",
		'file = LibVarString("matchfile", "match.c");',
		"matchtemplates = BotLoadMatchTemplates(file);",
		'if (!LibVarValue("nochat", "0"))',
		'file = LibVarString("rchatfile", "rchat.c");',
		"replychats = BotLoadReplyChat(file);",
		"InitConsoleMessageHeap();",
	)
	assert "if (consolemessageheap) FreeMemory(consolemessageheap);" in shutdown_chat_ai
	assert "consolemessageheap = NULL;" in shutdown_chat_ai

	assert "if (StringsMatch(ms->first, match))" in find_match
	assert find_match.index("for (i = 0; i < MAX_MATCHVARIABLES; i++)") < find_match.index(
		"if (StringsMatch(ms->first, match))"
	)
	assert "match->type = ms->type;" in find_match
	assert "match->subtype = ms->subtype;" in find_match

	assert "if (reply)" in expand_message
	assert "BotReplaceReplySynonyms(temp, vcontext);" in expand_message
	assert "BotReplaceSynonyms(temp, vcontext);" in expand_message
	assert "BotReplaceWeightedSynonyms(outputbuf, mcontext);" in expand_message
	assert expand_message.index("BotReplaceReplySynonyms(temp, vcontext);") < expand_message.index(
		"BotReplaceWeightedSynonyms(outputbuf, mcontext);"
	)

	assert "BotRemoveTildes(cs->chatmessage);" in reply_chat
	assert "BotRemoveTildes(cs->chatmessage);" in enter_chat
	assert "BotRemoveTildes(cs->chatmessage);" in get_chat
	assert "strcpy(cs->chatmessage, \"\");" in enter_chat
	assert "strcpy(cs->chatmessage, \"\");" in get_chat

	for private_helper in (
		"InitConsoleMessageHeap",
		"BotRemoveTildes",
		"BotReplaceWeightedSynonyms",
		"BotReplaceReplySynonyms",
		"StringsMatch",
	):
		assert private_helper not in public_api
		assert f"ai->{private_helper}" not in init_export

	for public_helper in (
		"BotReplaceSynonyms",
		"BotFindMatch",
		"BotMatchVariable",
		"BotLoadChatFile",
		"BotInitialChat",
		"BotReplyChat",
		"BotEnterChat",
		"BotGetChatMessage",
	):
		assert public_helper in public_api
		assert f"ai->{public_helper} = {public_helper};" in init_export
