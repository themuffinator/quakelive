"""Guard retail-backed cgame HUD seams against source drift."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_DRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
HUD_MENU = REPO_ROOT / "src" / "ui" / "hud.menu"
UI_SHARED = REPO_ROOT / "src" / "code" / "ui" / "ui_shared.c"
Q_SHARED = REPO_ROOT / "src" / "code" / "game" / "q_shared.h"
MSG = REPO_ROOT / "src" / "code" / "qcommon" / "msg.c"
G_ACTIVE = REPO_ROOT / "src" / "code" / "game" / "g_active.c"


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


def _menu_item_keys(source: str) -> set[str]:
	text = re.sub(r"//.*", "", source)
	lines = [line.strip() for line in text.splitlines() if line.strip()]
	keys: set[str] = set()
	in_item = False

	for line in lines:
		if line.startswith("itemDef"):
			in_item = True
			continue
		if in_item and line == "}":
			in_item = False
			continue
		if not in_item:
			continue

		token = line.split()[0]
		if token not in {"{", "}"}:
			keys.add(token.lower())

	return keys


def _menu_ownerdraw_tokens(source: str) -> set[str]:
	text = re.sub(r"//.*", "", source)
	return set(re.findall(r"\bownerdraw\s+([A-Z0-9_]+)", text))


def _menu_ownerdrawflag_tokens(source: str) -> set[str]:
	text = re.sub(r"//.*", "", source)
	return set(re.findall(r"\bownerdrawflag\s+([A-Z0-9_]+)", text))


def test_teammate_poi_overlay_uses_retail_projection_and_status_markers() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	draw_block = _block_from_marker(source, "static void CG_DrawTeammatePOIs")
	label_block = _block_from_marker(source, "static void CG_BuildTeammatePOILabel")
	trim_block = _block_from_marker(source, "static void CG_TrimTeammatePOILabelToWidth")
	icon_block = _block_from_marker(source, "static void CG_DrawTeammatePOIIcons")

	assert "static qboolean CG_ShouldDrawTeammatePOIs( void )" in source
	assert "cg_teammateNames.integer == 0 && cg_teammatePOIs.integer == 0" in source
	assert "cg_teammatePOIsMinWidth.value * SMALLCHAR_WIDTH" in draw_block
	assert "cg_teammatePOIsMaxWidth.value * SMALLCHAR_WIDTH" in label_block
	assert '"..%s"' in trim_block
	assert "trap_R_inPVS( cg.refdef.vieworg, poiOrigin )" in draw_block
	assert "CG_WorldCoordToScreenCoord( poiOrigin, &screenX, &screenY )" in draw_block
	assert "CG_ConfigString( CS_LOCATIONS + ci->location )" in source
	assert "CG_GetColorForHealth( ci->health, ci->armor, healthColor )" in draw_block
	assert "CG_StatusHandle( ci->teamTask )" in icon_block
	assert "BG_FindItemForPowerup( powerup )" in source
	assert "PW_REDFLAG" in icon_block
	assert "PW_BLUEFLAG" in icon_block
	assert "PW_NEUTRALFLAG" in icon_block
	assert "PW_QUAD" in icon_block
	assert "PW_BATTLESUIT" in icon_block
	assert "PW_REGEN" in icon_block
	assert "PW_HASTE" in icon_block
	assert "PW_INVIS" in icon_block


def test_draw2d_calls_teammate_poi_overlay_for_team_games() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	draw2d_block = _block_from_marker(source, "static void CG_Draw2D( void )")

	assert "if ( cgs.gametype >= GT_TEAM ) {" in draw2d_block
	assert "CG_DrawTeammatePOIs();" in draw2d_block


def test_crosshair_name_overlay_restores_retail_team_health_and_armor_readout() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	name_block = _block_from_marker(source, "static void CG_DrawCrosshairNames")
	vitals_block = _block_from_marker(source, "static void CG_DrawCrosshairTeamVitals")
	color_block = _block_from_marker(source, "static void CG_GetCrosshairTeamVitalColor")

	assert "static qboolean CG_ShouldDrawCrosshairTeamVitals( const clientInfo_t *ci )" in source
	assert "cg_drawCrosshairTeamHealth.integer <= 0 || cgs.gametype < GT_TEAM" in source
	assert "nameScale = 0.26f;" in name_block
	assert "CG_DrawCrosshairTeamVitals( ci, color );" in name_block
	assert 'Com_sprintf( healthText, sizeof( healthText ), "%i ", ci->health );' in vitals_block
	assert 'Com_sprintf( armorText, sizeof( armorText ), " %i", ci->armor );' in vitals_block
	assert "textY = 198.0f + textScale * 16.0f;" in vitals_block
	assert "CG_Text_Paint( 320.0f - healthWidth, textY, textScale, healthColor, healthText, 0, 0, ITEM_TEXTSTYLE_SHADOWED );" in vitals_block
	assert 'CG_Text_Paint( 320.0f, textY, textScale, slashColor, "/", 0, 0, ITEM_TEXTSTYLE_SHADOWED );' in vitals_block
	assert "CG_Text_Paint( 325.0f, textY, textScale, armorColor, armorText, 0, 0, ITEM_TEXTSTYLE_SHADOWED );" in vitals_block
	assert "cg_drawCrosshairTeamHealth.integer == 2" in vitals_block
	assert "cg.snap->ps.stats[STAT_MAX_HEALTH]" in vitals_block
	assert "highComponent = (float)value / (float)( maxValue + maxValue );" in color_block


def test_crosshair_team_health_default_matches_retail_mode_cvar() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")

	assert '{ &cg_drawCrosshairTeamHealth, "cg_drawCrosshairTeamHealth", "2", CVAR_ARCHIVE },' in source
	assert '{ &cg_drawCrosshairTeamHealthSize, "cg_drawCrosshairTeamHealthSize", "0.12", CVAR_ARCHIVE },' in source


def test_crosshair_draw_uses_retail_vertical_scaler_and_numeric_shader_names() -> None:
	draw_source = CG_DRAW.read_text(encoding="utf-8")
	main_source = CG_MAIN.read_text(encoding="utf-8")
	local_header = (REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h").read_text(encoding="utf-8")
	draw_block = _block_from_marker(draw_source, "static void CG_DrawCrosshair(void)")
	register_block = _block_from_marker(main_source, "static void CG_RegisterGraphics( void )")

	assert "#define\tNUM_CROSSHAIRS\t\t30" in local_header
	assert "x *= cgs.screenYScale;" in draw_block
	assert "y *= cgs.screenYScale;" in draw_block
	assert "w *= cgs.screenYScale;" in draw_block
	assert "h *= cgs.screenYScale;" in draw_block
	assert "CG_AdjustFrom640( &x, &y, &w, &h );" not in draw_block
	assert "if ( ca <= 0 || ( ca % NUM_CROSSHAIRS ) == 0 ) {" in draw_block
	assert "0.5 * (cg.refdef.width - w)" in draw_block
	assert "0.5 * (cg.refdef.height - h)" in draw_block

	assert "for ( i = 1 ; i < NUM_CROSSHAIRS ; i++ ) {" in register_block
	assert 'trap_R_RegisterShader( va( "gfx/2d/crosshair%d", i ) );' in register_block
	assert 'crosshair%c' not in register_block


def test_team_info_overlay_restores_fixed_retail_row_renderer() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	draw_block = _block_from_marker(source, "static void CG_DrawTeamInfo( void )")
	row_block = _block_from_marker(source, "static void CG_DrawTeamInfoRow")
	bar_block = _block_from_marker(source, "static void CG_DrawTeamInfoBar")

	assert "static qboolean CG_ShouldDrawTeamInfo( void )" in source
	assert "cg_drawTeamOverlay.integer <= 0 || cgs.gametype < GT_TEAM" in source
	assert "numSortedTeamPlayers > 0" in draw_block
	assert "cg.scores[i]" in draw_block
	assert "teamY[score->team] += 22.0f;" in draw_block
	assert "panelLeft = ( team == TEAM_RED ) ? 5.0f : 320.0f;" in row_block
	assert "panelRight = ( team == TEAM_RED ) ? 315.0f : 635.0f;" in row_block
	assert "CG_TeammatePOIPowerupIcon( powerups[i] )" in source
	assert "CG_StatusHandle( ci->teamTask )" in row_block
	assert "CG_GetColorForHealth( ci->health, ci->armor, healthColor );" in row_block
	assert "CG_GetTeamInfoArmorColor( ci->armor, armorColor );" in row_block
	assert "CG_TrimTeammatePOILabelToWidth( ci->name" in row_block
	assert "CG_TrimTeammatePOILabelToWidth( CG_TeamInfoLocation( ci )" in row_block
	assert "CG_DrawTeamInfoBar( barX, y + 3.0f, 64.0f, 6.0f, CG_TeamInfoBarFraction( ci->health ), cgs.media.healthBar200, healthColor );" in row_block
	assert "CG_DrawTeamInfoBar( barX, y + 11.0f, 64.0f, 6.0f, CG_TeamInfoBarFraction( ci->armor ), cgs.media.armorBar200, armorColor );" in row_block
	assert "trap_R_DrawStretchPic" in bar_block


def test_draw2d_calls_fixed_team_info_overlay_after_follow_and_warmup() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	draw2d_block = _block_from_marker(source, "static void CG_Draw2D( void )")

	assert "if ( !CG_DrawFollow() ) {" in draw2d_block
	assert "CG_DrawWarmup();" in draw2d_block
	assert "CG_DrawTeamInfo();" in draw2d_block


def test_lower_right_hud_restores_powerup_popup_and_team_overlay_branch() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	powerups_block = _block_from_marker(source, "static float CG_DrawPowerups")
	lower_right_block = _block_from_marker(source, "static void CG_DrawLowerRight")
	draw2d_block = _block_from_marker(source, "static void CG_Draw2D( void )")

	assert "static int CG_CountActiveTimedPowerups( const playerState_t *ps )" in source
	assert "cg.powerupActive <= PW_NONE || cg.powerupActive >= PW_NUM_POWERUPS" in powerups_block
	assert "CG_FadeColor( cg.powerupTime, 3000 )" in powerups_block
	assert 'Com_sprintf( powerupTimeText, sizeof( powerupTimeText ), "%i:%i%i", mins, tens, seconds );' in powerups_block
	assert "BG_FindItemForPowerup( cg.powerupActive )" in powerups_block
	assert "CG_TeammatePOIPowerupIcon( cg.powerupActive )" in powerups_block
	assert 'Com_sprintf( stackText, sizeof( stackText ), "x%i", activeCount );' in powerups_block
	assert "y = 408.0f;" in lower_right_block
	assert "CG_DrawTeamOverlay( y, qtrue, qfalse );" in lower_right_block
	assert "CG_DrawPowerups( y );" in lower_right_block
	assert "if ( !menuHudActive ) {" in draw2d_block
	assert "CG_DrawLowerRight();" in draw2d_block


def test_classic_speedometer_restores_retail_history_ring_and_draw_order() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	speedometer_block = _block_from_marker(source, "static void CG_DrawSpeedometer( void )")
	record_block = _block_from_marker(source, "static void CG_RecordSpeedometerSample( void )")
	draw2d_block = _block_from_marker(source, "static void CG_Draw2D( void )")

	assert "#define CG_SPEEDOMETER_HISTORY_SAMPLES\t128" in source
	assert "#define CG_SPEEDOMETER_RANGE\t\t\t960.0f" in source
	assert "static float CG_SampleLegacySpeedometer( void )" in source
	assert "cg_speedometerHistoryHead = ( cg_speedometerHistoryHead + 1 ) & ( CG_SPEEDOMETER_HISTORY_SAMPLES - 1 );" in record_block
	assert "cg_speedometerHistory[cg_speedometerHistoryHead] = CG_SampleLegacySpeedometer();" in record_block
	assert "mode = cg_speedometer.integer;" in speedometer_block
	assert "graphX = 592.0f;" in speedometer_block
	assert "graphY = 384.0f;" in speedometer_block
	assert "graphWidth = 128.0f;" in speedometer_block
	assert "graphHeight = 32.0f;" in speedometer_block
	assert "barScale = ( graphHeight - 5.0f ) / CG_SPEEDOMETER_RANGE;" in speedometer_block
	assert "if ( mode < 3 ) {" in speedometer_block
	assert 'Com_sprintf( speedText, sizeof( speedText ), "%i", (int)currentSpeed );' in speedometer_block
	assert "CG_DrawSpeedometer();" in draw2d_block


def test_classic_input_cmd_overlay_restores_retail_follow_and_arrow_icon_path() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	shared = Q_SHARED.read_text(encoding="utf-8")
	msg = MSG.read_text(encoding="utf-8")
	active = G_ACTIVE.read_text(encoding="utf-8")
	input_block = _block_from_marker(source, "static void CG_DrawInputCmds( void )")
	register_block = _block_from_marker(source, "static void CG_RegisterInputCmdShaders( void )")
	draw2d_block = _block_from_marker(source, "static void CG_Draw2D( void )")

	assert 'trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_up" )' in register_block
	assert 'trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_down" )' in register_block
	assert 'trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_right" )' in register_block
	assert 'trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_left" )' in register_block
	assert "cg_drawInputCmds.integer == 0" in input_block
	assert "cg.snap->ps.pm_type == PM_INTERMISSION" in input_block
	assert "cg.snap->ps.pm_type == PM_SPECTATOR && !( cg.snap->ps.pm_flags & PMF_FOLLOW )" in input_block
	assert "cg_drawInputCmds.integer == 2 && !( cg.snap->ps.pm_flags & PMF_FOLLOW )" in input_block
	assert "if ( ( cg.snap->ps.pm_flags & PMF_FOLLOW ) || cg.demoPlayback ) {" in input_block
	assert "forwardMove = cg.snap->ps.forwardmove;" in input_block
	assert "rightMove = cg.snap->ps.rightmove;" in input_block
	assert "upMove = cg.snap->ps.upmove;" in input_block
	assert "cmdNum = trap_GetCurrentCmdNumber();" in input_block
	assert "trap_GetUserCmd( cmdNum, &cmd )" in input_block
	assert "x = cg_drawInputCmdsX.value;" in input_block
	assert "y = cg_drawInputCmdsY.value;" in input_block
	assert "size = cg_drawInputCmdsSize.value;" in input_block
	assert "CG_DrawPic( x - 8.0f, y - size - 16.0f, 16.0f, 16.0f, upShader );" in input_block
	assert "CG_DrawPic( x + size, y - 8.0f, 16.0f, 16.0f, rightShader );" in input_block
	assert "CG_DrawPic( x - size - 16.0f, y - 8.0f, 16.0f, 16.0f, leftShader );" in input_block
	assert "CG_DrawPic( x + size + 16.0f, y + size, 16.0f, 16.0f, downShader );" in input_block
	assert "int\t\t\tforwardmove;" in shared
	assert "int\t\t\trightmove;" in shared
	assert "int\t\t\tupmove;" in shared
	assert "{ PSF(forwardmove), 8 }" in msg
	assert "{ PSF(rightmove), 8 }" in msg
	assert "{ PSF(upmove), 8 }" in msg
	assert "client->ps.forwardmove = ucmd->forwardmove;" in active
	assert "client->ps.rightmove = ucmd->rightmove;" in active
	assert "client->ps.upmove = ucmd->upmove;" in active
	assert "CG_DrawInputCmds();" in draw2d_block
	assert draw2d_block.index( "CG_DrawInputCmds();" ) < draw2d_block.index( "CG_DrawSpeedometer();" )
	assert draw2d_block.index( "CG_DrawSpeedometer();" ) < draw2d_block.index( "CG_DrawLowerRight();" )


def test_default_hud_item_keywords_are_backed_by_item_parsers() -> None:
	hud_source = HUD_MENU.read_text(encoding="utf-8")
	ui_shared_source = UI_SHARED.read_text(encoding="utf-8")
	hud_keys = _menu_item_keys(hud_source)
	parser_names = {
		name.lower()
		for name in re.findall(r"qboolean\s+ItemParse_([A-Za-z0-9_]+)\s*\(", ui_shared_source)
	}

	missing = sorted(hud_keys - parser_names)
	assert not missing, f"hud.menu item keys lack ItemParse_ coverage: {missing}"


def test_default_hud_ownerdraws_and_visibility_flags_are_backed_by_cgame() -> None:
	hud_source = HUD_MENU.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	visible_block = _block_from_marker(newdraw_source, "qboolean CG_OwnerDrawVisible")

	missing_ownerdraws = sorted(
		name for name in _menu_ownerdraw_tokens(hud_source) if f"case {name}:" not in newdraw_source
	)
	missing_flags = sorted(
		name for name in _menu_ownerdrawflag_tokens(hud_source) if name not in visible_block
	)

	assert not missing_ownerdraws, f"hud.menu ownerdraws lack CG_OwnerDraw cases: {missing_ownerdraws}"
	assert not missing_flags, f"hud.menu ownerdraw flags lack CG_OwnerDrawVisible coverage: {missing_flags}"


def test_default_hud_score_widgets_refresh_the_competitive_score_cache() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	refresh_block = _block_from_marker(source, "static qboolean CG_IsCompetitiveScoreOwnerDraw")

	for ownerdraw in (
		"CG_1ST_PLACE_SCORE",
		"CG_2ND_PLACE_SCORE",
		"CG_TEAM_PLYR_COUNT",
		"CG_ENEMY_PLYR_COUNT",
	):
		assert ownerdraw in refresh_block
