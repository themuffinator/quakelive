from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
FUNCTIONS_CSV = (
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
QL_STEAM_HLIL_PART04 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part04.txt"
)
BOTLIB_L_PRECOMP = REPO_ROOT / "src" / "code" / "botlib" / "l_precomp.c"
BOTLIB_L_SCRIPT = REPO_ROOT / "src" / "code" / "botlib" / "l_script.c"
BOTLIB_L_SCRIPT_H = REPO_ROOT / "src" / "code" / "botlib" / "l_script.h"

EXPECTED_PARSER_TAIL_ALIASES = {
	"4AA610": "PC_EvaluateTokens",
	"4AD4F0": "PS_ReadEscapeCharacter",
	"4ADBA0": "PS_ReadNumber",
	"4AE160": "PS_ExpectTokenType",
}

EXPECTED_PARSER_TAIL_SIZES = {
	"4AA610": 2689,
	"4AD4F0": 564,
	"4ADBA0": 710,
	"4AE160": 858,
}

BOTLIB_SUPPORT_TAIL_START = 0x4A83C0
BOTLIB_SUPPORT_TAIL_END = 0x4AF820


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _aliases() -> dict[str, str]:
	return json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]


def _extract_function_block(source: str, signature: str) -> str:
	start = source.find(signature)
	assert start != -1, signature
	brace = source.find("{", start)
	assert brace != -1, signature

	depth = 0
	for offset in range(brace, len(source)):
		if source[offset] == "{":
			depth += 1
		elif source[offset] == "}":
			depth -= 1
			if depth == 0:
				return source[start : offset + 1]

	raise AssertionError(f"unterminated function block: {signature}")


def _function_row(address: str) -> str:
	with FUNCTIONS_CSV.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			if row["entry"] == f"00{address.lower()}":
				return f'{row["name"]},{row["entry"]},{row["size"]},{row["thunk"]},{row["calling_convention"]}'
	raise AssertionError(f"missing function row: {address}")


def test_parser_tail_aliases_rows_and_hlil_anchors_are_pinned() -> None:
	aliases = _aliases()
	hlil = _read(QL_STEAM_HLIL_PART03) + "\n" + _read(QL_STEAM_HLIL_PART04)

	for address, name in EXPECTED_PARSER_TAIL_ALIASES.items():
		assert aliases[f"sub_{address}"] == name
		assert _function_row(address) == (
			f"FUN_00{address.lower()},00{address.lower()},"
			f"{EXPECTED_PARSER_TAIL_SIZES[address]},0,unknown"
		)

	for hlil_anchor in (
		"004aa610    int32_t sub_4aa610(void* arg1, void* arg2, int32_t* arg3, double* arg4, int32_t arg5)",
		"004ab3b0          if (sub_4aa610(esi, i_2, arg2, arg3, arg4) == 0)",
		"004ab730      if (sub_4aa610(esi, i_2, arg2, arg3, arg4) == 0)",
		"004ad4f0    int32_t sub_4ad4f0(void* arg1, char* arg2)",
		"004ad7fb          sub_4ad4f0(arg1, i + ebx)",
		"004adba0    int32_t sub_4adba0(void* arg1, char* arg2)",
		"004ae0d1          int32_t eax_8 = sub_4adba0(arg1, arg2)",
		"004ae160    int32_t sub_4ae160(int32_t* arg1, int32_t arg2, int32_t arg3, int32_t* arg4)",
		"00482f27                  if (sub_4ae160(var_43c, 1, 0, &var_438) == 0)",
		"trailing operator in #if/#elif",
		"undefined name %s in #if/#elif",
		"divide by zero in #if/#elif\\n",
		"unknown escape char",
		"expected a %s, found %s",
		"expected %s, found %s",
	):
		assert hlil_anchor in hlil


def test_precompiler_expression_evaluator_source_shape_matches_retail_mapping() -> None:
	precomp = _read(BOTLIB_L_PRECOMP)

	evaluate_tokens = _extract_function_block(
		precomp,
		"int PC_EvaluateTokens(source_t *source, token_t *tokens, signed long int *intvalue,",
	)
	evaluate = _extract_function_block(
		precomp,
		"int PC_Evaluate(source_t *source, signed long int *intvalue,",
	)
	dollar_evaluate = _extract_function_block(
		precomp,
		"int PC_DollarEvaluate(source_t *source, signed long int *intvalue,",
	)

	for source_anchor in (
		"operator_t operator_heap[MAX_OPERATORS];",
		"value_t value_heap[MAX_VALUES];",
		"if (intvalue) *intvalue = 0;",
		"if (floatvalue) *floatvalue = 0;",
		"if (strcmp(t->string, \"defined\"))",
		'SourceError(source, "undefined name %s in #if/#elif", t->string);',
		"PC_FindHashedDefine(source->definehash, t->string)",
		"PC_FindDefine(source->defines, t->string)",
		'SourceError(source, "defined without name in #if/#elif");',
		'SourceError(source, "defined without ) in #if/#elif");',
		'SourceError(source, "misplaced minus sign in #if/#elif");',
		'SourceError(source, "too many ) in #if/#elsif");',
		'SourceError(source, "illigal operator %s on floating point operands\\n", t->string);',
		'SourceError(source, "++ or -- used in #if/#elif");',
		'SourceError(source, "! or ~ after value in #if/#elif");',
		'SourceError(source, "operator %s after operator in #if/#elif", t->string);',
		'o->priority = PC_OperatorPriority(t->subtype);',
		'SourceError(source, "trailing operator in #if/#elif");',
		'SourceError(source, "too many ( in #if/#elif");',
		'SourceError(source, "mising values in #if/#elif");',
		"case P_LOGIC_NOT:",
		"case P_BIN_NOT:",
		"case P_MUL:",
		"case P_DIV:",
		'SourceError(source, "divide by zero in #if/#elif\\n");',
		"case P_MOD:",
		"case P_LOGIC_AND:",
		"case P_RSHIFT:",
		"case P_BIN_XOR:",
		"case P_COLON:",
		'SourceError(source, ": without ? in #if/#elif");',
		"case P_QUESTIONMARK:",
		'SourceError(source, "? after ? in #if/#elif");',
		"if (o->operator != P_QUESTIONMARK) v = v->next;",
		"if (!error) return qtrue;",
		"if (intvalue) *intvalue = 0;",
		"if (floatvalue) *floatvalue = 0;",
		"return qfalse;",
	):
		assert source_anchor in evaluate_tokens

	assert "if (!PC_EvaluateTokens(source, firsttoken, intvalue, floatvalue, integer)) return qfalse;" in evaluate
	assert "if (!PC_EvaluateTokens(source, firsttoken, intvalue, floatvalue, integer)) return qfalse;" in dollar_evaluate


def test_script_escape_number_and_expect_type_source_shape_matches_retail_mapping() -> None:
	script = _read(BOTLIB_L_SCRIPT)
	script_h = _read(BOTLIB_L_SCRIPT_H)

	read_escape = _extract_function_block(script, "int PS_ReadEscapeCharacter(script_t *script, char *ch)")
	read_string = _extract_function_block(script, "int PS_ReadString(script_t *script, token_t *token, int quote)")
	read_number = _extract_function_block(script, "int PS_ReadNumber(script_t *script, token_t *token)")
	read_token = _extract_function_block(script, "int PS_ReadToken(script_t *script, token_t *token)")
	expect_type = _extract_function_block(
		script,
		"int PS_ExpectTokenType(script_t *script, int type, int subtype, token_t *token)",
	)

	for script_header_anchor in (
		"#define BINARYNUMBERS",
		"#define NUMBERVALUE",
		"#define SCFL_PRIMITIVE",
		"#define P_COLON",
		"#define P_QUESTIONMARK",
		"int PS_ExpectTokenType(script_t *script, int type, int subtype, token_t *token);",
	):
		assert script_header_anchor in script_h

	for escape_anchor in (
		"script->script_p++;",
		"case '\\\\': c = '\\\\'; break;",
		"case 'n': c = '\\n'; break;",
		"case 'r': c = '\\r'; break;",
		"case 't': c = '\\t'; break;",
		"case 'v': c = '\\v'; break;",
		"case 'b': c = '\\b'; break;",
		"case 'f': c = '\\f'; break;",
		"case 'a': c = '\\a'; break;",
		"case '\\'': c = '\\''; break;",
		"case '\\\"': c = '\\\"'; break;",
		"case '\\?': c = '\\?'; break;",
		"case 'x':",
		"val = (val << 4) + c;",
		'ScriptWarning(script, "too large value in escape character");',
		'if (*script->script_p < \'0\' || *script->script_p > \'9\') ScriptError(script, "unknown escape char");',
		"val = val * 10 + c;",
		"*ch = c;",
		"return 1;",
	):
		assert escape_anchor in read_escape

	for number_anchor in (
		"token->type = TT_NUMBER;",
		"(*(script->script_p + 1) == 'x' ||",
		"*(script->script_p + 1) == 'X'))",
		"(c >= 'a' && c <= 'f') ||",
		"(c >= 'A' && c <= 'A'))",
		'ScriptError(script, "hexadecimal number longer than MAX_TOKEN = %d", MAX_TOKEN);',
		"token->subtype |= TT_HEX;",
		"#ifdef BINARYNUMBERS",
		"(*(script->script_p + 1) == 'b' ||",
		"*(script->script_p + 1) == 'B'))",
		"while(c == '0' || c == '1')",
		'ScriptError(script, "binary number longer than MAX_TOKEN = %d", MAX_TOKEN);',
		"token->subtype |= TT_BINARY;",
		"#endif //BINARYNUMBERS",
		"if (*script->script_p == '0') octal = qtrue;",
		"if (c == '.') dot = qtrue;",
		"else if (c == '8' || c == '9') octal = qfalse;",
		'ScriptError(script, "number longer than MAX_TOKEN = %d", MAX_TOKEN);',
		"if (octal) token->subtype |= TT_OCTAL;",
		"else token->subtype |= TT_DECIMAL;",
		"if (dot) token->subtype |= TT_FLOAT;",
		"if ( (c == 'l' || c == 'L')",
		"token->subtype |= TT_LONG;",
		"else if ( (c == 'u' || c == 'U')",
		"token->subtype |= TT_UNSIGNED;",
		"NumberValue(token->string, token->subtype, &token->intvalue, &token->floatvalue);",
		"if (!(token->subtype & TT_FLOAT)) token->subtype |= TT_INTEGER;",
	):
		assert number_anchor in read_number

	assert "if (!PS_ReadEscapeCharacter(script, &token->string[len]))" in read_string
	assert "if (!PS_ReadNumber(script, token)) return 0;" in read_token
	assert "return PS_ReadPrimitive(script, token);" in read_token

	for expect_anchor in (
		"if (!PS_ReadToken(script, token))",
		'ScriptError(script, "couldn\'t read expected token");',
		'if (type == TT_STRING) strcpy(str, "string");',
		'if (type == TT_LITERAL) strcpy(str, "literal");',
		'if (type == TT_NUMBER) strcpy(str, "number");',
		'if (type == TT_NAME) strcpy(str, "name");',
		'if (type == TT_PUNCTUATION) strcpy(str, "punctuation");',
		'ScriptError(script, "expected a %s, found %s", str, token->string);',
		"if ((token->subtype & subtype) != subtype)",
		'if (subtype & TT_DECIMAL) strcpy(str, "decimal");',
		'if (subtype & TT_HEX) strcpy(str, "hex");',
		'if (subtype & TT_OCTAL) strcpy(str, "octal");',
		'if (subtype & TT_BINARY) strcpy(str, "binary");',
		'if (subtype & TT_LONG) strcat(str, " long");',
		'if (subtype & TT_UNSIGNED) strcat(str, " unsigned");',
		'if (subtype & TT_FLOAT) strcat(str, " float");',
		'if (subtype & TT_INTEGER) strcat(str, " integer");',
		'ScriptError(script, "expected %s, found %s", str, token->string);',
		"if (subtype < 0)",
		'ScriptError(script, "BUG: wrong punctuation subtype");',
		"if (token->subtype != subtype)",
		'ScriptError(script, "expected %s, found %s",',
		"return 1;",
	):
		assert expect_anchor in expect_type


def test_botlib_support_tail_promoted_alias_scan_has_direct_test_mentions() -> None:
	aliases = _aliases()
	botlib_test_text = "\n".join(
		path.read_text(encoding="utf-8")
		for path in sorted((REPO_ROOT / "tests").glob("test_botlib_*.py"))
	)
	missing: list[str] = []

	for key, name in aliases.items():
		if not key.startswith("sub_"):
			continue
		try:
			address = int(key[4:], 16)
		except ValueError:
			continue
		if not BOTLIB_SUPPORT_TAIL_START <= address <= BOTLIB_SUPPORT_TAIL_END:
			continue

		address_text = key[4:]
		if not any(
			form in botlib_test_text
			for form in (key, address_text, address_text.lower(), address_text.upper(), name)
		):
			missing.append(f"0x{address:08X} {key} {name}")

	assert missing == []
