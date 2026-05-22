import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BG_MISC = REPO_ROOT / "src" / "code" / "game" / "bg_misc.c"
BG_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "bg_public.h"
INV_HEADER = REPO_ROOT / "src" / "code" / "game" / "inv.h"
MSG_C = REPO_ROOT / "src" / "code" / "qcommon" / "msg.c"
Q_SHARED = REPO_ROOT / "src" / "code" / "game" / "q_shared.h"

EXPECTED_RETAIL_ITEM_ORDER = [
    "item_armor_shard",
    "item_armor_combat",
    "item_armor_body",
    "item_armor_jacket",
    "item_health_small",
    "item_health",
    "item_health_large",
    "item_health_mega",
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
    "ammo_shells",
    "ammo_bullets",
    "ammo_grenades",
    "ammo_cells",
    "ammo_lightning",
    "ammo_rockets",
    "ammo_slugs",
    "ammo_bfg",
    "holdable_teleporter",
    "holdable_medkit",
    "item_quad",
    "item_enviro",
    "item_haste",
    "item_invis",
    "item_regen",
    "item_flight",
    "team_CTF_redflag",
    "team_CTF_blueflag",
    "holdable_kamikaze",
    "holdable_portal",
    "holdable_invulnerability",
    "ammo_nails",
    "ammo_mines",
    "ammo_belt",
    "item_scout",
    "item_guard",
    "item_doubler",
    "item_armorregen",
    "team_CTF_neutralflag",
    "item_redcube",
    "item_bluecube",
    "weapon_nailgun",
    "weapon_prox_launcher",
    "weapon_chaingun",
    "item_spawnarmor",
    "weapon_hmg",
    "ammo_hmg",
    "ammo_pack",
    "item_key_silver",
    "item_key_gold",
    "item_key_master",
]


def _bg_item_names():
    prefixes = ("\"item_", "\"weapon_", "\"ammo_", "\"holdable_", "\"team_")
    names = []
    for line in BG_MISC.read_text().splitlines():
        stripped = line.strip()
        if any(stripped.startswith(prefix) for prefix in prefixes):
            names.append(stripped.split('"')[1])
    return names


def _modelindex_values():
	pattern = re.compile(r"^#define\s+MODELINDEX_[A-Z0-9_]+\s+(\d+)$", re.MULTILINE)
	return [int(match.group(1)) for match in pattern.finditer(INV_HEADER.read_text())]


def _armor_gitags():
	pattern = re.compile(
		r'"(?P<name>item_armor_(?:combat|body|jacket))".*?IT_ARMOR,\s*(?P<tag>\d+),',
		re.DOTALL,
	)
	return {match.group("name"): int(match.group("tag")) for match in pattern.finditer(BG_MISC.read_text())}


def _item_type_enum_entries():
	match = re.search(
		r"typedef enum \{\s*(?P<body>.*?)\}\s*itemType_t;",
		BG_PUBLIC.read_text(),
		re.DOTALL,
	)
	assert match, "itemType_t definition missing from bg_public.h"
	return re.findall(r"\bIT_[A-Z_]+\b", match.group("body"))


def _player_touches_item_body():
	match = re.search(
		r"qboolean\s+BG_PlayerTouchesItem\s*\(.*?\)\s*\{(?P<body>.*?)\n\}",
		BG_MISC.read_text(),
		re.DOTALL,
	)
	assert match, "BG_PlayerTouchesItem definition missing from bg_misc.c"
	return match.group("body")


def test_modelindex_definitions_match_bg_itemlist():
    item_names = _bg_item_names()
    assert item_names == EXPECTED_RETAIL_ITEM_ORDER, (
        "bg_itemlist order must stay aligned with the retail Quake Live item table"
    )
    model_indexes = _modelindex_values()
    assert len(model_indexes) == len(item_names), (
        "MODELINDEX_* definitions must cover every bg_itemlist entry"
    )
    assert model_indexes == list(range(1, len(item_names) + 1)), (
        "MODELINDEX_* values must stay sequential to match bg_itemlist order"
    )


def test_tiered_armor_metadata_matches_retail():
	assert _armor_gitags() == {
		"item_armor_combat": 2,
		"item_armor_body": 1,
		"item_armor_jacket": 3,
	}
	assert "int\t\t\tarmorTier;" in Q_SHARED.read_text()
	assert "{ PSF(armorTier), 2 }" not in MSG_C.read_text()
	assert "CG_GetArmorTierColor( cg.snap->ps.stats[STAT_ARMOR], color );" in (
		REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
	).read_text()


def test_item_type_order_matches_retail_dispatch():
	assert _item_type_enum_entries() == [
		"IT_BAD",
		"IT_WEAPON",
		"IT_AMMO",
		"IT_ARMOR",
		"IT_HEALTH",
		"IT_POWERUP",
		"IT_HOLDABLE",
		"IT_PERSISTANT_POWERUP",
		"IT_TEAM",
		"IT_KEY",
	]


def test_player_touch_bounds_match_retail_flag_behavior():
	body = _player_touches_item_body()

	assert "maxZDelta = 29.0f;" in body
	assert "maxZDelta = 64.0f;" in body
	assert "BG_IsTeamFlagItem( itemDef )" in body
	assert "ps->origin[0] - origin[0] > 36" in body
	assert "ps->origin[0] - origin[0] < -36" in body
	assert "ps->origin[2] - origin[2] > maxZDelta" in body
	assert "ps->origin[2] - origin[2] < -50" in body
