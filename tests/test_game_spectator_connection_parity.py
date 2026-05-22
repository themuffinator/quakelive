from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
G_ACTIVE_PATH = REPO_ROOT / "src" / "code" / "game" / "g_active.c"
G_CLIENT_PATH = REPO_ROOT / "src" / "code" / "game" / "g_client.c"
G_CMDS_PATH = REPO_ROOT / "src" / "code" / "game" / "g_cmds.c"


def _function_body(path: Path, signature: str) -> str:
	source = path.read_text(encoding="utf-8")
	match = re.search(
		rf"void {re.escape(signature)}\s*\([^)]*\)\s*\{{(?P<body>.*?)^\}}",
		source,
		re.MULTILINE | re.DOTALL,
	)

	assert match is not None, f"{signature} definition missing"
	return match.group("body")


def test_scoreboard_spectators_consume_usercmd_time_without_moving() -> None:
	source = G_ACTIVE_PATH.read_text(encoding="utf-8")
	marker = "if ( client->sess.spectatorState == SPECTATOR_SCOREBOARD ) {"
	start = source.index(marker)
	end = source.index("\n\t\t}", start)
	scoreboard_block = source[start:end]

	assert "client->ps.pm_flags |= PMF_NO_MOVE;" in scoreboard_block
	assert "SpectatorThink( ent, ucmd );" in scoreboard_block
	assert "client->ps.pm_flags &= ~PMF_NO_MOVE;" in scoreboard_block
	assert scoreboard_block.index("client->ps.pm_flags |= PMF_NO_MOVE;") < scoreboard_block.index("SpectatorThink( ent, ucmd );")
	assert scoreboard_block.index("SpectatorThink( ent, ucmd );") < scoreboard_block.index("client->ps.pm_flags &= ~PMF_NO_MOVE;")
	assert scoreboard_block.index("client->ps.pm_flags &= ~PMF_NO_MOVE;") < scoreboard_block.index("return;")


def test_client_spawn_seeds_scoreboard_spectator_state_before_first_snapshot() -> None:
	body = _function_body(G_CLIENT_PATH, "ClientSpawn")

	assert "client->ps.persistant[PERS_TEAM] = client->sess.sessionTeam;" in body
	assert "client->ps.pm_type = PM_SPECTATOR;" in body
	assert "client->ps.pm_flags |= PMF_SCOREBOARD;" in body
	assert "client->ps.pm_flags &= ~PMF_SCOREBOARD;" in body
	assert "ent->takedamage = qfalse;" in body
	assert "ent->r.contents = 0;" in body
	assert "ent->clipmask = 0;" in body
	assert body.index("client->ps.persistant[PERS_TEAM] = client->sess.sessionTeam;") < body.index("client->ps.pm_type = PM_SPECTATOR;")
	assert body.index("client->ps.pm_type = PM_SPECTATOR;") < body.index("G_FreezeInitClient( ent );")
	assert body.index("ent->r.contents = CONTENTS_BODY;") < body.index("ent->r.contents = 0;")


def test_scoreboard_spectator_userinfo_preserves_player_netname() -> None:
	body = _function_body(G_CLIENT_PATH, "ClientUserinfoChanged")
	start = body.index("// set name")
	end = body.index("if ( client->pers.connected == CON_CONNECTED )", start)
	name_block = body[start:end]

	assert "ClientCleanName( s, client->pers.netname, sizeof(client->pers.netname) );" in name_block
	assert "\"scoreboard\"" not in name_block
	assert "SPECTATOR_SCOREBOARD" not in name_block


def test_stop_following_restores_session_team_and_self_client_slot() -> None:
	source = G_CMDS_PATH.read_text(encoding="utf-8")
	body = _function_body(G_CMDS_PATH, "StopFollowing")

	assert "spectatorState_t G_DefaultSpectatorState( void )" in source
	assert "return g_teamSpecFreeCam.integer ? SPECTATOR_FREE : SPECTATOR_SCOREBOARD;" in source
	assert "clientNum = ent - g_entities;" in body
	assert "ent->client->ps.persistant[ PERS_TEAM ] = ent->client->sess.sessionTeam;" in body
	assert "ent->client->sess.sessionTeam = TEAM_SPECTATOR" not in body
	assert "ent->client->sess.spectatorState = G_DefaultSpectatorState();" in body
	assert "ent->client->sess.spectatorClient = clientNum;" in body
	assert "ent->client->ps.pm_flags &= ~PMF_FOLLOW;" in body
	assert "ent->client->ps.pm_flags |= PMF_SCOREBOARD;" in body
	assert "ent->client->ps.clientNum = clientNum;" in body


def test_follow_command_accepts_retail_shortcuts_and_powerup_suffix() -> None:
	body = _function_body(G_CMDS_PATH, "Cmd_Follow_f")

	assert "argc = trap_Argc();" in body
	assert "if ( argc < 2 ) {" in body
	assert "trap_Argc() != 2" not in body
	assert 'if ( !Q_stricmp( arg, "follow1" ) ) {' in body
	assert "i = FOLLOW_ACTIVE1;" in body
	assert '} else if ( !Q_stricmp( arg, "follow2" ) ) {' in body
	assert "i = FOLLOW_ACTIVE2;" in body
	assert body.index('if ( !Q_stricmp( arg, "follow1" ) ) {') < body.index("ClientNumberFromString( ent, arg )")
	assert "Free-flying spectators are disabled while g_teamSpecFreeCam is 0." in body


def test_spectator_end_frame_drops_missing_follow_targets_through_stop_following() -> None:
	body = _function_body(G_ACTIVE_PATH, "SpectatorClientEndFrame")

	assert "if ( clientNum == -1 ) {" in body
	assert "clientNum = level.follow1;" in body
	assert "clientNum = level.follow2;" in body
	assert "if ( clientNum < 0 && clientNum > -10 ) {" in body
	assert "StopFollowing( ent );" in body
	assert "ent->client->sess.spectatorClient = -1;" not in body
	assert "ClientBegin( ent->client - level.clients );" not in body
