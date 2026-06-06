from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _function_body(source: str, signature: str) -> str:
	match = re.search(
		rf"{re.escape(signature)}\s*\{{(?P<body>.*?)^\}}",
		source,
		re.MULTILINE | re.DOTALL,
	)

	assert match is not None, f"{signature} definition missing"
	return match.group("body")


def _case_block(source: str, start: str, end: str) -> str:
	start_index = source.index(start)
	end_index = source.index(end, start_index)
	return source[start_index:end_index]


def test_cgame_grapple_impact_media_matches_retail_evidence() -> None:
	cg_local_h = _read("src/code/cgame/cg_local.h")
	cg_main_c = _read("src/code/cgame/cg_main.c")
	cg_weapons_c = _read("src/code/cgame/cg_weapons.c")
	cgame_ghidra = _read("references/reverse-engineering/ghidra/cgamex86/decompile_top_functions.c")
	cgame_hlil = _read("references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt")
	cgame_symbols = _read("references/symbol-maps/cgame.json")

	impact_body = _function_body(
		cg_weapons_c,
		"void CG_MissileHitWall( int weapon, int clientNum, vec3_t origin, vec3_t dir, impactSound_t soundType )",
	)
	grapple_impact = _case_block(impact_body, "case WP_GRAPPLING_HOOK:", "case WP_HEAVY_MACHINEGUN:")

	assert "qhandle_t\tcrackedMarkShader;" in cg_local_h
	assert "sfxHandle_t\tsfx_grapplehit;" in cg_local_h
	assert 'cgs.media.crackedMarkShader = trap_R_RegisterShader( "gfx/damage/cracked_mrk" );' in cg_main_c
	assert 'cgs.media.sfx_grapplehit = trap_S_RegisterSound( "sound/weapons/grapple/grhit.ogg", qfalse );' in cg_main_c

	for expected in (
		"case WP_GRAPPLING_HOOK:",
		"sfx = cgs.media.sfx_grapplehit;",
		"mark = cgs.media.crackedMarkShader;",
		"radius = 16;",
	):
		assert expected in grapple_impact

	for expected in (
		'DAT_10a5f8d4 = (**(code **)(DAT_1074cccc + 0xb8))("sound/weapons/grapple/grhit.ogg");',
		'DAT_10a5f634 = (**(code **)(DAT_1074cccc + 0xd0))("gfx/damage/cracked_mrk");',
		"case 10:",
		"iVar6 = DAT_10a5f8d4;",
		"local_178c = DAT_10a5f634;",
	):
		assert expected in cgame_ghidra

	for expected in (
		'data_10a5f8d4 = (*(ecx_142 + 0xb8))("sound/weapons/grapple/grhit.ogg")',
		"data_10a5f634 = eax_452",
	):
		assert expected in cgame_hlil

	assert "grapple-impact `gfx/damage/cracked_mrk` handle" in cgame_symbols
	assert "retail grappling-hook branch that uses `sound/weapons/grapple/grhit.ogg`" in cgame_symbols


def test_grappling_hook_cross_binary_mapping_aliases_are_promoted() -> None:
	aliases = json.loads(_read("references/analysis/quakelive_symbol_aliases.json"))
	cgame_aliases = aliases["cgame"]
	qagame_aliases = aliases["qagamex86"]
	steam_aliases = aliases["quakelive_steam_srp"]
	qagame_functions = _read("references/reverse-engineering/ghidra/qagamex86/functions.csv")
	cgame_functions = _read("references/reverse-engineering/ghidra/cgamex86/functions.csv")
	steam_functions = _read("references/reverse-engineering/ghidra/quakelive_steam/functions.csv")
	qagame_symbols = _read("references/symbol-maps/qagame.json")
	cgame_symbols = _read("references/symbol-maps/cgame.json")

	for raw, normalized in {
		"FUN_100178e0": "CG_Grapple",
		"sub_100178e0": "CG_Grapple",
		"FUN_10050990": "CG_GrappleTrail",
		"sub_10050990": "CG_GrappleTrail",
	}.items():
		assert cgame_aliases[raw] == normalized

	for raw, normalized in {
		"sub_490550": "AAS_Reachability_Grapple",
		"sub_4A3DE0": "BotTravel_Grapple",
	}.items():
		assert steam_aliases[raw] == normalized

	for raw, normalized in {
		"sub_1005a420": "TeleportPlayer",
		"FUN_1005bbe0": "G_MissileImpact",
		"sub_1005bbe0": "G_MissileImpact",
		"FUN_1005d270": "fire_grapple",
		"sub_1005d270": "fire_grapple",
		"FUN_1006e2c0": "Weapon_GrapplingHook_Fire",
		"sub_1006e2c0": "Weapon_GrapplingHook_Fire",
		"FUN_1006e330": "Weapon_HookFree",
		"sub_1006e330": "Weapon_HookFree",
		"FUN_1006e400": "Weapon_HookThink",
		"sub_1006e400": "Weapon_HookThink",
		"FUN_1006f290": "FireWeapon",
		"sub_1006f290": "FireWeapon",
	}.items():
		assert qagame_aliases[raw] == normalized

	for expected in (
		"FUN_1005bbe0,1005bbe0,3347,0,unknown",
		"FUN_1005d270,1005d270,409,0,unknown",
		"FUN_1006e2c0,1006e2c0,105,0,unknown",
		"FUN_1006e330,1006e330,205,0,unknown",
		"FUN_1006e400,1006e400,950,0,unknown",
	):
		assert expected in qagame_functions

	for expected in (
		"FUN_100178e0,100178e0,513,0,unknown",
		"FUN_10050990,10050990,266,0,unknown",
	):
		assert expected in cgame_functions

	for expected in (
		"FUN_00490550,00490550,1822,0,unknown",
		"FUN_004a3de0,004a3de0,1183,0,unknown",
	):
		assert expected in steam_functions

	for expected in (
		"Retail grapple projectile constructor",
		"Retail grapple-fire gate",
		"Exact match for the grapple cleanup helper",
		"Retail grapple think routine",
		"the grapple hook handling",
		"frees an active grappling hook through Weapon_HookFree",
	):
		assert expected in qagame_symbols

	for expected in (
		"Grapple-hook renderer",
		"Grapple chain trail callback installed for the hook weapon",
		"retail grappling-hook branch",
	):
		assert expected in cgame_symbols
