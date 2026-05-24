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


def test_runtime_probes_keep_multitexture_enabled_for_post_process() -> None:
	client_probe = _read("tools/client/run_client_runtime_probe.ps1")
	qcommon_probe = _read("tools/qcommon/run_qcommon_runtime_probe.ps1")

	assert "'+set', 'r_ext_multitexture', '1'" in client_probe
	assert "'+set', 'r_ext_multitexture', '1'" in qcommon_probe
	assert "'+set', 'r_ext_multitexture', '0'" not in client_probe
	assert "'+set', 'r_ext_multitexture', '0'" not in qcommon_probe


def test_color_correct_is_shader_backed_and_surfaces_retail_controls() -> None:
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_init = _read("src/code/renderer/tr_init.c")

	assert "qglGetTexImage(" not in tr_backend
	assert "qglCopyTexSubImage2D( GL_TEXTURE_RECTANGLE_ARB, 0, 0, 0, 0, 0, glConfig.vidWidth, glConfig.vidHeight );" in tr_backend
	assert '"p_gammaRecip"' in tr_backend
	assert '"p_overbright"' in tr_backend
	assert '"p_contrast"' in tr_backend
	assert 'r_contrast = ri.Cvar_Get( "r_contrast", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'web_browserActive = ri.Cvar_Get( "web_browserActive", "0", CVAR_ROM );' in tr_init
	assert "if ( ( !web_browserActive || !web_browserActive->integer ) && r_gamma && r_gamma->value > 0.0f ) {" in tr_backend
	assert "if ( ( !web_browserActive || !web_browserActive->integer ) && r_contrast ) {" in tr_backend
	assert "\t\tcontrast = r_contrast->value;" in tr_backend
	assert "overbright = 2.0f * r_overBrightBits->integer;" in tr_backend
	assert "color *= p_overbright;" in tr_backend


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
	assert "qglOrtho( 0, width, height, 0, 0, 1 );" in tr_backend
	assert "RB_SetGL2D();" not in _extract_function_block(tr_backend, "static void RBPP_Set2DState( int width, int height ) {")
	assert "if ( backEnd.colorCorrectActive ) {" in tr_backend
	assert "\t\tRBPP_ApplyColorCorrectPass();" in tr_backend
	assert "approximate Quake Live" not in tr_backend


def test_hardware_gamma_color_mapping_matches_retail_color_correct_owner() -> None:
	tr_image = _read("src/code/renderer/tr_image.c")
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_init = _read("src/code/renderer/tr_init.c")

	color_mapping_block = _extract_function_block(tr_image, "void R_SetColorMappings( void ) {")
	color_correct_block = _extract_function_block(tr_backend, "static void RBPP_ApplyColorCorrectPass( void ) {")
	restart_block = _extract_function_block(tr_init, "static void R_PostProcessRestart( void ) {")

	assert "if ( !tr.colorCorrectActive && !glConfig.deviceSupportsGamma ) {" in color_mapping_block
	assert "if ( !tr.colorCorrectActive && glConfig.deviceSupportsGamma )" in color_mapping_block
	assert "GLimp_SetGamma( s_gammatable, s_gammatable, s_gammatable );" in color_mapping_block
	assert "if ( ( !web_browserActive || !web_browserActive->integer ) && r_gamma && r_gamma->value > 0.0f ) {" in color_correct_block
	assert "if ( ( !web_browserActive || !web_browserActive->integer ) && r_contrast ) {" in color_correct_block
	assert "R_SyncRenderThread();" in restart_block
	assert "RB_ShutdownRenderTargets();" in restart_block
	assert "RB_InitRenderTargets();" in restart_block
	assert "R_SetColorMappings();" in restart_block


def test_win32_hardware_gamma_ramp_matches_retail_contract() -> None:
	win_gamma = _read("src/code/win32/win_gamma.c")
	win_glimp = _read("src/code/win32/win_glimp.c")

	check_block = _extract_function_block(win_gamma, "void WG_CheckHardwareGamma( void )\n{")
	set_block = _extract_function_block(win_gamma, "void GLimp_SetGamma( unsigned char red[256], unsigned char green[256], unsigned char blue[256] ) {")
	restore_block = _extract_function_block(win_gamma, "void WG_RestoreGamma( void )\n{")
	extensions_block = _extract_function_block(win_glimp, "static void GLW_InitExtensions( void )")
	shutdown_block = _extract_function_block(win_glimp, "void GLimp_Shutdown( void )\n{")

	assert "glConfig.deviceSupportsGamma = qfalse;" in check_block
	assert "qwglGetDeviceGammaRamp3DFX( hDC, s_oldHardwareGamma );" in check_block
	assert "if ( glConfig.driverType == GLDRV_STANDALONE )" in check_block
	assert "if ( !r_ignorehwgamma->integer )" in check_block
	assert "GetDeviceGammaRamp( hDC, s_oldHardwareGamma );" in check_block
	assert "HIBYTE( s_oldHardwareGamma[0][255] ) <= HIBYTE( s_oldHardwareGamma[0][0] )" in check_block
	assert 'ri.Printf( PRINT_WARNING, "WARNING: suspicious gamma tables, using linear ramp for restoration\\n" );' in check_block
	assert "for ( g = 0; g < 255; g++ )" in check_block

	assert "if ( !glConfig.deviceSupportsGamma || r_ignorehwgamma->integer || !glw_state.hDC ) {" in set_block
	assert "table[0][i] = ( ( ( unsigned short ) red[i] ) << 8 ) | red[i];" in set_block
	assert 'Com_DPrintf( "performing W2K gamma clamp.\\n" );' in set_block
	assert 'Com_DPrintf( "skipping W2K gamma clamp.\\n" );' in set_block
	assert "if ( table[j][i] < table[j][i-1] ) {" in set_block
	assert "qwglSetDeviceGammaRamp3DFX( glw_state.hDC, table );" in set_block
	assert "SetDeviceGammaRamp( glw_state.hDC, table );" in set_block

	assert "qwglSetDeviceGammaRamp3DFX( glw_state.hDC, s_oldHardwareGamma );" in restore_block
	assert "SetDeviceGammaRamp( hDC, s_oldHardwareGamma );" in restore_block
	assert 'if ( !r_ignorehwgamma->integer && r_ext_gamma_control->integer )' in extensions_block
	assert shutdown_block.index("WG_RestoreGamma();") < shutdown_block.index("qwglMakeCurrent( NULL, NULL )")


def _extract_function_block(source: str, signature: str) -> str:
	start = source.index(signature)
	depth = 0
	for offset, char in enumerate(source[start:]):
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start : start + offset + 1]
	raise AssertionError(f"could not extract function block for {signature}")


def test_post_process_render_targets_match_retail_fbo_format_lane() -> None:
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_local = _read("src/code/renderer/tr_local.h")

	assert 'r_floatingPointFBOs = ri.Cvar_Get( "r_floatingPointFBOs", "0", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert "extern cvar_t\t*r_floatingPointFBOs;" in tr_local
	assert "internalFormat = GL_RGBA8;" in tr_backend
	assert "pixelType = GL_UNSIGNED_BYTE;" in tr_backend
	assert "if ( r_floatingPointFBOs && r_floatingPointFBOs->integer ) {" in tr_backend
	assert "\t\tinternalFormat = GL_RGBA16;" in tr_backend
	assert "\t\tpixelType = GL_FLOAT;" in tr_backend
	assert "qglTexImage2D( GL_TEXTURE_RECTANGLE_ARB, 0, internalFormat, width, height, 0, GL_RGBA, pixelType, NULL );" in tr_backend
	assert "s_postProcess.procs.qglFramebufferRenderbufferEXTFunc( GL_FRAMEBUFFER_EXT, GL_STENCIL_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT, target->depthBuffer );" in tr_backend


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
