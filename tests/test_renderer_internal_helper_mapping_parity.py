import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _normalize_whitespace(text: str) -> str:
	return " ".join(text.split())


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


def test_mapping_round_100_records_rg_p5_closure_without_invented_aliases() -> None:
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_100.md")
	normalized = _normalize_whitespace(mapping_round)

	assert "# Quake Live Steam Host Mapping Round 100" in mapping_round
	assert "## Phase 5 Closure Update (2026-04-09)" in mapping_round
	assert "no new aliases were promoted in this pass" in mapping_round
	assert "source-backed compatibility decompositions or compiler-shaped micro-splits" in normalized
	assert "No unresolved high-impact ownership gap remains in an active runtime path." in mapping_round


def test_renderer_internal_helper_ownership_note_bounds_all_rg_g06_file_bands() -> None:
	ownership_note = _read("docs/reverse-engineering/renderer-internal-helper-ownership-2026-04-09.md")
	normalized = _normalize_whitespace(ownership_note)

	assert "## Phase 5 Ownership Closure" in ownership_note
	assert "| `tr_backend.c` |" in ownership_note
	assert "| `tr_bsp.c` |" in ownership_note
	assert "| `tr_curve.c` |" in ownership_note
	assert "| `tr_flares.c` |" in ownership_note
	assert "| `win_glimp.c` |" in ownership_note
	assert "source-backed compatibility decompositions" in normalized
	assert "compiler-shaped splits" in normalized
	assert "No unresolved high-impact ownership gap remains in an active runtime path." in ownership_note


def test_renderer_audit_and_repo_summaries_mark_rg_p5_complete() -> None:
	renderer_audit = _read("docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md")
	audit_summary = _read("AUDIT.md")
	implementation_plan = _read("IMPLEMENTATION_PLAN.md")

	assert "`RG-G06` stays closed" in renderer_audit
	assert "The earlier `RG-P1`..`RG-P6` work remains valid" in renderer_audit
	assert "## What Still Holds From `RG-P1`..`RG-P6`" in renderer_audit
	assert "The open renderer gap register is now wider than the old single-tranche `RG-G05` story." in audit_summary
	assert "`RG-P5` is now complete." in audit_summary
	assert "Task 75: Renderer strict retail-font-stack re-audit and closure-plan refresh [COMPLETED]" in implementation_plan
	assert "Task 73: Renderer internal helper-family ownership closure tranche [COMPLETED]" in implementation_plan
	assert "Parity estimate: **before 93% -> after 96%** (`RG-P5` complete; `RG-G06` closed)" in implementation_plan


def test_representative_rg_g06_helper_seams_remain_present_in_source() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_bsp = _read("src/code/renderer/tr_bsp.c")
	tr_curve = _read("src/code/renderer/tr_curve.c")
	tr_flares = _read("src/code/renderer/tr_flares.c")
	win_glimp = _read("src/code/win32/win_glimp.c")

	assert aliases["sub_435730"] == "GL_BindToTarget"
	assert aliases["sub_4357B0"] == "GL_Bind"
	assert "void RB_ExecuteRenderCommands( const void *data ) {" in tr_backend
	assert "static void RBPP_RebuildState( void ) {" in tr_backend
	assert "void GL_BindToTarget( image_t *image, int glTarget ) {" in tr_backend
	assert "void GL_Bind( image_t *image ) {" in tr_backend
	assert "GL_BindToTarget( image, GL_TEXTURE_2D );" in tr_backend
	assert "static\tvoid R_LoadSurfaces( lump_t *surfs, lump_t *verts, lump_t *indexLump ) {" in tr_bsp
	assert "int R_StitchPatches( int grid1num, int grid2num ) {" in tr_bsp
	assert "static void LerpDrawVert( drawVert_t *a, drawVert_t *b, drawVert_t *out ) {" in tr_curve
	assert "void R_FreeSurfaceGridMesh( srfGridMesh_t *grid ) {" in tr_curve
	assert "void RB_RenderFlares (void) {" in tr_flares
	assert "void RB_TestFlare( flare_t *f ) {" in tr_flares
	assert "static void GLW_StartOpenGL( void )" in win_glimp
	assert "void GLimp_Init( void )" in win_glimp


def test_renderer_mapping_round_314_keeps_image_hash_and_listing_parity() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt")
	hlil_part04 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt")
	functions_csv = _read("references/reverse-engineering/ghidra/quakelive_steam/functions.csv").lower()
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_314.md")
	tr_image = _read("src/code/renderer/tr_image.c")
	tr_shader = _read("src/code/renderer/tr_shader.c")

	expected_aliases = {
		"sub_444940": "R_ImageList_f",
		"sub_446D00": "R_FindImageFile",
		"sub_4474C0": "R_CreateBuiltinImages",
		"sub_4475D0": "R_SetColorMappings",
		"sub_447800": "R_DeleteTextures",
		"sub_4D8990": "generateHashValue",
	}

	for symbol, alias in expected_aliases.items():
		assert aliases[symbol] == alias
		assert symbol.replace("sub_", "fun_00").lower() in functions_csv
		assert f"| `{symbol}` | `{alias}` | High |" in mapping_round

	for expected in (
		"00444940    int32_t sub_444940()",
		'var_1c_2 = "RGB8 "',
		"00446d35  char* esi = *((sub_4d8990(arg1, 0x400) << 2) + &data_586840)",
		"004474c0    int32_t sub_4474c0()",
		"004475d0    int32_t sub_4475d0",
		"00447800    int32_t sub_447800()",
	):
		assert expected in hlil_part02

	for expected in (
		"004d8990    int32_t sub_4d8990(char* arg1, int32_t arg2)",
		"return (arg2 - 1) & ebx",
	):
		assert expected in hlil_part04

	assert 'ri.Printf( PRINT_ALL, "RGB8 " );' in tr_image
	assert "static long generateHashValue( const char *fname, const int size ) {" in tr_shader
	assert "`R_ImageList_f` now prints the retail `RGB8 ` diagnostic label." in mapping_round


def test_renderer_mapping_round_315_restores_color_correct_upload_gamma_gate() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt")
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_315.md")
	mapping_round_316 = _read("docs/reverse-engineering/quakelive_steam_mapping_round_316.md")
	tr_image = _read("src/code/renderer/tr_image.c")
	tr_backend = _read("src/code/renderer/tr_backend.c")

	light_scale_block = _block_from_marker(tr_image, "void R_LightScaleTexture")
	color_mapping_block = _block_from_marker(tr_image, "void R_SetColorMappings")
	color_correct_enabled_block = _block_from_marker(tr_backend, "qboolean RBPP_ColorCorrectEnabled")

	assert aliases["sub_43CCE0"] == "RBPP_ColorCorrectEnabled"
	assert aliases["sub_444D00"] == "R_LightScaleTexture"
	assert "00444d03  void* eax = sub_43cce0()" in hlil_part02
	assert "00444d0a  if (eax == 0)" in hlil_part02
	assert "00444e14  return eax" in hlil_part02
	assert "004475e6  int32_t eax_1 = sub_43cce0()" in hlil_part02
	assert "004477a9  int32_t result = sub_43cce0()" in hlil_part02
	assert "if ( RBPP_ColorCorrectEnabled() ) {\n\t\treturn;\n\t}" in light_scale_block
	assert light_scale_block.index("if ( RBPP_ColorCorrectEnabled() )") < light_scale_block.index("if ( only_gamma )")
	assert "if ( !RBPP_ColorCorrectEnabled() && !glConfig.deviceSupportsGamma ) {" in color_mapping_block
	assert "if ( !RBPP_ColorCorrectEnabled() && glConfig.deviceSupportsGamma )" in color_mapping_block
	assert "if ( !RB_PostProcessEnabled() ) {" in color_correct_enabled_block
	assert "if ( !s_postProcess.supported ) {" in color_correct_enabled_block
	assert "if ( !r_colorCorrectActive || !r_colorCorrectActive->integer ) {" in color_correct_enabled_block
	assert "`R_LightScaleTexture` now exits before upload-time gamma/intensity scaling when shader color correction is active." in mapping_round
	assert "`R_SetColorMappings` now calls `RBPP_ColorCorrectEnabled()` at the same two decision points retail calls `sub_43CCE0`." in mapping_round_316


def test_renderer_mapping_round_317_reconstructs_bloom_scene_target_owner() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	hlil_part01 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_317.md")
	tr_backend = _read("src/code/renderer/tr_backend.c")

	bloom_enabled_block = _block_from_marker(tr_backend, "static qboolean RBPP_BloomEnabled( void ) {")
	bloom_init_block = _block_from_marker(tr_backend, "static qboolean RBPP_InitBloomResources( void ) {")
	bloom_shutdown_block = _block_from_marker(tr_backend, "static void RBPP_ShutdownBloomResources( void ) {")
	bind_block = _block_from_marker(tr_backend, "static void RBPP_BindSceneRenderTarget( void ) {")
	begin_block = _block_from_marker(tr_backend, "void RB_BeginScreenshotReadback")
	end_block = _block_from_marker(tr_backend, "void RB_EndScreenshotReadback")
	bloom_command_block = _block_from_marker(tr_backend, "static const void *RB_BloomPostProcessCommand( const void *data ) {")

	assert aliases["sub_4384A0"] == "RBPP_BloomEnabled"
	assert aliases["sub_4380F0"] == "RBPP_InitBloomResources"
	assert "004384a0    int32_t sub_4384a0()" in hlil_part01
	assert "004384bb  if (sub_4507c0() != 0 && data_1743be8 != 0 && *(data_1740eb8 + 0x30) != 0)" in hlil_part01
	assert "0043814b  if (*(data_1740e38 + 0x30) != 0)" in hlil_part01
	assert "00437e40    int32_t __fastcall sub_437e40" in hlil_part01
	assert "00437b43              if (sub_4384a0() != 0)" in hlil_part01
	assert "00448215  if (sub_4384a0() != 0)" in hlil_part02

	assert "if ( !RB_PostProcessEnabled() ) {" in bloom_enabled_block
	assert "if ( !s_postProcess.supported ) {" in bloom_enabled_block
	assert "if ( !r_bloomActive || !r_bloomActive->integer ) {" in bloom_enabled_block
	assert "RBPP_CreateRenderTarget( &s_postProcess.sceneTarget, width, height, qfalse )" in bloom_init_block
	assert "targets[0] = &s_postProcess.sceneTarget;" in bloom_shutdown_block
	assert bloom_shutdown_block.index("RBPP_DestroyBloomPrograms();") < bloom_shutdown_block.index("qglDeleteTextures") < bloom_shutdown_block.index("qglDeleteFramebuffersEXTFunc") < bloom_shutdown_block.index("qglDeleteRenderbuffersEXTFunc")
	assert "if ( !RBPP_BloomEnabled() || !s_postProcess.sceneTarget.initialized ) {" in bind_block
	assert "if ( !RBPP_BloomEnabled() || !s_postProcess.sceneTarget.initialized ) {" in begin_block
	assert "if ( !RBPP_BloomEnabled() || !s_postProcess.sceneTarget.initialized ) {" in end_block
	assert "if ( cmd->sceneTexture && RBPP_BloomEnabled() && s_postProcess.sceneTarget.initialized ) {" in bloom_command_block
	assert "offscreen scene target is bloom-owned" in mapping_round
	assert "Color-correct-only frames should not route world rendering through the bloom" in mapping_round


def test_renderer_mapping_round_318_reconstructs_postprocess_command_abi() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	hlil_part01 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_318.md")
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_cmds = _read("src/code/renderer/tr_cmds.c")
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_local = _read("src/code/renderer/tr_local.h")
	tr_shader = _read("src/code/renderer/tr_shader.c")

	expected_aliases = {
		"sub_436DC0": "RB_ColorCorrectPostProcessCommand",
		"sub_436EC0": "RB_BloomPostProcessCommand",
		"sub_4384D0": "R_AddBloomPostProcessCommand",
		"sub_43CBA0": "R_AddBindSceneRenderTargetCommand",
		"sub_43CD10": "R_AddColorCorrectPostProcessCommand",
	}
	for symbol, alias in expected_aliases.items():
		assert aliases[symbol] == alias
		assert f"| `{symbol}` | `{alias}` | High |" in mapping_round

	for expected in (
		"00436dc0    void* sub_436dc0(void* arg1)",
		"00436eb7  return arg1 + 0x10",
		"00436ec0    void* sub_436ec0(int32_t arg1)",
		"00437448  return arg1 + 0x38",
		"00437b2d              eax_3, ecx, edx = sub_436dc0(esi)",
		"00437b35              eax_3, ecx, edx, edi = sub_436ec0(esi)",
		"00437b43              if (sub_4384a0() != 0)",
		"00438507              *result = 0xa",
		"00438537              *(result + 0x34) = data_5860c4",
	):
		assert expected in hlil_part01

	for expected in (
		"0043cac0    void sub_43cac0(int32_t* arg1, int32_t* arg2)",
		"0043cad0      sub_43cd10()",
		"0043cbd1          *result = 0xb",
		"0043cd3b              *result = 9",
		"data_5878c0 = j_sub_43cba0",
		"data_5878c4 = j_sub_4384d0",
	):
		assert expected in hlil_part02

	assert "colorCorrectPostProcessCommand_t" in tr_local
	assert "bloomPostProcessCommand_t" in tr_local
	assert "bindSceneRenderTargetCommand_t" in tr_local
	assert "RC_COLOR_CORRECT_POST_PROCESS" in tr_local
	assert "RC_BLOOM_POST_PROCESS" in tr_local
	assert "RC_BIND_SCENE_RENDER_TARGET" in tr_local
	assert "void R_AddBindSceneRenderTargetCommand( void ) {" in tr_backend
	assert "void R_AddBloomPostProcessCommand( void ) {" in tr_backend
	assert "void R_AddColorCorrectPostProcessCommand( void ) {" in tr_backend
	assert "static const void *RB_ColorCorrectPostProcessCommand( const void *data ) {" in tr_backend
	assert "static const void *RB_BloomPostProcessCommand( const void *data ) {" in tr_backend
	assert "static const void *RB_BindSceneRenderTargetCommand( const void *data ) {" in tr_backend
	assert "R_AddBindSceneRenderTargetCommand();" in _block_from_marker(tr_cmds, "void\tR_AddDrawSurfCmd")
	assert "R_AddBloomPostProcessCommand();" in _block_from_marker(tr_cmds, "void RE_EndFrame")
	assert "R_AddColorCorrectPostProcessCommand();" in _block_from_marker(tr_cmds, "void RE_EndFrame")
	assert "re.RetailPostProcessCapture = R_AddBindSceneRenderTargetCommand;" in tr_init
	assert "case RC_COLOR_CORRECT_POST_PROCESS:" in tr_shader
	assert "case RC_BLOOM_POST_PROCESS:" in tr_shader
	assert "case RC_BIND_SCENE_RENDER_TARGET:" in tr_shader
	assert "post-process command abi lane: before 88%, after 96%" in mapping_round.lower()


def test_renderer_mapping_round_319_reconstructs_postprocess_refexport_tail() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	hlil_part01 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_319.md")
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_public = _read("src/code/renderer/tr_public.h")

	for symbol, alias in (
		("sub_4386D0", "RBPP_SetBloomUniforms"),
		("sub_438590", "RBPP_SetBloomUniformsFromCvars"),
		("sub_4384D0", "R_AddBloomPostProcessCommand"),
		("sub_451420", "R_SetPostProcessBloomParameters"),
	):
		assert aliases[symbol] == alias
		assert f"| `{symbol}` | `{alias}` | High |" in mapping_round

	for expected in (
		"data_5878c0 = j_sub_43cba0",
		"data_5878c4 = j_sub_4384d0",
		"data_5878c8 = sub_449f10",
		"data_5878cc = sub_451420",
		"0045142d  data_1740d08 = 1",
		"0045145b  return sub_4386d0",
	):
		assert expected in hlil_part02

	for expected in (
		"0043742e  if (data_1740d08 != 0)",
		"00437430      sub_438590()",
		"00437435      data_1740d08 = 0",
		"004386d0    void* sub_4386d0(float arg1, float arg2, float arg3, float arg4, float arg5)",
		"00438717          data_16e3bd0(data_585fcc, fconvert.s(fconvert.t(arg1)))",
		"0043874e          int32_t var_8_7 = data_16e3bd0(data_5860c8, fconvert.s(fconvert.t(arg2)))",
		"00438761          int32_t var_8_9 = data_16e3bd0(data_5860cc, fconvert.s(fconvert.t(arg4)))",
		"0043876f          int32_t var_8_11 = data_16e3bd0(data_5860d0, fconvert.s(fconvert.t(arg3)))",
		"0043877a          data_16e3bd0(data_5860d4, fconvert.s(fconvert.t(arg5)))",
	):
		assert expected in hlil_part01

	assert "void\t(*RetailBloomPostProcessCommand)( void );" in tr_public
	assert tr_public.index("(*RetailPostProcessCapture)") < tr_public.index("(*RetailBloomPostProcessCommand)") < tr_public.index("(*PostProcessRestart)") < tr_public.index("(*RetailPostProcessPass)")
	assert "re.RetailBloomPostProcessCommand = R_AddBloomPostProcessCommand;" in tr_init
	assert "re.RetailPostProcessPass = R_SetPostProcessBloomParameters;" in tr_init
	assert "static qboolean s_bloomUniformsDirty;" in tr_backend
	assert "static void RBPP_SetBloomUniforms( float brightThreshold, float bloomSaturation, float bloomIntensity, float sceneSaturation, float sceneIntensity ) {" in tr_backend
	assert "void RBPP_SetBloomUniformsFromCvars( void ) {" in tr_backend
	assert "void R_SetPostProcessBloomParameters( float brightThreshold, float bloomSaturation, float bloomIntensity, float sceneSaturation, float sceneIntensity ) {" in tr_backend
	assert "post-process private-tail lane: before 96%, after 99%" in mapping_round.lower()


def test_renderer_mapping_round_320_corrects_bloom_uniform_slot_order() -> None:
	ghidra = _read("src2/ghidra/quakelive_steam/quakelive_steam_decomp.cpp")
	hlil_part01 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt").lower()
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_320.md")
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_local = _read("src/code/renderer/tr_local.h")

	for expected in (
		'DAT_005860c8 = (*DAT_016e3d00)(DAT_005860c4, "p_bloomsaturation");',
		'DAT_005860cc = (*DAT_016e3d00)(DAT_005860c4, "p_scenesaturation");',
		'DAT_005860d0 = (*DAT_016e3d00)(DAT_005860c4, "p_bloomintensity");',
		'DAT_005860d4 = (*DAT_016e3d00)(DAT_005860c4, "p_sceneintensity");',
	):
		assert expected in ghidra

	for expected in (
		"0043874e          int32_t var_8_7 = data_16e3bd0(data_5860c8, fconvert.s(fconvert.t(arg2)))",
		"00438761          int32_t var_8_9 = data_16e3bd0(data_5860cc, fconvert.s(fconvert.t(arg4)))",
		"0043876f          int32_t var_8_11 = data_16e3bd0(data_5860d0, fconvert.s(fconvert.t(arg3)))",
		"0043877a          data_16e3bd0(data_5860d4, fconvert.s(fconvert.t(arg5)))",
	):
		assert expected in hlil_part01

	assert "void R_SetPostProcessBloomParameters( float brightThreshold, float bloomSaturation, float bloomIntensity, float sceneSaturation, float sceneIntensity );" in tr_local
	assert "static void RBPP_SetBloomUniforms( float brightThreshold, float bloomSaturation, float bloomIntensity, float sceneSaturation, float sceneIntensity ) {" in tr_backend
	assert "void R_SetPostProcessBloomParameters( float brightThreshold, float bloomSaturation, float bloomIntensity, float sceneSaturation, float sceneIntensity ) {" in tr_backend
	assert tr_backend.index("GLint bloomSaturationUniform;") < tr_backend.index("GLint sceneSaturationUniform;") < tr_backend.index("GLint bloomIntensityUniform;") < tr_backend.index("GLint sceneIntensityUniform;")
	load_program_block = _block_from_marker(tr_backend, "static qboolean RBPP_LoadProgram( ppProgram_t *program, const char *name, const char *fragmentPath, const char *vertexPath ) {")
	assert load_program_block.index('"p_bloomsaturation"') < load_program_block.index('"p_scenesaturation"') < load_program_block.index('"p_bloomintensity"') < load_program_block.index('"p_sceneintensity"')
	set_uniforms_block = _block_from_marker(tr_backend, "static void RBPP_SetBloomUniforms( float brightThreshold, float bloomSaturation, float bloomIntensity, float sceneSaturation, float sceneIntensity ) {")
	assert set_uniforms_block.index("combineProgram.bloomSaturationUniform") < set_uniforms_block.index("combineProgram.sceneSaturationUniform") < set_uniforms_block.index("combineProgram.bloomIntensityUniform") < set_uniforms_block.index("combineProgram.sceneIntensityUniform")
	assert "post-process bloom uniform naming lane: before 99%, after 99.5%" in mapping_round.lower()


def test_renderer_mapping_round_321_reconstructs_color_correct_uniform_helper() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	ghidra = _read("src2/ghidra/quakelive_steam/quakelive_steam_decomp.cpp")
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_321.md")
	tr_backend = _read("src/code/renderer/tr_backend.c")

	assert aliases["sub_43CD60"] == "RBPP_SetColorCorrectUniformsFromCvars"

	for expected in (
		"0043cd60    void sub_43cd60()",
		"0043cd89  if (sub_4507c0() != 0 && data_1743be8 != 0 && *(data_1740d90 + 0x30) != 0)",
		"0043cdf5          data_16e3bd0(data_586224",
		"0043ce2e          data_16e3bd0(data_586228",
		"0043ce33      data_16e3bd0(data_58622c",
		"0043d083          int32_t eax_5 = data_16e3d00(data_586220, \"p_gammarecip\")",
		"0043d0a0          data_586228 = data_16e3d00(edx_2, \"p_overbright\")",
		"0043d0b0          int32_t eax_8 = data_16e3d00(data_586220, \"p_contrast\")",
	):
		assert expected in hlil_part02

	for expected in (
		'(*DAT_016e3bd0)(DAT_00586224, fVar4);',
		'(*DAT_016e3bd0)(DAT_00586228, fVar2);',
		'(*DAT_016e3bd0)(DAT_0058622c, uVar3);',
		'DAT_00586224 = (*DAT_016e3d00)(DAT_00586220, "p_gammaRecip");',
		'DAT_00586228 = (*DAT_016e3d00)(DAT_00586220, "p_overbright");',
		'DAT_0058622c = (*DAT_016e3d00)(DAT_00586220, "p_contrast");',
	):
		assert expected in ghidra

	color_uniform_block = _block_from_marker(tr_backend, "static void RBPP_SetColorCorrectUniforms( qboolean browserOverride ) {")
	color_uniform_from_cvars_block = _block_from_marker(tr_backend, "void RBPP_SetColorCorrectUniformsFromCvars( void ) {")
	color_init_block = _block_from_marker(tr_backend, "static qboolean RBPP_InitColorCorrectResources( void ) {")
	color_pass_block = _block_from_marker(tr_backend, "static void RBPP_ApplyColorCorrectPass( const colorCorrectPostProcessCommand_t *cmd ) {")

	assert "static void RBPP_SetColorCorrectUniforms( qboolean browserOverride ) {" in tr_backend
	assert "void RBPP_SetColorCorrectUniformsFromCvars( void ) {" in tr_backend
	assert "if ( !RBPP_ColorCorrectEnabled() ) {" in color_uniform_from_cvars_block
	assert "RBPP_SetColorCorrectUniforms( qtrue );" in color_uniform_from_cvars_block
	assert color_uniform_block.index("colorCorrectProgram.gammaRecipUniform") < color_uniform_block.index("colorCorrectProgram.overbrightUniform") < color_uniform_block.index("colorCorrectProgram.contrastUniform")
	assert "RBPP_SetColorCorrectUniforms( qfalse );" in color_init_block
	assert "RBPP_SetColorCorrectUniformsFromCvars();" in color_pass_block
	assert "qglUniform1fARBFunc" not in color_pass_block
	assert "post-process color-correct uniform helper lane: before 99.5%, after 99.7%" in mapping_round.lower()


def test_renderer_mapping_round_322_reconstructs_live_postprocess_cvar_refresh() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	ghidra = _read("src2/ghidra/quakelive_steam/quakelive_steam_decomp.cpp")
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_322.md")
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_cmds = _read("src/code/renderer/tr_cmds.c")
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_local = _read("src/code/renderer/tr_local.h")

	assert aliases["sub_43CD60"] == "RBPP_SetColorCorrectUniformsFromCvars"
	assert aliases["sub_438590"] == "RBPP_SetBloomUniformsFromCvars"

	for expected in (
		"if ((*(int*)(DAT_01740ddc + 0x20) != 0) || (*(int*)(DAT_01740e40 + 0x20) != 0))",
		"*(std::uint32_t*)(DAT_01740e40 + 0x20) = 0;",
		"FUN_0043cd60();",
		"if ((((*(int*)(DAT_01740e84 + 0x20) != 0) || (*(int*)(DAT_01740e44 + 0x20) != 0)) ||",
		"*(std::uint32_t*)(DAT_01740e84 + 0x20) = 0;",
		"*(std::uint32_t*)(DAT_01740e44 + 0x20) = 0;",
		"*(std::uint32_t*)(DAT_01740e5c + 0x20) = 0;",
		"*(std::uint32_t*)(DAT_01743c10 + 0x20) = 0;",
		"*(std::uint32_t*)(DAT_01740e78 + 0x20) = 0;",
		"FUN_00438590();",
		"if (*(int*)(DAT_01740ddc + 0x20) != 0)",
		"R_SetColorMappings();",
	):
		assert expected in ghidra

	for expected in (
		"0043c922      if (*(data_1740ddc + 0x20) != 0 || *(eax_5 + 0x20) != 0)",
		"0043c924          *(eax_5 + 0x20) = 0",
		"0043c927          sub_43cd60()",
		"0043c960      if (*(eax_6 + 0x20) != 0 || *(data_1740e44 + 0x20) != 0 || *(data_1740e5c + 0x20) != 0",
		"0043c962          *(eax_6 + 0x20) = 0",
		"0043c96a          *(data_1740e44 + 0x20) = 0",
		"0043c973          *(data_1740e5c + 0x20) = 0",
		"0043c97c          *(data_1743c10 + 0x20) = 0",
		"0043c984          *(data_1740e78 + 0x20) = 0",
		"0043c987          sub_438590()",
		"0043c994      if (*(eax_9 + 0x20) != 0)",
		"0043c9b7          sub_4475d0(0)",
	):
		assert expected in hlil_part02

	live_block = _block_from_marker(tr_cmds, "static void R_RefreshLivePostProcessCvars( void ) {")
	begin_frame_block = _block_from_marker(tr_cmds, "void RE_BeginFrame( stereoFrame_t stereoFrame ) {")

	assert "static void R_ClearLivePostProcessModifiedFlags( void ) {" not in tr_init
	assert "R_ClearLivePostProcessModifiedFlags();" not in tr_init
	assert "void RBPP_SetColorCorrectUniformsFromCvars( void );" in tr_local
	assert "void RBPP_SetBloomUniformsFromCvars( void );" in tr_local
	assert "void RBPP_SetColorCorrectUniformsFromCvars( void ) {" in tr_backend
	assert "void RBPP_SetBloomUniformsFromCvars( void ) {" in tr_backend
	assert "r_gamma->modified = qfalse;" not in live_block
	assert "\t\t\tr_contrast->modified = qfalse;" in live_block
	assert "\t\t\tr_bloomBrightThreshold->modified = qfalse;" in live_block
	assert "\t\t\tr_bloomSaturation->modified = qfalse;" in live_block
	assert "\t\t\tr_bloomSceneSaturation->modified = qfalse;" in live_block
	assert "\t\t\tr_bloomIntensity->modified = qfalse;" in live_block
	assert "\t\t\tr_bloomSceneIntensity->modified = qfalse;" in live_block
	assert "RBPP_SetColorCorrectUniformsFromCvars();" in live_block
	assert "RBPP_SetBloomUniformsFromCvars();" in live_block
	assert begin_frame_block.index("R_RefreshLivePostProcessCvars();") < begin_frame_block.index("if ( r_gamma->modified ) {")
	assert "post-process live cvar refresh lane: before 99.7%, after 99.85%" in mapping_round.lower()


def test_renderer_mapping_round_323_splits_color_correct_init_and_live_browser_override() -> None:
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	ghidra = _read("src2/ghidra/quakelive_steam/quakelive_steam_decomp.cpp")
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_323.md")
	tr_backend = _read("src/code/renderer/tr_backend.c")

	live_hlil = hlil_part02[hlil_part02.index("0043cd60    void sub_43cd60()"):hlil_part02.index("0043ce50    int32_t __fastcall sub_43ce50")]
	init_hlil = hlil_part02[hlil_part02.index("0043cfe0    void sub_43cfe0()"):hlil_part02.index("0043d160    void __convention")]
	live_ghidra = ghidra[ghidra.index("/* FUN_0043cd60 @ 0x0043CD60 size 229 */"):ghidra.index("/* FUN_0043ce50 @ 0x0043CE50 size 345 */")]
	init_ghidra = ghidra[ghidra.index("/* FUN_0043cfe0 @ 0x0043CFE0 size 383 */"):ghidra.index("/* FUN_0043d160 @ 0x0043D160 size 145 */")]
	color_uniform_block = _block_from_marker(tr_backend, "static void RBPP_SetColorCorrectUniforms( qboolean browserOverride ) {")
	color_uniform_from_cvars_block = _block_from_marker(tr_backend, "void RBPP_SetColorCorrectUniformsFromCvars( void ) {")
	color_init_block = _block_from_marker(tr_backend, "static qboolean RBPP_InitColorCorrectResources( void ) {")

	assert "data_15ee390" in live_hlil
	assert "data_15ee390" not in init_hlil
	assert "0043cd98      int32_t ecx_2 = data_15ee390" in live_hlil
	assert "0043d12d          data_16e3bd0(data_58622c, fconvert.s(fconvert.t(*(data_1740e40 + 0x2c))))" in init_hlil
	assert "DAT_015ee390 != 0" in live_ghidra
	assert "DAT_015ee390" not in init_ghidra
	assert "static void RBPP_SetColorCorrectUniforms( qboolean browserOverride ) {" in tr_backend
	assert "if ( ( !browserOverride || !web_browserActive || !web_browserActive->integer ) && r_gamma && r_gamma->value > 0.0f ) {" in color_uniform_block
	assert "if ( ( !browserOverride || !web_browserActive || !web_browserActive->integer ) && r_contrast ) {" in color_uniform_block
	assert "RBPP_SetColorCorrectUniforms( qfalse );" in color_init_block
	assert "RBPP_SetColorCorrectUniforms( qtrue );" in color_uniform_from_cvars_block
	assert "post-process color-correct browser override lane: before 99.85%, after 99.9%" in mapping_round.lower()


def test_renderer_mapping_round_324_retires_legacy_framebuffer_scratch_lane() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	hlil_part01 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_324.md")
	tr_backend = _read("src/code/renderer/tr_backend.c")

	create_block = _block_from_marker(tr_backend, "static qboolean RBPP_CreateRenderTarget( ppRenderTarget_t *target, int width, int height, qboolean linearFilter ) {")
	renderbuffer_block = _block_from_marker(tr_backend, "static GLuint RBPP_CreateDepthStencilRenderbuffer( int width, int height ) {")
	swap_block = _block_from_marker(tr_backend, "const void\t*RB_SwapBuffers( const void *data ) {")
	execute_block = _block_from_marker(tr_backend, "void RB_ExecuteRenderCommands( const void *data ) {")

	expected_aliases = {
		"sub_437E40": "RBPP_CreateBloomRenderTargets",
		"sub_438790": "RBPP_BindSceneRenderTarget",
		"sub_4387D0": "RBPP_ReleaseSceneRenderTarget",
		"sub_4500B0": "RBPP_CreateRenderTarget",
	}
	for symbol, alias in expected_aliases.items():
		assert aliases[symbol] == alias
		assert f"| `{symbol}` | `{alias}` | High |" in mapping_round

	for expected in (
		"00437e40    int32_t __fastcall sub_437e40",
		"sub_4500b0(",
		"00438790    int32_t sub_438790()",
		"return data_16e403c(0x8d40, result)",
		"004387d0    int32_t sub_4387d0()",
		"return data_16e403c(0x8d40, 0)",
	):
		assert expected in hlil_part01

	for expected in (
		"004500b0    int32_t sub_4500b0(",
		"data_16e3dfc(0x84f5, *arg3)",
		"data_16e3c7c(0x84f5, 0, var_2c",
		"data_16e403c(0x8d40, *arg4)",
		"data_16e3d34(0x8d40, 0x8ce0, 0x84f5, *arg3, 0)",
		"data_16e3ee0(0x8d40, 0x8d00, 0x8d41, *arg5)",
		"data_16e3ee0(0x8d40, 0x8d20, 0x8d41, *arg5)",
		'"post process failure - unable to',
	):
		assert expected in hlil_part02

	assert "GL_TEXTURE_RECTANGLE_ARB" in create_block
	assert "GL_DEPTH24_STENCIL8_EXT" in renderbuffer_block
	assert "GL_STENCIL_ATTACHMENT_EXT" in create_block
	assert "GL_TEXTURE_2D" not in create_block
	assert "glFramebufferProcs_t" not in tr_backend
	assert "renderTarget_t" not in tr_backend
	assert "s_fboProcs" not in tr_backend
	assert "s_sceneRenderTarget" not in tr_backend
	assert "RB_LoadFramebufferProcs" not in tr_backend
	assert "RB_UploadBloomScratch" not in tr_backend
	assert "RB_DrawBloomPass" not in tr_backend
	assert "RBPP_ReleaseSceneRenderTarget();" in swap_block
	assert "RBPP_ResetIfNeeded();" in execute_block
	assert "post-process framebuffer owner lane: before 99.9%, after 99.93%" in mapping_round.lower()


def test_renderer_mapping_round_325_reconstructs_bloom_teardown_order() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	hlil_part01 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_325.md")
	tr_backend = _read("src/code/renderer/tr_backend.c")

	bloom_programs_block = _block_from_marker(tr_backend, "static void RBPP_DestroyBloomPrograms( void ) {")
	bloom_shutdown_block = _block_from_marker(tr_backend, "static void RBPP_ShutdownBloomResources( void ) {")
	destroy_program_block = _block_from_marker(tr_backend, "static void RBPP_DestroyProgram( ppProgram_t *program ) {")

	assert aliases["sub_437DA0"] == "RBPP_ShutdownBloomResources"
	assert aliases["sub_4506A0"] == "RBPP_DestroyProgram"
	assert "| `sub_437DA0` | `RBPP_ShutdownBloomResources` | High |" in mapping_round
	assert "| `sub_4506A0` | `RBPP_DestroyProgram` | High |" in mapping_round

	for expected in (
		"00437da0    int32_t sub_437da0()",
		"for (void* i = &data_585fb8; i s< &data_5860d8; i += 0x24)",
		"sub_4506a0(i)",
		"data_16e3fb4(1, i_1 + &data_585f78)",
		"data_16e3ca4(1, i_1 + &data_585f98)",
		"data_16e3e70(1, i_1 + &data_5860d8)",
		'return data_1740d48("r_bloomactive"',
	):
		assert expected in hlil_part01

	for expected in (
		"004506a0    void sub_4506a0(void* arg1)",
		"data_16e3ac4(ecx, eax_1)",
		"data_16e3dc0(*(arg1 + 0x10))",
		"data_16e3b18(eax_4)",
	):
		assert expected in hlil_part02

	assert bloom_programs_block.index("&s_postProcess.brightPassProgram") < bloom_programs_block.index("&s_postProcess.downsampleProgram") < bloom_programs_block.index("&s_postProcess.blurVerticalProgram") < bloom_programs_block.index("&s_postProcess.blurHorizontalProgram") < bloom_programs_block.index("&s_postProcess.combineProgram")
	assert "targets[0] = &s_postProcess.sceneTarget;" in bloom_shutdown_block
	assert "targets[7] = &s_postProcess.bloomQuarterHorizontalTarget;" in bloom_shutdown_block
	assert bloom_shutdown_block.index("RBPP_DestroyBloomPrograms();") < bloom_shutdown_block.index("qglDeleteTextures")
	assert bloom_shutdown_block.index("qglDeleteTextures") < bloom_shutdown_block.index("qglDeleteFramebuffersEXTFunc")
	assert bloom_shutdown_block.index("qglDeleteFramebuffersEXTFunc") < bloom_shutdown_block.index("qglDeleteRenderbuffersEXTFunc")
	assert bloom_shutdown_block.index("qglDeleteRenderbuffersEXTFunc") < bloom_shutdown_block.index("Com_Memset")
	assert 'ri.Cvar_Set( "r_bloomActive", "0" );' in bloom_shutdown_block
	assert "qglDetachObjectARBFunc" in destroy_program_block
	assert destroy_program_block.index("qglDetachObjectARBFunc") < destroy_program_block.index("qglDeleteObjectARBFunc( program->programObject )")
	assert destroy_program_block.index("qglDeleteObjectARBFunc( program->programObject )") < destroy_program_block.index("qglDeleteObjectARBFunc( program->fragmentObject )") < destroy_program_block.index("qglDeleteObjectARBFunc( program->vertexObject )")
	assert "post-process bloom teardown lane: before 99.93%, after 99.95%" in mapping_round.lower()


def test_renderer_mapping_round_326_reconstructs_depth_stencil_renderbuffer_cache() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	functions_csv = _read("references/reverse-engineering/ghidra/quakelive_steam/functions.csv").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_326.md")
	tr_backend = _read("src/code/renderer/tr_backend.c")

	renderbuffer_block = _block_from_marker(tr_backend, "static GLuint RBPP_CreateDepthStencilRenderbuffer( int width, int height ) {")
	create_block = _block_from_marker(tr_backend, "static qboolean RBPP_CreateRenderTarget( ppRenderTarget_t *target, int width, int height, qboolean linearFilter ) {")
	shutdown_block = _block_from_marker(tr_backend, "static void RBPP_ShutdownBloomResources( void ) {")

	expected_aliases = {
		"sub_44FFD0": "RBPP_CreateDepthStencilRenderbuffer",
		"sub_4500B0": "RBPP_CreateRenderTarget",
		"sub_450710": "RBPP_RebuildState",
		"sub_450780": "RBPP_Shutdown",
	}
	for symbol, alias in expected_aliases.items():
		assert aliases[symbol] == alias
		assert f"| `{symbol}` | `{alias}` | High |" in mapping_round
		assert symbol.replace("sub_", "fun_00").lower() in functions_csv

	for expected in (
		"0044ffd0    int32_t __convention(\"regparm\") sub_44ffd0",
		"0044ffdd  if (data_1743bac s>= 0x18)",
		"0045000b      if (edx + 1 s<= 8)",
		"0045003d          data_16e3b2c(0x8d41, 0x88f0, var_18, arg5)",
		"00450043          int32_t eax_1 = data_16e3a9c()",
		"00450088              *(ecx_3 + &data_1716e20) = arg4",
		"00450096              *(ecx_3 + &data_1716e28) = result",
		"0045014b  int32_t eax_1 = sub_44ffd0",
		"00450156  if (eax_1 s< 1)",
		"00450178  *arg5 = eax_1",
		"004502ad      data_16e3ee0(0x8d40, 0x8d00, 0x8d41, *arg5)",
		"00450719  sub_4c95e0(&data_1716e20, 0, 0x60)",
		"00450728  data_5881e8 = 0",
		"00450789  sub_4c95e0(&data_1716e20, 0, 0x60)",
		"0045078e  data_5881e8 = 0",
	):
		assert expected in hlil_part02

	assert "#define POST_PROCESS_RENDERBUFFER_CACHE_MAX 8" in tr_backend
	assert "ppRenderbufferCacheEntry_t renderbufferCache[POST_PROCESS_RENDERBUFFER_CACHE_MAX];" in tr_backend
	assert "int renderbufferCacheCount;" in tr_backend
	assert "if ( glConfig.depthBits < 24 ) {" in renderbuffer_block
	assert "s_postProcess.renderbufferCache[i].width == width && s_postProcess.renderbufferCache[i].height == height" in renderbuffer_block
	assert "s_postProcess.renderbufferCacheCount >= POST_PROCESS_RENDERBUFFER_CACHE_MAX" in renderbuffer_block
	assert "s_postProcess.procs.qglGenRenderbuffersEXTFunc( 1, &renderbuffer );" in renderbuffer_block
	assert "s_postProcess.procs.qglRenderbufferStorageEXTFunc( GL_RENDERBUFFER_EXT, GL_DEPTH24_STENCIL8_EXT, width, height );" in renderbuffer_block
	assert "errorCode = qglGetError();" in renderbuffer_block
	assert "s_postProcess.renderbufferCache[i].renderbuffer = renderbuffer;" in renderbuffer_block
	assert "depthBuffer = RBPP_CreateDepthStencilRenderbuffer( width, height );" in create_block
	assert "target->depthBuffer = depthBuffer;" in create_block
	assert 'ri.Printf( PRINT_DEVELOPER, "Unable to create render buffer object.\\n\\n" );' in create_block
	assert "s_postProcess.procs.qglGenRenderbuffersEXTFunc" not in create_block
	assert "s_postProcess.procs.qglBindRenderbufferEXTFunc" not in create_block
	assert "s_postProcess.procs.qglRenderbufferStorageEXTFunc" not in create_block
	assert create_block.index("RBPP_CreateDepthStencilRenderbuffer") < create_block.index("qglGenTextures")
	assert create_block.index("qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, 0 );") < create_block.index("qglGenFramebuffersEXTFunc")
	assert "Com_Memset( s_postProcess.renderbufferCache, 0, sizeof( s_postProcess.renderbufferCache ) );" in shutdown_block
	assert "s_postProcess.renderbufferCacheCount = 0;" in shutdown_block
	assert "post-process depth-stencil renderbuffer cache lane: before 99.95%, after 99.97%" in mapping_round.lower()


def test_renderer_mapping_round_327_reconstructs_postprocess_gl_error_wiring() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	functions_csv = _read("references/reverse-engineering/ghidra/quakelive_steam/functions.csv").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_327.md")
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_local = _read("src/code/renderer/tr_local.h")

	create_block = _block_from_marker(tr_backend, "static qboolean RBPP_CreateRenderTarget( ppRenderTarget_t *target, int width, int height, qboolean linearFilter ) {")
	link_block = _block_from_marker(tr_backend, "static qboolean RBPP_LinkProgram( ppProgram_t *program ) {")
	load_program_block = _block_from_marker(tr_backend, "static qboolean RBPP_LoadProgram( ppProgram_t *program, const char *name, const char *fragmentPath, const char *vertexPath ) {")
	color_texture_block = _block_from_marker(tr_backend, "static qboolean RBPP_CreateColorCorrectTexture( void ) {")
	gl_check_block = _block_from_marker(tr_init, "qboolean GL_CheckErrors( void ) {")

	expected_aliases = {
		"sub_447E40": "GL_CheckErrors",
		"sub_4500B0": "RBPP_CreateRenderTarget",
		"sub_4505F0": "RBPP_LinkProgram",
		"sub_450640": "RBPP_LoadProgram",
	}
	for symbol, alias in expected_aliases.items():
		assert aliases[symbol] == alias
		assert f"| `{symbol}` | `{alias}` | High |" in mapping_round
		assert symbol.replace("sub_", "fun_00").lower() in functions_csv

	for expected in (
		"00447e40    int32_t sub_447e40()",
		"00447e50  int32_t eax_2 = data_16e3a9c()",
		"00447e74  if (eax_2 == 0 || *(data_1740f4c + 0x30) != 0)",
		"00447e69      return 0",
		"00447fd1  data_1740d24(0, \"gl_checkerrors: %s\", &var_48)",
		"00447fec  return 1",
		"004501de  if (sub_447e40() == 0)",
		"00450303          int32_t eax_8 = sub_447e40()",
		"004505f0    int32_t sub_4505f0(void* arg1)",
		"00450625  data_16e3e94(*(arg1 + 0x10))",
		"0045062b  int32_t eax_3 = sub_447e40()",
		"0045068d      return sub_4505f0(arg3)",
	):
		assert expected in hlil_part02

	assert "qboolean GL_CheckErrors( void );" in tr_local
	assert "qboolean GL_CheckErrors( void ) {" in tr_init
	assert "return qfalse;" in gl_check_block
	assert "return qtrue;" in gl_check_block
	assert "ri.Error( ERR_FATAL, \"GL_CheckErrors: %s\", s );" in gl_check_block
	assert "if ( GL_CheckErrors() ) {" in create_block
	assert "qglGetError()" not in create_block
	assert "s_postProcess.procs.qglBindRenderbufferEXTFunc" not in create_block
	assert create_block.index("qglTexImage2D") < create_block.index("if ( GL_CheckErrors() )") < create_block.index("qglTexParameteri")
	assert create_block.index("qglCheckFramebufferStatusEXTFunc") < create_block.rindex("if ( GL_CheckErrors() )")
	assert "static qboolean RBPP_LinkProgram( ppProgram_t *program ) {" in tr_backend
	assert "program->programObject = s_postProcess.procs.qglCreateProgramObjectARBFunc();" in link_block
	assert "s_postProcess.procs.qglAttachObjectARBFunc( program->programObject, program->fragmentObject );" in link_block
	assert "s_postProcess.procs.qglAttachObjectARBFunc( program->programObject, program->vertexObject );" in link_block
	assert "s_postProcess.procs.qglLinkProgramARBFunc( program->programObject );" in link_block
	assert "if ( GL_CheckErrors() ) {" in link_block
	assert "RBPP_LinkProgram( program )" in load_program_block
	assert "GL_OBJECT_LINK_STATUS_ARB" not in tr_backend
	assert "linkStatus" not in load_program_block
	assert "qglGetObjectParameterivARBFunc( program->programObject" not in load_program_block
	assert "if ( GL_CheckErrors() ) {" in color_texture_block
	assert "qglGetError()" not in color_texture_block
	assert "post-process gl error and link lane: before 99.97%, after 99.985%" in mapping_round.lower()


def test_renderer_mapping_round_328_splits_framebuffer_and_shader_proc_gates() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_328.md")
	tr_backend = _read("src/code/renderer/tr_backend.c")

	framebuffer_loader_block = _block_from_marker(tr_backend, "static qboolean RBPP_LoadFramebufferProcs( void ) {")
	full_loader_block = _block_from_marker(tr_backend, "static qboolean RBPP_LoadProcs( void ) {")
	create_block = _block_from_marker(tr_backend, "static qboolean RBPP_CreateRenderTarget( ppRenderTarget_t *target, int width, int height, qboolean linearFilter ) {")
	load_program_block = _block_from_marker(tr_backend, "static qboolean RBPP_LoadProgram( ppProgram_t *program, const char *name, const char *fragmentPath, const char *vertexPath ) {")

	assert aliases["sub_4500B0"] == "RBPP_CreateRenderTarget"
	assert aliases["sub_450640"] == "RBPP_LoadProgram"
	assert "| `sub_4500B0` | `RBPP_CreateRenderTarget` | High |" in mapping_round
	assert "| `sub_450640` | `RBPP_LoadProgram` | High |" in mapping_round

	for expected in (
		"0045013c  if (data_16e3bec == 0 || data_16e3ca4 == 0 || data_16e403c == 0 || data_16e3d34 == 0",
		"|| data_16e3f34 == 0 || data_16e3d2c == 0 || data_16e3e70 == 0",
		"|| data_16e3c44 == 0 || data_16e3b2c == 0 || data_16e4020 == 0",
		"|| data_16e3ee0 == 0)",
		"00450655  if (*(data_1740ed4 + 0x30) == 0 || data_1743be8 == 0)",
		"0045066a  if (sub_4504f0(arg1, arg3) != 0 && sub_450570(arg2, arg3) != 0)",
		"0045068d      return sub_4505f0(arg3)",
	):
		assert expected in hlil_part02

	assert "qboolean framebufferProcsLoaded;" in tr_backend
	assert "qboolean framebufferSupported;" in tr_backend
	assert "static qboolean RBPP_LoadFramebufferProcs( void ) {" in tr_backend
	assert "if ( s_postProcess.framebufferProcsLoaded ) {" in framebuffer_loader_block
	assert "return s_postProcess.framebufferSupported;" in framebuffer_loader_block
	assert "GL_EXT_framebuffer_object" in framebuffer_loader_block
	assert "GL_ARB_texture_rectangle" in framebuffer_loader_block
	assert "GL_ARB_shader_objects" not in framebuffer_loader_block
	assert "qglCreateShaderObjectARBFunc" not in framebuffer_loader_block
	assert "qglGetUniformLocationARBFunc" not in framebuffer_loader_block
	assert "qglGetIntegerv( GL_MAX_RECTANGLE_TEXTURE_SIZE_ARB, &s_postProcess.maxRectangleTextureSize );" in framebuffer_loader_block
	assert "s_postProcess.framebufferSupported = qtrue;" in framebuffer_loader_block
	assert "if ( !RBPP_LoadFramebufferProcs() ) {" in full_loader_block
	assert "GL_ARB_shader_objects" in full_loader_block
	assert "GL_ARB_vertex_shader" in full_loader_block
	assert "GL_ARB_fragment_shader" in full_loader_block
	assert "qglCreateShaderObjectARBFunc" in full_loader_block
	assert "qglGetUniformLocationARBFunc" in full_loader_block
	assert "RBPP_LoadFramebufferProcs()" in create_block
	assert "RBPP_LoadProcs()" not in create_block
	assert "RBPP_LoadProcs()" in load_program_block
	assert "post-process proc gate lane: before 99.985%, after 99.99%" in mapping_round.lower()


def test_renderer_mapping_round_341_closes_postprocess_command_payload_wiring() -> None:
	hlil_part01 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_341.md")
	tr_backend = _read("src/code/renderer/tr_backend.c")

	apply_bloom_block = _block_from_marker(tr_backend, "static qboolean RBPP_ApplyBloom( const bloomPostProcessCommand_t *cmd ) {")
	apply_color_block = _block_from_marker(tr_backend, "static void RBPP_ApplyColorCorrectPass( const colorCorrectPostProcessCommand_t *cmd ) {")
	bloom_command_block = _block_from_marker(tr_backend, "static const void *RB_BloomPostProcessCommand( const void *data ) {")
	color_command_block = _block_from_marker(tr_backend, "static const void *RB_ColorCorrectPostProcessCommand( const void *data ) {")

	for expected in (
		"00436dff      data_16e3d98(0x84f5)",
		"00436e46      int32_t edx_2 = data_16e3d14(*(arg1 + 8))",
		"00436eb7  return arg1 + 0x10",
		"00438537              *(result + 0x34) = data_5860c4",
		"00437448  return arg1 + 0x38",
	):
		assert expected in hlil_part01

	for expected in (
		"0043cd3b              *result = 9",
		"0043cd47              *(result + 8) = data_586220",
		"0043cd50              *(result + 4) = data_586234",
	):
		assert expected in hlil_part02

	assert "RBPP_ApplyBloom( cmd )" in bloom_command_block
	assert "RBPP_BlitSceneTarget( cmd->sceneTexture );" in bloom_command_block
	assert "RBPP_ApplyColorCorrectPass( cmd );" in color_command_block
	assert "qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, cmd->colorCorrectTexture );" in apply_color_block
	assert "s_postProcess.procs.qglUseProgramObjectARBFunc( cmd->colorCorrectProgram );" in apply_color_block
	assert "s_postProcess.procs.qglUseProgramObjectARBFunc( cmd->downsampleProgram );" in apply_bloom_block
	assert "s_postProcess.procs.qglUseProgramObjectARBFunc( cmd->brightPassProgram );" in apply_bloom_block
	assert "s_postProcess.procs.qglUseProgramObjectARBFunc( cmd->blurVerticalProgram );" in apply_bloom_block
	assert "s_postProcess.procs.qglUseProgramObjectARBFunc( cmd->blurHorizontalProgram );" in apply_bloom_block
	assert "s_postProcess.procs.qglUseProgramObjectARBFunc( cmd->combineProgram );" in apply_bloom_block
	assert "post-process command payload wiring lane: before 99.99%, after 100%" in mapping_round.lower()


def test_renderer_mapping_round_342_closes_win32_gl_startup_wiring() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	functions_csv = _read("references/reverse-engineering/ghidra/quakelive_steam/functions.csv").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	hlil_part06 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt").lower()
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_342.md")
	renderer_wiring = _read("docs/reverse-engineering/renderer-wiring-reverse-engineering-round-2026-05-20.md")
	source_ledger = _read("docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md")
	renderer_audit = _read("docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md")
	ownership_note = _read("docs/reverse-engineering/renderer-internal-helper-ownership-2026-04-09.md")
	tr_init = _read("src/code/renderer/tr_init.c")
	win_glimp = _read("src/code/win32/win_glimp.c")
	normalized_renderer_wiring = _normalize_whitespace(renderer_wiring)
	normalized_source_ledger = _normalize_whitespace(source_ledger)
	normalized_renderer_audit = _normalize_whitespace(renderer_audit)
	normalized_ownership_note = _normalize_whitespace(ownership_note)

	expected_aliases = {
		"sub_46A2A0": "GLW_MakeContext",
		"sub_46A9F0": "GLW_GetModeInfo",
		"sub_46B7A0": "GLW_CheckOSVersion",
		"sub_46C020": "GLW_StartDriverAndSetMode",
		"sub_46C060": "GLW_LoadOpenGL",
		"sub_46C1E0": "GLW_StartOpenGL",
		"sub_46C2E0": "GLimp_Init",
	}

	for symbol, alias in expected_aliases.items():
		assert aliases[symbol] == alias
		assert symbol.replace("sub_", "fun_00").lower() in functions_csv

	for expected in (
		"0046a2a0    int32_t sub_46a2a0",
		"0046a9f0    int32_t __convention(\"regparm\") sub_46a9f0",
		"0046b7a0    int32_t sub_46b7a0()",
		"0046c020    int32_t __fastcall sub_46c020",
		"0046c060    int32_t sub_46c060",
		"0046c1e0    void* sub_46c1e0()",
		"0046c2e0    int32_t sub_46c2e0()",
		"0046c187          if (sub_46c020(arg1, 7.00649232e-45f) != 0)",
		"0046c19b          if (sub_46c020(arg1, 1.68155816e-44f) != 0)",
	):
		assert expected in hlil_part02

	assert '00534e38  char const data_534e38[0x35] = "glw_startopengl() - could not load opengl subsystem\\n", 0' in hlil_part06
	assert '{ "Mode  5: 640x480",\t\t640,\t480,\t0 },' in tr_init
	assert '{ "Mode 12: 1024x768",\t\t1024,\t768,\t0 },' in tr_init
	assert "static int GLW_MakeContext( PIXELFORMATDESCRIPTOR *pPFD )" in win_glimp
	assert "static qboolean GLW_GetModeInfo( int *width, int *height, int *aspectRatio, int mode, qboolean fullscreen )" in win_glimp
	assert "static qboolean GLW_CheckOSVersion( void )" in win_glimp
	assert "static qboolean GLW_StartDriverAndSetMode( const char *drivername," in win_glimp
	assert "static qboolean GLW_LoadOpenGL( const char *drivername )" in win_glimp
	assert "static void GLW_StartOpenGL( void )" in win_glimp
	assert "started = GLW_StartDriverAndSetMode( drivername, 5, 16, qtrue );" in win_glimp
	assert "started = GLW_StartDriverAndSetMode( drivername, 12, 16, qtrue );" in win_glimp
	assert "GLW_StartDriverAndSetMode( drivername, 3, 16, qtrue )" not in win_glimp
	assert "Win32 OpenGL startup/fallback wiring lane: before 96%, after 100%" in mapping_round
	assert "2026-06-02 follow-up: Win32 OpenGL startup wiring is now pinned through" in renderer_wiring
	assert "retail mode `5` then mode `12` safe-mode sequence" in normalized_renderer_wiring
	assert "2026-06-02 follow-up validation pins the Win32 OpenGL startup lane through mapping round 342" in normalized_renderer_wiring
	assert "Win32 OpenGL startup/fallback wiring pinned in round 342" in source_ledger
	assert "retail ICD fallback pair at Quake Live modes `5` and `12`" in normalized_source_ledger
	assert "mapping rounds 98, 100, and 342" in renderer_audit
	assert "OpenGL startup ICD fallback modes `5` then `12`" in normalized_renderer_audit
	assert "mapping round 342's promoted `GLW_MakeContext`, `GLW_CheckOSVersion`, `GLW_StartDriverAndSetMode`, `GLW_LoadOpenGL`, and `GLW_StartOpenGL` helpers" in normalized_ownership_note


def test_renderer_advertisement_debug_labels_use_host_text() -> None:
	tr_world = _read("src/code/renderer/tr_world.c")
	block = _block_from_marker(tr_world, "static void R_DrawAdvertisementDebugText")

	for expected in (
		"#define R_DEBUG_ADVERTISEMENT_TEXT_X\t\t25",
		"#define R_DEBUG_ADVERTISEMENT_TEXT_Y\t\t256",
		"#define R_DEBUG_ADVERTISEMENT_TEXT_STEP\t16",
		"#define R_DEBUG_ADVERTISEMENT_TEXT_SCALE\t( 16.0f / 48.0f )",
		"RE_DrawScaledText( R_DEBUG_ADVERTISEMENT_TEXT_X, y, text,",
		"0, R_DEBUG_ADVERTISEMENT_TEXT_SCALE, 0, NULL, qtrue, color );",
	):
		assert expected in tr_world

	assert "DrawStretchPic" not in block
	assert "charSetShader" not in block


def test_renderer_mapping_round_37_keeps_ambient_and_directed_scaling_retail_parity() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt")
	hlil_part06 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt")
	ghidra = _read("references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c")
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_light = _read("src/code/renderer/tr_light.c")
	cvar_matrix = _read("docs/renderer_cvar_matrix.md")

	assert aliases["sub_44A810"] == "R_SetupEntityLightingGrid"
	assert (
		'data_1740d44("r_ambientScale", &data_52f68c, &data_551624, &data_52f690, 0x81800)'
		in hlil_part02
	)
	assert 'data_1743c14 = data_1740d40("r_directedScale", &data_551624, 0x200)' in hlil_part02
	assert '0052f67c  char const data_52f67c[0xf] = "r_ambientScale", 0' in hlil_part06
	assert "0052f68c                                      31 30 00 00" in hlil_part06
	assert "0052f690                                                  31 30 30 00" in hlil_part06
	assert '0052f474  char const data_52f474[0x10] = "r_directedScale", 0' in hlil_part06

	for offset in ("0xa4", "0xa8", "0xac"):
		assert f"*(float *)(param_1 + {offset}) = *(float *)(DAT_01740f88 + 0x2c)" in ghidra
	for offset in ("0xb4", "0xb8", "0xbc"):
		assert f"*(float *)(param_1 + {offset}) = *(float *)(DAT_01743c14 + 0x2c)" in ghidra

	assert 'r_ambientScale = ri.Cvar_GetBounded( "r_ambientScale", "10", "1", "100", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in tr_init
	assert 'r_directedScale = ri.Cvar_Get( "r_directedScale", "1", CVAR_CHEAT );' in tr_init
	assert "AssertCvarRange( r_ambientScale, 1, 100, qtrue );" in tr_init
	assert tr_light.index("VectorScale( ent->ambientLight, totalFactor, ent->ambientLight );") < tr_light.index("VectorScale( ent->ambientLight, r_ambientScale->value, ent->ambientLight );")
	assert tr_light.index("VectorScale( ent->directedLight, totalFactor, ent->directedLight );") < tr_light.index("VectorScale( ent->directedLight, r_directedScale->value, ent->directedLight );")
	assert tr_light.index("VectorScale( ent->ambientLight, r_ambientScale->value, ent->ambientLight );") < tr_light.index("VectorScale( ent->directedLight, r_directedScale->value, ent->directedLight );")
	assert tr_light.index("VectorScale( ent->directedLight, r_directedScale->value, ent->directedLight );") < tr_light.index("VectorNormalize2( direction, ent->lightDir );")
	assert "`r_ambientScale` | Bounded protected/VM-created/cloud `10`." in cvar_matrix
	assert "`r_directedScale` | Cheat `1`." in cvar_matrix


def test_renderer_mapping_round_278_promotes_tail_postprocess_and_command_symbols() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	functions_csv = _read("references/reverse-engineering/ghidra/quakelive_steam/functions.csv").lower()
	hlil_part01 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	tr_cmds = _read("src/code/renderer/tr_cmds.c")
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_font = _read("src/code/renderer/tr_font.c")

	expected_aliases = {
		"sub_4386D0": "RBPP_SetBloomUniforms",
		"sub_43C480": "R_IssueRenderCommands",
		"sub_43C540": "R_SyncRenderThread",
		"sub_43C570": "R_GetCommandBuffer",
		"sub_43CBE0": "RE_DrawScaledText",
		"sub_43CC50": "RE_MeasureScaledText",
		"sub_449F10": "R_PostProcessRestart",
		"sub_450710": "RBPP_RebuildState",
		"sub_450780": "RBPP_Shutdown",
		"sub_4507C0": "RB_PostProcessEnabled",
		"sub_451420": "R_SetPostProcessBloomParameters",
		"sub_451460": "R_ProjectPointToClipBounds",
	}

	for symbol, alias in expected_aliases.items():
		assert aliases[symbol] == alias

	for symbol in expected_aliases:
		if symbol == "sub_449F10":
			continue
		assert symbol.replace("sub_", "fun_00").lower() in functions_csv

	assert "004384d0    void* sub_4384d0()" in hlil_part01
	assert "004386d0    void* sub_4386d0(float arg1, float arg2, float arg3, float arg4, float arg5)" in hlil_part01
	assert "data_16e3bd0(data_585fcc, fconvert.s(fconvert.t(arg1)))" in hlil_part01
	assert "data_16e3bd0(data_5860c8, fconvert.s(fconvert.t(arg2)))" in hlil_part01
	assert "data_16e3bd0(data_5860d0, fconvert.s(fconvert.t(arg3)))" in hlil_part01
	assert "data_16e3bd0(data_5860cc, fconvert.s(fconvert.t(arg4)))" in hlil_part01
	assert "data_16e3bd0(data_5860d4, fconvert.s(fconvert.t(arg5)))" in hlil_part01

	for expected in (
		"0043c480    enum wait_event sub_43c480(int32_t arg1)",
		"0043c540    void sub_43c540()",
		"0043c570    void* sub_43c570(int32_t arg1)",
		"r_getcommandbuffer: bad size %i",
		"00449f10  sub_43c540()",
		"00449f15  sub_450780()",
		"00449f1a  sub_450710()",
		"data_5878c8 = sub_449f10",
		"data_5878cc = sub_451420",
		"data_5878d0 = sub_451460",
		"data_5878d8 = sub_43cbe0",
		"data_5878dc = sub_43cc50",
		"00450710    void* sub_450710()",
		"gl_arb_multitexture is either no",
		"00450780    int32_t sub_450780()",
		"004507c0    int32_t sub_4507c0()",
		"0045145b  return sub_4386d0",
		"0045147a  sub_44b660(arg1, &data_17175cc, &data_171758c, arg2, arg3)",
	):
		assert expected in hlil_part02

	assert "void R_IssueRenderCommands( qboolean runPerformanceCounters ) {" in tr_cmds
	assert "void R_SyncRenderThread( void ) {" in tr_cmds
	assert "void *R_GetCommandBuffer( int bytes ) {" in tr_cmds
	assert "static qboolean RB_PostProcessEnabled( void ) {" in tr_backend
	assert "static void RBPP_SetBloomUniforms( float brightThreshold, float bloomSaturation, float bloomIntensity, float sceneSaturation, float sceneIntensity ) {" in tr_backend
	assert "static void RBPP_RebuildState( void ) {" in tr_backend
	assert "static void RBPP_Shutdown( void ) {" in tr_backend
	assert "void R_SetPostProcessBloomParameters( float brightThreshold, float bloomSaturation, float bloomIntensity, float sceneSaturation, float sceneIntensity ) {" in tr_backend
	assert "static void R_PostProcessRestart( void ) {" in tr_init
	assert "re.RetailBloomPostProcessCommand = R_AddBloomPostProcessCommand;" in tr_init
	assert "re.RetailPostProcessPass = R_SetPostProcessBloomParameters;" in tr_init
	assert "void RE_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor, const float *baseColor ) {" in tr_font
	assert "void RE_MeasureScaledText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outWidth, float *outHeight, float *outLeft ) {" in tr_font


def test_renderer_mapping_round_279_promotes_postprocess_program_and_command_symbols() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	functions_csv = _read("references/reverse-engineering/ghidra/quakelive_steam/functions.csv").lower()
	hlil_part01 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	tr_backend = _read("src/code/renderer/tr_backend.c")
	bloom_enabled_block = _block_from_marker(tr_backend, "static qboolean RBPP_BloomEnabled( void ) {")

	expected_aliases = {
		"sub_437A50": "RB_ExecuteRenderCommands",
		"sub_437DA0": "RBPP_ShutdownBloomResources",
		"sub_4384A0": "RBPP_BloomEnabled",
		"sub_4384D0": "R_AddBloomPostProcessCommand",
		"sub_438590": "RBPP_SetBloomUniformsFromCvars",
		"sub_43CCD0": "RBPP_DestroyColorCorrectProgram",
		"sub_43CCE0": "RBPP_ColorCorrectEnabled",
		"sub_43CD10": "R_AddColorCorrectPostProcessCommand",
		"sub_43CD60": "RBPP_SetColorCorrectUniformsFromCvars",
		"sub_43CE50": "RBPP_CreateColorCorrectTexture",
		"sub_43CFE0": "RBPP_InitColorCorrectResources",
		"sub_450640": "RBPP_LoadProgram",
		"sub_4506A0": "RBPP_DestroyProgram",
	}

	for symbol, alias in expected_aliases.items():
		assert aliases[symbol] == alias

	for symbol in expected_aliases:
		if symbol == "sub_4384D0":
			continue
		assert symbol.replace("sub_", "fun_00").lower() in functions_csv

	for expected in (
		"00437a50    int32_t sub_437a50(int32_t* arg1)",
		"sub_436dc0(esi)",
		"sub_436ec0(esi)",
		"if (sub_4384a0() != 0)",
		"00437da0    int32_t sub_437da0()",
		"sub_4506a0(i)",
		"r_bloomactive",
		"004384a0    int32_t sub_4384a0()",
		"004384d0    void* sub_4384d0()",
		"*result = 0xa",
		"00438590    void sub_438590()",
		"data_16e3bd0(data_585fcc",
		"data_16e3bd0(data_5860c8",
		"data_16e3bd0(data_5860d0",
		"data_16e3bd0(data_5860cc",
		"data_16e3bd0(data_5860d4",
	):
		assert expected in hlil_part01

	for expected in (
		"0043ccd0    int32_t sub_43ccd0()",
		"0043ccdb  return sub_4506a0(&data_586210)",
		"0043cce0    int32_t sub_43cce0()",
		"0043cd10    void* sub_43cd10()",
		"*result = 9",
		"0043cd60    void sub_43cd60()",
		"data_16e3bd0(data_586224",
		"data_16e3bd0(data_586228",
		"data_16e3bd0(data_58622c",
		"0043ce50    int32_t __fastcall sub_43ce50(int32_t arg1)",
		"color correct failure - unable t",
		"0043cfe0    void sub_43cfe0()",
		"sub_450640(\"colorcorrect\", \"scripts/colorcorrect.fs\", \"scripts/posteffect.vs\")",
		"00450640    int32_t sub_450640(int32_t* arg1, int32_t arg2, int32_t* arg3)",
		"004506a0    void sub_4506a0(void* arg1)",
		"data_16e3ac4(ecx, eax_1)",
		"data_16e3dc0(*(arg1 + 0x10))",
	):
		assert expected in hlil_part02

	assert "void RB_ExecuteRenderCommands( const void *data ) {" in tr_backend
	assert "static void RBPP_DestroyProgram( ppProgram_t *program ) {" in tr_backend
	assert "static qboolean RBPP_LoadProgram( ppProgram_t *program, const char *name, const char *fragmentPath, const char *vertexPath ) {" in tr_backend
	assert "if ( !RB_PostProcessEnabled() ) {" in bloom_enabled_block
	assert "if ( !s_postProcess.supported ) {" in bloom_enabled_block
	assert "if ( !r_bloomActive || !r_bloomActive->integer ) {" in bloom_enabled_block
	assert "static void RBPP_ShutdownBloomResources( void ) {" in tr_backend
	assert "static void RBPP_DestroyColorCorrectProgram( void ) {" in tr_backend
	assert "static qboolean RBPP_CreateColorCorrectTexture( void ) {" in tr_backend
	assert "static qboolean RBPP_InitColorCorrectResources( void ) {" in tr_backend
	assert "static qboolean RBPP_ApplyBloom( const bloomPostProcessCommand_t *cmd ) {" in tr_backend
	assert "void RBPP_SetColorCorrectUniformsFromCvars( void ) {" in tr_backend
	assert "if ( !RBPP_ColorCorrectEnabled() ) {" in _block_from_marker(tr_backend, "void RBPP_SetColorCorrectUniformsFromCvars( void ) {")
	assert "static void RBPP_ApplyColorCorrectPass( const colorCorrectPostProcessCommand_t *cmd ) {" in tr_backend
	assert "RBPP_SetColorCorrectUniforms( qfalse );" in _block_from_marker(tr_backend, "static qboolean RBPP_InitColorCorrectResources( void ) {")
	assert "RBPP_SetColorCorrectUniformsFromCvars();" in _block_from_marker(tr_backend, "static void RBPP_ApplyColorCorrectPass( const colorCorrectPostProcessCommand_t *cmd ) {")
	assert "s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.brightPassProgram.brightThresholdUniform, brightThreshold );" in tr_backend
	assert "s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.colorCorrectProgram.gammaRecipUniform, gammaRecip );" in tr_backend


def test_renderer_mapping_round_281_promotes_backend_command_handlers_and_scene_target_wiring() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	functions_csv = _read("references/reverse-engineering/ghidra/quakelive_steam/functions.csv").lower()
	hlil_part01 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	tr_backend = _read("src/code/renderer/tr_backend.c")

	expected_aliases = {
		"sub_436280": "RB_SetGL2D",
		"sub_4367F0": "RB_SetColor",
		"sub_436DC0": "RB_ColorCorrectPostProcessCommand",
		"sub_436EC0": "RB_BloomPostProcessCommand",
		"sub_437450": "RB_DrawSurfs",
		"sub_437920": "RB_SetViewportAndScissorCommand",
		"sub_4379B0": "RB_DrawFontStashTextCommand",
		"sub_437BC0": "RB_RenderThread",
		"sub_438790": "RBPP_BindSceneRenderTarget",
		"sub_4387B0": "RBPP_BindBloomRenderTargetByIndex",
		"sub_4387D0": "RBPP_ReleaseSceneRenderTarget",
		"sub_4387E0": "RBPP_GetBloomMode",
		"sub_43CBA0": "R_AddBindSceneRenderTargetCommand",
	}

	for symbol, alias in expected_aliases.items():
		assert aliases[symbol] == alias

	for symbol in expected_aliases:
		if symbol == "sub_43CBA0":
			continue
		assert symbol.replace("sub_", "fun_00").lower() in functions_csv

	for expected in (
		"00436280    int32_t sub_436280()",
		"data_16e3f8c(0, 0, ecx, eax_1)",
		"004367f0    void* sub_4367f0",
		"data_1745f2c = (int.d(x87_r7_1)).b",
		"00436dc0    void* sub_436dc0(void* arg1)",
		"data_16e40d4(0x84f5",
		"00437450    void* sub_437450(void* arg1)",
		"__builtin_memcpy(dest: 0x1745a84",
		"sub_435ff0(*(arg1 + 0x3cc), *(arg1 + 0x3d0))",
		"00437920    void* sub_437920(void* arg1)",
		"data_1746004 = 1",
		"data_16e3e8c(*(arg1 + 4), *(arg1 + 8), *(arg1 + 0xc), *(arg1 + 0x10))",
		"004379b0    void* sub_4379b0(void* arg1)",
		"sub_444360(data_586238",
		"00437bc0    int32_t* sub_437bc0()",
		"result = sub_46bb60()",
		"00438790    int32_t sub_438790()",
		"return data_16e403c(0x8d40, result)",
		"004387b0    int32_t sub_4387b0(int32_t arg1)",
		"return data_16e403c(0x8d40, (&data_585f98)[arg1])",
		"004387d0    int32_t sub_4387d0()",
		"return data_16e403c(0x8d40, 0)",
		"004387e0    int32_t sub_4387e0()",
		"return data_55c308",
	):
		assert expected in hlil_part01

	for expected in (
		"0043cba0    int32_t* sub_43cba0()",
		"*result = 0xb",
		"data_5878c0 = j_sub_43cba0",
		"data_5878e0 = sub_43c750",
	):
		assert expected in hlil_part02

	assert "void\tRB_SetGL2D (void) {" in tr_backend
	assert "const void\t*RB_SetColor( const void *data ) {" in tr_backend
	assert "const void\t*RB_DrawSurfs( const void *data ) {" in tr_backend
	assert "void RB_RenderThread( void ) {" in tr_backend
	assert "static const void *RB_ColorCorrectPostProcessCommand( const void *data ) {" in tr_backend
	assert "static const void *RB_BloomPostProcessCommand( const void *data ) {" in tr_backend
	assert "static void RBPP_BindSceneRenderTarget( void ) {" in tr_backend
	assert "if ( !RBPP_BloomEnabled() || !s_postProcess.sceneTarget.initialized ) {" in _block_from_marker(tr_backend, "static void RBPP_BindSceneRenderTarget( void ) {")
	assert "static void RBPP_ReleaseSceneRenderTarget( void ) {" in tr_backend
	assert "static int RBPP_GetBloomMode( void ) {" in tr_backend
	assert "static void RBPP_ApplyColorCorrectPass( const colorCorrectPostProcessCommand_t *cmd ) {" in tr_backend
	assert "static void SetViewportAndScissor( void ) {" in tr_backend


def test_renderer_screenshot_readback_matches_retail_command_wiring() -> None:
	hlil_part01 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_local = _read("src/code/renderer/tr_local.h")
	tr_shader = _read("src/code/renderer/tr_shader.c")

	assert "00437b18              eax_3, ecx, edx = sub_4483b0(esi)" in hlil_part01
	assert "00448215  if (sub_4384a0() != 0)" in hlil_part02
	assert "00448217      sub_4387d0()" in hlil_part02
	assert "00448237  data_16e3d74(arg1, arg2, arg3, arg4, 0x1907, 0x1401, &eax_3[0x12])" in hlil_part02
	assert "00448244  if (sub_4384a0() != 0)" in hlil_part02
	assert "00448246      sub_438790()" in hlil_part02
	assert "00448308  if (sub_4384a0() != 0)" in hlil_part02
	assert "0044832a  data_16e3d74(arg1, arg2, arg3, arg4, 0x1908, 0x1401, eax_4)" in hlil_part02
	assert "00448978      *eax_14 = 6" in hlil_part02
	assert "00448b58      *eax_14 = 6" in hlil_part02

	command_enum = tr_local[tr_local.index("typedef enum {"):tr_local.index("} renderCommand_t;")]
	for earlier, later in (
		("RC_DRAW_BUFFER", "RC_SWAP_BUFFERS"),
		("RC_SWAP_BUFFERS", "RC_SCREENSHOT"),
		("RC_SCREENSHOT", "RC_ADVERTISEMENT_QUERIES"),
	):
		assert command_enum.index(earlier) < command_enum.index(later)

	for marker in (
		"void RB_TakeScreenshot(",
		"void RB_TakeScreenshotJPEG(",
	):
		block = _block_from_marker(tr_init, marker)
		assert "qglReadBuffer" not in block
		assert block.index("RB_BeginScreenshotReadback();") < block.index("qglReadPixels")
		assert block.index("qglReadPixels") < block.index("RB_EndScreenshotReadback();")

	levelshot_block = _block_from_marker(tr_init, "void R_LevelShot( void )")
	assert "qglReadBuffer" not in levelshot_block

	begin_block = _block_from_marker(tr_backend, "void RB_BeginScreenshotReadback( void )")
	end_block = _block_from_marker(tr_backend, "void RB_EndScreenshotReadback( void )")
	assert "if ( !RBPP_BloomEnabled() || !s_postProcess.sceneTarget.initialized ) {" in begin_block
	assert "RBPP_ReleaseSceneRenderTarget();" in begin_block
	assert "if ( !RBPP_BloomEnabled() || !s_postProcess.sceneTarget.initialized ) {" in end_block
	assert "RBPP_BindSceneRenderTarget();" in end_block
	assert "case RC_SCREENSHOT:" in tr_backend
	assert "data = RB_TakeScreenshotCmd( data );" in tr_backend
	assert "case RC_SCREENSHOT:" in tr_shader
	assert "const screenshotCommand_t *ss_cmd = (const screenshotCommand_t *)curCmd;" in tr_shader


def test_renderer_mapping_round_282_promotes_command_buffer_and_glimp_thread_wiring() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	functions_csv = _read("references/reverse-engineering/ghidra/quakelive_steam/functions.csv").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	tr_cmds = _read("src/code/renderer/tr_cmds.c")
	win_glimp = _read("src/code/win32/win_glimp.c")

	expected_aliases = {
		"sub_43C400": "R_InitCommandBuffers",
		"sub_43C460": "R_ShutdownCommandBuffers",
		"sub_43C5D0": "R_AddDrawSurfCmd",
		"sub_46B840": "GLimp_EndFrame",
		"sub_46B8F0": "GLimp_Shutdown",
		"sub_46BAA0": "GLimp_LogComment",
		"sub_46BAD0": "GLimp_RenderThreadWrapper",
		"sub_46BAF0": "GLimp_SpawnRenderThread",
		"sub_46BB60": "GLimp_RendererSleep",
		"sub_46BBF0": "GLimp_FrontEndSleep",
		"sub_46BC20": "GLimp_WakeRenderer",
	}

	for symbol, alias in expected_aliases.items():
		assert aliases[symbol] == alias

	for symbol in expected_aliases:
		if symbol == "sub_46BAD0":
			continue
		assert symbol.replace("sub_", "fun_00").lower() in functions_csv

	for expected in (
		"0043c400    void* sub_43c400()",
		"trying smp acceleration",
		"sub_46baf0(sub_437bc0)",
		"0043c460    void sub_43c460()",
		"sub_46bc20(0)",
		"0043c5d0    void* sub_43c5d0(int32_t arg1, int32_t arg2)",
		"*result = 3",
		"__builtin_memcpy(dest: result + 4",
		"__builtin_memcpy(dest: result + 0x19c",
		"0046b840    int32_t sub_46b840()",
		"glimp_endframe() - swapbuffers",
		"0046b8f0    void sub_46b8f0()",
		"shutting down opengl subsystem",
		"0046baa0    int32_t sub_46baa0(int32_t arg1)",
		"return fprintf(result, &data_52d0f4, arg1)",
		"0046bad0    int32_t sub_46bad0()",
		"0046baf0    int32_t sub_46baf0(int32_t arg1)",
		"createeventa(lpeventattributes: nullptr",
		"createthread(lpthreadattributes: nullptr",
		"0046bb60    int32_t sub_46bb60()",
		"setevent(hevent: data_16e4134)",
		"waitforsingleobject(hhandle: data_16e40e8",
		"0046bbf0    int32_t sub_46bbf0()",
		"waitforsingleobject(hhandle: data_16e4134",
		"0046bc20    enum wait_event sub_46bc20(int32_t arg1)",
		"data_e411d0 = arg1",
		"setevent(hevent: data_16e40e8)",
	):
		assert expected in hlil_part02

	assert "void R_InitCommandBuffers( void ) {" in tr_cmds
	assert "void R_ShutdownCommandBuffers( void ) {" in tr_cmds
	assert "void\tR_AddDrawSurfCmd( drawSurf_t *drawSurfs, int numDrawSurfs ) {" in tr_cmds
	assert "cmd->commandId = RC_DRAW_SURFS;" in tr_cmds
	assert "cmd->refdef = tr.refdef;" in tr_cmds
	assert "cmd->viewParms = tr.viewParms;" in tr_cmds
	assert "void GLimp_EndFrame (void)" in win_glimp
	assert "void GLimp_Shutdown( void )" in win_glimp
	assert "void GLimp_LogComment( char *comment )" in win_glimp
	assert "void GLimp_RenderThreadWrapper( void ) {" in win_glimp
	assert "qboolean GLimp_SpawnRenderThread( void (*function)( void ) ) {" in win_glimp
	assert "void *GLimp_RendererSleep( void ) {" in win_glimp
	assert "void GLimp_FrontEndSleep( void ) {" in win_glimp
	assert "void GLimp_WakeRenderer( void *data ) {" in win_glimp


def test_renderer_mapping_round_284_promotes_patch_curve_grid_helpers() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	functions_csv = _read("references/reverse-engineering/ghidra/quakelive_steam/functions.csv").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_284.md")
	tr_curve = _read("src/code/renderer/tr_curve.c")
	tr_local = _read("src/code/renderer/tr_local.h")
	tr_bsp = _read("src/code/renderer/tr_bsp.c")

	expected_aliases = {
		"sub_43D160": "LerpDrawVert",
		"sub_43D200": "Transpose",
		"sub_43DB20": "InvertCtrl",
		"sub_43DBB0": "InvertErrorTable",
		"sub_43DCB0": "PutPointsOnCurve",
		"sub_43DE30": "R_CreateSurfaceGridMesh",
		"sub_43E000": "R_FreeSurfaceGridMesh",
	}

	for symbol, alias in expected_aliases.items():
		assert aliases[symbol] == alias
		assert symbol.replace("sub_", "fun_00").lower() in functions_csv
		assert f"| `{symbol}` | `{alias}` | High |" in mapping_round

	for expected in (
		"0043d160    void __convention(\"regparm\") sub_43d160",
		"0043d1bf  arg1[0xa].b = ((zx.d(arg4[0xa].b) + zx.d(arg3[0xa].b)) s>> 1).b",
		"0043d200    int32_t sub_43d200(int32_t arg1, int32_t arg2, int32_t arg3)",
		"__builtin_memcpy(dest: &var_38, src: eax_5, n: 0x2c)",
		"0043db20    void __convention(\"regparm\") sub_43db20",
		"__builtin_memcpy(dest: edx_1, src: ebx_1, n: 0x2c)",
		"0043dbb0    float* __convention(\"regparm\") sub_43dbb0",
		"0043dcb0    int32_t sub_43dcb0(float* arg1, int32_t arg2, int32_t arg3)",
		"0043dd07                  edx = sub_43d160(edi_2,",
		"0043de30    int32_t* sub_43de30(float arg1, float arg2, float arg3, float arg4)",
		"data_1740d38(i_2 i* arg2 * 0x2c + 0x5c)",
		"*result = 3",
		"0043e000    int32_t sub_43e000(void* arg1)",
		"data_1740d3c(*(arg1 + 0x54))",
		"0043e030    long double sub_43e030",
		"0043e5dc      sub_43d200(i_8, var_2d858, &var_2d854)",
		"0043e623  sub_43dcb0(&var_2d854, i_8, ebx_5)",
		"0043e801      sub_43dbb0(eax_30, edx_14, i_8, i_16)",
		"0043e81f      sub_43db20(&var_2d854, i_8, i_14)",
		"0043e84c  sub_43de30(i_8, i_16, var_1c_5, var_18_5)",
		"0043e913                          edx_1 = sub_43d160(eax_2, edx_1, &esi_1[0xb], esi_1)",
		"0043eb25      result = sub_43de30(ebx_2, i_2, &var_2d83c, &var_210)",
		"0043ec25                      edx = sub_43d160(eax_5, edx, ebx_3, esi_3)",
		"0043ede5  int32_t* result = sub_43de30(i_3, edi_1, &var_2d83c, &var_210)",
	):
		assert expected in hlil_part02

	assert "# Quake Live Steam Host Mapping Round 284" in mapping_round
	assert "renderer patch/curve helper symbol coverage: before 82%, after 96%" in mapping_round.lower()
	assert "static void LerpDrawVert( drawVert_t *a, drawVert_t *b, drawVert_t *out ) {" in tr_curve
	assert "static void Transpose( int width, int height, drawVert_t ctrl[MAX_GRID_SIZE][MAX_GRID_SIZE] ) {" in tr_curve
	assert "static void InvertCtrl( int width, int height, drawVert_t ctrl[MAX_GRID_SIZE][MAX_GRID_SIZE] ) {" in tr_curve
	assert "static void InvertErrorTable( float errorTable[2][MAX_GRID_SIZE], int width, int height ) {" in tr_curve
	assert "static void PutPointsOnCurve( drawVert_t\tctrl[MAX_GRID_SIZE][MAX_GRID_SIZE]," in tr_curve
	assert "srfGridMesh_t *R_CreateSurfaceGridMesh(int width, int height," in tr_curve
	assert "void R_FreeSurfaceGridMesh( srfGridMesh_t *grid ) {" in tr_curve
	assert "return R_CreateSurfaceGridMesh( width, height, ctrl, errorTable );" in tr_curve
	assert "R_FreeSurfaceGridMesh(grid);" in tr_curve
	assert "grid = R_CreateSurfaceGridMesh( width, height, ctrl, errorTable );" in tr_curve
	assert "srfGridMesh_t *R_SubdividePatchToGrid( int width, int height," in tr_local
	assert "void R_FreeSurfaceGridMesh( srfGridMesh_t *grid );" in tr_local
	assert "R_FreeSurfaceGridMesh( grid );" in tr_bsp


def test_renderer_bsp_loader_tracks_quakelive_advertisement_brush_models() -> None:
	tr_bsp = _read("src/code/renderer/tr_bsp.c")
	tr_local = _read("src/code/renderer/tr_local.h")
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_main = _read("src/code/renderer/tr_main.c")
	tr_world = _read("src/code/renderer/tr_world.c")

	assert "#define\tLUMP_ADVERTISEMENTS_QL\t17" in tr_bsp
	assert "static void R_LoadAdvertisements( lump_t *l ) {" in tr_bsp
	assert '"R_LoadAdvertisements: funny lump size\\n"' in tr_bsp
	assert '"R_LoadAdvertisements: number of advertisements exceeds level limit.\\n"' in tr_bsp
	assert '"cell ID %d has no brush model. It has been ignored.\\n"' in tr_bsp
	assert '"cell ID %d has multiple surfaces. It has been ignored.\\n"' in tr_bsp
	assert "R_LoadAdvertisements( &qlAdvertisementsLump );" in tr_bsp
	assert "int\t\t\tnumAdvertisements;" in tr_local
	assert "qlAdvertisement_t\t*advertisements;" in tr_local
	assert "int\t\t\tbmodelHandleBase;" in tr_local
	assert "int\t\t\tnumBmodels;" in tr_local
	assert "bmodel_t\t*bmodel;" in tr_local
	assert "vec3_t\t\tnormal;" in tr_local
	assert "vec3_t\t\tpoints[4];" in tr_local
	assert "int\t\t\tsourceIndex;" in tr_local
	assert "void\t\tR_AdvertisementList_f( void );" in tr_local
	assert "static int R_AddAdvertisementSurface( qlAdvertisement_t *advertisement ) {" in tr_world
	assert "void R_AdvertisementList_f( void ) {" in tr_world
	assert 'ri.Printf( PRINT_ALL, "advertlist: world=%s loaded=%d\\n",' in tr_world
	assert '"advertlist: [%d] cellId=%d sourceIndex=%d model=*%d surfaces=%d shader=%s center=(%.1f %.1f %.1f) normal=(%.3f %.3f %.3f)\\n"' in tr_world
	assert '"advertlist:      points=(%.1f %.1f %.1f) (%.1f %.1f %.1f) (%.1f %.1f %.1f) (%.1f %.1f %.1f)\\n"' in tr_world
	assert "static int R_CullAdvertisementQuad( const vec3_t points[4] ) {" in tr_world
	assert "s_worldData.bmodelHandleBase = tr.numModels;" in tr_bsp
	assert "s_worldData.numBmodels = count;" in tr_bsp
	assert "model = R_GetModelByHandle( s_worldData.bmodelHandleBase + modelNum );" in tr_bsp
	assert "bmodel = model ? model->bmodel : NULL;" in tr_bsp
	assert "out[s_worldData.numAdvertisements].bmodel = bmodel;" in tr_bsp
	assert "out[s_worldData.numAdvertisements].sourceIndex = i;" in tr_bsp
	assert "for ( j = 0 ; j < 4 ; j++ ) {" in tr_bsp
	assert "tr.currentEntity = &tr.worldEntity;" in tr_world
	assert "VectorSubtract( tr.refdef.vieworg, advertisement->center, viewDelta );" in tr_world
	assert "if ( DotProduct( advertisement->normal, viewDelta ) <= 0.0f ) {" in tr_world
	assert "cull = R_CullAdvertisementQuad( advertisement->points );" in tr_world
	assert "if ( cull == CULL_OUT ) {" in tr_world
	assert "R_AddDrawSurf( surface->data, surface->shader, surface->fogIndex, qfalse );" in tr_world
	assert "R_UpdateAdvertisements();" in tr_main
	assert 'ri.Cmd_AddCommand( "advertlist", R_AdvertisementList_f );' in tr_init
	assert 'ri.Cmd_RemoveCommand( "advertlist" );' in tr_init


def test_renderer_model_surface_limits_match_retail_quakelive_loader_caps() -> None:
	qcommon_qfiles = _read("src/code/qcommon/qfiles.h")
	bspc_q3files = _read("src/code/bspc/q3files.h")
	tr_model = _read("src/code/renderer/tr_model.c")

	assert "#define\tSHADER_MAX_VERTEXES\t2000" in qcommon_qfiles
	assert "#define\tSHADER_MAX_INDEXES\t(6*SHADER_MAX_VERTEXES)" in qcommon_qfiles
	assert "#define\tSHADER_MAX_VERTEXES\t2000" in bspc_q3files
	assert "#define\tSHADER_MAX_INDEXES\t(6*SHADER_MAX_VERTEXES)" in bspc_q3files
	assert 'ri.Error (ERR_DROP, "R_LoadMD3: %s has more than %i verts on a surface (%i)",' in tr_model
	assert 'ri.Error (ERR_DROP, "R_LoadMD3: %s has more than %i triangles on a surface (%i)",' in tr_model
