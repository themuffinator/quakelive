import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _normalize_whitespace(text: str) -> str:
	return " ".join(text.split())


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
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_bsp = _read("src/code/renderer/tr_bsp.c")
	tr_curve = _read("src/code/renderer/tr_curve.c")
	tr_flares = _read("src/code/renderer/tr_flares.c")
	win_glimp = _read("src/code/win32/win_glimp.c")

	assert "void RB_ExecuteRenderCommands( const void *data ) {" in tr_backend
	assert "static void RBPP_RebuildState( void ) {" in tr_backend
	assert "void GL_Bind( image_t *image ) {" in tr_backend
	assert "static\tvoid R_LoadSurfaces( lump_t *surfs, lump_t *verts, lump_t *indexLump ) {" in tr_bsp
	assert "int R_StitchPatches( int grid1num, int grid2num ) {" in tr_bsp
	assert "static void LerpDrawVert( drawVert_t *a, drawVert_t *b, drawVert_t *out ) {" in tr_curve
	assert "void R_FreeSurfaceGridMesh( srfGridMesh_t *grid ) {" in tr_curve
	assert "void RB_RenderFlares (void) {" in tr_flares
	assert "void RB_TestFlare( flare_t *f ) {" in tr_flares
	assert "static void GLW_StartOpenGL( void )" in win_glimp
	assert "void GLimp_Init( void )" in win_glimp


def test_renderer_mapping_round_278_promotes_tail_postprocess_and_command_symbols() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam"]
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
	assert "static void RBPP_RebuildState( void ) {" in tr_backend
	assert "static void RBPP_Shutdown( void ) {" in tr_backend
	assert "static void R_PostProcessRestart( void ) {" in tr_init
	assert "void RE_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor, const float *baseColor ) {" in tr_font
	assert "void RE_MeasureScaledText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outWidth, float *outHeight, float *outLeft ) {" in tr_font


def test_renderer_mapping_round_279_promotes_postprocess_program_and_command_symbols() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam"]
	functions_csv = _read("references/reverse-engineering/ghidra/quakelive_steam/functions.csv").lower()
	hlil_part01 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	tr_backend = _read("src/code/renderer/tr_backend.c")

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
	assert "static void RBPP_ShutdownBloomResources( void ) {" in tr_backend
	assert "static void RBPP_DestroyColorCorrectProgram( void ) {" in tr_backend
	assert "static qboolean RBPP_CreateColorCorrectTexture( void ) {" in tr_backend
	assert "static qboolean RBPP_InitColorCorrectResources( void ) {" in tr_backend
	assert "static qboolean RBPP_ApplyBloom( void ) {" in tr_backend
	assert "static void RBPP_ApplyColorCorrectPass( void ) {" in tr_backend
	assert "s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.brightPassProgram.brightThresholdUniform, brightThreshold );" in tr_backend
	assert "s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.colorCorrectProgram.gammaRecipUniform, gammaRecip );" in tr_backend


def test_renderer_mapping_round_281_promotes_backend_command_handlers_and_scene_target_wiring() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam"]
	functions_csv = _read("references/reverse-engineering/ghidra/quakelive_steam/functions.csv").lower()
	hlil_part01 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt").lower()
	hlil_part02 = _read("references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt").lower()
	tr_backend = _read("src/code/renderer/tr_backend.c")

	expected_aliases = {
		"sub_436280": "RB_SetGL2D",
		"sub_4367F0": "RB_SetColor",
		"sub_436DC0": "RBPP_ApplyColorCorrectPass",
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
	assert "static void RBPP_BindSceneRenderTarget( void ) {" in tr_backend
	assert "static void RBPP_ReleaseSceneRenderTarget( void ) {" in tr_backend
	assert "static int RBPP_GetBloomMode( void ) {" in tr_backend
	assert "static void RBPP_ApplyColorCorrectPass( void ) {" in tr_backend
	assert "static void SetViewportAndScissor( void ) {" in tr_backend


def test_renderer_mapping_round_282_promotes_command_buffer_and_glimp_thread_wiring() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam"]
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
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam"]
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
