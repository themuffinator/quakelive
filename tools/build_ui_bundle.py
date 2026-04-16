#!/usr/bin/env python3
"""Prepare local UI validation artifacts without duplicating retail PK3 content."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


if __package__ in (None, ""):
	sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ui.retail_ui_corpus import (  # noqa: E402
	DEFAULT_BASEQ3_ROOT,
	REPO_ROOT,
	load_bundle_manifest,
	resolve_manifest_source_path,
)


DEFAULT_MANIFEST = REPO_ROOT / "tools" / "packaging" / "ui_bundle_manifest.json"
DEFAULT_BUILD_ROOT = REPO_ROOT / "build" / "ui_bundle"
DEFAULT_ARTIFACT_ROOT = REPO_ROOT / "artifacts" / "ui_bundle"
FONT_BAKE_TOOL = REPO_ROOT / "tools" / "packaging" / "bake_fonts.py"
UI_RETAIL_OVERRIDE_TOOL = REPO_ROOT / "scripts" / "ui" / "write_retail_ui_overrides.py"
UI_RETAIL_CORPUS_TOOL = REPO_ROOT / "scripts" / "ui" / "check_retail_ui_corpus.py"
RETAIL_UI_PACKAGE_NAME = "pak_uiql.pk3"
OVERLAY_PACKAGE_NAME = "pak_ui_src_retail_overlay.pk3"

# The Steam-era retail UI pack carries several renamed PNG assets while the
# native menus still request the legacy symbolic names. Stage compatibility
# aliases so the renderer's existing .tga -> .png fallback can resolve them.
RUNTIME_UI_COMPATIBILITY_ALIASES: tuple[tuple[str, str], ...] = (
	("ui/assets/hud/ffa.png", "ui/assets/hud/dm.png"),
	("ui/assets/hud/duel.png", "ui/assets/hud/tourn.png"),
	("ui/assets/score/flagr.png", "ui/assets/redchip.png"),
	("ui/assets/score/flagb.png", "ui/assets/bluechip.png"),
	("ui/assets/score/specl.png", "ui/assets/score/navbarl.png"),
	("ui/assets/score/specm.png", "ui/assets/score/navbarm.png"),
	("ui/assets/score/specr.png", "ui/assets/score/navbarr.png"),
	("ui/assets/score/btn.png", "ui/assets/score/navleft.png"),
	("ui/assets/score/btn.png", "ui/assets/score/navright.png"),
	("ui/assets/score/scorebox_follow.png", "ui/assets/score/navfriends.png"),
)


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Prepare local UI validation artifacts without packaging retail Quake Live data."
	)
	parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
	parser.add_argument("--baseq3-root", type=Path, default=DEFAULT_BASEQ3_ROOT)
	parser.add_argument("--build-root", type=Path, default=DEFAULT_BUILD_ROOT)
	parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
	parser.add_argument(
		"--runtime-root",
		type=Path,
		default=None,
		help=(
			"Optional writable baseq3 runtime root that should receive refreshed "
			"pak_uiql.pk3 and pak_ui_src_retail_overlay.pk3 artifacts."
		),
	)
	return parser.parse_args()


def run_python_step(*args: str | Path) -> int:
	command = [sys.executable]
	command.extend(str(arg) for arg in args)
	return subprocess.run(command, cwd=REPO_ROOT, check=False).returncode


def _iter_manifest_matches(source_dir: Path, include_patterns: list[str]) -> list[Path]:
	matches: dict[str, Path] = {}

	if not source_dir.is_dir():
		return []

	for pattern in include_patterns:
		for candidate in source_dir.glob(pattern):
			if candidate.is_file():
				matches[candidate.as_posix()] = candidate

	return [matches[key] for key in sorted(matches)]


def _copy_file(source_path: Path, destination_path: Path) -> None:
	destination_path.parent.mkdir(parents=True, exist_ok=True)
	shutil.copy2(source_path, destination_path)


def stage_runtime_compatibility_aliases(staging_baseq3: Path) -> None:
	for source_relpath, alias_relpath in RUNTIME_UI_COMPATIBILITY_ALIASES:
		source_path = staging_baseq3 / Path(source_relpath)
		if not source_path.is_file():
			raise FileNotFoundError(
				f"Required UI compatibility alias source was not found: {source_path}"
			)

		alias_path = staging_baseq3 / Path(alias_relpath)
		_copy_file(source_path, alias_path)


def stage_runtime_bundle(
	manifest_path: Path,
	baseq3_root: Path,
	build_root: Path,
	font_output: Path,
) -> Path:
	manifest = load_bundle_manifest(manifest_path)
	staging_root = build_root / "staging"
	staging_baseq3 = staging_root / "baseq3"
	font_runtime_root = font_output / "fonts"

	if staging_root.exists():
		shutil.rmtree(staging_root, ignore_errors=True)
	staging_baseq3.mkdir(parents=True, exist_ok=True)

	for entry in manifest.get("files", []):
		destination_root = staging_baseq3 / Path(entry["destination"])

		if "source" in entry:
			source_path = resolve_manifest_source_path(entry["source"], baseq3_root)
			if not source_path.is_file():
				raise FileNotFoundError(f"Required UI bundle input was not found: {source_path}")
			_copy_file(source_path, destination_root)
			continue

		source_dir = resolve_manifest_source_path(entry["source_dir"], baseq3_root)
		include_patterns = [str(pattern) for pattern in entry.get("include", ["**/*"])]
		matches = _iter_manifest_matches(source_dir, include_patterns)
		if not matches:
			raise FileNotFoundError(
				f"Required UI bundle directory was not found or matched no files: {source_dir} ({include_patterns})"
			)

		for match in matches:
			relative_path = match.relative_to(source_dir)
			_copy_file(match, destination_root / relative_path)

	if font_runtime_root.is_dir():
		for font_artifact in font_runtime_root.iterdir():
			if font_artifact.is_file():
				_copy_file(font_artifact, staging_baseq3 / "fonts" / font_artifact.name)

	stage_runtime_compatibility_aliases(staging_baseq3)

	return staging_root


def _iter_tree_files(root: Path) -> list[Path]:
	return sorted((path for path in root.rglob("*") if path.is_file()), key=lambda path: path.as_posix())


def _write_pk3_from_tree(source_root: Path, output_path: Path) -> None:
	output_path.parent.mkdir(parents=True, exist_ok=True)
	if output_path.exists():
		output_path.unlink()

	with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
		for file_path in _iter_tree_files(source_root):
			archive.write(file_path, file_path.relative_to(source_root).as_posix())


def emit_runtime_packages(
	staging_root: Path,
	overlay_manifest_path: Path,
	runtime_root: Path,
) -> tuple[Path, Path | None]:
	staging_baseq3 = staging_root / "baseq3"
	main_package_path = runtime_root / RETAIL_UI_PACKAGE_NAME
	overlay_package_path = runtime_root / OVERLAY_PACKAGE_NAME

	if not staging_baseq3.is_dir():
		raise FileNotFoundError(f"Runtime staging root was not found: {staging_baseq3}")

	runtime_root.mkdir(parents=True, exist_ok=True)
	_write_pk3_from_tree(staging_baseq3, main_package_path)

	if overlay_package_path.exists():
		overlay_package_path.unlink()

	overlay_manifest = json.loads(overlay_manifest_path.read_text(encoding="utf-8"))
	overlay_entries = overlay_manifest.get("overlay_entries", [])
	if not overlay_entries:
		return main_package_path, None

	with zipfile.ZipFile(overlay_package_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
		for entry in overlay_entries:
			source_path = REPO_ROOT / entry["retail_source_path"]
			archive_path = str(entry["overlay_path"]).replace("\\", "/")
			if archive_path.startswith("baseq3/"):
				archive_path = archive_path[len("baseq3/") :]

			if not source_path.is_file():
				raise FileNotFoundError(f"Runtime overlay source was not found: {source_path}")

			archive.write(source_path, archive_path)

	return main_package_path, overlay_package_path


def main() -> int:
	args = parse_args()

	manifest_path = args.manifest.resolve()
	baseq3_root = args.baseq3_root.resolve()
	build_root = args.build_root.resolve()
	artifact_root = args.artifact_root.resolve()
	runtime_root = args.runtime_root.resolve() if args.runtime_root else None
	font_output = build_root / "font_validation"
	staging_root = build_root / "staging"
	log_dir = artifact_root / "logs"
	metrics_dir = artifact_root / "metrics"
	overlay_manifest_json = artifact_root / "ui_src_retail_overlay.json"
	ui_retail_inventory_json = artifact_root / "ui_retail_inventory.json"
	bake_log = log_dir / "font_bake.log"
	metrics_json = metrics_dir / "font_metrics.json"
	stale_package_paths = (
		build_root / RETAIL_UI_PACKAGE_NAME,
		artifact_root / RETAIL_UI_PACKAGE_NAME,
		build_root / OVERLAY_PACKAGE_NAME,
		artifact_root / OVERLAY_PACKAGE_NAME,
	)

	build_root.mkdir(parents=True, exist_ok=True)
	log_dir.mkdir(parents=True, exist_ok=True)
	metrics_dir.mkdir(parents=True, exist_ok=True)
	artifact_root.mkdir(parents=True, exist_ok=True)
	if staging_root.exists():
		shutil.rmtree(staging_root, ignore_errors=True)
	if font_output.exists():
		shutil.rmtree(font_output, ignore_errors=True)
	font_output.mkdir(parents=True, exist_ok=True)
	for stale_path in stale_package_paths:
		if stale_path.exists():
			stale_path.unlink()

	if run_python_step(
		UI_RETAIL_CORPUS_TOOL,
		"--baseq3-root",
		baseq3_root,
		"--bundle-manifest",
		manifest_path,
		"--inventory-out",
		ui_retail_inventory_json,
		"--strict",
	) != 0:
		return 1

	if run_python_step(
		UI_RETAIL_OVERRIDE_TOOL,
		"--retail-root",
		baseq3_root / "ui",
		"--manifest",
		overlay_manifest_json,
	) != 0:
		return 1

	if run_python_step(
		FONT_BAKE_TOOL,
		"--manifest",
		manifest_path,
		"--output",
		font_output,
		"--log",
		bake_log,
		"--metrics",
		metrics_json,
		"--baseq3-root",
		baseq3_root,
	) != 0:
		return 1

	staged_runtime_root = stage_runtime_bundle(
		manifest_path=manifest_path,
		baseq3_root=baseq3_root,
		build_root=build_root,
		font_output=font_output,
	)
	runtime_package_paths: tuple[Path, Path | None] | None = None
	if runtime_root is not None:
		runtime_package_paths = emit_runtime_packages(
			staging_root=staged_runtime_root,
			overlay_manifest_path=overlay_manifest_json,
			runtime_root=runtime_root,
		)

	print("UI validation inputs prepared.")
	print(f"  retail baseq3 root: {baseq3_root}")
	print(f"  runtime staging root: {staged_runtime_root}")
	if runtime_package_paths is not None:
		print(f"  runtime ui package: {runtime_package_paths[0]}")
		if runtime_package_paths[1] is not None:
			print(f"  runtime overlay package: {runtime_package_paths[1]}")
	print(f"  font validation output: {font_output}")
	print(f"  src/ui overlay manifest: {overlay_manifest_json}")
	print(f"  retail ui inventory: {ui_retail_inventory_json}")
	print(f"  font bake log: {bake_log}")
	print(f"  font metrics: {metrics_json}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
