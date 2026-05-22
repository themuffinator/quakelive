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

	assert "static void AimAtTargetRunFrame( gentity_t *self, float thinktime )" in trigger_c
	assert "self->runFrame = AimAtTargetRunFrame;" in trigger_c
	assert "self->think = AimAtTarget;" in trigger_c


def test_target_push_marks_launch_latch_for_next_pmove() -> None:
	trigger_c = _read("src/code/game/g_trigger.c")
	start = trigger_c.index("static void Use_target_push")
	end = trigger_c.index("/*QUAKED target_push", start)
	body = trigger_c[start:end]

	assert "VectorCopy (self->s.origin2, activator->client->ps.velocity);" in body
	assert "activator->client->ps.jumppad_ent = self->s.number;" in body
	assert "activator->client->ps.jumppad_frame = activator->client->ps.pmove_framecount;" in body
