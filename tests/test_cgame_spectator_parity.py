"""Guard retail-backed cgame spectator/export behavior against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"


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


def test_shutdown_restores_ui_mainmenu() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	block = _block_from_marker(source, "void CG_Shutdown")

	assert 'trap_Cvar_Set( "ui_mainmenu", "1" );' in block


def test_auto_follow_powerup_matches_retail_command_shape() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	should_follow = _block_from_marker(source, "static qboolean CG_ShouldAutoFollowTrack")
	try_follow = _block_from_marker(source, "static void CG_TryAutoFollowPowerup")
	track_event = _block_from_marker(source, "void CG_SpectatorTrackEvent")

	assert "CG_SPECTATOR_TRACK_FLAG || trackType == CG_SPECTATOR_TRACK_POWERUP" in should_follow
	assert "followMode > 1 && trackType != CG_SPECTATOR_TRACK_FLAG" not in should_follow

	assert 'suffix = " pw";' in try_follow
	assert "cg_followPowerup.integer == 2 && trackType == CG_SPECTATOR_TRACK_POWERUP" in try_follow
	assert 'trap_SendClientCommand( va( "follow %d%s", clientNum, suffix ) );' in try_follow

	assert "CG_TryAutoFollowPowerup( clientNum, trackType );" in track_event
	assert 'trap_SendClientCommand( va( "follow %d", clientNum ) );' not in track_event


def test_tracked_slot_notifiers_arm_retail_latches_and_replay_last_message() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	slot_block = _block_from_marker(main_source, "static void CG_ShowTrackedPlayerSlot")
	first_block = _block_from_marker(main_source, "static void CG_Show1stTrackedPlayer")
	second_block = _block_from_marker(main_source, "static void CG_Show2ndTrackedPlayer")
	tracked_block = _block_from_marker(newdraw_source, "static qboolean CG_SpectatorSlotTracked")

	assert "spectatorSlotTrackedTime[2];" in local_source
	assert "cg.spectatorSlotTrackedTime[slot] = cg.time + CG_SPECTATOR_SLOT_TRACK_HOLD;" in slot_block
	assert "CG_ReplayLastMessageFromCvar();" in slot_block
	assert "clientNum =" not in slot_block
	assert "infoValid" not in slot_block
	assert "CG_ShowTrackedPlayerSlot( 0 );" in first_block
	assert "CG_ShowTrackedPlayerSlot( 1 );" in second_block
	assert "trackedTime = cg.spectatorSlotTrackedTime[0];" in tracked_block
	assert "trackedTime = cg.spectatorSlotTrackedTime[1];" in tracked_block
	assert "if ( trackedTime > cg.time ) {" in tracked_block


def test_key_event_intercepts_retail_hud_binding_commands() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	handler_block = _block_from_marker(source, "static qboolean CG_HandleHudBindingCommand")
	key_block = _block_from_marker(source, "void CG_KeyEvent")

	for expected in (
		'"messagemode"',
		'"screenshot"',
		'"screenshotJPEG"',
		'"+voice"',
		'"+scores"',
		'Q_stricmpn( binding, "messagemode", sizeof( "messagemode" ) - 1 ) == 0',
		'trap_SendConsoleCommand( binding );',
		'trap_SendConsoleCommand( "+voice\\n" );',
		"CG_ScoresDown_f();",
	):
		assert expected in handler_block

	assert "trap_Cmd_ExecuteText( EXEC_APPEND, binding );" not in handler_block
	assert 'trap_Cmd_ExecuteText( EXEC_APPEND, "+voice\\n" );' not in handler_block
	assert "CG_RequestScoreboard" not in source
	assert "char bindingBuf[0x20] = { 0 };" in key_block
	assert "trap_Key_GetBindingBuf( key, bindingBuf, sizeof( bindingBuf ) );" in key_block
	assert "if ( CG_HandleHudBindingCommand( bindingBuf ) ) {" in key_block
	assert "CG_BrowserDisplayHandleKey( key, down, cgs.cursorX, cgs.cursorY );" in key_block
	assert "CG_EventHandling(CGAME_EVENT_NONE);" not in key_block
	assert "trap_Key_SetCatcher(0);" not in key_block
	assert "cgs.capturedItem =" not in key_block


def test_duel_scorebox_status_ownerdraws_restore_retail_label_split() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	status_block = _block_from_marker(source, "static qboolean CG_BuildSpectatorStatusText")
	shader_block = _block_from_marker(source, "static qhandle_t CG_GetSpectatorStatusShader")
	label_block = _block_from_marker(source, "static void CG_DrawSpectatorStatusLabel")
	primary_block = _block_from_marker(source, "static void CG_DrawSpectatorPrimaryStatus")
	secondary_block = _block_from_marker(source, "static void CG_DrawSpectatorSecondaryStatus")
	metric_block = _block_from_marker(source, "static qboolean CG_BuildPlacementMetricText")
	placement_block = _block_from_marker(source, "static qboolean CG_DrawPlacementMetricOwnerDraw")

	for expected in (
		"cgs.gametype == GT_TOURNAMENT",
		"cg.warmup == 0",
		"cg.snap->ps.pm_type != PM_INTERMISSION",
		'Q_strncpyz( buffer, "LEADS", bufferSize );',
		'Q_strncpyz( buffer, "TRAILS", bufferSize );',
		'Q_strncpyz( buffer, "TIED", bufferSize );',
		'Q_strncpyz( buffer, "READY", bufferSize );',
		'Q_strncpyz( buffer, "NOT READY", bufferSize );',
		"CG_ClientReadyForScoreboxStatus( score->client )",
		"*shader = CG_GetSpectatorStatusShader( slot, status );",
	):
		assert expected in status_block

	for expected in (
		"return cgs.media.scoreFirstPlayerReadyShader;",
		"return cgs.media.scoreFirstPlayerNotReadyShader;",
		"return cgs.media.scoreFirstPlayerLeadsShader;",
		"return cgs.media.scoreFirstPlayerTiedShader;",
		"return cgs.media.scoreFirstPlayerTrailsShader;",
		"return cgs.media.scoreSecondPlayerReadyShader;",
		"return cgs.media.scoreSecondPlayerNotReadyShader;",
		"return cgs.media.scoreSecondPlayerLeadsShader;",
		"return cgs.media.scoreSecondPlayerTiedShader;",
		"return cgs.media.scoreSecondPlayerTrailsShader;",
	):
		assert expected in shader_block

	assert "CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );" in label_block
	assert "CG_Text_Paint( x, rect->y + rect->h, 0.16f, colorWhite, buffer, 0, 0, 3 );" in label_block
	assert "CG_DrawSpectatorStatusLabel( rect, 0 );" in primary_block
	assert "CG_DrawSpectatorStatusLabel( rect, 1 );" in secondary_block
	assert "case CG_1ST_PLYR_READY:" in metric_block
	assert "return qfalse;" in metric_block
	assert "if ( ownerDraw == CG_1ST_PLYR_READY ) {" in placement_block
	assert "CG_DrawSpectatorPrimaryStatus( rect );" in placement_block
	assert "if ( ownerDraw == CG_2ND_PLYR_READY ) {" in placement_block
	assert "CG_DrawSpectatorSecondaryStatus( rect );" in placement_block
	assert 'Q_strncpyz( buffer, CG_ClientReadyOnIntermission( score->client ) ? "Ready" : "-", bufferSize );' not in source
	assert "Vector4Set( color," not in status_block


def test_score_value_wrapper_restores_retail_competitive_score_owner() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	value_block = _block_from_marker(source, "static void CG_DrawScoreValue")

	for expected in (
		"case CG_PLAYER_SCORE:",
		"CG_DrawPlayerScore( rect, scale, color, shader, textStyle );",
	):
		assert expected in value_block

	for expected in (
		"case CG_PLAYER_SCORE:",
		"CG_DrawScoreValue( &rect, scale, color, shader, textStyle, ownerDraw );",
		"case CG_RED_SCORE:",
		"CG_DrawTeamScore( &rect, scale, color, textStyle, TEAM_RED, align );",
		"case CG_BLUE_SCORE:",
		"CG_DrawTeamScore( &rect, scale, color, textStyle, TEAM_BLUE, align );",
	):
		assert expected in source
