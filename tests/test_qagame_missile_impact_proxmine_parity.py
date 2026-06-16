from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_MISSILE = REPO_ROOT / "src" / "code" / "game" / "g_missile.c"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
QAGAME_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "qagame.json"
QAGAME_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "functions.csv"
)
QAGAME_HLIL_PART02 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part02.txt"
)


MISSILE_IMPACT_PROXMINE_FUNCTIONS = (
	{
		"address": "0x1005B350",
		"aliases": ("FUN_1005b350", "sub_1005b350"),
		"normalized": "G_BounceMissile",
		"signature": "void G_BounceMissile(gentity_t *ent, trace_t *trace)",
		"ghidra": ("1005b350", "FUN_1005b350", 423),
	},
	{
		"address": "0x1005B500",
		"aliases": ("FUN_1005b500", "sub_1005b500"),
		"normalized": "G_ExplodeMissile",
		"signature": "void G_ExplodeMissile(gentity_t *ent)",
		"ghidra": ("1005b500", "FUN_1005b500", 533),
	},
	{
		"address": "0x1005B730",
		"aliases": ("FUN_1005b730", "sub_1005b730"),
		"normalized": "ProximityMine_Explode",
		"signature": "void ProximityMine_Explode(gentity_t *mine)",
		"ghidra": None,
	},
	{
		"address": "0x1005B7A0",
		"aliases": ("FUN_1005b7a0", "sub_1005b7a0"),
		"normalized": "ProximityMine_Die",
		"signature": "void ProximityMine_Die(gentity_t *ent, gentity_t *inflictor, gentity_t *attacker, int damage, int mod)",
		"ghidra": None,
	},
	{
		"address": "0x1005B7C0",
		"aliases": ("FUN_1005b7c0", "sub_1005b7c0"),
		"normalized": "ProximityMine_Trigger",
		"signature": "void ProximityMine_Trigger(gentity_t *trigger, gentity_t *other, trace_t *trace)",
		"ghidra": ("1005b7c0", "FUN_1005b7c0", 221),
	},
	{
		"address": "0x1005B8A0",
		"aliases": ("FUN_1005b8a0", "sub_1005b8a0"),
		"normalized": "ProximityMine_Activate",
		"signature": "void ProximityMine_Activate(gentity_t *ent)",
		"ghidra": None,
	},
	{
		"address": "0x1005B9D0",
		"aliases": ("FUN_1005b9d0", "sub_1005b9d0"),
		"normalized": "ProximityMine_ExplodeOnPlayer",
		"signature": "void ProximityMine_ExplodeOnPlayer(gentity_t *mine)",
		"ghidra": None,
	},
	{
		"address": "0x1005BAB0",
		"aliases": ("FUN_1005bab0", "sub_1005bab0"),
		"normalized": "ProximityMine_Player",
		"signature": "void ProximityMine_Player(gentity_t *mine, gentity_t *player)",
		"ghidra": ("1005bab0", "FUN_1005bab0", 292),
	},
	{
		"address": "0x1005BBE0",
		"aliases": ("FUN_1005bbe0", "sub_1005bbe0"),
		"normalized": "G_MissileImpact",
		"signature": "void G_MissileImpact(gentity_t *ent, trace_t *trace)",
		"ghidra": ("1005bbe0", "FUN_1005bbe0", 3347),
	},
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _extract_function_block(text: str, signature: str) -> str:
	scan_text = "\n".join(line.split("//", 1)[0] for line in text.splitlines())
	start = scan_text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = scan_text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(scan_text)):
		char = scan_text[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return scan_text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def _function_rows_by_entry(path: Path) -> dict[str, dict[str, str]]:
	with path.open(newline="", encoding="utf-8") as file:
		return {row["entry"].lower(): row for row in csv.DictReader(file)}


def test_qagame_missile_impact_proxmine_aliases_metadata_and_hlil_are_pinned() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	hlil = _read(QAGAME_HLIL_PART02)

	for function in MISSILE_IMPACT_PROXMINE_FUNCTIONS:
		for raw_name in function["aliases"]:
			assert aliases[raw_name] == function["normalized"]

		symbol = symbol_map[function["address"].lower()]
		assert symbol["normalized_name"] == function["normalized"]
		assert symbol["signature"] == function["signature"]
		assert symbol["status"] == "matched"

		if function["ghidra"]:
			entry, raw_name, size = function["ghidra"]
			row = function_rows[entry]
			assert row["name"] == raw_name
			assert int(row["size"]) == size
			assert row["thunk"] == "0"

	for expected in (
		"1005b350    void sub_1005b350(float arg1)",
		"1005b3eb      long double x87_r6_7 = fconvert.t(0.65000000000000002)",
		"1005b449          if (not(fconvert.t(40f) <= fconvert.t(fconvert.s(x87_r7_13 * x87_r7_13",
		"1005b4f0  *(ebx + 0x10) = data_105dce5c",
		"1005b500    int32_t sub_1005b500(int32_t arg1)",
		"1005b517  sub_1002d210(data_105dce5c, arg1 + 0xc, &var_c)",
		"1005b5a9  int32_t eax_3 = sub_10070110(&var_c)",
		"1005b61e  *(arg1 + 0x264) = 1",
		"1005b62a  if (*(arg1 + 0x330) != 0)",
		"1005b714  return (*(data_104b13ac + 0x9c))(arg1)",
		"1005b730    int32_t sub_1005b730(int32_t arg1)",
		"1005b737  int32_t result = sub_1005b500(arg1)",
		"1005b770          *(esi + 0x244) = \"freed\"",
		"1005b793      *(arg1 + 0x348) = 0",
		"1005b7a0    void* sub_1005b7a0(void* arg1)",
		"1005b7a4  *(arg1 + 0x2f8) = sub_1005b730",
		"1005b7b5  *(arg1 + 0x2f4) = data_105dce5c + 1",
		"1005b7c0    void sub_1005b7c0(void* arg1, int32_t* arg2)",
		"1005b7d6  if (arg2[0x8f] != 0)",
		"1005b861          void* eax_3 = *(arg1 + 0x290)",
		"1005b876          sub_1006c660(eax_3, 0, 0x42)",
		"1005b8a0    int32_t sub_1005b8a0(void* arg1)",
		"1005b8a6  *(arg1 + 0x2f8) = sub_1005b730",
		"1005b8c2  *(arg1 + 0x2f4) = data_105a4bac * 0x3e8 + data_105dce5c",
		"1005b8e4  *(arg1 + 0x314) = sub_1005b7a0",
		"1005b8f3  *(arg1 + 0xa4) = sub_1006be90(\"sound/weapons/proxmine/wstbtick.…\")",
		"1005b906  *(eax_4 + 0x244) = \"proxmine_trigger\"",
		"1005b9b0  *(eax_4 + 0x308) = sub_1005b7c0",
		"1005b9c6  *(arg1 + 0x348) = eax_4",
		"1005b9d0    void* sub_1005b9d0(int32_t arg1)",
		"1005b9e1  *(ecx + 0x68) &= 0xfffffffd",
		"1005ba20      *(*(esi i+ 0x23c) + 0x564) = 0",
		"1005ba3f      return sub_1006c490(*(esi i+ 0x23c) + 0x14, 0x47)",
		"1005baa0  return sub_1005b500(arg1) __tailcall",
		"1005bab0    void __convention(\"regparm\") sub_1005bab0(void* arg1, int32_t arg2, void* arg3)",
		"1005bb42          *(ecx + 0x330) += *(arg1 + 0x330)",
		"1005bb48          *(arg1 + 0x2f8) = sub_1005a660",
		"1005bb65      *(edx_9 + 0x68) |= 2",
		"1005bb72      *(arg1 + 8) |= 0x80",
		"1005bb9c      *(arg1 + 0x2f8) = sub_1005b9d0",
		"1005bbc0          *(arg1 + 0x2f4) = ecx_2 + 0x7d0",
		"1005bbcd      *(arg1 + 0x2f4) = ecx_2 + 0x2710",
		"1005bbe0    int32_t* __convention(\"regparm\") sub_1005bbe0",
		"1005be09                  arg4[0xbe] = sub_1005b8a0",
		"1005be4a                  arg4[0xc5] = sub_1005b7a0",
		"1005bd8b                  sub_1005bab0(result, 0, edi_2)",
		"1005bf05              char const* const esi_5 = \"hook\"",
		"1005c092                      edx_6 = sub_1006c660(arg4, sub_10070110(arg3 i+ 0x18), 0x30)",
		"1005c4ad                      edx_14 = sub_1006c660(arg4, sub_10070110(arg3 i+ 0x18), 0x56)",
		"1005c8d5                  result = (*(data_104b13ac + 0x9c))(arg4)",
	):
		assert expected in hlil


def test_qagame_bounce_and_explode_source_paths_match_retail() -> None:
	g_missile = _read(GAME_MISSILE)
	bounce_body = _extract_function_block(g_missile, "void G_BounceMissile( gentity_t *ent, trace_t *trace )")
	explode_body = _extract_function_block(g_missile, "void G_ExplodeMissile( gentity_t *ent )")

	for expected in (
		"hitTime = level.previousTime + ( level.time - level.previousTime ) * trace->fraction;",
		"BG_EvaluateTrajectoryDelta( &ent->s.pos, hitTime, velocity );",
		"dot = DotProduct( velocity, trace->plane.normal );",
		"VectorMA( velocity, -2*dot, trace->plane.normal, ent->s.pos.trDelta );",
		"if ( ent->s.eFlags & EF_BOUNCE_HALF )",
		"VectorScale( ent->s.pos.trDelta, 0.65, ent->s.pos.trDelta );",
		"trace->plane.normal[2] > 0.2 && VectorLength( ent->s.pos.trDelta ) < 40",
		"G_SetOrigin( ent, trace->endpos );",
		"VectorAdd( ent->r.currentOrigin, trace->plane.normal, ent->r.currentOrigin);",
		"VectorCopy( ent->r.currentOrigin, ent->s.pos.trBase );",
		"ent->s.pos.trTime = level.time;",
	):
		assert expected in bounce_body

	for expected in (
		"BG_EvaluateTrajectory( &ent->s.pos, level.time, origin );",
		"SnapVector( origin );",
		"G_SetOrigin( ent, origin );",
		"dir[0] = dir[1] = 0;",
		"dir[2] = 1;",
		"ent->s.eType = ET_GENERAL;",
		"G_AddEvent( ent, EV_MISSILE_MISS, DirToByte( dir ) );",
		"ent->freeAfterEvent = qtrue;",
		"if ( ent->splashDamage )",
		"G_RadiusDamage( ent->r.currentOrigin, ent->parent, ent->splashDamage, ent->splashRadius, ent",
		"g_entities[ent->r.ownerNum].client->accuracy_hits++;",
		"g_entities[ent->r.ownerNum].client->pers.accuracy_hits[ent->s.weapon]++;",
		"trap_LinkEntity( ent );",
	):
		assert expected in explode_body


def test_qagame_proxmine_source_paths_match_retail() -> None:
	g_missile = _read(GAME_MISSILE)
	explode_body = _extract_function_block(g_missile, "static void ProximityMine_Explode( gentity_t *mine )")
	die_body = _extract_function_block(
		g_missile,
		"static void ProximityMine_Die( gentity_t *ent, gentity_t *inflictor, gentity_t *attacker, int damage, int mod )",
	)
	trigger_body = _extract_function_block(g_missile, "void ProximityMine_Trigger( gentity_t *trigger, gentity_t *other, trace_t *trace )")
	activate_body = _extract_function_block(g_missile, "static void ProximityMine_Activate( gentity_t *ent )")
	explode_on_player_body = _extract_function_block(g_missile, "static void ProximityMine_ExplodeOnPlayer( gentity_t *mine )")
	player_body = _extract_function_block(g_missile, "static void ProximityMine_Player( gentity_t *mine, gentity_t *player )")

	for expected in (
		"G_ExplodeMissile( mine );",
		"if (mine->activator)",
		"G_FreeEntity(mine->activator);",
		"mine->activator = NULL;",
	):
		assert expected in explode_body

	for expected in (
		"ent->think = ProximityMine_Explode;",
		"ent->nextthink = level.time + 1;",
	):
		assert expected in die_body

	for expected in (
		"if( !other->client )",
		"VectorSubtract( trigger->s.pos.trBase, other->s.pos.trBase, v );",
		"VectorLength( v ) > trigger->parent->splashRadius",
		"if ( g_gametype.integer >= GT_TEAM )",
		"trigger->parent->s.generic1 == other->client->sess.sessionTeam",
		"if( !CanDamage( other, trigger->s.pos.trBase ) )",
		"mine = trigger->parent;",
		"mine->s.loopSound = 0;",
		"G_AddEvent( mine, EV_PROXIMITY_MINE_TRIGGER, 0 );",
		"mine->nextthink = level.time + 500;",
		"G_FreeEntity( trigger );",
	):
		assert expected in trigger_body

	for expected in (
		"ent->think = ProximityMine_Explode;",
		"ent->nextthink = level.time + g_proxMineTimeout.integer * 1000;",
		"ent->takedamage = qtrue;",
		"ent->health = 1;",
		"ent->die = ProximityMine_Die;",
		'ent->s.loopSound = G_SoundIndex( "sound/weapons/proxmine/wstbtick.wav" );',
		"trigger = G_Spawn ();",
		'trigger->classname = "proxmine_trigger";',
		"r = ent->splashRadius;",
		"VectorSet( trigger->r.mins, -r, -r, -r );",
		"VectorSet( trigger->r.maxs, r, r, r );",
		"G_SetOrigin( trigger, ent->s.pos.trBase );",
		"trigger->parent = ent;",
		"trigger->r.contents = CONTENTS_TRIGGER;",
		"trigger->touch = ProximityMine_Trigger;",
		"trap_LinkEntity (trigger);",
		"ent->activator = trigger;",
	):
		assert expected in activate_body

	for expected in (
		"player = mine->enemy;",
		"player->client->ps.eFlags &= ~EF_TICKING;",
		"if ( player->client->invulnerabilityTime > level.time )",
		"G_Damage( player, mine->parent, mine->parent, vec3_origin, mine->s.origin, 1000, DAMAGE_NO_KNOCKBACK, MOD_JUICED );",
		"player->client->invulnerabilityTime = 0;",
		"player->client->holdableInvulnerabilityTime = 0;",
		"G_TempEntity( player->client->ps.origin, EV_JUICED );",
		"G_SetOrigin( mine, player->s.pos.trBase );",
		"mine->r.svFlags &= ~SVF_NOCLIENT;",
		"mine->splashMethodOfDeath = MOD_PROXIMITY_MINE;",
		"G_ExplodeMissile( mine );",
	):
		assert expected in explode_on_player_body

	for expected in (
		"if( mine->s.eFlags & EF_NODRAW )",
		"G_AddEvent( mine, EV_PROXIMITY_MINE_STICK, 0 );",
		"if( player->s.eFlags & EF_TICKING )",
		"player->activator->splashDamage += mine->splashDamage;",
		"player->activator->splashRadius *= 1.50;",
		"mine->think = G_FreeEntity;",
		"mine->nextthink = level.time;",
		"player->client->ps.eFlags |= EF_TICKING;",
		"player->activator = mine;",
		"mine->s.eFlags |= EF_NODRAW;",
		"mine->r.svFlags |= SVF_NOCLIENT;",
		"mine->s.pos.trType = TR_LINEAR;",
		"VectorClear( mine->s.pos.trDelta );",
		"mine->enemy = player;",
		"mine->think = ProximityMine_ExplodeOnPlayer;",
		"mine->nextthink = level.time + 2 * 1000;",
		"mine->nextthink = level.time + 10 * 1000;",
	):
		assert expected in player_body


def test_qagame_missile_impact_source_path_matches_retail() -> None:
	g_missile = _read(GAME_MISSILE)
	impact_body = _extract_function_block(g_missile, "void G_MissileImpact( gentity_t *ent, trace_t *trace )")

	for expected in (
		"other = &g_entities[trace->entityNum];",
		"ent->s.eFlags & ( EF_BOUNCE | EF_BOUNCE_HALF )",
		"G_BounceMissile( ent, trace );",
		"G_AddEvent( ent, EV_GRENADE_BOUNCE, 0 );",
		'other->s.eType == ET_MOVER && ( !Q_stricmp( other->classname, "func_train" ) || !Q_stricmp( other->classname, "func_rotating" ) )',
		"ent->s.weapon != WP_PROX_LAUNCHER",
		"other->client && other->client->invulnerabilityTime > level.time",
		"G_InvulnerabilityEffect( other, forward, ent->s.pos.trBase, impactpoint, bouncedir )",
		"ent->target_ent = other;",
		"LogAccuracyHit( other, &g_entities[ent->r.ownerNum] )",
		"BG_EvaluateTrajectoryDelta( &ent->s.pos, level.time, velocity );",
		"velocity[2] = 1;",
		"G_Damage (other, ent, &g_entities[ent->r.ownerNum], velocity,",
		"if( ent->s.weapon == WP_PROX_LAUNCHER )",
		"if( ent->s.pos.trType != TR_GRAVITY )",
		"ProximityMine_Player( ent, other );",
		"SnapVectorTowards( trace->endpos, ent->s.pos.trBase );",
		"ent->s.pos.trType = TR_STATIONARY;",
		"G_AddEvent( ent, EV_PROXIMITY_MINE_STICK, trace->surfaceFlags );",
		"ent->think = ProximityMine_Activate;",
		"ent->nextthink = level.time + 2000;",
		"ent->die = ProximityMine_Die;",
		"VectorCopy(trace->plane.normal, ent->movedir);",
		"if (!strcmp(ent->classname, \"hook\"))",
		"G_AddEvent( nent, EV_MISSILE_HIT, DirToByte( trace->plane.normal ) );",
		"ent->s.eType = ET_GRAPPLE;",
		"ent->think = Weapon_HookThink;",
		"ent->parent->client->ps.pm_flags |= PMF_GRAPPLE_PULL;",
		"Weapon_UpdateHookGrapplePoint( ent );",
		"G_AddEvent( ent, EV_MISSILE_HIT, DirToByte( trace->plane.normal ) );",
		"G_AddEvent( ent, EV_MISSILE_MISS_METAL, DirToByte( trace->plane.normal ) );",
		"G_AddEvent( ent, EV_MISSILE_MISS_DMGTHROUGH, DirToByte( trace->plane.normal ) );",
		"G_AddEvent( ent, EV_MISSILE_MISS, DirToByte( trace->plane.normal ) );",
		"ent->freeAfterEvent = qtrue;",
		"ent->s.eType = ET_GENERAL;",
		"G_SetOrigin( ent, trace->endpos );",
		"VectorCopy( trace->endpos, splashOrigin );",
		"VectorCopy( trace->plane.normal, normal );",
		"normalLength = VectorLengthSquared( normal );",
		"VectorMA( splashOrigin, g_splashdamageOffset.value, normal, splashOrigin );",
		"ent->s.weapon == WP_ROCKET_LAUNCHER && g_weaponConfig.rocketSplashOffset != 0",
		"splashOffset = ( float )g_weaponConfig.rocketSplashOffset;",
		"VectorMA( splashOrigin, splashOffset, normal, splashOrigin );",
		"G_RadiusDamage( splashOrigin, ent->parent, ent->splashDamage, ent->splashRadius,",
		"if( !hitClient )",
		"trap_LinkEntity( ent );",
	):
		assert expected in impact_body
