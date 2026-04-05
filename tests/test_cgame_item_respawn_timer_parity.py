"""Guard the retail world-item respawn timer and queued marker seams against drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_DRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_ENTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_ents.c"
CG_BG_PLAN = REPO_ROOT / "docs" / "reverse-engineering" / "cgame-bg-parity-implementation-plan.md"


def _block_from_marker(source: str, marker: str) -> str:
	start = source.rindex(marker)
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


def test_item_respawn_timer_fallback_and_icon_boundaries_match_retail_family() -> None:
	source = CG_ENTS.read_text(encoding="utf-8")
	uses_block = _block_from_marker(source, "static qboolean CG_ItemUsesRespawnTimer")
	duration_block = _block_from_marker(source, "static int CG_ItemRespawnTimerDuration")
	icon_block = _block_from_marker(source, "static qhandle_t CG_ItemRespawnTimerIcon")

	for expected in (
		"if ( item->giType == IT_ARMOR ) {",
		"if ( item->giType == IT_HEALTH && item->quantity >= 100 ) {",
		"if ( item->giType == IT_POWERUP ) {",
		"if ( item->giType == IT_HOLDABLE && BG_HoldableForItemTag( item->giTag ) == HI_MEDKIT ) {",
	):
		assert expected in uses_block

	for expected in (
		"return 25 * 1000;",
		"return 35 * 1000;",
		"return 120 * 1000;",
		"return 60 * 1000;",
	):
		assert expected in duration_block

	for expected in (
		"return cgs.media.itemTimerArmorShader;",
		"return cgs.media.itemTimerHealthShader;",
		"return cgs.media.itemTimerQuadShader;",
		"return cgs.media.itemTimerBattleSuitShader;",
		"return cgs.media.itemTimerHasteShader;",
		"return cgs.media.itemTimerInvisShader;",
		"return cgs.media.itemTimerRegenShader;",
		"return cgs.media.itemTimerMedkitShader;",
		"return cgs.media.itemTimerUnknownShader;",
	):
		assert expected in icon_block


def test_item_respawn_timer_slice_selection_and_draw_math_match_retail_shape() -> None:
	source = CG_ENTS.read_text(encoding="utf-8")
	slices_block = _block_from_marker(source, "static void CG_ItemRespawnTimerSlices")
	sprite_block = _block_from_marker(source, "static void CG_DrawItemRespawnTimerSprite")
	draw_block = _block_from_marker(source, "static void CG_DrawItemRespawnTimer")

	for expected in (
		"durationBuckets = respawnDuration / 5000;",
		"if ( durationBuckets <= 5 ) {",
		"*sliceCount = 5;",
		"if ( durationBuckets <= 7 ) {",
		"*sliceCount = 7;",
		"if ( durationBuckets <= 12 ) {",
		"*sliceCount = 12;",
		"*sliceCount = 24;",
	):
		assert expected in slices_block

	for expected in (
		"ent.reType = RT_SPRITE;",
		"ent.radius = 16.0f;",
		"ent.rotation = rotation;",
		"ent.customShader = shader;",
		"ent.shaderRGBA[3] = alphaByte;",
	):
		assert expected in sprite_block

	for expected in (
		"if ( !item || !origin || !cg_itemTimers.integer ) {",
		"if ( respawnRemaining > respawnDuration ) {",
		"timerOrigin[2] += 8.0f;",
		"if ( distance <= 256.0f ) {",
		"} else if ( distance < 768.0f ) {",
		"alpha = ( 768.0f - distance ) * ( 1.0f / 512.0f );",
		"elapsedSlice = ( ( respawnDuration - respawnRemaining ) / 5000 ) + 1;",
		'CG_DrawItemRespawnTimerSprite( iconShader, timerOrigin, alpha, 180.0f );',
		"sliceStep = 360 / sliceCount;",
		"rotation = -( 180 / sliceCount );",
		"( sliceIndex == elapsedSlice ) ? currentSliceShader : sliceShader,",
	):
		assert expected in draw_block


def test_cg_item_calls_respawn_timer_before_skip_items_and_uses_time2_fallback() -> None:
	source = CG_ENTS.read_text(encoding="utf-8")
	item_block = _block_from_marker(source, "static void CG_Item")

	for expected in (
		"if ( CG_ItemUsesRespawnTimer( item ) && es->time > cg.time ) {",
		"respawnDuration = es->time2;",
		"if ( respawnDuration <= 0 ) {",
		"respawnDuration = CG_ItemRespawnTimerDuration( item );",
		"respawnRemaining = es->time - cg.time;",
		"CG_DrawItemRespawnTimer( item, respawnRemaining, respawnDuration,",
		"cent->lerpOrigin, 0,",
		"(qboolean)( ( es->eFlags & EF_NODRAW ) != 0 ) );",
		'trap_Cvar_VariableStringBuffer( "cg_skipItems", skipItems, sizeof( skipItems ) );',
	):
		assert expected in item_block

	assert item_block.index("CG_DrawItemRespawnTimer(") < item_block.index('trap_Cvar_VariableStringBuffer( "cg_skipItems"')


def test_cgame_draw_lane_keeps_world_marker_owners_and_closes_appendix_gap() -> None:
	draw_source = CG_DRAW.read_text(encoding="utf-8")
	plan = CG_BG_PLAN.read_text(encoding="utf-8")

	for marker in (
		"cgQueuedWorldMarker_t *CG_AllocQueuedWorldMarker",
		"void CG_UpdateQueuedWorldMarkers",
		"void CG_DrawQueuedWorldMarkers",
	):
		assert marker in draw_source

	assert "| `CG-D2` | Completed 2026-04-05 |" in plan

	cg_d_rows = [line for line in plan.splitlines() if line.startswith("| `CG-D` |")]
	assert cg_d_rows
	assert cg_d_rows[-1].endswith("| None |")
