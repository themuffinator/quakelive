from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_EVENT = REPO_ROOT / "src" / "code" / "cgame" / "cg_event.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_PARTICLES = REPO_ROOT / "src" / "code" / "cgame" / "cg_particles.c"
CG_WEAPONS = REPO_ROOT / "src" / "code" / "cgame" / "cg_weapons.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CGAME_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "cgame.json"
CGAME_GHIDRA = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "cgamex86"
	/ "decompile_top_functions.c"
)
CGAME_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "cgamex86"
	/ "functions.csv"
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _block_from_marker(source: str, marker: str) -> str:
	start = source.index(marker)
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


def _case_block(source: str, marker: str) -> str:
	start = source.index(marker)
	next_markers = [
		position
		for position in (
			source.find("\n\tcase ", start + len(marker)),
			source.find("\n\tdefault:", start + len(marker)),
		)
		if position != -1
	]
	end = min(next_markers) if next_markers else len(source)
	return source[start:end]


def test_cgame_impact_effects_are_backed_by_committed_retail_evidence() -> None:
	symbol_map = json.loads(_read(CGAME_SYMBOL_MAP))
	entries = {
		entry["normalized_name"]: entry
		for entry in symbol_map["functions"]
		if "normalized_name" in entry
	}

	for name in (
		"CG_BubbleTrail",
		"CG_SmokePuff",
		"CG_ImpactMark",
		"CG_MissileHitWall",
		"CG_MissileHitPlayer",
		"CG_MissileHitWallDmgThrough",
		"CG_ShotgunPellet",
		"CG_ShotgunPattern",
		"CG_ShotgunFire",
		"CG_Tracer",
		"CG_Bullet",
	):
		assert entries[name]["status"] == "matched"

	ghidra = _read(CGAME_GHIDRA)
	for expected in (
		'DAT_10a5f74c = (**(code **)(DAT_1074cccc + 0xd0))("surfacePuff");',
		"/* FUN_10054db0 @ 10054db0 size 1657 */",
		"FUN_10012f30(local_1770,DAT_1007417c,DAT_10073f74,DAT_10073f74,DAT_1006723c,0x3f800000,",
		"FUN_10053ef0(param_3,0,param_1);",
		"/* FUN_10053ef0 @ 10053ef0 size 3471 */",
	):
		assert expected in ghidra

	functions = _read(CGAME_FUNCTIONS)
	assert "FUN_100561f0,100561f0,506,0,unknown" in functions


def test_cgame_event_dispatch_keeps_retail_impact_effect_wiring() -> None:
	event_block = _block_from_marker(_read(CG_EVENT), "void CG_EntityEvent( centity_t *cent, vec3_t position )")

	dmgthrough = _case_block(event_block, "case EV_MISSILE_MISS_DMGTHROUGH:")
	assert dmgthrough.index("ByteToDir( es->eventParm, dir );") < dmgthrough.index(
		"CG_MissileHitWallDmgThrough( position, dir, es->weapon );"
	)

	missile_hit = _case_block(event_block, "case EV_MISSILE_HIT:")
	assert "CG_MissileHitPlayer( es->weapon, position, dir, es->otherEntityNum );" in missile_hit

	missile_miss = _case_block(event_block, "case EV_MISSILE_MISS:")
	assert "CG_MissileHitWall( es->weapon, 0, position, dir, IMPACTSOUND_DEFAULT );" in missile_miss

	missile_metal = _case_block(event_block, "case EV_MISSILE_MISS_METAL:")
	assert "CG_MissileHitWall( es->weapon, 0, position, dir, IMPACTSOUND_METAL );" in missile_metal

	rail = _case_block(event_block, "case EV_RAILTRAIL:")
	assert rail.index("CG_RailTrail( ci, es->origin2, es->pos.trBase );") < rail.index(
		"CG_MissileHitWall( es->weapon, es->clientNum, position, dir, IMPACTSOUND_DEFAULT );"
	)

	bullet_wall = _case_block(event_block, "case EV_BULLET_HIT_WALL:")
	assert "CG_Bullet( es->pos.trBase, es->otherEntityNum, dir, qfalse, ENTITYNUM_WORLD );" in bullet_wall

	bullet_flesh = _case_block(event_block, "case EV_BULLET_HIT_FLESH:")
	assert "CG_Bullet( es->pos.trBase, es->otherEntityNum, dir, qtrue, es->eventParm );" in bullet_flesh

	shotgun = _case_block(event_block, "case EV_SHOTGUN:")
	assert "CG_ShotgunFire( es );" in shotgun

	shotgun_kill = _case_block(event_block, "case EV_SHOTGUN_KILL:")
	assert "CG_ShotgunKillEffect( cent, es );" in shotgun_kill


def test_cgame_damage_through_impact_sparks_match_retail_surfacepuff_path() -> None:
	weapons = _read(CG_WEAPONS)
	dmgthrough = _block_from_marker(
		weapons,
		"void CG_MissileHitWallDmgThrough( vec3_t origin, vec3_t dir, int weapon )",
	)

	for expected in (
		"probeDistance = CG_GetDamageThroughProbeDistance();",
		"VectorMA( origin, probeDistance, dir, probeOrigin );",
		"CG_Trace( &trace, probeOrigin, NULL, NULL, origin, ENTITYNUM_NONE, CONTENTS_SOLID );",
		"if ( trace.fraction < 1.0f && !trace.startsolid ) {",
		"CG_ImpactMark( cgs.media.burnMarkShader, trace.endpos, trace.plane.normal,",
		"qfalse, 64.0f, qfalse );",
		"if ( cgs.media.surfacePuffShader ) {",
		"for ( i = 0; i < 10; i++ ) {",
		"speed = 250.0f + ( ( random() - 0.5f ) * 300.0f );",
		"VectorScale( trace.plane.normal, speed, velocity );",
		"400.0f - ( speed / 500.0f ) * 200.0f,",
		"cgs.media.surfacePuffShader );",
		"CG_MissileHitWall( weapon, 0, origin, dir, IMPACTSOUND_DEFAULT );",
	):
		assert expected in dmgthrough

	assert dmgthrough.index("if ( cgs.media.surfacePuffShader ) {") < dmgthrough.index(
		"CG_MissileHitWall( weapon, 0, origin, dir, IMPACTSOUND_DEFAULT );"
	)

	particles = _read(CG_PARTICLES)
	assert "static void CG_ParticleSparks (vec3_t org, vec3_t vel, int duration, float x, float y, float speed)" in particles
	assert particles.count("CG_ParticleSparks") == 1


def test_cgame_normal_impact_switch_and_media_registration_stay_wired() -> None:
	weapons = _read(CG_WEAPONS)
	main = _read(CG_MAIN)
	local = _read(CG_LOCAL)

	hitwall = _block_from_marker(
		weapons,
		"void CG_MissileHitWall( int weapon, int clientNum, vec3_t origin, vec3_t dir, impactSound_t soundType )",
	)
	for expected in (
		"case WP_MACHINEGUN:",
		"case WP_HEAVY_MACHINEGUN:",
		"case WP_SHOTGUN:",
		"case WP_CHAINGUN:",
		"case WP_NAILGUN:",
		"case WP_LIGHTNING:",
		"case WP_RAILGUN:",
		"case WP_PLASMAGUN:",
		"case WP_ROCKET_LAUNCHER:",
		"case WP_GRENADE_LAUNCHER:",
		"case WP_PROX_LAUNCHER:",
		"alphaFade = (mark == cgs.media.energyMarkShader);",
		"CG_ResolveClientWeaponColor( ci, NULL, color )",
		"CG_ImpactMark( mark, origin, dir, random()*360, color[0],color[1], color[2],1, alphaFade, radius, qfalse );",
	):
		assert expected in hitwall

	machinegun = _case_block(hitwall, "case WP_MACHINEGUN:")
	for expected in (
		"mod = cgs.media.bulletFlashModel;",
		"shader = cgs.media.bulletExplosionShader;",
		"mark = cgs.media.bulletMarkShader;",
		"sfx = cgs.media.sfx_ric1;",
		"sfx = cgs.media.sfx_ric2;",
		"sfx = cgs.media.sfx_ric3;",
		"radius = 8;",
	):
		assert expected in machinegun

	hmg = _case_block(hitwall, "case WP_HEAVY_MACHINEGUN:")
	for expected in (
		"mod = cgs.media.bulletFlashModel;",
		"shader = cgs.media.bulletExplosionShader;",
		"mark = cgs.media.bulletMarkShader;",
		"radius = 4;",
	):
		assert expected in hmg

	shotgun = _case_block(hitwall, "case WP_SHOTGUN:")
	assert "sfx = 0;" in shotgun
	assert "radius = 4;" in shotgun

	for expected in (
		'cgs.media.surfacePuffShader = trap_R_RegisterShader( "surfacePuff" );',
		'cgs.media.bulletFlashModel = trap_R_RegisterModel("models/weaphits/bullet.md3");',
		'cgs.media.ringFlashModel = trap_R_RegisterModel("models/weaphits/ring02.md3");',
		'cgs.media.dishFlashModel = trap_R_RegisterModel("models/weaphits/boom01.md3");',
		'cgs.media.bulletMarkShader = trap_R_RegisterShader( "gfx/damage/bullet_mrk" );',
		'cgs.media.burnMarkShader = trap_R_RegisterShader( "gfx/damage/burn_med_mrk" );',
		'cgs.media.holeMarkShader = trap_R_RegisterShader( "gfx/damage/hole_lg_mrk" );',
		'cgs.media.energyMarkShader = trap_R_RegisterShader( "gfx/damage/plasma_mrk" );',
		'cgs.media.sfx_ric1 = trap_S_RegisterSound( "sound/weapons/machinegun/ric1.ogg", qfalse );',
		'cgs.media.sfx_nghit = trap_S_RegisterSound( "sound/weapons/nailgun/wnalimpd.ogg", qfalse );',
		'cgs.media.sfx_chghit = trap_S_RegisterSound( "sound/weapons/vulcan/wvulimpd.ogg", qfalse );',
	):
		assert expected in main

	for expected in (
		'cgs.media.lightningExplosionModel = trap_R_RegisterModel( "models/weaphits/crackle.md3" );',
		'cgs.media.sfx_lghit1 = trap_S_RegisterSound( "sound/weapons/lightning/lg_hit.ogg", qfalse );',
		'cgs.media.bulletExplosionShader = trap_R_RegisterShader( "bulletExplosion" );',
	):
		assert expected in weapons

	for expected in (
		"qhandle_t\tsurfacePuffShader;",
		"qhandle_t\tbulletFlashModel;",
		"qhandle_t\tbulletExplosionShader;",
		"void CG_MissileHitWallDmgThrough( vec3_t origin, vec3_t dir, int weapon );",
		"void CG_Bullet( vec3_t origin, int sourceEntityNum, vec3_t normal, qboolean flesh, int fleshEntityNum );",
	):
		assert expected in local
