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


def test_check_exit_rules_matches_retail_gate_order_and_limit_owners() -> None:
	main_c = _read("src/code/game/g_main.c")
	check_block = _block_from_marker(main_c, "void CheckExitRules( void )")

	assert "if ( level.time - level.intermissionQueued >= 200 ) {" in check_block
	assert check_block.index("if ( level.warmupTime ) {") < check_block.index("if ( G_CanForfeit( NULL, qfalse ) ) {")
	assert "case GT_CLAN_ARENA:" in check_block
	assert "case GT_ATTACK_DEFEND:" in check_block
	assert "case GT_RED_ROVER:" in check_block
	assert "case GT_FREEZE:" in check_block

	assert "timeLimitMsec = G_BuildExitRuleLimitMsec( g_timelimit.integer, level.overtimeAccumulatedMsec );" in check_block
	assert "mercyLimitMsec = G_BuildExitRuleLimitMsec( g_mercytime.integer, level.overtimeAccumulatedMsec );" in check_block
	assert "if ( ScoreIsTied() ) {" in check_block
	assert "if ( g_timelimit.integer == 0 || g_overtime.integer <= 0 ) {" in check_block
	assert "if ( G_StartOrExtendOvertime() ) {" in check_block
	assert "G_TempEntity( vec3_origin, EV_OVERTIME );" in check_block

	assert "( g_gametype.integer == GT_FFA || g_gametype.integer == GT_TOURNAMENT ||" in check_block
	assert "g_gametype.integer == GT_TEAM ) && g_fraglimit.integer" in check_block
	assert "( g_gametype.integer == GT_CTF || g_gametype.integer == GT_1FCTF ||" in check_block
	assert "g_gametype.integer == GT_OBELISK || g_gametype.integer == GT_HARVESTER ) &&" in check_block
	assert "if ( g_gametype.integer == GT_DOMINATION && g_scorelimit.integer ) {" in check_block

	assert check_block.index("if ( g_gametype.integer == GT_DOMINATION && g_scorelimit.integer ) {") < check_block.index(
		"if ( g_gametype.integer >= GT_TEAM && mercylimit.integer > 0 && elapsed >= mercyLimitMsec ) {"
	)
	assert "if ( scoreDelta >= mercylimit.integer ) {" in check_block
	assert "if ( -scoreDelta >= mercylimit.integer ) {" in check_block


def test_intermission_exit_flow_uses_retail_fixed_grace_window_and_latch() -> None:
	main_c = _read("src/code/game/g_main.c")
	intermission_block = _block_from_marker(main_c, "void CheckIntermissionExit( void )")

	assert 'trap_Cvar_VariableStringBuffer( "nextmaps", nextmaps, sizeof( nextmaps ) );' in intermission_block
	assert "intermissionDelay = 10000;" in intermission_block
	assert "intermissionDelay = 20000;" in intermission_block
	assert 'trap_SetConfigstring( CS_INTERMISSION_EXIT_STATUS, "1" );' in intermission_block
	assert "level.intermissionExitStatusLatched = qtrue;" in intermission_block
	assert "if ( level.time >= level.intermissiontime + intermissionDelay + 3000 ) {" in intermission_block
	assert "ready++" not in intermission_block
	assert "notReady" not in intermission_block


def test_intermission_pipeline_clears_and_publishes_retail_state() -> None:
	main_c = _read("src/code/game/g_main.c")
	begin_block = _block_from_marker(main_c, "void BeginIntermission( void )")
	exit_block = _block_from_marker(main_c, "void ExitLevel (void)")
	spawn_c = _read("src/code/game/g_spawn.c")
	cmds_c = _read("src/code/game/g_cmds.c")
	bg_public_h = _read("src/code/game/bg_public.h")

	assert "static void G_ClearIntermissionReadyState( void ) {" in main_c
	assert "static void G_PublishNextMapVoteCounts( void ) {" in main_c
	assert "static void G_PublishRotationPreviewConfigstrings( void ) {" in main_c
	assert "void G_ClearNextMapVoteState( void ) {" in cmds_c
	assert "void G_UpdateNextMapVoteTallies( void ) {" in cmds_c
	assert "level.voteTime = level.time;" in main_c
	assert 'trap_SetConfigstring( CS_VOTE_TIME, va( "%i", level.voteTime ) );' in main_c
	assert 'trap_SetConfigstring( CS_INTERMISSION, "1" );' in begin_block
	assert 'trap_SetConfigstring( CS_INTERMISSION, "0" );' in exit_block
	assert "G_BroadcastGlobalTeamSound" not in begin_block
	assert "G_ClearNextMapVoteState();" in begin_block
	assert "G_ClearIntermissionReadyState();" in begin_block
	assert "G_PublishRotationPreviewConfigstrings();" in begin_block
	assert "G_ClearNextMapVoteState();" in exit_block
	assert "G_ClearIntermissionReadyState();" in exit_block
	assert 'trap_SetConfigstring( CS_ROTATION_TITLES, "" );' in exit_block
	assert 'trap_SetConfigstring( CS_ROTATION_CONFIGS, "" );' in exit_block
	assert "G_PublishNextMapVoteCounts();" in main_c
	assert '#define CS_ROTATION_CONFIGS' in bg_public_h
	assert "#define CS_INTERMISSION_EXIT_STATUS" in bg_public_h
	assert 'trap_SetConfigstring( CS_INTERMISSION_EXIT_STATUS, "" );' in spawn_c
	assert "trap_GetServerinfo( serverinfo, sizeof( serverinfo ) );" in exit_block
	assert 'Q_strncpyz( mapName, Info_ValueForKey( serverinfo, "mapname" ), sizeof( mapName ) );' in exit_block
	assert 'if ( trap_Cvar_VariableIntegerValue( "sv_killserver" ) ) {' in exit_block
	assert 'trap_SendConsoleCommand( EXEC_APPEND, "killserver\\n" );' in exit_block
	assert 'if ( trap_Cvar_VariableIntegerValue( "sv_quitOnExitLevel" ) ) {' in exit_block
	assert 'trap_SendConsoleCommand( EXEC_APPEND, "quit\\n" );' in exit_block
	assert "G_AutoAction( AUTOACTION_MATCH_END" not in exit_block
	assert exit_block.index( 'BotInterbreedEndMatch();' ) > exit_block.index(
		'if ( trap_Cvar_VariableIntegerValue( "sv_quitOnExitLevel" ) ) {'
	)
	assert exit_block.index( 'trap_SetConfigstring( CS_INTERMISSION, "0" );' ) > exit_block.index( 'BotInterbreedEndMatch();' )
	assert exit_block.count( "level.intermissionQueued = 0;" ) == 2


def test_nextmap_vote_pipeline_matches_retail_intermission_vote_flow() -> None:
	main_c = _read("src/code/game/g_main.c")
	cmds_c = _read("src/code/game/g_cmds.c")
	vote_block = _block_from_marker(cmds_c, "void Cmd_Vote_f( gentity_t *ent )")
	exit_block = _block_from_marker(main_c, "void ExitLevel (void)")

	assert "qboolean G_HandleNextMapVote( gentity_t *ent ) {" in cmds_c
	assert "if ( level.time - level.voteTime >= 20000 ) {" in cmds_c
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting time has expired.\\n\\"" );' in cmds_c
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"You may only vote once every 2 seconds.\\n\\"" );' in cmds_c
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"You already voted for this arena.\\n\\"" );' in cmds_c
	assert 'trap_SendServerCommand( -1, va( "print \\"%s voted for %s.\\n\\"", ent->client->pers.netname, voteLabel ) );' in cmds_c
	assert 'trap_SetConfigstring( CS_ROTATION_CONFIGS, voteCounts );' in cmds_c
	assert 'Info_SetValueForKey( voteCounts, key, value );' in cmds_c
	assert "if ( level.intermissiontime ) {" in vote_block
	assert "G_HandleNextMapVote( ent );" in vote_block
	assert "return;" in vote_block

	assert "static int G_SelectNextMapVoteSlot( void ) {" in main_c
	assert 'trap_Cvar_VariableStringBuffer( "nextmaps", nextmaps, sizeof( nextmaps ) );' in exit_block
	assert "selectedSlot = G_SelectNextMapVoteSlot();" in exit_block
	assert 'trap_Cvar_Set( "nextmap", va( "map %s %s", selectedMap, selectedCfg ) );' in exit_block
	assert 'trap_Cvar_Set( "nextmap", va( "map %s", selectedMap ) );' in exit_block
	assert 'if ( !g_singlePlayer.integer && ( !Q_stricmp( mapName, selectedMap ) || !Q_stricmp( selectedMap, "default" ) ) ) {' in exit_block
	assert 'trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\\n" );' in exit_block
	assert "level.restarted = qtrue;" in exit_block
	assert exit_block.index( "level.intermissionQueued = 0;" ) > exit_block.index( 'trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\\n" );' )
	assert 'trap_SendConsoleCommand( EXEC_APPEND, "vstr nextmap\\n" );' in exit_block
	assert "if ( g_gametype.integer == GT_TOURNAMENT ) {" in exit_block
	assert "RemoveTournamentLoser();" in exit_block


def test_log_exit_emits_retail_match_end_events() -> None:
	main_c = _read("src/code/game/g_main.c")
	log_exit_block = _block_from_marker(main_c, "void LogExit( const char *string )")

	assert "teamMatchEnd = ( g_gametype.integer > GT_SINGLE_PLAYER && g_gametype.integer != GT_RED_ROVER );" in log_exit_block
	assert 'trap_SetConfigstring( CS_INTERMISSION, "1" );' not in log_exit_block
	assert 'te = G_TempEntity( vec3_origin, EV_GLOBAL_TEAM_SOUND );' in log_exit_block
	assert 'te = G_TempEntity( vec3_origin, EV_GAMEOVER );' in log_exit_block
	assert "G_SetRetailGlobalTeamSoundPayload( te," in log_exit_block
	assert "te->r.svFlags |= SVF_BROADCAST;" in log_exit_block


def test_cgame_and_match_state_follow_retail_configstring_ownership() -> None:
	cgame_servercmds = _read("src/code/cgame/cg_servercmds.c")
	match_state_c = _read("src/code/game/g_match_state.c")

	assert "cgs.matchSuddenDeathActive = cgs.matchOvertimeActive;" in cgame_servercmds
	assert "static void CG_ParseIntermissionExitStatus( void ) {" in cgame_servercmds
	assert "info = CG_ConfigString( CS_INTERMISSION_EXIT_STATUS );" in cgame_servercmds
	assert "cgs.intermissionExitStatusLatched = value ? qtrue : qfalse;" in cgame_servercmds
	assert "trap_SetConfigstring( CS_SUDDENDEATH_STATUS" not in match_state_c
