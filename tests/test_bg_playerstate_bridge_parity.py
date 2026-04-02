from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BG_MISC = REPO_ROOT / "src" / "code" / "game" / "bg_misc.c"
BG_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "bg_public.h"
G_ACTIVE = REPO_ROOT / "src" / "code" / "game" / "g_active.c"
G_LOCAL = REPO_ROOT / "src" / "code" / "game" / "g_local.h"
G_MAIN = REPO_ROOT / "src" / "code" / "game" / "g_main.c"


def _function_body(path: Path, pattern: str) -> str:
	source = path.read_text(encoding="utf-8")
	match = re.search(
		pattern,
		source,
		re.MULTILINE | re.DOTALL,
	)
	assert match is not None, f"Function definition missing from {path.name}"
	return match.group("body")


def test_playerstate_bridge_surface_matches_retail_helper_inventory() -> None:
	public_source = BG_PUBLIC.read_text(encoding="utf-8")
	bg_misc_source = BG_MISC.read_text(encoding="utf-8")

	assert "void\tBG_PlayerStateToEntityState( playerState_t *ps, entityState_t *s, qboolean snap );" in public_source
	assert "BG_PlayerStateToEntityStateExtraPolate" not in public_source
	assert "void BG_PlayerStateToEntityState( playerState_t *ps, entityState_t *s, qboolean snap ) {" in bg_misc_source
	assert "BG_PlayerStateToEntityStateExtraPolate" not in bg_misc_source


def test_playerstate_bridge_body_stays_on_the_interpolating_retail_path() -> None:
	body = _function_body(
		BG_MISC,
		r"void BG_PlayerStateToEntityState\( playerState_t \*ps, entityState_t \*s, qboolean snap \)\s*\{(?P<body>.*?)^\}",
	)

	assert "s->pos.trType = TR_INTERPOLATE;" in body
	assert "VectorCopy( ps->velocity, s->pos.trDelta );" in body
	assert "s->apos.trType = TR_INTERPOLATE;" in body
	assert "s->powerups |= 1 << i;" in body
	assert "TR_LINEAR_STOP" not in body
	assert "s->pos.trTime = time;" not in body
	assert "s->pos.trDuration = 50;" not in body


def test_qagame_call_sites_route_directly_through_bg_playerstate_bridge() -> None:
	source = G_ACTIVE.read_text(encoding="utf-8")

	assert "BG_PlayerStateToEntityStateExtraPolate" not in source
	assert "g_smoothClients" not in source
	assert source.count("BG_PlayerStateToEntityState( &ent->client->ps, &ent->s, qtrue );") == 2


def test_qagame_no_longer_registers_the_source_only_smooth_clients_cvar() -> None:
	assert "g_smoothClients" not in G_LOCAL.read_text(encoding="utf-8")
	assert "g_smoothClients" not in G_MAIN.read_text(encoding="utf-8")
