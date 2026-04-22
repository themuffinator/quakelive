from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from tests._shared import REPO_ROOT, contains_all as _contains_all, read_json as _read_json, write_json as _write_json

RETAIL_MODULE_PARITY_GATE_PATH = (
	REPO_ROOT / "artifacts" / "module_validation" / "logs" / "retail_module_parity_gate.json"
)
RETAIL_MODULE_RUNTIME_EVIDENCE_ARTIFACT_NAME = "retail_module_runtime_evidence_latest.json"
RETAIL_MODULE_RUNTIME_EVIDENCE_PATH = (
	REPO_ROOT / "artifacts" / "module_validation" / "logs" / RETAIL_MODULE_RUNTIME_EVIDENCE_ARTIFACT_NAME
)
RETAIL_MODULE_PLAN_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "game-module-parity-audit-and-implementation-plan-2026-04-09.md"
)
CURRENT_MODULE_AUDIT_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "game-module-parity-audit-and-implementation-plan-2026-04-10.md"
)
IMPLEMENTATION_PLAN_PATH = REPO_ROOT / "IMPLEMENTATION_PLAN.md"
AUDIT_PATH = REPO_ROOT / "AUDIT.md"
UI_PLAN_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "ui-full-parity-audit-and-implementation-plan-2026-04-05.md"
)
NATIVE_PIPELINE_PATH = REPO_ROOT / "docs" / "architecture" / "native-pipeline.md"
BUILD_PIPELINE_PATH = REPO_ROOT / "docs" / "build-pipeline.md"
WOW64_DOC_PATH = REPO_ROOT / "docs" / "testing" / "wow64-smoketest.md"
WOW64_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "wow64-smoketest.ps1"
SCRIPTING_GUIDE_PATH = REPO_ROOT / "docs" / "ui" / "scripting-guide.md"
RUNTIME_PROBE_PATH = REPO_ROOT / "tools" / "modules" / "run_retail_module_runtime_probe.ps1"
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "module-validation.yml"

VM_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "vm.c"
SV_GAME_PATH = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
CL_UI_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_ui.c"
CL_CGAME_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
FILES_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "files.c"
CL_WEBPAK_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_webpak.c"
CL_STEAM_RESOURCES_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_steam_resources.c"
PLATFORM_SERVICES_TEST_PATH = REPO_ROOT / "tests" / "test_platform_services.py"

GAP_ORDER = ("GMR-G01", "GMR-G02", "GMR-G05")

def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8")

def _entry(gap_id: str, status: str, summary: str, details: dict[str, Any]) -> dict[str, Any]:
	return {
		"gap_id": gap_id,
		"status": status,
		"summary": summary,
		"details": details,
	}

def _runtime_evidence_is_sufficient(runtime_evidence: dict[str, Any] | None) -> bool:
	if runtime_evidence is None:
		return False

	before = float(runtime_evidence["parity_estimate"]["before"])
	after = float(runtime_evidence["parity_estimate"]["after"])
	main_menu = runtime_evidence["main_menu"]
	map_runtime = runtime_evidence["map_runtime"]
	trace_stats = map_runtime["trace_stats"]
	bounded_owner_items = runtime_evidence.get("bounded_owner_items", [])
	renderer_owner_blocker = map_runtime.get("renderer_owner_blocker", "")
	renderer_bounded = any(
		item.get("owner") == "renderer" and item.get("message", "").startswith("R_")
		for item in bounded_owner_items
	)
	renderer_drop_bounded = renderer_owner_blocker.startswith("R_LoadMD3:")
	renderer_font_livelock_bounded = renderer_owner_blocker.startswith("R_fonsErrorCallback:")
	clean_runtime = (
		runtime_evidence["warnings"] == []
		and runtime_evidence["missing_log_markers"] == []
		and map_runtime["engine_screenshot"]
		and map_runtime["active_seen"] is True
		and map_runtime["frame_ready"] is True
		and map_runtime["restart_seen"] is True
		and map_runtime["shot_logged"] is True
		and trace_stats["cgame_call_count"] >= 16
		and trace_stats["qagame_create_count"] >= 2
		and trace_stats["qagame_free_count"] >= 2
	)
	bounded_runtime = (
		renderer_bounded
		and renderer_owner_blocker.startswith("R_")
		and map_runtime["active_seen"] is False
		and map_runtime["frame_ready"] is False
		and map_runtime["restart_seen"] is False
		and trace_stats["cgame_create_count"] >= 1
		and trace_stats["cgame_call_count"] >= 8
		and trace_stats["qagame_create_count"] >= 1
		and trace_stats["qagame_call_count"] >= 16
		and (
			(
				renderer_drop_bounded
				and trace_stats["cgame_free_count"] >= 1
				and trace_stats["qagame_free_count"] >= 1
			)
			or renderer_font_livelock_bounded
		)
	)

	return (
		runtime_evidence["phase"] == "GMR-P1"
		and abs(before - 97.1) < 0.01
		and abs(after - 98.0) < 0.01
		and main_menu["engine_screenshot"]
		and main_menu["ui_init_complete"] is True
		and main_menu["retail_ui_load_seen"] is True
		and map_runtime["map"] == "catalyst"
		and map_runtime["server_seen"] is True
		and map_runtime["retail_cgame_load_seen"] is True
		and map_runtime["retail_qagame_load_seen"] is True
		and (trace_stats["cgame_free_count"] >= 1 or renderer_font_livelock_bounded)
		and (clean_runtime or bounded_runtime)
	)

def _build_retail_module_parity_gate_report() -> dict[str, Any]:
	retail_module_plan = _read_text(RETAIL_MODULE_PLAN_PATH)
	current_module_audit = _read_text(CURRENT_MODULE_AUDIT_PATH)
	implementation_plan = _read_text(IMPLEMENTATION_PLAN_PATH)
	audit = _read_text(AUDIT_PATH)
	ui_plan = _read_text(UI_PLAN_PATH)
	native_pipeline = _read_text(NATIVE_PIPELINE_PATH)
	build_pipeline = _read_text(BUILD_PIPELINE_PATH)
	wow64_doc = _read_text(WOW64_DOC_PATH)
	wow64_script = _read_text(WOW64_SCRIPT_PATH)
	scripting_guide = _read_text(SCRIPTING_GUIDE_PATH)
	runtime_probe = _read_text(RUNTIME_PROBE_PATH)
	workflow_text = _read_text(WORKFLOW_PATH) if WORKFLOW_PATH.exists() else ""
	vm = _read_text(VM_PATH)
	sv_game = _read_text(SV_GAME_PATH)
	cl_ui = _read_text(CL_UI_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	files_c = _read_text(FILES_PATH)
	cl_webpak = _read_text(CL_WEBPAK_PATH)
	steam_resources = _read_text(CL_STEAM_RESOURCES_PATH)
	platform_tests = _read_text(PLATFORM_SERVICES_TEST_PATH)
	runtime_evidence = _read_json(RETAIL_MODULE_RUNTIME_EVIDENCE_PATH) if RETAIL_MODULE_RUNTIME_EVIDENCE_PATH.exists() else None

	runtime_evidence_sufficient = _runtime_evidence_is_sufficient(runtime_evidence)
	wow64_ui_export_probe_present = (
		"Name = 'uix86.dll'" in wow64_script
		and "Source = Join-Path $RepoRoot 'assets/quakelive/baseq3/uix86.dll'" in wow64_script
		and "FallbackSource = Join-Path $RepoRoot 'build/win32/Debug/bin/baseq3/uix86.dll'" in wow64_script
	)

	gmr_g01_ok = (
		RUNTIME_PROBE_PATH.exists()
		and RETAIL_MODULE_RUNTIME_EVIDENCE_ARTIFACT_NAME in runtime_probe
		and "map $MapName ffa" in runtime_probe
		and runtime_evidence_sufficient
		and "tests/test_game_module_retail_parity_gate.py" in workflow_text
		and "tests/test_platform_services.py" in workflow_text
		and "tools/modules/run_retail_module_runtime_probe.ps1" in workflow_text
		and "retail_module_parity_gate.json" in build_pipeline
		and RETAIL_MODULE_RUNTIME_EVIDENCE_ARTIFACT_NAME in build_pipeline
		and "tools/modules/run_retail_module_runtime_probe.ps1" in native_pipeline
		and RETAIL_MODULE_RUNTIME_EVIDENCE_ARTIFACT_NAME in native_pipeline
		and wow64_ui_export_probe_present
		and "Loads `qagamex86.dll`, `cgamex86.dll`, and `uix86.dll`, probing for `dllEntry` and `vmMain`" in wow64_doc
		and "Q_strncpyz( sv_gameClientConnectDenied, denied, sizeof( sv_gameClientConnectDenied ) );" in sv_game
		and "VM_Call( gvm, GAME_SHUTDOWN, qtrue );" in sv_game
		and "gvm = VM_Restart( gvm );" in sv_game
		and "VM_Free( vm );" in vm
		and 'vm = VM_Create( name, systemCall, VMI_NATIVE, dllImports, dllApiVersion );' in vm
		and "VM_Call( cgvm, CG_SHUTDOWN );" in cl_cgame
		and "VM_Free( cgvm );" in cl_cgame
		and "VM_Call( uivm, UI_SHUTDOWN );" in cl_ui
		and "VM_Free( uivm );" in cl_ui
		and "## GMR-G01: Closed retail DLL host validation" in retail_module_plan
	)

	gmr_g02_ok = (
		"FS_OnlineServicesEnabled" not in files_c
		and 'Com_sprintf( outPath, outSize, "%s/%s", fs_webpath->string, localPath );' in files_c
		and "return ( cl_webPak != NULL || cl_webDataPak.loaded );" in cl_webpak
		and "if ( CL_WebDataPak_Load( pakPath ) ) {" in cl_webpak
		and 'Com_Printf( "web.pak datapack mounted from %s\\n", pakPath );' in cl_webpak
		and "CL_OnlineServicesEnabled()" not in cl_webpak
		and "if ( CL_SteamResources_IsSteamURL( url ) ) {" in steam_resources
		and "if ( !CL_SteamServicesEnabled() ) {" in steam_resources
		and "UI: launcher resource request stubbed" not in steam_resources
		and "Launcher backend disabled by build/runtime policy" not in steam_resources
		and "test_launcher_resource_bridge_reconstructs_retail_web_fallback_owner" in platform_tests
		and "test_launcher_resource_fallbacks_survive_service_disabled_policy" in platform_tests
		and "Launcher-compatible local resource loads stay available even when live online services are disabled" in scripting_guide
		and "## GMR-G02: Retail launcher/bootstrap ownership still leaks into module parity [CLOSED 2026-04-09]" in retail_module_plan
	)

	gmr_g05_ok = (
		"| `cgame` suite | `170 passed` |" in retail_module_plan
		and "| `qagame` suite | `91 passed`, `5 skipped` |" in retail_module_plan
		and "| `ui` suite + fs/vote checks | `49 passed`, `6 skipped` |" in retail_module_plan
		and "| shared platform-service seam | `41 passed` |" in retail_module_plan
		and "- Current strict retail module parity estimate: **`100%`**" in retail_module_plan
		and "### GMR-G05: Module parity documentation is still scope-collapsed in places [CLOSED 2026-04-09]" in retail_module_plan
		and "### GMR-P5: Reconcile the parity ledgers and publish final evidence [COMPLETED]" in retail_module_plan
		and _contains_all(
			current_module_audit,
			"- Current strict retail module parity estimate: **`100%`**",
			"### GMR-P8: Final module-ledger and runtime-evidence reconciliation [COMPLETED]",
			"All planned current-worktree module closure phases are now complete.",
		)
		and _contains_all(
			current_module_audit,
			"| `cgame` suite | `170 passed` |",
			"| `qagame` suite + lifecycle | `91 passed`, `5 skipped` |",
			"| `ui` suite + fs/vote checks | `58 passed`, `2 skipped` |",
			"| shared platform-service seam + module gate | `57 passed`, `1 skipped` |",
		)
		and _contains_all(
			audit,
			"`GMR-P7` is now complete",
			"`GMR-P8` is now complete",
			"supporting pipeline notes now all point at the",
			"same closure state again",
			"**100%** in the refreshed module report.",
		)
		and "### Task 31: Strict retail game-module parity closure [COMPLETED]" in implementation_plan
		and "### Task 104: Strict retail game-module final ledger and runtime-evidence reconciliation [COMPLETED]" in implementation_plan
		and _contains_all(
			build_pipeline,
			"tests/test_platform_services.py",
			"tests/test_game_module_retail_parity_gate.py",
			"retail_module_parity_gate.json",
			"`GMR-P8`",
			"`GMR-P5`",
			"closure artifact",
			RETAIL_MODULE_RUNTIME_EVIDENCE_ARTIFACT_NAME,
		)
		and _contains_all(
			native_pipeline,
			"tests/test_game_module_retail_parity_gate.py",
			"retail_module_parity_gate.json",
			"`GMR-P8`",
			"`GMR-P5`",
			RETAIL_MODULE_RUNTIME_EVIDENCE_ARTIFACT_NAME,
		)
		and RETAIL_MODULE_RUNTIME_EVIDENCE_ARTIFACT_NAME in current_module_audit
		and "combined strict-retail module audit now also treats the audited offline UI launcher/resource slice as closed" in ui_plan
	)

	report: dict[str, Any] = {
		"artifact_version": 3,
		"phase": "GMR-P8",
		"parity_estimate": {
			"before": 100.0,
			"after": 100.0,
		},
		"gap_order": list(GAP_ORDER),
		"tranches": {},
	}

	report["tranches"]["GMR-G01"] = _entry(
		"GMR-G01",
		"pass" if gmr_g01_ok else "fail",
		(
			"Retail DLL host validation remains backed by the tracked runtime probe, static edge-contract checks, and the archived runtime artifact."
			if gmr_g01_ok
			else "Retail DLL host validation wiring or evidence is incomplete."
		),
		{
			"runtime_probe_present": RUNTIME_PROBE_PATH.exists(),
			"runtime_probe_mentions_latest_alias": RETAIL_MODULE_RUNTIME_EVIDENCE_ARTIFACT_NAME in runtime_probe,
			"runtime_probe_uses_current_map_contract": "map $MapName ffa" in runtime_probe,
			"runtime_evidence_present": RETAIL_MODULE_RUNTIME_EVIDENCE_PATH.exists(),
			"runtime_evidence_sufficient": runtime_evidence_sufficient,
			"workflow_references_gate": "tests/test_game_module_retail_parity_gate.py" in workflow_text,
			"workflow_runs_platform_services": "tests/test_platform_services.py" in workflow_text,
			"workflow_mentions_runtime_probe": "tools/modules/run_retail_module_runtime_probe.ps1" in workflow_text,
			"build_pipeline_mentions_runtime_artifact": RETAIL_MODULE_RUNTIME_EVIDENCE_ARTIFACT_NAME in build_pipeline,
			"native_pipeline_mentions_runtime_artifact": RETAIL_MODULE_RUNTIME_EVIDENCE_ARTIFACT_NAME in native_pipeline,
			"wow64_ui_export_probe_present": wow64_ui_export_probe_present,
			"retail_plan_marks_gap_closed": "## GMR-G01: Closed retail DLL host validation" in retail_module_plan,
		},
	)

	report["tranches"]["GMR-G02"] = _entry(
		"GMR-G02",
		"pass" if gmr_g02_ok else "fail",
		(
			"Audited offline launcher-resource fallbacks stay available without enabling live services, and the closure is locked by the focused platform-service regression surface."
			if gmr_g02_ok
			else "Offline launcher-resource fallback closure is incomplete or no longer reflected in source/tests."
		),
		{
			"filesystem_gate_removed": "FS_OnlineServicesEnabled" not in files_c,
			"webpak_remains_available_offline": "return ( cl_webPak != NULL || cl_webDataPak.loaded );" in cl_webpak and "CL_OnlineServicesEnabled()" not in cl_webpak,
			"datapack_bridge_present": "if ( CL_WebDataPak_Load( pakPath ) ) {" in cl_webpak and 'Com_Printf( "web.pak datapack mounted from %s\\n", pakPath );' in cl_webpak,
			"steam_only_uri_gate_preserved": "if ( CL_SteamResources_IsSteamURL( url ) ) {" in steam_resources and "if ( !CL_SteamServicesEnabled() ) {" in steam_resources,
			"platform_service_coverage_present": (
				"test_launcher_resource_bridge_reconstructs_retail_web_fallback_owner" in platform_tests
				and "test_launcher_resource_fallbacks_survive_service_disabled_policy" in platform_tests
			),
			"scripting_guide_mentions_offline_resource_fallbacks": "Launcher-compatible local resource loads stay available even when live online services are disabled" in scripting_guide,
			"retail_plan_marks_gap_closed": "## GMR-G02: Retail launcher/bootstrap ownership still leaks into module parity [CLOSED 2026-04-09]" in retail_module_plan,
		},
	)

	report["tranches"]["GMR-G05"] = _entry(
		"GMR-G05",
		"pass" if gmr_g05_ok else "fail",
		(
			"Parity ledgers, the final module gate, and the pipeline notes now agree on a fully closed strict-retail game-module register."
			if gmr_g05_ok
			else "Parity ledgers or closure notes still disagree on the final strict-retail module state."
		),
		{
			"retail_plan_current_parity_is_100": "- Current strict retail module parity estimate: **`100%`**" in retail_module_plan,
			"retail_plan_marks_gmr_g05_closed": "### GMR-G05: Module parity documentation is still scope-collapsed in places [CLOSED 2026-04-09]" in retail_module_plan,
			"retail_plan_marks_gmr_p5_completed": "### GMR-P5: Reconcile the parity ledgers and publish final evidence [COMPLETED]" in retail_module_plan,
			"current_audit_parity_is_100": "- Current strict retail module parity estimate: **`100%`**" in current_module_audit,
			"current_audit_marks_gmr_p8_completed": "### GMR-P8: Final module-ledger and runtime-evidence reconciliation [COMPLETED]" in current_module_audit,
			"audit_marks_gmr_p7_and_gmr_p8_completed": _contains_all(
				audit,
				"`GMR-P7` is now complete",
				"`GMR-P8` is now complete",
				"same closure state again",
			),
			"implementation_plan_marks_task_31_completed": "### Task 31: Strict retail game-module parity closure [COMPLETED]" in implementation_plan,
			"implementation_plan_marks_task_104_completed": "### Task 104: Strict retail game-module final ledger and runtime-evidence reconciliation [COMPLETED]" in implementation_plan,
			"pipeline_docs_reference_current_closure": _contains_all(
				build_pipeline,
				"tests/test_platform_services.py",
				"tests/test_game_module_retail_parity_gate.py",
				"retail_module_parity_gate.json",
				"`GMR-P8`",
				"`GMR-P5`",
				"closure artifact",
				RETAIL_MODULE_RUNTIME_EVIDENCE_ARTIFACT_NAME,
			) and _contains_all(
				native_pipeline,
				"tests/test_game_module_retail_parity_gate.py",
				"retail_module_parity_gate.json",
				"`GMR-P8`",
				"`GMR-P5`",
				RETAIL_MODULE_RUNTIME_EVIDENCE_ARTIFACT_NAME,
			),
			"ui_plan_marks_combined_closure_alignment": "combined strict-retail module audit now also treats the audited offline UI launcher/resource slice as closed" in ui_plan,
			"historical_suite_counts_preserved": (
				"| `cgame` suite | `170 passed` |" in retail_module_plan
				and "| `qagame` suite | `91 passed`, `5 skipped` |" in retail_module_plan
				and "| `ui` suite + fs/vote checks | `49 passed`, `6 skipped` |" in retail_module_plan
				and "| shared platform-service seam | `41 passed` |" in retail_module_plan
			),
			"current_suite_counts_synced": (
				"| `cgame` suite | `170 passed` |" in current_module_audit
				and "| `qagame` suite + lifecycle | `91 passed`, `5 skipped` |" in current_module_audit
				and "| `ui` suite + fs/vote checks | `58 passed`, `2 skipped` |" in current_module_audit
				and "| shared platform-service seam + module gate | `57 passed`, `1 skipped` |" in current_module_audit
			),
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

def test_retail_module_runtime_evidence_artifact_is_tracked_and_clean() -> None:
	runtime_evidence = _read_json(RETAIL_MODULE_RUNTIME_EVIDENCE_PATH)

	assert runtime_evidence["phase"] == "GMR-P1"
	assert float(runtime_evidence["parity_estimate"]["before"]) == pytest.approx(97.1)
	assert float(runtime_evidence["parity_estimate"]["after"]) == pytest.approx(98.0)
	assert runtime_evidence["main_menu"]["engine_screenshot"]
	assert runtime_evidence["main_menu"]["ui_init_complete"] is True
	assert runtime_evidence["main_menu"]["retail_ui_load_seen"] is True
	assert runtime_evidence["map_runtime"]["map"] == "catalyst"
	assert runtime_evidence["map_runtime"]["server_seen"] is True
	assert runtime_evidence["map_runtime"]["retail_cgame_load_seen"] is True
	assert runtime_evidence["map_runtime"]["retail_qagame_load_seen"] is True
	assert runtime_evidence["map_runtime"]["trace_stats"]["cgame_create_count"] >= 1
	assert runtime_evidence["map_runtime"]["trace_stats"]["qagame_create_count"] >= 1
	renderer_owner_blocker = runtime_evidence["map_runtime"]["renderer_owner_blocker"]
	if not renderer_owner_blocker.startswith("R_fonsErrorCallback:"):
		assert runtime_evidence["map_runtime"]["trace_stats"]["cgame_free_count"] >= 1
		assert runtime_evidence["map_runtime"]["trace_stats"]["qagame_free_count"] >= 1
	assert _runtime_evidence_is_sufficient(runtime_evidence)

def test_retail_module_parity_gate_writes_status_artifact() -> None:
	report = _build_retail_module_parity_gate_report()
	_write_json(RETAIL_MODULE_PARITY_GATE_PATH, report)

	assert RETAIL_MODULE_PARITY_GATE_PATH.exists()
	assert _read_json(RETAIL_MODULE_PARITY_GATE_PATH) == report
	assert report["artifact_version"] == 3
	assert report["phase"] == "GMR-P8"
	assert report["gap_order"] == list(GAP_ORDER)
	assert set(report["tranches"]) == set(GAP_ORDER)
	assert report["overall_status"] == "pass"
	assert report["non_passing_gap_ids"] == []
	assert report["summary"] == {
		"passing_count": 3,
		"blocked_count": 0,
		"failing_count": 0,
	}

	for gap_id in GAP_ORDER:
		entry = report["tranches"][gap_id]
		assert entry["gap_id"] == gap_id
		assert entry["status"] in {"pass", "fail", "blocked"}
		assert entry["summary"]

def test_retail_module_parity_gate_release_mode() -> None:
	if os.environ.get("RETAIL_MODULE_PARITY_GATE_ENFORCE") != "1":
		pytest.skip("Set RETAIL_MODULE_PARITY_GATE_ENFORCE=1 to require a full retail-module parity pass.")

	report = _build_retail_module_parity_gate_report()
	_write_json(RETAIL_MODULE_PARITY_GATE_PATH, report)
	assert report["overall_status"] == "pass", (
		"Retail module parity gate failed for "
		+ ", ".join(report["non_passing_gap_ids"])
	)
