import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _function_body(source: str, signature: str) -> str:
	start = source.index(signature)
	brace = source.index("{", start)
	depth = 1
	index = brace + 1

	while depth > 0:
		if source[index] == "{":
			depth += 1
		elif source[index] == "}":
			depth -= 1
		index += 1

	return source[brace + 1 : index - 1]


def test_ammo_pack_item_metadata_matches_retail_table() -> None:
	bg_misc = _read("src/code/game/bg_misc.c")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt")

	assert re.search(
		r'\{\s*"ammo_pack",\s*'
		r'"sound/misc/am_pkup.wav",\s*'
		r'\{\s*"models/powerups/ammo/ammopack.md3",\s*0,\s*0,\s*0\},\s*'
		r'/\* icon \*/\s*"icons/ammo_pack",\s*'
		r'/\* pickup \*/\s*"Ammo Pack",\s*'
		r"1,\s*IT_AMMO,\s*WP_NUM_WEAPONS,",
		bg_misc,
		re.DOTALL,
	)

	for expected in (
		'10081970  char const (* data_10081970)[0xa] = data_1007e600 {"ammo_pack"}',
		'10081974  char const (* data_10081974)[0x17] = data_1007f348 {"sound/misc/am_pkup.wav"}',
		'10081978  char const (* data_10081978)[0x22] = data_1007e5dc {"models/powerups/ammo/ammopack.md',
		'10081998  char const (* data_10081998)[0x10] = data_1007e5cc {"icons/ammo_pack"}',
		'1008199c  char const (* data_1008199c)[0xa] = data_1007e5c0 {"Ammo Pack"}',
		"100819a0  01 00 00 00 02 00 00 00 0f 00 00 00",
	):
		assert expected in qagame_hlil


def test_ammo_pack_grab_rule_uses_owned_weapon_sentinel_scan() -> None:
	bg_misc = _read("src/code/game/bg_misc.c")
	body = _function_body(
		bg_misc,
		"qboolean BG_CanItemBeGrabbed( int gametype, int currentTime, const entityState_t *ent, const playerState_t *ps )",
	)
	ammo_case = body[body.index("case IT_AMMO:") : body.index("case IT_ARMOR:")]

	assert "if ( item->giTag == WP_NUM_WEAPONS ) {" in ammo_case
	assert "for ( weapon = WP_MACHINEGUN ; weapon < WP_NUM_WEAPONS ; weapon++ ) {" in ammo_case
	assert "maxAmmo = BG_GetWeaponMaxAmmo( weapon );" in ammo_case
	assert "if ( !( ps->stats[STAT_WEAPONS] & ( 1 << weapon ) ) ) {" in ammo_case
	assert "if ( ps->ammo[weapon] < maxAmmo ) {" in ammo_case
	assert ammo_case.index("if ( item->giTag == WP_NUM_WEAPONS ) {") < ammo_case.index(
		"weapon = BG_WeaponForItemTag( item->giTag );"
	)


def test_add_ammo_owns_retail_ammo_pack_sentinel_and_pickup_forwards_item_tag() -> None:
	items_c = _read("src/code/game/g_items.c")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt")
	qagame_symbols = _read("references/symbol-maps/qagame.json")
	add_body = _function_body(items_c, "void Add_Ammo (gentity_t *ent, int weapon, int count)")
	pickup_body = _function_body(items_c, "int Pickup_Ammo (gentity_t *ent, gentity_t *other)")

	assert "if ( weaponIndex == WP_NUM_WEAPONS ) {" in add_body
	assert "for ( ownedWeapon = WP_MACHINEGUN; ownedWeapon < WP_NUM_WEAPONS; ownedWeapon++ ) {" in add_body
	assert "ent->client->ps.stats[STAT_WEAPONS] & ( 1 << ownedWeapon )" in add_body
	assert "ammoPackCount = G_GetAmmoPackPickupCount( (weapon_t)ownedWeapon, 0 );" in add_body
	assert "Add_Ammo( ent, ownedWeapon, ammoPackCount );" in add_body
	assert add_body.index("if ( weaponIndex == WP_NUM_WEAPONS ) {") < add_body.index(
		"if ( weaponIndex <= WP_NONE || weaponIndex >= WP_NUM_WEAPONS ) {"
	)

	assert "quantity = ent->count;" in pickup_body
	assert "if ( quantity == 0 ) {" in pickup_body
	assert "quantity = ent->item->quantity;" in pickup_body
	assert "Add_Ammo( other, BG_WeaponForItemTag( ent->item->giTag ), quantity );" in pickup_body
	assert "ent->item->giTag == WP_NUM_WEAPONS" not in pickup_body
	assert "G_GetAmmoPackPickupCount" not in pickup_body
	assert "for ( weapon = WP_MACHINEGUN" not in pickup_body

	for expected in (
		"1004dafa      if (arg1 != 0xf)",
		"1004dafc          int32_t ecx_2 = 4",
		"1004db01          int32_t i = 0x188",
		"1004db06          void* esi_1 = &data_1008ff74",
		"1004db1c              if ((edx_1[0x33] & ecx_2) != 0)",
		"1004db20                  *(edx_1 + i) += *esi_1",
		"1004e520  sub_1004dab0(*(*(arg3 + 0x37c) + 0x38), arg2)",
	):
		assert expected in qagame_hlil

	for expected in (
		'"normalized_name": "Add_Ammo"',
		'"signature": "void Add_Ammo(gentity_t *ent, int weapon, int count)"',
		'"normalized_name": "Pickup_Ammo"',
		'"signature": "int Pickup_Ammo(gentity_t *ent, gentity_t *other)"',
		"Exact retail ammo pickup helper. It forwards the item tag and resolved pickup quantity into `Add_Ammo`",
	):
		assert expected in qagame_symbols


def test_ammo_pack_factory_gate_switches_global_and_weapon_ammo_families() -> None:
	items_c = _read("src/code/game/g_items.c")
	config_c = _read("src/game/g_config.c")
	g_main = _read("src/code/game/g_main.c")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt")
	spawn_body = _function_body(items_c, "static qboolean G_ItemFactorySpawnAllowed( const gitem_t *item )")
	ammo_case = spawn_body[spawn_body.index("case IT_AMMO:") : spawn_body.index("default:")]

	assert """case IT_AMMO:
		if ( !g_factoryCvarConfig.spawnItemAmmo ) {
			return qfalse;
		}

		if ( item->giTag == WP_NUM_WEAPONS ) {
			return ( g_factoryCvarConfig.ammoPackEnabled || g_factoryCvarConfig.ammoPackHackEnabled ) ? qtrue : qfalse;
		}

		return ( g_factoryCvarConfig.ammoPackEnabled || g_factoryCvarConfig.ammoPackHackEnabled ) ? qfalse : qtrue;""" in ammo_case

	for expected in (
		'{ &g_ammoPack,             "g_ammoPack",             STRINGIZE( DEFAULT_AMMO_PACK_TOGGLE ), CVAR_ARCHIVE',
		'{ &g_ammoPackHack,         "g_ammoPackHack",         STRINGIZE( DEFAULT_AMMO_PACK_HACK ), CVAR_ARCHIVE',
		"config.ammoPackEnabled = G_ReadFactoryBoolCvar( &g_ammoPack, DEFAULT_AMMO_PACK_TOGGLE, \"g_ammoPack\" );",
		"config.ammoPackHackEnabled = G_ReadFactoryBoolCvar( &g_ammoPackHack, DEFAULT_AMMO_PACK_HACK, \"g_ammoPackHack\" );",
	):
		assert expected in config_c

	assert "G_UpdateAmmoPackConfig();" in g_main

	for expected in (
		'1008dbf4  char const (* data_1008dbf4)[0xb] = data_10087434 {"g_ammoPack"}',
		'1008dc0c  char const (* data_1008dc0c)[0xf] = data_10087424 {"g_ammoPackHack"}',
		'1008dc24  char const (* data_1008dc24)[0xe] = data_10087414 {"g_ammoRespawn"}',
	):
		assert expected in qagame_hlil
