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


def test_cgame_binding_bridge_uses_direct_retail_copy_path() -> None:
	client = _read("src/code/client/cl_cgame.c")

	assert "case CG_KEY_GETBINDINGBUF:" in client
	assert 'Q_strncpyz( VMA(2), Key_GetBinding( args[1] ), args[3] );' in client


def test_team_balance_helper_is_split_out_for_setteam_and_readyup() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "static qboolean Team_CountsBalanced( int redCount, int blueCount ) {" in game_cmds
	assert "if ( g_teamForceBalance.integer && !Team_CountsBalanced( redCount, blueCount ) ) {" in game_cmds
	assert "if ( !Team_CountsBalanced( nextRedCount, nextBlueCount ) ) {" in game_cmds


def test_client_spawn_uses_recovered_loadout_and_rr_helpers() -> None:
	game_client = _read("src/code/game/g_client.c")
	game_team = _read("src/code/game/g_team.c")
	game_local = _read("src/code/game/g_local.h")

	assert "static weapon_t G_SelectConfiguredSpawnWeapon( gclient_t *client, unsigned int startingMask ) {" in game_client
	assert "static weapon_t G_FinalizeSpawnLoadout( gentity_t *ent, const factoryCvarConfig_t *factoryConfig ) {" in game_client
	assert "client->sess.selectedSpawnWeapon = (int)spawnWeapon;" in game_client
	assert "if ( client->rrInfectionState == RR_STATE_INFECTED ) {" in game_client
	assert "spawnWeapon = G_FinalizeSpawnLoadout( ent, factoryConfig );" in game_client
	assert "static void G_RRFinalizeSpawnLoadout( gentity_t *ent ) {" in game_client
	assert "client->ps.stats[STAT_WEAPONS] = 1u << WP_GAUNTLET;" in game_client
	assert "client->pers.maxHealth = client->ps.stats[STAT_MAX_HEALTH] + g_rrInfectedZombieHealthBonus.integer;" in game_client
	assert "G_RRFinalizeSpawnLoadout( ent );" in game_client
	assert game_client.index("G_RRFinalizeSpawnLoadout( ent );") < game_client.index("spawnWeapon = G_FinalizeSpawnLoadout( ent, factoryConfig );")
	assert "gentity_t *G_SelectRankedSpawnPoint( gentity_t *spots[], int spotCount, vec3_t origin, vec3_t angles ) {" in game_client
	assert "static gentity_t *G_SelectClientSpawnPoint( gentity_t *ent, vec3_t origin, vec3_t angles ) {" in game_client
	assert "spawnPoint = G_SelectClientSpawnPoint( ent, spawn_origin, spawn_angles );" in game_client
	assert "gentity_t *Team_SelectDominationSpawnPoint( gentity_t *ent, vec3_t origin, vec3_t angles ) {" in game_team
	assert "spawnPoint = Team_SelectDominationSpawnPoint( ent, origin, angles );" in game_client
	assert "return G_SelectRankedSpawnPoint( spots, count, origin, angles );" in game_team
	assert "gentity_t *G_SelectRankedSpawnPoint( gentity_t *spots[], int spotCount, vec3_t origin, vec3_t angles );" in game_local
	assert "gentity_t *Team_SelectDominationSpawnPoint( gentity_t *ent, vec3_t origin, vec3_t angles );" in game_local


def test_input_spawn_and_host_map_paths_keep_retail_factory_gates() -> None:
	cl_keys = _read("src/code/client/cl_keys.c")
	game_client = _read("src/code/game/g_client.c")
	server_cmds = _read("src/code/server/sv_ccmds.c")
	field_block = _block_from_marker(cl_keys, "void Field_KeyDownEvent")
	spawn_block = _block_from_marker(game_client, "static gentity_t *G_SelectClientSpawnPoint")
	list_block = _block_from_marker(server_cmds, "static void SV_FactoryPrintValidList")
	apply_block = _block_from_marker(server_cmds, "static void SV_FactoryApplySelection")
	map_block = _block_from_marker(server_cmds, "static void SV_Map_f")

	for expected in (
		"if ( key == K_DEL || key == K_KP_DEL ) {",
		"if ( key == K_RIGHTARROW || key == K_KP_RIGHTARROW )",
		"if ( key == K_LEFTARROW || key == K_KP_LEFTARROW )",
		"if ( key == K_HOME || key == K_KP_HOME || ( tolower(key) == 'a' && keys[K_CTRL].down ) ) {",
		"if ( key == K_END || key == K_KP_END || ( tolower(key) == 'e' && keys[K_CTRL].down ) ) {",
		"if ( key == K_INS || key == K_KP_INS ) {",
	):
		assert expected in field_block

	assert "g_gametype.integer == GT_TOURNAMENT" in spawn_block
	assert "level.trainingMapActive && client->pers.localClient" in spawn_block
	assert "client->pers.localClient || g_gametype.integer == GT_TOURNAMENT || level.trainingMapActive" not in spawn_block

	for expected in (
		'} else if ( !Q_stricmp( key, "title" ) ) {',
		"title = SV_FactoryParseJsonString( state );",
		'} else if ( !Q_stricmp( key, "cvars" ) ) {',
		"if ( !SV_FactoryParseCvarOverrides( state, definition ) ) {",
		"definition->title = title;",
	):
		assert expected in server_cmds

	for expected in (
		'Com_Printf( "Valid factories: " );',
		"factory->id[0] != '_'",
		'Com_Printf( "%s ", factory->id );',
	):
		assert expected in list_block

	for expected in (
		"if ( s_svCurrentFactory == factory ) {",
		'Cvar_Set( "g_gametype", gametypeBuffer );',
		'Cvar_Set( "g_factory", factory->id ? factory->id : "" );',
		'Cvar_Set( "g_factoryTitle", factory->title ? factory->title : "" );',
	):
		assert expected in apply_block

	assert "Cvar_Reset( override->name );" in server_cmds

	assert "static const svFactoryDefinition_t *s_svCurrentFactory = NULL;" in server_cmds
	for expected in (
		"requiredArgs = s_svCurrentFactory ? 2 : 3;",
		'Com_Printf( "%s (map) (factory)\\n", cmd );',
		"SV_FactoryPrintValidList();",
		"factoryOverride = s_svCurrentFactory;",
		"SV_FactoryApplySelection( factoryOverride );",
	):
		assert expected in map_block


def test_freeze_helpers_match_recovered_retail_boundaries() -> None:
	freeze_c = _read("src/code/game/g_freeze.c")
	active_c = _read("src/code/game/g_active.c")

	assert "static void G_FreezeSetClientFrozenState( gentity_t *ent, qboolean frozen, qboolean environmental, qboolean wasAuto, int helperNum ) {" in freeze_c
	assert "G_FreezeSetClientFrozenState( ent, qfalse, qfalse, wasAuto, helperNum );" in freeze_c
	assert "G_FreezeSetClientFrozenState( self, qtrue, environmental, qfalse, -1 );" in freeze_c

	assert "static void G_FreezeResetClientForRound( gentity_t *ent, qboolean warmup ) {" in active_c
	assert "G_FreezeResetClientForRound( ent, warmup );" in active_c
	assert "static qboolean G_FreezeTeamIsFullyFrozen( team_t team ) {" in active_c
	assert "redFrozen = G_FreezeTeamIsFullyFrozen( TEAM_RED );" in active_c
	assert "static int G_TotalLivingHealthByTeam( team_t team ) {" in active_c
	assert "G_CountActivePlayersByTeam( level.freezeLivingCount );" in active_c
	assert "level.freezeLivingHealth[TEAM_RED] = G_TotalLivingHealthByTeam( TEAM_RED );" in active_c


def test_red_rover_helpers_match_recovered_retail_boundaries() -> None:
	game_active = _read("src/code/game/g_active.c")
	game_client = _read("src/code/game/g_client.c")
	game_local = _read("src/code/game/g_local.h")
	reset_block = _block_from_marker(game_client, "static void G_RRResetClientForRound")

	assert "int G_RRResolveRoundState( void ) {" in game_active
	assert "if ( G_RRResolveRoundState() != ROUNDSTATE_ACTIVE ) {" in game_client
	assert "static void G_RRResetClientForRound( gentity_t *ent ) {" in game_client
	assert "G_RRResetClientForRound( ent );" in game_client
	assert "ClientSpawn( ent );" in reset_block
	assert "void G_RRHandleCompletedRound( void );" in game_local
	assert "void G_RRHandlePlayerDeath( team_t oldTeam, gentity_t *victim, int meansOfDeath );" in game_local
	assert "void G_RRHandleCompletedRound( void ) {" in game_client
	assert "void G_RRHandlePlayerDeath( team_t oldTeam, gentity_t *victim, int meansOfDeath ) {" in game_client
	assert "G_RRHandlePlayerDeath( client->sess.sessionTeam, self, meansOfDeath );" in game_client
	assert "G_CountConnectedClientsByTeam( counts );" in game_client
	assert "if ( G_RRCheckRoundCompletion( counts ) ) {" in game_client
	assert "level.roundTransitionTime = level.time + ( level.rrPendingMatchExit ? 1500 : 3500 );" in game_client
	assert "level.roundPendingExit = level.rrPendingMatchExit;" in game_client
	assert "if ( ScoreIsTied() ) {" in game_client


def test_last_alive_alert_helpers_match_recovered_retail_boundaries() -> None:
	game_team = _read("src/code/game/g_team.c")
	game_local = _read("src/code/game/g_local.h")
	shared_block = _block_from_marker(game_team, "static qboolean G_NotifyLastAlivePlayer")
	ad_block = _block_from_marker(game_team, "qboolean G_ADNotifyLastAlivePlayer")
	ca_block = _block_from_marker(game_team, "qboolean G_CANotifyLastAlivePlayer")
	freeze_block = _block_from_marker(game_team, "qboolean G_FreezeNotifyLastAlivePlayer")
	rr_block = _block_from_marker(game_team, "qboolean G_RRNotifyLastAlivePlayer")

	assert "G_BroadcastGlobalTeamSound( vec3_origin, GTS_LAST_STANDING, -1, team, 0 );" in shared_block
	assert 'va( "cp \\"%s\\\\n\\"", G_LastManStandingMessage() )' in shared_block

	for expected in (
		"qboolean G_ADNotifyLastAlivePlayer( team_t team );",
		"qboolean G_CANotifyLastAlivePlayer( team_t team );",
		"qboolean G_FreezeNotifyLastAlivePlayer( team_t team );",
		"qboolean G_RRNotifyLastAlivePlayer( team_t team );",
	):
		assert expected in game_local

	for block in (ad_block, ca_block, freeze_block, rr_block):
		assert "return G_NotifyLastAlivePlayer( team );" in block
		assert "G_BroadcastGlobalTeamSound(" not in block


def test_timeout_race_and_direct_command_helpers_match_recovered_boundaries() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	game_match_state = _read("src/code/game/g_match_state.c")
	game_main = _read("src/code/game/g_main.c")
	game_race = _read("src/code/game/g_race.c")
	game_client = _read("src/code/game/g_client.c")
	game_svcmds = _read("src/code/game/g_svcmds.c")
	game_local = _read("src/code/game/g_local.h")

	assert "static qboolean G_StartTimeout( gentity_t *ent, int durationSeconds ) {" in game_cmds
	assert "static qboolean G_BeginTimein( gentity_t *ent ) {" in game_cmds
	assert "void Cmd_Pause_f( gentity_t *ent ) {" in game_cmds
	assert "static int G_KickOrBanClient( gentity_t *ent, char *targetToken, qboolean banTarget ) {" in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Can not kick admins.\\n\\"" );' in game_cmds
	assert "G_KickOrBanClient( ent, arg, qfalse );" in game_cmds
	assert "G_KickOrBanClient( ent, arg, qtrue );" in game_cmds
	assert "G_KickOrBanClient( ent, val, qfalse );" in game_cmds
	assert "G_KickOrBanClient( ent, val, qtrue );" in game_cmds

	assert "void G_UpdateTimeoutConfigStrings( void ) {" in game_match_state
	assert "static void G_UpdateRoundStartConfigString( void ) {" in game_match_state
	assert "trap_SetConfigstring( CS_ROUND_START_TIME" in game_match_state
	assert "trap_SetConfigstring( CS_TIMEOUT_START_TIME" in game_match_state
	assert "trap_SetConfigstring( CS_TIMEOUT_EXPIRE_TIME" in game_match_state
	assert "trap_SetConfigstring( CS_TIMEOUT_COUNT_RED" in game_match_state
	assert "trap_SetConfigstring( CS_TIMEOUT_COUNT_BLUE" in game_match_state
	assert "G_UpdateRoundStartConfigString();" in game_match_state
	assert "G_UpdateTimeoutConfigStrings();" in game_match_state

	assert "static void G_CheckTimeoutExpired( void ) {" in game_main
	assert "G_CheckTimeoutExpired();" in game_main
	assert "static void G_UpdateDominationCaptureTimeConfigstring( qboolean forceBroadcast ) {" in game_main
	assert "trap_SetConfigstring( CS_DOMINATION_CAPTURE_TIME, payload );" in game_main
	assert "static void G_UpdateRRInfectedSurvivorPingRateConfigstring( qboolean forceBroadcast ) {" in game_main
	assert "trap_SetConfigstring( CS_RR_INFECTED_SURVIVOR_PING_RATE, payload );" in game_main
	assert "static void G_UpdateModeSpecificConfigstrings( qboolean forceBroadcast ) {" in game_main
	assert "G_UpdateModeSpecificConfigstrings( qtrue );" in game_main
	assert "G_UpdateModeSpecificConfigstrings( qfalse );" in game_main
	assert "static int G_AdminAccessForConnectedClient( int clientNum ) {" in game_main
	assert "void G_ReloadAdminAccess( void ) {" in game_main
	assert "client->sess.privilege = G_AdminAccessForConnectedClient( clientNum );" in game_main
	assert "void\tG_ReloadAdminAccess( void );" in game_local
	assert "trap_SetConfigstring( CS_SPAWN_HINTS" not in _read("src/game/g_match_config.c")

	assert "void G_RaceResetClientAndSpawn( gentity_t *ent ) {" in game_race
	assert "G_RaceBroadcastInitCommand( ent->s.number );" in game_race
	assert "G_RaceResetClientAndSpawn( ent );" in game_client

	assert "static void Svcmd_DumpVars_f( void ) {" in game_svcmds
	assert 'G_Printf( "Data Dump: (%s)\\n", cl->pers.netname );' in game_svcmds
	assert 'G_Printf( "clientNum: %d\\n", ( int )( cl - level.clients ) );' in game_svcmds
	assert 'G_Printf( "pm_type: 0x%08x\\n", cl->ps.pm_type );' in game_svcmds
	assert 'G_Printf( "pm_flags: 0x%08x\\n", cl->ps.pm_flags );' in game_svcmds
	assert 'G_Printf( "pm_time: %d\\n", cl->ps.pm_time );' in game_svcmds
	assert 'G_Printf( "eFlags: %d\\n", cl->ps.eFlags );' in game_svcmds
	assert 'G_Printf( "origin: (%0.3f, %0.3f, %0.3f)\\n", cl->ps.origin[0], cl->ps.origin[1], cl->ps.origin[2] );' in game_svcmds
	assert "static void Svcmd_GameCrash_f( void ) {" in game_svcmds
	assert 'trap_Cvar_VariableIntegerValue( "developer" ) < 1' in game_svcmds
	assert "*(volatile int *)0 = 0x12345678;" in game_svcmds
	assert "static void Svcmd_ReloadAccess_f( void ) {" in game_svcmds
	assert "G_ReloadAdminAccess();" in game_svcmds
	assert 'if ( Q_stricmp (cmd, "game_crash") == 0 ) {' in game_svcmds
	assert 'if ( Q_stricmp (cmd, "forceshuffle") == 0 ) {' in game_svcmds
	assert 'if ( Q_stricmp (cmd, "dumpvars") == 0 ) {' in game_svcmds
	assert 'if ( Q_stricmp (cmd, "reload_access") == 0 ) {' in game_svcmds
	assert "Svcmd_GameCrash_f();" in game_svcmds
	assert "Svcmd_DumpVars_f();" in game_svcmds
	assert "Svcmd_ReloadAccess_f();" in game_svcmds


def test_console_tail_and_training_bootstrap_helpers_match_recovered_boundaries() -> None:
	game_svcmds = _read("src/code/game/g_svcmds.c")
	game_bot = _read("src/code/game/g_bot.c")
	init_bots = _block_from_marker(game_bot, "void G_InitBots")

	assert 'Q_stricmp( cmd, "markstate" ) == 0 ||' in game_svcmds
	assert 'Q_stricmp( cmd, "diffstate" ) == 0 ||' in game_svcmds
	assert 'Q_stricmp( cmd, "dumpentities" ) == 0 ||' in game_svcmds
	assert 'Q_stricmp( cmd, "printentitystates" ) == 0 ) {' in game_svcmds
	assert 'if ( Q_stricmp( cmd, "floodstatus" ) == 0 ) {' in game_svcmds
	assert "Svcmd_FloodStatus_f();" in game_svcmds

	assert "static void G_AddTrainerBot( void ) {" in game_bot
	assert 'G_AddBot( "Trainer", skill, "", 5000, "" );' in game_bot
	assert 'trap_SendServerCommand( -1, "loaddeferred\\n" );' in game_bot
	assert 'if( Q_stricmp( strValue, "training" ) == 0 ) {' in init_bots
	assert "G_AddTrainerBot();" in init_bots
	assert 'G_SpawnBots( Info_ValueForKey( arenainfo, "bots" ), BOT_BEGIN_DELAY_BASE );' in init_bots
	assert "basedelay += 10000;" not in game_bot
