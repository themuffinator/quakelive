from __future__ import annotations

import importlib.util
from collections import OrderedDict, defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATOR_PATH = REPO_ROOT / "tools" / "reverse-engineering" / "generate_source_file_audit.py"
BOTLIB_AAS_MAIN = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_main.c"


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


def test_completed_cgame_surface_classifies_as_walked_closed() -> None:
	module = _load_generator_module()

	assert module.classify("src/code/cgame/cg_draw.c") == "walked-closed"
	assert module.ledger_state("src/code/cgame/cg_draw.c") == "Current function walk complete; no file-level parity gap isolated"
	assert module.ledger_evidence("src/code/cgame/cg_draw.c") == (
		"[module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk"
	)
	assert module.classify("src/code/client/ql_auth.c") == "gap-note-open"


def test_write_plan_marks_cgame_completed_and_ui_pending(tmp_path: Path) -> None:
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
	assert "- [ ] Audit `src/code/ui` function-by-function (`9` tracked files) (read-only source tree)." in content


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
