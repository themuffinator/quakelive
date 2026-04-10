from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_tr_font_explicitly_separates_retail_and_compatibility_paths() -> None:
	tr_font = _read("src/code/renderer/tr_font.c")

	assert "#define R_FONT_ATLAS_SIZE 256" in tr_font
	assert "#define R_FONT_ATLAS_PIXEL_COUNT ( R_FONT_ATLAS_SIZE * R_FONT_ATLAS_SIZE )" in tr_font
	assert "#define R_COMPAT_FONT_CELL_SIZE 16" in tr_font
	assert "#define R_COMPAT_FONT_GRID_SIZE 16" in tr_font
	assert "#define R_COMPAT_FONT_TOP 12" in tr_font
	assert "#define R_COMPAT_FONT_BOTTOM -4" in tr_font

	assert "static void R_BuildFontCacheStem( const char *fontName, char *cacheStem, int cacheStemSize ) {" in tr_font
	assert "static void R_BuildLegacyFontCacheName( int pointSize, char *cacheName, int cacheNameSize ) {" in tr_font
	assert "static const char *R_FindCachedFontDataName( const char *cacheName, const char *legacyCacheName ) {" in tr_font
	assert "static void R_RegisterCachedFontShaders( fontInfo_t *font ) {" in tr_font
	assert "static void R_FlushFontAtlasPage( const char *fontName, int pointSize, int imageNumber, fontInfo_t *font, int firstGlyph, int lastGlyph, byte *out ) {" in tr_font

	assert 'Com_sprintf( cacheName, cacheNameSize, "fonts/fontImage_%s_%i.dat", cacheStem, pointSize );' in tr_font
	assert 'Com_sprintf( pageName, pageNameSize, "fonts/fontImage_%s_%i_%i.tga", cacheStem, imageNumber, pointSize );' in tr_font
	assert 'Com_sprintf( cacheName, cacheNameSize, "fonts/fontImage_%i.dat", pointSize );' in tr_font


def test_tr_font_pins_inclusive_cached_font_and_atlas_ranges() -> None:
	tr_font = _read("src/code/renderer/tr_font.c")

	assert "loadName = R_FindCachedFontDataName( cacheName, legacyCacheName );" in tr_font
	assert "R_RegisterCachedFontShaders( font );" in tr_font
	assert "for ( i = GLYPH_START; i <= GLYPH_END; i++ ) {" in tr_font
	assert "for ( j = firstGlyph; j <= lastGlyph; j++ ) {" in tr_font
	assert "R_FlushFontAtlasPage( fontName, pointSize, imageNumber++, font, lastStart, i - 1, out );" in tr_font
	assert "R_FlushFontAtlasPage( fontName, pointSize, imageNumber++, font, lastStart, i, out );" in tr_font
	assert "lastStart = i;" in tr_font


def test_tr_font_guards_classic_atlas_writes_before_copying_rows() -> None:
	tr_font = _read("src/code/renderer/tr_font.c")

	assert "*xOut + glyph.pitch > R_FONT_ATLAS_SIZE" in tr_font
	assert "*yOut + glyph.height > R_FONT_ATLAS_SIZE" in tr_font
	assert "dst = imageOut + (*yOut * R_FONT_ATLAS_SIZE) + *xOut;" in tr_font
	assert "dst += R_FONT_ATLAS_SIZE;" in tr_font


def test_tr_font_pins_representative_compatibility_glyph_metrics() -> None:
	tr_font = _read("src/code/renderer/tr_font.c")

	assert "cell = 1.0f / R_COMPAT_FONT_GRID_SIZE;" in tr_font
	assert "glyph->height = R_COMPAT_FONT_CELL_SIZE;" in tr_font
	assert "glyph->top = R_COMPAT_FONT_TOP;" in tr_font
	assert "glyph->bottom = R_COMPAT_FONT_BOTTOM;" in tr_font
	assert "glyph->pitch = R_COMPAT_FONT_CELL_SIZE;" in tr_font
	assert "glyph->xSkip = R_COMPAT_FONT_CELL_SIZE;" in tr_font
	assert "glyph->imageWidth = R_COMPAT_FONT_CELL_SIZE;" in tr_font
	assert "glyph->imageHeight = R_COMPAT_FONT_CELL_SIZE;" in tr_font


def test_rg_p7_ownership_note_and_renderer_audit_mark_rg_g05_closed() -> None:
	ownership_note = _read("docs/reverse-engineering/renderer-font-cache-and-atlas-ownership-2026-04-10.md")
	renderer_audit = _read("docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md")

	assert "## Retail-Backed Classic Font Behaviors" in ownership_note
	assert "## Compatibility-Only Scaffolding That Remains Intentional" in ownership_note
	assert "RG-G05 is now considered closed" in ownership_note
	assert "## RG-G05 - Classic renderer font/cache/atlas exactness remains partially source-biased" in renderer_audit
	assert "**Status:** Closed" in renderer_audit
	assert "Strict renderer estimate after `RG-P7` closure: **95%**" in renderer_audit
	assert "Strict renderer estimate after `RG-P8` closure: **97%**" in renderer_audit
	assert "Strict renderer estimate after `RG-P9` closure: **98%**" in renderer_audit
	assert "Strict renderer estimate after `RG-P10` closure: **99%**" in renderer_audit
	assert "Strict renderer estimate after `RG-P11` closure: **100%**" in renderer_audit
	assert "No confirmed renderer gaps remain after `RG-P11`." in renderer_audit
