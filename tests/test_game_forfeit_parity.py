from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_cmd_forfeit_is_now_a_thin_gate() -> None:
	cmds_c = _read("src/code/game/g_cmds.c")

	start = cmds_c.index("void Cmd_Forfeit_f( gentity_t *ent ) {")
	end = cmds_c.index("/*\n=================\nBroadCastTeamChange", start)
	cmd_block = cmds_c[start:end]

	assert "Forfeit is not available during a pause or timeout." in cmd_block
	assert "Forfeit is not available during a round countdown." in cmd_block
	assert "if ( G_CanForfeit( ent, qtrue ) ) {" in cmd_block
	assert "G_ApplyForfeit();" in cmd_block
	assert "Forfeits are not enabled on this server." not in cmd_block
	assert "Forfeit is not available in warmup." not in cmd_block


def test_forfeit_eligibility_helper_is_shared_with_exit_rules() -> None:
	cmds_c = _read("src/code/game/g_cmds.c")
	main_c = _read("src/code/game/g_main.c")

	assert "qboolean G_CanForfeit( gentity_t *ent, qboolean fromCommand ) {" in cmds_c

	check_exit_start = main_c.index("void CheckExitRules( void ) {")
	check_exit_end = main_c.index("/*", check_exit_start + 1)
	check_exit_block = main_c[check_exit_start:check_exit_end]

	assert "if ( G_CanForfeit( NULL, qfalse ) ) {" in check_exit_block
	assert "G_ApplyForfeit();" in check_exit_block


def test_duel_forfeit_gate_marks_surrendering_player_before_shared_executor() -> None:
	cmds_c = _read("src/code/game/g_cmds.c")

	start = cmds_c.index("qboolean G_CanForfeit( gentity_t *ent, qboolean fromCommand ) {")
	end = cmds_c.index("/*\n=============\nCmd_Kill_f", start)
	can_forfeit_block = cmds_c[start:end]
	tournament_start = can_forfeit_block.index("if ( gametype == GT_TOURNAMENT ) {")
	tournament_block = can_forfeit_block[tournament_start:]

	assert "ent->client->ps.persistant[PERS_SCORE] = -999;" in tournament_block
	assert tournament_block.index("ent->client->ps.persistant[PERS_SCORE] = -999;") < tournament_block.index("return qtrue;")
	assert "G_ApplyForfeit();" not in can_forfeit_block


def test_g_apply_forfeit_marks_only_the_losing_side() -> None:
	main_c = _read("src/code/game/g_main.c")

	start = main_c.index("void G_ApplyForfeit( void ) {")
	end = main_c.index("/*", start + 1)
	apply_block = main_c[start:end]

	assert "level.teamScores[losingTeam] = -999;" in apply_block
	assert "level.teamScores[TEAM_RED] = -999;" not in apply_block
	assert "level.teamScores[TEAM_BLUE] = -999;" not in apply_block
	assert "player_die(" not in apply_block
	assert "CalculateRanks();" in apply_block
	assert 'LogExit( "Players have forfeited." );' in apply_block


def test_legacy_g_handleforfeit_wrapper_is_removed() -> None:
	local_h = _read("src/code/game/g_local.h")
	main_c = _read("src/code/game/g_main.c")

	assert "G_HandleForfeit" not in local_h
	assert "G_HandleForfeit" not in main_c
