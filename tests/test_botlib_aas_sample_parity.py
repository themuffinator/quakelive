from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

BOTLIB_AAS_SAMPLE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_sample.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
GAME_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
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


def test_aas_sample_aliases_and_ghidra_rows_match_retail() -> None:
	aliases = _aliases()
	functions_csv = _read(QL_STEAM_FUNCTIONS)
	hlil = _read(QL_STEAM_HLIL_PART03)

	expected_aliases = {
		"495270": "AAS_PresenceTypeBoundingBox",
		"495350": "AAS_InitAASLinkHeap",
		"495420": "AAS_FreeAASLinkHeap",
		"495450": "AAS_InitAASLinkedEntities",
		"495490": "AAS_FreeAASLinkedEntities",
		"4954B0": "AAS_PointAreaNum",
		"495540": "AAS_PointReachabilityAreaIndex",
		"495670": "AAS_AreaPresenceType",
		"4956C0": "AAS_PointPresenceType",
		"495700": "AAS_AreaEntityCollision",
		"4957F0": "AAS_TraceClientBBox",
		"495F40": "AAS_TraceAreas",
		"4962F0": "AAS_InsideFace",
		"496460": "AAS_BoxOnPlaneSide2",
		"496550": "AAS_UnlinkFromAreas",
		"4965C0": "AAS_AASLinkEntity",
		"496760": "AAS_LinkEntityClientBBox",
		"4967E0": "AAS_BBoxAreas",
		"496830": "AAS_AreaInfo",
		"496920": "AAS_PlaneFromNum",
	}
	expected_sizes = {
		"495270": 214,
		"495350": 207,
		"495420": 35,
		"495450": 54,
		"495490": 29,
		"4954B0": 136,
		"495540": 296,
		"495670": 68,
		"4956C0": 60,
		"495700": 231,
		"4957F0": 1858,
		"495F40": 940,
		"4962F0": 355,
		"496460": 226,
		"496550": 112,
		"4965C0": 415,
		"496760": 125,
		"4967E0": 72,
		"496830": 229,
		"496920": 33,
	}

	for address, name in expected_aliases.items():
		assert aliases[f"sub_{address}"] == name
		assert f"00{address.lower()}    " in hlil
		assert f"sub_{address.lower()}" in hlil
		_assert_function_row(functions_csv, address, expected_sizes[address])

	for evidence in (
		"AAS_PresenceTypeBoundingBox: unk",
		"AAS_AreaPresenceType: invalid ar",
		"AAS_TraceBoundingBox: stack over",
		"AAS_TraceAreas: stack overflow\\n",
		"AAS_LinkEntity: aas not loaded\\n",
		"AAS_LinkEntity: stack overflow\\n",
		"AAS_AreaInfo: areanum %d out of ",
	):
		assert evidence in hlil


def test_aas_sample_heap_presence_and_point_queries_match_retail_shape() -> None:
	source = _read(BOTLIB_AAS_SAMPLE)

	presence_bbox = _extract_function_block(
		source,
		"void AAS_PresenceTypeBoundingBox(int presencetype, vec3_t mins, vec3_t maxs)",
	)
	init_heap = _extract_function_block(source, "void AAS_InitAASLinkHeap(void)")
	free_heap = _extract_function_block(source, "void AAS_FreeAASLinkHeap(void)")
	init_entities = _extract_function_block(source, "void AAS_InitAASLinkedEntities(void)")
	free_entities = _extract_function_block(source, "void AAS_FreeAASLinkedEntities(void)")
	point_area = _extract_function_block(source, "int AAS_PointAreaNum(vec3_t point)")
	reach_index = _extract_function_block(source, "int AAS_PointReachabilityAreaIndex( vec3_t origin )")
	area_presence = _extract_function_block(source, "int AAS_AreaPresenceType(int areanum)")
	point_presence = _extract_function_block(source, "int AAS_PointPresenceType(vec3_t point)")

	assert "vec3_t boxmins[3] = {{0, 0, 0}, {-15, -15, -24}, {-15, -15, -24}};" in presence_bbox
	assert "vec3_t boxmaxs[3] = {{0, 0, 0}, { 15,  15,  32}, { 15,  15,   8}};" in presence_bbox
	assert "if (presencetype == PRESENCE_NORMAL) index = 1;" in presence_bbox
	assert "else if (presencetype == PRESENCE_CROUCH) index = 2;" in presence_bbox
	assert 'botimport.Print(PRT_FATAL, "AAS_PresenceTypeBoundingBox: unknown presence type\\n");' in presence_bbox
	assert "VectorCopy(boxmins[index], mins);" in presence_bbox
	assert "VectorCopy(boxmaxs[index], maxs);" in presence_bbox

	assert "max_aaslinks = aasworld.linkheapsize;" in init_heap
	assert 'max_aaslinks = (int) LibVarValue("max_aaslinks", "6144");' in init_heap
	assert "aasworld.linkheap = (aas_link_t *) GetHunkMemory(max_aaslinks * sizeof(aas_link_t));" in init_heap
	assert "aasworld.linkheap[0].prev_ent = NULL;" in init_heap
	assert "aasworld.freelinks = &aasworld.linkheap[0];" in init_heap
	assert "numaaslinks = max_aaslinks;" in init_heap
	assert "if (aasworld.linkheap) FreeMemory(aasworld.linkheap);" in free_heap
	assert "aasworld.linkheapsize = 0;" in free_heap
	assert "if (!aasworld.loaded) return;" in init_entities
	assert "aasworld.numareas * sizeof(aas_link_t *)" in init_entities
	assert "if (aasworld.arealinkedentities) FreeMemory(aasworld.arealinkedentities);" in free_entities
	assert "aasworld.arealinkedentities = NULL;" in free_entities

	assert "nodenum = 1;" in point_area
	assert "dist = DotProduct(point, plane->normal) - plane->dist;" in point_area
	assert "return -nodenum;" in point_area
	assert "if ( !origin )" in reach_index
	assert "index += aasworld.clusters[i].numreachabilityareas;" in reach_index
	assert "if ( !areanum || !AAS_AreaReachability(areanum) )" in reach_index
	assert "cluster = aasworld.portals[-cluster].frontcluster;" in reach_index
	assert "return aasworld.areasettings[areanum].presencetype;" in area_presence
	assert 'botimport.Print(PRT_ERROR, "AAS_AreaPresenceType: invalid area number\\n");' in area_presence
	assert "areanum = AAS_PointAreaNum(point);" in point_presence
	assert "if (!areanum) return PRESENCE_NONE;" in point_presence
	assert "return aasworld.areasettings[areanum].presencetype;" in point_presence


def test_aas_sample_collision_trace_and_link_helpers_match_retail_shape() -> None:
	source = _read(BOTLIB_AAS_SAMPLE)

	area_collision = _extract_function_block(source, "qboolean AAS_AreaEntityCollision(int areanum")
	trace_bbox = _extract_function_block(source, "aas_trace_t AAS_TraceClientBBox(vec3_t start")
	trace_areas = _extract_function_block(source, "int AAS_TraceAreas(vec3_t start")
	inside_face = _extract_function_block(source, "qboolean AAS_InsideFace(aas_face_t *face")
	box_side = _extract_function_block(source, "int AAS_BoxOnPlaneSide2(vec3_t absmins")
	unlink = _extract_function_block(source, "void AAS_UnlinkFromAreas(aas_link_t *areas)")
	link_entity = _extract_function_block(source, "aas_link_t *AAS_AASLinkEntity(vec3_t absmins")
	client_bbox = _extract_function_block(source, "aas_link_t *AAS_LinkEntityClientBBox(vec3_t absmins")
	bbox_areas = _extract_function_block(source, "int AAS_BBoxAreas(vec3_t absmins")
	area_info = _extract_function_block(source, "int AAS_AreaInfo( int areanum")
	plane_from_num = _extract_function_block(source, "aas_plane_t *AAS_PlaneFromNum(int planenum)")

	assert "AAS_PresenceTypeBoundingBox(presencetype, boxmins, boxmaxs);" in area_collision
	assert "for (link = aasworld.arealinkedentities[areanum]; link; link = link->next_ent)" in area_collision
	assert "if (link->entnum == passent) continue;" in area_collision
	assert "CONTENTS_SOLID|CONTENTS_PLAYERCLIP" in area_collision
	assert "trace->startsolid = bsptrace.startsolid;" in area_collision
	assert "trace->ent = bsptrace.ent;" in area_collision
	assert "trace->area = 0;" in area_collision

	assert "aas_tracestack_t tracestack[127];" in trace_bbox
	assert "tstack_p->nodenum = 1;" in trace_bbox
	assert "if (!(aasworld.areasettings[-nodenum].presencetype & presencetype))" in trace_bbox
	assert "AAS_AreaEntityCollision(-nodenum, tstack_p->start," in trace_bbox
	assert "TRACEPLANE_EPSILON" in trace_bbox
	assert 'botimport.Print(PRT_ERROR, "AAS_TraceBoundingBox: stack overflow\\n");' in trace_bbox

	assert "areas[0] = 0;" in trace_areas
	assert "areas[numareas] = -nodenum;" in trace_areas
	assert "if (points) VectorCopy(tstack_p->start, points[numareas]);" in trace_areas
	assert 'botimport.Print(PRT_ERROR, "AAS_TraceAreas: stack overflow\\n");' in trace_areas

	assert "AAS_OrthogonalToVectors(edgevec, pnormal, sepnormal);" in inside_face
	assert "if (DotProduct(pointvec, sepnormal) < -epsilon) return qfalse;" in inside_face
	assert "vec3_t corners[2];" in box_side
	assert "dist1 = DotProduct(p->normal, corners[0]) - p->dist;" in box_side
	assert "if (dist1 >= 0) sides = 1;" in box_side
	assert "if (dist2 < 0) sides |= 2;" in box_side

	assert "if (link->prev_ent) link->prev_ent->next_ent = link->next_ent;" in unlink
	assert "AAS_DeAllocAASLink(link);" in unlink
	assert "aas_linkstack_t linkstack[128];" in link_entity
	assert 'botimport.Print(PRT_ERROR, "AAS_LinkEntity: aas not loaded\\n");' in link_entity
	assert "side = AAS_BoxOnPlaneSide2(absmins, absmaxs, plane);" in link_entity
	assert "link = AAS_AllocAASLink();" in link_entity
	assert "aasworld.arealinkedentities[-nodenum] = link;" in link_entity
	assert 'botimport.Print(PRT_ERROR, "AAS_LinkEntity: stack overflow\\n");' in link_entity

	assert "AAS_PresenceTypeBoundingBox(presencetype, mins, maxs);" in client_bbox
	assert "VectorSubtract(absmins, maxs, newabsmins);" in client_bbox
	assert "return AAS_AASLinkEntity(newabsmins, newabsmaxs, entnum);" in client_bbox
	assert "linkedareas = AAS_AASLinkEntity(absmins, absmaxs, -1);" in bbox_areas
	assert "areas[num] = link->areanum;" in bbox_areas
	assert "AAS_UnlinkFromAreas(linkedareas);" in bbox_areas

	assert "if (!info)" in area_info
	assert 'botimport.Print(PRT_ERROR, "AAS_AreaInfo: areanum %d out of range\\n", areanum);' in area_info
	assert "info->cluster = settings->cluster;" in area_info
	assert "info->presencetype = settings->presencetype;" in area_info
	assert "VectorCopy(aasworld.areas[areanum].center, info->center);" in area_info
	assert "return sizeof(aas_areainfo_t);" in area_info
	assert "if (!aasworld.loaded) return 0;" in plane_from_num
	assert "return &aasworld.planes[planenum];" in plane_from_num


def test_aas_sample_public_export_and_vm_syscall_wiring_match_retail_shape() -> None:
	botlib_h = _read(BOTLIB_PUBLIC)
	interface = _read(BOTLIB_INTERFACE)
	server = _read(SERVER_GAME)
	server_imports = _read(SERVER_QL_GAME_IMPORTS)
	g_syscalls = _read(GAME_SYSCALLS)
	g_public = _read(GAME_PUBLIC)

	_assert_order(
		botlib_h,
		"void\t\t(*AAS_EntityInfo)(int entnum, struct aas_entityinfo_s *info);",
		"int\t\t\t(*AAS_Initialized)(void);",
		"void\t\t(*AAS_PresenceTypeBoundingBox)(int presencetype, vec3_t mins, vec3_t maxs);",
		"float\t\t(*AAS_Time)(void);",
		"int\t\t\t(*AAS_PointAreaNum)(vec3_t point);",
		"int\t\t\t(*AAS_PointReachabilityAreaIndex)( vec3_t point );",
		"int\t\t\t(*AAS_TraceAreas)(vec3_t start, vec3_t end, int *areas, vec3_t *points, int maxareas);",
		"int\t\t\t(*AAS_BBoxAreas)(vec3_t absmins, vec3_t absmaxs, int *areas, int maxareas);",
		"int\t\t\t(*AAS_AreaInfo)( int areanum, struct aas_areainfo_s *info );",
		"int\t\t\t(*AAS_PointContents)(vec3_t point);",
	)
	_assert_order(
		interface,
		"aas->AAS_EntityInfo = AAS_EntityInfo;",
		"aas->AAS_Initialized = AAS_Initialized;",
		"aas->AAS_PresenceTypeBoundingBox = AAS_PresenceTypeBoundingBox;",
		"aas->AAS_Time = AAS_Time;",
		"aas->AAS_PointAreaNum = AAS_PointAreaNum;",
		"aas->AAS_PointReachabilityAreaIndex = AAS_PointReachabilityAreaIndex;",
		"aas->AAS_TraceAreas = AAS_TraceAreas;",
		"aas->AAS_BBoxAreas = AAS_BBoxAreas;",
		"aas->AAS_AreaInfo = AAS_AreaInfo;",
		"aas->AAS_PointContents = AAS_PointContents;",
	)

	for expected in (
		"case BOTLIB_AAS_BBOX_AREAS:\n\t\treturn botlib_export->aas.AAS_BBoxAreas( VMA(1), VMA(2), VMA(3), args[4] );",
		"case BOTLIB_AAS_AREA_INFO:\n\t\treturn botlib_export->aas.AAS_AreaInfo( args[1], VMA(2) );",
		"case BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX:\n\t\tbotlib_export->aas.AAS_PresenceTypeBoundingBox( args[1], VMA(2), VMA(3) );",
		"case BOTLIB_AAS_POINT_AREA_NUM:\n\t\treturn botlib_export->aas.AAS_PointAreaNum( VMA(1) );",
		"case BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX:\n\t\treturn botlib_export->aas.AAS_PointReachabilityAreaIndex( VMA(1) );",
		"case BOTLIB_AAS_TRACE_AREAS:\n\t\treturn botlib_export->aas.AAS_TraceAreas( VMA(1), VMA(2), VMA(3), VMA(4), args[5] );",
	):
		assert expected in server

	_assert_order(
		server,
		"[BOTLIB_AAS_POINT_AREA_NUM] = (ql_import_f)QL_G_trap_AAS_PointAreaNum,",
		"[BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX] = (ql_import_f)QL_G_trap_AAS_PointReachabilityAreaIndex,",
		"[BOTLIB_AAS_TRACE_AREAS] = (ql_import_f)QL_G_trap_AAS_TraceAreas,",
		"[BOTLIB_AAS_BBOX_AREAS] = (ql_import_f)QL_G_trap_AAS_BBoxAreas,",
		"[BOTLIB_AAS_AREA_INFO] = (ql_import_f)QL_G_trap_AAS_AreaInfo,",
	)
	_assert_order(
		server,
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_BBOX_AREAS] = (ql_import_f)QL_G_trap_AAS_BBoxAreas;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_AREA_INFO] = (ql_import_f)QL_G_trap_AAS_AreaInfo;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_ENTITY_INFO] = (ql_import_f)QL_G_trap_AAS_EntityInfo;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_INITIALIZED] = (ql_import_f)QL_G_trap_AAS_Initialized;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX] = (ql_import_f)QL_G_trap_AAS_PresenceTypeBoundingBox;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_TIME] = (ql_import_f)QL_G_trap_AAS_Time;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM] = (ql_import_f)QL_G_trap_AAS_PointAreaNum;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX] = (ql_import_f)QL_G_trap_AAS_PointReachabilityAreaIndex;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS] = (ql_import_f)QL_G_trap_AAS_TraceAreas;",
	)

	for expected in (
		"G_QL_IMPORT_BOTLIB_AAS_BBOX_AREAS = 61,",
		"G_QL_IMPORT_BOTLIB_AAS_AREA_INFO = 62,",
		"G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM = 67,",
		"G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS = 69,",
	):
		assert expected in g_public

	for expected in (
		"static int QDECL QL_G_trap_AAS_PointAreaNum( vec3_t point ) {\n\treturn G_Import_Syscall( BOTLIB_AAS_POINT_AREA_NUM, point );\n}",
		"static int QDECL QL_G_trap_AAS_TraceAreas( vec3_t start, vec3_t end, int *areas, vec3_t *points, int maxareas ) {\n\treturn G_Import_Syscall( BOTLIB_AAS_TRACE_AREAS, start, end, areas, points, maxareas );\n}",
		"static int QDECL QL_G_trap_AAS_BBoxAreas( vec3_t absmins, vec3_t absmaxs, int *areas, int maxareas ) {\n\treturn G_Import_Syscall( BOTLIB_AAS_BBOX_AREAS, absmins, absmaxs, areas, maxareas );\n}",
		"static int QDECL QL_G_trap_AAS_AreaInfo( int areanum, void /* struct aas_areainfo_s */ *info ) {\n\treturn G_Import_Syscall( BOTLIB_AAS_AREA_INFO, areanum, info );\n}",
	):
		assert expected in server_imports

	for expected in (
		"case BOTLIB_AAS_BBOX_AREAS: return G_QL_IMPORT_BOTLIB_AAS_BBOX_AREAS;",
		"case BOTLIB_AAS_AREA_INFO: return G_QL_IMPORT_BOTLIB_AAS_AREA_INFO;",
		"case BOTLIB_AAS_POINT_AREA_NUM: return G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM;",
		"case BOTLIB_AAS_TRACE_AREAS: return G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS;",
		"int trap_AAS_PointAreaNum(vec3_t point) {\n\treturn syscall( BOTLIB_AAS_POINT_AREA_NUM, point );\n}",
		"int trap_AAS_TraceAreas(vec3_t start, vec3_t end, int *areas, vec3_t *points, int maxareas) {\n\treturn syscall( BOTLIB_AAS_TRACE_AREAS, start, end, areas, points, maxareas );\n}",
		"int trap_AAS_BBoxAreas(vec3_t absmins, vec3_t absmaxs, int *areas, int maxareas) {\n\treturn syscall( BOTLIB_AAS_BBOX_AREAS, absmins, absmaxs, areas, maxareas );\n}",
		"int trap_AAS_AreaInfo( int areanum, void /* struct aas_areainfo_s */ *info ) {\n\treturn syscall( BOTLIB_AAS_AREA_INFO, areanum, info );\n}",
	):
		assert expected in g_syscalls
