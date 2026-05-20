from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _extract_block(source: str, anchor: str) -> str:
	start = source.index(anchor)
	brace_start = source.index("{", start)
	depth = 0

	for index in range(brace_start, len(source)):
		char = source[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start : index + 1]

	raise AssertionError(f"Unterminated block for {anchor}")


def test_runframe_keeps_frame_only_timers_out_of_entity_think_loop() -> None:
	source = (REPO_ROOT / "src" / "code" / "game" / "g_main.c").read_text(encoding="utf-8")
	block = _extract_block(source, "static void G_DispatchScheduledThinks( qlr_game_frame_context_t *ctx, int msec ) {")

	assert "G_UpdateCvars();" not in block
	assert "LevelCheckTimers();" not in block


def test_runframe_restores_timeout_and_ctf_frame_hooks() -> None:
	source = (REPO_ROOT / "src" / "code" / "game" / "g_main.c").read_text(encoding="utf-8")
	runframe_block = _extract_block(source, "void G_RunFrame( int levelTime ) {")
	timeout_block = _extract_block(source, "static void G_RunFrameTimeoutAdvance( int msec ) {")
	level_check_timers_block = _extract_block(source, "static void LevelCheckTimers( void ) {")
	count_hook_block = _extract_block(source, "static void G_RunFrameRoundModeCountHooks( void ) {")
	hook_block = _extract_block(source, "static void G_RunFrameGametypeHooks( void ) {")
	level_timer_block = _extract_block(
		source,
		"static void G_CheckLevelTimers( qlr_game_frame_context_t *ctx, int previousWarmupTime, int previousIntermissionQueued ) {",
	)

	assert "G_RunFrameTimeoutAdvance( msec );" in runframe_block
	assert "LevelCheckTimers();" in runframe_block
	assert "AddTournamentPlayer();" in runframe_block
	assert "G_RunFrameRoundModeCountHooks();" in runframe_block
	assert "if ( g_gametype.integer == GT_TOURNAMENT ) {" not in runframe_block
	assert runframe_block.index("G_RunFrameRoundModeCountHooks();") < runframe_block.index("LevelCheckTimers();")
	assert runframe_block.index("LevelCheckTimers();") < runframe_block.index(
		"G_CheckLevelTimers( ctx, previousWarmupTime, previousIntermissionQueued );"
	)
	assert runframe_block.index("AddTournamentPlayer();") < runframe_block.index("G_SyncTournamentQueueTeamTasks();")
	assert "G_Frame_UpdateRoundController();" not in runframe_block
	assert "G_UpdateTeamCountConfigstrings();" not in runframe_block

	assert "level.startTime += msec;" in timeout_block
	assert "ent->s.pos.trTime += msec;" in timeout_block
	assert "ent->nextthink += msec;" in timeout_block
	assert "ent->eventTime += msec;" in timeout_block
	assert "if ( level.timeoutActive ) {" in level_check_timers_block
	assert "level.previousTime += level.msec;" in level_check_timers_block
	assert level_check_timers_block.index("level.previousTime += level.msec;") < level_check_timers_block.index(
		"G_CheckTimeoutExpired();"
	)

	assert "case GT_CLAN_ARENA:" in count_hook_block
	assert "case GT_FREEZE:" in count_hook_block
	assert "case GT_ATTACK_DEFEND:" in count_hook_block
	assert "case GT_RED_ROVER:" in count_hook_block
	assert "G_UpdateTeamCountConfigstrings();" in count_hook_block

	assert "G_EnsureQuadHogQuad();" in hook_block
	assert "G_Frame_UpdateRoundController();" in hook_block
	assert "G_RRTrackRoundActivity();" in hook_block
	assert "Team_ReturnFlagIfMissing( TEAM_RED );" in hook_block
	assert "Team_ReturnFlagIfMissing( TEAM_BLUE );" in hook_block
	assert "G_UpdateDominationPointCountConfigstrings();" in hook_block
	assert "G_QuadHogFrame();" not in hook_block

	assert "G_AutoShuffleCountdown_Frame();" in level_timer_block
	assert "Team_UpdateAutoShuffleState();" in level_timer_block
	assert "G_RunFrameGametypeHooks();" in level_timer_block
	assert "if ( g_gametype.integer >= GT_TEAM ) {" in level_timer_block
	assert level_timer_block.index("CheckExitRules();") < level_timer_block.index("CheckTeamStatus();")
	assert level_timer_block.index("CheckTeamStatus();") < level_timer_block.index("G_AutoShuffleCountdown_Frame();")
	assert level_timer_block.index("G_RunFrameGametypeHooks();") < level_timer_block.index("CheckVote();")
	assert "CheckTeamVote( TEAM_RED );" not in level_timer_block
	assert "CheckTeamVote( TEAM_BLUE );" not in level_timer_block


def test_ctf_flag_sanity_helper_exists_and_returns_missing_flags() -> None:
	source = (REPO_ROOT / "src" / "code" / "game" / "g_team.c").read_text(encoding="utf-8")
	block = _extract_block(source, "gentity_t *Team_ReturnFlagIfMissing")

	assert "ent->flags & FL_DROPPED_ITEM" in block
	assert "ent->r.contents != 0 || !( ent->s.eFlags & EF_NODRAW )" in block
	assert "ent->client->ps.powerups[flagPowerup]" in block
	assert "Team_ReturnFlag( team );" in block


def test_timeout_resume_restores_retail_client_timer_shifts() -> None:
	source = (REPO_ROOT / "src" / "code" / "game" / "g_main.c").read_text(encoding="utf-8")
	shift_block = _extract_block(source, "static int G_ShiftTimeoutAbsoluteTime( int value, int msec ) {")
	client_block = _extract_block(
		source,
		"static void G_ApplyTimeoutPauseDeltaToClient( gclient_t *client, int msec, qboolean freezeEnabled ) {",
	)
	pause_delta_block = _extract_block(source, "void G_ApplyTimeoutPauseDelta( int msec ) {")

	assert "value <= 0 || value == INT_MAX" in shift_block
	assert "return value + msec;" in shift_block

	assert "client->ps.pm_flags &= ~PMF_TIME_WATERJUMP;" in client_block
	assert "client->respawnTime = G_ShiftTimeoutAbsoluteTime( client->respawnTime, msec );" in client_block
	assert "client->airOutTime = G_ShiftTimeoutAbsoluteTime( client->airOutTime, msec );" in client_block
	assert "client->invulnerabilityTime = G_ShiftTimeoutAbsoluteTime( client->invulnerabilityTime, msec );" in client_block
	assert "client->holdableInvulnerabilityTime = G_ShiftTimeoutAbsoluteTime( client->holdableInvulnerabilityTime, msec );" in client_block
	assert "client->freezeTime = G_ShiftTimeoutAbsoluteTime( client->freezeTime, msec );" in client_block
	assert "client->freezeNextThawTick = G_ShiftTimeoutAbsoluteTime( client->freezeNextThawTick, msec );" in client_block
	assert "client->freezeAutoThawTime = G_ShiftTimeoutAbsoluteTime( client->freezeAutoThawTime, msec );" in client_block
	assert "client->freezeEnvironmentalRespawnTime = G_ShiftTimeoutAbsoluteTime( client->freezeEnvironmentalRespawnTime, msec );" in client_block
	assert "client->freezeProtectedUntil = G_ShiftTimeoutAbsoluteTime( client->freezeProtectedUntil, msec );" in client_block
	assert "client->ps.powerups[powerup] = G_ShiftTimeoutAbsoluteTime( client->ps.powerups[powerup], msec );" in client_block
	assert "client->inactivityTime = G_ShiftTimeoutAbsoluteTime" not in client_block

	assert "freezeEnabled = G_FreezeGametypeEnabled();" in pause_delta_block
	assert "G_ApplyTimeoutPauseDeltaToClient( client, msec, freezeEnabled );" in pause_delta_block


def test_timeout_expiry_helper_preserves_retail_resume_handoff() -> None:
	source = (REPO_ROOT / "src" / "code" / "game" / "g_main.c").read_text(encoding="utf-8")
	timeout_block = _extract_block(source, "static void G_CheckTimeoutExpired( void ) {")

	assert "if ( !level.timeoutActive ) {" in timeout_block
	assert "return;" in timeout_block
	assert "if ( !level.timeoutExpireTime || level.time < level.timeoutExpireTime ) {" in timeout_block
	assert "pausedDuration = 0;" in timeout_block
	assert "if ( level.timeoutStartTime > 0 && level.time > level.timeoutStartTime ) {" in timeout_block
	assert "pausedDuration = level.time - level.timeoutStartTime;" in timeout_block
	assert "G_ApplyTimeoutPauseDelta( pausedDuration );" in timeout_block
	assert "G_ResetTimeoutState();" in timeout_block
	assert "G_UpdateMatchStateConfigString();" in timeout_block
	assert timeout_block.index("G_ApplyTimeoutPauseDelta( pausedDuration );") < timeout_block.index("G_ResetTimeoutState();")
	assert timeout_block.index("G_ResetTimeoutState();") < timeout_block.index("G_UpdateMatchStateConfigString();")
