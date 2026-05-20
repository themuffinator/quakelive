from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _static_array_block(source: str, marker: str) -> str:
	start = source.index(marker)
	end = source.index("};", start)
	return source[start:end]


def test_qagame_uses_compact_smscores_fallback_when_forced_or_overflowing() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "static qboolean G_BuildCompactScoreboardMessage( char *payload, int payloadSize, int *emittedCount )" in game_cmds
	assert "\" %i %i %i %i %i %i %i %i\"" in game_cmds
	assert "useCompact = g_forceSmallScoreboardMessage.integer ? qtrue : qfalse;" in game_cmds
	assert "useCompact = G_BuildRichScoreboardMessage( string, sizeof( string ), &emittedCount ) ? qfalse : qtrue;" in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, va( "smscores %i %i %i%s",' in game_cmds


def test_cgame_parses_smscores_with_compact_row_stride() -> None:
	servercmds = _read("src/code/cgame/cg_servercmds.c")

	assert "static void CG_ParseCompactScores( void ) {" in servercmds
	assert "cg.scores[i].client = atoi( CG_Argv( i * 8 + 4 ) );" in servercmds
	assert "cg.scores[i].scoreFlags = 0;" in servercmds
	assert "cg.scores[i].activePlayer = atoi( CG_Argv( i * 8 + 9 ) ) ? qtrue : qfalse;" in servercmds
	assert "cg.scores[i].damage = atoi( CG_Argv( i * 8 + 10 ) );" in servercmds
	assert "cg.scores[i].deaths = atoi( CG_Argv( i * 8 + 11 ) );" in servercmds
	assert 'if ( !strcmp( cmd, "smscores" ) ) {' in servercmds
	assert "CG_ParseCompactScores();" in servercmds


def test_qagame_emits_retail_castats_rows_during_clan_arena_intermission() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "static void G_SendCAStatsMessage( gentity_t *ent ) {" in game_cmds
	assert 'trap_SendServerCommand( ent - g_entities, va( "castats %i%s", i, payload ) );' in game_cmds
	assert "if ( level.intermissiontime ) {" in game_cmds
	assert "if ( g_gametype.integer == GT_CLAN_ARENA ) {" in game_cmds
	assert "G_SendCAStatsMessage( ent );" in game_cmds


def test_castats_use_retail_weapon_entry_order() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	servercmds = _read("src/code/cgame/cg_servercmds.c")

	for source, marker in (
		(game_cmds, "static const weapon_t castatWeapons"),
		(servercmds, "static const weapon_t cgCAStatWeapons"),
	):
		order_block = _static_array_block(source, marker)

		for expected in (
			"WP_GAUNTLET",
			"WP_MACHINEGUN",
			"WP_SHOTGUN",
			"WP_GRAPPLING_HOOK",
			"WP_NAILGUN",
			"WP_PROX_LAUNCHER",
			"WP_CHAINGUN",
			"WP_HEAVY_MACHINEGUN",
		):
			assert expected in order_block

		assert order_block.index("WP_SHOTGUN") < order_block.index("WP_HEAVY_MACHINEGUN")
		assert order_block.index("WP_GRAPPLING_HOOK") < order_block.index("WP_NAILGUN")
		assert order_block.index("WP_CHAINGUN") < order_block.index("WP_HEAVY_MACHINEGUN")

	assert "weapon = castatWeapons[weaponIndex];" in game_cmds
	assert "weapon = cgCAStatWeapons[weaponIndex];" in servercmds


def test_cgame_caches_and_parses_retail_castats_rows() -> None:
	servercmds = _read("src/code/cgame/cg_servercmds.c")
	local = _read("src/code/cgame/cg_local.h")

	assert "typedef struct {\n\tqboolean\tvalid;\n\tint\t\tdamageGiven;\n\tint\t\tdamageReceived;" in local
	assert "cgClanArenaStats_t\tclanArenaStats[MAX_CLIENTS];" in local

	assert "static void CG_ClearClanArenaStatsCache( void ) {" in servercmds
	assert "static void CG_ParseClanArenaStats( void ) {" in servercmds
	assert "row = &cg.clanArenaStats[rowIndex];" in servercmds
	assert "row->damageGiven = atoi( CG_Argv( 2 ) );" in servercmds
	assert "row->damageReceived = atoi( CG_Argv( 3 ) );" in servercmds
	assert "row->weaponFrags[weapon] = atoi( CG_Argv( arg++ ) );" in servercmds
	assert "row->weaponAccuracy[weapon] = atoi( CG_Argv( arg++ ) );" in servercmds
	assert "CG_ClearClanArenaStatsCache();" in servercmds
	assert 'if ( !strcmp( cmd, "castats" ) ) {' in servercmds
	assert "CG_ParseClanArenaStats();" in servercmds
