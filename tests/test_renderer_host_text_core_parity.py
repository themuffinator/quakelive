from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
TR_FONT_PATH = REPO_ROOT / "src" / "code" / "renderer" / "tr_font.c"
TR_INIT_PATH = REPO_ROOT / "src" / "code" / "renderer" / "tr_init.c"
TR_LOCAL_PATH = REPO_ROOT / "src" / "code" / "renderer" / "tr_local.h"
RENDERER_AUDIT_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "renderer-full-parity-audit-and-implementation-plan-2026-04-09.md"
)
RETAIL_FONT_STACK_PATH = REPO_ROOT / "docs" / "platform" / "retail-font-stack.md"
RG_P8_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "renderer-host-text-core-ownership-2026-04-10.md"
)


def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def test_renderer_host_text_core_matches_retail_surface() -> None:
	tr_font = _read_text(TR_FONT_PATH)
	tr_init = _read_text(TR_INIT_PATH)
	tr_local = _read_text(TR_LOCAL_PATH)

	assert '#define R_FONTSTASH_TEXTURE_NAME "*fontstash"' in tr_font
	assert "#define R_FONTSTASH_INITIAL_WIDTH 512" in tr_font
	assert "#define R_FONTSTASH_INITIAL_HEIGHT 512" in tr_font
	assert "#define R_FONTSTASH_MAX_WIDTH 2048" in tr_font
	assert "#define R_FONTSTASH_MAX_HEIGHT 1024" in tr_font
	assert "static void R_fonsErrorCallback( rFontStashState_t *fontStash, int error, int val ) {" in tr_font
	assert 'ri.Printf( PRINT_ALL, "R_fonsErrorCallback: error %d val %d\\n", error, val );' in tr_font
	assert 'ri.Printf( PRINT_ALL, "Expand font atlas to %dx%d\\n", width, height );' in tr_font
	assert 'ri.Printf( PRINT_ALL, "Max font atlas size, flushing\\n" );' in tr_font
	assert 'R_LoadFontStashFace( R_FONTSTASH_FACE_NORMAL, "normal", "fonts/handelgothic.ttf" );' in tr_font
	assert 'R_LoadFontStashFace( R_FONTSTASH_FACE_SANS, "sans", "fonts/notosans-regular.ttf" );' in tr_font
	assert 'R_LoadFontStashFace( R_FONTSTASH_FACE_MONO, "mono", "fonts/droidsansmono.ttf" );' in tr_font
	assert 'R_LoadFontStashFace( R_FONTSTASH_FACE_SANS_FALLBACK, "sans-fallback", "fonts/droidsansfallbackfull.ttf" );' in tr_font
	assert 'R_LoadFontStashFace( R_FONTSTASH_FACE_SANS_WINDOWS_FALLBACK, "sans-windows-fallback",' in tr_font
	assert 'ri.Printf( PRINT_ALL, "Using font fallback from the Windows host: arialuni.ttf\\n" );' in tr_font
	assert 'ri.Printf( PRINT_ALL, "Using font fallback from the Windows host: segoeui.ttf\\n" );' in tr_font
	assert 'ri.Printf( PRINT_ALL, "Using font fallback from the Windows host: l_10646.ttf\\n" );' in tr_font
	assert "r_fontStash.primarySansFace = R_GetFontStashFace( R_FONTSTASH_FACE_SANS );" in tr_font
	assert "r_fontStash.fallbackSansFace = R_GetFontStashFace( R_FONTSTASH_FACE_SANS_FALLBACK );" in tr_font
	assert "r_fontStash.windowsFallbackFace = R_GetFontStashFace( R_FONTSTASH_FACE_SANS_WINDOWS_FALLBACK );" in tr_font
	assert "static qboolean R_EnsureFontStashCompatibilityFont( rFontStashFace_t *face ) {" in tr_font
	assert "r_fontStash.errorCallback = R_fonsErrorCallback;" in tr_font
	assert "void R_InitFontStash( void ) {" in tr_font
	assert "void R_DoneFontStash( void ) {" in tr_font
	assert "void R_InitFontStash( void );" in tr_local
	assert "void R_DoneFontStash( void );" in tr_local
	assert 'ri.Printf( PRINT_ALL, "R_Init: InitFontStash\\n" );' in tr_init
	assert "R_InitFontStash();" in tr_init
	assert "R_DoneFontStash();" in tr_init

	r_get_glyph_block = tr_font.split("static glyphInfo_t *R_GetFontStashGlyph", 1)[1]
	assert "if ( face->ftFace && r_fontStash.shader ) {" in r_get_glyph_block
	assert "if ( R_EnsureFontStashCompatibilityFont( face ) ) {" in r_get_glyph_block
	assert r_get_glyph_block.index("if ( face->ftFace && r_fontStash.shader ) {") < r_get_glyph_block.index(
		"if ( R_EnsureFontStashCompatibilityFont( face ) ) {"
	)
	assert "Retail host DrawScaledText/MeasureText resolve glyphs from the retained" in r_get_glyph_block


def test_renderer_host_text_core_docs_track_rg_p8_completion() -> None:
	renderer_audit = _read_text(RENDERER_AUDIT_PATH)
	retail_font_stack = _read_text(RETAIL_FONT_STACK_PATH)
	rg_p8_note = _read_text(RG_P8_NOTE_PATH)

	assert "## Retail-Backed Host Text Core Behaviors" in rg_p8_note
	assert "## Downstream Closure" in rg_p8_note
	assert "RG-P8 is now considered complete." in rg_p8_note
	assert "## RG-P8 - Host text-engine core recovery [COMPLETED]" in renderer_audit
	assert "Strict renderer estimate after `RG-P8` closure: **97%**" in renderer_audit
	assert "*fontstash" in retail_font_stack
	assert "renderer-owned retained host text core" in retail_font_stack
