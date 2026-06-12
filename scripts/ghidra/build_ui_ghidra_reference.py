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
 * Retail native import-table layout (DAT_106b40a8 in Ghidra).
 * Indices are 32-bit pointer slots; slot i == DAT_106b40a8 + i*4.
 * This is distinct from the legacy source/QVM uiImport_t syscall ABI.
 */
"""

_FOOTER = """
#endif /* QLR_UI_GHIDRA_REFERENCE_H */
"""

_NATIVE_IMPORTS = [
	("QL_UITRAP_PRINT", 0x00, "slot 0x00 / offset 0x000"),
	("QL_UITRAP_ERROR", 0x01, "slot 0x01 / offset 0x004"),
	("QL_UITRAP_MILLISECONDS", 0x02, "slot 0x02 / offset 0x008"),
	("QL_UITRAP_REAL_TIME", 0x03, "slot 0x03 / offset 0x00C"),
	("QL_UITRAP_CVAR_REGISTER", 0x04, "slot 0x04 / offset 0x010"),
	("QL_UITRAP_CVAR_CREATE", 0x05, "slot 0x05 / offset 0x014"),
	("QL_UITRAP_CVAR_UPDATE", 0x06, "slot 0x06 / offset 0x018"),
	("QL_UITRAP_CVAR_SET", 0x07, "slot 0x07 / offset 0x01C"),
	("QL_UITRAP_CVAR_SET_VALUE", 0x08, "slot 0x08 / offset 0x020"),
	("QL_UITRAP_CVAR_VARIABLE_STRING_BUFFER", 0x09, "slot 0x09 / offset 0x024"),
	("QL_UITRAP_CVAR_VARIABLE_VALUE", 0x0A, "slot 0x0A / offset 0x028"),
	("QL_UITRAP_ARGC", 0x0B, "slot 0x0B / offset 0x02C"),
	("QL_UITRAP_ARGV", 0x0C, "slot 0x0C / offset 0x030"),
	("QL_UITRAP_CMD_ARGS_BUFFER", 0x0D, "slot 0x0D / offset 0x034"),
	("QL_UITRAP_FS_FOPENFILE", 0x0E, "slot 0x0E / offset 0x038"),
	("QL_UITRAP_FS_READ", 0x0F, "slot 0x0F / offset 0x03C"),
	("QL_UITRAP_FS_WRITE", 0x10, "slot 0x10 / offset 0x040"),
	("QL_UITRAP_FS_FCLOSEFILE", 0x11, "slot 0x11 / offset 0x044"),
	("QL_UITRAP_FS_SEEK", 0x12, "slot 0x12 / offset 0x048"),
	("QL_UITRAP_FS_GETFILELIST", 0x13, "slot 0x13 / offset 0x04C"),
	("QL_UITRAP_CMD_EXECUTETEXT", 0x14, "slot 0x14 / offset 0x050"),
	("QL_UITRAP_R_REGISTERMODEL", 0x15, "slot 0x15 / offset 0x054"),
	("QL_UITRAP_R_REGISTERSKIN", 0x16, "slot 0x16 / offset 0x058"),
	("QL_UITRAP_R_REGISTERSHADERNOMIP", 0x17, "slot 0x17 / offset 0x05C"),
	("QL_UITRAP_R_CLEARSCENE", 0x18, "slot 0x18 / offset 0x060"),
	("QL_UITRAP_R_ADDREFENTITYTOSCENE", 0x19, "slot 0x19 / offset 0x064"),
	("QL_UITRAP_R_ADDPOLYTOSCENE", 0x1A, "slot 0x1A / offset 0x068"),
	("QL_UITRAP_R_ADDLIGHTTOSCENE", 0x1B, "slot 0x1B / offset 0x06C"),
	("QL_UITRAP_R_RENDERSCENE", 0x1C, "slot 0x1C / offset 0x070"),
	("QL_UITRAP_R_SETCOLOR", 0x1D, "slot 0x1D / offset 0x074"),
	("QL_UITRAP_R_DRAWSTRETCHPIC", 0x1E, "slot 0x1E / offset 0x078"),
	("QL_UITRAP_R_MODELBOUNDS", 0x1F, "slot 0x1F / offset 0x07C"),
	("QL_UITRAP_UPDATESCREEN", 0x20, "slot 0x20 / offset 0x080"),
	("QL_UITRAP_CM_LERPTAG", 0x21, "slot 0x21 / offset 0x084"),
	("QL_UITRAP_S_STARTLOCALSOUND", 0x22, "slot 0x22 / offset 0x088"),
	("QL_UITRAP_S_REGISTERSOUND", 0x23, "slot 0x23 / offset 0x08C"),
	("QL_UITRAP_KEY_KEYNUMTOSTRINGBUF", 0x24, "slot 0x24 / offset 0x090"),
	("QL_UITRAP_KEY_GETBINDINGBUF", 0x25, "slot 0x25 / offset 0x094"),
	("QL_UITRAP_KEY_SETBINDING", 0x26, "slot 0x26 / offset 0x098"),
	("QL_UITRAP_KEY_ISDOWN", 0x27, "slot 0x27 / offset 0x09C"),
	("QL_UITRAP_KEY_GETOVERSTRIKEMODE", 0x28, "slot 0x28 / offset 0x0A0"),
	("QL_UITRAP_KEY_SETOVERSTRIKEMODE", 0x29, "slot 0x29 / offset 0x0A4"),
	("QL_UITRAP_KEY_CLEARSTATES", 0x2A, "slot 0x2A / offset 0x0A8"),
	("QL_UITRAP_KEY_GETCATCHER", 0x2B, "slot 0x2B / offset 0x0AC"),
	("QL_UITRAP_KEY_SETCATCHER", 0x2C, "slot 0x2C / offset 0x0B0"),
	("QL_UITRAP_GETCLIPBOARDDATA", 0x2D, "slot 0x2D / offset 0x0B4"),
	("QL_UITRAP_GETCLIENTSTATE", 0x2E, "slot 0x2E / offset 0x0B8"),
	("QL_UITRAP_GETGLCONFIG", 0x2F, "slot 0x2F / offset 0x0BC"),
	("QL_UITRAP_GETCONFIGSTRING", 0x30, "slot 0x30 / offset 0x0C0"),
	("QL_UITRAP_LAN_GETSERVERCOUNT", 0x31, "slot 0x31 / offset 0x0C4"),
	("QL_UITRAP_LAN_GETSERVERADDRESSSTRING", 0x32, "slot 0x32 / offset 0x0C8"),
	("QL_UITRAP_LAN_GETSERVERINFO", 0x33, "slot 0x33 / offset 0x0CC"),
	("QL_UITRAP_LAN_GETSERVERPING", 0x34, "slot 0x34 / offset 0x0D0"),
	("QL_UITRAP_LAN_GETPINGQUEUECOUNT", 0x35, "slot 0x35 / offset 0x0D4"),
	("QL_UITRAP_LAN_CLEARPING", 0x36, "slot 0x36 / offset 0x0D8"),
	("QL_UITRAP_LAN_GETPING", 0x37, "slot 0x37 / offset 0x0DC"),
	("QL_UITRAP_LAN_GETPINGINFO", 0x38, "slot 0x38 / offset 0x0E0"),
	("QL_UITRAP_LAN_LOADCACHEDSERVERS", 0x39, "slot 0x39 / offset 0x0E4"),
	("QL_UITRAP_LAN_SAVECACHEDSERVERS", 0x3A, "slot 0x3A / offset 0x0E8"),
	("QL_UITRAP_LAN_MARKSERVERVISIBLE", 0x3B, "slot 0x3B / offset 0x0EC"),
	("QL_UITRAP_LAN_SERVERISVISIBLE", 0x3C, "slot 0x3C / offset 0x0F0"),
	("QL_UITRAP_LAN_UPDATEVISIBLEPINGS", 0x3D, "slot 0x3D / offset 0x0F4"),
	("QL_UITRAP_LAN_ADDSERVER", 0x3E, "slot 0x3E / offset 0x0F8"),
	("QL_UITRAP_LAN_REMOVESERVER", 0x3F, "slot 0x3F / offset 0x0FC"),
	("QL_UITRAP_LAN_RESETPINGS", 0x40, "slot 0x40 / offset 0x100"),
	("QL_UITRAP_LAN_SERVERSTATUS", 0x41, "slot 0x41 / offset 0x104"),
	("QL_UITRAP_LAN_COMPARESERVERS", 0x42, "slot 0x42 / offset 0x108"),
	("QL_UITRAP_MEMORY_REMAINING", 0x43, "slot 0x43 / offset 0x10C"),
	("QL_UITRAP_GET_CDKEY", 0x44, "slot 0x44 / offset 0x110"),
	("QL_UITRAP_SET_CDKEY", 0x45, "slot 0x45 / offset 0x114"),
	("QL_UITRAP_R_REGISTERFONT", 0x46, "slot 0x46 / offset 0x118"),
	("QL_UITRAP_S_STOPBACKGROUNDTRACK", 0x47, "slot 0x47 / offset 0x11C"),
	("QL_UITRAP_S_STARTBACKGROUNDTRACK", 0x48, "slot 0x48 / offset 0x120"),
	("QL_UITRAP_CIN_PLAYCINEMATIC", 0x49, "slot 0x49 / offset 0x124"),
	("QL_UITRAP_CIN_STOPCINEMATIC", 0x4A, "slot 0x4A / offset 0x128"),
	("QL_UITRAP_CIN_DRAWCINEMATIC", 0x4B, "slot 0x4B / offset 0x12C"),
	("QL_UITRAP_CIN_RUNCINEMATIC", 0x4C, "slot 0x4C / offset 0x130"),
	("QL_UITRAP_CIN_SETEXTENTS", 0x4D, "slot 0x4D / offset 0x134"),
	("QL_UITRAP_R_REMAP_SHADER", 0x4E, "slot 0x4E / offset 0x138"),
	("QL_UITRAP_VERIFY_CDKEY", 0x4F, "slot 0x4F / offset 0x13C"),
	("QL_UITRAP_SETUP_ADVERT_CELL_SHADER", 0x50, "slot 0x50 / offset 0x140"),
	("QL_UITRAP_REFRESH_ADVERT_CELL_SHADER", 0x51, "slot 0x51 / offset 0x144"),
	("QL_UITRAP_INIT_ADVERTISEMENT_BRIDGE", 0x52, "slot 0x52 / offset 0x148"),
	("QL_UITRAP_UNUSED_83", 0x53, "slot 0x53 / offset 0x14C / update-advert callback"),
	("QL_UITRAP_ACTIVATE_ADVERT", 0x54, "slot 0x54 / offset 0x150"),
	("QL_UITRAP_UNUSED_85", 0x55, "slot 0x55 / offset 0x154"),
	("QL_UITRAP_SET_CURSOR_POS", 0x56, "slot 0x56 / offset 0x158"),
	("QL_UITRAP_GET_CURSOR_POS", 0x57, "slot 0x57 / offset 0x15C"),
	("QL_UITRAP_PC_ADD_GLOBAL_DEFINE", 0x58, "slot 0x58 / offset 0x160"),
	("QL_UITRAP_PC_LOAD_SOURCE", 0x59, "slot 0x59 / offset 0x164"),
	("QL_UITRAP_PC_FREE_SOURCE", 0x5A, "slot 0x5A / offset 0x168"),
	("QL_UITRAP_PC_READ_TOKEN", 0x5B, "slot 0x5B / offset 0x16C"),
	("QL_UITRAP_PC_SOURCE_FILE_AND_LINE", 0x5C, "slot 0x5C / offset 0x170"),
	("QL_UITRAP_IS_SUBSCRIBED_APP", 0x5D, "slot 0x5D / offset 0x174"),
	("QL_UITRAP_DRAW_SCALED_TEXT", 0x5E, "slot 0x5E / offset 0x178"),
	("QL_UITRAP_MEASURE_TEXT", 0x5F, "slot 0x5F / offset 0x17C"),
	("QL_UITRAP_GET_ITEM_DOWNLOAD_INFO", 0x60, "slot 0x60 / offset 0x180"),
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
	for name, value, comment in _NATIVE_IMPORTS:
		lines.append(f"#define {name:<46} 0x{value:02X}\t/* {comment} */")

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
