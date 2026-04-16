"""Guard retail-backed cgame display-context bridge behavior against source drift."""

from __future__ import annotations

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_EFFECTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_effects.c"
CG_EVENT = REPO_ROOT / "src" / "code" / "cgame" / "cg_event.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_PLAYERS = REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c"
CG_SCOREBOARD = REPO_ROOT / "src" / "code" / "cgame" / "cg_scoreboard.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CG_DRAWTOOLS = REPO_ROOT / "src" / "code" / "cgame" / "cg_drawtools.c"
CG_ENTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_ents.c"
CG_DRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_PREDICT = REPO_ROOT / "src" / "code" / "cgame" / "cg_predict.c"
CG_VIEW = REPO_ROOT / "src" / "code" / "cgame" / "cg_view.c"
CG_WEAPONS = REPO_ROOT / "src" / "code" / "cgame" / "cg_weapons.c"
CG_MARKS = REPO_ROOT / "src" / "code" / "cgame" / "cg_marks.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CG_LOCALENTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_localents.c"
CG_PUBLIC = REPO_ROOT / "src" / "code" / "cgame" / "cg_public.h"
CG_SCREEN = REPO_ROOT / "src" / "code" / "cgame" / "cg_screen.c"
CG_SYSCALLS = REPO_ROOT / "src" / "code" / "cgame" / "cg_syscalls.c"
CG_BG_PLAN = REPO_ROOT / "docs" / "reverse-engineering" / "cgame-bg-parity-implementation-plan.md"
CL_CGAME = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
G_CLIENT = REPO_ROOT / "src" / "code" / "game" / "g_client.c"
G_ITEMS = REPO_ROOT / "src" / "code" / "game" / "g_items.c"
G_MAIN = REPO_ROOT / "src" / "code" / "game" / "g_main.c"
QL_CGAME_IMPORTS = REPO_ROOT / "src" / "code" / "client" / "ql_cgame_imports.inc"
UI_MAIN = REPO_ROOT / "src" / "code" / "ui" / "ui_main.c"
UI_ATOMS = REPO_ROOT / "src" / "code" / "ui" / "ui_atoms.c"
UI_SHARED = REPO_ROOT / "src" / "code" / "ui" / "ui_shared.c"
UI_SHARED_H = REPO_ROOT / "src" / "code" / "ui" / "ui_shared.h"


def _block_from_marker(source: str, marker: str) -> str:
	start = source.rindex(marker)
	brace_start = source.index("{", start)
	depth = 0

	for index in range(brace_start, len(source)):
		char = source[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start:index + 1]

	raise AssertionError(f"Unbalanced block for marker: {marker}")


def test_cgame_display_context_wires_binding_and_execute_hooks() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")

	for expected in (
		"cgDC.setOverstrikeMode = &trap_Key_SetOverstrikeMode;",
		"cgDC.getOverstrikeMode = &trap_Key_GetOverstrikeMode;",
		"cgDC.setBinding = &trap_Key_SetBinding;",
		"cgDC.getBindingBuf = &trap_Key_GetBindingBuf;",
		"cgDC.keynumToStringBuf = &trap_Key_KeynumToStringBuf;",
		"cgDC.executeText = &trap_Cmd_ExecuteText;",
	):
		assert expected in source

	for stale in (
		"//cgDC.setOverstrikeMode = &trap_Key_SetOverstrikeMode;",
		"//cgDC.getOverstrikeMode = &trap_Key_GetOverstrikeMode;",
		"//cgDC.setBinding = &trap_Key_SetBinding;",
		"//cgDC.getBindingBuf = &trap_Key_GetBindingBuf;",
		"//cgDC.keynumToStringBuf = &trap_Key_KeynumToStringBuf;",
		"//cgDC.executeText = &trap_Cmd_ExecuteText;",
	):
		assert stale not in source


def test_cgame_ui_alloc_pool_matches_retail_mapping_note() -> None:
	source = UI_SHARED.read_text(encoding="utf-8")

	assert "#define MEM_POOL_SIZE  0x600000" in source
	assert "#define MEM_POOL_SIZE  128 * 1024" not in source


def test_cgame_register_graphics_uses_retail_cursor_assets_and_skips_nonretail_flag_icons() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	register_block = _block_from_marker(source, "static void CG_RegisterGraphics( void )")
	ghidra_source = (
		REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "cgamex86" / "decompile_top_functions.c"
	).read_text(encoding="utf-8")

	assert 'cgs.media.cursor = trap_R_RegisterShaderNoMip( "menu/art/3_cursor2" );' in register_block
	assert 'cgs.media.sizeCursor = trap_R_RegisterShaderNoMip( "ui/assets/sizecursor.tga" );' in register_block
	assert 'cgs.media.selectCursor = trap_R_RegisterShaderNoMip( "ui/assets/3_cursor3.tga" );' in register_block
	assert "selectcursor.tga" not in register_block
	assert "flag_in_base.tga" not in register_block
	assert "flag_capture.tga" not in register_block
	assert "flag_missing.tga" not in register_block

	assert '"ui/assets/sizecursor.tga"' in ghidra_source
	assert '"ui/assets/3_cursor3.tga"' in ghidra_source
	assert "selectcursor.tga" not in ghidra_source
	assert "flag_in_base.tga" not in ghidra_source


def test_cgame_weapon_reload_configstring_bridge_restored() -> None:
	servercmds = CG_SERVERCMDS.read_text(encoding="utf-8")
	weapons = CG_WEAPONS.read_text(encoding="utf-8")

	for expected in (
		"static const weapon_t cg_retailWeaponReloadOrder[] = {",
		"WP_GAUNTLET,",
		"WP_BFG,",
		"WP_HEAVY_MACHINEGUN",
		"static void CG_ParseWeaponReloadConfigString( void ) {",
		"payload = CG_ConfigString( CS_WEAPON_RELOAD_TIMES );",
		"token = COM_ParseExt( &cursor, qfalse );",
		"cg_pmoveSettings.weaponReloadTimes[cg_retailWeaponReloadOrder[i]] = parsed[i];",
		"CG_ParseWeaponReloadConfigString();",
		"} else if ( num == CS_WEAPON_RELOAD_TIMES ) {",
	):
		assert expected in servercmds

	assert "static int CG_GetWeaponReloadTime( weapon_t weapon ) {" in weapons
	assert "railReloadTime = CG_GetWeaponReloadTime( WP_RAILGUN );" in weapons
	assert "f = (float)cg.predictedPlayerState.weaponTime / (float)railReloadTime;" in weapons
	assert "f = (float)cg.predictedPlayerState.weaponTime / 1500;" not in weapons


def test_cgame_weapon_helper_split_restores_retail_view_weapon_and_selection_seam() -> None:
	weapons_source = CG_WEAPONS.read_text(encoding="utf-8")
	rail_block = _block_from_marker(weapons_source, "static void CG_SpawnRailTrail")
	powerup_block = _block_from_marker(weapons_source, "static void CG_AddWeaponWithPowerups")
	cycle_block = _block_from_marker(weapons_source, "static void CG_CycleWeaponSelection")
	highest_block = _block_from_marker(weapons_source, "static void CG_SelectHighestWeapon")
	next_block = _block_from_marker(weapons_source, "void CG_NextWeapon_f( void )")
	prev_block = _block_from_marker(weapons_source, "void CG_PrevWeapon_f( void )")
	out_of_ammo_block = _block_from_marker(weapons_source, "void CG_OutOfAmmoChange( void )")

	assert "static void CG_SpawnRailTrail( centity_t *cent, vec3_t origin ) {" in weapons_source
	for expected in (
		"if ( cent->currentState.weapon != WP_RAILGUN ) {",
		"if ( !cent->pe.railgunFlash ) {",
		"cent->pe.railgunFlash = qfalse;",
		"VectorCopy( origin, start );",
		"VectorCopy( cent->pe.railgunImpact, end );",
		"CG_RailTrail( ci, start, end );",
	):
		assert expected in rail_block
	assert "forcePredicted" not in rail_block
	assert "CG_GetStoredPredictedBeam" not in rail_block

	assert "static void CG_AddWeaponWithPowerups( const centity_t *cent, refEntity_t *gun ) {" in weapons_source
	for expected in (
		"int\t\tpowerups;",
		"powerups = cent->currentState.powerups;",
		"CG_AddWeaponWithPowerups( cent, &gun );",
		"CG_AddWeaponWithPowerups( cent, &barrel );",
		"CG_AddWeaponWithPowerups( cent, &ammo );",
		"CG_SpawnRailTrail( cent, flash.origin );",
	):
		assert expected in weapons_source or expected in powerup_block

	for expected in (
		"if ( !cg.snap ) {",
		"if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {",
		"cg.weaponSelectTime = cg.time;",
		"selected = cg.weaponSelect;",
		"if ( next ) {",
		"selected++;",
		"selected--;",
		"if ( selected == MAX_WEAPONS ) {",
		"selected = WP_NUM_WEAPONS;",
		"if ( selected == WP_GAUNTLET || selected == WP_NUM_WEAPONS ) {",
		"CG_SetWeaponSelect( selected );",
	):
		assert expected in cycle_block

	for expected in (
		"cg.weaponSelectTime = cg.time;",
		"for ( i = MAX_WEAPONS - 1 ; i > 0 ; i-- ) {",
		"if ( i == WP_NUM_WEAPONS ) {",
		"CG_SetWeaponSelect( i );",
	):
		assert expected in highest_block

	assert "CG_CycleWeaponSelection( qtrue );" in next_block
	assert "CG_CycleWeaponSelection( qfalse );" in prev_block
	assert "CG_SelectHighestWeapon();" in out_of_ammo_block


def test_cgame_mark_axis_helper_restores_retail_impact_mark_math_split() -> None:
	marks_source = CG_MARKS.read_text(encoding="utf-8")
	axis_block = _block_from_marker(marks_source, "static void CG_BuildMarkAxis")
	impact_block = _block_from_marker(marks_source, "void CG_ImpactMark")

	for expected in (
		"static void CG_BuildMarkAxis( const vec3_t dir, float orientation, vec3_t axis[3] ) {",
		"VectorNormalize2( dir, axis[0] );",
		"PerpendicularVector( axis[1], axis[0] );",
		"RotatePointAroundVector( axis[2], axis[0], axis[1], orientation );",
		"CrossProduct( axis[0], axis[2], axis[1] );",
	):
		assert expected in axis_block

	assert "CG_BuildMarkAxis( dir, orientation, axis );" in impact_block

	for unexpected in (
		"VectorNormalize2( dir, axis[0] );",
		"PerpendicularVector( axis[1], axis[0] );",
		"RotatePointAroundVector( axis[2], axis[0], axis[1], orientation );",
		"CrossProduct( axis[0], axis[2], axis[1] );",
	):
		assert unexpected not in impact_block


def test_cgame_match_state_auxiliary_configstrings_drive_live_timeout_and_team_count_state() -> None:
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	event_source = CG_EVENT.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	reset_block = _block_from_marker(servercmds_source, "static void CG_ResetMatchStateFields( void )")
	parse_timeout_block = _block_from_marker(servercmds_source, "static void CG_ParseTimeoutConfigStrings( void )")
	parse_team_block = _block_from_marker(servercmds_source, "static void CG_ParseTeamCountConfigStrings( void )")
	parse_match_block = _block_from_marker(servercmds_source, "static void CG_ParseMatchState( void )")
	parse_round_start_block = _block_from_marker(servercmds_source, "static void CG_ParseRoundStartTimeConfigString( void )")
	set_config_values_block = _block_from_marker(servercmds_source, "void CG_SetConfigValues( void )")
	get_timeout_start_block = _block_from_marker(servercmds_source, "int CG_GetMatchTimeoutStartTime( void )")
	get_round_start_block = _block_from_marker(servercmds_source, "int CG_GetMatchRoundStartTime( void )")
	match_clock_block = _block_from_marker(event_source, "static int CG_MatchClockMilliseconds( void )")
	match_label_block = _block_from_marker(newdraw_source, "static void CG_BuildMatchStateLabel")

	assert "static int cg_matchTimeoutStartTime;" in servercmds_source
	assert "static int cg_matchRoundStartTime;" in servercmds_source
	assert "cg_matchTimeoutStartTime = 0;" in reset_block
	assert "cg_matchRoundStartTime = 0;" in reset_block
	assert "int CG_GetMatchTimeoutStartTime( void );" in local_source
	assert "int CG_GetMatchRoundStartTime( void );" in local_source
	assert "return cg_matchTimeoutStartTime;" in get_timeout_start_block
	assert "return cg_matchRoundStartTime;" in get_round_start_block

	for expected in (
		"info = CG_ConfigString( CS_ROUND_START_TIME );",
		"cg_matchRoundStartTime = 0;",
		"cg_matchRoundStartTime = atoi( info );",
	):
		assert expected in parse_round_start_block

	for expected in (
		"info = CG_ConfigString( CS_TIMEOUT_START_TIME );",
		"cg_matchTimeoutStartTime = value;",
		"info = CG_ConfigString( CS_TIMEOUT_EXPIRE_TIME );",
		"cgs.matchTimeoutExpireTime = value;",
		"info = CG_ConfigString( CS_TIMEOUT_COUNT_RED );",
		"info = CG_ConfigString( CS_TIMEOUT_COUNT_BLUE );",
		"value = cgs.matchTimeoutCountPerTeam;",
		"cgs.matchTimeoutRemaining[TEAM_RED] = value;",
		"cgs.matchTimeoutRemaining[TEAM_BLUE] = value;",
	):
		assert expected in parse_timeout_block

	for expected in (
		"info = CG_ConfigString( CS_TEAM_COUNT_RED );",
		"cgs.matchTeamCount[TEAM_RED] = value;",
		"info = CG_ConfigString( CS_TEAM_COUNT_BLUE );",
		"cgs.matchTeamCount[TEAM_BLUE] = value;",
	):
		assert expected in parse_team_block

	assert "CG_ParseMatchFactoryConfig( info );" in parse_match_block
	assert "if( cgs.gametype == GT_CTF || cgs.gametype == GT_ATTACK_DEFEND || cgs.gametype == GT_OBELISK ) {" in set_config_values_block
	assert "CG_ParseRoundStartTimeConfigString();" in set_config_values_block
	assert "CG_ParseTimeoutConfigStrings();" in parse_match_block
	assert "CG_ParseTeamCountConfigStrings();" in parse_match_block
	assert "CG_ParseTimeoutConfigStrings();" in set_config_values_block
	assert "CG_ParseTeamCountConfigStrings();" in set_config_values_block
	assert "if( cgs.gametype == GT_CTF || cgs.gametype == GT_ATTACK_DEFEND || cgs.gametype == GT_OBELISK ) {" in servercmds_source
	assert "num == CS_ROUND_START_TIME" in servercmds_source
	assert "num == CS_TEAM_COUNT_RED || num == CS_TEAM_COUNT_BLUE" in servercmds_source
	assert "num == CS_TIMEOUT_START_TIME || num == CS_TIMEOUT_EXPIRE_TIME ||" in servercmds_source
	assert "num == CS_TIMEOUT_COUNT_RED || num == CS_TIMEOUT_COUNT_BLUE" in servercmds_source

	assert "timeoutStart = CG_GetMatchTimeoutStartTime();" in match_clock_block
	assert "} else if ( timeoutStart > 0 ) {" in match_clock_block
	assert "timeoutStartTime = CG_GetMatchTimeoutStartTime();" in match_label_block
	assert 'Com_sprintf( buffer, bufferSize, "Timeout %s", CG_GetTeamLabel( cgs.matchTimeoutTeam ) );' in match_label_block


def test_cgame_overtime_ownerdraw_reconstruction_matches_retail_label_family() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	event_source = CG_EVENT.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	scoreboard_source = CG_SCOREBOARD.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
	draw_block = _block_from_marker(newdraw_source, "static void CG_DrawOvertime")
	scoreboard_block = _block_from_marker(scoreboard_source, "static void CG_UpdateHudScoreboardBanners( void )")

	assert "int CG_GetOvertimeCount( void );" in local_source
	assert "int CG_GetOvertimeCount( void ) {" in event_source

	for expected in (
		"overtimeCount = CG_GetOvertimeCount();",
		'Com_sprintf( buffer, sizeof( buffer ), "Overtime x%i", overtimeCount );',
		'Q_strncpyz( buffer, "Overtime", sizeof( buffer ) );',
	):
		assert expected in draw_block
		assert expected in width_block

	assert 'CG_Text_Paint(rect->x, rect->y, scale, color, buffer, 0, 0, textStyle);' in draw_block
	assert "return CG_Text_Width( buffer, scale, 0 );" in width_block
	assert "if ( cgHudScoreboard.overtimeCount > 1 ) {" in scoreboard_block


def test_scoreboard_and_race_server_command_wrappers_match_retail_dispatch() -> None:
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	ffa_block = _block_from_marker(servercmds_source, "static void CG_ParseFFAScores( void )")
	rich_payload_block = _block_from_marker(servercmds_source, "static void CG_ParseRichScoreboardPayload( void )")
	compact_block = _block_from_marker(servercmds_source, "static void CG_ParseCompactScores( void )")
	race_info_block = _block_from_marker(servercmds_source, "static void CG_ParseRaceInfo( void )")

	assert 'if ( !strcmp( cmd, "scores_ffa" ) ) {' in servercmds_source
	assert "\t\tCG_ParseFFAScores();" in servercmds_source
	assert 'if ( !strcmp( cmd, "scores" ) ) {' in servercmds_source
	assert "\t\tCG_ParseScores();" in servercmds_source
	assert 'if ( !strcmp( cmd, "smscores" ) ) {' in servercmds_source
	assert "\t\tCG_ParseCompactScores();" in servercmds_source
	assert 'if ( !strcmp( cmd, "tinfo" ) ) {' in servercmds_source
	assert "\t\tCG_ParseTeamInfo();" in servercmds_source
	assert 'if ( !strcmp( cmd, "race_info" ) ) {' in servercmds_source
	assert "\t\tCG_ParseRaceInfo();" in servercmds_source
	assert "CG_ParseRaceInfoCommand" not in servercmds_source

	assert "CG_ParseRichScoreboardPayload();" in ffa_block
	for expected in (
		"cg.numScores = atoi( CG_Argv( 1 ) );",
		"cg.teamScores[0] = atoi( CG_Argv( 2 ) );",
		"cg.teamScores[1] = atoi( CG_Argv( 3 ) );",
		"CG_ParseGenericScoreRows( 4, 16 );",
	):
		assert expected in rich_payload_block

	assert "cg.scores[i].scoreFlags = 0;" in compact_block
	assert "cg.scores[i].activePlayer = atoi( CG_Argv( i * 8 + 9 ) ) ? qtrue : qfalse;" in compact_block
	assert "CG_FinalizeParsedScoreRow( &cg.scores[i], powerups );" in compact_block
	assert "cg.scores[i].scoreFlags = atoi( CG_Argv( i * 8 + 9 ) );" not in compact_block

	for expected in (
		"cgs.raceInfoActive = atoi( CG_Argv( 1 ) ) ? qtrue : qfalse;",
		"cgs.raceInfoStartTime = atoi( CG_Argv( 2 ) );",
		"cgs.raceInfoLastTime = atoi( CG_Argv( 3 ) );",
		"cgs.raceInfoCheckpointCount = atoi( CG_Argv( 4 ) );",
		"cgs.raceInfoCurrentCheckpointEntityNum = atoi( CG_Argv( 5 ) );",
		"cgs.raceInfoNextCheckpointEntityNum = atoi( CG_Argv( 6 ) );",
	):
		assert expected in race_info_block

	assert "cgs.raceLeaderSplitCount = 0;" not in race_info_block


def test_cgame_attack_defend_round_scoreboard_owner_matches_retail_warmup_panel() -> None:
	draw_source = CG_DRAW.read_text(encoding="utf-8")
	status_block = _block_from_marker(draw_source, "static const char *CG_ADRoundScoreboardStatusText( void )")
	scoreboard_block = _block_from_marker(draw_source, "static void CG_DrawADRoundScoreboard( void )")
	warmup_block = _block_from_marker(draw_source, "static void CG_DrawWarmupStatusText( int gametype )")

	for expected in (
		'value = Info_ValueForKey( info, "g_scorelimit" );',
		'value = Info_ValueForKey( info, "roundlimit" );',
		"if ( cgs.matchRoundTurn != 0 ) {",
		'return "Red Wins! Good Game";',
		'return "Last Chance";',
		'return "Match Point";',
	):
		assert expected in status_block

	for expected in (
		"if ( cgs.matchRoundNumber <= 0 ) {",
		"CG_FillRect( 200.0f, 150.0f, 240.0f, 48.0f, panelColor );",
		"roundWindowStart = ( cgs.matchRoundNumber > ( CG_AD_SCORE_HISTORY_LENGTH / 2 ) ) ?",
		"activeColumn = cgs.matchRoundNumber - roundWindowStart;",
		"activeRowY = 182.0f;",
		"activeRowY = 166.0f;",
		"CG_FillRect( 200.0f, activeRowY, 40.0f, 16.0f, *activeTeamFillColor );",
		"CG_FillRect( 240.0f + activeColumn * 16.0f, activeRowY, 16.0f, 16.0f, *activeRoundFillColor );",
		'CG_Text_PaintNoAdjust( 204.0f, 162.0f, 0.20f, colorWhite, "Round", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );',
		'CG_Text_PaintNoAdjust( 204.0f, 178.0f, 0.25f, colorRed, "Red", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );',
		'CG_Text_PaintNoAdjust( 204.0f, 194.0f, 0.25f, colorBlue, "Blue", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );',
		"historyIndex = column * 2;",
		"if ( cg.adScoreHistory[historyIndex] >= 0 ) {",
		"if ( cg.adScoreHistory[historyIndex + 1] >= 0 ) {",
		'CG_Text_PaintNoAdjust( 404.0f, 162.0f, 0.25f, colorWhite, "Score", 0, ITEM_TEXTSTYLE_SHADOWEDMORE );',
		"statusText = CG_ADRoundScoreboardStatusText();",
		'if ( !Q_stricmp( statusText, "Red Wins! Good Game" ) ) {',
	):
		assert expected in scoreboard_block

	assert "} else if ( gametype == GT_ATTACK_DEFEND && cgs.matchRoundState == ROUNDSTATE_WARMUP ) {" in warmup_block
	assert "CG_DrawADRoundScoreboard();" in warmup_block


def test_bg_plan_marks_cg_b3_closed_after_ad_round_scoreboard_validation() -> None:
	plan = CG_BG_PLAN.read_text(encoding="utf-8")
	assert "| `CG-B3a` | `CG-B` | Boundary-only |" in plan

	cg_b3_rows = [line for line in plan.splitlines() if line.startswith("| `CG-B3` |")]
	assert cg_b3_rows
	cg_b3_row = cg_b3_rows[-1]
	assert "Completed 2026-04-05" in cg_b3_row
	assert "`cg_draw.c`" in cg_b3_row
	assert "`CG_DrawADRoundScoreboard`" in cg_b3_row
	assert "Completed." in cg_b3_row

	cg_b_lane_rows = [line for line in plan.splitlines() if line.startswith("| `CG-B` |")]
	assert cg_b_lane_rows
	assert cg_b_lane_rows[-1].strip().endswith("None |")


def test_bg_plan_marks_cg_b1_closed_after_teamsize_transport_validation() -> None:
	plan = CG_BG_PLAN.read_text(encoding="utf-8")
	assert "| `CG-B1a` | `CG-B` | Transport |" in plan

	cg_b1_rows = [line for line in plan.splitlines() if line.startswith("| `CG-B1` |")]
	assert cg_b1_rows
	cg_b1_row = cg_b1_rows[-1]
	assert "Completed 2026-04-05" in cg_b1_row
	assert "`teamsize` alias" in cg_b1_row
	assert "Completed." in cg_b1_row
	assert "g_playerCylinders" not in cg_b1_row

	assert any("| `CG-B` | `CLOSED` |" in line for line in plan.splitlines())


def test_cgame_acc_vertical_overlay_reconstruction_uses_retail_acc_parser_and_sender() -> None:
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	console_source = (REPO_ROOT / "src" / "code" / "cgame" / "cg_consolecmds.c").read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	game_source = (REPO_ROOT / "src" / "code" / "game" / "g_cmds.c").read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")

	shared_parse_block = _block_from_marker(servercmds_source, "static void CG_ParseRetailAccuracyCommand( void )")
	parse_block = _block_from_marker(servercmds_source, "static void CG_ParseAcc( void )")
	pstats_parse_block = _block_from_marker(servercmds_source, "static void CG_ParsePStats( void )")
	acc_down_block = _block_from_marker(console_source, "static void CG_AccDown_f( void )")
	acc_up_block = _block_from_marker(console_source, "static void CG_AccUp_f( void )")
	pstats_down_block = _block_from_marker(console_source, "static void CG_PStatsDown_f( void )")
	pstats_up_block = _block_from_marker(console_source, "static void CG_PStatsUp_f( void )")
	draw_gate_block = _block_from_marker(newdraw_source, "static qboolean CG_ShouldDrawAccVertical( void )")
	draw_weapon_block = _block_from_marker(newdraw_source, "static void CG_DrawWeaponVertical( rectDef_t *rect, vec4_t color )")
	draw_acc_block = _block_from_marker(newdraw_source, "static void CG_DrawAccVertical( rectDef_t *rect, float scale, vec4_t color, int textStyle )")
	source_client_block = _block_from_marker(game_source, "static gclient_t *G_RetailAccuracySourceClient( gentity_t *ent )")
	shared_sender_block = _block_from_marker(game_source, "static void G_SendRetailAccuracyPayloadCommand( gentity_t *ent, const char *command )")
	sender_block = _block_from_marker(game_source, "static void G_SendRetailAccuracyCommand( gentity_t *ent )")
	pstats_sender_block = _block_from_marker(game_source, "static void G_SendRetailPStatsCommand( gentity_t *ent )")
	cmd_acc_block = _block_from_marker(game_source, "void Cmd_Acc_f( gentity_t *ent )")
	cmd_pstats_block = _block_from_marker(game_source, "void Cmd_PStats_f( gentity_t *ent )")

	for expected in (
		"int\t\t\tweaponAccuracies[WP_NUM_WEAPONS];",
		"qboolean\taccRequestActive;",
		"int\t\t\taccRequestTime;",
	):
		assert expected in local_source

	for expected in (
		"static const weapon_t cg_retailAccuracyCommandOrder[] = {",
		"WP_NONE,",
		"WP_GAUNTLET,",
		"WP_HEAVY_MACHINEGUN",
	):
		assert expected in servercmds_source

	for expected in (
		"memset( cg.weaponAccuracies, 0, sizeof( cg.weaponAccuracies ) );",
		"weapon = cg_retailAccuracyCommandOrder[i];",
		"value = atoi( CG_Argv( i + 1 ) );",
		"cg.weaponAccuracies[weapon] = value;",
	):
		assert expected in shared_parse_block

	assert 'if ( !strcmp( cmd, "acc" ) ) {' in servercmds_source
	assert "\t\tCG_ParseAcc();" in servercmds_source
	assert 'if ( !strcmp( cmd, "pstats" ) ) {' in servercmds_source
	assert "\t\tCG_ParsePStats();" in servercmds_source
	assert "CG_ParseRetailAccuracyCommand();" in parse_block
	assert "CG_ParseRetailAccuracyCommand();" in pstats_parse_block

	assert '"+acc"' in console_source
	assert '"-acc"' in console_source
	assert '"+pstats"' in console_source
	assert '"-pstats"' in console_source
	assert 'trap_AddCommand ("acc");' in console_source
	assert "cg.accRequestActive = qtrue;" in acc_down_block
	assert "cg.accRequestTime = 0;" in acc_down_block
	assert 'trap_SendClientCommand( "acc" );' in acc_down_block
	assert "cg.accRequestActive = qfalse;" in acc_up_block
	assert 'trap_SendClientCommand( "pstats" );' in pstats_down_block
	assert "cg_pstatsRequestActive = qtrue;" in pstats_down_block
	assert "cg_pstatsRequestActive = qfalse;" in pstats_up_block

	for expected in (
		"static const weapon_t cgVerticalAccWeaponOrder[] = {",
		"WP_MACHINEGUN,",
		"WP_BFG,",
		"WP_HEAVY_MACHINEGUN",
	):
		assert expected in newdraw_source

	assert "if ( !cg.accRequestActive || !cg.snap ) {" in draw_gate_block
	assert "cg.snap->ps.pm_type == PM_SPECTATOR" in draw_gate_block
	assert "cg.snap->ps.pm_flags & PMF_FOLLOW" in draw_gate_block
	assert 'trap_SendClientCommand( "acc" );' in draw_gate_block

	assert "icon = CG_GetStartingWeaponIconHandle( cgVerticalAccWeaponOrder[i] );" in draw_weapon_block
	assert "CG_DrawPic( rect->x, rect->y + rect->h * i, rect->w, rect->w, icon );" in draw_weapon_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%i%%", cg.weaponAccuracies[weapon] );' in draw_acc_block
	assert "CG_Text_Paint( rect->x, rect->y + rect->h * ( i + 1 ), scale, color, buffer, 0, 0, textStyle );" in draw_acc_block

	assert "case CG_WP_VERTICAL:" in newdraw_source
	assert "CG_DrawWeaponVertical( &rect, color );" in newdraw_source
	assert "case CG_ACC_VERTICAL:" in newdraw_source
	assert "CG_DrawAccVertical( &rect, scale, color, textStyle );" in newdraw_source

	for expected in (
		"static const weapon_t retailAccuracyCommandOrder[] = {",
		"WP_NONE,",
		"WP_GAUNTLET,",
		"WP_HEAVY_MACHINEGUN",
	):
		assert expected in game_source

	assert "ent->client->sess.sessionTeam == TEAM_SPECTATOR" in source_client_block
	assert "ent->client->sess.spectatorState == SPECTATOR_FOLLOW" in source_client_block
	assert "ent->client->sess.spectatorClient" in source_client_block
	assert "level.clients[clientNum].pers.connected == CON_CONNECTED" in source_client_block

	assert "client = G_RetailAccuracySourceClient( ent );" in shared_sender_block
	assert "client->pers.accuracy_hits[weapon]" in shared_sender_block
	assert "client->pers.accuracy_shots[weapon]" in shared_sender_block
	assert 'trap_SendServerCommand( ent-g_entities, va( "%s %s", command, payload ) );' in shared_sender_block
	assert 'G_SendRetailAccuracyPayloadCommand( ent, "acc" );' in sender_block
	assert 'G_SendRetailAccuracyPayloadCommand( ent, "pstats" );' in pstats_sender_block
	assert "G_SendRetailAccuracyCommand( ent );" in cmd_acc_block
	assert "G_SendRetailPStatsCommand( ent );" in cmd_pstats_block
	assert 'else if (Q_stricmp (cmd, "pstats") == 0) {' in game_source


def test_cgame_placement_scorebox_widgets_match_retail_split_ownerdraws() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	slot_block = _block_from_marker(source, "static int CG_GetSpectatorOwnerDrawSlot")
	flag_shader_block = _block_from_marker(source, "static qhandle_t CG_GetPlacementFlagShader")
	flag_block = _block_from_marker(source, "static void CG_DrawPlacementFlagOwnerDraw")
	avatar_block = _block_from_marker(source, "static void CG_DrawPlacementAvatarOwnerDraw")
	frags_block = _block_from_marker(source, "static qboolean CG_DrawPlacementFragsOwnerDraw")
	deaths_block = _block_from_marker(source, "static qboolean CG_DrawPlacementDeathsOwnerDraw")
	damage_block = _block_from_marker(source, "static qboolean CG_DrawPlacementDamageOwnerDraw")
	wins_block = _block_from_marker(source, "static qboolean CG_DrawPlacementWinsOwnerDraw")
	build_metric_block = _block_from_marker(source, "static qboolean CG_BuildPlacementMetricText")
	draw_metric_block = _block_from_marker(source, "static qboolean CG_DrawPlacementMetricOwnerDraw")

	for expected in (
		"case CG_1ST_PLYR_HEALTH_ARMOR:",
		"case CG_2ND_PLYR_HEALTH_ARMOR:",
		"case CG_SPEC_COMPARE_PRIMARY:",
		"case CG_SPEC_COMPARE_SECONDARY:",
	):
		assert expected in slot_block

	assert "ci->countryFlagShader ? ci->countryFlagShader : CG_RegisterCountryFlag( ci->country );" in flag_shader_block
	assert "PW_REDFLAG" not in flag_shader_block
	assert "PW_BLUEFLAG" not in flag_shader_block
	assert "PW_NEUTRALFLAG" not in flag_shader_block

	assert "CG_GetPlacementFlagShader( slot );" in flag_block
	assert "CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );" in flag_block
	assert "CG_DrawSpectatorProfileImage( rect, slot );" in avatar_block

	assert 'Com_sprintf( buffer, sizeof( buffer ), "%i", CG_GetPlacementFragCount( score ) );' in frags_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%i", score->deaths );' in deaths_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%i", score->damage );' in damage_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%i", ci->wins );' in wins_block

	assert "case CG_1ST_PLYR_FLAG:" in build_metric_block
	assert 'Q_strncpyz( buffer, hasFlag ? "Yes" : "-", bufferSize );' not in source

	for expected in (
		"case CG_1ST_PLYR_FRAGS:",
		"return CG_DrawPlacementFragsOwnerDraw( rect, scale, color, textStyle, slot );",
		"case CG_1ST_PLYR_DEATHS:",
		"return CG_DrawPlacementDeathsOwnerDraw( rect, scale, color, textStyle, slot );",
		"case CG_1ST_PLYR_DMG:",
		"return CG_DrawPlacementDamageOwnerDraw( rect, scale, color, textStyle, slot );",
		"case CG_1ST_PLYR_WINS:",
		"return CG_DrawPlacementWinsOwnerDraw( rect, scale, color, textStyle, slot );",
		"case CG_1ST_PLYR_FLAG:",
		"CG_DrawPlacementFlagOwnerDraw( rect, slot );",
	):
		assert expected in draw_metric_block

	assert "case CG_1ST_PLYR_HEALTH_ARMOR:" in source
	assert "CG_DrawSpectatorComparison( &rect, scale, color, textStyle, ownerDraw );" in source
	assert "case CG_1ST_PLYR_AVATAR:" in source
	assert "CG_DrawPlacementAvatarOwnerDraw( &rect, 0 );" in source
	assert "case CG_2ND_PLYR_AVATAR:" in source
	assert "CG_DrawPlacementAvatarOwnerDraw( &rect, 1 );" in source


def test_cgame_placement_metric_wrappers_restore_retail_direct_owners() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	resolve_block = _block_from_marker(source, "static qboolean CG_ResolvePlacementMetricOwnerDraw")
	text_block = _block_from_marker(source, "static qboolean CG_DrawPlacementMetricTextOwnerDraw")
	ping_block = _block_from_marker(source, "static void CG_DrawPlacementPingOwnerDraw")
	accuracy_block = _block_from_marker(source, "static void CG_DrawPlacementAccuracyOwnerDraw")
	weapon_frags_block = _block_from_marker(source, "static void CG_DrawPlacementWeaponFragsOwnerDraw")
	weapon_hits_block = _block_from_marker(source, "static void CG_DrawPlacementWeaponHitsOwnerDraw")
	weapon_shots_block = _block_from_marker(source, "static void CG_DrawPlacementWeaponShotsOwnerDraw")
	weapon_damage_block = _block_from_marker(source, "static void CG_DrawPlacementWeaponDamageOwnerDraw")
	weapon_accuracy_block = _block_from_marker(source, "static void CG_DrawPlacementWeaponAccuracyOwnerDraw")
	pickup_count_block = _block_from_marker(source, "static void CG_DrawPlacementPickupCountOwnerDraw")
	pickup_average_block = _block_from_marker(source, "static void CG_DrawPlacementPickupAverageOwnerDraw")
	award_count_block = _block_from_marker(source, "static void CG_DrawPlacementAwardCountOwnerDraw")
	dispatch_block = _block_from_marker(source, "static qboolean CG_DrawPlacementMetricOwnerDraw")

	for expected in (
		"if ( ownerDraw >= CG_1ST_PLYR_READY && ownerDraw <= CG_1ST_PLYR_TIER ) {",
		"} else if ( ownerDraw >= CG_2ND_PLYR_READY && ownerDraw <= CG_2ND_PLYR_TIER ) {",
		"resolvedOwnerDraw = ownerDraw - ( CG_2ND_PLYR - CG_1ST_PLYR );",
	):
		assert expected in resolve_block

	for expected in (
		"score = CG_GetPlacementScore( slot );",
		"ci = CG_GetPlacementClientInfo( score );",
		"CG_BuildPlacementMetricText( normalized, score, ci, buffer, sizeof( buffer ) )",
		"CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );",
	):
		assert expected in text_block

	for expected in (
		"if ( score->ping >= 80 ) {",
		"} else if ( score->ping >= 40 ) {",
		"(void)CG_DrawPlacementMetricTextOwnerDraw( rect, scale, drawColor, textStyle, ownerDraw );",
	):
		assert expected in ping_block

	for wrapper_block in (
		accuracy_block,
		weapon_frags_block,
		weapon_hits_block,
		weapon_shots_block,
		weapon_damage_block,
		weapon_accuracy_block,
		pickup_count_block,
		pickup_average_block,
		award_count_block,
	):
		assert "(void)CG_DrawPlacementMetricTextOwnerDraw( rect, scale, color, textStyle, ownerDraw );" in wrapper_block

	for expected in (
		"CG_DrawPlacementPingOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementAccuracyOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementWeaponFragsOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementWeaponHitsOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementWeaponShotsOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementWeaponDamageOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementWeaponAccuracyOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementPickupCountOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementPickupAverageOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementAwardCountOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"return CG_DrawPlacementMetricTextOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
	):
		assert expected in dispatch_block


def test_cgame_country_flag_cache_restores_retail_player_configstring_transport() -> None:
	cg_main = CG_MAIN.read_text(encoding="utf-8")
	cg_players = CG_PLAYERS.read_text(encoding="utf-8")
	cg_local = CG_LOCAL.read_text(encoding="utf-8")
	g_client = G_CLIENT.read_text(encoding="utf-8")
	init_block = _block_from_marker(cg_main, "void CG_Init( int serverMessageNum, int serverCommandSequence, int clientNum )")
	cache_block = _block_from_marker(cg_main, "static void CG_CacheCountryFlags( void )")
	register_block = _block_from_marker(cg_main, "qhandle_t CG_RegisterCountryFlag( const char *countryCode )")
	new_client_block = _block_from_marker(cg_players, "void CG_NewClientInfo( int clientNum )")

	assert "country[MAX_COUNTRY_CODE]" in cg_local
	assert "countryFlagShader;" in cg_local

	for expected in (
		"ui/assets/flags/none.tga",
		"ui/country.txt",
		"ERROR: CG_CacheCountryFlags: %s too small\\n",
		"ERROR: CG_CacheCountryFlags: %s too large. Size is %d, limit is %d\\n",
		"trap_FS_FOpenFile( filename, &f, FS_READ );",
		"trap_FS_Read( buffer, len, f );",
		"token = COM_Parse( &text_p );",
		"CG_RegisterCountryFlag( token );",
	):
		assert expected in cache_block

	for expected in (
		'Com_sprintf( filename, sizeof( filename ), "ui/assets/flags/%s.tga", normalized );',
		'trap_R_RegisterShaderNoMip( "ui/assets/flags/none.tga" );',
		"Q_strlwr( normalized );",
	):
		assert expected in register_block

	assert init_block.index("CG_ParseServerinfo();") < init_block.index("CG_CacheCountryFlags();") < init_block.index("CG_InitDisplayContext();")
	assert 'Info_ValueForKey( configstring, "country" );' in new_client_block
	assert "newInfo.countryFlagShader = CG_RegisterCountryFlag( newInfo.country );" in new_client_block
	assert 'Info_ValueForKey( userinfo, "country" )' in g_client
	assert g_client.count(r"\\country\\%s") >= 2


def test_cgame_live_placement_and_follow_ownerdraws_follow_retail_helper_split() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	first_place_block = _block_from_marker(source, "static void CG_Draw1stPlace(")
	second_place_block = _block_from_marker(source, "static void CG_Draw2ndPlace(")
	value_block = _block_from_marker(source, "static qboolean CG_BuildPlacementScoreValue")
	line_block = _block_from_marker(source, "static void CG_DrawPlacementScoreLine")
	first_score_block = _block_from_marker(source, "static void CG_Draw1stPlaceScore")
	second_score_block = _block_from_marker(source, "static void CG_Draw2ndPlaceScore")
	follow_block = _block_from_marker(source, "static void CG_DrawFollowPlayerNameEx")

	assert 'CG_Text_Paint(rect->x, rect->y, scale, color, va("%2i", cgs.scores1),0, 0, textStyle);' in first_place_block
	assert 'CG_Text_Paint(rect->x, rect->y, scale, color, va("%2i", cgs.scores2),0, 0, textStyle);' in second_place_block

	for expected in (
		"if ( cgs.gametype == GT_RACE ) {",
		"CG_RaceFormatMilliseconds( value, buffer, bufferSize );",
		'Q_strncpyz( buffer, "-", bufferSize );',
		'Com_sprintf( buffer, bufferSize, "%d", value );',
	):
		assert expected in value_block

	for expected in (
		"CG_Text_Paint_Limit( &maxX, x, rect->y, scale, color, nameText, 0, 0 );",
		'CG_Text_Paint( ellipsisX, rect->y, scale, color, "...", 0, 0, textStyle );',
		"CG_Text_Paint( valueX, rect->y, scale, color, valueText, 0, 0, textStyle );",
	):
		assert expected in line_block

	for expected in (
		"CG_GetActiveScoreByIndex( 0 );",
		'CG_DrawPlacementScoreLine( rect, scale, color, textStyle, "1. ", nameBuffer, valueBuffer );',
		"CG_GetTeamName( leaderTeam )",
	):
		assert expected in first_score_block

	for expected in (
		"score = CG_GetScoreForClientNum( cg.snap->ps.clientNum );",
		"score = CG_GetActiveScoreByIndex( 1 );",
		'Com_sprintf( rankBuffer, sizeof( rankBuffer ), "%d. ", localRank );',
		"CG_DrawPlacementScoreLine( rect, scale, color, textStyle, rankBuffer, nameBuffer, valueBuffer );",
	):
		assert expected in second_score_block

	for expected in (
		"if ( ownerDraw == CG_FOLLOW_PLAYER_NAME ) {",
		'"Following - %s"',
		"Q_strncpyz( buffer, ci->name, sizeof( buffer ) );",
		"Vector4Copy( CG_TeamColor( ci->team ), drawColor );",
		"if ( align == ITEM_ALIGN_CENTER ) {",
		"} else if ( align == ITEM_ALIGN_RIGHT ) {",
	):
		assert expected in follow_block

	assert "case CG_1ST_PLACE_SCORE:" in source
	assert "CG_Draw1stPlaceScore(&rect, scale, color, textStyle);" in source
	assert "case CG_2ND_PLACE_SCORE:" in source
	assert "CG_Draw2ndPlaceScore(&rect, scale, color, textStyle);" in source
	assert "case CG_FOLLOW_PLAYER_NAME:" in source
	assert "CG_DrawFollowPlayerNameEx(&rect, scale, color, textStyle, ownerDraw, align);" in source
	assert "case CG_FOLLOW_PLAYER_NAME_EX:" in source


def test_cgame_objective_ownerdraws_restore_retail_flag_key_and_powerup_seam() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	harvester_block = _block_from_marker(source, "static void CG_HarvesterSkulls")
	oneflag_block = _block_from_marker(source, "static void CG_OneFlagStatus")
	powerup_block = _block_from_marker(source, "static void CG_DrawCTFPowerUp")
	key_block = _block_from_marker(source, "static void CG_DrawPlayerHasKey")
	flag_block = _block_from_marker(source, "static void CG_DrawPlayerHasFlag")

	assert "int value = cg.snap->ps.generic1;" in harvester_block
	assert "value = cg.snap->ps.stats[STAT_PERSISTANT_POWERUP];" in powerup_block
	assert "x += rect->w * 0.5f;" in key_block
	assert "x += rect->w * 0.65f;" not in key_block

	for expected in (
		"shaderIndex = 0;",
		"case FLAG_TAKEN_RED:",
		"shaderIndex = 1;",
		"case FLAG_TAKEN_BLUE:",
		"shaderIndex = 2;",
		"case FLAG_DROPPED:",
		"shaderIndex = 3;",
		"CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cgs.media.flagShader[shaderIndex] );",
	):
		assert expected in oneflag_block

	assert "cgs.media.flagShaders[index]" not in oneflag_block

	for expected in (
		"inset = force2D ? 0.0f : 4.0f;",
		'key = trap_Key_GetKey( "dropflag" );',
		'trap_Key_KeynumToStringBuf( key, keyName, sizeof( keyName ) );',
		'Q_strupr( keyName );',
		'Com_sprintf( prompt, sizeof( prompt ), "Press %s to throw.", keyName );',
		'CG_Text_Paint( promptX, rect->y + rect->h, promptScale, promptColor, prompt, 0, 0, 3 );',
	):
		assert expected in flag_block

	for expected in (
		"case CG_ONEFLAG_STATUS:",
		"CG_OneFlagStatus(&rect);",
		"case CG_CTF_POWERUP:",
		"CG_DrawCTFPowerUp(&rect);",
		"case CG_PLAYER_HASFLAG:",
		"CG_DrawPlayerHasFlag(&rect, qfalse);",
		"case CG_PLAYER_HASFLAG2D:",
		"CG_DrawPlayerHasFlag(&rect, qtrue);",
		"case CG_PLAYER_HASKEY:",
		"CG_DrawPlayerHasKey( &rect );",
	):
		assert expected in source


def test_cgame_classic_player_status_ownerdraws_follow_retail_leaf_split() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	health_range_block = _block_from_marker(source, "static void CG_DrawPlayerHealthBarRange")
	health_100_block = _block_from_marker(source, "static void CG_DrawPlayerHealthBar100")
	health_200_block = _block_from_marker(source, "static void CG_DrawPlayerHealthBar200")
	armor_range_block = _block_from_marker(source, "static void CG_DrawPlayerArmorBarRange")
	armor_100_block = _block_from_marker(source, "static void CG_DrawPlayerArmorBar100")
	armor_200_block = _block_from_marker(source, "static void CG_DrawPlayerArmorBar200")
	armor_icon_block = _block_from_marker(source, "static void CG_DrawPlayerArmorIcon")
	armor_value_block = _block_from_marker(source, "static void CG_DrawPlayerArmorValue")
	ammo_icon_block = _block_from_marker(source, "static void CG_DrawPlayerAmmoIcon")
	ammo_value_block = _block_from_marker(source, "static void CG_DrawPlayerAmmoValue")
	head_block = _block_from_marker(source, "static void CG_DrawPlayerHead")
	tiered_block = _block_from_marker(source, "static void CG_DrawArmorTieredColorized")

	for expected in (
		"ratio = use200Range ? CG_NormalizedTo200( health ) : CG_NormalizedTo100( health );",
		"shader = use200Range ? cgs.media.healthBar200 : cgs.media.healthBar100;",
		"CG_DrawBarFill( rect, shader, ratio, barColor );",
	):
		assert expected in health_range_block

	assert "CG_DrawPlayerHealthBarRange( rect, shader, qfalse );" in health_100_block
	assert "CG_DrawPlayerHealthBarRange( rect, shader, qtrue );" in health_200_block

	for expected in (
		"CG_GetArmorTierColor( armor, barColor );",
		"ratio = use200Range ? CG_NormalizedTo200( armor ) : CG_NormalizedTo100( armor );",
		"shader = use200Range ? cgs.media.armorBar200 : cgs.media.armorBar100;",
	):
		assert expected in armor_range_block

	assert "CG_DrawPlayerArmorBarRange( rect, shader, qfalse );" in armor_100_block
	assert "CG_DrawPlayerArmorBarRange( rect, shader, qtrue );" in armor_200_block

	for expected in (
		"cgs.media.armorIcon",
		"cgs.media.armorModel",
		"CG_Draw3DModel( rect->x, rect->y, rect->w, rect->h, cgs.media.armorModel, 0, origin, angles );",
	):
		assert expected in armor_icon_block

	assert "value = ps->stats[STAT_ARMOR];" in armor_value_block

	for expected in (
		"cg_weapons[ cg.predictedPlayerState.weapon ].ammoIcon",
		"cg_weapons[ cent->currentState.weapon ].ammoModel",
		"CG_Draw3DModel( rect->x, rect->y, rect->w, rect->h, cg_weapons[ cent->currentState.weapon ].ammoModel, 0, origin, angles );",
	):
		assert expected in ammo_icon_block

	assert "value = ps->ammo[cent->currentState.weapon];" in ammo_value_block
	assert "CG_DrawHead( x, rect->y, rect->w, rect->h, cg.snap->ps.clientNum, angles );" in head_block

	for expected in (
		"CG_GetArmorTierColor( cg.snap->ps.stats[STAT_ARMOR], color );",
		"color[3] = 0.5f;",
		"CG_FillRect( rect->x, rect->y, rect->w, rect->h, color );",
	):
		assert expected in tiered_block

	for expected in (
		"case CG_PLAYER_ARMOR_BAR_100:",
		"CG_DrawPlayerArmorBar100( &rect, shader );",
		"case CG_PLAYER_ARMOR_BAR_200:",
		"CG_DrawPlayerArmorBar200( &rect, shader );",
		"case CG_PLAYER_HEALTH_BAR_100:",
		"CG_DrawPlayerHealthBar100( &rect, shader );",
		"case CG_PLAYER_HEALTH_BAR_200:",
		"CG_DrawPlayerHealthBar200( &rect, shader );",
		"case CG_PLAYER_ARMOR_ICON:",
		"CG_DrawPlayerArmorIcon( &rect, ownerDrawFlags & CG_SHOW_2DONLY );",
		"case CG_PLAYER_ARMOR_VALUE:",
		"CG_DrawPlayerArmorValue( &rect, scale, color, shader, textStyle );",
		"case CG_PLAYER_AMMO_ICON:",
		"CG_DrawPlayerAmmoIcon( &rect, ownerDrawFlags & CG_SHOW_2DONLY );",
		"case CG_PLAYER_AMMO_VALUE:",
		"CG_DrawPlayerAmmoValue( &rect, scale, color, shader, textStyle );",
		"case CG_PLAYER_HEAD:",
		"CG_DrawPlayerHead( &rect, ownerDrawFlags & CG_SHOW_2DONLY );",
		"case CG_PLAYER_HEALTH:",
		"CG_DrawPlayerHealth( &rect, scale, color, shader, textStyle );",
	):
		assert expected in source


def test_cgame_team_score_name_playercount_and_match_phase_ownerdraws_follow_retail_shared_leaves() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	align_block = _block_from_marker(source, "static float CG_AlignTextInRectX")
	score_text_block = _block_from_marker(source, "static qboolean CG_BuildTeamScoreText")
	score_block = _block_from_marker(source, "static void CG_DrawTeamScore")
	name_block = _block_from_marker(source, "static void CG_DrawTeamName")
	player_count_block = _block_from_marker(source, "static void CG_DrawTeamPlayerCount")
	match_phase_block = _block_from_marker(source, "static const char *CG_GetMatchPhaseText")
	match_status_block = _block_from_marker(source, "static const char *CG_GetMatchStatusText")
	match_state_block = _block_from_marker(source, "static void CG_DrawMatchState")

	for expected in (
		"if ( align == ITEM_ALIGN_CENTER ) {",
		"if ( align == ITEM_ALIGN_RIGHT ) {",
		"return rect->x;",
	):
		assert expected in align_block

	for expected in (
		"score = ( team == TEAM_RED ) ? cgs.scores1 : cgs.scores2;",
		"if ( score == SCORE_NOT_PRESENT || score == CG_SCORE_FORFEIT ) {",
		'Q_strncpyz( buffer, "-", bufferSize );',
		'Com_sprintf( buffer, bufferSize, "%i", score );',
	):
		assert expected in score_text_block

	for expected in (
		"CG_TranslateHudRectForWidescreen( rect, &widescreenRect );",
		"x = CG_AlignTextInRectX( &widescreenRect, scale, buffer, align );",
		"CG_Text_Paint( x, widescreenRect.y + widescreenRect.h, scale, color, buffer, 0, 0, textStyle );",
	):
		assert expected in score_block

	for expected in (
		"teamName = CG_GetTeamName( team );",
		"x = CG_AlignTextInRectX( &widescreenRect, scale, teamName, align );",
	):
		assert expected in name_block

	for expected in (
		"teamLimit = cgs.playerCountTeamSize;",
		"case GT_TEAM:",
		'Com_sprintf( buffer, sizeof( buffer ), "(%d/%d)", count, teamLimit );',
		'Com_sprintf( buffer, sizeof( buffer ), "(%d)", count );',
		"if ( teamLimit > 0 && teamLimit * 2 <= cgs.maxclients ) {",
		'Com_sprintf( buffer, sizeof( buffer ), "%d/%d Players", count, teamLimit );',
		'Com_sprintf( buffer, sizeof( buffer ), "%d Player%s", count, ( count == 1 ) ? "" : "s" );',
		"x = CG_AlignTextInRectX( rect, scale, buffer, align );",
	):
		assert expected in player_count_block

	for expected in (
		'return "MATCH SUMMARY";',
		'return "MATCH WARMUP";',
		'return "MATCH IN PROGRESS";',
	):
		assert expected in match_phase_block

	assert "phase = CG_GetMatchPhaseText();" in match_status_block
	assert "CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, CG_GetMatchPhaseText(), 0, 0, textStyle );" in match_state_block

	for expected in (
		"case CG_RED_SCORE:",
		"CG_DrawTeamScore( &rect, scale, color, textStyle, TEAM_RED, align );",
		"case CG_BLUE_SCORE:",
		"CG_DrawTeamScore( &rect, scale, color, textStyle, TEAM_BLUE, align );",
		"case CG_RED_PLAYER_COUNT:",
		"CG_DrawTeamPlayerCount(&rect, scale, color, textStyle, TEAM_RED, align);",
		"case CG_BLUE_PLAYER_COUNT:",
		"CG_DrawTeamPlayerCount(&rect, scale, color, textStyle, TEAM_BLUE, align);",
		"case CG_RED_NAME:",
		"CG_DrawTeamName( &rect, scale, color, textStyle, TEAM_RED, align );",
		"case CG_BLUE_NAME:",
		"CG_DrawTeamName( &rect, scale, color, textStyle, TEAM_BLUE, align );",
		"case CG_MATCH_STATE:",
		"CG_DrawMatchState(&rect, scale, color, textStyle);",
	):
		assert expected in source

	assert "static void CG_DrawRedScore" not in source
	assert "static void CG_DrawBlueScore" not in source
	assert "static void CG_DrawRedName" not in source
	assert "static void CG_DrawBlueName" not in source


def test_cgame_intro_panel_and_player_count_widgets_restore_retail_detail_and_cap_rules() -> None:
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	game_source = G_MAIN.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	player_limit_block = _block_from_marker(newdraw_source, "static int CG_GetConfiguredPlayerCountLimit")
	player_counts_block = _block_from_marker(newdraw_source, "static void CG_DrawPlayerCounts")
	location_block = _block_from_marker(newdraw_source, "static void CG_GetServerLocation")
	detail_block = _block_from_marker(newdraw_source, "static void CG_BuildIntroPanelDetailString")
	game_type_map_block = _block_from_marker(newdraw_source, "static void CG_DrawGameTypeMap")
	match_details_block = _block_from_marker(newdraw_source, "static void CG_DrawMatchDetails")
	parse_serverinfo_block = _block_from_marker(servercmds_source, "void CG_ParseServerinfo")

	assert "playerCountTeamSize;" in local_source

	for expected in (
		"playerLimit = cgs.maxclients;",
		"if ( cgs.gametype == GT_FFA || cgs.playerCountTeamSize <= 0 ) {",
		"playerLimit = cgs.playerCountTeamSize * 2;",
		"if ( playerLimit > cgs.maxclients ) {",
		"return cgs.playerCountTeamSize;",
	):
		assert expected in player_limit_block

	for expected in (
		"active = CG_CountActivePlayers();",
		"playerLimit = CG_GetConfiguredPlayerCountLimit();",
		"if ( playerLimit <= 0 ) {",
		'Com_sprintf( buffer, sizeof( buffer ), "%i/%i Players", active, playerLimit );',
	):
		assert expected in player_counts_block

	for expected in (
		'CG_GetServerInfoValue( info, "location", buffer, bufferSize );',
		'CG_GetServerInfoValue( info, "sv_location", buffer, bufferSize );',
		'CG_GetServerInfoValue( info, "server_location", buffer, bufferSize );',
		'CG_GetServerInfoValue( info, "sv_hostname", buffer, bufferSize );',
	):
		assert expected in location_block

	for expected in (
		"CG_GetMapDisplayName( mapName, sizeof( mapName ) );",
		"CG_GetServerLocation( location, sizeof( location ) );",
		'Com_sprintf( buffer, bufferSize, "%s - %s", location, mapName );',
		'Q_strncpyz( buffer, mapName, bufferSize );',
	):
		assert expected in detail_block

	assert "CG_BuildIntroPanelDetailString( detailBuffer, sizeof( detailBuffer ) );" in game_type_map_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%s - %s", CG_GameTypeString(), detailBuffer );' in game_type_map_block
	assert "CG_BuildIntroPanelDetailString( detailBuffer, sizeof( detailBuffer ) );" in match_details_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%s - %s - %s",' in match_details_block

	assert '&g_teamSizeMin, "g_teamSizeMin", &g_teamSizeLegacy, "teamsize", "0", CVAR_SERVERINFO | CVAR_NORESTART' in game_source

	for expected in (
		'playerCountTeamSizeValue = Info_ValueForKey( info, "teamsize" );',
		"cgs.playerCountTeamSize = playerCountTeamSizeValue[0] ? atoi( playerCountTeamSizeValue ) : 0;",
		"if ( cgs.playerCountTeamSize < 0 ) {",
	):
		assert expected in parse_serverinfo_block

	assert 'Info_ValueForKey( info, "g_teamSizeMin" )' not in parse_serverinfo_block


def test_cgame_hud_ownerdraw_reconstruction_keeps_retail_medal_spectator_advert_and_team_pickup_seam() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	syscalls_source = CG_SYSCALLS.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	public_source = CG_PUBLIC.read_text(encoding="utf-8")
	client_source = CL_CGAME.read_text(encoding="utf-8")
	build_spectator_block = _block_from_marker(main_source, "void CG_BuildSpectatorString()")
	speedometer_block = _block_from_marker(newdraw_source, "static void CG_DrawSpeedometerOwnerDraw")
	spectator_block = _block_from_marker(newdraw_source, "void CG_DrawTeamSpectators")
	advert_block = _block_from_marker(newdraw_source, "static void CG_DrawAdvert")
	medal_block = _block_from_marker(newdraw_source, "void CG_DrawMedal")
	team_pickup_block = _block_from_marker(newdraw_source, "static void CG_DrawTeamPickupOwnerDraw")
	syscall_block = _block_from_marker(syscalls_source, "void trap_QL_UpdateAdvert")
	client_block = _block_from_marker(client_source, "static void QDECL QL_CG_trap_UpdateAdvert")

	for expected in (
		"cg.spectatorOffset = 0;",
		"cg.spectatorPaintX = 0;",
		"cg.spectatorPaintX2 = 0;",
		"cg.spectatorPaintLen = 0;",
		"cg.spectatorTime = 0;",
	):
		assert expected in build_spectator_block

	assert "CG_DrawSpeedometer( rect, scale, color, textStyle );" in speedometer_block

	for expected in (
		"cg.spectatorOffset < 0 || cg.spectatorOffset >= cg.spectatorEntryCount",
		"entry = cg.spectatorEntries[i];",
		"pendingWidth += 10;",
		"CG_Text_Paint( x, y, scale, color, entry, 0, 0, 0 );",
		"cg.spectatorTime = cg.time + 4000;",
		"cg.spectatorOffset = startIndex + displayedCount;",
	):
		assert expected in spectator_block
	assert "CG_UpdateSpectatorTargets();" not in spectator_block

	for expected in (
		"trap_R_SetColor( color );",
		"CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );",
		"pixelArea = (int)( rect->w * rect->h );",
		"trap_QL_UpdateAdvert( shader, pixelArea );",
		"trap_R_SetColor( NULL );",
	):
		assert expected in advert_block

	for expected in (
		"case CG_ACCURACY:",
		'text = va("%i%%", (int)value);',
		'text = "Wow";',
		"CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );",
	):
		assert expected in medal_block

	assert "CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );" in team_pickup_block

	assert "case CG_SPECTATORS:" in newdraw_source
	assert "CG_DrawTeamSpectators(&rect, scale, color, shader);" in newdraw_source
	assert "case UI_ADVERT:" in newdraw_source
	assert "CG_DrawAdvert( &rect, color, shader );" in newdraw_source
	assert "case CG_SPEEDOMETER:" in newdraw_source
	assert "CG_DrawSpeedometerOwnerDraw( &rect, scale, color, textStyle );" in newdraw_source

	assert "CG_QL_IMPORT_UPDATE_ADVERT = 58," in public_source
	assert "void\t\ttrap_QL_UpdateAdvert( int handleOrToken, int area );" in local_source
	assert "cg_imports[CG_QL_IMPORT_UPDATE_ADVERT]" in syscall_block
	assert "(void)handleOrToken;" in client_block
	assert "(void)area;" in client_block
	assert "ql_cgame_imports[CG_QL_IMPORT_UPDATE_ADVERT] = (ql_import_f)QL_CG_trap_UpdateAdvert;" in client_source


def test_cgame_spectator_cache_restores_retail_queue_metadata_and_cached_strip() -> None:
	players_source = CG_PLAYERS.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	main_source = CG_MAIN.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	parse_block = _block_from_marker(players_source, "void CG_NewClientInfo( int clientNum )")
	compare_block = _block_from_marker(main_source, "static int QDECL CG_CompareSpectatorClients")
	build_block = _block_from_marker(main_source, "void CG_BuildSpectatorString()")
	draw_block = _block_from_marker(newdraw_source, "void CG_DrawTeamSpectators")

	for expected in (
		"qboolean\t\tspectateOnly;",
		"int\t\t\t\tspectatorQueuePosition;",
		"char\t\t\tspectatorEntries[MAX_CLIENTS][64];",
		"int\t\t\t\tspectatorEntryCount;",
	):
		assert expected in local_source

	for expected in (
		'v = Info_ValueForKey( configstring, "so" );',
		"newInfo.spectateOnly = atoi( v );",
		'v = Info_ValueForKey( configstring, "pq" );',
		"newInfo.spectatorQueuePosition = atoi( v );",
	):
		assert expected in parse_block

	for expected in (
		"clientA->spectateOnly > clientB->spectateOnly",
		"clientA->spectatorQueuePosition > clientB->spectatorQueuePosition",
		"return clientNumA - clientNumB;",
	):
		assert expected in compare_block

	for expected in (
		"qsort( spectatorClients, newEntryCount, sizeof( spectatorClients[0] ), CG_CompareSpectatorClients );",
		"Q_CleanStr( cleanName );",
		'Com_sprintf( entry, sizeof( entry ), "^7(^5s^7) %s", cleanName );',
		'Com_sprintf( entry, sizeof( entry ), "(%d) %s", ci->spectatorQueuePosition, cleanName );',
		"memcpy( cg.spectatorEntries, newSpectatorEntries, sizeof( cg.spectatorEntries ) );",
		"cg.spectatorEntryCount = newEntryCount;",
	):
		assert expected in build_block

	for expected in (
		"cg.spectatorEntryCount <= 0",
		"entry = cg.spectatorEntries[i];",
		"entry = cg.spectatorEntries[startIndex + i];",
		"cg.spectatorEntryCount > displayedCount",
	):
		assert expected in draw_block

	assert "CG_UpdateSpectatorTargets();" not in draw_block


def test_cgame_team_scoreboard_and_award_ownerdraws_follow_retail_helper_split() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	average_ping_block = _block_from_marker(source, "static void CG_DrawTeamAveragePing")
	timeheld_build_block = _block_from_marker(source, "static qboolean CG_BuildTeamTimeHeldText")
	timeheld_block = _block_from_marker(source, "static void CG_DrawTeamTimeHeldOwnerDraw")
	award_client_block = _block_from_marker(source, "static int CG_GetAwardClientNum")
	award_player_block = _block_from_marker(source, "static qboolean CG_DrawAwardPlayer")

	assert 'Com_sprintf( buffer, sizeof( buffer ), "Avg ping %i", average );' in average_ping_block
	assert "if ( !CG_IsTeamTimeHeldOwnerDraw( ownerDraw ) ) {" in timeheld_build_block
	assert 'Q_strncpyz( buffer, CG_FormatMinutesSeconds( value ), bufferSize );' in timeheld_build_block
	assert "CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );" in timeheld_block

	assert "score = CG_FindAwardScore( ownerDraw );" in award_client_block
	assert "if ( !CG_IsAwardOwnerDraw( ownerDraw ) ) {" in award_player_block
	assert "clientNum = CG_GetAwardClientNum( ownerDraw );" in award_player_block
	assert "CG_DrawProfileModel( rect, clientNum, qtrue );" in award_player_block

	assert "if ( CG_DrawAwardPlayer( &rect, ownerDraw ) ) {" in source
	assert "case CG_RED_AVG_PING:" in source
	assert "CG_DrawTeamAveragePing(&rect, scale, color, textStyle, TEAM_RED);" in source
	assert "case CG_BLUE_AVG_PING:" in source
	assert "CG_DrawTeamAveragePing(&rect, scale, color, textStyle, TEAM_BLUE);" in source
	assert "case CG_RED_TEAM_TIMEHELD_QUAD:" in source
	assert "case CG_BLUE_TEAM_TIMEHELD_INVIS:" in source
	assert "CG_DrawTeamTimeHeldOwnerDraw( &rect, scale, color, textStyle, ownerDraw );" in source


def test_register_cvars_publishes_retail_version_and_vote_reset() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	block = _block_from_marker(source, "void CG_RegisterCvars")
	load_hud_block = _block_from_marker(source, "void CG_LoadHudMenu()")

	assert 'trap_Cvar_Register(NULL, "cg_version", Q3_VERSION, CVAR_ROM );' in block
	assert 'trap_Cvar_Set( "ui_voteactive", "0" );' in block
	assert "cg.hudMenusLoaded = CG_HudScriptHasMenuLoads( hudSet );" in load_hud_block
	assert "cg.competitiveHudLoaded = CG_HudScriptHasCompetitiveMenus( hudSet );" in load_hud_block


def test_load_hud_menu_uses_menu_load_presence_for_runtime_hud_gate() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	draw_source = CG_DRAW.read_text(encoding="utf-8")
	menu_load_block = _block_from_marker(source, "static qboolean CG_HudScriptHasMenuLoads")
	competitive_block = _block_from_marker(source, "static qboolean CG_HudScriptHasCompetitiveMenus")
	menu_gate_block = _block_from_marker(draw_source, "static qboolean CG_IsMenuHudActive")

	assert 'return ( strstr( buffer, "loadMenu" ) != NULL ) ? qtrue : qfalse;' in menu_load_block
	assert 'if ( strstr( buffer, "comp_hud" ) || strstr( buffer, "comp_spectator" ) ) {' in competitive_block
	assert "return cg.hudMenusLoaded;" in menu_gate_block


def test_register_sounds_prefers_retail_announcer_folders_before_fallbacks() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	folder_block = _block_from_marker(source, "static const char *CG_RetailAnnouncerFolderForProfile")
	retail_clip_block = _block_from_marker(source, "static sfxHandle_t CG_RegisterRetailAnnouncerClip")
	voice_set_block = _block_from_marker(source, "static void CG_RegisterAnnouncerVoiceSet")
	argv_block = _block_from_marker(source, "const char *CG_Argv")
	error_block = _block_from_marker(source, "void QDECL CG_Error")

	assert 'return "vo";' in folder_block
	assert 'return "vo_evil";' in folder_block
	assert 'return "vo_female";' in folder_block
	assert "pathStem = CG_BuildAnnouncerSoundPathForProfile( profile, sample );" in retail_clip_block
	assert 'Com_sprintf( path, sizeof( path ), "%s%s", pathStem, exts[i] );' in retail_clip_block
	assert 'Com_sprintf( path, sizeof( path ), "sound/%s/%s%s", folder, sample, exts[i] );' not in retail_clip_block
	assert "#define CG_REGISTER_ANNOUNCER_SAMPLE(field, sample)" in voice_set_block
	assert "set->field = CG_RegisterRetailAnnouncerClip( profile, sample );" in voice_set_block
	assert "set->field = CG_RegisterAnnouncerClip( folder, sample );" in voice_set_block
	assert 'CG_REGISTER_ANNOUNCER_SAMPLE( oneMinuteSound, "1_minute" );' in voice_set_block
	assert 'CG_REGISTER_ANNOUNCER_SAMPLE( threeFragSound, "3_frags" );' in voice_set_block
	assert "trap_Argv( arg, buffer, sizeof( buffer ) );" in argv_block
	assert "trap_Error( text );" in error_block


def test_display_context_print_and_error_bridges_use_retail_direct_trap_wrappers() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	com_error_block = _block_from_marker(source, "void QDECL Com_Error")
	com_printf_block = _block_from_marker(source, "void QDECL Com_Printf")

	assert "(void)level;" in com_error_block
	assert "trap_Error( text );" in com_error_block
	assert "CG_Error( \"%s\", text);" not in com_error_block

	assert "trap_Print( text );" in com_printf_block
	assert "CG_Printf (\"%s\", text);" not in com_printf_block


def test_cgame_browser_runtime_wrappers_drive_hud_reload_and_score_feeders() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	console_source = (REPO_ROOT / "src" / "code" / "cgame" / "cg_consolecmds.c").read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")

	init_block = _block_from_marker(main_source, "void CG_InitBrowserRuntime")
	init_overlay_block = _block_from_marker(main_source, "void CG_InitBrowserOverlay")
	reset_block = _block_from_marker(main_source, "void CG_ResetBrowserOverlayState")
	item_hash_block = _block_from_marker(main_source, "void CG_SetupBrowserItemKeywordHash")
	parse_item_block = _block_from_marker(main_source, "qboolean CG_ParseBrowserItem")
	menu_hash_block = _block_from_marker(main_source, "void CG_SetupBrowserMenuKeywordHash")
	parse_menu_block = _block_from_marker(main_source, "qboolean CG_ParseBrowserMenu")
	feeder_block = _block_from_marker(main_source, "void CG_SetBrowserFeederSelection")
	load_menus_block = _block_from_marker(main_source, "void CG_LoadMenus")
	score_block = _block_from_marker(main_source, "void CG_SetScoreSelection")
	load_hud_cmd_block = _block_from_marker(console_source, "static void CG_LoadHud_f")
	cgame_init_block = _block_from_marker(main_source, "void CG_Init( int serverMessageNum, int serverCommandSequence, int clientNum )")

	assert "void CG_InitBrowserRuntime( void );" in local_source
	assert "void CG_InitBrowserOverlay( void *overlay );" in local_source
	assert "void CG_ResetBrowserOverlayState( void );" in local_source
	assert "void CG_SetupBrowserItemKeywordHash( void );" in local_source
	assert "qboolean CG_ParseBrowserItem( int handle, void *item );" in local_source
	assert "void CG_SetupBrowserMenuKeywordHash( void );" in local_source
	assert "qboolean CG_ParseBrowserMenu( int handle, void *menu );" in local_source
	assert "void CG_SetBrowserFeederSelection( void *overlay, int feeder, int index );" in local_source

	assert "String_Init();" in init_block
	assert "CG_SetupBrowserItemKeywordHash();" in init_block
	assert "CG_SetupBrowserMenuKeywordHash();" in init_block
	assert "Menu_Reset();" in reset_block
	assert "CG_ResetDraw2DMenuCache();" in reset_block
	assert "CG_ResetJoinGameMenuCaptureState();" in reset_block
	assert "menuScoreboard = NULL;" not in reset_block
	assert "Menu_Init( (menuDef_t *)overlay );" in init_overlay_block
	assert "Item_SetupKeywordHash();" in item_hash_block
	assert "return Item_Parse( handle, (itemDef_t *)item );" in parse_item_block
	assert "Menu_SetupKeywordHash();" in menu_hash_block
	assert "return Menu_Parse( handle, (menuDef_t *)menu );" in parse_menu_block
	assert "Menu_SetFeederSelection( (menuDef_t *)overlay, feeder, index, NULL );" in feeder_block

	assert "CG_ResetBrowserOverlayState();" in load_menus_block
	assert "Menu_Reset();" not in load_menus_block
	assert "CG_SetBrowserFeederSelection( menu, feeder, cg.selectedScore );" in score_block
	assert "CG_SetBrowserFeederSelection( menu, FEEDER_SCOREBOARD, cg.selectedScore );" in score_block
	assert "Menu_SetFeederSelection(menu, feeder, i, NULL);" not in score_block
	assert "Menu_SetFeederSelection(menu, FEEDER_SCOREBOARD, cg.selectedScore, NULL);" not in score_block

	assert "CG_InitBrowserRuntime();" in load_hud_cmd_block
	assert "String_Init();" not in load_hud_cmd_block
	assert "Menu_Reset();" not in load_hud_cmd_block
	assert "menuScoreboard = NULL;" not in load_hud_cmd_block

	assert "CG_InitBrowserRuntime();" in cgame_init_block


def test_cgame_browser_overlay_focus_wrappers_restore_retail_direct_owner_slice() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	screen_source = CG_SCREEN.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")

	update_presets_block = _block_from_marker(main_source, "void CG_UpdateBrowserPresetLists")
	update_positions_block = _block_from_marker(main_source, "void CG_UpdateBrowserWidgetPositions")
	find_overlay_block = _block_from_marker(main_source, "void *CG_FindBrowserOverlayByName")
	open_overlay_block = _block_from_marker(main_source, "void *CG_OpenBrowserOverlayByName")
	close_overlay_block = _block_from_marker(main_source, "void *CG_CloseBrowserOverlayByName")
	cache_block = _block_from_marker(main_source, "static void CG_CacheScoreboardSelectionMenus")
	handle_mouse_block = _block_from_marker(newdraw_source, "static void CG_BrowserHandleMouseMove")
	clear_focus_block = _block_from_marker(newdraw_source, "static void *CG_ClearBrowserFocus")
	set_focus_block = _block_from_marker(newdraw_source, "static qboolean CG_SetBrowserFocus")
	set_mouse_over_block = _block_from_marker(newdraw_source, "static void CG_SetBrowserMouseOver")
	mouse_enter_block = _block_from_marker(newdraw_source, "static void CG_BrowserMouseEnter")
	mouse_leave_block = _block_from_marker(newdraw_source, "static void CG_BrowserMouseLeave")
	prev_cursor_block = _block_from_marker(newdraw_source, "static void *CG_SetPrevBrowserCursorItem")
	next_cursor_block = _block_from_marker(newdraw_source, "static void *CG_SetNextBrowserCursorItem")
	open_join_block = _block_from_marker(screen_source, "static menuDef_t *CG_OpenJoinGameMenu")
	close_join_block = _block_from_marker(screen_source, "void CG_CloseJoinGameMenu")

	for expected in (
		"void *CG_FindBrowserOverlayByName( const char *name );",
		"void *CG_OpenBrowserOverlayByName( const char *name );",
		"void *CG_CloseBrowserOverlayByName( const char *name );",
		"void CG_UpdateBrowserPresetLists( void *overlay );",
		"void CG_UpdateBrowserWidgetPositions( void *overlay );",
		"void CG_ActivateBrowserOverlay( void *overlay );",
	):
		assert expected in local_source

	for expected in (
		'trap_Cvar_VariableStringBuffer( item->cvar, currentPreset, sizeof( currentPreset ) );',
		'trap_Cvar_Set( item->cvar, "Custom" );',
	):
		assert expected in update_presets_block

	assert "Menu_UpdatePosition( (menuDef_t *)overlay );" in update_positions_block
	assert "return Menus_FindByName( name );" in find_overlay_block

	for expected in (
		"CG_UpdateBrowserWidgetPositions( menu );",
		"CG_UpdateBrowserPresetLists( menu );",
		"CG_ActivateBrowserOverlay( menu );",
	):
		assert expected in open_overlay_block

	assert "Menus_OpenByName( name );" not in open_overlay_block

	for expected in (
		"Menus_CloseByName( name );",
		"menu->window.flags &= ~WINDOW_FORCED;",
	):
		assert expected in close_overlay_block

	for expected in (
		"cgScoreboardSelectionMenus[0] = CG_FindBrowserOverlayByName( liveMenuName );",
		"cgScoreboardSelectionMenus[1] = CG_FindBrowserOverlayByName( endMenuName );",
	):
		assert expected in cache_block

	assert "Menu_HandleMouseMove( (menuDef_t *)overlay, x, y );" in handle_mouse_block
	assert "return Menu_ClearFocus( (menuDef_t *)overlay );" in clear_focus_block
	for expected in (
		"!CG_BrowserWidgetEnableShowViaCvar( item, CVAR_ENABLE )",
		"!CG_BrowserWidgetEnableShowViaCvar( item, CVAR_SHOW )",
		"oldFocus = CG_ClearBrowserFocus( item->parent );",
		"CG_BrowserRectContainsPoint( CG_BrowserCorrectedTextRect( item ), x, y )",
		"CG_RunBrowserScript( oldFocus, oldFocus->onFocus );",
		"CG_RunBrowserScript( item, item->onFocus );",
		"cgDC.startLocalSound( *sfx, CHAN_LOCAL_SOUND );",
	):
		assert expected in set_focus_block
	assert "Item_SetMouseOver( (itemDef_t *)widget, focus );" in set_mouse_over_block
	for expected in (
		"!CG_BrowserWidgetEnableShowViaCvar( item, CVAR_ENABLE )",
		"!CG_BrowserWidgetEnableShowViaCvar( item, CVAR_SHOW )",
		"CG_BrowserRectContainsPoint( CG_BrowserCorrectedTextRect( item ), x, y )",
		"CG_RunBrowserScript( item, item->mouseEnterText );",
		"CG_RunBrowserScript( item, item->mouseEnter );",
		"Item_ListBox_MouseEnter( item, x, y );",
	):
		assert expected in mouse_enter_block
	for expected in (
		"CG_RunBrowserScript( item, item->mouseExitText );",
		"CG_RunBrowserScript( item, item->mouseExit );",
		"item->window.flags &= ~( WINDOW_LB_RIGHTARROW | WINDOW_LB_LEFTARROW );",
		"CG_SetBrowserMouseOver( widget, qfalse );",
	):
		assert expected in mouse_leave_block

	assert "Item_SetFocus( (itemDef_t *)widget, x, y )" not in set_focus_block
	assert "Item_MouseEnter( (itemDef_t *)widget, x, y )" not in mouse_enter_block
	assert "Item_MouseLeave( (itemDef_t *)widget )" not in mouse_leave_block

	for expected in (
		"CG_SetBrowserFocus( menu->items[menu->cursorItem], (float)cgDC.cursorx, (float)cgDC.cursory )",
		"CG_BrowserHandleMouseMove( menu, menu->items[menu->cursorItem]->window.rect.x + 1, menu->items[menu->cursorItem]->window.rect.y + 1 );",
	):
		assert expected in prev_cursor_block
		assert expected in next_cursor_block

	for expected in (
		'menu = CG_FindBrowserOverlayByName( "joingame_menu" );',
		'menu = CG_OpenBrowserOverlayByName( "joingame_menu" );',
	):
		assert expected in open_join_block

	assert 'CG_CloseBrowserOverlayByName( "joingame_menu" );' in close_join_block
	assert 'Menus_OpenByName( "joingame_menu" );' not in open_join_block
	assert 'Menus_CloseByName( "joingame_menu" );' not in close_join_block


def test_cgame_browser_runtime_state_and_simple_script_wrappers_restore_retail_owner_slice() -> None:
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")

	rect_block = _block_from_marker(newdraw_source, "static qboolean CG_BrowserRectContainsPoint")
	items_group_block = _block_from_marker(newdraw_source, "static int CG_BrowserItemsMatchingGroup")
	get_matching_block = _block_from_marker(newdraw_source, "static void *CG_BrowserGetMatchingItemByNumber")
	find_widget_block = _block_from_marker(newdraw_source, "static void *CG_FindBrowserWidgetByName")
	run_script_block = _block_from_marker(newdraw_source, "static void CG_RunBrowserScript")
	enable_show_block = _block_from_marker(newdraw_source, "static qboolean CG_BrowserWidgetEnableShowViaCvar")
	show_items_block = _block_from_marker(newdraw_source, "static void CG_ShowBrowserItemsByName")
	script_show_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptShow")
	script_hide_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptHide")
	script_open_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptOpen")
	script_conditional_open_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptConditionalOpen")
	script_close_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptClose")
	script_toggle_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptToggle")
	script_set_focus_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptSetFocus")
	over_active_block = _block_from_marker(newdraw_source, "static qboolean CG_BrowserOverActiveItem")

	assert "return Rect_ContainsPoint( (rectDef_t *)rect, x, y );" in rect_block
	assert "return Menu_ItemsMatchingGroup( (menuDef_t *)overlay, name );" in items_group_block
	assert "return Menu_GetMatchingItemByNumber( (menuDef_t *)overlay, index, name );" in get_matching_block
	assert "return Menu_FindItemByName( (menuDef_t *)overlay, name );" in find_widget_block
	assert "Item_RunScript( (itemDef_t *)widget, script );" in run_script_block
	assert "return Item_EnableShowViaCvar( (itemDef_t *)widget, flag );" in enable_show_block

	for expected in (
		"count = CG_BrowserItemsMatchingGroup( menu, name );",
		"item = CG_BrowserGetMatchingItemByNumber( name, menu, i );",
		"item->window.flags |= WINDOW_VISIBLE;",
		"item->window.flags &= ~WINDOW_VISIBLE;",
		"cgDC.stopCinematic( item->window.cinematic );",
	):
		assert expected in show_items_block

	assert "CG_ShowBrowserItemsByName( name, item->parent, qtrue );" in script_show_block
	assert "CG_ShowBrowserItemsByName( name, item->parent, qfalse );" in script_hide_block
	assert "CG_OpenBrowserOverlayByName( name );" in script_open_block

	for expected in (
		"value = trap_Cvar_VariableValue( cvar );",
		"CG_OpenBrowserOverlayByName( name2 );",
		"CG_OpenBrowserOverlayByName( name1 );",
	):
		assert expected in script_conditional_open_block

	assert "CG_CloseBrowserOverlayByName( name );" in script_close_block

	for expected in (
		"menu = CG_FindBrowserOverlayByName( name );",
		"if ( menu->window.flags & WINDOW_VISIBLE ) {",
		"CG_CloseBrowserOverlayByName( name );",
		"CG_OpenBrowserOverlayByName( name );",
	):
		assert expected in script_toggle_block

	for expected in (
		"focusItem = CG_FindBrowserWidgetByName( item->parent, name );",
		"CG_ClearBrowserFocus( item->parent );",
		"CG_RunBrowserScript( focusItem, focusItem->onFocus );",
		"cgDC.startLocalSound( cgDC.Assets.itemFocusSound, CHAN_LOCAL_SOUND );",
	):
		assert expected in script_set_focus_block

	for expected in (
		"CG_BrowserRectContainsPoint( &menu->window.rect, x, y )",
		"CG_BrowserRectContainsPoint( &item->window.rect, x, y )",
		"CG_BrowserRectContainsPoint( CG_BrowserCorrectedTextRect( item ), x, y )",
	):
		assert expected in over_active_block


def test_cgame_browser_runtime_surface_restores_overlay_draw_and_capture_owners() -> None:
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	draw_source = CG_DRAW.read_text(encoding="utf-8")
	screen_source = CG_SCREEN.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")

	capture_block = _block_from_marker(newdraw_source, "static void *CG_BrowserDisplayCaptureItem")
	alloc_block = _block_from_marker(newdraw_source, "static void CG_AllocBrowserWidgetState")
	frame_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserWidgetFrame")
	widget_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserWidget")
	overlay_tree_block = _block_from_marker(newdraw_source, "void CG_DrawBrowserOverlayTree")
	overlays_block = _block_from_marker(newdraw_source, "void CG_DrawBrowserOverlays")
	oob_block = _block_from_marker(newdraw_source, "static void CG_BrowserHandleOOBClick")
	handle_key_block = _block_from_marker(newdraw_source, "static void CG_BrowserHandleKey")
	display_handle_block = _block_from_marker(newdraw_source, "static void CG_BrowserDisplayHandleKey")
	cached_menu_block = _block_from_marker(draw_source, "static qboolean CG_DrawCachedOverlayMenu")
	scoreboard_block = _block_from_marker(draw_source, "static qboolean CG_DrawScoreboard")
	stats_block = _block_from_marker(draw_source, "static qboolean CG_DrawStatsMenu")
	draw_2d_block = _block_from_marker(draw_source, "static void CG_Draw2D")
	join_menu_block = _block_from_marker(screen_source, "void CG_DrawJoinGameMenu( void )")

	for expected in (
		"void CG_DrawBrowserOverlayTree( void *overlay, qboolean forcePaint );",
		"void CG_DrawBrowserOverlays( void );",
	):
		assert expected in local_source

	assert "return Display_CaptureItem( x, y );" in capture_block
	assert "Item_ValidateTypeData( (itemDef_t *)widget );" in alloc_block
	assert "Window_Paint( window, fadeAmount, fadeClamp, fadeCycle );" in frame_block
	assert "CG_AllocBrowserWidgetState( item );" in widget_block
	assert "Item_Paint( item );" in widget_block
	assert "switch ( item->type ) {" not in widget_block
	assert "static void CG_NormalizeBrowserFullscreenBackgroundRect( rectDef_t *rect ) {" in newdraw_source
	assert "Menus_HandleOOBClick( (menuDef_t *)overlay, key, down );" in oob_block

	for expected in (
		"if ( menu->window.ownerDrawFlags2 && cgDC.ownerDrawVisible &&",
		"!cgDC.ownerDrawVisible( menu->window.ownerDrawFlags2 ) ) {",
		"CG_UpdateBrowserPresetLists( menu );",
		"CG_NormalizeBrowserFullscreenBackgroundRect( &backgroundRect );",
		"CG_DrawBrowserWidgetFrame( &menu->window, menu->fadeAmount, menu->fadeClamp, menu->fadeCycle );",
		"CG_DrawBrowserWidget( menu->items[i] );",
		"cgDC.setAdjustFrom640Mode( WIDESCREEN_STRETCH );",
	):
		assert expected in overlay_tree_block

	assert "Menu_PaintAll();" in overlays_block
	assert "CG_BrowserHandleOOBClick( menu, key, down );" in handle_key_block
	assert "overlay = CG_BrowserDisplayCaptureItem( x, y );" in display_handle_block
	assert "overlay = CG_GetFocusedBrowserOverlay();" in display_handle_block

	assert "CG_DrawBrowserOverlayTree( menu, qtrue );" in cached_menu_block
	assert "Menu_Paint( menu, qtrue );" not in cached_menu_block

	for expected in (
		"menuScoreboard = CG_FindBrowserOverlayByName( menuName );",
		"menuScoreboard = CG_FindBrowserOverlayByName( fallback );",
		"CG_DrawBrowserOverlayTree( menuScoreboard, qtrue );",
	):
		assert expected in scoreboard_block

	assert 'menuStats = CG_FindBrowserOverlayByName( "stats_menu" );' in stats_block
	assert "CG_DrawBrowserOverlayTree( menuStats, qtrue );" in stats_block
	assert "CG_DrawBrowserOverlays();" in draw_2d_block
	assert "Menu_PaintAll();" not in draw_2d_block

	assert "CG_DrawBrowserOverlayTree( menu, qtrue );" in join_menu_block
	assert "Menu_Paint( menu, qtrue );" not in join_menu_block


def test_cgame_browser_leaf_wrappers_restore_remaining_retail_owner_slice() -> None:
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	main_source = CG_MAIN.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")

	list_max_block = _block_from_marker(newdraw_source, "static int CG_BrowserListMaxScroll")
	list_thumb_block = _block_from_marker(newdraw_source, "static int CG_BrowserListThumbPosition")
	list_thumb_draw_block = _block_from_marker(newdraw_source, "static int CG_BrowserListThumbDrawPosition")
	list_over_block = _block_from_marker(newdraw_source, "static int CG_BrowserListOverLB")
	textfield_key_block = _block_from_marker(newdraw_source, "static qboolean CG_BrowserTextFieldHandleKey")
	script_fade_in_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptFadeIn")
	script_fade_out_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptFadeOut")
	script_set_background_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptSetBackground")
	script_set_color_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptSetColor")
	script_set_team_color_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptSetTeamColor")
	script_set_item_color_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptSetItemColor")
	transition_items_block = _block_from_marker(newdraw_source, "static void CG_TransitionBrowserItemsByName")
	script_transition_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptTransition")
	orbit_items_block = _block_from_marker(newdraw_source, "static void CG_OrbitBrowserItemsByName")
	script_orbit_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptOrbit")
	script_activate_advert_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptActivateAdvert")
	script_set_model_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptSetPlayerModel")
	script_set_head_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptSetPlayerHead")
	script_set_cvar_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptSetCvar")
	script_exec_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptExec")
	script_play_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptPlay( void *widget, char **args )")
	script_play_looped_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptPlayLooped( void *widget, char **args )")
	multi_find_block = _block_from_marker(newdraw_source, "static int CG_BrowserMultiFindCvarByValue")
	multi_setting_block = _block_from_marker(newdraw_source, "static const char *CG_BrowserMultiSetting")
	preset_setting_block = _block_from_marker(newdraw_source, "static const char *CG_BrowserPresetListSetting")
	preset_find_block = _block_from_marker(newdraw_source, "static int CG_BrowserPresetListFindCvarByValue")
	yesno_draw_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserYesNoControl")
	multi_draw_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserMultiControl")
	preset_draw_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserPresetList")
	controls_get_block = _block_from_marker(newdraw_source, "static void CG_BrowserControlsGetConfig")
	controls_set_block = _block_from_marker(newdraw_source, "static void CG_BrowserControlsSetConfig")
	binding_id_block = _block_from_marker(newdraw_source, "static int CG_BrowserBindingIDFromName")
	binding_from_block = _block_from_marker(newdraw_source, "static void CG_BrowserBindingFromName")
	bind_draw_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserBindControl")
	bind_key_block = _block_from_marker(newdraw_source, "static qboolean CG_BrowserBindHandleKey")
	slider_thumb_block = _block_from_marker(newdraw_source, "static float CG_BrowserSliderThumbPosition")
	text_extents_block = _block_from_marker(newdraw_source, "static void CG_BrowserSetTextExtents")
	slider_draw_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserSliderControl")
	slider_color_draw_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserSliderColorControl")
	text_color_block = _block_from_marker(newdraw_source, "static void CG_BrowserTextColor")
	auto_text_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserAutoWrappedText")
	wrapped_text_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserWrappedText")
	text_draw_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserText( void *widget )")
	editfield_draw_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserEditFieldControl")
	model_draw_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserModelPreview")
	list_draw_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserListWidget")
	textfield_draw_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserTextField")
	close_cinematics_block = _block_from_marker(newdraw_source, "static void CG_CloseBrowserCinematics")
	activate_overlay_block = _block_from_marker(newdraw_source, "void CG_ActivateBrowserOverlay")
	multi_key_block = _block_from_marker(newdraw_source, "static qboolean CG_BrowserMultiHandleKey")
	preset_key_block = _block_from_marker(newdraw_source, "static qboolean CG_BrowserPresetListHandleKey")
	list_repeat_block = _block_from_marker(newdraw_source, "static void CG_BrowserListRepeatScroll")
	list_drag_block = _block_from_marker(newdraw_source, "static void CG_BrowserListDragThumb")
	slider_apply_block = _block_from_marker(newdraw_source, "static void CG_BrowserSliderApplyFromCursor")
	start_capture_block = _block_from_marker(newdraw_source, "static void CG_BrowserStartCapture")
	slider_key_block = _block_from_marker(newdraw_source, "static qboolean CG_BrowserSliderHandleKey")
	slider_over_block = _block_from_marker(newdraw_source, "static int CG_BrowserSliderOverControl")
	widget_key_block = _block_from_marker(newdraw_source, "static qboolean CG_BrowserWidgetHandleKey")
	widget_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserWidget")
	open_overlay_block = _block_from_marker(main_source, "void *CG_OpenBrowserOverlayByName")

	for expected in (
		"void CG_UpdateBrowserPresetLists( void *overlay );",
		"void CG_UpdateBrowserWidgetPositions( void *overlay );",
		"void CG_ActivateBrowserOverlay( void *overlay );",
	):
		assert expected in local_source

	assert "return Item_ListBox_MaxScroll( (itemDef_t *)widget );" in list_max_block
	assert "return Item_ListBox_ThumbPosition( (itemDef_t *)widget );" in list_thumb_block
	assert "return Item_ListBox_ThumbDrawPosition( (itemDef_t *)widget );" in list_thumb_draw_block
	assert "return Item_ListBox_OverLB( (itemDef_t *)widget, x, y );" in list_over_block
	assert "return Item_TextField_HandleKey( (itemDef_t *)widget, key );" in textfield_key_block

	assert "Menu_FadeItemByName( (menuDef_t *)item->parent, name, qfalse );" in script_fade_in_block
	assert "Menu_FadeItemByName( (menuDef_t *)item->parent, name, qtrue );" in script_fade_out_block
	assert "Script_SetBackground( (itemDef_t *)widget, args );" in script_set_background_block
	assert "Script_SetColor( (itemDef_t *)widget, args );" in script_set_color_block
	assert "Script_SetTeamColor( (itemDef_t *)widget, args );" in script_set_team_color_block
	assert "Script_SetItemColor( (itemDef_t *)widget, args );" in script_set_item_color_block
	assert "Menu_TransitionItemByName( (menuDef_t *)overlay, name, rectFrom, rectTo, time, amount );" in transition_items_block
	assert "CG_TransitionBrowserItemsByName( item->parent, name, rectFrom, rectTo, time, amount );" in script_transition_block
	assert "Menu_OrbitItemByName( (menuDef_t *)overlay, name, x, y, cx, cy, time );" in orbit_items_block
	assert "CG_OrbitBrowserItemsByName( item->parent, name, x, y, cx, cy, time );" in script_orbit_block
	assert "cgDC.activateAdvert( atoi( cellIdToken ) );" in script_activate_advert_block
	assert "item->window.flags &= ~WINDOW_HASFOCUS;" in script_activate_advert_block
	assert "Script_SetPlayerModel( (itemDef_t *)widget, args );" in script_set_model_block
	assert "Script_SetPlayerHead( (itemDef_t *)widget, args );" in script_set_head_block
	assert "Script_SetCvar( (itemDef_t *)widget, args );" in script_set_cvar_block
	assert "Script_Exec( (itemDef_t *)widget, args );" in script_exec_block
	assert "Script_Play( (itemDef_t *)widget, args );" in script_play_block
	assert "Script_playLooped( (itemDef_t *)widget, args );" in script_play_looped_block

	assert "return Item_Multi_FindCvarByValue( (itemDef_t *)widget );" in multi_find_block
	assert "return Item_Multi_Setting( (itemDef_t *)widget );" in multi_setting_block
	assert "return Item_PresetList_Setting( (itemDef_t *)widget );" in preset_setting_block
	assert "return Item_PresetList_FindCvarByValue( (itemDef_t *)widget );" in preset_find_block
	assert "Item_YesNo_Paint( (itemDef_t *)widget );" in yesno_draw_block
	assert "Item_Multi_Paint( (itemDef_t *)widget );" in multi_draw_block
	assert "Item_PresetList_Paint( (itemDef_t *)widget );" in preset_draw_block
	assert "Controls_GetConfig();" in controls_get_block
	assert "Controls_SetConfig( restart );" in controls_set_block
	assert "return BindingIDFromName( name );" in binding_id_block
	assert "BindingFromName( name );" in binding_from_block
	assert "Item_Bind_Paint( (itemDef_t *)widget );" in bind_draw_block
	assert "return Item_Bind_HandleKey( (itemDef_t *)widget, key, down );" in bind_key_block
	assert "return Item_Slider_ThumbPosition( (itemDef_t *)widget );" in slider_thumb_block
	assert "Item_SetTextExtents( (itemDef_t *)widget, width, height, text );" in text_extents_block
	assert "Item_Slider_Paint( (itemDef_t *)widget );" in slider_draw_block
	assert "Item_SliderColor_Paint( (itemDef_t *)widget );" in slider_color_draw_block
	assert "Item_TextColor( (itemDef_t *)widget, newColor );" in text_color_block
	assert "Item_Text_AutoWrapped_Paint( (itemDef_t *)widget );" in auto_text_block
	assert "Item_Text_Wrapped_Paint( (itemDef_t *)widget );" in wrapped_text_block
	assert "Item_Text_Paint( item );" in text_draw_block
	assert "Item_TextField_Paint( (itemDef_t *)widget );" in editfield_draw_block
	assert "Item_Model_Paint( (itemDef_t *)widget );" in model_draw_block
	assert "Item_ListBox_Paint( (itemDef_t *)widget );" in list_draw_block
	assert "CG_DrawBrowserEditFieldControl( widget );" in textfield_draw_block

	assert "CG_CloseBrowserMenuCinematics( &Menus[i] );" in close_cinematics_block
	assert "Menus_Activate( (menuDef_t *)overlay );" in activate_overlay_block
	assert "return Item_Multi_HandleKey( (itemDef_t *)widget, key );" in multi_key_block
	assert "return Item_PresetList_HandleKey( (itemDef_t *)widget, key );" in preset_key_block
	assert "Item_ListBox_HandleKey( (itemDef_t *)widget, key, qtrue, qfalse );" in list_repeat_block
	assert "listPtr->startPos = pos;" in list_drag_block
	assert "cgDC.setCVar( item->cvar, buffer );" in slider_apply_block
	assert "Item_StartCapture( (itemDef_t *)widget, key );" in start_capture_block
	assert "return Item_Slider_HandleKey( (itemDef_t *)widget, key, down );" in slider_key_block
	assert "return Item_Slider_OverSlider( (itemDef_t *)widget, x, y );" in slider_over_block

	for expected in (
		"return Item_ListBox_HandleKey( item, key, down, qfalse );",
		"return Item_YesNo_HandleKey( item, key );",
		"return CG_BrowserMultiHandleKey( item, key );",
		"return CG_BrowserBindHandleKey( item, key, down );",
		"return CG_BrowserSliderHandleKey( item, key, down );",
		"return CG_BrowserPresetListHandleKey( item, key );",
	):
		assert expected in widget_key_block

	assert "Item_Paint( item );" in widget_block
	assert "switch ( item->type ) {" not in widget_block

	for expected in (
		"CG_UpdateBrowserWidgetPositions( menu );",
		"CG_UpdateBrowserPresetLists( menu );",
		"CG_ActivateBrowserOverlay( menu );",
	):
		assert expected in open_overlay_block

	assert "Menus_OpenByName( name );" not in open_overlay_block


def test_cgame_menu_parser_and_score_selection_restore_retail_parser_and_cursor_seam() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	parse_menu_start = source.index("void CG_ParseMenu(const char *menuFile)")
	load_menu_start = source.index("qboolean CG_Load_Menu(char **p)")
	parse_menu_block = source[parse_menu_start:load_menu_start]
	score_block = _block_from_marker(source, "void CG_SetScoreSelection")
	selection_block = _block_from_marker(source, "static void CG_FeederSelection")

	for expected in (
		'handle = trap_PC_LoadSource("ui/testhud.menu");',
		'if (Q_stricmp(token.string, "assetGlobalDef") == 0) {',
		"if (CG_Asset_Parse(handle)) {",
		'if (Q_stricmp(token.string, "menudef") == 0) {',
		"menu = &Menus[menuCount];",
		"CG_InitBrowserOverlay( menu );",
		"if ( CG_ParseBrowserMenu( handle, menu ) ) {",
		"Menu_PostParse( menu );",
		"menuCount++;",
	):
		assert expected in parse_menu_block

	assert "Menu_New(handle);" not in parse_menu_block

	for expected in (
		"token = COM_ParseExt(p, qtrue);",
		"if (token[0] != '{') {",
		'if (Q_stricmp(token, "}") == 0) {',
		"CG_ParseMenu(token);",
	):
		assert expected in source

	for expected in (
		"if ( cg.selectedScore < 0 || cg.selectedScore >= cg.numScores ) {",
		"CG_SetBrowserFeederSelection( menu, feeder, cg.selectedScore );",
		"CG_SetBrowserFeederSelection( menu, FEEDER_SCOREBOARD, cg.selectedScore );",
	):
		assert expected in score_block

	for expected in (
		"if ( index == -1 ) {",
		"if ( cg.snap->ps.pm_type == PM_INTERMISSION ) {",
		"selectedClient = cg.scores[cg.selectedScore].client;",
		"if ( cg.scores[i].client == selectedClient ) {",
		"CG_SyncScoreboardTeamListSelection( team, selectedIndex );",
	):
		assert expected in selection_block


def test_cgame_serverinfo_restores_retail_map_alias_normalizer() -> None:
	source = CG_SERVERCMDS.read_text(encoding="utf-8")
	normalize_block = _block_from_marker(source, "static const char *CG_NormalizeMapFilename")
	parse_block = _block_from_marker(source, "void CG_ParseServerinfo")

	for expected in (
		'{ "qzca1", "asylum" },',
		'{ "qzdm6", "campgrounds" },',
		'{ "qztourney7", "furiousheights" },',
		'{ "ztntourney1", "bloodrun" }',
	):
		assert expected in source

	for expected in (
		'if ( !Q_stricmp( mapname, cg_retailMapAliases[i].legacyName ) ) {',
		"return cg_retailMapAliases[i].retailName;",
	):
		assert expected in normalize_block

	assert 'mapname = CG_NormalizeMapFilename( Info_ValueForKey( info, "mapname" ) );' in parse_block
	assert 'Com_sprintf( cgs.mapname, sizeof( cgs.mapname ), "maps/%s.bsp", mapname );' in parse_block


def test_cgame_scoreboard_feeder_stats_restore_retail_leaf_split() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	count_block = _block_from_marker(source, "static int CG_FeederCount")
	text_block = _block_from_marker(source, "static const char *CG_FeederItemText")
	image_block = _block_from_marker(source, "static qhandle_t CG_FeederItemImage")
	scoreboard_block = _block_from_marker(source, "static const char *CG_FeederItemTextScoreboard")
	race_block = _block_from_marker(source, "static const char *CG_FeederItemTextRaceScoreboard")
	tdm_block = _block_from_marker(source, "static const char *CG_FeederItemTextTDMFreezeStats")
	ca_block = _block_from_marker(source, "static const char *CG_FeederItemTextClanArenaStats")
	ctf_block = _block_from_marker(source, "static const char *CG_FeederItemTextCTFFamilyStats")

	for expected in (
		"feederID == FEEDER_REDTEAM_STATS",
		"feederID == FEEDER_BLUETEAM_STATS",
		"CG_IsScoreboardFeeder( feederID )",
	):
		assert expected in count_block

	for expected in (
		"(void)feederID;",
		"(void)index;",
		"return 0;",
	):
		assert expected in image_block

	for expected in (
		"if ( CG_IsTeamStatsFeeder( feederID ) ) {",
		"return CG_FeederItemTextTDMFreezeStats( team, index, column, handle );",
		"return CG_FeederItemTextClanArenaStats( team, index, column, handle );",
		"return CG_FeederItemTextCTFFamilyStats( team, index, column, handle );",
		"return CG_FeederItemTextRaceScoreboard( index, column, handle );",
		"return CG_FeederItemTextScoreboard( index, column, handle );",
	):
		assert expected in text_block

	assert "return CG_FeederItemTextBaseColumns( &row, column, handle );" in scoreboard_block
	assert "return CG_FeederItemTextScoreboard( index, column, handle );" in race_block

	for expected in (
		"stats = &cg.tdmStats[row.scoreIndex];",
		"net = kills + stats->values[8] - stats->values[9] - stats->values[10];",
		'return va( "%i%%", row.scoreRow->accuracy );',
		'return va( "%i", stats->values[5] );',
		'return va( "%i", stats->values[0] );',
	):
		assert expected in tdm_block

	for expected in (
		"stats = &cg.clanArenaStats[row.scoreIndex];",
		'return va( "%i", stats->damageGiven );',
		'return va( "%i", stats->damageReceived );',
		'"^3%i ^7%i%%"',
		"stats->weaponFrags[WP_HEAVY_MACHINEGUN]",
	):
		assert expected in ca_block

	for expected in (
		"stats = &cg.ctfStats[row.scoreIndex];",
		"net = row.scoreRow->kills - row.scoreRow->deaths - stats->values[11];",
		'return va( "%i", stats->values[10] );',
		'return va( "%i", stats->values[8] );',
		'return va( "%i", stats->values[0] );',
	):
		assert expected in ctf_block


def test_cgame_team_list_feeders_restore_retail_family_split() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	text_block = _block_from_marker(source, "static const char *CG_FeederItemText")
	lead_block = _block_from_marker(source, "static const char *CG_FeederItemTextTeamListLeadColumns")
	fallback_block = _block_from_marker(source, "static const char *CG_FeederItemTextFallbackTeamList")
	tdm_block = _block_from_marker(source, "static const char *CG_FeederItemTextTDMFreezeTeamList")
	ca_block = _block_from_marker(source, "static const char *CG_FeederItemTextClanArenaTeamList")
	ctf_block = _block_from_marker(source, "static const char *CG_FeederItemTextCTFFamilyTeamList")

	for expected in (
		"return CG_FeederItemTextTDMFreezeTeamList( team, index, column, handle );",
		"return CG_FeederItemTextClanArenaTeamList( team, index, column, handle );",
		"return CG_FeederItemTextCTFFamilyTeamList( team, index, column, handle );",
		"return CG_FeederItemTextFallbackTeamList( team, index, column, handle );",
	):
		assert expected in text_block

	for expected in (
		"row->scoreRow->bestWeapon > WP_NONE",
		"cg_weapons[ row->scoreRow->bestWeapon ].weaponIcon",
		"row->scoreRow->activePlayer ) {",
		'return "*";',
		"return row->info->name;",
	):
		assert expected in lead_block

	for expected in (
		"return CG_FeederItemTextTeamListLeadColumns( &row, column, handle );",
		'return va( "%i", row.scoreRow->score );',
		'if ( row.scoreRow->ping == -1 ) {',
		'return va( "%4i", row.scoreRow->ping );',
	):
		assert expected in fallback_block

	for expected in (
		"stats = &cg.tdmStats[row.scoreIndex];",
		"if ( cgs.gametype == GT_FREEZE ) {",
		'return va( "%i/%i", row.scoreRow->kills, row.scoreRow->deaths );',
		'return va( "%i", row.scoreRow->damage );',
		'return va( "%i%%", row.scoreRow->accuracy );',
	):
		assert expected in tdm_block

	for expected in (
		'return va( "%i/%i", row.scoreRow->kills, row.scoreRow->deaths );',
		'return va( "%i", row.scoreRow->damage );',
		"cg_weapons[ row.scoreRow->bestWeapon ].weaponIcon",
		'return va( "%i%%", row.scoreRow->accuracy );',
	):
		assert expected in ca_block

	for expected in (
		'return va( "%i/%i", row.scoreRow->kills, row.scoreRow->deaths );',
		'return va( "%i", row.scoreRow->captures );',
		'return va( "%i", row.scoreRow->assistCount );',
		'return va( "%i", row.scoreRow->defendCount );',
	):
		assert expected in ctf_block


def test_cgame_scoreboard_selection_callbacks_restore_cached_team_list_menu_seam() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	menu_name_block = _block_from_marker(source, "static const char *CG_GetScoreboardSelectionMenuName")
	cache_block = _block_from_marker(source, "static void CG_CacheScoreboardSelectionMenus")
	sync_block = _block_from_marker(source, "static void CG_SyncScoreboardTeamListSelection")
	image_block = _block_from_marker(source, "static qhandle_t CG_FeederItemImage")
	selection_block = _block_from_marker(source, "static void CG_FeederSelection")
	load_hud_block = _block_from_marker(source, "void CG_LoadHudMenu()")

	for expected in (
		'return "score_menu_ffa";',
		'return "endscore_menu_ffa";',
		'return "teamscore_menu_tdm";',
		'return "endteamscore_menu_tdm";',
		'return "teamscore_menu_har";',
		'return "endteamscore_menu_har";',
		'return "endscoreteam";',
		'return "endscorenoteam";',
	):
		assert expected in menu_name_block

	for expected in (
		"cgScoreboardSelectionMenus[0] = CG_FindBrowserOverlayByName( liveMenuName );",
		"cgScoreboardSelectionMenus[1] = CG_FindBrowserOverlayByName( endMenuName );",
	):
		assert expected in cache_block

	assert "Menus_FindByName( liveMenuName );" not in cache_block
	assert "Menus_FindByName( endMenuName );" not in cache_block

	for expected in (
		'selectedItemName = ( team == TEAM_RED ) ? "playerlistRED" : "playerlistBLUE";',
		'clearedItemName = ( team == TEAM_RED ) ? "playerlistBLUE" : "playerlistRED";',
		"CG_SetScoreboardTeamListCursor( cgScoreboardSelectionMenus[i], selectedItemName, index );",
		"CG_SetScoreboardTeamListCursor( cgScoreboardSelectionMenus[i], clearedItemName, -1 );",
	):
		assert expected in sync_block

	for expected in (
		"(void)feederID;",
		"(void)index;",
		"return 0;",
	):
		assert expected in image_block

	for expected in (
		"selectedIndex = index;",
		"CG_CacheScoreboardSelectionMenus();",
		"CG_SyncScoreboardTeamListSelection( team, selectedIndex );",
	):
		assert expected in selection_block

	assert "CG_CacheScoreboardSelectionMenus();" in load_hud_block


def test_cgame_gameinfo_cvars_restore_retail_training_and_gametype_text() -> None:
	source = CG_SERVERCMDS.read_text(encoding="utf-8")
	game_info_block = _block_from_marker(source, "static void CG_SetGameInfoCvars")
	parse_block = _block_from_marker(source, "void CG_ParseServerinfo( void )")

	for expected in (
		"static const char *const cg_retailBlankGameInfoLines[6] = {",
		"static const char *const cg_retailTrainingGameInfoLines[6] = {",
		'"Welcome to QUAKE LIVE training"',
		'"A trainer named \'Crash\' is waiting to give you a quick introduction"',
		'"to the game. Follow \'Crash\' through a tour of the warm-up arena, then"',
		'"compete against her in a free-for-all deathmatch game."',
		'"Click \'Start Training\' to begin."',
		"static const char *const cg_retailGameInfoLines[GT_MAX_GAME_TYPE][6] = {",
		'"This is a 1 vs 1 Duel game"',
		'"If the time limit is hit and there is a tie, the match extends"',
		'"into overtime."',
		'"This is a Team Deathmatch game"',
		'"This is an Attack and Defend game"',
		'"Frag enemies and they will respawn onto your team."',
	):
		assert expected in source

	for expected in (
		'info = CG_ConfigString( CS_SERVERINFO );',
		'trainingValue = Info_ValueForKey( info, "g_training" );',
		"gameInfo = cg_retailBlankGameInfoLines;",
		"gameInfo = cg_retailTrainingGameInfoLines;",
		"gameInfo = cg_retailGameInfoLines[cgs.gametype];",
		'trap_Cvar_Set( "cg_gameInfo1", gameInfo[0] );',
		'trap_Cvar_Set( "cg_gameInfo2", gameInfo[1] );',
		'trap_Cvar_Set( "cg_gameInfo3", gameInfo[2] );',
		'trap_Cvar_Set( "cg_gameInfo4", gameInfo[3] );',
		'trap_Cvar_Set( "cg_gameInfo5", gameInfo[4] );',
		'trap_Cvar_Set( "cg_gameInfo6", gameInfo[5] );',
	):
		assert expected in game_info_block

	assert "CG_SetGameInfoCvars();" in parse_block
	assert parse_block.index("CG_SetGameInfoCvars();") > parse_block.index('cgs.timelimit = atoi( Info_ValueForKey( info, "timelimit" ) );')
	assert parse_block.index("CG_SetGameInfoCvars();") < parse_block.index('voteFlagsValue = Info_ValueForKey( info, "g_voteFlags" );')


def test_display_context_uses_named_cvar_string_and_native_chat_helpers() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	display_block = _block_from_marker(source, "static void CG_InitDisplayContext")
	cvar_string_block = _block_from_marker(source, "void CG_Cvar_GetString")
	compact_hud_block = _block_from_marker(source, "static qboolean CG_UseMatchSummaryChatLayout")
	physics_block = _block_from_marker(source, "static int CG_GetPhysicsTime")
	chat_y_block = _block_from_marker(source, "static float CG_GetChatFieldY")
	chat_width_block = _block_from_marker(source, "static float CG_GetChatFieldPixelWidth")
	chat_chars_block = _block_from_marker(source, "static int CG_GetChatFieldWidthInChars")

	assert "cgDC.getCVarString = &CG_Cvar_GetString;" in display_block
	assert "trap_Cvar_VariableStringBuffer( cvar, buffer, bufsize );" in cvar_string_block
	assert "cg.snap->ps.pm_type == PM_INTERMISSION" in compact_hud_block
	assert "return qtrue;" in compact_hud_block
	assert "return qfalse;" in compact_hud_block
	assert "cg_useLegacyHud" not in compact_hud_block
	assert "return cg.physicsTime;" in physics_block
	assert "return CG_UseMatchSummaryChatLayout() ? 455.0f : 413.0f;" in chat_y_block
	assert "return CG_UseMatchSummaryChatLayout() ? 300.0f : 640.0f;" in chat_width_block
	assert "return CG_UseMatchSummaryChatLayout() ? 30 : 73;" in chat_chars_block


def test_cgame_init_splits_display_context_bootstrap_before_collision_map() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	display_block = _block_from_marker(source, "static void CG_InitDisplayContext")
	load_hud_block = _block_from_marker(source, "void CG_LoadHudMenu()")
	asset_block = _block_from_marker(source, "void CG_AssetCache()")
	init_block = _block_from_marker(source, "void CG_Init( int serverMessageNum, int serverCommandSequence, int clientNum )")

	for expected in (
		"cgDC.registerShaderNoMip = &trap_R_RegisterShaderNoMip;",
		"cgDC.setColor = &trap_R_SetColor;",
		"cgDC.drawHandlePic = &CG_DrawPic;",
		"cgDC.drawTextExt = &CG_Text_PaintExt;",
		"cgDC.textWidthExt = &CG_Text_WidthExt;",
		"cgDC.textHeightExt = &CG_Text_HeightExt;",
		"cgDC.fillRect = &CG_FillRect;",
		"cgDC.drawRect = &CG_DrawRect;",
		"cgDC.drawSides = &CG_DrawSides;",
		"cgDC.drawTopBottom = &CG_DrawTopBottom;",
		"cgDC.registerModel = &trap_R_RegisterModel;",
		"cgDC.modelBounds = &trap_R_ModelBounds;",
		"cgDC.clearScene = &trap_R_ClearScene;",
		"cgDC.addRefEntityToScene = &trap_R_AddRefEntityToScene;",
		"cgDC.renderScene = &trap_R_RenderScene;",
		"cgDC.registerFont = &trap_R_RegisterFont;",
		"cgDC.registerSound = &trap_S_RegisterSound;",
		"cgDC.startBackgroundTrack = &trap_S_StartBackgroundTrack;",
		"cgDC.stopBackgroundTrack = &trap_S_StopBackgroundTrack;",
		"cgDC.drawTextWithCursorExt = &CG_Text_PaintWithCursorExt;",
		"cgDC.adjustFrom640 = &CG_AdjustFrom640;",
		"cgDC.setAdjustFrom640Mode = &CG_SetAdjustFrom640Mode;",
		"cgDC.bias = cgs.screenXBias;",
		"Init_Display( &cgDC );",
	):
		assert expected in display_block

	assert "Init_Display(" not in load_hud_block
	assert "CG_RegisterHudFonts();" in asset_block

	collision_index = init_block.index('CG_LoadingString( "collision map" );')
	assert init_block.index("CG_InitDisplayContext();") < collision_index
	assert init_block.index("CG_RegisterHudFonts();") < collision_index

	for expected in (
		"cgs.screenXScale = cgs.glconfig.vidWidth / 640.0;",
		"cgs.screenYScale = cgs.glconfig.vidHeight / 480.0;",
		"cgs.screenXBias = 0.5f * ( (float)cgs.glconfig.vidWidth - ( (float)cgs.glconfig.vidHeight * ( (float)SCREEN_WIDTH / (float)SCREEN_HEIGHT ) ) );",
		"cgs.screenXBias = 0.0f;",
	):
		assert expected in init_block


def test_cgame_host_text_helpers_honor_retail_font_buckets() -> None:
	draw_source = CG_DRAW.read_text(encoding="utf-8")
	main_source = CG_MAIN.read_text(encoding="utf-8")
	select_block = _block_from_marker(draw_source, "int CG_SelectTextFontHandle")
	width_block = _block_from_marker(draw_source, "int CG_Text_WidthExt")
	height_block = _block_from_marker(draw_source, "int CG_Text_HeightExt")
	paint_block = _block_from_marker(draw_source, "void CG_Text_PaintExt")
	cursor_ext_block = _block_from_marker(main_source, "static void CG_Text_PaintWithCursorExt")
	cursor_block = _block_from_marker(main_source, "void CG_Text_PaintWithCursor")

	for expected in (
		"if ( fontIndex != ITEM_FONT_INHERIT ) {",
		"case FONT_SANS:",
		"return FONT_SANS;",
		"case FONT_MONO:",
		"return FONT_MONO;",
		"case FONT_DEFAULT:",
		"return FONT_DEFAULT;",
		"if ( scale <= cg_smallFont.value ) {",
	):
		assert expected in select_block

	assert "CG_GetHostTextMetrics( text, scale, limit, fontIndex, &width, NULL );" in width_block
	assert "CG_GetHostTextMetrics( text, scale, limit, fontIndex, NULL, &height );" in height_block
	assert "CG_DrawHostTextSpan( x, y, scale, color, drawText, fontIndex, style, qfalse );" in paint_block
	assert "CG_Text_PaintExt( x, y, scale, color, text, 0.0f, limit, style, fontIndex );" in cursor_ext_block
	assert "CG_Text_PaintWithCursorExt( x, y, scale, color, text, cursorPos, cursor, limit, style, ITEM_FONT_INHERIT );" in cursor_block

	for expected in (
		"return CG_Text_WidthExt( text, scale, limit, ITEM_FONT_INHERIT );",
		"return CG_Text_HeightExt( text, scale, limit, ITEM_FONT_INHERIT );",
		"CG_Text_PaintExt( x, y, scale, color, text, adjust, limit, style, ITEM_FONT_INHERIT );",
	):
		assert expected in draw_source


def test_cgame_text_paint_limit_reuses_shared_font_selector() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	block = _block_from_marker(source, "static void CG_Text_Paint_Limit")

	assert "fontHandle = CG_SelectTextFontHandle( scale, ITEM_FONT_INHERIT );" in block
	assert "fontHandle = ( scale <= cg_smallFont.value ) ? FONT_SANS : FONT_DEFAULT;" not in block


def test_cgame_host_text_shadow_offsets_stay_in_virtual_space() -> None:
	draw_source = CG_DRAW.read_text(encoding="utf-8")
	span_block = _block_from_marker(draw_source, "static void CG_DrawHostTextSpan")

	for expected in (
		"hostScale = scale * QL_FONT_HOST_POINT_SIZE * yScale;",
		"shadowOffset = ( style == ITEM_TEXTSTYLE_SHADOWED ) ? 1.0f : 2.0f;",
		"shadowX = x + shadowOffset;",
		"shadowY = y + shadowOffset;",
		"CG_AdjustFrom640( &shadowX, &shadowY, NULL, NULL );",
		"trap_QL_DrawScaledText( (int)shadowX, (int)shadowY, text, fontHandle, hostScale, 0, NULL, qtrue );",
		"trap_QL_DrawScaledText( (int)screenX, (int)screenY, text, fontHandle, hostScale, 0, NULL, forceColor );",
	):
		assert expected in span_block


def test_cgame_advert_bridge_lifecycle_matches_retail_init_and_shutdown_order() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	init_block = _block_from_marker(source, "void CG_Init( int serverMessageNum, int serverCommandSequence, int clientNum )")
	shutdown_block = _block_from_marker(source, "void CG_Shutdown( void )")

	assert "trap_AdvertisementBridge_InitCGame();" in init_block
	assert init_block.index("trap_AdvertisementBridge_InitCGame();") > init_block.index("CG_ShaderStateChanged();")
	assert init_block.index("trap_AdvertisementBridge_InitCGame();") < init_block.index("trap_S_ClearLoopingSounds( qtrue );")

	assert "trap_AdvertisementBridge_ShutdownCGame();" in shutdown_block
	assert shutdown_block.index("trap_AdvertisementBridge_ShutdownCGame();") < shutdown_block.index('trap_Cvar_Set( "ui_mainmenu", "1" );')


def test_cgame_drawtools_keep_retail_widescreen_bias_consumers() -> None:
	source = CG_DRAWTOOLS.read_text(encoding="utf-8")
	adjust_block = _block_from_marker(source, "void CG_AdjustFrom640")

	for expected in (
		"static int cgAdjustFrom640Mode = -1;",
		"static void CG_GetAdjustedXScale( float *xScale, float *xBias ) {",
		"centered = ( trap_Key_GetCatcher() & KEYCATCH_CGAME ) != 0;",
		"if ( cgAdjustFrom640Mode == WIDESCREEN_STRETCH && !centered ) {",
		"if ( cgAdjustFrom640Mode == WIDESCREEN_RIGHT ) {",
		"if ( cgAdjustFrom640Mode == WIDESCREEN_CENTER || centered ) {",
		"CG_GetAdjustedXScale( &xScale, &xBias );",
		"if ( x ) {",
		"if ( y ) {",
		"if ( w ) {",
		"if ( h ) {",
		"*x = (*x * xScale) + xBias;",
		"ax = x * xScale + xBias;",
		"ay = y * cgs.screenYScale;",
		"aw = (float)propMapB[ch][2] * xScale;",
		"ah = (float)PROPB_HEIGHT * cgs.screenYScale;",
		"aw = (float)propMap[ch][2] * xScale * sizeScale;",
		"ah = (float)PROP_HEIGHT * cgs.screenYScale * sizeScale;",
		"size *= xScale;",
		"void CG_SetAdjustFrom640Mode( int widescreen ) {",
	):
		assert expected in source

	assert "if ( x ) {" in adjust_block
	assert "ax = x * cgs.screenXScale + cgs.screenXBias;" not in source
	assert "ay = y * cgs.screenXScale;" not in source
	assert "size *= cgs.screenXScale;" not in source


def test_cgame_crosshair_resets_renderer_color_after_shader_draw() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	block = _block_from_marker(source, "static void CG_DrawCrosshair(void)")

	assert "if ( !cg_drawCrosshair.integer ) {" in block
	assert block.index("if ( !cg_drawCrosshair.integer ) {") < block.index("trap_R_SetColor(")
	assert "trap_R_DrawStretchPic( x + cg.refdef.x + 0.5 * (cg.refdef.width - w)," in block
	assert "trap_R_SetColor( NULL );" in block
	assert block.index("trap_R_SetColor( NULL );") > block.index("trap_R_DrawStretchPic(")


def test_cgame_drawtools_big_string_wrappers_use_retail_text_paint_path() -> None:
	source = CG_DRAWTOOLS.read_text(encoding="utf-8")
	big_block = _block_from_marker(source, "void CG_DrawBigString")
	big_color_block = _block_from_marker(source, "void CG_DrawBigStringColor")

	assert "CG_Text_Paint( (float)x, (float)( y + BIGCHAR_HEIGHT ), 0.25f, color, s, 0, 0, 0 );" in big_block
	assert "CG_DrawStringExt(" not in big_block

	assert "CG_Text_Paint( (float)x, (float)( y + BIGCHAR_HEIGHT ), 0.25f, color, s, 0, 0, 0 );" in big_color_block
	assert "CG_DrawStringExt(" not in big_color_block


def test_cgame_effect_event_bridge_keeps_retail_teleport_and_impact_callbacks() -> None:
	event_source = CG_EVENT.read_text(encoding="utf-8")
	effects_source = CG_EFFECTS.read_text(encoding="utf-8")
	obelisk_block = _block_from_marker(effects_source, "void CG_ObeliskPain")

	for expected in (
		"CG_SpawnEffect( position);",
		"CG_SpawnEffect(  position);",
		"CG_KamikazeEffect( cent->lerpOrigin );",
		"CG_ObeliskExplode( cent->lerpOrigin, es->eventParm );",
		"CG_ObeliskPain( cent->lerpOrigin );",
		"CG_InvulnerabilityImpact( cent->lerpOrigin, cent->currentState.angles );",
		"CG_LightningBoltBeam(es->origin2, es->pos.trBase);",
	):
		assert expected in event_source

	assert re.search(r"\bint\s+r;", obelisk_block)
	assert "float r;" not in obelisk_block
	assert "r = rand() & 3;" in obelisk_block


def test_cgame_effects_keep_retail_lightning_discharge_sprite_producer() -> None:
	source = CG_EFFECTS.read_text(encoding="utf-8")
	block = _block_from_marker(source, "void CG_LightningDischargeEffect")

	assert 'trap_R_RegisterShader( "models/weaphits/electric.tga" );' in block
	assert "radius = (float)( ( magnitude * 10 + 48 ) >> 4 );" in block
	assert "duration = magnitude + 300;" in block
	assert "le = CG_SmokePuff( origin, vec3_origin, radius," in block
	assert "le->leType = LE_SCALE_FADE;" in block


def test_cgame_race_reset_state_keeps_retail_raceinit_command() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	run_block = _block_from_marker(source, "void CG_RaceResetRunState")
	block = _block_from_marker(source, "void CG_RaceResetState")

	assert "memset( cgs.raceProgress, 0, sizeof( cgs.raceProgress ) );" in run_block
	assert "cgs.raceInfoActive = qfalse;" in run_block
	assert "cgs.raceInfoCurrentCheckpointEntityNum = -1;" in run_block
	assert "cgs.raceInfoNextCheckpointEntityNum = -1;" in run_block
	assert "if ( clearRecordedTimes ) {" in run_block
	assert "memset( cgs.raceLeaderSplits, 0, sizeof( cgs.raceLeaderSplits ) );" in run_block
	assert "cgs.raceInfoLastTime = -1;" in run_block
	assert "CG_RaceResetRunState( qtrue );" in block
	assert "if ( cgs.gametype == GT_RACE ) {" in block
	assert 'trap_SendClientCommand( "raceinit" );' in block


def test_cgame_race_follow_payload_drives_followed_progress_and_times() -> None:
	draw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	progress_block = _block_from_marker(draw_source, "static qboolean CG_RaceApplyObservedFollowProgress")
	update_block = _block_from_marker(draw_source, "static void CG_RaceUpdateClientProgress")
	times_block = _block_from_marker(draw_source, "static qboolean CG_RaceBuildTimesStrings")

	assert "static qboolean CG_RaceApplyObservedFollowProgress( int clientNum, cgRaceClientProgress_t *progress ) {" in draw_source
	assert "clientNum != cg.spectatorFollowClient" in progress_block
	assert "clientNum != cg.clientNum" in progress_block
	assert "progress->runActive = cgs.raceInfoActive;" in progress_block
	assert "progress->currentCheckpoint = cgs.raceInfoCheckpointCount;" in progress_block
	assert "if ( CG_RaceApplyObservedFollowProgress( clientNum, progress ) ) {" in update_block
	assert "currentElapsed = cg.time - cgs.raceInfoStartTime;" in times_block
	assert "lastTime = ( cgs.raceInfoLastTime >= 0 ) ? cgs.raceInfoLastTime : -1;" in times_block


def test_cgame_view_keeps_retail_aspect_ratio_fallback_and_horplus_helpers() -> None:
	view_source = CG_VIEW.read_text(encoding="utf-8")
	aspect_block = _block_from_marker(view_source, "static qboolean CG_GetTargetAspectDimensions")
	horplus_block = _block_from_marker(view_source, "static float CG_CalcHorPlusFov")

	assert "case 1:" in aspect_block
	assert "case 2:" in aspect_block
	assert "case 3:" in aspect_block
	assert "if ( ratio <= 0 ) {" in aspect_block
	assert "*targetWidth = 5.0f;" in aspect_block
	assert "*targetHeight = 4.0f;" in aspect_block
	assert "return qfalse;" in aspect_block

	assert "baseWidth = 4.0f;" in horplus_block
	assert "baseHeight = 3.0f;" in horplus_block
	assert "x = baseWidth / tan( baseFov / 360.0f * M_PI );" in horplus_block
	assert "fovY = atan2( baseHeight, x );" in horplus_block
	assert "x = targetHeight / tan( fovY / 360.0f * M_PI );" in horplus_block
	assert "return atan2( targetWidth, x ) * 360.0f / M_PI;" in horplus_block


def test_cgame_view_keeps_retail_fov_order_for_horplus_and_zoom_trace() -> None:
	view_source = CG_VIEW.read_text(encoding="utf-8")
	fov_block = _block_from_marker(view_source, "static int CG_CalcFov")
	trace_block = _block_from_marker(view_source, "static float CG_CalcSmartCameraTraceRange")

	assert "fov_x = CG_CalcHorPlusFov( fov_x );" in fov_block
	assert "x = cg.refdef.width / tan( fov_x / 360 * M_PI );" in fov_block
	assert "fov_y = atan2( cg.refdef.height, x );" in fov_block
	assert "fov_y = fov_y * 360 / M_PI;" in fov_block
	assert "fov_x += v;" in fov_block
	assert "fov_y -= v;" in fov_block
	assert "fovY = atan2( 480.0f, x ) * 360.0f / M_PI;" in trace_block
	assert "fovX = CG_CalcAspectAdjustedFovFromVertical( fovY );" in trace_block


def test_cgame_event_reconstruction_keeps_retail_overtime_gameover_and_race_handlers() -> None:
	event_source = CG_EVENT.read_text(encoding="utf-8")
	view_source = CG_VIEW.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	winner_block = _block_from_marker(event_source, "static qboolean CG_IsLocalPlayerWinner")
	overtime_block = _block_from_marker(event_source, "int CG_GetOvertimeCount( void )")
	local_client_block = _block_from_marker(event_source, "static qboolean CG_IsRetailLocalEventClient")
	event_block = _block_from_marker(event_source, "void CG_EntityEvent")
	view_block = _block_from_marker(view_source, "void CG_ClearBufferedAnnouncements")

	for expected in (
		"QL_EV_OVERTIME = 0x54",
		"QL_EV_GAMEOVER = 0x55",
		"QL_EV_LIGHTNING_DISCHARGE = 0x5c",
		"QL_EV_RACE_START = 0x5d",
		"QL_EV_RACE_CHECKPOINT = 0x5e",
		"QL_EV_RACE_FINISH = 0x5f",
	):
		assert expected in event_source

	assert "void CG_ClearBufferedAnnouncements( void );" in local_source
	assert "CG_ClearBufferedSounds();" in view_block

	assert "if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {" in local_client_block
	assert "return ( qboolean )( clientNum == cg.spectatorFollowClient );" in local_client_block
	assert "return ( qboolean )( clientNum == cg.clientNum );" in local_client_block

	assert "rank = cg.snap->ps.persistant[PERS_RANK];" in winner_block
	assert "if ( rank & RANK_TIED_FLAG ) {" in winner_block
	assert "if ( cg.teamScores[0] == cg.teamScores[1] ) {" in winner_block
	assert "return ( qboolean )( cg.teamScores[0] > cg.teamScores[1] );" in winner_block
	assert "return ( qboolean )( cg.teamScores[1] > cg.teamScores[0] );" in winner_block

	assert "if ( cgs.matchOvertimeCount > 0 ) {" in overtime_block
	assert "regulationEnd = cgs.levelStartTime + ( cgs.timelimit * 60000 );" in overtime_block
	assert "elapsed = anchor - regulationEnd;" in overtime_block
	assert "return elapsed / overtimeWindow;" in overtime_block

	for expected in (
		"case QL_EV_OVERTIME:",
		'trap_S_RegisterSound( "sound/world/klaxon2.ogg", qfalse )',
		'CG_CenterPrint( va( "Overtime! %d seconds added", secondsAdded ), 90, BIGCHAR_WIDTH );',
		"CG_AddBufferedSound( cgs.media.overtimeSound );",
		"case QL_EV_GAMEOVER:",
		"CG_ClearBufferedAnnouncements();",
		'trap_S_StartLocalSound( trap_S_RegisterSound( "sound/world/buzzer.ogg", qfalse ), CHAN_LOCAL_SOUND );',
		'trap_S_StartBackgroundTrack( "music/win", "" );',
		'trap_S_StartBackgroundTrack( "music/loss", "" );',
		"case QL_EV_LIGHTNING_DISCHARGE:",
		"CG_LightningDischargeEffect( cent->lerpOrigin, es->eventParm );",
		"case QL_EV_RACE_START:",
		"CG_RaceResetRunState( qfalse );",
		"cgs.raceInfoStartTime = CG_GetRetailEventIntPayload( es );",
		"CG_RacePlayCue( CG_RACE_CUE_START );",
		"case QL_EV_RACE_CHECKPOINT:",
		"cgs.raceInfoCheckpointCount = CG_GetRaceEventCheckpointCount( es );",
		"CG_RacePlayCue( CG_RACE_CUE_CHECKPOINT );",
		"case QL_EV_RACE_FINISH:",
		"cgs.raceInfoLastTime = CG_GetRetailEventIntPayload( es );",
		"CG_RacePlayCue( CG_RACE_CUE_FINISH );",
	):
		assert expected in event_block


def test_cgame_event_reconstruction_keeps_retail_award_and_local_reward_handlers() -> None:
	event_source = CG_EVENT.read_text(encoding="utf-8")
	main_source = CG_MAIN.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	award_block = _block_from_marker(event_source, "static void CG_HandleRetailAwardEvent")

	for expected in (
		"QL_EV_AWARD = 0x61",
		"QL_EV_INFECTED = 0x62",
		"QL_EV_NEW_HIGH_SCORE = 99",
		"static int CG_GetRetailEventClientNum( const entityState_t *es )",
		"static int CG_GetRetailAwardType( const entityState_t *es )",
		"static int CG_GetRetailAwardCount( const entityState_t *es )",
	):
		assert expected in event_source

	for expected in (
		"qhandle_t\tmedalAccuracy;",
		"qhandle_t\tmedalComboKill;",
		"sfxHandle_t comboKillSound;",
		"sfxHandle_t comboKillSound2;",
		"sfxHandle_t comboKillSound3;",
		"sfxHandle_t accuracySound;",
		"sfxHandle_t rampageSound2;",
		"sfxHandle_t rampageSound3;",
		"sfxHandle_t revengeSound2;",
		"sfxHandle_t revengeSound3;",
		"sfxHandle_t infectedSound;",
		"sfxHandle_t newHighScoreSound;",
		"void pushReward( sfxHandle_t sfx, qhandle_t shader, int rewardCount );",
	):
		assert expected in local_source

	for expected in (
		"CG_REGISTER_RETAIL_REWARD_SAMPLE( comboKillSound, \"combokill1\", \"combokill1\" );",
		"CG_REGISTER_RETAIL_REWARD_SAMPLE( comboKillSound2, \"combokill2\", \"combokill2\" );",
		"CG_REGISTER_RETAIL_REWARD_SAMPLE( comboKillSound3, \"combokill3\", \"combokill3\" );",
		"CG_REGISTER_RETAIL_REWARD_SAMPLE( accuracySound, \"accuracy\", \"accuracy\" );",
		"CG_REGISTER_RETAIL_REWARD_SAMPLE( infectedSound, \"infected\", \"infected\" );",
		"CG_REGISTER_RETAIL_REWARD_SAMPLE( newHighScoreSound, \"new_high_score\", \"new_high_score\" );",
		'cgs.media.medalAccuracy = trap_R_RegisterShaderNoMip( "medal_accuracy" );',
		'cgs.media.medalComboKill = trap_R_RegisterShaderNoMip( "medal_combokill" );',
	):
		assert expected in main_source

	for expected in (
		"rewardCount = CG_GetRetailAwardCount( es );",
		"variant = rand() % 3;",
		"shader = cgs.media.medalComboKill;",
		"shader = cgs.media.medalAccuracy;",
		"shader = cgs.media.medalFirstFrag;",
		"rewardCount = 1;",
		"pushReward( sfx, shader, rewardCount );",
		"case QL_EV_AWARD:",
		"CG_HandleRetailAwardEvent( es );",
		"case QL_EV_INFECTED:",
		"CG_AddBufferedSound( cgs.media.infectedSound );",
		"case QL_EV_NEW_HIGH_SCORE:",
		"CG_AddBufferedSound( cgs.media.newHighScoreSound );",
	):
		assert expected in event_source

	assert "CG_IsRetailLocalEventClient( clientNum )" in award_block
	assert "CG_GetRetailEventClientNum( es )" in event_source


def test_cgame_event_reconstruction_keeps_retail_damage_plum_bridge() -> None:
	event_source = CG_EVENT.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	localents_source = CG_LOCALENTS.read_text(encoding="utf-8")
	damage_plum_block = _block_from_marker(event_source, "static void CG_DamagePlum")

	for expected in (
		"static int CG_GetRetailDamagePlumDamage( const entityState_t *es )",
		"static weapon_t CG_GetRetailDamagePlumWeapon( const entityState_t *es )",
		"static void CG_GetDamagePlumColor( int damage, weapon_t weapon, vec4_t color )",
		"static void CG_DamagePlum( vec3_t org, int damage, weapon_t weapon )",
		"case EV_DAMAGEPLUM:",
		"CG_DamagePlum( cent->lerpOrigin, CG_GetRetailDamagePlumDamage( es ), CG_GetRetailDamagePlumWeapon( es ) );",
	):
		assert expected in event_source

	for expected in (
		"if ( damage <= 0 || !CG_DamagePlumsEnabled() ) {",
		"if ( !CG_ShouldRenderDamagePlumForWeapon( weapon ) ) {",
		"CG_GetDamagePlumColor( damage, weapon, color );",
		"marker = CG_AllocQueuedWorldMarker();",
		"marker->origin[0] += crandom() * 10.0f;",
		"marker->duration = 2000;",
		"marker->fadeDelay = 1000;",
		"marker->rise = 100.0f;",
		"marker->textScale = 0.18f;",
		"Vector4Copy( color, marker->color );",
		'Com_sprintf( marker->text, sizeof( marker->text ), "%d", damage );',
	):
		assert expected in damage_plum_block

	assert "CG_IsRetailLocalEventClient( CG_GetRetailEventClientNum( es ) )" in event_source
	assert "return es->eventParm;" in event_source
	assert "return WP_NONE;" in event_source
	assert "LEF_SCOREPLUM_CUSTOMCOLOR" not in local_source
	assert "LEF_SCOREPLUM_CUSTOMCOLOR" not in localents_source
	assert "re->shaderRGBA[3] = (byte)( 0xff * 4 * c );" in localents_source
	assert "re->shaderRGBA[3] = 0xff;" in localents_source


def test_cgame_server_settings_panel_reconstruction_uses_retail_custom_setting_configstrings() -> None:
	servercmds_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c" ).read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	parse_custom_block = _block_from_marker(servercmds_source, "static void CG_ParseCustomSettingsConfigString")
	parse_serverinfo_block = _block_from_marker(servercmds_source, "void CG_ParseServerinfo")
	parse_armor_block = _block_from_marker(servercmds_source, "static void CG_ParseArmorTieredConfigString")
	parse_info_block = _block_from_marker(servercmds_source, "static void CG_ParseServerSettingsInfoConfigStrings")
	draw_block = _block_from_marker(newdraw_source, "static void CG_DrawServerSettings")
	set_config_values_block = _block_from_marker(servercmds_source, "void CG_SetConfigValues")

	for expected in (
		"unsigned long long\tcustomSettingsMask;",
		"qboolean\tserverSettingsArmorTiered;",
		"int\t\tserverSettingsQuadFactor;",
		"int\t\tserverSettingsGravity;",
	):
		assert expected in local_source

	assert "info = CG_ConfigString( CS_CUSTOM_SETTINGS );" in parse_custom_block
	assert "value = strtoull( info, &end, 0 );" in parse_custom_block
	assert "cgs.customSettingsMask = value;" in parse_custom_block

	for expected in (
		'info = CG_ConfigString( CS_SERVER_SETTINGS_INFO_A );',
		'Info_ValueForKey( info, "armor_tiered" )',
		'value = "0";',
		"cgs.serverSettingsArmorTiered = (qboolean)( atoi( value ) != 0 );",
		"cg.armorTieredEnabled = cgs.serverSettingsArmorTiered;",
		'trap_Cvar_Set( "cg_armorTiered", value );',
		"trap_Cvar_Update( &cg_armorTiered );",
	):
		assert expected in parse_armor_block

	assert 'Info_ValueForKey( info, "g_armorTiered" )' not in parse_serverinfo_block
	assert 'trap_Cvar_Set( "cg_armorTiered", armorTieredValue );' not in parse_serverinfo_block

	for expected in (
		'info = CG_ConfigString( CS_SERVER_SETTINGS_INFO_B );',
		'Info_ValueForKey( info, "g_quadDamageFactor" )',
		'Info_ValueForKey( info, "g_gravity" )',
		"cgs.serverSettingsQuadFactor = value[0] ? atoi( value ) : 3;",
		"cgs.serverSettingsGravity = value[0] ? atoi( value ) : 800;",
	):
		assert expected in parse_info_block

	assert "CG_ParseCustomSettingsConfigString();" in set_config_values_block
	assert "CG_ParseArmorTieredConfigString();" in set_config_values_block
	assert "CG_ParseServerSettingsInfoConfigStrings();" in set_config_values_block
	assert "num == CS_CUSTOM_SETTINGS" in servercmds_source
	assert "num == CS_SERVER_SETTINGS_INFO_A" in servercmds_source
	assert "num == CS_SERVER_SETTINGS_INFO_B" in servercmds_source

	for expected in (
		'"AIR CONTROL"',
		'"RAMP JUMPING"',
		'"TIERED ARMOR"',
		'"MODIFIED WEAPON SWITCH"',
		'"%ix QUAD"',
		'"MODIFIED PHYSICS"',
		'"GRAVITY %i"',
		'"INSTAGIB"',
		'"QUAD HOG"',
		'"REGEN HEALTH"',
		'"DROP DAMAGED HEALTH"',
		'"VAMPIRIC DAMAGE"',
		'"MODIFIED ITEM SPAWNING"',
		'"HEADSHOTS ENABLED"',
		'"RAIL JUMPING"',
		'"MODIFIED WEAPONS"',
		"weaponMask = (unsigned int)( cgs.customSettingsMask & CUSTOM_SETTING_WEAPON_MASK );",
		"cgs.serverSettingsQuadFactor != 3",
		"cgs.serverSettingsGravity != 800",
		"cgs.serverSettingsArmorTiered",
		"if ( activeCount < 15 ) {",
		"CG_DrawPic( iconX, iconY, iconSize, iconSize, icon );",
	):
		assert expected in draw_block


def test_cgame_armor_tiered_configstring_retains_direct_retail_parser_boundary() -> None:
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	parse_block = _block_from_marker(servercmds_source, "static void CG_ParseArmorTieredConfigString")
	set_config_values_block = _block_from_marker(servercmds_source, "void CG_SetConfigValues")
	configstring_modified_block = _block_from_marker(servercmds_source, "static void CG_ConfigStringModified")
	parse_serverinfo_block = _block_from_marker(servercmds_source, "void CG_ParseServerinfo")

	assert 'info = CG_ConfigString( CS_SERVER_SETTINGS_INFO_A );' in parse_block
	assert 'Info_ValueForKey( info, "armor_tiered" )' in parse_block
	assert 'trap_Cvar_Set( "cg_armorTiered", value );' in parse_block
	assert "trap_Cvar_Update( &cg_armorTiered );" in parse_block

	assert "CG_ParseArmorTieredConfigString();" in set_config_values_block
	assert "num == CS_SERVER_SETTINGS_INFO_A" in configstring_modified_block
	assert "CG_ParseArmorTieredConfigString();" in configstring_modified_block

	assert 'Info_ValueForKey( info, "armor_tiered" )' not in parse_serverinfo_block
	assert 'trap_Cvar_Set( "cg_armorTiered", value );' not in parse_serverinfo_block


def test_cgame_player_cylinders_configstring_retains_direct_retail_parser_boundary() -> None:
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	parse_block = _block_from_marker(servercmds_source, "static void CG_ParsePlayerCylindersConfigString")
	set_config_values_block = _block_from_marker(servercmds_source, "void CG_SetConfigValues")
	configstring_modified_block = _block_from_marker(servercmds_source, "static void CG_ConfigStringModified")
	parse_serverinfo_block = _block_from_marker(servercmds_source, "void CG_ParseServerinfo")

	assert "info = CG_ConfigString( CS_PLAYER_CYLINDERS );" in parse_block
	assert 'value = ( info && info[0] ) ? va( "%i", atoi( info ) ) : "0";' in parse_block
	assert "cgs.playerCylindersEnabled = (qboolean)( atoi( value ) != 0 );" in parse_block
	assert 'trap_Cvar_Set( "cg_playerCylinders", value );' in parse_block
	assert "trap_Cvar_Update( &cg_playerCylinders );" in parse_block

	assert "CG_ParsePlayerCylindersConfigString();" in set_config_values_block
	assert "num == CS_PLAYER_CYLINDERS" in configstring_modified_block
	assert "CG_ParsePlayerCylindersConfigString();" in configstring_modified_block

	assert 'Info_ValueForKey( info, "g_playerCylinders" )' not in parse_serverinfo_block
	assert 'trap_Cvar_Set( "cg_playerCylinders", playerCylindersValue );' not in parse_serverinfo_block


def test_game_cvar_transport_redundancy_stays_off_serverinfo_slabs() -> None:
	game_source = G_MAIN.read_text(encoding="utf-8")

	for expected in (
		'{ &g_playermodelOverride, "g_playermodelOverride", "", CVAR_ARCHIVE, 0, qfalse, qfalse, "Optional model path used to override every player\'s model selection server-wide." },',
		'{ &g_playerheadmodelOverride, "g_playerheadmodelOverride", "", CVAR_ARCHIVE, 0, qfalse, qfalse, "Optional head model override applied to all players for consistent visuals." },',
		'{ &g_playerCylinders, "g_playerCylinders", "1", CVAR_ARCHIVE, 0, qfalse, qfalse, "Toggles the Quake Live player-cylinder collision volumes so forced cosmetics line up with the server\'s hitboxes." },',
		'{ &g_armorTiered, "g_armorTiered", "0", CVAR_ARCHIVE | CVAR_NORESTART, 0, qfalse, qfalse, "Enable retail Quake Live tiered armor behaviour for pickups, regen, and the dedicated HUD settings transport." },',
	):
		assert expected in game_source

	for unexpected in (
		'{ &g_playermodelOverride, "g_playermodelOverride", "", CVAR_SERVERINFO | CVAR_ARCHIVE,',
		'{ &g_playerheadmodelOverride, "g_playerheadmodelOverride", "", CVAR_SERVERINFO | CVAR_ARCHIVE,',
		'{ &g_playerCylinders, "g_playerCylinders", "1", CVAR_SERVERINFO | CVAR_ARCHIVE,',
		'{ &g_armorTiered, "g_armorTiered", "0", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART,',
	):
		assert unexpected not in game_source


def test_cgame_factory_title_reconstruction_uses_serverinfo_and_factory_flags_split() -> None:
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	parse_title_block = _block_from_marker(servercmds_source, "static void CG_ParseFactoryTitleServerinfo")
	parse_serverinfo_block = _block_from_marker(servercmds_source, "void CG_ParseServerinfo")
	parse_factory_block = _block_from_marker(servercmds_source, "static void CG_ParseFactoryMetadata")
	configstring_modified_block = _block_from_marker(servercmds_source, "static void CG_ConfigStringModified")

	assert 'Info_ValueForKey( info, "g_factoryTitle" )' in parse_title_block
	assert 'Com_sprintf( cgs.factoryTitle, sizeof( cgs.factoryTitle ), "%.*s", length, value + start );' in parse_title_block
	assert "CG_ParseFactoryTitleServerinfo( info );" in parse_serverinfo_block

	assert 'info = CG_ConfigString( CS_FACTORY_FLAGS );' in parse_factory_block
	assert "cgs.factoryTitle" not in parse_factory_block

	assert "num == CS_FACTORY_FLAGS" in configstring_modified_block
	assert "num == CS_FACTORY_TITLE" not in configstring_modified_block


def test_cgame_player_appearance_configstring_reconstruction_uses_retail_parser_and_head_gate() -> None:
	servercmds_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c" ).read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	players_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c" ).read_text(encoding="utf-8")
	draw_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c" ).read_text(encoding="utf-8")
	parse_block = _block_from_marker(servercmds_source, "static void CG_ParsePlayerAppearanceConfigString")
	set_config_values_block = _block_from_marker(servercmds_source, "void CG_SetConfigValues")
	new_client_block = _block_from_marker(players_source, "void CG_NewClientInfo( int clientNum )")
	draw_head_block = _block_from_marker(draw_source, "void CG_DrawHead( float x, float y, float w, float h, int clientNum, vec3_t headAngles )")

	for expected in (
		"qboolean\t\tallowCustomHeadmodels;",
		"float\t\t\tplayerHeadScale;",
		"float\t\t\tplayerHeadScaleOffset;",
		"float\t\t\tplayerModelScale;",
	):
		assert expected in local_source

	for expected in (
		"info = CG_ConfigString( CS_PLAYER_APPEARANCE );",
		'Info_ValueForKey( info, "g_playermodelOverride" )',
		'Info_ValueForKey( info, "g_playerheadmodelOverride" )',
		'Info_ValueForKey( info, "g_allowCustomHeadmodels" )',
		'Info_ValueForKey( info, "g_playerheadScale" )',
		'Info_ValueForKey( info, "g_playerheadScaleOffset" )',
		'Info_ValueForKey( info, "g_playerModelScale" )',
		"CG_ResetPlayerAppearanceState();",
		"cgs.allowCustomHeadmodels = (qboolean)( atoi( value ) != 0 );",
		"cgs.playerHeadScale = (float)atof( value );",
		"cgs.playerHeadScaleOffset = (float)atof( value );",
		"cgs.playerModelScale = (float)atof( value );",
		"CG_ApplyModelOverrides();",
	):
		assert expected in parse_block

	for unexpected in (
		"fallbackInfo = CG_ConfigString( CS_SERVERINFO );",
		'Info_ValueForKey( fallbackInfo, "g_playermodelOverride" )',
		'Info_ValueForKey( fallbackInfo, "g_playerheadmodelOverride" )',
	):
		assert unexpected not in parse_block

	assert "CG_ParsePlayerAppearanceConfigString();" in set_config_values_block
	assert "num == CS_PLAYER_APPEARANCE" in servercmds_source

	for expected in (
		"if ( !cgs.allowCustomHeadmodels ) {",
		"Q_strncpyz( newInfo.headModelName, newInfo.modelName, sizeof( newInfo.headModelName ) );",
		"Q_strncpyz( newInfo.headSkinName, newInfo.skinName, sizeof( newInfo.headSkinName ) );",
	):
		assert expected in new_client_block

	assert "len *= cgs.playerModelScale;" in draw_head_block


def test_cgame_head_offset_refresh_restores_retail_model_scale_seam() -> None:
	servercmds_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c" ).read_text(encoding="utf-8")
	players_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c" ).read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	parse_block = _block_from_marker(servercmds_source, "static void CG_ParsePlayerAppearanceConfigString")
	update_block = _block_from_marker(players_source, "static qboolean CG_UpdateClientHeadOffset")
	refresh_block = _block_from_marker(players_source, "void CG_RefreshClientHeadOffsets( void )")
	register_block = _block_from_marker(players_source, "static qboolean CG_RegisterClientModelname")

	assert "void CG_RefreshClientHeadOffsets( void );" in local_source

	for expected in (
		'!Q_stricmp( ci->modelName, "orbb" )',
		"ci->headOffset[0] = 1.0f;",
		"trap_R_ModelBounds( ci->headModel, mins, maxs );",
		'"tag_torso"',
		'"tag_head"',
		"cgs.playerModelScale",
		"ci->headOffset[0] = ( 56.0f / totalHeight ) * cgs.playerModelScale;",
	):
		assert expected in update_block

	for expected in (
		"oldPlayerModelScale = cgs.playerModelScale;",
		"oldPlayerModelScale != cgs.playerModelScale",
		"CG_RefreshClientHeadOffsets();",
	):
		assert expected in parse_block

	assert "CG_UpdateClientHeadOffset( ci );" in register_block
	assert "CG_UpdateClientHeadOffset( ci );" in refresh_block


def test_cgame_player_head_world_transform_restores_retail_scale_offset_seam() -> None:
	players_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c" ).read_text(encoding="utf-8")
	transform_block = _block_from_marker(players_source, "static void CG_ApplyPlayerHeadWorldTransform")
	player_block = _block_from_marker(players_source, "void CG_Player( centity_t *cent )")

	for expected in (
		"if ( !head || cg.renderingThirdPerson ) {",
		"head->nonNormalizedAxes = qtrue;",
		"head->origin[2] -= ( cgs.playerHeadScaleOffset * -0.1875f ) + 24.0f;",
		"VectorScale( head->axis[0], cgs.playerHeadScale, head->axis[0] );",
		"VectorScale( head->axis[1], cgs.playerHeadScale, head->axis[1] );",
		"VectorScale( head->axis[2], cgs.playerHeadScale, head->axis[2] );",
	):
		assert expected in transform_block

	tag_index = player_block.index('CG_PositionRotatedEntityOnTag( &head, &torso, ci->torsoModel, "tag_head");')
	transform_index = player_block.index("CG_ApplyPlayerHeadWorldTransform( &head );")
	shadow_index = player_block.index("head.shadowPlane = shadowPlane;")

	assert tag_index < transform_index < shadow_index


def test_cgame_player_color_helper_restores_retail_shared_color_scale_seam() -> None:
	players_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c" ).read_text(encoding="utf-8")
	scale_block = _block_from_marker(players_source, "static int CG_GetPlayerColorScale")
	tint_block = _block_from_marker(players_source, "static void CG_ApplyDeadBodyTint")
	set_color_block = _block_from_marker(players_source, "static void CG_SetRefEntityColor")
	resolve_block = _block_from_marker(players_source, "static void CG_ResolveClientModelColorBytes")
	apply_block = _block_from_marker(players_source, "static void CG_ApplyPlayerColors")
	player_block = _block_from_marker(players_source, "void CG_Player( centity_t *cent )")

	for expected in (
		'trap_Cvar_VariableStringBuffer( "r_colorCorrectActive", value, sizeof( value ) );',
		"return atof( value ) > 0.0f ? 1 : 2;",
	):
		assert expected in scale_block

	for expected in (
		"CG_SetScaledShaderRGBA( re->shaderRGBA, cg.deadBodyColor, colorScale );",
		"shaderColor[3] = 1.0f;",
		"CG_SetScaledShaderRGBA( ent->shaderRGBA, shaderColor, colorScale );",
	):
		assert expected in tint_block + set_color_block

	for expected in (
		"ci = &cgs.clientinfo[cent->currentState.clientNum];",
		"colorScale = CG_GetPlayerColorScale();",
		"CG_ShouldTintDeadBody( cent, ci )",
		"CG_SetScaledShaderRGBA( rgba, cg.deadBodyColor, colorScale );",
		"VectorCopy( ci->upperColor, shaderColor );",
		"CG_SetScaledShaderRGBA( rgba, shaderColor, colorScale );",
	):
		assert expected in resolve_block

	for expected in (
		"colorScale = CG_GetPlayerColorScale();",
		"CG_ResolveClientModelColorBytes( cent, torso->shaderRGBA );",
		"legs->shaderRGBA[0] = 255;",
		"memcpy( legs->shaderRGBA, torso->shaderRGBA, sizeof( legs->shaderRGBA ) );",
		"memcpy( head->shaderRGBA, torso->shaderRGBA, sizeof( head->shaderRGBA ) );",
		"CG_SetRefEntityColor( head, ci->headColor, colorScale );",
	):
		assert expected in apply_block

	assert "CG_ApplyPlayerColors( cent, ci, &legs, &torso, &head );" in player_block
	assert "tintCorpse = CG_ShouldTintDeadBody" not in player_block


def test_cgame_client_skin_normalizers_restore_retail_team_default_and_sport_split() -> None:
	players_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c" ).read_text(encoding="utf-8")
	default_skin_block = _block_from_marker(players_source, "static const char *CG_DefaultTeamSkinName")
	skin_block = _block_from_marker(players_source, "static void CG_NormalizeClientSkinName")
	head_skin_block = _block_from_marker(players_source, "static void CG_NormalizeClientHeadSkinName")
	new_client_block = _block_from_marker(players_source, "void CG_NewClientInfo( int clientNum )")

	for expected in (
		'return "red";',
		'return "blue";',
		'return "default";',
	):
		assert expected in default_skin_block

	for expected in (
		'Q_strncpyz( modelToken, ci->modelName, sizeof( modelToken ) );',
		"skinToken = strchr( modelToken, '/' );",
		"Q_strncpyz( ci->skinName, skinToken, sizeof( ci->skinName ) );",
		"CG_DefaultTeamSkinName( ci->team )",
		'!Q_stricmp( ci->skinName, "sport" )',
		'Q_strncpyz( ci->skinName, "sport_red", sizeof( ci->skinName ) );',
		'Q_strncpyz( ci->skinName, "sport_blue", sizeof( ci->skinName ) );',
	):
		assert expected in skin_block

	for expected in (
		'Q_strncpyz( headModelToken, ci->headModelName, sizeof( headModelToken ) );',
		"skinToken = strchr( headModelToken, '/' );",
		"Q_strncpyz( ci->headSkinName, skinToken, sizeof( ci->headSkinName ) );",
		"CG_DefaultTeamSkinName( ci->team )",
		'!Q_stricmp( ci->headSkinName, "sport" )',
		'Q_strncpyz( ci->headSkinName, "sport_red", sizeof( ci->headSkinName ) );',
		'Q_strncpyz( ci->headSkinName, "sport_blue", sizeof( ci->headSkinName ) );',
	):
		assert expected in head_skin_block

	for expected in (
		"CG_NormalizeClientSkinName( &newInfo );",
		"CG_NormalizeClientHeadSkinName( &newInfo );",
	):
		assert expected in new_client_block

	assert 'Q_strncpyz( newInfo.skinName, slash + 1, sizeof( newInfo.skinName ) );' not in new_client_block
	assert 'Q_strncpyz( newInfo.headSkinName, slash + 1, sizeof( newInfo.headSkinName ) );' not in new_client_block


def test_cgame_respawn_weapon_select_restores_retail_primary_preference_seam() -> None:
	playerstate_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_playerstate.c" ).read_text(encoding="utf-8")
	token_block = _block_from_marker(playerstate_source, "static weapon_t CG_RespawnWeaponFromToken")
	select_block = _block_from_marker(playerstate_source, "static void CG_SelectRespawnWeapon")
	respawn_block = _block_from_marker(playerstate_source, "void CG_Respawn( void )")

	for expected in (
		'"gauntlet"',
		'"rocket_launcher"',
		'"grappling_hook"',
		'"heavy_machinegun"',
		"return (weapon_t)atoi( token );",
	):
		assert expected in token_block

	for expected in (
		'trap_Cvar_VariableStringBuffer( "cg_weaponPrimary", buffer, sizeof( buffer ) );',
		"token = COM_ParseExt( &cursor, qtrue );",
		"weapon = CG_RespawnWeaponFromToken( token );",
		"cg.snap->ps.stats[STAT_WEAPONS] & ( 1 << weapon )",
		"CG_SetWeaponSelect( weapon );",
		"CG_SetWeaponSelect( cg.snap->ps.weapon );",
	):
		assert expected in select_block

	assert "CG_SelectRespawnWeapon();" in respawn_block
	assert "CG_SetWeaponSelect( cg.snap->ps.weapon );" not in respawn_block


def test_cgame_trace_capsule_helper_restores_retail_trace_split() -> None:
	predict_source = CG_PREDICT.read_text(encoding="utf-8")
	clip_block = _block_from_marker(predict_source, "static void CG_ClipMoveToEntities")
	capsule_block = _block_from_marker(predict_source, "static void CG_TraceCapsule")
	trace_block = _block_from_marker(predict_source, "void\tCG_Trace")

	for expected in (
		"int skipNumber, int mask, qboolean useCapsule, trace_t *tr )",
		"if ( useCapsule ) {",
		"cmodel = trap_CM_TempCapsuleModel( bmins, bmaxs );",
		"trap_CM_TransformedCapsuleTrace( &trace, start, end, mins, maxs, cmodel, mask, origin, angles );",
		"cmodel = trap_CM_TempBoxModel( bmins, bmaxs );",
		"trap_CM_TransformedBoxTrace( &trace, start, end, mins, maxs, cmodel, mask, origin, angles );",
	):
		assert expected in clip_block

	for expected in (
		"trap_CM_CapsuleTrace( &t, start, end, mins, maxs, 0, mask );",
		"CG_ClipMoveToEntities( start, mins, maxs, end, skipNumber, mask, qtrue, &t );",
	):
		assert expected in capsule_block

	for expected in (
		"if ( CG_UseCapsuleTrace() ) {",
		"CG_TraceCapsule( result, start, mins, maxs, end, skipNumber, mask );",
		"trap_CM_BoxTrace( &t, start, end, mins, maxs, 0, mask );",
		"CG_ClipMoveToEntities( start, mins, maxs, end, skipNumber, mask, qfalse, &t );",
	):
		assert expected in trace_block


def test_cgame_local_entity_dispatch_restores_retail_fragment_and_effect_split() -> None:
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	effects_source = CG_EFFECTS.read_text(encoding="utf-8")
	localents_source = CG_LOCALENTS.read_text(encoding="utf-8")
	fragment_block = _block_from_marker(localents_source, "void CG_AddFragment( localEntity_t *le )")
	tracer_fragment_block = _block_from_marker(localents_source, "static void CG_AddTracerFragmentTrail")
	tracer_block = _block_from_marker(localents_source, "static void CG_AddBigExplodeTracer")
	death_block = _block_from_marker(localents_source, "static void CG_AddDeathEffect")
	dispatch_block = _block_from_marker(localents_source, "void CG_AddLocalEntities( void )")

	for expected in (
		"LE_BIGEXPLODE_TRACER = 0x05,",
		"LE_05 = LE_BIGEXPLODE_TRACER,",
		"LE_DEATH_EFFECT = 0x0F,",
		"LE_0F = LE_DEATH_EFFECT,",
		"LE_SCALE_FADE_OUT = LE_DEATH_EFFECT,",
	):
		assert expected in local_source

	for expected in (
		"le->leType = LE_BIGEXPLODE_TRACER;",
		"le->leType = LE_DEATH_EFFECT;",
	):
		assert expected in effects_source

	for expected in (
		"if ( le->leType == LE_FRAGMENT_16 ) {",
		"CG_AddFragmentTrail( le, cgs.media.iceballShader );",
		"if ( CG_AddFragmentImpl( le ) && le->leType == LE_FRAGMENT_14 ) {",
		"CG_AddTracerFragmentTrail( le );",
	):
		assert expected in fragment_block

	assert "CG_AddFragmentTrail( le, cgs.media.tracerShader );" in tracer_fragment_block
	assert "(void)CG_AddSpriteEffectCommon( le );" in tracer_block
	assert "if ( CG_AddSpriteEffectCommon( le ) && le->light ) {" in death_block

	for expected in (
		"case LE_BIGEXPLODE_TRACER:",
		"CG_AddBigExplodeTracer( le );",
		"case LE_FRAGMENT_14:",
		"case LE_FRAGMENT_16:",
		"CG_AddFragment( le );",
		"case LE_DEATH_EFFECT:",
		"CG_AddDeathEffect( le );",
	):
		assert expected in dispatch_block

	for unexpected in (
		"CG_AddFragment14",
		"CG_AddFragment16",
		"CG_AddType05",
		"CG_AddType0F",
	):
		assert unexpected not in localents_source


def test_cgame_juiced_and_bigexplode_helpers_restore_retail_owner_split() -> None:
	effects_source = CG_EFFECTS.read_text(encoding="utf-8")
	event_source = CG_EVENT.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	localents_source = CG_LOCALENTS.read_text(encoding="utf-8")
	juiced_event_block = event_source.split("case EV_JUICED:")[1].split("break;", 1)[0]
	spawn_effects_block = _block_from_marker(effects_source, "static void CG_SpawnBigExplodeEffects")
	juiced_effect_block = _block_from_marker(effects_source, "void CG_InvulnerabilityJuiced")
	detonate_block = _block_from_marker(effects_source, "void CG_DetonateJuicedPlayer")
	bigexplode_block = _block_from_marker(effects_source, "void CG_BigExplode( vec3_t playerOrigin )")
	bigexplode_juiced_block = _block_from_marker(effects_source, "void CG_BigExplodeJuiced( vec3_t playerOrigin )")
	juiced_update_block = _block_from_marker(localents_source, "void CG_AddInvulnerabilityJuiced( localEntity_t *le )")

	assert "void CG_DetonateJuicedPlayer( const vec3_t playerOrigin, qboolean immediateFallback );" in local_source

	for expected in (
		"CG_SpawnDeathEffect( origin, elevatedShell );",
		"CG_SpawnBigExplodeTracer( tracerOrigin, cg.time + crandom() * 500.0f,",
	):
		assert expected in spawn_effects_block

	for expected in (
		"if ( cgs.media.haveDlcGibs ) {",
		"CG_GibPlayer( origin );",
		"CG_LaunchBigExplodeFragments( playerOrigin, !immediateFallback );",
		"CG_SpawnBigExplodeEffects( playerOrigin, !immediateFallback );",
	):
		assert expected in detonate_block

	assert "CG_DetonateJuicedPlayer( org, qtrue );" in juiced_effect_block
	assert "CG_DetonateJuicedPlayer( le->refEntity.origin, qfalse );" in juiced_update_block

	for expected in (
		"CG_LaunchBigExplodeFragments( playerOrigin, qfalse );",
		"CG_SpawnBigExplodeEffects( playerOrigin, qfalse );",
	):
		assert expected in bigexplode_block

	for expected in (
		"CG_LaunchBigExplodeFragments( playerOrigin, qtrue );",
		"CG_SpawnBigExplodeEffects( playerOrigin, qtrue );",
	):
		assert expected in bigexplode_juiced_block

	assert "CG_SpawnBigExplodeTracers" not in effects_source
	assert "if ( cgs.media.haveDlcGibs ) {" not in juiced_event_block
	assert "CG_InvulnerabilityJuiced( cent->lerpOrigin );" in juiced_event_block


def test_cgame_item_respawn_timer_helper_restores_retail_world_item_boundary() -> None:
	ents_source = CG_ENTS.read_text(encoding="utf-8")
	main_source = CG_MAIN.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	game_items_source = G_ITEMS.read_text(encoding="utf-8")
	item_block = _block_from_marker(ents_source, "static void CG_Item( centity_t *cent )")
	duration_block = _block_from_marker(ents_source, "static int CG_ItemRespawnTimerDuration")
	icon_block = _block_from_marker(ents_source, "static qhandle_t CG_ItemRespawnTimerIcon")
	slices_block = _block_from_marker(ents_source, "static void CG_ItemRespawnTimerSlices")
	timer_block = _block_from_marker(ents_source, "static void CG_DrawItemRespawnTimer")
	uses_block = _block_from_marker(game_items_source, "static qboolean G_ItemUsesRespawnTimer")
	publisher_block = _block_from_marker(game_items_source, "static void G_SetItemRespawnTimerState")

	for expected in (
		"qhandle_t\titemTimerArmorShader;",
		"qhandle_t\titemTimerUnknownShader;",
		"qhandle_t\titemTimerSlice24CurrentShader;",
	):
		assert expected in local_source

	for expected in (
		'cgs.media.itemTimerArmorShader = trap_R_RegisterShader( "gfx/2d/timer/armor" );',
		'cgs.media.itemTimerMedkitShader = trap_R_RegisterShader( "gfx/2d/timer/medkit" );',
		'cgs.media.itemTimerSlice24CurrentShader = trap_R_RegisterShader( "gfx/2d/timer/slice24_current" );',
	):
		assert expected in main_source

	for expected in (
		"if ( item->giType == IT_ARMOR ) {",
		"if ( item->giType == IT_HEALTH && item->quantity >= 100 ) {",
		"if ( item->giType == IT_POWERUP ) {",
		"if ( item->giType == IT_HOLDABLE && BG_HoldableForItemTag( item->giTag ) == HI_MEDKIT ) {",
	):
		assert expected in uses_block

	for expected in (
		"ent->s.time = markerTime;",
		"ent->s.time2 = respawnDuration;",
		"G_SetItemRespawnTimerState( ent, level.time, 0 );",
		"G_SetItemRespawnTimerState( ent, ( respawn > 0 ) ? ent->nextthink : level.time,",
		"G_SetItemRespawnTimerState( ent, ent->nextthink, (int)( respawn * 1000.0f ) );",
	):
		assert expected in game_items_source
	assert "if ( !ent || !G_ItemUsesRespawnTimer( ent->item ) ) {" in publisher_block

	for expected in (
		"if ( hiddenItem ) {",
		"return cgs.media.itemTimerUnknownShader;",
	):
		assert expected in icon_block

	assert "durationBuckets = respawnDuration / 5000;" in slices_block
	assert "respawnDuration = CG_ItemRespawnTimerDuration( item );" in item_block
	assert "return 120 * 1000;" in duration_block

	for expected in (
		"if ( !item || !origin || !cg_itemTimers.integer ) {",
		"alpha = ( 768.0f - distance ) * ( 1.0f / 512.0f );",
		"CG_ItemRespawnTimerSlices( respawnDuration, &sliceShader, &currentSliceShader, &sliceCount );",
		"elapsedSlice = ( ( respawnDuration - respawnRemaining ) / 5000 ) + 1;",
		"CG_DrawItemRespawnTimerSprite( iconShader, timerOrigin, alpha, 180.0f );",
		"rotation = -( 180 / sliceCount );",
	):
		assert expected in timer_block

	for expected in (
		"if ( CG_ItemUsesRespawnTimer( item ) && es->time > cg.time ) {",
		"respawnDuration = es->time2;",
		"respawnRemaining = es->time - cg.time;",
		"CG_DrawItemRespawnTimer( item, respawnRemaining, respawnDuration, cent->lerpOrigin, 0,",
		"(qboolean)( ( es->eFlags & EF_NODRAW ) != 0 ) );",
	):
		assert expected in item_block


def test_cgame_vote_widget_reconstruction_uses_retail_vote_cvar_and_text_paths() -> None:
	servercmds_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c" ).read_text(encoding="utf-8")
	main_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c" ).read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	vote_timer_block = _block_from_marker(newdraw_source, "static void CG_DrawVoteTimer")
	vote_count_block = _block_from_marker(newdraw_source, "static void CG_DrawVoteCount")
	set_config_values_block = _block_from_marker(servercmds_source, "void CG_SetConfigValues")

	for expected in (
		'cgs.voteTime = atoi( CG_ConfigString( CS_VOTE_TIME ) );',
		'cgs.voteYes = atoi( CG_ConfigString( CS_VOTE_YES ) );',
		'cgs.voteNo = atoi( CG_ConfigString( CS_VOTE_NO ) );',
		'Q_strncpyz( cgs.voteString, CG_ConfigString( CS_VOTE_STRING ), sizeof( cgs.voteString ) );',
		'trap_Cvar_Set( "ui_voteactive", cgs.voteTime ? "1" : "0" );',
		'trap_Cvar_Set( "ui_votestring", cgs.voteString );',
	):
		assert expected in set_config_values_block

	for expected in (
		'trap_Cvar_Set( "ui_votestring", "" );',
		'trap_Cvar_Set( "ui_votestring", cgs.voteString );',
		'cgs.voteString[0] = \'\\0\';',
	):
		assert expected in servercmds_source or expected in main_source

	for expected in (
		'"Voting has ended."',
		'"Voting ends in %i second."',
		'"Voting ends in %i seconds."',
	):
		assert expected in vote_timer_block

	assert '"Vote %is"' not in vote_timer_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "Votes: %s", countText );' in vote_count_block


def test_display_context_core_layout_matches_retail_widescreen_tail() -> None:
	source = UI_SHARED_H.read_text(encoding="utf-8")

	assert source.index("void (*drawText) (float x, float y, float scale, vec4_t color, const char *text, float adjust, int limit, int style );") < source.index("int (*textWidth) (const char *text, float scale, int limit);")
	assert source.index("int (*textWidth) (const char *text, float scale, int limit);") < source.index("int (*textHeight) (const char *text, float scale, int limit);")
	assert source.index("void (*drawTextWithCursor)(float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style);") < source.index("void (*setOverstrikeMode)(qboolean b);")
	assert source.index("qhandle_t (*playLauncherCinematic)(const char *name, qboolean loop, int width, int height);") < source.index("void (*stopCinematic)(int handle);")
	assert source.index("void (*activateAdvert)(int cellId);") < source.index("void (*adjustFrom640)(float *x, float *y, float *w, float *h);")
	assert source.index("void (*adjustFrom640)(float *x, float *y, float *w, float *h);") < source.index("void (*setAdjustFrom640Mode)(int widescreen);")
	assert source.index("void (*setAdjustFrom640Mode)(int widescreen);") < source.index("yscale;")
	assert source.index("float FPS;") < source.index("void (*drawTextExt)(float x, float y, float scale, vec4_t color, const char *text, float adjust, int limit, int style, int fontIndex);")
	assert source.index("void (*drawTextExt)(float x, float y, float scale, vec4_t color, const char *text, float adjust, int limit, int style, int fontIndex);") < source.index("int (*textWidthExt)(const char *text, float scale, int limit, int fontIndex);")
	assert source.index("int (*textHeightExt)(const char *text, float scale, int limit, int fontIndex);") < source.index("void (*drawTextWithCursorExt)(float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style, int fontIndex);")
	assert source.index("void (*drawTextWithCursorExt)(float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style, int fontIndex);") < source.index("void (*initAdvertisementBridge)(void);")


def test_shared_ui_widescreen_flow_uses_retail_adjust_callbacks() -> None:
	shared_source = UI_SHARED.read_text(encoding="utf-8")
	ui_main_source = UI_MAIN.read_text(encoding="utf-8")

	for expected in (
		"if (DC && DC->setAdjustFrom640Mode) {",
		"if (DC && DC->adjustFrom640) {",
		"if (DC->setAdjustFrom640Mode && item->widescreenSet) {",
		"DC->setAdjustFrom640Mode(item->widescreen);",
		"DC->setAdjustFrom640Mode(parent ? parent->widescreen : WIDESCREEN_STRETCH);",
		"DC->setAdjustFrom640Mode(menu->widescreen);",
		"DC->setAdjustFrom640Mode(WIDESCREEN_STRETCH);",
	):
		assert expected in shared_source

	for expected in (
		"uiInfo.uiDC.adjustFrom640 = &UI_AdjustFrom640;",
		"uiInfo.uiDC.setupAdvertCellShader = &UI_SetupAdvertCellShader;",
		"uiInfo.uiDC.refreshAdvertCellShader = &UI_RefreshAdvertCellShader;",
		"uiInfo.uiDC.activateAdvert = &UI_ActivateAdvert;",
		"uiInfo.uiDC.initAdvertisementBridge = &UI_InitAdvertisementBridge;",
	):
		assert expected in ui_main_source


def test_ui_adjust_from_640_uses_retail_bias_and_null_guards() -> None:
	source = UI_ATOMS.read_text(encoding="utf-8")
	adjust_block = _block_from_marker(source, "void UI_AdjustFrom640")

	for expected in (
		"if ( x ) {",
		"*x = ( *x * uiInfo.uiDC.xscale ) + uiInfo.uiDC.bias;",
		"if ( y ) {",
		"*y *= uiInfo.uiDC.yscale;",
		"if ( w ) {",
		"*w *= uiInfo.uiDC.xscale;",
		"if ( h ) {",
		"*h *= uiInfo.uiDC.yscale;",
	):
		assert expected in adjust_block

	assert "*x *= uiInfo.uiDC.xscale;" not in adjust_block


def test_ui_refresh_display_context_scale_keeps_centered_widescreen_xscale() -> None:
	source = UI_MAIN.read_text(encoding="utf-8")
	block = _block_from_marker(source, "static int UI_RefreshDisplayContextScale(void)")

	for expected in (
		"uiInfo.uiDC.yscale = uiInfo.uiDC.glconfig.vidHeight * (1.0f / 480.0f);",
		"if (uiInfo.uiDC.glconfig.vidWidth * SCREEN_HEIGHT > uiInfo.uiDC.glconfig.vidHeight * SCREEN_WIDTH) {",
		"uiInfo.uiDC.bias = 0.5f * (uiInfo.uiDC.glconfig.vidWidth - (uiInfo.uiDC.glconfig.vidHeight * (640.0f / 480.0f)));",
		"uiInfo.uiDC.xscale = uiInfo.uiDC.yscale;",
		"uiInfo.uiDC.xscale = uiInfo.uiDC.glconfig.vidWidth * (1.0f / 640.0f);",
	):
		assert expected in block


def test_ui_shared_widescreen_rect_flow_retargets_centered_ui_scale() -> None:
	source = UI_SHARED.read_text(encoding="utf-8")
	apply_block = _block_from_marker(source, "static void UI_ApplyWidescreenRect(rectDef_t *rect, int widescreen)")
	normalize_block = _block_from_marker(source, "static void UI_NormalizeFullscreenBackgroundRect(rectDef_t *rect)")
	paint_block = _block_from_marker(source, "void Menu_Paint(menuDef_t *menu, qboolean forcePaint)")

	for expected in (
		"if (DC->bias <= 0.0f) {",
		"fullXScale = (float)DC->glconfig.vidWidth / (float)SCREEN_WIDTH;",
		"biasVirtual = DC->bias / DC->xscale;",
		"stretchRatio = fullXScale / DC->xscale;",
		"rect->x -= biasVirtual;",
		"rect->x += biasVirtual;",
		"rect->x = (rect->x * stretchRatio) - biasVirtual;",
		"rect->w *= stretchRatio;",
	):
		assert expected in apply_block

	for expected in (
		"#define UI_FULLSCREEN_BACKGROUND_WIDTH\t1920.0f",
		"#define UI_FULLSCREEN_BACKGROUND_HEIGHT\t1080.0f",
		"rect->x *= (float)SCREEN_WIDTH / UI_FULLSCREEN_BACKGROUND_WIDTH;",
		"rect->y *= (float)SCREEN_HEIGHT / UI_FULLSCREEN_BACKGROUND_HEIGHT;",
		"rect->w *= (float)SCREEN_WIDTH / UI_FULLSCREEN_BACKGROUND_WIDTH;",
		"rect->h *= (float)SCREEN_HEIGHT / UI_FULLSCREEN_BACKGROUND_HEIGHT;",
	):
		assert expected in source
		assert expected in normalize_block or expected.startswith("#define")

	assert "UI_NormalizeFullscreenBackgroundRect(&backgroundRect);" in paint_block
	assert "UI_ApplyWidescreenRect(&backgroundRect, menu->widescreen);" in paint_block


def test_ui_text_alignment_retargets_local_stretch_anchors() -> None:
	source = UI_SHARED.read_text(encoding="utf-8")
	local_x_block = _block_from_marker(source, "static float UI_ApplyWidescreenLocalX")
	extents_block = _block_from_marker(source, "void Item_SetTextExtents(itemDef_t *item, int *width, int *height, const char *text)")
	auto_wrap_block = _block_from_marker(source, "void Item_Text_AutoWrapped_Paint(itemDef_t *item)")
	ownerdraw_block = _block_from_marker(source, "void Item_OwnerDraw_Paint(itemDef_t *item)")

	for expected in (
		"widescreen = UI_ResolveWidescreenMode(menu, item);",
		"if (widescreen != WIDESCREEN_STRETCH) {",
		"stretchRatio = fullXScale / DC->xscale;",
		"return x * stretchRatio;",
	):
		assert expected in local_x_block

	for expected in (
		"textAlignX = UI_ApplyWidescreenLocalX(menu, item, item->textalignx);",
		"item->textRect.x = textAlignX;",
		"item->textRect.x = textAlignX - originalWidth;",
		"item->textRect.x = textAlignX - originalWidth / 2;",
	):
		assert expected in extents_block

	for expected in (
		"textAlignX = UI_ApplyWidescreenLocalX(menu, item, item->textalignx);",
		"item->textRect.x = textAlignX;",
		"item->textRect.x = textAlignX - newLineWidth;",
		"item->textRect.x = textAlignX - newLineWidth / 2;",
	):
		assert expected in auto_wrap_block

	assert "textAlignX = UI_ApplyWidescreenLocalX(parent, item, item->textalignx);" in ownerdraw_block


def test_cgame_public_and_local_headers_expose_bridge_imports() -> None:
	public_source = CG_PUBLIC.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")

	assert "#define CGAME_NATIVE_IMPORT_COUNT\tCG_QL_IMPORT_TOTAL_COUNT" in public_source

	for expected in (
		"CG_QL_IMPORT_DRAW_SCALED_TEXT = 123",
		"CG_QL_IMPORT_MEASURE_TEXT = 124",
		"CG_QL_IMPORT_TOTAL_COUNT",
	):
		assert expected in public_source

	for expected in (
		"CG_KEY_GETBINDINGBUF",
		"CG_KEY_SETBINDING",
		"CG_KEY_GETOVERSTRIKEMODE",
		"CG_KEY_SETOVERSTRIKEMODE",
		"CG_CMD_EXECUTETEXT",
		"CG_ADVERTISEMENTBRIDGE_INITCGAME",
		"CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME",
		"CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS",
		"CG_ADVERTISEMENTBRIDGE_SETFRAMETIME",
	):
		assert expected in public_source

	assert "CG_MEMSET = 100" in public_source

	for expected in (
		"void\t\ttrap_Key_GetBindingBuf( int keynum, char *buf, int buflen );",
		"void\t\ttrap_Key_SetBinding( int keynum, const char *binding );",
		"qboolean\ttrap_Key_GetOverstrikeMode( void );",
		"void\t\ttrap_Key_SetOverstrikeMode( qboolean state );",
		"void\t\ttrap_Cmd_ExecuteText( int exec_when, const char *text );",
		"void\t\ttrap_AdvertisementBridge_InitCGame( void );",
		"void\t\ttrap_AdvertisementBridge_ShutdownCGame( void );",
		"void\t\ttrap_AdvertisementBridge_UpdateLoadingViewParameters( void );",
		"void\t\ttrap_AdvertisementBridge_SetFrameTime( int frameTime );",
	):
		assert expected in local_source


def test_cgame_syscall_bridge_handles_binding_and_execute_ops() -> None:
	syscalls = CG_SYSCALLS.read_text(encoding="utf-8")
	client = CL_CGAME.read_text(encoding="utf-8")

	for expected in (
		"void trap_Cmd_ExecuteText( int exec_when, const char *text ) {",
		"syscall( CG_CMD_EXECUTETEXT, exec_when, text );",
		"void trap_Key_GetBindingBuf( int keynum, char *buf, int buflen ) {",
		"syscall( CG_KEY_GETBINDINGBUF, keynum, buf, buflen );",
		"void trap_Key_SetBinding( int keynum, const char *binding ) {",
		"syscall( CG_KEY_SETBINDING, keynum, binding );",
		"qboolean trap_Key_GetOverstrikeMode( void ) {",
		"return syscall( CG_KEY_GETOVERSTRIKEMODE ) ? qtrue : qfalse;",
		"void trap_Key_SetOverstrikeMode( qboolean state ) {",
		"syscall( CG_KEY_SETOVERSTRIKEMODE, state ? qtrue : qfalse );",
		"void trap_AdvertisementBridge_InitCGame( void ) {",
		"syscall( CG_ADVERTISEMENTBRIDGE_INITCGAME );",
		"void trap_AdvertisementBridge_ShutdownCGame( void ) {",
		"syscall( CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME );",
		"void trap_AdvertisementBridge_UpdateLoadingViewParameters( void ) {",
		"syscall( CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS );",
		"void trap_AdvertisementBridge_SetFrameTime( int frameTime ) {",
		"syscall( CG_ADVERTISEMENTBRIDGE_SETFRAMETIME, frameTime );",
	):
		assert expected in syscalls

	switch_block = _block_from_marker(client, "int CL_CgameSystemCalls")
	for expected in (
		"case CG_CMD_EXECUTETEXT:",
		"Cbuf_ExecuteText( args[1], VMA(2) );",
		"case CG_KEY_GETBINDINGBUF:",
		'Q_strncpyz( VMA(2), Key_GetBinding( args[1] ), args[3] );',
		"case CG_KEY_SETBINDING:",
		"Key_SetBinding( args[1], VMA(2) );",
		"case CG_KEY_GETOVERSTRIKEMODE:",
		"return Key_GetOverstrikeMode();",
		"case CG_KEY_SETOVERSTRIKEMODE:",
		"Key_SetOverstrikeMode( args[1] );",
		"case CG_ADVERTISEMENTBRIDGE_INITCGAME:",
		"CL_AdvertisementBridge_InitCGame();",
		"case CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME:",
		"CL_AdvertisementBridge_ShutdownCGame();",
		"case CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS:",
		"CL_AdvertisementBridge_UpdateLoadingViewParameters();",
		"case CG_ADVERTISEMENTBRIDGE_SETFRAMETIME:",
		"CL_AdvertisementBridge_SetFrameTime( args[1] );",
	):
		assert expected in switch_block


def test_native_import_table_keeps_new_cgame_bridge_callbacks() -> None:
	imports_source = QL_CGAME_IMPORTS.read_text(encoding="utf-8")
	client_source = CL_CGAME.read_text(encoding="utf-8")

	for expected in (
		"static void QDECL QL_CG_trap_Cmd_ExecuteText( int exec_when, const char *text ) {",
		"CG_Import_Syscall( CG_CMD_EXECUTETEXT, exec_when, text );",
		"static void QDECL QL_CG_trap_Key_GetBindingBuf( int keynum, char *buf, int buflen ) {",
		"CG_Import_Syscall( CG_KEY_GETBINDINGBUF, keynum, buf, buflen );",
		"static void QDECL QL_CG_trap_Key_SetBinding( int keynum, const char *binding ) {",
		"CG_Import_Syscall( CG_KEY_SETBINDING, keynum, binding );",
		"static qboolean QDECL QL_CG_trap_Key_GetOverstrikeMode( void ) {",
		"return CG_Import_Syscall( CG_KEY_GETOVERSTRIKEMODE );",
		"static void QDECL QL_CG_trap_Key_SetOverstrikeMode( qboolean state ) {",
		"CG_Import_Syscall( CG_KEY_SETOVERSTRIKEMODE, state );",
		"static void QDECL QL_CG_trap_AdvertisementBridge_InitCGame( void ) {",
		"CG_Import_Syscall( CG_ADVERTISEMENTBRIDGE_INITCGAME );",
		"static void QDECL QL_CG_trap_AdvertisementBridge_ShutdownCGame( void ) {",
		"CG_Import_Syscall( CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME );",
		"static void QDECL QL_CG_trap_AdvertisementBridge_UpdateLoadingViewParameters( void ) {",
		"CG_Import_Syscall( CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS );",
		"static void QDECL QL_CG_trap_AdvertisementBridge_SetFrameTime( int frameTime ) {",
		"CG_Import_Syscall( CG_ADVERTISEMENTBRIDGE_SETFRAMETIME, frameTime );",
	):
		assert expected in imports_source

	for expected in (
		"static ql_import_f ql_cgame_imports[CGAME_NATIVE_IMPORT_COUNT] = {",
		"[CG_KEY_GETBINDINGBUF] = (ql_import_f)QL_CG_trap_Key_GetBindingBuf,",
		"[CG_KEY_SETBINDING] = (ql_import_f)QL_CG_trap_Key_SetBinding,",
		"[CG_KEY_GETOVERSTRIKEMODE] = (ql_import_f)QL_CG_trap_Key_GetOverstrikeMode,",
		"[CG_KEY_SETOVERSTRIKEMODE] = (ql_import_f)QL_CG_trap_Key_SetOverstrikeMode,",
		"[CG_CMD_EXECUTETEXT] = (ql_import_f)QL_CG_trap_Cmd_ExecuteText,",
		"[CG_ADVERTISEMENTBRIDGE_INITCGAME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_InitCGame,",
		"[CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_ShutdownCGame,",
		"[CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS] = (ql_import_f)QL_CG_trap_AdvertisementBridge_UpdateLoadingViewParameters,",
		"[CG_ADVERTISEMENTBRIDGE_SETFRAMETIME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_SetFrameTime,",
	):
		assert expected in client_source

	for expected in (
		"ql_cgame_imports[CG_QL_IMPORT_DRAW_SCALED_TEXT] = (ql_import_f)QL_CG_trap_DrawScaledText;",
		"ql_cgame_imports[CG_QL_IMPORT_MEASURE_TEXT] = (ql_import_f)QL_CG_trap_MeasureText;",
	):
		assert expected in client_source


def test_cgame_round_race_and_flag_ownerdraws_follow_retail_leaf_split() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	race_block = _block_from_marker(source, "static void CG_DrawRaceStatusAndTimes")
	round_timer_block = _block_from_marker(source, "static void CG_DrawRoundTimer")
	blue_flag_block = _block_from_marker(source, "static qboolean CG_ShowBlueTeamHasRedFlag")
	red_flag_block = _block_from_marker(source, "static qboolean CG_ShowRedTeamHasBlueFlag")
	visible_block = _block_from_marker(source, "qboolean CG_OwnerDrawVisible")

	for expected in (
		"if ( ownerDraw == CG_RACE_STATUS ) {",
		"text = CG_GetRaceStatusText();",
		"if ( ownerDraw != CG_RACE_TIMES ) {",
		"CG_RaceBuildTimesStrings( primary, sizeof( primary ), secondary, sizeof( secondary ) )",
		"CG_Text_Paint( rect->x, rect->y + rect->h + lineHeight, scale, color, secondary, 0, 0, textStyle );",
	):
		assert expected in race_block

	for expected in (
		"if ( cgs.matchRoundState != ROUNDSTATE_ACTIVE ) {",
		"if ( cgs.matchTimeoutActive ) {",
		"roundStartTime = CG_GetMatchRoundStartTime();",
		"roundTimeLimitSeconds = CG_GetRoundTimeLimitSeconds();",
		"remainingMilliseconds = roundTimeLimitSeconds * 1000 - cg.time + roundStartTime;",
		"if ( remainingMilliseconds <= 0 || remainingMilliseconds > 29999 ) {",
		"seconds = ( remainingMilliseconds + 500 ) / 1000;",
		'Q_strncpyz( buffer, CG_FormatMinutesSeconds( seconds ), sizeof( buffer ) );',
	):
		assert expected in round_timer_block

	assert "CG_DrawLevelTimer(" not in round_timer_block
	assert "CG_GetScoreboardTimerSeconds();" not in round_timer_block

	for expected in (
		"cgs.gametype != GT_CTF && cgs.gametype != GT_1FCTF && cgs.gametype != GT_ATTACK_DEFEND",
		"return ( cgs.redflag == FLAG_TAKEN || cgs.flagStatus == FLAG_TAKEN_RED ) ? qtrue : qfalse;",
	):
		assert expected in blue_flag_block

	for expected in (
		"cgs.gametype != GT_CTF && cgs.gametype != GT_1FCTF && cgs.gametype != GT_ATTACK_DEFEND",
		"return ( cgs.blueflag == FLAG_TAKEN || cgs.flagStatus == FLAG_TAKEN_BLUE ) ? qtrue : qfalse;",
	):
		assert expected in red_flag_block

	for expected in (
		"qboolean vis = qtrue;",
		"while ( flags ) {",
		"if (flags & (CG_SHOW_BLUE_TEAM_HAS_REDFLAG | CG_SHOW_RED_TEAM_HAS_BLUEFLAG)) {",
		"if (flags & CG_SHOW_BLUE_TEAM_HAS_REDFLAG && CG_ShowBlueTeamHasRedFlag()) {",
		"} else if (flags & CG_SHOW_RED_TEAM_HAS_BLUEFLAG && CG_ShowRedTeamHasBlueFlag()) {",
		"if ( flags & ( CG_SHOW_ANYTEAMGAME | UI_SHOW_ANYTEAMGAME ) ) {",
		"if (flags & (CG_SHOW_IF_LOADOUT_ENABLED | CG_SHOW_IF_LOADOUT_DISABLED |",
		"UI_SHOW_IF_LOADOUT_ENABLED | UI_SHOW_IF_LOADOUT_DISABLED)) {",
		"if (flags & (CG_SHOW_IF_WARMUP | CG_SHOW_IF_NOT_WARMUP |",
		"UI_SHOW_IF_WARMUP | UI_SHOW_IF_NOT_WARMUP)) {",
		"if ( ( flags & ( CG_SHOW_IF_WARMUP | UI_SHOW_IF_WARMUP ) ) && inWarmup ) {",
		"if ( ( flags & ( CG_SHOW_IF_NOT_WARMUP | UI_SHOW_IF_NOT_WARMUP ) ) && !inWarmup ) {",
		"if ( flags & CG_SHOW_IF_CHAT_VISIBLE ) {",
		"if ( flags & CG_SHOW_INTERMISSION ) {",
		"if ( flags & ( CG_SHOW_NOTINTERMISSION | UI_SHOW_IF_NOT_INTERMISSION ) ) {",
		"if ( flags & CG_SHOW_IF_PLYR_IS_ON_RED && playerTeam == TEAM_RED ) {",
		"if ( flags & CG_SHOW_IF_PLYR_IS_ON_BLUE && playerTeam == TEAM_BLUE ) {",
	):
		assert expected in visible_block

	for expected in (
		"case CG_RACE_STATUS:",
		"case CG_RACE_TIMES:",
		"CG_DrawRaceStatusAndTimes( &rect, scale, color, textStyle, ownerDraw );",
	):
		assert expected in source


def test_cgame_loaded_browser_menu_visibility_flags_are_backed_by_cgame() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	visible_block = _block_from_marker(source, "qboolean CG_OwnerDrawVisible")
	menu_files = (
		"intro.menu",
		"ingamescoreteam.menu",
		"ingamescorenoteam.menu",
		"endscoreteam.menu",
		"endscorenoteam.menu",
		"spectator.menu",
		"spectator_follow.menu",
		"comp_spectator.menu",
		"comp_spectator_follow.menu",
		"ingamestats.menu",
		"ingame_scoreboard_ffa.menu",
		"ingame_scoreboard_duel.menu",
		"ingame_scoreboard_race.menu",
		"ingame_scoreboard_tdm.menu",
		"ingame_scoreboard_ca.menu",
		"ingame_scoreboard_ctf.menu",
		"ingame_scoreboard_1fctf.menu",
		"ingame_scoreboard_har.menu",
		"ingame_scoreboard_ft.menu",
		"ingame_scoreboard_dom.menu",
		"ingame_scoreboard_ad.menu",
		"ingame_scoreboard_rr.menu",
		"end_scoreboard_ffa.menu",
		"end_scoreboard_duel.menu",
		"end_scoreboard_race.menu",
		"end_scoreboard_tdm.menu",
		"end_scoreboard_ca.menu",
		"end_scoreboard_ctf.menu",
		"end_scoreboard_1fctf.menu",
		"end_scoreboard_har.menu",
		"end_scoreboard_ft.menu",
		"end_scoreboard_dom.menu",
		"end_scoreboard_ad.menu",
		"end_scoreboard_rr.menu",
		"ingame.menu",
		"ingame_about.menu",
		"ingame_addbot.menu",
		"ingame_admin.menu",
		"ingame_callvote.menu",
		"ingame_controls.menu",
		"ingame_join.menu",
		"ingame_options.menu",
		"ingame_vote.menu",
		"hud.menu",
		"comp_hud.menu",
		"min_hud.menu",
	)
	flags: set[str] = set()

	for filename in menu_files:
		menu_source = (REPO_ROOT / "src" / "ui" / filename).read_text(encoding="utf-8")
		flags.update(re.findall(r"\bownerdrawflag2?\s+([A-Z0-9_]+)", menu_source))

	missing = sorted(flag for flag in flags if flag not in visible_block)
	assert not missing, f"loaded cgame browser menu flags lack CG_OwnerDrawVisible coverage: {missing}"

	assert "static void CG_DrawRaceStatus(" not in source
	assert "static void CG_DrawRaceTimes(" not in source


def test_cgame_objective_status_ownerdraws_use_shared_team_status_leaf() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	shader_block = _block_from_marker(source, "static qhandle_t CG_GetTeamFlagStatusShader")
	team_status_block = _block_from_marker(source, "static void CG_DrawTeamFlagOrBaseStatus")
	track_block = _block_from_marker(source, "static void CG_DrawObjectiveStatusTrack")
	ctf_strip_block = _block_from_marker(source, "static qboolean CG_DrawObjectiveStatusCtfFamilyStrip")
	oneflag_shader_block = _block_from_marker(source, "static qhandle_t CG_GetOneFlagStatusShader")
	oneflag_strip_block = _block_from_marker(source, "static qboolean CG_DrawObjectiveStatusOneFlagStrip")
	harvester_strip_block = _block_from_marker(source, "static qboolean CG_DrawObjectiveStatusHarvesterStrip")
	domination_strip_block = _block_from_marker(source, "static qboolean CG_DrawObjectiveStatusDominationStrip")
	strip_block = _block_from_marker(source, "static qboolean CG_DrawObjectiveStatusStrip")
	objective_label_block = _block_from_marker(source, "static qboolean CG_BuildObjectiveStatusLabel")
	objective_draw_block = _block_from_marker(source, "static void CG_DrawObjectiveStatus")

	for expected in (
		"if ( cgs.gametype == GT_HARVESTER && !baseStatus ) {",
		"return ( team == TEAM_RED ) ? cgs.media.redCubeIcon : cgs.media.blueCubeIcon;",
		"if ( cgs.gametype == GT_1FCTF ) {",
		"if ( team == TEAM_RED && cgs.flagStatus == FLAG_TAKEN_RED ) {",
		"return cgs.media.flagShader[3];",
		"if ( cgs.gametype != GT_CTF && cgs.gametype != GT_ATTACK_DEFEND && cgs.gametype != GT_OBELISK ) {",
		"status = ( team == TEAM_RED ) ? cgs.redflag : cgs.blueflag;",
		"if ( baseStatus && status != FLAG_ATBASE ) {",
		"return ( team == TEAM_RED ) ? cgs.media.redFlagShader[status] : cgs.media.blueFlagShader[status];",
	):
		assert expected in shader_block

	for expected in (
		"if ( shader && !baseStatus && cgs.gametype != GT_1FCTF ) {",
		"handle = CG_GetTeamFlagStatusShader( team, baseStatus );",
		"CG_DrawPic( rect->x, rect->y, rect->w, rect->h, handle );",
	):
		assert expected in team_status_block

	for expected in (
		"CG_FillRect( left, trackY, right - left, 2.0f, trackColor );",
		"CG_FillRect( centerX, rect->y + 2.0f, 2.0f, rect->h - 4.0f, dividerColor );",
	):
		assert expected in track_block

	for expected in (
		"if ( cgs.gametype != GT_CTF && cgs.gametype != GT_ATTACK_DEFEND && cgs.gametype != GT_OBELISK ) {",
		"redBaseShader = CG_GetTeamFlagStatusShader( TEAM_RED, qtrue );",
		"blueBaseShader = CG_GetTeamFlagStatusShader( TEAM_BLUE, qtrue );",
		"redFlagShader = CG_GetTeamFlagStatusShader( TEAM_RED, qfalse );",
		"blueFlagShader = CG_GetTeamFlagStatusShader( TEAM_BLUE, qfalse );",
		"CG_DrawObjectiveStatusTrack( rect, trackLeft, trackRight );",
		"CG_DrawPic( redMarkerX, markerY, markerSize, markerSize, redFlagShader );",
		"CG_DrawPic( blueMarkerX, markerY, markerSize, markerSize, blueFlagShader );",
	):
		assert expected in ctf_strip_block

	for expected in (
		"if ( cgs.flagStatus < FLAG_ATBASE || cgs.flagStatus > FLAG_DROPPED ) {",
		"return cgs.media.flagShader[shaderIndex];",
	):
		assert expected in oneflag_shader_block

	for expected in (
		"flagShader = CG_GetOneFlagStatusShader();",
		"redBaseShader = CG_GetTeamFlagStatusShader( TEAM_RED, qtrue );",
		"blueBaseShader = CG_GetTeamFlagStatusShader( TEAM_BLUE, qtrue );",
		"CG_DrawObjectiveStatusTrack( rect, leftIconX + iconSize + 6.0f, rightIconX - 6.0f );",
	):
		assert expected in oneflag_strip_block

	for expected in (
		"if ( !cgs.media.redCubeIcon && !cgs.media.blueCubeIcon ) {",
		"CG_DrawObjectiveStatusTrack( rect, rect->x + iconSize + 6.0f, rect->x + rect->w - iconSize - 6.0f );",
		"CG_DrawPic( rect->x, rect->y, iconSize, iconSize, cgs.media.redCubeIcon );",
		"CG_DrawPic( rect->x + rect->w - iconSize, rect->y, iconSize, iconSize, cgs.media.blueCubeIcon );",
	):
		assert expected in harvester_strip_block

	for expected in (
		"points[pointIndex] = cent;",
		"progressIndex = CG_ObjectiveStatusDominationProgressIndex( (float)cent->currentState.frame / 255.0f );",
		"shader = CG_ObjectiveStatusDominationSelectShader( captureIcon, distress, progressIndex );",
	):
		assert expected in domination_strip_block

	for expected in (
		"if ( CG_DrawObjectiveStatusCtfFamilyStrip( rect ) ) {",
		"if ( CG_DrawObjectiveStatusOneFlagStrip( rect ) ) {",
		"if ( CG_DrawObjectiveStatusHarvesterStrip( rect ) ) {",
		"return CG_DrawObjectiveStatusDominationStrip( rect );",
	):
		assert expected in strip_block

	for expected in (
		"if ( cgs.gametype == GT_ATTACK_DEFEND ) {",
		'Com_sprintf( buffer, bufferSize, "%s %s  %s %s",',
		"CG_GetTeamName( TEAM_RED ), CG_FlagStatusText( redStatus ),",
		"CG_GetTeamName( TEAM_BLUE ), CG_FlagStatusText( blueStatus ) );",
	):
		assert expected in objective_label_block

	assert "if ( CG_DrawObjectiveStatusStrip( rect ) ) {" in objective_draw_block
	assert "CG_BuildObjectiveStatusLabel( buffer, sizeof( buffer ) )" in objective_draw_block
	assert 'CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );' in objective_draw_block

	for expected in (
		"case CG_BLUE_FLAGSTATUS:",
		"CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_BLUE, qfalse, shader );",
		"case CG_RED_FLAGSTATUS:",
		"CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_RED, qfalse, shader );",
		"case CG_FLAG_STATUS:",
		"CG_DrawObjectiveStatus( &rect, scale, color, textStyle );",
		"case CG_RED_BASESTATUS:",
		"CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_RED, qtrue, shader );",
		"case CG_BLUE_BASESTATUS:",
		"CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_BLUE, qtrue, shader );",
	):
		assert expected in source

	assert "static void CG_DrawFlagStatusText(" not in source
	assert "static qboolean CG_BuildFlagStatusLabel(" not in source


def test_cgame_selected_player_and_placement_weapon_helpers_restore_retail_split() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	order_block = _block_from_marker(source, "void CG_CheckOrderPending()")
	selected_block = _block_from_marker(source, "static void CG_SetSelectedPlayerName()")
	next_block = _block_from_marker(source, "void CG_SelectNextPlayer()")
	prev_block = _block_from_marker(source, "void CG_SelectPrevPlayer()")
	weapon_block = _block_from_marker(source, "static weapon_t CG_GetPlacementMetricWeapon( int ownerDraw )")
	build_block = _block_from_marker(source, "static qboolean CG_BuildPlacementWeaponMetricText")

	for expected in (
		"if (cgs.gametype < GT_CTF) {",
		'trap_SendConsoleCommand( va( "teamtask %i\\n", cgs.currentOrder ) );',
		'trap_SendConsoleCommand( va( "cmd vsay_team %s\\n", p1 ) );',
		'trap_SendConsoleCommand( va( "cmd vtell %d %s\\n", sortedTeamPlayers[cg_currentSelectedPlayer.integer], p2 ) );',
		'trap_SendConsoleCommand(b);',
		"cgs.orderPending = qfalse;",
	):
		assert expected in order_block

	for expected in (
		'trap_Cvar_Set("cg_selectedPlayerName", ci->name);',
		'trap_Cvar_Set("cg_selectedPlayer", va("%d", sortedTeamPlayers[cg_currentSelectedPlayer.integer]));',
		"cgs.currentOrder = ci->teamTask;",
		'trap_Cvar_Set("cg_selectedPlayerName", "Everyone");',
	):
		assert expected in selected_block

	for expected in (
		"CG_CheckOrderPending();",
		"cg_currentSelectedPlayer.integer++;",
		"CG_SetSelectedPlayerName();",
	):
		assert expected in next_block

	for expected in (
		"CG_CheckOrderPending();",
		"cg_currentSelectedPlayer.integer--;",
		"CG_SetSelectedPlayerName();",
	):
		assert expected in prev_block

	for expected in (
		"if ( ownerDraw >= CG_2ND_PLYR_FRAGS_G && ownerDraw <= CG_2ND_PLYR_ACC_HMG ) {",
		"normalized = ownerDraw - ( CG_2ND_PLYR - CG_1ST_PLYR );",
		"case CG_1ST_PLYR_FRAGS_MG:",
		"case CG_1ST_PLYR_ACC_MG:",
		"return WP_MACHINEGUN;",
		"case CG_1ST_PLYR_FRAGS_CG:",
		"return WP_CHAINGUN;",
		"case CG_1ST_PLYR_FRAGS_NG:",
		"return WP_NAILGUN;",
		"case CG_1ST_PLYR_FRAGS_PL:",
		"return WP_PROX_LAUNCHER;",
		"case CG_1ST_PLYR_FRAGS_HMG:",
		"return WP_HEAVY_MACHINEGUN;",
		"return WP_NONE;",
	):
		assert expected in weapon_block

	for expected in (
		"weapon = CG_GetPlacementMetricWeapon( ownerDraw );",
		"if ( weapon == WP_NONE ) {",
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponFrags[weapon] );',
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponHits[weapon] );',
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponShots[weapon] );',
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponDamage[weapon] );',
		'shots = stats->weaponShots[weapon];',
		'hits = stats->weaponHits[weapon];',
	):
		assert expected in build_block
