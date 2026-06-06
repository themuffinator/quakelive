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
SERVER_SV_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SERVER_QL_GAME_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"
GAME_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"

EXPECTED_WORLD_IMPORT_ALIASES = {
	"4E1470": ("QL_G_trap_SetBrushModel", 9),
	"4E1480": ("QL_G_trap_Trace", 43),
	"4E14B0": ("QL_G_trap_TraceCapsule", 43),
	"4E14E0": ("QL_G_trap_PointContents", 9),
	"4DD230": ("BotImport_inPVS", 9),
	"4E14F0": ("QL_G_trap_InPVSIgnorePortals", 9),
	"4E1500": ("SV_AdjustAreaPortalState", 86),
	"4E1560": ("QL_G_trap_AreasConnected", 9),
	"4E1570": ("QL_G_trap_LinkEntity", 9),
	"4E1580": ("QL_G_trap_UnlinkEntity", 9),
	"4E1590": ("QL_G_trap_EntitiesInBox", 9),
	"4E15A0": ("SV_EntityContact", 99),
}

EXPECTED_NATIVE_WORLD_IMPORT_SLOTS = (
	("G_QL_IMPORT_SET_BRUSH_MODEL = 31,", "G_SET_BRUSH_MODEL", "QL_G_trap_SetBrushModel"),
	("G_QL_IMPORT_TRACE = 32,", "G_TRACE", "QL_G_trap_Trace"),
	("G_QL_IMPORT_TRACECAPSULE = 33,", "G_TRACECAPSULE", "QL_G_trap_TraceCapsule"),
	("G_QL_IMPORT_POINT_CONTENTS = 34,", "G_POINT_CONTENTS", "QL_G_trap_PointContents"),
	("G_QL_IMPORT_IN_PVS = 35,", "G_IN_PVS", "QL_G_trap_InPVS"),
	(
		"G_QL_IMPORT_IN_PVS_IGNORE_PORTALS = 36,",
		"G_IN_PVS_IGNORE_PORTALS",
		"QL_G_trap_InPVSIgnorePortals",
	),
	(
		"G_QL_IMPORT_ADJUST_AREA_PORTAL_STATE = 37,",
		"G_ADJUST_AREA_PORTAL_STATE",
		"QL_G_trap_AdjustAreaPortalState",
	),
	("G_QL_IMPORT_AREAS_CONNECTED = 38,", "G_AREAS_CONNECTED", "QL_G_trap_AreasConnected"),
	("G_QL_IMPORT_LINKENTITY = 39,", "G_LINKENTITY", "QL_G_trap_LinkEntity"),
	("G_QL_IMPORT_UNLINK_ENTITY = 40,", "G_UNLINKENTITY", "QL_G_trap_UnlinkEntity"),
	("G_QL_IMPORT_ENTITIES_IN_BOX = 41,", "G_ENTITIES_IN_BOX", "QL_G_trap_EntitiesInBox"),
	("G_QL_IMPORT_ENTITY_CONTACT = 42,", "G_ENTITY_CONTACT", "QL_G_trap_EntityContact"),
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _aliases() -> dict[str, str]:
	return json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]


def _function_rows() -> dict[str, str]:
	rows: dict[str, str] = {}
	with FUNCTIONS_CSV.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			rows[row["entry"].upper()[2:]] = (
				f'{row["name"]},{row["entry"]},{row["size"]},{row["thunk"]},{row["calling_convention"]}'
			)
	return rows


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


def test_qagame_world_import_slab_aliases_and_rows_are_pinned() -> None:
	aliases = _aliases()
	rows = _function_rows()

	for address, (name, size) in EXPECTED_WORLD_IMPORT_ALIASES.items():
		assert aliases[f"sub_{address}"] == name
		assert rows[address] == f"FUN_00{address.lower()},00{address.lower()},{size},0,unknown"


def test_qagame_world_import_slab_hlil_table_order_is_pinned() -> None:
	game_hlil = _read(QL_STEAM_HLIL_PART05)
	table_hlil = _read(QL_STEAM_HLIL_PART07)

	for hlil_anchor in (
		"004e1470    int32_t sub_4e1470()",
		"004e1474  return sub_4e1160() __tailcall",
		"004e1480    int32_t sub_4e1480(int32_t arg1, float* arg2, int32_t* arg3, int32_t* arg4, float* arg5, int32_t arg6, int32_t arg7)",
		"004e14aa  return sub_4e6930(arg1, arg2, arg3, arg4, arg5, arg6, arg7, 0)",
		"004e14b0    int32_t sub_4e14b0(int32_t arg1, float* arg2, int32_t* arg3, int32_t* arg4, float* arg5, int32_t arg6, int32_t arg7)",
		"004e14da  return sub_4e6930(arg1, arg2, arg3, arg4, arg5, arg6, arg7, 1)",
		"004e14e4  return sub_4e6ac0() __tailcall",
		"004e14f4  return sub_4e12c0() __tailcall",
		"004e1500    void* sub_4e1500(int32_t* arg1, int32_t arg2)",
		"004e151f  sub_4c9b60(1, \"SV_SvEntityForGentity: bad gEnt\")",
		"004e154c          return sub_4c4e90(*(result + 0x13c), ecx, arg2)",
		"004e1564  return sub_4c4f50() __tailcall",
		"004e1574  return sub_4e5f50() __tailcall",
		"004e1584  return sub_4e5ee0() __tailcall",
		"004e1594  return sub_4e6650() __tailcall",
		"004e15a0    int32_t sub_4e15a0(int32_t* arg1, int32_t* arg2, void* arg3)",
		"004e15e7  sub_4c7900(&var_40, &data_124a6b4, &data_124a6b4, arg1, arg2, sub_4e5cb0(arg3, 0),",
	):
		assert hlil_anchor in game_hlil

	for table_anchor in (
		"0056cffc  void* data_56cffc = sub_4e1470",
		"0056d000  void* data_56d000 = sub_4e1480",
		"0056d004  void* data_56d004 = sub_4e14b0",
		"0056d008  void* data_56d008 = sub_4e14e0",
		"0056d00c  void* data_56d00c = sub_4dd230",
		"0056d010  void* data_56d010 = sub_4e14f0",
		"0056d014  void* data_56d014 = sub_4e1500",
		"0056d018  void* data_56d018 = sub_4e1560",
		"0056d01c  void* data_56d01c = sub_4e1570",
		"0056d020  void* data_56d020 = sub_4e1580",
		"0056d024  void* data_56d024 = sub_4e1590",
		"0056d028  void* data_56d028 = sub_4e15a0",
		"0056d02c  void* data_56d02c = j_sub_4dcd30",
	):
		assert table_anchor in table_hlil


def test_qagame_world_import_slots_are_bound_to_direct_native_mappings() -> None:
	g_public = _read(GAME_PUBLIC)
	g_syscalls = _read(GAME_SYSCALLS)
	sv_game = _read(SERVER_SV_GAME)
	ql_game_imports = _read(SERVER_QL_GAME_IMPORTS)
	syscall_map = _extract_function_block(g_syscalls, "static int G_MapNativeImport")
	init_imports = _extract_function_block(sv_game, "static void SV_InitGameImports")

	for slot_anchor, legacy_import, trap_name in EXPECTED_NATIVE_WORLD_IMPORT_SLOTS:
		slot_name = slot_anchor.split(" = ", 1)[0]
		assert slot_anchor in g_public
		assert f"case {legacy_import}: return {slot_name};" in syscall_map
		assert f"ql_game_imports[{slot_name}] = (ql_import_f){trap_name};" in init_imports

	assert init_imports.index("G_QL_IMPORT_LINKENTITY") < init_imports.index("G_QL_IMPORT_UNLINK_ENTITY")
	assert g_public.index("G_QL_IMPORT_LINKENTITY = 39,") < g_public.index("G_QL_IMPORT_UNLINK_ENTITY = 40,")

	for wrapper_anchor in (
		"static qboolean QDECL QL_G_trap_InPVSIgnorePortals( const vec3_t p1, const vec3_t p2 )",
		"return G_Import_Syscall( G_IN_PVS_IGNORE_PORTALS, p1, p2 );",
		"static qboolean QDECL QL_G_trap_AreasConnected( int area1, int area2 )",
		"return G_Import_Syscall( G_AREAS_CONNECTED, area1, area2 );",
		"static void QDECL QL_G_trap_LinkEntity( sharedEntity_t *ent )",
		"G_Import_Syscall( G_LINKENTITY, ent );",
		"static void QDECL QL_G_trap_UnlinkEntity( sharedEntity_t *ent )",
		"G_Import_Syscall( G_UNLINKENTITY, ent );",
		"static qboolean QDECL QL_G_trap_EntityContact( const vec3_t mins, const vec3_t maxs, const sharedEntity_t *ent )",
		"return G_Import_Syscall( G_ENTITY_CONTACT, mins, maxs, ent );",
	):
		assert wrapper_anchor in ql_game_imports
