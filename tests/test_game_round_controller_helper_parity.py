from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_clan_arena_round_controller_helpers_match_retail_mapping_surface() -> None:
	active_c = _read("src/code/game/g_active.c")
	client_c = _read("src/code/game/g_client.c")
	combat_c = _read("src/code/game/g_combat.c")
	local_h = _read("src/code/game/g_local.h")
	team_c = _read("src/code/game/g_team.c")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt")

	assert "int G_CAResolveRoundState( void ) {" in active_c
	assert "static int CA_RoundStateTransition( qboolean announce ) {" in active_c
	assert "void G_SetClientAttackLockout( gentity_t *ent, qboolean lockout ) {" in active_c
	assert "void G_SetAllActiveClientAttackLockout( qboolean lockout ) {" in active_c
	assert "G_SetClientAttackLockout( ent, lockout );" in active_c
	assert "if ( g_gametype.integer == GT_CLAN_ARENA ) {" in active_c
	assert "CA_RoundStateTransition( qtrue );" in active_c
	assert "level.roundPendingExit = G_CAFZCheckExitRules( qfalse );" in active_c
	assert "static void G_CASendRoundWinnerPrint( team_t winner, const int counts[TEAM_NUM_TEAMS], const int health[TEAM_NUM_TEAMS] ) {" in active_c
	assert 'print \\"%s%s TEAM^3 WINS the round!^7 (%i hp remaining)\\n\\"' in active_c
	assert 'print \\"%s%s TEAM^3 WINS the round!^7 (%i players remaining)\\n\\"' in active_c
	assert 'print \\"%s%s TEAM^3 WINS the round!^7 (%s%i^7 hp vs %s%i^7 hp)\\n\\"' in active_c
	assert 'G_Error( "CA_RoundStateTransition: invalid state" );' in active_c
	assert "G_SetAllActiveClientAttackLockout( qtrue );" in active_c
	assert "G_SetAllActiveClientAttackLockout( qfalse );" in active_c
	assert "state = G_CAResolveRoundState();" in team_c
	assert "G_SetClientAttackLockout( ent, qtrue );" in team_c
	assert "G_SetClientAttackLockout( ent, qfalse );" in team_c
	assert "caState = G_CAResolveRoundState();" in client_c
	assert "qboolean G_CAHandleDamageScore( gentity_t *attacker, gentity_t *targ, int *take, int *asave );" in local_h
	assert "qboolean G_CAHandleDamageScore( gentity_t *attacker, gentity_t *targ, int *take, int *asave ) {" in team_c
	assert "if ( G_CAResolveRoundState() != ROUNDSTATE_ACTIVE ) {" in team_c
	assert "if ( cappedTake > targ->health ) {" in team_c
	assert "if ( cappedArmor > targ->client->ps.stats[STAT_ARMOR] ) {" in team_c
	assert "if ( !attacker->client || !targ->client || attacker == targ || OnSameTeam( attacker, targ ) ) {" in team_c
	assert "attacker->client->adAccumulatedDamage += damage;" in team_c
	assert "while ( attacker->client->adAccumulatedDamage >= 100 ) {" in team_c
	assert "attacker->client->ps.persistant[PERS_SCORE] += 1;" in team_c
	assert "CalculateRanks();" in team_c
	assert "if ( g_gametype.integer == GT_CLAN_ARENA ) {" in combat_c
	assert "if ( !G_CAHandleDamageScore( attacker, targ, &take, &asave ) ) {" in combat_c
	assert "10037fd0    int32_t sub_10037fd0" in qagame_hlil
	assert "100380b2          edx = sub_10038230(arg2)" in qagame_hlil
	assert "1003811e                  *(eax_10 + 0x328) += ecx_8 + edx_2" in qagame_hlil
	assert "10038140                      *(eax_12 + 0x100) += 1" in qagame_hlil


def test_round_waiting_warmup_releases_pre_round_weapon_lockout() -> None:
	active_c = _read("src/code/game/g_active.c")

	assert "static void G_Frame_ReleaseWaitingWarmupClients( void ) {" in active_c
	assert "ent->client->ps.pm_type == PM_FREEZE && !ent->client->freezeFrozen" in active_c
	assert "G_SetClientAttackLockout( ent, qfalse );" in active_c
	assert active_c.count("G_Frame_ReleaseWaitingWarmupClients();") >= 5


def test_freeze_round_controller_helpers_match_retail_mapping_surface() -> None:
	active_c = _read("src/code/game/g_active.c")
	client_c = _read("src/code/game/g_client.c")
	freeze_c = _read("src/code/game/g_freeze.c")
	main_c = _read("src/code/game/g_main.c")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt")

	assert "int G_FreezeResolveRoundState( void ) {" in active_c
	assert "static qboolean G_FreezeShouldCompleteRound( const int counts[TEAM_NUM_TEAMS] ) {" in active_c
	assert "static team_t G_FreezeEvaluateRoundWinner( const int counts[TEAM_NUM_TEAMS], const int health[TEAM_NUM_TEAMS] ) {" in active_c
	assert "static void G_FreezeRespawnThawedWinner( gentity_t *ent ) {" in active_c
	assert "G_FreezeRespawnThawedWinner( ent );" in active_c
	assert "tent = G_TempEntity( ent->client->ps.origin, EV_THAW_PLAYER );" in active_c
	assert "ent->client->ps.pm_type = PM_NORMAL;" in active_c
	assert "ClientSpawn( ent );" in active_c
	assert "void G_RoundHandleWarmupDelayCvarUpdate( void ) {" in active_c
	assert "return G_RoundTimeLimitExpired( level.roundStartTime );" in active_c
	assert "level.roundPendingExit = G_CAFZCheckExitRules( qfalse );" in active_c
	assert "mercyLimitMsec = G_BuildExitRuleLimitMsec( g_mercytime.integer, level.overtimeAccumulatedMsec );" in active_c
	assert "if ( level.teamScores[TEAM_RED] >= roundlimit.integer ) {" in active_c
	assert "&& level.teamScores[TEAM_RED] > level.teamScores[TEAM_BLUE]" not in active_c
	assert "switch ( level.roundState ) {" in active_c
	assert "state = G_FreezeResolveRoundState();" in active_c
	assert active_c.index("G_FreezeRecountLivingClients();") < active_c.index("if ( !G_FreezeShouldCompleteRound( level.freezeLivingCount ) ) {")
	assert active_c.index("if ( !G_FreezeShouldCompleteRound( level.freezeLivingCount ) ) {") < active_c.index("winner = G_FreezeEvaluateRoundWinner( level.freezeLivingCount, level.freezeLivingHealth );")
	assert "if ( !G_FreezeShouldCompleteRound( level.freezeLivingCount ) ) {" in active_c
	assert "winner = G_FreezeEvaluateRoundWinner( level.freezeLivingCount, level.freezeLivingHealth );" in active_c
	assert "G_SetAllActiveClientAttackLockout( qtrue );" in active_c
	assert "G_SetAllActiveClientAttackLockout( qfalse );" in active_c
	assert "Freeze_RoundStateTransition( qtrue );" in active_c
	freeze_handle_index = active_c.index("static void G_FreezeHandleRoundEnd( team_t winner ) {")
	freeze_rank_index = active_c.index("CalculateRanks();", freeze_handle_index)
	assert active_c.index("trap_SetConfigstring( CS_SCORES1", freeze_handle_index) < freeze_rank_index
	assert active_c.index("level.freezeLivingHealth[TEAM_RED]", freeze_handle_index) < freeze_rank_index
	assert freeze_rank_index < active_c.index("level.roundState = ROUNDSTATE_COMPLETE;", freeze_handle_index)
	assert "if ( G_FreezeResolveRoundState() != ROUNDSTATE_ACTIVE ) {" in freeze_c
	assert "roundState = G_FreezeResolveRoundState();" in client_c
	assert "client->freezeThawHelperActive = qfalse;" in client_c
	assert "client->freezeThawTimeRemaining = thawTotal;" in client_c
	assert "client->freezeAutoThawTime = 0;" in client_c
	assert "freezeThawHelperActive" in freeze_c
	assert "freezeThawTimeRemaining" in freeze_c
	assert "trap_EntitiesInBox( mins, maxs, entityList, MAX_GENTITIES );" in freeze_c
	assert "for ( i = 0; i < level.maxclients; i++ )" not in freeze_c
	assert "freezeNextThawTick" not in main_c
	assert "client->freezeProtectedUntil = G_ShiftTimeoutAbsoluteTime( client->freezeProtectedUntil, msec );" in main_c
	assert "1004c619                      *(*ecx_20 + 0xbcc) = 0" in qagame_hlil
	assert "1004c621                      *(*ecx_20 + 0xbc8) = 0" in qagame_hlil
	assert "1004c629                      *(*ecx_20 + 0xbc4) = 0" in qagame_hlil
	assert "1004c8df                      int32_t ecx_31 = *(eax_69 + 0xbc4)" in qagame_hlil
	assert '1004c92c                              "ACCURACY")' in qagame_hlil
	assert "1004c949                      if (*(eax_75 + 0x348) == ebx_1 && *(eax_75 + 0xbcc) == 0)" in qagame_hlil
	assert '1004c96e                              "PERFECT")' in qagame_hlil
	assert "1004c99b          sub_10056070()" in qagame_hlil


def test_red_rover_controller_readback_helpers_match_retail_mapping_surface() -> None:
	active_c = _read("src/code/game/g_active.c")
	client_c = _read("src/code/game/g_client.c")
	combat_c = _read("src/code/game/g_combat.c")
	cmds_c = _read("src/code/game/g_cmds.c")
	local_h = _read("src/code/game/g_local.h")
	rr_c = _read("src/code/game/g_rr.c")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt")
	build_inputs = [
		"tools/ci/build-posix-native.sh",
		"src/code/game/game.sh",
		"src/code/game/game_ta.sh",
		"src/code/game/game.vcxproj",
		"src/code/game/qagamex86.vcxproj",
	]

	assert "int G_RRResolveRoundState( void ) {" in active_c
	assert "static int RR_RoundStateTransition( qboolean announce ) {" in active_c
	assert "G_SetAllActiveClientAttackLockout( qtrue );" in active_c
	assert "G_SetAllActiveClientAttackLockout( qfalse );" in active_c
	assert "G_RRInitRoundController();" in active_c
	assert "RR_RoundStateTransition( qtrue );" in active_c
	assert "if ( level.warmupTime < 0 ) {" in active_c
	assert "G_RRResetClientForRound( ent );" in active_c
	assert "G_RRResetClientForRound( infectedClient );" in active_c
	assert "RR_ROUNDSTATE_INFECTION_SEED = 2," in local_h
	assert "RR_ROUNDSTATE_EXIT = 5" in local_h
	assert "void G_RRInitRoundController( void );" in local_h
	assert "void G_RRResetClientForRound( gentity_t *ent );" in local_h
	assert "qboolean G_RRHandleDamageScore( gentity_t *attacker, gentity_t *targ, int *take, int *asave );" in local_h
	assert "level.rrPendingRoundState = RR_ROUNDSTATE_ACTIVE;" in active_c
	assert "state == RR_ROUNDSTATE_INACTIVE && level.roundTransitionTime == ROUND_TRANSITION_NONE" in active_c
	assert "state == RR_ROUNDSTATE_ACTIVE || state == RR_ROUNDSTATE_INFECTION_SEED" in active_c
	assert 'G_Error( "RR_RoundStateTransition: invalid state" );' in active_c
	assert "G_RRResolveRoundState();" in cmds_c
	assert "if ( G_RRResolveRoundState() != RR_ROUNDSTATE_ACTIVE ) {" in client_c
	assert "void G_RRResetClientForRound( gentity_t *ent ) {" in client_c
	assert "qboolean G_RRHandleDamageScore( gentity_t *attacker, gentity_t *targ, int *take, int *asave ) {" in client_c
	assert "if ( cappedTake > targ->health ) {" in client_c
	assert "if ( cappedArmor > targ->client->ps.stats[STAT_ARMOR] ) {" in client_c
	assert "while ( attacker->client->rrAccumulatedDamage >= 100 ) {" in client_c
	assert "G_RRApplyRawScoreDelta( attacker, bonus );" in client_c
	assert "if ( g_gametype.integer == GT_RED_ROVER ) {" in combat_c
	assert "if ( !G_RRHandleDamageScore( attacker, targ, &take, &asave ) ) {" in combat_c
	assert "if ( !Team_HasMinimumPlayersForWarmup() ) {" in client_c
	assert "G_FreezeRunFrame();" in client_c
	assert "level.rrRoundState = RR_ROUNDSTATE_COMPLETE;" in client_c
	assert "G_SetAllActiveClientAttackLockout( qtrue );" in client_c
	assert "level.rrPendingRoundState = level.rrPendingMatchExit ? RR_ROUNDSTATE_EXIT : nextState;" in client_c
	assert "Red Rover has no standalone retail translation unit" in rr_c
	assert "G_RRHandleDamageScore(" not in rr_c
	for rel_path in build_inputs:
		assert "g_rr.c" not in _read(rel_path)
	assert "100643e0    int32_t sub_100643e0" in qagame_hlil
	assert "100644c2          st0_1, edx = sub_100649f0(arg2)" in qagame_hlil
	assert "10064542                  *(eax_10 + 0x328) += ecx_8 + edx_2" in qagame_hlil
	assert "1006456a                      *(eax_12 + 0x100) += data_1059eaec" in qagame_hlil


def test_red_rover_autojoin_helper_routes_team_selection() -> None:
	cmds_c = _read("src/code/game/g_cmds.c")

	assert "static team_t G_RRResolveAutoJoinTeam( int clientNum ) {" in cmds_c
	assert "if ( g_gametype.integer != GT_RED_ROVER || !g_rrInfected.integer ) {" in cmds_c
	assert "G_RRResolveRoundState();" in cmds_c
	assert "if ( clientNum == level.rrSelectedInfectedClientNum" in cmds_c
	assert "|| clientNum == level.rrCarryoverInfectedClientNum ) {" in cmds_c
	assert "} else if ( g_gametype.integer == GT_RED_ROVER ) {" in cmds_c
	assert "team = G_RRResolveAutoJoinTeam( clientNum );" in cmds_c
	assert cmds_c.index("} else if ( g_gametype.integer == GT_RED_ROVER ) {") < cmds_c.index("} else if ( g_gametype.integer >= GT_TEAM ) {")


def test_spawn_filter_exemption_helper_matches_retail_mapping_notes() -> None:
	spawn_c = _read("src/code/game/g_spawn.c")

	assert "static qboolean G_SpawnClassExemptFromSpawnFilter( const char *classname ) {" in spawn_c
	assert 'if ( !Q_stricmp( classname, "item_armor_shard" ) ) {' in spawn_c
	assert 'if ( !Q_stricmp( classname, "team_redobelisk" ) ) {' in spawn_c
	assert 'if ( !Q_stricmp( classname, "team_blueobelisk" ) ) {' in spawn_c
	assert 'spawnFilterExempt = G_SpawnClassExemptFromSpawnFilter( classname );' in spawn_c
	assert 'if ( G_SpawnString( "not_gametype", NULL, &value ) ) {' in spawn_c
	assert "if ( G_SpawnGametypeMatchesFilter( value ) ) {" in spawn_c
