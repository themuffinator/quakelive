from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BG_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"


def test_air_specific_accel_overrides_stay_scoped_to_airborne_move() -> None:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	accelerate_match = re.search(
		r"static void PM_Accelerate\( vec3_t wishdir, float wishspeed, float accel \)\s*\{(?P<body>.*?)^\}",
		source,
		re.MULTILINE | re.DOTALL,
	)
	air_move_match = re.search(
		r"static void PM_AirMove\( void \)\s*\{(?P<body>.*?)^\}",
		source,
		re.MULTILINE | re.DOTALL,
	)

	assert accelerate_match is not None, "PM_Accelerate definition missing"
	assert air_move_match is not None, "PM_AirMove definition missing"

	accelerate_body = accelerate_match.group("body")
	air_move_body = air_move_match.group("body")

	assert "currentSpeed = DotProduct( pm->ps->velocity, wishdir );" in accelerate_body
	assert "addSpeed = wishspeed - currentSpeed;" in accelerate_body
	assert "accelSpeed = accel * pml.frametime * wishspeed;" in accelerate_body
	assert "pm->ps->pm_type == PM_NORMAL" not in accelerate_body
	assert "!pml.walking" not in accelerate_body
	assert "pm->waterlevel <= 1" not in accelerate_body
	assert "pm_bunnyhop" not in accelerate_body
	assert "pm_autohop" not in accelerate_body

	assert "accelerate = pm_airaccelerate;" in air_move_body
	assert "currentSpeed = DotProduct( pm->ps->velocity, wishdir );" in air_move_body
	assert "accelerate = pm_airstopaccelerate;" in air_move_body
	assert "pm->ps->movementDir == 2 || pm->ps->movementDir == 6" in air_move_body
	assert "accelerate = pm_strafeaccelerate;" in air_move_body
	assert "PM_Accelerate( wishdir, wishspeed, accelerate );" in air_move_body
