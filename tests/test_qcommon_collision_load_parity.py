"""Retail CM_LoadMap BSP-version-floor parity probes."""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CM_LOAD_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "cm_load.c"
RETAIL_HLIL_PATH = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part06.txt"
)
QCOMMON_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "qcommon-validation.yml"


def test_cm_load_map_source_matches_retail_bsp_version_floor() -> None:
	source = CM_LOAD_PATH.read_text(encoding="utf-8")
	retail_hlil = RETAIL_HLIL_PATH.read_text(encoding="utf-8")

	assert "if ( header.version < BSP_VERSION_QL ) {" in source
	assert "header.version != BSP_VERSION && header.version != BSP_VERSION_QL" not in source
	assert (
		'"CM_LoadMap: %s has an invalid BSP version number (%i should be %i or greater)"'
		in source
	)
	assert (
		"CM_LoadMap: %s has an invalid BSP version number (%i should be %i or greater)"
		in retail_hlil
	)


def test_qcommon_workflow_runs_collision_load_parity_probe() -> None:
	workflow = QCOMMON_WORKFLOW_PATH.read_text(encoding="utf-8")

	assert "tests/test_qcommon_collision_load_parity.py" in workflow
