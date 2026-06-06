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
BOTLIB_CRC = REPO_ROOT / "src" / "code" / "botlib" / "l_crc.c"
BOTLIB_LIBVAR = REPO_ROOT / "src" / "code" / "botlib" / "l_libvar.c"
BOTLIB_ROUTE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_route.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"

SUPPORT_BLOCK_START = 0x004A84B0
SUPPORT_BLOCK_END = 0x004A8790

EXPECTED_ALIASES = {
	"sub_4A84B0": "CRC_ProcessString",
	"sub_4A8500": "LibVarStringValue",
	"sub_4A8590": "LibVarAlloc",
	"sub_4A85F0": "LibVarDeAllocAll",
	"sub_4A8640": "LibVarGetString",
	"sub_4A8680": "LibVarGetValue",
	"sub_4A86C0": "LibVar",
	"sub_4A8750": "LibVarString",
	"sub_4A8770": "LibVarValue",
	"sub_4A8790": "LibVarSet",
}


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _aliases() -> dict[str, str]:
	return json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]


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


def _function_rows_in_support_block() -> dict[int, str]:
	rows: dict[int, str] = {}
	with FUNCTIONS_CSV.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			address = int(row["entry"], 16)
			if SUPPORT_BLOCK_START <= address <= SUPPORT_BLOCK_END:
				rows[address] = f'{row["name"]},{row["entry"]},{row["size"]},{row["thunk"]},{row["calling_convention"]}'
	return rows


def test_botlib_crc_and_libvar_alias_block_is_now_closed() -> None:
	aliases = _aliases()
	rows = _function_rows_in_support_block()

	assert {alias: aliases[alias] for alias in EXPECTED_ALIASES} == EXPECTED_ALIASES
	assert sorted(rows) == [int(alias[4:], 16) for alias in EXPECTED_ALIASES]
	assert all(alias in aliases for alias in EXPECTED_ALIASES)

	for row in (
		"FUN_004a84b0,004a84b0,73,0,unknown",
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
		assert row in rows.values()

	assert "LibVarGet" not in aliases.values()
	assert "LibVarDeAlloc" not in aliases.values()


def test_crc_process_string_matches_route_cache_crc_owner() -> None:
	crc_source = _read(BOTLIB_CRC)
	route = _read(BOTLIB_ROUTE)
	hlil = _read(QL_STEAM_HLIL_PART03)

	crc_process = _extract_function_block(
		crc_source,
		"unsigned short CRC_ProcessString(unsigned char *data, int length)",
	)
	write_cache = _extract_function_block(route, "void AAS_WriteRouteCache(void)")
	read_route_cache = _extract_function_block(route, "int AAS_ReadRouteCache(void)")

	assert "#define CRC_INIT_VALUE\t0xffff" in crc_source
	assert "#define CRC_XOR_VALUE\t0x0000" in crc_source
	assert "unsigned short crctable[257]" in crc_source
	assert "CRC_Init(&crcvalue);" in crc_process
	assert "for (i = 0; i < length; i++)" in crc_process
	assert "ind = (crcvalue >> 8) ^ data[i];" in crc_process
	assert "if (ind < 0 || ind > 256) ind = 0;" in crc_process
	assert "crcvalue = (crcvalue << 8) ^ crctable[ind];" in crc_process
	assert "return CRC_Value(crcvalue);" in crc_process

	assert "routecacheheader.areacrc = CRC_ProcessString" in write_cache
	assert "routecacheheader.clustercrc = CRC_ProcessString" in write_cache
	assert "CRC_ProcessString( (unsigned char *)aasworld.areas, sizeof(aas_area_t) * aasworld.numareas )" in read_route_cache
	assert "CRC_ProcessString( (unsigned char *)aasworld.clusters, sizeof(aas_cluster_t) * aasworld.numclusters )" in read_route_cache

	for anchor in (
		"004a84b0    uint32_t sub_4a84b0(int32_t arg1, int32_t arg2)",
		"004a84b9  uint32_t result = 0xffff",
		"004a84da          uint32_t ecx_2 = zx.d(*(edx + arg1)) ^ zx.d(result.w) u>> 8",
		"004a84f4          result = zx.d((result << 8).w) ^ *((ecx_2 << 1) + &data_5643e8)",
		"004a84ff  return result",
	):
		assert anchor in hlil


def test_libvar_runtime_aliases_match_source_and_retail_hlil() -> None:
	libvar = _read(BOTLIB_LIBVAR)
	interface = _read(BOTLIB_INTERFACE)
	hlil = _read(QL_STEAM_HLIL_PART03)

	string_value = _extract_function_block(libvar, "float LibVarStringValue(char *string)")
	alloc = _extract_function_block(libvar, "libvar_t *LibVarAlloc(char *var_name)")
	get = _extract_function_block(libvar, "libvar_t *LibVarGet(char *var_name)")
	get_string = _extract_function_block(libvar, "char *LibVarGetString(char *var_name)")
	get_value = _extract_function_block(libvar, "float LibVarGetValue(char *var_name)")
	libvar_fn = _extract_function_block(libvar, "libvar_t *LibVar(char *var_name, char *value)")
	string_fn = _extract_function_block(libvar, "char *LibVarString(char *var_name, char *value)")
	value_fn = _extract_function_block(libvar, "float LibVarValue(char *var_name, char *value)")
	set_fn = _extract_function_block(libvar, "void LibVarSet(char *var_name, char *value)")
	export_set = _extract_function_block(interface, "int Export_BotLibVarSet(char *var_name, char *value)")
	export_get = _extract_function_block(interface, "int Export_BotLibVarGet(char *var_name, char *value, int size)")

	assert "if (dotfound || *string != '.')" in string_value
	assert "dotfound = 10;" in string_value
	assert "value = value + (float) (*string - '0') / (float) dotfound;" in string_value
	assert "value = value * 10.0 + (float) (*string - '0');" in string_value
	assert "GetMemory(sizeof(libvar_t) + strlen(var_name) + 1)" in alloc
	assert "Com_Memset(v, 0, sizeof(libvar_t));" in alloc
	assert "for (v = libvarlist; v; v = v->next)" in get
	assert "if (!Q_stricmp(v->name, var_name))" in get
	assert "v = LibVarGet(var_name);" in get_string
	assert 'return "";' in get_string
	assert "v = LibVarGet(var_name);" in get_value
	assert "return 0;" in get_value
	assert "v = LibVarGet(var_name);" in libvar_fn
	assert "if (v) return v;" in libvar_fn
	assert "v->modified = qtrue;" in libvar_fn
	assert "return v->string;" in string_fn
	assert "return v->value;" in value_fn
	assert "FreeMemory(v->string);" in set_fn
	assert "v->modified = qtrue;" in set_fn
	assert "LibVarSet(var_name, value);" in export_set
	assert "varvalue = LibVarGetString(var_name);" in export_get

	for anchor in (
		"004a8500    long double sub_4a8500(int32_t arg1)",
		"004a852d              if (ecx != 0 || eax.b != 0x2e)",
		"004a8590    void* sub_4a8590(char* arg1)",
		"004a85ad  void* result = sub_4a89a0(eax - &eax[1] + 0x19)",
		"004a85f0    void sub_4a85f0()",
		"004a8619      sub_4a8aa0(i)",
		"004a8640    int32_t sub_4a8640(char* arg1)",
		"004a8660      if (sub_4d9060(*i, arg1) == 0)",
		"004a8680    long double sub_4a8680(char* arg1)",
		"004a86c0    int32_t* sub_4a86c0(char* arg1, char* arg2)",
		"004a8733  i[4] = fconvert.s(sub_4a8500(i[1]))",
		"004a8750    int32_t sub_4a8750(char* arg1, char* arg2)",
		"004a8770    long double sub_4a8770(char* arg1, char* arg2)",
		"004a8790    int32_t sub_4a8790(char* arg1, char* arg2)",
		"004a881a              sub_4a8aa0(esi[1])",
		"004a8809  edi_1[3] = 1",
	):
		assert anchor in hlil
