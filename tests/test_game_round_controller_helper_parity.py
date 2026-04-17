from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_clan_arena_round_controller_helpers_match_retail_mapping_surface() -> None:
	active_c = _read("src/code/game/g_active.c")
	client_c = _read("src/code/game/g_client.c")
	team_c = _read("src/code/game/g_team.c")

	assert "int G_CAResolveRoundState( void ) {" in active_c
	assert "static int CA_RoundStateTransition( qboolean announce ) {" in active_c
	assert "if ( g_gametype.integer == GT_CLAN_ARENA ) {" in active_c
	assert "CA_RoundStateTransition( qtrue );" in active_c
	assert "level.roundPendingExit = G_CAFZCheckExitRules( qfalse );" in active_c
	assert "state = G_CAResolveRoundState();" in team_c
	assert "caState = G_CAResolveRoundState();" in client_c


def test_freeze_round_controller_helpers_match_retail_mapping_surface() -> None:
	active_c = _read("src/code/game/g_active.c")
	client_c = _read("src/code/game/g_client.c")
	freeze_c = _read("src/code/game/g_freeze.c")
	main_c = _read("src/code/game/g_main.c")

	assert "int G_FreezeResolveRoundState( void ) {" in active_c
	assert "static qboolean G_FreezeShouldCompleteRound( const int counts[TEAM_NUM_TEAMS] ) {" in active_c
	assert "static team_t G_FreezeEvaluateRoundWinner( const int counts[TEAM_NUM_TEAMS], const int health[TEAM_NUM_TEAMS] ) {" in active_c
	assert "void G_RoundHandleWarmupDelayCvarUpdate( void ) {" in active_c
	assert "return G_RoundTimeLimitExpired( level.roundStartTime );" in active_c
	assert "level.roundPendingExit = G_CAFZCheckExitRules( qfalse );" in active_c
	assert "switch ( level.roundState ) {" in active_c
	assert "state = G_FreezeResolveRoundState();" in active_c
	assert active_c.index("G_FreezeRecountLivingClients();") < active_c.index("if ( !G_FreezeShouldCompleteRound( level.freezeLivingCount ) ) {")
	assert active_c.index("if ( !G_FreezeShouldCompleteRound( level.freezeLivingCount ) ) {") < active_c.index("winner = G_FreezeEvaluateRoundWinner( level.freezeLivingCount, level.freezeLivingHealth );")
	assert "if ( !G_FreezeShouldCompleteRound( level.freezeLivingCount ) ) {" in active_c
	assert "winner = G_FreezeEvaluateRoundWinner( level.freezeLivingCount, level.freezeLivingHealth );" in active_c
	assert "Freeze_RoundStateTransition( qtrue );" in active_c
	assert "if ( G_FreezeResolveRoundState() != ROUNDSTATE_ACTIVE ) {" in freeze_c
	assert "roundState = G_FreezeResolveRoundState();" in client_c
	assert "client->freezeAccumulatedThaw = 0;" in client_c
	assert "client->freezeAutoThawTime = 0;" in client_c
	assert "client->freezeNextThawTick = G_ShiftTimeoutAbsoluteTime( client->freezeNextThawTick, msec );" in main_c
	assert "client->freezeProtectedUntil = G_ShiftTimeoutAbsoluteTime( client->freezeProtectedUntil, msec );" in main_c


def test_red_rover_controller_readback_helpers_match_retail_mapping_surface() -> None:
	active_c = _read("src/code/game/g_active.c")
	client_c = _read("src/code/game/g_client.c")
	cmds_c = _read("src/code/game/g_cmds.c")
	local_h = _read("src/code/game/g_local.h")

	assert "int G_RRResolveRoundState( void ) {" in active_c
	assert "static int RR_RoundStateTransition( qboolean announce ) {" in active_c
	assert "G_RRInitRoundController();" in active_c
	assert "RR_RoundStateTransition( qtrue );" in active_c
	assert "if ( level.warmupTime < 0 ) {" in active_c
	assert "RR_ROUNDSTATE_INFECTION_SEED = 2," in local_h
	assert "RR_ROUNDSTATE_EXIT = 5" in local_h
	assert "void G_RRInitRoundController( void );" in local_h
	assert "level.rrPendingRoundState = RR_ROUNDSTATE_ACTIVE;" in active_c
	assert "state == RR_ROUNDSTATE_INACTIVE && level.roundTransitionTime == ROUND_TRANSITION_NONE" in active_c
	assert "state == RR_ROUNDSTATE_ACTIVE || state == RR_ROUNDSTATE_INFECTION_SEED" in active_c
	assert "G_RRResolveRoundState();" in cmds_c
	assert "if ( G_RRResolveRoundState() != RR_ROUNDSTATE_ACTIVE ) {" in client_c
	assert "if ( !Team_HasMinimumPlayersForWarmup() ) {" in client_c
	assert "G_FreezeRunFrame();" in client_c
	assert "level.rrRoundState = RR_ROUNDSTATE_COMPLETE;" in client_c
	assert "level.rrPendingRoundState = level.rrPendingMatchExit ? RR_ROUNDSTATE_EXIT : nextState;" in client_c


def test_red_rover_autojoin_helper_routes_team_selection() -> None:
	cmds_c = _read("src/code/game/g_cmds.c")

	assert "static team_t G_RRResolveAutoJoinTeam( int clientNum ) {" in cmds_c
	assert "if ( g_gametype.integer != GT_RED_ROVER || !g_rrInfected.integer ) {" in cmds_c
	assert "G_RRResolveRoundState();" in cmds_c
	assert "if ( clientNum == level.rrSelectedInfectedClientNum" in cmds_c
	assert "|| clientNum == level.rrCarryoverInfectedClientNum ) {" in cmds_c
	assert "team = G_RRResolveAutoJoinTeam( clientNum );" in cmds_c


def test_spawn_filter_exemption_helper_matches_retail_mapping_notes() -> None:
	spawn_c = _read("src/code/game/g_spawn.c")

	assert "static qboolean G_SpawnClassExemptFromSpawnFilter( const char *classname ) {" in spawn_c
	assert 'if ( !Q_stricmp( classname, "item_armor_shard" ) ) {' in spawn_c
	assert 'if ( !Q_stricmp( classname, "team_redobelisk" ) ) {' in spawn_c
	assert 'if ( !Q_stricmp( classname, "team_blueobelisk" ) ) {' in spawn_c
	assert 'spawnFilterExempt = G_SpawnClassExemptFromSpawnFilter( classname );' in spawn_c
	assert 'if ( G_SpawnString( "not_gametype", NULL, &value ) ) {' in spawn_c
	assert "if ( G_SpawnGametypeMatchesFilter( value ) ) {" in spawn_c
