typedef enum {
	GAMETYPE_LIFECYCLE_INIT,
	GAMETYPE_LIFECYCLE_CLIENT_BEGIN,
	GAMETYPE_LIFECYCLE_CLIENT_SPAWN
} gametypeLifecycleStage_t;

#if defined(QLR_INSTRUMENT_GAMETYPE_LIFECYCLE)
void QLR_RecordGametypeDuelStage( gametypeLifecycleStage_t stage );
void QLR_RecordGametypeDefaultStage( gametypeLifecycleStage_t stage );
#endif
#if defined(QLR_INSTRUMENT_MATCH_SIM)
void QLR_RecordMatchSimDuelEvent( const char *action, const char *details );
#endif

static void G_DuelInit( void );
static void G_DuelClientBegin( gentity_t *ent );
static void G_DuelClientSpawn( gentity_t *ent );

/*
=============
G_LogDuelMatchSimEvent

Forwards duel-specific lifecycle markers to the match-sim instrumentation hook.
=============
*/
static void G_LogDuelMatchSimEvent( const char *action, const char *details ) {
#if defined(QLR_INSTRUMENT_MATCH_SIM)
	QLR_RecordMatchSimDuelEvent( action, details );
#else
	(void)action;
	(void)details;
#endif
}

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

Runs the duel lifecycle helpers: INIT resets CS_WARMUP/ready-up
configstrings and clears sudden-death state per g_suddenDeath* CVars;
ClientBegin restarts or pauses the g_warmup countdown while refreshing
those configstrings when players connect; ClientSpawn enforces the
spawn grant script defined by s_duelSpawnGrantScript so duel loadouts
are applied every time a player enters.
=============
*/
static void G_GametypeHandleDuel( gametypeLifecycleStage_t stage, gentity_t *ent ) {
	switch ( stage ) {
	case GAMETYPE_LIFECYCLE_INIT:
#if defined(QLR_INSTRUMENT_GAMETYPE_LIFECYCLE)
                QLR_RecordGametypeDuelStage( stage );
#endif
                G_DuelInit();
		G_LogDuelMatchSimEvent( "duel_ready_configstring", va( "%i", level.warmupTime ) );
                G_GametypeHandleDefault( stage, ent );
                break;
        case GAMETYPE_LIFECYCLE_CLIENT_BEGIN:
#if defined(QLR_INSTRUMENT_GAMETYPE_LIFECYCLE)
                QLR_RecordGametypeDuelStage( stage );
#endif
                if ( ent ) {
                        G_DuelClientBegin( ent );
                }
		G_LogDuelMatchSimEvent( "duel_ready_configstring", va( "%i", level.warmupTime ) );
                G_GametypeHandleDefault( stage, ent );
                break;
        case GAMETYPE_LIFECYCLE_CLIENT_SPAWN:
#if defined(QLR_INSTRUMENT_GAMETYPE_LIFECYCLE)
                QLR_RecordGametypeDuelStage( stage );
#endif
                if ( ent ) {
                        G_DuelClientSpawn( ent );
                }
		G_LogDuelMatchSimEvent( "duel_spawn_loadout", s_duelSpawnGrantScript );
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
		if ( g_gametype.integer == GT_ATTACK_DEFEND ) {
			if ( level.adRoundState == AD_ROUNDSTATE_EXIT ) {
				return;
			}
		}

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
		G_SetWarmupTime( -1 );
	} else {
		G_UpdateReadyUpConfigstring();
	}

	level.suddenDeathActive = qfalse;
	level.suddenDeathLastDelay = -1;
	level.suddenDeathNoRespawnLogged = qfalse;
	G_LogDuelMatchSimEvent(
		"duel_sudden_death",
		va(
			"respawn=%i start=%i tick=%i max=%i increment=%i print=%i",
			g_suddenDeathRespawn.integer,
			g_suddenDeathRespawnStart.integer,
			g_suddenDeathRespawnTick.integer,
			g_suddenDeathRespawnMax.integer,
			g_suddenDeathRespawnIncrement.integer,
			g_suddenDeathRespawnPrint.integer
		)
	);
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
			G_SetWarmupTime( -1 );
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

	G_SetWarmupTime( level.time + ( countdownSeconds - 1 ) * 1000 );
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
	case GT_ATTACK_DEFEND:
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
