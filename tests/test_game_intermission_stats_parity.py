from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _block(text: str, start_marker: str, end_marker: str) -> str:
	start = text.index(start_marker)
	end = text.index(end_marker, start)
	return text[start:end]


def test_qagame_emits_retail_tdmstats_rows_during_tdm_family_intermission() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "static void G_SendTDMStatsMessage( gentity_t *ent ) {" in game_cmds
	assert 'trap_SendServerCommand( ent - g_entities, va( "tdmstats %i%s", i, payload ) );' in game_cmds
	assert "if ( g_gametype.integer == GT_TEAM || g_gametype.integer == GT_FREEZE ) {" in game_cmds
	assert "G_SendTDMStatsMessage( ent );" in game_cmds


def test_qagame_emits_retail_ctfstats_rows_for_ctf_style_intermission() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "static qboolean G_IsCTFStyleScoreboardGametype( void ) {" in game_cmds
	assert "case GT_CTF:" in game_cmds
	assert "case GT_1FCTF:" in game_cmds
	assert "case GT_HARVESTER:" in game_cmds
	assert "case GT_DOMINATION:" in game_cmds
	assert "case GT_ATTACK_DEFEND:" in game_cmds
	assert "static void G_SendCTFStatsMessage( gentity_t *ent ) {" in game_cmds
	assert 'trap_SendServerCommand( ent - g_entities, va( "ctfstats %i%s", i, payload ) );' in game_cmds
	assert "if ( G_IsCTFStyleScoreboardGametype() ) {" in game_cmds
	assert "G_SendCTFStatsMessage( ent );" in game_cmds


def test_qagame_intermission_stat_rows_follow_retail_pickup_and_damage_order() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	tdm_block = _block(
		game_cmds,
		"static void G_SendTDMStatsMessage( gentity_t *ent ) {",
		"static void G_SendCTFStatsMessage( gentity_t *ent ) {",
	)
	ctf_block = _block(
		game_cmds,
		"static void G_SendCTFStatsMessage( gentity_t *ent ) {",
		"static void G_CopyRetailTeamScoreboardHeaderValues",
	)

	assert "values[0] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_BS];" in tdm_block
	assert "values[1] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_QUAD];" in tdm_block
	assert "values[2] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_MH];" in tdm_block
	assert "values[3] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_GA];" in tdm_block
	assert "values[4] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_YA];" in tdm_block
	assert "values[5] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_RA];" in tdm_block
	assert "values[6] = cl->pers.damageReceived;" in tdm_block
	assert "values[7] = cl->pers.damageGiven;" in tdm_block
	assert "values[8] = cl->teamDamageEventsReceived;" in tdm_block
	assert "values[9] = cl->teamDamageEventsGiven;" in tdm_block
	assert "values[10] = cl->environmentalDeaths;" in tdm_block
	assert "G_GetClientTeamHoldStatSeconds" not in tdm_block

	assert "values[0] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_INVIS];" in ctf_block
	assert "values[1] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_HASTE];" in ctf_block
	assert "values[2] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_REGEN];" in ctf_block
	assert "values[3] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_BS];" in ctf_block
	assert "values[4] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_QUAD];" in ctf_block
	assert "values[5] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_MH];" in ctf_block
	assert "values[6] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_GA];" in ctf_block
	assert "values[7] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_YA];" in ctf_block
	assert "values[8] = cl->pers.teamScoreStats[TEAMSTAT_PICKUPS_RA];" in ctf_block
	assert "values[9] = cl->pers.damageReceived;" in ctf_block
	assert "values[10] = cl->pers.damageGiven;" in ctf_block
	assert "values[11] = cl->environmentalDeaths;" in ctf_block
	assert "cl->pers.teamState." not in ctf_block


def test_deathmatch_scoreboard_message_orders_intermission_publishers_after_score_payloads() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	scoreboard_block = _block(
		game_cmds,
		"void DeathmatchScoreboardMessage( gentity_t *ent ) {",
		"void Cmd_Score_f( gentity_t *ent ) {",
	)

	assert scoreboard_block.index("G_SendScoreStatsMessage( ent );") < scoreboard_block.index("G_SendTeamScoreStatsMessage( ent );")
	assert scoreboard_block.index("G_SendTeamScoreStatsMessage( ent );") < scoreboard_block.index("if ( level.intermissiontime ) {")
	assert scoreboard_block.index("if ( level.intermissiontime ) {") < scoreboard_block.index("G_SendAllClientKeyMasks( ent - g_entities );")


def test_cgame_caches_and_parses_retail_tdm_and_ctf_intermission_stats() -> None:
	servercmds = _read("src/code/cgame/cg_servercmds.c")
	local = _read("src/code/cgame/cg_local.h")

	assert "#define CG_TDMSTAT_FIELD_COUNT\t11" in local
	assert "#define CG_CTFSTAT_FIELD_COUNT\t12" in local
	assert "cgTdmStats_t\ttdmStats[MAX_CLIENTS];" in local
	assert "cgCtfStats_t\tctfStats[MAX_CLIENTS];" in local

	assert "static void CG_ClearTDMStatsCache( void ) {" in servercmds
	assert "static void CG_ClearCTFStatsCache( void ) {" in servercmds
	assert "static void CG_ParseTDMStats( void ) {" in servercmds
	assert "static void CG_ParseCTFStats( void ) {" in servercmds
	assert "row = &cg.tdmStats[rowIndex];" in servercmds
	assert "row = &cg.ctfStats[rowIndex];" in servercmds
	assert "CG_ClearTDMStatsCache();" in servercmds
	assert "CG_ClearCTFStatsCache();" in servercmds
	assert 'if ( !strcmp( cmd, "tdmstats" ) ) {' in servercmds
	assert "CG_ParseTDMStats();" in servercmds
	assert 'if ( !strcmp( cmd, "ctfstats" ) ) {' in servercmds
	assert "CG_ParseCTFStats();" in servercmds


def test_team_damage_event_counters_are_tracked_for_retail_intermission_stats() -> None:
	game_local = _read("src/code/game/g_local.h")
	game_combat = _read("src/code/game/g_combat.c")

	assert "teamDamageEventsGiven" in game_local
	assert "teamDamageEventsReceived" in game_local
	assert "environmentalDeaths" in game_local
	assert "attacker->client->teamDamageEventsGiven++;" in game_combat
	assert "targ->client->teamDamageEventsReceived++;" in game_combat
	assert "self->client->environmentalDeaths++;" in game_combat
