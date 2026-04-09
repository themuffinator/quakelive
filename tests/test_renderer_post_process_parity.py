from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_renderer_post_process_pipeline_uses_retail_shader_family() -> None:
	tr_backend = _read("src/code/renderer/tr_backend.c")

	assert '"scripts/brightpass.fs"' in tr_backend
	assert '"scripts/downsample1.fs"' in tr_backend
	assert '"scripts/blurvertical.fs"' in tr_backend
	assert '"scripts/blurhoriz.fs"' in tr_backend
	assert '"scripts/combine.fs"' in tr_backend
	assert '"scripts/colorcorrect.fs"' in tr_backend
	assert '"scripts/posteffect.vs"' in tr_backend
	assert "GL_TEXTURE_RECTANGLE_ARB" in tr_backend
	assert "sampler2DRect" in tr_backend
	assert 'ri.Printf( PRINT_WARNING, "Post Process Failure - unable to create FBO : %d (%x)\\n", status, status );' in tr_backend
	assert 'ri.Printf( PRINT_WARNING, "GL_ARB_Multitexture is either not supported, or is disabled by r_ext_multiTexture. Post processing is disabled.\\n" );' in tr_backend


def test_color_correct_is_shader_backed_and_surfaces_retail_controls() -> None:
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_init = _read("src/code/renderer/tr_init.c")

	assert "qglGetTexImage(" not in tr_backend
	assert "qglCopyTexSubImage2D( GL_TEXTURE_RECTANGLE_ARB, 0, 0, 0, 0, 0, glConfig.vidWidth, glConfig.vidHeight );" in tr_backend
	assert '"p_gammaRecip"' in tr_backend
	assert '"p_overbright"' in tr_backend
	assert '"p_contrast"' in tr_backend
	assert 'r_contrast = ri.Cvar_Get( "r_contrast", "1", CVAR_ARCHIVE );' in tr_init
	assert "contrast = r_contrast ? r_contrast->value : 1.0f;" in tr_backend


def test_bloom_controls_and_active_mirrors_are_backend_validated() -> None:
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_init = _read("src/code/renderer/tr_init.c")

	assert "AssertCvarRange( r_enableBloom, 0, 1, qtrue );" in tr_init
	assert "blurFalloff = ( r_bloomBlurFalloff && r_bloomBlurFalloff->value > 0.0f ) ? r_bloomBlurFalloff->value : 0.75f;" in tr_backend
	assert "tr.postProcessActive = backEnd.postProcessActive;" in tr_backend
	assert "tr.bloomActive = backEnd.bloomActive;" in tr_backend
	assert "tr.colorCorrectActive = backEnd.colorCorrectActive;" in tr_backend
	assert 'ri.Cvar_Set( "r_postProcessActive", backEnd.postProcessActive ? "1" : "0" );' in tr_backend
	assert 'ri.Cvar_Set( "r_bloomActive", backEnd.bloomActive ? "1" : "0" );' in tr_backend
	assert 'ri.Cvar_Set( "r_colorCorrectActive", backEnd.colorCorrectActive ? "1" : "0" );' in tr_backend
	assert "approximate Quake Live" not in tr_backend
