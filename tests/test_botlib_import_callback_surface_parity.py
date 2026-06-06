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
BOTLIB_H = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
SERVER_SV_BOT = REPO_ROOT / "src" / "code" / "server" / "sv_bot.c"

EXPECTED_IMPORT_CALLBACK_ROWS = {
	"4DCF90": ("BotImport_Print", 90),
	"4DD0B0": ("BotImport_Trace", 173),
	"4DD160": ("BotImport_EntityTrace", 173),
	"4DD210": ("BotImport_PointContents", 19),
	"4DD230": ("BotImport_inPVS", 9),
	"4DD240": ("BotImport_BSPEntityData", None),
	"4DD250": ("BotImport_BSPModelMinsMaxsOrigin", 246),
	"4DD640": ("BotClientCommand", 35),
	"4DD350": ("BotImport_GetMemory", 19),
	"4DD370": ("BotImport_FreeMemory", 9),
	"4DD380": ("BotImport_HunkAlloc", 43),
	"4DD450": ("BotImport_DebugLineCreate", 46),
	"4DD430": ("BotImport_DebugPolygonDelete", 30),
	"4DD480": ("BotImport_DebugLineShow", 448),
	"4DD3B0": ("BotImport_DebugPolygonCreate", 125),
	"4DD940": ("SV_BotInitBotLib", 263),
}

EXPECTED_SOURCE_IMPORT_ORDER = (
	("Print", "BotImport_Print"),
	("Trace", "BotImport_Trace"),
	("EntityTrace", "BotImport_EntityTrace"),
	("PointContents", "BotImport_PointContents"),
	("inPVS", "BotImport_inPVS"),
	("BSPEntityData", "BotImport_BSPEntityData"),
	("BSPModelMinsMaxsOrigin", "BotImport_BSPModelMinsMaxsOrigin"),
	("BotClientCommand", "BotClientCommand"),
	("GetMemory", "BotImport_GetMemory"),
	("FreeMemory", "BotImport_FreeMemory"),
	("AvailableMemory", "Z_AvailableMemory"),
	("HunkAlloc", "BotImport_HunkAlloc"),
	("FS_FOpenFile", "FS_FOpenFileByMode"),
	("FS_Read", "FS_Read2"),
	("FS_Write", "FS_Write"),
	("FS_FCloseFile", "FS_FCloseFile"),
	("FS_Seek", "FS_Seek"),
	("DebugLineCreate", "BotImport_DebugLineCreate"),
	("DebugLineDelete", "BotImport_DebugPolygonDelete"),
	("DebugLineShow", "BotImport_DebugLineShow"),
	("DebugPolygonCreate", "BotImport_DebugPolygonCreate"),
	("DebugPolygonDelete", "BotImport_DebugPolygonDelete"),
)

EXPECTED_RETAIL_IMPORT_LOCALS = (
	"004dd99c  int32_t (* var_5c)(int32_t arg1, int32_t arg2) = sub_4dcf90",
	"004dd9a3  int32_t (* var_58)(int32_t* arg1, float* arg2, int32_t* arg3, int32_t* arg4, float* arg5,",
	"004dd9aa  int32_t (* var_54)(int32_t* arg1, float* arg2, int32_t* arg3, int32_t* arg4, float* arg5,",
	"004dd9b1  int32_t (* var_50)(float* arg1) = sub_4dd210",
	"004dd9b8  int32_t (* var_4c)() = sub_4dd230",
	"004dd9bf  int32_t (* var_48)() = j_sub_4c0250",
	"004dd9c6  float* (* var_44)(int32_t arg1, float* arg2, float* arg3, float* arg4, float* arg5) =",
	"004dd9cd  void* (* var_40)(int32_t arg1, char* arg2) = sub_4dd640",
	"004dd9d4  void* (* var_3c)(int32_t arg1) = sub_4dd350",
	"004dd9db  int32_t (* var_38)() = sub_4dd370",
	"004dd9e2  int32_t (* var_34)() = sub_4c9220",
	"004dd9e9  char* (* var_30)(int32_t arg1) = sub_4dd380",
	"004dd9f0  int32_t (* var_2c)(int32_t arg1, int32_t* arg2, int32_t arg3) = sub_4d22c0",
	"004dd9f7  void* (* var_28)(int32_t arg1, int32_t arg2, int32_t arg3) = sub_4d2a80",
	"004dd9fe  int32_t (* var_24)(int32_t arg1, int32_t arg2, int32_t arg3) = sub_4d00f0",
	"004dda05  int32_t (* var_20)(int32_t arg1) = sub_4cf320",
	"004dda0c  int32_t (* var_1c)(int32_t arg1 @ edi, int32_t arg2, int32_t arg3, int32_t arg4) =",
	"004dda13  int32_t (* var_18)() = sub_4dd450",
	"004dda1a  int32_t (* var_14)(int32_t arg1) = sub_4dd430",
	"004dda21  int32_t (* var_10)(int32_t arg1, float* arg2, float* arg3, int32_t arg4) = sub_4dd480",
	"004dda28  int32_t (* var_c)(int32_t arg1, int32_t arg2, int32_t* arg3) = sub_4dd3b0",
	"004dda2f  int32_t (* var_8)(int32_t arg1) = sub_4dd430",
	"004dda36  int32_t result = sub_4a83c0(2, &var_5c)",
	"004dda3e  data_13e1844 = result",
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _aliases() -> dict[str, str]:
	aliases = json.loads(_read(SYMBOL_ALIASES))
	if "quakelive_steam_srp" in aliases:
		return aliases["quakelive_steam_srp"]
	return aliases["quakelive_steam"]


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


def test_botlib_import_callback_surface_aliases_rows_and_hlil_are_pinned() -> None:
	aliases = _aliases()
	rows = _function_rows()
	hlil = _read(QL_STEAM_HLIL_PART04)

	for address, (name, size) in EXPECTED_IMPORT_CALLBACK_ROWS.items():
		assert aliases[f"sub_{address}"] == name
		if size is None:
			assert address not in rows
		else:
			assert rows[address] == f"FUN_00{address.lower()},00{address.lower()},{size},0,unknown"

	for anchor in EXPECTED_RETAIL_IMPORT_LOCALS:
		assert anchor in hlil

	assert hlil.index("004dda13  int32_t (* var_18)() = sub_4dd450") < hlil.index(
		"004dda1a  int32_t (* var_14)(int32_t arg1) = sub_4dd430"
	)
	assert hlil.index("004dda1a  int32_t (* var_14)(int32_t arg1) = sub_4dd430") < hlil.index(
		"004dda21  int32_t (* var_10)(int32_t arg1, float* arg2, float* arg3, int32_t arg4) = sub_4dd480"
	)
	assert hlil.index("004dda28  int32_t (* var_c)(int32_t arg1, int32_t arg2, int32_t* arg3) = sub_4dd3b0") < hlil.index(
		"004dda2f  int32_t (* var_8)(int32_t arg1) = sub_4dd430"
	)


def test_botlib_import_callback_surface_source_layout_matches_retail_order() -> None:
	botlib_h = _read(BOTLIB_H)
	sv_bot = _read(SERVER_SV_BOT)
	import_decl = _extract_function_block(botlib_h, "typedef struct botlib_import_s")
	init_botlib = _extract_function_block(sv_bot, "void SV_BotInitBotLib")
	debug_line_delete = _extract_function_block(sv_bot, "void BotImport_DebugLineDelete")

	last_field_pos = -1
	last_init_pos = -1
	for field, target in EXPECTED_SOURCE_IMPORT_ORDER:
		field_anchor = f"(*{field})"
		if field == "Print":
			field_anchor = "(QDECL *Print)"
		assert field_anchor in import_decl
		field_pos = import_decl.index(field_anchor)
		assert field_pos > last_field_pos
		last_field_pos = field_pos

		init_anchor = f"botlib_import.{field} = {target};"
		assert init_anchor in init_botlib
		init_pos = init_botlib.index(init_anchor)
		assert init_pos > last_init_pos
		last_init_pos = init_pos

	assert "botlib_import.DebugLineDelete = BotImport_DebugLineDelete;" not in init_botlib
	assert "BotImport_DebugPolygonDelete(line);" in debug_line_delete
	assert "botlib_export = (botlib_export_t *)GetBotLibAPI( BOTLIB_API_VERSION, &botlib_import );" in init_botlib
	assert "assert(botlib_export);" in init_botlib


def test_botlib_import_callback_surface_source_bodies_match_retail_contracts() -> None:
	sv_bot = _read(SERVER_SV_BOT)
	trace = _extract_function_block(
		sv_bot,
		"void BotImport_Trace(bsp_trace_t *bsptrace, vec3_t start, vec3_t mins, vec3_t maxs, vec3_t end, int passent, int contentmask)",
	)
	entity_trace = _extract_function_block(
		sv_bot,
		"void BotImport_EntityTrace(bsp_trace_t *bsptrace, vec3_t start, vec3_t mins, vec3_t maxs, vec3_t end, int entnum, int contentmask)",
	)
	bsp_entity_data = _extract_function_block(sv_bot, "char *BotImport_BSPEntityData")
	bsp_model_bounds = _extract_function_block(sv_bot, "void BotImport_BSPModelMinsMaxsOrigin")
	hunk_alloc = _extract_function_block(sv_bot, "void *BotImport_HunkAlloc")
	debug_polygon_create = _extract_function_block(sv_bot, "int BotImport_DebugPolygonCreate")
	debug_line_create = _extract_function_block(sv_bot, "int BotImport_DebugLineCreate")
	debug_line_show = _extract_function_block(sv_bot, "void BotImport_DebugLineShow")

	for trace_block, trace_call in (
		(trace, "SV_Trace(&trace, start, mins, maxs, end, passent, contentmask, qfalse);"),
		(entity_trace, "SV_ClipToEntity(&trace, start, mins, maxs, end, entnum, contentmask, qfalse);"),
	):
		assert trace_call in trace_block
		for copy_anchor in (
			"bsptrace->allsolid = trace.allsolid;",
			"bsptrace->startsolid = trace.startsolid;",
			"bsptrace->fraction = trace.fraction;",
			"VectorCopy(trace.endpos, bsptrace->endpos);",
			"bsptrace->plane.dist = trace.plane.dist;",
			"VectorCopy(trace.plane.normal, bsptrace->plane.normal);",
			"bsptrace->plane.signbits = trace.plane.signbits;",
			"bsptrace->plane.type = trace.plane.type;",
			"bsptrace->surface.value = trace.surfaceFlags;",
			"bsptrace->ent = trace.entityNum;",
			"bsptrace->exp_dist = 0;",
			"bsptrace->sidenum = 0;",
			"bsptrace->contents = 0;",
		):
			assert copy_anchor in trace_block

	assert "return CM_EntityString();" in bsp_entity_data
	for bounds_anchor in (
		"h = CM_InlineModel(modelnum);",
		"CM_ModelBounds(h, mins, maxs);",
		"if ((angles[0] || angles[1] || angles[2])) {",
		"max = RadiusFromBounds(mins, maxs);",
		"if (outmins) VectorCopy(mins, outmins);",
		"if (outmaxs) VectorCopy(maxs, outmaxs);",
		"if (origin) VectorClear(origin);",
	):
		assert bounds_anchor in bsp_model_bounds

	assert 'Com_Error( ERR_DROP, "SV_Bot_HunkAlloc: Alloc with marks already set\\n" );' in hunk_alloc
	assert "return Hunk_Alloc( size, h_high );" in hunk_alloc

	for polygon_anchor in (
		"if (!debugpolygons)",
		"for (i = 1; i < bot_maxdebugpolys; i++)",
		"if (i >= bot_maxdebugpolys)",
		"poly->inuse = qtrue;",
		"poly->color = color;",
		"poly->numPoints = numPoints;",
		"Com_Memcpy(poly->points, points, numPoints * sizeof(vec3_t));",
	):
		assert polygon_anchor in debug_polygon_create

	assert "return BotImport_DebugPolygonCreate(0, 0, points);" in debug_line_create
	for line_show_anchor in (
		"VectorSubtract(end, start, dir);",
		"VectorNormalize(dir);",
		"dot = DotProduct(dir, up);",
		"if (dot > 0.99 || dot < -0.99) VectorSet(cross, 1, 0, 0);",
		"else CrossProduct(dir, up, cross);",
		"VectorMA(points[0], 2, cross, points[0]);",
		"VectorMA(points[1], -2, cross, points[1]);",
		"VectorMA(points[2], -2, cross, points[2]);",
		"VectorMA(points[3], 2, cross, points[3]);",
		"BotImport_DebugPolygonShow(line, color, 4, points);",
	):
		assert line_show_anchor in debug_line_show
