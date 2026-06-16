from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_MOVER = REPO_ROOT / "src" / "code" / "game" / "g_mover.c"
GAME_SPAWN = REPO_ROOT / "src" / "code" / "game" / "g_spawn.c"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
QAGAME_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "qagame.json"
QAGAME_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "functions.csv"
)
QAGAME_HLIL_PART02 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part02.txt"
)


MOVER_STATIC_MOTION_FUNCTIONS = (
	{
		"address": "0x10060AA0",
		"aliases": ("FUN_10060aa0", "sub_10060aa0"),
		"normalized": "SP_func_static",
		"signature": "void SP_func_static(gentity_t *ent)",
		"ghidra": None,
	},
	{
		"address": "0x10060B00",
		"aliases": ("FUN_10060b00", "sub_10060b00"),
		"normalized": "SP_func_rotating",
		"signature": "void SP_func_rotating(gentity_t *ent)",
		"ghidra": ("10060b00", "FUN_10060b00", 255),
	},
	{
		"address": "0x10060C00",
		"aliases": ("FUN_10060c00", "sub_10060c00"),
		"normalized": "SP_func_bobbing",
		"signature": "void SP_func_bobbing(gentity_t *ent)",
		"ghidra": None,
	},
	{
		"address": "0x10060D50",
		"aliases": ("FUN_10060d50", "sub_10060d50"),
		"normalized": "SP_func_pendulum",
		"signature": "void SP_func_pendulum(gentity_t *ent)",
		"ghidra": ("10060d50", "FUN_10060d50", 377),
	},
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _extract_function_block(text: str, signature: str) -> str:
	scan_text = "\n".join(line.split("//", 1)[0] for line in text.splitlines())
	start = scan_text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = scan_text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(scan_text)):
		char = scan_text[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return scan_text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def _function_rows_by_entry(path: Path) -> dict[str, dict[str, str]]:
	with path.open(newline="", encoding="utf-8") as file:
		return {row["entry"].lower(): row for row in csv.DictReader(file)}


def test_qagame_mover_static_motion_aliases_metadata_and_hlil_are_pinned() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	hlil = _read(QAGAME_HLIL_PART02)

	for function in MOVER_STATIC_MOTION_FUNCTIONS:
		for raw_name in function["aliases"]:
			assert aliases[raw_name] == function["normalized"]

		symbol = symbol_map[function["address"].lower()]
		assert symbol["normalized_name"] == function["normalized"]
		assert symbol["signature"] == function["signature"]
		assert symbol["status"] == "matched"

		if function["ghidra"]:
			entry, raw_name, size = function["ghidra"]
			row = function_rows[entry]
			assert row["name"] == raw_name
			assert int(row["size"]) == size
			assert row["thunk"] == "0"

	for expected in (
		"10060aa0    int32_t sub_10060aa0(void* arg1)",
		"10060ab6  (*(data_104b13ac + 0x7c))(arg1, *(arg1 + 0x254))",
		"10060abb  int32_t result = sub_1005ee80(arg1, x87_r0)",
		"10060acf  *(arg1 + 0x18) = xmm0",
		"10060ade  *(arg1 + 0x220) = xmm0",
		"10060af7  return result",
		"10060b00    int32_t sub_10060b00(void* arg1)",
		"10060b23      *(esi + 0x2e4) = 0x42c80000",
		"10060b37  *(esi + 0x34) = 2",
		"10060b42      *(esi + 0x54) = fconvert.s(x87_r7)",
		"10060b4b      *(esi + 0x4c) = fconvert.s(x87_r7)",
		"10060b50      *(esi + 0x50) = fconvert.s(x87_r7)",
		"10060b62  sub_10065c00(&data_10088260, &data_1007d53c, &arg1)",
		"10060bbf  *(esi + 0x304) = sub_1005f140",
		"10060bfe  return (*(edx_1 + 0x9c))(esi)",
		"10060c00    char sub_10060c00(long double arg1 @ st0, long double arg2 @ st2)",
		"10060c14  sub_10065c00(\"speed\", &data_10086a90, &var_8)",
		"10060c3d  sub_10065c00(\"height\", &data_100883c4, &arg_4)",
		"10060c60  sub_10065c00(&data_10088260, &data_1007d53c, &var_8)",
		"10060c85  sub_10065c00(\"phase\", &data_1007d0a8, &var_8)",
		"10060d02  *(esi i+ 0x14) = eax_3",
		"10060d14  *(esi i+ 0x10) = eax_4",
		"10060d1d  *(esi i+ 0xc) = 4",
		"10060d29      *(esi i+ 0x24) = xmm0_1",
		"10060d38  *(esi i+ 0x28) = xmm0_1",
		"10060d43      *(esi i+ 0x2c) = xmm0_1",
		"10060d50    int32_t sub_10060d50(long double arg1 @ st0, long double arg2 @ st1, void* arg3)",
		"10060d6a  sub_10065c00(\"speed\", &data_1008732c, &var_14)",
		"10060d90  sub_10065c00(&data_10088260, &data_1007d53c, &var_14)",
		"10060dbb  sub_10065c00(\"phase\", &data_1007d0a8, &var_14)",
		"10060df0  var_14 = fconvert.s(fabs(fconvert.t(*(arg3 + 0x1f4))))",
		"10060e02  if (not(fconvert.t(8f) <= x87_r1_2))",
		"10060e22  long double x87_r1_4 = fconvert.t(data_104b36a8) / (fconvert.t(var_14) * fconvert.t(3.0))",
		"10060e2f  var_14 = fconvert.s(x87_r1_4 * fconvert.t(0.15915493667125702))",
		"10060e3d  int32_t eax_3 = sub_1007b550(fconvert.t(1000.0) / fconvert.t(var_14))",
		"10060eb8  *(arg3 + 0x34) = 4",
		"10060ebf  *(arg3 + 0x54) = var_c",
		"100805a8  char const (* data_100805a8)[0xc] = data_10089744 {\"func_static\"}",
		"100805ac  void* data_100805ac = sub_10060aa0",
		"100805b0  char const (* data_100805b0)[0xe] = data_10088114 {\"func_rotating\"}",
		"100805b4  void* data_100805b4 = sub_10060b00",
		"100805b8  char const (* data_100805b8)[0xd] = data_10089734 {\"func_bobbing\"}",
		"100805bc  void* data_100805bc = sub_10060c00",
		"100805c0  char const (* data_100805c0)[0xe] = data_10089724 {\"func_pendulum\"}",
		"100805c4  void* data_100805c4 = sub_10060d50",
	):
		assert expected in hlil


def test_qagame_static_rotating_bobbing_and_pendulum_source_paths_match_retail() -> None:
	g_mover = _read(GAME_MOVER)
	static_body = _extract_function_block(g_mover, "void SP_func_static( gentity_t *ent )")
	rotating_body = _extract_function_block(g_mover, "void SP_func_rotating (gentity_t *ent)")
	bobbing_body = _extract_function_block(g_mover, "void SP_func_bobbing (gentity_t *ent)")
	pendulum_body = _extract_function_block(g_mover, "void SP_func_pendulum(gentity_t *ent)")

	for expected in (
		"trap_SetBrushModel( ent, ent->model );",
		"InitMover( ent );",
		"VectorCopy( ent->s.origin, ent->s.pos.trBase );",
		"VectorCopy( ent->s.origin, ent->r.currentOrigin );",
	):
		assert expected in static_body

	for expected in (
		"if ( !ent->speed )",
		"ent->speed = 100;",
		"ent->s.apos.trType = TR_LINEAR;",
		"if ( ent->spawnflags & 4 )",
		"ent->s.apos.trDelta[2] = ent->speed;",
		"else if ( ent->spawnflags & 8 )",
		"ent->s.apos.trDelta[0] = ent->speed;",
		"ent->s.apos.trDelta[1] = ent->speed;",
		"ent->damage = 2;",
		"trap_SetBrushModel( ent, ent->model );",
		"InitMover( ent );",
		"VectorCopy( ent->s.origin, ent->s.pos.trBase );",
		"VectorCopy( ent->s.pos.trBase, ent->r.currentOrigin );",
		"VectorCopy( ent->s.apos.trBase, ent->r.currentAngles );",
		"trap_LinkEntity( ent );",
	):
		assert expected in rotating_body

	for expected in (
		'G_SpawnFloat( "speed", "4", &ent->speed );',
		'G_SpawnFloat( "height", "32", &height );',
		'G_SpawnInt( "dmg", "2", &ent->damage );',
		'G_SpawnFloat( "phase", "0", &phase );',
		"trap_SetBrushModel( ent, ent->model );",
		"InitMover( ent );",
		"VectorCopy( ent->s.origin, ent->s.pos.trBase );",
		"VectorCopy( ent->s.origin, ent->r.currentOrigin );",
		"ent->s.pos.trDuration = ent->speed * 1000;",
		"ent->s.pos.trTime = ent->s.pos.trDuration * phase;",
		"ent->s.pos.trType = TR_SINE;",
		"if ( ent->spawnflags & 1 )",
		"ent->s.pos.trDelta[0] = height;",
		"else if ( ent->spawnflags & 2 )",
		"ent->s.pos.trDelta[1] = height;",
		"ent->s.pos.trDelta[2] = height;",
	):
		assert expected in bobbing_body

	for expected in (
		'G_SpawnFloat( "speed", "30", &speed );',
		'G_SpawnInt( "dmg", "2", &ent->damage );',
		'G_SpawnFloat( "phase", "0", &phase );',
		"trap_SetBrushModel( ent, ent->model );",
		"length = fabs( ent->r.mins[2] );",
		"if ( length < 8 )",
		"length = 8;",
		"freq = 1 / ( M_PI * 2 ) * sqrt( g_gravity.value / ( 3 * length ) );",
		"ent->s.pos.trDuration = ( 1000 / freq );",
		"InitMover( ent );",
		"VectorCopy( ent->s.origin, ent->s.pos.trBase );",
		"VectorCopy( ent->s.origin, ent->r.currentOrigin );",
		"VectorCopy( ent->s.angles, ent->s.apos.trBase );",
		"ent->s.apos.trDuration = 1000 / freq;",
		"ent->s.apos.trTime = ent->s.apos.trDuration * phase;",
		"ent->s.apos.trType = TR_SINE;",
		"ent->s.apos.trDelta[2] = speed;",
	):
		assert expected in pendulum_body


def test_qagame_static_motion_spawn_order_matches_retail() -> None:
	g_spawn = _read(GAME_SPAWN)
	expected_spawn_order = [
		'{"func_plat", SP_func_plat}',
		'{"func_button", SP_func_button}',
		'{"func_door", SP_func_door}',
		'{"func_static", SP_func_static}',
		'{"func_rotating", SP_func_rotating}',
		'{"func_bobbing", SP_func_bobbing}',
		'{"func_pendulum", SP_func_pendulum}',
		'{"func_train", SP_func_train}',
		'{"func_group", SP_info_null}',
	]
	positions = [g_spawn.index(entry) for entry in expected_spawn_order]
	assert positions == sorted(positions)
