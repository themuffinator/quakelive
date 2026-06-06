from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOTLIB_DIR = REPO_ROOT / "src" / "code" / "botlib"
BOTLIB_L_PRECOMP = BOTLIB_DIR / "l_precomp.c"
BOTLIB_L_PRECOMP_H = BOTLIB_DIR / "l_precomp.h"
BOTLIB_L_STRUCT = BOTLIB_DIR / "l_struct.c"
BOTLIB_AI_CHAT = BOTLIB_DIR / "be_ai_chat.c"
BOTLIB_AI_CHAR = BOTLIB_DIR / "be_ai_char.c"
BOTLIB_AI_WEIGHT = BOTLIB_DIR / "be_ai_weight.c"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
QL_STEAM_HLIL_PART04 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part04.txt"
)
QL_STEAM_GHIDRA_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
)


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


def _all_botlib_c_text() -> str:
	return "\n".join(path.read_text(encoding="utf-8") for path in BOTLIB_DIR.glob("*.c"))


def test_botlib_precompiler_token_dispatch_matches_retail_references() -> None:
	l_precomp = BOTLIB_L_PRECOMP.read_text(encoding="utf-8")
	l_precomp_h = BOTLIB_L_PRECOMP_H.read_text(encoding="utf-8")
	l_struct = BOTLIB_L_STRUCT.read_text(encoding="utf-8")
	ai_chat = BOTLIB_AI_CHAT.read_text(encoding="utf-8")
	ai_char = BOTLIB_AI_CHAR.read_text(encoding="utf-8")
	ai_weight = BOTLIB_AI_WEIGHT.read_text(encoding="utf-8")
	botlib_c = _all_botlib_c_text()
	ql_steam_hlil = QL_STEAM_HLIL_PART04.read_text(encoding="utf-8")
	ghidra_functions = QL_STEAM_GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	read_token = _extract_function_block(l_precomp, "int PC_ReadToken(source_t *source, token_t *token)")
	expand_into_source = _extract_function_block(
		l_precomp,
		"int PC_ExpandDefineIntoSource(source_t *source, token_t *deftoken, define_t *define)",
	)
	expect_token_string = _extract_function_block(
		l_precomp, "int PC_ExpectTokenString(source_t *source, char *string)"
	)
	expect_token_type = _extract_function_block(
		l_precomp, "int PC_ExpectTokenType(source_t *source, int type, int subtype, token_t *token)"
	)
	expect_any_token = _extract_function_block(
		l_precomp, "int PC_ExpectAnyToken(source_t *source, token_t *token)"
	)
	check_token_string = _extract_function_block(
		l_precomp, "int PC_CheckTokenString(source_t *source, char *string)"
	)
	check_token_type = _extract_function_block(
		l_precomp, "int PC_CheckTokenType(source_t *source, int type, int subtype, token_t *token)"
	)
	skip_until_string = _extract_function_block(
		l_precomp, "int PC_SkipUntilString(source_t *source, char *string)"
	)
	unread_last_token = _extract_function_block(l_precomp, "void PC_UnreadLastToken(source_t *source)")
	unread_token = _extract_function_block(
		l_precomp, "void PC_UnreadToken(source_t *source, token_t *token)"
	)

	for prototype in (
		"int PC_ReadToken(source_t *source, token_t *token);",
		"int PC_ExpectTokenString(source_t *source, char *string);",
		"int PC_ExpectTokenType(source_t *source, int type, int subtype, token_t *token);",
		"int PC_ExpectAnyToken(source_t *source, token_t *token);",
		"int PC_CheckTokenString(source_t *source, char *string);",
		"int PC_CheckTokenType(source_t *source, int type, int subtype, token_t *token);",
		"int PC_SkipUntilString(source_t *source, char *string);",
		"void PC_UnreadLastToken(source_t *source);",
		"void PC_UnreadToken(source_t *source, token_t *token);",
	):
		assert prototype in l_precomp_h

	for snippet in (
		"if (!PC_ReadSourceToken(source, token)) return qfalse;",
		"if (token->type == TT_PUNCTUATION && *token->string == '#')",
		"if (!PC_ReadDirective(source)) return qfalse;",
		"if (token->type == TT_PUNCTUATION && *token->string == '$')",
		"if (!PC_ReadDollarDirective(source)) return qfalse;",
		"if (token->type == TT_STRING)",
		"token_t newtoken;",
		"if (PC_ReadToken(source, &newtoken))",
		"if (newtoken.type == TT_STRING)",
		"token->string[strlen(token->string)-1] = '\\0';",
		"if (strlen(token->string) + strlen(newtoken.string+1) + 1 >= MAX_TOKEN)",
		'SourceError(source, "string longer than MAX_TOKEN %d\\n", MAX_TOKEN);',
		"strcat(token->string, newtoken.string+1);",
		"PC_UnreadToken(source, &newtoken);",
		"if (source->skip) continue;",
		"if (token->type == TT_NAME)",
		"define = PC_FindHashedDefine(source->definehash, token->string);",
		"if (!PC_ExpandDefineIntoSource(source, token, define)) return qfalse;",
		"Com_Memcpy(&source->token, token, sizeof(token_t));",
	):
		assert snippet in read_token

	for snippet in (
		"if (!PC_ExpandDefine(source, deftoken, define, &firsttoken, &lasttoken)) return qfalse;",
		"lasttoken->next = source->tokens;",
		"source->tokens = firsttoken;",
	):
		assert snippet in expand_into_source

	for snippet in (
		'SourceError(source, "couldn\'t find expected %s", string);',
		'SourceError(source, "expected %s, found %s", string, token.string);',
	):
		assert snippet in expect_token_string

	for snippet in (
		'SourceError(source, "couldn\'t read expected token");',
		'if (type == TT_STRING) strcpy(str, "string");',
		'if (type == TT_LITERAL) strcpy(str, "literal");',
		'if (type == TT_NUMBER) strcpy(str, "number");',
		'if (type == TT_NAME) strcpy(str, "name");',
		'if (type == TT_PUNCTUATION) strcpy(str, "punctuation");',
		'SourceError(source, "expected a %s, found %s", str, token->string);',
		"if ((token->subtype & subtype) != subtype)",
		'if (subtype & TT_DECIMAL) strcpy(str, "decimal");',
		'if (subtype & TT_HEX) strcpy(str, "hex");',
		'if (subtype & TT_OCTAL) strcpy(str, "octal");',
		'if (subtype & TT_BINARY) strcpy(str, "binary");',
		'if (subtype & TT_LONG) strcat(str, " long");',
		'if (subtype & TT_UNSIGNED) strcat(str, " unsigned");',
		'if (subtype & TT_FLOAT) strcat(str, " float");',
		'if (subtype & TT_INTEGER) strcat(str, " integer");',
		'SourceError(source, "expected %s, found %s", str, token->string);',
		"else if (token->type == TT_PUNCTUATION)",
		"if (token->subtype != subtype)",
		'SourceError(source, "found %s", token->string);',
	):
		assert snippet in expect_token_type

	assert 'SourceError(source, "couldn\'t read expected token");' in expect_any_token
	assert "if (!strcmp(tok.string, string)) return qtrue;" in check_token_string
	assert "PC_UnreadSourceToken(source, &tok);" in check_token_string
	assert "tok.type == type &&" in check_token_type
	assert "(tok.subtype & subtype) == subtype" in check_token_type
	assert "Com_Memcpy(token, &tok, sizeof(token_t));" in check_token_type
	assert "PC_UnreadSourceToken(source, &tok);" in check_token_type
	assert "while(PC_ReadToken(source, &token))" in skip_until_string
	assert "if (!strcmp(token.string, string)) return qtrue;" in skip_until_string
	assert "PC_UnreadSourceToken(source, &source->token);" in unread_last_token
	assert "PC_UnreadSourceToken(source, token);" in unread_token

	assert len(re.findall(r"\bPC_CheckTokenType\s*\(", botlib_c)) == 1
	assert len(re.findall(r"\bPC_SkipUntilString\s*\(", botlib_c)) == 1
	assert l_precomp.count("PC_UnreadToken(source, &newtoken);") == 1

	for consumer_evidence in (
		"if (!PC_ExpectTokenType(source, TT_STRING, 0, &token)) return 0;",
		"PC_UnreadLastToken(source);",
	):
		assert consumer_evidence in l_struct
	assert "if (!PC_ExpectTokenType(source, TT_NUMBER, 0, &token))" in ai_char
	assert 'if (PC_CheckTokenString(source, "balance"))' in ai_weight
	assert "if (!PC_ExpectAnyToken(source, &token)) return qfalse;" in ai_weight
	assert "if (PC_CheckTokenString(source, \";\")) break;" in ai_chat

	for address, name in (
		("4A8C90", "PC_ReadSourceToken"),
		("4A8DB0", "PC_UnreadSourceToken"),
		("4A9410", "PC_FindHashedDefine"),
		("4A97B0", "PC_ExpandDefine"),
		("4A9B70", "PC_ExpandDefineIntoSource"),
		("4ABC10", "PC_ReadDirective"),
		("4ABF10", "PC_ReadDollarDirective"),
		("4AC030", "PC_UnreadLastToken"),
		("4AC440", "PC_ReadToken"),
		("4AC650", "PC_ExpectTokenString"),
		("4AC710", "PC_ExpectTokenType"),
		("4ACA30", "PC_ExpectAnyToken"),
		("4ACA70", "PC_CheckTokenString"),
		("4ACB10", "PC_ReadTokenHandle"),
	):
		assert aliases[f"sub_{address}"] == name

	for source_reconstruction_name in (
		"PC_CheckTokenType",
		"PC_SkipUntilString",
		"PC_UnreadToken",
	):
		assert source_reconstruction_name not in aliases.values()

	for evidence in (
		"004a9b70    int32_t sub_4a9b70(int32_t arg1, int32_t* arg2, int32_t* arg3)",
		"004a9b95  if (sub_4a97b0(arg1, arg2, arg3, &var_8, &var_c) != 0)",
		"004a9bab              *(eax_2 + 0x428) = *(arg1 + 0x808)",
		"004a9bb1              *(arg1 + 0x808) = ecx_1",
		"004ac030    int32_t sub_4ac030(void* arg1)",
		"004ac03e  sub_4a8db0(arg1, arg1 + 0x820)",
		"004ac440    int32_t sub_4ac440(int32_t arg1, int32_t* arg2)",
		"004ac46e  if (sub_4a8c90(edi, arg2) != 0)",
		"004ac47d          if (ecx_1 != 5)",
		"004ac483              if (i.b != 0x23)",
		"004ac483              else if (sub_4abc10(edi) == 0)",
		"004ac4aa                  if (sub_4abf10(edi) == 0)",
		"004ac4b8              if (ecx_1 == 1 && sub_4ac440(edi, &var_438) != 0)",
		"004ac55a                      sub_4a8db0(edi, &var_438)",
		"004ac518                      if (ecx_2 - &var_436 + eax_8 + 1 u>= 0x400)",
		'004ac603                          sub_4a8ad0(edi, "string longer than MAX_TOKEN %d\\n")',
		"004ac569              if (*(edi + 0x818) == 0)",
		"004ac580                  int32_t* eax_12 = sub_4a9410(*(edi + 0x810), arg2)",
		"004ac5ab                  if (sub_4a97b0(edi, arg2, eax_12, &var_43c, &var_440) == 0)",
		"004ac5c7                  *(eax_14 + 0x428) = *(edi + 0x808)",
		"004ac5cd                  *(edi + 0x808) = ecx_9",
		"004ac62b                      sub_4cb7d0(edi + 0x820, arg2, 0x430)",
		"004ac650    int32_t sub_4ac650(int32_t arg1, char* arg2)",
		"004ac67d  if (sub_4ac440(arg1, &var_438) == 0)",
		'004ac686      sub_4a8ad0(arg1, "couldn\'t find expected %s")',
		'004ac6df  sub_4a8ad0(arg1, "expected %s, found %s")',
		"004ac710    int32_t sub_4ac710(int32_t arg1, int32_t arg2, int32_t arg3, int32_t* arg4)",
		"004ac737  if (sub_4ac440(arg1, arg4) == 0)",
		"004ac759  int32_t eax_4 = arg4[0x100]",
		'004ac788          __builtin_strncpy(dest: &var_408, src: "string", n: 7)',
		'004ac81e          __builtin_strcpy(dest: &var_408, src: "punctuation")',
		"004ac85b  else if ((arg4[0x101] & arg3) != arg3)",
		'004ac9c6      sub_4a8ad0(arg1, "expected %s, found %s")',
		'004ac9f7          sub_4a8ad0(arg1, "found %s")',
		"004aca30    int32_t sub_4aca30(int32_t arg1, int32_t* arg2)",
		"004aca46  if (sub_4ac440(arg1, arg2) != 0)",
		'004aca4e  sub_4a8ad0(arg1, "couldn\'t read expected token")',
		"004aca70    int32_t sub_4aca70(int32_t arg1, char* arg2)",
		"004aca99  if (sub_4ac440(arg1, &var_438) != 0)",
		"004acae9      sub_4a8db0(arg1, &var_438)",
		"004acb10    int32_t sub_4acb10(int32_t arg1, int32_t* arg2)",
		"004acb47          int32_t result = sub_4ac440(eax_3, &var_438)",
	):
		assert evidence in ql_steam_hlil

	for row in (
		"FUN_004a97b0,004a97b0,947,0,unknown",
		"FUN_004a9b70,004a9b70,88,0,unknown",
		"FUN_004ac030,004ac030,24,0,unknown",
		"FUN_004ac440,004ac440,521,0,unknown",
		"FUN_004ac650,004ac650,190,0,unknown",
		"FUN_004ac710,004ac710,790,0,unknown",
		"FUN_004aca30,004aca30,51,0,unknown",
		"FUN_004aca70,004aca70,146,0,unknown",
		"FUN_004acb10,004acb10,163,0,unknown",
	):
		assert row in ghidra_functions
