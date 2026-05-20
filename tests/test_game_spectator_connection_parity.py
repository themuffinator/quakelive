from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
G_ACTIVE_PATH = REPO_ROOT / "src" / "code" / "game" / "g_active.c"
G_CLIENT_PATH = REPO_ROOT / "src" / "code" / "game" / "g_client.c"


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


def test_scoreboard_spectator_userinfo_preserves_player_netname() -> None:
	body = _function_body(G_CLIENT_PATH, "ClientUserinfoChanged")
	start = body.index("// set name")
	end = body.index("if ( client->pers.connected == CON_CONNECTED )", start)
	name_block = body[start:end]

	assert "ClientCleanName( s, client->pers.netname, sizeof(client->pers.netname) );" in name_block
	assert "\"scoreboard\"" not in name_block
	assert "SPECTATOR_SCOREBOARD" not in name_block
