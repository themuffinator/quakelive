"""Guard retail-backed cgame snapshot refresh behavior against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_PREDICT = REPO_ROOT / "src" / "code" / "cgame" / "cg_predict.c"
CG_PLAYERSTATE = REPO_ROOT / "src" / "code" / "cgame" / "cg_playerstate.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CG_SNAPSHOT = REPO_ROOT / "src" / "code" / "cgame" / "cg_snapshot.c"


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
