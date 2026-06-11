"""Guard retail-backed cgame sound command and announcer queue wiring."""

from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_DRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_ENTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_ents.c"
CG_EVENT = REPO_ROOT / "src" / "code" / "cgame" / "cg_event.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CG_LOCALENTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_localents.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_PLAYERS = REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c"
CG_PLAYERSTATE = REPO_ROOT / "src" / "code" / "cgame" / "cg_playerstate.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CG_SYSCALLS = REPO_ROOT / "src" / "code" / "cgame" / "cg_syscalls.c"
CG_VIEW = REPO_ROOT / "src" / "code" / "cgame" / "cg_view.c"
CG_WEAPONS = REPO_ROOT / "src" / "code" / "cgame" / "cg_weapons.c"
UI_SHARED = REPO_ROOT / "src" / "code" / "ui" / "ui_shared.c"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
CGAME_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "cgamex86"
	/ "functions.csv"
)
CGAME_DECOMPILE = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "cgamex86"
	/ "decompile_top_functions.c"
)
CGAME_HLIL = REPO_ROOT / "references" / "hlil" / "quakelive" / "cgamex86.dll" / "cgamex86.dll_hlil.txt"


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _block_from_marker(source: str, marker: str) -> str:
	start = source.rindex(marker)
	brace_start = source.index("{", start)
	depth = 0

	for index in range(brace_start, len(source)):
		char = source[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start:index + 1]

	raise AssertionError(f"Unbalanced block for marker: {marker}")


def _slice_between(source: str, start_marker: str, end_marker: str) -> str:
	start = source.index(start_marker)
	end = source.index(end_marker, start)
	return source[start:end]


def _function_rows() -> dict[str, dict[str, str]]:
	return {
		row["entry"].lower(): row
		for row in csv.DictReader(CGAME_FUNCTIONS.read_text(encoding="utf-8").splitlines())
	}


def _assert_order(block: str, *needles: str) -> None:
	cursor = 0
	for needle in needles:
		index = block.find(needle, cursor)
		if index == -1:
			raise AssertionError(f"expected ordered snippet not found after {cursor}: {needle}")
		cursor = index + len(needle)


def test_cgame_sound_helper_aliases_and_function_table_match_retail_offsets() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))["cgame"]
	rows = _function_rows()

	expected_aliases = {
		"FUN_1003ca30": "CG_CustomSound",
		"sub_1003ca30": "CG_CustomSound",
		"FUN_1004e050": "CG_PowerupTimerSounds",
		"sub_1004e050": "CG_PowerupTimerSounds",
		"FUN_1004e110": "CG_AddBufferedSound",
		"sub_1004e110": "CG_AddBufferedSound",
		"FUN_1004e180": "CG_ClearBufferedAnnouncements",
		"sub_1004e180": "CG_ClearBufferedAnnouncements",
		"FUN_1004e220": "CG_PlayBufferedSounds",
		"sub_1004e220": "CG_PlayBufferedSounds",
		"FUN_1000eb30": "CG_PlayWarmupCountSound",
		"sub_1000eb30": "CG_PlayWarmupCountSound",
		"FUN_10015450": "CG_SetEntitySoundPosition",
		"sub_10015450": "CG_SetEntitySoundPosition",
		"FUN_10015500": "CG_EntityEffects",
		"sub_10015500": "CG_EntityEffects",
		"FUN_100175f0": "CG_Missile",
		"FUN_10019af0": "CG_UseItem",
		"sub_10019af0": "CG_UseItem",
		"FUN_10019c40": "CG_ItemPickup",
		"sub_10019c40": "CG_ItemPickup",
		"FUN_10019ca0": "CG_PainEvent",
		"sub_10019ca0": "CG_PainEvent",
		"FUN_10019eb0": "CG_EntityEvent",
		"sub_10019eb0": "CG_EntityEvent",
		"FUN_10018ae0": "CG_AddCEntity",
		"sub_10018ae0": "CG_AddCEntity",
		"FUN_1001ec10": "CG_FragmentBounceSound",
		"sub_1001ec10": "CG_FragmentBounceSound",
		"FUN_10020dd0": "CG_BuildAnnouncerSoundPath",
		"sub_10020dd0": "CG_BuildAnnouncerSoundPath",
		"FUN_10020e70": "CG_RegisterSounds",
		"sub_10020e70": "CG_RegisterSounds",
		"FUN_10025320": "CG_StartMusic",
		"sub_10025320": "CG_StartMusic",
		"FUN_10042e50": "CG_CheckAmmo",
		"sub_10042e50": "CG_CheckAmmo",
		"FUN_100435b0": "CG_CheckLocalSounds",
		"sub_100435b0": "CG_CheckLocalSounds",
		"FUN_10052250": "CG_MachinegunSpinAngle",
		"sub_10052250": "CG_MachinegunSpinAngle",
		"FUN_10052420": "CG_AddPlayerWeapon",
		"sub_10052420": "CG_AddPlayerWeapon",
		"FUN_10053de0": "CG_FireWeapon",
		"sub_10053de0": "CG_FireWeapon",
		"FUN_10053ef0": "CG_MissileHitWall",
		"sub_10053ef0": "CG_MissileHitWall",
		"FUN_10054db0": "CG_MissileHitWallDmgThrough",
		"sub_10054db0": "CG_MissileHitWallDmgThrough",
		"FUN_10055c00": "CG_Tracer",
		"sub_10055c00": "CG_Tracer",
		"FUN_1004a560": "CG_HeadModelVoiceChats",
		"sub_1004a560": "CG_HeadModelVoiceChats",
		"FUN_1004a6a0": "CG_GetVoiceChat",
		"sub_1004a6a0": "CG_GetVoiceChat",
		"FUN_1004a740": "CG_VoiceChatListForClient",
		"sub_1004a740": "CG_VoiceChatListForClient",
		"FUN_1004aac0": "CG_PlayVoiceChat",
		"sub_1004aac0": "CG_PlayVoiceChat",
		"FUN_1004abc0": "CG_PlayBufferedVoiceChats",
		"sub_1004abc0": "CG_PlayBufferedVoiceChats",
		"FUN_1004ac30": "CG_AddBufferedVoiceChat",
		"sub_1004ac30": "CG_AddBufferedVoiceChat",
		"FUN_1004ac90": "CG_VoiceChatLocal",
		"sub_1004ac90": "CG_VoiceChatLocal",
		"sub_10059eb0": "CG_BrowserScriptPlay",
		"sub_10059f00": "CG_BrowserScriptPlayLooped",
		"FUN_10059f50": "CG_RunBrowserScript",
		"sub_10059f50": "CG_RunBrowserScript",
		"FUN_10060e20": "CG_BrowserItemParseFocusSound",
		"sub_10060e20": "CG_BrowserItemParseFocusSound",
		"FUN_10063010": "CG_BrowserMenuParseSoundLoop",
		"sub_10063010": "CG_BrowserMenuParseSoundLoop",
	}
	for symbol, expected_name in expected_aliases.items():
		assert aliases[symbol] == expected_name

	expected_rows = {
		"1000eb30": ("FUN_1000eb30", "151"),
		"10015450": ("FUN_10015450", "168"),
		"10015500": ("FUN_10015500", "201"),
		"100175f0": ("FUN_100175f0", "749"),
		"10019af0": ("FUN_10019af0", "325"),
		"10019c40": ("FUN_10019c40", "94"),
		"10019ca0": ("FUN_10019ca0", "127"),
		"10019eb0": ("FUN_10019eb0", "10088"),
		"10018ae0": ("FUN_10018ae0", "202"),
		"1001ec10": ("FUN_1001ec10", "190"),
		"10020dd0": ("FUN_10020dd0", "122"),
		"10020e70": ("FUN_10020e70", "8324"),
		"10025320": ("FUN_10025320", "196"),
		"1003ca30": ("FUN_1003ca30", "156"),
		"10042e50": ("FUN_10042e50", "183"),
		"100435b0": ("FUN_100435b0", "1420"),
		"10052250": ("FUN_10052250", "242"),
		"10052420": ("FUN_10052420", "2231"),
		"10053de0": ("FUN_10053de0", "266"),
		"10053ef0": ("FUN_10053ef0", "3471"),
		"10054db0": ("FUN_10054db0", "1657"),
		"10055c00": ("FUN_10055c00", "951"),
		"1004a560": ("FUN_1004a560", "314"),
		"1004a6a0": ("FUN_1004a6a0", "156"),
		"1004a740": ("FUN_1004a740", "872"),
		"1004aac0": ("FUN_1004aac0", "250"),
		"1004abc0": ("FUN_1004abc0", "97"),
		"1004ac30": ("FUN_1004ac30", "95"),
		"1004ac90": ("FUN_1004ac90", "241"),
		"1004e050": ("FUN_1004e050", "180"),
		"1004e110": ("FUN_1004e110", "109"),
		"1004e180": ("FUN_1004e180", "153"),
		"1004e220": ("FUN_1004e220", "182"),
		"10059f50": ("FUN_10059f50", "246"),
		"10060e20": ("FUN_10060e20", "171"),
		"10063010": ("FUN_10063010", "153"),
	}
	for address, (name, size) in expected_rows.items():
		assert rows[address]["name"] == name
		assert rows[address]["size"] == size


def test_cgame_browser_sound_parser_wiring_pins_focus_and_loop_tokens() -> None:
	alias_sections = json.loads(_read(SYMBOL_ALIASES))
	aliases = alias_sections["cgame"]
	ui_aliases = alias_sections["ui"]
	rows = _function_rows()
	hlil = _read(CGAME_HLIL)
	main_source = _read(CG_MAIN)
	newdraw_source = _read(CG_NEWDRAW)
	ui_shared = _read(UI_SHARED)
	item_focus_block = _block_from_marker(ui_shared, "qboolean ItemParse_focusSound")
	item_text_block = _block_from_marker(ui_shared, "qboolean ItemParse_text( itemDef_t")
	menu_loop_block = _block_from_marker(ui_shared, "qboolean MenuParse_soundLoop")
	activate_block = _block_from_marker(ui_shared, "void  Menus_Activate")
	cache_block = _block_from_marker(ui_shared, "static void Menu_CacheContents")
	browser_focus_block = _block_from_marker(newdraw_source, "static qboolean CG_SetBrowserFocus")
	setup_item_block = _block_from_marker(main_source, "void CG_SetupBrowserItemKeywordHash")
	parse_item_block = _block_from_marker(main_source, "qboolean CG_ParseBrowserItem")
	setup_menu_block = _block_from_marker(main_source, "void CG_SetupBrowserMenuKeywordHash")
	parse_menu_block = _block_from_marker(main_source, "qboolean CG_ParseBrowserMenu")
	init_runtime_block = _block_from_marker(main_source, "void CG_InitBrowserRuntime")

	assert ui_aliases["FUN_1001dc00"] == "ItemParse_focusSound"
	assert ui_aliases["FUN_1001fed0"] == "Parse_text_or_soundLoop"
	assert "sub_1001dc00" not in ui_aliases
	assert "sub_1001fed0" not in ui_aliases
	assert aliases["FUN_10060e20"] == "CG_BrowserItemParseFocusSound"
	assert aliases["sub_10060e20"] == "CG_BrowserItemParseFocusSound"
	assert aliases["FUN_10063010"] == "CG_BrowserMenuParseSoundLoop"
	assert aliases["sub_10063010"] == "CG_BrowserMenuParseSoundLoop"
	assert rows["10060e20"]["name"] == "FUN_10060e20"
	assert rows["10060e20"]["size"] == "171"
	assert rows["10063010"]["name"] == "FUN_10063010"
	assert rows["10063010"]["size"] == "153"

	for expected in (
		"10060e20    int32_t sub_10060e20(void* arg1, int32_t arg2)",
		"10060e5b  if ((*(data_1074cccc + 0x1b8))(arg2, &var_420) == 0)",
		"10060e6b  sub_10057330(\"NULL\", 0x1869f, &var_410)",
		"10060e8d  *(arg1 + 0x188) = (*(data_1074ccf8 + 0xac))(sub_10057830())",
		"10060eae  return 1",
		"10063010    int32_t sub_10063010(void* arg1, int32_t arg2)",
		"1006304b  if ((*(data_1074cccc + 0x1b8))(arg2, &var_420) == 0)",
		"1006305b  sub_10057330(\"NULL\", 0x1869f, &var_410)",
		"1006306e  *(arg1 + 0x130) = sub_10057830()",
		"1006308c  return 1",
		"10075874  char const (* data_10075874)[0x5] = data_10073610 {\"text\"}",
		"10075878  void* data_10075878 = sub_10063010",
		"10075b08  char const (* data_10075b08)[0xb] = data_100733ac {\"focusSound\"}",
		"10075b0c  void* data_10075b0c = sub_10060e20",
		"10075d90  char const (* data_10075d90)[0xa] = data_100731d0 {\"soundLoop\"}",
		"10075d94  void* data_10075d94 = sub_10063010",
	):
		assert expected in hlil

	assert "PC_String_Parse(handle, &temp)" in item_focus_block
	assert "item->focusSound = DC->registerSound(temp, qfalse);" in item_focus_block
	assert "PC_String_Parse(handle, &item->text)" in item_text_block
	assert "menuDef_t *menu = (menuDef_t*)item;" in menu_loop_block
	assert "PC_String_Parse(handle, &menu->soundName)" in menu_loop_block
	assert "{\"focusSound\", ItemParse_focusSound, NULL}" in ui_shared
	assert "{\"soundLoop\", MenuParse_soundLoop, NULL}" in ui_shared
	assert "DC->startBackgroundTrack(menu->soundName, menu->soundName);" in activate_block
	assert "DC->registerSound(menu->soundName, qfalse);" in cache_block

	assert "Item_SetupKeywordHash();" in setup_item_block
	assert "return Item_Parse( handle, (itemDef_t *)item );" in parse_item_block
	assert "Menu_SetupKeywordHash();" in setup_menu_block
	assert "return Menu_Parse( handle, (menuDef_t *)menu );" in parse_menu_block
	_assert_order(
		init_runtime_block,
		"String_Init();",
		"CG_SetupBrowserItemKeywordHash();",
		"CG_SetupBrowserMenuKeywordHash();",
	)

	assert "sfx = &cgDC.Assets.itemFocusSound;" in browser_focus_block
	assert browser_focus_block.count("sfx = &item->focusSound;") == 2
	assert "if ( playSound && sfx && cgDC.startLocalSound ) {" in browser_focus_block
	assert "cgDC.startLocalSound( *sfx, CHAN_LOCAL_SOUND );" in browser_focus_block


def test_cgame_browser_script_sound_verbs_pin_local_and_looped_playback_wiring() -> None:
	alias_sections = json.loads(_read(SYMBOL_ALIASES))
	aliases = alias_sections["cgame"]
	ui_aliases = alias_sections["ui"]
	rows = _function_rows()
	hlil = _read(CGAME_HLIL)
	main_source = _read(CG_MAIN)
	newdraw_source = _read(CG_NEWDRAW)
	ui_shared = _read(UI_SHARED)
	display_context_block = _block_from_marker(main_source, "static void CG_InitDisplayContext")
	run_script_block = _block_from_marker(newdraw_source, "static void CG_RunBrowserScript")
	browser_play_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptPlay( void *widget, char **args )")
	browser_looped_block = _block_from_marker(newdraw_source, "static void CG_BrowserScriptPlayLooped( void *widget, char **args )")
	shared_play_block = _block_from_marker(ui_shared, "void Script_Play")
	shared_looped_block = _block_from_marker(ui_shared, "void Script_playLooped")

	assert ui_aliases["sub_10016cd0"] == "Script_Play"
	assert ui_aliases["sub_10016d20"] == "Script_playLooped"
	assert aliases["sub_10059eb0"] == "CG_BrowserScriptPlay"
	assert aliases["sub_10059f00"] == "CG_BrowserScriptPlayLooped"
	assert aliases["FUN_10059f50"] == "CG_RunBrowserScript"
	assert aliases["sub_10059f50"] == "CG_RunBrowserScript"
	assert rows["10059f50"]["name"] == "FUN_10059f50"
	assert rows["10059f50"]["size"] == "246"

	for expected in (
		"10059eb0    int32_t sub_10059eb0(int32_t* arg1)",
		"10059eb7  int32_t result = sub_10057120(arg1, 0)",
		"10059ecc  int32_t* eax = sub_10057830()",
		"10059eeb  return (*(ecx_1 + 0x74))((*(ecx_1 + 0xac))(eax, 6))",
		"10059f00    int32_t sub_10059f00(int32_t* arg1)",
		"10059f07  int32_t result = sub_10057120(arg1, 0)",
		"10059f1c  int32_t* eax = sub_10057830()",
		"10059f2f  (*(data_1074ccf8 + 0xb4))()",
		"10059f3e  return (*(data_1074ccf8 + 0xb0))(eax, eax)",
		"10059f50    int32_t __convention(\"regparm\") sub_10059f50",
		"1005a026                  (&data_1007501c)[esi_1 * 2](arg4, &var_808)",
		"1005a012                  (*(data_1074ccf8 + 0x50))(&var_808)",
		"100750b0  char const (* data_100750b0)[0x5] = data_1007382c {\"play\"}",
		"100750b4  void* data_100750b4 = sub_10059eb0",
		"100750b8  char const (* data_100750b8)[0xb] = data_10073820 {\"playlooped\"}",
		"100750bc  void* data_100750bc = sub_10059f00",
	):
		assert expected in hlil

	assert "{ \"play\", CG_BrowserScriptPlay }," in run_script_block
	assert "{ \"playlooped\", CG_BrowserScriptPlayLooped }," in run_script_block
	assert "browserScriptCommands[i].handler( widget, &p );" in run_script_block
	assert "cgDC.runScript( &p );" in run_script_block
	assert "Script_Play( (itemDef_t *)widget, args );" in browser_play_block
	assert "Script_playLooped( (itemDef_t *)widget, args );" in browser_looped_block
	assert "DC->startLocalSound(DC->registerSound(val, qfalse), CHAN_LOCAL_SOUND);" in shared_play_block
	assert "DC->stopBackgroundTrack();" in shared_looped_block
	assert "DC->startBackgroundTrack(val, val);" in shared_looped_block
	assert "{\"play\", &Script_Play}" in ui_shared
	assert "{\"playlooped\", &Script_playLooped}" in ui_shared
	assert "cgDC.runScript = &CG_RunMenuScript;" in display_context_block
	_assert_order(
		display_context_block,
		"cgDC.startLocalSound = &trap_S_StartLocalSound;",
		"cgDC.startBackgroundTrack = &trap_S_StartBackgroundTrack;",
		"cgDC.stopBackgroundTrack = &trap_S_StopBackgroundTrack;",
	)


def test_cgame_item_pickup_use_and_powerup_sounds_match_retail_wiring() -> None:
	hlil = _read(CGAME_HLIL)
	event_source = _read(CG_EVENT)
	main_source = _read(CG_MAIN)
	use_item_block = _block_from_marker(event_source, "static void CG_UseItem")
	pickup_sound_block = _block_from_marker(event_source, "static sfxHandle_t CG_ItemPickupAnnouncerSound")
	add_pickup_sound_block = _block_from_marker(event_source, "static void CG_AddItemPickupAnnouncerSound")
	entity_event_block = _block_from_marker(event_source, "void CG_EntityEvent")
	register_powerups_block = _block_from_marker(main_source, "static void CG_RegisterPowerupAnnouncerSounds")
	register_sounds_block = _block_from_marker(main_source, "static void CG_RegisterSounds")

	for expected in (
		"10019af0    void* sub_10019af0()",
		"10019b0d      sub_10020b50(\"CG_UseItem: invalid item %d\")",
		"10019b70          result = sub_10001170(ecx, edi_1 - 0x15, 6)",
		"10019bb8                  sub_1000be10(sub_100575e0(\"Use %s\"), 0x90, fconvert.s(fconvert.t(0.5f)))",
		"10019bb8              result = sub_1000be10(\"No item to use\", 0x90, fconvert.s(fconvert.t(0.5f)))",
		"10019c14          return (*(data_1074cccc + 0x94))(0, *ebx, 5, data_10a5fa68)",
		"10019bd0      ecx_4 = data_10a5f8e4",
		"10019c2e  return (*(data_1074cccc + 0x94))(0, *ebx, 5, ecx_4)",
		"1001a4c6                      result_1 = \"EV_ITEM_PICKUP\\n\"",
		"1001a509                  if (eax_31 == 5 || eax_31 == 8)",
		"1001a542                      result_1 = data_10a5fcd8",
		"1001a519                      int32_t eax_33 = *(eax_32 + 0xb8)",
		"1001a583                          result = sub_1004e110(eax_37)",
		"1001a59f                      result = sub_10019c40(result_29)",
		"1001a5ad                      result_1 = \"EV_GLOBAL_ITEM_PICKUP\\n\"",
		"1001a5ec                      void* ecx_26 = data_1074cccc",
		"1001a607                      int32_t edx_18 = *(data_10a6f8c4 + 0xb4)",
		"1001a627                  if ((data_10a3ff28 & 0x40000) == 0)",
		"1001a660                          sub_1004e110(eax_43)",
		"1001a674                          sub_10019d20(var_458, result_1)",
		"1001a692                          result = sub_10019c40(result_30)",
		"1001be4f                      result_1 = \"EV_POWERUP_QUAD\\n\"",
		"1001be87                  result_1 = data_10a5f7f0",
		"1001be93                      result_1 = \"EV_POWERUP_BATTLESUIT\\n\"",
		"1001becc                  result_1 = data_10a5fcd4",
		"1001bed8                      result_1 = \"EV_POWERUP_REGEN\\n\"",
		"1001bf11                  result_1 = data_10a5fccc",
		"1001bf1d                      result_1 = \"EV_POWERUP_ARMORREGEN\\n\"",
		"1001bf55                  result_1 = data_10a5fcd0",
		"10022507  char const* const var_498_13 = \"battlesuit.ogg\"",
		"1002277d  char const* const var_498_16 = \"quad_damage.ogg\"",
		"10022929  char const* const var_498_18 = \"armor_regen.ogg\"",
		"10021978  int32_t eax_194 = (*(data_1074cccc + 0xb8))(\"sound/items/use_nothing.ogg\")",
		"10021ae5  int32_t eax_219 = (*(data_1074cccc + 0xb8))(\"sound/items/invul_activate.ogg\")",
		"10022bf3  int32_t eax_466 = (*(edx_128 + 0xb8))(\"sound/items/use_medkit.ogg\")",
		"10022c0d  data_10a5f7f0 = (*(ecx_132 + 0xb8))(\"sound/items/damage3.ogg\")",
		"10022e48  data_10a5fccc = (*(ecx_148 + 0xb8))(\"sound/items/regen.ogg\")",
		"10022e5d  int32_t eax_509 = (*(data_1074cccc + 0xb8))(\"sound/misc/ar1_pkup.ogg\")",
		"10022e78  int32_t eax_511 = (*(edx_146 + 0xb8))(\"sound/items/protect3.ogg\")",
	):
		assert expected in hlil

	for expected in (
		"CG_Error( \"CG_UseItem: invalid item %d\", itemNum );",
		"CG_CenterPrint( \"No item to use\", SCREEN_HEIGHT * 0.30f,",
		"CG_CenterPrint( va( \"Use %s\", item->pickup_name ), SCREEN_HEIGHT * 0.30f,",
		"trap_S_StartSound (NULL, es->number, CHAN_BODY, cgs.media.useNothingSound );",
		"ci->medkitUsageTime = cg.time;",
		"trap_S_StartSound (NULL, es->number, CHAN_BODY, cgs.media.medkitSound );",
		"trap_S_StartSound (NULL, es->number, CHAN_BODY, cgs.media.useInvulnerabilitySound );",
	):
		assert expected in use_item_block
	assert "itemNum = 0;" not in use_item_block
	_assert_order(
		use_item_block,
		"if ( itemNum < 0 || itemNum > HI_NUM_HOLDABLE ) {",
		"CG_Error( \"CG_UseItem: invalid item %d\", itemNum );",
		"if ( es->number == cg.snap->ps.clientNum ) {",
		"switch ( itemNum ) {",
		"case HI_NONE:",
		"case HI_MEDKIT:",
		"case HI_INVULNERABILITY:",
	)

	for expected in (
		"case IT_POWERUP:",
		"case PW_QUAD:",
		"return cgs.media.quadDamagePowerupSound;",
		"case PW_BATTLESUIT:",
		"return cgs.media.battleSuitPowerupSound;",
		"case PW_REGEN:",
		"return cgs.media.regenerationPowerupSound;",
		"case IT_PERSISTANT_POWERUP:",
		"case PW_SCOUT:",
		"return cgs.media.scoutPowerupSound;",
		"case PW_GUARD:",
		"return cgs.media.guardPowerupSound;",
		"case PW_DOUBLER:",
		"return cgs.media.damagePowerupSound;",
		"case PW_AMMOREGEN:",
		"return cgs.media.armorRegenPowerupSound;",
	):
		assert expected in pickup_sound_block
	_assert_order(
		add_pickup_sound_block,
		"sfx = CG_ItemPickupAnnouncerSound( item );",
		"if ( sfx ) {",
		"CG_AddBufferedSound( sfx );",
	)

	_assert_order(
		entity_event_block,
		"case EV_ITEM_PICKUP:",
		"index = es->eventParm;",
		"if ( item->giType == IT_POWERUP || item->giType == IT_TEAM) {",
		"trap_S_StartSound (NULL, es->number, CHAN_AUTO,\tcgs.media.n_healthSound );",
		"} else if ( item->pickup_sound ) {",
		"trap_S_StartSound (NULL, es->number, CHAN_AUTO,\ttrap_S_RegisterSound( item->pickup_sound, qfalse ) );",
		"if ( item->giType == IT_PERSISTANT_POWERUP ) {",
		"CG_AddItemPickupAnnouncerSound( item );",
		"if ( es->number == cg.snap->ps.clientNum ) {",
		"CG_ItemPickup( index );",
	)
	_assert_order(
		entity_event_block,
		"case EV_GLOBAL_ITEM_PICKUP:",
		"index = es->eventParm;",
		"if( item->pickup_sound ) {",
		"trap_S_StartSound (NULL, cg.snap->ps.clientNum, CHAN_AUTO, trap_S_RegisterSound( item->pickup_sound, qfalse ) );",
		"if ( cgs.customSettingsMask & CUSTOM_SETTING_QUAD_HOG ) {",
		"break;",
		"CG_AddItemPickupAnnouncerSound( item );",
		"if ( item->giType == IT_POWERUP ) {",
		"CG_SpectatorTrackEvent( es->groundEntityNum, CG_SPECTATOR_TRACK_POWERUP );",
		"if ( es->number == cg.snap->ps.clientNum ) {",
		"CG_ItemPickup( index );",
	)
	_assert_order(
		entity_event_block,
		"case EV_POWERUP_QUAD:",
		"cg.powerupActive = PW_QUAD;",
		"cg.powerupTime = cg.time;",
		"trap_S_StartSound (NULL, es->number, CHAN_ITEM, cgs.media.quadSound );",
		"case EV_POWERUP_BATTLESUIT:",
		"cg.powerupActive = PW_BATTLESUIT;",
		"trap_S_StartSound (NULL, es->number, CHAN_ITEM, cgs.media.protectSound );",
		"case EV_POWERUP_REGEN:",
		"cg.powerupActive = PW_REGEN;",
		"trap_S_StartSound (NULL, es->number, CHAN_ITEM, cgs.media.regenSound );",
		"case EV_POWERUP_ARMORREGEN:",
		"cg.powerupActive = PW_AMMOREGEN;",
		"trap_S_StartSound( NULL, es->number, CHAN_ITEM, cgs.media.armorregenSound );",
	)

	for expected in (
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( battleSuitPowerupSound, "battlesuit.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( hastePowerupSound, "haste.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( invisibilityPowerupSound, "invisibility.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( quadDamagePowerupSound, "quad_damage.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( regenerationPowerupSound, "regeneration.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( armorRegenPowerupSound, "armor_regen.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( damagePowerupSound, "damage.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( guardPowerupSound, "guard.ogg" );',
		'CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( scoutPowerupSound, "scout.ogg" );',
	):
		assert expected in register_powerups_block

	for expected in (
		'cgs.media.useNothingSound = trap_S_RegisterSound( "sound/items/use_nothing.ogg", qfalse );',
		'cgs.media.useInvulnerabilitySound = trap_S_RegisterSound( "sound/items/invul_activate.ogg", qfalse );',
		'cgs.media.medkitSound = trap_S_RegisterSound ("sound/items/use_medkit.ogg", qfalse);',
		'cgs.media.quadSound = trap_S_RegisterSound("sound/items/damage3.ogg", qfalse);',
		'cgs.media.regenSound = trap_S_RegisterSound("sound/items/regen.ogg", qfalse);',
		'cgs.media.protectSound = trap_S_RegisterSound("sound/items/protect3.ogg", qfalse);',
		'cgs.media.n_healthSound = trap_S_RegisterSound("sound/items/n_health.ogg", qfalse );',
		'cgs.media.armorregenSound = trap_S_RegisterSound("sound/misc/ar1_pkup.ogg", qfalse);',
	):
		assert expected in register_sounds_block


def test_cgame_movement_environment_event_sounds_match_retail_wiring() -> None:
	hlil = _read(CGAME_HLIL)
	event_source = _read(CG_EVENT)
	main_source = _read(CG_MAIN)
	pain_block = _block_from_marker(event_source, "void CG_PainEvent")
	entity_event_block = _block_from_marker(event_source, "void CG_EntityEvent")
	register_sounds_block = _block_from_marker(main_source, "static void CG_RegisterSounds")
	cvar_table = main_source[
		main_source.index("static cvarTable_t cvarTable[]"):
		main_source.index("static int  cvarTableSize")
	]

	for expected in (
		"10019ca0    void __convention(\"regparm\") sub_10019ca0(int32_t arg1, int32_t* arg2 @ esi)",
		"10019cbe  if (data_10a9c1ec - arg2[0xa3] s>= 0x1f4)",
		"10019cf1      int32_t eax_1 = sub_1003ca30(*arg2)",
		"10019d04      (*(edi_1 + 0x94))(0, *arg2, 3, eax_1)",
		"10019d0f      arg2[0xa4] ^= 1",
		"10019d17      arg2[0xa3] = edx_2",
		"10019f79                      result_1 = \"EV_FOOTSTEP\\n\"",
		"10019fcf                      result_1 = \"EV_FOOTSTEP_METAL\\n\"",
		"1001a01c                  result_1 = \"EV_FOOTSPLASH\\n\"",
		"1001a069                  result_1 = \"EV_FOOTWADE\\n\"",
		"1001a074                  result_1 = \"EV_SWIM\\n\"",
		"1001a07f                      result_1 = \"EV_FALL_SHORT\\n\"",
		"1001a0dc                      result_1 = \"EV_FALL_MEDIUM\\n\"",
		"1001a141                      result_1 = \"EV_FALL_FAR\\n\"",
		"1001a1b2                      result_1 = \"EV_JUMP_PAD\\n\"",
		"1001a243                  (*(data_1074cccc + 0x94))(&arg2[0xae], 0x3fe, 0, data_10a5f968)",
		"1001a275                      result_1 = \"EV_JUMP\\n\"",
		"1001a3e9                      result_1 = \"EV_WATER_TOUCH\\n\"",
		"1001a41e                      result_1 = \"EV_WATER_LEAVE\\n\"",
		"1001a453                      result_1 = \"EV_WATER_UNDER\\n\"",
		"1001a489                      result_1 = \"EV_WATER_CLEAR\\n\"",
		"1001a919                      result_1 = \"EV_PLAYER_TELEPORT_IN\\n\"",
		"1001a959                      result_1 = \"EV_PLAYER_TELEPORT_OUT\\n\"",
		"1001a9b5                      result_1 = \"EV_ITEM_RESPAWN\\n\"",
		"1001a9dd                      result_1 = \"EV_GRENADE_BOUNCE\\n\"",
		"1001bdac                      result_1 = \"EV_PAIN\\n\"",
		"1001bdc1                  result = sub_10019ca0(arg2[0x30], arg2)",
		"1001bdcf                      result_1 = \"EV_DEATHx\\n\"",
		"1001bdeb                  sub_100575e0(var_458)",
		"1001be17                      result_1 = \"EV_DROWN\\n\"",
		"1001c009                      result_1 = \"EV_FOOTSTEP_SNOW\\n\"",
		"1001c056                      result_1 = \"EV_FOOTSTEP_WOOD\\n\"",
		"10021b44  int32_t eax_226 = (*(edx_55 + 0xb8))(\"sound/world/telein.ogg\")",
		"10021b5e  data_10a5f94c = (*(ecx_59 + 0xb8))(\"sound/world/teleout.ogg\")",
		"10021b73  int32_t eax_229 = (*(data_1074cccc + 0xb8))(\"sound/items/respawn1.ogg\")",
		"10021bd2  int32_t eax_236 = (*(edx_59 + 0xb8))(\"sound/player/land1.ogg\")",
		"10021d0b  data_10a5fa58 = (*(ecx_71 + 0xb8))(\"sound/player/watr_in.ogg\")",
		"10021d20  int32_t eax_259 = (*(data_1074cccc + 0xb8))(\"sound/player/watr_out.ogg\")",
		"10021d38  int32_t eax_261 = (*(edx_69 + 0xb8))(\"sound/player/watr_un.ogg\")",
		"10021d50  int32_t eax_262 = (*(ecx_73 + 0xb8))(\"sound/world/jumppad.ogg\")",
		"10022251      sub_10057510(&var_484, 0x40, \"sound/player/footsteps/step%i.og",
		"10022279      sub_10057510(&var_484, 0x40, \"sound/player/footsteps/boot%i.og",
		"100222a0      sub_10057510(&var_484, 0x40, \"sound/player/footsteps/flesh%i.o",
		"100222c7      sub_10057510(&var_484, 0x40, \"sound/player/footsteps/mech%i.og",
		"100222f2      sub_10057510(&var_484, 0x40, \"sound/player/footsteps/energy%i.",
		"1002231a      sub_10057510(&var_484, 0x40, \"sound/player/footsteps/splash%i.",
		"10022341      sub_10057510(&var_484, 0x40, \"sound/player/footsteps/clank%i.o",
		"1002236c      sub_10057510(&var_484, 0x40, \"sound/player/footsteps/snow%i.og",
		"10022394      sub_10057510(&var_484, 0x40, \"sound/player/footsteps/wood%i.og",
		"10022ea7  int32_t eax_514 = (*(data_1074cccc + 0xb8))(\"sound/weapons/grenade/hgrenb1a.o",
		"10022ebf  int32_t eax_516 = (*(edx_148 + 0xb8))(\"sound/weapons/grenade/hgrenb2a.o",
	):
		assert expected in hlil

	for expected in (
		"if ( cg.time - cent->pe.painTime < 500 ) {",
		"snd = \"*pain25_1.wav\";",
		"snd = \"*pain50_1.wav\";",
		"snd = \"*pain75_1.wav\";",
		"snd = \"*pain100_1.wav\";",
		"CG_CustomSound( cent->currentState.number, snd ) );",
		"cent->pe.painTime = cg.time;",
		"cent->pe.painDirection ^= 1;",
	):
		assert expected in pain_block

	_assert_order(
		entity_event_block,
		"case EV_FOOTSTEP:",
		"cgs.media.footsteps[ ci->footsteps ][rand()&3]",
		"case EV_FOOTSTEP_METAL:",
		"cgs.media.footsteps[ FOOTSTEP_METAL ][rand()&3]",
		"case EV_FOOTSTEP_SNOW:",
		"cgs.media.footsteps[ FOOTSTEP_SNOW ][rand()&3]",
		"case EV_FOOTSTEP_WOOD:",
		"cgs.media.footsteps[ FOOTSTEP_WOOD ][rand()&3]",
		"case EV_FOOTSPLASH:",
		"cgs.media.footsteps[ FOOTSTEP_SPLASH ][rand()&3]",
		"case EV_FOOTWADE:",
		"cgs.media.footsteps[ FOOTSTEP_SPLASH ][rand()&3]",
		"case EV_SWIM:",
		"cgs.media.footsteps[ FOOTSTEP_SPLASH ][rand()&3]",
	)
	_assert_order(
		entity_event_block,
		"case EV_FALL_SHORT:",
		"cgs.media.landSound",
		"cg.landChange = -8 * cg.kickScale;",
		"case EV_FALL_MEDIUM:",
		"CG_CustomSound( es->number, \"*pain100_1.wav\" )",
		"cg.landChange = -16 * cg.kickScale;",
		"case EV_FALL_FAR:",
		"CG_CustomSound( es->number, \"*fall1.wav\" )",
		"cent->pe.painTime = cg.time;",
		"cg.landChange = -24 * cg.kickScale;",
	)
	_assert_order(
		entity_event_block,
		"case EV_JUMP_PAD:",
		"CG_SmokePuff( cent->lerpOrigin, up,",
		"cgs.media.jumpPadSound",
		"CG_CustomSound( es->number, \"*jump1.wav\" )",
		"case EV_JUMP:",
		"CG_CustomSound( es->number, \"*jump1.wav\" )",
	)
	_assert_order(
		entity_event_block,
		"case EV_WATER_TOUCH:",
		"cgs.media.watrInSound",
		"case EV_WATER_LEAVE:",
		"cgs.media.watrOutSound",
		"case EV_WATER_UNDER:",
		"cgs.media.watrUnSound",
		"case EV_WATER_CLEAR:",
		"CG_CustomSound( es->number, \"*gasp.wav\" )",
	)
	_assert_order(
		entity_event_block,
		"case EV_PLAYER_TELEPORT_IN:",
		"cgs.media.teleInSound",
		"CG_SpawnEffect( position);",
		"case EV_PLAYER_TELEPORT_OUT:",
		"cgs.media.teleOutSound",
		"CG_SpawnEffect(  position);",
		"case EV_ITEM_POP:",
		"cgs.media.respawnSound",
		"case EV_ITEM_RESPAWN:",
		"cent->miscTime = cg.time;",
		"cgs.media.respawnSound",
		"case EV_GRENADE_BOUNCE:",
		"cgs.media.hgrenb1aSound",
		"cgs.media.hgrenb2aSound",
	)
	_assert_order(
		entity_event_block,
		"case EV_PAIN:",
		"if ( cent->currentState.number != cg.snap->ps.clientNum ) {",
		"CG_PainEvent( cent, es->eventParm );",
		"case EV_DEATH1:",
		"case EV_DEATH2:",
		"case EV_DEATH3:",
		"va(\"*death%i.wav\", event - EV_DEATH1 + 1)",
		"case EV_DROWN:",
		"CG_CustomSound( es->number, \"*drown.wav\" )",
	)

	assert '{ &cg_footsteps, "cg_footsteps", "1", CVAR_CHEAT },' in cvar_table
	for expected in (
		'cgs.media.teleInSound = trap_S_RegisterSound( "sound/world/telein.ogg", qfalse );',
		'cgs.media.teleOutSound = trap_S_RegisterSound( "sound/world/teleout.ogg", qfalse );',
		'cgs.media.respawnSound = trap_S_RegisterSound( "sound/items/respawn1.ogg", qfalse );',
		'cgs.media.landSound = trap_S_RegisterSound( "sound/player/land1.ogg", qfalse);',
		'cgs.media.watrInSound = trap_S_RegisterSound( "sound/player/watr_in.ogg", qfalse);',
		'cgs.media.watrOutSound = trap_S_RegisterSound( "sound/player/watr_out.ogg", qfalse);',
		'cgs.media.watrUnSound = trap_S_RegisterSound( "sound/player/watr_un.ogg", qfalse);',
		'cgs.media.jumpPadSound = trap_S_RegisterSound ("sound/world/jumppad.ogg", qfalse );',
		'Com_sprintf (name, sizeof(name), "sound/player/footsteps/step%i.ogg", i+1);',
		'cgs.media.footsteps[FOOTSTEP_NORMAL][i] = trap_S_RegisterSound (name, qfalse);',
		'Com_sprintf (name, sizeof(name), "sound/player/footsteps/boot%i.ogg", i+1);',
		'cgs.media.footsteps[FOOTSTEP_BOOT][i] = trap_S_RegisterSound (name, qfalse);',
		'Com_sprintf (name, sizeof(name), "sound/player/footsteps/flesh%i.ogg", i+1);',
		'cgs.media.footsteps[FOOTSTEP_FLESH][i] = trap_S_RegisterSound (name, qfalse);',
		'Com_sprintf (name, sizeof(name), "sound/player/footsteps/mech%i.ogg", i+1);',
		'cgs.media.footsteps[FOOTSTEP_MECH][i] = trap_S_RegisterSound (name, qfalse);',
		'Com_sprintf (name, sizeof(name), "sound/player/footsteps/energy%i.ogg", i+1);',
		'cgs.media.footsteps[FOOTSTEP_ENERGY][i] = trap_S_RegisterSound (name, qfalse);',
		'Com_sprintf (name, sizeof(name), "sound/player/footsteps/splash%i.ogg", i+1);',
		'cgs.media.footsteps[FOOTSTEP_SPLASH][i] = trap_S_RegisterSound (name, qfalse);',
		'Com_sprintf (name, sizeof(name), "sound/player/footsteps/clank%i.ogg", i+1);',
		'cgs.media.footsteps[FOOTSTEP_METAL][i] = trap_S_RegisterSound (name, qfalse);',
		'Com_sprintf (name, sizeof(name), "sound/player/footsteps/snow%i.ogg", i+1);',
		'cgs.media.footsteps[FOOTSTEP_SNOW][i] = trap_S_RegisterSound (name, qfalse);',
		'Com_sprintf (name, sizeof(name), "sound/player/footsteps/wood%i.ogg", i+1);',
		'cgs.media.footsteps[FOOTSTEP_WOOD][i] = trap_S_RegisterSound (name, qfalse);',
		'cgs.media.hgrenb1aSound = trap_S_RegisterSound("sound/weapons/grenade/hgrenb1a.ogg", qfalse);',
		'cgs.media.hgrenb2aSound = trap_S_RegisterSound("sound/weapons/grenade/hgrenb2a.ogg", qfalse);',
	):
		assert expected in register_sounds_block


def test_cgame_event_team_result_and_gameover_music_matches_retail_wiring() -> None:
	hlil = _read(CGAME_HLIL)
	event_source = _read(CG_EVENT)
	main_source = _read(CG_MAIN)
	entity_event_block = _block_from_marker(event_source, "void CG_EntityEvent")
	register_sounds_block = _block_from_marker(main_source, "static void CG_RegisterSounds")

	for expected in (
		"10019eb0    char* sub_10019eb0(float arg1 @ esi, int32_t* arg2)",
		"1001b80c                          sub_1004e180()",
		"1001b851                              int32_t eax_149 = *(data_1074cccc + 0xbc)",
		"1001b859                              var_458 = \"music/win\"",
		"1001b875                              var_458 = \"music/loss\"",
		"1001b884                          result = sub_1004e110(data_10a5fa9c)",
		"1001b898                          sub_1004e180()",
		"1001b8e3                              var_458 = \"music/win\"",
		"1001b8fe                              var_458 = \"music/loss\"",
		"1001b90d                          result = sub_1004e110(data_10a5fa98)",
		"1001b932                          sub_1000be10(\"Red wins the round\", var_458, result_1)",
		"1001b93f                          result = sub_1004e110(data_10a5fab8)",
		"1001b95a                          sub_1000be10(\"Blue wins the round\", var_458, result_1)",
		"1001b967                          result = sub_1004e110(data_10a5fabc)",
		"1001bac5                              sub_1000be10(\"Round Draw\", var_458, result_1)",
		"1001c0c0                      result_1 = \"EV_GAMEOVER\\n\"",
		"1001c0cd                  sub_1004e180()",
		"1001c11b                      int32_t eax_217 = *(data_1074cccc + 0xbc)",
		"1001c123                      var_458 = \"music/win\"",
		"1001c192                      var_458 = \"music/win\"",
		"1001c16e                      var_458 = \"music/loss\"",
		"100212a2      data_10a5fa9c = (*(esi_23 + 0xb8))(sub_10020dd0(\"red_wins.ogg\"))",
		"1002131c              int32_t eax_85 = (*(esi_26 + 0xb8))(sub_10020dd0(\"red_wins_round.ogg\"))",
		"1002133a              int32_t eax_87 = (*(esi_27 + 0xb8))(sub_10020dd0(\"blue_wins_round.ogg\"))",
		"10021358              int32_t eax_90 = (*(esi_28 + 0xb8))(sub_10020dd0(\"round_draw.ogg\"))",
		"10021378              data_10a5fac4 = (*(esi_29 + 0xb8))(sub_10020dd0(\"round_over.ogg\"))",
	):
		assert expected in hlil

	for expected in (
		"case GTS_KAMIKAZE:",
		"trap_S_StartLocalSound(cgs.media.kamikazeFarSound, CHAN_ANNOUNCER);",
		"case GTS_REDTEAM_WINS:",
		"case GTS_BLUETEAM_WINS:",
		"case GTS_REDTEAM_WINS_ROUND:",
		"CG_AddBufferedSound( cgs.media.redWinsRoundSound );",
		"case GTS_BLUETEAM_WINS_ROUND:",
		"CG_AddBufferedSound( cgs.media.blueWinsRoundSound );",
		"case GTS_ROUND_DRAW:",
		"CG_AddBufferedSound( cgs.media.roundDrawSound );",
		"case GTS_ROUND_OVER:",
		"CG_AddBufferedSound( cgs.media.roundOverSound );",
		"case QL_EV_GAMEOVER:",
		"trap_S_StartBackgroundTrack( \"music/win\", \"\" );",
		"trap_S_StartBackgroundTrack( \"music/loss\", \"\" );",
	):
		assert expected in entity_event_block

	_assert_order(
		entity_event_block,
		"case GTS_REDTEAM_WINS:",
		"CG_ClearBufferedAnnouncements();",
		"CG_PlayBuzzerSound();",
		"if ( cgs.clientinfo[cg.clientNum].team == TEAM_RED ) {",
		"trap_S_StartBackgroundTrack( \"music/win\", \"\" );",
		"} else if ( cgs.clientinfo[cg.clientNum].team == TEAM_BLUE ) {",
		"trap_S_StartBackgroundTrack( \"music/loss\", \"\" );",
		"CG_AddBufferedSound( cgs.media.redWinsSound );",
	)
	_assert_order(
		entity_event_block,
		"case GTS_BLUETEAM_WINS:",
		"CG_ClearBufferedAnnouncements();",
		"CG_PlayBuzzerSound();",
		"if ( cgs.clientinfo[cg.clientNum].team == TEAM_BLUE ) {",
		"trap_S_StartBackgroundTrack( \"music/win\", \"\" );",
		"} else if ( cgs.clientinfo[cg.clientNum].team == TEAM_RED ) {",
		"trap_S_StartBackgroundTrack( \"music/loss\", \"\" );",
		"CG_AddBufferedSound( cgs.media.blueWinsSound );",
	)
	_assert_order(
		entity_event_block,
		"case QL_EV_GAMEOVER:",
		"CG_ClearBufferedAnnouncements();",
		"CG_PlayBuzzerSound();",
		"if ( CG_IsLocalPlayerWinner() ) {",
		"CG_AddBufferedSound( cgs.media.winnerSound );",
		"trap_S_StartBackgroundTrack( \"music/win\", \"\" );",
		"} else if ( cg.snap && cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR ) {",
		"trap_S_StartBackgroundTrack( \"music/win\", \"\" );",
		"} else {",
		"CG_AddBufferedSound( cgs.media.loserSound );",
		"trap_S_StartBackgroundTrack( \"music/loss\", \"\" );",
	)

	for expected in (
		'CG_REGISTER_RETAIL_REWARD_SAMPLE( redWinsSound, "red_wins", "red_wins" );',
		'CG_REGISTER_RETAIL_REWARD_SAMPLE( blueWinsSound, "blue_wins", "blue_wins" );',
		'CG_REGISTER_RETAIL_REWARD_SAMPLE( redWinsRoundSound, "red_wins_round", "red_wins_round" );',
		'CG_REGISTER_RETAIL_REWARD_SAMPLE( blueWinsRoundSound, "blue_wins_round", "blue_wins_round" );',
		'CG_REGISTER_RETAIL_REWARD_SAMPLE( roundDrawSound, "round_draw", "round_draw" );',
		'CG_REGISTER_RETAIL_REWARD_SAMPLE( roundOverSound, "round_over", "round_over" );',
		'cgs.media.kamikazeFarSound = trap_S_RegisterSound( "sound/items/kam_explode_far.ogg", qfalse );',
		'cgs.media.winnerSound = CG_RegisterConfiguredAnnouncerClip( "you_win.ogg" );',
		'cgs.media.loserSound = CG_RegisterConfiguredAnnouncerClip( "you_lose.ogg" );',
	):
		assert expected in register_sounds_block


def test_cgame_music_configstring_and_server_command_bridge_matches_retail_wiring() -> None:
	hlil = _read(CGAME_HLIL)
	main_source = _read(CG_MAIN)
	servercmds_source = _read(CG_SERVERCMDS)
	syscalls_source = _read(CG_SYSCALLS)
	local_source = _read(CG_LOCAL)
	start_music_block = _block_from_marker(main_source, "void CG_StartMusic")
	init_block = _block_from_marker(main_source, "void CG_Init( int serverMessageNum")
	config_string_block = _block_from_marker(servercmds_source, "static void CG_ConfigStringModified")
	map_restart_block = _block_from_marker(servercmds_source, "static void CG_MapRestart")
	parse_music_block = _block_from_marker(servercmds_source, "static void CG_ParsePlayMusic")
	stop_music_block = _block_from_marker(servercmds_source, "static void CG_ParseStopMusic")
	server_command_block = _block_from_marker(servercmds_source, "static void CG_ServerCommand")
	start_background_syscall = _block_from_marker(syscalls_source, "void\ttrap_S_StartBackgroundTrack")
	stop_background_syscall = _block_from_marker(syscalls_source, "void\ttrap_S_StopBackgroundTrack")

	for expected in (
		"10025320    int32_t sub_10025320()",
		"10025348  var_88 = data_10a38428 + 0x10a39420",
		"1002534c  sub_10057120(&var_88, 1)",
		"10025376  strncpy(&var_44, 0x100d6a78, 0x3f)",
		"10025387  sub_10057120(&var_88, 1)",
		"100253ab  strncpy(&var_84, 0x100d6a78, 0x3f)",
		"100253c8  int32_t result = (*(data_1074cccc + 0xbc))(&var_44, &var_84)",
		"10029ecf  sub_10025320()",
		"10049a00          return sub_10025320()",
		"1004a384  sub_10025320()",
		"1004b3ad                  char const* const ecx_34 = \"playMusic\"",
		"1004b402                      char const* const ecx_36 = \"stopMusic\"",
		"1004b445                          int32_t eax_65 = (*(data_1074cccc + 0xc0))()",
	):
		assert expected in hlil

	_assert_order(
		start_music_block,
		"s = (char *)CG_ConfigString( CS_MUSIC );",
		"Q_strncpyz( parm1, COM_Parse( &s ), sizeof( parm1 ) );",
		"Q_strncpyz( parm2, COM_Parse( &s ), sizeof( parm2 ) );",
		"trap_S_StartBackgroundTrack( parm1, parm2 );",
	)

	_assert_order(
		config_string_block,
		"trap_GetGameState( &cgs.gameState );",
		"str = CG_ConfigString( num );",
		"if ( num == CS_MUSIC ) {",
		"CG_StartMusic();",
		"} else if ( num == CS_SERVERINFO ) {",
	)

	_assert_order(
		map_restart_block,
		"CG_ClearBufferedAnnouncements();",
		"cg.mapRestart = qtrue;",
		"CG_StartMusic();",
		"trap_S_ClearLoopingSounds(qtrue);",
	)

	_assert_order(
		init_block,
		"CG_SetConfigValues();",
		"CG_StartMusic();",
		"CG_AdvanceLoadingProgress();",
		"CG_LoadingString( \"\" );",
	)

	assert "if ( trap_Argc() > 1 ) {" in parse_music_block
	assert "trap_S_StartBackgroundTrack( CG_Argv(1), CG_Argv(2) );" in parse_music_block
	assert "trap_S_StopBackgroundTrack();" in stop_music_block

	_assert_order(
		server_command_block,
		'if ( !strcmp( cmd, "playSound" ) ) {',
		"CG_ParsePlaySound();",
		'if ( !strcmp( cmd, "playMusic" ) ) {',
		"CG_ParsePlayMusic();",
		'if ( !strcmp( cmd, "stopMusic" ) ) {',
		"CG_ParseStopMusic();",
		'if ( !strcmp( cmd, "clearSounds" ) ) {',
	)

	assert "void\t\ttrap_S_StartBackgroundTrack( const char *intro, const char *loop );" in local_source
	assert "void\ttrap_S_StopBackgroundTrack( void );" in local_source
	assert "syscall( CG_S_STARTBACKGROUNDTRACK, intro, loop );" in start_background_syscall
	assert "syscall( CG_S_STOPBACKGROUNDTRACK );" in stop_background_syscall


def test_cgame_weapon_fire_impact_and_tracer_sounds_match_retail_wiring() -> None:
	hlil = _read(CGAME_HLIL)
	weapons_source = _read(CG_WEAPONS)
	main_source = _read(CG_MAIN)
	spin_block = _block_from_marker(weapons_source, "static float\tCG_MachinegunSpinAngle")
	add_weapon_block = _block_from_marker(weapons_source, "void CG_AddPlayerWeapon")
	fire_block = _block_from_marker(weapons_source, "void CG_FireWeapon")
	missile_hit_block = _block_from_marker(weapons_source, "void CG_MissileHitWall( int weapon")
	damage_through_block = _block_from_marker(
		weapons_source,
		"void CG_MissileHitWallDmgThrough( vec3_t origin, vec3_t dir, int weapon )",
	)
	tracer_block = _block_from_marker(weapons_source, "void CG_Tracer")
	register_sounds_block = _block_from_marker(main_source, "static void CG_RegisterSounds")

	for expected in (
		"10052250    int32_t sub_10052250(int32_t* arg1 @ esi)",
		"100522b5      x87_r7_1 = fconvert.t(fconvert.s((float.t(0x3e8 - eax_1) / fconvert.t(1000.0)",
		"10052332          return (*(data_1074cccc + 0x94))(result, *arg1, 2, data_10a5f8d0)",
		"10052420    void __convention(\"regparm\") sub_10052420",
		"1005245b  sub_10050aa0(edi, arg4)",
		"10052517              (*(data_1074cccc + 0xac))(*ebx, &ebx[0xae], &data_1074ccd8,",
		"10052582              (*(data_1074cccc + 0xac))(*ebx, &ebx[0xae], &data_1074ccd8, eax_7)",
		"100527c5          int32_t var_1c8_1 = sub_10052250(ebx)",
		"10053de0    int32_t sub_10053de0(int32_t* arg1 @ edi)",
		"10053e04          return sub_10020b50(\"CG_FireWeapon: ent->weapon >= WP…\")",
		"10053e1c      arg1[0x78] = result",
		"10053e7c                  (*(data_1074cccc + 0x94))(0, *arg1, 2, eax_6)",
		"10053ed8              (*(data_1074cccc + 0x94))(0, *arg1, 4, data_10a5f7f0)",
		"10053ef0    void* __stdcall sub_10053ef0",
		"1005425d              edx = (*(data_1074cccc + 0x94))(ebx, 0x3fe, 0, edi_1)",
		"10054db0    void* __stdcall sub_10054db0",
		"1005540b  void* result = sub_10053ef0(x87control, arg16, 0f, ebx_1, arg3, arg2, arg1, ebx,",
		"10055c00    int32_t sub_10055c00(float* arg1 @ edi, float* arg2)",
		"10055c55  if (not(fconvert.t(100.0) > fconvert.t(xmm0)))",
		"10055f3b      (*(data_1074cccc + 0x120))(data_10a5f4f8, 4, &var_70)",
		"10055f9c      result = (*(eax_6 + 0x94))(&var_10, 0x3fe, 0, ecx_2)",
	):
		assert expected in hlil

	assert "#define\t\tSPIN_SPEED\t0.9" in weapons_source
	assert "#define\t\tCOAST_TIME\t1000" in weapons_source

	for expected in (
		"if ( cent->pe.barrelSpinning == !(cent->currentState.eFlags & EF_FIRING) ) {",
		"cent->pe.barrelSpinning = !!(cent->currentState.eFlags & EF_FIRING);",
		"if ( cent->currentState.weapon == WP_CHAINGUN && !cent->pe.barrelSpinning ) {",
		"trap_S_StartSound( NULL, cent->currentState.number, CHAN_WEAPON, cgs.media.sfx_chgwind );",
	):
		assert expected in spin_block

	_assert_order(
		add_weapon_block,
		"CG_RegisterWeapon( weaponNum );",
		"continuousFlash = ( weaponNum == WP_LIGHTNING || weaponNum == WP_GAUNTLET || weaponNum == WP_GRAPPLING_HOOK );",
		"if ( ps && ( !cg_muzzleFlash.integer || !cg_drawGun.integer ) ) {",
		"if ( !ps ) {",
		"cent->pe.lightningFiring = qfalse;",
		"trap_S_AddLoopingSound( cent->currentState.number, cent->lerpOrigin, vec3_origin, weapon->firingSound );",
		"cent->pe.lightningFiring = qtrue;",
		"} else if ( weapon->readySound ) {",
		"trap_S_AddLoopingSound( cent->currentState.number, cent->lerpOrigin, vec3_origin, weapon->readySound );",
		"angles[ROLL] = CG_MachinegunSpinAngle( cent );",
	)

	_assert_order(
		fire_block,
		"if ( ent->weapon == WP_NONE ) {",
		"if ( ent->weapon >= WP_NUM_WEAPONS ) {",
		'CG_Error( "CG_FireWeapon: ent->weapon >= WP_NUM_WEAPONS" );',
		"cent->muzzleFlashTime = cg.time;",
		"if ( ent->weapon == WP_LIGHTNING ) {",
		"if ( cent->pe.lightningFiring ) {",
		"if ( cent->currentState.powerups & ( 1 << PW_QUAD ) ) {",
		"trap_S_StartSound (NULL, cent->currentState.number, CHAN_ITEM, cgs.media.quadSound );",
		"for ( c = 0 ; c < 4 ; c++ ) {",
		"c = rand() % c;",
		"trap_S_StartSound( NULL, ent->number, CHAN_WEAPON, weap->flashSound[c] );",
		"if ( weap->ejectBrassFunc && cg_brassTime.integer > 0 ) {",
	)

	for expected in (
		"if( soundType == IMPACTSOUND_FLESH ) {",
		"sfx = cgs.media.sfx_nghitflesh;",
		"sfx = cgs.media.sfx_lghit2;",
		"sfx = cgs.media.sfx_proxexp;",
		"sfx = cgs.media.sfx_rockexp;",
		"sfx = cgs.media.sfx_plasmaexp;",
		"sfx = cgs.media.sfx_grapplehit;",
		"sfx = 0;",
		"sfx = cgs.media.sfx_chghitflesh;",
		"sfx = cgs.media.sfx_ric1;",
		"trap_S_StartSound( origin, ENTITYNUM_WORLD, CHAN_AUTO, sfx );",
	):
		assert expected in missile_hit_block

	_assert_order(
		damage_through_block,
		"CG_Trace( &trace, probeOrigin, NULL, NULL, origin, ENTITYNUM_NONE, CONTENTS_SOLID );",
		"CG_SmokePuff( puffOrigin, velocity,",
		"CG_MissileHitWall( weapon, 0, origin, dir, IMPACTSOUND_DEFAULT );",
	)

	_assert_order(
		tracer_block,
		"VectorSubtract( dest, source, forward );",
		"if ( len < 100 ) {",
		"begin = 50 + random() * (len - 60);",
		"trap_R_AddPolyToScene( cgs.media.tracerShader, 4, verts );",
		"midpoint[0] = ( start[0] + finish[0] ) * 0.5;",
		"trap_S_StartSound( midpoint, ENTITYNUM_WORLD, CHAN_AUTO, cgs.media.tracerSound );",
	)

	for expected in (
		'cgs.media.tracerSound = trap_S_RegisterSound( "sound/weapons/machinegun/buletby1.ogg", qfalse );',
		'cgs.media.sfx_chgwind = trap_S_RegisterSound( "sound/weapons/vulcan/wvulwind.ogg", qfalse );',
	):
		assert expected in register_sounds_block


def test_cgame_low_ammo_sound_warning_matches_retail_threshold_contract() -> None:
	hlil = _read(CGAME_HLIL)
	playerstate_source = _read(CG_PLAYERSTATE)
	main_source = _read(CG_MAIN)
	draw_source = _read(CG_DRAW)
	weapons_source = _read(CG_WEAPONS)
	check_ammo_block = _block_from_marker(playerstate_source, "void CG_CheckAmmo")
	transition_block = _block_from_marker(playerstate_source, "void CG_TransitionPlayerState")
	low_ammo_update_block = _block_from_marker(main_source, "static void CG_UpdateLowAmmoWarningPercentile")
	cvar_table = main_source[
		main_source.index("static cvarTable_t cvarTable[]"):
		main_source.index("static int  cvarTableSize")
	]
	register_sounds_block = _block_from_marker(main_source, "static void CG_RegisterSounds")
	ammo_warning_block = _block_from_marker(draw_source, "static void CG_DrawAmmoWarning")
	weapon_bar_ammo_block = _block_from_marker(weapons_source, "static void CG_GetLegacyWeaponBarAmmoColor")

	for expected in (
		"10042e50    int32_t sub_10042e50()",
		"10042e51  void* ecx_1 = data_10a6f8c4",
		"10042e57  int32_t eax = *(ecx_1 + 0xbc)",
		"10042e5d  int32_t ecx_2 = *(ecx_1 + (eax << 2) + 0x1ac)",
		"10042e82      fconvert.s(float.t(*(eax * 0x30 + 0x10079078)) * fconvert.t(data_10a6a0e8))",
		"10042e93  if (float.t(ecx_2) >= fconvert.t(var_4_1) || ecx_2 == 0xffffffff)",
		"10042e9e      ecx_5 = 0",
		"10042e99      ecx_5 = sbb.d(ecx_3, ecx_3, ecx_2 != 0) + 2",
		"10042ea0  data_10ab8cd0 = ecx_5",
		"10042ead  if (ecx_5 == edx || ecx_5 != 2)",
		"10042ecd          ecx_6 = data_10a5f950",
		"10042eeb      ecx_6 = data_10a5f954",
		"10042f00  return (*(data_1074cccc + 0x9c))(ecx_6, 6, var_4_1)",
		"10043c48  sub_10042e50()",
	):
		assert expected in hlil

	for expected in (
		"weapon = (weapon_t)cg.snap->ps.weapon;",
		"previous = cg.lowAmmoWarning;",
		"if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {",
		"warning = 0;",
		"ammo = cg.snap->ps.ammo[ weapon ];",
		"threshold = (int)( BG_GetWeaponMaxAmmo( weapon ) * cg.lowAmmoWarningPercentile );",
		"if ( ammo == -1 || ammo >= threshold ) {",
		"} else if ( ammo != 0 ) {",
		"warning = 1;",
		"} else {",
		"warning = 2;",
		"cg.lowAmmoWarning = warning;",
		"if ( warning == previous ) {",
		"if ( warning == 2 ) {",
		"trap_S_StartLocalSound( cgs.media.noAmmoSound, CHAN_LOCAL_SOUND );",
		"if ( warning != 1 ) {",
		"switch ( cg_lowAmmoWarningSound.integer ) {",
		"warningSound = cgs.media.lowAmmoSound;",
		"warningSound = cgs.media.noAmmoSound;",
		"trap_S_StartLocalSound( warningSound, CHAN_LOCAL_SOUND );",
	):
		assert expected in check_ammo_block

	_assert_order(
		check_ammo_block,
		"weapon = (weapon_t)cg.snap->ps.weapon;",
		"previous = cg.lowAmmoWarning;",
		"threshold = (int)( BG_GetWeaponMaxAmmo( weapon ) * cg.lowAmmoWarningPercentile );",
		"cg.lowAmmoWarning = warning;",
		"if ( warning == previous ) {",
		"if ( warning == 2 ) {",
		"switch ( cg_lowAmmoWarningSound.integer ) {",
		"trap_S_StartLocalSound( warningSound, CHAN_LOCAL_SOUND );",
	)
	_assert_order(
		transition_block,
		"CG_CheckLocalSounds( ps, ops );",
		"CG_RecordCrosshairHitFeedback( ps, ops );",
		"CG_CheckAmmo();",
		"CG_CheckPlayerstateEvents( ps, ops );",
	)

	for expected in (
		'{ &cg_lowAmmoWarningPercentile, "cg_lowAmmoWarningPercentile", "0.20", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0.01", "1.00" },',
		'{ &cg_lowAmmoWarningSound, "cg_lowAmmoWarningSound", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "2" },',
		'{ &cg_lowAmmoWeaponBarWarning, "cg_lowAmmoWeaponBarWarning", "2", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "2" },',
	):
		assert expected in cvar_table

	for expected in (
		"clamped = Com_Clamp( 0.0f, 1.0f, cg_lowAmmoWarningPercentile.value );",
		"cg.lowAmmoWarningPercentile = clamped;",
		"lowAmmoWarningPercentileModCount = cg_lowAmmoWarningPercentile.modificationCount;",
	):
		assert expected in low_ammo_update_block

	for expected in (
		'cgs.media.lowAmmoSound = trap_S_RegisterSound( "sound/weapons/lowammo.ogg", qfalse );',
		'cgs.media.noAmmoSound = trap_S_RegisterSound( "sound/weapons/noammo.ogg", qfalse );',
	):
		assert expected in register_sounds_block

	for expected in (
		"if ( !cg.lowAmmoWarning ) {",
		"if ( cg.lowAmmoWarning == 2 ) {",
		's = "OUT OF AMMO";',
		's = "LOW AMMO WARNING";',
	):
		assert expected in ammo_warning_block

	for expected in (
		"if ( ammo == 0 && cg_lowAmmoWeaponBarWarning.integer != 0 ) {",
		"if ( ammo <= 0 || cg_lowAmmoWeaponBarWarning.integer < 2 ) {",
		"threshold = (int)( BG_GetWeaponMaxAmmo( (weapon_t)weapon ) * cg.lowAmmoWarningPercentile );",
		"if ( ammo < threshold ) {",
	):
		assert expected in weapon_bar_ammo_block


def test_cgame_local_reward_sound_transition_matches_retail_playerstate_contract() -> None:
	hlil = _read(CGAME_HLIL)
	source = _read(CG_PLAYERSTATE)
	push_reward_block = _block_from_marker(source, "void pushReward")
	local_sounds_block = _block_from_marker(source, "void CG_CheckLocalSounds")
	transition_block = _block_from_marker(source, "void CG_TransitionPlayerState")

	for expected in (
		"10043570    int32_t __convention(\"regparm\") sub_10043570",
		"10043578  if (result s< 0xf)",
		"1004357b      data_10ab8cec = result + 1",
		"10043580      (&data_10ab8d74)[result + 1] = arg3",
		"10043591      (&data_10ab8d34)[data_10ab8cec] = result",
		"100435a2      (&data_10ab8cf4)[data_10ab8cec] = arg5",
		"100435b0    int32_t __convention(\"regparm\") sub_100435b0(void* arg1, void* arg2)",
		"100435b9  int32_t result = *(arg1 + 0x110)",
		"100435c5  if (result == *(arg2 + 0x110))",
		"10043655                  (*(data_1074cccc + 0xa0))(eax_1, 6, fconvert.s(fconvert.t(data_10a629a8)))",
		"100436de          result, edx = (*(data_1074cccc + 0x9c))(edx_2, 6)",
		"10043710              edx = sub_10043570(eax_9, edx_3, data_10a5fa78, edx_3, eax_9)",
		"1004388e                  result = sub_1004e110(data_10a5f9d4)",
		"100438e1                          result = sub_1004e110(data_10a5fb08)",
		"10043958                                  result = sub_1004e110(data_10a5fa48)",
		"10043a9c                          result = sub_1004e110(data_10a5f974)",
		"10043ae2                      return sub_1004e110(data_10a5f984) __tailcall",
		"10043c18      sub_100435b0(arg1, edx_2)",
		"10043c48  sub_10042e50()",
		"10043c50  st0, result = sub_100434b0(arg1, arg2)",
	):
		assert expected in hlil

	for expected in (
		"if ( cgs.announcerProfile == ANNOUNCER_PROFILE_DISABLED || !cg_announcerRewardsVO.integer ) {",
		"sfx = 0;",
		"if (cg.rewardStack < (MAX_REWARDSTACK-1)) {",
		"cg.rewardStack++;",
		"cg.rewardSound[cg.rewardStack] = sfx;",
		"cg.rewardShader[cg.rewardStack] = shader;",
		"cg.rewardCount[cg.rewardStack] = rewardCount;",
	):
		assert expected in push_reward_block

	for expected in (
		"if ( ps->persistant[PERS_TEAM] != ops->persistant[PERS_TEAM] ) {",
		"hitDelta = ps->persistant[PERS_HITS] - ops->persistant[PERS_HITS];",
		"trap_QL_S_StartLocalSoundVolume( sfx, CHAN_LOCAL_SOUND, s_killBeepVolume.value );",
		"trap_S_StartLocalSound( sfx, CHAN_LOCAL_SOUND );",
		"trap_S_StartLocalSound( cgs.media.hitTeamSound, CHAN_LOCAL_SOUND );",
		"if ( cg.intermissionStarted ) {",
		"rewardVOEnabled = (qboolean)( cg_announcerRewardsVO.integer && cgs.announcerProfile != ANNOUNCER_PROFILE_DISABLED );",
		"pushReward(cgs.media.captureAwardSound, cgs.media.medalCapture, ps->persistant[PERS_CAPTURES]);",
		"pushReward(sfx, cgs.media.medalImpressive, ps->persistant[PERS_IMPRESSIVE_COUNT]);",
		"pushReward(sfx, cgs.media.medalExcellent, ps->persistant[PERS_EXCELLENT_COUNT]);",
		"pushReward(sfx, cgs.media.medalGauntlet, ps->persistant[PERS_GAUNTLET_FRAG_COUNT]);",
		"pushReward(cgs.media.defendSound, cgs.media.medalDefend, ps->persistant[PERS_DEFEND_COUNT]);",
		"pushReward(cgs.media.assistSound, cgs.media.medalAssist, ps->persistant[PERS_ASSIST_COUNT]);",
		"trap_S_StartLocalSound( cgs.media.deniedSound, CHAN_ANNOUNCER );",
		"trap_S_StartLocalSound( cgs.media.humiliationSound, CHAN_ANNOUNCER );",
		"trap_S_StartLocalSound( cgs.media.holyShitSound, CHAN_ANNOUNCER );",
		"pushReward(sfx, cgs.media.medalMidair, 1);",
		"pushReward(cgs.media.perfectSound, cgs.media.medalPerfect, 1);",
		"pushReward(cgs.media.quadGodSound, cgs.media.medalQuadGod, 1);",
		"pushReward(cgs.media.rampageSound, cgs.media.medalRampage, 1);",
		"pushReward(cgs.media.revengeSound, cgs.media.medalRevenge, 1);",
		"pushReward(cgs.media.perforatedSound, cgs.media.medalPerforated, 1);",
		"pushReward(cgs.media.headshotSound, cgs.media.medalHeadshot, 1);",
		"pushReward(cgs.media.firstFragSound, cgs.media.medalFirstFrag, 1);",
		"trap_S_StartLocalSound( cgs.media.youHaveFlagSound, CHAN_ANNOUNCER );",
		"CG_AddBufferedSound(cgs.media.takenLeadSound);",
		"CG_AddBufferedSound(cgs.media.tiedLeadSound);",
		"CG_AddBufferedSound(cgs.media.lostLeadSound);",
		"trap_S_StartLocalSound( cgs.media.suddenDeathSound, CHAN_ANNOUNCER );",
		"trap_S_StartLocalSound( cgs.media.oneMinuteSound, CHAN_ANNOUNCER );",
		"trap_S_StartLocalSound( cgs.media.fiveMinuteSound, CHAN_ANNOUNCER );",
		"CG_AddBufferedSound(cgs.media.oneFragSound);",
		"CG_AddBufferedSound(cgs.media.twoFragSound);",
		"CG_AddBufferedSound(cgs.media.threeFragSound);",
	):
		assert expected in local_sounds_block

	_assert_order(
		local_sounds_block,
		"if ( ps->persistant[PERS_TEAM] != ops->persistant[PERS_TEAM] ) {",
		"hitDelta = ps->persistant[PERS_HITS] - ops->persistant[PERS_HITS];",
		"if ( cg.intermissionStarted ) {",
		"rewardVOEnabled = (qboolean)( cg_announcerRewardsVO.integer && cgs.announcerProfile != ANNOUNCER_PROFILE_DISABLED );",
		"if ( cgs.gametype >= GT_TEAM ) {",
		"if (!reward) {",
		"if ( cgs.timelimit > 0 ) {",
		"if ( cgs.fraglimit > 0 && cgs.gametype < GT_CTF) {",
	)
	_assert_order(
		transition_block,
		"CG_CheckLocalSounds( ps, ops );",
		"CG_RecordCrosshairHitFeedback( ps, ops );",
		"CG_CheckAmmo();",
		"CG_CheckPlayerstateEvents( ps, ops );",
	)


def test_cgame_voice_chat_sound_queue_matches_retail_ring_contract() -> None:
	hlil = _read(CGAME_HLIL)
	source = _read(CG_SERVERCMDS)
	head_model_block = _block_from_marker(source, "int CG_HeadModelVoiceChats")
	get_voice_block = _block_from_marker(source, "int CG_GetVoiceChat")
	list_block = _block_from_marker(source, "voiceChatList_t *CG_VoiceChatListForClient")
	play_block = _block_from_marker(source, "void CG_PlayVoiceChat")
	play_buffered_block = _block_from_marker(source, "void CG_PlayBufferedVoiceChats")
	add_buffered_block = _block_from_marker(source, "void CG_AddBufferedVoiceChat")
	local_block = _block_from_marker(source, "void CG_VoiceChatLocal")

	for expected in (
		"1004a560    int32_t sub_1004a560()",
		"1004a58d  int32_t eax_2 = (*(data_1074cccc + 0x38))(ecx, &__return_addr, 0)",
		"1004a5bd          (*data_1074cccc)(sub_100575e0(\"^1voice chat file too large: %s",
		"1004a6a0    int32_t sub_1004a6a0(int32_t arg1, int32_t* arg2, void** arg3)",
		"1004a706              int32_t eax_6 = sub_10064260(float.t(rand() & 0x7fff) / fconvert.t(32767.0)",
		"1004a740    void* sub_1004a740(int32_t arg1)",
		"1004a762  if (eax_2 s< 0 || eax_2 s>= 0x40)",
		"1004a8fd                          int32_t eax_10 = sub_1004a560()",
		"1004aac0    void __convention(\"regparm\") sub_1004aac0(void* arg1)",
		"1004aaef          (*(data_1074cccc + 0x9c))(esi[1], 3)",
		"1004ab09              int32_t eax_1 = sub_10045050(&esi[3])",
		"1004ab20                  data_10a5f2c4 = data_10a9c1ec + 0x1388",
		"1004ab62              sub_10060710(\"voiceMenu\")",
		"1004abae      *(data_10ab8f48 * 0x138 + 0x10a02304) = 0",
		"1004abc0    void* sub_1004abc0()",
		"1004abef              result = sub_1004aac0(result + 0x10a02300)",
		"1004ac14              data_10ab8f48 = ecx_3",
		"1004ac1a              data_10ab8f40 = edx_2",
		"1004ac30    void __fastcall sub_1004ac30(int32_t arg1, int32_t arg2)",
		"1004ac55      __builtin_memcpy(dest: eax_1 * 0x138 + 0x10a02300, src: arg2, n: 0x138)",
		"1004ac6d      data_10ab8f44 = ecx_1",
		"1004ac83          sub_1004aac0(eax * 0x138 + 0x10a02300)",
		"1004ac88          data_10ab8f48 += 1",
		"1004ac90    int32_t __convention(\"regparm\") sub_1004ac90",
		"1004acf0      result = sub_1004a6a0(arg4, &var_144, &var_148)",
		"1004ad63          result = sub_1004ac30(sub_10057510(&var_9e, 0x96, \"(%s): %c%c%s\"), &var_140)",
	):
		assert expected in hlil

	for expected in (
		'trap_FS_FOpenFile( filename, &f, FS_READ );',
		"if ( len >= MAX_VOICEFILESIZE ) {",
		'trap_Print( va( S_COLOR_RED "voice chat file too large: %s is %i, max allowed is %i", filename, len, MAX_VOICEFILESIZE ) );',
		"return -1;",
	):
		assert expected in head_model_block

	for expected in (
		"rnd = random() * voiceChatList->voiceChats[i].numSounds;",
		"*snd = voiceChatList->voiceChats[i].sounds[rnd];",
		"*chat = voiceChatList->voiceChats[i].chats[rnd];",
	):
		assert expected in get_voice_block

	for expected in (
		"if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {",
		"clientNum = 0;",
		'Com_sprintf(filename, sizeof(filename), "scripts/%s.vc", headModelName);',
		"voiceChatNum = CG_HeadModelVoiceChats(filename);",
		"gender = GENDER_MALE;",
		"return &voiceChatLists[0];",
	):
		assert expected in list_block

	for expected in (
		"if ( cg.intermissionStarted ) {",
		"if ( cg_playVoiceChats.integer ) {",
		"trap_S_StartLocalSound( vchat->snd, CHAN_VOICE);",
		"int orderTask = CG_ValidOrder(vchat->cmd);",
		"cgs.acceptOrderTime = cg.time + 5000;",
		'Menus_OpenByName( "voiceMenu" );',
		"if ( !vchat->voiceOnly && cg_showVoiceText.integer ) {",
		"CG_AddToTeamChat( vchat->message );",
		'CG_Printf( "%s\\n", vchat->message );',
		"voiceChatBuffer[cg.voiceChatBufferOut].snd = 0;",
	):
		assert expected in play_block

	for expected in (
		"if ( cg.voiceChatTime < cg.time ) {",
		"if (cg.voiceChatBufferOut != cg.voiceChatBufferIn && voiceChatBuffer[cg.voiceChatBufferOut].snd) {",
		"CG_PlayVoiceChat(&voiceChatBuffer[cg.voiceChatBufferOut]);",
		"cg.voiceChatBufferOut = (cg.voiceChatBufferOut + 1) % MAX_VOICECHATBUFFER;",
		"cg.voiceChatTime = cg.time + 1000;",
	):
		assert expected in play_buffered_block

	for expected in (
		"memcpy(&voiceChatBuffer[cg.voiceChatBufferIn], vchat, sizeof(bufferedVoiceChat_t));",
		"cg.voiceChatBufferIn = (cg.voiceChatBufferIn + 1) % MAX_VOICECHATBUFFER;",
		"if (cg.voiceChatBufferIn == cg.voiceChatBufferOut) {",
		"CG_PlayVoiceChat( &voiceChatBuffer[cg.voiceChatBufferOut] );",
		"cg.voiceChatBufferOut++;",
	):
		assert expected in add_buffered_block
	assert "cg.voiceChatBufferOut = (cg.voiceChatBufferOut + 1) % MAX_VOICECHATBUFFER;" not in add_buffered_block

	for expected in (
		"CG_SetClientSpeakingState( clientNum, qtrue );",
		"voiceChatList = CG_VoiceChatListForClient( clientNum );",
		"if ( CG_GetVoiceChat( voiceChatList, cmd, &snd, &chat ) ) {",
		"if ( mode == SAY_TEAM || !cg_teamChatsOnly.integer ) {",
		"vchat.voiceOnly = voiceOnly;",
		"CG_AddBufferedVoiceChat(&vchat);",
	):
		assert expected in local_block


def test_cgame_custom_sound_reconstructs_retail_lookup_and_diagnostics() -> None:
	hlil = _read(CGAME_HLIL)
	source = _read(CG_PLAYERS)
	custom_sound_block = _block_from_marker(source, "sfxHandle_t\tCG_CustomSound")

	for expected in (
		"1003ca30    int32_t __convention(\"regparm\") sub_1003ca30",
		"1003ca4a      return (*(data_1074cccc + 0xb8))(ebx)",
		"1003caad          if (edi s< 0x20)",
		"1003cab5      sub_10020b50(\"Unknown custom sound: %s\")",
		"1003cacb  return *(arg1 * 0x738 + &data_10a41cf0 + (edi << 2) + 0x690)",
		'char const data_10071204[0x22] = "CG_CustomSound: invalid client %i", 0',
		'char const data_10071228[0x19] = "Unknown custom sound: %s", 0',
	):
		assert expected in hlil

	for expected in (
		"if ( soundName[0] != '*' ) {",
		"return trap_S_RegisterSound( soundName, qfalse );",
		"if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {",
		'CG_Error( "CG_CustomSound: invalid client %i", clientNum );',
		"for ( i = 0 ; i < MAX_CUSTOM_SOUNDS && cg_customSoundNames[i] ; i++ ) {",
		"if ( !strcmp( soundName, cg_customSoundNames[i] ) ) {",
		"return ci->sounds[i];",
		'CG_Error( "Unknown custom sound: %s", soundName );',
	):
		assert expected in custom_sound_block

	assert 'CG_Error( "CG_CustomSound: invalid client %d", clientNum );' not in custom_sound_block


def test_cgame_warmup_countdown_sounds_use_retail_announcer_volume_import() -> None:
	hlil = _read(CGAME_HLIL)
	draw_source = _read(CG_DRAW)
	main_source = _read(CG_MAIN)
	local_source = _read(CG_LOCAL)
	warmup_block = _block_from_marker(draw_source, "static void CG_PlayWarmupCountSound")

	for expected in (
		"1000eb30    void __convention(\"regparm\") sub_1000eb30(uint32_t arg1)",
		"1000eb8c          (*(data_1074cccc + 0xa0))(data_10a5fb70, 7, fconvert.s(fconvert.t(data_10a6b528)))",
		"1000eb8c          (*(data_1074cccc + 0xa0))(data_10a5fb6c, 7, fconvert.s(fconvert.t(data_10a6b528)))",
		"1000eb8c          (*(data_1074cccc + 0xa0))(data_10a5fb68, 7, fconvert.s(fconvert.t(data_10a6b528)))",
		"1000eb43          if (data_10a403e0 == 0)",
		"(*(data_1074cccc + 0xa0))(data_10a5fab4, 7,",
		"(*(data_1074cccc + 0xa0))(data_10a5fb78, 7,",
		"fconvert.s(fconvert.t(data_10a6b528)))",
		'char const data_1006a930[0x12] = "s_announcerVolume", 0',
		'char const (* data_100784d4)[0x12] = data_1006a930 {"s_announcerVolume"}',
		"10a6b528  int32_t data_10a6b528 = 0x0",
	):
		assert expected in hlil

	for expected in (
		"vmCvar_t\ts_announcerVolume;",
		'{ &s_announcerVolume, "s_announcerVolume", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "4" },',
	):
		assert expected in main_source

	assert "extern\tvmCvar_t\t\ts_announcerVolume;" in local_source

	for expected in (
		"trap_QL_S_StartLocalSoundVolume( cgs.media.count3Sound, CHAN_ANNOUNCER, s_announcerVolume.value );",
		"trap_QL_S_StartLocalSoundVolume( cgs.media.count2Sound, CHAN_ANNOUNCER, s_announcerVolume.value );",
		"trap_QL_S_StartLocalSoundVolume( cgs.media.count1Sound, CHAN_ANNOUNCER, s_announcerVolume.value );",
		"trap_QL_S_StartLocalSoundVolume( cgs.media.countPrepareSound, CHAN_ANNOUNCER, s_announcerVolume.value );",
		"trap_QL_S_StartLocalSoundVolume( cgs.media.roundBeginsInSound, CHAN_ANNOUNCER, s_announcerVolume.value );",
	):
		assert expected in warmup_block

	for legacy_sound in (
		"count3Sound",
		"count2Sound",
		"count1Sound",
		"countPrepareSound",
		"roundBeginsInSound",
	):
		assert f"trap_S_StartLocalSound( cgs.media.{legacy_sound}, CHAN_ANNOUNCER );" not in warmup_block


def test_cgame_spatial_and_fragment_sound_helpers_match_retail_wiring() -> None:
	hlil = _read(CGAME_HLIL)
	ents_source = _read(CG_ENTS)
	localents_source = _read(CG_LOCALENTS)
	set_position_block = _block_from_marker(ents_source, "void CG_SetEntitySoundPosition")
	fragment_block = _block_from_marker(localents_source, "void CG_FragmentBounceSound")

	for expected in (
		"10015450    int32_t sub_10015450(int32_t* arg1)",
		"1001546c  if (arg1[0x2e] != 0xffffff)",
		"100154e4      int32_t eax_6 = (*(data_1074cccc + 0xb0))(*arg1, &arg1[0xae])",
		"1001548d  var_10 = fconvert.s(fconvert.t(arg1[0xae]) + fconvert.t(*((ecx_1 << 2) + &data_10a410ec)))",
		"1001ec10    int32_t __convention(\"regparm\") sub_1001ec10(int32_t arg1, void* arg2 @ esi)",
		"1001ec2d      int32_t eax_1 = rand() & 3",
		"1001ec5e      int32_t eax_4 = (*(data_1074cccc + 0x94))(arg1 + 0xc, 0x3fe, 0, eax_2)",
		"1001ec82      int32_t eax_7 = rand() & 4",
		"1001ecc0      eax_5 = (*(data_1074cccc + 0x94))(arg1 + 0xc, 0x3fe, 0, eax_8)",
		"1001ecc6  *(arg2 + 0x9c) = 0",
	):
		assert expected in hlil

	for expected in (
		"if ( cent->currentState.solid == SOLID_BMODEL ) {",
		"v = cgs.inlineModelMidpoints[ cent->currentState.modelindex ];",
		"VectorAdd( cent->lerpOrigin, v, origin );",
		"trap_S_UpdateEntityPosition( cent->currentState.number, origin );",
		"trap_S_UpdateEntityPosition( cent->currentState.number, cent->lerpOrigin );",
	):
		assert expected in set_position_block

	for expected in (
		"if ( le->fragmentBounceSoundType == LEBS_BLOOD ) {",
		"r = rand() & 3;",
		"trap_S_StartSound( trace->endpos, ENTITYNUM_WORLD, CHAN_AUTO, s );",
		"} else if ( le->fragmentBounceSoundType == LEBS_ELECTRO ) {",
		"// Retail masks rand() with 4 here, so only sounds 01 and 04 are reachable.",
		"if ( rand() & 4 ) {",
		"le->fragmentBounceSoundType = LEBS_NONE;",
	):
		assert expected in fragment_block


def test_cgame_entity_effects_and_missile_loop_sounds_match_retail_native_wiring() -> None:
	hlil = _read(CGAME_HLIL)
	ents_source = _read(CG_ENTS)
	local_source = _read(CG_LOCAL)
	syscalls_source = _read(CG_SYSCALLS)
	entity_effects_hlil = _slice_between(
		hlil,
		'10015500    int32_t __convention("regparm") sub_10015500(int32_t* arg1)',
		"100155c9",
	)
	entity_effects_block = _block_from_marker(ents_source, "static void CG_EntityEffects")
	missile_block = _block_from_marker(ents_source, "static void CG_Missile")
	add_entity_block = _block_from_marker(ents_source, "static void CG_AddCEntity")

	for expected in (
		'10015500    int32_t __convention("regparm") sub_10015500(int32_t* arg1)',
		"10015504  sub_10015450(arg1)",
		"1001551d  if (eax != 0 && data_10a60a2c != 0)",
		"10015541      (*(data_1074cccc + 0xac))(*arg1, &arg1[0xae], &data_1074ccd8,",
		"*((eax << 2) + &data_10a408e8))",
		"100155c2  return (*(data_1074cccc + 0x128))(&arg1[0xae]",
		"1001769b  if (*(ebx_2 + 0x54) != 0)",
		"100176ac      sub_10001a70(data_10a9c1ec, &arg1[3], &var_10)",
		"100176cf      (*(data_1074cccc + 0xac))(*arg1, &arg1[0xae], &var_10, *(ebx_2 + 0x54))",
		"10018b01      int32_t ecx_1 = sub_10015500(arg1)",
		"10018b41              st0, eax_5 = sub_100175f0(arg1)",
	):
		assert expected in hlil

	assert "data_1074cccc + 0x144" not in entity_effects_hlil

	_assert_order(
		entity_effects_block,
		"CG_SetEntitySoundPosition( cent );",
		"if ( cent->currentState.loopSound ) {",
		"trap_S_AddLoopingSound( cent->currentState.number, cent->lerpOrigin, vec3_origin,",
		"cgs.gameSounds[ cent->currentState.loopSound ] );",
		"if ( cent->currentState.constantLight ) {",
	)
	assert "cent->currentState.eType != ET_SPEAKER" not in entity_effects_block
	assert "trap_S_AddRealLoopingSound" not in entity_effects_block

	_assert_order(
		missile_block,
		"if ( weapon->missileSound ) {",
		"BG_EvaluateTrajectoryDelta( &cent->currentState.pos, cg.time, velocity );",
		"trap_S_AddLoopingSound( cent->currentState.number, cent->lerpOrigin, velocity, weapon->missileSound );",
	)
	_assert_order(
		add_entity_block,
		"CG_CalcEntityLerpPositions( cent );",
		"CG_EntityEffects( cent );",
		"case ET_MISSILE:",
		"CG_Missile( cent );",
	)

	assert "void\t\ttrap_S_AddRealLoopingSound( int entityNum, const vec3_t origin, const vec3_t velocity, sfxHandle_t sfx );" in local_source
	assert "case CG_S_ADDREALLOOPINGSOUND: return CG_QL_IMPORT_COMPAT_S_ADDREALLOOPINGSOUND;" in syscalls_source


def test_cgame_server_sound_commands_preserve_retail_import_slots_and_order() -> None:
	decompile = _read(CGAME_DECOMPILE)
	source = _read(CG_SERVERCMDS)
	server_command_block = _block_from_marker(source, "static void CG_ServerCommand")

	for expected in (
		'pcVar8 = "playSound";',
		"iVar5 = (**(code **)(iVar5 + 0xb8))(uVar4);",
		"(**(code **)(DAT_1074cccc + 0x9c))(iVar5,6);",
		'pcVar8 = "playMusic";',
		"(**(code **)(iVar5 + 0xbc))(uVar4);",
		'pcVar8 = "stopMusic";',
		"(**(code **)(DAT_1074cccc + 0xc0))();",
		'pcVar8 = "clearSounds";',
		"(**(code **)(DAT_1074cccc + 0xa8))();",
	):
		assert expected in decompile

	_assert_order(
		server_command_block,
		'if ( !strcmp( cmd, "playSound" ) ) {',
		"CG_ParsePlaySound();",
		'if ( !strcmp( cmd, "playMusic" ) ) {',
		"CG_ParsePlayMusic();",
		'if ( !strcmp( cmd, "stopMusic" ) ) {',
		"CG_ParseStopMusic();",
		'if ( !strcmp( cmd, "clearSounds" ) ) {',
		"CG_ParseClearSounds();",
		'if ( !strcmp( cmd, "tchat" ) ) {',
	)

	parse_sound_block = _block_from_marker(source, "static void CG_ParsePlaySound")
	parse_music_block = _block_from_marker(source, "static void CG_ParsePlayMusic")
	stop_music_block = _block_from_marker(source, "static void CG_ParseStopMusic")
	clear_sounds_block = _block_from_marker(source, "static void CG_ParseClearSounds")

	assert "trap_S_StartLocalSound( trap_S_RegisterSound( CG_Argv( 1 ), qfalse ), CHAN_LOCAL_SOUND );" in parse_sound_block
	assert "trap_S_StartBackgroundTrack( CG_Argv(1), CG_Argv(2) );" in parse_music_block
	assert "trap_S_StopBackgroundTrack();" in stop_music_block
	assert "trap_S_ClearLoopingSounds( qtrue );" in clear_sounds_block


def test_cgame_buffered_announcer_queue_matches_retail_ring_and_channel_wiring() -> None:
	hlil = _read(CGAME_HLIL)
	source = _read(CG_VIEW)
	powerup_block = _block_from_marker(source, "static void CG_PowerupTimerSounds")
	clear_buffered_block = _block_from_marker(source, "static void CG_ClearBufferedSounds")
	clear_announcements_block = _block_from_marker(source, "void CG_ClearBufferedAnnouncements")
	add_block = _block_from_marker(source, "void CG_AddBufferedSound")
	play_block = _block_from_marker(source, "static void CG_PlayBufferedSounds")

	for expected in (
		"1004e050    void sub_1004e050()",
		"(*(data_1074cccc + 0x94))(0, *(ebx_1 + 0xb4), 4, data_10a5f800)",
		"1004e110    void __convention(\"regparm\") sub_1004e110",
		"*((data_10ab8db4 << 2) + &data_10ab8e3c) = arg1",
		"*((data_10ab8db4 << 2) + &data_10ab8ebc) = 0x5dc",
		"1004e180    int32_t sub_1004e180()",
		"memset(&data_10ab8e3c, 0, 0x80)",
		"data_10ab8dbc = esi",
		"1004e220    int32_t sub_1004e220()",
		"(*(data_1074cccc + 0xa0))(result, 7",
	):
		assert expected in hlil

	for expected in (
		"for ( i = 0 ; i < MAX_POWERUPS ; i++ ) {",
		"if ( ( t - cg.time ) / POWERUP_BLINK_TIME != ( t - cg.oldTime ) / POWERUP_BLINK_TIME ) {",
		"trap_S_StartSound( NULL, cg.snap->ps.clientNum, CHAN_ITEM, cgs.media.wearOffSound );",
	):
		assert expected in powerup_block

	for expected in (
		"if ( cg_bufferedSoundTimes[cg_bufferedSoundTail] > cg.time ) {",
		"nextSoundTime = cg_bufferedSoundTimes[cg_bufferedSoundTail];",
		"memset( cg_bufferedSounds, 0, sizeof( cg_bufferedSounds ) );",
		"memset( cg_bufferedSoundTimes, 0, sizeof( cg_bufferedSoundTimes ) );",
		"memset( cg_bufferedSoundDelays, 0, sizeof( cg_bufferedSoundDelays ) );",
		"cg_bufferedSoundTimes[0] = nextSoundTime;",
	):
		assert expected in clear_buffered_block

	assert "CG_ClearRewardStack();" in clear_announcements_block
	assert "CG_ClearBufferedSounds();" in clear_announcements_block

	for expected in (
		"if ( !sfx ) {",
		"if ( cgs.announcerProfile == ANNOUNCER_PROFILE_DISABLED ) {",
		"cg_bufferedSounds[cg_bufferedSoundHead] = sfx;",
		"cg_bufferedSoundDelays[cg_bufferedSoundHead] = CG_BUFFERED_ANNOUNCER_DELAY;",
		"cg_bufferedSoundHead = ( cg_bufferedSoundHead + 1 ) % CG_BUFFERED_ANNOUNCER_COUNT;",
		"if ( cg_bufferedSoundHead == cg_bufferedSoundTail ) {",
		"cg_bufferedSoundTail = ( cg_bufferedSoundTail + 1 ) % CG_BUFFERED_ANNOUNCER_COUNT;",
	):
		assert expected in add_block

	for expected in (
		"if ( cgs.announcerProfile == ANNOUNCER_PROFILE_DISABLED ) {",
		"CG_ClearBufferedSounds();",
		"if ( cg_bufferedSoundTimes[cg_bufferedSoundTail] > cg.time ) {",
		"sfx = cg_bufferedSounds[cg_bufferedSoundTail];",
		"if ( !sfx || cg_bufferedSoundTail == cg_bufferedSoundHead ) {",
		"trap_S_StartLocalSound( sfx, CHAN_ANNOUNCER );",
		"cg_bufferedSoundTimes[nextIndex] = cg_bufferedSoundDelays[cg_bufferedSoundTail] + cg.time;",
		"cg_bufferedSoundTail = nextIndex;",
	):
		assert expected in play_block
