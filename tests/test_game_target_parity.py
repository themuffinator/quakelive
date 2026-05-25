from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _function_block(source: str, signature: str) -> str:
	start = source.index(signature)
	brace = source.index("{", start)
	depth = 0
	for index in range(brace, len(source)):
		if source[index] == "{":
			depth += 1
		elif source[index] == "}":
			depth -= 1
			if depth == 0:
				return source[start : index + 1]
	raise AssertionError(f"unterminated function block for {signature}")


def test_selected_target_entities_are_wired_in_retail_spawn_order() -> None:
	spawn_c = _read("src/code/game/g_spawn.c")
	expected = [
		'{"target_give", SP_target_give}',
		'{"target_remove_keys", SP_target_remove_keys}',
		'{"target_remove_powerups", SP_target_remove_powerups}',
		'{"target_delay", SP_target_delay}',
		'{"target_speaker", SP_target_speaker}',
		'{"target_print", SP_target_print}',
		'{"target_laser", SP_target_laser}',
		'{"target_score", SP_target_score}',
		'{"target_teleporter", SP_target_teleporter}',
		'{"target_relay", SP_target_relay}',
	]

	positions = [spawn_c.index(entry) for entry in expected]
	assert positions == sorted(positions)


def test_target_give_consumes_matched_items_like_retail() -> None:
	target_c = _read("src/code/game/g_target.c")
	use_body = _function_block(target_c, "void Use_Target_Give")
	spawn_body = _function_block(target_c, "void SP_target_give")

	assert "if ( !activator->client )" in use_body
	assert "if ( !ent->target )" in use_body
	assert "memset( &trace, 0, sizeof( trace ) );" in use_body
	assert "G_Find (t, FOFS(targetname), ent->target)" in use_body
	assert "if ( !t->item )" in use_body
	assert "Touch_Item( t, activator, &trace );" in use_body
	assert "t->nextthink = 0;" in use_body
	assert "trap_UnlinkEntity( t );" in use_body
	assert "ent->use = Use_Target_Give;" in spawn_body


def test_target_remove_keys_and_powerups_clear_retail_inventory_paths() -> None:
	target_c = _read("src/code/game/g_target.c")
	keys_body = _function_block(target_c, "static void Use_Target_RemoveKeys")
	keys_spawn = _function_block(target_c, "void SP_target_remove_keys")
	powerups_body = _function_block(target_c, "void Use_target_remove_powerups")
	powerups_spawn = _function_block(target_c, "void SP_target_remove_powerups")

	assert "if ( !activator || !activator->client )" in keys_body
	assert "G_DropClientKeys( activator );" in keys_body
	assert "ent->use = Use_Target_RemoveKeys;" in keys_spawn

	for powerup in ("PW_REDFLAG", "PW_BLUEFLAG", "PW_NEUTRALFLAG"):
		assert f"G_TossFlag( activator, {powerup}, FLAG_DROP_CONTEXT_FORCED_RETURN" in powerups_body
	assert "if( !activator->client )" in powerups_body
	assert "memset( activator->client->ps.powerups, 0, sizeof( activator->client->ps.powerups ) );" in powerups_body
	assert "ent->use = Use_target_remove_powerups;" in powerups_spawn


def test_target_delay_uses_cached_activator_and_retail_delay_defaults() -> None:
	target_c = _read("src/code/game/g_target.c")
	think_body = _function_block(target_c, "void Think_Target_Delay")
	use_body = _function_block(target_c, "void Use_Target_Delay")
	spawn_body = _function_block(target_c, "void SP_target_delay")

	assert "G_UseTargets( ent, ent->activator );" in think_body
	assert "ent->nextthink = level.time + ( ent->wait + ent->random * crandom() ) * 1000;" in use_body
	assert "ent->think = Think_Target_Delay;" in use_body
	assert "ent->activator = activator;" in use_body
	assert 'G_SpawnFloat( "delay", "0", &ent->wait )' in spawn_body
	assert 'G_SpawnFloat( "wait", "1", &ent->wait );' in spawn_body
	assert "if ( !ent->wait )" in spawn_body
	assert "ent->wait = 1;" in spawn_body
	assert "ent->use = Use_Target_Delay;" in spawn_body


def test_target_score_print_and_speaker_callbacks_keep_retail_routing() -> None:
	target_c = _read("src/code/game/g_target.c")
	score_use = _function_block(target_c, "void Use_Target_Score")
	score_spawn = _function_block(target_c, "void SP_target_score")
	print_use = _function_block(target_c, "void Use_Target_Print")
	speaker_use = _function_block(target_c, "void Use_Target_Speaker")
	speaker_spawn = _function_block(target_c, "void SP_target_speaker")

	assert "AddScore( activator, ent->r.currentOrigin, ent->count );" in score_use
	assert "ent->count = 1;" in score_spawn
	assert "ent->use = Use_Target_Score;" in score_spawn

	assert "activator->client && ( ent->spawnflags & 4 )" in print_use
	assert 'trap_SendServerCommand( activator-g_entities, va("cp \\"%s\\"", ent->message ));' in print_use
	assert "G_TeamCommand( TEAM_RED" in print_use
	assert "G_TeamCommand( TEAM_BLUE" in print_use
	assert 'trap_SendServerCommand( -1, va("cp \\"%s\\"", ent->message ));' in print_use

	assert "if (ent->spawnflags & 3)" in speaker_use
	assert "ent->s.loopSound = 0;" in speaker_use
	assert "ent->s.loopSound = ent->noise_index;" in speaker_use
	assert "G_AddEvent( activator, EV_GENERAL_SOUND, ent->noise_index );" in speaker_use
	assert "G_AddEvent( ent, EV_GLOBAL_SOUND, ent->noise_index );" in speaker_use
	assert "G_AddEvent( ent, EV_GENERAL_SOUND, ent->noise_index );" in speaker_use
	assert 'G_SpawnFloat( "wait", "0", &ent->wait );' in speaker_spawn
	assert 'G_SpawnFloat( "random", "0", &ent->random );' in speaker_spawn
	assert 'G_Error( "target_speaker without a noise key at %s", vtos( ent->s.origin ) );' in speaker_spawn
	assert "ent->spawnflags |= 8;" in speaker_spawn
	assert 'Com_sprintf (buffer, sizeof(buffer), "%s.wav", s );' in speaker_spawn
	assert "ent->s.eType = ET_SPEAKER;" in speaker_spawn
	assert "ent->s.frame = ent->wait * 10;" in speaker_spawn
	assert "ent->s.clientNum = ent->random * 10;" in speaker_spawn
	assert "ent->r.svFlags |= SVF_BROADCAST;" in speaker_spawn
	assert "trap_LinkEntity( ent );" in speaker_spawn


def test_target_laser_bootstrap_toggle_and_beam_think_match_retail() -> None:
	target_c = _read("src/code/game/g_target.c")
	think_body = _function_block(target_c, "void target_laser_think")
	use_body = _function_block(target_c, "void target_laser_use")
	start_body = _function_block(target_c, "void target_laser_start")
	spawn_body = _function_block(target_c, "void SP_target_laser")

	assert "VectorMA (self->enemy->s.origin, 0.5, self->enemy->r.mins, point);" in think_body
	assert "VectorMA (point, 0.5, self->enemy->r.maxs, point);" in think_body
	assert "VectorMA (self->s.origin, 2048, self->movedir, end);" in think_body
	assert "CONTENTS_SOLID|CONTENTS_BODY|CONTENTS_CORPSE" in think_body
	assert "DAMAGE_NO_KNOCKBACK, MOD_TARGET_LASER" in think_body
	assert "VectorCopy (tr.endpos, self->s.origin2);" in think_body
	assert "self->nextthink = level.time + FRAMETIME;" in think_body

	assert "self->activator = activator;" in use_body
	assert "target_laser_off (self);" in use_body
	assert "target_laser_on (self);" in use_body

	assert "self->s.eType = ET_BEAM;" in start_body
	assert "G_Find (NULL, FOFS(targetname), self->target)" in start_body
	assert "G_SetMovedir (self->s.angles, self->movedir);" in start_body
	assert "self->use = target_laser_use;" in start_body
	assert "self->think = target_laser_think;" in start_body
	assert "self->damage = 1;" in start_body
	assert "target_laser_on (self);" in start_body
	assert "target_laser_off (self);" in start_body

	assert "self->think = target_laser_start;" in spawn_body
	assert "self->nextthink = level.time + FRAMETIME;" in spawn_body


def test_target_teleporter_and_relay_keep_retail_use_wiring() -> None:
	target_c = _read("src/code/game/g_target.c")
	teleport_use = _function_block(target_c, "void target_teleporter_use")
	teleport_spawn = _function_block(target_c, "void SP_target_teleporter")
	relay_use = _function_block(target_c, "void target_relay_use")
	relay_spawn = _function_block(target_c, "void SP_target_relay")

	assert "if (!activator->client)" in teleport_use
	assert "G_PickTarget( self->target )" in teleport_use
	assert 'G_Printf ("Couldn\'t find teleporter destination\\n");' in teleport_use
	assert "TeleportPlayer( activator, dest->s.origin, dest->s.angles );" in teleport_use
	assert 'G_Printf("untargeted %s at %s\\n", self->classname, vtos(self->s.origin));' in teleport_spawn
	assert "self->use = target_teleporter_use;" in teleport_spawn

	assert "( self->spawnflags & 1 ) && activator->client" in relay_use
	assert "activator->client->sess.sessionTeam != TEAM_RED" in relay_use
	assert "( self->spawnflags & 2 ) && activator->client" in relay_use
	assert "activator->client->sess.sessionTeam != TEAM_BLUE" in relay_use
	assert "if ( self->spawnflags & 4 )" in relay_use
	assert "ent = G_PickTarget( self->target );" in relay_use
	assert "ent->use( ent, self, activator );" in relay_use
	assert "G_UseTargets (self, activator);" in relay_use
	assert "self->use = target_relay_use;" in relay_spawn


def test_remaining_target_entities_are_wired_in_retail_spawn_order() -> None:
	spawn_c = _read("src/code/game/g_spawn.c")
	expected = [
		'{"target_kill", SP_target_kill}',
		'{"target_position", SP_target_position}',
		'{"target_location", SP_target_location}',
		'{"target_push", SP_target_push}',
		'{"target_cvar", SP_target_cvar}',
		'{"target_achievement", SP_target_achievement}',
	]

	positions = [spawn_c.index(entry) for entry in expected]
	assert positions == sorted(positions)


def test_target_kill_position_and_location_match_retail_wiring() -> None:
	target_c = _read("src/code/game/g_target.c")
	kill_use = _function_block(target_c, "void target_kill_use")
	kill_spawn = _function_block(target_c, "void SP_target_kill")
	position_spawn = _function_block(target_c, "void SP_target_position")
	location_link = _function_block(target_c, "static void target_location_linkup")
	location_spawn = _function_block(target_c, "void SP_target_location")

	assert "G_Damage ( activator, NULL, NULL, NULL, NULL, 100000, DAMAGE_NO_PROTECTION, MOD_TELEFRAG);" in kill_use
	assert "self->use = target_kill_use;" in kill_spawn
	assert "G_SetOrigin( self, self->s.origin );" in position_spawn

	assert "if (level.locationLinked)" in location_link
	assert "level.locationLinked = qtrue;" in location_link
	assert "level.locationHead = NULL;" in location_link
	assert 'trap_SetConfigstring( CS_LOCATIONS, "unknown" );' in location_link
	assert "i < level.num_entities && n < MAX_LOCATIONS" in location_link
	assert 'ent->classname && !Q_stricmp(ent->classname, "target_location")' in location_link
	assert "ent->health = n;" in location_link
	assert "trap_SetConfigstring( CS_LOCATIONS + n, ent->message );" in location_link
	assert "ent->nextTrain = level.locationHead;" in location_link
	assert "level.locationHead = ent;" in location_link

	assert "self->think = target_location_linkup;" in location_spawn
	assert "self->nextthink = level.time + 200;" in location_spawn
	assert "G_SetOrigin( self, self->s.origin );" in location_spawn


def test_target_push_matches_retail_g_trigger_wiring() -> None:
	trigger_c = _read("src/code/game/g_trigger.c")
	use_body = _function_block(trigger_c, "static void Use_target_push")
	spawn_body = _function_block(trigger_c, "void SP_target_push")

	assert use_body.index("if ( !activator->client )") < use_body.index("if ( activator->client->ps.pm_type != PM_NORMAL )")
	assert use_body.index("if ( activator->client->ps.pm_type != PM_NORMAL )") < use_body.index("if ( activator->client->ps.powerups[PW_FLIGHT] )")
	assert use_body.index("if ( activator->client->ps.powerups[PW_FLIGHT] )") < use_body.index("if ( activator->client->hook )")
	assert use_body.index("if ( activator->client->hook )") < use_body.index("VectorCopy (self->s.origin2, activator->client->ps.velocity);")
	assert "activator->client->ps.jumppad_ent" not in use_body
	assert "activator->client->ps.jumppad_frame" not in use_body
	assert "activator->fly_sound_debounce_time = level.time + 1500;" in use_body
	assert "G_Sound( activator, CHAN_AUTO, self->noise_index );" in use_body

	assert "self->speed = 1000;" in spawn_body
	assert "G_SetMovedir (self->s.angles, self->s.origin2);" in spawn_body
	assert "VectorScale (self->s.origin2, self->speed, self->s.origin2);" in spawn_body
	assert 'self->noise_index = G_SoundIndex("sound/world/jumppad.wav");' in spawn_body
	assert "sound/misc/windfly.wav" not in spawn_body
	assert "VectorCopy( self->s.origin, self->r.absmin );" in spawn_body
	assert "VectorCopy( self->s.origin, self->r.absmax );" in spawn_body
	assert "self->think = AimAtTarget;" in spawn_body
	assert "self->nextthink = level.time + FRAMETIME;" in spawn_body
	assert "self->use = Use_target_push;" in spawn_body


def test_target_cvar_and_achievement_match_retail_ql_only_wiring() -> None:
	target_c = _read("src/code/game/g_target.c")
	cvar_use = _function_block(target_c, "static void Use_Target_Cvar")
	cvar_spawn = _function_block(target_c, "void SP_target_cvar")
	achievement_use = _function_block(target_c, "static void Use_Target_Achievement")
	achievement_spawn = _function_block(target_c, "void SP_target_achievement")

	assert "trap_Cvar_Set( ent->message, va( \"%f\", ent->random ) );" in cvar_use
	assert '(void)other;' in cvar_use
	assert '(void)activator;' in cvar_use
	assert 'G_SpawnFloat( "cvarValue", "-1.0f", &ent->random );' in cvar_spawn
	assert "ent->use = Use_Target_Cvar;" in cvar_spawn

	assert "static const int s_targetAchievementIds[] = {\n\t0,\n\t2,\n\t3,\n\t4,\n\t5,\n\t6,\n\t7,\n\t8\n};" in target_c
	assert "if ( !activator || !activator->client )" in achievement_use
	assert "achievementIndex = ent->health;" in achievement_use
	assert "achievementIndex <= 0 || achievementIndex >= ARRAY_LEN( s_targetAchievementIds )" in achievement_use
	assert "achievementId = s_targetAchievementIds[achievementIndex];" in achievement_use
	assert "trap_HasSteamAchievement( activator->s.number, achievementId )" in achievement_use
	assert "trap_UnlockSteamAchievement( activator->s.number, achievementId );" in achievement_use
	assert 'G_SpawnInt( "id", "0", &ent->health );' in achievement_spawn
	assert "ent->use = Use_Target_Achievement;" in achievement_spawn
