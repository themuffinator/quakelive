from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BG_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"


def test_crouch_slide_friction_uses_constant_scale() -> None:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	match = re.search(
		r"static void PM_Friction\( void \)\s*\{(?P<body>.*?)^\}",
		source,
		re.MULTILINE | re.DOTALL,
	)

	assert match is not None, "PM_Friction definition missing"

	body = match.group("body")
	assert "settings->crouchSlideFriction" in body
	assert "friction = settings->crouchSlideFriction;" in body
	assert "pm->cmd.upmove < 0" in body
	assert "pm->ps->crouchSlideTime > 0" in body
	assert "frictionScale" not in body
	assert "targetScale" not in body
	assert "slideDuration" not in body
	assert "timeLeft" not in body
	assert "timeLeft / slideDuration" not in body
