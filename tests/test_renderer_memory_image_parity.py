from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_renderer_exposes_retail_memory_image_helper_family() -> None:
	tr_local = _read("src/code/renderer/tr_local.h")
	tr_image = _read("src/code/renderer/tr_image.c")

	assert "image_t\t\t*R_CreateImageWithTarget" in tr_local
	assert "int\t\t\tR_DetectImageTypeFromMemory( const byte *buffer, int bufferLength );" in tr_local
	assert "image_t\t\t*R_LoadImageFromMemory( const char *name, const byte *buffer, int bufferLength, qboolean mipmap" in tr_local

	assert "image_t *R_CreateImageWithTarget( const char *name, const byte *pic, int width, int height," in tr_image
	assert "int R_DetectImageTypeFromMemory( const byte *buffer, int bufferLength ) {" in tr_image
	assert "image_t *R_LoadImageFromMemory( const char *name, const byte *buffer, int bufferLength, qboolean mipmap, qboolean allowPicmip, int glWrapClampMode ) {" in tr_image


def test_public_image_constructor_wraps_target_aware_helper() -> None:
	tr_image = _read("src/code/renderer/tr_image.c")

	assert "return R_CreateImageWithTarget( name, pic, width, height, mipmap, allowPicmip, glWrapClampMode, GL_TEXTURE_2D );" in tr_image
	assert "qglTexParameterf( glTarget, GL_TEXTURE_WRAP_S, glWrapClampMode );" in tr_image
	assert "qglTexParameterf( glTarget, GL_TEXTURE_WRAP_T, glWrapClampMode );" in tr_image


def test_implicit_nomip_shaders_use_retail_edge_clamp() -> None:
	tr_local = _read("src/code/renderer/tr_local.h")
	tr_image = _read("src/code/renderer/tr_image.c")
	tr_shader = _read("src/code/renderer/tr_shader.c")

	assert "#define GL_CLAMP_TO_EDGE 0x812F" in tr_local
	assert "int\t\t\twrapClampMode;\t\t// GL_CLAMP, GL_CLAMP_TO_EDGE, or GL_REPEAT" in tr_local
	assert 'case GL_CLAMP_TO_EDGE:\n\t\t\tri.Printf( PRINT_ALL, "edge " );' in tr_image
	assert "image = R_FindImageFile( fileName, mipRawImage, mipRawImage, mipRawImage ? GL_REPEAT : GL_CLAMP_TO_EDGE );" in tr_shader


def test_memory_loader_dispatches_buffer_decoders_and_warns_on_unknown_payloads() -> None:
	tr_image = _read("src/code/renderer/tr_image.c")

	assert "switch ( R_DetectImageTypeFromMemory( buffer, bufferLength ) ) {" in tr_image
	assert "LoadJPGFromBuffer( name, buffer, bufferLength, &pic, &width, &height );" in tr_image
	assert "LoadBMPFromBuffer( name, buffer, bufferLength, &pic, &width, &height );" in tr_image
	assert "LoadTGAFromBuffer( name, buffer, bufferLength, &pic, &width, &height );" in tr_image
	assert "LoadPNGFromBuffer( name, buffer, bufferLength, &pic, &width, &height );" in tr_image
	assert 'ri.Printf( PRINT_WARNING, "WARNING: R_LoadImageFromMemory() Unable to detect image type.\\n" );' in tr_image
	assert "image = R_CreateImageWithTarget( name, pic, width, height, mipmap, allowPicmip, glWrapClampMode, GL_TEXTURE_2D );" in tr_image


def test_live_client_resource_registration_uses_renderer_memory_lane() -> None:
	cl_main = _read("src/code/client/cl_main.c")
	steam_resources = _read("src/code/client/cl_steam_resources.c")

	assert "qhandle_t CL_RegisterShaderFromRGBA( const char *name, const byte *pic, int width, int height, qboolean mipRawImage ) {" in cl_main
	assert "qhandle_t CL_RegisterShaderFromMemory( const char *name, const byte *buffer, int bufferLength, qboolean mipRawImage ) {" in cl_main
	assert "image = R_CreateImage( name, pic, width, height, mipRawImage, mipRawImage, mipRawImage ? GL_REPEAT : GL_CLAMP );" in cl_main
	assert "image = R_LoadImageFromMemory( name, buffer, bufferLength, mipRawImage, mipRawImage, mipRawImage ? GL_REPEAT : GL_CLAMP );" in cl_main

	assert "CL_SteamResources_BuildRendererName( url, slot, rendererName, sizeof( rendererName ) );" in steam_resources
	assert "shader = CL_RegisterShaderFromRGBA( rendererName, rgbaPixels, width, height, qfalse );" in steam_resources
	assert "shader = CL_RegisterShaderFromMemory( rendererName, buffer, bufferLength, qfalse );" in steam_resources
	assert "CL_SteamResources_EncodeAvatarTGA" not in steam_resources
	assert "CL_SteamResources_WriteCacheFile" not in steam_resources
