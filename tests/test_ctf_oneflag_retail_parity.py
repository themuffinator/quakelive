"""Retail parity guards for CTF and One Flag gametype wiring."""

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
G_TEAM = REPO_ROOT / "src" / "code" / "game" / "g_team.c"
G_COMBAT = REPO_ROOT / "src" / "code" / "game" / "g_combat.c"
G_MAIN = REPO_ROOT / "src" / "code" / "game" / "g_main.c"
G_CMDS = REPO_ROOT / "src" / "code" / "game" / "g_cmds.c"
AI_DMQ3 = REPO_ROOT / "src" / "code" / "game" / "ai_dmq3.c"
AI_TEAM = REPO_ROOT / "src" / "code" / "game" / "ai_team.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"


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


def _source(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _block(path: Path, marker: str) -> str:
	return _extract_block(_source(path), marker)


def _symbol_names(path: Path) -> set[str]:
	payload = json.loads(path.read_text(encoding="utf-8"))
	return {entry["normalized_name"] for entry in payload["functions"]}


def test_retail_symbol_maps_cover_ctf_and_oneflag_owner_functions() -> None:
	qagame_names = _symbol_names(QAGAME_SYMBOLS)
	cgame_names = _symbol_names(CGAME_SYMBOLS)

	for name in (
		"Team_SetFlagStatus",
		"Team_CheckDroppedItem",
		"Team_ReturnFlagIfMissing",
		"Team_FragBonuses",
		"Team_CheckHurtCarrier",
		"Team_TouchOurFlag",
		"Team_TouchEnemyFlag",
		"Pickup_Team",
		"CheckAlmostCapture",
	):
		assert name in qagame_names

	for name in (
		"CG_TeamBase",
		"CG_DrawObjectiveStatus",
		"CG_DrawTeamFlagOrBaseStatus",
		"CG_OneFlagStatus",
		"CG_OtherTeamHasFlag",
		"CG_YourTeamHasFlag",
		"CG_DrawPlayerHasFlag",
		"CG_ParseCtfScores",
		"CG_ParseCTFStats",
	):
		assert name in cgame_names


def test_team_init_and_flag_configstrings_keep_ctf_and_oneflag_split() -> None:
	source = _source(G_TEAM)
	init_block = _block(G_TEAM, "void Team_InitGame( void ) {")
	status_block = _block(G_TEAM, "void Team_SetFlagStatus( int team, flagStatus_t status ) {")
	dropped_block = _block(G_TEAM, "void Team_CheckDroppedItem( gentity_t *dropped ) {")
	reset_block = _block(G_TEAM, "void Team_ResetFlags( void ) {")
	config_values_block = _block(CG_SERVERCMDS, "void CG_SetConfigValues( void ) {")
	configstring_block = _block(CG_SERVERCMDS, "static void CG_ConfigStringModified( void ) {")

	assert "static char ctfFlagStatusRemap[] = { '0', '1', '*', '*', '2' };" in source
	assert "static char oneFlagStatusRemap[] = { '0', '1', '2', '3', '4' };" in source

	for expected in (
		"case GT_CTF:",
		"teamgame.redStatus = teamgame.blueStatus = -1;",
		"Team_SetFlagStatus( TEAM_RED, FLAG_ATBASE );",
		"Team_SetFlagStatus( TEAM_BLUE, FLAG_ATBASE );",
		"case GT_1FCTF:",
		"teamgame.flagStatus = -1;",
		"Team_SetFlagStatus( TEAM_FREE, FLAG_ATBASE );",
	):
		assert expected in init_block

	for expected in (
		"st[0] = ctfFlagStatusRemap[teamgame.redStatus];",
		"st[1] = ctfFlagStatusRemap[teamgame.blueStatus];",
		"st[0] = oneFlagStatusRemap[teamgame.flagStatus];",
		"trap_SetConfigstring( CS_FLAGSTATUS, st );",
		"G_RankSendFlagStatus( NULL, team, status );",
	):
		assert expected in status_block
	assert status_block.index("g_gametype.integer == GT_CTF") < status_block.index(
		"st[0] = oneFlagStatusRemap[teamgame.flagStatus];"
	)

	for expected in (
		"Team_SetFlagStatus( TEAM_RED, FLAG_DROPPED );",
		"Team_SetFlagStatus( TEAM_BLUE, FLAG_DROPPED );",
		"Team_SetFlagStatus( TEAM_FREE, FLAG_DROPPED );",
	):
		assert expected in dropped_block

	assert "if( g_gametype.integer == GT_CTF ) {" in reset_block
	assert "Team_ResetFlag( TEAM_RED );" in reset_block
	assert "Team_ResetFlag( TEAM_BLUE );" in reset_block
	assert "else if( g_gametype.integer == GT_1FCTF ) {" in reset_block
	assert "Team_ResetFlag( TEAM_FREE );" in reset_block

	for block in (config_values_block, configstring_block):
		assert "cgs.gametype == GT_CTF || cgs.gametype == GT_ATTACK_DEFEND || cgs.gametype == GT_OBELISK" in block
		assert "cgs.redflag = s[0] - '0';" in block or "cgs.redflag = str[0] - '0';" in block
		assert "cgs.blueflag = s[1] - '0';" in block or "cgs.blueflag = str[1] - '0';" in block
		assert "else if( cgs.gametype == GT_1FCTF )" in block
		assert "cgs.flagStatus = s[0] - '0';" in block or "cgs.flagStatus = str[0] - '0';" in block


def test_qagame_flag_touch_capture_and_bonus_paths_keep_oneflag_neutral_semantics() -> None:
	pickup_block = _block(G_TEAM, "int Pickup_Team( gentity_t *ent, gentity_t *other ) {")
	our_flag_block = _block(G_TEAM, "int Team_TouchOurFlag( gentity_t *ent, gentity_t *other, int team ) {")
	enemy_flag_block = _block(G_TEAM, "int Team_TouchEnemyFlag( gentity_t *ent, gentity_t *other, int team ) {")
	status_team_block = _block(G_TEAM, "static team_t Team_FlagPickupStatusTeam( int gametype, team_t team ) {")
	status_value_block = _block(G_TEAM, "static flagStatus_t Team_FlagPickupStatusValue( int gametype, team_t playerTeam ) {")
	frag_block = _block(G_TEAM, "void Team_FragBonuses(gentity_t *targ, gentity_t *inflictor, gentity_t *attacker)")
	hurt_block = _block(G_TEAM, "void Team_CheckHurtCarrier(gentity_t *targ, gentity_t *attacker)")

	for expected in (
		'strcmp(ent->classname, "team_CTF_redflag") == 0',
		'strcmp(ent->classname, "team_CTF_blueflag") == 0',
		'strcmp(ent->classname, "team_CTF_neutralflag") == 0',
		"if( g_gametype.integer == GT_1FCTF ) {",
		"return Team_TouchEnemyFlag( ent, other, cl->sess.sessionTeam );",
		"return Team_TouchOurFlag( ent, other, cl->sess.sessionTeam );",
	):
		assert expected in pickup_block

	assert "return ( gametype == GT_1FCTF ) ? TEAM_FREE : team;" in status_team_block
	assert "return ( playerTeam == TEAM_RED ) ? FLAG_TAKEN_RED : FLAG_TAKEN_BLUE;" in status_value_block
	assert "return FLAG_TAKEN;" in status_value_block

	for expected in (
		"enemy_flag = PW_NEUTRALFLAG;",
		'PrintMsg( NULL, "%s%s TEAM^3 CAPTURED the flag!^7 (%s captured in %d:%.03f)\\n"',
		"cl->ps.powerups[enemy_flag] = 0;",
		"AddTeamScore(ent->s.pos.trBase, other->client->sess.sessionTeam, 1);",
		"other->client->pers.teamState.captures++;",
		"G_RankSendPlayerMedal( other, \"CAPTURES\" );",
		"Team_CaptureFlagSound( ent, team );",
		"Team_ResetFlags();",
	):
		assert expected in our_flag_block

	for expected in (
		"Team_AnnounceNeutralFlagEvent( NEUTRAL_FLAG_EVENT_PICKUP, other );",
		"cl->ps.powerups[PW_NEUTRALFLAG] = INT_MAX;",
		"Team_SetFlagStatus( statusTeam, status );",
		"AddScore(other, ent->r.currentOrigin, CTF_FLAG_BONUS);",
		"Team_TakeFlagSound( ent, team, other->s.number );",
	):
		assert expected in enemy_flag_block

	assert "if (g_gametype.integer == GT_1FCTF) {" in frag_block
	assert "enemy_flag_pw = PW_NEUTRALFLAG;" in frag_block
	assert "targ->client->ps.powerups[enemy_flag_pw]" in frag_block
	assert "attacker->client->pers.teamState.lastfraggedcarrier = level.time;" in frag_block
	assert "AddScore(attacker, targ->r.currentOrigin, CTF_FRAG_CARRIER_BONUS);" in frag_block

	assert "PW_BLUEFLAG" in hurt_block
	assert "PW_REDFLAG" in hurt_block
	assert "PW_NEUTRALFLAG" not in hurt_block
	assert "targ->client->ps.generic1" in hurt_block
	assert "attacker->client->pers.teamState.lasthurtcarrier = level.time;" in hurt_block


def test_check_almost_capture_matches_retail_ctf_and_oneflag_base_selection() -> None:
	source_block = _block(G_COMBAT, "void CheckAlmostCapture( gentity_t *self, gentity_t *attacker ) {")
	hlil_source = _source(QAGAME_HLIL)

	assert "if ( BG_PlayerCarryingFlag( &self->client->ps ) ) {" in source_block
	assert "if ( g_gametype.integer == GT_CTF ) {" in source_block
	assert 'classname = "team_CTF_blueflag";' in source_block
	assert 'classname = "team_CTF_redflag";' in source_block
	assert source_block.index("if ( g_gametype.integer == GT_CTF ) {") < source_block.index("else {")
	assert "VectorLength(dir) < 200" in source_block
	assert "PLAYEREVENT_HOLYSHIT" in source_block

	for expected in (
		"if (ecx_1 == 5 || ecx_1 == 0xb)",
		'esi_1 = "team_CTF_blueflag"',
		'esi_1 = "team_CTF_redflag"',
		"200.0",
	):
		assert expected in hlil_source


def test_ctf_and_oneflag_server_scoreboard_transports_share_retail_ctf_family_path() -> None:
	game_cmds = _source(G_CMDS)
	cgame_cmds = _source(CG_SERVERCMDS)
	ctf_parse_block = _block(CG_SERVERCMDS, "static void CG_ParseCtfScores( void ) {")
	ctf_stats_block = _block(CG_SERVERCMDS, "static void CG_ParseCTFStats( void ) {")
	team_list_block = _block(CG_MAIN, "static const char *CG_FeederItemTextCTFFamilyTeamList")
	stats_feeder_block = _block(CG_MAIN, "static const char *CG_FeederItemTextCTFFamilyStats")

	for expected in (
		"case GT_CTF:",
		"case GT_1FCTF:",
		"cmd = \"scores_ctf\";",
		"if ( G_IsCTFStyleScoreboardGametype() ) {",
		"G_SendCTFStatsMessage( ent );",
		'trap_SendServerCommand( ent - g_entities, va( "ctfstats %i%s", i, payload ) );',
	):
		assert expected in game_cmds

	for expected in (
		'if ( !strcmp( cmd, "scores_ctf" ) ) {',
		"CG_ParseCtfScores();",
		'if ( !strcmp( cmd, "ctfstats" ) ) {',
		"CG_ParseCTFStats();",
	):
		assert expected in cgame_cmds

	for expected in (
		"trap_Argc() < 38",
		"CG_ParseRetailTeamScoreHeader( 1, cgRetailCtfTeamStatOrder, CG_RETAIL_CTF_TEAMSTAT_COUNT );",
		"cg.numScores = atoi( CG_Argv( 35 ) );",
		"cg.teamScores[0] = atoi( CG_Argv( 36 ) );",
		"cg.teamScores[1] = atoi( CG_Argv( 37 ) );",
		"CG_ParseRetailCtfScoreRows( 38 );",
	):
		assert expected in ctf_parse_block

	assert "argc < ( 2 + CG_CTFSTAT_FIELD_COUNT )" in ctf_stats_block
	assert "row = &cg.ctfStats[rowIndex];" in ctf_stats_block
	assert "row->values[fieldIndex] = atoi( CG_Argv( arg++ ) );" in ctf_stats_block
	assert "row->valid = qtrue;" in ctf_stats_block

	for expected in (
		"row.scoreRow->captures",
		"row.scoreRow->assistCount",
		"row.scoreRow->defendCount",
		"row.scoreRow->accuracy",
	):
		assert expected in team_list_block

	assert "stats = &cg.ctfStats[row.scoreIndex];" in stats_feeder_block
	assert "if ( !stats->valid ) {" in stats_feeder_block
	assert "net = row.scoreRow->kills - row.scoreRow->deaths - stats->values[11];" in stats_feeder_block


def test_cgame_flag_objective_and_visibility_wiring_keeps_oneflag_statuses_distinct() -> None:
	team_shader_block = _block(CG_NEWDRAW, "static qhandle_t CG_GetTeamFlagStatusShader( team_t team, qboolean baseStatus ) {")
	one_flag_icon_block = _block(CG_NEWDRAW, "static qhandle_t CG_GetOneFlagStatusShader( void ) {")
	one_flag_status_block = _block(CG_NEWDRAW, "static void CG_OneFlagStatus(rectDef_t *rect) {")
	one_flag_strip_block = _block(CG_NEWDRAW, "static qboolean CG_DrawObjectiveStatusOneFlagStrip( rectDef_t *rect ) {")
	objective_label_block = _block(CG_NEWDRAW, "static qboolean CG_BuildObjectiveStatusLabel( char *buffer, size_t bufferSize ) {")
	other_team_block = _block(CG_NEWDRAW, "qboolean CG_OtherTeamHasFlag( void ) {")
	your_team_block = _block(CG_NEWDRAW, "qboolean CG_YourTeamHasFlag( void ) {")
	blue_has_red_block = _block(CG_NEWDRAW, "static qboolean CG_ShowBlueTeamHasRedFlag( void ) {")
	red_has_blue_block = _block(CG_NEWDRAW, "static qboolean CG_ShowRedTeamHasBlueFlag( void ) {")
	draw_player_block = _block(CG_NEWDRAW, "static void CG_DrawPlayerHasFlag(rectDef_t *rect, qboolean force2D) {")
	ownerdraw_block = _block(CG_NEWDRAW, "void CG_OwnerDraw(")

	for expected in (
		"if ( cgs.gametype == GT_1FCTF ) {",
		"team == TEAM_RED && cgs.flagStatus == FLAG_TAKEN_RED",
		"team == TEAM_BLUE && cgs.flagStatus == FLAG_TAKEN_BLUE",
		"return cgs.media.flagShader[3];",
	):
		assert expected in team_shader_block

	for expected in (
		"case FLAG_TAKEN_RED:",
		"shaderIndex = 1;",
		"case FLAG_TAKEN_BLUE:",
		"shaderIndex = 2;",
		"case FLAG_DROPPED:",
		"shaderIndex = 3;",
	):
		assert expected in one_flag_icon_block

	for expected in (
		"if (cgs.gametype != GT_1FCTF)",
		"cgs.media.poiFlagAtBaseNeutralShader",
		"cgs.media.poiFlagTakenNeutralShader",
		"cgs.media.poiFlagDroppedNeutralShader",
		"cgs.media.poiFlagStolenNeutralShader",
	):
		assert expected in one_flag_status_block

	for expected in (
		"if ( cgs.gametype != GT_1FCTF ) {",
		"flagShader = CG_GetOneFlagStatusShader();",
		"redBaseShader = CG_GetTeamFlagStatusShader( TEAM_RED, qtrue );",
		"blueBaseShader = CG_GetTeamFlagStatusShader( TEAM_BLUE, qtrue );",
		"CG_DrawObjectiveStatusTrack( rect, leftIconX + iconSize + 6.0f, rightIconX - 6.0f );",
	):
		assert expected in one_flag_strip_block

	for expected in (
		"if ( cgs.gametype == GT_CTF ) {",
		"Both Flags Taken",
		"if ( cgs.gametype == GT_1FCTF ) {",
		"case FLAG_TAKEN_RED:",
		"case FLAG_TAKEN_BLUE:",
		"Neutral Flag Dropped",
		"Neutral Flag At Base",
	):
		assert expected in objective_label_block

	assert "team == TEAM_RED && cgs.flagStatus == FLAG_TAKEN_BLUE" in other_team_block
	assert "team == TEAM_BLUE && cgs.flagStatus == FLAG_TAKEN_RED" in other_team_block
	assert "team == TEAM_RED && cgs.flagStatus == FLAG_TAKEN_RED" in your_team_block
	assert "team == TEAM_BLUE && cgs.flagStatus == FLAG_TAKEN_BLUE" in your_team_block
	assert "return ( cgs.flagStatus == FLAG_TAKEN_BLUE ) ? qtrue : qfalse;" in blue_has_red_block
	assert "return ( cgs.flagStatus == FLAG_TAKEN_RED ) ? qtrue : qfalse;" in red_has_blue_block

	assert "cg.predictedPlayerState.powerups[PW_REDFLAG]" in draw_player_block
	assert "cg.predictedPlayerState.powerups[PW_BLUEFLAG]" in draw_player_block
	assert "cg.predictedPlayerState.powerups[PW_NEUTRALFLAG]" in draw_player_block
	assert "flagTeam = TEAM_FREE;" in draw_player_block
	assert "flagTeam == TEAM_FREE && cgs.gametype == GT_1FCTF" in draw_player_block

	assert "case CG_CTF_POWERUP:" in ownerdraw_block
	assert "case CG_PLAYER_HASFLAG:" in ownerdraw_block
	assert "case CG_PLAYER_HASFLAG2D:" in ownerdraw_block


def test_bot_ctf_and_oneflag_goal_state_wiring_tracks_neutral_flag_separately() -> None:
	ai_dmq3 = _source(AI_DMQ3)
	ai_team = _source(AI_TEAM)
	ctf_carry_block = _block(AI_DMQ3, "int BotCTFCarryingFlag(bot_state_t *bs) {")
	oneflag_carry_block = _block(AI_DMQ3, "int Bot1FCTFCarryingFlag(bot_state_t *bs) {")
	oneflag_orders_block = _block(AI_TEAM, "void Bot1FCTFOrders(bot_state_t *bs) {")
	team_ai_block = _block(AI_TEAM, "void BotTeamAI(bot_state_t *bs) {")

	assert "if (gametype != GT_CTF && gametype != GT_ATTACK_DEFEND) return CTF_FLAG_NONE;" in ctf_carry_block
	assert "INVENTORY_REDFLAG" in ctf_carry_block
	assert "INVENTORY_BLUEFLAG" in ctf_carry_block
	assert "INVENTORY_NEUTRALFLAG" not in ctf_carry_block

	assert "if (gametype != GT_1FCTF) return qfalse;" in oneflag_carry_block
	assert "INVENTORY_NEUTRALFLAG" in oneflag_carry_block
	assert "INVENTORY_REDFLAG" not in oneflag_carry_block
	assert "INVENTORY_BLUEFLAG" not in oneflag_carry_block

	for expected in (
		"bs->inventory[INVENTORY_REDFLAG] = bs->cur_ps.powerups[PW_REDFLAG] != 0;",
		"bs->inventory[INVENTORY_BLUEFLAG] = bs->cur_ps.powerups[PW_BLUEFLAG] != 0;",
		"bs->inventory[INVENTORY_NEUTRALFLAG] = bs->cur_ps.powerups[PW_NEUTRALFLAG] != 0;",
		"if ( entinfo.powerups & ( 1 << PW_NEUTRALFLAG ) )",
		"bs->neutralflagstatus = 3;",
		"if (gametype == GT_CTF)",
		"else if (gametype == GT_1FCTF)",
		"BotAI_Print(PRT_WARNING, \"One Flag CTF without Neutral Flag\\n\");",
	):
		assert expected in ai_dmq3

	for expected in (
		"case 0: Bot1FCTFOrders_FlagAtCenter(bs); break;",
		"case 1: Bot1FCTFOrders_TeamHasFlag(bs); break;",
		"case 2: Bot1FCTFOrders_EnemyHasFlag(bs); break;",
		"case 3: Bot1FCTFOrders_EnemyDroppedFlag(bs); break;",
	):
		assert expected in oneflag_orders_block

	assert "case GT_CTF:" in team_ai_block
	assert "BotCTFOrders(bs);" in team_ai_block
	assert "case GT_1FCTF:" in team_ai_block
	assert "Bot1FCTFOrders(bs);" in team_ai_block
