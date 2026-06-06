from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BG_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"
BG_PUBLIC_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_public.h"
G_CLIENT_PATH = REPO_ROOT / "src" / "code" / "game" / "g_client.c"
G_LOCAL_PATH = REPO_ROOT / "src" / "code" / "game" / "g_local.h"
G_MISC_PATH = REPO_ROOT / "src" / "code" / "game" / "g_misc.c"
AI_DMQ3_PATH = REPO_ROOT / "src" / "code" / "game" / "ai_dmq3.c"
BOTLIB_AAS_MOVE_PATH = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_move.c"
BOTLIB_AI_MOVE_PATH = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_move.c"
G_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "g_pmove.c"
CG_SERVERCMDS_PATH = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CLEAN_PMOVE_HEADER_PATH = REPO_ROOT / "src-re" / "clean" / "include" / "qlr_game_pmove.h"
CLEAN_PMOVE_SOURCE_PATH = REPO_ROOT / "src-re" / "clean" / "gameplay" / "pmove.c"
SYMBOL_MAP_DIR = REPO_ROOT / "references" / "symbol-maps"
SYMBOL_ALIASES_PATH = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"


def _function_body(signature: str) -> str:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	match = re.search(
		rf"(?:static )?(?:float|qboolean|void) {re.escape(signature)}\s*\([^)]*\)\s*\{{(?P<body>.*?)^\}}",
		source,
		re.MULTILINE | re.DOTALL,
	)

	assert match is not None, f"{signature} definition missing"
	return match.group("body")


def _symbol_comment(map_name: str, normalized_name: str) -> str:
	symbol_map = json.loads((SYMBOL_MAP_DIR / f"{map_name}.json").read_text(encoding="utf-8"))
	for entry in symbol_map["functions"]:
		if entry["normalized_name"] == normalized_name:
			return entry["comment"]

	raise AssertionError(f"{normalized_name} missing from {map_name} symbol map")


def _body_from_source(path: Path, signature: str) -> str:
	source = path.read_text(encoding="utf-8")
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


def test_pmove_surface_drops_the_source_only_parameter_block() -> None:
	bg_public = BG_PUBLIC_PATH.read_text(encoding="utf-8")
	bg_pmove = BG_PMOVE_PATH.read_text(encoding="utf-8")
	pmove_struct = bg_public[bg_public.index("// state (in / out)") : bg_public.index("} pmove_t;")]

	assert "typedef struct pmoveParams_s" not in bg_public
	assert "pmoveParams_t" not in bg_public
	assert "pmoveParams;" not in bg_public
	assert "PM_LoadMoveParams" not in bg_pmove
	assert "pm_defaultParams" not in bg_pmove
	assert "int\t\t\tframecount;" not in pmove_struct
	assert pmove_struct.index("qboolean\tgauntletHit;") < pmove_struct.index("// results (out)")
	assert pmove_struct.index("// results (out)") < pmove_struct.index("int\t\t\tnumtouch;")
	assert pmove_struct.index("int\t\t\tnumtouch;") < pmove_struct.index("int\t\t\ttouchents[MAXTOUCH];")


def test_retail_pmove_flag_bits_match_the_committed_hlil_layout() -> None:
	bg_public = BG_PUBLIC_PATH.read_text(encoding="utf-8")
	msg_source = (REPO_ROOT / "src" / "code" / "qcommon" / "msg.c").read_text(encoding="utf-8")

	assert "#define PMF_ATTACK_LOCKOUT\t4" in bg_public
	assert "#define\tPMF_TIME_LAND\t\t32" in bg_public
	assert "#define\tPMF_TIME_KNOCKBACK\t64" in bg_public
	assert "#define\tPMF_TIME_WATERJUMP\t128" in bg_public
	assert "#define PMF_NO_MOVE\t\t\t256" in bg_public
	assert "#define\tPMF_RESPAWNED\t\t512" in bg_public
	assert "#define\tPMF_USE_ITEM_HELD\t1024" in bg_public
	assert "#define PMF_GRAPPLE_PULL\t2048" in bg_public
	assert "#define PMF_FOLLOW\t\t\t4096" in bg_public
	assert "#define PMF_SCOREBOARD\t\t8192" in bg_public
	assert "#define PMF_INVULEXPAND\t\t16384" in bg_public
	assert "#define PMF_WEAPON_RESET\t32768" in bg_public
	assert "#define PMF_AIR_CONTROL\t\t65536" in bg_public
	assert "PMF_RAMP_JUMP" not in bg_public
	assert "#define PMF_DOUBLE_JUMP\t\t131072" in bg_public
	assert "PMF_CHAIN_JUMP" not in bg_public
	assert "#define PMF_REQUIRE_JUMP_RELEASE\t262144" in bg_public
	assert "#define PMF_CROUCH_SLIDE\t1048576" in bg_public
	assert "#define\tPMF_ALL_TIMES\t(PMF_TIME_WATERJUMP|PMF_TIME_LAND|PMF_TIME_KNOCKBACK)" in bg_public
	assert "{ PSF(pm_flags), 24 }" in msg_source


def test_load_move_tuning_constants_restores_the_retail_air_control_bundles() -> None:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	body = _function_body("PM_LoadMoveTuningConstants")
	mode_body = _function_body("PM_UpdateJumpVelocityMode")
	takeoff_body = _function_body("PM_EvaluateJumpTakeoffVelocity")

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
	assert "airControlTuning = ( pm->ps->pm_flags & PMF_AIR_CONTROL ) ? qtrue : qfalse;" in body
	assert "PM_UpdateJumpVelocityMode( settings );" in body
	assert "PM_JUMP_VELOCITY_MODE_AIR_CONTROL" in source
	assert mode_body.index("if ( airControlTuning ) {") < mode_body.index("chainJumpMode = settings->chainJump;")
	assert "pm_jumpVelocityMode = PM_JUMP_VELOCITY_MODE_AIR_CONTROL;" in mode_body
	assert "fadeWindow" not in takeoff_body
	assert "jumpVelocity += ( ( offsetThreshold - (float)timeDelta ) / offsetThreshold ) * addVelocity + addVelocity;" in takeoff_body
	assert "stepJumpActive ? settings->stepJumpVelocity : settings->chainJumpVelocity" in takeoff_body
	assert "pm_accelerate = PM_LoadMoveTuningFloat(" in body
	assert "pm_airaccelerate = PM_LoadMoveTuningFloat(" in body
	assert "pm_aircontrol = PM_LoadMoveTuningFloat(" in body
	assert "pm_retailAirControlTuning.airControl,\n\t\tairControlTuning," in body
	assert "pm_airsteps = airControlTuning" in body
	assert "pm_circlestrafe_friction = PM_LoadMoveTuningFloat(" in body
	assert "pm_wishspeed = PM_LoadMoveTuningFloat(" in body
	assert "PM_LoadMoveSettings();" in body


def test_pmove_configstring_uses_the_retail_compact_token_order() -> None:
	serialize_body = _body_from_source(
		G_PMOVE_PATH,
		"static qboolean G_PmoveSerializeSettings( const pmove_settings_t *settings, char *buffer, size_t bufferSize )",
	)
	parse_body = _body_from_source(
		CG_SERVERCMDS_PATH,
		"static qboolean CG_ParsePmoveCompactSettingsPayload( const char *payload, pmove_settings_t *settings )",
	)
	cg_servercmds_source = CG_SERVERCMDS_PATH.read_text(encoding="utf-8")
	required_tokens = [
		"settings->airAccel",
		"settings->airStepFriction",
		"settings->airSteps",
		"settings->airStopAccel",
		"settings->autoHop ? 1 : 0",
		"settings->bunnyHop ? 1 : 0",
		"settings->chainJump",
		"(int)settings->chainJumpVelocity",
		"settings->circleStrafeFriction",
		"settings->crouchSlideFriction",
		"settings->crouchSlideTime",
		"settings->crouchStepJump ? 1 : 0",
		"settings->jumpTimeDeltaMin",
		"settings->jumpVelocity",
		"settings->jumpVelocityMax",
		"settings->jumpVelocityScaleAdd",
		"settings->jumpVelocityTimeThreshold",
		"settings->jumpVelocityTimeThresholdOffset",
		"settings->noPlayerClip ? 1 : 0",
		"settings->rampJump ? 1 : 0",
		"settings->rampJumpScale",
		"settings->stepHeight",
		"settings->stepJump ? 1 : 0",
		"settings->stepJumpVelocity",
		"settings->strafeAccel",
		"settings->velocityGh",
		"settings->walkAccel",
		"settings->walkFriction",
		"settings->waterSwimScale",
		"settings->waterWadeScale",
		"settings->weaponDropTime",
		"settings->weaponRaiseTime",
		"settings->wishSpeed",
	]
	parse_tokens = [
		"PMOVE_COMPACT_FLOAT( airAccel );",
		"PMOVE_COMPACT_FLOAT( airStepFriction );",
		"PMOVE_COMPACT_INT( airSteps );",
		"PMOVE_COMPACT_FLOAT( airStopAccel );",
		"PMOVE_COMPACT_BOOL( autoHop );",
		"PMOVE_COMPACT_BOOL( bunnyHop );",
		"PMOVE_COMPACT_INT( chainJump );",
		"parsed.chainJumpVelocity = (float)integerValue;",
		"PMOVE_COMPACT_FLOAT( circleStrafeFriction );",
		"PMOVE_COMPACT_FLOAT( crouchSlideFriction );",
		"PMOVE_COMPACT_INT( crouchSlideTime );",
		"PMOVE_COMPACT_BOOL( crouchStepJump );",
		"PMOVE_COMPACT_FLOAT( jumpTimeDeltaMin );",
		"PMOVE_COMPACT_FLOAT( jumpVelocity );",
		"PMOVE_COMPACT_FLOAT( jumpVelocityMax );",
		"PMOVE_COMPACT_FLOAT( jumpVelocityScaleAdd );",
		"PMOVE_COMPACT_FLOAT( jumpVelocityTimeThreshold );",
		"PMOVE_COMPACT_FLOAT( jumpVelocityTimeThresholdOffset );",
		"PMOVE_COMPACT_BOOL( noPlayerClip );",
		"PMOVE_COMPACT_BOOL( rampJump );",
		"PMOVE_COMPACT_FLOAT( rampJumpScale );",
		"PMOVE_COMPACT_FLOAT( stepHeight );",
		"PMOVE_COMPACT_BOOL( stepJump );",
		"PMOVE_COMPACT_FLOAT( stepJumpVelocity );",
		"PMOVE_COMPACT_FLOAT( strafeAccel );",
		"PMOVE_COMPACT_FLOAT( velocityGh );",
		"PMOVE_COMPACT_FLOAT( walkAccel );",
		"PMOVE_COMPACT_FLOAT( walkFriction );",
		"PMOVE_COMPACT_FLOAT( waterSwimScale );",
		"PMOVE_COMPACT_FLOAT( waterWadeScale );",
		"PMOVE_COMPACT_INT( weaponDropTime );",
		"PMOVE_COMPACT_INT( weaponRaiseTime );",
		"PMOVE_COMPACT_FLOAT( wishSpeed );",
	]
	position = -1

	assert "JSON payload" not in serialize_body
	assert "weaponReloadTimes" not in serialize_body
	assert "Retail cgame consumes only the first 33 tokens." in serialize_body
	assert "Retail cgame consumes the first\n33 tokens" in cg_servercmds_source
	assert "CG_ParsePmoveJsonSettingsPayload" in cg_servercmds_source

	for token in required_tokens:
		next_position = serialize_body.index(token, position + 1)
		assert next_position > position
		position = next_position

	position = -1
	for token in parse_tokens:
		next_position = parse_body.index(token, position + 1)
		assert next_position > position
		position = next_position

	assert parse_body.index("PMOVE_COMPACT_FLOAT( wishSpeed );") < parse_body.index("PMOVE_COMPACT_FLOAT( airControl );")
	assert parse_body.index("PMOVE_COMPACT_BOOL( crouchSlide );") < parse_body.index("PMOVE_COMPACT_BOOL( doubleJump );")
	assert "flightThrust" not in serialize_body
	assert "flightThrust" not in parse_body
	assert "CG_ClampPmoveNonNegative( &parsed.jumpVelocityTimeThreshold );" in parse_body
	assert "CG_ClampPmoveNonNegative( &parsed.jumpVelocityTimeThresholdOffset );" in parse_body
	assert "CG_ClampPmoveNonNegative( &parsed.velocityGh );" in parse_body


def test_jump_release_override_uses_the_recovered_cg_autohop_flag() -> None:
	body = _function_body("PM_ShouldRequireJumpRelease")
	prepare_body = _function_body("PM_PrepareJumpTakeoff")

	assert "pm->ps->pm_flags & PMF_REQUIRE_JUMP_RELEASE" in body
	assert body.index("PMF_REQUIRE_JUMP_RELEASE") < body.index("activeSettings = settings ? settings : PM_GetActiveSettings();")
	assert "activeSettings->autoHop" in body
	assert "activeSettings->bunnyHop" not in body
	assert "pm_bunnyhop" not in body
	assert "releaseRequired = PM_ShouldRequireJumpRelease( settings );" in prepare_body
	assert "if ( releaseRequired && ( pm->ps->pm_flags & PMF_RESPAWNED ) ) {" in prepare_body
	assert prepare_body.index("releaseRequired = PM_ShouldRequireJumpRelease( settings );") < prepare_body.index("PMF_RESPAWNED")


def test_build_wish_move_3d_uses_the_shared_retail_axis_builder() -> None:
	body = _function_body("PM_BuildWishMove3D")

	assert "scale = PM_CmdScale( &pm->cmd );" in body
	assert "wishvel[i] = scale * pml.forward[i] * pm->cmd.forwardmove + scale * pml.right[i] * pm->cmd.rightmove;" in body
	assert "wishvel[2] += scale * pm->cmd.upmove;" in body
	assert "*wishspeed = VectorNormalize( wishdir );" in body


def test_3d_move_paths_share_the_retail_wish_builder() -> None:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	fly_body = _function_body("PM_FlyMove")

	assert source.count("PM_BuildWishMove3D( wishdir, &wishspeed )") >= 4
	assert "VectorSet( wishdir, 0.0f, 0.0f, -1.0f );" in source
	assert "PM_Friction ();" in fly_body
	assert "PM_BuildWishMove3D( wishdir, &wishspeed );" in fly_body
	assert "PM_Accelerate (wishdir, wishspeed, pm_flyaccelerate);" in fly_body
	assert "PM_StepSlideMove( qfalse );" in fly_body
	assert "PM_GetActiveSettings" not in fly_body
	assert "flightThrust" not in fly_body
	assert "STAT_PLAYER_ITEM_THRUST" not in fly_body
	assert "STAT_PLAYER_ITEM_TIME" not in fly_body
	assert "PMF_USE_ITEM_HELD" not in fly_body


def test_pm_accelerate_stays_on_the_generic_retail_body() -> None:
	body = _function_body("PM_Accelerate")

	assert "currentSpeed = DotProduct( pm->ps->velocity, wishdir );" in body
	assert "addSpeed = wishspeed - currentSpeed;" in body
	assert "accelSpeed = accel * pml.frametime * wishspeed;" in body
	assert "pm_wishspeed" not in body
	assert "pm_airstopaccelerate" not in body
	assert "pm_strafeaccelerate" not in body
	assert "airborneMove" not in body


def test_command_vector_helpers_keep_retail_math_contracts() -> None:
	clip_body = _function_body("PM_ClipVelocity")
	accelerate_body = _function_body("PM_Accelerate")
	cmdscale_body = _body_from_source(BG_PMOVE_PATH, "static float PM_CmdScale( usercmd_t *cmd )")
	movement_dir_body = _function_body("PM_SetMovementDir")

	assert "backoff = DotProduct (in, normal);" in clip_body
	assert "backoff *= overbounce;" in clip_body
	assert "backoff /= overbounce;" in clip_body
	assert "out[i] = in[i] - change;" in clip_body
	assert "accelSpeed = accel * pml.frametime * wishspeed;" in accelerate_body
	assert "if ( accelSpeed > addSpeed )" in accelerate_body
	assert "pm->ps->velocity[i] += accelSpeed * wishdir[i];" in accelerate_body
	assert "max = abs( cmd->forwardmove );" in cmdscale_body
	assert "total = sqrt( cmd->forwardmove * cmd->forwardmove" in cmdscale_body
	assert "scale = (float)pm->ps->speed * max / ( 127.0 * total );" in cmdscale_body
	assert "pm->ps->movementDir = 0;" in movement_dir_body
	assert "pm->ps->movementDir = 7;" in movement_dir_body
	assert "if ( pm->ps->movementDir == 2 )" in movement_dir_body
	assert "pm->ps->movementDir = 1;" in movement_dir_body
	assert "if ( pm->ps->movementDir == 6 )" in movement_dir_body
	assert "pm->ps->movementDir = 7;" in movement_dir_body

	for map_name in ("qagame", "cgame"):
		for symbol in ("PM_ClipVelocity", "PM_Accelerate", "PM_CmdScale", "PM_SetMovementDir"):
			assert "fixture" in _symbol_comment(map_name, symbol)


def test_symbol_maps_record_the_recovered_airmove_accel_edges() -> None:
	qagame_airmove = _symbol_comment("qagame", "PM_AirMove")
	cgame_airmove = _symbol_comment("cgame", "PM_AirMove")

	for comment in (qagame_airmove, cgame_airmove):
		assert "airstop" in comment
		assert "strafe" in comment
		assert "pm_wishspeed" in comment
		assert "PM_Accelerate" in comment
		assert "PM_AirControl" in comment
		assert "PM_InvulnerabilityMove" in comment
		assert "PMF_DOUBLE_JUMP" in comment


def test_symbol_maps_record_the_recovered_walkmove_edges() -> None:
	qagame_walk = _symbol_comment("qagame", "PM_WalkMove")
	cgame_walk = _symbol_comment("cgame", "PM_WalkMove")
	cgame_invulnerability = _symbol_comment("cgame", "PM_InvulnerabilityMove")

	for comment in (qagame_walk, cgame_walk):
		assert "PM_ShouldUseInvulnerabilityMove" in comment
		assert "PM_StepSlideMove(qfalse)" in comment
		assert "PM_InvulnerabilityMove" in comment
		assert "crouch-slide" in comment
		assert "0.75" in comment
		assert "slick/knockback" in comment
		assert "PMF_TIME_KNOCKBACK" in comment
		assert "pm_airaccelerate" in comment
		assert "pm_accelerate" in comment

	assert "walk and air movement tails" in cgame_invulnerability
	assert "stub remains minimal" not in cgame_invulnerability


def test_symbol_maps_record_the_recovered_3d_move_leaf_edges() -> None:
	for map_name in ("qagame", "cgame"):
		water = _symbol_comment(map_name, "PM_WaterMove")
		fly = _symbol_comment(map_name, "PM_FlyMove")
		ladder = _symbol_comment(map_name, "PM_LadderMove")
		noclip = _symbol_comment(map_name, "PM_NoclipMove")

		for comment in (water, fly, ladder, noclip):
			assert "PM_BuildWishMove3D" in comment
			assert "PM_Accelerate" in comment

		assert "-60" in water
		assert "pm_wateraccelerate" in water
		assert "PM_SlideMove(qfalse)" in water

		assert "spectator" in fly
		assert "flight-powerup" in fly
		assert "pm_flyaccelerate" in fly
		assert "PM_StepSlideMove(qfalse)" in fly

		assert "0.66" in ladder
		assert "66%" in ladder
		assert "pm_accelerate" in ladder

		assert "DEFAULT_VIEWHEIGHT" in noclip
		assert "1.5x friction" in noclip
		assert "frametime * velocity" in noclip


def test_symbol_maps_record_the_recovered_ground_contact_edges() -> None:
	for map_name in ("qagame", "cgame"):
		correct_all_solid = _symbol_comment(map_name, "PM_CorrectAllSolid")
		ground_trace_missed = _symbol_comment(map_name, "PM_GroundTraceMissed")
		ground_trace = _symbol_comment(map_name, "PM_GroundTrace")
		water_level = _symbol_comment(map_name, "PM_SetWaterLevel")

		assert "0.25" in correct_all_solid
		assert "groundEntityNum" in correct_all_solid
		assert "groundTraceLatest" not in correct_all_solid
		assert "pml.groundPlane" in correct_all_solid
		assert "pml.walking" in correct_all_solid

		assert "64" in ground_trace_missed
		assert "LEGS_JUMP" in ground_trace_missed
		assert "LEGS_JUMPB" in ground_trace_missed
		assert "PMF_BACKWARDS_JUMP" in ground_trace_missed
		assert "groundEntityNum" in ground_trace_missed
		assert "groundTraceLatest" not in ground_trace_missed

		assert "0.25" in ground_trace
		assert "kickoff dot > 10" in ground_trace
		assert "groundTraceLatest" not in ground_trace
		assert "pml.groundTrace" in ground_trace
		assert "PMF_TIME_WATERJUMP" in ground_trace
		assert "PMF_TIME_LAND" in ground_trace
		assert "250 ms" in ground_trace
		assert "PM_RecordGroundContact" not in ground_trace
		assert "PM_AddTouchEnt" in ground_trace

		assert "MASK_WATER" in water_level
		assert "MINS_Z + 1" in water_level
		assert "viewheight" in water_level


def test_symbol_maps_record_the_recovered_footstep_edges() -> None:
	for map_name in ("qagame", "cgame"):
		footsteps = _symbol_comment(map_name, "PM_Footsteps")

		assert "crouch-slide" in footsteps
		assert "LEGS_IDLECR" in footsteps
		assert "LEGS_SWIM" in footsteps
		assert "xyspeed < 5" in footsteps
		assert "bobCycle" in footsteps
		assert "axis-speed" in footsteps
		assert "EV_FOOTSPLASH" in footsteps
		assert "EV_SWIM" in footsteps


def test_friction_restores_the_retail_circle_strafe_branch() -> None:
	body = _function_body("PM_Friction")

	assert "friction = pm_friction;" in body
	assert "friction = settings->crouchSlideFriction;" in body
	assert "&& settings->crouchSlide" not in body
	assert "pm_aircontrol > 0.0f && pm->cmd.forwardmove && pm->cmd.rightmove" in body
	assert "pm->ps->movementDir == 1 || pm->ps->movementDir == 3" in body
	assert "pm->ps->movementDir == 5 || pm->ps->movementDir == 7" in body
	assert "friction = pm_circlestrafe_friction;" in body
	assert "drop += control * friction * pml.frametime;" in body
	assert "if ( pm->ps->pm_type == PM_FREEZE || ( pm->ps->pm_flags & PMF_SCOREBOARD ) ) {" in body
	assert "drop *= 0.25f;" in body
	assert body.index("if ( pm->ps->pm_type == PM_SPECTATOR)") < body.index("drop *= 0.25f;")
	assert body.index("drop *= 0.25f;") < body.index("newspeed = speed - drop;")


def test_symbol_maps_record_the_recovered_friction_edges() -> None:
	qagame_friction = _symbol_comment("qagame", "PM_Friction")
	cgame_friction = _symbol_comment("cgame", "PM_Friction")

	for comment in (qagame_friction, cgame_friction):
		assert "PMF_TIME_KNOCKBACK" in comment
		assert "crouch-slide" in comment
		assert "circle-strafe" in comment
		assert "PM_FREEZE" in comment
		assert "PMF_SCOREBOARD" in comment
		assert "0.25" in comment


def test_knockback_time_blocks_ground_control_until_drop_timers_expire() -> None:
	friction_body = _function_body("PM_Friction")
	walk_body = _function_body("PM_WalkMove")
	drop_timers_body = _function_body("PM_DropTimers")
	teleport_comment = _symbol_comment("qagame", "TeleportPlayer")
	bot_setup_comment = _symbol_comment("qagame", "BotSetupForMovement")
	spawn_body = _body_from_source(
		G_CLIENT_PATH,
		"void ClientSpawn(gentity_t *ent)",
	)
	teleport_body = _body_from_source(
		G_MISC_PATH,
		"void TeleportPlayer( gentity_t *player, vec3_t origin, vec3_t angles )",
	)
	bot_setup_body = _body_from_source(
		AI_DMQ3_PATH,
		"void BotSetupForMovement(bot_state_t *bs)",
	)

	assert "if ( !( pm->ps->pm_flags & PMF_TIME_KNOCKBACK ) ) {" in friction_body
	assert "drop += control * friction * pml.frametime;" in friction_body
	assert friction_body.index("if ( pml.walking && !(pml.groundTrace.surfaceFlags & SURF_SLICK) )") < friction_body.index("if ( !( pm->ps->pm_flags & PMF_TIME_KNOCKBACK ) ) {")
	assert friction_body.index("if ( !( pm->ps->pm_flags & PMF_TIME_KNOCKBACK ) ) {") < friction_body.index("drop += control * friction * pml.frametime;")

	assert "if ( ( pml.groundTrace.surfaceFlags & SURF_SLICK ) || pm->ps->pm_flags & PMF_TIME_KNOCKBACK ) {" in walk_body
	assert "accelerate = pm_airaccelerate;" in walk_body
	assert "accelerate = pm_accelerate;" in walk_body
	assert "pm->ps->velocity[2] -= pm->ps->gravity * pml.frametime;" in walk_body
	assert walk_body.index("accelerate = pm_airaccelerate;") < walk_body.index("PM_Accelerate (wishdir, wishspeed, accelerate);")
	gravity_position = walk_body.index("pm->ps->velocity[2] -= pm->ps->gravity * pml.frametime;")
	assert gravity_position < walk_body.index("PM_ClipVelocity (pm->ps->velocity", gravity_position)

	assert "pm->ps->pm_flags &= ~PMF_ALL_TIMES;" in drop_timers_body
	assert "pm->ps->pm_time = 0;" in drop_timers_body
	assert drop_timers_body.index("pm->ps->pm_flags &= ~PMF_ALL_TIMES;") < drop_timers_body.index("pm->ps->pm_time = 0;")

	assert "client->ps.pm_flags |= PMF_TIME_KNOCKBACK;" in spawn_body
	assert "client->ps.pm_time = 100;" in spawn_body
	assert spawn_body.index("client->ps.pm_flags |= PMF_TIME_KNOCKBACK;") < spawn_body.index("client->ps.pm_time = 100;")
	assert "player->client->ps.pm_time = 160;" in teleport_body
	assert "player->client->ps.pm_flags |= PMF_TIME_KNOCKBACK;" in teleport_body
	assert teleport_body.index("player->client->ps.pm_time = 160;") < teleport_body.index("player->client->ps.pm_flags |= PMF_TIME_KNOCKBACK;")
	assert "pm_time = 160" in teleport_comment
	assert "PMF_TIME_KNOCKBACK" in teleport_comment

	assert "if ((bs->cur_ps.pm_flags & PMF_TIME_KNOCKBACK) && (bs->cur_ps.pm_time > 0)) {" in bot_setup_body
	assert "initmove.or_moveflags |= MFL_TELEPORTED;" in bot_setup_body
	assert "if ((bs->cur_ps.pm_flags & PMF_TIME_WATERJUMP) && (bs->cur_ps.pm_time > 0)) {" in bot_setup_body
	assert "initmove.or_moveflags |= MFL_WATERJUMP;" in bot_setup_body
	assert bot_setup_body.index("PMF_TIME_KNOCKBACK") < bot_setup_body.index("PMF_TIME_WATERJUMP")
	assert "PMF_TIME_KNOCKBACK" in bot_setup_comment
	assert "MFL_TELEPORTED" in bot_setup_comment


def test_botlib_knockback_prediction_and_teleported_blocking_are_mapped() -> None:
	weapon_jump_body = _body_from_source(
		BOTLIB_AAS_MOVE_PATH,
		"float AAS_WeaponJumpZVelocity(vec3_t origin, float radiusdamage)",
	)
	rocket_jump_body = _body_from_source(
		BOTLIB_AAS_MOVE_PATH,
		"float AAS_RocketJumpZVelocity(vec3_t origin)",
	)
	bfg_jump_body = _body_from_source(
		BOTLIB_AAS_MOVE_PATH,
		"float AAS_BFGJumpZVelocity(vec3_t origin)",
	)
	bot_init_body = _body_from_source(
		BOTLIB_AI_MOVE_PATH,
		"void BotInitMoveState(int handle, bot_initmove_t *initmove)",
	)
	bot_teleport_body = _body_from_source(
		BOTLIB_AI_MOVE_PATH,
		"bot_moveresult_t BotTravel_Teleport(bot_movestate_t *ms, aas_reachability_t *reach)",
	)
	aliases = json.loads(SYMBOL_ALIASES_PATH.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	for expected in (
		"viewangles[PITCH] = 90;",
		"vec3_t rocketoffset = {8, 8, -8};",
		"VectorMA(start, 500, forward, end);",
		"points = radiusdamage - 0.5 * VectorLength(v);",
		"points *= 0.5;",
		"mass = 200;",
		"knockback = points;",
		"VectorScale(dir, 1600.0 * (float)knockback / mass, kvel);",
		"return kvel[2] + aassettings.phys_jumpvel;",
	):
		assert expected in weapon_jump_body

	assert "return AAS_WeaponJumpZVelocity(origin, 120);" in rocket_jump_body
	assert "return AAS_WeaponJumpZVelocity(origin, 120);" in bfg_jump_body
	assert aliases["sub_486D40"] == "AAS_WeaponJumpZVelocity"
	assert aliases["sub_4A4280"] == "BotTravel_RocketJump"
	assert aliases["sub_4A4470"] == "BotTravel_BFGJump"

	assert "ms->moveflags &= ~MFL_TELEPORTED;" in bot_init_body
	assert "if (initmove->or_moveflags & MFL_TELEPORTED) ms->moveflags |= MFL_TELEPORTED;" in bot_init_body
	assert "if (ms->moveflags & MFL_TELEPORTED) return result;" in bot_teleport_body


def test_apply_jump_takeoff_restores_the_retail_shared_jump_leaf() -> None:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	body = _function_body("PM_ApplyJumpTakeoff")

	assert "static void PM_ApplyJumpTakeoff( void ) {" in source
	assert "pm->ps->pm_flags |= PMF_JUMP_HELD;" in body
	assert "pm->ps->groundEntityNum = ENTITYNUM_NONE;" in body
	assert "groundTraceLatest" not in body
	assert "pm->ps->jumpTime = pm->cmd.serverTime;" in body
	assert "pm->ps->velocity[2] = pm_jumpTakeoffVelocity;" in body
	assert "PM_AddEvent( EV_JUMP );" in body
	assert "PM_ForceLegsAnim( LEGS_JUMP );" in body
	assert "PM_ForceLegsAnim( LEGS_JUMPB );" in body


def test_prepare_jump_takeoff_holds_the_shared_retail_jump_setup() -> None:
	body = _function_body("PM_PrepareJumpTakeoff")
	ramp_body = _function_body("PM_ApplyRampJumpVerticalVelocity")

	assert "jumpVelocity = PM_EvaluateJumpTakeoffVelocity( settings, qfalse, &timeDelta );" in body
	assert "PM_ApplyRampJumpVerticalVelocity( jumpVelocity, qfalse, settings );" in body
	assert "velocity = jumpVelocity;" in ramp_body
	assert "settings && settings->rampJump && !fromCrouchStep" in ramp_body
	assert "settings && settings->jumpVelocityMax > 0.0f && velocity > settings->jumpVelocityMax" in ramp_body
	assert "PM_ApplyJumpPlanarVelocity" not in BG_PMOVE_PATH.read_text(encoding="utf-8")
	assert "pml.groundTrace.plane.normal[2] < 0.999f" not in body
	assert "groundTraceLatest" not in body
	assert "pm_jumpTakeoffVelocity = PM_ApplyRampJumpVerticalVelocity( jumpVelocity, qfalse, settings );" in body
	assert "pm_jumpTakeoffDoubleJumpActive = doubleJumpActive;" in body
	assert "!settings->doubleJump" not in body
	assert "pm_jumpTakeoffChainJumpActive" not in body
	assert "pm_jumpTakeoffRampJumpActive" not in body
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
	step_body = _function_body("PM_PrepareStepJumpTakeoff")
	crouch_body = _function_body("PM_PrepareCrouchStepJumpTakeoff")

	assert "PM_PrepareJumpTakeoff( qfalse )" in body
	assert "PM_PrepareStepJumpTakeoff( settings )" in body
	assert "PM_PrepareCrouchStepJumpTakeoff( settings )" in body
	assert "!fromCrouchSlide && pm->cmd.upmove < 10" in body
	assert "PM_ApplyJumpTakeoff();" in body
	assert "settings->stepJumpVelocity" not in body
	assert "PM_CheckJump( qfalse )" not in body
	assert "PM_EvaluateJumpTakeoffVelocity( settings, qtrue, NULL );" in step_body
	assert "pm_jumpTakeoffVelocity = PM_ApplyRampJumpVerticalVelocity( jumpVelocity, qfalse, settings );" in step_body
	assert "PM_EvaluateJumpTakeoffVelocity( settings, qfalse, NULL );" in crouch_body
	assert "pm_jumpTakeoffVelocity = PM_ApplyRampJumpVerticalVelocity( jumpVelocity, qtrue, settings );" in crouch_body
	assert "pm_jumpTakeoffDoubleJumpActive = qfalse;" in crouch_body


def test_pm_weapon_owns_the_retail_firing_flag_latch() -> None:
	pmove_body = _function_body("PmoveSingle")
	weapon_body = _function_body("PM_Weapon")

	assert "pm->ps->eFlags &= ~EF_FIRING;" in pmove_body
	assert "pm->ps->eFlags |= EF_FIRING;" not in pmove_body
	assert "pm->ps->ammo[ pm->ps->weapon ] || pm->ps->weapon == WP_GRAPPLING_HOOK" in weapon_body
	assert "!( pm->ps->pm_flags & PMF_ATTACK_LOCKOUT )" in weapon_body
	assert "if ( ! ( pm->cmd.buttons & BUTTON_ATTACK ) || ( pm->ps->pm_flags & PMF_ATTACK_LOCKOUT ) ) {" in weapon_body
	assert "if ( pm->ps->pm_flags & PMF_WEAPON_RESET )" in weapon_body
	assert (
		"pm->ps->weaponTime = 0;\n"
		"\t\tpm->ps->weaponstate = WEAPON_READY;\n"
		"\t\tpm->ps->eFlags &= ~EF_FIRING;\n"
		"\t\tpm->ps->pm_flags &= ~PMF_WEAPON_RESET;"
	) in weapon_body
	assert weapon_body.index("if ( pm->ps->stats[STAT_HEALTH] <= 0 )") < weapon_body.index("pm->ps->eFlags |= EF_FIRING;")
	assert weapon_body.index("pm->ps->eFlags |= EF_FIRING;") < weapon_body.index("holdable = pm->ps->stats[STAT_HOLDABLE_ITEM];")
	assert weapon_body.index("if ( ! ( pm->cmd.buttons & BUTTON_ATTACK )") < weapon_body.index("if ( pm->ps->pm_flags & PMF_WEAPON_RESET )")
	assert weapon_body.index("if ( pm->ps->pm_flags & PMF_WEAPON_RESET )") < weapon_body.index("// start the animation even if out of ammo")


def test_pm_weapon_keeps_the_retail_refire_speedups() -> None:
	body = _function_body("PM_Weapon")

	assert "addTime = PM_GetWeaponReloadTime( (weapon_t)pm->ps->weapon );" in body
	assert "BG_PlayerHasPersistantPowerup( pm->ps, PW_SCOUT )" in body
	assert "addTime /= 1.25f;" in body
	assert "BG_PlayerHasPersistantPowerup( pm->ps, PW_AMMOREGEN )" in body
	assert "pm->ps->powerups[PW_HASTE]" in body
	assert "addTime /= 1.5;" not in body
	assert body.index("BG_PlayerHasPersistantPowerup( pm->ps, PW_SCOUT )") < body.index("addTime /= 1.25f;")
	assert body.index("addTime /= 1.25f;") < body.index("BG_PlayerHasPersistantPowerup( pm->ps, PW_AMMOREGEN )")
	assert body.index("BG_PlayerHasPersistantPowerup( pm->ps, PW_AMMOREGEN )") < body.index("pm->ps->powerups[PW_HASTE]")


def test_pm_weapon_tracks_the_retail_chaingun_spinup_stat() -> None:
	public_source = (REPO_ROOT / "src/code/game/bg_public.h").read_text(encoding="utf-8")
	finish_body = _function_body("PM_FinishWeaponChange")
	weapon_body = _function_body("PM_Weapon")

	assert "STAT_CHAINGUN_SPINUP" in public_source
	assert "pm->ps->stats[STAT_CHAINGUN_SPINUP] = 0;" in finish_body
	assert "if ( pm->ps->weapon == WP_CHAINGUN )" in weapon_body
	assert "pm->ps->stats[STAT_CHAINGUN_SPINUP] < 1000" in weapon_body
	assert "addTime *= 2;" in weapon_body
	assert "pm->ps->stats[STAT_CHAINGUN_SPINUP] += addTime;" in weapon_body
	assert "pm->ps->stats[STAT_CHAINGUN_SPINUP] -= pml.msec;" in weapon_body
	assert weapon_body.index("addTime = PM_GetWeaponReloadTime( (weapon_t)pm->ps->weapon );") < weapon_body.index("if ( pm->ps->weapon == WP_CHAINGUN )")
	assert weapon_body.index("pm->ps->stats[STAT_CHAINGUN_SPINUP] += addTime;") < weapon_body.index("BG_PlayerHasPersistantPowerup( pm->ps, PW_SCOUT )")


def test_symbol_maps_record_the_recovered_pmove_weapon_edges() -> None:
	qagame_weapon = _symbol_comment("qagame", "PM_Weapon")
	cgame_weapon = _symbol_comment("cgame", "PM_Weapon")
	qagame_finish = _symbol_comment("qagame", "PM_FinishWeaponChange")
	cgame_finish = _symbol_comment("cgame", "PM_FinishWeaponChange")
	qagame_water = _symbol_comment("qagame", "PM_WaterEvents")
	cgame_water = _symbol_comment("cgame", "PM_WaterEvents")
	qagame_fire = _symbol_comment("qagame", "FireWeapon")

	for comment in (qagame_weapon, cgame_weapon, qagame_finish, cgame_finish):
		assert "+0xe0" in comment
		assert "STAT_CHAINGUN_SPINUP" in comment

	for comment in (qagame_weapon, cgame_weapon):
		assert "PMF_WEAPON_RESET" in comment
		assert "sentinel" in comment
		assert "WP_CHAINGUN" in comment

	for comment in (qagame_water, cgame_water):
		assert "PM_DEAD" in comment
		assert "invulnerability" in comment

	assert "chaingun spread" in qagame_fire
	assert "+0xe0" in qagame_fire
	assert "PM_Weapon" in qagame_fire


def test_pm_weapon_preserves_the_retail_no_weapon_sentinel_path() -> None:
	begin_body = _function_body("PM_BeginWeaponChange")
	finish_body = _function_body("PM_FinishWeaponChange")
	weapon_body = _function_body("PM_Weapon")

	assert "weapon > WP_NUM_WEAPONS" in begin_body
	assert "weapon == WP_NUM_WEAPONS" in begin_body
	assert "pm->ps->weaponstate = WEAPON_READY;" in begin_body
	assert "pm->ps->weapon = WP_NUM_WEAPONS;" in begin_body
	assert "PM_StartTorsoAnim( TORSO_STAND );" in begin_body
	assert begin_body.index("PM_AddEvent( EV_CHANGE_WEAPON );") < begin_body.index("if ( weapon == WP_NUM_WEAPONS )")
	assert begin_body.index("if ( weapon == WP_NUM_WEAPONS )") < begin_body.index("settings = PM_GetActiveSettings();")
	assert "weapon > WP_NUM_WEAPONS" in finish_body
	assert "pm->ps->weapon = weapon;" in finish_body
	assert "if ( pm->ps->weapon == WP_NUM_WEAPONS ) {" in weapon_body
	assert weapon_body.index("if ( pm->ps->weapon == WP_NUM_WEAPONS ) {") < weapon_body.index("if ( ! ( pm->cmd.buttons & BUTTON_ATTACK )")


def test_event_and_touch_helpers_keep_the_retail_queue_contracts() -> None:
	event_body = _function_body("PM_AddEvent")
	touch_body = _function_body("PM_AddTouchEnt")
	qagame_event = _symbol_comment("qagame", "PM_AddEvent")
	cgame_event = _symbol_comment("cgame", "PM_AddEvent")
	qagame_touch = _symbol_comment("qagame", "PM_AddTouchEnt")
	cgame_touch = _symbol_comment("cgame", "PM_AddTouchEnt")

	assert "BG_AddPredictableEventToPlayerstate( newEvent, 0, pm->ps );" in event_body
	assert "entityNum == ENTITYNUM_WORLD" in touch_body
	assert "pm->numtouch == MAXTOUCH" in touch_body
	assert "pm->touchents[ i ] == entityNum" in touch_body
	assert "pm->touchents[pm->numtouch] = entityNum;" in touch_body
	assert touch_body.index("entityNum == ENTITYNUM_WORLD") < touch_body.index("pm->numtouch == MAXTOUCH")
	assert touch_body.index("pm->numtouch == MAXTOUCH") < touch_body.index("pm->touchents[ i ] == entityNum")
	assert touch_body.index("pm->touchents[ i ] == entityNum") < touch_body.index("pm->touchents[pm->numtouch] = entityNum;")

	for comment in (qagame_event, cgame_event):
		assert "event parm of 0" in comment
		assert "fixture" in comment

	for comment in (qagame_touch, cgame_touch):
		assert "ENTITYNUM_WORLD" in comment
		assert "MAXTOUCH" in comment
		assert "duplicate" in comment
		assert "fixture" in comment


def test_animation_starter_helpers_keep_retail_timer_and_life_gates() -> None:
	start_torso = _function_body("PM_StartTorsoAnim")
	start_legs = _function_body("PM_StartLegsAnim")
	continue_legs = _function_body("PM_ContinueLegsAnim")
	continue_torso = _function_body("PM_ContinueTorsoAnim")
	force_legs = _function_body("PM_ForceLegsAnim")
	qagame_start_torso = _symbol_comment("qagame", "PM_StartTorsoAnim")
	cgame_start_torso = _symbol_comment("cgame", "PM_StartTorsoAnim")
	qagame_continue_legs = _symbol_comment("qagame", "PM_ContinueLegsAnim")
	cgame_continue_legs = _symbol_comment("cgame", "PM_ContinueLegsAnim")
	qagame_force_legs = _symbol_comment("qagame", "PM_ForceLegsAnim")
	cgame_force_legs = _symbol_comment("cgame", "PM_ForceLegsAnim")

	assert "pm->ps->pm_type >= PM_DEAD" in start_torso
	assert "( pm->ps->torsoAnim & ANIM_TOGGLEBIT ) ^ ANIM_TOGGLEBIT" in start_torso
	assert "pm->ps->pm_type >= PM_DEAD" in start_legs
	assert "pm->ps->legsTimer > 0" in start_legs
	assert "( pm->ps->legsAnim & ANIM_TOGGLEBIT ) ^ ANIM_TOGGLEBIT" in start_legs
	assert "( pm->ps->legsAnim & ~ANIM_TOGGLEBIT ) == anim" in continue_legs
	assert "pm->ps->legsTimer > 0" in continue_legs
	assert "PM_StartLegsAnim( anim );" in continue_legs
	assert "( pm->ps->torsoAnim & ~ANIM_TOGGLEBIT ) == anim" in continue_torso
	assert "pm->ps->torsoTimer > 0" in continue_torso
	assert "PM_StartTorsoAnim( anim );" in continue_torso
	assert "pm->ps->legsTimer = 0;" in force_legs
	assert "PM_StartLegsAnim( anim );" in force_legs
	assert force_legs.index("pm->ps->legsTimer = 0;") < force_legs.index("PM_StartLegsAnim( anim );")

	for comment in (qagame_start_torso, cgame_start_torso):
		assert "PM_DEAD" in comment
		assert "toggle" in comment
		assert "fixture" in comment

	for comment in (qagame_continue_legs, cgame_continue_legs):
		assert "legsTimer" in comment
		assert "current anim" in comment
		assert "fixture" in comment

	for comment in (qagame_force_legs, cgame_force_legs):
		assert "clears" in comment
		assert "legsTimer" in comment
		assert "fixture" in comment


def test_pm_animate_keeps_the_retail_taunt_and_voice_button_priority() -> None:
	body = _function_body("PM_Animate")
	markers = [
		"pm->cmd.buttons & BUTTON_GESTURE",
		"pm->cmd.buttons & BUTTON_GETFLAG",
		"pm->cmd.buttons & BUTTON_GUARDBASE",
		"pm->cmd.buttons & BUTTON_PATROL",
		"pm->cmd.buttons & BUTTON_FOLLOWME",
		"pm->cmd.buttons & BUTTON_AFFIRMATIVE",
		"pm->cmd.buttons & BUTTON_NEGATIVE",
	]
	position = -1

	assert "pm->ps->torsoTimer == 0" in body
	assert "PM_StartTorsoAnim( TORSO_GESTURE );" in body
	assert "pm->ps->torsoTimer = TIMER_GESTURE;" in body
	assert "PM_AddEvent( EV_TAUNT );" in body
	assert body.count("pm->ps->torsoTimer = 600;") == 6

	for marker in markers:
		next_position = body.index(marker, position + 1)
		assert next_position > position
		position = next_position


def test_torso_animation_keeps_the_retail_ready_weapon_idle_split() -> None:
	body = _function_body("PM_TorsoAnimation")
	qagame_comment = _symbol_comment("qagame", "PM_TorsoAnimation")
	cgame_comment = _symbol_comment("cgame", "PM_TorsoAnimation")

	assert "pm->ps->weaponstate == WEAPON_READY" in body
	assert "pm->ps->weapon == WP_GAUNTLET" in body
	assert "PM_ContinueTorsoAnim( TORSO_STAND2 );" in body
	assert "PM_ContinueTorsoAnim( TORSO_STAND );" in body
	assert "PM_StartTorsoAnim" not in body
	assert body.index("pm->ps->weaponstate == WEAPON_READY") < body.index("pm->ps->weapon == WP_GAUNTLET")
	assert body.index("PM_ContinueTorsoAnim( TORSO_STAND2 );") < body.index("PM_ContinueTorsoAnim( TORSO_STAND );")

	for comment in (qagame_comment, cgame_comment):
		assert "ready-state" in comment
		assert "TORSO_STAND2" in comment
		assert "torso timer" in comment


def test_crash_land_keeps_the_retail_gib_health_event_gate() -> None:
	body = _function_body("PM_CrashLand")

	assert "pm->ps->legsTimer = TIMER_LAND;" in body
	assert "pm->ps->stats[STAT_HEALTH] > -40" in body
	assert "PM_AddEvent( EV_FALL_FAR );" in body
	assert "PM_AddEvent( EV_FALL_MEDIUM );" in body
	assert "PM_AddEvent( EV_FALL_SHORT );" in body
	assert body.index("pm->ps->stats[STAT_HEALTH] > -40") < body.index("PM_AddEvent( EV_FALL_FAR );")
	assert body.index("pm->ps->stats[STAT_HEALTH] > 0") < body.index("PM_AddEvent( EV_FALL_MEDIUM );")
	assert body.index("PM_AddEvent( PM_FootstepForSurface() );") < body.index("pm->ps->bobCycle = 0;")
	assert body.index("pm->ps->bobCycle = 0;") < body.index("pm->ps->pm_flags & PMF_DOUBLE_JUMP")
	assert "pm->ps->doubleJumped = qfalse;" in body


def test_update_view_angles_keeps_the_retail_freeze_exception() -> None:
	body = _function_body("PM_UpdateViewAngles")

	assert "ps->pm_type == PM_INTERMISSION || ps->pm_type == PM_SPINTERMISSION" in body
	assert "ps->pm_type != PM_SPECTATOR && ps->pm_type != PM_FREEZE && ps->stats[STAT_HEALTH] <= 0" in body
	assert body.index("ps->pm_type == PM_INTERMISSION") < body.index("ps->pm_type != PM_SPECTATOR")
	assert body.index("ps->pm_type != PM_SPECTATOR") < body.index("for (i=0 ; i<3 ; i++)")


def test_water_events_keep_the_retail_dead_player_head_event_gate() -> None:
	body = _function_body("PM_WaterEvents")

	assert "PM_AddEvent( EV_WATER_TOUCH );" in body
	assert "PM_AddEvent( EV_WATER_LEAVE );" in body
	assert "if ( pm->ps->pm_type == PM_DEAD ) {" in body
	assert "PM_AddEvent( EV_WATER_UNDER );" in body
	assert "if ( !pm->ps->powerups[PW_INVULNERABILITY] && pml.previous_waterlevel == 3 && pm->waterlevel != 3 ) {" in body
	assert "PM_AddEvent( EV_WATER_CLEAR );" in body
	assert body.index("PM_AddEvent( EV_WATER_LEAVE );") < body.index("if ( pm->ps->pm_type == PM_DEAD )")
	assert body.index("if ( pm->ps->pm_type == PM_DEAD )") < body.index("PM_AddEvent( EV_WATER_UNDER );")
	assert body.index("pm->ps->powerups[PW_INVULNERABILITY]") < body.index("PM_AddEvent( EV_WATER_CLEAR );")


def test_drop_timers_keeps_the_retail_misc_and_animation_timer_order() -> None:
	body = _function_body("PM_DropTimers")
	qagame_comment = _symbol_comment("qagame", "PM_DropTimers")
	cgame_comment = _symbol_comment("cgame", "PM_DropTimers")

	assert "pm->ps->pm_flags &= ~PMF_ALL_TIMES;" in body
	assert "pm->ps->pm_time = 0;" in body
	assert "pm->ps->legsTimer -= pml.msec;" in body
	assert "pm->ps->torsoTimer -= pml.msec;" in body
	assert "pm->ps->crouchSlideTime -= pml.msec;" in body
	assert body.index("pm->ps->pm_time") < body.index("pm->ps->legsTimer > 0")
	assert body.index("pm->ps->legsTimer > 0") < body.index("pm->ps->torsoTimer > 0")
	assert body.index("pm->ps->torsoTimer > 0") < body.index("pm->ps->pm_flags & PMF_CROUCH_SLIDE")

	for comment in (qagame_comment, cgame_comment):
		assert "PMF_ALL_TIMES" in comment
		assert "PMF_TIME_KNOCKBACK" in comment
		assert "legsTimer" in comment
		assert "torsoTimer" in comment
		assert "fixture" in comment


def test_pmove_single_keeps_the_retail_dispatch_order() -> None:
	body = _function_body("PmoveSingle")
	post_move_markers = [
		"PM_Animate();",
		"PM_GroundTrace();",
		"PM_SetWaterLevel();",
		"PM_Weapon();",
		"PM_TorsoAnimation();",
		"PM_Footsteps();",
		"PM_WaterEvents();",
	]
	position = -1
	initial_water_level = body.index("PM_SetWaterLevel();")
	check_duck = body.index("PM_CheckDuck ();", initial_water_level)
	initial_ground_trace = body.index("PM_GroundTrace();", check_duck)

	assert body.index("c_pmove++;") < body.index("pm->numtouch = 0;")
	assert body.index("pm->numtouch = 0;") < body.index("pm->watertype = 0;")
	assert body.index("pm->watertype = 0;") < body.index("pm->waterlevel = 0;")
	assert "pm->ps->stats[STAT_HEALTH] <= 0 && !pm->ps->powerups[PW_INVULNERABILITY]" in body
	assert body.index("PM_LoadMoveTuningConstants();") < body.index("pm->ps->stats[STAT_HEALTH] <= 0 && !pm->ps->powerups[PW_INVULNERABILITY]")
	assert body.index("pm->ps->stats[STAT_HEALTH] <= 0 && !pm->ps->powerups[PW_INVULNERABILITY]") < body.index("if ( settings->noPlayerClip )")
	assert "pm->ps->pm_flags |= PMF_AIR_CONTROL;" not in body
	assert "pm->ps->pm_flags &= ~PMF_AIR_CONTROL;" not in body
	assert "pm->ps->pm_flags |= PMF_DOUBLE_JUMP;" not in body
	assert "pm->ps->pm_flags &= ~PMF_DOUBLE_JUMP;" not in body
	assert "pm->ps->pm_flags |= PMF_CROUCH_SLIDE;" not in body
	assert "pm->ps->pm_flags &= ~PMF_CROUCH_SLIDE;" not in body
	assert body.index("settings = PM_GetActiveSettings();") < body.index("PM_LoadMoveTuningConstants();")
	assert body.index("pm->waterlevel = 0;") < body.index("PM_LoadMoveTuningConstants();")
	assert initial_water_level < check_duck
	assert check_duck < initial_ground_trace
	assert body.index("pm->ps->commandTime = pmove->cmd.serverTime;") < body.index("if ( pm->ps->pm_flags & PMF_NO_MOVE ) {")
	assert body.index("if ( pm->ps->pm_flags & PMF_NO_MOVE ) {") < body.index("VectorCopy (pm->ps->origin, pml.previous_origin);")
	assert body.index("PM_UpdateViewAngles( pm->ps, &pm->cmd );") < body.index("pm->ps->weaponPrimary = pm->cmd.weaponPrimary;")
	assert body.index("pm->ps->weaponPrimary = pm->cmd.weaponPrimary;") < body.index("pm->ps->fov = pm->cmd.fov;")
	assert body.index("pm->ps->fov = pm->cmd.fov;") < body.index("pm->ps->forwardmove = pm->cmd.forwardmove;")
	assert body.index("pm->ps->forwardmove = pm->cmd.forwardmove;") < body.index("pm->ps->rightmove = pm->cmd.rightmove;")
	assert body.index("pm->ps->rightmove = pm->cmd.rightmove;") < body.index("pm->ps->upmove = pm->cmd.upmove;")
	assert body.index("pm->ps->upmove = pm->cmd.upmove;") < body.index("AngleVectors (pm->ps->viewangles, pml.forward, pml.right, pml.up);")
	assert body.index("PM_DropTimers();") < body.index("PM_CheckLadder();")
	assert body.index("PM_CheckLadder();") < body.index("pm->ps->powerups[PW_INVULNERABILITY] = 0;")
	assert body.index("if ( pm->ps->powerups[PW_FLIGHT] )") < body.index("} else if (pm->ps->pm_flags & PMF_GRAPPLE_PULL)")
	assert body.index("} else if (pm->ps->pm_flags & PMF_GRAPPLE_PULL)") < body.index("} else if (pm->ps->pm_flags & PMF_TIME_WATERJUMP)")
	assert body.index("} else if (pm->ps->pm_flags & PMF_TIME_WATERJUMP)") < body.index("} else if ( pm->waterlevel > 1 )")
	assert body.index("} else if ( pm->waterlevel > 1 )") < body.index("} else if ( pml.ladder )")
	assert body.index("} else if ( pml.ladder )") < body.index("} else if ( pml.walking )")
	assert "trap_SnapVector" not in body

	for marker in post_move_markers:
		next_position = body.index(marker, position + 1)
		assert next_position > position
		position = next_position
	assert body.rfind("PM_WaterEvents();") == position


def test_spawn_owns_retail_movement_profile_flags() -> None:
	g_pmove_body = _body_from_source(
		G_PMOVE_PATH,
		"void G_PmoveApplyProfileFlags( playerState_t *ps )",
	)
	g_client_body = _body_from_source(
		G_CLIENT_PATH,
		"void ClientSpawn(gentity_t *ent)",
	)
	g_local = G_LOCAL_PATH.read_text(encoding="utf-8")

	assert "void G_PmoveApplyProfileFlags( playerState_t *ps );" in g_local
	assert "ps->pm_flags &= ~( PMF_CROUCH_SLIDE | PMF_DOUBLE_JUMP | PMF_AIR_CONTROL );" in g_pmove_body
	assert g_pmove_body.index("if ( g_pmoveSettings.crouchSlide )") < g_pmove_body.index("if ( g_pmoveSettings.doubleJump )")
	assert g_pmove_body.index("if ( g_pmoveSettings.doubleJump )") < g_pmove_body.index("if ( g_pmoveSettings.airControl > 0.0f )")
	assert "ps->crouchSlideTime = 0;" in g_pmove_body
	pers_team_pos = g_client_body.index("client->ps.persistant[PERS_TEAM] = client->sess.sessionTeam;")
	profile_flags_pos = g_client_body.index("G_PmoveApplyProfileFlags( &client->ps );", pers_team_pos)
	spectator_pm_pos = g_client_body.index("if ( spawnAsSpectator )", profile_flags_pos)
	assert "spawnAsSpectator = ( client->ps.pm_type == PM_SPECTATOR ||" in g_client_body
	assert "client->sess.sessionTeam == TEAM_SPECTATOR ) ? qtrue : qfalse;" in g_client_body
	assert pers_team_pos < profile_flags_pos < spectator_pm_pos


def test_pmove_replays_long_frames_through_the_retail_chunk_loop() -> None:
	body = _function_body("Pmove")

	assert "pmove->stepUp = 0.0f;" in body
	assert "pmove->stepUpTime = 0;" in body
	assert "if ( finalTime > pmove->ps->commandTime + 1000 ) {" in body
	assert "pmove->ps->pmove_framecount = (pmove->ps->pmove_framecount+1) & ((1<<PS_PMOVEFRAMECOUNTBITS)-1);" in body
	assert "while ( pmove->ps->commandTime != finalTime ) {" in body
	assert "if ( pmove->pmove_fixed ) {" in body
	assert "if ( msec > pmove->pmove_msec ) {" in body
	assert "if ( msec > 66 ) {" in body
	assert body.index("pmove->cmd.serverTime = pmove->ps->commandTime + msec;") < body.index("PmoveSingle( pmove );")
	assert "if ( pml.stepUp > 0.0f ) {" in body
	assert "pmove->stepUp += pml.stepUp;" in body
	assert "pmove->stepUpTime = pmove->cmd.serverTime;" in body
	assert "if ( ( pmove->ps->pm_flags & PMF_JUMP_HELD ) && originalUpmove >= 10 ) {" in body
	assert "pmove->cmd.upmove = 20;" in body


def test_walk_move_uses_the_grounded_jump_gate_before_friction() -> None:
	body = _function_body("PM_WalkMove")
	jump_gate = body.index("if ( PM_CheckJump( qfalse ) ) {")
	post_jump_water = body.index("if ( pm->waterlevel > 1 ) {", jump_gate)
	post_jump_air = body.index("PM_AirMove();", post_jump_water)

	assert "if ( PM_CheckJump( qfalse ) ) {" in body
	assert jump_gate < body.index("PM_Friction ();")
	assert jump_gate < post_jump_water
	assert post_jump_water < post_jump_air


def test_clean_pmove_shim_preserves_the_retail_check_jump_parameter() -> None:
	header = CLEAN_PMOVE_HEADER_PATH.read_text(encoding="utf-8")
	source = CLEAN_PMOVE_SOURCE_PATH.read_text(encoding="utf-8")

	assert "typedef bool (*qlr_game_pmove_check_jump_hook_t)(struct qlr_game_pmove_context_s *ctx, bool allowAirDoubleJump);" in header
	assert "bool PM_CheckJump(bool allowAirDoubleJump);" in header
	assert "bool PM_CheckJump(bool allowAirDoubleJump) {" in source
	assert "\"missing-hook ctx=%p allowAirDoubleJump=%d\"" in source
	assert "return ctx->hooks.check_jump(ctx, allowAirDoubleJump);" in source
