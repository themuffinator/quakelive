from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
RENDERER_FULL_PARITY_GATE_PATH = (
	REPO_ROOT / "artifacts" / "renderer_validation" / "logs" / "renderer_full_parity_gate.json"
)
RENDERER_RUNTIME_EVIDENCE_PATH = (
	REPO_ROOT / "artifacts" / "renderer_validation" / "logs" / "renderer_runtime_evidence_20260409.json"
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

TR_PUBLIC_PATH = REPO_ROOT / "src" / "code" / "renderer" / "tr_public.h"
TR_INIT_PATH = REPO_ROOT / "src" / "code" / "renderer" / "tr_init.c"
TR_IMAGE_PATH = REPO_ROOT / "src" / "code" / "renderer" / "tr_image.c"
TR_BACKEND_PATH = REPO_ROOT / "src" / "code" / "renderer" / "tr_backend.c"
TR_FONT_PATH = REPO_ROOT / "src" / "code" / "renderer" / "tr_font.c"
RENDERER_VCXPROJ_PATH = REPO_ROOT / "src" / "code" / "renderer" / "renderer.vcxproj"
RENDERER_VCPROJ_PATH = REPO_ROOT / "src" / "code" / "renderer" / "renderer.vcproj"
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


def _read_json(path: Path) -> dict[str, Any]:
	return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


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
	renderer_vcproj = _read_text(RENDERER_VCPROJ_PATH)
	win_wndproc = _read_text(WIN_WNDPROC_PATH)
	win_glimp = _read_text(WIN_GLIMP_PATH)
	win_syscon = _read_text(WIN_SYSCON_PATH)
	cl_main = _read_text(CL_MAIN_PATH)
	cl_ui = _read_text(CL_UI_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_steam_resources = _read_text(CL_STEAM_RESOURCES_PATH)
	client_h = _read_text(CLIENT_H_PATH)
	workflow_text = _read_text(WORKFLOW_PATH)
	rg_g06_note = _read_text(RG_G06_NOTE_PATH)
	rg_g06_mapping = _read_text(RG_G06_MAPPING_PATH)
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
		"phase": "RG-P6",
		"parity_estimate": {
			"before": 98,
			"after": 94,
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
		and 'r_contrast = ri.Cvar_Get( "r_contrast", "1", CVAR_ARCHIVE );' in tr_init
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
			"contrast_cvar_present": 'r_contrast = ri.Cvar_Get( "r_contrast", "1", CVAR_ARCHIVE );' in tr_init,
		},
	)

	rg_g04_ok = (
		"WIN_SyncWindowedModeFromClientRect" in win_wndproc
		and "windowStyle |= WS_MAXIMIZE;" in win_glimp
		and "void Sys_CreateLoadingWindow( void )" in win_syscon
		and "tests/test_renderer_win32_host_glue_parity.py" in workflow_text
		and runtime_evidence is not None
		and runtime_evidence["main_menu"]["window_capture"]
		and runtime_evidence["map_runtime"]["window_capture"]
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
			"runtime_window_capture_present": bool(runtime_evidence and runtime_evidence["main_menu"]["window_capture"]),
			"runtime_map_capture_present": bool(runtime_evidence and runtime_evidence["map_runtime"]["window_capture"]),
		},
	)

	rg_g05_open = "## RG-G05" in renderer_plan and "**Status:** Open" in renderer_plan
	rg_g05_remaining = "Classic renderer font/cache/atlas exactness remains partially source-biased" in renderer_plan
	rg_g05_fail_details = {
		"renderer_plan_still_marks_open": rg_g05_open,
		"renderer_plan_still_lists_font_gap": rg_g05_remaining,
		"font_fallback_helper_present": "static qboolean RE_RegisterFontFallback(" in tr_font,
		"font_registration_entry_present": "void RE_RegisterFont( const char *fontName, int pointSize, fontInfo_t *font ) {" in tr_font,
		"freetype_init_present": "void R_InitFreeType()" in tr_font,
	}
	report["tranches"]["RG-G05"] = _entry(
		"RG-G05",
		"fail",
		"Classic renderer font/cache/atlas exactness remains intentionally open.",
		rg_g05_fail_details,
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
		and runtime_evidence["phase"] == "RG-P6"
		and runtime_evidence["parity_estimate"] == {"before": 96, "after": 98}
		and runtime_evidence["warnings"] == []
		and runtime_evidence["missing_log_markers"] == []
		and runtime_evidence["main_menu"]["window_sha256"]
		and runtime_evidence["map_runtime"]["window_sha256"]
		and runtime_evidence["main_menu"]["window_sha256"] != runtime_evidence["map_runtime"]["window_sha256"]
		and runtime_evidence["map_runtime"]["server_seen"]
		and runtime_evidence["map_runtime"]["active_seen"]
		and runtime_evidence["map_runtime"]["shot_logged"]
	)
	rg_g07_ok = (
		RUNTIME_PROBE_PATH.exists()
		and runtime_clean
		and "tests/test_renderer_full_parity_gate.py" in workflow_text
		and "renderer_full_parity_gate.json" in build_pipeline
		and "renderer_runtime_evidence_20260409.json" in build_pipeline
		and "renderer_runtime_evidence_20260409.json" in hud_baseline
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
			"runtime_evidence_present": RENDERER_RUNTIME_EVIDENCE_PATH.exists(),
			"runtime_evidence_clean": runtime_clean,
			"workflow_references_gate": "tests/test_renderer_full_parity_gate.py" in workflow_text,
			"workflow_runs_gate": "tests/test_renderer_full_parity_gate.py" in workflow_text,
			"build_pipeline_mentions_gate": "renderer_full_parity_gate.json" in build_pipeline,
			"build_pipeline_mentions_runtime_artifact": "renderer_runtime_evidence_20260409.json" in build_pipeline,
			"hud_baseline_mentions_runtime_artifact": "renderer_runtime_evidence_20260409.json" in hud_baseline,
		},
	)

	rg_g08_open = "## RG-G08" in renderer_plan and "**Status:** Open" in renderer_plan
	rg_g08_note_present = "retail host FontStash text engine" in renderer_plan
	rg_g08_fail_details = {
		"renderer_plan_tracks_gap": rg_g08_open and rg_g08_note_present,
		"retail_font_stack_note_mentions_fontstash": "*fontstash" in retail_font_stack_note,
		"retail_font_stack_note_mentions_host_wrappers": "DrawScaledText" in retail_font_stack_note and "MeasureText" in retail_font_stack_note,
		"source_fontstash_impl_present": bool(fontstash_paths),
		"source_fons_error_callback_present": bool(fons_error_paths),
		"ui_draw_text_still_compat_shim": "font = QL_UI_GetScaledFont( fontHandle );" in cl_ui,
		"cgame_draw_text_still_compat_shim": "font = QL_CG_GetScaledFont( fontHandle );" in cl_cgame,
	}
	report["tranches"]["RG-G08"] = _entry(
		"RG-G08",
		"fail",
		"Retail host FontStash text subsystem is still missing from committed source.",
		rg_g08_fail_details,
	)

	rg_g09_open = "## RG-G09" in renderer_plan and "**Status:** Open" in renderer_plan
	rg_g09_note_present = "Renderer font build reproducibility and strict validation remain incomplete" in renderer_plan
	rg_g09_fail_details = {
		"renderer_plan_tracks_gap": rg_g09_open and rg_g09_note_present,
		"font_audit_script_present": FONT_AUDIT_SCRIPT_PATH.exists(),
		"renderer_vcxproj_references_ft2": "..\\ft2\\" in renderer_vcxproj,
		"renderer_vcproj_references_ft2": "..\\ft2\\" in renderer_vcproj,
		"ft2_source_tree_present": (SRC_CODE_ROOT / "ft2").exists(),
		"debug_font_atlas_registered": 'r_debugFontAtlas = ri.Cvar_Get( "r_debugFontAtlas", "0", CVAR_TEMP );' in tr_init,
		"debug_font_atlas_impl_present": bool(unexpected_debug_font_atlas_paths),
		"fontstash_or_fons_source_present": bool(fontstash_paths or fons_error_paths or fons_symbol_paths),
	}
	report["tranches"]["RG-G09"] = _entry(
		"RG-G09",
		"fail",
		"Renderer font build reproducibility and strict text validation remain incomplete.",
		rg_g09_fail_details,
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

	assert runtime_evidence["phase"] == "RG-P6"
	assert runtime_evidence["parity_estimate"] == {"before": 96, "after": 98}
	assert runtime_evidence["warnings"] == []
	assert runtime_evidence["missing_log_markers"] == []
	assert runtime_evidence["main_menu"]["engine_screenshot"]
	assert runtime_evidence["main_menu"]["window_sha256"]
	assert runtime_evidence["map_runtime"]["engine_screenshot"]
	assert runtime_evidence["map_runtime"]["window_sha256"]
	assert runtime_evidence["main_menu"]["window_sha256"] != runtime_evidence["map_runtime"]["window_sha256"]
	assert runtime_evidence["map_runtime"]["map"] == "bloodrun"
	assert runtime_evidence["map_runtime"]["server_seen"] is True
	assert runtime_evidence["map_runtime"]["active_seen"] is True
	assert runtime_evidence["map_runtime"]["shot_logged"] is True


def test_renderer_full_parity_gate_writes_status_artifact() -> None:
	report = _build_renderer_full_parity_gate_report()
	_write_json(RENDERER_FULL_PARITY_GATE_PATH, report)

	assert RENDERER_FULL_PARITY_GATE_PATH.exists()
	assert _read_json(RENDERER_FULL_PARITY_GATE_PATH) == report
	assert report["phase"] == "RG-P6"
	assert report["gap_order"] == list(GAP_ORDER)
	assert set(report["tranches"]) == set(GAP_ORDER)
	assert report["overall_status"] == "fail"
	assert report["non_passing_gap_ids"] == ["RG-G05", "RG-G08", "RG-G09"]
	assert report["summary"] == {
		"passing_count": 6,
		"blocked_count": 0,
		"failing_count": 3,
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
