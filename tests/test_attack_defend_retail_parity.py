"""Retail parity guards for Attack and Defend gametype wiring."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
QAGAME_SYMBOLS = REPO_ROOT / "references" / "symbol-maps" / "qagame.json"
CGAME_SYMBOLS = REPO_ROOT / "references" / "symbol-maps" / "cgame.json"
QAGAME_HLIL = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil.txt"
)
QAGAME_GHIDRA = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "decompile_top_functions.c"
)
CGAME_GHIDRA = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "cgamex86"
	/ "decompile_top_functions.c"
)
G_LOCAL = REPO_ROOT / "src" / "code" / "game" / "g_local.h"
G_TEAM = REPO_ROOT / "src" / "code" / "game" / "g_team.c"
G_ITEMS = REPO_ROOT / "src" / "code" / "game" / "g_items.c"
G_COMBAT = REPO_ROOT / "src" / "code" / "game" / "g_combat.c"
G_CLIENT = REPO_ROOT / "src" / "code" / "game" / "g_client.c"
G_ACTIVE = REPO_ROOT / "src" / "code" / "game" / "g_active.c"
G_MAIN = REPO_ROOT / "src" / "code" / "game" / "g_main.c"
G_CMDS = REPO_ROOT / "src" / "code" / "game" / "g_cmds.c"
G_MATCH_STATE = REPO_ROOT / "src" / "code" / "game" / "g_match_state.c"
G_FACTORY = REPO_ROOT / "src" / "code" / "game" / "g_factory.c"
G_SPAWN = REPO_ROOT / "src" / "code" / "game" / "g_spawn.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_DRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_ENTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_ents.c"
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_PLAYERS = REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
IMPLEMENTATION_PLAN = REPO_ROOT / "IMPLEMENTATION_PLAN.md"


def _source(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _extract_block(source: str, marker: str) -> str:
	start = source.index(marker)
	brace_start = source.index("{", start)
	depth = 0

	for index in range(brace_start, len(source)):
		char = source[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start : index + 1]

	raise AssertionError(f"Unterminated block for {marker}")


def _block(path: Path, marker: str) -> str:
	return _extract_block(_source(path), marker)


def _symbol_names(path: Path) -> set[str]:
	payload = json.loads(path.read_text(encoding="utf-8"))
	return {entry["normalized_name"] for entry in payload["functions"]}


def test_retail_symbol_maps_cover_attack_defend_owner_functions() -> None:
	qagame_names = _symbol_names(QAGAME_SYMBOLS)
	cgame_names = _symbol_names(CGAME_SYMBOLS)

	for name in (
		"G_CAADRespawnAsSpectator",
		"G_ADShouldTimeoutActiveRound",
		"G_ADResolveRoundState",
		"G_ADHandleDamageScore",
		"G_ADCheckExitRules",
		"AD_RoundStateTransition",
		"G_ADNotifyLastAlivePlayer",
		"G_ADResolveAttackingTeam",
		"G_ADResolveDefendingTeam",
		"G_ADResetScoreHistory",
		"G_ADUpdateScoreHistory",
		"G_CAADResetClientForRound",
		"Team_SetFlagStatus",
		"Team_TouchEnemyFlag",
		"Pickup_Team",
		"G_BuildCTFStyleScoreboardMessage",
		"Drop_Item",
	):
		assert name in qagame_names

	for name in (
		"CG_IsRoundStartGametype",
		"CG_DrawWarmupStartBanner",
		"CG_DrawWarmupStatusText",
		"CG_DrawADRoundScoreboard",
		"CG_ParseADScores",
		"CG_DrawObjectiveStatus",
		"CG_DrawDominationOwnedFlags",
		"CG_DrawMatchEndCondition",
		"CG_PlayerObjectiveSprite",
		"CG_FeederItemTextCTFFamilyTeamList",
		"CG_FeederItemTextCTFFamilyStats",
	):
		assert name in cgame_names


def test_ad_flag_status_and_map_item_validation_follow_retail_ctf_branch() -> None:
	init_block = _block(G_TEAM, "void Team_InitGame( void ) {")
	status_block = _block(G_TEAM, "void Team_SetFlagStatus( int team, flagStatus_t status ) {")
	check_block = _block(G_ITEMS, "void G_CheckTeamItems( void ) {")
	flag_parse_block = _block(CG_SERVERCMDS, "static void CG_ParseFlagStatusConfigString( const char *str ) {")
	config_values_block = _block(CG_SERVERCMDS, "void CG_SetConfigValues( void ) {")
	configstring_block = _block(CG_SERVERCMDS, "static void CG_ConfigStringModified( void ) {")
	qagame_hlil = _source(QAGAME_HLIL)
	qagame_decompile = _source(QAGAME_GHIDRA)

	assert init_block.index("case GT_CTF:") < init_block.index("case GT_ATTACK_DEFEND:")
	assert init_block.index("case GT_ATTACK_DEFEND:") < init_block.index(
		"teamgame.redStatus = teamgame.blueStatus = -1;"
	)
	assert "Team_SetFlagStatus( TEAM_RED, FLAG_ATBASE );" in init_block
	assert "Team_SetFlagStatus( TEAM_BLUE, FLAG_ATBASE );" in init_block
	assert "G_ADResetScoreHistory();" in init_block

	assert "g_gametype.integer == GT_CTF || g_gametype.integer == GT_ATTACK_DEFEND" in status_block
	assert "st[0] = ctfFlagStatusRemap[teamgame.redStatus];" in status_block
	assert "st[1] = ctfFlagStatusRemap[teamgame.blueStatus];" in status_block
	assert "st[2] = 0;" in status_block
	assert "st[0] = oneFlagStatusRemap[teamgame.flagStatus];" in status_block

	assert "g_gametype.integer == GT_CTF || g_gametype.integer == GT_ATTACK_DEFEND" in check_block
	assert 'BG_FindItem( "Red Flag" );' in check_block
	assert 'G_Printf( S_COLOR_YELLOW "WARNING: No team_CTF_redflag in map" );' in check_block
	assert 'BG_FindItem( "Blue Flag" );' in check_block
	assert 'G_Printf( S_COLOR_YELLOW "WARNING: No team_CTF_blueflag in map" );' in check_block

	assert "cgs.gametype == GT_CTF || cgs.gametype == GT_ATTACK_DEFEND || cgs.gametype == GT_OBELISK" in flag_parse_block
	assert "cgs.redflag = str[0] - '0';" in flag_parse_block
	assert "cgs.blueflag = str[1] - '0';" in flag_parse_block
	assert "CG_ParseFlagStatusConfigString( CG_ConfigString( CS_FLAGSTATUS ) );" in config_values_block
	assert "CG_ParseFlagStatusConfigString( str );" in configstring_block

	assert "if (esi_1 == 5 || esi_1 == 0xb)" in qagame_hlil
	assert "if (DAT_105a898c == 0xb) goto LAB_1004fd7b;" in qagame_decompile
	assert "if ((DAT_105a898c == 5) || (iVar1 = DAT_105a898c, DAT_105a898c == 0xb)) {" in qagame_decompile
	assert 'FUN_10053140("^3WARNING: No team_CTF_redflag in map");' in qagame_decompile
	assert 'FUN_10053140("^3WARNING: No team_CTF_blueflag in map");' in qagame_decompile


def test_ad_round_controller_damage_and_bonus_paths_are_connected() -> None:
	local_h = _source(G_LOCAL)
	team_c = _source(G_TEAM)
	combat_c = _source(G_COMBAT)
	bonus_block = _block(G_TEAM, "void G_ADAwardBonus( gentity_t *player, const vec3_t origin, int bonus, const char *label ) {")
	damage_block = _block(G_TEAM, "qboolean G_ADHandleDamageScore( gentity_t *attacker, int announce, gentity_t *targ, int *take, int *asave ) {")
	exit_block = _block(G_TEAM, "qboolean G_ADCheckExitRules( qboolean announce ) {")
	transition_block = _block(G_TEAM, "int AD_RoundStateTransition( qboolean announce ) {")

	for expected in (
		"AD_ROUNDSTATE_ACTIVE = 3",
		"AD_ROUNDSTATE_COMPLETE = 4",
		"AD_ROUNDSTATE_EXIT = 5",
		"int G_ADResolveRoundState( void );",
		"qboolean G_ADHandleDamageScore( gentity_t *attacker, int announce, gentity_t *targ, int *take, int *asave );",
		"qboolean G_ADCheckExitRules( qboolean announce );",
		"int AD_RoundStateTransition( qboolean announce );",
		"int G_ADResolveAttackingTeam( void );",
		"int G_ADResolveDefendingTeam( void );",
		"void G_CAADRespawnAsSpectator( gentity_t *ent );",
		"void G_CAADResetClientForRound( gentity_t *ent );",
		"adScoreHistory[AD_SCORE_HISTORY_LENGTH];",
		"adPublishedScoreHistory[AD_SCORE_HISTORY_LENGTH];",
		"adAccumulatedDamage;",
	):
		assert expected in local_h

	for expected in (
		"AddScore( player, origin, bonus );",
		"AddTeamScore( origin, player->client->sess.sessionTeam, bonus );",
		"G_ADAnnounceBonus( player, label, bonus );",
	):
		assert expected in bonus_block

	for expected in (
		"if ( G_ADResolveRoundState() != AD_ROUNDSTATE_ACTIVE ) {",
		"attackingTeam = G_ADResolveAttackingTeam();",
		"attacker->client->adAccumulatedDamage += damage;",
		"while ( attacker->client->adAccumulatedDamage >= 100 ) {",
		"attacker->client->adAccumulatedDamage -= 100;",
		"AddScore( attacker, targ->r.currentOrigin, 1 );",
	):
		assert expected in damage_block

	for expected in (
		"if ( level.teamScores[TEAM_RED] == level.teamScores[TEAM_BLUE] ) {",
		"mercyLimitMsec = G_BuildExitRuleLimitMsec( g_mercytime.integer, level.overtimeAccumulatedMsec );",
		'trap_SendServerCommand( -1, "print \\"Red hit the scorelimit.\\n\\"" );',
		'trap_SendServerCommand( -1, "print \\"Blue hit the mercylimit.\\n\\"" );',
	):
		assert expected in exit_block

	for expected in (
		"level.adPendingRoundState = AD_ROUNDSTATE_WARMUP;",
		"level.adRoundState = AD_ROUNDSTATE_ACTIVE;",
		"G_ADReleaseClientForRound( ent );",
		"level.adRoundWinnerAlreadyScored = qfalse;",
		"G_ADUpdateScoreHistory();",
		"G_ADCheckExitRules( qfalse )",
		"level.adPendingRoundState = AD_ROUNDSTATE_EXIT;",
		'G_Printf( "AD_RoundStateTransition: invalid state\\n" );',
	):
		assert expected in transition_block

	assert "G_ADHandleDamageScore( attacker, 0, targ, &take, &asave );" in combat_c
	assert "G_ADAwardBonus( attacker, self->r.currentOrigin, g_adElimScoreBonus.integer, S_COLOR_YELLOW \"Elimination bonus\" );" in combat_c
	assert "G_ADNotifyLastAlivePlayer( self->client->sess.sessionTeam );" in combat_c
	assert "int G_ADResolveRoundState( void ) {" in team_c
	assert "int G_ADResolveAttackingTeam( void ) {" in team_c
	assert "int G_ADResolveDefendingTeam( void ) {" in team_c


def test_ad_match_state_configstrings_follow_retail_compact_payloads() -> None:
	match_state = _source(G_MATCH_STATE)
	qagame_hlil = _source(QAGAME_HLIL)

	for expected in (
		'Q_strncpyz( info, "\\\\time\\\\-1\\\\round\\\\0\\\\turn\\\\0\\\\state\\\\0", MAX_INFO_STRING );',
		"G_SetMatchStateInt( info, MATCH_STATE_KEY_TIME, level.roundTransitionTime );",
		"G_SetMatchStateInt( info, MATCH_STATE_KEY_ROUND, level.roundNumber );",
		"G_SetMatchStateInt( info, MATCH_STATE_KEY_TURN, level.adTurnIndex );",
		"G_SetMatchStateInt( info, MATCH_STATE_KEY_STATE, ROUNDSTATE_WARMUP );",
		"G_SetMatchStateInt( info, MATCH_STATE_KEY_STATE, ROUNDSTATE_ACTIVE );",
		"G_SetMatchStateInt( info, MATCH_STATE_KEY_TURN, G_AttackDefendPublishedTurn() );",
		"&& !G_BuildAttackDefendMatchStateInfo( info )",
		"level.adRoundState == AD_ROUNDSTATE_COMPLETE || level.adRoundState == AD_ROUNDSTATE_EXIT",
		'trap_SetConfigstring( CS_ROUND_START_TIME, va( "%i", -1 ) );',
	):
		assert expected in match_state

	for expected in (
		'10035bec              (*(data_104b13ac + 0x64))(0x295, "\\time\\-1\\round\\0\\turn\\0\\state\\0", edi)',
		'char const data_10082144[0x22] = "\\\\time\\\\%d\\\\round\\\\%d\\\\turn\\\\%d\\\\state\\\\1", 0',
		'10035daa          (*(esi_4 + 0x64))(0x296, sub_10070cb0(&data_1007dd18))',
		'10035dcc              (*(data_104b13ac + 0x64))(0x295, sub_10070cb0("\\turn\\%d\\state\\2"))',
		"100361d8              eax_62 = (*(esi_12 + 0x64))(0x296, sub_10070cb0(&data_1007dd18))",
	):
		assert expected in qagame_hlil


def test_ad_objective_touch_spawn_and_frame_wiring_match_retail_surface() -> None:
	frag_block = _block(G_TEAM, "void Team_FragBonuses(gentity_t *targ, gentity_t *inflictor, gentity_t *attacker)")
	our_flag_block = _block(G_TEAM, "int Team_TouchOurFlag( gentity_t *ent, gentity_t *other, int team ) {")
	enemy_flag_block = _block(G_TEAM, "int Team_TouchEnemyFlag( gentity_t *ent, gentity_t *other, int team ) {")
	spawn_select_block = _block(G_CLIENT, "static qboolean G_GametypeUsesTeamSpawnSelection( int gametype ) {")
	client_respawn_block = _block(G_CLIENT, "void respawn( gentity_t *ent ) {")
	client_begin_block = _block(G_CLIENT, "void ClientBegin( int clientNum ) {")
	active_frame_block = _block(G_ACTIVE, "void G_Frame_UpdateRoundController( void ) {")
	runframe_hooks_block = _block(G_MAIN, "static void G_RunFrameGametypeHooks( void ) {")

	assert "if ( g_gametype.integer == GT_ATTACK_DEFEND ) {" in frag_block
	assert "adDefendingTeam = G_ADResolveDefendingTeam();" in frag_block
	assert "attacker->client->sess.sessionTeam != adDefendingTeam" in frag_block

	for expected in (
		"if ( G_ADResolveRoundState() != AD_ROUNDSTATE_ACTIVE ) {",
		"attackingTeam = G_ADResolveAttackingTeam();",
		"G_ADAwardBonus( other, ent->r.currentOrigin, g_adCaptureScoreBonus.integer, S_COLOR_GREEN \"Capture bonus\" );",
		"level.adRoundWinner = other->client->sess.sessionTeam;",
		"level.adRoundWinnerAlreadyScored = qtrue;",
		"level.adRoundState = AD_ROUNDSTATE_COMPLETE;",
		"AD_RoundStateTransition( qtrue );",
	):
		assert expected in our_flag_block

	for expected in (
		"if ( G_ADResolveRoundState() != AD_ROUNDSTATE_ACTIVE ) {",
		"if ( cl->sess.sessionTeam != G_ADResolveAttackingTeam() ) {",
		"Team_SetFlagStatus( statusTeam, status );",
		"G_ADAwardBonus( other, ent->r.currentOrigin, g_adTouchScoreBonus.integer, S_COLOR_CYAN \"Touch bonus\" );",
	):
		assert expected in enemy_flag_block

	assert "case GT_ATTACK_DEFEND:" in spawn_select_block
	assert "return qtrue;" in spawn_select_block
	assert "return SelectCTFSpawnPoint( client->sess.sessionTeam, client->pers.teamState.state, origin, angles );" in _source(G_CLIENT)
	assert "G_CAADResetClientForRound( ent );" in client_respawn_block
	assert "G_CAADResetClientForRound( ent );" in client_begin_block
	assert "G_Frame_UpdateAttackDefendRoundController();" in active_frame_block
	assert "level.adRoundState == AD_ROUNDSTATE_EXIT" in runframe_hooks_block
	assert "G_Frame_UpdateRoundController();" in runframe_hooks_block
	assert '[GT_ATTACK_DEFEND] = { "attackdefend", "ad", NULL }' in _source(G_SPAWN)
	assert '{ "ad", GT_ATTACK_DEFEND }' in _source(G_FACTORY)


def test_ad_scores_hud_poi_and_media_wiring_match_retail_surface() -> None:
	score_publish_block = _block(G_TEAM, "static void G_ADPublishScoreHistory( void ) {")
	score_parse_block = _block(CG_SERVERCMDS, "static qboolean CG_ParseADScoreHistory( void ) {")
	ad_scores_block = _block(CG_SERVERCMDS, "static void CG_ParseADScores( void ) {")
	status_text_block = _block(CG_DRAW, "static const char *CG_ADRoundScoreboardStatusText( void ) {")
	round_scoreboard_block = _block(CG_DRAW, "static void CG_DrawADRoundScoreboard( void ) {")
	warmup_status_block = _block(CG_DRAW, "static void CG_DrawWarmupStatusText( int gametype ) {")
	flag_status_gate_block = _block(CG_MAIN, "static qboolean CG_ShouldRegisterFlagStatusShaders( void ) {")
	register_graphics_block = _block(CG_MAIN, "static void CG_RegisterGraphics( void ) {")
	item_poi_block = _block(CG_ENTS, "static qhandle_t CG_ItemPOITeamShader( const gitem_t *item, vec4_t color ) {")
	player_poi_block = _block(CG_PLAYERS, "static void CG_PlayerObjectiveSprite( centity_t *cent ) {")
	objective_strip_block = _block(CG_NEWDRAW, "static qboolean CG_DrawObjectiveStatusCtfFamilyStrip( rectDef_t *rect ) {")
	match_end_block = _block(CG_NEWDRAW, "static void CG_DrawMatchEndCondition( rectDef_t *rect, float scale, vec4_t color, int textStyle ) {")
	cgame_decompile = _source(CGAME_GHIDRA)

	for expected in (
		'offset = Com_sprintf( command, sizeof( command ), "scores_ad" );',
		"level.adPublishedScoreHistory[i]",
		"level.teamScores[TEAM_RED], level.teamScores[TEAM_BLUE]",
		"trap_SendServerCommand( -1, command );",
	):
		assert expected in score_publish_block

	for expected in (
		"trap_Argc() != ( CG_AD_SCORE_HISTORY_LENGTH + 3 )",
		"cg.adScoreHistory[i] = atoi( CG_Argv( i + 1 ) );",
		"cg.teamScores[0] = atoi( CG_Argv( CG_AD_SCORE_HISTORY_LENGTH + 1 ) );",
		"cg.teamScores[1] = atoi( CG_Argv( CG_AD_SCORE_HISTORY_LENGTH + 2 ) );",
	):
		assert expected in score_parse_block
	assert "if ( CG_ParseADScoreHistory() ) {" in ad_scores_block
	assert "CG_ParseCtfScores();" in ad_scores_block
	assert 'if ( !strcmp( cmd, "scores_ad" ) ) {' in _source(CG_SERVERCMDS)
	assert 'if ( !strcmp( cmd, "adscores" ) ) {' in _source(CG_SERVERCMDS)
	assert 'cmd = "scores_ad";' in _source(G_CMDS)

	for expected in (
		"value = Info_ValueForKey( info, SERVERINFO_KEY_ROUNDLIMIT );",
		'return "Last Chance";',
		'return "Match Point";',
		'return "Red Wins! Good Game";',
	):
		assert expected in status_text_block
	assert "for ( column = 0; column < ( CG_AD_SCORE_HISTORY_LENGTH / 2 ); column++ ) {" in round_scoreboard_block
	assert "cg.adScoreHistory[historyIndex]" in round_scoreboard_block
	assert "CG_ADRoundScoreboardStatusText();" in round_scoreboard_block
	assert "CG_DrawADRoundScoreboard();" in warmup_status_block

	assert "case GT_ATTACK_DEFEND:" in flag_status_gate_block
	assert "cgs.gametype == GT_CTF || cgs.gametype == GT_1FCTF || cgs.gametype == GT_ATTACK_DEFEND || cgs.gametype == GT_HARVESTER" in register_graphics_block
	assert "cgs.gametype == GT_1FCTF || cgs.gametype == GT_ATTACK_DEFEND" in register_graphics_block
	assert "cgs.gametype == GT_CTF || cgs.gametype == GT_1FCTF || cgs.gametype == GT_ATTACK_DEFEND" in register_graphics_block
	assert 'cgs.media.poiAttackShader = trap_R_RegisterShader( "gfx/2d/ad/poi_attack" );' in register_graphics_block
	assert 'cgs.media.poiCaptureShader = trap_R_RegisterShader( "gfx/2d/ad/poi_capture" );' in register_graphics_block
	assert 'cgs.media.poiDefendShader = trap_R_RegisterShader( "gfx/2d/ad/poi_defend" );' in register_graphics_block

	assert "return cgs.media.poiDefendShader;" in item_poi_block
	assert "return cgs.media.poiAttackShader;" in item_poi_block
	assert "return cgs.media.poiCaptureShader;" in item_poi_block
	assert "shader = cgs.media.poiCaptureShader;" in player_poi_block
	assert "VectorCopy( cgs.poiObjectiveOrigins[objectiveIndex], marker->origin );" in player_poi_block
	assert "cgs.gametype != GT_CTF && cgs.gametype != GT_ATTACK_DEFEND && cgs.gametype != GT_OBELISK" in objective_strip_block
	assert "cgs.gametype == GT_DOMINATION || cgs.gametype == GT_ATTACK_DEFEND" in match_end_block

	assert 'DAT_10a5f39c = (**(code **)(DAT_1074cccc + 200))("models/flags/r_flag.md3");' in cgame_decompile
	assert 'DAT_10a5f3a0 = (**(code **)(DAT_1074cccc + 200))("models/flags/b_flag.md3");' in cgame_decompile
	assert "DAT_10a3ff14 == 0xb" in cgame_decompile
	assert 'DAT_10a5f4bc = (**(code **)(DAT_1074cccc + 0xd0))("sprites/flagcarrier");' in cgame_decompile
	assert '"gfx/2d/ad/poi_attack"' in cgame_decompile
	assert '"gfx/2d/ad/poi_capture"' in cgame_decompile
	assert '"gfx/2d/ad/poi_defend"' in cgame_decompile


def test_plan_records_attack_defend_parity_closure() -> None:
	plan = _source(IMPLEMENTATION_PLAN)

	assert "Task A232: Close Attack and Defend retail parity wiring [COMPLETED]" in plan
	assert "Parity estimate: **before 97% -> after 100%** for the focused Attack and" in plan
	assert "Defend gametype rules, flag-status transport, map item validation" in plan
	assert "Team_SetFlagStatus" in plan
	assert "G_CheckTeamItems" in plan
	assert "CG_RegisterGraphics" in plan
