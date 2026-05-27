from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from scripts.ui.retail_ui_corpus import inventory_missing_reason
from scripts.ui.retail_ui_corpus import DEFAULT_BASEQ3_ROOT

REPO_ROOT = Path(__file__).resolve().parent.parent


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


def test_ui_bundle_manifest_stages_runtime_icon_roots_without_baseq3_prefixes() -> None:
    manifest = json.loads((REPO_ROOT / "tools/packaging/ui_bundle_manifest.json").read_text(encoding="utf-8"))
    files = manifest["files"]
    by_source_dir = {
        entry["source_dir"]: entry
        for entry in files
        if "source_dir" in entry
    }

    assert by_source_dir["assets/quakelive/baseq3/icons"]["destination"] == "icons"
    assert by_source_dir["assets/quakelive/baseq3/menu/icons"]["destination"] == "menu/icons"
    assert by_source_dir["assets/quakelive/baseq3/levelshots"]["destination"] == "levelshots"

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


def test_ui_bundle_manifest_stages_runtime_menudef_header() -> None:
    manifest = json.loads((REPO_ROOT / "tools/packaging/ui_bundle_manifest.json").read_text(encoding="utf-8"))
    files = manifest["files"]

    header_entries = [
        entry
        for entry in files
        if entry.get("source") == "src/ui/menudef.h"
    ]
    assert len(header_entries) == 1
    assert header_entries[0]["destination"] == "ui/menudef.h"

    audit = manifest["audit"]
    assert "ui/menudef.h" in audit["required_paths"]

    runtime_probe = (REPO_ROOT / "tools/client/run_client_runtime_probe.ps1").read_text(encoding="utf-8")
    assert "( Join-Path $baseq3Root 'ui\\\\menudef.h' )" in runtime_probe


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

    assert 'UI_SyncRetailSliderColorCvar( &ui_teamHeadColor, "cg_teamHeadColor" );' in ui_main
    assert 'UI_SyncRetailSliderColorCvar( &ui_enemyHeadColor, "cg_enemyHeadColor" );' in ui_main
    assert "static int UI_CountPlayerModelEntries( qboolean skipAliasSkins )" in ui_main
    assert "UI_AddPlayerModelEntry( dirptr, skinname + 5, iconShaderName );" in ui_main
    assert "if ( UI_PlayerModelSkinIsAlias( ui_playerModelEntries[i].skinName ) ) {" in ui_main


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
    retail_join = (DEFAULT_BASEQ3_ROOT / "ui" / "ingame_join.menu").read_text(encoding="utf-8")

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

    assert "#define\tNUM_CROSSHAIRS\t\t\t30" in ui_shared_h
    assert "#define UI_CROSSHAIR_COLOR_COUNT\t26" in ui_main
    assert "static void UI_DrawCrosshairColor( rectDef_t *rect )" in ui_main
    assert 'trap_Cvar_VariableValue( "cg_crosshairColor" )' in ui_main
    assert "case UI_CROSSHAIR_COLOR:" in ui_main
    assert "return UI_CrosshairColor_HandleKey(flags, special, key);" in ui_main
    assert "case UI_VOTESTRING:" in ui_main
    assert "UI_DrawVoteString(&rect, scale, color, textStyle);" in ui_main
    assert 'UI_Cvar_VariableString("ui_votestring")' in ui_main
    assert "for ( n = 1; n < NUM_CROSSHAIRS; n++ ) {" in asset_cache_block
    assert 'trap_R_RegisterShaderNoMip( va( "gfx/2d/crosshair%d", n ) );' in asset_cache_block
    assert "crosshair%c" not in asset_cache_block


def test_ui_retail_starting_weapons_ownerdraw_restored() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    token_block = _extract_function_block(ui_main, "static int UI_StartingWeaponIndexFromToken")
    assert "#define UI_STARTING_WEAPON_ICON_COUNT\t14" in ui_main
    assert "static int UI_StartingWeaponIndexFromToken( const char *value )" in ui_main
    assert "COM_ParseExt( &cursor, qtrue )" in token_block
    assert "uiStartingWeaponIcons[i].token" in token_block
    assert 'trap_GetConfigString( CS_LOADOUT_MASK, loadoutMaskText, sizeof( loadoutMaskText ) );' in ui_main
    assert 'UI_Cvar_VariableString( "cg_weaponPrimaryQueued" )' in ui_main
    assert "case UI_STARTING_WEAPONS:" in ui_main
    assert "UI_DrawStartingWeapons(&rect, scale, color, textStyle);" in ui_main
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
    assert "static void Script_ActivateAdvert(itemDef_t *item, char **args)" in ui_shared
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
        "qboolean MenuParse_ownerdrawFlag2( itemDef_t *item, int handle ) {",
        '{"ownerdrawFlag2", ItemParse_ownerdrawFlag2, NULL},',
        '{"altrowcolor", ItemParse_altrowcolor, NULL},',
        '{"elementcolor", ItemParse_elementcolor, NULL},',
        '{"selectedcolor", ItemParse_selectedcolor, NULL},',
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
        "if ( i == item->cursorPos ) {\n\t\t\t\t\tDC->fillRect( x + 2, y + 2, item->window.rect.w - SCROLLBAR_SIZE - 4, listPtr->elementHeight, item->window.outlineColor );",
        "if ( listPtr->altRowColorSet && ( ( (int)i - listPtr->startPos ) & 1 ) ) {",
        "Item_DrawText(item, x + 4, y + listPtr->elementHeight, textColor, text, 0, 0);",
    ):
        assert expected in ui_shared


def test_ui_native_import_table_matches_recovered_retail_slots() -> None:
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")
    ui_public = (REPO_ROOT / "src/code/ui/ui_public.h").read_text(encoding="utf-8")
    ql_ui_imports = (REPO_ROOT / "src/code/client/ql_ui_imports.inc").read_text(encoding="utf-8")

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
    ):
        assert expected in ql_ui_imports

    assert "ql_ui_imports[85] = (ql_import_f)QL_UI_trap_S_StopBackgroundTrack;" not in cl_ui
    assert "UI_QL_IMPORT_MEMORY_REMAINING = 101" not in cl_ui
    assert "UI_QL_IMPORT_R_REMAP_SHADER = 104" not in cl_ui


def test_ui_native_host_text_wrappers_preserve_color_force_and_packed_measure_contract() -> None:
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")
    draw_block = _extract_function_block(
        cl_ui,
        "static void QDECL QL_UI_trap_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, int forceColor ) {",
    )
    measure_block = _extract_function_block(
        cl_ui,
        "static unsigned long long QDECL QL_UI_trap_MeasureText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outLeft ) {",
    )

    assert "RE_DrawScaledText( x, y, text, fontHandle, scale, maxX, outMaxX, forceColor != qfalse ? qtrue : qfalse, ql_ui_currentColor );" in draw_block
    assert "float width;" in measure_block
    assert "float height;" in measure_block
    assert "RE_MeasureScaledText( text, end, fontHandle, scale, maxX, &width, &height, outLeft );" in measure_block
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
        "void trap_QL_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor ) {",
        "unsigned long long trap_QL_MeasureText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outLeft ) {",
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
        "void trap_QL_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor ) {",
    )
    measure_block = _extract_function_block(
        ui_syscalls,
        "unsigned long long trap_QL_MeasureText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outLeft ) {",
    )

    for expected in (
        "ql_import_f import = UI_GetNativeImportFunction( UI_QL_IMPORT_DRAW_SCALED_TEXT );",
        "if ( !import ) {",
        "return;",
        "((void (QDECL *)( int, int, const char *, int, float, int, float *, int ))import)( x, y, text, fontHandle, scale, maxX, outMaxX, forceColor ? qtrue : qfalse );",
    ):
        assert expected in draw_block

    for expected in (
        "ql_import_f import = UI_GetNativeImportFunction( UI_QL_IMPORT_MEASURE_TEXT );",
        "if ( !import ) {",
        "return 0;",
        "return ((unsigned long long (QDECL *)( const char *, const char *, int, float, int, float * ))import)( text, end, fontHandle, scale, maxX, outLeft );",
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

    assert '{ &ui_smallFont, "ui_smallFont", "0.25", CVAR_ARCHIVE}' in ui_main
    assert '{ &ui_bigFont, "ui_bigFont", "0.4", CVAR_ARCHIVE}' in ui_main

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
        "fontHandle = UI_SelectTextFontHandle( scale, ITEM_FONT_INHERIT );",
        "trap_QL_DrawScaledText(",
        "scale * QL_FONT_HOST_POINT_SIZE * uiInfo.uiDC.yscale,",
        "(int)screenMaxX,",
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
    g_main = (REPO_ROOT / "src/code/game/g_main.c").read_text(encoding="utf-8")

    assert "#define CS_PLAYER_CYLINDERS\t\t0x2A2" in bg_public
    assert "static char\ts_playerCylindersPayload[32];" in g_main
    assert "static void G_UpdatePlayerCylindersConfigstring( qboolean forceBroadcast );" in g_main
    assert "static void G_UpdatePlayerCylindersConfigstring( qboolean forceBroadcast ) {" in g_main

    for expected in (
        'Com_sprintf( payload, sizeof( payload ), "%i", g_playerCylinders.integer );',
        "!forceBroadcast && !Q_stricmp( payload, s_playerCylindersPayload )",
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
    assert "#define UI_NEXTMAP_CONFIGSTRING\t0x29A" in ui_main
    assert "static const char *UI_GetNextMapText( void )" in ui_main
    assert "trap_GetConfigString( UI_NEXTMAP_CONFIGSTRING, nextMapText, sizeof( nextMapText ) );" in ui_main
    assert "trap_GetConfigString( CS_ROTATION_TITLES, rotationTitles, sizeof( rotationTitles ) );" in ui_main
    assert 'Info_ValueForKey( rotationTitles, "title_0" )' in ui_main
    assert 'Info_ValueForKey( rotationTitles, "map_0" )' in ui_main
    assert "UI_MapRotationEntryForIndex" not in ui_main
    assert "static void UI_DrawNextMap( rectDef_t *rect, float scale, vec4_t color, int textStyle )" in ui_main
    assert "Text_Paint( rect->x, rect->y, scale, color, nextMapText, 0, 0, textStyle );" in ui_main
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

    assert "text = UI_GetBotNameByNumber(value);" in draw_bot_block
    assert "if (value >= UI_GetNumBots()) {" in draw_bot_block
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
