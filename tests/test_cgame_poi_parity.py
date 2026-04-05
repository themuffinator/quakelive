"""Guard the retail POI width-clamp seam against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_DRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"


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
		'{ &cg_poiMinWidth, "cg_poiMinWidth", "16.0", CVAR_ARCHIVE },',
		'{ &cg_poiMaxWidth, "cg_poiMaxWidth", "32.0", CVAR_ARCHIVE },',
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
