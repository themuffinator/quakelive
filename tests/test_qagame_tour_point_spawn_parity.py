from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_MISC = REPO_ROOT / "src" / "code" / "game" / "g_misc.c"
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


def test_qagame_tour_point_aliases_metadata_and_hlil_are_pinned() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))["qagamex86"]
	symbol_map = {
		entry["address"].lower(): entry
		for entry in json.loads(_read(QAGAME_SYMBOL_MAP))["functions"]
	}
	function_rows = _function_rows_by_entry(QAGAME_FUNCTIONS)
	hlil = _read(QAGAME_HLIL_PART02)

	for raw_name in ("FUN_10059fd0", "sub_10059fd0"):
		assert aliases[raw_name] == "FinishSpawningTourPoint"
	assert aliases["sub_1005a1f0"] == "SP_info_tour_point"

	finisher_row = function_rows["10059fd0"]
	assert finisher_row["name"] == "FUN_10059fd0"
	assert int(finisher_row["size"]) == 541
	assert finisher_row["thunk"] == "0"

	finisher_symbol = symbol_map["0x10059fd0"]
	assert finisher_symbol["raw_name"] == "FUN_10059fd0"
	assert finisher_symbol["normalized_name"] == "FinishSpawningTourPoint"
	assert finisher_symbol["signature"] == "void FinishSpawningTourPoint(gentity_t *ent)"
	assert "Source-backed deferred `info_tour_point` finisher" in finisher_symbol["comment"]

	spawn_symbol = symbol_map["0x1005a1f0"]
	assert spawn_symbol["raw_name"] == "sub_1005a1f0"
	assert spawn_symbol["normalized_name"] == "SP_info_tour_point"
	assert spawn_symbol["signature"] == "void SP_info_tour_point(gentity_t *ent)"
	assert "Source-backed QL-only G_CallSpawn dispatch-table constructor" in spawn_symbol["comment"]
	assert "0x10087F74" in spawn_symbol["string_refs"]
	assert "0x10087FA4" in spawn_symbol["string_refs"]

	for expected in (
		"10059fd0    void* sub_10059fd0(void* arg1)",
		"1005a09c      int32_t eax_3 = ecx_1(&var_20, &var_2c, &var_14, 0x400)",
		"1005a0cf                  if (ecx_2 != 8 && ecx_2 != 7)",
		"1005a0d1                      *(eax_6 + 0x1e0) |= 1",
		"1005a0d8                      *(eax_6 + 8) |= 0x80",
		"1005a0df                      *(eax_6 + 0x204) = 0",
		"1005a10d      i_1, ecx_4, edx = sub_1006bfa0(nullptr, edx_2, 0x2d4, edx_2)",
		"1005a17b      result = sub_1006bfa0(nullptr, edx, 0x2c0, result)",
		"1005a1d0          result = sub_10053140(\"info_tour_point with no tourPoin…\")",
		"1005a1f0    int32_t __convention(\"regparm\") sub_1005a1f0",
		"1005a25c  if (*(arg7 + 0x2c0) == 0 && (*(arg7 + 0x248) & 1) == 0)",
		"1005a28e  sub_10065c00(\"radius\", &data_10085968, &var_4)",
		"1005a2b3  sub_10065c00(\"cvarValue\", \"-1.0f\", &var_4)",
		"1005a2d8  sub_10065c00(\"printChatTextTime\", \"2.0f\", &var_4)",
		"1005a2fd  sub_10065c00(\"ignorePlayerLocation\", &data_1007d0a8, &var_4)",
		"1005a322  sub_10065c00(\"noise\", &data_1007c414, &var_4)",
		"1005a3ff  *(arg7 + 0x2f8) = sub_10059fd0",
		"10080714  void* data_10080714 = sub_1005a1f0",
	):
		assert expected in hlil


def test_qagame_tour_point_source_spawn_and_finish_paths_match_retail() -> None:
	g_misc = _read(GAME_MISC)
	hide_body = _extract_function_block(g_misc, "static void G_HideTourPointLinkedEntity( gentity_t *ent )")
	finish_body = _extract_function_block(g_misc, "static void FinishSpawningTourPoint( gentity_t *ent )")
	spawn_body = _extract_function_block(g_misc, "void SP_info_tour_point( gentity_t *ent )")
	g_spawn = _read(GAME_SPAWN)

	for expected in (
		"ent->r.svFlags |= SVF_NOCLIENT;",
		"ent->s.eFlags |= EF_NODRAW;",
		"ent->r.contents = 0;",
		"trap_LinkEntity( ent );",
	):
		assert expected in hide_body

	for expected in (
		"if ( ent->spawnflags & 0x80 )",
		"VectorAdd( ent->r.currentOrigin, ent->r.mins, mins );",
		"VectorAdd( ent->r.currentOrigin, ent->r.maxs, maxs );",
		"num = trap_EntitiesInBox( mins, maxs, touch, MAX_GENTITIES );",
		"if ( other->s.eType != ET_ITEM )",
		"other->item->giType == IT_PERSISTANT_POWERUP || other->item->giType == IT_TEAM",
		"G_HideTourPointLinkedEntity( other );",
		"G_Find( match, FOFS( targetname ), ent->targetname )",
		"if ( match->target_ent )",
		"G_HideTourPointLinkedEntity( match );",
		"ent->target_ent = NULL;",
		"G_Find( NULL, FOFS( targetname ), ent->target )",
		'G_Printf( "info_tour_point with no tourPointTarget at %s!\\n", vtos( ent->s.origin ) );',
		"trap_LinkEntity( ent );",
	):
		assert expected in finish_body

	for expected in (
		'G_SpawnString( "tourPointTargetName", "", &value )',
		"if ( !( ent->spawnflags & 1 ) )",
		'G_Printf( "info_tour_point with no tourPointTargetName at %s\\n", vtos( ent->s.origin ) );',
		"G_FreeEntity( ent );",
		"ent->targetname = G_NewString( value );",
		'G_SpawnString( "tourPointTarget", "", &value )',
		"ent->target = G_NewString( value );",
		'G_SpawnFloat( "radius", "300", &ent->tourPointRadius );',
		'G_SpawnFloat( "cvarValue", "-1.0f", &ent->tourPointCvarValue );',
		'G_SpawnFloat( "printChatTextTime", "2.0f", &ent->tourPointPrintChatTextTime );',
		'G_SpawnInt( "ignorePlayerLocation", "0", &ignorePlayerLocation );',
		"ent->tourPointIgnorePlayerLocation = ignorePlayerLocation ? qtrue : qfalse;",
		'G_SpawnString( "noise", "", &value )',
		"ent->noise_index = G_SoundIndex( value );",
		"ent->s.eType = ET_GENERAL;",
		"G_SetOrigin( ent, ent->s.origin );",
		"VectorSet( ent->r.mins, -16, -16, -24 );",
		"VectorSet( ent->r.maxs, 16, 16, 32 );",
		"ent->nextthink = level.time + FRAMETIME;",
		"ent->think = FinishSpawningTourPoint;",
	):
		assert expected in spawn_body

	assert g_spawn.index('{"info_tour_point", SP_info_tour_point}') < g_spawn.index('{"func_plat", SP_func_plat}')
