from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _function_body(source: str, signature: str) -> str:
	definition = f"{signature} {{"
	start = source.index(definition)
	brace = start + len(definition) - 1
	depth = 1
	index = brace + 1

	while depth > 0:
		if source[index] == "{":
			depth += 1
		elif source[index] == "}":
			depth -= 1
		index += 1

	return source[brace + 1 : index - 1]


def test_key_item_definitions_match_retail_bits_and_assets() -> None:
	bg_public = _read("src/code/game/bg_public.h")
	bg_misc = _read("src/code/game/bg_misc.c")

	for expected in (
		"#define KEY_FLAG_SILVER         0x01",
		"#define KEY_FLAG_GOLD           0x02",
		"#define KEY_FLAG_MASTER         0x04",
		"STAT_KEY_MASK",
	):
		assert expected in bg_public

	for expected in (
		'"item_key_silver"',
		'"sound/items/key_silver.wav"',
		'"models/powerups/keys/key_silver.md3"',
		'"icons/key_silver"',
		'"Silver Key"',
		"KEY_FLAG_SILVER",
		'"item_key_gold"',
		'"sound/items/key_gold.wav"',
		'"models/powerups/keys/key_gold.md3"',
		'"icons/key_gold"',
		'"Gold Key"',
		"KEY_FLAG_GOLD",
		'"item_key_master"',
		'"models/powerups/keys/key_master.md3"',
		'"icons/key_master"',
		'"Master Key"',
		"KEY_FLAG_MASTER",
	):
		assert expected in bg_misc

	assert bg_misc.count("IT_KEY,") == 3
	assert bg_misc.count('"sound/items/key_gold.wav"') == 2


def test_key_pickup_reset_and_remove_paths_use_retail_key_mask() -> None:
	g_items = _read("src/code/game/g_items.c")
	g_target = _read("src/code/game/g_target.c")
	g_combat = _read("src/code/game/g_combat.c")

	reset_body = _function_body(g_items, "static gentity_t *G_ResetKeyItem( int bit )")
	pickup_body = _function_body(g_items, "static int Pickup_Key( gentity_t *ent, gentity_t *other )")
	drop_body = _function_body(g_items, "void G_DropClientKeys( gentity_t *ent )")
	remove_body = _function_body(g_target, "static void Use_Target_RemoveKeys( gentity_t *ent, gentity_t *other, gentity_t *activator )")

	assert '{ KEY_FLAG_SILVER, "item_key_silver" }' in g_items
	assert '{ KEY_FLAG_GOLD, "item_key_gold" }' in g_items
	assert '{ KEY_FLAG_MASTER, "item_key_master" }' in g_items
	assert "if ( ent->flags & FL_DROPPED_ITEM )" in reset_body
	assert "G_FreeEntity( ent );" in reset_body
	assert "RespawnItem( ent );" in reset_body
	assert "other->keyMask |= keyBit;" in pickup_body
	assert "other->client->ps.stats[STAT_KEY_MASK] = other->keyMask;" in pickup_body
	assert "return -1;" in pickup_body
	assert "G_ResetKeyItem( def->bit );" in drop_body
	assert "ent->keyMask = 0;" in drop_body
	assert "ent->client->ps.stats[STAT_KEY_MASK] = 0;" in drop_body
	assert "G_DropClientKeys( activator );" in remove_body
	assert "G_DropClientKeys( self );" in g_combat


def test_keyed_doors_and_buttons_accept_matching_key_or_master_bits() -> None:
	g_mover = _read("src/code/game/g_mover.c")

	door_body = _function_body(g_mover, "static void Touch_DoorTriggerKeyed( gentity_t *ent, gentity_t *other, trace_t *trace )")
	button_body = _function_body(g_mover, "static void Touch_ButtonKeyed( gentity_t *ent, gentity_t *other, trace_t *trace )")
	spawn_body = _function_body(g_mover, "void SP_func_button( gentity_t *ent )")

	assert "if ( !other->client )" in door_body
	assert "if ( other->client->ps.pm_type == PM_SPECTATOR )" in door_body
	assert "Touch_DoorTriggerSpectator( ent, other, trace );" in door_body
	assert "if ( door->moverState == MOVER_1TO2 )" in door_body
	assert "requiredKeys |= KEY_FLAG_SILVER | KEY_FLAG_MASTER;" in door_body
	assert "requiredKeys |= KEY_FLAG_GOLD | KEY_FLAG_MASTER;" in door_body
	assert "Use_BinaryMover( door, ent, other );" in door_body

	assert "if ( !other->client )" in button_body
	assert "if ( ent->moverState != MOVER_POS1 )" in button_body
	assert "ent->spawnflags & 16" in button_body
	assert "other->keyMask & ( KEY_FLAG_SILVER | KEY_FLAG_MASTER )" in button_body
	assert "ent->spawnflags & 32" in button_body
	assert "other->keyMask & ( KEY_FLAG_GOLD | KEY_FLAG_MASTER )" in button_body
	assert button_body.count("Use_BinaryMover( ent, other, other );") == 2

	assert spawn_body.index("if ( ent->spawnflags & ( 16 | 32 ) )") < spawn_body.index("} else if (ent->health) {")
	assert "ent->touch = Touch_ButtonKeyed;" in spawn_body
	assert "ent->touch = Touch_Button;" in spawn_body


def test_key_hud_ownerdraw_uses_replicated_local_stat_mask() -> None:
	cg_newdraw = _read("src/code/cgame/cg_newdraw.c")
	key_body = _function_body(cg_newdraw, "static void CG_DrawPlayerHasKey( rectDef_t *rect )")

	assert '{ KEY_FLAG_SILVER, "item_key_silver" }' in cg_newdraw
	assert '{ KEY_FLAG_GOLD, "item_key_gold" }' in cg_newdraw
	assert '{ KEY_FLAG_MASTER, "item_key_master" }' in cg_newdraw
	assert "mask = cg.snap->ps.stats[STAT_KEY_MASK];" in key_body
	assert "BG_FindItemByClassname( def->classname );" in key_body
	assert "CG_RegisterItemVisuals( itemNum );" in key_body
	assert "CG_DrawPic( x, rect->y, rect->w, rect->h, icon );" in key_body
	assert "x += rect->w * 0.5f;" in key_body
