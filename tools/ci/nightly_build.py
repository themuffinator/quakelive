#!/usr/bin/env python3
"""Version and package hosted nightly build artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Iterable


REQUIRED_WINDOWS_OUTPUTS = (
    ("build/win32/{configuration}/bin/quakelive_steam.exe", "quakelive_steam.exe"),
    ("build/win32/{configuration}/bin/awesomium_process.exe", "awesomium_process.exe"),
    ("build/win32/{configuration}/modules/qagamex86/qagamex86.dll", "baseq3/qagamex86.dll"),
    ("build/win32/{configuration}/modules/cgamex86/cgamex86.dll", "baseq3/cgamex86.dll"),
    ("build/win32/{configuration}/bin/baseq3/uix86.dll", "baseq3/uix86.dll"),
)

OPTIONAL_WINDOWS_OUTPUTS = (
    ("build/win32/{configuration}/bin/qzeroded.exe", "qzeroded.exe"),
)


def run_git(repo_root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stderr=subprocess.DEVNULL,
    ).strip()


def github_output_path(explicit_path: str | None) -> Path | None:
    path = explicit_path or os.environ.get("GITHUB_OUTPUT")
    if not path:
        return None
    return Path(path)


def append_github_outputs(path: Path | None, values: dict[str, str]) -> None:
    if path is None:
        return

    with path.open("a", encoding="utf-8", newline="\n") as output:
        for key, value in values.items():
            output.write(f"{key}={value}\n")


def normalise_sha(repo_root: Path, sha: str | None) -> str:
    if sha:
        return sha
    env_sha = os.environ.get("GITHUB_SHA")
    if env_sha:
        return env_sha
    return run_git(repo_root, "rev-parse", "HEAD")


def normalise_ref(repo_root: Path, ref_name: str | None) -> str:
    if ref_name:
        return ref_name
    env_ref = os.environ.get("GITHUB_REF_NAME")
    if env_ref:
        return env_ref
    return run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD")


def normalise_run_number(run_number: str | None) -> str:
    return run_number or os.environ.get("GITHUB_RUN_NUMBER") or "local"


def normalise_run_attempt(run_attempt: str | None) -> str:
    return run_attempt or os.environ.get("GITHUB_RUN_ATTEMPT") or "1"


def utc_build_date(explicit_date: str | None) -> str:
    if explicit_date:
        try:
            dt.datetime.strptime(explicit_date, "%Y%m%d")
        except ValueError as exc:
            raise SystemExit("--date-utc must use YYYYMMDD format") from exc
        return explicit_date
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_path_under(path: Path, root: Path) -> Path:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise SystemExit(f"Refusing to operate outside {resolved_root}: {resolved_path}") from exc
    return resolved_path


def repo_relative_path(repo_root: Path, path: Path) -> Path:
    if path.is_absolute():
        return path
    return repo_root / path


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_version(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    sha = normalise_sha(repo_root, args.sha)
    short_sha = sha[:12]
    ref_name = normalise_ref(repo_root, args.ref_name)
    run_number = normalise_run_number(args.run_number)
    run_attempt = normalise_run_attempt(args.run_attempt)
    build_date = utc_build_date(args.date_utc)

    version = f"0.0.0-{args.channel}.{build_date}.{run_number}+g{short_sha}"
    artifact_version = f"{args.channel}-{build_date}.{run_number}-g{short_sha}"
    generated_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    payload = {
        "artifactVersion": artifact_version,
        "buildDateUtc": build_date,
        "channel": args.channel,
        "generatedAtUtc": generated_at,
        "runAttempt": run_attempt,
        "runNumber": run_number,
        "semver": version,
        "sourceRef": ref_name,
        "sourceSha": sha,
    }

    output_path = repo_relative_path(repo_root, args.output)
    write_json(output_path, payload)
    append_github_outputs(
        github_output_path(args.github_output),
        {
            "artifact_version": artifact_version,
            "build_date_utc": build_date,
            "semver": version,
            "short_sha": short_sha,
        },
    )

    print(f"Nightly version: {artifact_version} ({version})")
    return 0


def copy_required_outputs(repo_root: Path, stage_root: Path, configuration: str) -> list[dict]:
    copied: list[dict] = []
    missing: list[str] = []

    for source_template, destination in REQUIRED_WINDOWS_OUTPUTS:
        source = repo_root / source_template.format(configuration=configuration)
        if not source.exists():
            missing.append(str(source.relative_to(repo_root)))
            continue
        copied.append(copy_artifact(source, stage_root / destination, stage_root))

    if missing:
        missing_list = "\n".join(f"  - {item}" for item in missing)
        raise SystemExit(f"Missing required nightly build outputs:\n{missing_list}")

    for source_template, destination in OPTIONAL_WINDOWS_OUTPUTS:
        source = repo_root / source_template.format(configuration=configuration)
        if source.exists():
            copied.append(copy_artifact(source, stage_root / destination, stage_root))

    return copied


def copy_optional_globs(repo_root: Path, stage_root: Path) -> list[dict]:
    copied: list[dict] = []
    for source in sorted((repo_root / "build/re/windows").glob("*.dll")):
        copied.append(copy_artifact(source, stage_root / "clean-room" / source.name, stage_root))

    ui_bundle = repo_root / "artifacts/ui_bundle/pak_uiql.pk3"
    if ui_bundle.exists():
        copied.append(copy_artifact(ui_bundle, stage_root / "baseq3/pak_uiql.pk3", stage_root))

    return copied


def copy_artifact(source: Path, destination: Path, stage_root: Path) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    staged_relative = destination.relative_to(stage_root).as_posix()
    return {
        "path": staged_relative,
        "sha256": sha256_file(destination),
        "size": destination.stat().st_size,
    }


def write_readme(stage_root: Path, manifest: dict, runtime_profile: str, toolset: str) -> dict:
    readme = stage_root / "README-nightly.txt"
    lines = [
        "QuakeLive-reverse nightly build",
        "",
        f"Version: {manifest['artifactVersion']}",
        f"Source: {manifest['sourceSha']}",
        f"Reference: {manifest['sourceRef']}",
        f"Toolset: {toolset}",
        f"Runtime profile: {runtime_profile}",
        "",
        "This package contains rebuilt project outputs only.",
        "It does not include retail pk3 files, retail launcher DLL payloads, or live online-service credentials.",
        "Quake Live-only online services remain disabled by default behind QL_BUILD_ONLINE_SERVICES.",
    ]
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "path": readme.relative_to(stage_root).as_posix(),
        "sha256": sha256_file(readme),
        "size": readme.stat().st_size,
    }


def zip_directory(source_root: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_root.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(source_root).as_posix())


def build_package_manifest(
    manifest: dict,
    package_path: Path,
    files: Iterable[dict],
    runtime_profile: str,
    toolset: str,
    configuration: str,
) -> dict:
    package_hash = sha256_file(package_path)
    return {
        "artifactVersion": manifest["artifactVersion"],
        "configuration": configuration,
        "files": list(files),
        "package": {
            "name": package_path.name,
            "sha256": package_hash,
            "size": package_path.stat().st_size,
        },
        "runtimeProfile": runtime_profile,
        "sourceRef": manifest["sourceRef"],
        "sourceSha": manifest["sourceSha"],
        "toolset": toolset,
    }


def package_build(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    output_root = ensure_path_under(repo_relative_path(repo_root, args.output_root), repo_root)
    manifest_path = repo_relative_path(repo_root, args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifact_version = manifest["artifactVersion"]

    stage_root = ensure_path_under(output_root / "staging" / artifact_version, repo_root)
    if stage_root.exists():
        shutil.rmtree(stage_root)
    stage_root.mkdir(parents=True)

    files = copy_required_outputs(repo_root, stage_root, args.configuration)
    files.extend(copy_optional_globs(repo_root, stage_root))
    manifest_destination = stage_root / "build-manifest.json"
    write_json(manifest_destination, manifest)
    files.append(
        {
            "path": manifest_destination.relative_to(stage_root).as_posix(),
            "sha256": sha256_file(manifest_destination),
            "size": manifest_destination.stat().st_size,
        }
    )
    files.append(write_readme(stage_root, manifest, args.runtime_profile, args.toolset))

    package_name = f"QuakeLive-reverse-{artifact_version}-windows-{args.runtime_profile}.zip"
    package_path = output_root / package_name
    zip_directory(stage_root, package_path)

    package_manifest = build_package_manifest(
        manifest,
        package_path,
        files,
        args.runtime_profile,
        args.toolset,
        args.configuration,
    )
    package_manifest_path = output_root / f"{artifact_version}-package-manifest.json"
    write_json(package_manifest_path, package_manifest)

    checksum_path = output_root / "checksums.sha256"
    checksum_path.write_text(
        f"{package_manifest['package']['sha256']}  {package_name}\n",
        encoding="utf-8",
    )

    append_github_outputs(
        github_output_path(args.github_output),
        {
            "checksum_path": str(checksum_path),
            "package_name": package_name,
            "package_path": str(package_path),
        },
    )

    print(f"Nightly package: {package_path}")
    print(f"SHA256: {package_manifest['package']['sha256']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    version = subparsers.add_parser("version", help="write nightly version metadata")
    version.add_argument("--repo-root", type=Path, default=Path("."))
    version.add_argument("--channel", default="nightly")
    version.add_argument("--date-utc")
    version.add_argument("--github-output")
    version.add_argument("--output", type=Path, required=True)
    version.add_argument("--ref-name")
    version.add_argument("--run-attempt")
    version.add_argument("--run-number")
    version.add_argument("--sha")
    version.set_defaults(func=build_version)

    package = subparsers.add_parser("package", help="package built nightly outputs")
    package.add_argument("--repo-root", type=Path, default=Path("."))
    package.add_argument("--configuration", default="Release")
    package.add_argument("--github-output")
    package.add_argument("--manifest", type=Path, required=True)
    package.add_argument("--output-root", type=Path, default=Path("artifacts/nightly"))
    package.add_argument("--runtime-profile", default="modern")
    package.add_argument("--toolset", default="v143")
    package.set_defaults(func=package_build)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
