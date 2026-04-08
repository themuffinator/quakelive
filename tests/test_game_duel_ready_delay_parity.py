from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


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


def test_session_serializer_persists_duel_queue_fields() -> None:
	session_c = _read("src/code/game/g_session.c")

	assert "client->sess.selectedSpawnWeapon" in session_c
	assert "client->sess.spectateOnly" in session_c
	assert "client->sess.spectatorQueuePosition" in session_c
	assert "sess->spectateOnly = qtrue;" in session_c
