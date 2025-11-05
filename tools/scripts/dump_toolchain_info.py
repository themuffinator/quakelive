#!/usr/bin/env python3
"""Extract linker and debug metadata from PE binaries."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path
from typing import Any, Dict, List

import pefile


def _read_fileinfo(pe: pefile.PE) -> Dict[str, str]:
    strings: Dict[str, str] = {}
    for fileinfo in getattr(pe, "FileInfo", []) or []:
        for st in fileinfo:
            if hasattr(st, "StringTable"):
                for entry in st.StringTable:
                    for key, value in entry.entries.items():
                        try:
                            decoded_key = key.decode()
                            decoded_val = value.decode("utf-8", "ignore")
                        except Exception:
                            continue
                        strings.setdefault(decoded_key, decoded_val)
    return strings


def _read_debug(pe: pefile.PE) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    if not hasattr(pe, "DIRECTORY_ENTRY_DEBUG"):
        return results
    for dbg in pe.DIRECTORY_ENTRY_DEBUG:
        entry = dbg.entry
        debug_type = getattr(dbg.struct, "Type", None)
        desc: Dict[str, Any] = {"type": debug_type}
        if debug_type == 2 and hasattr(entry, "CvSignature"):
            pdb_bytes = entry.PdbFileName.rstrip(b"\x00")
            guid = (
                f"{entry.Signature_Data1:08X}-"
                f"{entry.Signature_Data2:04X}-"
                f"{entry.Signature_Data3:04X}-"
                f"{entry.Signature_Data4:02X}{entry.Signature_Data5:02X}-"
                f"{entry.Signature_Data6.hex().upper()}"
            )
            desc.update(
                {
                    "format": entry.CvSignature.decode("ascii", "ignore"),
                    "guid": guid,
                    "age": entry.Age,
                    "pdb_path": pdb_bytes.decode("utf-8", "ignore"),
                }
            )
        results.append(desc)
    return results


DLL_CHARACTERISTICS_FLAGS = {
    0x0040: "DYNAMIC_BASE",
    0x0080: "FORCE_INTEGRITY",
    0x0100: "NX_COMPAT",
    0x0200: "NO_ISOLATION",
    0x0400: "NO_SEH",
    0x0800: "NO_BIND",
    0x1000: "APPCONTAINER",
    0x2000: "WDM_DRIVER",
    0x4000: "GUARD_CF",
    0x8000: "TERMINAL_SERVER_AWARE",
}


def _decode_dll_characteristics(value: int) -> List[str]:
    return [
        name
        for bit, name in sorted(DLL_CHARACTERISTICS_FLAGS.items())
        if value & bit
    ]


def analyze(path: Path) -> Dict[str, Any]:
    pe = pefile.PE(str(path))
    pe.parse_data_directories(
        directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_DEBUG"],
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"],
        ]
    )

    info: Dict[str, Any] = {
        "path": str(path),
        "machine": hex(pe.FILE_HEADER.Machine),
        "timestamp": _dt.datetime.utcfromtimestamp(
            pe.FILE_HEADER.TimeDateStamp
        ).isoformat()
        + "Z",
        "linker_version": f"{pe.OPTIONAL_HEADER.MajorLinkerVersion}.{pe.OPTIONAL_HEADER.MinorLinkerVersion}",
        "image_version": f"{pe.OPTIONAL_HEADER.MajorImageVersion}.{pe.OPTIONAL_HEADER.MinorImageVersion}",
        "subsystem_version": f"{pe.OPTIONAL_HEADER.MajorSubsystemVersion}.{pe.OPTIONAL_HEADER.MinorSubsystemVersion}",
        "dll_characteristics": hex(pe.OPTIONAL_HEADER.DllCharacteristics),
        "dll_characteristics_flags": _decode_dll_characteristics(
            pe.OPTIONAL_HEADER.DllCharacteristics
        ),
        "debug_entries": _read_debug(pe),
        "file_info": _read_fileinfo(pe),
    }
    return info


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binaries", nargs="+", type=Path)
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON output"
    )
    args = parser.parse_args()

    report = [analyze(path) for path in args.binaries]
    json.dump(report, fp=sys.stdout, indent=2 if args.pretty else None)
    if args.pretty:
        print()


if __name__ == "__main__":
    import sys

    main()
