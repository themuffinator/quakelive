from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOTLIB_L_PRECOMP = REPO_ROOT / "src" / "code" / "botlib" / "l_precomp.c"
BOTLIB_L_PRECOMP_H = REPO_ROOT / "src" / "code" / "botlib" / "l_precomp.h"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_H = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
GAME_PUBLIC_H = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
SERVER_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SERVER_QL_GAME_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"
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


def test_botlib_precompiler_directives_match_retail_references() -> None:
	l_precomp = BOTLIB_L_PRECOMP.read_text(encoding="utf-8")
	l_precomp_h = BOTLIB_L_PRECOMP_H.read_text(encoding="utf-8")
	be_interface = BOTLIB_INTERFACE.read_text(encoding="utf-8")
	botlib_h = BOTLIB_H.read_text(encoding="utf-8")
	game_public = GAME_PUBLIC_H.read_text(encoding="utf-8")
	game_syscalls = GAME_SYSCALLS.read_text(encoding="utf-8")
	server_game = SERVER_GAME.read_text(encoding="utf-8")
	server_imports = SERVER_QL_GAME_IMPORTS.read_text(encoding="utf-8")
	ql_steam_hlil = QL_STEAM_HLIL_PART04.read_text(encoding="utf-8")
	ghidra_functions = QL_STEAM_GHIDRA_FUNCTIONS.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	include = _extract_function_block(l_precomp, "int PC_Directive_include(source_t *source)")
	read_line = _extract_function_block(l_precomp, "int PC_ReadLine(source_t *source, token_t *token)")
	undef = _extract_function_block(l_precomp, "int PC_Directive_undef(source_t *source)")
	define = _extract_function_block(l_precomp, "int PC_Directive_define(source_t *source)")
	define_from_string = _extract_function_block(l_precomp, "define_t *PC_DefineFromString(char *string)")
	add_global_define = _extract_function_block(l_precomp, "int PC_AddGlobalDefine(char *string)")
	remove_all_global_defines = _extract_function_block(l_precomp, "void PC_RemoveAllGlobalDefines(void)")
	copy_define = _extract_function_block(l_precomp, "define_t *PC_CopyDefine(source_t *source, define_t *define)")
	add_globals_to_source = _extract_function_block(l_precomp, "void PC_AddGlobalDefinesToSource(source_t *source)")
	if_def = _extract_function_block(l_precomp, "int PC_Directive_if_def(source_t *source, int type)")
	ifdef = _extract_function_block(l_precomp, "int PC_Directive_ifdef(source_t *source)")
	ifndef = _extract_function_block(l_precomp, "int PC_Directive_ifndef(source_t *source)")
	else_directive = _extract_function_block(l_precomp, "int PC_Directive_else(source_t *source)")
	endif = _extract_function_block(l_precomp, "int PC_Directive_endif(source_t *source)")
	elif_directive = _extract_function_block(l_precomp, "int PC_Directive_elif(source_t *source)")
	if_directive = _extract_function_block(l_precomp, "int PC_Directive_if(source_t *source)")
	line = _extract_function_block(l_precomp, "int PC_Directive_line(source_t *source)")
	error = _extract_function_block(l_precomp, "int PC_Directive_error(source_t *source)")
	pragma = _extract_function_block(l_precomp, "int PC_Directive_pragma(source_t *source)")
	eval_directive = _extract_function_block(l_precomp, "int PC_Directive_eval(source_t *source)")
	evalfloat_directive = _extract_function_block(l_precomp, "int PC_Directive_evalfloat(source_t *source)")
	read_directive = _extract_function_block(l_precomp, "int PC_ReadDirective(source_t *source)")
	dollar_evalint = _extract_function_block(l_precomp, "int PC_DollarDirective_evalint(source_t *source)")
	dollar_evalfloat = _extract_function_block(l_precomp, "int PC_DollarDirective_evalfloat(source_t *source)")
	read_dollar_directive = _extract_function_block(l_precomp, "int PC_ReadDollarDirective(source_t *source)")
	load_source_file = _extract_function_block(l_precomp, "source_t *LoadSourceFile(const char *filename)")
	load_source_memory = _extract_function_block(
		l_precomp, "source_t *LoadSourceMemory(char *ptr, int length, char *name)"
	)
	shutdown = _extract_function_block(be_interface, "int Export_BotLibShutdown(void)")
	get_api = _extract_function_block(
		be_interface, "botlib_export_t *GetBotLibAPI(int apiVersion, botlib_import_t *import)"
	)

	for prototype in (
		"int PC_AddDefine(source_t *source, char *string);",
		"int PC_AddGlobalDefine(char *string);",
		"int PC_RemoveGlobalDefine(char *name);",
		"void PC_RemoveAllGlobalDefines(void);",
		"void PC_AddBuiltinDefines(source_t *source);",
	):
		assert prototype in l_precomp_h

	for snippet in (
		"if (source->skip > 0) return qtrue;",
		'SourceError(source, "#include without file name");',
		"if (token.linescrossed > 0)",
		"if (token.type == TT_STRING)",
		"StripDoubleQuotes(token.string);",
		"PC_ConvertPath(token.string);",
		"script = LoadScriptFile(token.string);",
		"strcpy(path, source->includepath);",
		"strcat(path, token.string);",
		"else if (token.type == TT_PUNCTUATION && *token.string == '<')",
		"while(PC_ReadSourceToken(source, &token))",
		'SourceWarning(source, "#include missing trailing >");',
		'SourceError(source, "#include without file name between < >");',
		'SourceError(source, "file %s not found", path);',
		"PC_PushScript(source, script);",
	):
		assert snippet in include

	for snippet in (
		"crossline = 0;",
		"if (!PC_ReadSourceToken(source, token)) return qfalse;",
		"if (token->linescrossed > crossline)",
		"PC_UnreadSourceToken(source, token);",
		'while(!strcmp(token->string, "\\\\")',
	):
		assert snippet in read_line

	for snippet in (
		"if (source->skip > 0) return qtrue;",
		'SourceError(source, "undef without name");',
		"if (token.type != TT_NAME)",
		'SourceError(source, "expected name, found %s", token.string);',
		"hash = PC_NameHash(token.string);",
		"for (lastdefine = NULL, define = source->definehash[hash]; define; define = define->hashnext)",
		"if (define->flags & DEFINE_FIXED)",
		'SourceWarning(source, "can\'t undef %s", token.string);',
		"PC_FreeDefine(define);",
	):
		assert snippet in undef

	for snippet in (
		"if (source->skip > 0) return qtrue;",
		'SourceError(source, "#define without name");',
		'SourceError(source, "expected name after #define, found %s", token.string);',
		"define = PC_FindHashedDefine(source->definehash, token.string);",
		'SourceError(source, "can\'t redefine %s", token.string);',
		'SourceWarning(source, "redefinition of %s", token.string);',
		"PC_UnreadSourceToken(source, &token);",
		"if (!PC_Directive_undef(source)) return qfalse;",
		"define = (define_t *) GetMemory(sizeof(define_t) + strlen(token.string) + 1);",
		"PC_AddDefineToHash(define, source->definehash);",
		"if (!PC_WhiteSpaceBeforeToken(&token) && !strcmp(token.string, \"(\"))",
		"if (!PC_CheckTokenString(source, \")\"))",
		'SourceError(source, "expected define parameter");',
		'SourceError(source, "invalid define parameter");',
		'SourceError(source, "two the same define parameters");',
		"PC_ClearTokenWhiteSpace(t);",
		'SourceError(source, "define parameters not terminated");',
		'SourceError(source, "define not terminated");',
		'SourceError(source, "recursive define (removed recursion)");',
		'!strcmp(define->tokens->string, "##")',
		'!strcmp(last->string, "##")',
		'SourceError(source, "define with misplaced ##");',
	):
		assert snippet in define

	for snippet in (
		'script = LoadScriptMemory(string, strlen(string), "*extern");',
		'strncpy(src.filename, "*extern", MAX_PATH);',
		"src.definehash = GetClearedMemory(DEFINEHASHSIZE * sizeof(define_t *));",
		"res = PC_Directive_define(&src);",
		"for (t = src.tokens; t; t = src.tokens)",
		"FreeScript(script);",
		"if (res > 0) return def;",
	):
		assert snippet in define_from_string

	assert "define = PC_DefineFromString(string);" in add_global_define
	assert "define->next = globaldefines;" in add_global_define
	assert "globaldefines = define;" in add_global_define
	assert "for (define = globaldefines; define; define = globaldefines)" in remove_all_global_defines
	assert "globaldefines = globaldefines->next;" in remove_all_global_defines
	assert "PC_FreeDefine(define);" in remove_all_global_defines
	assert "newdefine = (define_t *) GetMemory(sizeof(define_t) + strlen(define->name) + 1);" in copy_define
	assert "for (lasttoken = NULL, token = define->tokens; token; token = token->next)" in copy_define
	assert "for (lasttoken = NULL, token = define->parms; token; token = token->next)" in copy_define
	assert "for (define = globaldefines; define; define = define->next)" in add_globals_to_source
	assert "newdefine = PC_CopyDefine(source, define);" in add_globals_to_source
	assert "PC_AddDefineToHash(newdefine, source->definehash);" in add_globals_to_source

	for snippet in (
		'SourceError(source, "#ifdef without name");',
		'SourceError(source, "expected name after #ifdef, found %s", token.string);',
		"d = PC_FindHashedDefine(source->definehash, token.string);",
		"skip = (type == INDENT_IFDEF) == (d == NULL);",
		"PC_PushIndent(source, type, skip);",
	):
		assert snippet in if_def
	assert "return PC_Directive_if_def(source, INDENT_IFDEF);" in ifdef
	assert "return PC_Directive_if_def(source, INDENT_IFNDEF);" in ifndef
	assert 'SourceError(source, "misplaced #else");' in else_directive
	assert 'SourceError(source, "#else after #else");' in else_directive
	assert "PC_PushIndent(source, INDENT_ELSE, !skip);" in else_directive
	assert 'SourceError(source, "misplaced #endif");' in endif
	assert 'SourceError(source, "misplaced #elif");' in elif_directive
	assert "if (!PC_Evaluate(source, &value, NULL, qtrue)) return qfalse;" in elif_directive
	assert "PC_PushIndent(source, INDENT_ELIF, skip);" in elif_directive
	assert "PC_PushIndent(source, INDENT_IF, skip);" in if_directive
	assert 'SourceError(source, "#line directive not supported");' in line
	assert 'SourceError(source, "#error directive: %s", token.string);' in error
	assert 'SourceWarning(source, "#pragma directive not supported");' in pragma
	assert "while(PC_ReadLine(source, &token)) ;" in pragma

	for directive_block, expected in (
		(eval_directive, ("PC_Evaluate(source, &value, NULL, qtrue)", 'sprintf(token.string, "%d", abs(value));')),
		(evalfloat_directive, ("PC_Evaluate(source, NULL, &value, qfalse)", 'sprintf(token.string, "%1.2f", fabs(value));')),
		(dollar_evalint, ("PC_DollarEvaluate(source, &value, NULL, qtrue)", 'sprintf(token.string, "%d", abs(value));')),
		(dollar_evalfloat, ("PC_DollarEvaluate(source, NULL, &value, qfalse)", 'sprintf(token.string, "%1.2f", fabs(value));')),
	):
		for snippet in expected:
			assert snippet in directive_block
		assert "PC_UnreadSourceToken(source, &token);" in directive_block
		assert "if (value < 0) UnreadSignToken(source);" in directive_block

	for directive_name in (
		'{"if", PC_Directive_if}',
		'{"ifdef", PC_Directive_ifdef}',
		'{"ifndef", PC_Directive_ifndef}',
		'{"elif", PC_Directive_elif}',
		'{"else", PC_Directive_else}',
		'{"endif", PC_Directive_endif}',
		'{"include", PC_Directive_include}',
		'{"define", PC_Directive_define}',
		'{"undef", PC_Directive_undef}',
		'{"line", PC_Directive_line}',
		'{"error", PC_Directive_error}',
		'{"pragma", PC_Directive_pragma}',
		'{"eval", PC_Directive_eval}',
		'{"evalfloat", PC_Directive_evalfloat}',
		'{"evalint", PC_DollarDirective_evalint}',
		'{"evalfloat", PC_DollarDirective_evalfloat}',
	):
		assert directive_name in l_precomp

	for snippet in (
		'SourceError(source, "found # without name");',
		"if (token.linescrossed > 0)",
		'SourceError(source, "found # at end of line");',
		"for (i = 0; directives[i].name; i++)",
		"return directives[i].func(source);",
		'SourceError(source, "unknown precompiler directive %s", token.string);',
	):
		assert snippet in read_directive

	for snippet in (
		'SourceError(source, "found $ without name");',
		'SourceError(source, "found $ at end of line");',
		"for (i = 0; dollardirectives[i].name; i++)",
		"return dollardirectives[i].func(source);",
		"PC_UnreadSourceToken(source, &token);",
		'SourceError(source, "unknown precompiler directive %s", token.string);',
	):
		assert snippet in read_dollar_directive

	assert "PC_AddGlobalDefinesToSource(source);" in load_source_file
	assert "PC_AddGlobalDefinesToSource(source);" in load_source_memory
	assert shutdown.index("LibVarDeAllocAll();") < shutdown.index("PC_RemoveAllGlobalDefines();")
	assert shutdown.index("PC_RemoveAllGlobalDefines();") < shutdown.index("Log_Shutdown();")
	assert "int (*PC_AddGlobalDefine)(char *string);" in botlib_h
	assert "be_botlib_export.PC_AddGlobalDefine = PC_AddGlobalDefine;" in get_api
	assert get_api.index("be_botlib_export.PC_AddGlobalDefine = PC_AddGlobalDefine;") < get_api.index(
		"be_botlib_export.PC_LoadSourceHandle = PC_LoadSourceHandle;"
	)
	assert "BOTLIB_PC_ADD_GLOBAL_DEFINE" in game_public
	assert "G_QL_IMPORT_BOTLIB_PC_ADD_GLOBAL_DEFINE = 53" in game_public
	assert "case BOTLIB_PC_ADD_GLOBAL_DEFINE: return G_QL_IMPORT_BOTLIB_PC_ADD_GLOBAL_DEFINE;" in game_syscalls
	assert "return syscall( BOTLIB_PC_ADD_GLOBAL_DEFINE, string );" in game_syscalls
	assert "return botlib_export->PC_AddGlobalDefine( VMA(1) );" in server_game
	assert "[BOTLIB_PC_ADD_GLOBAL_DEFINE] = (ql_import_f)QL_G_trap_BotLibDefine," in server_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_PC_ADD_GLOBAL_DEFINE] = (ql_import_f)QL_G_trap_BotLibDefine;" in server_game
	assert "return G_Import_Syscall( BOTLIB_PC_ADD_GLOBAL_DEFINE, string );" in server_imports

	for address, name in (
		("4A9BD0", "PC_ConvertPath"),
		("4A9C50", "PC_Directive_include"),
		("4A9EA0", "PC_ReadLine"),
		("4A9F20", "PC_Directive_undef"),
		("4AA070", "PC_RemoveAllGlobalDefines"),
		("4AA0F0", "PC_CopyDefine"),
		("4AA250", "PC_AddGlobalDefinesToSource"),
		("4AA2E0", "PC_Directive_if_def"),
		("4AA3E0", "PC_Directive_ifdef"),
		("4AA400", "PC_Directive_ifndef"),
		("4AA420", "PC_Directive_else"),
		("4AA4E0", "PC_Directive_endif"),
		("4AB160", "PC_Evaluate"),
		("4AB450", "PC_DollarEvaluate"),
		("4AB780", "PC_Directive_elif"),
		("4AB810", "PC_Directive_if"),
		("4AB880", "PC_Directive_line"),
		("4AB8A0", "PC_Directive_error"),
		("4AB900", "PC_Directive_pragma"),
		("4AB9F0", "UnreadSignToken"),
		("4ABA70", "PC_Directive_eval"),
		("4ABB40", "PC_Directive_evalfloat"),
		("4ABC10", "PC_ReadDirective"),
		("4ABD20", "PC_DollarDirective_evalint"),
		("4ABE00", "PC_DollarDirective_evalfloat"),
		("4ABF10", "PC_ReadDollarDirective"),
		("4ACBC0", "PC_Directive_define"),
		("4AD0E0", "PC_DefineFromString"),
		("4AD200", "PC_AddGlobalDefine"),
	):
		assert aliases[f"sub_{address}"] == name

	for row in (
		"FUN_004a9c50,004a9c50,587,0,unknown",
		"FUN_004a9ea0,004a9ea0,115,0,unknown",
		"FUN_004a9f20,004a9f20,335,0,unknown",
		"FUN_004aa070,004aa070,117,0,unknown",
		"FUN_004aa0f0,004aa0f0,340,0,unknown",
		"FUN_004aa250,004aa250,130,0,unknown",
		"FUN_004aa2e0,004aa2e0,249,0,unknown",
		"FUN_004aa3e0,004aa3e0,19,0,unknown",
		"FUN_004aa400,004aa400,19,0,unknown",
		"FUN_004aa420,004aa420,179,0,unknown",
		"FUN_004aa4e0,004aa4e0,90,0,unknown",
		"FUN_004ab780,004ab780,137,0,unknown",
		"FUN_004ab810,004ab810,101,0,unknown",
		"FUN_004ab880,004ab880,24,0,unknown",
		"FUN_004ab8a0,004ab8a0,81,0,unknown",
		"FUN_004ab900,004ab900,239,0,unknown",
		"FUN_004aba70,004aba70,199,0,unknown",
		"FUN_004abb40,004abb40,208,0,unknown",
		"FUN_004abc10,004abc10,271,0,unknown",
		"FUN_004acbc0,004acbc0,1312,0,unknown",
		"FUN_004ad0e0,004ad0e0,285,0,unknown",
		"FUN_004ad200,004ad200,42,0,unknown",
	):
		assert row in ghidra_functions

	for evidence in (
		"004a9c50    int32_t sub_4a9c50(void* arg1)",
		"004a9c74  if (*(arg1 + 0x818) s> 0)",
		'004a9ca4      sub_4a8ad0(arg1, "#include without file name")',
		"004a9cd7      sub_4ae4c0(&var_478)",
		"004a9ce3      sub_4a9bd0(&var_478)",
		"004a9cef      eax_6 = sub_4ae5c0(&var_478)",
		"004a9d9c  if (sub_4a8c90(arg1, &var_478) != 0)",
		"004a9de6              sub_4a8db0(arg1, &var_478)",
		'004a9dfd      sub_4a8b30(arg1, "#include missing trailing >")',
		'004a9e45              sub_4a8ad0(arg1, "file %s not found")',
		"004a9e61      sub_4a8bd0(arg1, eax_6)",
		"004a9ea0    int32_t sub_4a9ea0(void* arg1, void* arg2)",
		"004a9ebc      if (sub_4a8c90(arg1, arg2) == 0)",
		"004a9f04          sub_4a8db0(arg1, arg2)",
		"004a9f20    int32_t sub_4a9f20(void* arg1)",
		'004a9f5e          sub_4a8ad0(arg1, "undef without name")',
		'004a9f97          sub_4a8ad0(arg1, "expected name, found %s")',
		"004a9fb9      int32_t eax_5 = sub_4a9370(&var_438)",
		"004aa070    void sub_4aa070()",
		"004aa079  for (void* i = data_16dd7e0; i != 0; i = data_16dd7e0)",
		"004aa0f0    void* sub_4aa0f0(int32_t* arg1)",
		"004aa250    void sub_4aa250(int32_t* arg1)",
		"004aa2e0    int32_t sub_4aa2e0(void* arg1, int32_t arg2)",
		"004aa373  int32_t* eax_5 = sub_4a9410(*(arg1 + 0x810), &var_438)",
		"004aa391  void* eax_9 = sub_4a89a0(0x10)",
		"004aa3e0    int32_t sub_4aa3e0(void* arg1)",
		"004aa3f2  return sub_4aa2e0(arg1, 8)",
		"004aa400    int32_t sub_4aa400(void* arg1)",
		"004aa412  return sub_4aa2e0(arg1, 0x10)",
		"004aa420    int32_t sub_4aa420(void* arg1)",
		'004aa482              sub_4a8ad0(arg1, "#else after #else")',
		'004aa468  sub_4a8ad0(arg1, "misplaced #else")',
		"004aa4e0    int32_t sub_4aa4e0(void* arg1)",
		"004ab780    int32_t sub_4ab780(int32_t arg1)",
		'004ab7fb      sub_4a8ad0(esi, "misplaced #elif")',
		"004ab810    int32_t __convention(\"regparm\") sub_4ab810",
		"004ab821  int32_t result = sub_4ab160(arg4, &var_8, nullptr, 1)",
		"004ab880    int32_t sub_4ab880(void* arg1)",
		'004ab88c  sub_4a8ad0(arg1, "#line directive not supported")',
		"004ab8a0    int32_t sub_4ab8a0(void* arg1)",
		'004ab8d8  sub_4a8ad0(arg1, "#error directive: %s")',
		"004ab900    int32_t sub_4ab900(void* arg1)",
		'004ab91e  sub_4a8b30(arg1, "#pragma directive not supported")',
		"004aba70    int32_t sub_4aba70(int32_t arg1)",
		"004aba93  int32_t result = sub_4ab160(arg1, &var_43c, nullptr, 1)",
		"004abb40    int32_t sub_4abb40(int32_t arg1)",
		"004abb63  int32_t result = sub_4ab160(arg1, nullptr, &var_440, 0)",
		"004abc10    int32_t sub_4abc10(void* arg1)",
		'004abc41      sub_4a8ad0(arg1, "found # without name")',
		'004abc73      sub_4a8ad0(arg1, "found # at end of line")',
		"004abd0a                  int32_t result = (&data_5645f4)[esi_1 * 2](arg1)",
		'004abce8  sub_4a8ad0(arg1, "unknown precompiler directive %s")',
		"004acbc0    int32_t sub_4acbc0(int32_t arg1)",
		"004acbe4  if (*(arg1 + 0x818) s> 0)",
		'004acc14      sub_4a8ad0(arg1, "#define without name")',
		'004acc4d          sub_4a8ad0(arg1, "expected name after #define, fou',
		"004acc74      int32_t* eax_6 = sub_4a9410(*(arg1 + 0x810), &var_438)",
		'004acc93          sub_4a8ad0(arg1, "can\'t redefine %s")',
		'004accb9      sub_4a8b30(arg1, "redefinition of %s")',
		"004accd6      if (sub_4a9f20(arg1) != 0)",
		"004acd28          sub_4a93b0(ebx, *(arg1 + 0x810))",
		'004acedb                      sub_4a8ad0(arg1, "expected define parameter")',
		'004acefc                          sub_4a8ad0(arg1, "invalid define parameter")',
		'004acf1d                          sub_4a8ad0(arg1, "two the same define parameters")',
		'004acf3e                          sub_4a8ad0(arg1, "define parameters not terminated")',
		'004acf5f                          sub_4a8ad0(arg1, "define not terminated")',
		'004acfeb                      sub_4a8ad0(esi_3, "recursive define (removed recurs',
		'004ad0af                      sub_4a8ad0(esi_3, "define with misplaced ##")',
		"004ad0e0    void* sub_4ad0e0(int32_t* arg1)",
		"004ad15b  int32_t eax_6 = sub_4acbc0(&var_c58)",
		"004ad200    void* sub_4ad200(int32_t* arg1)",
		"004ad207  void* result = sub_4ad0e0(arg1)",
	):
		assert evidence in ql_steam_hlil
