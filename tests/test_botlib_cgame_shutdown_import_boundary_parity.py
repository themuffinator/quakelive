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
QL_STEAM_HLIL_PART04 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part04.txt"
)
QL_STEAM_HLIL_PART05 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part05.txt"
)
QL_STEAM_HLIL_PART07 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part07.txt"
)
CLIENT_CL_CGAME = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
CLIENT_H = REPO_ROOT / "src" / "code" / "client" / "client.h"
CLIENT_CL_MAIN = REPO_ROOT / "src" / "code" / "client" / "cl_main.c"
COMMON_C = REPO_ROOT / "src" / "code" / "qcommon" / "common.c"
CGAME_PUBLIC = REPO_ROOT / "src" / "code" / "cgame" / "cg_public.h"

CGAME_NATIVE_POCKET_START = 0x004AF820
CGAME_NATIVE_POCKET_END = 0x004B0500

EXPECTED_RESIDUAL_CGAME_NATIVE_ROWS = {
	0x004AFFC0: "FUN_004affc0,004affc0,9,0,unknown",
	0x004B00C0: "FUN_004b00c0,004b00c0,10,0,unknown",
	0x004B0370: "FUN_004b0370,004b0370,51,0,unknown",
}

EXPECTED_PROMOTED_CGAME_NATIVE_ALIASES = {
	"sub_4AF820": "CL_GetServerCommand",
	"sub_4AFBF0": "CL_ShutdownCGame",
	"sub_4AFC40": "QLCGImport_AddCommand",
	"sub_4AFF80": "QLCGImport_AdvertisementBridge_UpdateViewParameters",
	"sub_4AFFE0": "QLCGImport_AdvertisementBridge_ClearDelay",
	"sub_4B0070": "QLCGImport_R_DrawStretchPic",
	"sub_4B00D0": "QLCGImport_R_LerpTag",
	"sub_4B0100": "QLCGImport_R_RemapShader",
	"sub_4B0150": "QLCGImport_GetSnapshot",
	"sub_4B0160": "QLCGImport_GetServerCommand",
	"sub_4B03B0": "QLCGImport_PublishTaggedInfoString",
	"sub_4B0460": "CL_LoadCGameForCvarRegistration",
	"sub_4B04C0": "CL_InitCGame",
}


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _aliases() -> dict[str, str]:
	return json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]


def _alias_key(address: int) -> str:
	return f"sub_{address:06X}"


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


def _function_rows_in_native_pocket() -> dict[int, str]:
	rows: dict[int, str] = {}
	with FUNCTIONS_CSV.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			address = int(row["entry"], 16)
			if CGAME_NATIVE_POCKET_START <= address <= CGAME_NATIVE_POCKET_END:
				rows[address] = f'{row["name"]},{row["entry"]},{row["size"]},{row["thunk"]},{row["calling_convention"]}'
	return rows


def test_cgame_native_boundary_now_promotes_shutdown_owner_and_bounds_residual_rows() -> None:
	aliases = _aliases()
	rows = _function_rows_in_native_pocket()
	unaliased = {
		address
		for address in rows
		if _alias_key(address) not in aliases
	}

	assert {alias: aliases[alias] for alias in EXPECTED_PROMOTED_CGAME_NATIVE_ALIASES} == EXPECTED_PROMOTED_CGAME_NATIVE_ALIASES
	assert len(rows) == 73
	assert unaliased == set(EXPECTED_RESIDUAL_CGAME_NATIVE_ROWS)
	assert {address: rows[address] for address in EXPECTED_RESIDUAL_CGAME_NATIVE_ROWS} == EXPECTED_RESIDUAL_CGAME_NATIVE_ROWS


def test_cl_shutdown_cgame_alias_matches_retail_lifecycle_body_and_call_sites() -> None:
	aliases = _aliases()
	cl_cgame = _read(CLIENT_CL_CGAME)
	client_h = _read(CLIENT_H)
	cl_main = _read(CLIENT_CL_MAIN)
	common_c = _read(COMMON_C)
	hlil = _read(QL_STEAM_HLIL_PART04)
	shutdown_block = _extract_function_block(cl_cgame, "void CL_ShutdownCGame( void )")

	assert aliases["sub_4AFBF0"] == "CL_ShutdownCGame"
	assert "void CL_ShutdownCGame( void );" in client_h
	assert cl_main.count("CL_ShutdownCGame();") == 2
	assert "void CL_ShutdownCGame( void );" in common_c
	assert "CL_ShutdownCGame();" in common_c

	for source_anchor in (
		"cls.keyCatchers &= ~KEYCATCH_CGAME;",
		"cls.cgameStarted = qfalse;",
		"if ( !cgvm )",
		"VM_Call( cgvm, CG_SHUTDOWN );",
		"VM_Free( cgvm );",
		"cgvm = NULL;",
	):
		assert source_anchor in shutdown_block

	for hlil_anchor in (
		"004afbf0    void sub_4afbf0()",
		"004afbf0  data_1528ba4.d &= 0xfffffff7",
		"004afbfe  data_1528cbc = 0",
		"004afc12      (*(data_146cc38 + 8))()",
		"004afc1b      sub_4ea0e0(data_1647f0c)",
		"004afc23      data_1647f0c = 0",
		"004afc2d      data_146cc38 = 0",
		"004b88e6  sub_4afbf0()",
		"004b9e73  sub_4afbf0()",
		"004bb696  sub_4afbf0()",
		"004bb8d8  sub_4afbf0()",
		"004ca910  sub_4afbf0()",
		"004cc264      sub_4afbf0()",
	):
		assert hlil_anchor in hlil


def test_adjacent_reserved_cgame_import_trampolines_remain_bounded_not_overpromoted() -> None:
	aliases = _aliases()
	cl_cgame = _read(CLIENT_CL_CGAME)
	cgame_public = _read(CGAME_PUBLIC)
	part04 = _read(QL_STEAM_HLIL_PART04)
	part05 = _read(QL_STEAM_HLIL_PART05)
	part07 = _read(QL_STEAM_HLIL_PART07)
	import_block = _extract_function_block(cl_cgame, "static void CL_InitCGameImports")
	reserved_block = _extract_function_block(cl_cgame, "static int QDECL QL_CG_trap_RetailReservedImport")

	for residual_alias in ("sub_4AFFC0", "sub_4B00C0", "sub_4B0370"):
		assert residual_alias not in aliases

	for public_slot in (
		"CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_65 = 65,",
		"CG_QL_IMPORT_RETAIL_RESERVED_80 = 80,",
		"CG_QL_IMPORT_RETAIL_RESERVED_112 = 112,",
		"CG_QL_IMPORT_RETAIL_RESERVED_113 = 113,",
		"CG_QL_IMPORT_RETAIL_RESERVED_117 = 117,",
	):
		assert public_slot in cgame_public

	for import_anchor in (
		"ql_cgame_imports[CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_65] = (ql_import_f)QL_CG_trap_RetailReservedImport;",
		"ql_cgame_imports[CG_QL_IMPORT_RETAIL_RESERVED_80] = (ql_import_f)QL_CG_trap_RetailReservedImport;",
		"ql_cgame_imports[CG_QL_IMPORT_RETAIL_RESERVED_112] = (ql_import_f)QL_CG_trap_RetailReservedImport;",
		"ql_cgame_imports[CG_QL_IMPORT_RETAIL_RESERVED_113] = (ql_import_f)QL_CG_trap_RetailReservedImport;",
		"ql_cgame_imports[CG_QL_IMPORT_RETAIL_RESERVED_117] = (ql_import_f)QL_CG_trap_RetailReservedImport;",
	):
		assert import_anchor in import_block

	assert "return 0;" in reserved_block

	for hlil_anchor in (
		"004affc0    int32_t sub_4affc0()",
		"004affc4  return sub_4f1fc0() __tailcall",
		"004b00c0    int32_t sub_4b00c0()",
		"004b00c4  jump(data_146ccf8)",
		"004b0370    int32_t sub_4b0370(float arg1, float arg2, float arg3, float arg4, float arg5)",
		"004b03a2  return data_146cce4(fconvert.s(fconvert.t(arg1)), fconvert.s(fconvert.t(arg2)),",
	):
		assert hlil_anchor in part04

	assert "004f1fc0    int32_t sub_4f1fc0(int32_t arg1)" in part05
	assert "004f1fde      return 0xffffffff" in part05

	for table_anchor in (
		"00565a6c  void* data_565a6c = sub_4affc0",
		"00565a98  void* data_565a98 = sub_4b00c0",
		"00565b2c  void* data_565b2c = sub_4b0370",
		"00565b30                                                  00 00 00 00 00 00 00 00",
	):
		assert table_anchor in part07
