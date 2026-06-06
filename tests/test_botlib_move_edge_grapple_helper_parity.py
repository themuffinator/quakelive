from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOTLIB_AAS_MOVE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_move.c"
BOTLIB_AAS_REACH = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_reach.c"
BOTLIB_AI_MOVE = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_move.c"
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


def test_botlib_move_edge_and_grapple_helper_aliases_match_retail_references() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]
	functions = _read(QL_STEAM_FUNCTIONS)
	hlil = _read(QL_STEAM_HLIL_PART03)

	expected_aliases = {
		"48B010": "VectorDistance",
		"48B060": "VectorBetweenVectors",
		"49FBC0": "AngleDiff",
		"4A3C80": "GrappleState",
		"4A3D40": "BotResetGrapple",
	}
	for address, name in expected_aliases.items():
		assert aliases[f"sub_{address}"] == name

	for row in (
		"FUN_0048b010,0048b010,77,0,unknown",
		"FUN_0048b060,0048b060,115,0,unknown",
		"FUN_0049fbc0,0049fbc0,97,0,unknown",
		"FUN_004a3c80,004a3c80,182,0,unknown",
		"FUN_004a3d40,004a3d40,159,0,unknown",
		"FUN_00486f40,00486f40,27,0,unknown",
	):
		assert row in functions

	for evidence in (
		"0048b010    long double sub_48b010(float* arg1, float arg2)",
		"0048b020  float var_10 = fconvert.s(fconvert.t(*eax) - fconvert.t(*arg1))",
		"0048b05c  return fconvert.t(fconvert.s(x87_r7_6 * x87_r7_6 + x87_r6 * x87_r6 + x87_r5 * x87_r5))",
		"0048b060    int32_t sub_48b060(float* arg1, float* arg2, float* arg3)",
		"0048b0ad  long double x87_r7_14 = fconvert.t(fconvert.s(fconvert.t(arg1[1]) - fconvert.t(arg3[1])))",
		"0048b0cc  return 1",
		"0049fbc0    long double sub_49fbc0(float arg1, float arg2)",
		"0049fbd1  arg1 = fconvert.s(x87_r7 - x87_r5)",
		"0049fc1c          return fconvert.t(fconvert.s(result + fconvert.t(360.0)))",
		"004a3c80    int32_t sub_4a3c80(void* arg1)",
		"004a3c9a  if ((*(arg1 + 0x60) & 0x40) != 0)",
		"004a3cbf  for (int32_t i = sub_485450(0); i != 0; i = sub_485450(i))",
		"004a3d40    void sub_4a3d40(void* arg1)",
		"004a3d5c  sub_494bb0(*(arg1 + 0x4c), &var_34)",
		"004a3dab              sub_4a7940(*(arg1 + 0x28), *(data_16de0e4 + 4))",
		"004a3db5          *(arg1 + 0x60) &= 0xffffff7f",
	):
		assert evidence in hlil


def test_botlib_aas_edge_math_helpers_match_source_and_retail_usage() -> None:
	reach = _read(BOTLIB_AAS_REACH)
	hlil = _read(QL_STEAM_HLIL_PART03)

	vector_distance = _extract_function_block(reach, "float VectorDistance(vec3_t v1, vec3_t v2)")
	vector_between = _extract_function_block(reach, "int VectorBetweenVectors(vec3_t v, vec3_t v1, vec3_t v2)")
	closest_edges = _extract_function_block(
		reach,
		"float AAS_ClosestEdgePoints(vec3_t v1, vec3_t v2, vec3_t v3, vec3_t v4,",
	)

	assert "VectorSubtract(v2, v1, dir);" in vector_distance
	assert "return VectorLength(dir);" in vector_distance

	assert "VectorSubtract(v, v1, dir1);" in vector_between
	assert "VectorSubtract(v, v2, dir2);" in vector_between
	assert "return (DotProduct(dir1, dir2) <= 0);" in vector_between

	for expected in (
		"if (VectorBetweenVectors(p1, v3, v4))",
		"dist = VectorDistance(v1, p1);",
		"if (VectorBetweenVectors(p2, v3, v4))",
		"dist = VectorDistance(v2, p2);",
		"if (VectorBetweenVectors(p3, v1, v2))",
		"dist = VectorDistance(v3, p3);",
		"if (VectorBetweenVectors(p4, v1, v2))",
		"dist = VectorDistance(v4, p4);",
		"dist = VectorDistance(v1, v3);",
		"dist = VectorDistance(v2, v4);",
	):
		assert expected in closest_edges

	assert "0048b0e0    long double sub_48b0e0" in hlil
	assert "fVar8 = (float10)FUN_0048b010(param_7,param_1);" in _read(
		REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "quakelive_steam" / "decompile_top_functions.c"
	)
	assert "uVar10 = FUN_0048b060(&local_1c,param_3,param_4);" in _read(
		REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "quakelive_steam" / "decompile_top_functions.c"
	)


def test_botlib_angle_and_grapple_helpers_match_source_and_retail_usage() -> None:
	move = _read(BOTLIB_AI_MOVE)
	hlil = _read(QL_STEAM_HLIL_PART03)

	angle_diff = _extract_function_block(move, "float AngleDiff(float ang1, float ang2)")
	grapple_state = _extract_function_block(move, "int GrappleState(bot_movestate_t *ms, aas_reachability_t *reach)")
	reset_grapple = _extract_function_block(move, "void BotResetGrapple(bot_movestate_t *ms)")
	travel_grapple = _extract_function_block(
		move,
		"bot_moveresult_t BotTravel_Grapple(bot_movestate_t *ms, aas_reachability_t *reach)",
	)
	travel_rocket = _extract_function_block(
		move,
		"bot_moveresult_t BotTravel_RocketJump(bot_movestate_t *ms, aas_reachability_t *reach)",
	)
	travel_bfg = _extract_function_block(
		move,
		"bot_moveresult_t BotTravel_BFGJump(bot_movestate_t *ms, aas_reachability_t *reach)",
	)
	move_to_goal = _extract_function_block(
		move,
		"void BotMoveToGoal(bot_moveresult_t *result, int movestate, bot_goal_t *goal, int travelflags)",
	)

	assert "diff = ang1 - ang2;" in angle_diff
	assert "if (diff > 180.0) diff -= 360.0;" in angle_diff
	assert "if (diff < -180.0) diff += 360.0;" in angle_diff
	assert "return diff;" in angle_diff

	assert "if (ms->moveflags & MFL_GRAPPLEPULL)" in grapple_state
	assert "return 2;" in grapple_state
	assert "for (i = AAS_NextEntity(0); i; i = AAS_NextEntity(i))" in grapple_state
	assert "if (AAS_EntityType(i) == (int) entitytypemissile->value)" in grapple_state
	assert "AAS_EntityInfo(i, &entinfo);" in grapple_state
	assert "if (entinfo.weapon == (int) weapindex_grapple->value)" in grapple_state
	assert "return 1;" in grapple_state
	assert "return 0;" in grapple_state

	assert "AAS_ReachabilityFromNum(ms->lastreachnum, &reach);" in reset_grapple
	assert "if ((reach.traveltype & TRAVELTYPE_MASK) != TRAVEL_GRAPPLEHOOK)" in reset_grapple
	assert "if ((ms->moveflags & MFL_ACTIVEGRAPPLE) || ms->grapplevisible_time)" in reset_grapple
	assert "EA_Command(ms->client, cmd_grappleoff->string);" in reset_grapple
	assert "ms->moveflags &= ~MFL_ACTIVEGRAPPLE;" in reset_grapple
	assert "ms->grapplevisible_time = 0;" in reset_grapple

	assert "state = GrappleState(ms, reach);" in travel_grapple
	assert "fabs(AngleDiff(result.ideal_viewangles[0], ms->viewangles[0])) < 2" in travel_grapple
	assert "fabs(AngleDiff(result.ideal_viewangles[1], ms->viewangles[1])) < 2" in travel_grapple
	assert "ms->moveflags |= MFL_ACTIVEGRAPPLE;" in travel_grapple
	assert "ms->moveflags |= MFL_GRAPPLERESET;" in travel_grapple
	assert "fabs(AngleDiff(result.ideal_viewangles[0], ms->viewangles[0])) < 5" in travel_rocket
	assert "fabs(AngleDiff(result.ideal_viewangles[1], ms->viewangles[1])) < 5" in travel_rocket
	assert "fabs(AngleDiff(result.ideal_viewangles[0], ms->viewangles[0])) < 5" in travel_bfg
	assert "fabs(AngleDiff(result.ideal_viewangles[1], ms->viewangles[1])) < 5" in travel_bfg
	assert "BotResetGrapple(ms);" in move_to_goal
	assert "case TRAVEL_GRAPPLEHOOK: *result = BotTravel_Grapple(ms, &reach); break;" in move_to_goal

	assert "004a3e97      int32_t eax_7 = sub_4a3c80(arg2)" in hlil
	assert "004a40b0      fabs(sub_49fbc0(fconvert.s(fconvert.t(arg1[0xa])), fconvert.s(fconvert.t(arg2[0xd]))))" in hlil
	assert "004a40db          fabs(sub_49fbc0(fconvert.s(fconvert.t(arg1[0xb]))," in hlil
	assert "004a4ae5  st0, eax_5 = sub_4a3d40(ebx)" in hlil


def test_botlib_weapon_jump_wrappers_remain_folded_and_unpromoted() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]
	aas_move = _read(BOTLIB_AAS_MOVE)
	hlil = _read(QL_STEAM_HLIL_PART03)

	rocket_wrapper = _extract_function_block(aas_move, "float AAS_RocketJumpZVelocity(vec3_t origin)")
	bfg_wrapper = _extract_function_block(aas_move, "float AAS_BFGJumpZVelocity(vec3_t origin)")

	assert "sub_486F40" not in aliases
	assert "return AAS_WeaponJumpZVelocity(origin, 120);" in rocket_wrapper
	assert "return AAS_WeaponJumpZVelocity(origin, 120);" in bfg_wrapper
	assert "00486f40    int80_t sub_486f40(float* arg1)" in hlil
	assert "00486f5a  return sub_486d40(arg1, fconvert.s(fconvert.t(120f)))" in hlil
	assert aliases["sub_486D40"] == "AAS_WeaponJumpZVelocity"
