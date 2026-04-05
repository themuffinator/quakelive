"""Guard retail-backed cgame ownerdraw text against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"


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


def test_game_limit_uses_retail_limit_strings() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    block = _block_from_marker(source, "static void CG_DrawGameLimit")

    for expected in (
        "Cap Limit: %d",
        "Frag Limit: %d",
        "Round Limit: %d",
        "Score Limit: %d",
    ):
        assert expected in block

    for stale in (
        "Time %i",
        "Captures %i",
        "Score %i",
        "Frags %i",
        "Mercy %i",
    ):
        assert stale not in block


def test_local_time_uses_retail_date_format() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    block = _block_from_marker(source, "static void CG_DrawLocalTime")

    assert "static const char *cgMonthAbbrev[12]" in source
    assert '%02d:%02d (%s %02d, %d)' in block
    assert '%02i:%02i' not in block


def test_spectator_messages_use_retail_copy_family() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    block = _block_from_marker(source, "static void CG_DrawSpectatorMessages")

    for expected in (
        "Round In Progress",
        "SPECTATOR MODE",
        "Press mouse button 1 to cycle through players",
        "waiting to play",
        "press ESC and use the JOIN buttons",
        "to enter the game",
    ):
        assert expected in block

    for stale in (
        "FOLLOWING %s",
        "FREE SPECTATE",
        "Press FIRE to cycle, JUMP for free camera",
        "Press FIRE to follow a player",
        "press ESC and use the JOIN menu to play",
    ):
        assert stale not in block


def test_level_timer_uses_retail_clock_format() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    block = _block_from_marker(source, "static void CG_DrawLevelTimer")

    assert '%i:%i%i' in block
    assert '%02i:%02i' not in block


def test_intro_panel_draws_use_retail_map_panel_shapes() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    game_type_map = _block_from_marker(source, "static void CG_DrawGameTypeMap")
    match_details = _block_from_marker(source, "static void CG_DrawMatchDetails")
    phase_label = _block_from_marker(source, "static const char *CG_GetMatchDetailsPhaseLabel")

    assert 'CG_GetMapDisplayName( mapName, sizeof( mapName ) );' in game_type_map
    assert '%s - %s", CG_GameTypeString(), mapName' in game_type_map
    assert 'CG_GetServerLocation' not in game_type_map
    assert '%s - %s - %s' not in game_type_map

    assert 'CG_GetMatchDetailsPhaseLabel()' in match_details
    assert '%s - %s - %s' in match_details
    assert '%s - %s - %s - %s' not in match_details
    assert 'CG_GetServerLocation' not in match_details

    for expected in (
        'MATCH WARMUP',
        'MATCH IN PROGRESS',
        'MATCH SUMMARY',
    ):
        assert expected in phase_label


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


def test_match_status_uses_retail_status_text_family() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    status_text = _block_from_marker(source, "const char *CG_GetGameStatusText()")
    status_helper = _block_from_marker(source, "static const char *CG_GetMatchStatusText")
    draw_match_status = _block_from_marker(source, "static void CG_DrawMatchStatus")

    assert "case GT_SINGLE_PLAYER:" in status_text
    assert "case GT_RED_ROVER:" in status_text
    assert "cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR" in status_text
    assert '"Teams are tied at %i"' in status_text
    assert '"^1Red^7 leads ^4Blue^7, %i to %i"' in status_text
    assert '"^4Blue^7 leads ^1Red^7, %i to %i"' in status_text
    assert '"Red leads Blue, %i to %i"' not in status_text
    assert '"Blue leads Red, %i to %i"' not in status_text
    assert "cgs.gametype < GT_TEAM" not in status_text

    assert 'phase = "MATCH SUMMARY";' in status_helper
    assert 'phase = "MATCH WARMUP";' in status_helper
    assert 'phase = "MATCH IN PROGRESS";' in status_helper
    assert "if ( !status || !status[0] )" in status_helper
    assert 'Com_sprintf( buffer, sizeof( buffer ), "%s - %s", phase, status );' in status_helper

    assert "statusText = CG_GetMatchStatusText();" in draw_match_status
    assert 'Com_sprintf( buffer, sizeof( buffer ), "%s - %s", CG_GetMatchStateLabel(), CG_GetGameStatusText() );' not in draw_match_status


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
    token_map = _block_from_marker(source, "static weapon_t CG_StartingWeaponFromToken")
    preview_mask = _block_from_marker(source, "static unsigned int CG_GetStartingWeaponPreviewMask")
    block = _block_from_marker(source, "static void CG_DrawStartingWeapons")

    assert "static const cgStartingWeaponInfo_t cgStartingWeaponIcons" in source
    assert "CG_ConfigString( CS_LOADOUT_MASK )" in preview_mask
    assert '"g_startingWeapons"' in preview_mask

    assert "CG_StartingWeaponFromToken( cg_weaponPrimaryQueued.string )" in block
    assert 'CG_Text_Paint( plusX, plusY, scale, color, "+", 0, 0, textStyle );' in block
    assert "CG_DrawPic( rect->x + xOffset, rect->y, rect->w, rect->h, shader );" in block
    assert "CG_DrawPic( rect->x + xOffset + rect->w, rect->y, rect->w, rect->h, shader );" in block

    for expected in (
        '"gauntlet"',
        '"rocket_launcher"',
        '"grappling_hook"',
        '"heavy_machinegun"',
    ):
        assert expected in token_map

    for stale in (
        "Factory loadouts active",
        "Default loadout",
        "Q_strcat( buffer",
        "CG_ResolveWeaponName( weapon )",
    ):
        assert stale not in block


def test_gametype_icons_use_retail_tga_registration_path() -> None:
    newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    register_block = _block_from_marker(newdraw_source, "void CG_RegisterGameTypeIcons")
    icon_block = _block_from_marker(newdraw_source, "static qhandle_t CG_GameTypeIconShader")

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

    for stale in (
        ".png",
        '"ui/assets/hud/flag.png"',
    ):
        assert stale not in newdraw_source

    assert "return cgGameTypeIconShaders[gametype];" in icon_block
    assert "CG_RegisterGameTypeIcons();" in main_source


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
