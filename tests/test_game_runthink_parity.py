from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_runthink_services_retail_runframe_callback() -> None:
	local_h = _read("src/code/game/g_local.h")
	main_c = _read("src/code/game/g_main.c")
	game_types_h = _read("src/game/ql_game_types.h")

	assert "(*runFrame)(gentity_t *self, float thinktime)" in local_h
	assert "if ( ent->runFrame ) {" in main_c
	assert "ent->runFrame( ent, thinktime );" in main_c
	assert "QL_GENTITY_OFFSET_RUNFRAME = 0x2FC" in game_types_h
	assert "ql_gentity_runframe_fn runFrame; // 0x2FC" in game_types_h
	assert 'QL_STATIC_ASSERT(offsetof(ql_gentity_t, runFrame) == 0x2FC, "gentity_t.runFrame offset");' in game_types_h


def test_trigger_push_uses_runframe_aim_refresh() -> None:
	trigger_c = _read("src/code/game/g_trigger.c")
	start = trigger_c.index("void SP_trigger_push")
	end = trigger_c.index("/*\n=============\ntrigger_capturezone_link", start)
	spawn_body = trigger_c[start:end]
	touch_start = trigger_c.index("static void trigger_push_touch")
	touch_end = trigger_c.index("/*\n=================\nAimAtTarget", touch_start)
	touch_body = trigger_c[touch_start:touch_end]

	assert "static void AimAtTargetRunFrame( gentity_t *self, float thinktime )" in trigger_c
	assert "self->runFrame = AimAtTargetRunFrame;" in spawn_body
	assert "self->think = AimAtTarget;" not in spawn_body
	assert "if ( other->client->hook )" in touch_body


def test_target_push_matches_retail_velocity_and_sound_path() -> None:
	trigger_c = _read("src/code/game/g_trigger.c")
	start = trigger_c.index("static void Use_target_push")
	end = trigger_c.index("/*QUAKED target_push", start)
	body = trigger_c[start:end]

	assert body.index("if ( !activator->client )") < body.index("if ( activator->client->ps.pm_type != PM_NORMAL )")
	assert body.index("if ( activator->client->ps.pm_type != PM_NORMAL )") < body.index("if ( activator->client->ps.powerups[PW_FLIGHT] )")
	assert body.index("if ( activator->client->ps.powerups[PW_FLIGHT] )") < body.index("if ( activator->client->hook )")
	assert body.index("if ( activator->client->hook )") < body.index("VectorCopy (self->s.origin2, activator->client->ps.velocity);")
	assert "VectorCopy (self->s.origin2, activator->client->ps.velocity);" in body
	assert "activator->client->ps.jumppad_ent" not in body
	assert "activator->client->ps.jumppad_frame" not in body
	assert 'G_SoundIndex("sound/world/jumppad.wav")' in trigger_c
	assert "sound/misc/windfly.wav" not in trigger_c


def test_trigger_hurt_use_callback_is_always_wired_like_retail() -> None:
	trigger_c = _read("src/code/game/g_trigger.c")
	start = trigger_c.index("void SP_trigger_hurt")
	end = trigger_c.index("/*\n==============================================================================\n\ntimer", start)
	body = trigger_c[start:end]

	assert "self->touch = hurt_touch;" in body
	assert "self->use = hurt_use;" in body
	assert "if ( self->spawnflags & 2 )" not in body
	assert body.index("self->r.contents = CONTENTS_TRIGGER;") < body.index("self->use = hurt_use;")
	assert body.index("self->use = hurt_use;") < body.index("if ( ! (self->spawnflags & 1) )")


def test_trigger_family_spawn_and_wiring_covers_retail_qagame_surfaces() -> None:
	spawn_c = _read("src/code/game/g_spawn.c")
	trigger_c = _read("src/code/game/g_trigger.c")
	expected_spawns = (
		'{"trigger_always", SP_trigger_always}',
		'{"trigger_multiple", SP_trigger_multiple}',
		'{"trigger_push", SP_trigger_push}',
		'{"trigger_teleport", SP_trigger_teleport}',
		'{"trigger_hurt", SP_trigger_hurt}',
		'{"trigger_capturezone", SP_trigger_capturezone}',
		'{"func_timer", SP_func_timer}',
		'{"target_push", SP_target_push}',
	)

	for spawn in expected_spawns:
		assert spawn in spawn_c

	assert "ent->touch = Touch_Multi;" in trigger_c
	assert "ent->use = Use_Multi;" in trigger_c
	assert "G_SpawnFloat( \"wait\", \"0.5\", &ent->wait );" in trigger_c
	assert "ent->nextthink = level.time + 300;" in trigger_c
	assert "ent->think = trigger_always_think;" in trigger_c
	assert "self->s.eType = ET_PUSH_TRIGGER;" in trigger_c
	assert "self->s.eType = ET_TELEPORT_TRIGGER;" in trigger_c
	assert "self->touch = trigger_teleporter_touch;" in trigger_c
	assert "ent->touch = Team_DominationPointTouch;" in trigger_c
	assert "self->use = func_timer_use;" in trigger_c
	assert "self->think = func_timer_think;" in trigger_c
