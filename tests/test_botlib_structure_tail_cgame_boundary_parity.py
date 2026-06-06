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
BOTLIB_L_STRUCT = REPO_ROOT / "src" / "code" / "botlib" / "l_struct.c"
BOTLIB_AI_WEAP = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_weap.c"
BOTLIB_AI_WEIGHT = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_weight.c"
CLIENT_CL_CGAME = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
CLIENT_CL_CIN = REPO_ROOT / "src" / "code" / "client" / "cl_cin.c"
CLIENT_CGAME_IMPORTS = REPO_ROOT / "src" / "code" / "client" / "ql_cgame_imports.inc"
CGAME_SYSCALLS = REPO_ROOT / "src" / "code" / "cgame" / "cg_syscalls.c"
CGAME_PUBLIC = REPO_ROOT / "src" / "code" / "cgame" / "cg_public.h"

SEAM_START = 0x004AF050
SEAM_END = 0x004AF820
POST_STRUCTURE_BOUNDARY_START = 0x004B0610
POST_STRUCTURE_BOUNDARY_END = 0x004B0F60
ROQ_CINEMATIC_CONTINUATION_START = 0x004B1010
ROQ_CINEMATIC_CONTINUATION_END = 0x004B3510
BOTLIB_BOUNDARY_ALIAS_COVERAGE_START = 0x004A83C0
BOTLIB_BOUNDARY_ALIAS_COVERAGE_END = ROQ_CINEMATIC_CONTINUATION_END

PROMOTED_BOUNDARY_ALIASES = {
	"sub_4AE830": "FindField",
	"sub_4AE8A0": "ReadNumber",
	"sub_4AECD0": "ReadStructure",
	"sub_4AF570": "CL_GetSnapshot",
	"sub_4AF690": "CL_ConfigstringModified",
	"sub_4AF820": "CL_GetServerCommand",
}

INTENTIONALLY_UNPROMOTED_SEAM_ROWS = {
	0x004AF050,
	0x004AF150,
	0x004AF190,
	0x004AF1C0,
	0x004AF2C0,
	0x004AF370,
	0x004AF400,
	0x004AF4C0,
	0x004AF4D0,
	0x004AF4E0,
	0x004AF500,
}

EXPECTED_SEAM_ROWS = {
	0x004AF050: "FUN_004af050,004af050,242,0,unknown",
	0x004AF150: "FUN_004af150,004af150,49,0,unknown",
	0x004AF190: "FUN_004af190,004af190,41,0,unknown",
	0x004AF1C0: "FUN_004af1c0,004af1c0,252,0,unknown",
	0x004AF2C0: "FUN_004af2c0,004af2c0,176,0,unknown",
	0x004AF370: "FUN_004af370,004af370,141,0,unknown",
	0x004AF400: "FUN_004af400,004af400,191,0,unknown",
	0x004AF4C0: "FUN_004af4c0,004af4c0,11,0,unknown",
	0x004AF4D0: "FUN_004af4d0,004af4d0,6,0,unknown",
	0x004AF4E0: "FUN_004af4e0,004af4e0,29,0,unknown",
	0x004AF500: "FUN_004af500,004af500,111,0,unknown",
	0x004AF570: "FUN_004af570,004af570,273,0,unknown",
	0x004AF690: "FUN_004af690,004af690,387,0,unknown",
	0x004AF820: "FUN_004af820,004af820,958,0,unknown",
}

POST_STRUCTURE_BOUNDARY_ALIASES = {
	"sub_4B0610": "CL_GameCommand",
	"sub_4B0630": "CL_CGameRendering",
	"sub_4B0660": "CL_AdjustServerTimeDelta",
	"sub_4B0760": "CL_FirstSnapshot",
	"sub_4B07C0": "CL_SetCGameTime",
	"sub_4B0A70": "RllDecodeStereoToStereo",
	"sub_4B0AF0": "move8_32",
	"sub_4B0BD0": "blit8_32",
	"sub_4B0CD0": "blitVQQuad32fs",
	"sub_4B0F60": "ROQ_GenYUVTables",
}

EXPECTED_POST_STRUCTURE_BOUNDARY_ROWS = {
	0x004B0610: "FUN_004b0610,004b0610,22,0,unknown",
	0x004B0630: "FUN_004b0630,004b0630,35,0,unknown",
	0x004B0660: "FUN_004b0660,004b0660,255,0,unknown",
	0x004B0760: "FUN_004b0760,004b0760,92,0,unknown",
	0x004B07C0: "FUN_004b07c0,004b07c0,641,0,unknown",
	0x004B0A50: "FUN_004b0a50,004b0a50,32,0,unknown",
	0x004B0A70: "FUN_004b0a70,004b0a70,128,0,unknown",
	0x004B0AF0: "FUN_004b0af0,004b0af0,214,0,unknown",
	0x004B0BD0: "FUN_004b0bd0,004b0bd0,255,0,unknown",
	0x004B0CD0: "FUN_004b0cd0,004b0cd0,654,0,unknown",
	0x004B0F60: "FUN_004b0f60,004b0f60,173,0,unknown",
}

ROQ_CINEMATIC_CONTINUATION_ALIASES = {
	"sub_4B1010": "yuv_to_rgb",
	"sub_4B1080": "yuv_to_rgb24",
	"sub_4B1100": "decodeCodeBook",
	"sub_4B1DA0": "recurseQuad",
	"sub_4B1EB0": "setupQuad",
	"sub_4B1FC0": "readQuadInfo",
	"sub_4B2110": "RoQPrepMcomp",
	"sub_4B21C0": "initRoQ",
	"sub_4B2220": "RoQ_init",
	"sub_4B2300": "RoQShutdown",
	"sub_4B2400": "CIN_StopCinematic",
	"sub_4B2480": "CIN_SetExtents",
	"sub_4B24D0": "CIN_DrawCinematic",
	"sub_4B2790": "SCR_DrawCinematic",
	"sub_4B27B0": "SCR_StopCinematic",
	"sub_4B27E0": "CIN_UploadCinematic",
	"sub_4B2890": "CIN_CloseAllVideos",
	"sub_4B2910": "RoQReset",
	"sub_4B29D0": "RoQInterrupt",
	"sub_4B2F40": "CIN_RunCinematic",
	"sub_4B3160": "CIN_PlayCinematic",
	"sub_4B3510": "SCR_RunCinematic",
}

EXPECTED_ROQ_CINEMATIC_CONTINUATION_ROWS = {
	0x004B1010: "FUN_004b1010,004b1010,111,0,unknown",
	0x004B1080: "FUN_004b1080,004b1080,124,0,unknown",
	0x004B1100: "FUN_004b1100,004b1100,3172,0,unknown",
	0x004B1DA0: "FUN_004b1da0,004b1da0,259,0,unknown",
	0x004B1EB0: "FUN_004b1eb0,004b1eb0,260,0,unknown",
	0x004B1FC0: "FUN_004b1fc0,004b1fc0,322,0,unknown",
	0x004B2110: "FUN_004b2110,004b2110,161,0,unknown",
	0x004B21C0: "FUN_004b21c0,004b21c0,83,0,unknown",
	0x004B2220: "FUN_004b2220,004b2220,223,0,unknown",
	0x004B2300: "FUN_004b2300,004b2300,254,0,unknown",
	0x004B2400: "FUN_004b2400,004b2400,122,0,unknown",
	0x004B2480: "FUN_004b2480,004b2480,74,0,unknown",
	0x004B24D0: "FUN_004b24d0,004b24d0,691,0,unknown",
	0x004B2790: "FUN_004b2790,004b2790,18,0,unknown",
	0x004B27B0: "FUN_004b27b0,004b27b0,35,0,unknown",
	0x004B27E0: "FUN_004b27e0,004b27e0,172,0,unknown",
	0x004B2890: "FUN_004b2890,004b2890,122,0,unknown",
	0x004B2910: "FUN_004b2910,004b2910,179,0,unknown",
	0x004B29D0: "FUN_004b29d0,004b29d0,1253,0,unknown",
	0x004B2F40: "FUN_004b2f40,004b2f40,532,0,unknown",
	0x004B3160: "FUN_004b3160,004b3160,938,0,unknown",
	0x004B3510: "FUN_004b3510,004b3510,18,0,unknown",
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


def _function_rows_in_seam() -> dict[int, str]:
	rows: dict[int, str] = {}
	with FUNCTIONS_CSV.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			address = int(row["entry"], 16)
			if SEAM_START <= address <= SEAM_END:
				rows[address] = f'{row["name"]},{row["entry"]},{row["size"]},{row["thunk"]},{row["calling_convention"]}'
	return rows


def _function_rows_in_post_structure_boundary() -> dict[int, str]:
	rows: dict[int, str] = {}
	with FUNCTIONS_CSV.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			address = int(row["entry"], 16)
			if POST_STRUCTURE_BOUNDARY_START <= address <= POST_STRUCTURE_BOUNDARY_END:
				rows[address] = f'{row["name"]},{row["entry"]},{row["size"]},{row["thunk"]},{row["calling_convention"]}'
	return rows


def _function_rows_in_roq_cinematic_continuation() -> dict[int, str]:
	rows: dict[int, str] = {}
	with FUNCTIONS_CSV.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			address = int(row["entry"], 16)
			if ROQ_CINEMATIC_CONTINUATION_START <= address <= ROQ_CINEMATIC_CONTINUATION_END:
				rows[address] = f'{row["name"]},{row["entry"]},{row["size"]},{row["thunk"]},{row["calling_convention"]}'
	return rows


def _test_botlib_file_text() -> str:
	return "\n".join(
		path.read_text(encoding="utf-8")
		for path in sorted((REPO_ROOT / "tests").glob("test_botlib_*.py"))
	)


def _promoted_aliases_in_botlib_boundary_range() -> dict[str, str]:
	entries: dict[str, str] = {}
	for retail_name, promoted_name in _aliases().items():
		if not retail_name.startswith("sub_"):
			continue
		try:
			address = int(retail_name.removeprefix("sub_"), 16)
		except ValueError:
			continue
		if BOTLIB_BOUNDARY_ALIAS_COVERAGE_START <= address <= BOTLIB_BOUNDARY_ALIAS_COVERAGE_END:
			entries[retail_name] = str(promoted_name)
	return entries


def test_botlib_structure_tail_boundary_promotes_only_evidence_backed_client_owners() -> None:
	aliases = _aliases()
	rows = _function_rows_in_seam()

	assert {address: aliases[address] for address in PROMOTED_BOUNDARY_ALIASES} == PROMOTED_BOUNDARY_ALIASES
	assert rows == EXPECTED_SEAM_ROWS
	assert {
		address for address in rows if f"sub_{address:X}" not in aliases
	} == INTENTIONALLY_UNPROMOTED_SEAM_ROWS

	for source_visible_but_unpromoted in (
		"ReadChar",
		"ReadString",
		"WriteIndent",
		"WriteFloat",
		"WriteStructWithIndent",
		"WriteStructure",
	):
		assert source_visible_but_unpromoted not in aliases.values()


def test_l_struct_write_helpers_are_source_real_but_not_the_adjacent_retail_seam() -> None:
	l_struct = _read(BOTLIB_L_STRUCT)
	ai_weap = _read(BOTLIB_AI_WEAP)
	ai_weight = _read(BOTLIB_AI_WEIGHT)
	hlil = _read(QL_STEAM_HLIL_PART04)

	read_structure = _extract_function_block(l_struct, "int ReadStructure(source_t *source, structdef_t *def, char *structure)")
	write_indent = _extract_function_block(l_struct, "int WriteIndent(FILE *fp, int indent)")
	write_float = _extract_function_block(l_struct, "int WriteFloat(FILE *fp, float value)")
	write_with_indent = _extract_function_block(
		l_struct,
		"int WriteStructWithIndent(FILE *fp, structdef_t *def, char *structure, int indent)",
	)
	write_structure = _extract_function_block(l_struct, "int WriteStructure(FILE *fp, structdef_t *def, char *structure)")

	assert "ReadStructure(source, fd->substruct, (char *) p);" in read_structure
	assert "if (!ReadStructure(source, fd->substruct" not in read_structure
	assert 'SourceError(source, "expected a comma, found %s", token.string);' in read_structure
	assert "while(indent-- > 0)" in write_indent
	assert 'fprintf(fp, "\\t")' in write_indent
	assert 'sprintf(buf, "%f", value);' in write_float
	assert "if (buf[l] != '0' && buf[l] != '.') break;" in write_float
	assert 'fprintf(fp, "%s", buf)' in write_float
	assert 'fprintf(fp, "{\\r\\n")' in write_with_indent
	assert "if (!WriteFloat(fp, *(float *)p)) return qfalse;" in write_with_indent
	assert "if (!WriteStructWithIndent(fp, fd->substruct, structure, indent)) return qfalse;" in write_with_indent
	assert "return WriteStructWithIndent(fp, def, structure, 0);" in write_structure

	dump_weapon_index = ai_weap.index("#ifdef DEBUG_AI_WEAP")
	dump_writer_index = ai_weap.index("WriteStructure(fp, &projectileinfo_struct")
	dump_end_index = ai_weap.index("#endif //DEBUG_AI_WEAP")
	load_weapon_index = ai_weap.index("weaponconfig_t *LoadWeaponConfig")
	assert dump_weapon_index < dump_writer_index < dump_end_index < load_weapon_index

	weight_writer_start = ai_weight.index("#if 0")
	weight_writer_use = ai_weight.index("if (!WriteFloat(fp, fs->weight)) return qfalse;")
	weight_writer_end = ai_weight.index("#endif", weight_writer_use)
	assert weight_writer_start < weight_writer_use < weight_writer_end

	for adjacent_non_botlib_anchor in (
		'004af1ed  sub_4af050(arg1, "camera01")',
		"004af500    int32_t sub_4af500(int32_t arg1)",
		"004af555          char ecx_3 = (eax_2.b - 0x66) ^",
		"004af570    int32_t sub_4af570(void* arg1, int32_t* arg2)",
		"004af690    int32_t sub_4af690()",
		"004af820    int32_t sub_4af820(int32_t arg1)",
	):
		assert adjacent_non_botlib_anchor in hlil


def test_cgame_snapshot_and_configstring_promotions_match_source_hlil_and_import_wiring() -> None:
	aliases = _aliases()
	cl_cgame = _read(CLIENT_CL_CGAME)
	cgame_imports = _read(CLIENT_CGAME_IMPORTS)
	cg_syscalls = _read(CGAME_SYSCALLS)
	cg_public = _read(CGAME_PUBLIC)
	hlil = _read(QL_STEAM_HLIL_PART04)

	get_snapshot = _extract_function_block(cl_cgame, "qboolean\tCL_GetSnapshot( int snapshotNumber, snapshot_t *snapshot )")
	configstring_modified = _extract_function_block(cl_cgame, "void CL_ConfigstringModified( void )")
	cgame_system_calls = _extract_function_block(cl_cgame, "static int CL_CgameSystemCallsImpl( int *args, qboolean logContract )")
	cg_map_native = _extract_function_block(cg_syscalls, "static int CG_MapNativeImport( int arg, const intptr_t *stack )")
	trap_get_snapshot = _extract_function_block(cg_syscalls, "qboolean\ttrap_GetSnapshot( int snapshotNumber, snapshot_t *snapshot )")

	assert aliases["sub_4AF570"] == "CL_GetSnapshot"
	assert aliases["sub_4AF690"] == "CL_ConfigstringModified"
	assert aliases["sub_4B0150"] == "QLCGImport_GetSnapshot"
	assert aliases["sub_4B0160"] == "QLCGImport_GetServerCommand"

	for source_anchor in (
		"if ( snapshotNumber > cl.snap.messageNum )",
		"if ( cl.snap.messageNum - snapshotNumber >= PACKET_BACKUP )",
		"clSnap = &cl.snapshots[snapshotNumber & PACKET_MASK];",
		"if ( cl.parseEntitiesNum - clSnap->parseEntitiesNum >= MAX_PARSE_ENTITIES )",
		"snapshot->serverCommandSequence = clSnap->serverCommandNum;",
		"Com_Memcpy( snapshot->areamask, clSnap->areamask, sizeof( snapshot->areamask ) );",
		"snapshot->ps = clSnap->ps;",
		"if ( count > MAX_ENTITIES_IN_SNAPSHOT )",
		"snapshot->entities[i] =",
	):
		assert source_anchor in get_snapshot

	for source_anchor in (
		"index = atoi( Cmd_Argv(1) );",
		"if ( index < 0 || index >= MAX_CONFIGSTRINGS )",
		'Com_Error( ERR_DROP, "configstring > MAX_CONFIGSTRINGS" );',
		"s = Cmd_ArgsFrom(2);",
		"old = cl.gameState.stringData + cl.gameState.stringOffsets[ index ];",
		"oldGs = cl.gameState;",
		"Com_Memset( &cl.gameState, 0, sizeof( cl.gameState ) );",
		"cl.gameState.dataCount = 1;",
		"dup = oldGs.stringData + oldGs.stringOffsets[ i ];",
		"if ( len + 1 + cl.gameState.dataCount > MAX_GAMESTATE_CHARS )",
		"cl.gameState.stringOffsets[ i ] = cl.gameState.dataCount;",
		"Com_Memcpy( cl.gameState.stringData + cl.gameState.dataCount, dup, len + 1 );",
		"if ( index == CS_SYSTEMINFO )",
		"CL_SystemInfoChanged();",
	):
		assert source_anchor in configstring_modified

	for hlil_anchor in (
		"004af570    int32_t sub_4af570(void* arg1, int32_t* arg2)",
		"004af573  int32_t eax = data_146cd30",
		"004af599  if (eax - arg1 s< 0x20)",
		"004af5a9      int32_t* ebx_3 = (arg1 & 0x1f) * 0x298 + 0x1472874",
		"004af5f2          sub_4cb7d0(&arg2[3], &ebx_3[6], 0x20)",
		"004af602          __builtin_memcpy(dest: &arg2[0xb], src: &ebx_3[0xf], n: 0x250)",
		"004af613          if (edx_2 s> 0x180)",
		"004af67a                  __builtin_memcpy(dest: edi_2, src: esi_5, n: 0xec)",
		"004af689          return 1",
		"004af690    int32_t sub_4af690()",
		"004af6b7  int32_t esi = atoi(sub_4c7ee0(1))",
		"004af6cc  if (esi s< 0 || esi s>= 0x400)",
		'004af6d5      sub_4c9b60(1, "configstring > MAX_CONFIGSTRINGS")',
		"004af6df  sub_4c7fd0(2)",
		"004af73f      int32_t var_4e8c[0x1399]",
		"004af750      result = sub_4c95e0(&data_146cfd4, 0, 0x4e84)",
		'004af7b0                  sub_4c9b60(1, "MAX_GAMESTATE_CHARS exceeded")',
		"004af807          result = sub_4bd620(esi)",
	):
		assert hlil_anchor in hlil

	assert "case CG_GETSNAPSHOT:" in cgame_system_calls
	assert "return CL_GetSnapshot( args[1], VMA(2) ) ? qtrue : qfalse;" in cgame_system_calls
	assert "case CG_GETSERVERCOMMAND:" in cgame_system_calls
	assert "return CL_GetServerCommand( args[1] ) ? qtrue : qfalse;" in cgame_system_calls
	assert "ql_cgame_imports[CG_QL_IMPORT_GETSNAPSHOT] = (ql_import_f)QL_CG_trap_GetSnapshot;" in cl_cgame
	assert "ql_cgame_imports[CG_QL_IMPORT_GETSERVERCOMMAND] = (ql_import_f)QL_CG_trap_GetServerCommand;" in cl_cgame
	assert "static qboolean QDECL QL_CG_trap_GetSnapshot( int snapshotNumber, snapshot_t *snapshot )" in cgame_imports
	assert "return CG_Import_Syscall( CG_GETSNAPSHOT, snapshotNumber, snapshot );" in cgame_imports
	assert "CG_QL_IMPORT_GETSNAPSHOT = 87," in cg_public
	assert "CG_QL_IMPORT_GETSERVERCOMMAND = 88," in cg_public
	assert "case CG_GETSNAPSHOT: return CG_QL_IMPORT_GETSNAPSHOT;" in cg_map_native
	assert "case CG_GETSERVERCOMMAND: return CG_QL_IMPORT_GETSERVERCOMMAND;" in cg_map_native
	assert "return syscall( CG_GETSNAPSHOT, snapshotNumber, snapshot ) ? qtrue : qfalse;" in trap_get_snapshot


def test_post_structure_tail_is_client_cgame_timing_and_roq_cinematic_boundary() -> None:
	aliases = _aliases()
	rows = _function_rows_in_post_structure_boundary()
	cl_cgame = _read(CLIENT_CL_CGAME)
	cl_cin = _read(CLIENT_CL_CIN)
	hlil = _read(QL_STEAM_HLIL_PART04)

	assert {address: aliases[address] for address in POST_STRUCTURE_BOUNDARY_ALIASES} == POST_STRUCTURE_BOUNDARY_ALIASES
	assert rows == EXPECTED_POST_STRUCTURE_BOUNDARY_ROWS

	game_command = _extract_function_block(cl_cgame, "qboolean CL_GameCommand( void )")
	cgame_rendering = _extract_function_block(cl_cgame, "void CL_CGameRendering( stereoFrame_t stereo )")
	adjust_time_delta = _extract_function_block(cl_cgame, "void CL_AdjustTimeDelta( void )")
	first_snapshot = _extract_function_block(cl_cgame, "void CL_FirstSnapshot( void )")
	set_cgame_time = _extract_function_block(cl_cgame, "void CL_SetCGameTime( void )")
	decode_stereo = _extract_function_block(
		cl_cin,
		"long RllDecodeStereoToStereo(unsigned char *from,short *to,unsigned int size,char signedOutput, unsigned short flag)",
	)
	move8 = _extract_function_block(cl_cin, "static void move8_32( byte *src, byte *dst, int spl )")
	blit8 = _extract_function_block(cl_cin, "static void blit8_32( byte *src, byte *dst, int spl  )")
	blit_vq = _extract_function_block(cl_cin, "static void blitVQQuad32fs( byte **status, unsigned char *data )")
	gen_yuv = _extract_function_block(cl_cin, "static void ROQ_GenYUVTables( void )")
	init_roq = _extract_function_block(cl_cin, "static void initRoQ()")
	cgame_import_integrity = _extract_function_block(cl_cgame, "void CL_CheckCGameNativeImportIntegrity( void )")

	for source_anchor in (
		"if ( !cgvm )",
		"return VM_Call( cgvm, CG_CONSOLE_COMMAND ) ? qtrue : qfalse;",
	):
		assert source_anchor in game_command

	for source_anchor in (
		"demoPlaying = clc.demoplaying ? qtrue : qfalse;",
		"VM_Call( cgvm, CG_DRAW_ACTIVE_FRAME, cl.serverTime, stereo, demoPlaying );",
		"VM_Debug( 0 );",
	):
		assert source_anchor in cgame_rendering

	for source_anchor in (
		"cl.newSnapshots = qfalse;",
		"if ( clc.demoplaying )",
		"cl.serverTimeDelta = newDelta;",
		"cl.oldServerTime = cl.snap.serverTime;",
		"cl.serverTimeDelta = ( cl.serverTimeDelta + newDelta ) >> 1;",
		"cl.serverTimeDelta -= 2;",
		"cl.serverTimeDelta++;",
	):
		assert source_anchor in adjust_time_delta

	for source_anchor in (
		"if ( cl.snap.snapFlags & SNAPFLAG_NOT_ACTIVE )",
		"cls.state = CA_ACTIVE;",
		"cl.serverTimeDelta = cl.snap.serverTime - cls.realtime;",
		"CL_WebView_PublishGameStart();",
		"Cbuf_AddText( cl_activeAction->string );",
		"Sys_BeginProfiling();",
	):
		assert source_anchor in first_snapshot

	for source_anchor in (
		"if ( cls.state != CA_PRIMED )",
		"CL_ReadDemoMessage();",
		"CL_FirstSnapshot();",
		'Com_Error( ERR_DROP, "CL_SetCGameTime: !cl.snap.valid" );',
		"cl.serverTime = cls.realtime + cl.serverTimeDelta - tn;",
		"if ( cl.newSnapshots )",
		"CL_AdjustTimeDelta();",
		"cl.serverTime = clc.timeDemoBaseTime + clc.timeDemoFrames * 50;",
	):
		assert source_anchor in set_cgame_time

	assert "sub_4B0A50" not in aliases
	assert "ql_cgame_imports[CG_QL_IMPORT_R_ADDREFENTITYTOSCENE] != (ql_import_f)QL_CG_trap_R_AddRefEntityToScene ||" in cgame_import_integrity
	assert "ql_cgame_imports[CG_QL_IMPORT_R_RENDERSCENE] != (ql_import_f)QL_CG_trap_R_RenderScene )" in cgame_import_integrity
	assert "CL_SetRetailClientMessageCGameImportGuardFlag();" in cgame_import_integrity

	for source_anchor in (
		"prevL = flag & 0xff00;",
		"prevR = (flag & 0x00ff) << 8;",
		"prevL = (short)(prevL + cin.sqrTable[*zz++]);",
		"prevR = (short)(prevR + cin.sqrTable[*zz++]);",
		"to[z+0] = (short)(prevL);",
		"to[z+1] = (short)(prevR);",
		"return (size>>1);",
	):
		assert source_anchor in decode_stereo

	assert "dsrc += dspl; ddst += dspl;" in move8
	assert "dsrc += 4; ddst += dspl;" in blit8
	assert "blit8_32( (byte *)&vq8[(*data)*128], status[index], spl );" in blit_vq
	assert "move8_32( status[index] + cin.mcomp[(*data)], status[index], spl );" in blit_vq
	assert "ROQ_UB_tab[i] = (long)( ( t_ub * x) + (1<<5));" in gen_yuv
	assert "ROQ_YY_tab[i] = (long)( (i << 6) | (i >> 2) );" in gen_yuv
	assert "cinTable[currentHandle].VQNormal = (void (*)(byte *, void *))blitVQQuad32fs;" in init_roq
	assert "cinTable[currentHandle].VQBuffer = (void (*)(byte *, void *))blitVQQuad32fs;" in init_roq
	assert "ROQ_GenYUVTables();" in init_roq

	for retail_anchor in (
		"004b0610    int32_t sub_4b0610()",
		"004b0624      jump(*(data_146cc38 + 0xc))",
		"004b061b  return 0",
		"004b0630    int32_t sub_4b0630(int32_t arg1)",
		"004b0652  return (*(data_146cc38 + 0x10))(data_146cfbc, arg1, data_16177e0)",
		"004b0660    void sub_4b0660(int32_t arg1 @ esi)",
		"004b0667  data_146cfd0 = 0",
		'004b06c0              sub_4c9860(esi_1, "<RESET> ")',
		'004b06e0              sub_4c9860(esi_1, "<FAST> ")',
		"004b0760    void sub_4b0760()",
		"004b0767  if ((data_146cd28 & 2) != 0)",
		"004b07b6  return sub_4d7980() __tailcall",
		"004b07c0    int32_t* __fastcall sub_4b07c0(int32_t arg1)",
		'004b0838          sub_4c9b60(1, "CL_SetCGameTime: !cl.snap.valid")',
		"004b0817          result = sub_4b0760()",
		"004b09b8              result = sub_4b0660(esi)",
		"004b0a50    int32_t sub_4b0a50()",
		"004b0a66  if (data_565a74 != sub_4b0000 || data_565a88 != sub_4bef80)",
		"004b0a68      data_565948 |= 0x40",
		"004b0a70    uint32_t sub_4b0a70(char* arg1, int32_t arg2, int32_t arg3, char arg4, int16_t arg5)",
		"004b0a8e  if (arg4 != 0)",
		"004b0aef  return eax u>> 1",
		"004b0af0    void* __convention(\"regparm\") sub_4b0af0(double* arg1, int32_t arg2, double* arg3)",
		"004b0bd0    void __convention(\"regparm\") sub_4b0bd0(double* arg1, int32_t arg2, double* arg3)",
		"004b0cd0    int32_t sub_4b0cd0(int32_t arg1, void* arg2)",
		"004b0d94          sub_4b0bd0((zx.d(*esi) << 8) + &data_10c18f0, edi, *(arg1 + (ebx << 2)))",
		"004b0d73          sub_4b0af0(*((zx.d(*esi) << 2) + &data_1060cd8) + ecx_7, edi, ecx_7)",
		"004b0f60    int32_t sub_4b0f60()",
		"004b0fa6          sub_526000(x87_r2_2 * fconvert.t(57.203998565673828) + x87_r6)",
		"004b0fea      *((esi << 2) + &data_114b930) = result",
		"004b21d4      *(eax + 0x1149a5c) = sub_4b0cd0",
		"004b21da      *(eax + 0x1149a60) = sub_4b0cd0",
		"004b21ea      sub_4b0f60()",
	):
		assert retail_anchor in hlil


def test_roq_cinematic_continuation_is_client_video_decode_not_botlib_tail() -> None:
	aliases = _aliases()
	rows = _function_rows_in_roq_cinematic_continuation()
	cl_cin = _read(CLIENT_CL_CIN)
	hlil = _read(QL_STEAM_HLIL_PART04)

	assert {address: aliases[address] for address in ROQ_CINEMATIC_CONTINUATION_ALIASES} == ROQ_CINEMATIC_CONTINUATION_ALIASES
	assert rows == EXPECTED_ROQ_CINEMATIC_CONTINUATION_ROWS

	yuv565 = _extract_function_block(cl_cin, "static unsigned short yuv_to_rgb( long y, long u, long v )")
	yuv24 = _extract_function_block(cl_cin, "static unsigned int yuv_to_rgb24( long y, long u, long v )")
	decode_code_book = _extract_function_block(cl_cin, "static void decodeCodeBook( byte *input, unsigned short roq_flags )")
	recurse_quad = _extract_function_block(
		cl_cin,
		"static void recurseQuad( long startX, long startY, long quadSize, long xOff, long yOff )",
	)
	setup_quad = _extract_function_block(cl_cin, "static void setupQuad( long xOff, long yOff )")
	read_quad_info = _extract_function_block(cl_cin, "static void readQuadInfo( byte *qData )")
	roq_prep_mcomp = _extract_function_block(cl_cin, "static void RoQPrepMcomp( long xoff, long yoff )")
	roq_init_tables = _extract_function_block(cl_cin, "static void initRoQ()")
	roq_init_stream = _extract_function_block(cl_cin, "static void RoQ_init( void )\n{")
	roq_shutdown = _extract_function_block(cl_cin, "static void RoQShutdown( void )")
	cin_stop = _extract_function_block(cl_cin, "e_status CIN_StopCinematic(int handle)")
	cin_set_extents = _extract_function_block(cl_cin, "void CIN_SetExtents (int handle, int x, int y, int w, int h)")
	cin_draw = _extract_function_block(cl_cin, "void CIN_DrawCinematic (int handle)")
	cin_upload = _extract_function_block(cl_cin, "void CIN_UploadCinematic(int handle)")
	cin_close_all = _extract_function_block(cl_cin, "void CIN_CloseAllVideos(void)")
	roq_reset = _extract_function_block(cl_cin, "static void RoQReset()")
	roq_interrupt = _extract_function_block(cl_cin, "static void RoQInterrupt(void)")
	cin_run = _extract_function_block(cl_cin, "e_status CIN_RunCinematic (int handle)")
	cin_play = _extract_function_block(
		cl_cin,
		"int CIN_PlayCinematic( const char *arg, int x, int y, int w, int h, int systemBits )",
	)
	scr_draw = _extract_function_block(cl_cin, "void SCR_DrawCinematic (void)")
	scr_run = _extract_function_block(cl_cin, "void SCR_RunCinematic (void)")
	scr_stop = _extract_function_block(cl_cin, "void SCR_StopCinematic(void)")

	for source_anchor in (
		"r = (YY + ROQ_VR_tab[v]) >> 9;",
		"g = (YY + ROQ_UG_tab[u] + ROQ_VG_tab[v]) >> 8;",
		"return (unsigned short)((r<<11)+(g<<5)+(b));",
	):
		assert source_anchor in yuv565

	for source_anchor in (
		"r = (YY + ROQ_VR_tab[v]) >> 6;",
		"g = (YY + ROQ_UG_tab[u] + ROQ_VG_tab[v]) >> 6;",
		"return LittleLong ((r)|(g<<8)|(b<<16)|(255<<24));",
	):
		assert source_anchor in yuv24

	for source_anchor in (
		"if (!roq_flags)",
		"two  = roq_flags>>8;",
		"four = roq_flags&0xff;",
		"four *= 2;",
		"bptr = (unsigned short *)vq2;",
		"if (!cinTable[currentHandle].half)",
		"if (!cinTable[currentHandle].smootheddouble)",
		"if (cinTable[currentHandle].samplesPerPixel==2)",
		"} else if (cinTable[currentHandle].samplesPerPixel==4) {",
		"} else if (cinTable[currentHandle].samplesPerPixel==1) {",
		"*ibptr++ = yuv_to_rgb24( ((y0*3)+y2)/4, cr, cb );",
		"VQ2TO4(iaptr, ibptr, icptr, idptr);",
		"VQ2TO2(iaptr,ibptr,icptr,idptr);",
	):
		assert source_anchor in decode_code_book

	for source_anchor in (
		"cin.qStatus[0][cinTable[currentHandle].onQuad  ] = scroff;",
		"cin.qStatus[1][cinTable[currentHandle].onQuad++] = scroff+offset;",
		"recurseQuad( startX,\t\t  startY\t\t  , quadSize, xOff, yOff );",
		"numQuadCels += 64;",
		"cinTable[currentHandle].onQuad = 0;",
		"cin.qStatus[0][i] = temp;",
	):
		assert source_anchor in recurse_quad or source_anchor in setup_quad

	for source_anchor in (
		"cinTable[currentHandle].xsize    = qData[0]+qData[1]*256;",
		"cinTable[currentHandle].screenDelta = cinTable[currentHandle].CIN_HEIGHT*cinTable[currentHandle].samplesPerLine;",
		"cinTable[currentHandle].VQ0 = cinTable[currentHandle].VQNormal;",
		"cinTable[currentHandle].drawX = cinTable[currentHandle].CIN_WIDTH;",
		"Com_Printf(\"HACK: approxmimating cinematic for Rage Pro or Voodoo\\n\");",
	):
		assert source_anchor in read_quad_info

	for source_anchor in (
		"temp2 = (y+yoff-8)*i;",
		"temp = (x+xoff-8)*j;",
		"cin.mcomp[(x*16)+y] = cinTable[currentHandle].normalBuffer0-(temp2+temp);",
		"cinTable[currentHandle].VQNormal = (void (*)(byte *, void *))blitVQQuad32fs;",
		"RllSetupTable();",
	):
		assert source_anchor in roq_prep_mcomp or source_anchor in roq_init_tables

	for source_anchor in (
		"cinTable[currentHandle].RoQPlayed = 24;",
		"cinTable[currentHandle].roqFPS\t = cin.file[ 6] + cin.file[ 7]*256;",
		"if (!cinTable[currentHandle].roqFPS) cinTable[currentHandle].roqFPS = 30;",
		"cinTable[currentHandle].roq_id\t\t= cin.file[ 8] + cin.file[ 9]*256;",
		"cinTable[currentHandle].RoQFrameSize\t= cin.file[10] + cin.file[11]*256 + cin.file[12]*65536;",
	):
		assert source_anchor in roq_init_stream

	for source_anchor in (
		"Com_DPrintf(\"finished cinematic\\n\");",
		"Sys_EndStreamedFile( cinTable[currentHandle].iFile );",
		"Cbuf_ExecuteText( EXEC_APPEND, va(\"%s\\n\", s) );",
		"CL_handle = -1;",
		"Com_DPrintf(\"trFMV::stop(), closing %s\\n\", cinTable[currentHandle].fileName);",
		"cinTable[currentHandle].status = FMV_EOF;",
		"RoQShutdown();",
	):
		assert source_anchor in roq_shutdown or source_anchor in cin_stop

	for source_anchor in (
		"cinTable[handle].xpos = x;",
		"cinTable[handle].height = h;",
		"cinTable[handle].dirty = qtrue;",
		"SCR_AdjustFrom640( &x, &y, &w, &h );",
		"re.DrawStretchRaw( x, y, w, h, cinTable[handle].drawX, cinTable[handle].drawY, buf, handle, cinTable[handle].dirty);",
		"CIN_StopCinematic(i);",
	):
		assert source_anchor in cin_set_extents or source_anchor in cin_draw or source_anchor in cin_close_all

	for source_anchor in (
		"Sys_EndStreamedFile(cinTable[currentHandle].iFile);",
		"FS_FOpenFileRead (cinTable[currentHandle].fileName, &cinTable[currentHandle].iFile, qtrue);",
		"Sys_BeginStreamedFile( cinTable[currentHandle].iFile, 0x10000 );",
		"Sys_StreamedRead (cin.file, 16, 1, cinTable[currentHandle].iFile);",
		"RoQ_init();",
		"cinTable[currentHandle].status = FMV_LOOPED;",
	):
		assert source_anchor in roq_reset

	for source_anchor in (
		"Sys_StreamedRead( cin.file, cinTable[currentHandle].RoQFrameSize+8, 1, cinTable[currentHandle].iFile );",
		"if ( cinTable[currentHandle].RoQPlayed >= cinTable[currentHandle].ROQSize )",
		"case\tROQ_QUAD_VQ:",
		"RoQPrepMcomp( cinTable[currentHandle].roqF0, cinTable[currentHandle].roqF1 );",
		"decodeCodeBook( framedata, (unsigned short)cinTable[currentHandle].roq_flags );",
		"RllDecodeStereoToStereo( framedata, sbuf, cinTable[currentHandle].RoQFrameSize, 0, (unsigned short)cinTable[currentHandle].roq_flags);",
		"readQuadInfo( framedata );",
		"setupQuad( 0, 0 );",
		"cinTable[currentHandle].roq_id\t\t = framedata[0] + framedata[1]*256;",
		"cinTable[currentHandle].RoQFrameSize = framedata[2] + framedata[3]*256 + framedata[4]*65536;",
		"if (cinTable[currentHandle].RoQFrameSize>65536||cinTable[currentHandle].roq_id==0x1084)",
		"if (cinTable[currentHandle].inMemory && (cinTable[currentHandle].status != FMV_EOF))",
		"cinTable[currentHandle].RoQPlayed\t+= cinTable[currentHandle].RoQFrameSize+8;",
	):
		assert source_anchor in roq_interrupt

	for source_anchor in (
		"RoQInterrupt();",
		"cinTable[currentHandle].tfps = ((((CL_ScaledMilliseconds()*com_timescale->value) - cinTable[currentHandle].startTime)*3)/100);",
		"if (cinTable[currentHandle].status == FMV_LOOPED)",
		"if (cinTable[currentHandle].status == FMV_EOF)",
		"return cinTable[currentHandle].status;",
	):
		assert source_anchor in cin_run

	for source_anchor in (
		"currentHandle = CIN_HandleForVideo();",
		"Com_DPrintf(\"SCR_PlayCinematic( %s )\\n\", arg);",
		"CIN_SetExtents(currentHandle, x, y, w, h);",
		"RoQ_init();",
		"CIN_DrawCinematic(CL_handle);",
		"CIN_RunCinematic(CL_handle);",
		"CIN_StopCinematic(CL_handle);",
		"re.UploadCinematic( cinTable[handle].drawX, cinTable[handle].drawY, cinTable[handle].drawX, cinTable[handle].drawY, cinTable[handle].buf, handle, cinTable[handle].dirty);",
	):
		assert source_anchor in cin_play or source_anchor in scr_draw or source_anchor in scr_run or source_anchor in scr_stop or source_anchor in cin_upload

	for retail_anchor in (
		"004b1010    int32_t __convention(\"regparm\") sub_4b1010",
		"004b107e  return (((eax_2 << 6) + ecx_2) << 5) + edx_2",
		"004b1080    int32_t __convention(\"regparm\") sub_4b1080",
		"004b10fb  return ((eax_2 | 0xffffff00) << 8 | ecx_3) << 8 | edx_1",
		"004b1100    void* __convention(\"regparm\") sub_4b1100",
		"004b111e      i_34 = eax_1 u>> 8",
		"004b1153  if (*(edi_1 + 0x1149a7c) != 0)",
		"004b1561                  *ebx = sub_4b1010(eax_20, edx_31, edi_18)",
		"004b1cf8                  eax_122, edx_100 = sub_4b1080(eax_121, i_34, ecx_41, edi_36)",
		"004b1d92  return result",
		"004b1da0    int32_t sub_4b1da0",
		"004b1eb0    int32_t sub_4b1eb0",
		"004b1fc0    int32_t __fastcall sub_4b1fc0(char* arg1)",
		"004b2110    int32_t sub_4b2110(int32_t arg1, int32_t arg2)",
		"004b2220    void* sub_4b2220",
		"004b2300    char* sub_4b2300()",
		"004b2400    int32_t sub_4b2400(int32_t arg1)",
		"004b2480    void* sub_4b2480",
		"004b24d0    void sub_4b24d0(int32_t arg1)",
		"004b2790    int32_t sub_4b2790()",
		"004b27bb      sub_4b2400(result)",
		"004b27e0    void sub_4b27e0(int32_t arg1)",
		"004b2861          data_146ccb0(0x100, 0x100, 0x100, 0x100, ecx_1, arg1, *(esi_2 + 0x1149a10))",
		"004b2890    void sub_4b2890()",
		"004b2910    void* sub_4b2910()",
		"004b29d0    void* sub_4b29d0",
		"004b2a16          sub_4ed020(&data_1050ad8, *(eax_3 + 0x1149a3c) + 8, 1, *(eax_3 + 0x1149a20))",
		"004b2bb0                  int32_t eax_7",
		"004b2c41              case 0x20",
		"004b2d59          int32_t ecx_20 = data_565b5c",
		"004b2dee              if (*(esi_2 + 0x1149a3c) u<= 0x10000 && *(esi_2 + 0x1149a4c) != 0x1084)",
		"004b2e91              sub_4c9ab0(\"roq_size>65536||roq_id==0x1084\\n\")",
		"004b2eb6          eax_2 = sub_4b2910()",
		"004b2f40    int32_t sub_4b2f40(int32_t arg1)",
		"004b2f84              x87control = sub_4b2910()",
		"004b3160    int32_t sub_4b3160",
		"004b3510    int32_t sub_4b3510()",
		"004b351b      result = sub_4b2f40(result)",
	):
		assert retail_anchor in hlil


def test_promoted_aliases_through_roq_cinematic_boundary_have_botlib_parity_mentions() -> None:
	test_text = _test_botlib_file_text()
	missing_mentions = {
		retail_name: promoted_name
		for retail_name, promoted_name in _promoted_aliases_in_botlib_boundary_range().items()
		if retail_name not in test_text and promoted_name not in test_text
	}

	assert missing_mentions == {}
