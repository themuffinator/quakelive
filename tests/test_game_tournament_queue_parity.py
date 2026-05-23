from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


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


def test_duel_queue_helpers_and_dirty_latch_match_retail_surface() -> None:
	local_h = _read("src/code/game/g_local.h")
	main_c = _read("src/code/game/g_main.c")

	assert "qboolean\tspectatorQueuePositionDirty;" in local_h
	assert "void G_UpdateTournamentQueuePositions( void );" in local_h
	assert "void G_SyncTournamentQueueTeamTasks( void );" in local_h
	assert "static qboolean G_IsTournamentQueueEligibleClient( const gclient_t *client ) {" in main_c
	assert "client->sess.spectatorState == SPECTATOR_SCOREBOARD ||" in main_c
	assert "client->sess.spectatorClient < 0" in main_c
	assert "static int QDECL G_CompareTournamentQueueTimes( const void *a, const void *b ) {" in main_c
	assert "void G_UpdateTournamentQueuePositions( void ) {" in main_c
	assert "for ( i = 0; i < level.numConnectedClients; i++ ) {" in main_c
	assert "clientNum = level.sortedClients[i];" in main_c
	assert main_c.count("G_IsTournamentQueueEligibleClient( client )") >= 2
	assert "qsort( queuedClients, queuedCount, sizeof( queuedClients[0] ), G_CompareTournamentQueueTimes );" in main_c
	assert "client->sess.spectatorQueuePosition = queuePosition;" in main_c
	assert "client->sess.spectatorQueuePositionDirty = qtrue;" in main_c
	assert "void G_SyncTournamentQueueTeamTasks( void ) {" in main_c
	assert "int\t\tdirtyClients[MAX_CLIENTS];" in main_c
	assert "if ( client->sess.spectatorQueuePositionDirty ) {" in main_c
	assert "client->sess.spectatorQueuePositionDirty = qfalse;" in main_c
	assert "dirtyClients[dirtyCount] = clientNum;" in main_c
	assert "for ( i = 0; i < dirtyCount; i++ ) {" in main_c
	assert 'Info_SetValueForKey( userinfo, "teamtask", va( "%d", client->sess.spectatorQueuePosition ) );' in main_c
	assert "trap_SetUserinfo( clientNum, userinfo );" in main_c
	assert "ClientUserinfoChanged( clientNum );" in main_c


def test_queue_teamtask_sync_clears_dequeued_spectators() -> None:
	main_c = _read("src/code/game/g_main.c")
	block = _extract_block(main_c, "void G_SyncTournamentQueueTeamTasks( void ) {")

	assert "clientNum = dirtyClients[i];" in block
	assert "client->sess.spectatorQueuePosition == 0" not in block
	assert "!G_IsTournamentQueueEligibleClient( client )" not in block
	assert 'Info_SetValueForKey( userinfo, "teamtask", va( "%d", client->sess.spectatorQueuePosition ) );' in block


def test_clientuserinfochanged_publishes_queue_surface() -> None:
	client_c = _read("src/code/game/g_client.c")

	assert "G_UpdateTournamentQueuePositions();" in client_c
	assert "\\\\rp\\\\%d\\\\p\\\\%d\\\\so\\\\%i\\\\pq\\\\%i" in client_c
	assert "\\\\so\\\\%i\\\\pq\\\\%i" in client_c


def test_queue_helpers_are_wired_into_init_and_frame_flow() -> None:
	main_c = _read("src/code/game/g_main.c")
	session_c = _read("src/code/game/g_session.c")

	assert "G_UpdateTournamentQueuePositions();" in main_c
	assert "G_SyncTournamentQueueTeamTasks();" in main_c
	assert "AddTournamentPlayer();" in main_c
	assert main_c.index("G_SyncTournamentQueueTeamTasks();") < main_c.index("CheckTournament();")
	assert main_c.index("AddTournamentPlayer();") < main_c.index("G_SyncTournamentQueueTeamTasks();")
	assert "G_UpdateTournamentQueuePositions();" not in _extract_block(session_c, "void G_WriteSessionData( void ) {")


def test_addtournamentplayer_self_gates_and_resets_duel_pregame_state() -> None:
	main_c = _read("src/code/game/g_main.c")
	block = _extract_block(main_c, "void AddTournamentPlayer( void ) {")

	assert "if ( g_gametype.integer != GT_TOURNAMENT ) {" in block
	assert "if ( level.intermissiontime || level.intermissionQueued || level.timeoutActive ) {" in block
	assert "G_ResetDuelWarmupState( qfalse );" in block
	assert 'SetTeam( nextInLine, "f" );' in block
	assert "G_ClearConnectedReadyStates( qtrue );" in block


def test_queue_dirty_slot_is_documented_in_source_overlay() -> None:
	game_types_h = _read("src/game/ql_game_types.h")

	assert "int32_t selectedSpawnWeapon;" in game_types_h
	assert "int32_t spectateOnly;" in game_types_h
	assert "int32_t spectatorQueuePosition;" in game_types_h
	assert "int32_t spectatorQueuePositionDirty;" in game_types_h
	assert 'QL_STATIC_ASSERT(offsetof(ql_clientSession_source_t, selectedSpawnWeapon) == 0x10, "clientSession_source_t.selectedSpawnWeapon offset");' in game_types_h
	assert 'QL_STATIC_ASSERT(offsetof(ql_clientSession_source_t, spectateOnly) == 0x24, "clientSession_source_t.spectateOnly offset");' in game_types_h
	assert 'QL_STATIC_ASSERT(offsetof(ql_clientSession_source_t, spectatorQueuePosition) == 0x28, "clientSession_source_t.spectatorQueuePosition offset");' in game_types_h
	assert 'QL_STATIC_ASSERT(offsetof(ql_clientSession_source_t, spectatorQueuePositionDirty) == 0x2C, "clientSession_source_t.spectatorQueuePositionDirty offset");' in game_types_h
