from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

BOTLIB_AAS_BSPQ3 = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_bspq3.c"
BOTLIB_AAS_CLUSTER = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_cluster.c"
BOTLIB_AAS_ENTITY = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_entity.c"
BOTLIB_AAS_FILE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_file.c"
BOTLIB_AAS_MAIN = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_main.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
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


def test_aas_lifecycle_aliases_and_retail_function_rows_are_pinned() -> None:
	aliases = _aliases()
	functions = _read(QL_STEAM_FUNCTIONS)
	hlil = _read(QL_STEAM_HLIL_PART03)

	expected_aliases = {
		"4829C0": "AAS_Trace",
		"4829F0": "AAS_PointContents",
		"482A00": "AAS_EntityCollision",
		"482A90": "AAS_inPVS",
		"482AA0": "AAS_BSPModelMinsMaxsOrigin",
		"482AB0": "AAS_NextBSPEntity",
		"482AD0": "AAS_ValueForBSPEpairKey",
		"482B70": "AAS_VectorForBSPEpairKey",
		"482C30": "AAS_FloatForBSPEpairKey",
		"482CA0": "AAS_IntForBSPEpairKey",
		"482D20": "AAS_FreeBSPEntities",
		"482D90": "AAS_ParseBSPEntities",
		"4830C0": "AAS_DumpBSPData",
		"483110": "AAS_LoadBSPFile",
		"4831B0": "AAS_UpdatePortal",
		"4832C0": "AAS_FloodClusterAreas_r",
		"4837C0": "AAS_FindClusters",
		"4838D0": "AAS_CreatePortals",
		"4841D0": "AAS_InitClustering",
		"4851B0": "AAS_EntityInfo",
		"485230": "AAS_EntityModelindex",
		"485270": "AAS_EntityType",
		"4852C0": "AAS_EntityModelNum",
		"485310": "AAS_OriginOfMoverWithModelNum",
		"485370": "AAS_ResetEntityLinks",
		"4853B0": "AAS_InvalidateEntities",
		"4853F0": "AAS_UnlinkInvalidEntities",
		"485450": "AAS_NextEntity",
		"4854A0": "AAS_SwapAASData",
		"485600": "AAS_DumpAASData",
		"4857D0": "AAS_LoadAASLump",
		"485860": "AAS_LoadAASFile",
		"485D90": "AAS_WriteAASLump",
		"485DD0": "AAS_WriteAASFile",
		"486210": "AAS_ContinueInit",
		"4862E0": "AAS_StartFrame",
		"4864C0": "AAS_LoadFiles",
		"486550": "AAS_LoadMap",
		"4865B0": "AAS_Setup",
		"486640": "AAS_Shutdown",
	}
	expected_sizes = {
		"4829C0": 46,
		"4829F0": 10,
		"482A00": 130,
		"482A90": 10,
		"482AA0": 10,
		"482AB0": 24,
		"482AD0": 159,
		"482B70": 188,
		"482C30": 112,
		"482CA0": 114,
		"482D20": 101,
		"482D90": 797,
		"4830C0": 74,
		"483110": 157,
		"4831B0": 257,
		"4832C0": 378,
		"4837C0": 264,
		"4838D0": 113,
		"4841D0": 667,
		"4851B0": 128,
		"485230": 57,
		"485270": 66,
		"4852C0": 66,
		"485310": 82,
		"485370": 58,
		"4853B0": 54,
		"4853F0": 96,
		"485450": 68,
		"4854A0": 345,
		"485600": 449,
		"4857D0": 139,
		"485860": 1321,
		"485D90": 63,
		"485DD0": 970,
		"486210": 200,
		"4862E0": 276,
		"4864C0": 139,
		"486550": 82,
		"4865B0": 134,
		"486640": 92,
	}

	for address, name in expected_aliases.items():
		assert aliases[f"sub_{address}"] == name
		_assert_function_row(functions, address, expected_sizes[address])

	for evidence in (
		"004829c0    int32_t sub_4829c0",
		"00482a00    int32_t sub_482a00",
		"00482d20    void sub_482d20()",
		"00482d90    int32_t* sub_482d90()",
		"00483110    int32_t sub_483110()",
		"004831b0    int32_t sub_4831b0",
		"004837c0    int32_t sub_4837c0()",
		"004841d0    void sub_4841d0()",
		"00485230    int32_t sub_485230",
		"00485310    int32_t sub_485310",
		"00485450    int32_t sub_485450",
		"004854a0    int32_t sub_4854a0()",
		"004857d0    char* sub_4857d0",
		"00485860    int32_t sub_485860",
		"00485d90    int32_t sub_485d90",
		"00485dd0    int32_t sub_485dd0",
		"00486210    void sub_486210",
		"00486550    int32_t sub_486550",
		"00486640    int32_t sub_486640()",
		"too many entities in BSP file\\n",
		"AAS file not sequentially read\\n",
		"trying to load %s\\n",
		"AAS initialized.\\n",
		"AAS shutdown.\\n",
	):
		assert evidence in hlil


def test_aas_bsp_entity_parser_and_import_wrappers_match_retail_shape() -> None:
	source = _read(BOTLIB_AAS_BSPQ3)

	aas_trace = _extract_function_block(source, "bsp_trace_t AAS_Trace(vec3_t start")
	entity_collision = _extract_function_block(source, "qboolean AAS_EntityCollision(int entnum")
	in_pvs = _extract_function_block(source, "qboolean AAS_inPVS(vec3_t p1, vec3_t p2)")
	in_phs = _extract_function_block(source, "qboolean AAS_inPHS(vec3_t p1, vec3_t p2)")
	bsp_model = _extract_function_block(source, "void AAS_BSPModelMinsMaxsOrigin(int modelnum")
	next_bsp = _extract_function_block(source, "int AAS_NextBSPEntity(int ent)")
	bsp_range = _extract_function_block(source, "int AAS_BSPEntityInRange(int ent)")
	value_key = _extract_function_block(source, "int AAS_ValueForBSPEpairKey(int ent")
	vector_key = _extract_function_block(source, "int AAS_VectorForBSPEpairKey(int ent")
	float_key = _extract_function_block(source, "int AAS_FloatForBSPEpairKey(int ent")
	int_key = _extract_function_block(source, "int AAS_IntForBSPEpairKey(int ent")
	free_bsp = _extract_function_block(source, "void AAS_FreeBSPEntities(void)")
	parse_bsp = _extract_function_block(source, "void AAS_ParseBSPEntities(void)")
	dump_bsp = _extract_function_block(source, "void AAS_DumpBSPData(void)")
	load_bsp = _extract_function_block(source, "int AAS_LoadBSPFile(void)")

	assert "botimport.Trace(&bsptrace, start, mins, maxs, end, passent, contentmask);" in aas_trace
	assert "return bsptrace;" in aas_trace
	assert "botimport.EntityTrace(&enttrace, start, boxmins, boxmaxs, end, entnum, contentmask);" in entity_collision
	assert "if (enttrace.fraction < trace->fraction)" in entity_collision
	assert "Com_Memcpy(trace, &enttrace, sizeof(bsp_trace_t));" in entity_collision
	assert "return botimport.inPVS(p1, p2);" in in_pvs
	assert "return qtrue;" in in_phs
	assert "botimport.BSPModelMinsMaxsOrigin(modelnum, angles, mins, maxs, origin);" in bsp_model

	assert "ent++;" in next_bsp
	assert "if (ent >= 1 && ent < bspworld.numentities) return ent;" in next_bsp
	assert 'botimport.Print(PRT_MESSAGE, "bsp entity out of range\\n");' in bsp_range
	assert "value[0] = '\\0';" in value_key
	assert "if (!AAS_BSPEntityInRange(ent)) return qfalse;" in value_key
	assert "for (epair = bspworld.entities[ent].epairs; epair; epair = epair->next)" in value_key
	assert "strncpy(value, epair->value, size-1);" in value_key
	assert "value[size-1] = '\\0';" in value_key
	assert "sscanf(buf, \"%lf %lf %lf\", &v1, &v2, &v3);" in vector_key
	assert "*value = atof(buf);" in float_key
	assert "*value = atoi(buf);" in int_key

	assert "for (i = 1; i < bspworld.numentities; i++)" in free_bsp
	assert "if (epair->key) FreeMemory(epair->key);" in free_bsp
	assert "if (epair->value) FreeMemory(epair->value);" in free_bsp
	assert "FreeMemory(epair);" in free_bsp
	assert "bspworld.numentities = 0;" in free_bsp
	assert 'script = LoadScriptMemory(bspworld.dentdata, bspworld.entdatasize, "entdata");' in parse_bsp
	assert "SetScriptFlags(script, SCFL_NOSTRINGWHITESPACES|SCFL_NOSTRINGESCAPECHARS);" in parse_bsp
	assert "bspworld.numentities = 1;" in parse_bsp
	assert 'botimport.Print(PRT_MESSAGE, "too many entities in BSP file\\n");' in parse_bsp
	assert "epair = (bsp_epair_t *) GetClearedHunkMemory(sizeof(bsp_epair_t));" in parse_bsp
	assert "StripDoubleQuotes(token.string);" in parse_bsp
	assert "epair->key = (char *) GetHunkMemory(strlen(token.string) + 1);" in parse_bsp
	assert "epair->value = (char *) GetHunkMemory(strlen(token.string) + 1);" in parse_bsp
	assert 'ScriptError(script, "missing }\\n");' in parse_bsp
	assert "AAS_FreeBSPEntities();" in dump_bsp
	assert "if (bspworld.dentdata) FreeMemory(bspworld.dentdata);" in dump_bsp
	assert "Com_Memset( &bspworld, 0, sizeof(bspworld) );" in dump_bsp
	assert "bspworld.entdatasize = strlen(botimport.BSPEntityData()) + 1;" in load_bsp
	assert "bspworld.dentdata = (char *) GetClearedHunkMemory(bspworld.entdatasize);" in load_bsp
	assert "Com_Memcpy(bspworld.dentdata, botimport.BSPEntityData(), bspworld.entdatasize);" in load_bsp
	assert "AAS_ParseBSPEntities();" in load_bsp


def test_aas_entity_helpers_and_consumers_match_retail_shape() -> None:
	entity = _read(BOTLIB_AAS_ENTITY)
	ai_move = _read(REPO_ROOT / "src" / "code" / "botlib" / "be_ai_move.c")
	ai_goal = _read(REPO_ROOT / "src" / "code" / "botlib" / "be_ai_goal.c")

	update_entity = _extract_function_block(entity, "int AAS_UpdateEntity(int entnum")
	model_index = _extract_function_block(entity, "int AAS_EntityModelindex(int entnum)")
	entity_type = _extract_function_block(entity, "int AAS_EntityType(int entnum)")
	model_num = _extract_function_block(entity, "int AAS_EntityModelNum(int entnum)")
	mover_origin = _extract_function_block(entity, "int AAS_OriginOfMoverWithModelNum(int modelnum")
	reset_links = _extract_function_block(entity, "void AAS_ResetEntityLinks(void)")
	invalidate = _extract_function_block(entity, "void AAS_InvalidateEntities(void)")
	unlink_invalid = _extract_function_block(entity, "void AAS_UnlinkInvalidEntities(void)")
	next_entity = _extract_function_block(entity, "int AAS_NextEntity(int entnum)")

	assert 'botimport.Print(PRT_MESSAGE, "AAS_UpdateEntity: not loaded\\n");' in update_entity
	assert "AAS_UnlinkFromAreas(ent->areas);" in update_entity
	assert "AAS_UnlinkFromBSPLeaves(ent->leaves);" in update_entity
	assert "ent->i.qlTimeSeconds = state->qlTimeSeconds;" in update_entity
	assert "Com_Memcpy(ent->i.qlPowerupsActive, state->qlPowerupsActive, sizeof(ent->i.qlPowerupsActive));" in update_entity
	assert "ent->i.qlRedBlueFlagCarrier = state->qlRedBlueFlagCarrier;" in update_entity
	assert "ent->i.number = entnum;" in update_entity
	assert "ent->i.valid = qtrue;" in update_entity
	assert "if (aasworld.numframes == 1) relink = qtrue;" in update_entity
	assert "AAS_BSPModelMinsMaxsOrigin(ent->i.modelindex, ent->i.angles, ent->i.mins, ent->i.maxs, NULL);" in update_entity
	assert "ent->areas = AAS_LinkEntityClientBBox(absmins, absmaxs, entnum, PRESENCE_NORMAL);" in update_entity
	assert "ent->leaves = AAS_BSPLinkEntity(absmins, absmaxs, entnum, 0);" in update_entity

	assert 'botimport.Print(PRT_FATAL, "AAS_EntityModelindex: entnum %d out of range\\n", entnum);' in model_index
	assert "return aasworld.entities[entnum].i.modelindex;" in model_index
	assert "if (!aasworld.initialized) return 0;" in entity_type
	assert 'botimport.Print(PRT_FATAL, "AAS_EntityType: entnum %d out of range\\n", entnum);' in entity_type
	assert "return aasworld.entities[entnum].i.type;" in entity_type
	assert "if (!aasworld.initialized) return 0;" in model_num
	assert 'botimport.Print(PRT_FATAL, "AAS_EntityModelNum: entnum %d out of range\\n", entnum);' in model_num
	assert "return aasworld.entities[entnum].i.modelindex;" in model_num
	assert "for (i = 0; i < aasworld.maxentities; i++)" in mover_origin
	assert "if (ent->i.type == ET_MOVER)" in mover_origin
	assert "if (ent->i.modelindex == modelnum)" in mover_origin
	assert "VectorCopy(ent->i.origin, origin);" in mover_origin

	assert "aasworld.entities[i].areas = NULL;" in reset_links
	assert "aasworld.entities[i].leaves = NULL;" in reset_links
	assert "aasworld.entities[i].i.valid = qfalse;" in invalidate
	assert "aasworld.entities[i].i.number = i;" in invalidate
	assert "if (!ent->i.valid)" in unlink_invalid
	assert "AAS_UnlinkFromAreas( ent->areas );" in unlink_invalid
	assert "AAS_UnlinkFromBSPLeaves( ent->leaves );" in unlink_invalid
	assert "if (!aasworld.loaded) return 0;" in next_entity
	assert "if (entnum < 0) entnum = -1;" in next_entity
	assert "while(++entnum < aasworld.maxentities)" in next_entity
	assert "if (aasworld.entities[entnum].i.valid) return entnum;" in next_entity

	assert "modelnum = AAS_EntityModelindex(bsptrace.ent);" in ai_move
	assert "if (!AAS_OriginOfMoverWithModelNum(modelnum, modelorigin))" in ai_move
	assert "if (trace.ent != ENTITYNUM_NONE && AAS_EntityModelNum(trace.ent) == modelnum)" in ai_move
	assert "for (i = AAS_NextEntity(0); i; i = AAS_NextEntity(i))" in ai_move
	assert "if (AAS_EntityType(i) == (int) entitytypemissile->value)" in ai_move
	assert "for (ent = AAS_NextEntity(0); ent; ent = AAS_NextEntity(ent))" in ai_goal
	assert "modelindex = AAS_EntityModelindex(ent);" in ai_goal
	assert "if (AAS_EntityType(ent) != ET_ITEM) continue;" in ai_goal


def test_aas_file_main_and_cluster_lifecycle_match_retail_shape() -> None:
	aas_file = _read(BOTLIB_AAS_FILE)
	aas_main = _read(BOTLIB_AAS_MAIN)
	cluster = _read(BOTLIB_AAS_CLUSTER)

	swap_data = _extract_function_block(aas_file, "void AAS_SwapAASData(void)")
	dump_data = _extract_function_block(aas_file, "void AAS_DumpAASData(void)")
	load_lump = _extract_function_block(aas_file, "char *AAS_LoadAASLump(fileHandle_t fp")
	dd_data = _extract_function_block(aas_file, "void AAS_DData(unsigned char *data, int size)")
	load_file = _extract_function_block(aas_file, "int AAS_LoadAASFile(char *filename)")
	write_lump = _extract_function_block(aas_file, "int AAS_WriteAASLump(fileHandle_t fp")
	write_file = _extract_function_block(aas_file, "qboolean AAS_WriteAASFile(char *filename)")
	continue_init = _extract_function_block(aas_main, "void AAS_ContinueInit(float time)")
	start_frame = _extract_function_block(aas_main, "int AAS_StartFrame(float time)")
	load_files = _extract_function_block(aas_main, "int AAS_LoadFiles(const char *mapname)")
	load_map = _extract_function_block(aas_main, "int AAS_LoadMap(const char *mapname)")
	setup = _extract_function_block(aas_main, "int AAS_Setup(void)")
	shutdown = _extract_function_block(aas_main, "void AAS_Shutdown(void)")
	init_clustering = _extract_function_block(cluster, "void AAS_InitClustering(void)")

	for expected in (
		"aasworld.bboxes[i].presencetype = LittleLong(aasworld.bboxes[i].presencetype);",
		"aasworld.vertexes[i][j] = LittleFloat(aasworld.vertexes[i][j]);",
		"aasworld.planes[i].dist = LittleFloat(aasworld.planes[i].dist);",
		"aasworld.faces[i].frontarea = LittleLong(aasworld.faces[i].frontarea);",
		"aasworld.reachability[i].traveltype = LittleLong(aasworld.reachability[i].traveltype);",
		"aasworld.reachability[i].traveltime = LittleShort(aasworld.reachability[i].traveltime);",
		"aasworld.portals[i].clusterareanum[1] = LittleLong(aasworld.portals[i].clusterareanum[1]);",
		"aasworld.clusters[i].firstportal = LittleLong(aasworld.clusters[i].firstportal);",
	):
		assert expected in swap_data

	for expected in (
		"aasworld.numbboxes = 0;",
		"if (aasworld.bboxes) FreeMemory(aasworld.bboxes);",
		"if (aasworld.reachability) FreeMemory(aasworld.reachability);",
		"if (aasworld.portalindex) FreeMemory(aasworld.portalindex);",
		"if (aasworld.clusters) FreeMemory(aasworld.clusters);",
		"aasworld.loaded = qfalse;",
		"aasworld.initialized = qfalse;",
		"aasworld.savefile = qfalse;",
	):
		assert expected in dump_data

	assert "if (!length)" in load_lump
	assert "return (char *) GetClearedHunkMemory(size+1);" in load_lump
	assert 'botimport.Print(PRT_WARNING, "AAS file not sequentially read\\n");' in load_lump
	assert "if (botimport.FS_Seek(fp, offset, FS_SEEK_SET))" in load_lump
	assert 'AAS_Error("can\'t seek to aas lump\\n");' in load_lump
	assert "buf = (char *) GetClearedHunkMemory(length+1);" in load_lump
	assert "botimport.FS_Read(buf, length, fp );" in load_lump
	assert "*lastoffset += length;" in load_lump
	assert "data[i] ^= (unsigned char) i * 119;" in dd_data

	assert 'botimport.Print(PRT_MESSAGE, "trying to load %s\\n", filename);' in load_file
	assert "AAS_DumpAASData();" in load_file
	assert "botimport.FS_FOpenFile( filename, &fp, FS_READ );" in load_file
	assert 'AAS_Error("can\'t open %s\\n", filename);' in load_file
	assert "if (header.ident != AASID)" in load_file
	assert 'AAS_Error("%s is not an AAS file\\n", filename);' in load_file
	assert "if (header.version != AASVERSION_OLD && header.version != AASVERSION)" in load_file
	assert 'AAS_Error("aas file %s is version %i, not %i\\n", filename, header.version, AASVERSION);' in load_file
	assert "AAS_DData((unsigned char *) &header + 8, sizeof(aas_header_t) - 8);" in load_file
	assert 'aasworld.bspchecksum = atoi(LibVarGetString( "sv_mapChecksum"));' in load_file
	assert 'AAS_Error("aas file %s is out of date\\n", filename);' in load_file
	assert "aasworld.bboxes = (aas_bbox_t *) AAS_LoadAASLump(fp, offset, length, &lastoffset, sizeof(aas_bbox_t));" in load_file
	assert "aasworld.clusters = (aas_cluster_t *) AAS_LoadAASLump(fp, offset, length, &lastoffset, sizeof(aas_cluster_t));" in load_file
	assert "AAS_SwapAASData();" in load_file
	assert "aasworld.loaded = qtrue;" in load_file
	assert "botimport.FS_FCloseFile(fp);" in load_file

	assert "lump->fileofs = LittleLong(AAS_WriteAASLump_offset);" in write_lump
	assert "lump->filelen = LittleLong(length);" in write_lump
	assert "botimport.FS_Write(data, length, fp );" in write_lump
	assert "AAS_WriteAASLump_offset += length;" in write_lump
	assert 'botimport.Print(PRT_MESSAGE, "writing %s\\n", filename);' in write_file
	assert "AAS_SwapAASData();" in write_file
	assert "header.ident = LittleLong(AASID);" in write_file
	assert "header.version = LittleLong(AASVERSION);" in write_file
	assert "botimport.FS_FOpenFile( filename, &fp, FS_WRITE );" in write_file
	assert "AAS_WriteAASLump_offset = sizeof(aas_header_t);" in write_file
	assert "AAS_WriteAASLump(fp, &header, AASLUMP_BBOXES, aasworld.bboxes," in write_file
	assert "AAS_WriteAASLump(fp, &header, AASLUMP_CLUSTERS, aasworld.clusters," in write_file
	assert "botimport.FS_Seek(fp, 0, FS_SEEK_SET);" in write_file
	assert "AAS_DData((unsigned char *) &header + 8, sizeof(aas_header_t) - 8);" in write_file

	_assert_order(
		continue_init,
		"if (AAS_ContinueInitReachability(time)) return;",
		"AAS_InitClustering();",
		"if (aasworld.savefile || ((int)LibVarGetValue(\"forcewrite\")))",
		"if ((int)LibVarValue(\"aasoptimize\", \"0\")) AAS_Optimize();",
		"if (AAS_WriteAASFile(aasworld.filename))",
		"AAS_InitRouting();",
		"AAS_SetInitialized();",
	)
	_assert_order(
		start_frame,
		"aasworld.time = time;",
		"AAS_UnlinkInvalidEntities();",
		"AAS_InvalidateEntities();",
		"AAS_ContinueInit(time);",
		"bot_showPath = LibVarGetValue(\"bot_showPath\");",
		"if (saveroutingcache->value)",
		"AAS_WriteRouteCache();",
	)
	_assert_order(
		load_files,
		"strcpy(aasworld.mapname, mapname);",
		"AAS_ResetEntityLinks();",
		"AAS_LoadBSPFile();",
		"Com_sprintf(aasfile, MAX_PATH, \"maps/%s.aas\", mapname);",
		"errnum = AAS_LoadAASFile(aasfile);",
		"botimport.Print(PRT_MESSAGE, \"loaded %s\\n\", aasfile);",
		"strncpy(aasworld.filename, aasfile, MAX_PATH);",
	)
	_assert_order(
		load_map,
		"aasworld.initialized = qfalse;",
		"AAS_FreeRoutingCaches();",
		"errnum = AAS_LoadFiles(mapname);",
		"AAS_InitSettings();",
		"AAS_InitAASLinkHeap();",
		"AAS_InitAASLinkedEntities();",
		"AAS_InitReachability();",
		"AAS_InitAlternativeRouting();",
	)
	assert 'aasworld.maxclients = (int) LibVarValue("maxclients", "128");' in setup
	assert 'aasworld.maxentities = (int) LibVarValue("maxentities", "1024");' in setup
	assert 'saveroutingcache = LibVar("saveroutingcache", "0");' in setup
	assert "aasworld.entities = (aas_entity_t *) GetClearedHunkMemory(aasworld.maxentities * sizeof(aas_entity_t));" in setup
	assert "AAS_InvalidateEntities();" in setup
	assert "aasworld.numframes = 0;" in setup
	_assert_order(
		shutdown,
		"AAS_ShutdownAlternativeRouting();",
		"AAS_DumpBSPData();",
		"AAS_FreeRoutingCaches();",
		"AAS_FreeAASLinkHeap();",
		"AAS_FreeAASLinkedEntities();",
		"AAS_DumpAASData();",
		"if (aasworld.entities) FreeMemory(aasworld.entities);",
		"Com_Memset(&aasworld, 0, sizeof(aas_t));",
		"botimport.Print(PRT_MESSAGE, \"AAS shutdown.\\n\");",
	)

	assert "if (!aasworld.loaded) return;" in init_clustering
	assert 'LibVarGetValue("forceclustering")' in init_clustering
	assert 'LibVarGetValue("forcereachability")' in init_clustering
	assert "AAS_SetViewPortalsAsClusterPortals();" in init_clustering
	assert "AAS_CountForcedClusterPortals();" in init_clustering
	assert "AAS_FindPossiblePortals();" in init_clustering
	assert "AAS_CreateViewPortals();" in init_clustering
	assert "aasworld.portals = (aas_portal_t *) GetClearedMemory(AAS_MAX_PORTALS * sizeof(aas_portal_t));" in init_clustering
	assert "aasworld.portalindex = (aas_portalindex_t *) GetClearedMemory(AAS_MAX_PORTALINDEXSIZE * sizeof(aas_portalindex_t));" in init_clustering
	assert "aasworld.clusters = (aas_cluster_t *) GetClearedMemory(AAS_MAX_CLUSTERS * sizeof(aas_cluster_t));" in init_clustering
	assert "aasworld.numportals = 1;" in init_clustering
	assert "aasworld.numclusters = 1;" in init_clustering
	assert "AAS_CreatePortals();" in init_clustering
	assert "if (!AAS_FindClusters())" in init_clustering
	assert "if (!AAS_TestPortals())" in init_clustering
	assert "aasworld.savefile = qtrue;" in init_clustering
	assert 'botimport.Print(PRT_MESSAGE, "%6d portals created\\n", aasworld.numportals);' in init_clustering


def test_aas_bsp_public_export_and_game_import_wiring_match_retail_shape() -> None:
	botlib_h = _read(BOTLIB_PUBLIC)
	interface = _read(BOTLIB_INTERFACE)
	server = _read(SERVER_GAME)
	server_imports = _read(SERVER_QL_GAME_IMPORTS)
	g_syscalls = _read(GAME_SYSCALLS)

	_assert_order(
		botlib_h,
		"int\t\t\t(*AAS_PointContents)(vec3_t point);",
		"int\t\t\t(*AAS_NextBSPEntity)(int ent);",
		"int\t\t\t(*AAS_ValueForBSPEpairKey)(int ent, char *key, char *value, int size);",
		"int\t\t\t(*AAS_VectorForBSPEpairKey)(int ent, char *key, vec3_t v);",
		"int\t\t\t(*AAS_FloatForBSPEpairKey)(int ent, char *key, float *value);",
		"int\t\t\t(*AAS_IntForBSPEpairKey)(int ent, char *key, int *value);",
	)
	_assert_order(
		interface,
		"aas->AAS_PointContents = AAS_PointContents;",
		"aas->AAS_NextBSPEntity = AAS_NextBSPEntity;",
		"aas->AAS_ValueForBSPEpairKey = AAS_ValueForBSPEpairKey;",
		"aas->AAS_VectorForBSPEpairKey = AAS_VectorForBSPEpairKey;",
		"aas->AAS_FloatForBSPEpairKey = AAS_FloatForBSPEpairKey;",
		"aas->AAS_IntForBSPEpairKey = AAS_IntForBSPEpairKey;",
	)

	for expected in (
		"case BOTLIB_AAS_POINT_CONTENTS:\n\t\treturn botlib_export->aas.AAS_PointContents( VMA(1) );",
		"case BOTLIB_AAS_NEXT_BSP_ENTITY:\n\t\treturn botlib_export->aas.AAS_NextBSPEntity( args[1] );",
		"case BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY:\n\t\treturn botlib_export->aas.AAS_ValueForBSPEpairKey( args[1], VMA(2), VMA(3), args[4] );",
		"case BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY:\n\t\treturn botlib_export->aas.AAS_VectorForBSPEpairKey( args[1], VMA(2), VMA(3) );",
		"case BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY:\n\t\treturn botlib_export->aas.AAS_FloatForBSPEpairKey( args[1], VMA(2), VMA(3) );",
		"case BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY:\n\t\treturn botlib_export->aas.AAS_IntForBSPEpairKey( args[1], VMA(2), VMA(3) );",
	):
		assert expected in server

	_assert_order(
		server,
		"[BOTLIB_AAS_POINT_CONTENTS] = (ql_import_f)QL_G_trap_AAS_PointContents,",
		"[BOTLIB_AAS_NEXT_BSP_ENTITY] = (ql_import_f)QL_G_trap_AAS_NextBSPEntity,",
		"[BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_ValueForBSPEpairKey,",
		"[BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_VectorForBSPEpairKey,",
		"[BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_FloatForBSPEpairKey,",
		"[BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_IntForBSPEpairKey,",
	)
	_assert_order(
		server,
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_POINT_CONTENTS] = (ql_import_f)QL_G_trap_AAS_PointContents;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_NEXT_BSP_ENTITY] = (ql_import_f)QL_G_trap_AAS_NextBSPEntity;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_ValueForBSPEpairKey;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_VectorForBSPEpairKey;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_FloatForBSPEpairKey;",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY] = (ql_import_f)QL_G_trap_AAS_IntForBSPEpairKey;",
	)

	for expected in (
		"static int QDECL QL_G_trap_AAS_PointContents( vec3_t point ) {\n\treturn G_Import_Syscall( BOTLIB_AAS_POINT_CONTENTS, point );\n}",
		"static int QDECL QL_G_trap_AAS_NextBSPEntity( int ent ) {\n\treturn G_Import_Syscall( BOTLIB_AAS_NEXT_BSP_ENTITY, ent );\n}",
		"static int QDECL QL_G_trap_AAS_ValueForBSPEpairKey( int ent, char *key, char *value, int size ) {\n\treturn G_Import_Syscall( BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY, ent, key, value, size );\n}",
		"static int QDECL QL_G_trap_AAS_VectorForBSPEpairKey( int ent, char *key, vec3_t v ) {\n\treturn G_Import_Syscall( BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY, ent, key, v );\n}",
		"static int QDECL QL_G_trap_AAS_FloatForBSPEpairKey( int ent, char *key, float *value ) {\n\treturn G_Import_Syscall( BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY, ent, key, value );\n}",
		"static int QDECL QL_G_trap_AAS_IntForBSPEpairKey( int ent, char *key, int *value ) {\n\treturn G_Import_Syscall( BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY, ent, key, value );\n}",
	):
		assert expected in server_imports

	for expected in (
		"case BOTLIB_AAS_POINT_CONTENTS: return G_QL_IMPORT_BOTLIB_AAS_POINT_CONTENTS;",
		"case BOTLIB_AAS_NEXT_BSP_ENTITY: return G_QL_IMPORT_BOTLIB_AAS_NEXT_BSP_ENTITY;",
		"case BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY: return G_QL_IMPORT_BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY;",
		"case BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY: return G_QL_IMPORT_BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY;",
		"case BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY: return G_QL_IMPORT_BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY;",
		"case BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY: return G_QL_IMPORT_BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY;",
		"int trap_AAS_PointContents(vec3_t point) {\n\treturn syscall( BOTLIB_AAS_POINT_CONTENTS, point );\n}",
		"int trap_AAS_NextBSPEntity(int ent) {\n\treturn syscall( BOTLIB_AAS_NEXT_BSP_ENTITY, ent );\n}",
		"int trap_AAS_ValueForBSPEpairKey(int ent, char *key, char *value, int size) {\n\treturn syscall( BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY, ent, key, value, size );\n}",
		"int trap_AAS_VectorForBSPEpairKey(int ent, char *key, vec3_t v) {\n\treturn syscall( BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY, ent, key, v );\n}",
		"int trap_AAS_FloatForBSPEpairKey(int ent, char *key, float *value) {\n\treturn syscall( BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY, ent, key, value );\n}",
		"int trap_AAS_IntForBSPEpairKey(int ent, char *key, int *value) {\n\treturn syscall( BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY, ent, key, value );\n}",
	):
		assert expected in g_syscalls
