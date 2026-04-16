import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BG_MISC = REPO_ROOT / "src" / "code" / "game" / "bg_misc.c"
BG_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "bg_public.h"
G_COMBAT = REPO_ROOT / "src" / "code" / "game" / "g_combat.c"


def _function_body(signature_pattern: str) -> str:
	source = BG_MISC.read_text(encoding="utf-8")
	match = re.search(
		signature_pattern,
		source,
		re.MULTILINE | re.DOTALL,
	)
	assert match is not None, "Function definition missing from bg_misc.c"
	return match.group("body")


def _g_combat_function_body(signature_pattern: str) -> str:
	source = G_COMBAT.read_text(encoding="utf-8")
	match = re.search(
		signature_pattern,
		source,
		re.MULTILINE | re.DOTALL,
	)
	assert match is not None, "Function definition missing from g_combat.c"
	return match.group("body")


def test_bg_misc_public_helper_surface_matches_retail() -> None:
	source = BG_PUBLIC.read_text(encoding="utf-8")

	assert "gitem_t\t*BG_FindItemByTypeAndTag( itemType_t type, int tag );" in source
	assert "qboolean\tBG_PlayerCarryingFlag( const playerState_t *ps );" in source
	assert "const char *BG_WeaponName( weapon_t weapon );" in source
	assert "int BG_ItemTagForHoldable( holdable_t holdable );" in source
	assert "holdable_t BG_HoldableForItemTag( int itemTag );" in source


def test_team_flag_predicate_matches_retail_helper_shape() -> None:
	body = _function_body(
		r"static qboolean BG_IsTeamFlagItem\( const gitem_t \*item \)\s*\{(?P<body>.*?)^\}",
	)

	assert "if ( !item ) {" in body
	assert "if ( item->giType != IT_TEAM ) {" in body
	assert "item->giTag == PW_REDFLAG" in body
	assert "item->giTag == PW_BLUEFLAG" in body
	assert "item->giTag == PW_NEUTRALFLAG" in body


def test_type_and_tag_lookup_helper_matches_retail_error_surface() -> None:
	body = _function_body(
		r"gitem_t\s*\*BG_FindItemByTypeAndTag\( itemType_t type, int tag \)\s*\{(?P<body>.*?)^\}",
	)

	assert "for ( it = bg_itemlist + 1 ; it->classname ; it++ ) {" in body
	assert "it->giType == type && it->giTag == tag" in body
	assert 'Com_Error( ERR_DROP, "Couldn\'t find item for type %i tag %i", type, tag );' in body


def test_weapon_and_holdable_wrappers_route_through_generic_item_lookup() -> None:
	weapon_body = _function_body(
		r"gitem_t\s*\*BG_FindItemForWeapon\( weapon_t weapon \)\s*\{(?P<body>.*?)^\}",
	)
	holdable_body = _function_body(
		r"gitem_t\s*\*BG_FindItemForHoldable\( holdable_t pw \)\s*\{(?P<body>.*?)^\}",
	)

	assert "weaponTag = BG_ItemTagForWeapon( weapon );" in weapon_body
	assert "return BG_FindItemByTypeAndTag( IT_WEAPON, weaponTag );" in weapon_body
	assert "holdableTag = BG_ItemTagForHoldable( pw );" in holdable_body
	assert "return BG_FindItemByTypeAndTag( IT_HOLDABLE, holdableTag );" in holdable_body


def test_weapon_name_helper_uses_retail_name_table_with_item_tag_mapping() -> None:
	source = BG_MISC.read_text(encoding="utf-8")
	body = _function_body(
		r"const char \*BG_WeaponName\( weapon_t weapon \)\s*\{(?P<body>.*?)^\}",
	)

	assert 'static const char *const bg_retailWeaponNames[WP_NUM_WEAPONS] = {' in source
	for expected in (
		'"None"',
		'"Machine Gun"',
		'"Plasma Gun"',
		'"Prox Launcher"',
		'"Heavy Machinegun"',
	):
		assert expected in source

	assert "weaponTag = BG_ItemTagForWeapon( weapon );" in body
	assert "return bg_retailWeaponNames[WP_NONE];" in body
	assert "return bg_retailWeaponNames[weaponTag];" in body


def test_flag_carrier_predicate_matches_retail_helper_shape() -> None:
	body = _function_body(
		r"qboolean BG_PlayerCarryingFlag\( const playerState_t \*ps \)\s*\{(?P<body>.*?)^\}",
	)

	assert "ps->powerups[PW_REDFLAG]" in body
	assert "ps->powerups[PW_BLUEFLAG]" in body
	assert "ps->powerups[PW_NEUTRALFLAG]" in body
	assert body.count("return qtrue;") == 3
	assert "return qfalse;" in body


def test_flag_carrier_predicate_is_reused_by_qagame_capture_path() -> None:
	body = _g_combat_function_body(
		r"void CheckAlmostCapture\( gentity_t \*self, gentity_t \*attacker \) \s*\{(?P<body>.*?)^\}",
	)

	assert "if ( BG_PlayerCarryingFlag( &self->client->ps ) ) {" in body
	assert "self->client->ps.powerups[PW_REDFLAG]" not in body
	assert "self->client->ps.powerups[PW_BLUEFLAG]" not in body
	assert "self->client->ps.powerups[PW_NEUTRALFLAG]" not in body


def test_can_item_be_grabbed_matches_retail_switch_surface() -> None:
	source = BG_MISC.read_text(encoding="utf-8")
	body = _function_body(
		r"qboolean BG_CanItemBeGrabbed\( int gametype, int currentTime, const entityState_t \*ent, const playerState_t \*ps \)\s*\{(?P<body>.*?)^\}",
	)

	assert "switch ( item->giType ) {" in body
	assert "case IT_WEAPON:" in body
	assert "return BG_CanGrabWeaponItem( gametype, currentTime, ent, ps, item, dropped );" in body
	assert "case IT_AMMO:" in body
	assert "if ( gametype == GT_DOMINATION ) {" in body
	assert "item->giTag == WP_NUM_WEAPONS" in body
	assert "weapon = BG_WeaponForItemTag( item->giTag );" in body
	assert "case IT_ARMOR:" in body
	assert "return BG_CanGrabArmorItem( gametype, currentTime, ent, ps, item, dropped );" in body
	assert "case IT_HEALTH:" in body
	assert "return BG_CanGrabHealthItem( gametype, currentTime, ent, ps, item, dropped );" in body
	assert "case IT_PERSISTANT_POWERUP:" in body
	assert "( ent->generic1 & 2 )" in body
	assert "( ent->generic1 & 4 )" in body
	assert "case IT_TEAM:" in body
	assert "carryingAnyFlag = BG_PlayerCarryingFlag( ps );" in body
	assert "case GT_CTF:" in body
	assert "case GT_1FCTF:" in body
	assert "case GT_HARVESTER:" in body
	assert "case GT_ATTACK_DEFEND:" in body
	assert "case IT_KEY:" in body

	assert "bg_itemGrabHandlers" not in source
	assert "static qboolean BG_CanGrabAmmoItem" not in source
	assert "static qboolean BG_CanGrabHealthItem" in source
	assert "static qboolean BG_CanGrabPersistantPowerupItem" not in source
	assert "static qboolean BG_CanGrabHoldableItem" not in source
	assert "static qboolean BG_CanGrabKeyItem" not in source
	assert "static qboolean BG_CanGrabTeamItem" not in source


def test_health_pickup_helper_restores_retail_leaf_boundary() -> None:
	body = _function_body(
		r"static qboolean BG_CanGrabHealthItem\( int gametype, int currentTime, const entityState_t \*ent, const playerState_t \*ps, const gitem_t \*item, qboolean dropped \)\s*\{(?P<body>.*?)^\}",
	)

	assert "upperBound = BG_GetHealthUpperBound( ps, item->quantity );" in body
	assert "if ( upperBound <= 0 ) {" in body
	assert "return ( ps->stats[STAT_HEALTH] < upperBound ) ? qtrue : qfalse;" in body


def test_weapon_pickup_helper_keeps_world_weapon_regrabs_open_outside_ironsights() -> None:
	body = _function_body(
		r"static qboolean BG_CanGrabWeaponItem\( int gametype, int currentTime, const entityState_t \*ent, const playerState_t \*ps, const gitem_t \*item, qboolean dropped \)\s*\{(?P<body>.*?)^\}",
	)

	assert "if ( ps->pm_flags & PMF_IRONSIGHTS ) {" in body
	assert "if ( dropped ) {" in body
	assert "(void)gametype;" in body
	assert "(void)currentTime;" in body
	assert "(void)ent;" in body
	assert "return qtrue;" in body
