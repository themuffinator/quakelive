from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BG_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"


def _function_body(pattern: str) -> str:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	match = re.search(
		pattern,
		source,
		re.MULTILINE | re.DOTALL,
	)

	assert match is not None, "Function definition missing"
	return match.group("body")


def test_checkduck_keeps_retail_crouch_time_and_slide_cleanup_inline() -> None:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	body = _function_body(
		r"static void PM_CheckDuck \(void\)\s*\{(?P<body>.*?)^\}",
	)

	assert "PM_UpdateCrouchSlideState" not in source
	assert "pm->cmd.upmove < 0" in body
	assert "pm->ps->crouchTime == 0" in body
	assert "pm->ps->crouchTime = pm->cmd.serverTime;" in body
	assert "pm->ps->crouchTime += pml.msec;" not in body
	assert "pm->ps->crouchTime = settings->crouchSlideTime;" not in body
	assert "pm->ps->crouchTime = 0;" not in body
	assert "pm->ps->pm_flags |= PMF_CROUCH_SLIDE;" not in body
	assert "pm->ps->pm_flags &= ~PMF_CROUCH_SLIDE;" not in body
	assert "wasDucked" not in body
	assert "horizontalSpeed" not in body
	assert "pm->ps->crouchSlideTime < 0" not in body
	assert "pm->ps->crouchSlideTime > settings->crouchSlideTime" not in body
	assert "settings->crouchSlideTime <= 0" not in body
	assert "pm->ps->crouchSlideTime != 0" in body
	assert "pml.groundPlane" in body
	assert "settings->crouchSlide" not in body


def test_crouch_slide_timer_decay_lives_in_drop_timers() -> None:
	checkduck_body = _function_body(
		r"static void PM_CheckDuck \(void\)\s*\{(?P<body>.*?)^\}",
	)
	drop_body = _function_body(
		r"static void PM_DropTimers\( void \)\s*\{(?P<body>.*?)^\}",
	)

	assert "pm->ps->crouchSlideTime -= pml.msec;" not in checkduck_body
	assert "pm->ps->pm_flags & PMF_CROUCH_SLIDE" in drop_body
	assert "pml.groundPlane" in drop_body
	assert "pm->ps->crouchSlideTime != 0" in drop_body
	assert "pm->ps->crouchSlideTime > 0" not in drop_body
	assert "pm->ps->crouchSlideTime -= pml.msec;" in drop_body
	assert "pm->ps->crouchSlideTime = 0;" in drop_body


def test_checkduck_restores_retail_crouch_speed_floor() -> None:
	body = _function_body(
		r"static void PM_CheckDuck \(void\)\s*\{(?P<body>.*?)^\}",
	)

	assert "pm->ps->pm_flags & PMF_CROUCH_SLIDE" in body
	assert "pm->ps->crouchSlideTime == 0" in body
	assert "pm->ps->speed < 400" in body
	assert "pm->ps->speed = 400;" in body


def test_walkmove_recharges_crouch_slide_time_with_retail_clamp() -> None:
	body = _function_body(
		r"static void PM_WalkMove\( void \)\s*\{(?P<body>.*?)^\}",
	)

	assert "settings = PM_GetActiveSettings();" in body
	assert "pm->ps->pm_flags & PMF_CROUCH_SLIDE" in body
	assert "pm->cmd.upmove >= 0" in body
	assert "pm->ps->crouchSlideTime += pml.msec * 5;" in body
	assert "pm->ps->crouchSlideTime > settings->crouchSlideTime" in body
	assert "pm->ps->crouchSlideTime = settings->crouchSlideTime;" in body


def test_walkmove_uses_retail_crouch_slide_duck_speed_cap() -> None:
	body = _function_body(
		r"static void PM_WalkMove\( void \)\s*\{(?P<body>.*?)^\}",
	)

	assert "duckScale = pm_duckScale;" in body
	assert "pm->ps->pm_flags & PMF_CROUCH_SLIDE" in body
	assert "duckScale = 0.75f;" in body
	assert "wishspeed > pm->ps->speed * duckScale" in body
	assert "wishspeed = pm->ps->speed * duckScale;" in body


def test_footsteps_treats_active_crouch_slide_as_retail_movement_input() -> None:
	body = _function_body(
		r"static void PM_Footsteps\( void \)\s*\{(?P<body>.*?)^\}",
	)

	assert "qboolean\tcrouchSlideMoving;" in body
	assert "qboolean\trunSpeed;" in body
	assert "pm->ps->pm_flags & PMF_CROUCH_SLIDE" in body
	assert "pm->cmd.upmove < 0" in body
	assert "pm->ps->crouchSlideTime > 0" in body
	assert "!pm->cmd.forwardmove && !pm->cmd.rightmove && !crouchSlideMoving" in body
	assert "pm->ps->velocity[0] >= 32.0f" in body
	assert "pm->ps->velocity[0] <= -32.0f" in body
	assert "pm->ps->velocity[1] >= 32.0f" in body
	assert "pm->ps->velocity[1] <= -32.0f" in body
	assert "bobmove = 0.35f;" in body
	assert body.index("crouchSlideMoving =") < body.index("if ( pm->ps->groundEntityNum == ENTITYNUM_NONE )")
	assert body.index("!pm->cmd.forwardmove && !pm->cmd.rightmove && !crouchSlideMoving") < body.index("footstep = qfalse;")
	assert body.index("runSpeed =") < body.index("if ( runSpeed )")
	assert body.index("bobmove = 0.35f;") < body.index("PM_ContinueLegsAnim( LEGS_BACKWALK );")


def test_jump_takeoff_clears_crouch_slide_timer() -> None:
	body = _function_body(
		r"static void PM_ApplyJumpTakeoff\( void \)\s*\{(?P<body>.*?)^\}",
	)

	assert "pm->ps->pm_flags & PMF_CROUCH_SLIDE" in body
	assert "pm->ps->crouchSlideTime = 0;" in body


def test_pmove_single_syncs_crouch_slide_feature_flag() -> None:
	body = _function_body(
		r"void PmoveSingle \(pmove_t \*pmove\) \s*\{(?P<body>.*?)^\}",
	)

	assert "settings = PM_GetActiveSettings();" in body
	assert "if ( settings->crouchSlide ) {" in body
	assert "pm->ps->pm_flags |= PMF_CROUCH_SLIDE;" in body
	assert "pm->ps->pm_flags &= ~PMF_CROUCH_SLIDE;" in body
	assert "pm->ps->crouchSlideTime = 0;" in body
