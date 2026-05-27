from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BG_SLIDEMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_slidemove.c"
BG_LOCAL_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_local.h"
BG_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"
BG_PUBLIC_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_public.h"
G_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "g_pmove.c"
CG_SERVERCMDS_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CG_PREDICT_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_predict.c"
SYMBOL_MAP_DIR = REPO_ROOT / "references" / "symbol-maps"


def _function_body(signature: str) -> str:
	source = BG_SLIDEMOVE_PATH.read_text(encoding="utf-8")
	match = re.search(
		rf"static qboolean {re.escape(signature)}\([^)]*\)\s*\{{(?P<body>.*?)^\}}",
		source,
		re.MULTILINE | re.DOTALL,
	)

	assert match is not None, f"{signature} definition missing"
	return match.group("body")


def _body_from_source(path: Path, signature: str) -> str:
	source = path.read_text(encoding="utf-8")
	search_start = 0
	while True:
		start = source.find(signature, search_start)
		assert start != -1, f"{signature} definition missing"
		after_signature = start + len(signature)
		while after_signature < len(source) and source[after_signature].isspace():
			after_signature += 1
		if after_signature < len(source) and source[after_signature] == "{":
			break
		search_start = after_signature

	brace_start = after_signature
	depth = 0

	for index in range(brace_start, len(source)):
		character = source[index]
		if character == "{":
			depth += 1
		elif character == "}":
			depth -= 1
			if depth == 0:
				return source[brace_start + 1:index]

	raise AssertionError(f"{signature} body did not close")


def _symbol_entries(map_name: str) -> dict[str, dict[str, object]]:
	symbol_map = json.loads((SYMBOL_MAP_DIR / f"{map_name}.json").read_text(encoding="utf-8"))
	return {entry["normalized_name"]: entry for entry in symbol_map["functions"]}


def test_step_jump_gate_uses_retail_jump_release_rules() -> None:
	source = BG_SLIDEMOVE_PATH.read_text(encoding="utf-8")
	release_body = _function_body("PM_ShouldRequireStepJumpRelease")
	probe_body = _function_body("PM_CanProbeStepJump")
	body = _function_body("PM_CanStepJump")

	assert "static qboolean PM_CanStepJump( void ) {" in source
	assert "PMF_RESPAWNED" in body
	assert "PM_IsJumpPadLaunchActive()" not in probe_body
	assert "PM_ShouldRequireStepJumpRelease( settings )" in body
	assert "PMF_JUMP_HELD" in body
	assert "pm->ps->pm_flags & PMF_REQUIRE_JUMP_RELEASE" in release_body
	assert "settings->autoHop" in release_body
	assert "settings->bunnyHop" not in release_body
	assert "pm_bunnyhop" not in release_body
	assert "releaseRequired = PM_ShouldRequireStepJumpRelease( settings );" in body
	assert "if ( releaseRequired && ( pm->ps->pm_flags & PMF_RESPAWNED ) ) {" in body
	assert "PM_IsJumpPadLaunchActive()" not in source


def test_cgame_symbol_map_uses_the_unified_step_jump_names() -> None:
	cgame_entries = _symbol_entries("cgame")
	qagame_entries = _symbol_entries("qagame")

	assert "PM_LaunchJump" not in cgame_entries
	assert "PM_ShouldTryCrouchStepJump" not in cgame_entries
	assert "PM_ShouldTryStepJump" not in cgame_entries

	expected = {
		"PM_ApplyJumpTakeoff": ("0x10002790", "0x1002E2C0"),
		"PM_CanCrouchStepJump": ("0x10002990", "0x1002E4C0"),
		"PM_CanStepJump": ("0x100029E0", "0x1002E510"),
	}
	for name, (cgame_address, qagame_address) in expected.items():
		assert cgame_entries[name]["address"] == cgame_address
		assert qagame_entries[name]["address"] == qagame_address
		assert name in cgame_entries[name]["signature"]
		assert name in qagame_entries[name]["signature"]


def test_step_jump_gate_clears_queued_jump_state_on_rejected_attempts() -> None:
	body = _function_body("PM_CanStepJump")

	assert "pm->cmd.upmove = 0;" in body
	assert body.index("releaseRequired && ( pm->ps->pm_flags & PMF_JUMP_HELD )") < body.index("pm->cmd.upmove = 0;")
	assert body.index("!PM_HasSatisfiedStepJumpDelay( settings )") < body.rindex("pm->cmd.upmove = 0;")


def test_step_jump_gate_uses_retail_jump_time_delay() -> None:
	body = _function_body("PM_HasSatisfiedStepJumpDelay")

	assert "pm->cmd.serverTime < pm->ps->jumpTime" in body
	assert "timeDelta = pm->cmd.serverTime - pm->ps->jumpTime;" in body
	assert "(float)timeDelta >= settings->jumpTimeDeltaMin" in body
	assert "groundTraceHistoryCount" not in body
	assert "groundTraceTimes" not in body
	assert "settings->jumpTimeDeltaMin" in body


def test_crouch_step_jump_gate_reuses_shared_retail_prechecks() -> None:
	source = BG_SLIDEMOVE_PATH.read_text(encoding="utf-8")
	body = _function_body("PM_CanCrouchStepJump")

	assert "static qboolean PM_CanCrouchStepJump( void ) {" in source
	assert "PM_CanProbeStepJump( settings )" in body
	assert "pm->cmd.upmove < 10" not in body
	assert "PM_ShouldRequireStepJumpRelease( settings )" not in body
	assert "PM_HasSatisfiedStepJumpDelay( settings )" in body
	assert "PMF_DUCKED" in body


def test_crouch_step_jump_gate_keeps_the_retail_crouch_leaf_shape() -> None:
	body = _function_body("PM_CanCrouchStepJump")

	assert "PMF_DUCKED" in body
	assert "pml.groundPlane" in body
	assert "pm->ps->velocity[2] < 0.0f" in body
	assert "PM_HasSatisfiedStepJumpDelay( settings )" in body
	assert "PMF_JUMP_HELD" not in body
	assert "PMF_RESPAWNED" not in body


def test_step_slide_move_restores_retail_public_signature() -> None:
	slidemove_source = BG_SLIDEMOVE_PATH.read_text(encoding="utf-8")
	local_source = BG_LOCAL_PATH.read_text(encoding="utf-8")
	cgame_entries = _symbol_entries("cgame")

	assert "void\t\tPM_StepSlideMove( qboolean gravity );" in local_source
	assert "void PM_StepSlideMove( qboolean gravity ) {" in slidemove_source
	assert "PM_StepSlideMoveWithStepHeight( gravity, pm_stepHeight );" in slidemove_source
	assert cgame_entries["PM_StepSlideMove"]["signature"] == "void PM_StepSlideMove(qboolean gravity)"


def test_step_slide_move_call_sites_stop_passing_step_height() -> None:
	pmove_source = BG_PMOVE_PATH.read_text(encoding="utf-8")

	assert "PM_StepSlideMove( qtrue, pm_stepHeight );" not in pmove_source
	assert "PM_StepSlideMove( qfalse, pm_stepHeight );" not in pmove_source
	assert pmove_source.count("PM_StepSlideMove( qtrue );") >= 1
	assert pmove_source.count("PM_StepSlideMove( qfalse );") >= 1


def test_step_slide_move_dispatch_wiring_matches_retail_call_matrix() -> None:
	pmove_source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	water_jump_body = _body_from_source(BG_PMOVE_PATH, "static void PM_WaterJumpMove( void )")
	water_body = _body_from_source(BG_PMOVE_PATH, "static void PM_WaterMove( void )")
	ladder_body = _body_from_source(BG_PMOVE_PATH, "static void PM_LadderMove( void )")
	fly_body = _body_from_source(BG_PMOVE_PATH, "static void PM_FlyMove( void )")
	air_body = _body_from_source(BG_PMOVE_PATH, "static void PM_AirMove( void )")
	walk_body = _body_from_source(BG_PMOVE_PATH, "static void PM_WalkMove( void )")

	assert pmove_source.count("PM_StepSlideMove( qtrue );") == 2
	assert pmove_source.count("PM_StepSlideMove( qfalse );") == 3
	assert "PM_StepSlideMove( qtrue );" in water_jump_body
	assert "PM_StepSlideMove( qtrue );" in air_body
	assert "PM_StepSlideMove( qfalse );" in fly_body
	assert walk_body.count("PM_StepSlideMove( qfalse );") == 2
	assert "PM_StepSlideMove" not in water_body
	assert "PM_StepSlideMove" not in ladder_body
	assert "PM_SlideMove( qfalse );" in water_body
	assert "PM_SlideMove( qfalse );" in ladder_body
	assert air_body.index("PM_StepSlideMove( qtrue );") < air_body.index("PM_InvulnerabilityMove();")
	assert walk_body.index("PM_ShouldUseInvulnerabilityMove()") < walk_body.index("PM_StepSlideMove( qfalse );")
	assert walk_body.rindex("PM_StepSlideMove( qfalse );") > walk_body.index("PM_Accelerate")


def test_step_slide_move_keeps_the_configurable_step_helper_private() -> None:
	slidemove_source = BG_SLIDEMOVE_PATH.read_text(encoding="utf-8")
	pmove_source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	local_source = BG_LOCAL_PATH.read_text(encoding="utf-8")

	assert slidemove_source.count("PM_StepSlideMoveWithStepHeight(") == 2
	assert "static void PM_StepSlideMoveWithStepHeight( qboolean gravity, float stepHeight ) {" in slidemove_source
	assert "PM_StepSlideMoveWithStepHeight(" not in pmove_source
	assert "PM_StepSlideMoveWithStepHeight" not in local_source


def test_step_slide_move_tuning_transport_feeds_the_private_globals() -> None:
	bg_public_source = BG_PUBLIC_PATH.read_text(encoding="utf-8")
	bg_pmove_source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	g_pmove_source = G_PMOVE_PATH.read_text(encoding="utf-8")
	cg_servercmds_source = CG_SERVERCMDS_PATH.read_text(encoding="utf-8")
	load_settings_body = _body_from_source(BG_PMOVE_PATH, "static void PM_LoadMoveSettings( void )")
	load_tuning_body = _body_from_source(BG_PMOVE_PATH, "static void PM_LoadMoveTuningConstants( void )")
	pmove_single_body = _body_from_source(BG_PMOVE_PATH, "void PmoveSingle (pmove_t *pmove)")
	serialize_body = _body_from_source(G_PMOVE_PATH, "static qboolean G_PmoveSerializeSettings( const pmove_settings_t *settings, char *buffer, size_t bufferSize )")
	compact_body = _body_from_source(CG_SERVERCMDS_PATH, "static qboolean CG_ParsePmoveCompactSettingsPayload( const char *payload, pmove_settings_t *settings )")

	assert "float\tairStepFriction;" in bg_public_source
	assert "int\tairSteps;" in bg_public_source
	assert "float\tstepHeight;" in bg_public_source
	assert "PMOVE_COMPACT_FLOAT( airStepFriction );" in compact_body
	assert "PMOVE_COMPACT_INT( airSteps );" in compact_body
	assert "PMOVE_COMPACT_FLOAT( stepHeight );" in compact_body
	assert "PMOVE_FLOAT_FIELD( airStepFriction )" in cg_servercmds_source
	assert "PMOVE_INT_FIELD( airSteps )" in cg_servercmds_source
	assert "PMOVE_FLOAT_FIELD( stepHeight )" in cg_servercmds_source
	assert "settings->airStepFriction" in serialize_body
	assert "settings->airSteps" in serialize_body
	assert "settings->stepHeight" in serialize_body
	assert 'G_PmoveRegisterCvar( &g_pmove_airStepFriction_cvar, "pmove_AirStepFriction", "0.03f", PMOVE_CVAR_FLAGS_FACTORY );' in g_pmove_source
	assert 'G_PmoveRegisterCvar( &g_pmove_airSteps_cvar, "pmove_AirSteps", "1", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );' in g_pmove_source
	assert 'G_PmoveRegisterCvar( &g_pmove_stepHeight_cvar, "pmove_StepHeight", "22.0f", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );' in g_pmove_source
	assert "stepHeight = settings->stepHeight;" in load_settings_body
	assert "pm_stepHeight = stepHeight;" in load_settings_body
	assert "pm_airstepfriction = PM_LoadMoveTuningFloat(" in load_tuning_body
	assert "pm_airsteps = airControlTuning" in load_tuning_body
	assert bg_pmove_source.index("PM_LoadMoveSettings();") < bg_pmove_source.index("void PM_ApplyStepJump")
	assert pmove_single_body.index("PM_LoadMoveTuningConstants();") < pmove_single_body.index("if ( pm->ps->stats[STAT_HEALTH] <= 0")


def test_step_slide_move_rechecks_the_general_step_jump_gate_before_takeoff() -> None:
	source = BG_SLIDEMOVE_PATH.read_text(encoding="utf-8")

	assert source.count("PM_CanStepJump()") >= 2
	assert "pm->trace( &trace, start_o, pm->mins, pm->maxs, pm->ps->origin" in source
	assert "velocityDot = DotProduct( pm->ps->velocity, trace.plane.normal );" in source
	assert "velocityDot < 0.0f || Q_fabs( velocityDot ) < 0.001f" in source
	assert "Q_fabs( velocityDot ) < 0.1f" not in source
	assert "if ( !trace.startsolid && !trace.allsolid && trace.fraction < 1.0f && trace.plane.normal[2] >= MIN_WALK_NORMAL ) {" in source
	assert "if ( canStepJump && PM_CanStepJump() ) {" in source
	assert "else if ( canCrouchStepJump && PM_CanCrouchStepJump() && PM_CanPerformCrouchStepJump() ) {" in source
	assert source.index("canStepJump = PM_CanStepJump();") < source.index("if ( canStepJump && PM_CanStepJump() ) {")
	assert "PM_IsJumpPadLaunchActive()" not in source


def test_step_slide_move_routes_crouch_step_branch_through_clearance_probe_before_shared_takeoff() -> None:
	source = BG_SLIDEMOVE_PATH.read_text(encoding="utf-8")

	assert "useCrouchStepJump" not in source
	assert "else if ( canCrouchStepJump && PM_CanCrouchStepJump() && PM_CanPerformCrouchStepJump() ) {" in source
	assert "PM_ApplyStepJump( delta, qtrue );" in source


def test_step_jump_takeoff_latches_preserve_normal_and_crouch_split() -> None:
	apply_body = _body_from_source(BG_PMOVE_PATH, "void PM_ApplyStepJump( float stepDelta, qboolean fromCrouchSlide )")
	normal_body = _body_from_source(BG_PMOVE_PATH, "static qboolean PM_PrepareStepJumpTakeoff( const pmove_settings_t *settings )")
	crouch_body = _body_from_source(BG_PMOVE_PATH, "static qboolean PM_PrepareCrouchStepJumpTakeoff( const pmove_settings_t *settings )")

	assert apply_body.index("PM_PrepareCrouchStepJumpTakeoff( settings )") < apply_body.index("PM_ApplyJumpTakeoff();")
	assert apply_body.index("PM_PrepareJumpTakeoff( qfalse )") < apply_body.index("PM_PrepareStepJumpTakeoff( settings )")
	assert apply_body.index("PM_PrepareStepJumpTakeoff( settings )") < apply_body.index("PM_ApplyJumpTakeoff();")
	assert "PM_EvaluateJumpTakeoffVelocity( settings, qtrue, NULL );" in normal_body
	assert "PM_ApplyRampJumpVerticalVelocity( jumpVelocity, qfalse, settings );" in normal_body
	assert "PM_EvaluateJumpTakeoffVelocity( settings, qfalse, NULL );" in crouch_body
	assert "PM_ApplyRampJumpVerticalVelocity( jumpVelocity, qtrue, settings );" in crouch_body


def test_step_slide_move_exports_step_delta_to_cgame_prediction_smoothing() -> None:
	pmove_body = _body_from_source(BG_PMOVE_PATH, "void Pmove (pmove_t *pmove)")
	step_body = _body_from_source(CG_PREDICT_PATH, "static void CG_UpdateStepChange( void )")
	predict_body = _body_from_source(CG_PREDICT_PATH, "void CG_PredictPlayerState( void )")

	assert "pmove->stepUp = 0.0f;" in pmove_body
	assert "pmove->stepUpTime = 0;" in pmove_body
	assert "if ( pml.stepUp > 0.0f ) {" in pmove_body
	assert "pmove->stepUp += pml.stepUp;" in pmove_body
	assert "pmove->stepUpTime = pmove->cmd.serverTime;" in pmove_body
	assert "cg_pmove.stepUp <= 0.0f" in step_body
	assert "cg_pmove.stepUpTime <= cg.stepTime" in step_body
	assert "cg.stepChange = oldStep + cg_pmove.stepUp;" in step_body
	assert "MAX_STEP_CHANGE" in step_body
	assert predict_body.index("Pmove (&cg_pmove);") < predict_body.index("CG_UpdateStepChange();")
