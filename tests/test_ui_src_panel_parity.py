from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from scripts.ui.retail_ui_corpus import (
	DEFAULT_BASEQ3_ROOT,
	compute_ui_panel_drift,
	inventory_missing_reason,
	materialize_manifest_corpus,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = REPO_ROOT / "src" / "ui"
RETAIL_ROOT = DEFAULT_BASEQ3_ROOT / "ui"
SCRIPT_PATH = REPO_ROOT / "scripts" / "ui" / "write_retail_ui_overrides.py"
CORPUS_CHECK_SCRIPT = REPO_ROOT / "scripts" / "ui" / "check_retail_ui_corpus.py"

def _sha256_bytes(data: bytes) -> str:
	return hashlib.sha256(data).hexdigest()


def _assert_repo_overlay_drift_contract(drift: dict[str, object]) -> list[str]:
	assert drift["missing_in_source"] == []
	assert drift["extra_in_source"] == []

	drift_files = sorted(drift["content_diffs"])
	assert drift_files == []
	return drift_files


def _require_retail_ui_corpus(retail_ui_corpus_inventory: dict[str, object]) -> None:
	if not retail_ui_corpus_inventory["retail_ui_corpus_available"]:
		pytest.skip(inventory_missing_reason(retail_ui_corpus_inventory))


def test_retail_ui_corpus_validator_writes_inventory_manifest(
	tmp_path: Path,
	retail_ui_corpus_inventory: dict[str, object],
) -> None:
	inventory_path = tmp_path / "ui_retail_inventory.json"
	result = subprocess.run(
		[
			sys.executable,
			str(CORPUS_CHECK_SCRIPT),
			"--inventory-out",
			str(inventory_path),
		],
		check=False,
		cwd=REPO_ROOT,
		text=True,
		capture_output=True,
	)

	assert inventory_path.exists()
	report = json.loads(inventory_path.read_text(encoding="utf-8"))
	assert report["retail_ui_corpus_available"] == retail_ui_corpus_inventory["retail_ui_corpus_available"]
	assert report["missing_required_inputs"] == retail_ui_corpus_inventory["missing_required_inputs"]

	if retail_ui_corpus_inventory["retail_ui_corpus_available"]:
		assert result.returncode == 0, result.stderr
		assert report["inventory_counts"]["files"] > 0
	else:
		assert result.returncode == 0
		assert report["missing_required_inputs"]
		assert "Retail UI corpus unavailable." in result.stderr


def test_src_ui_inventory_matches_retail_tree(
	retail_ui_corpus_inventory: dict[str, object],
) -> None:
	_require_retail_ui_corpus(retail_ui_corpus_inventory)
	drift = compute_ui_panel_drift(SOURCE_ROOT, RETAIL_ROOT)
	_assert_repo_overlay_drift_contract(drift)

	retail_assets = RETAIL_ROOT / "assets"
	assert retail_assets.is_dir()


def test_src_ui_content_drift_is_clean_against_retail_panels(
	retail_ui_corpus_inventory: dict[str, object],
) -> None:
	_require_retail_ui_corpus(retail_ui_corpus_inventory)
	drift = compute_ui_panel_drift(SOURCE_ROOT, RETAIL_ROOT)
	drift_files = _assert_repo_overlay_drift_contract(drift)
	assert drift_files == []


def test_retail_ui_override_script_manifest_records_hashes_and_stale_cleanup(
	tmp_path: Path,
) -> None:
	source_root = tmp_path / "source_ui"
	retail_root = tmp_path / "retail_ui"
	homepath_root = tmp_path / "overlay_home"
	manifest_path = tmp_path / "ui_retail_overrides.json"

	(source_root / "ui").mkdir(parents=True)
	(retail_root / "ui").mkdir(parents=True)

	(source_root / "ui" / "stable.menu").write_text("stable\n", encoding="utf-8")
	(retail_root / "ui" / "stable.menu").write_text("stable\n", encoding="utf-8")
	(source_root / "ui" / "hud.txt").write_text("source-hud\n", encoding="utf-8")
	(retail_root / "ui" / "hud.txt").write_text("retail-hud\n", encoding="utf-8")
	(retail_root / "ui" / "ingame_join.menu").write_text("retail-join\n", encoding="utf-8")

	stale_file = homepath_root / "baseq3" / "ui" / "stale" / "obsolete.menu"
	stale_file.parent.mkdir(parents=True, exist_ok=True)
	stale_file.write_text("obsolete\n", encoding="utf-8")
	manifest_path.write_text(
		json.dumps(
			{
				"overlay_files": [
					"baseq3/ui/stale/obsolete.menu",
				]
			},
			indent=2,
		),
		encoding="utf-8",
	)

	subprocess.run(
		[
			sys.executable,
			str(SCRIPT_PATH),
			"--source-root",
			str(source_root / "ui"),
			"--retail-root",
			str(retail_root / "ui"),
			"--homepath-root",
			str(homepath_root),
			"--manifest",
			str(manifest_path),
		],
		check=True,
		cwd=REPO_ROOT,
	)

	report = json.loads(manifest_path.read_text(encoding="utf-8"))
	expected_overlay_files = [
		"baseq3/ui/hud.txt",
		"baseq3/ui/ingame_join.menu",
	]

	assert report["manifest_version"] == 2
	assert report["drift_files"] == ["hud.txt", "ingame_join.menu"]
	assert report["overlay_files"] == expected_overlay_files
	assert report["materialization_mode"] == "report-only"
	assert report["materialized_overlay_files"] == []
	assert report["stale_removed_files"] == ["baseq3/ui/stale/obsolete.menu"]
	assert f"{homepath_root.as_posix()}/baseq3/ui/stale" in report["stale_removed_dirs"]
	assert report["stale_missing_files"] == []
	assert report["overlay_policy"]["mode"] == "retail-install-first-read-only-src-ui"
	assert report["overlay_policy"]["runtime_base_source"] == "retail-fs_basepath/baseq3"
	assert report["overlay_policy"]["duplication_policy"] == "do-not-duplicate-retail-distributables"
	assert report["overlay_policy"]["overlay_materialization_default"] == "report-only"
	assert "fs_basepath" in report["overlay_policy"]["precedence_contract"]
	assert "Do not package or mount duplicated retail UI bundles" in report["overlay_policy"]["precedence_contract"]
	assert "Report-only" in report["overlay_policy"]["materialization_warning"]
	assert not stale_file.exists()

	overlay_entries = {entry["overlay_path"]: entry for entry in report["overlay_entries"]}
	for overlay_path, relative_ui_path in (
		("baseq3/ui/hud.txt", "hud.txt"),
		("baseq3/ui/ingame_join.menu", "ingame_join.menu"),
	):
		entry = overlay_entries[overlay_path]
		retail_bytes = (retail_root / "ui" / relative_ui_path).read_bytes()
		assert entry["ui_path"] == relative_ui_path
		assert entry["size"] == len(retail_bytes)
		assert entry["sha256"] == _sha256_bytes(retail_bytes)
		assert report["overlay_file_hashes"][overlay_path] == entry["sha256"]


def test_retail_ui_override_script_reports_drifted_files_without_materializing_by_default(
	tmp_path: Path,
	retail_ui_corpus_inventory: dict[str, object],
) -> None:
	_require_retail_ui_corpus(retail_ui_corpus_inventory)
	homepath_root = tmp_path / "ui_homepath"
	manifest_path = tmp_path / "ui_retail_overrides.json"
	drift = compute_ui_panel_drift(SOURCE_ROOT, RETAIL_ROOT)
	drift_files = _assert_repo_overlay_drift_contract(drift)

	subprocess.run(
		[
			sys.executable,
			str(SCRIPT_PATH),
			"--homepath-root",
			str(homepath_root),
			"--manifest",
			str(manifest_path),
		],
		check=True,
		cwd=REPO_ROOT,
	)

	report = json.loads(manifest_path.read_text(encoding="utf-8"))
	assert report["manifest_version"] == 2
	assert report["materialization_mode"] == "report-only"
	assert report["materialized_overlay_files"] == []
	assert report["drift_files"] == drift_files
	assert set(report["overlay_files"]) == {f"baseq3/ui/{relative_path}" for relative_path in drift_files}
	assert set(report["overlay_file_hashes"]) == set(report["overlay_files"])
	assert set(report["overlay_policy"]) >= {
		"mode",
		"runtime_base_source",
		"duplication_policy",
		"overlay_materialization_default",
		"precedence_contract",
		"verification_contract",
		"materialization_warning",
	}

	for relative_path in drift_files:
		override_path = homepath_root / "baseq3" / "ui" / relative_path
		assert not override_path.exists()


def test_retail_ui_override_script_can_materialize_explicit_emit_files(
	tmp_path: Path,
	retail_ui_corpus_inventory: dict[str, object],
) -> None:
	_require_retail_ui_corpus(retail_ui_corpus_inventory)
	homepath_root = tmp_path / "ui_homepath"
	manifest_path = tmp_path / "ui_retail_overrides.json"
	drift = compute_ui_panel_drift(SOURCE_ROOT, RETAIL_ROOT)
	drift_files = _assert_repo_overlay_drift_contract(drift)

	subprocess.run(
		[
			sys.executable,
			str(SCRIPT_PATH),
			"--homepath-root",
			str(homepath_root),
			"--manifest",
			str(manifest_path),
			"--emit-files",
		],
		check=True,
		cwd=REPO_ROOT,
	)

	report = json.loads(manifest_path.read_text(encoding="utf-8"))
	assert report["materialization_mode"] == "emit-files"
	assert set(report["materialized_overlay_files"]) == {f"baseq3/ui/{relative_path}" for relative_path in drift_files}

	for relative_path in drift_files:
		override_path = homepath_root / "baseq3" / "ui" / relative_path
		retail_path = RETAIL_ROOT / relative_path
		assert override_path.exists()
		assert override_path.read_bytes() == retail_path.read_bytes()


def test_materialized_retail_corpus_refreshes_when_manifest_scope_expands(tmp_path: Path) -> None:
	baseq3_root = tmp_path / "steam_baseq3"
	output_root = tmp_path / "materialized_baseq3"
	manifest_path = tmp_path / "ui_bundle_manifest.json"
	pak_path = baseq3_root / "pak00.pk3"

	baseq3_root.mkdir(parents=True)
	with zipfile.ZipFile(pak_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
		archive.writestr("ui/main.menu", "main\n")
		archive.writestr("icons/icon_time.png", "icon-time\n")
		archive.writestr("menu/icons/quad.png", "quad\n")

	manifest_path.write_text(
		json.dumps(
			{
				"files": [
					{
						"source_dir": "assets/quakelive/baseq3/ui",
						"destination": "ui",
						"include": ["**/*.menu"],
					}
				]
			},
			indent=2,
		),
		encoding="utf-8",
	)

	result = materialize_manifest_corpus(baseq3_root, output_root, manifest_path)
	assert result == output_root
	assert (output_root / "ui" / "main.menu").is_file()
	assert not (output_root / "icons" / "icon_time.png").exists()

	manifest_path.write_text(
		json.dumps(
			{
				"files": [
					{
						"source_dir": "assets/quakelive/baseq3/ui",
						"destination": "ui",
						"include": ["**/*.menu"],
					},
					{
						"source_dir": "assets/quakelive/baseq3/icons",
						"destination": "icons",
						"include": ["**/*"],
					},
					{
						"source_dir": "assets/quakelive/baseq3/menu/icons",
						"destination": "menu/icons",
						"include": ["**/*"],
					},
				]
			},
			indent=2,
		),
		encoding="utf-8",
	)

	refreshed = materialize_manifest_corpus(baseq3_root, output_root, manifest_path)
	assert refreshed == output_root
	assert (output_root / "icons" / "icon_time.png").is_file()
	assert (output_root / "menu" / "icons" / "quad.png").is_file()


def test_retail_ui_override_script_supports_pk3_overlay_prefix(
	tmp_path: Path,
	retail_ui_corpus_inventory: dict[str, object],
) -> None:
	_require_retail_ui_corpus(retail_ui_corpus_inventory)
	overlay_root = tmp_path / "ui_overlay_pk3"
	manifest_path = tmp_path / "ui_overlay_pk3.json"
	drift = compute_ui_panel_drift(SOURCE_ROOT, RETAIL_ROOT)
	drift_files = _assert_repo_overlay_drift_contract(drift)

	subprocess.run(
		[
			sys.executable,
			str(SCRIPT_PATH),
			"--homepath-root",
			str(overlay_root),
			"--manifest",
			str(manifest_path),
			"--overlay-prefix",
			"ui",
		],
		check=True,
		cwd=REPO_ROOT,
	)

	report = json.loads(manifest_path.read_text(encoding="utf-8"))
	assert report["manifest_version"] == 2
	assert report["overlay_prefix"] == "ui"
	assert report["drift_files"] == drift_files
	assert set(report["overlay_files"]) == {f"ui/{relative_path}" for relative_path in drift_files}
	assert set(report["overlay_file_hashes"]) == set(report["overlay_files"])

	for relative_path in drift_files:
		override_path = overlay_root / "ui" / relative_path
		retail_path = RETAIL_ROOT / relative_path
		assert override_path.exists()
		assert override_path.read_bytes() == retail_path.read_bytes()


def test_ui_bundle_build_keeps_retail_packages_unmaterialized(
	retail_ui_corpus_inventory: dict[str, object],
) -> None:
	overlay_package = REPO_ROOT / "build" / "ui_bundle" / "pak_ui_src_retail_overlay.pk3"
	overlay_manifest = REPO_ROOT / "artifacts" / "ui_bundle" / "ui_src_retail_overlay.json"
	main_package = REPO_ROOT / "build" / "ui_bundle" / "pak_uiql.pk3"
	runtime_package_manifest = REPO_ROOT / "artifacts" / "ui_bundle" / "runtime_ui_package_manifest.json"
	metrics_path = REPO_ROOT / "artifacts" / "ui_bundle" / "metrics" / "font_metrics.json"
	inventory_manifest = REPO_ROOT / "artifacts" / "ui_bundle" / "ui_retail_inventory.json"
	staging_root = REPO_ROOT / "build" / "ui_bundle" / "staging" / "baseq3"
	preserved_files = {}
	for path in (
		overlay_package,
		overlay_manifest,
		main_package,
		runtime_package_manifest,
		metrics_path,
		inventory_manifest,
	):
		preserved_files[path] = path.read_bytes() if path.exists() else None

	try:
		if overlay_package.exists():
			overlay_package.unlink()
		if overlay_manifest.exists():
			overlay_manifest.unlink()
		if main_package.exists():
			main_package.unlink()
		if runtime_package_manifest.exists():
			runtime_package_manifest.unlink()
		if metrics_path.exists():
			metrics_path.unlink()
		if inventory_manifest.exists():
			inventory_manifest.unlink()

		result = subprocess.run(
			[sys.executable, str(REPO_ROOT / "tools" / "build_ui_bundle.py")],
			cwd=REPO_ROOT,
			check=False,
			text=True,
			capture_output=True,
		)

		assert inventory_manifest.exists()

		if retail_ui_corpus_inventory["retail_ui_corpus_available"]:
			assert result.returncode == 0, result.stderr
			assert overlay_manifest.exists()
			assert metrics_path.exists()
			assert not overlay_package.exists()
			assert not main_package.exists()
			assert not runtime_package_manifest.exists()
			assert (staging_root / "default.cfg").exists()
			assert (staging_root / "ui" / "main.menu").exists()
			assert (staging_root / "ui" / "assets" / "button_back.png").exists()
			assert (staging_root / "ui" / "assets" / "hud" / "ffa.png").exists()
			assert (staging_root / "ui" / "assets" / "hud" / "dm.png").exists()
			assert (staging_root / "ui" / "assets" / "hud" / "tourn.png").exists()
			assert (staging_root / "ui" / "assets" / "bluechip.png").exists()
			assert (staging_root / "ui" / "assets" / "redchip.png").exists()
			assert (staging_root / "ui" / "assets" / "score" / "scoretl.png").exists()
			assert (staging_root / "ui" / "assets" / "score" / "navbarl.png").exists()
			assert (staging_root / "ui" / "assets" / "score" / "navbarm.png").exists()
			assert (staging_root / "ui" / "assets" / "score" / "navbarr.png").exists()
			assert (staging_root / "ui" / "assets" / "score" / "navleft.png").exists()
			assert (staging_root / "ui" / "assets" / "score" / "navright.png").exists()
			assert (staging_root / "ui" / "assets" / "score" / "navfriends.png").exists()
			assert (staging_root / "fonts" / "font.dat").exists()
			assert (staging_root / "fonts" / "font.tga").exists()

			report = json.loads(overlay_manifest.read_text(encoding="utf-8"))
			drift = compute_ui_panel_drift(SOURCE_ROOT, RETAIL_ROOT)
			drift_files = _assert_repo_overlay_drift_contract(drift)
			assert report["overlay_prefix"] == "baseq3/ui"
			assert report["drift_files"] == drift_files
			assert report["materialization_mode"] == "report-only"
			assert report["materialized_overlay_files"] == []
			assert set(report["overlay_files"]) == {f"baseq3/ui/{relative_path}" for relative_path in drift_files}
			assert len(report["overlay_entries"]) == len(drift_files)
			return

		assert result.returncode != 0
		assert "Retail UI corpus unavailable." in result.stderr
		assert "Missing required inputs:" in result.stderr
		for expected in ("default.cfg", "fonts/handelgothic.ttf", "scripts/ui.shader", "ui/main.menu"):
			assert expected in result.stderr
	finally:
		for path, content in preserved_files.items():
			if content is None:
				if path.exists():
					path.unlink()
				continue

			path.parent.mkdir(parents=True, exist_ok=True)
			path.write_bytes(content)


def test_ui_bundle_build_emits_runtime_package_manifest_for_explicit_runtime_root(
	tmp_path: Path,
	retail_ui_corpus_inventory: dict[str, object],
) -> None:
	_require_retail_ui_corpus(retail_ui_corpus_inventory)
	build_root = tmp_path / "build"
	artifact_root = tmp_path / "artifacts"
	runtime_root = tmp_path / "runtime" / "baseq3"
	overlay_manifest = artifact_root / "ui_src_retail_overlay.json"
	runtime_package_manifest = artifact_root / "runtime_ui_package_manifest.json"
	main_package = runtime_root / "pak_uiql.pk3"
	overlay_package = runtime_root / "pak_ui_src_retail_overlay.pk3"
	drift = compute_ui_panel_drift(SOURCE_ROOT, RETAIL_ROOT)
	drift_files = _assert_repo_overlay_drift_contract(drift)

	result = subprocess.run(
		[
			sys.executable,
			str(REPO_ROOT / "tools" / "build_ui_bundle.py"),
			"--build-root",
			str(build_root),
			"--artifact-root",
			str(artifact_root),
			"--runtime-root",
			str(runtime_root),
		],
		cwd=REPO_ROOT,
		check=False,
		text=True,
		capture_output=True,
	)

	assert result.returncode == 0, result.stderr
	assert overlay_manifest.exists()
	assert runtime_package_manifest.exists()
	assert main_package.exists()
	assert overlay_package.exists() is bool(drift_files)

	report = json.loads(runtime_package_manifest.read_text(encoding="utf-8"))
	assert report["manifest_version"] == 1
	assert report["runtime_root"] == runtime_root.resolve().as_posix()
	assert report["overlay_manifest_path"] == overlay_manifest.resolve().as_posix()
	assert report["drift_files"] == drift_files
	assert report["main_package"]["path"] == main_package.resolve().as_posix()
	assert report["main_package"]["sha256"] == _sha256_bytes(main_package.read_bytes())
	assert report["main_package"]["required_entries_present"] is True
	assert report["main_package"]["missing_required_entries"] == []
	assert report["overlay_package"]["path"] == overlay_package.resolve().as_posix()
	assert report["overlay_package"]["exists"] is bool(drift_files)
	assert report["overlay_package"]["entry_count"] == len(drift_files)
	assert report["overlay_package"]["entry_paths"] == [f"ui/{relative_path}" for relative_path in drift_files]
	assert report["overlay_package"]["matches_overlay_manifest"] is True
	if drift_files:
		assert report["overlay_package"]["sha256"] == _sha256_bytes(overlay_package.read_bytes())

	with zipfile.ZipFile(main_package, "r") as archive:
		entry_names = set(archive.namelist())

	assert {
		"default.cfg",
		"fonts/font.dat",
		"fonts/font.tga",
		"ui/main.menu",
		"ui/hud3.txt",
		"ui/ingame_scoreboard_ffa.menu",
		"ui/assets/button_back.png",
		"ui/assets/hud/ffa.png",
		"ui/assets/hud/dm.png",
		"ui/assets/hud/tourn.png",
		"ui/assets/score/navbarl.png",
		"ui/assets/score/navbarm.png",
		"ui/assets/score/navbarr.png",
		"ui/assets/score/navleft.png",
		"ui/assets/score/navright.png",
		"ui/assets/score/navfriends.png",
		"ui/assets/score/scoretl.png",
	}.issubset(entry_names)

	if drift_files:
		with zipfile.ZipFile(overlay_package, "r") as archive:
			assert sorted(archive.namelist()) == [f"ui/{relative_path}" for relative_path in drift_files]
