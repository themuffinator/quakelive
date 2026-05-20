import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BG_MISC = REPO_ROOT / "src" / "code" / "game" / "bg_misc.c"
BG_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "bg_public.h"
Q_SHARED = REPO_ROOT / "src" / "code" / "game" / "q_shared.h"
G_COMBAT = REPO_ROOT / "src" / "code" / "game" / "g_combat.c"
QAGAME_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "qagame.json"
CGAME_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "cgame.json"


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


def test_weapon_and_holdable_tag_bridges_preserve_retail_item_numbering() -> None:
	source = BG_MISC.read_text(encoding="utf-8")
	public = BG_PUBLIC.read_text(encoding="utf-8")

	assert re.search(r"WP_HEAVY_MACHINEGUN,\s*WP_SHOTGUN,", public)
	assert re.search(r"ITEMTAG_WEAPON_CHAINGUN\s+13\s*#define ITEMTAG_WEAPON_HEAVY_MACHINEGUN\s+14", public)
	assert re.search(r"ITEMTAG_HOLDABLE_PORTAL\s+4\s*#define ITEMTAG_HOLDABLE_INVULNERABILITY\s+6", public)
	assert "ITEMTAG_WEAPON_HEAVY_MACHINEGUN," in source
	assert re.search(r"WP_CHAINGUN,\s*WP_HEAVY_MACHINEGUN", source)
	assert re.search(r"HI_PORTAL,\s*HI_NONE,\s*HI_INVULNERABILITY", source)


def test_cgame_symbol_map_uses_public_type_and_tag_lookup_name() -> None:
	symbols = json.loads(CGAME_SYMBOL_MAP.read_text(encoding="utf-8"))
	entry = next(symbol for symbol in symbols["functions"] if symbol["address"] == "0x10001170")

	assert entry["normalized_name"] == "BG_FindItemByTypeAndTag"
	assert "BG_FindItemByTypeAndTag" in entry["signature"]
	assert "BG_FindItemByTypeTag" not in entry["comment"]


def test_eventnames_table_stays_aligned_with_retail_entity_event_enum() -> None:
	public = BG_PUBLIC.read_text(encoding="utf-8")
	source = BG_MISC.read_text(encoding="utf-8")
	enum_body = re.search(r"typedef enum \{\s*EV_NONE = 0,(?P<body>.*?)\} entity_event_t;", public, re.DOTALL)
	names_body = re.search(r"char \*eventnames\[\] = \{(?P<body>.*?)\};", source, re.DOTALL)
	current_value = 0
	enum_events: list[tuple[int, str]] = [(0, "EV_NONE")]

	assert enum_body is not None
	assert names_body is not None

	for match in re.finditer(r"\b(EV_[A-Z0-9_]+)\s*(?:=\s*(\d+))?\s*,?", enum_body.group("body")):
		if match.group(2):
			current_value = int(match.group(2))
		else:
			current_value += 1
		enum_events.append((current_value, match.group(1)))

	event_names = re.findall(r'"(EV_[A-Z0-9_]+)"', names_body.group("body"))

	assert enum_events[-1] == (99, "EV_NEW_HIGH_SCORE")
	assert len(event_names) == 100
	assert event_names == [name for _, name in enum_events]


def test_symbol_maps_record_pickup_gate_as_direct_item_type_switch() -> None:
	for symbol_map, address in (
		(QAGAME_SYMBOL_MAP, "0x1002CED0"),
		(CGAME_SYMBOL_MAP, "0x10001560"),
	):
		symbols = json.loads(symbol_map.read_text(encoding="utf-8"))
		entry = next(symbol for symbol in symbols["functions"] if symbol["address"] == address)

		assert entry["normalized_name"] == "BG_CanItemBeGrabbed"
		assert "item-type switch" in entry["comment"]
		assert "bg_itemGrabHandlers" not in entry["comment"]


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
	assert "if ( !BG_IsArmorTieredModeEnabled() ) {" in body
	assert "return ( ps->stats[STAT_ARMOR] < BG_GetArmorUpperBound( ps ) ) ? qtrue : qfalse;" in body
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


def test_armor_pickup_helper_matches_retail_tiered_leaf_boundary() -> None:
	body = _function_body(
		r"static qboolean BG_CanGrabArmorItem\( int gametype, int currentTime, const entityState_t \*ent, const playerState_t \*ps, const gitem_t \*item, qboolean dropped \)\s*\{(?P<body>.*?)^\}",
	)

	assert "BG_IsArmorTieredModeEnabled()" not in body
	assert "BG_PlayerHasPersistantPowerup( ps, PW_SCOUT )" not in body
	assert "if ( item->quantity == 100 ) {" in body
	assert "return ( armor < 200 ) ? qtrue : qfalse;" in body
	assert "if ( item->quantity == 50 ) {" in body
	assert "if ( ps->armorTier <= 1 ) {" in body
	assert "return ( armor < 150 ) ? qtrue : qfalse;" in body
	assert "return ( armor <= 132 ) ? qtrue : qfalse;" in body
	assert "if ( item->quantity == 25 ) {" in body
	assert "return ( armor < 100 ) ? qtrue : qfalse;" in body
	assert "return ( armor <= 75 ) ? qtrue : qfalse;" in body
	assert "return ( armor <= 66 ) ? qtrue : qfalse;" in body


def test_health_pickup_helper_restores_retail_leaf_boundary() -> None:
	body = _function_body(
		r"static qboolean BG_CanGrabHealthItem\( int gametype, int currentTime, const entityState_t \*ent, const playerState_t \*ps, const gitem_t \*item, qboolean dropped \)\s*\{(?P<body>.*?)^\}",
	)

	assert "upperBound = BG_GetHealthUpperBound( ps, item->quantity );" in body
	assert "if ( upperBound <= 0 ) {" in body
	assert "return ( ps->stats[STAT_HEALTH] < upperBound ) ? qtrue : qfalse;" in body


def test_weapon_pickup_helper_restores_the_retail_world_weapon_regrab_gate() -> None:
	body = _function_body(
		r"static qboolean BG_CanGrabWeaponItem\( int gametype, int currentTime, const entityState_t \*ent, const playerState_t \*ps, const gitem_t \*item, qboolean dropped \)\s*\{(?P<body>.*?)^\}",
	)

	assert "if ( ps->pm_flags & PMF_IRONSIGHTS ) {" in body
	assert "if ( dropped ) {" in body
	assert "weapon = BG_WeaponForItemTag( item->giTag );" in body
	assert "if ( !( ps->stats[STAT_WEAPONS] & ( 1 << weapon ) ) ) {" in body
	assert "(void)gametype;" in body
	assert "(void)currentTime;" in body
	assert "(void)ent;" in body
	assert "return ( ps->ammo[weapon] <= 0 ) ? qtrue : qfalse;" in body


def test_trajectory_evaluators_keep_the_retail_type_six_acceleration_path() -> None:
	q_shared_source = Q_SHARED.read_text(encoding="utf-8")
	source = BG_MISC.read_text(encoding="utf-8")
	position_body = _function_body(
		r"void BG_EvaluateTrajectory\( const trajectory_t \*tr, int atTime, vec3_t result \)\s*\{(?P<body>.*?)^\}",
	)
	delta_body = _function_body(
		r"void BG_EvaluateTrajectoryDelta\( const trajectory_t \*tr, int atTime, vec3_t result \)\s*\{(?P<body>.*?)^\}",
	)

	assert "TR_QL_ACCEL" in q_shared_source
	assert "float\t\ttrAcceleration" not in q_shared_source
	assert "static float BG_TrajectoryAcceleration( const trajectory_t *tr )" in source
	assert "( (const byte *)tr + sizeof( *tr ) )" in source
	assert "case TR_QL_ACCEL:" in position_body
	assert "0.5 * BG_TrajectoryAcceleration( tr ) * deltaTime * deltaTime" in position_body
	assert "case TR_QL_ACCEL:" in delta_body
	assert "result[2] -= BG_TrajectoryAcceleration( tr ) * deltaTime;" in delta_body


def test_symbol_maps_record_the_type_six_trajectory_extension() -> None:
	for symbol_map in (QAGAME_SYMBOL_MAP, CGAME_SYMBOL_MAP):
		symbols = json.loads(symbol_map.read_text(encoding="utf-8"))
		trajectory = next(
			symbol
			for symbol in symbols["functions"]
			if symbol["normalized_name"] == "BG_EvaluateTrajectory"
		)
		delta = next(
			symbol
			for symbol in symbols["functions"]
			if symbol["normalized_name"] == "BG_EvaluateTrajectoryDelta"
		)

		assert "TR_QL_ACCEL" in trajectory["comment"]
		assert "extra acceleration scalar" in trajectory["comment"]
		assert "TR_QL_ACCEL" in delta["comment"]
		assert "extra acceleration scalar" in delta["comment"]


def test_qagame_symbol_map_records_retail_touch_bounds() -> None:
	symbols = json.loads(QAGAME_SYMBOL_MAP.read_text(encoding="utf-8"))
	entry = next(symbol for symbol in symbols["functions"] if symbol["address"] == "0x1002CD30")

	assert entry["normalized_name"] == "BG_PlayerTouchesItem"
	assert "+/-36" in entry["comment"]
	assert "-50" in entry["comment"]
	assert "29-unit" in entry["comment"]
	assert "64 units" in entry["comment"]
	assert "red, blue, and neutral" in entry["comment"]
	assert "44x44" not in entry["comment"]
	assert "35-unit" not in entry["comment"]


def test_qagame_symbol_map_labels_the_tiered_armor_pickup_leaf() -> None:
	symbols = json.loads(QAGAME_SYMBOL_MAP.read_text(encoding="utf-8"))
	entry = next(symbol for symbol in symbols["functions"] if symbol["address"] == "0x1002CE00")

	assert entry["normalized_name"] == "BG_CanGrabArmorItem"
	assert "BG_CanGrabArmorItem" in entry["signature"]
	assert "armor * 0.75 <= 99.0" in entry["comment"]
	assert "BG_CanGrabHealthItem" not in entry["comment"]
