from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
BG_PMOVE = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"
SURFACEFLAGS = REPO_ROOT / "src" / "code" / "game" / "surfaceflags.h"
TR_SHADER = REPO_ROOT / "src" / "code" / "renderer" / "tr_shader.c"


def test_cgame_registers_the_retail_footstep_ogg_table() -> None:
	source = CG_MAIN.read_text( encoding = "utf-8" )

	for expected in (
		'"sound/player/footsteps/step%i.ogg"',
		'"sound/player/footsteps/boot%i.ogg"',
		'"sound/player/footsteps/flesh%i.ogg"',
		'"sound/player/footsteps/mech%i.ogg"',
		'"sound/player/footsteps/energy%i.ogg"',
		'"sound/player/footsteps/splash%i.ogg"',
		'"sound/player/footsteps/clank%i.ogg"',
		'"sound/player/footsteps/snow%i.ogg"',
		'"sound/player/footsteps/wood%i.ogg"',
	):
		assert expected in source

	assert '"sound/player/footsteps/step%i.wav"' not in source
	assert '"sound/player/footsteps/boot%i.wav"' not in source
	assert '"sound/player/footsteps/flesh%i.wav"' not in source
	assert '"sound/player/footsteps/mech%i.wav"' not in source
	assert '"sound/player/footsteps/energy%i.wav"' not in source
	assert '"sound/player/footsteps/splash%i.wav"' not in source
	assert '"sound/player/footsteps/clank%i.wav"' not in source


def test_shared_surface_flags_restore_quakelive_snow_and_wood_steps() -> None:
	source = SURFACEFLAGS.read_text( encoding = "utf-8" )

	assert "#define\tSURF_DUST\t\t\t\t0x40000" in source
	assert "#define\tSURF_SNOWSTEPS\t\t\t0x80000" in source
	assert "#define\tSURF_WOODSTEPS\t\t\t0x100000" in source


def test_pmove_surface_helper_emits_retail_quakelive_step_events() -> None:
	source = BG_PMOVE.read_text( encoding = "utf-8" )

	assert "if ( pml.groundTrace.surfaceFlags & SURF_METALSTEPS ) {" in source
	assert "return EV_FOOTSTEP_METAL;" in source
	assert "if ( pml.groundTrace.surfaceFlags & SURF_SNOWSTEPS ) {" in source
	assert "return EV_FOOTSTEP_SNOW;" in source
	assert "if ( pml.groundTrace.surfaceFlags & SURF_WOODSTEPS ) {" in source
	assert "return EV_FOOTSTEP_WOOD;" in source


def test_shader_surfaceparm_table_restores_snowsteps_and_woodsteps() -> None:
	source = TR_SHADER.read_text( encoding = "utf-8" )

	assert '{"snowsteps",\t0,\tSURF_SNOWSTEPS,0 },' in source
	assert '{"woodsteps",\t0,\tSURF_WOODSTEPS,0 },' in source
