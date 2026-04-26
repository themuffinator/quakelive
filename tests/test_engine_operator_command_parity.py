from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SV_WORLD = REPO_ROOT / "src" / "code" / "server" / "sv_world.c"

# Retail command-owner evidence for this focused operator slice comes from
# `references/analysis/quakelive_symbol_aliases.json` plus the paired HLIL
# owners in `references/hlil/quakelive/quakelive_steam.exe/`:
# `sub_4DDCE0` -> `SV_Map_f`
# `sub_4DEEA0` -> `SV_ConSay_f`
# `sub_4DE050` -> retail `arena` command owner
# `sub_4DE670` -> `SV_MapRestart_f`
# `sub_4DEA40` -> `SV_Kick_f`
# `sub_4DEBE0` -> `SV_KickNum_f`
# `sub_4DEF40` -> `SV_Serverinfo_f`
# `sub_4DEFA0` -> `SV_DumpUser_f`
# `sub_4DF000` -> `SV_KillServer_f`
# `sub_4DF010` -> `steam_downloadugc`
# `sub_4DF070` -> `steam_subscribeugc`
# `sub_4DF0D0` -> `steam_unsubscribeugc`
# `sub_4DF130` -> `SV_AddOperatorCommands`
# `sub_45E8B0` -> `StartRandomMap_f`
# `sub_45ED90` -> `ReloadArenaDefinitions_f`
# `sub_45F340` -> `MapPool_Reload_f`
# `sub_45FB40` -> `Factory_Reload_f`
# `sub_4E5D20` -> `SV_SectorList_f`


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	in_string = False
	escaped = False
	for index in range(brace_start, len(text)):
		char = text[index]

		if in_string:
			if escaped:
				escaped = False
			elif char == "\\":
				escaped = True
			elif char == '"':
				in_string = False
			continue

		if char == '"':
			in_string = True
		elif char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def test_operator_command_registration_matches_retail_quakelive_surface() -> None:
	sv_ccmds = (REPO_ROOT / "src/code/server/sv_ccmds.c").read_text(encoding="utf-8")

	add_block = _extract_function_block(sv_ccmds, "void SV_AddOperatorCommands( void ) {")

	assert 'Cmd_AddCommand ("kick", SV_Kick_f);' in add_block
	assert 'Cmd_AddCommand ("clientkick", SV_KickNum_f);' in add_block
	assert 'Cmd_AddCommand ("serverinfo", SV_Serverinfo_f);' in add_block
	assert 'Cmd_AddCommand ("dumpuser", SV_DumpUser_f);' in add_block
	assert 'Cmd_AddCommand ("map_restart", SV_MapRestart_f);' in add_block
	assert 'Cmd_AddCommand ("sectorlist", SV_SectorList_f);' in add_block
	assert 'Cmd_AddCommand ("map", SV_Map_f);' in add_block
	assert 'Cmd_AddCommand ("arena", SV_Arena_f);' in add_block
	assert 'Cmd_AddCommand ("devmap", SV_Map_f);' in add_block
	assert 'Cmd_AddCommand ("killserver", SV_KillServer_f);' in add_block
	assert 'Cmd_AddCommand ("steam_downloadugc", SV_SteamCmd_DownloadUGC_f);' in add_block
	assert 'Cmd_AddCommand ("steam_subscribeugc", SV_SteamCmd_SubscribeUGC_f);' in add_block
	assert 'Cmd_AddCommand ("steam_unsubscribeugc", SV_SteamCmd_UnsubscribeUGC_f);' in add_block
	assert 'Cmd_AddCommand ("startRandomMap", StartRandomMap_f);' in add_block
	assert 'Cmd_AddCommand ("reload_mappool", MapPool_Reload_f);' in add_block
	assert 'Cmd_AddCommand ("reload_arenas", ReloadArenaDefinitions_f);' in add_block
	assert 'Cmd_AddCommand ("reload_factories", Factory_Reload_f);' in add_block
	assert "if( com_dedicated->integer ) {" in add_block
	assert 'Cmd_AddCommand ("say", SV_ConSay_f);' in add_block

	assert 'Cmd_AddCommand ("heartbeat", SV_Heartbeat_f);' not in add_block
	assert 'Cmd_AddCommand ("banUser", SV_Ban_f);' not in add_block
	assert 'Cmd_AddCommand ("banClient", SV_BanNum_f);' not in add_block
	assert 'Cmd_AddCommand ("systeminfo", SV_Systeminfo_f);' not in add_block
	assert 'Cmd_AddCommand ("spmap", SV_Map_f);' not in add_block
	assert 'Cmd_AddCommand ("spdevmap", SV_Map_f);' not in add_block


def test_operator_command_handlers_match_retail_kick_map_and_reload_contracts() -> None:
	sv_ccmds = (REPO_ROOT / "src/code/server/sv_ccmds.c").read_text(encoding="utf-8")
	sv_world = SV_WORLD.read_text(encoding="utf-8")

	kick_block = _extract_function_block(sv_ccmds, "static void SV_Kick_f( void ) {")
	clientkick_block = _extract_function_block(sv_ccmds, "static void SV_KickNum_f( void ) {")
	serverinfo_block = _extract_function_block(sv_ccmds, "static void SV_Serverinfo_f( void ) {")
	dumpuser_block = _extract_function_block(sv_ccmds, "static void SV_DumpUser_f( void ) {")
	map_restart_block = _extract_function_block(sv_ccmds, "static void SV_MapRestart_f( void ) {")
	map_block = _extract_function_block(sv_ccmds, "static void SV_Map_f( void ) {")
	arena_block = _extract_function_block(sv_ccmds, "static void SV_Arena_f( void ) {")
	killserver_block = _extract_function_block(sv_ccmds, "static void SV_KillServer_f( void ) {")
	random_map_block = _extract_function_block(sv_ccmds, "static void StartRandomMap_f( void ) {")
	reload_pool_block = _extract_function_block(sv_ccmds, "static void MapPool_Reload_f( void ) {")
	reload_arenas_block = _extract_function_block(sv_ccmds, "static void ReloadArenaDefinitions_f( void ) {")
	reload_factories_block = _extract_function_block(sv_ccmds, "static void Factory_Reload_f( void ) {")
	say_block = _extract_function_block(sv_ccmds, "static void SV_ConSay_f( void ) {")
	download_block = _extract_function_block(sv_ccmds, "static void SV_SteamCmd_DownloadUGC_f( void ) {")
	subscribe_block = _extract_function_block(sv_ccmds, "static void SV_SteamCmd_SubscribeUGC_f( void ) {")
	unsubscribe_block = _extract_function_block(sv_ccmds, "static void SV_SteamCmd_UnsubscribeUGC_f( void ) {")
	request_helper_block = _extract_function_block(sv_ccmds, "static void SV_SteamWorkshop_RequestDownload( uint32_t itemIdLow, uint32_t itemIdHigh ) {")
	subscribe_helper_block = _extract_function_block(sv_ccmds, "static void SV_SteamWorkshop_SubscribeItem( uint32_t itemIdLow, uint32_t itemIdHigh ) {")
	unsubscribe_helper_block = _extract_function_block(sv_ccmds, "static void SV_SteamWorkshop_UnsubscribeItem( uint32_t itemIdLow, uint32_t itemIdHigh ) {")
	sectorlist_block = _extract_function_block(sv_world, "void SV_SectorList_f( void ) {")

	assert 'reason = ( Cmd_Argc() > 2 ) ? Cmd_Argv( 2 ) : NULL;' in kick_block
	assert 'dropReason = va( "was kicked: %s", reason );' in kick_block
	assert 'SV_DropClient( cl, dropReason );' in kick_block
	assert 'SV_SendServerCommand(NULL, "print \\"%s\\"", "Cannot kick host player.\\n");' in kick_block

	assert 'Com_Printf ("Usage: kicknum <client number>\\n");' in clientkick_block
	assert 'SV_DropClient( cl, "was kicked" );' in clientkick_block

	assert 'Com_Printf ("Server info settings:\\n");' in serverinfo_block
	assert 'Info_Print ( Cvar_InfoString( CVAR_SERVERINFO ) );' in serverinfo_block
	assert 'Com_Printf ("Usage: info <userid>\\n");' in dumpuser_block
	assert 'Com_Printf( "userinfo\\n" );' in dumpuser_block

	assert "SV_UpdateMapPoolRotationCvars();" in map_restart_block
	assert 'Cvar_Set( "ui_singlePlayerActive", "1" );' in map_block
	assert 'Cvar_Set( "ui_priv", "3" );' in map_block

	assert 'Com_sprintf( path, sizeof( path ), "scripts/%s.sp_arena", arenaName );' in arena_block
	assert 'Com_Printf( "No arena name passed\\n" );' in arena_block
	assert 'Com_Printf( "^1file not found: %s\\n", path );' in arena_block
	assert 'Com_Printf( "Fraglimit was an invalid value! Valid values are 1 or greater. Setting to 20.\\n" );' in arena_block
	assert 'Com_Printf( "timelimit was an invalid value! Valid values are 0 or greater. Setting to 0.\\n" );' in arena_block
	assert 'Com_Printf( "bot_skill was an invalid value! Valid values are 1 - 5. Setting to 4.\\n" );' in arena_block
	assert 'Com_Printf( "Unknown value in %s\\n", path );' in arena_block
	assert 'SV_SpawnServer( mapName, qtrue );' in arena_block
	assert 'Cvar_Set( "sv_cheats", "0" );' in arena_block

	assert 'SV_Shutdown( "killserver" );' in killserver_block
	assert 'Cbuf_AddText( va( "map %s %s\\n", entry->mapName, entry->factoryId ) );' in random_map_block
	assert 'Com_Printf( "reloading map pool...\\n" );' in reload_pool_block
	assert 'SV_MapPoolLoadFromFile( sv_mapPoolFile ? sv_mapPoolFile->string : "mappool.txt" );' in reload_pool_block
	assert 'Com_Printf( "reloading arena definitions...\\n" );' in reload_arenas_block
	assert 'SV_LoadArenas();' in reload_arenas_block
	assert "SV_FactoryResetRegistry( qtrue );" in reload_factories_block
	assert "SV_FactoryEnsureRegistryLoaded();" in reload_factories_block
	assert "s_svFactoryRegistryLoaded = qtrue;" not in reload_factories_block

	assert 'for ( i = 0 ; i < AREA_NODES ; i++ ) {' in sectorlist_block
	assert 'for ( ent = sec->entities ; ent ; ent = ent->nextEntityInWorldSector ) {' in sectorlist_block
	assert 'Com_Printf( "sector %i: %i entities\\n", i, c );' in sectorlist_block

	assert 'Com_Printf( "Server is not running.\\n" );' in say_block
	assert 'Q_strncpyz( text, Cmd_Args(), sizeof( text ) );' in say_block
	assert 'if ( *p == \'\"\' ) {' in say_block
	assert 'SV_SendServerCommand( NULL, "chat %d \\"Server: %s\\n\\"", MAX_CLIENTS - 1, p );' in say_block

	assert 'Com_Printf( "Usage: steam_downloadugc <itemid>\\n" );' in download_block
	assert 'sscanf( Cmd_Argv( 1 ), "%llu", &itemId );' in download_block
	assert "SV_SteamWorkshop_RequestDownload( itemIdLow, itemIdHigh );" in download_block
	assert "SV_WorkshopServiceSupportsSteamCommands()" in request_helper_block
	assert 'Com_sprintf( detail, sizeof( detail ), "Workshop item %llu: in cache.", itemId );' in request_helper_block
	assert 'Com_sprintf( detail, sizeof( detail ), "Workshop item %llu: download", itemId );' in request_helper_block
	assert "QL_Steamworks_DownloadItem( itemIdLow, itemIdHigh, qtrue )" in request_helper_block
	assert '"download request failed"' not in request_helper_block

	assert 'Com_Printf( "Usage: steam_subscribeugc <itemid>\\n" );' in subscribe_block
	assert 'sscanf( Cmd_Argv( 1 ), "%llu", &itemId );' in subscribe_block
	assert "SV_SteamWorkshop_SubscribeItem( itemIdLow, itemIdHigh );" in subscribe_block
	assert "(void)QL_Steamworks_SubscribeItem( itemIdLow, itemIdHigh );" in subscribe_helper_block
	assert "QL_Steamworks_GetItemState( itemIdLow, itemIdHigh ) & 4u" in subscribe_helper_block
	assert "FS_Restart( sv.checksumFeed );" in subscribe_helper_block
	assert '"subscribe requested"' not in subscribe_helper_block
	assert '"subscribe request failed"' not in subscribe_helper_block

	assert 'Com_Printf( "Usage: steam_unsubscribeugc <itemid>\\n" );' in unsubscribe_block
	assert 'sscanf( Cmd_Argv( 1 ), "%llu", &itemId );' in unsubscribe_block
	assert "SV_SteamWorkshop_UnsubscribeItem( itemIdLow, itemIdHigh );" in unsubscribe_block
	assert "(void)QL_Steamworks_UnsubscribeItem( itemIdLow, itemIdHigh );" in unsubscribe_helper_block
	assert '"unsubscribe requested"' not in unsubscribe_helper_block
	assert '"unsubscribe request failed"' not in unsubscribe_helper_block


def test_spawn_restart_and_game_consumers_follow_retail_nextmap_payload_wiring() -> None:
	sv_ccmds = (REPO_ROOT / "src/code/server/sv_ccmds.c").read_text(encoding="utf-8")
	sv_init = (REPO_ROOT / "src/code/server/sv_init.c").read_text(encoding="utf-8")
	g_main = (REPO_ROOT / "src/code/game/g_main.c").read_text(encoding="utf-8")
	g_cmds = (REPO_ROOT / "src/code/game/g_cmds.c").read_text(encoding="utf-8")

	init_data_block = _extract_function_block(sv_ccmds, "void SV_InitRetailOperatorData( void ) {")
	update_rotation_block = _extract_function_block(sv_ccmds, "void SV_UpdateMapPoolRotationCvars( void ) {")
	build_nextmaps_block = _extract_function_block(sv_ccmds, "static void SV_MapPoolBuildNextMapsCvar( void ) {")
	spawn_block = _extract_function_block(sv_init, "void SV_SpawnServer( char *server, qboolean killBots ) {")
	init_block = _extract_function_block(sv_init, "void SV_Init (void) {")
	publish_rotation_block = _extract_function_block(g_main, "static void G_PublishRotationPreviewConfigstrings( void ) {")
	select_slot_block = _extract_function_block(g_main, "static int G_SelectNextMapVoteSlot( void ) {")
	exit_block = _extract_function_block(g_main, "void ExitLevel (void) {")
	nextmap_vote_block = _extract_function_block(g_cmds, "qboolean G_HandleNextMapVote( gentity_t *ent ) {")

	assert "SV_LoadArenas();" in init_data_block
	assert "SV_FactoryEnsureRegistryLoaded();" in init_data_block
	assert 'SV_MapPoolLoadFromFile( sv_mapPoolFile ? sv_mapPoolFile->string : "mappool.txt" );' in init_data_block
	assert "SV_MapPoolUpdateNextMap();" in update_rotation_block
	assert "SV_MapPoolBuildNextMapsCvar();" in update_rotation_block
	assert 'Info_SetValueForKey( nextmaps, va( "map_%i", slot ), entry->mapName );' in build_nextmaps_block
	assert 'Info_SetValueForKey( nextmaps, va( "cfg_%i", slot ), entry->factoryId );' in build_nextmaps_block
	assert 'Info_SetValueForKey( nextmaps, va( "gt_%i", slot ), entry->factoryTitle );' in build_nextmaps_block
	assert 'Cvar_Set( "nextmaps", nextmaps );' in build_nextmaps_block

	assert "SV_UpdateMapPoolRotationCvars();" in spawn_block
	assert "SV_InitRetailOperatorData();" in init_block
	assert 'value = Info_ValueForKey( nextmaps, key );' in publish_rotation_block
	assert 'value = Info_ValueForKey( nextmaps, key );' in select_slot_block
	assert 'value = Info_ValueForKey( nextmaps, key );' in exit_block
	assert 'Q_strncpyz( mapName, Info_ValueForKey( nextmaps, key ), sizeof( mapName ) );' in nextmap_vote_block
	assert 'Q_strncpyz( voteLabel, Info_ValueForKey( nextmaps, key ), sizeof( voteLabel ) );' in nextmap_vote_block
