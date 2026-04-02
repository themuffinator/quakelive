from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BG_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"
BG_PUBLIC_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_public.h"


def _function_body(signature: str) -> str:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	match = re.search(
		rf"(?:static )?(?:qboolean|void) {re.escape(signature)}\([^)]*\)\s*\{{(?P<body>.*?)^\}}",
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
