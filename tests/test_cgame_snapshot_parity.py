"""Guard retail-backed cgame snapshot refresh behavior against source drift."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_PREDICT = REPO_ROOT / "src" / "code" / "cgame" / "cg_predict.c"
CG_PLAYERSTATE = REPO_ROOT / "src" / "code" / "cgame" / "cg_playerstate.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CG_SNAPSHOT = REPO_ROOT / "src" / "code" / "cgame" / "cg_snapshot.c"
CGAME_MAPPING = REPO_ROOT / "docs" / "reverse-engineering" / "cgame-mapping.md"
CGAME_BG_PLAN = REPO_ROOT / "docs" / "reverse-engineering" / "cgame-bg-parity-implementation-plan.md"
CGAME_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "cgame.json"


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


def _cgame_symbol(normalized_name: str) -> dict[str, object]:
    data = json.loads(CGAME_SYMBOL_MAP.read_text(encoding="utf-8"))
    matches = [
        entry
        for entry in data["functions"]
        if entry.get("normalized_name") == normalized_name
    ]
    assert len(matches) == 1, normalized_name
    return matches[0]


def test_snapshot_refresh_queue_consumes_retail_model_override_path() -> None:
    source = CG_SNAPSHOT.read_text(encoding="utf-8")
    refresh_block = _block_from_marker(source, "static void CG_RefreshClientInfoContext")
    queue_block = _block_from_marker(source, "void CG_QueueClientInfoContextRefresh")
    initial_block = _block_from_marker(source, "void CG_SetInitialSnapshot")
    transition_block = _block_from_marker(source, "static void CG_TransitionSnapshot")

    assert "CG_ApplyModelOverrides();" in refresh_block
    assert "CG_LoadDeferredPlayers();" in refresh_block
    assert "CG_NewClientInfo( i );" not in refresh_block
    assert "if ( i == cg.clientNum ) {" not in refresh_block

    assert "cg_refreshClientInfoContextQueued = qtrue;" in queue_block
    assert "if ( cg.snap ) {" not in queue_block
    assert "CG_RefreshClientInfoContext();" not in queue_block

    assert "CG_RefreshClientInfoContext();" not in initial_block
    assert "CG_RefreshClientInfoContext();" in transition_block
    assert "ps->clientNum != ops->clientNum" not in transition_block
    assert "ps->persistant[ PERS_TEAM ] != ops->persistant[ PERS_TEAM ]" not in transition_block


def test_predict_player_state_queues_retail_follow_and_team_context_changes() -> None:
    source = CG_PREDICT.read_text(encoding="utf-8")
    helper_block = _block_from_marker(source, "static void CG_UpdateClientInfoContext")
    predict_block = _block_from_marker(source, "void CG_PredictPlayerState")

    for expected in (
        "( cg.predictedPlayerState.pm_flags & PMF_FOLLOW ) != 0",
        "clientNum = cg.predictedPlayerState.clientNum;",
        "team = cg.predictedPlayerState.persistant[ PERS_TEAM ];",
        "cg_clientInfoContextFollow != following",
        "cg_clientInfoContextTeam != team",
        "following && cg_clientInfoContextClientNum != clientNum",
        "CG_QueueClientInfoContextRefresh();",
    ):
        assert expected in helper_block

    assert "cg_clientInfoContextValid = qfalse;" in predict_block
    assert "CG_UpdateClientInfoContext();" in predict_block


def test_predict_and_snapshot_paths_keep_retail_interpolate_and_transition_gates() -> None:
    predict_source = CG_PREDICT.read_text(encoding="utf-8")
    snapshot_source = CG_SNAPSHOT.read_text(encoding="utf-8")
    predict_block = _block_from_marker(predict_source, "void CG_PredictPlayerState")
    transition_block = _block_from_marker(snapshot_source, "static void CG_TransitionSnapshot")

    assert "if ( cg.demoPlayback || (cg.snap->ps.pm_flags & PMF_FOLLOW) ) {" in predict_block
    assert "CG_InterpolatePlayerState( qfalse );" in predict_block
    assert "if ( cg_nopredict.integer || cg_synchronousClients.integer ) {" in predict_block
    assert "CG_InterpolatePlayerState( qtrue );" in predict_block
    assert "CG_TransitionPlayerState( &cg.predictedPlayerState, &oldPlayerState );" in predict_block
    assert predict_block.index("CG_UpdateClientInfoContext();") < predict_block.index("if ( cg.demoPlayback || (cg.snap->ps.pm_flags & PMF_FOLLOW) ) {")
    assert predict_block.index("CG_InterpolatePlayerState( qfalse );") < predict_block.index("if ( cg_nopredict.integer || cg_synchronousClients.integer ) {")
    assert predict_block.index("CG_InterpolatePlayerState( qtrue );") < predict_block.index("CG_TransitionPlayerState( &cg.predictedPlayerState, &oldPlayerState );")

    assert "if ( cg.demoPlayback || (cg.snap->ps.pm_flags & PMF_FOLLOW)" in transition_block
    assert "|| cg_nopredict.integer || cg_synchronousClients.integer ) {" in transition_block
    assert "CG_TransitionPlayerState( ps, ops );" in transition_block


def test_predict_player_state_replays_commands_through_retail_pmove_pipeline() -> None:
    source = CG_PREDICT.read_text(encoding="utf-8")
    predict_block = _block_from_marker(source, "void CG_PredictPlayerState")

    for expected in (
        "cg.hyperspace = qfalse;",
        "cg.projectileNudgeActive = qfalse;",
        "cg.projectileNudgeMsec = 0;",
        "cg.projectileNudgeCommandTime = 0;",
        "VectorClear( cg.projectileNudgeOrigin );",
        "cg_pmove.ps = &cg.predictedPlayerState;",
        "memcpy( &localPmoveSettings, &cg_pmoveSettings, sizeof( localPmoveSettings ) );",
        "cg_pmove.pmoveSettings = &localPmoveSettings;",
        "cg_pmove.trace = CG_Trace;",
        "cg_pmove.pointcontents = CG_PointContents;",
        "cg_pmove.tracemask = MASK_PLAYERSOLID & ~CONTENTS_BODY;",
        "cg_pmove.tracemask = MASK_PLAYERSOLID;",
        "cg_pmove.tracemask &= ~CONTENTS_BODY;",
        "cg_pmove.noFootsteps = ( cgs.dmflags & DF_NO_FOOTSTEPS ) > 0;",
        "trap_GetUserCmd( cmdNum, &oldestCmd );",
        "oldestCmd.serverTime > cg.snap->ps.commandTime",
        "trap_GetUserCmd( current, &latestCmd );",
        "CG_UpdatePredictedRailFire( &latestCmd );",
        "if ( cg.nextSnap && !cg.nextFrameTeleport && !cg.thisFrameTeleport ) {",
        "trap_Cvar_Set(\"pmove_msec\", \"8\");",
        "trap_Cvar_Set(\"pmove_msec\", \"33\");",
        "cg_pmove.pmove_fixed = pmove_fixed.integer;// | cg_pmove_fixed.integer;",
        "cg_pmove.pmove_msec = pmove_msec.integer;",
        "trap_GetUserCmd( cmdNum, &cg_pmove.cmd );",
        "PM_UpdateViewAngles( cg_pmove.ps, &cg_pmove.cmd );",
        "cg_pmove.cmd.serverTime <= cg.predictedPlayerState.commandTime",
        "cg_pmove.cmd.serverTime > latestCmd.serverTime",
        "cg_pmove.gauntletHit = qfalse;",
        "cg_pmove.cmd.serverTime = ((cg_pmove.cmd.serverTime + pmove_msec.integer-1) / pmove_msec.integer) * pmove_msec.integer;",
        "Pmove (&cg_pmove);",
        "CG_UpdateStepChange();",
        "CG_LocalProjectileNudge( nudgedOrigin, &nudgedTime );",
        "moved = qtrue;",
        "CG_TouchTriggerPrediction();",
        "//CG_CheckChangedPredictableEvents(&cg.predictedPlayerState);",
        'CG_Printf( "not moved\\n" );',
        "CG_TransitionPlayerState( &cg.predictedPlayerState, &oldPlayerState );",
    ):
        assert expected in predict_block

    assert predict_block.index("CG_UpdatePredictedRailFire( &latestCmd );") < predict_block.index(
        "if ( cg.nextSnap && !cg.nextFrameTeleport && !cg.thisFrameTeleport ) {"
    )
    assert predict_block.index('trap_Cvar_Set("pmove_msec", "8");') < predict_block.index(
        "cg_pmove.pmove_fixed = pmove_fixed.integer;// | cg_pmove_fixed.integer;"
    )
    assert predict_block.index("trap_GetUserCmd( cmdNum, &cg_pmove.cmd );") < predict_block.index(
        "PM_UpdateViewAngles( cg_pmove.ps, &cg_pmove.cmd );"
    )
    assert predict_block.index("PM_UpdateViewAngles( cg_pmove.ps, &cg_pmove.cmd );") < predict_block.index(
        "cg_pmove.cmd.serverTime <= cg.predictedPlayerState.commandTime"
    )
    assert predict_block.index("cg_pmove.cmd.serverTime <= cg.predictedPlayerState.commandTime") < predict_block.index(
        "cg_pmove.cmd.serverTime > latestCmd.serverTime"
    )
    assert predict_block.index("cg_pmove.gauntletHit = qfalse;") < predict_block.index("Pmove (&cg_pmove);")
    assert predict_block.index("Pmove (&cg_pmove);") < predict_block.index("CG_UpdateStepChange();")
    assert predict_block.index("CG_UpdateStepChange();") < predict_block.index(
        "CG_LocalProjectileNudge( nudgedOrigin, &nudgedTime );"
    )
    assert predict_block.index("CG_LocalProjectileNudge( nudgedOrigin, &nudgedTime );") < predict_block.index(
        "moved = qtrue;"
    )
    assert predict_block.index("moved = qtrue;") < predict_block.index("CG_TouchTriggerPrediction();")
    assert predict_block.index("if ( !moved ) {") < predict_block.rindex(
        "CG_AdjustPositionForMover( cg.predictedPlayerState.origin,"
    )
    assert predict_block.rindex("CG_AdjustPositionForMover( cg.predictedPlayerState.origin,") < predict_block.index(
        "CG_TransitionPlayerState( &cg.predictedPlayerState, &oldPlayerState );"
    )


def test_touch_item_prediction_keeps_retail_grab_event_and_weapon_side_effects() -> None:
    source = CG_PREDICT.read_text(encoding="utf-8")
    touch_block = _block_from_marker(source, "static void CG_TouchItem")

    for expected in (
        "if ( !cg_predictItems.integer ) {",
        "if ( !BG_PlayerTouchesItem( &cg.predictedPlayerState, &cent->currentState, cg.time ) ) {",
        "if ( cent->miscTime == cg.time ) {",
        "if ( !BG_CanItemBeGrabbed( cgs.gametype, cg.time, &cent->currentState, &cg.predictedPlayerState ) ) {",
        "item = &bg_itemlist[ cent->currentState.modelindex ];",
        "if ( CG_ItemSkipsPredictablePickup( item ) ) {",
        "if( cgs.gametype == GT_1FCTF ) {",
        "if( ( cgs.gametype == GT_CTF || cgs.gametype == GT_HARVESTER ) && BG_IsRedBlueFlagItem( item ) ) {",
        "BG_AddPredictableEventToPlayerstate( EV_ITEM_PICKUP, cent->currentState.modelindex , &cg.predictedPlayerState);",
        "cent->currentState.eFlags |= EF_NODRAW;",
        "cent->miscTime = cg.time;",
        "if ( item->giType == IT_WEAPON ) {",
        "weapon = BG_WeaponForItemTag( item->giTag );",
        "cg.predictedPlayerState.stats[ STAT_WEAPONS ] |= 1 << weapon;",
        "cg.predictedPlayerState.ammo[ weapon ] = 1;",
    ):
        assert expected in touch_block

    assert touch_block.index("if ( !cg_predictItems.integer ) {") < touch_block.index(
        "if ( !BG_PlayerTouchesItem( &cg.predictedPlayerState, &cent->currentState, cg.time ) ) {"
    )
    assert touch_block.index("if ( !BG_PlayerTouchesItem(") < touch_block.index("if ( cent->miscTime == cg.time ) {")
    assert touch_block.index("if ( cent->miscTime == cg.time ) {") < touch_block.index(
        "if ( !BG_CanItemBeGrabbed("
    )
    assert touch_block.index("item = &bg_itemlist[ cent->currentState.modelindex ];") < touch_block.index(
        "if ( CG_ItemSkipsPredictablePickup( item ) ) {"
    )
    assert touch_block.index("if ( CG_ItemSkipsPredictablePickup( item ) ) {") < touch_block.index(
        "BG_AddPredictableEventToPlayerstate( EV_ITEM_PICKUP"
    )
    assert touch_block.index("BG_AddPredictableEventToPlayerstate( EV_ITEM_PICKUP") < touch_block.index(
        "cent->currentState.eFlags |= EF_NODRAW;"
    )
    assert touch_block.index("cent->currentState.eFlags |= EF_NODRAW;") < touch_block.index(
        "cent->miscTime = cg.time;"
    )
    assert touch_block.index("cent->miscTime = cg.time;") < touch_block.index("if ( item->giType == IT_WEAPON ) {")


def test_touch_trigger_prediction_matches_retail_prediction_filters_and_box_trace() -> None:
    source = CG_PREDICT.read_text(encoding="utf-8")
    trigger_block = _block_from_marker(source, "static void CG_TouchTriggerPrediction")

    for expected in (
        "if ( cg.predictedPlayerState.stats[STAT_HEALTH] <= 0 ) {",
        "cg.predictedPlayerState.pm_type == PM_NOCLIP",
        "cg.predictedPlayerState.pm_type == PM_SPECTATOR",
        "cg.predictedPlayerState.pm_type == PM_DEAD",
        "cg.predictedPlayerState.pm_type == PM_INTERMISSION",
        "cg.predictedPlayerState.pm_type == PM_SPINTERMISSION",
        "if ( ent->eType == ET_ITEM ) {",
        "CG_TouchItem( cent );",
        "if ( ent->solid != SOLID_BMODEL ) {",
        "cmodel = trap_CM_InlineModel( ent->modelindex );",
        "trap_CM_BoxTrace( &trace, cg.predictedPlayerState.origin, cg.predictedPlayerState.origin,",
        "cg_pmove.mins, cg_pmove.maxs, cmodel, -1 );",
        "if ( ent->eType == ET_TELEPORT_TRIGGER ) {",
        "cg.hyperspace = qtrue;",
        "BG_TouchJumpPad( &cg.predictedPlayerState, ent );",
        "if ( cg.predictedPlayerState.jumppad_frame != cg.predictedPlayerState.pmove_framecount ) {",
        "cg.predictedPlayerState.jumppad_frame = 0;",
        "cg.predictedPlayerState.jumppad_ent = 0;",
    ):
        assert expected in trigger_block

    assert "cg.predictedPlayerState.pm_type == PM_FREEZE" not in trigger_block
    assert "CG_Trace(" not in trigger_block
    assert trigger_block.index("if ( cg.predictedPlayerState.stats[STAT_HEALTH] <= 0 ) {") < trigger_block.index(
        "cg.predictedPlayerState.pm_type == PM_NOCLIP"
    )
    assert trigger_block.index("if ( ent->eType == ET_ITEM ) {") < trigger_block.index("CG_TouchItem( cent );")
    assert trigger_block.index("CG_TouchItem( cent );") < trigger_block.index("if ( ent->solid != SOLID_BMODEL ) {")
    assert trigger_block.index("cmodel = trap_CM_InlineModel( ent->modelindex );") < trigger_block.index(
        "trap_CM_BoxTrace( &trace, cg.predictedPlayerState.origin, cg.predictedPlayerState.origin,"
    )
    assert trigger_block.index("trap_CM_BoxTrace( &trace, cg.predictedPlayerState.origin") < trigger_block.index(
        "if ( !trace.startsolid ) {"
    )
    assert trigger_block.index("if ( !trace.startsolid ) {") < trigger_block.index(
        "if ( ent->eType == ET_TELEPORT_TRIGGER ) {"
    )
    assert trigger_block.index("if ( cg.predictedPlayerState.jumppad_frame") > trigger_block.index(
        "for ( i = 0 ; i < cg_numTriggerEntities ; i++ ) {"
    )


def test_transition_player_state_keeps_retail_follow_reset_and_intermission_flow() -> None:
    source = CG_PLAYERSTATE.read_text(encoding="utf-8")
    transition_block = _block_from_marker(source, "void CG_TransitionPlayerState")

    assert "if ( ps->clientNum != ops->clientNum ) {" in transition_block
    assert "cg.thisFrameTeleport = qtrue;" in transition_block
    assert "*ops = *ps;" in transition_block
    assert transition_block.index("*ops = *ps;") < transition_block.index("if ( ps->damageEvent != ops->damageEvent && ps->damageCount ) {")

    assert "if ( cg.snap->ps.pm_type != PM_INTERMISSION" in transition_block
    assert "&& ps->persistant[PERS_TEAM] != TEAM_SPECTATOR ) {" in transition_block
    assert "CG_CheckLocalSounds( ps, ops );" in transition_block
    assert "CG_RecordCrosshairHitFeedback( ps, ops );" in transition_block
    assert transition_block.index("CG_CheckLocalSounds( ps, ops );") < transition_block.index("CG_RecordCrosshairHitFeedback( ps, ops );")

    assert "if ( ops->pm_type != PM_INTERMISSION && ps->pm_type == PM_INTERMISSION ) {" in transition_block
    assert "CG_HandleAutoActionsIntermission( ps );" in transition_block
    assert "CG_CheckAmmo();" in transition_block
    assert "CG_CheckPlayerstateEvents( ps, ops );" in transition_block
    assert transition_block.index("CG_HandleAutoActionsIntermission( ps );") < transition_block.index("CG_CheckAmmo();")
    assert transition_block.index("CG_CheckAmmo();") < transition_block.index("CG_CheckPlayerstateEvents( ps, ops );")
    assert transition_block.index("CG_CheckPlayerstateEvents( ps, ops );") < transition_block.index("if ( ps->viewheight != ops->viewheight ) {")


def test_crosshair_hit_feedback_keeps_retail_armor_bucket_clamp() -> None:
    source = CG_PLAYERSTATE.read_text(encoding="utf-8")
    block = _block_from_marker(source, "static void CG_RecordCrosshairHitFeedback")

    assert "if ( ps->persistant[PERS_HITS] <= ops->persistant[PERS_HITS] ) {" in block
    assert "armor = ps->persistant[PERS_ATTACKEE_ARMOR] & 0xff;" in block
    assert "cg_crosshairHitFeedbackValue = ( armor >> 6 ) + 1;" in block
    assert "if ( cg_crosshairHitFeedbackValue < 1 ) {" in block
    assert "} else if ( cg_crosshairHitFeedbackValue > 4 ) {" in block


def test_playerstate_event_and_reward_helpers_keep_retail_transition_payload_flow() -> None:
    source = CG_PLAYERSTATE.read_text(encoding="utf-8")
    events_block = _block_from_marker(source, "void CG_CheckPlayerstateEvents")
    sounds_block = _block_from_marker(source, "void CG_CheckLocalSounds")

    assert "if ( ps->externalEvent && ps->externalEvent != ops->externalEvent ) {" in events_block
    assert "cent->currentState.event = ps->externalEvent;" in events_block
    assert "cent->currentState.eventParm = ps->externalEventParm;" in events_block
    assert "for ( i = ps->eventSequence - MAX_PS_EVENTS ; i < ps->eventSequence ; i++ ) {" in events_block
    assert "cg.predictableEvents[ i & (MAX_PREDICTED_EVENTS-1) ] = event;" in events_block
    assert "cg.eventSequence++;" in events_block

    assert "if ( ps->persistant[PERS_TEAM] != ops->persistant[PERS_TEAM] ) {" in sounds_block
    assert "if ( cg.intermissionStarted ) {" in sounds_block
    assert "rewardVOEnabled = (qboolean)( cg_announcerRewardsVO.integer && cgs.announcerProfile != ANNOUNCER_PROFILE_DISABLED );" in sounds_block
    assert "if (ps->persistant[PERS_CAPTURES] != ops->persistant[PERS_CAPTURES]) {" in sounds_block
    assert "if (ps->persistant[PERS_IMPRESSIVE_COUNT] != ops->persistant[PERS_IMPRESSIVE_COUNT]) {" in sounds_block
    assert "if (ps->persistant[PERS_EXCELLENT_COUNT] != ops->persistant[PERS_EXCELLENT_COUNT]) {" in sounds_block
    assert "if (ps->persistant[PERS_GAUNTLET_FRAG_COUNT] != ops->persistant[PERS_GAUNTLET_FRAG_COUNT]) {" in sounds_block
    assert "if (ps->persistant[PERS_DEFEND_COUNT] != ops->persistant[PERS_DEFEND_COUNT]) {" in sounds_block
    assert "if (ps->persistant[PERS_ASSIST_COUNT] != ops->persistant[PERS_ASSIST_COUNT]) {" in sounds_block
    assert "if (ps->persistant[PERS_PLAYEREVENTS] != ops->persistant[PERS_PLAYEREVENTS]) {" in sounds_block
    assert sounds_block.index("if ( cg.intermissionStarted ) {") < sounds_block.index("rewardVOEnabled = (qboolean)( cg_announcerRewardsVO.integer && cgs.announcerProfile != ANNOUNCER_PROFILE_DISABLED );")


def test_local_player_configstring_update_reuses_client_info_context_queue() -> None:
    source = CG_SERVERCMDS.read_text(encoding="utf-8")
    config_block = _block_from_marker(source, "void CG_ConfigStringModified")
    players_start = config_block.index("} else if ( num >= CS_PLAYERS && num < CS_PLAYERS+MAX_CLIENTS ) {")
    players_end = config_block.index("} else if ( num == CS_FLAGSTATUS ) {", players_start)
    players_block = config_block[players_start:players_end]

    assert "if ( num - CS_PLAYERS == cg.clientNum ) {" in players_block
    assert "CG_QueueClientInfoContextRefresh();" in players_block
    assert "CG_NewClientInfo( num - CS_PLAYERS );" in players_block
    assert players_block.index("CG_QueueClientInfoContextRefresh();") < players_block.index("CG_NewClientInfo( num - CS_PLAYERS );")


def test_cgame_prediction_pmove_wiring_is_backed_by_committed_retail_evidence() -> None:
    mapping = CGAME_MAPPING.read_text(encoding="utf-8")
    plan = CGAME_BG_PLAN.read_text(encoding="utf-8")

    expected_symbols = {
        "CG_PredictPlayerState": ("0x100446E0", "Prediction loop"),
        "CG_TouchItem": ("0x100443C0", "Retail item-touch prediction helper"),
        "CG_TouchTriggerPrediction": ("0x100444D0", "Retail trigger-touch predictor"),
        "CG_UpdateStepChange": ("0x10044620", "Retail stair-step smoothing helper"),
        "CG_UpdatePredictedRailFire": ("0x10044CE0", "Retail predicted-rail replay helper"),
        "CG_TransitionPlayerState": ("0x10043B60", "Shared playerstate-transition helper"),
    }

    for name, (address, comment_token) in expected_symbols.items():
        entry = _cgame_symbol(name)
        assert entry["address"] == address
        assert entry["status"] == "matched"
        assert comment_token in entry["comment"]
        assert name in mapping

    for expected in (
        "The prediction seam now lines up cleanly from source to retail binary",
        "CG-C3",
        "prediction and transition seam",
        "Focused structural coverage",
    ):
        assert expected in mapping or expected in plan
