from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from tests._shared import (
	REPO_ROOT,
	contains_all as _contains_all,
	read_json as _read_json,
	section_text_for_id as _section_text_for_id,
	write_json as _write_json,
)

ENGINE_HOST_SUPPORT_FULL_PARITY_GATE_PATH = (
	REPO_ROOT / "artifacts" / "engine_host_support_validation" / "logs" / "engine_host_support_full_parity_gate.json"
)
ENGINE_HOST_SUPPORT_RUNTIME_EVIDENCE_PATH = (
	REPO_ROOT / "artifacts" / "engine_host_support_validation" / "logs" / "engine_host_support_runtime_evidence_20260410.json"
)
ENGINE_HOST_SUPPORT_PLAN_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "engine-host-support-full-parity-audit-and-implementation-plan-2026-04-10.md"
)
ENGINE_HOST_SUPPORT_VALIDATION_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "engine-host-support-validation-and-runtime-evidence-2026-04-10.md"
)
BOTLIB_INTERNAL_AUDIT_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md"
)
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "engine-host-support-validation.yml"
BUILD_PIPELINE_PATH = REPO_ROOT / "docs" / "build-pipeline.md"
WINDOWS_NATIVE_PIPELINE_PATH = REPO_ROOT / "docs" / "windows-native-pipeline.md"
IMPLEMENTATION_PLAN_PATH = REPO_ROOT / "IMPLEMENTATION_PLAN.md"
AUDIT_PATH = REPO_ROOT / "AUDIT.md"
AUTHENTICATION_NOTE_PATH = REPO_ROOT / "docs" / "platform" / "authentication.md"
TOOLCHAIN_MATRIX_PATH = REPO_ROOT / "docs" / "platform" / "toolchain-matrix.md"

PLATFORM_CONFIG_PATH = REPO_ROOT / "src" / "common" / "platform" / "platform_config.h"
PLATFORM_SERVICES_PATH = REPO_ROOT / "src" / "common" / "platform" / "platform_services.c"
PLATFORM_BACKEND_OPEN_STEAM_PATH = (
	REPO_ROOT / "src" / "common" / "platform" / "backends" / "platform_backend_open_steam.c"
)
PLATFORM_BACKEND_STEAMWORKS_PATH = (
	REPO_ROOT / "src" / "common" / "platform" / "backends" / "platform_backend_steamworks.c"
)
WIN_MAIN_PATH = REPO_ROOT / "src" / "code" / "win32" / "win_main.c"
WIN_CLIPBOARD_SHARED_PATH = REPO_ROOT / "src" / "code" / "win32" / "win_clipboard_shared.h"
WIN_INPUT_PATH = REPO_ROOT / "src" / "code" / "win32" / "win_input.c"
WIN_WNDPROC_PATH = REPO_ROOT / "src" / "code" / "win32" / "win_wndproc.c"
WIN_RAWINPUT_SHARED_PATH = REPO_ROOT / "src" / "code" / "win32" / "win_rawinput_shared.h"
WIN_SYSCON_PATH = REPO_ROOT / "src" / "code" / "win32" / "win_syscon.c"
UNIX_MAIN_PATH = REPO_ROOT / "src" / "code" / "unix" / "unix_main.c"
NULL_CLIENT_PATH = REPO_ROOT / "src" / "code" / "null" / "null_client.c"
NULL_INPUT_PATH = REPO_ROOT / "src" / "code" / "null" / "null_input.c"
BOTLIB_ROOT = REPO_ROOT / "src" / "code" / "botlib"
BOTLIB_INTERFACE_PATH = BOTLIB_ROOT / "be_interface.c"

COMPILER_SUPPORT_PATH = REPO_ROOT / "tests" / "compiler_support.py"
INPUT_TRANSLATION_TEST_PATH = REPO_ROOT / "tests" / "test_input_translation.py"
PLATFORM_SERVICES_TEST_PATH = REPO_ROOT / "tests" / "test_platform_services.py"
STEAMWORKS_HARNESS_TEST_PATH = REPO_ROOT / "tests" / "test_steamworks_harness.py"
RENDERER_WIN32_HOST_GLUE_TEST_PATH = REPO_ROOT / "tests" / "test_renderer_win32_host_glue_parity.py"
BOT_RESOURCE_LOADING_TEST_PATH = REPO_ROOT / "tests" / "test_bot_resource_loading.py"
BOTLIB_INTERNAL_HARNESS_PATH = REPO_ROOT / "tests" / "botlib_internal_harness.c"
BOTLIB_INTERNAL_TEST_PATH = REPO_ROOT / "tests" / "test_botlib_internal_parity.py"
WIN32_CLIPBOARD_TEST_PATH = REPO_ROOT / "tests" / "test_win32_clipboard_parity.py"
WIN32_RAW_INPUT_TEST_PATH = REPO_ROOT / "tests" / "test_win32_raw_input_parity.py"

GAP_ORDER = ("EH-G01", "EH-G02", "EH-G03", "EH-G04", "EH-G05", "EH-G06")
STRICT_RETAIL_GAP_IDS = ("EH-G01", "EH-G02", "EH-G04", "EH-G06")
COMPATIBILITY_ONLY_GAP_IDS = ("EH-G03", "EH-G05")
GAP_CLASSIFICATIONS = {
	"EH-G01": {
		"classification": "strict-retail",
		"counts_toward_strict_retail_score": True,
		"closure_phase": "EH-P2",
	},
	"EH-G02": {
		"classification": "strict-retail",
		"counts_toward_strict_retail_score": True,
		"closure_phase": "EH-P3",
	},
	"EH-G03": {
		"classification": "compatibility-only",
		"counts_toward_strict_retail_score": False,
		"closure_phase": "EH-P5",
	},
	"EH-G04": {
		"classification": "strict-retail",
		"counts_toward_strict_retail_score": True,
		"closure_phase": "EH-P4",
	},
	"EH-G05": {
		"classification": "compatibility-only",
		"counts_toward_strict_retail_score": False,
		"closure_phase": "EH-P5",
	},
	"EH-G06": {
		"classification": "validation-governance",
		"counts_toward_strict_retail_score": True,
		"closure_phase": "EH-P6",
	},
}

def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8", errors="ignore")

def _entry(gap_id: str, status: str, summary: str, details: dict[str, Any]) -> dict[str, Any]:
	gap_metadata = GAP_CLASSIFICATIONS[gap_id]
	return {
		"gap_id": gap_id,
		"status": status,
		"summary": summary,
		"classification": gap_metadata["classification"],
		"counts_toward_strict_retail_score": gap_metadata["counts_toward_strict_retail_score"],
		"closure_phase": gap_metadata["closure_phase"],
		"details": details,
	}

def _botlib_fixme_count() -> int:
	return sum(
		path.read_text(encoding="utf-8", errors="ignore").count("FIXME")
		for path in BOTLIB_ROOT.rglob("*.c")
	)

def _runtime_evidence_is_sufficient(runtime_evidence: dict[str, Any] | None) -> bool:
	if runtime_evidence is None:
		return False

	return (
		runtime_evidence["artifact_version"] == 1
		and runtime_evidence["phase"] == "EH-P6"
		and runtime_evidence["parity_estimate"] == {"before": 89, "after": 92}
		and runtime_evidence["runtime_root"] == "build/win32/Debug/bin/baseq3"
		and runtime_evidence["warnings"] == []
		and runtime_evidence["missing_markers"] == []
		and runtime_evidence["clipboard"]["unicode_preferred"] is True
		and runtime_evidence["clipboard"]["ansi_fallback_retained"] is True
		and runtime_evidence["clipboard"]["shared_utf16_helpers_present"] is True
		and runtime_evidence["clipboard"]["consumer_surface_stable"] is True
		and runtime_evidence["raw_input"]["registration_present"] is True
		and runtime_evidence["raw_input"]["wm_input_dispatch_present"] is True
		and runtime_evidence["raw_input"]["device_listing_present"] is True
		and runtime_evidence["raw_input"]["fallback_lanes_retained"] is True
		and runtime_evidence["loading_window"]["wrappers_present"] is True
		and runtime_evidence["loading_window"]["startup_order_proved"] is True
		and runtime_evidence["loading_window"]["fast_restart_maximize_preserved"] is True
		and runtime_evidence["input_translation"]["compiler_agnostic_fixture"] is True
		and runtime_evidence["input_translation"]["shared_library_name_used"] is True
		and runtime_evidence["input_translation"]["find_c_compiler_used"] is True
		and runtime_evidence["platform_and_bot_validation"]["platform_services_surface_tracked"] is True
		and runtime_evidence["platform_and_bot_validation"]["steamworks_harness_tracked"] is True
		and runtime_evidence["platform_and_bot_validation"]["bot_resource_schedule_tracked"] is True
		and runtime_evidence["platform_and_bot_validation"]["botlib_internal_surface_tracked"] is True
		and runtime_evidence["validated_by"]
		== [
			"tests/test_platform_services.py",
			"tests/test_steamworks_harness.py",
			"tests/test_renderer_win32_host_glue_parity.py",
			"tests/test_bot_resource_loading.py",
			"tests/test_botlib_internal_parity.py",
			"tests/test_win32_clipboard_parity.py",
			"tests/test_win32_raw_input_parity.py",
			"tests/test_input_translation.py",
			"tests/test_engine_host_support_full_parity_gate.py",
		]
	)

def _build_engine_host_support_full_parity_gate_report() -> dict[str, Any]:
	engine_host_support_plan = _read_text(ENGINE_HOST_SUPPORT_PLAN_PATH)
	engine_host_support_validation_note = _read_text(ENGINE_HOST_SUPPORT_VALIDATION_NOTE_PATH)
	botlib_internal_audit = _read_text(BOTLIB_INTERNAL_AUDIT_PATH)
	workflow_text = _read_text(WORKFLOW_PATH)
	build_pipeline = _read_text(BUILD_PIPELINE_PATH)
	windows_native_pipeline = _read_text(WINDOWS_NATIVE_PIPELINE_PATH)
	implementation_plan = _read_text(IMPLEMENTATION_PLAN_PATH)
	audit = _read_text(AUDIT_PATH)
	authentication_note = _read_text(AUTHENTICATION_NOTE_PATH)
	toolchain_matrix = _read_text(TOOLCHAIN_MATRIX_PATH)
	platform_config = _read_text(PLATFORM_CONFIG_PATH)
	platform_services = _read_text(PLATFORM_SERVICES_PATH)
	platform_backend_open_steam = _read_text(PLATFORM_BACKEND_OPEN_STEAM_PATH)
	platform_backend_steamworks = _read_text(PLATFORM_BACKEND_STEAMWORKS_PATH)
	win_main = _read_text(WIN_MAIN_PATH)
	win_clipboard_shared = _read_text(WIN_CLIPBOARD_SHARED_PATH)
	win_input = _read_text(WIN_INPUT_PATH)
	win_wndproc = _read_text(WIN_WNDPROC_PATH)
	win_rawinput_shared = _read_text(WIN_RAWINPUT_SHARED_PATH)
	win_syscon = _read_text(WIN_SYSCON_PATH)
	unix_main = _read_text(UNIX_MAIN_PATH)
	null_client = _read_text(NULL_CLIENT_PATH)
	null_input = _read_text(NULL_INPUT_PATH)
	compiler_support = _read_text(COMPILER_SUPPORT_PATH)
	input_translation_tests = _read_text(INPUT_TRANSLATION_TEST_PATH)
	platform_services_tests = _read_text(PLATFORM_SERVICES_TEST_PATH)
	steamworks_harness_tests = _read_text(STEAMWORKS_HARNESS_TEST_PATH)
	renderer_win32_host_glue_tests = _read_text(RENDERER_WIN32_HOST_GLUE_TEST_PATH)
	bot_resource_loading_tests = _read_text(BOT_RESOURCE_LOADING_TEST_PATH)
	botlib_internal_harness = _read_text(BOTLIB_INTERNAL_HARNESS_PATH)
	botlib_internal_tests = _read_text(BOTLIB_INTERNAL_TEST_PATH)
	botlib_interface = _read_text(BOTLIB_INTERFACE_PATH)
	win32_clipboard_tests = _read_text(WIN32_CLIPBOARD_TEST_PATH)
	win32_raw_input_tests = _read_text(WIN32_RAW_INPUT_TEST_PATH)
	runtime_evidence = _read_json(ENGINE_HOST_SUPPORT_RUNTIME_EVIDENCE_PATH) if ENGINE_HOST_SUPPORT_RUNTIME_EVIDENCE_PATH.exists() else None
	runtime_evidence_sufficient = _runtime_evidence_is_sufficient(runtime_evidence)
	botlib_fixme_count = _botlib_fixme_count()

	report: dict[str, Any] = {
		"artifact_version": 1,
		"phase": "EH-P1",
		"parity_estimate": {
			"before": 100,
			"after": 100,
		},
		"scope_boundary": {
			"headline_target": "retail Windows engine host/support replacement target outside qcommon/server/client/renderer",
			"excluded_owner_modules": ["qcommon", "server", "client", "renderer"],
			"excluded_module_trees": ["game", "cgame", "ui"],
			"compatibility_only_surfaces": [
				"src/common/platform/platform_services.c",
				"src/common/platform/backends/platform_backend_open_steam.c",
				"src/common/platform/backends/platform_backend_steamworks.c",
				"src/code/unix/*",
				"src/code/null/*",
			],
			"compatibility_only_gap_ids": list(COMPATIBILITY_ONLY_GAP_IDS),
			"strict_retail_scored_gap_ids": list(STRICT_RETAIL_GAP_IDS),
		},
		"gap_order": list(GAP_ORDER),
		"tranches": {},
	}

	eh_p1_complete = (
		"## EH-P1 - Formalise strict-retail versus compatibility-lane boundaries [COMPLETED 2026-04-10]"
		in engine_host_support_plan
		and _contains_all(
			engine_host_support_plan,
			"machine-readable gap register",
			"compatibility-only lanes",
			"top-level ledgers",
			"`EH-P1` boundary metadata",
		)
		and "### Task 109: Remaining engine host/support EH-P1 boundary formalisation closure [COMPLETED]"
		in implementation_plan
		and "Parity estimate: **before 100% -> after 100%** (`EH-P1` complete; strict-retail scope classification formalised)" in implementation_plan
		and _contains_all(
			engine_host_support_validation_note,
			"Scope: `EH-P1` / `EH-P5` / `EH-P6` closure",
			"`overall_status = pass`",
			"scope-boundary metadata",
			"classification metadata",
		)
		and _contains_all(
			build_pipeline,
			"`EH-P1` boundary metadata",
			"`scope_boundary`",
			"`classification_summary`",
		)
		and _contains_all(
			windows_native_pipeline,
			"`EH-P1` boundary metadata",
			"`scope_boundary`",
			"`classification_summary`",
		)
		and _contains_all(
			audit,
			"`EH-P1` is now complete.",
			"`overall_status: pass`",
			"machine-readable scope boundary and classification metadata",
		)
	)
	report["boundary_formalisation"] = {
		"phase": "EH-P1",
		"status": "pass" if eh_p1_complete else "fail",
		"summary": (
			"Strict-retail versus compatibility-lane boundaries are now formalised in the machine-readable host/support artifact and the linked ledgers."
			if eh_p1_complete
			else "The EH-P1 scope-boundary formalisation is incomplete."
		),
		"compatibility_only_gap_ids": list(COMPATIBILITY_ONLY_GAP_IDS),
		"strict_retail_scored_gap_ids": list(STRICT_RETAIL_GAP_IDS),
	}

	eh_g01_closed = "**Status:** Closed on 2026-04-10 by `EH-P2`" in _section_text_for_id(
		engine_host_support_plan, "EH-G01"
	)
	eh_g01_ok = (
		eh_g01_closed
		and _contains_all(
			win_main,
			"GetClipboardData( CF_UNICODETEXT )",
			"Sys_CloneClipboardUnicodeText( cliptext )",
			"GetClipboardData( CF_TEXT )",
			"Sys_CloneClipboardText( cliptext )",
		)
		and _contains_all(
			win_clipboard_shared,
			"QLR_Win32ClipboardWideToUtf8ByteCount",
			"QLR_Win32ClipboardWideToUtf8",
			"QLR_Win32ClipboardTrimText",
		)
		and _contains_all(
			win32_clipboard_tests,
			"test_shared_win32_clipboard_helper_converts_utf16_to_utf8_bytes",
			"test_shared_win32_clipboard_helper_trims_control_characters_after_conversion",
			"test_win32_clipboard_path_prefers_unicode_and_keeps_ansi_fallback",
			"test_clipboard_consumers_still_flow_through_the_host_utf8_helper",
		)
		and "### Task 103: Remaining engine host/support EH-P2 Win32 Unicode clipboard closure [COMPLETED]" in implementation_plan
	)
	report["tranches"]["EH-G01"] = _entry(
		"EH-G01",
		"pass" if eh_g01_ok else "fail",
		(
			"The Win32 clipboard host path is Unicode-first and retains the ANSI fallback lane."
			if eh_g01_ok
			else "The Win32 clipboard host path is no longer fully pinned to the Unicode-first closure lane."
		),
		{
			"plan_marks_closed": eh_g01_closed,
			"unicode_first_source_present": "GetClipboardData( CF_UNICODETEXT )" in win_main,
			"ansi_fallback_source_present": "GetClipboardData( CF_TEXT )" in win_main,
			"shared_helpers_present": _contains_all(
				win_clipboard_shared,
				"QLR_Win32ClipboardWideToUtf8ByteCount",
				"QLR_Win32ClipboardWideToUtf8",
				"QLR_Win32ClipboardTrimText",
			),
			"focused_tests_present": _contains_all(
				win32_clipboard_tests,
				"test_shared_win32_clipboard_helper_converts_utf16_to_utf8_bytes",
				"test_shared_win32_clipboard_helper_trims_control_characters_after_conversion",
				"test_win32_clipboard_path_prefers_unicode_and_keeps_ansi_fallback",
				"test_clipboard_consumers_still_flow_through_the_host_utf8_helper",
			),
		},
	)

	eh_g02_closed = "**Status:** Closed on 2026-04-10 by `EH-P3`" in _section_text_for_id(
		engine_host_support_plan, "EH-G02"
	)
	eh_g02_ok = (
		eh_g02_closed
		and _contains_all(
			win_input,
			"IN_InitRawInput()",
			'Cmd_AddCommand( "ListInputDevices", ListInputDevices_f );',
			'Com_Printf( "Falling back on raw input...\\n" );',
		)
		and _contains_all(
			win_wndproc,
			"case WM_INPUT:",
			"IN_RawInputEvent( wParam, lParam );",
			"IN_RawInputIsActive()",
		)
		and _contains_all(
			win_rawinput_shared,
			"QLR_Win32RawInputBuildRegistration",
			"QLR_Win32RawInputExtractMouseSample",
			"QLR_Win32RawInputTranslateButtonFlags",
		)
		and _contains_all(
			win32_raw_input_tests,
			"test_raw_input_registration_defaults_to_mouse_usage_page_and_null_target",
			"test_raw_input_removal_uses_ridev_remove_and_clears_the_target",
			"test_win32_raw_input_source_registers_cvars_and_raw_fallback_lane",
			"test_win32_raw_input_source_includes_device_listing_and_wm_input_dispatch",
		)
		and "### Task 105: Remaining engine host/support EH-P3 raw-input host closure [COMPLETED]" in implementation_plan
	)
	report["tranches"]["EH-G02"] = _entry(
		"EH-G02",
		"pass" if eh_g02_ok else "fail",
		(
			"The Win32 raw-input registration, dispatch, and translation lane remains source-backed and test-backed."
			if eh_g02_ok
			else "The Win32 raw-input closure lane is incomplete."
		),
		{
			"plan_marks_closed": eh_g02_closed,
			"raw_registration_present": "IN_InitRawInput()" in win_input,
			"list_input_devices_present": 'Cmd_AddCommand( "ListInputDevices", ListInputDevices_f );' in win_input,
			"wm_input_dispatch_present": "case WM_INPUT:" in win_wndproc,
			"shared_helpers_present": _contains_all(
				win_rawinput_shared,
				"QLR_Win32RawInputBuildRegistration",
				"QLR_Win32RawInputExtractMouseSample",
				"QLR_Win32RawInputTranslateButtonFlags",
			),
			"focused_tests_present": _contains_all(
				win32_raw_input_tests,
				"test_raw_input_registration_defaults_to_mouse_usage_page_and_null_target",
				"test_raw_input_removal_uses_ridev_remove_and_clears_the_target",
				"test_win32_raw_input_source_registers_cvars_and_raw_fallback_lane",
				"test_win32_raw_input_source_includes_device_listing_and_wm_input_dispatch",
			),
		},
	)

	eh_g03_closed = "**Status:** Closed on 2026-04-10 by `EH-P5`" in _section_text_for_id(
		engine_host_support_plan, "EH-G03"
	)
	eh_g03_ok = (
		eh_g03_closed
		and _contains_all(
			authentication_note,
			"compatibility-only provider lane",
			"strict retail Windows engine-host/support score",
			"`QL_BUILD_ONLINE_SERVICES` defaults to `0`",
			"documented open replacement path",
		)
		and _contains_all(
			platform_config,
			"#define QL_BUILD_ONLINE_SERVICES 0",
			"#define QL_BUILD_STEAMWORKS 0",
			"#define QL_BUILD_OPEN_STEAM 0",
		)
		and _contains_all(
			platform_services,
			'Build-disabled (QL_BUILD_ONLINE_SERVICES=0)',
			'"Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS"',
			'"Steamworks"',
			'"Open Steam Adapter"',
			'"Hybrid"',
			'getenv( "QL_DISABLE_EXTERNAL_ECOSYSTEMS" )',
		)
		and _contains_all(
			platform_backend_open_steam,
			'strstr( credential->value, "refresh" )',
			'strstr( credential->value, "denied" )',
			'strstr( credential->value, "invalid" )',
		)
		and _contains_all(
			platform_backend_steamworks,
			'strstr( credential->value, "retry" )',
			'strstr( credential->value, "denied" )',
			'strstr( credential->value, "invalid" )',
		)
		and AUTHENTICATION_NOTE_PATH.exists()
		and "test_platform_service_table_tracks_build_flags" in platform_services_tests
		and "test_hybrid_fallback_accepts_when_steam_pending" in platform_services_tests
		and "test_platform_service_table_respects_runtime_external_disable_env" in platform_services_tests
	)
	report["tranches"]["EH-G03"] = _entry(
		"EH-G03",
		"pass" if eh_g03_ok else "fail",
		(
			"Compatibility-only platform-service abstractions are policy-gated, default-disabled, and explicitly excluded from the strict-retail score."
			if eh_g03_ok
			else "The compatibility-only platform-service lane is no longer explicitly bounded and policy-gated."
		),
		{
			"plan_marks_closed": eh_g03_closed,
			"auth_doc_present": AUTHENTICATION_NOTE_PATH.exists(),
			"default_build_disabled": "#define QL_BUILD_ONLINE_SERVICES 0" in platform_config,
			"runtime_disable_env_present": 'getenv( "QL_DISABLE_EXTERNAL_ECOSYSTEMS" )' in platform_services,
			"compatibility_provider_labels_present": _contains_all(
				platform_services,
				'Build-disabled (QL_BUILD_ONLINE_SERVICES=0)',
				'"Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS"',
				'"Steamworks"',
				'"Open Steam Adapter"',
				'"Hybrid"',
			),
			"open_backend_token_heuristics_present": _contains_all(
				platform_backend_open_steam,
				'strstr( credential->value, "refresh" )',
				'strstr( credential->value, "denied" )',
				'strstr( credential->value, "invalid" )',
			),
			"steamworks_backend_token_heuristics_present": _contains_all(
				platform_backend_steamworks,
				'strstr( credential->value, "retry" )',
				'strstr( credential->value, "denied" )',
				'strstr( credential->value, "invalid" )',
			),
			"focused_tests_present": _contains_all(
				platform_services_tests,
				"test_platform_service_table_tracks_build_flags",
				"test_hybrid_fallback_accepts_when_steam_pending",
				"test_platform_service_table_respects_runtime_external_disable_env",
			),
			"excluded_from_strict_retail_score": _contains_all(
				authentication_note,
				"compatibility-only provider lane",
				"strict retail Windows engine-host/support score",
			),
		},
	)

	eh_g04_closed = "**Status:** Closed on 2026-04-10 by `EH-P4`" in _section_text_for_id(
		engine_host_support_plan, "EH-G04"
	)
	eh_g04_ok = (
		eh_g04_closed
		and BOTLIB_INTERNAL_AUDIT_PATH.exists()
		and _contains_all(
			botlib_internal_audit,
			"`docs/reverse-engineering/quakelive_steam_mapping_round_61.md`",
			"`AAS_PresenceTypeBoundingBox`",
			"`AAS_FallDamageDistance`",
			"`BotAllocGoalState`",
			"`BotResetGoalState`",
			"## Inherited Quake III Carries Versus Quake Live-Specific Deltas",
			"`EH-G04` is now considered closed.",
		)
		and BOT_RESOURCE_LOADING_TEST_PATH.exists()
		and _contains_all(
			bot_resource_loading_tests,
			"test_bot_spawn_schedule_applies_delays",
			"test_access_permissions_enforced_for_commands",
			"test_bot_resource_scenario_matches_expectation",
		)
		and _contains_all(
			botlib_internal_tests,
			"test_botlib_presence_type_bounding_box_matches_retail_boxes",
			"test_botlib_reachability_formula_helpers_match_expected_q3_physics",
			"test_botlib_goal_state_stack_and_avoid_timer_lifecycle",
			"test_botlib_goal_state_invalid_handle_messages_match_retail_strings",
			"test_botlib_interface_still_exports_aas_and_goal_owners",
		)
		and _contains_all(
			botlib_internal_harness,
			"QLR_BotlibPresenceTypeBoundingBoxFromArrays",
			"QLR_BotlibProjectPointOntoVector",
			"QLR_BotlibFallDamageDistance",
			"QLR_BotlibMaxJumpDistance",
			"QLR_BotlibAllocGoalState",
			"QLR_BotlibSetAvoidGoalTime",
		)
		and _contains_all(
			botlib_interface,
			"aas->AAS_PresenceTypeBoundingBox = AAS_PresenceTypeBoundingBox;",
			"aas->AAS_AreaTravelTimeToGoalArea = AAS_AreaTravelTimeToGoalArea;",
			"ai->BotResetGoalState = BotResetGoalState;",
			"ai->BotAllocGoalState = BotAllocGoalState;",
			"ai->BotFreeGoalState = BotFreeGoalState;",
		)
		and "tests/test_botlib_internal_parity.py" in workflow_text
		and "### Task 107: Remaining engine host/support EH-P4 botlib internal proof closure [COMPLETED]" in implementation_plan
		and "Parity estimate: **before 92% -> after 95%**" in implementation_plan
		and _contains_all(
			audit,
			"The refreshed strict `remaining engine host/support` estimate is now tracked as **100%**.",
			"`EH-P4` is now complete.",
			"`EH-G04` is now closed.",
		)
	)
	report["tranches"]["EH-G04"] = _entry(
		"EH-G04",
		"pass" if eh_g04_ok else "fail",
		(
			"Botlib now has a dedicated retail-backed audit plus deterministic internal proof for representative AAS, reachability, and goal-state helpers."
			if eh_g04_ok
			else "Botlib is no longer cleanly recorded as parity-closed at the internal-helper level."
		),
		{
			"plan_marks_closed": eh_g04_closed,
			"dedicated_audit_present": BOTLIB_INTERNAL_AUDIT_PATH.exists(),
			"focused_bot_resource_tests_present": _contains_all(
				bot_resource_loading_tests,
				"test_bot_spawn_schedule_applies_delays",
				"test_access_permissions_enforced_for_commands",
				"test_bot_resource_scenario_matches_expectation",
			),
			"focused_internal_tests_present": _contains_all(
				botlib_internal_tests,
				"test_botlib_presence_type_bounding_box_matches_retail_boxes",
				"test_botlib_reachability_formula_helpers_match_expected_q3_physics",
				"test_botlib_goal_state_stack_and_avoid_timer_lifecycle",
				"test_botlib_goal_state_invalid_handle_messages_match_retail_strings",
				"test_botlib_interface_still_exports_aas_and_goal_owners",
			),
			"harness_export_wrappers_present": _contains_all(
				botlib_internal_harness,
				"QLR_BotlibPresenceTypeBoundingBoxFromArrays",
				"QLR_BotlibProjectPointOntoVector",
				"QLR_BotlibFallDamageDistance",
				"QLR_BotlibMaxJumpDistance",
				"QLR_BotlibAllocGoalState",
				"QLR_BotlibSetAvoidGoalTime",
			),
			"interface_exports_present": _contains_all(
				botlib_interface,
				"aas->AAS_PresenceTypeBoundingBox = AAS_PresenceTypeBoundingBox;",
				"aas->AAS_AreaTravelTimeToGoalArea = AAS_AreaTravelTimeToGoalArea;",
				"ai->BotResetGoalState = BotResetGoalState;",
				"ai->BotAllocGoalState = BotAllocGoalState;",
				"ai->BotFreeGoalState = BotFreeGoalState;",
			),
			"workflow_runs_internal_tests": "tests/test_botlib_internal_parity.py" in workflow_text,
			"botlib_fixme_count": botlib_fixme_count,
		},
	)

	eh_g05_closed = "**Status:** Closed on 2026-04-10 by `EH-P5`" in _section_text_for_id(
		engine_host_support_plan, "EH-G05"
	)
	eh_g05_ok = (
		eh_g05_closed
		and TOOLCHAIN_MATRIX_PATH.exists()
		and _contains_all(
			toolchain_matrix,
			"compatibility-only ports",
			"strict retail Windows engine-host/support score",
			"excluded from the strict-retail parity score and the final `EH-P5` gate result",
		)
		and _contains_all(
			unix_main,
			"Sys_LowPhysicalMemory",
			"Sys_FunctionCmp",
			"Sys_FunctionCheckSum",
			"Sys_MonkeyShouldBeSpanked",
		)
		and _contains_all(
			null_client,
			"void CL_RefreshOnlineServicesBridgeState( void ) {",
			"void CL_WebHost_Init( void ) {",
			"void CL_WebHost_Shutdown( void ) {",
			"qboolean CL_WebHost_HasLiveView( void ) {",
			"void *CL_WebHost_GetCursorHandle( void ) {",
			"void CL_AdvertisementBridge_InitUI( void ) {",
		)
		and _contains_all(
			null_input,
			'void IN_Init( void ) {',
			'in_joystick = Cvar_Get( "in_joystick", "0", CVAR_ARCHIVE|CVAR_LATCH );',
			'Cvar_Set( "ui_joyavail", "0" );',
			'void Sys_SendKeyEvents( void ) {',
		)
	)
	report["tranches"]["EH-G05"] = _entry(
		"EH-G05",
		"pass" if eh_g05_ok else "fail",
		(
			"Unix/null compatibility ports are explicitly bounded as non-retail lanes and excluded from the strict-retail Windows closure score."
			if eh_g05_ok
			else "Unix/null compatibility-port scoping is no longer clearly bounded."
		),
		{
			"plan_marks_closed": eh_g05_closed,
			"toolchain_matrix_present": TOOLCHAIN_MATRIX_PATH.exists(),
			"unix_placeholder_lane_present": _contains_all(
				unix_main,
				"Sys_LowPhysicalMemory",
				"Sys_FunctionCmp",
				"Sys_FunctionCheckSum",
				"Sys_MonkeyShouldBeSpanked",
			),
			"null_stub_lane_present": _contains_all(
				null_client,
				"void CL_RefreshOnlineServicesBridgeState( void ) {",
				"void CL_WebHost_Init( void ) {",
				"void CL_WebHost_Shutdown( void ) {",
				"qboolean CL_WebHost_HasLiveView( void ) {",
				"void *CL_WebHost_GetCursorHandle( void ) {",
				"void CL_AdvertisementBridge_InitUI( void ) {",
			),
			"null_input_lane_present": _contains_all(
				null_input,
				'void IN_Init( void ) {',
				'in_joystick = Cvar_Get( "in_joystick", "0", CVAR_ARCHIVE|CVAR_LATCH );',
				'Cvar_Set( "ui_joyavail", "0" );',
				'void Sys_SendKeyEvents( void ) {',
			),
			"excluded_from_strict_retail_score": _contains_all(
				toolchain_matrix,
				"compatibility-only ports",
				"strict retail Windows engine-host/support score",
				"excluded from the strict-retail parity score and the final `EH-P5` gate result",
			),
		},
	)

	eh_g06_closed = "**Status:** Closed on 2026-04-10 by `EH-P6`" in _section_text_for_id(
		engine_host_support_plan, "EH-G06"
	)
	eh_g06_ok = (
		eh_g06_closed
		and COMPILER_SUPPORT_PATH.exists()
		and _contains_all(
			compiler_support,
			"def find_c_compiler() -> CCompiler | None:",
			"def shared_library_name(stem: str) -> str:",
			"def compile_c_binary(",
		)
		and _contains_all(
			input_translation_tests,
			"find_c_compiler",
			"shared_library_name",
			"compile_c_binary",
			"no supported C compiler is available for the input translation harness",
		)
		and runtime_evidence_sufficient
		and ENGINE_HOST_SUPPORT_VALIDATION_NOTE_PATH.exists()
		and _contains_all(
			engine_host_support_validation_note,
			"engine_host_support_runtime_evidence_20260410.json",
			"engine_host_support_full_parity_gate.json",
			"`EH-P5` is now considered complete.",
			"`EH-G03` and `EH-G05` are now considered closed as documented compatibility-only divergences.",
			"`EH-G04` is now considered closed.",
			"`EH-P6` is now considered complete.",
			"`EH-G06` is now considered closed.",
			"`overall_status = pass`",
		)
		and "## EH-P6 - Add the final remaining-engine host/support parity gate [COMPLETED 2026-04-10]" in engine_host_support_plan
		and _contains_all(
			workflow_text,
			"tests/test_platform_services.py",
			"tests/test_steamworks_harness.py",
			"tests/test_renderer_win32_host_glue_parity.py",
			"tests/test_bot_resource_loading.py",
			"tests/test_botlib_internal_parity.py",
			"tests/test_win32_clipboard_parity.py",
			"tests/test_win32_raw_input_parity.py",
			"tests/test_input_translation.py",
			"tests/test_engine_host_support_full_parity_gate.py",
		)
		and "engine_host_support_full_parity_gate.json" in build_pipeline
		and "engine_host_support_runtime_evidence_20260410.json" in build_pipeline
		and "engine_host_support_full_parity_gate.json" in windows_native_pipeline
		and "engine_host_support_runtime_evidence_20260410.json" in windows_native_pipeline
		and "### Task 106: Remaining engine host/support EH-P6 parity gate and evidence closure [COMPLETED]" in implementation_plan
		and "Parity estimate: **before 89% -> after 92%**" in implementation_plan
		and _contains_all(
			audit,
			"`EH-P6` is now complete.",
			"`EH-G06` is now closed",
		)
	)
	report["tranches"]["EH-G06"] = _entry(
		"EH-G06",
		"pass" if eh_g06_ok else "fail",
		(
			"The remaining-engine host/support scope now has a dedicated parity gate, tracked evidence bundle, and workflow wiring."
			if eh_g06_ok
			else "The remaining-engine host/support parity-gate/evidence lane is incomplete."
		),
		{
			"plan_marks_closed": eh_g06_closed,
			"compiler_helper_present": COMPILER_SUPPORT_PATH.exists(),
			"input_translation_uses_compiler_helper": _contains_all(
				input_translation_tests,
				"find_c_compiler",
				"shared_library_name",
				"compile_c_binary",
			),
			"runtime_evidence_present": ENGINE_HOST_SUPPORT_RUNTIME_EVIDENCE_PATH.exists(),
			"runtime_evidence_sufficient": runtime_evidence_sufficient,
			"validation_note_present": ENGINE_HOST_SUPPORT_VALIDATION_NOTE_PATH.exists(),
			"workflow_references_gate": "tests/test_engine_host_support_full_parity_gate.py" in workflow_text,
			"workflow_runs_input_translation": "tests/test_input_translation.py" in workflow_text,
			"build_pipeline_mentions_gate": "engine_host_support_full_parity_gate.json" in build_pipeline,
			"windows_pipeline_mentions_runtime_artifact": "engine_host_support_runtime_evidence_20260410.json" in windows_native_pipeline,
		},
	)

	non_passing_gap_ids = [
		gap_id
		for gap_id in GAP_ORDER
		if report["tranches"][gap_id]["status"] != "pass"
	]
	failing_gap_ids = [
		gap_id
		for gap_id in GAP_ORDER
		if report["tranches"][gap_id]["status"] == "fail"
	]
	blocked_gap_ids = [
		gap_id
		for gap_id in GAP_ORDER
		if report["tranches"][gap_id]["status"] == "blocked"
	]
	if failing_gap_ids:
		report["overall_status"] = "fail"
	elif blocked_gap_ids:
		report["overall_status"] = "blocked"
	else:
		report["overall_status"] = "pass"
	report["non_passing_gap_ids"] = non_passing_gap_ids
	report["classification_summary"] = {
		"strict_retail_count": sum(
			1 for gap_id in GAP_ORDER if GAP_CLASSIFICATIONS[gap_id]["classification"] == "strict-retail"
		),
		"compatibility_only_count": sum(
			1 for gap_id in GAP_ORDER if GAP_CLASSIFICATIONS[gap_id]["classification"] == "compatibility-only"
		),
		"validation_governance_count": sum(
			1 for gap_id in GAP_ORDER if GAP_CLASSIFICATIONS[gap_id]["classification"] == "validation-governance"
		),
	}
	report["summary"] = {
		"passing_count": sum(1 for gap_id in GAP_ORDER if report["tranches"][gap_id]["status"] == "pass"),
		"blocked_count": len(blocked_gap_ids),
		"failing_count": len(failing_gap_ids),
	}
	return report

def test_engine_host_support_runtime_evidence_artifact_is_tracked_and_clean() -> None:
	runtime_evidence = _read_json(ENGINE_HOST_SUPPORT_RUNTIME_EVIDENCE_PATH)

	assert runtime_evidence["artifact_version"] == 1
	assert runtime_evidence["phase"] == "EH-P6"
	assert runtime_evidence["parity_estimate"] == {"before": 89, "after": 92}
	assert runtime_evidence["runtime_root"] == "build/win32/Debug/bin/baseq3"
	assert runtime_evidence["warnings"] == []
	assert runtime_evidence["missing_markers"] == []
	assert runtime_evidence["clipboard"]["unicode_preferred"] is True
	assert runtime_evidence["clipboard"]["ansi_fallback_retained"] is True
	assert runtime_evidence["clipboard"]["shared_utf16_helpers_present"] is True
	assert runtime_evidence["clipboard"]["consumer_surface_stable"] is True
	assert runtime_evidence["raw_input"]["registration_present"] is True
	assert runtime_evidence["raw_input"]["wm_input_dispatch_present"] is True
	assert runtime_evidence["raw_input"]["device_listing_present"] is True
	assert runtime_evidence["raw_input"]["fallback_lanes_retained"] is True
	assert runtime_evidence["loading_window"]["wrappers_present"] is True
	assert runtime_evidence["loading_window"]["startup_order_proved"] is True
	assert runtime_evidence["loading_window"]["fast_restart_maximize_preserved"] is True
	assert runtime_evidence["input_translation"]["compiler_agnostic_fixture"] is True
	assert runtime_evidence["input_translation"]["shared_library_name_used"] is True
	assert runtime_evidence["input_translation"]["find_c_compiler_used"] is True
	assert runtime_evidence["platform_and_bot_validation"]["platform_services_surface_tracked"] is True
	assert runtime_evidence["platform_and_bot_validation"]["steamworks_harness_tracked"] is True
	assert runtime_evidence["platform_and_bot_validation"]["bot_resource_schedule_tracked"] is True
	assert runtime_evidence["platform_and_bot_validation"]["botlib_internal_surface_tracked"] is True
	assert _runtime_evidence_is_sufficient(runtime_evidence)

def test_engine_host_support_full_parity_gate_writes_status_artifact() -> None:
	report = _build_engine_host_support_full_parity_gate_report()
	_write_json(ENGINE_HOST_SUPPORT_FULL_PARITY_GATE_PATH, report)

	assert ENGINE_HOST_SUPPORT_FULL_PARITY_GATE_PATH.exists()
	assert _read_json(ENGINE_HOST_SUPPORT_FULL_PARITY_GATE_PATH) == report
	assert report["artifact_version"] == 1
	assert report["phase"] == "EH-P1"
	assert report["parity_estimate"] == {"before": 100, "after": 100}
	assert report["scope_boundary"] == {
		"headline_target": "retail Windows engine host/support replacement target outside qcommon/server/client/renderer",
		"excluded_owner_modules": ["qcommon", "server", "client", "renderer"],
		"excluded_module_trees": ["game", "cgame", "ui"],
		"compatibility_only_surfaces": [
			"src/common/platform/platform_services.c",
			"src/common/platform/backends/platform_backend_open_steam.c",
			"src/common/platform/backends/platform_backend_steamworks.c",
			"src/code/unix/*",
			"src/code/null/*",
		],
		"compatibility_only_gap_ids": ["EH-G03", "EH-G05"],
		"strict_retail_scored_gap_ids": ["EH-G01", "EH-G02", "EH-G04", "EH-G06"],
	}
	assert report["boundary_formalisation"] == {
		"phase": "EH-P1",
		"status": "pass",
		"summary": "Strict-retail versus compatibility-lane boundaries are now formalised in the machine-readable host/support artifact and the linked ledgers.",
		"compatibility_only_gap_ids": ["EH-G03", "EH-G05"],
		"strict_retail_scored_gap_ids": ["EH-G01", "EH-G02", "EH-G04", "EH-G06"],
	}
	assert report["gap_order"] == list(GAP_ORDER)
	assert set(report["tranches"]) == set(GAP_ORDER)
	assert report["overall_status"] == "pass"
	assert report["non_passing_gap_ids"] == []
	assert report["classification_summary"] == {
		"strict_retail_count": 3,
		"compatibility_only_count": 2,
		"validation_governance_count": 1,
	}
	assert report["summary"] == {
		"passing_count": 6,
		"blocked_count": 0,
		"failing_count": 0,
	}

	for gap_id in GAP_ORDER:
		entry = report["tranches"][gap_id]
		assert entry["gap_id"] == gap_id
		assert entry["status"] in {"pass", "fail", "blocked"}
		assert entry["classification"] in {"strict-retail", "compatibility-only", "validation-governance"}
		assert isinstance(entry["counts_toward_strict_retail_score"], bool)
		assert entry["closure_phase"].startswith("EH-P")
		assert entry["summary"]

def test_engine_host_support_full_parity_gate_release_mode() -> None:
	if os.environ.get("ENGINE_HOST_SUPPORT_FULL_PARITY_GATE_ENFORCE") != "1":
		pytest.skip(
			"Set ENGINE_HOST_SUPPORT_FULL_PARITY_GATE_ENFORCE=1 to require the remaining-engine host/support gate lane."
		)

	report = _build_engine_host_support_full_parity_gate_report()
	_write_json(ENGINE_HOST_SUPPORT_FULL_PARITY_GATE_PATH, report)
	assert report["overall_status"] == "pass", "Remaining-engine host/support gate must stay fully closed."
	assert report["boundary_formalisation"]["status"] == "pass", "EH-P1 boundary formalisation must stay closed."
	assert report["tranches"]["EH-G06"]["status"] == "pass", "EH-G06 must stay closed."
	assert report["tranches"]["EH-G03"]["status"] == "pass", "EH-G03 must stay classified as a closed compatibility lane."
	assert report["tranches"]["EH-G05"]["status"] == "pass", "EH-G05 must stay classified as a closed compatibility lane."
	assert report["summary"]["failing_count"] == 0, (
		"Remaining-engine host/support gate failed for "
		+ ", ".join(
			gap_id for gap_id in report["non_passing_gap_ids"] if report["tranches"][gap_id]["status"] == "fail"
		)
	)
	assert report["non_passing_gap_ids"] == [], "No remaining-engine host/support gap should remain non-passing."
