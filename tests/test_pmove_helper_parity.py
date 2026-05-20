from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BG_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"
BG_PUBLIC_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_public.h"
CLEAN_PMOVE_HEADER_PATH = REPO_ROOT / "src-re" / "clean" / "include" / "qlr_game_pmove.h"
CLEAN_PMOVE_SOURCE_PATH = REPO_ROOT / "src-re" / "clean" / "gameplay" / "pmove.c"
SYMBOL_MAP_DIR = REPO_ROOT / "references" / "symbol-maps"


def _function_body(signature: str) -> str:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	match = re.search(
		rf"(?:static )?(?:qboolean|void) {re.escape(signature)}\s*\([^)]*\)\s*\{{(?P<body>.*?)^\}}",
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
	assert "pm_accelerate = PM_LoadMoveTuningFloat(" in body
	assert "pm_airaccelerate = PM_LoadMoveTuningFloat(" in body
	assert "pm_aircontrol = PM_LoadMoveTuningFloat(" in body
	assert "pm_retailAirControlTuning.airControl,\n\t\tairControlTuning," in body
	assert "pm_airsteps = airControlTuning" in body
	assert "pm_circlestrafe_friction = PM_LoadMoveTuningFloat(" in body
	assert "pm_wishspeed = PM_LoadMoveTuningFloat(" in body
	assert "PM_LoadMoveSettings();" in body


def test_jump_release_override_uses_the_recovered_cg_autohop_flag() -> None:
	body = _function_body("PM_ShouldRequireJumpRelease")
	prepare_body = _function_body("PM_PrepareJumpTakeoff")

	assert "pm->ps->pm_flags & PMF_REQUIRE_JUMP_RELEASE" in body
	assert body.index("PMF_REQUIRE_JUMP_RELEASE") < body.index("activeSettings = settings ? settings : PM_GetActiveSettings();")
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

	assert source.count("PM_BuildWishMove3D( wishdir, &wishspeed )") >= 4
	assert "VectorSet( wishdir, 0.0f, 0.0f, -1.0f );" in source


def test_pm_accelerate_stays_on_the_generic_retail_body() -> None:
	body = _function_body("PM_Accelerate")

	assert "currentSpeed = DotProduct( pm->ps->velocity, wishdir );" in body
	assert "addSpeed = wishspeed - currentSpeed;" in body
	assert "accelSpeed = accel * pml.frametime * wishspeed;" in body
	assert "pm_wishspeed" not in body
	assert "pm_airstopaccelerate" not in body
	assert "pm_strafeaccelerate" not in body
	assert "airborneMove" not in body


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
		assert "groundTraceLatest" in correct_all_solid
		assert "pml.groundPlane" in correct_all_solid
		assert "pml.walking" in correct_all_solid

		assert "64" in ground_trace_missed
		assert "LEGS_JUMP" in ground_trace_missed
		assert "LEGS_JUMPB" in ground_trace_missed
		assert "PMF_BACKWARDS_JUMP" in ground_trace_missed
		assert "groundTraceLatest" in ground_trace_missed

		assert "0.25" in ground_trace
		assert "kickoff dot > 10" in ground_trace
		assert "groundTraceLatest" in ground_trace
		assert "PMF_TIME_WATERJUMP" in ground_trace
		assert "PMF_TIME_LAND" in ground_trace
		assert "250 ms" in ground_trace
		assert "PM_RecordGroundContact" in ground_trace
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
		assert "crouch-slide" in comment
		assert "circle-strafe" in comment
		assert "PM_FREEZE" in comment
		assert "PMF_SCOREBOARD" in comment
		assert "0.25" in comment


def test_apply_jump_takeoff_restores_the_retail_shared_jump_leaf() -> None:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	body = _function_body("PM_ApplyJumpTakeoff")

	assert "static void PM_ApplyJumpTakeoff( void ) {" in source
	assert "pm->ps->pm_flags |= PMF_JUMP_HELD;" in body
	assert "pm->ps->groundEntityNum = ENTITYNUM_NONE;" in body
	assert "pm->ps->groundTraceLatestEntNum = ENTITYNUM_NONE;" in body
	assert "pm->ps->jumpTime = pm->cmd.serverTime;" in body
	assert "pm->ps->velocity[2] = pm_jumpTakeoffVelocity;" in body
	assert "PM_AddEvent( EV_JUMP );" in body
	assert "PM_ForceLegsAnim( LEGS_JUMP );" in body
	assert "PM_ForceLegsAnim( LEGS_JUMPB );" in body


def test_prepare_jump_takeoff_holds_the_shared_retail_jump_setup() -> None:
	body = _function_body("PM_PrepareJumpTakeoff")

	assert "jumpVelocityScale = PM_EvaluateJumpVelocityScale( pm->ps, settings, pm->cmd.serverTime, &timeDelta );" in body
	assert "PM_ApplyJumpPlanarVelocity( chainJumpActive, rampJumpActive, settings );" in body
	assert "pm_jumpTakeoffVelocity = jumpVelocity;" in body
	assert "pm_jumpTakeoffDoubleJumpActive = doubleJumpActive;" in body
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

	assert "PM_PrepareJumpTakeoff( qfalse )" in body
	assert "PM_ApplyJumpTakeoff();" in body
	assert "PM_CheckJump( qfalse )" not in body


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
		"trap_SnapVector( pm->ps->velocity );",
	]
	position = -1
	initial_water_level = body.index("PM_SetWaterLevel();")
	check_duck = body.index("PM_CheckDuck ();", initial_water_level)
	initial_ground_trace = body.index("PM_GroundTrace();", check_duck)

	assert body.index("c_pmove++;") < body.index("pm->numtouch = 0;")
	assert body.index("pm->numtouch = 0;") < body.index("pm->watertype = 0;")
	assert body.index("pm->watertype = 0;") < body.index("pm->waterlevel = 0;")
	assert body.index("settings = PM_GetActiveSettings();") < body.index("if ( settings->airControl > 0.0f )")
	assert body.index("if ( settings->airControl > 0.0f )") < body.index("pm->ps->pm_flags |= PMF_AIR_CONTROL;")
	assert body.index("pm->ps->pm_flags &= ~PMF_AIR_CONTROL;") < body.index("PM_LoadMoveTuningConstants();")
	assert body.index("if ( settings->doubleJump )") < body.index("pm->ps->pm_flags |= PMF_DOUBLE_JUMP;")
	assert body.index("pm->ps->pm_flags &= ~PMF_DOUBLE_JUMP;") < body.index("PM_LoadMoveTuningConstants();")
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

	for marker in post_move_markers:
		next_position = body.index(marker, position + 1)
		assert next_position > position
		position = next_position


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
