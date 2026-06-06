from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOTLIB_LIBVAR = REPO_ROOT / "src" / "code" / "botlib" / "l_libvar.c"
BOTLIB_LIBVAR_H = REPO_ROOT / "src" / "code" / "botlib" / "l_libvar.h"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_AAS_MAIN = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_main.c"
BOTLIB_AAS_MOVE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_move.c"
BOTLIB_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
GAME_AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
GAME_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
SERVER_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SERVER_NATIVE_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"
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
QAGAME_GHIDRA_TOP = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "decompile_top_functions.c"
)


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


def test_botlib_libvar_runtime_matches_retail_hlil_body_shapes() -> None:
	libvar = _read(BOTLIB_LIBVAR)
	libvar_h = _read(BOTLIB_LIBVAR_H)
	hlil = _read(QL_STEAM_HLIL_PART03)
	functions = _read(QL_STEAM_FUNCTIONS)

	string_value = _extract_function_block(libvar, "float LibVarStringValue(char *string)")
	alloc = _extract_function_block(libvar, "libvar_t *LibVarAlloc(char *var_name)")
	dealloc = _extract_function_block(libvar, "void LibVarDeAlloc(libvar_t *v)")
	dealloc_all = _extract_function_block(libvar, "void LibVarDeAllocAll(void)")
	get = _extract_function_block(libvar, "libvar_t *LibVarGet(char *var_name)")
	get_string = _extract_function_block(libvar, "char *LibVarGetString(char *var_name)")
	get_value = _extract_function_block(libvar, "float LibVarGetValue(char *var_name)")
	libvar_fn = _extract_function_block(libvar, "libvar_t *LibVar(char *var_name, char *value)")
	string_fn = _extract_function_block(libvar, "char *LibVarString(char *var_name, char *value)")
	value_fn = _extract_function_block(libvar, "float LibVarValue(char *var_name, char *value)")
	set_fn = _extract_function_block(libvar, "void LibVarSet(char *var_name, char *value)")
	changed = _extract_function_block(libvar, "qboolean LibVarChanged(char *var_name)")
	set_not_modified = _extract_function_block(libvar, "void LibVarSetNotModified(char *var_name)")

	assert "char\t\t*name;" in libvar_h
	assert "char\t\t*string;" in libvar_h
	assert "int\t\tflags;" in libvar_h
	assert "qboolean\tmodified;" in libvar_h
	assert "float\t\tvalue;" in libvar_h
	assert "struct\tlibvar_s *next;" in libvar_h

	assert "int dotfound = 0;" in string_value
	assert "float value = 0;" in string_value
	assert "if (dotfound || *string != '.')" in string_value
	assert "return 0;" in string_value
	assert "dotfound = 10;" in string_value
	assert "value = value + (float) (*string - '0') / (float) dotfound;" in string_value
	assert "dotfound *= 10;" in string_value
	assert "value = value * 10.0 + (float) (*string - '0');" in string_value

	assert "GetMemory(sizeof(libvar_t) + strlen(var_name) + 1)" in alloc
	assert "Com_Memset(v, 0, sizeof(libvar_t));" in alloc
	assert "v->name = (char *) v + sizeof(libvar_t);" in alloc
	assert "v->next = libvarlist;" in alloc
	assert "libvarlist = v;" in alloc

	assert "if (v->string) FreeMemory(v->string);" in dealloc
	assert "FreeMemory(v);" in dealloc
	assert "for (v = libvarlist; v; v = libvarlist)" in dealloc_all
	assert "libvarlist = libvarlist->next;" in dealloc_all
	assert "LibVarDeAlloc(v);" in dealloc_all
	assert "libvarlist = NULL;" in dealloc_all

	assert "for (v = libvarlist; v; v = v->next)" in get
	assert "if (!Q_stricmp(v->name, var_name))" in get
	assert "return NULL;" in get

	assert "v = LibVarGet(var_name);" in get_string
	assert "return v->string;" in get_string
	assert 'return "";' in get_string
	assert "v = LibVarGet(var_name);" in get_value
	assert "return v->value;" in get_value
	assert "return 0;" in get_value

	assert "v = LibVarGet(var_name);" in libvar_fn
	assert "if (v) return v;" in libvar_fn
	assert "v = LibVarAlloc(var_name);" in libvar_fn
	assert "v->string = (char *) GetMemory(strlen(value) + 1);" in libvar_fn
	assert "v->value = LibVarStringValue(v->string);" in libvar_fn
	assert "v->modified = qtrue;" in libvar_fn
	assert "return v;" in libvar_fn

	assert "v = LibVar(var_name, value);" in string_fn
	assert "return v->string;" in string_fn
	assert "v = LibVar(var_name, value);" in value_fn
	assert "return v->value;" in value_fn

	assert "v = LibVarGet(var_name);" in set_fn
	assert "FreeMemory(v->string);" in set_fn
	assert "v = LibVarAlloc(var_name);" in set_fn
	assert "v->string = (char *) GetMemory(strlen(value) + 1);" in set_fn
	assert "v->value = LibVarStringValue(v->string);" in set_fn
	assert "v->modified = qtrue;" in set_fn

	assert "return v->modified;" in changed
	assert "return qfalse;" in changed
	assert "v->modified = qfalse;" in set_not_modified

	for expected in (
		"004a8500    long double sub_4a8500(int32_t arg1)",
		"004a852d              if (ecx != 0 || eax.b != 0x2e)",
		"004a852f              ecx = 0xa",
		"004a854f              long double x87_r5_2 = float.t(sx.d(*edx) - 0x30) / float.t(var_c)",
		"004a8582  return fconvert.t(var_8)",
		"004a8588                  return result",
		"004a8590    void* sub_4a8590(char* arg1)",
		"004a85ad  void* result = sub_4a89a0(eax - &eax[1] + 0x19)",
		"004a85b9  sub_4c95e0(result, 0, 0x18)",
		"004a85df  *(result + 0x14) = data_16dd7e8",
		"004a85e3  data_16dd7e8 = result",
		"004a85f0    void sub_4a85f0()",
		"004a85f9  for (void* i = data_16dd7e8; i != 0; i = data_16dd7e8)",
		"004a8610          sub_4a8aa0(eax_2)",
		"004a8619      sub_4a8aa0(i)",
		"004a862b  data_16dd7e8 = 0",
		"004a8640    int32_t sub_4a8640(char* arg1)",
		"004a864d  for (int32_t* i = data_16dd7e8; i != 0; i = i[5])",
		"004a8660      if (sub_4d9060(*i, arg1) == 0)",
		"004a8678          return i[1]",
		"004a8671  return &data_54f9da",
		"004a8680    long double sub_4a8680(char* arg1)",
		"004a86b5          return fconvert.t(i[4])",
		"004a86ae  return float.t(0)",
		"004a86c0    int32_t* sub_4a86c0(char* arg1, char* arg2)",
		"004a86f2  i = sub_4a8590(arg1)",
		"004a870b  void* eax_7 = sub_4a89a0(eax_4 - &eax_4[1] + 1)",
		"004a8733  i[4] = fconvert.s(sub_4a8500(i[1]))",
		"004a8739  i[3] = 1",
		"004a8750    int32_t sub_4a8750(char* arg1, char* arg2)",
		"004a8767  return sub_4a86c0(arg1, arg2)[1]",
		"004a8770    long double sub_4a8770(char* arg1, char* arg2)",
		"004a8787  return fconvert.t(sub_4a86c0(arg1, arg2)[4])",
		"004a8790    int32_t sub_4a8790(char* arg1, char* arg2)",
		"004a881a              sub_4a8aa0(esi[1])",
		"004a87fe  st0, result = sub_4a8500(edi_1[1])",
		"004a8803  edi_1[4] = fconvert.s(st0)",
		"004a8809  edi_1[3] = 1",
	):
		assert expected in hlil

	for expected in (
		"FUN_004a8500,004a8500,137,0,unknown",
		"FUN_004a8590,004a8590,94,0,unknown",
		"FUN_004a85f0,004a85f0,68,0,unknown",
		"FUN_004a8640,004a8640,57,0,unknown",
		"FUN_004a8680,004a8680,54,0,unknown",
		"FUN_004a86c0,004a86c0,134,0,unknown",
		"FUN_004a8750,004a8750,24,0,unknown",
		"FUN_004a8770,004a8770,24,0,unknown",
		"FUN_004a8790,004a8790,145,0,unknown",
	):
		assert expected in functions


def test_botlib_libvar_export_and_qagame_bridge_wiring_match_retail_evidence() -> None:
	interface = _read(BOTLIB_INTERFACE)
	botlib_public = _read(BOTLIB_PUBLIC)
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	server_imports = _read(SERVER_NATIVE_IMPORTS)
	hlil = _read(QL_STEAM_HLIL_PART03)
	qagame_hlil = _read(QAGAME_HLIL)
	qagame_ghidra = _read(QAGAME_GHIDRA_TOP)
	functions = _read(QL_STEAM_FUNCTIONS)
	aliases = json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]

	assert aliases["sub_4A7E40"] == "Export_BotLibVarSet"
	assert aliases["sub_4A7E60"] == "Export_BotLibVarGet"

	export_set = _extract_function_block(interface, "int Export_BotLibVarSet(char *var_name, char *value)")
	export_get = _extract_function_block(interface, "int Export_BotLibVarGet(char *var_name, char *value, int size)")
	get_api = _extract_function_block(interface, "botlib_export_t *GetBotLibAPI(int apiVersion, botlib_import_t *import)")
	map_native_import = _extract_function_block(game_syscalls, "static int G_MapNativeImport( int arg, const intptr_t *stack )")

	assert "LibVarSet(var_name, value);" in export_set
	assert "return BLERR_NOERROR;" in export_set

	assert "varvalue = LibVarGetString(var_name);" in export_get
	assert "strncpy(value, varvalue, size-1);" in export_get
	assert "value[size-1] = '\\0';" in export_get
	assert "return BLERR_NOERROR;" in export_get

	assert "be_botlib_export.BotLibVarSet = Export_BotLibVarSet;" in get_api
	assert "be_botlib_export.BotLibVarGet = Export_BotLibVarGet;" in get_api
	assert "int (*BotLibVarSet)(char *var_name, char *value);" in botlib_public
	assert "int (*BotLibVarGet)(char *var_name, char *value, int size);" in botlib_public

	assert "case BOTLIB_LIBVAR_SET: return G_QL_IMPORT_BOTLIB_LIBVAR_SET;" in map_native_import
	assert "case BOTLIB_LIBVAR_GET: return G_QL_IMPORT_BOTLIB_LIBVAR_GET;" in map_native_import
	assert "int trap_BotLibVarSet(char *var_name, char *value)" in game_syscalls
	assert "return syscall( BOTLIB_LIBVAR_SET, var_name, value );" in game_syscalls
	assert "int trap_BotLibVarGet(char *var_name, char *value, int size)" in game_syscalls
	assert "return syscall( BOTLIB_LIBVAR_GET, var_name, value, size );" in game_syscalls

	assert "BOTLIB_LIBVAR_SET," in game_public
	assert "BOTLIB_LIBVAR_GET," in game_public
	assert "G_QL_IMPORT_BOTLIB_LIBVAR_SET = 51," in game_public
	assert "G_QL_IMPORT_BOTLIB_LIBVAR_GET = 52," in game_public

	assert "case BOTLIB_LIBVAR_SET:" in server_game
	assert "return botlib_export->BotLibVarSet( VMA(1), VMA(2) );" in server_game
	assert "case BOTLIB_LIBVAR_GET:" in server_game
	assert "return botlib_export->BotLibVarGet( VMA(1), VMA(2), args[3] );" in server_game
	assert "[BOTLIB_LIBVAR_SET] = (ql_import_f)QL_G_trap_BotLibVarSet," in server_game
	assert "[BOTLIB_LIBVAR_GET] = (ql_import_f)QL_G_trap_BotLibVarGet," in server_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_LIBVAR_SET] = (ql_import_f)QL_G_trap_BotLibVarSet;" in server_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_LIBVAR_GET] = (ql_import_f)QL_G_trap_BotLibVarGet;" in server_game

	assert "static int QDECL QL_G_trap_BotLibVarSet( char *var_name, char *value )" in server_imports
	assert "return G_Import_Syscall( BOTLIB_LIBVAR_SET, var_name, value );" in server_imports
	assert "static int QDECL QL_G_trap_BotLibVarGet( char *var_name, char *value, int size )" in server_imports
	assert "return G_Import_Syscall( BOTLIB_LIBVAR_GET, var_name, value, size );" in server_imports

	for expected in (
		"004a7e40    int32_t sub_4a7e40(char* arg1, char* arg2)",
		"004a7e4b  sub_4a8790(arg1, arg2)",
		"004a7e56  return 0",
		"004a7e60    int32_t sub_4a7e60(char* arg1, int32_t arg2, int32_t arg3)",
		"004a7e7a  strncpy(arg2, sub_4a8640(arg1), arg3 - 1)",
		"004a7e83  *(arg2 + arg3 - 1) = 0",
		"004a7e8d  return 0",
	):
		assert expected in hlil

	assert "FUN_004a7e40,004a7e40,23,0,unknown" in functions
	assert "FUN_004a7e60,004a7e60,46,0,unknown" in functions

	assert '(*(data_104b13ac + 0xcc))("bot_showPath", 0x104b1cd4)' in qagame_hlil
	assert '(*(data_104b13ac + 0xcc))("maxclients", &var_94)' in qagame_hlil
	assert '(*(data_104b13ac + 0xcc))("bot_reloadcharacters", &var_94)' in qagame_hlil
	assert '(**(code **)(DAT_104b13ac + 0xcc))("memorydump",&DAT_1007d1d8);' in qagame_ghidra
	assert '(**(code **)(DAT_104b13ac + 0xcc))("maxclients",local_94);' in qagame_ghidra
	assert '(**(code **)(DAT_104b13ac + 0xcc))("bot_reloadcharacters",local_94);' in qagame_ghidra
	assert "(*(data_104b13ac + 0xd0))(" not in qagame_hlil
	assert "(**(code **)(DAT_104b13ac + 0xd0))" not in qagame_ghidra


def test_botlib_libvar_consumers_match_retail_default_propagation() -> None:
	interface = _read(BOTLIB_INTERFACE)
	aas_main = _read(BOTLIB_AAS_MAIN)
	aas_move = _read(BOTLIB_AAS_MOVE)
	ai_main = _read(GAME_AI_MAIN)
	hlil = _read(QL_STEAM_HLIL_PART03)
	qagame_hlil = _read(QAGAME_HLIL)
	qagame_ghidra = _read(QAGAME_GHIDRA_TOP)
	functions = _read(QL_STEAM_FUNCTIONS)

	botlib_setup = _extract_function_block(interface, "int Export_BotLibSetup(void)")
	botlib_shutdown = _extract_function_block(interface, "int Export_BotLibShutdown(void)")
	aas_continue_init = _extract_function_block(aas_main, "void AAS_ContinueInit(float time)")
	aas_start_frame = _extract_function_block(aas_main, "int AAS_StartFrame(float time)")
	aas_setup = _extract_function_block(aas_main, "int AAS_Setup(void)")
	aas_init_settings = _extract_function_block(aas_move, "void AAS_InitSettings(void)")
	bot_init_library = _extract_function_block(ai_main, "int BotInitLibrary(void)")

	assert 'bot_developer = LibVarGetValue("bot_developer");' in botlib_setup
	assert 'bot_showPath = LibVarGetValue("bot_showPath");' in botlib_setup
	assert 'botlibglobals.maxclients = (int) LibVarValue("maxclients", "128");' in botlib_setup
	assert 'botlibglobals.maxentities = (int) LibVarValue("maxentities", "1024");' in botlib_setup
	assert "errnum = AAS_Setup();" in botlib_setup
	assert "errnum = EA_Setup();" in botlib_setup

	assert "AAS_Shutdown();" in botlib_shutdown
	assert "EA_Shutdown();" in botlib_shutdown
	assert "LibVarDeAllocAll();" in botlib_shutdown
	assert "PC_RemoveAllGlobalDefines();" in botlib_shutdown

	for expected in (
		'trap_Cvar_VariableStringBuffer("sv_maxclients", buf, sizeof(buf));',
		'if (!strlen(buf)) strcpy(buf, "8");',
		'trap_BotLibVarSet("maxclients", buf);',
		'Com_sprintf(buf, sizeof(buf), "%d", MAX_GENTITIES);',
		'trap_BotLibVarSet("maxentities", buf);',
		'trap_Cvar_VariableStringBuffer("sv_mapChecksum", buf, sizeof(buf));',
		'if (strlen(buf)) trap_BotLibVarSet("sv_mapChecksum", buf);',
		'trap_Cvar_VariableStringBuffer("max_aaslinks", buf, sizeof(buf));',
		'if (strlen(buf)) trap_BotLibVarSet("max_aaslinks", buf);',
		'trap_Cvar_VariableStringBuffer("max_levelitems", buf, sizeof(buf));',
		'if (strlen(buf)) trap_BotLibVarSet("max_levelitems", buf);',
		'trap_Cvar_VariableStringBuffer("g_gametype", buf, sizeof(buf));',
		'if (!strlen(buf)) strcpy(buf, "0");',
		'trap_BotLibVarSet("g_gametype", buf);',
		'trap_BotLibVarSet("bot_developer", bot_developer.string);',
		'trap_BotLibVarSet("bot_showPath", "0");',
		'trap_Cvar_VariableStringBuffer("bot_log", buf, sizeof(buf));',
		'trap_BotLibVarSet("bot_log", buf);',
		'trap_Cvar_VariableStringBuffer("bot_nochat", buf, sizeof(buf));',
		'if (strlen(buf)) trap_BotLibVarSet("nochat", "0");',
		'trap_Cvar_VariableStringBuffer("bot_visualizejumppads", buf, sizeof(buf));',
		'if (strlen(buf)) trap_BotLibVarSet("bot_visualizejumppads", buf);',
		'trap_Cvar_VariableStringBuffer("bot_forceclustering", buf, sizeof(buf));',
		'if (strlen(buf)) trap_BotLibVarSet("forceclustering", buf);',
		'trap_Cvar_VariableStringBuffer("bot_forcereachability", buf, sizeof(buf));',
		'if (strlen(buf)) trap_BotLibVarSet("forcereachability", buf);',
		'trap_Cvar_VariableStringBuffer("bot_forcewrite", buf, sizeof(buf));',
		'if (strlen(buf)) trap_BotLibVarSet("forcewrite", buf);',
		'trap_Cvar_VariableStringBuffer("bot_aasoptimize", buf, sizeof(buf));',
		'if (strlen(buf)) trap_BotLibVarSet("aasoptimize", buf);',
		'trap_Cvar_VariableStringBuffer("bot_saveroutingcache", buf, sizeof(buf));',
		'if (strlen(buf)) trap_BotLibVarSet("saveroutingcache", buf);',
		'trap_Cvar_VariableStringBuffer("bot_reloadcharacters", buf, sizeof(buf));',
		'trap_BotLibVarSet("bot_reloadcharacters", buf);',
		'trap_Cvar_VariableStringBuffer("fs_basepath", buf, sizeof(buf));',
		'if (strlen(buf)) trap_BotLibVarSet("basedir", buf);',
		'trap_Cvar_VariableStringBuffer("fs_game", buf, sizeof(buf));',
		'if (strlen(buf)) trap_BotLibVarSet("gamedir", buf);',
		'trap_Cvar_VariableStringBuffer("fs_cdpath", buf, sizeof(buf));',
		'if (strlen(buf)) trap_BotLibVarSet("cddir", buf);',
		'trap_BotLibDefine("MISSIONPACK");',
		"return trap_BotLibSetup();",
	):
		assert expected in bot_init_library

	assert 'if (aasworld.savefile || ((int)LibVarGetValue("forcewrite")))' in aas_continue_init
	assert 'if ((int)LibVarValue("aasoptimize", "0")) AAS_Optimize();' in aas_continue_init

	for expected in (
		'if (LibVarGetValue("showcacheupdates"))',
		'LibVarSet("showcacheupdates", "0");',
		'if (LibVarGetValue("showmemoryusage"))',
		'LibVarSet("showmemoryusage", "0");',
		'if (LibVarGetValue("memorydump"))',
		'LibVarSet("memorydump", "0");',
		'bot_showPath = LibVarGetValue("bot_showPath");',
		"if (saveroutingcache->value)",
		'LibVarSet("saveroutingcache", "0");',
	):
		assert expected in aas_start_frame

	assert 'aasworld.maxclients = (int) LibVarValue("maxclients", "128");' in aas_setup
	assert 'aasworld.maxentities = (int) LibVarValue("maxentities", "1024");' in aas_setup
	assert 'saveroutingcache = LibVar("saveroutingcache", "0");' in aas_setup

	for expected in (
		'LibVarValue("phys_friction", "6")',
		'LibVarValue("phys_stopspeed", "100")',
		'LibVarValue("phys_gravity", "800")',
		'LibVarValue("phys_waterfriction", "1")',
		'LibVarValue("phys_watergravity", "400")',
		'LibVarValue("phys_maxvelocity", "320")',
		'LibVarValue("phys_maxwalkvelocity", "320")',
		'LibVarValue("phys_maxcrouchvelocity", "100")',
		'LibVarValue("phys_maxswimvelocity", "150")',
		'LibVarValue("phys_walkaccelerate", "10")',
		'LibVarValue("phys_airaccelerate", "1")',
		'LibVarValue("phys_swimaccelerate", "4")',
		'LibVarValue("phys_maxstep", "19")',
		'LibVarValue("phys_maxsteepness", "0.7")',
		'LibVarValue("phys_maxwaterjump", "18")',
		'LibVarValue("phys_maxbarrier", "33")',
		'LibVarValue("phys_jumpvel", "270")',
		'LibVarValue("phys_falldelta5", "40")',
		'LibVarValue("phys_falldelta10", "60")',
		'LibVarValue("rs_waterjump", "400")',
		'LibVarValue("rs_teleport", "50")',
		'LibVarValue("rs_barrierjump", "100")',
		'LibVarValue("rs_startcrouch", "300")',
		'LibVarValue("rs_startgrapple", "500")',
		'LibVarValue("rs_startwalkoffledge", "70")',
		'LibVarValue("rs_startjump", "300")',
		'LibVarValue("rs_rocketjump", "500")',
		'LibVarValue("rs_bfgjump", "500")',
		'LibVarValue("rs_jumppad", "250")',
		'LibVarValue("rs_aircontrolledjumppad", "300")',
		'LibVarValue("rs_funcbob", "300")',
		'LibVarValue("rs_startelevator", "50")',
		'LibVarValue("rs_falldamage5", "300")',
		'LibVarValue("rs_falldamage10", "500")',
		'LibVarValue("rs_maxfallheight", "0")',
		'LibVarValue("rs_maxjumpfallheight", "450")',
	):
		assert expected in aas_init_settings

	for expected in (
		"00486210    void sub_486210(float arg1)",
		'0048625f              eax_1 = sub_526000(sub_4a8680("forcewrite"))',
		'00486281              if (sub_526000(sub_4a8770("aasoptimize", U"0")) != 0)',
		"004862e0    int32_t sub_4862e0(float arg1)",
		'00486321      st0_1, eax_1 = sub_4a8680("showcacheupdates")',
		'00486343          sub_4a8790("showcacheupdates", U"0")',
		'00486350      st0_2, eax_2 = sub_4a8680("showmemoryusage")',
		'00486372          sub_4a8790("showmemoryusage", U"0")',
		'0048637f      st0_3, eax_3 = sub_4a8680("memorydump")',
		'004863a1          sub_4a8790("memorydump", U"0")',
		'004863bb  data_16dd7ec = sub_526000(sub_4a8680("bot_showPath"))',
		'004863e2      sub_4a8790("saveroutingcache", U"0")',
		"004865b0    int32_t sub_4865b0()",
		'004865ce  data_16de9a4 = sub_526000(sub_4a8770("maxclients", "128"))',
		'004865e7  data_16de9a0 = sub_526000(sub_4a8770("maxentities", "1024"))',
		'004865f1  data_16de87c = sub_4a86c0("saveroutingcache", U"0")',
		"00486740    int32_t sub_486740()",
		'00486769  data_16de7ec = fconvert.s(sub_4a8770("phys_friction", U"6"))',
		'0048677e  data_16de7f0 = fconvert.s(sub_4a8770("phys_stopspeed", "100"))',
		'00486793  data_16de7f4 = fconvert.s(sub_4a8770("phys_gravity", "800"))',
		'004868bf  data_16de82c = fconvert.s(sub_4a8770("phys_jumpvel", "270"))',
		'00486994  data_16de854 = fconvert.s(sub_4a8770("rs_rocketjump", "500"))',
		'004869a9  data_16de858 = fconvert.s(sub_4a8770("rs_bfgjump", "500"))',
		'00486a4f  st0_35, result = sub_4a8770("rs_maxjumpfallheight", "450")',
		"004a7ce0    int32_t sub_4a7ce0()",
		'004a7cf4  data_16ddaa0 = sub_526000(sub_4a8680("bot_developer"))',
		'004a7d03  data_16dd7ec = sub_526000(sub_4a8680("bot_showPath"))',
		'004a7d53  data_16dda98 = sub_526000(sub_4a8770("maxclients", "128"))',
		'004a7d65  data_16dda94 = sub_526000(sub_4a8770("maxentities", "1024"))',
		"004a7d6a  sub_4865b0()",
		"004a7dc0    int32_t sub_4a7dc0()",
		"004a7e02  sub_486640()",
		"004a7e07  sub_4a7ca0()",
		"004a7e0c  sub_4a85f0()",
	):
		assert expected in hlil

	for expected in (
		"FUN_00486210,00486210,200,0,unknown",
		"FUN_004862e0,004862e0,276,0,unknown",
		"FUN_004865b0,004865b0,134,0,unknown",
		"FUN_00486740,00486740,798,0,unknown",
	):
		assert expected in functions

	for expected in (
		'10023c61  (*(data_104b13ac + 0xcc))("maxclients", &var_94)',
		'10023c91  (*(data_104b13ac + 0xcc))("maxentities", &var_94)',
		'10023cd5      (*(data_104b13ac + 0xcc))("sv_mapChecksum", &var_94)',
		'10023d1f      (*(data_104b13ac + 0xcc))("max_aaslinks", &var_94)',
		'10023d66      (*(data_104b13ac + 0xcc))("max_levelitems", &var_94)',
		'10023db9  (*(data_104b13ac + 0xcc))("g_gametype", &var_94)',
		'10023dd0  (*(data_104b13ac + 0xcc))("bot_developer", 0x105e3134)',
		'10023de8  (*(data_104b13ac + 0xcc))("bot_showPath", 0x104b1cd4)',
		'10023e1a  (*(data_104b13ac + 0xcc))("bot_log", &var_94)',
		'10023e34  (*(data_104b13ac + 0x34))("bot_nochat", &var_94, 0x90)',
		'10023e61      (*(data_104b13ac + 0xcc))("nochat", &data_1007d0a8)',
		'10023eb0      (*(data_104b13ac + 0xcc))("bot_visualizejumppads", &var_94)',
		'10023f00      (*(data_104b13ac + 0xcc))("forceclustering", &var_94)',
		'10023f50      (*(data_104b13ac + 0xcc))("forcereachability", &var_94)',
		'10023fa0      (*(data_104b13ac + 0xcc))("forcewrite", &var_94)',
		'10023ff0      (*(data_104b13ac + 0xcc))("aasoptimize", &var_94)',
		'1002400d  (*(data_104b13ac + 0x34))("bot_saveroutingcache", &var_94, 0x90)',
		'10024040      (*(data_104b13ac + 0xcc))("saveroutingcache", &var_94)',
		'1002405d  (*(data_104b13ac + 0x34))("bot_reloadcharacters", &var_94, 0x90)',
		'10024099  (*(data_104b13ac + 0xcc))("bot_reloadcharacters", &var_94)',
		'100240e0      (*(data_104b13ac + 0xcc))("basedir", &var_94)',
		'10024130      (*(data_104b13ac + 0xcc))("gamedir", &var_94)',
		'10024180      (*(data_104b13ac + 0xcc))("cddir", &var_94)',
	):
		assert expected in qagame_hlil

	for expected in (
		'(**(code **)(DAT_104b13ac + 0xcc))("maxclients",local_94);',
		'(**(code **)(DAT_104b13ac + 0xcc))("maxentities",local_94);',
		'(**(code **)(DAT_104b13ac + 0xcc))("sv_mapChecksum",local_94);',
		'(**(code **)(DAT_104b13ac + 0xcc))("max_aaslinks",local_94);',
		'(**(code **)(DAT_104b13ac + 0xcc))("max_levelitems",local_94);',
		'(**(code **)(DAT_104b13ac + 0xcc))("g_gametype",local_94);',
		'(**(code **)(DAT_104b13ac + 0xcc))("bot_developer",&DAT_105e3134);',
		'(**(code **)(DAT_104b13ac + 0xcc))("bot_showPath",&DAT_104b1cd4);',
		'(**(code **)(DAT_104b13ac + 0xcc))("bot_log",local_94);',
		'(**(code **)(DAT_104b13ac + 0x34))("bot_nochat",local_94,0x90);',
		'(**(code **)(DAT_104b13ac + 0xcc))("nochat",&DAT_1007d0a8);',
		'(**(code **)(DAT_104b13ac + 0xcc))("bot_visualizejumppads",local_94);',
		'(**(code **)(DAT_104b13ac + 0xcc))("forceclustering",local_94);',
		'(**(code **)(DAT_104b13ac + 0xcc))("forcereachability",local_94);',
		'(**(code **)(DAT_104b13ac + 0xcc))("forcewrite",local_94);',
		'(**(code **)(DAT_104b13ac + 0xcc))("aasoptimize",local_94);',
		'(**(code **)(DAT_104b13ac + 0x34))("bot_saveroutingcache",local_94,0x90);',
		'(**(code **)(DAT_104b13ac + 0xcc))("saveroutingcache",local_94);',
		'(**(code **)(DAT_104b13ac + 0x34))("bot_reloadcharacters",local_94,0x90);',
		'(**(code **)(DAT_104b13ac + 0xcc))("bot_reloadcharacters",local_94);',
		'(**(code **)(DAT_104b13ac + 0xcc))("basedir",local_94);',
		'(**(code **)(DAT_104b13ac + 0xcc))("gamedir",local_94);',
		'(**(code **)(DAT_104b13ac + 0xcc))("cddir",local_94);',
		'(**(code **)(DAT_104b13ac + 0xd4))("MISSIONPACK");',
		'(**(code **)(DAT_104b13ac + 0xc4))();',
	):
		assert expected in qagame_ghidra
