"""Guard the retail cgame event transport seams against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
Q_SHARED = REPO_ROOT / "src" / "code" / "game" / "q_shared.h"
MSG = REPO_ROOT / "src" / "code" / "qcommon" / "msg.c"
G_UTILS = REPO_ROOT / "src" / "code" / "game" / "g_utils.c"
G_COMBAT = REPO_ROOT / "src" / "code" / "game" / "g_combat.c"
G_CLIENT = REPO_ROOT / "src" / "code" / "game" / "g_client.c"
G_TEAM = REPO_ROOT / "src" / "code" / "game" / "g_team.c"
G_WEAPON = REPO_ROOT / "src" / "code" / "game" / "g_weapon.c"
G_MAIN = REPO_ROOT / "src" / "code" / "game" / "g_main.c"
G_RACE = REPO_ROOT / "src" / "code" / "game" / "g_race.c"
BG_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "bg_public.h"
CG_EVENT = REPO_ROOT / "src" / "code" / "cgame" / "cg_event.c"


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


def test_shared_entity_state_restores_retail_event_data_slot() -> None:
	q_shared_source = Q_SHARED.read_text(encoding="utf-8")
	msg_source = MSG.read_text(encoding="utf-8")

	assert "int\t\tretailEventPadding[4];" in q_shared_source
	assert "int\t\tretailEventData;" in q_shared_source
	assert "{ NETF(retailEventData), 8 }" in msg_source
	assert "serializedBytes = sizeof( from->number );" in msg_source
	assert "assert( serializedBytes <= sizeof( *from ) );" in msg_source
	assert "assert( numFields + 1 == sizeof( *from )/4 );" not in msg_source


def test_qagame_payload_helpers_publish_recovered_retail_slots() -> None:
	source = G_UTILS.read_text(encoding="utf-8")
	recipient_block = _block_from_marker(source, "void G_SetRetailEventRecipient")
	int_payload_block = _block_from_marker(source, "void G_SetRetailEventIntPayload")
	data_block = _block_from_marker(source, "void G_SetRetailEventData")
	global_team_sound_block = _block_from_marker(source, "void G_SetRetailGlobalTeamSoundPayload")

	assert "ent->s.solid = ( clientNum >= 0 && clientNum < MAX_CLIENTS ) ? clientNum : ENTITYNUM_NONE;" in recipient_block
	assert "memcpy( &state->origin[0], &value, sizeof( value ) );" in int_payload_block
	assert "state->retailEventData = value;" in data_block
	assert "ent->s.weapon = sound;" in global_team_sound_block
	assert "ent->s.groundEntityNum = ( trackedClientNum >= 0 && trackedClientNum < MAX_CLIENTS ) ? trackedClientNum : ENTITYNUM_NONE;" in global_team_sound_block
	assert "ent->s.frame = team;" in global_team_sound_block
	assert "ent->s.legsAnim = index;" in global_team_sound_block


def test_qagame_damage_plum_uses_retail_temp_entity_payload() -> None:
	source = G_COMBAT.read_text(encoding="utf-8")
	helper_block = _block_from_marker(source, "static void G_AddDamagePlum")
	damage_block = _block_from_marker(source, "void G_Damage")

	for expected in (
		"plum = G_TempEntity( origin, EV_DAMAGEPLUM );",
		"plum->r.svFlags |= SVF_SINGLECLIENT;",
		"plum->r.singleClient = attacker->s.number;",
		"G_SetRetailEventRecipient( plum, attacker->s.number );",
		"G_SetRetailEventIntPayload( &plum->s, damage );",
		"G_SetRetailEventData( &plum->s, G_ModToWeapon( mod ) );",
	):
		assert expected in helper_block

	assert "plum->s.clientNum = attacker->s.number;" not in helper_block
	assert "plum->s.time = damage;" not in helper_block
	assert "plum->s.weapon = G_ModToWeapon( mod );" not in helper_block
	assert "G_AddDamagePlum( attacker, point ? point : targ->r.currentOrigin, damage, mod );" in damage_block
	assert "G_AddEvent( targ, EV_DAMAGEPLUM, damage );" not in damage_block


def test_qagame_infected_event_uses_retail_recipient_slot() -> None:
	source = G_CLIENT.read_text(encoding="utf-8")
	block = _block_from_marker(source, "static void G_RREmitInfectedEvent")

	assert "tent = G_TempEntity( ent->client->ps.origin, EV_INFECTED );" in block
	assert "tent->r.svFlags |= SVF_SINGLECLIENT;" in block
	assert "tent->r.singleClient = ent->s.number;" in block
	assert "G_SetRetailEventRecipient( tent, ent->s.number );" in block
	assert "tent->s.clientNum = ent->s.number;" not in block


def test_qagame_global_team_sound_uses_retail_payload_slots() -> None:
	team_source = G_TEAM.read_text(encoding="utf-8")
	weapon_source = G_WEAPON.read_text(encoding="utf-8")
	broadcast_block = _block_from_marker(team_source, "void G_BroadcastGlobalTeamSound")
	add_score_block = _block_from_marker(team_source, "void AddTeamScore")
	return_block = _block_from_marker(team_source, "void Team_ReturnFlagSound")
	capture_block = _block_from_marker(team_source, "void Team_CaptureFlagSound")
	kamikaze_block = _block_from_marker(weapon_source, "void G_StartKamikaze")

	assert "G_SetRetailGlobalTeamSoundPayload( te, sound, trackedClientNum, team, index );" in broadcast_block
	assert "te->s.eventParm = sound;" not in broadcast_block
	assert "te->s.otherEntityNum = ( trackedClientNum >= 0 && trackedClientNum < MAX_CLIENTS ) ? trackedClientNum : ENTITYNUM_NONE;" not in broadcast_block
	assert "te->s.clientNum = team;" not in broadcast_block
	assert "te->s.generic1 = index;" not in broadcast_block

	assert "G_SetRetailGlobalTeamSoundPayload( te, sound, -1, TEAM_FREE, 0 );" in add_score_block
	assert "G_SetRetailGlobalTeamSoundPayload( te," in return_block
	assert "G_SetRetailGlobalTeamSoundPayload( te," in capture_block
	assert "G_SetRetailGlobalTeamSoundPayload( te, GTS_KAMIKAZE, -1, TEAM_FREE, 0 );" in kamikaze_block


def test_red_rover_survival_bonus_emits_retail_global_team_sound() -> None:
	game_source = G_CLIENT.read_text(encoding="utf-8")
	cgame_source = CG_EVENT.read_text(encoding="utf-8")
	survival_bonus_block = _block_from_marker(game_source, "static void G_RRApplySurvivalBonus")
	global_team_sound_case = _block_from_marker(cgame_source, "case EV_GLOBAL_TEAM_SOUND:")

	assert 'trap_SendServerCommand( clientNum, va( "print \\"Survival Bonus! +%i\\n\\"", score ) );' in survival_bonus_block
	assert "G_BroadcastGlobalTeamSound( vec3_origin, GTS_SURVIVOR_WARNING, -1, TEAM_BLUE, 0 );" in survival_bonus_block
	assert "EV_SCOREPLUM" not in survival_bonus_block

	assert "case GTS_SURVIVOR_WARNING:" in global_team_sound_case
	assert "CG_AddBufferedSound( cgs.media.survivorWarningSound );" in global_team_sound_case


def test_last_alive_shared_helper_emits_retail_last_standing_sound() -> None:
	game_source = G_TEAM.read_text(encoding="utf-8")
	cgame_source = CG_EVENT.read_text(encoding="utf-8")
	shared_block = _block_from_marker(game_source, "static qboolean G_NotifyLastAlivePlayer")
	ad_block = _block_from_marker(game_source, "qboolean G_ADNotifyLastAlivePlayer")
	ca_block = _block_from_marker(game_source, "qboolean G_CANotifyLastAlivePlayer")
	freeze_block = _block_from_marker(game_source, "qboolean G_FreezeNotifyLastAlivePlayer")
	rr_block = _block_from_marker(game_source, "qboolean G_RRNotifyLastAlivePlayer")
	global_team_sound_case = _block_from_marker(cgame_source, "case EV_GLOBAL_TEAM_SOUND:")

	assert "G_BroadcastGlobalTeamSound( vec3_origin, GTS_LAST_STANDING, -1, team, 0 );" in shared_block
	assert "return G_NotifyLastAlivePlayer( team );" in ad_block
	assert "return G_NotifyLastAlivePlayer( team );" in ca_block
	assert "return G_NotifyLastAlivePlayer( team );" in freeze_block
	assert "return G_NotifyLastAlivePlayer( team );" in rr_block
	assert "GTS_SURVIVOR_WARNING" not in rr_block

	assert "case GTS_LAST_STANDING:" in global_team_sound_case
	assert "CG_AddBufferedSound( cgs.media.lastStandingSound );" in global_team_sound_case


def test_qagame_award_entity_restores_retail_temp_entity_payload() -> None:
	source = G_MAIN.read_text(encoding="utf-8")
	award_block = _block_from_marker(source, "static void G_AddAwardEntity")
	medal_block = _block_from_marker(source, "void G_RankSendPlayerMedal")

	assert "tent = G_TempEntity( ent->client->ps.origin, EV_AWARD );" in award_block
	assert "tent->r.svFlags |= SVF_SINGLECLIENT;" in award_block
	assert "tent->r.singleClient = ent->s.number;" in award_block
	assert "G_SetRetailEventRecipient( tent, ent->s.number );" in award_block
	assert "tent->s.frame = awardCount;" in award_block
	assert "G_SetRetailEventData( &tent->s, award );" in award_block
	assert "G_AddAwardEntity( ent, awardEventId );" in medal_block


def test_qagame_race_events_use_retail_single_client_payload_slots() -> None:
	source = G_RACE.read_text(encoding="utf-8")
	emit_block = _block_from_marker(source, "static gentity_t *G_RaceEmitClientEvent")
	start_block = _block_from_marker(source, "static void G_RaceEmitStartEvent")
	checkpoint_block = _block_from_marker(source, "static void G_RaceEmitCheckpointEvent")
	finish_block = _block_from_marker(source, "static void G_RaceEmitFinishEvent")
	high_score_block = _block_from_marker(source, "static void G_RaceEmitNewHighScoreEvent")
	touch_block = _block_from_marker(source, "void G_RaceHandlePointTouch")

	for expected in (
		"tent = G_TempEntity( player->client->ps.origin, event );",
		"tent->r.svFlags |= SVF_SINGLECLIENT;",
		"tent->r.singleClient = player->s.number;",
		"G_SetRetailEventRecipient( tent, player->s.number );",
	):
		assert expected in emit_block

	for expected in (
		"tent = G_RaceEmitClientEvent( player, EV_RACE_START );",
		"tent->s.groundEntityNum = G_RaceCheckpointCount( client );",
		"tent->s.constantLight = G_RacePointEntityNum( client->raceState.currentPoint );",
		"tent->s.legsAnim = G_RacePointEntityNum( client->raceState.nextPoint );",
		"G_SetRetailEventIntPayload( &tent->s, client->raceState.startTime );",
	):
		assert expected in start_block

	for expected in (
		"tent = G_RaceEmitClientEvent( player, EV_RACE_CHECKPOINT );",
		"tent->s.groundEntityNum = G_RaceCheckpointCount( client );",
		"tent->s.constantLight = G_RacePointEntityNum( client->raceState.currentPoint );",
		"tent->s.legsAnim = G_RacePointEntityNum( client->raceState.nextPoint );",
		"G_SetRetailEventIntPayload( &tent->s, splitDelta );",
		"G_SetRetailEventData( &tent->s, hasBestSplit ? 1 : 0 );",
	):
		assert expected in checkpoint_block

	assert "tent = G_RaceEmitClientEvent( player, EV_RACE_FINISH );" in finish_block
	assert "G_SetRetailEventIntPayload( &tent->s, elapsed );" in finish_block
	assert "G_SetRetailEventData( &tent->s, 1 );" in finish_block

	assert "(void)G_RaceEmitClientEvent( player, EV_NEW_HIGH_SCORE );" in high_score_block
	assert "if ( G_RacePointIsStart( point ) ) {" in touch_block
	assert "G_RaceStartRun( point, player );" in touch_block
	assert "G_RaceAdvanceCheckpoint( point, player );" in touch_block


def test_cgame_damage_plum_reads_retail_int_and_data_slots_directly() -> None:
	source = CG_EVENT.read_text(encoding="utf-8")
	damage_block = _block_from_marker(source, "static int CG_GetRetailDamagePlumDamage")
	weapon_block = _block_from_marker(source, "static weapon_t CG_GetRetailDamagePlumWeapon")

	assert "memcpy( &damage, &es->origin[0], sizeof( damage ) );" in damage_block
	assert "return damage;" in damage_block
	assert "return es->time;" not in damage_block
	assert "eventParm" not in damage_block

	assert "weapon = (weapon_t)es->retailEventData;" in weapon_block
	assert "return WP_NONE;" in weapon_block
	assert "weapon = (weapon_t)es->weapon;" not in weapon_block
	assert "cg.predictedPlayerState.weapon" not in weapon_block
	assert "cg.snap->ps.weapon" not in weapon_block


def test_cgame_race_events_read_retail_payload_slots_directly() -> None:
	source = CG_EVENT.read_text(encoding="utf-8")
	int_payload_block = _block_from_marker(source, "static int CG_GetRetailEventIntPayload")
	checkpoint_count_block = _block_from_marker(source, "static int CG_GetRaceEventCheckpointCount")
	current_checkpoint_block = _block_from_marker(source, "static int CG_GetRaceEventCurrentCheckpointEntityNum")
	next_checkpoint_block = _block_from_marker(source, "static int CG_GetRaceEventNextCheckpointEntityNum")
	event_block = _block_from_marker(source, "void CG_EntityEvent")

	assert "memcpy( &value, &es->origin[0], sizeof( value ) );" in int_payload_block
	assert "return value;" in int_payload_block
	assert "return es->groundEntityNum;" in checkpoint_count_block
	assert "return es->constantLight;" in current_checkpoint_block
	assert "return es->legsAnim;" in next_checkpoint_block

	for expected in (
		"CG_RaceResetRunState( qfalse );",
		"cgs.raceInfoActive = qtrue;",
		"cgs.raceInfoStartTime = CG_GetRetailEventIntPayload( es );",
		"cgs.raceInfoCheckpointCount = CG_GetRaceEventCheckpointCount( es );",
		"cgs.raceInfoCurrentCheckpointEntityNum = CG_GetRaceEventCurrentCheckpointEntityNum( es );",
		"cgs.raceInfoNextCheckpointEntityNum = CG_GetRaceEventNextCheckpointEntityNum( es );",
		"cgs.raceInfoLastTime = CG_GetRetailEventIntPayload( es );",
	):
		assert expected in event_block


def test_cgame_award_and_global_team_sound_read_retail_payload_slots_directly() -> None:
	source = CG_EVENT.read_text(encoding="utf-8")
	recipient_block = _block_from_marker(source, "static int CG_GetRetailEventClientNum")
	sound_block = _block_from_marker(source, "static int CG_GetGlobalTeamSound( const entityState_t *es )")
	tracked_client_block = _block_from_marker(source, "static int CG_GetGlobalTeamSoundTrackedClientNum")
	team_block = _block_from_marker(source, "static team_t CG_GetGlobalTeamSoundTeam")
	index_block = _block_from_marker(source, "static int CG_GetGlobalTeamSoundIndex")
	award_type_block = _block_from_marker(source, "static int CG_GetRetailAwardType")
	track_flag_block = _block_from_marker(source, "static void CG_TrackFlagCarrierForEvent")
	global_team_sound_case = _block_from_marker(source, "case EV_GLOBAL_TEAM_SOUND:")

	assert "if ( es->solid >= 0 && es->solid < MAX_CLIENTS ) {" in recipient_block
	assert "return es->solid;" in recipient_block
	assert "if ( es->number >= 0 && es->number < MAX_CLIENTS ) {" in recipient_block
	assert "if ( es->clientNum >= 0 && es->clientNum < MAX_CLIENTS ) {" not in recipient_block

	assert "if ( es->weapon < GTS_RED_CAPTURE || es->weapon > GTS_SURVIVOR_WARNING ) {" in sound_block
	assert "return es->weapon;" in sound_block

	assert "if ( es->groundEntityNum >= 0 && es->groundEntityNum < MAX_CLIENTS ) {" in tracked_client_block
	assert "return es->groundEntityNum;" in tracked_client_block
	assert "if ( es->otherEntityNum >= 0 && es->otherEntityNum < MAX_CLIENTS ) {" not in tracked_client_block

	assert "if ( es->frame >= TEAM_FREE && es->frame < TEAM_NUM_TEAMS ) {" in team_block
	assert "return (team_t)es->frame;" in team_block
	assert "if ( es->clientNum >= TEAM_FREE && es->clientNum < TEAM_NUM_TEAMS ) {" not in team_block

	assert "return es->legsAnim;" in index_block
	assert "return es->generic1;" not in index_block

	assert "if ( es->retailEventData >= 0 && es->retailEventData <= 9 ) {" in award_type_block
	assert "return es->retailEventData;" in award_type_block
	assert "return es->eventParm;" not in award_type_block
	assert "return es->generic1;" not in award_type_block

	assert "switch ( CG_GetGlobalTeamSound( es ) ) {" in track_flag_block
	assert "switch ( es->eventParm ) {" not in track_flag_block
	assert "globalTeamSound = CG_GetGlobalTeamSound( es );" in global_team_sound_case
	assert "switch( globalTeamSound ) {" in global_team_sound_case
	assert "switch( es->eventParm ) {" not in global_team_sound_case


def test_freeze_temp_entity_band_uses_explicit_retail_ordinals() -> None:
	bg_public_source = BG_PUBLIC.read_text(encoding="utf-8")
	g_client_source = G_CLIENT.read_text(encoding="utf-8")
	g_freeze_source = (REPO_ROOT / "src" / "code" / "game" / "g_freeze.c").read_text(encoding="utf-8")
	cg_event_source = CG_EVENT.read_text(encoding="utf-8")
	freeze_helper_block = _block_from_marker(g_freeze_source, "static void G_FreezeSetClientFrozenState")
	freeze_frame_block = _block_from_marker(g_client_source, "void G_FreezeClientEndFrame")

	assert "EV_DROWN = 57," in bg_public_source
	assert "EV_OBITUARY = 58," in bg_public_source
	assert "EV_THAW_PLAYER = 87," in bg_public_source
	assert "EV_THAW_TICK = 88," in bg_public_source

	assert "tent = G_TempEntity( client->ps.origin, EV_THAW_PLAYER );" in freeze_helper_block
	assert "tent = G_TempEntity( ent->client->ps.origin, EV_THAW_TICK );" in freeze_frame_block
	assert "QL_EVENTPARM_FREEZE_THAW" not in g_client_source
	assert "QL_EVENTPARM_FREEZE_THAW" not in g_freeze_source

	assert 'case EV_PLAYER_TELEPORT_IN:' in cg_event_source
	assert 'case EV_THAW_PLAYER:' in cg_event_source
	assert 'CG_ThawPlayer( position );' in cg_event_source
	assert 'case EV_THAW_TICK:' in cg_event_source
	assert 'trap_S_StartSound( NULL, es->number, CHAN_BODY, cgs.media.thawTickSound );' in cg_event_source


def test_cgame_powerup_pickups_queue_retail_announcer_voice() -> None:
	source = CG_EVENT.read_text(encoding="utf-8")
	g_items_source = (REPO_ROOT / "src" / "code" / "game" / "g_items.c").read_text(encoding="utf-8")
	resolver_block = _block_from_marker(source, "static sfxHandle_t CG_ItemPickupAnnouncerSound")
	local_pickup_block = _block_from_marker(source, "case EV_ITEM_PICKUP:")
	global_pickup_block = _block_from_marker(source, "case EV_GLOBAL_ITEM_PICKUP:")
	touch_item_block = _block_from_marker(g_items_source, "void Touch_Item")
	powerup_event_block = source[source.index("case EV_POWERUP_QUAD:"):source.index("case EV_GIB_PLAYER:")]

	for expected in (
		"case IT_POWERUP:",
		"case PW_QUAD:",
		"return cgs.media.quadDamagePowerupSound;",
		"case PW_BATTLESUIT:",
		"return cgs.media.battleSuitPowerupSound;",
		"case PW_HASTE:",
		"return cgs.media.hastePowerupSound;",
		"case PW_INVIS:",
		"return cgs.media.invisibilityPowerupSound;",
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
		assert expected in resolver_block

	assert "CG_AddBufferedSound( sfx );" in source
	assert "trap_S_RegisterSound( item->pickup_sound, qfalse )" in local_pickup_block
	assert "CG_AddItemPickupAnnouncerSound( item );" in local_pickup_block
	assert "cgs.media.scoutSound" not in local_pickup_block
	assert "cgs.media.guardSound" not in local_pickup_block
	assert "cgs.media.doublerSound" not in local_pickup_block
	assert "cgs.media.ammoregenSound" not in local_pickup_block

	assert "trap_S_RegisterSound( item->pickup_sound, qfalse )" in global_pickup_block
	assert "if ( cgs.customSettingsMask & CUSTOM_SETTING_QUAD_HOG ) {\n\t\t\t\tbreak;\n\t\t\t}" in global_pickup_block
	assert "CG_AddItemPickupAnnouncerSound( item );" in global_pickup_block

	assert "if ( item->giType == IT_POWERUP || item->giType == IT_TEAM)" in local_pickup_block
	assert "if ( ent->item->giType == IT_POWERUP || ent->item->giType == IT_TEAM ) {" in touch_item_block
	assert "ent->item->giType == IT_KEY" not in touch_item_block
	assert touch_item_block.count("te->s.groundEntityNum = other->s.number;") == 2
	assert "if ( item->giType == IT_POWERUP ) {" in global_pickup_block
	assert "CG_SpectatorTrackEvent( es->groundEntityNum, CG_SPECTATOR_TRACK_POWERUP );" in global_pickup_block
	assert global_pickup_block.index("if ( cgs.customSettingsMask & CUSTOM_SETTING_QUAD_HOG ) {") < global_pickup_block.index(
		"CG_AddItemPickupAnnouncerSound( item );"
	)
	assert global_pickup_block.index("CG_AddItemPickupAnnouncerSound( item );") < global_pickup_block.index(
		"CG_SpectatorTrackEvent( es->groundEntityNum, CG_SPECTATOR_TRACK_POWERUP );"
	)
	assert "CG_SpectatorTrackEvent(" not in powerup_event_block
