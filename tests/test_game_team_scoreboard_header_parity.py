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


def test_qagame_uses_retail_team_scoreboard_headers_without_legacy_outer_prefix() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "static qboolean G_BuildTeamScoreboardMessage( char *payload, int payloadSize, int *emittedCount )" in game_cmds
	assert "static qboolean G_BuildCTFStyleScoreboardMessage( gentity_t *viewer, char *payload, int payloadSize, int *emittedCount )" in game_cmds
	assert "static qboolean G_BuildFreezeScoreboardMessage( char *payload, int payloadSize, int *emittedCount )" in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, va( "%s%s", cmd, string ) );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, va( "%s %i %i %i%s",' in game_cmds


def test_attack_and_defend_uses_dedicated_scoreboard_command() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "case GT_ATTACK_DEFEND:" in game_cmds
	assert 'cmd = "scores_ad";' in game_cmds


def test_ctf_scoreboard_hides_opposing_team_header_for_live_team_viewers() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "static void G_ApplyRetailCTFEnemyHeaderSuppression( const gentity_t *viewer, int teamValues[2][RETAIL_CTF_TEAMSTAT_COUNT] )" in game_cmds
	assert "if ( !viewer || !viewer->client || level.intermissiontime ) {" in game_cmds
	assert "viewerTeam = viewer->client->sess.sessionTeam;" in game_cmds
	assert "enemyTeamIndex = ( viewerTeam == TEAM_RED ) ? 1 : 0;" in game_cmds
	assert "if ( statIndex == 8 || statIndex == 10 || statIndex == 16 ) {" in game_cmds
	assert "G_ApplyRetailCTFEnemyHeaderSuppression( viewer, teamValues );" in game_cmds


def test_qagame_emits_retail_team_family_scoreboard_row_fields() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "static qboolean G_BuildTdmScoreboardRows( char *payload, int payloadSize, int *emittedCount ) {" in game_cmds
	assert "cl->killCount," in game_cmds
	assert "cl->deathCount," in game_cmds
	assert "G_GetClientScoreboardAccuracy( cl )," in game_cmds
	assert "G_GetClientScoreboardWeapon( cl )," in game_cmds
	assert "cl->teamDamageEventsGiven," in game_cmds
	assert "cl->teamDamageEventsReceived," in game_cmds
	assert "cl->pers.damageGiven );" in game_cmds

	assert "static qboolean G_BuildCtfScoreboardRows( char *payload, int payloadSize, int *emittedCount ) {" in game_cmds
	assert "cl->ps.persistant[PERS_DEFEND_COUNT]," in game_cmds
	assert "cl->ps.persistant[PERS_ASSIST_COUNT]," in game_cmds
	assert "cl->ps.persistant[PERS_CAPTURES]," in game_cmds
	assert "perfect," in game_cmds
	assert "(cl->ps.pm_type == PM_NORMAL) ? 1 : 0 );" in game_cmds

	assert "static qboolean G_BuildFreezeScoreboardRows( char *payload, int payloadSize, int *emittedCount ) {" in game_cmds
	assert "cl->ps.persistant[PERS_ASSIST_COUNT]," in game_cmds
	assert "cl->teamDamageEventsGiven," in game_cmds
	assert "cl->teamDamageEventsReceived," in game_cmds
	assert "cl->pers.damageGiven," in game_cmds


def test_cgame_parses_retail_team_scoreboard_header_layouts() -> None:
	servercmds = _read("src/code/cgame/cg_servercmds.c")
	local = _read("src/code/cgame/cg_local.h")

	assert "#define CG_RETAIL_TDM_TEAMSTAT_COUNT\t14" in servercmds
	assert "#define CG_RETAIL_CTF_TEAMSTAT_COUNT\t17" in servercmds
	assert "#define CG_RETAIL_TDM_SCORE_ROW_FIELDS\t15" in servercmds
	assert "#define CG_RETAIL_CTF_SCORE_ROW_FIELDS\t17" in servercmds
	assert "#define CG_RETAIL_FREEZE_SCORE_ROW_FIELDS\t17" in servercmds
	assert "kills;" in local
	assert "bestWeapon;" in local
	assert "teamDamageGiven;" in local
	assert "teamDamageReceived;" in local
	assert "activePlayer;" in local
	assert "CG_ParseRetailTeamScoreHeader( 1, cgRetailTdmTeamStatOrder, CG_RETAIL_TDM_TEAMSTAT_COUNT );" in servercmds
	assert "cg.numScores = atoi( CG_Argv( 29 ) );" in servercmds
	assert "cg.teamScores[0] = atoi( CG_Argv( 30 ) );" in servercmds
	assert "cg.teamScores[1] = atoi( CG_Argv( 31 ) );" in servercmds
	assert "CG_ParseRetailTdmScoreRows( 32 );" in servercmds
	assert "CG_ParseRetailTeamScoreHeader( 1, cgRetailCtfTeamStatOrder, CG_RETAIL_CTF_TEAMSTAT_COUNT );" in servercmds
	assert "cg.numScores = atoi( CG_Argv( 35 ) );" in servercmds
	assert "cg.teamScores[0] = atoi( CG_Argv( 36 ) );" in servercmds
	assert "cg.teamScores[1] = atoi( CG_Argv( 37 ) );" in servercmds
	assert "CG_ParseRetailCtfScoreRows( 38 );" in servercmds
	assert "static void CG_ParseFreezeScores( void ) {" in servercmds
	assert "CG_ParseRetailFreezeScoreRows( 32 );" in servercmds
	assert 'if ( !strcmp( cmd, "scores_tdm" ) ) {' in servercmds
	assert 'if ( !strcmp( cmd, "scores_ctf" ) ) {' in servercmds
	assert 'if ( !strcmp( cmd, "scores_ft" ) ) {' in servercmds
	assert "CG_ParseFreezeScores();" in servercmds
	assert 'if ( !strcmp( cmd, "scores_ad" ) ) {' in servercmds


def test_cgame_maps_retail_team_scoreboard_rows_into_score_t_fields() -> None:
	servercmds = _read("src/code/cgame/cg_servercmds.c")

	assert "static void CG_ParseRetailTdmScoreRows( int rowStartArg ) {" in servercmds
	assert "cg.scores[i].kills = atoi( CG_Argv( baseArg + 5 ) );" in servercmds
	assert "cg.scores[i].deaths = atoi( CG_Argv( baseArg + 6 ) );" in servercmds
	assert "cg.scores[i].accuracy = atoi( CG_Argv( baseArg + 7 ) );" in servercmds
	assert "cg.scores[i].bestWeapon = atoi( CG_Argv( baseArg + 8 ) );" in servercmds
	assert "cg.scores[i].impressiveCount = atoi( CG_Argv( baseArg + 9 ) );" in servercmds
	assert "cg.scores[i].excellentCount = atoi( CG_Argv( baseArg + 10 ) );" in servercmds
	assert "cg.scores[i].guantletCount = atoi( CG_Argv( baseArg + 11 ) );" in servercmds
	assert "cg.scores[i].teamDamageGiven = atoi( CG_Argv( baseArg + 12 ) );" in servercmds
	assert "cg.scores[i].teamDamageReceived = atoi( CG_Argv( baseArg + 13 ) );" in servercmds
	assert "cg.scores[i].damage = atoi( CG_Argv( baseArg + 14 ) );" in servercmds

	assert "static void CG_ParseRetailCtfScoreRows( int rowStartArg ) {" in servercmds
	assert "cg.scores[i].defendCount = atoi( CG_Argv( baseArg + 12 ) );" in servercmds
	assert "cg.scores[i].assistCount = atoi( CG_Argv( baseArg + 13 ) );" in servercmds
	assert "cg.scores[i].captures = atoi( CG_Argv( baseArg + 14 ) );" in servercmds
	assert "cg.scores[i].perfect = atoi( CG_Argv( baseArg + 15 ) );" in servercmds
	assert "cg.scores[i].activePlayer = atoi( CG_Argv( baseArg + 16 ) ) ? qtrue : qfalse;" in servercmds

	assert "static void CG_ParseRetailFreezeScoreRows( int rowStartArg ) {" in servercmds
	assert "cg.scores[i].assistCount = atoi( CG_Argv( baseArg + 12 ) );" in servercmds
	assert "cg.scores[i].teamDamageGiven = atoi( CG_Argv( baseArg + 13 ) );" in servercmds
	assert "cg.scores[i].teamDamageReceived = atoi( CG_Argv( baseArg + 14 ) );" in servercmds
	assert "cg.scores[i].damage = atoi( CG_Argv( baseArg + 15 ) );" in servercmds
	assert "cg.scores[i].activePlayer = atoi( CG_Argv( baseArg + 16 ) ) ? qtrue : qfalse;" in servercmds


def test_selected_player_best_weapon_prefers_retail_scoreboard_row_weapon() -> None:
	newdraw = _read("src/code/cgame/cg_newdraw.c")
	best_weapon_block = _block_from_marker(newdraw, "static void CG_DrawSelectedPlayerBestWeapon")
	resolve_weapon_block = _block_from_marker(newdraw, "static const char *CG_ResolveWeaponName")

	assert "weapon = score->bestWeapon;" in best_weapon_block
	assert "weaponName = CG_ResolveWeaponName( weapon );" in best_weapon_block
	assert "CG_Text_Paint(rect->x, rect->y, scale, color, weaponName, 0, 0, textStyle);" in best_weapon_block
	assert "weapon = cent->currentState.weapon;" not in best_weapon_block
	assert '"Unknown"' not in best_weapon_block
	assert "rect->y + rect->h" not in best_weapon_block

	for expected in (
		'return "Grenade";',
		'return "Rail Gun";',
		'return "BFG";',
		'return "Nail Gun";',
		'return "Proximity Mines";',
		'return "Chain Gun";',
		'return "Heavy Machinegun";',
	):
		assert expected in resolve_weapon_block
