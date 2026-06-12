from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_duel_scoreboard_cache_fields_match_retail_level_tail() -> None:
	local_h = _read("src/code/game/g_local.h")
	game_types = _read("src/game/ql_game_types.h")

	assert "int\t\t\tduelScoreboardLowClientNum;" in local_h
	assert "int\t\t\tduelScoreboardHighClientNum;" in local_h
	assert "int32_t\tduelScoreboardLowClientNum;" in game_types
	assert "int32_t\tduelScoreboardHighClientNum;" in game_types


def test_nonteam_scoreboard_helper_family_is_split_from_generic_builder() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt")
	level_notes = _read("references/hlil/quakelive/qagamex86.dll/sully_interpreted/structs/level_locals_t.md")

	assert "static qboolean G_BuildObeliskScoreboardMessage( char *payload, int payloadSize, int *emittedCount ) {" in game_cmds
	assert "static qboolean G_BuildFFAScoreboardMessage( char *payload, int payloadSize, int *emittedCount ) {" in game_cmds
	assert "static qboolean G_BuildDuelScoreboardMessage( char *payload, int payloadSize, int *emittedCount ) {" in game_cmds
	assert "static const gentity_t\t*g_duelScoreboardViewer;" in game_cmds
	assert "static qboolean G_BuildClanArenaScoreboardMessage( char *payload, int payloadSize, int *emittedCount ) {" in game_cmds
	assert "static qboolean G_BuildRedRoverScoreboardMessage( char *payload, int payloadSize, int *emittedCount ) {" in game_cmds
	assert "level.duelScoreboardLowClientNum = -1;" in game_cmds
	assert "level.duelScoreboardHighClientNum = -1;" in game_cmds
	assert "level.duelScoreboardLowClientNum = firstClientNum;" in game_cmds
	assert "level.duelScoreboardHighClientNum = secondClientNum;" in game_cmds
	assert "if ( level.intermissionQueued || level.intermissiontime ) {" in game_cmds
	assert "lowRow = G_ShouldRevealDuelScoreboardDetails( g_duelScoreboardViewer, level.duelScoreboardLowClientNum ) ? lowPrivate : lowPublic;" in game_cmds
	assert "1003db06  if (data_105de9d4 != 0 || data_105de9d8 != 0)" in qagame_hlil
	assert '1003db7f      *(esp_1 - 0xc) = "scores_duel 2 %s %s"' in qagame_hlil
	assert "| `0x1B94` | `intermissionQueued`" in level_notes
	assert "| `0x1B98` | `intermissiontime`" in level_notes


def test_race_scoreboard_helper_is_exposed_and_reused() -> None:
	local_h = _read("src/code/game/g_local.h")
	race_c = _read("src/code/game/g_race.c")
	score_block = race_c[
		race_c.index("static void G_RaceBuildScoreString"):
		race_c.index("static gclient_t *G_RaceFindLeader")
	]

	assert "void\tG_BuildRaceScoreboardMessage( gentity_t *ent );" in local_h
	assert "void G_BuildRaceScoreboardMessage( gentity_t *ent ) {" in race_c
	assert "G_RaceBuildScoreString();" in race_c
	assert "count = level.numPlayingClients;" in score_block
	assert "clientNum = level.sortedClients[i];" in score_block
	assert "qsort(" not in score_block
	assert "G_RaceCompareClients" not in race_c
	assert "trap_SendServerCommand( ent - g_entities, g_raceScores );" in race_c
	assert "G_BuildRaceScoreboardMessage( ent );" in race_c


def test_deathmatch_scoreboard_dispatch_uses_retail_nonteam_helpers() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "if ( g_gametype.integer == GT_RACE ) {" in game_cmds
	assert "G_BuildRaceScoreboardMessage( ent );" in game_cmds
	assert "g_duelScoreboardViewer = ent;" in game_cmds
	assert "case GT_OBELISK:" in game_cmds
	assert 'cmd = "scores";' in game_cmds
	assert "useCompact = G_BuildFFAScoreboardMessage( string, sizeof( string ), &emittedCount ) ? qfalse : qtrue;" in game_cmds
	assert "useCompact = G_BuildDuelScoreboardMessage( string, sizeof( string ), &emittedCount ) ? qfalse : qtrue;" in game_cmds
	assert "useCompact = G_BuildObeliskScoreboardMessage( string, sizeof( string ), &emittedCount ) ? qfalse : qtrue;" in game_cmds
	assert "useCompact = G_BuildClanArenaScoreboardMessage( string, sizeof( string ), &emittedCount ) ? qfalse : qtrue;" in game_cmds
	assert "useCompact = G_BuildRedRoverScoreboardMessage( string, sizeof( string ), &emittedCount ) ? qfalse : qtrue;" in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, va( "%s %i%s", cmd, emittedCount, string ) );' in game_cmds
