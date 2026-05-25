from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
G_ACTIVE_PATH = REPO_ROOT / "src" / "code" / "game" / "g_active.c"
G_LOCAL_PATH = REPO_ROOT / "src" / "code" / "game" / "g_local.h"
G_MAIN_PATH = REPO_ROOT / "src" / "code" / "game" / "g_main.c"
QAGAME_MAP_PATH = REPO_ROOT / "references" / "symbol-maps" / "qagame.json"
QAGAME_MAPPING_PATH = REPO_ROOT / "docs" / "reverse-engineering" / "qagame-mapping.md"


def _function_body(source: str, signature: str) -> str:
	definition = f"{signature} {{"
	try:
		start = source.index(definition)
	except ValueError:
		start = source.index(signature)
	brace = source.index("{", start)
	depth = 1
	position = brace + 1
	while depth > 0:
		if source[position] == "{":
			depth += 1
		elif source[position] == "}":
			depth -= 1
		position += 1

	return source[brace + 1 : position - 1]


def _block_from_marker(source: str, marker: str) -> str:
	start = source.index(marker)
	brace = source.index("{", start)
	depth = 1
	position = brace + 1
	while depth > 0:
		if source[position] == "{":
			depth += 1
		elif source[position] == "}":
			depth -= 1
		position += 1

	return source[start:position]


def _symbol_comment(normalized_name: str) -> str:
	symbol_map = json.loads(QAGAME_MAP_PATH.read_text(encoding="utf-8"))
	for entry in symbol_map["functions"]:
		if entry["normalized_name"] == normalized_name:
			return entry["comment"]

	raise AssertionError(f"{normalized_name} missing from qagame symbol map")


def test_g_runframe_client_slots_dispatch_clientthink_real_inline_like_retail() -> None:
	g_main = G_MAIN_PATH.read_text(encoding="utf-8")
	g_local = G_LOCAL_PATH.read_text(encoding="utf-8")
	qagame_mapping = QAGAME_MAPPING_PATH.read_text(encoding="utf-8")
	step_body = _function_body(g_main, "static void G_StepEntities( qlr_game_frame_context_t *ctx )")
	client_block = _block_from_marker(step_body, "if ( i < MAX_CLIENTS ) {")

	assert "void ClientThink_real( gentity_t *ent );" in g_local
	assert "G_RunClient( ent );" not in client_block
	assert "G_RunThink( ent );" in client_block
	assert "if ( ent->inuse && ent->client ) {" in client_block
	assert "if ( ( ent->r.svFlags & SVF_BOT ) || g_synchronousClients.integer ) {" in client_block
	assert "ent->client->pers.cmd.serverTime = level.time;" in client_block
	assert "ClientThink_real( ent );" in client_block
	assert client_block.index("G_RunThink( ent );") < client_block.index("ClientThink_real( ent );")
	assert client_block.index("ClientThink_real( ent );") < client_block.index("ctx->hooks.physics_step")
	assert client_block.index("ctx->hooks.physics_step") < client_block.index("ctx->hooks.client_think")
	assert "G_RunFrame` at `0x100594D0` does not appear to call a standalone `G_RunClient` helper" in qagame_mapping
	assert "dispatches `ClientThink_real` directly" in qagame_mapping


def test_clientthink_real_builds_retail_pmove_and_playerstate_pipeline() -> None:
	g_active = G_ACTIVE_PATH.read_text(encoding="utf-8")
	body = _function_body(g_active, "void ClientThink_real( gentity_t *ent )")

	for snippet in (
		"client->ps.forwardmove = ucmd->forwardmove;",
		"client->ps.rightmove = ucmd->rightmove;",
		"client->ps.upmove = ucmd->upmove;",
		"if ( ucmd->serverTime > level.time + 200 ) {",
		"if ( ucmd->serverTime < level.time - 1000 ) {",
		"msec = ucmd->serverTime - client->ps.commandTime;",
		"if ( msec > 200 ) {",
		"if ( pmove_msec.integer < 8 ) {",
		"else if (pmove_msec.integer > 33) {",
		"ucmd->serverTime = ((ucmd->serverTime + pmove_msec.integer-1) / pmove_msec.integer) * pmove_msec.integer;",
	):
		assert snippet in body

	scoreboard_block = _block_from_marker(body, "if ( client->sess.spectatorState == SPECTATOR_SCOREBOARD ) {")
	assert "client->ps.pm_flags |= PMF_NO_MOVE;" in scoreboard_block
	assert "SpectatorThink( ent, ucmd );" in scoreboard_block
	assert "client->ps.pm_flags &= ~PMF_NO_MOVE;" in scoreboard_block
	assert scoreboard_block.index("client->ps.pm_flags |= PMF_NO_MOVE;") < scoreboard_block.index("SpectatorThink( ent, ucmd );")
	assert scoreboard_block.index("SpectatorThink( ent, ucmd );") < scoreboard_block.index("client->ps.pm_flags &= ~PMF_NO_MOVE;")

	assert body.index("ClientInactivityTimer( client )") < body.index("G_CheckClientFlood( ent )")
	assert body.index("G_CheckClientFlood( ent )") < body.index("if ( client->noclip ) {")
	assert body.index("if ( client->noclip ) {") < body.index("client->ps.gravity = g_gravity.value;")
	assert body.index("client->ps.gravity = g_gravity.value;") < body.index("oldEventSequence = client->ps.eventSequence;")
	assert body.index("oldEventSequence = client->ps.eventSequence;") < body.index("memset (&pm, 0, sizeof(pm));")

	for snippet in (
		"pm.ps = &client->ps;",
		"pm.cmd = *ucmd;",
		"pm.tracemask = MASK_PLAYERSOLID & ~CONTENTS_BODY;",
		"pm.tracemask = MASK_PLAYERSOLID | CONTENTS_BOTCLIP;",
		"pm.tracemask = MASK_PLAYERSOLID;",
		"pm.tracemask &= ~CONTENTS_BODY;",
		"pm.pmoveSettings = &g_pmoveSettings;",
		"pm.trace = trap_Trace;",
		"pm.pointcontents = trap_PointContents;",
		"pm.debugLevel = g_debugMove.integer;",
		"pm.noFootsteps = ( g_dmflags.integer & DF_NO_FOOTSTEPS ) > 0;",
		"pm.pmove_fixed = pmove_fixed.integer | client->pers.pmoveFixed;",
		"pm.pmove_msec = pmove_msec.integer;",
	):
		assert snippet in body

	assert body.index("Pmove (&pm);") < body.index("BG_PlayerStateToEntityState( &ent->client->ps, &ent->s, qtrue );")
	assert body.index("BG_PlayerStateToEntityState( &ent->client->ps, &ent->s, qtrue );") < body.index("SendPendingPredictableEvents( &ent->client->ps );")
	assert body.index("SendPendingPredictableEvents( &ent->client->ps );") < body.index("ClientEvents( ent, oldEventSequence );")
	assert body.index("ClientEvents( ent, oldEventSequence );") < body.index("trap_LinkEntity (ent);")
	assert body.index("trap_LinkEntity (ent);") < body.index("G_TouchTriggers( ent );")
	assert body.index("G_TouchTriggers( ent );") < body.index("ClientImpacts( ent, &pm );")
	assert body.index("ClientImpacts( ent, &pm );") < body.index("ClientTimerActions( ent, msec );")


def test_spectator_impacts_and_predictable_event_sidecars_match_retail_wiring() -> None:
	g_active = G_ACTIVE_PATH.read_text(encoding="utf-8")
	spectator_body = _function_body(g_active, "void SpectatorThink( gentity_t *ent, usercmd_t *ucmd )")
	impacts_body = _function_body(g_active, "void ClientImpacts( gentity_t *ent, pmove_t *pm )")
	triggers_body = _function_body(g_active, "void\tG_TouchTriggers( gentity_t *ent )")
	predictable_body = _function_body(g_active, "void SendPendingPredictableEvents( playerState_t *ps )")

	for snippet in (
		"client->ps.pm_type = PM_SPECTATOR;",
		"client->ps.speed = 400;",
		"pm.ps = &client->ps;",
		"pm.cmd = *ucmd;",
		"pm.tracemask = MASK_PLAYERSOLID & ~CONTENTS_BODY;",
		"pm.pmoveSettings = &g_pmoveSettings;",
		"pm.trace = trap_Trace;",
		"pm.pointcontents = trap_PointContents;",
		"Pmove (&pm);",
		"VectorCopy( client->ps.origin, ent->s.origin );",
		"G_TouchTriggers( ent );",
		"trap_UnlinkEntity( ent );",
		"Cmd_FollowCycle_f( ent, 1 );",
	):
		assert snippet in spectator_body

	assert spectator_body.index("Pmove (&pm);") < spectator_body.index("G_TouchTriggers( ent );")
	assert spectator_body.index("G_TouchTriggers( ent );") < spectator_body.index("trap_UnlinkEntity( ent );")
	assert "( client->buttons & BUTTON_ATTACK ) && ! ( client->oldbuttons & BUTTON_ATTACK )" in spectator_body

	assert "memset( &trace, 0, sizeof( trace ) );" in impacts_body
	assert "for (j=0 ; j<i ; j++) {" in impacts_body
	assert "if (pm->touchents[j] == pm->touchents[i] ) {" in impacts_body
	assert "( ent->r.svFlags & SVF_BOT ) && ( ent->touch )" in impacts_body
	assert "ent->touch( ent, other, &trace );" in impacts_body
	assert "if ( !other->touch ) {" in impacts_body
	assert "other->touch( other, ent, &trace );" in impacts_body
	assert impacts_body.index("if (j != i)") < impacts_body.index("( ent->r.svFlags & SVF_BOT ) && ( ent->touch )")
	assert impacts_body.index("( ent->r.svFlags & SVF_BOT ) && ( ent->touch )") < impacts_body.index("if ( !other->touch )")

	assert "static vec3_t\trange = { 40, 40, 52 };" in triggers_body
	assert "if ( ent->client->ps.stats[STAT_HEALTH] <= 0 ) {" in triggers_body
	assert "if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {" in triggers_body
	assert "hit->touch (hit, ent, &trace);" in triggers_body
	assert "ent->client->ps.jumppad_frame != ent->client->ps.pmove_framecount" in triggers_body
	assert "ent->client->ps.jumppad_ent = 0;" in triggers_body

	assert predictable_body.index("extEvent = ps->externalEvent;") < predictable_body.index("ps->externalEvent = 0;")
	assert predictable_body.index("ps->externalEvent = 0;") < predictable_body.index("BG_PlayerStateToEntityState( ps, &t->s, qtrue );")
	assert "t->s.eType = ET_EVENTS + event;" in predictable_body
	assert "t->s.eFlags |= EF_PLAYER_EVENT;" in predictable_body
	assert "t->s.otherEntityNum = ps->clientNum;" in predictable_body
	assert "t->r.svFlags |= SVF_NOTSINGLECLIENT;" in predictable_body
	assert "t->r.singleClient = ps->clientNum;" in predictable_body
	assert predictable_body.index("t->r.singleClient = ps->clientNum;") < predictable_body.index("ps->externalEvent = extEvent;")


def test_game_active_pmove_wiring_is_backed_by_committed_retail_evidence() -> None:
	qagame_mapping = QAGAME_MAPPING_PATH.read_text(encoding="utf-8")

	assert "Unique touch-entity walker" in _symbol_comment("ClientImpacts")
	assert "dispatches bot self-touch callbacks and touched-entity handlers after pmove" in _symbol_comment("ClientImpacts")
	assert "Spectator pmove path that sets PM_SPECTATOR" in _symbol_comment("SpectatorThink")
	assert "touches triggers afterward, and handles follow cycling" in _symbol_comment("SpectatorThink")
	assert "turns pending playerstate events into temporary ET_EVENTS entities" in _symbol_comment("SendPendingPredictableEvents")
	assert "Main per-command client simulation path covering command-time clamping" in _symbol_comment("ClientThink_real")
	assert "pmove, events, linking, impacts, respawn checks, and once-per-second timers" in _symbol_comment("ClientThink_real")
	assert "`ClientThink_real` is a clean retail boundary at `0x10034C90`" in qagame_mapping
	assert "`G_RunFrame` at `0x100594D0` does not appear to call a standalone `G_RunClient` helper" in qagame_mapping
