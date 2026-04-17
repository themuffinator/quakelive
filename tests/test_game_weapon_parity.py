from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _function_body(source: str, signature: str) -> str:
    match = re.search(
        rf"{re.escape(signature)}\s*\{{(?P<body>.*?)^\}}",
        source,
        re.MULTILINE | re.DOTALL,
    )

    assert match is not None, f"{signature} definition missing"
    return match.group("body")


def test_server_weapon_parity_hooks_match_retail_ql() -> None:
    bg_public_h = _read("src/code/game/bg_public.h")
    g_local_h = _read("src/code/game/g_local.h")
    g_main_c = _read("src/code/game/g_main.c")
    g_weapon_c = _read("src/code/game/g_weapon.c")

    assert "#define DEFAULT_SHOTGUN_COUNT\t20" in bg_public_h
    assert "chaingunDamage;" in g_local_h
    assert "lightningFalloffDamage;" in g_local_h
    assert "railJumpStrength;" in g_local_h
    assert "grappleDamage;" in g_local_h
    assert 'g_weaponConfig.chaingunDamage = G_ReadWeaponCvar( &g_damage_cg, 8, "g_damage_cg" );' in g_main_c
    assert 'g_weaponConfig.lightningFalloffDamage = G_ReadWeaponCvarNonNegative( &g_damage_lg_falloff, 0, "g_damage_lg_falloff" );' in g_main_c
    assert 'g_weaponConfig.railJumpStrength = G_ReadWeaponCvarNonNegative( &g_railJump, 0, "g_railJump" );' in g_main_c
    assert 'g_weaponConfig.grappleDamage = G_ReadWeaponCvar( &g_damage_gh, 10, "g_damage_gh" );' in g_main_c

    assert "return ( ent->client->ps.pm_flags & PMF_DUCKED ) ? qtrue : qfalse;" in g_weapon_c
    assert "return 3.0f;" in g_weapon_c
    assert "return 5.0f;" in g_weapon_c
    assert "reach = 43.0f;" in g_weapon_c
    assert "#define\tMACHINEGUN_SPREAD\t150" in g_weapon_c
    assert "#define\tHEAVY_MACHINEGUN_SPREAD\t350" in g_weapon_c
    assert "#define\tCHAINGUN_DAMAGE\t\t(g_weaponConfig.chaingunDamage)" in g_weapon_c
    assert "spread = 700.0f + ( weaponTime / 1000.0f ) * 700.0f;" in g_weapon_c
    assert "distancePastFalloff = G_RoundFloatToInt( distance - falloffRange );" in g_weapon_c
    assert "baseDamage -= falloffDamage;" in g_weapon_c
    assert "trap_Trace( &trace, muzzle, NULL, NULL, end, ent->s.number, CONTENTS_SOLID );" in g_weapon_c
    assert "ent->client->ps.velocity[2] += 20.0f;" in g_weapon_c
    assert "ent->client->accuracy_shots += DEFAULT_SHOTGUN_COUNT;" in g_weapon_c
    assert "ent->client->pers.accuracy_shots[WP_SHOTGUN] += DEFAULT_SHOTGUN_COUNT;" in g_weapon_c


def test_fireweapon_and_railgun_paths_drop_non_retail_branches() -> None:
    g_combat_c = _read("src/code/game/g_combat.c")
    g_missile_c = _read("src/code/game/g_missile.c")
    g_weapon_c = _read("src/code/game/g_weapon.c")

    fireweapon_body = _function_body(g_weapon_c, "void FireWeapon( gentity_t *ent )")
    railgun_body = _function_body(g_weapon_c, "void weapon_railgun_fire (gentity_t *ent)")
    grapple_body = _function_body(g_weapon_c, "void Weapon_GrapplingHook_Fire (gentity_t *ent)")
    fire_grapple_body = _function_body(g_missile_c, "gentity_t *fire_grapple (gentity_t *self, vec3_t start, vec3_t dir)")

    assert "Bullet_Fire( ent, MACHINEGUN_SPREAD, MACHINEGUN_DAMAGE, MOD_MACHINEGUN );" in fireweapon_body
    assert "MACHINEGUN_TEAM_DAMAGE" not in fireweapon_body
    assert "G_GetChaingunSpread( ent )" in fireweapon_body
    assert "CHAINGUN_DAMAGE" in fireweapon_body

    assert "MOD_RAILGUN_HEADSHOT" not in railgun_body
    assert "G_ApplyRailJump( ent );" in railgun_body
    assert "G_Damage( traceEnt, ent, ent, forward, trace.endpos, shotDamage, 0, MOD_RAILGUN );" in railgun_body
    assert "if ( mod == MOD_RAILGUN && G_IsRailgunHeadshot( targ, point ) ) {" in g_combat_c
    assert "if ( mod == MOD_RAILGUN || mod == MOD_RAILGUN_HEADSHOT ) {" not in g_combat_c
    assert "hook = fire_grapple( ent, muzzle, forward );" in grapple_body
    assert "hook->damage *= s_quadFactor;" in grapple_body
    assert "hook->damage = g_weaponConfig.grappleDamage;" in fire_grapple_body
    assert "case MOD_GRAPPLE:" in g_combat_c
    assert "configuredDamage = g_weaponConfig.grappleDamage;" in g_combat_c


def test_lightning_path_uses_retail_falloff_and_muzzle_discharge_gate() -> None:
    g_weapon_c = _read("src/code/game/g_weapon.c")
    lightning_body = _function_body(g_weapon_c, "void Weapon_LightningFire( gentity_t *ent )")

    assert "muzzleContents = trap_PointContents( muzzle, ENTITYNUM_NONE );" in lightning_body
    assert "trap_Trace( &dischargeTrace" not in lightning_body
    assert "dischargeAmmo = Weapon_GetLightningDischargeAmmoCount( ent );" in lightning_body
    assert "dischargeDamage = dischargeAmmo * g_weaponConfig.lightningDamage;" in lightning_body
    assert "dischargeRadius = dischargeDamage + 16.0f;" in lightning_body
    assert "ent->client->ps.ammo[WP_LIGHTNING] = 0;" in lightning_body
    assert "Weapon_LightningDischargeDamage( dischargePoint, ent, dischargeDamage, dischargeRadius )" in lightning_body
    assert "MOD_LIGHTNING_DISCHARGE );" not in lightning_body
    assert "damage = G_GetLightningDamageForDistance( distance ) * s_quadFactor;" in lightning_body


def test_missile_pipeline_matches_retail_callback_schedule() -> None:
    g_main_c = _read("src/code/game/g_main.c")
    g_missile_c = _read("src/code/game/g_missile.c")

    run_missile_body = _function_body(g_missile_c, "void G_RunMissile( gentity_t *ent )")
    fire_rocket_body = _function_body(g_missile_c, "gentity_t *fire_rocket (gentity_t *self, vec3_t start, vec3_t dir)")
    fire_plasma_body = _function_body(g_missile_c, "gentity_t *fire_plasma (gentity_t *self, vec3_t start, vec3_t dir)")
    fire_bfg_body = _function_body(g_missile_c, "gentity_t *fire_bfg (gentity_t *self, vec3_t start, vec3_t dir)")
    fire_nail_body = _function_body(g_missile_c, "gentity_t *fire_nail( gentity_t *self, vec3_t start, vec3_t forward, vec3_t right, vec3_t up )")
    nail_bounce_body = _function_body(g_missile_c, "static qboolean G_HandleNailgunBounce( gentity_t *ent, trace_t *trace )")

    assert "#define\tGUIDED_ROCKET_THINK_TIME\t25" in g_missile_c
    assert "#define\tGUIDED_ROCKET_SPEED\t20.0f" in g_missile_c
    assert "#define\tNAILGUN_LIFETIME\t4500" in g_missile_c
    assert "#define\tEF_NAIL_BOUNCE\tEF_READY" in g_missile_c
    assert "static void G_RunGuidedRocketThink( gentity_t *ent )" in g_missile_c
    assert "static void G_RunRocketAccelerationThink( gentity_t *ent )" in g_missile_c
    assert "static void G_RunPlasmaAccelerationThink( gentity_t *ent )" in g_missile_c
    assert "static void G_RunBfgAccelerationThink( gentity_t *ent )" in g_missile_c

    assert "g_weaponConfig.guidedRocketEnabled && ent->count" not in run_missile_body
    assert "G_UpdateMissileAcceleration( ent );" not in run_missile_body
    assert "bolt->nextthink = level.time + GUIDED_ROCKET_INITIAL_THINK_TIME;" in fire_rocket_body
    assert "bolt->think = G_RunGuidedRocketThink;" in fire_rocket_body
    assert "bolt->think = G_RunRocketAccelerationThink;" in fire_rocket_body
    assert "bolt->think = G_RunPlasmaAccelerationThink;" in fire_plasma_body
    assert "bolt->think = G_RunBfgAccelerationThink;" in fire_bfg_body

    assert 'g_accelFactor_rl", "1"' in g_main_c
    assert 'g_accelFactor_pg", "1"' in g_main_c
    assert 'g_accelFactor_bfg", "1"' in g_main_c
    assert 'G_ReadWeaponFloatCvarNonNegative( &g_accelFactor_rl, 1.0f, "g_accelFactor_rl" );' in g_main_c
    assert 'G_ReadWeaponFloatCvarNonNegative( &g_accelFactor_pg, 1.0f, "g_accelFactor_pg" );' in g_main_c
    assert 'G_ReadWeaponFloatCvarNonNegative( &g_accelFactor_bfg, 1.0f, "g_accelFactor_bfg" );' in g_main_c

    assert "bolt->nextthink = level.time + NAILGUN_LIFETIME;" in fire_nail_body
    assert "bolt->s.eFlags = canBounce ? EF_NAIL_BOUNCE : 0;" in fire_nail_body
    assert "bolt->count = 0;" in fire_nail_body
    assert "vectoangles( dir, angles );" not in fire_nail_body
    assert "G_AddEvent( ent, EV_GRENADE_BOUNCE, 0 );" in nail_bounce_body
    assert "ent->count++;" in nail_bounce_body
    assert "g_weaponConfig.nailgunBounceEnabled" not in nail_bounce_body


def test_lightning_discharge_helper_matches_retail_radius_burst_shape() -> None:
    g_weapon_c = _read("src/code/game/g_weapon.c")
    discharge_helper = _function_body(
        g_weapon_c,
        "static qboolean Weapon_LightningDischargeDamage( vec3_t origin, gentity_t *attacker, float damage, float radius )",
    )
    discharge_ammo = _function_body(
        g_weapon_c,
        "static int Weapon_GetLightningDischargeAmmoCount( const gentity_t *ent )",
    )

    assert "#define LIGHTNING_DISCHARGE_DEFAULT_AMMO\t150" in g_weapon_c
    assert "if ( g_factoryCvarConfig.infiniteAmmo || ammoCount < 0 ) {" in discharge_ammo
    assert "return LIGHTNING_DISCHARGE_DEFAULT_AMMO;" in discharge_ammo
    assert "ammoCount += 1;" in discharge_ammo
    assert "numListedEntities = trap_EntitiesInBox( mins, maxs, entityList, MAX_GENTITIES );" in discharge_helper
    assert "points = damage * ( 1.0f - dist / radius );" in discharge_helper
    assert "if ( !CanDamage( ent, origin ) ) {" in discharge_helper
    assert "if ( LogAccuracyHit( ent, attacker ) ) {" in discharge_helper
    assert "dir[2] += 24.0f;" in discharge_helper
    assert "G_Damage( ent, NULL, attacker, dir, origin, (int)points, DAMAGE_RADIUS, MOD_LIGHTNING_DISCHARGE );" in discharge_helper


def test_client_true_shotgun_pattern_matches_server_ring() -> None:
    cg_weapons_c = _read("src/code/cgame/cg_weapons.c")
    pattern_body = _function_body(
        cg_weapons_c,
        "static void CG_ShotgunPattern( vec3_t origin, vec3_t origin2, int seed, int otherEntNum )",
    )

    assert "if ( i < 6 ) {" in pattern_body
    assert "r = 4000.0f * cos( DEG2RAD( angle ) );" in pattern_body
    assert "u = 4000.0f * sin( DEG2RAD( angle ) );" in pattern_body
    assert "} else if ( i < 12 ) {" in pattern_body
    assert "r = 8000.0f * cos( DEG2RAD( angle ) );" in pattern_body
    assert "u = 8000.0f * sin( DEG2RAD( angle ) );" in pattern_body
    assert "r = 12000.0f * cos( DEG2RAD( angle ) );" in pattern_body
    assert "u = 12000.0f * sin( DEG2RAD( angle ) );" in pattern_body


def test_retail_weapon_reload_defaults_match_recovered_cgame_table() -> None:
    bg_pmove_c = _read("src/code/game/bg_pmove.c")

    assert "[WP_BFG] = 300," in bg_pmove_c
    assert "[WP_GRAPPLING_HOOK] = 100," in bg_pmove_c
    assert "[WP_HEAVY_MACHINEGUN] = 75," in bg_pmove_c
