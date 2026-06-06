from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOTLIB_AAS_MAIN = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_main.c"
BOTLIB_AAS_ROUTE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_route.c"
BOTLIB_AAS_ROUTE_H = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_route.h"
BOTLIB_MOVE = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_move.c"
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


def test_botlib_route_prelude_aliases_match_retail_references() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]
	functions = _read(QL_STEAM_FUNCTIONS)
	hlil = _read(QL_STEAM_HLIL_PART03)
	hlil_strings = _read(QL_STEAM_HLIL_PART06)

	expected_aliases = {
		"4925F0": "AAS_RoutingInfo",
		"492630": "AAS_ClusterAreaNum",
		"492680": "AAS_InitTravelFlagFromType",
		"4927E0": "AAS_TravelFlagForType",
		"492800": "AAS_RemoveRoutingCacheInCluster",
		"4928B0": "AAS_RemoveRoutingCacheUsingArea",
		"492990": "AAS_EnableRoutingArea",
		"492A20": "AAS_AreaContentsTravelFlags",
		"492A40": "AAS_InitAreaContentsTravelFlags",
		"492B10": "AAS_CreateReversedReachability",
		"492C30": "AAS_AreaTravelTime",
		"492CD0": "AAS_CalculateAreaTravelTimes",
		"492F20": "AAS_InitPortalMaxTravelTimes",
	}
	for address, name in expected_aliases.items():
		assert aliases[f"sub_{address}"] == name

	for row in (
		"FUN_00492680,00492680,351,0,unknown",
		"FUN_00492cd0,00492cd0,575,0,unknown",
		"FUN_00492b10,00492b10,266,0,unknown",
		"FUN_00492f20,00492f20,226,0,unknown",
		"FUN_004928b0,004928b0,215,0,unknown",
		"FUN_00492a40,00492a40,193,0,unknown",
		"FUN_00492800,00492800,174,0,unknown",
		"FUN_00492c30,00492c30,145,0,unknown",
		"FUN_00492630,00492630,79,0,unknown",
		"FUN_004925f0,004925f0,63,0,unknown",
		"FUN_004927e0,004927e0,32,0,unknown",
		"FUN_00492a20,00492a20,17,0,unknown",
	):
		assert row in functions

	for evidence in (
		"004925f0    int32_t sub_4925f0()",
		"004925fd  data_16dd800(1, \"%d area cache updates\\n\", data_16de774)",
		"00492630    int32_t sub_492630(int32_t arg1, int32_t arg2)",
		"00492680    int32_t sub_492680()",
		"004927e0    int32_t sub_4927e0(int32_t arg1)",
		"004927e6  int32_t eax_1 = arg1 & 0xffffff",
		"00492800    void sub_492800(int32_t arg1)",
		"004928b0    int32_t sub_4928b0(int32_t arg1)",
		"004929e4          sub_4928b0(arg1)",
		"00492a20    int32_t sub_492a20(int32_t arg1)",
		"00492a40    char* sub_492a40()",
		"00492a5f  char* result = sub_4a89d0(data_16de950 << 2)",
		"00492b10    char* sub_492b10()",
		"00492b42  char* result = sub_4a89d0((data_16de950 << 3) + data_16de960 * 0xc)",
		"00492c30    int32_t sub_492c30(int32_t arg1, float arg2, float* arg3)",
		"00492ca8          arg2 = fconvert.s(fconvert.t(arg2) * fconvert.t(0.33000001311302185))",
		"00492cd0    char* sub_492cd0()",
		"00492f20    int32_t sub_492f20()",
		"00492f4a  data_16dfa58 = sub_4a89d0(data_16de970 << 2)",
	):
		assert evidence in hlil

	for string_anchor in (
		"0053a780  char const data_53a780[0x18] = \"%d bytes routing cache\\n\", 0",
		"0053a798  char const data_53a798[0x19] = \"%d portal cache updates\\n\", 0",
		"0053a7b4  char const data_53a7b4[0x17] = \"%d area cache updates\\n\", 0",
		"0053a7fc  char const data_53a7fc[0x2a] = \"area %d has more than 128 reachabilities\\n\", 0",
	):
		assert string_anchor in hlil_strings


def test_botlib_route_prelude_source_shapes_match_retail_hlil() -> None:
	route = _read(BOTLIB_AAS_ROUTE)

	routing_info = _extract_function_block(route, "void AAS_RoutingInfo(void)")
	cluster_area_num = _extract_function_block(route, "__inline int AAS_ClusterAreaNum")
	init_travel_flags = _extract_function_block(route, "void AAS_InitTravelFlagFromType(void)")
	travel_flag = _extract_function_block(route, "int AAS_TravelFlagForType(int traveltype)")
	remove_cluster = _extract_function_block(route, "void AAS_RemoveRoutingCacheInCluster")
	remove_using_area = _extract_function_block(route, "void AAS_RemoveRoutingCacheUsingArea")
	enable_area = _extract_function_block(route, "int AAS_EnableRoutingArea(int areanum, int enable)")
	area_contents = _extract_function_block(route, "int AAS_AreaContentsTravelFlags(int areanum)")
	init_area_contents = _extract_function_block(route, "void AAS_InitAreaContentsTravelFlags(void)")
	reversed_reach = _extract_function_block(route, "void AAS_CreateReversedReachability(void)")
	area_travel_time = _extract_function_block(route, "unsigned short int AAS_AreaTravelTime")
	calculate_area_times = _extract_function_block(route, "void AAS_CalculateAreaTravelTimes(void)")
	portal_max_time = _extract_function_block(route, "int AAS_PortalMaxTravelTime(int portalnum)")
	init_portal_times = _extract_function_block(route, "void AAS_InitPortalMaxTravelTimes(void)")

	assert 'botimport.Print(PRT_MESSAGE, "%d area cache updates\\n", numareacacheupdates);' in routing_info
	assert 'botimport.Print(PRT_MESSAGE, "%d portal cache updates\\n", numportalcacheupdates);' in routing_info
	assert 'botimport.Print(PRT_MESSAGE, "%d bytes routing cache\\n", routingcachesize);' in routing_info

	assert "areacluster = aasworld.areasettings[areanum].cluster;" in cluster_area_num
	assert "if (areacluster > 0) return aasworld.areasettings[areanum].clusterareanum;" in cluster_area_num
	assert "side = aasworld.portals[-areacluster].frontcluster != cluster;" in cluster_area_num
	assert "return aasworld.portals[-areacluster].clusterareanum[side];" in cluster_area_num

	for expected in (
		"aasworld.travelflagfortype[TRAVEL_INVALID] = TFL_INVALID;",
		"aasworld.travelflagfortype[TRAVEL_WALK] = TFL_WALK;",
		"aasworld.travelflagfortype[TRAVEL_CROUCH] = TFL_CROUCH;",
		"aasworld.travelflagfortype[TRAVEL_GRAPPLEHOOK] = TFL_GRAPPLEHOOK;",
		"aasworld.travelflagfortype[TRAVEL_DOUBLEJUMP] = TFL_DOUBLEJUMP;",
		"aasworld.travelflagfortype[TRAVEL_RAMPJUMP] = TFL_RAMPJUMP;",
		"aasworld.travelflagfortype[TRAVEL_STRAFEJUMP] = TFL_STRAFEJUMP;",
		"aasworld.travelflagfortype[TRAVEL_JUMPPAD] = TFL_JUMPPAD;",
		"aasworld.travelflagfortype[TRAVEL_FUNCBOB] = TFL_FUNCBOB;",
	):
		assert expected in init_travel_flags
	assert "return AAS_TravelFlagForType_inline(traveltype);" in travel_flag

	assert "if (!aasworld.clusterareacache)" in remove_cluster
	assert "cluster = &aasworld.clusters[clusternum];" in remove_cluster
	assert "for (cache = aasworld.clusterareacache[clusternum][i]; cache; cache = nextcache)" in remove_cluster
	assert "AAS_FreeRoutingCache(cache);" in remove_cluster
	assert "aasworld.clusterareacache[clusternum][i] = NULL;" in remove_cluster

	assert "clusternum = aasworld.areasettings[areanum].cluster;" in remove_using_area
	assert "AAS_RemoveRoutingCacheInCluster( clusternum );" in remove_using_area
	assert "AAS_RemoveRoutingCacheInCluster( aasworld.portals[-clusternum].frontcluster );" in remove_using_area
	assert "AAS_RemoveRoutingCacheInCluster( aasworld.portals[-clusternum].backcluster );" in remove_using_area
	assert "for (cache = aasworld.portalcache[i]; cache; cache = nextcache)" in remove_using_area
	assert "aasworld.portalcache[i] = NULL;" in remove_using_area

	assert "flags = aasworld.areasettings[areanum].areaflags & AREA_DISABLED;" in enable_area
	assert "if (enable < 0)" in enable_area
	assert "aasworld.areasettings[areanum].areaflags &= ~AREA_DISABLED;" in enable_area
	assert "aasworld.areasettings[areanum].areaflags |= AREA_DISABLED;" in enable_area
	assert "AAS_RemoveRoutingCacheUsingArea( areanum );" in enable_area

	assert "return aasworld.areacontentstravelflags[areanum];" in area_contents
	assert "if (aasworld.areacontentstravelflags) FreeMemory(aasworld.areacontentstravelflags);" in init_area_contents
	assert "aasworld.areacontentstravelflags = (int *) GetClearedMemory(aasworld.numareas * sizeof(int));" in init_area_contents
	assert "aasworld.areacontentstravelflags[i] = AAS_GetAreaContentsTravelFlags(i);" in init_area_contents

	assert "if (aasworld.reversedreachability) FreeMemory(aasworld.reversedreachability);" in reversed_reach
	assert "aasworld.reversedreachability = (aas_reversedreachability_t *) ptr;" in reversed_reach
	assert 'botimport.Print(PRT_WARNING, "area %d has more than 128 reachabilities\\n", i);' in reversed_reach
	assert "revlink->areanum = i;" in reversed_reach
	assert "revlink->linknum = settings->firstreachablearea + n;" in reversed_reach
	assert "aasworld.reversedreachability[reach->areanum].numlinks++;" in reversed_reach

	assert "VectorSubtract(start, end, dir);" in area_travel_time
	assert "dist = VectorLength(dir);" in area_travel_time
	assert "if (AAS_AreaCrouch(areanum)) dist *= DISTANCEFACTOR_CROUCH;" in area_travel_time
	assert "else if (AAS_AreaSwim(areanum)) dist *= DISTANCEFACTOR_SWIM;" in area_travel_time
	assert "else dist *= DISTANCEFACTOR_WALK;" in area_travel_time
	assert "if (intdist <= 0) intdist = 1;" in area_travel_time

	assert "if (aasworld.areatraveltimes) FreeMemory(aasworld.areatraveltimes);" in calculate_area_times
	assert "size = aasworld.numareas * sizeof(unsigned short **);" in calculate_area_times
	assert "size += settings->numreachableareas * revreach->numlinks * sizeof(unsigned short);" in calculate_area_times
	assert "aasworld.areatraveltimes = (unsigned short ***) ptr;" in calculate_area_times
	assert "aasworld.areatraveltimes[i][l][n] = AAS_AreaTravelTime(i, end, reach->start);" in calculate_area_times

	assert "portal = &aasworld.portals[portalnum];" in portal_max_time
	assert "revreach = &aasworld.reversedreachability[portal->areanum];" in portal_max_time
	assert "t = aasworld.areatraveltimes[portal->areanum][l][n];" in portal_max_time
	assert "if (t > maxt)" in portal_max_time

	assert "if (aasworld.portalmaxtraveltimes) FreeMemory(aasworld.portalmaxtraveltimes);" in init_portal_times
	assert "aasworld.portalmaxtraveltimes = (int *) GetClearedMemory(aasworld.numportals * sizeof(int));" in init_portal_times
	assert "aasworld.portalmaxtraveltimes[i] = AAS_PortalMaxTravelTime(i);" in init_portal_times


def test_botlib_route_prelude_helpers_are_wired_into_aas_and_move_ai() -> None:
	aas_main = _read(BOTLIB_AAS_MAIN)
	route = _read(BOTLIB_AAS_ROUTE)
	route_h = _read(BOTLIB_AAS_ROUTE_H)
	move = _read(BOTLIB_MOVE)

	start_frame = _extract_function_block(aas_main, "int AAS_StartFrame(float time)")
	init_routing = _extract_function_block(route, "void AAS_InitRouting(void)")
	bot_valid_travel = _extract_function_block(move, "int BotValidTravel")
	bot_move_to_goal = _extract_function_block(move, "void BotMoveToGoal(bot_moveresult_t *result")

	assert "if (LibVarGetValue(\"showcacheupdates\"))" in start_frame
	assert "AAS_RoutingInfo();" in start_frame
	assert "LibVarSet(\"showcacheupdates\", \"0\");" in start_frame

	for earlier, later in (
		("AAS_InitTravelFlagFromType();", "AAS_InitAreaContentsTravelFlags();"),
		("AAS_InitAreaContentsTravelFlags();", "AAS_InitRoutingUpdate();"),
		("AAS_InitRoutingUpdate();", "AAS_CreateReversedReachability();"),
		("AAS_CreateReversedReachability();", "AAS_InitClusterAreaCache();"),
		("AAS_CalculateAreaTravelTimes();", "AAS_InitPortalMaxTravelTimes();"),
		("AAS_InitPortalMaxTravelTimes();", "AAS_InitReachabilityAreas();"),
	):
		assert init_routing.index(earlier) < init_routing.index(later)

	assert "if (AAS_TravelFlagForType(reach->traveltype) & ~travelflags) return qfalse;" in bot_valid_travel
	assert "if (AAS_AreaContentsTravelFlags(reach->areanum) & ~travelflags) return qfalse;" in bot_valid_travel
	assert "if (!(AAS_TravelFlagForType(reach.traveltype) & travelflags))" in bot_move_to_goal

	for declaration in (
		"void AAS_RoutingInfo(void);",
		"int AAS_TravelFlagForType(int traveltype);",
		"int AAS_AreaContentsTravelFlags(int areanum);",
		"unsigned short int AAS_AreaTravelTime(int areanum, vec3_t start, vec3_t end);",
		"int AAS_EnableRoutingArea(int areanum, int enable);",
	):
		assert declaration in route_h


def test_botlib_route_prelude_inline_or_fused_helpers_are_not_over_promoted() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]
	hlil = _read(QL_STEAM_HLIL_PART03)

	assert "AAS_UnlinkCache" not in aliases.values()
	assert "AAS_LinkCache" not in aliases.values()
	assert "AAS_FreeRoutingCache" not in aliases.values()
	assert "AAS_RoutingTime" not in aliases.values()
	assert "AAS_GetAreaContentsTravelFlags" not in aliases.values()
	assert "AAS_PortalMaxTravelTime" not in aliases.values()

	assert "00492cd6  sub_4a7cc0()" in hlil
	assert "00492e86                          if (sub_488d80(ebx_12) == 0)" in hlil
	assert "00492e9e                              if (sub_488db0(ebx_12) == 0)" in hlil
	assert "00492f23  void* eax = data_16dfa58" in hlil
	assert "00492fc0                          uint32_t edx_6 = zx.d(*ecx_5)" in hlil
