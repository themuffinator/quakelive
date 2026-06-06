from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOTLIB_L_PRECOMP = REPO_ROOT / "src" / "code" / "botlib" / "l_precomp.c"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
QL_STEAM_HLIL_PART03 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part03.txt"
)
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


def test_botlib_precompiler_macro_expansion_matches_retail_references() -> None:
	l_precomp = BOTLIB_L_PRECOMP.read_text(encoding="utf-8")
	ql_steam_hlil = (
		QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
		+ "\n"
		+ QL_STEAM_HLIL_PART04.read_text(encoding="utf-8")
	)
	ghidra_functions = QL_STEAM_GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	read_define_parms = _extract_function_block(
		l_precomp, "int PC_ReadDefineParms(source_t *source, define_t *define, token_t **parms, int maxparms)"
	)
	stringize_tokens = _extract_function_block(l_precomp, "int PC_StringizeTokens(token_t *tokens, token_t *token)")
	merge_tokens = _extract_function_block(l_precomp, "int PC_MergeTokens(token_t *t1, token_t *t2)")
	name_hash = _extract_function_block(l_precomp, "int PC_NameHash(char *name)")
	add_define_to_hash = _extract_function_block(
		l_precomp, "void PC_AddDefineToHash(define_t *define, define_t **definehash)"
	)
	find_hashed_define = _extract_function_block(
		l_precomp, "define_t *PC_FindHashedDefine(define_t **definehash, char *name)"
	)
	find_define_parm = _extract_function_block(l_precomp, "int PC_FindDefineParm(define_t *define, char *name)")
	free_define = _extract_function_block(l_precomp, "void PC_FreeDefine(define_t *define)")
	add_builtin_defines = _extract_function_block(l_precomp, "void PC_AddBuiltinDefines(source_t *source)")
	expand_builtin_define = _extract_function_block(
		l_precomp,
		"int PC_ExpandBuiltinDefine(source_t *source, token_t *deftoken, define_t *define,",
	)
	expand_define = _extract_function_block(
		l_precomp,
		"int PC_ExpandDefine(source_t *source, token_t *deftoken, define_t *define,",
	)
	expand_into_source = _extract_function_block(
		l_precomp, "int PC_ExpandDefineIntoSource(source_t *source, token_t *deftoken, define_t *define)"
	)
	directive_define = _extract_function_block(l_precomp, "int PC_Directive_define(source_t *source)")
	evaluate = _extract_function_block(
		l_precomp, "int PC_Evaluate(source_t *source, signed long int *intvalue,"
	)
	dollar_evaluate = _extract_function_block(
		l_precomp, "int PC_DollarEvaluate(source_t *source, signed long int *intvalue,"
	)
	read_token = _extract_function_block(l_precomp, "int PC_ReadToken(source_t *source, token_t *token)")

	for snippet in (
		"if (!PC_ReadSourceToken(source, &token))",
		'SourceError(source, "define %s missing parms", define->name);',
		"if (define->numparms > maxparms)",
		'SourceError(source, "define with more than %d parameters", maxparms);',
		"for (i = 0; i < define->numparms; i++) parms[i] = NULL;",
		'if (strcmp(token.string, "("))',
		"PC_UnreadSourceToken(source, &token);",
		"for (done = 0, numparms = 0, indent = 0; !done;)",
		"if (numparms >= maxparms)",
		'SourceError(source, "define %s with too many parms", define->name);',
		"if (numparms >= define->numparms)",
		'SourceWarning(source, "define %s has too many parms", define->name);',
		"lastcomma = 1;",
		"if (!PC_ReadSourceToken(source, &token))",
		'SourceError(source, "define %s incomplete", define->name);',
		'if (!strcmp(token.string, ","))',
		"if (indent <= 0)",
		'if (lastcomma) SourceWarning(source, "too many comma\'s");',
		'if (!strcmp(token.string, "("))',
		"indent++;",
		'else if (!strcmp(token.string, ")"))',
		"if (--indent <= 0)",
		'SourceWarning(source, "too few define parms");',
		"t = PC_CopyToken(&token);",
		"if (last) last->next = t;",
		"else parms[numparms] = t;",
	):
		assert snippet in read_define_parms

	for snippet in (
		"token->type = TT_STRING;",
		"token->whitespace_p = NULL;",
		"token->endwhitespace_p = NULL;",
		"token->string[0] = '\\0';",
		'strcat(token->string, "\\"");',
		"for (t = tokens; t; t = t->next)",
		"strncat(token->string, t->string, MAX_TOKEN - strlen(token->string));",
		'strncat(token->string, "\\"", MAX_TOKEN - strlen(token->string));',
	):
		assert snippet in stringize_tokens

	for snippet in (
		"if (t1->type == TT_NAME && (t2->type == TT_NAME || t2->type == TT_NUMBER))",
		"strcat(t1->string, t2->string);",
		"if (t1->type == TT_STRING && t2->type == TT_STRING)",
		"t1->string[strlen(t1->string)-1] = '\\0';",
		"strcat(t1->string, &t2->string[1]);",
		"return qfalse;",
	):
		assert snippet in merge_tokens

	for snippet in (
		"hash += name[i] * (119 + i);",
		"hash = (hash ^ (hash >> 10) ^ (hash >> 20)) & (DEFINEHASHSIZE-1);",
	):
		assert snippet in name_hash
	assert "hash = PC_NameHash(define->name);" in add_define_to_hash
	assert "define->hashnext = definehash[hash];" in add_define_to_hash
	assert "definehash[hash] = define;" in add_define_to_hash
	assert "hash = PC_NameHash(name);" in find_hashed_define
	assert "for (d = definehash[hash]; d; d = d->hashnext)" in find_hashed_define
	assert "if (!strcmp(d->name, name)) return d;" in find_hashed_define
	assert "for (p = define->parms; p; p = p->next)" in find_define_parm
	assert "if (!strcmp(p->string, name)) return i;" in find_define_parm
	assert "return -1;" in find_define_parm
	assert "for (t = define->parms; t; t = next)" in free_define
	assert "for (t = define->tokens; t; t = next)" in free_define
	assert "FreeMemory(define);" in free_define

	for snippet in (
		'{ "__LINE__",\tBUILTIN_LINE }',
		'{ "__FILE__",\tBUILTIN_FILE }',
		'{ "__DATE__",\tBUILTIN_DATE }',
		'{ "__TIME__",\tBUILTIN_TIME }',
		"define->flags |= DEFINE_FIXED;",
		"define->builtin = builtin[i].builtin;",
		"PC_AddDefineToHash(define, source->definehash);",
	):
		assert snippet in add_builtin_defines

	for snippet in (
		"token = PC_CopyToken(deftoken);",
		"case BUILTIN_LINE:",
		'sprintf(token->string, "%d", deftoken->line);',
		"token->type = TT_NUMBER;",
		"token->subtype = TT_DECIMAL | TT_INTEGER;",
		"case BUILTIN_FILE:",
		"strcpy(token->string, source->scriptstack->filename);",
		"token->type = TT_NAME;",
		"case BUILTIN_DATE:",
		"t = time(NULL);",
		"curtime = ctime(&t);",
		'strncat(token->string, curtime+4, 7);',
		'strncat(token->string+7, curtime+20, 4);',
		"case BUILTIN_TIME:",
		'strncat(token->string, curtime+11, 8);',
		"*firsttoken = NULL;",
		"*lasttoken = NULL;",
	):
		assert snippet in expand_builtin_define

	for snippet in (
		"if (define->builtin)",
		"return PC_ExpandBuiltinDefine(source, deftoken, define, firsttoken, lasttoken);",
		"if (define->numparms)",
		"if (!PC_ReadDefineParms(source, define, parms, MAX_DEFINEPARMS)) return qfalse;",
		"for (dt = define->tokens; dt; dt = dt->next)",
		"if (dt->type == TT_NAME)",
		"parmnum = PC_FindDefineParm(define, dt->string);",
		"for (pt = parms[parmnum]; pt; pt = pt->next)",
		"t = PC_CopyToken(pt);",
		"if (dt->string[0] == '#' && dt->string[1] == '\\0')",
		"if (dt->next) parmnum = PC_FindDefineParm(define, dt->next->string);",
		"dt = dt->next;",
		"if (!PC_StringizeTokens(parms[parmnum], &token))",
		'SourceError(source, "can\'t stringize tokens");',
		'SourceWarning(source, "stringizing operator without define parameter");',
		"if (t->next->string[0] == '#' && t->next->string[1] == '#')",
		"t1 = t;",
		"t2 = t->next->next;",
		"if (!PC_MergeTokens(t1, t2))",
		'SourceError(source, "can\'t merge %s with %s", t1->string, t2->string);',
		"PC_FreeToken(t1->next);",
		"t1->next = t2->next;",
		"if (t2 == last) last = t1;",
		"PC_FreeToken(t2);",
		"*firsttoken = first;",
		"*lasttoken = last;",
		"for (i = 0; i < define->numparms; i++)",
		"PC_FreeToken(pt);",
	):
		assert snippet in expand_define

	for snippet in (
		"if (!PC_ExpandDefine(source, deftoken, define, &firsttoken, &lasttoken)) return qfalse;",
		"lasttoken->next = source->tokens;",
		"source->tokens = firsttoken;",
	):
		assert snippet in expand_into_source

	assert "PC_FindDefineParm(define, token.string) >= 0" in directive_define
	assert "PC_ClearTokenWhiteSpace(t);" in directive_define
	assert "define->parms = t;" in directive_define
	assert "define->tokens = t;" in directive_define
	assert "if (!PC_ExpandDefineIntoSource(source, &token, define)) return qfalse;" in evaluate
	assert "if (!PC_ExpandDefineIntoSource(source, &token, define)) return qfalse;" in dollar_evaluate
	assert "if (!PC_ExpandDefineIntoSource(source, token, define)) return qfalse;" in read_token

	for address, name in (
		("4A8C30", "PC_CopyToken"),
		("4A8C90", "PC_ReadSourceToken"),
		("4A8DB0", "PC_UnreadSourceToken"),
		("4A8E20", "PC_ReadDefineParms"),
		("4A9230", "PC_StringizeTokens"),
		("4A92D0", "PC_MergeTokens"),
		("4A9370", "PC_NameHash"),
		("4A93B0", "PC_AddDefineToHash"),
		("4A9410", "PC_FindHashedDefine"),
		("4A94A0", "PC_FindDefineParm"),
		("4A9500", "PC_FreeDefine"),
		("4A9570", "PC_ExpandBuiltinDefine"),
		("4A97B0", "PC_ExpandDefine"),
		("4A9B70", "PC_ExpandDefineIntoSource"),
	):
		assert aliases[f"sub_{address}"] == name

	for row in (
		"FUN_004a8e20,004a8e20,1012,0,unknown",
		"FUN_004a9230,004a9230,157,0,unknown",
		"FUN_004a92d0,004a92d0,145,0,unknown",
		"FUN_004a9370,004a9370,63,0,unknown",
		"FUN_004a93b0,004a93b0,85,0,unknown",
		"FUN_004a9410,004a9410,138,0,unknown",
		"FUN_004a94a0,004a94a0,92,0,unknown",
		"FUN_004a9500,004a9500,98,0,unknown",
		"FUN_004a9570,004a9570,556,0,unknown",
		"FUN_004a97b0,004a97b0,947,0,unknown",
		"FUN_004a9b70,004a9b70,88,0,unknown",
	):
		assert row in ghidra_functions

	for evidence in (
		"004a8e20    int32_t sub_4a8e20(void* arg1, int32_t* arg2, int32_t* arg3, int32_t arg4)",
		"004a8e63  if (sub_4a8c90(arg1, &var_438) == 0)",
		'004a8e6e      sub_4a8ad0(arg1, "define %s missing parms")',
		"004a8e91  if (ecx_3 s> arg4)",
		"004a8ec0          arg3[i] = 0",
		"004a8f0b      sub_4a8db0(arg1, &var_438)",
		'004a91af          sub_4a8ad0(arg1, "define %s with too many parms")',
		'004a91d9          sub_4a8b30(arg1, "define %s has too many parms")',
		'004a9209                  sub_4a8ad0(arg1, "define %s incomplete")',
		'004a912b                      sub_4a8b30(arg1, "too many comma\'s")',
		'004a9156                              sub_4a8b30(arg1, "too few define parms")',
		"004a90d1                      sub_4cb7d0(eax_23, &var_438, 0x430)",
		"004a9230    int32_t sub_4a9230(void* arg1, char* arg2)",
		"004a923a  *(arg2 + 0x400) = 1",
		"004a9267  *edi = 0x22",
		"004a9293      strncat(arg2, i_1, 0x400 - (eax - &eax[1]))",
		"004a92d0    int32_t sub_4a92d0(char* arg1, void* arg2)",
		"004a92f4  if (eax == 4 && (edx == 4 || edx == 3))",
		"004a932e      if (eax != 1 || *(esi + 0x400) != eax)",
		"004a9360          return 0",
		"004a9370    int32_t sub_4a9370(char* arg1)",
		"004a93ae  return ((esi s>> 0xa ^ esi) s>> 0xa ^ esi) & 0x3ff",
		"004a93b0    int32_t sub_4a93b0(int32_t* arg1, int32_t arg2)",
		"004a9410    int32_t* sub_4a9410(int32_t arg1, char* arg2)",
		"004a94a0    int32_t sub_4a94a0(void* arg1, char* arg2)",
		"004a9500    int32_t* sub_4a9500(void* arg1)",
		"004a9570    int32_t __convention(\"regparm\") sub_4a9570",
		"004a957c  void* eax = sub_4a89a0(0x430)",
		"004a95c5  int32_t eax_3 = *(arg6 + 8) - 1",
		"004a95e3          sprintf(eax, &data_52d9b4, arg5[0x108])",
		"004a9631          char* ecx_2 = *(arg4 + 0x804)",
		"004a9691          var_8 = _time64(0)",
		"004a9721          var_8 = _time64(0)",
		"004a97b0    int32_t sub_4a97b0(int32_t arg1, int32_t* arg2, int32_t* arg3, void** arg4, void** arg5)",
		"004a97f0  if (esi[2] != 0)",
		"004a9823      int32_t result = sub_4a8e20(arg1, esi, &var_650, 0x80)",
		"004a986f              eax_3 = sub_4a94a0(esi, i)",
		"004a9943                      sub_4a9230(var_650[eax_5], &var_438)",
		'004a9970                  sub_4a8b30(arg1, "stringizing operator without def',
		"004a9a47              if (sub_4a92d0(i_1, esi_2) == 0)",
		'004a9b4b                  sub_4a8ad0(arg1, "can\'t merge %s with %s")',
		"004a9ae1  *arg4 = i_1",
		"004a9ae5  *arg5 = i_5",
		"004a9b70    int32_t sub_4a9b70(int32_t arg1, int32_t* arg2, int32_t* arg3)",
		"004a9b95  if (sub_4a97b0(arg1, arg2, arg3, &var_8, &var_c) != 0)",
		"004a9bab              *(eax_2 + 0x428) = *(arg1 + 0x808)",
		"004a9bb1              *(arg1 + 0x808) = ecx_1",
	):
		assert evidence in ql_steam_hlil
