import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BG_MISC = REPO_ROOT / "src" / "code" / "game" / "bg_misc.c"
BG_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "bg_public.h"
G_ITEMS = REPO_ROOT / "src" / "code" / "game" / "g_items.c"
CG_WEAPONS = REPO_ROOT / "src" / "code" / "cgame" / "cg_weapons.c"
CG_ENTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_ents.c"
CG_PREDICT = REPO_ROOT / "src" / "code" / "cgame" / "cg_predict.c"
CG_EVENT = REPO_ROOT / "src" / "code" / "cgame" / "cg_event.c"


ITEM_PATTERN = re.compile(
	r'\{\s*"(?P<name>[^"]+)"\s*,\s*(?:NULL|"[^"]*")\s*,\s*\{\s*'
	r'(?P<model0>0|NULL|"[^"]*")\s*,\s*'
	r'(?P<model1>0|NULL|"[^"]*")\s*,\s*'
	r'(?P<model2>0|NULL|"[^"]*")\s*,\s*'
	r'(?P<model3>0|NULL|"[^"]*")\s*\}\s*,\s*'
	r'/\* icon \*/\s*(?P<icon>NULL|"[^"]*")\s*,\s*'
	r'/\* pickup \*/\s*(?P<pickup>NULL|"[^"]*")\s*,\s*'
	r'(?P<quantity>-?\d+)\s*,(?:\s*//[^\n]*)?\s*'
	r'(?P<item_type>[A-Z_]+)\s*,\s*'
	r'(?P<tag>[A-Z0-9_]+)\s*,',
	re.DOTALL,
)


def _parse_token(token):
	token = token.strip()
	if token in {"0", "NULL"}:
		return None
	return token.strip('"')


def _item_metadata():
	items = {}
	for match in ITEM_PATTERN.finditer(BG_MISC.read_text()):
		items[match.group("name")] = {
			"models": [
				_parse_token(match.group("model0")),
				_parse_token(match.group("model1")),
				_parse_token(match.group("model2")),
				_parse_token(match.group("model3")),
			],
			"icon": _parse_token(match.group("icon")),
			"pickup": _parse_token(match.group("pickup")),
			"quantity": int(match.group("quantity")),
			"item_type": match.group("item_type"),
			"tag": match.group("tag"),
		}
	return items


def test_retail_pickup_names_match_item_table():
	items = _item_metadata()

	assert {name: items[name]["pickup"] for name in [
		"item_armor_combat",
		"item_armor_body",
		"weapon_machinegun",
		"ammo_bfg",
		"item_redcube",
		"item_bluecube",
	]} == {
		"item_armor_combat": "Yellow Armor",
		"item_armor_body": "Red Armor",
		"weapon_machinegun": "Machine Gun",
		"ammo_bfg": "BFG Ammo",
		"item_redcube": "Red Skull",
		"item_bluecube": "Blue Skull",
	}


def test_retail_weapon_and_ammo_quantities_match_item_table():
	items = _item_metadata()

	assert {name: items[name]["quantity"] for name in [
		"weapon_gauntlet",
		"weapon_shotgun",
		"weapon_machinegun",
		"weapon_grenadelauncher",
		"weapon_rocketlauncher",
		"weapon_lightning",
		"weapon_railgun",
		"weapon_plasmagun",
		"weapon_bfg",
		"weapon_grapplinghook",
		"weapon_nailgun",
		"weapon_prox_launcher",
		"weapon_chaingun",
		"weapon_hmg",
		"ammo_shells",
		"ammo_bullets",
		"ammo_grenades",
		"ammo_cells",
		"ammo_lightning",
		"ammo_rockets",
		"ammo_slugs",
		"ammo_bfg",
		"ammo_nails",
		"ammo_mines",
		"ammo_belt",
		"ammo_hmg",
		"ammo_pack",
	]} == {
		"weapon_gauntlet": 0,
		"weapon_shotgun": 10,
		"weapon_machinegun": 100,
		"weapon_grenadelauncher": 10,
		"weapon_rocketlauncher": 10,
		"weapon_lightning": 100,
		"weapon_railgun": 10,
		"weapon_plasmagun": 50,
		"weapon_bfg": 10,
		"weapon_grapplinghook": 0,
		"weapon_nailgun": 10,
		"weapon_prox_launcher": 5,
		"weapon_chaingun": 100,
		"weapon_hmg": 100,
		"ammo_shells": 5,
		"ammo_bullets": 50,
		"ammo_grenades": 5,
		"ammo_cells": 50,
		"ammo_lightning": 50,
		"ammo_rockets": 5,
		"ammo_slugs": 5,
		"ammo_bfg": 5,
		"ammo_nails": 5,
		"ammo_mines": 5,
		"ammo_belt": 100,
		"ammo_hmg": 50,
		"ammo_pack": 1,
	}


def test_retail_weapon_and_ammo_tags_match_item_table():
	items = _item_metadata()

	assert {name: items[name]["tag"] for name in [
		"weapon_gauntlet",
		"weapon_machinegun",
		"weapon_shotgun",
		"weapon_grenadelauncher",
		"weapon_rocketlauncher",
		"weapon_lightning",
		"weapon_railgun",
		"weapon_plasmagun",
		"weapon_bfg",
		"weapon_grapplinghook",
		"weapon_nailgun",
		"weapon_prox_launcher",
		"weapon_chaingun",
		"weapon_hmg",
		"ammo_shells",
		"ammo_bullets",
		"ammo_grenades",
		"ammo_cells",
		"ammo_lightning",
		"ammo_rockets",
		"ammo_slugs",
		"ammo_bfg",
		"ammo_nails",
		"ammo_mines",
		"ammo_belt",
		"ammo_hmg",
	]} == {
		"weapon_gauntlet": "ITEMTAG_WEAPON_GAUNTLET",
		"weapon_machinegun": "ITEMTAG_WEAPON_MACHINEGUN",
		"weapon_shotgun": "ITEMTAG_WEAPON_SHOTGUN",
		"weapon_grenadelauncher": "ITEMTAG_WEAPON_GRENADE_LAUNCHER",
		"weapon_rocketlauncher": "ITEMTAG_WEAPON_ROCKET_LAUNCHER",
		"weapon_lightning": "ITEMTAG_WEAPON_LIGHTNING",
		"weapon_railgun": "ITEMTAG_WEAPON_RAILGUN",
		"weapon_plasmagun": "ITEMTAG_WEAPON_PLASMAGUN",
		"weapon_bfg": "ITEMTAG_WEAPON_BFG",
		"weapon_grapplinghook": "ITEMTAG_WEAPON_GRAPPLING_HOOK",
		"weapon_nailgun": "ITEMTAG_WEAPON_NAILGUN",
		"weapon_prox_launcher": "ITEMTAG_WEAPON_PROX_LAUNCHER",
		"weapon_chaingun": "ITEMTAG_WEAPON_CHAINGUN",
		"weapon_hmg": "ITEMTAG_WEAPON_HEAVY_MACHINEGUN",
		"ammo_shells": "ITEMTAG_WEAPON_SHOTGUN",
		"ammo_bullets": "ITEMTAG_WEAPON_MACHINEGUN",
		"ammo_grenades": "ITEMTAG_WEAPON_GRENADE_LAUNCHER",
		"ammo_cells": "ITEMTAG_WEAPON_PLASMAGUN",
		"ammo_lightning": "ITEMTAG_WEAPON_LIGHTNING",
		"ammo_rockets": "ITEMTAG_WEAPON_ROCKET_LAUNCHER",
		"ammo_slugs": "ITEMTAG_WEAPON_RAILGUN",
		"ammo_bfg": "ITEMTAG_WEAPON_BFG",
		"ammo_nails": "ITEMTAG_WEAPON_NAILGUN",
		"ammo_mines": "ITEMTAG_WEAPON_PROX_LAUNCHER",
		"ammo_belt": "ITEMTAG_WEAPON_CHAINGUN",
		"ammo_hmg": "ITEMTAG_WEAPON_HEAVY_MACHINEGUN",
	}


def test_retail_armor_and_health_tags_match_item_table():
	items = _item_metadata()

	assert {name: items[name]["tag"] for name in [
		"item_armor_shard",
		"item_armor_combat",
		"item_armor_body",
		"item_armor_jacket",
		"item_health_small",
		"item_health",
		"item_health_large",
		"item_health_mega",
	]} == {
		"item_armor_shard": "4",
		"item_armor_combat": "2",
		"item_armor_body": "1",
		"item_armor_jacket": "3",
		"item_health_small": "4",
		"item_health": "3",
		"item_health_large": "2",
		"item_health_mega": "1",
	}


def test_retail_holdable_tags_match_item_table():
	items = _item_metadata()

	assert {name: items[name]["tag"] for name in [
		"holdable_teleporter",
		"holdable_medkit",
		"holdable_kamikaze",
		"holdable_portal",
		"holdable_invulnerability",
	]} == {
		"holdable_teleporter": "ITEMTAG_HOLDABLE_TELEPORTER",
		"holdable_medkit": "ITEMTAG_HOLDABLE_MEDKIT",
		"holdable_kamikaze": "ITEMTAG_HOLDABLE_KAMIKAZE",
		"holdable_portal": "ITEMTAG_HOLDABLE_PORTAL",
		"holdable_invulnerability": "ITEMTAG_HOLDABLE_INVULNERABILITY",
	}


def test_retail_weapon_item_tags_route_through_shared_mapping_helpers():
	bg_public = BG_PUBLIC.read_text()
	bg_misc = BG_MISC.read_text()
	g_items = G_ITEMS.read_text()
	cg_weapons = CG_WEAPONS.read_text()
	cg_ents = CG_ENTS.read_text()
	cg_predict = CG_PREDICT.read_text()
	cg_event = CG_EVENT.read_text()

	assert "int BG_ItemTagForWeapon( weapon_t weapon );" in bg_public
	assert "weapon_t BG_WeaponForItemTag( int itemTag );" in bg_public
	assert "weaponTag = BG_ItemTagForWeapon( weapon );" in bg_misc
	assert "weapon = BG_WeaponForItemTag( item->giTag );" in bg_misc
	assert "weapon = ent->item ? BG_WeaponForItemTag( ent->item->giTag ) : WP_NONE;" in g_items
	assert "Add_Ammo( other, BG_WeaponForItemTag( ent->item->giTag ), quantity );" in g_items
	assert "BG_WeaponForItemTag( item->giTag ) == weaponNum" in cg_weapons
	assert "CG_RegisterWeapon( BG_WeaponForItemTag( item->giTag ) );" in cg_weapons
	assert "wi = &cg_weapons[BG_WeaponForItemTag( item->giTag )];" in cg_ents
	assert "weapon = BG_WeaponForItemTag( item->giTag );" in cg_predict
	assert "weapon = BG_WeaponForItemTag( bg_itemlist[itemNum].giTag );" in cg_event


def test_retail_holdable_item_tags_route_through_shared_mapping_helpers():
	bg_public = BG_PUBLIC.read_text()
	bg_misc = BG_MISC.read_text()
	g_items = G_ITEMS.read_text()
	cg_ents = CG_ENTS.read_text()

	assert "int BG_ItemTagForHoldable( holdable_t holdable );" in bg_public
	assert "holdable_t BG_HoldableForItemTag( int itemTag );" in bg_public
	assert "static const int bg_holdableToItemTag[HI_NUM_HOLDABLE] = {" in bg_misc
	assert "static const holdable_t bg_itemTagToHoldable[ITEMTAG_HOLDABLE_INVULNERABILITY + 1] = {" in bg_misc
	assert "ITEMTAG_HOLDABLE_INVULNERABILITY" in bg_misc
	assert "BG_HoldableForItemTag( item->giTag ) == HI_MEDKIT" in g_items
	assert "BG_HoldableForItemTag( ent->item->giTag ) == HI_KAMIKAZE" in g_items
	assert "BG_HoldableForItemTag( item->giTag ) == HI_KAMIKAZE" in cg_ents


def test_retail_flag_visual_rows_match_item_table():
	items = _item_metadata()

	assert {name: (items[name]["models"], items[name]["icon"]) for name in [
		"team_CTF_redflag",
		"team_CTF_blueflag",
		"team_CTF_neutralflag",
	]} == {
		"team_CTF_redflag": (
			["models/flags/r_flag.md3", None, "models/flag3/r_flag3.md3", None],
			"gfx/2d/flag_status/red_flag_at_base",
		),
		"team_CTF_blueflag": (
			["models/flags/b_flag.md3", None, "models/flag3/b_flag3.md3", None],
			"gfx/2d/flag_status/blue_flag_at_base",
		),
		"team_CTF_neutralflag": (
			["models/flags/n_flag.md3", None, "models/flag3/n_flag3.md3", None],
			"gfx/2d/flag_status/flag_at_base",
		),
	}


def test_retail_persistant_powerup_and_key_quantities_match_item_table():
	items = _item_metadata()

	assert {name: items[name]["quantity"] for name in [
		"item_scout",
		"item_guard",
		"item_doubler",
		"item_armorregen",
		"item_key_silver",
		"item_key_gold",
		"item_key_master",
	]} == {
		"item_scout": 0,
		"item_guard": 0,
		"item_doubler": 0,
		"item_armorregen": 0,
		"item_key_silver": 1,
		"item_key_gold": 1,
		"item_key_master": 1,
	}
