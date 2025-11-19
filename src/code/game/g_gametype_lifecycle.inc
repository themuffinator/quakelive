typedef enum {
	GAMETYPE_LIFECYCLE_INIT,
	GAMETYPE_LIFECYCLE_CLIENT_BEGIN,
	GAMETYPE_LIFECYCLE_CLIENT_SPAWN
} gametypeLifecycleStage_t;

#if defined(QLR_INSTRUMENT_GAMETYPE_LIFECYCLE)
void QLR_RecordGametypeDuelStage( gametypeLifecycleStage_t stage );
void QLR_RecordGametypeDefaultStage( gametypeLifecycleStage_t stage );
#endif

static void G_DuelInit( void );
static void G_DuelClientBegin( gentity_t *ent );
static void G_DuelClientSpawn( gentity_t *ent );

/*
=============
G_GametypeHandleDefault

No-op placeholder used when a gametype does not require custom
lifecycle handling.
=============
*/
static void G_GametypeHandleDefault( gametypeLifecycleStage_t stage, gentity_t *ent ) {
#if defined(QLR_INSTRUMENT_GAMETYPE_LIFECYCLE)
	QLR_RecordGametypeDefaultStage( stage );
#endif
	(void)stage;
	(void)ent;
}

/*
=============
G_GametypeHandleDuel

Dispatches duel-specific lifecycle helpers recovered from the HLIL flow.
=============
*/
static void G_GametypeHandleDuel( gametypeLifecycleStage_t stage, gentity_t *ent ) {
	switch ( stage ) {
	case GAMETYPE_LIFECYCLE_INIT:
#if defined(QLR_INSTRUMENT_GAMETYPE_LIFECYCLE)
		QLR_RecordGametypeDuelStage( stage );
#endif
		G_DuelInit();
		G_GametypeHandleDefault( stage, ent );
		break;
	case GAMETYPE_LIFECYCLE_CLIENT_BEGIN:
#if defined(QLR_INSTRUMENT_GAMETYPE_LIFECYCLE)
		QLR_RecordGametypeDuelStage( stage );
#endif
		if ( ent ) {
			G_DuelClientBegin( ent );
		}
		G_GametypeHandleDefault( stage, ent );
		break;
	case GAMETYPE_LIFECYCLE_CLIENT_SPAWN:
#if defined(QLR_INSTRUMENT_GAMETYPE_LIFECYCLE)
		QLR_RecordGametypeDuelStage( stage );
#endif
		if ( ent ) {
			G_DuelClientSpawn( ent );
		}
		G_GametypeHandleDefault( stage, ent );
		break;
	default:
		G_GametypeHandleDefault( stage, ent );
		break;
	}
}

/*
=============
G_GametypeHandleRoundBased

Ensures round-based matches start in the warmup state so the round
controller can manage respawns.
=============
*/
static void G_GametypeHandleRoundBased( gametypeLifecycleStage_t stage, gentity_t *ent ) {
	if ( stage == GAMETYPE_LIFECYCLE_INIT ) {
		G_Frame_BeginRoundWarmup();
	}

	(void)ent;
}

/*
=============
G_GametypeHandleRace

Routes the race-specific lifecycle hooks.
=============
*/
static void G_GametypeHandleRace( gametypeLifecycleStage_t stage, gentity_t *ent ) {
	switch ( stage ) {
	case GAMETYPE_LIFECYCLE_CLIENT_BEGIN:
		if ( ent ) {
			G_RaceClientBegin( ent );
		}
		break;

	case GAMETYPE_LIFECYCLE_CLIENT_SPAWN:
		if ( ent ) {
			G_RaceClientSpawn( ent );
		}
		break;

	default:
		break;
	}

	G_GametypeHandleDefault( stage, ent );
}

/*
=============
G_DuelInit

Resets duel warmup and sudden-death state before the countdown begins.
=============
*/
static void G_DuelInit( void ) {
	if ( level.warmupTime != -1 ) {
		level.warmupTime = -1;
		trap_SetConfigstring( CS_WARMUP, va( "%i", level.warmupTime ) );
	}

	G_UpdateReadyUpConfigstring();
	level.suddenDeathActive = qfalse;
	level.suddenDeathLastDelay = -1;
	level.suddenDeathNoRespawnLogged = qfalse;
}

/*
=============
G_DuelClientBegin

Starts or pauses the warmup countdown whenever duel players connect.
=============
*/
static void G_DuelClientBegin( gentity_t *ent ) {
	int		countdownSeconds;

	if ( !ent || !ent->client ) {
		return;
	}

	if ( level.numPlayingClients < 2 ) {
		if ( level.warmupTime != -1 ) {
			level.warmupTime = -1;
			trap_SetConfigstring( CS_WARMUP, va( "%i", level.warmupTime ) );
			G_UpdateReadyUpConfigstring();
		}
		return;
	}

	if ( level.warmupTime >= 0 ) {
		return;
	}

	countdownSeconds = g_warmup.integer;
	if ( countdownSeconds < 1 ) {
		countdownSeconds = 1;
	}

	level.warmupTime = level.time + ( countdownSeconds - 1 ) * 1000;
	trap_SetConfigstring( CS_WARMUP, va( "%i", level.warmupTime ) );
	G_UpdateReadyUpConfigstring();
}

/*
=============
G_DuelClientSpawn

Applies the duel spawn loadout captured from the HLIL notes.
=============
*/
static void G_DuelClientSpawn( gentity_t *ent ) {
	if ( !ent || !ent->client ) {
		return;
	}

	if ( ent->client->sess.sessionTeam == TEAM_SPECTATOR ) {
		return;
	}

	G_RunGrantScript( ent, s_duelSpawnGrantScript );
}

/*
=============
G_RunGametypeLifecycle

Routes the current lifecycle stage through any gametype-specific helper
that needs to mirror the Quake Live dispatch table.
=============
*/
static void G_RunGametypeLifecycle( gametypeLifecycleStage_t stage, gentity_t *ent ) {
	switch ( g_gametype.integer ) {
	case GT_TOURNAMENT:
		G_GametypeHandleDuel( stage, ent );
		break;
	case GT_RACE:
		G_GametypeHandleRace( stage, ent );
		break;

	case GT_CLAN_ARENA:
	case GT_RED_ROVER:
		G_GametypeHandleRoundBased( stage, ent );
		break;

	default:
		G_GametypeHandleDefault( stage, ent );
		break;
	}
}

/*
=============
G_GametypeInit

Executes the init-stage lifecycle hook for the current gametype.
=============
*/
void G_GametypeInit( void ) {
	G_RunGametypeLifecycle( GAMETYPE_LIFECYCLE_INIT, NULL );
}

/*
=============
G_GametypeClientBegin

Executes the ClientBegin-stage lifecycle hook for the current gametype.
=============
*/
void G_GametypeClientBegin( gentity_t *ent ) {
	G_RunGametypeLifecycle( GAMETYPE_LIFECYCLE_CLIENT_BEGIN, ent );
}

/*
=============
G_GametypeClientSpawn

Executes the ClientSpawn-stage lifecycle hook for the current gametype.
=============
*/
void G_GametypeClientSpawn( gentity_t *ent ) {
	G_RunGametypeLifecycle( GAMETYPE_LIFECYCLE_CLIENT_SPAWN, ent );
}
