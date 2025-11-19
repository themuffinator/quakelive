#!/usr/bin/env python3
"""Headless UI validation harness for Quake Live HUD assets."""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys
import zipfile
from typing import Dict, List, Tuple

PANELS = [
    "hud.txt",
    "hud2.txt",
    "hud3.menu",
    "default.menu",
    "end_scoreboard_ca.menu",
]
FONT_PATTERN = re.compile(r"\b(font|smallFont|bigFont)\s+\"([^\"]+)\"", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate baked UI assets")
    parser.add_argument("--bundle", type=pathlib.Path, default=pathlib.Path("build/ui_bundle/pak_uiql.pk3"))
    parser.add_argument("--homepath", type=pathlib.Path, default=pathlib.Path("build/ui_validation/home"))
    parser.add_argument("--log-dir", type=pathlib.Path, default=pathlib.Path("artifacts/ui_validation/logs"))
    parser.add_argument("--metrics", type=pathlib.Path, default=pathlib.Path("artifacts/ui_bundle/metrics/font_metrics.json"))
    parser.add_argument("--expected-metrics", type=pathlib.Path,
                        default=pathlib.Path("tests/expectations/ui/font_metrics_quakelive.json"))
    parser.add_argument("--expected-shaders", type=pathlib.Path,
                        default=pathlib.Path("tests/expectations/ui/shader_handles.json"))
    parser.add_argument("--panels-root", type=pathlib.Path, default=pathlib.Path("src/ui"))
    parser.add_argument("--shader-source", type=pathlib.Path,
                        default=pathlib.Path("src/code/cgame/cg_main.c"))
    return parser.parse_args()


def ensure_clean_homepath(homepath: pathlib.Path) -> pathlib.Path:
    if homepath.exists():
        shutil.rmtree(homepath)
    (homepath / "baseq3").mkdir(parents=True, exist_ok=True)
    return homepath / "baseq3"


def extract_bundle(bundle: pathlib.Path, baseq3: pathlib.Path) -> None:
    if not bundle.exists():
        raise SystemExit(f"UI bundle not found: {bundle}")
    with zipfile.ZipFile(bundle, "r") as archive:
        archive.extractall(baseq3)


def inspect_panels(root: pathlib.Path) -> Dict[str, Dict[str, object]]:
    report: Dict[str, Dict[str, object]] = {}
    for panel in PANELS:
        panel_path = root / panel
        if not panel_path.exists():
            report[panel] = {"error": "missing"}
            continue
        text = panel_path.read_text(encoding="utf-8", errors="ignore")
        fonts = sorted({match.group(2) for match in FONT_PATTERN.finditer(text)})
        report[panel] = {
            "fonts": fonts,
            "lineCount": text.count("\n") + 1,
        }
    return report


def verify_metrics(metrics_path: pathlib.Path, expected_path: pathlib.Path) -> Tuple[bool, Dict[str, object]]:
    actual = json.loads(metrics_path.read_text())
    expected = json.loads(expected_path.read_text())
    drifts: List[Dict[str, object]] = []
    for atlas, expectation in expected.items():
        actual_entry = actual.get(atlas)
        if not actual_entry:
            drifts.append({"atlas": atlas, "field": "missing", "expected": expectation})
            continue
        for field, expected_value in expectation.items():
            actual_value = actual_entry.get(field)
            if actual_value != expected_value:
                drifts.append({
                    "atlas": atlas,
                    "field": field,
                    "expected": expected_value,
                    "actual": actual_value,
                })
    return not drifts, {"expected": expected, "actual": actual, "drifts": drifts}


def verify_shaders(shader_source: pathlib.Path, expectations_path: pathlib.Path) -> Tuple[bool, Dict[str, object]]:
    text = shader_source.read_text(encoding="utf-8", errors="ignore")
    expectations = json.loads(expectations_path.read_text())
    missing: Dict[str, List[str]] = {}
    for key, handles in expectations.items():
        missing_handles = [handle for handle in handles if handle not in text]
        if missing_handles:
            missing[key] = missing_handles
    return not missing, {"expected": expectations, "missing": missing}


def main() -> int:
    args = parse_args()
    baseq3 = ensure_clean_homepath(args.homepath)
    extract_bundle(args.bundle, baseq3)

    panels_report = inspect_panels(args.panels_root)
    metrics_ok, metrics_report = verify_metrics(args.metrics, args.expected_metrics)
    shaders_ok, shader_report = verify_shaders(args.shader_source, args.expected_shaders)

    summary = {
        "bundle": args.bundle.as_posix(),
        "homepath": args.homepath.as_posix(),
        "panels": panels_report,
        "glyphMetrics": metrics_report,
        "shaderHandles": shader_report,
    }

    args.log_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.log_dir / "ui_validation_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Panel report written to {summary_path}")

    return 0 if (metrics_ok and shaders_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
