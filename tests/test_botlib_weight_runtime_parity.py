from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOTLIB_AI_GOAL = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_goal.c"
BOTLIB_AI_WEAP = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_weap.c"
BOTLIB_AI_WEIGHT = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_weight.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
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


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(text)):
		char = text[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def test_botlib_weight_runtime_retail_function_map_is_bounded() -> None:
	functions_csv = QL_STEAM_FUNCTIONS.read_text(encoding="utf-8")
	hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")
	aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]

	for address, name in (
		("4A63F0", "ReadValue"),
		("4A64D0", "ReadFuzzyWeight"),
		("4A65C0", "FreeFuzzySeperators_r"),
		("4A6600", "FreeWeightConfig2"),
		("4A6670", "FreeWeightConfig"),
		("4A66A0", "ReadFuzzySeperators_r"),
		("4A6B40", "ReadWeightConfig"),
		("4A7140", "FindFuzzyWeight"),
		("4A71A0", "FuzzyWeight_r"),
		("4A7260", "FuzzyWeightUndecided_r"),
		("4A7390", "FuzzyWeight"),
		("4A73B0", "FuzzyWeightUndecided"),
		("4A73D0", "EvolveFuzzySeperator_r"),
		("4A74B0", "EvolveWeightConfig"),
		("4A75C0", "InterbreedFuzzySeperator_r"),
		("4A76D0", "InterbreedWeightConfigs"),
		("4A7820", "BotShutdownWeights"),
		("49F6F0", "BotLoadItemWeights"),
		("49F780", "BotFreeItemWeights"),
		("49CC30", "BotInterbreedGoalFuzzyLogic"),
		("49CCF0", "BotSaveGoalFuzzyLogic"),
		("49CD30", "BotMutateGoalFuzzyLogic"),
		("4A5FA0", "WeaponWeightIndex"),
		("4A5FF0", "BotFreeWeaponWeights"),
		("4A6060", "BotLoadWeaponWeights"),
		("4A6190", "BotChooseBestFightWeapon"),
	):
		assert aliases[f"sub_{address}"] == name

	for row in (
		"FUN_004a63f0,004a63f0,211,0,unknown",
		"FUN_004a64d0,004a64d0,230,0,unknown",
		"FUN_004a65c0,004a65c0,55,0,unknown",
		"FUN_004a6600,004a6600,108,0,unknown",
		"FUN_004a6670,004a6670,35,0,unknown",
		"FUN_004a66a0,004a66a0,1180,0,unknown",
		"FUN_004a6b40,004a6b40,1524,0,unknown",
		"FUN_004a7140,004a7140,89,0,unknown",
		"FUN_004a71a0,004a71a0,180,0,unknown",
		"FUN_004a7260,004a7260,295,0,unknown",
		"FUN_004a7390,004a7390,28,0,unknown",
		"FUN_004a73b0,004a73b0,28,0,unknown",
		"FUN_004a73d0,004a73d0,220,0,unknown",
		"FUN_004a74b0,004a74b0,264,0,unknown",
		"FUN_004a75c0,004a75c0,258,0,unknown",
		"FUN_004a76d0,004a76d0,332,0,unknown",
		"FUN_004a7820,004a7820,158,0,unknown",
	):
		assert row in functions_csv

	for evidence in (
		"004a64d0    int32_t sub_4a64d0(int32_t arg1, void* arg2)",
		'004a64ec  if (sub_4aca70(arg1, "balance") == 0)',
		'004a645f          sub_4a8b30(arg1, "negative value set to zero\\n")',
		'004a648f          sub_4a8ad0(arg1, "invalid return value %s\\n")',
		"004a66a0    int32_t* sub_4a66a0(int32_t arg1)",
		'004a6a44              sub_4a8ad0(var_440, "switch already has a default\\n")',
		'004a6a85          sub_4a8b30(var_440, "switch without default\\n")',
		"004a6b40    char* sub_4a6b40(char* arg1)",
		'004a6bf7          data_16dd800(3, "weightFileList was full trying t',
		"004a6c4d      data_16dd800(3, \"counldn't load %s\\n\", arg1)",
		'004a6f12              sub_4a8b30(esi_2, "too many fuzzy weights\\n")',
		'004a6ece  data_16dd800(1, "loaded %s\\n", arg1)',
		"004a7140    int32_t sub_4a7140(int32_t* arg1, char* arg2)",
		"004a71a0    int32_t* sub_4a71a0(float arg1, int32_t* arg2)",
		"004a7260    int32_t* sub_4a7260(int32_t arg1, float arg2)",
		"004a7390    int32_t* sub_4a7390(float arg1, int32_t arg2, int32_t arg3)",
		"004a73b0    int32_t* sub_4a73b0(int32_t arg1, int32_t arg2, int32_t arg3)",
		"004a7820    void sub_4a7820()",
	):
		assert evidence in hlil


def test_botlib_weight_parser_source_shape_matches_retail_diagnostics() -> None:
	weight_source = BOTLIB_AI_WEIGHT.read_text(encoding="utf-8")

	read_value = _extract_function_block(weight_source, "int ReadValue(source_t *source, float *value)")
	read_fuzzy_weight = _extract_function_block(weight_source, "int ReadFuzzyWeight(source_t *source, fuzzyseperator_t *fs)")
	read_switch = _extract_function_block(
		weight_source, "fuzzyseperator_t *ReadFuzzySeperators_r(source_t *source)"
	)
	read_config = _extract_function_block(weight_source, "weightconfig_t *ReadWeightConfig(char *filename)")
	free_config = _extract_function_block(weight_source, "void FreeWeightConfig(weightconfig_t *config)")
	shutdown = _extract_function_block(weight_source, "void BotShutdownWeights(void)")

	assert 'SourceWarning(source, "negative value set to zero\\n");' in read_value
	assert 'SourceError(source, "invalid return value %s\\n", token.string);' in read_value
	assert "fs->type = WT_BALANCE;" in read_fuzzy_weight
	assert 'if (!PC_ExpectTokenString(source, "balance"))' not in read_fuzzy_weight
	assert 'if (PC_CheckTokenString(source, "balance"))' in read_fuzzy_weight
	assert "fs->minweight = fs->weight;" in read_fuzzy_weight
	assert "fs->maxweight = fs->weight;" in read_fuzzy_weight
	assert 'if (!PC_ExpectTokenString(source, ";")) return qfalse;' in read_fuzzy_weight

	assert 'if (!PC_ExpectTokenString(source, "(")) return NULL;' in read_switch
	assert "def = !strcmp(token.string, \"default\");" in read_switch
	assert 'if (def || !strcmp(token.string, "case"))' in read_switch
	assert 'SourceError(source, "switch already has a default\\n");' in read_switch
	assert "fs->value = MAX_INVENTORYVALUE;" in read_switch
	assert "fs->child = ReadFuzzySeperators_r(source);" in read_switch
	assert 'SourceError(source, "invalid name %s\\n", token.string);' in read_switch
	assert 'SourceWarning(source, "switch without default\\n");' in read_switch
	assert "fs->weight = 0;" in read_switch

	assert 'if (!LibVarGetValue("bot_reloadcharacters"))' in read_config
	assert "for( n = 0; n < MAX_WEIGHT_FILES; n++ )" in read_config
	assert 'botimport.Print( PRT_ERROR, "weightFileList was full trying to load %s\\n", filename );' in read_config
	assert "PC_SetBaseFolder(BOTFILESBASEFOLDER);" in read_config
	assert "botimport.Print(PRT_ERROR, \"counldn't load %s\\n\", filename);" in read_config
	assert "config = (weightconfig_t *) GetClearedMemory(sizeof(weightconfig_t));" in read_config
	assert "Q_strncpyz( config->filename, filename, sizeof(config->filename) );" in read_config
	assert 'if (!strcmp(token.string, "weight"))' in read_config
	assert "if (config->numweights >= MAX_WEIGHTS)" in read_config
	assert 'SourceWarning(source, "too many fuzzy weights\\n");' in read_config
	assert "config->weights[config->numweights].name = (char *) GetClearedMemory(strlen(token.string) + 1);" in read_config
	assert "fs = ReadFuzzySeperators_r(source);" in read_config
	assert "fs->value = MAX_INVENTORYVALUE;" in read_config
	assert 'SourceError(source, "invalid name %s\\n", token.string);' in read_config
	assert 'botimport.Print(PRT_MESSAGE, "loaded %s\\n", filename);' in read_config
	assert "weightFileList[avail] = config;" in read_config

	assert 'if (!LibVarGetValue("bot_reloadcharacters")) return;' in free_config
	assert "FreeWeightConfig2(config);" in free_config
	assert "for( i = 0; i < MAX_WEIGHT_FILES; i++ )" in shutdown
	assert "FreeWeightConfig2(weightFileList[i]);" in shutdown
	assert "weightFileList[i] = NULL;" in shutdown


def test_botlib_weight_evaluator_and_mutation_shape_matches_retail() -> None:
	weight_source = BOTLIB_AI_WEIGHT.read_text(encoding="utf-8")
	hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")

	fuzzy = _extract_function_block(weight_source, "float FuzzyWeight_r(int *inventory, fuzzyseperator_t *fs)")
	undecided = _extract_function_block(weight_source, "float FuzzyWeightUndecided_r(int *inventory, fuzzyseperator_t *fs)")
	fuzzy_wrapper = _extract_function_block(weight_source, "float FuzzyWeight(int *inventory, weightconfig_t *wc, int weightnum)")
	undecided_wrapper = _extract_function_block(
		weight_source, "float FuzzyWeightUndecided(int *inventory, weightconfig_t *wc, int weightnum)"
	)
	evolve = _extract_function_block(weight_source, "void EvolveFuzzySeperator_r(fuzzyseperator_t *fs)")
	scale_weight = _extract_function_block(weight_source, "void ScaleWeight(weightconfig_t *config, char *name, float scale)")
	scale_range = _extract_function_block(weight_source, "void ScaleFuzzyBalanceRange(weightconfig_t *config, float scale)")
	interbreed = _extract_function_block(weight_source, "void InterbreedWeightConfigs(weightconfig_t *config1, weightconfig_t *config2,")

	assert "if (inventory[fs->index] < fs->value)" in fuzzy
	assert "if (fs->child) return FuzzyWeight_r(inventory, fs->child);" in fuzzy
	assert "if (inventory[fs->index] < fs->next->value)" in fuzzy
	assert "scale = (inventory[fs->index] - fs->value) / (fs->next->value - fs->value);" in fuzzy
	assert "return scale * w1 + (1 - scale) * w2;" in fuzzy

	assert "if (fs->child) return FuzzyWeightUndecided_r(inventory, fs->child);" in undecided
	assert "else return fs->minweight + random() * (fs->maxweight - fs->minweight);" in undecided
	assert "if (fs->next->child) w2 = FuzzyWeight_r(inventory, fs->next->child);" in undecided
	assert "else w2 = fs->next->minweight + random() * (fs->next->maxweight - fs->next->minweight);" in undecided
	assert "return FuzzyWeightUndecided_r(inventory, fs->next);" in undecided

	assert "#ifdef EVALUATERECURSIVELY" in fuzzy_wrapper
	assert "return FuzzyWeight_r(inventory, wc->weights[weightnum].firstseperator);" in fuzzy_wrapper
	assert "return FuzzyWeightUndecided_r(inventory, wc->weights[weightnum].firstseperator);" in undecided_wrapper

	assert "if (random() < 0.01)" in evolve
	assert "fs->weight += crandom() * (fs->maxweight - fs->minweight);" in evolve
	assert "else fs->weight += crandom() * (fs->maxweight - fs->minweight) * 0.5;" in evolve
	assert "if (fs->weight < fs->minweight) fs->minweight = fs->weight;" in evolve
	assert "else if (fs->weight > fs->maxweight) fs->maxweight = fs->weight;" in evolve

	assert "if (scale < 0) scale = 0;" in scale_weight
	assert "else if (scale > 1) scale = 1;" in scale_weight
	assert "ScaleFuzzySeperator_r(config->weights[i].firstseperator, scale);" in scale_weight
	assert "if (scale < 0) scale = 0;" in scale_range
	assert "else if (scale > 100) scale = 100;" in scale_range
	assert "ScaleFuzzySeperatorBalanceRange_r(config->weights[i].firstseperator, scale);" in scale_range

	assert "InterbreedFuzzySeperator_r(config1->weights[i].firstseperator," in interbreed
	assert "config2->weights[i].firstseperator," in interbreed
	assert "configout->weights[i].firstseperator);" in interbreed
	assert "if (!InterbreedFuzzySeperator_r(fs2->child, fs2->child, fsout->child))" in weight_source
	assert 'botimport.Print(PRT_ERROR, "cannot interbreed weight configs, unequal child\\n");' in weight_source
	assert 'botimport.Print(PRT_ERROR, "cannot interbreed weight configs, unequal balance\\n");' in weight_source
	assert 'botimport.Print(PRT_ERROR, "cannot interbreed weight configs, unequal next\\n");' in weight_source
	assert 'botimport.Print(PRT_ERROR, "cannot interbreed weight configs, unequal numweights\\n");' in weight_source

	assert "004a7221  int32_t temp0 = divs.dp.d(sx.q(*(edi i+ (*esi << 2)) - ecx_3), *(esi[7] + 4) - ecx_3)" in hlil
	assert "004a72c0                  * (fconvert.t(esi[5]) - fconvert.t(esi[4])) + fconvert.t(esi[4]))" in hlil
	assert '004a7600          data_16dd800(3, "cannot interbreed weight configs' in hlil
	assert "004a75f2      if (sub_4a75c0(eax, eax, ecx_1) == 0)" in hlil


def test_botlib_weight_consumers_and_export_wiring_match_retail() -> None:
	ai_goal = BOTLIB_AI_GOAL.read_text(encoding="utf-8")
	ai_weap = BOTLIB_AI_WEAP.read_text(encoding="utf-8")
	interface = BOTLIB_INTERFACE.read_text(encoding="utf-8")
	public_api = BOTLIB_PUBLIC.read_text(encoding="utf-8")
	hlil = QL_STEAM_HLIL_PART03.read_text(encoding="utf-8")

	item_index = _extract_function_block(ai_goal, "int *ItemWeightIndex(weightconfig_t *iwc, itemconfig_t *ic)")
	load_items = _extract_function_block(ai_goal, "int BotLoadItemWeights(int goalstate, char *filename)")
	free_items = _extract_function_block(ai_goal, "void BotFreeItemWeights(int goalstate)")
	choose_ltg = _extract_function_block(
		ai_goal, "int BotChooseLTGItem(int goalstate, vec3_t origin, int *inventory, int travelflags)"
	)
	choose_nbg = _extract_function_block(
		ai_goal, "int BotChooseNBGItem(int goalstate, vec3_t origin, int *inventory, int travelflags,"
	)
	weapon_index = _extract_function_block(ai_weap, "int *WeaponWeightIndex(weightconfig_t *wwc, weaponconfig_t *wc)")
	load_weapons = _extract_function_block(ai_weap, "int BotLoadWeaponWeights(int weaponstate, char *filename)")
	choose_weapon = _extract_function_block(ai_weap, "int BotChooseBestFightWeapon(int weaponstate, int *inventory)")
	init_export = _extract_function_block(interface, "static void Init_AI_Export( ai_export_t *ai )")

	assert "index = (int *) GetClearedMemory(sizeof(int) * ic->numiteminfo);" in item_index
	assert "index[i] = FindFuzzyWeight(iwc, ic->iteminfo[i].classname);" in item_index
	assert 'Log_Write("item info %d \\"%s\\" has no fuzzy weight\\r\\n", i, ic->iteminfo[i].classname);' in item_index
	assert "gs->itemweightconfig = ReadWeightConfig(filename);" in load_items
	assert "botimport.Print(PRT_FATAL, \"couldn't load weights\\n\");" in load_items
	assert "if (!itemconfig) return BLERR_CANNOTLOADITEMWEIGHTS;" in load_items
	assert "gs->itemweightindex = ItemWeightIndex(gs->itemweightconfig, itemconfig);" in load_items
	assert "if (gs->itemweightconfig) FreeWeightConfig(gs->itemweightconfig);" in free_items
	assert "if (gs->itemweightindex) FreeMemory(gs->itemweightindex);" in free_items

	for block in (choose_ltg, choose_nbg):
		assert "if (!gs->itemweightconfig)" in block
		assert "weightnum = gs->itemweightindex[iteminfo->number];" in block
		assert "if (weightnum < 0)" in block
		assert "weight = FuzzyWeight(inventory, gs->itemweightconfig, weightnum);" in block
		assert "if (li->flags & IFL_ROAM) weight *= li->weight;" in block
		assert "weight /= (float) t * TRAVELTIME_SCALE;" in block

	assert "index = (int *) GetClearedMemory(sizeof(int) * wc->numweapons);" in weapon_index
	assert "index[i] = FindFuzzyWeight(wwc, wc->weaponinfo[i].name);" in weapon_index
	assert "BotFreeWeaponWeights(weaponstate);" in load_weapons
	assert "ws->weaponweightconfig = ReadWeightConfig(filename);" in load_weapons
	assert "botimport.Print(PRT_FATAL, \"couldn't load weapon config %s\\n\", filename);" in load_weapons
	assert "if (!weaponconfig) return BLERR_CANNOTLOADWEAPONCONFIG;" in load_weapons
	assert "ws->weaponweightindex = WeaponWeightIndex(ws->weaponweightconfig, weaponconfig);" in load_weapons
	assert "if (!ws->weaponweightconfig) return 0;" in choose_weapon
	assert "index = ws->weaponweightindex[i];" in choose_weapon
	assert "if (index < 0) continue;" in choose_weapon
	assert "weight = FuzzyWeight(inventory, ws->weaponweightconfig, index);" in choose_weapon

	for assignment in (
		"ai->BotLoadItemWeights = BotLoadItemWeights;",
		"ai->BotFreeItemWeights = BotFreeItemWeights;",
		"ai->BotInterbreedGoalFuzzyLogic = BotInterbreedGoalFuzzyLogic;",
		"ai->BotSaveGoalFuzzyLogic = BotSaveGoalFuzzyLogic;",
		"ai->BotMutateGoalFuzzyLogic = BotMutateGoalFuzzyLogic;",
		"ai->BotChooseBestFightWeapon = BotChooseBestFightWeapon;",
		"ai->BotLoadWeaponWeights = BotLoadWeaponWeights;",
	):
		assert assignment in init_export
		assert assignment.replace("ai->", "(*") not in init_export

	for declaration in (
		"int\t\t(*BotLoadItemWeights)(int goalstate, char *filename);",
		"void\t(*BotFreeItemWeights)(int goalstate);",
		"void\t(*BotInterbreedGoalFuzzyLogic)(int parent1, int parent2, int child);",
		"void\t(*BotSaveGoalFuzzyLogic)(int goalstate, char *filename);",
		"void\t(*BotMutateGoalFuzzyLogic)(int goalstate, float range);",
		"int\t\t(*BotChooseBestFightWeapon)(int weaponstate, int *inventory);",
		"int\t\t(*BotLoadWeaponWeights)(int weaponstate, char *filename);",
	):
		assert declaration in public_api

	for assignment in (
		"004a8299  arg1[0x31] = sub_49f6f0",
		"004a82a3  arg1[0x32] = sub_49f780",
		"004a82ad  arg1[0x33] = sub_49cc30",
		"004a82b7  arg1[0x34] = sub_49ccf0",
		"004a82c1  arg1[0x35] = sub_49cd30",
		"004a8357  arg1[0x44] = sub_4a6190",
		"004a836b  arg1[0x46] = sub_4a6060",
	):
		assert assignment in hlil
