"""Guard the retail POI width-clamp seam against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_DRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_ENTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_ents.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CGAME_HLIL = REPO_ROOT / "references" / "hlil" / "quakelive" / "cgamex86.dll" / "cgamex86.dll_hlil.txt"


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


def test_poi_marker_width_clamp_matches_retail_hidden_cvar_defaults() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	draw_source = CG_DRAW.read_text(encoding="utf-8")
	poi_block = _block_from_marker(draw_source, "float CG_POIMarkerSizeForOrigin")

	for expected in (
		'{ &cg_poiMinWidth, "cg_poiMinWidth", "16.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "2.0", "16.0" },',
		'{ &cg_poiMaxWidth, "cg_poiMaxWidth", "32.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "16.0", "32.0" },',
	):
		assert expected in main_source

	assert "Applies the retail POI width clamp from the hidden cg_poi* cvars." in draw_source
	assert "Approximates the retail POI width clamp" not in draw_source

	for expected in (
		"maxWidth = ( cg_poiMaxWidth.value > 0.0f ) ? cg_poiMaxWidth.value : 32.0f;",
		"minWidth = ( cg_poiMinWidth.value > 0.0f ) ? cg_poiMinWidth.value : 16.0f;",
		"if ( minWidth > maxWidth ) {",
		"distance = Distance( cg.refdef.vieworg, origin );",
		"if ( distance <= 256.0f ) {",
		"if ( distance >= 768.0f ) {",
		"frac = ( distance - 256.0f ) / ( 768.0f - 256.0f );",
		"return maxWidth + ( minWidth - maxWidth ) * frac;",
	):
		assert expected in poi_block


def test_world_marker_projection_uses_left_axis_sign_and_active_widescreen_inverse() -> None:
	draw_source = CG_DRAW.read_text(encoding="utf-8")
	projection_block = _block_from_marker(draw_source, "static qboolean CG_WorldCoordToScreenCoord")

	for expected in (
		"left = DotProduct( transformed, cg.refdef.viewaxis[1] );",
		"ndcX = -left / ( forward * tanHalfFovX );",
		"pixelX = cg.refdef.x + ( 1.0f + ndcX ) * cg.refdef.width * 0.5f;",
		"pixelY = cg.refdef.y + ( 1.0f - ndcY ) * cg.refdef.height * 0.5f;",
		"CG_AdjustFrom640( &xBias, NULL, &xScale, &yScale );",
		"*x = ( pixelX - xBias ) / xScale;",
		"*y = pixelY / yScale;",
	):
		assert expected in projection_block

	for unexpected in (
		"right = DotProduct( transformed, cg.refdef.viewaxis[1] );",
		"ndcX = right / ( forward * tanHalfFovX );",
		"widthScale = (float)SCREEN_WIDTH / (float)cgs.glconfig.vidWidth;",
		"heightScale = (float)SCREEN_HEIGHT / (float)cgs.glconfig.vidHeight;",
	):
		assert unexpected not in projection_block


def test_incoming_powerup_poi_bank_matches_retail_per_powerup_handles() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	ents_source = CG_ENTS.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	register_block = _block_from_marker(main_source, "static void CG_RegisterGraphics( void )")
	incoming_block = _block_from_marker(ents_source, "static qhandle_t CG_ItemPOIPowerupIncomingShader")
	marker_block = _block_from_marker(ents_source, "static qboolean CG_ItemPOIPowerupMarker")

	for address in (
		"data_10a5fbbc",
		"data_10a5fbc0",
		"data_10a5fbc8",
		"data_10a5fbc4",
		"data_10a5fbcc",
	):
		assert f'{address} = ' in hlil_source

	assert hlil_source.count('"gfx/2d/powerup/incoming"') >= 5

	for field in (
		"qhandle_t\tpoiPowerupQuadIncomingShader;",
		"qhandle_t\tpoiPowerupBattleSuitIncomingShader;",
		"qhandle_t\tpoiPowerupHasteIncomingShader;",
		"qhandle_t\tpoiPowerupInvisIncomingShader;",
		"qhandle_t\tpoiPowerupRegenIncomingShader;",
	):
		assert field in local_source

	for assignment in (
		'cgs.media.poiPowerupQuadIncomingShader = trap_R_RegisterShader( "gfx/2d/powerup/incoming" );',
		'cgs.media.poiPowerupBattleSuitIncomingShader = trap_R_RegisterShader( "gfx/2d/powerup/incoming" );',
		'cgs.media.poiPowerupInvisIncomingShader = trap_R_RegisterShader( "gfx/2d/powerup/incoming" );',
		'cgs.media.poiPowerupHasteIncomingShader = trap_R_RegisterShader( "gfx/2d/powerup/incoming" );',
		'cgs.media.poiPowerupRegenIncomingShader = trap_R_RegisterShader( "gfx/2d/powerup/incoming" );',
	):
		assert assignment in register_block

	assert register_block.index('cgs.media.poiPowerupRegenShader = trap_R_RegisterShader( "gfx/2d/powerup/regen" );') < register_block.index(
		'cgs.media.poiPowerupQuadIncomingShader = trap_R_RegisterShader( "gfx/2d/powerup/incoming" );'
	)

	for expected in (
		"return cgs.media.poiPowerupQuadIncomingShader;",
		"return cgs.media.poiPowerupBattleSuitIncomingShader;",
		"return cgs.media.poiPowerupHasteIncomingShader;",
		"return cgs.media.poiPowerupInvisIncomingShader;",
		"return cgs.media.poiPowerupRegenIncomingShader;",
	):
		assert expected in incoming_block

	assert "incomingShader = CG_ItemPOIPowerupIncomingShader( item );" in marker_block
	assert "*shader = incomingShader;" in marker_block
	assert "poiPowerupIncomingShader" not in local_source
	assert "poiPowerupIncomingShader" not in register_block
	assert "poiPowerupIncomingShader" not in marker_block


def test_teamplay_flag_poi_bank_matches_retail_status_handles_and_item_markers() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	ents_source = CG_ENTS.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	register_block = _block_from_marker(main_source, "static void CG_RegisterGraphics( void )")
	team_shader_block = _block_from_marker(ents_source, "static qhandle_t CG_ItemPOITeamShader")
	queue_block = _block_from_marker(ents_source, "static void CG_QueueItemPOIMarker")

	for address in (
		"data_10a5fc2c",
		"data_10a5fc30",
		"data_10a5fc34",
		"data_10a5fc38",
		"data_10a5fc3c",
		"data_10a5fc40",
		"data_10a5fc44",
		"data_10a5fc48",
		"data_10a5fc4c",
		"data_10a5fc50",
		"data_10a5fc54",
		"data_10a5fc58",
		"data_10a5fc78",
	):
		assert f"{address} =" in hlil_source

	for path in (
		"gfx/2d/flag_status/flag_at_base.tga",
		"gfx/2d/flag_status/flag_taken.tga",
		"gfx/2d/flag_status/flag_dropped.tga",
		"gfx/2d/flag_status/flag_stolen.tga",
		"gfx/2d/flag_status/red_flag_at_base.tga",
		"gfx/2d/flag_status/red_flag_taken.tga",
		"gfx/2d/flag_status/red_flag_dropped.tga",
		"gfx/2d/flag_status/red_flag_stolen.tga",
		"gfx/2d/flag_status/blue_flag_at_base.tga",
		"gfx/2d/flag_status/blue_flag_taken.tga",
		"gfx/2d/flag_status/blue_flag_dropped.tga",
		"gfx/2d/flag_status/blue_flag_stolen.tga",
		"gfx/2d/flag_status/track_pointer.tga",
	):
		assert f'"{path}"' in hlil_source
		assert f'trap_R_RegisterShader( "{path}" )' in register_block

	for field in (
		"qhandle_t\tpoiFlagAtBaseNeutralShader;",
		"qhandle_t\tpoiFlagTakenNeutralShader;",
		"qhandle_t\tpoiFlagDroppedNeutralShader;",
		"qhandle_t\tpoiFlagStolenNeutralShader;",
		"qhandle_t\tpoiFlagAtBaseRedShader;",
		"qhandle_t\tpoiFlagTakenRedShader;",
		"qhandle_t\tpoiFlagDroppedRedShader;",
		"qhandle_t\tpoiFlagStolenRedShader;",
		"qhandle_t\tpoiFlagAtBaseBlueShader;",
		"qhandle_t\tpoiFlagTakenBlueShader;",
		"qhandle_t\tpoiFlagDroppedBlueShader;",
		"qhandle_t\tpoiFlagStolenBlueShader;",
		"qhandle_t\tpoiFlagTrackPointerShader;",
	):
		assert field in local_source

	for expected in (
		"static qhandle_t CG_ItemPOITeamShader( const gitem_t *item, vec4_t color )",
		"color[0] = 1.0f;",
		"color[1] = 0.2f;",
		"color[2] = 0.2f;",
		"color[0] = 0.2f;",
		"color[1] = 0.6f;",
		"color[2] = 1.0f;",
		"return cgs.media.poiDefendShader;",
		"return cgs.media.poiAttackShader;",
		"return cgs.media.poiCaptureShader;",
		"return cgs.media.poiFlagDroppedRedShader;",
		"return cgs.media.poiFlagDroppedBlueShader;",
		"return cgs.media.poiFlagDroppedNeutralShader;",
	):
		assert expected in team_shader_block

	for unexpected in (
		"cgs.redflag == FLAG_DROPPED",
		"cgs.blueflag == FLAG_DROPPED",
		"cgs.flagStatus == FLAG_DROPPED",
	):
		assert unexpected not in team_shader_block

	assert "shader = CG_ItemPOITeamShader( item, color );" in queue_block
	assert "Vector4Copy( color, marker->color );" in queue_block
	assert "marker->color[3] *= alpha;" in queue_block


def test_domination_point_poi_uses_retail_queued_world_marker_slab() -> None:
	ents_source = CG_ENTS.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	symbol_source = (REPO_ROOT / "references" / "symbol-maps" / "cgame.json").read_text(encoding="utf-8")
	add_block = _block_from_marker(ents_source, "static void CG_DominationAddBillboard")
	queue_block = _block_from_marker(ents_source, "static void CG_QueueDominationPointBillboard")

	assert "#define CG_QUEUED_MARKER_KIND_DOMINATION_POINT\t4" in local_source
	assert "allocating a queued world marker through `CG_AllocQueuedWorldMarker`" in symbol_source
	assert "marker = CG_AllocQueuedWorldMarkerForKey( CG_QUEUED_MARKER_KIND_DOMINATION_POINT, cent->currentState.number );" in add_block
	assert "VectorCopy( cent->lerpOrigin, marker->origin );" in add_block
	assert "marker->origin[2] += height;" in add_block
	assert "marker->duration = 200;" in add_block
	assert "marker->fadeDelay = 200;" in add_block
	assert "marker->size = radius;" in add_block
	assert "marker->shader = shader;" in add_block
	assert "RT_SPRITE" not in add_block
	assert "trap_R_AddRefEntityToScene" not in add_block

	for expected in (
		"shader = CG_DominationSelectShader( captureIcon, distress, progressIndex );",
		"radius = ( distance < 512.0f ) ? DOM_POINT_NEAR_RADIUS : DOM_POINT_FAR_RADIUS;",
		"CG_DominationAddBillboard( cent, shader, DOM_POINT_ICON_HEIGHT, radius );",
	):
		assert expected in queue_block
