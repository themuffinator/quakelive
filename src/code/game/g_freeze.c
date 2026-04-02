#include "g_local.h"

#define QL_EV_FREEZE_THAW_PROGRESS	0x58

/*
============
G_FreezeResolveThawProgressTarget

Finds the linked frozen client for a retail thaw-progress temp entity.
============
*/
static int G_FreezeResolveThawProgressTarget( const gentity_t *ent ) {
	int		targetClientNum;

	if ( !ent ) {
		return -1;
	}

	targetClientNum = ent->s.otherEntityNum;
	if ( targetClientNum >= 0 && targetClientNum < level.maxclients ) {
		if ( g_entities[targetClientNum].inuse
			&& g_entities[targetClientNum].client
			&& level.clients[targetClientNum].pers.connected == CON_CONNECTED ) {
			return targetClientNum;
		}
	}

	targetClientNum = ent->s.clientNum;
	if ( targetClientNum >= 0 && targetClientNum < level.maxclients ) {
		if ( g_entities[targetClientNum].inuse
			&& g_entities[targetClientNum].client
			&& level.clients[targetClientNum].pers.connected == CON_CONNECTED ) {
			return targetClientNum;
		}
	}

	return -1;
}

/*
============
G_FreezeCanSeeThawProgressEvent

Retail-only native export helper for the Freeze thaw-progress temp entity.
============
*/
qboolean G_FreezeCanSeeThawProgressEvent( int clientNum, int entNum ) {
	gentity_t	*ent;
	int		targetClientNum;

	if ( clientNum < 0 || clientNum >= level.maxclients ) {
		return qfalse;
	}

	if ( level.clients[clientNum].pers.connected != CON_CONNECTED ) {
		return qfalse;
	}

	if ( !G_FreezeGametypeEnabled() ) {
		return qfalse;
	}

	if ( level.roundState != ROUNDSTATE_ACTIVE ) {
		return qfalse;
	}

	if ( entNum < 0 || entNum >= level.num_entities ) {
		return qfalse;
	}

	ent = &g_entities[entNum];
	if ( !ent->inuse ) {
		return qfalse;
	}

	if ( ent->s.eType != ET_EVENTS + QL_EV_FREEZE_THAW_PROGRESS ) {
		return qfalse;
	}

	targetClientNum = G_FreezeResolveThawProgressTarget( ent );
	if ( targetClientNum < 0 ) {
		return qfalse;
	}

	return G_ClientNumsOnSameTeam( clientNum, targetClientNum );
}

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
G_FreezeSetClientFrozenState

Shared retail-style Freeze state mutator spanning the frozen and thawed paths.
============
*/
static void G_FreezeSetClientFrozenState( gentity_t *ent, qboolean frozen, qboolean environmental, qboolean wasAuto, int helperNum ) {
	gclient_t	*client;
	int			thawTick;
	int			protectTime;
	gentity_t	*tent;

	if ( !ent || !ent->client ) {
		return;
	}

	client = ent->client;
	if ( frozen ) {
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
		ent->takedamage = qfalse;
		ent->health = 1;
		client->ps.stats[STAT_HEALTH] = 1;
		return;
	}

	if ( !client->freezeFrozen ) {
		return;
	}

	client->freezeFrozen = qfalse;
	client->freezeTime = 0;
	client->freezeAccumulatedThaw = 0;
	client->freezeNextThawTick = 0;
	client->freezeLastHelper = -1;
	client->freezeAutoThawTime = 0;
	client->freezeEnvironmentalRespawnTime = 0;
	client->ps.pm_type = PM_NORMAL;
	ent->takedamage = qtrue;

	// Reset health/armor to spawn defaults or specific thaw values?
	// QL usually resets them or keeps what they had?
	// Usually they respawn with default health/armor.
	ent->health = client->ps.stats[STAT_MAX_HEALTH];
	client->ps.stats[STAT_HEALTH] = ent->health;
	client->ps.stats[STAT_ARMOR] = g_factoryCvarConfig.startingArmor;
	BG_UpdateArmorTierFromCurrentArmor( &client->ps, g_armorTiered.integer ? qtrue : qfalse );

	protectTime = level.freezeConfig.protectedSpawnTime;
	if ( protectTime > 0 ) {
		client->invulnerabilityTime = level.time + protectTime;
		client->freezeProtectedUntil = client->invulnerabilityTime;
	}
	else {
		client->invulnerabilityTime = 0;
		client->freezeProtectedUntil = 0;
	}
	client->holdableInvulnerabilityTime = 0;

	// Effect
	tent = G_TempEntity( client->ps.origin, EV_PLAYER_TELEPORT_IN );
	tent->s.clientNum = ent->s.clientNum;
	tent->s.eventParm = QL_EVENTPARM_FREEZE_THAW;

	// Sound
	G_Sound( ent, CHAN_AUTO, G_SoundIndex( "sound/items/respawn1.wav" ) );

	if ( wasAuto ) {
		// Auto-thaw logic (e.g. round end or sudden death)
	} else if ( helperNum >= 0 && helperNum < level.maxclients ) {
		gentity_t *helper = &g_entities[helperNum];
		if ( helper && helper->client ) {
			AddScore( helper, ent->r.currentOrigin, 1 ); // Score for thawing
			trap_SendServerCommand( -1, va( "cp \"%s thawed %s!\"\n", helper->client->pers.netname, client->pers.netname ) );
			helper->client->ps.persistant[PERS_ASSIST_COUNT]++;
			G_RankSendPlayerMedal( helper, "ASSISTS" );
		}
	}
}

/*
============
G_FreezeThawClient

Unfreezes a player, applies invulnerability, and announces the thaw.
============
*/
void G_FreezeThawClient( gentity_t *ent, qboolean wasAuto, int helperNum ) {
	G_FreezeSetClientFrozenState( ent, qfalse, qfalse, wasAuto, helperNum );
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
	G_FreezeSetClientFrozenState( self, qtrue, environmental, qfalse, -1 );
}
