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
QL_STEAM_HLIL_PART03 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part03.txt"
)
BOTLIB_AAS_MOVE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_move.c"
BOTLIB_AAS_REACH = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_reach.c"
BOTLIB_AI_MOVE = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_move.c"

EXPECTED_LATE_SUPPORT_ALIASES = {
	"4866A0": "AAS_DropToFloor",
	"486A60": "AAS_AgainstLadder",
	"486C20": "AAS_OnGround",
	"486FF0": "AAS_ApplyFriction",
	"487080": "AAS_ClipToBBox",
	"4886A0": "AAS_GetJumpPadInfo",
	"4890E0": "AAS_Reachability_EqualFloorHeight",
	"48EBE0": "AAS_FindFaceReachabilities",
	"4A2BC0": "BotTravel_Elevator",
	"4A3410": "BotTravel_FuncBobbing",
	"4A4640": "BotFinishTravel_WeaponJump",
	"4A4700": "BotTravel_JumpPad",
	"4A47A0": "BotFinishTravel_JumpPad",
	"4A4870": "BotReachabilityTime",
	"4A4910": "BotMoveInGoalArea",
}

EXPECTED_LATE_SUPPORT_SIZES = {
	"4866A0": 156,
	"486A60": 434,
	"486C20": 201,
	"486FF0": 142,
	"487080": 597,
	"4886A0": 1033,
	"4890E0": 1526,
	"48EBE0": 1233,
	"4A2BC0": 1346,
	"4A3410": 1467,
	"4A4640": 186,
	"4A4700": 157,
	"4A47A0": 197,
	"4A4870": 76,
	"4A4910": 314,
}


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


def _function_row(address: str) -> str:
	with FUNCTIONS_CSV.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			if row["entry"] == f"00{address.lower()}":
				return f'{row["name"]},{row["entry"]},{row["size"]},{row["thunk"]},{row["calling_convention"]}'
	raise AssertionError(f"missing function row: {address}")


def test_late_movement_support_aliases_rows_and_hlil_anchors_are_pinned() -> None:
	aliases = _aliases()
	hlil = _read(QL_STEAM_HLIL_PART03)

	for address, name in EXPECTED_LATE_SUPPORT_ALIASES.items():
		assert aliases[f"sub_{address}"] == name
		assert _function_row(address) == (
			f"FUN_00{address.lower()},00{address.lower()},"
			f"{EXPECTED_LATE_SUPPORT_SIZES[address]},0,unknown"
		)
		assert f"00{address.lower()}    " in hlil
		assert f"sub_{address.lower()}" in hlil

	for hlil_anchor in (
		"004866a0    int32_t sub_4866a0(float* arg1, int32_t arg2, int32_t arg3)",
		"00486a60    int32_t sub_486a60(float* arg1)",
		"00486c20    int32_t sub_486c20(float* arg1, int32_t arg2, float* arg3)",
		"00486ff0    int32_t sub_486ff0(float arg1, float arg2, float arg3, float arg4)",
		"00487080    void sub_487080(int32_t* arg1, float* arg2, float* arg3, int32_t arg4, float* arg5, float* arg6)",
		"004886a0    int32_t sub_4886a0(int32_t arg1, float* arg2, float* arg3, float* arg4, float arg5)",
		"004890e0    int32_t sub_4890e0(int16_t arg1 @ x87control, int32_t arg2, int32_t arg3)",
		"0048ebe0    int32_t* sub_48ebe0(float* arg1, int32_t arg2, float arg3, int32_t arg4)",
		"004a2bc0    void* sub_4a2bc0(void* arg1, float* arg2, void* arg3)",
		"004a3410    void* sub_4a3410(void* arg1, float* arg2, void* arg3)",
		"004a4640    void* sub_4a4640(void* arg1, float arg2, void* arg3)",
		"004a4700    void* sub_4a4700(void* arg1, float* arg2, void* arg3)",
		"004a47a0    int80_t sub_4a47a0(void* arg1, float arg2, void* arg3)",
		"004a4870    int32_t sub_4a4870(void* arg1)",
		"004a4910    void* sub_4a4910(void* arg1, float* arg2, float* arg3)",
		"sub_4a4870(var_3b0)",
		"src: sub_4a2bc0(var_3b0, ebx, var_3a8_33), n: 0x34",
		"src: sub_4a3410(var_3b0, ebx, var_3a8_38), n: 0x34",
		"sub_4a4640(var_3b0, var_3ac_52, var_3a8_58), n: 0x34",
		"sub_4a4700(var_3b0, ebx, var_3a8_37), n: 0x34",
	):
		assert hlil_anchor in hlil


def test_aas_movement_physics_helpers_match_source_shape() -> None:
	source = _read(BOTLIB_AAS_MOVE)

	drop_to_floor = _extract_function_block(source, "int AAS_DropToFloor(vec3_t origin")
	against_ladder = _extract_function_block(source, "int AAS_AgainstLadder(vec3_t origin)")
	on_ground = _extract_function_block(source, "int AAS_OnGround(vec3_t origin")
	apply_friction = _extract_function_block(source, "void AAS_ApplyFriction(vec3_t vel")
	clip_to_bbox = _extract_function_block(source, "int AAS_ClipToBBox(aas_trace_t *trace")

	assert "end[2] -= 100;" in drop_to_floor
	assert "trace = AAS_Trace(origin, mins, maxs, end, 0, CONTENTS_SOLID);" in drop_to_floor
	assert "if (trace.startsolid) return qfalse;" in drop_to_floor
	assert "VectorCopy(trace.endpos, origin);" in drop_to_floor

	assert "areanum = AAS_PointAreaNum(org);" in against_ladder
	assert "org[0] += 1;" in against_ladder
	assert "org[1] += 1;" in against_ladder
	assert "if (!(aasworld.areasettings[areanum].areaflags & AREA_LADDER)) return qfalse;" in against_ladder
	assert "if (!(face->faceflags & FACE_LADDER)) continue;" in against_ladder
	assert "plane = &aasworld.planes[face->planenum ^ side];" in against_ladder
	assert "if (abs(DotProduct(plane->normal, origin) - plane->dist) < 3)" in against_ladder
	assert "if (AAS_PointInsideFace(abs(facenum), origin, 0.1f)) return qtrue;" in against_ladder

	assert "end[2] -= 10;" in on_ground
	assert "trace = AAS_TraceClientBBox(origin, end, presencetype, passent);" in on_ground
	assert "if (trace.startsolid) return qfalse;" in on_ground
	assert "if (trace.fraction >= 1.0) return qfalse;" in on_ground
	assert "if (origin[2] - trace.endpos[2] > 10) return qfalse;" in on_ground
	assert "plane = AAS_PlaneFromNum(trace.planenum);" in on_ground
	assert "if (DotProduct(plane->normal, up) < aassettings.phys_maxsteepness) return qfalse;" in on_ground

	assert "speed = sqrt(vel[0] * vel[0] + vel[1] * vel[1]);" in apply_friction
	assert "control = speed < stopspeed ? stopspeed : speed;" in apply_friction
	assert "newspeed = speed - frametime * control * friction;" in apply_friction
	assert "if (newspeed < 0) newspeed = 0;" in apply_friction
	assert "vel[0] *= newspeed;" in apply_friction
	assert "vel[1] *= newspeed;" in apply_friction

	assert "AAS_PresenceTypeBoundingBox(presencetype, bboxmins, bboxmaxs);" in clip_to_bbox
	assert "VectorSubtract(mins, bboxmaxs, absmins);" in clip_to_bbox
	assert "VectorSubtract(maxs, bboxmins, absmaxs);" in clip_to_bbox
	assert "if (start[i] < absmins[i] && end[i] < absmins[i]) return qfalse;" in clip_to_bbox
	assert "front = start[i] - planedist;" in clip_to_bbox
	assert "frac = front / (front-back);" in clip_to_bbox
	assert "trace->fraction = frac;" in clip_to_bbox
	assert "trace->ent = 0;" in clip_to_bbox
	assert "for (j = 0; j < 3; j++) trace->endpos[j] = start[j] + dir[j] * frac;" in clip_to_bbox


def test_reachability_generation_support_helpers_match_source_shape() -> None:
	source = _read(BOTLIB_AAS_REACH)

	jumppad = _extract_function_block(source, "int AAS_GetJumpPadInfo(int ent")
	equal_floor = _extract_function_block(source, "int AAS_Reachability_EqualFloorHeight(int area1num")
	face_reaches = _extract_function_block(
		source,
		"aas_lreachability_t *AAS_FindFaceReachabilities(vec3_t *facepoints",
	)

	assert 'AAS_FloatForBSPEpairKey(ent, "speed", &speed);' in jumppad
	assert "if (!speed) speed = 1000;" in jumppad
	assert 'AAS_ValueForBSPEpairKey(ent, "model", model, MAX_EPAIRKEY);' in jumppad
	assert "AAS_BSPModelMinsMaxsOrigin(modelnum, angles, absmins, absmaxs, origin);" in jumppad
	assert "trace = AAS_TraceClientBBox(teststart, origin, PRESENCE_CROUCH, -1);" in jumppad
	assert 'botimport.Print(PRT_MESSAGE, "trigger_push start solid\\n");' in jumppad
	assert 'AAS_ValueForBSPEpairKey(ent, "target", target, MAX_EPAIRKEY);' in jumppad
	assert 'AAS_ValueForBSPEpairKey(ent2, "targetname", targetname, MAX_EPAIRKEY)' in jumppad
	assert 'botimport.Print(PRT_MESSAGE, "trigger_push without target entity %s\\n", target);' in jumppad
	assert "time = sqrt( height / ( 0.5 * gravity ) );" in jumppad
	assert 'botimport.Print(PRT_MESSAGE, "trigger_push without time\\n");' in jumppad
	assert "forward *= 1.1f;" in jumppad
	assert "velocity[2] = time * gravity;" in jumppad

	assert "if (!AAS_AreaGrounded(area1num) || !AAS_AreaGrounded(area2num)) return qfalse;" in equal_floor
	assert "if (area1->mins[i] > area2->maxs[i] + 10) return qfalse;" in equal_floor
	assert "if (area2->mins[2] > area1->maxs[2]) return qfalse;" in equal_floor
	assert "if (!(face1->faceflags & FACE_GROUND)) continue;" in equal_floor
	assert "if (!(face2->faceflags & FACE_GROUND)) continue;" in equal_floor
	assert "abs(aasworld.edgeindex[face1->firstedge + edgenum1]) !=" in equal_floor
	assert "VectorMA(end, INSIDEUNITS_WALKEND, normal, end);" in equal_floor
	assert "VectorMA(start, INSIDEUNITS_WALKSTART, normal, start);" in equal_floor
	assert "lr.traveltype = TRAVEL_WALK;" in equal_floor
	assert "lreach = AAS_AllocReachability();" in equal_floor
	assert "if (!AAS_AreaCrouch(area1num) && AAS_AreaCrouch(area2num))" in equal_floor
	assert "lreach->traveltime += aassettings.rs_startcrouch;" in equal_floor
	assert "reach_equalfloor++;" in equal_floor

	assert "lreachabilities = NULL;" in face_reaches
	assert "for (i = 1; i < aasworld.numareas; i++)" in face_reaches
	assert "if (!(face->faceflags & FACE_GROUND)) continue;" in face_reaches
	assert "dist = AAS_ClosestEdgePoints(v1, v2, v3, v4, faceplane, plane," in face_reaches
	assert "if (bestdist > 192) continue;" in face_reaches
	assert "VectorMiddle(beststart, beststart2, beststart);" in face_reaches
	assert "VectorMiddle(bestend, bestend2, bestend);" in face_reaches
	assert "if (hordist > 2 * AAS_MaxJumpDistance(aassettings.phys_jumpvel)) continue;" in face_reaches
	assert "if (bestend[2] - 32 > beststart[2]) continue;" in face_reaches
	assert "if (bestend[2] < beststart[2] - 128) continue;" in face_reaches
	assert "if (!AAS_HorizontalVelocityForJump(0, beststart, bestend, &speed)) continue;" in face_reaches
	assert "if (!AAS_PointInsideFace(bestfacenum, testpoint, 0.1f))" in face_reaches
	assert "lreach->next = lreachabilities;" in face_reaches
	assert "lreachabilities = lreach;" in face_reaches


def test_late_ai_travel_helpers_and_dispatch_match_source_shape() -> None:
	source = _read(BOTLIB_AI_MOVE)

	elevator = _extract_function_block(
		source,
		"bot_moveresult_t BotTravel_Elevator(bot_movestate_t *ms, aas_reachability_t *reach)",
	)
	funcbob = _extract_function_block(
		source,
		"bot_moveresult_t BotTravel_FuncBobbing(bot_movestate_t *ms, aas_reachability_t *reach)",
	)
	weapon_finish = _extract_function_block(
		source,
		"bot_moveresult_t BotFinishTravel_WeaponJump(bot_movestate_t *ms, aas_reachability_t *reach)",
	)
	jumppad = _extract_function_block(
		source,
		"bot_moveresult_t BotTravel_JumpPad(bot_movestate_t *ms, aas_reachability_t *reach)",
	)
	jumppad_finish = _extract_function_block(
		source,
		"bot_moveresult_t BotFinishTravel_JumpPad(bot_movestate_t *ms, aas_reachability_t *reach)",
	)
	reach_time = _extract_function_block(source, "int BotReachabilityTime(aas_reachability_t *reach)")
	goal_area = _extract_function_block(
		source,
		"bot_moveresult_t BotMoveInGoalArea(bot_movestate_t *ms, bot_goal_t *goal)",
	)
	move_to_goal = _extract_function_block(
		source,
		"void BotMoveToGoal(bot_moveresult_t *result, int movestate, bot_goal_t *goal, int travelflags)",
	)

	assert "if (BotOnMover(ms->origin, ms->entitynum, reach))" in elevator
	assert "if (abs(ms->origin[2] - reach->end[2]) < sv_maxbarrier->value)" in elevator
	assert "if (!BotCheckBarrierJump(ms, hordir, 100))" in elevator
	assert "MoverBottomCenter(reach, bottomcenter);" in elevator
	assert "if (!MoverDown(reach))" in elevator
	assert "result.type = RESULTTYPE_ELEVATORUP;" in elevator
	assert "result.flags |= MOVERESULT_WAITING;" in elevator
	assert "if (dist1 < 20 || dist2 < dist1 || DotProduct(dir1, dir2) < 0)" in elevator

	assert "BotFuncBobStartEnd(reach, bob_start, bob_end, bob_origin);" in funcbob
	assert "if (BotOnMover(ms->origin, ms->entitynum, reach))" in funcbob
	assert "VectorSubtract(bob_origin, bob_end, dir);" in funcbob
	assert "MoverBottomCenter(reach, bottomcenter);" in funcbob
	assert "VectorSubtract(bob_origin, bob_start, dir);" in funcbob
	assert "if (VectorLength(dir) > 16)" in funcbob
	assert "result.type = RESULTTYPE_WAITFORFUNCBOBBING;" in funcbob
	assert "result.flags |= MOVERESULT_WAITING;" in funcbob
	assert "if (dist1 < 20 || dist2 < dist1 || DotProduct(dir1, dir2) < 0)" in funcbob

	assert "if (!ms->jumpreach) return result;" in weapon_finish
	assert "if (!BotAirControl(ms->origin, ms->velocity, reach->end, hordir, &speed))" in weapon_finish
	assert "speed = 400;" in weapon_finish
	assert "EA_Move(ms->client, hordir, speed);" in weapon_finish
	assert "VectorCopy(hordir, result.movedir);" in weapon_finish

	assert "hordir[0] = reach->start[0] - ms->origin[0];" in jumppad
	assert "BotCheckBlocked(ms, hordir, qtrue, &result);" in jumppad
	assert "speed = 400;" in jumppad
	assert "EA_Move(ms->client, hordir, speed);" in jumppad
	assert "if (!BotAirControl(ms->origin, ms->velocity, reach->end, hordir, &speed))" in jumppad_finish
	assert "BotCheckBlocked(ms, hordir, qtrue, &result);" in jumppad_finish
	assert "EA_Move(ms->client, hordir, speed);" in jumppad_finish

	for traveltype, timeout in (
		("TRAVEL_WALK", "5"),
		("TRAVEL_LADDER", "6"),
		("TRAVEL_ELEVATOR", "10"),
		("TRAVEL_GRAPPLEHOOK", "8"),
		("TRAVEL_ROCKETJUMP", "6"),
		("TRAVEL_BFGJUMP", "6"),
		("TRAVEL_JUMPPAD", "10"),
		("TRAVEL_FUNCBOB", "10"),
	):
		assert f"case {traveltype}: return {timeout};" in reach_time
	assert 'botimport.Print(PRT_ERROR, "travel type %d not implemented yet\\n", reach->traveltype);' in reach_time
	assert "return 8;" in reach_time

	assert "if (ms->moveflags & MFL_SWIMMING)" in goal_area
	assert "result.traveltype = TRAVEL_SWIM;" in goal_area
	assert "result.traveltype = TRAVEL_WALK;" in goal_area
	assert "if (dist > 100) dist = 100;" in goal_area
	assert "speed = 400 - (400 - 4 * dist);" in goal_area
	assert "if (speed < 10) speed = 0;" in goal_area
	assert "BotCheckBlocked(ms, dir, qtrue, &result);" in goal_area
	assert "EA_Move(ms->client, dir, speed);" in goal_area
	assert "ms->lastgoalareanum = goal->areanum;" in goal_area

	assert "if (AAS_OnGround(ms->origin, ms->presencetype, ms->entitynum)) ms->moveflags |= MFL_ONGROUND;" in move_to_goal
	assert "if (AAS_AgainstLadder(ms->origin)) ms->moveflags |= MFL_AGAINSTLADDER;" in move_to_goal
	assert "if (ms->areanum == goal->areanum)" in move_to_goal
	assert "*result = BotMoveInGoalArea(ms, goal);" in move_to_goal
	assert "if (ms->lastgoalareanum != goal->areanum" in move_to_goal
	assert "ms->lastareanum != ms->areanum)" in move_to_goal
	assert "ms->reachability_time = AAS_Time() + BotReachabilityTime(&reach);" in move_to_goal
	assert "case TRAVEL_ELEVATOR: *result = BotTravel_Elevator(ms, &reach); break;" in move_to_goal
	assert "case TRAVEL_JUMPPAD: *result = BotTravel_JumpPad(ms, &reach); break;" in move_to_goal
	assert "case TRAVEL_FUNCBOB: *result = BotTravel_FuncBobbing(ms, &reach); break;" in move_to_goal
	assert "case TRAVEL_ROCKETJUMP:" in move_to_goal
	assert "case TRAVEL_BFGJUMP: *result = BotFinishTravel_WeaponJump(ms, &reach); break;" in move_to_goal
	assert "case TRAVEL_JUMPPAD: *result = BotFinishTravel_JumpPad(ms, &reach); break;" in move_to_goal
