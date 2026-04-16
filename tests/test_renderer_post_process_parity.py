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
	assert 'r_contrast = ri.Cvar_Get( "r_contrast", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert "contrast = r_contrast ? r_contrast->value : 1.0f;" in tr_backend


def test_bloom_controls_and_active_mirrors_are_backend_validated() -> None:
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_public = _read("src/code/renderer/tr_public.h")
	cl_main = _read("src/code/client/cl_main.c")

	assert 'cvar_t\t*(*Cvar_GetBounded)( const char *name, const char *value, const char *minValue, const char *maxValue, int flags );' in tr_public
	assert "ri.Cvar_GetBounded = Cvar_GetBounded;" in cl_main
	assert 'r_bloomPasses = ri.Cvar_GetBounded( "r_bloomPasses", "1", "1", "2", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_BOUNDED_DISCRETE | CVAR_CLOUD );' in tr_init
	assert "AssertCvarRange( r_enableBloom, 0, 2, qtrue );" in tr_init
	assert "static int RBPP_GetBloomMode( void ) {" in tr_backend
	assert "bloomMode = RBPP_GetBloomMode();" in tr_backend
	assert "if ( bloomMode == 2 ) {" in tr_backend
	assert '"p_blurStep"' not in tr_backend
	assert '"p_blurFalloff"' not in tr_backend
	assert "tr.postProcessActive = backEnd.postProcessActive;" in tr_backend
	assert "tr.bloomActive = backEnd.bloomActive;" in tr_backend
	assert "tr.colorCorrectActive = backEnd.colorCorrectActive;" in tr_backend
	assert 'ri.Cvar_Set( "r_postProcessActive", backEnd.postProcessActive ? "1" : "0" );' in tr_backend
	assert 'ri.Cvar_Set( "r_bloomActive", backEnd.bloomActive ? "1" : "0" );' in tr_backend
	assert 'ri.Cvar_Set( "r_colorCorrectActive", backEnd.colorCorrectActive ? "1" : "0" );' in tr_backend
	assert 'ri.Cvar_Set( "r_postProcessActive", tr.postProcessActive ? "1" : "0" );' not in tr_init
	assert 'ri.Cvar_Set( "r_bloomActive", tr.bloomActive ? "1" : "0" );' not in tr_init
	assert 'ri.Cvar_Set( "r_colorCorrectActive", tr.colorCorrectActive ? "1" : "0" );' not in tr_init
	assert 'passes = ( r_bloomPasses && r_bloomPasses->integer > 0 ) ? r_bloomPasses->integer : 1;' not in tr_backend
	assert "RBPP_BindRenderTarget( &s_postProcess.bloomDownsampleTarget );" in tr_backend
	assert "RBPP_BindRenderTarget( &s_postProcess.bloomQuarterDownsampleTarget );" in tr_backend
	assert "if ( backEnd.colorCorrectActive ) {" in tr_backend
	assert "\t\tRBPP_ApplyColorCorrectPass();" in tr_backend
	assert "approximate Quake Live" not in tr_backend


def test_live_post_process_tuning_cvars_consume_retail_modified_flags() -> None:
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_cmds = _read("src/code/renderer/tr_cmds.c")

	assert "static void R_ClearLivePostProcessModifiedFlags( void ) {" in tr_init
	assert "if ( r_contrast && r_contrast->modified ) {" in tr_init
	assert "\t\tr_contrast->modified = qfalse;" in tr_init
	assert "if ( r_bloomBrightThreshold && r_bloomBrightThreshold->modified ) {" in tr_init
	assert "\t\tr_bloomBrightThreshold->modified = qfalse;" in tr_init
	assert "if ( r_bloomSaturation && r_bloomSaturation->modified ) {" in tr_init
	assert "\t\tr_bloomSaturation->modified = qfalse;" in tr_init
	assert "if ( r_bloomSceneSaturation && r_bloomSceneSaturation->modified ) {" in tr_init
	assert "\t\tr_bloomSceneSaturation->modified = qfalse;" in tr_init
	assert "if ( r_bloomIntensity && r_bloomIntensity->modified ) {" in tr_init
	assert "\t\tr_bloomIntensity->modified = qfalse;" in tr_init
	assert "if ( r_bloomSceneIntensity && r_bloomSceneIntensity->modified ) {" in tr_init
	assert "\t\tr_bloomSceneIntensity->modified = qfalse;" in tr_init
	assert "R_ClearLivePostProcessModifiedFlags();" in tr_init
	assert "if ( r_gamma->modified ) {" in tr_cmds
