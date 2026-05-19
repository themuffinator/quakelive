"""Guard retail-backed cgame HUD seams against source drift."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_DRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_SCREEN = REPO_ROOT / "src" / "code" / "cgame" / "cg_screen.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
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
	main_source = CG_MAIN.read_text(encoding="utf-8")
	local_header = CG_LOCAL.read_text(encoding="utf-8")
	draw_block = _block_from_marker(source, "static void CG_DrawTeammatePOIs")
	register_block = _block_from_marker(main_source, "static void CG_RegisterGraphics( void )")
	poi_register_gate_block = _block_from_marker(main_source, "static qboolean CG_ShouldRegisterPOIPowerupShaders")
	flag_status_gate_block = _block_from_marker(main_source, "static qboolean CG_ShouldRegisterFlagStatusShaders")
	label_block = _block_from_marker(source, "static void CG_BuildTeammatePOILabel")
	trim_block = _block_from_marker(source, "static void CG_TrimTeammatePOILabelToWidth")
	icon_block = _block_from_marker(source, "static void CG_DrawTeammatePOIIcons")
	item_icon_block = _block_from_marker(source, "static qhandle_t CG_ItemBackedPowerupIcon")
	powerup_icon_block = _block_from_marker(source, "static qhandle_t CG_TeammatePOIPowerupIcon")
	bar_block = _block_from_marker(source, "static void CG_DrawTeammatePOIBar")

	assert "static qboolean CG_ShouldDrawTeammatePOIs( void )" in source
	assert "cg_teammateNames.integer == 0 && cg_teammatePOIs.integer == 0" in source
	assert "qhandle_t\thealthSegmentShader;" in local_header
	assert 'cgs.media.healthSegmentShader = trap_R_RegisterShader( "gfx/2d/health_segment.tga" );' in register_block
	assert "if ( CG_ShouldRegisterPOIPowerupShaders() )" in register_block
	assert "case GT_RACE:" in poi_register_gate_block
	assert "case GT_CLAN_ARENA:" in poi_register_gate_block
	assert "case GT_DOMINATION:" in poi_register_gate_block
	assert "case GT_RED_ROVER:" in poi_register_gate_block
	assert "return qfalse;" in poi_register_gate_block
	assert 'cgs.media.poiPowerupQuadShader = trap_R_RegisterShader( "gfx/2d/powerup/quad" );' in register_block
	assert 'cgs.media.poiPowerupBattleSuitShader = trap_R_RegisterShader( "gfx/2d/powerup/bs" );' in register_block
	assert 'cgs.media.poiPowerupHasteShader = trap_R_RegisterShader( "gfx/2d/powerup/haste" );' in register_block
	assert 'cgs.media.poiPowerupInvisShader = trap_R_RegisterShader( "gfx/2d/powerup/invis" );' in register_block
	assert 'cgs.media.poiPowerupRegenShader = trap_R_RegisterShader( "gfx/2d/powerup/regen" );' in register_block
	assert "if ( CG_ShouldRegisterFlagStatusShaders() )" in register_block
	assert "case GT_RACE:" in flag_status_gate_block
	assert "case GT_CTF:" in flag_status_gate_block
	assert "case GT_1FCTF:" in flag_status_gate_block
	assert "case GT_OBELISK:" in flag_status_gate_block
	assert "case GT_DOMINATION:" in flag_status_gate_block
	assert "case GT_ATTACK_DEFEND:" in flag_status_gate_block
	assert 'cgs.media.poiFlagDroppedNeutralShader = trap_R_RegisterShader( "gfx/2d/flag_status/flag_dropped" );' in register_block
	assert 'cgs.media.poiFlagDroppedRedShader = trap_R_RegisterShader( "gfx/2d/flag_status/red_flag_dropped" );' in register_block
	assert 'cgs.media.poiFlagDroppedBlueShader = trap_R_RegisterShader( "gfx/2d/flag_status/blue_flag_dropped" );' in register_block
	assert "if ( cgs.gametype == GT_FFA || cg_buildScript.integer )" in register_block
	assert 'cgs.media.poiQuadHogShader = trap_R_RegisterShader( "gfx/2d/quad_hog/quadhog" );' in register_block
	assert "cg_teammatePOIsMinWidth.value * SMALLCHAR_WIDTH" in draw_block
	assert "cg_teammatePOIsMaxWidth.value * SMALLCHAR_WIDTH" in label_block
	assert '"..%s"' in trim_block
	assert "trap_R_inPVS( cg.refdef.vieworg, poiOrigin )" in draw_block
	assert "CG_WorldCoordToScreenCoord( poiOrigin, &screenX, &screenY )" in draw_block
	assert "CG_ConfigString( CS_LOCATIONS + ci->location )" in source
	assert "CG_GetColorForHealth( ci->health, ci->armor, healthColor )" in draw_block
	assert 'trap_R_RegisterShader( "gfx/2d/health_segment.tga" )' in bar_block
	assert "cgs.media.healthSegmentShader" in draw_block
	assert "CG_StatusHandle( ci->teamTask )" in icon_block
	assert "return cgs.media.poiPowerupQuadShader;" in powerup_icon_block
	assert "return cgs.media.poiPowerupBattleSuitShader;" in powerup_icon_block
	assert "return cgs.media.poiPowerupHasteShader;" in powerup_icon_block
	assert "return cgs.media.poiPowerupInvisShader;" in powerup_icon_block
	assert "return cgs.media.poiPowerupRegenShader;" in powerup_icon_block
	assert "return CG_ItemBackedPowerupIcon( powerup );" in powerup_icon_block
	assert "BG_FindItemForPowerup( powerup )" in item_icon_block
	assert "return cg_items[ITEM_INDEX( item )].icon;" in item_icon_block
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
	local_header = CG_LOCAL.read_text(encoding="utf-8")
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


def test_screen_damage_and_vignette_use_registered_retail_media_handles() -> None:
	draw_source = CG_DRAW.read_text(encoding="utf-8")
	main_source = CG_MAIN.read_text(encoding="utf-8")
	screen_source = CG_SCREEN.read_text(encoding="utf-8")
	local_header = CG_LOCAL.read_text(encoding="utf-8")
	register_block = _block_from_marker(main_source, "static void CG_RegisterGraphics( void )")
	vignette_block = _block_from_marker(draw_source, "static void CG_DrawScreenVignette")
	damage_shader_block = _block_from_marker(screen_source, "static qhandle_t CG_GetScreenDamageBlendShader")

	assert "qhandle_t\tviewDamageBlendShader;" in local_header
	assert "qhandle_t\tvignetteShader;" in local_header
	assert '{ &cg_vignette, "cg_vignette", "0", CVAR_ARCHIVE },' in main_source
	assert 'cgs.media.viewDamageBlendShader = trap_R_RegisterShader( "viewDamageBlend" );' in register_block
	assert 'cgs.media.vignetteShader = trap_R_RegisterShader( "gfx/misc/vignette" );' in register_block
	assert "cgs.media.viewDamageBlendShader = trap_R_RegisterShader( \"viewDamageBlend\" );" in damage_shader_block
	assert "return cgs.media.viewDamageBlendShader;" in damage_shader_block
	assert "static qhandle_t\tcg_screenDamageBlendShader;" not in screen_source
	assert "vec4_t vignetteColor = { 1.0f, 1.0f, 1.0f, 0.35f };" in vignette_block
	assert "cgs.media.vignetteShader = trap_R_RegisterShader( \"gfx/misc/vignette\" );" in vignette_block
	assert "trap_R_SetColor( vignetteColor );" in vignette_block
	assert "CG_DrawPic( 0.0f, 0.0f, 640.0f, 480.0f, cgs.media.vignetteShader );" in vignette_block
	assert "trap_R_SetColor( NULL );" in vignette_block
	assert "static qhandle_t\tvignetteShader;" not in vignette_block


def test_disconnect_warning_uses_retail_net_icon_callsite() -> None:
	draw_source = CG_DRAW.read_text(encoding="utf-8")
	main_source = CG_MAIN.read_text(encoding="utf-8")
	register_block = _block_from_marker(main_source, "static void CG_RegisterGraphics( void )")
	disconnect_block = _block_from_marker(draw_source, "static void CG_DrawDisconnect")
	lagometer_block = _block_from_marker(draw_source, "static void CG_DrawLagometer")
	draw2d_block = _block_from_marker(draw_source, "static void CG_Draw2D( void )")

	assert 'cgs.media.connectionShader = trap_R_RegisterShader( "disconnected" );' in register_block
	assert 'netShader = trap_R_RegisterShader( "gfx/2d/net.tga" );' in disconnect_block
	assert "CG_DrawPic( x, y, 48, 48, netShader );" in disconnect_block
	assert "cgs.media.connectionShader" not in disconnect_block
	assert "cgs.localServer || cg.renderingThirdPerson" in lagometer_block
	assert "CG_DrawDisconnect();" not in lagometer_block
	assert "CG_DrawLagometer();" in draw2d_block
	assert "if ( !cg.renderingThirdPerson ) {" in draw2d_block
	assert draw2d_block.index("CG_DrawLagometer();") < draw2d_block.index("CG_DrawDisconnect();")


def test_global_vote_banner_uses_retail_keys_format_and_text_lane() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	main_source = CG_MAIN.read_text(encoding="utf-8")
	local_header = CG_LOCAL.read_text(encoding="utf-8")
	vote_block = _block_from_marker(source, "static void CG_DrawVote")
	draw2d_block = _block_from_marker(source, "static void CG_Draw2D( void )")

	assert "CG_DrawTeamVote" not in source
	assert "TEAMVOTE(" not in source
	assert "vmCvar_t\tcg_complaintWarning;" in main_source
	assert "extern\tvmCvar_t\t\tcg_complaintWarning;" in local_header
	assert '{ &cg_complaintWarning, "cg_complaintWarning", "1", CVAR_ARCHIVE },' in main_source
	assert "static vec4_t\tvoteColor = { 1.0f, 1.0f, 0.0f, 1.0f };" in vote_block
	assert 'CG_GetBindKeyName( "vote yes", yesKey, sizeof( yesKey ) );' in vote_block
	assert 'CG_GetBindKeyName( "vote no", noKey, sizeof( noKey ) );' in vote_block
	assert vote_block.index('CG_GetBindKeyName( "vote yes"') < vote_block.index("if ( !cgs.voteTime )")
	assert "cgs.gametype >= GT_TEAM && cgs.gametype != GT_RED_ROVER" in vote_block
	assert "cg_complaintWarning.integer && cg.complaintClient >= 0" in vote_block
	assert "cg.complaintEndTime > cg.time && !cg.renderingThirdPerson" in vote_block
	assert 's = va( "File complaint against %s for team-killing?", cgs.clientinfo[cg.complaintClient].name );' in vote_block
	assert 'CG_Text_Paint( 4.0f, 300.0f, 0.22f, voteColor, s, 0, 0, 0 );' in vote_block
	assert 's = va( "Press \'%s\' for Yes, or \'%s\' for No (%is)", yesKey, noKey, sec );' in vote_block
	assert 'CG_Text_Paint( 8.0f, 312.0f, 0.22f, colorWhite, s, 0, 0, 0 );' in vote_block
	assert "cg_complaintWarning.integer > 0 && cg.complaintClient < 0" in vote_block
	assert '"Your complaint has been filed."' in vote_block
	assert '"Your complaint has been dismissed."' in vote_block
	assert '"Comlaints cannot be filed against server admins."' in vote_block
	assert '"You received friendly fire from a server admin."' in vote_block
	assert "CG_Text_PaintNoAdjust( 3.0f, 300.0f, 0.22f, colorWhite, s, 0, 0 );" in vote_block
	assert 's = va( "VOTE(%is):%s Yes(%s):%i No(%s):%i", sec, cgs.voteString, yesKey, cgs.voteYes, noKey, cgs.voteNo );' in vote_block
	assert 'CG_Text_PaintNoAdjust( 4.0f, 300.0f, 0.22f, voteColor, s, 0, 0 );' in vote_block
	assert 'CG_Text_PaintNoAdjust( 8.0f, 312.0f, 0.22f, colorWhite, "or press ESC then click Vote", 0, 0 );' in vote_block
	assert draw2d_block.index("CG_DrawLagometer();") < draw2d_block.index("CG_DrawDisconnect();")
	assert draw2d_block.index("CG_DrawSpeedometer();") < draw2d_block.index("CG_DrawVote();")
	assert draw2d_block.index("CG_DrawVote();") < draw2d_block.index("CG_DrawUpperRight();")
	assert "cgs.gametype >= GT_TEAM && cg_drawTeamOverlay.integer == 2" in draw2d_block
	assert "CG_DrawTeamOverlay( 408.0f, qtrue, qfalse );" in draw2d_block
	assert draw2d_block.index("CG_DrawUpperRight();") < draw2d_block.index("CG_DrawLowerRight();")
	assert draw2d_block.index("CG_DrawUpperRight();") < draw2d_block.index("cg_drawTeamOverlay.integer == 2")
	assert draw2d_block.index("cg_drawTeamOverlay.integer == 2") < draw2d_block.index("CG_DrawLowerRight();")
	assert "CG_DrawTeamVote();" not in draw2d_block
	assert "CG_DrawSmallString" not in vote_block
	assert 'va("VOTE(%i):%s yes:%i no:%i"' not in vote_block


def test_cg_draw_bind_prompts_preserve_retail_raw_key_strings() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	bind_block = _block_from_marker(source, "static const char *CG_GetBindKeyName")
	pregame_block = _block_from_marker(source, "static void CG_DrawPregamePlacementPrompt")
	warmup_ready_block = _block_from_marker(source, "static void CG_DrawWarmupReadyPrompt")

	assert 'key = trap_Key_GetKey( cmd );' in bind_block
	assert 'trap_Key_KeynumToStringBuf( key, buf, len );' in bind_block
	assert "Q_strupr" not in bind_block
	assert 'Q_strncpyz( buf, "???"' not in bind_block
	assert "key == -1" not in bind_block

	assert 'keyName = CG_GetBindKeyName( "readyup", keyBuf, sizeof( keyBuf ) );' in pregame_block
	assert 'CG_GetBindKeyName( "ready", keyBuf, sizeof( keyBuf ) );' not in pregame_block
	assert '"???"' not in pregame_block
	assert 'prompt = va( "Press %s to skip the tutorial", keyName );' in pregame_block
	assert 'prompt = va( "Press %s to start the match", keyName );' in pregame_block

	assert 'keyName = CG_GetBindKeyName( "readyup", keyBuf, sizeof( keyBuf ) );' in warmup_ready_block
	assert 'prompt = va( "Press %s to unready yourself", keyName );' in warmup_ready_block
	assert 'prompt = va( "Press %s to ready yourself", keyName );' in warmup_ready_block


def test_warmup_waiting_status_preserves_retail_begin_copy() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	deadline_block = _block_from_marker(source, "static int CG_WarmupReadyDeadlineSeconds")
	waiting_block = _block_from_marker(source, "static void CG_BuildWarmupWaitingStatus")

	assert "remaining = ( cgs.matchReadyUpDeadline - cg.time ) / 1000 + 1;" in deadline_block
	assert "( ( cgs.matchReadyUpDeadline - cg.time ) + 1000 ) / 1000" not in deadline_block
	assert "if ( remaining < 0 ) {" in deadline_block
	assert 'Q_strncpyz( line1, "The wanking will begin", line1Size );' in waiting_block
	assert 'Q_strncpyz( line1, "The wanking will begin when", line1Size );' in waiting_block
	assert '"The match will begin"' not in waiting_block
	assert 'Q_strncpyz( line2, "when more players are ready.", line2Size );' in waiting_block
	assert 'Q_strncpyz( line2, "when more players join.", line2Size );' in waiting_block
	assert 'Q_strncpyz( line1, "Waiting for more players.", line1Size );' in waiting_block
	assert 'Com_sprintf( line2, line2Size, "The match requires %i player%s per team."' in waiting_block


def test_proximity_mine_warning_uses_retail_text_paint_lane() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	prox_block = _block_from_marker(source, "static void CG_DrawProxWarning")

	assert 'Com_sprintf( s, sizeof( s ), "INTERNAL COMBUSTION IN: %i", proxTick );' in prox_block
	assert 'Com_sprintf( s, sizeof( s ), "YOU HAVE BEEN MINED" );' in prox_block
	assert "CG_Text_GetExtents( s, 0.25f, 0, ITEM_TEXTSTYLE_SHADOWEDMORE, &w, NULL );" in prox_block
	assert "CG_Text_PaintNoAdjust( 320 - w / 2, 112.0f, 0.25f, g_color_table[ColorIndex(COLOR_RED)], s, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );" in prox_block
	assert "CG_DrawBigStringColor" not in prox_block


def test_demo_playback_controls_match_retail_geometry_and_colors() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	pair_block = _block_from_marker(source, "static void CG_DrawDemoControlPair")
	demo_block = _block_from_marker(source, "static void CG_DrawDemoPlaybackControls")

	assert "static vec4_t\tdemoKeyColor = { 1.0f, 1.0f, 0.0f, 1.0f };" in pair_block
	assert "0.15f, demoKeyColor" in pair_block
	assert "trap_Cvar_VariableValue( \"cl_freezeDemo\" )" in demo_block
	assert "panelColor[3] = 0.5f;" in demo_block
	assert "CG_FillRect( 210.0f, 355.0f, 220.0f, 60.0f, panelColor );" in demo_block
	assert "CG_DrawRect(" not in demo_block
	assert "CG_Text_PaintNoAdjust( 288.0f, 375.0f, 0.30f, colorWhite, deltaText, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );" in demo_block
	assert "320.0f - textWidth * 0.5f" not in demo_block
	assert "CG_DrawDemoControlPair( 235.0f - columnOffset, stateLabel, \"[SPACE]\" );" in demo_block
	assert "CG_DrawDemoControlPair( 275.0f - columnOffset, \"-\", \"[LEFT]\" );" in demo_block
	assert "CG_Text_PaintNoAdjust( 290.0f, 395.0f, 0.25f, colorWhite, speedText, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );" in demo_block
	assert "CG_DrawDemoControlPair( 320.0f - columnOffset, speedText, NULL );" not in demo_block
	assert "CG_DrawDemoControlPair( 330.0f - columnOffset, \"+\", \"[RIGHT]\" );" in demo_block
	assert "CG_DrawDemoControlPair( 370.0f - columnOffset, \"1.0x\", \"[DOWN]\" );" in demo_block
	assert "CG_DrawDemoControlPair( 320.0f - columnOffset, \"Advance\", \"[RIGHT]\" );" in demo_block
	assert "CG_DrawDemoControlPair( 410.0f - columnOffset, \"Hide\", \"[DEL]\" );" in demo_block


def test_centerprint_uses_retail_scale_and_race_y_bias() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	local_header = CG_LOCAL.read_text(encoding="utf-8")
	center_block = _block_from_marker(source, "void CG_CenterPrint")
	draw_block = _block_from_marker(source, "static void CG_DrawCenterString")

	assert "float\t\t\tcenterPrintScale;" in local_header
	assert "centerPrintCharWidth" not in local_header
	assert "cg.centerPrintTime = cg.time;" in center_block
	assert "if ( cgs.gametype == GT_RACE ) {" in center_block
	assert "cg.centerPrintY = y + 10;" in center_block
	assert "cg.centerPrintY = y;" in center_block
	assert "cg.centerPrintScale = scale;" in center_block
	assert "cg.centerPrintLines = 1;" in center_block
	assert "if (*s == '\\n')" in center_block
	assert "scale = cg.centerPrintScale;" in draw_block
	assert "scale = 0.5f;" in draw_block
	assert "cg.centerPrintY - (int)( (float)( cg.centerPrintLines * BIGCHAR_HEIGHT ) * scale );" in draw_block
	assert "CG_Text_Paint( x, y + h, scale, color, linebuffer, 0, 0, 0 );" in draw_block
	assert "ITEM_TEXTSTYLE_SHADOWEDMORE" not in draw_block


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
	assert "CG_ItemBackedPowerupIcon( powerups[i] )" in source
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
	pause_block = _block_from_marker(source, "static void CG_DrawMatchPauseStatus")
	status_block = _block_from_marker(source, "static void CG_DrawWarmupStatusText")

	assert "if ( !CG_DrawFollow() ) {" in draw2d_block
	assert "CG_DrawMatchPauseStatus();" in draw2d_block
	assert "CG_DrawWarmup();" in draw2d_block
	assert "CG_DrawTeamInfo();" in draw2d_block
	assert 'title = va( "%s vs %s", ci1->name, ci2->name );' in status_block
	assert "titleY = 90.0f;" in status_block
	assert "titleY = 60.0f;" not in status_block
	assert "titleY + verticalOffset" in status_block
	assert "remaining = ( cgs.matchTimeoutExpireTime - cg.time ) / 1000;" in pause_block
	assert "( ( cgs.matchTimeoutExpireTime - cg.time ) + 1000 ) / 1000" not in pause_block
	assert 'text = va( "Match resuming in ^5%d^7 seconds", remaining );' in pause_block
	assert "CG_Text_PaintNoAdjust( 320 - w / 2, 128.0f, 0.5f, colorWhite, text, 0, ITEM_TEXTSTYLE_SHADOWEDMORE );" in pause_block


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
	assert "CG_ItemBackedPowerupIcon( cg.powerupActive )" in powerups_block
	assert "CG_TeammatePOIPowerupIcon( cg.powerupActive )" not in powerups_block
	assert 'Com_sprintf( stackText, sizeof( stackText ), "x%i", activeCount );' in powerups_block
	assert "y = 408.0f;" in lower_right_block
	assert "cg_drawTeamOverlay.integer == 3" in lower_right_block
	assert "cg_drawTeamOverlay.integer == 2" not in lower_right_block
	assert "CG_DrawTeamOverlay( y, qtrue, qfalse );" in lower_right_block
	assert "CG_DrawPowerups( y );" in lower_right_block
	assert "if ( !menuHudActive ) {" in draw2d_block
	assert "CG_DrawLowerRight();" in draw2d_block


def test_upper_right_debug_stack_uses_retail_host_text_lanes() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	snapshot_block = _block_from_marker(source, "static float CG_DrawSnapshot")
	fps_block = _block_from_marker(source, "static float CG_DrawFPS")
	upper_right_block = _block_from_marker(source, "static float CG_DrawUpperRightStack")

	assert 's = va( "time:%i snap:%i cmd:%i", cg.snap->serverTime,' in snapshot_block
	assert "w = CG_Text_WidthExt( s, 0.25f, 0, FONT_DEFAULT );" in snapshot_block
	assert "drawY = (float)(int)( y + 2.0f ) + 16.0f;" in snapshot_block
	assert "CG_Text_PaintExt( 635.0f - w, drawY, 0.25f, colorWhite, s, 0.0f, 0, ITEM_TEXTSTYLE_NORMAL, FONT_DEFAULT );" in snapshot_block
	assert "return y + 16.0f + 4.0f;" in snapshot_block
	assert "CG_DrawBigString" not in snapshot_block

	assert 's = va( "%ifps", fps );' in fps_block
	assert "w = CG_Text_WidthExt( s, 0.25f, 0, FONT_MONO );" in fps_block
	assert "h = CG_Text_HeightExt( s, 0.25f, 0, FONT_MONO );" in fps_block
	assert "CG_Text_PaintExt( 635.0f - w, y + h, 0.25f, colorWhite, s, 0.0f, 0, ITEM_TEXTSTYLE_NORMAL, FONT_MONO );" in fps_block
	assert "return y + h;" in fps_block
	assert "return y;" in fps_block
	assert "CG_DrawBigString" not in fps_block

	assert upper_right_block.index( "CG_DrawSnapshot( y )" ) < upper_right_block.index( "CG_DrawFPS( y )" )
	assert upper_right_block.index( "CG_DrawFPS( y )" ) < upper_right_block.index( "CG_DrawAttacker( y )" )


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
	main_source = CG_MAIN.read_text(encoding="utf-8")
	local_header = CG_LOCAL.read_text(encoding="utf-8")
	shared = Q_SHARED.read_text(encoding="utf-8")
	msg = MSG.read_text(encoding="utf-8")
	active = G_ACTIVE.read_text(encoding="utf-8")
	input_block = _block_from_marker(source, "static void CG_DrawInputCmds( void )")
	register_block = _block_from_marker(source, "static void CG_RegisterInputCmdShaders( void )")
	graphics_block = _block_from_marker(main_source, "static void CG_RegisterGraphics( void )")
	draw2d_block = _block_from_marker(source, "static void CG_Draw2D( void )")

	for expected in (
		"qhandle_t\traceNavShader;",
		"qhandle_t\traceCommandUpShader;",
		"qhandle_t\traceCommandDownShader;",
		"qhandle_t\traceCommandRightShader;",
		"qhandle_t\traceCommandLeftShader;",
	):
		assert expected in local_header

	for expected in (
		'cgs.media.raceNavShader = trap_R_RegisterShader( "gfx/misc/racenav.jpg" );',
		'cgs.media.raceCommandUpShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_up" );',
		'cgs.media.raceCommandDownShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_down" );',
		'cgs.media.raceCommandRightShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_right" );',
		'cgs.media.raceCommandLeftShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_left" );',
	):
		assert expected in graphics_block

	for expected in (
		'cgs.media.raceCommandUpShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_up" );',
		'cgs.media.raceCommandDownShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_down" );',
		'cgs.media.raceCommandRightShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_right" );',
		'cgs.media.raceCommandLeftShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_left" );',
	):
		assert expected in register_block

	assert "static qhandle_t\tcg_inputCmdUpShader;" not in source
	assert "upShader = cgs.media.raceCommandUpShader;" in input_block
	assert "downShader = cgs.media.raceCommandDownShader;" in input_block
	assert "rightShader = cgs.media.raceCommandRightShader;" in input_block
	assert "leftShader = cgs.media.raceCommandLeftShader;" in input_block
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
