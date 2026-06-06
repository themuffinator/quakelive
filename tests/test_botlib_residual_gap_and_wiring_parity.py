import csv
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
FUNCTIONS_CSV = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
)
QL_STEAM_HLIL_PART03 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part03.txt"
)
BOTLIB_AAS_MOVE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_move.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_H = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
G_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
G_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
SV_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
QL_GAME_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"

BOTLIB_NEIGHBORHOOD_START = 0x00482000
BOTLIB_NEIGHBORHOOD_END = 0x004A8400

JPEG_MEMORY_MANAGER_RESIDUAL_GAPS = (
	0x00482150,
	0x004821F0,
	0x00482290,
	0x004823E0,
	0x00482530,
	0x00482640,
	0x00482780,
	0x004828A0,
	0x004828C0,
	0x004828E0,
	0x004828F0,
	0x00482910,
	0x00482930,
	0x00482950,
	0x004829A0,
)
FOLDED_WEAPON_JUMP_THUNK = 0x00486F40
EXPECTED_RESIDUAL_GAPS = (*JPEG_MEMORY_MANAGER_RESIDUAL_GAPS, FOLDED_WEAPON_JUMP_THUNK)

DIRECT_NATIVE_BOTLIB_IMPORTS = {
	"G_QL_IMPORT_BOTLIB_AI_DRAW_DEBUG_AREAS",
	"G_QL_IMPORT_BOTLIB_AI_DRAW_AVOID_SPOTS",
	"G_QL_IMPORT_BOTLIB_EA_WALK",
}


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _aliases() -> dict[str, str]:
	return json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]


def _alias_key(address: int) -> str:
	return f"sub_{address:06X}"


def _function_rows_in_neighborhood() -> dict[int, str]:
	rows: dict[int, str] = {}
	with FUNCTIONS_CSV.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			address = int(row["entry"], 16)
			if BOTLIB_NEIGHBORHOOD_START <= address <= BOTLIB_NEIGHBORHOOD_END:
				rows[address] = row["name"]
	return rows


def _residual_unaliased_addresses() -> list[int]:
	aliases = _aliases()
	aliased_addresses = {
		int(alias[4:], 16)
		for alias in aliases
		if alias.startswith("sub_")
	}
	rows = _function_rows_in_neighborhood()
	return [
		address
		for address in sorted(rows)
		if address not in aliased_addresses
	]


def _assert_in_order(source: str, needles: list[str]) -> None:
	positions = [source.index(needle) for needle in needles]
	assert positions == sorted(positions)


def test_botlib_neighborhood_has_only_documented_residual_gaps() -> None:
	aliases = _aliases()
	rows = _function_rows_in_neighborhood()
	residual = _residual_unaliased_addresses()

	assert len(rows) == 417
	assert sum(1 for address in rows if _alias_key(address) in aliases) == 401
	assert sum(
		1
		for alias in aliases
		if alias.startswith("sub_")
		and BOTLIB_NEIGHBORHOOD_START <= int(alias[4:], 16) <= BOTLIB_NEIGHBORHOOD_END
	) == 407
	assert residual == list(EXPECTED_RESIDUAL_GAPS)

	assert aliases["sub_4829C0"] == "AAS_Trace"
	assert aliases["sub_4A83C0"] == "GetBotLibAPI"
	assert min(JPEG_MEMORY_MANAGER_RESIDUAL_GAPS) > 0x00482100
	assert max(JPEG_MEMORY_MANAGER_RESIDUAL_GAPS) < 0x004829C0
	assert FOLDED_WEAPON_JUMP_THUNK in residual

	for address in EXPECTED_RESIDUAL_GAPS:
		assert _alias_key(address) not in aliases


def test_residual_jpeg_memory_manager_block_is_not_botlib() -> None:
	aliases = _aliases()
	hlil = _read(QL_STEAM_HLIL_PART03)

	assert aliases["sub_480290"] == "jinit_marker_reader"
	assert aliases["sub_4811C0"] == "jpeg_fdct_float"
	assert aliases["sub_4814A0"] == "jpeg_idct_float"
	assert aliases["sub_4829C0"] == "AAS_Trace"

	for address in JPEG_MEMORY_MANAGER_RESIDUAL_GAPS:
		assert _alias_key(address) not in aliases

	for anchor in (
		"004827c7  *eax = sub_481b50",
		"004827f7  eax[7] = sub_482290",
		"004827fe  eax[8] = sub_4823e0",
		"00482805  eax[9] = sub_482530",
		"0048280c  eax[0xa] = sub_482640",
		'0048283a  int32_t eax_3 = getenv("JPEGMEM")',
		"00482980      result = memcpy(ecx_1, eax_1, arg6)",
		"004829b6  return memset(arg1, 0, arg2)",
		"004829c0    int32_t sub_4829c0(",
	):
		assert anchor in hlil


def test_folded_weapon_jump_thunk_remains_deliberate_non_alias() -> None:
	aliases = _aliases()
	aas_move = _read(BOTLIB_AAS_MOVE)
	hlil = _read(QL_STEAM_HLIL_PART03)

	assert "sub_486F40" not in aliases
	assert aliases["sub_486D40"] == "AAS_WeaponJumpZVelocity"
	assert aliases["sub_486F60"] == "AAS_Accelerate"
	assert aas_move.count("return AAS_WeaponJumpZVelocity(origin, 120);") == 2
	assert "float AAS_RocketJumpZVelocity(vec3_t origin)" in aas_move
	assert "float AAS_BFGJumpZVelocity(vec3_t origin)" in aas_move
	assert "00486f40    int80_t sub_486f40(float* arg1)" in hlil
	assert "00486f5a  return sub_486d40(arg1, fconvert.s(fconvert.t(120f)))" in hlil


def test_botlib_native_import_bridge_has_complete_static_wiring() -> None:
	g_public = _read(G_PUBLIC)
	g_syscalls = _read(G_SYSCALLS)
	sv_game = _read(SV_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)
	be_interface = _read(BOTLIB_INTERFACE)
	botlib_h = _read(BOTLIB_H)
	aliases = _aliases()

	public_slots = set(re.findall(r"\b(G_QL_IMPORT_BOTLIB_[A-Z0-9_]+)\b", g_public))
	mapped_pairs = re.findall(
		r"case\s+(BOTLIB_[A-Z0-9_]+)\s*:\s*return\s+(G_QL_IMPORT_BOTLIB_[A-Z0-9_]+)\s*;",
		g_syscalls,
	)
	mapped_slots = {slot for _, slot in mapped_pairs}
	registered_pairs = re.findall(
		r"ql_game_imports\[(G_QL_IMPORT_BOTLIB_[A-Z0-9_]+)\]\s*=\s*"
		r"\(ql_import_f\)(QL_G_trap_[A-Za-z0-9_]+);",
		sv_game,
	)
	registered_slots = {slot for slot, _ in registered_pairs}

	assert len(public_slots) == 136
	assert len(mapped_pairs) == 133
	assert len(registered_pairs) == 136
	assert len(registered_slots) == 136
	assert public_slots == registered_slots
	assert mapped_slots == public_slots - DIRECT_NATIVE_BOTLIB_IMPORTS
	assert registered_slots - mapped_slots == DIRECT_NATIVE_BOTLIB_IMPORTS

	for _, wrapper in registered_pairs:
		assert wrapper in ql_game_imports or wrapper in sv_game

	assert "G_GetDirectImport( G_QL_IMPORT_BOTLIB_AI_DRAW_DEBUG_AREAS )" in g_syscalls
	assert "G_GetDirectImport( G_QL_IMPORT_BOTLIB_AI_DRAW_AVOID_SPOTS )" in g_syscalls
	assert "trap_EA_Walk" not in g_syscalls
	assert "static void QDECL QL_G_trap_EA_Walk( int client )" in ql_game_imports

	assert "#define\tBOTLIB_API_VERSION\t\t2" in botlib_h
	assert aliases["sub_4A7FC0"] == "Init_AAS_Export"
	assert aliases["sub_4A8060"] == "Init_EA_Export"
	assert aliases["sub_4A8110"] == "Init_AI_Export"
	assert aliases["sub_4A83C0"] == "GetBotLibAPI"
	_assert_in_order(
		be_interface,
		[
			"if ( apiVersion != BOTLIB_API_VERSION )",
			"Init_AAS_Export(&be_botlib_export.aas);",
			"Init_EA_Export(&be_botlib_export.ea);",
			"Init_AI_Export(&be_botlib_export.ai);",
			"be_botlib_export.BotLibSetup = Export_BotLibSetup;",
			"be_botlib_export.BotLibShutdown = Export_BotLibShutdown;",
			"be_botlib_export.BotLibVarSet = Export_BotLibVarSet;",
			"be_botlib_export.BotLibVarGet = Export_BotLibVarGet;",
			"be_botlib_export.BotLibStartFrame = Export_BotLibStartFrame;",
			"be_botlib_export.BotLibLoadMap = Export_BotLibLoadMap;",
			"be_botlib_export.BotLibUpdateEntity = Export_BotLibUpdateEntity;",
			"be_botlib_export.Test = BotExportTest;",
			"return &be_botlib_export;",
		],
	)
