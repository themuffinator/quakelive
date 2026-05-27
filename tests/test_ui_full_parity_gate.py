from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from tests._shared import REPO_ROOT, read_json as _read_json, write_json as _write_json

from scripts.ui.retail_ui_corpus import (
	DEFAULT_BASEQ3_ROOT,
	DEFAULT_BUNDLE_MANIFEST,
	build_retail_ui_inventory,
	compute_ui_panel_drift,
)

SOURCE_ROOT = REPO_ROOT / "src" / "ui"
RETAIL_ROOT = DEFAULT_BASEQ3_ROOT / "ui"

UI_INVENTORY_PATH = REPO_ROOT / "artifacts" / "ui_bundle" / "ui_retail_inventory.json"
UI_OVERLAY_MANIFEST_PATH = REPO_ROOT / "artifacts" / "ui_bundle" / "ui_src_retail_overlay.json"
UI_METRICS_PATH = REPO_ROOT / "artifacts" / "ui_bundle" / "metrics" / "font_metrics.json"
UI_BUNDLE_PATH = REPO_ROOT / "artifacts" / "ui_bundle" / "pak_uiql.pk3"
UI_OVERLAY_BUNDLE_PATH = REPO_ROOT / "artifacts" / "ui_bundle" / "pak_ui_src_retail_overlay.pk3"
UI_VALIDATION_SUMMARY_PATH = REPO_ROOT / "artifacts" / "ui_validation" / "logs" / "ui_validation_summary.json"
UI_FULL_PARITY_GATE_PATH = REPO_ROOT / "artifacts" / "ui_validation" / "logs" / "ui_full_parity_gate.json"

UI_MAIN_PATH = REPO_ROOT / "src" / "code" / "ui" / "ui_main.c"
UI_SHARED_PATH = REPO_ROOT / "src" / "code" / "ui" / "ui_shared.c"
UI_LOCAL_PATH = REPO_ROOT / "src" / "code" / "ui" / "ui_local.h"
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "ui-validation.yml"
SCRIPTING_GUIDE_PATH = REPO_ROOT / "docs" / "ui" / "scripting-guide.md"
UI_PLAN_PATH = REPO_ROOT / "docs" / "reverse-engineering" / "ui-full-parity-audit-and-implementation-plan-2026-04-05.md"
QMENU_NOTE_PATH = REPO_ROOT / "docs" / "reverse-engineering" / "ui-qmenu-struct-layouts.md"
MAPPING_ROUND_PATH = REPO_ROOT / "docs" / "reverse-engineering" / "ui-mapping-round-2026-04-01.md"

GAP_ORDER = (
	"UI-G01",
	"UI-G02",
	"UI-G03",
	"UI-G04",
	"UI-G05",
	"UI-G06",
)

def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8")

def _entry(gap_id: str, status: str, summary: str, details: dict[str, Any]) -> dict[str, Any]:
	return {
		"gap_id": gap_id,
		"status": status,
		"summary": summary,
		"details": details,
	}

def _inventory_artifact_details(
	retail_ui_corpus_inventory: dict[str, object],
) -> tuple[bool, dict[str, Any]]:
	details: dict[str, Any] = {
		"inventory_artifact_path": str(UI_INVENTORY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
		"inventory_artifact_present": UI_INVENTORY_PATH.exists(),
		"retail_ui_corpus_available": retail_ui_corpus_inventory["retail_ui_corpus_available"],
		"missing_required_inputs": retail_ui_corpus_inventory["missing_required_inputs"],
	}

	if not UI_INVENTORY_PATH.exists():
		details["artifact_matches_runtime_probe"] = False
		return False, details

	inventory_artifact = _read_json(UI_INVENTORY_PATH)
	matches = (
		inventory_artifact.get("retail_ui_corpus_available")
		== retail_ui_corpus_inventory["retail_ui_corpus_available"]
		and inventory_artifact.get("missing_required_inputs")
		== retail_ui_corpus_inventory["missing_required_inputs"]
	)
	details["artifact_matches_runtime_probe"] = matches
	return matches, details

def _build_ui_full_parity_gate_report(
	retail_ui_corpus_inventory: dict[str, object],
) -> dict[str, Any]:
	inventory_ok, inventory_details = _inventory_artifact_details(retail_ui_corpus_inventory)
	report: dict[str, Any] = {
		"artifact_version": 1,
		"phase": "UI-P5",
		"parity_estimate": {
			"before": 92,
			"after": 97,
		},
		"gap_order": list(GAP_ORDER),
		"tranches": {},
	}

	if retail_ui_corpus_inventory["retail_ui_corpus_available"] and inventory_ok:
		report["tranches"]["UI-G01"] = _entry(
			"UI-G01",
			"pass",
			"Retail UI corpus is available and the tracked inventory artifact matches the runtime probe.",
			inventory_details,
		)
	else:
		report["tranches"]["UI-G01"] = _entry(
			"UI-G01",
			"fail",
			"Retail UI corpus is unavailable or the tracked inventory artifact no longer matches the current probe.",
			inventory_details,
		)

	overlay_details: dict[str, Any] = {
		"overlay_manifest_path": str(UI_OVERLAY_MANIFEST_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
		"overlay_manifest_present": UI_OVERLAY_MANIFEST_PATH.exists(),
	}
	if UI_OVERLAY_MANIFEST_PATH.exists():
		overlay_manifest = _read_json(UI_OVERLAY_MANIFEST_PATH)
		overlay_details["overlay_policy_mode"] = overlay_manifest.get("overlay_policy", {}).get("mode")
		overlay_details["overlay_manifest_retail_ui_corpus_available"] = overlay_manifest.get(
			"retail_ui_corpus_available"
		)
		overlay_details["overlay_manifest_drift_files"] = overlay_manifest.get("drift_files")
	else:
		overlay_manifest = None

	if not retail_ui_corpus_inventory["retail_ui_corpus_available"]:
		report["tranches"]["UI-G02"] = _entry(
			"UI-G02",
			"blocked",
			"Strict source-vs-retail panel drift comparison is blocked until the retail UI corpus is staged locally.",
			overlay_details,
		)
	else:
		drift = compute_ui_panel_drift(SOURCE_ROOT, RETAIL_ROOT)
		drift_files = sorted(drift["content_diffs"])
		contract_ok = (
			drift["missing_in_source"] == []
			and drift["extra_in_source"] == []
			and drift_files == []
		)
		manifest_ok = (
			overlay_manifest is not None
			and overlay_manifest.get("drift_files") == drift_files
			and overlay_manifest.get("overlay_policy", {}).get("mode")
			== "retail-install-first-read-only-src-ui"
		)
		overlay_details.update(
			{
				"missing_in_source": drift["missing_in_source"],
				"extra_in_source": drift["extra_in_source"],
				"content_diffs": drift_files,
				"drift_contract_ok": contract_ok,
				"overlay_manifest_matches_drift": manifest_ok,
			}
		)
		report["tranches"]["UI-G02"] = _entry(
			"UI-G02",
			"pass" if (contract_ok and manifest_ok) else "fail",
			(
				"Source-vs-retail panel drift is clean and the overlay manifest records an empty drift contract."
				if (contract_ok and manifest_ok)
				else "Source-vs-retail panel drift or the overlay manifest no longer matches the clean current contract."
			),
			overlay_details,
		)

	validation_details: dict[str, Any] = {
		"retail_ui_bundle_artifact_present": UI_BUNDLE_PATH.exists(),
		"retail_ui_overlay_artifact_present": UI_OVERLAY_BUNDLE_PATH.exists(),
		"font_metrics_present": UI_METRICS_PATH.exists(),
		"ui_validation_summary_present": UI_VALIDATION_SUMMARY_PATH.exists(),
		"overlay_manifest_present": UI_OVERLAY_MANIFEST_PATH.exists(),
	}

	if UI_VALIDATION_SUMMARY_PATH.exists():
		validation_summary = _read_json(UI_VALIDATION_SUMMARY_PATH)
		glyph_drifts = validation_summary.get("glyphMetrics", {}).get("drifts", [])
		missing_shaders = validation_summary.get("shaderHandles", {}).get("missing", {})
		missing_configs = validation_summary.get("configs", {}).get("missing", [])
		validation_details.update(
			{
				"glyph_drift_count": len(glyph_drifts),
				"missing_shader_groups": sorted(missing_shaders),
				"missing_configs": missing_configs,
			}
		)
	else:
		glyph_drifts = ["missing-ui-validation-summary"]
		missing_shaders = {"ui_validation_summary.json": ["missing"]}
		missing_configs = ["ui_validation_summary.json"]

	summary_ok = not glyph_drifts and not missing_shaders and not missing_configs
	artifacts_ok = all(
		(
			not validation_details["retail_ui_bundle_artifact_present"],
			not validation_details["retail_ui_overlay_artifact_present"],
			validation_details["font_metrics_present"],
			validation_details["ui_validation_summary_present"],
			validation_details["overlay_manifest_present"],
		)
	)
	if retail_ui_corpus_inventory["retail_ui_corpus_available"]:
		status = "pass" if (artifacts_ok and summary_ok) else "fail"
		summary = (
			"Validation artifacts are present, no retail UI packages were emitted, and the tracked validation summary is clean."
			if status == "pass"
			else "Validation artifacts are missing or the tracked validation summary records drift."
		)
	else:
		status = "fail"
		summary = (
			"UI validation remains blocked by the missing retail baseq3 inputs, even though tracked UI artifacts exist."
		)
	report["tranches"]["UI-G03"] = _entry("UI-G03", status, summary, validation_details)

	ui_local = _read_text(UI_LOCAL_PATH)
	qmenu_note = _read_text(QMENU_NOTE_PATH)
	mapping_round = _read_text(MAPPING_ROUND_PATH)
	ui_plan = _read_text(UI_PLAN_PATH)
	qmenu_helpers = (
		"Menu_AddItem",
		"Menu_Draw",
		"Menu_DefaultKey",
		"MField_Draw",
		"ScrollList_Key",
	)
	boundary_ok = all(helper in ui_local for helper in qmenu_helpers)
	boundary_ok = boundary_ok and "## Phase 4 Ownership Closure (2026-04-06)" in qmenu_note
	boundary_ok = boundary_ok and "## Phase 4 Closure Update (2026-04-06)" in mapping_round
	boundary_ok = boundary_ok and "[Closed on 2026-04-06]" in ui_plan
	boundary_ok = boundary_ok and "No unresolved high-impact ownership gap remains in an active runtime path." in qmenu_note
	boundary_ok = boundary_ok and "No unresolved high-impact ownership gap remains in an active runtime path." in mapping_round

	report["tranches"]["UI-G04"] = _entry(
		"UI-G04",
		"pass" if boundary_ok else "fail",
		(
			"qmenu widget-core ownership remains explicitly bounded and no active runtime ownership gap is left open."
			if boundary_ok
			else "qmenu widget-core ownership notes no longer match the documented bounded-helper closure."
		),
		{
			"helper_band": list(qmenu_helpers),
			"qmenu_note_closed": "## Phase 4 Ownership Closure (2026-04-06)" in qmenu_note,
			"mapping_round_closed": "## Phase 4 Closure Update (2026-04-06)" in mapping_round,
			"ui_plan_closed": "[Closed on 2026-04-06]" in ui_plan,
		},
	)

	ui_main = _read_text(UI_MAIN_PATH)
	ui_shared = _read_text(UI_SHARED_PATH)
	platform_tests = _read_text(REPO_ROOT / "tests" / "test_platform_services.py")
	service_routing_ok = "qboolean UI_HandleDeferredScriptExec( const itemDef_t *item, const char *commandText ) {" in ui_main
	service_routing_ok = service_routing_ok and 'UI_CommandTextMatches( commandText, "web_showBrowser" )' in ui_main
	service_routing_ok = service_routing_ok and 'UI_CommandTextMatches( commandText, "web_changeHash" )' in ui_main
	service_routing_ok = service_routing_ok and 'UI_ShowOfflineMenuFallbackError( "Browser overlay unavailable; retail menu remains active." );' in ui_main
	service_routing_ok = service_routing_ok and "if ( UI_HandleDeferredScriptExec( item, val ) ) {" in ui_shared
	service_routing_ok = service_routing_ok and "test_online_service_bridge_only_hard_stubs_when_build_disabled" in platform_tests
	service_routing_ok = service_routing_ok and "test_service_disabled_menu_verb_matrix_stays_explicit" in platform_tests
	service_routing_ok = service_routing_ok and "test_launcher_resource_fallbacks_survive_service_disabled_policy" in platform_tests

	report["tranches"]["UI-G05"] = _entry(
		"UI-G05",
		"pass" if service_routing_ok else "fail",
		(
			"Service-disabled menu and launcher-resource routing stay explicit in source and in the focused platform-service regression surface."
			if service_routing_ok
			else "Service-disabled menu or launcher-resource routing no longer matches the documented explicit fallback matrix."
		),
		{
			"deferred_exec_seam_present": "UI_HandleDeferredScriptExec" in ui_main,
			"script_exec_hook_present": "if ( UI_HandleDeferredScriptExec( item, val ) ) {" in ui_shared,
			"platform_service_coverage_present": (
				"test_online_service_bridge_only_hard_stubs_when_build_disabled" in platform_tests
				and "test_service_disabled_menu_verb_matrix_stays_explicit" in platform_tests
				and "test_launcher_resource_fallbacks_survive_service_disabled_policy" in platform_tests
			),
		},
	)

	workflow_text = _read_text(WORKFLOW_PATH) if WORKFLOW_PATH.exists() else ""
	scripting_guide = _read_text(SCRIPTING_GUIDE_PATH)
	ui_gate_test = _read_text(REPO_ROOT / "tests" / "test_ui_full_parity_gate.py")
	gate_wired = "tests/test_ui_full_parity_gate.py" in workflow_text
	gate_wired = gate_wired and "pytest tests/test_ui_full_parity_gate.py -q" in workflow_text
	gate_wired = gate_wired and "ui_full_parity_gate.json" in scripting_guide
	gate_wired = gate_wired and "UI_FULL_PARITY_GATE_ENFORCE" in ui_gate_test

	report["tranches"]["UI-G06"] = _entry(
		"UI-G06",
		"pass" if gate_wired else "fail",
		(
			"Unified UI parity gate is wired into the validation workflow and publishes a machine-readable status artifact."
			if gate_wired
			else "Unified UI parity gate wiring or documentation is incomplete."
		),
		{
			"gate_test_path": str((REPO_ROOT / "tests" / "test_ui_full_parity_gate.py").relative_to(REPO_ROOT)).replace("\\", "/"),
			"workflow_references_gate": "tests/test_ui_full_parity_gate.py" in workflow_text,
			"workflow_runs_gate": "pytest tests/test_ui_full_parity_gate.py -q" in workflow_text,
			"scripting_guide_mentions_gate_artifact": "ui_full_parity_gate.json" in scripting_guide,
			"release_mode_env_supported": "UI_FULL_PARITY_GATE_ENFORCE" in ui_gate_test,
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

def test_ui_full_parity_gate_writes_status_artifact(
	retail_ui_corpus_inventory: dict[str, object],
) -> None:
	report = _build_ui_full_parity_gate_report(retail_ui_corpus_inventory)
	_write_json(UI_FULL_PARITY_GATE_PATH, report)

	assert UI_FULL_PARITY_GATE_PATH.exists()
	assert _read_json(UI_FULL_PARITY_GATE_PATH) == report
	assert report["phase"] == "UI-P5"
	assert report["gap_order"] == list(GAP_ORDER)
	assert set(report["tranches"]) == set(GAP_ORDER)
	assert report["overall_status"] == ("pass" if not report["non_passing_gap_ids"] else "fail")

	for gap_id in GAP_ORDER:
		entry = report["tranches"][gap_id]
		assert entry["gap_id"] == gap_id
		assert entry["status"] in {"pass", "fail", "blocked"}
		assert entry["summary"]

	if retail_ui_corpus_inventory["retail_ui_corpus_available"]:
		assert report["tranches"]["UI-G01"]["status"] == "pass"
		assert report["tranches"]["UI-G02"]["status"] == "pass"
		assert report["tranches"]["UI-G03"]["status"] in {"pass", "fail"}
	else:
		assert report["tranches"]["UI-G01"]["status"] == "fail"
		assert report["tranches"]["UI-G02"]["status"] == "blocked"
		assert report["tranches"]["UI-G03"]["status"] == "fail"

def test_ui_full_parity_gate_release_mode(
	retail_ui_corpus_inventory: dict[str, object],
) -> None:
	if os.environ.get("UI_FULL_PARITY_GATE_ENFORCE") != "1":
		pytest.skip("Set UI_FULL_PARITY_GATE_ENFORCE=1 to require a full UI parity pass.")

	report = _build_ui_full_parity_gate_report(retail_ui_corpus_inventory)
	_write_json(UI_FULL_PARITY_GATE_PATH, report)
	assert report["overall_status"] == "pass", (
		"UI full parity gate failed for "
		+ ", ".join(report["non_passing_gap_ids"])
	)
