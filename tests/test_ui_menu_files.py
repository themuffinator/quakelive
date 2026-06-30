from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pytest

from scripts.ui.retail_ui_corpus import inventory_missing_reason, read_retail_root_file
from scripts.ui.retail_ui_corpus import DEFAULT_BASEQ3_ROOT

REPO_ROOT = Path(__file__).resolve().parent.parent
UI_HLIL_PART01 = (
    REPO_ROOT
    / "references"
    / "hlil"
    / "quakelive"
    / "uix86.all"
    / "uix86.dll_hlil_split"
    / "uix86.dll_hlil_part01.txt"
)
QL_STEAM_HLIL_PART04 = (
    REPO_ROOT
    / "references"
    / "hlil"
    / "quakelive"
    / "quakelive_steam.exe"
    / "quakelive_steam.exe_hlil_split"
    / "quakelive_steam.exe_hlil_part04.txt"
)
QL_STEAM_HLIL_PART07 = (
    REPO_ROOT
    / "references"
    / "hlil"
    / "quakelive"
    / "quakelive_steam.exe"
    / "quakelive_steam.exe_hlil_split"
    / "quakelive_steam.exe_hlil_part07.txt"
)
QL_STEAM_FUNCTIONS = (
    REPO_ROOT
    / "references"
    / "reverse-engineering"
    / "ghidra"
    / "quakelive_steam"
    / "functions.csv"
)
UI_FUNCTIONS = (
    REPO_ROOT
    / "references"
    / "reverse-engineering"
    / "ghidra"
    / "uix86"
    / "functions.csv"
)
CGAME_HLIL = REPO_ROOT / "references" / "hlil" / "quakelive" / "cgamex86.dll" / "cgamex86.dll_hlil.txt"
CGAME_FUNCTIONS = (
    REPO_ROOT
    / "references"
    / "reverse-engineering"
    / "ghidra"
    / "cgamex86"
    / "functions.csv"
)
UI_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "ui.json"
CGAME_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "cgame.json"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"


def _extract_define(text: str, name: str) -> str:
    pattern = rf"#define\s+{re.escape(name)}\s+\"([^\"]+)\""
    match = re.search(pattern, text)
    if not match:
        raise AssertionError(f"define for {name} not found")
    return match.group(1)


def _extract_numeric_defines(text: str, prefix: str) -> dict[str, int]:
    return {
        match.group(1): int(match.group(2), 0)
        for match in re.finditer(
            rf"#define\s+({re.escape(prefix)}[A-Z0-9_]+)\s+(0x[0-9a-fA-F]+|\d+)",
            text,
        )
    }


def _extract_enum_values(text: str, enum_name: str) -> dict[str, int]:
    end_match = re.search(rf"\}}\s*{re.escape(enum_name)}\s*;", text)
    if not end_match:
        raise AssertionError(f"enum {enum_name} not found")

    start = text.rfind("typedef enum", 0, end_match.start())
    if start == -1:
        raise AssertionError(f"typedef enum start for {enum_name} not found")

    brace_start = text.find("{", start, end_match.start())
    if brace_start == -1:
        raise AssertionError(f"enum body for {enum_name} not found")

    body = re.sub(r"/\*.*?\*/", "", text[brace_start + 1 : end_match.start()], flags=re.DOTALL)
    body = "\n".join(line.split("//", 1)[0] for line in body.splitlines())

    values: dict[str, int] = {}
    next_value = 0
    for raw_entry in body.split(","):
        entry = raw_entry.strip()
        if not entry:
            continue

        if "=" in entry:
            name, value_text = (part.strip() for part in entry.split("=", 1))
            value = int(value_text.rstrip("uU"), 0)
        else:
            name = entry
            value = next_value

        values[name] = value
        next_value = value + 1

    return values


def _extract_ui_native_import_map(text: str) -> dict[str, str]:
    block = _extract_function_block(text, "static int UI_MapNativeImport( int arg ) {")
    return {
        match.group(1): match.group(2)
        for match in re.finditer(
            r"case\s+(UI_[A-Z0-9_]+):\s+return\s+(UI_QL_IMPORT_[A-Z0-9_]+);",
            block,
        )
    }


def _extract_vcxproj_group(text: str, condition: str) -> str:
    pattern = (
        r"<ItemDefinitionGroup Condition=\""
        + re.escape(condition)
        + r"\">(.*?)</ItemDefinitionGroup>"
    )
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        raise AssertionError(f"ItemDefinitionGroup for {condition} not found")
    return match.group(1)


def _extract_vcxproj_compile_item(text: str, include: str) -> str:
    pattern = r"<ClCompile Include=\"" + re.escape(include) + r"\">(.*?)</ClCompile>"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        raise AssertionError(f"ClCompile for {include} not found")
    return match.group(1)


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


def test_ui_menu_defaults_use_existing_assets() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert '"ui_menuFiles", UI_MENU_FILE_QUAKELIVE' in ui_main
    assert '"ui_menuFlow", "1"' in ui_main

    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")
    legacy_menu = _extract_define(ui_local, "UI_MENU_FILE_LEGACY")
    legacy_ingame = _extract_define(ui_local, "UI_INGAME_FILE_LEGACY")

    for menu_file in (legacy_menu, legacy_ingame):
        assert (REPO_ROOT / "src" / menu_file).exists(), menu_file


def test_ui_listbox_columns_consume_full_retail_scoreboard_rows() -> None:
    ui_shared_h = (REPO_ROOT / "src/code/ui/ui_shared.h").read_text(encoding="utf-8")
    ui_shared_c = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    end_scoreboard_dom = (REPO_ROOT / "src/ui/end_scoreboard_dom.menu").read_text(encoding="utf-8")

    declared_columns = [int(match.group(1)) for match in re.finditer(r"\bcolumns\s+(\d+)", end_scoreboard_dom)]
    assert declared_columns
    assert max(declared_columns) == 19
    assert "#define MAX_LB_COLUMNS 19" in ui_shared_h

    parse_block = _extract_function_block(ui_shared_c, "qboolean ItemParse_columns( itemDef_t *item, int handle ) {")
    assert "listPtr->numColumns = storedColumns;" in parse_block
    assert "for (i = 0; i < num; i++) {" in parse_block
    assert "if (i < MAX_LB_COLUMNS) {" in parse_block


def test_ui_does_not_generate_bridge_menu_assets() -> None:
    assert not (REPO_ROOT / "src/code/ui/ui_quakelive_bridge.c").exists()

    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_atoms = (REPO_ROOT / "src/code/ui/ui_atoms.c").read_text(encoding="utf-8")
    ui_cdkey = (REPO_ROOT / "src/code/ui/ui_cdkey.c").read_text(encoding="utf-8")
    combined = "\n".join((ui_local, ui_main, ui_atoms, ui_cdkey))

    for removed in (
        "UI_MENU_FILE_QUAKELIVE_BRIDGE",
        "UI_INGAME_FILE_QUAKELIVE_BRIDGE",
        "UI_MENU_FLOW_BRIDGED",
        "UI_WriteBridgeFile",
        "UI_WriteBridgeScripts",
        "UI_OpenBrowserBridgeMenu",
        "UI_BrowserBridgeAvailable",
        "ql_bridge_",
        "menus_quakelive_bridge.auto.txt",
        "ingame_quakelive_bridge.auto.txt",
    ):
        assert removed not in combined


def test_ui_bundle_manifest_validates_retail_icon_roots_without_repo_asset_sources() -> None:
    manifest = json.loads((REPO_ROOT / "tools/packaging/ui_bundle_manifest.json").read_text(encoding="utf-8"))
    files = manifest["files"]
    by_source_dir = {
        entry["source_dir"]: entry
        for entry in files
        if "source_dir" in entry
    }

    assert by_source_dir["baseq3/icons"]["destination"] == "icons"
    assert by_source_dir["baseq3/menu/icons"]["destination"] == "menu/icons"
    assert by_source_dir["baseq3/levelshots"]["destination"] == "levelshots"
    assert not any(
        str(entry.get("source", entry.get("source_dir", ""))).startswith("assets/quakelive/")
        for entry in files
    )

    audit = manifest["audit"]
    assert "icons" in audit["required_paths"]
    assert "menu/icons" in audit["required_paths"]
    assert "levelshots" in audit["required_paths"]
    assert "baseq3/icons" not in audit["required_paths"]
    assert "baseq3/levelshots" not in audit["required_paths"]
    assert "icons/**/*" in audit["required_globs"]
    assert "menu/icons/**/*" in audit["required_globs"]
    assert "levelshots/**/*" in audit["required_globs"]
    assert "baseq3/icons/**/*" not in audit["required_globs"]
    assert "baseq3/levelshots/**/*" not in audit["required_globs"]


def test_ui_bundle_manifest_validates_retail_menudef_header() -> None:
    manifest = json.loads((REPO_ROOT / "tools/packaging/ui_bundle_manifest.json").read_text(encoding="utf-8"))
    files = manifest["files"]

    header_entries = [
        entry
        for entry in files
        if entry.get("source") == "baseq3/ui/menudef.h"
    ]
    assert len(header_entries) == 1
    assert header_entries[0]["destination"] == "ui/menudef.h"

    audit = manifest["audit"]
    assert "ui/menudef.h" in audit["required_paths"]

    runtime_probe = (REPO_ROOT / "tools/client/run_client_runtime_probe.ps1").read_text(encoding="utf-8")
    assert "fs_cdpath must point at the installed Quake Live root" in runtime_probe


def test_ui_extended_native_exports_match_retail_bridge_surface() -> None:
    ui_public = (REPO_ROOT / "src/code/ui/ui_public.h").read_text(encoding="utf-8")
    assert "#define UI_QL_API_VERSION\t8" in ui_public
    assert "#define UI_QL_NATIVE_IMPORT_COUNT\t256" in ui_public
    assert "UI_REFRESH_DISPLAY_CONTEXT" in ui_public
    assert "UI_MENUS_ANY_VISIBLE" in ui_public
    assert "UI_FOR_EACH_ARENA_NAME" in ui_public
    assert "UI_DRAW_ADVERTISEMENT_WAIT_SCREEN" in ui_public
    assert "UI_QL_IMPORT_LAN_GETPINGQUEUECOUNT = 53" in ui_public
    assert "UI_QL_IMPORT_LAN_SAVECACHEDSERVERS = 58" in ui_public
    assert "UI_QL_IMPORT_LAN_ADDSERVER = 62" in ui_public
    assert "UI_QL_IMPORT_LAN_SERVERSTATUS = 65" in ui_public
    assert "UI_QL_IMPORT_LAN_COMPARESERVERS = 66" in ui_public
    assert "UI_QL_IMPORT_MEMORY_REMAINING = 67" in ui_public
    assert "UI_QL_IMPORT_S_STOPBACKGROUNDTRACK = 71" in ui_public
    assert "UI_QL_IMPORT_R_REMAP_SHADER = 78" in ui_public
    assert "UI_QL_IMPORT_SETUP_ADVERT_CELL_SHADER = 80" in ui_public
    assert "UI_QL_IMPORT_REFRESH_ADVERT_CELL_SHADER = 81" in ui_public
    assert "UI_QL_IMPORT_INIT_ADVERTISEMENT_BRIDGE = 82" in ui_public
    assert "UI_QL_IMPORT_ACTIVATE_ADVERT = 84" in ui_public
    assert "UI_QL_IMPORT_SET_CURSOR_POS = 86" in ui_public
    assert "UI_QL_IMPORT_GET_CURSOR_POS = 87" in ui_public
    assert "UI_QL_IMPORT_PC_ADD_GLOBAL_DEFINE = 88" in ui_public
    assert "UI_QL_IMPORT_GET_ITEM_DOWNLOAD_INFO = 96" in ui_public

    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert "return UI_QL_API_VERSION;" in ui_main
    assert "UI_RefreshDisplayContextScale" in ui_main
    assert "UI_DrawAdvertisementWaitScreen" in ui_main
    assert "Waiting on Advertisement" in ui_main
    assert "Press ESC to cancel" in ui_main
    assert "Waiting for new key... Press ESCAPE to cancel" in ui_main

    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    assert "qboolean Menus_AnyVisible()" in ui_shared

    vm_text = (REPO_ROOT / "src/code/qcommon/vm.c").read_text(encoding="utf-8")
    assert "case UI_REFRESH_DISPLAY_CONTEXT:" in vm_text
    assert "case UI_MENUS_ANY_VISIBLE:" in vm_text
    assert "case UI_FOR_EACH_ARENA_NAME:" in vm_text
    assert "case UI_DRAW_ADVERTISEMENT_WAIT_SCREEN:" in vm_text
    assert "VM_CallNativeExports(ui): callnum=" not in vm_text

    ui_vcxproj = (REPO_ROOT / "src/code/ui/ui.vcxproj").read_text(encoding="utf-8")
    debug_group = _extract_vcxproj_group(ui_vcxproj, "'$(Configuration)|$(Platform)'=='Debug|Win32'")
    release_group = _extract_vcxproj_group(ui_vcxproj, "'$(Configuration)|$(Platform)'=='Release|Win32'")
    assert "<ModuleDefinitionFile>.\\ui.def</ModuleDefinitionFile>" in debug_group
    assert "<ModuleDefinitionFile>.\\ui.def</ModuleDefinitionFile>" in release_group

    debug_exclusion = "<ExcludedFromBuild Condition=\"'$(Configuration)|$(Platform)'=='Debug|Win32'\">true</ExcludedFromBuild>"
    release_exclusion = "<ExcludedFromBuild Condition=\"'$(Configuration)|$(Platform)'=='Release|Win32'\">true</ExcludedFromBuild>"
    for include in (
        "..\\game\\bg_lib.c",
        "..\\game\\bg_misc.c",
        "..\\game\\q_math.c",
        "..\\game\\q_shared.c",
        "ui_atoms.c",
        "ui_cdkey.c",
        "ui_gameinfo.c",
        "ui_main.c",
        "ui_players.c",
        "ui_shared.c",
        "ui_util.c",
    ):
        compile_item = _extract_vcxproj_compile_item(ui_vcxproj, include)
        assert debug_exclusion not in compile_item
        assert release_exclusion not in compile_item


def test_ui_cdkey_runtime_wrapper_restored() -> None:
    ui_cdkey = (REPO_ROOT / "src/code/ui/ui_cdkey.c").read_text(encoding="utf-8")
    assert "UI_CDKeyMenu_OpenBridge" not in ui_cdkey
    assert 'Menus_ActivateByName( "ql_bridge_credentials" );' not in ui_cdkey
    assert "native CD-key popup fallback is not linked" in ui_cdkey
    assert "UI_PushMenu( &cdkeyMenuInfo.menu );" in ui_cdkey
    assert "void UI_CDKeyMenu_f( void ) {" in ui_cdkey

    ui_atoms = (REPO_ROOT / "src/code/ui/ui_atoms.c").read_text(encoding="utf-8")
    assert "UI_CDKeyMenu_Cache();" in ui_atoms
    assert 'Q_stricmp (cmd, "ui_cdkey")' not in ui_atoms

    q3asm = (REPO_ROOT / "src/code/ui/ui.q3asm").read_text(encoding="utf-8")
    assert "ui_cdkey" in q3asm

    ui_vcxproj = (REPO_ROOT / "src/code/ui/ui.vcxproj").read_text(encoding="utf-8")
    assert '<ClCompile Include="ui_cdkey.c">' in ui_vcxproj


def test_ui_retail_console_command_wrappers_restored() -> None:
    ui_atoms = (REPO_ROOT / "src/code/ui/ui_atoms.c").read_text(encoding="utf-8")
    assert 'Q_stricmp (cmd, "listPlayerModels")' in ui_atoms
    assert "UI_ListPlayerModels();" in ui_atoms
    assert 'Q_stricmp (cmd, "menu_close")' in ui_atoms
    assert "UI_ConsoleCommand_MenuClose();" in ui_atoms
    assert "Menus_CloseByName( menuName );" in ui_atoms
    assert 'Q_stricmp (cmd, "menu_open")' in ui_atoms
    assert "UI_ConsoleCommand_MenuOpen();" in ui_atoms
    assert "Menus_OpenByName( menuName );" in ui_atoms

    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")
    assert "void UI_ListPlayerModels( void );" in ui_local

    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert "void UI_ListPlayerModels( void ) {" in ui_main
    assert 'Com_Printf( "Player Models\\n" );' in ui_main
    assert "UI_CountPlayerModelEntries( qfalse );" in ui_main
    assert 'Com_Printf( "%s\\n", ui_playerModelEntries[i].modelName );' in ui_main
    assert 'Com_Printf( "%s/%s\\n", ui_playerModelEntries[i].modelName, ui_playerModelEntries[i].skinName );' in ui_main


def test_ui_player_model_catalog_matches_retail_skin_filtering() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert "static qboolean UI_PlayerModelSkinIsAlias( const char *skinName )" in ui_main
    assert 'Q_stricmp( skinName, "blue" ) == 0' in ui_main
    assert 'Q_stricmp( skinName, "bright" ) == 0' in ui_main
    assert 'Q_stricmp( skinName, "red" ) == 0' in ui_main
    assert 'Q_stricmp( skinName, "sport" ) == 0' in ui_main
    assert 'Q_stricmp( skinName, "sport_blue" ) == 0' in ui_main
    assert 'Q_stricmp( skinName, "sport_red" ) == 0' in ui_main
    assert "static qboolean UI_PlayerModelEntryHasSkin( int index )" in ui_main
    assert 'Com_sprintf( filename, sizeof( filename ), "models/players/%s/lower_%s.skin", entry->modelName, entry->skinName );' in ui_main


def test_ui_ownerdraw_force_model_previews_match_retail_ql() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ownerdraw_block = _extract_function_block(
        ui_main,
        "static void UI_OwnerDraw(float x, float y, float w, float h, float text_x, float text_y, int ownerDraw, int ownerDrawFlags, int align, float special, float scale, vec4_t color, qhandle_t shader, int textStyle) {",
    )

    assert "case UI_TEAMPLAYERMODEL:" in ownerdraw_block
    assert "case UI_ENEMYPLAYERMODEL:" in ownerdraw_block
    assert "case UI_REDTEAMMODEL:" in ownerdraw_block
    assert "case UI_BLUETEAMMODEL:" in ownerdraw_block

    assert "static void UI_DrawTeamPlayerModel( rectDef_t *rect )" in ui_main
    assert "static void UI_DrawEnemyPlayerModel( rectDef_t *rect )" in ui_main
    assert "static void UI_DrawRedTeamModel( rectDef_t *rect )" in ui_main
    assert "static void UI_DrawBlueTeamModel( rectDef_t *rect )" in ui_main

    assert '"ui_forceTeamModel"' in ui_main
    assert '"ui_forceEnemyModel"' in ui_main
    assert '"ui_forceTeamModelBright"' in ui_main
    assert '"ui_forceEnemyModelBright"' in ui_main
    assert '"ui_teamModelBright"' not in ui_main
    assert '"ui_enemyModelBright"' not in ui_main

    assert 'UI_CVAR_TABLE_CALLBACK( &ui_teamHeadColor, "ui_teamHeadColor", "0", CVAR_ARCHIVE, UI_UpdateRetailSliderColorCvar ),' in ui_main
    assert 'UI_CVAR_TABLE_CALLBACK( &ui_enemyHeadColor, "ui_enemyHeadColor", "0", CVAR_ARCHIVE, UI_UpdateRetailSliderColorCvar ),' in ui_main
    color_callback_block = _extract_function_block(
        ui_main,
        "static void UI_UpdateRetailSliderColorCvar( vmCvar_t *uiCvar ) {",
    )
    assert 'UI_SyncRetailSliderColorCvar( uiCvar, "cg_teamHeadColor" );' in color_callback_block
    assert 'UI_SyncRetailSliderColorCvar( uiCvar, "cg_enemyHeadColor" );' in color_callback_block
    assert "static int UI_CountPlayerModelEntries( qboolean skipAliasSkins )" in ui_main
    assert "UI_AddPlayerModelEntry( dirptr, skinname + 5, iconShaderName );" in ui_main
    assert "if ( UI_PlayerModelSkinIsAlias( ui_playerModelEntries[i].skinName ) ) {" in ui_main


def test_ui_cvar_table_reconstructs_retail_callback_lane() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")
    ui_hlil = UI_HLIL_PART01.read_text(encoding="utf-8", errors="ignore")

    struct_start = ui_main.index("typedef struct {\n\tvmCvar_t\t*vmCvar;")
    struct_block = ui_main[struct_start:ui_main.index("} cvarTable_t;", struct_start)]
    assert "uiCvarUpdate_t\tupdate;" in struct_block
    assert "int\t\t\tcvarFlags;" in struct_block
    assert struct_block.index("uiCvarUpdate_t\tupdate;") < struct_block.index("int\t\t\tcvarFlags;")

    assert "#define UI_CVAR_TABLE_ENTRY( vmCvar, cvarName, defaultString, cvarFlags ) \\" in ui_main
    assert "{ (vmCvar), (cvarName), (defaultString), NULL, (cvarFlags) }" in ui_main
    assert "#define UI_CVAR_TABLE_CALLBACK( vmCvar, cvarName, defaultString, cvarFlags, update ) \\" in ui_main
    assert "{ (vmCvar), (cvarName), (defaultString), (update), (cvarFlags) }" in ui_main
    assert "vmCvar_t\tui_version;" in ui_main
    assert "extern vmCvar_t\tui_version;" in ui_local

    init_block = _extract_function_block(ui_main, "void _UI_Init( qboolean inGameLoad ) {")
    assert 'trap_Cvar_Register(NULL, "debug_protocol", "", 0 );' in init_block
    assert 'trap_Cvar_Set("ui_actualNetGameType", va("%d", ui_netGameType.integer));' in init_block
    assert 'trap_Cvar_Register(&ui_version, "ui_version", QL_UI_VERSION, CVAR_ROM );' in init_block
    assert init_block.index('trap_Cvar_Set("ui_actualNetGameType", va("%d", ui_netGameType.integer));') < init_block.index('trap_Cvar_Register(&ui_version, "ui_version", QL_UI_VERSION, CVAR_ROM );')

    update_block = _extract_function_block(ui_main, "void UI_UpdateCvars( void ) {")
    assert "oldModificationCount = cv->vmCvar->modificationCount;" in update_block
    assert "trap_Cvar_Update( cv->vmCvar );" in update_block
    assert "&& oldModificationCount != 0" in update_block
    assert "&& oldModificationCount != cv->vmCvar->modificationCount" in update_block
    assert "cv->update( cv->vmCvar );" in update_block
    assert "uiTeamHeadColorModificationCount" not in ui_main
    assert "uiScreenDamageTeamModificationCount" not in ui_main

    assert "10011747  void** esi_1 = &data_1002afe0" in ui_hlil
    assert "1001174c  int32_t i_3 = 0x82" in ui_hlil
    assert "(*(data_106b40a8 + 0x10))(esi_1[-2], esi_1[-1], *esi_1, esi_1[2])" in ui_hlil
    assert 'char const data_1002665c[0x22] = "1069 win-x86 Jun  3 2016 16:09:57", 0' in ui_hlil
    assert 'char const data_10027e54[0xb] = "ui_version", 0' in ui_hlil
    assert "100118a3  void** esi = &data_1002afd8" in ui_hlil
    assert "100118a8  int32_t i_1 = 0x82" in ui_hlil
    assert "result = esi[3]" in ui_hlil
    assert "if (result != 0 && edi_1 != 0)" in ui_hlil
    assert "if (edi_1 != *(ecx_3 + 4))" in ui_hlil
    assert "result = result(ecx_3)" in ui_hlil


def test_ui_cvar_table_reconstructs_retail_slider_color_callbacks() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")
    ui_hlil = UI_HLIL_PART01.read_text(encoding="utf-8", errors="ignore")

    assert "vmCvar_t\tui_enemyColor;" in ui_main
    assert "vmCvar_t\tui_teamColor;" in ui_main
    assert "extern vmCvar_t\tui_enemyColor;" in ui_local
    assert "extern vmCvar_t\tui_teamColor;" in ui_local
    assert 'UI_CVAR_TABLE_CALLBACK( &ui_enemyColor, "ui_enemyColor", "0", CVAR_ARCHIVE, UI_UpdateRetailSliderColorCvar ),' in ui_main
    assert 'UI_CVAR_TABLE_CALLBACK( &ui_teamColor, "ui_teamColor", "0", CVAR_ARCHIVE, UI_UpdateRetailSliderColorCvar ),' in ui_main

    color_callback_block = _extract_function_block(
        ui_main,
        "static void UI_UpdateRetailSliderColorCvar( vmCvar_t *uiCvar ) {",
    )
    team_bulk_block = color_callback_block[
        color_callback_block.index("if ( uiCvar == &ui_teamColor ) {"):
        color_callback_block.index("if ( uiCvar == &ui_enemyColor ) {")
    ]
    enemy_bulk_block = color_callback_block[
        color_callback_block.index("if ( uiCvar == &ui_enemyColor ) {"):
        color_callback_block.index("if ( uiCvar == &ui_teamHeadColor ) {")
    ]
    assert team_bulk_block.index('"cg_teamUpperColor"') < team_bulk_block.index('"cg_teamLowerColor"')
    assert team_bulk_block.index('"cg_teamLowerColor"') < team_bulk_block.index('"cg_teamHeadColor"')
    assert enemy_bulk_block.index('"cg_enemyUpperColor"') < enemy_bulk_block.index('"cg_enemyLowerColor"')
    assert enemy_bulk_block.index('"cg_enemyLowerColor"') < enemy_bulk_block.index('"cg_enemyHeadColor"')

    for target in (
        '"cg_teamHeadColor"',
        '"cg_teamUpperColor"',
        '"cg_teamLowerColor"',
        '"cg_enemyHeadColor"',
        '"cg_enemyUpperColor"',
        '"cg_enemyLowerColor"',
        '"cg_screenDamage"',
        '"cg_screenDamage_Team"',
    ):
        assert target in color_callback_block

    assert 'data_1002b258 = 0x107404c0' in ui_hlil
    assert 'data_1002b25c)[0xe] = data_10026240 {"ui_enemyColor"}' in ui_hlil
    assert "data_1002b264 = sub_10011240" in ui_hlil
    assert 'data_1002b974 = 0x1073fbc0' in ui_hlil
    assert 'data_1002b978)[0xd] = data_10025ec4 {"ui_teamColor"}' in ui_hlil
    assert "data_1002b980 = sub_10011240" in ui_hlil
    assert "10011240    void sub_10011240(float arg1)" in ui_hlil
    assert '"cg_teamUpperColor", sub_10001900("0x%08x")' in ui_hlil
    assert '"cg_enemyUpperColor", sub_10001900("0x%08x")' in ui_hlil
    assert '"cg_screenDamage_Team", sub_10001900("0x%08x")' in ui_hlil


def test_ui_cvar_table_reconstructs_retail_force_model_and_announcer_callbacks() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_hlil = UI_HLIL_PART01.read_text(encoding="utf-8", errors="ignore")

    assert 'UI_CVAR_TABLE_CALLBACK( &ui_forceEnemyModel, "ui_forceEnemyModel", "", CVAR_ARCHIVE, UI_UpdateForceEnemyModelSettings ),' in ui_main
    assert 'UI_CVAR_TABLE_CALLBACK( &ui_forceEnemySkin, "ui_forceEnemySkin", "", CVAR_ARCHIVE, UI_UpdateForceEnemyModelSettings ),' in ui_main
    assert 'UI_CVAR_TABLE_CALLBACK( &ui_forceTeamModel, "ui_forceTeamModel", "", CVAR_ARCHIVE, UI_UpdateForceTeamModelSettings ),' in ui_main
    assert 'UI_CVAR_TABLE_CALLBACK( &ui_forceTeamSkin, "ui_forceTeamSkin", "", CVAR_ARCHIVE, UI_UpdateForceTeamModelSettings ),' in ui_main
    assert 'UI_CVAR_TABLE_CALLBACK( &ui_announcer, "cg_announcer", "1", CVAR_ARCHIVE, UI_UpdateAnnouncer ),' in ui_main

    announcer_block = _extract_function_block(ui_main, "static void UI_UpdateAnnouncer( vmCvar_t *uiCvar ) {")
    assert 'sample = "sound/misc/vo_evil.wav";' in announcer_block
    assert 'sample = "sound/misc/vo_female.wav";' in announcer_block
    assert 'sample = "sound/misc/vo_default.wav";' in announcer_block
    assert "trap_S_StartLocalSound( sound, CHAN_ANNOUNCER );" in announcer_block
    assert 'trap_Cvar_Set( "ui_announcer", va( "%i", uiCvar->integer ) );' in announcer_block

    assert 'data_1002afdc)[0xd] = data_1002641c {"cg_announcer"}' in ui_hlil
    assert "data_1002afe4 = sub_10011690" in ui_hlil
    assert "10011640  int32_t eax" in ui_hlil
    assert 'sub_10011510(eax, edx, "cg_forceTeamSkin", "cg_forceTeamModel")' in ui_hlil
    assert "data_1002b304 = sub_10011630" in ui_hlil
    assert 'sub_10011510(eax, edx, "cg_forceEnemySkin", "cg_forceEnemyModel")' in ui_hlil
    assert "data_1002b2c8 = sub_10011660" in ui_hlil
    assert '"sound/misc/vo_default.wav", 7' in ui_hlil
    assert '"sound/misc/vo_evil.wav", 7' in ui_hlil
    assert '"sound/misc/vo_female.wav", 7' in ui_hlil
    assert '("ui_announcer", sub_10001900(&data_10025920))' in ui_hlil


def test_ui_startup_uses_retail_teaminfo_path() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert "static const char *UI_GetRetailMenuPathAlias( const char *filename ) {" in ui_main
    assert 'if ( !Q_stricmp( filename, "teaminfo.txt" ) ) {' in ui_main
    assert 'return "ui/teaminfo.txt";' in ui_main
    assert 'if ( !Q_stricmp( filename, "country.txt" ) ) {' in ui_main
    assert 'return "ui/country.txt";' in ui_main

    init_block = _extract_function_block(ui_main, "void _UI_Init( qboolean inGameLoad ) {")
    assert 'UI_ParseTeamInfo("ui/teaminfo.txt");' in init_block
    assert 'UI_ParseTeamInfo("teaminfo.txt");' not in init_block
    assert "UI_LoadTeams();" not in init_block
    assert 'UI_ParseGameInfo("gameinfo.txt");' not in init_block
    assert 'buff = GetMenuBuffer("ui/country.txt");' in ui_main
    assert 'buff = GetMenuBuffer("country.txt");' not in ui_main


def test_ui_project_outputs_runtime_dll_to_launcher_build_tree() -> None:
    ui_vcxproj = (REPO_ROOT / "src/code/ui/ui.vcxproj").read_text(encoding="utf-8")
    assert "<OutDir>$(ProjectDir)..\\..\\..\\build\\win32\\$(Configuration)\\bin\\baseq3\\" in ui_vcxproj
    assert "<IntDir>$(ProjectDir)..\\..\\..\\build\\win32\\$(Configuration)\\obj\\$(ProjectName)\\" in ui_vcxproj
    assert "$(SolutionDir)..\\..\\build\\win32\\$(Configuration)\\bin\\baseq3\\" not in ui_vcxproj


def test_ui_retail_gameinfo_paths_do_not_bootstrap_map_rotation_cache() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")

    load_block = _extract_function_block(ui_main, "void UI_Load() {")
    assert 'UI_ParseGameInfo("gameinfo.txt");' in load_block
    assert "UI_LoadArenas();" in load_block
    assert "UI_LoadMapRotations();" not in load_block
    assert "UI_LoadRulesets();" not in load_block

    init_block = _extract_function_block(ui_main, "void _UI_Init( qboolean inGameLoad ) {")
    assert 'UI_ParseGameInfo("gameinfo.txt");' not in init_block
    assert "UI_LoadMapRotations();" not in init_block
    assert "UI_LoadRulesets();" not in init_block

    run_menu_script_block = _extract_function_block(
        ui_main, "static void UI_RunMenuScript(char **args) {"
    )
    assert '} else if (Q_stricmp(name, "loadGameInfo") == 0) {' in run_menu_script_block
    assert 'UI_ParseGameInfo("gameinfo.txt");' in run_menu_script_block
    assert "UI_LoadBestScores(uiInfo.mapList[ui_currentMap.integer].mapLoadName, uiInfo.gameTypes[ui_gameType.integer].gtEnum);" in run_menu_script_block
    load_gameinfo_slice = run_menu_script_block[
        run_menu_script_block.index('} else if (Q_stricmp(name, "loadGameInfo") == 0) {'):
        run_menu_script_block.index('} else if (Q_stricmp(name, "resetScores") == 0) {')
    ]
    assert "UI_LoadMapRotations();" not in load_gameinfo_slice


def test_ui_arena_file_loader_matches_retail_catalog_limits_and_tokens() -> None:
    ui_gameinfo = (REPO_ROOT / "src/code/ui/ui_gameinfo.c").read_text(encoding="utf-8")
    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")
    bg_public = (REPO_ROOT / "src/code/game/bg_public.h").read_text(encoding="utf-8")

    arena_type_block = _extract_function_block(ui_gameinfo, "static int UI_ArenaTypeBits( const char *type ) {")
    load_block = _extract_function_block(ui_gameinfo, "void UI_LoadArenas( void ) {")

    assert "#define MAX_MAPS 256" in ui_local
    assert "#define\tMAX_ARENAS_TEXT\t\t0x4000" in bg_public
    assert '#include "../../game/match_state_keys.h"' in ui_gameinfo
    assert 'trap_FS_GetFileList("scripts", ".arena", dirlist, 1024 );' in load_block
    assert '"WARNING: not enough memory in pool to load all arenas\\n"' in load_block
    assert '"WARNING: not anough memory in pool to load all arenas\\n"' not in load_block
    assert "Info_ValueForKey(ui_arenaInfos[n], ARENA_INFO_KEY_MAP)" in load_block
    assert "Info_ValueForKey(ui_arenaInfos[n], ARENA_INFO_KEY_LONGNAME)" in load_block
    assert 'String_Alloc(va("levelshots/preview/%s", uiInfo.mapList[uiInfo.mapCount].mapLoadName))' in load_block
    assert "UI_ArenaTypeBits( Info_ValueForKey( ui_arenaInfos[n], ARENA_INFO_KEY_TYPE ) )" in load_block

    for expected in (
        'strstr( type, "duel" )',
        'strstr( type, "race" )',
        'strstr( type, "tdm" )',
        'strstr( type, "ca" )',
        'strstr( type, "oneflag" )',
        'strstr( type, "overload" )',
        'strstr( type, "hh" )',
        'strstr( type, "har" )',
        'strstr( type, "ft" )',
        'strstr( type, "dom" )',
        'strstr( type, "ad" )',
        'strstr( type, "rr" )',
    ):
        assert expected in arena_type_block

    for forbidden in (
        '"single"',
        '"team"',
        '"clanarena"',
        '"harvester"',
        '"freeze"',
        '"freezetag"',
        '"domination"',
        '"attackdefend"',
        '"redrover"',
    ):
        assert forbidden not in arena_type_block


def test_ui_retail_ruleset_cache_scaffolding_is_removed() -> None:
    ui_gameinfo = (REPO_ROOT / "src/code/ui/ui_gameinfo.c").read_text(encoding="utf-8")
    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")

    for removed in (
        "#define MAX_RULESETS 8",
        "} rulesetInfo_t;",
        "void UI_LoadRulesets( void );",
        "int rulesetCount;",
        "int rulesetIndex;",
        "rulesetInfo_t rulesets[MAX_RULESETS];",
        "char activeRuleset[MAX_CVAR_VALUE_STRING];",
    ):
        assert removed not in ui_local

    for removed in (
        "UI_ClearRulesets",
        "UI_AddRulesetFromToken",
        "UI_LoadRulesets",
        "ui_rulesets",
        "g_ruleset",
        "defaultRulesets[]",
        "uiInfo.rulesetCount",
        "uiInfo.rulesetIndex",
        "uiInfo.rulesets",
        "uiInfo.activeRuleset",
    ):
        assert removed not in ui_gameinfo

    load_block = _extract_function_block(ui_main, "void UI_Load() {")
    assert "UI_LoadRulesets();" not in load_block


def test_ui_dead_postgame_popup_helper_is_removed() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")

    assert "UI_ActivateCompatibilityPostgame" not in ui_main
    assert "void UI_ShowPostGame(qboolean newHigh);" not in ui_local
    assert "void UI_ShowPostGame(qboolean newHigh) {" not in ui_main


def test_ui_dead_legacy_helper_band_is_removed() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")

    for removed in (
        "static uiMenuFlow_t UI_RequestedMenuFlow(void) {",
        "qboolean UI_UsingLegacyMenuFlow(void) {",
        "static void UI_LoadTeams() {",
        "static const char *UI_ValidateCountryCode(const char *code) {",
    ):
        assert removed not in ui_main

    assert "qboolean UI_UsingLegacyMenuFlow(void);" not in ui_local

    resolve_menu_flow_block = _extract_function_block(
        ui_main, "static uiMenuFlow_t UI_ResolveMenuFlowInternal(void) {"
    )
    load_menus_block = _extract_function_block(
        ui_main, "void UI_LoadMenus(const char *menuFile, qboolean reset) {"
    )
    assert "return UI_MENU_FLOW_QUAKELIVE;" in resolve_menu_flow_block
    assert "UI_BrowserBridgeAvailable()" not in resolve_menu_flow_block
    assert "UI_RequestedMenuFlow" not in resolve_menu_flow_block
    assert "static qboolean UI_MenuFlowUsesBrowserOverlay(uiMenuFlow_t flow) {" in ui_main
    assert "static qboolean UI_ShouldUseResolvedMenuFile(const char *menuFile) {" in ui_main
    assert "UI_SetBrowserActive(flow == UI_MENU_FLOW_QUAKELIVE);" not in ui_main
    assert "UI_SetBrowserActive(ui_activeMenuFlow == UI_MENU_FLOW_QUAKELIVE);" not in ui_main
    assert "UI_SetBrowserActive(UI_MenuFlowUsesBrowserOverlay(ui_activeMenuFlow));" in load_menus_block


def test_ui_browser_active_state_does_not_write_client_owned_rom_cvar() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")

    browser_active_block = _extract_function_block(
        ui_main, "static void UI_SetBrowserActive(qboolean active) {"
    )
    init_block = _extract_function_block(ui_main, "void _UI_Init( qboolean inGameLoad ) {")

    assert "ui_browserActiveState = active;" in browser_active_block
    assert "ui_browserActiveKnown = qtrue;" in browser_active_block
    assert "web_browserActive 1" not in browser_active_block
    assert "web_browserActive 0" not in browser_active_block
    assert 'trap_Cmd_ExecuteText(EXEC_NOW, active ? "web_browserActive' not in browser_active_block
    assert 'trap_Cvar_Set("web_browserActive", "0");' not in init_block
    assert "UI_SetBrowserActive(qfalse);" in init_block


def test_ui_menu_flow_uses_retail_roots_when_overlay_is_absent() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_atoms = (REPO_ROOT / "src/code/ui/ui_atoms.c").read_text(encoding="utf-8")
    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")

    selector_block = _extract_function_block(
        ui_main, "static qboolean UI_ShouldUseResolvedMenuFile(const char *menuFile) {"
    )
    load_block = _extract_function_block(ui_main, "void UI_Load() {")
    init_block = _extract_function_block(ui_main, "void _UI_Init( qboolean inGameLoad ) {")
    noningame_block = _extract_function_block(ui_main, "void UI_LoadNonIngame() {")
    console_command_block = _extract_function_block(ui_atoms, "qboolean UI_ConsoleCommand( int realTime ) {")

    assert "qboolean UI_OpenBrowserBridgeMenu( void );" not in ui_local
    assert "UI_MENU_FILE_QUAKELIVE_BRIDGE" not in ui_local
    assert "UI_MenuFileEquals(menuFile, UI_MENU_FILE_QUAKELIVE)" in selector_block
    assert "UI_MENU_FILE_QUAKELIVE_BRIDGE" not in selector_block
    assert "if (UI_ShouldUseResolvedMenuFile(menuSet)) {\n\t\tmenuSet = UI_DefaultMenuFile();" in load_block
    assert "if (UI_ShouldUseResolvedMenuFile(menuSet)) {\n                menuSet = UI_DefaultMenuFile();" in init_block
    assert "if (UI_ShouldUseResolvedMenuFile(menuSet)) {\n                menuSet = UI_DefaultMenuFile();" in noningame_block
    assert 'Com_Printf("UI: browser overlay unavailable; web_showBrowser stubbed.\\n");' in console_command_block


def test_ui_service_disabled_exec_paths_keep_menu_flow_navigable() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")
    main_menu = (REPO_ROOT / "src/ui/main.menu").read_text(encoding="utf-8")
    intro_menu = (REPO_ROOT / "src/ui/intro.menu").read_text(encoding="utf-8")
    ingame_menu = (REPO_ROOT / "src/ui/ingame.menu").read_text(encoding="utf-8")
    lowernav_menu = (REPO_ROOT / "src/ui/ingame_lowernav.menu").read_text(encoding="utf-8")

    deferred_exec_block = _extract_function_block(
        ui_main, "qboolean UI_HandleDeferredScriptExec( const itemDef_t *item, const char *commandText ) {"
    )
    script_exec_block = _extract_function_block(ui_shared, "void Script_Exec(itemDef_t *item, char **args) {")
    connect_block = _extract_function_block(ui_main, "void UI_DrawConnectScreen( qboolean overlay ) {")
    advert_wait_block = _extract_function_block(
        ui_main, "static void UI_DrawAdvertisementWaitScreen(const char *menuName) {"
    )

    assert "qboolean UI_HandleDeferredScriptExec( const itemDef_t *item, const char *commandText );" in ui_local
    assert 'UI_CommandTextMatches( commandText, "web_showBrowser" )' in deferred_exec_block
    assert 'UI_CommandTextMatches( commandText, "web_changeHash" )' in deferred_exec_block
    assert "UI_OpenBrowserBridgeMenu()" not in deferred_exec_block
    assert 'UI_ShowOfflineMenuFallbackError( "Browser overlay unavailable; retail menu remains active." );' in deferred_exec_block
    assert 'Com_Printf( "UI: browser overlay unavailable; keeping retail menu fallback for %s.\\n", commandText );' in deferred_exec_block

    assert "#ifndef CGAME" in script_exec_block
    assert "if ( UI_HandleDeferredScriptExec( item, val ) ) {" in script_exec_block
    assert 'DC->executeText(EXEC_APPEND, va("%s ; ", val));' in script_exec_block

    assert "action { exec web_showBrowser }" in main_menu
    assert 'action { exec "web_changeHash /"  ; open ingame_about ;' in intro_menu
    assert 'action { exec "web_changeHash /settings" ; open ingame_about ;' in intro_menu
    assert 'action { exec "web_changeHash /" ; open ingame_about ;' in ingame_menu
    assert 'action { exec "web_changeHash /settings" ; open ingame_about ;' in ingame_menu
    assert 'action { open ingame_about ; exec "web_showBrowser" }' in lowernav_menu

    assert 'menuDef_t *menu = Menus_FindByName("Connect");' in connect_block
    assert 'Text_PaintCenter(centerPoint, yStart + 48, scale, colorWhite, va("Starting up..."), 0);' in connect_block
    assert 'Text_PaintCenter(centerPoint, yStart + 48, scale, colorWhite,text , 0);' in connect_block
    assert 'strcpy(text, va("Connecting to %s", cstate.servername));' in connect_block
    assert 'Text_PaintCenter(centerPoint, yStart + 80, scale, colorWhite, s, 0);' in connect_block
    assert 'Text_PaintCenter(centerPoint, 440, scale, colorWhite, "Press ESC to cancel", 0);' in connect_block

    assert 'static const char *waitingText = "Waiting on Advertisement";' in advert_wait_block
    assert 'static const char *cancelText = "Press ESC to cancel";' in advert_wait_block
    assert "Menus_FindByName(menuName);" in advert_wait_block
    assert "Menu_Paint(menu, qtrue);" in advert_wait_block


def test_ui_qmenu_widget_core_boundary_notes_are_explicitly_bounded() -> None:
    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")
    qmenu_note = (
        REPO_ROOT / "docs/reverse-engineering/ui-qmenu-struct-layouts.md"
    ).read_text(encoding="utf-8")
    mapping_round = (
        REPO_ROOT / "docs/reverse-engineering/ui-mapping-round-2026-04-01.md"
    ).read_text(encoding="utf-8")
    parity_plan = (
        REPO_ROOT
        / "docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md"
    ).read_text(encoding="utf-8")

    for helper in (
        "Menu_AddItem",
        "Menu_Draw",
        "Menu_DefaultKey",
        "MField_Draw",
        "ScrollList_Key",
    ):
        assert helper in ui_local
        assert f"`{helper}`" in qmenu_note
        assert f"`{helper}`" in mapping_round

    assert "## Phase 4 Ownership Closure (2026-04-06)" in qmenu_note
    assert "source-backed compatibility helpers" in qmenu_note
    assert "No unresolved high-impact ownership gap remains in an active runtime path." in qmenu_note

    assert "## Phase 4 Closure Update (2026-04-06)" in mapping_round
    assert "no new aliases were" in mapping_round
    assert "promoted in this pass" in mapping_round
    assert 'open-ended "missing retail owner" bucket' in mapping_round
    assert "No unresolved high-impact ownership gap remains in an active runtime path." in mapping_round

    assert "Overall estimated UI module parity (behavior + data + assets + integration): **100%**." in parity_plan
    assert "### UI-G04: Residual qmenu widget-core ownership uncertainty [Closed on 2026-04-06]" in parity_plan
    assert "Remaining risk is limited to future-evidence alias promotion rather than current runtime uncertainty." in parity_plan
    assert "- **UI-P4:** qmenu/widget-core boundary mapping pass. `[completed 2026-04-06]`" in parity_plan


def test_ui_phase6_runtime_evidence_artifact_closes_full_parity_plan() -> None:
    parity_plan = (
        REPO_ROOT
        / "docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md"
    ).read_text(encoding="utf-8")
    scripting_guide = (REPO_ROOT / "docs/ui/scripting-guide.md").read_text(encoding="utf-8")
    runtime_evidence = json.loads(
        (REPO_ROOT / "artifacts/ui_validation/logs/ui_runtime_evidence_20260406.json").read_text(encoding="utf-8")
    )

    assert runtime_evidence["phase"] == "UI-P6"
    assert runtime_evidence["parity_estimate"] == {"before": 97, "after": 100}
    assert set(runtime_evidence["ingame_runtime_flow"]["stages"]) == {
        "ingame",
        "spectator",
        "scoreboard",
        "vote",
        "ingamemenu",
    }
    assert runtime_evidence["parser_errors"] == []
    assert runtime_evidence["blocking_service_script_failures"] == []

    stage_hashes = {
        runtime_evidence["ingame_runtime_flow"]["stages"][stage]["window_sha256"]
        for stage in runtime_evidence["ingame_runtime_flow"]["stages"]
    }
    assert len(stage_hashes) == 5

    assert "**Status:** Completed on 2026-04-06 via `artifacts/ui_validation/logs/ui_runtime_evidence_20260406.json`" in parity_plan
    assert "- **UI-P6:** Final runtime parity evidence pass and closure report. `[completed 2026-04-06]`" in parity_plan
    assert "artifacts/ui_validation/logs/ui_runtime_evidence_20260406.json" in scripting_guide


def test_ui_runtime_ingame_join_matches_retail_and_fixup_stays_defensive(
    retail_ui_corpus_inventory: dict[str, object],
) -> None:
    if not retail_ui_corpus_inventory["retail_ui_corpus_available"]:
        pytest.skip(inventory_missing_reason(retail_ui_corpus_inventory))

    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    src_join = (REPO_ROOT / "src/ui/ingame_join.menu").read_text(encoding="utf-8")
    retail_join = read_retail_root_file(
        DEFAULT_BASEQ3_ROOT / "ui",
        "ingame_join.menu",
    ).decode("utf-8")

    assert src_join == retail_join
    for expected in (
        "name country_label",
        "name country_list",
        "feeder FEEDER_COUNTRIES",
    ):
        assert expected not in src_join
        assert expected not in retail_join

    fixup_block = _extract_function_block(ui_main, "static void UI_ApplyRetailMenuFixups( void ) {")
    assert "defensive no-op seam" in ui_main
    assert 'menu = Menus_FindByName( "ingame_join" );' in fixup_block
    assert 'Menu_ShowItemByName( menu, "country_label", qfalse );' in fixup_block
    assert 'Menu_ShowItemByName( menu, "country_list", qfalse );' in fixup_block

    load_block = _extract_function_block(ui_main, "void UI_Load() {")
    assert "UI_ApplyRetailMenuFixups();" in load_block

    init_block = _extract_function_block(ui_main, "void _UI_Init( qboolean inGameLoad ) {")
    assert "UI_ApplyRetailMenuFixups();" in init_block


def test_ui_best_score_loader_skips_unseeded_metadata_probes() -> None:
    ui_atoms = (REPO_ROOT / "src/code/ui/ui_atoms.c").read_text(encoding="utf-8")

    load_best_scores_block = _extract_function_block(
        ui_atoms, "void UI_LoadBestScores(const char *map, int game) {"
    )
    assert "uiInfo.demoAvailable = qfalse;" in load_best_scores_block
    assert "if ( !map || !map[0] || game < 0 || game >= GT_MAX_GAME_TYPE ) {" in load_best_scores_block
    assert "UI_SetBestScores(&newInfo, qfalse);" in load_best_scores_block
    assert 'Com_sprintf(fileName, MAX_QPATH, "games/%s_%i.game", map, game);' in load_best_scores_block
    assert 'Com_sprintf(fileName, MAX_QPATH, "demos/%s_%d.dm_%d", map, game, (int)trap_Cvar_VariableValue("protocol"));' in load_best_scores_block


def test_ui_retail_ownerdraw_extensions_restored() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_shared_h = (REPO_ROOT / "src/code/ui/ui_shared.h").read_text(encoding="utf-8")
    asset_cache_block = _extract_function_block(ui_main, "void AssetCache() {")
    vote_block = _extract_function_block(
        ui_main, "static void UI_DrawVoteString(rectDef_t *rect, float scale, vec4_t color, int textStyle)"
    )

    assert "#define\tNUM_CROSSHAIRS\t\t\t30" in ui_shared_h
    assert "#define UI_CROSSHAIR_COLOR_COUNT\t26" in ui_main
    assert "static void UI_DrawCrosshairColor( rectDef_t *rect )" in ui_main
    assert 'trap_Cvar_VariableValue( "cg_crosshairColor" )' in ui_main
    assert "case UI_CROSSHAIR_COLOR:" in ui_main
    assert "return UI_CrosshairColor_HandleKey(flags, special, key);" in ui_main
    assert "case UI_VOTESTRING:" in ui_main
    assert "UI_DrawVoteString(&rect, scale, color, textStyle);" in ui_main
    assert "char voteString[MAX_INFO_STRING];" in vote_block
    assert 'trap_Cvar_VariableStringBuffer( "ui_votestring", voteString, sizeof( voteString ) );' in vote_block
    assert "paintX = (int)rect->x;" in vote_block
    assert "textWidth = Text_Width( voteString, scale, 0 );" in vote_block
    assert "paintX -= textWidth / 2;" in vote_block
    assert "Text_Paint( (float)paintX, rect->y, scale, color, voteString, 0, 0, textStyle );" in vote_block
    assert 'UI_Cvar_VariableString("ui_votestring")' not in vote_block
    assert "rect->w - Text_Width" not in vote_block
    assert "for ( n = 1; n < NUM_CROSSHAIRS; n++ ) {" in asset_cache_block
    assert 'trap_R_RegisterShaderNoMip( va( "gfx/2d/crosshair%d", n ) );' in asset_cache_block
    assert "crosshair%c" not in asset_cache_block


def test_ui_retail_ownerdraw_visibility_cvar_gates_match_ql() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    visible_block = _extract_function_block(
        ui_main,
        "static qboolean UI_OwnerDrawVisibleFlags( int flags ) {",
    )

    for expected in (
        "if (flags & UI_SHOW_IF_LOADOUT_ENABLED) {",
        'if (trap_Cvar_VariableValue("cg_loadout") != 1.0f) {',
        "flags &= ~UI_SHOW_IF_LOADOUT_ENABLED;",
        "if (flags & UI_SHOW_IF_LOADOUT_DISABLED) {",
        'if (trap_Cvar_VariableValue("cg_loadout") == 1.0f) {',
        "flags &= ~UI_SHOW_IF_LOADOUT_DISABLED;",
        "if (flags & UI_SHOW_IF_NOT_INTERMISSION) {",
        'if (trap_Cvar_VariableValue("ui_intermission") == 1.0f) {',
        "flags &= ~UI_SHOW_IF_NOT_INTERMISSION;",
        "if (flags & UI_SHOW_IF_WARMUP) {",
        'if (trap_Cvar_VariableValue("ui_warmup") >= 0.0f) {',
        "flags &= ~UI_SHOW_IF_WARMUP;",
        "if (flags & UI_SHOW_IF_NOT_WARMUP) {",
        'if (trap_Cvar_VariableValue("ui_warmup") < 0.0f) {',
        "flags &= ~UI_SHOW_IF_NOT_WARMUP;",
    ):
        assert expected in visible_block

    order = (
        "if (flags & UI_SHOW_IF_LOADOUT_ENABLED) {",
        "if (flags & UI_SHOW_IF_LOADOUT_DISABLED) {",
        "if (flags & UI_SHOW_IF_NOT_INTERMISSION) {",
        "if (flags & UI_SHOW_IF_WARMUP) {",
        "if (flags & UI_SHOW_IF_NOT_WARMUP) {",
        "if (flags & UI_SHOW_ANYTEAMGAME) {",
    )
    assert [visible_block.index(marker) for marker in order] == sorted(
        visible_block.index(marker) for marker in order
    )


def test_ui_retail_gametype_selector_ownerdraws_match_ql() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    draw_game_block = _extract_function_block(ui_main, "static void UI_DrawGameType")
    draw_net_block = _extract_function_block(ui_main, "static void UI_DrawNetGameType")
    draw_join_block = _extract_function_block(ui_main, "static void UI_DrawJoinGameType")
    game_key_block = _extract_function_block(ui_main, "static qboolean UI_GameType_HandleKey")
    net_visible_block = _extract_function_block(ui_main, "static qboolean UI_NetGameTypeVisible")
    net_key_block = _extract_function_block(ui_main, "static qboolean UI_NetGameType_HandleKey")
    join_key_block = _extract_function_block(ui_main, "static qboolean UI_JoinGameType_HandleKey")
    draw_dispatch_block = _extract_function_block(
        ui_main,
        "static void UI_OwnerDraw(float x, float y, float w, float h, float text_x, float text_y, int ownerDraw, int ownerDrawFlags, int align, float special, float scale, vec4_t color, qhandle_t shader, int textStyle) {",
    )
    key_dispatch_block = _extract_function_block(
        ui_main, "static qboolean UI_OwnerDrawHandleKey(int ownerDraw, int flags, float *special, int key) {"
    )

    assert "Text_Paint(rect->x, rect->y, scale, color, uiInfo.gameTypes[ui_gameType.integer].gameType, 0, 0, textStyle);" in draw_game_block
    assert "case UI_GAMETYPE:" in draw_dispatch_block
    assert "UI_DrawGameType(&rect, scale, color, textStyle);" in draw_dispatch_block
    assert "return UI_GameType_HandleKey(flags, special, key, qtrue);" in key_dispatch_block
    assert "if (ui_gameType.integer == 2) {" in game_key_block
    assert "ui_gameType.integer = 3;" in game_key_block
    assert 'trap_Cvar_Set("ui_gameType", va("%d", ui_gameType.integer));' in game_key_block
    assert "UI_SetCapFragLimits(qtrue);" in game_key_block
    assert "UI_LoadBestScores(uiInfo.mapList[ui_currentMap.integer].mapLoadName, uiInfo.gameTypes[ui_gameType.integer].gtEnum);" in game_key_block
    assert "ui_Q3Model" not in game_key_block

    assert 'trap_Cvar_Set("ui_netGameType", "0");' in draw_net_block
    assert 'trap_Cvar_Set("ui_actualNetGameType", "0");' in draw_net_block
    assert "Text_Paint(rect->x, rect->y, scale, color, uiInfo.gameTypes[ui_netGameType.integer].gameType , 0, 0, textStyle);" in draw_net_block
    assert "case UI_NETGAMETYPE:" in draw_dispatch_block
    assert "UI_DrawNetGameType(&rect, scale, color, textStyle);" in draw_dispatch_block
    assert "UI_NetGameType_HandleKey(flags, special, key);" in key_dispatch_block
    assert "gtEnum = uiInfo.gameTypes[gameTypeIndex].gtEnum;" in net_visible_block
    assert "gtEnum != GT_1FCTF &&" in net_visible_block
    assert "gtEnum != GT_OBELISK &&" in net_visible_block
    assert "gtEnum != GT_HARVESTER;" in net_visible_block
    assert "direction = ( key == K_MOUSE2 ) ? -1 : 1;" in net_key_block
    assert "ui_netGameType.integer += direction;" in net_key_block
    assert "} while ( guard < uiInfo.numGameTypes && !UI_NetGameTypeVisible( ui_netGameType.integer ) );" in net_key_block
    assert 'trap_Cvar_Set( "ui_actualnetGameType", va("%d", uiInfo.gameTypes[ui_netGameType.integer].gtEnum));' in net_key_block
    assert 'trap_Cvar_Set( "ui_currentNetMap", "0");' in net_key_block
    assert "UI_MapCountByGameType(qfalse);" in net_key_block
    assert "Menu_SetFeederSelection(NULL, FEEDER_ALLMAPS, 0, NULL);" in net_key_block

    assert 'trap_Cvar_Set("ui_joinGameType", "0");' in draw_join_block
    assert "Text_Paint(rect->x, rect->y, scale, color, uiInfo.joinGameTypes[ui_joinGameType.integer].gameType , 0, 0, textStyle);" in draw_join_block
    assert "case UI_JOINGAMETYPE:" in draw_dispatch_block
    assert "UI_DrawJoinGameType(&rect, scale, color, textStyle);" in draw_dispatch_block
    assert "UI_JoinGameType_HandleKey(flags, special, key);" in key_dispatch_block
    assert 'trap_Cvar_Set( "ui_joinGameType", va("%d", ui_joinGameType.integer));' in join_key_block
    assert "UI_BuildServerDisplayList(qtrue);" in join_key_block


def test_ui_retail_skill_mappreview_maptime_ownerdraws_match_ql() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ghidra_reference = (
        REPO_ROOT / "references/reverse-engineering/ghidra/uix86/ui_ghidra_reference.h"
    ).read_text(encoding="utf-8")
    hlil = UI_HLIL_PART01.read_text(encoding="utf-8")
    draw_skill_block = _extract_function_block(
        ui_main, "static void UI_DrawSkill(rectDef_t *rect, float scale, vec4_t color, int textStyle) {"
    )
    draw_preview_block = _extract_function_block(
        ui_main, "static void UI_DrawMapPreview(rectDef_t *rect, float scale, vec4_t color, qboolean net) {"
    )
    draw_time_block = _extract_function_block(
        ui_main, "static void UI_DrawMapTimeToBeat(rectDef_t *rect, float scale, vec4_t color, int textStyle) {"
    )
    skill_key_block = _extract_function_block(
        ui_main, "static qboolean UI_Skill_HandleKey(int flags, float *special, int key) {"
    )
    draw_dispatch_block = _extract_function_block(
        ui_main,
        "static void UI_OwnerDraw(float x, float y, float w, float h, float text_x, float text_y, int ownerDraw, int ownerDrawFlags, int align, float special, float scale, vec4_t color, qhandle_t shader, int textStyle) {",
    )
    key_dispatch_block = _extract_function_block(
        ui_main, "static qboolean UI_OwnerDrawHandleKey(int ownerDraw, int flags, float *special, int key) {"
    )
    skill_key_case = key_dispatch_block.split("case UI_SKILL:", 1)[1].split("case UI_BLUETEAMNAME:", 1)[0]

    assert "#define QLR_UI_ADDR_UI_DRAWSKILL" in ghidra_reference
    assert "0x10005350u" in ghidra_reference
    assert "#define QLR_UI_ADDR_UI_DRAWMAPPREVIEW" in ghidra_reference
    assert "0x100053C0u" in ghidra_reference
    assert "#define QLR_UI_ADDR_UI_DRAWMAPTIMETOBEAT" in ghidra_reference
    assert "0x100054A0u" in ghidra_reference
    assert "#define QLR_UI_ADDR_UI_SKILL_HANDLEKEY" in ghidra_reference
    assert "0x1000A390u" in ghidra_reference
    assert "10005350    int32_t sub_10005350" in hlil
    assert '1000535d  (*(data_106b40a8 + 0x28))("g_spSkill")' in hlil
    assert "1000536f  if (eax s< 1 || eax s> 5)" in hlil
    assert '100053c0    int32_t __convention("regparm") sub_100053c0' in hlil
    assert "100053db  if (esi_1 s< 0 || esi_1 s> data_1075add0)" in hlil
    assert '1000545d      *(esp_1 - 4) = "menu/art/unknownmap"' in hlil
    assert "100054a0    int32_t sub_100054a0" in hlil
    assert "100054af  if (eax_1 s< 0 || eax_1 s> data_1075add0)" in hlil
    assert '10005522  eax_8, ecx_4 = sub_10001900("%02i:%02i")' in hlil
    assert '1000a390    int32_t __convention("regparm") sub_1000a390' in hlil
    assert '1000a3c1  (*(data_106b40a8 + 0x28))("g_spSkill")' in hlil
    assert "1000a3da  if (eax_3 s< 1)" in hlil
    assert "1000a3e8      eax_3 = 1" in hlil

    assert 'trap_Cvar_VariableValue( "g_spSkill" );' in draw_skill_block
    assert "if (i < 1 || i > numSkillLevels) {" in draw_skill_block
    assert "i = 1;" in draw_skill_block
    assert "skillLevels[i-1]" in draw_skill_block
    assert "case UI_SKILL:" in draw_dispatch_block
    assert "UI_DrawSkill(&rect, scale, color, textStyle);" in draw_dispatch_block
    assert "return UI_Skill_HandleKey(flags, special, key);" in skill_key_case
    assert "if (key == K_MOUSE1 || key == K_MOUSE2 || key == K_ENTER || key == K_KP_ENTER) {" in skill_key_block
    assert 'int i = trap_Cvar_VariableValue( "g_spSkill" );' in skill_key_block
    assert "if (key == K_MOUSE2) {" in skill_key_block
    assert "i--;" in skill_key_block
    assert "i++;" in skill_key_block
    assert "i = numSkillLevels;" in skill_key_block
    assert "i = 1;" in skill_key_block
    assert 'trap_Cvar_Set("g_spSkill", va("%i", i));' in skill_key_block

    assert "int map = (net) ? ui_currentNetMap.integer : ui_currentMap.integer;" in draw_preview_block
    assert "if (map < 0 || map > uiInfo.mapCount) {" in draw_preview_block
    assert 'trap_Cvar_Set("ui_currentNetMap", "0");' in draw_preview_block
    assert 'trap_Cvar_Set("ui_currentMap", "0");' in draw_preview_block
    assert "uiInfo.mapList[map].levelShot = trap_R_RegisterShaderNoMip(uiInfo.mapList[map].imageName);" in draw_preview_block
    assert 'trap_R_RegisterShaderNoMip("menu/art/unknownmap")' in draw_preview_block
    assert "case UI_MAPPREVIEW:" in draw_dispatch_block
    assert "UI_DrawMapPreview(&rect, scale, color, qtrue);" in draw_dispatch_block

    assert "if (ui_currentMap.integer < 0 || ui_currentMap.integer > uiInfo.mapCount) {" in draw_time_block
    assert 'trap_Cvar_Set("ui_currentMap", "0");' in draw_time_block
    assert "time = uiInfo.mapList[ui_currentMap.integer].timeToBeat[uiInfo.gameTypes[ui_gameType.integer].gtEnum];" in draw_time_block
    assert "minutes = time / 60;" in draw_time_block
    assert "seconds = time % 60;" in draw_time_block
    assert 'va("%02i:%02i", minutes, seconds)' in draw_time_block
    assert "case UI_MAP_TIMETOBEAT:" in draw_dispatch_block
    assert "UI_DrawMapTimeToBeat(&rect, scale, color, textStyle);" in draw_dispatch_block


def test_ui_retail_map_media_ownerdraws_match_ql() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ghidra_reference = (
        REPO_ROOT / "references/reverse-engineering/ghidra/uix86/ui_ghidra_reference.h"
    ).read_text(encoding="utf-8")
    hlil = UI_HLIL_PART01.read_text(encoding="utf-8")
    draw_map_cinematic = _extract_function_block(
        ui_main, "static void UI_DrawMapCinematic(rectDef_t *rect, float scale, vec4_t color, qboolean net) {"
    )
    draw_net_preview = _extract_function_block(
        ui_main, "static void UI_DrawNetMapPreview(rectDef_t *rect, float scale, vec4_t color) {"
    )
    draw_net_cinematic = _extract_function_block(
        ui_main, "static void UI_DrawNetMapCinematic(rectDef_t *rect, float scale, vec4_t color) {"
    )
    stop_cinematic = _extract_function_block(ui_main, "static void UI_StopCinematic(int handle) {")
    init_block = _extract_function_block(ui_main, "void _UI_Init( qboolean inGameLoad ) {")
    draw_dispatch_block = _extract_function_block(
        ui_main,
        "static void UI_OwnerDraw(float x, float y, float w, float h, float text_x, float text_y, int ownerDraw, int ownerDrawFlags, int align, float special, float scale, vec4_t color, qhandle_t shader, int textStyle) {",
    )
    key_dispatch_block = _extract_function_block(
        ui_main, "static qboolean UI_OwnerDrawHandleKey(int ownerDraw, int flags, float *special, int key) {"
    )
    width_block = _extract_function_block(ui_main, "static int UI_OwnerDrawWidth(int ownerDraw, float scale) {")

    assert "#define QLR_UI_ADDR_UI_DRAWMAPCINEMATIC" in ghidra_reference
    assert "0x10005560u" in ghidra_reference
    assert "#define QLR_UI_ADDR_UI_DRAWNETMAPPREVIEW" in ghidra_reference
    assert "0x100065B0u" in ghidra_reference
    assert "#define QLR_UI_ADDR_UI_DRAWNETMAPCINEMATIC" in ghidra_reference
    assert "0x10006600u" in ghidra_reference
    assert "10005560    int32_t __convention(\"regparm\") sub_10005560" in hlil
    assert "10005581  if (esi_1 s< 0 || esi_1 s> data_1075add0)" in hlil
    assert '100055f1      *(esp_1 - 0x1c) = "%s.roq"' in hlil
    assert "10005680      int32_t eax_12 = sub_100053c0(arg1, arg3)" in hlil
    assert "100065b0    int32_t sub_100065b0" in hlil
    assert "100065b7  if (eax_1 s<= 0)" in hlil
    assert '100065c6      eax_1 = (*(data_106b40a8 + 0x5c))("menu/art/unknownmap")' in hlil
    assert "10006600    int32_t sub_10006600" in hlil
    assert "1000660f  if (eax_10 s< 0 || eax_10 s> data_1075add0)" in hlil
    assert "10006639  if (eax_1 s>= 0)" in hlil
    assert "1000668d  int32_t eax_7 = data_107644b0" in hlil
    assert "100098fd          return sub_100053c0(1, &var_18)" in hlil
    assert "10009931      case 0x17" in hlil
    assert "10009931          return sub_10005560(0, edx, &var_18)" in hlil
    assert "10009999      case 6" in hlil
    assert "10009999          return sub_100065b0(&var_18)" in hlil
    assert "100099a9      case 0x19" in hlil
    assert "100099a9          return sub_10006600(&var_18)" in hlil
    assert "1000f893  if (eax_3 == 0x218)" in hlil
    assert "1000f8c2          *(data_10744ccc * 0x64 + 0x1075adec) = 0xffffffff" in hlil
    assert "1000f893  else if (eax_3 == 0x21a)" in hlil
    assert "1000f8ee          data_107644b4 = 0xffffffff" in hlil

    assert "int map = (net) ? ui_currentNetMap.integer : ui_currentMap.integer;" in draw_map_cinematic
    assert "if (map < 0 || map > uiInfo.mapCount) {" in draw_map_cinematic
    assert 'trap_Cvar_Set("ui_currentNetMap", "0");' in draw_map_cinematic
    assert 'trap_Cvar_Set("ui_currentMap", "0");' in draw_map_cinematic
    assert 'trap_CIN_PlayCinematic(va("%s.roq", uiInfo.mapList[map].mapLoadName), 0, 0, 0, 0, (CIN_loop | CIN_silent) );' in draw_map_cinematic
    assert "trap_CIN_RunCinematic(uiInfo.mapList[map].cinematic);" in draw_map_cinematic
    assert "trap_CIN_SetExtents(uiInfo.mapList[map].cinematic, rect->x, rect->y, rect->w, rect->h);" in draw_map_cinematic
    assert "trap_CIN_DrawCinematic(uiInfo.mapList[map].cinematic);" in draw_map_cinematic
    assert "uiInfo.mapList[map].cinematic = -2;" in draw_map_cinematic
    assert "UI_DrawMapPreview(rect, scale, color, net);" in draw_map_cinematic
    assert "case UI_MAPCINEMATIC:" in draw_dispatch_block
    assert "UI_DrawMapCinematic(&rect, scale, color, qfalse);" in draw_dispatch_block

    assert "if (uiInfo.serverStatus.currentServerPreview > 0) {" in draw_net_preview
    assert "UI_DrawHandlePic( rect->x, rect->y, rect->w, rect->h, uiInfo.serverStatus.currentServerPreview);" in draw_net_preview
    assert 'trap_R_RegisterShaderNoMip("menu/art/unknownmap")' in draw_net_preview
    assert "case UI_NETMAPPREVIEW:" in draw_dispatch_block
    assert "UI_DrawNetMapPreview(&rect, scale, color);" in draw_dispatch_block

    assert "if (ui_currentNetMap.integer < 0 || ui_currentNetMap.integer > uiInfo.mapCount) {" in draw_net_cinematic
    assert 'trap_Cvar_Set("ui_currentNetMap", "0");' in draw_net_cinematic
    assert "if (uiInfo.serverStatus.currentServerCinematic >= 0) {" in draw_net_cinematic
    assert "trap_CIN_RunCinematic(uiInfo.serverStatus.currentServerCinematic);" in draw_net_cinematic
    assert "trap_CIN_SetExtents(uiInfo.serverStatus.currentServerCinematic, rect->x, rect->y, rect->w, rect->h);" in draw_net_cinematic
    assert "trap_CIN_DrawCinematic(uiInfo.serverStatus.currentServerCinematic);" in draw_net_cinematic
    assert "UI_DrawNetMapPreview(rect, scale, color);" in draw_net_cinematic
    assert "case UI_NETMAPCINEMATIC:" in draw_dispatch_block
    assert "UI_DrawNetMapCinematic(&rect, scale, color);" in draw_dispatch_block

    assert "uiInfo.uiDC.stopCinematic = &UI_StopCinematic;" in init_block
    assert "if (handle >= 0) {" in stop_cinematic
    assert "trap_CIN_StopCinematic(handle);" in stop_cinematic
    assert "handle = abs(handle);" in stop_cinematic
    assert "if (handle == UI_MAPCINEMATIC) {" in stop_cinematic
    assert "trap_CIN_StopCinematic(uiInfo.mapList[ui_currentMap.integer].cinematic);" in stop_cinematic
    assert "uiInfo.mapList[ui_currentMap.integer].cinematic = -1;" in stop_cinematic
    assert "} else if (handle == UI_NETMAPCINEMATIC) {" in stop_cinematic
    assert "trap_CIN_StopCinematic(uiInfo.serverStatus.currentServerCinematic);" in stop_cinematic
    assert "uiInfo.serverStatus.currentServerCinematic = -1;" in stop_cinematic
    assert "case UI_MAPCINEMATIC:" not in key_dispatch_block
    assert "case UI_NETMAPPREVIEW:" not in key_dispatch_block
    assert "case UI_NETMAPCINEMATIC:" not in key_dispatch_block
    assert "case UI_MAPCINEMATIC:" not in width_block
    assert "case UI_NETMAPPREVIEW:" not in width_block
    assert "case UI_NETMAPCINEMATIC:" not in width_block


def test_ui_retail_map_selection_ownerdraws_match_ql() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ghidra_reference = (
        REPO_ROOT / "references/reverse-engineering/ghidra/uix86/ui_ghidra_reference.h"
    ).read_text(encoding="utf-8")
    hlil = UI_HLIL_PART01.read_text(encoding="utf-8")
    draw_selection = _extract_function_block(
        ui_main,
        "static void UI_DrawAllMapsSelection(rectDef_t *rect, float scale, vec4_t color, int textStyle, qboolean net) {",
    )
    draw_map_cinematic = _extract_function_block(
        ui_main, "static void UI_DrawMapCinematic(rectDef_t *rect, float scale, vec4_t color, qboolean net) {"
    )
    draw_dispatch_block = _extract_function_block(
        ui_main,
        "static void UI_OwnerDraw(float x, float y, float w, float h, float text_x, float text_y, int ownerDraw, int ownerDrawFlags, int align, float special, float scale, vec4_t color, qhandle_t shader, int textStyle) {",
    )
    key_dispatch_block = _extract_function_block(
        ui_main, "static qboolean UI_OwnerDrawHandleKey(int ownerDraw, int flags, float *special, int key) {"
    )
    width_block = _extract_function_block(ui_main, "static int UI_OwnerDrawWidth(int ownerDraw, float scale) {")

    assert "#define QLR_UI_ADDR_UI_DRAWALLMAPSSELECTION" in ghidra_reference
    assert "0x10006890u" in ghidra_reference
    assert "#define QLR_UI_ADDR_UI_DRAWMAPCINEMATIC" in ghidra_reference
    assert "0x10005560u" in ghidra_reference
    assert '10005560    int32_t __convention("regparm") sub_10005560' in hlil
    assert "1000556f  if (arg1 == 0)" in hlil
    assert "10005581  if (esi_1 s< 0 || esi_1 s> data_1075add0)" in hlil
    assert '100055f1      *(esp_1 - 0x1c) = "%s.roq"' in hlil
    assert "10005680      int32_t eax_12 = sub_100053c0(arg1, arg3)" in hlil
    assert "10006890    int32_t __convention(\"regparm\") sub_10006890" in hlil
    assert "10006895  int32_t result = data_10742f8c" in hlil
    assert "1000689a  if (arg6 == 0)" in hlil
    assert "1000689c      result = data_10744ccc" in hlil
    assert "100068ab  if (result s< 0 || result s>= data_1075add0)" in hlil
    assert "100068de      fconvert.s(fconvert.t(arg4)), arg5, *(result * 0x64 + 0x1075add4)," in hlil
    assert "100099e7      case 0xf" in hlil
    assert "100099fd          return sub_10006890(arg12, arg14, &var_18, fconvert.s(fconvert.t(arg11)), arg12," in hlil
    assert "100099fd              1)" in hlil
    assert "10009946      case 0x22" in hlil
    assert "10009946          return sub_10005560(1, edx, &var_18)" in hlil
    assert "100099fe      case 0x23" in hlil
    assert "10009a11          if (eax_1 s>= 0 && eax_1 s< data_1075add0)" in hlil
    assert "10009a5a                  fconvert.s(float.t(0)), 0)" in hlil

    assert "int map = (net) ? ui_currentNetMap.integer : ui_currentMap.integer;" in draw_selection
    assert "if (map >= 0 && map < uiInfo.mapCount) {" in draw_selection
    assert "Text_Paint(rect->x, rect->y, scale, color, uiInfo.mapList[map].mapName, 0, 0, textStyle);" in draw_selection
    assert "case UI_ALLMAPS_SELECTION:" in draw_dispatch_block
    assert "UI_DrawAllMapsSelection(&rect, scale, color, textStyle, qtrue);" in draw_dispatch_block
    assert "case UI_MAPS_SELECTION:" in draw_dispatch_block
    assert "UI_DrawAllMapsSelection(&rect, scale, color, textStyle, qfalse);" in draw_dispatch_block

    assert "int map = (net) ? ui_currentNetMap.integer : ui_currentMap.integer;" in draw_map_cinematic
    assert "if (map < 0 || map > uiInfo.mapCount) {" in draw_map_cinematic
    assert 'trap_Cvar_Set("ui_currentNetMap", "0");' in draw_map_cinematic
    assert 'trap_Cvar_Set("ui_currentMap", "0");' in draw_map_cinematic
    assert 'trap_CIN_PlayCinematic(va("%s.roq", uiInfo.mapList[map].mapLoadName), 0, 0, 0, 0, (CIN_loop | CIN_silent) );' in draw_map_cinematic
    assert "trap_CIN_RunCinematic(uiInfo.mapList[map].cinematic);" in draw_map_cinematic
    assert "UI_DrawMapPreview(rect, scale, color, net);" in draw_map_cinematic
    assert "case UI_STARTMAPCINEMATIC:" in draw_dispatch_block
    assert "UI_DrawMapCinematic(&rect, scale, color, qtrue);" in draw_dispatch_block

    allmaps_width_case = width_block.split("case UI_ALLMAPS_SELECTION:", 1)[1].split("case UI_OPPONENT_NAME:", 1)[0]
    assert "break;" in allmaps_width_case
    assert "s =" not in allmaps_width_case
    assert "case UI_MAPS_SELECTION:" not in width_block
    assert "case UI_STARTMAPCINEMATIC:" not in width_block
    assert "case UI_ALLMAPS_SELECTION:" not in key_dispatch_block
    assert "case UI_MAPS_SELECTION:" not in key_dispatch_block
    assert "case UI_STARTMAPCINEMATIC:" not in key_dispatch_block


def test_ui_retail_server_info_ownerdraws_match_ql() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ghidra_reference = (
        REPO_ROOT / "references/reverse-engineering/ghidra/uix86/ui_ghidra_reference.h"
    ).read_text(encoding="utf-8")
    hlil = UI_HLIL_PART01.read_text(encoding="utf-8")
    draw_refresh = _extract_function_block(
        ui_main, "static void UI_DrawServerRefreshDate(rectDef_t *rect, float scale, vec4_t color, int textStyle) {"
    )
    draw_motd = _extract_function_block(
        ui_main, "static void UI_DrawServerMOTD(rectDef_t *rect, float scale, vec4_t color) {"
    )
    draw_glinfo = _extract_function_block(
        ui_main, "static void UI_DrawGLInfo(rectDef_t *rect, float scale, vec4_t color, int textStyle) {"
    )
    build_server_display = _extract_function_block(
        ui_main, "static void UI_BuildServerDisplayList(qboolean force) {"
    )
    draw_dispatch_block = _extract_function_block(
        ui_main,
        "static void UI_OwnerDraw(float x, float y, float w, float h, float text_x, float text_y, int ownerDraw, int ownerDrawFlags, int align, float special, float scale, vec4_t color, qhandle_t shader, int textStyle) {",
    )
    key_dispatch_block = _extract_function_block(
        ui_main, "static qboolean UI_OwnerDrawHandleKey(int ownerDraw, int flags, float *special, int key) {"
    )
    width_block = _extract_function_block(ui_main, "static int UI_OwnerDrawWidth(int ownerDraw, float scale) {")

    assert "#define QLR_UI_ADDR_UI_DRAWSERVERREFRESHDATE" in ghidra_reference
    assert "0x10008F20u" in ghidra_reference
    assert "#define QLR_UI_ADDR_UI_DRAWSERVERMOTD" in ghidra_reference
    assert "0x10009080u" in ghidra_reference
    assert "#define QLR_UI_ADDR_UI_DRAWGLINFO" in ghidra_reference
    assert "0x100093B0u" in ghidra_reference
    assert "10008f20    int32_t sub_10008f20" in hlil
    assert '10009037      eax_12, ecx_5 = sub_10001900("Refresh Time: %s")' in hlil
    assert '10008fdc      var_80_1 = sub_10001900("Getting info for %d servers (ESC…")' in hlil
    assert "10009080    void sub_10009080" in hlil
    assert "10009221          edx = sub_10004280(&var_c, edx, 0f, float.s(data_107644c0)," in hlil
    assert "10009285          sub_10004280(&var_4, edx, esi_1, float.s(ecx_1)," in hlil
    assert "100093b0    int32_t sub_100093b0" in hlil
    assert '100093e0  eax_2, ecx_1 = sub_10001900("VENDOR: %s")' in hlil
    assert '10009434  eax_3, ecx_3 = sub_10001900("VERSION: %s: %s")' in hlil
    assert '100094a0  eax_5, ecx_6 = sub_10001900("PIXELFORMAT: color(%d-bits) Z(%d…")' in hlil
    assert '10026c88  char const data_10026c88[0x39] = "Press ENTER or CLICK to change, Press BACKSPACE to clear", 0' in hlil
    assert '100270ec  char const data_100270ec[0x2c] = "Getting info for %d servers (ESC to cancel)", 0' in hlil
    assert '10027118  char const data_10027118[0x11] = "Refresh Time: %s", 0' in hlil
    assert '1002712c  char const data_1002712c[0xb] = "VENDOR: %s", 0' in hlil
    assert '10027138  char const data_10027138[0x10] = "VERSION: %s: %s", 0' in hlil
    assert '10027148  char const data_10027148[0x38] = "PIXELFORMAT: color(%d-bits) Z(%d-bits) stencil(%d-bits)", 0' in hlil
    assert '10027be0  char const data_10027be0[0x17] = "Welcome to Team Arena!", 0' in hlil
    assert "10009b35      case 0x1a" in hlil
    assert "10009b4b          return sub_10008f20(arg12, &var_18, fconvert.s(fconvert.t(arg11)))" in hlil
    assert "10009b53      case 0x1b" in hlil
    assert "10009b5b          int80_t st0" in hlil
    assert "10009b74      case 0x1c" in hlil
    assert "10009b8a          return sub_100093b0(&var_18, fconvert.s(fconvert.t(arg11)), arg14)" in hlil
    assert "10006abb          case 0x21b" in hlil
    assert '10006ada                  &data_10042f38, 0x400)' in hlil

    assert "if (uiInfo.serverStatus.refreshActive) {" in draw_refresh
    assert "lowLight[0] = 0.8 * color[0];" in draw_refresh
    assert "lowLight[3] = 0.8 * color[3];" in draw_refresh
    assert "LerpColor(color,lowLight,newColor,0.5+0.5*sin(uiInfo.uiDC.realTime / PULSE_DIVISOR));" in draw_refresh
    assert 'va("Getting info for %d servers (ESC to cancel)", trap_LAN_GetServerCount(ui_netSource.integer))' in draw_refresh
    assert "char buff[64];" in draw_refresh
    assert 'Q_strncpyz(buff, UI_Cvar_VariableString(va("ui_lastServerRefresh_%i", ui_netSource.integer)), 64);' in draw_refresh
    assert 'va("Refresh Time: %s", buff)' in draw_refresh
    assert "case UI_SERVERREFRESHDATE:" in draw_dispatch_block
    assert "UI_DrawServerRefreshDate(&rect, scale, color, textStyle);" in draw_dispatch_block
    assert "case UI_SERVERREFRESHDATE:" in width_block
    assert 's = UI_Cvar_VariableString(va("ui_lastServerRefresh_%i", ui_netSource.integer));' in width_block

    assert 'trap_Cvar_VariableStringBuffer( "cl_motdString", uiInfo.serverStatus.motd, sizeof(uiInfo.serverStatus.motd) );' in build_server_display
    assert "len = strlen(uiInfo.serverStatus.motd);" in build_server_display
    assert "if (len == 0) {" in build_server_display
    assert 'strcpy(uiInfo.serverStatus.motd, "Welcome to Team Arena!");' in build_server_display
    assert "uiInfo.serverStatus.motdWidth = -1;" in build_server_display
    assert "if (uiInfo.serverStatus.motdLen) {" in draw_motd
    assert "uiInfo.serverStatus.motdPaintX = rect->x + 1;" in draw_motd
    assert "uiInfo.serverStatus.motdPaintX2 = -1;" in draw_motd
    assert "uiInfo.serverStatus.motdTime = uiInfo.uiDC.realTime + 10;" in draw_motd
    assert "uiInfo.serverStatus.motdPaintX -= 2;" in draw_motd
    assert "maxX = rect->x + rect->w - 2;" in draw_motd
    assert "Text_Paint_Limit(&maxX, uiInfo.serverStatus.motdPaintX, rect->y + rect->h - 3, scale, color, &uiInfo.serverStatus.motd[uiInfo.serverStatus.motdOffset], 0, 0);" in draw_motd
    assert "Text_Paint_Limit(&maxX2, uiInfo.serverStatus.motdPaintX2, rect->y + rect->h - 3, scale, color, uiInfo.serverStatus.motd, 0, uiInfo.serverStatus.motdOffset);" in draw_motd
    assert "case UI_SERVERMOTD:" in draw_dispatch_block
    assert "UI_DrawServerMOTD(&rect, scale, color);" in draw_dispatch_block

    assert 'va("VENDOR: %s", uiInfo.uiDC.glconfig.vendor_string)' in draw_glinfo
    assert 'va("VERSION: %s: %s", uiInfo.uiDC.glconfig.version_string,uiInfo.uiDC.glconfig.renderer_string)' in draw_glinfo
    assert 'va ("PIXELFORMAT: color(%d-bits) Z(%d-bits) stencil(%d-bits)", uiInfo.uiDC.glconfig.colorBits, uiInfo.uiDC.glconfig.depthBits, uiInfo.uiDC.glconfig.stencilBits)' in draw_glinfo
    assert "Q_strncpyz(buff, uiInfo.uiDC.glconfig.extensions_string, 1024);" in draw_glinfo
    assert "y = rect->y + 45;" in draw_glinfo
    assert "while ( y < rect->y + rect->h && *eptr )" in draw_glinfo
    assert "lines[numLines++] = eptr;" in draw_glinfo
    assert "Text_Paint(rect->x + 2, y, scale, color, lines[i++], 0, 20, textStyle);" in draw_glinfo
    assert "Text_Paint(rect->x + rect->w / 2, y, scale, color, lines[i++], 0, 20, textStyle);" in draw_glinfo
    assert "if (y > rect->y + rect->h - 11) {" in draw_glinfo
    assert "case UI_GLINFO:" in draw_dispatch_block
    assert "UI_DrawGLInfo(&rect,scale, color, textStyle);" in draw_dispatch_block

    assert "case UI_SERVERREFRESHDATE:" not in key_dispatch_block
    assert "case UI_SERVERMOTD:" not in key_dispatch_block
    assert "case UI_GLINFO:" not in key_dispatch_block
    assert "case UI_SERVERMOTD:" not in width_block
    assert "case UI_GLINFO:" not in width_block


def test_ui_retail_botname_botskill_redblue_ownerdraws_match_ql() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    botname_draw = _extract_function_block(
        ui_main, "static void UI_DrawBotName(rectDef_t *rect, float scale, vec4_t color, int textStyle) {"
    )
    botskill_draw = _extract_function_block(
        ui_main, "static void UI_DrawBotSkill(rectDef_t *rect, float scale, vec4_t color, int textStyle) {"
    )
    redblue_draw = _extract_function_block(
        ui_main, "static void UI_DrawRedBlue(rectDef_t *rect, float scale, vec4_t color, int textStyle) {"
    )
    botname_key = _extract_function_block(
        ui_main, "static qboolean UI_BotName_HandleKey(int flags, float *special, int key) {"
    )
    botskill_key = _extract_function_block(
        ui_main, "static qboolean UI_BotSkill_HandleKey(int flags, float *special, int key) {"
    )
    redblue_key = _extract_function_block(
        ui_main, "static qboolean UI_RedBlue_HandleKey(int flags, float *special, int key) {"
    )
    draw_dispatch_block = _extract_function_block(
        ui_main,
        "static void UI_OwnerDraw(float x, float y, float w, float h, float text_x, float text_y, int ownerDraw, int ownerDrawFlags, int align, float special, float scale, vec4_t color, qhandle_t shader, int textStyle) {",
    )
    key_dispatch_block = _extract_function_block(
        ui_main, "static qboolean UI_OwnerDrawHandleKey(int ownerDraw, int flags, float *special, int key) {"
    )
    botname_key_case = key_dispatch_block.split("case UI_BOTNAME:", 1)[1].split("case UI_BOTSKILL:", 1)[0]
    botskill_key_case = key_dispatch_block.split("case UI_BOTSKILL:", 1)[1].split("case UI_REDBLUE:", 1)[0]
    redblue_key_case = key_dispatch_block.split("case UI_REDBLUE:", 1)[1].split("case UI_CROSSHAIR:", 1)[0]

    assert "botCount = UI_GetNumBots();" in botname_draw
    assert 'const char *text = "Sarge";' in botname_draw
    assert "if (value >= botCount) {" in botname_draw
    assert "if (value < 0 || value >= botCount) {" in botname_draw
    assert 'trap_Print(va(S_COLOR_RED "Invalid bot number: %i\\n", value));' in botname_draw
    assert "text = UI_GetBotNameByNumber(value);" in botname_draw
    assert "case UI_BOTNAME:" in draw_dispatch_block
    assert "UI_DrawBotName(&rect, scale, color, textStyle);" in draw_dispatch_block
    assert "return UI_BotName_HandleKey(flags, special, key);" in botname_key_case
    assert "value = UI_GetNumBots() + 2 - 1;" in botname_key
    assert "uiInfo.botIndex = value;" in botname_key
    assert 'trap_Cvar_VariableValue("g_gametype")' not in botname_draw
    assert 'trap_Cvar_VariableValue("g_gametype")' not in botname_key
    assert "uiInfo.characterList[value].name" not in botname_draw
    assert "uiInfo.characterCount + 2" not in botname_key

    assert "if (uiInfo.skillIndex >= 0 && uiInfo.skillIndex < numSkillLevels) {" in botskill_draw
    assert "skillLevels[uiInfo.skillIndex]" in botskill_draw
    assert "case UI_BOTSKILL:" in draw_dispatch_block
    assert "UI_DrawBotSkill(&rect, scale, color, textStyle);" in draw_dispatch_block
    assert "return UI_BotSkill_HandleKey(flags, special, key);" in botskill_key_case
    assert "uiInfo.skillIndex++;" in botskill_key
    assert "uiInfo.skillIndex--;" in botskill_key
    assert "if (uiInfo.skillIndex >= numSkillLevels) {" in botskill_key
    assert "uiInfo.skillIndex = numSkillLevels-1;" in botskill_key

    assert '(uiInfo.redBlue == 0) ? "Red" : "Blue"' in redblue_draw
    assert "case UI_REDBLUE:" in draw_dispatch_block
    assert "UI_DrawRedBlue(&rect, scale, color, textStyle);" in draw_dispatch_block
    assert "UI_RedBlue_HandleKey(flags, special, key);" in redblue_key_case
    assert "return UI_RedBlue_HandleKey" not in redblue_key_case
    assert "uiInfo.redBlue ^= 1;" in redblue_key
    assert "return qtrue;" in redblue_key


def test_ui_retail_handicap_netsource_netfilter_ownerdraws_match_ql() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    handicap_draw = _extract_function_block(ui_main, "static void UI_DrawHandicap")
    netsource_draw = _extract_function_block(ui_main, "static void UI_DrawNetSource")
    netfilter_draw = _extract_function_block(ui_main, "static void UI_DrawNetFilter")
    width_block = _extract_function_block(ui_main, "static int UI_OwnerDrawWidth")
    handicap_key = _extract_function_block(ui_main, "static qboolean UI_Handicap_HandleKey")
    netsource_key = _extract_function_block(ui_main, "static qboolean UI_NetSource_HandleKey")
    netfilter_key = _extract_function_block(ui_main, "static qboolean UI_NetFilter_HandleKey")
    draw_dispatch_block = _extract_function_block(
        ui_main,
        "static void UI_OwnerDraw(float x, float y, float w, float h, float text_x, float text_y, int ownerDraw, int ownerDrawFlags, int align, float special, float scale, vec4_t color, qhandle_t shader, int textStyle) {",
    )
    key_dispatch_block = _extract_function_block(
        ui_main, "static qboolean UI_OwnerDrawHandleKey(int ownerDraw, int flags, float *special, int key) {"
    )
    netsource_key_case = key_dispatch_block.split("case UI_NETSOURCE:", 1)[1].split("case UI_NETFILTER:", 1)[0]
    netfilter_key_case = key_dispatch_block.split("case UI_NETFILTER:", 1)[1].split("case UI_BOTNAME:", 1)[0]

    assert 'static const char *handicapValues[] = {"None","95","90","85","80","75","70","65","60","55","50","45","40","35","30","25","20","15","10","5",NULL};' in ui_main
    assert 'h = Com_Clamp( 5, 100, trap_Cvar_VariableValue("handicap") );' in handicap_draw
    assert "i = 20 - h / 5;" in handicap_draw
    assert "Text_Paint(rect->x, rect->y, scale, color, handicapValues[i], 0, 0, textStyle);" in handicap_draw
    assert "case UI_HANDICAP:" in draw_dispatch_block
    assert "UI_DrawHandicap(&rect, scale, color, textStyle);" in draw_dispatch_block
    assert "return UI_Handicap_HandleKey(flags, special, key);" in key_dispatch_block
    assert 'h = Com_Clamp( 5, 100, trap_Cvar_VariableValue("handicap") );' in handicap_key
    assert "h -= 5;" in handicap_key
    assert "h += 5;" in handicap_key
    assert "if (h > 100) {" in handicap_key
    assert "h = 5;" in handicap_key
    assert "} else if (h < 0) {" in handicap_key
    assert "h = 100;" in handicap_key
    assert 'trap_Cvar_Set( "handicap", va( "%i", h) );' in handicap_key

    assert '"Local",\n\t"Mplayer",\n\t"Internet",\n\t"Favorites"' in ui_main
    assert "static const int numNetSources = sizeof(netSources) / sizeof(const char*);" in ui_main
    assert "if (ui_netSource.integer < 0 || ui_netSource.integer >= numNetSources) {" in netsource_draw
    assert 'Text_Paint(rect->x, rect->y, scale, color, va("Source: %s", netSources[ui_netSource.integer]), 0, 0, textStyle);' in netsource_draw
    assert "if (ui_netSource.integer < 0 || ui_netSource.integer >= numNetSources) {" in width_block
    assert 's = va("Source: %s", netSources[ui_netSource.integer]);' in width_block
    assert "case UI_NETSOURCE:" in draw_dispatch_block
    assert "UI_DrawNetSource(&rect, scale, color, textStyle);" in draw_dispatch_block
    assert "UI_NetSource_HandleKey(flags, special, key);" in netsource_key_case
    assert "return UI_NetSource_HandleKey" not in netsource_key_case
    assert "if (ui_netSource.integer == AS_MPLAYER)" in netsource_key
    assert "if (ui_netSource.integer >= numNetSources) {" in netsource_key
    assert "ui_netSource.integer = numNetSources - 1;" in netsource_key
    assert "UI_BuildServerDisplayList(qtrue);" in netsource_key
    assert "if (ui_netSource.integer != AS_GLOBAL) {" in netsource_key
    assert "UI_StartServerRefresh(qtrue);" in netsource_key
    assert 'trap_Cvar_Set( "ui_netSource", va("%d", ui_netSource.integer));' in netsource_key

    assert '{"OSP", "osp" },' in ui_main
    assert "static const int numServerFilters = sizeof(serverFilters) / sizeof(serverFilter_t);" in ui_main
    assert "if (ui_serverFilterType.integer < 0 || ui_serverFilterType.integer >= numServerFilters) {" in netfilter_draw
    assert 'Text_Paint(rect->x, rect->y, scale, color, va("Filter: %s", serverFilters[ui_serverFilterType.integer].description), 0, 0, textStyle);' in netfilter_draw
    assert "if (ui_serverFilterType.integer < 0 || ui_serverFilterType.integer >= numServerFilters) {" in width_block
    assert 's = va("Filter: %s", serverFilters[ui_serverFilterType.integer].description );' in width_block
    assert "case UI_NETFILTER:" in draw_dispatch_block
    assert "UI_DrawNetFilter(&rect, scale, color, textStyle);" in draw_dispatch_block
    assert "UI_NetFilter_HandleKey(flags, special, key);" in netfilter_key_case
    assert "return UI_NetFilter_HandleKey" not in netfilter_key_case
    assert "if (ui_serverFilterType.integer >= numServerFilters) {" in netfilter_key
    assert "ui_serverFilterType.integer = numServerFilters - 1;" in netfilter_key
    assert "UI_BuildServerDisplayList(qtrue);" in netfilter_key
    assert 'trap_Cvar_Set( "ui_serverFilterType"' not in netfilter_key


def test_ui_retail_player_opponent_ownerdraws_match_ql() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ghidra_reference = (
        REPO_ROOT / "references/reverse-engineering/ghidra/uix86/ui_ghidra_reference.h"
    ).read_text(encoding="utf-8")
    hlil = UI_HLIL_PART01.read_text(encoding="utf-8")
    key_hlil_block = hlil.split("1000a820    int32_t __convention(\"regparm\") sub_1000a820", 1)[
        1
    ].split("1000a917", 1)[0]
    player_draw = _extract_function_block(ui_main, "static void UI_DrawPlayerModel(rectDef_t *rect) {")
    opponent_draw = _extract_function_block(ui_main, "static void UI_DrawOpponent(rectDef_t *rect) {")
    opponent_name_draw = _extract_function_block(
        ui_main, "static void UI_DrawOpponentName(rectDef_t *rect, float scale, vec4_t color, int textStyle) {"
    )
    draw_dispatch_block = _extract_function_block(
        ui_main,
        "static void UI_OwnerDraw(float x, float y, float w, float h, float text_x, float text_y, int ownerDraw, int ownerDrawFlags, int align, float special, float scale, vec4_t color, qhandle_t shader, int textStyle) {",
    )
    key_dispatch_block = _extract_function_block(
        ui_main, "static qboolean UI_OwnerDrawHandleKey(int ownerDraw, int flags, float *special, int key) {"
    )
    width_block = _extract_function_block(ui_main, "static int UI_OwnerDrawWidth(int ownerDraw, float scale) {")
    opponent_name_width_case = width_block.split("case UI_OPPONENT_NAME:", 1)[1].split(
        "case UI_KEYBINDSTATUS:", 1
    )[0]

    assert "#define QLR_UI_ADDR_UI_DRAWPLAYERMODEL" in ghidra_reference
    assert "0x10005690u" in ghidra_reference
    assert "#define QLR_UI_ADDR_UI_DRAWOPPONENT" in ghidra_reference
    assert "0x10006730u" in ghidra_reference
    assert "#define QLR_UI_ADDR_UI_DRAWOPPONENTNAME" in ghidra_reference
    assert "0x100068F0u" in ghidra_reference
    assert "10005690    int32_t sub_10005690" in hlil
    assert '100056c6  (*(data_106b40a8 + 0x24))("model", &data_10042f38, 0x400)' in hlil
    assert '100056ff  (*(data_106b40a8 + 0x24))("headmodel", &data_10042f38, 0x400)' in hlil
    assert '10005733  (*(eax_4 + 0x28))("cg_loadout")' in hlil
    assert '10005754      (*(data_106b40a8 + 0x28))("cg_weaponPrimary")' in hlil
    assert "10005776      esi = 0xe" in hlil
    assert "100057a5      int32_t var_250_1 = 0x43520000" in hlil
    assert "100057b8      float var_254 = 5f" in hlil
    assert "1000580d  data_1004f9c8 = 0" in hlil
    assert "10005824  int32_t result = sub_10012d90()" in hlil
    assert "10006730    int32_t sub_10006730" in hlil
    assert '1000676b      (*(data_106b40a8 + 0x24))("ui_opponentModel", &data_10042f38, 0x400)' in hlil
    assert '10006799      (*(data_106b40a8 + 0x24))("ui_opponentModel", &data_10042f38, 0x400)' in hlil
    assert "100067d5      int32_t var_194_1 = 0x432a0000" in hlil
    assert "1000680c      int32_t eax_6" in hlil
    assert "10006850  data_100468a8 = 0" in hlil
    assert "10006866      fconvert.s(fconvert.t(*arg1)), fconvert.s(x87_r7_2))" in hlil
    assert "100068f0    int32_t sub_100068f0" in hlil
    assert '10006907  int32_t ecx_1 = (*(data_106b40a8 + 0x24))("ui_opponentName", &data_10042f38, 0x400)' in hlil
    assert "10009824          float* var_2c_2 = &var_18" in hlil
    assert "10009833          return sub_10005690(x87_r0)" in hlil
    assert "100099da      case 9" in hlil
    assert "100099da          return sub_10006730(&var_18)" in hlil
    assert "10009a66      case 0x10" in hlil
    assert "10009a7c          return sub_100068f0(&var_18, fconvert.s(fconvert.t(arg11)), arg12, arg14)" in hlil
    assert "case 0x211" not in key_hlil_block
    assert "case 0x213" in key_hlil_block

    assert 'trap_Cvar_VariableStringBuffer("model", model, sizeof(model));' in player_draw
    assert 'trap_Cvar_VariableStringBuffer("headmodel", head, sizeof(head));' in player_draw
    assert "team[0] = '\\0';" in player_draw
    assert "weapon = WP_MACHINEGUN;" in player_draw
    assert 'if (trap_Cvar_VariableValue("cg_loadout") != 0.0f) {' in player_draw
    assert 'weapon = (weapon_t)(int)trap_Cvar_VariableValue("cg_weaponPrimary");' in player_draw
    assert "item = BG_FindItemForWeapon(weapon);" in player_draw
    assert "if (!item || item->giType != IT_WEAPON) {" in player_draw
    assert "weapon = WP_HEAVY_MACHINEGUN;" in player_draw
    assert "viewangles[PITCH] = 5;" in player_draw
    assert "viewangles[YAW]   = 210;" in player_draw
    assert "UI_PlayerInfo_SetModel( &info, model, head, team);" in player_draw
    assert "UI_PlayerInfo_SetInfo( &info, LEGS_IDLE, TORSO_STAND, viewangles, moveangles, weapon, qfalse );" in player_draw
    assert "info.headColor[0] = 0.0f;" in player_draw
    assert "UI_DrawPlayer( rect->x, rect->y, rect->w, rect->h, &info, uiInfo.uiDC.realTime / 2);" in player_draw
    assert '"ui_Q3Model"' not in player_draw
    assert '"team_model"' not in player_draw
    assert '"team_headmodel"' not in player_draw
    assert "q3Model" not in ui_main
    assert "case UI_PLAYERMODEL:" in draw_dispatch_block
    assert "UI_DrawPlayerModel(&rect);" in draw_dispatch_block

    assert 'trap_Cvar_VariableStringBuffer("ui_opponentModel", model, sizeof(model));' in opponent_draw
    assert 'trap_Cvar_VariableStringBuffer("ui_opponentModel", headmodel, sizeof(headmodel));' in opponent_draw
    assert "team[0] = '\\0';" in opponent_draw
    assert "viewangles[YAW]   = 180 - 10;" in opponent_draw
    assert 'UI_PlayerInfo_SetModel( &info2, model, headmodel, "");' in opponent_draw
    assert "UI_PlayerInfo_SetInfo( &info2, LEGS_IDLE, TORSO_STAND, viewangles, moveangles, WP_MACHINEGUN, qfalse );" in opponent_draw
    assert "UI_RegisterClientModelname( &info2, model, headmodel, team);" in opponent_draw
    assert "updateOpponentModel = qfalse;" in opponent_draw
    assert "info2.headColor[0] = 0.0f;" in opponent_draw
    assert "UI_DrawPlayer( rect->x, rect->y, rect->w, rect->h, &info2, uiInfo.uiDC.realTime / 2);" in opponent_draw
    assert "case UI_OPPONENTMODEL:" in draw_dispatch_block
    assert "UI_DrawOpponent(&rect);" in draw_dispatch_block

    assert "char opponentName[MAX_INFO_STRING];" in opponent_name_draw
    assert 'trap_Cvar_VariableStringBuffer("ui_opponentName", opponentName, sizeof(opponentName));' in opponent_name_draw
    assert "Text_Paint(rect->x, rect->y, scale, color, opponentName, 0, 0, textStyle);" in opponent_name_draw
    assert 'UI_Cvar_VariableString("ui_opponentName")' not in opponent_name_draw
    assert "case UI_OPPONENT_NAME:" in draw_dispatch_block
    assert "UI_DrawOpponentName(&rect, scale, color, textStyle);" in draw_dispatch_block
    assert "case UI_OPPONENT_NAME:" in width_block
    assert "break;" in opponent_name_width_case
    assert "s =" not in opponent_name_width_case
    assert "case UI_PLAYERMODEL:" not in width_block
    assert "case UI_OPPONENTMODEL:" not in width_block
    assert "case UI_PLAYERMODEL:" not in key_dispatch_block
    assert "case UI_OPPONENTMODEL:" not in key_dispatch_block
    assert "case UI_OPPONENT_NAME:" not in key_dispatch_block
    assert "UI_OpponentName_HandleKey" not in ui_main
    assert "UI_NextOpponent" not in ui_main
    assert "UI_PriorOpponent" not in ui_main


def test_ui_retail_starting_weapons_ownerdraw_restored() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    token_block = _extract_function_block(ui_main, "static int UI_StartingWeaponIndexFromToken")
    starting_block = _extract_function_block(ui_main, "static void UI_DrawStartingWeapons")
    assert "#define UI_STARTING_WEAPON_ICON_COUNT\t14" in ui_main
    assert "static int UI_StartingWeaponIndexFromToken( const char *value )" in ui_main
    assert "COM_ParseExt( &cursor, qtrue )" in token_block
    assert "uiStartingWeaponIcons[i].token" in token_block
    assert '{ "hmg", "icons/weap_hmg.tga" }' in ui_main
    assert 'trap_GetConfigString( CS_LOADOUT_MASK, loadoutMaskText, sizeof( loadoutMaskText ) );' in ui_main
    assert "loadoutMask = (unsigned int)atoi( loadoutMaskText );" in starting_block
    assert "xOffset += rect->w * 1.5f;" in starting_block
    assert 'if ( trap_Cvar_VariableValue( "cg_loadout" ) != 1.0f ) {' in ui_main
    assert "plusX = rect->x + xOffset;" in starting_block
    assert 'plusY = rect->y + rect->h * 0.5f + Text_Height( "+", scale, 0 ) * 0.5f;' in starting_block
    assert 'Text_Paint( plusX, plusY, scale, color, "+", 0, 0, textStyle );' in starting_block
    assert 'UI_Cvar_VariableString( "cg_weaponPrimaryQueued" )' in ui_main
    assert "UI_DrawHandlePic( rect->x + xOffset + rect->w, rect->y, rect->w, rect->h, shader );" in starting_block
    assert "case UI_STARTING_WEAPONS:" in ui_main
    assert "UI_DrawStartingWeapons(&rect, scale, color, textStyle);" in ui_main
    assert "strtoul( loadoutMaskText" not in starting_block
    assert "plusWidth" not in starting_block
    assert "( rect->w - plusWidth )" not in starting_block
    for stale in ('"gauntlet"', '"rocket_launcher"', '"grappling_hook"', '"heavy_machinegun"'):
        assert stale not in token_block


def test_ui_retail_advert_runtime_seam_restored() -> None:
    ui_shared_h = (REPO_ROOT / "src/code/ui/ui_shared.h").read_text(encoding="utf-8")
    assert "int cellId;" in ui_shared_h
    assert "const char *defaultContent;" in ui_shared_h
    assert "setupAdvertCellShader" in ui_shared_h
    assert "refreshAdvertCellShader" in ui_shared_h
    assert "activateAdvert" in ui_shared_h
    assert "initAdvertisementBridge" in ui_shared_h

    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    update_block = _extract_function_block(
        ui_shared, "static qhandle_t Item_UpdateAdvertShader(itemDef_t *item, qboolean refresh) {"
    )
    post_parse_block = _extract_function_block(ui_shared, "void Menu_PostParse(menuDef_t *menu) {")
    script_block = _extract_function_block(ui_shared, "static void Script_ActivateAdvert")
    assert "static void Menu_SetupAdvertCellShaders(menuDef_t *menu)" in ui_shared
    assert "static void Menu_RefreshAdvertCellShaders(menuDef_t *menu)" in ui_shared
    assert "static qhandle_t Item_UpdateAdvertShader(itemDef_t *item, qboolean refresh)" in ui_shared
    assert 'if (item->window.ownerDraw == UI_ADVERT)' in ui_shared
    assert "parent = (menuDef_t *)item->parent;" in ui_shared
    assert "!(parent->window.flags & WINDOW_VISIBLE)" in ui_shared
    assert "!(parent->window.flags & WINDOW_FORCED)" in ui_shared
    assert "rect.x = 0.0f;" in ui_shared
    assert "rect.y = 0.0f;" in ui_shared
    assert "rect.w = 0.0f;" in ui_shared
    assert "rect.h = 0.0f;" in ui_shared
    assert "shader = DC->refreshAdvertCellShader(item->defaultContent, &rect, item->cellId);" in update_block
    assert "shader = DC->setupAdvertCellShader(item->defaultContent, &rect, item->cellId);" in update_block
    assert "item->window.background = shader;" in update_block
    assert "item->window.style = WINDOW_STYLE_SHADER;" in update_block
    assert post_parse_block.index("Menu_UpdatePosition(menu);") < post_parse_block.index(
        "Menu_SetupAdvertCellShaders(menu);"
    )
    assert "static void Script_ActivateAdvert(itemDef_t *item, char **args)" in ui_shared
    assert "if (!String_Parse(args, &cellIdToken)) {" in script_block
    assert "DC->activateAdvert(atoi(cellIdToken));" in script_block
    assert '{"activateAdvert", &Script_ActivateAdvert}' in ui_shared
    assert '{"cellId", ItemParse_cellId, NULL}' in ui_shared
    assert '{"defaultContent", ItemParse_defaultContent, NULL}' in ui_shared

    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")
    assert "void\t\t\ttrap_QL_InitAdvertisementBridge( void );" in ui_local
    assert "qhandle_t\t\ttrap_QL_SetupAdvertCellShader( const char *defaultContent, const rectDef_t *rect, int cellId );" in ui_local
    assert "qhandle_t\t\ttrap_QL_RefreshAdvertCellShader( const char *defaultContent, const rectDef_t *rect, int cellId );" in ui_local
    assert "void\t\t\ttrap_QL_UpdateAdvert( int handleOrToken, int area );" in ui_local
    assert "void\t\t\ttrap_QL_ActivateAdvert( int cellId );" in ui_local

    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    advert_block = _extract_function_block(
        ui_main, "static void UI_DrawAdvert(rectDef_t *rect, vec4_t color, qhandle_t shader) {"
    )
    assert "static qhandle_t UI_SetupAdvertCellShader" in ui_main
    assert "static qhandle_t UI_RefreshAdvertCellShader" in ui_main
    assert "static void UI_ActivateAdvert(int cellId)" in ui_main
    assert "static void UI_InitAdvertisementBridge(void)" in ui_main
    assert "trap_QL_InitAdvertisementBridge();" in ui_main
    assert "qhandle_t shader = trap_QL_SetupAdvertCellShader( defaultContent, rect, cellId );" in ui_main
    assert "qhandle_t shader = trap_QL_RefreshAdvertCellShader( defaultContent, rect, cellId );" in ui_main
    assert "trap_QL_UpdateAdvert( shader, pixelArea );" in ui_main
    assert "trap_QL_ActivateAdvert( cellId );" in ui_main
    assert "static void UI_DrawAdvert(rectDef_t *rect, vec4_t color, qhandle_t shader)" in ui_main
    assert advert_block.index("trap_R_SetColor(color);") < advert_block.index(
        "UI_DrawHandlePic(rect->x, rect->y, rect->w, rect->h, shader);"
    )
    assert advert_block.index("UI_DrawHandlePic(rect->x, rect->y, rect->w, rect->h, shader);") < advert_block.index(
        "trap_QL_UpdateAdvert( shader, pixelArea );"
    )
    assert advert_block.index("trap_QL_UpdateAdvert( shader, pixelArea );") < advert_block.index(
        "trap_R_SetColor(NULL);"
    )
    assert "case UI_ADVERT:" in ui_main
    assert "UI_InitAdvertisementBridge();" in ui_main
    assert "uiInfo.uiDC.setupAdvertCellShader = &UI_SetupAdvertCellShader;" in ui_main
    assert "uiInfo.uiDC.refreshAdvertCellShader = &UI_RefreshAdvertCellShader;" in ui_main
    assert "uiInfo.uiDC.activateAdvert = &UI_ActivateAdvert;" in ui_main
    assert "uiInfo.uiDC.initAdvertisementBridge();" not in ui_main
    assert ui_main.index("UI_InitAdvertisementBridge();") < ui_main.index("uiInfo.uiDC.setupAdvertCellShader = &UI_SetupAdvertCellShader;")


def test_ui_retail_advert_paint_refresh_and_browser_active_gate_restored() -> None:
    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    helper_block = _extract_function_block(ui_shared, "static qboolean Menu_WebBrowserActive(void) {")
    paint_block = _extract_function_block(ui_shared, "void Menu_Paint(menuDef_t *menu, qboolean forcePaint) {")

    assert 'DC->getCVarValue("web_browserActive")' in helper_block

    hidden_gate = paint_block.index("if (!(menu->window.flags & WINDOW_VISIBLE) &&  !forcePaint) {")
    hidden_clear = paint_block.index("menu->window.flags &= ~WINDOW_FORCED;", hidden_gate)
    hidden_refresh = paint_block.index("Menu_RefreshAdvertCellShaders(menu);", hidden_clear)
    hidden_return = paint_block.index("return;", hidden_refresh)
    assert hidden_gate < hidden_clear < hidden_refresh < hidden_return

    ownerdraw_gate = paint_block.index("if ((menu->window.ownerDrawFlags || menu->window.ownerDrawFlags2) && DC->ownerDrawVisible &&")
    browser_gate = paint_block.index("if (Menu_WebBrowserActive()) {")
    force_flag = paint_block.index("if (forcePaint) {")
    visible_refresh = paint_block.index("Menu_RefreshAdvertCellShaders(menu);", browser_gate)
    preset_refresh = paint_block.index("Menu_UpdatePresetLists(menu);")

    assert ownerdraw_gate < browser_gate < force_flag < visible_refresh < preset_refresh


def test_ui_retail_listbox_and_secondary_ownerdraw_flags_parse_cleanly() -> None:
    ui_shared_h = (REPO_ROOT / "src/code/ui/ui_shared.h").read_text(encoding="utf-8")
    assert "int ownerDrawFlags2;" in ui_shared_h
    assert "vec4_t altRowColor;" in ui_shared_h
    assert "vec4_t elementColor;" in ui_shared_h
    assert "vec4_t selectedColor;" in ui_shared_h
    assert "qhandle_t outlineImage;" in ui_shared_h
    assert "qboolean altRowColorSet;" in ui_shared_h
    assert "qboolean elementColorSet;" in ui_shared_h
    assert "qboolean selectedColorSet;" in ui_shared_h

    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    for expected in (
        "qboolean ItemParse_ownerdrawFlag2( itemDef_t *item, int handle ) {",
        "static qboolean ItemParse_listBoxColor( itemDef_t *item, int handle, vec4_t target, qboolean *colorSet ) {",
        "qboolean ItemParse_altrowcolor( itemDef_t *item, int handle ) {",
        "qboolean ItemParse_elementcolor( itemDef_t *item, int handle ) {",
        "qboolean ItemParse_selectedcolor( itemDef_t *item, int handle ) {",
        "qboolean ItemParse_outlineimage( itemDef_t *item, int handle ) {",
        "qboolean MenuParse_ownerdrawFlag2( itemDef_t *item, int handle ) {",
        '{"ownerdrawFlag2", ItemParse_ownerdrawFlag2, NULL},',
        '{"altrowcolor", ItemParse_altrowcolor, NULL},',
        '{"elementcolor", ItemParse_elementcolor, NULL},',
        '{"selectedcolor", ItemParse_selectedcolor, NULL},',
        '{"outlineimage", ItemParse_outlineimage, NULL},',
        '{"ownerdrawFlag2", MenuParse_ownerdrawFlag2, NULL},',
        "item->window.ownerDrawFlags2 |= i;",
        "menu->window.ownerDrawFlags2 |= i;",
        "if ((item->window.ownerDrawFlags || item->window.ownerDrawFlags2) && DC->ownerDrawVisible) {",
        "if (!DC->ownerDrawVisible(item->window.ownerDrawFlags, item->window.ownerDrawFlags2)) {",
        "if ((menu->window.ownerDrawFlags || menu->window.ownerDrawFlags2) && DC->ownerDrawVisible &&",
        "!DC->ownerDrawVisible(menu->window.ownerDrawFlags, menu->window.ownerDrawFlags2)) {",
        "((listBoxDef_t *)item->typeData)->elementColor[0] = 1.0f;",
        "((listBoxDef_t *)item->typeData)->elementColor[3] = 1.0f;",
        "((listBoxDef_t *)item->typeData)->selectedColor[0] = 1.0f;",
        "((listBoxDef_t *)item->typeData)->selectedColor[3] = 1.0f;",
        "item->outlineImage = DC->registerShaderNoMip( imageName );",
        "backgroundX = x + 2;",
        "backgroundY = y + 6;",
        "backgroundW = item->window.rect.w - SCROLLBAR_SIZE - 6;",
        "if ( item->outlineImage ) {\n\t\t\t\t\t\tDC->drawHandlePic( backgroundX, backgroundY, backgroundW, listPtr->elementHeight, item->outlineImage );\n\t\t\t\t\t} else {\n\t\t\t\t\t\tDC->fillRect( backgroundX, backgroundY, backgroundW, listPtr->elementHeight, item->window.outlineColor );",
        "if ( listPtr->altRowColorSet && ( (int)i & 1 ) ) {",
        "DC->fillRect( backgroundX, backgroundY, backgroundW, listPtr->elementHeight, listPtr->altRowColor );",
        "Item_DrawText(item, x + 4, y + listPtr->elementHeight, textColor, text, 0, 0);",
    ):
        assert expected in ui_shared


def test_ui_native_import_table_matches_recovered_retail_slots() -> None:
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")
    ui_public = (REPO_ROOT / "src/code/ui/ui_public.h").read_text(encoding="utf-8")
    ql_ui_imports = (REPO_ROOT / "src/code/client/ql_ui_imports.inc").read_text(encoding="utf-8")
    aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]
    function_rows = {
        row["entry"].lower(): row
        for row in csv.DictReader(QL_STEAM_FUNCTIONS.read_text(encoding="utf-8").splitlines())
    }
    steam_hlil = QL_STEAM_HLIL_PART04.read_text(encoding="utf-8")
    steam_table_hlil = QL_STEAM_HLIL_PART07.read_text(encoding="utf-8")

    assert "UI_QL_IMPORT_R_REGISTERFONT = 70," in ui_public
    assert "UI_QL_IMPORT_DRAW_SCALED_TEXT = 94," in ui_public
    assert "UI_QL_IMPORT_MEASURE_TEXT = 95," in ui_public
    assert (
        ui_public.index("UI_QL_IMPORT_R_REGISTERFONT = 70,")
        < ui_public.index("UI_QL_IMPORT_DRAW_SCALED_TEXT = 94,")
        < ui_public.index("UI_QL_IMPORT_MEASURE_TEXT = 95,")
    )

    for expected in (
        "static qhandle_t QDECL QL_UI_trap_SetupAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {",
        "static qhandle_t QDECL QL_UI_trap_RefreshAdvertCellShader( const char *defaultContent, const void *rect, int cellId ) {",
        "static void QDECL QL_UI_trap_InitAdvertisementBridge( void ) {",
        "static void QDECL QL_UI_trap_UpdateAdvert( int handleOrToken, int area ) {",
        "static void QDECL QL_UI_trap_ActivateAdvert( int cellId ) {",
        "static int QDECL QL_UI_trap_Unused85( void ) {",
        "static int QDECL QL_UI_trap_SetCursorPos( int x, int y ) {",
        "static int QDECL QL_UI_trap_GetCursorPos( int *x, int *y ) {",
        "static int QDECL QL_UI_trap_IsSubscribedApp( int arg1 ) {",
        "static void QDECL QL_UI_trap_DrawScaledText(",
        "static unsigned long long QDECL QL_UI_trap_MeasureText(",
        "static void QDECL QL_UI_trap_GetItemDownloadInfo(",
        "static ql_import_f ql_ui_imports[UI_QL_NATIVE_IMPORT_COUNT];",
        "ql_ui_imports[UI_QL_IMPORT_S_STARTLOCALSOUND] = (ql_import_f)QL_UI_trap_S_StartLocalSound;",
        "ql_ui_imports[UI_QL_IMPORT_S_REGISTERSOUND] = (ql_import_f)QL_UI_trap_S_RegisterSound_QL;",
        "ql_ui_imports[UI_QL_IMPORT_LAN_GETPINGQUEUECOUNT] = (ql_import_f)QL_UI_trap_LAN_GetPingQueueCount;",
        "ql_ui_imports[UI_QL_IMPORT_LAN_CLEARPING] = (ql_import_f)QL_UI_trap_LAN_ClearPing;",
        "ql_ui_imports[UI_QL_IMPORT_LAN_GETPING] = (ql_import_f)QL_UI_trap_LAN_GetPing;",
        "ql_ui_imports[UI_QL_IMPORT_LAN_GETPINGINFO] = (ql_import_f)QL_UI_trap_LAN_GetPingInfo;",
        "ql_ui_imports[UI_QL_IMPORT_LAN_SAVECACHEDSERVERS] = (ql_import_f)QL_UI_trap_LAN_SaveCachedServers;",
        "ql_ui_imports[UI_QL_IMPORT_LAN_ADDSERVER] = (ql_import_f)QL_UI_trap_LAN_AddServer;",
        "ql_ui_imports[UI_QL_IMPORT_LAN_SERVERSTATUS] = (ql_import_f)QL_UI_trap_LAN_ServerStatus;",
        "ql_ui_imports[UI_QL_IMPORT_LAN_COMPARESERVERS] = (ql_import_f)QL_UI_trap_LAN_CompareServers;",
        "ql_ui_imports[UI_QL_IMPORT_MEMORY_REMAINING] = (ql_import_f)QL_UI_trap_MemoryRemaining;",
        "ql_ui_imports[UI_QL_IMPORT_S_STOPBACKGROUNDTRACK] = (ql_import_f)QL_UI_trap_S_StopBackgroundTrack;",
        "ql_ui_imports[UI_QL_IMPORT_S_STARTBACKGROUNDTRACK] = (ql_import_f)QL_UI_trap_S_StartBackgroundTrack;",
        "ql_ui_imports[UI_QL_IMPORT_R_REMAP_SHADER] = (ql_import_f)QL_UI_trap_R_RemapShader;",
        "ql_ui_imports[UI_QL_IMPORT_SETUP_ADVERT_CELL_SHADER] = (ql_import_f)QL_UI_trap_SetupAdvertCellShader;",
        "ql_ui_imports[UI_QL_IMPORT_REFRESH_ADVERT_CELL_SHADER] = (ql_import_f)QL_UI_trap_RefreshAdvertCellShader;",
        "ql_ui_imports[UI_QL_IMPORT_INIT_ADVERTISEMENT_BRIDGE] = (ql_import_f)QL_UI_trap_InitAdvertisementBridge;",
        "ql_ui_imports[UI_QL_IMPORT_UNUSED_83] = (ql_import_f)QL_UI_trap_UpdateAdvert;",
        "ql_ui_imports[UI_QL_IMPORT_ACTIVATE_ADVERT] = (ql_import_f)QL_UI_trap_ActivateAdvert;",
        "ql_ui_imports[UI_QL_IMPORT_UNUSED_85] = (ql_import_f)QL_UI_trap_Unused85;",
        "ql_ui_imports[UI_QL_IMPORT_SET_CURSOR_POS] = (ql_import_f)QL_UI_trap_SetCursorPos;",
        "ql_ui_imports[UI_QL_IMPORT_GET_CURSOR_POS] = (ql_import_f)QL_UI_trap_GetCursorPos;",
        "ql_ui_imports[UI_QL_IMPORT_PC_ADD_GLOBAL_DEFINE] = (ql_import_f)QL_UI_trap_PC_AddGlobalDefine;",
        "ql_ui_imports[UI_QL_IMPORT_IS_SUBSCRIBED_APP] = (ql_import_f)QL_UI_trap_IsSubscribedApp;",
        "ql_ui_imports[UI_QL_IMPORT_DRAW_SCALED_TEXT] = (ql_import_f)QL_UI_trap_DrawScaledText;",
        "ql_ui_imports[UI_QL_IMPORT_MEASURE_TEXT] = (ql_import_f)QL_UI_trap_MeasureText;",
        "ql_ui_imports[UI_QL_IMPORT_GET_ITEM_DOWNLOAD_INFO] = (ql_import_f)QL_UI_trap_GetItemDownloadInfo;",
    ):
        assert expected in cl_ui

    assert "return CL_AdvertisementBridge_SetupUIAdvertCellShader( defaultContent, rect, cellId );" in cl_ui
    assert "return CL_AdvertisementBridge_RefreshUIAdvertCellShader( defaultContent, rect, cellId );" in cl_ui

    for expected in (
        "static void QDECL QL_UI_trap_R_RegisterFont( const char *fontName, int pointSize, fontInfo_t *font ) {",
        "UI_Import_Syscall( UI_R_REGISTERFONT, fontName, pointSize, font );",
        "static void QDECL QL_UI_trap_S_StartLocalSound( sfxHandle_t sfx, int channelNum ) {",
        "UI_Import_Syscall( UI_S_STARTLOCALSOUND, sfx, channelNum );",
        "static sfxHandle_t QDECL QL_UI_trap_S_RegisterSound( const char *sample, qboolean compressed ) {",
        "return UI_Import_Syscall( UI_S_REGISTERSOUND, sample, compressed );",
        "static void QDECL QL_UI_trap_S_StopBackgroundTrack( void ) {",
        "UI_Import_Syscall( UI_S_STOPBACKGROUNDTRACK );",
        "static void QDECL QL_UI_trap_S_StartBackgroundTrack( const char *intro, const char *loop ) {",
        "UI_Import_Syscall( UI_S_STARTBACKGROUNDTRACK, intro, loop );",
    ):
        assert expected in ql_ui_imports

    for alias, name in {
        "sub_4BEFB0": "QLCGImport_S_StartLocalSound",
        "sub_4befb0": "QLCGImport_S_StartLocalSound",
        "FUN_004befb0": "QLCGImport_S_StartLocalSound",
        "sub_4AFEC0": "QLCGImport_S_RegisterSound",
        "sub_4afec0": "QLCGImport_S_RegisterSound",
        "sub_4AFED0": "QLCGImport_S_StartBackgroundTrack",
        "sub_4DB030": "S_StopBackgroundTrack",
    }.items():
        assert aliases[alias] == name

    for entry, (name, size) in {
        "004befb0": ("FUN_004befb0", "9"),
        "004afec0": ("FUN_004afec0", "9"),
        "004afed0": ("FUN_004afed0", "9"),
        "004db030": ("FUN_004db030", "35"),
    }.items():
        assert function_rows[entry]["name"] == name
        assert function_rows[entry]["size"] == size
    assert "004b02f0" not in function_rows
    assert "sub_4B02F0" not in aliases
    assert "QLCGImport_S_StopBackgroundTrack" not in aliases.values()
    assert "QLUIImport_S_StopBackgroundTrack" not in aliases.values()

    for expected in (
        "004befb0    int32_t sub_4befb0()",
        "004befb4  return sub_4db3f0() __tailcall",
        "004afec0    int32_t sub_4afec0()",
        "004afec4  return sub_4d9e50() __tailcall",
        "004afed0    int32_t sub_4afed0()",
        "004afed4  return sub_4db060() __tailcall",
        "004bd978      sub_4db030()",
        "004db030    void sub_4db030()",
    ):
        assert expected in steam_hlil

    for expected in (
        "005673c0  void* data_5673c0 = sub_4befb0",
        "005673c4  void* data_5673c4 = sub_4afec0",
        "00567450  void* data_567450 = sub_4afff0",
        "00567454  void* data_567454 = 0x4b02f0",
        "00567458  void* data_567458 = sub_4afed0",
        "0056745c  void* data_56745c = sub_4bf290",
    ):
        assert expected in steam_table_hlil

    assert "ql_ui_imports[85] = (ql_import_f)QL_UI_trap_S_StopBackgroundTrack;" not in cl_ui
    assert "UI_QL_IMPORT_MEMORY_REMAINING = 101" not in cl_ui
    assert "UI_QL_IMPORT_R_REMAP_SHADER = 104" not in cl_ui


def test_ui_sound_import_wiring_matches_retail_native_and_vm_paths() -> None:
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")
    ql_ui_imports = (REPO_ROOT / "src/code/client/ql_ui_imports.inc").read_text(encoding="utf-8")
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_public = (REPO_ROOT / "src/code/ui/ui_public.h").read_text(encoding="utf-8")
    ui_syscalls = (REPO_ROOT / "src/code/ui/ui_syscalls.c").read_text(encoding="utf-8")
    steam_hlil = QL_STEAM_HLIL_PART04.read_text(encoding="utf-8")
    steam_table_hlil = QL_STEAM_HLIL_PART07.read_text(encoding="utf-8")
    aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]
    function_rows = {
        row["entry"].lower(): row
        for row in csv.DictReader(QL_STEAM_FUNCTIONS.read_text(encoding="utf-8").splitlines())
    }

    ui_import_values = _extract_enum_values(ui_public, "uiImport_t")
    ql_import_values = _extract_enum_values(ui_public, "uiQlImport_t")
    native_import_map = _extract_ui_native_import_map(ui_syscalls)

    expected_sound_slots = {
        "UI_S_STARTLOCALSOUND": ("UI_QL_IMPORT_S_STARTLOCALSOUND", 32, 34),
        "UI_S_STOPBACKGROUNDTRACK": ("UI_QL_IMPORT_S_STOPBACKGROUNDTRACK", 62, 71),
        "UI_S_STARTBACKGROUNDTRACK": ("UI_QL_IMPORT_S_STARTBACKGROUNDTRACK", 63, 72),
    }
    for legacy_name, (native_name, legacy_slot, native_slot) in expected_sound_slots.items():
        assert ui_import_values[legacy_name] == legacy_slot
        assert native_import_map[legacy_name] == native_name
        assert ql_import_values[native_name] == native_slot

    for expected in (
        "case UI_S_STARTLOCALSOUND: return UI_QL_IMPORT_S_STARTLOCALSOUND;",
        "case UI_S_STOPBACKGROUNDTRACK: return UI_QL_IMPORT_S_STOPBACKGROUNDTRACK;",
        "case UI_S_STARTBACKGROUNDTRACK: return UI_QL_IMPORT_S_STARTBACKGROUNDTRACK;",
        "void trap_S_StartLocalSound( sfxHandle_t sfx, int channelNum ) {",
        "syscall( UI_S_STARTLOCALSOUND, sfx, channelNum );",
        "void trap_S_StopBackgroundTrack( void ) {",
        "syscall( UI_S_STOPBACKGROUNDTRACK );",
        "void trap_S_StartBackgroundTrack( const char *intro, const char *loop) {",
        "syscall( UI_S_STARTBACKGROUNDTRACK, intro, loop );",
    ):
        assert expected in ui_syscalls

    for expected in (
        "case UI_S_STARTLOCALSOUND:",
        "S_StartLocalSound( args[1], args[2] );",
        "case UI_S_STOPBACKGROUNDTRACK:",
        "S_StopBackgroundTrack();",
        "case UI_S_STARTBACKGROUNDTRACK:",
        "S_StartBackgroundTrack( VMA(1), VMA(2));",
        "ql_ui_imports[UI_QL_IMPORT_S_STARTLOCALSOUND] = (ql_import_f)QL_UI_trap_S_StartLocalSound;",
        "ql_ui_imports[UI_QL_IMPORT_S_STOPBACKGROUNDTRACK] = (ql_import_f)QL_UI_trap_S_StopBackgroundTrack;",
        "ql_ui_imports[UI_QL_IMPORT_S_STARTBACKGROUNDTRACK] = (ql_import_f)QL_UI_trap_S_StartBackgroundTrack;",
    ):
        assert expected in cl_ui

    for expected in (
        "static void QDECL QL_UI_trap_S_StartLocalSound( sfxHandle_t sfx, int channelNum ) {",
        "UI_Import_Syscall( UI_S_STARTLOCALSOUND, sfx, channelNum );",
        "static void QDECL QL_UI_trap_S_StopBackgroundTrack( void ) {",
        "UI_Import_Syscall( UI_S_STOPBACKGROUNDTRACK );",
        "static void QDECL QL_UI_trap_S_StartBackgroundTrack( const char *intro, const char *loop ) {",
        "UI_Import_Syscall( UI_S_STARTBACKGROUNDTRACK, intro, loop );",
    ):
        assert expected in ql_ui_imports

    for expected in (
        "uiInfo.uiDC.startLocalSound = &trap_S_StartLocalSound;",
        "uiInfo.uiDC.startBackgroundTrack = &trap_S_StartBackgroundTrack;",
        "uiInfo.uiDC.stopBackgroundTrack = &trap_S_StopBackgroundTrack;",
    ):
        assert expected in ui_main

    assert ui_main.index("uiInfo.uiDC.startLocalSound = &trap_S_StartLocalSound;") < ui_main.index(
        "uiInfo.uiDC.startBackgroundTrack = &trap_S_StartBackgroundTrack;"
    )
    assert ui_main.index("uiInfo.uiDC.startBackgroundTrack = &trap_S_StartBackgroundTrack;") < ui_main.index(
        "uiInfo.uiDC.stopBackgroundTrack = &trap_S_StopBackgroundTrack;"
    )

    for alias, name in {
        "sub_4BEFB0": "QLCGImport_S_StartLocalSound",
        "sub_4befb0": "QLCGImport_S_StartLocalSound",
        "FUN_004befb0": "QLCGImport_S_StartLocalSound",
        "sub_4AFED0": "QLCGImport_S_StartBackgroundTrack",
        "sub_4afed0": "QLCGImport_S_StartBackgroundTrack",
        "sub_4DB030": "S_StopBackgroundTrack",
        "sub_4DB060": "S_StartBackgroundTrack",
    }.items():
        assert aliases[alias] == name

    for entry, (name, size) in {
        "004befb0": ("FUN_004befb0", "9"),
        "004afed0": ("FUN_004afed0", "9"),
        "004db030": ("FUN_004db030", "35"),
        "004db060": ("FUN_004db060", "351"),
    }.items():
        assert function_rows[entry]["name"] == name
        assert function_rows[entry]["size"] == size
    assert "004b02f0" not in function_rows
    assert "sub_4B02F0" not in aliases
    assert "QLCGImport_S_StopBackgroundTrack" not in aliases.values()
    assert "QLUIImport_S_StopBackgroundTrack" not in aliases.values()

    for expected in (
        "004befb0    int32_t sub_4befb0()",
        "004befb4  return sub_4db3f0() __tailcall",
        "004afed0    int32_t sub_4afed0()",
        "004afed4  return sub_4db060() __tailcall",
        "004bd978      sub_4db030()",
        "004db030    void sub_4db030()",
        "004db060    int32_t sub_4db060(char* arg1, char* arg2)",
    ):
        assert expected in steam_hlil

    for expected in (
        "005673c0  void* data_5673c0 = sub_4befb0",
        "00567450  void* data_567450 = sub_4afff0",
        "00567454  void* data_567454 = 0x4b02f0",
        "00567458  void* data_567458 = sub_4afed0",
        "0056745c  void* data_56745c = sub_4bf290",
    ):
        assert expected in steam_table_hlil

    assert "case UI_S_STARTLOCALSOUND: return UI_QL_IMPORT_S_REGISTERSOUND;" not in ui_syscalls
    assert "case UI_S_STOPBACKGROUNDTRACK: return UI_QL_IMPORT_UNUSED_85;" not in ui_syscalls
    assert "ql_ui_imports[85] = (ql_import_f)QL_UI_trap_S_StopBackgroundTrack;" not in cl_ui


def test_ui_script_sound_verbs_match_retail_hlil_and_display_context_callbacks() -> None:
    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_hlil = UI_HLIL_PART01.read_text(encoding="utf-8", errors="ignore")
    aliases = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))["ui"]
    function_rows = {
        row["entry"].lower(): row
        for row in csv.DictReader(UI_FUNCTIONS.read_text(encoding="utf-8").splitlines())
    }

    script_play_block = _extract_function_block(
        ui_shared, "void Script_Play(itemDef_t *item, char **args) {"
    )
    script_looped_block = _extract_function_block(
        ui_shared, "void Script_playLooped(itemDef_t *item, char **args) {"
    )
    item_run_script_block = _extract_function_block(
        ui_shared, "void Item_RunScript(itemDef_t *item, const char *s) {"
    )
    init_display_block = _extract_function_block(ui_main, "void _UI_Init( qboolean inGameLoad ) {")
    command_list_block = ui_shared.split("commandDef_t commandList[] =", 1)[1].split(
        "int scriptCommandCount = sizeof(commandList) / sizeof(commandDef_t);", 1
    )[0]

    assert aliases["sub_10016cd0"] == "Script_Play"
    assert aliases["sub_10016d20"] == "Script_playLooped"
    assert aliases["FUN_10016d70"] == "Item_RunScript"
    assert function_rows["10016d70"]["name"] == "FUN_10016d70"
    assert function_rows["10016d70"]["size"] == "246"
    assert "10016cd0" not in function_rows
    assert "10016d20" not in function_rows

    for expected in (
        "10016cd0    int32_t sub_10016cd0(int32_t* arg1)",
        "10016cd7  int32_t result = sub_10001500(arg1, 0)",
        "10016cec  int32_t* eax = sub_10014560()",
        "10016d0b  return (*(ecx_1 + 0x74))((*(ecx_1 + 0xac))(eax, 6))",
        "10016d20    int32_t sub_10016d20(int32_t* arg1)",
        "10016d27  int32_t result = sub_10001500(arg1, 0)",
        "10016d3c  int32_t* eax = sub_10014560()",
        "10016d4f  (*(data_106b40d0 + 0xb4))()",
        "10016d5e  return (*(data_106b40d0 + 0xb0))(eax, eax)",
        "10016d70    int32_t __convention(\"regparm\") sub_10016d70",
        "10016e04              char* eax_3 = (&data_1002a018)[esi_1 * 2]",
        "10016e46                  (&data_1002a01c)[esi_1 * 2](arg4, &var_808)",
        "10016e32                  (*(data_106b40d0 + 0x50))(&var_808)",
        "1002a0b0  char const (* data_1002a0b0)[0x5] = data_10028e74 {\"play\"}",
        "1002a0b4  void* data_1002a0b4 = sub_10016cd0",
        "1002a0b8  char const (* data_1002a0b8)[0xb] = data_10028e68 {\"playlooped\"}",
        "1002a0bc  void* data_1002a0bc = sub_10016d20",
    ):
        assert expected in ui_hlil

    assert "{\"play\", &Script_Play}" in command_list_block
    assert "{\"playlooped\", &Script_playLooped}" in command_list_block
    assert "String_Parse(args, &val)" in script_play_block
    assert "DC->startLocalSound(DC->registerSound(val, qfalse), CHAN_LOCAL_SOUND);" in script_play_block
    assert "DC->stopBackgroundTrack();" in script_looped_block
    assert "DC->startBackgroundTrack(val, val);" in script_looped_block
    assert "char script[UI_SCRIPT_BUFFER_SIZE], *p;" in item_run_script_block
    assert "(commandList[i].handler(item, &p));" in item_run_script_block
    assert "DC->runScript(&p);" in item_run_script_block
    assert "uiInfo.uiDC.registerSound = &trap_S_RegisterSound;" in init_display_block
    assert "uiInfo.uiDC.startLocalSound = &trap_S_StartLocalSound;" in init_display_block
    assert "uiInfo.uiDC.startBackgroundTrack = &trap_S_StartBackgroundTrack;" in init_display_block
    assert "uiInfo.uiDC.stopBackgroundTrack = &trap_S_StopBackgroundTrack;" in init_display_block


def test_ui_import_t_legacy_surface_has_complete_retail_native_remap() -> None:
    ui_public = (REPO_ROOT / "src/code/ui/ui_public.h").read_text(encoding="utf-8")
    ui_syscalls = (REPO_ROOT / "src/code/ui/ui_syscalls.c").read_text(encoding="utf-8")

    ui_import_values = _extract_enum_values(ui_public, "uiImport_t")
    ql_import_values = _extract_enum_values(ui_public, "uiQlImport_t")
    native_import_map = _extract_ui_native_import_map(ui_syscalls)

    expected_legacy_order = (
        "UI_ERROR",
        "UI_PRINT",
        "UI_MILLISECONDS",
        "UI_CVAR_SET",
        "UI_CVAR_VARIABLEVALUE",
        "UI_CVAR_VARIABLESTRINGBUFFER",
        "UI_CVAR_SETVALUE",
        "UI_CVAR_RESET",
        "UI_CVAR_CREATE",
        "UI_CVAR_INFOSTRINGBUFFER",
        "UI_ARGC",
        "UI_ARGV",
        "UI_CMD_EXECUTETEXT",
        "UI_FS_FOPENFILE",
        "UI_FS_READ",
        "UI_FS_WRITE",
        "UI_FS_FCLOSEFILE",
        "UI_FS_GETFILELIST",
        "UI_R_REGISTERMODEL",
        "UI_R_REGISTERSKIN",
        "UI_R_REGISTERSHADERNOMIP",
        "UI_R_CLEARSCENE",
        "UI_R_ADDREFENTITYTOSCENE",
        "UI_R_ADDPOLYTOSCENE",
        "UI_R_ADDLIGHTTOSCENE",
        "UI_R_RENDERSCENE",
        "UI_R_SETCOLOR",
        "UI_R_DRAWSTRETCHPIC",
        "UI_UPDATESCREEN",
        "UI_CM_LERPTAG",
        "UI_CM_LOADMODEL",
        "UI_S_REGISTERSOUND",
        "UI_S_STARTLOCALSOUND",
        "UI_KEY_KEYNUMTOSTRINGBUF",
        "UI_KEY_GETBINDINGBUF",
        "UI_KEY_SETBINDING",
        "UI_KEY_ISDOWN",
        "UI_KEY_GETOVERSTRIKEMODE",
        "UI_KEY_SETOVERSTRIKEMODE",
        "UI_KEY_CLEARSTATES",
        "UI_KEY_GETCATCHER",
        "UI_KEY_SETCATCHER",
        "UI_GETCLIPBOARDDATA",
        "UI_GETGLCONFIG",
        "UI_GETCLIENTSTATE",
        "UI_GETCONFIGSTRING",
        "UI_LAN_GETPINGQUEUECOUNT",
        "UI_LAN_CLEARPING",
        "UI_LAN_GETPING",
        "UI_LAN_GETPINGINFO",
        "UI_CVAR_REGISTER",
        "UI_CVAR_UPDATE",
        "UI_MEMORY_REMAINING",
        "UI_GET_CDKEY",
        "UI_SET_CDKEY",
        "UI_R_REGISTERFONT",
        "UI_R_MODELBOUNDS",
        "UI_PC_ADD_GLOBAL_DEFINE",
        "UI_PC_LOAD_SOURCE",
        "UI_PC_FREE_SOURCE",
        "UI_PC_READ_TOKEN",
        "UI_PC_SOURCE_FILE_AND_LINE",
        "UI_S_STOPBACKGROUNDTRACK",
        "UI_S_STARTBACKGROUNDTRACK",
        "UI_REAL_TIME",
        "UI_LAN_GETSERVERCOUNT",
        "UI_LAN_GETSERVERADDRESSSTRING",
        "UI_LAN_GETSERVERINFO",
        "UI_LAN_MARKSERVERVISIBLE",
        "UI_LAN_UPDATEVISIBLEPINGS",
        "UI_LAN_RESETPINGS",
        "UI_LAN_LOADCACHEDSERVERS",
        "UI_LAN_SAVECACHEDSERVERS",
        "UI_LAN_ADDSERVER",
        "UI_LAN_REMOVESERVER",
        "UI_CIN_PLAYCINEMATIC",
        "UI_CIN_STOPCINEMATIC",
        "UI_CIN_RUNCINEMATIC",
        "UI_CIN_DRAWCINEMATIC",
        "UI_CIN_SETEXTENTS",
        "UI_R_REMAP_SHADER",
        "UI_VERIFY_CDKEY",
        "UI_LAN_SERVERSTATUS",
        "UI_LAN_GETSERVERPING",
        "UI_LAN_SERVERISVISIBLE",
        "UI_LAN_COMPARESERVERS",
        "UI_FS_SEEK",
        "UI_SET_PBCLSTATUS",
        "UI_LAUNCHER_READSCREENSHOT",
    )
    expected_libc_values = {
        "UI_MEMSET": 100,
        "UI_MEMCPY": 101,
        "UI_STRNCPY": 102,
        "UI_SIN": 103,
        "UI_COS": 104,
        "UI_ATAN2": 105,
        "UI_SQRT": 106,
        "UI_FLOOR": 107,
        "UI_CEIL": 108,
    }

    for value, name in enumerate(expected_legacy_order):
        assert ui_import_values[name] == value
    assert {name: ui_import_values[name] for name in expected_libc_values} == expected_libc_values
    assert set(ui_import_values) == set(expected_legacy_order) | set(expected_libc_values)

    expected_native_slot_by_legacy_import = {
        "UI_PRINT": 0,
        "UI_ERROR": 1,
        "UI_MILLISECONDS": 2,
        "UI_REAL_TIME": 3,
        "UI_CVAR_REGISTER": 4,
        "UI_CVAR_CREATE": 5,
        "UI_CVAR_UPDATE": 6,
        "UI_CVAR_SET": 7,
        "UI_CVAR_SETVALUE": 8,
        "UI_CVAR_VARIABLESTRINGBUFFER": 9,
        "UI_CVAR_VARIABLEVALUE": 10,
        "UI_ARGC": 11,
        "UI_ARGV": 12,
        "UI_FS_FOPENFILE": 14,
        "UI_FS_READ": 15,
        "UI_FS_WRITE": 16,
        "UI_FS_FCLOSEFILE": 17,
        "UI_FS_SEEK": 18,
        "UI_FS_GETFILELIST": 19,
        "UI_CMD_EXECUTETEXT": 20,
        "UI_R_REGISTERMODEL": 21,
        "UI_R_REGISTERSKIN": 22,
        "UI_R_REGISTERSHADERNOMIP": 23,
        "UI_R_CLEARSCENE": 24,
        "UI_R_ADDREFENTITYTOSCENE": 25,
        "UI_R_ADDPOLYTOSCENE": 26,
        "UI_R_ADDLIGHTTOSCENE": 27,
        "UI_R_RENDERSCENE": 28,
        "UI_R_SETCOLOR": 29,
        "UI_R_DRAWSTRETCHPIC": 30,
        "UI_R_MODELBOUNDS": 31,
        "UI_UPDATESCREEN": 32,
        "UI_CM_LERPTAG": 33,
        "UI_S_STARTLOCALSOUND": 34,
        "UI_S_REGISTERSOUND": 35,
        "UI_KEY_KEYNUMTOSTRINGBUF": 36,
        "UI_KEY_GETBINDINGBUF": 37,
        "UI_KEY_SETBINDING": 38,
        "UI_KEY_ISDOWN": 39,
        "UI_KEY_GETOVERSTRIKEMODE": 40,
        "UI_KEY_SETOVERSTRIKEMODE": 41,
        "UI_KEY_CLEARSTATES": 42,
        "UI_KEY_GETCATCHER": 43,
        "UI_KEY_SETCATCHER": 44,
        "UI_GETCLIPBOARDDATA": 45,
        "UI_GETCLIENTSTATE": 46,
        "UI_GETGLCONFIG": 47,
        "UI_GETCONFIGSTRING": 48,
        "UI_LAN_GETSERVERCOUNT": 49,
        "UI_LAN_GETSERVERADDRESSSTRING": 50,
        "UI_LAN_GETSERVERINFO": 51,
        "UI_LAN_GETSERVERPING": 52,
        "UI_LAN_GETPINGQUEUECOUNT": 53,
        "UI_LAN_CLEARPING": 54,
        "UI_LAN_GETPING": 55,
        "UI_LAN_GETPINGINFO": 56,
        "UI_LAN_LOADCACHEDSERVERS": 57,
        "UI_LAN_SAVECACHEDSERVERS": 58,
        "UI_LAN_MARKSERVERVISIBLE": 59,
        "UI_LAN_SERVERISVISIBLE": 60,
        "UI_LAN_UPDATEVISIBLEPINGS": 61,
        "UI_LAN_ADDSERVER": 62,
        "UI_LAN_REMOVESERVER": 63,
        "UI_LAN_RESETPINGS": 64,
        "UI_LAN_SERVERSTATUS": 65,
        "UI_LAN_COMPARESERVERS": 66,
        "UI_MEMORY_REMAINING": 67,
        "UI_GET_CDKEY": 68,
        "UI_SET_CDKEY": 69,
        "UI_R_REGISTERFONT": 70,
        "UI_S_STOPBACKGROUNDTRACK": 71,
        "UI_S_STARTBACKGROUNDTRACK": 72,
        "UI_CIN_PLAYCINEMATIC": 73,
        "UI_CIN_STOPCINEMATIC": 74,
        "UI_CIN_DRAWCINEMATIC": 75,
        "UI_CIN_RUNCINEMATIC": 76,
        "UI_CIN_SETEXTENTS": 77,
        "UI_R_REMAP_SHADER": 78,
        "UI_VERIFY_CDKEY": 79,
        "UI_PC_ADD_GLOBAL_DEFINE": 88,
        "UI_PC_LOAD_SOURCE": 89,
        "UI_PC_FREE_SOURCE": 90,
        "UI_PC_READ_TOKEN": 91,
        "UI_PC_SOURCE_FILE_AND_LINE": 92,
        "UI_CVAR_RESET": 97,
        "UI_CVAR_INFOSTRINGBUFFER": 98,
        "UI_CM_LOADMODEL": 108,
        "UI_SET_PBCLSTATUS": 109,
        "UI_LAUNCHER_READSCREENSHOT": 110,
    }
    direct_native_only_slots = {
        13,
        80,
        81,
        82,
        83,
        84,
        85,
        86,
        87,
        93,
        94,
        95,
        96,
    }

    assert set(native_import_map) == set(expected_native_slot_by_legacy_import)
    assert direct_native_only_slots.isdisjoint(
        {
            ql_import_values[native_name]
            for native_name in native_import_map.values()
        }
    )
    for legacy_name, expected_native_slot in expected_native_slot_by_legacy_import.items():
        assert ql_import_values[native_import_map[legacy_name]] == expected_native_slot


def test_ui_native_host_text_wrappers_preserve_color_force_and_packed_measure_contract() -> None:
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")
    draw_block = _extract_function_block(
        cl_ui,
        "static void QDECL QL_UI_trap_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int limit, float *maxX, int forceColor ) {",
    )
    measure_block = _extract_function_block(
        cl_ui,
        "static unsigned long long QDECL QL_UI_trap_MeasureText( const char *text, const char *end, int fontHandle, float scale, int limit, float *outLeft ) {",
    )

    assert "RE_DrawScaledText( x, y, text, fontHandle, scale, limit, maxX, forceColor != qfalse ? qtrue : qfalse, ql_ui_currentColor );" in draw_block
    assert "float width;" in measure_block
    assert "float height;" in measure_block
    assert "float left;" in measure_block
    assert "RE_MeasureScaledText( text, end, fontHandle, scale, limit, &width, &height, &left );" in measure_block
    assert "QL_UI_WriteMeasureTextBounds( outLeft, left, width, height );" in measure_block
    assert "return QL_UI_PackFloatBits64( width, height );" in measure_block
    assert "RE_RegisterFont" not in draw_block
    assert "RE_RegisterFont" not in measure_block


def test_ui_native_syscall_bridge_matches_recovered_retail_slots() -> None:
    ui_syscalls = (REPO_ROOT / "src/code/ui/ui_syscalls.c").read_text(encoding="utf-8")

    for expected in (
        "static int UI_MapNativeImport( int arg ) {",
        "case UI_LAN_GETPINGQUEUECOUNT: return UI_QL_IMPORT_LAN_GETPINGQUEUECOUNT;",
        "case UI_LAN_CLEARPING: return UI_QL_IMPORT_LAN_CLEARPING;",
        "case UI_LAN_GETPING: return UI_QL_IMPORT_LAN_GETPING;",
        "case UI_LAN_GETPINGINFO: return UI_QL_IMPORT_LAN_GETPINGINFO;",
        "case UI_LAN_LOADCACHEDSERVERS: return UI_QL_IMPORT_LAN_LOADCACHEDSERVERS;",
        "case UI_LAN_SAVECACHEDSERVERS: return UI_QL_IMPORT_LAN_SAVECACHEDSERVERS;",
        "case UI_LAN_ADDSERVER: return UI_QL_IMPORT_LAN_ADDSERVER;",
        "case UI_LAN_SERVERSTATUS: return UI_QL_IMPORT_LAN_SERVERSTATUS;",
        "case UI_LAN_COMPARESERVERS: return UI_QL_IMPORT_LAN_COMPARESERVERS;",
        "case UI_MEMORY_REMAINING: return UI_QL_IMPORT_MEMORY_REMAINING;",
        "case UI_S_STOPBACKGROUNDTRACK: return UI_QL_IMPORT_S_STOPBACKGROUNDTRACK;",
        "case UI_CIN_SETEXTENTS: return UI_QL_IMPORT_CIN_SETEXTENTS;",
        "case UI_R_REGISTERFONT: return UI_QL_IMPORT_R_REGISTERFONT;",
        "case UI_R_REMAP_SHADER: return UI_QL_IMPORT_R_REMAP_SHADER;",
        "case UI_VERIFY_CDKEY: return UI_QL_IMPORT_VERIFY_CDKEY;",
        "case UI_SET_PBCLSTATUS: return UI_QL_IMPORT_SET_PBCLSTATUS;",
        "case UI_LAUNCHER_READSCREENSHOT: return UI_QL_IMPORT_LAUNCHER_READSCREENSHOT;",
        "static int QDECL UI_NativeImportSyscall( int arg, ... ) {",
        "importIndex = UI_MapNativeImport( arg );",
        "if ( importIndex < 0 || importIndex >= UI_QL_NATIVE_IMPORT_COUNT ) {",
        "import = ui_imports[importIndex];",
        "void dllEntry( void **exports, void *imports, int *apiVersion ) {",
        "ui_imports = (ql_import_f *)imports;",
        "syscall = UI_NativeImportSyscall;",
        "*exports = UI_GetNativeExportTable();",
        "*apiVersion = UI_QL_API_VERSION;",
        "static ql_import_f UI_GetNativeImportFunction( int importIndex ) {",
        "void trap_QL_InitAdvertisementBridge( void ) {",
        "qhandle_t trap_QL_SetupAdvertCellShader( const char *defaultContent, const rectDef_t *rect, int cellId ) {",
        "qhandle_t trap_QL_RefreshAdvertCellShader( const char *defaultContent, const rectDef_t *rect, int cellId ) {",
        "void trap_QL_UpdateAdvert( int handleOrToken, int area ) {",
        "void trap_QL_ActivateAdvert( int cellId ) {",
        "qboolean trap_QL_SetCursorPos( int x, int y ) {",
        "qboolean trap_QL_GetCursorPos( int *x, int *y ) {",
        "qboolean trap_QL_IsSubscribedApp( int appId ) {",
        "void trap_QL_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int limit, float *maxX, qboolean forceColor ) {",
        "unsigned long long trap_QL_MeasureText( const char *text, const char *end, int fontHandle, float scale, int limit, float *outLeft ) {",
        "void trap_QL_GetItemDownloadInfo( unsigned int itemIdLow, unsigned int itemIdHigh, unsigned long long *outDownloaded, unsigned long long *outTotal ) {",
        "UI_GetNativeImportFunction( UI_QL_IMPORT_INIT_ADVERTISEMENT_BRIDGE )",
        "UI_GetNativeImportFunction( UI_QL_IMPORT_SETUP_ADVERT_CELL_SHADER )",
        "UI_GetNativeImportFunction( UI_QL_IMPORT_REFRESH_ADVERT_CELL_SHADER )",
        "UI_GetNativeImportFunction( UI_QL_IMPORT_ACTIVATE_ADVERT )",
        "UI_GetNativeImportFunction( UI_QL_IMPORT_SET_CURSOR_POS )",
        "UI_GetNativeImportFunction( UI_QL_IMPORT_GET_CURSOR_POS )",
        "UI_GetNativeImportFunction( UI_QL_IMPORT_IS_SUBSCRIBED_APP )",
        "UI_GetNativeImportFunction( UI_QL_IMPORT_DRAW_SCALED_TEXT )",
        "UI_GetNativeImportFunction( UI_QL_IMPORT_MEASURE_TEXT )",
        "UI_GetNativeImportFunction( UI_QL_IMPORT_GET_ITEM_DOWNLOAD_INFO )",
    ):
        assert expected in ui_syscalls

    draw_block = _extract_function_block(
        ui_syscalls,
        "void trap_QL_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int limit, float *maxX, qboolean forceColor ) {",
    )
    measure_block = _extract_function_block(
        ui_syscalls,
        "unsigned long long trap_QL_MeasureText( const char *text, const char *end, int fontHandle, float scale, int limit, float *outLeft ) {",
    )

    for expected in (
        "ql_import_f import = UI_GetNativeImportFunction( UI_QL_IMPORT_DRAW_SCALED_TEXT );",
        "if ( !import ) {",
        "return;",
        "((void (QDECL *)( int, int, const char *, int, float, int, float *, int ))import)( x, y, text, fontHandle, scale, limit, maxX, forceColor ? qtrue : qfalse );",
    ):
        assert expected in draw_block

    for expected in (
        "ql_import_f import = UI_GetNativeImportFunction( UI_QL_IMPORT_MEASURE_TEXT );",
        "if ( !import ) {",
        "return 0;",
        "return ((unsigned long long (QDECL *)( const char *, const char *, int, float, int, float * ))import)( text, end, fontHandle, scale, limit, outLeft );",
    ):
        assert expected in measure_block

    assert "syscall(" not in draw_block
    assert "syscall(" not in measure_block
    assert "case UI_S_STOPBACKGROUNDTRACK: return UI_QL_IMPORT_UNUSED_85;" not in ui_syscalls


def test_ui_native_export_table_matches_recovered_retail_order() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")

    for expected in (
        "static void *ui_nativeExports[UI_NATIVE_EXPORT_COUNT] = {",
        "[UI_NATIVE_EXPORT_INIT] = UI_NativeInit,",
        "[UI_NATIVE_EXPORT_SHUTDOWN] = _UI_Shutdown,",
        "[UI_NATIVE_EXPORT_KEY_EVENT] = UI_NativeKeyEvent,",
        "[UI_NATIVE_EXPORT_MOUSE_EVENT] = _UI_MouseEvent,",
        "[UI_NATIVE_EXPORT_REFRESH] = _UI_Refresh,",
        "[UI_NATIVE_EXPORT_IS_FULLSCREEN] = _UI_IsFullscreen,",
        "[UI_NATIVE_EXPORT_SET_ACTIVE_MENU] = _UI_SetActiveMenu,",
        "[UI_NATIVE_EXPORT_CONSOLE_COMMAND] = UI_ConsoleCommand,",
        "[UI_NATIVE_EXPORT_DRAW_CONNECT_SCREEN] = UI_NativeDrawConnectScreen,",
        "[UI_NATIVE_EXPORT_HAS_UNIQUE_CD_KEY] = UI_NativeHasUniqueCDKey,",
        "[UI_NATIVE_EXPORT_REFRESH_DISPLAY_CONTEXT] = UI_RefreshDisplayContext,",
        "[UI_NATIVE_EXPORT_MENUS_ANY_VISIBLE] = Menus_AnyVisible,",
        "[UI_NATIVE_EXPORT_FOR_EACH_ARENA_NAME] = UI_ForEachArenaName,",
        "[UI_NATIVE_EXPORT_DRAW_ADVERTISEMENT_WAIT_SCREEN] = UI_DrawAdvertisementWaitScreen",
        "void **UI_GetNativeExportTable( void ) {",
        "return ui_nativeExports;",
    ):
        assert expected in ui_main

    ui_def = (REPO_ROOT / "src/code/ui/ui.def").read_text(encoding="utf-8")
    assert "EXPORTS" in ui_def
    assert "\tvmMain" in ui_def
    assert "\tdllEntry" in ui_def

    export_manifest = (REPO_ROOT / "tools/ci/manifests/native-dll-exports.json").read_text(encoding="utf-8")
    assert '"name": "uix86.dll"' in export_manifest
    assert '"exports": ["dllEntry", "vmMain"]' in export_manifest


def test_ui_native_api_bridge_is_anchored_to_committed_hlil_contract() -> None:
    ui_public = (REPO_ROOT / "src/code/ui/ui_public.h").read_text(encoding="utf-8")
    ui_syscalls = (REPO_ROOT / "src/code/ui/ui_syscalls.c").read_text(encoding="utf-8")
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")
    vm_source = (REPO_ROOT / "src/code/qcommon/vm.c").read_text(encoding="utf-8")
    ui_hlil = UI_HLIL_PART01.read_text(encoding="utf-8", errors="ignore")

    native_exports = _extract_enum_values(ui_public, "uiNativeExport_t")
    expected_export_order = (
        "UI_NATIVE_EXPORT_INIT",
        "UI_NATIVE_EXPORT_SHUTDOWN",
        "UI_NATIVE_EXPORT_KEY_EVENT",
        "UI_NATIVE_EXPORT_MOUSE_EVENT",
        "UI_NATIVE_EXPORT_REFRESH",
        "UI_NATIVE_EXPORT_IS_FULLSCREEN",
        "UI_NATIVE_EXPORT_SET_ACTIVE_MENU",
        "UI_NATIVE_EXPORT_CONSOLE_COMMAND",
        "UI_NATIVE_EXPORT_DRAW_CONNECT_SCREEN",
        "UI_NATIVE_EXPORT_HAS_UNIQUE_CD_KEY",
        "UI_NATIVE_EXPORT_REFRESH_DISPLAY_CONTEXT",
        "UI_NATIVE_EXPORT_MENUS_ANY_VISIBLE",
        "UI_NATIVE_EXPORT_FOR_EACH_ARENA_NAME",
        "UI_NATIVE_EXPORT_DRAW_ADVERTISEMENT_WAIT_SCREEN",
    )

    for index, export_name in enumerate(expected_export_order):
        assert native_exports[export_name] == index
    assert native_exports["UI_NATIVE_EXPORT_COUNT"] == len(expected_export_order)

    for expected in (
        "10003970    void*** dllEntry(void*** arg1, int32_t arg2, int32_t* arg3)",
        "1000397c  *arg1 = &data_1002aea4",
        "10003982  data_106b40a8 = arg2",
        "10003988  *arg3 = 8",
        "1002aea4  void* data_1002aea4 = sub_1000fab0",
        "1002aea8  void* data_1002aea8 = 0x100044e0",
        "1002aeac  void* data_1002aeac = sub_1000ff40",
        "1002aeb0  void* data_1002aeb0 = sub_10010000",
        "1002aeb4  void* data_1002aeb4 = sub_10004390",
        "1002aeb8  void* data_1002aeb8 = sub_10010380",
        "1002aebc  void* data_1002aebc = sub_100100d0",
        "1002aec0  void* data_1002aec0 = sub_10002ac0",
        "1002aec4  void* data_1002aec4 = sub_10010e30",
        "1002aec8  void* data_1002aec8 = sub_10003910",
        "1002aecc  void* data_1002aecc = sub_10003920",
        "1002aed0  void* data_1002aed0 = sub_100103c0",
        "1002aed4  void* data_1002aed4 = sub_10003930",
        "1002aed8  void* data_1002aed8 = sub_10011130",
    ):
        assert expected in ui_hlil

    dll_entry_block = _extract_function_block(
        ui_syscalls,
        "void dllEntry( void **exports, void *imports, int *apiVersion ) {",
    )
    assert "ui_imports = (ql_import_f *)imports;" in dll_entry_block
    assert "*exports = UI_GetNativeExportTable();" in dll_entry_block
    assert "*apiVersion = UI_QL_API_VERSION;" in dll_entry_block

    native_export_table_block = _extract_function_block(
        ui_main,
        "void **UI_GetNativeExportTable( void ) {",
    )
    assert "return ui_nativeExports;" in native_export_table_block
    assert "static void *ui_nativeExports[UI_NATIVE_EXPORT_COUNT] = {" in ui_main

    vm_bridge_block = _extract_function_block(
        vm_source,
        "static int VM_CallNativeExports( vm_t *vm, int callnum, const int *args ) {",
    )
    assert "if ( vm->dllInterface && vm->dllApiVersion > UI_API_VERSION ) {" in vm_bridge_block
    assert "if ( callnum == UI_GETAPIVERSION ) {" in vm_bridge_block
    assert "return vm->dllApiVersion;" in vm_bridge_block
    assert "uiExportIndex = callnum - 1;" in vm_bridge_block

    ql_import_values = _extract_enum_values(ui_public, "uiQlImport_t")
    assert ql_import_values["UI_QL_IMPORT_CMD_ARGS_BUFFER"] == 13
    assert ql_import_values["UI_QL_IMPORT_SETUP_ADVERT_CELL_SHADER"] == 80
    assert ql_import_values["UI_QL_IMPORT_IS_SUBSCRIBED_APP"] == 93
    assert ql_import_values["UI_QL_IMPORT_DRAW_SCALED_TEXT"] == 94
    assert ql_import_values["UI_QL_IMPORT_MEASURE_TEXT"] == 95
    assert ql_import_values["UI_QL_IMPORT_GET_ITEM_DOWNLOAD_INFO"] == 96

    for expected in (
        "ql_ui_imports[UI_QL_IMPORT_CMD_ARGS_BUFFER] = (ql_import_f)QL_UI_trap_Cmd_ArgsBuffer_QL;",
        "ql_ui_imports[UI_QL_IMPORT_SETUP_ADVERT_CELL_SHADER] = (ql_import_f)QL_UI_trap_SetupAdvertCellShader;",
        "ql_ui_imports[UI_QL_IMPORT_REFRESH_ADVERT_CELL_SHADER] = (ql_import_f)QL_UI_trap_RefreshAdvertCellShader;",
        "ql_ui_imports[UI_QL_IMPORT_INIT_ADVERTISEMENT_BRIDGE] = (ql_import_f)QL_UI_trap_InitAdvertisementBridge;",
        "ql_ui_imports[UI_QL_IMPORT_UNUSED_83] = (ql_import_f)QL_UI_trap_UpdateAdvert;",
        "ql_ui_imports[UI_QL_IMPORT_ACTIVATE_ADVERT] = (ql_import_f)QL_UI_trap_ActivateAdvert;",
        "ql_ui_imports[UI_QL_IMPORT_SET_CURSOR_POS] = (ql_import_f)QL_UI_trap_SetCursorPos;",
        "ql_ui_imports[UI_QL_IMPORT_GET_CURSOR_POS] = (ql_import_f)QL_UI_trap_GetCursorPos;",
        "ql_ui_imports[UI_QL_IMPORT_IS_SUBSCRIBED_APP] = (ql_import_f)QL_UI_trap_IsSubscribedApp;",
        "ql_ui_imports[UI_QL_IMPORT_DRAW_SCALED_TEXT] = (ql_import_f)QL_UI_trap_DrawScaledText;",
        "ql_ui_imports[UI_QL_IMPORT_MEASURE_TEXT] = (ql_import_f)QL_UI_trap_MeasureText;",
        "ql_ui_imports[UI_QL_IMPORT_GET_ITEM_DOWNLOAD_INFO] = (ql_import_f)QL_UI_trap_GetItemDownloadInfo;",
    ):
        assert expected in cl_ui


def test_ui_native_import_reference_headers_match_recovered_hlil_slots() -> None:
    ui_public = (REPO_ROOT / "src/code/ui/ui_public.h").read_text(encoding="utf-8")
    ui_hlil = UI_HLIL_PART01.read_text(encoding="utf-8", errors="ignore")
    ql_import_values = _extract_enum_values(ui_public, "uiQlImport_t")
    expected_reference_values = {
        f"QL_UITRAP_{name.removeprefix('UI_QL_IMPORT_')}": value
        for name, value in ql_import_values.items()
        if name.startswith("UI_QL_IMPORT_") and value <= 96
    }
    assert sorted(expected_reference_values.values()) == list(range(97))

    generator = (REPO_ROOT / "scripts/ghidra/build_ui_ghidra_reference.py").read_text(
        encoding="utf-8"
    )
    generator_values = {
        match.group(1): int(match.group(2), 0)
        for match in re.finditer(
            r'\("(?P<name>QL_UITRAP_[A-Z0-9_]+)",\s*(?P<value>0x[0-9a-fA-F]+|\d+),',
            generator,
        )
    }
    assert generator_values == expected_reference_values

    reference_paths = (
        "references/reverse-engineering/ghidra/uix86/ui_ghidra_reference.h",
        "references/reverse-engineering/ghidra/uix86/source-recreation/include/ui_ghidra_reference.h",
        "src-re/ui/include/ui_local.h",
    )
    for relative_path in reference_paths:
        text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert _extract_numeric_defines(text, "QL_UITRAP_") == expected_reference_values
        assert "Retail native import-table layout (DAT_106b40a8 in Ghidra)" in text
        assert "legacy source/QVM uiImport_t syscall ABI" in text

    hlil_offset_evidence = {
        "QL_UITRAP_CVAR_REGISTER": 0x10,
        "QL_UITRAP_CVAR_UPDATE": 0x18,
        "QL_UITRAP_CVAR_SET": 0x1C,
        "QL_UITRAP_CVAR_VARIABLE_STRING_BUFFER": 0x24,
        "QL_UITRAP_CVAR_VARIABLE_VALUE": 0x28,
        "QL_UITRAP_FS_FOPENFILE": 0x38,
        "QL_UITRAP_CMD_EXECUTETEXT": 0x50,
        "QL_UITRAP_R_REGISTERMODEL": 0x54,
        "QL_UITRAP_R_RENDERSCENE": 0x70,
        "QL_UITRAP_R_SETCOLOR": 0x74,
        "QL_UITRAP_GETCLIENTSTATE": 0xB8,
        "QL_UITRAP_GETGLCONFIG": 0xBC,
        "QL_UITRAP_GETCONFIGSTRING": 0xC0,
        "QL_UITRAP_LAN_GETSERVERCOUNT": 0xC4,
        "QL_UITRAP_R_REGISTERFONT": 0x118,
        "QL_UITRAP_S_STARTBACKGROUNDTRACK": 0x120,
        "QL_UITRAP_CIN_PLAYCINEMATIC": 0x124,
        "QL_UITRAP_INIT_ADVERTISEMENT_BRIDGE": 0x148,
        "QL_UITRAP_UNUSED_83": 0x14C,
        "QL_UITRAP_UNUSED_85": 0x154,
        "QL_UITRAP_PC_LOAD_SOURCE": 0x164,
        "QL_UITRAP_PC_FREE_SOURCE": 0x168,
        "QL_UITRAP_PC_READ_TOKEN": 0x16C,
        "QL_UITRAP_PC_SOURCE_FILE_AND_LINE": 0x170,
        "QL_UITRAP_IS_SUBSCRIBED_APP": 0x174,
        "QL_UITRAP_DRAW_SCALED_TEXT": 0x178,
        "QL_UITRAP_MEASURE_TEXT": 0x17C,
        "QL_UITRAP_GET_ITEM_DOWNLOAD_INFO": 0x180,
    }
    for macro, byte_offset in hlil_offset_evidence.items():
        assert f"data_106b40a8 + 0x{byte_offset:x}" in ui_hlil
        assert expected_reference_values[macro] == byte_offset // 4


def test_ui_native_import_slab_assigns_every_recovered_retail_slot() -> None:
    ui_public = (REPO_ROOT / "src/code/ui/ui_public.h").read_text(encoding="utf-8")
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")
    ql_imports_inc = (REPO_ROOT / "src/code/client/ql_ui_imports.inc").read_text(
        encoding="utf-8"
    )
    init_block = _extract_function_block(cl_ui, "static void CL_InitUIImports( void ) {")
    ql_import_values = _extract_enum_values(ui_public, "uiQlImport_t")
    assignments = {
        match.group(1): match.group(2)
        for match in re.finditer(
            r"ql_ui_imports\[(UI_QL_IMPORT_[A-Z0-9_]+)\]\s*=\s*"
            r"\(ql_import_f\)([A-Za-z0-9_]+);",
            init_block,
        )
    }

    retail_native_imports = {
        name
        for name, value in ql_import_values.items()
        if name.startswith("UI_QL_IMPORT_") and value <= 96
    }
    source_bridge_extensions = {
        "UI_QL_IMPORT_CVAR_RESET",
        "UI_QL_IMPORT_CVAR_INFOSTRINGBUFFER",
        "UI_QL_IMPORT_CM_LOADMODEL",
        "UI_QL_IMPORT_SET_PBCLSTATUS",
        "UI_QL_IMPORT_LAUNCHER_READSCREENSHOT",
    }

    assert len(retail_native_imports) == 97
    assert sorted(ql_import_values[name] for name in retail_native_imports) == list(range(97))
    assert source_bridge_extensions.isdisjoint(retail_native_imports)
    assert set(assignments) == {
        name for name in ql_import_values if name.startswith("UI_QL_IMPORT_")
    }
    assert retail_native_imports.issubset(assignments)
    assert source_bridge_extensions.issubset(assignments)

    expected_direct_wrappers = {
        "UI_QL_IMPORT_CMD_ARGS_BUFFER": "QL_UI_trap_Cmd_ArgsBuffer_QL",
        "UI_QL_IMPORT_R_SETCOLOR": "QL_UI_trap_R_SetColor_QL",
        "UI_QL_IMPORT_SET_CDKEY": "QL_UI_trap_SetCDKey_QL",
        "UI_QL_IMPORT_SETUP_ADVERT_CELL_SHADER": "QL_UI_trap_SetupAdvertCellShader",
        "UI_QL_IMPORT_REFRESH_ADVERT_CELL_SHADER": "QL_UI_trap_RefreshAdvertCellShader",
        "UI_QL_IMPORT_INIT_ADVERTISEMENT_BRIDGE": "QL_UI_trap_InitAdvertisementBridge",
        "UI_QL_IMPORT_UNUSED_83": "QL_UI_trap_UpdateAdvert",
        "UI_QL_IMPORT_ACTIVATE_ADVERT": "QL_UI_trap_ActivateAdvert",
        "UI_QL_IMPORT_UNUSED_85": "QL_UI_trap_Unused85",
        "UI_QL_IMPORT_SET_CURSOR_POS": "QL_UI_trap_SetCursorPos",
        "UI_QL_IMPORT_GET_CURSOR_POS": "QL_UI_trap_GetCursorPos",
        "UI_QL_IMPORT_IS_SUBSCRIBED_APP": "QL_UI_trap_IsSubscribedApp",
        "UI_QL_IMPORT_DRAW_SCALED_TEXT": "QL_UI_trap_DrawScaledText",
        "UI_QL_IMPORT_MEASURE_TEXT": "QL_UI_trap_MeasureText",
        "UI_QL_IMPORT_GET_ITEM_DOWNLOAD_INFO": "QL_UI_trap_GetItemDownloadInfo",
    }
    for import_name, wrapper_name in expected_direct_wrappers.items():
        assert assignments[import_name] == wrapper_name

    wrapper_sources = cl_ui + "\n" + ql_imports_inc
    for import_name, wrapper_name in assignments.items():
        assert re.search(rf"\b{re.escape(wrapper_name)}\s*\(", wrapper_sources), import_name

    assert "Com_Memset( ql_ui_imports, 0, sizeof( ql_ui_imports ) );" in init_block
    assert "ql_ui_imports[UI_QL_IMPORT_UNUSED_85] = (ql_import_f)QL_UI_trap_Unused85;" in init_block


def test_ui_retail_keybind_pending_prompt_matches_width_and_paint_paths() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    width_block = _extract_function_block(ui_main, "static int UI_OwnerDrawWidth(int ownerDraw, float scale) {")
    paint_block = _extract_function_block(
        ui_main, "static void UI_DrawKeyBindStatus(rectDef_t *rect, float scale, vec4_t color, int textStyle) {"
    )

    assert 's = "Waiting for new key... Press ESCAPE to cancel";' in width_block
    assert 'Text_Paint(rect->x, rect->y, scale, color, "Waiting for new key... Press ESCAPE to cancel", 0, 0, textStyle);' in paint_block
    assert '"Waiting for new key... Press ESC..."' not in ui_main


def test_ui_retail_crosshair_color_key_handler_respects_health_color_gate() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    handle_block = _extract_function_block(
        ui_main, "static qboolean UI_OwnerDrawHandleKey(int ownerDraw, int flags, float *special, int key) {"
    )
    color_case = handle_block.split("case UI_CROSSHAIR_COLOR:", 1)[1].split("case UI_SELECTEDPLAYER:", 1)[0]

    assert 'if (trap_Cvar_VariableValue("cg_crosshairHealth") == 0) {' in color_case
    assert "return UI_CrosshairColor_HandleKey(flags, special, key);" in color_case
    assert color_case.index('if (trap_Cvar_VariableValue("cg_crosshairHealth") == 0) {') < color_case.index(
        "return UI_CrosshairColor_HandleKey(flags, special, key);"
    )


def test_ui_retail_crosshair_color_uses_one_based_palette_indices() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    preview_block = _extract_function_block(
        ui_main, "static void UI_GetCrosshairPreviewColor( const vec4_t baseColor, vec4_t previewColor ) {"
    )
    chooser_block = _extract_function_block(ui_main, "static void UI_DrawCrosshairColor( rectDef_t *rect ) {")
    key_block = _extract_function_block(
        ui_main, "static qboolean UI_CrosshairColor_HandleKey(int flags, float *special, int key) {"
    )

    assert "static const vec4_t uiCrosshairPalette[UI_CROSSHAIR_COLOR_COUNT]" in ui_main
    for expected in (
        "{ 1.0f, 0.0f, 0.0f, 1.0f }",
        "{ 1.0f, 1.0f, 1.0f, 1.0f }",
        "{ 0.5f, 0.5f, 0.5f, 1.0f }",
    ):
        assert expected in ui_main
    assert "Vector4Copy( uiCrosshairPalette[UI_GetCrosshairColorIndex() - 1], previewColor );" in preview_block
    assert "previewColor[i] *= brightness;" in preview_block
    assert "selected = UI_GetCrosshairColorIndex() - 1;" in chooser_block
    assert "segmentWidth = rect->w / (float)UI_CROSSHAIR_COLOR_COUNT;" in chooser_block
    assert "for ( i = 0; i < UI_CROSSHAIR_COLOR_COUNT; i++ ) {" in chooser_block
    assert "if (colorIndex > UI_CROSSHAIR_COLOR_COUNT) {" in key_block
    assert "colorIndex = UI_CROSSHAIR_COLOR_COUNT;" in key_block


def test_ui_retail_crosshair_nextmap_selectedplayer_ownerdraws_match_ql() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    crosshair_block = _extract_function_block(ui_main, "static void UI_DrawCrosshair(rectDef_t *rect, float scale, vec4_t color) {")
    nextmap_block = _extract_function_block(ui_main, "static void UI_DrawNextMap")
    selected_block = _extract_function_block(ui_main, "static void UI_DrawSelectedPlayer")
    build_player_block = _extract_function_block(ui_main, "static void UI_BuildPlayerList() {")
    selected_key_block = _extract_function_block(ui_main, "static qboolean UI_SelectedPlayer_HandleKey")
    draw_dispatch_block = _extract_function_block(
        ui_main,
        "static void UI_OwnerDraw(float x, float y, float w, float h, float text_x, float text_y, int ownerDraw, int ownerDrawFlags, int align, float special, float scale, vec4_t color, qhandle_t shader, int textStyle) {",
    )
    key_dispatch_block = _extract_function_block(
        ui_main, "static qboolean UI_OwnerDrawHandleKey(int ownerDraw, int flags, float *special, int key) {"
    )

    assert "case UI_CROSSHAIR:" in draw_dispatch_block
    assert "UI_DrawCrosshair(&rect, scale, color);" in draw_dispatch_block
    assert "case UI_CROSSHAIR:" in key_dispatch_block
    assert "UI_Crosshair_HandleKey(flags, special, key);" in key_dispatch_block
    assert "UI_GetCrosshairPreviewColor(color, previewColor);" in crosshair_block
    assert 'size = trap_Cvar_VariableValue("cg_crosshairSize");' in crosshair_block
    assert "if (size > 40.0f) {" in crosshair_block
    assert "size = 40.0f;" in crosshair_block
    assert "size = 24.0f;" in crosshair_block
    assert "x = rect->x - 2.0f;" in crosshair_block
    assert "y = rect->y - rect->h + 2.0f;" in crosshair_block
    assert "UI_DrawHandlePic(x, y, size, size, uiInfo.uiDC.Assets.crosshairShader[uiInfo.currentCrosshair]);" in crosshair_block
    assert "rect->w - size" not in crosshair_block
    assert "rect->h - size" not in crosshair_block

    assert "#define UI_NEXTMAP_CONFIGSTRING\t0x29A" in ui_main
    assert "case UI_NEXTMAP:" in draw_dispatch_block
    assert "UI_DrawNextMap(&rect, scale, color, textStyle);" in draw_dispatch_block
    assert "char nextMapText[MAX_INFO_STRING];" in nextmap_block
    assert "if ( !trap_GetConfigString( UI_NEXTMAP_CONFIGSTRING, nextMapText, sizeof( nextMapText ) ) ) {" in nextmap_block
    assert "Text_Paint( rect->x, rect->y, scale, color, nextMapText, 0, 0, textStyle );" in nextmap_block
    assert "CS_ROTATION_TITLES" not in nextmap_block
    assert "Info_ValueForKey" not in nextmap_block

    assert "case UI_SELECTEDPLAYER:" in draw_dispatch_block
    assert "UI_DrawSelectedPlayer(&rect, scale, color, textStyle);" in draw_dispatch_block
    assert "case UI_SELECTEDPLAYER:" in key_dispatch_block
    assert "UI_SelectedPlayer_HandleKey(flags, special, key);" in key_dispatch_block
    assert "uiInfo.playerRefresh = uiInfo.uiDC.realTime + 3000;" in selected_block
    assert "UI_BuildPlayerList();" in selected_block
    assert 'trap_Cvar_VariableStringBuffer( (uiInfo.teamLeader) ? "cg_selectedPlayerName" : "name", selectedPlayer, sizeof( selectedPlayer ) );' in selected_block
    assert "Text_Paint(rect->x, rect->y, scale, color, selectedPlayer, 0, 0, textStyle);" in selected_block
    assert 'UI_Cvar_VariableString("cg_selectedPlayerName")' not in selected_block
    assert 'UI_Cvar_VariableString("name")' not in selected_block
    assert 'trap_Cvar_Set("cg_selectedPlayer", va("%d", playerTeamNumber));' in build_player_block
    assert 'trap_Cvar_Set("cg_selectedPlayerName", uiInfo.teamNames[n]);' in build_player_block
    assert "UI_BuildPlayerList();" in selected_key_block
    assert "if (!uiInfo.teamLeader) {" in selected_key_block
    assert 'trap_Cvar_Set( "cg_selectedPlayerName", "Everyone");' in selected_key_block
    assert 'trap_Cvar_Set( "cg_selectedPlayerName", uiInfo.teamNames[selected]);' in selected_key_block
    assert 'trap_Cvar_Set( "cg_selectedPlayer", va("%d", selected));' in selected_key_block


def test_ui_retail_toggle_script_command_restored() -> None:
    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    assert "static void Script_Toggle(itemDef_t *item, char **args)" in ui_shared
    assert "menu = Menus_FindByName(name);" in ui_shared
    assert "if (menu->window.flags & WINDOW_VISIBLE)" in ui_shared
    assert "Menus_CloseByName(name);" in ui_shared
    assert "Menus_ActivateByName(name);" in ui_shared
    assert '{"toggle", &Script_Toggle}' in ui_shared
    assert 'DC->setCVar("model", name);' in ui_shared
    assert 'DC->setCVar("headmodel", name);' in ui_shared


def test_ui_display_mousemove_matches_retail_routing_only() -> None:
    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    block = _extract_function_block(ui_shared, "qboolean Display_MouseMove(void *p, int x, int y)")
    assert "menu = Menu_GetFocused();" in block
    assert "if (menu && (menu->window.flags & WINDOW_POPUP))" in block
    assert "Menu_HandleMouseMove(menu, x, y);" in block
    assert "Menu_HandleMouseMove(&Menus[i], x, y);" in block
    assert "menu->window.rectClient.x += x;" not in block
    assert "menu->window.rectClient.y += y;" not in block
    assert "Menu_UpdatePosition(menu);" not in block


def test_ui_mouse_event_projects_screen_coords_like_retail() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    block = _extract_function_block(ui_main, "void _UI_MouseEvent( int x, int y )\n{")

    for expected in (
        "static int UI_ConvertScreenCursorXToVirtual( int x ) {",
        "static int UI_ConvertScreenCursorYToVirtual( int y ) {",
        "uiInfo.uiDC.cursorx = UI_ConvertScreenCursorXToVirtual( x );",
        "uiInfo.uiDC.cursory = UI_ConvertScreenCursorYToVirtual( y );",
        "Display_MouseMove( NULL, uiInfo.uiDC.cursorx, uiInfo.uiDC.cursory );",
    ):
        assert expected in ui_main

    for unexpected in (
        "uiInfo.uiDC.cursorx += dx;",
        "uiInfo.uiDC.cursory += dy;",
        "Display_MouseMove(NULL, uiInfo.uiDC.cursorx, uiInfo.uiDC.cursory);",
    ):
        assert unexpected not in ui_main

    assert "(unsigned int)uiInfo.uiDC.cursorx <= SCREEN_WIDTH" in block
    assert "(unsigned int)uiInfo.uiDC.cursory <= SCREEN_HEIGHT" in block


def test_vm_mouse_consumer_bridge_pins_ui_and_cgame_retail_owners() -> None:
    alias_maps = json.loads(SYMBOL_ALIASES.read_text(encoding="utf-8"))
    ui_aliases = alias_maps["ui"]
    cgame_aliases = alias_maps["cgame"]
    ui_symbol_map = json.loads(UI_SYMBOL_MAP.read_text(encoding="utf-8"))
    cgame_symbol_map = json.loads(CGAME_SYMBOL_MAP.read_text(encoding="utf-8"))
    ui_hlil = UI_HLIL_PART01.read_text(encoding="utf-8")
    cgame_hlil = CGAME_HLIL.read_text(encoding="utf-8")
    ui_functions = UI_FUNCTIONS.read_text(encoding="utf-8")
    cgame_functions = CGAME_FUNCTIONS.read_text(encoding="utf-8")
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    cgame_main = (REPO_ROOT / "src/code/cgame/cg_main.c").read_text(encoding="utf-8")
    cgame_newdraw = (REPO_ROOT / "src/code/cgame/cg_newdraw.c").read_text(encoding="utf-8")
    vm_source = (REPO_ROOT / "src/code/qcommon/vm.c").read_text(encoding="utf-8")

    assert ui_aliases["sub_10010000"] == "_UI_MouseEvent"
    assert ui_aliases["FUN_1001d600"] == "Menu_HandleMouseMove"
    assert ui_aliases["FUN_10020740"] == "Display_MouseMove"
    assert ui_aliases["FUN_100208f0"] == "Menu_OverActiveItem"
    assert "sub_100208f0" not in ui_aliases

    assert cgame_aliases["sub_100208f0"] == "CG_MouseEvent"
    assert cgame_aliases["FUN_10063830"] == "CG_BrowserDisplayMouseMove"
    assert cgame_aliases["sub_10063830"] == "CG_BrowserDisplayMouseMove"
    assert "FUN_100208f0" not in cgame_aliases

    ui_mouse_entry = next(entry for entry in ui_symbol_map["functions"] if entry["raw_name"] == "sub_10010000")
    cgame_mouse_entry = next(entry for entry in cgame_symbol_map["functions"] if entry["raw_name"] == "sub_100208f0")
    assert "Projects host screen coordinates into the 640x480 UI cursor space" in ui_mouse_entry["comment"]
    assert "Accumulates cursor deltas" not in ui_mouse_entry["comment"]
    assert cgame_mouse_entry["signature"] == "void CG_MouseEvent(int x, int y)"
    assert "native export-table entry for the retail mouse path" in cgame_mouse_entry["comment"]

    for expected in (
        "FUN_1001d600,1001d600,426,0,unknown",
        "FUN_10020740,10020740,173,0,unknown",
        "FUN_100208f0,100208f0,249,0,unknown",
    ):
        assert expected in ui_functions
    assert "FUN_10063830,10063830,173,0,unknown" in cgame_functions

    for expected in (
        "10010000    int32_t sub_10010000(int32_t arg1, int32_t arg2)",
        "1001002a      x87_r7_2 = x87_r7 * fconvert.t(640.0) / float.t(data_10758248)",
        "1001003b  data_10746430 = eax",
        "1001004d  int32_t result = sub_10021270(float.t(arg2) * fconvert.t(480.0) / float.t(data_1075824c))",
        "10010059  data_10746434 = result",
        "1001006d  if (not(cond:1) && eax u<= 0x280 && result u<= 0x1e0)",
        "1001006f      return sub_10020740(result)",
        "10020740    int32_t __convention(\"regparm\") sub_10020740(int32_t arg1)",
        "1002077c      sub_1001d600(eax, float.s(ebx), float.s(arg1))",
        "100207cb          sub_1001d600(esi_1, var_20_2, var_1c_2)",
        "1002aeb0  void* data_1002aeb0 = sub_10010000",
    ):
        assert expected in ui_hlil

    for expected in (
        "10063830    int32_t __convention(\"regparm\") sub_10063830(int32_t arg1)",
        "1006383d  int32_t eax = sub_10060610()",
        "1006386c      sub_10060820(eax, float.s(ebx), float.s(arg1))",
        "100638bb          sub_10060820(esi_1, var_20_2, var_1c_2)",
        "100769c8  void* data_100769c8 = 0x100208f0",
    ):
        assert expected in cgame_hlil

    assert "case UI_MOUSE_EVENT:\n\t\t_UI_MouseEvent( arg0, arg1 );" in ui_main
    assert "[UI_NATIVE_EXPORT_MOUSE_EVENT] = _UI_MouseEvent," in ui_main
    ui_mouse_block = _extract_function_block(ui_main, "void _UI_MouseEvent( int x, int y )\n{")
    for expected in (
        "uiInfo.uiDC.cursorx = UI_ConvertScreenCursorXToVirtual( x );",
        "uiInfo.uiDC.cursory = UI_ConvertScreenCursorYToVirtual( y );",
        "Display_MouseMove( NULL, uiInfo.uiDC.cursorx, uiInfo.uiDC.cursory );",
    ):
        assert expected in ui_mouse_block
    assert "uiInfo.uiDC.cursorx += x;" not in ui_mouse_block
    assert "uiInfo.uiDC.cursory += y;" not in ui_mouse_block

    ui_move_block = _extract_function_block(ui_shared, "qboolean Display_MouseMove(void *p, int x, int y)")
    assert "Menu_HandleMouseMove(menu, x, y);" in ui_move_block
    assert "Menu_HandleMouseMove(&Menus[i], x, y);" in ui_move_block
    assert "Menu_UpdatePosition(menu);" not in ui_move_block

    assert "case CG_MOUSE_EVENT:\n\t\tcgDC.cursorx = cgs.cursorX;\n\t\tcgDC.cursory = cgs.cursorY;\n\t\tCG_MouseEvent( arg0, arg1 );" in cgame_main
    assert "[CG_NATIVE_EXPORT_MOUSE_EVENT] = CG_NativeMouseEvent," in cgame_main
    cgame_native_mouse_block = _extract_function_block(cgame_main, "static void CG_NativeMouseEvent( int dx, int dy ) {")
    assert "cgDC.cursorx = cgs.cursorX;" in cgame_native_mouse_block
    assert "cgDC.cursory = cgs.cursorY;" in cgame_native_mouse_block
    assert "CG_MouseEvent( dx, dy );" in cgame_native_mouse_block

    cgame_mouse_block = _extract_function_block(cgame_newdraw, "void CG_MouseEvent( int x, int y ) {")
    for expected in (
        "if ( cg_ignoreMouseInput.integer ) {",
        "allowSpectatorUi = CG_ShouldCaptureSpectatorUi();",
        "cgs.cursorX = CG_ConvertScreenCursorXToVirtual( x );",
        "cgs.cursorY = CG_ConvertScreenCursorYToVirtual( y );",
        "cgDC.cursorx = cgs.cursorX;",
        "cgDC.cursory = cgs.cursorY;",
        "n = CG_BrowserDisplayCursorType( cgs.cursorX, cgs.cursorY );",
        "CG_BrowserDisplayMouseMove( NULL, cgs.cursorX, cgs.cursorY );",
    ):
        assert expected in cgame_mouse_block
    assert "cgs.cursorX += x;" not in cgame_mouse_block
    assert "cgs.cursorY += y;" not in cgame_mouse_block
    assert "Display_MouseMove(" not in cgame_mouse_block

    cgame_browser_move_block = _extract_function_block(
        cgame_newdraw, "static qboolean CG_BrowserDisplayMouseMove( void *overlay, int x, int y ) {"
    )
    assert "CG_BrowserHandleMouseMove( overlay, (float)x, (float)y );" in cgame_browser_move_block
    assert "return Display_MouseMove( overlay, x, y );" in cgame_browser_move_block

    native_bridge_block = _extract_function_block(
        vm_source, "static int VM_CallNativeExports( vm_t *vm, int callnum, const int *args ) {"
    )
    assert "int uiExportIndex = callnum;" in native_bridge_block
    assert "uiExportIndex = callnum - 1;" in native_bridge_block
    assert "case UI_MOUSE_EVENT:" in native_bridge_block
    assert "exportFunc = dllExports[uiExportIndex];" in native_bridge_block
    assert "case CG_MOUSE_EVENT:" in native_bridge_block
    assert "dllExports[CG_NATIVE_EXPORT_MOUSE_EVENT]" in native_bridge_block
    assert native_bridge_block.count("((void (QDECL *)( int, int ))exportFunc)( args[0], args[1] );") >= 2


def test_ui_retail_item_font_runtime_compatibility_restored() -> None:
    ui_shared_h = (REPO_ROOT / "src/code/ui/ui_shared.h").read_text(encoding="utf-8")
    assert "#define ITEM_FONT_INHERIT -1" in ui_shared_h
    assert "int fontIndex;                 // retail item font bucket" in ui_shared_h
    assert "drawTextExt" in ui_shared_h
    assert "textWidthExt" in ui_shared_h
    assert "textHeightExt" in ui_shared_h
    assert "drawTextWithCursorExt" in ui_shared_h

    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    assert "qboolean ItemParse_font( itemDef_t *item, int handle )" in ui_shared
    assert '{"font", ItemParse_font, NULL}' in ui_shared
    assert "item->fontIndex = FONT_DEFAULT;" in ui_shared
    assert "if (!PC_Int_Parse(handle, &item->fontIndex)) {" in ui_shared
    assert "DC->textWidthExt(text, item->textscale, limit, item->fontIndex)" in ui_shared
    assert "DC->textHeightExt(text, item->textscale, limit, item->fontIndex)" in ui_shared
    assert "DC->drawTextExt(x, y, item->textscale, color, text, adjust, limit, item->textStyle, item->fontIndex);" in ui_shared
    assert "DC->drawTextWithCursorExt(x, y, item->textscale, color, text, cursorPos, cursor, limit, item->textStyle, item->fontIndex);" in ui_shared
    assert "Item_DrawText(item, item->textRect.x, item->textRect.y, color, textPtr, 0, 0);" in ui_shared
    assert "Item_DrawTextWithCursor(item, item->textRect.x + item->textRect.w + offset, item->textRect.y, newColor, buff + editPtr->paintOffset, item->cursorPos - editPtr->paintOffset , cursor, editPtr->maxPaintChars);" in ui_shared

    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert "static fontInfo_t *UI_SelectTextFont(float scale, int fontIndex)" in ui_main
    assert "return Text_WidthExt(text, scale, limit, ITEM_FONT_INHERIT);" in ui_main
    assert "return Text_HeightExt(text, scale, limit, ITEM_FONT_INHERIT);" in ui_main
    assert "Text_PaintExt(x, y, scale, color, text, adjust, limit, style, ITEM_FONT_INHERIT);" in ui_main
    assert "Text_PaintWithCursorExt(x, y, scale, color, text, cursorPos, cursor, limit, style, ITEM_FONT_INHERIT);" in ui_main
    assert "uiInfo.uiDC.drawTextExt = &Text_PaintExt;" in ui_main
    assert "uiInfo.uiDC.textWidthExt = &Text_WidthExt;" in ui_main
    assert "uiInfo.uiDC.textHeightExt = &Text_HeightExt;" in ui_main
    assert "uiInfo.uiDC.drawTextWithCursorExt = &Text_PaintWithCursorExt;" in ui_main


def test_ui_retail_font_cvars_and_scale_buckets_match_retail() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")

    assert 'UI_CVAR_TABLE_ENTRY( &ui_smallFont, "ui_smallFont", "0.25", CVAR_ARCHIVE ),' in ui_main
    assert 'UI_CVAR_TABLE_ENTRY( &ui_bigFont, "ui_bigFont", "0.4", CVAR_ARCHIVE ),' in ui_main

    select_block = _extract_function_block(
        ui_main,
        "static fontInfo_t *UI_SelectTextFont(float scale, int fontIndex) {",
    )
    small_threshold = select_block.index("if (scale <= ui_smallFont.value) {")
    big_threshold = select_block.index("if (scale >= ui_bigFont.value) {")
    text_return = select_block.rindex("return &uiInfo.uiDC.Assets.textFont;")

    assert small_threshold < big_threshold < text_return
    assert "return &uiInfo.uiDC.Assets.smallFont;" in select_block[small_threshold:big_threshold]
    assert "return &uiInfo.uiDC.Assets.bigFont;" in select_block[big_threshold:text_return]

    handle_block = _extract_function_block(
        ui_main,
        "static int UI_SelectTextFontHandle( float scale, int fontIndex ) {",
    )
    for expected in (
        "case FONT_SANS:",
        "return FONT_SANS;",
        "case FONT_MONO:",
        "return FONT_MONO;",
        "case FONT_DEFAULT:",
        "return FONT_DEFAULT;",
        "font = UI_SelectTextFont( scale, ITEM_FONT_INHERIT );",
        "if ( font == &uiInfo.uiDC.Assets.smallFont ) {",
    ):
        assert expected in handle_block
    assert "uiInfo.uiDC.Assets.bigFont" not in handle_block


def test_ui_text_paint_limit_uses_host_text_max_projection() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    block = _extract_function_block(
        ui_main,
        "static void Text_Paint_Limit(float *maxX, float x, float y, float scale, vec4_t color, const char* text, float adjust, int limit) {",
    )

    for expected in (
        "limitEnd = UI_GetTextLimitEnd( text, limit );",
        "UI_CopyTextSpan( text, limitEnd, limitedText, sizeof( limitedText ) );",
        "UI_AdjustFrom640( &screenX, &screenY, NULL, NULL );",
        "UI_AdjustFrom640( &screenMaxX, NULL, NULL, NULL );",
        "outMaxX = screenMaxX;",
        "fontHandle = UI_SelectTextFontHandle( scale, ITEM_FONT_INHERIT );",
        "trap_QL_DrawScaledText(",
        "scale * QL_FONT_HOST_POINT_SIZE * uiInfo.uiDC.yscale,",
        "0,",
        "&outMaxX,",
        "*maxX = ( outMaxX - uiInfo.uiDC.bias ) / uiInfo.uiDC.xscale;",
    ):
        assert expected in block

    assert "Text_PaintChar" not in block
    assert "trap_R_DrawStretchPic" not in block


def test_ui_host_text_metrics_span_and_cursor_use_retail_traps() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    metrics_block = _extract_function_block(
        ui_main,
        "static void UI_GetHostTextMetrics( const char *text, float scale, int limit, int fontIndex, int *outWidth, int *outHeight ) {",
    )
    span_block = _extract_function_block(
        ui_main,
        "static void UI_DrawHostTextSpan( float x, float y, float scale, const vec4_t color, const char *text, int fontIndex, int style, qboolean forceColor ) {",
    )
    cursor_block = _extract_function_block(
        ui_main,
        "static void Text_PaintWithCursorExt(float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style, int fontIndex) {",
    )

    for expected in (
        "UI_RefreshDisplayContextScale();",
        "limitEnd = UI_GetTextLimitEnd( text, limit );",
        "packed = trap_QL_MeasureText(",
        "UI_SelectTextFontHandle( scale, fontIndex ),",
        "scale * QL_FONT_HOST_POINT_SIZE * uiInfo.uiDC.yscale,",
        "UI_UnpackFloatBits64( packed, &width, &height );",
        "*outWidth = (int)( width / uiInfo.uiDC.xscale );",
        "*outHeight = (int)( height / uiInfo.uiDC.yscale );",
    ):
        assert expected in metrics_block

    for expected in (
        "UI_AdjustFrom640( &screenX, &screenY, NULL, NULL );",
        "hostScale = scale * QL_FONT_HOST_POINT_SIZE * uiInfo.uiDC.yscale;",
        "fontHandle = UI_SelectTextFontHandle( scale, fontIndex );",
        "ofs = ( style == ITEM_TEXTSTYLE_SHADOWED ) ? 1 : 2;",
        "trap_QL_DrawScaledText( (int)screenX + ofs, (int)screenY + ofs, text, fontHandle, hostScale, 0, NULL, qtrue );",
        "trap_QL_DrawScaledText( (int)screenX, (int)screenY, text, fontHandle, hostScale, 0, NULL, forceColor );",
    ):
        assert expected in span_block

    for expected in (
        "UI_DrawHostTextSpan( x, y, scale, color, drawText, fontIndex, style, qfalse );",
        "cursorEnd = UI_GetCursorTextEnd( text, limitEnd, cursorPos, color, cursorColor );",
        "UI_AdjustFrom640( &screenX, &screenY, NULL, NULL );",
        "hostScale = scale * QL_FONT_HOST_POINT_SIZE * uiInfo.uiDC.yscale;",
        "fontHandle = UI_SelectTextFontHandle( scale, fontIndex );",
        "UI_UnpackFloatBits64( trap_QL_MeasureText( text, cursorEnd, fontHandle, hostScale, 0, NULL ), &prefixWidth, &unusedHeight );",
        "trap_QL_DrawScaledText( (int)( screenX + prefixWidth ) + ofs, (int)screenY + ofs, cursorString, fontHandle, hostScale, 0, NULL, qtrue );",
        "trap_QL_DrawScaledText( (int)( screenX + prefixWidth ), (int)screenY, cursorString, fontHandle, hostScale, 0, NULL, qtrue );",
    ):
        assert expected in cursor_block

    for block in (span_block, cursor_block):
        assert "Text_PaintChar" not in block
        assert "trap_R_DrawStretchPic" not in block


def test_ui_retail_centered_text_helper_keeps_plain_text_style() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    paint_center_block = _extract_function_block(
        ui_main, "void Text_PaintCenter(float x, float y, float scale, vec4_t color, const char *text, float adjust) {"
    )

    assert "(void)adjust;" in paint_center_block
    assert "len = Text_Width(text, scale, 0);" in paint_center_block
    assert "Text_Paint(x - len / 2, y, scale, color, text, 0, 0, 0);" in paint_center_block
    assert "ITEM_TEXTSTYLE_SHADOWEDMORE" not in paint_center_block


def test_ui_retail_download_info_reads_item_progress_through_native_slot() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    download_block = _extract_function_block(
        ui_main,
        "static void UI_DisplayDownloadInfo( const char *downloadName, float centerPoint, float yStart, float scale ) {",
    )
    native_start = download_block.index("#ifndef Q3_VM")
    fallback_start = download_block.index("#else", native_start)
    native_block = download_block[native_start:fallback_start]

    assert 'trap_Cvar_VariableStringBuffer( "cl_downloadItem", downloadItem, sizeof( downloadItem ) );' in native_block
    assert 'sscanf( downloadItem, "%llu", &downloadItemId );' in native_block
    assert "trap_QL_GetItemDownloadInfo( (unsigned int)downloadItemId, (unsigned int)( downloadItemId >> 32 ), &downloadCount, &downloadSize );" in native_block
    assert 'trap_Cvar_VariableValue( "cl_downloadTime" );' in download_block
    assert 'trap_Cvar_VariableValue( "cl_downloadCount" )' not in native_block
    assert 'trap_Cvar_VariableValue( "cl_downloadSize" )' not in native_block
    assert "unsigned long long downloadSize, downloadCount;" in download_block


def test_ui_menu_font_parser_stores_resolved_font_token() -> None:
    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    block = _extract_function_block(ui_shared, "qboolean MenuParse_font( itemDef_t *item, int handle ) {")

    assert "qboolean MenuParse_font( itemDef_t *item, int handle )" in ui_shared
    for expected in (
        "if (!PC_String_Parse(handle, &menu->font)) {",
        "fontPath = menu->font;",
        "UI_NormalizeFontPath( &fontPath, &pointSize, QL_FONT_NAME_TEXT, QL_FONT_TEXT_POINT_SIZE );",
        "menu->font = String_Alloc( fontPath );",
        "if (!DC->Assets.fontRegistered) {",
        "DC->registerFont( fontPath, pointSize, &DC->Assets.textFont );",
        "DC->registerFont( QL_FONT_NAME_SMALL, QL_FONT_SMALL_POINT_SIZE, &DC->Assets.smallFont );",
        "DC->registerFont( QL_FONT_NAME_BIG, QL_FONT_BIG_POINT_SIZE, &DC->Assets.bigFont );",
        "DC->Assets.fontRegistered = qtrue;",
    ):
        assert expected in block


def test_ui_font_cache_ownership_and_registered_font_sizes_match_retail() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_shared_h = (REPO_ROOT / "src/code/ui/ui_shared.h").read_text(encoding="utf-8")
    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    main_menu = (REPO_ROOT / "src/ui/main.menu").read_text(encoding="utf-8")
    hud_menu = (REPO_ROOT / "src/ui/hud.menu").read_text(encoding="utf-8")
    asset_cache_block = _extract_function_block(ui_main, "void AssetCache() {")
    asset_parse_block = _extract_function_block(ui_main, "qboolean Asset_Parse(int handle) {")
    normalize_block = _extract_function_block(ui_shared, "void UI_NormalizeFontPath( const char **fontName, int *pointSize, const char *defaultFont, int defaultPointSize ) {")

    for expected in (
        '#define QL_FONT_NAME_TEXT "fonts/font"',
        '#define QL_FONT_NAME_SMALL "fonts/smallfont"',
        '#define QL_FONT_NAME_BIG "fonts/bigfont"',
        '#define QL_FONT_NAME_MONO "fonts/monofont"',
        "#define QL_FONT_TEXT_POINT_SIZE 24",
        "#define QL_FONT_SMALL_POINT_SIZE 16",
        "#define QL_FONT_BIG_POINT_SIZE 48",
        "#define QL_FONT_MONO_POINT_SIZE 16",
    ):
        assert expected in ui_shared_h

    assert "trap_R_RegisterFont(" not in asset_cache_block
    assert "trap_R_RegisterFont(fontPath, pointSize, &uiInfo.uiDC.Assets.textFont);" in asset_parse_block
    assert "trap_R_RegisterFont(fontPath, pointSize, &uiInfo.uiDC.Assets.smallFont);" in asset_parse_block
    assert "trap_R_RegisterFont(fontPath, pointSize, &uiInfo.uiDC.Assets.bigFont);" in asset_parse_block

    for expected in (
        '{ "FONT_DEFAULT", QL_FONT_NAME_TEXT, QL_FONT_TEXT_POINT_SIZE }',
        '{ "FONT_SANS", QL_FONT_NAME_SMALL, QL_FONT_SMALL_POINT_SIZE }',
        '{ "FONT_MONO", QL_FONT_NAME_MONO, QL_FONT_MONO_POINT_SIZE }',
        '{ "font2", QL_FONT_NAME_BIG, QL_FONT_BIG_POINT_SIZE }',
        '{ "fonts/arial.ttf", QL_FONT_NAME_TEXT, QL_FONT_TEXT_POINT_SIZE }',
        '{ "fonts/verdana.ttf", QL_FONT_NAME_SMALL, QL_FONT_SMALL_POINT_SIZE }',
    ):
        assert expected in ui_shared

    for expected in (
        "*fontName = uiLegacyFontMap[i].fontName;",
        "*pointSize = uiLegacyFontMap[i].pointSize;",
        "*fontName = defaultFont;",
        "*pointSize = defaultPointSize;",
    ):
        assert expected in normalize_block

    for expected in (
        'font "fonts/font" 16',
        'smallFont "fonts/smallfont" 12',
        'bigFont "fonts/bigfont" 20',
    ):
        assert re.search(expected.replace(" ", r"\s+"), main_menu)

    for expected in (
        'font "fonts/font" 24',
        'smallFont "fonts/smallfont" 16',
        'bigFont "fonts/bigfont" 48',
    ):
        assert re.search(expected.replace(" ", r"\s+"), hud_menu)


def test_ui_retail_preset_and_precision_runtime_restored() -> None:
    ui_shared_h = (REPO_ROOT / "src/code/ui/ui_shared.h").read_text(encoding="utf-8")
    assert "int precision;" in ui_shared_h
    assert "qboolean integer;" in ui_shared_h

    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    assert "static void Menu_UpdatePresetLists(menuDef_t *menu)" in ui_shared
    assert "static const char *Item_GetTextSource(itemDef_t *item, char *buffer, int bufferSize)" in ui_shared
    assert "static void UI_SetItemCvarValue(itemDef_t *item, float value)" in ui_shared
    assert "qboolean ItemParse_precision( itemDef_t *item, int handle )" in ui_shared
    assert "qboolean ItemParse_cvara( itemDef_t *item, int handle )" in ui_shared
    assert "qboolean ItemParse_cvarInt( itemDef_t *item, int handle )" in ui_shared
    assert "qboolean ItemParse_cvarPreset( itemDef_t *item, int handle )" in ui_shared
    assert '{"precision", ItemParse_precision, NULL}' in ui_shared
    assert '{"cvara", ItemParse_cvara, NULL}' in ui_shared
    assert '{"cvarInt", ItemParse_cvarInt, NULL}' in ui_shared
    assert '{"cvarPreset", ItemParse_cvarPreset, NULL}' in ui_shared
    assert '{"cvarPresetList", ItemParse_cvarStrList, NULL}' in ui_shared
    assert "const char *Item_PresetList_Setting(itemDef_t *item)" in ui_shared
    assert "int Item_PresetList_FindCvarByValue(itemDef_t *item)" in ui_shared
    assert "qboolean Item_PresetList_HandleKey(itemDef_t *item, int key)" in ui_shared
    assert "void Item_PresetList_Paint(itemDef_t *item)" in ui_shared
    assert "void Item_SliderColor_Paint(itemDef_t *item)" in ui_shared
    slider_color_block = _extract_function_block(ui_shared, "void Item_SliderColor_Paint(itemDef_t *item) {")
    assert "static const vec4_t uiSliderColorPalette[]" in ui_shared
    assert "colorIndex--;" in slider_color_block
    assert "thumbColor[3] = uiSliderColorPalette[colorIndex][3];" in slider_color_block
    assert "case ITEM_TYPE_PRESETLIST:" in ui_shared
    assert "case ITEM_TYPE_SLIDER_COLOR:" in ui_shared
    assert "Menu_UpdatePresetLists(menu);" in ui_shared
    assert 'DC->setCVar(item->cvar, "Custom");' in ui_shared

    basic_menu = (REPO_ROOT / "src/ui/ingame_options_basic.menu").read_text(encoding="utf-8")
    assert 'type ITEM_TYPE_PRESETLIST' in basic_menu
    assert 'cvara "ui_globalpreset"' in basic_menu
    assert 'cvarPresetList { "Default", "globalpreset_default"' in basic_menu

    advanced_menu = (REPO_ROOT / "src/ui/ingame_options_advanced.menu").read_text(encoding="utf-8")
    assert 'type ITEM_TYPE_PRESET' in advanced_menu
    assert 'type ITEM_TYPE_SLIDER_COLOR' in advanced_menu
    assert 'cvarPreset { "cg_forceEnemySkin" bright }' in advanced_menu
    assert 'cvarInt "cg_crosshairColor" 25 1 26' in advanced_menu


def test_ui_retail_parser_gating_extensions_restored() -> None:
    ui_shared_h = (REPO_ROOT / "src/code/ui/ui_shared.h").read_text(encoding="utf-8")
    assert "#define MAX_MENUITEMS 1024" in ui_shared_h
    assert "#define ITEM_CVAR_SLOT_COUNT 4" in ui_shared_h
    assert "const char *cvarTest[ITEM_CVAR_SLOT_COUNT];" in ui_shared_h
    assert "const char *enableCvar[ITEM_CVAR_SLOT_COUNT];" in ui_shared_h
    assert "int cvarFlags[ITEM_CVAR_SLOT_COUNT];" in ui_shared_h
    assert "Rectangle backgroundRect;" in ui_shared_h
    assert "qboolean backgroundSizeSet;" in ui_shared_h

    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    assert re.search(r"#define\s+UI_SCRIPT_BUFFER_SIZE\s+2048\b", ui_shared)
    assert "static qboolean Item_HasCvarFlags( const itemDef_t *item, int mask )" in ui_shared
    assert "static qboolean Item_EnableShowViaCvarSlot( const itemDef_t *item, int slot, int flag )" in ui_shared
    assert "qboolean ItemParse_cvarTest2( itemDef_t *item, int handle )" in ui_shared
    assert "qboolean ItemParse_cvarTest3( itemDef_t *item, int handle )" in ui_shared
    assert "qboolean ItemParse_cvarTest4( itemDef_t *item, int handle )" in ui_shared
    assert "static qboolean Parse_showCvar2_or_hideCvar2( itemDef_t *item, int handle, int flag )" in ui_shared
    assert "static qboolean Parse_showCvar3_or_hideCvar3( itemDef_t *item, int handle, int flag )" in ui_shared
    assert "static qboolean Parse_showCvar4_or_hideCvar4( itemDef_t *item, int handle, int flag )" in ui_shared
    assert '{"cvarTest2", ItemParse_cvarTest2, NULL}' in ui_shared
    assert '{"cvarTest3", ItemParse_cvarTest3, NULL}' in ui_shared
    assert '{"cvarTest4", ItemParse_cvarTest4, NULL}' in ui_shared
    assert '{"showCvar2", ItemParse_showCvar2, NULL}' in ui_shared
    assert '{"showCvar3", ItemParse_showCvar3, NULL}' in ui_shared
    assert '{"showCvar4", ItemParse_showCvar4, NULL}' in ui_shared
    assert '{"hideCvar2", ItemParse_hideCvar2, NULL}' in ui_shared
    assert '{"hideCvar3", ItemParse_hideCvar3, NULL}' in ui_shared
    assert '{"hideCvar4", ItemParse_hideCvar4, NULL}' in ui_shared
    assert "qboolean MenuParse_backgroundSize( itemDef_t *item, int handle )" in ui_shared
    assert 'menu->backgroundSizeSet = qtrue;' in ui_shared
    assert '{"backgroundSize", MenuParse_backgroundSize, NULL}' in ui_shared

    script_parse_start = ui_shared.index(
        "qboolean PC_Script_Parse(int handle, const char **out) {"
    )
    script_parse_block = ui_shared[
        script_parse_start:ui_shared.index(
            "// display, window, menu, item code", script_parse_start
        )
    ]
    assert "char script[UI_SCRIPT_BUFFER_SIZE];" in script_parse_block
    assert script_parse_block.count("Q_strcat(script, UI_SCRIPT_BUFFER_SIZE,") == 3

    run_script_block = _extract_function_block(
        ui_shared, "void Item_RunScript(itemDef_t *item, const char *s) {"
    )
    assert "char script[UI_SCRIPT_BUFFER_SIZE], *p;" in run_script_block
    assert "Q_strcat(script, sizeof(script), s);" in run_script_block

    command_list_block = ui_shared.split("commandDef_t commandList[] =", 1)[1].split(
        "int scriptCommandCount = sizeof(commandList) / sizeof(commandDef_t);", 1
    )[0]
    assert command_list_block.count('{"') == 23
    for expected in (
        '{"fadein", &Script_FadeIn}',
        '{"fadeout", &Script_FadeOut}',
        '{"show", &Script_Show}',
        '{"hide", &Script_Hide}',
        '{"setcolor", &Script_SetColor}',
        '{"open", &Script_Open}',
        '{"conditionalopen", &Script_ConditionalOpen}',
        '{"close", &Script_Close}',
        '{"toggle", &Script_Toggle}',
        '{"setasset", &Script_SetAsset}',
        '{"setbackground", &Script_SetBackground}',
        '{"setitemcolor", &Script_SetItemColor}',
        '{"setteamcolor", &Script_SetTeamColor}',
        '{"setfocus", &Script_SetFocus}',
        '{"setplayermodel", &Script_SetPlayerModel}',
        '{"setplayerhead", &Script_SetPlayerHead}',
        '{"transition", &Script_Transition}',
        '{"setcvar", &Script_SetCvar}',
        '{"exec", &Script_Exec}',
        '{"play", &Script_Play}',
        '{"playlooped", &Script_playLooped}',
        '{"orbit", &Script_Orbit}',
        '{"activateAdvert", &Script_ActivateAdvert}',
    ):
        assert expected in command_list_block
    for nonretail in (
        "playlaunchercinematic",
        "stoprefresh",
        "closeingame",
        '"leave"',
    ):
        assert nonretail not in command_list_block

    cvar_slot_block = _extract_function_block(
        ui_shared,
        "static qboolean Item_EnableShowViaCvarSlot( const itemDef_t *item, int slot, int flag ) {",
    )
    assert "char script[UI_SCRIPT_BUFFER_SIZE], *p;" in cvar_slot_block
    assert "char buff[1024];" in cvar_slot_block
    assert "DC->getCVarString( item->cvarTest[slot], buff, sizeof( buff ) );" in cvar_slot_block
    assert "Q_strcat( script, sizeof( script ), item->enableCvar[slot] );" in cvar_slot_block

    ui_hlil = UI_HLIL_PART01.read_text(encoding="utf-8", errors="ignore")
    assert "10014d1a  memset(&var_810, 0, 0x800)" in ui_hlil
    assert "sub_10001750(0x800, edx_2)" in ui_hlil
    assert "10016d9b  result, edx = memset(&var_804, 0, 0x800)" in ui_hlil
    assert "10016dc7      sub_10001750(0x800, edx)" in ui_hlil
    assert "1002a014                                                              17 00 00 00" in ui_hlil
    assert "10016e9f      memset(&var_804, 0, 0x800)" in ui_hlil
    assert (
        "10016ee6                  char* edx_2 = "
        "(*(data_106b40d0 + 0x58))(eax_3, &var_c04, 0x400)"
    ) in ui_hlil

    admin_menu = (REPO_ROOT / "src/ui/ingame_admin.menu").read_text(encoding="utf-8")
    assert 'cvarTest2 "cg_gametype"' in admin_menu
    assert 'hideCvar2 { "0" ; "1" ; "2" ; "12" }' in admin_menu

    callvote_menu = (REPO_ROOT / "src/ui/ingame_callvote.menu").read_text(encoding="utf-8")
    assert 'cvarTest2 "ui_gameTypeVotingDisabled"' in callvote_menu
    assert 'showCvar2 { "1" }' in callvote_menu

    main_menu = (REPO_ROOT / "src/ui/main.menu").read_text(encoding="utf-8")
    connect_menu = (REPO_ROOT / "src/ui/connect.menu").read_text(encoding="utf-8")
    assert "backgroundSize 0 0 1920 1080" in main_menu
    assert "backgroundSize 0 0 1920 1080" in connect_menu

    controls_menu = (REPO_ROOT / "src/ui/ingame_controls.menu").read_text(encoding="utf-8")
    advanced_menu = (REPO_ROOT / "src/ui/ingame_options_advanced.menu").read_text(encoding="utf-8")
    assert controls_menu.lower().count("itemdef") > 96
    assert advanced_menu.lower().count("itemdef") > 96


def test_ui_run_menu_script_covers_retail_action_surface_and_wiring() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    ui_hlil = UI_HLIL_PART01.read_text(encoding="utf-8", errors="ignore")
    retail_hlil_block = ui_hlil[
        ui_hlil.index("1000b0e0"):ui_hlil.index("1000d2f0", ui_hlil.index("1000b0e0"))
    ]
    run_menu_script_block = _extract_function_block(
        ui_main, "static void UI_RunMenuScript(char **args) {"
    )
    init_block = _extract_function_block(ui_main, "void _UI_Init( qboolean inGameLoad ) {")
    item_run_script_block = _extract_function_block(
        ui_shared, "void Item_RunScript(itemDef_t *item, const char *s) {"
    )

    retail_actions = {
        "StartServer",
        "resetDefaults",
        "getCDKey",
        "verifyCDKey",
        "loadArenas",
        "saveControls",
        "loadControls",
        "clearError",
        "loadGameInfo",
        "RefreshServers",
        "RefreshFilter",
        "RunSPDemo",
        "LoadDemos",
        "LoadMovies",
        "LoadMods",
        "playMovie",
        "RunMod",
        "RunDemo",
        "Quake3",
        "closeJoin",
        "StopRefresh",
        "UpdateFilter",
        "ServerStatus",
        "FoundPlayerServerStatus",
        "FindPlayer",
        "JoinServer",
        "FoundPlayerJoinServer",
        "Quit",
        "Controls",
        "Leave",
        "clearComError",
        "ServerSort",
        "closeingame",
        "setFullScreen",
        "setWindowed",
        "toggleFullscreen",
        "updateCallvoteMapPreview",
        "voteMap",
        "voteKick",
        "voteGame",
        "addBot",
        "addFavorite",
        "deleteFavorite",
        "createFavorite",
        "orders",
        "voiceOrdersTeam",
        "voiceOrders",
        "update",
        "teamColorDefaults",
        "enemyColorDefaults",
        "enemyModelChanged",
        "teamModelChanged",
        "openWebGameSettings",
        "playerModelChanged",
        "kickPlayer",
        "clientviewProfile",
        "clientFriendInvite",
        "tempbanPlayer",
        "banPlayer",
        "clientmutePlayer",
        "mutePlayer",
        "unmutePlayer",
        "modPlayer",
        "adminPlayer",
        "deopPlayer",
        "putred",
        "putblue",
        "putspec",
    }
    compatibility_actions = {
        "stopRefresh",
        "web_showBrowser",
        "updateSPMenu",
        "resetScores",
        "nextSkirmish",
        "SkirmishStart",
        "voteLeader",
        "glCustom",
        "setPbClStatus",
    }
    source_actions = set(
        re.findall(r'Q_stricmp\(name,\s*"([^"]+)"\)\s*==\s*0', run_menu_script_block)
    )

    assert len(retail_actions) == 68
    assert retail_actions <= source_actions
    assert source_actions - retail_actions - compatibility_actions == set()
    for action in retail_actions:
        assert f'"{action}"' in retail_hlil_block

    for expected in (
        "uiInfo.uiDC.runScript = &UI_RunMenuScript;",
        "uiInfo.uiDC.executeText = &trap_Cmd_ExecuteText;",
        "uiInfo.uiDC.setCVar = trap_Cvar_Set;",
        "uiInfo.uiDC.startLocalSound = &trap_S_StartLocalSound;",
        "uiInfo.uiDC.startBackgroundTrack = &trap_S_StartBackgroundTrack;",
        "uiInfo.uiDC.stopBackgroundTrack = &trap_S_StopBackgroundTrack;",
        "uiInfo.uiDC.setupAdvertCellShader = &UI_SetupAdvertCellShader;",
        "uiInfo.uiDC.refreshAdvertCellShader = &UI_RefreshAdvertCellShader;",
        "uiInfo.uiDC.activateAdvert = &UI_ActivateAdvert;",
    ):
        assert expected in init_block

    assert "DC->runScript(&p);" in item_run_script_block
    assert "DC->executeText(EXEC_APPEND, va(\"%s ; \", val));" in ui_shared


def test_committed_ui_menu_scripts_are_fully_wired_to_retail_handlers() -> None:
    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    command_list_block = ui_shared.split("commandDef_t commandList[] =", 1)[1].split(
        "int scriptCommandCount = sizeof(commandList) / sizeof(commandDef_t);", 1
    )[0]
    shared_actions = {
        action.lower()
        for action in re.findall(r'\{"([^"]+)"', command_list_block)
    }
    run_menu_script_block = _extract_function_block(
        ui_main, "static void UI_RunMenuScript(char **args) {"
    )
    ui_actions = {
        action.lower()
        for action in re.findall(r'Q_stricmp\(name,\s*"([^"]+)"\)\s*==\s*0', run_menu_script_block)
    }

    def strip_menu_comments(text: str) -> str:
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
        return re.sub(r"//.*", "", text)

    def tokenize_script_commands(script: str) -> list[list[str]]:
        commands: list[list[str]] = []
        command: list[str] = []
        index = 0
        while index < len(script):
            char = script[index]
            if char.isspace() or char in "{}":
                index += 1
                continue
            if char == ";":
                if command:
                    commands.append(command)
                    command = []
                index += 1
                continue
            if char == '"':
                end = index + 1
                token: list[str] = []
                while end < len(script) and script[end] != '"':
                    token.append(script[end])
                    end += 1
                command.append("".join(token))
                index = end + 1
                continue

            end = index
            while end < len(script) and not script[end].isspace() and script[end] not in "{};":
                end += 1
            command.append(script[index:end])
            index = end

        if command:
            commands.append(command)
        return commands

    def iter_script_blocks(text: str) -> list[str]:
        blocks: list[str] = []
        for match in re.finditer(
            r"\b(action|onOpen|onClose|mouseEnter|mouseExit|mouseEnterText|mouseExitText)\b\s*\{",
            text,
            flags=re.IGNORECASE,
        ):
            brace_start = text.find("{", match.start())
            depth = 0
            for index in range(brace_start, len(text)):
                if text[index] == "{":
                    depth += 1
                elif text[index] == "}":
                    depth -= 1
                    if depth == 0:
                        blocks.append(text[brace_start + 1:index])
                        break
        return blocks

    shared_used: set[str] = set()
    ui_used: set[str] = set()
    unknown: list[str] = []
    for menu_file in (REPO_ROOT / "src/ui").glob("*.menu"):
        text = strip_menu_comments(menu_file.read_text(encoding="utf-8"))
        for script in iter_script_blocks(text):
            for command in tokenize_script_commands(script):
                verb = command[0].lower()
                if verb == "uiscript":
                    if len(command) < 2:
                        unknown.append(f"{menu_file.name}: missing uiScript action")
                        continue
                    action = command[1].lower()
                    ui_used.add(action)
                    if action not in ui_actions:
                        unknown.append(f"{menu_file.name}: uiScript {command[1]}")
                else:
                    shared_used.add(verb)
                    if verb not in shared_actions:
                        unknown.append(f"{menu_file.name}: {command[0]}")

    assert unknown == []
    assert shared_used == {
        "activateadvert",
        "close",
        "exec",
        "fadein",
        "fadeout",
        "hide",
        "open",
        "play",
        "setcolor",
        "setitemcolor",
        "show",
        "transition",
    }
    assert ui_used == {
        "addbot",
        "adminplayer",
        "banplayer",
        "clearcomerror",
        "clientfriendinvite",
        "clientmuteplayer",
        "clientviewprofile",
        "closeingame",
        "deopplayer",
        "enemycolordefaults",
        "enemymodelchanged",
        "glcustom",
        "kickplayer",
        "leave",
        "loadarenas",
        "loadcontrols",
        "loaddemos",
        "modplayer",
        "muteplayer",
        "putblue",
        "putred",
        "putspec",
        "quit",
        "resetdefaults",
        "rundemo",
        "savecontrols",
        "stoprefresh",
        "teamcolordefaults",
        "teammodelchanged",
        "tempbanplayer",
        "unmuteplayer",
        "update",
        "updatecallvotemappreview",
        "votemap",
    }


def test_ui_retail_server_settings_ownerdraw_restored() -> None:
    bg_public = (REPO_ROOT / "src/code/game/bg_public.h").read_text(encoding="utf-8")
    assert "#define CS_SERVER_SETTINGS_INFO_A\t0x2A9" in bg_public
    assert "#define CS_SERVER_SETTINGS_INFO_B\t0x2AA" in bg_public
    assert "#define CS_WEAPON_RELOAD_TIMES\t\t0x2AB" in bg_public
    assert "#define CUSTOM_SETTING_MACHINEGUN\t\t0x00000002u" in bg_public
    assert "#define CUSTOM_SETTING_ITEM_SPAWNING\t\t0x00400000u" in bg_public
    assert "#define CUSTOM_SETTING_WEAPON_MASK" in bg_public

    g_config_h = (REPO_ROOT / "src/game/g_config.h").read_text(encoding="utf-8")
    assert "uint64_t G_ComputeConfigCustomSettingsMask( void );" in g_config_h

    g_pmove = (REPO_ROOT / "src/code/game/g_pmove.c").read_text(encoding="utf-8")
    assert "qboolean G_PmoveHasAirControlCustomSetting( void ) {" in g_pmove
    assert "qboolean G_PmoveHasPhysicsCustomSetting( void ) {" in g_pmove
    assert "qboolean G_PmoveHasGrappleVelocityCustomSetting( void ) {" in g_pmove
    assert 'return ( g_pmove_velocityGh_cvar.value != 800.0f ) ? qtrue : qfalse;' in g_pmove

    g_config = (REPO_ROOT / "src/game/g_config.c").read_text(encoding="utf-8")
    assert "uint64_t G_ComputeConfigCustomSettingsMask( void ) {" in g_config
    assert "g_weaponConfig.machinegunIronsightsScale" in g_config
    assert "G_PmoveHasGrappleVelocityCustomSetting()" in g_config
    assert "mask |= CUSTOM_SETTING_MACHINEGUN;" in g_config
    assert "mask |= CUSTOM_SETTING_ROCKET_LAUNCHER;" in g_config
    assert "mask |= CUSTOM_SETTING_GRAPPLING_HOOK;" in g_config
    assert "mask |= CUSTOM_SETTING_NAILGUN;" in g_config
    assert "mask |= CUSTOM_SETTING_ITEM_SPAWNING;" in g_config

    g_main = (REPO_ROOT / "src/code/game/g_main.c").read_text(encoding="utf-8")
    assert "static void G_UpdateServerSettingsInfoConfigstrings( qboolean forceBroadcast ) {" in g_main
    assert 'Info_SetValueForKey( payloadA, SERVER_SETTINGS_KEY_ARMOR_TIERED, va( "%i", g_armorTiered.integer ) );' in g_main
    assert 'Info_SetValueForKey( payloadB, SERVER_SETTINGS_KEY_QUAD_DAMAGE_FACTOR, va( "%i", g_quadDamageFactor.integer ) );' in g_main
    assert 'Info_SetValueForKey( payloadB, SERVER_SETTINGS_KEY_GRAVITY, va( "%i", g_gravity.integer ) );' in g_main
    assert "trap_SetConfigstring( CS_SERVER_SETTINGS_INFO_A, payloadA );" in g_main
    assert "trap_SetConfigstring( CS_SERVER_SETTINGS_INFO_B, payloadB );" in g_main
    compute_mask_block = _extract_function_block(
        g_main, "static uint64_t G_ComputeCustomSettingsMask( void ) {"
    )
    assert "mask = G_ComputeConfigCustomSettingsMask();" in compute_mask_block
    assert "CUSTOM_SETTING_AIR_CONTROL" in compute_mask_block
    assert "CUSTOM_SETTING_PHYSICS" in compute_mask_block
    assert "CUSTOM_SETTING_INSTAGIB" in compute_mask_block
    assert "CUSTOM_SETTING_NO_PLAYER_CLIP" in compute_mask_block
    assert "CUSTOM_SETTING_LIGHTNING_DISCHARGE" in compute_mask_block

    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert "static void UI_DrawServerSettings( rectDef_t *rect, float scale, vec4_t color, int textStyle )" in ui_main
    assert 'UI_QLGametypeName( gametype )' in ui_main
    assert 'trap_GetConfigString( CS_SERVER_SETTINGS_INFO_A, serverSettingsA, sizeof( serverSettingsA ) );' in ui_main
    assert 'trap_GetConfigString( CS_SERVER_SETTINGS_INFO_B, serverSettingsB, sizeof( serverSettingsB ) );' in ui_main
    assert 'static qboolean UI_GetServerSettingInt( const char *serverInfo, const char *key, int *valueOut ) {' in ui_main
    assert 'static qboolean UI_GetInfoSettingInt( const char *settingsText, const char *key, int *valueOut ) {' in ui_main
    assert "trap_Cvar_VariableStringBuffer( fallbackCvar, buffer, sizeof( buffer ) );" not in ui_main
    assert 'UI_GetServerSettingInt( serverInfo, "g_gametype", &gametype )' in ui_main
    assert 'UI_GetServerSettingInt( serverInfo, "timelimit", &value )' in ui_main
    assert 'UI_GetServerSettingInt( serverInfo, "fraglimit", &value )' in ui_main
    assert 'UI_GetServerSettingInt( serverInfo, "mercylimit", &value )' in ui_main
    assert 'UI_GetServerSettingInt( serverInfo, "capturelimit", &value )' in ui_main
    assert 'UI_GetServerSettingInt( serverInfo, "roundlimit", &value )' in ui_main
    assert 'UI_GetServerSettingInt( serverInfo, "scorelimit", &value )' in ui_main
    assert '"Tiered Armor"' in ui_main
    assert '"Weapon Switching"' in ui_main
    assert '"Physics"' in ui_main
    assert '"Quad Hog"' in ui_main
    assert '"Regen Health"' in ui_main
    assert '"Drop Health"' in ui_main
    assert '"Vampiric Damage"' in ui_main
    assert '"Item Spawning"' in ui_main
    assert '"Headshots"' in ui_main
    assert '"Rail Jumping"' in ui_main
    assert "static qboolean UI_ServerSettingsWeaponHiddenForGametype( unsigned int weaponBit, int gametype ) {" in ui_main
    assert "case CUSTOM_SETTING_SHOTGUN:" in ui_main
    assert "case CUSTOM_SETTING_GRENADE_LAUNCHER:" in ui_main
    assert "case CUSTOM_SETTING_ROCKET_LAUNCHER:" in ui_main
    assert "case CUSTOM_SETTING_RAILGUN:" in ui_main
    assert "case CUSTOM_SETTING_PLASMAGUN:" in ui_main
    assert '"MODIFIED WEAPONS:"' in ui_main
    assert '"Default Settings"' in ui_main
    assert "case UI_SERVER_SETTINGS:" in ui_main
    assert "UI_DrawServerSettings(&rect, scale, color, textStyle);" in ui_main


def test_game_retail_player_cylinders_configstring_restored() -> None:
    bg_public = (REPO_ROOT / "src/code/game/bg_public.h").read_text(encoding="utf-8")
    g_client = (REPO_ROOT / "src/code/game/g_client.c").read_text(encoding="utf-8")
    g_main = (REPO_ROOT / "src/code/game/g_main.c").read_text(encoding="utf-8")

    assert "#define CS_PLAYER_CYLINDERS\t\t0x2A2" in bg_public
    assert "static char\ts_playerCylindersPayload[32];" in g_main
    assert "void G_SyncPlayerCylinderFlag( gentity_t *ent ) {" in g_main
    assert "static void G_UpdatePlayerCylindersConfigstring( qboolean forceBroadcast );" in g_main
    assert "static void G_UpdatePlayerCylindersConfigstring( qboolean forceBroadcast ) {" in g_main
    assert "G_SyncPlayerCylinderFlag( ent );" in g_client

    for expected in (
        'Com_sprintf( payload, sizeof( payload ), "%i", g_playerCylinders.integer );',
        "!forceBroadcast && !Q_stricmp( payload, s_playerCylindersPayload )",
        "G_SyncPlayerCylinderClientFlags();",
        "trap_SetConfigstring( CS_PLAYER_CYLINDERS, payload );",
        "Q_strncpyz( s_playerCylindersPayload, payload, sizeof( s_playerCylindersPayload ) );",
        "G_UpdatePlayerCylindersConfigstring( qtrue );",
        "G_UpdatePlayerCylindersConfigstring( qfalse );",
    ):
        assert expected in g_main


def test_game_retail_player_appearance_configstring_restored() -> None:
    bg_public = (REPO_ROOT / "src/code/game/bg_public.h").read_text(encoding="utf-8")
    g_main = (REPO_ROOT / "src/code/game/g_main.c").read_text(encoding="utf-8")

    assert "#define CS_PLAYER_APPEARANCE\t\t0x2AC" in bg_public
    assert "static void G_UpdatePlayerAppearanceConfigstring( qboolean forceBroadcast ) {" in g_main

    for expected in (
        'Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERMODEL_OVERRIDE, g_playermodelOverride.string );',
        'Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERHEADMODEL_OVERRIDE, g_playerheadmodelOverride.string );',
        'Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_ALLOW_CUSTOM_HEADMODELS, va( "%i", g_allowCustomHeadmodels.integer ) );',
        'Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERHEAD_SCALE, va( "%g", g_playerheadScale.value ) );',
        'Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERHEAD_SCALE_OFFSET, va( "%g", g_playerheadScaleOffset.value ) );',
        'Info_SetValueForKey( payload, PLAYER_APPEARANCE_KEY_PLAYERMODEL_SCALE, va( "%g", g_playerModelScale.value ) );',
        "trap_SetConfigstring( CS_PLAYER_APPEARANCE, payload );",
        "G_UpdatePlayerAppearanceConfigstring( qtrue );",
        "G_UpdatePlayerAppearanceConfigstring( qfalse );",
    ):
        assert expected in g_main


def test_game_retail_weapon_reload_configstring_restored() -> None:
    bg_public = (REPO_ROOT / "src/code/game/bg_public.h").read_text(encoding="utf-8")
    g_main = (REPO_ROOT / "src/code/game/g_main.c").read_text(encoding="utf-8")

    assert "#define CS_WEAPON_RELOAD_TIMES\t\t0x2AB" in bg_public
    assert "static void G_UpdateWeaponReloadConfigstring( qboolean forceBroadcast ) {" in g_main

    for expected in (
        "g_pmoveSettings.weaponReloadTimes[WP_GAUNTLET],",
        "g_pmoveSettings.weaponReloadTimes[WP_BFG],",
        "g_pmoveSettings.weaponReloadTimes[WP_HEAVY_MACHINEGUN]",
        "trap_SetConfigstring( CS_WEAPON_RELOAD_TIMES, payload );",
        "G_UpdateWeaponReloadConfigstring( qtrue );",
        "G_UpdateWeaponReloadConfigstring( qfalse );",
    ):
        assert expected in g_main


def test_ui_retail_nextmap_ownerdraw_restored() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    nextmap_block = _extract_function_block(ui_main, "static void UI_DrawNextMap")
    assert "#define UI_NEXTMAP_CONFIGSTRING\t0x29A" in ui_main
    assert "static const char *UI_GetNextMapText( void )" not in ui_main
    assert "char nextMapText[MAX_INFO_STRING];" in nextmap_block
    assert "if ( !trap_GetConfigString( UI_NEXTMAP_CONFIGSTRING, nextMapText, sizeof( nextMapText ) ) ) {" in nextmap_block
    assert "CS_ROTATION_TITLES" not in nextmap_block
    assert "Info_ValueForKey" not in nextmap_block
    assert "UI_MapRotationEntryForIndex" not in ui_main
    assert "static void UI_DrawNextMap( rectDef_t *rect, float scale, vec4_t color, int textStyle )" in ui_main
    assert "Text_Paint( rect->x, rect->y, scale, color, nextMapText, 0, 0, textStyle );" in nextmap_block
    assert "case UI_NEXTMAP:" in ui_main
    assert "UI_DrawNextMap(&rect, scale, color, textStyle);" in ui_main


def test_ui_retail_callvote_map_token_path_restored() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")

    helper_block = _extract_function_block(
        ui_main, "static const char *UI_GetCallvoteGametypeToken(int gametype) {"
    )
    for expected in (
        'case GT_FFA:\n\t\t\treturn "ffa";',
        'case GT_TOURNAMENT:\n\t\t\treturn "duel";',
        'case GT_SINGLE_PLAYER:\n\t\t\treturn "race";',
        'case GT_TEAM:\n\t\t\treturn "tdm";',
        'case GT_CLAN_ARENA:\n\t\t\treturn "ca";',
        'case GT_CTF:\n\t\t\treturn "ctf";',
        'case GT_1FCTF:\n\t\t\treturn "oneflag";',
        'case GT_HARVESTER:\n\t\t\treturn "har";',
        'case GT_FREEZE:\n\t\t\treturn "ft";',
        'case GT_DOMINATION:\n\t\t\treturn "dom";',
        'case GT_ATTACK_DEFEND:\n\t\t\treturn "ad";',
        'case GT_RED_ROVER:\n\t\t\treturn "rr";',
        'default:\n\t\t\treturn "";',
    ):
        assert expected in helper_block
    assert "case GT_OBELISK:" not in helper_block

    run_menu_script_block = _extract_function_block(
        ui_main, "static void UI_RunMenuScript(char **args) {"
    )
    assert 'const char *gametypeToken = "";' in run_menu_script_block
    assert "gametypeToken = UI_GetCallvoteGametypeToken(ui_cvGameType.integer);" in run_menu_script_block
    assert 'trap_Cmd_ExecuteText(EXEC_APPEND, va("callvote map %s %s\\n", mapName, gametypeToken));' in run_menu_script_block
    assert "rotation->factoryId" not in run_menu_script_block
    assert 'va("callvote map %s\\n", mapName)' not in run_menu_script_block

    init_block = _extract_function_block(ui_main, "void _UI_Init( qboolean inGameLoad ) {")
    assert 'trap_Cvar_Set("ui_cvGameType", "-1");' in init_block
    assert "trap_Cvar_Update(&ui_cvGameType);" in init_block

    active_menu_block = _extract_function_block(
        ui_main, "void _UI_SetActiveMenu( uiMenuCommand_t menu ) {"
    )
    assert 'trap_Cvar_Set( "ui_cvGameType", "-1" );' in active_menu_block
    assert "trap_Cvar_Update( &ui_cvGameType );" in active_menu_block
    assert 'Menus_ActivateByName("ingame");' in active_menu_block
    assert 'Menus_ActivateByName("ingame_about");' in active_menu_block


def test_ui_retail_admin_scripts_use_player_list_client_numbers() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")
    build_player_list_block = _extract_function_block(ui_main, "static void UI_BuildPlayerList() {")
    admin_client_block = _extract_function_block(
        ui_main, "static qboolean UI_GetSelectedAdminClientNum(const char *scriptName, int *clientNum) {"
    )
    run_menu_script_block = _extract_function_block(
        ui_main, "static void UI_RunMenuScript(char **args) {"
    )

    assert "int playerClientNums[MAX_CLIENTS];" in ui_local
    assert "uiInfo.playerClientNums[uiInfo.playerCount] = n;" in build_player_list_block
    assert "uiInfo.playerIndex;" in admin_client_block
    assert "selected >= uiInfo.playerCount" in admin_client_block
    assert "*clientNum = uiInfo.playerClientNums[selected];" in admin_client_block
    assert 'trap_Cvar_VariableValue("cg_selectedPlayer")' not in admin_client_block
    assert "uiInfo.teamClientNums[selected]" not in admin_client_block

    for command in (
        'va("clientviewprofile %i\\n", clientNum)',
        'va("clientfriendinvite %i\\n", clientNum)',
        'va("clientmute %i\\n", clientNum)',
        'va("callvote clientkick %i\\n", clientNum)',
        'va("tempban %i\\n", clientNum)',
        'va("ban %i\\n", clientNum)',
        'va("mute %i\\n", clientNum)',
        'va("unmute %i\\n", clientNum)',
        'va("addmod %i\\n", clientNum)',
        'va("addadmin %i\\n", clientNum)',
        'va("demote %i\\n", clientNum)',
        'va("put %i r\\n", clientNum)',
        'va("put %i b\\n", clientNum)',
        'va("put %i s\\n", clientNum)',
    ):
        assert command in run_menu_script_block


def test_ui_retail_vote_kick_uses_player_name_suffix_for_spaced_names() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    run_menu_script_block = _extract_function_block(
        ui_main, "static void UI_RunMenuScript(char **args) {"
    )
    vote_kick_block = run_menu_script_block.split('Q_stricmp(name, "voteKick") == 0', 1)[1].split(
        'Q_stricmp(name, "voteGame") == 0', 1
    )[0]

    assert "const char *kickName;" in vote_kick_block
    assert 'kickName = strstr(uiInfo.playerNames[uiInfo.playerIndex], " ");' in vote_kick_block
    assert "if (!kickName) {" in vote_kick_block
    assert "kickName = uiInfo.playerNames[uiInfo.playerIndex];" in vote_kick_block
    assert 'va("callvote kick %s\\n", kickName)' in vote_kick_block
    assert 'va("callvote kick %s\\n",uiInfo.playerNames[uiInfo.playerIndex])' not in vote_kick_block


def test_ui_retail_addbot_uses_bot_catalog_independent_of_gametype() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    draw_bot_block = _extract_function_block(
        ui_main, "static void UI_DrawBotName(rectDef_t *rect, float scale, vec4_t color, int textStyle) {"
    )
    handle_bot_block = _extract_function_block(
        ui_main, "static qboolean UI_BotName_HandleKey(int flags, float *special, int key) {"
    )
    run_menu_script_block = _extract_function_block(
        ui_main, "static void UI_RunMenuScript(char **args) {"
    )
    addbot_block = run_menu_script_block.split('Q_stricmp(name, "addBot") == 0', 1)[1].split(
        'Q_stricmp(name, "addFavorite") == 0', 1
    )[0]

    assert "botCount = UI_GetNumBots();" in draw_bot_block
    assert "if (value >= botCount) {" in draw_bot_block
    assert "if (value < 0 || value >= botCount) {" in draw_bot_block
    assert 'trap_Print(va(S_COLOR_RED "Invalid bot number: %i\\n", value));' in draw_bot_block
    assert "text = UI_GetBotNameByNumber(value);" in draw_bot_block
    assert 'trap_Cvar_VariableValue("g_gametype")' not in draw_bot_block
    assert "uiInfo.characterList[value].name" not in draw_bot_block

    assert "if (value >= UI_GetNumBots() + 2) {" in handle_bot_block
    assert "value = UI_GetNumBots() + 2 - 1;" in handle_bot_block
    assert 'trap_Cvar_VariableValue("g_gametype")' not in handle_bot_block
    assert "uiInfo.characterCount + 2" not in handle_bot_block

    assert 'va("addbot %s %i %s\\n", UI_GetBotNameByNumber(uiInfo.botIndex), uiInfo.skillIndex+1,' in addbot_block
    assert 'trap_Cvar_VariableValue("g_gametype")' not in addbot_block
    assert "uiInfo.characterList[uiInfo.botIndex].name" not in addbot_block


def test_ui_retail_team_order_scripts_route_selected_team_targets() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    run_menu_script_block = _extract_function_block(
        ui_main, "static void UI_RunMenuScript(char **args) {"
    )
    orders_block = _extract_function_block(ui_main, "static void UI_RunOrdersScript(const char *command) {")
    voice_team_block = _extract_function_block(
        ui_main, "static void UI_RunVoiceOrdersTeamScript(const char *command) {"
    )
    voice_block = _extract_function_block(ui_main, "static void UI_RunVoiceOrdersScript(const char *command) {")

    for command_name, helper_name in (
        ("orders", "UI_RunOrdersScript(name2);"),
        ("voiceOrdersTeam", "UI_RunVoiceOrdersTeamScript(name2);"),
        ("voiceOrders", "UI_RunVoiceOrdersScript(name2);"),
    ):
        script_case = run_menu_script_block.split(f'Q_stricmp(name, "{command_name}") == 0', 1)[1].split(
            "} else if", 1
        )[0]
        assert "if (String_Parse(args, &name2)) {" in script_case
        assert helper_name in script_case

    assert 'selected = trap_Cvar_VariableValue("cg_selectedPlayer");' in orders_block
    assert "selected >= 0 && selected < uiInfo.myTeamCount" in orders_block
    assert "va(command, uiInfo.teamClientNums[selected])" in orders_block
    assert "for (i = 0; i < uiInfo.myTeamCount; i++) {" in orders_block
    assert 'Q_stricmp(uiInfo.teamNames[i], UI_Cvar_VariableString("name"))' in orders_block
    assert "va(command, uiInfo.teamNames[i])" in orders_block
    assert 'trap_Cmd_ExecuteText(EXEC_APPEND, "\\n");' in orders_block
    assert "UI_CloseInGameMenu();" in orders_block

    assert 'selected = trap_Cvar_VariableValue("cg_selectedPlayer");' in voice_team_block
    assert "selected == uiInfo.myTeamCount" in voice_team_block
    assert "trap_Cmd_ExecuteText(EXEC_APPEND, command);" in voice_team_block
    assert 'trap_Cmd_ExecuteText(EXEC_APPEND, "\\n");' in voice_team_block
    assert "UI_CloseInGameMenu();" in voice_team_block

    assert 'selected = trap_Cvar_VariableValue("cg_selectedPlayer");' in voice_block
    assert "selected >= 0 && selected < uiInfo.myTeamCount" in voice_block
    assert "va(command, uiInfo.teamClientNums[selected])" in voice_block
    assert 'trap_Cmd_ExecuteText(EXEC_APPEND, "\\n");' in voice_block
    assert "UI_CloseInGameMenu();" in voice_block


def test_ui_retail_model_update_scripts_restore_alias_and_player_refresh_flag() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    run_menu_script_block = _extract_function_block(
        ui_main, "static void UI_RunMenuScript(char **args) {"
    )
    team_model_block = run_menu_script_block.split(
        'Q_stricmp(name, "teamModelChanged") == 0', 1
    )[1].split('Q_stricmp(name, "teamColorDefaults") == 0', 1)[0]
    enemy_model_block = run_menu_script_block.split(
        'Q_stricmp(name, "enemyModelChanged") == 0', 1
    )[1].split('Q_stricmp(name, "enemyColorDefaults") == 0', 1)[0]
    player_model_block = run_menu_script_block.split(
        'Q_stricmp(name, "playerModelChanged") == 0', 1
    )[1].split('Q_stricmp(name, "ServerSort") == 0', 1)[0]

    assert 'Q_stricmp(name, "openWebGameSettings") == 0' in team_model_block
    assert "UI_UpdateForceModelSettings(qtrue);" in team_model_block
    assert "UI_UpdateForceModelSettings(qfalse);" in enemy_model_block
    assert "updateModel = qtrue;" in player_model_block


def test_ui_retail_fullscreen_menu_scripts_match_native_command_surface() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    run_menu_script_block = _extract_function_block(
        ui_main, "static void UI_RunMenuScript(char **args) {"
    )
    fullscreen_block = run_menu_script_block.split(
        'Q_stricmp(name, "setFullScreen") == 0', 1
    )[1].split('Q_stricmp(name, "clientviewProfile") == 0', 1)[0]

    for expected in (
        'Q_stricmp(name, "setWindowed") == 0',
        'Q_stricmp(name, "toggleFullscreen") == 0',
        'trap_Cvar_Set( "r_fullScreen", "1" );',
        'trap_Cvar_Set( "r_fullScreen", "0" );',
        'fullscreen = ( trap_Cvar_VariableValue( "r_fullScreen" ) != 0.0f ) ? qtrue : qfalse;',
        'trap_Cvar_Set( "r_fullScreen", fullscreen ? "0" : "1" );',
    ):
        assert expected in fullscreen_block

    assert fullscreen_block.count('trap_Cmd_ExecuteText( EXEC_APPEND, "vid_restart fast\\n" );') == 3


def test_ui_legacy_fullscreen_controls_use_fast_vid_restart_bridge() -> None:
    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    basic_menu = (REPO_ROOT / "src/ui/ingame_options_basic.menu").read_text(encoding="utf-8")
    advanced_menu = (REPO_ROOT / "src/ui/ingame_options_advanced.menu").read_text(encoding="utf-8")

    script_exec_block = _extract_function_block(ui_shared, "void Script_Exec(itemDef_t *item, char **args) {")
    yesno_block = _extract_function_block(ui_shared, "qboolean Item_YesNo_HandleKey(itemDef_t *item, int key) {")

    assert "static qboolean Item_UsesFullscreenCvar( const itemDef_t *item ) {" in ui_shared
    assert "static qboolean UI_CommandIsVidRestart( const char *command ) {" in ui_shared
    assert 'return ( item && item->cvar && !Q_stricmp( item->cvar, "r_fullscreen" ) ) ? qtrue : qfalse;' in ui_shared
    assert 'return ( command && !Q_stricmp( command, "vid_restart" ) ) ? qtrue : qfalse;' in ui_shared
    assert "if ( Item_UsesFullscreenCvar( item ) && UI_CommandIsVidRestart( val ) ) {" in script_exec_block
    assert 'DC->executeText( EXEC_APPEND, "vid_restart fast\\n" );' in script_exec_block
    assert "if ( Item_UsesFullscreenCvar( item ) && ( !item->action || !item->action[0] ) ) {" in yesno_block
    assert 'DC->executeText( EXEC_APPEND, "vid_restart fast\\n" );' in yesno_block

    assert 'cvar "r_fullscreen"' in basic_menu
    assert 'action { uiScript glCustom ;  exec "vid_restart" ; open ingame_options }' in basic_menu
    assert 'cvar "r_fullscreen"' in advanced_menu


def test_ui_retail_callvote_map_feeder_uses_active_map_slab() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")

    assert "static int UI_CVMapCountByGameType(void);" in ui_main
    assert "static void UI_SelectCallvoteMap(int index);" in ui_main
    assert "applyCallvotePreset" not in ui_main
    assert "ui_cvPresetRotation" not in ui_main
    assert "ui_cvPresetGameType" not in ui_main
    assert "ui_cvPresetActive" not in ui_main

    feeder_count_block = _extract_function_block(ui_main, "static int UI_FeederCount(float feederID) {")
    assert "if (feederID == FEEDER_CVMAPS) {" in feeder_count_block
    assert "return UI_CVMapCountByGameType();" in feeder_count_block
    assert "FEEDER_MAP_ROTATIONS" not in feeder_count_block

    cv_count_block = _extract_function_block(ui_main, "static int UI_CVMapCountByGameType(void) {")
    for expected in (
        "gametype = UI_GetFilteredCallvoteGametype();",
        "uiInfo.mapList[i].active = qfalse;",
        "for (i = 0; i < uiInfo.mapRotationCount; i++) {",
        "mapIndex = uiInfo.mapRotations[i].mapIndex;",
        "if (uiInfo.mapList[mapIndex].active) {",
        "uiInfo.mapList[mapIndex].active = qtrue;",
    ):
        assert expected in cv_count_block

    select_callvote_map_block = _extract_function_block(
        ui_main, "static void UI_SelectCallvoteMap(int index) {"
    )
    assert "available = UI_CVMapCountByGameType();" in select_callvote_map_block
    assert "UI_SelectedMap(index, &actual);" in select_callvote_map_block
    assert 'trap_Cvar_Set("ui_mapIndex", va("%d", index));' in select_callvote_map_block
    assert "UI_SetCurrentNetMap(actual);" in select_callvote_map_block

    run_menu_script_block = _extract_function_block(
        ui_main, "static void UI_RunMenuScript(char **args) {"
    )
    assert 'Q_stricmp(name, "updateCallvoteMapPreview") == 0' in run_menu_script_block
    assert "UI_FeederSelection(FEEDER_CVMAPS, ui_mapIndex.integer, NULL);" in run_menu_script_block
    assert "UI_HandleCallvoteMapPreviewScript" not in ui_main
    assert "applyCallvotePreset" not in run_menu_script_block

    feeder_text_block = _extract_function_block(
        ui_main, "static const char *UI_FeederItemText(float feederID, int index, int column, qhandle_t *handle) {"
    )
    assert "UI_CVMapCountByGameType();" in feeder_text_block
    assert "return UI_SelectedMap(index, &actual);" in feeder_text_block
    assert "FEEDER_MAP_ROTATIONS" not in feeder_text_block

    feeder_image_block = _extract_function_block(
        ui_main, "static qhandle_t UI_FeederItemImage(float feederID, int index) {"
    )
    assert "UI_CVMapCountByGameType();" in feeder_image_block
    assert "UI_SelectedMap(index, &actual);" in feeder_image_block
    assert "uiInfo.mapList[actual].levelShot" in feeder_image_block

    feeder_selection_block = _extract_function_block(
        ui_main, "static void UI_FeederSelection(float feederID, int index, const char *cvar) {"
    )
    assert "UI_SelectCallvoteMap(index);" in feeder_selection_block
    assert "FEEDER_MAP_ROTATIONS" not in feeder_selection_block

    assert "UI_CountVisibleCallvoteRotations" not in ui_main
    assert "UI_GetCallvoteRotationIndexFromDisplayRow" not in ui_main
    assert "UI_GetCallvoteDisplayRowForRotation" not in ui_main
    assert "UI_GetCallvoteRotationEntryForDisplay" not in ui_main


def test_ui_retail_feeder_matrix_matches_menu_consumers_and_callback_ownership() -> None:
    menudef = (REPO_ROOT / "src/ui/menudef.h").read_text(encoding="utf-8")
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    ui_shared_h = (REPO_ROOT / "src/code/ui/ui_shared.h").read_text(encoding="utf-8")
    defines = _extract_numeric_defines(menudef, "FEEDER_")

    expected_ids = {
        "FEEDER_HEADS": 0x00,
        "FEEDER_MAPS": 0x01,
        "FEEDER_SERVERS": 0x02,
        "FEEDER_CLANS": 0x03,
        "FEEDER_ALLMAPS": 0x04,
        "FEEDER_REDTEAM_LIST": 0x05,
        "FEEDER_BLUETEAM_LIST": 0x06,
        "FEEDER_PLAYER_LIST": 0x07,
        "FEEDER_TEAM_LIST": 0x08,
        "FEEDER_MODS": 0x09,
        "FEEDER_DEMOS": 0x0A,
        "FEEDER_SCOREBOARD": 0x0B,
        "FEEDER_Q3HEADS": 0x0C,
        "FEEDER_SERVERSTATUS": 0x0D,
        "FEEDER_FINDPLAYER": 0x0E,
        "FEEDER_CINEMATICS": 0x0F,
        "FEEDER_ENDSCOREBOARD": 0x10,
        "FEEDER_REDTEAM_STATS": 0x11,
        "FEEDER_BLUETEAM_STATS": 0x12,
        "FEEDER_CVMAPS": 0x13,
    }
    assert {name: defines[name] for name in expected_ids} == expected_ids

    menu_feeders: set[str] = set()
    menu_text_by_name: dict[str, str] = {}
    for menu_path in (REPO_ROOT / "src/ui").glob("*.menu"):
        menu_text = menu_path.read_text(encoding="utf-8")
        menu_text_by_name[menu_path.name] = menu_text
        menu_feeders.update(
            re.findall(r"\bfeeder\s+(FEEDER_[A-Z0-9_]+)\b", menu_text)
        )

    ui_menu_feeders = {
        "FEEDER_ALLMAPS",
        "FEEDER_CVMAPS",
        "FEEDER_DEMOS",
        "FEEDER_HEADS",
        "FEEDER_PLAYER_LIST",
        "FEEDER_Q3HEADS",
    }
    cgame_menu_feeders = {
        "FEEDER_BLUETEAM_LIST",
        "FEEDER_BLUETEAM_STATS",
        "FEEDER_REDTEAM_LIST",
        "FEEDER_REDTEAM_STATS",
        "FEEDER_SCOREBOARD",
    }
    assert menu_feeders == ui_menu_feeders | cgame_menu_feeders
    assert "FEEDER_CLANS" not in menu_feeders
    assert "FEEDER_COUNTRIES" not in menu_feeders
    assert "FEEDER_ENDSCOREBOARD" not in menu_feeders

    non_team_end_scoreboards = {
        "end_scoreboard_ffa.menu",
        "end_scoreboard_race.menu",
        "end_scoreboard_rr.menu",
        "endscorenoteam.menu",
    }
    for menu_name in non_team_end_scoreboards:
        menu_text = menu_text_by_name[menu_name]
        assert "feeder FEEDER_SCOREBOARD" in menu_text
        assert "FEEDER_ENDSCOREBOARD" not in menu_text

    rich_team_end_scoreboards = {
        "end_scoreboard_1fctf.menu",
        "end_scoreboard_ad.menu",
        "end_scoreboard_ca.menu",
        "end_scoreboard_ctf.menu",
        "end_scoreboard_dom.menu",
        "end_scoreboard_ft.menu",
        "end_scoreboard_har.menu",
        "end_scoreboard_tdm.menu",
    }
    for menu_name in rich_team_end_scoreboards:
        menu_text = menu_text_by_name[menu_name]
        assert "feeder FEEDER_REDTEAM_LIST" in menu_text
        assert "feeder FEEDER_BLUETEAM_LIST" in menu_text
        assert "feeder FEEDER_REDTEAM_STATS" in menu_text
        assert "feeder FEEDER_BLUETEAM_STATS" in menu_text
        assert "FEEDER_ENDSCOREBOARD" not in menu_text

    legacy_team_end_scoreboard = menu_text_by_name["endscoreteam.menu"]
    assert "feeder FEEDER_REDTEAM_LIST" in legacy_team_end_scoreboard
    assert "feeder FEEDER_BLUETEAM_LIST" in legacy_team_end_scoreboard
    assert "FEEDER_ENDSCOREBOARD" not in legacy_team_end_scoreboard

    feeder_count_block = _extract_function_block(ui_main, "static int UI_FeederCount(float feederID) {")
    feeder_text_block = _extract_function_block(
        ui_main, "static const char *UI_FeederItemText(float feederID, int index, int column, qhandle_t *handle) {"
    )
    feeder_image_block = _extract_function_block(
        ui_main, "static qhandle_t UI_FeederItemImage(float feederID, int index) {"
    )
    feeder_selection_block = _extract_function_block(
        ui_main, "static void UI_FeederSelection(float feederID, int index, const char *cvar) {"
    )

    ui_count_and_text_feeders = {
        "FEEDER_ALLMAPS",
        "FEEDER_CINEMATICS",
        "FEEDER_CVMAPS",
        "FEEDER_DEMOS",
        "FEEDER_FINDPLAYER",
        "FEEDER_HEADS",
        "FEEDER_MAPS",
        "FEEDER_MODS",
        "FEEDER_PLAYER_LIST",
        "FEEDER_Q3HEADS",
        "FEEDER_SERVERS",
        "FEEDER_SERVERSTATUS",
        "FEEDER_TEAM_LIST",
    }
    for feeder in ui_count_and_text_feeders:
        assert feeder in feeder_count_block
        assert feeder in feeder_text_block

    for feeder in (
        "FEEDER_ALLMAPS",
        "FEEDER_CVMAPS",
        "FEEDER_HEADS",
        "FEEDER_MAPS",
        "FEEDER_Q3HEADS",
    ):
        assert feeder in feeder_image_block

    for feeder in ui_count_and_text_feeders:
        assert feeder in feeder_selection_block

    assert "UI_CountPlayerModelEntries( qfalse )" in feeder_count_block
    assert "UI_CountPlayerModelEntries( qtrue )" in feeder_count_block
    assert "UI_PlayerModelIndexForFeederRow( index, feederID == FEEDER_Q3HEADS )" in feeder_text_block
    assert "UI_PlayerModelIndexForFeederRow( index, feederID == FEEDER_Q3HEADS )" in feeder_image_block
    assert "UI_PlayerModelIndexForFeederRow( index, feederID == FEEDER_Q3HEADS )" in feeder_selection_block
    assert 'trap_Cvar_Set( cvar, modelName );' in feeder_selection_block
    assert 'trap_Cvar_Set( "model", modelName );' in feeder_selection_block
    assert 'trap_Cvar_Set( "headmodel", modelName );' in feeder_selection_block
    assert '"team_model"' not in feeder_selection_block
    assert '"team_headmodel"' not in feeder_selection_block
    assert "SORT_PUNKBUSTER" not in feeder_text_block
    assert "void (*feederSelection)(float feederID, int index, const char *cvar);" in ui_shared_h
    assert "DC->feederSelection(item->special, item->cursorPos, item->cvar);" in ui_shared
    assert "DC->feederSelection(menu->items[i]->special, menu->items[i]->cursorPos, menu->items[i]->cvar);" in ui_shared

    cgame_owned_feeders = {
        "FEEDER_BLUETEAM_LIST",
        "FEEDER_BLUETEAM_STATS",
        "FEEDER_ENDSCOREBOARD",
        "FEEDER_REDTEAM_LIST",
        "FEEDER_REDTEAM_STATS",
        "FEEDER_SCOREBOARD",
    }
    for feeder in cgame_owned_feeders | {"FEEDER_CLANS"}:
        assert feeder not in feeder_count_block
        assert feeder not in feeder_text_block
        assert feeder not in feeder_image_block
        assert feeder not in feeder_selection_block


def test_ui_retail_feeder_leaf_callbacks_match_remaining_ui_owned_ids() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    feeder_count_block = _extract_function_block(ui_main, "static int UI_FeederCount(float feederID) {")
    feeder_text_block = _extract_function_block(
        ui_main, "static const char *UI_FeederItemText(float feederID, int index, int column, qhandle_t *handle) {"
    )
    feeder_selection_block = _extract_function_block(
        ui_main, "static void UI_FeederSelection(float feederID, int index, const char *cvar) {"
    )

    for expected in (
        "return uiInfo.serverStatus.numDisplayServers;",
        "return uiInfo.serverStatusInfo.numLines;",
        "return uiInfo.numFoundPlayerServers;",
        "return uiInfo.playerCount;",
        "return uiInfo.myTeamCount;",
        "return uiInfo.modCount;",
        "return uiInfo.movieCount;",
        "return uiInfo.demoCount;",
        "uiInfo.playerRefresh = uiInfo.uiDC.realTime + 3000;",
        "UI_BuildPlayerList();",
    ):
        assert expected in feeder_count_block

    for expected in (
        "SORT_HOST",
        "SORT_MAP",
        "SORT_CLIENTS",
        "SORT_GAME",
        "SORT_PING",
        'return "...";',
        "column >= 0 && column < 4",
        "return uiInfo.foundPlayerServerNames[index];",
        "return uiInfo.playerNames[index];",
        "return uiInfo.teamNames[index];",
        "uiInfo.modList[index].modDescr",
        "return uiInfo.movieList[index];",
        "return uiInfo.demoList[index];",
    ):
        assert expected in feeder_text_block

    for expected in (
        "trap_LAN_GetServerInfo(ui_netSource.integer, uiInfo.serverStatus.displayServers[index], info, MAX_STRING_CHARS);",
        "uiInfo.serverStatus.currentServerPreview = trap_R_RegisterShaderNoMip",
        "uiInfo.currentFoundPlayerServer = index;",
        "Q_strncpyz(uiInfo.serverStatusAddress, uiInfo.foundPlayerServerAddresses[uiInfo.currentFoundPlayerServer], sizeof(uiInfo.serverStatusAddress));",
        "Menu_SetFeederSelection(NULL, FEEDER_SERVERSTATUS, 0, NULL);",
        "UI_BuildServerStatus(qtrue);",
        "uiInfo.playerIndex = index;",
        "uiInfo.teamIndex = index;",
        "uiInfo.modIndex = index;",
        "uiInfo.movieIndex = index;",
        "uiInfo.previewMovie = -1;",
        "uiInfo.demoIndex = index;",
    ):
        assert expected in feeder_selection_block


def test_ui_retail_clan_feeder_scaffolding_is_removed() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")

    for removed in (
        "static void UI_ResetClanList(void);",
        "static void UI_LoadClanRoster(void);",
        "UI_ResetClanList",
        "UI_LoadClanRoster",
        "ui_clanIndex",
        "ui_clanName",
        "No clans available",
    ):
        assert removed not in ui_main

    feeder_count_block = _extract_function_block(ui_main, "static int UI_FeederCount(float feederID) {")
    feeder_text_block = _extract_function_block(
        ui_main, "static const char *UI_FeederItemText(float feederID, int index, int column, qhandle_t *handle) {"
    )
    feeder_image_block = _extract_function_block(
        ui_main, "static qhandle_t UI_FeederItemImage(float feederID, int index) {"
    )
    feeder_selection_block = _extract_function_block(
        ui_main, "static void UI_FeederSelection(float feederID, int index, const char *cvar) {"
    )

    assert "FEEDER_CLANS" not in feeder_count_block
    assert "FEEDER_CLANS" not in feeder_text_block
    assert "FEEDER_CLANS" not in feeder_image_block
    assert "FEEDER_CLANS" not in feeder_selection_block

    for removed in (
        "#define MAX_CLANS 256",
        "} uiClanInfo_t;",
        "int clanCount;",
        "uiClanInfo_t clanList[MAX_CLANS];",
        "int currentClan;",
        "qboolean clanListLoaded;",
        "extern vmCvar_t\tui_clanIndex;",
        "extern vmCvar_t\tui_clanName;",
    ):
        assert removed not in ui_local

    assert "`FEEDER_CLANS` remains only as a shared `menudef.h` constant" in ui_local


def test_ui_retail_matchsummary_cache_scaffolding_is_removed() -> None:
    ui_atoms = (REPO_ROOT / "src/code/ui/ui_atoms.c").read_text(encoding="utf-8")
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")

    for removed in (
        "#define FEEDER_MATCHSUMMARY_END",
        "#define FEEDER_MATCHSUMMARY_RED",
        "#define FEEDER_MATCHSUMMARY_BLUE",
        "#define MAX_MATCH_SUMMARY_PLAYERS",
        "} uiMatchPlayerInfo_t;",
        "} uiMatchPlayerList_t;",
        "} uiMatchSummaryCache_t;",
        "uiMatchSummaryCache_t matchSummary;",
        "int currentMatchSummaryEnd;",
        "int currentMatchSummaryRed;",
        "int currentMatchSummaryBlue;",
        "void UI_ResetMatchSummaryCache( void );",
        "void UI_MatchSummaryParseFromPostgame( void );",
    ):
        assert removed not in ui_local

    for removed in (
        "UI_ClearMatchSummaryList",
        "UI_MatchSummaryParseFromPostgame",
        "UI_MatchSummaryListForFeeder",
        "UI_MatchSummaryTeamString",
        "uiInfo.matchSummary",
        "currentMatchSummaryEnd",
        "currentMatchSummaryRed",
        "currentMatchSummaryBlue",
        "FEEDER_MATCHSUMMARY_END",
        "FEEDER_MATCHSUMMARY_RED",
        "FEEDER_MATCHSUMMARY_BLUE",
    ):
        assert removed not in ui_main

    assert "UI_MatchSummaryParseFromPostgame" not in ui_atoms
