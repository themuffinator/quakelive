from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


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


def test_duel_ready_delay_cvars_and_deadline_publication_present() -> None:
	local_h = _read("src/code/game/g_local.h")
	main_c = _read("src/code/game/g_main.c")

	assert "g_warmupReadyDelay" in local_h
	assert "g_warmupReadyDelayAction" in local_h
	assert "readyUpDelayDeadline" in local_h
	assert "if ( level.readyUpDelayDeadline > 0 )" in main_c
	assert "G_CheckReadyUpDelayAction( void )" in main_c


def test_duel_queue_semantics_use_spectate_only_latch() -> None:
	cmds_c = _read("src/code/game/g_cmds.c")
	main_c = _read("src/code/game/g_main.c")

	assert "client->sess.spectateOnly" in cmds_c
	assert "client->sess.spectatorQueuePosition = 0;" in cmds_c
	assert "You are in the queue to play" in cmds_c
	assert "You are set to spectate only" in cmds_c
	assert "if ( client->sess.spectateOnly )" in main_c


def test_checktournament_gates_duel_countdown_on_ready_state() -> None:
	main_c = _read("src/code/game/g_main.c")

	assert "G_GetDuelReadyStateCounts( &eligibleCount, &readyCount );" in main_c
	assert "G_ResetDuelWarmupState( qtrue );" in main_c
	assert "if ( eligibleCount == 2 && readyCount == 2 )" in main_c
	assert "G_CheckReadyUpDelayAction();" in main_c


def test_ready_delay_uses_cached_retail_tally() -> None:
	local_h = _read("src/code/game/g_local.h")
	main_c = _read("src/code/game/g_main.c")
	delay_block = _block_from_marker(main_c, "static void G_CheckReadyUpDelayAction")

	assert "readyUpEligibleClients" in local_h
	assert "readyUpReadyClients" in local_h
	assert "level.readyUpEligibleClients = eligibleCount;" in main_c
	assert "level.readyUpReadyClients = readyCount;" in main_c
	assert "level.readyUpReadyClients != 1" in delay_block
	assert "eligibleCount != 2" not in delay_block


def test_checktournament_preserves_live_duels_and_clears_ready_latches_on_forced_reset() -> None:
	main_c = _read("src/code/game/g_main.c")
	check_block = _block_from_marker(main_c, "void CheckTournament")
	add_block = _block_from_marker(main_c, "void AddTournamentPlayer")

	assert "static qboolean G_ClearConnectedReadyStates( qboolean updateUserinfo ) {" in main_c
	assert "ClientUserinfoChanged( i );" in main_c
	assert check_block.index("if ( level.warmupTime == 0 ) {") < check_block.index("if ( level.numPlayingClients < 2 ) {")
	assert "if ( G_CanForfeit( NULL, qfalse ) ) {" in check_block
	assert "G_ApplyForfeit();" in check_block
	assert "G_ResetDuelWarmupState( ( level.warmupTime != -1 ) ? qtrue : qfalse );" in check_block
	assert "G_ClearConnectedReadyStates( qtrue );" in check_block
	assert 'SetTeam( nextInLine, "f" );' in add_block
	assert "G_ClearConnectedReadyStates( qtrue );" in add_block
	assert add_block.index('SetTeam( nextInLine, "f" );') < add_block.index("G_ClearConnectedReadyStates( qtrue );")


def test_session_serializer_persists_duel_queue_fields() -> None:
	session_c = _read("src/code/game/g_session.c")

	assert "client->sess.selectedSpawnWeapon" in session_c
	assert "client->sess.spectateOnly" in session_c
	assert "client->sess.spectatorQueuePosition" in session_c
	assert "sess->spectateOnly = qtrue;" in session_c
