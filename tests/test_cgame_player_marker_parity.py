"""Guard retail-backed cgame player overhead marker wiring."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_PLAYERS = REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c"


def _block_from_marker(source: str, marker: str) -> str:
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
				return source[start:index + 1]

	raise AssertionError(f"Unbalanced block for marker: {marker}")


def test_player_overhead_marker_media_matches_retail_registrations() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	local_header = CG_LOCAL.read_text(encoding="utf-8")
	graphics_block = _block_from_marker(main_source, "static void CG_RegisterGraphics( void )")

	for field in (
		"qhandle_t\tfriendShader;",
		"qhandle_t\tfriendHitShader;",
		"qhandle_t\tfriendDeadShader;",
		"qhandle_t\tfrozenPlayerShader;",
		"qhandle_t\tflagCarrierShader;",
		"qhandle_t\tflagCarrierHitShader;",
	):
		assert field in local_header

	for registration in (
		'cgs.media.friendShader = trap_R_RegisterShader( "sprites/friend" );',
		'cgs.media.friendHitShader = trap_R_RegisterShader( "sprites/friend_hit" );',
		'cgs.media.friendDeadShader = trap_R_RegisterShader( "sprites/friend_dead" );',
		'cgs.media.frozenPlayerShader = trap_R_RegisterShader( "sprites/frozen" );',
		'cgs.media.flagCarrierShader = trap_R_RegisterShader( "sprites/flagcarrier" );',
		'cgs.media.flagCarrierHitShader = trap_R_RegisterShader( "sprites/flagcarrier_hit" );',
		'cgs.media.poiNeutralFlagCarrierShader = trap_R_RegisterShader( "sprites/neutralflagcarrier" );',
		'cgs.media.poiInfectedShader = trap_R_RegisterShader( "gfx/2d/infected/bite" );',
		'cgs.media.teamStatusBar = trap_R_RegisterShader( "gfx/2d/colorbar" );',
		'cgs.media.medalDefend = trap_R_RegisterShaderNoMip( "medal_defense" );',
	):
		assert registration in graphics_block

	assert '"sprites/foe"' not in graphics_block
	assert '"medal_defend"' not in graphics_block


def test_player_sprites_use_retail_priority_and_teammate_poi_cvars() -> None:
	source = CG_PLAYERS.read_text(encoding="utf-8")
	marker_gate_block = _block_from_marker(source, "static qboolean CG_ShouldDrawTeamPlayerMarker")
	player_sprites_block = _block_from_marker(source, "static void CG_PlayerSprites")

	assert "if ( !cg_teammatePOIs.integer || cg_teammateNames.integer ) {" in marker_gate_block
	assert "cg_drawFriend" not in player_sprites_block
	assert "clientNum == cg.snap->ps.clientNum && !cg.renderingThirdPerson" in player_sprites_block

	expected_order = [
		"EF_CONNECTION",
		"cgs.gametype == GT_1FCTF && sameTeam",
		"CG_ShouldDrawTeamPlayerMarker( sameTeam ) && CG_PlayerHasFlagPowerup( cent )",
		"cgs.gametype == GT_FREEZE && sameTeam",
		"EF_TALK",
		"EF_AWARD_IMPRESSIVE",
		"EF_AWARD_EXCELLENT",
		"EF_AWARD_GAUNTLET",
		"EF_AWARD_DEFEND",
		"EF_AWARD_ASSIST",
		"EF_AWARD_CAP",
		"CG_ShouldDrawInfectedTargetMarker( ci )",
		"cg_drawHitFriendTime.integer",
	]
	positions = [player_sprites_block.index(token) for token in expected_order]
	assert positions == sorted(positions)

	for expected in (
		"1 << PW_NEUTRALFLAG",
		"CG_PlayerRecentlyHit( cent, 1500 )",
		"cgs.media.flagCarrierHitShader",
		"1 << PW_NUM_POWERUPS",
		"!( cent->currentState.eFlags & EF_DEAD )",
		"!redRoverBlocked",
		"cgs.media.friendHitShader",
		"cgs.media.friendShader",
	):
		assert expected in player_sprites_block


def test_red_rover_infected_marker_wiring_matches_retail_special_case() -> None:
	source = CG_PLAYERS.read_text(encoding="utf-8")
	blocked_block = _block_from_marker(source, "static qboolean CG_PlayerSpriteBlockedByInfectedTarget")
	marker_block = _block_from_marker(source, "static qboolean CG_ShouldDrawInfectedTargetMarker")
	player_sprites_block = _block_from_marker(source, "static void CG_PlayerSprites")

	for expected in (
		"cgs.gametype != GT_RED_ROVER",
		"cgs.customSettingsMask & CUSTOM_SETTING_INFECTED",
		"sameTeam || !ci || ci->team != TEAM_BLUE",
	):
		assert expected in blocked_block

	for expected in (
		"cgs.gametype != GT_RED_ROVER",
		"cgs.customSettingsMask & CUSTOM_SETTING_INFECTED",
		"!ci || ci->team != TEAM_BLUE",
		"CG_PlayerSpriteLocalClientTeam() == TEAM_RED",
	):
		assert expected in marker_block

	assert "CG_PlayerFloatSprite( cent, cgs.media.poiInfectedShader );" in player_sprites_block
