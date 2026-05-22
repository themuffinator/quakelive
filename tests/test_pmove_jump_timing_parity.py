from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BG_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"
BG_PMOVE_JUMP_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove_jump.h"
Q_SHARED_PATH = REPO_ROOT / "src" / "code" / "game" / "q_shared.h"
MSG_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "msg.c"


def _function_body(path: Path, pattern: str) -> str:
	source = path.read_text(encoding="utf-8")
	match = re.search(
		pattern,
		source,
		re.MULTILINE | re.DOTALL,
	)

	assert match is not None, f"Function definition missing in {path.name}"
	return match.group("body")


def test_playerstate_uses_retail_jump_time_and_double_jump_latch() -> None:
	source = Q_SHARED_PATH.read_text(encoding="utf-8")

	assert "int\t\t\tjumpTime;" in source
	assert "int\t\t\tdoubleJumped;" in source
	assert "doubleJumpTime" not in source
	assert "doubleJumpEntNum" not in source
	assert "doubleJumpNormal" not in source
	assert "groundTraceHistory" not in source
	assert "groundTraceLatest" not in source
	assert source.index("int\t\t\tgroundEntityNum;") < source.index("int\t\t\tlegsTimer;")


def test_playerstate_delta_replication_matches_retail_jump_fields() -> None:
	source = MSG_PATH.read_text(encoding="utf-8")

	assert "{ PSF(jumpTime), 32 }" in source
	assert "{ PSF(doubleJumped), 1 }" in source
	assert "PSF(doubleJumpTime)" not in source
	assert "PSF(doubleJumpEntNum)" not in source
	assert "PSF(doubleJumpNormal[0])" not in source
	assert "PSF(groundTraceHistory" not in source
	assert "PSF(groundTraceLatest" not in source
	assert source.index("{ PSF(groundEntityNum), GENTITYNUM_BITS }") < source.index("{ PSF(jumpTime), 32 }")


def test_jump_velocity_scaling_uses_previous_jump_time() -> None:
	source = BG_PMOVE_JUMP_PATH.read_text(encoding="utf-8")

	assert "ps->jumpTime > 0" not in source
	assert "commandTime >= ps->jumpTime" in source
	assert "timeDelta = commandTime - ps->jumpTime;" in source
	assert "( threshold - (float)timeDelta ) / threshold" in source
	assert "jumpVelocityTimeThresholdOffset" not in source
	assert "groundTraceHistoryCount" not in source
	assert "groundTraceTimes" not in source


def test_air_move_probes_retail_double_jump_path() -> None:
	body = _function_body(
		BG_PMOVE_PATH,
		r"static void PM_AirMove\( void \)\s*\{(?P<body>.*?)^\}",
	)

	assert "settings = PM_GetActiveSettings();" in body
	assert "accelerate = pm_airaccelerate;" in body
	assert "currentSpeed = DotProduct( pm->ps->velocity, wishdir );" in body
	assert "accelerate = pm_airstopaccelerate;" in body
	assert "pm->ps->movementDir == 2 || pm->ps->movementDir == 6" in body
	assert "accelerate = pm_strafeaccelerate;" in body
	assert "PM_Accelerate( wishdir, wishspeed, accelerate );" in body
	assert body.index("PM_Accelerate( wishdir, wishspeed, accelerate );") < body.index("PM_AirControl( wishdir, wishspeed );")
	assert "pm_circlestrafe_friction" not in body
	assert "if ( pm->ps->pm_flags & PMF_DOUBLE_JUMP ) {" in body
	assert "PM_CheckJump( qtrue );" in body


def test_jump_takeoff_split_keeps_retail_jump_time_gate_and_double_jump_latch() -> None:
	prepare_body = _function_body(
		BG_PMOVE_PATH,
		r"static qboolean PM_PrepareJumpTakeoff\( qboolean allowAirDoubleJump \)\s*\{(?P<body>.*?)^\}",
	)
	takeoff_body = _function_body(
		BG_PMOVE_PATH,
		r"static void PM_ApplyJumpTakeoff\( void \)\s*\{(?P<body>.*?)^\}",
	)

	assert "timeDelta < settings->jumpTimeDeltaMin" in prepare_body
	assert "pm->cmd.upmove = 0;" in prepare_body
	assert "pm->ps->jumpTime = pm->cmd.serverTime;" in takeoff_body
	assert "pm->ps->doubleJumped = qtrue;" in takeoff_body
	assert "PM_CanTriggerDoubleJump" not in prepare_body
	assert "PM_ResetDoubleJumpSupport" not in takeoff_body


def test_crash_land_owns_the_retail_double_jump_latch_clear() -> None:
	crash_land_body = _function_body(
		BG_PMOVE_PATH,
		r"static void PM_CrashLand\( void \)\s*\{(?P<body>.*?)^\}",
	)
	ground_trace_body = _function_body(
		BG_PMOVE_PATH,
		r"static void PM_GroundTrace\( void \)\s*\{(?P<body>.*?)^\}",
	)

	assert "if ( pm->ps->pm_flags & PMF_DOUBLE_JUMP ) {" in crash_land_body
	assert "pm->ps->doubleJumped = qfalse;" in crash_land_body
	assert crash_land_body.index("pm->ps->bobCycle = 0;") < crash_land_body.index("pm->ps->doubleJumped = qfalse;")
	assert "pm->ps->doubleJumped = qfalse;" not in ground_trace_body
