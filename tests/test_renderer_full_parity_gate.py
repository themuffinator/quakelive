from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from tests._shared import REPO_ROOT, read_json as _read_json, write_json as _write_json

RENDERER_FULL_PARITY_GATE_PATH = (
	REPO_ROOT / "artifacts" / "renderer_validation" / "logs" / "renderer_full_parity_gate.json"
)
RENDERER_RUNTIME_EVIDENCE_ARTIFACT_NAME = "renderer_runtime_evidence_latest.json"
RENDERER_RUNTIME_EVIDENCE_PATH = (
	REPO_ROOT / "artifacts" / "renderer_validation" / "logs" / RENDERER_RUNTIME_EVIDENCE_ARTIFACT_NAME
)
RENDERER_PLAN_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "renderer-full-parity-audit-and-implementation-plan-2026-04-09.md"
)
RETAIL_FONT_STACK_NOTE_PATH = REPO_ROOT / "docs" / "platform" / "retail-font-stack.md"
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "renderer-validation.yml"
BUILD_PIPELINE_PATH = REPO_ROOT / "docs" / "build-pipeline.md"
HUD_BASELINE_PATH = REPO_ROOT / "docs" / "hud_render_baseline.md"
RUNTIME_PROBE_PATH = REPO_ROOT / "tools" / "renderer" / "run_renderer_runtime_probe.ps1"
FONT_AUDIT_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "audit-retail-font-stack.ps1"
BUILD_SCRIPT_PATH = REPO_ROOT / ".vscode" / "build.ps1"

TR_PUBLIC_PATH = REPO_ROOT / "src" / "code" / "renderer" / "tr_public.h"
TR_INIT_PATH = REPO_ROOT / "src" / "code" / "renderer" / "tr_init.c"
TR_IMAGE_PATH = REPO_ROOT / "src" / "code" / "renderer" / "tr_image.c"
TR_BACKEND_PATH = REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c"
TR_FONT_PATH = REPO_ROOT / "src" / "code" / "renderer" / "tr_font.c"
RENDERER_VCXPROJ_PATH = REPO_ROOT / "src" / "code" / "renderer" / "renderer.vcxproj"
RENDERER_VCXPROJ_FILTERS_PATH = REPO_ROOT / "src" / "code" / "renderer" / "renderer.vcxproj.filters"
RENDERER_VCPROJ_PATH = REPO_ROOT / "src" / "code" / "renderer" / "renderer.vcproj"
QUAKELIVE_STEAM_VCXPROJ_PATH = REPO_ROOT / "src" / "code" / "quakelive_steam.vcxproj"
UNIX_MAKEFILE_PATH = REPO_ROOT / "src" / "code" / "unix" / "Makefile"
WIN_WNDPROC_PATH = REPO_ROOT / "src" / "code" / "win32" / "win_wndproc.c"
WIN_GLIMP_PATH = REPO_ROOT / "src" / "code" / "win32" / "win_glimp.c"
WIN_SYSCON_PATH = REPO_ROOT / "src" / "code" / "win32" / "win_syscon.c"
CL_MAIN_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_main.c"
CL_UI_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_ui.c"
CL_CGAME_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
CL_STEAM_RESOURCES_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_steam_resources.c"
CLIENT_H_PATH = REPO_ROOT / "src" / "code" / "client" / "client.h"
SRC_CODE_ROOT = REPO_ROOT / "src" / "code"

RG_G06_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "renderer-internal-helper-ownership-2026-04-09.md"
)
RG_G06_MAPPING_PATH = REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_100.md"
RG_G05_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "renderer-font-cache-and-atlas-ownership-2026-04-10.md"
)
RG_P8_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "renderer-host-text-core-ownership-2026-04-10.md"
)
RG_P9_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "renderer-host-text-import-switchover-and-debug-atlas-2026-04-10.md"
)
RG_P10_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "renderer-freetype-build-lane-recovery-2026-04-10.md"
)
RG_P11_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "renderer-text-strict-validation-and-runtime-evidence-2026-04-10.md"
)

GAP_ORDER = (
	"RG-G01",
	"RG-G02",
	"RG-G03",
	"RG-G04",
	"RG-G05",
	"RG-G06",
	"RG-G07",
	"RG-G08",
	"RG-G09",
)

def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8")

def _source_code_files() -> list[Path]:
	return sorted(
		path
		for path in SRC_CODE_ROOT.rglob("*")
		if path.is_file() and path.suffix.lower() in {".c", ".h"}
	)

def _paths_with_pattern(pattern: str) -> list[Path]:
	return [
		path
		for path in _source_code_files()
		if pattern in path.read_text(encoding="utf-8", errors="ignore")
	]

def _entry(gap_id: str, status: str, summary: str, details: dict[str, Any]) -> dict[str, Any]:
	return {
		"gap_id": gap_id,
		"status": status,
		"summary": summary,
		"details": details,
	}

def _build_renderer_full_parity_gate_report() -> dict[str, Any]:
	renderer_plan = _read_text(RENDERER_PLAN_PATH)
	retail_font_stack_note = _read_text(RETAIL_FONT_STACK_NOTE_PATH)
	build_pipeline = _read_text(BUILD_PIPELINE_PATH)
	hud_baseline = _read_text(HUD_BASELINE_PATH)
	tr_public = _read_text(TR_PUBLIC_PATH)
	tr_init = _read_text(TR_INIT_PATH)
	tr_image = _read_text(TR_IMAGE_PATH)
	tr_backend = _read_text(TR_BACKEND_PATH)
	tr_font = _read_text(TR_FONT_PATH)
	renderer_vcxproj = _read_text(RENDERER_VCXPROJ_PATH)
	renderer_vcxproj_filters = _read_text(RENDERER_VCXPROJ_FILTERS_PATH)
	renderer_vcproj = _read_text(RENDERER_VCPROJ_PATH)
	quakelive_steam_vcxproj = _read_text(QUAKELIVE_STEAM_VCXPROJ_PATH)
	unix_makefile = _read_text(UNIX_MAKEFILE_PATH)
	win_wndproc = _read_text(WIN_WNDPROC_PATH)
	win_glimp = _read_text(WIN_GLIMP_PATH)
	win_syscon = _read_text(WIN_SYSCON_PATH)
	cl_main = _read_text(CL_MAIN_PATH)
	cl_ui = _read_text(CL_UI_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_steam_resources = _read_text(CL_STEAM_RESOURCES_PATH)
	client_h = _read_text(CLIENT_H_PATH)
	workflow_text = _read_text(WORKFLOW_PATH)
	runtime_probe = _read_text(RUNTIME_PROBE_PATH)
	build_script = _read_text(BUILD_SCRIPT_PATH)
	rg_g06_note = _read_text(RG_G06_NOTE_PATH)
	rg_g06_mapping = _read_text(RG_G06_MAPPING_PATH)
	rg_g05_note = _read_text(RG_G05_NOTE_PATH)
	rg_p8_note = _read_text(RG_P8_NOTE_PATH)
	rg_p9_note = _read_text(RG_P9_NOTE_PATH)
	rg_p10_note = _read_text(RG_P10_NOTE_PATH)
	rg_p11_note = _read_text(RG_P11_NOTE_PATH)
	runtime_evidence = _read_json(RENDERER_RUNTIME_EVIDENCE_PATH) if RENDERER_RUNTIME_EVIDENCE_PATH.exists() else None
	fontstash_paths = _paths_with_pattern("*fontstash")
	fons_error_paths = _paths_with_pattern("R_fonsErrorCallback")
	fons_symbol_paths = _paths_with_pattern("fons")
	debug_font_atlas_paths = _paths_with_pattern("r_debugFontAtlas")
	expected_debug_font_atlas_paths = {TR_INIT_PATH.resolve(), (REPO_ROOT / "src" / "code" / "renderer" / "tr_local.h").resolve()}
	unexpected_debug_font_atlas_paths = [
		path for path in debug_font_atlas_paths if path.resolve() not in expected_debug_font_atlas_paths
	]

	report: dict[str, Any] = {
		"artifact_version": 1,
		"phase": "RG-P11",
		"parity_estimate": {
			"before": 98,
			"after": 100,
		},
		"gap_order": list(GAP_ORDER),
		"tranches": {},
	}

	rg_g01_ok = (
		"AdvertisementBridge_UpdateLoadingViewParameters" in tr_public
		and "AdvertisementBridge_UpdateLoadingViewParameters = AdvertisementBridge_UpdateLoadingViewParameters;" in tr_init
		and "void CL_RegisterFont( const char *fontName, int pointSize, fontInfo_t *font ) {" in cl_main
		and "tests/test_renderer_export_tail_parity.py" in workflow_text
	)
	report["tranches"]["RG-G01"] = _entry(
		"RG-G01",
		"pass" if rg_g01_ok else "fail",
		(
			"Export-tail ABI closure remains pinned by source and validation wiring."
			if rg_g01_ok
			else "Export-tail ABI closure no longer matches the documented validation surface."
		),
		{
			"advert_bridge_slot_present": "AdvertisementBridge_UpdateLoadingViewParameters" in tr_public,
			"bridge_assignment_present": "AdvertisementBridge_UpdateLoadingViewParameters = AdvertisementBridge_UpdateLoadingViewParameters;" in tr_init,
			"client_font_lane_present": "void CL_RegisterFont( const char *fontName, int pointSize, fontInfo_t *font ) {" in cl_main,
			"workflow_references_export_test": "tests/test_renderer_export_tail_parity.py" in workflow_text,
		},
	)

	rg_g02_ok = (
		"image_t *R_CreateImageWithTarget(" in tr_image
		and "int R_DetectImageTypeFromMemory( const byte *buffer, int bufferLength ) {" in tr_image
		and "image_t *R_LoadImageFromMemory(" in tr_image
		and "qhandle_t CL_RegisterShaderFromRGBA(" in cl_main
		and "qhandle_t CL_RegisterShaderFromMemory(" in cl_main
		and "CL_RegisterShaderFromMemory( rendererName, buffer, bufferLength, qfalse );" in cl_steam_resources
		and "tests/test_renderer_memory_image_parity.py" in workflow_text
	)
	report["tranches"]["RG-G02"] = _entry(
		"RG-G02",
		"pass" if rg_g02_ok else "fail",
		(
			"Renderer memory-image ingestion remains wired and validated."
			if rg_g02_ok
			else "Renderer memory-image ingestion no longer matches the documented parity lane."
		),
		{
			"target_aware_constructor_present": "image_t *R_CreateImageWithTarget(" in tr_image,
			"memory_type_detection_present": "int R_DetectImageTypeFromMemory( const byte *buffer, int bufferLength ) {" in tr_image,
			"memory_loader_present": "image_t *R_LoadImageFromMemory(" in tr_image,
			"client_rgba_wrapper_present": "qhandle_t CL_RegisterShaderFromRGBA(" in cl_main,
			"client_memory_wrapper_present": "qhandle_t CL_RegisterShaderFromMemory(" in cl_main,
			"steam_bridge_memory_registration_present": "CL_RegisterShaderFromMemory( rendererName, buffer, bufferLength, qfalse );" in cl_steam_resources,
		},
	)

	rg_g03_ok = (
		'"scripts/colorcorrect.fs"' in tr_backend
		and '"scripts/posteffect.vs"' in tr_backend
		and "GL_TEXTURE_RECTANGLE_ARB" in tr_backend
		and "tr.postProcessActive = backEnd.postProcessActive;" in tr_backend
		and 'r_contrast = ri.Cvar_Get( "r_contrast", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
		and "tests/test_renderer_post_process_parity.py" in workflow_text
	)
	report["tranches"]["RG-G03"] = _entry(
		"RG-G03",
		"pass" if rg_g03_ok else "fail",
		(
			"Renderer post-process exactness remains pinned by the shader-backed validation surface."
			if rg_g03_ok
			else "Renderer post-process validation no longer matches the recovered shader-backed implementation."
		),
		{
			"colorcorrect_shader_present": '"scripts/colorcorrect.fs"' in tr_backend,
			"posteffect_vertex_shader_present": '"scripts/posteffect.vs"' in tr_backend,
			"rectangle_texture_path_present": "GL_TEXTURE_RECTANGLE_ARB" in tr_backend,
			"active_state_mirror_present": "tr.postProcessActive = backEnd.postProcessActive;" in tr_backend,
			"contrast_cvar_present": 'r_contrast = ri.Cvar_Get( "r_contrast", "1", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init,
		},
	)

	rg_g04_ok = (
		"WIN_SyncWindowedModeFromClientRect" in win_wndproc
		and "windowStyle |= WS_MAXIMIZE;" in win_glimp
		and "void Sys_CreateLoadingWindow( void )" in win_syscon
		and "tests/test_renderer_win32_host_glue_parity.py" in workflow_text
		and runtime_evidence is not None
		and runtime_evidence["main_menu"]["engine_screenshot"]
		and runtime_evidence["map_runtime"]["engine_screenshot"]
	)
	report["tranches"]["RG-G04"] = _entry(
		"RG-G04",
		"pass" if rg_g04_ok else "fail",
		(
			"Win32 renderer-host glue closure remains covered by source checks and windowed runtime evidence."
			if rg_g04_ok
			else "Win32 renderer-host glue evidence is incomplete."
		),
		{
			"windowed_sync_helper_present": "WIN_SyncWindowedModeFromClientRect" in win_wndproc,
			"maximize_preservation_present": "windowStyle |= WS_MAXIMIZE;" in win_glimp,
			"loading_window_wrapper_present": "void Sys_CreateLoadingWindow( void )" in win_syscon,
			"runtime_main_engine_capture_present": bool(runtime_evidence and runtime_evidence["main_menu"]["engine_screenshot"]),
			"runtime_map_engine_capture_present": bool(runtime_evidence and runtime_evidence["map_runtime"]["engine_screenshot"]),
		},
	)

	rg_g05_closed = "## RG-G05" in renderer_plan and "**Status:** Closed" in renderer_plan
	rg_g05_ok = (
		rg_g05_closed
		and "docs/reverse-engineering/renderer-font-cache-and-atlas-ownership-2026-04-10.md" in renderer_plan
		and "## Retail-Backed Classic Font Behaviors" in rg_g05_note
		and "## Compatibility-Only Scaffolding That Remains Intentional" in rg_g05_note
		and "RG-G05 is now considered closed" in rg_g05_note
		and "static void R_BuildFontCacheStem( const char *fontName, char *cacheStem, int cacheStemSize ) {" in tr_font
		and "static void R_BuildLegacyFontCacheName( int pointSize, char *cacheName, int cacheNameSize ) {" in tr_font
		and "static const char *R_FindCachedFontDataName( const char *cacheName, const char *legacyCacheName ) {" in tr_font
		and "static void R_RegisterCachedFontShaders( fontInfo_t *font ) {" in tr_font
		and "static void R_FlushFontAtlasPage( const char *fontName, int pointSize, int imageNumber, fontInfo_t *font, int firstGlyph, int lastGlyph, byte *out ) {" in tr_font
		and "loadName = R_FindCachedFontDataName( cacheName, legacyCacheName );" in tr_font
		and "R_RegisterCachedFontShaders( font );" in tr_font
		and "R_FlushFontAtlasPage( fontName, pointSize, imageNumber++, font, lastStart, i - 1, out );" in tr_font
		and "R_FlushFontAtlasPage( fontName, pointSize, imageNumber++, font, lastStart, i, out );" in tr_font
		and "for ( i = GLYPH_START; i <= GLYPH_END; i++ ) {" in tr_font
	)
	report["tranches"]["RG-G05"] = _entry(
		"RG-G05",
		"pass" if rg_g05_ok else "fail",
		(
			"Classic renderer font/cache/atlas exactness is now closed and structurally pinned."
			if rg_g05_ok
			else "Classic renderer font/cache/atlas exactness is not yet fully pinned."
		),
		{
			"renderer_plan_marks_closed": rg_g05_closed,
			"ownership_note_present": RG_G05_NOTE_PATH.exists(),
			"ownership_note_has_retail_section": "## Retail-Backed Classic Font Behaviors" in rg_g05_note,
			"ownership_note_has_compat_section": "## Compatibility-Only Scaffolding That Remains Intentional" in rg_g05_note,
			"cache_stem_helper_present": "static void R_BuildFontCacheStem( const char *fontName, char *cacheStem, int cacheStemSize ) {" in tr_font,
			"legacy_cache_helper_present": "static void R_BuildLegacyFontCacheName( int pointSize, char *cacheName, int cacheNameSize ) {" in tr_font,
			"cache_probe_helper_present": "static const char *R_FindCachedFontDataName( const char *cacheName, const char *legacyCacheName ) {" in tr_font,
			"cached_shader_rebind_helper_present": "static void R_RegisterCachedFontShaders( fontInfo_t *font ) {" in tr_font,
			"atlas_flush_helper_present": "static void R_FlushFontAtlasPage( const char *fontName, int pointSize, int imageNumber, fontInfo_t *font, int firstGlyph, int lastGlyph, byte *out ) {" in tr_font,
			"cached_font_probe_present": "loadName = R_FindCachedFontDataName( cacheName, legacyCacheName );" in tr_font,
			"inclusive_cached_shader_rebind_present": "R_RegisterCachedFontShaders( font );" in tr_font,
			"inclusive_page_flush_present": "R_FlushFontAtlasPage( fontName, pointSize, imageNumber++, font, lastStart, i, out );" in tr_font,
		},
	)

	rg_g06_ok = (
		"## Phase 5 Ownership Closure" in rg_g06_note
		and "## Phase 5 Closure Update (2026-04-09)" in rg_g06_mapping
		and "tests/test_renderer_internal_helper_mapping_parity.py" in workflow_text
	)
	report["tranches"]["RG-G06"] = _entry(
		"RG-G06",
		"pass" if rg_g06_ok else "fail",
		(
			"Bounded renderer helper-band ownership closure remains documented and gated."
			if rg_g06_ok
			else "Bounded renderer helper-band ownership closure is no longer fully wired."
		),
		{
			"ownership_note_closed": "## Phase 5 Ownership Closure" in rg_g06_note,
			"mapping_round_closed": "## Phase 5 Closure Update (2026-04-09)" in rg_g06_mapping,
			"workflow_references_rg_g06_test": "tests/test_renderer_internal_helper_mapping_parity.py" in workflow_text,
		},
	)

	runtime_clean = (
		runtime_evidence is not None
		and runtime_evidence["phase"] == "RG-P11"
		and runtime_evidence["parity_estimate"] == {"before": 98, "after": 100}
		and runtime_evidence["warnings"] == []
		and runtime_evidence["missing_log_markers"] == []
		and runtime_evidence["main_menu"]["engine_sha256"]
		and runtime_evidence["debug_atlas"]["engine_sha256"]
		and runtime_evidence["main_menu"]["engine_sha256"] != runtime_evidence["debug_atlas"]["engine_sha256"]
		and runtime_evidence["map_runtime"]["engine_sha256"]
		and runtime_evidence["map_runtime"]["server_seen"]
		and runtime_evidence["map_runtime"]["active_seen"]
		and runtime_evidence["map_runtime"]["shot_logged"]
		and runtime_evidence["text_validation"]["fontstash_init_seen"]
		and not runtime_evidence["text_validation"]["registerfont_fallback_seen"]
		and runtime_evidence["text_validation"]["debug_atlas_engine_capture_distinct"]
	)
	rg_g07_ok = (
		RUNTIME_PROBE_PATH.exists()
		and RENDERER_RUNTIME_EVIDENCE_ARTIFACT_NAME in runtime_probe
		and "map $MapName ffa" in runtime_probe
		and runtime_clean
		and "tests/test_renderer_full_parity_gate.py" in workflow_text
		and "renderer_full_parity_gate.json" in build_pipeline
		and RENDERER_RUNTIME_EVIDENCE_ARTIFACT_NAME in build_pipeline
		and RENDERER_RUNTIME_EVIDENCE_ARTIFACT_NAME in hud_baseline
		and "tools/renderer/run_renderer_runtime_probe.ps1" in hud_baseline
	)
	report["tranches"]["RG-G07"] = _entry(
		"RG-G07",
		"pass" if rg_g07_ok else "fail",
		(
			"Renderer parity gate and tracked runtime evidence are now present."
			if rg_g07_ok
			else "Renderer parity gate wiring or runtime evidence is incomplete."
		),
		{
			"runtime_probe_present": RUNTIME_PROBE_PATH.exists(),
			"runtime_probe_mentions_latest_alias": RENDERER_RUNTIME_EVIDENCE_ARTIFACT_NAME in runtime_probe,
			"runtime_probe_uses_current_map_contract": "map $MapName ffa" in runtime_probe,
			"runtime_evidence_present": RENDERER_RUNTIME_EVIDENCE_PATH.exists(),
			"runtime_evidence_clean": runtime_clean,
			"runtime_no_registerfont_fallback": (
				runtime_evidence is not None
				and not runtime_evidence["text_validation"]["registerfont_fallback_seen"]
			),
			"workflow_references_gate": "tests/test_renderer_full_parity_gate.py" in workflow_text,
			"workflow_runs_gate": "tests/test_renderer_full_parity_gate.py" in workflow_text,
			"build_pipeline_mentions_gate": "renderer_full_parity_gate.json" in build_pipeline,
			"build_pipeline_mentions_runtime_artifact": RENDERER_RUNTIME_EVIDENCE_ARTIFACT_NAME in build_pipeline,
			"hud_baseline_mentions_runtime_artifact": RENDERER_RUNTIME_EVIDENCE_ARTIFACT_NAME in hud_baseline,
		},
	)

	rg_g08_closed = "## RG-G08" in renderer_plan and "**Status:** Closed" in renderer_plan
	rg_g08_note_present = (
		"retail host text switchover and debug-atlas closure remain incomplete" in renderer_plan
		or "retail host text import switchover and debug-atlas closure are now complete" in renderer_plan
	)
	rg_g08_ok = (
		rg_g08_closed
		and rg_g08_note_present
		and RG_P9_NOTE_PATH.exists()
		and "RG-P9 is now considered complete." in rg_p9_note
		and "void RE_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor, const float *baseColor ) {" in tr_font
		and "void RE_MeasureScaledText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outWidth, float *outHeight, float *outLeft ) {" in tr_font
		and "RE_DrawScaledText( x, y, text, fontHandle, scale, maxX, outMaxX," in cl_ui
		and "RE_DrawScaledText( x, y, text, fontHandle, scale, maxX, outMaxX," in cl_cgame
		and "RE_MeasureScaledText( text, end, fontHandle, scale, maxX, &width, &height, outLeft );" in cl_ui
		and "RE_MeasureScaledText( text, end, fontHandle, scale, maxX, &width, &height, outLeft );" in cl_cgame
		and "QL_UI_GetScaledFont" not in cl_ui
		and "QL_CG_GetScaledFont" not in cl_cgame
		and "static void RB_ShowFontAtlas( void ) {" in tr_backend
		and "R_GetFontStashDebugInfo( &image, &atlasWidth, &atlasHeight )" in tr_backend
		and bool(unexpected_debug_font_atlas_paths)
	)
	report["tranches"]["RG-G08"] = _entry(
		"RG-G08",
		"pass" if rg_g08_ok else "fail",
		(
			"Retail host text import switchover and debug-atlas closure are now pinned in source."
			if rg_g08_ok
			else "Retail host text import switchover and debug-atlas closure remain incomplete."
		),
		{
			"renderer_plan_marks_closed": rg_g08_closed,
			"retail_font_stack_note_mentions_fontstash": "*fontstash" in retail_font_stack_note,
			"retail_font_stack_note_mentions_host_wrappers": "DrawScaledText" in retail_font_stack_note and "MeasureText" in retail_font_stack_note,
			"source_fontstash_impl_present": bool(fontstash_paths),
			"source_fons_error_callback_present": bool(fons_error_paths),
			"rg_p8_note_marks_complete": "RG-P8 is now considered complete." in rg_p8_note,
			"rg_p9_note_present": RG_P9_NOTE_PATH.exists(),
			"rg_p9_note_marks_complete": "RG-P9 is now considered complete." in rg_p9_note,
			"ui_routes_through_renderer_host_text": "RE_DrawScaledText( x, y, text, fontHandle, scale, maxX, outMaxX," in cl_ui,
			"cgame_routes_through_renderer_host_text": "RE_DrawScaledText( x, y, text, fontHandle, scale, maxX, outMaxX," in cl_cgame,
			"ui_compat_shim_removed": "QL_UI_GetScaledFont" not in cl_ui,
			"cgame_compat_shim_removed": "QL_CG_GetScaledFont" not in cl_cgame,
			"debug_font_atlas_impl_present": bool(unexpected_debug_font_atlas_paths),
		},
	)

	rg_g09_closed = "## RG-G09" in renderer_plan and "**Status:** Closed" in renderer_plan
	rg_g09_note_present = "Renderer font build reproducibility and strict validation are now complete" in renderer_plan
	rg_g09_ok = (
		rg_g09_closed
		and rg_g09_note_present
		and FONT_AUDIT_SCRIPT_PATH.exists()
		and RG_P10_NOTE_PATH.exists()
		and RG_P11_NOTE_PATH.exists()
		and "RG-P10 is now considered complete." in rg_p10_note
		and "RG-P11 is now considered complete." in rg_p11_note
		and "#include <ft2build.h>" in tr_font
		and "#include FT_FREETYPE_H" in tr_font
		and "QLEnableFreeType" in renderer_vcxproj
		and "<QLEnableFreeType Condition=\"'$(QLEnableFreeType)'==''\">1</QLEnableFreeType>" in renderer_vcxproj
		and "ValidateFreeType" in renderer_vcxproj
		and "..\\ft2\\" not in renderer_vcxproj
		and "..\\ft2\\" not in renderer_vcxproj_filters
		and "..\\ft2\\" not in renderer_vcproj
		and "QLEnableFreeType" in quakelive_steam_vcxproj
		and "<QLEnableFreeType Condition=\"'$(QLEnableFreeType)'==''\">1</QLEnableFreeType>" in quakelive_steam_vcxproj
		and "ValidateFreeType" in quakelive_steam_vcxproj
		and "$(FreeTypeDependencies);$(VorbisDependencies);$(PngDependencies);winmm.lib;wsock32.lib;Dbghelp.lib;%(AdditionalDependencies)" in quakelive_steam_vcxproj
		and "QLEnableFreeType" in build_script
		and "Invoke-InternalDependencyBootstrap -DependencyName 'freetype'" in build_script
		and "build_internal_deps.ps1" in build_script
		and "VCPKG_ROOT" not in renderer_vcxproj
		and "VCPKG_ROOT" not in quakelive_steam_vcxproj
		and "VCPKG_ROOT" not in build_script
		and "QL_ENABLE_FREETYPE ?= 0" in unix_makefile
		and "pkg-config --cflags freetype2" in unix_makefile
		and "CLIENT_FREETYPE_CFLAGS := $(FREETYPE_CFLAGS) -DBUILD_FREETYPE" in unix_makefile
		and runtime_clean
	)
	report["tranches"]["RG-G09"] = _entry(
		"RG-G09",
		"pass" if rg_g09_ok else "fail",
		(
			"Renderer font build reproducibility and strict text validation are now closed."
			if rg_g09_ok
			else "Renderer font build reproducibility and strict text validation remain incomplete."
		),
		{
			"renderer_plan_marks_closed": rg_g09_closed,
			"rg_p10_note_present": RG_P10_NOTE_PATH.exists(),
			"rg_p11_note_present": RG_P11_NOTE_PATH.exists(),
			"rg_p10_note_marks_complete": "RG-P10 is now considered complete." in rg_p10_note,
			"rg_p11_note_marks_complete": "RG-P11 is now considered complete." in rg_p11_note,
			"tr_font_uses_external_ft2build": "#include <ft2build.h>" in tr_font,
			"tr_font_uses_ft_freetype_macro": "#include FT_FREETYPE_H" in tr_font,
			"renderer_vcxproj_has_freetype_toggle": "QLEnableFreeType" in renderer_vcxproj,
			"renderer_vcxproj_defaults_freetype_on": "<QLEnableFreeType Condition=\"'$(QLEnableFreeType)'==''\">1</QLEnableFreeType>" in renderer_vcxproj,
			"renderer_vcxproj_has_validate_target": "ValidateFreeType" in renderer_vcxproj,
			"renderer_vcxproj_references_ft2": "..\\ft2\\" in renderer_vcxproj,
			"renderer_vcxproj_filters_references_ft2": "..\\ft2\\" in renderer_vcxproj_filters,
			"renderer_vcproj_references_ft2": "..\\ft2\\" in renderer_vcproj,
			"engine_vcxproj_has_freetype_toggle": "QLEnableFreeType" in quakelive_steam_vcxproj,
			"engine_vcxproj_defaults_freetype_on": "<QLEnableFreeType Condition=\"'$(QLEnableFreeType)'==''\">1</QLEnableFreeType>" in quakelive_steam_vcxproj,
			"engine_vcxproj_has_validate_target": "ValidateFreeType" in quakelive_steam_vcxproj,
			"engine_vcxproj_links_freetype_dependencies": "$(FreeTypeDependencies);$(VorbisDependencies);$(PngDependencies);winmm.lib;wsock32.lib;Dbghelp.lib;%(AdditionalDependencies)" in quakelive_steam_vcxproj,
			"build_script_has_freetype_toggle": "QLEnableFreeType" in build_script,
			"build_script_bootstraps_freetype": "Invoke-InternalDependencyBootstrap -DependencyName 'freetype'" in build_script,
			"build_script_bootstraps_internal_codecs": "build_internal_deps.ps1" in build_script,
			"renderer_vcxproj_has_vcpkg_probe": "VCPKG_ROOT" in renderer_vcxproj,
			"engine_vcxproj_has_vcpkg_probe": "VCPKG_ROOT" in quakelive_steam_vcxproj,
			"build_script_has_vcpkg_probe": "VCPKG_ROOT" in build_script,
			"unix_makefile_has_freetype_toggle": "QL_ENABLE_FREETYPE ?= 0" in unix_makefile,
			"unix_makefile_uses_pkg_config_freetype": "pkg-config --cflags freetype2" in unix_makefile,
			"unix_makefile_defines_build_freetype": "CLIENT_FREETYPE_CFLAGS := $(FREETYPE_CFLAGS) -DBUILD_FREETYPE" in unix_makefile,
			"runtime_artifact_is_text_strict": runtime_clean,
		},
	)

	non_passing_gap_ids = [
		gap_id
		for gap_id in GAP_ORDER
		if report["tranches"][gap_id]["status"] != "pass"
	]
	report["overall_status"] = "pass" if not non_passing_gap_ids else "fail"
	report["non_passing_gap_ids"] = non_passing_gap_ids
	report["summary"] = {
		"passing_count": sum(1 for gap_id in GAP_ORDER if report["tranches"][gap_id]["status"] == "pass"),
		"blocked_count": sum(1 for gap_id in GAP_ORDER if report["tranches"][gap_id]["status"] == "blocked"),
		"failing_count": sum(1 for gap_id in GAP_ORDER if report["tranches"][gap_id]["status"] == "fail"),
	}
	return report

def test_renderer_runtime_evidence_artifact_is_tracked_and_clean() -> None:
	runtime_evidence = _read_json(RENDERER_RUNTIME_EVIDENCE_PATH)

	assert runtime_evidence["phase"] == "RG-P11"
	assert runtime_evidence["parity_estimate"] == {"before": 98, "after": 100}
	assert runtime_evidence["warnings"] == []
	assert runtime_evidence["missing_log_markers"] == []
	assert runtime_evidence["main_menu"]["engine_screenshot"]
	assert runtime_evidence["main_menu"]["engine_sha256"]
	assert runtime_evidence["debug_atlas"]["engine_screenshot"]
	assert runtime_evidence["debug_atlas"]["engine_sha256"]
	assert runtime_evidence["main_menu"]["engine_sha256"] != runtime_evidence["debug_atlas"]["engine_sha256"]
	assert runtime_evidence["map_runtime"]["engine_screenshot"]
	assert runtime_evidence["map_runtime"]["engine_sha256"]
	assert runtime_evidence["map_runtime"]["map"] == "bloodrun"
	assert runtime_evidence["map_runtime"]["server_seen"] is True
	assert runtime_evidence["map_runtime"]["active_seen"] is True
	assert runtime_evidence["map_runtime"]["shot_logged"] is True
	assert runtime_evidence["text_validation"]["fontstash_init_seen"] is True
	assert runtime_evidence["text_validation"]["debug_atlas_engine_capture_distinct"] is True

def test_renderer_full_parity_gate_writes_status_artifact() -> None:
	report = _build_renderer_full_parity_gate_report()
	_write_json(RENDERER_FULL_PARITY_GATE_PATH, report)

	assert RENDERER_FULL_PARITY_GATE_PATH.exists()
	assert _read_json(RENDERER_FULL_PARITY_GATE_PATH) == report
	assert report["phase"] == "RG-P11"
	assert report["gap_order"] == list(GAP_ORDER)
	assert set(report["tranches"]) == set(GAP_ORDER)
	assert report["overall_status"] == "pass"
	assert report["non_passing_gap_ids"] == []
	assert report["summary"] == {
		"passing_count": 9,
		"blocked_count": 0,
		"failing_count": 0,
	}

	for gap_id in GAP_ORDER:
		entry = report["tranches"][gap_id]
		assert entry["gap_id"] == gap_id
		assert entry["status"] in {"pass", "fail", "blocked"}
		assert entry["summary"]

def test_renderer_full_parity_gate_release_mode() -> None:
	if os.environ.get("RENDERER_FULL_PARITY_GATE_ENFORCE") != "1":
		pytest.skip("Set RENDERER_FULL_PARITY_GATE_ENFORCE=1 to require a full renderer parity pass.")

	report = _build_renderer_full_parity_gate_report()
	_write_json(RENDERER_FULL_PARITY_GATE_PATH, report)
	assert report["overall_status"] == "pass", (
		"Renderer full parity gate failed for "
		+ ", ".join(report["non_passing_gap_ids"])
	)
