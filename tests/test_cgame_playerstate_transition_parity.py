"""Guard retail-backed cgame playerstate and prediction transition behavior."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_PLAYERSTATE = REPO_ROOT / "src" / "code" / "cgame" / "cg_playerstate.c"
CG_PREDICT = REPO_ROOT / "src" / "code" / "cgame" / "cg_predict.c"


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


def test_cgame_transition_player_state_keeps_retail_transition_order() -> None:
	source = CG_PLAYERSTATE.read_text(encoding="utf-8")
	transition_block = _block_from_marker(source, "void CG_TransitionPlayerState")

	for expected in (
		"if ( ps->clientNum != ops->clientNum ) {",
		"cg.thisFrameTeleport = qtrue;",
		"*ops = *ps;",
		"if ( ps->damageEvent != ops->damageEvent && ps->damageCount ) {",
		"if ( ps->persistant[PERS_SPAWN_COUNT] != ops->persistant[PERS_SPAWN_COUNT] ) {",
		"if ( cg.mapRestart ) {",
		"cg.mapRestart = qfalse;",
		"if ( cg.snap->ps.pm_type != PM_INTERMISSION",
		"&& ps->persistant[PERS_TEAM] != TEAM_SPECTATOR ) {",
		"CG_CheckLocalSounds( ps, ops );",
		"CG_RecordCrosshairHitFeedback( ps, ops );",
		"CG_CheckAmmo();",
		"CG_CheckPlayerstateEvents( ps, ops );",
		"if ( ps->viewheight != ops->viewheight ) {",
		"cg.duckChange = ps->viewheight - ops->viewheight;",
		"cg.duckTime = cg.time;",
	):
		assert expected in transition_block

	assert transition_block.index("if ( ps->damageEvent != ops->damageEvent && ps->damageCount ) {") < transition_block.index(
		"if ( ps->persistant[PERS_SPAWN_COUNT] != ops->persistant[PERS_SPAWN_COUNT] ) {"
	)
	assert transition_block.index("CG_CheckLocalSounds( ps, ops );") < transition_block.index(
		"CG_RecordCrosshairHitFeedback( ps, ops );"
	)
	assert transition_block.index("CG_RecordCrosshairHitFeedback( ps, ops );") < transition_block.index("CG_CheckAmmo();")
	assert transition_block.index("CG_CheckAmmo();") < transition_block.index("CG_CheckPlayerstateEvents( ps, ops );")
	assert transition_block.index("CG_CheckPlayerstateEvents( ps, ops );") < transition_block.index(
		"if ( ps->viewheight != ops->viewheight ) {"
	)


def test_cgame_check_local_sounds_keeps_retail_reward_and_warning_gates() -> None:
	source = CG_PLAYERSTATE.read_text(encoding="utf-8")
	local_sounds_block = _block_from_marker(source, "void CG_CheckLocalSounds")

	for expected in (
		"if ( ps->persistant[PERS_TEAM] != ops->persistant[PERS_TEAM] ) {",
		"rewardVOEnabled = (qboolean)( cg_announcerRewardsVO.integer && cgs.announcerProfile != ANNOUNCER_PROFILE_DISABLED );",
		"reward = qfalse;",
		"pushReward(cgs.media.captureAwardSound, cgs.media.medalCapture, ps->persistant[PERS_CAPTURES]);",
		"pushReward(sfx, cgs.media.medalImpressive, ps->persistant[PERS_IMPRESSIVE_COUNT]);",
		"pushReward(sfx, cgs.media.medalExcellent, ps->persistant[PERS_EXCELLENT_COUNT]);",
		"pushReward(sfx, cgs.media.medalGauntlet, ps->persistant[PERS_GAUNTLET_FRAG_COUNT]);",
		"pushReward(cgs.media.defendSound, cgs.media.medalDefend, ps->persistant[PERS_DEFEND_COUNT]);",
		"pushReward(cgs.media.assistSound, cgs.media.medalAssist, ps->persistant[PERS_ASSIST_COUNT]);",
		"if (ps->persistant[PERS_PLAYEREVENTS] != ops->persistant[PERS_PLAYEREVENTS]) {",
		"if ( rewardVOEnabled ) {",
		"trap_S_StartLocalSound( cgs.media.youHaveFlagSound, CHAN_ANNOUNCER );",
		"if (!reward) {",
		"if ( !cg.warmup ) {",
		"CG_AddBufferedSound(cgs.media.takenLeadSound);",
		"CG_AddBufferedSound(cgs.media.tiedLeadSound);",
		"CG_AddBufferedSound(cgs.media.lostLeadSound);",
		"if ( cgs.timelimit > 0 ) {",
		"if ( cgs.fraglimit > 0 && cgs.gametype < GT_CTF) {",
	):
		assert expected in local_sounds_block

	assert local_sounds_block.index("reward = qfalse;") < local_sounds_block.index(
		"if (ps->persistant[PERS_CAPTURES] != ops->persistant[PERS_CAPTURES]) {"
	)
	assert local_sounds_block.index("if (ps->persistant[PERS_PLAYEREVENTS] != ops->persistant[PERS_PLAYEREVENTS]) {") < local_sounds_block.index(
		"if ( cgs.gametype >= GT_TEAM ) {"
	)
	assert local_sounds_block.index("if ( cgs.gametype >= GT_TEAM ) {") < local_sounds_block.index("if (!reward) {")
	assert local_sounds_block.index("if (!reward) {") < local_sounds_block.index("if ( cgs.timelimit > 0 ) {")
	assert local_sounds_block.index("if ( cgs.timelimit > 0 ) {") < local_sounds_block.index(
		"if ( cgs.fraglimit > 0 && cgs.gametype < GT_CTF) {"
	)


def test_cgame_crosshair_hit_feedback_keeps_retail_bucket_clamp() -> None:
	source = CG_PLAYERSTATE.read_text(encoding="utf-8")
	feedback_block = _block_from_marker(source, "static void CG_RecordCrosshairHitFeedback")

	for expected in (
		"if ( !ps || !ops ) {",
		"if ( ps->persistant[PERS_HITS] <= ops->persistant[PERS_HITS] ) {",
		"armor = ps->persistant[PERS_ATTACKEE_ARMOR] & 0xff;",
		"cg_crosshairHitFeedbackTime = cg.time;",
		"cg_crosshairHitFeedbackValue = ( armor >> 6 ) + 1;",
		"if ( cg_crosshairHitFeedbackValue < 1 ) {",
		"cg_crosshairHitFeedbackValue = 1;",
		"} else if ( cg_crosshairHitFeedbackValue > 4 ) {",
		"cg_crosshairHitFeedbackValue = 4;",
	):
		assert expected in feedback_block


def test_cgame_predict_player_state_keeps_retail_transition_handoff() -> None:
	source = CG_PREDICT.read_text(encoding="utf-8")
	predict_block = _block_from_marker(source, "void CG_PredictPlayerState")

	for expected in (
		"CG_UpdateClientInfoContext();",
		"if ( cg.demoPlayback || (cg.snap->ps.pm_flags & PMF_FOLLOW) ) {",
		"CG_InterpolatePlayerState( qfalse );",
		"if ( cg_nopredict.integer || cg_synchronousClients.integer ) {",
		"CG_InterpolatePlayerState( qtrue );",
		"if ( !moved ) {",
		"CG_AdjustPositionForMover( cg.predictedPlayerState.origin,",
		"CG_TransitionPlayerState( &cg.predictedPlayerState, &oldPlayerState );",
	):
		assert expected in predict_block

	assert predict_block.index("CG_UpdateClientInfoContext();") < predict_block.index(
		"if ( cg.demoPlayback || (cg.snap->ps.pm_flags & PMF_FOLLOW) ) {"
	)
	assert predict_block.index("if ( !moved ) {") < predict_block.rindex("CG_AdjustPositionForMover( cg.predictedPlayerState.origin,")
	assert predict_block.rindex("CG_AdjustPositionForMover( cg.predictedPlayerState.origin,") < predict_block.index(
		"CG_TransitionPlayerState( &cg.predictedPlayerState, &oldPlayerState );"
	)


def test_cgame_check_playerstate_events_keeps_retail_external_and_predictable_replay() -> None:
	source = CG_PLAYERSTATE.read_text(encoding="utf-8")
	events_block = _block_from_marker(source, "void CG_CheckPlayerstateEvents")

	for expected in (
		"if ( ps->externalEvent && ps->externalEvent != ops->externalEvent ) {",
		"cent = &cg_entities[ ps->clientNum ];",
		"cent->currentState.event = ps->externalEvent;",
		"cent->currentState.eventParm = ps->externalEventParm;",
		"cent = &cg.predictedPlayerEntity;",
		"for ( i = ps->eventSequence - MAX_PS_EVENTS ; i < ps->eventSequence ; i++ ) {",
		"i >= ops->eventSequence",
		"ps->events[i & (MAX_PS_EVENTS-1)] != ops->events[i & (MAX_PS_EVENTS-1)]",
		"cent->currentState.event = event;",
		"cent->currentState.eventParm = ps->eventParms[ i & (MAX_PS_EVENTS-1) ];",
		"CG_EntityEvent( cent, cent->lerpOrigin );",
		"cg.predictableEvents[ i & (MAX_PREDICTED_EVENTS-1) ] = event;",
		"cg.eventSequence++;",
	):
		assert expected in events_block
