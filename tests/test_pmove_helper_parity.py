from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BG_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"
BG_PUBLIC_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_public.h"
CLEAN_PMOVE_HEADER_PATH = REPO_ROOT / "src-re" / "clean" / "include" / "qlr_game_pmove.h"
CLEAN_PMOVE_SOURCE_PATH = REPO_ROOT / "src-re" / "clean" / "gameplay" / "pmove.c"


def _function_body(signature: str) -> str:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	match = re.search(
		rf"(?:static )?(?:qboolean|void) {re.escape(signature)}\s*\([^)]*\)\s*\{{(?P<body>.*?)^\}}",
		source,
		re.MULTILINE | re.DOTALL,
	)

	assert match is not None, f"{signature} definition missing"
	return match.group("body")


def test_pmove_surface_drops_the_source_only_parameter_block() -> None:
	bg_public = BG_PUBLIC_PATH.read_text(encoding="utf-8")
	bg_pmove = BG_PMOVE_PATH.read_text(encoding="utf-8")

	assert "typedef struct pmoveParams_s" not in bg_public
	assert "pmoveParams_t" not in bg_public
	assert "pmoveParams;" not in bg_public
	assert "PM_LoadMoveParams" not in bg_pmove
	assert "pm_defaultParams" not in bg_pmove


def test_load_move_tuning_constants_restores_the_retail_air_control_bundles() -> None:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	body = _function_body("PM_LoadMoveTuningConstants")

	assert "static const pmove_tuning_constants_t\tpm_retailDefaultTuning" in source
	assert "static const pmove_tuning_constants_t\tpm_retailAirControlTuning" in source
	assert ".airControl = 150.0f," in source
	assert ".airAccel = 1.1f," in source
	assert ".airStopAccel = 2.5f," in source
	assert ".circleStrafeFriction = 5.5f," in source
	assert ".strafeAccel = 70.0f," in source
	assert ".walkAccel = 15.0f," in source
	assert ".airSteps = 3," in source
	assert ".wishSpeed = 35.0f," in source
	assert "airControlTuning = ( settings->airControl > 0.0f ) ? qtrue : qfalse;" in body
	assert "pm_accelerate = PM_LoadMoveTuningFloat(" in body
	assert "pm_airaccelerate = PM_LoadMoveTuningFloat(" in body
	assert "pm_aircontrol = PM_LoadMoveTuningFloat(" in body
	assert "pm_airsteps = airControlTuning" in body
	assert "pm_circlestrafe_friction = PM_LoadMoveTuningFloat(" in body
	assert "pm_wishspeed = PM_LoadMoveTuningFloat(" in body
	assert "PM_LoadMoveSettings();" in body


def test_build_wish_move_3d_uses_the_shared_retail_axis_builder() -> None:
	body = _function_body("PM_BuildWishMove3D")

	assert "scale = PM_CmdScale( &pm->cmd );" in body
	assert "wishvel[i] = scale * pml.forward[i] * pm->cmd.forwardmove + scale * pml.right[i] * pm->cmd.rightmove;" in body
	assert "wishvel[2] += scale * pm->cmd.upmove;" in body
	assert "*wishspeed = VectorNormalize( wishdir );" in body


def test_3d_move_paths_share_the_retail_wish_builder() -> None:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")

	assert source.count("PM_BuildWishMove3D( wishdir, &wishspeed )") >= 4
	assert "VectorSet( wishdir, 0.0f, 0.0f, -1.0f );" in source


def test_pm_accelerate_stays_on_the_generic_retail_body() -> None:
	body = _function_body("PM_Accelerate")

	assert "currentSpeed = DotProduct( pm->ps->velocity, wishdir );" in body
	assert "addSpeed = wishspeed - currentSpeed;" in body
	assert "accelSpeed = accel * pml.frametime * wishspeed;" in body
	assert "pm_wishspeed" not in body
	assert "pm_airstopaccelerate" not in body
	assert "pm_strafeaccelerate" not in body
	assert "airborneMove" not in body


def test_friction_restores_the_retail_circle_strafe_branch() -> None:
	body = _function_body("PM_Friction")

	assert "friction = pm_friction;" in body
	assert "friction = settings->crouchSlideFriction;" in body
	assert "pm_aircontrol > 0.0f && pm->cmd.forwardmove && pm->cmd.rightmove" in body
	assert "pm->ps->movementDir == 1 || pm->ps->movementDir == 3" in body
	assert "pm->ps->movementDir == 5 || pm->ps->movementDir == 7" in body
	assert "friction = pm_circlestrafe_friction;" in body
	assert "drop += control * friction * pml.frametime;" in body


def test_apply_jump_takeoff_restores_the_retail_shared_jump_leaf() -> None:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	body = _function_body("PM_ApplyJumpTakeoff")

	assert "static void PM_ApplyJumpTakeoff( void ) {" in source
	assert "pm->ps->pm_flags |= PMF_JUMP_HELD;" in body
	assert "pm->ps->groundEntityNum = ENTITYNUM_NONE;" in body
	assert "pm->ps->groundTraceLatestEntNum = ENTITYNUM_NONE;" in body
	assert "pm->ps->jumpTime = pm->cmd.serverTime;" in body
	assert "pm->ps->velocity[2] = pm_jumpTakeoffVelocity;" in body
	assert "PM_AddEvent( EV_JUMP );" in body
	assert "PM_ForceLegsAnim( LEGS_JUMP );" in body
	assert "PM_ForceLegsAnim( LEGS_JUMPB );" in body


def test_prepare_jump_takeoff_holds_the_shared_retail_jump_setup() -> None:
	body = _function_body("PM_PrepareJumpTakeoff")

	assert "jumpVelocityScale = PM_EvaluateJumpVelocityScale( pm->ps, settings, pm->cmd.serverTime, &timeDelta );" in body
	assert "PM_ApplyJumpPlanarVelocity( chainJumpActive, rampJumpActive, settings );" in body
	assert "pm_jumpTakeoffVelocity = jumpVelocity;" in body
	assert "pm_jumpTakeoffDoubleJumpActive = doubleJumpActive;" in body
	assert "pm_jumpTakeoffChainJumpActive = chainJumpActive;" in body
	assert "pm_jumpTakeoffRampJumpActive = rampJumpActive;" in body
	assert "PM_ApplyJumpTakeoff();" not in body


def test_check_jump_routes_through_the_shared_takeoff_helper() -> None:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	body = _function_body("PM_CheckJump")

	assert "PM_PrepareJumpTakeoff( allowAirDoubleJump )" in body
	assert body.count("PM_ApplyJumpTakeoff();") == 1
	assert "return qfalse;" in body
	assert "return qtrue;" in body


def test_step_jump_routes_through_the_shared_takeoff_helper() -> None:
	body = _function_body("PM_ApplyStepJump")

	assert "PM_PrepareJumpTakeoff( qfalse )" in body
	assert "PM_ApplyJumpTakeoff();" in body
	assert "PM_CheckJump( qfalse )" not in body


def test_pmove_single_keeps_the_retail_dispatch_order() -> None:
	body = _function_body("PmoveSingle")
	post_move_markers = [
		"PM_Animate();",
		"PM_GroundTrace();",
		"PM_SetWaterLevel();",
		"PM_Weapon();",
		"PM_TorsoAnimation();",
		"PM_Footsteps();",
		"PM_WaterEvents();",
		"trap_SnapVector( pm->ps->velocity );",
	]
	position = -1
	initial_water_level = body.index("PM_SetWaterLevel();")
	check_duck = body.index("PM_CheckDuck ();", initial_water_level)
	initial_ground_trace = body.index("PM_GroundTrace();", check_duck)

	assert initial_water_level < check_duck
	assert check_duck < initial_ground_trace
	assert body.index("PM_DropTimers();") < body.index("PM_CheckLadder();")
	assert body.index("PM_CheckLadder();") < body.index("pm->ps->powerups[PW_INVULNERABILITY] = 0;")
	assert body.index("if ( pm->ps->powerups[PW_FLIGHT] )") < body.index("} else if (pm->ps->pm_flags & PMF_GRAPPLE_PULL)")
	assert body.index("} else if (pm->ps->pm_flags & PMF_GRAPPLE_PULL)") < body.index("} else if (pm->ps->pm_flags & PMF_TIME_WATERJUMP)")
	assert body.index("} else if (pm->ps->pm_flags & PMF_TIME_WATERJUMP)") < body.index("} else if ( pm->waterlevel > 1 )")
	assert body.index("} else if ( pm->waterlevel > 1 )") < body.index("} else if ( pml.ladder )")
	assert body.index("} else if ( pml.ladder )") < body.index("} else if ( pml.walking )")

	for marker in post_move_markers:
		next_position = body.index(marker, position + 1)
		assert next_position > position
		position = next_position


def test_pmove_replays_long_frames_through_the_retail_chunk_loop() -> None:
	body = _function_body("Pmove")

	assert "pmove->stepUp = 0.0f;" in body
	assert "pmove->stepUpTime = 0;" in body
	assert "if ( finalTime > pmove->ps->commandTime + 1000 ) {" in body
	assert "pmove->ps->pmove_framecount = (pmove->ps->pmove_framecount+1) & ((1<<PS_PMOVEFRAMECOUNTBITS)-1);" in body
	assert "while ( pmove->ps->commandTime != finalTime ) {" in body
	assert "if ( pmove->pmove_fixed ) {" in body
	assert "if ( msec > pmove->pmove_msec ) {" in body
	assert "if ( msec > 66 ) {" in body
	assert body.index("pmove->cmd.serverTime = pmove->ps->commandTime + msec;") < body.index("PmoveSingle( pmove );")
	assert "if ( pml.stepUp > 0.0f ) {" in body
	assert "pmove->stepUp += pml.stepUp;" in body
	assert "pmove->stepUpTime = pmove->cmd.serverTime;" in body
	assert "if ( ( pmove->ps->pm_flags & PMF_JUMP_HELD ) && originalUpmove >= 10 ) {" in body
	assert "pmove->cmd.upmove = 20;" in body


def test_walk_move_uses_the_grounded_jump_gate_before_friction() -> None:
	body = _function_body("PM_WalkMove")
	jump_gate = body.index("if ( PM_CheckJump( qfalse ) ) {")
	post_jump_water = body.index("if ( pm->waterlevel > 1 ) {", jump_gate)
	post_jump_air = body.index("PM_AirMove();", post_jump_water)

	assert "if ( PM_CheckJump( qfalse ) ) {" in body
	assert jump_gate < body.index("PM_Friction ();")
	assert jump_gate < post_jump_water
	assert post_jump_water < post_jump_air


def test_clean_pmove_shim_preserves_the_retail_check_jump_parameter() -> None:
	header = CLEAN_PMOVE_HEADER_PATH.read_text(encoding="utf-8")
	source = CLEAN_PMOVE_SOURCE_PATH.read_text(encoding="utf-8")

	assert "typedef bool (*qlr_game_pmove_check_jump_hook_t)(struct qlr_game_pmove_context_s *ctx, bool allowAirDoubleJump);" in header
	assert "bool PM_CheckJump(bool allowAirDoubleJump);" in header
	assert "bool PM_CheckJump(bool allowAirDoubleJump) {" in source
	assert "\"missing-hook ctx=%p allowAirDoubleJump=%d\"" in source
	assert "return ctx->hooks.check_jump(ctx, allowAirDoubleJump);" in source
