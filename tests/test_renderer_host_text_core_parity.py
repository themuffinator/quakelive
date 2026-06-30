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


def _block_from_marker(source: str, marker: str) -> str:
	start = source.index(marker)
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
	assert "static int R_GetFontStashScaleTenths( float scale ) {" in tr_font
	assert "static FT_F26Dot6 R_GetFontStashPixelHeightCharSize( rFontStashFace_t *face, int scaleTenths ) {" in tr_font
	assert "static const char *R_DecodeFontStashCodepoint( const char *text, const char *end, unsigned int *outCodepoint ) {" in tr_font
	assert "static qboolean R_ParseHostTextColorEscape( const char *text, const char *end, int *outColorIndex, const char **outNext ) {" in tr_font
	assert "static int R_BuildFontStashFaceChain( rFontStashFace_t *face, rFontStashFace_t **faces, int maxFaces ) {" in tr_font
	assert "static void R_FlushFontStashRenderCommands( void ) {" in tr_font
	assert "r_fontStash.errorCallback = R_fonsErrorCallback;" in tr_font
	assert "void R_InitFontStash( void ) {" in tr_font
	assert "void R_DoneFontStash( void ) {" in tr_font
	assert "void R_InitFontStash( void );" in tr_local
	assert "void R_DoneFontStash( void );" in tr_local
	assert 'ri.Printf( PRINT_ALL, "R_Init: InitFontStash\\n" );' in tr_init
	assert "R_InitFontStash();" in tr_init
	assert "R_DoneFontStash();" in tr_init

	r_get_glyph_block = tr_font.split("static glyphInfo_t *R_GetFontStashGlyph", 1)[1]
	assert "if ( r_fontStash.shader ) {" in r_get_glyph_block
	assert "R_BuildFontStashFaceChain( face, faceChain, ARRAY_LEN( faceChain ) );" in r_get_glyph_block
	assert "codepoint <= GLYPH_END && R_EnsureFontStashCompatibilityFont( face )" in r_get_glyph_block
	assert r_get_glyph_block.index("if ( r_fontStash.shader ) {") < r_get_glyph_block.index(
		"codepoint <= GLYPH_END && R_EnsureFontStashCompatibilityFont( face )"
	)
	assert "R_FindFontStashGlyph( candidateFace, codepoint, scaleTenths );" in r_get_glyph_block
	assert "R_CacheFontStashGlyph( candidateFace, codepoint, scaleTenths, qtrue, &cachedGlyph )" in r_get_glyph_block
	assert "Retail host DrawScaledText/MeasureText resolve glyphs from the retained" in r_get_glyph_block
	assert "R_DecodeFontStashCodepoint( s, end, &codepoint )" in tr_font
	assert "R_ParseHostTextColorEscape( s, end, &colorIndex, &colorNext )" in tr_font
	assert "static void R_RescaleFontStashGlyphUVs( int oldWidth, int oldHeight, int newWidth, int newHeight ) {" in tr_font

	upload_block = tr_font.split("static void R_UploadFontStashAtlas", 1)[1].split("static qboolean R_EnsureFontStashImage", 1)[0]
	assert "r_fontStash.image->internalFormat = GL_ALPHA;" in upload_block
	assert "previousTMU = glState.currenttmu;" in upload_block
	assert "glState.currenttextures[glState.currenttmu] = 0;" in upload_block
	assert "GL_Bind( r_fontStash.image );" in upload_block
	assert "qglTexImage2D( GL_TEXTURE_2D, 0, GL_ALPHA, r_fontStash.width, r_fontStash.height, 0, GL_ALPHA, GL_UNSIGNED_BYTE, r_fontStash.buffer );" in upload_block
	assert "qglBindTexture( GL_TEXTURE_2D, 0 );" not in upload_block
	assert "R_BuildFontStashSeedImage" not in upload_block

	resize_block = tr_font.split("static qboolean R_ResizeFontStashAtlas", 1)[1].split("static void R_fonsErrorCallback", 1)[0]
	assert "oldBuffer = r_fontStash.buffer;" in resize_block
	assert "if ( oldBuffer ) {" in resize_block
	assert "if ( oldWidth > 0 && oldHeight > 0 ) {" in resize_block
	assert "Com_Memcpy( newBuffer + row * width, oldBuffer + row * oldWidth, copyWidth );" in resize_block
	assert "Z_Free( oldBuffer );" in resize_block
	assert "R_RescaleFontStashGlyphUVs( oldWidth, oldHeight, width, height );" in resize_block
	assert "R_ClearFontStashFaceGlyphState();" not in resize_block

	flush_block = _block_from_marker(tr_font, "static void R_FlushFontStashRenderCommands")
	assert "if ( !tr.registered || !backEndData[tr.smpFrame] ) {" in flush_block
	assert "if ( backEndData[tr.smpFrame]->commands.used <= 0 ) {" in flush_block
	assert "R_SyncRenderThread();" in flush_block

	error_block = _block_from_marker(tr_font, "static void R_fonsErrorCallback")
	assert error_block.index('ri.Printf( PRINT_ALL, "Expand font atlas to %dx%d\\n", width, height );') < error_block.index("R_FlushFontStashRenderCommands();")
	assert error_block.index("R_FlushFontStashRenderCommands();") < error_block.index("R_ResizeFontStashAtlas( width, height );")
	assert error_block.rindex("R_FlushFontStashRenderCommands();") < error_block.index("R_ClearFontStashAtlas();")

	r_init_block = tr_font.split("void R_InitFontStash( void ) {", 1)[1].split("void R_DoneFontStash( void ) {", 1)[0]
	assert "R_InitFontStashFaces();" in r_init_block
	assert "R_PrebuildFontStashAtlas" not in tr_font
	assert "R_FONTSTASH_PREBUILD_ATTEMPTS" not in tr_font
	assert 'R_InitFontStash: unable to prebuild retained' not in tr_font


def test_renderer_host_text_face_scale_color_and_clipping_contract() -> None:
	tr_font = _read_text(TR_FONT_PATH)
	scale_block = _block_from_marker(tr_font, "static int R_GetFontStashScaleTenths")
	pixel_height_block = _block_from_marker(tr_font, "static FT_F26Dot6 R_GetFontStashPixelHeightCharSize")
	set_size_block = _block_from_marker(tr_font, "static qboolean R_SetFontStashFaceSize")
	metrics_block = _block_from_marker(tr_font, "static qboolean R_GetFontStashFaceMetrics")
	color_block = _block_from_marker(tr_font, "static qboolean R_ParseHostTextColorEscape")
	face_block = _block_from_marker(tr_font, "static rFontStashFace_t *R_GetFontStashFaceForHandle")
	draw_block = _block_from_marker(tr_font, "void RE_DrawScaledText")
	measure_block = _block_from_marker(tr_font, "void RE_MeasureScaledText")

	for expected in (
		"if ( scale <= 0.0f ) {",
		"scale = R_FONTSTASH_POINT_SIZE;",
		"scaleTenths = (int)( scale * 10.0f + 0.5f );",
		"scaleTenths = 2;",
		"scaleTenths = 0x7fff;",
	):
		assert expected in scale_block

	for expected in (
		"pixelHeight = ( scaleTenths * 64 + 5 ) / 10;",
		"unitsPerEm = face->ftFace->units_per_EM;",
		"fontHeight = face->ftFace->ascender - face->ftFace->descender;",
		"adjustedCharSize = ( (long long)pixelHeight * unitsPerEm + fontHeight / 2 ) / fontHeight;",
	):
		assert expected in pixel_height_block
	assert "charSize = R_GetFontStashPixelHeightCharSize( face, scaleTenths );" in set_size_block
	assert "FT_Set_Char_Size( face->ftFace, 0, charSize, 72, 72 )" in set_size_block

	for expected in (
		"fontHeight = face->ftFace->ascender - face->ftFace->descender;",
		"lineHeight = face->ftFace->height;",
		"size = (float)scaleTenths / 10.0f;",
		"outMetrics->ascent = size * (float)face->ftFace->ascender / (float)fontHeight;",
		"outMetrics->descent = size * (float)face->ftFace->descender / (float)fontHeight;",
		"outMetrics->lineHeight = size * (float)lineHeight / (float)fontHeight;",
	):
		assert expected in metrics_block

	for expected in (
		"if ( !text || *text != Q_COLOR_ESCAPE ) {",
		"next = R_DecodeFontStashCodepoint( text + 1, end, &codepoint );",
		"if ( next <= text + 1 || codepoint < '0' || codepoint > '7' ) {",
		"*outColorIndex = (int)( codepoint - '0' );",
		"*outNext = next;",
	):
		assert expected in color_block
	assert "Q_IsColorString" not in color_block

	for expected in (
		"case R_FONTSTASH_FACE_SANS:",
		"face = r_fontStash.primarySansFace;",
		"case R_FONTSTASH_FACE_MONO:",
		"face = R_GetFontStashFace( R_FONTSTASH_FACE_MONO );",
		"case R_FONTSTASH_FACE_NORMAL:",
		"face = R_GetFontStashFace( R_FONTSTASH_FACE_NORMAL );",
		"if ( !face || !face->loaded ) {",
		"face = R_GetFontStashFace( R_FONTSTASH_FACE_NORMAL );",
		"if ( ( !face || !face->loaded ) && r_fontStash.primarySansFace && r_fontStash.primarySansFace->loaded ) {",
	):
		assert expected in face_block

	for expected in (
		"clipX = maxX ? *maxX : 0.0f;",
		"hasClipX = ( maxX && clipX > 0.0f );",
		"if ( maxX && !hasClipX ) {",
		"*maxX = (float)x;",
		"currentColor[0] = 1.0f;",
		"face = R_GetFontStashFaceForHandle( fontHandle );",
		"hasLimit = ( limit > 0 );",
		"if ( R_ParseHostTextColorEscape( s, end, &colorIndex, &colorNext ) ) {",
		"if ( !forceColor ) {",
		"newColor[3] = currentColor[3];",
		"RE_SetColor( newColor );",
		"s = colorNext;",
		"if ( hasLimit && remaining <= 0 ) {",
		"next = R_DecodeFontStashCodepoint( s, end, &codepoint );",
		"glyphMaxX = penX + advance;",
		"if ( penX + drawRight > glyphMaxX ) {",
		"if ( hasClipX && glyphMaxX > clipX ) {",
		"*maxX = penX;",
		"RE_StretchPic(",
		"penX + drawLeft,",
		"(float)y - drawTop,",
		"penX += advance;",
		"if ( maxX && !hasClipX ) {",
		"*maxX = glyphMaxX;",
		"remaining--;",
		"RE_SetColor( currentColor );",
	):
		assert expected in draw_block
	assert draw_block.index("if ( hasClipX && glyphMaxX > clipX ) {") < draw_block.index("RE_StretchPic(")

	for expected in (
		"*outWidth = 0.0f;",
		"*outHeight = 0.0f;",
		"*outLeft = 0.0f;",
		"face = R_GetFontStashFaceForHandle( fontHandle );",
		"hasLimit = ( limit > 0 );",
		"for ( s = text; *s && ( !end || s < end ); ) {",
		"if ( hasLimit && remaining <= 0 ) {",
		"if ( R_ParseHostTextColorEscape( s, end, &colorIndex, &colorNext ) ) {",
		"s = colorNext;",
		"next = R_DecodeFontStashCodepoint( s, end, &codepoint );",
		"glyphRight = penX + drawRight;",
		"glyphMaxX = penX + advance;",
		"if ( glyphRight > glyphMaxX ) {",
		"hasBounds = qtrue;",
		"remaining--;",
		"width = maxRight - minLeft;",
		"height = maxBottom - minTop;",
		"height = metricsAscent;",
		"*outLeft = hasBounds ? minLeft : 0.0f;",
	):
		assert expected in measure_block
	assert "hasMaxX" not in measure_block
	assert "maxXf" not in measure_block


def test_renderer_host_text_core_docs_track_rg_p8_completion() -> None:
	renderer_audit = _read_text(RENDERER_AUDIT_PATH)
	retail_font_stack = _read_text(RETAIL_FONT_STACK_PATH)
	rg_p8_note = _read_text(RG_P8_NOTE_PATH)

	assert "## Retail-Backed Host Text Core Behaviors" in rg_p8_note
	assert "## 2026-04-17 Audit Refresh" in rg_p8_note
	assert "## Downstream Closure" in rg_p8_note
	assert "RG-P8 is now considered complete." in rg_p8_note
	assert "## RG-P8 - Host text-engine core recovery [COMPLETED]" in renderer_audit
	assert "Strict renderer estimate after `RG-P8` closure: **97%**" in renderer_audit
	assert "The 2026-04-17 full font audit reopened one hidden renderer-host exactness tail" in renderer_audit
	assert "The 2026-05-20 wiring refresh removed the eager retained-atlas prebuild" in renderer_audit
	assert "*fontstash" in retail_font_stack
	assert "renderer-owned retained host text core" in retail_font_stack
	assert "consume UTF-8 text through the" in retail_font_stack
	assert "retained host lane instead of indexing raw bytes" in retail_font_stack
	assert "cached lazily as text is measured or drawn" in retail_font_stack
	assert "preserves the previous atlas pixels" in retail_font_stack
	assert "cached glyph coordinates when `R_fonsErrorCallback` expands" in retail_font_stack
	assert "texture as a `GL_ALPHA` atlas" in retail_font_stack
	assert "No confirmed renderer or client screen-overlay font-stack gap remains after" in retail_font_stack
