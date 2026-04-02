from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BG_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"
G_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "g_pmove.c"


def _function_body(path: Path, pattern: str) -> str:
	source = path.read_text(encoding="utf-8")
	match = re.search(
		pattern,
		source,
		re.MULTILINE | re.DOTALL,
	)

	assert match is not None, f"Function definition missing in {path.name}"
	return match.group("body")


def test_shared_water_scale_defaults_match_retail() -> None:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")

	assert "float\tpm_swimScale = 0.60f;" in source
	assert "float\tpm_wadeScale = 0.80f;" in source
	assert "\t.waterSwimScale = 0.60f," in source
	assert "\t.waterWadeScale = 0.80f," in source


def test_walkmove_uses_retail_wade_interpolation() -> None:
	body = _function_body(
		BG_PMOVE_PATH,
		r"static void PM_WalkMove\( void \)\s*\{(?P<body>.*?)^\}",
	)

	assert "if ( pm->waterlevel == 1 ) {" in body
	assert "waterScale = pm_wadeScale;" in body
	assert "waterScale = 1.0f - ( ( (float)pm->waterlevel ) / 3.0f ) * ( 1.0f - pm_swimScale );" in body
	assert "0.5f * ( pm_wadeScale + pm_swimScale )" not in body


def test_friction_does_not_scale_water_drag_by_wade_swim_cvars() -> None:
	body = _function_body(
		BG_PMOVE_PATH,
		r"static void PM_Friction\( void \)\s*\{(?P<body>.*?)^\}",
	)

	assert "speed * pm_waterfriction * pm->waterlevel * pml.frametime" in body
	assert "waterFrictionScale" not in body
	assert "pm_wadeScale" not in body
	assert "pm_swimScale" not in body


def test_game_cvar_defaults_match_retail_water_scales() -> None:
	source = G_PMOVE_PATH.read_text(encoding="utf-8")

	assert '"pmove_WaterSwimScale", "0.6f"' in source
	assert '"pmove_WaterWadeScale", "0.8f"' in source
