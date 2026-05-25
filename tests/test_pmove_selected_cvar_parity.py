from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
G_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "g_pmove.c"
BG_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"
BG_PMOVE_JUMP_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove_jump.h"
G_CONFIG_PATH = REPO_ROOT / "src" / "game" / "g_config.c"
G_MAIN_PATH = REPO_ROOT / "src" / "code" / "game" / "g_main.c"
CG_SERVERCMDS_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
SYMBOL_MAP_DIR = REPO_ROOT / "references" / "symbol-maps"


SELECTED_PMOVE_CVARS = [
	{
		"name": "pmove_AirAccel",
		"variable": "g_pmove_airAccel_cvar",
		"default": "1.0f",
		"flags": "PMOVE_CVAR_FLAGS_CUSTOM_LATCH",
		"field": "airAccel",
		"parse": "PMOVE_COMPACT_FLOAT( airAccel );",
		"cache": "g_pmoveSettings.airAccel = g_pmove_airAccel_cvar.value;",
		"refresh": "qtrue",
		"default_field": ".airAccel = 1.0f,",
	},
	{
		"name": "pmove_AirControl",
		"variable": "g_pmove_airControl_cvar",
		"default": "0",
		"flags": "PMOVE_CVAR_FLAGS_CUSTOM",
		"field": "airControl",
		"parse": "PMOVE_COMPACT_FLOAT( airControl );",
		"cache": "g_pmoveSettings.airControl = g_pmove_airControl_cvar.value;",
		"refresh": "qfalse",
		"default_field": ".airControl = 0.0f,",
	},
	{
		"name": "pmove_AirStopAccel",
		"variable": "g_pmove_airStopAccel_cvar",
		"default": "1.0f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "airStopAccel",
		"parse": "PMOVE_COMPACT_FLOAT( airStopAccel );",
		"cache": "g_pmoveSettings.airStopAccel = g_pmove_airStopAccel_cvar.value;",
		"refresh": "qtrue",
		"default_field": ".airStopAccel = 1.0f,",
	},
	{
		"name": "pmove_AutoHop",
		"variable": "g_pmove_autoHop_cvar",
		"default": "1",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "autoHop",
		"parse": "PMOVE_COMPACT_BOOL( autoHop );",
		"cache": "g_pmoveSettings.autoHop = ( g_pmove_autoHop_cvar.integer != 0 );",
		"refresh": "qtrue",
		"default_field": ".autoHop = qtrue,",
	},
	{
		"name": "pmove_ChainJump",
		"variable": "g_pmove_chainJump_cvar",
		"default": "1",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "chainJump",
		"parse": "PMOVE_COMPACT_INT( chainJump );",
		"cache": "g_pmoveSettings.chainJump = g_pmove_chainJump_cvar.integer;",
		"refresh": "qtrue",
		"default_field": ".chainJump = PM_JUMP_VELOCITY_MODE_SCALE,",
	},
	{
		"name": "pmove_CircleStrafeFriction",
		"variable": "g_pmove_circleStrafeFriction_cvar",
		"default": "6.0f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "circleStrafeFriction",
		"parse": "PMOVE_COMPACT_FLOAT( circleStrafeFriction );",
		"cache": "g_pmoveSettings.circleStrafeFriction = g_pmove_circleStrafeFriction_cvar.value;",
		"refresh": "qtrue",
		"default_field": ".circleStrafeFriction = 6.0f,",
	},
	{
		"name": "pmove_StrafeAccel",
		"variable": "g_pmove_strafeAccel_cvar",
		"default": "1.0f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "strafeAccel",
		"parse": "PMOVE_COMPACT_FLOAT( strafeAccel );",
		"cache": "g_pmoveSettings.strafeAccel = g_pmove_strafeAccel_cvar.value;",
		"refresh": "qtrue",
		"default_field": ".strafeAccel = 1.0f,",
	},
	{
		"name": "pmove_WalkAccel",
		"variable": "g_pmove_walkAccel_cvar",
		"default": "10.0f",
		"flags": "PMOVE_CVAR_FLAGS_CUSTOM_LATCH",
		"field": "walkAccel",
		"parse": "PMOVE_COMPACT_FLOAT( walkAccel );",
		"cache": "g_pmoveSettings.walkAccel = g_pmove_walkAccel_cvar.value;",
		"refresh": "qtrue",
		"default_field": ".walkAccel = 10.0f,",
	},
	{
		"name": "pmove_WalkFriction",
		"variable": "g_pmove_walkFriction_cvar",
		"default": "6.0f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "walkFriction",
		"parse": "PMOVE_COMPACT_FLOAT( walkFriction );",
		"cache": "g_pmoveSettings.walkFriction = g_pmove_walkFriction_cvar.value;",
		"refresh": "qtrue",
		"default_field": ".walkFriction = 6.0f,",
	},
	{
		"name": "pmove_WishSpeed",
		"variable": "g_pmove_wishSpeed_cvar",
		"default": "400.0f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "wishSpeed",
		"parse": "PMOVE_COMPACT_FLOAT( wishSpeed );",
		"cache": "g_pmoveSettings.wishSpeed = g_pmove_wishSpeed_cvar.value;",
		"refresh": "qtrue",
		"default_field": ".wishSpeed = 400.0f,",
	},
]


JUMP_PMOVE_CVARS = [
	{
		"name": "pmove_ChainJumpVelocity",
		"variable": "g_pmove_chainJumpVelocity_cvar",
		"default": "110.0f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "chainJumpVelocity",
		"parse": "parsed.chainJumpVelocity = (float)integerValue;",
		"json_parse": "PMOVE_FLOAT_FIELD( chainJumpVelocity )",
		"cache": "g_pmoveSettings.chainJumpVelocity = g_pmove_chainJumpVelocity_cvar.value;",
		"serialize": "(int)settings->chainJumpVelocity",
		"refresh": "qtrue",
		"default_field": ".chainJumpVelocity = 110.0f,",
	},
	{
		"name": "pmove_JumpTimeDeltaMin",
		"variable": "g_pmove_jumpTimeDeltaMin_cvar",
		"default": "100.0f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "jumpTimeDeltaMin",
		"parse": "PMOVE_COMPACT_FLOAT( jumpTimeDeltaMin );",
		"json_parse": "PMOVE_FLOAT_FIELD( jumpTimeDeltaMin )",
		"cache": "g_pmoveSettings.jumpTimeDeltaMin = g_pmove_jumpTimeDeltaMin_cvar.value;",
		"serialize": "settings->jumpTimeDeltaMin",
		"refresh": "qtrue",
		"default_field": ".jumpTimeDeltaMin = 100.0f,",
	},
	{
		"name": "pmove_JumpVelocity",
		"variable": "g_pmove_jumpVelocity_cvar",
		"default": "275.0f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "jumpVelocity",
		"parse": "PMOVE_COMPACT_FLOAT( jumpVelocity );",
		"json_parse": "PMOVE_FLOAT_FIELD( jumpVelocity )",
		"cache": "g_pmoveSettings.jumpVelocity = g_pmove_jumpVelocity_cvar.value;",
		"serialize": "settings->jumpVelocity",
		"refresh": "qtrue",
		"default_field": ".jumpVelocity = 275.0f,",
	},
	{
		"name": "pmove_JumpVelocityMax",
		"variable": "g_pmove_jumpVelocityMax_cvar",
		"default": "700.0f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "jumpVelocityMax",
		"parse": "PMOVE_COMPACT_FLOAT( jumpVelocityMax );",
		"json_parse": "PMOVE_FLOAT_FIELD( jumpVelocityMax )",
		"cache": "g_pmoveSettings.jumpVelocityMax = g_pmove_jumpVelocityMax_cvar.value;",
		"serialize": "settings->jumpVelocityMax",
		"refresh": "qtrue",
		"default_field": ".jumpVelocityMax = 700.0f,",
	},
	{
		"name": "pmove_JumpVelocityScaleAdd",
		"variable": "g_pmove_jumpVelocityScaleAdd_cvar",
		"default": "0.4f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "jumpVelocityScaleAdd",
		"parse": "PMOVE_COMPACT_FLOAT( jumpVelocityScaleAdd );",
		"json_parse": "PMOVE_FLOAT_FIELD( jumpVelocityScaleAdd )",
		"cache": "g_pmoveSettings.jumpVelocityScaleAdd = g_pmove_jumpVelocityScaleAdd_cvar.value;",
		"serialize": "settings->jumpVelocityScaleAdd",
		"refresh": "qtrue",
		"default_field": ".jumpVelocityScaleAdd = 0.4f,",
	},
	{
		"name": "pmove_JumpVelocityTimeThreshold",
		"variable": "g_pmove_jumpVelocityTimeThreshold_cvar",
		"default": "500.0f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "jumpVelocityTimeThreshold",
		"parse": "PMOVE_COMPACT_FLOAT( jumpVelocityTimeThreshold );",
		"json_parse": "PMOVE_FLOAT_FIELD( jumpVelocityTimeThreshold )",
		"cache": "g_pmoveSettings.jumpVelocityTimeThreshold = G_PmoveClampRetailMinPositive( g_pmove_jumpVelocityTimeThreshold_cvar.value );",
		"serialize": "settings->jumpVelocityTimeThreshold",
		"refresh": "qtrue",
		"default_field": ".jumpVelocityTimeThreshold = 500.0f,",
	},
	{
		"name": "pmove_JumpVelocityTimeThresholdOffset",
		"variable": "g_pmove_jumpVelocityTimeThresholdOffset_cvar",
		"default": "0.6f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "jumpVelocityTimeThresholdOffset",
		"parse": "PMOVE_COMPACT_FLOAT( jumpVelocityTimeThresholdOffset );",
		"json_parse": "PMOVE_FLOAT_FIELD( jumpVelocityTimeThresholdOffset )",
		"cache": "g_pmoveSettings.jumpVelocityTimeThresholdOffset = G_PmoveClampRetailMinPositive( g_pmove_jumpVelocityTimeThresholdOffset_cvar.value );",
		"serialize": "settings->jumpVelocityTimeThresholdOffset",
		"refresh": "qtrue",
		"default_field": ".jumpVelocityTimeThresholdOffset = 0.6f,",
	},
	{
		"name": "pmove_RampJump",
		"variable": "g_pmove_rampJump_cvar",
		"default": "0",
		"flags": "PMOVE_CVAR_FLAGS_CUSTOM_LATCH",
		"field": "rampJump",
		"parse": "PMOVE_COMPACT_BOOL( rampJump );",
		"json_parse": "PMOVE_BOOL_FIELD( rampJump )",
		"cache": "g_pmoveSettings.rampJump = ( g_pmove_rampJump_cvar.integer != 0 );",
		"serialize": "settings->rampJump ? 1 : 0",
		"refresh": "qtrue",
		"default_field": ".rampJump = qfalse,",
	},
	{
		"name": "pmove_RampJumpScale",
		"variable": "g_pmove_rampJumpScale_cvar",
		"default": "1.0f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "rampJumpScale",
		"parse": "PMOVE_COMPACT_FLOAT( rampJumpScale );",
		"json_parse": "PMOVE_FLOAT_FIELD( rampJumpScale )",
		"cache": "g_pmoveSettings.rampJumpScale = g_pmove_rampJumpScale_cvar.value;",
		"serialize": "settings->rampJumpScale",
		"refresh": "qtrue",
		"default_field": ".rampJumpScale = 1.0f,",
	},
	{
		"name": "pmove_StepJumpVelocity",
		"variable": "g_pmove_stepJumpVelocity_cvar",
		"default": "48.0f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "stepJumpVelocity",
		"parse": "PMOVE_COMPACT_FLOAT( stepJumpVelocity );",
		"json_parse": "PMOVE_FLOAT_FIELD( stepJumpVelocity )",
		"cache": "g_pmoveSettings.stepJumpVelocity = g_pmove_stepJumpVelocity_cvar.value;",
		"serialize": "settings->stepJumpVelocity",
		"refresh": "qtrue",
		"default_field": ".stepJumpVelocity = 48.0f,",
	},
]


PROFILE_UTILITY_PMOVE_CVARS = [
	{
		"name": "pmove_AirStepFriction",
		"variable": "g_pmove_airStepFriction_cvar",
		"default": "0.03f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "airStepFriction",
		"parse": "PMOVE_COMPACT_FLOAT( airStepFriction );",
		"json_parse": "PMOVE_FLOAT_FIELD( airStepFriction )",
		"cache": "g_pmoveSettings.airStepFriction = g_pmove_airStepFriction_cvar.value;",
		"serialize": "settings->airStepFriction",
		"refresh": "qtrue",
		"default_field": ".airStepFriction = 0.03f,",
	},
	{
		"name": "pmove_AirSteps",
		"variable": "g_pmove_airSteps_cvar",
		"default": "1",
		"flags": "PMOVE_CVAR_FLAGS_CUSTOM_LATCH",
		"field": "airSteps",
		"parse": "PMOVE_COMPACT_INT( airSteps );",
		"json_parse": "PMOVE_INT_FIELD( airSteps )",
		"cache": "g_pmoveSettings.airSteps = g_pmove_airSteps_cvar.integer;",
		"serialize": "settings->airSteps",
		"refresh": "qtrue",
		"default_field": ".airSteps = 1,",
	},
	{
		"name": "pmove_BunnyHop",
		"variable": "g_pmove_bunnyHop_cvar",
		"default": "1",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "bunnyHop",
		"parse": "PMOVE_COMPACT_BOOL( bunnyHop );",
		"json_parse": "PMOVE_BOOL_FIELD( bunnyHop )",
		"cache": "g_pmoveSettings.bunnyHop = ( g_pmove_bunnyHop_cvar.integer != 0 );",
		"serialize": "settings->bunnyHop ? 1 : 0",
		"refresh": "qtrue",
		"default_field": ".bunnyHop = qtrue,",
	},
	{
		"name": "pmove_CrouchSlide",
		"variable": "g_pmove_crouchSlide_cvar",
		"default": "0",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY_ONLY",
		"field": "crouchSlide",
		"parse": "PMOVE_COMPACT_BOOL( crouchSlide );",
		"json_parse": "PMOVE_BOOL_FIELD( crouchSlide )",
		"cache": "g_pmoveSettings.crouchSlide = ( g_pmove_crouchSlide_cvar.integer != 0 );",
		"serialize": "settings->crouchSlide ? 1 : 0",
		"refresh": "qfalse",
		"default_field": ".crouchSlide = qfalse,",
	},
	{
		"name": "pmove_CrouchSlideFriction",
		"variable": "g_pmove_crouchSlideFriction_cvar",
		"default": "0.5f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "crouchSlideFriction",
		"parse": "PMOVE_COMPACT_FLOAT( crouchSlideFriction );",
		"json_parse": "PMOVE_FLOAT_FIELD( crouchSlideFriction )",
		"cache": "g_pmoveSettings.crouchSlideFriction = g_pmove_crouchSlideFriction_cvar.value;",
		"serialize": "settings->crouchSlideFriction",
		"refresh": "qtrue",
		"default_field": ".crouchSlideFriction = 0.5f,",
	},
	{
		"name": "pmove_CrouchSlideTime",
		"variable": "g_pmove_crouchSlideTime_cvar",
		"default": "2000",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "crouchSlideTime",
		"parse": "PMOVE_COMPACT_INT( crouchSlideTime );",
		"json_parse": "PMOVE_INT_FIELD( crouchSlideTime )",
		"cache": "g_pmoveSettings.crouchSlideTime = g_pmove_crouchSlideTime_cvar.integer;",
		"serialize": "settings->crouchSlideTime",
		"refresh": "qtrue",
		"default_field": ".crouchSlideTime = 2000,",
	},
	{
		"name": "pmove_CrouchStepJump",
		"variable": "g_pmove_crouchStepJump_cvar",
		"default": "1",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "crouchStepJump",
		"parse": "PMOVE_COMPACT_BOOL( crouchStepJump );",
		"json_parse": "PMOVE_BOOL_FIELD( crouchStepJump )",
		"cache": "g_pmoveSettings.crouchStepJump = ( g_pmove_crouchStepJump_cvar.integer != 0 );",
		"serialize": "settings->crouchStepJump ? 1 : 0",
		"refresh": "qtrue",
		"default_field": ".crouchStepJump = qtrue,",
	},
	{
		"name": "pmove_DoubleJump",
		"variable": "g_pmove_doubleJump_cvar",
		"default": "0",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY_ONLY",
		"field": "doubleJump",
		"parse": "PMOVE_COMPACT_BOOL( doubleJump );",
		"json_parse": "PMOVE_BOOL_FIELD( doubleJump )",
		"cache": "g_pmoveSettings.doubleJump = ( g_pmove_doubleJump_cvar.integer != 0 );",
		"serialize": "settings->doubleJump ? 1 : 0",
		"refresh": "qfalse",
		"default_field": ".doubleJump = qfalse,",
	},
	{
		"name": "pmove_noPlayerClip",
		"variable": "g_pmove_noPlayerClip_cvar",
		"default": "0",
		"flags": "PMOVE_CVAR_FLAGS_CUSTOM_LATCH",
		"field": "noPlayerClip",
		"parse": "PMOVE_COMPACT_BOOL( noPlayerClip );",
		"json_parse": "PMOVE_BOOL_FIELD( noPlayerClip )",
		"cache": "noPlayerClip = ( g_pmove_noPlayerClip_cvar.integer != 0 );",
		"serialize": "settings->noPlayerClip ? 1 : 0",
		"refresh": "qtrue",
		"default_field": ".noPlayerClip = qfalse,",
	},
	{
		"name": "pmove_StepHeight",
		"variable": "g_pmove_stepHeight_cvar",
		"default": "22.0f",
		"flags": "PMOVE_CVAR_FLAGS_CUSTOM_LATCH",
		"field": "stepHeight",
		"parse": "PMOVE_COMPACT_FLOAT( stepHeight );",
		"json_parse": "PMOVE_FLOAT_FIELD( stepHeight )",
		"cache": "g_pmoveSettings.stepHeight = g_pmove_stepHeight_cvar.value;",
		"serialize": "settings->stepHeight",
		"refresh": "qtrue",
		"default_field": ".stepHeight = 22.0f,",
	},
	{
		"name": "pmove_StepJump",
		"variable": "g_pmove_stepJump_cvar",
		"default": "1",
		"flags": "PMOVE_CVAR_FLAGS_CUSTOM_LATCH",
		"field": "stepJump",
		"parse": "PMOVE_COMPACT_BOOL( stepJump );",
		"json_parse": "PMOVE_BOOL_FIELD( stepJump )",
		"cache": "g_pmoveSettings.stepJump = ( g_pmove_stepJump_cvar.integer != 0 );",
		"serialize": "settings->stepJump ? 1 : 0",
		"refresh": "qtrue",
		"default_field": ".stepJump = qtrue,",
	},
	{
		"name": "pmove_velocity_gh",
		"variable": "g_pmove_velocityGh_cvar",
		"default": "800",
		"flags": "PMOVE_CVAR_FLAGS_CUSTOM_LATCH",
		"field": "velocityGh",
		"parse": "PMOVE_COMPACT_FLOAT( velocityGh );",
		"json_parse": "PMOVE_FLOAT_FIELD( velocityGh )",
		"cache": "g_pmoveSettings.velocityGh = G_PmoveClampRetailMinPositive( g_pmove_velocityGh_cvar.value );",
		"serialize": "settings->velocityGh",
		"refresh": "qtrue",
		"default_field": ".velocityGh = 800.0f,",
	},
	{
		"name": "pmove_WaterSwimScale",
		"variable": "g_pmove_waterSwimScale_cvar",
		"default": "0.6f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "waterSwimScale",
		"parse": "PMOVE_COMPACT_FLOAT( waterSwimScale );",
		"json_parse": "PMOVE_FLOAT_FIELD( waterSwimScale )",
		"cache": "g_pmoveSettings.waterSwimScale = g_pmove_waterSwimScale_cvar.value;",
		"serialize": "settings->waterSwimScale",
		"refresh": "qtrue",
		"default_field": ".waterSwimScale = 0.60f,",
	},
	{
		"name": "pmove_WaterWadeScale",
		"variable": "g_pmove_waterWadeScale_cvar",
		"default": "0.8f",
		"flags": "PMOVE_CVAR_FLAGS_FACTORY",
		"field": "waterWadeScale",
		"parse": "PMOVE_COMPACT_FLOAT( waterWadeScale );",
		"json_parse": "PMOVE_FLOAT_FIELD( waterWadeScale )",
		"cache": "g_pmoveSettings.waterWadeScale = g_pmove_waterWadeScale_cvar.value;",
		"serialize": "settings->waterWadeScale",
		"refresh": "qtrue",
		"default_field": ".waterWadeScale = 0.80f,",
	},
	{
		"name": "pmove_WeaponDropTime",
		"variable": "g_pmove_weaponDropTime_cvar",
		"default": "200",
		"flags": "PMOVE_CVAR_FLAGS_CUSTOM_LATCH",
		"field": "weaponDropTime",
		"parse": "PMOVE_COMPACT_INT( weaponDropTime );",
		"json_parse": "PMOVE_INT_FIELD( weaponDropTime )",
		"cache": "g_pmoveSettings.weaponDropTime = g_pmove_weaponDropTime_cvar.integer;",
		"serialize": "settings->weaponDropTime",
		"refresh": "qtrue",
		"default_field": ".weaponDropTime = 200,",
	},
	{
		"name": "pmove_WeaponRaiseTime",
		"variable": "g_pmove_weaponRaiseTime_cvar",
		"default": "200",
		"flags": "PMOVE_CVAR_FLAGS_CUSTOM_LATCH",
		"field": "weaponRaiseTime",
		"parse": "PMOVE_COMPACT_INT( weaponRaiseTime );",
		"json_parse": "PMOVE_INT_FIELD( weaponRaiseTime )",
		"cache": "g_pmoveSettings.weaponRaiseTime = g_pmove_weaponRaiseTime_cvar.integer;",
		"serialize": "settings->weaponRaiseTime",
		"refresh": "qtrue",
		"default_field": ".weaponRaiseTime = 200,",
	},
]


def _function_body(source: str, signature: str) -> str:
	definition = f"{signature} {{"
	try:
		start = source.index(definition)
	except ValueError:
		start = source.index(signature)
	brace = source.index("{", start)
	depth = 1
	position = brace + 1
	while depth > 0:
		if source[position] == "{":
			depth += 1
		elif source[position] == "}":
			depth -= 1
		position += 1

	return source[brace + 1 : position - 1]


def _symbol_comment(map_name: str, normalized_name: str) -> str:
	symbol_map = json.loads((SYMBOL_MAP_DIR / f"{map_name}.json").read_text(encoding="utf-8"))
	for entry in symbol_map["functions"]:
		if entry["normalized_name"] == normalized_name:
			return entry["comment"]

	raise AssertionError(f"{normalized_name} missing from {map_name} symbol map")


def test_selected_pmove_cvars_match_retail_registration_defaults_and_flags() -> None:
	source = G_PMOVE_PATH.read_text(encoding="utf-8")
	register_body = _function_body(source, "void G_RegisterPmoveCvars( void )")

	for cvar in SELECTED_PMOVE_CVARS:
		expected = (
			f'G_PmoveRegisterCvar( &{cvar["variable"]}, "{cvar["name"]}", '
			f'"{cvar["default"]}", {cvar["flags"]} );'
		)
		assert expected in register_body


def test_selected_pmove_cvars_reset_refresh_cache_and_cross_vm_transport() -> None:
	g_pmove = G_PMOVE_PATH.read_text(encoding="utf-8")
	cg_servercmds = CG_SERVERCMDS_PATH.read_text(encoding="utf-8")

	reset_body = _function_body(g_pmove, "void G_PmoveResetFactoryManagedCvars( void )")
	refresh_body = _function_body(g_pmove, "void G_RefreshPmoveSettings( void )")
	cache_body = _function_body(g_pmove, "static void G_PmoveCacheSettings( void )")
	serialize_body = _function_body(
		g_pmove,
		"static qboolean G_PmoveSerializeSettings( const pmove_settings_t *settings, char *buffer, size_t bufferSize )",
	)
	compact_parse_body = _function_body(
		cg_servercmds,
		"static qboolean CG_ParsePmoveCompactSettingsPayload( const char *payload, pmove_settings_t *settings )",
	)
	json_parse_body = _function_body(
		cg_servercmds,
		"static qboolean CG_ParsePmoveJsonSettingsPayload( const char *payload, pmove_settings_t *settings )",
	)

	for cvar in SELECTED_PMOVE_CVARS:
		assert f'trap_Cvar_Set( "{cvar["name"]}", "{cvar["default"]}" );' in reset_body
		assert f'G_PmoveUpdateCvar( &{cvar["variable"]}, "{cvar["name"]}", {cvar["refresh"]} );' in refresh_body
		assert cvar["cache"] in cache_body
		assert f'settings->{cvar["field"]}' in serialize_body
		assert cvar["parse"] in compact_parse_body
		if cvar["field"] == "chainJump":
			assert 'else if ( !Q_stricmp( key, "chainJump" ) ) {' in json_parse_body
			assert "CG_ParsePmoveJsonIntOrBool( &cursor, &parsed.chainJump )" in json_parse_body
		else:
			field_type = "BOOL" if "BOOL" in cvar["parse"] else "INT" if "INT" in cvar["parse"] else "FLOAT"
			assert f"PMOVE_{field_type}_FIELD( {cvar['field']} )" in json_parse_body

	assert serialize_body.index("settings->wishSpeed") < serialize_body.index("settings->airControl")
	assert compact_parse_body.index("PMOVE_COMPACT_FLOAT( wishSpeed );") < compact_parse_body.index("PMOVE_COMPACT_FLOAT( airControl );")


def test_selected_pmove_cvars_have_retail_defaults_and_active_consumers() -> None:
	bg_pmove = BG_PMOVE_PATH.read_text(encoding="utf-8")
	load_body = _function_body(bg_pmove, "static void PM_LoadMoveTuningConstants( void )")
	air_move_body = _function_body(bg_pmove, "static void PM_AirMove( void )")
	friction_body = _function_body(bg_pmove, "static void PM_Friction( void )")
	walk_move_body = _function_body(bg_pmove, "static void PM_WalkMove( void )")
	jump_release_body = _function_body(bg_pmove, "static qboolean PM_ShouldRequireJumpRelease( const pmove_settings_t *settings )")
	mode_body = _function_body(bg_pmove, "static void PM_UpdateJumpVelocityMode( const pmove_settings_t *settings )")

	for cvar in SELECTED_PMOVE_CVARS:
		assert cvar["default_field"] in bg_pmove

	for snippet in (
		"settings->walkAccel",
		"settings->airAccel",
		"settings->airControl",
		"settings->airStopAccel",
		"settings->strafeAccel",
		"settings->circleStrafeFriction",
		"settings->wishSpeed",
		"settings->walkFriction",
		"pm_autohop = settings->autoHop;",
		"PM_UpdateJumpVelocityMode( settings );",
	):
		assert snippet in load_body

	assert "chainJumpMode = settings->chainJump;" in mode_body
	assert mode_body.index("if ( airControlTuning ) {") < mode_body.index("chainJumpMode = settings->chainJump;")
	assert "accelerate = pm_airaccelerate;" in air_move_body
	assert "accelerate = pm_airstopaccelerate;" in air_move_body
	assert "accelerate = pm_strafeaccelerate;" in air_move_body
	assert "wishspeed = pm_wishspeed;" in air_move_body
	assert "PM_AirControl( wishdir, wishspeed );" in air_move_body
	assert "friction = pm_friction;" in friction_body
	assert "friction = pm_circlestrafe_friction;" in friction_body
	assert "accelerate = pm_accelerate;" in walk_move_body
	assert "PM_Accelerate (wishdir, wishspeed, accelerate);" in walk_move_body
	assert "activeSettings->autoHop" in jump_release_body
	assert "activeSettings->bunnyHop" not in jump_release_body


def test_selected_pmove_cvars_are_backed_by_committed_retail_evidence() -> None:
	qagame_register = _symbol_comment("qagame", "G_RegisterCvars")
	qagame_update = _symbol_comment("qagame", "G_UpdateCvars")
	qagame_loader = _symbol_comment("qagame", "PM_LoadMoveTuningConstants")
	qagame_airmove = _symbol_comment("qagame", "PM_AirMove")
	qagame_friction = _symbol_comment("qagame", "PM_Friction")
	qagame_jump = _symbol_comment("qagame", "PM_CheckJump")

	assert "`pmove_*` registrations" in qagame_register
	assert "recovered default strings" in qagame_register
	assert "`pmove_AirControl`" in qagame_update
	assert "callback slots" in qagame_update
	assert "PMF_AIR_CONTROL" in qagame_loader
	assert "pm_wishspeed clamp" in qagame_airmove
	assert "airstop versus strafe" in qagame_airmove
	assert "diagonal circle-strafe overrides" in qagame_friction
	assert "autoHop" in qagame_jump


def test_selected_jump_pmove_cvars_match_retail_registration_defaults_and_flags() -> None:
	source = G_PMOVE_PATH.read_text(encoding="utf-8")
	register_body = _function_body(source, "void G_RegisterPmoveCvars( void )")

	for cvar in JUMP_PMOVE_CVARS:
		expected = (
			f'G_PmoveRegisterCvar( &{cvar["variable"]}, "{cvar["name"]}", '
			f'"{cvar["default"]}", {cvar["flags"]} );'
		)
		assert expected in register_body


def test_selected_jump_pmove_cvars_reset_refresh_cache_and_cross_vm_transport() -> None:
	g_pmove = G_PMOVE_PATH.read_text(encoding="utf-8")
	cg_servercmds = CG_SERVERCMDS_PATH.read_text(encoding="utf-8")

	reset_body = _function_body(g_pmove, "void G_PmoveResetFactoryManagedCvars( void )")
	refresh_body = _function_body(g_pmove, "void G_RefreshPmoveSettings( void )")
	cache_body = _function_body(g_pmove, "static void G_PmoveCacheSettings( void )")
	serialize_body = _function_body(
		g_pmove,
		"static qboolean G_PmoveSerializeSettings( const pmove_settings_t *settings, char *buffer, size_t bufferSize )",
	)
	compact_parse_body = _function_body(
		cg_servercmds,
		"static qboolean CG_ParsePmoveCompactSettingsPayload( const char *payload, pmove_settings_t *settings )",
	)
	json_parse_body = _function_body(
		cg_servercmds,
		"static qboolean CG_ParsePmoveJsonSettingsPayload( const char *payload, pmove_settings_t *settings )",
	)

	for cvar in JUMP_PMOVE_CVARS:
		assert f'trap_Cvar_Set( "{cvar["name"]}", "{cvar["default"]}" );' in reset_body
		assert f'G_PmoveUpdateCvar( &{cvar["variable"]}, "{cvar["name"]}", {cvar["refresh"]} );' in refresh_body
		assert cvar["cache"] in cache_body
		assert cvar["serialize"] in serialize_body
		assert cvar["parse"] in compact_parse_body
		assert cvar["json_parse"] in json_parse_body

	assert serialize_body.index("(int)settings->chainJumpVelocity") < serialize_body.index("settings->jumpTimeDeltaMin")
	assert compact_parse_body.index("parsed.chainJumpVelocity = (float)integerValue;") < compact_parse_body.index("PMOVE_COMPACT_FLOAT( jumpTimeDeltaMin );")
	assert compact_parse_body.index("PMOVE_COMPACT_FLOAT( jumpVelocityTimeThreshold );") < compact_parse_body.index("PMOVE_COMPACT_FLOAT( jumpVelocityTimeThresholdOffset );")


def test_selected_jump_pmove_cvars_have_retail_defaults_and_active_consumers() -> None:
	bg_pmove = BG_PMOVE_PATH.read_text(encoding="utf-8")
	jump_header = BG_PMOVE_JUMP_PATH.read_text(encoding="utf-8")
	takeoff_body = _function_body(
		bg_pmove,
		"static float PM_EvaluateJumpTakeoffVelocity( const pmove_settings_t *settings, qboolean stepJumpActive, int *outTimeDelta )",
	)
	ramp_body = _function_body(
		bg_pmove,
		"static float PM_ApplyRampJumpVerticalVelocity( float jumpVelocity, qboolean fromCrouchStep, const pmove_settings_t *settings )",
	)
	step_body = _function_body(bg_pmove, "static qboolean PM_PrepareStepJumpTakeoff( const pmove_settings_t *settings )")
	crouch_step_body = _function_body(bg_pmove, "static qboolean PM_PrepareCrouchStepJumpTakeoff( const pmove_settings_t *settings )")
	prepare_body = _function_body(bg_pmove, "static qboolean PM_PrepareJumpTakeoff( qboolean allowAirDoubleJump )")
	consumer_sources = "\n".join((takeoff_body, ramp_body, step_body, crouch_step_body, prepare_body, jump_header))

	for cvar in JUMP_PMOVE_CVARS:
		assert cvar["default_field"] in bg_pmove

	for snippet in (
		"settings->chainJumpVelocity",
		"settings->jumpTimeDeltaMin",
		"settings->jumpVelocity",
		"settings->jumpVelocityMax",
		"settings->jumpVelocityScaleAdd",
		"settings->jumpVelocityTimeThreshold",
		"settings->jumpVelocityTimeThresholdOffset",
		"settings->rampJump",
		"settings->rampJumpScale",
		"settings->stepJumpVelocity",
	):
		assert snippet in consumer_sources

	assert "jumpVelocity = ( settings->jumpVelocity > 0.0f ) ? settings->jumpVelocity : JUMP_VELOCITY;" in takeoff_body
	assert "threshold = settings->jumpVelocityTimeThreshold;" in takeoff_body
	assert "jumpVelocity *= PM_EvaluateJumpVelocityScale( pm->ps, settings, pm->cmd.serverTime, NULL );" in takeoff_body
	assert "jumpVelocity += stepJumpActive ? settings->stepJumpVelocity : settings->chainJumpVelocity;" in takeoff_body
	assert "offsetThreshold = threshold * settings->jumpVelocityTimeThresholdOffset;" in takeoff_body
	assert "addVelocity = stepJumpActive ? settings->stepJumpVelocity : settings->chainJumpVelocity;" in takeoff_body
	assert "velocity = pm->ps->velocity[2] * settings->rampJumpScale + jumpVelocity;" in ramp_body
	assert "settings && settings->rampJump && !fromCrouchStep" in ramp_body
	assert "settings && settings->jumpVelocityMax > 0.0f && velocity > settings->jumpVelocityMax" in ramp_body
	assert "velocity = settings->jumpVelocityMax;" in ramp_body
	assert "PM_EvaluateJumpTakeoffVelocity( settings, qtrue, NULL );" in step_body
	assert "PM_ApplyRampJumpVerticalVelocity( jumpVelocity, qfalse, settings );" in step_body
	assert "PM_EvaluateJumpTakeoffVelocity( settings, qtrue, NULL );" in crouch_step_body
	assert "PM_ApplyRampJumpVerticalVelocity( jumpVelocity, qtrue, settings );" in crouch_step_body
	assert "PM_EvaluateJumpTakeoffVelocity( settings, qfalse, &timeDelta );" in prepare_body
	assert "PM_ApplyRampJumpVerticalVelocity( jumpVelocity, qfalse, settings );" in prepare_body
	assert "settings->jumpTimeDeltaMin > 0.0f && timeDelta >= 0" in prepare_body
	assert "settings->jumpVelocityTimeThreshold" in jump_header
	assert "settings->jumpVelocityScaleAdd" in jump_header
	assert "return 1.0f + ( ( threshold - (float)timeDelta ) / threshold ) * scaleAdd;" in jump_header


def test_selected_jump_pmove_cvars_are_backed_by_committed_retail_evidence() -> None:
	qagame_jump = _symbol_comment("qagame", "PM_ApplyJumpTakeoff")
	cgame_jump = _symbol_comment("cgame", "PM_ApplyJumpTakeoff")
	qagame_mapping = (REPO_ROOT / "docs" / "reverse-engineering" / "qagame-mapping.md").read_text(encoding="utf-8")
	cgame_mapping = (REPO_ROOT / "docs" / "reverse-engineering" / "cgame-mapping.md").read_text(encoding="utf-8")

	for comment in (qagame_jump, cgame_jump):
		assert "gradient chain-jump scaler" in comment
		assert "additive chain/step branch" in comment
		assert "PMF_AIR_CONTROL" in comment
		assert "`pmove_StepJumpVelocity`" in comment
		assert "`pmove_ChainJumpVelocity`" in comment
		assert "ramp-accumulated then max-clamped" in comment

	assert "`pmove_JumpVelocityTimeThreshold`" in qagame_mapping
	assert "`pmove_JumpVelocityTimeThresholdOffset`" in qagame_mapping
	assert "vertical ramp-jump accumulation plus max clamp" in cgame_mapping


def test_selected_profile_utility_pmove_cvars_match_retail_registration_defaults_and_flags() -> None:
	source = G_PMOVE_PATH.read_text(encoding="utf-8")
	register_body = _function_body(source, "void G_RegisterPmoveCvars( void )")

	for cvar in PROFILE_UTILITY_PMOVE_CVARS:
		expected = (
			f'G_PmoveRegisterCvar( &{cvar["variable"]}, "{cvar["name"]}", '
			f'"{cvar["default"]}", {cvar["flags"]} );'
		)
		assert expected in register_body


def test_selected_profile_utility_pmove_cvars_reset_refresh_cache_and_cross_vm_transport() -> None:
	g_pmove = G_PMOVE_PATH.read_text(encoding="utf-8")
	cg_servercmds = CG_SERVERCMDS_PATH.read_text(encoding="utf-8")

	reset_body = _function_body(g_pmove, "void G_PmoveResetFactoryManagedCvars( void )")
	refresh_body = _function_body(g_pmove, "void G_RefreshPmoveSettings( void )")
	cache_body = _function_body(g_pmove, "static void G_PmoveCacheSettings( void )")
	serialize_body = _function_body(
		g_pmove,
		"static qboolean G_PmoveSerializeSettings( const pmove_settings_t *settings, char *buffer, size_t bufferSize )",
	)
	compact_parse_body = _function_body(
		cg_servercmds,
		"static qboolean CG_ParsePmoveCompactSettingsPayload( const char *payload, pmove_settings_t *settings )",
	)
	json_parse_body = _function_body(
		cg_servercmds,
		"static qboolean CG_ParsePmoveJsonSettingsPayload( const char *payload, pmove_settings_t *settings )",
	)

	for cvar in PROFILE_UTILITY_PMOVE_CVARS:
		assert f'trap_Cvar_Set( "{cvar["name"]}", "{cvar["default"]}" );' in reset_body
		assert f'G_PmoveUpdateCvar( &{cvar["variable"]}, "{cvar["name"]}", {cvar["refresh"]} );' in refresh_body
		assert cvar["cache"] in cache_body
		assert cvar["serialize"] in serialize_body
		assert cvar["parse"] in compact_parse_body
		assert cvar["json_parse"] in json_parse_body

	assert 'trap_Cvar_Set( "g_instaGib", "0" );' in reset_body
	assert 'G_PmoveUpdateCvar( &g_instaGib, "g_instaGib", qfalse );' in refresh_body
	assert "g_pmoveSettings.noPlayerClip = noPlayerClip;" in cache_body
	assert "CG_ClampPmoveNonNegative( &parsed.velocityGh );" in compact_parse_body
	assert serialize_body.index("settings->wishSpeed") < serialize_body.index("settings->airControl")
	assert serialize_body.index("settings->airControl") < serialize_body.index("settings->crouchSlide ? 1 : 0")
	assert serialize_body.index("settings->crouchSlide ? 1 : 0") < serialize_body.index("settings->doubleJump ? 1 : 0")
	assert compact_parse_body.index("PMOVE_COMPACT_FLOAT( wishSpeed );") < compact_parse_body.index("PMOVE_COMPACT_BOOL( crouchSlide );")
	assert compact_parse_body.index("PMOVE_COMPACT_BOOL( crouchSlide );") < compact_parse_body.index("PMOVE_COMPACT_BOOL( doubleJump );")


def test_selected_profile_utility_pmove_cvars_have_retail_defaults_profile_flags_and_active_consumers() -> None:
	g_pmove = G_PMOVE_PATH.read_text(encoding="utf-8")
	g_config = G_CONFIG_PATH.read_text(encoding="utf-8")
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	bg_pmove = BG_PMOVE_PATH.read_text(encoding="utf-8")

	load_settings_body = _function_body(bg_pmove, "static void PM_LoadMoveSettings( void )")
	load_tuning_body = _function_body(bg_pmove, "static void PM_LoadMoveTuningConstants( void )")
	apply_step_body = _function_body(bg_pmove, "void PM_ApplyStepJump( float stepDelta, qboolean fromCrouchSlide )")
	friction_body = _function_body(bg_pmove, "static void PM_Friction( void )")
	walk_move_body = _function_body(bg_pmove, "static void PM_WalkMove( void )")
	grapple_body = _function_body(bg_pmove, "static void PM_GrappleMove( void )")
	begin_weapon_body = _function_body(bg_pmove, "static void PM_BeginWeaponChange( int weapon )")
	finish_weapon_body = _function_body(bg_pmove, "static void PM_FinishWeaponChange( void )")
	pmove_single_body = _function_body(bg_pmove, "void PmoveSingle (pmove_t *pmove)")
	profile_body = _function_body(g_pmove, "void G_PmoveApplyProfileFlags( playerState_t *ps )")
	physics_body = _function_body(g_pmove, "qboolean G_PmoveHasPhysicsCustomSetting( void )")
	weapon_switch_body = _function_body(g_pmove, "qboolean G_PmoveHasWeaponSwitchingCustomSetting( void )")
	no_clip_body = _function_body(g_pmove, "qboolean G_PmoveHasNoPlayerClipCustomSetting( void )")
	grapple_custom_body = _function_body(g_pmove, "qboolean G_PmoveHasGrappleVelocityCustomSetting( void )")
	config_custom_body = _function_body(g_config, "uint64_t G_ComputeConfigCustomSettingsMask( void )")
	custom_mask_body = _function_body(g_main, "static uint64_t G_ComputeCustomSettingsMask( void )")

	for cvar in PROFILE_UTILITY_PMOVE_CVARS:
		assert cvar["default_field"] in bg_pmove

	for snippet in (
		"swimScale = settings->waterSwimScale;",
		"wadeScale = settings->waterWadeScale;",
		"stepHeight = settings->stepHeight;",
		"pm_swimScale = swimScale;",
		"pm_wadeScale = wadeScale;",
		"pm_stepHeight = stepHeight;",
	):
		assert snippet in load_settings_body

	for snippet in (
		"settings->airStepFriction",
		"settings->airSteps",
		"pm_bunnyhop = settings->bunnyHop;",
		"PM_LoadMoveSettings();",
	):
		assert snippet in load_tuning_body

	assert "if ( !settings->stepJump ) {" in apply_step_body
	assert "if ( !settings->crouchStepJump ) {" in apply_step_body
	assert "friction = settings->crouchSlideFriction;" in friction_body
	assert "if ( friction < 0.0f ) {" in friction_body
	assert "settings->crouchSlideTime > 0" in walk_move_body
	assert "pm->ps->crouchSlideTime = settings->crouchSlideTime;" in walk_move_body
	assert "maxSpeed = settings->velocityGh;" in grapple_body
	assert "maxSpeed = pm_defaultSettings.velocityGh;" in grapple_body
	assert "dropTime = ( settings->weaponDropTime > 0 ) ? settings->weaponDropTime : 200;" in begin_weapon_body
	assert "raiseTime = ( settings->weaponRaiseTime > 0 ) ? settings->weaponRaiseTime : 200;" in finish_weapon_body
	assert pmove_single_body.index("pm->ps->stats[STAT_HEALTH] <= 0 && !pm->ps->powerups[PW_INVULNERABILITY]") < pmove_single_body.index("if ( settings->noPlayerClip )")
	assert "ps->pm_flags &= ~( PMF_CROUCH_SLIDE | PMF_DOUBLE_JUMP | PMF_AIR_CONTROL );" in profile_body
	assert "if ( g_pmoveSettings.crouchSlide ) {" in profile_body
	assert "ps->pm_flags |= PMF_CROUCH_SLIDE;" in profile_body
	assert "if ( g_pmoveSettings.doubleJump ) {" in profile_body
	assert "ps->pm_flags |= PMF_DOUBLE_JUMP;" in profile_body
	assert "if ( g_pmoveSettings.airControl > 0.0f ) {" in profile_body
	assert "ps->pm_flags |= PMF_AIR_CONTROL;" in profile_body
	assert "ps->crouchSlideTime = 0;" in profile_body

	for snippet in (
		"g_pmove_airSteps_cvar.integer != 1",
		"g_pmove_bunnyHop_cvar.integer != 1",
		"g_pmove_stepJump_cvar.integer != 1",
		"g_pmove_stepHeight_cvar.value != 22.0f",
	):
		assert snippet in physics_body

	assert "g_pmove_weaponRaiseTime_cvar.integer != 200" in weapon_switch_body
	assert "g_pmove_weaponDropTime_cvar.integer != 200" in weapon_switch_body
	assert "return ( g_pmove_noPlayerClip_cvar.integer != 0 ) ? qtrue : qfalse;" in no_clip_body
	assert "return ( g_pmove_velocityGh_cvar.value != 800.0f ) ? qtrue : qfalse;" in grapple_custom_body
	assert "G_PmoveHasGrappleVelocityCustomSetting()" in config_custom_body
	assert "mask |= CUSTOM_SETTING_GRAPPLING_HOOK;" in config_custom_body
	assert "G_PmoveHasPhysicsCustomSetting()" in custom_mask_body
	assert "G_PmoveHasWeaponSwitchingCustomSetting()" in custom_mask_body
	assert "G_PmoveHasNoPlayerClipCustomSetting()" in custom_mask_body


def test_selected_profile_utility_pmove_cvars_are_backed_by_committed_retail_evidence() -> None:
	qagame_register = _symbol_comment("qagame", "G_RegisterCvars")
	qagame_update = _symbol_comment("qagame", "G_UpdateCvars")
	qagame_friction = _symbol_comment("qagame", "PM_Friction")
	qagame_grapple = _symbol_comment("qagame", "PM_GrappleMove")
	qagame_begin_weapon = _symbol_comment("qagame", "PM_BeginWeaponChange")
	qagame_finish_weapon = _symbol_comment("qagame", "PM_FinishWeaponChange")
	qagame_pmove_single = _symbol_comment("qagame", "PmoveSingle")
	qagame_spawn = _symbol_comment("qagame", "ClientSpawn")
	cgame_friction = _symbol_comment("cgame", "PM_Friction")
	cgame_grapple = _symbol_comment("cgame", "PM_GrappleMove")
	cgame_pmove_single = _symbol_comment("cgame", "PmoveSingle")
	qagame_mapping = (REPO_ROOT / "docs" / "reverse-engineering" / "qagame-mapping.md").read_text(encoding="utf-8")
	cgame_bg_plan = (REPO_ROOT / "docs" / "reverse-engineering" / "cgame-bg-parity-implementation-plan.md").read_text(encoding="utf-8")

	assert "`pmove_*` registrations" in qagame_register
	assert "callback/no-callback split" in qagame_register
	assert "pmove slab callbacks update cached movement globals" in qagame_update
	assert "`pmove_CrouchSlide`, and `pmove_DoubleJump` intentionally have null callback slots" in qagame_update
	assert "crouch-slide and diagonal circle-strafe overrides" in qagame_friction
	assert "crouch-slide and diagonal circle-strafe friction overrides" in cgame_friction
	assert "pmove_velocity_gh pull speed" in qagame_grapple
	assert "g_velocity_gh" in qagame_grapple
	assert "grapplePoint - 16 * forward" in cgame_grapple
	assert "starts the drop timer" in qagame_begin_weapon
	assert "applies the raise timer" in qagame_finish_weapon
	assert "consumes the movement-profile flags already present in playerState" in qagame_pmove_single
	assert "consumes the movement-profile flags already present in playerState" in cgame_pmove_single
	assert "PMF_CROUCH_SLIDE / PMF_DOUBLE_JUMP / PMF_AIR_CONTROL profile bits" in qagame_spawn
	assert "profile/utility pmove cvar mapping sentinel" in qagame_mapping
	assert "`pmove_AirStepFriction`" in qagame_mapping
	assert "`pmove_WeaponRaiseTime`" in qagame_mapping
	assert "profile/utility pmove cvar mapping sentinel" in cgame_bg_plan
	assert "`pmove_CrouchSlide`" in cgame_bg_plan
	assert "`pmove_velocity_gh`" in cgame_bg_plan
