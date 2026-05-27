from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


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


def test_spectator_respawn_eflag_alias_drives_cgame_specresp_command() -> None:
	bg_public = _read("src/code/game/bg_public.h")
	cg_playerstate = _read("src/code/cgame/cg_playerstate.c")
	respawn_block = _block_from_marker(cg_playerstate, "void CG_Respawn")

	assert "#define\tEF_VOTED\t\t\t0x00004000" in bg_public
	assert "#define\tEF_SPECTATOR_RESPAWN\t0x00004000" in bg_public
	assert "if ( cg.predictedPlayerState.eFlags & EF_SPECTATOR_RESPAWN ) {" in respawn_block
	assert 'trap_SendClientCommand( "specresp" );' in respawn_block
	assert respawn_block.index("if ( cg.predictedPlayerState.eFlags & EF_SPECTATOR_RESPAWN ) {") < respawn_block.index('trap_SendClientCommand( "specresp" );')
	assert "& 0x00004000" not in respawn_block


def test_qagame_team_change_and_spawn_publish_spectator_respawn_state() -> None:
	g_cmds = _read("src/code/game/g_cmds.c")
	g_client = _read("src/code/game/g_client.c")
	apply_block = _block_from_marker(g_cmds, "static void G_ApplyTeamChange")
	spawn_block = _block_from_marker(g_client, "void ClientSpawn")

	assert "client->ps.eFlags |= EF_SPECTATOR_RESPAWN;" in apply_block
	assert "client->ps.eFlags &= ~EF_SPECTATOR_RESPAWN;" in apply_block
	assert apply_block.index("client->ps.eFlags |= EF_SPECTATOR_RESPAWN;") < apply_block.index("client->sess.sessionTeam = team;")
	assert apply_block.index("client->sess.sessionTeam = team;") < apply_block.index("G_SyncSpectatorItemStatesForClient( clientNum );")

	assert "if ( client->sess.sessionTeam == TEAM_SPECTATOR ) {" in spawn_block
	assert "client->ps.eFlags |= EF_SPECTATOR_RESPAWN;" in spawn_block
	assert "client->ps.eFlags &= ~EF_SPECTATOR_RESPAWN;" in spawn_block
	assert "flags = client->ps.eFlags & ( EF_TELEPORT_BIT | EF_SPECTATOR_RESPAWN | EF_TEAMVOTED );" in spawn_block
	assert "flags ^= EF_TELEPORT_BIT;" in spawn_block
	assert spawn_block.index("client->ps.eFlags |= EF_SPECTATOR_RESPAWN;") < spawn_block.index("flags ^= EF_TELEPORT_BIT;")
	assert spawn_block.index("flags ^= EF_TELEPORT_BIT;") < spawn_block.index("client->ps.eFlags = flags;")
	assert "never clear the voted flag" not in spawn_block


def test_followed_snapshot_preserves_observer_spectator_state_bit() -> None:
	g_active = _read("src/code/game/g_active.c")
	end_frame_block = _block_from_marker(g_active, "void SpectatorClientEndFrame")

	assert "flags = ( cl->ps.eFlags & ~( EF_SPECTATOR_RESPAWN | EF_TEAMVOTED ) ) |" in end_frame_block
	assert "( ent->client->ps.eFlags & ( EF_SPECTATOR_RESPAWN | EF_TEAMVOTED ) );" in end_frame_block
	assert "ent->client->ps = cl->ps;" in end_frame_block
	assert "ent->client->ps.pm_type = PM_SPECTATOR;" in end_frame_block
	assert "ent->client->ps.pm_flags |= PMF_FOLLOW;" in end_frame_block
	assert "ent->client->ps.eFlags = flags;" in end_frame_block
	assert end_frame_block.index("flags = ( cl->ps.eFlags") < end_frame_block.index("ent->client->ps = cl->ps;")
	assert end_frame_block.index("ent->client->ps.pm_flags |= PMF_FOLLOW;") < end_frame_block.index("ent->client->ps.eFlags = flags;")


def test_specresp_and_team_entry_resync_live_spectator_item_state() -> None:
	g_cmds = _read("src/code/game/g_cmds.c")
	g_items = _read("src/code/game/g_items.c")
	client_command = _block_from_marker(g_cmds, "void ClientCommand")
	apply_block = _block_from_marker(g_cmds, "static void G_ApplyTeamChange")
	sync_block = _block_from_marker(g_items, "void G_SyncSpectatorItemStatesForClient")

	assert 'else if ( !Q_stricmp( cmd, "specresp" ) )' in client_command
	assert "G_SyncSpectatorItemStatesForClient( clientNum );" in client_command
	assert "if ( team == TEAM_SPECTATOR ) {" in apply_block
	assert "G_SyncSpectatorItemStatesForClient( clientNum );" in apply_block

	assert "if ( !G_IsSpectatorItemSyncClient( clientNum ) ) {" in sync_block
	assert "for ( i = level.maxclients; i < level.num_entities; i++ ) {" in sync_block
	assert "G_SendSpectatorItemStateToClient( clientNum, &g_entities[i], qtrue );" in sync_block


def test_spectator_item_event_payload_matches_cgame_cache_decoder() -> None:
	g_items = _read("src/code/game/g_items.c")
	cg_draw = _read("src/code/cgame/cg_draw.c")
	send_block = _block_from_marker(g_items, "static void G_SendSpectatorItemStateToClient")
	record_block = _block_from_marker(cg_draw, "void CG_RecordSpectatorItemPickup")

	for expected in (
		"te = G_TempEntity( itemEnt->s.pos.trBase, EV_ITEM_PICKUP_SPEC );",
		"te->r.svFlags |= SVF_SINGLECLIENT;",
		"te->r.singleClient = clientNum;",
		"te->s.groundEntityNum = itemEnt->spectatorItemPickupClientNum;",
		"te->s.constantLight = itemEnt->spectatorItemPickupPalette;",
		"te->s.origin[0] = (float)itemEnt->nextthink;",
		"te->s.origin[1] = (float)( g_gametype.integer == GT_TOURNAMENT );",
		"te->s.clientNum = itemEnt->s.modelindex;",
		"te->s.frame = itemEnt->spectatorItemPickupLayoutOrder;",
		"te->s.loopSound = initialSync ? 1 : 0;",
		"te->s.modelindex2 = 0;",
	):
		assert expected in send_block

	for expected in (
		"clientNum = es->groundEntityNum - 1;",
		"itemNum = es->clientNum;",
		"pickup->palette = es->constantLight;",
		"pickup->itemNum = itemNum;",
		"pickup->remainingTime = (int)es->origin[0] - cg.time;",
		"pickup->duelLayout = (int)es->origin[1];",
		"pickup->layoutOrder = es->frame * ( ( es->loopSound > 0 ) ? 2 : 1 );",
		"VectorCopy( es->pos.trBase, pickup->origin );",
	):
		assert expected in record_block


def test_item_touch_records_owner_state_before_broadcasting_hidden_respawn() -> None:
	g_items = _read("src/code/game/g_items.c")
	record_block = _block_from_marker(g_items, "static void G_RecordSpectatorItemPickup")
	touch_block = _block_from_marker(g_items, "void Touch_Item")

	assert "itemEnt->spectatorItemPickupClientNum = player->s.number + 1;" in record_block
	assert "itemEnt->spectatorItemPickupPalette = G_GetSpectatorItemPickupPalette( player );" in record_block
	assert "itemEnt->spectatorItemPickupLayoutOrder = G_GetSpectatorItemPickupLayoutOrder( player );" in record_block

	assert "G_RecordSpectatorItemPickup( ent, other, respawn );" in touch_block
	assert "ent->r.svFlags |= SVF_NOCLIENT;" in touch_block
	assert "ent->s.eFlags |= EF_NODRAW;" in touch_block
	assert "ent->nextthink = level.time + respawn * 1000;" in touch_block
	assert "trap_LinkEntity( ent );" in touch_block
	assert "G_BroadcastSpectatorItemState( ent );" in touch_block
	record_pos = touch_block.index("G_RecordSpectatorItemPickup( ent, other, respawn );")
	assert record_pos < touch_block.index("ent->s.eFlags |= EF_NODRAW;", record_pos)
	assert touch_block.index("trap_LinkEntity( ent );") < touch_block.index("G_BroadcastSpectatorItemState( ent );")


def test_cgame_event_filter_and_overlay_update_consume_spectator_item_state() -> None:
	cg_event = _read("src/code/cgame/cg_event.c")
	cg_draw = _read("src/code/cgame/cg_draw.c")
	cg_main = _read("src/code/cgame/cg_main.c")
	filter_block = _block_from_marker(cg_event, "static qboolean CG_IsSpectatorItemPickupEvent")
	event_block = _block_from_marker(cg_event, "void CG_EntityEvent")
	update_block = _block_from_marker(cg_draw, "void CG_UpdateSpectatorItemPickups")
	draw_block = _block_from_marker(cg_draw, "static void CG_DrawSpectatorItemPickups")

	assert "if ( !es || es->eType <= ET_EVENTS ) {" in filter_block
	assert "if ( es->groundEntityNum <= 0 || es->groundEntityNum > MAX_CLIENTS ) {" in filter_block
	assert "if ( es->clientNum <= 0 || es->clientNum >= bg_numItems ) {" in filter_block
	assert "case IT_POWERUP:" in filter_block
	assert "case IT_HEALTH:" in filter_block
	assert "case IT_ARMOR:" in filter_block
	assert "if ( event == EV_ITEM_PICKUP_SPEC && CG_IsSpectatorItemPickupEvent( es ) ) {" in event_block
	assert "CG_RecordSpectatorItemPickup( es );" in event_block

	assert "if ( !CG_IsSpectatorItemPickupModeActive() ) {" in update_block
	assert "pickup.remainingTime -= cg.frametime;" in update_block
	assert "qsort( activePickups, liveCount, sizeof( activePickups[0] ), CG_CompareSpectatorItemPickups );" in update_block
	assert "if ( cg_specItemTimers.integer <= 0 || cg.spectatorItemPickupCount <= 0 ) {" in draw_block
	assert "if ( !CG_IsSpectatorItemPickupModeActive() ) {" in draw_block
	assert "if ( !CG_IsSpectatorItemPickupVisible( pickup ) ) {" in draw_block

	for expected in (
		'{ &cg_specItemTimers, "cg_specItemTimers", "7", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "15" },',
		'{ &cg_specItemTimersSize, "cg_specItemTimersSize", "0.24", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0.12", "0.35" },',
		'{ &cg_specItemTimersX, "cg_specItemTimersX", "10", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "640" },',
		'{ &cg_specItemTimersY, "cg_specItemTimersY", "200", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "480" },',
	):
		assert expected in cg_main


def test_mapping_ledgers_record_cross_binary_spectator_state_reconstruction() -> None:
	qagame_map = _read("references/symbol-maps/qagame.json")
	cgame_map = _read("references/symbol-maps/cgame.json")
	qagame_mapping = _read("docs/reverse-engineering/qagame-mapping.md")
	cgame_mapping = _read("docs/reverse-engineering/cgame-mapping.md")
	note = _read("docs/reverse-engineering/spectator-client-state-wiring-reconstruction-2026-05-27.md")

	for expected in (
		'"address": "0x10040440"',
		'"normalized_name": "G_ApplyTeamChange"',
		'"address": "0x1003BC30"',
		'"normalized_name": "ClientSpawn"',
		'"address": "0x1004EAC0"',
		'"normalized_name": "G_SendSpectatorItemStateToClient"',
	):
		assert expected in qagame_map

	for expected in (
		'"address": "0x100433D0"',
		'"normalized_name": "CG_Respawn"',
		'"address": "0x10019D90"',
		'"normalized_name": "CG_RecordSpectatorItemPickup"',
		'"address": "0x1000F700"',
		'"normalized_name": "CG_DrawSpectatorItemPickups"',
	):
		assert expected in cgame_map

	assert "EF_SPECTATOR_RESPAWN" in qagame_mapping
	assert "EF_SPECTATOR_RESPAWN" in cgame_mapping
	assert "0x10040440" in note
	assert "0x1003BC30" in note
	assert "0x100433D0" in note
	assert "0x1004EAC0" in note
	assert "Scoped spectator client-state parity: before 99.90% -> after 99.97%." in note
