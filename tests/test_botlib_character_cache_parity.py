from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

BOTLIB_AI_CHAR = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_char.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
GAME_AI_CHAR_H = REPO_ROOT / "src" / "code" / "game" / "be_ai_char.h"
GAME_AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
GAME_G_LOCAL = REPO_ROOT / "src" / "code" / "game" / "g_local.h"
GAME_G_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
SERVER_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SERVER_QL_GAME_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"
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


def test_character_cache_aliases_and_retail_function_rows_are_pinned() -> None:
	aliases = _aliases()
	functions = _read(QL_STEAM_FUNCTIONS)
	hlil = _read(QL_STEAM_HLIL_PART03)

	expected_aliases = {
		"496950": "BotDumpCharacter",
		"4969E0": "BotFreeCharacterStrings",
		"496A10": "BotFreeCharacter2",
		"496A80": "BotFreeCharacter",
		"496AB0": "BotDefaultCharacteristics",
		"496B40": "BotLoadCharacterFromFile",
		"497040": "BotFindCachedCharacter",
		"4970E0": "BotLoadCachedCharacter",
		"497360": "BotLoadCharacterSkill",
		"4973D0": "BotInterpolateCharacters",
		"497590": "BotLoadCharacter",
		"4976F0": "CheckCharacteristicIndex",
		"497780": "Characteristic_Float",
		"497810": "Characteristic_BFloat",
		"4978C0": "Characteristic_Integer",
		"497950": "Characteristic_BInteger",
		"4979E0": "Characteristic_String",
		"497A80": "BotShutdownCharacters",
	}
	expected_sizes = {
		"496950": 144,
		"4969E0": 43,
		"496A10": 102,
		"496A80": 35,
		"496AB0": 140,
		"496B40": 1271,
		"497040": 145,
		"4970E0": 627,
		"497360": 104,
		"4973D0": 438,
		"497590": 337,
		"4976F0": 131,
		"497780": 139,
		"497810": 172,
		"4978C0": 143,
		"497950": 139,
		"4979E0": 147,
		"497A80": 114,
	}

	for address, name in expected_aliases.items():
		assert aliases[f"sub_{address}"] == name
		_assert_function_row(functions, address, expected_sizes[address])

	for evidence in (
		"00496950    int32_t sub_496950(void* arg1)",
		"004969e0    void sub_4969e0(void* arg1)",
		"00496a10    int32_t* sub_496a10(int32_t arg1)",
		"00496a80    int32_t sub_496a80()",
		"00496ab0    float sub_496ab0(float arg1, float arg2)",
		"00496b40    char* sub_496b40(char* arg1, int32_t arg2)",
		"00497040    int32_t sub_497040(char* arg1, float arg2)",
		"004970e0    int32_t sub_4970e0(char* arg1, float arg2, int32_t arg3)",
		"00497360    int32_t sub_497360(char* arg1, float arg2)",
		"004973d0    int32_t sub_4973d0(int32_t arg1, void* arg2, float arg3)",
		"00497590    void sub_497590(char* arg1, float arg2)",
		"004976f0    int32_t sub_4976f0(int32_t arg1, int32_t arg2)",
		"00497780    long double sub_497780(int32_t arg1, int32_t arg2)",
		"00497810    long double sub_497810(float arg1, int32_t arg2, float arg3, float arg4)",
		"004978c0    int32_t sub_4978c0(int32_t arg1, int32_t arg2)",
		"00497950    int32_t sub_497950(int32_t arg1, int32_t arg2, int32_t arg3, int32_t arg4)",
		"004979e0    int32_t sub_4979e0(int32_t arg1, int32_t arg2, int32_t arg3, int32_t arg4)",
		"00497a80    int32_t* sub_497a80()",
		"004a8110  *arg1 = sub_497590",
		"004a8116  arg1[1] = sub_496a80",
		"004a811d  arg1[2] = sub_497780",
		"004a8124  arg1[3] = sub_497810",
		"004a812b  arg1[4] = sub_4978c0",
		"004a8132  arg1[5] = sub_497950",
		"004a8139  arg1[6] = sub_4979e0",
	):
		assert evidence in hlil


def test_character_cleanup_defaulting_and_cache_source_match_retail_shape() -> None:
	source = _read(BOTLIB_AI_CHAR)

	dump = _extract_function_block(source, "void BotDumpCharacter(bot_character_t *ch)")
	free_strings = _extract_function_block(source, "void BotFreeCharacterStrings(bot_character_t *ch)")
	free2 = _extract_function_block(source, "void BotFreeCharacter2(int handle)")
	free_public = _extract_function_block(source, "void BotFreeCharacter(int handle)")
	defaults = _extract_function_block(source, "void BotDefaultCharacteristics(bot_character_t *ch, bot_character_t *defaultch)")
	find_cached = _extract_function_block(source, "int BotFindCachedCharacter(char *charfile, float skill)")
	load_cached = _extract_function_block(source, "int BotLoadCachedCharacter(char *charfile, float skill, int reload)")
	load_skill = _extract_function_block(source, "int BotLoadCharacterSkill(char *charfile, float skill)")

	assert "#define MAX_CHARACTERISTICS\t\t80" in source
	assert "#define CT_INTEGER\t\t\t\t1" in source
	assert "#define CT_FLOAT\t\t\t\t2" in source
	assert "#define CT_STRING\t\t\t\t3" in source
	assert '#define DEFAULT_CHARACTER\t\t"bots/default_c.c"' in source
	assert "bot_character_t *botcharacters[MAX_CLIENTS + 1];" in source

	assert 'Log_Write("%s", ch->filename);' in dump
	assert 'Log_Write("skill %d\\n", ch->skill);' in dump
	assert "for (i = 0; i < MAX_CHARACTERISTICS; i++)" in dump
	assert 'case CT_INTEGER: Log_Write(" %4d %d\\n", i, ch->c[i].value.integer); break;' in dump
	assert 'case CT_FLOAT: Log_Write(" %4d %f\\n", i, ch->c[i].value._float); break;' in dump
	assert 'case CT_STRING: Log_Write(" %4d %s\\n", i, ch->c[i].value.string); break;' in dump

	assert "if (ch->c[i].type == CT_STRING)" in free_strings
	assert "FreeMemory(ch->c[i].value.string);" in free_strings
	assert 'botimport.Print(PRT_FATAL, "character handle %d out of range\\n", handle);' in free2
	assert 'botimport.Print(PRT_FATAL, "invalid character %d\\n", handle);' in free2
	assert "BotFreeCharacterStrings(botcharacters[handle]);" in free2
	assert "FreeMemory(botcharacters[handle]);" in free2
	assert "botcharacters[handle] = NULL;" in free2
	assert 'if (!LibVarGetValue("bot_reloadcharacters")) return;' in free_public
	assert "BotFreeCharacter2(handle);" in free_public

	assert "if (ch->c[i].type) continue;" in defaults
	assert "if (defaultch->c[i].type == CT_FLOAT)" in defaults
	assert "ch->c[i].value._float = defaultch->c[i].value._float;" in defaults
	assert "else if (defaultch->c[i].type == CT_INTEGER)" in defaults
	assert "ch->c[i].value.integer = defaultch->c[i].value.integer;" in defaults
	assert "else if (defaultch->c[i].type == CT_STRING)" in defaults
	assert "ch->c[i].value.string = (char *) GetMemory(strlen(defaultch->c[i].value.string)+1);" in defaults
	assert "strcpy(ch->c[i].value.string, defaultch->c[i].value.string);" in defaults

	assert "for (handle = 1; handle <= MAX_CLIENTS; handle++)" in find_cached
	assert "if ( !botcharacters[handle] ) continue;" in find_cached
	assert "strcmp( botcharacters[handle]->filename, charfile ) == 0" in find_cached
	assert "(skill < 0 || fabs(botcharacters[handle]->skill - skill) < 0.01)" in find_cached
	assert "return handle;" in find_cached
	assert "return 0;" in find_cached

	assert "for (handle = 1; handle <= MAX_CLIENTS; handle++)" in load_cached
	assert "if (handle > MAX_CLIENTS) return 0;" in load_cached
	assert "cachedhandle = BotFindCachedCharacter(charfile, skill);" in load_cached
	assert 'botimport.Print(PRT_MESSAGE, "loaded cached skill %f from %s\\n", skill, charfile);' in load_cached
	assert "intskill = (int) (skill + 0.5);" in load_cached
	assert "ch = BotLoadCharacterFromFile(charfile, intskill);" in load_cached
	assert 'botimport.Print(PRT_WARNING, "couldn\'t find skill %d in %s\\n", intskill, charfile);' in load_cached
	assert "cachedhandle = BotFindCachedCharacter(DEFAULT_CHARACTER, skill);" in load_cached
	assert "ch = BotLoadCharacterFromFile(DEFAULT_CHARACTER, intskill);" in load_cached
	assert "cachedhandle = BotFindCachedCharacter(charfile, -1);" in load_cached
	assert "ch = BotLoadCharacterFromFile(charfile, -1);" in load_cached
	assert "cachedhandle = BotFindCachedCharacter(DEFAULT_CHARACTER, -1);" in load_cached
	assert "ch = BotLoadCharacterFromFile(DEFAULT_CHARACTER, -1);" in load_cached
	assert 'botimport.Print(PRT_WARNING, "couldn\'t load any skill from %s\\n", charfile);' in load_cached

	assert "defaultch = BotLoadCachedCharacter(DEFAULT_CHARACTER, skill, qfalse);" in load_skill
	assert 'ch = BotLoadCachedCharacter(charfile, skill, LibVarGetValue("bot_reloadcharacters"));' in load_skill
	assert "BotDefaultCharacteristics(botcharacters[ch], botcharacters[defaultch]);" in load_skill


def test_character_loader_interpolation_and_accessors_match_retail_shape() -> None:
	source = _read(BOTLIB_AI_CHAR)
	hlil = _read(QL_STEAM_HLIL_PART03)

	load_from_file = _extract_function_block(source, "bot_character_t *BotLoadCharacterFromFile(char *charfile, int skill)")
	interpolate = _extract_function_block(source, "int BotInterpolateCharacters(int handle1, int handle2, float desiredskill)")
	load_public = _extract_function_block(source, "int BotLoadCharacter(char *charfile, float skill)")
	check_index = _extract_function_block(source, "int CheckCharacteristicIndex(int character, int index)")
	char_float = _extract_function_block(source, "float Characteristic_Float(int character, int index)")
	char_bfloat = _extract_function_block(source, "float Characteristic_BFloat(int character, int index, float min, float max)")
	char_integer = _extract_function_block(source, "int Characteristic_Integer(int character, int index)")
	char_binteger = _extract_function_block(source, "int Characteristic_BInteger(int character, int index, int min, int max)")
	char_string = _extract_function_block(source, "void Characteristic_String(int character, int index, char *buf, int size)")
	shutdown = _extract_function_block(source, "void BotShutdownCharacters(void)")

	assert "PC_SetBaseFolder(BOTFILESBASEFOLDER);" in load_from_file
	assert "source = LoadSourceFile(charfile);" in load_from_file
	assert 'botimport.Print(PRT_ERROR, "counldn\'t load %s\\n", charfile);' in load_from_file
	assert "ch = (bot_character_t *) GetClearedMemory(sizeof(bot_character_t) +" in load_from_file
	assert "MAX_CHARACTERISTICS * sizeof(bot_characteristic_t));" in load_from_file
	assert "strcpy(ch->filename, charfile);" in load_from_file
	assert 'if (!strcmp(token.string, "skill"))' in load_from_file
	assert "if (skill < 0 || (int)token.intvalue == skill)" in load_from_file
	assert "foundcharacter = qtrue;" in load_from_file
	assert "ch->skill = token.intvalue;" in load_from_file
	assert "if (token.type != TT_NUMBER || !(token.subtype & TT_INTEGER))" in load_from_file
	assert 'SourceError(source, "expected integer index, found %s\\n", token.string);' in load_from_file
	assert "if (index < 0 || index > MAX_CHARACTERISTICS)" in load_from_file
	assert 'SourceError(source, "characteristic index out of range [0, %d]\\n", MAX_CHARACTERISTICS);' in load_from_file
	assert 'SourceError(source, "characteristic %d already initialized\\n", index);' in load_from_file
	assert "if (token.subtype & TT_FLOAT)" in load_from_file
	assert "ch->c[index].type = CT_FLOAT;" in load_from_file
	assert "ch->c[index].type = CT_INTEGER;" in load_from_file
	assert "StripDoubleQuotes(token.string);" in load_from_file
	assert "ch->c[index].value.string = GetMemory(strlen(token.string)+1);" in load_from_file
	assert "ch->c[index].type = CT_STRING;" in load_from_file
	assert 'SourceError(source, "expected integer, float or string, found %s\\n", token.string);' in load_from_file
	assert "indent = 1;" in load_from_file
	assert 'if (!strcmp(token.string, "{")) indent++;' in load_from_file
	assert 'else if (!strcmp(token.string, "}")) indent--;' in load_from_file
	assert 'SourceError(source, "unknown definition %s\\n", token.string);' in load_from_file
	assert "if (!foundcharacter)" in load_from_file

	assert "ch1 = BotCharacterFromHandle(handle1);" in interpolate
	assert "ch2 = BotCharacterFromHandle(handle2);" in interpolate
	assert "out = (bot_character_t *) GetClearedMemory(sizeof(bot_character_t) +" in interpolate
	assert "out->skill = desiredskill;" in interpolate
	assert "strcpy(out->filename, ch1->filename);" in interpolate
	assert "botcharacters[handle] = out;" in interpolate
	assert "scale = (float) (desiredskill - ch1->skill) / (ch2->skill - ch1->skill);" in interpolate
	assert "if (ch1->c[i].type == CT_FLOAT && ch2->c[i].type == CT_FLOAT)" in interpolate
	assert "out->c[i].value._float = ch1->c[i].value._float +" in interpolate
	assert "else if (ch1->c[i].type == CT_INTEGER)" in interpolate
	assert "out->c[i].value.integer = ch1->c[i].value.integer;" in interpolate
	assert "else if (ch1->c[i].type == CT_STRING)" in interpolate
	assert "out->c[i].value.string = (char *) GetMemory(strlen(ch1->c[i].value.string)+1);" in interpolate
	assert "strcpy(out->c[i].value.string, ch1->c[i].value.string);" in interpolate

	assert "if (skill < 1.0) skill = 1.0;" in load_public
	assert "else if (skill > 5.0) skill = 5.0;" in load_public
	assert "if (skill == 1.0 || skill == 4.0 || skill == 5.0)" in load_public
	assert "return BotLoadCharacterSkill(charfile, skill);" in load_public
	assert "handle = BotFindCachedCharacter(charfile, skill);" in load_public
	assert "if (skill < 4.0)" in load_public
	assert "firstskill = BotLoadCharacterSkill(charfile, 1);" in load_public
	assert "secondskill = BotLoadCharacterSkill(charfile, 4);" in load_public
	assert "firstskill = BotLoadCharacterSkill(charfile, 4);" in load_public
	assert "secondskill = BotLoadCharacterSkill(charfile, 5);" in load_public
	assert "handle = BotInterpolateCharacters(firstskill, secondskill, skill);" in load_public
	assert "BotDumpCharacter(botcharacters[handle]);" in load_public

	assert "ch = BotCharacterFromHandle(character);" in check_index
	assert "if (index < 0 || index >= MAX_CHARACTERISTICS)" in check_index
	assert 'botimport.Print(PRT_ERROR, "characteristic %d does not exist\\n", index);' in check_index
	assert "if (!ch->c[index].type)" in check_index
	assert 'botimport.Print(PRT_ERROR, "characteristic %d is not initialized\\n", index);' in check_index

	assert "if (!CheckCharacteristicIndex(character, index)) return 0;" in char_float
	assert "return (float) ch->c[index].value.integer;" in char_float
	assert "return ch->c[index].value._float;" in char_float
	assert 'botimport.Print(PRT_ERROR, "characteristic %d is not a float\\n", index);' in char_float
	assert "if (min > max)" in char_bfloat
	assert 'botimport.Print(PRT_ERROR, "cannot bound characteristic %d between %f and %f\\n", index, min, max);' in char_bfloat
	assert "value = Characteristic_Float(character, index);" in char_bfloat
	assert "if (value < min) return min;" in char_bfloat
	assert "if (value > max) return max;" in char_bfloat

	assert "if (!CheckCharacteristicIndex(character, index)) return 0;" in char_integer
	assert "return ch->c[index].value.integer;" in char_integer
	assert "return (int) ch->c[index].value._float;" in char_integer
	assert 'botimport.Print(PRT_ERROR, "characteristic %d is not a integer\\n", index);' in char_integer
	assert "if (min > max)" in char_binteger
	assert 'botimport.Print(PRT_ERROR, "cannot bound characteristic %d between %d and %d\\n", index, min, max);' in char_binteger
	assert "value = Characteristic_Integer(character, index);" in char_binteger
	assert "if (value < min) return min;" in char_binteger
	assert "if (value > max) return max;" in char_binteger

	assert "if (!CheckCharacteristicIndex(character, index)) return;" in char_string
	assert "if (ch->c[index].type == CT_STRING)" in char_string
	assert "strncpy(buf, ch->c[index].value.string, size-1);" in char_string
	assert "buf[size-1] = '\\0';" in char_string
	assert 'botimport.Print(PRT_ERROR, "characteristic %d is not a string\\n", index);' in char_string
	assert "for (handle = 1; handle <= MAX_CLIENTS; handle++)" in shutdown
	assert "BotFreeCharacter2(handle);" in shutdown

	for evidence in (
		"00496e4e                  if (var_38 != 3 || (var_34 & 0x1000) == 0)",
		"00496e4e                  else if (var_30 s< 0 || var_30 s> 0x50)",
		"00496e7c                      if (*(edi + result + 0x44) != 0)",
		"00497093              x87_r7 - x87_r6",
		"004970a1                  long double x87_r4_3 = fabs(fconvert.t(*(esi_1 + 0x40)) - x87_r7)",
		"004973ba  sub_496ab0(*((result << 2) + &data_16de560), *((eax << 2) + &data_16de560))",
		"004974fb  long double x87_r7_2 = (x87_r7 - fconvert.t(*(ebx_1 + 0x40)))",
		"00497510      eax_4.b = *(ebx_2 + esi)",
		"0049751a      if (eax_4.b == 2 && *(esi + ecx_4) == eax_4.b)",
		"00497532          *esi = eax_4.b",
		"0049753f          *esi = eax_4.b",
		"004976a3                                  sub_4973d0(edi_1, eax_4, fconvert.s(fconvert.t(arg2)))",
		"004976bf                                  sub_496950(*((eax_7 << 2) + &data_16de560))",
		"00497740  if (*(eax_1 + (arg2 << 3) + 0x44) != 0)",
		"004977d6  if (sub_4976f0(arg1, arg2) != 0)",
		"00497894  long double x87_r7_5 = fconvert.t(fconvert.s(sub_497780(arg1, arg2)))",
		"00497916  if (sub_4976f0(arg1, arg2) != 0)",
		"00497a27  int32_t eax_3 = sub_4976f0(arg1, arg2)",
	):
		assert evidence in hlil


def test_character_api_export_import_and_ai_consumer_wiring_are_pinned() -> None:
	interface = _read(BOTLIB_INTERFACE)
	public_api = _read(BOTLIB_PUBLIC)
	header = _read(GAME_AI_CHAR_H)
	ai_main = _read(GAME_AI_MAIN)
	g_local = _read(GAME_G_LOCAL)
	g_public = _read(GAME_G_PUBLIC)
	g_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	server_imports = _read(SERVER_QL_GAME_IMPORTS)
	hlil = _read(QL_STEAM_HLIL_PART03)

	shutdown = _extract_function_block(interface, "int Export_BotLibShutdown(void)")
	init_export = _extract_function_block(interface, "static void Init_AI_Export( ai_export_t *ai )")
	bot_setup = _extract_function_block(ai_main, "int BotAISetupClient(int client, struct bot_settings_s *settings, qboolean restart)")
	bot_shutdown = _extract_function_block(ai_main, "int BotAIShutdownClient(int client, qboolean restart)")
	syscall_float = _extract_function_block(g_syscalls, "float trap_Characteristic_Float(int character, int index)")
	syscall_bfloat = _extract_function_block(g_syscalls, "float trap_Characteristic_BFloat(int character, int index, float min, float max)")

	assert "int BotLoadCharacter(char *charfile, float skill);" in header
	assert "void BotFreeCharacter(int character);" in header
	assert "float Characteristic_Float(int character, int index);" in header
	assert "float Characteristic_BFloat(int character, int index, float min, float max);" in header
	assert "int Characteristic_Integer(int character, int index);" in header
	assert "int Characteristic_BInteger(int character, int index, int min, int max);" in header
	assert "void Characteristic_String(int character, int index, char *buf, int size);" in header
	assert "void BotShutdownCharacters(void);" in header

	_assert_order(
		public_api,
		"int\t\t(*BotLoadCharacter)(char *charfile, float skill);",
		"void\t(*BotFreeCharacter)(int character);",
		"float\t(*Characteristic_Float)(int character, int index);",
		"float\t(*Characteristic_BFloat)(int character, int index, float min, float max);",
		"int\t\t(*Characteristic_Integer)(int character, int index);",
		"int\t\t(*Characteristic_BInteger)(int character, int index, int min, int max);",
		"void\t(*Characteristic_String)(int character, int index, char *buf, int size);",
		"int\t\t(*BotAllocChatState)(void);",
	)
	_assert_order(
		init_export,
		"ai->BotLoadCharacter = BotLoadCharacter;",
		"ai->BotFreeCharacter = BotFreeCharacter;",
		"ai->Characteristic_Float = Characteristic_Float;",
		"ai->Characteristic_BFloat = Characteristic_BFloat;",
		"ai->Characteristic_Integer = Characteristic_Integer;",
		"ai->Characteristic_BInteger = Characteristic_BInteger;",
		"ai->Characteristic_String = Characteristic_String;",
		"ai->BotAllocChatState = BotAllocChatState;",
	)
	_assert_order(
		shutdown,
		"BotShutdownWeights();\t\t//be_ai_weight.c",
		"BotShutdownCharacters();\t//be_ai_char.c",
		"AAS_Shutdown();",
	)

	assert "\tBOTLIB_AI_LOAD_CHARACTER = 500," in g_public
	assert "\tBOTLIB_AI_CHARACTERISTIC_STRING," in g_public
	assert "\tG_QL_IMPORT_BOTLIB_AI_LOAD_CHARACTER = 110," in g_public
	assert "\tG_QL_IMPORT_BOTLIB_AI_FREE_CHARACTER = 111," in g_public
	assert "\tG_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_FLOAT = 112," in g_public
	assert "\tG_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BFLOAT = 113," in g_public
	assert "\tG_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_INTEGER = 114," in g_public
	assert "\tG_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_BINTEGER = 115," in g_public
	assert "\tG_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_STRING = 116," in g_public
	assert "case BOTLIB_AI_LOAD_CHARACTER: return G_QL_IMPORT_BOTLIB_AI_LOAD_CHARACTER;" in g_syscalls
	assert "case BOTLIB_AI_CHARACTERISTIC_STRING: return G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_STRING;" in g_syscalls
	assert "int\t\ttrap_BotLoadCharacter(char *charfile, float skill);" in g_local
	assert "void\ttrap_BotFreeCharacter(int character);" in g_local
	assert "float\ttrap_Characteristic_BFloat(int character, int index, float min, float max);" in g_local
	assert "void\ttrap_Characteristic_String(int character, int index, char *buf, int size);" in g_local

	assert "return syscall( BOTLIB_AI_LOAD_CHARACTER, charfile, PASSFLOAT(skill));" in g_syscalls
	assert "syscall( BOTLIB_AI_FREE_CHARACTER, character );" in g_syscalls
	assert "G_GetMappedImport( BOTLIB_AI_CHARACTERISTIC_FLOAT, NULL )" in syscall_float
	assert "temp = syscall( BOTLIB_AI_CHARACTERISTIC_FLOAT, character, index );" in syscall_float
	assert "G_GetMappedImport( BOTLIB_AI_CHARACTERISTIC_BFLOAT, NULL )" in syscall_bfloat
	assert "temp = syscall( BOTLIB_AI_CHARACTERISTIC_BFLOAT, character, index, PASSFLOAT(min), PASSFLOAT(max) );" in syscall_bfloat
	assert "return syscall( BOTLIB_AI_CHARACTERISTIC_INTEGER, character, index );" in g_syscalls
	assert "return syscall( BOTLIB_AI_CHARACTERISTIC_BINTEGER, character, index, min, max );" in g_syscalls
	assert "syscall( BOTLIB_AI_CHARACTERISTIC_STRING, character, index, buf, size );" in g_syscalls

	assert "case BOTLIB_AI_LOAD_CHARACTER:" in server_game
	assert "return botlib_export->ai.BotLoadCharacter( VMA(1), VMF(2) );" in server_game
	assert "case BOTLIB_AI_FREE_CHARACTER:" in server_game
	assert "botlib_export->ai.BotFreeCharacter( args[1] );" in server_game
	assert "return FloatAsInt( botlib_export->ai.Characteristic_Float( args[1], args[2] ) );" in server_game
	assert "return FloatAsInt( botlib_export->ai.Characteristic_BFloat( args[1], args[2], VMF(3), VMF(4) ) );" in server_game
	assert "return botlib_export->ai.Characteristic_Integer( args[1], args[2] );" in server_game
	assert "return botlib_export->ai.Characteristic_BInteger( args[1], args[2], args[3], args[4] );" in server_game
	assert "botlib_export->ai.Characteristic_String( args[1], args[2], VMA(3), args[4] );" in server_game
	assert "[BOTLIB_AI_LOAD_CHARACTER] = (ql_import_f)QL_G_trap_BotLoadCharacter," in server_game
	assert "[BOTLIB_AI_CHARACTERISTIC_STRING] = (ql_import_f)QL_G_trap_Characteristic_String," in server_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_LOAD_CHARACTER] = (ql_import_f)QL_G_trap_BotLoadCharacter;" in server_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_CHARACTERISTIC_STRING] = (ql_import_f)QL_G_trap_Characteristic_String;" in server_game

	assert "static int QDECL QL_G_trap_BotLoadCharacter( char *charfile, float skill )" in server_imports
	assert "return G_Import_Syscall( BOTLIB_AI_LOAD_CHARACTER, charfile, QL_G_PASSFLOAT(skill));" in server_imports
	assert "static void QDECL QL_G_trap_BotFreeCharacter( int character )" in server_imports
	assert "G_Import_Syscall( BOTLIB_AI_FREE_CHARACTER, character );" in server_imports
	assert "temp = G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_FLOAT, character, index );" in server_imports
	assert "temp = G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_BFLOAT, character, index, QL_G_PASSFLOAT(min), QL_G_PASSFLOAT(max) );" in server_imports
	assert "return G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_INTEGER, character, index );" in server_imports
	assert "return G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_BINTEGER, character, index, min, max );" in server_imports
	assert "G_Import_Syscall( BOTLIB_AI_CHARACTERISTIC_STRING, character, index, buf, size );" in server_imports

	assert "bs->character = trap_BotLoadCharacter(settings->characterfile, settings->skill);" in bot_setup
	assert "trap_Characteristic_String(bs->character, CHARACTERISTIC_ITEMWEIGHTS, filename, MAX_PATH);" in bot_setup
	assert "trap_Characteristic_String(bs->character, CHARACTERISTIC_WEAPONWEIGHTS, filename, MAX_PATH);" in bot_setup
	assert "trap_Characteristic_String(bs->character, CHARACTERISTIC_CHAT_FILE, filename, MAX_PATH);" in bot_setup
	assert "trap_Characteristic_String(bs->character, CHARACTERISTIC_CHAT_NAME, name, MAX_PATH);" in bot_setup
	assert "trap_Characteristic_String(bs->character, CHARACTERISTIC_GENDER, gender, MAX_PATH);" in bot_setup
	assert "bs->walker = trap_Characteristic_BFloat(bs->character, CHARACTERISTIC_WALKER, 0, 1);" in bot_setup
	assert "if (bs->character) trap_BotFreeCharacter(bs->character);" in bot_setup
	assert "trap_BotFreeCharacter(bs->character);" in bot_shutdown

	for evidence in (
		"004a8110  *arg1 = sub_497590",
		"004a8116  arg1[1] = sub_496a80",
		"004a811d  arg1[2] = sub_497780",
		"004a8124  arg1[3] = sub_497810",
		"004a812b  arg1[4] = sub_4978c0",
		"004a8132  arg1[5] = sub_497950",
		"004a8139  arg1[6] = sub_4979e0",
		"004a8140  arg1[7] = sub_49c440",
	):
		assert evidence in hlil
