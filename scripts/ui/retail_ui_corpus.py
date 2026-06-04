#!/usr/bin/env python3
"""Shared helpers for validating and inventorying the retail UI corpus."""
from __future__ import annotations

import hashlib
import json
import os
import zipfile
from pathlib import Path
from pathlib import PurePosixPath


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE_MANIFEST = REPO_ROOT / "tools" / "packaging" / "ui_bundle_manifest.json"
REPO_ASSET_BASEQ3_PREFIX = "assets/quakelive/baseq3/"
BASEQ3_SOURCE_PREFIX = "baseq3/"


def _steam_install_candidates() -> list[Path]:
	program_files_x86 = os.environ.get("ProgramFiles(x86)")
	program_files = os.environ.get("ProgramFiles")

	candidates = [
		Path.home() / ".steam" / "steam" / "steamapps" / "common" / "Quake Live" / "baseq3",
		Path.home() / ".local" / "share" / "Steam" / "steamapps" / "common" / "Quake Live" / "baseq3",
		Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/Quake Live/baseq3"),
		Path("/mnt/c/Program Files/Steam/steamapps/common/Quake Live/baseq3"),
	]
	for root in (program_files_x86, program_files):
		if not root:
			continue
		candidates.append(Path(root) / "Steam" / "steamapps" / "common" / "Quake Live" / "baseq3")

	return candidates


def iter_baseq3_root_candidates() -> list[Path]:
	candidates: list[Path] = []
	for env_name in ("QL_RETAIL_BASEQ3_ROOT", "UI_RETAIL_BASEQ3_ROOT"):
		env_value = os.environ.get(env_name)
		if env_value:
			candidates.append(Path(env_value))

	candidates.extend(_steam_install_candidates())

	deduped: list[Path] = []
	seen: set[str] = set()
	for candidate in candidates:
		key = str(candidate).lower()
		if key in seen:
			continue
		seen.add(key)
		deduped.append(candidate)

	return deduped


def detect_default_baseq3_root() -> Path:
	for candidate in iter_baseq3_root_candidates():
		if candidate.exists():
			return candidate
	candidates = iter_baseq3_root_candidates()
	return candidates[0] if candidates else Path("baseq3")


def _normalize_relpath(path: str | Path) -> str:
	return str(path).replace("\\", "/").strip("/")


def _repo_relative(path: Path) -> str:
	try:
		return path.relative_to(REPO_ROOT).as_posix()
	except ValueError:
		return path.as_posix()


def resolve_manifest_source_path(path: str | Path, baseq3_root: Path) -> Path:
	normalized = _normalize_relpath(path)
	if normalized.startswith(BASEQ3_SOURCE_PREFIX):
		return baseq3_root / normalized[len(BASEQ3_SOURCE_PREFIX) :]
	if normalized.startswith(REPO_ASSET_BASEQ3_PREFIX):
		return baseq3_root / normalized[len(REPO_ASSET_BASEQ3_PREFIX) :]

	candidate = Path(path)
	return candidate if candidate.is_absolute() else REPO_ROOT / candidate


def _manifest_entry_relpath(path: str | Path) -> str:
	normalized = _normalize_relpath(path)
	if normalized.startswith(BASEQ3_SOURCE_PREFIX):
		return normalized[len(BASEQ3_SOURCE_PREFIX) :]
	if normalized.startswith(REPO_ASSET_BASEQ3_PREFIX):
		return normalized[len(REPO_ASSET_BASEQ3_PREFIX) :]
	return normalized


def _pak00_path(baseq3_root: Path) -> Path:
	return baseq3_root / "pak00.pk3"


def _matches_include_pattern(relative_path: str, pattern: str) -> bool:
	path_obj = PurePosixPath(relative_path)
	return path_obj.match(pattern) or (pattern.startswith("**/") and path_obj.match(pattern[3:]))


def _archive_file_names(baseq3_root: Path) -> set[str]:
	pak_path = _pak00_path(baseq3_root)
	if not pak_path.is_file():
		return set()

	with zipfile.ZipFile(pak_path) as archive:
		return {
			name.rstrip("/")
			for name in archive.namelist()
			if name and not name.endswith("/")
		}


def _source_rel_exists(baseq3_root: Path, relative_path: str) -> bool:
	normalized = _normalize_relpath(relative_path)
	if (baseq3_root / normalized).is_file():
		return True
	return normalized in _archive_file_names(baseq3_root)


def _source_dir_exists(baseq3_root: Path, relative_path: str) -> bool:
	normalized = _normalize_relpath(relative_path)
	if (baseq3_root / normalized).is_dir():
		return True
	prefix = f"{normalized}/" if normalized else ""
	return any(name.startswith(prefix) for name in _archive_file_names(baseq3_root))


def read_retail_corpus_file(baseq3_root: Path, relative_path: str) -> bytes:
	normalized = _normalize_relpath(relative_path)
	source_path = baseq3_root / normalized
	if source_path.is_file():
		return source_path.read_bytes()

	with zipfile.ZipFile(_pak00_path(baseq3_root)) as archive:
		return archive.read(normalized)


def _record_source(baseq3_root: Path, relative_path: str) -> dict[str, object]:
	normalized = _normalize_relpath(relative_path)
	source_path = baseq3_root / normalized
	if source_path.is_file():
		return _record_file(source_path, baseq3_root)

	data = read_retail_corpus_file(baseq3_root, normalized)
	return {
		"path": normalized,
		"size": len(data),
		"sha256": hashlib.sha256(data).hexdigest(),
		"container": _inventory_relative(_pak00_path(baseq3_root), baseq3_root),
	}


def _collect_matching_source_relpaths(
	baseq3_root: Path,
	source_dir_rel: str,
	include_patterns: list[str],
) -> list[str]:
	normalized_dir = _normalize_relpath(source_dir_rel)
	source_dir = baseq3_root / normalized_dir
	matches: set[str] = set()

	if source_dir.is_dir():
		for match in _collect_matching_files(source_dir, include_patterns):
			matches.add(match.relative_to(baseq3_root).as_posix())

	prefix = f"{normalized_dir}/" if normalized_dir else ""
	for name in _archive_file_names(baseq3_root):
		if not name.startswith(prefix):
			continue
		relative_to_dir = name[len(prefix) :]
		if any(_matches_include_pattern(relative_to_dir, pattern) for pattern in include_patterns):
			matches.add(name)

	return sorted(matches)


def materialize_manifest_corpus(
	baseq3_root: Path,
	output_root: Path | None = None,
	manifest_path: Path = DEFAULT_BUNDLE_MANIFEST,
) -> Path:
	"""Return the retail baseq3 root without copying or extracting assets."""
	return baseq3_root


def collect_files(root: Path) -> set[str]:
	if not root.exists():
		return set()

	return {
		path.relative_to(root).as_posix()
		for path in root.rglob("*")
		if path.is_file()
	}


def _retail_root_context(root: Path) -> tuple[Path, str]:
	if root.name.lower() == "ui":
		return root.parent, "ui"
	return root, ""


def collect_retail_corpus_files(root: Path) -> set[str]:
	if root.exists():
		return collect_files(root)

	baseq3_root, prefix = _retail_root_context(root)
	archive_names = _archive_file_names(baseq3_root)
	if not prefix:
		return archive_names

	archive_prefix = f"{prefix}/"
	return {
		name[len(archive_prefix) :]
		for name in archive_names
		if name.startswith(archive_prefix)
	}


def read_retail_root_file(root: Path, relative_path: str) -> bytes:
	source_path = root / relative_path
	if source_path.is_file():
		return source_path.read_bytes()

	baseq3_root, prefix = _retail_root_context(root)
	archive_path = f"{prefix}/{_normalize_relpath(relative_path)}" if prefix else _normalize_relpath(relative_path)
	return read_retail_corpus_file(baseq3_root, archive_path)


def compute_ui_drift(source_root: Path, retail_root: Path) -> dict[str, object]:
	source_files = collect_files(source_root)
	retail_files = collect_retail_corpus_files(retail_root)
	common_files = sorted(source_files & retail_files)
	content_diffs = [
		relative_path
		for relative_path in common_files
		if (source_root / relative_path).read_bytes() != read_retail_root_file(retail_root, relative_path)
	]

	return {
		"source_root": _repo_relative(source_root),
		"retail_root": _repo_relative(retail_root),
		"source_file_count": len(source_files),
		"retail_file_count": len(retail_files),
		"missing_in_source": sorted(retail_files - source_files),
		"extra_in_source": sorted(source_files - retail_files),
		"content_diffs": content_diffs,
	}


def compute_ui_panel_drift(source_root: Path, retail_root: Path) -> dict[str, object]:
	panel_extensions = {".menu", ".txt"}
	source_files = {
		path.relative_to(source_root).as_posix()
		for path in source_root.rglob("*")
		if path.is_file() and path.suffix in panel_extensions
	}
	retail_files = {
		relative_path
		for relative_path in collect_retail_corpus_files(retail_root)
		if Path(relative_path).suffix in panel_extensions
	}
	common_files = sorted(source_files & retail_files)
	content_diffs = [
		relative_path
		for relative_path in common_files
		if (source_root / relative_path).read_bytes() != read_retail_root_file(retail_root, relative_path)
	]

	return {
		"source_root": _repo_relative(source_root),
		"retail_root": _repo_relative(retail_root),
		"source_file_count": len(source_files),
		"retail_file_count": len(retail_files),
		"missing_in_source": sorted(retail_files - source_files),
		"extra_in_source": sorted(source_files - retail_files),
		"content_diffs": content_diffs,
		"comparison_scope": "runtime-ui-panels",
	}


def load_bundle_manifest(manifest_path: Path = DEFAULT_BUNDLE_MANIFEST) -> dict[str, object]:
	return json.loads(manifest_path.read_text(encoding="utf-8"))


DEFAULT_SOURCE_BASEQ3_ROOT = detect_default_baseq3_root()
DEFAULT_BASEQ3_ROOT = materialize_manifest_corpus(DEFAULT_SOURCE_BASEQ3_ROOT)
DEFAULT_UI_ROOT = DEFAULT_BASEQ3_ROOT / "ui"


def _baseq3_relative(path: Path, baseq3_root: Path) -> str:
	return path.relative_to(baseq3_root).as_posix()


def _inventory_relative(path: Path, baseq3_root: Path) -> str:
	try:
		return _baseq3_relative(path, baseq3_root)
	except ValueError:
		return _repo_relative(path)


def _sha256_file(path: Path) -> str:
	sha256 = hashlib.sha256()
	with path.open("rb") as handle:
		for chunk in iter(lambda: handle.read(1024 * 1024), b""):
			sha256.update(chunk)
	return sha256.hexdigest()


def _record_file(path: Path, baseq3_root: Path) -> dict[str, object]:
	return {
		"path": _inventory_relative(path, baseq3_root),
		"size": path.stat().st_size,
		"sha256": _sha256_file(path),
	}


def _collect_matching_files(source_dir: Path, include_patterns: list[str]) -> list[Path]:
	if not source_dir.is_dir():
		return []

	matches: dict[str, Path] = {}
	for pattern in include_patterns:
		for candidate in source_dir.glob(pattern):
			if candidate.is_file():
				matches[candidate.as_posix()] = candidate

	return [matches[key] for key in sorted(matches)]


def _destination_for_entry(entry: dict[str, object]) -> str:
	return _normalize_relpath(entry["destination"])


def _find_entry_for_staging_path(
	relative_path: str,
	entries: list[dict[str, object]],
) -> dict[str, object] | None:
	normalized_path = _normalize_relpath(relative_path)
	best_entry = None
	best_length = -1

	for entry in entries:
		destination = _destination_for_entry(entry)
		if not destination:
			continue

		if normalized_path == destination or normalized_path.startswith(f"{destination}/"):
			if len(destination) > best_length:
				best_entry = entry
				best_length = len(destination)

	return best_entry


def _source_rel_for_staging_path(
	relative_path: str,
	entries: list[dict[str, object]],
) -> str | None:
	entry = _find_entry_for_staging_path(relative_path, entries)
	if entry is None:
		return None

	destination = _destination_for_entry(entry)
	suffix = _normalize_relpath(relative_path)[len(destination) :].strip("/")

	if "source" in entry:
		if suffix:
			return None
		return _manifest_entry_relpath(entry["source"])

	source_dir_rel = _manifest_entry_relpath(entry["source_dir"])
	return f"{source_dir_rel}/{suffix}" if suffix else source_dir_rel


def _glob_static_prefix(pattern: str) -> str:
	normalized = _normalize_relpath(pattern)
	cut_points = [normalized.find(token) for token in ("*", "?", "[") if token in normalized]
	if not cut_points:
		return normalized

	return normalized[: min(cut_points)].rstrip("/")


def _map_required_staging_glob_to_source(
	pattern: str,
	entries: list[dict[str, object]],
	baseq3_root: Path,
) -> tuple[str | None, list[str]]:
	normalized = _normalize_relpath(pattern)
	entry = _find_entry_for_staging_path(_glob_static_prefix(normalized), entries)
	if entry is None:
		return None, []

	destination = _destination_for_entry(entry)
	suffix = normalized[len(destination) :].strip("/")

	if "source" in entry:
		source_rel = _manifest_entry_relpath(entry["source"])
		matches = [source_rel] if _source_rel_exists(baseq3_root, source_rel) and not suffix else []
		return source_rel, matches

	source_dir_rel = _manifest_entry_relpath(entry["source_dir"])
	matches = _collect_matching_source_relpaths(baseq3_root, source_dir_rel, [suffix or "**/*"])
	source_glob = source_dir_rel
	if suffix:
		source_glob = f"{source_glob}/{suffix}"
	return source_glob, matches


def _dedupe_strings(values: list[str]) -> list[str]:
	seen: set[str] = set()
	result: list[str] = []
	for value in values:
		if value in seen:
			continue
		seen.add(value)
		result.append(value)
	return result


def _categorize_inventory_file(path: str) -> str:
	if path.startswith("ui/assets/"):
		return "ui_asset_files"
	if path.startswith("ui/"):
		return "ui_files"
	if path.startswith("scripts/"):
		return "shader_files"
	if path.startswith("fonts/"):
		return "font_files"
	if path.startswith("icons/"):
		return "icon_files"
	if path.startswith("levelshots/"):
		return "levelshot_files"
	if path.endswith(".cfg"):
		return "config_files"
	return "other_files"


def build_retail_ui_inventory(
	baseq3_root: Path = DEFAULT_BASEQ3_ROOT,
	manifest_path: Path = DEFAULT_BUNDLE_MANIFEST,
) -> dict[str, object]:
	manifest = load_bundle_manifest(manifest_path)
	entries = manifest.get("files", [])
	audit = manifest.get("audit", {})
	missing_required_inputs: list[str] = []
	expected_sources: list[dict[str, object]] = []
	inventory_files: dict[str, dict[str, object]] = {}

	for entry in entries:
		if "source" in entry:
			source_rel = _manifest_entry_relpath(entry["source"])
			exists = _source_rel_exists(baseq3_root, source_rel)
			expected_sources.append(
				{
					"kind": "file",
					"path": source_rel,
					"destination": _destination_for_entry(entry),
					"exists": exists,
				}
			)
			if exists:
				inventory_files[source_rel] = _record_source(baseq3_root, source_rel)
			else:
				missing_required_inputs.append(source_rel)
			continue

		source_dir_rel = _manifest_entry_relpath(entry["source_dir"])
		include_patterns = [_normalize_relpath(pattern) for pattern in entry.get("include", ["**/*"])]
		matches = _collect_matching_source_relpaths(baseq3_root, source_dir_rel, include_patterns)
		source_dir_exists = _source_dir_exists(baseq3_root, source_dir_rel)

		expected_sources.append(
			{
				"kind": "directory",
				"path": source_dir_rel,
				"destination": _destination_for_entry(entry),
				"exists": source_dir_exists,
				"include": include_patterns,
				"match_count": len(matches),
			}
		)

		if not source_dir_exists:
			missing_required_inputs.append(source_dir_rel)
			continue
		if not matches:
			missing_required_inputs.append(f"{source_dir_rel} (no files matched {include_patterns})")
			continue

		for match in matches:
			inventory_files[match] = _record_source(baseq3_root, match)

	required_paths = []
	for relative_path in audit.get("required_paths", []):
		source_rel = _source_rel_for_staging_path(relative_path, entries)
		exists = _source_rel_exists(baseq3_root, source_rel) if source_rel is not None else False
		required_paths.append(
			{
				"staging_path": _normalize_relpath(relative_path),
				"source_path": source_rel,
				"exists": exists,
			}
		)
		if not exists:
			missing_required_inputs.append(source_rel or _normalize_relpath(relative_path))

	required_globs = []
	for pattern in audit.get("required_globs", []):
		source_glob, matches = _map_required_staging_glob_to_source(pattern, entries, baseq3_root)
		required_globs.append(
			{
				"staging_glob": _normalize_relpath(pattern),
				"source_glob": source_glob,
				"match_count": len(matches),
			}
		)
		if not matches:
			missing_required_inputs.append(source_glob or _normalize_relpath(pattern))

	inventory_file_list = [inventory_files[key] for key in sorted(inventory_files)]
	inventory_counts = {
		"files": len(inventory_file_list),
		"ui_files": 0,
		"ui_asset_files": 0,
		"shader_files": 0,
		"font_files": 0,
		"config_files": 0,
		"icon_files": 0,
		"levelshot_files": 0,
		"other_files": 0,
	}

	for record in inventory_file_list:
		inventory_counts[_categorize_inventory_file(record["path"])] += 1

	ui_root = baseq3_root / "ui"
	ui_root_file_count = len(collect_retail_corpus_files(ui_root))
	missing_required_inputs = _dedupe_strings(missing_required_inputs)

	return {
		"baseq3_root": _repo_relative(baseq3_root),
		"bundle_manifest": _repo_relative(manifest_path),
		"retail_ui_root": _baseq3_relative(ui_root, baseq3_root),
		"retail_ui_tree_present": ui_root.is_dir(),
		"retail_ui_pak_present": _pak00_path(baseq3_root).is_file(),
		"retail_ui_tree_file_count": ui_root_file_count,
		"retail_asset_policy": "retail-install-only-no-repo-copy",
		"retail_ui_corpus_available": len(missing_required_inputs) == 0,
		"missing_required_inputs": missing_required_inputs,
		"expected_sources": expected_sources,
		"audit_required_paths": required_paths,
		"audit_required_globs": required_globs,
		"inventory_counts": inventory_counts,
		"inventory_files": inventory_file_list,
	}


def inventory_missing_reason(inventory: dict[str, object], limit: int = 8) -> str:
	if inventory.get("retail_ui_corpus_available"):
		return ""

	missing = inventory.get("missing_required_inputs", [])
	preview = ", ".join(missing[:limit])
	if len(missing) > limit:
		preview = f"{preview}, +{len(missing) - limit} more"

	baseq3_root = inventory.get("baseq3_root", _repo_relative(DEFAULT_BASEQ3_ROOT))
	return (
		f"Retail UI corpus unavailable under {baseq3_root}. "
		f"Set QL_RETAIL_BASEQ3_ROOT to the installed Quake Live baseq3 path or run "
		f"scripts/ui/check_retail_ui_corpus.py for the full missing-input report. Missing: {preview}"
	)


def write_inventory_manifest(output_path: Path, inventory: dict[str, object]) -> None:
	output_path.parent.mkdir(parents=True, exist_ok=True)
	output_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
