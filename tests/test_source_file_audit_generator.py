from __future__ import annotations

import importlib.util
from collections import OrderedDict, defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATOR_PATH = REPO_ROOT / "tools" / "reverse-engineering" / "generate_source_file_audit.py"
BOTLIB_AAS_MAIN = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_main.c"
JPEG_JCAPIMIN = REPO_ROOT / "src" / "code" / "jpeg-6" / "jcapimin.c"
SPLINES_UTIL_STR = REPO_ROOT / "src" / "code" / "splines" / "util_str.cpp"


def _load_generator_module():
	spec = importlib.util.spec_from_file_location("generate_source_file_audit", GENERATOR_PATH)
	assert spec is not None
	assert spec.loader is not None
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


def test_extract_functions_accepts_brace_on_next_line_definitions() -> None:
	module = _load_generator_module()
	text = """
int SameLine(void) {
\treturn 1;
}

static void WrappedDefinition(int value)
{
\t(void)value;
}

void PrototypeOnly(int value);
"""

	assert module.extract_functions(text) == ["SameLine", "WrappedDefinition"]


def test_extract_functions_ignores_control_flow_keywords() -> None:
	module = _load_generator_module()
	text = """
void RealFunction(void)
{
\tif (condition)
\t{
\t\treturn;
\t}

\tfor (;;)
\t{
\t\tbreak;
\t}
}
"""

	assert module.extract_functions(text) == ["RealFunction"]


def test_extract_functions_finds_real_botlib_definitions() -> None:
	module = _load_generator_module()
	text = BOTLIB_AAS_MAIN.read_text(encoding="utf-8", errors="ignore")
	functions = module.extract_functions(text)

	assert "AAS_Error" in functions
	assert "AAS_Setup" in functions
	assert len(functions) >= 10


def test_extract_functions_accepts_libjpeg_macro_style_definitions() -> None:
	module = _load_generator_module()
	text = JPEG_JCAPIMIN.read_text(encoding="utf-8", errors="ignore")
	functions = module.extract_functions(text)

	assert "jpeg_create_compress" in functions
	assert "jpeg_finish_compress" in functions
	assert len(functions) >= 5


def test_extract_functions_accepts_cpp_qualified_methods() -> None:
	module = _load_generator_module()
	text = SPLINES_UTIL_STR.read_text(encoding="utf-8", errors="ignore")
	functions = module.extract_functions(text)

	assert "idStr::toLower" in functions
	assert "idStr::operator+=" in functions
	assert len(functions) >= 10


def test_completed_cgame_surface_classifies_as_walked_closed() -> None:
	module = _load_generator_module()

	assert module.classify("src/code/cgame/cg_draw.c") == "walked-closed"
	assert module.ledger_state("src/code/cgame/cg_draw.c") == "Current function walk complete; no file-level parity gap isolated"
	assert module.ledger_evidence("src/code/cgame/cg_draw.c") == (
		"[module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk"
	)
	assert module.classify("src/code/client/ql_auth.c") == "documented-divergence"
	assert module.ledger_state("src/code/client/ql_auth.c") == "RW-G01 documented divergence note"
	assert module.ledger_evidence("src/code/client/ql_auth.c") == (
		"[repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g01-client-auth.md)"
	)


def test_completed_ui_surface_classifies_as_walked_closed() -> None:
	module = _load_generator_module()

	assert module.classify("src/code/ui/ui_main.c") == "walked-closed"
	assert module.ledger_state("src/code/ui/ui_main.c") == "Current read-only function walk complete; no file-level parity gap isolated"
	assert module.ledger_evidence("src/code/ui/ui_main.c") == (
		"[ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) + current 2026-04-22 source walk"
	)


def test_completed_unix_surface_classifies_non_note_members_as_walked_closed() -> None:
	module = _load_generator_module()

	assert module.classify("src/code/unix/linux_common.c") == "walked-closed"
	assert module.ledger_state("src/code/unix/linux_common.c") == (
		"Current compatibility function walk complete; no new file-level portability gap isolated"
	)
	assert module.ledger_evidence("src/code/unix/linux_common.c") == (
		"[repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + current 2026-04-22 source walk"
	)
	assert module.classify("src/code/unix/unix_main.c") == "gap-note-open"


def test_completed_null_surface_classifies_non_note_members_and_new_gap_owner() -> None:
	module = _load_generator_module()

	assert module.classify("src/code/null/null_net.c") == "walked-closed"
	assert module.ledger_state("src/code/null/null_net.c") == (
		"Current compatibility function walk complete; no new file-level portability gap isolated"
	)
	assert module.ledger_evidence("src/code/null/null_net.c") == (
		"[repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + current 2026-04-22 source walk"
	)
	assert module.classify("src/code/null/null_glimp.c") == "gap-note-open"
	assert module.classify("src/code/null/null_main.c") == "gap-note-open"


def test_completed_secondary_surfaces_classify_as_walked_closed() -> None:
	module = _load_generator_module()

	assert module.classify("src/code/bspc/bspc.c") == "walked-closed"
	assert module.classify("src/code/jpeg-6/jcapimin.c") == "walked-closed"
	assert module.classify("src/code/splines/util_str.cpp") == "walked-closed"
	assert module.classify("src/game/g_config.c") == "walked-closed"
	assert module.classify("src/lcc/src/alloc.c") == "walked-closed"
	assert module.classify("src/libs/cmdlib/cmdlib.cpp") == "walked-closed"
	assert module.classify("src/q3asm/q3asm.c") == "walked-closed"
	assert module.classify("src/q3map/light.c") == "walked-closed"
	assert module.classify("src/q3radiant/MainFrm.cpp") == "walked-closed"
	assert module.ledger_state("src/code/jpeg-6/jcapimin.c") == (
		"Current secondary function walk complete; no new file-level gap isolated"
	)
	assert module.ledger_evidence("src/code/jpeg-6/jcapimin.c") == (
		"[source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk"
	)
	assert module.ledger_state("src/q3asm/q3asm.c") == (
		"Current secondary function walk complete; no new file-level gap isolated"
	)
	assert module.ledger_state("src/lcc/src/alloc.c") == (
		"Current secondary function walk complete; no new file-level gap isolated"
	)
	assert module.ledger_state("src/libs/cmdlib/cmdlib.cpp") == (
		"Current secondary function walk complete; no new file-level gap isolated"
	)
	assert module.ledger_state("src/q3radiant/MainFrm.cpp") == (
		"Current secondary function walk complete; no new file-level gap isolated"
	)


def test_write_plan_marks_completed_cgame_and_ui_tranches(tmp_path: Path) -> None:
	module = _load_generator_module()
	module.PLAN_PATH = tmp_path / "source-file-plan.md"

	primary_sections = OrderedDict((section, []) for section in module.PRIMARY_SECTIONS)
	primary_sections["src/common"] = ["a"] * 18
	primary_sections["src/code/qcommon"] = ["a"] * 19
	primary_sections["src/code/client"] = ["a"] * 22
	primary_sections["src/code/server"] = ["a"] * 11
	primary_sections["src/code/renderer"] = ["a"] * 23
	primary_sections["src/code/win32"] = ["a"] * 11
	primary_sections["src/code/botlib"] = ["a"] * 28
	primary_sections["src/code/game"] = ["a"] * 45
	primary_sections["src/code/cgame"] = ["a"] * 22
	primary_sections["src/code/ui"] = ["a"] * 9
	compatibility_sections = OrderedDict((section, []) for section in module.COMPATIBILITY_SECTIONS)
	secondary_sections = OrderedDict((section, []) for section in module.SECONDARY_SECTIONS)

	module.write_plan(primary_sections, compatibility_sections, secondary_sections, total_tracked=567)

	content = module.PLAN_PATH.read_text(encoding="utf-8")

	assert "- [x] Audit `src/code/cgame` function-by-function (`22` tracked files)." in content
	assert "focused cgame parity lane (`199 passed`, `1 skipped`)" in content
	assert "- [x] Audit `src/code/ui` function-by-function (`9` tracked files) (read-only source tree)." in content
	assert "focused UI" in content
	assert "parity lane (`56 passed`, `2 skipped`)" in content


def test_write_plan_marks_completed_unix_and_null_tranches(tmp_path: Path) -> None:
	module = _load_generator_module()
	module.PLAN_PATH = tmp_path / "source-file-plan.md"

	primary_sections = OrderedDict((section, []) for section in module.PRIMARY_SECTIONS)
	compatibility_sections = OrderedDict((section, []) for section in module.COMPATIBILITY_SECTIONS)
	compatibility_sections["src/code/unix"] = ["a"] * 10
	compatibility_sections["src/code/null"] = ["a"] * 7
	secondary_sections = OrderedDict((section, []) for section in module.SECONDARY_SECTIONS)

	module.write_plan(primary_sections, compatibility_sections, secondary_sections, total_tracked=567)

	content = module.PLAN_PATH.read_text(encoding="utf-8")

	assert (
		"- [x] Audit `src/code/unix` and convert tree-level `RW-G02` status into file-specific notes where warranted (`10` tracked files)."
	) in content
	assert "focused non-Windows" in content
	assert "portability lane (`8 passed`)" in content
	assert (
		"- [x] Audit `src/code/null` and convert tree-level `RW-G02` status into file-specific notes where warranted (`7` tracked files)."
	) in content
	assert "null compatibility walk isolated" in content
	assert "`null_glimp.c` as an additional `RW-G02` owner" in content


def test_write_plan_marks_completed_all_phase4_tranches(tmp_path: Path) -> None:
	module = _load_generator_module()
	module.PLAN_PATH = tmp_path / "source-file-plan.md"

	primary_sections = OrderedDict((section, []) for section in module.PRIMARY_SECTIONS)
	compatibility_sections = OrderedDict((section, []) for section in module.COMPATIBILITY_SECTIONS)
	secondary_sections = OrderedDict((section, []) for section in module.SECONDARY_SECTIONS)
	secondary_sections["src/code/bspc"] = ["a"] * 47
	secondary_sections["src/code/jpeg-6"] = ["a"] * 51
	secondary_sections["src/code/splines"] = ["a"] * 8
	secondary_sections["src/game"] = ["a"] * 10
	secondary_sections["src/q3asm"] = ["a"] * 2
	secondary_sections["src/q3map"] = ["a"] * 28
	secondary_sections["src/lcc"] = ["a"] * 74
	secondary_sections["src/libs"] = ["a"] * 25
	secondary_sections["src/q3radiant"] = ["a"] * 97

	module.write_plan(primary_sections, compatibility_sections, secondary_sections, total_tracked=567)

	content = module.PLAN_PATH.read_text(encoding="utf-8")

	assert (
		"- [x] Audit `src/code/bspc/`, `src/code/jpeg-6/`, and `src/code/splines/` after the primary runtime surface is complete (`106` tracked files)."
	) in content
	assert "no new file-level gap owners were isolated across the" in content
	assert "refreshed function-count pass now" in content
	assert (
		"- [x] Audit `src/game/`, `src/q3asm/`, and `src/q3map/` after the primary runtime surface is complete (`40` tracked files)."
	) in content
	assert "second secondary-source tranche" in content
	assert "retained gameplay fixture helpers" in content
	assert (
		"- [x] Audit `src/lcc/` and `src/libs/` after the primary runtime surface is complete (`99` tracked files)."
	) in content
	assert "third secondary-source tranche" in content
	assert "retained LCC compiler/preprocessor" in content
	assert (
		"- [x] Audit `src/q3radiant/` after the primary runtime surface is complete (`97` tracked files)."
	) in content
	assert "final secondary-source tranche" in content
	assert "retained Gtk/MFC-era Radiant editor" in content


def test_write_ledger_marks_completed_cgame_section(tmp_path: Path) -> None:
	module = _load_generator_module()
	module.LEDGER_PATH = tmp_path / "source-file-ledger.md"

	all_tracked = ["src/code/cgame/cg_draw.c"]
	function_counts = {"src/code/cgame/cg_draw.c": 140}
	status_counts: defaultdict[str, int] = defaultdict(int)
	status_counts["walked-closed"] = 1
	primary_sections = OrderedDict([("src/code/cgame", ["src/code/cgame/cg_draw.c"])])
	compatibility_sections = OrderedDict()
	secondary_sections = OrderedDict()

	module.write_ledger(
		all_tracked,
		function_counts,
		status_counts,
		primary_sections,
		compatibility_sections,
		secondary_sections,
	)

	content = module.LEDGER_PATH.read_text(encoding="utf-8")

	assert "Current 2026-04-22 audit result: the `src/code/cgame` function walk did" in content
	assert "focused cgame parity" in content
	assert "lane (`199 passed`, `1 skipped`)" in content
	assert (
		"| `src/code/cgame/cg_draw.c` | `140` | Current function walk complete; no file-level parity gap isolated | "
		"[module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |"
	) in content


def test_write_ledger_marks_completed_unix_section(tmp_path: Path) -> None:
	module = _load_generator_module()
	module.LEDGER_PATH = tmp_path / "source-file-ledger.md"

	all_tracked = ["src/code/unix/linux_common.c", "src/code/unix/unix_main.c"]
	function_counts = {
		"src/code/unix/linux_common.c": 6,
		"src/code/unix/unix_main.c": 59,
	}
	status_counts: defaultdict[str, int] = defaultdict(int)
	status_counts["walked-closed"] = 1
	status_counts["gap-note-open"] = 1
	primary_sections = OrderedDict()
	compatibility_sections = OrderedDict(
		[("src/code/unix", ["src/code/unix/linux_common.c", "src/code/unix/unix_main.c"])]
	)
	secondary_sections = OrderedDict()

	module.write_ledger(
		all_tracked,
		function_counts,
		status_counts,
		primary_sections,
		compatibility_sections,
		secondary_sections,
	)

	content = module.LEDGER_PATH.read_text(encoding="utf-8")

	assert "Current 2026-04-22 audit result: the `src/code/unix` function walk did" in content
	assert "focused non-Windows portability lane" in content
	assert (
		"| `src/code/unix/linux_common.c` | `6` | Current compatibility function walk complete; no new file-level portability gap isolated | "
		"[repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + current 2026-04-22 source walk | - |"
	) in content
	assert (
		"| `src/code/unix/unix_main.c` | `59` | RW-G02 file-level note open | "
		"[repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g02-unix-main.md) | "
		"[note](source-file-gap-notes/rw-g02-unix-main.md) |"
	) in content


def test_write_ledger_separates_documented_divergences_from_active_gap_notes(tmp_path: Path) -> None:
	module = _load_generator_module()
	module.LEDGER_PATH = tmp_path / "source-file-ledger.md"

	all_tracked = ["src/code/client/ql_auth.c", "src/code/unix/unix_main.c"]
	function_counts = {
		"src/code/client/ql_auth.c": 16,
		"src/code/unix/unix_main.c": 59,
	}
	status_counts: defaultdict[str, int] = defaultdict(int)
	status_counts["documented-divergence"] = 1
	status_counts["gap-note-open"] = 1
	primary_sections = OrderedDict([("src/code/client", ["src/code/client/ql_auth.c"])])
	compatibility_sections = OrderedDict([("src/code/unix", ["src/code/unix/unix_main.c"])])
	secondary_sections = OrderedDict()

	module.write_ledger(
		all_tracked,
		function_counts,
		status_counts,
		primary_sections,
		compatibility_sections,
		secondary_sections,
	)

	content = module.LEDGER_PATH.read_text(encoding="utf-8")

	assert "## Documented divergence notes" in content
	assert "| `src/code/client/ql_auth.c` | `RW-G01` | [note](source-file-gap-notes/rw-g01-client-auth.md) |" in content
	assert "## Active file-level gap notes" in content
	assert "| `src/code/unix/unix_main.c` | `RW-G02` | [note](source-file-gap-notes/rw-g02-unix-main.md) |" in content
	assert (
		"| `src/code/client/ql_auth.c` | `16` | RW-G01 documented divergence note | "
		"[repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g01-client-auth.md) | "
		"[note](source-file-gap-notes/rw-g01-client-auth.md) |"
	) in content


def test_write_ledger_marks_completed_null_section(tmp_path: Path) -> None:
	module = _load_generator_module()
	module.LEDGER_PATH = tmp_path / "source-file-ledger.md"

	all_tracked = ["src/code/null/null_net.c", "src/code/null/null_glimp.c"]
	function_counts = {
		"src/code/null/null_net.c": 5,
		"src/code/null/null_glimp.c": 7,
	}
	status_counts: defaultdict[str, int] = defaultdict(int)
	status_counts["walked-closed"] = 1
	status_counts["gap-note-open"] = 1
	primary_sections = OrderedDict()
	compatibility_sections = OrderedDict(
		[("src/code/null", ["src/code/null/null_glimp.c", "src/code/null/null_net.c"])]
	)
	secondary_sections = OrderedDict()

	module.write_ledger(
		all_tracked,
		function_counts,
		status_counts,
		primary_sections,
		compatibility_sections,
		secondary_sections,
	)

	content = module.LEDGER_PATH.read_text(encoding="utf-8")

	assert "Current 2026-04-22 audit result: the `src/code/null` function walk" in content
	assert "isolated `null_glimp.c` as an additional `RW-G02` owner" in content
	assert (
		"| `src/code/null/null_net.c` | `5` | Current compatibility function walk complete; no new file-level portability gap isolated | "
		"[repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + current 2026-04-22 source walk | - |"
	) in content
	assert (
		"| `src/code/null/null_glimp.c` | `7` | RW-G02 file-level note open | "
		"[repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g02-null-glimp.md) | "
		"[note](source-file-gap-notes/rw-g02-null-glimp.md) |"
	) in content


def test_write_ledger_marks_completed_first_phase4_sections(tmp_path: Path) -> None:
	module = _load_generator_module()
	module.LEDGER_PATH = tmp_path / "source-file-ledger.md"

	all_tracked = [
		"src/code/bspc/bspc.c",
		"src/code/jpeg-6/jcapimin.c",
		"src/code/splines/util_str.cpp",
	]
	function_counts = {
		"src/code/bspc/bspc.c": 9,
		"src/code/jpeg-6/jcapimin.c": 7,
		"src/code/splines/util_str.cpp": 15,
	}
	status_counts: defaultdict[str, int] = defaultdict(int)
	status_counts["walked-closed"] = 3
	primary_sections = OrderedDict()
	compatibility_sections = OrderedDict()
	secondary_sections = OrderedDict(
		[
			("src/code/bspc", ["src/code/bspc/bspc.c"]),
			("src/code/jpeg-6", ["src/code/jpeg-6/jcapimin.c"]),
			("src/code/splines", ["src/code/splines/util_str.cpp"]),
		]
	)

	module.write_ledger(
		all_tracked,
		function_counts,
		status_counts,
		primary_sections,
		compatibility_sections,
		secondary_sections,
	)

	content = module.LEDGER_PATH.read_text(encoding="utf-8")

	assert "Current 2026-04-22 audit result: the `src/code/bspc` function walk did" in content
	assert "Current 2026-04-22 audit result: the `src/code/jpeg-6` function walk" in content
	assert "Current 2026-04-22 audit result: the `src/code/splines` function walk" in content
	assert (
		"| `src/code/jpeg-6/jcapimin.c` | `7` | Current secondary function walk complete; no new file-level gap isolated | "
		"[source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |"
	) in content
	assert (
		"| `src/code/splines/util_str.cpp` | `15` | Current secondary function walk complete; no new file-level gap isolated | "
		"[source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |"
	) in content


def test_write_ledger_marks_completed_second_phase4_sections(tmp_path: Path) -> None:
	module = _load_generator_module()
	module.LEDGER_PATH = tmp_path / "source-file-ledger.md"

	all_tracked = [
		"src/game/g_config.c",
		"src/q3asm/q3asm.c",
		"src/q3map/light.c",
	]
	function_counts = {
		"src/game/g_config.c": 30,
		"src/q3asm/q3asm.c": 18,
		"src/q3map/light.c": 27,
	}
	status_counts: defaultdict[str, int] = defaultdict(int)
	status_counts["walked-closed"] = 3
	primary_sections = OrderedDict()
	compatibility_sections = OrderedDict()
	secondary_sections = OrderedDict(
		[
			("src/game", ["src/game/g_config.c"]),
			("src/q3asm", ["src/q3asm/q3asm.c"]),
			("src/q3map", ["src/q3map/light.c"]),
		]
	)

	module.write_ledger(
		all_tracked,
		function_counts,
		status_counts,
		primary_sections,
		compatibility_sections,
		secondary_sections,
	)

	content = module.LEDGER_PATH.read_text(encoding="utf-8")

	assert "Current 2026-04-22 audit result: the `src/game` function walk did not" in content
	assert "Current 2026-04-22 audit result: the `src/q3asm` function walk did not" in content
	assert "Current 2026-04-22 audit result: the `src/q3map` function walk did not" in content
	assert (
		"| `src/game/g_config.c` | `30` | Current secondary function walk complete; no new file-level gap isolated | "
		"[source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |"
	) in content
	assert (
		"| `src/q3asm/q3asm.c` | `18` | Current secondary function walk complete; no new file-level gap isolated | "
		"[source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |"
	) in content
	assert (
		"| `src/q3map/light.c` | `27` | Current secondary function walk complete; no new file-level gap isolated | "
		"[source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |"
	) in content


def test_write_ledger_marks_completed_third_phase4_sections(tmp_path: Path) -> None:
	module = _load_generator_module()
	module.LEDGER_PATH = tmp_path / "source-file-ledger.md"

	all_tracked = [
		"src/lcc/src/alloc.c",
		"src/libs/cmdlib/cmdlib.cpp",
	]
	function_counts = {
		"src/lcc/src/alloc.c": 6,
		"src/libs/cmdlib/cmdlib.cpp": 41,
	}
	status_counts: defaultdict[str, int] = defaultdict(int)
	status_counts["walked-closed"] = 2
	primary_sections = OrderedDict()
	compatibility_sections = OrderedDict()
	secondary_sections = OrderedDict(
		[
			("src/lcc", ["src/lcc/src/alloc.c"]),
			("src/libs", ["src/libs/cmdlib/cmdlib.cpp"]),
		]
	)

	module.write_ledger(
		all_tracked,
		function_counts,
		status_counts,
		primary_sections,
		compatibility_sections,
		secondary_sections,
	)

	content = module.LEDGER_PATH.read_text(encoding="utf-8")

	assert "Current 2026-04-22 audit result: the `src/lcc` function walk did not" in content
	assert "Current 2026-04-22 audit result: the tracked `src/libs` function walk" in content
	assert (
		"| `src/lcc/src/alloc.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | "
		"[source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |"
	) in content
	assert (
		"| `src/libs/cmdlib/cmdlib.cpp` | `41` | Current secondary function walk complete; no new file-level gap isolated | "
		"[source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |"
	) in content


def test_write_ledger_marks_completed_final_phase4_section(tmp_path: Path) -> None:
	module = _load_generator_module()
	module.LEDGER_PATH = tmp_path / "source-file-ledger.md"

	all_tracked = ["src/q3radiant/MainFrm.cpp"]
	function_counts = {"src/q3radiant/MainFrm.cpp": 348}
	status_counts: defaultdict[str, int] = defaultdict(int)
	status_counts["walked-closed"] = 1
	primary_sections = OrderedDict()
	compatibility_sections = OrderedDict()
	secondary_sections = OrderedDict([("src/q3radiant", ["src/q3radiant/MainFrm.cpp"])])

	module.write_ledger(
		all_tracked,
		function_counts,
		status_counts,
		primary_sections,
		compatibility_sections,
		secondary_sections,
	)

	content = module.LEDGER_PATH.read_text(encoding="utf-8")

	assert "Current 2026-04-22 audit result: the `src/q3radiant` function walk did" in content
	assert "retained Radiant editor" in content
	assert (
		"| `src/q3radiant/MainFrm.cpp` | `348` | Current secondary function walk complete; no new file-level gap isolated | "
		"[source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |"
	) in content
