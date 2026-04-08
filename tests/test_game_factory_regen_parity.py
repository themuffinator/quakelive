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

	assert "#define DEFAULT_REGEN_HEALTH_DELAY_MILLISECONDS     1250" in config_c
	assert "#define DEFAULT_REGEN_HEALTH_RATE_MILLISECONDS      133" in config_c
	assert "#define DEFAULT_REGEN_ARMOR_DELAY_MILLISECONDS      1250" in config_c
	assert "#define DEFAULT_REGEN_ARMOR_RATE_MILLISECONDS       133" in config_c
	assert "Milliseconds after taking damage before factory health regeneration begins." in config_c
	assert "Milliseconds after taking damage before factory armor regeneration begins." in config_c
	assert "int\t\tregenHealthDelayMilliseconds;" in local_h
	assert "int\t\tregenHealthRateMilliseconds;" in local_h
	assert "int\t\tregenArmorDelayMilliseconds;" in local_h
	assert "int\t\tregenArmorRateMilliseconds;" in local_h
