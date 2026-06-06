from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

BOTLIB_AI_GEN = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_gen.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
GAME_AI_GEN_H = REPO_ROOT / "src" / "code" / "game" / "be_ai_gen.h"
GAME_AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
GAME_G_LOCAL = REPO_ROOT / "src" / "code" / "game" / "g_local.h"
GAME_G_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
SERVER_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SERVER_QL_GAME_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
QL_STEAM_FUNCTIONS = (
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


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _aliases() -> dict[str, str]:
	return json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	assert start != -1, signature
	brace = text.find("{", start)
	assert brace != -1, signature

	depth = 0
	for offset in range(brace, len(text)):
		if text[offset] == "{":
			depth += 1
		elif text[offset] == "}":
			depth -= 1
			if depth == 0:
				return text[start : offset + 1]

	raise AssertionError(f"unterminated function block: {signature}")


def _assert_order(text: str, *needles: str) -> None:
	position = -1
	for needle in needles:
		next_position = text.find(needle)
		assert next_position != -1, needle
		assert next_position > position, needle
		position = next_position


def test_genetic_selection_aliases_and_retail_function_rows_are_pinned() -> None:
	aliases = _aliases()
	functions = _read(QL_STEAM_FUNCTIONS)
	hlil = _read(QL_STEAM_HLIL_PART03)

	assert aliases["sub_49C6C0"] == "GeneticSelection"
	assert aliases["sub_49C810"] == "GeneticParentsAndChildSelection"
	assert "FUN_0049c6c0,0049c6c0,321,0,unknown" in functions
	assert "FUN_0049c810,0049c810,1047,0,unknown" in functions

	for evidence in (
		"0049c6c0    void sub_49c6c0(int32_t arg1, void* arg2)",
		"0049c756  x87_r7 - fconvert.t(var_8_1)",
		"0049c7c1  int32_t edx_3 = sub_526000(float.t(rand() & 0x7fff) / fconvert.t(32767.0) * float.t(arg1))",
		"0049c810    int32_t sub_49c810",
		"GeneticParentsAndChildSelection:",
		"0049c9bf  st0, eax_7 = sub_49c6c0(arg1, &var_408)",
		"0049c9e1  st0_1, eax_8 = sub_49c6c0(arg1, &var_408)",
		"0049cc01  st0_2, eax_9 = sub_49c6c0(arg1, &var_408)",
		"004a8393  arg1[0x4a] = sub_49c810",
	):
		assert evidence in hlil


def test_genetic_selection_source_shape_matches_retail_helper_pair() -> None:
	source = _read(BOTLIB_AI_GEN)

	select_block = _extract_function_block(source, "int GeneticSelection(int numranks, float *rankings)")
	parents_block = _extract_function_block(
		source,
		"int GeneticParentsAndChildSelection(int numranks, float *ranks, int *parent1, int *parent2, int *child)",
	)

	assert "sum = 0;" in select_block
	assert "for (i = 0; i < numranks; i++)" in select_block
	assert "if (rankings[i] < 0) continue;" in select_block
	assert "sum += rankings[i];" in select_block
	assert "if (sum > 0)" in select_block
	assert "select = random() * sum;" in select_block
	assert "sum -= rankings[i];" in select_block
	assert "if (sum <= 0) return i;" in select_block
	assert "index = random() * numranks;" in select_block
	assert "if (rankings[index] >= 0) return index;" in select_block
	assert "index = (index + 1) % numranks;" in select_block
	assert "return 0;" in select_block

	assert "if (numranks > 256)" in parents_block
	assert 'botimport.Print(PRT_WARNING, "GeneticParentsAndChildSelection: too many bots\\n");' in parents_block
	assert "*parent1 = *parent2 = *child = 0;" in parents_block
	assert "return qfalse;" in parents_block
	assert "for (max = 0, i = 0; i < numranks; i++)" in parents_block
	assert "if (ranks[i] < 0) continue;" in parents_block
	assert "max++;" in parents_block
	assert "if (max < 3)" in parents_block
	assert 'botimport.Print(PRT_WARNING, "GeneticParentsAndChildSelection: too few valid bots\\n");' in parents_block
	assert "Com_Memcpy(rankings, ranks, sizeof(float) * numranks);" in parents_block
	assert "*parent1 = GeneticSelection(numranks, rankings);" in parents_block
	assert "rankings[*parent1] = -1;" in parents_block
	assert "*parent2 = GeneticSelection(numranks, rankings);" in parents_block
	assert "rankings[*parent2] = -1;" in parents_block
	assert "if (rankings[i] > max) max = rankings[i];" in parents_block
	assert "rankings[i] = max - rankings[i];" in parents_block
	assert "*child = GeneticSelection(numranks, rankings);" in parents_block
	assert "return qtrue;" in parents_block


def test_genetic_parent_child_export_and_import_wiring_match_retail_shape() -> None:
	interface = _read(BOTLIB_INTERFACE)
	public_api = _read(BOTLIB_PUBLIC)
	header = _read(GAME_AI_GEN_H)
	g_public = _read(GAME_G_PUBLIC)
	g_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	server_imports = _read(SERVER_QL_GAME_IMPORTS)
	hlil = _read(QL_STEAM_HLIL_PART03)

	init_export = _extract_function_block(interface, "static void Init_AI_Export( ai_export_t *ai )")

	assert "int GeneticParentsAndChildSelection(int numranks, float *ranks, int *parent1, int *parent2, int *child);" in header
	assert "int\t\t(*GeneticParentsAndChildSelection)(int numranks, float *ranks, int *parent1, int *parent2, int *child);" in public_api
	assert "ai->GeneticParentsAndChildSelection = GeneticParentsAndChildSelection;" in init_export
	_assert_order(
		public_api,
		"void\t(*BotResetWeaponState)(int weaponstate);",
		"int\t\t(*GeneticParentsAndChildSelection)(int numranks, float *ranks, int *parent1, int *parent2, int *child);",
		"void\t(*BotDrawDebugAreas)(vec3_t origin, int enable, int areanum);",
	)
	_assert_order(
		init_export,
		"ai->BotResetWeaponState = BotResetWeaponState;",
		"ai->GeneticParentsAndChildSelection = GeneticParentsAndChildSelection;",
		"ai->BotDrawDebugAreas = BotDrawDebugAreas;",
	)

	assert "\tBOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION," in g_public
	assert "\tG_QL_IMPORT_BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION = 184," in g_public
	assert "case BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION: return G_QL_IMPORT_BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION;" in g_syscalls
	assert "return syscall( BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION, numranks, ranks, parent1, parent2, child );" in g_syscalls
	assert "case BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION:" in server_game
	assert "return botlib_export->ai.GeneticParentsAndChildSelection(args[1], VMA(2), VMA(3), VMA(4), VMA(5));" in server_game
	assert "[BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION] = (ql_import_f)QL_G_trap_GeneticParentsAndChildSelection," in server_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION] = (ql_import_f)QL_G_trap_GeneticParentsAndChildSelection;" in server_game
	assert "static int QDECL QL_G_trap_GeneticParentsAndChildSelection" in server_imports
	assert "return G_Import_Syscall( BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION, numranks, ranks, parent1, parent2, child );" in server_imports
	assert "004a8393  arg1[0x4a] = sub_49c810" in hlil


def test_qagame_interbreed_consumer_uses_genetic_selection_result_shape() -> None:
	ai_main = _read(GAME_AI_MAIN)
	g_local = _read(GAME_G_LOCAL)

	interbreed = _extract_function_block(ai_main, "void BotInterbreedBots(void)")
	end_match = _extract_function_block(ai_main, "void BotInterbreedEndMatch(void)")

	assert "int\t\ttrap_GeneticParentsAndChildSelection(int numranks, float *ranks, int *parent1, int *parent2, int *child);" in g_local
	assert "float ranks[MAX_CLIENTS];" in interbreed
	assert "int parent1, parent2, child;" in interbreed
	assert "ranks[i] = botstates[i]->num_kills * 2 - botstates[i]->num_deaths;" in interbreed
	assert "ranks[i] = -1;" in interbreed
	assert "if (trap_GeneticParentsAndChildSelection(MAX_CLIENTS, ranks, &parent1, &parent2, &child))" in interbreed
	assert "trap_BotInterbreedGoalFuzzyLogic(botstates[parent1]->gs, botstates[parent2]->gs, botstates[child]->gs);" in interbreed
	assert "trap_BotMutateGoalFuzzyLogic(botstates[child]->gs, 1);" in interbreed
	assert "botstates[i]->num_kills = 0;" in interbreed
	assert "botstates[i]->num_deaths = 0;" in interbreed
	_assert_order(
		interbreed,
		"if (trap_GeneticParentsAndChildSelection(MAX_CLIENTS, ranks, &parent1, &parent2, &child))",
		"trap_BotInterbreedGoalFuzzyLogic(botstates[parent1]->gs, botstates[parent2]->gs, botstates[child]->gs);",
		"trap_BotMutateGoalFuzzyLogic(botstates[child]->gs, 1);",
		"botstates[i]->num_kills = 0;",
	)

	assert "if (!bot_interbreed) return;" in end_match
	assert "bot_interbreedmatchcount++;" in end_match
	assert "if (bot_interbreedmatchcount >= bot_interbreedcycle.integer)" in end_match
	assert 'trap_Cvar_Update(&bot_interbreedwrite);' in end_match
	assert 'trap_Cvar_Set("bot_interbreedwrite", "");' in end_match
	assert "BotInterbreedBots();" in end_match
