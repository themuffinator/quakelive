from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_team_count_configstrings_are_declared_and_published() -> None:
	bg_public = _read("src/code/game/bg_public.h")
	match_state = _read("src/code/game/g_match_state.c")
	main_c = _read("src/code/game/g_main.c")

	assert "#define CS_ROUND_START_TIME" in bg_public
	assert "#define CS_TEAM_COUNT_RED" in bg_public
	assert "#define CS_TEAM_COUNT_BLUE" in bg_public
	assert "static void G_UpdateRoundStartConfigString( void ) {" in match_state
	assert 'trap_SetConfigstring( CS_ROUND_START_TIME, va( "%i", level.roundStartTime ) );' in match_state
	assert "void G_UpdateTeamCountConfigstrings( void ) {" in match_state
	assert "level.time > s_lastTeamCountConfigstringUpdateTime" in match_state
	assert "level.time - s_lastTeamCountConfigstringUpdateTime <= 250" in match_state
	assert "s_lastTeamCountConfigstringUpdateTime = level.time;" in match_state
	assert 'trap_SetConfigstring( CS_TEAM_COUNT_RED, va( "%i", counts[TEAM_RED] ) );' in match_state
	assert 'trap_SetConfigstring( CS_TEAM_COUNT_BLUE, va( "%i", counts[TEAM_BLUE] ) );' in match_state
	assert "G_UpdateTeamCountConfigstrings();" in main_c


def test_match_state_team_counts_follow_retail_round_controller_policy() -> None:
	match_state = _read("src/code/game/g_match_state.c")

	assert "static qboolean G_UsesRoundControllerTeamCounts( void ) {" in match_state
	assert "case GT_CLAN_ARENA:" in match_state
	assert "case GT_ATTACK_DEFEND:" in match_state
	assert "case GT_FREEZE:" in match_state
	assert "case GT_RED_ROVER:" in match_state
	assert "return ( level.roundState != ROUNDSTATE_INACTIVE ) ? qtrue : qfalse;" in match_state
	assert "G_CountActivePlayersByTeam( counts );" in match_state
	assert "G_CountConnectedClientsByTeam( counts );" in match_state
	assert "G_SetMatchStateInt( info, MATCH_STATE_KEY_TEAM_RED_COUNT, counts[TEAM_RED] );" in match_state
	assert "G_SetMatchStateInt( info, MATCH_STATE_KEY_TEAM_BLUE_COUNT, counts[TEAM_BLUE] );" in match_state


def test_team_helper_surface_matches_retail_native_helper_bundle() -> None:
	local_h = _read("src/code/game/g_local.h")
	team_c = _read("src/code/game/g_team.c")

	assert "qboolean G_ClientsOnSameTeam( gclient_t *clientA, gclient_t *clientB );" in local_h
	assert "qboolean G_ClientNumsOnSameTeam( int clientNumA, int clientNumB );" in local_h
	assert "qboolean G_AreEnemyClients( int clientNumA, int clientNumB );" in local_h
	assert "qboolean G_IsClientSpectator( int clientNum );" in local_h
	assert "qboolean G_IsClientAdmin( int clientNum );" in local_h
	assert "int G_GetClientScore( int clientNum );" in local_h
	assert "void G_CountActivePlayersByTeam( int counts[TEAM_NUM_TEAMS] );" in local_h
	assert "void G_CountConnectedClientsByTeam( int counts[TEAM_NUM_TEAMS] );" in local_h

	assert "static gclient_t *G_GetValidatedClientSlot( int clientNum ) {" in team_c
	assert "qboolean G_ClientsOnSameTeam( gclient_t *clientA, gclient_t *clientB ) {" in team_c
	assert "qboolean G_ClientNumsOnSameTeam( int clientNumA, int clientNumB ) {" in team_c
	assert "qboolean G_AreEnemyClients( int clientNumA, int clientNumB ) {" in team_c
	assert "qboolean G_IsClientSpectator( int clientNum ) {" in team_c
	assert "qboolean G_IsClientAdmin( int clientNum ) {" in team_c
	assert "int G_GetClientScore( int clientNum ) {" in team_c
	assert "return ( client && client->sess.privilege == PRIV_ADMIN ) ? qtrue : qfalse;" in team_c
	assert "return client->ps.persistant[PERS_SCORE];" in team_c
	assert "return G_ClientsOnSameTeam( ent1->client, ent2->client );" in team_c
