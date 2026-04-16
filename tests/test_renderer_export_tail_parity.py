from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_refexport_tail_restores_retail_loading_view_slot() -> None:
	tr_public = _read("src/code/renderer/tr_public.h")

	assert tr_public.index("(*RenderScene)") < tr_public.index("(*AdvertisementBridge_UpdateLoadingViewParameters)") < tr_public.index("(*SetColor)")
	assert tr_public.index("(*DrawStretchRaw)") < tr_public.index("(*BeginFrame)")
	assert "(*RegisterFont)" not in tr_public


def test_getrefapi_assigns_retail_tail_without_font_export() -> None:
	tr_init = _read("src/code/renderer/tr_init.c")
	expected_tail = (
		"re.RenderScene = RE_RenderScene;",
		"re.AdvertisementBridge_UpdateLoadingViewParameters = AdvertisementBridge_UpdateLoadingViewParameters;",
		"re.SetColor = RE_SetColor;",
		"re.DrawStretchPic = RE_StretchPic;",
		"re.DrawStretchRaw = RE_StretchRaw;",
		"re.UploadCinematic = RE_UploadCinematic;",
		"re.BeginFrame = RE_BeginFrame;",
		"re.EndFrame = RE_EndFrame;",
		"re.MarkFragments = R_MarkFragments;",
		"re.LerpTag = R_LerpTag;",
		"re.ModelBounds = R_ModelBounds;",
		"re.RemapShader = R_RemapShader;",
		"re.GetEntityToken = R_GetEntityToken;",
		"re.inPVS = R_inPVS;",
	)

	positions = [tr_init.index(entry) for entry in expected_tail]
	assert positions == sorted(positions)
	assert "re.RegisterFont = RE_RegisterFont;" not in tr_init


def test_client_font_registration_uses_compatibility_lane() -> None:
	client_h = _read("src/code/client/client.h")
	cl_main = _read("src/code/client/cl_main.c")
	cl_ui = _read("src/code/client/cl_ui.c")
	cl_cgame = _read("src/code/client/cl_cgame.c")
	ql_ui_imports = _read("src/code/client/ql_ui_imports.inc")
	ql_cgame_imports = _read("src/code/client/ql_cgame_imports.inc")

	assert "void CL_RegisterFont( const char *fontName, int pointSize, fontInfo_t *font );" in client_h
	assert "void CL_RegisterFont( const char *fontName, int pointSize, fontInfo_t *font ) {" in cl_main
	assert "RE_RegisterFont( fontName, pointSize, font );" in cl_main

	assert "CL_RegisterFont( VMA(1), args[2], VMA(3) );" in cl_ui
	assert "CL_RegisterFont( VMA(1), args[2], VMA(3) );" in cl_cgame
	assert "RE_DrawScaledText( x, y, text, fontHandle, scale, maxX, outMaxX," in cl_ui
	assert "RE_MeasureScaledText( text, end, fontHandle, scale, maxX, &width, &height, outLeft );" in cl_ui
	assert "RE_DrawScaledText( x, y, text, fontHandle, scale, maxX, outMaxX," in cl_cgame
	assert "RE_MeasureScaledText( text, end, fontHandle, scale, maxX, &width, &height, outLeft );" in cl_cgame
	assert "re.RegisterFont(" not in cl_ui
	assert "re.RegisterFont(" not in cl_cgame

	assert "ql_ui_imports[UI_QL_IMPORT_R_REGISTERFONT] = (ql_import_f)QL_UI_trap_R_RegisterFont;" in cl_ui
	assert "ql_cgame_imports[CG_QL_IMPORT_R_REGISTERFONT] = (ql_import_f)QL_CG_trap_R_RegisterFont;" in cl_cgame
	assert "UI_Import_Syscall( UI_R_REGISTERFONT, fontName, pointSize, font );" in ql_ui_imports
	assert "CG_Import_Syscall(CG_R_REGISTERFONT, fontName, pointSize, font );" in ql_cgame_imports


def test_loading_view_bridge_routes_through_renderer_export_slot() -> None:
	cl_cgame = _read("src/code/client/cl_cgame.c")
	tr_scene = _read("src/code/renderer/tr_scene.c")

	assert "void CL_AdvertisementBridge_RefreshLoadingViewParameters( void ) {" in cl_cgame
	assert "re.AdvertisementBridge_UpdateLoadingViewParameters();" in cl_cgame
	assert "CL_AdvertisementBridge_RefreshLoadingViewParameters();" in cl_cgame

	assert "void AdvertisementBridge_UpdateLoadingViewParameters( void ) {" in tr_scene
	assert "CL_AdvertisementBridge_RefreshLoadingViewParameters();" in tr_scene


def test_render_scene_preserves_retail_viewport_flip_handoff() -> None:
	tr_scene = _read("src/code/renderer/tr_scene.c")

	for expected in (
		"parms.viewportX = tr.refdef.x;",
		"parms.viewportY = glConfig.vidHeight - ( tr.refdef.y + tr.refdef.height );",
		"parms.viewportWidth = tr.refdef.width;",
		"parms.viewportHeight = tr.refdef.height;",
		"parms.fovX = tr.refdef.fov_x;",
		"parms.fovY = tr.refdef.fov_y;",
	):
		assert expected in tr_scene


def test_render_view_rejects_zero_sized_viewports_before_incrementing_counts() -> None:
	tr_main = _read("src/code/renderer/tr_main.c")

	assert "if ( parms->viewportWidth <= 0 || parms->viewportHeight <= 0 ) {" in tr_main
	assert "tr.viewCount++;" in tr_main
	assert tr_main.index("if ( parms->viewportWidth <= 0 || parms->viewportHeight <= 0 ) {") < tr_main.index("tr.viewCount++;")
