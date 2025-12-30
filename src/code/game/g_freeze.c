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
	int			thawTime;

	if ( !ent || !ent->client || !ent->client->freezeFrozen ) {
		return;
	}

	ent->client->freezeFrozen = qfalse;
	ent->client->freezeTime = 0;
	ent->client->freezeAccumulatedThaw = 0;
	ent->client->ps.pm_type = PM_NORMAL;
	ent->takedamage = qtrue;
	ent->s.powerups |= ( 1 << PW_INVULNERABILITY );

	// Reset health/armor to spawn defaults or specific thaw values?
	// QL usually resets them or keeps what they had?
	// Usually they respawn with default health/armor.
	ent->health = ent->client->ps.stats[STAT_MAX_HEALTH];
	ent->client->ps.stats[STAT_HEALTH] = ent->health;
	ent->client->ps.stats[STAT_ARMOR] = g_factoryCvarConfig.startingArmor;

	ent->client->invulnerabilityTime = level.time + 3000; // 3 seconds protection

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
G_FreezeHandlePlayerDeath

Handles the "death" of a player in Freeze Tag (freezing them instead of killing).
Returns qtrue if the death was intercepted (player frozen), qfalse if normal death should occur (e.g. falling into void).
============
*/
qboolean G_FreezeHandlePlayerDeath( gentity_t *self, gentity_t *inflictor, gentity_t *attacker, int damage, int meansOfDeath ) {
	if ( !G_FreezeGametypeEnabled() ) {
		return qfalse;
	}

	if ( meansOfDeath == MOD_FALLING || meansOfDeath == MOD_SUICIDE || meansOfDeath == MOD_LAVA || meansOfDeath == MOD_SLIME || meansOfDeath == MOD_TRIGGER_HURT ) {
		// Environmental deaths might still kill or freeze?
		// In QL, falling into void usually kills/spectates or freezes at spawn.
		// For now, let's assume environmental damage freezes them in place or at valid spot.
		// But if they fall into void, we can't freeze them there.
		if ( self->health < -999 ) { // Gibbed?
			return qfalse; // Allow normal death (respawn)
		}
	}

	if ( self->client->freezeFrozen ) {
		return qtrue; // Already frozen
	}

	// Freeze the player
	self->client->freezeFrozen = qtrue;
	self->client->freezeTime = level.time;
	self->client->ps.pm_type = PM_FREEZE;
	self->takedamage = qfalse; // Can't take further damage while frozen (except maybe to be pushed?)
	self->health = 1; // Keep them "alive"
	self->client->ps.stats[STAT_HEALTH] = 1;

	// Check for "impending doom" or bad spot?
	// If in void, move to spawn.

	// G_AddEvent( self, EV_DEATH1, meansOfDeath ); // Play death sound/anim?
	// Instead play freeze sound
	G_Sound( self, CHAN_AUTO, G_SoundIndex( "sound/player/frozen.wav" ) ); // Need to ensure sound exists or use generic

	// Message
	if ( attacker && attacker->client && attacker != self ) {
		trap_SendServerCommand( -1, va( "cp \"%s froze %s!\"\n", attacker->client->pers.netname, self->client->pers.netname ) );
		AddScore( attacker, self->r.currentOrigin, 1 );
	} else {
		trap_SendServerCommand( -1, va( "cp \"%s froze!\"\n", self->client->pers.netname ) );
	}

	return qtrue;
}

/*
============
G_FreezeClientEndFrame

Updates thaw progress for frozen clients.
============
*/
void G_FreezeClientEndFrame( gentity_t *ent ) {
	if ( !G_FreezeGametypeEnabled() ) {
		return;
	}

	if ( !ent->client->freezeFrozen ) {
		return;
	}

	// Check for nearby teammates to thaw
	// ... implementation of proximity thawing ...
	// For parity, QL uses a "thaw tick" logic.

	// If auto-thaw enabled
	if ( level.freezeConfig.autoThawTime > 0 ) {
		if ( level.time - ent->client->freezeTime > level.freezeConfig.autoThawTime * 1000 ) {
			G_FreezeThawClient( ent, qtrue, -1 );
		}
	}
}
