#include "rules_fixtures.h"
#include "syscall_mocks.h"

#if defined(__has_include)
#if __has_include("g_local.h")
#include "g_local.h"
#elif __has_include("../code/game/g_local.h")
#include "../code/game/g_local.h"
#elif __has_include("../../code/game/g_local.h")
#include "../../code/game/g_local.h"
#else
#error "Unable to locate g_local.h for weapon cvar fixtures"
#endif
#else
#include "../../code/game/g_local.h"
#endif

#include <string.h>

/*
=================
HLIL defaults referenced by these fixtures

The Quake Live HLIL listings pin the following gameplay baselines:
- g_powerupRespawn = 120 seconds.
- g_respawn_delay_min = 2100 ms while g_respawn_delay_max = 2400 ms.
- g_regenHealthRate defaults to 100 milliseconds per health point.
=================
*/

static qboolean GT_ProxDamageConfigFeedsWeaponCache(void);
static qboolean GT_FactoryConfigPreservesRespawnBounds(void);
static qboolean GT_GDamageSchedulesRespawnAndPlum(void);
static qboolean GT_ClientTimerAppliesRegenPerSecond(void);

static void GT_SetVmCvarInt(vmCvar_t *cvar, int value);
static void GT_SetVmCvarFloat(vmCvar_t *cvar, float value);
static void GT_ResetGameWorld(void);
static gentity_t *GT_PrepareClientEntity(int index, int health);

/*
=============
GT_SetVmCvarInt

Applies an integer payload to a vmCvar_t in place so helper code can consume it without trap_Cvar_* calls.
=============
*/
static void GT_SetVmCvarInt(vmCvar_t *cvar, int value) {
	if (!cvar) {
		return;
	}

	cvar->integer = value;
	cvar->value = (float)value;
	Com_sprintf(cvar->string, sizeof(cvar->string), "%i", value);
	cvar->modificationCount++;
}

/*
=============
GT_SetVmCvarFloat

Writes a floating-point payload into a vmCvar_t structure for tests that exercise float-based helpers.
=============
*/
static void GT_SetVmCvarFloat(vmCvar_t *cvar, float value) {
	if (!cvar) {
		return;
	}

	cvar->value = value;
	cvar->integer = (int)value;
	Com_sprintf(cvar->string, sizeof(cvar->string), "%0.3f", value);
	cvar->modificationCount++;
}

/*
=============
GT_ResetGameWorld

Clears the global level/g_entity/g_client state and binds the syscall surface so server code can run in isolation.
=============
*/
static void GT_ResetGameWorld(void) {
	int i;

	GT_ResetSyscallMocks();
	memset(&level, 0, sizeof(level));
	memset(g_entities, 0, sizeof(g_entities));
	memset(g_clients, 0, sizeof(g_clients));

	level.clients = g_clients;
	level.maxclients = MAX_CLIENTS;
	level.num_entities = 0;

	for (i = 0; i < MAX_CLIENTS; ++i) {
		g_entities[i].client = &level.clients[i];
		g_entities[i].s.number = i;
	}

	g_entities[ENTITYNUM_WORLD].s.number = ENTITYNUM_WORLD;
}

/*
=============
GT_PrepareClientEntity

Initialises a player gentity/gclient pair with sane defaults so combat helpers can operate without G_InitGame.
=============
*/
static gentity_t *GT_PrepareClientEntity(int index, int health) {
	gentity_t *ent;
	gclient_t *client;

	if (index < 0 || index >= MAX_CLIENTS) {
		return NULL;
	}

	ent = &g_entities[index];
	client = &level.clients[index];

	memset(ent, 0, sizeof(*ent));
	memset(client, 0, sizeof(*client));

	ent->s.number = index;
	ent->client = client;
	ent->health = health;
	ent->takedamage = qtrue;
	ent->die = player_die;
	VectorClear(ent->r.mins);
	VectorClear(ent->r.maxs);

	client->ps.stats[STAT_MAX_HEALTH] = health;
	client->ps.stats[STAT_HEALTH] = health;
	client->ps.stats[STAT_ARMOR] = 0;
	client->pers.connected = CON_CONNECTED;

	return ent;
}

/*
=============
GT_ProxDamageConfigFeedsWeaponCache

Verifies that g_damage_pl and g_quadDamageFactor flow through G_InitWeaponConfig into the cached weaponConfig block.
=============
*/
static qboolean GT_ProxDamageConfigFeedsWeaponCache(void) {
	memset(&g_weaponConfig, 0, sizeof(g_weaponConfig));

	GT_SetVmCvarInt(&g_damage_pl, 42);
	GT_SetVmCvarFloat(&g_quadDamageFactor, 4.25f);

	G_InitWeaponConfig();

	if (g_weaponConfig.proximityLauncherDamage != 42) {
		return GT_Failf("expected prox direct damage 42, received %d", g_weaponConfig.proximityLauncherDamage);
	}

	if (Q_fabs(g_weaponConfig.quadDamageMultiplier - 4.25f) > 0.01f) {
		return GT_Failf("expected quad damage multiplier 4.25, received %.2f", g_weaponConfig.quadDamageMultiplier);
	}

	return qtrue;
}

/*
=============
GT_FactoryConfigPreservesRespawnBounds

Ensures the factory CVar loader honours regen/powerup timings while keeping the retail min/max respawn fields independent.
=============
*/
static qboolean GT_FactoryConfigPreservesRespawnBounds(void) {
	GT_SetVmCvarInt(&g_powerupRespawn, 30);
	GT_SetVmCvarInt(&g_respawn_delay_min, 2500);
	GT_SetVmCvarInt(&g_respawn_delay_max, 1000);
	GT_SetVmCvarInt(&g_regenHealthRate, 266);

	G_InitFactoryCvarConfig();

	if (g_factoryCvarConfig.powerupRespawnSeconds != 30) {
		return GT_Failf("expected powerup respawn 30, received %d", g_factoryCvarConfig.powerupRespawnSeconds);
	}

	if (g_factoryCvarConfig.respawnDelayMinMilliseconds != 2500) {
		return GT_Failf("expected respawn min 2500, received %d", g_factoryCvarConfig.respawnDelayMinMilliseconds);
	}

	if (g_factoryCvarConfig.respawnDelayMaxMilliseconds != 1000) {
		return GT_Failf("expected respawn max grace 1000, received %d", g_factoryCvarConfig.respawnDelayMaxMilliseconds);
	}

	if (g_factoryCvarConfig.regenHealthRateMilliseconds != 266) {
		return GT_Failf("expected regen health rate 266, received %d", g_factoryCvarConfig.regenHealthRateMilliseconds);
	}

	return qtrue;
}

/*
=============
GT_GDamageSchedulesRespawnAndPlum

Seeds two virtual clients, applies lethal damage, and validates the combat bookkeeping plus respawn timer scheduling.
=============
*/
static qboolean GT_GDamageSchedulesRespawnAndPlum(void) {
	gentity_t *attacker;
	gentity_t *target;

	GT_ResetGameWorld();
	attacker = GT_PrepareClientEntity(0, 100);
	target = GT_PrepareClientEntity(1, 100);
	if (!attacker || !target) {
		return GT_Failf("failed to allocate test clients");
	}

	level.time = 3200;
	g_factoryCvarConfig.respawnDelayMinMilliseconds = 2100;
	g_factoryCvarConfig.respawnDelayMaxMilliseconds = 2400;
	g_suddenDeathRespawn.integer = 0;
	G_Damage(target, attacker, attacker, NULL, NULL, 200, 0, MOD_ROCKET);

	if (target->client->respawnTime != level.time + 2100) {
		return GT_Failf("expected respawn time %d, received %d", level.time + 2100, target->client->respawnTime);
	}

	if (target->client->damage_blood <= 0) {
		return GT_Failf("expected positive damage plum payload, received %d", target->client->damage_blood);
	}

	if (target->client->ps.persistant[PERS_ATTACKER] != attacker->s.number) {
		return GT_Failf("expected attacker slot %d, received %d",
		attacker->s.number,
		target->client->ps.persistant[PERS_ATTACKER]);
	}

	return qtrue;
}

/*
=============
GT_ClientTimerAppliesRegenPerSecond

Confirms ClientTimerActions adds the HLIL regen delta per tick and bleeds health back toward the max when overstacked.
=============
*/
static qboolean GT_ClientTimerAppliesRegenPerSecond(void) {
	gentity_t *ent;
	int baseHealth;

	GT_ResetGameWorld();
	ent = GT_PrepareClientEntity(0, 125);
	if (!ent) {
		return GT_Failf("failed to allocate regen client");
	}

	baseHealth = 80;
	ent->health = baseHealth;
	ent->client->ps.stats[STAT_HEALTH] = baseHealth;
	ent->client->ps.powerups[PW_REGEN] = level.time + 5000;

	ClientTimerActions(ent, 1000);
	if (ent->health != baseHealth + 15) {
		return GT_Failf("expected regen to add 15 health, received %d", ent->health - baseHealth);
	}

	ent->health = ent->client->ps.stats[STAT_MAX_HEALTH] + 5;
	ent->client->ps.powerups[PW_REGEN] = 0;
	ClientTimerActions(ent, 1000);
	if (ent->health != ent->client->ps.stats[STAT_MAX_HEALTH] + 4) {
		return GT_Failf("expected bleed to remove 1 health, received %d", ent->health - ent->client->ps.stats[STAT_MAX_HEALTH]);
	}

	return qtrue;
}

static const game_fixture_t gt_weapon_cvar_fixtures[] = {
	{
		"weapon_config_caches_damage_and_quad",
		NULL,
		GT_ProxDamageConfigFeedsWeaponCache,
		NULL,
		"Ensures g_damage_pl and g_quadDamageFactor flow into g_weaponConfig"
	},
	{
		"factory_config_preserves_respawn_bounds",
		NULL,
		GT_FactoryConfigPreservesRespawnBounds,
		NULL,
		"Validates g_powerupRespawn, g_regenHealthRate, and independent respawn delay bounds"
	},
	{
		"g_damage_schedules_respawn",
		NULL,
		GT_GDamageSchedulesRespawnAndPlum,
		NULL,
		"Kills a client via G_Damage and inspects damage bookkeeping plus respawn time"
	},
	{
		"client_timer_regen_tick",
		NULL,
		GT_ClientTimerAppliesRegenPerSecond,
		NULL,
		"Confirms ClientTimerActions applies HLIL regen deltas and bleeds overheal"
	}
};

/*
=============
GT_RunWeaponCvarFixtures

Executes the weapon/regen CVar-driven fixture suite with the default trap-backed reporter.
=============
*/
game_fixture_result_t GT_RunWeaponCvarFixtures(void) {
	game_fixture_reporter_t reporter;
	GT_InitDefaultReporter(&reporter);
	return GT_RunFixtureSuite(
	"weapon_cvar_rules",
	gt_weapon_cvar_fixtures,
	GAME_TESTS_ARRAY_LEN(gt_weapon_cvar_fixtures),
	&reporter);
}
