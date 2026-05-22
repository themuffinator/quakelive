from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BG_SLIDEMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_slidemove.c"
BG_LOCAL_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_local.h"
BG_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"
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
	assert "PM_IsJumpPadLaunchActive()" in probe_body
	assert "PM_ShouldRequireStepJumpRelease( settings )" in body
	assert "PMF_JUMP_HELD" in body
	assert "pm->ps->pm_flags & PMF_REQUIRE_JUMP_RELEASE" in release_body
	assert "settings->autoHop" in release_body
	assert "settings->bunnyHop" not in release_body
	assert "pm_bunnyhop" not in release_body
	assert "releaseRequired = PM_ShouldRequireStepJumpRelease( settings );" in body
	assert "if ( releaseRequired && ( pm->ps->pm_flags & PMF_RESPAWNED ) ) {" in body


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


def test_step_slide_move_keeps_the_configurable_step_helper_private() -> None:
	slidemove_source = BG_SLIDEMOVE_PATH.read_text(encoding="utf-8")
	pmove_source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	local_source = BG_LOCAL_PATH.read_text(encoding="utf-8")

	assert slidemove_source.count("PM_StepSlideMoveWithStepHeight(") == 2
	assert "static void PM_StepSlideMoveWithStepHeight( qboolean gravity, float stepHeight ) {" in slidemove_source
	assert "PM_StepSlideMoveWithStepHeight(" not in pmove_source
	assert "PM_StepSlideMoveWithStepHeight" not in local_source


def test_step_slide_move_rechecks_the_general_step_jump_gate_before_takeoff() -> None:
	source = BG_SLIDEMOVE_PATH.read_text(encoding="utf-8")

	assert source.count("PM_CanStepJump()") >= 2
	assert "jumpPadLaunchActive = PM_IsJumpPadLaunchActive();" in source
	assert "if ( jumpPadLaunchActive && start_v[2] > 0.0f ) {" in source
	assert "if ( canStepJump && PM_CanStepJump() ) {" in source
	assert "else if ( canCrouchStepJump && PM_CanCrouchStepJump() && PM_CanPerformCrouchStepJump() ) {" in source
	assert source.index("canStepJump = PM_CanStepJump();") < source.index("if ( canStepJump && PM_CanStepJump() ) {")


def test_step_slide_move_routes_crouch_step_branch_through_clearance_probe_before_shared_takeoff() -> None:
	source = BG_SLIDEMOVE_PATH.read_text(encoding="utf-8")

	assert "useCrouchStepJump" not in source
	assert "else if ( canCrouchStepJump && PM_CanCrouchStepJump() && PM_CanPerformCrouchStepJump() ) {" in source
	assert "PM_ApplyStepJump( delta, qtrue );" in source
