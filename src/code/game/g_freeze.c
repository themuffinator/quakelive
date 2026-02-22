#include "g_local.h"

/*
============
G_FreezeInitClient

Initializes client state for Freeze Tag at the start of a round or upon connecting.
============
*/
void G_FreezeInitClient( gentity_t *ent ) {
	if ( !ent || !ent->client ) {
		return;
	}

	ent->client->freezeFrozen = qfalse;
	ent->client->freezeTime = 0;
	ent->client->freezeAccumulatedThaw = 0;
	ent->client->freezeLastHelper = -1;
	ent->client->freezeNextThawTick = 0;
	ent->client->freezeAutoThawTime = 0;
	ent->client->freezeProtectedUntil = 0;

	if ( ent->client->sess.sessionTeam != TEAM_SPECTATOR ) {
		ent->client->ps.pm_type = PM_NORMAL;
	}
}

/*
============
G_FreezeThawClient

Unfreezes a player, applies invulnerability, and announces the thaw.
============
*/
void G_FreezeThawClient( gentity_t *ent, qboolean wasAuto, int helperNum ) {
	gentity_t	*tent;
	int			protectTime;

	if ( !ent || !ent->client || !ent->client->freezeFrozen ) {
		return;
	}

	ent->client->freezeFrozen = qfalse;
	ent->client->freezeTime = 0;
	ent->client->freezeAccumulatedThaw = 0;
	ent->client->freezeNextThawTick = 0;
	ent->client->freezeLastHelper = -1;
	ent->client->freezeAutoThawTime = 0;
	ent->client->freezeEnvironmentalRespawnTime = 0;
	ent->client->ps.pm_type = PM_NORMAL;
	ent->takedamage = qtrue;

	// Reset health/armor to spawn defaults or specific thaw values?
	// QL usually resets them or keeps what they had?
	// Usually they respawn with default health/armor.
	ent->health = ent->client->ps.stats[STAT_MAX_HEALTH];
	ent->client->ps.stats[STAT_HEALTH] = ent->health;
	ent->client->ps.stats[STAT_ARMOR] = g_factoryCvarConfig.startingArmor;

	protectTime = level.freezeConfig.protectedSpawnTime;
	if ( protectTime > 0 ) {
		ent->client->invulnerabilityTime = level.time + protectTime;
		ent->client->freezeProtectedUntil = ent->client->invulnerabilityTime;
	} else {
		ent->client->invulnerabilityTime = 0;
		ent->client->freezeProtectedUntil = 0;
	}

	// Effect
	tent = G_TempEntity( ent->client->ps.origin, EV_PLAYER_TELEPORT_IN );
	tent->s.clientNum = ent->s.clientNum;

	// Sound
	G_Sound( ent, CHAN_AUTO, G_SoundIndex( "sound/items/respawn1.wav" ) );

	if ( wasAuto ) {
		// Auto-thaw logic (e.g. round end or sudden death)
	} else if ( helperNum >= 0 && helperNum < level.maxclients ) {
		gentity_t *helper = &g_entities[helperNum];
		if ( helper && helper->client ) {
			AddScore( helper, ent->r.currentOrigin, 1 ); // Score for thawing
			trap_SendServerCommand( -1, va( "cp \"%s thawed %s!\"\n", helper->client->pers.netname, ent->client->pers.netname ) );
			helper->client->ps.persistant[PERS_ASSIST_COUNT]++;
		}
	}
}

/*
============
G_FreezeCountThawHelpers

Counts nearby allies who can thaw the frozen player and returns a helper.
============
*/
int G_FreezeCountThawHelpers( gentity_t *ent, gentity_t **helperOut ) {
	gentity_t	*helper;
	int		count;
	float		bestDistSq;
	vec3_t		delta;
	float		thawRadius;
	int		i;

	if ( helperOut ) {
		*helperOut = NULL;
	}

	if ( !ent || !ent->client || !ent->client->freezeFrozen ) {
		return 0;
	}

	thawRadius = (float)level.freezeConfig.thawRadius;
	if ( thawRadius <= 0.0f ) {
		return 0;
	}

	count = 0;
	bestDistSq = 0.0f;

	for ( i = 0; i < level.maxclients; i++ ) {
		helper = &g_entities[i];
		if ( !helper->inuse || !helper->client ) {
			continue;
		}
		if ( helper == ent ) {
			continue;
		}
		if ( helper->client->sess.sessionTeam != ent->client->sess.sessionTeam ) {
			continue;
		}
		if ( helper->client->freezeFrozen ) {
			continue;
		}
		if ( helper->client->ps.pm_type == PM_DEAD ) {
			continue;
		}

		VectorSubtract( helper->r.currentOrigin, ent->r.currentOrigin, delta );
		if ( VectorLengthSquared( delta ) > thawRadius * thawRadius ) {
			continue;
		}

		if ( !level.freezeConfig.thawThroughSurface ) {
			trace_t trace;
			trap_Trace( &trace, ent->r.currentOrigin, NULL, NULL, helper->r.currentOrigin, ent->s.number, MASK_SOLID );
			if ( trace.fraction < 1.0f && trace.entityNum != helper->s.number ) {
				continue;
			}
		}

		count++;
		if ( helperOut ) {
			float distSq = VectorLengthSquared( delta );
			if ( !*helperOut || distSq < bestDistSq ) {
				*helperOut = helper;
				bestDistSq = distSq;
			}
		}
	}

	return count;
}

/*
============
G_FreezeApplyFreezeState

Applies the frozen state to a client after a freeze-tag "death".
============
*/
void G_FreezeApplyFreezeState( gentity_t *self, qboolean environmental ) {
	gclient_t	*client;
	int		thawTick;

	if ( !self || !self->client ) {
		return;
	}

	client = self->client;
	if ( client->freezeFrozen ) {
		return;
	}

	client->freezeFrozen = qtrue;
	client->freezeTime = level.time;
	client->freezeAccumulatedThaw = 0;
	client->freezeLastHelper = -1;

	thawTick = level.freezeConfig.thawTick;
	if ( thawTick <= 0 ) {
		thawTick = 100;
	}
	client->freezeNextThawTick = level.time + thawTick;

	client->freezeAutoThawTime = 0;
	if ( level.freezeConfig.autoThawTime > 0 ) {
		client->freezeAutoThawTime = level.time + level.freezeConfig.autoThawTime;
	}

	client->freezeEnvironmentalRespawnTime = 0;
	if ( environmental && level.freezeConfig.environmentalRespawnDelay > 0 ) {
		client->freezeEnvironmentalRespawnTime = level.time + level.freezeConfig.environmentalRespawnDelay;
	}

	client->freezeProtectedUntil = 0;
	client->ps.pm_type = PM_FREEZE;
	self->takedamage = qfalse;
	self->health = 1;
	client->ps.stats[STAT_HEALTH] = 1;
}
