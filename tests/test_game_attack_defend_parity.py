from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_attack_defend_helper_surface_matches_retail_mapping_bundle() -> None:
	local_h = _read("src/code/game/g_local.h")
	team_c = _read("src/code/game/g_team.c")

	assert "typedef enum {" in local_h
	assert "AD_ROUNDSTATE_ACTIVE = 3" in local_h
	assert "AD_ROUNDSTATE_COMPLETE = 4" in local_h
	assert "AD_ROUNDSTATE_EXIT = 5" in local_h
	assert "int G_ADResolveRoundState( void );" in local_h
	assert "qboolean G_ADHandleDamageScore( gentity_t *attacker, int announce, gentity_t *targ, int *take, int *asave );" in local_h
	assert "qboolean G_ADCheckExitRules( qboolean announce );" in local_h
	assert "int AD_RoundStateTransition( qboolean announce );" in local_h
	assert "int G_ADResolveAttackingTeam( void );" in local_h
	assert "int G_ADResolveDefendingTeam( void );" in local_h
	assert "int G_ADResetScoreHistory( void );" in local_h
	assert "int G_ADUpdateScoreHistory( void );" in local_h
	assert "void G_CAADRespawnAsSpectator( gentity_t *ent );" in local_h
	assert "void G_CAADResetClientForRound( gentity_t *ent );" in local_h
	assert "adRoundState;" in local_h
	assert "adPendingRoundState;" in local_h
	assert "adScoreHistory[AD_SCORE_HISTORY_LENGTH];" in local_h
	assert "adPublishedScoreHistory[AD_SCORE_HISTORY_LENGTH];" in local_h
	assert "adAccumulatedDamage;" in local_h

	assert "int G_ADResolveRoundState( void ) {" in team_c
	assert "qboolean G_ADHandleDamageScore( gentity_t *attacker, int announce, gentity_t *targ, int *take, int *asave ) {" in team_c
	assert "qboolean G_ADCheckExitRules( qboolean announce ) {" in team_c
	assert "int AD_RoundStateTransition( qboolean announce ) {" in team_c
	assert "int G_ADResolveAttackingTeam( void ) {" in team_c
	assert "int G_ADResolveDefendingTeam( void ) {" in team_c
	assert "int G_ADResetScoreHistory( void ) {" in team_c
	assert "int G_ADUpdateScoreHistory( void ) {" in team_c
	assert "void G_CAADRespawnAsSpectator( gentity_t *ent ) {" in team_c
	assert "void G_CAADResetClientForRound( gentity_t *ent ) {" in team_c


def test_attack_defend_round_controller_hooks_use_retail_boundaries() -> None:
	active_c = _read("src/code/game/g_active.c")
	client_c = _read("src/code/game/g_client.c")
	match_state_c = _read("src/code/game/g_match_state.c")
	main_c = _read("src/code/game/g_main.c")
	cmds_c = _read("src/code/game/g_cmds.c")

	assert "case GT_ATTACK_DEFEND:" in active_c
	assert "static void G_Frame_UpdateAttackDefendRoundController( void ) {" in active_c
	assert "state = G_ADResolveRoundState();" in active_c
	assert "level.adRoundState = AD_ROUNDSTATE_WARMUP;" in active_c
	assert "level.adRoundState = AD_ROUNDSTATE_COMPLETE;" in active_c
	assert "AD_RoundStateTransition( qtrue );" in active_c
	assert "&& ent->client->ps.pm_type == PM_SPECTATOR ) ) {" in active_c

	assert "useRoundFollowReset = ( adState != AD_ROUNDSTATE_INACTIVE && adState != AD_ROUNDSTATE_WARMUP ) ? qtrue : qfalse;" in client_c
	assert "G_CAADResetClientForRound( ent );" in client_c
	assert "ent->client->ps.pm_type != PM_SPECTATOR ) {" in client_c

	assert "case GT_ATTACK_DEFEND:" in match_state_c
	assert "turn = level.adTurnIndex;" in match_state_c

	assert "level.adRoundState = AD_ROUNDSTATE_INACTIVE;" in main_c
	assert "if ( g_gametype.integer == GT_ATTACK_DEFEND ) {" in main_c
	assert "if ( level.adRoundState == AD_ROUNDSTATE_EXIT ) {" in main_c

	assert 'cmd = "scores_ad";' in cmds_c


def test_attack_defend_objective_and_damage_paths_call_retail_helpers() -> None:
	team_c = _read("src/code/game/g_team.c")
	combat_c = _read("src/code/game/g_combat.c")

	assert "if ( G_ADResolveRoundState() != AD_ROUNDSTATE_ACTIVE ) {" in team_c
	assert "attackingTeam = G_ADResolveAttackingTeam();" in team_c
	assert "adDefendingTeam = G_ADResolveDefendingTeam();" in team_c
	assert "level.adRoundWinnerAlreadyScored = qtrue;" in team_c
	assert "level.adRoundState = AD_ROUNDSTATE_COMPLETE;" in team_c
	assert "G_ADUpdateScoreHistory();" in team_c
	assert "G_ADPublishScoreHistory();" in team_c
	assert "mercyLimitMsec = G_BuildExitRuleLimitMsec( g_mercytime.integer, level.overtimeAccumulatedMsec );" in team_c
	assert 'trap_SendServerCommand( -1, "print \\"Red hit the scorelimit.\\n\\"" );' in team_c
	assert 'trap_SendServerCommand( -1, "print \\"Blue hit the mercylimit.\\n\\"" );' in team_c

	assert "G_ADHandleDamageScore( attacker, 0, targ, &take, &asave );" in combat_c
