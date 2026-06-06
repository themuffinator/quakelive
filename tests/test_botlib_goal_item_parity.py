from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

BOTLIB_AI_GOAL = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_goal.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
BOTLIB_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
GAME_AI_DMQ3 = REPO_ROOT / "src" / "code" / "game" / "ai_dmq3.c"
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


def _assert_function_row(functions_csv: str, address: str, size: int) -> None:
	row = f"FUN_00{address.lower()},00{address.lower()},{size},0,unknown"
	assert row in functions_csv


def _assert_order(text: str, *needles: str) -> None:
	position = -1
	for needle in needles:
		next_position = text.find(needle)
		assert next_position != -1, needle
		assert next_position > position, needle
		position = next_position


def test_goal_item_aliases_and_retail_function_rows_are_pinned() -> None:
	aliases = _aliases()
	functions = _read(QL_STEAM_FUNCTIONS)
	hlil = _read(QL_STEAM_HLIL_PART03)

	expected_aliases = {
		"49CD80": "BotLoadItemConfig",
		"49D010": "ItemWeightIndex",
		"49D080": "InitLevelItemHeap",
		"49D110": "BotFreeInfoEntities",
		"49D180": "BotInitInfoEntities",
		"49D3C0": "BotInitLevelItems",
		"49D940": "BotGoalName",
		"49D9B0": "BotResetAvoidGoals",
		"49DA20": "BotDumpAvoidGoals",
		"49DB00": "BotAddToAvoidGoals",
		"49DBA0": "BotRemoveFromAvoidGoals",
		"49DC40": "BotAvoidGoalTime",
		"49DD00": "BotSetAvoidGoalTime",
		"49DDF0": "BotGetLevelItemGoal",
		"49DF80": "BotGetMapLocationGoal",
		"49E000": "BotGetNextCampSpotGoal",
		"49E070": "BotUpdateEntityItems",
		"49E590": "BotDumpGoalStack",
		"49E870": "BotChooseLTGItem",
		"49EDA0": "BotChooseNBGItem",
	}
	expected_sizes = {
		"49CD80": 646,
		"49D010": 102,
		"49D080": 141,
		"49D110": 91,
		"49D180": 568,
		"49D3C0": 1395,
		"49D940": 99,
		"49D9B0": 109,
		"49DA20": 216,
		"49DB00": 147,
		"49DBA0": 148,
		"49DC40": 172,
		"49DD00": 233,
		"49DDF0": 395,
		"49DF80": 122,
		"49E000": 110,
		"49E070": 1292,
		"49E590": 181,
		"49E870": 1315,
		"49EDA0": 1562,
	}

	for address, name in expected_aliases.items():
		assert aliases[f"sub_{address}"] == name
		_assert_function_row(functions, address, expected_sizes[address])

	for evidence in (
		"0049cd80    char* sub_49cd80(int32_t arg1)",
		"0049d010    char* sub_49d010(int32_t* arg1, char* arg2)",
		"0049d03d      int32_t eax_3 = sub_4a7140(arg1, edi[1] + ebx_1)",
		"0049d080    char* sub_49d080()",
		'0049d0a3  int32_t eax = sub_526000(sub_4a8770("max_levelitems", "256"))',
		"0049d110    void* sub_49d110()",
		"0049d180    int32_t sub_49d180()",
		"0049d195  sub_49d110()",
		"0049d3c0    char* sub_49d3c0()",
		"0049d3d5  sub_49d180()",
		"0049d3da  char* eax_2 = sub_49d080()",
		'0049d922          eax_2 = data_16dd800(1, "found %d level items\\n", data_e49fa4)',
		"0049db00    int32_t* sub_49db00(void* arg1, int32_t arg2, float arg3)",
		"0049dd00    int32_t* sub_49dd00(int32_t* arg1, int32_t arg2, float arg3)",
		"0049e070    void sub_49e070()",
		"0049e0e7                  *(i_2 + 0x38) = data_e49f9c",
		"0049e4de                                                  int32_t eax_27 = sub_491ea0(&esi_2[0x10],",
		"0049e870    int32_t sub_49e870(int32_t arg1, float* arg2, int32_t arg3, int32_t arg4)",
		"0049eda0    int32_t sub_49eda0(int32_t arg1, float* arg2, int32_t arg3, int32_t arg4, void* arg5)",
		"004a8271  arg1[0x2d] = sub_49dc40",
		"004a827b  arg1[0x2e] = sub_49dd00",
		"004a8285  arg1[0x2f] = sub_49d3c0",
		"004a828f  arg1[0x30] = sub_49e070",
		"004a8299  arg1[0x31] = sub_49f6f0",
		"004a82a3  arg1[0x32] = sub_49f780",
	):
		assert evidence in hlil


def test_goal_item_config_heap_and_info_entity_source_match_retail_shape() -> None:
	source = _read(BOTLIB_AI_GOAL)

	load_config = _extract_function_block(source, "itemconfig_t *LoadItemConfig(char *filename)")
	item_index = _extract_function_block(source, "int *ItemWeightIndex(weightconfig_t *iwc, itemconfig_t *ic)")
	init_heap = _extract_function_block(source, "void InitLevelItemHeap(void)")
	alloc_item = _extract_function_block(source, "levelitem_t *AllocLevelItem(void)")
	free_item = _extract_function_block(source, "void FreeLevelItem(levelitem_t *li)")
	add_item = _extract_function_block(source, "void AddLevelItemToList(levelitem_t *li)")
	remove_item = _extract_function_block(source, "void RemoveLevelItemFromList(levelitem_t *li)")
	free_info = _extract_function_block(source, "void BotFreeInfoEntities(void)")
	init_info = _extract_function_block(source, "void BotInitInfoEntities(void)")
	init_level = _extract_function_block(source, "void BotInitLevelItems(void)")

	assert "max_iteminfo = (int) LibVarValue(\"max_iteminfo\", \"256\");" in load_config
	assert 'botimport.Print(PRT_ERROR, "max_iteminfo = %d\\n", max_iteminfo);' in load_config
	assert 'LibVarSet( "max_iteminfo", "256" );' in load_config
	assert "PC_SetBaseFolder(BOTFILESBASEFOLDER);" in load_config
	assert "source = LoadSourceFile( path );" in load_config
	assert 'botimport.Print( PRT_ERROR, "counldn\'t load %s\\n", path );' in load_config
	assert "ic = (itemconfig_t *) GetClearedHunkMemory(sizeof(itemconfig_t) +" in load_config
	assert 'if (!strcmp(token.string, "iteminfo"))' in load_config
	assert 'SourceError(source, "more than %d item info defined\\n", max_iteminfo);' in load_config
	assert "ReadStructure(source, &iteminfo_struct, (char *) ii)" in load_config
	assert 'SourceError(source, "unknown definition %s\\n", token.string);' in load_config
	assert 'botimport.Print(PRT_WARNING, "no item info loaded\\n");' in load_config
	assert 'botimport.Print(PRT_MESSAGE, "loaded %s\\n", path);' in load_config

	assert "index = (int *) GetClearedMemory(sizeof(int) * ic->numiteminfo);" in item_index
	assert "index[i] = FindFuzzyWeight(iwc, ic->iteminfo[i].classname);" in item_index
	assert 'Log_Write("item info %d \\"%s\\" has no fuzzy weight\\r\\n", i, ic->iteminfo[i].classname);' in item_index

	assert "if (levelitemheap) FreeMemory(levelitemheap);" in init_heap
	assert 'max_levelitems = (int) LibVarValue("max_levelitems", "256");' in init_heap
	assert "levelitemheap = (levelitem_t *) GetClearedMemory(max_levelitems * sizeof(levelitem_t));" in init_heap
	assert "levelitemheap[i].next = &levelitemheap[i + 1];" in init_heap
	assert "freelevelitems = levelitemheap;" in init_heap
	assert 'botimport.Print(PRT_FATAL, "out of level items\\n");' in alloc_item
	assert "freelevelitems = freelevelitems->next;" in alloc_item
	assert "Com_Memset(li, 0, sizeof(levelitem_t));" in alloc_item
	assert "li->next = freelevelitems;" in free_item
	assert "freelevelitems = li;" in free_item
	assert "if (levelitems) levelitems->prev = li;" in add_item
	assert "levelitems = li;" in add_item
	assert "if (li->prev) li->prev->next = li->next;" in remove_item
	assert "if (li->next) li->next->prev = li->prev;" in remove_item

	assert "for (ml = maplocations; ml; ml = nextml)" in free_info
	assert "FreeMemory(ml);" in free_info
	assert "maplocations = NULL;" in free_info
	assert "for (cs = campspots; cs; cs = nextcs)" in free_info
	assert "FreeMemory(cs);" in free_info
	assert "campspots = NULL;" in free_info
	assert "BotFreeInfoEntities();" in init_info
	assert "for (ent = AAS_NextBSPEntity(0); ent; ent = AAS_NextBSPEntity(ent))" in init_info
	assert 'if (!AAS_ValueForBSPEpairKey(ent, "classname", classname, MAX_EPAIRKEY)) continue;' in init_info
	assert 'if (!strcmp(classname, "target_location"))' in init_info
	assert "AAS_VectorForBSPEpairKey(ent, \"origin\", ml->origin);" in init_info
	assert "ml->areanum = AAS_PointAreaNum(ml->origin);" in init_info
	assert 'else if (!strcmp(classname, "info_camp"))' in init_info
	assert 'AAS_FloatForBSPEpairKey(ent, "range", &cs->range);' in init_info
	assert 'botimport.Print(PRT_MESSAGE, "camp spot at %1.1f %1.1f %1.1f in solid\\n",' in init_info
	assert 'botimport.Print(PRT_MESSAGE, "%d map locations\\n", numlocations);' in init_info
	assert 'botimport.Print(PRT_MESSAGE, "%d camp spots\\n", numcampspots);' in init_info

	assert "BotInitInfoEntities();" in init_level
	assert "InitLevelItemHeap();" in init_level
	assert "levelitems = NULL;" in init_level
	assert "numlevelitems = 0;" in init_level
	assert "if (!AAS_Loaded()) return;" in init_level
	assert 'Log_Write("item %s has modelindex 0", ic->iteminfo[i].classname);' in init_level
	assert "for (ent = AAS_NextBSPEntity(0); ent; ent = AAS_NextBSPEntity(ent))" in init_level
	assert 'AAS_IntForBSPEpairKey(ent, "spawnflags", &spawnflags);' in init_level
	assert 'Log_Write("entity %s unknown item\\r\\n", classname);' in init_level
	assert 'botimport.Print(PRT_ERROR, "item %s without origin\\n", classname);' in init_level
	assert "goalareanum = AAS_BestReachableFromJumpPadArea(origin, ic->iteminfo[i].mins, ic->iteminfo[i].maxs);" in init_level
	assert "li = AllocLevelItem();" in init_level
	assert 'if (!strcmp(classname, "item_botroam"))' in init_level
	assert "li->flags |= IFL_ROAM;" in init_level
	assert 'AAS_FloatForBSPEpairKey(ent, "weight", &li->weight);' in init_level
	assert "li->goalareanum = AAS_BestReachableArea(origin," in init_level
	assert "AddLevelItemToList(li);" in init_level
	assert 'botimport.Print(PRT_MESSAGE, "found %d level items\\n", numlevelitems);' in init_level


def test_goal_item_update_avoid_and_selection_source_match_retail_shape() -> None:
	source = _read(BOTLIB_AI_GOAL)

	goal_name = _extract_function_block(source, "void BotGoalName(int number, char *name, int size)")
	add_avoid = _extract_function_block(source, "void BotAddToAvoidGoals(bot_goalstate_t *gs, int number, float avoidtime)")
	remove_avoid = _extract_function_block(source, "void BotRemoveFromAvoidGoals(int goalstate, int number)")
	avoid_time = _extract_function_block(source, "float BotAvoidGoalTime(int goalstate, int number)")
	set_avoid = _extract_function_block(source, "void BotSetAvoidGoalTime(int goalstate, int number, float avoidtime)")
	find_entity = _extract_function_block(source, "void BotFindEntityForLevelItem(levelitem_t *li)")
	update_items = _extract_function_block(source, "void BotUpdateEntityItems(void)")
	choose_ltg = _extract_function_block(
		source, "int BotChooseLTGItem(int goalstate, vec3_t origin, int *inventory, int travelflags)"
	)
	choose_nbg = _extract_function_block(
		source, "int BotChooseNBGItem(int goalstate, vec3_t origin, int *inventory, int travelflags,"
	)

	assert "strncpy(name, itemconfig->iteminfo[li->iteminfo].name, size-1);" in goal_name
	assert "name[size-1] = '\\0';" in goal_name
	assert 'strcpy(name, "");' in goal_name
	assert "if (gs->avoidgoals[i] == number)" in add_avoid
	assert "gs->avoidgoaltimes[i] = AAS_Time() + avoidtime;" in add_avoid
	assert "if (gs->avoidgoaltimes[i] < AAS_Time())" in add_avoid
	assert "if (gs->avoidgoals[i] == number && gs->avoidgoaltimes[i] >= AAS_Time())" in remove_avoid
	assert "gs->avoidgoaltimes[i] = 0;" in remove_avoid
	assert "return gs->avoidgoaltimes[i] - AAS_Time();" in avoid_time
	assert "if (avoidtime < 0)" in set_avoid
	assert "avoidtime = itemconfig->iteminfo[li->iteminfo].respawntime;" in set_avoid
	assert "avoidtime = AVOID_DEFAULT_TIME;" in set_avoid
	assert "avoidtime = AVOID_MINIMUM_TIME;" in set_avoid
	assert "BotAddToAvoidGoals(gs, number, avoidtime);" in set_avoid

	assert "for (ent = AAS_NextEntity(0); ent; ent = AAS_NextEntity(ent))" in find_entity
	assert "modelindex = AAS_EntityModelindex(ent);" in find_entity
	assert "AAS_EntityInfo(ent, &entinfo);" in find_entity
	assert "VectorSubtract(li->origin, entinfo.origin, dir);" in find_entity
	assert "if (VectorLength(dir) < 30)" in find_entity
	assert "li->entitynum = ent;" in find_entity

	assert "for (li = levelitems; li; li = nextli)" in update_items
	assert "if (li->timeout < AAS_Time())" in update_items
	assert "RemoveLevelItemFromList(li);" in update_items
	assert "FreeLevelItem(li);" in update_items
	assert "if (AAS_EntityType(ent) != ET_ITEM) continue;" in update_items
	assert "modelindex = AAS_EntityModelindex(ent);" in update_items
	assert "AAS_EntityInfo(ent, &entinfo);" in update_items
	assert "if (li->entitynum && li->entitynum == ent)" in update_items
	assert "if (ic->iteminfo[li->iteminfo].modelindex != modelindex)" in update_items
	assert "VectorCopy(entinfo.origin, li->origin);" in update_items
	assert "li->goalareanum = AAS_BestReachableArea(li->origin," in update_items
	assert "if (li->entitynum) continue;" in update_items
	assert "if (VectorLength(dir) < 30)" in update_items
	assert "li = AllocLevelItem();" in update_items
	assert "li->number = numlevelitems + ent;" in update_items
	assert "if (AAS_AreaJumpPad(li->goalareanum))" in update_items
	assert "li->timeout = AAS_Time() + 30;" in update_items
	assert "AddLevelItemToList(li);" in update_items

	for block in (choose_ltg, choose_nbg):
		assert "gs = BotGoalStateFromHandle(goalstate);" in block
		assert "if (!gs->itemweightconfig)" in block
		assert "areanum = BotReachabilityArea(origin, gs->client);" in block
		assert "gs->lastreachabilityarea = areanum;" in block
		assert "for (li = levelitems; li; li = li->next)" in block
		assert "if (li->flags & IFL_NOTBOT)" in block
		assert "if (!li->goalareanum)" in block
		assert "if (!li->entitynum && !(li->flags & IFL_ROAM))" in block
		assert "weightnum = gs->itemweightindex[iteminfo->number];" in block
		assert "weight = FuzzyWeight(inventory, gs->itemweightconfig, weightnum);" in block
		assert "if (li->flags & IFL_ROAM) weight *= li->weight;" in block
		assert "avoidtime = BotAvoidGoalTime(goalstate, li->number);" in block
		assert "if (avoidtime - t * 0.009 > 0)" in block
		assert "weight /= (float) t * TRAVELTIME_SCALE;" in block
		assert "goal.flags = GFL_ITEM;" in block
		assert "goal.flags |= GFL_DROPPED;" in block
		assert "goal.flags |= GFL_ROAM;" in block
		assert "BotAddToAvoidGoals(gs, bestitem->number, avoidtime);" in block
		assert "BotPushGoal(goalstate, &goal);" in block

	assert "if (ltg) ltg_time = AAS_AreaTravelTimeToGoalArea(areanum, origin, ltg->areanum, travelflags);" in choose_nbg
	assert "if (t > 0 && t < maxtime)" in choose_nbg
	assert "t = AAS_AreaTravelTimeToGoalArea(li->goalareanum, li->goalorigin, ltg->areanum, travelflags);" in choose_nbg
	assert "if (t <= ltg_time)" in choose_nbg


def test_goal_item_api_export_import_and_qagame_consumers_are_pinned() -> None:
	interface = _read(BOTLIB_INTERFACE)
	public_api = _read(BOTLIB_PUBLIC)
	g_public = _read(GAME_G_PUBLIC)
	g_local = _read(GAME_G_LOCAL)
	g_syscalls = _read(GAME_SYSCALLS)
	server_game = _read(SERVER_GAME)
	server_imports = _read(SERVER_QL_GAME_IMPORTS)
	ai_dmq3 = _read(GAME_AI_DMQ3)
	hlil = _read(QL_STEAM_HLIL_PART03)

	init_export = _extract_function_block(interface, "static void Init_AI_Export( ai_export_t *ai )")
	load_map = _extract_function_block(interface, "int Export_BotLibLoadMap(const char *mapname)")
	syscall_avoid_time = _extract_function_block(g_syscalls, "float trap_BotAvoidGoalTime(int goalstate, int number)")
	dont_avoid = _extract_function_block(ai_dmq3, "void BotDontAvoid(bot_state_t *bs, char *itemname)")

	_assert_order(
		public_api,
		"void\t(*BotResetAvoidGoals)(int goalstate);",
		"void\t(*BotRemoveFromAvoidGoals)(int goalstate, int number);",
		"void\t(*BotDumpAvoidGoals)(int goalstate);",
		"void\t(*BotGoalName)(int number, char *name, int size);",
		"int\t\t(*BotChooseLTGItem)(int goalstate, vec3_t origin, int *inventory, int travelflags);",
		"int\t\t(*BotChooseNBGItem)(int goalstate, vec3_t origin, int *inventory, int travelflags,",
		"int\t\t(*BotGetLevelItemGoal)(int index, char *classname, struct bot_goal_s *goal);",
		"int\t\t(*BotGetNextCampSpotGoal)(int num, struct bot_goal_s *goal);",
		"int\t\t(*BotGetMapLocationGoal)(char *name, struct bot_goal_s *goal);",
		"float\t(*BotAvoidGoalTime)(int goalstate, int number);",
		"void\t(*BotSetAvoidGoalTime)(int goalstate, int number, float avoidtime);",
		"void\t(*BotInitLevelItems)(void);",
		"void\t(*BotUpdateEntityItems)(void);",
		"int\t\t(*BotLoadItemWeights)(int goalstate, char *filename);",
		"void\t(*BotFreeItemWeights)(int goalstate);",
	)
	_assert_order(
		init_export,
		"ai->BotResetAvoidGoals = BotResetAvoidGoals;",
		"ai->BotRemoveFromAvoidGoals = BotRemoveFromAvoidGoals;",
		"ai->BotDumpAvoidGoals = BotDumpAvoidGoals;",
		"ai->BotGoalName = BotGoalName;",
		"ai->BotChooseLTGItem = BotChooseLTGItem;",
		"ai->BotChooseNBGItem = BotChooseNBGItem;",
		"ai->BotGetLevelItemGoal = BotGetLevelItemGoal;",
		"ai->BotGetNextCampSpotGoal = BotGetNextCampSpotGoal;",
		"ai->BotGetMapLocationGoal = BotGetMapLocationGoal;",
		"ai->BotAvoidGoalTime = BotAvoidGoalTime;",
		"ai->BotSetAvoidGoalTime = BotSetAvoidGoalTime;",
		"ai->BotInitLevelItems = BotInitLevelItems;",
		"ai->BotUpdateEntityItems = BotUpdateEntityItems;",
		"ai->BotLoadItemWeights = BotLoadItemWeights;",
		"ai->BotFreeItemWeights = BotFreeItemWeights;",
	)
	assert "BotInitLevelItems();\t\t//be_ai_goal.h" in load_map
	assert "BotSetBrushModelTypes();" in load_map

	for legacy_name in (
		"BOTLIB_AI_CHOOSE_LTG_ITEM",
		"BOTLIB_AI_CHOOSE_NBG_ITEM",
		"BOTLIB_AI_GET_LEVEL_ITEM_GOAL",
		"BOTLIB_AI_AVOID_GOAL_TIME",
		"BOTLIB_AI_INIT_LEVEL_ITEMS",
		"BOTLIB_AI_UPDATE_ENTITY_ITEMS",
		"BOTLIB_AI_LOAD_ITEM_WEIGHTS",
		"BOTLIB_AI_FREE_ITEM_WEIGHTS",
		"BOTLIB_AI_GET_NEXT_CAMP_SPOT_GOAL",
		"BOTLIB_AI_GET_MAP_LOCATION_GOAL",
		"BOTLIB_AI_SET_AVOID_GOAL_TIME",
	):
		assert legacy_name in g_public
		assert f"case {legacy_name}: return G_QL_IMPORT_{legacy_name};" in g_syscalls

	assert "\tG_QL_IMPORT_BOTLIB_AI_GET_MAP_LOCATION_GOAL = 153," in g_public
	assert "\tG_QL_IMPORT_BOTLIB_AI_AVOID_GOAL_TIME = 155," in g_public
	assert "\tG_QL_IMPORT_BOTLIB_AI_SET_AVOID_GOAL_TIME = 156," in g_public
	assert "\tG_QL_IMPORT_BOTLIB_AI_INIT_LEVEL_ITEMS = 157," in g_public
	assert "\tG_QL_IMPORT_BOTLIB_AI_UPDATE_ENTITY_ITEMS = 158," in g_public
	assert "\tG_QL_IMPORT_BOTLIB_AI_LOAD_ITEM_WEIGHTS = 159," in g_public
	assert "\tG_QL_IMPORT_BOTLIB_AI_FREE_ITEM_WEIGHTS = 160," in g_public
	assert "void\ttrap_BotInitLevelItems(void);" in g_local
	assert "void\ttrap_BotUpdateEntityItems(void);" in g_local
	assert "float\ttrap_BotAvoidGoalTime(int goalstate, int number);" in g_local
	assert "void\ttrap_BotSetAvoidGoalTime(int goalstate, int number, float avoidtime);" in g_local
	assert "G_GetMappedImport( BOTLIB_AI_AVOID_GOAL_TIME, NULL )" in syscall_avoid_time
	assert "temp = syscall( BOTLIB_AI_AVOID_GOAL_TIME, goalstate, number );" in syscall_avoid_time
	assert "syscall( BOTLIB_AI_SET_AVOID_GOAL_TIME, goalstate, number, PASSFLOAT(avoidtime));" in g_syscalls
	assert "syscall( BOTLIB_AI_INIT_LEVEL_ITEMS );" in g_syscalls
	assert "syscall( BOTLIB_AI_UPDATE_ENTITY_ITEMS );" in g_syscalls
	assert "return syscall( BOTLIB_AI_LOAD_ITEM_WEIGHTS, goalstate, filename );" in g_syscalls
	assert "syscall( BOTLIB_AI_FREE_ITEM_WEIGHTS, goalstate );" in g_syscalls

	assert "return botlib_export->ai.BotChooseLTGItem( args[1], VMA(2), VMA(3), args[4] );" in server_game
	assert "return botlib_export->ai.BotChooseNBGItem( args[1], VMA(2), VMA(3), args[4], VMA(5), VMF(6) );" in server_game
	assert "return FloatAsInt( botlib_export->ai.BotAvoidGoalTime( args[1], args[2] ) );" in server_game
	assert "botlib_export->ai.BotSetAvoidGoalTime( args[1], args[2], VMF(3));" in server_game
	assert "botlib_export->ai.BotInitLevelItems();" in server_game
	assert "botlib_export->ai.BotUpdateEntityItems();" in server_game
	assert "return botlib_export->ai.BotLoadItemWeights( args[1], VMA(2) );" in server_game
	assert "botlib_export->ai.BotFreeItemWeights( args[1] );" in server_game
	assert "[BOTLIB_AI_CHOOSE_LTG_ITEM] = (ql_import_f)QL_G_trap_BotChooseLTGItem," in server_game
	assert "[BOTLIB_AI_AVOID_GOAL_TIME] = (ql_import_f)QL_G_trap_BotAvoidGoalTime," in server_game
	assert "[BOTLIB_AI_UPDATE_ENTITY_ITEMS] = (ql_import_f)QL_G_trap_BotUpdateEntityItems," in server_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_INIT_LEVEL_ITEMS] = (ql_import_f)QL_G_trap_BotInitLevelItems;" in server_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_AI_FREE_ITEM_WEIGHTS] = (ql_import_f)QL_G_trap_BotFreeItemWeights;" in server_game

	assert "return G_Import_Syscall( BOTLIB_AI_CHOOSE_LTG_ITEM, goalstate, origin, inventory, travelflags );" in server_imports
	assert "return G_Import_Syscall( BOTLIB_AI_CHOOSE_NBG_ITEM, goalstate, origin, inventory, travelflags, ltg, QL_G_PASSFLOAT(maxtime) );" in server_imports
	assert "temp = G_Import_Syscall( BOTLIB_AI_AVOID_GOAL_TIME, goalstate, number );" in server_imports
	assert "G_Import_Syscall( BOTLIB_AI_SET_AVOID_GOAL_TIME, goalstate, number, QL_G_PASSFLOAT(avoidtime));" in server_imports
	assert "G_Import_Syscall( BOTLIB_AI_INIT_LEVEL_ITEMS );" in server_imports
	assert "G_Import_Syscall( BOTLIB_AI_UPDATE_ENTITY_ITEMS );" in server_imports
	assert "return G_Import_Syscall( BOTLIB_AI_LOAD_ITEM_WEIGHTS, goalstate, filename );" in server_imports
	assert "G_Import_Syscall( BOTLIB_AI_FREE_ITEM_WEIGHTS, goalstate );" in server_imports

	assert "for (cs = trap_BotGetNextCampSpotGoal(0, &goal); cs; cs = trap_BotGetNextCampSpotGoal(cs, &goal))" in ai_dmq3
	assert "num = trap_BotGetLevelItemGoal(-1, itemname, &goal);" in dont_avoid
	assert "trap_BotRemoveFromAvoidGoals(bs->gs, goal.number);" in dont_avoid
	assert "num = trap_BotGetLevelItemGoal(num, itemname, &goal);" in dont_avoid

	for evidence in (
		"004a822b  arg1[0x26] = sub_49e870",
		"004a8235  arg1[0x27] = sub_49eda0",
		"004a823f  arg1[0x28] = sub_49f3c0",
		"004a8253  arg1[0x2a] = sub_49ddf0",
		"004a825d  arg1[0x2b] = sub_49e000",
		"004a8267  arg1[0x2c] = sub_49df80",
		"004a8271  arg1[0x2d] = sub_49dc40",
		"004a827b  arg1[0x2e] = sub_49dd00",
		"004a8285  arg1[0x2f] = sub_49d3c0",
		"004a828f  arg1[0x30] = sub_49e070",
	):
		assert evidence in hlil
