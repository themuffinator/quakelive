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


def test_cgame_binding_bridge_uses_direct_retail_copy_path() -> None:
	client = _read("src/code/client/cl_cgame.c")

	assert "case CG_KEY_GETBINDINGBUF:" in client
	assert 'Q_strncpyz( VMA(2), Key_GetBinding( args[1] ), args[3] );' in client


def test_team_balance_helper_is_split_out_for_setteam_and_readyup() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "static qboolean Team_CountsBalanced( int redCount, int blueCount ) {" in game_cmds
	assert "if ( g_teamForceBalance.integer && !Team_CountsBalanced( redCount, blueCount ) ) {" in game_cmds
	assert "if ( !Team_CountsBalanced( nextRedCount, nextBlueCount ) ) {" in game_cmds


def test_setteam_recovered_executor_boundary_matches_retail_wiring() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	game_combat = _read("src/code/game/g_combat.c")
	qagame_map = _read("references/symbol-maps/qagame.json")
	revenge_block = _block_from_marker(game_combat, "void G_ClearClientRevengeState")
	apply_block = _block_from_marker(game_cmds, "static void G_ApplyTeamChange")
	setteam_block = _block_from_marker(game_cmds, "void SetTeam")
	cmd_team_block = _block_from_marker(game_cmds, "void Cmd_Team_f")

	assert '"address": "0x10040440"' in qagame_map
	assert '"normalized_name": "G_ApplyTeamChange"' in qagame_map
	assert '"address": "0x100406D0"' in qagame_map
	assert '"normalized_name": "SetTeam"' in qagame_map
	assert '"address": "0x10040D90"' in qagame_map
	assert '"normalized_name": "Cmd_Team_f"' in qagame_map

	assert "static void G_ApplyTeamChange( gentity_t *ent, team_t team, spectatorState_t specState, int specClient ) {" in game_cmds
	assert "void G_ClearClientRevengeState( int clientNum ) {" in game_combat
	assert "for ( i = 0; i < level.numConnectedClients; i++ ) {" in revenge_block
	assert "otherClientNum = level.sortedClients[i];" in revenge_block
	assert "other->revengeKillStreaks[clientNum] = 0;" in revenge_block
	assert "G_ApplyTeamChange( ent, (team_t)team, specState, specClient );" in setteam_block
	assert "CalculateRanks();" in setteam_block
	assert setteam_block.index("G_ApplyTeamChange( ent, (team_t)team, specState, specClient );") < setteam_block.index("CalculateRanks();")
	assert 'if ( !s ) {' in setteam_block
	assert 's = "";' in setteam_block
	assert "if ( level.numPlayingClients < 1 ) {" in setteam_block
	assert "specClient = FOLLOW_ACTIVE1;" in setteam_block
	assert "if ( level.numPlayingClients < 2 ) {" in setteam_block
	assert "specClient = FOLLOW_ACTIVE2;" in setteam_block
	assert "} else if ( g_gametype.integer == GT_RED_ROVER ) {" in setteam_block
	assert setteam_block.index("} else if ( g_gametype.integer == GT_RED_ROVER ) {") < setteam_block.index("} else if ( g_gametype.integer >= GT_TEAM ) {")

	assert "clientNum = ent - g_entities;" in apply_block
	assert "oldTeam = client->sess.sessionTeam;" in apply_block
	assert "if ( client->ps.stats[STAT_HEALTH] <= 0 ) {" in apply_block
	assert "CopyToBodyQue( ent );" in apply_block
	assert "client->pers.teamState.state = TEAM_BEGIN;" in apply_block
	assert "G_RankSendPlayerStats( ent, qtrue );" in apply_block
	assert "G_RankResetClientStats( client );" in apply_block
	assert "player_die( ent, ent, ent, 100000, MOD_SWITCHTEAM );" in apply_block
	assert "client->sess.spectatorTime = (int)time( NULL );" in apply_block
	assert "client->sess.sessionTeam = team;" in apply_block
	assert "client->sess.spectatorState = specState;" in apply_block
	assert "client->sess.spectatorClient = specClient;" in apply_block
	assert "G_SyncSpectatorItemStatesForClient( clientNum );" in apply_block
	assert "TeamLeader( team );" in apply_block
	assert "SetLeader( team, clientNum );" in apply_block
	assert "CheckTeamLeader( oldTeam );" in apply_block
	assert "if ( g_gametype.integer != GT_RED_ROVER || team == TEAM_SPECTATOR ) {" in apply_block
	assert "BroadcastTeamChange( client, oldTeam );" in apply_block
	assert "G_ClearClientRevengeState( clientNum );" in apply_block
	assert "ClientUserinfoChanged( clientNum );" in apply_block
	assert "ClientBegin( clientNum );" in apply_block
	assert "G_RankSendPlayerSwitchTeam( ent, oldTeam, team );" in apply_block
	assert apply_block.index("G_ClearClientRevengeState( clientNum );") < apply_block.index("ClientUserinfoChanged( clientNum );")
	assert apply_block.index("ClientUserinfoChanged( clientNum );") < apply_block.index("ClientBegin( clientNum );")
	assert apply_block.index("ClientBegin( clientNum );") < apply_block.index("G_RankSendPlayerSwitchTeam( ent, oldTeam, team );")

	assert "if ( trap_Argc() < 2 ) {" in cmd_team_block
	assert "s = ConcatArgs( 1 );" in cmd_team_block
	assert "trap_Argv( 1, s" not in cmd_team_block


def test_revenge_counter_matrix_matches_retail_death_respawn_and_team_change_wiring() -> None:
	game_local = _read("src/code/game/g_local.h")
	game_client = _read("src/code/game/g_client.c")
	game_combat = _read("src/code/game/g_combat.c")
	qagame_overlay = _read("src/game/ql_game_types.h")
	spawn_block = _block_from_marker(game_client, "void ClientSpawn")
	disconnect_block = _block_from_marker(game_client, "void ClientDisconnect")
	death_block = _block_from_marker(game_combat, "void player_die")

	assert "int32_t revenge_kill_streaks[64];" in qagame_overlay
	assert "offsetof(ql_gclient_t, revenge_kill_streaks) == 0x3E4" in qagame_overlay
	assert "int\t\t\trevengeKillStreaks[MAX_CLIENTS];" in game_local
	assert "int\t\tsavedRevengeKillStreaks[MAX_CLIENTS];" in spawn_block
	assert "memcpy( savedRevengeKillStreaks, client->revengeKillStreaks, sizeof( savedRevengeKillStreaks ) );" in spawn_block
	assert "memcpy( client->revengeKillStreaks, savedRevengeKillStreaks, sizeof( client->revengeKillStreaks ) );" in spawn_block
	assert "attackerClientNum = attacker->s.number;" in death_block
	assert "victimClientNum = self->s.number;" in death_block
	assert "attacker->client->revengeKillStreaks[victimClientNum]++;" in death_block
	assert "if ( self->client->revengeKillStreaks[attackerClientNum] > 2 ) {" in death_block
	assert "attacker->client->ps.persistant[PERS_PLAYEREVENTS] ^= PLAYEREVENT_REVENGE;" in death_block
	assert 'G_RankSendPlayerMedal( attacker, "REVENGE" );' in death_block
	assert "self->client->revengeKillStreaks[attackerClientNum] = 0;" in death_block
	assert "void G_ClearClientRevengeState( int clientNum );" in game_local
	assert "G_ClearClientRevengeState( clientNum );" in disconnect_block
	assert disconnect_block.index("StopFollowing( &g_entities[i] );") < disconnect_block.index("G_ClearClientRevengeState( clientNum );")


def test_game_say_reconstructs_retail_chat_tokens_and_message_limits() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	qagame_map = _read("references/symbol-maps/qagame.json")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt")
	formatter_block = _block_from_marker(game_cmds, "static void G_ExpandChatTokens")
	say_block = _block_from_marker(game_cmds, "void G_Say")
	bot_say_block = _block_from_marker(game_cmds, "static void Cmd_BotSay_f")
	client_command_block = _block_from_marker(game_cmds, "void ClientCommand")

	assert '"G_Say: truncate at %d characters\\n"' in say_block
	assert "strlen( chatText ) > MAX_SAY_TEXT" in say_block
	assert "G_ExpandChatTokens( ent, chatText, text, sizeof( text ) );" in say_block
	assert "originalMode = mode;" in say_block
	assert "( originalMode == SAY_TEAM || originalMode == SAY_TELL ) && ent->client" in say_block
	assert say_block.index("originalMode = mode;") < say_block.index("if ( g_gametype.integer < GT_TEAM && mode == SAY_TEAM )")
	assert "Q_strncpyz( text, chatText, sizeof( text ) );" in say_block

	for expected in (
		"case '#':",
		"case 'a':",
		"case 'h':",
		"case 'w':",
		"ent->client->ps.stats[STAT_ARMOR]",
		"ent->client->ps.stats[STAT_HEALTH] < 1 ? 0 : ent->client->ps.stats[STAT_HEALTH]",
		"weapon == WP_GAUNTLET",
		'Com_sprintf( tokenText, sizeof( tokenText ), "%s [%d]", BG_WeaponName( (weapon_t)weapon ), ent->client->ps.ammo[weapon] );',
	):
		assert expected in formatter_block

	assert '"Chat token output buffer overflow...\\n"' in game_cmds
	assert '"normalized_name": "G_ExpandChatTokens"' in qagame_map
	assert "Chat token output buffer overflo" in qagame_hlil
	assert '"G_Say: truncate at %d characters' in qagame_hlil
	assert '"normalized_name": "Cmd_BotSay_f"' in qagame_map
	assert 'sub_10070a40("botSay"' in qagame_hlil
	assert "sub_10041cc0" in qagame_hlil

	assert "if ( !( ent->r.svFlags & SVF_BOT ) ) {" in bot_say_block
	assert "trap_Argv( 1, arg, sizeof( arg ) );" in bot_say_block
	assert "targetNum = atoi( arg );" in bot_say_block
	assert "trap_Argv( 2, arg, sizeof( arg ) );" in bot_say_block
	assert "holdSeconds = atoi( arg );" in bot_say_block
	assert "if ( holdSeconds < 0 ) {" in bot_say_block
	assert "p = ConcatArgs( 3 );" in bot_say_block
	assert 'G_LogPrintf( "botSay: %s for %i seconds to client %i\\n", ent->client->pers.netname, holdSeconds, targetNum );' in bot_say_block
	assert 'trap_SendServerCommand( targetNum, va( "bchat \\"%s%c%c%s\\" %i", name, Q_COLOR_ESCAPE, COLOR_GREEN, p, holdSeconds ) );' in bot_say_block
	assert 'if (Q_stricmp (cmd, "botSay") == 0) {' in client_command_block
	assert "Cmd_BotSay_f( ent );" in client_command_block
	assert client_command_block.index('if (Q_stricmp (cmd, "tell") == 0)') < client_command_block.index('if (Q_stricmp (cmd, "botSay") == 0)')
	assert client_command_block.index('if (Q_stricmp (cmd, "botSay") == 0)') < client_command_block.index('if (Q_stricmp (cmd, "vsay") == 0)')


def test_game_chat_voice_client_command_tranche_matches_retail_ladder() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	qagame_map = _read("references/symbol-maps/qagame.json")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt")
	client_command_block = _block_from_marker(game_cmds, "void ClientCommand")
	say_block = _block_from_marker(game_cmds, "static void Cmd_Say_f")
	tell_block = _block_from_marker(game_cmds, "static void Cmd_Tell_f")
	bot_say_block = _block_from_marker(game_cmds, "static void Cmd_BotSay_f")
	voice_block = _block_from_marker(game_cmds, "static void Cmd_Voice_f")
	voice_tell_block = _block_from_marker(game_cmds, "static void Cmd_VoiceTell_f")
	voice_to_block = _block_from_marker(game_cmds, "static void G_VoiceTo")
	voice_public_block = _block_from_marker(game_cmds, "void G_Voice")
	voice_taunt_block = _block_from_marker(game_cmds, "static void Cmd_VoiceTaunt_f")

	for normalized_name in (
		"Cmd_Say_f",
		"Cmd_Tell_f",
		"Cmd_BotSay_f",
		"Cmd_Voice_f",
		"Cmd_VoiceTell_f",
		"Cmd_VoiceTaunt_f",
		"ClientCommand",
	):
		assert f'"normalized_name": "{normalized_name}"' in qagame_map

	for hlil_signal in (
		'sub_10070a40("say"',
		'sub_10070a40("say_team"',
		'sub_10070a40("tell"',
		'sub_10070a40("botSay"',
		'sub_10070a40("vsay"',
		'sub_10070a40("vsay_team"',
		'sub_10070a40("vtell"',
		'sub_10070a40("vosay"',
		'sub_10070a40("vosay_team"',
		'sub_10070a40("votell"',
		"sub_10041b60",
		"sub_10041b90",
		"sub_10041cc0",
		"sub_10041e40",
		"sub_10041e60",
		"vtell: %s to %s: %s",
	):
		assert hlil_signal in qagame_hlil
	assert 'sub_10070a40("complaint"' not in qagame_hlil

	dispatch_pairs = (
		('if (Q_stricmp (cmd, "say") == 0)', "Cmd_Say_f (ent, SAY_ALL, qfalse);"),
		('if (Q_stricmp (cmd, "say_team") == 0)', "Cmd_Say_f (ent, SAY_TEAM, qfalse);"),
		('if (Q_stricmp (cmd, "tell") == 0)', "Cmd_Tell_f ( ent );"),
		('if (Q_stricmp (cmd, "botSay") == 0)', "Cmd_BotSay_f( ent );"),
		('if (Q_stricmp (cmd, "vsay") == 0)', "Cmd_Voice_f (ent, SAY_ALL, qfalse, qfalse);"),
		('if (Q_stricmp (cmd, "vsay_team") == 0)', "Cmd_Voice_f (ent, SAY_TEAM, qfalse, qfalse);"),
		('if (Q_stricmp (cmd, "vtell") == 0)', "Cmd_VoiceTell_f ( ent, qfalse );"),
		('if (Q_stricmp (cmd, "vosay") == 0)', "Cmd_Voice_f (ent, SAY_ALL, qfalse, qtrue);"),
		('if (Q_stricmp (cmd, "vosay_team") == 0)', "Cmd_Voice_f (ent, SAY_TEAM, qfalse, qtrue);"),
		('if (Q_stricmp (cmd, "votell") == 0)', "Cmd_VoiceTell_f ( ent, qtrue );"),
	)
	for dispatch, handler in dispatch_pairs:
		assert dispatch in client_command_block
		assert handler in client_command_block
		assert client_command_block.index(dispatch) < client_command_block.index(handler)
	for current, following in zip(dispatch_pairs, dispatch_pairs[1:]):
		assert client_command_block.index(current[0]) < client_command_block.index(following[0])
	assert client_command_block.index('if (Q_stricmp (cmd, "vtaunt") == 0)') < client_command_block.index('if (Q_stricmp (cmd, "complaint") == 0)')

	assert "p = ConcatArgs( 1 );" in say_block
	assert 'G_FloodLimited( ent, ( mode == SAY_TEAM ) ? "using team chat" : "chatting", qtrue )' in say_block
	assert "G_Say( ent, NULL, mode, p );" in say_block
	assert "targetNum = atoi( arg );" in tell_block
	assert 'G_FloodLimited( ent, "sending tells", qtrue )' in tell_block
	assert 'G_LogPrintf( "tell: %s to %s: %s\\n", ent->client->pers.netname, target->client->pers.netname, p );' in tell_block
	assert "G_Say( ent, target, SAY_TELL, p );" in tell_block
	assert "if ( ent != target && !(ent->r.svFlags & SVF_BOT)) {" in tell_block
	assert "if ( !( ent->r.svFlags & SVF_BOT ) ) {" in bot_say_block
	assert 'trap_SendServerCommand( targetNum, va( "bchat \\"%s%c%c%s\\" %i", name, Q_COLOR_ESCAPE, COLOR_GREEN, p, holdSeconds ) );' in bot_say_block

	assert 'cmd = "vtchat";' in voice_to_block
	assert 'cmd = "vtell";' in voice_to_block
	assert 'cmd = "vchat";' in voice_to_block
	assert 'trap_SendServerCommand( other-g_entities, va("%s %d %d %d %s", cmd, voiceonly, ent->s.number, color, id));' in voice_to_block
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"You are muted.\\n\\"" );' in voice_public_block
	assert 'G_Printf( "voice: %s %s\\n", ent->client->pers.netname, id);' in voice_public_block
	assert 'action = voiceonly ? "using team voice commands" : "using team voice chat";' in voice_block
	assert 'action = voiceonly ? "using voice commands" : "using voice chat";' in voice_block
	assert "G_Voice( ent, NULL, mode, p, voiceonly );" in voice_block
	assert 'G_FloodLimited( ent, voiceonly ? "sending private voice commands" : "sending private voice chats", qtrue )' in voice_tell_block
	assert 'G_LogPrintf( "vtell: %s to %s: %s\\n", ent->client->pers.netname, target->client->pers.netname, id );' in voice_tell_block
	assert "G_Voice( ent, target, SAY_TELL, id, voiceonly );" in voice_tell_block
	assert "G_FloodLimited( ent, \"sending voice taunts\", qtrue )" in voice_taunt_block


def test_game_score_vote_cheat_client_command_tranche_matches_retail_ladder() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	qagame_map = _read("references/symbol-maps/qagame.json")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt")
	qagame_strings = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt")
	client_command_block = _block_from_marker(game_cmds, "void ClientCommand")
	score_block = _block_from_marker(game_cmds, "void Cmd_Score_f")
	acc_block = _block_from_marker(game_cmds, "void Cmd_Acc_f")
	pstats_block = _block_from_marker(game_cmds, "void Cmd_PStats_f")
	readyup_block = _block_from_marker(game_cmds, "void Cmd_ReadyUp_f")
	vote_block = _block_from_marker(game_cmds, "void Cmd_Vote_f")
	nextmap_vote_block = _block_from_marker(game_cmds, "qboolean G_HandleNextMapVote")
	give_block = _block_from_marker(game_cmds, "void Cmd_Give_f")
	god_block = _block_from_marker(game_cmds, "void Cmd_God_f")
	notarget_block = _block_from_marker(game_cmds, "void Cmd_Notarget_f")
	noclip_block = _block_from_marker(game_cmds, "void Cmd_Noclip_f")
	kill_block = _block_from_marker(game_cmds, "void Cmd_Kill_f")

	for normalized_name in (
		"Cmd_Score_f",
		"Cmd_Acc_f",
		"Cmd_Pstats_f",
		"Cmd_ReadyUp_f",
		"Cmd_Vote_f",
		"Cmd_Give_f",
		"Cmd_God_f",
		"Cmd_Notarget_f",
		"Cmd_Noclip_f",
		"Cmd_Kill_f",
		"ClientCommand",
	):
		assert f'"normalized_name": "{normalized_name}"' in qagame_map

	for hlil_signal in (
		'sub_10070a40("score"',
		'sub_10070a40("acc"',
		'sub_10070a40("pstats"',
		'data_10084f0c[0x8] = "readyup"',
		'data_10084f14[0x9] = "ragequit"',
		'sub_10070a40("vote"',
		'sub_10070a40("give"',
		'sub_10070a40("god"',
		'data_10084f34[0x9] = "notarget"',
		'data_10084f40[0x7] = "noclip"',
		'sub_10070a40("kill"',
		"acc %s",
		"pstats %s",
		"Vote cast.",
		"Kill is not enabled on this server.",
		"godmode ON",
		"notarget ON",
		"noclip ON",
	):
		assert hlil_signal in qagame_hlil or hlil_signal in qagame_strings

	dispatch_pairs = (
		('if (Q_stricmp (cmd, "score") == 0)', "Cmd_Score_f (ent);"),
		('else if (Q_stricmp (cmd, "acc") == 0)', "Cmd_Acc_f (ent);"),
		('else if (Q_stricmp (cmd, "pstats") == 0)', "Cmd_PStats_f (ent);"),
		('else if (Q_stricmp (cmd, "readyup") == 0)', "Cmd_ReadyUp_f (ent);"),
		('else if (Q_stricmp (cmd, "vote") == 0)', "Cmd_Vote_f (ent);"),
		('if (Q_stricmp (cmd, "give") == 0)', "Cmd_Give_f (ent);"),
		('else if (Q_stricmp (cmd, "god") == 0)', "Cmd_God_f (ent);"),
		('else if (Q_stricmp (cmd, "notarget") == 0)', "Cmd_Notarget_f (ent);"),
		('else if (Q_stricmp (cmd, "noclip") == 0)', "Cmd_Noclip_f (ent);"),
		('else if (Q_stricmp (cmd, "kill") == 0)', "Cmd_Kill_f (ent);"),
	)
	for dispatch, handler in dispatch_pairs:
		assert dispatch in client_command_block
		assert handler in client_command_block
		assert client_command_block.index(dispatch) < client_command_block.index(handler)
	for current, following in zip(dispatch_pairs, dispatch_pairs[1:]):
		assert client_command_block.index(current[0]) < client_command_block.index(following[0])

	intermission_gate = '// ignore all other commands when at intermission'
	assert client_command_block.index('else if (Q_stricmp (cmd, "vote") == 0)') < client_command_block.index(intermission_gate)
	assert client_command_block.index(intermission_gate) < client_command_block.index('if (Q_stricmp (cmd, "give") == 0)')
	assert client_command_block.index('else if (Q_stricmp (cmd, "ready") == 0)') > client_command_block.index('else if (Q_stricmp (cmd, "vote") == 0)')
	assert 'Q_stricmp (cmd, "ragequit")' not in client_command_block

	assert "G_RaceSendScoreboard( ent );" in score_block
	assert "DeathmatchScoreboardMessage( ent );" in score_block
	assert "G_SendRetailAccuracyCommand( ent );" in acc_block
	assert "G_SendRetailPStatsCommand( ent );" in pstats_block
	assert "G_ResetTrainingSession( ent );" in readyup_block
	assert "G_SetClientReadyState( ent->client, ready );" in readyup_block
	assert "G_WarmupReadyToStart();" in readyup_block
	assert "if ( level.intermissiontime ) {" in vote_block
	assert "G_HandleNextMapVote( ent );" in vote_block
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"No vote in progress.\\n\\"" );' in vote_block
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Vote cast.\\n\\"" );' in vote_block
	assert "G_UpdateVoteCounts();" in vote_block
	assert "G_UpdateNextMapVoteTallies();" in nextmap_vote_block
	assert 'trap_SendServerCommand( ent-g_entities, "disable_vote_ui" );' in nextmap_vote_block
	assert "if ( !CheatsOk( ent ) ) {" in give_block
	assert 'G_GiveItemByName( ent, "health" );' in give_block
	assert 'G_GiveItemByName( ent, "weapons" );' in give_block
	assert 'G_GiveItemByName( ent, "ammo" );' in give_block
	assert 'G_GiveItemByName( ent, "armor" );' in give_block
	assert "ent->flags ^= FL_GODMODE;" in god_block
	assert 'msg = "godmode ON\\n";' in god_block
	assert "ent->flags ^= FL_NOTARGET;" in notarget_block
	assert 'msg = "notarget ON\\n";' in notarget_block
	assert "ent->client->noclip = !ent->client->noclip;" in noclip_block
	assert 'msg = "noclip ON\\n";' in noclip_block
	assert "cooldown = g_allowKill.integer;" in kill_block
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Kill is not enabled on this server.\\n\\"" );' in kill_block
	assert "player_die( ent, ent, ent, 100000, MOD_SUICIDE );" in kill_block


def test_game_direct_mute_commands_follow_retail_chat_status_contract() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	qagame_map = _read("references/symbol-maps/qagame.json")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt")
	mute_block = _block_from_marker(game_cmds, "void Cmd_Mute_f")
	unmute_block = _block_from_marker(game_cmds, "void Cmd_Unmute_f")

	assert '"normalized_name": "Cmd_Mute_f"' in qagame_map
	assert '"normalized_name": "Cmd_Unmute_f"' in qagame_map
	assert "sub_100627c0" in qagame_hlil
	assert "sub_10062890" in qagame_hlil
	assert "%s has been muted" in qagame_hlil
	assert "%s has been unmuted" in qagame_hlil

	assert "target = G_AdminResolvePlayerIdArg( ent );" in mute_block
	assert "if ( G_AdminRejectSameOrHigherTarget( ent, target, NULL ) ) {" in mute_block
	assert "target->client->sess.muted = qtrue;" in mute_block
	assert "G_CleanClientNameFromClientNum( clientNum, targetName );" in mute_block
	assert 'trap_SendServerCommand( -1, va("print \\"%s has been muted\\n\\"", targetName) );' in mute_block
	assert 'trap_SendServerCommand( ent-g_entities, va("print \\"%s muted.\\n\\"", target->client->pers.netname) );' not in mute_block
	assert 'trap_SendServerCommand( target-g_entities, "print \\"You have been muted.\\n\\"" );' not in mute_block

	assert "target = G_AdminResolvePlayerIdArg( ent );" in unmute_block
	assert "G_AdminRejectSameOrHigherTarget" not in unmute_block
	assert "target->client->sess.muted = qfalse;" in unmute_block
	assert "G_CleanClientNameFromClientNum( clientNum, targetName );" in unmute_block
	assert 'trap_SendServerCommand( -1, va("print \\"%s has been unmuted\\n\\"", targetName) );' in unmute_block
	assert 'trap_SendServerCommand( ent-g_entities, va("print \\"%s unmuted.\\n\\"", target->client->pers.netname) );' not in unmute_block
	assert 'trap_SendServerCommand( target-g_entities, "print \\"You have been unmuted.\\n\\"" );' not in unmute_block


def test_game_direct_command_table_reconstructs_retail_client_command_tranche() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	game_local = _read("src/code/game/g_local.h")
	qagame_map = _read("references/symbol-maps/qagame.json")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt")
	players_block = _block_from_marker(game_cmds, "void Cmd_Players_f")
	op_say_block = _block_from_marker(game_cmds, "static void Cmd_OpSay_f")
	dispatch_block = _block_from_marker(game_cmds, "static qboolean G_DispatchDirectCommand")
	help_block = _block_from_marker(game_cmds, "static void G_PrintDirectCommandHelp")
	allready_block = _block_from_marker(game_cmds, "void Cmd_AllReady_f")
	lock_block = _block_from_marker(game_cmds, "void Cmd_Lock_f")
	unlock_block = _block_from_marker(game_cmds, "void Cmd_Unlock_f")
	putteam_block = _block_from_marker(game_cmds, "void Cmd_PutTeam_f")
	client_command_block = _block_from_marker(game_cmds, "void ClientCommand")

	for normalized_name in (
		"Cmd_Players_f",
		"G_ValidateDirectCommandState",
		"G_AdminResolvePlayerIdArg",
		"G_AdminParseTeamArg",
		"Cmd_AllReady_f",
		"G_TeamJoinAllowed",
		"Cmd_Lock_f",
		"Cmd_Unlock_f",
		"Cmd_PutTeam_f",
		"Cmd_OpSay_f",
		"G_PrintDirectCommandHelp",
		"G_DispatchDirectCommand",
	):
		assert f'"normalized_name": "{normalized_name}"' in qagame_map

	assert "data_10080750:" in qagame_hlil
	assert 'data_10088950 {"players"}' in qagame_hlil
	assert 'data_10088910 {"timeout"}' in qagame_hlil
	assert 'data_100885e0 {"opsay"}' in qagame_hlil
	assert "1008076c" in qagame_hlil
	assert "10080780" in qagame_hlil
	assert "10080794" in qagame_hlil
	assert "100807a8" in qagame_hlil
	assert "100807bc" in qagame_hlil
	assert "100807d0" in qagame_hlil
	assert "100807e4" in qagame_hlil
	assert "100807f8" in qagame_hlil
	assert "1008080c" in qagame_hlil
	assert "10080898" in qagame_hlil
	assert "sub_10060ee0" in qagame_hlil
	assert "sub_10061090" in qagame_hlil
	assert "sub_100611d0" in qagame_hlil
	assert "sub_10061350" in qagame_hlil
	assert "sub_10061800" in qagame_hlil
	assert "sub_10061940" in qagame_hlil
	assert "sub_10061a40" in qagame_hlil
	assert "sub_10061b40" in qagame_hlil
	assert "sub_10062bf0" in qagame_hlil
	assert "sub_10062e20" in qagame_hlil
	assert "100808a4" in qagame_hlil
	assert 'print "%2d %llu %c %s' in qagame_hlil
	assert "Missing PlayerID (use \\\\players for a list)" in qagame_hlil
	assert "Invalid TeamName (use R/B/S)" in qagame_hlil
	assert "Allready may not be used until two players are in the match." in qagame_hlil
	assert "The %s team is now %slocked" in qagame_hlil
	assert "A maximum of two players are allowed in the match." in qagame_hlil
	assert '<@%s^7> %s' in qagame_hlil
	assert "You do not have the privileges required to use this command" in qagame_hlil

	assert "uint64_t\t\tsteamId;" in players_block
	assert 'G_DirectCommandPrivilegeChar( cl->sess.privilege );' in players_block
	assert 'va( "print \\"%2d %llu %c %s\\n\\"",' in players_block
	assert "if ( trap_Argc() < 2 ) {" in op_say_block
	assert "message = ConcatArgs( 1 );" in op_say_block
	assert "speakerName = G_CleanClientNameFromClientNum( ent - g_entities, cleanName );" in op_say_block
	assert 'speakerName = "server";' in op_say_block
	assert 'trap_SendServerCommand( -1, va("print \\"<@%s^7> %s\\n\\"", speakerName, message) );' in op_say_block

	assert "static const directCommand_t s_directCommands[] = {" in game_cmds
	for expected_entry in (
		'{ "players", Cmd_Players_f, PRIV_NONE, 0,',
		'{ "timeout", Cmd_Timeout_f, PRIV_NONE, 0,',
		'{ "timein", Cmd_Timein_f, PRIV_NONE, 0,',
		'{ "allready", Cmd_AllReady_f, PRIV_MOD, 0,',
		'{ "pause", Cmd_Pause_f, PRIV_MOD, 0,',
		'{ "unpause", Cmd_Timein_f, PRIV_MOD, 0,',
		'{ "lock", Cmd_Lock_f, PRIV_MOD, 0,',
		'{ "unlock", Cmd_Unlock_f, PRIV_MOD, 0,',
		'{ "putteam", Cmd_PutTeam_f, PRIV_MOD, 0,',
		'{ "opsay", Cmd_OpSay_f, PRIV_MOD, 0,',
	):
		assert expected_entry in game_cmds
	assert "qboolean\tteamLocks[TEAM_NUM_TEAMS];" in game_local
	assert 'G_DirectCommandPrint( ent, "print \\"Missing PlayerID (use \\\\players for a list)\\n\\"" );' in game_cmds
	assert 'G_DirectCommandPrint( ent, "print \\"Invalid TeamName (use R/B/S)\\n\\"" );' in game_cmds
	assert "G_SetTeamLock( TEAM_RED, qtrue );" in lock_block
	assert "G_SetTeamLock( TEAM_BLUE, qtrue );" in lock_block
	assert "G_SetTeamLock( team, qtrue );" in lock_block
	assert "G_SetTeamLock( TEAM_RED, qfalse );" in unlock_block
	assert "G_SetTeamLock( TEAM_BLUE, qfalse );" in unlock_block
	assert "G_SetTeamLock( team, qfalse );" in unlock_block
	assert "target = G_AdminResolvePlayerIdArg( ent );" in putteam_block
	assert "team = G_AdminParseTeamArg( 2, ent, TEAM_NUM_TEAMS );" in putteam_block
	assert 'G_DirectCommandPrint( ent, "print \\"Allready may not be used until two players are in the match.\\n\\"" );' in allready_block
	assert "G_SetClientReadyState( &level.clients[i], qtrue );" in allready_block
	assert "directCommand->flags == DIRECTCMD_HELP_HIDDEN" in help_block
	assert "privilege = G_DirectCommandCallerPrivilege( ent );" in dispatch_block
	assert "for ( directCommand = s_directCommands; directCommand->name; directCommand++ ) {" in dispatch_block
	assert "if ( privilege < directCommand->requiredPrivilege ) {" in dispatch_block
	assert 'G_DirectCommandPrint( ent, "print \\"You do not have the privileges required to use this command\\n\\"" );' in dispatch_block
	assert "directCommand->handler( ent );" in dispatch_block
	assert "if ( G_DispatchDirectCommand( cmd, ent ) ) {" in client_command_block
	assert client_command_block.index("trap_Argv( 0, cmd, sizeof( cmd ) );") < client_command_block.index("if ( G_DispatchDirectCommand( cmd, ent ) )")
	assert client_command_block.index("if ( G_DispatchDirectCommand( cmd, ent ) )") < client_command_block.index('if (Q_stricmp (cmd, "say") == 0)')


def test_game_direct_admin_access_command_tranche_matches_retail_table() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	game_main = _read("src/code/game/g_main.c")
	game_local = _read("src/code/game/g_local.h")
	qagame_map = _read("references/symbol-maps/qagame.json")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt")
	qagame_access_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt")
	promote_block = _block_from_marker(game_cmds, "static void G_AdminPromoteTarget")
	demote_block = _block_from_marker(game_cmds, "static void Cmd_Demote_f")
	kick_ban_block = _block_from_marker(game_cmds, "static int G_KickOrBanClientWithMode")
	ban_block = _block_from_marker(game_cmds, "void Cmd_Ban_f")
	tempban_block = _block_from_marker(game_cmds, "static void Cmd_TempBan_f")
	unban_block = _block_from_marker(game_cmds, "static void Cmd_Unban_f")
	listaccess_block = _block_from_marker(game_cmds, "static void Cmd_ListAccess_f")
	abort_block = _block_from_marker(game_cmds, "static void Cmd_Abort_f")
	access_print_block = _block_from_marker(game_main, "void G_PrintAccessListPage")

	for normalized_name in (
		"Cmd_Abort_f",
		"Cmd_AddAdmin_f",
		"Cmd_AddMod_f",
		"Cmd_Demote_f",
		"Cmd_Mute_f",
		"Cmd_Unmute_f",
		"G_KickOrBanClient",
		"Cmd_Unban_f",
		"Cmd_ListAccess_f",
		"G_PrintAccessListPage",
	):
		assert f'"normalized_name": "{normalized_name}"' in qagame_map

	for offset in (
		"10080818",
		"1008082c",
		"10080840",
		"10080854",
		"10080868",
		"1008087c",
		"100808a4",
		"100808b8",
		"100808cc",
		"100808e0",
	):
		assert offset in qagame_hlil

	for raw_name in (
		"sub_100627c0",
		"sub_10062890",
		"sub_10062940",
		"sub_10062ad0",
		"sub_10062c60",
		"sub_10062470",
		"sub_10062560",
		"sub_10062650",
		"sub_10061550",
	):
		assert raw_name in qagame_hlil

	assert "Access List: Page %i of %i" in qagame_access_hlil
	assert "TEMP" in qagame_access_hlil
	assert "PERM" in qagame_access_hlil
	assert "%llu %s %s" in qagame_access_hlil
	assert "Can not kick admins." in qagame_hlil
	assert "was kicked" in qagame_hlil
	assert "Can not demote someone at or above your level." in qagame_hlil
	assert "%s has become an administrator" in qagame_hlil
	assert "%s has become a moderator" in qagame_hlil
	assert "%s has had their privileges removed" in qagame_hlil
	assert "%llu has been unbanned" in qagame_hlil
	assert "Match is currently paused. You must unpause before aborting the match." in qagame_hlil
	assert "map_restart 3" in qagame_hlil

	for expected_entry in (
		'{ "mute", Cmd_Mute_f, PRIV_MOD, 0,',
		'{ "unmute", Cmd_Unmute_f, PRIV_MOD, 0,',
		'{ "tempban", Cmd_TempBan_f, PRIV_MOD, 0,',
		'{ "ban", Cmd_Ban_f, PRIV_MOD, 0,',
		'{ "listaccess", Cmd_ListAccess_f, PRIV_MOD, 0,',
		'{ "unban", Cmd_Unban_f, PRIV_MOD, 0,',
		'{ "addadmin", Cmd_AddAdmin_f, PRIV_ADMIN, 0,',
		'{ "addmod", Cmd_AddMod_f, PRIV_ADMIN, 0,',
		'{ "demote", Cmd_Demote_f, PRIV_ADMIN, 0,',
		'{ "abort", Cmd_Abort_f, PRIV_MOD, 0,',
	):
		assert expected_entry in game_cmds

	assert "void\tG_SetAdminAccessForSteamID( const char *steamId, int tier, qboolean temporary );" in game_local
	assert "void\tG_RemoveAdminAccessForSteamID( const char *steamId );" in game_local
	assert "void\tG_PrintAccessListPage( gentity_t *ent, unsigned int page );" in game_local
	assert "void G_SetAdminAccessForSteamID( const char *steamId, int tier, qboolean temporary ) {" in game_main
	assert "void G_RemoveAdminAccessForSteamID( const char *steamId ) {" in game_main
	assert "static const char *G_AdminAccessTierLabel( int tier ) {" in game_main
	assert 'return "ADMIN ";' in game_main
	assert 'return "MOD   ";' in game_main
	assert 'return "BAN   ";' in game_main

	assert "enum { ACCESS_LIST_PAGE_SIZE = 20 };" in access_print_block
	assert 'Com_sprintf( line, sizeof( line ), "Access List: Page %i of %i\\n", page + 1, totalPages );' in access_print_block
	assert 'G_PrintAccessListLine( ent, "=============================\\n" );' in access_print_block
	assert 'entry->temporary ? "TEMP" : "PERM"' in access_print_block
	assert 'sscanf( entry->steamId, "%llu", &steamIdValue );' in access_print_block
	assert 'Com_sprintf( line, sizeof( line ), "%llu %s %s\\n",' in access_print_block

	assert "G_SetAdminAccessForSteamID( steamId, privilege, qfalse );" in promote_block
	assert 'trap_SendServerCommand( clientNum, va( "priv %i", target->client->sess.privilege ) );' in promote_block
	assert 'G_AdminPromoteTarget( ent, PRIV_ADMIN, "print \\"%s has become an administrator\\n\\"" );' in game_cmds
	assert 'G_AdminPromoteTarget( ent, PRIV_MOD, "print \\"%s has become a moderator\\n\\"" );' in game_cmds
	assert 'G_AdminRejectSameOrHigherTarget( ent, target,\n\t\t\t"print \\"Can not demote someone at or above your level.\\n\\"" )' in demote_block
	assert "G_RemoveAdminAccessForSteamID( steamId );" in demote_block
	assert 'trap_SendServerCommand( -1, va( "print \\"%s has had their privileges removed\\n\\"", targetName ) );' in demote_block
	assert 'trap_SendServerCommand( clientNum, va( "priv %i", target->client->sess.privilege ) );' in demote_block

	assert "G_KickOrBanClientWithMode( ent, targetToken, banTarget, qfalse );" in game_cmds
	assert "G_KickOrBanClientWithMode( ent, arg, qtrue, qtrue );" in tempban_block
	assert "G_KickOrBanClient( ent, arg, qtrue );" in ban_block
	assert "trap_Argv( 0, command, sizeof( command ) );" in kick_ban_block
	assert '!Q_stricmp( command, "tempban" )' in kick_ban_block
	assert '!Q_stricmp( command, "ban" )' in kick_ban_block
	assert "target = G_AdminResolvePlayerIdArg( ent );" in kick_ban_block
	assert "target->client->sess.privilege > PRIV_NONE" in kick_ban_block
	assert 'G_DirectCommandPrint( ent, "print \\"Can not kick admins.\\n\\"" );' in kick_ban_block
	assert "G_SetAdminAccessForSteamID( steamId, -1, temporary );" in kick_ban_block
	assert 'trap_DropClient( clientNum, "was kicked" );' in kick_ban_block
	assert "addip" not in kick_ban_block

	assert "page = atoi( arg ) - 1;" in listaccess_block
	assert "G_PrintAccessListPage( ent, (unsigned int)page );" in listaccess_block
	assert 'sscanf( arg, "%llu", &steamIdValue );' in unban_block
	assert "G_RemoveAdminAccessForSteamID( steamId );" in unban_block
	assert 'G_DirectCommandPrint( ent, va( "print \\"%llu has been unbanned\\n\\"", steamIdValue ) );' in unban_block
	assert 'G_DirectCommandPrint( ent,\n\t\t\t"print \\"Match is currently paused. You must unpause before aborting the match.\\n\\"" );' in abort_block
	assert 'trap_SendServerCommand( -1, va( "pcp \\"%s has aborted the match\\\\n\\"", callerName ) );' in abort_block
	assert 'trap_SendServerCommand( -1, "pcp \\"The server has aborted the match\\\\n\\"" );' in abort_block
	assert "G_ResetTimeoutState();" in abort_block
	assert "G_SetWarmupTime( -1 );" in abort_block
	assert "G_UpdateMatchStateConfigString();" in abort_block
	assert 'trap_SendConsoleCommand( EXEC_APPEND, "map_restart 3\\n" );' in abort_block


def test_game_direct_score_time_command_tail_matches_retail_table() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	qagame_map = _read("references/symbol-maps/qagame.json")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt")
	addscore_block = _block_from_marker(game_cmds, "static void Cmd_AddScore_f")
	addteamscore_block = _block_from_marker(game_cmds, "static void Cmd_AddTeamScore_f")
	setmatchtime_block = _block_from_marker(game_cmds, "static void Cmd_SetMatchTime_f")
	format_time_block = _block_from_marker(game_cmds, "static void G_FormatDirectMatchTime")
	dispatch_block = _block_from_marker(game_cmds, "static qboolean G_DispatchDirectCommand")

	for normalized_name in (
		"Cmd_AddScore_f",
		"Cmd_AddTeamScore_f",
		"Cmd_SetMatchTime_f",
	):
		assert f'"normalized_name": "{normalized_name}"' in qagame_map

	for offset in (
		"100808f4",
		"10080908",
		"1008091c",
		"10080930",
	):
		assert offset in qagame_hlil

	for raw_name in (
		"sub_10061670",
		"sub_10061730",
		"sub_10062ce0",
	):
		assert raw_name in qagame_hlil

	assert "Player score adjusted." in qagame_hlil
	assert "Team score adjusted." in qagame_hlil
	assert "%s has had their score %screased by %i." in qagame_hlil
	assert "Match time has been set to %s." in qagame_hlil
	assert 'data_100883f4[0x5] = "rcon"' in qagame_hlil

	for expected_entry in (
		'{ "addscore", Cmd_AddScore_f, PRIV_MOD, 0,',
		'{ "addteamscore", Cmd_AddTeamScore_f, PRIV_MOD, 0,',
		'{ "setmatchtime", Cmd_SetMatchTime_f, PRIV_MOD, 0,',
		'{ "rcon", NULL, PRIV_ADMIN, 0,',
	):
		assert expected_entry in game_cmds

	assert "if ( !directCommand->handler ) {" in dispatch_block
	assert "return qfalse;" in dispatch_block
	assert "target = G_AdminResolvePlayerIdArg( ent );" in addscore_block
	assert "score = atoi( arg );" in addscore_block
	assert "AddScore( target, target->r.currentOrigin, score );" in addscore_block
	assert 'trap_SendServerCommand( -1, "pcp \\"Player score adjusted.\\n\\"" );' in addscore_block
	assert 'va( "print \\"%s has had their score %screased by %i.\\n\\"",' in addscore_block
	assert "team = G_AdminParseTeamArg( 1, ent, TEAM_NUM_TEAMS );" in addteamscore_block
	assert "score = atoi( arg );" in addteamscore_block
	assert "AddTeamScore( vec3_origin, team, score );" in addteamscore_block
	assert 'trap_SendServerCommand( -1, "pcp \\"Team score adjusted.\\n\\"" );' in addteamscore_block
	assert 'va( "print \\"%s has had their score %screased by %i.\\n\\"",' in addteamscore_block
	assert 'Com_sprintf( buffer, bufferSize, "%i:%i%i", seconds / 60, ( seconds % 60 ) / 10, seconds % 10 );' in format_time_block
	assert "level.startTime = level.time - seconds * 1000;" in setmatchtime_block
	assert 'trap_SetConfigstring( CS_LEVEL_START_TIME, va( "%i", level.startTime ) );' in setmatchtime_block
	assert "G_FormatDirectMatchTime( seconds, timeBuffer, sizeof( timeBuffer ) );" in setmatchtime_block
	assert 'va( "pcp \\"Match time has been set to %s.\\n\\"", timeBuffer )' in setmatchtime_block


def test_qagame_server_command_wiring_tranche_matches_retail_evidence() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	game_svcmds = _read("src/code/game/g_svcmds.c")
	game_bot = _read("src/code/game/g_bot.c")
	game_mem = _read("src/code/game/g_mem.c")
	qagame_map = _read("references/symbol-maps/qagame.json")
	qagame_bot_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt")
	console_block = _block_from_marker(game_svcmds, "qboolean\tConsoleCommand")
	g_addbot_block = _block_from_marker(game_bot, "static void G_AddBot")
	addbot_block = _block_from_marker(game_bot, "void Svcmd_AddBot_f")
	game_crash_block = _block_from_marker(game_svcmds, "static void Svcmd_GameCrash_f")
	reload_access_block = _block_from_marker(game_svcmds, "static void Svcmd_ReloadAccess_f")
	game_mem_block = _block_from_marker(game_mem, "void Svcmd_GameMem_f")

	for normalized_name in (
		"Cmd_AddScore_f",
		"Cmd_AddTeamScore_f",
		"Cmd_SetMatchTime_f",
		"Svcmd_EntityList_f",
		"Svcmd_ForceTeam_f",
		"Svcmd_AddBot_f",
		"Svcmd_BotList_f",
		"Svcmd_ReloadAccess_f",
		"ConsoleCommand",
	):
		assert f'"normalized_name": "{normalized_name}"' in qagame_map

	for expected_entry in (
		'{ "addscore", Cmd_AddScore_f, PRIV_MOD, 0,',
		'{ "addteamscore", Cmd_AddTeamScore_f, PRIV_MOD, 0,',
		'{ "setmatchtime", Cmd_SetMatchTime_f, PRIV_MOD, 0,',
	):
		assert expected_entry in game_cmds

	for expected_dispatch in (
		('if ( Q_stricmp (cmd, "entitylist") == 0 ) {', "Svcmd_EntityList_f();"),
		('if ( Q_stricmp (cmd, "forceteam") == 0 ) {', "Svcmd_ForceTeam_f();"),
		('if (Q_stricmp (cmd, "game_memory") == 0) {', "Svcmd_GameMem_f();"),
		('if (Q_stricmp (cmd, "addbot") == 0) {', "Svcmd_AddBot_f();"),
		('if (Q_stricmp (cmd, "botlist") == 0) {', "Svcmd_BotList_f();"),
		('if ( Q_stricmp (cmd, "game_crash") == 0 ) {', "Svcmd_GameCrash_f();"),
		('if ( Q_stricmp (cmd, "reload_access") == 0 ) {', "Svcmd_ReloadAccess_f();"),
	):
		assert expected_dispatch[0] in console_block
		assert expected_dispatch[1] in console_block
		assert console_block.index(expected_dispatch[0]) < console_block.index(expected_dispatch[1])

	for hlil_signal in (
		'data_100884b4 {"addscore"}',
		'data_1008846c {"addteamscore"}',
		'data_10088420 {"setmatchtime"}',
		'sub_10070a40("entitylist"',
		'sub_10070a40("forceteam"',
		'sub_10070a40("game_memory"',
		'sub_10070a40("addbot"',
		'sub_10070a40("botlist"',
		'sub_10070a40("game_crash"',
		'sub_10070a40("reload_access"',
		'Game memory status: %i out of %i',
		"*nullptr = 0x12345678",
	):
		assert hlil_signal in qagame_hlil

	assert "10037910" in qagame_bot_hlil
	assert '"loaddeferred\\n"' in qagame_bot_hlil
	for hlil_signal in (
		'1003768c  sub_10070f30(&var_448, edx_4, "model", &var_448)',
		'100376b2  sub_10070f30(eax_11, edx_5, "headmodel", &var_448)',
		"100376f5      int32_t var_484_8 = 7",
		'10037710  sub_10070f30(eax_13, edx_7, "color1", &var_448)',
		"10037729      int32_t var_484_10 = 0x19",
		'10037744  sub_10070f30(eax_14, &var_448, "color2", &var_448)',
	):
		assert hlil_signal in qagame_bot_hlil
	assert "1008235c  data_1008235c:" in qagame_hlil
	assert "25 69 00 00" in qagame_hlil
	assert "void\tSvcmd_EntityList_f" in game_svcmds
	assert "void\tSvcmd_ForceTeam_f" in game_svcmds
	assert "void Svcmd_AddBot_f( void ) {" in game_bot
	assert "void Svcmd_BotList_f( void ) {" in game_bot
	assert "static void Svcmd_GameCrash_f( void ) {" in game_svcmds
	assert "static void Svcmd_ReloadAccess_f( void ) {" in game_svcmds
	assert 'trap_SendServerCommand( -1, "loaddeferred\\n" );' in addbot_block
	assert "loaddefered" not in addbot_block
	assert 'key = "model";' in g_addbot_block
	assert 'Info_SetValueForKey( userinfo, key, model );' in g_addbot_block
	assert 'key = "team_model";' not in g_addbot_block
	assert 'key = "headmodel";' in g_addbot_block
	assert 'Info_SetValueForKey( userinfo, key, headmodel );' in g_addbot_block
	assert 'key = "team_headmodel";' not in g_addbot_block
	assert 'key = "color1";' in g_addbot_block
	assert 's = "7";' in g_addbot_block
	assert 'key = "color2";' in g_addbot_block
	assert 's = "25";' in g_addbot_block
	assert 'G_Printf( "Game memory status: %i out of %i bytes allocated\\n", allocPoint, POOLSIZE );' in game_mem_block
	assert 'trap_Cvar_VariableIntegerValue( "developer" ) < 1' in game_crash_block
	assert "*(volatile int *)0 = 0x12345678;" in game_crash_block
	assert "G_ReloadAdminAccess();" in reload_access_block


def test_team_join_guard_and_connect_broadcast_match_retail_flow() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	game_client = _read("src/code/game/g_client.c")
	game_session = _read("src/code/game/g_session.c")
	join_block = _block_from_marker(game_cmds, "static qboolean G_TeamJoinAllowed")
	setteam_block = _block_from_marker(game_cmds, "void SetTeam")
	connect_block = _block_from_marker(game_client, "char *ClientConnect")
	spawn_block = _block_from_marker(game_client, "void ClientSpawn")
	session_block = _block_from_marker(game_session, "void G_InitSessionData")

	assert "static qboolean G_TeamJoinAllowed( team_t team, gentity_t *ent ) {" in game_cmds
	assert "if ( team == TEAM_SPECTATOR || team == TEAM_FREE ) {" in join_block
	assert "if ( team < TEAM_FREE || team >= TEAM_NUM_TEAMS ) {" in join_block
	assert "if ( !level.teamLocks[team] && !g_teamSpawnAsSpec.integer ) {" in join_block
	assert "teamName = TeamName( team );" in join_block
	assert 'G_Printf( "The %s team is locked!\\n", teamName );' in join_block
	assert 'va( "print \\"The %s team is locked!\\\\n\\"", teamName )' in join_block
	assert "if ( !G_TeamJoinAllowed( (team_t)team, ent ) ) {" in setteam_block
	assert "counts[TEAM_BLUE] = TeamCount( clientNum, TEAM_BLUE );" in setteam_block
	assert "counts[TEAM_RED] = TeamCount( clientNum, TEAM_RED );" in setteam_block
	assert "TeamCount( ent->client->ps.clientNum, TEAM_BLUE )" not in setteam_block
	assert "TeamCount( ent->client->ps.clientNum, TEAM_RED )" not in setteam_block
	assert "runFirstTimeConnectSideEffects = ( firstTime && !level.trainingMapActive ) ? qtrue : qfalse;" in connect_block
	assert 'client->pers.recordingPreferences = atoi( Info_ValueForKey( userinfo, "cg_autoAction" ) );' in game_client
	assert "if ( firstTime && !isBot ) {" in connect_block
	assert "if ( !firstTime && !isBot ) {" not in connect_block
	assert "G_FilterPacket" not in connect_block
	assert "client->sess.privilege = connectionPrivilege;" not in connect_block
	assert 'trap_SendServerCommand( clientNum, va( "priv %i", client->sess.privilege ) );' in connect_block
	assert "trap_GetSteamId( clientNum, &printSteamIdLow, &printSteamIdHigh )" in connect_block
	assert 'Info_ValueForKey( userinfo, "steamid" )' not in connect_block
	assert "G_StartAutoRecordForClient( ent );" in connect_block
	assert 'G_LogPrintf( "ClientMask: %i %s\\n", clientNum, ( ent->r.svFlags & SVF_BOT ) ? "bot" : "human" );' not in connect_block
	assert "G_AutoAction( AUTOACTION_PLAYER_CONNECT, ent, autoDetail );" not in connect_block
	assert "G_SendItemTimerState( clientNum, g_itemTimers.integer ? 1 : 0, g_itemHeight.integer );" not in connect_block
	assert connect_block.index("G_RankClientConnect( ent );") < connect_block.index("BroadcastTeamChange( client, -1 );")
	assert connect_block.index("BroadcastTeamChange( client, -1 );") < connect_block.index("G_StartAutoRecordForClient( ent );")
	assert connect_block.index("if ( runFirstTimeConnectSideEffects ) {") < connect_block.index("BroadcastTeamChange( client, -1 );")
	assert connect_block.index("client->pers.steamIdLow = connectSteamIdLow;") < connect_block.index("G_InitSessionData( client, userinfo );")
	assert connect_block.index("client->pers.steamIdHigh = connectSteamIdHigh;") < connect_block.index("G_InitSessionData( client, userinfo );")
	assert connect_block.index("G_InitSessionData( client, userinfo );") < connect_block.index("G_RankResetClientStats( client );")
	assert connect_block.index("G_RankResetClientStats( client );") < connect_block.index("G_ReadSessionData( client );")
	assert connect_block.index("G_RankResetClientStats( client );") < connect_block.index("ClientUserinfoChanged( clientNum );")
	assert "G_ReadSessionData( client );" in connect_block
	assert "G_ReadSessionData( client, firstTime );" not in connect_block
	assert "if ( client->pers.localClient ) {" in session_block
	assert "if ( client->pers.steamIdValid ) {" in session_block
	assert "sess->privilege = G_AdminAccessForSteamID( steamIdString );" in session_block
	assert 'sess->privilege = G_AdminAccessForSteamID( Info_ValueForKey( userinfo, "steamid" ) );' in session_block
	assert "g_teamSpawnAsSpec.integer && g_gametype.integer >= GT_TEAM" not in spawn_block


def test_client_connect_autorecord_helpers_match_recovered_retail_boundaries() -> None:
	game_main = _read("src/code/game/g_main.c")
	game_local = _read("src/code/game/g_local.h")
	update_state_block = _block_from_marker(game_main, "static void G_UpdateGameStateForLevel")
	check_record_block = _block_from_marker(game_main, "static void G_CheckAutoRecord")

	assert "#define AUTO_RECORD_STATE_RECORDING\t( 1 << 0 )" in game_main
	assert "#define AUTO_RECORD_STATE_SCREENSHOT\t( 1 << 1 )" in game_main
	assert "static char\ts_autoRecordBasename[AUTO_RECORD_BASENAME_MAX];" in game_main
	assert "static char *G_SanitizeFilenameToken( char *dst, const char *src ) {" in game_main
	assert "static char *G_BuildAutoRecordBasename( gentity_t *ent ) {" in game_main
	assert "static void G_StopAutoRecord( void ) {" in game_main
	assert "void G_StartAutoRecordForClient( gentity_t *ent ) {" in game_main
	assert "static void G_CheckAutoRecord( void ) {" in game_main
	assert 'trap_SendServerCommand( clientNum, va( "record \\"%s\\"\\n", G_BuildAutoRecordBasename( ent ) ) );' in game_main
	assert 'trap_SendServerCommand( i, va( "screenshot \\"%s\\"\\n", G_BuildAutoRecordBasename( ent ) ) );' in game_main
	assert "G_CheckAutoRecord();" in update_state_block
	assert "if ( level.warmupTime == -1 ) {" in check_record_block
	assert "G_StopAutoRecord();" in check_record_block
	assert "s_autoRecordState = 0;" in check_record_block
	assert check_record_block.index("if ( level.warmupTime == -1 ) {") < check_record_block.index("if ( level.warmupTime != 0 ) {")
	assert "if ( level.time - level.intermissiontime <= 4000 ) {" in check_record_block
	assert "if ( s_autoRecordState & AUTO_RECORD_STATE_SCREENSHOT ) {" in check_record_block
	assert "s_autoRecordState |= AUTO_RECORD_STATE_SCREENSHOT;" in check_record_block
	assert check_record_block.index("G_StopAutoRecord();") < check_record_block.index("s_autoRecordState |= AUTO_RECORD_STATE_SCREENSHOT;")
	assert check_record_block.index("s_autoRecordState |= AUTO_RECORD_STATE_SCREENSHOT;") < check_record_block.index('trap_SendServerCommand( i, va( "screenshot \\"%s\\"\\n", G_BuildAutoRecordBasename( ent ) ) );')
	assert "void G_StartAutoRecordForClient( gentity_t *ent );" in game_local
	assert "int\t\t\trecordingPreferences;\t// server-visible cg_autoAction bitfield for match media helpers" in game_local


def test_session_init_and_serializer_follow_recovered_retail_shape() -> None:
	game_session = _read("src/code/game/g_session.c")
	game_main = _read("src/code/game/g_main.c")
	game_local = _read("src/code/game/g_local.h")
	init_block = _block_from_marker(game_session, "void G_InitSessionData")
	read_block = _block_from_marker(game_session, "void G_ReadSessionData")
	write_block = _block_from_marker(game_session, "void G_WriteClientSessionData")

	assert "if ( g_gametype.integer >= GT_TEAM && g_teamAutoJoin.integer ) {" in init_block
	assert "sess->sessionTeam = TEAM_SPECTATOR;" in init_block
	assert 'Info_ValueForKey( userinfo, "team" )' not in init_block
	assert "level.numNonSpectatorClients" not in init_block
	assert "g_maxGameClients.integer" not in init_block
	assert "sess->spectatorState = SPECTATOR_FREE;" in init_block
	assert "sess->spectatorTime = (int)time( NULL );" in init_block
	assert "g_teamSpecFreeCam.integer ? SPECTATOR_FREE : SPECTATOR_SCOREBOARD" not in init_block
	assert "if ( g_gametype.integer == GT_TOURNAMENT ) {" in init_block
	assert "sess->spectateOnly = qtrue;" in init_block

	assert '%i %ld %i %i %i %i %i %i %i %i %i %i %i %i' in write_block
	assert "client->sess.sessionReservedTail" in write_block
	assert "ignoredSessionTail" in write_block
	assert "client->sess.skill1" not in write_block
	assert "client->sess.skill2" not in write_block
	assert "client->sess.skill3" not in write_block

	assert '%i %ld %i %i %i %i %i %i %i %i %i %i %i %i' in read_block
	assert read_block.count( "sscanf" ) == 1
	assert "ignoredSessionTail" in read_block
	assert "client->sess.skill1 = 0;" in read_block
	assert "client->sess.skill2 = 0;" in read_block
	assert "client->sess.skill3 = 0;" in read_block
	assert "if ( g_teamSpawnAsSpec.integer && g_gametype.integer >= GT_TEAM && level.warmupTime != 0 ) {" in read_block
	assert "g_maintainTeam.integer" not in read_block
	assert "firstTime" not in read_block
	assert "g_teamSpecFreeCam.integer ? SPECTATOR_FREE : SPECTATOR_SCOREBOARD" not in read_block
	assert "g_maintainTeam" not in game_main
	assert "g_maintainTeam" not in game_local


def test_client_spawn_uses_recovered_loadout_and_rr_helpers() -> None:
	game_client = _read("src/code/game/g_client.c")
	game_items = _read("src/code/game/g_items.c")
	game_team = _read("src/code/game/g_team.c")
	game_local = _read("src/code/game/g_local.h")
	loadout_block = _block_from_marker(game_client, "static weapon_t G_FinalizeSpawnLoadout")
	init_spawn_block = _block_from_marker(game_client, "static weapon_t G_InitClientSpawnState")
	spawn_block = _block_from_marker(game_client, "void ClientSpawn")
	defer_block = _block_from_marker(game_client, "static void G_DeferClientSpawnRetry")
	retry_block = _block_from_marker(game_client, "static void G_RetryDeferredClientSpawn")
	eligibility_block = _block_from_marker(game_client, "static qboolean G_ClientCanUseSpawnPoint")
	ranked_filter_block = _block_from_marker(game_client, "static qboolean G_RankedSpawnPointAllowed( const")
	ranked_mode_filter_block = _block_from_marker(game_client, "static qboolean G_RankedSpawnPointAllowedForMode")
	ranked_spawn_block = _block_from_marker(game_client, "static gentity_t *G_SelectRankedSpawnPointForTeamMode")
	initial_spawn_block = _block_from_marker(game_client, "gentity_t *SelectInitialSpawnPoint")
	ctf_spawn_block = _block_from_marker(game_team, "gentity_t *SelectCTFSpawnPoint")
	team_spawn_gate_block = _block_from_marker(game_client, "static qboolean G_GametypeUsesTeamSpawnSelection")
	skip_targets_block = _block_from_marker(game_client, "static qboolean G_GametypeSkipsSpawnPointTargets")
	warmup_gate_block = _block_from_marker(game_client, "static qboolean G_ShouldGrantWarmupLevelWeapons")
	warmup_allowed_block = _block_from_marker(game_client, "static qboolean G_WarmupLevelWeaponAllowed")
	warmup_ammo_block = _block_from_marker(game_client, "static int G_WarmupLevelWeaponAmmo")

	assert "static weapon_t G_SelectConfiguredSpawnWeapon( gclient_t *client, unsigned int startingMask ) {" in game_client
	assert "static weapon_t G_FinalizeSpawnLoadout( gentity_t *ent, const factoryCvarConfig_t *factoryConfig ) {" in game_client
	assert "client->sess.selectedSpawnWeapon = (int)spawnWeapon;" in game_client
	assert "if ( client->rrInfectionState != RR_STATE_INFECTED ) {" in game_client
	assert "#define\tMAX_RANKED_SPAWN_POINTS\t26" in game_client
	assert "#define\tCLIENT_SPAWN_RETRY_DELAY\t600" in game_client
	assert "#define\tRANKED_SPAWN_INITIAL_FLAG\t1" in game_client
	assert "#define\tRANKED_SPAWN_EXCLUDE_FLAG\t2" in game_client
	assert "static qboolean G_ClientCanUseSpawnPoint( const gentity_t *ent, const gentity_t *spawnPoint ) {" in game_client
	assert "spawnPoint->flags & FL_NO_BOTS" in eligibility_block
	assert "spawnPoint->flags & FL_NO_HUMANS" in eligibility_block
	assert "static qboolean G_RankedSpawnPointAllowed( const gentity_t *spot ) {" in game_client
	assert "spot->spawnflags & RANKED_SPAWN_EXCLUDE_FLAG" in ranked_filter_block
	assert "return qfalse;" in ranked_filter_block
	assert "static qboolean G_RankedSpawnPointAllowedForMode( const gentity_t *spot, qboolean requireInitial ) {" in game_client
	assert "G_RankedSpawnPointAllowed( spot )" in ranked_mode_filter_block
	assert "requireInitial && !( spot->spawnflags & RANKED_SPAWN_INITIAL_FLAG )" in ranked_mode_filter_block
	assert ranked_spawn_block.count("G_RankedSpawnPointAllowedForMode( spot, requireInitial )") == 2
	assert ranked_spawn_block.index("if ( !G_RankedSpawnPointAllowedForMode( spot, requireInitial ) ) {") < ranked_spawn_block.index("if ( SpotWouldTelefrag( spot ) ) {")
	assert "static void G_RetryDeferredClientSpawn( gentity_t *ent ) {" in game_client
	assert "ClientSpawn( ent );" in retry_block
	assert "static void G_DeferClientSpawnRetry( gentity_t *ent ) {" in game_client
	assert "client->respawnTime = level.time + CLIENT_SPAWN_RETRY_DELAY;" in defer_block
	assert "client->ps.pm_type = PM_SPECTATOR;" in defer_block
	assert "client->noSpawnRetryCount++;" in defer_block
	assert "ent->think = G_RetryDeferredClientSpawn;" in defer_block
	assert "ent->nextthink = client->respawnTime;" in defer_block
	assert "static qboolean G_GametypeUsesTeamSpawnSelection( int gametype ) {" in game_client
	assert "case GT_CLAN_ARENA:" in team_spawn_gate_block
	assert "case GT_ATTACK_DEFEND:" in team_spawn_gate_block
	assert "case GT_RED_ROVER:" not in team_spawn_gate_block
	assert "return qfalse;" in team_spawn_gate_block
	assert "static weapon_t G_InitClientSpawnState( gentity_t *ent, gentity_t *spawnPoint, const factoryCvarConfig_t *factoryConfig ) {" in game_client
	assert "spawnWeapon = G_InitClientSpawnState( ent, spawnPoint, factoryConfig );" in spawn_block
	assert "static qboolean G_ShouldGrantWarmupLevelWeapons( void ) {" in game_client
	assert "level.warmupTime != 0" in warmup_gate_block
	assert "!g_training.integer" in warmup_gate_block
	assert "!( practiceflags.integer & 1 )" in warmup_gate_block
	assert "!g_loadout.integer" in warmup_gate_block
	assert "static qboolean G_WarmupLevelWeaponAllowed( weapon_t weapon, unsigned int startingWeaponsMask ) {" in game_client
	assert "weapon != WP_MACHINEGUN && weapon != WP_GRAPPLING_HOOK" in warmup_allowed_block
	assert "weaponTag = BG_ItemTagForWeapon( weapon );" in warmup_allowed_block
	assert "startingWeaponsMask & ( 1u << ( weaponTag - 1 ) )" in warmup_allowed_block
	assert "static int G_WarmupLevelWeaponAmmo( weapon_t weapon ) {" in game_client
	assert "case WP_MACHINEGUN:" in warmup_ammo_block
	assert "case WP_HEAVY_MACHINEGUN:" in warmup_ammo_block
	assert "return 150;" in warmup_ammo_block
	assert "gitem_t" in loadout_block
	assert "*weaponItem;" in loadout_block
	assert "qboolean\t\twarmupLevelWeaponsGranted[WP_NUM_WEAPONS] = { qfalse };" in loadout_block
	assert "startingMask = factoryConfig->startingWeaponsStatMask;" in loadout_block
	assert "startingMask = g_startingWeapons.integer;" not in loadout_block
	assert "if ( G_ShouldGrantWarmupLevelWeapons() ) {" in loadout_block
	assert "for ( weapon = WP_MACHINEGUN; weapon < WP_NUM_WEAPONS; ++weapon ) {" in loadout_block
	assert "G_ItemRegistered( weaponItem )" in loadout_block
	assert "G_WarmupLevelWeaponAllowed( weapon, factoryConfig->startingWeaponsMask )" in loadout_block
	assert "startingMask |= 1u << weapon;" in loadout_block
	assert "rrInfectionState" not in loadout_block
	assert "warmupLevelWeaponsGranted[weapon] = qtrue;" in loadout_block
	assert loadout_block.index("startingMask |= 1u << weapon;") < loadout_block.index("client->ps.stats[STAT_WEAPONS] = startingMask;")
	assert "weaponItem = BG_FindItemForWeapon( weapon );" in loadout_block
	assert "RegisterItem( weaponItem );" in loadout_block
	assert loadout_block.index("RegisterItem( weaponItem );") < loadout_block.index("G_SeedConfiguredSpawnAmmo( &client->ps, weapon, startingAmmoTable[weapon] );")
	assert "G_SeedConfiguredSpawnAmmo( &client->ps, weapon, G_WarmupLevelWeaponAmmo( weapon ) );" in loadout_block
	assert "qboolean G_ItemRegistered( const gitem_t *item );" in game_local
	assert "qboolean G_ItemRegistered( const gitem_t *item ) {" in game_items
	assert "return itemRegistered[itemIndex];" in game_items
	assert "static qboolean G_RRFinalizeSpawnLoadout( gentity_t *ent ) {" in game_client
	assert "client->ps.stats[STAT_WEAPONS] = 1u << WP_GAUNTLET;" in game_client
	assert "client->pers.maxHealth = client->ps.stats[STAT_MAX_HEALTH] + g_rrInfectedZombieHealthBonus.integer;" in game_client
	assert "rrLoadoutFinalized = G_RRFinalizeSpawnLoadout( ent );" in init_spawn_block
	assert "G_UseTargets( spawnPoint, ent );" in init_spawn_block
	assert "if ( rrLoadoutFinalized ) {" in init_spawn_block
	assert "return WP_GAUNTLET;" in init_spawn_block
	assert "return G_FinalizeSpawnLoadout( ent, factoryConfig );" in init_spawn_block
	assert init_spawn_block.index("rrLoadoutFinalized = G_RRFinalizeSpawnLoadout( ent );") < init_spawn_block.index("G_UseTargets( spawnPoint, ent );")
	assert init_spawn_block.index("G_UseTargets( spawnPoint, ent );") < init_spawn_block.index("if ( rrLoadoutFinalized ) {")
	assert init_spawn_block.index("if ( rrLoadoutFinalized ) {") < init_spawn_block.index("return G_FinalizeSpawnLoadout( ent, factoryConfig );")
	assert "static qboolean G_GametypeSkipsSpawnPointTargets( int gametype ) {" in game_client
	assert "case GT_RACE:" in skip_targets_block
	assert "case GT_CLAN_ARENA:" in skip_targets_block
	assert "case GT_DOMINATION:" in skip_targets_block
	assert "case GT_RED_ROVER:" in skip_targets_block
	assert "return qfalse;" in skip_targets_block
	assert "return qtrue;" in skip_targets_block
	assert spawn_block.index("client->lastkilled_client = -1;") < spawn_block.index("client->lasthurt_client = -1;")
	assert "do {" not in spawn_block[spawn_block.index("// find a spawn point"):spawn_block.index("client->pers.teamState.state = TEAM_ACTIVE;")]
	assert "for ( spawnAttempts = 0; spawnAttempts < MAX_SPAWN_POINTS; ++spawnAttempts ) {" in spawn_block
	assert "if ( !spawnPoint || G_ClientCanUseSpawnPoint( ent, spawnPoint ) ) {" in spawn_block
	assert "if ( !G_ClientCanUseSpawnPoint( ent, spawnPoint ) ) {" in spawn_block
	assert "G_DeferClientSpawnRetry( ent );" in spawn_block
	assert "client->noSpawnRetryCount = 0;" in spawn_block
	assert spawn_block.index("spawnPoint = G_SelectClientSpawnPoint( ent, spawn_origin, spawn_angles );") < spawn_block.index("G_DeferClientSpawnRetry( ent );")
	assert "static gentity_t *G_SelectInitialRankedSpawnPoint( gentity_t *spots[], int spotCount, vec3_t origin, vec3_t angles ) {" in game_client
	assert "return G_SelectRankedSpawnPointForTeamMode( spots, spotCount, TEAM_FREE, qtrue, origin, angles );" in game_client
	assert "spotCount = G_CollectSpawnPointsByClassname( \"info_player_deathmatch\", spots, ARRAY_LEN( spots ) );" in initial_spawn_block
	assert "spot = G_SelectInitialRankedSpawnPoint( spots, spotCount, origin, angles );" in initial_spawn_block
	assert "while ((spot = G_Find" not in initial_spawn_block
	assert spawn_block.index("client->ps.pm_flags |= PMF_RESPAWNED;") < spawn_block.index("spawnWeapon = G_InitClientSpawnState( ent, spawnPoint, factoryConfig );")
	assert spawn_block.index("spawnWeapon = G_InitClientSpawnState( ent, spawnPoint, factoryConfig );") < spawn_block.index("trap_GetUsercmd( client - level.clients, &ent->client->pers.cmd );")
	assert spawn_block.index("G_GrantConfiguredItems( ent );") < spawn_block.index("BG_PlayerStateToEntityState( &client->ps, &ent->s, qtrue );")
	assert spawn_block.index("G_GrantConfiguredItems( ent );") < spawn_block.index("G_GametypeClientSpawn( ent );")
	assert "gentity_t *G_SelectRankedSpawnPoint( gentity_t *spots[], int spotCount, vec3_t origin, vec3_t angles ) {" in game_client
	assert "static gentity_t *G_SelectClientSpawnPoint( gentity_t *ent, vec3_t origin, vec3_t angles ) {" in game_client
	assert "spawnPoint = G_SelectClientSpawnPoint( ent, spawn_origin, spawn_angles );" in game_client
	assert "if ( G_GametypeUsesTeamSpawnSelection( g_gametype.integer ) ) {" in game_client
	assert "if ( g_gametype.integer >= GT_CTF ) {" not in game_client
	assert "gentity_t *Team_SelectDominationSpawnPoint( gentity_t *ent, vec3_t origin, vec3_t angles ) {" in game_team
	assert "spawnPoint = Team_SelectDominationSpawnPoint( ent, origin, angles );" in game_client
	assert "return G_SelectRankedSpawnPointForTeam( spots, count, OtherTeam( team ), origin, angles );" in game_team
	assert "spot = G_SelectRankedSpawnPointForTeam( spots, count, OtherTeam( team ), origin, angles );" in game_team
	assert "if ( !spot && teamstate == TEAM_BEGIN ) {" in ctf_spawn_block
	assert ctf_spawn_block.count("classname = \"team_CTF_redspawn\";") == 2
	assert ctf_spawn_block.count("classname = \"team_CTF_bluespawn\";") == 2
	assert ctf_spawn_block.index("spot = G_SelectRankedSpawnPointForTeam( spots, count, OtherTeam( team ), origin, angles );") < ctf_spawn_block.index("if ( !spot && teamstate == TEAM_BEGIN ) {")
	assert "gentity_t *G_SelectRankedSpawnPointForTeam( gentity_t *spots[], int spotCount, team_t enemyTeam, vec3_t origin, vec3_t angles );" in game_local
	assert "gentity_t *G_SelectRankedSpawnPoint( gentity_t *spots[], int spotCount, vec3_t origin, vec3_t angles );" in game_local
	assert "gentity_t *Team_SelectDominationSpawnPoint( gentity_t *ent, vec3_t origin, vec3_t angles );" in game_local


def test_input_spawn_and_host_map_paths_keep_retail_factory_gates() -> None:
	cl_keys = _read("src/code/client/cl_keys.c")
	game_client = _read("src/code/game/g_client.c")
	server_cmds = _read("src/code/server/sv_ccmds.c")
	field_block = _block_from_marker(cl_keys, "void Field_KeyDownEvent")
	spawn_block = _block_from_marker(game_client, "static gentity_t *G_SelectClientSpawnPoint")
	list_block = _block_from_marker(server_cmds, "static void SV_FactoryPrintValidList")
	apply_block = _block_from_marker(server_cmds, "static void SV_FactoryApplySelection")
	map_block = _block_from_marker(server_cmds, "static void SV_Map_f")

	for expected in (
		"if ( key == K_DEL || key == K_KP_DEL ) {",
		"if ( key == K_RIGHTARROW || key == K_KP_RIGHTARROW )",
		"if ( key == K_LEFTARROW || key == K_KP_LEFTARROW )",
		"if ( key == K_HOME || key == K_KP_HOME || ( tolower(key) == 'a' && keys[K_CTRL].down ) ) {",
		"if ( key == K_END || key == K_KP_END || ( tolower(key) == 'e' && keys[K_CTRL].down ) ) {",
		"if ( key == K_INS || key == K_KP_INS ) {",
	):
		assert expected in field_block

	assert "g_gametype.integer == GT_TOURNAMENT" in spawn_block
	assert "level.trainingMapActive && client->pers.localClient" in spawn_block
	assert "client->pers.localClient || g_gametype.integer == GT_TOURNAMENT || level.trainingMapActive" not in spawn_block

	for expected in (
		'} else if ( !Q_stricmp( key, "title" ) ) {',
		"title = SV_FactoryParseJsonString( state );",
		'} else if ( !Q_stricmp( key, "cvars" ) ) {',
		"if ( !SV_FactoryParseCvarOverrides( state, definition ) ) {",
		"definition->title = title;",
	):
		assert expected in server_cmds

	for expected in (
		'Com_Printf( "Valid factories: " );',
		"factory->id[0] != '_'",
		'Com_Printf( "%s ", factory->id );',
	):
		assert expected in list_block

	for expected in (
		"if ( s_svCurrentFactory == factory ) {",
		'Cvar_Set( "g_gametype", gametypeBuffer );',
		'Cvar_Set( "g_factory", factory->id ? factory->id : "" );',
		'Cvar_Set( "g_factoryTitle", factory->title ? factory->title : "" );',
	):
		assert expected in apply_block

	assert "Cvar_Reset( override->name );" in server_cmds

	assert "static const svFactoryDefinition_t *s_svCurrentFactory = NULL;" in server_cmds
	for expected in (
		"requiredArgs = s_svCurrentFactory ? 2 : 3;",
		'Com_Printf( "%s (map) (factory)\\n", cmd );',
		"SV_FactoryPrintValidList();",
		"factoryOverride = s_svCurrentFactory;",
		"SV_FactoryApplySelection( factoryOverride );",
	):
		assert expected in map_block


def test_freeze_helpers_match_recovered_retail_boundaries() -> None:
	freeze_c = _read("src/code/game/g_freeze.c")
	combat_c = _read("src/code/game/g_combat.c")
	active_c = _read("src/code/game/g_active.c")
	game_local = _read("src/code/game/g_local.h")

	assert "static void G_FreezeSetClientFrozenState( gentity_t *ent, qboolean frozen, qboolean environmental, qboolean wasAuto, int helperNum ) {" in freeze_c
	assert "G_FreezeSetClientFrozenState( ent, qfalse, qfalse, wasAuto, helperNum );" in freeze_c
	assert "G_FreezeSetClientFrozenState( self, qtrue, environmental, qfalse, -1 );" in freeze_c
	assert "static void G_FreezeAwardThawAssist( gentity_t *ent, int helperNum ) {" in freeze_c
	assert "GibEntity( ent );" in freeze_c
	assert "self->client->ps.powerups[PW_NUM_POWERUPS]" in combat_c
	assert "ClientSpawn( self );" in combat_c
	assert "trap_EntitiesInBox( mins, maxs, entityList, MAX_GENTITIES );" in freeze_c
	assert "G_FreezeClientCanHelpThaw( ent, helper, thawRadius, NULL )" in freeze_c

	assert "void G_FreezeResetClientForRound( gentity_t *ent ) {" in active_c
	assert "warmupSpawn = ( level.roundState != ROUNDSTATE_ACTIVE ) ? qtrue : qfalse;" in active_c
	assert "G_RequestClientSpawn( ent, warmupSpawn, qfalse );" in active_c
	assert "static void G_FreezeResetClientsForRound( void ) {" in active_c
	assert "G_FreezeResetClientForRound( ent );" in active_c
	assert "static qboolean G_FreezeTeamIsFullyFrozen( team_t team ) {" in active_c
	assert "redFrozen = G_FreezeTeamIsFullyFrozen( TEAM_RED );" in active_c
	assert "static int G_TotalLivingHealthByTeam( team_t team ) {" in active_c
	assert "G_CountActivePlayersByTeam( level.freezeLivingCount );" in active_c
	assert "level.freezeLivingHealth[TEAM_RED] = G_TotalLivingHealthByTeam( TEAM_RED );" in active_c
	assert "void\tG_FreezeResetClientForRound( gentity_t *ent );" in game_local
	assert "void GibEntity( gentity_t *self );" in game_local


def test_client_begin_and_respawn_dispatch_freeze_and_rr_like_retail() -> None:
	game_client = _read("src/code/game/g_client.c")
	begin_block = _block_from_marker(game_client, "void ClientBegin")
	respawn_block = _block_from_marker(game_client, "void respawn")

	assert "g_gametype.integer == GT_FREEZE" in begin_block
	assert "G_FreezeResetClientForRound( ent );" in begin_block
	assert "spawnedImmediately = level.clientSpawnQueued[clientNum] ? qfalse : qtrue;" in begin_block
	assert "g_gametype.integer == GT_RED_ROVER" in begin_block
	assert "G_RRResetClientForRound( ent );" in begin_block

	assert "g_gametype.integer == GT_FREEZE" in respawn_block
	assert "G_FreezeResetClientForRound( ent );" in respawn_block
	assert "spawnedImmediately = level.clientSpawnQueued[clientNum] ? qfalse : qtrue;" in respawn_block
	assert "g_gametype.integer == GT_RED_ROVER" in respawn_block
	assert "G_RRResetClientForRound( ent );" in respawn_block


def test_client_begin_refreshes_userinfo_before_retail_log_tail() -> None:
	game_client = _read("src/code/game/g_client.c")
	begin_block = _block_from_marker(game_client, "void ClientBegin")

	assert "ClientUserinfoChanged( clientNum );" in begin_block
	assert begin_block.index("ClientUserinfoChanged( clientNum );") < begin_block.index('G_LogPrintf( "ClientBegin: %i\\n", clientNum );')


def test_red_rover_helpers_match_recovered_retail_boundaries() -> None:
	game_active = _read("src/code/game/g_active.c")
	game_client = _read("src/code/game/g_client.c")
	game_local = _read("src/code/game/g_local.h")
	reset_block = _block_from_marker(game_client, "void G_RRResetClientForRound")

	assert "int G_RRResolveRoundState( void ) {" in game_active
	assert "if ( G_RRResolveRoundState() != RR_ROUNDSTATE_ACTIVE ) {" in game_client
	assert "void G_RRResetClientForRound( gentity_t *ent ) {" in game_client
	assert "G_RRResetClientForRound( ent );" in game_client
	assert "ClientSpawn( ent );" in reset_block
	assert "if ( level.rrRoundState == RR_ROUNDSTATE_WARMUP ) {" in reset_block
	assert "G_SetClientAttackLockout( ent, qtrue );" in reset_block
	assert "void G_RRInitRoundController( void );" in game_local
	assert "void G_RRResetClientForRound( gentity_t *ent );" in game_local
	assert "void G_RRHandleCompletedRound( void );" in game_local
	assert "void G_RRHandlePlayerDeath( team_t oldTeam, gentity_t *victim, gentity_t *attacker, int meansOfDeath );" in game_local
	assert "qboolean G_RRHandleDamageScore( gentity_t *attacker, gentity_t *targ, int *take, int *asave );" in game_local
	assert "void G_RRHandleCompletedRound( void ) {" in game_client
	assert "void G_RRHandlePlayerDeath( team_t oldTeam, gentity_t *victim, gentity_t *attacker, int meansOfDeath ) {" in game_client
	assert "qboolean G_RRHandleDamageScore( gentity_t *attacker, gentity_t *targ, int *take, int *asave ) {" in game_client
	assert "G_RRHandlePlayerDeath( client->sess.sessionTeam, self, attacker, meansOfDeath );" in game_client
	assert "G_FreezeRunFrame();" in game_client
	assert "G_CountConnectedClientsByTeam( counts );" in game_client
	assert "if ( G_RRCheckRoundCompletion( counts ) ) {" in game_client
	assert "level.roundTransitionTime = level.time + ( level.rrPendingMatchExit ? 1500 : 3500 );" in game_client
	assert "level.roundPendingExit = level.rrPendingMatchExit;" in game_client
	assert "if ( ScoreIsTied() ) {" in game_client


def test_client_spawn_queue_runs_on_client_frame_and_disconnect_cleanup() -> None:
	game_active = _read("src/code/game/g_active.c")
	game_client = _read("src/code/game/g_client.c")
	game_spawn = _read("src/code/game/g_spawn.c")
	game_local = _read("src/code/game/g_local.h")
	run_client_block = _block_from_marker(game_active, "void G_RunClient")
	disconnect_block = _block_from_marker(game_client, "void ClientDisconnect")
	cancel_block = _block_from_marker(game_spawn, "void G_CancelQueuedClientSpawn")

	assert "G_RunThink( ent );" in run_client_block
	assert run_client_block.index("G_RunThink( ent );") < run_client_block.index("if ( !(ent->r.svFlags & SVF_BOT) ) {")
	assert "if ( !ent->inuse || !ent->client ) {" in run_client_block
	assert "void\tG_CancelQueuedClientSpawn( int clientNum );" in game_local
	assert "G_CancelQueuedClientSpawn( clientNum );" in disconnect_block
	assert "ent->think = NULL;" in cancel_block
	assert "ent->nextthink = 0;" in cancel_block
	assert "G_ClearQueuedSpawnState( clientNum );" in cancel_block
	assert "G_UpdateSpawnQueueFlag();" in cancel_block


def test_initial_client_spawn_bypasses_respawn_queue() -> None:
	game_spawn = _read("src/code/game/g_spawn.c")
	request_block = _block_from_marker(game_spawn, "qboolean G_RequestClientSpawn")

	assert "if ( initialSpawn ) {" in request_block
	assert "delayMs = 0;" in request_block
	assert request_block.index("if ( initialSpawn ) {") < request_block.index("} else if ( warmupSpawn ) {")
	assert request_block.index("if ( initialSpawn ) {") < request_block.index("level.clientSpawnQueued[clientNum] = qtrue;")


def test_last_alive_alert_helpers_match_recovered_retail_boundaries() -> None:
	game_team = _read("src/code/game/g_team.c")
	game_local = _read("src/code/game/g_local.h")
	shared_block = _block_from_marker(game_team, "static qboolean G_NotifyLastAlivePlayer")
	ad_block = _block_from_marker(game_team, "qboolean G_ADNotifyLastAlivePlayer")
	ca_block = _block_from_marker(game_team, "qboolean G_CANotifyLastAlivePlayer")
	freeze_block = _block_from_marker(game_team, "qboolean G_FreezeNotifyLastAlivePlayer")
	rr_block = _block_from_marker(game_team, "qboolean G_RRNotifyLastAlivePlayer")

	assert "G_BroadcastGlobalTeamSound( vec3_origin, GTS_LAST_STANDING, -1, team, 0 );" in shared_block
	assert 'va( "cp \\"%s\\\\n\\"", G_LastManStandingMessage() )' in shared_block

	for expected in (
		"qboolean G_ADNotifyLastAlivePlayer( team_t team );",
		"qboolean G_CANotifyLastAlivePlayer( team_t team );",
		"qboolean G_FreezeNotifyLastAlivePlayer( team_t team );",
		"qboolean G_RRNotifyLastAlivePlayer( team_t team );",
	):
		assert expected in game_local

	for block in (ad_block, ca_block, freeze_block, rr_block):
		assert "return G_NotifyLastAlivePlayer( team );" in block
		assert "G_BroadcastGlobalTeamSound(" not in block


def test_timeout_race_and_direct_command_helpers_match_recovered_boundaries() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")
	game_match_state = _read("src/code/game/g_match_state.c")
	game_main = _read("src/code/game/g_main.c")
	game_race = _read("src/code/game/g_race.c")
	game_client = _read("src/code/game/g_client.c")
	game_svcmds = _read("src/code/game/g_svcmds.c")
	game_local = _read("src/code/game/g_local.h")
	race_info_block = _block_from_marker(game_race, "static void G_RaceBuildInfoCommand")
	race_abort_block = _block_from_marker(game_race, "static void G_RaceAbortClientRunState")
	race_leader_block = _block_from_marker(game_race, "static gclient_t *G_RaceFindLeader")
	race_score_block = _block_from_marker(game_race, "static void G_RaceBuildScoreString")
	race_start_predicate_block = _block_from_marker(game_race, "static qboolean G_RacePointIsStart")
	race_checkpoint_count_block = _block_from_marker(game_race, "static int G_RaceCheckpointCount")
	race_start_block = _block_from_marker(game_race, "static void G_RaceStartRun")
	race_finish_block = _block_from_marker(game_race, "static void G_RaceFinishRun")
	race_advance_block = _block_from_marker(game_race, "static void G_RaceAdvanceCheckpoint")
	race_touch_block = _block_from_marker(game_race, "void G_RaceHandlePointTouch")

	assert "static qboolean G_StartTimeout( gentity_t *ent, int durationSeconds ) {" in game_cmds
	assert "static qboolean G_BeginTimein( gentity_t *ent ) {" in game_cmds
	assert "void Cmd_Pause_f( gentity_t *ent ) {" in game_cmds
	assert "static int G_KickOrBanClient( gentity_t *ent, char *targetToken, qboolean banTarget ) {" in game_cmds
	assert 'G_DirectCommandPrint( ent, "print \\"Can not kick admins.\\n\\"" );' in game_cmds
	assert "G_KickOrBanClient( ent, arg, qfalse );" in game_cmds
	assert "G_KickOrBanClient( ent, arg, qtrue );" in game_cmds
	assert "G_KickOrBanClient( ent, val, qfalse );" in game_cmds
	assert "G_KickOrBanClient( ent, val, qtrue );" in game_cmds

	assert "void G_UpdateTimeoutConfigStrings( void ) {" in game_match_state
	assert "static void G_UpdateRoundStartConfigString( void ) {" in game_match_state
	assert "if ( level.roundState == ROUNDSTATE_ACTIVE ) {" in game_match_state
	assert "g_gametype.integer == GT_CLAN_ARENA && level.roundState == ROUNDSTATE_COMPLETE" in game_match_state
	assert "g_gametype.integer == GT_ATTACK_DEFEND" in game_match_state
	assert "level.adRoundState == AD_ROUNDSTATE_COMPLETE || level.adRoundState == AD_ROUNDSTATE_EXIT" in game_match_state
	assert "g_gametype.integer == GT_RED_ROVER" in game_match_state
	assert "level.rrRoundState == RR_ROUNDSTATE_COMPLETE || level.rrRoundState == RR_ROUNDSTATE_EXIT" in game_match_state
	assert "trap_SetConfigstring( CS_ROUND_START_TIME, va( \"%i\", -1 ) );" in game_match_state
	assert "trap_SetConfigstring( CS_ROUND_START_TIME" in game_match_state
	assert "trap_SetConfigstring( CS_TIMEOUT_START_TIME" in game_match_state
	assert "trap_SetConfigstring( CS_TIMEOUT_EXPIRE_TIME" in game_match_state
	assert "trap_SetConfigstring( CS_TIMEOUT_COUNT_RED" in game_match_state
	assert "trap_SetConfigstring( CS_TIMEOUT_COUNT_BLUE" in game_match_state
	assert "G_UpdateRoundStartConfigString();" in game_match_state
	assert "G_UpdateTimeoutConfigStrings();" in game_match_state

	assert "static void G_CheckTimeoutExpired( void ) {" in game_main
	assert "G_CheckTimeoutExpired();" in game_main
	assert "static void G_UpdateDominationCaptureTimeConfigstring( qboolean forceBroadcast ) {" in game_main
	assert "trap_SetConfigstring( CS_DOMINATION_CAPTURE_TIME, payload );" in game_main
	assert "static void G_UpdateRRInfectedSurvivorPingRateConfigstring( qboolean forceBroadcast ) {" in game_main
	assert "trap_SetConfigstring( CS_RR_INFECTED_SURVIVOR_PING_RATE, payload );" in game_main
	assert "static void G_UpdateModeSpecificConfigstrings( qboolean forceBroadcast ) {" in game_main
	assert "G_UpdateModeSpecificConfigstrings( qtrue );" in game_main
	assert "G_UpdateModeSpecificConfigstrings( qfalse );" in game_main
	assert "static int G_AdminAccessForConnectedClient( int clientNum ) {" in game_main
	assert "void G_ReloadAdminAccess( void ) {" in game_main
	assert "client->sess.privilege = G_AdminAccessForConnectedClient( clientNum );" in game_main
	assert "void\tG_ReloadAdminAccess( void );" in game_local
	assert "trap_SetConfigstring( CS_SPAWN_HINTS" not in _read("src/game/g_match_config.c")

	assert "void G_RaceResetClientAndSpawn( gentity_t *ent ) {" in game_race
	assert "void Cmd_RaceInit_f( gentity_t *ent ) {" in game_race
	assert "G_RaceBroadcastInitCommand( ent->s.number );" in game_race
	assert 'trap_SendServerCommand( clientNum, "race_init" );' in game_race
	assert "G_RaceAbortClientRunState( ent->client );" in game_race
	assert "client->raceState.startTime = 0;" not in race_abort_block
	assert "memset( client->raceState.currentSplits" not in race_abort_block
	assert "qboolean FollowCycle( gentity_t *ent, int dir ) {" in game_cmds
	assert "qboolean FollowCycle( gentity_t *ent, int dir );" in game_local
	assert 'G_Error( "FollowCycle: bad dir %i", dir );' in game_cmds
	assert 'G_Printf( "FollowCycle: bad input clientnum value: %d, maxclients: %d\\n", clientnum, level.maxclients );' in game_cmds
	assert "clientTeam = ent->client->sess.sessionTeam;" in game_cmds
	assert "if ( clientnum < 0 || clientnum >= level.maxclients ) {" in game_cmds
	assert "if ( curr >= level.maxclients ) {" in game_cmds
	assert "level.clients[curr].ps.pm_type == PM_SPECTATOR" in game_cmds
	assert "level.clients[curr].ps.pm_flags & PMF_FOLLOW" in game_cmds
	assert "clientTeam != TEAM_SPECTATOR && g_gametype.integer >= GT_TEAM" in game_cmds
	assert "G_RaceSendInfoCommand( ent - g_entities );" in game_cmds
	assert "FollowCycle( ent, dir );" in game_cmds
	assert "level.numPois" not in game_cmds
	assert "poiIndex" not in game_cmds
	assert 'Com_sprintf( buffer, bufferSize, "race_info %i %i %i %i %i %i",' in game_race
	assert "checkpointCount = G_RaceCheckpointCount( client );" in race_info_block
	assert "if ( client->raceState.active ) {" not in race_info_block
	assert "static gentity_t *G_RacePickPointTarget( const gentity_t *point ) {" in game_race
	assert "static qboolean G_RacePointIsStart( const gentity_t *point ) {" in game_race
	assert "if ( !point->targetname || !point->targetname[0] ) {" in race_start_predicate_block
	assert "if ( point->racePointAdminSpawned && point->racePointIndex == 0 ) {" in race_start_predicate_block
	assert "if ( point->racePointIndex == 0 ) {" not in race_start_predicate_block
	assert "static gentity_t *G_RaceEmitClientEvent( gentity_t *player, int event ) {" in game_race
	assert "client->raceState.currentPoint = currentPoint;" in game_race
	assert "client->raceState.nextPoint = G_RacePickPointTarget( currentPoint );" in game_race
	assert "client->raceState.currentPoint = G_RacePickPointTarget( point );" in game_race
	assert "client->raceState.nextPoint = G_RacePickPointTarget( client->raceState.currentPoint );" in game_race
	assert "return client->raceState.nextCheckpoint;" in race_checkpoint_count_block
	assert "client->raceState.nextCheckpoint - 1" not in race_checkpoint_count_block
	assert "client->raceState.nextCheckpoint = 0;" in race_start_block
	assert "client->raceState.currentSplits[0] = 0;" not in race_start_block
	assert "client->raceState.currentSplits[client->raceState.nextCheckpoint] = elapsed;" in race_advance_block
	assert "client->raceState.currentSplits[client->raceState.nextCheckpoint] = elapsed;" not in race_finish_block
	assert "G_RaceEmitStartEvent( player );" in game_race
	assert "G_RaceEmitCheckpointEvent( player, splitDelta, hasBestSplit );" in game_race
	assert "G_RaceEmitFinishEvent( player, elapsed );" in game_race
	assert "G_RaceEmitNewHighScoreEvent( player );" in game_race
	assert 'format = personalBest ? "^1Personal best! ^7%s^7 finished the race in in %s\\n" : "%s^7 finished the race in %s\\n";' in game_race
	assert "static void G_RaceSyncScore( gclient_t *client ) {" in game_race
	assert "client->ps.persistant[PERS_SCORE] = client->raceState.bestTime;" in game_race
	assert "G_RaceSyncScore( client );" in game_race
	assert "client->raceState.bestTime = RACE_INVALID_TIME;" in game_race
	assert "memset( client->raceState.bestSplits, 0, sizeof( client->raceState.bestSplits ) );" in game_race
	assert "static int G_RaceResolveUniqueFinishTime( int elapsed ) {" in game_race
	assert "if ( elapsed == level.clients[clientNum].ps.persistant[PERS_SCORE] ) {" in game_race
	assert "elapsed = G_RaceResolveUniqueFinishTime( elapsed );" in game_race
	assert "client->ps.persistant[PERS_SCORE] == RACE_INVALID_TIME" in race_leader_block
	assert "client->ps.persistant[PERS_SCORE] < leader->ps.persistant[PERS_SCORE]" in race_leader_block
	assert "newHighScore = ( leader == NULL || elapsed < leader->ps.persistant[PERS_SCORE] ) ? qtrue : qfalse;" in race_finish_block
	assert "G_RaceClearClientRunState( client );\n\tCalculateRanks();" in game_race
	assert "if ( level.intermissiontime ) {" in race_touch_block
	assert "static int G_RaceScoreboardPing( const gclient_t *client ) {" in game_race
	assert "static int G_RaceScoreboardSessionSeconds( const gclient_t *client ) {" in game_race
	assert "ping = G_RaceScoreboardPing( client );" in game_race
	assert "sessionSeconds = G_RaceScoreboardSessionSeconds( client );" in game_race
	assert "count = level.numPlayingClients;" in race_score_block
	assert "clientNum = level.sortedClients[i];" in race_score_block
	assert "indices[" not in race_score_block
	assert "qsort(" not in race_score_block
	assert 'Com_sprintf( entry, sizeof( entry ), " %i %i %i %i", clientNum, bestTime, ping, sessionSeconds );' in race_score_block
	assert "if ( g_gametype.integer == GT_RACE ) {" in game_main
	assert "ca->ps.persistant[PERS_SCORE]\n\t\t\t< cb->ps.persistant[PERS_SCORE]" in game_main
	assert "ca->ps.persistant[PERS_SCORE]\n\t\t\t> cb->ps.persistant[PERS_SCORE]" in game_main
	assert "Cmd_RaceInit_f( ent );" in game_cmds
	assert "void\tCmd_RaceInit_f( gentity_t *ent );" in game_local
	assert "gentity_t\t\t*currentPoint;" in game_local
	assert "gentity_t\t\t*nextPoint;" in game_local
	assert "G_RaceResetClientAndSpawn( ent );" in game_client

	assert "static void Svcmd_DumpVars_f( void ) {" in game_svcmds
	assert 'G_Printf( "Data Dump: (%s)\\n", cl->pers.netname );' in game_svcmds
	assert 'G_Printf( "clientNum: %d\\n", ( int )( cl - level.clients ) );' in game_svcmds
	assert 'G_Printf( "pm_type: 0x%08x\\n", cl->ps.pm_type );' in game_svcmds
	assert 'G_Printf( "pm_flags: 0x%08x\\n", cl->ps.pm_flags );' in game_svcmds
	assert 'G_Printf( "pm_time: %d\\n", cl->ps.pm_time );' in game_svcmds
	assert 'G_Printf( "eFlags: %d\\n", cl->ps.eFlags );' in game_svcmds
	assert 'G_Printf( "origin: (%0.3f, %0.3f, %0.3f)\\n", cl->ps.origin[0], cl->ps.origin[1], cl->ps.origin[2] );' in game_svcmds
	assert "static void Svcmd_GameCrash_f( void ) {" in game_svcmds
	assert 'trap_Cvar_VariableIntegerValue( "developer" ) < 1' in game_svcmds
	assert "*(volatile int *)0 = 0x12345678;" in game_svcmds
	assert "static void Svcmd_ReloadAccess_f( void ) {" in game_svcmds
	assert "G_ReloadAdminAccess();" in game_svcmds
	assert 'if ( Q_stricmp (cmd, "game_crash") == 0 ) {' in game_svcmds
	assert 'if ( Q_stricmp (cmd, "forceshuffle") == 0 ) {' in game_svcmds
	assert 'if ( Q_stricmp (cmd, "dumpvars") == 0 ) {' in game_svcmds
	assert 'if ( Q_stricmp (cmd, "reload_access") == 0 ) {' in game_svcmds
	assert "Svcmd_GameCrash_f();" in game_svcmds
	assert "Svcmd_DumpVars_f();" in game_svcmds
	assert "Svcmd_ReloadAccess_f();" in game_svcmds


def test_custom_settings_cvar_helper_matches_recovered_boundary() -> None:
	game_main = _read("src/code/game/g_main.c")
	register_block = _block_from_marker(game_main, "void G_RegisterCvars")
	update_block = _block_from_marker(game_main, "void G_UpdateCvars")
	helper_block = _block_from_marker(game_main, "static void G_UpdateCustomSettingsMaskForCvar")

	assert "static void G_UpdateCustomSettingsMaskForCvar( const cvarTable_t *cv );" in game_main
	assert "if ( !cv || !cv->customSetting ) {" in helper_block
	assert "s_customSettingsDirty = qtrue;" in helper_block
	assert "G_UpdateCustomSettingsMaskForCvar( cv );" in register_block
	assert "G_UpdateCustomSettingsMaskForCvar( cv );" in update_block


def test_g_initgame_pipeline_matches_recovered_retail_bootstrap_order() -> None:
	game_main = _read("src/code/game/g_main.c")
	game_session = _read("src/code/game/g_session.c")
	game_local = _read("src/code/game/g_local.h")
	init_block = _block_from_marker(game_main, "void G_InitGame")
	published_block = _block_from_marker(game_main, "static void G_InitPublishedCvarState")
	level_mirror_block = _block_from_marker(game_main, "static void G_InitLevelCvarMirrors")

	assert "static int\ts_adminAccessEntryCount = 0;" in game_main
	assert "static adminAccessEntry_t\ts_adminAccessList[MAX_ADMIN_ACCESS_ENTRIES];" in game_main
	assert "level.adminAccessEntryCount" not in game_main
	assert "level.adminAccessList" not in game_main

	assert "G_MatchConfig_UpdateConfigstrings();" in published_block
	assert "G_UpdateDisableLoadoutConfigstrings();" in published_block
	assert "G_PmoveSetConfigstringsReady( qtrue );" in published_block
	assert "G_RefreshPmoveSettings();" in published_block
	assert "G_UpdateItemTimerConfig( qtrue );" in published_block
	assert "G_UpdateForcedCosmeticsConfigstring( qtrue );" in published_block
	assert "G_UpdateGametypeTutorialText();" in published_block
	assert "G_SyncMatchFactoryConfigToLevel();" in level_mirror_block
	assert "level.quadHogEnabled = ( g_weaponConfig.quadHogEnabled != 0 );" in level_mirror_block

	for expected in (
		"Factory_ApplyCurrentSelection( qtrue );",
		"G_InitPublishedCvarState();",
		"G_LoadAdminAccessFile();",
		"G_InitMemory();",
		"G_InitLevelCvarMirrors();",
		"level.previousTime = levelTime;",
		"level.pendingVoteClientNum = -1;",
		'trap_Cvar_Set( "g_levelStartTime", startTimeBuffer );',
		"G_SetGameState( GAME_STATE_PRE_GAME );",
		"level.timeoutOwner = -1;",
		"level.timeoutTeam = TEAM_FREE;",
		"level.timeoutActive = qfalse;",
		"level.timeoutStartTime = 0;",
		"level.timeoutExpireTime = 0;",
		"level.intermissionExitStatusLatched = qfalse;",
		"level.overtimeAccumulatedMsec = 0;",
		"level.overtimeActive = qfalse;",
		"level.overtimeStartTime = 0;",
		"level.overtimeEndTime = 0;",
		"level.overtimeCount = 0;",
		"level.suddenDeathActive = qfalse;",
		"level.suddenDeathLastDelay = -1;",
		"level.suddenDeathNoRespawnLogged = qfalse;",
		"level.timeoutRemaining[team] = g_matchFactoryConfig.timeoutCountPerTeam;",
		"matchFlow_lastConfig = g_matchFactoryConfig;",
		'trap_Cvar_VariableStringBuffer( "session", session, sizeof( session ) );',
		'G_Printf( "Gametype changed, clearing session data.\\n" );',
		'trap_GetConfigstring( CS_MATCH_GUID, matchGuidInfo, sizeof( matchGuidInfo ) );',
		'trap_SetConfigstring( CS_MATCH_GUID, matchGuidInfo );',
		"FindIntermissionPoint();",
		"G_FreezeSyncCvars();",
		"level.timeoutRemaining[team] = 0;",
		"level.timeoutOwner = -1;",
		"level.timeoutTeam = TEAM_FREE;",
		"level.timeoutExpireTime = 0;",
		"level.timeoutStartTime = 0;",
		"G_UpdateTimeoutConfigStrings();",
		"G_SpawnQuadHogQuad();",
		"G_SpawnItemPowerups();",
		"LevelCheckTimers();",
		"G_UpdateMatchStateConfigString();",
		"G_UpdateTeamCountConfigstrings();",
		"G_MatchConfig_UpdateConfigstrings();",
		"G_UpdateTournamentQueuePositions();",
	):
		assert expected in init_block

	assert "G_ProcessIPBans();" not in init_block
	assert "G_AutoAction( AUTOACTION_MATCH_START" not in init_block
	assert "G_InitWorldSession();" not in init_block
	assert "void G_InitWorldSession( void ) {" not in game_session
	assert "void G_InitWorldSession( void );" not in game_local

	assert init_block.index("Factory_ApplyCurrentSelection( qtrue );") < init_block.index("G_InitPublishedCvarState();")
	assert init_block.index("G_InitPublishedCvarState();") < init_block.index("G_LoadAdminAccessFile();")
	assert init_block.index("G_LoadAdminAccessFile();") < init_block.index("G_InitMemory();")
	assert init_block.index("G_InitMemory();") < init_block.index("memset( &level, 0, sizeof( level ) );")
	assert init_block.index("memset( &level, 0, sizeof( level ) );") < init_block.index("G_InitLevelCvarMirrors();")
	assert init_block.index("level.pendingVoteClientNum = -1;") < init_block.index('trap_Cvar_Set( "g_levelStartTime", startTimeBuffer );')
	assert init_block.index('trap_Cvar_Set( "g_levelStartTime", startTimeBuffer );') < init_block.index('level.snd_fry = G_SoundIndex("sound/player/fry.wav");')
	assert init_block.index("G_SetGameState( GAME_STATE_PRE_GAME );") < init_block.index("level.timeoutOwner = -1;")
	assert init_block.index("level.suddenDeathNoRespawnLogged = qfalse;") < init_block.index("matchFlow_lastConfig = g_matchFactoryConfig;")
	assert init_block.index('trap_Cvar_VariableStringBuffer( "session", session, sizeof( session ) );') < init_block.index("memset( g_entities, 0, MAX_GENTITIES * sizeof(g_entities[0]) );")

	assert published_block.index("G_PmoveSetConfigstringsReady( qtrue );") < published_block.index("G_RefreshPmoveSettings();")
	assert published_block.index("G_UpdateItemTimerConfig( qtrue );") < published_block.index("G_UpdateForcedCosmeticsConfigstring( qtrue );")
	assert published_block.index("G_UpdateForcedCosmeticsConfigstring( qtrue );") < published_block.index("G_UpdateWeaponReloadConfigstring( qtrue );")


	assert init_block.index('trap_GetConfigstring( CS_MATCH_GUID, matchGuidInfo, sizeof( matchGuidInfo ) );') < init_block.index("trap_LocateGameData( level.gentities, level.num_entities, sizeof( gentity_t ),")
	assert init_block.index('trap_SetConfigstring( CS_MATCH_GUID, matchGuidInfo );') < init_block.index("trap_LocateGameData( level.gentities, level.num_entities, sizeof( gentity_t ),")
	assert init_block.index("G_SpawnEntitiesFromString();") < init_block.index("FindIntermissionPoint();")
	assert init_block.index("FindIntermissionPoint();") < init_block.index("G_CountSpawnPoints();")
	assert init_block.index("G_CountSpawnPoints();") < init_block.index("G_InitLagHaxHistory();")
	lag_history_index = init_block.index("G_InitLagHaxHistory();")
	assert lag_history_index < init_block.index("G_UpdateTrainingState();", lag_history_index)
	assert init_block.index("G_UpdateTimeoutConfigStrings();") < init_block.index("BotAISetup( restart );")
	assert init_block.index("BotAISetup( restart );") < init_block.index("G_SpawnQuadHogQuad();")
	assert init_block.index("G_SpawnQuadHogQuad();") < init_block.index("G_SpawnItemPowerups();")
	assert init_block.index("G_RemapTeamShaders();") < init_block.index("LevelCheckTimers();")
	assert init_block.index("LevelCheckTimers();") < init_block.index("G_UpdateMatchStateConfigString();")
	assert init_block.index("G_UpdateMatchStateConfigString();") < init_block.index("G_UpdateTeamCountConfigstrings();")
	assert init_block.index("G_UpdateTeamCountConfigstrings();") < init_block.index("G_MatchConfig_UpdateConfigstrings();")
	assert init_block.index("G_MatchConfig_UpdateConfigstrings();") < init_block.index("G_UpdateTournamentQueuePositions();")


def test_register_cvars_does_not_publish_configstrings_during_app_bootstrap() -> None:
	game_main = _read("src/code/game/g_main.c")
	register_block = _block_from_marker(game_main, "void G_RegisterCvars")

	for forbidden in (
		"G_RemapTeamShaders();",
		"G_RefreshPmoveSettings();",
		"G_UpdateItemTimerConfig( qtrue );",
		"G_MatchConfig_UpdateConfigstrings();",
		"G_UpdateForcedCosmeticsConfigstring( qtrue );",
		"G_UpdateGametypeTutorialText();",
	):
		assert forbidden not in register_block


def test_console_tail_and_training_bootstrap_helpers_match_recovered_boundaries() -> None:
	game_svcmds = _read("src/code/game/g_svcmds.c")
	game_bot = _read("src/code/game/g_bot.c")
	game_local = _read("src/code/game/g_local.h")
	init_bots = _block_from_marker(game_bot, "void G_InitBots")
	addbot_block = _block_from_marker(game_bot, "void Svcmd_AddBot_f")

	assert 'Q_stricmp( cmd, "markstate" ) == 0 ||' in game_svcmds
	assert 'Q_stricmp( cmd, "diffstate" ) == 0 ||' in game_svcmds
	assert 'Q_stricmp( cmd, "dumpentities" ) == 0 ||' in game_svcmds
	assert 'Q_stricmp( cmd, "printentitystates" ) == 0 ) {' in game_svcmds
	assert 'if ( Q_stricmp( cmd, "floodstatus" ) == 0 ) {' in game_svcmds
	assert "Svcmd_FloodStatus_f();" in game_svcmds

	assert "void G_AddTrainerBot( void ) {" in game_bot
	assert "void G_AddTrainerBot( void );" in game_local
	assert 'G_AddBot( "Trainer", skill, "", 5000, "" );' in game_bot
	assert 'trap_SendServerCommand( -1, "loaddeferred\\n" );' in game_bot
	assert 'if ( level.trainingMapActive ) {' in addbot_block
	assert 'trap_Printf( "Addbot not allowed during training.\\n" );' in addbot_block
	assert 'trap_SendServerCommand( -1, "loaddeferred\\n" );' in addbot_block
	assert "loaddefered" not in addbot_block
	assert addbot_block.index('trap_Cvar_VariableIntegerValue( "bot_enable" )') < addbot_block.index("if ( level.trainingMapActive )")
	assert addbot_block.index("if ( level.trainingMapActive )") < addbot_block.index("trap_Argv( 1, name, sizeof( name ) );")
	assert 'if( Q_stricmp( strValue, "training" ) == 0 ) {' in init_bots
	assert "G_AddTrainerBot();" in init_bots
	assert "G_SpawnBots( Info_ValueForKey( arenainfo, ARENA_INFO_KEY_BOTS ), BOT_BEGIN_DELAY_BASE );" in init_bots
	assert "basedelay += 10000;" not in game_bot


def test_shutdown_game_routes_engine_error_message_through_retail_log_exit_path() -> None:
	game_main = _read("src/code/game/g_main.c")
	retail_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt")
	shutdown_block = _block_from_marker(game_main, "void G_ShutdownGame")

	assert '(*(data_104b13ac + 0x34))("com_errorMessage", &var_404, 0x400)' in retail_hlil
	assert "if (var_404 == 0)" in retail_hlil
	assert '__builtin_strncpy(dest: &var_404, src: "Shutdown", n: 9)' in retail_hlil
	assert "if (data_105dce5c != 0)" in retail_hlil
	assert "sub_10057510(x87_r0, 1, arg1, &var_404)" in retail_hlil
	assert "sub_10065af0()" in retail_hlil
	assert "sub_10032a10()" in retail_hlil

	for expected in (
		"char\texitReason[MAX_STRING_CHARS];",
		"G_PmoveClearConfigstring();",
		"G_PmoveSetConfigstringsReady( qfalse );",
		'trap_Cvar_VariableStringBuffer( "com_errorMessage", exitReason, sizeof( exitReason ) );',
		"if ( !exitReason[0] ) {",
		'Q_strncpyz( exitReason, "Shutdown", sizeof( exitReason ) );',
		"if ( level.time ) {",
		"LogExit( exitReason );",
		"G_WriteSessionData();",
		"G_WriteAdminAccessFile();",
		"level.logFile = 0;",
	):
		assert expected in shutdown_block

	assert shutdown_block.index("G_PmoveClearConfigstring();") < shutdown_block.index("G_PmoveSetConfigstringsReady( qfalse );")
	assert shutdown_block.index('trap_Cvar_VariableStringBuffer( "com_errorMessage", exitReason, sizeof( exitReason ) );') < shutdown_block.index("if ( !exitReason[0] ) {")
	assert shutdown_block.index("if ( !exitReason[0] ) {") < shutdown_block.index("if ( level.time ) {")
	assert shutdown_block.index("if ( level.time ) {") < shutdown_block.index("LogExit( exitReason );")
	assert shutdown_block.index("LogExit( exitReason );") < shutdown_block.index("G_WriteSessionData();")
	assert shutdown_block.index("G_WriteSessionData();") < shutdown_block.index("G_WriteAdminAccessFile();")
	assert shutdown_block.index("G_WriteAdminAccessFile();") < shutdown_block.index("if ( level.logFile ) {")
	assert shutdown_block.index("level.logFile = 0;") < shutdown_block.index('trap_Cvar_VariableIntegerValue( "bot_enable" )')


def test_bot_training_state_tail_is_wired_to_bot_frame() -> None:
	ai_main = _read("src/code/game/ai_main.c")
	training_tail = _block_from_marker(ai_main, "static void BotUpdateTrainingState")
	start_frame = _block_from_marker(ai_main, "int BotAIStartFrame")

	assert "static void BotSetPredictItemPickupDisabled( int clientNum, qboolean disabled ) {" in ai_main
	assert "static void BotUpdateItemDelayTime( int time ) {" in ai_main
	assert "static void BotUpdateTrainingBotSkill( int botClient ) {" in ai_main
	assert "static void BotUpdateTrainingReadyState( int localClient, int botClient ) {" in ai_main
	assert "static void BotUpdateTrainingMusic( int localClient ) {" in ai_main
	assert 'BotSetTrainingCvarIfChanged( "g_training", "0" );' in ai_main
	assert 'BotSetTrainingCvarIfChanged( "bot_training", "0" );' in ai_main
	assert 'BotSetTrainingCvarIfChanged( "bot_dynamicSkill", "0" );' in ai_main
	assert 'BotSetTrainingCvarIfChanged( "bot_followMe", "1" );' in ai_main
	assert 'BotSetTrainingCvarIfChanged( "bot_itemDelayTime", delayValue );' in ai_main
	assert 'BotSetTrainingCvarIfChanged( "bot_startingSkill", BotFormatTrainingSkill( skill ) );' in ai_main
	assert "localClient = BotGetLocalClient();" in training_tail
	assert "botClient = BotGetFirstBotClient();" in training_tail
	assert 'trap_Cvar_Set( "g_spSkill", BotFormatTrainingSkill( bootstrapSkill ) );' in training_tail
	assert "G_AddTrainerBot();" in training_tail
	assert 'trap_SendServerCommand( localClient, "stopMusic" );' in ai_main
	assert 'trap_SendServerCommand( localClient, "playMusic music/fla22k_01_loop" );' in ai_main
	assert 'trap_SendServerCommand( localClient, "playMusic music/win" );' in ai_main
	assert 'trap_SendServerCommand( localClient, "playMusic music/loss" );' in ai_main
	assert "BotUpdateTrainingState();" in start_frame
	assert start_frame.index("trap_BotUserCommand(botstates[i]->client, &botstates[i]->lastucmd);") < start_frame.index("BotUpdateTrainingState();")
	assert start_frame.index("BotUpdateItemDelayTime( time );") < start_frame.index("BotUpdateDynamicSkill( time );")
	assert start_frame.index("BotUpdateDynamicSkill( time );") < start_frame.index("BotUpdateTrainingState();")
	assert start_frame.index("BotUpdateTrainingState();") < start_frame.index("RETAIL_SELECTED_BOT_INFO_CONFIGSTRING")


def test_bot_selected_debug_info_uses_retail_node_name_storage() -> None:
	ai_main = _read("src/code/game/ai_main.c")
	ai_main_h = _read("src/code/game/ai_main.h")
	ai_dmnet = _read("src/code/game/ai_dmnet.c")
	qagame_symbols = _read("references/symbol-maps/qagame.json")
	qagame_ghidra = _read("references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c")
	qagame_hlil = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt")
	record_block = _block_from_marker(ai_dmnet, "void BotRecordNodeSwitch")
	publish_block = _block_from_marker(ai_main, "static int BotPublishDebugInfoString")
	start_frame = _block_from_marker(ai_main, "int BotAIStartFrame")
	reset_block = _block_from_marker(ai_main, "void BotResetState")
	retail_payload = "e\\\\%s\\\\ed\\\\%.1f\\\\tg\\\\%s\\\\tgd\\\\%.1f\\\\sg\\\\%s\\\\sgd\\\\%.1f\\\\ainode\\\\%s\\\\ltg\\\\%s\\\\ban\\\\%i\\\\gan\\\\%i\\\\bh\\\\%i\\\\ba\\\\%i\\\\sk\\\\%.1f\\\\eh\\\\%i\\\\"

	assert '"normalized_name": "BotRecordNodeSwitch"' in qagame_symbols
	assert '"normalized_name": "BotPublishDebugInfoString"' in qagame_symbols
	assert '"address": "0x10008460"' in qagame_symbols
	assert '"address": "0x10022EE0"' in qagame_symbols
	assert "sub_10070be0(arg1 + 0x23cc, 0x50, &data_1007c7bc)" in qagame_hlil
	assert "10022d2c  memset(arg1, 0, 0x2698)" in qagame_hlil
	assert "param_1 + 0x23cc,&local_1e0" in qagame_ghidra
	assert retail_payload in qagame_ghidra

	assert "#define MAX_AINODENAME" in ai_main_h
	assert "80" in ai_main_h[ai_main_h.index("#define MAX_AINODENAME"):ai_main_h.index("//bot flags")]
	assert "char ainodename[MAX_AINODENAME];" in ai_main_h
	assert 'Com_sprintf(bs->ainodename, sizeof(bs->ainodename), "%s", node);' in record_block
	assert record_block.index("Com_sprintf(nodeswitch[numnodeswitches]") < record_block.index("Com_sprintf(bs->ainodename")

	assert "BotDebugAINodeName" not in ai_main
	assert retail_payload in publish_block
	assert "bs->ainodename," in publish_block
	assert "trap_SetConfigstring( RETAIL_SELECTED_BOT_INFO_CONFIGSTRING" in publish_block
	assert "memset(bs, 0, sizeof(bot_state_t));" in reset_block
	assert "ainodename" not in reset_block
	assert 'if ( !bot_developer.integer || bot_report.integer < 0 ) {' in start_frame
	assert "BotPublishDebugInfoString( botstates[i] );" in start_frame
	assert start_frame.index("bot_report.integer < 0") < start_frame.index("BotPublishDebugInfoString( botstates[i] );")


def test_info_string_helpers_keep_room_for_the_terminating_nul() -> None:
	q_shared_c = _read("src/code/game/q_shared.c")
	q_shared_cpp = _read("src/code/splines/q_shared.cpp")

	assert "if (strlen(newi) + strlen(s) >= MAX_INFO_STRING)" in q_shared_c
	assert "if (strlen(newi) + strlen(s) >= BIG_INFO_STRING)" in q_shared_c
	assert "if (strlen(newi) + strlen(s) >= MAX_INFO_STRING)" in q_shared_cpp
