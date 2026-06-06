import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

BOTLIB_AAS_MOVE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_move.c"
BOTLIB_AAS_OPTIMIZE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_optimize.c"
BOTLIB_AAS_REACH = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_reach.c"
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


def _assert_function_row(functions_csv: str, address: str, size: int) -> None:
	row = f"FUN_00{address.lower()},00{address.lower()},{size},0,unknown"
	assert row in functions_csv


def test_reachability_generation_aliases_and_ghidra_rows_match_retail() -> None:
	aliases = _aliases()
	functions_csv = _read(QL_STEAM_FUNCTIONS)
	hlil = _read(QL_STEAM_HLIL_PART03)

	expected_aliases = {
		"4881F0": "AAS_ClientMovementHitBBox",
		"488240": "AAS_HorizontalVelocityForJump",
		"488340": "AAS_JumpReachRunStart",
		"488430": "AAS_Optimize",
		"488450": "AAS_FaceArea",
		"4885A0": "AAS_AreaVolume",
		"488AB0": "AAS_SetupReachabilityHeap",
		"488B10": "AAS_AllocReachability",
		"488B50": "AAS_AreaReachability",
		"488B90": "AAS_FaceCenter",
		"488CA0": "AAS_FallDamageDistance",
		"488CF0": "AAS_FallDelta",
		"488D30": "AAS_MaxJumpDistance",
		"488D80": "AAS_AreaCrouch",
		"488DB0": "AAS_AreaSwim",
		"488DE0": "AAS_AreaLava",
		"488E00": "AAS_AreaSlime",
		"488E20": "AAS_ReachabilityExists",
		"491750": "AAS_StoreReachability",
		"491B60": "AAS_BestReachableLinkArea",
		"492100": "AAS_SetWeaponJumpAreaFlags",
		"492570": "AAS_InitReachability",
	}
	expected_sizes = {
		"4881F0": 75,
		"488240": 242,
		"488340": 239,
		"488430": 17,
		"488450": 329,
		"4885A0": 246,
		"488AB0": 75,
		"488B10": 50,
		"488B50": 57,
		"488B90": 257,
		"488CA0": 68,
		"488CF0": 61,
		"488D30": 67,
		"488D80": 37,
		"488DB0": 34,
		"488DE0": 31,
		"488E00": 31,
		"488E20": 44,
		"491750": 230,
		"491B60": 115,
		"492100": 1126,
		"492570": 126,
	}

	for address, name in expected_aliases.items():
		assert aliases[f"sub_{address}"] == name
		assert f"00{address.lower()}    " in hlil
		assert f"sub_{address.lower()}" in hlil
		_assert_function_row(functions_csv, address, expected_sizes[address])


def test_retail_aas_optimize_is_non_bspc_stub_with_bspc_optimizer_retained() -> None:
	source = _read(BOTLIB_AAS_OPTIMIZE)
	hlil = _read(QL_STEAM_HLIL_PART03)

	optimize = _extract_function_block(source, "void AAS_Optimize(void)")

	assert "#ifndef BSPC" in optimize
	assert 'botimport.Print(PRT_MESSAGE, "skipped AAS data optimization.\\n");' in optimize
	assert "#else" in optimize
	assert "AAS_OptimizeAlloc(&optimized);" in optimize
	assert "AAS_OptimizeArea(&optimized, i);" in optimize
	assert "AAS_OptimizeStore(&optimized);" in optimize
	assert 'botimport.Print(PRT_MESSAGE, "AAS data optimized.\\n");' in optimize
	assert "#endif" in optimize

	assert "00488430    int32_t sub_488430()" in hlil
	assert 'return data_16dd800(1, "skipped AAS data optimization.\\n")' in hlil


def test_aas_movement_jump_helpers_match_retail_shape() -> None:
	source = _read(BOTLIB_AAS_MOVE)
	hlil = _read(QL_STEAM_HLIL_PART03)

	hit_bbox = _extract_function_block(
		source,
		"int AAS_ClientMovementHitBBox(struct aas_clientmove_s *move",
	)
	horizontal_velocity = _extract_function_block(
		source,
		"int AAS_HorizontalVelocityForJump(float zvel, vec3_t start, vec3_t end, float *velocity)",
	)
	jump_run_start = _extract_function_block(
		source,
		"void AAS_JumpReachRunStart(aas_reachability_t *reach, vec3_t runstart)",
	)

	assert "return AAS_ClientMovementPrediction(move, entnum, origin, presencetype, onground," in hit_bbox
	assert "frametime, SE_HITBOUNDINGBOX, 0," in hit_bbox
	assert "maxjump = 0.5 * phys_gravity * (zvel / phys_gravity) * (zvel / phys_gravity);" in horizontal_velocity
	assert "if (height2fall < 0)" in horizontal_velocity
	assert "if ( (t + zvel / phys_gravity) == 0.0f )" in horizontal_velocity
	assert "if (*velocity > phys_maxvelocity)" in horizontal_velocity
	assert "hordir[0] = reach->start[0] - reach->end[0];" in jump_run_start
	assert "VectorScale(hordir, 400, cmdmove);" in jump_run_start
	assert "AAS_PredictClientMovement(&move, -1, start, PRESENCE_NORMAL, qtrue," in jump_run_start
	assert "if (move.stopevent & (SE_ENTERSLIME|SE_ENTERLAVA|SE_HITGROUNDDAMAGE))" in jump_run_start

	assert "004881f0    int32_t sub_4881f0" in hlil
	assert "0x800, 0, arg11, arg12, arg13)" in hlil
	assert "00488240    void sub_488240" in hlil
	assert "data_16de800" in hlil
	assert "00488340    int32_t sub_488340" in hlil
	assert "sub_4872e0(&var_68, 0xffffffff, &var_74, 2, 1" in hlil
	assert "0x7c, 0, &var_8c, &var_98, 0)" in hlil


def test_aas_reachability_support_helpers_match_retail_shape() -> None:
	source = _read(BOTLIB_AAS_REACH)
	hlil = _read(QL_STEAM_HLIL_PART03)

	face_area = _extract_function_block(source, "float AAS_FaceArea(aas_face_t *face)")
	area_volume = _extract_function_block(source, "float AAS_AreaVolume(int areanum)")
	best_link = _extract_function_block(source, "int AAS_BestReachableLinkArea(aas_link_t *areas)")
	setup_heap = _extract_function_block(source, "void AAS_SetupReachabilityHeap(void)")
	alloc_reach = _extract_function_block(source, "aas_lreachability_t *AAS_AllocReachability(void)")
	area_reachability = _extract_function_block(source, "int AAS_AreaReachability(int areanum)")
	face_center = _extract_function_block(source, "void AAS_FaceCenter(int facenum, vec3_t center)")
	fall_distance = _extract_function_block(source, "int AAS_FallDamageDistance(void)")
	fall_delta = _extract_function_block(source, "float AAS_FallDelta(float distance)")
	max_jump_distance = _extract_function_block(source, "float AAS_MaxJumpDistance(float phys_jumpvel)")
	area_crouch = _extract_function_block(source, "int AAS_AreaCrouch(int areanum)")
	area_swim = _extract_function_block(source, "int AAS_AreaSwim(int areanum)")
	area_lava = _extract_function_block(source, "int AAS_AreaLava(int areanum)")
	area_slime = _extract_function_block(source, "int AAS_AreaSlime(int areanum)")
	reachability_exists = _extract_function_block(source, "qboolean AAS_ReachabilityExists(int area1num, int area2num)")

	assert "CrossProduct(d1, d2, cross);" in face_area
	assert "total += 0.5 * VectorLength(cross);" in face_area
	assert "d = -(DotProduct (corner, plane->normal) - plane->dist);" in area_volume
	assert "volume /= 3;" in area_volume
	assert "if (AAS_AreaGrounded(link->areanum) || AAS_AreaSwim(link->areanum))" in best_link
	assert "if (link->areanum) return link->areanum;" in best_link
	assert "if (AAS_AreaReachability(link->areanum))" in best_link
	assert "AAS_MAX_REACHABILITYSIZE * sizeof(aas_lreachability_t)" in setup_heap
	assert "reachabilityheap[AAS_MAX_REACHABILITYSIZE-1].next = NULL;" in setup_heap
	assert "nextreachability = reachabilityheap;" in setup_heap
	assert 'if (!nextreachability->next) AAS_Error("AAS_MAX_REACHABILITYSIZE");' in alloc_reach
	assert "numlreachabilities++;" in alloc_reach
	assert 'AAS_Error("AAS_AreaReachability: areanum %d out of range", areanum);' in area_reachability
	assert "return aasworld.areasettings[areanum].numreachableareas;" in area_reachability
	assert "VectorAdd(center, aasworld.vertexes[edge->v[0]], center);" in face_center
	assert "scale = 0.5 / face->numedges;" in face_center
	assert "maxzvelocity = sqrt(30 * 10000);" in fall_distance
	assert "return 0.5 * gravity * t * t;" in fall_distance
	assert "t = sqrt(fabs(distance) * 2 / gravity);" in fall_delta
	assert "return delta * delta * 0.0001;" in fall_delta
	assert "t = sqrt(aassettings.rs_maxjumpfallheight / (0.5 * phys_gravity));" in max_jump_distance
	assert "return phys_maxvelocity * (t + phys_jumpvel / phys_gravity);" in max_jump_distance
	assert "if (!(aasworld.areasettings[areanum].presencetype & PRESENCE_NORMAL)) return qtrue;" in area_crouch
	assert "if (aasworld.areasettings[areanum].areaflags & AREA_LIQUID) return qtrue;" in area_swim
	assert "return (aasworld.areasettings[areanum].contents & AREACONTENTS_LAVA);" in area_lava
	assert "return (aasworld.areasettings[areanum].contents & AREACONTENTS_SLIME);" in area_slime
	assert "for (r = areareachability[area1num]; r; r = r->next)" in reachability_exists
	assert "if (r->areanum == area2num) return qtrue;" in reachability_exists

	assert "00488450    long double sub_488450" in hlil
	assert "sub_488450(eax_20)" in hlil
	assert "004885a0    long double sub_4885a0" in hlil
	assert "return fconvert.t(fconvert.s(fconvert.t(arg1) / fconvert.t(3.0)))" in hlil
	assert "00488ab0    char* sub_488ab0" in hlil
	assert "sub_4a89d0(0x300000)" in hlil
	assert "00488b10    void* sub_488b10" in hlil
	assert 'sub_4861a0("AAS_MAX_REACHABILITYSIZE")' in hlil
	assert "00488b90    float sub_488b90" in hlil
	assert "fconvert.t(0.5) / float.t(*edi)" in hlil
	assert "00488ca0    int32_t sub_488ca0" in hlil
	assert "00488d80    uint32_t sub_488d80" in hlil
	assert "00488e20    int32_t sub_488e20" in hlil


def test_aas_reachability_store_and_init_pipeline_match_retail_shape() -> None:
	source = _read(BOTLIB_AAS_REACH)
	hlil = _read(QL_STEAM_HLIL_PART03)

	store = _extract_function_block(source, "void AAS_StoreReachability(void)")
	continue_init = _extract_function_block(source, "int AAS_ContinueInitReachability(float time)")
	init = _extract_function_block(source, "void AAS_InitReachability(void)")
	set_weapon_flags = _extract_function_block(source, "void AAS_SetWeaponJumpAreaFlags(void)")

	assert "aasworld.reachability = (aas_reachability_t *) GetClearedMemory((numlreachabilities + 10)" in store
	assert "aasworld.reachabilitysize = 1;" in store
	assert "areasettings->firstreachablearea = aasworld.reachabilitysize;" in store
	assert "reach->areanum = lreach->areanum;" in store
	assert "reach->traveltime = lreach->traveltime;" in store
	assert "aasworld.reachabilitysize += areasettings->numreachableareas;" in store

	assert "if (AAS_Reachability_Swim(i, j)) continue;" in continue_init
	assert "if (AAS_Reachability_Step_Barrier_WaterJump_WalkOffLedge(i, j)) continue;" in continue_init
	assert "if (AAS_Reachability_Ladder(i, j)) continue;" in continue_init
	assert "if (AAS_Reachability_Jump(i, j)) continue;" in continue_init
	assert "if (calcgrapplereach) AAS_Reachability_Grapple(i, j);" in continue_init
	assert "AAS_Reachability_WeaponJump(i, j);" in continue_init
	assert "AAS_Reachability_WalkOffLedge(i);" in continue_init
	assert "AAS_Reachability_JumpPad();" in continue_init
	assert "AAS_Reachability_Teleport();" in continue_init
	assert "AAS_Reachability_Elevator();" in continue_init
	assert "AAS_Reachability_FuncBobbing();" in continue_init
	assert "AAS_StoreReachability();" in continue_init
	assert "AAS_ShutDownReachabilityHeap();" in continue_init

	assert 'if (!((int)LibVarGetValue("forcereachability")))' in init
	assert 'calcgrapplereach = LibVarGetValue("grapplereach");' in init
	assert "aasworld.savefile = qtrue;" in init
	assert "aasworld.numreachabilityareas = 1;" in init
	assert "AAS_SetupReachabilityHeap();" in init
	assert "aasworld.numareas * sizeof(aas_lreachability_t *)" in init
	assert "AAS_SetWeaponJumpAreaFlags();" in init

	assert '!strcmp(classname, "item_armor_body")' in set_weapon_flags
	assert '!strcmp(classname, "item_health_mega")' in set_weapon_flags
	assert '!strcmp(classname, "weapon_rocketlauncher")' in set_weapon_flags
	assert "aasworld.areasettings[areanum].areaflags |= AREA_WEAPONJUMP;" in set_weapon_flags
	assert 'botimport.Print(PRT_MESSAGE, "%d weapon jump areas\\n", weaponjumpareas);' in set_weapon_flags

	assert "00491750    int32_t sub_491750" in hlil
	assert "data_16de964 = sub_4a89d0((data_16de78c + 0xa) * 0x2c)" in hlil
	assert "00491b60    int32_t sub_491b60" in hlil
	assert "(*(edx + result * 0x1c + 4) & 5) != 0" in hlil
	assert "00491840    int32_t sub_491840" in hlil
	assert "sub_488e50(var_24) == 0" in hlil
	assert "x87control = sub_48bd40()" in hlil
	assert "00492100    int32_t sub_492100" in hlil
	assert '"item_armor_body"' in hlil
	assert '"weapon_rocketlauncher"' in hlil
	assert "00492570    void sub_492570" in hlil
	assert 'sub_4a8680("forcereachability")' in hlil
	assert 'sub_4a8680("grapplereach")' in hlil
	assert "return sub_492100() __tailcall" in hlil
