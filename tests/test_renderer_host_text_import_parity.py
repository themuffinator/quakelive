from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_renderer_host_text_imports_route_through_shared_renderer_core() -> None:
	tr_font = _read("src/code/renderer/tr_font.c")
	tr_local = _read("src/code/renderer/tr_local.h")
	client_h = _read("src/code/client/client.h")
	cl_ui = _read("src/code/client/cl_ui.c")
	cl_cgame = _read("src/code/client/cl_cgame.c")

	assert "qboolean R_GetFontStashDebugInfo( image_t **image, int *width, int *height ) {" in tr_font
	assert "qboolean RE_GetScaledFontMetrics( int fontHandle, float scale, float *outAscent, float *outDescent, float *outLineHeight ) {" in tr_font
	assert "void RE_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int limit, float *maxX, qboolean forceColor, const float *baseColor ) {" in tr_font
	assert "void RE_MeasureScaledText( const char *text, const char *end, int fontHandle, float scale, int limit, float *outWidth, float *outHeight, float *outLeft ) {" in tr_font
	assert "qboolean R_GetFontStashDebugInfo( image_t **image, int *width, int *height );" in tr_local
	assert "qboolean RE_GetScaledFontMetrics( int fontHandle, float scale, float *outAscent, float *outDescent, float *outLineHeight );" in tr_local
	assert "void RE_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int limit, float *maxX, qboolean forceColor, const float *baseColor );" in tr_local
	assert "void RE_MeasureScaledText( const char *text, const char *end, int fontHandle, float scale, int limit, float *outWidth, float *outHeight, float *outLeft );" in tr_local
	assert "qboolean RE_GetScaledFontMetrics( int fontHandle, float scale, float *outAscent, float *outDescent, float *outLineHeight );" in client_h
	assert "void RE_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int limit, float *maxX, qboolean forceColor, const float *baseColor );" in client_h
	assert "void RE_MeasureScaledText( const char *text, const char *end, int fontHandle, float scale, int limit, float *outWidth, float *outHeight, float *outLeft );" in client_h
	assert "RE_DrawScaledText( x, y, text, fontHandle, scale, limit, maxX," in cl_ui
	assert "RE_MeasureScaledText( text, end, fontHandle, scale, limit, &width, &height, &left );" in cl_ui
	assert "QL_UI_WriteMeasureTextBounds( outLeft, left, width, height );" in cl_ui
	assert "RE_DrawScaledText( x, y, text, fontHandle, scale, limit, maxX," in cl_cgame
	assert "RE_MeasureScaledText( text, end, fontHandle, scale, limit, &width, &height, &left );" in cl_cgame
	assert "QL_CG_WriteMeasureTextBounds( outLeft, left, width, height );" in cl_cgame
	assert "QL_UI_GetScaledFont" not in cl_ui
	assert "QL_CG_GetScaledFont" not in cl_cgame


def test_renderer_debug_font_atlas_path_is_implemented() -> None:
	tr_backend = _read("src/code/renderer/tr_backend.c")
	retail_font_stack = _read("docs/platform/retail-font-stack.md")

	assert "static void RB_ShowFontAtlas( void ) {" in tr_backend
	assert "R_GetFontStashDebugInfo( &image, &atlasWidth, &atlasHeight )" in tr_backend
	assert "if ( r_debugFontAtlas->integer ) {" in tr_backend
	assert "RB_ShowFontAtlas();" in tr_backend
	assert "DrawScaledText` / `MeasureText` now route through the shared" in retail_font_stack
	assert "`r_debugFontAtlas` now has an in-source draw path" in retail_font_stack
	assert "codepoints, caches retained glyphs by codepoint plus rounded size tenths" in retail_font_stack
	assert "probes the recovered retained fallback-face chain before dropping to the" in retail_font_stack


def test_renderer_host_text_virtual_point_baseline_matches_retail_wrapper_scale() -> None:
	ui_shared_h = _read("src/code/ui/ui_shared.h")
	cg_draw = _read("src/code/cgame/cg_draw.c")
	ui_main = _read("src/code/ui/ui_main.c")

	assert "#define QL_FONT_HOST_POINT_SIZE 60.0f" in ui_shared_h
	assert "#define QL_FONT_HOST_POINT_SIZE 48.0f" not in ui_shared_h
	assert "scale * QL_FONT_HOST_POINT_SIZE * yScale" in cg_draw
	assert "scale * QL_FONT_HOST_POINT_SIZE * uiInfo.uiDC.yscale" in ui_main
	assert "*outWidth = (int)( width / xScale );" in cg_draw
	assert "width / yScale" not in cg_draw
	assert "*outWidth = (int)( width / uiInfo.uiDC.xscale );" in ui_main
	assert "width / uiInfo.uiDC.yscale" not in ui_main


def test_renderer_measure_scaled_text_uses_retail_bounds_and_ascent() -> None:
	tr_font = _read("src/code/renderer/tr_font.c")
	measure_block = tr_font.split("void RE_MeasureScaledText", 1)[1].split("/*\n=================\nRE_RegisterFontFallback", 1)[0]

	assert "width = maxRight - minLeft;" in measure_block
	assert "RE_GetScaledFontMetrics( fontHandle, scale, &metricsAscent, NULL, NULL )" in measure_block
	assert "height = metricsAscent;" in measure_block
	assert "width = penX;" not in measure_block
	assert "height = maxBottom - minTop;" in measure_block
