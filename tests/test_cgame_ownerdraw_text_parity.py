"""Guard retail-backed cgame ownerdraw text against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_DRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
UI_SHARED = REPO_ROOT / "src" / "code" / "ui" / "ui_shared.c"
MENUDEF_H = REPO_ROOT / "src" / "ui" / "menudef.h"
INTRO_MENU = REPO_ROOT / "src" / "ui" / "intro.menu"
ENDSCORETEAM_MENU = REPO_ROOT / "src" / "ui" / "endscoreteam.menu"
SPECTATOR_MENU = REPO_ROOT / "src" / "ui" / "spectator.menu"
SPECTATOR_FOLLOW_MENU = REPO_ROOT / "src" / "ui" / "spectator_follow.menu"
CGAME_HLIL = (
    REPO_ROOT
    / "references"
    / "hlil"
    / "quakelive"
    / "cgamex86.dll"
    / "cgamex86.dll_hlil.txt"
)
CGAME_GHIDRA = (
    REPO_ROOT
    / "references"
    / "reverse-engineering"
    / "ghidra"
    / "cgamex86"
    / "decompile_top_functions.c"
)


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


def _text_between(source: str, start_marker: str, end_marker: str) -> str:
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[start:end]


def test_vertical_accuracy_overlay_keeps_retail_payload_and_row_wiring() -> None:
    newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
    servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    stats_menu = (REPO_ROOT / "src" / "ui" / "ingamestats.menu").read_text(encoding="utf-8")
    order_block = _text_between(
        servercmds_source,
        "static const weapon_t cg_retailAccuracyCommandOrder[] = {",
        "static const cgRetailMapAlias_t",
    )
    vertical_order_block = _text_between(
        newdraw_source,
        "static const weapon_t cgVerticalAccWeaponOrder[] = {",
        "/*\n=============\nCG_ShouldDrawAccVertical",
    )
    parse_block = _block_from_marker(servercmds_source, "static void CG_ParseRetailAccuracyCommand")
    draw_weapons_block = _block_from_marker(newdraw_source, "static void CG_DrawWeaponVertical")
    draw_acc_block = _block_from_marker(newdraw_source, "static void CG_DrawAccVertical")
    ownerdraw_block = _block_from_marker(newdraw_source, "void CG_OwnerDraw(")

    for expected in (
        "WP_NONE",
        "WP_GAUNTLET",
        "WP_GRAPPLING_HOOK",
        "WP_HEAVY_MACHINEGUN",
    ):
        assert expected in order_block

    for expected in (
        "WP_GAUNTLET",
        "WP_MACHINEGUN",
        "WP_SHOTGUN",
        "WP_GRENADE_LAUNCHER",
        "WP_ROCKET_LAUNCHER",
        "WP_LIGHTNING",
        "WP_RAILGUN",
        "WP_PLASMAGUN",
        "WP_BFG",
        "WP_CHAINGUN",
        "WP_NAILGUN",
        "WP_PROX_LAUNCHER",
        "WP_HEAVY_MACHINEGUN",
    ):
        assert expected in vertical_order_block

    assert "WP_NONE" not in vertical_order_block
    assert "WP_GRAPPLING_HOOK" not in vertical_order_block
    assert "memset( cg.weaponAccuracies, 0, sizeof( cg.weaponAccuracies ) );" in parse_block
    assert "value = atoi( CG_Argv( i + 1 ) );" in parse_block
    assert "cg.weaponAccuracies[weapon] = value;" in parse_block
    assert "value < 0" not in parse_block
    assert "value > 100" not in parse_block
    assert "CG_DrawPic( rect->x, rect->y + rect->h * i, rect->w, rect->w, icon );" in draw_weapons_block
    assert "Com_sprintf( buffer, sizeof( buffer ), \"%i%%\", cg.weaponAccuracies[weapon] );" in draw_acc_block
    assert "CG_Text_Paint( rect->x, rect->y + rect->h * i, scale, color, buffer, 0, 0, textStyle );" in draw_acc_block
    assert "rect->h * ( i + 1 )" not in draw_acc_block

    assert "#define\tCG_WP_VERTICAL\t\t\t\t\t\t97" in menudef_source
    assert "#define\tCG_ACC_VERTICAL\t\t\t\t\t\t98" in menudef_source
    assert "ownerdraw CG_WP_VERTICAL" in stats_menu
    assert "ownerdraw CG_ACC_VERTICAL" in stats_menu
    assert "case CG_WP_VERTICAL:" in ownerdraw_block
    assert "CG_DrawWeaponVertical( &rect, color );" in ownerdraw_block
    assert "case CG_ACC_VERTICAL:" in ownerdraw_block
    assert "CG_DrawAccVertical( &rect, scale, color, textStyle );" in ownerdraw_block


def test_game_limit_uses_retail_limit_strings() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
    ui_shared_source = UI_SHARED.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    intro_menu = INTRO_MENU.read_text(encoding="utf-8")
    endscoreteam_menu = ENDSCORETEAM_MENU.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    block = _block_from_marker(source, "static void CG_DrawGameLimit")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
    display_context_block = _block_from_marker(main_source, "static void CG_InitDisplayContext")
    parse_serverinfo_block = _block_from_marker(servercmds_source, "void CG_ParseServerinfo")
    item_ownerdraw_parse_block = _block_from_marker(ui_shared_source, "qboolean ItemParse_ownerdraw( itemDef_t")
    retail_block = _text_between(
        hlil_source,
        '10033800    int32_t __convention("regparm") sub_10033800',
        "10033910",
    )
    retail_ownerdraw_block = _block_from_marker(ghidra_source, "void FUN_1003b0f0(")

    for expected in (
        '"Cap Limit: %d"',
        '"Frag Limit: %d"',
        '"Round Limit: %d"',
        '"Score Limit: %d"',
        "data_10a3ff38",
        "data_10a3ff48",
        "data_10a3ff54",
        "data_10a3ff34",
        "if (arg8 == 1)",
        "sub_100082b0(0, 0, result, &var_4, nullptr, 0, fconvert.s(fconvert.t(arg5)))",
        "var_4 = fconvert.s(x87_r7_5 - float.t(var_4))",
        "fconvert.s(fconvert.t(arg4[1]))",
    ):
        assert expected in retail_block

    assert "arg4[3]" not in retail_block

    for expected in (
        "case GT_CTF:",
        "case GT_1FCTF:",
        "case GT_OBELISK:",
        "case GT_HARVESTER:",
        'Com_sprintf( buffer, sizeof( buffer ), "Cap Limit: %d", cgs.capturelimit );',
        "case GT_CLAN_ARENA:",
        "case GT_FREEZE:",
        "case GT_RED_ROVER:",
        'Com_sprintf( buffer, sizeof( buffer ), "Round Limit: %d", cgs.roundlimit );',
        "case GT_DOMINATION:",
        "case GT_ATTACK_DEFEND:",
        'Com_sprintf( buffer, sizeof( buffer ), "Score Limit: %d", cgs.scorelimit );',
        'Com_sprintf( buffer, sizeof( buffer ), "Frag Limit: %d", cgs.fraglimit );',
        "if ( align == ITEM_ALIGN_CENTER ) {",
        "x -= CG_Text_Width( buffer, scale, 0 ) * 0.5f;",
        "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );",
    ):
        assert expected in block

    for stale in (
        "Time %i",
        "Captures %i",
        "Score %i",
        "Frags %i",
        "Mercy %i",
        "CG_GetServerInfoValue",
        "CG_HasObjectiveCountStat",
        "limitValue > 0",
        "CG_GetTextPosition",
        "ITEM_ALIGN_RIGHT",
        "rect->y + rect->h",
    ):
        assert stale not in block

    start = ownerdraw_block.index("case CG_GAME_LIMIT:")
    end = ownerdraw_block.index("break;", start)
    game_limit_case = ownerdraw_block[start:end]
    assert "CG_DrawGameLimit( &rect, scale, color, textStyle, align );" in game_limit_case
    assert "FUN_10033800(&local_18,param_13,param_14,param_16,param_10);" in retail_ownerdraw_block

    for expected in (
		"cgs.fraglimit = atoi( Info_ValueForKey( info, SERVERINFO_KEY_FRAGLIMIT ) );",
		"cgs.capturelimit = atoi( Info_ValueForKey( info, SERVERINFO_KEY_CAPTURELIMIT ) );",
		"cgs.scorelimit = atoi( Info_ValueForKey( info, SERVERINFO_KEY_SCORELIMIT ) );",
		"cgs.roundlimit = atoi( Info_ValueForKey( info, SERVERINFO_KEY_ROUNDLIMIT ) );",
    ):
        assert expected in parse_serverinfo_block

    assert any(line.split() == ["#define", "CG_GAME_LIMIT", "3"] for line in menudef_source.splitlines())
    assert '#include "ui/menudef.h"' in intro_menu
    assert "ownerdraw CG_GAME_LIMIT" in intro_menu
    assert '#include "ui/menudef.h"' in endscoreteam_menu
    assert "ownerdraw CG_GAME_LIMIT" in endscoreteam_menu
    assert "PC_Int_Parse(handle, &item->window.ownerDraw)" in item_ownerdraw_parse_block
    assert "item->type = ITEM_TYPE_OWNERDRAW;" in item_ownerdraw_parse_block
    assert "cgDC.ownerDrawItem = &CG_OwnerDraw;" in display_context_block
    assert "cgDC.ownerDrawWidth = &CG_OwnerDrawWidth;" in display_context_block
    assert "CG_GAME_LIMIT" not in width_block


def test_match_end_condition_uses_retail_condition_strings() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    end_condition_menu_hits = [
        path
        for path in (REPO_ROOT / "src" / "ui").glob("*.menu")
        if "ownerdraw CG_MATCH_END_CONDITION" in path.read_text(encoding="utf-8")
    ]
    block = _block_from_marker(source, "static void CG_DrawMatchEndCondition")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_block = _text_between(
        hlil_source,
        '10034280    int32_t __convention("regparm") sub_10034280',
        "10034360",
    )
    retail_ownerdraw_block = _block_from_marker(ghidra_source, "void FUN_1003b0f0")

    for expected in (
        '"Fastest race time within the time limit"',
        '"Most flag captures within the time limit"',
        '"Most rounds won within the time limit"',
        '"Highest score within the time limit"',
        '"First to reach the capture limit"',
        '"First to reach the mercy limit"',
        '"First to reach the round limit"',
        '"First to reach the score limit"',
        '"Highest score at the end of the game"',
    ):
        assert expected in hlil_source

    for expected in (
        "data_10a3ff14",
        "data_10a3ff44",
        "data_10a3ff38",
        "data_10a403ec",
        "data_10a403f0",
    ):
        assert expected in retail_block

    for expected in (
        "if ( cgs.gametype == GT_RACE ) {",
        'reason = "Fastest race time within the time limit";',
        "timeLimitExpired = ( cgs.timelimit > 0",
        "&& cg.time - cgs.levelStartTime >= cgs.timelimit * 60000 ) ? qtrue : qfalse;",
        'reason = "Most flag captures within the time limit";',
        'reason = "Most rounds won within the time limit";',
        'reason = "Highest score within the time limit";',
        "if ( cgs.capturelimit == 0 || ( cgs.scores1 < cgs.capturelimit && cgs.scores2 < cgs.capturelimit ) ) {",
        'reason = "First to reach the mercy limit";',
        'reason = "First to reach the capture limit";',
        'reason = "First to reach the round limit";',
        'reason = "First to reach the score limit";',
        'reason = "Highest score at the end of the game";',
        "CG_Text_Paint( rect->x, rect->y, scale, color, reason, 0, 0, textStyle );",
    ):
        assert expected in block

    assert any(line.split()[:3] == ["#define", "CG_MATCH_END_CONDITION", "9"] for line in menudef_source.splitlines())
    assert len(end_condition_menu_hits) >= 10
    assert "case 9:" in retail_ownerdraw_block
    assert "FUN_10034280(param_13,param_14,param_16);" in retail_ownerdraw_block
    assert "case CG_MATCH_END_CONDITION:" in ownerdraw_block
    assert "CG_DrawMatchEndCondition( &rect, scale, color, textStyle );" in ownerdraw_block
    assert "CG_DrawMatchEndCondition(&rect, text_x, text_y, scale, color, textStyle);" not in ownerdraw_block

    for stale in (
        "Match complete",
        "Time limit hit",
        "Capture limit hit",
        "Score limit hit",
        "Frag limit hit",
        "Mercy rule",
        "Sudden death",
        "CG_TimeLimitHit",
        "CG_FragLimitHit",
        "CG_CaptureLimitHit",
        "CG_ScoreLimitHit",
        "CG_MercyLimitHit",
        "CG_GetTextPosition",
    ):
        assert stale not in block


def test_local_time_uses_retail_date_format() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    block = _block_from_marker(source, "static void CG_DrawLocalTime")

    assert "static const char *cgMonthAbbrev[12]" in source
    assert '%02d:%02d (%s %02d, %d)' in block
    assert "x = rect->x;" in block
    assert "CG_AlignTextX( &x, buffer, scale, align );" in block
    assert "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );" in block
    assert "CG_GetTextPosition" not in block
    assert '%02i:%02i' not in block


def test_spectator_messages_use_retail_copy_family() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    spectator_menu = SPECTATOR_MENU.read_text(encoding="utf-8")
    spectator_follow_menu = SPECTATOR_FOLLOW_MENU.read_text(encoding="utf-8")
    block = _block_from_marker(source, "static void CG_DrawSpectatorMessages")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_block = _text_between(
        hlil_source,
        "10034d70    int32_t __fastcall sub_10034d70",
        "100350c0",
    )
    retail_decompile = _text_between(
        ghidra_source,
        "/* FUN_10034d70 @ 10034d70",
        "/* FUN_10005e60",
    )
    retail_switch = _text_between(ghidra_source, "case 0x23:", "case 0x24:")

    for expected in (
        "vec4_t spectatorHintColor = { 0.73f, 0.73f, 0.73f, 0.7f };",
        "(void)scale;",
        "(void)color;",
        "(void)textStyle;",
        "if ( !rect || !cg.snap || !cg_drawSpecMessages.integer ) {",
        "cgs.gametype == GT_CLAN_ARENA || cgs.gametype == GT_RED_ROVER",
        "cg.snap->ps.pm_type == PM_SPECTATOR",
        "cg.snap->ps.persistant[PERS_TEAM] != TEAM_SPECTATOR",
        "Round In Progress",
        "x = 320.0f - (float)CG_Text_Width( message, 0.35f, 0 ) * 0.5f;",
        "CG_Text_Paint( x, 60.0f, 0.35f, colorWhite, message, 0, 0, 3 );",
        'CG_Text_Paint( rect->x, rect->y, 0.22f, colorWhite, "SPECTATOR MODE", 0, 0, 0 );',
        "SPECTATOR MODE",
        'CG_Text_Paint( rect->x, rect->y + 12.0f, 0.18f, spectatorHintColor, "Press mouse button 1 to cycle through players", 0, 0, 0 );',
        "Press mouse button 1 to cycle through players",
        'trap_Key_GetBindingBuf( trap_Key_GetKey( "+moveup" ), bindingBuf, sizeof( bindingBuf ) );',
        'CG_FindBrowserOverlayByName( "comp_specfollowhud_menu" )',
        "!cgs.clientinfo[cg.clientNum].spectateOnly",
        'CG_Text_Paint( 20.0f, 461.0f, 0.28f, colorWhite, "waiting to play", 0, 0, 3 );',
        "waiting to play",
        'CG_Text_Paint( 20.0f, 453.0f, 0.28f, colorWhite, "press ESC and use the JOIN buttons", 0, 0, 3 );',
        "press ESC and use the JOIN buttons",
        'CG_Text_Paint( 20.0f, 470.0f, 0.28f, colorWhite, "to enter the game", 0, 0, 3 );',
        "to enter the game",
    ):
        assert expected in block

    for expected in (
        "eax_2 == 4 || eax_2 == 0xb",
        "*(ecx + 0x30) == 2",
        "*(ecx + 0x138) != 3",
        "data_10aa6934 == 0",
        'sub_100575e0("SPECTATOR MODE")',
        '(*(data_1074cccc + 0x184))("+moveup")',
        "data_10ab9688 == 0 ||",
        "data_10a42404 == 0",
    ):
        assert expected in retail_block

    for expected in (
        '"Press mouse button 1 to cycle through players"',
        '"press ESC and use the JOIN buttons"',
        '"to enter the game"',
    ):
        assert expected in hlil_source
    assert '"Press mouse button 1 to cycle through players"' in retail_decompile

    assert "FUN_10034d70();" in retail_switch
    assert "case CG_SPEC_MESSAGES:" in ownerdraw_block
    assert "CG_DrawSpectatorMessages( &rect, scale, color, textStyle );" in ownerdraw_block
    assert "#define\tCG_SPEC_MESSAGES" in menudef_source
    assert spectator_menu.count("ownerdraw CG_SPEC_MESSAGES") == 2
    assert spectator_follow_menu.count("ownerdraw CG_SPEC_MESSAGES") == 2

    for stale in (
        "FOLLOWING %s",
        "FREE SPECTATE",
        "Press FIRE to cycle, JUMP for free camera",
        "Press FIRE to follow a player",
        "press ESC and use the JOIN menu to play",
        "CG_DrawPregameCoach(rect",
        "case GT_FREEZE:",
        "case GT_ATTACK_DEFEND:",
        "cgs.matchRoundState",
        "scale * 0.8f",
    ):
        assert stale not in block


def test_spec_and_player_preview_ownerdraws_match_retail_dispatch_cluster() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    spectator_menu = SPECTATOR_MENU.read_text(encoding="utf-8")
    spectator_follow_menu = SPECTATOR_FOLLOW_MENU.read_text(encoding="utf-8")
    all_menu_source = "\n".join(
        path.read_text(encoding="utf-8") for path in (REPO_ROOT / "src" / "ui").glob("*.menu")
    )
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    value_block = _block_from_marker(source, "float CG_GetValue")
    width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
    key_block = _block_from_marker(main_source, "static qboolean CG_OwnerDrawHandleKey")
    display_context_block = _block_from_marker(main_source, "static void CG_InitDisplayContext")
    spectator_block = _block_from_marker(source, "static void CG_DrawSpectatorMessages")
    player_head_block = _block_from_marker(source, "static void CG_DrawPlayerHead")
    player_model_block = _block_from_marker(source, "static void CG_DrawPlayerModel")
    armor_icon_block = _block_from_marker(source, "static void CG_DrawPlayerArmorIcon")
    retail_switch = _block_from_marker(ghidra_source, "void FUN_1003b0f0")
    retail_spectator = _text_between(
        hlil_source,
        "10034d70    int32_t __fastcall sub_10034d70",
        "100350c0",
    )
    retail_player_head = _text_between(
        hlil_source,
        "1002f950    int80_t sub_1002f950",
        "1002fc70",
    )
    retail_player_model = _text_between(
        hlil_source,
        "10034980    int32_t __convention",
        "10034a00",
    )
    retail_armor_icon = _text_between(
        hlil_source,
        "1002e3f0    void __convention",
        "1002e500",
    )
    constants = {}
    for line in menudef_source.splitlines():
        parts = line.split()
        if len(parts) < 3 or parts[0] != "#define":
            continue
        try:
            constants[parts[1]] = int(parts[2], 0)
        except ValueError:
            continue

    assert constants["CG_SPEC_MESSAGES"] == 35
    assert constants["CG_PLAYER_HEAD"] == 36
    assert constants["CG_PLAYERMODEL"] == 37
    assert constants["CG_PLAYER_ARMOR_ICON"] == 38
    assert constants["CG_PLAYER_ARMOR_ICON2D"] == 39

    for expected in (
        "case 0x23:\n    FUN_10034d70();",
        "case 0x24:\n    FUN_1002f950();",
        "case 0x25:\n    FUN_10034980();",
        "case 0x26:\n    FUN_1002e3f0(param_8 & 0x10000000);",
        "case 0x27:\n    FUN_1002e3f0(1);",
    ):
        assert expected in retail_switch

    for expected in (
        "case CG_SPEC_MESSAGES:",
        "CG_DrawSpectatorMessages( &rect, scale, color, textStyle );",
        "case CG_PLAYER_HEAD:",
        "CG_DrawPlayerHead( &rect, ownerDrawFlags & CG_SHOW_2DONLY );",
        "case CG_PLAYERMODEL:",
        "CG_DrawPlayerModel( &rect );",
        "case CG_PLAYER_ARMOR_ICON:",
        "CG_DrawPlayerArmorIcon( &rect, ownerDrawFlags & CG_SHOW_2DONLY );",
        "case CG_PLAYER_ARMOR_ICON2D:",
        "CG_DrawPlayerArmorIcon( &rect, qtrue );",
    ):
        assert expected in ownerdraw_block

    for expected in (
        "Round In Progress",
        "SPECTATOR MODE",
        "Press mouse button 1 to cycle through players",
        "waiting to play",
        "press ESC and use the JOIN buttons",
        "to enter the game",
        'CG_FindBrowserOverlayByName( "comp_specfollowhud_menu" )',
    ):
        assert expected in spectator_block
    for expected in (
        '"Round In Progress"',
        '"SPECTATOR MODE"',
    ):
        assert expected in retail_spectator
    for expected in (
        '"Press mouse button 1 to cycle through players"',
        '"press ESC and use the JOIN buttons"',
        '"to enter the game"',
    ):
        assert expected in hlil_source

    for expected in (
        "if ( cg.damageTime && cg.time - cg.damageTime < DAMAGE_TIME )",
        "cg.headStartYaw = 180 + cg.damageX * 45;",
        "frac = frac * frac * ( 3 - 2 * frac );",
        "CG_DrawHead( x, rect->y, rect->w, rect->h, cg.snap->ps.clientNum, angles );",
    ):
        assert expected in player_head_block
    for expected in (
        "data_10ab8f9c",
        "data_10ab8fa0",
        "return sub_10009490",
    ):
        assert expected in retail_player_head

    for expected in (
        "clientNum = cg.spectatorTrackedClient;",
        "clientNum = cg.snap->ps.clientNum;",
        "weaponNum = CG_ClientPreviewWeapon( clientNum );",
        "VectorSet( previewAngles, 5.0f, 210.0f, 0.0f );",
        "CG_DrawClientModelPreview( rect, clientNum, weaponNum, previewAngles, qtrue );",
    ):
        assert expected in player_model_block
    for expected in (
        "data_10a249cc",
        "data_10a9c7a0",
        "0x43520000",
        "return sub_10008c40",
    ):
        assert expected in retail_player_model

    for expected in (
        "if ( draw2D || ( !cg_draw3dIcons.integer && cg_drawIcons.integer) )",
        "CG_DrawPic( rect->x, rect->y + rect->h/2 + 1, rect->w, rect->h, cgs.media.armorIcon );",
        "origin[0] = 90;",
        "origin[2] = -10;",
        "angles[YAW] = ( cg.time & 2047 ) * 360 / 2048.0;",
        "CG_Draw3DModel( rect->x, rect->y, rect->w, rect->h, cgs.media.armorModel, 0, origin, angles );",
    ):
        assert expected in armor_icon_block
    for expected in (
        "data_10a5f418",
        "data_10a5f414",
        "data_10a64a4c != 0",
        "data_10a69a2c != 0",
        "data_10b7102c != 0",
    ):
        assert expected in retail_armor_icon

    assert spectator_menu.count("ownerdraw CG_SPEC_MESSAGES") == 2
    assert spectator_follow_menu.count("ownerdraw CG_SPEC_MESSAGES") == 2
    for absent_menu_draw in (
        "CG_PLAYER_HEAD",
        "CG_PLAYERMODEL",
        "CG_PLAYER_ARMOR_ICON",
        "CG_PLAYER_ARMOR_ICON2D",
    ):
        assert f"ownerdraw {absent_menu_draw}" not in all_menu_source

    for callback_block in (value_block, width_block, key_block):
        for draw_name in (
            "CG_SPEC_MESSAGES",
            "CG_PLAYER_HEAD",
            "CG_PLAYERMODEL",
            "CG_PLAYER_ARMOR_ICON",
            "CG_PLAYER_ARMOR_ICON2D",
        ):
            assert draw_name not in callback_block
    assert "cgDC.ownerDrawItem = &CG_OwnerDraw;" in display_context_block
    assert "cgDC.getValue = &CG_GetValue;" in display_context_block
    assert "cgDC.ownerDrawWidth = &CG_OwnerDrawWidth;" in display_context_block
    assert "cgDC.ownerDrawHandleKey = &CG_OwnerDrawHandleKey;" in display_context_block


def test_player_status_ownerdraws_40_to_44_match_retail_dispatch_values_and_menus() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    hud_menu = (REPO_ROOT / "src" / "ui" / "hud.menu").read_text(encoding="utf-8")
    all_menu_source = "\n".join(
        path.read_text(encoding="utf-8") for path in (REPO_ROOT / "src" / "ui").glob("*.menu")
    )
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    value_block = _block_from_marker(source, "float CG_GetValue")
    width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
    key_block = _block_from_marker(main_source, "static qboolean CG_OwnerDrawHandleKey")
    display_context_block = _block_from_marker(main_source, "static void CG_InitDisplayContext")
    armor_value_block = _block_from_marker(source, "static void CG_DrawPlayerArmorValue")
    armor_100_block = _block_from_marker(source, "static void CG_DrawPlayerArmorBar100")
    armor_200_block = _block_from_marker(source, "static void CG_DrawPlayerArmorBar200")
    tiered_block = _block_from_marker(source, "static void CG_DrawArmorTieredColorized")
    health_block = _block_from_marker(source, "static void CG_DrawPlayerHealth")
    retail_switch = _block_from_marker(ghidra_source, "void FUN_1003b0f0")
    retail_value = _text_between(
        hlil_source,
        "10031610    long double sub_10031610",
        "100316ab",
    )
    retail_armor_value = _text_between(
        hlil_source,
        "1002e500    void __convention",
        "1002e660",
    )
    retail_armor_100 = _text_between(
        hlil_source,
        "1002efb0    int32_t sub_1002efb0",
        "1002f0c0",
    )
    retail_armor_200 = _text_between(
        hlil_source,
        "1002f0c0    void sub_1002f0c0",
        "1002f1f0",
    )
    retail_tiered = _text_between(
        hlil_source,
        '1002f780    int32_t __convention("regparm") sub_1002f780',
        "1002f860",
    )
    retail_health = _text_between(
        hlil_source,
        "1002fdf0    void __convention",
        "1002ff50",
    )
    def menu_ownerdraw_count(menu_source: str, ownerdraw: str) -> int:
        return sum(
            1
            for line in menu_source.splitlines()
            if line.split()[:2] == ["ownerdraw", ownerdraw]
        )

    for ownerdraw, value in (
        ("CG_PLAYER_ARMOR_VALUE", "40"),
        ("CG_PLAYER_ARMOR_BAR_100", "41"),
        ("CG_PLAYER_ARMOR_BAR_200", "42"),
        ("CG_ARMORTIERED_COLORIZED", "43"),
        ("CG_PLAYER_HEALTH", "44"),
    ):
        assert any(line.split()[:3] == ["#define", ownerdraw, value] for line in menudef_source.splitlines())
        assert ownerdraw not in width_block
        assert ownerdraw not in key_block

    for expected in (
        "case 0x28:\n    FUN_1002e500(param_12,param_13,param_14,param_16,param_10);",
        "case 0x29:\n    FUN_1002efb0(param_15);",
        "case 0x2a:\n    FUN_1002f0c0(param_15);",
        "case 0x2b:\n    FUN_1002f780(param_15);",
        "case 0x2c:\n    FUN_1002fdf0(param_12,param_13,param_14,param_16,param_10);",
    ):
        assert expected in retail_switch

    for expected in (
        "case CG_PLAYER_ARMOR_VALUE:",
        "CG_DrawPlayerArmorValue( &rect, scale, color, shader, textStyle, align );",
        "case CG_PLAYER_ARMOR_BAR_100:",
        "CG_DrawPlayerArmorBar100( &rect, shader );",
        "case CG_PLAYER_ARMOR_BAR_200:",
        "CG_DrawPlayerArmorBar200( &rect, shader );",
        "case CG_ARMORTIERED_COLORIZED:",
        "CG_DrawArmorTieredColorized(&rect);",
        "case CG_PLAYER_HEALTH:",
        "CG_DrawPlayerHealth( &rect, scale, color, shader, textStyle, align );",
    ):
        assert expected in ownerdraw_block

    assert "case CG_PLAYER_ARMOR_VALUE:" in value_block
    assert "return ps->stats[STAT_ARMOR];" in value_block
    assert "case CG_PLAYER_HEALTH:" in value_block
    assert "return ps->stats[STAT_HEALTH];" in value_block
    for absent_value in (
        "CG_PLAYER_ARMOR_BAR_100",
        "CG_PLAYER_ARMOR_BAR_200",
        "CG_ARMORTIERED_COLORIZED",
    ):
        assert absent_value not in value_block
    for expected in (
        "case 0x28",
        "return float.t(*(esi + 0xfc))",
        "case 0x2c",
        "return float.t(*(esi + 0xec))",
    ):
        assert expected in retail_value

    for expected in (
        "value = ps->stats[STAT_ARMOR];",
        "if ( shader ) {",
        "CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );",
        'Com_sprintf( num, sizeof( num ), "%i", value );',
        "y = rect->y + CG_Text_Height( num, scale, 0 );",
        "CG_AlignTextX( &x, num, scale, align );",
        "CG_Text_Paint( x, y, scale, color, num, 0, 0, textStyle );",
    ):
        assert expected in armor_value_block
    for expected in (
        "int32_t ebp = *(data_10a6f8c4 + 0xfc)",
        "if (arg1 != 0)",
        "(*(data_1074cccc + 0x138))(arg6)",
        "if (arg8 == 1)",
        "else if (arg8 == 2)",
        "var_4 = fconvert.s(fconvert.t(ebx[1]) + float.t(var_4))",
        "sub_10008440(fconvert.s(fconvert.t(*ebx)), fconvert.s(fconvert.t(var_4)), arg4,",
    ):
        assert expected in retail_armor_value

    for expected in (
        "armor = cg.snap->ps.stats[STAT_ARMOR];",
        "Vector4Copy( CG_TeamColor( cg.snap->ps.persistant[PERS_TEAM] ), barColor );",
        "ratio = CG_BarValueFraction( armor, 100 );",
        "shader = cgs.media.armorBar100;",
        "CG_DrawBarFillFromRight( rect, shader, ratio, barColor );",
    ):
        assert expected in armor_100_block
    for expected in (
        "float.t(*(ecx + 0xfc))",
        "var_8 = 100f",
        "float var_4_1 = fconvert.s(float.t(1) - fconvert.t(var_8_1) / x87_r6_2)",
        "fconvert.t(arg1[2]) + fconvert.t(*arg1)",
        "sub_10012710",
    ):
        assert expected in retail_armor_100

    for expected in (
        "excessArmor = armor - 100;",
        "if ( excessArmor <= 0 ) {",
        "Vector4Copy( CG_TeamColor( cg.snap->ps.persistant[PERS_TEAM] ), barColor );",
        "ratio = CG_BarValueFraction( excessArmor, 100 );",
        "shader = cgs.media.armorBar200;",
        "CG_DrawBarFillFromBottom( rect, shader, ratio, barColor );",
    ):
        assert expected in armor_200_block
    for expected in (
        "float.t(*(ecx + 0xfc)) - fconvert.t(100.0)",
        "return",
        "float var_4 = fconvert.s(float.t(1) - fconvert.t(var_8_3) / x87_r5_2)",
        "fconvert.t(arg1[1]) + fconvert.t(arg1[3])",
        "sub_10012710",
    ):
        assert expected in retail_armor_200

    for expected in (
        "CG_GetArmorTierColorForTier( cg.snap->ps.stats[STAT_ARMOR_TIER], color );",
        "color[3] = 0.5f;",
        "CG_FillRect( rect->x, rect->y, rect->w, rect->h, color );",
    ):
        assert expected in tiered_block
    for expected in (
        "int32_t eax_3 = *(data_10a6f8c4 + 0x124)",
        "0x3f800000",
        "var_8_1 = *(arg3 + 0xc)",
        "(*(data_1074cccc + 0x138))(&var_14)",
        "sub_100126a0(fconvert.s(fconvert.t(*arg4)))",
    ):
        assert expected in retail_tiered

    for expected in (
        "value = ps->stats[STAT_HEALTH];",
        "if (shader) {",
        "CG_DrawPic(rect->x, rect->y, rect->w, rect->h, shader);",
        'Com_sprintf (num, sizeof(num), "%i", value);',
        "y = rect->y + CG_Text_Height( num, scale, 0 );",
        "CG_AlignTextX( &x, num, scale, align );",
        "CG_Text_Paint( x, y, scale, color, num, 0, 0, textStyle );",
    ):
        assert expected in health_block
    for expected in (
        "int32_t ebp = *(data_10a6f8c4 + 0xec)",
        "if (arg1 != 0)",
        "(*(data_1074cccc + 0x138))(arg6)",
        "if (arg8 == 1)",
        "else if (arg8 == 2)",
        "var_4 = fconvert.s(fconvert.t(ebx[1]) + float.t(var_4))",
        "sub_10008440(fconvert.s(fconvert.t(*ebx)), fconvert.s(fconvert.t(var_4)), arg4,",
    ):
        assert expected in retail_health

    assert menu_ownerdraw_count(hud_menu, "CG_PLAYER_ARMOR_BAR_100") == 1
    assert menu_ownerdraw_count(hud_menu, "CG_PLAYER_ARMOR_BAR_200") == 1
    assert menu_ownerdraw_count(all_menu_source, "CG_PLAYER_ARMOR_VALUE") == 7
    assert menu_ownerdraw_count(all_menu_source, "CG_ARMORTIERED_COLORIZED") == 5
    assert menu_ownerdraw_count(all_menu_source, "CG_PLAYER_HEALTH") == 7

    assert "cgDC.ownerDrawItem = &CG_OwnerDraw;" in display_context_block
    assert "cgDC.getValue = &CG_GetValue;" in display_context_block
    assert "cgDC.ownerDrawWidth = &CG_OwnerDrawWidth;" in display_context_block
    assert "cgDC.ownerDrawHandleKey = &CG_OwnerDrawHandleKey;" in display_context_block


def test_health_bar_and_ammo_ownerdraws_45_to_49_match_retail_dispatch_values_and_menus() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    hud_menu = (REPO_ROOT / "src" / "ui" / "hud.menu").read_text(encoding="utf-8")
    all_menu_source = "\n".join(
        path.read_text(encoding="utf-8") for path in (REPO_ROOT / "src" / "ui").glob("*.menu")
    )
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    value_block = _block_from_marker(source, "float CG_GetValue")
    width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
    key_block = _block_from_marker(main_source, "static qboolean CG_OwnerDrawHandleKey")
    display_context_block = _block_from_marker(main_source, "static void CG_InitDisplayContext")
    health_100_block = _block_from_marker(source, "static void CG_DrawPlayerHealthBar100")
    health_200_block = _block_from_marker(source, "static void CG_DrawPlayerHealthBar200")
    ammo_icon_block = _block_from_marker(source, "static void CG_DrawPlayerAmmoIcon")
    ammo_value_block = _block_from_marker(source, "static void CG_DrawPlayerAmmoValue")
    retail_switch = _block_from_marker(ghidra_source, "void FUN_1003b0f0")
    retail_value = _text_between(
        hlil_source,
        "10031610    long double sub_10031610",
        "100316ab",
    )
    retail_health_100 = _text_between(
        hlil_source,
        "1002ed50    int32_t sub_1002ed50",
        "1002ee50",
    )
    retail_health_200 = _text_between(
        hlil_source,
        "1002ee50    int32_t sub_1002ee50",
        "1002efb0",
    )
    retail_ammo_icon = _text_between(
        hlil_source,
        '1002e660    void* __convention("regparm") sub_1002e660',
        "1002e7c0",
    )
    retail_ammo_value = _text_between(
        hlil_source,
        '1002e7c0    int32_t __convention("regparm") sub_1002e7c0',
        "1002e9b0",
    )
    def menu_ownerdraw_count(menu_source: str, ownerdraw: str) -> int:
        return sum(
            1
            for line in menu_source.splitlines()
            if line.split()[:2] == ["ownerdraw", ownerdraw]
        )

    for ownerdraw, value in (
        ("CG_PLAYER_HEALTH_BAR_100", "45"),
        ("CG_PLAYER_HEALTH_BAR_200", "46"),
        ("CG_PLAYER_AMMO_ICON", "47"),
        ("CG_PLAYER_AMMO_ICON2D", "48"),
        ("CG_PLAYER_AMMO_VALUE", "49"),
    ):
        assert any(line.split()[:3] == ["#define", ownerdraw, value] for line in menudef_source.splitlines())
        assert ownerdraw not in width_block
        assert ownerdraw not in key_block

    for expected in (
        "case 0x2d:\n    FUN_1002ed50(param_15);",
        "case 0x2e:\n    FUN_1002ee50(param_15);",
        "case 0x2f:\n    FUN_1002e660(param_8 & 0x10000000);",
        "case 0x30:\n    FUN_1002e660(1);",
        "case 0x31:\n    FUN_1002e7c0(param_12,param_13,param_15,param_16,param_10);",
    ):
        assert expected in retail_switch

    for expected in (
        "case CG_PLAYER_HEALTH_BAR_100:",
        "CG_DrawPlayerHealthBar100( &rect, shader );",
        "case CG_PLAYER_HEALTH_BAR_200:",
        "CG_DrawPlayerHealthBar200( &rect, shader );",
        "case CG_PLAYER_AMMO_ICON:",
        "CG_DrawPlayerAmmoIcon( &rect, ownerDrawFlags & CG_SHOW_2DONLY );",
        "case CG_PLAYER_AMMO_ICON2D:",
        "CG_DrawPlayerAmmoIcon( &rect, qtrue );",
        "case CG_PLAYER_AMMO_VALUE:",
        "CG_DrawPlayerAmmoValue( &rect, scale, color, shader, textStyle, align );",
    ):
        assert expected in ownerdraw_block

    assert "case CG_PLAYER_AMMO_VALUE:" in value_block
    assert "return ps->ammo[cent->currentState.weapon];" in value_block
    for absent_value in (
        "CG_PLAYER_HEALTH_BAR_100",
        "CG_PLAYER_HEALTH_BAR_200",
        "CG_PLAYER_AMMO_ICON",
        "CG_PLAYER_AMMO_ICON2D",
    ):
        assert absent_value not in value_block
    for expected in (
        "case 0x31",
        "int32_t eax_3 = *(ecx * 0x2d0 + 0x10abbb90)",
        "if (eax_3 != 0)",
        "return float.t(*(esi + (eax_3 << 2) + 0x1ac))",
    ):
        assert expected in retail_value

    for expected in (
        "health = cg.snap->ps.stats[STAT_HEALTH];",
        "maxHealth = CG_PlayerMaxHealth();",
        "Vector4Copy( CG_TeamColor( cg.snap->ps.persistant[PERS_TEAM] ), barColor );",
        "ratio = CG_BarValueFraction( health, maxHealth );",
        "shader = cgs.media.healthBar100;",
        "CG_DrawBarFill( rect, shader, ratio, barColor );",
    ):
        assert expected in health_100_block
    for expected in (
        "float.t(*(ecx + 0xec))",
        "float.t(*(ecx + 0x108))",
        "var_8 = var_4",
        "float var_8_1 = fconvert.s(fconvert.t(var_4_2) / x87_r6_2)",
        "sub_10012710(fconvert.s(fconvert.t(*arg1)), fconvert.s(fconvert.t(arg1[1])),",
    ):
        assert expected in retail_health_100

    for expected in (
        "excessHealth = health - maxHealth;",
        "if ( excessHealth <= 0 ) {",
        "Vector4Copy( CG_TeamColor( cg.snap->ps.persistant[PERS_TEAM] ), barColor );",
        "ratio = CG_BarValueFraction( excessHealth, maxHealth );",
        "shader = cgs.media.healthBar200;",
        "CG_DrawBarFillFromBottom( rect, shader, ratio, barColor );",
    ):
        assert expected in health_200_block
    for expected in (
        "*(ecx + 0xec) - result",
        "if (not(0f <= xmm0))",
        "if (xmm0 f<= 0)",
        "float var_8_1 = fconvert.s(float.t(1) - fconvert.t(var_4_4) / x87_r6_2)",
        "fconvert.t(arg1[1]) + fconvert.t(arg1[3])",
        "sub_10012710",
    ):
        assert expected in retail_health_200

    for expected in (
        "if ( draw2D || (!cg_draw3dIcons.integer && cg_drawIcons.integer) )",
        "weapon = cg.predictedPlayerState.weapon;",
        "icon = cg_weapons[ weapon ].ammoIcon;",
        "CG_DrawPic( rect->x, rect->y, rect->w, rect->h, icon );",
        "weapon = cent->currentState.weapon;",
        "origin[0] = 70;",
        "angles[YAW] = 90 + 20 * sin( cg.time / 1000.0 );",
        "CG_Draw3DModel( rect->x, rect->y, rect->w, rect->h, cg_weapons[ weapon ].ammoModel, 0, origin, angles );",
    ):
        assert expected in ammo_icon_block
    for expected in (
        "if (arg2 != 0)",
        "data_10a9c2a0 * 0x88",
        "data_10a69a2c != 0",
        "data_10b7102c != 0",
        "var_18 = 0x428c0000",
        "fconvert.t(20.0) + fconvert.t(90.0)",
    ):
        assert expected in retail_ammo_icon

    for expected in (
        "weapon = cent->currentState.weapon;",
        "if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {",
        "if ( weapon == WP_GAUNTLET || weapon == WP_GRAPPLING_HOOK ) {",
        "value = ps->ammo[weapon];",
        "if ( value == -1 ) {",
        "if ( cgs.media.infiniteAmmoShader ) {",
        "iconSize = rect->w;",
        "CG_DrawPic( iconX, rect->y, iconSize, iconSize, cgs.media.infiniteAmmoShader );",
        "CG_AlignTextX( &x, num, scale, align );",
        "CG_Text_Paint( x, y, scale, color, num, 0, 0, textStyle );",
    ):
        assert expected in ammo_value_block
    for expected in (
        "if (result != 0 && result != 1 && result != 0xa)",
        "int32_t esi_1 = *(ecx_1 + (result << 2) + 0x1ac)",
        "if (esi_1 s> 0xffffffff)",
        "if (arg5 != 0)",
        "sub_100575e0(&data_100687a8)",
        "if (esi_1 == 0xffffffff)",
        "if (arg7 == 1)",
        "else if (arg7 == 2)",
        "data_10a5f4e8",
    ):
        assert expected in retail_ammo_value

    assert menu_ownerdraw_count(hud_menu, "CG_PLAYER_HEALTH_BAR_100") == 1
    assert menu_ownerdraw_count(hud_menu, "CG_PLAYER_HEALTH_BAR_200") == 1
    assert menu_ownerdraw_count(all_menu_source, "CG_PLAYER_AMMO_ICON") == 0
    assert menu_ownerdraw_count(all_menu_source, "CG_PLAYER_AMMO_ICON2D") == 5
    assert menu_ownerdraw_count(all_menu_source, "CG_PLAYER_AMMO_VALUE") == 6

    assert "cgDC.ownerDrawItem = &CG_OwnerDraw;" in display_context_block
    assert "cgDC.getValue = &CG_GetValue;" in display_context_block
    assert "cgDC.ownerDrawWidth = &CG_OwnerDrawWidth;" in display_context_block
    assert "cgDC.ownerDrawHandleKey = &CG_OwnerDrawHandleKey;" in display_context_block


def test_item_score_race_and_oneflag_ownerdraws_50_to_54_match_retail_dispatch_values_and_menus() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    all_menu_source = "\n".join(
        path.read_text(encoding="utf-8") for path in (REPO_ROOT / "src" / "ui").glob("*.menu")
    )
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    value_block = _block_from_marker(source, "float CG_GetValue")
    width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
    key_block = _block_from_marker(main_source, "static qboolean CG_OwnerDrawHandleKey")
    display_context_block = _block_from_marker(main_source, "static void CG_InitDisplayContext")
    item_block = _block_from_marker(source, "static void CG_DrawPlayerItem")
    compact_score_block = _block_from_marker(source, "static qboolean CG_BuildCompactScoreValueText")
    player_score_block = _block_from_marker(source, "static void CG_DrawPlayerScore")
    score_value_block = _block_from_marker(source, "static void CG_DrawScoreValue")
    race_times_block = _block_from_marker(source, "static qboolean CG_RaceBuildTimesStrings")
    race_block = _block_from_marker(source, "static void CG_DrawRaceStatusAndTimes")
    oneflag_block = _block_from_marker(source, "static void CG_OneFlagStatus")
    retail_switch = _block_from_marker(ghidra_source, "void FUN_1003b0f0")
    retail_item = _text_between(
        hlil_source,
        "1002fc70    float sub_1002fc70",
        "1002fdf0",
    )
    retail_race = _text_between(
        hlil_source,
        "1002f1f0    int32_t __convention",
        "1002f5d0",
    )
    retail_oneflag = _text_between(
        hlil_source,
        "10030ff0    void sub_10030ff0",
        "100310f0",
    )
    retail_score = _text_between(
        hlil_source,
        "100323d0    void* __convention",
        "10032520",
    )

    def menu_ownerdraw_count(menu_source: str, ownerdraw: str) -> int:
        return sum(
            1
            for line in menu_source.splitlines()
            if line.split()[:2] == ["ownerdraw", ownerdraw]
        )

    for ownerdraw, value in (
        ("CG_PLAYER_ITEM", "50"),
        ("CG_PLAYER_SCORE", "51"),
        ("CG_RACE_STATUS", "52"),
        ("CG_RACE_TIMES", "53"),
        ("CG_ONEFLAG_STATUS", "54"),
    ):
        assert any(line.split()[:3] == ["#define", ownerdraw, value] for line in menudef_source.splitlines())
        assert ownerdraw not in width_block
        assert ownerdraw not in key_block

    for expected in (
        "case 0x32:\n    FUN_1002fc70(param_13);",
        "case 0x33:",
        "case 0x53:",
        "case 0x56:",
        "FUN_100323d0(param_7,param_13,param_16,param_10);",
        "case 0x34:",
        "case 0x35:",
        "FUN_1002f1f0(param_13,param_10);",
        "case 0x36:\n    FUN_10030ff0();",
    ):
        assert expected in retail_switch

    for expected in (
        "case CG_PLAYER_ITEM:",
        "CG_DrawPlayerItem( &rect, scale, ownerDrawFlags & CG_SHOW_2DONLY );",
        "case CG_PLAYER_SCORE:",
        "CG_DrawScoreValue( &rect, scale, color, shader, textStyle, ownerDraw );",
        "case CG_ONEFLAG_STATUS:",
        "CG_OneFlagStatus(&rect);",
        "case CG_RACE_STATUS:",
        "case CG_RACE_TIMES:",
        "CG_DrawRaceStatusAndTimes( &rect, scale, color, textStyle, ownerDraw );",
    ):
        assert expected in ownerdraw_block

    assert "case CG_PLAYER_SCORE:" in value_block
    assert "return cg.snap->ps.persistant[PERS_SCORE];" in value_block
    for absent_value in (
        "CG_PLAYER_ITEM",
        "CG_RACE_STATUS",
        "CG_RACE_TIMES",
        "CG_ONEFLAG_STATUS",
    ):
        assert absent_value not in value_block

    for expected in (
        "int32_t esi = *(result i+ 0xf0)",
        "sub_10051770(esi, edi)",
        "*((result << 3) + &data_10067298) == 6",
        "*(eax_4 + 0x114)",
        "*(eax_4 + 0x118)",
        '"%d%%"',
        "fconvert.t(arg1) * fconvert.t(0.25)",
    ):
        assert expected in retail_item

    for expected in (
        "value = cg.snap->ps.stats[STAT_HOLDABLE_ITEM];",
        "CG_RegisterItemVisuals( value );",
        "CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cg_items[ value ].icon );",
        "CG_Draw3DModel(rect->x, rect->y, rect->w, rect->h, cg_items[ value ].models[0], 0, origin, angles );",
        "BG_HoldableForItemTag( bg_itemlist[ value ].giTag ) == HI_INVULNERABILITY",
        "cg.snap->ps.stats[STAT_PLAYER_ITEM_TIME]",
        "cg.snap->ps.stats[STAT_PLAYER_ITEM_TIME_MAX]",
        'Com_sprintf( progressText, sizeof( progressText ), "%d%%", progressPercent );',
        "progressScale = scale * 0.25f;",
        "CG_Text_Paint( rect->x + ( rect->w - progressWidth ) * 0.5f, rect->y + rect->h, progressScale,",
    ):
        assert expected in item_block

    for expected in (
        "if (result == 0x33)",
        "if (edx != 2)",
        "ecx = *(result + 0x12c)",
        "ecx = *(*(result + 0xb4) * 0x738 + 0x10a41e1c)",
        "if (ecx != 0xffffd8f1)",
        "ecx == 0x7fffffff || ecx s< 0",
        "sub_100012a0(ecx)",
        "sub_10008440",
    ):
        assert expected in retail_score

    for expected in (
        "if ( value == SCORE_NOT_PRESENT ) {",
        "if ( cgs.gametype == GT_RACE ) {",
        "if ( value == 0x7fffffff || value < 0 ) {",
        'Q_strncpyz( buffer, "-", bufferSize );',
        "CG_FormatSignedWholeSeconds( value )",
        'Com_sprintf( buffer, bufferSize, "%i", value );',
    ):
        assert expected in compact_score_block
    for expected in (
        "value = cg.snap->ps.persistant[PERS_SCORE];",
        "if ( cgs.gametype == GT_RACE ) {",
        "value = cgs.clientinfo[clientNum].score;",
        "CG_BuildCompactScoreValueText( value, num, sizeof( num ) )",
        "CG_Text_Paint( rect->x, rect->y, scale, color, num, 0, 0, textStyle );",
    ):
        assert expected in player_score_block
    for expected in (
        "case CG_PLAYER_SCORE:",
        "CG_DrawPlayerScore( rect, scale, color, shader, textStyle );",
        "case CG_1STPLACE:",
        "value = cgs.scores1;",
        "case CG_2NDPLACE:",
        "value = cgs.scores2;",
    ):
        assert expected in score_value_block

    for expected in (
        "data_10a3ff14 == 2",
        "if (arg3 == 0x34)",
        'sub_100575e0("Bind \'kill\' to respawn")',
        'sub_100575e0("Press %s to respawn.")',
        '"LAST TIME"',
        '"CURRENT RUN"',
        "else if (arg3 == 0x35)",
        "sub_10001320(data_10abaab8)",
    ):
        assert expected in retail_race

    for expected in (
        'Q_strncpyz( primary, "Warmup", primarySize );',
        'Com_sprintf( primary, primarySize, "Cur %s", timeBuffer );',
        'Com_sprintf( primary, primarySize, "Last %s", timeBuffer );',
        'Q_strncpyz( primary, "Ready", primarySize );',
        'Com_sprintf( secondary, secondarySize, "Best %s (%s)", timeBuffer, deltaText );',
        'Com_sprintf( secondary, secondarySize, "Best %s", timeBuffer );',
        'Com_sprintf( secondary, secondarySize, "Leader %s", timeBuffer );',
    ):
        assert expected in race_times_block
    for expected in (
        "if ( ownerDraw == CG_RACE_STATUS ) {",
        "text = CG_GetRaceStatusText();",
        "if ( ownerDraw != CG_RACE_TIMES ) {",
        "CG_RaceBuildTimesStrings( primary, sizeof( primary ), secondary, sizeof( secondary ) )",
        "lineHeight = ( rect->h > 0.0f ) ? rect->h : ( scale * 12.0f );",
        "CG_Text_Paint( rect->x, rect->y + rect->h + lineHeight, scale, color, secondary, 0, 0, textStyle );",
    ):
        assert expected in race_block

    for expected in (
        "data_10a3ff14 == 6",
        "data_10a403fc",
        "if (eax == 3 || eax == 4)",
        "var_4 = 9",
        "var_4 = 0xfffffff7",
        "(&data_10a5fc2c)[esi_1]",
        "sub_100126a0",
    ):
        assert expected in retail_oneflag

    for expected in (
        "if (cgs.gametype != GT_1FCTF) {",
        "shader = cgs.media.poiFlagAtBaseNeutralShader;",
        "shader = cgs.media.poiFlagTakenNeutralShader;",
        "shader = cgs.media.poiFlagDroppedNeutralShader;",
        "shader = cgs.media.poiFlagStolenNeutralShader;",
        "if ( cgs.scores1 == SCORE_NOT_PRESENT || cgs.scores1 < cgs.scores2 ) {",
        "if ( cgs.scores2 == SCORE_NOT_PRESENT || cgs.scores2 <= cgs.scores1 ) {",
        "yOffset = 9.0f;",
        "yOffset = -9.0f;",
        "trap_R_SetColor( colorWhite );",
        "CG_DrawPic( rect->x, rect->y + yOffset, rect->w, rect->h, shader );",
        "trap_R_SetColor( NULL );",
    ):
        assert expected in oneflag_block
    assert "cgs.media.flagShader[shaderIndex]" not in oneflag_block

    assert menu_ownerdraw_count(all_menu_source, "CG_PLAYER_ITEM") == 6
    assert menu_ownerdraw_count(all_menu_source, "CG_PLAYER_SCORE") == 4
    assert menu_ownerdraw_count(all_menu_source, "CG_RACE_STATUS") == 5
    assert menu_ownerdraw_count(all_menu_source, "CG_RACE_TIMES") == 5
    assert menu_ownerdraw_count(all_menu_source, "CG_ONEFLAG_STATUS") == 6

    assert "cgDC.ownerDrawItem = &CG_OwnerDraw;" in display_context_block
    assert "cgDC.getValue = &CG_GetValue;" in display_context_block
    assert "cgDC.ownerDrawWidth = &CG_OwnerDrawWidth;" in display_context_block
    assert "cgDC.ownerDrawHandleKey = &CG_OwnerDrawHandleKey;" in display_context_block


def test_level_timer_uses_retail_clock_format() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    draw_source = CG_DRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    helper_block = _block_from_marker(source, "static qboolean CG_BuildLevelTimerMilliseconds")
    block = _block_from_marker(source, "static void CG_DrawLevelTimer")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    classic_timer_block = _block_from_marker(draw_source, "static float CG_DrawTimer")
    retail_timer_block = _text_between(
        hlil_source,
        "10030c00    void sub_10030c00",
        "10030d20",
    )
    retail_clock_block = _text_between(
        hlil_source,
        "10029770    int32_t sub_10029770()",
        "10029820",
    )

    for expected in (
        "sub_10029770() == 1",
        'sub_100575e0("%i:%i%i")',
        "if (eax_9 == 1)",
        "else if (eax_9 != 2)",
        "fconvert.t(eax_12[1])",
    ):
        assert expected in retail_timer_block

    for expected in (
        "int32_t edx = data_10a403e0",
        "if (edx == 0)",
        "edx = data_10a9c1ec",
        "if (data_10ab8f4c != 0)",
        "data_10ab8f58 == 0",
        "int32_t ecx_1 = esi * 0xea60",
        "int32_t eax_7 = ecx_1 - edx + edi",
        "*ebx = edx - ecx_1 - edi",
        "if (data_10a6e6ac != 1)",
        "eax_7 = edx - edi",
    ):
        assert expected in retail_clock_block

    for expected in (
        "timeoutStart = CG_GetMatchTimeoutStartTime();",
        "currentTime = timeoutStart;",
        "if ( currentTime == 0 ) {",
        "currentTime = cg.time;",
        "if ( cg.warmup != 0 ) {",
        "if ( !CG_ShowPlayersRemaining() || cgs.matchRoundNumber <= 0 ) {",
        "return qfalse;",
        "limitMilliseconds = cgs.timelimit * 60000;",
        "milliseconds = limitMilliseconds - currentTime + cgs.levelStartTime;",
        "milliseconds = currentTime - limitMilliseconds - cgs.levelStartTime;",
        "else if ( cg_levelTimerDirection.integer != 1 ) {",
        "milliseconds = currentTime - cgs.levelStartTime;",
        "*millisecondsOut = milliseconds;",
        "return qtrue;",
    ):
        assert expected in helper_block

    for expected in (
        "CG_BuildLevelTimerMilliseconds( &milliseconds );",
        "seconds = milliseconds / 1000;",
        'Q_strncpyz( buffer, CG_FormatMinutesSeconds( seconds ), sizeof( buffer ) );',
        "x = rect->x;",
        "CG_AlignTextX( &x, buffer, scale, align );",
        "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );",
    ):
        assert expected in block

    assert "CG_DrawLevelTimer(&rect, scale, color, textStyle, align);" in ownerdraw_block
    assert '{ &cg_levelTimerDirection, "cg_levelTimerDirection", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },' in main_source
    assert "cg_levelTimerDirection.integer == 1" in classic_timer_block

    for stale in (
        "CG_GetScoreboardTimerSeconds",
        "rect->y + rect->h",
        "( elapsed + 500 ) / 1000",
        "( milliseconds + 500 ) / 1000",
        '%02i:%02i',
        '"up"',
        '"down"',
    ):
        assert stale not in block


def test_intro_panel_draws_use_retail_map_panel_shapes() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    match_details_menu_hits = [
        path
        for path in (REPO_ROOT / "src" / "ui").glob("*.menu")
        if "ownerdraw CG_MATCH_DETAILS" in path.read_text(encoding="utf-8")
    ]
    game_type_map = _block_from_marker(source, "static void CG_DrawGameTypeMap")
    match_details = _block_from_marker(source, "static void CG_DrawMatchDetails")
    phase_label = _block_from_marker(source, "static const char *CG_GetMatchPhaseText")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_ownerdraw_block = _block_from_marker(ghidra_source, "void FUN_1003b0f0")
    retail_match_details = _text_between(
        hlil_source,
        '10034420    int32_t __convention("regparm") sub_10034420',
        "100344b0",
    )
    retail_game_type_map = _text_between(
        hlil_source,
        "100344b0    void sub_100344b0",
        "10034590",
    )

    assert "CG_BuildIntroPanelDetailString( detailBuffer, sizeof( detailBuffer ) );" in game_type_map
    assert '%s - %s", CG_GameTypeString(), detailBuffer' in game_type_map
    assert "x = rect->x;" in game_type_map
    assert "CG_AlignTextX( &x, buffer, scale, align );" in game_type_map
    assert "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );" in game_type_map
    assert 'CG_GetMapDisplayName( mapName, sizeof( mapName ) );' not in game_type_map
    assert '%s - %s - %s' not in game_type_map
    assert "CG_GetTextPosition" not in game_type_map

    for expected in (
        "eax_2, ecx_1 = sub_100575e0(\"%s - %s\")",
        "if (arg5 == 1)",
        "*ebp = fconvert.s(fconvert.t(*ebp) - float.t(arg1) * fconvert.t(0.5))",
        "else if (arg5 == 2)",
        "*ebp = fconvert.s(fconvert.t(*ebp) - float.t(arg1))",
    ):
        assert expected in retail_game_type_map

    assert "CG_BuildIntroPanelDetailString( detailBuffer, sizeof( detailBuffer ) );" in match_details
    assert 'CG_GetMatchPhaseText()' in match_details
    assert 'CG_GameTypeShortString(), detailBuffer );' in match_details
    assert '%s - %s - %s' in match_details
    assert "CG_Text_PaintExt( rect->x, rect->y, scale, color, buffer, 0, 0, ITEM_TEXTSTYLE_NORMAL, FONT_DEFAULT );" in match_details
    assert "CG_Text_Paint( rect->x, rect->y, scale, color, buffer, 0, 0, textStyle );" not in match_details
    assert '%s - %s - %s - %s' not in match_details
    assert 'CG_GetMapDisplayName( mapName, sizeof( mapName ) );' not in match_details
    assert "CG_GetTextPosition" not in match_details
    assert 'sub_100575e0("%s - %s - %s")' in retail_match_details
    assert "sub_10008440(fconvert.s(fconvert.t(var_4)), fconvert.s(fconvert.t(var_8)), 0," in retail_match_details
    assert "fconvert.s(float.t(0)), 0)" in retail_match_details

    for expected in (
        'MATCH WARMUP',
        'MATCH IN PROGRESS',
        'MATCH SUMMARY',
    ):
        assert expected in phase_label

    assert "CG_GetMatchDetailsPhaseLabel" not in source
    assert any(line.split()[:3] == ["#define", "CG_MATCH_DETAILS", "8"] for line in menudef_source.splitlines())
    assert len(match_details_menu_hits) >= 10
    assert "case 8:" in retail_ownerdraw_block
    assert "FUN_10034420(param_13,param_14,param_16);" in retail_ownerdraw_block
    assert "CG_DrawGameTypeMap( &rect, scale, color, textStyle, align );" in ownerdraw_block
    assert "case CG_MATCH_DETAILS:" in ownerdraw_block
    assert "CG_DrawMatchDetails( &rect, scale, color, textStyle );" in ownerdraw_block
    assert "CG_DrawGameTypeMap(&rect, text_x, text_y, scale, color, textStyle);" not in ownerdraw_block
    assert "CG_DrawMatchDetails(&rect, text_x, text_y, scale, color, textStyle);" not in ownerdraw_block


def test_intro_panel_gametype_tables_match_retail_labels() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    short_labels = _block_from_marker(source, "static const char *CG_GameTypeShortString")
    full_labels = _block_from_marker(source, "const char *CG_GameTypeString()")

    for expected in (
        'return "DUEL";',
        'return "RACE";',
        'return "1F";',
        'return "OB";',
        'return "HAR";',
        'return "FT";',
        'return "DOM";',
        'return "AD";',
        'return "RR";',
        'return "Unknown Gametype";',
    ):
        assert expected in short_labels

    assert 'return "Attack and Defend";' in full_labels
    assert 'Attack & Defend' not in source


def test_plain_gametype_and_match_state_draws_use_retail_origin_alignment() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    game_type = _block_from_marker(source, "static void CG_DrawGameType( rectDef_t")
    match_state = _block_from_marker(source, "static void CG_DrawMatchState")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_game_type = _text_between(
        hlil_source,
        "10034c20    int32_t sub_10034c20",
        "10034cc0",
    )
    retail_match_state = _text_between(
        hlil_source,
        "10034360    int32_t sub_10034360",
        "100343d0",
    )

    for expected in (
        "if (arg5 == 1)",
        "sub_100082b0(0, 0, ebx, &arg1, nullptr, 0, fconvert.s(fconvert.t(arg2)))",
        "float var_28 = fconvert.s(fconvert.t(*(ebp + 4)))",
        "return sub_10008440(fconvert.s(fconvert.t(arg1)), var_28, 0,",
    ):
        assert expected in retail_game_type
    assert "else if (arg5 == 2)" not in retail_game_type

    for expected in (
        "gameType = CG_GameTypeString();",
        "x = rect->x;",
        "if ( align == ITEM_ALIGN_CENTER ) {",
        "x -= CG_Text_Width( gameType, scale, 0 ) * 0.5f;",
        "CG_Text_Paint( x, rect->y, scale, color, gameType, 0, 0, textStyle );",
    ):
        assert expected in game_type
    assert "ITEM_ALIGN_RIGHT" not in game_type
    assert "rect->y + rect->h" not in game_type
    assert "qhandle_t shader" not in game_type
    assert "CG_DrawGameType( &rect, scale, color, textStyle, align );" in ownerdraw_block
    assert "CG_DrawGameType(&rect, scale, color, shader, textStyle);" not in ownerdraw_block

    assert "fconvert.s(fconvert.t(arg1[1]))" in retail_match_state
    assert "arg1[3]" not in retail_match_state
    assert "CG_Text_Paint( rect->x, rect->y, scale, color, CG_GetMatchPhaseText(), 0, 0, textStyle );" in match_state
    assert "rect->y + rect->h" not in match_state


def test_match_status_uses_retail_status_text_family() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    intro_menu = INTRO_MENU.read_text(encoding="utf-8")
    status_text = _block_from_marker(source, "const char *CG_GetGameStatusText")
    status_helper = _block_from_marker(source, "const char *CG_GetMatchStatusText")
    draw_match_status = _block_from_marker(source, "static void CG_DrawMatchStatus")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_draw_match_status = _text_between(
        hlil_source,
        "10034cc0    void sub_10034cc0",
        "10034d70",
    )
    retail_status_helper = _text_between(
        hlil_source,
        "10034a00    char const* const sub_10034a00()",
        "10034b30",
    )

    assert "case GT_SINGLE_PLAYER:" in status_text
    assert "case GT_RED_ROVER:" in status_text
    assert "cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR" in status_text
    assert '"Teams are tied at %i"' in status_text
    assert '"^1Red^7 leads ^4Blue^7, %i to %i"' in status_text
    assert '"^4Blue^7 leads ^1Red^7, %i to %i"' in status_text
    assert '"Red leads Blue, %i to %i"' not in status_text
    assert '"Blue leads Red, %i to %i"' not in status_text
    assert "cgs.gametype < GT_TEAM" not in status_text

    assert "phase = CG_GetMatchPhaseText();" in status_helper
    assert 'phase = "MATCH SUMMARY";' not in status_helper
    assert 'phase = "MATCH WARMUP";' not in status_helper
    assert 'phase = "MATCH IN PROGRESS";' not in status_helper
    assert "if ( cgs.scores1 == SCORE_NOT_PRESENT && cgs.scores2 == SCORE_NOT_PRESENT &&" in status_helper
    assert "( cgs.gametype < GT_TEAM || cgs.gametype == GT_RED_ROVER )" in status_helper
    assert "if ( cgs.gametype == GT_RACE ) {" in status_helper
    assert "CG_FormatSignedMilliseconds( cgs.scores1 )" in status_helper
    assert '"%s - %s^7 leads with a score of %s"' in status_helper
    assert "if ( cgs.gametype >= GT_TEAM && cgs.gametype != GT_RED_ROVER ) {" in status_helper
    assert '"%s - Teams are tied at %i"' in status_helper
    assert '"%s - ^1Red^7 leads ^4Blue^7, %i to %i"' in status_helper
    assert '"%s - ^4Blue^7 leads ^1Red^7, %i to %i"' in status_helper
    assert "cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR" in status_helper
    assert "if ( cgs.scores1 != CG_SCORE_FORFEIT ) {" in status_helper
    assert "if ( cgs.scores1 != SCORE_NOT_PRESENT ) {" not in status_helper
    assert "leaderName = cgs.firstPlaceName;" in status_helper
    assert "leaderName = cgs.secondPlaceName;" in status_helper
    assert '"%s - %s leads with %i"' in status_helper
    assert '"%s - %s place with %i"' in status_helper
    assert "CG_GetGameStatusText()" not in status_helper
    assert "if ( !status || !status[0] )" not in status_helper

    assert "statusText = CG_GetMatchStatusText();" in draw_match_status
    assert "x = rect->x;" in draw_match_status
    assert "CG_AlignTextX( &x, statusText, scale, align );" in draw_match_status
    assert "CG_Text_Paint( x, rect->y, scale, color, statusText, 0, 0, textStyle );" in draw_match_status
    assert 'Com_sprintf( buffer, sizeof( buffer ), "%s - %s", CG_GetMatchStateLabel(), CG_GetGameStatusText() );' not in draw_match_status
    assert "if ( !cg.snap ) {" not in draw_match_status
    assert "CG_GetTextPosition" not in draw_match_status
    assert any(line.split()[:3] == ["#define", "CG_MATCH_STATUS", "10"] for line in menudef_source.splitlines())
    assert "ownerdraw CG_MATCH_STATUS" in intro_menu
    assert "case CG_MATCH_STATUS:" in ownerdraw_block
    assert "CG_DrawMatchStatus( &rect, scale, color, textStyle, align );" in ownerdraw_block
    assert "CG_DrawMatchStatus(&rect, text_x, text_y, scale, color, textStyle);" not in ownerdraw_block

    for expected in (
        "if (esi == edx && esi == 0xffffd8f1 && (eax s< 3 || eax == 0xc))",
        "if (eax == 2)",
        'var_18 = " - %s^7 leads with a score of %s"',
        "else if (eax s>= 3 && eax != 0xc)",
        'var_18 = " - ^4Blue^7 leads ^1Red^7, %i to',
        'var_18 = " - ^1Red^7 leads ^4Blue^7, %i to',
        "if (*(edi + 0x138) == 3)",
        "if (esi != 0xfffffc19)",
        'var_18 = " - %s leads with %i"',
        'var_18 = " - %s place with %i"',
    ):
        assert expected in retail_status_helper

    for expected in (
        "char* eax = sub_10034a00()",
        "int32_t eax_1 = sub_100575e0(&data_10068de8)",
        "if (edx == 1)",
        "*ebx = fconvert.s(fconvert.t(*ebx) - float.t(arg_10) * fconvert.t(0.5))",
        "else if (edx == 2)",
        "*ebx = fconvert.s(fconvert.t(*ebx) - float.t(arg_10))",
    ):
        assert expected in retail_draw_match_status


def test_game_status_ownerdraw_matches_retail_text_and_wiring() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    local_source = CG_LOCAL.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")

    status_text = _block_from_marker(source, "const char *CG_GetGameStatusText")
    draw_game_status = _block_from_marker(source, "static void CG_DrawGameStatus")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
    retail_status_text = _text_between(
        hlil_source,
        "10034b30    void* const sub_10034b30()",
        "10034bc7",
    )
    retail_draw_call = _text_between(
        ghidra_source,
        "  case 7:\n    FUN_10034bd0(param_13,param_14,param_16);",
        "  case 8:",
    )

    assert "#define\tCG_GAME_STATUS\t\t\t\t\t\t7" in menudef_source
    assert "case 7:\n    FUN_10034bd0(param_13,param_14,param_16);" in retail_draw_call
    assert "const char *CG_GetGameStatusText( void );" in local_source

    for menu_name in (
        "ingamescoreteam.menu",
        "ingamescorenoteam.menu",
        "ingame_scoreboard_1fctf.menu",
        "ingame_scoreboard_ad.menu",
        "ingame_scoreboard_ca.menu",
        "ingame_scoreboard_ctf.menu",
        "ingame_scoreboard_dom.menu",
        "ingame_scoreboard_duel.menu",
        "ingame_scoreboard_ffa.menu",
        "ingame_scoreboard_ft.menu",
        "ingame_scoreboard_har.menu",
        "ingame_scoreboard_race.menu",
        "ingame_scoreboard_rr.menu",
        "ingame_scoreboard_tdm.menu",
    ):
        menu_source = (REPO_ROOT / "src" / "ui" / menu_name).read_text(encoding="utf-8")
        assert "ownerdraw CG_GAME_STATUS" in menu_source

    for expected in (
        "case GT_SINGLE_PLAYER:",
        "case GT_FFA:",
        "case GT_TOURNAMENT:",
        "case GT_RED_ROVER:",
        "cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR",
        '"%s place with %i"',
        "if ( cg.teamScores[0] == cg.teamScores[1] ) {",
        '"Teams are tied at %i"',
        "if ( cg.teamScores[0] > cg.teamScores[1] ) {",
        '"^1Red^7 leads ^4Blue^7, %i to %i"',
        '"^4Blue^7 leads ^1Red^7, %i to %i"',
    ):
        assert expected in status_text

    for stale in (
        "cgs.scores1",
        "cgs.scores2",
        "CG_GetMatchStatusText",
        "CG_GetMatchStateLabel",
        '" - Teams are tied at %i"',
        '"Red leads Blue, %i to %i"',
        '"Blue leads Red, %i to %i"',
    ):
        assert stale not in status_text

    for expected in (
        "if (esi == 2)",
        "if (esi s< 3 || esi == 0xc)",
        "if (*(edx + 0x138) == 3)",
        'return sub_100575e0("%s place with %i")',
        "int32_t eax_1 = data_10a9cdc8",
        "int32_t ecx_2 = data_10a9cdcc",
        'return sub_100575e0("Teams are tied at %i")',
        'return sub_100575e0("^4Blue^7 leads ^1Red^7, %i to %i")',
        'return sub_100575e0("^1Red^7 leads ^4Blue^7, %i to %i")',
    ):
        assert expected in retail_status_text

    assert "static void CG_DrawGameStatus( rectDef_t *rect, float scale, vec4_t color, int textStyle )" in draw_game_status
    assert "qhandle_t shader" not in draw_game_status
    assert "CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, CG_GetGameStatusText(), 0, 0, textStyle);" in draw_game_status
    assert "CG_DrawGameStatus( &rect, scale, color, textStyle );" in ownerdraw_block
    assert "CG_DrawGameStatus(&rect, scale, color, shader, textStyle);" not in ownerdraw_block
    assert "return CG_Text_Width( CG_GetGameStatusText(), scale, 0 );" in width_block


def test_player_model_helper_restores_retail_3d_preview_scene() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    shared_block = _block_from_marker(source, "static void CG_DrawProfileModel")
    preview_block = _block_from_marker(source, "static void CG_DrawClientModelPreview")
    first_place_block = _block_from_marker(source, "static void CG_DrawFirstPlaceModel")
    player_block = _block_from_marker(source, "static void CG_DrawPlayerModel")

    assert "shader = ci->modelIcon;" in shared_block
    assert "shader = CG_GetProfileFallbackShader();" in shared_block
    assert "Vector4Set( modulate, 1.0f, 1.0f, 1.0f, active ? 1.0f : 0.8f );" in shared_block

    for expected in (
        "heightScale = ( ci->headOffset[0] > 0.0f ) ? ci->headOffset[0] : 1.0f;",
        "previewHeight = 32.0f / ( heightScale * 0.85f );",
        "refdef.rdflags = RDF_NOWORLDMODEL;",
        "CG_InitClientPreviewEntity( &legs, origin, renderfx );",
        'CG_PositionRotatedEntityOnTag( &torso, &legs, ci->legsModel, "tag_torso" );',
        'CG_PositionRotatedEntityOnTag( &head, &torso, ci->torsoModel, "tag_head" );',
        'CG_PositionEntityOnTag( &gun, &torso, ci->torsoModel, "tag_weapon" );',
        "trap_R_AddLightToScene( lightOrigin, 500.0f, 1.0f, 1.0f, 1.0f );",
        "trap_R_AddLightToScene( lightOrigin, 500.0f, 1.0f, 0.0f, 0.0f );",
        "trap_R_RenderScene( &refdef );",
        "CG_DrawProfileModel( rect, clientNum, active );",
    ):
        assert expected in preview_block

    for expected in (
        "weaponNum = score->bestWeapon;",
        "weaponNum = CG_ClientPreviewWeapon( score->client );",
        "VectorSet( previewAngles, 5.0f, 160.0f, 0.0f );",
        "CG_DrawClientModelPreview( rect, score->client, weaponNum, previewAngles, active );",
    ):
        assert expected in first_place_block

    assert "clientNum = cg.spectatorTrackedClient;" in player_block
    assert "clientNum = cg.snap->ps.clientNum;" in player_block
    assert "weaponNum = CG_ClientPreviewWeapon( clientNum );" in player_block
    assert "VectorSet( previewAngles, 5.0f, 210.0f, 0.0f );" in player_block
    assert "CG_DrawClientModelPreview( rect, clientNum, weaponNum, previewAngles, qtrue );" in player_block


def test_endgame_summary_uses_retail_message_family() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    summary_block = _block_from_marker(source, "static const char *CG_GetEndGameScoreText")
    winner_block = _block_from_marker(source, "static const char *CG_GetMatchWinnerText")

    assert "#define CG_SCORE_FORFEIT -999" in source
    assert "static const char *CG_PluralSuffix( int count )" in source

    for expected in (
        "PERS_DEFEND_COUNT",
        "PERS_ASSIST_COUNT",
        "PERS_CAPTURES",
        '"You forfeited the match."',
        '"You finished with a score of %d."',
        '"You finished %s with a score of %d"',
        '"You had %d assist%s."',
        '"You had %d defend%s."',
        '"You had %d flag capture%s."',
        '"You captured %d skull%s."',
        "cgs.gametype == GT_HARVESTER",
        "cgs.gametype == GT_RED_ROVER",
        "score == CG_SCORE_FORFEIT",
    ):
        assert expected in summary_block

    for stale in (
        '"Your score: %i"',
        '"Score: %i"',
        '"Top score: %i"',
        '"%s %i - %i %s"',
    ):
        assert stale not in summary_block

    assert '"^%c%s^7 WINS by forfeit"' in winner_block
    assert '"%s^7 WINS by forfeit"' in winner_block
    assert "winner->score == CG_SCORE_FORFEIT" in winner_block
    assert "byForfeit = qtrue;" in winner_block


def test_starting_weapons_uses_retail_icon_preview_path() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    token_table = _block_from_marker(main_source, "static const cgRetailWeaponToken_t cgRetailWeaponTokens")
    token_helper = _block_from_marker(main_source, "int CG_StartingWeaponIndexFromToken")
    preview_mask = _block_from_marker(source, "static unsigned int CG_GetStartingWeaponPreviewMask")
    block = _block_from_marker(source, "static void CG_DrawStartingWeapons")
    retail_block = _text_between(
        hlil_source,
        "10033910    int32_t sub_10033910",
        "10033b10",
    )

    assert "static const cgStartingWeaponInfo_t cgStartingWeaponIcons" in source
    assert "CG_ConfigString( CS_LOADOUT_MASK )" in preview_mask
    assert '"g_startingWeapons"' not in preview_mask
    for expected in (
        "if ((data_10a601dc & result) != 0)",
        "if (data_10a249cc != 0)",
        "int32_t esi_1 = data_10a9c7a4",
        "esi_1 = 0xe",
    ):
        assert expected in retail_block

    assert "primaryIndex = cg.weaponPrimary;" in block
    assert "primaryIndex = CG_STARTING_WEAPON_ICON_COUNT;" in block
    assert "CG_GetStartingWeaponIconHandle( cgStartingWeaponIcons[primaryIndex - 1].weapon )" in block
    assert 'CG_Text_Paint( plusX, plusY, scale, color, "+", 0, 0, textStyle );' in block
    assert "CG_DrawPic( rect->x + xOffset, rect->y, rect->w, rect->h, shader );" in block
    assert "CG_DrawPic( rect->x + xOffset + rect->w, rect->y, rect->w, rect->h, shader );" in block

    for expected in (
        '{ "g", WP_GAUNTLET, 1 }',
        '{ "mg", WP_MACHINEGUN, 2 }',
        '{ "sg", WP_SHOTGUN, 3 }',
        '{ "cg", WP_CHAINGUN, 13 }',
        '{ "hmg", WP_HEAVY_MACHINEGUN, 14 }',
    ):
        assert expected in token_table

    for expected in (
        "token = COM_ParseExt( &cursor, qtrue );",
        "weaponToken = CG_RetailWeaponTokenForToken( token );",
        "return weaponToken->index;",
    ):
        assert expected in token_helper

    for stale in (
        "Factory loadouts active",
        "Default loadout",
        "Q_strcat( buffer",
        "CG_ResolveWeaponName( weapon )",
        "CG_StartingWeaponFromToken",
        "cg_weaponPrimary.integer",
    ):
        assert stale not in block


def test_front_panel_ownerdraw_trio_matches_retail_dispatch_and_callback_surface() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    intro_menu = INTRO_MENU.read_text(encoding="utf-8")
    endscoreteam_menu = ENDSCORETEAM_MENU.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_ownerdraw_block = _block_from_marker(ghidra_source, "void FUN_1003b0f0")
    value_block = _block_from_marker(source, "float CG_GetValue")
    width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
    key_block = _block_from_marker(main_source, "static qboolean CG_OwnerDrawHandleKey")
    display_context_block = _block_from_marker(main_source, "static void CG_InitDisplayContext")
    server_case = _text_between(ownerdraw_block, "case CG_SERVER_SETTINGS:", "case CG_STARTING_WEAPONS:")
    starting_case = _text_between(ownerdraw_block, "case CG_STARTING_WEAPONS:", "case CG_GAME_LIMIT:")
    limit_case = _text_between(ownerdraw_block, "case CG_GAME_LIMIT:", "case CG_GAME_TYPE_ICON:")

    assert any(line.split() == ["#define", "CG_SERVER_SETTINGS", "1"] for line in menudef_source.splitlines())
    assert any(line.split() == ["#define", "CG_STARTING_WEAPONS", "2"] for line in menudef_source.splitlines())
    assert any(line.split() == ["#define", "CG_GAME_LIMIT", "3"] for line in menudef_source.splitlines())

    assert "CG_DrawServerSettings(&rect, text_x, text_y, scale, color, textStyle);" in server_case
    assert "CG_DrawStartingWeapons(&rect, text_x, text_y, scale, color, textStyle);" in starting_case
    assert "CG_DrawGameLimit( &rect, scale, color, textStyle, align );" in limit_case

    assert "case 1:" in retail_ownerdraw_block
    assert "FUN_1003a1c0(param_13,param_14);" in retail_ownerdraw_block
    assert "case 2:" in retail_ownerdraw_block
    assert "FUN_10033910(param_13,param_14,param_16);" in retail_ownerdraw_block
    assert "case 3:" in retail_ownerdraw_block
    assert "FUN_10033800(&local_18,param_13,param_14,param_16,param_10);" in retail_ownerdraw_block

    for ownerdraw in ("CG_SERVER_SETTINGS", "CG_STARTING_WEAPONS", "CG_GAME_LIMIT"):
        assert ownerdraw not in value_block
        assert ownerdraw not in width_block
        assert ownerdraw not in key_block

    assert "cgDC.ownerDrawItem = &CG_OwnerDraw;" in display_context_block
    assert "cgDC.getValue = &CG_GetValue;" in display_context_block
    assert "cgDC.ownerDrawWidth = &CG_OwnerDrawWidth;" in display_context_block
    assert "cgDC.ownerDrawHandleKey = &CG_OwnerDrawHandleKey;" in display_context_block

    assert "ownerdraw CG_STARTING_WEAPONS" in intro_menu
    assert "ownerdraw CG_GAME_LIMIT" in intro_menu
    assert "ownerdraw CG_GAME_LIMIT" in endscoreteam_menu


def test_gametype_ownerdraw_trio_matches_retail_dispatch_and_callback_surface() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_ownerdraw_block = _block_from_marker(ghidra_source, "void FUN_1003b0f0")
    value_block = _block_from_marker(source, "float CG_GetValue")
    width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
    key_block = _block_from_marker(main_source, "static qboolean CG_OwnerDrawHandleKey")
    display_context_block = _block_from_marker(main_source, "static void CG_InitDisplayContext")
    icon_case = _text_between(ownerdraw_block, "case CG_GAME_TYPE_ICON:", "case CG_GAME_TYPE_MAP:")
    map_case = _text_between(ownerdraw_block, "case CG_GAME_TYPE_MAP:", "case CG_GAME_TYPE:")
    type_case = _text_between(ownerdraw_block, "case CG_GAME_TYPE:", "case CG_GAME_STATUS:")
    menu_text = {
        path.name: path.read_text(encoding="utf-8")
        for path in (REPO_ROOT / "src" / "ui").glob("*.menu")
    }

    def menu_hits_for(ownerdraw: str) -> set[str]:
        return {
            name
            for name, text in menu_text.items()
            if any(line.split()[:2] == ["ownerdraw", ownerdraw] for line in text.splitlines())
        }

    assert any(line.split()[:3] == ["#define", "CG_GAME_TYPE", "4"] for line in menudef_source.splitlines())
    assert any(line.split()[:3] == ["#define", "CG_GAME_TYPE_ICON", "5"] for line in menudef_source.splitlines())
    assert any(line.split()[:3] == ["#define", "CG_GAME_TYPE_MAP", "6"] for line in menudef_source.splitlines())

    assert "CG_DrawGameTypeIcon(&rect);" in icon_case
    assert "CG_DrawGameTypeMap( &rect, scale, color, textStyle, align );" in map_case
    assert "CG_DrawGameType( &rect, scale, color, textStyle, align );" in type_case

    assert "case 4:" in retail_ownerdraw_block
    assert "FUN_10034c20(&local_18,param_13,param_14,param_16,param_10);" in retail_ownerdraw_block
    assert "case 5:" in retail_ownerdraw_block
    assert "FUN_10034840();" in retail_ownerdraw_block
    assert "case 6:" in retail_ownerdraw_block
    assert "FUN_100344b0(&local_18,param_13,param_14,param_16,param_10);" in retail_ownerdraw_block

    assert "case CG_GAME_TYPE:" in width_block
    assert "return CG_Text_Width( CG_GameTypeString(), scale, 0 );" in width_block
    assert "CG_GAME_TYPE_ICON" not in width_block
    assert "CG_GAME_TYPE_MAP" not in width_block

    for ownerdraw in ("CG_GAME_TYPE", "CG_GAME_TYPE_ICON", "CG_GAME_TYPE_MAP"):
        assert ownerdraw not in value_block
        assert ownerdraw not in key_block

    assert "cgDC.ownerDrawItem = &CG_OwnerDraw;" in display_context_block
    assert "cgDC.getValue = &CG_GetValue;" in display_context_block
    assert "cgDC.ownerDrawWidth = &CG_OwnerDrawWidth;" in display_context_block
    assert "cgDC.ownerDrawHandleKey = &CG_OwnerDrawHandleKey;" in display_context_block

    assert menu_hits_for("CG_GAME_TYPE") == {
        "endscorenoteam.menu",
        "endscoreteam.menu",
        "end_scoreboard_ffa.menu",
        "end_scoreboard_race.menu",
        "end_scoreboard_rr.menu",
    }
    assert menu_hits_for("CG_GAME_TYPE_ICON") == {
        "hud.menu",
        "intro.menu",
        "min_hud.menu",
        "spectator.menu",
        "spectator_follow.menu",
    }
    assert menu_hits_for("CG_GAME_TYPE_MAP") == {"intro.menu"}


def test_gametype_icons_use_retail_tga_registration_path() -> None:
    newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    register_block = _block_from_marker(newdraw_source, "void CG_RegisterGameTypeIcons")
    icon_block = _block_from_marker(newdraw_source, "static qhandle_t CG_GameTypeIconShader")
    retail_icon_block = _text_between(
        hlil_source,
        "10034840    int32_t __fastcall sub_10034840",
        "10034900",
    )

    assert "static qhandle_t cgGameTypeIconShaders[GT_MAX_GAME_TYPE];" in newdraw_source
    assert 'memset( cgGameTypeIconShaders, 0, sizeof( cgGameTypeIconShaders ) );' in register_block

    for expected in (
        '"ui/assets/hud/ffa.tga"',
        '"ui/assets/hud/duel.tga"',
        '"ui/assets/hud/race.tga"',
        '"ui/assets/hud/tdm.tga"',
        '"ui/assets/hud/ca.tga"',
        '"ui/assets/hud/ctf.tga"',
        '"ui/assets/hud/1f.tga"',
        '"ui/assets/hud/har.tga"',
        '"ui/assets/hud/ft.tga"',
        '"ui/assets/hud/dom.tga"',
        '"ui/assets/hud/ad.tga"',
        '"ui/assets/hud/rr.tga"',
    ):
        assert expected in register_block

    for expected in (
        "else if (eax_2 != 0xb)",
        "if (eax_2 != 0xc)",
        "eax = data_10a5f328",
    ):
        assert expected in retail_icon_block

    assert "cgGameTypeIconShaders[GT_OBELISK] = cgGameTypeIconShaders[GT_FFA];" in register_block

    for stale in (
        ".png",
        '"ui/assets/hud/flag.png"',
        'cgGameTypeIconShaders[GT_OBELISK] = trap_R_RegisterShaderNoMip( "ui/assets/hud/dom.tga" );',
    ):
        assert stale not in newdraw_source

    assert "return cgGameTypeIconShaders[gametype];" in icon_block
    assert "CG_RegisterGameTypeIcons();" in main_source


def test_first_twenty_limit_count_map_and_vote_draws_match_retail_origins() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    capfrag_block = _block_from_marker(source, "static void CG_DrawCapFragLimit")
    race_limit_block = _block_from_marker(source, "static int CG_GetRaceCapFragLimitValue")
    count_block = _block_from_marker(source, "static int CG_CountActivePlayers")
    player_counts_block = _block_from_marker(source, "static void CG_DrawPlayerCounts")
    map_text_block = _block_from_marker(source, "static const char *CG_MapNameText")
    map_name_block = _block_from_marker(source, "static void CG_DrawMapName")
    map_display_block = _block_from_marker(source, "static void CG_GetMapDisplayName")
    detail_block = _block_from_marker(source, "static void CG_BuildIntroPanelDetailString")
    vote_gametype_block = _block_from_marker(source, "static void CG_DrawVoteGametype")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_capfrag = _text_between(
        hlil_source,
        "10032260    void sub_10032260",
        "100323d0",
    )
    retail_player_counts = _text_between(
        hlil_source,
        "10032f30    void sub_10032f30",
        "10033040",
    )
    retail_map_name = _text_between(
        hlil_source,
        "100343d0    int32_t sub_100343d0",
        "10034420",
    )
    retail_vote_gametype = _text_between(
        hlil_source,
        '100356f0    void* __convention("regparm") sub_100356f0',
        "10035790",
    )

    for expected in (
        "data_10a3ff38",
        "data_10a3ff48",
        "data_10a3ff54",
        "data_10a3ff34",
        "atoi(data_10a38f38 + 0x10a39420) - data_10abaad4",
        "if (arg5 == 1)",
        "else if (arg5 == 2)",
        "var_8 = fconvert.s(fconvert.t(arg1[1]))",
    ):
        assert expected in retail_capfrag

    for expected in (
        "case GT_RACE:",
        "limit = CG_GetRaceCapFragLimitValue();",
        "case GT_CTF:",
        "case GT_1FCTF:",
        "case GT_OBELISK:",
        "case GT_HARVESTER:",
        "limit = cgs.capturelimit;",
        "case GT_CLAN_ARENA:",
        "case GT_FREEZE:",
        "case GT_RED_ROVER:",
        "limit = cgs.roundlimit;",
        "case GT_DOMINATION:",
        "case GT_ATTACK_DEFEND:",
        "limit = cgs.scorelimit;",
        "limit = cgs.fraglimit;",
        'Com_sprintf( buffer, sizeof( buffer ), "%2i", limit );',
        "CG_AlignTextX( &x, buffer, scale, align );",
        "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );",
    ):
        assert expected in capfrag_block

    assert "remaining = cgs.racePointCount - ( progress->currentCheckpoint + 1 );" in race_limit_block
    assert "CG_HasObjectiveCountStat" not in capfrag_block
    assert "qhandle_t shader" not in capfrag_block
    assert "rect->y + rect->h" not in capfrag_block
    assert "CG_DrawCapFragLimit( &rect, scale, color, textStyle, align );" in ownerdraw_block

    for expected in (
        "if (*eax_1 != 0)",
        'eax_2, ecx = sub_100575e0("%d/%d Players")',
        "if (arg6 == 1)",
        "else if (arg6 == 2)",
        "fconvert.t(*(ebp + 4))",
    ):
        assert expected in retail_player_counts

    assert "for ( i = 0; i < cgs.maxclients && i < MAX_CLIENTS; i++ )" in count_block
    assert "cgs.clientinfo[i].infoValid" in count_block
    assert "cg.numScores" not in count_block
    assert "TEAM_SPECTATOR" not in count_block
    assert "CG_AlignTextX( &x, buffer, scale, align );" in player_counts_block
    assert "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );" in player_counts_block
    assert "rect->y + rect->h" not in player_counts_block
    assert "CG_DrawPlayerCounts(&rect, scale, color, textStyle, align);" in ownerdraw_block

    for expected in (
        "int32_t var_10 = data_10a3842c + 0x10a39420",
        "eax_1, ecx_1 = sub_100575e0(&data_10068de8)",
        "return sub_10008440(fconvert.s(fconvert.t(*arg1))",
        "fconvert.s(fconvert.t(arg1[1]))",
    ):
        assert expected in retail_map_name

    for expected in (
        "info = CG_ConfigString( CS_SERVERINFO );",
        "mapName = info ? Info_ValueForKey( info, SERVERINFO_KEY_MAPNAME ) : \"\";",
        "return mapName ? mapName : \"\";",
    ):
        assert expected in map_text_block
    assert "cgs.mapname" not in map_text_block

    assert "CG_Text_Paint( rect->x, rect->y, scale, color, CG_MapNameText(), 0, 0, textStyle );" in map_name_block
    assert "rect->y + rect->h" not in map_name_block
    assert "Q_strncpyz( buffer, CG_MapNameText(), bufferSize );" in map_display_block
    assert "CG_GetMapDisplayName( buffer, bufferSize );" in detail_block
    assert "CG_GetServerLocation" not in source
    assert "CG_BuildMapDisplayName" not in source
    assert "ARENA_INFO_KEY_LONGNAME" not in source
    assert 'CG_FindArenaLongNameInFile( "scripts/arenas.txt", mapName, buffer, bufferSize )' not in source
    assert "CG_DrawMapName( &rect, scale, color, textStyle );" in ownerdraw_block

    assert "if (arg1 == 0x13 || arg1 == 0x14 || arg1 == 0x15)" in retail_vote_gametype
    assert "arg2[1]) - fconvert.t(8.0)" in retail_vote_gametype
    assert 'CG_GetVoteSlotString( slot, "Gametype", buffer, sizeof( buffer ) );' in vote_gametype_block
    assert "CG_AlignTextX( &x, buffer, scale, align );" in vote_gametype_block
    assert "CG_Text_Paint( x, rect->y - 8.0f, scale, color, buffer, 0, 0, textStyle );" in vote_gametype_block
    assert "CG_GetTextPosition" not in vote_gametype_block
    assert "case CG_VOTEGAMETYPE1:" in ownerdraw_block
    assert "CG_DrawVoteGametype(&rect, scale, color, textStyle, 1, align);" in ownerdraw_block
    assert "case CG_VOTEGAMETYPE2:" in ownerdraw_block
    assert "CG_DrawVoteGametype(&rect, scale, color, textStyle, 2, align);" in ownerdraw_block


def test_vote_gametype_and_map_first_five_match_retail_dispatch_alignment_and_payloads() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    endgamevote_menu = (REPO_ROOT / "src" / "ui" / "endgamevote.menu").read_text(encoding="utf-8")
    all_menu_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (REPO_ROOT / "src" / "ui").glob("*.menu")
    )
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_ownerdraw_block = _block_from_marker(ghidra_source, "void FUN_1003b0f0")
    vote_gametype_block = _block_from_marker(source, "static void CG_DrawVoteGametype")
    vote_map_block = _block_from_marker(source, "static void CG_DrawVoteMapSlot")
    vote_cvar_name_block = _block_from_marker(source, "static void CG_BuildVoteSlotCvarName")
    vote_string_block = _block_from_marker(source, "static void CG_GetVoteSlotString")
    set_vote_cvar_block = _block_from_marker(servercmds_source, "static void CG_SetRotationVoteSlotCvar")
    parse_rotation_block = _block_from_marker(servercmds_source, "static void CG_ParseRotationVoteConfigStrings")
    value_block = _block_from_marker(source, "float CG_GetValue")
    width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
    key_block = _block_from_marker(main_source, "static qboolean CG_OwnerDrawHandleKey")
    display_context_block = _block_from_marker(main_source, "static void CG_InitDisplayContext")
    retail_vote_map = _text_between(
        hlil_source,
        '100355d0    void* __convention("regparm") sub_100355d0',
        "10035660",
    )
    retail_vote_gametype = _text_between(
        hlil_source,
        '100356f0    void* __convention("regparm") sub_100356f0',
        "10035790",
    )

    for ownerdraw, value in (
        ("CG_VOTEGAMETYPE1", "19"),
        ("CG_VOTEGAMETYPE2", "20"),
        ("CG_VOTEGAMETYPE3", "21"),
        ("CG_VOTEMAP1", "22"),
        ("CG_VOTEMAP2", "23"),
    ):
        assert any(line.split()[:3] == ["#define", ownerdraw, value] for line in menudef_source.splitlines())
        assert ownerdraw not in value_block
        assert ownerdraw not in width_block
        assert ownerdraw not in key_block

    for expected in (
        "case 0x13:",
        "case 0x14:",
        "case 0x15:",
        "FUN_100356f0(param_13,param_14,param_16,param_10);",
        "case 0x16:",
        "case 0x17:",
        "FUN_100355d0(param_13,param_14,param_16,param_10);",
    ):
        assert expected in retail_ownerdraw_block

    for expected in (
        "if (arg1 == 0x13 || arg1 == 0x14 || arg1 == 0x15)",
        "sub_1002e050(arg6, edx, result_1, fconvert.s(fconvert.t(arg3)))",
        "fconvert.t(arg2[1]) - fconvert.t(8.0)",
    ):
        assert expected in retail_vote_gametype

    for expected in (
        "if (arg1 == 0x16 || arg1 == 0x17 || arg1 == 0x18)",
        "sub_1002e050(arg6, edx, result_1, fconvert.s(fconvert.t(arg3)))",
        "fconvert.s(fconvert.t(*arg2))",
        "fconvert.s(fconvert.t(arg2[1]))",
    ):
        assert expected in retail_vote_map

    for expected in (
        'CG_GetVoteSlotString( slot, "Gametype", buffer, sizeof( buffer ) );',
        "x = rect->x;",
        "CG_AlignTextX( &x, buffer, scale, align );",
        "CG_Text_Paint( x, rect->y - 8.0f, scale, color, buffer, 0, 0, textStyle );",
    ):
        assert expected in vote_gametype_block

    for expected in (
        'CG_GetVoteSlotString( slot, "Map", buffer, sizeof( buffer ) );',
        "x = rect->x;",
        "CG_AlignTextX( &x, buffer, scale, align );",
        "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );",
    ):
        assert expected in vote_map_block

    for expected in (
        "CG_DrawVoteGametype(&rect, scale, color, textStyle, 1, align);",
        "CG_DrawVoteGametype(&rect, scale, color, textStyle, 2, align);",
        "CG_DrawVoteGametype(&rect, scale, color, textStyle, 3, align);",
        "CG_DrawVoteMapSlot(&rect, scale, color, textStyle, 1, align);",
        "CG_DrawVoteMapSlot(&rect, scale, color, textStyle, 2, align);",
    ):
        assert expected in ownerdraw_block

    for stale in (
        "CG_DrawVoteGametype(&rect, scale, color, textStyle, 1);",
        "CG_DrawVoteMapSlot(&rect, scale, color, textStyle, 1);",
        "CG_Text_Paint( rect->x, rect->y - 8.0f, scale, color, buffer, 0, 0, textStyle );",
        "CG_Text_Paint( rect->x, rect->y, scale, color, buffer, 0, 0, textStyle );",
        "CG_GetTextPosition",
    ):
        assert stale not in vote_gametype_block
        assert stale not in vote_map_block

    assert 'Com_sprintf( buffer, bufferSize, "ui_vote%s%i", suffix, slot );' in vote_cvar_name_block
    assert "if ( slot < 1 || slot > 3 ) {" in vote_string_block
    assert "trap_Cvar_VariableStringBuffer( name, buffer, bufferSize );" in vote_string_block
    assert 'Com_sprintf( key, sizeof( key ), "ui_vote%s%i", suffix, slot + 1 );' in set_vote_cvar_block
    assert 'CG_SetRotationVoteSlotCvar( slot, "Map", mapName );' in parse_rotation_block
    assert 'CG_SetRotationVoteSlotCvar( slot, "Gametype", voteGametype );' in parse_rotation_block

    for ownerdraw in ("CG_VOTEGAMETYPE1", "CG_VOTEGAMETYPE2", "CG_VOTEGAMETYPE3"):
        assert f"ownerdraw {ownerdraw}" in endgamevote_menu
    assert "ownerdraw CG_VOTEMAP1" not in all_menu_source
    assert "ownerdraw CG_VOTEMAP2" not in all_menu_source

    assert "cgDC.ownerDrawItem = &CG_OwnerDraw;" in display_context_block
    assert "cgDC.getValue = &CG_GetValue;" in display_context_block
    assert "cgDC.ownerDrawWidth = &CG_OwnerDrawWidth;" in display_context_block
    assert "cgDC.ownerDrawHandleKey = &CG_OwnerDrawHandleKey;" in display_context_block


def test_vote_name_and_count_next_five_match_retail_dispatch_alignment_and_payloads() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    endgamevote_menu = (REPO_ROOT / "src" / "ui" / "endgamevote.menu").read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_ownerdraw_block = _block_from_marker(ghidra_source, "void FUN_1003b0f0")
    vote_name_block = _block_from_marker(source, "static void CG_DrawVoteName")
    vote_count_block = _block_from_marker(source, "static void CG_DrawVoteCount")
    set_vote_cvar_block = _block_from_marker(servercmds_source, "static void CG_SetRotationVoteSlotCvar")
    parse_rotation_block = _block_from_marker(servercmds_source, "static void CG_ParseRotationVoteConfigStrings")
    value_block = _block_from_marker(source, "float CG_GetValue")
    width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
    key_block = _block_from_marker(main_source, "static qboolean CG_OwnerDrawHandleKey")
    display_context_block = _block_from_marker(main_source, "static void CG_InitDisplayContext")
    retail_vote_name = _text_between(
        hlil_source,
        '10035660    void* __convention("regparm") sub_10035660',
        "100356f0",
    )
    retail_vote_count = _text_between(
        hlil_source,
        "10035820    void __convention",
        "10035920",
    )

    for ownerdraw, value in (
        ("CG_VOTENAME1", "28"),
        ("CG_VOTENAME2", "29"),
        ("CG_VOTENAME3", "30"),
        ("CG_VOTECOUNT1", "31"),
        ("CG_VOTECOUNT2", "32"),
    ):
        assert any(line.split()[:3] == ["#define", ownerdraw, value] for line in menudef_source.splitlines())
        assert f"ownerdraw {ownerdraw}" in endgamevote_menu
        assert ownerdraw not in value_block
        assert ownerdraw not in width_block
        assert ownerdraw not in key_block

    for expected in (
        "case 0x1c:",
        "case 0x1d:",
        "case 0x1e:",
        "FUN_10035660(param_13,param_14,param_16,param_10);",
        "case 0x1f:",
        "case 0x20:",
        "FUN_10035820(&local_18,param_12,param_13,param_14,param_16,param_10);",
    ):
        assert expected in retail_ownerdraw_block

    for expected in (
        "if (arg1 == 0x1c || arg1 == 0x1d || arg1 == 0x1e)",
        "sub_1002e050(arg6, edx, result_1, fconvert.s(fconvert.t(arg3)))",
        "fconvert.s(fconvert.t(*arg2))",
        "fconvert.s(fconvert.t(arg2[1]))",
    ):
        assert expected in retail_vote_name

    for expected in (
        "if (arg3 == 0x1f || arg3 == 0x20 || arg3 == 0x21)",
        'eax_1, ecx_5 = sub_100575e0("Votes: %s")',
        "if (arg9 == 1)",
        "else if (arg9 == 2)",
        "fconvert.s(fconvert.t(arg4[1]))",
    ):
        assert expected in retail_vote_count

    for expected in (
        'CG_GetVoteSlotString( slot, "Name", buffer, sizeof( buffer ) );',
        'CG_GetVoteSlotString( slot, "Map", buffer, sizeof( buffer ) );',
        "x = rect->x;",
        "CG_AlignTextX( &x, buffer, scale, align );",
        "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );",
    ):
        assert expected in vote_name_block

    for expected in (
        'CG_GetVoteSlotString( slot, "Count", countText, sizeof( countText ) );',
        'Com_sprintf( buffer, sizeof( buffer ), "Votes: %s", countText );',
        "x = rect->x;",
        "CG_AlignTextX( &x, buffer, scale, align );",
        "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );",
    ):
        assert expected in vote_count_block

    for expected in (
        "CG_DrawVoteName(&rect, scale, color, textStyle, 1, align);",
        "CG_DrawVoteName(&rect, scale, color, textStyle, 2, align);",
        "CG_DrawVoteName(&rect, scale, color, textStyle, 3, align);",
        "CG_DrawVoteCount(&rect, scale, color, textStyle, 1, align);",
        "CG_DrawVoteCount(&rect, scale, color, textStyle, 2, align);",
    ):
        assert expected in ownerdraw_block

    for stale in (
        "CG_DrawVoteName(&rect, scale, color, textStyle, 1);",
        "CG_Text_Paint( rect->x, rect->y, scale, color, buffer, 0, 0, textStyle );",
        "CG_GetTextPosition",
    ):
        assert stale not in vote_name_block

    assert 'Com_sprintf( key, sizeof( key ), "ui_vote%s%i", suffix, slot + 1 );' in set_vote_cvar_block
    assert 'CG_SetRotationVoteSlotCvar( slot, "Name", voteName );' in parse_rotation_block
    assert 'CG_SetRotationVoteSlotCvar( slot, "Count", voteCount );' in parse_rotation_block

    assert "cgDC.ownerDrawItem = &CG_OwnerDraw;" in display_context_block
    assert "cgDC.getValue = &CG_GetValue;" in display_context_block
    assert "cgDC.ownerDrawWidth = &CG_OwnerDrawWidth;" in display_context_block
    assert "cgDC.ownerDrawHandleKey = &CG_OwnerDrawHandleKey;" in display_context_block


def test_vote_shot_count3_and_timer_match_retail_dispatch_assets_and_payloads() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    endgamevote_menu = (REPO_ROOT / "src" / "ui" / "endgamevote.menu").read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_ownerdraw_block = _block_from_marker(ghidra_source, "void FUN_1003b0f0")
    vote_shot_block = _block_from_marker(source, "static void CG_DrawVoteShot")
    vote_count_block = _block_from_marker(source, "static void CG_DrawVoteCount")
    vote_timer_block = _block_from_marker(source, "static void CG_DrawVoteTimer")
    set_vote_cvar_block = _block_from_marker(servercmds_source, "static void CG_SetRotationVoteSlotCvar")
    parse_rotation_block = _block_from_marker(servercmds_source, "static void CG_ParseRotationVoteConfigStrings")
    value_block = _block_from_marker(source, "float CG_GetValue")
    width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
    key_block = _block_from_marker(main_source, "static qboolean CG_OwnerDrawHandleKey")
    display_context_block = _block_from_marker(main_source, "static void CG_InitDisplayContext")
    retail_vote_shot = _text_between(
        hlil_source,
        "10035790    int32_t __convention",
        "10035820",
    )
    retail_vote_count = _text_between(
        hlil_source,
        "10035820    void __convention",
        "10035920",
    )
    retail_vote_timer = _text_between(
        hlil_source,
        "10035920    void sub_10035920",
        "10035a10",
    )

    for ownerdraw, value in (
        ("CG_VOTESHOT1", "25"),
        ("CG_VOTESHOT2", "26"),
        ("CG_VOTESHOT3", "27"),
        ("CG_VOTECOUNT3", "33"),
        ("CG_VOTETIMER", "34"),
    ):
        assert any(line.split()[:3] == ["#define", ownerdraw, value] for line in menudef_source.splitlines())
        assert f"ownerdraw {ownerdraw}" in endgamevote_menu
        assert ownerdraw not in value_block
        assert ownerdraw not in width_block
        assert ownerdraw not in key_block

    for expected in (
        "case 0x19:",
        "case 0x1a:",
        "case 0x1b:",
        "FUN_10035790();",
        "case 0x21:",
        "FUN_10035820(&local_18,param_12,param_13,param_14,param_16,param_10);",
        "case 0x22:",
        "FUN_10035920(param_13,param_14,param_16,param_10);",
    ):
        assert expected in retail_ownerdraw_block

    for expected in (
        "if (arg1 == 0x19 || arg1 == 0x1a || arg1 == 0x1b)",
        'eax_2 = "default"',
        'sub_100575e0("levelshots/preview/%s")',
        "return sub_100126a0(fconvert.s(fconvert.t(*arg2)))",
    ):
        assert expected in retail_vote_shot

    for expected in (
        "if (arg3 == 0x1f || arg3 == 0x20 || arg3 == 0x21)",
        'eax_1, ecx_5 = sub_100575e0("Votes: %s")',
        "if (arg9 == 1)",
        "else if (arg9 == 2)",
        "fconvert.s(fconvert.t(arg4[1]))",
    ):
        assert expected in retail_vote_count

    for expected in (
        "data_10a3ffc4 - data_10a9c1ec + 0x4e20",
        '"Voting has ended."',
        '"Voting ends in %i second."',
        '"Voting ends in %i seconds."',
        "if (eax_5 == 1)",
        "else if (eax_5 == 2)",
        "fconvert.s(fconvert.t(ebx[1]))",
    ):
        assert expected in retail_vote_timer

    for expected in (
        "if ( slot < 1 || slot > 3 ) {",
        'CG_GetVoteSlotString( slot, "Shot", previewToken, sizeof( previewToken ) );',
        'Q_strncpyz( previewToken, "default", sizeof( previewToken ) );',
        'Com_sprintf( path, sizeof( path ), "levelshots/preview/%s", previewToken );',
        "cache = &cg_voteShotCache[slot - 1];",
        "cache->handle = trap_R_RegisterShaderNoMip( path );",
        "CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cache->handle );",
    ):
        assert expected in vote_shot_block

    for expected in (
        'CG_GetVoteSlotString( slot, "Count", countText, sizeof( countText ) );',
        'Com_sprintf( buffer, sizeof( buffer ), "Votes: %s", countText );',
        "CG_AlignTextX( &x, buffer, scale, align );",
        "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );",
    ):
        assert expected in vote_count_block

    for expected in (
        "remaining = ( cgs.voteTime - cg.time + 20000 ) / 1000;",
        'Q_strncpyz( buffer, "Voting has ended.", sizeof( buffer ) );',
        'Com_sprintf( buffer, sizeof( buffer ), "Voting ends in %i second.", remaining );',
        'Com_sprintf( buffer, sizeof( buffer ), "Voting ends in %i seconds.", remaining );',
        "CG_AlignTextX( &x, buffer, scale, align );",
        "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );",
    ):
        assert expected in vote_timer_block

    for expected in (
        "CG_DrawVoteShot(&rect, 1);",
        "CG_DrawVoteShot(&rect, 2);",
        "CG_DrawVoteShot(&rect, 3);",
        "CG_DrawVoteCount(&rect, scale, color, textStyle, 3, align);",
        "CG_DrawVoteTimer(&rect, scale, color, textStyle, align);",
    ):
        assert expected in ownerdraw_block

    for stale in (
        "VOTE_TIME - ( cg.time - cgs.voteTime ) + 999",
        '"Vote %is"',
        "CG_GetTextPosition",
    ):
        assert stale not in vote_timer_block
        assert stale not in vote_count_block

    assert 'Com_sprintf( key, sizeof( key ), "ui_vote%s%i", suffix, slot + 1 );' in set_vote_cvar_block
    assert 'CG_SetRotationVoteSlotCvar( slot, "Shot", voteShot );' in parse_rotation_block
    assert 'CG_SetRotationVoteSlotCvar( slot, "Count", voteCount );' in parse_rotation_block
    assert 'trap_Cvar_Set( "ui_voteactive", cgs.voteTime ? "1" : "0" );' in servercmds_source
    assert 'trap_Cvar_Set( "ui_votestring", cgs.voteString );' in servercmds_source

    assert "cgDC.ownerDrawItem = &CG_OwnerDraw;" in display_context_block
    assert "cgDC.getValue = &CG_GetValue;" in display_context_block
    assert "cgDC.ownerDrawWidth = &CG_OwnerDrawWidth;" in display_context_block
    assert "cgDC.ownerDrawHandleKey = &CG_OwnerDrawHandleKey;" in display_context_block


def test_second_twenty_vote_and_local_player_ownerdraws_match_retail_wiring() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    vote_gametype_block = _block_from_marker(source, "static void CG_DrawVoteGametype")
    vote_map_block = _block_from_marker(source, "static void CG_DrawVoteMapSlot")
    vote_name_block = _block_from_marker(source, "static void CG_DrawVoteName")
    vote_shot_block = _block_from_marker(source, "static void CG_DrawVoteShot")
    vote_count_block = _block_from_marker(source, "static void CG_DrawVoteCount")
    vote_timer_block = _block_from_marker(source, "static void CG_DrawVoteTimer")
    spectator_block = _block_from_marker(source, "static void CG_DrawSpectatorMessages")
    armor_icon_block = _block_from_marker(source, "static void CG_DrawPlayerArmorIcon")
    armor_value_block = _block_from_marker(source, "static void CG_DrawPlayerArmorValue")
    player_head_block = _block_from_marker(source, "static void CG_DrawPlayerHead")
    player_model_block = _block_from_marker(source, "static void CG_DrawPlayerModel")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_vote_map = _text_between(
        hlil_source,
        '100355d0    void* __convention("regparm") sub_100355d0',
        "10035660",
    )
    retail_vote_name = _text_between(
        hlil_source,
        '10035660    void* __convention("regparm") sub_10035660',
        "100356f0",
    )
    retail_vote_shot = _text_between(
        hlil_source,
        "10035790    int32_t __convention",
        "10035820",
    )
    retail_vote_count = _text_between(
        hlil_source,
        "10035820    void __convention",
        "10035920",
    )
    retail_vote_timer = _text_between(
        hlil_source,
        "10035920    void sub_10035920",
        "10035a10",
    )
    retail_armor_value = _text_between(
        hlil_source,
        "1002e500    void __convention",
        "1002e660",
    )
    retail_armor_icon = _text_between(
        hlil_source,
        "1002e3f0    void __convention",
        "1002e500",
    )
    retail_player_head = _text_between(
        hlil_source,
        "1002f950    int80_t sub_1002f950",
        "1002fc70",
    )
    retail_player_model = _text_between(
        hlil_source,
        "10034980    int32_t __convention",
        "10034a00",
    )
    retail_spectator = _text_between(
        hlil_source,
        "10034d70    int32_t __fastcall sub_10034d70",
        "100350c0",
    )

    assert "if (arg1 == 0x13 || arg1 == 0x14 || arg1 == 0x15)" in hlil_source
    assert "CG_DrawVoteGametype(&rect, scale, color, textStyle, 3, align);" in ownerdraw_block
    assert "CG_GetTextPosition" not in vote_gametype_block

    for expected in (
        "if (arg1 == 0x16 || arg1 == 0x17 || arg1 == 0x18)",
        "fconvert.s(fconvert.t(*arg2))",
        "fconvert.s(fconvert.t(arg2[1]))",
    ):
        assert expected in retail_vote_map
    assert 'CG_GetVoteSlotString( slot, "Map", buffer, sizeof( buffer ) );' in vote_map_block
    assert "CG_AlignTextX( &x, buffer, scale, align );" in vote_map_block
    assert "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );" in vote_map_block
    assert "CG_GetTextPosition" not in vote_map_block

    assert "if (arg1 == 0x1c || arg1 == 0x1d || arg1 == 0x1e)" in retail_vote_name
    assert 'CG_GetVoteSlotString( slot, "Name", buffer, sizeof( buffer ) );' in vote_name_block
    assert "CG_AlignTextX( &x, buffer, scale, align );" in vote_name_block
    assert "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );" in vote_name_block
    assert "CG_GetTextPosition" not in vote_name_block

    for expected in (
        "if (arg1 == 0x19 || arg1 == 0x1a || arg1 == 0x1b)",
        'eax_2 = "default"',
        'sub_100575e0("levelshots/preview/%s")',
    ):
        assert expected in retail_vote_shot
    assert 'Q_strncpyz( previewToken, "default", sizeof( previewToken ) );' in vote_shot_block
    assert 'Com_sprintf( path, sizeof( path ), "levelshots/preview/%s", previewToken );' in vote_shot_block

    for expected in (
        "if (arg3 == 0x1f || arg3 == 0x20 || arg3 == 0x21)",
        'eax_1, ecx_5 = sub_100575e0("Votes: %s")',
        "if (arg9 == 1)",
        "else if (arg9 == 2)",
        "fconvert.s(fconvert.t(arg4[1]))",
    ):
        assert expected in retail_vote_count
    assert 'Com_sprintf( buffer, sizeof( buffer ), "Votes: %s", countText );' in vote_count_block
    assert "CG_AlignTextX( &x, buffer, scale, align );" in vote_count_block
    assert "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );" in vote_count_block
    assert "CG_GetTextPosition" not in vote_count_block

    for expected in (
        "data_10a3ffc4 - data_10a9c1ec + 0x4e20",
        '"Voting has ended."',
        '"Voting ends in %i second."',
        '"Voting ends in %i seconds."',
        "if (eax_5 == 1)",
        "else if (eax_5 == 2)",
    ):
        assert expected in retail_vote_timer
    assert "remaining = ( cgs.voteTime - cg.time + 20000 ) / 1000;" in vote_timer_block
    assert "CG_AlignTextX( &x, buffer, scale, align );" in vote_timer_block
    assert "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );" in vote_timer_block
    assert "CG_GetTextPosition" not in vote_timer_block

    for expected in (
        "case CG_VOTEMAP1:",
        "CG_DrawVoteMapSlot(&rect, scale, color, textStyle, 1, align);",
        "case CG_VOTESHOT1:",
        "CG_DrawVoteShot(&rect, 1);",
        "case CG_VOTENAME1:",
        "CG_DrawVoteName(&rect, scale, color, textStyle, 1, align);",
        "case CG_VOTECOUNT1:",
        "CG_DrawVoteCount(&rect, scale, color, textStyle, 1, align);",
        "case CG_VOTETIMER:",
        "CG_DrawVoteTimer(&rect, scale, color, textStyle, align);",
    ):
        assert expected in ownerdraw_block

    assert "Round In Progress" in retail_spectator
    assert "SPECTATOR MODE" in spectator_block
    assert "CG_DrawSpectatorMessages( &rect, scale, color, textStyle );" in ownerdraw_block

    assert "data_10a5f418" in retail_armor_icon
    assert "data_10a5f414" in retail_armor_icon
    assert "CG_DrawPlayerArmorIcon( &rect, ownerDrawFlags & CG_SHOW_2DONLY );" in ownerdraw_block
    assert "CG_DrawPlayerArmorIcon( &rect, qtrue );" in ownerdraw_block
    assert "cgs.media.armorIcon" in armor_icon_block
    assert "cgs.media.armorModel" in armor_icon_block

    for expected in (
        "if (arg1 != 0)",
        "if (arg8 == 1)",
        "else if (arg8 == 2)",
        "fconvert.t(ebx[1]) + float.t(var_4)",
    ):
        assert expected in retail_armor_value
    assert "value = ps->stats[STAT_ARMOR];" in armor_value_block
    assert "CG_AlignTextX( &x, num, scale, align );" in armor_value_block
    assert "y = rect->y + CG_Text_Height( num, scale, 0 );" in armor_value_block
    assert "CG_DrawPlayerArmorValue( &rect, scale, color, shader, textStyle, align );" in ownerdraw_block

    assert "CG_DrawHead( x, rect->y, rect->w, rect->h, cg.snap->ps.clientNum, angles );" in player_head_block
    assert "return sub_10009490" in retail_player_head
    assert "CG_DrawPlayerHead( &rect, ownerDrawFlags & CG_SHOW_2DONLY );" in ownerdraw_block

    assert "VectorSet( previewAngles, 5.0f, 210.0f, 0.0f );" in player_model_block
    assert "0x43520000" in retail_player_model
    assert "CG_DrawPlayerModel( &rect );" in ownerdraw_block


def test_team_pickup_ownerdraws_use_team_scorestats_payload() -> None:
    newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
    local_source = CG_LOCAL.read_text(encoding="utf-8")
    block = _block_from_marker(newdraw_source, "static qboolean CG_BuildTeamPickupText")

    assert "int\t\tfieldCount;" in local_source or "int\t\t\tfieldCount;" in local_source
    assert "cg.teamScoreStats.valid" in block
    assert "cg.teamScoreStats.fieldCount <= 0" in block
    assert "statIndex >= cg.teamScoreStats.fieldCount" in block
    assert "cg.teamScoreStats.values[teamIndex][statIndex]" in block

    for stale in (
        "CG_TeamMapPickupProxyTotal",
        "legacy map-pickup proxy",
        "currently available proxy data",
    ):
        assert stale not in newdraw_source


def test_placement_frags_use_retail_team_family_kill_rows() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    helper_block = _block_from_marker(source, "static int CG_GetPlacementFragCount")
    placement_block = _block_from_marker(source, "static qboolean CG_BuildPlacementMetricText")

    for expected in (
        "case GT_TEAM:",
        "case GT_CTF:",
        "case GT_1FCTF:",
        "case GT_HARVESTER:",
        "case GT_DOMINATION:",
        "case GT_ATTACK_DEFEND:",
        "case GT_FREEZE:",
        "return score->kills;",
        "return score->score;",
    ):
        assert expected in helper_block

    assert "case CG_1ST_PLYR_FRAGS:" in placement_block
    assert 'Com_sprintf( buffer, bufferSize, "%i", CG_GetPlacementFragCount( score ) );' in placement_block
