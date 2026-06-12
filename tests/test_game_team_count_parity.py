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
	assert "if ( level.roundState == ROUNDSTATE_ACTIVE ) {" in match_state
	assert 'trap_SetConfigstring( CS_ROUND_START_TIME, va( "%i", level.roundStartTime ) );' in match_state
	assert "g_gametype.integer == GT_CLAN_ARENA && level.roundState == ROUNDSTATE_COMPLETE" in match_state
	assert "g_gametype.integer == GT_ATTACK_DEFEND" in match_state
	assert "level.adRoundState == AD_ROUNDSTATE_COMPLETE || level.adRoundState == AD_ROUNDSTATE_EXIT" in match_state
	assert "g_gametype.integer == GT_RED_ROVER" in match_state
	assert "level.rrRoundState == RR_ROUNDSTATE_COMPLETE || level.rrRoundState == RR_ROUNDSTATE_EXIT" in match_state
	assert 'trap_SetConfigstring( CS_ROUND_START_TIME, va( "%i", -1 ) );' in match_state
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


def test_clan_arena_match_state_uses_retail_compact_payload_shape() -> None:
	match_state = _read("src/code/game/g_match_state.c")

	assert "static qboolean G_BuildClanArenaMatchStateInfo( char *info ) {" in match_state
	assert 'Q_strncpyz( info, "\\\\time\\\\-1\\\\round\\\\0", MAX_INFO_STRING );' in match_state
	assert "G_SetMatchStateInt( info, MATCH_STATE_KEY_TIME, level.warmupTime );" in match_state
	assert "G_SetMatchStateInt( info, MATCH_STATE_KEY_ROUND, G_ClanArenaWarmupRoundNumber() );" in match_state
	assert "G_SetMatchStateInt( info, MATCH_STATE_KEY_ROUND, level.roundNumber );" in match_state
	assert "if ( !G_BuildClanArenaMatchStateInfo( info )" in match_state


def test_attack_defend_match_state_uses_retail_compact_payload_shape() -> None:
	match_state = _read("src/code/game/g_match_state.c")

	assert "static int G_AttackDefendPublishedTurn( void ) {" in match_state
	assert "static qboolean G_BuildAttackDefendMatchStateInfo( char *info ) {" in match_state
	assert 'Q_strncpyz( info, "\\\\time\\\\-1\\\\round\\\\0\\\\turn\\\\0\\\\state\\\\0", MAX_INFO_STRING );' in match_state
	assert "G_SetMatchStateInt( info, MATCH_STATE_KEY_TIME, level.roundTransitionTime );" in match_state
	assert "G_SetMatchStateInt( info, MATCH_STATE_KEY_ROUND, level.roundNumber );" in match_state
	assert "G_SetMatchStateInt( info, MATCH_STATE_KEY_TURN, level.adTurnIndex );" in match_state
	assert "G_SetMatchStateInt( info, MATCH_STATE_KEY_STATE, ROUNDSTATE_WARMUP );" in match_state
	assert "G_SetMatchStateInt( info, MATCH_STATE_KEY_STATE, ROUNDSTATE_ACTIVE );" in match_state
	assert "G_SetMatchStateInt( info, MATCH_STATE_KEY_TURN, G_AttackDefendPublishedTurn() );" in match_state
	assert "&& !G_BuildAttackDefendMatchStateInfo( info )" in match_state


def test_red_rover_match_state_uses_retail_compact_payload_shape() -> None:
	match_state = _read("src/code/game/g_match_state.c")

	assert "static int G_RedRoverPublishedRoundNumber( void ) {" in match_state
	assert "static qboolean G_BuildRedRoverMatchStateInfo( char *info ) {" in match_state
	assert "g_gametype.integer != GT_RED_ROVER" in match_state
	assert 'Q_strncpyz( info, "\\\\time\\\\-1\\\\round\\\\0", MAX_INFO_STRING );' in match_state
	assert "case RR_ROUNDSTATE_WARMUP:" in match_state
	assert "case RR_ROUNDSTATE_INFECTION_SEED:" in match_state
	assert "G_SetMatchStateInt( info, MATCH_STATE_KEY_TIME, level.roundTransitionTime );" in match_state
	assert "G_SetMatchStateInt( info, MATCH_STATE_KEY_ROUND, G_RedRoverPublishedRoundNumber() );" in match_state
	assert "case RR_ROUNDSTATE_ACTIVE:" in match_state
	assert "case RR_ROUNDSTATE_COMPLETE:" in match_state
	assert "case RR_ROUNDSTATE_EXIT:" in match_state
	assert "&& !G_BuildRedRoverMatchStateInfo( info )" in match_state


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
