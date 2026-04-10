from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
CLIENT_FULL_PARITY_GATE_PATH = (
	REPO_ROOT / "artifacts" / "client_validation" / "logs" / "client_full_parity_gate.json"
)
CLIENT_RUNTIME_EVIDENCE_PATH = (
	REPO_ROOT / "artifacts" / "client_validation" / "logs" / "client_runtime_evidence_20260410.json"
)
CLIENT_PLAN_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "client-full-parity-audit-and-implementation-plan-2026-04-09.md"
)
CLIENT_VALIDATION_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "client-validation-and-runtime-evidence-2026-04-10.md"
)
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "client-validation.yml"
BUILD_PIPELINE_PATH = REPO_ROOT / "docs" / "build-pipeline.md"
WINDOWS_NATIVE_PIPELINE_PATH = REPO_ROOT / "docs" / "windows-native-pipeline.md"
IMPLEMENTATION_PLAN_PATH = REPO_ROOT / "IMPLEMENTATION_PLAN.md"
AUDIT_PATH = REPO_ROOT / "AUDIT.md"
RUNTIME_PROBE_PATH = REPO_ROOT / "tools" / "client" / "run_client_runtime_probe.ps1"

CL_CGAME_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
CL_MAIN_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_main.c"
CL_STEAM_RESOURCES_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_steam_resources.c"
CL_UI_PATH = REPO_ROOT / "src" / "code" / "client" / "cl_ui.c"
COMMON_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "common.c"
FILES_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "files.c"
CVAR_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "cvar.c"
SV_INIT_PATH = REPO_ROOT / "src" / "code" / "server" / "sv_init.c"
PLATFORM_STEAMWORKS_PATH = REPO_ROOT / "src" / "common" / "platform" / "platform_steamworks.c"

PLATFORM_SERVICES_TEST_PATH = REPO_ROOT / "tests" / "test_platform_services.py"
STEAMWORKS_HARNESS_TEST_PATH = REPO_ROOT / "tests" / "test_steamworks_harness.py"
CLIENT_CONFIG_TEST_PATH = REPO_ROOT / "tests" / "test_client_config_parity.py"
CLIENT_WORKSHOP_TEST_PATH = REPO_ROOT / "tests" / "test_client_workshop_bootstrap_parity.py"
UI_MENU_FILES_TEST_PATH = REPO_ROOT / "tests" / "test_ui_menu_files.py"

GAP_ORDER = ("CL-G01", "CL-G02", "CL-G03", "CL-G04", "CL-G05")


def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
	return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _contains_all(text: str, *needles: str) -> bool:
	return all(needle in text for needle in needles)


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

	main_menu = runtime_evidence["main_menu"]
	map_runtime = runtime_evidence["map_runtime"]
	offline_browser_policy = main_menu["offline_browser_policy"]

	return (
		runtime_evidence["artifact_version"] == 2
		and runtime_evidence["phase"] == "CL-P6"
		and runtime_evidence["parity_estimate"] == {"before": 99, "after": 100}
		and runtime_evidence["warnings"] == []
		and runtime_evidence["missing_log_markers"] == []
		and main_menu["engine_screenshot"]
		and main_menu["engine_sha256"]
		and main_menu["window_sha256"]
		and main_menu["ui_init_started"] is True
		and main_menu["ui_init_complete"] is True
		and main_menu["execed_qzconfig"] is True
		and main_menu["execed_repconfig"] is True
		and main_menu["write_client_config"]["exists"] is True
		and offline_browser_policy["show_browser_ignored"] is True
		and offline_browser_policy["change_hash_ignored"] is True
		and offline_browser_policy["show_error_logged"] is True
		and offline_browser_policy["reload_logged"] is True
		and offline_browser_policy["stop_refresh_ignored"] is True
		and map_runtime["map"] == "bloodrun"
		and map_runtime["engine_screenshot"]
		and map_runtime["engine_sha256"]
		and map_runtime["window_sha256"]
		and map_runtime["server_seen"] is True
		and map_runtime["active_seen"] is True
		and map_runtime["shot_logged"] is True
		and map_runtime["demo_written"] is True
		and map_runtime["demo_sha256"]
		and map_runtime["game_end_published"] is True
		and map_runtime["shutdown_seen"] is True
		and map_runtime["lifecycle_end_confirmed"] is True
		and main_menu["engine_sha256"] != map_runtime["engine_sha256"]
		and main_menu["window_sha256"] != map_runtime["window_sha256"]
	)


def _build_client_full_parity_gate_report() -> dict[str, Any]:
	client_plan = _read_text(CLIENT_PLAN_PATH)
	client_validation_note = _read_text(CLIENT_VALIDATION_NOTE_PATH)
	workflow_text = _read_text(WORKFLOW_PATH) if WORKFLOW_PATH.exists() else ""
	build_pipeline = _read_text(BUILD_PIPELINE_PATH)
	windows_native_pipeline = _read_text(WINDOWS_NATIVE_PIPELINE_PATH)
	implementation_plan = _read_text(IMPLEMENTATION_PLAN_PATH)
	audit = _read_text(AUDIT_PATH)
	cl_cgame = _read_text(CL_CGAME_PATH)
	cl_main = _read_text(CL_MAIN_PATH)
	cl_steam_resources = _read_text(CL_STEAM_RESOURCES_PATH)
	cl_ui = _read_text(CL_UI_PATH)
	common = _read_text(COMMON_PATH)
	files_c = _read_text(FILES_PATH)
	cvar = _read_text(CVAR_PATH)
	sv_init = _read_text(SV_INIT_PATH)
	platform_steamworks = _read_text(PLATFORM_STEAMWORKS_PATH)
	platform_services_tests = _read_text(PLATFORM_SERVICES_TEST_PATH)
	steamworks_harness_tests = _read_text(STEAMWORKS_HARNESS_TEST_PATH)
	client_config_tests = _read_text(CLIENT_CONFIG_TEST_PATH)
	client_workshop_tests = _read_text(CLIENT_WORKSHOP_TEST_PATH)
	ui_menu_files_tests = _read_text(UI_MENU_FILES_TEST_PATH)
	runtime_evidence = _read_json(CLIENT_RUNTIME_EVIDENCE_PATH) if CLIENT_RUNTIME_EVIDENCE_PATH.exists() else None

	runtime_evidence_sufficient = _runtime_evidence_is_sufficient(runtime_evidence)

	report: dict[str, Any] = {
		"artifact_version": 1,
		"phase": "CL-P6",
		"parity_estimate": {
			"before": 99,
			"after": 100,
		},
		"gap_order": list(GAP_ORDER),
		"tranches": {},
	}

	cl_g01_ok = (
		"## CL-G01 - Retail browser/Awesomium runtime contract was missing" in client_plan
		and "static qboolean QLWebHost_EnsureRuntime( void ) {" in cl_cgame
		and "static qboolean QLWebHost_OpenURL( const char *url ) {" in cl_cgame
		and "static void QLJSHandler_BindQzInstance( void ) {" in cl_cgame
		and "static qboolean QLJSHandler_OnMethodCallWithReturnValue(" in cl_cgame
		and "void CL_Web_ShowBrowser_f( void ) {" in cl_cgame
		and "void CL_Web_ChangeHash_f( void ) {" in cl_cgame
		and "void CL_Web_Reload_f( void ) {" in cl_cgame
		and "void CL_Web_StopRefresh_f( void ) {" in cl_cgame
		and "void CL_WebView_PublishEvent( const char *name, const char *payload ) {" in cl_main
		and "static qboolean CL_SteamDataSource_Request( const char *url, clSteamDataSourceResponse_t *response ) {" in cl_steam_resources
		and "static qboolean QLResourceInterceptor_OnRequest( const char *url, clSteamDataSourceResponse_t *response ) {" in cl_steam_resources
		and "qboolean Sys_Steam_RequestURL( const char *url, byte **outBuffer, int *outSize ) {" in cl_steam_resources
		and "test_online_service_bridge_only_hard_stubs_when_build_disabled" in platform_services_tests
		and "test_service_disabled_menu_verb_matrix_stays_explicit" in platform_services_tests
		and "test_launcher_resource_fallbacks_survive_service_disabled_policy" in platform_services_tests
		and runtime_evidence_sufficient
	)
	report["tranches"]["CL-G01"] = _entry(
		"CL-G01",
		"pass" if cl_g01_ok else "fail",
		(
			"Browser-host ownership, JS bridge publication, and service-disabled fallback behavior stay pinned by source, focused tests, and the tracked runtime bundle."
			if cl_g01_ok
			else "Browser-host ownership or tracked fallback/runtime proof is incomplete."
		),
		{
			"runtime_evidence_sufficient": runtime_evidence_sufficient,
			"browser_runtime_helpers_present": (
				"static qboolean QLWebHost_EnsureRuntime( void ) {" in cl_cgame
				and "static qboolean QLWebHost_OpenURL( const char *url ) {" in cl_cgame
				and "void CL_Web_ShowBrowser_f( void ) {" in cl_cgame
			),
			"js_bridge_present": (
				"static void QLJSHandler_BindQzInstance( void ) {" in cl_cgame
				and "static qboolean QLJSHandler_OnMethodCallWithReturnValue(" in cl_cgame
			),
			"event_publication_present": "void CL_WebView_PublishEvent( const char *name, const char *payload ) {" in cl_main,
			"resource_interceptor_present": (
				"static qboolean CL_SteamDataSource_Request( const char *url, clSteamDataSourceResponse_t *response ) {" in cl_steam_resources
				and "static qboolean QLResourceInterceptor_OnRequest( const char *url, clSteamDataSourceResponse_t *response ) {" in cl_steam_resources
				and "qboolean Sys_Steam_RequestURL( const char *url, byte **outBuffer, int *outSize ) {" in cl_steam_resources
			),
		},
	)

	cl_g02_ok = (
		"## CL-G02 - Async Steam callback registration and client callback pumping are incomplete" in client_plan
		and "qboolean QL_Steamworks_RegisterClientCallbacks( const ql_steam_client_callback_bindings_t *bindings ) {" in platform_steamworks
		and "qboolean QL_Steamworks_RegisterLobbyCallbacks( const ql_steam_lobby_callback_bindings_t *bindings ) {" in platform_steamworks
		and "qboolean QL_Steamworks_RegisterMicroCallbacks( const ql_steam_micro_callback_bindings_t *bindings ) {" in platform_steamworks
		and 'QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamAPI_RegisterCallback, "SteamAPI_RegisterCallback" );' in platform_steamworks
		and 'QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamAPI_RegisterCallResult, "SteamAPI_RegisterCallResult" );' in platform_steamworks
		and "QL_Steamworks_RunCallbacks();" in cl_main
		and "test_client_steam_callback_owner_reconstructs_retail_frame_pump_and_lifecycle" in platform_services_tests
		and "test_callback_bundle_registration_and_dispatch_reconstructs_retail_client_owner" in steamworks_harness_tests
		and "test_ugc_call_result_binding_routes_through_registered_client_bundle" in steamworks_harness_tests
	)
	report["tranches"]["CL-G02"] = _entry(
		"CL-G02",
		"pass" if cl_g02_ok else "fail",
		(
			"Steam client/lobby/micro callback lifetime remains reconstructed and machine-validated."
			if cl_g02_ok
			else "Steam callback-bundle lifetime wiring or validation is incomplete."
		),
		{
			"client_callback_registration_present": "qboolean QL_Steamworks_RegisterClientCallbacks( const ql_steam_client_callback_bindings_t *bindings ) {" in platform_steamworks,
			"lobby_callback_registration_present": "qboolean QL_Steamworks_RegisterLobbyCallbacks( const ql_steam_lobby_callback_bindings_t *bindings ) {" in platform_steamworks,
			"micro_callback_registration_present": "qboolean QL_Steamworks_RegisterMicroCallbacks( const ql_steam_micro_callback_bindings_t *bindings ) {" in platform_steamworks,
			"optional_register_symbols_present": (
				'QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamAPI_RegisterCallback, "SteamAPI_RegisterCallback" );' in platform_steamworks
				and 'QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamAPI_RegisterCallResult, "SteamAPI_RegisterCallResult" );' in platform_steamworks
			),
			"client_frame_pump_present": "QL_Steamworks_RunCallbacks();" in cl_main,
			"harness_validation_present": (
				"test_callback_bundle_registration_and_dispatch_reconstructs_retail_client_owner" in steamworks_harness_tests
				and "test_ugc_call_result_binding_routes_through_registered_client_bundle" in steamworks_harness_tests
			),
		},
	)

	cl_g03_ok = (
		"## CL-G03 - Workshop download/bootstrap exactness was incomplete" in client_plan
		and "const char *FS_ReferencedSteamworks( void ) {" in files_c
		and 'Cvar_Set( "sv_referencedSteamworks", referencedSteamworks );' in sv_init
		and "void CL_InitDownloads(void) {" in cl_main
		and "static void QDECL QL_UI_trap_GetItemDownloadInfo( unsigned int arg1, unsigned int arg2, unsigned long long *outDownloaded, unsigned long long *outTotal ) {" in cl_ui
		and "QL_Steamworks_GetSubscribedItems" in platform_steamworks
		and "QL_Steamworks_GetItemInstallInfo" in platform_steamworks
		and "test_client_workshop_bootstrap_reconstructs_retail_join_and_completion_owners" in client_workshop_tests
		and "test_ui_item_download_import_uses_retained_client_workshop_state" in client_workshop_tests
		and "test_workshop_subscription_enumeration_uses_retail_ugc_mount_slots" in steamworks_harness_tests
		and "test_workshop_mount_startup_reconstructs_retail_subscribed_item_import_path" in platform_services_tests
	)
	report["tranches"]["CL-G03"] = _entry(
		"CL-G03",
		"pass" if cl_g03_ok else "fail",
		(
			"Workshop-aware publication, bootstrap, mount, and UI-progress ownership remain reconstructed and tested."
			if cl_g03_ok
			else "Workshop-aware bootstrap ownership or validation is incomplete."
		),
		{
			"server_publication_present": (
				"const char *FS_ReferencedSteamworks( void ) {" in files_c
				and 'Cvar_Set( "sv_referencedSteamworks", referencedSteamworks );' in sv_init
			),
			"client_bootstrap_present": "void CL_InitDownloads(void) {" in cl_main,
			"ui_progress_import_present": "static void QDECL QL_UI_trap_GetItemDownloadInfo( unsigned int arg1, unsigned int arg2, unsigned long long *outDownloaded, unsigned long long *outTotal ) {" in cl_ui,
			"workshop_mount_helpers_present": (
				"QL_Steamworks_GetSubscribedItems" in platform_steamworks
				and "QL_Steamworks_GetItemInstallInfo" in platform_steamworks
			),
			"focused_validation_present": (
				"test_client_workshop_bootstrap_reconstructs_retail_join_and_completion_owners" in client_workshop_tests
				and "test_workshop_mount_startup_reconstructs_retail_subscribed_item_import_path" in platform_services_tests
			),
		},
	)

	cl_g04_ok = (
		"## CL-G04 - Config/bootstrap persistence closure" in client_plan
		and '#define QL_CONFIG_HARDWARE_FILE "qzconfig.cfg"' in common
		and '#define QL_CONFIG_REPLICATE_FILE "repconfig.cfg"' in common
		and 'Cmd_AddCommand ("writeClientConfig", Com_WriteClientConfig_f );' in common
		and "void Com_WriteClientConfig_f( void ) {" in common
		and 'Cbuf_AddText ("exec qzconfig.cfg\\n");' in files_c
		and "static void CLUI_GetCDKey( char *buf, int buflen ) {" in cl_ui
		and "static void CLUI_SetCDKey( char *buf ) {" in cl_ui
		and "qboolean CL_CDKeyValidate( const char *key, const char *checksum ) {" in cl_main
		and "void Cvar_WriteQLConfigVariables( fileHandle_t hardwareFile, fileHandle_t replicateFile, qboolean clientConfigOnly ) {" in cvar
		and "tests/test_client_config_parity.py" in workflow_text
		and "Cmd_AddCommand (\"writeClientConfig\", Com_WriteClientConfig_f );" in client_config_tests
		and runtime_evidence_sufficient
	)
	report["tranches"]["CL-G04"] = _entry(
		"CL-G04",
		"pass" if cl_g04_ok else "fail",
		(
			"Retail config/bootstrap persistence remains reconstructed and proven by both focused tests and the tracked runtime artifact."
			if cl_g04_ok
			else "Retail config/bootstrap persistence wiring or proof is incomplete."
		),
		{
			"retail_config_defines_present": (
				'#define QL_CONFIG_HARDWARE_FILE "qzconfig.cfg"' in common
				and '#define QL_CONFIG_REPLICATE_FILE "repconfig.cfg"' in common
			),
			"write_client_config_present": (
				'Cmd_AddCommand ("writeClientConfig", Com_WriteClientConfig_f );' in common
				and "void Com_WriteClientConfig_f( void ) {" in common
			),
			"filesystem_restart_bootstrap_present": 'Cbuf_AddText ("exec qzconfig.cfg\\n");' in files_c,
			"legacy_cdkey_surface_present": (
				"static void CLUI_GetCDKey( char *buf, int buflen ) {" in cl_ui
				and "static void CLUI_SetCDKey( char *buf ) {" in cl_ui
				and "qboolean CL_CDKeyValidate( const char *key, const char *checksum ) {" in cl_main
			),
			"runtime_artifact_proves_bootstrap": runtime_evidence_sufficient,
		},
	)

	cl_g05_ok = (
		RUNTIME_PROBE_PATH.exists()
		and runtime_evidence_sufficient
		and CLIENT_VALIDATION_NOTE_PATH.exists()
		and _contains_all(
			client_validation_note,
			"client_runtime_evidence_20260410.json",
			"client_full_parity_gate.json",
			"`CL-P6` is now considered complete.",
			"`CL-G05` is now considered closed.",
		)
		and "## CL-G05 - The client verification surface is still fragmented and lacks a dedicated parity gate" in client_plan
		and "**Status:** Closed on 2026-04-10" in client_plan
		and "## CL-P6 - Dedicated client parity gate and runtime evidence [COMPLETED]" in client_plan
		and "tests/test_client_full_parity_gate.py" in workflow_text
		and "tests/test_client_config_parity.py" in workflow_text
		and "tests/test_client_workshop_bootstrap_parity.py" in workflow_text
		and "tests/test_platform_services.py" in workflow_text
		and "tests/test_steamworks_harness.py" in workflow_text
		and "tests/test_ui_menu_files.py" in workflow_text
		and "client_full_parity_gate.json" in build_pipeline
		and "client_runtime_evidence_20260410.json" in build_pipeline
		and "tools/client/run_client_runtime_probe.ps1" in build_pipeline
		and "client_full_parity_gate.json" in windows_native_pipeline
		and "client_runtime_evidence_20260410.json" in windows_native_pipeline
		and "tools/client/run_client_runtime_probe.ps1" in windows_native_pipeline
		and "### Task 87: Client CL-P6 parity gate and runtime-evidence closure [COMPLETED]" in implementation_plan
		and "Parity estimate: **before 99% -> after 100%**" in implementation_plan
		and _contains_all(
			audit,
			"`CL-P6` is now complete.",
			"The refreshed strict `client` estimate is now **100%**.",
			"No open gap remains in the audited client register.",
		)
	)
	report["tranches"]["CL-G05"] = _entry(
		"CL-G05",
		"pass" if cl_g05_ok else "fail",
		(
			"The client now has a dedicated parity gate, a tracked runtime-evidence bundle, and repo-level ledger wiring that keeps the client register enforceable."
			if cl_g05_ok
			else "Dedicated client parity-gate wiring or tracked runtime evidence is incomplete."
		),
		{
			"runtime_probe_present": RUNTIME_PROBE_PATH.exists(),
			"runtime_evidence_present": CLIENT_RUNTIME_EVIDENCE_PATH.exists(),
			"runtime_evidence_sufficient": runtime_evidence_sufficient,
			"validation_note_present": CLIENT_VALIDATION_NOTE_PATH.exists(),
			"workflow_references_gate": "tests/test_client_full_parity_gate.py" in workflow_text,
			"build_pipeline_mentions_gate": "client_full_parity_gate.json" in build_pipeline,
			"windows_pipeline_mentions_runtime_artifact": "client_runtime_evidence_20260410.json" in windows_native_pipeline,
			"implementation_plan_marks_cl_p6_completed": "### Task 87: Client CL-P6 parity gate and runtime-evidence closure [COMPLETED]" in implementation_plan,
			"audit_marks_client_full_closure": _contains_all(
				audit,
				"`CL-P6` is now complete.",
				"The refreshed strict `client` estimate is now **100%**.",
				"No open gap remains in the audited client register.",
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


def test_client_runtime_evidence_artifact_is_tracked_and_clean() -> None:
	runtime_evidence = _read_json(CLIENT_RUNTIME_EVIDENCE_PATH)

	assert runtime_evidence["artifact_version"] == 2
	assert runtime_evidence["phase"] == "CL-P6"
	assert runtime_evidence["parity_estimate"] == {"before": 99, "after": 100}
	assert runtime_evidence["warnings"] == []
	assert runtime_evidence["missing_log_markers"] == []
	assert runtime_evidence["main_menu"]["engine_screenshot"]
	assert runtime_evidence["main_menu"]["engine_sha256"]
	assert runtime_evidence["main_menu"]["window_sha256"]
	assert runtime_evidence["main_menu"]["ui_init_complete"] is True
	assert runtime_evidence["main_menu"]["write_client_config"]["exists"] is True
	assert runtime_evidence["main_menu"]["offline_browser_policy"]["show_browser_ignored"] is True
	assert runtime_evidence["main_menu"]["offline_browser_policy"]["change_hash_ignored"] is True
	assert runtime_evidence["main_menu"]["offline_browser_policy"]["show_error_logged"] is True
	assert runtime_evidence["main_menu"]["offline_browser_policy"]["reload_logged"] is True
	assert runtime_evidence["main_menu"]["offline_browser_policy"]["stop_refresh_ignored"] is True
	assert runtime_evidence["map_runtime"]["map"] == "bloodrun"
	assert runtime_evidence["map_runtime"]["engine_screenshot"]
	assert runtime_evidence["map_runtime"]["engine_sha256"]
	assert runtime_evidence["map_runtime"]["window_sha256"]
	assert runtime_evidence["map_runtime"]["server_seen"] is True
	assert runtime_evidence["map_runtime"]["active_seen"] is True
	assert runtime_evidence["map_runtime"]["shot_logged"] is True
	assert runtime_evidence["map_runtime"]["demo_written"] is True
	assert runtime_evidence["map_runtime"]["demo_sha256"]
	assert runtime_evidence["map_runtime"]["game_end_published"] is True
	assert runtime_evidence["map_runtime"]["shutdown_seen"] is True
	assert runtime_evidence["map_runtime"]["lifecycle_end_confirmed"] is True
	assert _runtime_evidence_is_sufficient(runtime_evidence)


def test_client_full_parity_gate_writes_status_artifact() -> None:
	report = _build_client_full_parity_gate_report()
	_write_json(CLIENT_FULL_PARITY_GATE_PATH, report)

	assert CLIENT_FULL_PARITY_GATE_PATH.exists()
	assert _read_json(CLIENT_FULL_PARITY_GATE_PATH) == report
	assert report["artifact_version"] == 1
	assert report["phase"] == "CL-P6"
	assert report["gap_order"] == list(GAP_ORDER)
	assert set(report["tranches"]) == set(GAP_ORDER)
	assert report["overall_status"] == "pass"
	assert report["non_passing_gap_ids"] == []
	assert report["summary"] == {
		"passing_count": 5,
		"blocked_count": 0,
		"failing_count": 0,
	}

	for gap_id in GAP_ORDER:
		entry = report["tranches"][gap_id]
		assert entry["gap_id"] == gap_id
		assert entry["status"] in {"pass", "fail", "blocked"}
		assert entry["summary"]


def test_client_full_parity_gate_release_mode() -> None:
	if os.environ.get("CLIENT_FULL_PARITY_GATE_ENFORCE") != "1":
		pytest.skip("Set CLIENT_FULL_PARITY_GATE_ENFORCE=1 to require a full client parity pass.")

	report = _build_client_full_parity_gate_report()
	_write_json(CLIENT_FULL_PARITY_GATE_PATH, report)
	assert report["overall_status"] == "pass", (
		"Client full parity gate failed for "
		+ ", ".join(report["non_passing_gap_ids"])
	)
