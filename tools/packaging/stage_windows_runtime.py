#!/usr/bin/env python3
import argparse
import json
import pathlib
import shutil
import sys
import urllib.request


def _write_log(log_path: pathlib.Path, lines: list[str]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _download_file(url: str, dest: pathlib.Path) -> None:
    with urllib.request.urlopen(url) as response:
        dest.write_bytes(response.read())


def stage_runtime(manifest_path: pathlib.Path, output_root: pathlib.Path, log_path: pathlib.Path,
                  include_proprietary: bool, fetch_urls: bool) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    repo_root = manifest_path.parents[2].resolve()
    files = manifest.get("files", [])
    if not files:
        raise RuntimeError("Manifest does not define any files.")

    output_root.mkdir(parents=True, exist_ok=True)
    log_lines: list[str] = []

    for entry in files:
        name = entry.get("name", "<unnamed>")
        if entry.get("proprietary") and not include_proprietary:
            log_lines.append(f"SKIP proprietary: {name}")
            continue
        destination = entry.get("destination")
        if not destination:
            raise RuntimeError(f"Entry missing destination: {entry}")
        dest_path = output_root / destination
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if "source" in entry:
            source = repo_root / entry["source"]
            if not source.exists():
                raise FileNotFoundError(f"Missing source file: {source}")
            shutil.copy2(source, dest_path)
            log_lines.append(f"COPY {name}: {source} -> {dest_path}")
        elif "url" in entry:
            if not fetch_urls:
                raise RuntimeError(f"URL fetch disabled for {name}: {entry['url']}")
            _download_file(entry["url"], dest_path)
            log_lines.append(f"FETCH {name}: {entry['url']} -> {dest_path}")
        else:
            raise RuntimeError(f"Entry missing source or url: {entry}")

    _write_log(log_path, log_lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage Windows runtime dependencies.")
    parser.add_argument("--manifest", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--log", required=True, type=pathlib.Path)
    parser.add_argument("--include-proprietary", action="store_true")
    parser.add_argument("--fetch-urls", action="store_true")
    args = parser.parse_args()

    stage_runtime(
        manifest_path=args.manifest,
        output_root=args.output,
        log_path=args.log,
        include_proprietary=args.include_proprietary,
        fetch_urls=args.fetch_urls,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
