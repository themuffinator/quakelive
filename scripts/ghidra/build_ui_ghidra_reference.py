#!/usr/bin/env python3
"""Build a Ghidra-readable C reference header for the Quake Live UI module.

This helper turns the committed UI symbol map plus the current hand-authored
reverse-engineering notes into a self-contained C header that Ghidra can ingest
or that exported machine-generated C can include directly.

Usage::

    python3 scripts/ghidra/build_ui_ghidra_reference.py [--repo-root <path>]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


_HEADER = """\
/*
 * Quake Live UI Module -- Ghidra-readable reference header
 *
 * Binary  : uix86.dll
 * Sources : references/symbol-maps/ui.json
 *           references/reverse-engineering/ghidra/uix86/
 *           references/hlil/quakelive/uix86.all/
 *           src-re/ui/include/ui_local.h
 *           src-re/ui/ui_main.c
 *
 * This header is generated for Ghidra and machine-generated source exports.
 * It is not a production runtime header.
 *
 * Symbol coverage: {mapped} mapped functions
 * Generated from : {map_name}
 *
 * Do NOT edit by hand -- regenerate by running:
 *   python3 scripts/ghidra/build_ui_ghidra_reference.py
 */

#ifndef QLR_UI_GHIDRA_REFERENCE_H
#define QLR_UI_GHIDRA_REFERENCE_H

typedef enum {{ qfalse = 0, qtrue = 1 }} qboolean;
typedef int qhandle_t;
typedef int sfxHandle_t;
typedef int fileHandle_t;
typedef float vec_t;
typedef vec_t vec3_t[3];

typedef enum {{
	UIMENU_NONE = 0,
	UIMENU_MAIN,
	UIMENU_INGAME,
	UIMENU_NEED_CD,
	UIMENU_BAD_CD_KEY,
	UIMENU_TEAM,
	UIMENU_POSTGAME
}} uiMenuCommand_t;

/*
 * Retail syscall-table layout (DAT_106b40a8 in Ghidra).
 * Indices are 32-bit pointer slots.
 */
"""

_FOOTER = """
#endif /* QLR_UI_GHIDRA_REFERENCE_H */
"""

_SYSCALLS = [
	("QL_UITRAP_CVAR_REGISTER", 0x00, "slot 0x00"),
	("QL_UITRAP_CVAR_UPDATE", 0x01, "slot 0x01"),
	("QL_UITRAP_CVAR_SET", 0x02, "slot 0x02"),
	("QL_UITRAP_CVAR_VARIABLEVALUE", 0x07, "slot 0x07"),
	("QL_UITRAP_CVAR_SETVALUE", 0x08, "slot 0x08"),
	("QL_UITRAP_CVAR_INFOSTRINGBUFFER", 0x0A, "slot 0x0A"),
	("QL_UITRAP_ARGC", 0x0B, "slot 0x0B"),
	("QL_UITRAP_ARGV", 0x0C, "slot 0x0C"),
	("QL_UITRAP_CMD_EXECUTETEXT", 0x0D, "slot 0x0D"),
	("QL_UITRAP_FS_FOPENFILE", 0x0F, "slot 0x0F"),
	("QL_UITRAP_FS_READ", 0x10, "slot 0x10"),
	("QL_UITRAP_FS_WRITE", 0x11, "slot 0x11"),
	("QL_UITRAP_FS_FCLOSEFILE", 0x12, "slot 0x12"),
	("QL_UITRAP_FS_GETFILELIST", 0x13, "slot 0x13"),
	("QL_UITRAP_R_REGISTERSHADERNOMIP", 0x14, "slot 0x14"),
	("QL_UITRAP_R_DRAWSTRETCHPIC", 0x18, "slot 0x18"),
	("QL_UITRAP_R_MODELBOUNDS", 0x1C, "slot 0x1C"),
	("QL_UITRAP_R_REGISTERMODEL", 0x1E, "slot 0x1E"),
	("QL_UITRAP_R_REGISTERFONT", 0x20, "slot 0x20"),
	("QL_UITRAP_R_SETCOLOR", 0x22, "slot 0x22"),
	("QL_UITRAP_UPDATESCREEN", 0x23, "slot 0x23"),
	("QL_UITRAP_CM_LERPTAG", 0x24, "slot 0x24"),
	("QL_UITRAP_S_REGISTERSOUND", 0x27, "slot 0x27"),
	("QL_UITRAP_S_STARTLOCALSOUND", 0x28, "slot 0x28"),
	("QL_UITRAP_KEY_KEYNUMTOSTRINGBUF", 0x29, "slot 0x29"),
	("QL_UITRAP_KEY_GETBINDINGBUF", 0x2A, "slot 0x2A"),
	("QL_UITRAP_KEY_SETBINDING", 0x2B, "slot 0x2B"),
	("QL_UITRAP_KEY_ISDOWN", 0x2C, "slot 0x2C"),
	("QL_UITRAP_KEY_GETOVERSTRIKEMODE", 0x2D, "slot 0x2D"),
	("QL_UITRAP_KEY_SETOVERSTRIKEMODE", 0x2E, "slot 0x2E"),
	("QL_UITRAP_KEY_CLEARSTATES", 0x2F, "slot 0x2F"),
	("QL_UITRAP_KEY_GETCATCHER", 0x30, "slot 0x30"),
	("QL_UITRAP_KEY_SETCATCHER", 0x31, "slot 0x31"),
	("QL_UITRAP_GETCLIPBOARDDATA", 0x32, "slot 0x32"),
	("QL_UITRAP_GETGLCONFIG", 0x33, "slot 0x33"),
	("QL_UITRAP_GETCLIENTSTATE", 0x34, "slot 0x34"),
	("QL_UITRAP_GETCONFIGSTRING", 0x35, "slot 0x35"),
	("QL_UITRAP_LAN_GETPINGINFO", 0x36, "slot 0x36"),
	("QL_UITRAP_LAN_GETPING", 0x37, "slot 0x37"),
	("QL_UITRAP_LAN_MARKSERVERVISIBLE", 0x38, "slot 0x38"),
	("QL_UITRAP_LAN_UPDATEVISIBLEPINGS", 0x39, "slot 0x39"),
	("QL_UITRAP_LAN_RESETPINGS", 0x3A, "slot 0x3A"),
	("QL_UITRAP_LAN_LOADCACHEDSERVERS", 0x3B, "slot 0x3B"),
	("QL_UITRAP_LAN_SAVECACHEDSERVERS", 0x3C, "slot 0x3C"),
	("QL_UITRAP_LAN_ADDSERVER", 0x3D, "slot 0x3D"),
	("QL_UITRAP_LAN_REMOVESERVER", 0x3E, "slot 0x3E"),
	("QL_UITRAP_SNAPSHOTINFO", 0x3F, "slot 0x3F"),
	("QL_UITRAP_SETPBCLSTATUS", 0x40, "slot 0x40"),
	("QL_UITRAP_GETSAVEDGAMES", 0x41, "slot 0x41"),
	("QL_UITRAP_LOADSAVEGAME", 0x42, "slot 0x42"),
	("QL_UITRAP_AUTOSAVE", 0x43, "slot 0x43"),
	("QL_UITRAP_LAN_GETSERVERADDRESS", 0x52, "slot 0x52"),
	("QL_UITRAP_GETMAPNAME", 0x53, "slot 0x53"),
	("QL_UITRAP_GETSKILLRATING", 0x54, "slot 0x54"),
	("QL_UITRAP_GETMATCHSTARTTIME", 0x55, "slot 0x55"),
]

_CURATED_PROTOTYPES = [
	("void", "dllEntry", "void *syscallTable", "Ordinal 1 / dllEntry @ 0x10003970"),
	("void", "_UI_Init", "int singlePlayerMenu", "_UI_Init @ 0x1000FAB0"),
	("void", "_UI_Shutdown", "void", "_UI_Shutdown @ 0x100044E0"),
	("void", "_UI_KeyEvent", "int key, qboolean down", "_UI_KeyEvent @ 0x1000FF40"),
	("void", "_UI_MouseEvent", "int dx, int dy", "_UI_MouseEvent @ 0x10010000"),
	("void", "_UI_Refresh", "int realtime", "_UI_Refresh @ 0x10004390"),
	("qboolean", "_UI_IsFullscreen", "void", "_UI_IsFullscreen @ 0x10010380"),
	("void", "_UI_SetActiveMenu", "uiMenuCommand_t menu", "_UI_SetActiveMenu @ 0x100100D0"),
	("qboolean", "UI_ConsoleCommand", "int realtime", "UI_ConsoleCommand @ 0x10002AC0"),
	("void", "UI_DrawConnectScreen", "qboolean overlay", "UI_DrawConnectScreen @ 0x10010E30"),
	("void", "UI_RefreshDisplayContext", "void", "UI_RefreshDisplayContext @ 0x10003920"),
	("void", "UI_RefreshDisplayContextScale", "void", "UI_RefreshDisplayContextScale @ 0x1000F9F0"),
	("void", "UI_RegisterCvars", "void", "UI_RegisterCvars @ 0x10011730"),
	("const char *", "UI_GetCallvoteGametypeToken", "int gametype", "UI_GetCallvoteGametypeToken @ 0x10001000"),
	("int", "UI_StartingWeaponIndexFromToken", "void", "UI_StartingWeaponIndexFromToken @ 0x10001090"),
	("void", "AnglesToAxis", "const vec3_t angles, vec3_t axis[3]", "AnglesToAxis @ 0x100010F0"),
	("void", "AngleSubtract", "float a1, float a2, float *out", "AngleSubtract @ 0x10001140"),
	("void", "MatrixMultiply", "float in1[3][3], float in2[3][3], float out[3][3]", "MatrixMultiply @ 0x100011C0"),
	("void", "AngleVectors", "const vec3_t angles, vec3_t forward, vec3_t right, vec3_t up", "AngleVectors @ 0x100012A0"),
	("int", "COM_Compress", "char *data_p", "COM_Compress @ 0x10001400"),
	("char *", "COM_ParseExt", "char **data_p, qboolean allowLineBreaks", "COM_ParseExt @ 0x10001500"),
	("qboolean", "String_IsNumeric", "const char *s", "String_IsNumeric @ 0x10001670"),
	("int", "Q_stricmpn", "const char *s1, const char *s2, int n", "Q_stricmpn @ 0x100016C0"),
	("int", "Q_stricmp", "const char *s1, const char *s2", "Q_stricmp @ 0x10001730"),
	("void", "Q_strncpyz", "char *dest, const char *src, int destsize", "Q_strncpyz @ 0x10001750"),
	("void", "Q_CleanStr", "char *string", "Q_CleanStr @ 0x100017E0"),
	("void", "Com_sprintf", "char *dest, int size, const char *fmt, ...", "Com_sprintf @ 0x10001830"),
	("char *", "va", "const char *format, ...", "va @ 0x10001900"),
]


def _sanitize_macro(name: str) -> str:
	ident = re.sub(r"[^0-9A-Za-z_]", "_", name)
	if ident and ident[0].isdigit():
		ident = "_" + ident
	return ident.upper()


def _first_sentence(text: str) -> str:
	if not text:
		return ""
	line = re.sub(r"\s+", " ", text.strip())
	match = re.match(r"(.+?[.?!])(\s|$)", line)
	return match.group(1) if match else line


def main(argv: list[str] | None = None) -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument(
		"--repo-root",
		type=Path,
		default=Path(__file__).resolve().parents[2],
		help="Path to repository root (default: two levels above this script)",
	)
	args = parser.parse_args(argv)
	repo_root = args.repo_root.resolve()

	map_path = repo_root / "references" / "symbol-maps" / "ui.json"
	out_path = repo_root / "references" / "reverse-engineering" / "ghidra" / "uix86" / "ui_ghidra_reference.h"

	if not map_path.is_file():
		print(f"ERROR: symbol map not found: {map_path}", file=sys.stderr)
		return 1

	with map_path.open(encoding="utf-8") as fh:
		manifest = json.load(fh)

	functions = manifest.get("functions", [])
	if not functions:
		print(f"ERROR: no functions in symbol map: {map_path}", file=sys.stderr)
		return 1

	lines: list[str] = []
	lines.append(_HEADER.format(mapped=len(functions), map_name=map_path.name))
	for name, value, comment in _SYSCALLS:
		lines.append(f"#define {name:<34} 0x{value:02X}\t/* {comment} */")

	lines.append("")
	lines.append("/* Curated exact prototypes recovered from committed UI reconstruction work. */")
	for ret_type, name, params, comment in _CURATED_PROTOTYPES:
		lines.append(f"/* {comment} */")
		lines.append(f"{ret_type}\t{name}( {params} );")
		lines.append("")

	lines.append("/*")
	lines.append(" * Full mapped symbol-address catalog derived from references/symbol-maps/ui.json.")
	lines.append(" * Comments are short summaries from the committed reverse-engineering notes.")
	lines.append(" */")

	seen_macros: set[str] = set()
	for entry in functions:
		name = entry.get("normalized_name", "").strip()
		addr = entry.get("address", "").strip()
		comment = _first_sentence(entry.get("comment", ""))
		if not name or not addr:
			continue
		macro = f"QLR_UI_ADDR_{_sanitize_macro(name)}"
		if macro in seen_macros:
			hex_addr = addr[2:] if addr.lower().startswith("0x") else addr
			macro = f"{macro}_{hex_addr.upper()}"
		seen_macros.add(macro)
		if comment:
			lines.append(f"/* {name}: {comment} */")
		else:
			lines.append(f"/* {name} */")
		lines.append(f"#define {macro:<56} {addr}u")

	lines.append(_FOOTER)
	out_path.write_text("\n".join(lines), encoding="utf-8")
	print(f"Wrote {out_path} ({len(functions)} mapped functions)")
	return 0


if __name__ == "__main__":
	sys.exit(main())
