#!/usr/bin/env python3
"""Bake Quake Live font assets into deterministic atlas metadata."""
from __future__ import annotations

import argparse
import json
import pathlib
import struct
import sys
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

TARGETS = {
    "font": {"atlas": "font", "point_size": 24},
    "bigFont": {"atlas": "bigfont", "point_size": 48},
    "smallFont": {"atlas": "smallfont", "point_size": 16},
    "mono": {"atlas": "monofont", "point_size": 16},
}


@dataclass
class TableRecord:
    tag: str
    checksum: int
    offset: int
    length: int


class TrueTypeReader:
    def __init__(self, data: bytes) -> None:
        self._data = data
        self._records: Dict[str, TableRecord] = {}
        if len(data) < 12:
            raise ValueError("TTF is truncated; missing offset table")
        scalar_type, num_tables, search_range, entry_selector, range_shift = struct.unpack(
            ">IHHHH", data[:12]
        )
        _ = (scalar_type, search_range, entry_selector, range_shift)
        offset = 12
        for _ in range(num_tables):
            if offset + 16 > len(data):
                raise ValueError("TTF is truncated while reading table records")
            tag = data[offset : offset + 4].decode("ascii")
            checksum, table_offset, length = struct.unpack(
                ">III", data[offset + 4 : offset + 16]
            )
            self._records[tag] = TableRecord(tag, checksum, table_offset, length)
            offset += 16

    def table_slice(self, tag: str) -> bytes:
        record = self._records.get(tag)
        if not record:
            raise KeyError(f"TTF is missing required {tag} table")
        end = record.offset + record.length
        if end > len(self._data):
            raise ValueError(f"TTF table {tag} extends beyond file bounds")
        return self._data[record.offset : end]


@dataclass
class FontMetrics:
    glyphs: int
    units_per_em: int
    ascent: int
    descent: int
    bbox: Tuple[int, int, int, int]


def parse_font_metrics(ttf_path: pathlib.Path) -> FontMetrics:
    data = ttf_path.read_bytes()
    reader = TrueTypeReader(data)

    maxp = reader.table_slice("maxp")
    if len(maxp) < 6:
        raise ValueError("maxp table is truncated")
    glyphs = struct.unpack(">H", maxp[4:6])[0]

    head = reader.table_slice("head")
    if len(head) < 54:
        raise ValueError("head table is truncated")
    units_per_em = struct.unpack(">H", head[18:20])[0]
    bbox = struct.unpack(">hhhh", head[36:44])

    hhea = reader.table_slice("hhea")
    if len(hhea) < 8:
        raise ValueError("hhea table is truncated")
    ascent, descent = struct.unpack(">hh", hhea[4:8])

    return FontMetrics(glyphs, units_per_em, ascent, descent, bbox)


def write_metadata(dat_path: pathlib.Path, atlas_name: str, metrics: FontMetrics, *,
                   point_size: int, source_display: str) -> None:
    lines = [
        "# Auto-generated font atlas metadata for Quake Live HUD validation.",
        f"fontName {atlas_name}",
        f"source {source_display}",
        f"pointSize {point_size}",
        f"glyphCount {metrics.glyphs}",
        f"unitsPerEm {metrics.units_per_em}",
        f"ascent {metrics.ascent}",
        f"descent {metrics.descent}",
        f"bbox {' '.join(str(v) for v in metrics.bbox)}",
        f"timestamp {int(time.time())}",
    ]
    dat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_blank_tga(tga_path: pathlib.Path, *, width: int = 256, height: int = 256) -> None:
    header = bytearray(18)
    header[2] = 2
    header[12:14] = width.to_bytes(2, "little")
    header[14:16] = height.to_bytes(2, "little")
    header[16] = 32
    header[17] = 0x20

    pixel = (0, 0, 0, 0)
    pixel_bytes = bytes(pixel)
    body = pixel_bytes * (width * height)
    tga_path.write_bytes(header + body)


def load_manifest(manifest_path: pathlib.Path) -> Dict:
    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_roles(manifest: Dict, repo_root: pathlib.Path) -> Dict[str, pathlib.Path]:
    role_map: Dict[str, pathlib.Path] = {}
    for entry in manifest.get("files", []):
        source = pathlib.Path(entry["source"])
        if not source.is_absolute():
            source = repo_root / source
        source = source.resolve()
        for role in entry.get("roles", []):
            role_map.setdefault(role, source)
    return role_map


def bake_fonts(manifest_path: pathlib.Path, output_root: pathlib.Path, log_path: pathlib.Path,
               metrics_path: pathlib.Path) -> None:
    manifest = load_manifest(manifest_path)
    repo_root = manifest_path.parents[2].resolve()
    role_map = resolve_roles(manifest, repo_root)

    logs: List[str] = []
    metrics_payload: Dict[str, Dict[str, object]] = {}

    fonts_dir = output_root / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)

    for role, config in TARGETS.items():
        atlas = config["atlas"]
        point_size = config["point_size"]
        source = role_map.get(role)
        if not source:
            raise SystemExit(f"Manifest does not define a font with role '{role}'")
        metrics = parse_font_metrics(source)
        dat_path = fonts_dir / f"{atlas}.dat"
        tga_path = fonts_dir / f"{atlas}.tga"
        try:
            source_display = source.relative_to(repo_root).as_posix()
        except ValueError:
            source_display = source.as_posix()
        write_metadata(dat_path, atlas, metrics, point_size=point_size, source_display=source_display)
        write_blank_tga(tga_path)

        entry = {
            "role": role,
            "atlas": atlas,
            "pointSize": point_size,
            "glyphs": metrics.glyphs,
            "unitsPerEm": metrics.units_per_em,
            "ascent": metrics.ascent,
            "descent": metrics.descent,
            "bbox": metrics.bbox,
            "source": source_display,
        }
        metrics_payload[atlas] = entry
        logs.append(
            f"Baked {role} -> fonts/{atlas}.dat (glyphs={metrics.glyphs}, unitsPerEm={metrics.units_per_em})"
        )

    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(logs) + "\n", encoding="utf-8")

    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")


def main(argv: Iterable[str]) -> int:
    parser = argparse.ArgumentParser(description="Bake UI font atlases for Quake Live testing")
    parser.add_argument("--manifest", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--log", required=True, type=pathlib.Path)
    parser.add_argument("--metrics", required=True, type=pathlib.Path)
    args = parser.parse_args(argv)

    bake_fonts(args.manifest, args.output, args.log, args.metrics)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
