#!/usr/bin/env python3
"""Portable Quake Live UI bundle builder."""
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
	resolve_manifest_source_path,
)


DEFAULT_MANIFEST = REPO_ROOT / "tools" / "packaging" / "ui_bundle_manifest.json"
DEFAULT_BUILD_ROOT = REPO_ROOT / "build" / "ui_bundle"
DEFAULT_ARTIFACT_ROOT = REPO_ROOT / "artifacts" / "ui_bundle"
FONT_BAKE_TOOL = REPO_ROOT / "tools" / "packaging" / "bake_fonts.py"
UI_RETAIL_OVERRIDE_TOOL = REPO_ROOT / "scripts" / "ui" / "write_retail_ui_overrides.py"
UI_RETAIL_CORPUS_TOOL = REPO_ROOT / "scripts" / "ui" / "check_retail_ui_corpus.py"
OVERLAY_PACKAGE_NAME = "pak_ui_src_retail_overlay.pk3"


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Build the retail Quake Live UI bundle and overlay package."
	)
	parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
	parser.add_argument("--baseq3-root", type=Path, default=DEFAULT_BASEQ3_ROOT)
	parser.add_argument("--build-root", type=Path, default=DEFAULT_BUILD_ROOT)
	parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
	return parser.parse_args()


def create_zip(source_dir: Path, output_path: Path) -> None:
	output_path.parent.mkdir(parents=True, exist_ok=True)
	with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
		for candidate in sorted(source_dir.rglob("*")):
			if candidate.is_dir():
				continue
			archive.write(candidate, candidate.relative_to(source_dir).as_posix())


def run_python_step(*args: str | Path) -> int:
	command = [sys.executable]
	command.extend(str(arg) for arg in args)
	return subprocess.run(command, cwd=REPO_ROOT, check=False).returncode


def load_json(path: Path) -> dict[str, object]:
	return json.loads(path.read_text(encoding="utf-8"))


def copy_file(source: Path, destination: Path, staging: Path, logs: list[str]) -> None:
	if not source.is_file():
		raise RuntimeError(f"Missing source file: {source}")

	destination.parent.mkdir(parents=True, exist_ok=True)
	shutil.copy2(source, destination)
	logs.append(f"Copied {source} -> {destination.relative_to(staging).as_posix()}")


def populate_staging(manifest_path: Path, baseq3_root: Path, staging: Path, log_path: Path) -> None:
	manifest = load_json(manifest_path)
	logs: list[str] = []

	for entry in manifest.get("files", []):
		if "source_dir" in entry:
			source_dir = resolve_manifest_source_path(entry["source_dir"], baseq3_root)
			if not source_dir.is_dir():
				raise RuntimeError(f"Manifest source_dir is missing: {source_dir}")

			include_patterns = entry.get("include", ["**/*"])
			matched = False
			for pattern in include_patterns:
				for candidate in source_dir.glob(pattern):
					if candidate.is_dir():
						continue

					relative_path = candidate.relative_to(source_dir)
					destination = staging / entry["destination"] / relative_path
					copy_file(candidate, destination, staging, logs)
					matched = True

			if not matched:
				raise RuntimeError(
					f"No files matched manifest include patterns {include_patterns} under {source_dir}"
				)
			continue

		source = resolve_manifest_source_path(entry["source"], baseq3_root)
		destination = staging / entry["destination"]
		copy_file(source, destination, staging, logs)

	audit = manifest.get("audit", {})
	errors: list[str] = []
	for relative_path in audit.get("required_paths", []):
		target = staging / relative_path
		if not target.exists():
			errors.append(f"Missing required path in staging: {relative_path}")

	for pattern in audit.get("required_globs", []):
		matches = [path for path in staging.glob(pattern) if path.is_file()]
		if not matches:
			errors.append(f"No files matched audit glob '{pattern}' in staging")

	if errors:
		raise RuntimeError(
			"Asset validation failed; required inputs are missing or misplaced\n"
			+ "\n".join(errors)
		)

	log_path.parent.mkdir(parents=True, exist_ok=True)
	log_path.write_text(("\n".join(logs) + "\n") if logs else "", encoding="utf-8")


def main() -> int:
	args = parse_args()

	manifest_path = args.manifest.resolve()
	baseq3_root = args.baseq3_root.resolve()
	build_root = args.build_root.resolve()
	artifact_root = args.artifact_root.resolve()
	staging = build_root / "staging"
	log_dir = artifact_root / "logs"
	metrics_dir = artifact_root / "metrics"
	overlay_build_root = build_root / "src_ui_retail_overlay"
	overlay_staging = overlay_build_root / "staging"
	overlay_manifest_json = artifact_root / "ui_src_retail_overlay.json"
	overlay_pk3_path = build_root / OVERLAY_PACKAGE_NAME
	ui_retail_inventory_json = artifact_root / "ui_retail_inventory.json"
	copy_log = log_dir / "manifest_copy.log"
	bake_log = log_dir / "font_bake.log"
	metrics_json = metrics_dir / "font_metrics.json"

	build_root.mkdir(parents=True, exist_ok=True)
	log_dir.mkdir(parents=True, exist_ok=True)
	metrics_dir.mkdir(parents=True, exist_ok=True)
	artifact_root.mkdir(parents=True, exist_ok=True)
	if staging.exists():
		shutil.rmtree(staging, ignore_errors=True)
	staging.mkdir(parents=True, exist_ok=True)

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

	if overlay_staging.exists():
		shutil.rmtree(overlay_staging, ignore_errors=True)
	overlay_staging.mkdir(parents=True, exist_ok=True)

	if run_python_step(
		UI_RETAIL_OVERRIDE_TOOL,
		"--retail-root",
		baseq3_root / "ui",
		"--homepath-root",
		overlay_staging,
		"--manifest",
		overlay_manifest_json,
		"--overlay-prefix",
		"ui",
	) != 0:
		return 1

	overlay_manifest = load_json(overlay_manifest_json)
	overlay_file_count = len(overlay_manifest.get("overlay_files", []))
	if overlay_pk3_path.exists():
		overlay_pk3_path.unlink()
	if overlay_file_count > 0:
		create_zip(overlay_staging, overlay_pk3_path)
		shutil.copy2(overlay_pk3_path, artifact_root / OVERLAY_PACKAGE_NAME)

	manifest = load_json(manifest_path)
	package_name = str(manifest["package"])

	try:
		populate_staging(manifest_path, baseq3_root, staging, copy_log)
	except RuntimeError as exc:
		print(str(exc), file=sys.stderr)
		return 1

	if run_python_step(
		FONT_BAKE_TOOL,
		"--manifest",
		manifest_path,
		"--output",
		staging,
		"--log",
		bake_log,
		"--metrics",
		metrics_json,
		"--baseq3-root",
		baseq3_root,
	) != 0:
		return 1

	pk3_path = build_root / package_name
	if pk3_path.exists():
		pk3_path.unlink()
	create_zip(staging, pk3_path)
	shutil.copy2(pk3_path, artifact_root / package_name)

	print("UI bundle complete.")
	print(f"  package: {pk3_path}")
	print(f"  src/ui retail overlay: {overlay_pk3_path}")
	print(f"  src/ui overlay manifest: {overlay_manifest_json}")
	print(f"  retail ui inventory: {ui_retail_inventory_json}")
	print(f"  manifest log: {copy_log}")
	print(f"  font bake log: {bake_log}")
	print(f"  font metrics: {metrics_json}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
