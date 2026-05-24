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
BG_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "bg_public.h"
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
MENUDEF_H = REPO_ROOT / "src" / "ui" / "menudef.h"
INTRO_MENU = REPO_ROOT / "src" / "ui" / "intro.menu"
CGAME_GHIDRA_DECOMPILE = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "cgamex86"
	/ "decompile_top_functions.c"
)
QAGAME_GHIDRA_DECOMPILE = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "decompile_top_functions.c"
)
CGAME_HLIL = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "cgamex86.dll"
	/ "cgamex86.dll_hlil.txt"
)


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


def _text_between(source: str, start_marker: str, end_marker: str) -> str:
	start = source.index(start_marker)
	end = source.index(end_marker, start)
	return source[start:end]


def _menudef_ownerdraw_constants() -> dict[str, int]:
	menudef = MENUDEF_H.read_text(encoding="utf-8")
	constants: dict[str, int] = {}

	for match in re.finditer(
		r"#define\s+(CG_[A-Z0-9_]+|UI_ADVERT)\s+(0x[0-9a-fA-F]+|\d+)",
		menudef,
	):
		constants[match.group(1)] = int(match.group(2), 0)

	return constants


def _retail_cg_ownerdraw_case_values() -> set[int]:
	source = CGAME_GHIDRA_DECOMPILE.read_text(encoding="utf-8")
	start = source.index("void FUN_1003b0f0(")
	end = source.index("/* FUN_1003a1c0", start)
	block = source[start:end]

	return {
		int(match.group(1), 0)
		for match in re.finditer(r"case\s+(0x[0-9a-fA-F]+|\d+)\s*:", block)
	}


def _retail_cg_ownerdraw_cases_for_target(target: str) -> set[int]:
	source = CGAME_GHIDRA_DECOMPILE.read_text(encoding="utf-8")
	start = source.index("void FUN_1003b0f0(")
	end = source.index("/* FUN_1003a1c0", start)
	block = source[start:end]
	cases: set[int] = set()
	active_cases: list[int] = []

	for line in block.splitlines():
		match = re.match(r"\s*case\s+(0x[0-9a-fA-F]+|\d+)\s*:", line)
		if match:
			active_cases.append(int(match.group(1), 0))
			continue

		if target in line and active_cases:
			cases.update(active_cases)
			active_cases = []
			continue

		if re.match(r"\s*(break|return);", line):
			active_cases = []

	return cases


def _case_labels(block: str) -> list[str]:
	return re.findall(r"^\s*case\s+([A-Z0-9_]+)\s*:", block, flags=re.MULTILINE)


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
	weapon_strip_block = _block_from_marker(weapons_source, "static void CG_DrawWeaponSelectStrip")
	legacy_mode_block = _block_from_marker(weapons_source, "static int CG_GetLegacyWeaponBarWidescreenMode")
	legacy_draw_block = _block_from_marker(weapons_source, "static void CG_DrawLegacyWeaponSelect")
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

	assert "w = CG_Text_Width( name, 0.25f, 0 );" in weapon_strip_block
	assert "CG_DrawStrlen( name ) * BIGCHAR_WIDTH" not in weapon_strip_block
	assert "case 2:" in legacy_mode_block
	assert "return WIDESCREEN_RIGHT;" in legacy_mode_block
	assert "case 3:" in legacy_mode_block
	assert "return WIDESCREEN_CENTER;" in legacy_mode_block
	assert "return WIDESCREEN_LEFT;" in legacy_mode_block
	assert "CG_SetAdjustFrom640Mode( CG_GetLegacyWeaponBarWidescreenMode() );" in legacy_draw_block
	assert "CG_SetAdjustFrom640Mode( WIDESCREEN_STRETCH );" in legacy_draw_block
	assert legacy_draw_block.index("CG_DrawPic( x + selectX, y - 2.0f, 52.0f, 20.0f, selectionShader );") < legacy_draw_block.index("CG_DrawPic( x, y, 16.0f, 16.0f, cg_weapons[weapon].weaponIcon );")
	assert legacy_draw_block.index("CG_DrawPic( x, y, 16.0f, 16.0f, cg_weapons[weapon].weaponIcon );") < legacy_draw_block.index("CG_DrawLegacyWeaponBarAmmo( x, y, ammoX, infiniteAmmoX, weapon );")

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


def test_grenade_missile_model_uses_weapon_color_entity_lane() -> None:
	ents_source = CG_ENTS.read_text(encoding="utf-8")
	main_source = CG_MAIN.read_text(encoding="utf-8")
	unpack_block = _block_from_marker(main_source, "static void CG_UnpackWeaponBarColor")
	parse_block = _block_from_marker(main_source, "static qboolean CG_ParseWeaponBarColor")
	color_block = _block_from_marker(ents_source, "static void CG_ApplyGrenadeEntityColor")
	missile_block = _block_from_marker(ents_source, "static void CG_Missile")

	for expected in (
		"color[0] = (float)( ( packedColor >> 24 ) & 0xff ) / 255.0f;",
		"color[1] = (float)( ( packedColor >> 16 ) & 0xff ) / 255.0f;",
		"color[2] = (float)( ( packedColor >> 8 ) & 0xff ) / 255.0f;",
		"color[3] = (float)( packedColor & 0xff ) / 255.0f;",
	):
		assert expected in unpack_block

	assert "packedColor = (unsigned int)strtoul( hex, &endPtr, 0 );" in parse_block
	assert "CG_UnpackWeaponBarColor( packedColor, color );" in parse_block

	for expected in (
		"ent->shaderRGBA[0] = (byte)( Com_Clamp( 0.0f, 1.0f, cg.weaponBarGrenadeColor[0] ) * 255.0f );",
		"ent->shaderRGBA[1] = (byte)( Com_Clamp( 0.0f, 1.0f, cg.weaponBarGrenadeColor[1] ) * 255.0f );",
		"ent->shaderRGBA[2] = (byte)( Com_Clamp( 0.0f, 1.0f, cg.weaponBarGrenadeColor[2] ) * 255.0f );",
		"ent->shaderRGBA[3] = (byte)( Com_Clamp( 0.0f, 1.0f, cg.weaponBarGrenadeColor[3] ) * 255.0f );",
	):
		assert expected in color_block

	assert "if ( cent->currentState.weapon == WP_GRENADE_LAUNCHER ) {" in missile_block
	assert "CG_ApplyGrenadeEntityColor( &ent );" in missile_block
	assert missile_block.index("ent.renderfx = weapon->missileRenderfx | RF_NOSHADOW;") < missile_block.index("CG_ApplyGrenadeEntityColor( &ent );")
	assert missile_block.index("CG_ApplyGrenadeEntityColor( &ent );") < missile_block.index("VectorNormalize2( s1->pos.trDelta, ent.axis[0] )")


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
	ghidra_source = CGAME_GHIDRA_DECOMPILE.read_text(encoding="utf-8")
	event_source = CG_EVENT.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	scoreboard_source = CG_SCOREBOARD.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	draw_block = _block_from_marker(newdraw_source, "static void CG_DrawOvertime")
	ownerdraw_block = _block_from_marker(newdraw_source, "void CG_OwnerDraw(")
	retail_ownerdraw_block = _block_from_marker(ghidra_source, "void FUN_1003b0f0(")
	scoreboard_block = _block_from_marker(scoreboard_source, "static void CG_UpdateHudScoreboardBanners( void )")
	constants = _menudef_ownerdraw_constants()

	assert "int CG_GetOvertimeCount( void );" in local_source
	assert "int CG_GetOvertimeCount( void ) {" in event_source
	assert _retail_cg_ownerdraw_cases_for_target("FUN_10030d20") == {
		constants["CG_OVERTIME"],
	}

	for expected in (
		"overtimeCount = CG_GetOvertimeCount();",
		'Com_sprintf( buffer, sizeof( buffer ), "Overtime x%i", overtimeCount );',
		'Q_strncpyz( buffer, "Overtime", sizeof( buffer ) );',
	):
		assert expected in draw_block

	assert 'CG_Text_Paint(rect->x, rect->y, scale, color, buffer, 0, 0, textStyle);' in draw_block
	assert "if ( cgHudScoreboard.overtimeCount > 1 ) {" in scoreboard_block
	assert "case 0xf:" in retail_ownerdraw_block
	assert "if (DAT_10ab8f4c == 0) {" in retail_ownerdraw_block
	assert "FUN_10030d20(param_13,param_14,param_16,param_10);" in retail_ownerdraw_block

	start = ownerdraw_block.index("case CG_OVERTIME:")
	end = ownerdraw_block.index("break;", start)
	overtime_case = ownerdraw_block[start:end]
	assert "if ( cg.warmup == 0 ) {" in overtime_case
	assert "CG_DrawOvertime(&rect, scale, color, textStyle);" in overtime_case


def test_cgame_ownerdraw_width_callback_matches_retail_hlil_surface() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
	retail_width_block = _text_between(
		hlil_source,
		"10028d80    int32_t sub_10028d80",
		"10028e80    int32_t sub_10028e80",
	)

	for expected in (
		"switch (arg1 + &jump_table_10028e30[4])",
		'ecx_1 = "Unknown Gametype"',
		"eax_4, ecx = sub_10034b30()",
		"eax_4, ecx = sub_10034a00()",
		'eax_4, ecx = sub_100575e0("Fragged by %s")',
		"return 0",
	):
		assert expected in retail_width_block

	assert set(_case_labels(width_block)) == {
		"CG_GAME_TYPE",
		"CG_GAME_STATUS",
		"CG_MATCH_STATUS",
		"CG_KILLER",
	}

	for expected in (
		"return CG_Text_Width( CG_GameTypeString(), scale, 0 );",
		"return CG_Text_Width( CG_GetGameStatusText(), scale, 0 );",
		"return CG_Text_Width( CG_GetMatchStatusText(), scale, 0 );",
		"return CG_Text_Width( CG_GetKillerText(), scale, 0 );",
		"return 0;",
	):
		assert expected in width_block

	for stale in (
		"CG_LEVELTIMER",
		"CG_ROUNDTIMER",
		"CG_OVERTIME",
		"CG_ROUND",
		"CG_HEALTH_COLORIZED",
		"CG_1ST_PLYR_HEALTH_ARMOR",
		"CG_RACE_STATUS",
		"CG_RACE_TIMES",
		"CG_RED_NAME",
		"CG_BLUE_NAME",
	):
		assert stale not in width_block

	assert "static int CG_LevelTimerWidth" not in main_source
	assert "static int CG_RoundLabelWidth" not in main_source
	assert "const char *CG_GetMatchStatusText( void );" in local_source
	assert "const char *CG_GetMatchStatusText( void )" in newdraw_source
	assert "static const char *CG_GetMatchStatusText" not in newdraw_source


def test_cgame_match_status_ownerdrawtype_wiring_matches_retail_dispatch() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	ui_shared_source = UI_SHARED.read_text(encoding="utf-8")
	menudef_source = MENUDEF_H.read_text(encoding="utf-8")
	intro_source = INTRO_MENU.read_text(encoding="utf-8")
	ghidra_source = CGAME_GHIDRA_DECOMPILE.read_text(encoding="utf-8")
	ownerdraw_block = _block_from_marker(newdraw_source, "void CG_OwnerDraw(")
	width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
	display_context_block = _block_from_marker(main_source, "static void CG_InitDisplayContext")
	item_ownerdraw_parse_block = _block_from_marker(ui_shared_source, "qboolean ItemParse_ownerdraw( itemDef_t")
	retail_ownerdraw_block = _block_from_marker(ghidra_source, "void FUN_1003b0f0")

	assert re.search(r"#define\s+CG_MATCH_STATUS\s+10\b", menudef_source)
	assert '#include "ui/menudef.h"' in intro_source
	assert re.search(r"\bownerdraw\s+CG_MATCH_STATUS\b", intro_source)

	for expected in (
		"case 10:",
		"FUN_10034cc0(param_13,param_14,param_16,param_10);",
	):
		assert expected in retail_ownerdraw_block

	for expected in (
		"case CG_MATCH_STATUS:",
		"CG_DrawMatchStatus( &rect, scale, color, textStyle, align );",
	):
		assert expected in ownerdraw_block

	for expected in (
		"case CG_MATCH_STATUS:",
		"return CG_Text_Width( CG_GetMatchStatusText(), scale, 0 );",
	):
		assert expected in width_block

	for expected in (
		"cgDC.ownerDrawItem = &CG_OwnerDraw;",
		"cgDC.ownerDrawVisible = &CG_OwnerDrawVisible;",
		"cgDC.ownerDrawWidth = &CG_OwnerDrawWidth;",
	):
		assert expected in display_context_block

	assert "PC_Int_Parse(handle, &item->window.ownerDraw)" in item_ownerdraw_parse_block
	assert "item->type = ITEM_TYPE_OWNERDRAW;" in item_ownerdraw_parse_block
	assert '{"ownerdraw", ItemParse_ownerdraw, NULL}' in ui_shared_source


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
	assert "if ( cg.accRequestTime + 1000 < cg.time ) {" in acc_down_block
	assert "cg.accRequestTime = cg.time;" in acc_down_block
	assert 'trap_SendClientCommand( "acc" );' in acc_down_block
	assert "cg.accRequestTime = 0;" not in acc_down_block
	assert "cg.accRequestActive = qfalse;" in acc_up_block
	assert 'trap_SendClientCommand( "pstats" );' in pstats_down_block
	assert "cg_pstatsRequestActive = qtrue;" in pstats_down_block
	assert "cg_pstatsRequestActive = qfalse;" in pstats_up_block

	for expected in (
		"static const weapon_t cgVerticalAccWeaponOrder[] = {",
		"WP_GAUNTLET,",
		"WP_MACHINEGUN,",
		"WP_BFG,",
		"WP_HEAVY_MACHINEGUN",
	):
		assert expected in newdraw_source
	vertical_order_block = _block_from_marker(newdraw_source, "static const weapon_t cgVerticalAccWeaponOrder[] = {")
	assert "WP_GAUNTLET,\n\tWP_MACHINEGUN," in vertical_order_block
	assert "WP_GRAPPLING_HOOK" not in vertical_order_block

	assert "if ( !cg.accRequestActive || !cg.snap ) {" in draw_gate_block
	assert "cg.snap->ps.pm_type == PM_SPECTATOR" in draw_gate_block
	assert "cg.snap->ps.pm_flags & PMF_FOLLOW" in draw_gate_block
	assert 'trap_SendClientCommand( "acc" );' in draw_gate_block

	assert "CG_ShouldDrawAccVertical()" not in draw_weapon_block
	assert "CG_ShouldDrawAccVertical()" not in draw_acc_block
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
	spectator_info_block = _block_from_marker(source, "static const clientInfo_t *CG_SpectatorClientInfo")
	spectator_score_block = _block_from_marker(source, "static const score_t *CG_SpectatorClientScore")
	name_text_block = _block_from_marker(source, "static qboolean CG_BuildSpectatorPlayerNameText")
	name_block = _block_from_marker(source, "static void CG_DrawSpectatorPlayerName")
	score_draw_block = _block_from_marker(source, "static void CG_DrawSpectatorPlayerScore")
	slot_block = _block_from_marker(source, "static int CG_GetSpectatorOwnerDrawSlot")
	flag_shader_block = _block_from_marker(source, "static qhandle_t CG_GetPlacementFlagShader")
	flag_block = _block_from_marker(source, "static void CG_DrawPlacementFlagOwnerDraw")
	avatar_block = _block_from_marker(source, "static void CG_DrawPlacementAvatarOwnerDraw")
	profile_block = _block_from_marker(source, "static void CG_DrawSpectatorProfileImage")
	comparison_block = _block_from_marker(source, "static void CG_DrawSpectatorComparison")
	stats_block = _block_from_marker(source, "static const cgScoreStats_t *CG_GetPlacementScoreStats")
	frags_block = _block_from_marker(source, "static qboolean CG_DrawPlacementFragsOwnerDraw")
	deaths_block = _block_from_marker(source, "static qboolean CG_DrawPlacementDeathsOwnerDraw")
	damage_block = _block_from_marker(source, "static qboolean CG_DrawPlacementDamageOwnerDraw")
	wins_block = _block_from_marker(source, "static qboolean CG_DrawPlacementWinsOwnerDraw")
	build_metric_block = _block_from_marker(source, "static qboolean CG_BuildPlacementMetricText")
	draw_metric_block = _block_from_marker(source, "static qboolean CG_DrawPlacementMetricOwnerDraw")

	for block in (spectator_info_block, spectator_score_block, stats_block):
		assert "clientNum < 0 || clientNum >= cgs.maxclients || clientNum >= MAX_CLIENTS" in block or (
			"score->client < 0 || score->client >= cgs.maxclients || score->client >= MAX_CLIENTS" in block
		)

	for expected in (
		"Q_strncpyz( nameBuffer, cgs.firstPlaceName, nameBufferSize );",
		"Q_strncpyz( nameBuffer, cgs.secondPlaceName, nameBufferSize );",
		"if ( cgs.gametype == GT_TOURNAMENT && !nameBuffer[0] ) {",
		'Q_strncpyz( nameBuffer, "-", nameBufferSize );',
		"if ( CG_Text_Width( nameBuffer, scale, 0 ) <= 140 ) {",
		"if ( CG_Text_Width( truncated, scale, 0 ) < 132 ) {",
		'Com_sprintf( nameBuffer, nameBufferSize, "%s...", truncated );',
	):
		assert expected in name_text_block

	for expected in (
		"if ( !rect || !CG_BuildSpectatorPlayerNameText( slot, scale, nameBuffer, sizeof( nameBuffer ) ) ) {",
		"CG_AlignTextX( &x, nameBuffer, scale, align );",
		"CG_Text_Paint( x, rect->y, scale, color, nameBuffer, 0, 0, textStyle );",
	):
		assert expected in name_block

	for expected in (
		"score = ( slot == 0 ) ? cgs.scores1 : cgs.scores2;",
		"if ( score == SCORE_NOT_PRESENT || score == CG_SCORE_FORFEIT ) {",
		'Q_strncpyz( buffer, "-", sizeof( buffer ) );',
		'Com_sprintf( buffer, sizeof( buffer ), "%d", score );',
		"CG_AlignTextX( &x, buffer, scale, align );",
		"CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );",
	):
		assert expected in score_draw_block
	assert "if ( !rect || !cg_drawProfileImages.integer ) {" in profile_block
	assert "if ( !rect ) {" in comparison_block

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

	for block in (frags_block, deaths_block, damage_block, wins_block):
		assert "if ( !rect ) {" in block

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
		"if ( !rect || !CG_ResolvePlacementMetricOwnerDraw( ownerDraw, &slot, &normalized ) ) {",
		"score = CG_GetPlacementScore( slot );",
		"ci = CG_GetPlacementClientInfo( score );",
		"CG_BuildPlacementMetricText( normalized, score, ci, buffer, sizeof( buffer ) )",
		"CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );",
	):
		assert expected in text_block

	for expected in (
		"if ( !rect || !CG_ResolvePlacementMetricOwnerDraw( ownerDraw, &slot, NULL ) ) {",
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
		"if ( !rect || !CG_IsRetailPlacementMetricOwnerDraw( ownerDraw ) ) {",
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


def test_cgame_placement_metric_target_groups_match_retail_ownerdraw_switch() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	constants = _menudef_ownerdraw_constants()
	guard_block = _block_from_marker(source, "static qboolean CG_IsRetailPlacementMetricOwnerDraw")
	build_block = _block_from_marker(source, "static qboolean CG_BuildPlacementMetricText")
	dispatch_block = _block_from_marker(source, "static qboolean CG_DrawPlacementMetricOwnerDraw")
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	all_weapons = ("G", "MG", "SG", "GL", "RL", "LG", "RG", "PG", "BFG", "CG", "NG", "PL", "HMG")
	non_gauntlet_weapons = all_weapons[1:]

	def values(names: set[str]) -> set[int]:
		return {constants[name] for name in names}

	def weapon_names(metric: str, weapons: tuple[str, ...]) -> set[str]:
		return {
			f"CG_{slot}_PLYR_{metric}_{weapon}"
			for slot in ("1ST", "2ND")
			for weapon in weapons
		}

	simple_target_groups = {
		"FUN_10035bd0": {"CG_1ST_PLYR", "CG_2ND_PLYR"},
		"FUN_10037ba0": {"CG_1ST_PLYR_READY"},
		"FUN_10035f30": {"CG_1ST_PLYR_SCORE", "CG_2ND_PLYR_SCORE"},
		"FUN_100361f0": {"CG_1ST_PLYR_FRAGS", "CG_2ND_PLYR_FRAGS"},
		"FUN_10036320": {"CG_1ST_PLYR_DEATHS", "CG_2ND_PLYR_DEATHS"},
		"FUN_10036770": {"CG_1ST_PLYR_DMG", "CG_2ND_PLYR_DMG"},
		"FUN_10036070": {"CG_1ST_PLYR_PING", "CG_2ND_PLYR_PING"},
		"FUN_10036450": {"CG_1ST_PLYR_WINS", "CG_2ND_PLYR_WINS"},
		"FUN_10036570": {"CG_1ST_PLYR_ACC", "CG_2ND_PLYR_ACC"},
		"FUN_10036720": {"CG_1ST_PLYR_FLAG", "CG_2ND_PLYR_FLAG"},
		"FUN_100366a0": {"CG_1ST_PLYR_AVATAR", "CG_2ND_PLYR_AVATAR"},
		"FUN_10033040": {"CG_1ST_PLYR_HEALTH_ARMOR", "CG_2ND_PLYR_HEALTH_ARMOR"},
		"FUN_10037d60": {"CG_2ND_PLYR_READY"},
	}

	for target, names in simple_target_groups.items():
		assert _retail_cg_ownerdraw_cases_for_target(target) == values(names)

	assert _retail_cg_ownerdraw_cases_for_target("FUN_100368a0") == values(weapon_names("FRAGS", all_weapons))
	assert _retail_cg_ownerdraw_cases_for_target("FUN_100369d0") == values(weapon_names("HITS", non_gauntlet_weapons))
	assert _retail_cg_ownerdraw_cases_for_target("FUN_10036b00") == values(weapon_names("SHOTS", non_gauntlet_weapons))
	assert _retail_cg_ownerdraw_cases_for_target("FUN_10036c30") == values(weapon_names("DMG", all_weapons))
	assert _retail_cg_ownerdraw_cases_for_target("FUN_10036d60") == values(weapon_names("ACC", non_gauntlet_weapons))
	assert _retail_cg_ownerdraw_cases_for_target("FUN_10036eb0") == values({
		"CG_1ST_PLYR_PICKUPS",
		"CG_1ST_PLYR_PICKUPS_RA",
		"CG_1ST_PLYR_PICKUPS_YA",
		"CG_1ST_PLYR_PICKUPS_GA",
		"CG_1ST_PLYR_PICKUPS_MH",
		"CG_2ND_PLYR_PICKUPS",
		"CG_2ND_PLYR_PICKUPS_RA",
		"CG_2ND_PLYR_PICKUPS_YA",
		"CG_2ND_PLYR_PICKUPS_GA",
		"CG_2ND_PLYR_PICKUPS_MH",
	})
	assert _retail_cg_ownerdraw_cases_for_target("FUN_10037730") == values({
		"CG_1ST_PLYR_AVG_PICKUP_TIME_RA",
		"CG_1ST_PLYR_AVG_PICKUP_TIME_YA",
		"CG_1ST_PLYR_AVG_PICKUP_TIME_GA",
		"CG_1ST_PLYR_AVG_PICKUP_TIME_MH",
		"CG_2ND_PLYR_AVG_PICKUP_TIME_RA",
		"CG_2ND_PLYR_AVG_PICKUP_TIME_YA",
		"CG_2ND_PLYR_AVG_PICKUP_TIME_GA",
		"CG_2ND_PLYR_AVG_PICKUP_TIME_MH",
	})
	assert _retail_cg_ownerdraw_cases_for_target("FUN_10037990") == values({
		"CG_1ST_PLYR_EXCELLENT",
		"CG_1ST_PLYR_IMPRESSIVE",
		"CG_1ST_PLYR_HUMILIATION",
		"CG_2ND_PLYR_EXCELLENT",
		"CG_2ND_PLYR_IMPRESSIVE",
		"CG_2ND_PLYR_HUMILIATION",
	})

	assert set(_case_labels(guard_block)) == {
		"CG_1ST_PLYR_READY",
		"CG_2ND_PLYR_READY",
		"CG_1ST_PLYR_FRAGS",
		"CG_2ND_PLYR_FRAGS",
		"CG_1ST_PLYR_DEATHS",
		"CG_2ND_PLYR_DEATHS",
		"CG_1ST_PLYR_DMG",
		"CG_2ND_PLYR_DMG",
		"CG_1ST_PLYR_PING",
		"CG_2ND_PLYR_PING",
		"CG_1ST_PLYR_WINS",
		"CG_2ND_PLYR_WINS",
		"CG_1ST_PLYR_ACC",
		"CG_2ND_PLYR_ACC",
		"CG_1ST_PLYR_FLAG",
		"CG_2ND_PLYR_FLAG",
	}

	for expected in (
		"ownerDraw >= CG_1ST_PLYR_FRAGS_G && ownerDraw <= CG_1ST_PLYR_FRAGS_HMG",
		"ownerDraw >= CG_1ST_PLYR_HITS_MG && ownerDraw <= CG_1ST_PLYR_HITS_HMG",
		"ownerDraw >= CG_1ST_PLYR_SHOTS_MG && ownerDraw <= CG_1ST_PLYR_SHOTS_HMG",
		"ownerDraw >= CG_1ST_PLYR_DMG_G && ownerDraw <= CG_1ST_PLYR_DMG_HMG",
		"ownerDraw >= CG_1ST_PLYR_ACC_MG && ownerDraw <= CG_1ST_PLYR_ACC_HMG",
		"ownerDraw >= CG_1ST_PLYR_PICKUPS && ownerDraw <= CG_1ST_PLYR_PICKUPS_MH",
		"ownerDraw >= CG_1ST_PLYR_AVG_PICKUP_TIME_RA && ownerDraw <= CG_1ST_PLYR_AVG_PICKUP_TIME_MH",
		"ownerDraw >= CG_1ST_PLYR_EXCELLENT && ownerDraw <= CG_1ST_PLYR_HUMILIATION",
		"ownerDraw >= CG_2ND_PLYR_EXCELLENT && ownerDraw <= CG_2ND_PLYR_HUMILIATION",
	):
		assert expected in guard_block

	for direct_owner_draw in (
		"CG_1ST_PLYR_SCORE",
		"CG_2ND_PLYR_SCORE",
		"CG_1ST_PLYR_HEALTH_ARMOR",
		"CG_2ND_PLYR_HEALTH_ARMOR",
		"CG_1ST_PLYR_AVATAR",
		"CG_2ND_PLYR_AVATAR",
	):
		assert direct_owner_draw not in guard_block
		assert direct_owner_draw in ownerdraw_block

	for absent_owner_draw in (
		"CG_1ST_PLYR_TIME",
		"CG_2ND_PLYR_TIME",
		"CG_1ST_PLYR_TIMEOUT_COUNT",
		"CG_2ND_PLYR_TIMEOUT_COUNT",
		"CG_1ST_PLYR_PR",
		"CG_2ND_PLYR_PR",
		"CG_1ST_PLYR_TIER",
		"CG_2ND_PLYR_TIER",
	):
		assert absent_owner_draw not in guard_block
		assert absent_owner_draw not in build_block

	start = ownerdraw_block.index("case CG_1ST_PLYR_TIME:")
	end = ownerdraw_block.index("case CG_1ST_PLYR_HEALTH_ARMOR:", start)
	first_player_noop_block = ownerdraw_block[start:end]
	assert "case CG_1ST_PLYR_TIMEOUT_COUNT:" in first_player_noop_block
	assert "common no-op return target" in first_player_noop_block
	assert "return;" in first_player_noop_block

	assert "if ( !rect || !CG_IsRetailPlacementMetricOwnerDraw( ownerDraw ) ) {" in dispatch_block
	assert "CG_BuildPlacementProgressionMetricText" not in source


def test_cgame_first_player_weapon_frag_and_hit_slice_matches_retail_scorestats_wiring() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	constants = _menudef_ownerdraw_constants()
	weapon_block = _block_from_marker(source, "static weapon_t CG_GetPlacementMetricWeapon( int ownerDraw )")
	build_block = _block_from_marker(source, "static qboolean CG_BuildPlacementWeaponMetricText")
	dispatch_block = _block_from_marker(source, "static qboolean CG_DrawPlacementMetricOwnerDraw")
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	frags_slice = {
		"CG_1ST_PLYR_FRAGS_RL",
		"CG_1ST_PLYR_FRAGS_LG",
		"CG_1ST_PLYR_FRAGS_RG",
		"CG_1ST_PLYR_FRAGS_PG",
		"CG_1ST_PLYR_FRAGS_BFG",
		"CG_1ST_PLYR_FRAGS_CG",
		"CG_1ST_PLYR_FRAGS_NG",
		"CG_1ST_PLYR_FRAGS_PL",
		"CG_1ST_PLYR_FRAGS_HMG",
	}
	hits_slice = {
		"CG_1ST_PLYR_HITS_MG",
		"CG_1ST_PLYR_HITS_SG",
		"CG_1ST_PLYR_HITS_GL",
		"CG_1ST_PLYR_HITS_RL",
		"CG_1ST_PLYR_HITS_LG",
		"CG_1ST_PLYR_HITS_RG",
		"CG_1ST_PLYR_HITS_PG",
		"CG_1ST_PLYR_HITS_BFG",
		"CG_1ST_PLYR_HITS_CG",
		"CG_1ST_PLYR_HITS_NG",
		"CG_1ST_PLYR_HITS_PL",
	}

	assert {constants[name] for name in frags_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_100368a0")
	assert {constants[name] for name in hits_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_100369d0")

	for name in sorted(frags_slice | hits_slice):
		assert f"case {name}:" not in ownerdraw_block

	for expected in (
		"case CG_1ST_PLYR_FRAGS_RL:",
		"case CG_1ST_PLYR_HITS_RL:",
		"return WP_ROCKET_LAUNCHER;",
		"case CG_1ST_PLYR_FRAGS_LG:",
		"case CG_1ST_PLYR_HITS_LG:",
		"return WP_LIGHTNING;",
		"case CG_1ST_PLYR_FRAGS_RG:",
		"case CG_1ST_PLYR_HITS_RG:",
		"return WP_RAILGUN;",
		"case CG_1ST_PLYR_FRAGS_PG:",
		"case CG_1ST_PLYR_HITS_PG:",
		"return WP_PLASMAGUN;",
		"case CG_1ST_PLYR_FRAGS_BFG:",
		"case CG_1ST_PLYR_HITS_BFG:",
		"return WP_BFG;",
		"case CG_1ST_PLYR_FRAGS_CG:",
		"case CG_1ST_PLYR_HITS_CG:",
		"return WP_CHAINGUN;",
		"case CG_1ST_PLYR_FRAGS_NG:",
		"case CG_1ST_PLYR_HITS_NG:",
		"return WP_NAILGUN;",
		"case CG_1ST_PLYR_FRAGS_PL:",
		"case CG_1ST_PLYR_HITS_PL:",
		"return WP_PROX_LAUNCHER;",
		"case CG_1ST_PLYR_FRAGS_HMG:",
		"return WP_HEAVY_MACHINEGUN;",
	):
		assert expected in weapon_block

	for expected in (
		"if ( normalized >= CG_1ST_PLYR_FRAGS_G && normalized <= CG_1ST_PLYR_FRAGS_HMG ) {",
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponFrags[weapon] );',
		"if ( normalized >= CG_1ST_PLYR_HITS_MG && normalized <= CG_1ST_PLYR_HITS_HMG ) {",
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponHits[weapon] );',
		'Q_strncpyz( buffer, "-", bufferSize );',
	):
		assert expected in build_block

	for expected in (
		"CG_DrawPlacementWeaponFragsOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementWeaponHitsOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
	):
		assert expected in dispatch_block


def test_cgame_first_player_weapon_hit_shot_and_damage_slice_matches_retail_scorestats_wiring() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	constants = _menudef_ownerdraw_constants()
	weapon_block = _block_from_marker(source, "static weapon_t CG_GetPlacementMetricWeapon( int ownerDraw )")
	build_block = _block_from_marker(source, "static qboolean CG_BuildPlacementWeaponMetricText")
	dispatch_block = _block_from_marker(source, "static qboolean CG_DrawPlacementMetricOwnerDraw")
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	hits_slice = {"CG_1ST_PLYR_HITS_HMG"}
	shots_slice = {
		"CG_1ST_PLYR_SHOTS_MG",
		"CG_1ST_PLYR_SHOTS_SG",
		"CG_1ST_PLYR_SHOTS_GL",
		"CG_1ST_PLYR_SHOTS_RL",
		"CG_1ST_PLYR_SHOTS_LG",
		"CG_1ST_PLYR_SHOTS_RG",
		"CG_1ST_PLYR_SHOTS_PG",
		"CG_1ST_PLYR_SHOTS_BFG",
		"CG_1ST_PLYR_SHOTS_CG",
		"CG_1ST_PLYR_SHOTS_NG",
		"CG_1ST_PLYR_SHOTS_PL",
		"CG_1ST_PLYR_SHOTS_HMG",
	}
	damage_slice = {
		"CG_1ST_PLYR_DMG_G",
		"CG_1ST_PLYR_DMG_MG",
		"CG_1ST_PLYR_DMG_SG",
		"CG_1ST_PLYR_DMG_GL",
		"CG_1ST_PLYR_DMG_RL",
		"CG_1ST_PLYR_DMG_LG",
		"CG_1ST_PLYR_DMG_RG",
	}

	assert {constants[name] for name in hits_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_100369d0")
	assert {constants[name] for name in shots_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036b00")
	assert {constants[name] for name in damage_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036c30")

	for name in sorted(hits_slice | shots_slice | damage_slice):
		assert f"case {name}:" not in ownerdraw_block

	for expected in (
		"case CG_1ST_PLYR_HITS_HMG:",
		"case CG_1ST_PLYR_SHOTS_HMG:",
		"return WP_HEAVY_MACHINEGUN;",
		"case CG_1ST_PLYR_DMG_G:",
		"return WP_GAUNTLET;",
		"case CG_1ST_PLYR_SHOTS_MG:",
		"case CG_1ST_PLYR_DMG_MG:",
		"return WP_MACHINEGUN;",
		"case CG_1ST_PLYR_SHOTS_SG:",
		"case CG_1ST_PLYR_DMG_SG:",
		"return WP_SHOTGUN;",
		"case CG_1ST_PLYR_SHOTS_GL:",
		"case CG_1ST_PLYR_DMG_GL:",
		"return WP_GRENADE_LAUNCHER;",
		"case CG_1ST_PLYR_SHOTS_RL:",
		"case CG_1ST_PLYR_DMG_RL:",
		"return WP_ROCKET_LAUNCHER;",
		"case CG_1ST_PLYR_SHOTS_LG:",
		"case CG_1ST_PLYR_DMG_LG:",
		"return WP_LIGHTNING;",
		"case CG_1ST_PLYR_SHOTS_RG:",
		"case CG_1ST_PLYR_DMG_RG:",
		"return WP_RAILGUN;",
	):
		assert expected in weapon_block

	for expected in (
		"if ( normalized >= CG_1ST_PLYR_HITS_MG && normalized <= CG_1ST_PLYR_HITS_HMG ) {",
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponHits[weapon] );',
		"if ( normalized >= CG_1ST_PLYR_SHOTS_MG && normalized <= CG_1ST_PLYR_SHOTS_HMG ) {",
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponShots[weapon] );',
		"if ( normalized >= CG_1ST_PLYR_DMG_G && normalized <= CG_1ST_PLYR_DMG_HMG ) {",
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponDamage[weapon] );',
		'Q_strncpyz( buffer, "-", bufferSize );',
	):
		assert expected in build_block

	for expected in (
		"CG_DrawPlacementWeaponHitsOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementWeaponShotsOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementWeaponDamageOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
	):
		assert expected in dispatch_block


def test_cgame_first_player_weapon_damage_accuracy_and_pickup_slice_matches_retail_scorestats_wiring() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	constants = _menudef_ownerdraw_constants()
	weapon_block = _block_from_marker(source, "static weapon_t CG_GetPlacementMetricWeapon( int ownerDraw )")
	weapon_metric_block = _block_from_marker(source, "static qboolean CG_BuildPlacementWeaponMetricText")
	pickup_metric_block = _block_from_marker(source, "static qboolean CG_BuildPlacementPickupMetricText")
	dispatch_block = _block_from_marker(source, "static qboolean CG_DrawPlacementMetricOwnerDraw")
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	scorestats_block = _block_from_marker(servercmds_source, "static void CG_ParseScoreStats")
	duel_scores_block = _block_from_marker(servercmds_source, "static void CG_ParseDuelScores")
	damage_slice = {
		"CG_1ST_PLYR_DMG_PG",
		"CG_1ST_PLYR_DMG_BFG",
		"CG_1ST_PLYR_DMG_CG",
		"CG_1ST_PLYR_DMG_NG",
		"CG_1ST_PLYR_DMG_PL",
		"CG_1ST_PLYR_DMG_HMG",
	}
	accuracy_slice = {
		"CG_1ST_PLYR_ACC_MG",
		"CG_1ST_PLYR_ACC_SG",
		"CG_1ST_PLYR_ACC_GL",
		"CG_1ST_PLYR_ACC_RL",
		"CG_1ST_PLYR_ACC_LG",
		"CG_1ST_PLYR_ACC_RG",
		"CG_1ST_PLYR_ACC_PG",
		"CG_1ST_PLYR_ACC_BFG",
		"CG_1ST_PLYR_ACC_CG",
		"CG_1ST_PLYR_ACC_NG",
		"CG_1ST_PLYR_ACC_PL",
		"CG_1ST_PLYR_ACC_HMG",
	}
	pickup_slice = {
		"CG_1ST_PLYR_PICKUPS",
		"CG_1ST_PLYR_PICKUPS_RA",
	}

	assert {constants[name] for name in damage_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036c30")
	assert {constants[name] for name in accuracy_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036d60")
	assert {constants[name] for name in pickup_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036eb0")

	for name in sorted(damage_slice | accuracy_slice | pickup_slice):
		assert f"case {name}:" not in ownerdraw_block

	assert "weaponAccuracy[WP_NUM_WEAPONS];" in local_source
	assert "cg.scoreStats[clientNum].weaponAccuracy[weapon] = ( shots > 0 ) ? ( hits * 100 ) / shots : 0;" in scorestats_block
	assert "cg.scoreStats[clientNum].weaponAccuracy[weapon] =" in duel_scores_block
	assert "shots = cg.scoreStats[clientNum].weaponShots[weapon];" in duel_scores_block

	for expected in (
		"case CG_1ST_PLYR_DMG_PG:",
		"case CG_1ST_PLYR_ACC_PG:",
		"return WP_PLASMAGUN;",
		"case CG_1ST_PLYR_DMG_BFG:",
		"case CG_1ST_PLYR_ACC_BFG:",
		"return WP_BFG;",
		"case CG_1ST_PLYR_DMG_CG:",
		"case CG_1ST_PLYR_ACC_CG:",
		"return WP_CHAINGUN;",
		"case CG_1ST_PLYR_DMG_NG:",
		"case CG_1ST_PLYR_ACC_NG:",
		"return WP_NAILGUN;",
		"case CG_1ST_PLYR_DMG_PL:",
		"case CG_1ST_PLYR_ACC_PL:",
		"return WP_PROX_LAUNCHER;",
		"case CG_1ST_PLYR_DMG_HMG:",
		"case CG_1ST_PLYR_ACC_HMG:",
		"return WP_HEAVY_MACHINEGUN;",
	):
		assert expected in weapon_block

	for expected in (
		"if ( normalized >= CG_1ST_PLYR_DMG_G && normalized <= CG_1ST_PLYR_DMG_HMG ) {",
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponDamage[weapon] );',
		"if ( normalized >= CG_1ST_PLYR_ACC_MG && normalized <= CG_1ST_PLYR_ACC_HMG ) {",
		'Com_sprintf( buffer, bufferSize, "%i%%", stats->weaponAccuracy[weapon] );',
		"( hits * 100 ) / shots",
	):
		if expected == "( hits * 100 ) / shots":
			assert expected not in weapon_metric_block
		else:
			assert expected in weapon_metric_block

	for expected in (
		"CG_ResolvePlacementMetricOwnerDraw( ownerDraw, NULL, &normalized );",
		"if ( normalized == CG_1ST_PLYR_PICKUPS ) {",
		"for ( index = 0; index < CG_SCORESTAT_PICKUP_COUNT; index++ ) {",
		"total += stats->pickupCounts[index];",
		"if ( normalized >= CG_1ST_PLYR_PICKUPS_RA && normalized <= CG_1ST_PLYR_PICKUPS_MH ) {",
		"index = normalized - CG_1ST_PLYR_PICKUPS_RA;",
		'Com_sprintf( buffer, bufferSize, "%i", stats->pickupCounts[index] );',
	):
		assert expected in pickup_metric_block

	for expected in (
		"CG_DrawPlacementWeaponDamageOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementWeaponAccuracyOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementPickupCountOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
	):
		assert expected in dispatch_block


def test_cgame_first_player_pickup_average_awards_and_second_player_start_slice_matches_retail_wiring() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	constants = _menudef_ownerdraw_constants()
	resolve_block = _block_from_marker(source, "static qboolean CG_ResolvePlacementMetricOwnerDraw")
	pickup_metric_block = _block_from_marker(source, "static qboolean CG_BuildPlacementPickupMetricText")
	build_metric_block = _block_from_marker(source, "static qboolean CG_BuildPlacementMetricText")
	dispatch_block = _block_from_marker(source, "static qboolean CG_DrawPlacementMetricOwnerDraw")
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	secondary_status_block = _block_from_marker(source, "static void CG_DrawSpectatorSecondaryStatus")
	pickup_tail_slice = {
		"CG_1ST_PLYR_PICKUPS_YA",
		"CG_1ST_PLYR_PICKUPS_GA",
		"CG_1ST_PLYR_PICKUPS_MH",
	}
	pickup_average_slice = {
		"CG_1ST_PLYR_AVG_PICKUP_TIME_RA",
		"CG_1ST_PLYR_AVG_PICKUP_TIME_YA",
		"CG_1ST_PLYR_AVG_PICKUP_TIME_GA",
		"CG_1ST_PLYR_AVG_PICKUP_TIME_MH",
	}
	award_slice = {
		"CG_1ST_PLYR_EXCELLENT",
		"CG_1ST_PLYR_IMPRESSIVE",
		"CG_1ST_PLYR_HUMILIATION",
	}
	second_metric_slice = {
		"CG_2ND_PLYR_READY",
		"CG_2ND_PLYR_FRAGS",
		"CG_2ND_PLYR_DEATHS",
		"CG_2ND_PLYR_DMG",
		"CG_2ND_PLYR_PING",
	}
	no_retail_route_slice = {
		"CG_1ST_PLYR_PR",
		"CG_1ST_PLYR_TIER",
		"CG_2ND_PLYR_TIME",
	}

	assert {constants[name] for name in pickup_tail_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036eb0")
	assert {constants[name] for name in pickup_average_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10037730")
	assert {constants[name] for name in award_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10037990")
	assert {constants["CG_2ND_PLYR"]} <= _retail_cg_ownerdraw_cases_for_target("FUN_10035bd0")
	assert {constants["CG_2ND_PLYR_READY"]} <= _retail_cg_ownerdraw_cases_for_target("FUN_10037d60")
	assert {constants["CG_2ND_PLYR_SCORE"]} <= _retail_cg_ownerdraw_cases_for_target("FUN_10035f30")
	assert {constants["CG_2ND_PLYR_FRAGS"]} <= _retail_cg_ownerdraw_cases_for_target("FUN_100361f0")
	assert {constants["CG_2ND_PLYR_DEATHS"]} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036320")
	assert {constants["CG_2ND_PLYR_DMG"]} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036770")
	assert {constants["CG_2ND_PLYR_PING"]} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036070")

	for name in sorted(pickup_tail_slice | pickup_average_slice | award_slice | second_metric_slice):
		assert f"case {name}:" not in ownerdraw_block

	for name in sorted(no_retail_route_slice):
		assert f"case {name}:" not in ownerdraw_block
		assert name not in build_metric_block

	average_start = pickup_metric_block.index("if ( normalized >= CG_1ST_PLYR_AVG_PICKUP_TIME_RA")
	average_block = pickup_metric_block[average_start:]
	for expected in (
		"if ( normalized >= CG_1ST_PLYR_PICKUPS_RA && normalized <= CG_1ST_PLYR_PICKUPS_MH ) {",
		"index = normalized - CG_1ST_PLYR_PICKUPS_RA;",
		"if ( normalized >= CG_1ST_PLYR_AVG_PICKUP_TIME_RA && normalized <= CG_1ST_PLYR_AVG_PICKUP_TIME_MH ) {",
		"index = normalized - CG_1ST_PLYR_AVG_PICKUP_TIME_RA;",
		"if ( stats->pickupCounts[index] <= 0 ) {",
		"buffer[0] = '\\0';",
		'Com_sprintf( buffer, bufferSize, "%3.2f", stats->pickupAvgSeconds[index] );',
	):
		assert expected in pickup_metric_block
	assert 'Q_strncpyz( buffer, "-", bufferSize );' not in average_block

	for expected in (
		"case CG_1ST_PLYR_EXCELLENT:",
		'Com_sprintf( buffer, bufferSize, "%i", score->excellentCount );',
		"case CG_1ST_PLYR_IMPRESSIVE:",
		'Com_sprintf( buffer, bufferSize, "%i", score->impressiveCount );',
		"case CG_1ST_PLYR_HUMILIATION:",
		'Com_sprintf( buffer, bufferSize, "%i", score->guantletCount );',
	):
		assert expected in build_metric_block

	for expected in (
		"} else if ( ownerDraw >= CG_2ND_PLYR_READY && ownerDraw <= CG_2ND_PLYR_TIER ) {",
		"resolvedSlot = 1;",
		"resolvedOwnerDraw = ownerDraw - ( CG_2ND_PLYR - CG_1ST_PLYR );",
	):
		assert expected in resolve_block

	for expected in (
		"CG_DrawSpectatorStatusLabel( rect, 1 );",
		"if ( ownerDraw == CG_2ND_PLYR_READY ) {",
		"CG_DrawSpectatorSecondaryStatus( rect );",
		"if ( ownerDraw == CG_1ST_PLYR_PING || ownerDraw == CG_2ND_PLYR_PING ) {",
		"CG_DrawPlacementPingOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"return CG_DrawPlacementFragsOwnerDraw( rect, scale, color, textStyle, slot );",
		"return CG_DrawPlacementDeathsOwnerDraw( rect, scale, color, textStyle, slot );",
		"return CG_DrawPlacementDamageOwnerDraw( rect, scale, color, textStyle, slot );",
	):
		if expected == "CG_DrawSpectatorStatusLabel( rect, 1 );":
			assert expected in secondary_status_block
		else:
			assert expected in dispatch_block

	for expected in (
		"case CG_2ND_PLYR: {",
		"CG_DrawSpectatorPlayerName(&rect, scale, color, textStyle, 1, align);",
		"case CG_2ND_PLYR_SCORE:",
		"CG_DrawSpectatorPlayerScore(&rect, scale, color, textStyle, 1, align);",
	):
		assert expected in ownerdraw_block


def test_cgame_second_player_core_and_weapon_frag_slice_matches_retail_wiring() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	constants = _menudef_ownerdraw_constants()
	weapon_block = _block_from_marker(source, "static weapon_t CG_GetPlacementMetricWeapon( int ownerDraw )")
	weapon_metric_block = _block_from_marker(source, "static qboolean CG_BuildPlacementWeaponMetricText")
	guard_block = _block_from_marker(source, "static qboolean CG_IsRetailPlacementMetricOwnerDraw")
	dispatch_block = _block_from_marker(source, "static qboolean CG_DrawPlacementMetricOwnerDraw")
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	metric_slice = {
		"CG_2ND_PLYR_WINS",
		"CG_2ND_PLYR_ACC",
		"CG_2ND_PLYR_FLAG",
	}
	direct_widget_slice = {
		"CG_2ND_PLYR_AVATAR",
		"CG_2ND_PLYR_HEALTH_ARMOR",
	}
	frag_slice = {
		"CG_2ND_PLYR_FRAGS_G",
		"CG_2ND_PLYR_FRAGS_MG",
		"CG_2ND_PLYR_FRAGS_SG",
		"CG_2ND_PLYR_FRAGS_GL",
		"CG_2ND_PLYR_FRAGS_RL",
		"CG_2ND_PLYR_FRAGS_LG",
		"CG_2ND_PLYR_FRAGS_RG",
		"CG_2ND_PLYR_FRAGS_PG",
		"CG_2ND_PLYR_FRAGS_BFG",
		"CG_2ND_PLYR_FRAGS_CG",
		"CG_2ND_PLYR_FRAGS_NG",
		"CG_2ND_PLYR_FRAGS_PL",
		"CG_2ND_PLYR_FRAGS_HMG",
	}
	hit_slice = {"CG_2ND_PLYR_HITS_MG"}

	assert {constants["CG_2ND_PLYR_WINS"]} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036450")
	assert {constants["CG_2ND_PLYR_ACC"]} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036570")
	assert {constants["CG_2ND_PLYR_FLAG"]} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036720")
	assert {constants["CG_2ND_PLYR_AVATAR"]} <= _retail_cg_ownerdraw_cases_for_target("FUN_100366a0")
	assert {constants["CG_2ND_PLYR_HEALTH_ARMOR"]} <= _retail_cg_ownerdraw_cases_for_target("FUN_10033040")
	assert {constants[name] for name in frag_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_100368a0")
	assert {constants[name] for name in hit_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_100369d0")
	assert constants["CG_2ND_PLYR_TIMEOUT_COUNT"] not in _retail_cg_ownerdraw_case_values()

	for name in sorted(metric_slice | frag_slice | hit_slice):
		assert f"case {name}:" not in ownerdraw_block

	for expected in (
		"case CG_2ND_PLYR_AVATAR:",
		"CG_DrawPlacementAvatarOwnerDraw( &rect, 1 );",
		"case CG_2ND_PLYR_HEALTH_ARMOR:",
		"CG_DrawSpectatorComparison( &rect, scale, color, textStyle, ownerDraw );",
		"case CG_2ND_PLYR_TIMEOUT_COUNT:",
		"Retail has no raw ownerdraw 0xcd helper route.",
	):
		assert expected in ownerdraw_block

	for expected in (
		"case CG_2ND_PLYR_WINS:",
		"case CG_2ND_PLYR_ACC:",
		"case CG_2ND_PLYR_FLAG:",
		"ownerDraw >= CG_2ND_PLYR_FRAGS_G && ownerDraw <= CG_2ND_PLYR_FRAGS_HMG",
		"ownerDraw >= CG_2ND_PLYR_HITS_MG && ownerDraw <= CG_2ND_PLYR_HITS_HMG",
	):
		assert expected in guard_block

	for expected in (
		"if ( ownerDraw >= CG_2ND_PLYR_FRAGS_G && ownerDraw <= CG_2ND_PLYR_ACC_HMG ) {",
		"normalized = ownerDraw - ( CG_2ND_PLYR - CG_1ST_PLYR );",
		"case CG_1ST_PLYR_FRAGS_G:",
		"return WP_GAUNTLET;",
		"case CG_1ST_PLYR_FRAGS_MG:",
		"case CG_1ST_PLYR_HITS_MG:",
		"return WP_MACHINEGUN;",
		"case CG_1ST_PLYR_FRAGS_HMG:",
		"return WP_HEAVY_MACHINEGUN;",
	):
		assert expected in weapon_block

	for expected in (
		"if ( normalized >= CG_1ST_PLYR_FRAGS_G && normalized <= CG_1ST_PLYR_FRAGS_HMG ) {",
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponFrags[weapon] );',
		"if ( normalized >= CG_1ST_PLYR_HITS_MG && normalized <= CG_1ST_PLYR_HITS_HMG ) {",
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponHits[weapon] );',
	):
		assert expected in weapon_metric_block

	for expected in (
		"if ( ownerDraw == CG_1ST_PLYR_ACC || ownerDraw == CG_2ND_PLYR_ACC ) {",
		"CG_DrawPlacementAccuracyOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementWeaponFragsOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementWeaponHitsOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"return CG_DrawPlacementWinsOwnerDraw( rect, scale, color, textStyle, slot );",
		"CG_DrawPlacementFlagOwnerDraw( rect, slot );",
	):
		assert expected in dispatch_block


def test_cgame_second_player_weapon_hit_tail_and_shot_head_slice_matches_retail_wiring() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	constants = _menudef_ownerdraw_constants()
	weapon_block = _block_from_marker(source, "static weapon_t CG_GetPlacementMetricWeapon( int ownerDraw )")
	weapon_metric_block = _block_from_marker(source, "static qboolean CG_BuildPlacementWeaponMetricText")
	dispatch_block = _block_from_marker(source, "static qboolean CG_DrawPlacementMetricOwnerDraw")
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	hit_slice = {
		"CG_2ND_PLYR_HITS_SG",
		"CG_2ND_PLYR_HITS_GL",
		"CG_2ND_PLYR_HITS_RL",
		"CG_2ND_PLYR_HITS_LG",
		"CG_2ND_PLYR_HITS_RG",
		"CG_2ND_PLYR_HITS_PG",
		"CG_2ND_PLYR_HITS_BFG",
		"CG_2ND_PLYR_HITS_CG",
		"CG_2ND_PLYR_HITS_NG",
		"CG_2ND_PLYR_HITS_PL",
		"CG_2ND_PLYR_HITS_HMG",
	}
	shot_slice = {
		"CG_2ND_PLYR_SHOTS_MG",
		"CG_2ND_PLYR_SHOTS_SG",
		"CG_2ND_PLYR_SHOTS_GL",
		"CG_2ND_PLYR_SHOTS_RL",
		"CG_2ND_PLYR_SHOTS_LG",
		"CG_2ND_PLYR_SHOTS_RG",
		"CG_2ND_PLYR_SHOTS_PG",
		"CG_2ND_PLYR_SHOTS_BFG",
		"CG_2ND_PLYR_SHOTS_CG",
	}

	assert {constants[name] for name in hit_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_100369d0")
	assert {constants[name] for name in shot_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036b00")

	for name in sorted(hit_slice | shot_slice):
		assert f"case {name}:" not in ownerdraw_block

	for expected in (
		"if ( ownerDraw >= CG_2ND_PLYR_FRAGS_G && ownerDraw <= CG_2ND_PLYR_ACC_HMG ) {",
		"normalized = ownerDraw - ( CG_2ND_PLYR - CG_1ST_PLYR );",
		"case CG_1ST_PLYR_HITS_SG:",
		"case CG_1ST_PLYR_SHOTS_SG:",
		"return WP_SHOTGUN;",
		"case CG_1ST_PLYR_HITS_GL:",
		"case CG_1ST_PLYR_SHOTS_GL:",
		"return WP_GRENADE_LAUNCHER;",
		"case CG_1ST_PLYR_HITS_RL:",
		"case CG_1ST_PLYR_SHOTS_RL:",
		"return WP_ROCKET_LAUNCHER;",
		"case CG_1ST_PLYR_HITS_CG:",
		"case CG_1ST_PLYR_SHOTS_CG:",
		"return WP_CHAINGUN;",
	):
		assert expected in weapon_block

	for expected in (
		"normalized = ownerDraw;",
		"if ( ownerDraw >= CG_2ND_PLYR_FRAGS_G && ownerDraw <= CG_2ND_PLYR_ACC_HMG ) {",
		"normalized = ownerDraw - ( CG_2ND_PLYR - CG_1ST_PLYR );",
		"if ( normalized >= CG_1ST_PLYR_HITS_MG && normalized <= CG_1ST_PLYR_HITS_HMG ) {",
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponHits[weapon] );',
		"if ( normalized >= CG_1ST_PLYR_SHOTS_MG && normalized <= CG_1ST_PLYR_SHOTS_HMG ) {",
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponShots[weapon] );',
	):
		assert expected in weapon_metric_block

	for expected in (
		"CG_DrawPlacementWeaponHitsOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementWeaponShotsOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
	):
		assert expected in dispatch_block


def test_cgame_second_player_weapon_shot_tail_damage_and_accuracy_head_slice_matches_retail_wiring() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	constants = _menudef_ownerdraw_constants()
	weapon_block = _block_from_marker(source, "static weapon_t CG_GetPlacementMetricWeapon( int ownerDraw )")
	weapon_metric_block = _block_from_marker(source, "static qboolean CG_BuildPlacementWeaponMetricText")
	dispatch_block = _block_from_marker(source, "static qboolean CG_DrawPlacementMetricOwnerDraw")
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	shot_tail_slice = {
		"CG_2ND_PLYR_SHOTS_NG",
		"CG_2ND_PLYR_SHOTS_PL",
		"CG_2ND_PLYR_SHOTS_HMG",
	}
	damage_slice = {
		"CG_2ND_PLYR_DMG_G",
		"CG_2ND_PLYR_DMG_MG",
		"CG_2ND_PLYR_DMG_SG",
		"CG_2ND_PLYR_DMG_GL",
		"CG_2ND_PLYR_DMG_RL",
		"CG_2ND_PLYR_DMG_LG",
		"CG_2ND_PLYR_DMG_RG",
		"CG_2ND_PLYR_DMG_PG",
		"CG_2ND_PLYR_DMG_BFG",
		"CG_2ND_PLYR_DMG_CG",
		"CG_2ND_PLYR_DMG_NG",
		"CG_2ND_PLYR_DMG_PL",
		"CG_2ND_PLYR_DMG_HMG",
	}
	accuracy_head_slice = {
		"CG_2ND_PLYR_ACC_MG",
		"CG_2ND_PLYR_ACC_SG",
		"CG_2ND_PLYR_ACC_GL",
		"CG_2ND_PLYR_ACC_RL",
	}

	assert {constants[name] for name in shot_tail_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036b00")
	assert {constants[name] for name in damage_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036c30")
	assert {constants[name] for name in accuracy_head_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036d60")

	for name in sorted(shot_tail_slice | damage_slice | accuracy_head_slice):
		assert f"case {name}:" not in ownerdraw_block

	for expected in (
		"if ( ownerDraw >= CG_2ND_PLYR_FRAGS_G && ownerDraw <= CG_2ND_PLYR_ACC_HMG ) {",
		"normalized = ownerDraw - ( CG_2ND_PLYR - CG_1ST_PLYR );",
		"case CG_1ST_PLYR_SHOTS_NG:",
		"case CG_1ST_PLYR_DMG_NG:",
		"return WP_NAILGUN;",
		"case CG_1ST_PLYR_SHOTS_PL:",
		"case CG_1ST_PLYR_DMG_PL:",
		"return WP_PROX_LAUNCHER;",
		"case CG_1ST_PLYR_SHOTS_HMG:",
		"case CG_1ST_PLYR_DMG_HMG:",
		"return WP_HEAVY_MACHINEGUN;",
		"case CG_1ST_PLYR_DMG_G:",
		"return WP_GAUNTLET;",
		"case CG_1ST_PLYR_DMG_MG:",
		"case CG_1ST_PLYR_ACC_MG:",
		"return WP_MACHINEGUN;",
		"case CG_1ST_PLYR_DMG_RL:",
		"case CG_1ST_PLYR_ACC_RL:",
		"return WP_ROCKET_LAUNCHER;",
	):
		assert expected in weapon_block

	for expected in (
		"if ( normalized >= CG_1ST_PLYR_SHOTS_MG && normalized <= CG_1ST_PLYR_SHOTS_HMG ) {",
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponShots[weapon] );',
		"if ( normalized >= CG_1ST_PLYR_DMG_G && normalized <= CG_1ST_PLYR_DMG_HMG ) {",
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponDamage[weapon] );',
		"if ( normalized >= CG_1ST_PLYR_ACC_MG && normalized <= CG_1ST_PLYR_ACC_HMG ) {",
		'Com_sprintf( buffer, bufferSize, "%i%%", stats->weaponAccuracy[weapon] );',
	):
		assert expected in weapon_metric_block

	for expected in (
		"CG_DrawPlacementWeaponShotsOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementWeaponDamageOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementWeaponAccuracyOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
	):
		assert expected in dispatch_block


def test_cgame_second_player_accuracy_pickup_average_and_award_slice_matches_retail_wiring() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	constants = _menudef_ownerdraw_constants()
	weapon_block = _block_from_marker(source, "static weapon_t CG_GetPlacementMetricWeapon( int ownerDraw )")
	weapon_metric_block = _block_from_marker(source, "static qboolean CG_BuildPlacementWeaponMetricText")
	pickup_metric_block = _block_from_marker(source, "static qboolean CG_BuildPlacementPickupMetricText")
	build_metric_block = _block_from_marker(source, "static qboolean CG_BuildPlacementMetricText")
	dispatch_block = _block_from_marker(source, "static qboolean CG_DrawPlacementMetricOwnerDraw")
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	accuracy_tail_slice = {
		"CG_2ND_PLYR_ACC_LG",
		"CG_2ND_PLYR_ACC_RG",
		"CG_2ND_PLYR_ACC_PG",
		"CG_2ND_PLYR_ACC_BFG",
		"CG_2ND_PLYR_ACC_CG",
		"CG_2ND_PLYR_ACC_NG",
		"CG_2ND_PLYR_ACC_PL",
		"CG_2ND_PLYR_ACC_HMG",
	}
	pickup_slice = {
		"CG_2ND_PLYR_PICKUPS",
		"CG_2ND_PLYR_PICKUPS_RA",
		"CG_2ND_PLYR_PICKUPS_YA",
		"CG_2ND_PLYR_PICKUPS_GA",
		"CG_2ND_PLYR_PICKUPS_MH",
	}
	average_slice = {
		"CG_2ND_PLYR_AVG_PICKUP_TIME_RA",
		"CG_2ND_PLYR_AVG_PICKUP_TIME_YA",
		"CG_2ND_PLYR_AVG_PICKUP_TIME_GA",
		"CG_2ND_PLYR_AVG_PICKUP_TIME_MH",
	}
	award_slice = {
		"CG_2ND_PLYR_EXCELLENT",
		"CG_2ND_PLYR_IMPRESSIVE",
		"CG_2ND_PLYR_HUMILIATION",
	}

	assert {constants[name] for name in accuracy_tail_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036d60")
	assert {constants[name] for name in pickup_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10036eb0")
	assert {constants[name] for name in average_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10037730")
	assert {constants[name] for name in award_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10037990")

	for name in sorted(accuracy_tail_slice | pickup_slice | average_slice | award_slice):
		assert f"case {name}:" not in ownerdraw_block

	for expected in (
		"if ( ownerDraw >= CG_2ND_PLYR_FRAGS_G && ownerDraw <= CG_2ND_PLYR_ACC_HMG ) {",
		"normalized = ownerDraw - ( CG_2ND_PLYR - CG_1ST_PLYR );",
		"case CG_1ST_PLYR_ACC_LG:",
		"return WP_LIGHTNING;",
		"case CG_1ST_PLYR_ACC_RG:",
		"return WP_RAILGUN;",
		"case CG_1ST_PLYR_ACC_PG:",
		"return WP_PLASMAGUN;",
		"case CG_1ST_PLYR_ACC_BFG:",
		"return WP_BFG;",
		"case CG_1ST_PLYR_ACC_CG:",
		"return WP_CHAINGUN;",
		"case CG_1ST_PLYR_ACC_NG:",
		"return WP_NAILGUN;",
		"case CG_1ST_PLYR_ACC_PL:",
		"return WP_PROX_LAUNCHER;",
		"case CG_1ST_PLYR_ACC_HMG:",
		"return WP_HEAVY_MACHINEGUN;",
	):
		assert expected in weapon_block

	for expected in (
		"if ( normalized >= CG_1ST_PLYR_ACC_MG && normalized <= CG_1ST_PLYR_ACC_HMG ) {",
		'Com_sprintf( buffer, bufferSize, "%i%%", stats->weaponAccuracy[weapon] );',
	):
		assert expected in weapon_metric_block

	for expected in (
		"normalized = ownerDraw;",
		"CG_ResolvePlacementMetricOwnerDraw( ownerDraw, NULL, &normalized );",
		"if ( normalized == CG_1ST_PLYR_PICKUPS ) {",
		"if ( normalized >= CG_1ST_PLYR_PICKUPS_RA && normalized <= CG_1ST_PLYR_PICKUPS_MH ) {",
		"index = normalized - CG_1ST_PLYR_PICKUPS_RA;",
		"if ( normalized >= CG_1ST_PLYR_AVG_PICKUP_TIME_RA && normalized <= CG_1ST_PLYR_AVG_PICKUP_TIME_MH ) {",
		"index = normalized - CG_1ST_PLYR_AVG_PICKUP_TIME_RA;",
		"buffer[0] = '\\0';",
	):
		assert expected in pickup_metric_block

	for expected in (
		"normalized = ownerDraw;",
		"CG_ResolvePlacementMetricOwnerDraw( ownerDraw, NULL, &normalized );",
		"switch ( normalized ) {",
		"case CG_1ST_PLYR_EXCELLENT:",
		'Com_sprintf( buffer, bufferSize, "%i", score->excellentCount );',
		"case CG_1ST_PLYR_IMPRESSIVE:",
		'Com_sprintf( buffer, bufferSize, "%i", score->impressiveCount );',
		"case CG_1ST_PLYR_HUMILIATION:",
		'Com_sprintf( buffer, bufferSize, "%i", score->guantletCount );',
		"CG_BuildPlacementWeaponMetricText( normalized, score, buffer, bufferSize )",
		"CG_BuildPlacementPickupMetricText( normalized, score, buffer, bufferSize )",
	):
		assert expected in build_metric_block

	for expected in (
		"CG_DrawPlacementWeaponAccuracyOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementPickupCountOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementPickupAverageOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
		"CG_DrawPlacementAwardCountOwnerDraw( rect, scale, color, textStyle, ownerDraw );",
	):
		assert expected in dispatch_block


def test_cgame_second_player_progression_tail_and_red_team_head_slice_matches_retail_wiring() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	constants = _menudef_ownerdraw_constants()
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	score_block = _block_from_marker(source, "static void CG_DrawTeamScore")
	name_block = _block_from_marker(source, "static void CG_DrawTeamName")
	player_count_block = _block_from_marker(source, "static void CG_DrawTeamPlayerCount")
	pickup_meta_block = _block_from_marker(source, "static qboolean CG_GetTeamPickupOwnerDrawMeta")
	pickup_text_block = _block_from_marker(source, "static qboolean CG_BuildTeamPickupText")
	timeheld_text_block = _block_from_marker(source, "static qboolean CG_BuildTeamTimeHeldText")
	no_route_slice = {"CG_2ND_PLYR_PR", "CG_2ND_PLYR_TIER"}
	direct_targets = {
		"FUN_10030a80": {"CG_RED_FLAGSTATUS", "CG_RED_BASESTATUS"},
		"FUN_1002ff50": {"CG_RED_SCORE"},
		"FUN_10030090": {"CG_RED_NAME"},
		"FUN_100337a0": {"CG_RED_OWNED_FLAGS"},
		"FUN_10039e70": {"CG_RED_AVG_PING"},
		"FUN_100333c0": {"CG_RED_PLAYER_COUNT"},
		"FUN_100335f0": {"CG_RED_CLAN_PLYRS"},
		"FUN_10033530": {"CG_RED_TIMEOUT_COUNT"},
	}
	pickup_slice = {
		"CG_RED_TEAM_MAP_PICKUPS",
		"CG_RED_TEAM_PICKUPS_RA",
		"CG_RED_TEAM_PICKUPS_YA",
		"CG_RED_TEAM_PICKUPS_GA",
		"CG_RED_TEAM_PICKUPS_MH",
		"CG_RED_TEAM_PICKUPS_QUAD",
		"CG_RED_TEAM_PICKUPS_BS",
	}
	timeheld_slice = {
		"CG_RED_TEAM_TIMEHELD_QUAD",
		"CG_RED_TEAM_TIMEHELD_BS",
	}

	for name in no_route_slice:
		assert constants[name] not in _retail_cg_ownerdraw_case_values()

	for target, names in direct_targets.items():
		assert {constants[name] for name in names} <= _retail_cg_ownerdraw_cases_for_target(target)

	assert {constants[name] for name in pickup_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10037f80")
	assert {constants[name] for name in timeheld_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10039ae0")

	for expected in (
		"case CG_2ND_PLYR_PR:",
		"case CG_2ND_PLYR_TIER:",
		"Retail has no raw ownerdraw 0x119-0x11a helper route.",
		"case CG_RED_FLAGSTATUS:",
		"CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_RED, qfalse, shader );",
		"case CG_RED_SCORE:",
		"CG_DrawTeamScore( &rect, scale, color, textStyle, TEAM_RED, align );",
		"case CG_RED_NAME:",
		"CG_DrawTeamName( &rect, scale, color, textStyle, TEAM_RED, align );",
		"case CG_RED_AVG_PING:",
		"CG_DrawTeamAveragePing(&rect, scale, color, textStyle, TEAM_RED);",
		"case CG_RED_BASESTATUS:",
		"CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_RED, qtrue, shader );",
		"case CG_RED_PLAYER_COUNT:",
		"CG_DrawTeamPlayerCount(&rect, scale, color, textStyle, TEAM_RED, align);",
	):
		assert expected in ownerdraw_block

	for marker, expected in (
		("case CG_RED_OWNED_FLAGS:", "CG_DrawDominationOwnedFlags(&rect, scale, color, textStyle, TEAM_RED);"),
		("case CG_RED_CLAN_PLYRS:", "CG_DrawClanArenaPlayers(&rect, scale, color, textStyle, TEAM_RED);"),
		("case CG_RED_TIMEOUT_COUNT:", "CG_DrawTeamTimeoutCount( &rect, scale, color, textStyle, TEAM_RED, align );"),
	):
		start = ownerdraw_block.index(marker)
		end = ownerdraw_block.index("break;", start)
		case_block = ownerdraw_block[start:end]
		assert expected in case_block
		if marker == "case CG_RED_OWNED_FLAGS:":
			assert "if ( cgs.gametype == GT_DOMINATION || cgs.gametype == GT_ATTACK_DEFEND ) {" in case_block
		elif marker == "case CG_RED_CLAN_PLYRS:":
			assert "if ( CG_ShowPlayersRemaining() ) {" in case_block
		else:
			assert "if ( cgs.playerCountTeamSize > 0 ) {" in case_block

	for expected in (
		"case CG_RED_TEAM_MAP_PICKUPS:",
		"case CG_RED_TEAM_PICKUPS_RA:",
		"case CG_RED_TEAM_PICKUPS_BS:",
		"CG_DrawTeamPickupOwnerDraw( &rect, scale, color, textStyle, ownerDraw );",
		"case CG_RED_TEAM_TIMEHELD_QUAD:",
		"case CG_RED_TEAM_TIMEHELD_BS:",
		"CG_DrawTeamTimeHeldOwnerDraw( &rect, scale, color, textStyle, ownerDraw );",
	):
		assert expected in ownerdraw_block

	for expected in (
		"CG_TranslateHudRectForWidescreen( rect, &widescreenRect );",
		"x = CG_AlignTextInRectX( &widescreenRect, scale, buffer, align );",
	):
		assert expected in score_block
	assert "teamName = CG_GetTeamName( team );" in name_block
	assert "teamLimit = cgs.playerCountTeamSize;" in player_count_block

	for expected in (
		"if ( ownerDraw >= CG_RED_TEAM_MAP_PICKUPS && ownerDraw <= CG_RED_TEAM_TIMEHELD_INVIS ) {",
		"resolvedTeam = TEAM_RED;",
		"resolvedStatIndex = ownerDraw - CG_RED_TEAM_MAP_PICKUPS;",
	):
		assert expected in pickup_meta_block

	for expected in (
		"teamIndex = ( team == TEAM_RED ) ? 0 : 1;",
		"value = cg.teamScoreStats.values[teamIndex][statIndex];",
		'Com_sprintf( buffer, bufferSize, "%i", value );',
	):
		assert expected in pickup_text_block

	for expected in (
		"if ( !CG_IsTeamTimeHeldOwnerDraw( ownerDraw ) ) {",
		"if ( !CG_GetTeamPickupOwnerDrawMeta( ownerDraw, &team, &statIndex ) ) {",
		"Q_strncpyz( buffer, CG_FormatMinutesSeconds( value ), bufferSize );",
	):
		assert expected in timeheld_text_block


def test_cgame_red_pickup_tail_and_blue_team_head_slice_matches_retail_wiring() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	constants = _menudef_ownerdraw_constants()
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	score_text_block = _block_from_marker(source, "static qboolean CG_BuildTeamScoreText")
	team_status_block = _block_from_marker(source, "static void CG_DrawTeamFlagOrBaseStatus")
	score_block = _block_from_marker(source, "static void CG_DrawTeamScore")
	name_block = _block_from_marker(source, "static void CG_DrawTeamName")
	average_ping_block = _block_from_marker(source, "static void CG_DrawTeamAveragePing")
	pickup_meta_block = _block_from_marker(source, "static qboolean CG_GetTeamPickupOwnerDrawMeta")
	pickup_text_block = _block_from_marker(source, "static qboolean CG_BuildTeamPickupText")
	timeheld_text_block = _block_from_marker(source, "static qboolean CG_BuildTeamTimeHeldText")
	red_pickup_tail_slice = {
		"CG_RED_TEAM_PICKUPS_FLAG",
		"CG_RED_TEAM_PICKUPS_MEDKIT",
		"CG_RED_TEAM_PICKUPS_REGEN",
		"CG_RED_TEAM_PICKUPS_HASTE",
		"CG_RED_TEAM_PICKUPS_INVIS",
	}
	red_timeheld_tail_slice = {
		"CG_RED_TEAM_TIMEHELD_FLAG",
		"CG_RED_TEAM_TIMEHELD_REGEN",
		"CG_RED_TEAM_TIMEHELD_HASTE",
		"CG_RED_TEAM_TIMEHELD_INVIS",
	}
	blue_pickup_head_slice = {
		"CG_BLUE_TEAM_MAP_PICKUPS",
		"CG_BLUE_TEAM_PICKUPS_RA",
	}
	blue_direct_targets = {
		"FUN_10030a80": {"CG_BLUE_FLAGSTATUS", "CG_BLUE_BASESTATUS"},
		"FUN_10030090": {"CG_BLUE_NAME"},
		"FUN_1002ff50": {"CG_BLUE_SCORE"},
		"FUN_100337a0": {"CG_BLUE_OWNED_FLAGS"},
		"FUN_10039e70": {"CG_BLUE_AVG_PING"},
		"FUN_100333c0": {"CG_BLUE_PLAYER_COUNT"},
		"FUN_100335f0": {"CG_BLUE_CLAN_PLYRS"},
		"FUN_10033530": {"CG_BLUE_TIMEOUT_COUNT"},
	}

	assert {constants[name] for name in red_pickup_tail_slice | blue_pickup_head_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10037f80")
	assert {constants[name] for name in red_timeheld_tail_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10039ae0")
	for target, names in blue_direct_targets.items():
		assert {constants[name] for name in names} <= _retail_cg_ownerdraw_cases_for_target(target)

	for expected in (
		"case CG_RED_TEAM_PICKUPS_FLAG:",
		"case CG_RED_TEAM_PICKUPS_MEDKIT:",
		"case CG_RED_TEAM_PICKUPS_REGEN:",
		"case CG_RED_TEAM_PICKUPS_HASTE:",
		"case CG_RED_TEAM_PICKUPS_INVIS:",
		"case CG_BLUE_TEAM_MAP_PICKUPS:",
		"case CG_BLUE_TEAM_PICKUPS_RA:",
		"CG_DrawTeamPickupOwnerDraw( &rect, scale, color, textStyle, ownerDraw );",
		"case CG_RED_TEAM_TIMEHELD_FLAG:",
		"case CG_RED_TEAM_TIMEHELD_REGEN:",
		"case CG_RED_TEAM_TIMEHELD_HASTE:",
		"case CG_RED_TEAM_TIMEHELD_INVIS:",
		"CG_DrawTeamTimeHeldOwnerDraw( &rect, scale, color, textStyle, ownerDraw );",
	):
		assert expected in ownerdraw_block

	for expected in (
		"case CG_BLUE_FLAGSTATUS:",
		"CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_BLUE, qfalse, shader );",
		"case CG_BLUE_NAME:",
		"CG_DrawTeamName( &rect, scale, color, textStyle, TEAM_BLUE, align );",
		"case CG_BLUE_SCORE:",
		"CG_DrawTeamScore( &rect, scale, color, textStyle, TEAM_BLUE, align );",
		"case CG_BLUE_AVG_PING:",
		"CG_DrawTeamAveragePing(&rect, scale, color, textStyle, TEAM_BLUE);",
		"case CG_BLUE_BASESTATUS:",
		"CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_BLUE, qtrue, shader );",
		"case CG_BLUE_PLAYER_COUNT:",
		"CG_DrawTeamPlayerCount(&rect, scale, color, textStyle, TEAM_BLUE, align);",
	):
		assert expected in ownerdraw_block

	for marker, expected in (
		("case CG_BLUE_OWNED_FLAGS:", "CG_DrawDominationOwnedFlags(&rect, scale, color, textStyle, TEAM_BLUE);"),
		("case CG_BLUE_CLAN_PLYRS:", "CG_DrawClanArenaPlayers(&rect, scale, color, textStyle, TEAM_BLUE);"),
		("case CG_BLUE_TIMEOUT_COUNT:", "CG_DrawTeamTimeoutCount( &rect, scale, color, textStyle, TEAM_BLUE, align );"),
	):
		start = ownerdraw_block.index(marker)
		end = ownerdraw_block.index("break;", start)
		case_block = ownerdraw_block[start:end]
		assert expected in case_block
		if marker == "case CG_BLUE_OWNED_FLAGS:":
			assert "if ( cgs.gametype == GT_DOMINATION || cgs.gametype == GT_ATTACK_DEFEND ) {" in case_block
		elif marker == "case CG_BLUE_CLAN_PLYRS:":
			assert "if ( CG_ShowPlayersRemaining() ) {" in case_block
		else:
			assert "if ( cgs.playerCountTeamSize > 0 ) {" in case_block

	for expected in (
		"} else if ( ownerDraw >= CG_BLUE_TEAM_MAP_PICKUPS && ownerDraw <= CG_BLUE_TEAM_TIMEHELD_INVIS ) {",
		"resolvedTeam = TEAM_BLUE;",
		"resolvedStatIndex = ownerDraw - CG_BLUE_TEAM_MAP_PICKUPS;",
	):
		assert expected in pickup_meta_block

	for expected in (
		"teamIndex = ( team == TEAM_RED ) ? 0 : 1;",
		"value = cg.teamScoreStats.values[teamIndex][statIndex];",
		'Com_sprintf( buffer, bufferSize, "%i", value );',
	):
		assert expected in pickup_text_block

	for expected in (
		"if ( !CG_GetTeamScoreStatValue( team, statIndex, &value ) ) {",
		'Q_strncpyz( buffer, "-", bufferSize );',
		"Q_strncpyz( buffer, CG_FormatMinutesSeconds( value ), bufferSize );",
	):
		assert expected in timeheld_text_block

	for expected in (
		"if ( shader && !baseStatus && cgs.gametype != GT_1FCTF ) {",
		"handle = CG_GetTeamFlagStatusShader( team, baseStatus );",
	):
		assert expected in team_status_block
	assert "score = ( team == TEAM_RED ) ? cgs.scores1 : cgs.scores2;" in score_text_block
	assert "teamName = CG_GetTeamName( team );" in name_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "Avg ping %i", average );' in average_ping_block


def test_cgame_blue_pickup_tail_and_final_ownerdraw_slice_matches_retail_wiring() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	symbol_map = (REPO_ROOT / "references" / "symbol-maps" / "cgame.json").read_text(encoding="utf-8")
	constants = _menudef_ownerdraw_constants()
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	pickup_meta_block = _block_from_marker(source, "static qboolean CG_GetTeamPickupOwnerDrawMeta")
	pickup_text_block = _block_from_marker(source, "static qboolean CG_BuildTeamPickupText")
	timeheld_text_block = _block_from_marker(source, "static qboolean CG_BuildTeamTimeHeldText")
	objective_draw_block = _block_from_marker(source, "static void CG_DrawObjectiveStatus")
	health_block = _block_from_marker(source, "static void CG_DrawHealthColorized")
	match_state_block = _block_from_marker(source, "static void CG_DrawMatchState")
	blue_pickup_tail_slice = {
		"CG_BLUE_TEAM_PICKUPS_YA",
		"CG_BLUE_TEAM_PICKUPS_GA",
		"CG_BLUE_TEAM_PICKUPS_MH",
		"CG_BLUE_TEAM_PICKUPS_QUAD",
		"CG_BLUE_TEAM_PICKUPS_BS",
		"CG_BLUE_TEAM_PICKUPS_FLAG",
		"CG_BLUE_TEAM_PICKUPS_MEDKIT",
		"CG_BLUE_TEAM_PICKUPS_REGEN",
		"CG_BLUE_TEAM_PICKUPS_HASTE",
		"CG_BLUE_TEAM_PICKUPS_INVIS",
	}
	blue_timeheld_tail_slice = {
		"CG_BLUE_TEAM_TIMEHELD_QUAD",
		"CG_BLUE_TEAM_TIMEHELD_BS",
		"CG_BLUE_TEAM_TIMEHELD_FLAG",
		"CG_BLUE_TEAM_TIMEHELD_REGEN",
		"CG_BLUE_TEAM_TIMEHELD_HASTE",
		"CG_BLUE_TEAM_TIMEHELD_INVIS",
	}
	singleton_targets = {
		"FUN_10030240": {"CG_FLAG_STATUS"},
		"FUN_1002f6b0": {"CG_HEALTH_COLORIZED"},
		"FUN_10034360": {"CG_MATCH_STATE"},
	}

	assert {constants[name] for name in blue_pickup_tail_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10037f80")
	assert {constants[name] for name in blue_timeheld_tail_slice} <= _retail_cg_ownerdraw_cases_for_target("FUN_10039ae0")
	for target, names in singleton_targets.items():
		assert {constants[name] for name in names} <= _retail_cg_ownerdraw_cases_for_target(target)

	for expected in (
		"case CG_BLUE_TEAM_PICKUPS_YA:",
		"case CG_BLUE_TEAM_PICKUPS_GA:",
		"case CG_BLUE_TEAM_PICKUPS_MH:",
		"case CG_BLUE_TEAM_PICKUPS_QUAD:",
		"case CG_BLUE_TEAM_PICKUPS_BS:",
		"case CG_BLUE_TEAM_PICKUPS_FLAG:",
		"case CG_BLUE_TEAM_PICKUPS_MEDKIT:",
		"case CG_BLUE_TEAM_PICKUPS_REGEN:",
		"case CG_BLUE_TEAM_PICKUPS_HASTE:",
		"case CG_BLUE_TEAM_PICKUPS_INVIS:",
		"CG_DrawTeamPickupOwnerDraw( &rect, scale, color, textStyle, ownerDraw );",
		"case CG_BLUE_TEAM_TIMEHELD_QUAD:",
		"case CG_BLUE_TEAM_TIMEHELD_BS:",
		"case CG_BLUE_TEAM_TIMEHELD_FLAG:",
		"case CG_BLUE_TEAM_TIMEHELD_REGEN:",
		"case CG_BLUE_TEAM_TIMEHELD_HASTE:",
		"case CG_BLUE_TEAM_TIMEHELD_INVIS:",
		"CG_DrawTeamTimeHeldOwnerDraw( &rect, scale, color, textStyle, ownerDraw );",
		"case CG_FLAG_STATUS:",
		"CG_DrawObjectiveStatus( &rect, scale, color, textStyle );",
		"case CG_HEALTH_COLORIZED:",
		"CG_DrawHealthColorized(&rect, followShader);",
		"case CG_MATCH_STATE:",
		"CG_DrawMatchState(&rect, scale, color, textStyle);",
	):
		assert expected in ownerdraw_block

	for expected in (
		"} else if ( ownerDraw >= CG_BLUE_TEAM_MAP_PICKUPS && ownerDraw <= CG_BLUE_TEAM_TIMEHELD_INVIS ) {",
		"resolvedTeam = TEAM_BLUE;",
		"resolvedStatIndex = ownerDraw - CG_BLUE_TEAM_MAP_PICKUPS;",
	):
		assert expected in pickup_meta_block

	for expected in (
		"teamIndex = ( team == TEAM_RED ) ? 0 : 1;",
		"value = cg.teamScoreStats.values[teamIndex][statIndex];",
		'Com_sprintf( buffer, bufferSize, "%i", value );',
	):
		assert expected in pickup_text_block

	for expected in (
		"if ( !CG_GetTeamScoreStatValue( team, statIndex, &value ) ) {",
		'Q_strncpyz( buffer, "-", bufferSize );',
		"Q_strncpyz( buffer, CG_FormatMinutesSeconds( value ), bufferSize );",
	):
		assert expected in timeheld_text_block

	for expected in (
		"if ( CG_DrawObjectiveStatusStrip( rect ) ) {",
		"CG_BuildObjectiveStatusLabel( buffer, sizeof( buffer ) )",
		"CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );",
	):
		assert expected in objective_draw_block

	for expected in (
		"if ( !rect || !cg.snap ) {",
		"if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {",
		"slot = ( rect->x + rect->w * 0.5f < 320.0f ) ? 0 : 1;",
		"ci = CG_SpectatorClientInfo( slot );",
		"health = cg.snap->ps.stats[STAT_HEALTH];",
		"armor = cg.snap->ps.stats[STAT_ARMOR];",
		"health = ci->health;",
		"armor = ci->armor;",
		"CG_GetColorForHealth( health, armor, color );",
		"trap_R_DrawStretchPic( x, y, w, h, 0.0f, 0.0f, 1.0f, 1.0f, shader );",
		"CG_FillRect( rect->x, rect->y, rect->w, rect->h, color );",
	):
		assert expected in health_block

	assert "CG_Text_Paint( rect->x, rect->y, scale, color, CG_GetMatchPhaseText(), 0, 0, textStyle );" in match_state_block
	assert '"normalized_name": "CG_DrawObjectiveStatus"' in symbol_map
	assert '"normalized_name": "CG_DrawHealthColorized"' in symbol_map
	assert '"normalized_name": "CG_DrawMatchState"' in symbol_map


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
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	game_source = G_MAIN.read_text(encoding="utf-8")
	bg_public_source = BG_PUBLIC.read_text(encoding="utf-8")
	qagame_ghidra_source = QAGAME_GHIDRA_DECOMPILE.read_text(encoding="utf-8")
	player_score_block = _block_from_marker(source, "static void CG_DrawPlayerScore")
	score_value_block = _block_from_marker(source, "static void CG_DrawScoreValue")
	value_block = _block_from_marker(source, "static qboolean CG_BuildPlacementScoreValue")
	line_block = _block_from_marker(source, "static void CG_DrawPlacementScoreLine")
	team_name_block = _block_from_marker(source, "static const char *CG_GetRetailPlacementTeamName")
	first_score_block = _block_from_marker(source, "static void CG_Draw1stPlaceScore")
	second_score_block = _block_from_marker(source, "static void CG_Draw2ndPlaceScore")
	follow_block = _block_from_marker(source, "static void CG_DrawFollowPlayerNameEx")
	resolve_weapon_block = _block_from_marker(source, "static const char *CG_ResolveWeaponName")
	selected_score_block = _block_from_marker(source, "score_t *CG_GetSelectedScore")
	selected_client_block = _block_from_marker(source, "static clientInfo_t *CG_GetSelectedClientInfo")
	selected_team_color_block = _block_from_marker(source, "static void CG_DrawSelectedPlayerTeamColor")
	selected_accuracy_block = _block_from_marker(source, "static void CG_DrawSelectedPlayerAccuracy")
	best_weapon_block = _block_from_marker(source, "static void CG_DrawSelectedPlayerBestWeapon")
	match_winner_block = _block_from_marker(source, "static void CG_DrawMatchWinner")
	endgame_score_block = _block_from_marker(source, "static void CG_DrawEndGameScore")
	new_chat_block = _block_from_marker(source, "static void CG_DrawNewChatArea")
	set_config_values_block = _block_from_marker(servercmds_source, "void CG_SetConfigValues( void )")
	configstring_modified_block = _block_from_marker(servercmds_source, "static void CG_ConfigStringModified")
	calculate_ranks_block = _block_from_marker(game_source, "void CalculateRanks( void )")
	retail_calculate_ranks_block = _block_from_marker(qagame_ghidra_source, "void FUN_10056070(void)")
	constants = _menudef_ownerdraw_constants()
	retail_best_weapon_block = _text_between(
		hlil_source,
		'100345f0    int32_t __convention("regparm") sub_100345f0',
		"100346e0",
	)

	assert _retail_cg_ownerdraw_cases_for_target("FUN_100323d0") == {
		constants["CG_PLAYER_SCORE"],
		constants["CG_1STPLACE"],
		constants["CG_2NDPLACE"],
	}
	assert _retail_cg_ownerdraw_cases_for_target("FUN_1002ff50") == {
		constants["CG_RED_SCORE"],
		constants["CG_BLUE_SCORE"],
	}
	assert _retail_cg_ownerdraw_cases_for_target("FUN_100345f0") == {
		constants["CG_PLYR_BEST_WEAPON_NAME"],
	}

	assert set(_case_labels(score_value_block)) == {
		"CG_PLAYER_SCORE",
		"CG_1STPLACE",
		"CG_2NDPLACE",
	}
	assert "CG_DrawTeamScore" not in score_value_block
	assert "case CG_RED_SCORE:" not in score_value_block
	assert "case CG_BLUE_SCORE:" not in score_value_block

	for expected in (
		"CG_DrawPlayerScore( rect, scale, color, shader, textStyle );",
		"if ( cgs.scores1 != SCORE_NOT_PRESENT ) {",
		'CG_Text_Paint( rect->x, rect->y, scale, color, va( "%2i", cgs.scores1 ), 0, 0, textStyle );',
		"if ( cgs.scores2 != SCORE_NOT_PRESENT ) {",
		'CG_Text_Paint( rect->x, rect->y, scale, color, va( "%2i", cgs.scores2 ), 0, 0, textStyle );',
	):
		assert expected in score_value_block

	assert "CG_Text_Paint( rect->x, rect->y, scale, color, num, 0, 0, textStyle );" in player_score_block
	assert "rect->y + rect->h" not in player_score_block
	for expected in (
		"if ( cgs.gametype == GT_RACE ) {",
		"value = cgs.clientinfo[clientNum].score;",
		"if ( value == SCORE_NOT_PRESENT ) {",
		"if ( value == 0x7fffffff || value < 0 ) {",
		'Q_strncpyz( num, "-", sizeof( num ) );',
		"Q_strncpyz( num, CG_FormatSignedWholeSeconds( value ), sizeof( num ) );",
	):
		assert expected in player_score_block

	for expected in (
		"if ( cgs.gametype == GT_RACE ) {",
		"qboolean requirePositiveRaceTime",
		"requirePositiveRaceTime && value == 0",
		"CG_RaceFormatMilliseconds( value, valueText, sizeof( valueText ) );",
		'Q_strncpyz( buffer, leadingSpace ? " -" : "-", bufferSize );',
		'Com_sprintf( buffer, bufferSize, " %s", valueText );',
		'Com_sprintf( buffer, bufferSize, leadingSpace ? " %d" : "%d", value );',
	):
		assert expected in value_block
	assert "if ( value == CG_SCORE_FORFEIT ) {" not in value_block

	for expected in (
		"teamName = cgs.redTeamName;",
		'return "Red Team";',
		"teamName = cgs.blueTeamName;",
		'return "Blue Team";',
	):
		assert expected in team_name_block
	for stale in (
		"cg_redTeamName",
		"cg_blueTeamName",
		"DEFAULT_REDTEAM_NAME",
		"DEFAULT_BLUETEAM_NAME",
	):
		assert stale not in team_name_block

	for expected in (
		"if ( !valueText || !valueText[0] ) {",
		"CG_Text_PaintExt( x, rect->y, scale, color, rankText, 0.0f, 0, textStyle, FONT_DEFAULT );",
		"CG_Text_WidthExt( rankText, scale, 0, FONT_DEFAULT );",
		"CG_Text_WidthExt( valueText, scale, 0, FONT_DEFAULT );",
		"CG_Text_PaintExt( x, rect->y, scale, color, nameText, 0.0f, 0, textStyle, FONT_DEFAULT );",
		"CG_Text_Paint_LimitExt( &maxX, x, rect->y, scale, color, nameText, 0.0f, 0, FONT_DEFAULT );",
		'CG_Text_PaintExt( ellipsisX, rect->y, scale, color, "...", 0.0f, 0, textStyle, FONT_DEFAULT );',
		"CG_Text_PaintExt( valueX, rect->y, scale, color, valueText, 0.0f, 0, textStyle, FONT_DEFAULT );",
	):
		assert expected in line_block

	for expected in (
		"CG_GetRetailPlacementTeamName( leaderTeam )",
		"leaderTeam = TEAM_RED;",
		"leaderTeam = ( cgs.scores1 < cgs.scores2 ) ? TEAM_BLUE : TEAM_RED;",
		"CG_BuildPlacementScoreValue( value, valueBuffer, sizeof( valueBuffer ), qfalse, qfalse )",
		"if ( cgs.scores1 == SCORE_NOT_PRESENT ) {",
		'CG_Text_Paint( rect->x, rect->y, scale, color, "1.", 0, 0, textStyle );',
		"CG_BuildPlacementScoreValue( cgs.scores1, valueBuffer, sizeof( valueBuffer ), qtrue, qfalse )",
		"Q_strncpyz( nameBuffer, cgs.firstPlaceName, sizeof( nameBuffer ) );",
		'CG_DrawPlacementScoreLine( rect, scale, color, textStyle, "1. ", nameBuffer, valueBuffer );',
	):
		assert expected in first_score_block
	for stale in (
		"CG_GetActiveScoreByIndex( 0 );",
		"CG_GetTeamName( leaderTeam )",
		"Unknown",
		"^%c%s^7",
	):
		assert stale not in first_score_block

	for expected in (
		"CG_GetRetailPlacementTeamName( trailingTeam )",
		"CG_BuildPlacementScoreValue( value, valueBuffer, sizeof( valueBuffer ), qfalse, qfalse )",
		"cg.snap && cg.snap->ps.pm_type != PM_SPECTATOR && !CG_ShowPlayerIsFirstPlace()",
		"rank = cg.snap->ps.persistant[PERS_RANK];",
		"rank &= ~RANK_TIED_FLAG;",
		"localRank = rank + 1;",
		"value = ( cgs.gametype == GT_RACE ) ? cgs.clientinfo[clientNum].score : cg.snap->ps.persistant[PERS_SCORE];",
		"CG_BuildPlacementScoreValue( value, valueBuffer, sizeof( valueBuffer ), qtrue, qtrue )",
		"value = cgs.scores2;",
		"CG_BuildPlacementScoreValue( value, valueBuffer, sizeof( valueBuffer ), qtrue, qtrue )",
		"localRank = ( cgs.scores1 != cgs.scores2 ) ? 2 : 1;",
		"Q_strncpyz( nameBuffer, cgs.secondPlaceName, sizeof( nameBuffer ) );",
		'Com_sprintf( rankBuffer, sizeof( rankBuffer ), "%d. ", localRank );',
		"CG_DrawPlacementScoreLine( rect, scale, color, textStyle, rankBuffer, nameBuffer, valueBuffer );",
	):
		assert expected in second_score_block
	for stale in (
		"CG_GetScoreForClientNum( cg.snap->ps.clientNum )",
		"CG_GetActiveScoreByIndex( 1 )",
		"CG_GetTeamName( trailingTeam )",
		"^%c%s^7",
	):
		assert stale not in second_score_block

	for expected in (
		"#define CS_FIRST_PLACE_NAME\t\t0x293",
		"#define CS_SECOND_PLACE_NAME\t0x294",
	):
		assert expected in bg_public_source
	for expected in (
		"char\t\t\tfirstPlaceName[40];",
		"char\t\t\tsecondPlaceName[40];",
	):
		assert expected in local_source
	for expected in (
		"Q_strncpyz( cgs.firstPlaceName, CG_ConfigString( CS_FIRST_PLACE_NAME ), sizeof( cgs.firstPlaceName ) );",
		"Q_strncpyz( cgs.secondPlaceName, CG_ConfigString( CS_SECOND_PLACE_NAME ), sizeof( cgs.secondPlaceName ) );",
	):
		assert expected in set_config_values_block
	for expected in (
		"} else if ( num == CS_FIRST_PLACE_NAME ) {",
		"Q_strncpyz( cgs.firstPlaceName, str, sizeof( cgs.firstPlaceName ) );",
		"} else if ( num == CS_SECOND_PLACE_NAME ) {",
		"Q_strncpyz( cgs.secondPlaceName, str, sizeof( cgs.secondPlaceName ) );",
	):
		assert expected in configstring_modified_block
	for expected in (
		"trap_SetConfigstring( CS_FIRST_PLACE_NAME, \"TEAM_RED\" );",
		"trap_SetConfigstring( CS_SECOND_PLACE_NAME, \"TEAM_BLUE\" );",
		"if ( level.numPlayingClients < 1 ) {",
		"trap_SetConfigstring( CS_FIRST_PLACE_NAME, level.clients[ level.sortedClients[0] ].pers.netname );",
		"if ( level.numPlayingClients < 2 ) {",
		"trap_SetConfigstring( CS_SECOND_PLACE_NAME, level.clients[ level.sortedClients[1] ].pers.netname );",
	):
		assert expected in calculate_ranks_block
	for stale in (
		"trap_SetConfigstring( CS_FIRST_PLACE_NAME, \"\" );\n\t\ttrap_SetConfigstring( CS_SECOND_PLACE_NAME, \"\" );",
		"level.numConnectedClients == 0",
		"level.numConnectedClients == 1",
	):
		assert stale not in calculate_ranks_block
	for expected in (
		'(**(code **)(DAT_104b13ac + 100))(0x293,"TEAM_RED");',
		'(**(code **)(DAT_104b13ac + 100))(0x294,"TEAM_BLUE");',
		"if (DAT_105dce94 < 1) {",
		"if (DAT_105dce94 < 2) {",
	):
		assert expected in retail_calculate_ranks_block

	for expected in (
		"if ( !rect || !ci ) {",
		"if ( ownerDraw == CG_FOLLOW_PLAYER_NAME ) {",
		'"Following - %s"',
		"Q_strncpyz( buffer, ci->name, sizeof( buffer ) );",
		"Vector4Copy( CG_TeamColor( ci->team ), drawColor );",
		"CG_AlignTextX( &x, buffer, scale, align );",
	):
		assert expected in follow_block
	assert "rect->w - width" not in follow_block

	assert "cg.selectedScore < 0 || cg.selectedScore >= cg.numScores || cg.selectedScore >= MAX_CLIENTS" in selected_score_block
	assert "score->client < 0 || score->client >= cgs.maxclients || score->client >= MAX_CLIENTS" in selected_client_block

	for block in (
		selected_team_color_block,
		selected_accuracy_block,
		best_weapon_block,
		match_winner_block,
		endgame_score_block,
	):
		assert "if ( !rect ) {" in block

	for expected in (
		"switch ( ci->team ) {",
		"Vector4Set( fill, 1.0f, 0.0f, 0.0f, 0.45f );",
		"Vector4Set( fill, 0.2f, 0.35f, 1.0f, 0.45f );",
		"Vector4Set( fill, 1.0f, 1.0f, 1.0f, 0.25f );",
	):
		assert expected in selected_team_color_block

	assert 'Com_sprintf( buffer, sizeof( buffer ), "%i%%", score->accuracy );' in selected_accuracy_block
	for expected in (
		'case WP_GAUNTLET:',
		'return "Gauntlet";',
		'case WP_GRENADE_LAUNCHER:',
		'return "Grenade";',
		'case WP_RAILGUN:',
		'return "Rail Gun";',
		'case WP_BFG:',
		'return "BFG";',
		'case WP_NAILGUN:',
		'return "Nail Gun";',
		'case WP_PROX_LAUNCHER:',
		'return "Proximity Mines";',
		'case WP_CHAINGUN:',
		'return "Chain Gun";',
		'case WP_HEAVY_MACHINEGUN:',
		'return "Heavy Machinegun";',
	):
		assert expected in resolve_weapon_block
	assert "BG_FindItemForWeapon" not in resolve_weapon_block

	for expected in (
		"(&data_10a9ceac)[data_10a9cdc4 * 0x9a] - 1",
		'eax_2 = "Gauntlet"',
		'eax_2 = "Grenade"',
		'eax_2 = "Rail Gun"',
		"eax_2 = &data_10065140",
		'eax_2 = "Nail Gun"',
		'eax_2 = "Proximity Mines"',
		'eax_2 = "Chain Gun"',
		'eax_2 = "Heavy Machinegun"',
		"sub_10008440(fconvert.s(fconvert.t(*arg3)),",
		"fconvert.s(fconvert.t(arg3[1]))",
	):
		assert expected in retail_best_weapon_block
	assert "weapon = score->bestWeapon;" in best_weapon_block
	assert "weaponName = CG_ResolveWeaponName( weapon );" in best_weapon_block
	assert "if ( !weaponName ) {" in best_weapon_block
	assert "return;" in best_weapon_block
	assert "CG_Text_Paint(rect->x, rect->y, scale, color, weaponName, 0, 0, textStyle);" in best_weapon_block
	assert "weapon = cent->currentState.weapon;" not in best_weapon_block
	assert '"Unknown"' not in best_weapon_block
	assert "rect->y + rect->h" not in best_weapon_block
	assert "if ( !rect || cg_teamChatTime.integer <= 0 ) {" in new_chat_block

	assert "case CG_1ST_PLACE_SCORE:" in source
	assert "CG_Draw1stPlaceScore(&rect, scale, color, textStyle);" in source
	assert "case CG_2ND_PLACE_SCORE:" in source
	assert "CG_Draw2ndPlaceScore(&rect, scale, color, textStyle);" in source
	assert "case CG_1STPLACE:" in source
	assert "case CG_2NDPLACE:" in source
	assert "CG_DrawScoreValue( &rect, scale, color, shader, textStyle, ownerDraw );" in source
	assert "static void CG_Draw1stPlace(" not in source
	assert "static void CG_Draw2ndPlace(" not in source
	assert "case CG_FOLLOW_PLAYER_NAME:" in source
	assert "CG_DrawFollowPlayerNameEx(&rect, scale, color, textStyle, ownerDraw, align);" in source
	assert "case CG_FOLLOW_PLAYER_NAME_EX:" in source
	for expected in (
		"case CG_SELECTED_PLYR_TEAM_COLOR:",
		"CG_DrawSelectedPlayerTeamColor(&rect);",
		"case CG_SELECTED_PLYR_ACCURACY:",
		"CG_DrawSelectedPlayerAccuracy(&rect, scale, color, textStyle);",
		"case CG_PLYR_BEST_WEAPON_NAME:",
		"CG_DrawSelectedPlayerBestWeapon(&rect, scale, color, textStyle);",
		"case CG_MATCH_WINNER:",
		"CG_DrawMatchWinner( &rect, text_x, text_y, scale, color, textStyle );",
		"case CG_PLYR_END_GAME_SCORE:",
		"CG_DrawEndGameScore( &rect, text_x, text_y, scale, color, textStyle );",
		"case CG_AREA_NEW_CHAT:",
		"CG_DrawNewChatArea(&rect, scale, color, textStyle);",
	):
		assert expected in source


def test_cgame_objective_ownerdraws_restore_retail_flag_key_and_powerup_seam() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	harvester_block = _block_from_marker(source, "static void CG_HarvesterSkulls")
	oneflag_block = _block_from_marker(source, "static void CG_OneFlagStatus")
	powerup_block = _block_from_marker(source, "static void CG_DrawCTFPowerUp")
	key_block = _block_from_marker(source, "static void CG_DrawPlayerHasKey")
	flag_block = _block_from_marker(source, "static void CG_DrawPlayerHasFlag")

	assert "value = cg.snap->ps.generic1 & 0x3f;" in harvester_block
	assert "value = cg.snap->ps.stats[STAT_PERSISTANT_POWERUP];" in powerup_block
	assert "if ( value <= 0 || value >= bg_numItems ) {" in powerup_block
	assert "cgs.gametype < GT_CTF" not in powerup_block
	assert "mask = cg.snap->ps.stats[STAT_KEY_MASK];" in key_block
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
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	bar_fraction_block = _block_from_marker(source, "static float CG_BarValueFraction")
	bar_right_block = _block_from_marker(source, "static void CG_DrawBarFillFromRight")
	bar_bottom_block = _block_from_marker(source, "static void CG_DrawBarFillFromBottom")
	health_100_block = _block_from_marker(source, "static void CG_DrawPlayerHealthBar100")
	health_200_block = _block_from_marker(source, "static void CG_DrawPlayerHealthBar200")
	armor_100_block = _block_from_marker(source, "static void CG_DrawPlayerArmorBar100")
	armor_200_block = _block_from_marker(source, "static void CG_DrawPlayerArmorBar200")
	armor_icon_block = _block_from_marker(source, "static void CG_DrawPlayerArmorIcon")
	armor_value_block = _block_from_marker(source, "static void CG_DrawPlayerArmorValue")
	ammo_icon_block = _block_from_marker(source, "static void CG_DrawPlayerAmmoIcon")
	ammo_value_block = _block_from_marker(source, "static void CG_DrawPlayerAmmoValue")
	health_block = _block_from_marker(source, "static void CG_DrawPlayerHealth")
	head_block = _block_from_marker(source, "static void CG_DrawPlayerHead")
	item_block = _block_from_marker(source, "static void CG_DrawPlayerItem")
	tiered_block = _block_from_marker(source, "static void CG_DrawArmorTieredColorized")
	team_colorized_block = _block_from_marker(source, "static void CG_DrawTeamColorized")
	constants = _menudef_ownerdraw_constants()
	retail_health_block = _text_between(
		hlil_source,
		"1002fdf0    void __convention(\"regparm\") sub_1002fdf0",
		"1002ff50",
	)
	retail_armor_value_block = _text_between(
		hlil_source,
		"1002e500    void __convention(\"regparm\") sub_1002e500",
		"1002e660",
	)
	retail_ammo_value_block = _text_between(
		hlil_source,
		"1002e7c0    int32_t __convention(\"regparm\") sub_1002e7c0",
		"1002e9b0",
	)

	assert (
		"return Com_Clamp( 0.0f, (float)maximum, (float)value ) / (float)maximum;"
		in bar_fraction_block
	)

	for expected in (
		"x = rect->x + rect->w - w;",
		"trap_R_DrawStretchPic( x, y, w, h, s1, 0.0f, 1.0f, 1.0f, shader );",
	):
		assert expected in bar_right_block

	for expected in (
		"y = rect->y + rect->h - h;",
		"trap_R_DrawStretchPic( x, y, w, h, 0.0f, t1, 1.0f, 1.0f, shader );",
	):
		assert expected in bar_bottom_block

	for expected in (
		"maxHealth = CG_PlayerMaxHealth();",
		"Vector4Copy( CG_TeamColor( cg.snap->ps.persistant[PERS_TEAM] ), barColor );",
		"ratio = CG_BarValueFraction( health, maxHealth );",
		"shader = cgs.media.healthBar100;",
		"CG_DrawBarFill( rect, shader, ratio, barColor );",
	):
		assert expected in health_100_block

	for expected in (
		"excessHealth = health - maxHealth;",
		"if ( excessHealth <= 0 ) {",
		"Vector4Copy( CG_TeamColor( cg.snap->ps.persistant[PERS_TEAM] ), barColor );",
		"ratio = CG_BarValueFraction( excessHealth, maxHealth );",
		"shader = cgs.media.healthBar200;",
		"CG_DrawBarFillFromBottom( rect, shader, ratio, barColor );",
	):
		assert expected in health_200_block

	for expected in (
		"Vector4Copy( CG_TeamColor( cg.snap->ps.persistant[PERS_TEAM] ), barColor );",
		"ratio = CG_BarValueFraction( armor, 100 );",
		"shader = cgs.media.armorBar100;",
		"CG_DrawBarFillFromRight( rect, shader, ratio, barColor );",
	):
		assert expected in armor_100_block

	for expected in (
		"excessArmor = armor - 100;",
		"if ( excessArmor <= 0 ) {",
		"Vector4Copy( CG_TeamColor( cg.snap->ps.persistant[PERS_TEAM] ), barColor );",
		"ratio = CG_BarValueFraction( excessArmor, 100 );",
		"shader = cgs.media.armorBar200;",
		"CG_DrawBarFillFromBottom( rect, shader, ratio, barColor );",
	):
		assert expected in armor_200_block

	for expected in (
		"cgs.media.armorIcon",
		"cgs.media.armorModel",
		"CG_Draw3DModel( rect->x, rect->y, rect->w, rect->h, cgs.media.armorModel, 0, origin, angles );",
	):
		assert expected in armor_icon_block

	for expected in (
		"value = ps->stats[STAT_ARMOR];",
		"if ( shader ) {",
		"trap_R_SetColor( color );",
		"CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );",
		"trap_R_SetColor( NULL );",
		'Com_sprintf( num, sizeof( num ), "%i", value );',
		"x = rect->x;",
		"y = rect->y + CG_Text_Height( num, scale, 0 );",
		"CG_AlignTextX( &x, num, scale, align );",
		"CG_Text_Paint( x, y, scale, color, num, 0, 0, textStyle );",
	):
		assert expected in armor_value_block
	assert _retail_cg_ownerdraw_cases_for_target("FUN_1002e500") == {
		constants["CG_PLAYER_ARMOR_VALUE"],
	}
	for expected in (
		"int32_t ebp = *(data_10a6f8c4 + 0xfc)",
		"if (arg1 != 0)",
		"(*(data_1074cccc + 0x138))(arg6)",
		"sub_100126a0(fconvert.s(fconvert.t(*ebx)))",
		"eax_2, ecx_3 = sub_100575e0(&data_100687a8)",
		"if (arg8 == 1)",
		"else if (arg8 == 2)",
		"sub_100082b0(eax_3, 0, eax_3, nullptr, &var_4, 0, fconvert.s(fconvert.t(arg5)))",
		"var_4 = fconvert.s(fconvert.t(ebx[1]) + float.t(var_4))",
		"sub_10008440(fconvert.s(fconvert.t(*ebx)), fconvert.s(fconvert.t(var_4)), arg4,",
	):
		assert expected in retail_armor_value_block

	for expected in (
		"weapon = cg.predictedPlayerState.weapon;",
		"cg_weapons[ weapon ].ammoIcon",
		"weapon = cent->currentState.weapon;",
		"cg_weapons[ weapon ].ammoModel",
		"CG_Draw3DModel( rect->x, rect->y, rect->w, rect->h, cg_weapons[ weapon ].ammoModel, 0, origin, angles );",
	):
		assert expected in ammo_icon_block

	assert _retail_cg_ownerdraw_cases_for_target("FUN_1002e7c0") == {
		constants["CG_PLAYER_AMMO_VALUE"],
	}
	for expected in (
		"int32_t result = *(*(ecx_1 + 0xb4) * 0x2d0 + 0x10abbb90)",
		"if (result != 0 && result != 1 && result != 0xa)",
		"int32_t esi_1 = *(ecx_1 + (result << 2) + 0x1ac)",
		"if (esi_1 s> 0xffffffff)",
		"if (arg5 != 0)",
		"sub_100575e0(&data_100687a8)",
		"if (esi_1 == 0xffffffff)",
		"if (arg7 == 1)",
		"else if (arg7 == 2)",
		"data_10a5f4e8",
		"arg1[3]",
	):
		assert expected in retail_ammo_value_block
	for expected in (
		"weapon = cent->currentState.weapon;",
		"if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {",
		"if ( weapon == WP_GAUNTLET || weapon == WP_GRAPPLING_HOOK ) {",
		"value = ps->ammo[weapon];",
	):
		assert expected in ammo_value_block
	for expected in (
		"if ( value == -1 ) {",
		"if ( cgs.media.infiniteAmmoShader ) {",
		"iconSize = rect->w;",
		"if ( align == ITEM_ALIGN_CENTER ) {",
		"} else if ( align == ITEM_ALIGN_RIGHT ) {",
		"CG_DrawPic( iconX, rect->y, iconSize, iconSize, cgs.media.infiniteAmmoShader );",
		"return;",
	):
		assert expected in ammo_value_block
	assert "iconSize = ( rect->h > 0.0f ) ? rect->h : rect->w;" not in ammo_value_block
	for expected in (
		"x = rect->x;",
		"y = rect->y + CG_Text_Height( num, scale, 0 );",
		"CG_AlignTextX( &x, num, scale, align );",
		"CG_Text_Paint( x, y, scale, color, num, 0, 0, textStyle );",
	):
		assert expected in ammo_value_block

	for expected in (
		"x = rect->x;",
		"value = ps->stats[STAT_HEALTH];",
		"if (shader) {",
		"trap_R_SetColor( color );",
		"CG_DrawPic(rect->x, rect->y, rect->w, rect->h, shader);",
		"trap_R_SetColor( NULL );",
		'Com_sprintf (num, sizeof(num), "%i", value);',
		"y = rect->y + CG_Text_Height( num, scale, 0 );",
		"CG_AlignTextX( &x, num, scale, align );",
		"CG_Text_Paint( x, y, scale, color, num, 0, 0, textStyle );",
	):
		assert expected in health_block
	assert _retail_cg_ownerdraw_cases_for_target("FUN_1002fdf0") == {
		constants["CG_PLAYER_HEALTH"],
	}
	for expected in (
		"int32_t ebp = *(data_10a6f8c4 + 0xec)",
		"if (arg1 != 0)",
		"(*(data_1074cccc + 0x138))(arg6)",
		"sub_100126a0(fconvert.s(fconvert.t(*ebx)))",
		"eax_2, ecx_3 = sub_100575e0(&data_100687a8)",
		"if (arg8 == 1)",
		"else if (arg8 == 2)",
		"sub_100082b0(eax_3, 0, eax_3, nullptr, &var_4, 0, fconvert.s(fconvert.t(arg5)))",
		"var_4 = fconvert.s(fconvert.t(ebx[1]) + float.t(var_4))",
		"sub_10008440(fconvert.s(fconvert.t(*ebx)), fconvert.s(fconvert.t(var_4)), arg4,",
	):
		assert expected in retail_health_block

	assert "CG_DrawHead( x, rect->y, rect->w, rect->h, cg.snap->ps.clientNum, angles );" in head_block

	for expected in (
		"value = cg.snap->ps.stats[STAT_HOLDABLE_ITEM];",
		"BG_HoldableForItemTag( bg_itemlist[ value ].giTag ) == HI_INVULNERABILITY",
		"cg.snap->ps.stats[STAT_PLAYER_ITEM_TIME] > 0",
		"cg.snap->ps.stats[STAT_PLAYER_ITEM_TIME_MAX] > 0",
		"progressPercent = (int)( ( cg.snap->ps.stats[STAT_PLAYER_ITEM_TIME] * 100.0f ) / cg.snap->ps.stats[STAT_PLAYER_ITEM_TIME_MAX] + 0.5f );",
		"progressPercent = 0;",
		"progressPercent = 100;",
		'Com_sprintf( progressText, sizeof( progressText ), "%d%%", progressPercent );',
		"progressScale = scale * 0.25f;",
		"progressWidth = CG_Text_Width( progressText, progressScale, 0 );",
		"CG_Text_Paint( rect->x + ( rect->w - progressWidth ) * 0.5f, rect->y + rect->h, progressScale,",
	):
		assert expected in item_block

	for expected in (
		"CG_GetArmorTierColorForTier( cg.snap->ps.stats[STAT_ARMOR_TIER], color );",
		"color[3] = 0.5f;",
		"CG_FillRect( rect->x, rect->y, rect->w, rect->h, color );",
	):
		assert expected in tiered_block

	for expected in (
		"if ( !rect ) {",
		"Vector4Copy( CG_TeamColor( team ), color );",
		"color[3] = itemColor[3];",
		"trap_R_SetColor( color );",
	):
		assert expected in team_colorized_block
	assert "CG_DrawTeamColorized( &rect, color, teamShader );" in source

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
		"CG_DrawPlayerArmorValue( &rect, scale, color, shader, textStyle, align );",
		"case CG_PLAYER_AMMO_ICON:",
		"CG_DrawPlayerAmmoIcon( &rect, ownerDrawFlags & CG_SHOW_2DONLY );",
		"case CG_PLAYER_AMMO_VALUE:",
		"CG_DrawPlayerAmmoValue( &rect, scale, color, shader, textStyle, align );",
		"case CG_PLAYER_HEAD:",
		"CG_DrawPlayerHead( &rect, ownerDrawFlags & CG_SHOW_2DONLY );",
		"case CG_PLAYER_ITEM:",
		"CG_DrawPlayerItem( &rect, scale, ownerDrawFlags & CG_SHOW_2DONLY );",
		"case CG_PLAYER_HEALTH:",
		"CG_DrawPlayerHealth( &rect, scale, color, shader, textStyle, align );",
	):
		assert expected in source


def test_cgame_team_score_name_playercount_and_match_phase_ownerdraws_follow_retail_shared_leaves() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	align_block = _block_from_marker(source, "static float CG_AlignTextInRectX")
	score_text_block = _block_from_marker(source, "static qboolean CG_BuildTeamScoreText")
	score_block = _block_from_marker(source, "static void CG_DrawTeamScore")
	name_block = _block_from_marker(source, "static void CG_DrawTeamName")
	player_count_block = _block_from_marker(source, "static void CG_DrawTeamPlayerCount")
	round_team_count_block = _block_from_marker(source, "static int CG_GetRoundTeamCount")
	clan_arena_block = _block_from_marker(source, "static void CG_DrawClanArenaPlayers")
	round_player_count_team_block = _block_from_marker(source, "static team_t CG_GetRoundPlayerCountTeam")
	round_player_count_block = _block_from_marker(source, "static void CG_DrawPlayerCount( rectDef_t")
	timeout_count_block = _block_from_marker(source, "static void CG_DrawTeamTimeoutCount")
	domination_count_block = _block_from_marker(source, "static int CG_CountDominationOwnedFlags")
	domination_flags_block = _block_from_marker(source, "static void CG_DrawDominationOwnedFlags")
	round_label_block = _block_from_marker(source, "static void CG_DrawRoundLabel")
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	game_type_block = _block_from_marker(source, "static void CG_DrawGameType( rectDef_t")
	match_phase_block = _block_from_marker(source, "static const char *CG_GetMatchPhaseText")
	match_status_block = _block_from_marker(source, "const char *CG_GetMatchStatusText")
	draw_match_status_block = _block_from_marker(source, "static void CG_DrawMatchStatus")
	match_state_block = _block_from_marker(source, "static void CG_DrawMatchState")
	retail_match_state_block = _text_between(
		hlil_source,
		"10034360    int32_t sub_10034360",
		"100343d0",
	)
	retail_game_type_block = _text_between(
		hlil_source,
		"10034c20    int32_t sub_10034c20",
		"10034cc0",
	)
	retail_round_player_count_block = _text_between(
		hlil_source,
		'10033650    int32_t __convention("regparm") sub_10033650',
		"100336e0",
	)
	retail_clan_arena_block = _text_between(
		hlil_source,
		'100335f0    int32_t __convention("regparm") sub_100335f0',
		"10033650",
	)
	retail_timeout_count_block = _text_between(
		hlil_source,
		'10033530    void __convention("regparm") sub_10033530',
		"100335f0",
	)
	retail_round_label_block = _text_between(
		hlil_source,
		"100336e0    void sub_100336e0",
		"100337a0",
	)
	retail_domination_flags_block = _text_between(
		hlil_source,
		'100337a0    int32_t __convention("regparm") sub_100337a0',
		"10033800",
	)

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

	assert "int32_t var_c = *((arg2 << 2) + &data_10a404b8)" in retail_clan_arena_block
	assert "10068e44              25 64 00 00" in hlil_source
	assert "return cgs.matchTeamCount[team];" in round_team_count_block
	assert "CG_CountPlayersForTeam" not in round_team_count_block
	assert "count > 0" not in round_team_count_block
	assert "count = CG_GetRoundTeamCount( team );" in clan_arena_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%d", count );' in clan_arena_block
	assert "CG_GetTeamLabel" not in clan_arena_block
	assert "players" not in clan_arena_block

	assert "int32_t eax_1 = *(data_10a6f8c4 + 0x138)" in retail_round_player_count_block
	assert "if (arg4 == 0)" in retail_round_player_count_block
	assert "eax_1 = 2" in retail_round_player_count_block
	assert "eax_1 = 1" in retail_round_player_count_block
	assert "int32_t var_8 = *((eax_1 << 2) + &data_10a404b8)" in retail_round_player_count_block

	for expected in (
		"team = (team_t)cg.predictedPlayerState.persistant[PERS_TEAM];",
		"if ( !friendly ) {",
		"if ( team == TEAM_RED ) {",
		"team = TEAM_BLUE;",
		"team = TEAM_RED;",
		"return TEAM_FREE;",
	):
		assert expected in round_player_count_team_block

	assert "cg.snap->ps.persistant[PERS_TEAM]" not in round_player_count_team_block
	assert "if ( !rect ) {" in round_player_count_block
	assert "team = CG_GetRoundPlayerCountTeam( friendly );" in round_player_count_block
	assert "count = ( team == TEAM_RED || team == TEAM_BLUE ) ? cgs.matchTeamCount[team] : 0;" in round_player_count_block
	assert "CG_CountLivingPlayers" not in round_player_count_block
	assert "friendCount" not in round_player_count_block
	assert "enemyCount" not in round_player_count_block
	assert "static void CG_CountLivingPlayers" not in source

	for expected in (
		"remaining = cgs.matchTimeoutRemaining[team];",
		'Com_sprintf( buffer, sizeof( buffer ), "TO: %d", remaining );',
		"x = CG_AlignTextInRectX( rect, scale, buffer, align );",
		"CG_Text_Paint( x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );",
	):
		assert expected in timeout_count_block

	for expected in (
		"int32_t var_10 = *((arg1 << 2) + &data_10a404d8)",
		"int32_t eax_1 = sub_100575e0(&data_10068de8)",
		"if (edx == 1)",
		"*ebx = fconvert.s(fconvert.t(*ebx) - float.t(arg_10) * fconvert.t(0.5))",
		"else if (edx == 2)",
		"*ebx = fconvert.s(fconvert.t(*ebx) - float.t(arg_10))",
	):
		assert expected in retail_timeout_count_block

	assert "if ( cgs.gametype != GT_DOMINATION && cgs.gametype != GT_ATTACK_DEFEND ) {" in domination_count_block
	assert "!cg.snap" not in domination_count_block
	assert "return cgs.dominationOwnedPointCount[team];" in domination_count_block
	assert "int32_t var_c = *((arg2 << 2) + &data_10a404c8)" in retail_domination_flags_block
	assert "eax_1, ecx_1 = sub_100575e0(&data_10068e44)" in retail_domination_flags_block
	assert "owned = CG_CountDominationOwnedFlags( team );" in domination_flags_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%d", owned );' in domination_flags_block
	assert "CG_GetTeamLabel" not in domination_flags_block
	assert "flags" not in domination_flags_block

	for expected in (
		"int32_t eax_3 = data_10ab8f58",
		"if (eax_3 s<= 0)",
		'ebp = "Warmup"',
		'ebp = sub_100575e0("Round %d")',
		"int32_t eax_1 = sub_100575e0(&data_10068de8)",
		"if (edx == 1)",
		"*ebx = fconvert.s(fconvert.t(*ebx) - float.t(arg_10) * fconvert.t(0.5))",
		"else if (edx == 2)",
		"*ebx = fconvert.s(fconvert.t(*ebx) - float.t(arg_10))",
	):
		assert expected in retail_round_label_block

	for expected in (
		"if ( cgs.matchRoundNumber > 0 ) {",
		'Com_sprintf( label, sizeof( label ), "Round %d", cgs.matchRoundNumber );',
		'Q_strncpyz( label, "Warmup", sizeof( label ) );',
		"x = CG_AlignTextInRectX( rect, scale, label, align );",
		"CG_Text_Paint( x, rect->y + rect->h, scale, color, label, 0, 0, textStyle );",
	):
		assert expected in round_label_block

	assert "cgs.matchRoundState" not in round_label_block
	assert "cg.warmup" not in round_label_block
	assert "CG_GetTextPosition" not in round_label_block
	assert "if ( !label[0] )" not in round_label_block
	assert "CG_GetMatchStateLabel();" not in round_label_block

	for expected in (
		'return "MATCH SUMMARY";',
		'return "MATCH WARMUP";',
		'return "MATCH IN PROGRESS";',
	):
		assert expected in match_phase_block

	for expected in (
		"if ( cg.snap && cg.snap->ps.pm_type == PM_INTERMISSION ) {",
		"if ( cgs.scores1 == SCORE_NOT_PRESENT && cgs.scores2 == SCORE_NOT_PRESENT &&",
		"if ( cgs.gametype == GT_RACE ) {",
		"if ( cgs.gametype >= GT_TEAM && cgs.gametype != GT_RED_ROVER ) {",
		"cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR",
	):
		assert expected in match_status_block
	assert "CG_GetGameStatusText()" not in match_status_block
	assert "CG_AlignTextX( &x, statusText, scale, align );" in draw_match_status_block
	assert "CG_Text_Paint( x, rect->y, scale, color, statusText, 0, 0, textStyle );" in draw_match_status_block
	assert "CG_GetTextPosition" not in draw_match_status_block
	for expected in (
		"if (arg5 == 1)",
		"sub_100082b0(0, 0, ebx, &arg1, nullptr, 0, fconvert.s(fconvert.t(arg2)))",
		"arg1 = fconvert.s(x87_r7_5 - float.t(arg1))",
		"float var_28 = fconvert.s(fconvert.t(*(ebp + 4)))",
	):
		assert expected in retail_game_type_block
	assert "else if (arg5 == 2)" not in retail_game_type_block
	assert "gameType = CG_GameTypeString();" in game_type_block
	assert "if ( align == ITEM_ALIGN_CENTER ) {" in game_type_block
	assert "x -= CG_Text_Width( gameType, scale, 0 ) * 0.5f;" in game_type_block
	assert "CG_Text_Paint( x, rect->y, scale, color, gameType, 0, 0, textStyle );" in game_type_block
	assert "ITEM_ALIGN_RIGHT" not in game_type_block
	assert "rect->y + rect->h" not in game_type_block
	assert "qhandle_t shader" not in game_type_block
	assert "fconvert.s(fconvert.t(arg1[1]))" in retail_match_state_block
	assert "arg1[3]" not in retail_match_state_block
	assert "CG_Text_Paint( rect->x, rect->y, scale, color, CG_GetMatchPhaseText(), 0, 0, textStyle );" in match_state_block
	assert "rect->y + rect->h" not in match_state_block
	assert "CG_DrawGameType( &rect, scale, color, textStyle, align );" in ownerdraw_block
	assert "CG_DrawGameType(&rect, scale, color, shader, textStyle);" not in ownerdraw_block
	assert ownerdraw_block.count("if ( CG_ShowPlayersRemaining() ) {") >= 5

	start = ownerdraw_block.index("case CG_ROUND:")
	end = ownerdraw_block.index("break;", start)
	round_case_block = ownerdraw_block[start:end]
	assert "if ( CG_ShowPlayersRemaining() ) {" in round_case_block
	assert "CG_DrawRoundLabel( &rect, scale, color, textStyle, align );" in round_case_block

	for marker, expected in (
		("case CG_RED_OWNED_FLAGS:", "CG_DrawDominationOwnedFlags(&rect, scale, color, textStyle, TEAM_RED);"),
		("case CG_BLUE_OWNED_FLAGS:", "CG_DrawDominationOwnedFlags(&rect, scale, color, textStyle, TEAM_BLUE);"),
	):
		start = ownerdraw_block.index(marker)
		end = ownerdraw_block.index("break;", start)
		case_block = ownerdraw_block[start:end]
		assert "if ( cgs.gametype == GT_DOMINATION || cgs.gametype == GT_ATTACK_DEFEND ) {" in case_block
		assert expected in case_block

	for marker, expected in (
		("case CG_RED_TIMEOUT_COUNT:", "CG_DrawTeamTimeoutCount( &rect, scale, color, textStyle, TEAM_RED, align );"),
		("case CG_BLUE_TIMEOUT_COUNT:", "CG_DrawTeamTimeoutCount( &rect, scale, color, textStyle, TEAM_BLUE, align );"),
	):
		start = ownerdraw_block.index(marker)
		end = ownerdraw_block.index("break;", start)
		case_block = ownerdraw_block[start:end]
		assert "if ( cgs.playerCountTeamSize > 0 ) {" in case_block
		assert expected in case_block

	for marker, expected in (
		("case CG_RED_CLAN_PLYRS:", "CG_DrawClanArenaPlayers(&rect, scale, color, textStyle, TEAM_RED);"),
		("case CG_BLUE_CLAN_PLYRS:", "CG_DrawClanArenaPlayers(&rect, scale, color, textStyle, TEAM_BLUE);"),
		("case CG_TEAM_PLYR_COUNT:", "CG_DrawPlayerCount(&rect, scale, color, textStyle, qtrue);"),
		("case CG_ENEMY_PLYR_COUNT:", "CG_DrawPlayerCount(&rect, scale, color, textStyle, qfalse);"),
	):
		start = ownerdraw_block.index(marker)
		end = ownerdraw_block.index("break;", start)
		case_block = ownerdraw_block[start:end]
		assert "if ( CG_ShowPlayersRemaining() ) {" in case_block
		assert expected in case_block

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
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	active_count_block = _block_from_marker(newdraw_source, "static int CG_CountActivePlayers")
	player_limit_block = _block_from_marker(newdraw_source, "static int CG_GetConfiguredPlayerCountLimit")
	player_counts_block = _block_from_marker(newdraw_source, "static void CG_DrawPlayerCounts")
	ownerdraw_block = _block_from_marker(newdraw_source, "void CG_OwnerDraw(")
	retail_player_counts_block = _text_between(hlil_source, "10032f30    void sub_10032f30", "10033040")
	location_block = _block_from_marker(newdraw_source, "static void CG_GetServerLocation")
	detail_block = _block_from_marker(newdraw_source, "static void CG_BuildIntroPanelDetailString")
	game_type_map_block = _block_from_marker(newdraw_source, "static void CG_DrawGameTypeMap")
	match_details_block = _block_from_marker(newdraw_source, "static void CG_DrawMatchDetails")
	parse_serverinfo_block = _block_from_marker(servercmds_source, "void CG_ParseServerinfo")

	assert "playerCountTeamSize;" in local_source

	for expected in (
		"playerLimit = cgs.maxclients;",
		"if ( cgs.gametype == GT_FFA || cgs.gametype == GT_TOURNAMENT || cgs.playerCountTeamSize <= 0 ) {",
		"playerLimit = cgs.playerCountTeamSize * 2;",
		"if ( playerLimit > cgs.maxclients ) {",
		"return cgs.playerCountTeamSize;",
	):
		assert expected in player_limit_block

	assert "if (esi_1 == 1 || i_4 == 0)" in retail_player_counts_block
	assert "if (esi_1 s>= 3)" in retail_player_counts_block
	assert "if (*eax_1 != 0)" in retail_player_counts_block
	assert "fconvert.t(*(ebp + 4))" in retail_player_counts_block

	assert "for ( i = 0; i < cgs.maxclients && i < MAX_CLIENTS; i++ )" in active_count_block
	assert "cgs.clientinfo[i].infoValid" in active_count_block
	assert "cg.numScores" not in active_count_block
	assert "TEAM_SPECTATOR" not in active_count_block

	for expected in (
		"active = CG_CountActivePlayers();",
		"playerLimit = CG_GetConfiguredPlayerCountLimit();",
		"if ( playerLimit <= 0 ) {",
		'Com_sprintf( buffer, sizeof( buffer ), "%i/%i Players", active, playerLimit );',
		"x = rect->x;",
		"CG_AlignTextX( &x, buffer, scale, align );",
		"CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );",
	):
		assert expected in player_counts_block

	assert "rect->y + rect->h" not in player_counts_block
	assert "CG_DrawPlayerCounts(&rect, scale, color, textStyle, align);" in ownerdraw_block

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
	assert "CG_AlignTextX( &x, buffer, scale, align );" in game_type_map_block
	assert "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );" in game_type_map_block
	assert "CG_GetMapDisplayName( mapName, sizeof( mapName ) );" not in game_type_map_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%s - %s", CG_GameTypeString(), mapName );' not in game_type_map_block
	assert "CG_GetTextPosition" not in game_type_map_block
	assert "CG_BuildIntroPanelDetailString( detailBuffer, sizeof( detailBuffer ) );" in match_details_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%s - %s - %s",' in match_details_block
	assert "CG_GameTypeShortString(), detailBuffer );" in match_details_block
	assert "CG_Text_Paint( rect->x, rect->y, scale, color, buffer, 0, 0, textStyle );" in match_details_block
	assert "CG_GetMapDisplayName( mapName, sizeof( mapName ) );" not in match_details_block
	assert "CG_GameTypeShortString(), mapName );" not in match_details_block
	assert "CG_GetTextPosition" not in match_details_block

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
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	build_spectator_block = _block_from_marker(main_source, "void CG_BuildSpectatorString()")
	speedometer_core_block = _block_from_marker(newdraw_source, "static void CG_DrawSpeedometer(rectDef_t")
	speedometer_block = _block_from_marker(newdraw_source, "static void CG_DrawSpeedometerOwnerDraw")
	spectator_block = _block_from_marker(newdraw_source, "void CG_DrawTeamSpectators")
	advert_block = _block_from_marker(newdraw_source, "static void CG_DrawAdvert")
	medal_block = _block_from_marker(newdraw_source, "void CG_DrawMedal")
	retail_medal_block = _text_between(
		hlil_source,
		'10035340    int32_t __convention("regparm") sub_10035340',
		"1003550b",
	)
	accuracy_start = medal_block.index("if ( ownerDraw == CG_ACCURACY ) {")
	accuracy_block = medal_block[accuracy_start:medal_block.index("} else {", accuracy_start)]
	powerup_stack_block = _block_from_marker(newdraw_source, "static void CG_DrawPowerupSpriteStack")
	area_powerup_block = _block_from_marker(newdraw_source, "static void CG_DrawAreaPowerUp")
	team_color_block = _block_from_marker(newdraw_source, "static void CG_DrawTeamColor")
	team_pickup_block = _block_from_marker(newdraw_source, "static void CG_DrawTeamPickupOwnerDraw")
	ownerdraw_block = _block_from_marker(newdraw_source, "void CG_OwnerDraw(")
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

	assert "if ( !rect || !CG_ShouldDrawSpeedometer() ) {" in speedometer_core_block
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

	start = ownerdraw_block.index("case CG_KILLER:")
	end = ownerdraw_block.index("break;", start)
	killer_case_block = ownerdraw_block[start:end]
	assert "if ( cg.killerName[0] ) {" in killer_case_block
	assert "CG_DrawKiller(&rect, scale, color, shader, textStyle);" in killer_case_block

	start = ownerdraw_block.index("case CG_SPECTATORS:")
	end = ownerdraw_block.index("break;", start)
	spectators_case_block = ownerdraw_block[start:end]
	assert "if ( cg.spectatorEntryCount > 0 ) {" in spectators_case_block
	assert "CG_DrawTeamSpectators(&rect, scale, color, shader);" in spectators_case_block

	for expected in (
		"trap_R_SetColor( color );",
		"CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );",
		"pixelArea = (int)( rect->w * rect->h );",
		"trap_QL_UpdateAdvert( shader, pixelArea );",
		"trap_R_SetColor( NULL );",
	):
		assert expected in advert_block

	for expected in (
		"if ( !rect || cg.selectedScore < 0 || cg.selectedScore >= cg.numScores || cg.selectedScore >= MAX_CLIENTS ) {",
		"case CG_ACCURACY:",
		'text = va( "%i%%", (int)value );',
		'text = "Wow";',
		"CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );",
	):
		assert expected in medal_block

	for expected in (
		"case 0x40",
		"xmm0_1 = float.s(*(eax_2 + 0xac))",
		'ebp = sub_100575e0("%i%%")',
		"*(arg6 i+ 0xc) = 0x3f800000",
	):
		assert expected in retail_medal_block
	assert 'text = va( "%i%%", (int)value );' in accuracy_block
	assert "color[3] = 1.0;" in accuracy_block
	assert "value > 50" not in accuracy_block

	for stale_medal in ("CG_COMBOKILLS", "CG_RAMPAGES", "CG_MIDAIRS"):
		assert stale_medal not in medal_block

	for expected in (
		"if ( !rect || !cg.snap ) {",
		"CG_DrawTeamBackground( rect->x, rect->y, rect->w, rect->h, color[3], cg.snap->ps.persistant[PERS_TEAM] );",
	):
		assert expected in team_color_block

	for expected in (
		"for ( i = 1; i < MAX_POWERUPS; i++ ) {",
		"if ( i == PW_NEUTRALFLAG || i == PW_NUM_POWERUPS ) {",
		"if ( !ps->powerups[i] || ps->powerups[i] == 0x7fffffff ) {",
		"if ( t <= 0 || t >= 999000 ) {",
		"for ( j = active; j > 0 && t < sortedTime[j - 1]; j-- ) {",
		'Com_sprintf(num, sizeof(num), "%i", sortedTime[i] / 1000 + 1);',
	):
		assert expected in powerup_stack_block

	assert "if ( !rect || !cg.snap || !cg_drawSprites.integer ) {" in area_powerup_block

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


def test_cgame_team_pickup_timeheld_and_medal_dispatch_groups_match_retail_switch() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	constants = _menudef_ownerdraw_constants()
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	medal_block = ownerdraw_block[
		ownerdraw_block.index("case CG_ACCURACY:"):
		ownerdraw_block.index("case CG_SPECTATORS:")
	]
	pickup_block = ownerdraw_block[
		ownerdraw_block.index("case CG_RED_TEAM_MAP_PICKUPS:"):
		ownerdraw_block.index("case CG_RED_TEAM_TIMEHELD_QUAD:")
	]
	timeheld_block = ownerdraw_block[
		ownerdraw_block.index("case CG_RED_TEAM_TIMEHELD_QUAD:"):
		ownerdraw_block.index("case CG_MATCH_WINNER:")
	]
	medal_names = {
		"CG_ACCURACY",
		"CG_ASSISTS",
		"CG_CAPTURES",
		"CG_DEFEND",
		"CG_EXCELLENT",
		"CG_GAUNTLET",
		"CG_IMPRESSIVE",
		"CG_PERFECT",
	}
	pickup_names = {
		"CG_RED_TEAM_MAP_PICKUPS",
		"CG_RED_TEAM_PICKUPS_RA",
		"CG_RED_TEAM_PICKUPS_YA",
		"CG_RED_TEAM_PICKUPS_GA",
		"CG_RED_TEAM_PICKUPS_MH",
		"CG_RED_TEAM_PICKUPS_QUAD",
		"CG_RED_TEAM_PICKUPS_BS",
		"CG_RED_TEAM_PICKUPS_FLAG",
		"CG_RED_TEAM_PICKUPS_MEDKIT",
		"CG_RED_TEAM_PICKUPS_REGEN",
		"CG_RED_TEAM_PICKUPS_HASTE",
		"CG_RED_TEAM_PICKUPS_INVIS",
		"CG_BLUE_TEAM_MAP_PICKUPS",
		"CG_BLUE_TEAM_PICKUPS_RA",
		"CG_BLUE_TEAM_PICKUPS_YA",
		"CG_BLUE_TEAM_PICKUPS_GA",
		"CG_BLUE_TEAM_PICKUPS_MH",
		"CG_BLUE_TEAM_PICKUPS_QUAD",
		"CG_BLUE_TEAM_PICKUPS_BS",
		"CG_BLUE_TEAM_PICKUPS_FLAG",
		"CG_BLUE_TEAM_PICKUPS_MEDKIT",
		"CG_BLUE_TEAM_PICKUPS_REGEN",
		"CG_BLUE_TEAM_PICKUPS_HASTE",
		"CG_BLUE_TEAM_PICKUPS_INVIS",
	}
	timeheld_names = {
		"CG_RED_TEAM_TIMEHELD_QUAD",
		"CG_RED_TEAM_TIMEHELD_BS",
		"CG_RED_TEAM_TIMEHELD_FLAG",
		"CG_RED_TEAM_TIMEHELD_REGEN",
		"CG_RED_TEAM_TIMEHELD_HASTE",
		"CG_RED_TEAM_TIMEHELD_INVIS",
		"CG_BLUE_TEAM_TIMEHELD_QUAD",
		"CG_BLUE_TEAM_TIMEHELD_BS",
		"CG_BLUE_TEAM_TIMEHELD_FLAG",
		"CG_BLUE_TEAM_TIMEHELD_REGEN",
		"CG_BLUE_TEAM_TIMEHELD_HASTE",
		"CG_BLUE_TEAM_TIMEHELD_INVIS",
	}

	assert _retail_cg_ownerdraw_cases_for_target("FUN_10035340") == {
		constants[name]
		for name in medal_names
	}
	assert _retail_cg_ownerdraw_cases_for_target("FUN_10037f80") == {
		constants[name]
		for name in pickup_names
	}
	assert _retail_cg_ownerdraw_cases_for_target("FUN_10039ae0") == {
		constants[name]
		for name in timeheld_names
	}

	assert set(_case_labels(medal_block)) == medal_names
	assert set(_case_labels(pickup_block)) == pickup_names
	assert set(_case_labels(timeheld_block)) == timeheld_names
	assert "CG_DrawMedal(ownerDraw, &rect, scale, color, shader);" in medal_block
	assert "CG_DrawTeamPickupOwnerDraw( &rect, scale, color, textStyle, ownerDraw );" in pickup_block
	assert "CG_DrawTeamTimeHeldOwnerDraw( &rect, scale, color, textStyle, ownerDraw );" in timeheld_block

	for stale in timeheld_names:
		assert stale not in pickup_block
	for stale in pickup_names:
		assert stale not in timeheld_block


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
	award_config_block = _block_from_marker(source, "static int CG_AwardConfigStringIndex")
	award_client_block = _block_from_marker(source, "static int CG_GetAwardClientNum")
	award_player_block = _block_from_marker(source, "static qboolean CG_DrawAwardPlayer")

	assert 'Com_sprintf( buffer, sizeof( buffer ), "Avg ping %i", average );' in average_ping_block
	for expected in (
		"Vector4Copy( color, drawColor );",
		"if ( average >= 80 ) {",
		"} else if ( average >= 40 ) {",
		"CG_Text_Paint(rect->x, rect->y + rect->h, scale, drawColor, buffer, 0, 0, textStyle);",
	):
		assert expected in average_ping_block
	assert "if ( !CG_IsTeamTimeHeldOwnerDraw( ownerDraw ) ) {" in timeheld_build_block
	assert 'Q_strncpyz( buffer, CG_FormatMinutesSeconds( value ), bufferSize );' in timeheld_build_block
	assert "CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );" in timeheld_block

	for expected in (
		"case CG_MOST_VALUABLE_OFFENSIVE_PLYR:",
		"return CS_AWARD_MOST_VALUABLE_OFFENSIVE;",
		"case CG_MOST_VALUABLE_DEFENSIVE_PLYR:",
		"return CS_AWARD_MOST_VALUABLE_DEFENSIVE;",
		"case CG_MOST_VALUABLE_PLYR:",
		"return CS_AWARD_MOST_VALUABLE;",
		"case CG_BEST_ITEMCONTROL_PLYR:",
		"return CS_AWARD_BEST_ITEMCONTROL;",
		"case CG_MOST_ACCURATE_PLYR:",
		"return CS_AWARD_MOST_ACCURATE;",
		"case CG_MOST_DAMAGEDEALT_PLYR:",
		"return CS_AWARD_MOST_DAMAGEDEALT;",
	):
		assert expected in award_config_block

	for expected in (
		"configStringIndex = CG_AwardConfigStringIndex( ownerDraw );",
		"configString = CG_ConfigString( configStringIndex );",
		"return atoi( configString );",
	):
		assert expected in award_client_block

	assert "CG_FindAwardScore" not in source
	assert "CG_AwardMetricValue" not in source
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
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	table_decl = _text_between(source, "typedef struct {\n\tvmCvar_t\t*vmCvar;", "} cvarTable_t;")
	cvar_table = source[source.index("static cvarTable_t cvarTable[]"):source.index("static int  cvarTableSize")]
	block = _block_from_marker(source, "void CG_RegisterCvars")
	update_block = _block_from_marker(source, "void CG_UpdateCvars")
	load_hud_block = _block_from_marker(source, "void CG_LoadHudMenu( void )")
	retail_register_block = _text_between(hlil_source, "10020bb0    int32_t sub_10020bb0", "10020c94")
	retail_update_block = _text_between(hlil_source, "10020ca0    int32_t* sub_10020ca0", "10020d5b")
	retail_cvar_table = _text_between(hlil_source, "10076ad8  void* data_10076ad8", "10076da4")
	retail_force_cvar_table = _text_between(hlil_source, "10077468  void* data_10077468", "10077498")
	retail_flags = "CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD"

	assert "const char\t*cvarName;" in table_decl
	assert "const char\t*defaultString;" in table_decl
	assert "const char\t*minimumString;" in table_decl
	assert "const char\t*maximumString;" in table_decl
	assert "static int  cvarTableSize = sizeof( cvarTable ) / sizeof( cvarTable[0] );" in source
	for expected in (
		'{ &cg_autoAction, "cg_autoAction", "0", CVAR_ARCHIVE | CVAR_LATCH },',
		'{ &cg_autoHop, "cg_autoHop", "1", CVAR_ARCHIVE | CVAR_LATCH },',
		'{ &cg_autoProjectileNudge, "cg_autoProjectileNudge", "0", ' + retail_flags + ', "0", "1" },',
		'{ &cg_predictLocalRailshots, "cg_predictLocalRailshots", "1", 0 },',
		'{ &cg_projectileNudge, "cg_projectileNudge", "0", CVAR_CHEAT },',
		'{ &cg_crosshairBrightness, "cg_crosshairBrightness", "1.0", ' + retail_flags + ', "0.0", "1.0" },',
		'{ &cg_crosshairColor, "cg_crosshairColor", "25", ' + retail_flags + ', "1", "26" },',
		'{ &cg_crosshairHealth, "cg_crosshairHealth", "0", ' + retail_flags + ', "0", "1" },',
		'{ &cg_crosshairHitColor, "cg_crosshairHitColor", "1", ' + retail_flags + ', "1", "26" },',
		'{ &cg_crosshairHitStyle, "cg_crosshairHitStyle", "1", ' + retail_flags + ', "0", "8" },',
		'{ &cg_crosshairHitTime, "cg_crosshairHitTime", "200.0", ' + retail_flags + ', "0.0", "1000.0" },',
		'{ &cg_crosshairPulse, "cg_crosshairPulse", "1", ' + retail_flags + ', "0", "1" },',
		'{ &cg_crosshairSize, "cg_crosshairSize", "32", ' + retail_flags + ', "0", "320" },',
		'{ &cg_crosshairX, "cg_crosshairX", "0", ' + retail_flags + ', "-320", "320" },',
		'{ &cg_crosshairY, "cg_crosshairY", "0", ' + retail_flags + ', "-240", "240" },',
		'{ &cg_forceDrawCrosshair, "cg_forceDrawCrosshair", "0", ' + retail_flags + ', "0", "1" },',
	):
		assert expected in cvar_table
	assert 'if ( ( cv->cvarFlags & CVAR_VM_CREATED ) && cv->minimumString && cv->maximumString ) {' in block
	assert 'trap_QL_Cvar_RegisterRange( cv->vmCvar, cv->cvarName,' in block
	assert 'trap_Cvar_Register( cv->vmCvar, cv->cvarName,' in block
	assert 'trap_Cvar_VariableStringBuffer( "sv_running", var, sizeof( var ) );' in block
	assert 'cgs.localServer = atoi( var );' in block
	assert 'trap_Cvar_Register(NULL, "cg_version", Q3_VERSION, CVAR_ROM );' in block
	assert 'trap_Cvar_Set( "ui_voteactive", "0" );' in block
	assert 'trap_Cvar_Set( "ui_votestring", "" );' in block
	assert "trap_Cvar_Update( cv->vmCvar );" in update_block
	assert "CG_UpdateDamagePlumSettings();" in update_block
	assert "CG_UpdateCrosshairColorSettings();" in update_block
	assert "CG_UpdateCrosshairPulseSettings();" in update_block
	assert "CG_UpdateCrosshairHitSettings();" in update_block
	assert "cg.hudMenusLoaded = CG_HudScriptHasMenuLoads( hudSet );" in load_hud_block
	assert "cg.competitiveHudLoaded = CG_HudScriptHasCompetitiveMenus( hudSet );" in load_hud_block

	for expected in (
		"void* esi = &data_10076a14",
		"int32_t i_1 = 0x127",
		"if ((eax_1 & 0x1000) == 0)",
		"(*(data_1074cccc + 0x14))",
		"esi += 0x18",
		'(*(data_1074cccc + 0x10))(i_1, "model", "sarge", 0x803)',
		'(*(data_1074cccc + 0x10))(i_1, "headmodel", "sarge", 0x803)',
		'"cg_version"',
		'return (*(data_1074cccc + 0x1c))("ui_voteactive", &data_1006841c)',
	):
		assert expected in retail_register_block
	for expected in (
		"void** esi = &data_10076a00",
		"int32_t i_1 = 0x127",
		"result = (*(data_1074cccc + 0x18))(*esi)",
		"esi = &esi[6]",
		"return sub_1003e640",
	):
		assert expected in retail_update_block
	for expected in (
		'{"cg_autoAction"}',
		'{"cg_autoHop"}',
		'{"cg_autoProjectileNudge"}',
		'{"cg_crosshairBrightness"}',
		'{"cg_crosshairColor"}',
		'{"cg_crosshairHealth"}',
		'{"cg_crosshairHitColor"}',
		'{"cg_crosshairHitStyle"}',
		'{"cg_crosshairHitTime"}',
		'{"cg_crosshairPulse"}',
		'{"cg_crosshairSize"}',
		'{"cg_crosshairX"}',
		'{"cg_crosshairY"}',
	):
		assert expected in retail_cvar_table
	assert '{"cg_forceDrawCrosshair"}' in retail_force_cvar_table


def test_cgame_weapon_settings_match_retail_cvar_table_and_style_wiring() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	effects_source = CG_EFFECTS.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	weapons_source = CG_WEAPONS.read_text(encoding="utf-8")
	cvar_table = source[source.index("static cvarTable_t cvarTable[]"):source.index("static int  cvarTableSize")]
	bubble_block = _block_from_marker(effects_source, "void CG_BubbleTrail")
	weapon_position_block = _block_from_marker(weapons_source, "static void CG_CalculateWeaponPosition")
	powerups_block = _block_from_marker(weapons_source, "static void CG_AddWeaponWithPowerups")
	add_player_weapon_block = _block_from_marker(weapons_source, "void CG_AddPlayerWeapon")
	view_weapon_block = _block_from_marker(weapons_source, "void CG_AddViewWeapon")
	plasma_block = _block_from_marker(weapons_source, "static void CG_PlasmaTrail")
	missile_hit_block = _block_from_marker(weapons_source, "void CG_MissileHitWall( int weapon")
	retail_flags = "CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD"
	cloud_flags = "CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD"

	for expected in (
		'{ &cg_autoswitch, "cg_autoswitch", "0", ' + retail_flags + ', "0", "1" },',
		'{ &cg_brassTime, "cg_brassTime", "2500", ' + retail_flags + ', "0", "10000" },',
		'{ &cg_bubbleTrail, "cg_bubbleTrail", "1", ' + retail_flags + ', "0", "1" },',
		'{ &cg_drawFullWeaponBar, "cg_drawFullWeaponBar", "0", ' + retail_flags + ', "0", "1" },',
		'{ &cg_drawGun, "cg_drawGun", "1", ' + retail_flags + ', "0", "3" },',
		'{ &cg_forceEnemyWeaponColor, "cg_forceEnemyWeaponColor", "0", ' + retail_flags + ', "0", "1" },',
		'{ &cg_forceTeamWeaponColor, "cg_forceTeamWeaponColor", "0", ' + retail_flags + ', "0", "1" },',
		'{ &cg_gun_x, "cg_gunX", "0", ' + retail_flags + ', "-10", "10" },',
		'{ &cg_gun_y, "cg_gunY", "0", ' + retail_flags + ', "-10", "20" },',
		'{ &cg_gun_z, "cg_gunZ", "0", ' + retail_flags + ', "-8", "0" },',
		'{ &cg_lightningImpact, "cg_lightningImpact", "1", ' + retail_flags + ', "0", "1" },',
		'{ &cg_lightningImpactCap, "cg_lightningImpactCap", "192", ' + retail_flags + ', "0", "768" },',
		'{ &cg_lightningStyle, "cg_lightningStyle", "1", ' + retail_flags + ', "1", "5" },',
		'{ &cg_lowAmmoWarningPercentile, "cg_lowAmmoWarningPercentile", "0.20", ' + retail_flags + ', "0.01", "1.00" },',
		'{ &cg_lowAmmoWarningSound, "cg_lowAmmoWarningSound", "1", ' + retail_flags + ', "0", "2" },',
		'{ &cg_lowAmmoWeaponBarWarning, "cg_lowAmmoWeaponBarWarning", "2", ' + retail_flags + ', "0", "2" },',
		'{ &cg_muzzleFlash, "cg_muzzleFlash", "1", ' + retail_flags + ', "0", "1" },',
		'{ &cg_plasmaStyle, "cg_plasmaStyle", "1", ' + retail_flags + ', "1", "2" },',
		'{ &cg_railStyle, "cg_railStyle", "1", ' + retail_flags + ', "1", "2" },',
		'{ &cg_railTrailTime, "cg_railTrailTime", "2000", ' + retail_flags + ', "0", "2000" },',
		'{ &cg_rocketStyle, "cg_rocketStyle", "1", ' + retail_flags + ', "1", "2" },',
		'{ &cg_switchOnEmpty, "cg_switchOnEmpty", "1", ' + retail_flags + ', "0", "1" },',
		'{ &cg_switchToEmpty, "cg_switchToEmpty", "1", ' + retail_flags + ', "0", "1" },',
		'{ &cg_trueLightning, "cg_trueLightning", "1", ' + retail_flags + ', "0", "1" },',
		'{ &cg_trueShotgun, "cg_trueShotgun", "0", ' + retail_flags + ', "0", "1" },',
		'{ &cg_weaponBar, "cg_weaponBar", "1", ' + retail_flags + ', "0", "4" },',
		'{ &cg_weaponColor_grenade, "cg_weaponColor_grenade", DEFAULT_WEAPON_BAR_GRENADE_COLOR, ' + cloud_flags + ' },',
		'{ &cg_weaponConfig, "cg_weaponConfig", "", ' + cloud_flags + ' },',
		'{ &cg_weaponConfig_g, "cg_weaponConfig_g", "", ' + cloud_flags + ' },',
		'{ &cg_weaponConfig_mg, "cg_weaponConfig_mg", "", ' + cloud_flags + ' },',
		'{ &cg_weaponConfig_sg, "cg_weaponConfig_sg", "", ' + cloud_flags + ' },',
		'{ &cg_weaponConfig_gl, "cg_weaponConfig_gl", "", ' + cloud_flags + ' },',
		'{ &cg_weaponConfig_rl, "cg_weaponConfig_rl", "", ' + cloud_flags + ' },',
		'{ &cg_weaponConfig_lg, "cg_weaponConfig_lg", "", ' + cloud_flags + ' },',
		'{ &cg_weaponConfig_rg, "cg_weaponConfig_rg", "", ' + cloud_flags + ' },',
		'{ &cg_weaponConfig_pg, "cg_weaponConfig_pg", "", ' + cloud_flags + ' },',
		'{ &cg_weaponConfig_bfg, "cg_weaponConfig_bfg", "", ' + cloud_flags + ' },',
		'{ &cg_weaponConfig_gh, "cg_weaponConfig_gh", "", ' + cloud_flags + ' },',
		'{ &cg_weaponConfig_ng, "cg_weaponConfig_ng", "", ' + cloud_flags + ' },',
		'{ &cg_weaponConfig_pl, "cg_weaponConfig_pl", "", ' + cloud_flags + ' },',
		'{ &cg_weaponConfig_cg, "cg_weaponConfig_cg", "", ' + cloud_flags + ' },',
		'{ &cg_weaponConfig_hmg, "cg_weaponConfig_hmg", "", ' + cloud_flags + ' },',
	):
		assert expected in cvar_table

	for retired in ('"cg_oldPlasma"', '"cg_oldRocket"', '"cg_noProjectileTrail"', '"cg_gun_frame"'):
		assert retired not in cvar_table

	assert "if ( !cg_bubbleTrail.integer ) {" in bubble_block
	assert "cg_noProjectileTrail" not in bubble_block
	assert "qhandle_t\tghostWeaponShader;" in local_source
	assert 'cgs.media.ghostWeaponShader = trap_R_RegisterShader("ghostWeaponShader" );' in source
	assert "if ( cg_drawGun.integer != 1 ) {" in weapon_position_block
	assert "localViewWeapon = ( cent->currentState.number == cg.predictedPlayerState.clientNum );" in powerups_block
	assert "if ( ( powerups & ( 1 << PW_INVIS ) ) && !localViewWeapon ) {" in powerups_block
	assert "if ( localViewWeapon && cg_drawGun.integer == 3 ) {" in powerups_block
	assert "gun->customShader = cgs.media.ghostWeaponShader;" in powerups_block
	assert "if ( ps && ( !cg_muzzleFlash.integer || !cg_drawGun.integer ) ) {" in add_player_weapon_block
	assert "drawFlash = qfalse;" in add_player_weapon_block
	assert "special hack for lightning gun" not in view_weapon_block
	assert "if ( cg_plasmaStyle.integer != 2 ) {" in plasma_block
	assert "cg_noProjectileTrail" not in plasma_block
	assert "cg_oldPlasma" not in plasma_block
	assert "if ( cg_rocketStyle.integer == 2 ) {" in missile_hit_block
	assert "cg_oldRocket" not in missile_hit_block


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
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	com_error_block = _block_from_marker(source, "void QDECL Com_Error")
	com_printf_block = _block_from_marker(source, "void QDECL Com_Printf")
	retail_printf_block = _text_between(hlil_source, "10020a90    int32_t sub_10020a90", "10020af0")
	retail_error_block = _text_between(hlil_source, "10020af0    int32_t sub_10020af0", "10020b50")

	assert "(void)level;" in com_error_block
	assert "vsprintf( text, error, argptr );" in com_error_block
	assert "trap_Error( text );" in com_error_block
	assert "CG_Error( \"%s\", text);" not in com_error_block

	assert "vsprintf( text, msg, argptr );" in com_printf_block
	assert "trap_Print( text );" in com_printf_block
	assert "CG_Printf (\"%s\", text);" not in com_printf_block

	for expected in (
		"vsprintf(&var_404, arg1, &arg_8)",
		"(*data_1074cccc)(&var_404)",
	):
		assert expected in retail_printf_block

	for expected in (
		"vsprintf(&var_404, arg1, &arg_c)",
		"(*(data_1074cccc + 4))(&var_404)",
	):
		assert expected in retail_error_block


def test_command_and_configstring_music_bridges_match_retail_wrappers() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	symbol_map = (REPO_ROOT / "references" / "symbol-maps" / "cgame.json").read_text(encoding="utf-8")
	alias_map = (REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json").read_text(encoding="utf-8")
	argv_block = _block_from_marker(source, "const char *CG_Argv( int arg )")
	config_block = _block_from_marker(source, "const char *CG_ConfigString( int index )")
	music_block = _block_from_marker(source, "void CG_StartMusic( void )")
	retail_argv_block = _text_between(
		hlil_source,
		'10020db0    int32_t __convention("regparm") sub_10020db0',
		"10020dd0",
	)
	retail_config_block = _text_between(hlil_source, "100252f0    int32_t sub_100252f0", "10025320")
	retail_music_block = _text_between(hlil_source, "10025320    int32_t sub_10025320", "100253f0")

	assert "trap_Argv( arg, buffer, sizeof( buffer ) );" in argv_block
	assert "return buffer;" in argv_block
	assert "CG_Error( \"CG_ConfigString: bad index: %i\", index );" in config_block
	assert "return cgs.gameState.stringData + cgs.gameState.stringOffsets[ index ];" in config_block
	assert "s = (char *)CG_ConfigString( CS_MUSIC );" in music_block
	assert "Q_strncpyz( parm1, COM_Parse( &s ), sizeof( parm1 ) );" in music_block
	assert "Q_strncpyz( parm2, COM_Parse( &s ), sizeof( parm2 ) );" in music_block
	assert "trap_S_StartBackgroundTrack( parm1, parm2 );" in music_block

	for expected in (
		"sub_10020db0",
		"data_100bb910",
		"0x400",
		"(*(data_1074cccc + 0x30))(arg1, &data_100bb910, 0x400)",
	):
		assert expected in retail_argv_block

	for expected in (
		"arg1 s< 0 || arg1 s>= 0x400",
		'"CG_ConfigString: bad index: %i"',
		"return (&data_10a38420)[arg1] + 0x10a39420",
	):
		assert expected in retail_config_block

	for expected in (
		"var_88 = data_10a38428 + 0x10a39420",
		"sub_10057120(&var_88, 1)",
		"strncpy(&var_44, 0x100d6a78, 0x3f)",
		"strncpy(&var_84, 0x100d6a78, 0x3f)",
		"(*(data_1074cccc + 0xbc))(&var_44, &var_84)",
	):
		assert expected in retail_music_block

	for expected in (
		'"FUN_10020db0": "CG_Argv"',
		'"FUN_100252f0": "CG_ConfigString"',
		'"FUN_10025320": "CG_StartMusic"',
	):
		assert expected in alias_map

	for expected in (
		'"address": "0x10020DB0"',
		'"normalized_name": "CG_Argv"',
		'"address": "0x100252F0"',
		'"normalized_name": "CG_ConfigString"',
		'"address": "0x10025320"',
		'"normalized_name": "CG_StartMusic"',
	):
		assert expected in symbol_map


def test_hud_asset_parser_matches_retail_assetglobaldef_leaf() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	symbol_map = (REPO_ROOT / "references" / "symbol-maps" / "cgame.json").read_text(encoding="utf-8")
	alias_map = (REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json").read_text(encoding="utf-8")
	asset_block = _block_from_marker(source, "qboolean CG_Asset_Parse( int handle )")
	parse_menu_block = _text_between(
		source,
		"void CG_ParseMenu( const char *menuFile )",
		"qboolean CG_Load_Menu( char **p )",
	)
	retail_asset_block = _text_between(hlil_source, "10025590    int32_t sub_10025590", "10025ac0")

	for expected in (
		"if (!trap_PC_ReadToken(handle, &token))",
		"if (Q_stricmp(token.string, \"{\") != 0) {",
		"if (Q_stricmp(token.string, \"}\") == 0) {",
		"if (Q_stricmp(token.string, \"font\") == 0) {",
		"cgDC.registerFont(tempStr, pointSize, &cgDC.Assets.textFont);",
		"if (Q_stricmp(token.string, \"smallFont\") == 0) {",
		"cgDC.registerFont(tempStr, pointSize, &cgDC.Assets.smallFont);",
		"if (Q_stricmp(token.string, \"bigfont\") == 0) {",
		"cgDC.registerFont(tempStr, pointSize, &cgDC.Assets.bigFont);",
		"if (Q_stricmp(token.string, \"gradientbar\") == 0) {",
		"cgDC.Assets.gradientBar = trap_R_RegisterShaderNoMip(tempStr);",
		"if (Q_stricmp(token.string, \"menuEnterSound\") == 0) {",
		"cgDC.Assets.menuEnterSound = trap_S_RegisterSound( tempStr, qfalse );",
		"if (Q_stricmp(token.string, \"menuExitSound\") == 0) {",
		"cgDC.Assets.menuExitSound = trap_S_RegisterSound( tempStr, qfalse );",
		"if (Q_stricmp(token.string, \"itemFocusSound\") == 0) {",
		"cgDC.Assets.itemFocusSound = trap_S_RegisterSound( tempStr, qfalse );",
		"if (Q_stricmp(token.string, \"menuBuzzSound\") == 0) {",
		"cgDC.Assets.menuBuzzSound = trap_S_RegisterSound( tempStr, qfalse );",
		"if (Q_stricmp(token.string, \"cursor\") == 0) {",
		"cgDC.Assets.cursor = trap_R_RegisterShaderNoMip( cgDC.Assets.cursorStr);",
		"if (Q_stricmp(token.string, \"fadeClamp\") == 0) {",
		"if (Q_stricmp(token.string, \"fadeCycle\") == 0) {",
		"if (Q_stricmp(token.string, \"fadeAmount\") == 0) {",
		"if (Q_stricmp(token.string, \"shadowX\") == 0) {",
		"if (Q_stricmp(token.string, \"shadowY\") == 0) {",
		"if (Q_stricmp(token.string, \"shadowColor\") == 0) {",
		"cgDC.Assets.shadowFadeClamp = cgDC.Assets.shadowColor[3];",
	):
		assert expected in asset_block

	for expected in (
		'if ( Q_stricmp( token.string, "assetGlobalDef" ) == 0 ) {',
		"if ( CG_Asset_Parse( handle ) ) {",
	):
		assert expected in parse_menu_block

	for expected in (
		"(*(data_1074cccc + 0x1b8))(edi, &var_830)",
		"sub_10057330(U\"{}\", 0x1869f, &var_820)",
		"sub_10057330(\"font\", 0x1869f, &var_820)",
		"sub_10057330(\"smallFont\", 0x1869f, &var_820)",
		"sub_10057330(\"bigfont\", 0x1869f, &var_820)",
		"sub_10057330(\"gradientbar\", 0x1869f, &var_820)",
		"sub_10057330(\"menuEnterSound\", 0x1869f, &var_820)",
		"sub_10057330(\"menuExitSound\", 0x1869f, &var_820)",
		"sub_10057330(\"itemFocusSound\", 0x1869f, &var_820)",
		"sub_10057330(\"menuBuzzSound\", 0x1869f, &var_820)",
		"sub_10057330(\"cursor\", 0x1869f, &var_820)",
		"sub_10057330(\"fadeClamp\", 0x1869f,",
		"sub_10057330(\"fadeCycle\", 0x1869f,",
		"sub_10057330(\"fadeAmount\", 0x1869f,",
		"sub_10057330(\"shadowX\", 0x1869f,",
		"sub_10057330(\"shadowY\", 0x1869f,",
		"sub_10057330(\"shadowColor\",",
		"data_10a3485c = data_10a34858",
		"return 1",
		"return 0",
	):
		assert expected in retail_asset_block

	for expected in (
		'"FUN_10025590": "CG_Asset_Parse"',
		'"address": "0x10025590"',
		'"normalized_name": "CG_Asset_Parse"',
	):
		assert expected in alias_map or expected in symbol_map


def test_hud_menu_file_loader_matches_retail_fallback_and_timing_path() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	symbol_map = (REPO_ROOT / "references" / "symbol-maps" / "cgame.json").read_text(encoding="utf-8")
	alias_map = (REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json").read_text(encoding="utf-8")
	load_menus_block = _block_from_marker(source, "void CG_LoadMenus( const char *menuFile )")
	retail_load_menus_block = _text_between(hlil_source, "10025ca0    int32_t __convention", "10025e60")

	for expected in (
		"start = trap_Milliseconds();",
		"len = trap_FS_FOpenFile( menuFile, &f, FS_READ );",
		'CG_Printf( S_COLOR_YELLOW "menu file not found: %s, using default\\n", menuFile );',
		"len = trap_FS_FOpenFile( CG_LEGACY_HUD_FILE, &f, FS_READ );",
		'trap_Error( va( S_COLOR_RED "default menu file not found: %s, unable to continue!\\n", CG_LEGACY_HUD_FILE ) );',
		"if ( len >= MAX_MENUDEFFILE ) {",
		'trap_Error( va( S_COLOR_RED "menu file too large: %s is %i, max allowed is %i", menuFile, len, MAX_MENUDEFFILE ) );',
		"trap_FS_Read( buf, len, f );",
		"buf[len] = 0;",
		"trap_FS_FCloseFile( f );",
		"COM_Compress( buf );",
		"CG_ResetBrowserOverlayState();",
		"CG_ParseMenu( cgRetailSupplementalMenuFiles[i] );",
		"token = COM_ParseExt( &p, qtrue );",
		'if ( Q_stricmp( token, "loadmenu" ) == 0 ) {',
		"if ( CG_Load_Menu( &p ) ) {",
		'Com_Printf( "UI menu load time = %d milli seconds\\n", trap_Milliseconds() - start );',
	):
		assert expected in load_menus_block

	assert 'trap_Error( va( S_COLOR_YELLOW "menu file not found: %s, using default\\n", menuFile ) );' not in load_menus_block
	assert "Menu_Reset();" not in load_menus_block

	for expected in (
		"(*(data_1074cccc + 8))()",
		"(*(data_1074cccc + 0x38))(arg1, &var_14, 0)",
		'"Warning: menu file not found: %s',
		'"ui/hud.txt"',
		'"^1default menu file not found: u',
		"esi s>= 0x1000",
		'"^1menu file too large: %s is %i,',
		"(*(data_1074cccc + 0x3c))(&data_100bbd10, esi, var_14)",
		"(*(edx_4 + 0x44))(ecx_5)",
		"sub_10057020()",
		"sub_10057120(&var_10, 1)",
		"sub_10057330(\"loadmenu\", 0x1869f, 0x100d6a78)",
		"sub_10025c40(&var_10)",
		'"UI menu load time = %d milli sec',
	):
		assert expected in retail_load_menus_block

	for expected in (
		'"FUN_10025ca0": "CG_LoadMenus"',
		'"address": "0x10025CA0"',
		'"normalized_name": "CG_LoadMenus"',
	):
		assert expected in alias_map or expected in symbol_map


def test_hud_bootstrap_and_asset_cache_match_retail_split_helpers() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	symbol_map = (REPO_ROOT / "references" / "symbol-maps" / "cgame.json").read_text(encoding="utf-8")
	alias_map = (REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json").read_text(encoding="utf-8")
	load_hud_block = _block_from_marker(source, "void CG_LoadHudMenu( void )")
	asset_block = _block_from_marker(source, "void CG_AssetCache( void )")
	init_block = _block_from_marker(source, "void CG_Init( int serverMessageNum, int serverCommandSequence, int clientNum )")
	retail_load_hud_block = _text_between(hlil_source, "10029120    int32_t sub_10029120", "10029210")
	retail_asset_block = _text_between(hlil_source, "10029420    int32_t sub_10029420", "100295c0")

	for expected in (
		'trap_Cvar_VariableStringBuffer( "cg_hudFiles", buff, sizeof( buff ) );',
		"hudSet = buff;",
		"if ( hudSet[0] == '\\0' ) {",
		"hudSet = CG_DEFAULT_HUD_FILE;",
		"cg.hudMenusLoaded = CG_HudScriptHasMenuLoads( hudSet );",
		"cg.competitiveHudLoaded = CG_HudScriptHasCompetitiveMenus( hudSet );",
		"CG_LoadMenus( hudSet );",
		"CG_CacheDraw2DMenuCache();",
		"CG_CacheScoreboardSelectionMenus();",
	):
		assert expected in load_hud_block

	assert "Init_Display(" not in load_hud_block
	assert "CG_InitDisplayContext();" in init_block
	assert init_block.index("CG_InitDisplayContext();") < init_block.index("CG_LoadHudMenu();")

	for expected in (
		"data_1074cd0c = 0",
		"(*(data_1074cccc + 0x24))(\"cg_hudFiles\", &var_404, 0x400)",
		'if (var_404 == 0)',
		'eax_4 = "ui/hud.txt"',
		"sub_10025ca0(eax_4)",
		"sub_10028f30()",
	):
		assert expected in retail_load_hud_block

	for expected in (
		"cgDC.Assets.gradientBar = trap_R_RegisterShaderNoMip( ASSET_GRADIENTBAR );",
		"cgDC.Assets.fxBasePic = trap_R_RegisterShaderNoMip( ART_FX_BASE );",
		"cgDC.Assets.fxPic[0] = trap_R_RegisterShaderNoMip( ART_FX_RED );",
		"cgDC.Assets.fxPic[1] = trap_R_RegisterShaderNoMip( ART_FX_YELLOW );",
		"cgDC.Assets.fxPic[2] = trap_R_RegisterShaderNoMip( ART_FX_GREEN );",
		"cgDC.Assets.fxPic[3] = trap_R_RegisterShaderNoMip( ART_FX_TEAL );",
		"cgDC.Assets.fxPic[4] = trap_R_RegisterShaderNoMip( ART_FX_BLUE );",
		"cgDC.Assets.fxPic[5] = trap_R_RegisterShaderNoMip( ART_FX_CYAN );",
		"cgDC.Assets.fxPic[6] = trap_R_RegisterShaderNoMip( ART_FX_WHITE );",
		"cgDC.Assets.scrollBar = trap_R_RegisterShaderNoMip( ASSET_SCROLLBAR );",
		"cgDC.Assets.scrollBarArrowDown = trap_R_RegisterShaderNoMip( ASSET_SCROLLBAR_ARROWDOWN );",
		"cgDC.Assets.scrollBarArrowUp = trap_R_RegisterShaderNoMip( ASSET_SCROLLBAR_ARROWUP );",
		"cgDC.Assets.scrollBarArrowLeft = trap_R_RegisterShaderNoMip( ASSET_SCROLLBAR_ARROWLEFT );",
		"cgDC.Assets.scrollBarArrowRight = trap_R_RegisterShaderNoMip( ASSET_SCROLLBAR_ARROWRIGHT );",
		"cgDC.Assets.scrollBarThumb = trap_R_RegisterShaderNoMip( ASSET_SCROLL_THUMB );",
		"cgDC.Assets.sliderBar = trap_R_RegisterShaderNoMip( ASSET_SLIDER_BAR );",
		"cgDC.Assets.sliderThumb = trap_R_RegisterShaderNoMip( ASSET_SLIDER_THUMB );",
		"CG_RegisterScoreTextures();",
	):
		assert expected in asset_block

	for expected in (
		'"ui/assets/gradientbar2.tga"',
		'"menu/art/fx_base"',
		'"menu/art/fx_red"',
		'"menu/art/fx_yel"',
		'"menu/art/fx_grn"',
		'"menu/art/fx_teal"',
		'"menu/art/fx_blue"',
		'"menu/art/fx_cyan"',
		'"menu/art/fx_white"',
		'"ui/assets/scrollbar.tga"',
		'"ui/assets/scrollbar_arrow_dwn_a.',
		'"ui/assets/scrollbar_arrow_up_a.t',
		'"ui/assets/scrollbar_arrow_left.t',
		'"ui/assets/scrollbar_arrow_right.',
		'"ui/assets/scrollbar_thumb.tga"',
		'"ui/assets/slider2.tga"',
		'"ui/assets/sliderbutt_1.tga"',
		"(*(data_1074cccc + 0xd4))",
	):
		assert expected in retail_asset_block

	for expected in (
		'"FUN_10029120": "CG_LoadHudMenu"',
		'"FUN_10029420": "CG_AssetCache"',
		'"address": "0x10029120"',
		'"normalized_name": "CG_LoadHudMenu"',
		'"address": "0x10029420"',
		'"normalized_name": "CG_AssetCache"',
	):
		assert expected in alias_map or expected in symbol_map


def test_cgame_browser_runtime_wrappers_drive_hud_reload_and_score_feeders() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	console_source = (REPO_ROOT / "src" / "code" / "cgame" / "cg_consolecmds.c").read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	ui_shared = UI_SHARED.read_text(encoding="utf-8")

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
	menu_font_block = _block_from_marker(ui_shared, "qboolean MenuParse_font")
	menu_keywords_block = _text_between(
		ui_shared,
		"keywordHash_t menuParseKeywords[] = {",
		"keywordHash_t *menuParseKeywordHash[KEYWORDHASH_SIZE];",
	)

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
	assert '{"font", MenuParse_font, NULL}' in menu_keywords_block
	for expected in (
		"fontPath = menu->font;",
		"UI_NormalizeFontPath( &fontPath, &pointSize, QL_FONT_NAME_TEXT, QL_FONT_TEXT_POINT_SIZE );",
		"menu->font = String_Alloc( fontPath );",
		"if (!DC->Assets.fontRegistered) {",
		"DC->registerFont( fontPath, pointSize, &DC->Assets.textFont );",
		"DC->registerFont( QL_FONT_NAME_SMALL, QL_FONT_SMALL_POINT_SIZE, &DC->Assets.smallFont );",
		"DC->registerFont( QL_FONT_NAME_BIG, QL_FONT_BIG_POINT_SIZE, &DC->Assets.bigFont );",
		"DC->Assets.fontRegistered = qtrue;",
	):
		assert expected in menu_font_block

	assert "CG_ResetBrowserOverlayState();" in load_menus_block
	assert "Menu_Reset();" not in load_menus_block
	assert "teamIndex = CG_TeamRowFromScoreIndex( cg.selectedScore, cg.scores[cg.selectedScore].team );" in score_block
	assert "CG_SetBrowserFeederSelection( menu, feeder, teamIndex );" in score_block
	assert "CG_SetBrowserFeederSelection( menu, FEEDER_SCOREBOARD, cg.selectedScore );" in score_block
	assert "Menu_SetFeederSelection(menu, feeder, i, NULL);" not in score_block
	assert "Menu_SetFeederSelection(menu, FEEDER_SCOREBOARD, cg.selectedScore, NULL);" not in score_block

	assert "CG_InitBrowserRuntime();" in load_hud_cmd_block
	assert load_hud_cmd_block.index("CG_InitBrowserRuntime();") < load_hud_cmd_block.index("CG_LoadHudMenu();")
	assert "String_Init();" not in load_hud_cmd_block
	assert "Menu_Reset();" not in load_hud_cmd_block
	assert "menuScoreboard = NULL;" not in load_hud_cmd_block

	assert "CG_InitBrowserRuntime();" in cgame_init_block
	assert cgame_init_block.index("CG_InitDisplayContext();") < cgame_init_block.index("CG_RegisterHudFonts();")
	assert cgame_init_block.index("CG_RegisterHudFonts();") < cgame_init_block.index("CG_InitBrowserRuntime();")
	assert cgame_init_block.index("CG_InitBrowserRuntime();") < cgame_init_block.index("CG_AssetCache();")
	assert cgame_init_block.index("CG_AssetCache();") < cgame_init_block.index("CG_LoadHudMenu();")


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
	clamp_join_block = _block_from_marker(screen_source, "static void CG_ClampJoinGameMenuCursor")
	enable_join_block = _block_from_marker(screen_source, "static void CG_EnableJoinGameMenuCursor")
	disable_join_block = _block_from_marker(screen_source, "static void CG_DisableJoinGameMenuCursor")
	open_join_block = _block_from_marker(screen_source, "static menuDef_t *CG_OpenJoinGameMenu")
	close_join_block = _block_from_marker(screen_source, "void CG_CloseJoinGameMenu")
	reset_join_block = _block_from_marker(screen_source, "void CG_ResetJoinGameMenuCaptureState")
	should_draw_join_block = _block_from_marker(screen_source, "static qboolean CG_ShouldDrawJoinGameMenu")

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
		"wasVisible = (qboolean)( ( menu->window.flags & WINDOW_VISIBLE ) != 0 );",
		"if ( !wasVisible ) {",
		"CG_EnableJoinGameMenuCursor();",
		"if ( !cg_joinGameMenuCursorActive || !( catcher & KEYCATCH_CGAME ) ) {",
	):
		assert expected in open_join_block

	for expected in (
		"cgs.cursorX = 0;",
		"cgs.cursorX = SCREEN_WIDTH;",
		"cgs.cursorY = 0;",
		"cgs.cursorY = SCREEN_HEIGHT;",
	):
		assert expected in clamp_join_block

	for expected in (
		"catcher = trap_Key_GetCatcher();",
		"if ( !( catcher & KEYCATCH_CGAME ) ) {",
		"trap_Key_SetCatcher( catcher | KEYCATCH_CGAME );",
		"CG_ClampJoinGameMenuCursor();",
		"cgDC.cursorx = cgs.cursorX;",
		"cgDC.cursory = cgs.cursorY;",
		"cgs.activeCursor = cgs.media.cursor ? cgs.media.cursor : cgs.media.selectCursor;",
		"cg_joinGameMenuCursorActive = qtrue;",
	):
		assert expected in enable_join_block

	for expected in (
		"if ( !cg_joinGameMenuCursorActive ) {",
		"cg_joinGameMenuCursorActive = qfalse;",
		"cgs.capturedItem = NULL;",
		"cgs.activeCursor = 0;",
		"trap_Key_SetCatcher( catcher & ~KEYCATCH_CGAME );",
	):
		assert expected in disable_join_block

	assert "CG_DisableJoinGameMenuCursor();" in reset_join_block
	assert "cg_joinGameMenuCursorActive = qfalse;" in reset_join_block
	assert "cg.scoreBoardShowing" not in should_draw_join_block
	assert "cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR" in should_draw_join_block
	assert 'CG_CloseBrowserOverlayByName( "joingame_menu" );' in close_join_block
	assert "CG_DisableJoinGameMenuCursor();" in close_join_block
	assert 'Menus_OpenByName( "joingame_menu" );' not in open_join_block
	assert 'Menus_CloseByName( "joingame_menu" );' not in close_join_block
	assert "trap_Key_SetCatcher( catcher | KEYCATCH_CGAME );" not in open_join_block
	assert "CG_CenterJoinGameMenuCursor" not in screen_source


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
	fullscreen_background_block = _block_from_marker(newdraw_source, "static void CG_DrawBrowserFullscreenBackground")
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
	assert "static int CG_ResolveBrowserMenuWidescreenMode( const menuDef_t *menu ) {" in newdraw_source
	assert "static void CG_DrawBrowserFullscreenBackground( const menuDef_t *menu ) {" in newdraw_source
	assert "Menus_HandleOOBClick( (menuDef_t *)overlay, key, down );" in oob_block

	for expected in (
		"sourceWidth = menu->backgroundRect.w;",
		"if ( sourceWidth > 0.0f ) {",
		"screenWidth = (float)cgDC.glconfig.vidWidth;",
		"screenHeight = (float)cgDC.glconfig.vidHeight;",
		"s0 = ( ( sourceWidth - screenWidth * ( sourceHeight / screenHeight ) ) / sourceWidth ) * 0.5f;",
		"cgDC.drawStretchPic( 0.0f, 0.0f, screenWidth, screenHeight, s0, 0.0f, 1.0f - s0, 1.0f, menu->window.background );",
		"cgDC.drawHandlePic( 0.0f, 0.0f, SCREEN_WIDTH, SCREEN_HEIGHT, menu->window.background );",
	):
		assert expected in fullscreen_background_block

	for expected in (
		"if ( ( menu->window.ownerDrawFlags || menu->window.ownerDrawFlags2 ) && cgDC.ownerDrawVisible &&",
		"!cgDC.ownerDrawVisible( menu->window.ownerDrawFlags, menu->window.ownerDrawFlags2 ) ) {",
		"CG_UpdateBrowserPresetLists( menu );",
		"CG_DrawBrowserFullscreenBackground( menu );",
		"CG_DrawBrowserWidgetFrame( &menu->window, menu->fadeAmount, menu->fadeClamp, menu->fadeCycle );",
		"CG_DrawBrowserWidget( menu->items[i] );",
		"cgDC.setAdjustFrom640Mode( CG_ResolveBrowserMenuWidescreenMode( menu ) );",
		"cgDC.setAdjustFrom640Mode( WIDESCREEN_CENTER );",
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
	assert "if ( !CG_ShouldDrawAccOverlay() || !menuStats ) {" in stats_block
	assert "CG_DrawBrowserOverlayTree( menuStats, qtrue );" in stats_block
	assert "CG_DrawBrowserOverlays();" in draw_2d_block
	assert "CG_DrawBrowserCursor();" in draw_2d_block
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
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	parse_menu_start = source.index("void CG_ParseMenu( const char *menuFile )")
	load_menu_start = source.index("qboolean CG_Load_Menu( char **p )")
	parse_menu_block = source[parse_menu_start:load_menu_start]
	load_menu_block = _block_from_marker(source, "qboolean CG_Load_Menu( char **p )")
	retail_parse_menu_block = _text_between(hlil_source, "10025ac0    void sub_10025ac0", "10025c40")
	retail_load_menu_block = _text_between(hlil_source, "10025c40    int32_t sub_10025c40", "10025ca0")
	retail_score_selection_block = _text_between(hlil_source, "10025f60    void sub_10025f60", "100260e0")
	retail_info_block = _text_between(hlil_source, "100260e0    void* __convention", "10026160")
	score_block = _block_from_marker(source, "void CG_SetScoreSelection")
	info_block = _block_from_marker(source, "static clientInfo_t *CG_InfoFromScoreIndex")
	selection_block = _block_from_marker(source, "static void CG_FeederSelection")

	for expected in (
		'handle = trap_PC_LoadSource( "ui/testhud.menu" );',
		'if ( Q_stricmp( token.string, "assetGlobalDef" ) == 0 ) {',
		"if ( CG_Asset_Parse( handle ) ) {",
		'if ( Q_stricmp( token.string, "menudef" ) == 0 ) {',
		"menu = &Menus[menuCount];",
		"CG_InitBrowserOverlay( menu );",
		"if ( CG_ParseBrowserMenu( handle, menu ) ) {",
		"Menu_PostParse( menu );",
		"menuCount++;",
	):
		assert expected in parse_menu_block

	assert "Menu_New(handle);" not in parse_menu_block

	for expected in (
		"token = COM_ParseExt( p, qtrue );",
		"if ( token[0] != '{' ) {",
		'if ( Q_stricmp( token, "}" ) == 0 ) {',
		"CG_ParseMenu( token );",
	):
		assert expected in load_menu_block

	for expected in (
		'"ui/testhud.menu"',
		'"assetGlobalDef"',
		'"menudef"',
		"+ 0x1b0",
		"+ 0x1b4",
		"+ 0x1b8",
	):
		assert expected in retail_parse_menu_block

	for expected in (
		"sub_10025ac0(0x100d6a78)",
		'"}"',
	):
		assert expected in retail_load_menu_block

	for expected in (
		"void CG_SetScoreSelection( void *menu );",
	):
		assert expected in local_source

	for expected in (
		"if ( cg.selectedScore < 0 || cg.selectedScore >= cg.numScores ) {",
		"teamIndex = CG_TeamRowFromScoreIndex( cg.selectedScore, cg.scores[cg.selectedScore].team );",
		"CG_SetBrowserFeederSelection( menu, feeder, teamIndex );",
		"CG_SetBrowserFeederSelection( menu, FEEDER_SCOREBOARD, cg.selectedScore );",
	):
		assert expected in score_block

	for expected in (
		"CG_BuildHudScoreboard();",
		"entry = CG_GetHudScoreboardEntry( index, team );",
		"mappedIndex = CG_FindScoreIndexForClient( entry->clientNum );",
		"if ( cgs.gametype >= GT_TEAM && ( team == TEAM_RED || team == TEAM_BLUE ) ) {",
		"for ( i = 0; i < cg.numScores; i++ ) {",
		"if ( cg.scores[i].team == team ) {",
		"*scoreIndex = index;",
	):
		assert expected in info_block

	for expected in (
		"data_10a9cdc4 = ebx",
		"data_10a3ff14 s>= 3",
		"sub_10060650(var_8, arg1, ecx_3)",
	):
		assert expected in retail_score_selection_block

	for expected in (
		"data_10a3ff14 s>= 3",
		"*arg2 = eax",
		"*arg2 = arg1",
		"data_10a9cdc0",
	):
		assert expected in retail_info_block

	for expected in (
		"if ( index == -1 ) {",
		"if ( cgs.gametype < GT_TEAM || ( !CG_IsTeamListFeeder( feederID ) && !CG_IsTeamStatsFeeder( feederID ) ) ) {",
		"selectedScoreIndex = CG_ScoreIndexFromTeamRow( index, team );",
		"cg.selectedScore = selectedScoreIndex;",
		"selectedIndex = CG_TeamRowFromScoreIndex( cg.selectedScore, team );",
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
	powerup_block = _block_from_marker(source, "static qhandle_t CG_FeederPowerupHandle")
	ready_block = _block_from_marker(source, "static qboolean CG_FeederShouldShowReadyIcon")
	damage_block = _block_from_marker(source, "static const char *CG_FeederFormattedDamage")
	race_time_block = _block_from_marker(source, "static const char *CG_FeederFormatRaceTime")
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
		"if ( CG_IsTeamListFeeder( feederID ) ) {",
		"return CG_FeederItemTextTDMFreezeStats( team, index, column, handle );",
		"return CG_FeederItemTextClanArenaStats( team, index, column, handle );",
		"return CG_FeederItemTextCTFFamilyStats( team, index, column, handle );",
		"return CG_FeederItemTextRaceScoreboard( index, column, handle );",
		"return CG_FeederItemTextScoreboard( index, column, handle );",
	):
		assert expected in text_block

	assert "if ( CG_IsScoreboardFeeder( feederID ) ) {" not in text_block

	for expected in (
		"for ( powerup = PW_QUAD; powerup < PW_NUM_POWERUPS; powerup++ ) {",
		"if ( powerup == PW_NEUTRALFLAG ) {",
		"return trap_R_RegisterShaderNoMip( item->icon );",
	):
		assert expected in powerup_block

	for expected in (
		"cg.snap->ps.pm_type == PM_INTERMISSION",
		"cgs.matchReadyUpDeadline > 0",
		"cgs.matchWarmupReadyEligible > 0",
		"cgs.intermissionExitStatusLatched",
	):
		assert expected in ready_block

	for expected in (
		'return va( "%2.0fK", (float)damage / 1000.0f );',
		'return va( "%1.1fK", (float)damage / 1000.0f );',
	):
		assert expected in damage_block

	for expected in (
		'return "-";',
		'return va( "%i:%02i.%03i", minutes, seconds, millis );',
	):
		assert expected in race_time_block

	for expected in (
		"row.info->team == TEAM_SPECTATOR",
		"case 0:",
		"*handle = CG_FeederCountryFlagHandle( row.info );",
		"case 1:",
		"row.socialHandle",
		"case 3:",
		"icon = CG_FeederPowerupHandle( row.info->powerups );",
		"if ( icon ) {",
		"case 5:",
		"return row.info->name;",
		"case 7:",
		"return CG_FeederScoreValue( score );",
		"case 8:",
		'return va( "%i/%i", row.scoreRow->kills, row.scoreRow->deaths );',
		"case 9:",
		"return CG_FeederFormattedDamage( row.scoreRow->damage );",
		"case 10:",
		"icon = CG_FeederBestWeaponHandle( row.scoreRow );",
		"case 11:",
		'return va( "%i%%", row.scoreRow->accuracy );',
		"case 12:",
		'return va( "%4i", time );',
		"case 13:",
		'return va( "%4i", ping );',
	):
		assert expected in scoreboard_block

	for expected in (
		"case 0:",
		"*handle = CG_FeederCountryFlagHandle( row.info );",
		"case 2:",
		"icon = CG_FeederReadyHandle( &row );",
		"if ( icon ) {",
		"case 3:",
		"return row.info->name;",
		"case 4:",
		"return CG_FeederFormatRaceTime( score );",
		"case 5:",
		'return va( "%4i", time );',
		"case 6:",
		'return va( "%4i", ping );',
	):
		assert expected in race_block

	assert "return CG_FeederItemTextScoreboard( index, column, handle );" not in race_block

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
		'return va( "%i", stats->weaponFrags[WP_GAUNTLET] );',
		'"^3%i ^7%i%%"',
		"stats->weaponFrags[WP_HEAVY_MACHINEGUN]",
	):
		assert expected in ca_block

	assert "stats->weaponAccuracy[WP_GAUNTLET]" not in ca_block

	for expected in (
		"stats = &cg.ctfStats[row.scoreIndex];",
		"net = row.scoreRow->kills - row.scoreRow->deaths - stats->values[11];",
		'return va( "%i", stats->values[10] );',
		'return va( "%i", stats->values[8] );',
		'return va( "%i", stats->values[0] );',
	):
		assert expected in ctf_block


def test_cgame_scoreboard_feeder_matrix_owns_all_retail_scoreboard_feeders() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	scoreboard_predicate = _block_from_marker(source, "static qboolean CG_IsScoreboardFeeder")
	team_list_predicate = _block_from_marker(source, "static qboolean CG_IsTeamListFeeder")
	team_stats_predicate = _block_from_marker(source, "static qboolean CG_IsTeamStatsFeeder")
	team_resolver = _block_from_marker(source, "static int CG_GetFeederTeam")
	count_block = _block_from_marker(source, "static int CG_FeederCount")
	text_block = _block_from_marker(source, "static const char *CG_FeederItemText")
	selection_block = _block_from_marker(source, "static void CG_FeederSelection")
	init_block = _block_from_marker(source, "static void CG_InitDisplayContext")
	retail_count_block = _text_between(hlil_source, "10025e70    int32_t sub_10025e70", "10025f60")
	retail_text_block = _text_between(hlil_source, "10028830    void* sub_10028830", "10028b10")
	retail_bootstrap_block = _text_between(hlil_source, "10029210    void* sub_10029210", "10029420")

	for expected in (
		"FEEDER_SCOREBOARD",
		"FEEDER_ENDSCOREBOARD",
	):
		assert expected in scoreboard_predicate
	assert "return ( feederID == FEEDER_SCOREBOARD || feederID == FEEDER_ENDSCOREBOARD ) ? qtrue : qfalse;" in scoreboard_predicate

	for expected in (
		"FEEDER_REDTEAM_LIST",
		"FEEDER_BLUETEAM_LIST",
	):
		assert expected in team_list_predicate
		assert expected in count_block

	for expected in (
		"FEEDER_REDTEAM_STATS",
		"FEEDER_BLUETEAM_STATS",
	):
		assert expected in team_stats_predicate
		assert expected in count_block

	for expected in (
		"FEEDER_REDTEAM_LIST || feederID == FEEDER_REDTEAM_STATS",
		"FEEDER_BLUETEAM_LIST || feederID == FEEDER_BLUETEAM_STATS",
		"return TEAM_RED;",
		"return TEAM_BLUE;",
	):
		assert expected in team_resolver

	for expected in (
		"if ( CG_IsTeamStatsFeeder( feederID ) ) {",
		"if ( CG_IsTeamListFeeder( feederID ) ) {",
		"if ( cgs.gametype == GT_RACE ) {",
		"return CG_FeederItemTextScoreboard( index, column, handle );",
	):
		assert expected in text_block
	assert "FEEDER_SCOREBOARD" not in text_block
	assert "FEEDER_ENDSCOREBOARD" not in text_block

	for expected in (
		"CG_BuildHudScoreboard();",
		"} else if ( CG_IsScoreboardFeeder( feederID ) ) {",
		"return hud ? hud->count : 0;",
		"return cg.numScores;",
	):
		assert expected in count_block

	for expected in (
		"(void)cvar;",
		"CG_IsTeamListFeeder( feederID )",
		"CG_IsTeamStatsFeeder( feederID )",
		"cg.selectedScore = index;",
		"CG_ScoreIndexFromTeamRow( index, team );",
		"CG_SyncScoreboardTeamListSelection( team, selectedIndex );",
	):
		assert expected in selection_block

	for expected in (
		"cgDC.feederCount = &CG_FeederCount;",
		"cgDC.feederItemImage = &CG_FeederItemImage;",
		"cgDC.feederItemText = &CG_FeederItemText;",
		"cgDC.feederSelection = &CG_FeederSelection;",
	):
		assert expected in init_block

	for expected in (
		"arg1 - 5f",
		"float temp1_1 = data_10078fc0",
		"arg1 - 17f",
		"arg1 - 18f",
		"arg1 - 11f",
		"return data_10a9cdc0",
	):
		assert expected in retail_count_block

	for expected in (
		"arg1 - 5f",
		"float temp1 = data_10078fc0",
		"arg1 - 17f",
		"arg1 - 18f",
		"return sub_10026160(arg2, arg3, arg4)",
		"return sub_10027c40(arg4, arg2, arg3)",
	):
		assert expected in retail_text_block
	assert "arg1 - 16f" not in retail_text_block

	for expected in (
		"data_10a2569c = sub_10025e70",
		"data_10a256a0 = sub_10028830",
		"data_10a256a8 = sub_10028b10",
	):
		assert expected in retail_bootstrap_block


def test_cgame_team_list_feeders_restore_retail_family_split() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	text_block = _block_from_marker(source, "static const char *CG_FeederItemText")
	lead_block = _block_from_marker(source, "static const char *CG_FeederItemTextTeamListLeadColumns")
	fallback_block = _block_from_marker(source, "static const char *CG_FeederItemTextFallbackTeamList")
	tdm_block = _block_from_marker(source, "static const char *CG_FeederItemTextTDMFreezeTeamList")
	ca_block = _block_from_marker(source, "static const char *CG_FeederItemTextClanArenaTeamList")
	ctf_block = _block_from_marker(source, "static const char *CG_FeederItemTextCTFFamilyTeamList")

	for expected in (
		"if ( CG_IsTeamListFeeder( feederID ) ) {",
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
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	menu_name_block = _block_from_marker(source, "static const char *CG_GetScoreboardSelectionMenuName")
	cache_block = _block_from_marker(source, "static void CG_CacheScoreboardSelectionMenus")
	sync_block = _block_from_marker(source, "static void CG_SyncScoreboardTeamListSelection")
	image_block = _block_from_marker(source, "static qhandle_t CG_FeederItemImage( float feederID, int index )")
	selection_block = _block_from_marker(source, "static void CG_FeederSelection( float feederID, int index, const char *cvar )")
	retail_selection_block = _text_between(hlil_source, "10028b10    void sub_10028b10", "10028c30")
	retail_bootstrap_block = _text_between(hlil_source, "10029210    void* sub_10029210", "10029420")
	load_hud_block = _block_from_marker(source, "void CG_LoadHudMenu( void )")

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
		"selectedScoreIndex = CG_ScoreIndexFromTeamRow( index, team );",
		"selectedIndex = CG_TeamRowFromScoreIndex( cg.selectedScore, team );",
		"CG_CacheScoreboardSelectionMenus();",
		"CG_SyncScoreboardTeamListSelection( team, selectedIndex );",
	):
		assert expected in selection_block

	for expected in (
		"data_10a256a4 = sub_10025e60",
		"data_10a256a0 = sub_10028830",
		"data_10a256a8 = sub_10028b10",
	):
		assert expected in retail_bootstrap_block

	for expected in (
		'"playerlistRED"',
		'"playerlistBLUE"',
		"data_10a9cdc4 = edi",
		"= 0xffffffff",
	):
		assert expected in retail_selection_block

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
	assert 'cgs.scorelimit = atoi( Info_ValueForKey( info, "g_scorelimit" ) );' in parse_block
	assert 'cgs.roundlimit = atoi( Info_ValueForKey( info, "roundlimit" ) );' in parse_block
	assert parse_block.index('cgs.scorelimit = atoi( Info_ValueForKey( info, "g_scorelimit" ) );') > parse_block.index('cgs.capturelimit = atoi( Info_ValueForKey( info, "capturelimit" ) );')
	assert parse_block.index('cgs.roundlimit = atoi( Info_ValueForKey( info, "roundlimit" ) );') > parse_block.index('cgs.timelimit = atoi( Info_ValueForKey( info, "timelimit" ) );')
	assert parse_block.index("CG_SetGameInfoCvars();") > parse_block.index('cgs.timelimit = atoi( Info_ValueForKey( info, "timelimit" ) );')
	assert parse_block.index("CG_SetGameInfoCvars();") > parse_block.index('cgs.roundlimit = atoi( Info_ValueForKey( info, "roundlimit" ) );')
	assert parse_block.index("CG_SetGameInfoCvars();") < parse_block.index('voteFlagsValue = Info_ValueForKey( info, "g_voteFlags" );')


def test_display_context_uses_named_cvar_string_and_native_chat_helpers() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	display_block = _block_from_marker(source, "static void CG_InitDisplayContext")
	cvar_string_block = _block_from_marker(source, "void CG_Cvar_GetString")
	compact_hud_block = _block_from_marker(source, "static qboolean CG_UseMatchSummaryChatLayout")
	physics_block = _block_from_marker(source, "static int CG_GetPhysicsTime")
	chat_y_block = _block_from_marker(source, "static float CG_GetChatFieldY")
	chat_width_block = _block_from_marker(source, "static float CG_GetChatFieldPixelWidth")
	chat_chars_block = _block_from_marker(source, "static int CG_GetChatFieldWidthInChars")
	physics_hlil = _text_between(hlil_source, "1004e4d0    int32_t sub_1004e4d0", "1004e4d6")
	chat_y_hlil = _text_between(hlil_source, "100209e0    long double sub_100209e0", "100209f7")
	chat_width_hlil = _text_between(hlil_source, "10020a00    long double sub_10020a00", "10020a17")
	chat_chars_hlil = _text_between(hlil_source, "10020a20    int32_t sub_10020a20", "10020a33")

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
	assert "return data_10a9c1f4" in physics_hlil
	for expected in (
		"data_10a9c214.d != 5",
		"return fconvert.t(413f)",
		"return fconvert.t(455f)",
	):
		assert expected in chat_y_hlil
	for expected in (
		"data_10a9c214.d != 5",
		"return fconvert.t(640f)",
		"return fconvert.t(300f)",
	):
		assert expected in chat_width_hlil
	for expected in (
		"data_10a9c214.d - 5",
		"& 0x2b) + 0x1e",
	):
		assert expected in chat_chars_hlil


def test_cgame_native_sidecar_helpers_match_retail_export_leafs() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	public_source = CG_PUBLIC.read_text(encoding="utf-8")
	tracked_block = _block_from_marker(source, "static void CG_ShowTrackedPlayerSlot")
	first_tracked_block = _block_from_marker(source, "static void CG_Show1stTrackedPlayer")
	second_tracked_block = _block_from_marker(source, "static void CG_Show2ndTrackedPlayer")
	identity_block = _block_from_marker(source, "static qboolean CG_CopyClientIdentity")
	speaking_block = _block_from_marker(source, "void *CG_SetClientSpeakingState")
	native_speaking_block = _block_from_marker(source, "static int CG_NativeSetClientSpeakingState")
	identity_hlil = _text_between(hlil_source, "10020910    int32_t sub_10020910", "100209de")
	first_tracked_hlil = _text_between(hlil_source, "10029ff0    int32_t sub_10029ff0", "1002a053")
	second_tracked_hlil = _text_between(hlil_source, "1002a060    int32_t sub_1002a060", "1002a0c3")
	speaking_hlil = _text_between(hlil_source, "10020a40    void* sub_10020a40", "10020a68")

	for expected in (
		"if ( slot < 0 || slot > 1 ) {",
		"cg.spectatorSlotTrackedTime[slot] = cg.time + CG_SPECTATOR_SLOT_TRACK_HOLD;",
		"CG_ReplayLastMessageFromCvar();",
	):
		assert expected in tracked_block
	assert "CG_ShowTrackedPlayerSlot( 0 );" in first_tracked_block
	assert "CG_ShowTrackedPlayerSlot( 1 );" in second_tracked_block

	for expected in (
		"data_10a5f2f8 = data_10a9c1ec + 0xbb8",
		'(*(edx + 0x24))("cg_lastmsg", &var_104, 0x100)',
		"sub_10006910(&var_104, 0, 0)",
	):
		assert expected in first_tracked_hlil
	for expected in (
		"data_10a5f2fc = data_10a9c1ec + 0xbb8",
		'(*(edx + 0x24))("cg_lastmsg", &var_104, 0x100)',
		"sub_10006910(&var_104, 0, 0)",
	):
		assert expected in second_tracked_hlil

	for expected in (
		"if ( !outIdentity ) {",
		"if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {",
		"if ( !ci->infoValid ) {",
		"memset( identity, 0, sizeof( *identity ) );",
		"identity->clientNum = clientNum;",
		"identity->identityTransport = 0;",
		"identity->identityLow = ci->identityLow;",
		"identity->identityHigh = ci->identityHigh;",
		"Q_strncpyz( identity->displayName, ci->name, sizeof( identity->displayName ) );",
		"Q_CleanStr( cleanName );",
		"return qtrue;",
	):
		assert expected in identity_block
	for expected in (
		"#define CG_CLIENT_IDENTITY_NAME_CHARS\t40",
		"char\t\t\tdisplayName[CG_CLIENT_IDENTITY_NAME_CHARS];",
		"char\t\t\tcleanName[CG_CLIENT_IDENTITY_NAME_CHARS];",
	):
		assert expected in public_source
	for expected in (
		"if (arg1 u> 0x3f)",
		"if (*(arg1 * 0x738 + &data_10a41cf0) == 0)",
		"*arg2 = arg1",
		"arg2[1] = *(arg1 * 0x738 + 0x10a42400)",
		"arg2[2] = *(arg1 * 0x738 + &data_10a42418)",
		"arg2[3] = *(arg1 * 0x738 + 0x10a4241c)",
		"strncpy(&arg2[4], arg1 * 0x738 + 0x10a41cf8, 0x27)",
		"*(arg2 + 0x37) = 0",
		"strncpy(&arg2[0xe], arg1 * 0x738 + 0x10a41d38, 0x27)",
		"*(arg2 + 0x5f) = 0",
		"return 1",
	):
		assert expected in identity_hlil

	for expected in (
		"if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {",
		"speakingState->speaking = speaking ? qtrue : qfalse;",
		"speakingState->time = cg.time;",
		"cgs.currentVoiceClient = clientNum;",
		"cg.voiceTime = cg.time;",
		"cgs.currentVoiceClient = -1;",
		"cg.voiceTime = 0;",
		"return ci;",
	):
		assert expected in speaking_block
	assert "return (int)(intptr_t)CG_SetClientSpeakingState( clientNum, speaking );" in native_speaking_block
	for expected in (
		"int32_t eax = arg1 * 0x738",
		"*(eax + 0x10a4240c) = arg2",
		"*(eax + 0x10a42410) = edx_1",
		"return eax + &data_10a41cf0",
	):
		assert expected in speaking_hlil


def test_cgame_getvalue_callback_surface_matches_retail_score_stat_leaf() -> None:
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	main_source = CG_MAIN.read_text(encoding="utf-8")
	ghidra_source = CGAME_GHIDRA_DECOMPILE.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	ui_shared_h = UI_SHARED_H.read_text(encoding="utf-8")
	value_block = _block_from_marker(newdraw_source, "float CG_GetValue")
	display_block = _block_from_marker(main_source, "static void CG_InitDisplayContext")
	retail_bootstrap_block = _block_from_marker(ghidra_source, "void FUN_10029210(void)")
	retail_value_block = _text_between(
		hlil_source,
		"10031610    long double sub_10031610",
		"100316ab",
	)
	constants = _menudef_ownerdraw_constants()

	assert {
		name: constants[name]
		for name in (
			"CG_PLAYER_ARMOR_VALUE",
			"CG_PLAYER_AMMO_VALUE",
			"CG_PLAYER_SCORE",
			"CG_PLAYER_HEALTH",
			"CG_RED_SCORE",
			"CG_BLUE_SCORE",
		)
	} == {
		"CG_PLAYER_ARMOR_VALUE": 40,
		"CG_PLAYER_AMMO_VALUE": 49,
		"CG_PLAYER_SCORE": 51,
		"CG_PLAYER_HEALTH": 44,
		"CG_RED_SCORE": 284,
		"CG_BLUE_SCORE": 312,
	}

	for expected in (
		"_DAT_10a25664 = FUN_1003b0f0;",
		"_DAT_10a25668 = &LAB_10031610;",
		"_DAT_10a2566c = FUN_10031790;",
		"_DAT_10a256c8 = &LAB_10028d80;",
	):
		assert expected in retail_bootstrap_block

	assert retail_bootstrap_block.index("_DAT_10a25664 = FUN_1003b0f0;") < retail_bootstrap_block.index("_DAT_10a25668 = &LAB_10031610;")
	assert retail_bootstrap_block.index("_DAT_10a25668 = &LAB_10031610;") < retail_bootstrap_block.index("_DAT_10a2566c = FUN_10031790;")
	assert display_block.index("cgDC.ownerDrawItem = &CG_OwnerDraw;") < display_block.index("cgDC.getValue = &CG_GetValue;")
	assert display_block.index("cgDC.getValue = &CG_GetValue;") < display_block.index("cgDC.ownerDrawVisible = &CG_OwnerDrawVisible;")
	assert "cgDC.ownerDrawWidth = &CG_OwnerDrawWidth;" in display_block

	assert set(_case_labels(value_block)) == {
		"CG_PLAYER_ARMOR_VALUE",
		"CG_PLAYER_AMMO_VALUE",
		"CG_PLAYER_SCORE",
		"CG_PLAYER_HEALTH",
		"CG_RED_SCORE",
		"CG_BLUE_SCORE",
	}

	for expected in (
		"return ps->stats[STAT_ARMOR];",
		"return ps->ammo[cent->currentState.weapon];",
		"return cg.snap->ps.persistant[PERS_SCORE];",
		"return ps->stats[STAT_HEALTH];",
		"return cgs.scores1;",
		"return cgs.scores2;",
		"return -1;",
	):
		assert expected in value_block

	for expected in (
		"case 0x31",
		"int32_t ecx = *(esi + 0xb4)",
		"int32_t eax_3 = *(ecx * 0x2d0 + 0x10abbb90)",
		"if (eax_3 != 0)",
		"return float.t(*(esi + (eax_3 << 2) + 0x1ac))",
	):
		assert expected in retail_value_block

	for stale in (
		"#define CG_SELECTEDPLAYER_ARMOR 350",
		"#define CG_SELECTEDPLAYER_HEALTH 351",
	):
		assert stale in ui_shared_h

	for stale in (
		"CG_SELECTEDPLAYER_ARMOR",
		"CG_SELECTEDPLAYER_HEALTH",
		"cg.selectedTeamPlayer",
		"CG_GetSelectedPlayer",
	):
		assert stale not in value_block


def test_cgame_init_splits_display_context_bootstrap_before_collision_map() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	ghidra_source = CGAME_GHIDRA_DECOMPILE.read_text(encoding="utf-8")
	display_block = _block_from_marker(source, "static void CG_InitDisplayContext")
	cvar_float_block = _block_from_marker(source, "static float CG_Cvar_Get")
	play_cinematic_block = _block_from_marker(source, "static int CG_PlayCinematic")
	stop_cinematic_block = _block_from_marker(source, "static void CG_StopCinematic")
	draw_cinematic_block = _block_from_marker(source, "static void CG_DrawCinematic")
	run_cinematic_block = _block_from_marker(source, "static void CG_RunCinematicFrame")
	retail_bootstrap_block = _block_from_marker(ghidra_source, "void FUN_10029210(void)")
	retail_play_cinematic_block = _text_between(hlil_source, "10028e80    int32_t sub_10028e80", "10028eb5")
	retail_draw_cinematic_block = _text_between(hlil_source, "10028ec0    int32_t sub_10028ec0", "10028f20")
	load_hud_block = _block_from_marker(source, "void CG_LoadHudMenu( void )")
	register_fonts_block = _block_from_marker(source, "static void CG_RegisterHudFonts( void )")
	asset_block = _block_from_marker(source, "void CG_AssetCache( void )")
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
		"cgDC.feederItemImage = &CG_FeederItemImage;",
		"cgDC.feederItemText = &CG_FeederItemText;",
		"cgDC.feederSelection = &CG_FeederSelection;",
		"cgDC.getCVarValue = CG_Cvar_Get;",
		"cgDC.playCinematic = &CG_PlayCinematic;",
		"cgDC.stopCinematic = &CG_StopCinematic;",
		"cgDC.drawCinematic = &CG_DrawCinematic;",
		"cgDC.runCinematicFrame = &CG_RunCinematicFrame;",
		"cgDC.adjustFrom640 = &CG_AdjustFrom640;",
		"cgDC.setAdjustFrom640Mode = &CG_SetAdjustFrom640Mode;",
		"cgDC.bias = cgs.screenXBias;",
		"Init_Display( &cgDC );",
	):
		assert expected in display_block

	for expected in (
		"_DAT_10a2567c = &LAB_10028c30;",
		"_DAT_10a256d8 = &LAB_10028e80;",
		"_DAT_10a256dc = &LAB_10028ec0;",
		"_DAT_10a256e0 = &LAB_10028ed0;",
		"_DAT_10a256e4 = &LAB_10028f20;",
	):
		assert expected in retail_bootstrap_block

	assert "trap_Cvar_VariableStringBuffer( cvar, buff, sizeof( buff ) );" in cvar_float_block
	assert "return atof( buff );" in cvar_float_block
	assert "trap_CIN_PlayCinematic( name, x, y, w, h, CIN_loop );" in play_cinematic_block
	assert "trap_CIN_StopCinematic( handle );" in stop_cinematic_block
	assert "trap_CIN_SetExtents( handle, x, y, w, h );" in draw_cinematic_block
	assert "trap_CIN_DrawCinematic( handle );" in draw_cinematic_block
	assert "trap_CIN_RunCinematic( handle );" in run_cinematic_block

	assert "int.d(fconvert.t(arg2))" in retail_play_cinematic_block
	assert "int.d(fconvert.t(arg5)), 2)" in retail_play_cinematic_block
	assert "+ 0x194" in retail_play_cinematic_block
	assert "+ 0x198" in retail_draw_cinematic_block
	assert "a4 01 00 00" in retail_draw_cinematic_block
	assert "a0 01 00 00" in retail_draw_cinematic_block

	assert "Init_Display(" not in load_hud_block
	assert "CG_RegisterHudFonts();" not in asset_block
	for expected in (
		"trap_R_RegisterFont( QL_FONT_NAME_TEXT, QL_FONT_TEXT_POINT_SIZE, &cgDC.Assets.textFont );",
		"trap_R_RegisterFont( QL_FONT_NAME_SMALL, QL_FONT_SMALL_POINT_SIZE, &cgDC.Assets.smallFont );",
		"trap_R_RegisterFont( QL_FONT_NAME_BIG, QL_FONT_BIG_POINT_SIZE, &cgDC.Assets.bigFont );",
		"cgDC.Assets.fontRegistered = qtrue;",
	):
		assert expected in register_fonts_block

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
	cursor_block = _block_from_marker(main_source, "void CG_Text_PaintWithCursor( float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style )")

	for expected in (
		'{ &cg_smallFont, "ui_smallFont", "0.25", CVAR_ARCHIVE}',
		'{ &cg_bigFont, "ui_bigFont", "0.4", CVAR_ARCHIVE}',
	):
		assert expected in main_source

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
	assert "cg_bigFont" not in select_block

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


def test_cgame_host_text_metrics_extents_and_cursor_wrappers_use_retail_traps() -> None:
	draw_source = CG_DRAW.read_text(encoding="utf-8")
	main_source = CG_MAIN.read_text(encoding="utf-8")
	metrics_block = _block_from_marker(draw_source, "static void CG_GetHostTextMetrics")
	span_block = _block_from_marker(draw_source, "static void CG_DrawHostTextSpan")
	extents_block = _block_from_marker(draw_source, "static void CG_Text_GetExtents")
	cursor_ext_block = _block_from_marker(main_source, "static void CG_Text_PaintWithCursorExt")
	cursor_block = _block_from_marker(main_source, "void CG_Text_PaintWithCursor( float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style )")

	for expected in (
		"CG_AdjustFrom640( NULL, NULL, &xScale, &yScale );",
		"limitEnd = CG_GetTextLimitEnd( text, limit );",
		"packed = trap_QL_MeasureText(",
		"CG_SelectTextFontHandle( scale, fontIndex ),",
		"scale * QL_FONT_HOST_POINT_SIZE * yScale,",
		"CG_UnpackFloatBits64( packed, &width, &height );",
		"*outWidth = (int)( width / xScale );",
		"*outHeight = (int)( height / yScale );",
	):
		assert expected in metrics_block

	for expected in (
		"CG_AdjustFrom640( &screenX, &screenY, NULL, &yScale );",
		"hostScale = scale * QL_FONT_HOST_POINT_SIZE * yScale;",
		"fontHandle = CG_SelectTextFontHandle( scale, fontIndex );",
		"shadowOffset = ( style == ITEM_TEXTSTYLE_SHADOWED ) ? 1.0f : 2.0f;",
		"trap_QL_DrawScaledText( (int)shadowX, (int)shadowY, text, fontHandle, hostScale, 0, NULL, qtrue );",
		"trap_QL_DrawScaledText( (int)screenX, (int)screenY, text, fontHandle, hostScale, 0, NULL, forceColor );",
	):
		assert expected in span_block

	assert "CG_GetHostTextMetrics( text, scale, limit, ITEM_FONT_INHERIT, outWidth, outHeight );" in extents_block

	for expected in (
		"(void)cursorPos;",
		"(void)cursor;",
		"CG_Text_PaintExt( x, y, scale, color, text, 0.0f, limit, style, fontIndex );",
	):
		assert expected in cursor_ext_block
	assert "CG_Text_PaintWithCursorExt( x, y, scale, color, text, cursorPos, cursor, limit, style, ITEM_FONT_INHERIT );" in cursor_block

	assert "CG_Text_PaintChar" not in span_block
	assert "trap_R_DrawStretchPic" not in span_block


def test_cgame_text_paint_limit_reuses_shared_font_selector() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	ext_block = _block_from_marker(source, "static void CG_Text_Paint_LimitExt")
	wrapper_block = _block_from_marker(source, "static void CG_Text_Paint_Limit")

	for expected in (
		"CG_AdjustFrom640( &screenX, &screenY, NULL, NULL );",
		"CG_AdjustFrom640( &screenMaxX, NULL, NULL, NULL );",
		"CG_AdjustFrom640( &xBias, NULL, &xScale, &yScale );",
		"fontHandle = CG_SelectTextFontHandle( scale, fontIndex );",
		"trap_QL_DrawScaledText(",
		"scale * QL_FONT_HOST_POINT_SIZE * yScale,",
		"(int)screenMaxX,",
		"&outMaxX,",
		"*maxX = ( outMaxX - xBias ) / xScale;",
	):
		assert expected in ext_block

	assert "CG_Text_Paint_LimitExt( maxX, x, y, scale, color, text, adjust, limit, ITEM_FONT_INHERIT );" in wrapper_block
	assert "fontHandle = ( scale <= cg_smallFont.value ) ? FONT_SANS : FONT_DEFAULT;" not in ext_block
	assert "trap_R_DrawStretchPic" not in ext_block


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


def test_cgame_native_export_table_and_vmmain_wrappers_match_retail_order() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	public_source = CG_PUBLIC.read_text(encoding="utf-8")
	native_table = source[source.index("static void *cg_nativeExports"):source.index("void **CG_GetNativeExportTable")]
	vm_main_block = _block_from_marker(source, "int vmMain")
	draw_wrapper = _block_from_marker(source, "static void CG_NativeDrawActiveFrame")
	key_wrapper = _block_from_marker(source, "static void CG_NativeKeyEvent")
	mouse_wrapper = _block_from_marker(source, "static void CG_NativeMouseEvent")
	chat_down_wrapper = _block_from_marker(source, "static void CG_NativeChatDown")
	chat_up_wrapper = _block_from_marker(source, "static void CG_NativeChatUp")
	export_getter = _block_from_marker(source, "void **CG_GetNativeExportTable")
	retail_entry_block = _text_between(hlil_source, "10020a70    void*** dllEntry", "10020a90")
	retail_native_table = _text_between(hlil_source, "100769a8  void* data_100769a8", "100769fc")
	native_enum = _text_between(public_source, "typedef enum {\n\tCG_NATIVE_EXPORT_INIT", "} cgameNativeExport_t;")

	assert "CG_DrawActiveFrame( serverTime, stereoView, demoPlayback );" in draw_wrapper
	assert "CG_KeyEvent( key, down );" in key_wrapper
	for expected in (
		"cgDC.cursorx = cgs.cursorX;",
		"cgDC.cursory = cgs.cursorY;",
		"CG_MouseEvent( dx, dy );",
	):
		assert expected in mouse_wrapper
	assert "cg.chatHistoryVisible = qtrue;" in chat_down_wrapper
	assert "cg.chatHistoryVisible = qfalse;" in chat_up_wrapper
	assert "return cg_nativeExports;" in export_getter

	for expected in (
		"case CG_DRAW_ACTIVE_FRAME:",
		"CG_NativeDrawActiveFrame( arg0, arg1, arg2 ? qtrue : qfalse );",
		"case CG_KEY_EVENT:",
		"CG_NativeKeyEvent( arg0, arg1 ? qtrue : qfalse );",
		"case CG_MOUSE_EVENT:",
		"cgDC.cursorx = cgs.cursorX;",
		"cgDC.cursory = cgs.cursorY;",
		"CG_MouseEvent( arg0, arg1 );",
		"case CG_EVENT_HANDLING:",
		"CG_EventHandling( arg0 );",
		"case CG_CHAT_DOWN:",
		"cg.chatHistoryVisible = qtrue;",
		"case CG_CHAT_UP:",
		"cg.chatHistoryVisible = qfalse;",
	):
		assert expected in vm_main_block

	expected_exports = (
		"[CG_NATIVE_EXPORT_INIT] = CG_Init,",
		"[CG_NATIVE_EXPORT_REGISTER_CVARS] = CG_RegisterCvars,",
		"[CG_NATIVE_EXPORT_SHUTDOWN] = CG_Shutdown,",
		"[CG_NATIVE_EXPORT_CONSOLE_COMMAND] = CG_ConsoleCommand,",
		"[CG_NATIVE_EXPORT_DRAW_ACTIVE_FRAME] = CG_NativeDrawActiveFrame,",
		"[CG_NATIVE_EXPORT_CROSSHAIR_PLAYER] = CG_CrosshairPlayer,",
		"[CG_NATIVE_EXPORT_LAST_ATTACKER] = CG_LastAttacker,",
		"[CG_NATIVE_EXPORT_KEY_EVENT] = CG_NativeKeyEvent,",
		"[CG_NATIVE_EXPORT_MOUSE_EVENT] = CG_NativeMouseEvent,",
		"[CG_NATIVE_EXPORT_EVENT_HANDLING] = CG_EventHandling,",
		"[CG_NATIVE_EXPORT_SHOW_1ST_TRACKED_PLAYER] = CG_Show1stTrackedPlayer,",
		"[CG_NATIVE_EXPORT_SHOW_2ND_TRACKED_PLAYER] = CG_Show2ndTrackedPlayer,",
		"[CG_NATIVE_EXPORT_CHAT_DOWN] = CG_NativeChatDown,",
		"[CG_NATIVE_EXPORT_CHAT_UP] = CG_NativeChatUp,",
		"[CG_NATIVE_EXPORT_GET_PHYSICS_TIME] = CG_GetPhysicsTime,",
		"[CG_NATIVE_EXPORT_COPY_CLIENT_IDENTITY] = CG_CopyClientIdentity,",
		"[CG_NATIVE_EXPORT_RESERVED_NULL] = NULL,",
		"[CG_NATIVE_EXPORT_GET_CHAT_FIELD_Y] = CG_NativeGetChatFieldY,",
		"[CG_NATIVE_EXPORT_GET_CHAT_FIELD_PIXEL_WIDTH] = CG_NativeGetChatFieldPixelWidth,",
		"[CG_NATIVE_EXPORT_GET_CHAT_FIELD_WIDTH_IN_CHARS] = CG_GetChatFieldWidthInChars,",
		"[CG_NATIVE_EXPORT_SET_CLIENT_SPEAKING_STATE] = CG_NativeSetClientSpeakingState",
	)
	last_index = -1
	for expected in expected_exports:
		current_index = native_table.index(expected)
		assert current_index > last_index
		last_index = current_index
		assert expected.split("]")[0].removeprefix("[") in native_enum

	for expected in (
		"*arg1 = &data_100769a8",
		"*arg3 = 8",
	):
		assert expected in retail_entry_block

	for expected in (
		"100769a8  void* data_100769a8 = sub_10029820",
		"100769ac  void* data_100769ac = sub_10020bb0",
		"100769b0  void* data_100769b0 = sub_10029fc0",
		"100769b4  void* data_100769b4 = sub_10007f00",
		"100769b8  void* data_100769b8 = sub_1004e4e0",
		"100769bc  void* data_100769bc = sub_10020d60",
		"100769c0  void* data_100769c0 = sub_10020d80",
		"100769c4  void* data_100769c4 = sub_1003c6f0",
		"100769c8  void* data_100769c8 = 0x100208f0",
		"100769cc  void* data_100769cc = sub_1003c620",
		"100769d0  void* data_100769d0 = sub_10029ff0",
		"100769d4  void* data_100769d4 = sub_1002a060",
		"100769d8  void* data_100769d8 = sub_10007cd0",
		"100769dc  void* data_100769dc = sub_10007cf0",
		"100769e0  void* data_100769e0 = sub_1004e4d0",
		"100769e4  void* data_100769e4 = sub_10020910",
		"100769e8",
		"00 00 00 00",
		"100769ec  void* data_100769ec = sub_100209e0",
		"100769f0  void* data_100769f0 = sub_10020a00",
		"100769f4  void* data_100769f4 = sub_10020a20",
		"100769f8  void* data_100769f8 = sub_10020a40",
	):
		assert expected in retail_native_table


def test_cgame_advert_bridge_lifecycle_matches_retail_init_and_shutdown_order() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	symbol_map = (REPO_ROOT / "references" / "symbol-maps" / "cgame.json").read_text(encoding="utf-8")
	alias_map = (REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json").read_text(encoding="utf-8")
	native_table = source[source.index("static void *cg_nativeExports"):source.index("void **CG_GetNativeExportTable")]
	init_block = _block_from_marker(source, "void CG_Init( int serverMessageNum, int serverCommandSequence, int clientNum )")
	shutdown_block = _block_from_marker(source, "void CG_Shutdown( void )")
	retail_init_tail = _text_between(hlil_source, "10029e21  sub_10029420()", "10029fc0")
	retail_shutdown_block = _text_between(hlil_source, "10029fc0    int32_t sub_10029fc0", "10029ff0")
	retail_native_table = _text_between(hlil_source, "100769a8  void* data_100769a8", "100769d0")

	assert "trap_AdvertisementBridge_InitCGame();" in init_block
	assert init_block.index("trap_AdvertisementBridge_InitCGame();") > init_block.index("CG_ShaderStateChanged();")
	assert init_block.index("trap_AdvertisementBridge_InitCGame();") < init_block.index("trap_S_ClearLoopingSounds( qtrue );")
	assert init_block.index("CG_SetConfigValues();") < init_block.index("CG_StartMusic();")

	assert "trap_AdvertisementBridge_ShutdownCGame();" in shutdown_block
	assert shutdown_block.index("trap_AdvertisementBridge_ShutdownCGame();") < shutdown_block.index('trap_Cvar_Set( "ui_mainmenu", "1" );')

	for expected in (
		"[CG_NATIVE_EXPORT_INIT] = CG_Init,",
		"[CG_NATIVE_EXPORT_SHUTDOWN] = CG_Shutdown,",
	):
		assert expected in native_table

	for expected in (
		"sub_10029420()",
		"sub_10029120()",
		"sub_10049420",
		"sub_10025320()",
		"(*(data_1074cccc + 0xf4))()",
		"sub_100295c0()",
		"sub_100253f0()",
	):
		assert expected in retail_init_tail

	assert retail_init_tail.index("sub_10049420") < retail_init_tail.index("sub_10025320()")
	assert retail_init_tail.index("(*(data_1074cccc + 0xf4))()") < retail_init_tail.index("sub_100295c0()")
	assert retail_init_tail.index("sub_100295c0()") < retail_init_tail.index("sub_100253f0()")

	for expected in (
		"(*(data_1074cccc + 0xf8))()",
		'(*(data_1074cccc + 0x1c))("ui_mainmenu", &data_10068c04)',
	):
		assert expected in retail_shutdown_block

	for expected in (
		"100769a8  void* data_100769a8 = sub_10029820",
		"100769b0  void* data_100769b0 = sub_10029fc0",
	):
		assert expected in retail_native_table

	for expected in (
		'"sub_10029fc0": "CG_Shutdown"',
		'"address": "0x10029820"',
		'"normalized_name": "CG_Init"',
		'"address": "0x10029FC0"',
		'"normalized_name": "CG_Shutdown"',
	):
		assert expected in alias_map or expected in symbol_map


def test_cgame_drawtools_keep_retail_widescreen_bias_consumers() -> None:
	source = CG_DRAWTOOLS.read_text(encoding="utf-8")
	adjust_block = _block_from_marker(source, "void CG_AdjustFrom640")
	team_color_block = _block_from_marker(source, "float *CG_TeamColor")

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

	for expected in (
		"static vec4_t\tfree = {1.0f, 0.8f, 0.2f, 1.0f};",
		"static vec4_t\tred = {1.0f, 0.2f, 0.1f, 1.0f};",
		"static vec4_t\tblue = {0.2f, 0.4f, 1.0f, 1.0f};",
		"static vec4_t\tspectator = {0.75f, 0.75f, 0.75f, 1.0f};",
		"case TEAM_FREE:",
	):
		assert expected in team_color_block


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
	assert "*targetWidth = (float)cg.refdef.width;" in aspect_block
	assert "*targetHeight = (float)cg.refdef.height;" in aspect_block
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
		"marker->origin[0] += CG_DamagePlumRandom() * 20.0f - 10.0f;",
		"marker->duration = 1000;",
		"marker->fadeDelay = 600;",
		"marker->rise = 0.0f;",
		"marker->textScale = 0.15f;",
		"marker->screenVelocity[0] = CG_DamagePlumRandom() * 100.0f - 50.0f;",
		"marker->screenVelocity[1] = -120.0f - CG_DamagePlumRandom() * 20.0f;",
		"marker->screenAcceleration[1] = 150.0f;",
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


def test_cgame_damage_plum_retail_color_and_motion_constants() -> None:
	event_source = CG_EVENT.read_text(encoding="utf-8")
	draw_source = CG_DRAW.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	random_block = _block_from_marker(event_source, "static float CG_DamagePlumRandom")
	lerp_block = _block_from_marker(event_source, "static void CG_LerpDamagePlumColor")
	weapon_color_block = _block_from_marker(event_source, "static void CG_GetDamagePlumWeaponColor")
	color_block = _block_from_marker(event_source, "static void CG_GetDamagePlumColor")
	draw_block = _block_from_marker(draw_source, "void CG_DrawQueuedWorldMarkers")

	assert "static int damagePlumSeed = 0x92;" in event_source
	assert "static const vec4_t cg_damagePlumWhite = { 1.0f, 1.0f, 1.0f, 1.0f };" in event_source
	assert "static const vec4_t cg_damagePlumRed = { 1.0f, 0.0f, 0.0f, 1.0f };" in event_source
	assert "return Q_random( &damagePlumSeed );" in random_block

	for expected in (
		"frac = Com_Clamp( 0.0f, 1.0f, frac );",
		"color[i] = start[i] + ( end[i] - start[i] ) * frac;",
	):
		assert expected in lerp_block

	for expected in (
		"stats = BG_GetWeaponStats( weapon );",
		"color[0] = stats->pickupHandicapScale;",
		"color[1] = stats->armorHandicapScale;",
		"color[2] = stats->healthHandicapScale;",
		"color[3] = stats->respawnHandicapScale;",
	):
		assert expected in weapon_color_block

	for expected in (
		"if ( damage > 75 ) {",
		"color[0] = 1.0f;",
		"color[1] = 0.0f;",
		"color[2] = 0.0f;",
		"} else if ( damage > 50 ) {",
		"color[1] = 0.5f;",
		"} else if ( damage <= 25 ) {",
		"color[0] = 0.25f;",
		"color[1] = 0.5f;",
		"color[2] = 1.0f;",
		"CG_GetDamagePlumWeaponColor( weapon, color );",
		"CG_LerpDamagePlumColor( color, cg_damagePlumWhite, cg_damagePlumRed, (float)damage / 100.0f );",
	):
		assert expected in color_block

	assert "float\t\tscreenVelocity[2];" in local_source
	assert "float\t\tscreenAcceleration[2];" in local_source
	for expected in (
		"float\t\t\telapsedSeconds;",
		"elapsedSeconds = (float)( cg.time - marker->startTime ) * 0.001f;",
		"screenX += marker->screenVelocity[0] * elapsedSeconds +",
		"0.5f * marker->screenAcceleration[0] * elapsedSeconds * elapsedSeconds;",
		"drawY = screenY + marker->screenVelocity[1] * elapsedSeconds +",
		"0.5f * marker->screenAcceleration[1] * elapsedSeconds * elapsedSeconds;",
	):
		assert expected in draw_block


def test_cgame_weapon_token_index_parser_uses_retail_bit_order() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	event_source = CG_EVENT.read_text(encoding="utf-8")
	token_table = _block_from_marker(main_source, "static const cgRetailWeaponToken_t cgRetailWeaponTokens")
	damage_bit_block = _block_from_marker(main_source, "unsigned int CG_DamagePlumBitForWeapon")
	damage_mask_block = _block_from_marker(main_source, "static unsigned int CG_ParseDamagePlumWeaponMask")
	should_render_block = _block_from_marker(event_source, "qboolean CG_ShouldRenderDamagePlumForWeapon")

	for expected in (
		'{ "g", WP_GAUNTLET, 1 }',
		'{ "mg", WP_MACHINEGUN, 2 }',
		'{ "sg", WP_SHOTGUN, 3 }',
		'{ "gl", WP_GRENADE_LAUNCHER, 4 }',
		'{ "rl", WP_ROCKET_LAUNCHER, 5 }',
		'{ "lg", WP_LIGHTNING, 6 }',
		'{ "rg", WP_RAILGUN, 7 }',
		'{ "pg", WP_PLASMAGUN, 8 }',
		'{ "bfg", WP_BFG, 9 }',
		'{ "gh", WP_GRAPPLING_HOOK, 10 }',
		'{ "ng", WP_NAILGUN, 11 }',
		'{ "pl", WP_PROX_LAUNCHER, 12 }',
		'{ "cg", WP_CHAINGUN, 13 }',
		'{ "hmg", WP_HEAVY_MACHINEGUN, 14 }',
	):
		assert expected in token_table

	for expected in (
		"#define DAMAGE_PLUM_ALL_WEAPONS_MASK\t0x7ffeu",
		"while ( tokenCount < 16 )",
		"mask |= DAMAGE_PLUM_WEAPON_BIT( weaponToken->index );",
		"return DAMAGE_PLUM_WEAPON_BIT( cgRetailWeaponTokens[i].index );",
	):
		assert expected in main_source

	assert "weaponBit = CG_DamagePlumBitForWeapon( weapon );" in should_render_block
	assert "1u << weapon" not in should_render_block

	for stale in (
		'"gauntlet"',
		'"machinegun"',
		'"heavy_machinegun"',
		'"rocket_launcher"',
		'"grappling_hook"',
	):
		assert stale not in token_table
		assert stale not in damage_mask_block
		assert stale not in damage_bit_block


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

	assert 'trap_Cvar_Set( "cg_weaponPrimary", va( "%i", cg.weaponPrimary ) );' in respawn_block
	assert "CG_SelectRespawnWeapon();" in respawn_block
	assert respawn_block.index('trap_Cvar_Set( "cg_weaponPrimary"') < respawn_block.index("CG_SelectRespawnWeapon();")
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
	uses_block = _block_from_marker(game_items_source, "qboolean G_ItemUsesRespawnTimer")
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
		"if ( item->giType == IT_ARMOR && item->quantity >= 25 ) {",
		"if ( item->giType == IT_HEALTH && item->quantity >= 100 ) {",
		"if ( item->giType == IT_POWERUP ) {",
		"case PW_QUAD:",
		"case PW_BATTLESUIT:",
		"case PW_HASTE:",
		"case PW_INVIS:",
		"case PW_REGEN:",
		"if ( item->giType == IT_HOLDABLE && BG_HoldableForItemTag( item->giTag ) == HI_MEDKIT ) {",
	):
		assert expected in uses_block

	for expected in (
		"ent->s.time = markerTime;",
		"ent->s.time2 = respawnDuration;",
		"ent->s.retailEventData = ent->team ? 1 : 0;",
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
		"(qboolean)( es->retailEventData != 0 ) );",
	):
		assert expected in item_block


def test_cgame_vote_widget_reconstruction_uses_retail_vote_cvar_and_text_paths() -> None:
	servercmds_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c" ).read_text(encoding="utf-8")
	main_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c" ).read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	vote_gametype_block = _block_from_marker(newdraw_source, "static void CG_DrawVoteGametype")
	vote_map_block = _block_from_marker(newdraw_source, "static void CG_DrawVoteMapSlot")
	vote_name_block = _block_from_marker(newdraw_source, "static void CG_DrawVoteName")
	vote_timer_block = _block_from_marker(newdraw_source, "static void CG_DrawVoteTimer")
	vote_timer_hlil = _text_between(hlil_source, "10035920    void sub_10035920", "10035a10")
	vote_count_block = _block_from_marker(newdraw_source, "static void CG_DrawVoteCount")
	vote_shot_block = _block_from_marker(newdraw_source, "static void CG_DrawVoteShot")
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
		assert expected in vote_timer_hlil

	assert "data_10a3ffc4 - data_10a9c1ec + 0x4e20" in vote_timer_hlil
	assert "remaining = ( cgs.voteTime - cg.time + 20000 ) / 1000;" in vote_timer_block
	assert "if ( !cgs.voteTime ) {" not in vote_timer_block
	assert "VOTE_TIME - ( cg.time - cgs.voteTime ) + 999" not in vote_timer_block
	assert '"Vote %is"' not in vote_timer_block
	assert "CG_Text_Paint( rect->x, rect->y - 8.0f, scale, color, buffer, 0, 0, textStyle );" in vote_gametype_block
	assert "CG_GetTextPosition" not in vote_gametype_block
	assert "CG_Text_Paint( rect->x, rect->y, scale, color, buffer, 0, 0, textStyle );" in vote_map_block
	assert "CG_GetTextPosition" not in vote_map_block
	assert "CG_Text_Paint( rect->x, rect->y, scale, color, buffer, 0, 0, textStyle );" in vote_name_block
	assert "CG_GetTextPosition" not in vote_name_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "Votes: %s", countText );' in vote_count_block
	assert "CG_AlignTextX( &x, buffer, scale, align );" in vote_count_block
	assert "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );" in vote_count_block
	assert "CG_GetTextPosition" not in vote_count_block
	assert "CG_AlignTextX( &x, buffer, scale, align );" in vote_timer_block
	assert "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );" in vote_timer_block
	assert "CG_GetTextPosition" not in vote_timer_block
	assert 'CG_GetVoteSlotString( slot, "Shot", previewToken, sizeof( previewToken ) );' in vote_shot_block
	assert 'Q_strncpyz( previewToken, "default", sizeof( previewToken ) );' in vote_shot_block
	assert 'Com_sprintf( path, sizeof( path ), "levelshots/preview/%s", previewToken );' in vote_shot_block
	assert "trap_R_RegisterShaderNoMip( path );" in vote_shot_block


def test_cgame_rotation_vote_payload_populates_endgamevote_ownerdraw_cvars() -> None:
	servercmds_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c" ).read_text(encoding="utf-8")
	parse_block = _block_from_marker(servercmds_source, "static void CG_ParseRotationVoteConfigStrings( void )")
	config_modified_block = _block_from_marker(servercmds_source, "static void CG_ConfigStringModified( void )")
	set_config_values_block = _block_from_marker(servercmds_source, "void CG_SetConfigValues")

	assert "static void CG_SetRotationVoteSlotCvar( int slot, const char *suffix, const char *value ) {" in servercmds_source
	assert 'rotationTitles = CG_ConfigString( CS_ROTATION_TITLES );' in parse_block
	assert 'rotationCounts = CG_ConfigString( CS_ROTATION_CONFIGS );' in parse_block
	assert 'CG_SetRotationVoteSlotCvar( slot, "Map", mapName );' in parse_block
	assert 'CG_SetRotationVoteSlotCvar( slot, "Name", voteName );' in parse_block
	assert 'CG_SetRotationVoteSlotCvar( slot, "Gametype", voteGametype );' in parse_block
	assert 'CG_SetRotationVoteSlotCvar( slot, "Count", voteCount );' in parse_block
	assert 'CG_SetRotationVoteSlotCvar( slot, "Shot", voteShot );' in parse_block
	assert "Q_strncpyz( voteShot, mapName, sizeof( voteShot ) );" in parse_block
	assert '"levelshots/%s"' not in parse_block
	assert "CG_ParseRotationVoteConfigStrings();" in set_config_values_block
	assert "} else if ( num == CS_ROTATION_TITLES || num == CS_ROTATION_CONFIGS ) {" in config_modified_block
	assert "CG_ParseRotationVoteConfigStrings();" in config_modified_block


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
		"static int UI_ResolveMenuWidescreenMode(const menuDef_t *menu) {",
		"if (!menu->widescreenSet && !menu->fullScreen) {",
		"return WIDESCREEN_CENTER;",
		"if (DC->setAdjustFrom640Mode && item->widescreenSet) {",
		"DC->setAdjustFrom640Mode(item->widescreen);",
		"DC->setAdjustFrom640Mode(parent ? UI_ResolveMenuWidescreenMode(parent) : WIDESCREEN_CENTER);",
		"DC->setAdjustFrom640Mode(UI_ResolveMenuWidescreenMode(menu));",
		"DC->setAdjustFrom640Mode(WIDESCREEN_CENTER);",
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
	menu_update_block = _block_from_marker(source, "void Menu_UpdatePosition(menuDef_t *menu)")
	background_block = _block_from_marker(source, "static void UI_DrawFullscreenBackground(const menuDef_t *menu)")
	paint_block = _block_from_marker(source, "void Menu_Paint(menuDef_t *menu, qboolean forcePaint)")
	parse_block = _block_from_marker(source, "qboolean MenuParse_widescreen( itemDef_t *item, int handle )")

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
		"sourceWidth = menu->backgroundRect.w;",
		"if (sourceWidth > 0.0f) {",
		"screenWidth = (float)DC->glconfig.vidWidth;",
		"screenHeight = (float)DC->glconfig.vidHeight;",
		"s0 = ((sourceWidth - screenWidth * (sourceHeight / screenHeight)) / sourceWidth) * 0.5f;",
		"DC->drawStretchPic(0.0f, 0.0f, screenWidth, screenHeight, s0, 0.0f, 1.0f - s0, 1.0f, menu->window.background);",
		"DC->drawHandlePic(0.0f, 0.0f, SCREEN_WIDTH, SCREEN_HEIGHT, menu->window.background);",
	):
		assert expected in background_block

	assert "UI_DrawFullscreenBackground(menu);" in paint_block
	assert "UI_ApplyWidescreenRect(&rect, UI_ResolveMenuWidescreenMode(menu));" in menu_update_block
	assert "menu->widescreenSet = qtrue;" in parse_block


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
		"CG_QL_IMPORT_R_REGISTERFONT = 93",
		"CG_QL_IMPORT_DRAW_SCALED_TEXT = 123",
		"CG_QL_IMPORT_MEASURE_TEXT = 124",
		"CG_QL_IMPORT_TOTAL_COUNT",
	):
		assert expected in public_source

	assert (
		public_source.index("CG_QL_IMPORT_R_REGISTERFONT = 93")
		< public_source.index("CG_QL_IMPORT_DRAW_SCALED_TEXT = 123")
		< public_source.index("CG_QL_IMPORT_MEASURE_TEXT = 124")
	)

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
		"void\t\ttrap_QL_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor );",
		"unsigned long long trap_QL_MeasureText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outLeft );",
	):
		assert expected in local_source


def test_cgame_font_syscall_bridge_uses_native_host_text_imports() -> None:
	syscalls = CG_SYSCALLS.read_text(encoding="utf-8")
	draw_block = _block_from_marker(syscalls, "void trap_QL_DrawScaledText")
	measure_block = _block_from_marker(syscalls, "unsigned long long trap_QL_MeasureText")

	for expected in (
		"ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_DRAW_SCALED_TEXT );",
		"if ( !import ) {",
		"return;",
		"((void (QDECL *)( int, int, const char *, int, float, int, float *, int ))import)( x, y, text, fontHandle, scale, maxX, outMaxX, forceColor ? qtrue : qfalse );",
	):
		assert expected in draw_block

	for expected in (
		"ql_import_f import = CG_GetNativeImportFunction( CG_QL_IMPORT_MEASURE_TEXT );",
		"if ( !import ) {",
		"return 0;",
		"return ((unsigned long long (QDECL *)( const char *, const char *, int, float, int, float * ))import)( text, end, fontHandle, scale, maxX, outLeft );",
	):
		assert expected in measure_block

	assert "syscall(" not in draw_block
	assert "syscall(" not in measure_block


def test_cgame_q3_vm_font_import_stubs_fail_closed() -> None:
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	draw_stub = _block_from_marker(local_source, "static ID_INLINE void trap_QL_DrawScaledText")
	measure_stub = _block_from_marker(local_source, "static ID_INLINE unsigned long long trap_QL_MeasureText")

	for expected in (
		"(void)x;",
		"(void)y;",
		"(void)text;",
		"(void)fontHandle;",
		"(void)scale;",
		"(void)maxX;",
		"if ( outMaxX ) {",
		"*outMaxX = 0.0f;",
		"(void)forceColor;",
	):
		assert expected in draw_stub

	for expected in (
		"(void)text;",
		"(void)end;",
		"(void)fontHandle;",
		"(void)scale;",
		"(void)maxX;",
		"if ( outLeft ) {",
		"*outLeft = 0.0f;",
		"return 0;",
	):
		assert expected in measure_stub

	assert "syscall(" not in draw_stub
	assert "syscall(" not in measure_stub


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
	draw_block = _block_from_marker(client_source, "static void QDECL QL_CG_trap_DrawScaledText")
	measure_block = _block_from_marker(client_source, "static unsigned long long QDECL QL_CG_trap_MeasureText")

	for expected in (
		"static void QDECL QL_CG_trap_R_RegisterFont( const char *fontName, int pointSize, fontInfo_t *font ) {",
		"CG_Import_Syscall(CG_R_REGISTERFONT, fontName, pointSize, font );",
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
		"ql_cgame_imports[CG_QL_IMPORT_R_REGISTERFONT] = (ql_import_f)QL_CG_trap_R_RegisterFont;",
		"ql_cgame_imports[CG_QL_IMPORT_DRAW_SCALED_TEXT] = (ql_import_f)QL_CG_trap_DrawScaledText;",
		"ql_cgame_imports[CG_QL_IMPORT_MEASURE_TEXT] = (ql_import_f)QL_CG_trap_MeasureText;",
	):
		assert expected in client_source

	assert (
		client_source.index("ql_cgame_imports[CG_QL_IMPORT_R_REGISTERFONT] = (ql_import_f)QL_CG_trap_R_RegisterFont;")
		< client_source.index("ql_cgame_imports[CG_QL_IMPORT_DRAW_SCALED_TEXT] = (ql_import_f)QL_CG_trap_DrawScaledText;")
		< client_source.index("ql_cgame_imports[CG_QL_IMPORT_MEASURE_TEXT] = (ql_import_f)QL_CG_trap_MeasureText;")
	)

	assert "RE_DrawScaledText( x, y, text, fontHandle, scale, maxX, outMaxX, forceColor != qfalse ? qtrue : qfalse, ql_cgame_currentColor );" in draw_block
	assert "float width;" in measure_block
	assert "float height;" in measure_block
	assert "RE_MeasureScaledText( text, end, fontHandle, scale, maxX, &width, &height, outLeft );" in measure_block
	assert "return QL_CG_PackFloatBits64( width, height );" in measure_block
	assert "RE_RegisterFont" not in draw_block
	assert "RE_RegisterFont" not in measure_block


def test_cgame_primary_ownerdraw_first_half_flags_are_defined_and_wired() -> None:
	menudef_source = MENUDEF_H.read_text(encoding="utf-8")
	ui_shared_source = UI_SHARED.read_text(encoding="utf-8")
	ui_shared_header = UI_SHARED_H.read_text(encoding="utf-8")
	main_source = CG_MAIN.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	primary_block = _block_from_marker(newdraw_source, "static qboolean CG_OwnerDrawPrimaryFlagVisible")
	visible_block = _block_from_marker(newdraw_source, "qboolean CG_OwnerDrawVisible")
	first_half_flags = {
		"CG_SHOW_BLUE_TEAM_HAS_REDFLAG": "0x00000001",
		"CG_SHOW_RED_TEAM_HAS_BLUEFLAG": "0x00000002",
		"CG_SHOW_DUEL": "0x00000004",
		"CG_SHOW_CLAN_ARENA": "0x00000008",
		"CG_SHOW_CTF": "0x00000010",
		"CG_SHOW_ONEFLAG": "0x00000020",
		"CG_SHOW_OBELISK": "0x00000040",
		"CG_SHOW_HARVESTER": "0x00000080",
		"CG_SHOW_DOMINATION": "0x00000100",
		"CG_SHOW_ANYNONTEAMGAME": "0x00000200",
		"CG_SHOW_ANYTEAMGAME": "0x00000400",
		"CG_SHOW_HEALTHCRITICAL": "0x00000800",
		"CG_SHOW_IF_NOT_WARMUP": "0x00001000",
		"CG_SHOW_IF_PLAYER_HAS_FLAG": "0x00002000",
		"CG_SHOW_IF_WARMUP": "0x00004000",
		"CG_SHOW_IF_BLUE_IS_FIRST_PLACE": "0x00008000",
	}

	for name, value in first_half_flags.items():
		assert re.search(rf"#define\s+{name}\s+{value}\b", menudef_source)
		assert name in primary_block

	for expected in (
		"int ownerDrawFlags;",
		"int ownerDrawFlags2;",
		"qboolean (*ownerDrawVisible) (int flags, int flags2);",
	):
		assert expected in ui_shared_header

	for expected in (
		"item->window.ownerDrawFlags |= i;",
		"menu->window.ownerDrawFlags |= i;",
		"DC->ownerDrawVisible(item->window.ownerDrawFlags, item->window.ownerDrawFlags2)",
		"!DC->ownerDrawVisible(menu->window.ownerDrawFlags, menu->window.ownerDrawFlags2)) {",
	):
		assert expected in ui_shared_source

	assert "cgDC.ownerDrawVisible = &CG_OwnerDrawVisible;" in main_source
	assert "CG_OwnerDrawPrimaryFlagVisible( flags )" in visible_block


def test_cgame_primary_ownerdraw_second_half_flags_are_defined_and_wired() -> None:
	menudef_source = MENUDEF_H.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	primary_block = _block_from_marker(newdraw_source, "static qboolean CG_OwnerDrawPrimaryFlagVisible")
	player_first_block = _block_from_marker(newdraw_source, "static qboolean CG_ShowPlayerIsFirstPlace")
	leading_team_block = _block_from_marker(newdraw_source, "static team_t CG_GetLeadingHudTeam")
	players_remaining_block = _block_from_marker(newdraw_source, "static qboolean CG_ShowPlayersRemaining")
	ownerdraw_block = _block_from_marker(newdraw_source, "void CG_OwnerDraw")
	second_half_flags = {
		"CG_SHOW_TEAMINFO": "0x00010000",
		"CG_SHOW_NOTEAMINFO": "0x00020000",
		"CG_SHOW_OTHERTEAMHASFLAG": "0x00040000",
		"CG_SHOW_YOURTEAMHASENEMYFLAG": "0x00080000",
		"CG_SHOW_INTERMISSION": "0x00100000",
		"CG_SHOW_NOTINTERMISSION": "0x00200000",
		"CG_SHOW_IF_MSG_PRESENT": "0x00400000",
		"CG_SHOW_IF_NOTICE_PRESENT": "0x00800000",
		"CG_SHOW_IF_CHAT_VISIBLE": "0x01000000",
		"CG_SHOW_IF_PLYR_IS_FIRST_PLACE": "0x02000000",
		"CG_SHOW_IF_PLYR_IS_NOT_FIRST_PLACE": "0x04000000",
		"CG_SHOW_IF_RED_IS_FIRST_PLACE": "0x08000000",
		"CG_SHOW_2DONLY": "0x10000000",
		"CG_SHOW_IF_PLYR_IS_ON_RED": "0x20000000",
		"CG_SHOW_IF_PLYR_IS_ON_BLUE": "0x40000000",
		"CG_SHOW_PLAYERS_REMAINING": "0x80000000",
	}

	for name, value in second_half_flags.items():
		assert re.search(rf"#define\s+{name}\s+{value}\b", menudef_source)

	for expected in (
		"if ( flags & CG_SHOW_TEAMINFO ) {",
		"cg_currentSelectedPlayer.integer == numSortedTeamPlayers",
		"if ( flags & CG_SHOW_NOTEAMINFO ) {",
		"cg_currentSelectedPlayer.integer != numSortedTeamPlayers",
		"if ( flags & CG_SHOW_OTHERTEAMHASFLAG ) {",
		"return CG_OtherTeamHasFlag();",
		"if ( flags & CG_SHOW_YOURTEAMHASENEMYFLAG ) {",
		"return CG_YourTeamHasFlag();",
		"if ( ( flags & CG_SHOW_INTERMISSION ) && cg.snap->ps.pm_type == PM_INTERMISSION ) {",
		"if ( ( flags & CG_SHOW_NOTINTERMISSION ) && cg.snap->ps.pm_type != PM_INTERMISSION ) {",
		"if ( ( flags & CG_SHOW_IF_MSG_PRESENT ) && CG_HasHudPlayerMessage() ) {",
		"if ( ( flags & CG_SHOW_IF_NOTICE_PRESENT ) && CG_HasHudNoticeMessage() ) {",
		"if ( ( flags & CG_SHOW_IF_CHAT_VISIBLE ) && ( cg.chatHistoryVisible || cg.scoreBoardShowing ) ) {",
		"if ( flags & ( CG_SHOW_IF_PLYR_IS_FIRST_PLACE | CG_SHOW_IF_PLYR_IS_NOT_FIRST_PLACE ) ) {",
		"if ( ( flags & CG_SHOW_IF_RED_IS_FIRST_PLACE ) && leadingTeam == TEAM_RED ) {",
		"if ( ( flags & CG_SHOW_IF_PLYR_IS_ON_RED ) && playerTeam == TEAM_RED ) {",
		"if ( ( flags & CG_SHOW_IF_PLYR_IS_ON_BLUE ) && playerTeam == TEAM_BLUE ) {",
		"if ( ( flags & CG_SHOW_PLAYERS_REMAINING ) && CG_ShowPlayersRemaining() ) {",
	):
		assert expected in primary_block

	assert "PM_SPINTERMISSION" not in primary_block
	assert "CG_SHOW_2DONLY" not in primary_block

	for expected in (
		"CG_DrawPlayerArmorIcon( &rect, ownerDrawFlags & CG_SHOW_2DONLY );",
		"CG_DrawPlayerAmmoIcon( &rect, ownerDrawFlags & CG_SHOW_2DONLY );",
		"CG_DrawPlayerHead( &rect, ownerDrawFlags & CG_SHOW_2DONLY );",
		"CG_DrawPlayerItem( &rect, scale, ownerDrawFlags & CG_SHOW_2DONLY );",
	):
		assert expected in ownerdraw_block

	for expected in (
		"cgs.scores1 != SCORE_NOT_PRESENT && cgs.scores2 != SCORE_NOT_PRESENT && cgs.scores1 < cgs.scores2",
		"return TEAM_BLUE;",
		"return TEAM_RED;",
	):
		assert expected in leading_team_block

	for expected in (
		"clientNum = cg.snap->ps.clientNum;",
		"if ( cgs.gametype >= GT_TEAM && cgs.gametype != GT_RED_ROVER ) {",
		"ci = &cgs.clientinfo[clientNum];",
		"if ( ci->team == TEAM_RED ) {",
		"return ( cgs.scores1 >= cgs.scores2 ) ? qtrue : qfalse;",
		"if ( ci->team == TEAM_BLUE ) {",
		"return ( cgs.scores2 > cgs.scores1 ) ? qtrue : qfalse;",
		"rank = cg.snap->ps.persistant[PERS_RANK];",
		"if ( rank & RANK_TIED_FLAG ) {",
		"return ( rank == 0 ) ? qtrue : qfalse;",
	):
		assert expected in player_first_block

	assert "CG_GetActiveScoreByIndex( 0 )" not in player_first_block
	assert "CG_GetScoreForClientNum( clientNum )" not in player_first_block

	for expected in (
		"case GT_CLAN_ARENA:",
		"case GT_FREEZE:",
		"case GT_ATTACK_DEFEND:",
		"case GT_RED_ROVER:",
	):
		assert expected in players_remaining_block


def test_cgame_secondary_ownerdrawflags2_are_defined_and_wired() -> None:
	menudef_source = MENUDEF_H.read_text(encoding="utf-8")
	ui_shared_source = UI_SHARED.read_text(encoding="utf-8")
	ui_shared_header = UI_SHARED_H.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	secondary_block = _block_from_marker(newdraw_source, "static qboolean CG_OwnerDrawSecondaryFlagVisible")
	slot_match_block = _block_from_marker(newdraw_source, "static qboolean CG_PlacementSlotContainsPredictedPlayer")
	slot_follow_block = _block_from_marker(newdraw_source, "static qboolean CG_PlacementSlotCanBeFollowed")
	weapon_fired_block = _block_from_marker(newdraw_source, "static qboolean CG_PlacementWeaponFired")
	loadout_block = _block_from_marker(newdraw_source, "static qboolean CG_LoadoutsEnabled")
	visible_block = _block_from_marker(newdraw_source, "qboolean CG_OwnerDrawVisible")
	flags2 = {
		"CG_SHOW_IF_PLYR1": "0x00000001",
		"CG_SHOW_IF_PLYR2": "0x00000002",
		"CG_SHOW_IF_G_FIRED": "0x00000004",
		"CG_SHOW_IF_MG_FIRED": "0x00000008",
		"CG_SHOW_IF_SG_FIRED": "0x00000010",
		"CG_SHOW_IF_GL_FIRED": "0x00000020",
		"CG_SHOW_IF_RL_FIRED": "0x00000040",
		"CG_SHOW_IF_LG_FIRED": "0x00000080",
		"CG_SHOW_IF_RG_FIRED": "0x00000100",
		"CG_SHOW_IF_PG_FIRED": "0x00000200",
		"CG_SHOW_IF_BFG_FIRED": "0x00000400",
		"CG_SHOW_IF_CG_FIRED": "0x00000800",
		"CG_SHOW_IF_NG_FIRED": "0x00001000",
		"CG_SHOW_IF_PL_FIRED": "0x00002000",
		"CG_SHOW_IF_HMG_FIRED": "0x00004000",
		"CG_SHOW_IF_PLYR_IS_ON_RED_OR_SPEC": "0x00008000",
		"CG_SHOW_IF_PLYR_IS_ON_BLUE_OR_SPEC": "0x00010000",
		"CG_SHOW_IF_PLYR_IS_ON_RED_NO_SPEC": "0x00020000",
		"CG_SHOW_IF_PLYR_IS_ON_BLUE_NO_SPEC": "0x00040000",
		"CG_SHOW_IF_LOADOUT_ENABLED": "0x00080000",
		"CG_SHOW_IF_LOADOUT_DISABLED": "0x00100000",
		"CG_SHOW_IF_1ST_PLYR_FOLLOWED": "0x00200000",
		"CG_SHOW_IF_2ND_PLYR_FOLLOWED": "0x00400000",
	}

	for name, value in flags2.items():
		assert re.search(rf"#define\s+{name}\s+{value}\b", menudef_source)
		assert name in secondary_block

	for expected in (
		"int ownerDrawFlags2;",
		"qboolean (*ownerDrawVisible) (int flags, int flags2);",
	):
		assert expected in ui_shared_header

	for expected in (
		"item->window.ownerDrawFlags2 |= i;",
		"menu->window.ownerDrawFlags2 |= i;",
		"DC->ownerDrawVisible(item->window.ownerDrawFlags, item->window.ownerDrawFlags2)",
		"!DC->ownerDrawVisible(menu->window.ownerDrawFlags, menu->window.ownerDrawFlags2)) {",
	):
		assert expected in ui_shared_source

	for expected in (
		"if ( !cg.snap ) {",
		"if ( cg.snap->ps.pm_type == PM_SPECTATOR ) {",
		"score = CG_GetPlacementScore( slot );",
		"return ( score->client == cg.snap->ps.clientNum ) ? qtrue : qfalse;",
	):
		assert expected in slot_match_block

	for expected in (
		"score = CG_GetPlacementScore( slot );",
		"return ( score->client != cg.snap->ps.clientNum ) ? qtrue : qfalse;",
	):
		assert expected in slot_follow_block

	assert "return ( cg_loadout.integer != 0 ) ? qtrue : qfalse;" in loadout_block

	for expected in (
		"for ( i = 0; i < cg.numScores && i < 2; i++ ) {",
		"score = CG_GetPlacementScore( i );",
		"stats = CG_GetPlacementScoreStats( score );",
		"if ( weapon == WP_GAUNTLET ) {",
		"value = stats->weaponShots[weapon];",
		"value = stats->weaponDamage[weapon];",
	):
		assert expected in weapon_fired_block

	for expected in (
		"if ( ( flags2 & CG_SHOW_IF_PLYR1 ) && CG_PlacementSlotContainsPredictedPlayer( 0 ) ) {",
		"if ( ( flags2 & CG_SHOW_IF_PLYR2 ) && CG_PlacementSlotContainsPredictedPlayer( 1 ) ) {",
		"CG_PlacementWeaponFired( WP_GAUNTLET )",
		"CG_PlacementWeaponFired( WP_MACHINEGUN )",
		"CG_PlacementWeaponFired( WP_SHOTGUN )",
		"CG_PlacementWeaponFired( WP_GRENADE_LAUNCHER )",
		"CG_PlacementWeaponFired( WP_ROCKET_LAUNCHER )",
		"CG_PlacementWeaponFired( WP_LIGHTNING )",
		"CG_PlacementWeaponFired( WP_RAILGUN )",
		"CG_PlacementWeaponFired( WP_PLASMAGUN )",
		"CG_PlacementWeaponFired( WP_BFG )",
		"CG_PlacementWeaponFired( WP_CHAINGUN )",
		"CG_PlacementWeaponFired( WP_NAILGUN )",
		"CG_PlacementWeaponFired( WP_PROX_LAUNCHER )",
		"CG_PlacementWeaponFired( WP_HEAVY_MACHINEGUN )",
		"if ( ( flags2 & CG_SHOW_IF_LOADOUT_ENABLED ) && loadoutsEnabled ) {",
		"if ( ( flags2 & CG_SHOW_IF_LOADOUT_DISABLED ) && !loadoutsEnabled ) {",
		"pmType = PM_NORMAL;",
		"pmType = cg.snap->ps.pm_type;",
		"if ( ( flags2 & CG_SHOW_IF_PLYR_IS_ON_RED_OR_SPEC ) && ( playerTeam == TEAM_RED || pmType == PM_SPECTATOR ) ) {",
		"if ( ( flags2 & CG_SHOW_IF_PLYR_IS_ON_BLUE_OR_SPEC ) && ( playerTeam == TEAM_BLUE || pmType == PM_SPECTATOR ) ) {",
		"if ( ( flags2 & CG_SHOW_IF_PLYR_IS_ON_RED_NO_SPEC ) && playerTeam == TEAM_RED && pmType != PM_SPECTATOR ) {",
		"if ( ( flags2 & CG_SHOW_IF_PLYR_IS_ON_BLUE_NO_SPEC ) && playerTeam == TEAM_BLUE && pmType != PM_SPECTATOR ) {",
		"if ( ( flags2 & CG_SHOW_IF_1ST_PLYR_FOLLOWED ) && CG_PlacementSlotCanBeFollowed( 0 ) ) {",
		"if ( ( flags2 & CG_SHOW_IF_2ND_PLYR_FOLLOWED ) && CG_PlacementSlotCanBeFollowed( 1 ) ) {",
	):
		assert expected in secondary_block

	for stale in (
		"CG_SpectatorPlayerSlotActive",
		"CG_SpectatorSlotFollowed( 0 )",
		"CG_SpectatorSlotFollowed( 1 )",
		"PMF_FOLLOW",
		"CG_SHOW_IF_PLYR_IS_ON_RED )",
		"CG_SHOW_IF_PLYR_IS_ON_BLUE )",
	):
		assert stale not in secondary_block

	assert "if ( flags2 && CG_OwnerDrawSecondaryFlagVisible( flags2 ) ) {" in visible_block


def test_cgame_round_race_and_flag_ownerdraws_follow_retail_leaf_split() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	race_block = _block_from_marker(source, "static void CG_DrawRaceStatusAndTimes")
	round_timer_block = _block_from_marker(source, "static void CG_DrawRoundTimer")
	other_flag_block = _block_from_marker(source, "qboolean CG_OtherTeamHasFlag")
	your_flag_block = _block_from_marker(source, "qboolean CG_YourTeamHasFlag")
	blue_flag_block = _block_from_marker(source, "static qboolean CG_ShowBlueTeamHasRedFlag")
	red_flag_block = _block_from_marker(source, "static qboolean CG_ShowRedTeamHasBlueFlag")
	notification_block = _block_from_marker(source, "static qboolean CG_HudNotificationVisible")
	notice_block = _block_from_marker(source, "static qboolean CG_HasHudNoticeMessage")
	message_block = _block_from_marker(source, "static qboolean CG_HasHudPlayerMessage")
	weapon_fired_block = _block_from_marker(source, "static qboolean CG_PlacementWeaponFired")
	visible_block = "\n".join(
		(
			_block_from_marker(source, "static qboolean CG_OwnerDrawPrimaryFlagVisible"),
			_block_from_marker(source, "static qboolean CG_OwnerDrawSecondaryFlagVisible"),
			_block_from_marker(source, "qboolean CG_OwnerDrawVisible"),
		)
	)

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
		"cgs.gametype == GT_CTF || cgs.gametype == GT_1FCTF || cgs.gametype == GT_ATTACK_DEFEND",
		"team == TEAM_RED && cgs.flagStatus == FLAG_TAKEN_BLUE",
		"team == TEAM_BLUE && cgs.flagStatus == FLAG_TAKEN_RED",
		"team == TEAM_RED && cgs.redflag == FLAG_TAKEN",
		"team == TEAM_BLUE && cgs.blueflag == FLAG_TAKEN",
	):
		assert expected in other_flag_block

	for expected in (
		"cgs.gametype == GT_CTF || cgs.gametype == GT_1FCTF || cgs.gametype == GT_ATTACK_DEFEND",
		"team == TEAM_RED && cgs.flagStatus == FLAG_TAKEN_RED",
		"team == TEAM_BLUE && cgs.flagStatus == FLAG_TAKEN_BLUE",
		"team == TEAM_RED && cgs.blueflag == FLAG_TAKEN",
		"team == TEAM_BLUE && cgs.redflag == FLAG_TAKEN",
	):
		assert expected in your_flag_block

	for expected in (
		"cgs.gametype != GT_CTF && cgs.gametype != GT_1FCTF && cgs.gametype != GT_ATTACK_DEFEND",
		"if ( cgs.gametype == GT_1FCTF ) {",
		"return ( cgs.flagStatus == FLAG_TAKEN_BLUE ) ? qtrue : qfalse;",
		"return ( cgs.redflag == FLAG_TAKEN || cgs.flagStatus == FLAG_TAKEN_RED ) ? qtrue : qfalse;",
	):
		assert expected in blue_flag_block

	for expected in (
		"cgs.gametype != GT_CTF && cgs.gametype != GT_1FCTF && cgs.gametype != GT_ATTACK_DEFEND",
		"if ( cgs.gametype == GT_1FCTF ) {",
		"return ( cgs.flagStatus == FLAG_TAKEN_RED ) ? qtrue : qfalse;",
		"return ( cgs.blueflag == FLAG_TAKEN || cgs.flagStatus == FLAG_TAKEN_BLUE ) ? qtrue : qfalse;",
	):
		assert expected in red_flag_block

	for expected in (
		"if ( expireTime <= 0 || expireTime < cg.time ) {",
		"return ( cg.time & 0x200 ) ? qtrue : qfalse;",
	):
		assert expected in notification_block

	assert "return CG_HudNotificationVisible( cg.spectatorSlotTrackedTime[1] );" in notice_block
	assert "return CG_HudNotificationVisible( cg.spectatorSlotTrackedTime[0] );" in message_block

	for expected in (
		"for ( i = 0; i < cg.numScores && i < 2; i++ ) {",
		"score = CG_GetPlacementScore( i );",
		"stats = CG_GetPlacementScoreStats( score );",
		"if ( weapon == WP_GAUNTLET ) {",
		"value = stats->weaponShots[weapon];",
		"value = stats->weaponDamage[weapon];",
		"if ( value != 0 ) {",
	):
		assert expected in weapon_fired_block

	for expected in (
		"static qboolean CG_OwnerDrawPrimaryFlagVisible( int flags ) {",
		"if ( flags & ( CG_SHOW_BLUE_TEAM_HAS_REDFLAG | CG_SHOW_RED_TEAM_HAS_BLUEFLAG ) ) {",
		"if ( ( flags & CG_SHOW_BLUE_TEAM_HAS_REDFLAG ) && CG_ShowBlueTeamHasRedFlag() ) {",
		"if ( ( flags & CG_SHOW_RED_TEAM_HAS_BLUEFLAG ) && CG_ShowRedTeamHasBlueFlag() ) {",
		"if ( ( flags & CG_SHOW_DUEL ) && cgs.gametype == GT_TOURNAMENT ) {",
		"if ( ( flags & CG_SHOW_CLAN_ARENA ) && cgs.gametype == GT_CLAN_ARENA ) {",
		"if ( ( flags & CG_SHOW_CTF ) && cgs.gametype == GT_CTF ) {",
		"if ( ( flags & CG_SHOW_ONEFLAG ) && cgs.gametype == GT_1FCTF ) {",
		"if ( ( flags & CG_SHOW_OBELISK ) && cgs.gametype == GT_OBELISK ) {",
		"if ( ( flags & CG_SHOW_HARVESTER ) && cgs.gametype == GT_HARVESTER ) {",
		"if ( ( flags & CG_SHOW_DOMINATION ) && cgs.gametype == GT_DOMINATION ) {",
		"if ( ( flags & CG_SHOW_ANYNONTEAMGAME ) && cgs.gametype < GT_TEAM ) {",
		"if ( ( flags & CG_SHOW_ANYTEAMGAME ) && cgs.gametype >= GT_TEAM ) {",
		"if ( ( flags & CG_SHOW_HEALTHCRITICAL ) && cg.snap->ps.stats[STAT_HEALTH] < 25 ) {",
		"if ( ( flags & CG_SHOW_IF_NOT_WARMUP ) && cg.warmup >= 0 ) {",
		"if ( ( flags & CG_SHOW_IF_PLAYER_HAS_FLAG ) &&",
		"if ( ( flags & CG_SHOW_IF_WARMUP ) && cg.warmup < 0 ) {",
		"if ( ( flags & CG_SHOW_IF_CHAT_VISIBLE ) && ( cg.chatHistoryVisible || cg.scoreBoardShowing ) ) {",
		"if ( ( flags & CG_SHOW_INTERMISSION ) &&",
		"if ( ( flags & CG_SHOW_NOTINTERMISSION ) &&",
		"static qboolean CG_OwnerDrawSecondaryFlagVisible( int flags2 ) {",
		"if ( ( flags2 & CG_SHOW_IF_PLYR1 ) && CG_PlacementSlotContainsPredictedPlayer( 0 ) ) {",
		"if ( ( flags2 & CG_SHOW_IF_PLYR2 ) && CG_PlacementSlotContainsPredictedPlayer( 1 ) ) {",
		"if ( ( flags2 & CG_SHOW_IF_LOADOUT_ENABLED ) && loadoutsEnabled ) {",
		"if ( ( flags2 & CG_SHOW_IF_PLYR_IS_ON_RED_OR_SPEC ) && ( playerTeam == TEAM_RED || pmType == PM_SPECTATOR ) ) {",
		"if ( ( flags2 & CG_SHOW_IF_PLYR_IS_ON_BLUE_OR_SPEC ) && ( playerTeam == TEAM_BLUE || pmType == PM_SPECTATOR ) ) {",
		"if ( ( flags2 & CG_SHOW_IF_PLYR_IS_ON_RED_NO_SPEC ) && playerTeam == TEAM_RED && pmType != PM_SPECTATOR ) {",
		"if ( ( flags2 & CG_SHOW_IF_PLYR_IS_ON_BLUE_NO_SPEC ) && playerTeam == TEAM_BLUE && pmType != PM_SPECTATOR ) {",
		"if ( ( flags2 & CG_SHOW_IF_1ST_PLYR_FOLLOWED ) && CG_PlacementSlotCanBeFollowed( 0 ) ) {",
		"if ( ( flags2 & CG_SHOW_IF_2ND_PLYR_FOLLOWED ) && CG_PlacementSlotCanBeFollowed( 1 ) ) {",
		"CG_PlacementWeaponFired( WP_GAUNTLET )",
		"CG_PlacementWeaponFired( WP_MACHINEGUN )",
		"CG_PlacementWeaponFired( WP_HEAVY_MACHINEGUN )",
		"if ( flags && CG_OwnerDrawPrimaryFlagVisible( flags ) ) {",
		"if ( flags2 && CG_OwnerDrawSecondaryFlagVisible( flags2 ) ) {",
	):
		assert expected in visible_block

	assert "CG_LocalPlayerHasWeapon" not in source

	for cgame_collision in (
		"UI_SHOW_ANYTEAMGAME",
		"UI_SHOW_IF_LOADOUT_ENABLED",
		"UI_SHOW_IF_WARMUP",
		"UI_SHOW_IF_NOT_WARMUP",
		"UI_SHOW_IF_NOT_INTERMISSION",
	):
		assert cgame_collision not in visible_block

	for expected in (
		"case CG_RACE_STATUS:",
		"case CG_RACE_TIMES:",
		"CG_DrawRaceStatusAndTimes( &rect, scale, color, textStyle, ownerDraw );",
	):
		assert expected in source

	for source_only_flag in (
		"CG_SHOW_IF_1ST_PLYR_TRACKED",
		"CG_SHOW_IF_2ND_PLYR_TRACKED",
	):
		assert source_only_flag not in visible_block
		assert source_only_flag not in UI_SHARED_H.read_text(encoding="utf-8")


def test_cgame_loaded_browser_menu_visibility_flags_are_backed_by_cgame() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	visible_block = "\n".join(
		(
			_block_from_marker(source, "static qboolean CG_OwnerDrawPrimaryFlagVisible"),
			_block_from_marker(source, "static qboolean CG_OwnerDrawSecondaryFlagVisible"),
			_block_from_marker(source, "qboolean CG_OwnerDrawVisible"),
		)
	)
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

	flags = {flag for flag in flags if not flag.startswith("UI_SHOW_")}
	missing = sorted(flag for flag in flags if flag not in visible_block)
	assert not missing, f"loaded cgame browser menu flags lack CG_OwnerDrawVisible coverage: {missing}"

	assert "static void CG_DrawRaceStatus(" not in source
	assert "static void CG_DrawRaceTimes(" not in source


def test_cgame_ownerdraw_dispatch_covers_committed_retail_switch_cases() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	constants = _menudef_ownerdraw_constants()
	names_by_value = {value: name for name, value in constants.items()}
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	source_case_names = set(re.findall(r"case\s+([A-Z0-9_]+)\s*:", ownerdraw_block))
	covered_values = {
		constants[name]
		for name in source_case_names
		if name in constants
	}

	for first, last in (
		("CG_1ST_PLYR_READY", "CG_1ST_PLYR_TIER"),
		("CG_2ND_PLYR_READY", "CG_2ND_PLYR_TIER"),
	):
		covered_values.update(range(constants[first], constants[last] + 1))

	for award_owner_draw in (
		"CG_MOST_DAMAGEDEALT_PLYR",
		"CG_MOST_ACCURATE_PLYR",
		"CG_MOST_VALUABLE_OFFENSIVE_PLYR",
		"CG_MOST_VALUABLE_DEFENSIVE_PLYR",
		"CG_MOST_VALUABLE_PLYR",
		"CG_BEST_ITEMCONTROL_PLYR",
	):
		covered_values.add(constants[award_owner_draw])

	missing_named_cases = [
		names_by_value[value]
		for value in sorted(_retail_cg_ownerdraw_case_values())
		if value in names_by_value and value not in covered_values
	]

	assert not missing_named_cases


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


def test_cgame_legacy_ui_shared_ownerdraws_match_retail_noop_slots() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	ui_shared_h = UI_SHARED_H.read_text(encoding="utf-8")
	menudef_h = MENUDEF_H.read_text(encoding="utf-8")
	value_block = _block_from_marker(source, "float CG_GetValue")
	competitive_refresh_block = _block_from_marker(source, "static qboolean CG_IsCompetitiveScoreOwnerDraw")
	ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
	start = ownerdraw_block.index("case CG_AREA_SYSTEMCHAT:")
	end = ownerdraw_block.index("case CG_AREA_NEW_CHAT:", start)
	legacy_chat_cases = ownerdraw_block[start:end]
	start = ownerdraw_block.index("case CG_1STPLACE_PLYR_MODEL_ACTIVE:")
	end = ownerdraw_block.index("case CG_2NDPLACE:", start)
	active_model_case = ownerdraw_block[start:end]
	start = ownerdraw_block.index("case CG_PLAYERMODEL:")
	end = ownerdraw_block.index("case CG_PLAYER_ITEM:", start)
	player_model_case = ownerdraw_block[start:end]
	start = ownerdraw_block.index("case CG_TEAMINFO:")
	end = ownerdraw_block.index("case CG_1STPLACE:", start)
	teaminfo_case = ownerdraw_block[start:end]
	start = ownerdraw_block.index("case CG_SELECTEDPLAYER_HEAD:")
	end = ownerdraw_block.index("case CG_PLAYER_HEAD:", start)
	selectedplayer_cases = ownerdraw_block[start:end]
	start = ownerdraw_block.index("case CG_BLUE_FLAGHEAD:")
	end = ownerdraw_block.index("case CG_HARVESTER_SKULLS:", start)
	legacy_flag_cases = ownerdraw_block[start:end]
	start = ownerdraw_block.index("case CG_SCOREBOX_FOLLOW_BACKGROUND:")
	end = ownerdraw_block.index("case CG_HEALTH_COLORIZED:", start)
	scorebox_spectator_cases = ownerdraw_block[start:end]

	assert "#define\tCG_PLAYERMODEL\t\t\t\t\t\t37" in menudef_h
	assert "#define\tCG_1STPLACE_PLYR_MODEL_ACTIVE\t\t102" in menudef_h
	assert "CG_1STPLACE_PLYR_MODEL ||" in competitive_refresh_block
	assert "CG_1STPLACE_PLYR_MODEL_ACTIVE" not in competitive_refresh_block

	for expected in (
		"#define CG_SELECTEDPLAYER_HEAD 344",
		"#define CG_SELECTEDPLAYER_HEALTH 351",
		"#define CG_VOICE_HEAD 352",
		"#define CG_SCOREBOX_FOLLOW_BACKGROUND 356",
		"#define CG_TEAMINFO 358",
		"#define CG_PLAYER_STATUS 364",
		"#define CG_AREA_SYSTEMCHAT 365",
		"#define CG_AREA_CHAT 367",
	):
		assert expected in ui_shared_h

	for stale in (
		"case CG_SELECTEDPLAYER_ARMOR:",
		"case CG_SELECTEDPLAYER_HEALTH:",
	):
		assert stale not in value_block

	assert "return;" in selectedplayer_cases
	for stale in (
		"CG_DrawSelectedPlayerHead",
		"CG_DrawSelectedPlayerName",
		"CG_DrawSelectedPlayerStatus",
		"CG_DrawSelectedPlayerArmor",
		"CG_DrawSelectedPlayerHealth",
		"CG_DrawSelectedPlayerLocation",
		"CG_DrawSelectedPlayerWeapon",
		"CG_DrawSelectedPlayerPowerup",
	):
		assert stale not in selectedplayer_cases

	assert "return;" in active_model_case
	assert "CG_DrawFirstPlaceModel" not in active_model_case
	assert "CG_DrawPlayerModel( &rect );" in player_model_case

	for expected in (
		"case CG_ROUND_BACKGROUND:",
		"case CG_OVERTIME_BACKGROUND:",
		"case CG_BLUE_FLAGHEAD:",
		"case CG_BLUE_FLAGNAME:",
		"case CG_RED_FLAGHEAD:",
		"case CG_RED_FLAGNAME:",
		"case CG_PLAYER_LOCATION:",
		"case CG_PLAYER_STATUS:",
		"case CG_AREA_SYSTEMCHAT:",
		"case CG_AREA_TEAMCHAT:",
		"case CG_AREA_CHAT:",
		"case CG_SCOREBOX_FOLLOW_BACKGROUND:",
		"case CG_SCOREBOX_SPEC_BACKGROUND:",
		"case CG_SPEC_FOLLOW_PRIMARY:",
		"case CG_SPEC_FOLLOW_SECONDARY:",
		"case CG_SPEC_COMPARE_PRIMARY:",
		"case CG_SPEC_COMPARE_SECONDARY:",
	):
		assert expected in ownerdraw_block

	for stale in (
		"CG_DrawAreaSystemChat",
		"CG_DrawAreaTeamChat",
		"CG_DrawAreaChat",
	):
		assert stale not in legacy_chat_cases

	for stale in (
		"CG_DrawBlueFlagHead",
		"CG_DrawBlueFlagName",
		"CG_DrawRedFlagHead",
		"CG_DrawRedFlagName",
		"CG_DrawPlayerLocation",
		"CG_DrawPlayerStatus",
	):
		assert stale not in legacy_flag_cases

	for stale in (
		"CG_DrawScoreboxFollowBackground",
		"CG_DrawScoreboxSpecBackground",
		"CG_DrawSpectatorFollowIndicator",
		"CG_DrawSpectatorComparison",
	):
		assert stale not in scorebox_spectator_cases

	assert "return;" in teaminfo_case
	assert "CG_DrawNewTeamInfo" not in teaminfo_case


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
		'Com_sprintf( buffer, bufferSize, "%i%%", stats->weaponAccuracy[weapon] );',
	):
		assert expected in build_block
