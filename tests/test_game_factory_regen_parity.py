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


def test_spawn_and_sudden_death_cvar_table_matches_retail_defaults_and_flags() -> None:
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
		'{ &g_startingHealth, "g_startingHealth", "100", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse',
		'{ &g_startingArmor, "g_startingArmor", "0", CVAR_GAMERULE, 0, qfalse',
		'{ &g_startingWeapons, "g_startingWeapons", "3", CVAR_GAMERULE, 0, qfalse',
		'{ &g_suddenDeathRespawn, "g_suddenDeathRespawn", "0", CVAR_GAMERULE, 0, qfalse',
		'{ &g_suddenDeathRespawnStart, "g_suddenDeathRespawnStart", "3", CVAR_GAMERULE, 0, qfalse',
		'{ &g_suddenDeathRespawnTick, "g_suddenDeathRespawnTick", "60", CVAR_GAMERULE, 0, qfalse',
		'{ &g_suddenDeathRespawnMax, "g_suddenDeathRespawnMax", "10", CVAR_GAMERULE, 0, qfalse',
		'{ &g_suddenDeathRespawnIncrement, "g_suddenDeathRespawnIncrement", "1", CVAR_GAMERULE, 0, qfalse',
		'{ &g_suddenDeathRespawnPrint, "g_suddenDeathRespawnPrint", "1", CVAR_GAMERULE, 0, qfalse',
	):
		assert expected in g_main
	assert '{ &g_startingHealthBonus,  "g_startingHealthBonus",  STRINGIZE( DEFAULT_STARTING_HEALTH_BONUS ), CVAR_GAMERULE,' in g_config
	assert '{ &g_suddenDeathRespawn,   "g_suddenDeathRespawn",   STRINGIZE( DEFAULT_SUDDEN_DEATH_RESPAWN ), CVAR_GAMERULE,' in g_config

	for expected in (
		'1008f3f4  char const (* data_1008f3f4)[0x10] = data_1008603c {"g_startingArmor"}',
		'1008f3f8  void* data_1008f3f8 = data_1007d0a8',
		'1008f3fc                                                                                      00 00 10 00',
		'1008f40c  char const (* data_1008f40c)[0x11] = data_10086028 {"g_startingHealth"}',
		'1008f410  void* data_1008f410 = data_1007e154',
		'1008f414                                                              04 00 10 00',
		'1008f424  char const (* data_1008f424)[0x16] = data_10086010 {"g_startingHealthBonus"}',
		'1008f428  void* data_1008f428 = data_1007e1dc',
		'1008f42c                                      00 00 10 00',
		'1008f43c  char const (* data_1008f43c)[0x12] = data_10085ffc {"g_startingWeapons"}',
		'1008f440  void* data_1008f440 = 0x100874e0',
		'1008f444              00 00 10 00',
		'1008f454  char const (* data_1008f454)[0x15] = data_10085fe4 {"g_suddenDeathRespawn"}',
		'1008f458  void* data_1008f458 = data_1007d0a8',
		'1008f45c                                                                                      00 00 10 00',
		'1008f46c  char const (* data_1008f46c)[0x1e] = data_10085fc4 {"g_suddenDeathRespawnIncrement"}',
		'1008f470  void* data_1008f470 = data_1007d1d8',
		'1008f474                                                              00 00 10 00',
		'1008f484  char const (* data_1008f484)[0x18] = data_10085fac {"g_suddenDeathRespawnMax"}',
		'1008f488  void* data_1008f488 = data_1007e194',
		'1008f48c                                      00 00 10 00',
		'1008f49c  char const (* data_1008f49c)[0x1a] = data_10085f90 {"g_suddenDeathRespawnPrint"}',
		'1008f4a0  void* data_1008f4a0 = data_1007d1d8',
		'1008f4a4              00 00 10 00',
		'1008f4b4  char const (* data_1008f4b4)[0x1a] = data_10085f74 {"g_suddenDeathRespawnStart"}',
		'1008f4b8  void* data_1008f4b8 = 0x100874e0',
		'1008f4bc                                                                                      00 00 10 00',
		'1008f4cc  char const (* data_1008f4cc)[0x19] = data_10085f58 {"g_suddenDeathRespawnTick"}',
		'1008f4d0  void* data_1008f4d0 = 0x1008674c',
		'1008f4d4                                                              00 00 10 00',
	):
		assert expected in qagame_hlil

	for expected in (
		"1007d0a8                          30 00 00 00                                                                      0...",
		"1007d1d8                                                                          31 00 00 00                                      1...",
		"1007e154                                                              31 30 30 00                                              100.",
		"1007e194                                                              31 30 00 00                                              10..",
		"1007e1dc                                                                                      32 35 00 00                              25..",
		"1008674b                                   00 36 30 00 00                                                             .60..",
		'10085f58  char const data_10085f58[0x19] = "g_suddenDeathRespawnTick", 0',
		'10085f74  char const data_10085f74[0x1a] = "g_suddenDeathRespawnStart", 0',
		'10085f90  char const data_10085f90[0x1a] = "g_suddenDeathRespawnPrint", 0',
		'10085fac  char const data_10085fac[0x18] = "g_suddenDeathRespawnMax", 0',
		'10085fc4  char const data_10085fc4[0x1e] = "g_suddenDeathRespawnIncrement", 0',
		'10085fe4  char const data_10085fe4[0x15] = "g_suddenDeathRespawn", 0',
		'10085ffc  char const data_10085ffc[0x12] = "g_startingWeapons", 0',
		'10086010  char const data_10086010[0x16] = "g_startingHealthBonus", 0',
		'10086028  char const data_10086028[0x11] = "g_startingHealth", 0',
		'1008603c  char const data_1008603c[0x10] = "g_startingArmor", 0',
		"100874e0  33 00 00 00                                                                                      3...",
	):
		assert expected in qagame_strings


def test_spawn_and_sudden_death_cvars_keep_retail_behavioral_wiring() -> None:
	config_c = _read("src/game/g_config.c")
	match_config_c = _read("src/game/g_match_config.c")
	game_client = _read("src/code/game/g_client.c")
	game_main = _read("src/code/game/g_main.c")
	game_combat = _read("src/code/game/g_combat.c")
	game_items = _read("src/code/game/g_items.c")
	match_state_c = _read("src/code/game/g_match_state.c")

	for expected in (
		'config.startingWeaponsMask = G_ReadStartingWeaponsMaskCvar( &g_startingWeapons, DEFAULT_STARTING_WEAPONS_MASK, "g_startingWeapons" );',
		"config.startingWeaponsStatMask = G_ComputeStartingWeaponsStatMask( config.startingWeaponsMask );",
		"config.startingWeaponsMask = DEFAULT_STARTING_WEAPONS_MASK;",
		'config.suddenDeathRespawn = G_ReadFactoryBoolCvar( &g_suddenDeathRespawn, DEFAULT_SUDDEN_DEATH_RESPAWN, "g_suddenDeathRespawn" );',
		'config.startingHealth = G_ReadFactoryPositiveCvar( &g_startingHealth, DEFAULT_STARTING_HEALTH, "g_startingHealth" );',
		'config.startingHealthBonus = G_ReadFactoryNonNegativeCvar( &g_startingHealthBonus, DEFAULT_STARTING_HEALTH_BONUS, "g_startingHealthBonus" );',
		'config.startingArmor = G_ReadFactoryNonNegativeCvar( &g_startingArmor, DEFAULT_STARTING_ARMOR, "g_startingArmor" );',
	):
		assert expected in config_c

	for expected in (
		"static qboolean G_WarmupLevelWeaponAllowed( weapon_t weapon, unsigned int startingWeaponsMask ) {",
		"startingWeaponsMask & ( 1u << ( weaponTag - 1 ) )",
		"startingMask = factoryConfig->startingWeaponsStatMask;",
		"G_WarmupLevelWeaponAllowed( weapon, factoryConfig->startingWeaponsMask )",
		"G_SeedConfiguredSpawnAmmo( &client->ps, weapon, startingAmmoTable[weapon] );",
		"G_ApplySpawnHealth( ent, factoryConfig );",
		"if ( g_startingArmor.integer > 0 ) {",
		"client->ps.stats[STAT_ARMOR] = g_startingArmor.integer;",
		"else if ( factoryConfig->startingArmor > 0 ) {",
		"client->ps.stats[STAT_ARMOR] = factoryConfig->startingArmor;",
		"if ( g_startingHealth.integer > 0 ) {",
		"baseHealth = g_startingHealth.integer;",
		"baseHealth = factoryConfig->startingHealth;",
	):
		assert expected in game_client

	for expected in (
		'config.suddenDeathRespawnsEnabled = G_MatchConfig_ReadBoolCvar( &g_suddenDeathRespawn, DEFAULT_SUDDEN_DEATH_RESPAWN ? qtrue : qfalse, "g_suddenDeathRespawn" );',
		'config.suddenDeathStartSeconds = G_MatchConfig_ReadNonNegativeCvar( &g_suddenDeathRespawnStart, DEFAULT_SUDDEN_DEATH_START_SECONDS, "g_suddenDeathRespawnStart" );',
		'config.suddenDeathTickSeconds = G_MatchConfig_ReadPositiveCvar( &g_suddenDeathRespawnTick, DEFAULT_SUDDEN_DEATH_TICK_SECONDS, "g_suddenDeathRespawnTick" );',
		'config.suddenDeathMaxSeconds = G_MatchConfig_ReadNonNegativeCvar( &g_suddenDeathRespawnMax, DEFAULT_SUDDEN_DEATH_MAX_SECONDS, "g_suddenDeathRespawnMax" );',
		"if ( config.suddenDeathMaxSeconds < config.suddenDeathStartSeconds ) {",
		'config.suddenDeathIncrementSeconds = G_MatchConfig_ReadNonNegativeCvar( &g_suddenDeathRespawnIncrement, DEFAULT_SUDDEN_DEATH_INCREMENT_SECONDS, "g_suddenDeathRespawnIncrement" );',
		'config.suddenDeathPrintAnnouncements = G_MatchConfig_ReadBoolCvar( &g_suddenDeathRespawnPrint, DEFAULT_SUDDEN_DEATH_PRINT ? qtrue : qfalse, "g_suddenDeathRespawnPrint" );',
		"config.suddenDeathSpawnDelayActive = ( config.suddenDeathRespawnsEnabled && ( config.suddenDeathStartSeconds > 0 || config.suddenDeathIncrementSeconds > 0 ) ) ? qtrue : qfalse;",
		"FACTORY_FLAG_SUDDEN_DEATH_ENABLED",
		"FACTORY_FLAG_SUDDEN_DEATH_START",
		"FACTORY_FLAG_SUDDEN_DEATH_TICK",
		"FACTORY_FLAG_SUDDEN_DEATH_MAX",
		"FACTORY_FLAG_SUDDEN_DEATH_INCREMENT",
		"FACTORY_FLAG_SUDDEN_DEATH_PRINT",
	):
		assert expected in match_config_c

	for expected in (
		"int G_GetSuddenDeathRespawnDelay( void ) {",
		"if ( !config->suddenDeathRespawnsEnabled ) {",
		"int baseDelay = config->suddenDeathStartSeconds;",
		"int tick = config->suddenDeathTickSeconds;",
		"int increment = config->suddenDeathIncrementSeconds;",
		"int maxDelay = config->suddenDeathMaxSeconds;",
		"int steps = elapsed / tick;",
		"int delaySeconds = baseDelay + steps * increment;",
		"return delaySeconds * 1000;",
		"level.suddenDeathLastDelay = -1;",
		"previousConfig.suddenDeathRespawnsEnabled != config->suddenDeathRespawnsEnabled",
		"static void G_TrackSuddenDeathAnnouncements( void ) {",
		'trap_SendServerCommand( -1, "cp \\"Sudden-death respawns disabled\\n\\"" );',
		'trap_SendServerCommand( -1, va( "cp \\"Sudden-death respawns available in %i seconds\\n\\"", delay / 1000 ) );',
		'trap_SendServerCommand( -1, "cp \\"Sudden-death respawns available now\\n\\"" );',
		"G_TrackSuddenDeathAnnouncements();",
	):
		assert expected in game_main

	assert "if ( level.suddenDeathActive && level.overtimeActive && g_suddenDeathRespawn.integer > 0 ) {" in game_combat
	assert "if ( level.suddenDeathActive && !g_factoryCvarConfig.suddenDeathRespawn ) {" in game_items
	assert "G_SetMatchStateInt( info, MATCH_STATE_KEY_SUDDEN_RESPAWNS, config->suddenDeathRespawnsEnabled ? 1 : 0 );" in match_state_c
	assert 'trap_SetConfigstring( CS_SUDDENDEATH_STATUS, level.suddenDeathActive ? "1" : "0" );' in match_state_c


def test_factory_regen_uses_retail_delay_and_tick_helpers() -> None:
	active_c = _read("src/code/game/g_active.c")

	assert "static void G_RunFactoryHealthRegen( gentity_t *ent, int msec ) {" in active_c
	assert "static void G_RunFactoryArmorRegen( gentity_t *ent, int msec ) {" in active_c
	assert "level.time - client->factoryRegenLastDamageTime <= g_factoryCvarConfig.regenHealthDelayMilliseconds" in active_c
	assert "level.time - client->factoryRegenLastDamageTime <= g_factoryCvarConfig.regenArmorDelayMilliseconds" in active_c
	assert "client->factoryRegenHealthAccumulatorMs += msec;" in active_c
	assert "client->factoryRegenArmorAccumulatorMs += msec;" in active_c
	assert "while ( client->factoryRegenHealthAccumulatorMs >= g_factoryCvarConfig.regenHealthRateMilliseconds )" in active_c
	assert "while ( client->factoryRegenArmorAccumulatorMs >= g_factoryCvarConfig.regenArmorRateMilliseconds )" in active_c
	assert "if ( g_factoryCvarConfig.regenArmorAfterHealth && ent->health < client->ps.stats[STAT_MAX_HEALTH] ) {" in active_c
	assert "static void G_RunFactoryRegen( gentity_t *ent ) {" not in active_c


def test_client_timer_actions_calls_factory_regen_sidecars_once_per_frame() -> None:
	active_c = _read("src/code/game/g_active.c")
	start = active_c.index("void ClientTimerActions( gentity_t *ent, int msec ) {")
	end = active_c.index("/*", start + 1)
	timer_actions = active_c[start:end]

	assert timer_actions.index("while ( client->timeResidual >= 1000 ) {") < timer_actions.index("G_RunFactoryHealthRegen( ent, msec );")
	assert timer_actions.index("G_RunFactoryHealthRegen( ent, msec );") < timer_actions.index("G_RunFactoryArmorRegen( ent, msec );")
	assert "G_RunFactoryRegen( ent );" not in timer_actions


def test_factory_regen_client_layout_uses_named_retail_sidecars() -> None:
	local_h = _read("src/code/game/g_local.h")
	client_c = _read("src/code/game/g_client.c")

	assert "factoryRegenLastDamageTime;\t// retail shared last-damage timestamp for the split factory regen helpers" in local_h
	assert "factoryRegenArmorAccumulatorMs;\t// retail per-frame factory armor regen accumulator" in local_h
	assert "factoryRegenHealthAccumulatorMs;\t// retail per-frame factory health regen accumulator" in local_h
	assert "factoryRegenHealthPending;\t// retail health-regen pending latch armed by spawn/damage paths" in local_h
	assert "factoryRegenArmorPending;\t// retail armor-regen pending latch armed by spawn/damage paths" in local_h
	assert "client->factoryRegenArmorAccumulatorMs = 0;" in client_c
	assert "client->factoryRegenHealthAccumulatorMs = 0;" in client_c
	assert "client->factoryRegenHealthPending = qfalse;" in client_c
	assert "client->factoryRegenArmorPending = qfalse;" in client_c


def test_damage_path_marks_factory_regen_pending_from_retail_damage_gate() -> None:
	combat_c = _read("src/code/game/g_combat.c")

	assert "if ( targ && targ->client && ( take > 0 || asave > 0 ) ) {" in combat_c
	assert "targ->client->factoryRegenLastDamageTime = level.time;" in combat_c
	assert "targ->client->factoryRegenHealthPending = qtrue;" in combat_c
	assert "targ->client->factoryRegenArmorPending = qtrue;" in combat_c


def test_factory_config_mirrors_regen_delay_and_rate_milliseconds() -> None:
	config_c = _read("src/game/g_config.c")
	local_h = _read("src/code/game/g_local.h")

	assert "#define DEFAULT_REGEN_HEALTH_DELAY_MILLISECONDS     0" in config_c
	assert "#define DEFAULT_REGEN_HEALTH_RATE_MILLISECONDS      100" in config_c
	assert "#define DEFAULT_REGEN_ARMOR_DELAY_MILLISECONDS      0" in config_c
	assert "#define DEFAULT_REGEN_ARMOR_RATE_MILLISECONDS       100" in config_c
	assert "Milliseconds after taking damage before factory health regeneration begins." in config_c
	assert "Milliseconds after taking damage before factory armor regeneration begins." in config_c
	assert "int\t\tregenHealthDelayMilliseconds;" in local_h
	assert "int\t\tregenHealthRateMilliseconds;" in local_h
	assert "int\t\tregenArmorDelayMilliseconds;" in local_h
	assert "int\t\tregenArmorRateMilliseconds;" in local_h


def test_respawn_delay_cvars_match_retail_registration_and_reset() -> None:
	config_c = _read("src/game/g_config.c")

	assert "#define CONFIG_CVAR_FLAG_FACTORY_MANAGED 0x00100000" in config_c
	assert "#define DEFAULT_RESPAWN_DELAY_MIN_MILLISECONDS      2100" in config_c
	assert "#define DEFAULT_RESPAWN_DELAY_MAX_MILLISECONDS      2400" in config_c
	assert '{ &g_respawn_delay_min,    "g_respawn_delay_min",    STRINGIZE( DEFAULT_RESPAWN_DELAY_MIN_MILLISECONDS ), CONFIG_CVAR_FLAG_FACTORY_MANAGED,' in config_c
	assert '{ &g_respawn_delay_max,    "g_respawn_delay_max",    STRINGIZE( DEFAULT_RESPAWN_DELAY_MAX_MILLISECONDS ), CONFIG_CVAR_FLAG_FACTORY_MANAGED,' in config_c
	assert 'trap_Cvar_Set( "g_respawn_delay_min", STRINGIZE( DEFAULT_RESPAWN_DELAY_MIN_MILLISECONDS ) );' in config_c
	assert 'trap_Cvar_Set( "g_respawn_delay_max", STRINGIZE( DEFAULT_RESPAWN_DELAY_MAX_MILLISECONDS ) );' in config_c


def test_respawn_delay_min_and_max_are_independent_retail_fields() -> None:
	config_c = _read("src/game/g_config.c")
	load_start = config_c.index("static factoryCvarConfig_t G_LoadFactoryCvarConfig( void ) {")
	load_end = config_c.index("return config;", load_start)
	load_block = config_c[load_start:load_end]

	assert 'config.respawnDelayMinMilliseconds = G_ReadFactoryNonNegativeCvar( &g_respawn_delay_min, DEFAULT_RESPAWN_DELAY_MIN_MILLISECONDS, "g_respawn_delay_min" );' in load_block
	assert 'config.respawnDelayMaxMilliseconds = G_ReadFactoryNonNegativeCvar( &g_respawn_delay_max, DEFAULT_RESPAWN_DELAY_MAX_MILLISECONDS, "g_respawn_delay_max" );' in load_block
	assert "respawnDelayMaxMilliseconds < config.respawnDelayMinMilliseconds" not in load_block


def test_respawn_delay_wiring_uses_death_minimum_and_active_max_grace() -> None:
	active_c = _read("src/code/game/g_active.c")
	combat_c = _read("src/code/game/g_combat.c")
	spawn_c = _read("src/code/game/g_spawn.c")
	dead_start = active_c.index("// check for respawning")
	dead_end = active_c.index("// perform once-a-second actions", dead_start)
	dead_block = active_c[dead_start:dead_end]

	assert "static int G_GetRespawnDelayMilliseconds( void ) {" in combat_c
	assert "delay = g_factoryCvarConfig.respawnDelayMinMilliseconds;" in combat_c
	assert "if ( level.suddenDeathActive && level.overtimeActive && g_suddenDeathRespawn.integer > 0 ) {" in combat_c
	assert "self->client->respawnTime = level.time + G_GetRespawnDelayMilliseconds();" in combat_c
	assert "if ( level.time >= client->respawnTime ) {" in dead_block
	assert "respawnElapsed = level.time - client->respawnTime;" in dead_block
	assert "respawnElapsed > g_factoryCvarConfig.respawnDelayMaxMilliseconds" in dead_block
	assert "g_forcerespawn.integer" not in dead_block
	assert "G_FactoryRespawnWindowActive" not in spawn_c
	assert "G_FactoryComputeRespawnDelay" not in spawn_c
	assert "g_factoryCvarConfig.respawnDelayMinMilliseconds" not in spawn_c
	assert "g_factoryCvarConfig.respawnDelayMaxMilliseconds" not in spawn_c


def test_factory_item_spawn_defaults_match_retail_registration() -> None:
	config_c = _read("src/game/g_config.c")

	assert "#define DEFAULT_SPAWN_ITEM_POWERUP                  1" in config_c
	assert "#define DEFAULT_SPAWN_ITEM_HOLDABLE                 1" in config_c
	assert "#define DEFAULT_SPAWN_ITEM_WEAPONS                  1" in config_c
	assert "#define DEFAULT_SPAWN_ITEM_HEALTH                   1" in config_c
	assert "#define DEFAULT_SPAWN_ITEM_ARMOR                    1" in config_c
	assert "#define DEFAULT_SPAWN_ITEM_AMMO                     1" in config_c


def test_factory_item_spawn_cvars_are_vm_owned_startup_settings() -> None:
	config_c = _read("src/game/g_config.c")

	assert '{ &g_spawnItemPowerup,     "g_spawnItemPowerup",     STRINGIZE( DEFAULT_SPAWN_ITEM_POWERUP ), CVAR_SERVERINFO | CVAR_INIT,' in config_c
	assert '{ &g_spawnItemHoldable,    "g_spawnItemHoldable",    STRINGIZE( DEFAULT_SPAWN_ITEM_HOLDABLE ), CVAR_SERVERINFO | CVAR_INIT,' in config_c
	assert '{ &g_spawnItemWeapons,     "g_spawnItemWeapons",     STRINGIZE( DEFAULT_SPAWN_ITEM_WEAPONS ), CVAR_SERVERINFO | CVAR_INIT,' in config_c
	assert '{ &g_spawnItemHealth,      "g_spawnItemHealth",      STRINGIZE( DEFAULT_SPAWN_ITEM_HEALTH ), CVAR_SERVERINFO | CVAR_INIT,' in config_c
	assert '{ &g_spawnItemArmor,       "g_spawnItemArmor",       STRINGIZE( DEFAULT_SPAWN_ITEM_ARMOR ), CVAR_SERVERINFO | CVAR_INIT,' in config_c
	assert '{ &g_spawnItemAmmo,        "g_spawnItemAmmo",        STRINGIZE( DEFAULT_SPAWN_ITEM_AMMO ), CVAR_SERVERINFO | CVAR_INIT,' in config_c


def test_factory_apply_resets_factory_managed_cvars_before_overrides() -> None:
	config_c = _read("src/game/g_config.c")
	pmove_c = _read("src/code/game/g_pmove.c")
	local_h = _read("src/code/game/g_local.h")
	factory_c = _read("src/code/game/g_factory.c")

	assert "void G_Config_ResetFactoryManagedCvars( void ) {" in config_c
	assert 'trap_Cvar_Set( "weapon_reload_gauntlet", "0" );' in config_c
	assert 'trap_Cvar_Set( "weapon_reload_hmg", "0" );' in config_c
	assert 'trap_Cvar_Set( "g_loadout", STRINGIZE( DEFAULT_FACTORY_LOADOUT ) );' in config_c
	assert 'trap_Cvar_Set( "g_runes", STRINGIZE( DEFAULT_FACTORY_RUNES ) );' in config_c
	assert 'trap_Cvar_Set( "g_ammoPack", STRINGIZE( DEFAULT_AMMO_PACK_TOGGLE ) );' in config_c
	assert 'trap_Cvar_Set( "g_ammoPackHack", STRINGIZE( DEFAULT_AMMO_PACK_HACK ) );' in config_c
	assert 'trap_Cvar_Set( "g_ammoRespawn", STRINGIZE( DEFAULT_AMMO_RESPAWN_SECONDS ) );' in config_c
	assert 'trap_Cvar_Set( "g_regenHealth", STRINGIZE( DEFAULT_REGEN_HEALTH_DELAY_MILLISECONDS ) );' in config_c
	assert 'trap_Cvar_Set( "g_spawnItemPowerup", STRINGIZE( DEFAULT_SPAWN_ITEM_POWERUP ) );' in config_c
	assert 'trap_Cvar_Set( "g_spawnItemAmmo", STRINGIZE( DEFAULT_SPAWN_ITEM_AMMO ) );' in config_c
	assert "void G_PmoveResetFactoryManagedCvars( void );" in local_h
	assert "void G_PmoveResetFactoryManagedCvars( void ) {" in pmove_c
	assert 'trap_Cvar_Set( "pmove_AirControl", "0" );' in pmove_c
	assert 'trap_Cvar_Set( "g_instaGib", "0" );' in pmove_c
	assert 'trap_Cvar_Set( "g_velocity_gh", "1800" );' in pmove_c
	assert 'trap_Cvar_Set( "g_ironsights_mg", "1.0" );' in pmove_c
	assert 'trap_Cvar_Set( "g_quadHogPingRate", "0" );' in pmove_c
	assert "g_pmove_force_update = qtrue;" in pmove_c
	assert factory_c.count("G_Config_ResetFactoryManagedCvars();") == 2
	assert factory_c.count("G_PmoveResetFactoryManagedCvars();") == 2


def test_factory_apply_refreshes_pmove_after_retail_factory_override_sequence() -> None:
	factory_c = _read("src/code/game/g_factory.c")
	config_c = _read("src/game/g_config.c")
	apply_body = _function_body(
		factory_c, "qboolean Factory_Apply( const factoryDefinition_t *factory, qboolean forceReapply )"
	)
	refresh_body = _function_body(factory_c, "static void Factory_RefreshMatchConfig( void )")
	reload_body = _function_body(config_c, "void G_UpdateWeaponReloadConfig( void )")

	null_sequence = [
		"G_Config_ResetFactoryManagedCvars();",
		"G_PmoveResetFactoryManagedCvars();",
		'trap_Cvar_Set( "g_factoryTitle", "" );',
		"G_RefreshAllCvars();",
		"G_Config_UpdateCvars();",
		"Factory_RefreshMatchConfig();",
	]
	position = -1
	for statement in null_sequence:
		next_position = apply_body.index(statement, position + 1)
		assert next_position > position
		position = next_position

	active_sequence = [
		"G_Config_ResetFactoryManagedCvars();",
		"G_PmoveResetFactoryManagedCvars();",
		"for ( override = factory->overrides; override; override = override->next ) {",
		'trap_Cvar_Set( "g_gametype", gametypeBuffer );',
		"G_RefreshAllCvars();",
		"G_Config_UpdateCvars();",
		"Factory_RefreshMatchConfig();",
	]
	position = apply_body.index("s_activeFactory = factory;")
	for statement in active_sequence:
		next_position = apply_body.index(statement, position + 1)
		assert next_position > position
		position = next_position

	refresh_sequence = [
		"G_UpdateWeaponConfig();",
		"G_UpdateWeaponReloadConfig();",
		"G_UpdateKnockbackConfig();",
		"G_UpdateStartingAmmoConfig();",
		"G_UpdateAmmoPackConfig();",
		"G_UpdateFactoryCvarConfig();",
		"G_UpdateMatchFactoryConfig();",
		"G_SyncMatchFactoryConfigToLevel();",
	]
	position = -1
	for statement in refresh_sequence:
		next_position = refresh_body.index(statement, position + 1)
		assert next_position > position
		position = next_position

	assert reload_body.index("G_InitWeaponReloadConfig();") < reload_body.index("G_RefreshPmoveSettings();")


def test_factory_pmove_reset_tracks_every_nonlocal_pmove_input_surface() -> None:
	pmove_c = _read("src/code/game/g_pmove.c")
	g_main = _read("src/code/game/g_main.c")
	config_c = _read("src/game/g_config.c")

	assert "if ( g_instaGib.integer != 0 ) {" in pmove_c
	assert "g_pmoveSettings.velocityGh = G_PmoveClampRetailMinPositive( g_pmove_velocityGh_cvar.value );" in pmove_c
	assert "grappleSpeed = ( float )g_weaponConfig.grappleSpeed;" not in pmove_c
	assert '{ &g_velocity_gh, "g_velocity_gh", "1800", 0, 0, qtrue, qfalse,' in g_main
	assert 'g_weaponConfig.grappleSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_gh, 1800, "g_velocity_gh", 1 );' in g_main
	assert "g_weaponConfig.grappleSpeed != 1800" in config_c
	assert "machinegunIronsightsScale = g_weaponConfig.machinegunIronsightsScale;" in pmove_c
	assert "g_pmoveSettings.guidedRocketEnabled = ( g_weaponConfig.guidedRocketEnabled != 0 );" in pmove_c
	assert "g_pmoveSettings.quadHogPingRateSeconds = g_weaponConfig.quadHogPingRateSeconds;" in pmove_c
	assert 'trap_Cvar_Set( "g_velocity_gh", "1800" );' in pmove_c
	assert 'trap_Cvar_Set( "g_gauntletSpeedFactor", "1.0" );' in pmove_c
	assert 'trap_Cvar_Set( "g_guidedRocket", "0" );' in pmove_c
	assert 'trap_Cvar_Set( "g_quadHogTime", "0" );' in pmove_c


def test_retail_flight_cvars_are_registered_but_not_movement_or_pickup_inputs() -> None:
	bg_public = _read("src/code/game/bg_public.h")
	bg_pmove = _read("src/code/game/bg_pmove.c")
	g_items = _read("src/code/game/g_items.c")
	g_main = _read("src/code/game/g_main.c")
	local_h = _read("src/code/game/g_local.h")
	pmove_c = _read("src/code/game/g_pmove.c")

	assert '{ &g_flightThrust, "g_flightThrust", "1200", CVAR_ARCHIVE | CVAR_NORESTART' in g_main
	assert '{ &g_flightRefuelRate, "g_flightRefuelRate", "0", CVAR_ARCHIVE | CVAR_NORESTART' in g_main
	assert "extern vmCvar_t g_flightRefuelRate;" in local_h
	assert "G_GetFlightRefuelMilliseconds" not in g_items
	assert "flightThrust" not in bg_public
	assert "flightThrust" not in pmove_c
	assert "g_flightThrust" not in pmove_c
	assert "g_flightRefuelRate" not in pmove_c
	fly_start = bg_pmove.index("static void PM_FlyMove( void )")
	fly_end = bg_pmove.index("static void PM_AirMove", fly_start)
	assert "flightThrust" not in bg_pmove[fly_start:fly_end]
	assert "g_flightRefuelRate" not in bg_pmove[fly_start:fly_end]
	pickup_start = g_items.index("int Pickup_Powerup( gentity_t *ent, gentity_t *other )")
	pickup_end = g_items.index("return RESPAWN_POWERUP;", pickup_start)
	pickup_body = g_items[pickup_start:pickup_end]
	assert "ent->item->giTag == PW_FLIGHT" not in pickup_body
	assert "g_flightRefuelRate" not in pickup_body
	assert "other->client->ps.powerups[ent->item->giTag] += quantity * 1000;" in pickup_body


def test_factory_runes_are_gated_separately_from_map_powerups() -> None:
	config_c = _read("src/game/g_config.c")
	items_c = _read("src/code/game/g_items.c")
	local_h = _read("src/code/game/g_local.h")

	assert "extern vmCvar_t g_loadout;" in local_h
	assert "extern vmCvar_t g_runes;" in local_h
	assert '{ &g_loadout,              "g_loadout",              STRINGIZE( DEFAULT_FACTORY_LOADOUT ), CVAR_SERVERINFO | CVAR_GAMERULE,' in config_c
	assert '{ &g_runes,                "g_runes",                STRINGIZE( DEFAULT_FACTORY_RUNES ), 0,' in config_c
	assert """\tcase IT_PERSISTANT_POWERUP:
\t\treturn g_runes.integer ? qtrue : qfalse;""" in items_c
	assert items_c.count("if ( !g_runes.integer ) {") == 3
	assert "if ( g_runes.integer ) {" in items_c


def test_factory_ammo_spawn_gate_switches_between_global_and_weapon_ammo_families() -> None:
	items_c = _read("src/code/game/g_items.c")
	config_c = _read("src/game/g_config.c")

	assert """\tcase IT_AMMO:
\t\tif ( !g_factoryCvarConfig.spawnItemAmmo ) {
\t\t\treturn qfalse;
\t\t}

\t\tif ( item->giTag == WP_NUM_WEAPONS ) {
\t\t\treturn ( g_factoryCvarConfig.ammoPackEnabled || g_factoryCvarConfig.ammoPackHackEnabled ) ? qtrue : qfalse;
\t\t}

\t\treturn ( g_factoryCvarConfig.ammoPackEnabled || g_factoryCvarConfig.ammoPackHackEnabled ) ? qfalse : qtrue;""" in items_c
	assert "Allow the active ammo pickup family to spawn when factories expose either global ammo packs or weapon-specific ammo." in config_c


def test_ammo_vote_labels_select_retail_global_and_weapon_modes() -> None:
	vote_c = _read("src/code/game/g_vote.c")

	global_start = vote_c.index('if ( !Q_stricmp( args, "GLOBAL" ) ) {')
	weapon_start = vote_c.index('if ( !Q_stricmp( args, "WEAP" ) ) {', global_start)
	error_start = vote_c.index('trap_SendServerCommand( -1, "print \\"^3Valid loadout options are:', weapon_start)
	global_block = vote_c[global_start:weapon_start]
	weapon_block = vote_c[weapon_start:error_start]

	assert 'trap_Cvar_Set( "g_ammoPack", "1" );' in global_block
	assert 'trap_Cvar_Set( "g_ammoPack", "0" );' in weapon_block


def test_factory_selection_falls_back_to_retail_gametype_defaults() -> None:
	factory_c = _read("src/code/game/g_factory.c")

	assert "static const char *Factory_GetDefaultIdForGametype( gametype_t gametype ) {" in factory_c
	assert 'case GT_FFA:\n\t\treturn "ffa";' in factory_c
	assert 'case GT_OBELISK:\n\t\treturn "ovl";' in factory_c
	assert 'case GT_ATTACK_DEFEND:\n\t\treturn "ad";' in factory_c
	assert "static qboolean Factory_ApplyDefaultSelection( qboolean forceReapply ) {" in factory_c
	assert 'G_Printf( "factories: no retail default for g_gametype %i\\n", g_gametype.integer );' in factory_c
	assert 'G_Printf( "factories: missing retail default id %s for g_gametype %i\\n", defaultId, g_gametype.integer );' in factory_c
	assert factory_c.count("Factory_ApplyDefaultSelection( forceReapply );") == 2


def test_factory_loader_accepts_both_plural_and_singular_supplement_extensions() -> None:
	factory_c = _read("src/code/game/g_factory.c")
	server_c = _read("src/code/server/sv_ccmds.c")

	assert 'total = trap_FS_GetFileList( "scripts", ".factories", fileList, sizeof( fileList ) );' in factory_c
	assert 'if ( total <= 0 ) {' in factory_c
	assert 'total = trap_FS_GetFileList( "scripts", ".factory", fileList, sizeof( fileList ) );' in factory_c
	assert 'count = FS_GetFileList( "scripts", ".factories", fileList, sizeof( fileList ) );' in server_c
	assert 'if ( count <= 0 ) {' in server_c
	assert 'count = FS_GetFileList( "scripts", ".factory", fileList, sizeof( fileList ) );' in server_c


def test_factory_vm_parser_enforces_retail_definition_schema() -> None:
	factory_c = _read("src/code/game/g_factory.c")

	assert 'qboolean sawTitle = qfalse;' in factory_c
	assert 'qboolean sawBasegt = qfalse;' in factory_c
	assert 'qboolean sawCvars = qfalse;' in factory_c
	assert '^1A specified factory is missing required key \\"id\\", or is not a string.\\n^7' in factory_c
	assert '^1Factory with id %s is missing key \\"basegt\\", or is not a string.\\n^7' in factory_c
	assert '^1Factory with id %s is missing key \\"title\\", or is not a string.\\n^7' in factory_c
	assert '^1Factory with id %s is missing key \\"cvars\\", or is not an object.\\n^7' in factory_c
	assert '^1Factory with id %s specifies an invalid basegt.\\n^7' in factory_c
	assert '^1Factory with id %s already exists.\\n^7' in factory_c
	assert '^1A specified factory is not an object. All factories must be JSON objects.\\n^7' in factory_c
	assert "offset = cursor - state->start;" in factory_c
	assert factory_c.count("state->cursor--;") >= 2


def test_ruleset_sync_stops_seeding_factory_and_registers_weapon_spawn_alias() -> None:
	main_c = _read("src/code/game/g_main.c")

	assert '{ &g_spawnItemWeapons, "g_spawnItemWeapons", &g_spawnItemWeaponLegacy, "g_spawnItemWeapon", "1", CVAR_SERVERINFO | CVAR_INIT, -1, -1 }' in main_c
	assert 'trap_Cvar_Set( "g_factory", ruleset );' not in main_c
	assert "defaulting to the current gametype's retail factory when unset or invalid." in main_c
