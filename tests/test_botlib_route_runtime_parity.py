from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOTLIB_AAS_ROUTE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_route.c"
BOTLIB_AAS_ROUTEALT = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_routealt.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
GAME_AI_DMQ3 = REPO_ROOT / "src" / "code" / "game" / "ai_dmq3.c"
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
QL_STEAM_HLIL_PART06 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part06.txt"
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


def test_botlib_route_cache_internal_aliases_match_retail_references() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]
	functions = _read(QL_STEAM_FUNCTIONS)
	hlil = _read(QL_STEAM_HLIL_PART03)

	expected_aliases = {
		"493010": "AAS_FreeOldestCache",
		"493140": "AAS_FreeAllClusterAreaCache",
		"493230": "AAS_InitClusterAreaCache",
		"4932E0": "AAS_FreeAllPortalCache",
		"493390": "AAS_InitRoutingUpdate",
		"493420": "AAS_WriteRouteCache",
		"493670": "AAS_ReadCache",
		"4936D0": "AAS_ReadRouteCache",
		"4938A0": "AAS_InitReachabilityAreas",
		"493A50": "AAS_InitRouting",
		"493AD0": "AAS_FreeRoutingCaches",
		"493BA0": "AAS_UpdateAreaRoutingCache",
		"493F30": "AAS_GetAreaRoutingCache",
		"4940D0": "AAS_UpdatePortalRoutingCache",
		"494300": "AAS_GetPortalRoutingCache",
		"494460": "AAS_AreaRouteToGoalArea",
		"494830": "AAS_AreaTravelTimeToGoalArea",
		"494870": "AAS_PredictRoute",
		"494BB0": "AAS_ReachabilityFromNum",
		"494C10": "AAS_NextAreaReachability",
		"494C90": "AAS_NextModelReachability",
		"494D10": "AAS_AltRoutingFloodCluster_r",
		"494DB0": "AAS_AlternativeRouteGoals",
	}
	for address, name in expected_aliases.items():
		assert aliases[f"sub_{address}"] == name

	for row in (
		"FUN_00494db0,00494db0,1036,0,unknown",
		"FUN_00494460,00494460,968,0,unknown",
		"FUN_00493ba0,00493ba0,908,0,unknown",
		"FUN_00494870,00494870,830,0,unknown",
		"FUN_004940d0,004940d0,547,0,unknown",
		"FUN_004936d0,004936d0,460,0,unknown",
		"FUN_00493f30,00493f30,414,0,unknown",
		"FUN_004938a0,004938a0,393,0,unknown",
		"FUN_00494300,00494300,331,0,unknown",
		"FUN_00493010,00493010,289,0,unknown",
		"FUN_00493140,00493140,236,0,unknown",
		"FUN_004932e0,004932e0,168,0,unknown",
		"FUN_00493230,00493230,160,0,unknown",
		"FUN_00493390,00493390,134,0,unknown",
		"FUN_00494d10,00494d10,145,0,unknown",
		"FUN_00494c10,00494c10,123,0,unknown",
		"FUN_00494c90,00494c90,113,0,unknown",
		"FUN_00493670,00493670,90,0,unknown",
		"FUN_00494bb0,00494bb0,89,0,unknown",
		"FUN_00494830,00494830,49,0,unknown",
	):
		assert row in functions

	for evidence in (
		"00493010    int32_t sub_493010()",
		"00493140    void sub_493140()",
		"00493230    void* sub_493230()",
		"004932e0    void sub_4932e0()",
		"00493390    char* sub_493390()",
		"00493670    void* __convention(\"regparm\") sub_493670",
		"004936d0    int32_t sub_4936d0()",
		"004938a0    char* sub_4938a0()",
		"00493a50    int32_t sub_493a50()",
		"00494460    int32_t sub_494460",
		"00494db0    void sub_494db0",
	):
		assert evidence in hlil


def test_botlib_route_cache_persistence_source_matches_retail_hlil_shape() -> None:
	route = _read(BOTLIB_AAS_ROUTE)
	hlil = _read(QL_STEAM_HLIL_PART03)
	hlil_strings = _read(QL_STEAM_HLIL_PART06)

	write_cache = _extract_function_block(route, "void AAS_WriteRouteCache(void)")
	read_cache = _extract_function_block(route, "aas_routingcache_t *AAS_ReadCache(fileHandle_t fp)")
	read_route_cache = _extract_function_block(route, "int AAS_ReadRouteCache(void)")
	init_routing = _extract_function_block(route, "void AAS_InitRouting(void)")
	free_routing = _extract_function_block(route, "void AAS_FreeRoutingCaches(void)")

	assert "int ident;" in route
	assert "int version;" in route
	assert "int numportalcache;" in route
	assert "int numareacache;" in route
	assert "#define RCID" in route
	assert "(('C'<<24)+('R'<<16)+('E'<<8)+'M')" in route
	assert "#define RCVERSION" in route
	assert "2" in route[route.index("#define RCVERSION") : route.index("//void AAS_DecompressVis")]

	assert 'Com_sprintf(filename, MAX_QPATH, "maps/%s.rcd", aasworld.mapname);' in write_cache
	assert "botimport.FS_FOpenFile( filename, &fp, FS_WRITE );" in write_cache
	assert "AAS_Error(\"Unable to open file: %s\\n\", filename);" in write_cache
	assert "routecacheheader.ident = RCID;" in write_cache
	assert "routecacheheader.version = RCVERSION;" in write_cache
	assert "routecacheheader.areacrc = CRC_ProcessString" in write_cache
	assert "routecacheheader.clustercrc = CRC_ProcessString" in write_cache
	assert "routecacheheader.numportalcache = numportalcache;" in write_cache
	assert "routecacheheader.numareacache = numareacache;" in write_cache
	assert "botimport.FS_Write(&routecacheheader, sizeof(routecacheheader_t), fp);" in write_cache
	assert "botimport.FS_Write(cache, cache->size, fp);" in write_cache
	assert "botimport.FS_FCloseFile(fp);" in write_cache
	assert 'botimport.Print(PRT_MESSAGE, "\\nroute cache written to %s\\n", filename);' in write_cache
	assert 'botimport.Print(PRT_MESSAGE, "written %d bytes of routing cache\\n", totalsize);' in write_cache

	assert "botimport.FS_Read(&size, sizeof(size), fp);" in read_cache
	assert "cache = (aas_routingcache_t *) GetMemory(size);" in read_cache
	assert "cache->size = size;" in read_cache
	assert "botimport.FS_Read((unsigned char *)cache + sizeof(size), size - sizeof(size), fp);" in read_cache
	assert "cache->reachabilities = (unsigned char *) cache + sizeof(aas_routingcache_t) - sizeof(unsigned short)" in read_cache
	assert "(size - sizeof(aas_routingcache_t) + sizeof(unsigned short)) / 3 * 2;" in read_cache

	assert 'Com_sprintf(filename, MAX_QPATH, "maps/%s.rcd", aasworld.mapname);' in read_route_cache
	assert "botimport.FS_FOpenFile( filename, &fp, FS_READ );" in read_route_cache
	assert "if (routecacheheader.ident != RCID)" in read_route_cache
	assert 'AAS_Error("%s is not a route cache dump\\n");' in read_route_cache
	assert "routecacheheader.version != RCVERSION" in read_route_cache
	assert "routecacheheader.numareas != aasworld.numareas" in read_route_cache
	assert "routecacheheader.numclusters != aasworld.numclusters" in read_route_cache
	assert "CRC_ProcessString( (unsigned char *)aasworld.areas, sizeof(aas_area_t) * aasworld.numareas )" in read_route_cache
	assert "CRC_ProcessString( (unsigned char *)aasworld.clusters, sizeof(aas_cluster_t) * aasworld.numclusters )" in read_route_cache
	assert "cache = AAS_ReadCache(fp);" in read_route_cache
	assert "cache->next = aasworld.portalcache[cache->areanum];" in read_route_cache
	assert "clusterareanum = AAS_ClusterAreaNum(cache->cluster, cache->areanum);" in read_route_cache
	assert "aasworld.clusterareacache[cache->cluster][clusterareanum] = cache;" in read_route_cache
	assert "botimport.FS_FCloseFile(fp);" in read_route_cache

	for earlier, later in (
		("AAS_InitTravelFlagFromType();", "AAS_InitAreaContentsTravelFlags();"),
		("AAS_InitAreaContentsTravelFlags();", "AAS_InitRoutingUpdate();"),
		("AAS_InitRoutingUpdate();", "AAS_CreateReversedReachability();"),
		("AAS_CreateReversedReachability();", "AAS_InitClusterAreaCache();"),
		("AAS_InitClusterAreaCache();", "AAS_InitPortalCache();"),
		("AAS_InitPortalCache();", "AAS_CalculateAreaTravelTimes();"),
		("AAS_CalculateAreaTravelTimes();", "AAS_InitPortalMaxTravelTimes();"),
		("AAS_InitPortalMaxTravelTimes();", "AAS_InitReachabilityAreas();"),
		("max_routingcachesize = 1024 * (int) LibVarValue(\"max_routingcache\", \"4096\");", "AAS_ReadRouteCache();"),
	):
		assert init_routing.index(earlier) < init_routing.index(later)

	for expected in (
		"AAS_FreeAllClusterAreaCache();",
		"AAS_FreeAllPortalCache();",
		"if (aasworld.areatraveltimes) FreeMemory(aasworld.areatraveltimes);",
		"if (aasworld.portalmaxtraveltimes) FreeMemory(aasworld.portalmaxtraveltimes);",
		"if (aasworld.reversedreachability) FreeMemory(aasworld.reversedreachability);",
		"if (aasworld.areaupdate) FreeMemory(aasworld.areaupdate);",
		"if (aasworld.portalupdate) FreeMemory(aasworld.portalupdate);",
		"if (aasworld.reachabilityareas) FreeMemory(aasworld.reachabilityareas);",
		"if (aasworld.reachabilityareaindex) FreeMemory(aasworld.reachabilityareaindex);",
		"if (aasworld.areacontentstravelflags) FreeMemory(aasworld.areacontentstravelflags);",
	):
		assert expected in free_routing

	for evidence in (
		"00493420    int32_t sub_493420()",
		"004934c4  sub_4d9160(&var_48, 0x40, \"maps/%s.rcd\")",
		"0049351f  __builtin_strncpy(dest: &var_68, src: \"MERC\", n: 4)",
		"00493526  int32_t var_64 = 2",
		"00493548  uint32_t var_58 = zx.d(sub_4a84b0(eax_4, eax_3 * 0x30))",
		"0049355d  uint32_t var_54 = zx.d(sub_4a84b0(data_16de984, data_16de980 << 4))",
		"00493641  data_16dd800(1, \"\\nroute cache written to %s\\n\", &var_48)",
		"0049364f  int32_t eax_13 = data_16dd800(1, \"written %d bytes of routing cach…\", ebx_2)",
		"00493670    void* __convention(\"regparm\") sub_493670",
		"004936bf  *(result + 0x38) = result + (((var_8 - 0x3e) u/ 3) << 1) + 0x3e",
		"004936d0    int32_t sub_4936d0()",
		"004936f1  sub_4d9160(&var_48, 0x40, \"maps/%s.rcd\")",
		"00493728      if (var_68 == 0x4352454d)",
		"00493758              sub_4861a0(\"route cache dump has wrong versi…\")",
		"0049372f          sub_4861a0(\"%s is not a route cache dump\\n\")",
		"00493881                  data_16dd83c(var_6c)",
	):
		assert evidence in hlil

	for string_anchor in (
		"0053a854  char const data_53a854[0x1c] = \"\\nroute cache written to %s\\n\", 0",
		"0053a898  char const data_53a898[0x34] = \"route cache dump has wrong version %d, should be %d\", 0",
		"0053a8cc  char const data_53a8cc[0x1e] = \"%s is not a route cache dump\\n\", 0",
	):
		assert string_anchor in hlil_strings


def test_botlib_route_query_prediction_and_reachability_source_match_retail_shape() -> None:
	route = _read(BOTLIB_AAS_ROUTE)
	hlil = _read(QL_STEAM_HLIL_PART03)
	hlil_strings = _read(QL_STEAM_HLIL_PART06)

	area_route = _extract_function_block(
		route,
		"int AAS_AreaRouteToGoalArea(int areanum, vec3_t origin, int goalareanum, int travelflags, int *traveltime, int *reachnum)",
	)
	travel_time = _extract_function_block(
		route,
		"int AAS_AreaTravelTimeToGoalArea(int areanum, vec3_t origin, int goalareanum, int travelflags)",
	)
	predict_route = _extract_function_block(
		route,
		"int AAS_PredictRoute(struct aas_predictroute_s *route, int areanum, vec3_t origin",
	)
	reach_from_num = _extract_function_block(
		route,
		"void AAS_ReachabilityFromNum(int num, struct aas_reachability_s *reach)",
	)
	next_area_reach = _extract_function_block(route, "int AAS_NextAreaReachability(int areanum, int reachnum)")
	next_model_reach = _extract_function_block(route, "int AAS_NextModelReachability(int num, int modelnum)")

	assert "if (!aasworld.initialized) return qfalse;" in area_route
	assert "if (areanum == goalareanum)" in area_route
	assert "*traveltime = 1;" in area_route
	assert "*reachnum = 0;" in area_route
	assert 'botimport.Print(PRT_ERROR, "AAS_AreaTravelTimeToGoalArea: areanum %d out of range\\n", areanum);' in area_route
	assert 'botimport.Print(PRT_ERROR, "AAS_AreaTravelTimeToGoalArea: goalareanum %d out of range\\n", goalareanum);' in area_route
	assert "while(AvailableMemory() < 1 * 1024 * 1024)" in area_route
	assert "if (!AAS_FreeOldestCache()) break;" in area_route
	assert "travelflags |= TFL_DONOTENTER;" in area_route
	assert "areacache = AAS_GetAreaRoutingCache(clusternum, goalareanum, travelflags);" in area_route
	assert "portalcache = AAS_GetPortalRoutingCache(goalclusternum, goalareanum, travelflags);" in area_route
	assert "*traveltime = portalcache->traveltimes[-clusternum];" in area_route
	assert "t += aasworld.portalmaxtraveltimes[portalnum];" in area_route
	assert "if (bestreachnum < 0)" in area_route
	assert "*reachnum = bestreachnum;" in area_route
	assert "*traveltime = besttime;" in area_route

	assert "if (AAS_AreaRouteToGoalArea(areanum, origin, goalareanum, travelflags, &traveltime, &reachnum))" in travel_time
	assert "return traveltime;" in travel_time
	assert "return 0;" in travel_time

	for expected in (
		"route->stopevent = RSE_NONE;",
		"route->endarea = goalareanum;",
		"route->endcontents = 0;",
		"route->endtravelflags = 0;",
		"VectorCopy(origin, route->endpos);",
		"route->time = 0;",
		"for (i = 0; curareanum != goalareanum && (!maxareas || i < maxareas) && i < aasworld.numareas; i++)",
		"reachnum = AAS_AreaReachabilityToGoalArea(curareanum, curorigin, goalareanum, travelflags);",
		"route->stopevent = RSE_NOROUTE;",
		"if (stopevent & RSE_USETRAVELTYPE)",
		"if (AAS_TravelFlagForType_inline(reach->traveltype) & stoptfl)",
		"if (AAS_AreaContentsTravelFlags_inline(reach->areanum) & stoptfl)",
		"if (stopevent & RSE_ENTERCONTENTS)",
		"if (stopevent & RSE_ENTERAREA)",
		"route->time += AAS_AreaTravelTime(areanum, origin, reach->start);",
		"route->time += reach->traveltime;",
		"route->endarea = reach->areanum;",
		"route->endtravelflags = AAS_TravelFlagForType_inline(reach->traveltype);",
		"if (maxtime && route->time > maxtime)",
		"if (curareanum != goalareanum)",
	):
		assert expected in predict_route

	assert "Com_Memset(reach, 0, sizeof(aas_reachability_t));" in reach_from_num
	assert "Com_Memcpy(reach, &aasworld.reachability[num], sizeof(aas_reachability_t));" in reach_from_num
	assert "return settings->firstreachablearea;" in next_area_reach
	assert 'botimport.Print(PRT_FATAL, "AAS_NextAreaReachability: reachnum < settings->firstreachableara");' in next_area_reach
	assert "reachnum >= settings->firstreachablearea + settings->numreachableareas" in next_area_reach
	assert "(aasworld.reachability[i].traveltype & TRAVELTYPE_MASK) == TRAVEL_ELEVATOR" in next_model_reach
	assert "(aasworld.reachability[i].traveltype & TRAVELTYPE_MASK) == TRAVEL_FUNCBOB" in next_model_reach
	assert "(aasworld.reachability[i].facenum & 0x0000FFFF) == modelnum" in next_model_reach

	for evidence in (
		"00494460    int32_t sub_494460",
		"0049446d  if (data_16de884 == 0)",
		"00494487      *arg5 = 1",
		"0049448e      *arg6 = 0",
		"004944d7                  if (sub_493010() == 0)",
		"004944e3              while (i s< 0x100000)",
		"004944ff              arg4 |= 0x800000",
		"00494667              char* eax_30 = sub_494300",
		"00494703                              sub_493f30",
		"004947f7          data_16dd800(3, \"AAS_AreaTravelTimeToGoalArea: go…\", arg3)",
		"00494819      data_16dd800(3, \"AAS_AreaTravelTimeToGoalArea: ar…\", arg1)",
		"00494830    int32_t sub_494830",
		"0049484e  int32_t eax_1 = sub_494460",
		"00494870    int32_t sub_494870",
		"00494884  esi[3] = ecx",
		"0049488a  esi[4] = 0",
		"0049488d  esi[5] = 0",
		"00494890  esi[6] = 0",
		"004948a0  esi[8] = 0",
		"004948f1              int32_t eax_3 = sub_494460",
		"00494bb0    int32_t sub_494bb0",
		"00494bcd      return sub_4c95e0(arg2, 0, 0x2c)",
		"00494bf6      return sub_4cb7d0(arg2, arg1 * 0x2c + data_16de964, 0x2c)",
		"00494c10    int32_t sub_494c10",
		"00494c57          data_16dd800(4, \"AAS_NextAreaReachability: reachn…\")",
		"00494c7e      data_16dd800(3, \"AAS_NextAreaReachability: areanu…\", arg1)",
		"00494c90    int32_t sub_494c90",
		"00494cdc          if (ecx_3 == 0xb)",
		"00494cdc          else if (ecx_3 == 0x13)",
	):
		assert evidence in hlil

	for string_anchor in (
		"0053a908  char const data_53a908[0x37] = \"AAS_AreaTravelTimeToGoalArea: areanum %d out of range\\n\", 0",
		"0053a940  char const data_53a940[0x3b] = \"AAS_AreaTravelTimeToGoalArea: goalareanum %d out of range\\n\", 0",
		"0053a97c  char const data_53a97c[0x33] = \"AAS_NextAreaReachability: areanum %d out of range\\n\", 0",
		"0053a9b0  char const data_53a9b0[0x41] = \"AAS_NextAreaReachability: reachnum < settings->firstreachableara\", 0",
	):
		assert string_anchor in hlil_strings


def test_botlib_alternative_route_goals_and_import_wiring_match_retail_shape() -> None:
	routealt = _read(BOTLIB_AAS_ROUTEALT)
	interface = _read(BOTLIB_INTERFACE)
	botlib_public = _read(BOTLIB_PUBLIC)
	server_game = _read(SERVER_GAME)
	ql_imports = _read(SERVER_QL_GAME_IMPORTS)
	game_syscalls = _read(GAME_SYSCALLS)
	ai_dmq3 = _read(GAME_AI_DMQ3)
	hlil = _read(QL_STEAM_HLIL_PART03)

	flood = _extract_function_block(routealt, "void AAS_AltRoutingFloodCluster_r(int areanum)")
	alternative = _extract_function_block(
		routealt,
		"int AAS_AlternativeRouteGoals(vec3_t start, int startareanum, vec3_t goal, int goalareanum, int travelflags,",
	)
	init_alt = _extract_function_block(routealt, "void AAS_InitAlternativeRouting(void)")
	shutdown_alt = _extract_function_block(routealt, "void AAS_ShutdownAlternativeRouting(void)")
	init_aas_export = _extract_function_block(interface, "static void Init_AAS_Export( aas_export_t *aas )")
	trap_predict = _extract_function_block(
		ql_imports,
		"static int QDECL QL_G_trap_AAS_PredictRoute",
	)
	trap_alt = _extract_function_block(
		ql_imports,
		"static int QDECL QL_G_trap_AAS_AlternativeRouteGoals",
	)
	sys_predict = _extract_function_block(
		game_syscalls,
		"int trap_AAS_PredictRoute(void /*struct aas_predictroute_s*/ *route, int areanum, vec3_t origin,",
	)
	sys_alt = _extract_function_block(
		game_syscalls,
		"int trap_AAS_AlternativeRouteGoals(vec3_t start, int startareanum, vec3_t goal, int goalareanum, int travelflags,",
	)

	assert "clusterareas[numclusterareas] = areanum;" in flood
	assert "midrangeareas[areanum].valid = qfalse;" in flood
	assert "face = &aasworld.faces[abs(aasworld.faceindex[area->firstface + i])];" in flood
	assert "if (!midrangeareas[otherareanum].valid) continue;" in flood
	assert "AAS_AltRoutingFloodCluster_r(otherareanum);" in flood

	assert "if (!startareanum || !goalareanum)" in alternative
	assert "goaltraveltime = AAS_AreaTravelTimeToGoalArea(startareanum, start, goalareanum, travelflags);" in alternative
	assert "Com_Memset(midrangeareas, 0, aasworld.numareas * sizeof(midrangearea_t));" in alternative
	assert "if (!(type & ALTROUTEGOAL_ALL))" in alternative
	assert "type & ALTROUTEGOAL_CLUSTERPORTALS" in alternative
	assert "type & ALTROUTEGOAL_VIEWPORTALS" in alternative
	assert "if (!AAS_AreaReachability(i)) continue;" in alternative
	assert "starttime = AAS_AreaTravelTimeToGoalArea(startareanum, start, i, travelflags);" in alternative
	assert "if (starttime > (float) 1.1 * goaltraveltime) continue;" in alternative
	assert "goaltime = AAS_AreaTravelTimeToGoalArea(i, NULL, goalareanum, travelflags);" in alternative
	assert "if (goaltime > (float) 0.8 * goaltraveltime) continue;" in alternative
	assert "midrangeareas[i].valid = qtrue;" in alternative
	assert 'Log_Write("%d midrange area %d", nummidrangeareas, i);' in alternative
	assert "AAS_AltRoutingFloodCluster_r(i);" in alternative
	assert "VectorScale(mid, 1.0 / numclusterareas, mid);" in alternative
	assert "VectorCopy(aasworld.areas[bestareanum].center, altroutegoals[numaltroutegoals].origin);" in alternative
	assert "altroutegoals[numaltroutegoals].extratraveltime =" in alternative
	assert "if (numaltroutegoals >= maxaltroutegoals) break;" in alternative

	assert "midrangeareas = (midrangearea_t *) GetMemory(aasworld.numareas * sizeof(midrangearea_t));" in init_alt
	assert "clusterareas = (int *) GetMemory(aasworld.numareas * sizeof(int));" in init_alt
	assert "if (midrangeareas) FreeMemory(midrangeareas);" in shutdown_alt
	assert "midrangeareas = NULL;" in shutdown_alt
	assert "if (clusterareas) FreeMemory(clusterareas);" in shutdown_alt
	assert "clusterareas = NULL;" in shutdown_alt
	assert "numclusterareas = 0;" in shutdown_alt

	assert "(*AAS_AreaTravelTimeToGoalArea)" in botlib_public
	assert "(*AAS_EnableRoutingArea)" in botlib_public
	assert "(*AAS_PredictRoute)" in botlib_public
	assert "(*AAS_AlternativeRouteGoals)" in botlib_public
	assert botlib_public.index("(*AAS_AreaTravelTimeToGoalArea)") < botlib_public.index("(*AAS_EnableRoutingArea)")
	assert botlib_public.index("(*AAS_EnableRoutingArea)") < botlib_public.index("(*AAS_PredictRoute)")
	assert botlib_public.index("(*AAS_PredictRoute)") < botlib_public.index("(*AAS_AlternativeRouteGoals)")
	assert botlib_public.index("(*AAS_AlternativeRouteGoals)") < botlib_public.index("(*AAS_Swimming)")

	assert "aas->AAS_AreaTravelTimeToGoalArea = AAS_AreaTravelTimeToGoalArea;" in init_aas_export
	assert "aas->AAS_EnableRoutingArea = AAS_EnableRoutingArea;" in init_aas_export
	assert "aas->AAS_PredictRoute = AAS_PredictRoute;" in init_aas_export
	assert "aas->AAS_AlternativeRouteGoals = AAS_AlternativeRouteGoals;" in init_aas_export
	assert init_aas_export.index("aas->AAS_PredictRoute = AAS_PredictRoute;") < init_aas_export.index(
		"aas->AAS_AlternativeRouteGoals = AAS_AlternativeRouteGoals;"
	)
	assert init_aas_export.index("aas->AAS_AlternativeRouteGoals = AAS_AlternativeRouteGoals;") < init_aas_export.index(
		"aas->AAS_Swimming = AAS_Swimming;"
	)

	assert "return botlib_export->aas.AAS_PredictRoute( VMA(1), args[2], VMA(3), args[4], args[5], args[6], args[7], args[8], args[9], args[10], args[11] );" in server_game
	assert "return botlib_export->aas.AAS_AlternativeRouteGoals( VMA(1), args[2], VMA(3), args[4], args[5], VMA(6), args[7], args[8] );" in server_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_PREDICT_ROUTE] = (ql_import_f)QL_G_trap_AAS_PredictRoute;" in server_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL] = (ql_import_f)QL_G_trap_AAS_AlternativeRouteGoals;" in server_game
	assert "return G_Import_Syscall( BOTLIB_AAS_PREDICT_ROUTE, route, areanum, origin, goalareanum, travelflags, maxareas, maxtime, stopevent, stopcontents, stoptfl, stopareanum );" in trap_predict
	assert "return G_Import_Syscall( BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL, start, startareanum, goal, goalareanum, travelflags, altroutegoals, maxaltroutegoals, type );" in trap_alt
	assert "return syscall( BOTLIB_AAS_PREDICT_ROUTE, route, areanum, origin, goalareanum, travelflags, maxareas, maxtime, stopevent, stopcontents, stoptfl, stopareanum );" in sys_predict
	assert "return syscall( BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL, start, startareanum, goal, goalareanum, travelflags, altroutegoals, maxaltroutegoals, type );" in sys_alt
	assert ai_dmq3.count("trap_AAS_AlternativeRouteGoals(") >= 8

	for evidence in (
		"00494d10    int32_t sub_494d10(int32_t arg1)",
		"00494d24  *(data_16de770 + (result << 2)) = arg1",
		"00494d39  *(data_16de768 + (arg1 << 3)) = 0",
		"00494d8e              result = sub_494d10(result)",
		"00494db0    void sub_494db0",
		"00494dca  if (edi == 0 || arg3 == 0)",
		"00494ddb  int32_t eax_2 = sub_494830(edi, arg1, arg3, arg4)",
		"00494df8  sub_4c95e0(data_16de768, 0, data_16de950 << 3)",
		"fconvert.t(1.1000000238418579)",
		"fconvert.t(0.80000001192092896)",
		"00494f09                                  sub_4a8970(\"%d midrange area %d\")",
		"00494f5a              sub_494d10(i)",
		"004a803d  arg1[0x12] = sub_494870",
		"004a8044  arg1[0x13] = sub_494db0",
	):
		assert evidence in hlil

