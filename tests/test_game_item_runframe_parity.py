from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_launchitem_assigns_retail_dropped_powerup_runframe() -> None:
	items_c = _read("src/code/game/g_items.c")

	assert "static void G_DroppedPowerupRunFrame( gentity_t *ent, float thinktime )" in items_c
	assert "static int G_DroppedPowerupTouchCaptureZone( gentity_t *trigger, gentity_t *ent )" in items_c
	assert 'if ( !Q_stricmp( trigger->classname, "trigger_push" ) ) {' in items_c
	assert 'if ( !Q_stricmp( trigger->classname, "trigger_teleport" ) ) {' in items_c
	assert 'if ( !Q_stricmp( trigger->classname, "trigger_capturezone" ) ) {' in items_c
	assert 'te->s.eventParm = G_SoundIndex( "sound/world/jumppad.wav" );' in items_c
	assert 'te->s.eventParm = G_SoundIndex( "sound/world/teleout.ogg" );' in items_c
	assert 'te->s.eventParm = G_SoundIndex( "sound/world/telein.ogg" );' in items_c
	assert "dropped->runFrame = G_DroppedPowerupRunFrame;" in items_c


def test_dropped_powerup_capturezone_bridge_routes_to_flag_capture_path() -> None:
	items_c = _read("src/code/game/g_items.c")
	team_h = _read("src/code/game/g_team.h")
	start = items_c.index("static int G_DroppedPowerupTouchCaptureZone")
	end = items_c.index("/*\n=================\nG_DroppedPowerupRunFrame", start)
	body = items_c[start:end]

	assert 'trigger->team, "red"' in body
	assert 'flagClassname = "team_CTF_redflag";' in body
	assert "team = TEAM_RED;" in body
	assert 'trigger->team, "blue"' in body
	assert 'flagClassname = "team_CTF_blueflag";' in body
	assert "team = TEAM_BLUE;" in body
	assert "if ( !other->client && other->parent && other->parent->client )" in body
	assert "other = other->parent;" in body
	assert "flag = G_Find( flag, FOFS( classname ), flagClassname )" in body
	assert "flag->flags & FL_DROPPED_ITEM" in body
	assert "return Team_TouchOurFlag( flag, other, team );" in body
	assert "int Team_TouchOurFlag( gentity_t *ent, gentity_t *other, int team );" in team_h


def test_g_runitem_uses_retail_think_before_move_order() -> None:
	items_c = _read("src/code/game/g_items.c")
	start = items_c.index("void G_RunItem( gentity_t *ent ) {")
	end = items_c.index("G_BounceItem( ent, &tr );", start)
	run_item = items_c[start:end]

	assert run_item.index("G_RunThink( ent );") < run_item.index("if ( ent->s.pos.trType == TR_STATIONARY ) {")
	assert run_item.index("if ( ent->s.pos.trType == TR_STATIONARY ) {") < run_item.index("BG_EvaluateTrajectory( &ent->s.pos, level.time, origin );")
	assert run_item.count("G_RunThink( ent );") == 1
