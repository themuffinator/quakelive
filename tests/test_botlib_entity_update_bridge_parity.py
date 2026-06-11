from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

BOTLIB_H = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
BOTLIB_BE_AAS_H = REPO_ROOT / "src" / "code" / "game" / "be_aas.h"
BOTLIB_AAS_ENTITY = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_entity.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
GAME_AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
GAME_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
SERVER_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
QL_GAME_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
QL_STEAM_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
)
QAGAME_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "functions.csv"
)
QAGAME_DECOMPILE_TOP = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "decompile_top_functions.c"
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
QAGAME_HLIL_PART01 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part01.txt"
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _function_rows(path: Path) -> dict[str, str]:
	rows: dict[str, str] = {}
	with path.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			rows[row["entry"].upper()] = (
				f'{row["name"]},{row["entry"]},{row["size"]},{row["thunk"]},{row["calling_convention"]}'
			)
	return rows


def _extract_function_block(source: str, signature: str) -> str:
	start = source.find(signature)
	assert start != -1, signature
	brace = source.find("{", start)
	assert brace != -1, signature

	depth = 0
	for offset in range(brace, len(source)):
		if source[offset] == "{":
			depth += 1
		elif source[offset] == "}":
			depth -= 1
			if depth == 0:
				return source[start : offset + 1]

	raise AssertionError(f"unterminated function block: {signature}")


def _assert_ordered(text: str, anchors: tuple[str, ...]) -> None:
	offset = 0
	for anchor in anchors:
		found = text.find(anchor, offset)
		assert found != -1, anchor
		offset = found + len(anchor)


def test_botlib_entity_update_retail_symbols_and_function_rows_are_pinned() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))
	ql_aliases = aliases["quakelive_steam_srp"]
	qagame_aliases = aliases["qagamex86"]
	ql_rows = _function_rows(QL_STEAM_FUNCTIONS)
	qagame_rows = _function_rows(QAGAME_FUNCTIONS)

	for address, name in (
		("sub_484E20", "AAS_UpdateEntity"),
		("sub_4A7F40", "Export_BotLibUpdateEntity"),
		("sub_4E17A0", "QL_G_trap_BotLibUpdateEntity"),
	):
		assert ql_aliases[address] == name

	assert qagame_aliases["FUN_10023400"] == "BotAIStartFrame"
	assert qagame_aliases["sub_10023400"] == "BotAIStartFrame"

	assert ql_rows["00484E20"] == "FUN_00484e20,00484e20,907,0,unknown"
	assert ql_rows["004A7F40"] == "FUN_004a7f40,004a7f40,102,0,unknown"
	assert ql_rows["004E17A0"] == "FUN_004e17a0,004e17a0,18,0,unknown"
	assert qagame_rows["10023400"] == "FUN_10023400,10023400,2038,0,unknown"


def test_botlib_entity_update_source_bridge_matches_retail_wiring() -> None:
	botlib_h = _read(BOTLIB_H)
	be_aas_h = _read(BOTLIB_BE_AAS_H)
	ai_main = _read(GAME_AI_MAIN)
	aas_entity = _read(BOTLIB_AAS_ENTITY)
	be_interface = _read(BOTLIB_INTERFACE)
	game_public = _read(GAME_PUBLIC)
	game_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	ql_game_imports = _read(QL_GAME_IMPORTS)

	for expected in (
		"float\tqlTimeSeconds;\t// retail word 0x1c",
		"int\t\tqlPowerupsActive[BOTLIB_QL_POWERUP_ACTIVE_COUNT];\t// retail words 0x22-0x31",
		"int\t\tqlFlagsBit18Clear;\t// retail word 0x32",
		"int\t\tqlRedBlueFlagCarrier;\t// retail word 0x33",
	):
		assert expected in botlib_h

	for expected in (
		"float\tqlTimeSeconds;\t// retail word 0x23",
		"int\t\tqlPowerupsActive[BOTLIB_QL_POWERUP_ACTIVE_COUNT];\t// retail words 0x29-0x38",
		"int\t\tqlFlagsBit18Clear;\t// retail word 0x39",
		"int\t\tqlRedBlueFlagCarrier;\t// retail word 0x3a",
	):
		assert expected in be_aas_h

	start_frame = _extract_function_block(ai_main, "int BotAIStartFrame(int time)")
	assert start_frame.count("trap_BotLibUpdateEntity(i, NULL);") == 6
	assert "if (ent->s.eType == ET_MISSILE && ent->s.weapon != WP_GRAPPLING_HOOK)" in start_frame
	assert "if (ent->s.eType > ET_EVENTS)" in start_frame
	assert "if (ent->touch == ProximityMine_Trigger)" in start_frame
	assert "state.qlFlagsBit18Clear = ( ent->flags & RETAIL_BOTLIB_GENTITY_FLAG_BIT18 ) ? 0 : 1;" in start_frame
	assert "state.qlRedBlueFlagCarrier = ( ent->client->ps.powerups[PW_REDFLAG]" in start_frame
	assert "powerupTime >= level.time || powerupTime == INT_MAX" in start_frame
	_assert_ordered(
		start_frame,
		(
			"trap_BotLibStartFrame((float) time / 1000);",
			"if (!trap_AAS_Initialized()) return qfalse;",
			"for (i = 0; i < MAX_GENTITIES; i++)",
			"memset(&state, 0, sizeof(bot_entitystate_t));",
			"state.qlTimeSeconds = (float)( ent->s.time / 1000 );",
			"state.qlFlagsBit18Clear = ( ent->flags & RETAIL_BOTLIB_GENTITY_FLAG_BIT18 ) ? 0 : 1;",
			"if (ent->client) {",
			"state.qlPlayerGravity = ent->client->ps.gravity;",
			"state.qlPlayerSpeed = ent->client->ps.speed;",
			"state.qlPlayerDeltaAngle0 = ent->client->ps.delta_angles[0];",
			"state.qlEntityHealth = ent->health;",
			"state.qlClientMaxHealth = ent->client->ps.stats[STAT_MAX_HEALTH];",
			"state.qlRedBlueFlagCarrier = ( ent->client->ps.powerups[PW_REDFLAG]",
			"for ( powerup = 0; powerup < BOTLIB_QL_POWERUP_ACTIVE_COUNT && powerup < MAX_POWERUPS; powerup++ )",
			"state.qlPowerupsActive[powerup] =",
			"trap_BotLibUpdateEntity(i, &state);",
			"BotAIRegularUpdate();",
		),
	)

	update_entity = _extract_function_block(aas_entity, "int AAS_UpdateEntity(int entnum, bot_entitystate_t *state)")
	assert "AAS_UnlinkFromAreas(ent->areas);" in update_entity
	assert "AAS_UnlinkFromBSPLeaves(ent->leaves);" in update_entity
	assert "ent->areas = NULL;" in update_entity
	assert "ent->leaves = NULL;" in update_entity
	_assert_ordered(
		update_entity,
		(
			"ent->i.powerups = state->powerups;",
			"ent->i.weapon = state->weapon;",
			"ent->i.legsAnim = state->legsAnim;",
			"ent->i.torsoAnim = state->torsoAnim;",
			"ent->i.qlTimeSeconds = state->qlTimeSeconds;",
			"ent->i.qlPlayerGravity = state->qlPlayerGravity;",
			"ent->i.qlPlayerSpeed = state->qlPlayerSpeed;",
			"ent->i.qlPlayerDeltaAngle0 = state->qlPlayerDeltaAngle0;",
			"ent->i.qlEntityHealth = state->qlEntityHealth;",
			"ent->i.qlClientMaxHealth = state->qlClientMaxHealth;",
			"Com_Memcpy(ent->i.qlPowerupsActive, state->qlPowerupsActive, sizeof(ent->i.qlPowerupsActive));",
			"ent->i.qlFlagsBit18Clear = state->qlFlagsBit18Clear;",
			"ent->i.qlRedBlueFlagCarrier = state->qlRedBlueFlagCarrier;",
			"ent->i.number = entnum;",
			"ent->i.valid = qtrue;",
			"ent->areas = AAS_LinkEntityClientBBox(absmins, absmaxs, entnum, PRESENCE_NORMAL);",
			"ent->leaves = AAS_BSPLinkEntity(absmins, absmaxs, entnum, 0);",
		),
	)

	entity_info = _extract_function_block(aas_entity, "void AAS_EntityInfo(int entnum, aas_entityinfo_t *info)")
	assert "Com_Memset(info, 0, sizeof(aas_entityinfo_t));" in entity_info
	assert "Com_Memcpy(info, &aasworld.entities[entnum].i, sizeof(aas_entityinfo_t));" in entity_info

	export_update = _extract_function_block(be_interface, "int Export_BotLibUpdateEntity(int ent, bot_entitystate_t *state)")
	_assert_ordered(
		export_update,
		(
			'if (!BotLibSetup("BotUpdateEntity")) return BLERR_LIBRARYNOTSETUP;',
			'if (!ValidEntityNumber(ent, "BotUpdateEntity")) return BLERR_INVALIDENTITYNUMBER;',
			"return AAS_UpdateEntity(ent, state);",
		),
	)
	assert "be_botlib_export.BotLibUpdateEntity = Export_BotLibUpdateEntity;" in be_interface

	for expected in (
		"BOTLIB_UPDATENTITY,",
		"G_QL_IMPORT_BOTLIB_UPDATE_ENTITY = 56,",
	):
		assert expected in game_public

	for expected in (
		"case BOTLIB_UPDATENTITY: return G_QL_IMPORT_BOTLIB_UPDATE_ENTITY;",
		"int trap_BotLibUpdateEntity(int ent, void /* struct bot_updateentity_s */ *bue)",
		"return syscall( BOTLIB_UPDATENTITY, ent, bue );",
	):
		assert expected in game_syscalls

	for expected in (
		"case BOTLIB_UPDATENTITY:",
		"return botlib_export->BotLibUpdateEntity( args[1], VMA(2) );",
		"[BOTLIB_UPDATENTITY] = (ql_import_f)QL_G_trap_BotLibUpdateEntity,",
		"ql_game_imports[G_QL_IMPORT_BOTLIB_UPDATE_ENTITY] = (ql_import_f)QL_G_trap_BotLibUpdateEntity;",
	):
		assert expected in server_game

	assert "QL_G_trap_BotLibUpdateEntity" in ql_game_imports
	assert "return G_Import_Syscall( BOTLIB_UPDATENTITY, ent, bue );" in ql_game_imports


def test_botlib_entity_update_retail_hlil_pins_ql_tail_and_bridge_sizes() -> None:
	ql_hlil = _read(QL_STEAM_HLIL_PART03)
	qagame_hlil = _read(QAGAME_HLIL_PART01)
	qagame_ghidra = _read(QAGAME_DECOMPILE_TOP)

	for expected in (
		"00484e20    int32_t sub_484e20(int32_t arg1, int32_t* arg2)",
		'00484e49      data_16dd800(1, "AAS_UpdateEntity: not loaded\\n")',
		"00484e6b  int32_t* ebx_2 = arg1 * 0xf4 + data_16de9a8",
		"00484eb2      return 0",
		"00484f28  ebx_2[0x23] = fconvert.s(fconvert.t(arg2[0x1c]))",
		"00484f31  ebx_2[0x24] = arg2[0x1d]",
		"00484f3a  ebx_2[0x25] = arg2[0x1e]",
		"00484f43  ebx_2[0x26] = arg2[0x1f]",
		"00484f4c  ebx_2[0x27] = arg2[0x20]",
		"00484f55  ebx_2[0x28] = arg2[0x21]",
		"00484f5e  ebx_2[0x39] = arg2[0x32]",
		"00484f69  __builtin_memcpy(dest: &ebx_2[0x29], src: &arg2[0x22], n: 0x40)",
		"00484fa0  ebx_2[0x3a] = arg2[0x33]",
		"00484fa9  ebx_2[5] = arg1",
		"00484fac  *ebx_2 = 1",
		"004851dd      return sub_4c95e0(arg2, 0, 0xec)",
		"return sub_4cb7d0(arg2, arg1 * 0xf4 + data_16de9a8, 0xec)",
		"004a7f40    int32_t sub_4a7f40(int32_t arg1, int32_t* arg2)",
		'data_16dd800(3, "%s: bot library used before bein',
		"004a7fa5      return sub_484e20(arg1, arg2)",
		"004a8495  data_16dda7c = sub_4a7f40",
	):
		assert expected in ql_hlil

	for expected in (
		"memset(&iStack_e0,0,0xd0);",
		"fStack_70 = (float)(piVar4[0x47] / 1000);",
		"uStack_6c = *(undefined4 *)(iVar3 + 0x30);",
		"uStack_68 = *(undefined4 *)(iVar3 + 0x34);",
		"iStack_60 = piVar4[0x52];",
		"uStack_5c = *(undefined4 *)(iVar3 + 0xdc);",
		"if ((*(int *)(iVar3 + 0x144) != 0) || (uStack_14 = 0, *(int *)(iVar3 + 0x148) != 0))",
		"piVar5 = (int *)(iVar3 + 0x180);",
		"memset(auStack_58,0,0x40);",
	):
		assert expected in qagame_ghidra

	for expected in (
		"10023400    int32_t sub_10023400(long double arg1 @ st0, int32_t arg2)",
		"*(esp_14 + 0x88) = float.s",
		"*(esp_14 + 0xe0) = not.d(edx_25 u>> 0x12) & 1",
		"*(esp_14 + 0x98) = *(i + 0x148)",
		"*(esp_14 + 0x9c) = *(edx_30 + 0xdc)",
		"if (*(edx_30 + 0x144) == 0)",
		"if (*(edx_30 + 0x144) != 0 || not(cond:2_1))",
		"void* esi_4 = edx_30 + 0x180",
		"if (edx_31 s>= *j || edx_31 == 0xffffffff)",
	):
		assert expected in qagame_hlil
