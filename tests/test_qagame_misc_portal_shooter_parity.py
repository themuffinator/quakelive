from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_MISC = REPO_ROOT / "src" / "code" / "game" / "g_misc.c"
GAME_SPAWN = REPO_ROOT / "src" / "code" / "game" / "g_spawn.c"
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


MISC_PORTAL_SHOOTER_FUNCTIONS = (
	{
		"address": "0x1005A6C0",
		"aliases": ("FUN_1005a6c0", "sub_1005a6c0"),
		"normalized": "locateCamera",
		"signature": "void locateCamera(gentity_t *ent)",
		"ghidra": ("1005a6c0", "FUN_1005a6c0", 349),
	},
	{
		"address": "0x1005A820",
		"aliases": ("sub_1005a820",),
		"normalized": "SP_misc_portal_surface",
		"signature": "void SP_misc_portal_surface(gentity_t *ent)",
		"ghidra": None,
	},
	{
		"address": "0x1005A8C0",
		"aliases": ("sub_1005a8c0",),
		"normalized": "SP_misc_portal_camera",
		"signature": "void SP_misc_portal_camera(gentity_t *ent)",
		"ghidra": None,
	},
	{
		"address": "0x1005A950",
		"aliases": ("FUN_1005a950", "sub_1005a950"),
		"normalized": "Use_Shooter",
		"signature": "void Use_Shooter(gentity_t *ent, gentity_t *other, gentity_t *activator)",
		"ghidra": ("1005a950", "FUN_1005a950", 748),
	},
	{
		"address": "0x1005AC40",
		"aliases": ("FUN_1005ac40", "sub_1005ac40"),
		"normalized": "InitShooter_Finish",
		"signature": "void InitShooter_Finish(gentity_t *ent)",
		"ghidra": ("1005ac40", "FUN_1005ac40", 42),
	},
	{
		"address": "0x1005AC70",
		"aliases": ("FUN_1005ac70", "sub_1005ac70"),
		"normalized": "InitShooter",
		"signature": "void InitShooter(gentity_t *ent, int weapon)",
		"ghidra": ("1005ac70", "FUN_1005ac70", 278),
	},
	{
		"address": "0x1005AD90",
		"aliases": ("FUN_1005ad90", "sub_1005ad90"),
		"normalized": "SP_shooter_rocket",
		"signature": "void SP_shooter_rocket(gentity_t *ent)",
		"ghidra": ("1005ad90", "FUN_1005ad90", 17),
	},
	{
		"address": "0x1005ADB0",
		"aliases": ("FUN_1005adb0", "sub_1005adb0"),
		"normalized": "SP_shooter_plasma",
		"signature": "void SP_shooter_plasma(gentity_t *ent)",
		"ghidra": ("1005adb0", "FUN_1005adb0", 17),
	},
	{
		"address": "0x1005ADD0",
		"aliases": ("FUN_1005add0", "sub_1005add0"),
		"normalized": "SP_shooter_grenade",
		"signature": "void SP_shooter_grenade(gentity_t *ent)",
		"ghidra": ("1005add0", "FUN_1005add0", 17),
	},
	{
		"address": "0x1005ADF0",
		"aliases": ("FUN_1005adf0", "sub_1005adf0"),
		"normalized": "DropPortalDestination",
		"signature": "void DropPortalDestination(gentity_t *player)",
		"ghidra": ("1005adf0", "FUN_1005adf0", 481),
	},
	{
		"address": "0x1005AFE0",
		"aliases": ("FUN_1005afe0", "sub_1005afe0"),
		"normalized": "PortalTouch",
		"signature": "void PortalTouch(gentity_t *self, gentity_t *other, trace_t *trace)",
		"ghidra": ("1005afe0", "FUN_1005afe0", 384),
	},
	{
		"address": "0x1005B160",
		"aliases": ("FUN_1005b160", "sub_1005b160"),
		"normalized": "PortalEnable",
		"signature": "void PortalEnable(gentity_t *self)",
		"ghidra": None,
	},
	{
		"address": "0x1005B190",
		"aliases": ("FUN_1005b190", "sub_1005b190"),
		"normalized": "DropPortalSource",
		"signature": "void DropPortalSource(gentity_t *player)",
		"ghidra": ("1005b190", "FUN_1005b190", 435),
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


def test_qagame_misc_portal_shooter_aliases_metadata_and_hlil_are_pinned() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	hlil = _read(QAGAME_HLIL_PART02)

	for function in MISC_PORTAL_SHOOTER_FUNCTIONS:
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
		"1005a6c0    int32_t sub_1005a6c0(void* arg1)",
		"1005a6e3      sub_10053140(\"Couldn't find target for misc_po…\")",
		"1005a748          *(arg1 + 0xb4) = 0x19",
		"1005a758          *(arg1 + 0xb4) = 0x4b",
		"1005a773      *(arg1 + 0xc4) = (sx.d(not.b(eax_1[0x92].b)) & 4) u>> 2",
		"1005a820    int32_t sub_1005a820(void* arg1)",
		"1005a870  *(arg1 + 0x1e0) = 0x40",
		"1005a897      *(arg1 + 0x2f8) = sub_1005a6c0",
		"1005a8c0    int32_t sub_1005a8c0(long double arg1 @ st0, void* arg2)",
		"1005a931  sub_10065c00(\"roll\", &data_1007d0a8, &arg2)",
		"1005a950    long double sub_1005a950(int32_t* arg1)",
		"1005ab69  if (eax_8 == 4)",
		"1005ab69  else if (eax_8 == 5)",
		"1005ab6c  else if (eax_8 == 8)",
		"1005ac40    int32_t sub_1005ac40(void* arg1)",
		"1005ac51  *(arg1 + 0x344) = sub_1006c010(*(arg1 + 0x2d0))",
		"1005ac70    int32_t __fastcall sub_1005ac70(int32_t arg1, int32_t arg2, void* arg3 @ edi)",
		"1005ac78  *(arg3 + 0x30c) = sub_1005a950",
		"1005ad53      *(arg3 + 0x2f8) = sub_1005ac40",
		"1005ad90    int32_t sub_1005ad90(void* arg1)",
		"1005ada0  return sub_1005ac70(ecx, 5, arg1)",
		"1005adb0    int32_t sub_1005adb0(void* arg1)",
		"1005adc0  return sub_1005ac70(ecx, 8, arg1)",
		"1005add0    int32_t sub_1005add0(void* arg1)",
		"1005ade0  return sub_1005ac70(ecx, 4, arg1)",
		"1005adf0    int32_t sub_1005adf0(void* arg1)",
		"1005ae11  *(eax + 0xa8) = sub_1006be90(\"models/powerups/teleporter/tele_…\")",
		"1005aec5  *(eax + 0x244) = \"hi_portal destination\"",
		"1005aed8  *(eax + 0x204) = 0x4000000",
		"1005aef6  *(eax + 0x314) = sub_1005a660",
		"1005af42  int32_t eax_6 = data_105dea3c + 1",
		"1005afe0    void sub_1005afe0(void* arg1, int32_t* arg2)",
		"1005aff2      int32_t eax = arg2[0x8f]",
		"1005b127                  sub_1005a420(arg1 + 0x29c, edx_1, arg2, arg1 + 0x7c)",
		"1005b160    void* sub_1005b160(void* arg1)",
		"1005b164  *(arg1 + 0x308) = sub_1005afe0",
		"1005b190    void* sub_1005b190(void* arg1)",
		"1005b2e3  *(eax + 0x2f8) = sub_1005b160",
		"100806a0  char const (* data_100806a0)[0x14] = data_100895fc {\"misc_portal_surface\"}",
		"100806a4  void* data_100806a4 = sub_1005a820",
		"100806a8  char const (* data_100806a8)[0x13] = data_100895e8 {\"misc_portal_camera\"}",
		"100806ac  void* data_100806ac = sub_1005a8c0",
		"100806b0  char const (* data_100806b0)[0xf] = data_100895d8 {\"shooter_rocket\"}",
		"100806b4  void* data_100806b4 = sub_1005ad90",
		"100806b8  char const (* data_100806b8)[0x10] = data_100895c8 {\"shooter_grenade\"}",
		"100806bc  void* data_100806bc = sub_1005add0",
		"100806c0  char const (* data_100806c0)[0xf] = data_100895b8 {\"shooter_plasma\"}",
		"100806c4  void* data_100806c4 = sub_1005adb0",
	):
		assert expected in hlil


def test_qagame_misc_portal_surface_and_camera_source_paths_match_retail() -> None:
	g_misc = _read(GAME_MISC)
	locate_body = _extract_function_block(g_misc, "void locateCamera( gentity_t *ent )")
	surface_body = _extract_function_block(g_misc, "void SP_misc_portal_surface(gentity_t *ent)")
	camera_body = _extract_function_block(g_misc, "void SP_misc_portal_camera(gentity_t *ent)")

	for expected in (
		"owner = G_PickTarget( ent->target );",
		'G_Printf( "Couldn\'t find target for misc_partal_surface\\n" );',
		"G_FreeEntity( ent );",
		"ent->r.ownerNum = owner->s.number;",
		"ent->s.frame = 25;",
		"ent->s.frame = 75;",
		"ent->s.powerups = 0;",
		"ent->s.powerups = 1;",
		"ent->s.clientNum = owner->s.clientNum;",
		"VectorCopy( owner->s.origin, ent->s.origin2 );",
		"target = G_PickTarget( owner->target );",
		"VectorSubtract( target->s.origin, owner->s.origin, dir );",
		"G_SetMovedir( owner->s.angles, dir );",
		"ent->s.eventParm = DirToByte( dir );",
	):
		assert expected in locate_body

	for expected in (
		"VectorClear( ent->r.mins );",
		"VectorClear( ent->r.maxs );",
		"trap_LinkEntity (ent);",
		"ent->r.svFlags = SVF_PORTAL;",
		"ent->s.eType = ET_PORTAL;",
		"VectorCopy( ent->s.origin, ent->s.origin2 );",
		"ent->think = locateCamera;",
		"ent->nextthink = level.time + 100;",
	):
		assert expected in surface_body

	for expected in (
		"VectorClear( ent->r.mins );",
		"VectorClear( ent->r.maxs );",
		"trap_LinkEntity (ent);",
		'G_SpawnFloat( "roll", "0", &roll );',
		"ent->s.clientNum = roll/360.0 * 256;",
	):
		assert expected in camera_body


def test_qagame_shooter_source_paths_match_retail() -> None:
	g_misc = _read(GAME_MISC)
	use_body = _extract_function_block(
		g_misc,
		"void Use_Shooter( gentity_t *ent, gentity_t *other, gentity_t *activator )",
	)
	finish_body = _extract_function_block(g_misc, "static void InitShooter_Finish( gentity_t *ent )")
	init_body = _extract_function_block(g_misc, "void InitShooter( gentity_t *ent, int weapon )")
	rocket_body = _extract_function_block(g_misc, "void SP_shooter_rocket( gentity_t *ent )")
	plasma_body = _extract_function_block(g_misc, "void SP_shooter_plasma( gentity_t *ent )")
	grenade_body = _extract_function_block(g_misc, "void SP_shooter_grenade( gentity_t *ent )")

	for expected in (
		"if ( ent->enemy )",
		"VectorSubtract( ent->enemy->r.currentOrigin, ent->s.origin, dir );",
		"VectorCopy( ent->movedir, dir );",
		"PerpendicularVector( up, dir );",
		"CrossProduct( up, dir, right );",
		"deg = crandom() * ent->random;",
		"VectorMA( dir, deg, up, dir );",
		"VectorMA( dir, deg, right, dir );",
		"case WP_GRENADE_LAUNCHER:",
		"fire_grenade( ent, ent->s.origin, dir );",
		"case WP_ROCKET_LAUNCHER:",
		"fire_rocket( ent, ent->s.origin, dir );",
		"case WP_PLASMAGUN:",
		"fire_plasma( ent, ent->s.origin, dir );",
		"G_AddEvent( ent, EV_FIRE_WEAPON, 0 );",
	):
		assert expected in use_body

	for expected in (
		"ent->enemy = G_PickTarget( ent->target );",
		"ent->think = 0;",
		"ent->nextthink = 0;",
	):
		assert expected in finish_body

	for expected in (
		"ent->use = Use_Shooter;",
		"ent->s.weapon = weapon;",
		"RegisterItem( BG_FindItemForWeapon( weapon ) );",
		"G_SetMovedir( ent->s.angles, ent->movedir );",
		"ent->random = 1.0;",
		"ent->random = sin( M_PI * ent->random / 180 );",
		"ent->think = InitShooter_Finish;",
		"ent->nextthink = level.time + 500;",
		"trap_LinkEntity( ent );",
	):
		assert expected in init_body

	assert "InitShooter( ent, WP_ROCKET_LAUNCHER );" in rocket_body
	assert "InitShooter( ent, WP_PLASMAGUN);" in plasma_body
	assert "InitShooter( ent, WP_GRENADE_LAUNCHER);" in grenade_body


def test_qagame_holdable_portal_source_paths_match_retail() -> None:
	g_misc = _read(GAME_MISC)
	destination_body = _extract_function_block(g_misc, "void DropPortalDestination( gentity_t *player )")
	touch_body = _extract_function_block(
		g_misc,
		"static void PortalTouch( gentity_t *self, gentity_t *other, trace_t *trace)",
	)
	enable_body = _extract_function_block(g_misc, "static void PortalEnable( gentity_t *self )")
	source_body = _extract_function_block(g_misc, "void DropPortalSource( gentity_t *player )")

	for expected in (
		'ent->s.modelindex = G_ModelIndex( "models/powerups/teleporter/tele_exit.md3" );',
		"VectorCopy( player->s.pos.trBase, snapped );",
		"SnapVector( snapped );",
		"G_SetOrigin( ent, snapped );",
		"VectorCopy( player->r.mins, ent->r.mins );",
		"VectorCopy( player->r.maxs, ent->r.maxs );",
		'ent->classname = "hi_portal destination";',
		"ent->s.pos.trType = TR_STATIONARY;",
		"ent->r.contents = CONTENTS_CORPSE;",
		"ent->takedamage = qtrue;",
		"ent->health = 200;",
		"ent->die = ( void (*)( gentity_t *self, gentity_t *inflictor, gentity_t *attacker, int damage, int mod ) )G_FreeEntity;",
		"VectorCopy( player->s.apos.trBase, ent->s.angles );",
		"ent->think = G_FreeEntity;",
		"ent->nextthink = level.time + 2 * 60 * 1000;",
		"trap_LinkEntity( ent );",
		"player->client->portalID = ++level.portalSequence;",
		"ent->count = player->client->portalID;",
		'player->client->ps.stats[STAT_HOLDABLE_ITEM] = BG_FindItem( "Portal" ) - bg_itemlist;',
	):
		assert expected in destination_body

	for expected in (
		"if( other->health <= 0 )",
		"if( !other->client )",
		"G_TossFlag( other, PW_NEUTRALFLAG, FLAG_DROP_CONTEXT_SCRIPTED, NULL, MOD_UNKNOWN, NULL );",
		"G_TossFlag( other, PW_REDFLAG, FLAG_DROP_CONTEXT_SCRIPTED, NULL, MOD_UNKNOWN, NULL );",
		"G_TossFlag( other, PW_BLUEFLAG, FLAG_DROP_CONTEXT_SCRIPTED, NULL, MOD_UNKNOWN, NULL );",
		'destination = G_Find(destination, FOFS(classname), "hi_portal destination")',
		"if( destination->count == self->count )",
		"TeleportPlayer( other, self->pos1, self->s.angles );",
		"G_Damage( other, other, other, NULL, NULL, 100000, DAMAGE_NO_PROTECTION, MOD_TELEFRAG );",
		"TeleportPlayer( other, destination->s.pos.trBase, destination->s.angles );",
	):
		assert expected in touch_body

	for expected in (
		"self->touch = PortalTouch;",
		"self->think = G_FreeEntity;",
		"self->nextthink = level.time + 2 * 60 * 1000;",
	):
		assert expected in enable_body

	for expected in (
		'ent->s.modelindex = G_ModelIndex( "models/powerups/teleporter/tele_enter.md3" );',
		"VectorCopy( player->s.pos.trBase, snapped );",
		"SnapVector( snapped );",
		"G_SetOrigin( ent, snapped );",
		"VectorCopy( player->r.mins, ent->r.mins );",
		"VectorCopy( player->r.maxs, ent->r.maxs );",
		'ent->classname = "hi_portal source";',
		"ent->s.pos.trType = TR_STATIONARY;",
		"ent->r.contents = CONTENTS_CORPSE | CONTENTS_TRIGGER;",
		"ent->takedamage = qtrue;",
		"ent->health = 200;",
		"ent->die = ( void (*)( gentity_t *self, gentity_t *inflictor, gentity_t *attacker, int damage, int mod ) )G_FreeEntity;",
		"trap_LinkEntity( ent );",
		"ent->count = player->client->portalID;",
		"player->client->portalID = 0;",
		"ent->nextthink = level.time + 1000;",
		"ent->think = PortalEnable;",
		'destination = G_Find(destination, FOFS(classname), "hi_portal destination")',
		"VectorCopy( destination->s.pos.trBase, ent->pos1 );",
	):
		assert expected in source_body


def test_qagame_misc_portal_and_shooter_spawn_order_matches_retail() -> None:
	g_spawn = _read(GAME_SPAWN)
	expected = [
		'{"misc_teleporter_dest", SP_misc_teleporter_dest}',
		'{"misc_model", SP_misc_model}',
		'{"advertisement", SP_advertisement}',
		'{"misc_portal_surface", SP_misc_portal_surface}',
		'{"misc_portal_camera", SP_misc_portal_camera}',
		'{"race_point", SP_race_point}',
		'{"shooter_rocket", SP_shooter_rocket}',
		'{"shooter_grenade", SP_shooter_grenade}',
		'{"shooter_plasma", SP_shooter_plasma}',
	]

	positions = [g_spawn.index(entry) for entry in expected]
	assert positions == sorted(positions)
