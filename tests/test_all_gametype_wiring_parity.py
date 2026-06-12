from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _function_body(source: str, signature: str) -> str:
	definition = f"{signature} {{"
	start = source.index(definition)
	brace = start + len(definition) - 1
	depth = 1
	index = brace + 1

	while depth > 0:
		if source[index] == "{":
			depth += 1
		elif source[index] == "}":
			depth -= 1
		index += 1

	return source[brace + 1 : index - 1]


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


def _assert_ordered(block: str, tokens: list[str]) -> None:
	position = -1
	for token in tokens:
		next_position = block.index(token, position + 1)
		assert next_position > position
		position = next_position


def test_all_retail_gametype_ids_factory_defaults_info_text_and_icons_are_wired() -> None:
	bg_public = _read("src/code/game/bg_public.h")
	factory_c = _read("src/code/game/g_factory.c")
	cg_servercmds = _read("src/code/cgame/cg_servercmds.c")
	cg_newdraw = _read("src/code/cgame/cg_newdraw.c")

	enum_block = bg_public[
		bg_public.index("typedef enum {\n\tGT_FFA") :
		bg_public.index("} gametype_t;")
	]
	_assert_ordered(
		enum_block,
		[
			"GT_FFA,",
			"GT_TOURNAMENT,",
			"GT_SINGLE_PLAYER,",
			"GT_TEAM,",
			"GT_CLAN_ARENA,",
			"GT_CTF,",
			"GT_1FCTF,",
			"GT_OBELISK,",
			"GT_HARVESTER,",
			"GT_FREEZE,",
			"GT_DOMINATION,",
			"GT_ATTACK_DEFEND,",
			"GT_RED_ROVER,",
			"GT_MAX_GAME_TYPE",
		],
	)
	assert "#define GT_RACE\t\tGT_SINGLE_PLAYER" in bg_public

	basegt_body = _function_body(
		factory_c,
		"static qboolean Factory_MapBaseGametype( const char *token, gametype_t *outType )",
	)
	for token, gametype in (
		("ffa", "GT_FFA"),
		("duel", "GT_TOURNAMENT"),
		("race", "GT_RACE"),
		("tdm", "GT_TEAM"),
		("ca", "GT_CLAN_ARENA"),
		("ctf", "GT_CTF"),
		("oneflag", "GT_1FCTF"),
		("dom", "GT_DOMINATION"),
		("ad", "GT_ATTACK_DEFEND"),
		("ft", "GT_FREEZE"),
		("har", "GT_HARVESTER"),
		("obelisk", "GT_OBELISK"),
		("rr", "GT_RED_ROVER"),
	):
		assert f'{{ "{token}", {gametype} }}' in basegt_body

	default_body = _function_body(
		factory_c,
		"static const char *Factory_GetDefaultIdForGametype( gametype_t gametype )",
	)
	for gametype, factory_id in (
		("GT_FFA", "ffa"),
		("GT_TOURNAMENT", "duel"),
		("GT_SINGLE_PLAYER", "race"),
		("GT_TEAM", "tdm"),
		("GT_CLAN_ARENA", "ca"),
		("GT_CTF", "ctf"),
		("GT_1FCTF", "oneflag"),
		("GT_OBELISK", "ovl"),
		("GT_HARVESTER", "har"),
		("GT_FREEZE", "ft"),
		("GT_DOMINATION", "dom"),
		("GT_ATTACK_DEFEND", "ad"),
		("GT_RED_ROVER", "rr"),
	):
		assert f'case {gametype}:\n\t\treturn "{factory_id}";' in default_body

	for gametype, first_line in (
		("GT_FFA", "This is a Free For All game"),
		("GT_TOURNAMENT", "This is a 1 vs 1 Duel game"),
		("GT_SINGLE_PLAYER", "This is a Race game"),
		("GT_TEAM", "This is a Team Deathmatch game"),
		("GT_CLAN_ARENA", "This is a Clan Arena game"),
		("GT_CTF", "This is a Capture the Flag game"),
		("GT_1FCTF", "This is a One Flag game"),
		("GT_OBELISK", "This is an Overload game"),
		("GT_HARVESTER", "This is a Harvester game"),
		("GT_FREEZE", "This is a Freeze Tag game"),
		("GT_DOMINATION", "This is a Domination game"),
		("GT_ATTACK_DEFEND", "This is an Attack and Defend game"),
		("GT_RED_ROVER", "This is a Red Rover game"),
	):
		assert f'[{gametype}] = {{\n\t\t"{first_line}",' in cg_servercmds

	for expected in (
		'cgGameTypeIconShaders[GT_FFA] = trap_R_RegisterShaderNoMip( "ui/assets/hud/ffa.tga" );',
		'cgGameTypeIconShaders[GT_TOURNAMENT] = trap_R_RegisterShaderNoMip( "ui/assets/hud/duel.tga" );',
		'cgGameTypeIconShaders[GT_SINGLE_PLAYER] = trap_R_RegisterShaderNoMip( "ui/assets/hud/race.tga" );',
		'cgGameTypeIconShaders[GT_TEAM] = trap_R_RegisterShaderNoMip( "ui/assets/hud/tdm.tga" );',
		'cgGameTypeIconShaders[GT_CLAN_ARENA] = trap_R_RegisterShaderNoMip( "ui/assets/hud/ca.tga" );',
		'cgGameTypeIconShaders[GT_CTF] = trap_R_RegisterShaderNoMip( "ui/assets/hud/ctf.tga" );',
		'cgGameTypeIconShaders[GT_1FCTF] = trap_R_RegisterShaderNoMip( "ui/assets/hud/1f.tga" );',
		"cgGameTypeIconShaders[GT_OBELISK] = cgGameTypeIconShaders[GT_FFA];",
		'cgGameTypeIconShaders[GT_HARVESTER] = trap_R_RegisterShaderNoMip( "ui/assets/hud/har.tga" );',
		'cgGameTypeIconShaders[GT_FREEZE] = trap_R_RegisterShaderNoMip( "ui/assets/hud/ft.tga" );',
		'cgGameTypeIconShaders[GT_DOMINATION] = trap_R_RegisterShaderNoMip( "ui/assets/hud/dom.tga" );',
		'cgGameTypeIconShaders[GT_ATTACK_DEFEND] = trap_R_RegisterShaderNoMip( "ui/assets/hud/ad.tga" );',
		'cgGameTypeIconShaders[GT_RED_ROVER] = trap_R_RegisterShaderNoMip( "ui/assets/hud/rr.tga" );',
	):
		assert expected in cg_newdraw


def test_qagame_and_cgame_scoreboard_transport_matrix_covers_every_gametype_bucket() -> None:
	g_cmds = _read("src/code/game/g_cmds.c")
	cg_servercmds = _read("src/code/cgame/cg_servercmds.c")
	cg_main = _read("src/code/cgame/cg_main.c")
	qagame_strings = _read(
		"references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt"
	)
	cgame_hlil = _read(
		"references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part02.txt"
	)

	scoreboard_body = _function_body(g_cmds, "void DeathmatchScoreboardMessage( gentity_t *ent )")
	_assert_ordered(
		scoreboard_body,
		[
			"case GT_FFA:\n\t\tcmd = \"scores_ffa\";",
			"case GT_TOURNAMENT:\n\t\tcmd = \"scores_duel\";",
			"case GT_OBELISK:\n\t\tcmd = \"scores\";",
			"case GT_TEAM:\n\t\tcmd = \"scores_tdm\";",
			"case GT_CLAN_ARENA:\n\t\tcmd = \"scores_ca\";",
			"case GT_CTF:",
			"case GT_1FCTF:",
			"case GT_HARVESTER:",
			"case GT_DOMINATION:",
			"cmd = \"scores_ctf\";",
			"case GT_ATTACK_DEFEND:\n\t\tcmd = \"scores_ad\";",
			"case GT_FREEZE:\n\t\tcmd = \"scores_ft\";",
			"case GT_RED_ROVER:\n\t\tcmd = \"scores_rr\";",
		],
	)
	for builder in (
		"G_BuildFFAScoreboardMessage",
		"G_BuildDuelScoreboardMessage",
		"G_BuildRaceScoreboardMessage",
		"G_BuildTeamScoreboardMessage",
		"G_BuildClanArenaScoreboardMessage",
		"G_BuildObeliskScoreboardMessage",
		"G_BuildCTFStyleScoreboardMessage",
		"G_BuildFreezeScoreboardMessage",
		"G_BuildRedRoverScoreboardMessage",
	):
		assert builder in scoreboard_body or builder in g_cmds
	assert "if ( g_gametype.integer == GT_TEAM || g_gametype.integer == GT_FREEZE ) {\n\t\t\tG_SendTDMStatsMessage( ent );" in scoreboard_body
	assert "if ( g_gametype.integer == GT_CLAN_ARENA ) {\n\t\t\tG_SendCAStatsMessage( ent );" in scoreboard_body
	assert "if ( G_IsCTFStyleScoreboardGametype() ) {\n\t\t\tG_SendCTFStatsMessage( ent );" in scoreboard_body

	for command, parser in (
		("scores_ffa", "CG_ParseFFAScores"),
		("scores_duel", "CG_ParseDuelScores"),
		("scores_race", "CG_ParseRaceScores"),
		("scores_tdm", "CG_ParseTdmScores"),
		("scores_ca", "CG_ParseClanArenaScores"),
		("scores_ctf", "CG_ParseCtfScores"),
		("scores_ft", "CG_ParseFreezeScores"),
		("scores_ad", "CG_ParseADScores"),
		("adscores", "CG_ParseADScores"),
		("scores_rr", "CG_ParseRedRoverScores"),
		("tdmstats", "CG_ParseTDMStats"),
		("castats", "CG_ParseClanArenaStats"),
		("ctfstats", "CG_ParseCTFStats"),
		("smscores", "CG_ParseCompactScores"),
		("scores", "CG_ParseScores"),
	):
		assert f'if ( !strcmp( cmd, "{command}" ) ) {{' in cg_servercmds
		assert f"{parser}();" in cg_servercmds

	feeder_body = _function_body(
		cg_main,
		"static const char *CG_FeederItemText( float feederID, int index, int column, qhandle_t *handle )",
	)
	for expected in (
		"case GT_TEAM:\n\t\tcase GT_FREEZE:\n\t\t\treturn CG_FeederItemTextTDMFreezeStats",
		"case GT_CLAN_ARENA:\n\t\t\treturn CG_FeederItemTextClanArenaStats",
		"case GT_CTF:\n\t\tcase GT_1FCTF:\n\t\tcase GT_HARVESTER:\n\t\tcase GT_DOMINATION:\n\t\tcase GT_ATTACK_DEFEND:\n\t\t\treturn CG_FeederItemTextCTFFamilyStats",
		"case GT_TEAM:\n\t\tcase GT_FREEZE:\n\t\t\treturn CG_FeederItemTextTDMFreezeTeamList",
		"case GT_CLAN_ARENA:\n\t\t\treturn CG_FeederItemTextClanArenaTeamList",
		"case GT_CTF:\n\t\tcase GT_1FCTF:\n\t\tcase GT_HARVESTER:\n\t\tcase GT_DOMINATION:\n\t\tcase GT_ATTACK_DEFEND:\n\t\t\treturn CG_FeederItemTextCTFFamilyTeamList",
		"if ( cgs.gametype == GT_RACE ) {\n\t\treturn CG_FeederItemTextRaceScoreboard",
		"return CG_FeederItemTextScoreboard",
	):
		assert expected in feeder_body

	for expected in (
		'char const data_10082cdc[0x16] = "scores_ffa %i %i %i%s", 0',
		'char const data_10082d58[0x14] = "scores_duel 2 %s %s", 0',
		'char const data_10082da8[0x11] = "scores_race %i%s", 0',
		'char const data_10082df0[0x6a] = "scores_tdm',
		'char const data_10082e80[0xe] = "tdmstats %i%s", 0',
		'char const data_10082ec4[0x15] = "scores_ca %i %i %i%s", 0',
		'char const data_10082ee4[0xd] = "castats %i%s", 0',
		'char const data_10082f28[0x7c] = "scores_ctf',
		'char const data_10082fcc[0xe] = "ctfstats %i%s", 0',
		'char const data_10082fe0[0x69] = "scores_ft',
		'char const data_100821b8[0x4c] = "scores_ad',
		'char const data_10083088[0x15] = "scores_rr %i %i %i%s", 0',
	):
		assert expected in qagame_strings

	for expected in (
		'char const data_10072128[0xb] = "scores_ffa", 0',
		'char const data_10072134[0xc] = "scores_duel", 0',
		'char const data_10072140[0xc] = "scores_race", 0',
		'char const data_1007214c[0xb] = "scores_tdm", 0',
		'char const data_10072158[0xa] = "scores_ca", 0',
		'char const data_10072164[0xb] = "scores_ctf", 0',
		'char const data_10072170[0xa] = "scores_ft", 0',
		'char const data_1007217c[0xa] = "scores_ad", 0',
		'char const data_10072194[0xa] = "scores_rr", 0',
	):
		assert expected in cgame_hlil


def test_shared_gametype_runframe_exit_round_and_status_buckets_match_retail_groups() -> None:
	g_lifecycle = _read("src/code/game/g_gametype_lifecycle.inc")
	g_cmds = _read("src/code/game/g_cmds.c")
	g_main = _read("src/code/game/g_main.c")
	g_match_state = _read("src/code/game/g_match_state.c")
	g_team = _read("src/code/game/g_team.c")
	cg_servercmds = _read("src/code/cgame/cg_servercmds.c")

	lifecycle_body = _function_body(
		g_lifecycle,
		"static void G_RunGametypeLifecycle( gametypeLifecycleStage_t stage, gentity_t *ent )",
	)
	assert "case GT_TOURNAMENT:\n\t\tG_GametypeHandleDuel( stage, ent );" in lifecycle_body
	assert "case GT_RACE:\n\t\tG_GametypeHandleRace( stage, ent );" in lifecycle_body
	assert "case GT_CLAN_ARENA:\n\tcase GT_ATTACK_DEFEND:\n\tcase GT_RED_ROVER:\n\t\tG_GametypeHandleRoundBased( stage, ent );" in lifecycle_body

	runframe_counts = _block_from_marker(g_main, "static void G_RunFrameRoundModeCountHooks")
	for expected in ("case GT_CLAN_ARENA:", "case GT_FREEZE:", "case GT_ATTACK_DEFEND:", "case GT_RED_ROVER:"):
		assert expected in runframe_counts
	assert "G_UpdateTeamCountConfigstrings();" in runframe_counts

	runframe_hooks = _block_from_marker(g_main, "static void G_RunFrameGametypeHooks")
	for expected in (
		"if ( g_gametype.integer == GT_FFA ) {\n\t\tG_EnsureQuadHogQuad();",
		"} else if ( g_gametype.integer == GT_CLAN_ARENA || g_gametype.integer == GT_FREEZE ) {\n\t\tG_Frame_UpdateRoundController();",
		"} else if ( g_gametype.integer == GT_ATTACK_DEFEND ) {",
		"} else if ( g_gametype.integer == GT_RED_ROVER ) {\n\t\tG_RRTrackRoundActivity();",
		"} else if ( g_gametype.integer == GT_CTF ) {\n\t\tTeam_ReturnFlagIfMissing( TEAM_RED );",
		"} else if ( g_gametype.integer == GT_DOMINATION ) {\n\t\tG_UpdateDominationPointCountConfigstrings();",
	):
		assert expected in runframe_hooks

	exit_rules = _block_from_marker(g_main, "void CheckExitRules( void )")
	for expected in (
		"case GT_CLAN_ARENA:",
		"case GT_ATTACK_DEFEND:",
		"case GT_RED_ROVER:",
		"case GT_FREEZE:",
		"if ( g_freezeRoundDelay.integer != 0 ) {",
		"( g_gametype.integer == GT_FFA || g_gametype.integer == GT_TOURNAMENT ||",
		"g_gametype.integer == GT_TEAM ) && g_fraglimit.integer",
		"( g_gametype.integer == GT_CTF || g_gametype.integer == GT_1FCTF ||",
		"g_gametype.integer == GT_OBELISK || g_gametype.integer == GT_HARVESTER ) &&",
		"if ( g_gametype.integer == GT_DOMINATION && g_scorelimit.integer ) {",
		"if ( g_gametype.integer >= GT_TEAM && mercylimit.integer > 0 && elapsed >= mercyLimitMsec ) {",
	):
		assert expected in exit_rules

	requires_both_teams = _function_body(g_cmds, "static qboolean G_GametypeRequiresBothTeamsPresent( void )")
	for expected in (
		"case GT_TEAM:",
		"case GT_CLAN_ARENA:",
		"case GT_CTF:",
		"case GT_1FCTF:",
		"case GT_OBELISK:",
		"case GT_HARVESTER:",
		"case GT_FREEZE:",
		"case GT_DOMINATION:",
		"case GT_ATTACK_DEFEND:",
	):
		assert expected in requires_both_teams
	assert "case GT_RED_ROVER:" not in requires_both_teams

	ctf_scoreboard_family = _function_body(g_cmds, "static qboolean G_IsCTFStyleScoreboardGametype( void )")
	for expected in ("case GT_CTF:", "case GT_1FCTF:", "case GT_HARVESTER:", "case GT_DOMINATION:", "case GT_ATTACK_DEFEND:"):
		assert expected in ctf_scoreboard_family
	assert "case GT_OBELISK:" not in ctf_scoreboard_family
	assert "case GT_FREEZE:" not in ctf_scoreboard_family

	team_counts = _function_body(g_match_state, "static void G_BuildPublishedTeamCounts( int counts[TEAM_NUM_TEAMS] )")
	assert "if ( g_gametype.integer < GT_TEAM ) {" in team_counts
	assert "if ( G_UsesRoundControllerTeamCounts() ) {" in team_counts
	assert "G_CountActivePlayersByTeam( counts );" in team_counts
	assert "G_CountConnectedClientsByTeam( counts );" in team_counts

	flag_status_server = _function_body(g_team, "void Team_SetFlagStatus( int team, flagStatus_t status )")
	assert "if( g_gametype.integer == GT_CTF || g_gametype.integer == GT_ATTACK_DEFEND ) {" in flag_status_server
	assert "st[0] = ctfFlagStatusRemap[teamgame.redStatus];" in flag_status_server
	assert "st[0] = oneFlagStatusRemap[teamgame.flagStatus];" in flag_status_server
	assert "trap_SetConfigstring( CS_FLAGSTATUS, st );" in flag_status_server

	flag_status_client = _function_body(cg_servercmds, "static void CG_ParseFlagStatusConfigString( const char *str )")
	assert "cgs.gametype == GT_CTF || cgs.gametype == GT_ATTACK_DEFEND || cgs.gametype == GT_OBELISK" in flag_status_client
	assert "else if( cgs.gametype == GT_1FCTF ) {" in flag_status_client

	shared_race_dom = _function_body(cg_servercmds, "static void CG_ParseSharedRaceDominationConfigStrings( void )")
	assert "if ( cgs.gametype == GT_RACE ) {" in shared_race_dom
	assert "if ( cgs.gametype != GT_DOMINATION && cgs.gametype != GT_ATTACK_DEFEND ) {" in shared_race_dom
	assert "cgs.dominationOwnedPointCount[TEAM_RED] = value;" in shared_race_dom
	assert "cgs.dominationOwnedPointCount[TEAM_BLUE] = value;" in shared_race_dom
