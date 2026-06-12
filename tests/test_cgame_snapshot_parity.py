"""Guard retail-backed cgame snapshot refresh behavior against source drift."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_PREDICT = REPO_ROOT / "src" / "code" / "cgame" / "cg_predict.c"
CG_ENTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_ents.c"
CG_PLAYERSTATE = REPO_ROOT / "src" / "code" / "cgame" / "cg_playerstate.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CG_SNAPSHOT = REPO_ROOT / "src" / "code" / "cgame" / "cg_snapshot.c"
CG_VIEW = REPO_ROOT / "src" / "code" / "cgame" / "cg_view.c"
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


def _assert_order(block: str, *needles: str) -> None:
    cursor = 0
    for needle in needles:
        index = block.find(needle, cursor)
        if index == -1:
            raise AssertionError(f"expected ordered snippet not found after {cursor}: {needle}")
        cursor = index + len(needle)


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


def test_active_frame_prediction_wiring_feeds_view_and_packet_entities() -> None:
    source = CG_VIEW.read_text(encoding="utf-8")
    draw_block = _block_from_marker(source, "void CG_DrawActiveFrame")
    calc_view_block = _block_from_marker(source, "static int CG_CalcViewValues")

    _assert_order(
        draw_block,
        "cg.time = serverTime;",
        "cg.demoPlayback = demoPlayback;",
        "CG_UpdateCvars();",
        "if ( cg.infoScreenText[0] != 0 ) {",
        "trap_S_ClearLoopingSounds(qfalse);",
        "trap_R_ClearScene();",
        "CG_UpdateQueuedWorldMarkers();",
        "CG_ProcessSnapshots();",
        "if ( !cg.snap || ( cg.snap->snapFlags & SNAPFLAG_NOT_ACTIVE ) ) {",
        "CG_UpdateSpectatorCvar();",
        "cg.clientFrame++;",
        "CG_PredictPlayerState();",
        "cg.renderingThirdPerson = (qboolean)( ( cg.snap->ps.stats[STAT_HEALTH] <= 0 )",
        "inwater = CG_CalcViewValues();",
        "trap_SetUserCmdValue( cg.weaponSelect, cg.weaponPrimary, cg.zoomSensitivity, cg.userCmdFov );",
        "if ( !cg.renderingThirdPerson ) {",
        "if ( !cg.hyperspace ) {",
        "CG_AddPacketEntities();",
        "CG_AddMarks();",
        "CG_AddParticles ();",
        "CG_AddLocalEntities();",
        "CG_AddViewWeapon( &cg.predictedPlayerState );",
        "cg.refdef.time = cg.time;",
        "memcpy( cg.refdef.areamask, cg.snap->areamask, sizeof( cg.refdef.areamask ) );",
        "CG_PowerupTimerSounds();",
        "CG_PlayBufferedSounds();",
        "CG_PlayBufferedVoiceChats();",
        "CG_RunPendingFollowKiller();",
        "trap_S_Respatialize( cg.snap->ps.clientNum, cg.refdef.vieworg, cg.refdef.viewaxis, inwater );",
        "if ( stereoView != STEREO_RIGHT ) {",
        "CG_AddLagometerFrameInfo();",
        "CG_UpdateSpectatorItemPickups();",
        "CG_DrawActive( stereoView );",
    )

    assert "CG_AddPacketEntities();" in draw_block[draw_block.index("if ( !cg.hyperspace ) {"):]
    assert "CG_AddViewWeapon( &cg.predictedPlayerState );" in draw_block
    assert "ps = &cg.predictedPlayerState;" in calc_view_block
    assert "VectorCopy( ps->origin, cg.refdef.vieworg );" in calc_view_block
    assert "VectorCopy( ps->viewangles, cg.refdefViewAngles );" in calc_view_block
    assert "VectorMA( cg.refdef.vieworg, f, cg.predictedError, cg.refdef.vieworg );" in calc_view_block
    assert "cg.refdef.rdflags |= RDF_NOWORLDMODEL | RDF_HYPERSPACE;" in calc_view_block


def test_packet_entity_prediction_proxy_and_mover_wiring_match_retail_shape() -> None:
    source = CG_ENTS.read_text(encoding="utf-8")
    packet_block = _block_from_marker(source, "void CG_AddPacketEntities")
    lerp_block = _block_from_marker(source, "static void CG_CalcEntityLerpPositions")
    mover_block = _block_from_marker(source, "void CG_AdjustPositionForMover")

    for expected in (
        "if ( cg.nextSnap ) {",
        "cg.frameInterpolation = (float)( cg.time - cg.snap->serverTime ) / delta;",
        "cg.frameInterpolation = 0;",
        "cg.autoAngles[1] = ( cg.time & 2047 ) * 360 / 2048.0;",
        "cg.autoAnglesFast[1] = ( cg.time & 1023 ) * 360 / 1024.0f;",
        "AnglesToAxis( cg.autoAngles, cg.autoAxis );",
        "AnglesToAxis( cg.autoAnglesFast, cg.autoAxisFast );",
        "ps = &cg.predictedPlayerState;",
        "BG_PlayerStateToEntityState( ps, &cg.predictedPlayerEntity.currentState, qfalse );",
        "if ( !( ps->pm_flags & PMF_FOLLOW ) || ps->stats[STAT_HEALTH] <= GIB_HEALTH ) {",
        "CG_AddCEntity( &cg.predictedPlayerEntity );",
        "CG_CalcEntityLerpPositions( &cg.predictedPlayerEntity );",
        "CG_EntityEffects( &cg.predictedPlayerEntity );",
        "CG_Player( &cg.predictedPlayerEntity );",
        "CG_CalcEntityLerpPositions( &cg_entities[ cg.snap->ps.clientNum ] );",
        "for ( num = 0 ; num < cg.snap->numEntities ; num++ ) {",
        "CG_AddCEntity( cent );",
    ):
        assert expected in packet_block

    _assert_order(
        packet_block,
        "ps = &cg.predictedPlayerState;",
        "BG_PlayerStateToEntityState( ps, &cg.predictedPlayerEntity.currentState, qfalse );",
        "if ( !( ps->pm_flags & PMF_FOLLOW ) || ps->stats[STAT_HEALTH] <= GIB_HEALTH ) {",
        "CG_CalcEntityLerpPositions( &cg_entities[ cg.snap->ps.clientNum ] );",
        "for ( num = 0 ; num < cg.snap->numEntities ; num++ ) {",
    )

    assert "if ( cent != &cg.predictedPlayerEntity ) {" in lerp_block
    assert "CG_AdjustPositionForMover( cent->lerpOrigin, cent->currentState.groundEntityNum," in lerp_block

    for expected in (
        "if ( moverNum <= 0 || moverNum >= ENTITYNUM_MAX_NORMAL ) {",
        "if ( cent->currentState.eType != ET_MOVER ) {",
        "BG_EvaluateTrajectory( &cent->currentState.pos, fromTime, oldOrigin );",
        "BG_EvaluateTrajectory( &cent->currentState.apos, fromTime, oldAngles );",
        "BG_EvaluateTrajectory( &cent->currentState.pos, toTime, origin );",
        "BG_EvaluateTrajectory( &cent->currentState.apos, toTime, angles );",
        "VectorSubtract( origin, oldOrigin, deltaOrigin );",
        "VectorSubtract( angles, oldAngles, deltaAngles );",
        "VectorAdd( in, deltaOrigin, out );",
    ):
        assert expected in mover_block


def test_snapshot_handoff_wiring_keeps_prediction_inputs_in_retail_order() -> None:
    source = CG_SNAPSHOT.read_text(encoding="utf-8")
    initial_block = _block_from_marker(source, "void CG_SetInitialSnapshot")
    transition_block = _block_from_marker(source, "static void CG_TransitionSnapshot")
    next_block = _block_from_marker(source, "static void CG_SetNextSnap")
    read_block = _block_from_marker(source, "static snapshot_t *CG_ReadNextSnapshot")
    process_block = _block_from_marker(source, "void CG_ProcessSnapshots")

    _assert_order(
        initial_block,
        "cg.snap = snap;",
        "BG_PlayerStateToEntityState( &snap->ps, &cg_entities[ snap->ps.clientNum ].currentState, qfalse );",
        "CG_BuildSolidList();",
        "CG_ExecuteNewServerCommands( snap->serverCommandSequence );",
        "CG_Respawn();",
        "for ( i = 0 ; i < cg.snap->numEntities ; i++ ) {",
        "memcpy(&cent->currentState, state, sizeof(entityState_t));",
        "CG_SyncTeamOverlayClientInfo( state );",
        "cent->interpolate = qfalse;",
        "cent->currentValid = qtrue;",
        "CG_ResetEntity( cent );",
        "CG_CheckEvents( cent );",
    )

    _assert_order(
        transition_block,
        "CG_ExecuteNewServerCommands( cg.nextSnap->serverCommandSequence );",
        "cent->currentValid = qfalse;",
        "oldFrame = cg.snap;",
        "cg.snap = cg.nextSnap;",
        "BG_PlayerStateToEntityState( &cg.snap->ps, &cg_entities[ cg.snap->ps.clientNum ].currentState, qfalse );",
        "cg_entities[ cg.snap->ps.clientNum ].interpolate = qfalse;",
        "CG_TransitionEntity( cent );",
        "CG_SyncTeamOverlayClientInfo( &cent->currentState );",
        "cent->snapShotTime = cg.snap->serverTime;",
        "if ( ( ps->eFlags ^ ops->eFlags ) & EF_TELEPORT_BIT ) {",
        "if ( cg.demoPlayback || (cg.snap->ps.pm_flags & PMF_FOLLOW)",
        "CG_TransitionPlayerState( ps, ops );",
        "if ( cg_refreshClientInfoContextQueued ) {",
        "CG_RefreshClientInfoContext();",
        "cg.nextSnap = NULL;",
    )

    _assert_order(
        next_block,
        "cg.nextSnap = snap;",
        "BG_PlayerStateToEntityState( &snap->ps, &cg_entities[ snap->ps.clientNum ].nextState, qfalse );",
        "cg_entities[ cg.snap->ps.clientNum ].interpolate = qtrue;",
        "for ( num = 0 ; num < snap->numEntities ; num++ ) {",
        "memcpy(&cent->nextState, es, sizeof(entityState_t));",
        "if ( !cent->currentValid || ( ( cent->currentState.eFlags ^ es->eFlags ) & EF_TELEPORT_BIT )  ) {",
        "if ( cg.snap && ( ( snap->ps.eFlags ^ cg.snap->ps.eFlags ) & EF_TELEPORT_BIT ) ) {",
        "if ( cg.nextSnap->ps.clientNum != cg.snap->ps.clientNum ) {",
        "if ( ( cg.nextSnap->snapFlags ^ cg.snap->snapFlags ) & SNAPFLAG_SERVERCOUNT ) {",
        "CG_BuildSolidList();",
    )

    _assert_order(
        read_block,
        "if ( cg.latestSnapshotNum > cgs.processedSnapshotNum + 1000 ) {",
        "if ( cg.snap == &cg.activeSnapshots[0] ) {",
        "cgs.processedSnapshotNum++;",
        "r = trap_GetSnapshot( cgs.processedSnapshotNum, dest );",
        "if ( r ) {",
        "CG_AddLagometerSnapshotInfo( dest );",
        "return dest;",
        "CG_AddLagometerSnapshotInfo( NULL );",
        "return NULL;",
    )

    _assert_order(
        process_block,
        "trap_GetCurrentSnapshotNumber( &n, &cg.latestSnapshotTime );",
        "while ( !cg.snap ) {",
        "snap = CG_ReadNextSnapshot();",
        "CG_SetInitialSnapshot( snap );",
        "do {",
        "if ( !cg.nextSnap ) {",
        "snap = CG_ReadNextSnapshot();",
        "CG_SetNextSnap( snap );",
        "if ( cg.nextSnap->serverTime < cg.snap->serverTime ) {",
        "if ( cg.time >= cg.snap->serverTime && cg.time < cg.nextSnap->serverTime ) {",
        "CG_TransitionSnapshot();",
        "if ( cg.snap == NULL ) {",
        "if ( cg.time < cg.snap->serverTime ) {",
        "if ( cg.nextSnap != NULL && cg.nextSnap->serverTime <= cg.time ) {",
    )


def test_team_overlay_snapshot_sync_mirrors_retail_entity_state_vitals() -> None:
    source = CG_SNAPSHOT.read_text(encoding="utf-8")
    sync_block = _block_from_marker(source, "static void CG_SyncTeamOverlayClientInfo")
    initial_block = _block_from_marker(source, "void CG_SetInitialSnapshot")
    transition_block = _block_from_marker(source, "static void CG_TransitionSnapshot")

    for expected in (
        "clientNum = state->clientNum;",
        "if ( state->number != clientNum ) {",
        "ci->location = state->location;",
        "ci->health = state->health;",
        "ci->armor = state->armor;",
        "ci->curWeapon = state->weapon;",
        "ci->powerups = state->powerups;",
    ):
        assert expected in sync_block

    assert "CG_SyncTeamOverlayClientInfo( state );" in initial_block
    assert "CG_SyncTeamOverlayClientInfo( &cg_entities[ snap->ps.clientNum ].currentState );" in initial_block
    assert "CG_SyncTeamOverlayClientInfo( &cent->currentState );" in transition_block
    assert "CG_SyncTeamOverlayClientInfo( &cg_entities[ cg.snap->ps.clientNum ].currentState );" in transition_block


def test_prediction_solid_trace_and_interpolation_helpers_match_retail_shape() -> None:
    source = CG_PREDICT.read_text(encoding="utf-8")
    solid_block = _block_from_marker(source, "void CG_BuildSolidList")
    clip_block = _block_from_marker(source, "static void CG_ClipMoveToEntities")
    capsule_block = _block_from_marker(source, "static void CG_TraceCapsule")
    trace_block = _block_from_marker(source, "void\tCG_Trace")
    contents_block = _block_from_marker(source, "int\t\tCG_PointContents")
    interpolate_block = _block_from_marker(source, "static void CG_InterpolatePlayerState")

    for expected in (
        "cg_numSolidEntities = 0;",
        "cg_numTriggerEntities = 0;",
        "if ( cg.nextSnap && !cg.nextFrameTeleport && !cg.thisFrameTeleport ) {",
        "snap = cg.nextSnap;",
        "snap = cg.snap;",
        "ent->eType == ET_ITEM || ent->eType == ET_PUSH_TRIGGER || ent->eType == ET_TELEPORT_TRIGGER",
        "cg_triggerEntities[cg_numTriggerEntities] = cent;",
        "if ( cent->nextState.solid ) {",
        "cg_solidEntities[cg_numSolidEntities] = cent;",
    ):
        assert expected in solid_block

    assert solid_block.index("if ( cg.nextSnap && !cg.nextFrameTeleport && !cg.thisFrameTeleport ) {") < solid_block.index(
        "for ( i = 0 ; i < snap->numEntities ; i++ ) {"
    )
    assert solid_block.index("ent->eType == ET_ITEM") < solid_block.index("if ( cent->nextState.solid ) {")

    for expected in (
        "if ( ent->number == skipNumber ) {",
        "if ( ent->solid == SOLID_BMODEL ) {",
        "cmodel = trap_CM_InlineModel( ent->modelindex );",
        "BG_EvaluateTrajectory( &cent->currentState.pos, cg.physicsTime, origin );",
        "x = (ent->solid & 255);",
        "zd = ((ent->solid>>8) & 255);",
        "zu = ((ent->solid>>16) & 255) - 32;",
        "cmodel = trap_CM_TempCapsuleModel( bmins, bmaxs );",
        "cmodel = trap_CM_TempBoxModel( bmins, bmaxs );",
        "trap_CM_TransformedCapsuleTrace( &trace, start, end, mins, maxs, cmodel, mask, origin, angles );",
        "trap_CM_TransformedBoxTrace( &trace, start, end, mins, maxs, cmodel, mask, origin, angles );",
        "trace.entityNum = ent->number;",
        "*tr = trace;",
        "tr->startsolid = qtrue;",
        "if ( tr->allsolid ) {",
    ):
        assert expected in clip_block

    assert clip_block.index("if ( ent->number == skipNumber ) {") < clip_block.index(
        "if ( ent->solid == SOLID_BMODEL ) {"
    )
    assert clip_block.index("cmodel = trap_CM_TempCapsuleModel( bmins, bmaxs );") < clip_block.index(
        "trap_CM_TransformedCapsuleTrace("
    )
    assert clip_block.index("cmodel = trap_CM_TempBoxModel( bmins, bmaxs );") < clip_block.index(
        "trap_CM_TransformedBoxTrace("
    )

    for expected in (
        "trap_CM_CapsuleTrace( &t, start, end, mins, maxs, 0, mask );",
        "t.entityNum = t.fraction != 1.0 ? ENTITYNUM_WORLD : ENTITYNUM_NONE;",
        "CG_ClipMoveToEntities( start, mins, maxs, end, skipNumber, mask, qtrue, &t );",
        "*result = t;",
    ):
        assert expected in capsule_block
    assert capsule_block.index("trap_CM_CapsuleTrace(") < capsule_block.index(
        "CG_ClipMoveToEntities( start, mins, maxs, end, skipNumber, mask, qtrue, &t );"
    )

    for expected in (
        "if ( CG_UseCapsuleTrace() ) {",
        "CG_TraceCapsule( result, start, mins, maxs, end, skipNumber, mask );",
        "trap_CM_BoxTrace( &t, start, end, mins, maxs, 0, mask );",
        "t.entityNum = t.fraction != 1.0 ? ENTITYNUM_WORLD : ENTITYNUM_NONE;",
        "CG_ClipMoveToEntities( start, mins, maxs, end, skipNumber, mask, qfalse, &t );",
        "*result = t;",
    ):
        assert expected in trace_block
    assert trace_block.index("if ( CG_UseCapsuleTrace() ) {") < trace_block.index("trap_CM_BoxTrace(")

    for expected in (
        "contents = trap_CM_PointContents (point, 0);",
        "if ( ent->number == passEntityNum ) {",
        "if (ent->solid != SOLID_BMODEL) {",
        "cmodel = trap_CM_InlineModel( ent->modelindex );",
        "if ( !cmodel ) {",
        "contents |= trap_CM_TransformedPointContents( point, cmodel, ent->origin, ent->angles );",
        "return contents;",
    ):
        assert expected in contents_block

    for expected in (
        "*out = cg.snap->ps;",
        "if ( grabAngles ) {",
        "cmdNum = trap_GetCurrentCmdNumber();",
        "trap_GetUserCmd( cmdNum, &cmd );",
        "PM_UpdateViewAngles( out, &cmd );",
        "if ( cg.nextFrameTeleport ) {",
        "if ( !next || next->serverTime <= prev->serverTime ) {",
        "f = (float)( cg.time - prev->serverTime ) / ( next->serverTime - prev->serverTime );",
        "out->bobCycle = prev->ps.bobCycle + f * ( i - prev->ps.bobCycle );",
        "out->origin[i] = prev->ps.origin[i] + f * (next->ps.origin[i] - prev->ps.origin[i] );",
        "out->viewangles[i] = LerpAngle(",
        "out->velocity[i] = prev->ps.velocity[i] +",
    ):
        assert expected in interpolate_block
    assert interpolate_block.index("if ( grabAngles ) {") < interpolate_block.index("if ( cg.nextFrameTeleport ) {")


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
    flag_block = _block_from_marker(source, "static qboolean BG_IsRedBlueFlagItem")
    skip_block = _block_from_marker(source, "static qboolean CG_ItemSkipsPredictablePickup")
    touch_block = _block_from_marker(source, "static void CG_TouchItem")

    for expected in (
        "if ( item->giType != IT_TEAM ) {",
        "return (qboolean)( item->giTag == PW_REDFLAG || item->giTag == PW_BLUEFLAG );",
    ):
        assert expected in flag_block

    for expected in (
        "if ( item->giType == IT_ARMOR && item->quantity >= 25 ) {",
        "if ( item->giType == IT_HEALTH && item->quantity >= 100 ) {",
        "if ( item->giType == IT_POWERUP ) {",
        "case PW_QUAD:",
        "case PW_BATTLESUIT:",
        "case PW_HASTE:",
        "case PW_INVIS:",
        "case PW_REGEN:",
        "if ( item->giType == IT_HOLDABLE && BG_HoldableForItemTag( item->giTag ) == HI_MEDKIT ) {",
    ):
        assert expected in skip_block

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
        "BG_IsRedBlueFlagItem": ("0x10001000", "Deliberate synthetic retail flag-item predicate"),
        "CG_PredictPlayerState": ("0x100446E0", "Prediction loop"),
        "CG_BuildSolidList": ("0x10043C90", "Retail prediction helper"),
        "CG_ClipMoveToEntities": ("0x10043D40", "Prediction collision helper"),
        "CG_Trace": ("0x10044040", "Retail prediction trace wrapper"),
        "CG_TraceCapsule": ("0x10044100", "Retail capsule-trace sidecar"),
        "CG_PointContents": ("0x100441A0", "Retail point-contents wrapper"),
        "CG_InterpolatePlayerState": ("0x10044230", "Prediction fallback path"),
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


def test_prediction_related_frame_snapshot_and_entity_wiring_has_retail_evidence() -> None:
    mapping = CGAME_MAPPING.read_text(encoding="utf-8")

    expected_symbols = {
        "CG_AdjustPositionForMover": ("0x10017F70", "Mover compensation helper"),
        "CG_AddPacketEntities": ("0x10018BE0", "Packet-entity frame pass"),
        "CG_SetInitialSnapshot": ("0x1004BE80", "Initial snapshot handoff helper"),
        "CG_TransitionSnapshot": ("0x1004C020", "Snapshot handoff routine"),
        "CG_SetNextSnap": ("0x1004C2E0", "Retail next-snapshot priming helper"),
        "CG_ReadNextSnapshot": ("0x1004C3E0", "Snapshot fetch helper"),
        "CG_ProcessSnapshots": ("0x1004C4D0", "Snapshot pump"),
        "CG_DrawActiveFrame": ("0x1004E4E0", "Top-level render/update frame loop"),
    }

    for name, (address, comment_token) in expected_symbols.items():
        entry = _cgame_symbol(name)
        assert entry["address"] == address
        assert entry["status"] == "matched"
        assert comment_token in entry["comment"]
        assert name in mapping

    for expected in (
        "`0x10018BE0` is instead `CG_AddPacketEntities`",
        "builds the predicted player entity from playerstate",
        "CG_SetInitialSnapshot",
        "CG_SetNextSnap",
        "CG_ReadNextSnapshot",
        "final `CG_BuildSolidList` handoff",
        "Top-level frame loop that updates cvars, clears scene state, calls `CG_ProcessSnapshots`, runs prediction, and builds the view",
    ):
        assert expected in mapping
