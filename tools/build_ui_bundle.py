#!/usr/bin/env python3
"""Validate retail UI inputs without copying or packaging retail assets."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


if __package__ in (None, ""):
	sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ui.retail_ui_corpus import (  # noqa: E402
	DEFAULT_BASEQ3_ROOT,
	REPO_ROOT,
)


DEFAULT_MANIFEST = REPO_ROOT / "tools" / "packaging" / "ui_bundle_manifest.json"
DEFAULT_BUILD_ROOT = REPO_ROOT / "build" / "ui_bundle"
DEFAULT_ARTIFACT_ROOT = REPO_ROOT / "artifacts" / "ui_bundle"
UI_RETAIL_OVERRIDE_TOOL = REPO_ROOT / "scripts" / "ui" / "write_retail_ui_overrides.py"
UI_RETAIL_CORPUS_TOOL = REPO_ROOT / "scripts" / "ui" / "check_retail_ui_corpus.py"
RETAIL_UI_PACKAGE_NAME = "pak_uiql.pk3"
OVERLAY_PACKAGE_NAME = "pak_ui_src_retail_overlay.pk3"
RUNTIME_PACKAGE_MANIFEST_NAME = "runtime_ui_package_manifest.json"


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Validate the installed Quake Live UI corpus without copying retail assets."
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
			"Optional writable baseq3 runtime root to clean of stale generated UI packages. "
			"No retail package is emitted."
		),
	)
	return parser.parse_args()


def run_python_step(*args: str | Path) -> int:
	command = [sys.executable]
	command.extend(str(arg) for arg in args)
	return subprocess.run(command, cwd=REPO_ROOT, check=False).returncode


def _display_path(path: Path) -> str:
	try:
		return path.resolve().relative_to(REPO_ROOT).as_posix()
	except ValueError:
		return path.resolve().as_posix()


def _sha256_file(path: Path) -> str:
	digest = hashlib.sha256()
	with path.open("rb") as handle:
		for chunk in iter(lambda: handle.read(1024 * 1024), b""):
			digest.update(chunk)
	return digest.hexdigest()


def _remove_path(path: Path) -> bool:
	if path.is_dir():
		shutil.rmtree(path, ignore_errors=True)
		return True
	if path.exists():
		path.unlink()
		return True
	return False


def clean_generated_asset_outputs(
	build_root: Path,
	artifact_root: Path,
	runtime_root: Path | None,
) -> list[str]:
	candidates = [
		build_root / "staging",
		build_root / "font_validation",
		build_root / RETAIL_UI_PACKAGE_NAME,
		build_root / OVERLAY_PACKAGE_NAME,
		artifact_root / RETAIL_UI_PACKAGE_NAME,
		artifact_root / OVERLAY_PACKAGE_NAME,
		artifact_root / "metrics" / "font_metrics.json",
	]
	if runtime_root is not None:
		candidates.extend(
			[
				runtime_root / RETAIL_UI_PACKAGE_NAME,
				runtime_root / OVERLAY_PACKAGE_NAME,
			]
		)

	removed: list[str] = []
	for candidate in candidates:
		if _remove_path(candidate):
			removed.append(_display_path(candidate))

	return sorted(removed)


def write_runtime_policy_manifest(
	manifest_path: Path,
	runtime_root: Path | None,
	baseq3_root: Path,
	overlay_manifest_path: Path,
	removed_paths: list[str],
) -> None:
	overlay_manifest = json.loads(overlay_manifest_path.read_text(encoding="utf-8"))
	report: dict[str, object] = {
		"manifest_version": 2,
		"asset_policy": "retail-install-only-no-repo-copy",
		"runtime_root": _display_path(runtime_root) if runtime_root is not None else "",
		"retail_baseq3_root": _display_path(baseq3_root),
		"overlay_manifest_path": _display_path(overlay_manifest_path),
		"overlay_manifest_sha256": _sha256_file(overlay_manifest_path),
		"retail_ui_corpus_available": overlay_manifest.get("retail_ui_corpus_available"),
		"drift_files": overlay_manifest.get("drift_files", []),
		"removed_generated_asset_outputs": removed_paths,
		"main_package": {
			"path": _display_path((runtime_root or Path()) / RETAIL_UI_PACKAGE_NAME)
			if runtime_root is not None
			else "",
			"exists": False,
			"emitted": False,
			"reason": "Retail UI assets are loaded from the installed Quake Live baseq3/pak00.pk3.",
		},
		"overlay_package": {
			"path": _display_path((runtime_root or Path()) / OVERLAY_PACKAGE_NAME)
			if runtime_root is not None
			else "",
			"exists": False,
			"emitted": False,
			"entry_count": 0,
			"entry_paths": [],
			"matches_overlay_manifest": not overlay_manifest.get("overlay_entries", []),
		},
	}

	manifest_path.parent.mkdir(parents=True, exist_ok=True)
	manifest_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
	args = parse_args()

	manifest_path = args.manifest.resolve()
	baseq3_root = args.baseq3_root.resolve()
	build_root = args.build_root.resolve()
	artifact_root = args.artifact_root.resolve()
	runtime_root = args.runtime_root.resolve() if args.runtime_root else None
	log_dir = artifact_root / "logs"
	overlay_manifest_json = artifact_root / "ui_src_retail_overlay.json"
	ui_retail_inventory_json = artifact_root / "ui_retail_inventory.json"
	runtime_package_manifest_json = artifact_root / RUNTIME_PACKAGE_MANIFEST_NAME

	build_root.mkdir(parents=True, exist_ok=True)
	log_dir.mkdir(parents=True, exist_ok=True)
	artifact_root.mkdir(parents=True, exist_ok=True)

	removed_paths = clean_generated_asset_outputs(build_root, artifact_root, runtime_root)

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

	write_runtime_policy_manifest(
		manifest_path=runtime_package_manifest_json,
		runtime_root=runtime_root,
		baseq3_root=baseq3_root,
		overlay_manifest_path=overlay_manifest_json,
		removed_paths=removed_paths,
	)

	print("Retail UI validation inputs verified without copying assets.")
	print(f"  retail baseq3 root: {baseq3_root}")
	print(f"  src/ui overlay manifest: {overlay_manifest_json}")
	print(f"  retail ui inventory: {ui_retail_inventory_json}")
	print(f"  runtime policy manifest: {runtime_package_manifest_json}")
	if removed_paths:
		print("  removed stale generated asset outputs:")
		for removed_path in removed_paths:
			print(f"    {removed_path}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
