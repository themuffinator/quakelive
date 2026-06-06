from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOTLIB_AAS_MAIN = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_main.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_LOG = REPO_ROOT / "src" / "code" / "botlib" / "l_log.c"
BOTLIB_LOG_H = REPO_ROOT / "src" / "code" / "botlib" / "l_log.h"
BOTLIB_MEMORY = REPO_ROOT / "src" / "code" / "botlib" / "l_memory.c"
BOTLIB_MEMORY_H = REPO_ROOT / "src" / "code" / "botlib" / "l_memory.h"
BOTLIB_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
GAME_AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
QCOMMON_COMMON = REPO_ROOT / "src" / "code" / "qcommon" / "common.c"
QCOMMON_PUBLIC = REPO_ROOT / "src" / "code" / "qcommon" / "qcommon.h"
SERVER_BOT = REPO_ROOT / "src" / "code" / "server" / "sv_bot.c"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
QL_STEAM_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
)
QL_STEAM_IMPORTS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "imports.txt"
)
QL_STEAM_METADATA = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "metadata.txt"
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


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _extract_function_block(text: str, signature: str, *, last: bool = False) -> str:
	start = text.rfind(signature) if last else text.find(signature)
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


def test_botlib_memory_log_retail_function_map_is_pinned() -> None:
	metadata = _read(QL_STEAM_METADATA)
	functions_csv = _read(QL_STEAM_FUNCTIONS)
	imports = _read(QL_STEAM_IMPORTS)
	hlil = _read(QL_STEAM_HLIL_PART03)
	aliases = json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]

	for expected in (
		"program_name=quakelive_steam.exe",
		"program_language=x86:LE:32:default",
		"function_count=5473",
	):
		assert expected in metadata

	for expected_import in (
		"MSVCR100.DLL!fclose",
		"MSVCR100.DLL!fflush",
		"MSVCR100.DLL!fopen",
		"MSVCR100.DLL!memset",
		"MSVCR100.DLL!strncpy",
		"MSVCR100.DLL!vfprintf",
	):
		assert expected_import in imports

	for address, name in (
		("4A8830", "Log_Open"),
		("4A8910", "Log_Close"),
		("4A8960", "Log_Shutdown"),
		("4A8970", "Log_Write"),
		("4A89A0", "GetMemory"),
		("4A89D0", "GetClearedMemory"),
		("4A8A20", "GetHunkMemory"),
		("4A8A50", "GetClearedHunkMemory"),
		("4A8AA0", "FreeMemory"),
		("4A8AC0", "AvailableMemory"),
	):
		assert aliases[f"sub_{address}"] == name

	for row in (
		"FUN_004a8830,004a8830,210,0,unknown",
		"FUN_004a8910,004a8910,72,0,unknown",
		"FUN_004a8960,004a8960,15,0,unknown",
		"FUN_004a8970,004a8970,44,0,unknown",
		"FUN_004a89a0,004a89a0,36,0,unknown",
		"FUN_004a89d0,004a89d0,71,0,unknown",
		"FUN_004a8a20,004a8a20,36,0,unknown",
		"FUN_004a8a50,004a8a50,71,0,unknown",
		"FUN_004a8aa0,004a8aa0,29,0,unknown",
		"FUN_004a8ac0,004a8ac0,6,0,unknown",
	):
		assert row in functions_csv

	for evidence in (
		"004a8830    int32_t sub_4a8830(char* arg1)",
		'004a883e  st0, result = sub_4a8770("bot_log", U"0")',
		'004a8893              return data_16dd800(3, "log file %s is already opened\\n", 0xe4a0c8)',
		'004a88c1              return data_16dd800(3, "can\'t open the log file %s\\n", arg1)',
		"004a88cd          strncpy(0xe4a0c8, arg1, 0x400)",
		'004a88ec          return data_16dd800(1, "Opened log %s\\n", 0xe4a0c8)',
		"004a8910    int32_t sub_4a8910()",
		"004a892a  if (fclose(result) != 0)",
		'004a894e  return data_16dd800(1, "Closed log %s\\n", 0xe4a0c8)',
		"004a8969  return sub_4a8910() __tailcall",
		"004a8970    int32_t sub_4a8970(int32_t arg1)",
		"004a8985  vfprintf(result, arg1, &arg_8)",
		"004a8991  return fflush(data_e4a4c8)",
		"004a89a0    void* sub_4a89a0(int32_t arg1)",
		"004a89aa  int32_t* result = data_16dd820(arg1 + 4)",
		"004a89b9  *result = 0x12345678",
		"004a89c3  return &result[1]",
		"004a89d0    char* sub_4a89d0(int32_t arg1)",
		"004a89ee      sub_4c95e0(nullptr, 0, arg1)",
		"004a8a03  *eax_1 = 0x12345678",
		"004a8a09  sub_4c95e0(&eax_1[1], 0, arg1)",
		"004a8a20    void* sub_4a8a20(int32_t arg1)",
		"004a8a2a  int32_t* result = data_16dd82c(arg1 + 4)",
		"004a8a39  *result = 0x87654321",
		"004a8a50    char* sub_4a8a50(int32_t arg1)",
		"004a8a6e      sub_4c95e0(nullptr, 0, arg1)",
		"004a8a83  *eax_1 = 0x87654321",
		"004a8a89  sub_4c95e0(&eax_1[1], 0, arg1)",
		"004a8aa0    int32_t* sub_4a8aa0(void* arg1)",
		"004a8aa6  int32_t* result = arg1 - 4",
		"004a8aaf  if (*result != 0x12345678)",
		"004a8ab2  return data_16dd824(result)",
		"004a8ac0    int32_t sub_4a8ac0()",
		"004a8ac0  jump(data_16dd828)",
	):
		assert evidence in hlil


def test_botlib_memory_runtime_source_shape_matches_retail() -> None:
	memory_source = _read(BOTLIB_MEMORY)
	memory_header = _read(BOTLIB_MEMORY_H)

	assert "//#define MEMORYMANEGER" in memory_source
	assert "#define MEM_ID\t\t0x12345678l" in memory_source
	assert "#define HUNK_ID\t\t0x87654321l" in memory_source
	assert "#define GetHunkMemory GetMemory" in memory_header
	assert "#define GetClearedHunkMemory GetClearedMemory" in memory_header

	get_memory = _extract_function_block(memory_source, "void *GetMemory(unsigned long size)", last=True)
	assert "unsigned long int *memid;" in get_memory
	assert "ptr = botimport.GetMemory(size + sizeof(unsigned long int));" in get_memory
	assert "if (!ptr) return NULL;" in get_memory
	assert "*memid = MEM_ID;" in get_memory
	assert "return (unsigned long int *) ((char *) ptr + sizeof(unsigned long int));" in get_memory

	get_cleared = _extract_function_block(
		memory_source, "void *GetClearedMemory(unsigned long size)", last=True
	)
	assert "ptr = GetMemory(size);" in get_cleared
	assert "Com_Memset(ptr, 0, size);" in get_cleared
	assert "return ptr;" in get_cleared

	get_hunk = _extract_function_block(memory_source, "void *GetHunkMemory(unsigned long size)", last=True)
	assert "ptr = botimport.HunkAlloc(size + sizeof(unsigned long int));" in get_hunk
	assert "if (!ptr) return NULL;" in get_hunk
	assert "*memid = HUNK_ID;" in get_hunk
	assert "return (unsigned long int *) ((char *) ptr + sizeof(unsigned long int));" in get_hunk

	get_cleared_hunk = _extract_function_block(
		memory_source, "void *GetClearedHunkMemory(unsigned long size)", last=True
	)
	assert "ptr = GetHunkMemory(size);" in get_cleared_hunk
	assert "Com_Memset(ptr, 0, size);" in get_cleared_hunk
	assert "return ptr;" in get_cleared_hunk

	free_memory = _extract_function_block(memory_source, "void FreeMemory(void *ptr)", last=True)
	assert "memid = (unsigned long int *) ((char *) ptr - sizeof(unsigned long int));" in free_memory
	assert "if (*memid == MEM_ID)" in free_memory
	assert "botimport.FreeMemory(memid);" in free_memory
	assert "HUNK_ID" not in free_memory

	available = _extract_function_block(memory_source, "int AvailableMemory(void)", last=True)
	assert "return botimport.AvailableMemory();" in available

	assert _extract_function_block(memory_source, "void PrintUsedMemorySize(void)", last=True).strip().endswith("{\n}")
	assert _extract_function_block(memory_source, "void PrintMemoryLabels(void)", last=True).strip().endswith("{\n}")


def test_botlib_log_source_and_debug_cvar_bridge_match_retail() -> None:
	log_source = _read(BOTLIB_LOG)
	log_header = _read(BOTLIB_LOG_H)
	botlib_interface = _read(BOTLIB_INTERFACE)
	aas_main = _read(BOTLIB_AAS_MAIN)
	game_ai_main = _read(GAME_AI_MAIN)

	assert "#define MAX_LOGFILENAMESIZE\t\t1024" in log_source
	assert "void Log_Open(char *filename);" in log_header
	assert "void Log_Shutdown(void);" in log_header
	assert "void QDECL Log_Write(char *fmt, ...);" in log_header

	log_open = _extract_function_block(log_source, "void Log_Open(char *filename)")
	assert 'if (!LibVarValue("bot_log", "0")) return;' in log_open
	assert 'botimport.Print(PRT_MESSAGE, "openlog <filename>\\n");' in log_open
	assert 'botimport.Print(PRT_ERROR, "log file %s is already opened\\n", logfile.filename);' in log_open
	assert 'logfile.fp = fopen(filename, "wb");' in log_open
	assert 'botimport.Print(PRT_ERROR, "can\'t open the log file %s\\n", filename);' in log_open
	assert "strncpy(logfile.filename, filename, MAX_LOGFILENAMESIZE);" in log_open
	assert 'botimport.Print(PRT_MESSAGE, "Opened log %s\\n", logfile.filename);' in log_open

	log_close = _extract_function_block(log_source, "void Log_Close(void)")
	assert "if (!logfile.fp) return;" in log_close
	assert "if (fclose(logfile.fp))" in log_close
	assert 'botimport.Print(PRT_ERROR, "can\'t close log file %s\\n", logfile.filename);' in log_close
	assert "logfile.fp = NULL;" in log_close
	assert 'botimport.Print(PRT_MESSAGE, "Closed log %s\\n", logfile.filename);' in log_close

	log_shutdown = _extract_function_block(log_source, "void Log_Shutdown(void)")
	assert "if (logfile.fp) Log_Close();" in log_shutdown

	log_write = _extract_function_block(log_source, "void QDECL Log_Write(char *fmt, ...)")
	assert "if (!logfile.fp) return;" in log_write
	assert "vfprintf(logfile.fp, fmt, ap);" in log_write
	assert "fflush(logfile.fp);" in log_write

	assert 'Log_Open("botlib.log");' in botlib_interface
	assert "Log_Shutdown();" in botlib_interface
	assert 'trap_Cvar_Register(&bot_log, "bot_log", "0", 0);' in game_ai_main
	assert 'trap_Cvar_VariableStringBuffer("bot_log", buf, sizeof(buf));' in game_ai_main
	assert 'trap_BotLibVarSet("bot_log", buf);' in game_ai_main

	assert 'if (LibVarGetValue("showmemoryusage"))' in aas_main
	assert "PrintUsedMemorySize();" in aas_main
	assert 'LibVarSet("showmemoryusage", "0");' in aas_main
	assert 'if (LibVarGetValue("memorydump"))' in aas_main
	assert "PrintMemoryLabels();" in aas_main
	assert 'LibVarSet("memorydump", "0");' in aas_main
	assert 'trap_BotLibVarSet("memorydump", "1");' in game_ai_main
	assert 'trap_Cvar_Register(&bot_memorydump, "bot_memorydump", "0", CVAR_CHEAT);' in game_ai_main


def test_botlib_memory_engine_import_wiring_is_bounded() -> None:
	botlib_public = _read(BOTLIB_PUBLIC)
	server_bot = _read(SERVER_BOT)
	qcommon_common = _read(QCOMMON_COMMON)
	qcommon_public = _read(QCOMMON_PUBLIC)
	hlil = _read(QL_STEAM_HLIL_PART04)

	for field in (
		"void\t\t*(*GetMemory)(int size);\t\t// allocate from Zone",
		"void\t\t(*FreeMemory)(void *ptr);\t\t// free memory from Zone",
		"int\t\t\t(*AvailableMemory)(void);\t\t// available Zone memory",
		"void\t\t*(*HunkAlloc)(int size);\t\t// allocate from hunk",
	):
		assert field in botlib_public

	get_memory = _extract_function_block(server_bot, "void *BotImport_GetMemory(int size)")
	assert "ptr = Z_TagMalloc( size, TAG_BOTLIB );" in get_memory
	assert "return ptr;" in get_memory

	free_memory = _extract_function_block(server_bot, "void BotImport_FreeMemory(void *ptr)")
	assert "Z_Free(ptr);" in free_memory

	hunk_alloc = _extract_function_block(server_bot, "void *BotImport_HunkAlloc( int size )")
	assert "if( Hunk_CheckMark() )" in hunk_alloc
	assert 'Com_Error( ERR_DROP, "SV_Bot_HunkAlloc: Alloc with marks already set\\n" );' in hunk_alloc
	assert "return Hunk_Alloc( size, h_high );" in hunk_alloc

	for assignment in (
		"botlib_import.GetMemory = BotImport_GetMemory;",
		"botlib_import.FreeMemory = BotImport_FreeMemory;",
		"botlib_import.AvailableMemory = Z_AvailableMemory;",
		"botlib_import.HunkAlloc = BotImport_HunkAlloc;",
	):
		assert assignment in server_bot

	assert "int Z_AvailableMemory( void );" in qcommon_public
	assert "int Z_AvailableMemory( void ) {\n\treturn Z_AvailableZoneMemory( mainzone );\n}" in qcommon_common
	assert "void Z_Free( void *ptr )" in qcommon_common
	assert "void *Z_TagMalloc( int size, int tag )" in qcommon_common
	assert "qboolean Hunk_CheckMark( void )" in qcommon_common
	assert "void *Hunk_Alloc( int size, ha_pref preference )" in qcommon_common

	for evidence in (
		"004dd350    void* sub_4dd350(int32_t arg1)",
		"004dd362  return sub_4ca2c0(arg1, 2)",
		"004ca2c0    void* sub_4ca2c0(int32_t arg1, int32_t arg2)",
		"004ca2d2      sub_4c9b60(arg2, \"Z_TagMalloc: tried to use a 0 ta",
		"004dd370    int32_t sub_4dd370()",
		"004dd374  return sub_4ca1d0() __tailcall",
		"004ca1d0    void sub_4ca1d0(char* arg1)",
		"004dd9d4  void* (* var_3c)(int32_t arg1) = sub_4dd350",
		"004dd9db  int32_t (* var_38)() = sub_4dd370",
		"004dd9e2  int32_t (* var_34)() = sub_4c9220",
		"004c9220    int32_t sub_4c9220()",
		"004dd9e9  char* (* var_30)(int32_t arg1) = sub_4dd380",
		"004dd380    char* sub_4dd380(int32_t arg1)",
		"004dd38a  if (sub_4c9310() == 0)",
		"004dd3aa      return sub_4ca980(arg1, 0)",
		"004dd393  sub_4c9b60(1, \"SV_Bot_HunkAlloc: Alloc with mar",
	):
		assert evidence in hlil
