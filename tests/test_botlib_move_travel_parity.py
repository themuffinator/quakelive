import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

BOTLIB_AI_MOVE = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_move.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_H = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
SERVER_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SERVER_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"
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


def _extract_function_block(source: str, signature: str, *, use_last: bool = False) -> str:
	start = source.rfind(signature) if use_last else source.find(signature)
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


def test_botlib_move_helper_aliases_and_ghidra_rows_match_retail() -> None:
	aliases = _aliases()
	functions_csv = _read(QL_STEAM_FUNCTIONS)
	hlil = _read(QL_STEAM_HLIL_PART03)

	expected_aliases = {
		"4A00B0": "BotOnMover",
		"4A0270": "MoverDown",
		"4A0490": "BotOnTopOfEntity",
		"4A0540": "BotAddToAvoidReach",
		"4A0600": "DistanceFromLineSquared",
		"4A0A50": "BotGetReachabilityToGoal",
		"4A0C00": "BotAddToTarget",
		"4A0F10": "BotVisible",
		"4A10E0": "MoverBottomCenter",
		"4A11A0": "BotGapDistance",
		"4A1340": "BotCheckBarrierJump",
		"4A18E0": "BotCheckBlocked",
		"4A1AA0": "BotTravel_Walk",
		"4A1C20": "BotTravel_Crouch",
		"4A1CD0": "BotTravel_BarrierJump",
		"4A1DC0": "BotFinishTravel_BarrierJump",
		"4A1E70": "BotTravel_Swim",
		"4A1F30": "BotTravel_WaterJump",
		"4A2040": "BotFinishTravel_WaterJump",
		"4A21A0": "BotTravel_WalkOffLedge",
		"4A2380": "BotAirControl",
		"4A24E0": "BotFinishTravel_WalkOffLedge",
		"4A2620": "BotTravel_Jump",
		"4A2900": "BotFinishTravel_Jump",
		"4A2A00": "BotTravel_Ladder",
		"4A2AD0": "BotTravel_Teleport",
		"4A3110": "BotFinishTravel_Elevator",
		"4A3260": "BotFuncBobStartEnd",
	}
	expected_sizes = {
		"4A00B0": 445,
		"4A0270": 154,
		"4A0490": 165,
		"4A0540": 178,
		"4A0600": 359,
		"4A0A50": 418,
		"4A0C00": 204,
		"4A0F10": 88,
		"4A10E0": 191,
		"4A11A0": 408,
		"4A1340": 453,
		"4A18E0": 439,
		"4A1AA0": 384,
		"4A1C20": 166,
		"4A1CD0": 239,
		"4A1DC0": 173,
		"4A1E70": 178,
		"4A1F30": 257,
		"4A2040": 345,
		"4A21A0": 470,
		"4A2380": 341,
		"4A24E0": 320,
		"4A2620": 726,
		"4A2900": 241,
		"4A2A00": 204,
		"4A2AD0": 229,
		"4A3110": 323,
		"4A3260": 425,
	}

	for address, name in expected_aliases.items():
		assert aliases[f"sub_{address}"] == name
		assert f"00{address.lower()}    " in hlil
		assert f"sub_{address.lower()}" in hlil
		_assert_function_row(functions_csv, address, expected_sizes[address])

	assert aliases["sub_4A21A0"] == "BotTravel_WalkOffLedge"
	assert aliases["sub_4A24E0"] == "BotFinishTravel_WalkOffLedge"
	assert aliases["sub_4A2620"] == "BotTravel_Jump"


def test_botlib_reachability_view_and_visibility_helpers_match_retail_shape() -> None:
	source = _read(BOTLIB_AI_MOVE)
	hlil = _read(QL_STEAM_HLIL_PART03)

	on_mover = _extract_function_block(source, "int BotOnMover(vec3_t origin, int entnum, aas_reachability_t *reach)")
	mover_down = _extract_function_block(source, "int MoverDown(aas_reachability_t *reach)")
	on_top = _extract_function_block(source, "int BotOnTopOfEntity(bot_movestate_t *ms)")
	add_avoid = _extract_function_block(source, "void BotAddToAvoidReach(bot_movestate_t *ms, int number, float avoidtime)")
	reach_goal = _extract_function_block(
		source,
		"int BotGetReachabilityToGoal(vec3_t origin, int areanum",
	)
	add_target = _extract_function_block(
		source,
		"int BotAddToTarget(vec3_t start, vec3_t end, float maxdist, float *dist, vec3_t target)",
	)
	view_target = _extract_function_block(
		source,
		"int BotMovementViewTarget(int movestate, bot_goal_t *goal, int travelflags, float lookahead, vec3_t target)",
	)
	visible = _extract_function_block(source, "int BotVisible(int ent, vec3_t eye, vec3_t target)")
	predict_visible = _extract_function_block(
		source,
		"int BotPredictVisiblePosition(vec3_t origin, int areanum, bot_goal_t *goal, int travelflags, vec3_t target)",
	)

	assert "AAS_BSPModelMinsMaxsOrigin(modelnum, angles, mins, maxs, NULL);" in on_mover
	assert "if (!AAS_OriginOfMoverWithModelNum(modelnum, modelorigin))" in on_mover
	assert "if (origin[i] > modelorigin[i] + maxs[i] + 16) return qfalse;" in on_mover
	assert "AAS_Trace(org, boxmins, boxmaxs, end, entnum, CONTENTS_SOLID|CONTENTS_PLAYERCLIP)" in on_mover
	assert "AAS_EntityModelNum(trace.ent) == modelnum" in on_mover

	assert "origin[2] + maxs[2] < reach->start[2]" in mover_down
	assert "AAS_PresenceTypeBoundingBox(ms->presencetype, mins, maxs);" in on_top
	assert "trace.ent != ENTITYNUM_WORLD && trace.ent != ENTITYNUM_NONE" in on_top
	assert "if (ms->avoidreach[i] == number)" in add_avoid
	assert "ms->avoidreachtimes[i] = AAS_Time() + avoidtime;" in add_avoid
	assert "ms->avoidreachtries[i] = 1;" in add_avoid

	assert "if (!areanum) return 0;" in reach_goal
	assert "AAS_AreaDoNotEnter(areanum) || AAS_AreaDoNotEnter(goal->areanum)" in reach_goal
	assert "for (reachnum = AAS_NextAreaReachability(areanum, 0); reachnum;" in reach_goal
	assert "if (lastgoalareanum == goal->areanum && reach.areanum == lastareanum) continue;" in reach_goal
	assert "if (!BotValidTravel(origin, &reach, movetravelflags)) continue;" in reach_goal
	assert "t = AAS_AreaTravelTimeToGoalArea(reach.areanum, reach.end, goal->areanum, travelflags);" in reach_goal
	assert "if (BotAvoidSpots(origin, &reach, avoidspots, numavoidspots))" in reach_goal
	assert "t += reach.traveltime;" in reach_goal

	assert "VectorSubtract(end, start, dir);" in add_target
	assert "curdist = VectorNormalize(dir);" in add_target
	assert "if (*dist + curdist < maxdist)" in add_target
	assert "if ((reach.traveltype & TRAVELTYPE_MASK) == TRAVEL_TELEPORT) return qtrue;" in view_target
	assert "if ((reach.traveltype & TRAVELTYPE_MASK) == TRAVEL_ROCKETJUMP) return qtrue;" in view_target
	assert "if ((reach.traveltype & TRAVELTYPE_MASK) == TRAVEL_BFGJUMP) return qtrue;" in view_target
	assert "(reach.traveltype & TRAVELTYPE_MASK) != TRAVEL_JUMPPAD" in view_target
	assert "(reach.traveltype & TRAVELTYPE_MASK) != TRAVEL_ELEVATOR" in view_target
	assert "(reach.traveltype & TRAVELTYPE_MASK) != TRAVEL_FUNCBOB" in view_target
	assert "reachnum = BotGetReachabilityToGoal(reach.end, reach.areanum," in view_target
	assert "trace = AAS_Trace(eye, NULL, NULL, target, ent, CONTENTS_SOLID|CONTENTS_PLAYERCLIP);" in visible
	assert "for (i = 0; i < 20 && (areanum != goal->areanum); i++)" in predict_visible
	assert "if (BotVisible(goal->entitynum, goal->origin, reach.start))" in predict_visible
	assert "if (BotVisible(goal->entitynum, goal->origin, reach.end))" in predict_visible

	assert "004a00b0    int32_t sub_4a00b0" in hlil
	assert 'data_16dd800(1, "no entity with model %d\\n", edi_1)' in hlil
	assert "004a0a50    int32_t* sub_4a0a50" in hlil
	assert "for (int32_t* i = sub_494c10(arg2, 0); i != 0; i = sub_494c10(arg2, i))" in hlil
	assert "int32_t eax_14 = sub_494830(var_34, &var_1c, *(arg8 + 0xc), arg9)" in hlil
	assert "int32_t eax_17 = sub_4a0770(arg1, &var_34, arg11, arg12)" in hlil
	assert "004a0cd0    int32_t sub_4a0cd0" in hlil
	assert "sub_4a0c00(&var_4c, &var_28, fconvert.s(fconvert.t(arg4)), &var_3c, arg5)" in hlil
	assert "eax_10 == 0xa || eax_10 == 0xc || eax_10 == 0xd" in hlil
	assert "004a0f70    int32_t sub_4a0f70" in hlil
	assert "if (ebx_1 s>= 0x14)" in hlil


def test_botlib_direct_movement_and_travel_methods_match_retail_shape() -> None:
	source = _read(BOTLIB_AI_MOVE)
	hlil = _read(QL_STEAM_HLIL_PART03)

	gap_distance = _extract_function_block(source, "float BotGapDistance(vec3_t origin, vec3_t hordir, int entnum)")
	barrier_jump = _extract_function_block(source, "int BotCheckBarrierJump(bot_movestate_t *ms, vec3_t dir, float speed)")
	walk_direction = _extract_function_block(source, "int BotWalkInDirection(bot_movestate_t *ms, vec3_t dir, float speed, int type)")
	move_direction = _extract_function_block(source, "int BotMoveInDirection(int movestate, vec3_t dir, float speed, int type)")
	check_blocked = _extract_function_block(
		source,
		"void BotCheckBlocked(bot_movestate_t *ms, vec3_t dir, int checkbottom, bot_moveresult_t *result)",
	)
	air_control = _extract_function_block(
		source,
		"int BotAirControl(vec3_t origin, vec3_t velocity, vec3_t goal, vec3_t dir, float *speed)",
	)

	assert "end[2] -= 60;" in gap_distance
	assert "for (dist = 8; dist <= 100; dist += 8)" in gap_distance
	assert "end[2] -= 48 + sv_maxbarrier->value;" in gap_distance
	assert "trace.endpos[2] < startz - sv_maxstep->value - 8" in gap_distance
	assert "EA_Jump(ms->client);" in barrier_jump
	assert "ms->moveflags |= MFL_BARRIERJUMP;" in barrier_jump
	assert "AAS_PredictClientMovement(&move, ms->entitynum, origin, presencetype, qtrue," in walk_direction
	assert "stopevent = SE_HITGROUND|SE_HITGROUNDDAMAGE|" in walk_direction
	assert "if (type & MOVE_CROUCH) EA_Crouch(ms->client);" in walk_direction
	assert "if (AAS_Swimming(ms->origin))" in move_direction
	assert "return BotSwimInDirection(ms, dir, speed, type);" in move_direction
	assert "return BotWalkInDirection(ms, dir, speed, type);" in move_direction
	assert "AAS_PresenceTypeBoundingBox(ms->presencetype, mins, maxs);" in check_blocked
	assert "result->flags |= MOVERESULT_ONTOPOFOBSTACLE;" in check_blocked
	assert "for (i = 0; i < 50; i++)" in air_control
	assert "vel[2] -= sv_gravity->value * 0.01;" in air_control
	assert "*speed = 400 - (400 - 13 * dist);" in air_control

	assert "004a11a0    long double sub_4a11a0" in hlil
	assert "sub_4957f0(&var_78, &var_20, &var_14, 4, arg3)" in hlil
	assert "004a1340    void sub_4a1340" in hlil
	assert "sub_488190(&var_98, arg1[9], &var_44, var_9c_1, 1, &var_38, &var_2c" in hlil
	assert "004a17f0    int32_t sub_4a17f0" in hlil
	assert "sub_486cf0(esi)" in hlil
	assert "sub_4a1510(esi, arg2, fconvert.s(fconvert.t(arg3)), arg4)" in hlil
	assert "004a18e0    void* sub_4a18e0" in hlil
	assert "*(arg4 + 8) = 1" in hlil
	assert "*(result + 0x14) |= 0x20" in hlil


def test_botlib_travel_dispatch_and_finish_aliases_match_retail_shape() -> None:
	source = _read(BOTLIB_AI_MOVE)
	hlil = _read(QL_STEAM_HLIL_PART03)

	walkoff = _extract_function_block(
		source,
		"bot_moveresult_t BotTravel_WalkOffLedge(bot_movestate_t *ms, aas_reachability_t *reach)",
	)
	finish_walkoff = _extract_function_block(
		source,
		"bot_moveresult_t BotFinishTravel_WalkOffLedge(bot_movestate_t *ms, aas_reachability_t *reach)",
	)
	jump = _extract_function_block(
		source,
		"bot_moveresult_t BotTravel_Jump(bot_movestate_t *ms, aas_reachability_t *reach)",
		use_last=True,
	)
	finish_jump = _extract_function_block(
		source,
		"bot_moveresult_t BotFinishTravel_Jump(bot_movestate_t *ms, aas_reachability_t *reach)",
	)
	ladder = _extract_function_block(
		source,
		"bot_moveresult_t BotTravel_Ladder(bot_movestate_t *ms, aas_reachability_t *reach)",
	)
	teleport = _extract_function_block(
		source,
		"bot_moveresult_t BotTravel_Teleport(bot_movestate_t *ms, aas_reachability_t *reach)",
	)
	elevator_finish = _extract_function_block(
		source,
		"bot_moveresult_t BotFinishTravel_Elevator(bot_movestate_t *ms, aas_reachability_t *reach)",
	)
	funcbob_start_end = _extract_function_block(
		source,
		"void BotFuncBobStartEnd(aas_reachability_t *reach, vec3_t start, vec3_t end, vec3_t origin)",
	)
	move_to_goal = _extract_function_block(
		source,
		"void BotMoveToGoal(bot_moveresult_t *result, int movestate, bot_goal_t *goal, int travelflags)",
	)

	assert "else if (!AAS_HorizontalVelocityForJump(0, reach->start, reach->end, &speed))" in walkoff
	assert "speed = 100;" in walkoff
	assert "speed = 400 - (256 - 4 * dist);" in walkoff
	assert "BotCheckBlocked(ms, hordir, qtrue, &result);" in walkoff
	assert "VectorMA(reach->end, 16, v, end)" in finish_walkoff
	assert "BotAirControl(ms->origin, ms->velocity, end, hordir, &speed)" in finish_walkoff
	assert "AAS_JumpReachRunStart(reach, runstart);" in jump
	assert "for (dist1 = 0; dist1 < 80; dist1 += 10)" in jump
	assert "if (dist1 < 24) EA_Jump(ms->client);" in jump
	assert "else if (dist1 < 32) EA_DelayedJump(ms->client);" in jump
	assert "EA_Move(ms->client, hordir, 600);" in jump
	assert "ms->jumpreach = ms->lastreachnum;" in jump
	assert "if (!ms->jumpreach) return result;" in finish_jump
	assert "if (DotProduct(hordir, hordir2) < -0.5 && dist < 24) return result;" in finish_jump
	assert "speed = 800;" in finish_jump
	assert "Vector2Angles(viewdir, result.ideal_viewangles);" in ladder
	assert "EA_MoveForward(ms->client);" in ladder
	assert "if (ms->moveflags & MFL_TELEPORTED) return result;" in teleport
	assert "if (dist < 30) EA_Move(ms->client, hordir, 200);" in teleport
	assert "MoverBottomCenter(reach, bottomcenter);" in elevator_finish
	assert "EA_Move(ms->client, bottomdir, 300);" in elevator_finish
	assert "spawnflags = reach->facenum >> 16;" in funcbob_start_end
	assert "if (num0 > 0x00007FFF) num0 |= 0xFFFF0000;" in funcbob_start_end

	assert "case TRAVEL_WALKOFFLEDGE: *result = BotTravel_WalkOffLedge(ms, &reach); break;" in move_to_goal
	assert "case TRAVEL_JUMP: *result = BotTravel_Jump(ms, &reach); break;" in move_to_goal
	assert "case TRAVEL_WALK: *result = BotTravel_Walk(ms, &reach); break;//BotFinishTravel_Walk(ms, &reach); break;" in move_to_goal
	assert "case TRAVEL_WALKOFFLEDGE: *result = BotFinishTravel_WalkOffLedge(ms, &reach); break;" in move_to_goal
	assert "case TRAVEL_JUMP: *result = BotFinishTravel_Jump(ms, &reach); break;" in move_to_goal
	assert "case TRAVEL_ELEVATOR: *result = BotFinishTravel_Elevator(ms, &reach); break;" in move_to_goal
	assert "case TRAVEL_FUNCBOB: *result = BotFinishTravel_FuncBobbing(ms, &reach); break;" in move_to_goal

	assert "004a21a0    void* sub_4a21a0" in hlil
	assert "sub_488240(fconvert.s(float.t(0)), arg3 + 0xc, arg3 + 0x18, &var_24)" in hlil
	assert "004a24e0    int80_t sub_4a24e0" in hlil
	assert "st0_1, eax_3, ecx = sub_4a2380(arg2, &arg2[3], &var_30, &var_14, &var_24)" in hlil
	assert "004a2620    void* sub_4a2620" in hlil
	assert "sub_488340(arg3, &var_20)" in hlil
	assert "sub_4a7a20(arg2[0xa])" in hlil
	assert "arg2[0x19] = arg2[0x13]" in hlil
	assert "004a2900    void sub_4a2900" in hlil
	assert "fconvert.t(800f)" in hlil
	assert "004a2a00    void* sub_4a2a00" in hlil
	assert "sub_4a7af0(arg2[0xa])" in hlil
	assert "004a2ad0    void sub_4a2ad0" in hlil
	assert "fconvert.t(30.0)" in hlil
	assert "004a3110    int32_t sub_4a3110" in hlil
	assert "sub_4a7b70(arg2[0xa], eax_4, fconvert.s(fconvert.t(300f)))" in hlil
	assert "004a3260    int32_t sub_4a3260" in hlil
	assert '"BotFuncBobStartEnd: no entity wi' in hlil


def test_botlib_movement_export_and_qagame_import_wiring_still_matches_retail_order() -> None:
	botlib_h = _read(BOTLIB_H)
	be_interface = _read(BOTLIB_INTERFACE)
	sv_game = _read(SERVER_GAME)
	server_imports = _read(SERVER_IMPORTS)
	g_syscalls = _read(GAME_SYSCALLS)

	ai_export = _extract_function_block(botlib_h, "typedef struct ai_export_s")
	init_ai = _extract_function_block(be_interface, "static void Init_AI_Export( ai_export_t *ai )")

	for text in (
		"void\t(*BotMoveToGoal)(struct bot_moveresult_s *result, int movestate, struct bot_goal_s *goal, int travelflags);",
		"int\t\t(*BotMoveInDirection)(int movestate, vec3_t dir, float speed, int type);",
		"int\t\t(*BotReachabilityArea)(vec3_t origin, int testground);",
		"int\t\t(*BotMovementViewTarget)(int movestate, struct bot_goal_s *goal, int travelflags, float lookahead, vec3_t target);",
		"int\t\t(*BotPredictVisiblePosition)(vec3_t origin, int areanum, struct bot_goal_s *goal, int travelflags, vec3_t target);",
		"void\t(*BotAddAvoidSpot)(int movestate, vec3_t origin, float radius, int type);",
	):
		assert text in ai_export

	assert ai_export.index("(*BotMoveToGoal)") < ai_export.index("(*BotMoveInDirection)")
	assert ai_export.index("(*BotResetLastAvoidReach)") < ai_export.index("(*BotReachabilityArea)")
	assert ai_export.index("(*BotReachabilityArea)") < ai_export.index("(*BotMovementViewTarget)")
	assert ai_export.index("(*BotMovementViewTarget)") < ai_export.index("(*BotPredictVisiblePosition)")
	assert ai_export.index("(*BotPredictVisiblePosition)") < ai_export.index("(*BotAllocMoveState)")

	for text in (
		"ai->BotMoveToGoal = BotMoveToGoal;",
		"ai->BotMoveInDirection = BotMoveInDirection;",
		"ai->BotReachabilityArea = BotReachabilityArea;",
		"ai->BotMovementViewTarget = BotMovementViewTarget;",
		"ai->BotPredictVisiblePosition = BotPredictVisiblePosition;",
		"ai->BotAddAvoidSpot = BotAddAvoidSpot;",
	):
		assert text in init_ai

	assert init_ai.index("ai->BotMoveToGoal = BotMoveToGoal;") < init_ai.index(
		"ai->BotMoveInDirection = BotMoveInDirection;"
	)
	assert init_ai.index("ai->BotReachabilityArea = BotReachabilityArea;") < init_ai.index(
		"ai->BotMovementViewTarget = BotMovementViewTarget;"
	)
	assert init_ai.index("ai->BotMovementViewTarget = BotMovementViewTarget;") < init_ai.index(
		"ai->BotPredictVisiblePosition = BotPredictVisiblePosition;"
	)

	assert "botlib_export->ai.BotMoveToGoal( VMA(1), args[2], VMA(3), args[4] );" in sv_game
	assert "return botlib_export->ai.BotMoveInDirection( args[1], VMA(2), VMF(3), args[4] );" in sv_game
	assert "return botlib_export->ai.BotReachabilityArea( VMA(1), args[2] );" in sv_game
	assert "return botlib_export->ai.BotMovementViewTarget( args[1], VMA(2), args[3], VMF(4), VMA(5) );" in sv_game
	assert "return botlib_export->ai.BotPredictVisiblePosition( VMA(1), args[2], VMA(3), args[4], VMA(5) );" in sv_game
	assert "[BOTLIB_AI_MOVE_TO_GOAL] = (ql_import_f)QL_G_trap_BotMoveToGoal," in sv_game
	assert "[BOTLIB_AI_MOVE_IN_DIRECTION] = (ql_import_f)QL_G_trap_BotMoveInDirection," in sv_game
	assert "[BOTLIB_AI_REACHABILITY_AREA] = (ql_import_f)QL_G_trap_BotReachabilityArea," in sv_game
	assert "[BOTLIB_AI_MOVEMENT_VIEW_TARGET] = (ql_import_f)QL_G_trap_BotMovementViewTarget," in sv_game
	assert "[BOTLIB_AI_PREDICT_VISIBLE_POSITION] = (ql_import_f)QL_G_trap_BotPredictVisiblePosition," in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVE_TO_GOAL] = (ql_import_f)QL_G_trap_BotMoveToGoal;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVE_IN_DIRECTION] = (ql_import_f)QL_G_trap_BotMoveInDirection;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_REACHABILITY_AREA] = (ql_import_f)QL_G_trap_BotReachabilityArea;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_MOVEMENT_VIEW_TARGET] = (ql_import_f)QL_G_trap_BotMovementViewTarget;" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_PREDICT_VISIBLE_POSITION] = (ql_import_f)QL_G_trap_BotPredictVisiblePosition;" in sv_game

	assert "G_Import_Syscall( BOTLIB_AI_MOVE_TO_GOAL, result, movestate, goal, travelflags );" in server_imports
	assert "return G_Import_Syscall( BOTLIB_AI_MOVE_IN_DIRECTION, movestate, dir, QL_G_PASSFLOAT(speed), type );" in server_imports
	assert "return G_Import_Syscall( BOTLIB_AI_REACHABILITY_AREA, origin, testground );" in server_imports
	assert "return G_Import_Syscall( BOTLIB_AI_MOVEMENT_VIEW_TARGET, movestate, goal, travelflags, QL_G_PASSFLOAT(lookahead), target );" in server_imports
	assert "return G_Import_Syscall( BOTLIB_AI_PREDICT_VISIBLE_POSITION, origin, areanum, goal, travelflags, target );" in server_imports
	assert "syscall( BOTLIB_AI_MOVE_TO_GOAL, result, movestate, goal, travelflags );" in g_syscalls
	assert "return syscall( BOTLIB_AI_MOVE_IN_DIRECTION, movestate, dir, PASSFLOAT(speed), type );" in g_syscalls
	assert "return syscall( BOTLIB_AI_REACHABILITY_AREA, origin, testground );" in g_syscalls
	assert "return syscall( BOTLIB_AI_MOVEMENT_VIEW_TARGET, movestate, goal, travelflags, PASSFLOAT(lookahead), target );" in g_syscalls
	assert "return syscall( BOTLIB_AI_PREDICT_VISIBLE_POSITION, origin, areanum, goal, travelflags, target );" in g_syscalls
