from __future__ import annotations

import argparse
from collections import OrderedDict, defaultdict
from pathlib import Path
import re


DATE = "2026-04-22"
REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = REPO_ROOT / "docs" / "reverse-engineering"
GAP_NOTES_ROOT = DOCS_ROOT / "source-file-gap-notes"

LEDGER_PATH = DOCS_ROOT / f"source-file-parity-ledger-{DATE}.md"
PLAN_PATH = DOCS_ROOT / f"source-file-parity-audit-plan-{DATE}.md"
INDEX_PATH = DOCS_ROOT / f"historical-audit-index-{DATE}.md"
README_PATH = GAP_NOTES_ROOT / "README.md"

SOURCE_EXTENSIONS = {".c", ".cc", ".cpp", ".cxx"}
EXCLUDED_PARTS = {"_deps", "_build"}
TYPE_SEPARATOR_PATTERN = r"(?:[ \t\*&]+|[ \t]*\r?\n[ \t]*)"
FUNCTION_NAME_PATTERN = r"(?:[A-Za-z_]\w*::)*(?:~?[A-Za-z_]\w*|operator(?:\[\]|\(\)|[^\s(]+))"
FUNCTION_PATTERN = re.compile(
	rf"(?ms)^[ \t]*(?!#)(?:[A-Za-z_]\w*(?:{TYPE_SEPARATOR_PATTERN}[A-Za-z_]\w*)*){TYPE_SEPARATOR_PATTERN}(?P<name>{FUNCTION_NAME_PATTERN})[ \t\r\n]*\([^;{{}}]*\)[ \t\r\n]*\{{"
)
NON_FUNCTION_KEYWORDS = {"if", "for", "while", "switch"}

DOC_LINKS = {
	"engine_full": ("engine-full-parity-audit-and-implementation-plan-2026-04-10.md", "engine-wide closure"),
	"client": ("client-full-parity-audit-and-implementation-plan-2026-04-09.md", "client audit"),
	"qcommon": ("qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md", "qcommon audit"),
	"renderer": ("renderer-full-parity-audit-and-implementation-plan-2026-04-09.md", "renderer audit"),
	"server": ("server-full-parity-audit-and-implementation-plan-2026-04-10.md", "server audit"),
	"ui": ("ui-full-parity-audit-and-implementation-plan-2026-04-05.md", "ui audit"),
	"modules": ("game-module-parity-audit-and-implementation-plan-2026-04-10.md", "module audit"),
	"platform": ("platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md", "platform-specific audit"),
	"botlib": ("botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md", "botlib audit"),
	"repo": ("repo-wide-parity-audit-2026-04-21.md", "repo-wide audit"),
	"plan": (f"source-file-parity-audit-plan-{DATE}.md", "source-file plan"),
}

STATUS_DESCRIPTIONS = OrderedDict(
	[
		(
			"walked-closed",
			"The 2026-04-22 campaign has rerun the full file walk for this file and did not isolate a new file-level gap.",
		),
		(
			"baseline-closed",
			"Subsystem or strict-retail closure already exists; this 2026-04-22 campaign has not yet rerun the full file walk.",
		),
		(
			"documented-divergence",
			"The file has a dedicated note because it remains an intentional bounded compatibility divergence, not active parity debt.",
		),
		(
			"gap-note-open",
			"A concrete file-level parity gap is already evidenced and has a dedicated note.",
		),
		(
			"compatibility-open",
			"The file sits inside an open repo-wide compatibility or portability lane; a file-specific gap note will be added once the function walk isolates it.",
		),
		(
			"queued-secondary",
			"The file belongs to a secondary tool, editor, compiler, or legacy support tree; it is catalogued now and queued after the primary runtime surface.",
		),
	]
)

HEADER_EXCEPTIONS = ["src/common/platform/platform_config.h"]

NOTE_FILES = {
	"src/common/platform/platform_config.h": "rw-g01-platform-config.md",
	"src/common/platform/platform_services.c": "rw-g01-platform-services.md",
	"src/common/platform/backends/platform_backend_open_steam.c": "rw-g01-open-steam-backend.md",
	"src/common/platform/backends/platform_backend_steamworks.c": "rw-g01-steamworks-backend.md",
	"src/code/client/ql_auth.c": "rw-g01-client-auth.md",
	"src/code/client/cl_steam_resources.c": "rw-g01-client-steam-resources.md",
	"src/code/server/sv_rankings.c": "rw-g01-server-rankings.md",
	"src/code/unix/unix_main.c": "rw-g02-unix-main.md",
	"src/code/unix/linux_glimp.c": "rw-g02-linux-glimp.md",
	"src/code/unix/linux_snd.c": "rw-g02-linux-snd.md",
	"src/code/unix/linux_joystick.c": "rw-g02-linux-joystick.md",
	"src/code/null/null_main.c": "rw-g02-null-main.md",
	"src/code/null/null_glimp.c": "rw-g02-null-glimp.md",
	"src/code/null/null_client.c": "rw-g02-null-client.md",
	"src/code/null/null_input.c": "rw-g02-null-input.md",
	"src/code/null/null_snddma.c": "rw-g02-null-snddma.md",
}

GAP_NOTE_ORDER = list(NOTE_FILES.keys())

PRIMARY_SECTIONS = OrderedDict(
	[
		("src/common", []),
		("src/code/client", []),
		("src/code/cgame", []),
		("src/code/game", []),
		("src/code/qcommon", []),
		("src/code/renderer", []),
		("src/code/server", []),
		("src/code/ui", []),
		("src/code/win32", []),
		("src/code/botlib", []),
	]
)

COMPATIBILITY_SECTIONS = OrderedDict(
	[
		("src/code/unix", []),
		("src/code/null", []),
	]
)

SECONDARY_SECTIONS = OrderedDict(
	[
		("src/code/bspc", []),
		("src/code/jpeg-6", []),
		("src/code/splines", []),
		("src/game", []),
		("src/lcc", []),
		("src/libs", []),
		("src/q3asm", []),
		("src/q3map", []),
		("src/q3radiant", []),
	]
)

PHASE4_GROUP_AUDITS: list[dict[str, object]] = [
	{
		"label": "`src/code/bspc/`, `src/code/jpeg-6/`, and `src/code/splines/`",
		"sections": ("src/code/bspc", "src/code/jpeg-6", "src/code/splines"),
		"plan_result": [
			"2026-04-22 result: no new file-level gap owners were isolated across the",
			"first secondary-source tranche; the refreshed function-count pass now",
			"lands on libjpeg macro definitions and splines C++ methods, while the",
			"retained BSPC toolchain, bundled `jpeg-6` sources, and legacy splines",
			"helpers remain bounded secondary support trees on current evidence.",
		],
	},
	{
		"label": "`src/game/`, `src/q3asm/`, and `src/q3map/`",
		"sections": ("src/game", "src/q3asm", "src/q3map"),
		"plan_result": [
			"2026-04-22 result: no new file-level gap owners were isolated across the",
			"second secondary-source tranche; the retained gameplay fixture helpers,",
			"`q3asm` bytecode assembler sources, and `q3map` compile/light/vis",
			"toolchain remain bounded secondary support trees on current evidence.",
		],
	},
	{
		"label": "`src/lcc/` and `src/libs/`",
		"sections": ("src/lcc", "src/libs"),
		"plan_result": [
			"2026-04-22 result: no new file-level gap owners were isolated across the",
			"third secondary-source tranche; the retained LCC compiler/preprocessor,",
			"test fixtures, and tracked support-library sources under `src/libs`",
			"remain bounded secondary support trees on current evidence.",
		],
	},
	{
		"label": "`src/q3radiant/`",
		"sections": ("src/q3radiant",),
		"plan_result": [
			"2026-04-22 result: no new file-level gap owners were isolated across the",
			"final secondary-source tranche; the retained Gtk/MFC-era Radiant editor,",
			"plugin bridge, OpenGL host glue, and bundled spline/editor helpers",
			"remain bounded secondary support trees on current evidence.",
		],
	},
]

SECTION_AUDITS: dict[str, dict[str, object]] = {
	"src/common": {
		"completed": True,
		"row_state": "Current function walk complete; no new file-level gap isolated",
		"plan_result": [
			"2026-04-22 result: no new file-level gap owners were isolated beyond the",
			"existing `RW-G01` policy/configuration notes; `platform_steamworks.c`",
			"remains a retained Steamworks wrapper surface gated by",
			"`platform_config.h`, not a newly opened repo-wide gap owner.",
		],
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/common` function walk did not",
			"isolate any new file-level owners beyond the already-seeded `RW-G01`",
			"policy/configuration surfaces. The retained `platform_steamworks.c`",
			"wrapper family remains baseline-closed on current evidence; the",
			"deliberate compatibility-only boundary still lives in",
			"`platform_config.h`, `platform_services.c`, and the existing",
			"auth/backend call sites.",
		],
	},
	"src/code/qcommon": {
		"completed": True,
		"row_state": "Current function walk complete; no file-level parity gap isolated",
		"plan_result": [
			"2026-04-22 result: no new file-level gap owners were isolated inside the",
			"closed strict-retail `qcommon` register; `vm_x86.c` remains the documented",
			"compatibility carry beneath the closed `vm.c` host-selection seam rather",
			"than a newly opened repo-wide or subsystem gap owner.",
		],
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/code/qcommon` function walk did",
			"not isolate any new file-level owners inside the closed strict-retail",
			"`qcommon` register. The refreshed qcommon audit and the current runtime",
			"proof lane still bound the tree on current evidence, while `vm_x86.c`",
			"remains the already-documented compatibility carry beneath the closed",
			"`vm.c` host-selection seam rather than a new repo-wide or subsystem gap",
			"owner.",
		],
	},
	"src/code/client": {
		"completed": True,
		"row_state": "Current function walk complete; no new file-level gap isolated",
		"plan_result": [
			"2026-04-22 result: no new file-level gap owners were isolated beyond the",
			"existing `RW-G01` notes for `ql_auth.c` and `cl_steam_resources.c`; the",
			"rest of the strict-retail client register remains closed on current",
			"evidence.",
		],
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/code/client` function walk did",
			"not isolate any new file-level owners beyond the already-seeded `RW-G01`",
			"compatibility-policy notes. The strict-retail client register remains",
			"closed on current evidence, while `ql_auth.c` and",
			"`cl_steam_resources.c` continue to own the repo-wide bounded",
			"online-services story inside this tree.",
		],
	},
	"src/code/server": {
		"completed": True,
		"row_state": "Current function walk complete; no new file-level gap isolated",
		"plan_result": [
			"2026-04-22 result: no new file-level gap owners were isolated beyond the",
			"existing `RW-G01` note for `sv_rankings.c`; the rest of the strict-retail",
			"server register remains closed on current evidence.",
		],
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/code/server` function walk did",
			"not isolate any new file-level owners beyond the already-seeded `RW-G01`",
			"ownership note for `sv_rankings.c`. The strict-retail server register",
			"remains closed on current evidence, while the retained rankings policy",
			"surface stays bounded in its existing per-file note instead of reopening",
			"the subsystem.",
		],
	},
	"src/code/renderer": {
		"completed": True,
		"row_state": "Current function walk complete; no file-level parity gap isolated",
		"plan_result": [
			"2026-04-22 result plus 2026-05-20 renderer wiring refresh: no new",
			"file-level gap owners were isolated inside the closed strict-retail",
			"`renderer` register. The stale `R_fonsErrorCallback` module-runtime",
			"artifact remains part of `RW-G04` evidence freshness rather than a new",
			"source-file gap owner after the non-retail eager FontStash prebuild was",
			"removed from `tr_font.c`.",
		],
		"ledger_summary": [
			"Current 2026-04-22 audit result plus 2026-05-20 renderer wiring refresh:",
			"the `src/code/renderer` function walk did not isolate any new file-level",
			"owners inside the closed strict-retail `renderer` register. The retained",
			"export, image, post-process, scene/runtime, font, and host-text closures",
			"still hold on current evidence, while the stale `R_fonsErrorCallback`",
			"module-runtime artifact remains part of `RW-G04` evidence freshness rather",
			"than a new renderer source-gap owner.",
		],
	},
	"src/code/win32": {
		"completed": True,
		"row_state": "Current function walk complete; no file-level parity gap isolated",
		"plan_result": [
			"2026-04-22 result: no new file-level gap owners were isolated inside the",
			"closed strict-retail Windows platform register; the earlier `PS-G01`",
			"`win_glimp.c` pixel-format drift remains closed on current evidence.",
		],
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/code/win32` function walk did",
			"not isolate any new file-level owners inside the closed strict-retail",
			"Windows platform register. The retained clipboard, raw-input,",
			"loading-window, renderer-host glue, and `win_glimp.c` pixel-format",
			"closures still hold on current evidence.",
		],
	},
	"src/code/botlib": {
		"completed": True,
		"row_state": "Current function walk complete; no file-level parity gap isolated",
		"plan_result": [
			"2026-04-22 result: no new file-level gap owners were isolated inside the",
			"closed botlib internal register; the retained mapping-round `61`",
			"bridge/import ownership and deterministic AAS/reachability/goal-state",
			"proof lane still bound the tree on current evidence.",
		],
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/code/botlib` function walk did",
			"not isolate any new file-level owners inside the closed botlib internal",
			"register. The retained mapping-round `61` bridge/import ownership and the",
			"deterministic AAS/reachability/goal-state proof lane still bound the tree",
			"on current evidence, while the remaining live-map or gameplay-tuning",
			"nuance stays outside the repo-wide/file-level gap register.",
		],
	},
	"src/code/game": {
		"completed": True,
		"row_state": "Current function walk complete; no file-level parity gap isolated",
		"plan_result": [
			"2026-04-22 result: no new file-level gap owners were isolated inside the",
			"closed strict-retail module register; the refreshed module audit, the",
			"qagame retail gate, the focused gameplay sweep, and the current",
			"auto-shuffle/countdown plus Clan Arena shuffle regression lanes still",
			"bound the tree on current evidence.",
		],
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/code/game` function walk did",
			"not isolate any new file-level owners inside the closed strict-retail",
			"module register. The refreshed module audit, the qagame retail gate, the",
			"focused gameplay sweep, and the current auto-shuffle/countdown plus Clan",
			"Arena shuffle regression lanes still bound this tree on current",
			"evidence.",
		],
	},
	"src/code/cgame": {
		"completed": True,
		"row_state": "Current function walk complete; no file-level parity gap isolated",
		"plan_result": [
			"2026-04-22 result: no new file-level gap owners were isolated inside the",
			"closed strict-retail module register; the refreshed module audit, the",
			"focused cgame parity lane (`199 passed`, `1 skipped`), and the shared",
			"native export helper certification still bound the tree on current",
			"evidence.",
		],
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/code/cgame` function walk did",
			"not isolate any new file-level owners inside the closed strict-retail",
			"module register. The refreshed module audit, the focused cgame parity",
			"lane (`199 passed`, `1 skipped`), and the shared native export helper",
			"certification still bound this tree on current evidence, so no new",
			"repo-wide gap note is opened here.",
		],
	},
	"src/code/ui": {
		"completed": True,
		"row_state": "Current read-only function walk complete; no file-level parity gap isolated",
		"plan_result": [
			"2026-04-22 result: no new file-level gap owners were isolated inside the",
			"closed strict-retail UI register; the refreshed UI audit, the focused UI",
			"parity lane (`56 passed`, `2 skipped`), and the clean read-only",
			"`src/ui` runtime-panel parity proof still bound the tree on current",
			"evidence.",
		],
		"ledger_summary": [
			"Current 2026-04-22 audit result: the read-only `src/code/ui` function",
			"walk did not isolate any new file-level owners inside the closed",
			"strict-retail UI register. The refreshed UI audit, the focused UI",
			"parity lane (`56 passed`, `2 skipped`), the clean read-only `src/ui`",
			"runtime-panel parity proof, and the bundle/runtime evidence still bound",
			"this tree on current evidence, so no new repo-wide gap note is opened",
			"here.",
		],
	},
	"src/code/unix": {
		"completed": True,
		"row_state": "Current compatibility function walk complete; no new file-level portability gap isolated",
		"plan_result": [
			"2026-04-22 result: no new file-level gap owners were isolated beyond the",
			"existing `RW-G02` notes for `unix_main.c`, `linux_glimp.c`,",
			"`linux_snd.c`, and `linux_joystick.c`; the focused non-Windows",
			"portability lane (`8 passed`) and the current repo-wide audit still",
			"bound the remaining Unix files on current evidence.",
		],
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/code/unix` function walk did",
			"not isolate any new file-level owners beyond the existing `RW-G02`",
			"notes for `unix_main.c`, `linux_glimp.c`, `linux_snd.c`, and",
			"`linux_joystick.c`. The focused non-Windows portability lane",
			"(`8 passed`) and the current repo-wide audit still bound",
			"`linux_common.c`, `linux_qgl.c`, `linux_signals.c`, `unix_net.c`,",
			"`unix_shared.c`, and `vm_x86.c` on current evidence.",
		],
	},
	"src/code/null": {
		"completed": True,
		"row_state": "Current compatibility function walk complete; no new file-level portability gap isolated",
		"plan_result": [
			"2026-04-22 result: the null compatibility walk isolated",
			"`null_glimp.c` as an additional `RW-G02` owner beside the existing",
			"notes for `null_main.c`, `null_client.c`, `null_input.c`, and",
			"`null_snddma.c`; the focused non-Windows portability lane",
			"(`8 passed`) and the current repo-wide audit still bound `null_net.c`",
			"and `mac_net.c` on current evidence.",
		],
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/code/null` function walk",
			"isolated `null_glimp.c` as an additional `RW-G02` owner beside the",
			"existing notes for `null_main.c`, `null_client.c`, `null_input.c`,",
			"and `null_snddma.c`. The focused non-Windows portability lane",
			"(`8 passed`) and the current repo-wide audit still bound",
			"`null_net.c` and `mac_net.c` on current evidence, so no further",
			"file-level owner is opened inside the null tree this round.",
		],
	},
	"src/code/bspc": {
		"completed": True,
		"row_state": "Current secondary function walk complete; no new file-level gap isolated",
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/code/bspc` function walk did",
			"not isolate any new file-level owners. This retained BSP/AAS compiler",
			"toolchain remains a secondary support surface outside the primary",
			"runtime replacement target on current evidence.",
		],
	},
	"src/code/jpeg-6": {
		"completed": True,
		"row_state": "Current secondary function walk complete; no new file-level gap isolated",
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/code/jpeg-6` function walk",
			"did not isolate any new file-level owners. The refreshed extractor now",
			"lands on the macro-style IJG definitions instead of the earlier zero-row",
			"placeholders, while this bundled JPEG support tree remains a secondary",
			"support surface on current evidence.",
		],
	},
	"src/code/splines": {
		"completed": True,
		"row_state": "Current secondary function walk complete; no new file-level gap isolated",
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/code/splines` function walk",
			"did not isolate any new file-level owners. The refreshed extractor now",
			"lands on the retained C++ method definitions, while this legacy spline",
			"editor/helper tree remains a bounded secondary support surface on",
			"current evidence.",
		],
	},
	"src/game": {
		"completed": True,
		"row_state": "Current secondary function walk complete; no new file-level gap isolated",
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/game` function walk did not",
			"isolate any new file-level owners. The retained gameplay config helpers",
			"and standalone fixture/support sources remain a bounded secondary",
			"support surface on current evidence.",
		],
	},
	"src/q3asm": {
		"completed": True,
		"row_state": "Current secondary function walk complete; no new file-level gap isolated",
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/q3asm` function walk did not",
			"isolate any new file-level owners. This retained bytecode assembler",
			"toolchain remains a bounded secondary support surface on current",
			"evidence.",
		],
	},
	"src/q3map": {
		"completed": True,
		"row_state": "Current secondary function walk complete; no new file-level gap isolated",
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/q3map` function walk did not",
			"isolate any new file-level owners. The retained map compile, light,",
			"and vis toolchain remains a bounded secondary support surface on",
			"current evidence.",
		],
	},
	"src/lcc": {
		"completed": True,
		"row_state": "Current secondary function walk complete; no new file-level gap isolated",
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/lcc` function walk did not",
			"isolate any new file-level owners. The retained LCC compiler,",
			"preprocessor, code-generator, and bundled test sources remain a",
			"bounded secondary support surface on current evidence.",
		],
	},
	"src/libs": {
		"completed": True,
		"row_state": "Current secondary function walk complete; no new file-level gap isolated",
		"ledger_summary": [
			"Current 2026-04-22 audit result: the tracked `src/libs` function walk",
			"did not isolate any new file-level owners. The retained command-line,",
			"JPEG, and pak-support helper sources remain a bounded secondary",
			"support surface on current evidence.",
		],
	},
	"src/q3radiant": {
		"completed": True,
		"row_state": "Current secondary function walk complete; no new file-level gap isolated",
		"ledger_summary": [
			"Current 2026-04-22 audit result: the `src/q3radiant` function walk did",
			"not isolate any new file-level owners. The retained Radiant editor",
			"shell, plugin bridge, OpenGL host glue, and bundled spline/editor",
			"helper sources remain a bounded secondary support surface on current",
			"evidence.",
		],
	},
}


def doc_link(key: str) -> str:
	filename, label = DOC_LINKS[key]
	return f"[{label}]({filename})"


def source_files() -> list[str]:
	files: list[str] = []
	for path in REPO_ROOT.joinpath("src").rglob("*"):
		if not path.is_file():
			continue
		if path.suffix.lower() not in SOURCE_EXTENSIONS:
			continue
		rel = path.relative_to(REPO_ROOT)
		if any(part in EXCLUDED_PARTS for part in rel.parts):
			continue
		files.append(rel.as_posix())
	files.sort()
	return files


def read_text(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8", errors="ignore")


def extract_functions(text: str) -> list[str]:
	return [
		match.group("name")
		for match in FUNCTION_PATTERN.finditer(text)
		if match.group("name") not in NON_FUNCTION_KEYWORDS
	]


def subsystem_key(rel_path: str) -> str:
	if rel_path.startswith("src/code/client/"):
		return "client"
	if rel_path.startswith("src/code/qcommon/"):
		return "qcommon"
	if rel_path.startswith("src/code/renderer/"):
		return "renderer"
	if rel_path.startswith("src/code/server/"):
		return "server"
	if rel_path.startswith("src/code/ui/"):
		return "ui"
	if rel_path.startswith("src/code/cgame/") or rel_path.startswith("src/code/game/"):
		return "modules"
	if rel_path.startswith("src/code/win32/"):
		return "platform"
	if rel_path.startswith("src/code/botlib/"):
		return "botlib"
	if rel_path.startswith("src/common/"):
		return "engine_full"
	if rel_path.startswith("src/code/unix/") or rel_path.startswith("src/code/null/"):
		return "repo"
	return "plan"


def owning_audited_section(rel_path: str) -> str | None:
	for section in PRIMARY_SECTIONS:
		if rel_path.startswith(section + "/") or rel_path == section:
			return section
	for section in COMPATIBILITY_SECTIONS:
		if rel_path.startswith(section + "/") or rel_path == section:
			return section
	for section in SECONDARY_SECTIONS:
		if rel_path.startswith(section + "/") or rel_path == section:
			return section
	return None


def section_audit(rel_path_or_section: str) -> dict[str, object] | None:
	section = rel_path_or_section
	if section not in PRIMARY_SECTIONS and section not in COMPATIBILITY_SECTIONS and section not in SECONDARY_SECTIONS:
		section = owning_audited_section(rel_path_or_section) or ""
	if not section:
		return None
	return SECTION_AUDITS.get(section)


def has_current_walk(rel_path: str) -> bool:
	audit = section_audit(rel_path)
	return bool(audit and audit.get("completed"))


def note_family(rel_path: str) -> str | None:
	if rel_path not in NOTE_FILES:
		return None
	return "RW-G01" if NOTE_FILES[rel_path].startswith("rw-g01") else "RW-G02"


def note_status(rel_path: str) -> str | None:
	family = note_family(rel_path)
	if family == "RW-G01":
		return "documented-divergence"
	if family == "RW-G02":
		return "gap-note-open"
	return None


def classify(rel_path: str) -> str:
	if rel_path in NOTE_FILES:
		return str(note_status(rel_path))
	if has_current_walk(rel_path):
		return "walked-closed"
	if rel_path.startswith(("src/code/unix/", "src/code/null/")):
		return "compatibility-open"
	if rel_path.startswith(
		(
			"src/code/bspc/",
			"src/code/jpeg-6/",
			"src/code/splines/",
			"src/game/",
			"src/lcc/",
			"src/libs/",
			"src/q3asm/",
			"src/q3map/",
			"src/q3radiant/",
		)
	):
		return "queued-secondary"
	return "baseline-closed"


def ledger_state(rel_path: str) -> str:
	status = classify(rel_path)
	if status == "documented-divergence":
		return f"{note_family(rel_path)} documented divergence note"
	if status == "gap-note-open":
		return f"{note_family(rel_path)} file-level note open"
	if status == "compatibility-open":
		return "RW-G02 tree still open; file-specific gap not yet isolated"
	if status == "queued-secondary":
		return "Secondary source tree; queued after primary runtime surface"
	if status == "walked-closed":
		audit = section_audit(rel_path)
		return str(audit["row_state"])
	if rel_path.startswith("src/code/ui/"):
		return "Subsystem closure stands; read-only file walk pending"
	return "Subsystem closure stands; function walk pending"


def ledger_evidence(rel_path: str) -> str:
	status = classify(rel_path)
	if status in {"documented-divergence", "gap-note-open"}:
		return f"{doc_link('repo')} + [note](source-file-gap-notes/{NOTE_FILES[rel_path]})"
	if status == "compatibility-open":
		return doc_link("repo")
	if status == "queued-secondary":
		return doc_link("plan")
	if status == "walked-closed":
		return f"{doc_link(subsystem_key(rel_path))} + current 2026-04-22 source walk"
	return doc_link(subsystem_key(rel_path))


def gap_note_link(rel_path: str) -> str:
	if rel_path in NOTE_FILES:
		return f"[note](source-file-gap-notes/{NOTE_FILES[rel_path]})"
	return "-"


def add_note(
	configs: dict[str, dict[str, object]],
	rel_path: str,
	family: str,
	classification: str,
	why: str,
	observed: list[str],
	closure: list[str],
	default_status: tuple[str, str] | None = None,
	overrides: dict[str, tuple[str, str]] | None = None,
	surface_rows: list[tuple[str, str, str]] | None = None,
) -> None:
	configs[rel_path] = {
		"family": family,
		"classification": classification,
		"why": why,
		"observed": observed,
		"closure": closure,
		"default_status": default_status,
		"overrides": overrides or {},
		"surface_rows": surface_rows,
	}


def build_gap_note_configs() -> dict[str, dict[str, object]]:
	configs: dict[str, dict[str, object]] = {}

	add_note(
		configs,
		"src/common/platform/platform_config.h",
		"RW-G01",
		"Documented repo-wide divergence; strict-retail Windows closure intentionally excludes this default-disabled compatibility-only build lane.",
		"This header defaults `QL_BUILD_ONLINE_SERVICES` to `0` and forces both provider macros off in the default build, which keeps the checked-in online-service story explicitly bounded instead of over-claiming retail-equivalent behavior.",
		[
			"`QL_BUILD_ONLINE_SERVICES` defaults to `0` when no override is supplied.",
			"When online services are disabled, both `QL_BUILD_STEAMWORKS` and `QL_BUILD_OPEN_STEAM` are forced to `0` as well.",
			"The derived `QL_PLATFORM_HAS_*` and `QL_PLATFORM_BUILD_HYBRID` macros therefore advertise a bounded compatibility story instead of retail live-service parity in default builds.",
		],
		[
			"Keep the default-disabled policy documented as an intentional divergence unless a real open service path becomes a target.",
			"When the policy changes, the surrounding service table, auth dispatch, and runtime evidence need to be refreshed together so this header does not drift from the rest of the lane.",
		],
		surface_rows=[
			("`QL_BUILD_ONLINE_SERVICES`", "divergence owner", "Defaults to `0`, which keeps the whole online-service lane explicitly bounded by policy."),
			("`QL_BUILD_STEAMWORKS`", "bounded compatibility", "Forced off in the default build unless online services are explicitly enabled."),
			("`QL_BUILD_OPEN_STEAM`", "bounded compatibility", "Forced off in the default build unless online services are explicitly enabled."),
			("`QL_PLATFORM_HAS_ONLINE_SERVICES`", "derived divergence flag", "Mirrors the bounded build policy rather than proving a retail-equivalent service surface."),
			("`QL_PLATFORM_HAS_STEAMWORKS`", "derived divergence flag", "Only reports an opted-in build capability."),
			("`QL_PLATFORM_HAS_OPEN_STEAM`", "derived divergence flag", "Only reports an opted-in build capability."),
			("`QL_PLATFORM_BUILD_HYBRID`", "derived divergence flag", "Advertises a hybrid fallback lane rather than a retail live-service closure claim."),
			("`QL_PLATFORM_HAS_STEAM_SERVICES`", "derived divergence flag", "Reports bounded Steam-facing service availability, not repo-wide parity closure."),
		],
	)

	add_note(
		configs,
		"src/common/platform/platform_services.c",
		"RW-G01",
		"Documented repo-wide divergence; strict-retail Windows closure intentionally excludes this compatibility-only build lane.",
		"This file publishes build-disabled, externally-disabled, Steamworks, open-adapter, and hybrid descriptors. That keeps the repo honest and makes the bounded compatibility story explicit instead of pretending the checked-in tree has a retail-equivalent live-service surface.",
		[
			"Default builds return `Build-disabled (QL_BUILD_ONLINE_SERVICES=0)` provider labels for auth, matchmaking, workshop, overlay, and stats.",
			"Runtime environment variables can also force the descriptor table into a disabled external-ecosystem mode.",
			"Hybrid and open-adapter provider labels remain explicit compatibility descriptors, not evidence of a retail live-service implementation.",
		],
		[
			"Keep the current explicit compatibility labels while this lane remains a documented divergence.",
			"If a real open implementation is pursued later, refresh the descriptor table, auth, workshop, and runtime evidence together so the policy story stays consistent.",
		],
		default_status=("helper closed", "Helper-only function; not the primary remaining parity blocker by itself."),
		overrides={
			"QL_PlatformExternalEcosystemsDisabled": ("bounded compatibility", "Runtime kill-switch for the non-retail external ecosystem lane."),
			"QL_FinaliseDescriptor": ("bounded compatibility", "Normalises fallback labels for compatibility descriptors."),
			"QL_PlatformSteamworks_InitOnce": ("bounded compatibility", "Caches wrapper initialisation, but still sits under the bounded online-service policy."),
			"QL_BuildServiceTable": ("divergence owner", "Builds the service descriptor table that explicitly advertises build-disabled and compatibility-only providers."),
		},
	)

	add_note(
		configs,
		"src/common/platform/backends/platform_backend_open_steam.c",
		"RW-G01",
		"Documented repo-wide divergence; this backend intentionally remains a heuristic compatibility surface.",
		"The open adapter backend still decides accept, retry, and deny outcomes from token length and substring heuristics rather than from a transport-backed exchange with a documented open replacement service.",
		[
			"Standalone launcher tokens are accepted, retried, or denied based on payload length and substring checks such as `refresh`, `revoke`, and `denied`.",
			"Steam fallback tickets are also accepted or denied from local string inspection rather than an external validation path.",
			"The file is honest about being a bounded compatibility path, but it is still not a retail-equivalent service implementation.",
		],
		[
			"If this lane stays bounded, keep the heuristic token-shape logic documented as intentional compatibility behavior.",
			"If a documented open transport path is adopted later, replace the heuristics and refresh the surrounding auth evidence together.",
		],
		default_status=("divergence owner", "This file is entirely the current heuristic open-adapter compatibility backend."),
	)

	add_note(
		configs,
		"src/common/platform/backends/platform_backend_steamworks.c",
		"RW-G01",
		"Documented repo-wide divergence; this backend intentionally resolves auth outcomes heuristically.",
		"The Steamworks auth backend currently uses local ticket-length and substring heuristics to decide accepted, pending, or denied outcomes, so it remains a bounded compatibility surface rather than direct proof of retail-equivalent live-service behavior.",
		[
			"Short tickets are denied immediately as malformed.",
			"The backend returns `PENDING` on string matches such as `retry` and denies tickets containing `denied` or `invalid`.",
			"Accepted responses are still generated locally from ticket shape rather than a live validation exchange.",
		],
		[
			"If repo-wide online-service parity ever becomes a target, replace the heuristic accept or retry mapping with a real validated path.",
			"Until then, keep the file documented as a bounded compatibility backend.",
		],
		default_status=("divergence owner", "This file is entirely the current heuristic Steamworks auth backend."),
	)

	add_note(
		configs,
		"src/code/client/ql_auth.c",
		"RW-G01",
		"Documented repo-wide divergence; this dispatcher intentionally routes into bounded compatibility backends.",
		"The client auth owner cleanly reconstructs the dispatcher and ticket lifetime, but the actual online-service lane it drives is still bounded by build/runtime policy and heuristic Steam or open-adapter backends.",
		[
			"Steam auth requests are blocked entirely when `CL_SteamServicesEnabled()` is false.",
			"Standalone launcher auth is blocked when `CL_OnlineServicesEnabled()` is false.",
			"Hybrid dispatch explicitly falls back to the open adapter whenever the Steamworks lane does not accept the credential.",
		],
		[
			"Keep the dispatcher aligned with the bounded provider set while this lane remains a documented divergence.",
			"If the providers beneath it change, refresh `platform_services.c`, the backend files, and the runtime evidence/docs together so the auth story stays consistent end-to-end.",
		],
		default_status=("helper closed", "Local helper or logging function; not the direct remaining parity blocker on its own."),
		overrides={
			"QL_ClientAuth_InvokeBackend": ("bounded compatibility", "Reports build-unavailable backend states instead of closing the live-service lane."),
			"QL_ClientAuth_RequestSteamTicket": ("bounded compatibility", "Still depends on the build/runtime Steam-service gate before any online auth path exists."),
			"QL_ClientAuth_HandleSteamworksTicket": ("divergence owner", "Dispatches into the heuristic Steamworks backend."),
			"QL_ClientAuth_HandleOpenSteamTicket": ("divergence owner", "Dispatches into the heuristic open-adapter Steam fallback path."),
			"QL_ClientAuth_HandleStandaloneToken": ("divergence owner", "Dispatches standalone launcher tokens into the same bounded open-adapter lane."),
			"QL_ClientAuth_HandleHybridSteam": ("divergence owner", "Explicitly encodes the hybrid compatibility fallback from Steamworks to the open adapter."),
			"QL_ClientAuth_DispatchSteam": ("divergence owner", "Selects between Steamworks, open-adapter, and hybrid compatibility providers."),
			"QL_Auth_ExecuteRequest": ("divergence owner", "Top-level auth request path remains gated by build/runtime policy and bounded providers."),
		},
	)

	add_note(
		configs,
		"src/code/client/cl_steam_resources.c",
		"RW-G01",
		"Documented repo-wide divergence; live resource resolution remains a bounded bridge or stub lane.",
		"The client resource bridge reconstructs the menu-facing resource flow, but Steam-backed requests still devolve into stubs or fallback launch-resource paths whenever live services are disabled or unavailable.",
		[
			"`CL_Steam_RegisterShader()` logs `UI: Steam resource request stubbed` when Steam services are disabled by build or runtime policy.",
			"`QLResourceInterceptor_OnRequest()` falls back from SteamDataSource to launcher/web filesystem owners instead of proving a retail-equivalent live resource path.",
			"`CL_InitSteamResources()` explicitly reports that the Steam resource bridge is disabled by build/runtime policy when the lane is unavailable.",
		],
		[
			"Keep the fallback and stub logging explicit while Steam-backed menu resources remain an intentional bounded compatibility story.",
			"If a real open replacement path is adopted later, refresh the request bridge and note accordingly.",
		],
		default_status=("helper closed", "Utility parser or cache helper; not the direct remaining parity blocker on its own."),
		overrides={
			"CL_SteamResources_RequestAvatarRGBA": ("bounded compatibility", "Still depends on the Steam-facing compatibility bridge rather than a repo-wide-closed live path."),
			"CL_SteamDataSource_Request": ("divergence owner", "Live resource requests still depend on bounded Steam or launcher compatibility backends."),
			"QLResourceInterceptor_OnRequest": ("divergence owner", "Routes URI resources through the current fallback bridge instead of a closed retail-equivalent lane."),
			"CL_Steam_RegisterShader": ("divergence owner", "Resource registration still stubs or falls back when the live service lane is disabled."),
			"CL_InitSteamResources": ("bounded compatibility", "Publishes the build/runtime-disabled status of the bridge."),
			"Sys_Steam_RequestURL": ("divergence owner", "Public request bridge still returns launcher-backed compatibility data rather than a closed retail service surface."),
		},
	)

	add_note(
		configs,
		"src/code/server/sv_rankings.c",
		"RW-G01",
		"Documented repo-wide divergence; default builds intentionally expose a retained rankings compatibility surface instead of a live service integration.",
		"The default `!QL_ENABLE_RANKINGS` branch is explicit and useful, but it keeps the checked-in default build honest about not implementing retail-equivalent rankings behavior.",
		[
			"The disabled branch logs `Rankings disabled by build policy (QL_ENABLE_RANKINGS=0)` and forces `sv_enableRankings` back to `0` when requested.",
			"Most disabled-branch functions publish compatibility-safe return values or no-ops rather than a live rankings path.",
			"The live rankings implementation remains present under the enabled branch, but the repo-wide default policy keeps that surface outside closure.",
		],
		[
			"Keep rankings permanently documented as a bounded compatibility lane unless a real open replacement path is adopted.",
			"If the checked-in default branch changes, refresh the rankings note and repo-wide audit together.",
		],
		default_status=("bounded compatibility", "File member inside the retained rankings compatibility branch."),
		overrides={
			"SV_RankPublishDisabledState": ("divergence owner", "Publishes the disabled compatibility state to cvars."),
			"SV_RankLogDisabledState": ("divergence owner", "Makes the build-disabled rankings policy explicit at runtime."),
			"SV_RankBegin": ("divergence owner", "Disabled-branch entry point forces the rankings surface back to compatibility-only behavior."),
			"SV_RankCheckInit": ("bounded compatibility", "Only reports the stub server-id state in disabled builds."),
			"SV_RankActive": ("bounded compatibility", "Hard-wired false in the disabled branch."),
			"SV_RankPoll": ("bounded compatibility", "No-op in the disabled branch."),
			"SV_RankUserStatus": ("bounded compatibility", "Returns compatibility-safe defaults in the disabled branch."),
			"SV_RankUserReset": ("bounded compatibility", "No-op compatibility branch."),
			"SV_RankReportInt": ("bounded compatibility", "No-op compatibility branch."),
			"SV_RankReportStr": ("bounded compatibility", "No-op compatibility branch."),
		},
	)

	add_note(
		configs,
		"src/code/unix/unix_main.c",
		"RW-G02",
		"Open repo-wide gap; several helpers are now bounded, but the broader Unix host still remains compatibility-only rather than retail-equivalent.",
		"This file has absorbed a lot of restoration work, yet its current state is still explicitly bounded: profiling is optional, clipboard access depends on host tools, `Sys_CheckCD()` is only a coarse data-root probe, and the surrounding Unix runtime is not claimed as a retail-equivalent client host.",
		[
			"`Sys_LowPhysicalMemory()`, `Sys_FunctionCmp()`, `Sys_FunctionCheckSum()`, `Sys_MonkeyShouldBeSpanked()`, bounded `gprof` hooks, clipboard retrieval, and `Sys_CheckCD()` are all restored in scoped form.",
			"The file still underpins a broader Unix runtime that the repo-wide audit explicitly classifies as compatibility-only rather than a closed retail replacement target.",
			"Optional profiling and environment-dependent clipboard helpers remain bounded host shims, not broad portability closure proof.",
		],
		[
			"Finish deciding whether the Unix runtime is meant to reach client/runtime parity or remain a compatibility-only boundary.",
			"When that decision is made, rerun the full Unix file walk and split the still-bounded helpers from any truly closed retail-equivalent host functions.",
		],
		default_status=("not currently implicated", "Recovered or retained helper not currently singled out as the active remaining portability blocker."),
		overrides={
			"Sys_ResolveProfilingHooks": ("bounded compatibility", "Optional `moncontrol` / `_mcleanup` path only exists when the host build enables profiling."),
			"Sys_SetProfilingEnabled": ("bounded compatibility", "Only meaningful inside the bounded optional profiling lane."),
			"Sys_BeginProfiling": ("bounded compatibility", "Restored, but still intentionally scoped to `QL_ENABLE_GPROF=1` hosts."),
			"Sys_EndProfiling": ("bounded compatibility", "Restored, but still intentionally scoped to `QL_ENABLE_GPROF=1` hosts."),
			"Sys_CheckCD": ("bounded compatibility", "Now a coarse data-root probe rather than an unconditional success stub, but still not a full portability closure claim."),
			"Sys_IsExecutableOnPath": ("bounded compatibility", "Supports the bounded clipboard helper chain rather than a broad host-API abstraction."),
			"main": ("compatibility host owner", "Top-level Unix host entry remains part of the broader still-open portability lane."),
		},
	)

	add_note(
		configs,
		"src/code/unix/linux_glimp.c",
		"RW-G02",
		"Open repo-wide gap; this legacy X11/GLX client host path is not currently closed as a retail-equivalent portability surface.",
		"The file is the retained Linux OpenGL/input host implementation, but the repo-wide audit still treats the Linux client, renderer, and input runtime as compatibility-only rather than part of the closed Windows replacement target.",
		[
			"The file still owns the Linux GLX window, gamma, input-grab, and renderer-thread glue path.",
			"No current repo-wide claim says the Linux client/runtime is equivalent to the closed Windows target.",
			"The portability work completed so far has focused on bounded Unix helper restoration rather than on closing this renderer/input host lane.",
		],
		[
			"Close the broader Linux client/runtime portability decision first, then rerun this file function-by-function with the chosen target in mind.",
			"If Linux client/runtime parity is not a target, keep this file explicitly classified as a compatibility-only host carry.",
		],
		default_status=(
			"bounded compatibility",
			"Legacy Linux renderer/input host helper inside the still-open portability tree; not currently isolated as a separate repo-wide owner.",
		),
		overrides={
			"GLimp_SetGamma": ("open portability owner", "Renderer gamma host path remains inside the still-open Linux client/runtime lane."),
			"GLimp_Shutdown": ("open portability owner", "Linux GL teardown still belongs to the unresolved portability host surface."),
			"GLimp_Init": ("open portability owner", "Top-level Linux GL init path remains inside the unresolved portability lane."),
			"GLimp_EndFrame": ("open portability owner", "Linux swap/end-frame host path is not closed repo-wide."),
			"IN_Shutdown": ("open portability owner", "Linux input teardown stays in the open portability lane."),
			"IN_Frame": ("open portability owner", "Linux input pump remains part of the unresolved non-Windows client path."),
			"IN_Activate": ("open portability owner", "Linux active/inactive input state remains portability-owned."),
			"IN_StartupJoystick": ("open portability owner", "Linux joystick startup remains part of the unresolved portability lane."),
		},
	)

	add_note(
		configs,
		"src/code/unix/linux_snd.c",
		"RW-G02",
		"Open repo-wide gap; this OSS audio host path remains part of the unresolved non-Windows client/runtime lane.",
		"The file still implements a classic `/dev/dsp` OSS path, which the repo-wide audit does not treat as closed portability proof for a Linux client/runtime replacement target.",
		[
			"Audio initialisation still opens `snddevice`, which defaults to `/dev/dsp`.",
			"The file owns the OSS capability probing, format selection, and mmap-backed DMA path.",
			"The repo-wide audit still classifies Linux client/runtime support as compatibility-only rather than closed parity.",
		],
		[
			"Either modernise the Linux sound host and validate it as an actual portability target or keep this file explicitly compatibility-only.",
		],
		default_status=("open portability owner", "This function is part of the still-open OSS/Linux sound host path."),
	)

	add_note(
		configs,
		"src/code/unix/linux_joystick.c",
		"RW-G02",
		"Open repo-wide gap; Linux joystick support remains part of the unresolved non-Windows input host lane.",
		"The file still owns `/dev/js*` probing and axis-to-key translation, but that input path is not currently claimed as a closed portability surface in the repo-wide audit.",
		[
			"The startup path walks `/dev/js0` through `/dev/js3` to find a joystick device.",
			"Axis values are still translated into Quake-style key events through threshold checks.",
			"The repo-wide audit still treats Linux input support as part of the broader unresolved portability lane.",
		],
		[
			"Do not close this file until the broader Linux input story is either validated or explicitly bounded permanently.",
		],
		default_status=("open portability owner", "This function belongs to the still-open Linux joystick/input lane."),
	)

	add_note(
		configs,
		"src/code/null/null_main.c",
		"RW-G02",
		"Open repo-wide gap; this is a compatibility-only null host, not a retail-equivalent runtime.",
		"The file now carries more of the current host contract than the old stale null runtime did, but it is still explicitly a null compatibility host rather than a real runtime replacement path.",
		[
			"The file now preserves executable-name, path, wall-clock, directory, and stream helpers that match current host expectations more closely.",
			"`Sys_GetGameAPI()` still returns `NULL`, and `Sys_GetClipboardData()` still returns `NULL`.",
			"The repo-wide audit still classifies the null runtime as compatibility-only rather than part of the closed Windows replacement target.",
		],
		[
			"Either keep the null host as a permanent compatibility shim or raise it to a better-defined portability target with explicit non-null host contracts.",
			"Until then, treat the file as evidence that the repo-wide score still excludes non-Windows/null host equivalence.",
		],
		default_status=("bounded compatibility", "Compatibility-only null-host helper."),
		overrides={
			"Sys_UnloadGame": ("bounded compatibility", "No-op null-host lifecycle stub."),
			"Sys_GetGameAPI": ("open portability owner", "Returns `NULL`, so the null runtime still cannot stand in for a real module host."),
			"Sys_GetClipboardData": ("open portability owner", "Returns `NULL`; clipboard remains absent in the null host."),
			"Sys_DisplaySystemConsole": ("bounded compatibility", "No-op null-host console shim."),
			"Sys_SetErrorText": ("bounded compatibility", "No-op null-host error-text shim."),
			"Sys_Init": ("bounded compatibility", "Initialises the null host path but does not close the portability lane."),
			"main": ("open portability owner", "Top-level null runtime entry remains part of the unresolved compatibility-only host lane."),
		},
	)

	add_note(
		configs,
		"src/code/null/null_glimp.c",
		"RW-G02",
		"Open repo-wide gap; the file is a compatibility-only null renderer host rather than a real graphics runtime.",
		"The file now carries the corrected renderer-host signatures, but every GL entry point is still empty or returns a compatibility-safe default, so the null runtime still lacks a real graphics host.",
		[
			"`GLimp_Init()`, `GLimp_EndFrame()`, and `GLimp_Shutdown()` are empty.",
			"`QGL_Init()` returns `qtrue` without loading a renderer library or binding real GL entry points.",
			"The repo-wide audit still states that the null runtime does not implement a real live graphics/audio/input host.",
		],
		[
			"Either keep the null renderer host as an explicit compatibility shim or raise it to a better-defined non-Windows graphics target.",
			"Do not close the file while the null runtime still lacks a real graphics context, swap path, and GL loader contract.",
		],
		default_status=("bounded compatibility", "Null renderer-host compatibility shim."),
		overrides={
			"GLimp_EndFrame": ("open portability owner", "No-op swap/end-frame path inside the null compatibility host."),
			"GLimp_Init": ("open portability owner", "No-op renderer-host initialisation; the null runtime creates no graphics context."),
			"GLimp_Shutdown": ("open portability owner", "No-op renderer-host teardown inside the null compatibility lane."),
			"QGL_Init": ("open portability owner", "Returns `qtrue` without loading or validating a real GL backend."),
		},
	)

	add_note(
		configs,
		"src/code/null/null_client.c",
		"RW-G02",
		"Open repo-wide gap; the file is a retained compatibility shim for browser, advert, and client entry points.",
		"This file carries the modern null-client contract more honestly than the older stubs did, but almost every browser, advert, and client-owner entry point still resolves to a no-op or compatibility-safe default.",
		[
			"Browser state is forced off through `ui_browserAwesomium` and `web_browserActive` cvars.",
			"Live-view, bound-window-object, cursor, event-publication, and advert-bridge entry points remain null-host stubs.",
			"The repo-wide audit still treats the null client/browser/advert lane as compatibility-only rather than closed parity.",
		],
		[
			"If the null client remains only a portability shim, keep these no-op bridges explicit and leave the repo-wide portability gap open.",
			"Do not close the file unless the repo begins claiming a richer null-host parity target than the current compatibility boundary.",
		],
		default_status=("bounded compatibility", "Null-client compatibility shim."),
		overrides={
			"CL_RefreshOnlineServicesBridgeState": ("open portability owner", "Explicitly forces the browser/online-service cvars into the null-host state."),
			"CL_WebHost_Init": ("open portability owner", "Initialises only the null browser-host compatibility state."),
			"CL_WebHost_Shutdown": ("open portability owner", "Shuts down only the null browser-host compatibility state."),
			"CL_WebHost_Frame": ("open portability owner", "No-op browser-host frame pump for the null runtime."),
			"CL_WebHost_HasLiveView": ("open portability owner", "Always false in the null compatibility host."),
			"CL_WebHost_HasBoundWindowObject": ("open portability owner", "Always false in the null compatibility host."),
			"CL_WebHost_GetCursorHandle": ("open portability owner", "Always returns `NULL`."),
			"CL_WebHost_NotifyAppActivation": ("bounded compatibility", "No-op null-host activation shim."),
			"CL_WebView_PublishEvent": ("open portability owner", "Null-host publication stub for browser events."),
			"CL_WebView_InvokeCommNotice": ("open portability owner", "Null-host browser bridge stub."),
			"CL_WebView_PublishGameError": ("open portability owner", "Null-host browser bridge stub."),
			"CL_WebView_PublishGameEnd": ("open portability owner", "Null-host browser bridge stub."),
			"CL_WebView_PublishBindChanged": ("open portability owner", "Null-host browser bridge stub."),
			"CL_WebView_PublishGameStart": ("open portability owner", "Null-host browser bridge stub."),
			"CL_WebView_PublishGameScreenshot": ("open portability owner", "Null-host browser bridge stub."),
			"CL_WebView_OnMouseMove": ("open portability owner", "Null-host input bridge stub."),
			"CL_WebView_OnMouseButtonEvent": ("open portability owner", "Null-host input bridge stub."),
			"CL_WebView_OnMouseWheelEvent": ("open portability owner", "Null-host input bridge stub."),
			"CL_WebView_OnKeyEvent": ("open portability owner", "Null-host input bridge stub."),
			"CL_AdvertisementBridge_RefreshLoadingViewParameters": ("open portability owner", "Null advert bridge shim."),
			"CL_AdvertisementBridge_UpdateLoadingViewParameters": ("open portability owner", "Null advert bridge shim."),
			"CL_AdvertisementBridge_InitUI": ("open portability owner", "Null advert bridge shim."),
			"CL_AdvertisementBridge_ActivateAdvert": ("open portability owner", "Null advert bridge shim."),
			"CL_AdvertisementBridge_SetActiveAdvert": ("open portability owner", "Null advert bridge shim."),
		},
	)

	add_note(
		configs,
		"src/code/null/null_input.c",
		"RW-G02",
		"Open repo-wide gap; the file exposes bootstrap cvars but still resolves to a no-device input shim.",
		"The file now touches the modern input cvar surface and keeps `ui_joyavail` honest, but it still represents a no-device compatibility path rather than a real input host.",
		[
			"The current null input path seeds `in_mouse`, `in_nograb`, `in_joystick`, `in_debugjoystick`, and `joy_threshold` cvars.",
			"`IN_Frame()` only refreshes the compatibility state; it does not drive a real input backend.",
			"`Sys_SendKeyEvents()` remains empty.",
		],
		[
			"Either keep the null input layer explicitly no-op or promote it to a better-defined host target; do not blur the current boundary.",
		],
		default_status=("bounded compatibility", "Null-input compatibility shim."),
		overrides={
			"IN_NullRefreshCompatibilityState": ("open portability owner", "Maintains the explicit no-device input state."),
			"IN_Init": ("open portability owner", "Initialises only the null input compatibility cvars."),
			"IN_Frame": ("open portability owner", "No real input pump; only refreshes null compatibility state."),
			"IN_Shutdown": ("bounded compatibility", "Null-input shutdown shim."),
			"Sys_SendKeyEvents": ("open portability owner", "Still empty, so the null runtime has no real key-event pump."),
		},
	)

	add_note(
		configs,
		"src/code/null/null_snddma.c",
		"RW-G02",
		"Open repo-wide gap; the file is an explicitly silent sound/device compatibility shim.",
		"This file honestly exposes the current sound entry points, but it still resolves every one of them to silent or no-op behavior, which keeps the null runtime outside any repo-wide parity closure claim.",
		[
			"`SNDDMA_Init()` returns `qfalse`.",
			"DMA position, shutdown, begin-painting, submit, activation, local-sound, and voice-sample entry points are all compatibility-safe no-ops.",
			"The repo-wide audit explicitly classifies these sound/device activation and voice surfaces as shims, not as portability closure.",
		],
		[
			"Keep the file explicitly classified as a silent compatibility shim unless the null runtime grows a richer audio target.",
		],
		default_status=("open portability owner", "Silent sound or voice compatibility stub."),
	)

	return configs


def write_lines(path: Path, lines: list[str]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_gap_note(rel_path: str, config: dict[str, object]) -> None:
	text = read_text(rel_path)
	functions = extract_functions(text)
	classification = str(config["classification"])
	is_documented_divergence = "documented" in classification.lower() and "divergence" in classification.lower()
	title = "Divergence Note" if is_documented_divergence else "Gap Note"
	why_heading = "## Why this file remains a documented divergence" if is_documented_divergence else "## Why this file is still open"
	target_heading = "## Maintenance expectations" if is_documented_divergence else "## Closure target"

	lines = [
		f"# `{rel_path}` {title}",
		"",
		f"Last updated: {DATE}",
		"",
		f"Gap family: `{config['family']}`",
		"- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.",
		f"- Current classification: {config['classification']}",
		"",
		why_heading,
		"",
		str(config["why"]),
		"",
		"## Observed facts",
		"",
	]
	for item in config["observed"]:  # type: ignore[index]
		lines.append(f"- {item}")
	lines.extend(["", "## Function-by-function status" if not config.get("surface_rows") else "## Surface-by-surface status", ""])

	if config.get("surface_rows"):
		lines.extend(
			[
				"| Surface | Status | Notes |",
				"| --- | --- | --- |",
			]
		)
		for surface, status, notes in config["surface_rows"]:  # type: ignore[index]
			lines.append(f"| {surface} | `{status}` | {notes} |")
	else:
		default_status = config.get("default_status", ("not currently implicated", "No file-specific parity gap has been isolated to this function yet."))
		overrides: dict[str, tuple[str, str]] = config["overrides"]  # type: ignore[index]
		lines.extend(
			[
				"| Function | Status | Notes |",
				"| --- | --- | --- |",
			]
		)
		for function in functions:
			status, notes = overrides.get(function, default_status)  # type: ignore[arg-type]
			lines.append(f"| `{function}` | `{status}` | {notes} |")

	lines.extend(["", target_heading, ""])
	for item in config["closure"]:  # type: ignore[index]
		lines.append(f"- {item}")

	write_lines(GAP_NOTES_ROOT / NOTE_FILES[rel_path], lines)


def write_gap_notes(configs: dict[str, dict[str, object]]) -> None:
	for rel_path in GAP_NOTE_ORDER:
		render_gap_note(rel_path, configs[rel_path])

	write_lines(
		README_PATH,
		[
			"# Source-File Gap Notes",
			"",
			f"Last updated: {DATE}",
			"",
			"Each note in this directory exists only when a concrete parity gap or documented bounded divergence has already been isolated to a specific file. The main ledger keeps tree-level or inherited status; these notes are for file-level ownership only.",
			"",
			"Every note should capture:",
			"",
			"- the owning repo-wide gap family;",
			"- the file-level reason the gap remains open or the divergence remains intentional;",
			"- observed facts grounded in current source or committed evidence;",
			"- a function-by-function status table; and",
			"- an explicit closure target or maintenance expectation.",
		],
	)


def write_plan(
	primary_sections: OrderedDict[str, list[str]],
	compatibility_sections: OrderedDict[str, list[str]],
	secondary_sections: OrderedDict[str, list[str]],
	total_tracked: int,
) -> None:
	primary_total = sum(len(files) for files in primary_sections.values())
	compatibility_total = sum(len(files) for files in compatibility_sections.values())
	secondary_total = sum(len(files) for files in secondary_sections.values())

	lines = [
		"# Source-File Parity Audit Plan",
		"",
		f"Last updated: {DATE}",
		"",
		"## Purpose",
		"",
		"This campaign breaks the broad parity story back down into manageable, checklisted file walks. It supplements `AUDIT.md`, `IMPLEMENTATION_PLAN.md`, and the existing subsystem ledgers instead of replacing them.",
		"",
		"Per tracked file, the campaign should eventually produce:",
		"",
		"- one concise row in the main source-file parity ledger;",
		"- a dedicated per-file note whenever a concrete parity gap or documented bounded divergence is confirmed; and",
		"- a function-by-function status table inside that per-file note.",
		"",
		"## Scope",
		"",
		f"- Primary runtime and reconstruction surface tracked now: `{primary_total}` files.",
		f"- Compatibility-only Unix/null surface tracked now: `{compatibility_total}` files.",
		f"- Secondary tool, editor, compiler, and legacy source surface tracked now: `{secondary_total}` files.",
		f"- Header exception tracked alongside compilation units: `{len(HEADER_EXCEPTIONS)}` file (`src/common/platform/platform_config.h`).",
		f"- Total tracked source entries in the campaign ledger: `{total_tracked}`.",
		"- Generated/vendor mirror trees under `src/libs/_deps/` and `src/libs/_build/` stay out of this campaign so the audit remains focused on repo-owned reconstruction and support sources.",
		"",
		"## Deliverables",
		"",
		f"- Main ledger: `docs/reverse-engineering/source-file-parity-ledger-{DATE}.md`",
		f"- Historical index: `docs/reverse-engineering/historical-audit-index-{DATE}.md`",
		"- File-level gap notes: `docs/reverse-engineering/source-file-gap-notes/`",
		"- Repo-wide summary ledgers remain `AUDIT.md` and `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`.",
		"",
		"## Checklist",
		"",
		"### Phase 0 - Documentation Baseline",
		"",
		"- [x] Keep `AUDIT.md` and `IMPLEMENTATION_PLAN.md` in place as gate-facing ledgers.",
		f"- [x] Create `source-file-parity-ledger-{DATE}.md` as the clean main file-by-file ledger.",
		f"- [x] Create `historical-audit-index-{DATE}.md` instead of renaming or moving older audit docs that workflows and tests already reference.",
		f"- [x] Seed `{len(GAP_NOTE_ORDER)}` concrete per-file notes for the currently evidenced `RW-G01` documented divergences and `RW-G02` gap owners.",
		"",
		"### Phase 1 - Strict-Retail Engine Core",
		"",
	]

	def append_section_plan_item(section: str, count: int, read_only: bool = False, compatibility: bool = False) -> None:
		audit = section_audit(section)
		checked = bool(audit and audit.get("completed"))
		mark = "x" if checked else " "
		if compatibility:
			lines.append(
				f"- [{mark}] Audit `{section}` and convert tree-level `RW-G02` status into file-specific notes where warranted (`{count}` tracked files)."
			)
		else:
			suffix = " (read-only source tree)." if read_only else "."
			lines.append(f"- [{mark}] Audit `{section}` function-by-function (`{count}` tracked files){suffix}")
		if checked:
			for note in audit.get("plan_result", []):  # type: ignore[union-attr]
				lines.append(f"  {note}")

	for section in (
		"src/common",
		"src/code/qcommon",
		"src/code/client",
		"src/code/server",
		"src/code/renderer",
		"src/code/win32",
		"src/code/botlib",
	):
		append_section_plan_item(section, len(primary_sections[section]))

	lines.extend(["", "### Phase 2 - Module And Gameplay Surface", ""])

	for section in ("src/code/game", "src/code/cgame", "src/code/ui"):
		append_section_plan_item(section, len(primary_sections[section]), read_only=(section == "src/code/ui"))

	lines.extend(["", "### Phase 3 - Compatibility-Only Host Surface", ""])

	for section in ("src/code/unix", "src/code/null"):
		append_section_plan_item(section, len(compatibility_sections[section]), compatibility=True)

	lines.extend(["", "### Phase 4 - Secondary Tool, Editor, Compiler, And Legacy Source Trees", ""])

	for group in PHASE4_GROUP_AUDITS:
		sections = group["sections"]  # type: ignore[assignment]
		count = sum(len(secondary_sections[section]) for section in sections)  # type: ignore[index]
		checked = all(bool(section_audit(section) and section_audit(section).get("completed")) for section in sections)  # type: ignore[union-attr]
		mark = "x" if checked else " "
		lines.append(
			f"- [{mark}] Audit {group['label']} after the primary runtime surface is complete (`{count}` tracked files)."
		)
		if checked:
			for note in group.get("plan_result", []):  # type: ignore[union-attr]
				lines.append(f"  {note}")

	lines.extend(["", "## Current seeded documented-divergence note set", ""])

	for rel_path in GAP_NOTE_ORDER:
		if note_status(rel_path) != "documented-divergence":
			continue
		lines.append(
			f"- `{note_family(rel_path)}`: `{rel_path}` -> `docs/reverse-engineering/source-file-gap-notes/{NOTE_FILES[rel_path]}`"
		)

	lines.extend(["", "## Current seeded active file-level gap set", ""])

	for rel_path in GAP_NOTE_ORDER:
		if note_status(rel_path) != "gap-note-open":
			continue
		lines.append(
			f"- `{note_family(rel_path)}`: `{rel_path}` -> `docs/reverse-engineering/source-file-gap-notes/{NOTE_FILES[rel_path]}`"
		)

	lines.extend(
		[
			"",
			"## Completion criteria",
			"",
			"- Every tracked file in the ledger has been explicitly walked in the current campaign, not just inherited from an older subsystem closure note.",
			"- Every file with a confirmed parity gap or documented divergence has its own dedicated note with a function-by-function status table and explicit closure conditions.",
			"- `AUDIT.md` and the repo-wide audit remain concise summary ledgers instead of turning into file dumps.",
		]
	)

	write_lines(PLAN_PATH, lines)


def write_historical_index() -> None:
	lines = [
		"# Historical Audit Index",
		"",
		f"Last updated: {DATE}",
		"",
		"## Why this exists",
		"",
		"The repo already has workflows and parity tests that reference specific audit documents by name. This index archives and reorganises the current audit landscape without renaming or moving those files.",
		"",
		"## Current summary ledgers",
		"",
		"- `AUDIT.md` - current top-level parity summary and active repo-wide gap register.",
		"- `IMPLEMENTATION_PLAN.md` - current repo-level work queue and active task list.",
		"- `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md` - current repo-wide gap rationale and evidence register.",
		f"- `docs/reverse-engineering/source-file-parity-ledger-{DATE}.md` - new file-by-file campaign ledger.",
		f"- `docs/reverse-engineering/source-file-parity-audit-plan-{DATE}.md` - new chunked execution plan for the file walk.",
		"",
		"## Current strict-retail closure ledgers",
		"",
	]

	for doc in (
		"engine-full-parity-audit-and-implementation-plan-2026-04-10.md",
		"game-module-parity-audit-and-implementation-plan-2026-04-10.md",
		"ui-full-parity-audit-and-implementation-plan-2026-04-05.md",
		"client-full-parity-audit-and-implementation-plan-2026-04-09.md",
		"qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md",
		"qshared-retail-helper-parity-audit-2026-04-17.md",
		"renderer-full-parity-audit-and-implementation-plan-2026-04-09.md",
		"server-full-parity-audit-and-implementation-plan-2026-04-10.md",
		"engine-host-support-full-parity-audit-and-implementation-plan-2026-04-10.md",
		"platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md",
		"engine-netcode-parity-audit-2026-04-16.md",
		"awesomium-browser-host-parity-audit-and-implementation-plan-2026-04-16.md",
	):
		lines.append(f"- `docs/reverse-engineering/{doc}`")

	lines.extend(
		[
			"",
			"## Focused ownership, runtime, and mapping references",
			"",
			"- `docs/reverse-engineering/quakelive_steam_mapping_round_*.md` - mapping-round history and promoted ownership evidence.",
			"- `docs/reverse-engineering/*validation-and-runtime-evidence*.md` - retained runtime bundles and validation notes.",
			"- `docs/reverse-engineering/*ownership*.md` and `docs/reverse-engineering/*struct-layouts*.md` - focused ownership and recovered layout notes.",
			"- `docs/reverse-engineering/cgame-*.md`, `qagame-*.md`, and related subsystem notebooks - narrower reconstruction notes that predate the repo-wide consolidation.",
			"",
			"## Historical broad-planning snapshots",
			"",
			"- `docs/parity-plan.md`",
			"- `docs/ui_deltas.md`",
			"- `docs/ui_followup_issues.md`",
			"",
			"These files remain useful as historical context, but they should not be treated as the current parity source of truth.",
			"",
			"## File-level gap notes",
			"",
			"- `docs/reverse-engineering/source-file-gap-notes/` now holds the current per-file gap drill-downs opened by the source-file campaign.",
			"- Only files with concrete, currently evidenced parity gaps should receive a note; tree-level suspicion belongs in the main ledger until the function walk isolates the file.",
		]
	)

	write_lines(INDEX_PATH, lines)


def place_in_sections(all_tracked: list[str]) -> tuple[OrderedDict[str, list[str]], OrderedDict[str, list[str]], OrderedDict[str, list[str]]]:
	primary = OrderedDict((section, []) for section in PRIMARY_SECTIONS)
	compatibility = OrderedDict((section, []) for section in COMPATIBILITY_SECTIONS)
	secondary = OrderedDict((section, []) for section in SECONDARY_SECTIONS)

	for rel_path in all_tracked:
		for section in primary:
			if rel_path.startswith(section + "/") or rel_path == section:
				primary[section].append(rel_path)
				break
		else:
			for section in compatibility:
				if rel_path.startswith(section + "/") or rel_path == section:
					compatibility[section].append(rel_path)
					break
			else:
				for section in secondary:
					if rel_path.startswith(section + "/") or rel_path == section:
						secondary[section].append(rel_path)
						break

	return primary, compatibility, secondary


def write_ledger(
	all_tracked: list[str],
	function_counts: dict[str, int | str],
	status_counts: defaultdict[str, int],
	primary_sections: OrderedDict[str, list[str]],
	compatibility_sections: OrderedDict[str, list[str]],
	secondary_sections: OrderedDict[str, list[str]],
) -> None:
	lines = [
		"# Source-File Parity Ledger",
		"",
		f"Last updated: {DATE}",
		"",
		"## Purpose",
		"",
		"This is the clean main parity document for the new source-file campaign. It keeps one concise row per tracked source file while leaving the detailed reasoning in the existing subsystem audits and in the new per-file gap notes.",
		"",
		"The ledger does not replace the current gate-facing ledgers. `AUDIT.md`, `IMPLEMENTATION_PLAN.md`, and `repo-wide-parity-audit-2026-04-21.md` remain the high-level summary sources.",
		"",
		"## Scope",
		"",
		f"- Tracked compilation units under `src/` excluding generated/vendor mirror trees under `src/libs/_deps/` and `src/libs/_build/`: `{len(all_tracked) - len(HEADER_EXCEPTIONS)}` files.",
		f"- Header exception tracked because it owns a documented repo-wide divergence policy surface: `{len(HEADER_EXCEPTIONS)}` file.",
		f"- Total tracked source entries in this ledger: `{len(all_tracked)}`.",
		"- Function counts are approximate source-definition counts from the checked-in tree and are meant for audit triage, not for ABI accounting.",
		"",
		"## Status legend",
		"",
	]

	for status, description in STATUS_DESCRIPTIONS.items():
		lines.append(f"- `{status}`: {description}")

	lines.extend(["", "## Current totals", ""])

	for status in STATUS_DESCRIPTIONS:
		lines.append(f"- `{status}`: `{status_counts[status]}` files")

	documented_divergences = [rel_path for rel_path in GAP_NOTE_ORDER if classify(rel_path) == "documented-divergence"]
	open_gap_notes = [rel_path for rel_path in GAP_NOTE_ORDER if classify(rel_path) == "gap-note-open"]

	lines.extend(["", "## Documented divergence notes", "", "| File | Gap family | Note |", "| --- | --- | --- |"])

	for rel_path in documented_divergences:
		lines.append(f"| `{rel_path}` | `{note_family(rel_path)}` | [note](source-file-gap-notes/{NOTE_FILES[rel_path]}) |")

	lines.extend(["", "## Active file-level gap notes", "", "| File | Gap family | Note |", "| --- | --- | --- |"])

	for rel_path in open_gap_notes:
		lines.append(f"| `{rel_path}` | `{note_family(rel_path)}` | [note](source-file-gap-notes/{NOTE_FILES[rel_path]}) |")

	def emit_section(title: str, sections: OrderedDict[str, list[str]]) -> None:
		lines.extend(["", f"## {title}", ""])
		for section, files in sections.items():
			if not files:
				continue
			audit = section_audit(section)
			lines.extend(
				[
					f"### `{section}` ({len(files)} files)",
					"",
				]
			)
			if audit and audit.get("completed"):
				lines.extend(audit.get("ledger_summary", []))  # type: ignore[arg-type]
				lines.append("")
			lines.extend(
				[
					"| File | Functions | Current parity state | Primary evidence | Gap note |",
					"| --- | ---: | --- | --- | --- |",
				]
			)
			for rel_path in files:
				count = function_counts.get(rel_path, "n/a")
				lines.append(
					f"| `{rel_path}` | `{count}` | {ledger_state(rel_path)} | {ledger_evidence(rel_path)} | {gap_note_link(rel_path)} |"
				)

	emit_section("Primary Runtime And Reconstruction Surface", primary_sections)
	emit_section("Compatibility-Only Unix And Null Host Surface", compatibility_sections)
	emit_section("Secondary Tool, Editor, Compiler, And Legacy Source Surface", secondary_sections)

	write_lines(LEDGER_PATH, lines)


def main() -> None:
	argparse.ArgumentParser(description="Generate the 2026-04-22 source-file audit docs.").parse_args()

	GAP_NOTES_ROOT.mkdir(parents=True, exist_ok=True)

	tracked_source_files = source_files()
	all_tracked = list(dict.fromkeys(tracked_source_files + HEADER_EXCEPTIONS))

	function_counts: dict[str, int | str] = {}
	for rel_path in tracked_source_files:
		function_counts[rel_path] = len(extract_functions(read_text(rel_path)))
	function_counts["src/common/platform/platform_config.h"] = "n/a"

	status_counts: defaultdict[str, int] = defaultdict(int)
	for rel_path in all_tracked:
		status_counts[classify(rel_path)] += 1

	primary_sections, compatibility_sections, secondary_sections = place_in_sections(all_tracked)

	write_plan(primary_sections, compatibility_sections, secondary_sections, len(all_tracked))
	write_historical_index()
	write_gap_notes(build_gap_note_configs())
	write_ledger(
		all_tracked,
		function_counts,
		status_counts,
		primary_sections,
		compatibility_sections,
		secondary_sections,
	)

	print(f"Wrote {PLAN_PATH.relative_to(REPO_ROOT)}")
	print(f"Wrote {INDEX_PATH.relative_to(REPO_ROOT)}")
	print(f"Wrote {README_PATH.relative_to(REPO_ROOT)}")
	print(f"Wrote {LEDGER_PATH.relative_to(REPO_ROOT)}")
	print(f"Gap notes written: {len(GAP_NOTE_ORDER)}")


if __name__ == "__main__":
	main()
