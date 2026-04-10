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
	assert "void RE_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor, const float *baseColor ) {" in tr_font
	assert "void RE_MeasureScaledText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outWidth, float *outHeight, float *outLeft ) {" in tr_font
	assert "qboolean R_GetFontStashDebugInfo( image_t **image, int *width, int *height );" in tr_local
	assert "void RE_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor, const float *baseColor );" in tr_local
	assert "void RE_MeasureScaledText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outWidth, float *outHeight, float *outLeft );" in tr_local
	assert "void RE_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor, const float *baseColor );" in client_h
	assert "void RE_MeasureScaledText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outWidth, float *outHeight, float *outLeft );" in client_h
	assert "RE_DrawScaledText( x, y, text, fontHandle, scale, maxX, outMaxX," in cl_ui
	assert "RE_MeasureScaledText( text, end, fontHandle, scale, maxX, &width, &height, outLeft );" in cl_ui
	assert "RE_DrawScaledText( x, y, text, fontHandle, scale, maxX, outMaxX," in cl_cgame
	assert "RE_MeasureScaledText( text, end, fontHandle, scale, maxX, &width, &height, outLeft );" in cl_cgame
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
