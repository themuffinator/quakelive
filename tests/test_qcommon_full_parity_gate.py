from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
QCOMMON_FULL_PARITY_GATE_PATH = (
	REPO_ROOT / "artifacts" / "qcommon_validation" / "logs" / "qcommon_full_parity_gate.json"
)
QCOMMON_RUNTIME_EVIDENCE_PATH = (
	REPO_ROOT / "artifacts" / "qcommon_validation" / "logs" / "qcommon_runtime_evidence_20260410.json"
)
QCOMMON_PLAN_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md"
)
QCOMMON_VALIDATION_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "qcommon-validation-and-runtime-evidence-2026-04-10.md"
)
QCOMMON_COLLISION_OWNERSHIP_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "qcommon-collision-leaf-ownership-2026-04-10.md"
)
QCOMMON_VM_FALLBACK_OWNERSHIP_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "qcommon-vm-fallback-ownership-2026-04-10.md"
)
QSHARED_AUDIT_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "qshared-retail-helper-parity-audit-2026-04-17.md"
)
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "qcommon-validation.yml"
BUILD_PIPELINE_PATH = REPO_ROOT / "docs" / "build-pipeline.md"
WINDOWS_NATIVE_PIPELINE_PATH = REPO_ROOT / "docs" / "windows-native-pipeline.md"
IMPLEMENTATION_PLAN_PATH = REPO_ROOT / "IMPLEMENTATION_PLAN.md"
AUDIT_PATH = REPO_ROOT / "AUDIT.md"
RUNTIME_PROBE_PATH = REPO_ROOT / "tools" / "qcommon" / "run_qcommon_runtime_probe.ps1"

FILES_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "files.c"
CM_PATCH_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "cm_patch.c"
CM_POLYLIB_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "cm_polylib.c"
VM_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "vm.c"
VM_INTERPRETED_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "vm_interpreted.c"
VM_X86_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "vm_x86.c"

COMPILER_SUPPORT_PATH = REPO_ROOT / "tests" / "compiler_support.py"
CVAR_ALIAS_TEST_PATH = REPO_ROOT / "tests" / "test_cvar_alias_console.py"
FS_SEARCH_TEST_PATH = REPO_ROOT / "tests" / "test_fs_search_paths.py"
PLAYERSTATE_TEST_PATH = REPO_ROOT / "tests" / "test_playerstate_replication.py"
QSHARED_TEST_PATH = REPO_ROOT / "tests" / "test_qshared_retail_parity.py"
CM_COLLISION_HARNESS_PATH = REPO_ROOT / "tests" / "cm_collision_harness.c"
CM_COLLISION_TEST_PATH = REPO_ROOT / "tests" / "test_qcommon_collision_leaf_parity.py"
VM_FALLBACK_HARNESS_PATH = REPO_ROOT / "tests" / "vm_fallback_harness.c"
VM_FALLBACK_TEST_PATH = REPO_ROOT / "tests" / "test_qcommon_vm_fallback_parity.py"
ROUND_108_PATH = REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_108.md"
ROUND_109_PATH = REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_109.md"

GAP_ORDER = ("QC-G01", "QC-G02", "QC-G03", "QC-G04", "QC-G05")


def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
	return json.loads(path.read_text(encoding="utf-8"))


def _home_ui_search_path_is_clean(main_menu: dict[str, Any]) -> bool:
	if "search_path_contains_home_duplicate_ui_pk3" in main_menu:
		return main_menu["search_path_contains_home_duplicate_ui_pk3"] is False

	return main_menu.get("search_path_contains_home_overlay") is True


def _write_json(path: Path, payload: dict[str, Any]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _contains_all(text: str, *needles: str) -> bool:
	return all(needle in text for needle in needles)


def _section_text_for_id(text: str, section_id: str) -> str:
	match = re.search(rf"^## {re.escape(section_id)}\b.*$", text, re.MULTILINE)
	if match is None:
		return ""

	start = match.start()
	next_match = re.search(r"\n## ", text[match.end() :])
	if next_match is None:
		return text[start:]

	end = match.end() + next_match.start()
	return text[start:end]


def _entry(gap_id: str, status: str, summary: str, details: dict[str, Any]) -> dict[str, Any]:
	return {
		"gap_id": gap_id,
		"status": status,
		"summary": summary,
		"details": details,
	}


def _dll_load_root_contract_is_sufficient(load_roots: dict[str, Any]) -> bool:
	attempts = load_roots.get("attempts")
	if isinstance(attempts, dict):
		attempts = [attempts]
	if not isinstance(attempts, list) or not attempts:
		return False

	return load_roots["writable_homepath_ok"] is True


def _runtime_evidence_is_sufficient(runtime_evidence: dict[str, Any] | None) -> bool:
	if runtime_evidence is None:
		return False

	main_menu = runtime_evidence["main_menu"]
	service_disabled_policy = main_menu["service_disabled_policy"]
	map_runtime = runtime_evidence["map_runtime"]

	return (
		runtime_evidence["artifact_version"] == 1
		and runtime_evidence["phase"] == "QC-P6"
		and runtime_evidence["parity_estimate"] == {"before": 98, "after": 100}
		and runtime_evidence["warnings"] == []
		and runtime_evidence["missing_log_markers"] == []
		and runtime_evidence["probe_script"] == "tools/qcommon/run_qcommon_runtime_probe.ps1"
		and main_menu["engine_screenshot"]
		and main_menu["engine_sha256"]
		and main_menu["ui_init_complete"] is True
		and main_menu["execed_qzconfig"] is True
		and main_menu["execed_repconfig"] is True
		and main_menu["current_search_path"]
		and main_menu["search_path_contains_homepath_root"] is True
		and _home_ui_search_path_is_clean(main_menu)
		and main_menu["search_path_contains_retail_pak00"] is True
		and service_disabled_policy["steam_resource_bridge_disabled"] is True
		and service_disabled_policy["show_browser_ignored"] is True
		and service_disabled_policy["change_hash_ignored"] is True
		and service_disabled_policy["game_error_published"] is True
		and service_disabled_policy["native_stop_refresh_logged"] is True
		and _dll_load_root_contract_is_sufficient(main_menu["ui_dll_load_roots"])
		and map_runtime["map"] == "bloodrun"
		and map_runtime["engine_screenshot"]
		and map_runtime["engine_sha256"]
		and map_runtime["server_seen"] is True
		and map_runtime["active_seen"] is True
		and map_runtime["shot_logged"] is True
		and _dll_load_root_contract_is_sufficient(map_runtime["qagame_dll_load_roots"])
		and _dll_load_root_contract_is_sufficient(map_runtime["cgame_dll_load_roots"])
		and main_menu["engine_sha256"] != map_runtime["engine_sha256"]
	)


def _build_qcommon_full_parity_gate_report() -> dict[str, Any]:
	qcommon_plan = _read_text(QCOMMON_PLAN_PATH)
	qcommon_validation_note = _read_text(QCOMMON_VALIDATION_NOTE_PATH)
	collision_ownership_note = _read_text(QCOMMON_COLLISION_OWNERSHIP_NOTE_PATH)
	vm_fallback_ownership_note = _read_text(QCOMMON_VM_FALLBACK_OWNERSHIP_NOTE_PATH)
	workflow_text = _read_text(WORKFLOW_PATH)
	build_pipeline = _read_text(BUILD_PIPELINE_PATH)
	windows_native_pipeline = _read_text(WINDOWS_NATIVE_PIPELINE_PATH)
	implementation_plan = _read_text(IMPLEMENTATION_PLAN_PATH)
	audit = _read_text(AUDIT_PATH)
	files_c = _read_text(FILES_PATH)
	cm_patch = _read_text(CM_PATCH_PATH)
	cm_polylib = _read_text(CM_POLYLIB_PATH)
	vm_c = _read_text(VM_PATH)
	vm_interpreted = _read_text(VM_INTERPRETED_PATH)
	vm_x86 = _read_text(VM_X86_PATH)
	compiler_support = _read_text(COMPILER_SUPPORT_PATH)
	cvar_alias_tests = _read_text(CVAR_ALIAS_TEST_PATH)
	fs_search_tests = _read_text(FS_SEARCH_TEST_PATH)
	playerstate_tests = _read_text(PLAYERSTATE_TEST_PATH)
	collision_harness = _read_text(CM_COLLISION_HARNESS_PATH)
	collision_tests = _read_text(CM_COLLISION_TEST_PATH)
	vm_fallback_harness = _read_text(VM_FALLBACK_HARNESS_PATH)
	vm_fallback_tests = _read_text(VM_FALLBACK_TEST_PATH)
	round_108 = _read_text(ROUND_108_PATH)
	round_109 = _read_text(ROUND_109_PATH)
	runtime_evidence = _read_json(QCOMMON_RUNTIME_EVIDENCE_PATH) if QCOMMON_RUNTIME_EVIDENCE_PATH.exists() else None
	runtime_evidence_sufficient = _runtime_evidence_is_sufficient(runtime_evidence)

	report: dict[str, Any] = {
		"artifact_version": 1,
		"phase": "QC-P6",
		"parity_estimate": {
			"before": 98,
			"after": 100,
		},
		"gap_order": list(GAP_ORDER),
		"tranches": {},
	}

	qc_g01_closed = "**Status:** Closed on 2026-04-10" in _section_text_for_id( qcommon_plan, "QC-G01" )
	audit_records_qc_p3 = _contains_all(
		audit,
		"The refreshed strict `qcommon` estimate is now **92%**.",
		"`QC-P2` and `QC-P3` are now complete.",
		"`QC-G04` and `QC-G01` are now closed.",
	)
	qc_g01_ok = (
		qc_g01_closed
		and "FS_DetectSteamHomePath" not in files_c
		and "static const char *FS_ResolveHomePath( const char *basePath ) {" in files_c
		and "QL_Steamworks_GetUserSteamID" in files_c
		and "test_homepath_resolution_defaults_to_basepath_without_steam_user" in fs_search_tests
		and "test_homepath_resolution_appends_retail_steamid_suffix_when_available" in fs_search_tests
		and "test_web_fallback_reads_mapped_fs_webpath_content_and_reports_resolution" in fs_search_tests
		and "test_web_fallback_routes_screenshot_requests_through_homepath" in fs_search_tests
		and "### Task 94: Qcommon QC-P3 retail homepath closure [COMPLETED]" in implementation_plan
		and audit_records_qc_p3
	)
	report["tranches"]["QC-G01"] = _entry(
		"QC-G01",
		"pass" if qc_g01_ok else "fail",
		(
			"Win32 homepath selection now follows the retail Steam-ID-backed `FS_Startup` path."
			if qc_g01_ok
			else "The Win32 homepath selection path still diverges from the retail Steam-ID-backed `FS_Startup` behavior."
		),
		{
			"plan_marks_closed": qc_g01_closed,
			"heuristic_helper_present": "FS_DetectSteamHomePath" in files_c,
			"homepath_helper_present": "static const char *FS_ResolveHomePath( const char *basePath ) {" in files_c,
			"steam_user_lookup_present": "QL_Steamworks_GetUserSteamID" in files_c,
			"focused_homepath_tests_present": (
				"test_homepath_resolution_defaults_to_basepath_without_steam_user" in fs_search_tests
				and "test_homepath_resolution_appends_retail_steamid_suffix_when_available" in fs_search_tests
			),
			"focused_web_fallback_tests_present": (
				"test_web_fallback_reads_mapped_fs_webpath_content_and_reports_resolution" in fs_search_tests
				and "test_web_fallback_routes_screenshot_requests_through_homepath" in fs_search_tests
			),
			"implementation_plan_records_qc_p3": (
				"### Task 94: Qcommon QC-P3 retail homepath closure [COMPLETED]" in implementation_plan
			),
			"audit_records_qc_p3": audit_records_qc_p3,
		},
	)

	qc_g02_closed = "**Status:** Closed" in _section_text_for_id( qcommon_plan, "QC-G02" )
	audit_records_qc_p4 = _contains_all(
		audit,
		"The refreshed strict `qcommon` estimate is now **95%**.",
		"`QC-P4` is now complete.",
		"`QC-G02` is now closed.",
	)
	qc_g02_ok = (
		qc_g02_closed
		and _contains_all(
			collision_ownership_note,
			"QLCGImport_CM_MarkFragments",
			"CG_CM_MARKFRAGMENTS",
			"re.MarkFragments",
			"CM_GeneratePatchCollide",
			"BaseWindingForPlane",
			"tests/test_qcommon_collision_leaf_parity.py",
		)
		and '#include "../src/code/qcommon/cm_local.h"' in collision_harness
		and "QLR_CM_TestCurvedPatchStats" in collision_harness
		and "QLR_CM_TestFlatPatchPointTrace" in collision_harness
		and "QLR_CM_TestBaseWindingClip" in collision_harness
		and "QLR_CM_TestCheckFacetPlane" in collision_harness
		and "test_curved_patch_generation_reports_expected_planes_facets_and_bounds" in collision_tests
		and "test_flat_patch_point_trace_matches_surface_clip_epsilon" in collision_tests
		and "test_flat_patch_position_test_detects_box_overlap" in collision_tests
		and "test_base_winding_clip_matches_expected_mark_fragment_style_bounds" in collision_tests
		and "test_check_facet_plane_reports_expected_enter_fraction" in collision_tests
		and "### Task 97: Qcommon QC-P4 collision leaf ownership closure [COMPLETED]" in implementation_plan
		and audit_records_qc_p4
		and "CM_GeneratePatchCollide" in cm_patch
		and "BaseWindingForPlane" in cm_polylib
	)
	report["tranches"]["QC-G02"] = _entry(
		"QC-G02",
		"pass" if qc_g02_ok else "fail",
		(
			"The low-confidence collision-model leaves are no longer treated as an open parity bucket."
			if qc_g02_ok
			else "The collision-model leaf exactness bucket remains open beneath the otherwise strong `CM_*` ABI."
		),
		{
			"plan_marks_closed": qc_g02_closed,
			"ownership_note_present": QCOMMON_COLLISION_OWNERSHIP_NOTE_PATH.exists(),
			"ownership_note_binds_renderer_mark_fragments_seam": _contains_all(
				collision_ownership_note,
				"QLCGImport_CM_MarkFragments",
				"CG_CM_MARKFRAGMENTS",
				"re.MarkFragments",
			),
			"ownership_note_binds_patch_polylib_leaf_band": _contains_all(
				collision_ownership_note,
				"CM_GeneratePatchCollide",
				"BaseWindingForPlane",
				"cm_patch.c",
				"cm_polylib.c",
			),
			"collision_harness_present": CM_COLLISION_HARNESS_PATH.exists(),
			"collision_harness_exports_leaf_probes": _contains_all(
				collision_harness,
				"QLR_CM_TestCurvedPatchStats",
				"QLR_CM_TestFlatPatchPointTrace",
				"QLR_CM_TestBaseWindingClip",
				"QLR_CM_TestCheckFacetPlane",
			),
			"collision_tests_present": CM_COLLISION_TEST_PATH.exists(),
			"collision_tests_cover_leaf_probes": _contains_all(
				collision_tests,
				"test_curved_patch_generation_reports_expected_planes_facets_and_bounds",
				"test_flat_patch_point_trace_matches_surface_clip_epsilon",
				"test_flat_patch_position_test_detects_box_overlap",
				"test_base_winding_clip_matches_expected_mark_fragment_style_bounds",
				"test_check_facet_plane_reports_expected_enter_fraction",
			),
			"implementation_plan_records_qc_p4": (
				"### Task 97: Qcommon QC-P4 collision leaf ownership closure [COMPLETED]" in implementation_plan
			),
			"audit_records_qc_p4": audit_records_qc_p4,
		},
	)

	qc_g03_closed = "**Status:** Closed" in _section_text_for_id( qcommon_plan, "QC-G03" )
	audit_records_qc_p5 = _contains_all(
		audit,
		"The refreshed strict `qcommon` estimate is now **98%**.",
		"`QC-P5` is now complete.",
		"`QC-G03` is now closed.",
	)
	qc_g03_ok = (
		qc_g03_closed
		and _contains_all(
			vm_fallback_ownership_note,
			"VM_Create",
			"VM_Restart",
			"VM_CallInterpreted",
			"VM_Compile",
			"VM_CallCompiled",
			"tests/test_qcommon_vm_fallback_parity.py",
			"vm_x86.c",
			"compatibility carry",
		)
		and _contains_all(
			vm_fallback_harness,
			"QLR_VM_TestNativeFallbackToCompiled",
			"QLR_VM_TestRestrictForcesCompiled",
			"QLR_VM_TestMissingQvmAfterNativeFailure",
			"QLR_VM_TestInterpreterAdd",
			"QLR_VM_TestInterpreterSyscall",
			"QLR_VM_TestRestartNativeFallback",
			"QLR_VM_TestArgPtrModes",
		)
		and _contains_all(
			vm_fallback_tests,
			"test_native_failure_falls_back_to_compiled_qvm_and_dispatches_compiled_call",
			"test_fs_restrict_forces_compiled_qvm_without_native_load_attempt",
			"test_missing_qvm_after_native_failure_returns_null_and_logs_fallback_failure",
			"test_bytecode_lane_uses_real_interpreter_and_executes_add_program",
			"test_interpreted_syscall_lane_preserves_contract_logging",
			"test_restart_retries_native_then_falls_back_to_compiled_qvm",
			"test_vm_arg_ptr_and_explicit_arg_ptr_preserve_native_and_qvm_pointer_modes",
			"test_vm_fallback_sources_bound_host_selection_and_legacy_x86_backend",
		)
		and "tests/test_qcommon_vm_fallback_parity.py" in workflow_text
		and "tests/test_qcommon_vm_fallback_parity.py" in build_pipeline
		and "tests/test_qcommon_vm_fallback_parity.py" in windows_native_pipeline
		and "### Task 102: Qcommon QC-P5 fallback VM closure [COMPLETED]" in implementation_plan
		and audit_records_qc_p5
		and _contains_all(
			vm_c,
			"interpret = VMI_COMPILED;",
			'Failed to load dll, looking for qvm.',
			"VM_PrepareInterpreter",
			"VM_Compile",
			"VM_Create( name, systemCall, VMI_NATIVE, dllImports, dllApiVersion );",
		)
		and _contains_all(
			vm_interpreted,
			'SyscallContract_LogEvent( "vm-interpreted", vm->name',
			"vm->currentlyInterpreting = qtrue;",
			"VM_PrepareInterpreter",
			"VM_CallInterpreted",
		)
		and _contains_all(
			vm_x86,
			"AsmCall",
			"VM_Compile",
			"VM_CallCompiled",
			"instructionPointers = vm->instructionPointers",
			"callMask = vm->dataMask",
		)
	)
	report["tranches"]["QC-G03"] = _entry(
		"QC-G03",
		"pass" if qc_g03_ok else "fail",
		(
			"The fallback Windows QVM/JIT lane is no longer an open qcommon gap."
			if qc_g03_ok
			else "The fallback Windows QVM/JIT lane remains a less-explicitly bounded tail than the native DLL path."
		),
		{
			"plan_marks_closed": qc_g03_closed,
			"ownership_note_present": QCOMMON_VM_FALLBACK_OWNERSHIP_NOTE_PATH.exists(),
			"ownership_note_binds_vm_host_and_carry_split": _contains_all(
				vm_fallback_ownership_note,
				"VM_Create",
				"VM_Restart",
				"VM_CallInterpreted",
				"VM_Compile",
				"VM_CallCompiled",
				"compatibility carry",
			),
			"fallback_harness_present": VM_FALLBACK_HARNESS_PATH.exists(),
			"fallback_harness_exports_runtime_probes": _contains_all(
				vm_fallback_harness,
				"QLR_VM_TestNativeFallbackToCompiled",
				"QLR_VM_TestRestrictForcesCompiled",
				"QLR_VM_TestMissingQvmAfterNativeFailure",
				"QLR_VM_TestInterpreterAdd",
				"QLR_VM_TestInterpreterSyscall",
				"QLR_VM_TestRestartNativeFallback",
				"QLR_VM_TestArgPtrModes",
			),
			"fallback_tests_present": VM_FALLBACK_TEST_PATH.exists(),
			"fallback_tests_cover_runtime_and_source_probes": _contains_all(
				vm_fallback_tests,
				"test_native_failure_falls_back_to_compiled_qvm_and_dispatches_compiled_call",
				"test_fs_restrict_forces_compiled_qvm_without_native_load_attempt",
				"test_missing_qvm_after_native_failure_returns_null_and_logs_fallback_failure",
				"test_bytecode_lane_uses_real_interpreter_and_executes_add_program",
				"test_interpreted_syscall_lane_preserves_contract_logging",
				"test_restart_retries_native_then_falls_back_to_compiled_qvm",
				"test_vm_arg_ptr_and_explicit_arg_ptr_preserve_native_and_qvm_pointer_modes",
				"test_vm_fallback_sources_bound_host_selection_and_legacy_x86_backend",
			),
			"workflow_references_vm_fallback_tests": "tests/test_qcommon_vm_fallback_parity.py" in workflow_text,
			"build_pipeline_mentions_vm_fallback_tests": "tests/test_qcommon_vm_fallback_parity.py" in build_pipeline,
			"windows_pipeline_mentions_vm_fallback_tests": "tests/test_qcommon_vm_fallback_parity.py" in windows_native_pipeline,
			"implementation_plan_records_qc_p5": (
				"### Task 102: Qcommon QC-P5 fallback VM closure [COMPLETED]" in implementation_plan
			),
			"audit_records_qc_p5": audit_records_qc_p5,
		},
	)

	qc_g04_closed = "**Status:** Closed on 2026-04-10" in _section_text_for_id( qcommon_plan, "QC-G04" )
	qc_g04_ok = (
		qc_g04_closed
		and COMPILER_SUPPORT_PATH.exists()
		and QSHARED_TEST_PATH.exists()
		and QSHARED_AUDIT_PATH.exists()
		and "def find_c_compiler() -> CCompiler | None:" in compiler_support
		and "tests/test_qcommon_full_parity_gate.py" in workflow_text
		and "tests/test_cvar_alias_console.py" in workflow_text
		and "tests/test_fs_search_paths.py" in workflow_text
		and "tests/test_playerstate_replication.py" in workflow_text
		and "tests/test_qshared_retail_parity.py" in workflow_text
		and "find_c_compiler" in cvar_alias_tests
		and "find_c_compiler" in fs_search_tests
		and "shared_library_name" in fs_search_tests
		and "find_c_compiler" in playerstate_tests
		and "shared_library_name" in playerstate_tests
		and 'skipif(os.name == "nt"' not in playerstate_tests
		and "qcommon_full_parity_gate.json" in build_pipeline
		and "tests/test_qshared_retail_parity.py" in build_pipeline
		and "qcommon_full_parity_gate.json" in windows_native_pipeline
		and "tests/test_qshared_retail_parity.py" in windows_native_pipeline
		and "### Task 92: Qcommon QC-P2 parity gate and Windows-friendly harness closure [COMPLETED]" in implementation_plan
	)
	report["tranches"]["QC-G04"] = _entry(
		"QC-G04",
		"pass" if qc_g04_ok else "fail",
		(
			"Qcommon now has a dedicated machine-readable parity gate plus Windows-friendly harness coverage."
			if qc_g04_ok
			else "The qcommon parity gate or Windows-friendly harness coverage is still incomplete."
		),
		{
			"plan_marks_closed": qc_g04_closed,
			"compiler_helper_present": COMPILER_SUPPORT_PATH.exists(),
			"workflow_references_gate": "tests/test_qcommon_full_parity_gate.py" in workflow_text,
			"workflow_references_windows_harnesses": (
				"tests/test_cvar_alias_console.py" in workflow_text
				and "tests/test_fs_search_paths.py" in workflow_text
				and "tests/test_playerstate_replication.py" in workflow_text
			),
			"workflow_references_qshared_test": "tests/test_qshared_retail_parity.py" in workflow_text,
			"cvar_alias_uses_compiler_helper": "find_c_compiler" in cvar_alias_tests,
			"fs_search_uses_compiler_helper": "find_c_compiler" in fs_search_tests and "shared_library_name" in fs_search_tests,
			"playerstate_windows_skip_removed": 'skipif(os.name == "nt"' not in playerstate_tests,
			"qshared_test_present": QSHARED_TEST_PATH.exists(),
			"qshared_audit_present": QSHARED_AUDIT_PATH.exists(),
			"build_pipeline_mentions_gate": "qcommon_full_parity_gate.json" in build_pipeline,
			"build_pipeline_mentions_qshared_test": "tests/test_qshared_retail_parity.py" in build_pipeline,
			"windows_pipeline_mentions_gate": "qcommon_full_parity_gate.json" in windows_native_pipeline,
			"windows_pipeline_mentions_qshared_test": "tests/test_qshared_retail_parity.py" in windows_native_pipeline,
		},
	)

	round_108_stale = "do not yet have a writable owner" in round_108
	round_109_stale = "does not have a writable owner" in round_109
	qc_g05_closed = "**Status:** Closed on 2026-04-10" in _section_text_for_id( qcommon_plan, "QC-G05" )
	qc_g05_ok = (
		qc_g05_closed
		and not round_108_stale
		and not round_109_stale
		and RUNTIME_PROBE_PATH.exists()
		and runtime_evidence_sufficient
		and QCOMMON_VALIDATION_NOTE_PATH.exists()
		and _contains_all(
			qcommon_validation_note,
			"qcommon_runtime_evidence_20260410.json",
			"qcommon_full_parity_gate.json",
			"`QC-P6` is now considered complete.",
			"`QC-G05` is now considered closed.",
		)
		and "## QC-P6 - Reconcile stale mapping notes and publish final qcommon runtime evidence [COMPLETED 2026-04-10]" in qcommon_plan
		and "tools/qcommon/run_qcommon_runtime_probe.ps1" in workflow_text
		and "tests/test_qcommon_full_parity_gate.py" in workflow_text
		and "qcommon_full_parity_gate.json" in build_pipeline
		and "qcommon_runtime_evidence_20260410.json" in build_pipeline
		and "tools/qcommon/run_qcommon_runtime_probe.ps1" in build_pipeline
		and "qcommon_full_parity_gate.json" in windows_native_pipeline
		and "qcommon_runtime_evidence_20260410.json" in windows_native_pipeline
		and "tools/qcommon/run_qcommon_runtime_probe.ps1" in windows_native_pipeline
		and "### Task 104: Qcommon QC-P6 runtime-evidence and ledger closure [COMPLETED]" in implementation_plan
		and "Parity estimate: **before 98% -> after 100%**" in implementation_plan
		and _contains_all(
			audit,
			"The refreshed strict `qcommon` estimate is now **100%**.",
			"`QC-P6` is now complete.",
			"`QC-G05` is now closed.",
			"No open gap remains in the audited qcommon register.",
		)
	)
	report["tranches"]["QC-G05"] = _entry(
		"QC-G05",
		"pass" if qc_g05_ok else "fail",
		(
			"The qcommon ledger now has a dedicated runtime-evidence bundle and reconciled mapping notes."
			if qc_g05_ok
			else "The qcommon ledger/runtime-evidence closure lane is still incomplete."
		),
		{
			"plan_marks_closed": qc_g05_closed,
			"round_108_stale_write_client_config_note": round_108_stale,
			"round_109_stale_write_client_config_note": round_109_stale,
			"runtime_probe_present": RUNTIME_PROBE_PATH.exists(),
			"runtime_evidence_present": QCOMMON_RUNTIME_EVIDENCE_PATH.exists(),
			"runtime_evidence_sufficient": runtime_evidence_sufficient,
			"validation_note_present": QCOMMON_VALIDATION_NOTE_PATH.exists(),
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


def test_qcommon_runtime_evidence_artifact_is_tracked_and_clean() -> None:
	runtime_evidence = _read_json(QCOMMON_RUNTIME_EVIDENCE_PATH)

	assert runtime_evidence["artifact_version"] == 1
	assert runtime_evidence["phase"] == "QC-P6"
	assert runtime_evidence["parity_estimate"] == {"before": 98, "after": 100}
	assert runtime_evidence["warnings"] == []
	assert runtime_evidence["missing_log_markers"] == []
	assert runtime_evidence["main_menu"]["engine_screenshot"]
	assert runtime_evidence["main_menu"]["engine_sha256"]
	assert runtime_evidence["main_menu"]["ui_init_complete"] is True
	assert runtime_evidence["main_menu"]["execed_qzconfig"] is True
	assert runtime_evidence["main_menu"]["execed_repconfig"] is True
	assert runtime_evidence["main_menu"]["search_path_contains_homepath_root"] is True
	assert _home_ui_search_path_is_clean(runtime_evidence["main_menu"])
	assert runtime_evidence["main_menu"]["search_path_contains_retail_pak00"] is True
	assert runtime_evidence["main_menu"]["service_disabled_policy"]["steam_resource_bridge_disabled"] is True
	assert runtime_evidence["main_menu"]["service_disabled_policy"]["show_browser_ignored"] is True
	assert runtime_evidence["main_menu"]["service_disabled_policy"]["change_hash_ignored"] is True
	assert runtime_evidence["main_menu"]["service_disabled_policy"]["game_error_published"] is True
	assert runtime_evidence["main_menu"]["service_disabled_policy"]["native_stop_refresh_logged"] is True
	assert _dll_load_root_contract_is_sufficient(runtime_evidence["main_menu"]["ui_dll_load_roots"])
	assert runtime_evidence["map_runtime"]["map"] == "bloodrun"
	assert runtime_evidence["map_runtime"]["engine_screenshot"]
	assert runtime_evidence["map_runtime"]["engine_sha256"]
	assert runtime_evidence["map_runtime"]["server_seen"] is True
	assert runtime_evidence["map_runtime"]["active_seen"] is True
	assert runtime_evidence["map_runtime"]["shot_logged"] is True
	assert _dll_load_root_contract_is_sufficient(runtime_evidence["map_runtime"]["qagame_dll_load_roots"])
	assert _dll_load_root_contract_is_sufficient(runtime_evidence["map_runtime"]["cgame_dll_load_roots"])
	assert _runtime_evidence_is_sufficient(runtime_evidence)


def test_qcommon_full_parity_gate_writes_status_artifact() -> None:
	report = _build_qcommon_full_parity_gate_report()
	_write_json(QCOMMON_FULL_PARITY_GATE_PATH, report)

	assert QCOMMON_FULL_PARITY_GATE_PATH.exists()
	assert _read_json(QCOMMON_FULL_PARITY_GATE_PATH) == report
	assert report["artifact_version"] == 1
	assert report["phase"] == "QC-P6"
	assert report["parity_estimate"] == {"before": 98, "after": 100}
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


def test_qcommon_full_parity_gate_release_mode() -> None:
	if os.environ.get("QCOMMON_FULL_PARITY_GATE_ENFORCE") != "1":
		pytest.skip("Set QCOMMON_FULL_PARITY_GATE_ENFORCE=1 to require a full qcommon parity pass.")

	report = _build_qcommon_full_parity_gate_report()
	_write_json(QCOMMON_FULL_PARITY_GATE_PATH, report)
	assert report["overall_status"] == "pass", (
		"Qcommon full parity gate failed for "
		+ ", ".join(report["non_passing_gap_ids"])
	)
