from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ARTIFACT_PATH = (
	REPO_ROOT / "artifacts" / "renderer_validation" / "logs" / "renderer_runtime_evidence_20260410.json"
)


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_renderer_runtime_artifact_tracks_text_specific_rg_p11_evidence() -> None:
	runtime_evidence = json.loads(RUNTIME_ARTIFACT_PATH.read_text(encoding="utf-8"))

	assert runtime_evidence["phase"] == "RG-P11"
	assert runtime_evidence["parity_estimate"] == {"before": 98, "after": 100}
	assert runtime_evidence["warnings"] == []
	assert runtime_evidence["missing_log_markers"] == []
	assert runtime_evidence["main_menu"]["engine_sha256"]
	assert runtime_evidence["debug_atlas"]["engine_sha256"]
	assert runtime_evidence["debug_atlas"]["window_sha256"]
	assert runtime_evidence["main_menu"]["engine_sha256"] != runtime_evidence["debug_atlas"]["engine_sha256"]
	assert runtime_evidence["main_menu"]["window_sha256"] != runtime_evidence["debug_atlas"]["window_sha256"]
	assert runtime_evidence["map_runtime"]["map"] == "bloodrun"
	assert runtime_evidence["text_validation"]["fontstash_init_seen"] is True
	assert runtime_evidence["text_validation"]["registerfont_fallback_seen"] is False
	assert runtime_evidence["text_validation"]["debug_atlas_engine_capture_distinct"] is True
	assert runtime_evidence["text_validation"]["debug_atlas_window_capture_distinct"] is True


def test_renderer_docs_and_probe_track_rg_p11_closure() -> None:
	runtime_probe = _read("tools/renderer/run_renderer_runtime_probe.ps1")
	renderer_audit = _read("docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md")
	build_pipeline = _read("docs/build-pipeline.md")
	hud_baseline = _read("docs/hud_render_baseline.md")
	rg_p11_note = _read("docs/reverse-engineering/renderer-text-strict-validation-and-runtime-evidence-2026-04-10.md")

	assert "r_debugFontAtlas" in runtime_probe
	assert "codex_renderer_p11_atlas_" in runtime_probe
	assert "phase = 'RG-P11'" in runtime_probe
	assert "renderer_runtime_evidence_20260410.json" in renderer_audit
	assert "Strict renderer estimate after `RG-P11` closure: **100%**" in renderer_audit
	assert "renderer_runtime_evidence_20260410.json" in build_pipeline
	assert "renderer_runtime_evidence_20260410.json" in hud_baseline
	assert "RG-P11 is now considered complete." in rg_p11_note
