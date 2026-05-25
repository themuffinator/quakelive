from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_game_vote_and_complaint_cvar_table_matches_retail_defaults_and_flags() -> None:
	g_main = _read("src/code/game/g_main.c")
	g_config = _read("src/game/g_config.c")
	q_shared = _read("src/code/game/q_shared.h")
	qagame_hlil = _read(
		"references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt"
	)
	qagame_strings = _read(
		"references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt"
	)

	assert "#define CVAR_GAMERULE\t0x100000" in q_shared
	for expected in (
		'{ &g_allowSpecVote, "g_allowSpecVote", "0", 0, 0, qfalse }',
		'{ &g_allowVote, "g_allowVote", "1", CVAR_ARCHIVE, 0, qfalse }',
		'{ &g_allowVoteMidGame, "g_allowVoteMidGame", "0", 0, 0, qfalse }',
		'{ &g_allowForfeit, "g_allowForfeit", "1", CVAR_GAMERULE, 0, qfalse',
		'{ &g_allowKill, "g_allowKill", "1000", CVAR_GAMERULE, 0, qfalse',
		'{ &g_complaintLimit, "g_complaintLimit", "5", CVAR_ARCHIVE, 0, qfalse',
		'{ &g_complaintDamageThreshold, "g_complaintDamageThreshold", "400", CVAR_ARCHIVE, 0, qfalse',
		'{ &g_voteFlags, "g_voteFlags", "0", CVAR_ARCHIVE | CVAR_SERVERINFO, 0, qfalse }',
		'{ &g_voteDelay, "g_voteDelay", "0", 0, 0, qfalse }',
		'{ &g_voteLimit, "g_voteLimit", "0", 0, 0, qfalse }',
	):
		assert expected in g_main

	for expected in (
		'1008db64  char const (* data_1008db64)[0xf] = data_10087490 {"g_allowForfeit"}',
		'1008db68  void* data_1008db68 = data_1007d1d8',
		'1008db6c                                      00 00 10 00',
		'1008db7c  char const (* data_1008db7c)[0xc] = data_10087484 {"g_allowKill"}',
		'1008db80  char const (* data_1008db80)[0x5] = data_1008747c {"1000"}',
		'1008db84              00 00 10 00',
		'1008db94  char const (* data_1008db94)[0x10] = data_1008746c {"g_allowSpecVote"}',
		'1008db98  void* data_1008db98 = data_1007d0a8',
		'1008db9c                                                                                      00 00 00 00',
		'1008dbac  char const (* data_1008dbac)[0xc] = data_10087460 {"g_allowVote"}',
		'1008dbb0  void* data_1008dbb0 = data_1007d1d8',
		'1008dbb4                                                              01 00 00 00',
		'1008dbc4  char const (* data_1008dbc4)[0x13] = data_1008744c {"g_allowVoteMidGame"}',
		'1008dbc8  void* data_1008dbc8 = data_1007d0a8',
		'1008dbcc                                      00 00 00 00',
		'1008dce4  char const (* data_1008dce4)[0x1b] = data_1008735c {"g_complaintDamageThreshold"}',
		'1008dce8  void* data_1008dce8 = 0x10087358',
		'1008dcec                                      01 00 00 00',
		'1008dcfc  char const (* data_1008dcfc)[0x11] = data_10087344 {"g_complaintLimit"}',
		'1008dd00  void* data_1008dd00 = 0x10087340',
		'1008dd04              01 00 00 00',
		'1008f6f4  char const (* data_1008f6f4)[0xc] = data_10085de4 {"g_voteFlags"}',
		'1008f6f8  void* data_1008f6f8 = data_1007d0a8',
		'1008f6fc                                                                                      05 00 00 00',
		'1008f70c  char const (* data_1008f70c)[0xc] = data_10085dd8 {"g_voteDelay"}',
		'1008f710  void* data_1008f710 = data_1007d0a8',
		'1008f714                                                              00 00 00 00',
		'1008f724  char const (* data_1008f724)[0xc] = data_10085dcc {"g_voteLimit"}',
		'1008f728  void* data_1008f728 = data_1007d0a8',
		'1008f72c                                      00 00 00 00',
	):
		assert expected in qagame_hlil

	for expected in (
		"1007d0a8                          30 00 00 00                                                                      0...",
		"1007d1d8                                                                          31 00 00 00                                      1...",
		'10085dcc  char const data_10085dcc[0xc] = "g_voteLimit", 0',
		'10085dd8  char const data_10085dd8[0xc] = "g_voteDelay", 0',
		'10085de4  char const data_10085de4[0xc] = "g_voteFlags", 0',
		"10087340  35 00 00 00                                                                                      5...",
		"10087355                                                                 00 00 00 34 30 30 00                                   ...400.",
		'1008744c  char const data_1008744c[0x13] = "g_allowVoteMidGame", 0',
		'10087460  char const data_10087460[0xc] = "g_allowVote", 0',
		'1008746c  char const data_1008746c[0x10] = "g_allowSpecVote", 0',
		'1008747c  char const data_1008747c[0x5] = "1000", 0',
		'10087484  char const data_10087484[0xc] = "g_allowKill", 0',
		'10087490  char const data_10087490[0xf] = "g_allowForfeit", 0',
	):
		assert expected in qagame_strings

	assert "#define DEFAULT_COMPLAINT_DAMAGE_THRESHOLD        400" in g_config
	assert "#define DEFAULT_COMPLAINT_LIMIT                   5" in g_config
	assert 'G_ReadFactoryNonNegativeCvar( &g_allowKill, DEFAULT_ALLOW_KILL_DELAY_MILLISECONDS, "g_allowKill" )' in g_config
	assert 'G_ReadFactoryNonNegativeCvar( &g_complaintDamageThreshold, DEFAULT_COMPLAINT_DAMAGE_THRESHOLD, "g_complaintDamageThreshold" )' in g_config
	assert 'G_ReadFactoryNonNegativeCvar( &g_complaintLimit, DEFAULT_COMPLAINT_LIMIT, "g_complaintLimit" )' in g_config


def test_game_cosmetic_timer_loadout_cvar_table_matches_retail_defaults_and_flags() -> None:
	g_main = _read("src/code/game/g_main.c")
	g_local = _read("src/code/game/g_local.h")
	g_config = _read("src/game/g_config.c")
	q_shared = _read("src/code/game/q_shared.h")
	qagame_hlil = _read(
		"references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt"
	)
	qagame_strings = _read(
		"references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt"
	)

	assert "#define CVAR_GAMERULE\t0x100000" in q_shared
	for expected in (
		'{ &g_customSettings, "g_customSettings", "0", CVAR_SERVERINFO, 0, qfalse',
		'{ &g_itemTimers, "g_itemTimers", "1", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse',
		'{ &g_itemHeight, "g_itemHeight", "35", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse',
		'{ &g_forceSmallScoreboardMessage, "g_forceSmallScoreboardMessage", "0", 0, 0, qfalse',
		'{ &g_forceSendConfigstring, "g_forceSendConfigstring", "0", 0, 0, qfalse',
		'{ &g_forceAtmosphericEffects, "g_forceAtmosphericEffects", "", CVAR_GAMERULE, 0, qfalse',
		'{ &g_forceDmgThroughSurface, "g_forceDmgThroughSurface", "0", CVAR_GAMERULE, 0, qfalse',
		'{ &g_specItemTimers, "g_specItemTimers", "1", 0, 0, qfalse }',
	):
		assert expected in g_main

	assert "extern\tvmCvar_t\tg_specItemTimers;" in g_local
	assert '{ &g_loadout,              "g_loadout",              STRINGIZE( DEFAULT_FACTORY_LOADOUT ), CVAR_SERVERINFO | CVAR_GAMERULE,' in g_config
	assert '{ &g_infiniteAmmo,         "g_infiniteAmmo",         STRINGIZE( DEFAULT_INFINITE_AMMO ), CVAR_GAMERULE,' in g_config
	assert "#define DEFAULT_FACTORY_LOADOUT            0" in g_config
	assert "#define DEFAULT_INFINITE_AMMO              0" in g_config

	for expected in (
		'1008dd2c  char const (* data_1008dd2c)[0x11] = data_10087318 {"g_customSettings"}',
		'1008dd30  void* data_1008dd30 = data_1007d0a8',
		'1008dd34                                                              04 00 00 00',
		'1008e29c  char const (* data_1008e29c)[0x19] = data_10086f0c {"g_forceDmgThroughSurface"}',
		'1008e2a0  void* data_1008e2a0 = data_1007d0a8',
		'1008e2a4              00 00 10 00',
		'1008e2b4  char const (* data_1008e2b4)[0x1a] = data_10086ef0 {"g_forceAtmosphericEffects"}',
		'1008e2b8  void* data_1008e2b8 = data_1007c414',
		'1008e2bc                                                                                      00 00 10 00',
		'1008e2cc  char const (* data_1008e2cc)[0x18] = data_10086ed8 {"g_forceSendConfigstring"}',
		'1008e2d0  void* data_1008e2d0 = data_1007d0a8',
		'1008e2d4                                                              00 00 00 00',
		'1008e2e4  char const (* data_1008e2e4)[0x1e] = data_10086eb8 {"g_forceSmallScoreboardMessage"}',
		'1008e2e8  void* data_1008e2e8 = data_1007d0a8',
		'1008e2ec                                      00 00 00 00',
		'1008e554  char const (* data_1008e554)[0xf] = data_10086c64 {"g_infiniteAmmo"}',
		'1008e558  void* data_1008e558 = data_1007d0a8',
		'1008e55c                                                                                      00 00 10 00',
		'1008e59c  char const (* data_1008e59c)[0xd] = data_10086c38 {"g_itemHeight"}',
		'1008e5a0  void* data_1008e5a0 = 0x10086c34',
		'1008e5a4              04 00 10 00',
		'1008e5b4  char const (* data_1008e5b4)[0xd] = data_10086c24 {"g_itemTimers"}',
		'1008e5b8  void* data_1008e5b8 = data_1007d1d8',
		'1008e5bc                                                                                      04 00 10 00',
		'1008e884  char const (* data_1008e884)[0xa] = data_100869f0 {"g_loadout"}',
		'1008e888  void* data_1008e888 = data_1007d0a8',
		'1008e88c                                      04 00 10 00',
		'1008f16c  char const (* data_1008f16c)[0x11] = data_1008625c {"g_specItemTimers"}',
		'1008f170  void* data_1008f170 = data_1007d1d8',
		'1008f174                                                              00 00 00 00',
	):
		assert expected in qagame_hlil

	for expected in (
		"1007c414                                                              00 00 00 00                                              ....",
		"1007d0a8                          30 00 00 00                                                                      0...",
		"1007d1d8                                                                          31 00 00 00                                      1...",
		'1008625c  char const data_1008625c[0x11] = "g_specItemTimers", 0',
		'100869f0  char const data_100869f0[0xa] = "g_loadout", 0',
		'10086c24  char const data_10086c24[0xd] = "g_itemTimers", 0',
		"10086c31                                                     00 00 00 33 35 00 00                                           ...35..",
		'10086c38  char const data_10086c38[0xd] = "g_itemHeight", 0',
		'10086c64  char const data_10086c64[0xf] = "g_infiniteAmmo", 0',
		'10086eb8  char const data_10086eb8[0x1e] = "g_forceSmallScoreboardMessage", 0',
		'10086ed8  char const data_10086ed8[0x18] = "g_forceSendConfigstring", 0',
		'10086ef0  char const data_10086ef0[0x1a] = "g_forceAtmosphericEffects", 0',
		'10086f0c  char const data_10086f0c[0x19] = "g_forceDmgThroughSurface", 0',
		'10087318  char const data_10087318[0x11] = "g_customSettings", 0',
	):
		assert expected in qagame_strings


def test_game_cosmetic_timer_loadout_cvars_keep_retail_behavioral_wiring() -> None:
	g_main = _read("src/code/game/g_main.c")
	g_cmds = _read("src/code/game/g_cmds.c")
	g_client = _read("src/code/game/g_client.c")
	g_config = _read("src/game/g_config.c")
	g_items = _read("src/code/game/g_items.c")
	g_team = _read("src/code/game/g_team.c")
	g_vote = _read("src/code/game/g_vote.c")
	g_weapon = _read("src/code/game/g_weapon.c")
	cg_servercmds = _read("src/code/cgame/cg_servercmds.c")
	cg_newdraw = _read("src/code/cgame/cg_newdraw.c")
	qagame_hlil = _read(
		"references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt"
	)

	for expected in (
		"static const char *G_SelectForcedAtmosphere( void ) {",
		"if ( g_forceAtmosphericEffects.string[0] ) {",
		'Info_SetValueForKey( info, FORCED_COSMETICS_KEY_SMALL_SCOREBOARD, g_forceSmallScoreboardMessage.integer ? "1" : "0" );',
		'Info_SetValueForKey( info, FORCED_COSMETICS_KEY_HUD, g_forceSendConfigstring.integer ? "1" : "0" );',
		'Info_SetValueForKey( info, FORCED_COSMETICS_KEY_DAMAGE, g_forceDmgThroughSurface.integer ? "1" : "0" );',
		"atmosphere = G_SelectForcedAtmosphere();",
		"Info_SetValueForKey( info, FORCED_COSMETICS_KEY_ATMOSPHERE, atmosphere );",
		"G_UpdateForcedCosmeticsConfigstring( qtrue );",
		"g_forceSmallScoreboardMessage.modificationCount != s_forceSmallScoreboardMessageModCount",
		"g_forceSendConfigstring.modificationCount != s_forceSendConfigstringModCount",
		"g_forceAtmosphericEffects.modificationCount != s_forceAtmosphericEffectsModCount",
		"g_forceDmgThroughSurface.modificationCount != s_forceDmgThroughSurfaceModCount",
		"g_forcedAtmosphere.modificationCount != s_forcedAtmosphereModCount",
	):
		assert expected in g_main

	for expected in (
		"static void G_UpdateItemTimerConfig( qboolean forceBroadcast ) {",
		"enabled = g_itemTimers.integer ? 1 : 0;",
		"height = g_itemHeight.integer;",
		"height = ITEM_TIMER_DEFAULT_HEIGHT;",
		"G_BroadcastItemTimerState( enabled, height );",
		"if ( g_itemTimers.modificationCount != s_itemTimersModCount || g_itemHeight.modificationCount != s_itemHeightModCount ) {",
	):
		assert expected in g_main
	assert "G_SendItemTimerState( clientNum, g_itemTimers.integer ? 1 : 0, g_itemHeight.integer );" in g_client
	assert 'trap_SendServerCommand( clientNum, va( "itemcfg %i %i", enabled ? 1 : 0, clampedHeight ) );' in g_cmds
	assert "G_SendItemTimerState( -1, enabled, height );" in g_cmds
	assert "if ( g_itemTimers.integer == 0 ) {" in g_items
	assert "if ( g_itemTimers.integer == 0 ) {" in g_team
	assert 'trap_Cvar_Set( "g_itemTimers", va( "%i", enabled ) );' in g_vote
	assert "G_BroadcastItemTimerState( enabled, g_itemHeight.integer );" in g_vote

	for expected in (
		"static qboolean s_customSettingsDirty = qtrue;",
		"s_customSettingsDirty = qtrue;",
		"qboolean G_CustomSettingsDirty( void ) {",
		"void G_ClearCustomSettingsDirtyFlag( void ) {",
		"mask = G_ComputeCustomSettingsMask();",
		'trap_Cvar_Set( "g_customSettings", payload );',
		"trap_SetConfigstring( CS_CUSTOM_SETTINGS, payload );",
	):
		assert expected in g_main

	for expected in (
		'trap_Cvar_Set( "g_loadout", STRINGIZE( DEFAULT_FACTORY_LOADOUT ) );',
		'trap_Cvar_Set( "g_loadout", "1" );',
		'trap_Cvar_Set( "g_loadout", "0" );',
		'config.infiniteAmmo = G_ReadFactoryBoolCvar( &g_infiniteAmmo, DEFAULT_INFINITE_AMMO, "g_infiniteAmmo" );',
	):
		assert expected in g_config + g_vote
	assert "if ( g_factoryCvarConfig.infiniteAmmo || configuredAmmo < 0 ) {" in g_client
	assert "if ( g_factoryCvarConfig.infiniteAmmo || ammoCount < 0 ) {" in g_weapon
	assert "if ( !g_factoryCvarConfig.infiniteAmmo && ent->client->ps.ammo[WP_LIGHTNING] >= 0 ) {" in g_weapon
	assert 'trap_Cvar_Set( "cg_loadout", cgs.loadout );' in cg_servercmds
	assert "return ( cg_loadout.integer != 0 ) ? qtrue : qfalse;" in cg_newdraw

	assert qagame_hlil.count('{"g_specItemTimers"}') == 1
	assert "g_specItemTimers.integer" not in g_main + g_cmds + g_client + g_items + g_team + g_vote + g_weapon


def test_game_vote_and_complaint_cvars_keep_retail_behavioral_wiring() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	game_combat = _read("src/code/game/g_combat.c")
	main_c = _read("src/code/game/g_main.c")

	for expected in (
		"if ( !g_allowVote.integer && !privilegedCallVote ) {",
		"if ( !g_allowVote.integer ) {",
		"if ( isSpectator && !g_allowSpecVote.integer && !privilegedCallVote ) {",
		"if ( client->sess.sessionTeam == TEAM_SPECTATOR && !g_allowSpecVote.integer ) {",
		"if ( !g_allowVoteMidGame.integer && midGame && !privilegedCallVote ) {",
		"delayMsec = g_voteDelay.integer > 0 ? g_voteDelay.integer * 1000 : 0;",
		"if ( g_voteLimit.integer > 0 && client->pers.voteCount >= g_voteLimit.integer && !privilegedCallVote ) {",
		"if ( g_voteFlags.integer & VF_NO_ENDVOTE ) {",
		"if ( ( g_voteFlags.integer & VF_NO_MAP_RESTART ) && !privilegedCallVote ) {",
		"if ( ( g_voteFlags.integer & VF_NO_RANDOM ) && !privilegedCallVote ) {",
		"if ( ( g_voteFlags.integer & VF_NO_LOADOUTS ) && !privilegedCallVote ) {",
		"if ( ( g_voteFlags.integer & VF_NO_WEAPRESPAWN ) && !privilegedCallVote ) {",
		"if ( g_allowForfeit.integer <= 0 ) {",
		"cooldown = g_allowKill.integer;",
	):
		assert expected in game_cmds

	for expected in (
		"threshold = g_complaintDamageThreshold.integer;",
		"if ( g_complaintLimit.integer > 0 && attackerClient->complaintCount >= g_complaintLimit.integer ) {",
	):
		assert expected in game_combat

	assert "if ( !g_singlePlayer.integer && !( g_voteFlags.integer & VF_NO_ENDVOTE ) ) {" in main_c


def test_cmd_callvote_exposes_retail_random_and_toggle_votes() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "#define VF_NO_TIME_LIMIT\t\t0x0020" in game_cmds
	assert "#define VF_NO_FRAG_LIMIT\t\t0x0040" in game_cmds
	assert "#define VF_NO_SHUFFLE\t\t\t0x0080" in game_cmds
	assert "#define VF_NO_TEAMSIZE\t\t\t0x0100" in game_cmds
	assert "#define VF_NO_RANDOM\t\t\t0x0200" in game_cmds
	assert "#define VF_NO_LOADOUTS\t\t\t0x0400" in game_cmds
	assert "#define VF_NO_ENDVOTE\t\t\t0x0800" in game_cmds
	assert "#define VF_NO_AMMO\t\t\t0x1000" in game_cmds
	assert "#define VF_NO_TIMERS\t\t\t0x2000" in game_cmds
	assert "#define VF_NO_WEAPRESPAWN\t\t0x4000" in game_cmds
	assert "#define VF_NO_BOTS" not in game_cmds
	assert "static qboolean G_IsVoteTokenIdentifier( const char *token ) {" in game_cmds
	assert "static qboolean G_IsSafeVoteToken( const char *token ) {" in game_cmds
	assert "static qboolean G_CallVoteTargetPlayerExists( const char *name ) {" in game_cmds
	assert "static qboolean G_CallVoteClientSlotIsActive( int clientNum ) {" in game_cmds
	assert "static qboolean G_VoteArgumentIsNumericValue( const char *text ) {" in game_cmds
	assert "static qboolean G_VoteArgumentIsUnsignedInteger( const char *text ) {" not in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to coin toss is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Valid cointoss parameters are:    ^5heads    ^5tails ^7\\\\n\\"" );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "cointoss %s", arg2 );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Random number generation is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid upper limit, parameter must be an integer.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid upper limit. (Valid Range: 2 - 100)\\\\n\\"" );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "random %d", upperLimit );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to alter loadouts is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to alter loadouts is only allowed during the warm up period.\\\\n\\"" );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "loadouts %s", arg2 );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to alter the ammo system is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to alter the ammo system is only allowed during the warm up period.\\\\n\\"" );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "ammo %s", arg2 );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to alter the item timers is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to alter the item timers is only allowed during the warm up period.\\\\n\\"" );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "timers %s", arg2 );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to change the weapon respawn time is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Missing desired weapon respawn time.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid desired weapon respawn time, parameter must be an integer.\\\\n\\"" );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "weaprespawn %d", atoi( arg2 ) );' in game_cmds

	assert '!Q_stricmp( arg1, "kickbot" )' not in game_cmds
	assert '!Q_stricmp( arg1, "addbot" )' not in game_cmds
	assert '!Q_stricmp( arg1, "scorelimit" )' not in game_cmds
	assert '!Q_stricmp( arg1, "roundlimit" )' not in game_cmds
	assert '!Q_stricmp( arg1, "randommap" )' not in game_cmds
	assert '!Q_stricmp( arg1, "ruleset" )' not in game_cmds


def test_cmd_callvote_restores_retail_privileged_bypass() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "static qboolean G_ClientBypassesCallVoteRestrictions( const gclient_t *client ) {" in game_cmds
	assert "return ( client->sess.privilege >= PRIV_MOD ) ? qtrue : qfalse;" in game_cmds
	assert "privilegedCallVote = G_ClientBypassesCallVoteRestrictions( client );" in game_cmds

	assert "if ( !g_allowVote.integer && !privilegedCallVote ) {" in game_cmds
	assert "if ( g_voteLimit.integer > 0 && client->pers.voteCount >= g_voteLimit.integer && !privilegedCallVote ) {" in game_cmds
	assert "if ( isSpectator && !g_allowSpecVote.integer && !privilegedCallVote ) {" in game_cmds
	assert "if ( !g_allowVoteMidGame.integer && midGame && !privilegedCallVote ) {" in game_cmds

	assert "if ( ( g_voteFlags.integer & VF_NO_MAP_RESTART ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_NEXTMAP ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_MAP ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_GAMETYPE ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_SHUFFLE ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_TEAMSIZE ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_KICK ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_TIME_LIMIT ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_FRAG_LIMIT ) && !privilegedCallVote ) {" in game_cmds


def test_cmd_callvote_restores_retail_map_nextmap_and_kick_validation() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert 'trap_Argv( 1, arg1, sizeof( arg1 ) );' in game_cmds
	assert 'if ( !G_IsSafeVoteToken( arg1 ) || !G_IsSafeVoteToken( arg2 ) || !G_IsSafeVoteToken( arg3 ) ) {' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid vote string.\\\\n\\"" );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"No nextmap is currently set.\\\\n\\"" );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "map %s; set nextmap' not in game_cmds
	assert 'Q_strncpyz( level.voteString, buffer, sizeof( level.voteString ) );' in game_cmds
	assert 'Q_strncpyz( level.voteDisplayString, buffer, sizeof( level.voteDisplayString ) );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Factory does not exist.\\\\n\\"" );' in game_cmds

	assert 'if ( !G_CallVoteTargetPlayerExists( arg2 ) ) {' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, va( "print \\"Player %s is not on the server.\\\\n\\"", arg2 ) );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "kick \\"%s\\"", arg2 );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Missing player id.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid player id, parameter must be an integer.\\\\n\\"" );' in game_cmds
	assert 'if ( !G_CallVoteClientSlotIsActive( clientNum ) ) {' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to kick a server admin is not allowed.\\\\n\\"" );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Missing desired timelimit.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid desired timelimit, parameter must be an integer in minutes.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Missing desired fraglimit.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid desired fraglimit, parameter must be an integer.\\\\n\\"" );' in game_cmds


def test_cmd_callvote_promotes_pending_vote_through_retail_start_helper() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "static void G_StartPublicVote( void ) {" in game_cmds
	assert "clientNum = level.pendingVoteClientNum;" in game_cmds
	assert "voteSelection = client->pers.voteLastSelection;" in game_cmds
	assert "G_RegisterVoteCall( client, clientNum, voteSelection );" in game_cmds
	assert 'trap_SendServerCommand( -1, va( "print \\"%s called a vote.\\\\n\\"", client->pers.netname ) );' in game_cmds
	assert "client->pers.voteState = VOTE_STATE_YES;" in game_cmds
	assert "level.pendingVoteClientNum = -1;" in game_cmds
	assert 'trap_SetConfigstring( CS_VOTE_TIME, va( "%i", level.voteTime ) );' in game_cmds
	assert 'trap_SetConfigstring( CS_VOTE_STRING, level.voteDisplayString );' in game_cmds
	assert "client->pers.voteLastSelection = voteSelection;" in game_cmds
	assert "level.pendingVoteClientNum = ent-g_entities;" in game_cmds
	assert "G_StartPublicVote();" in game_cmds


def test_cmd_callvote_restores_retail_shuffle_teamsize_and_help_listing() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to shuffle the teams is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to shuffle the teams is only permitted during warmup.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Too many parameters called for a shuffle.\\\\n\\"" );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Teamsize is not available in Duel.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to change team size is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Missing desired teamsize.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid desired teamsize, parameter must be an integer.\\\\n\\"" );' in game_cmds
	assert "G_CountActivePlayersByTeam( activeCounts );" in game_cmds
	assert 'va( "print \\"^1The arena has more than %d players. Players must leave before this teamsize can be set.^7\\"", desiredSize )' in game_cmds
	assert 'va( "print \\"^1%s has more than %d players. Players must leave the team before this teamsize can be set.^7\\"",' in game_cmds
	assert 'va( "print \\"Invalid team size. (Valid Range: %d - %d)\\\\n\\"", 0, maxSize )' in game_cmds

	assert "static int G_CallVoteHelpColor( int voteFlagMask ) {" in game_cmds
	assert "if ( g_voteFlags.integer & voteFlagMask ) {" in game_cmds
	assert "static void G_CallVotePrintHelp( gentity_t *ent ) {" in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"^3Callvote commands:\\\\n\\"" );' in game_cmds
	assert 'va( "print \\"^%imap           ^%inextmap        ^%imap_restart   ^7\\\\n\\"",' in game_cmds
	assert 'va( "print \\"^%ikick          ^%iclientkick                      ^7\\\\n\\"",' in game_cmds
	assert 'va( "print \\"^%ishuffle       ^%iteamsize       ^%icointoss      ^7\\\\n\\"",' in game_cmds
	assert 'va( "print \\"^%itimelimit     ^%ifraglimit      ^%iweaprespawn   ^7\\\\n\\"",' in game_cmds
	assert 'va( "print \\"^%iloadouts      ^%iammo           ^%itimers        ^7\\\\n\\"",' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Usage: ^3\\\\\\\\callvote <command> <params>^7\\\\n\\"" );' in game_cmds
	assert "G_CallVotePrintHelp( ent );" in game_cmds
