from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


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


def test_retail_flight_thrust_cvar_is_registered_but_not_a_pmove_input_surface() -> None:
	bg_public = _read("src/code/game/bg_public.h")
	bg_pmove = _read("src/code/game/bg_pmove.c")
	g_items = _read("src/code/game/g_items.c")
	g_main = _read("src/code/game/g_main.c")
	local_h = _read("src/code/game/g_local.h")
	pmove_c = _read("src/code/game/g_pmove.c")

	assert '{ &g_flightThrust, "g_flightThrust", "1200", CVAR_ARCHIVE | CVAR_NORESTART' in g_main
	assert "g_flightRefuelRate" not in g_main
	assert "g_flightRefuelRate" not in local_h
	assert "G_GetFlightRefuelMilliseconds" not in g_items
	assert "flightThrust" not in bg_public
	assert "flightThrust" not in pmove_c
	assert "g_flightThrust" not in pmove_c
	fly_start = bg_pmove.index("static void PM_FlyMove( void )")
	fly_end = bg_pmove.index("static void PM_AirMove", fly_start)
	assert "flightThrust" not in bg_pmove[fly_start:fly_end]
	pickup_start = g_items.index("int Pickup_Powerup( gentity_t *ent, gentity_t *other )")
	pickup_end = g_items.index("return RESPAWN_POWERUP;", pickup_start)
	pickup_body = g_items[pickup_start:pickup_end]
	assert "ent->item->giTag == PW_FLIGHT" not in pickup_body
	assert "other->client->ps.powerups[ent->item->giTag] += quantity * 1000;" in pickup_body


def test_factory_runes_are_gated_separately_from_map_powerups() -> None:
	config_c = _read("src/game/g_config.c")
	items_c = _read("src/code/game/g_items.c")
	local_h = _read("src/code/game/g_local.h")

	assert "extern vmCvar_t g_loadout;" in local_h
	assert "extern vmCvar_t g_runes;" in local_h
	assert '{ &g_loadout,              "g_loadout",              STRINGIZE( DEFAULT_FACTORY_LOADOUT ), CVAR_SERVERINFO,' in config_c
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
